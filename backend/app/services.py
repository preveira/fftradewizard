import json
import logging
import os
from typing import Dict, List, Optional

import requests

from .schemas import Player, ROSResult, TradeAnalysis
from .models import DEFAULT_PLAYERS

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------
# ESPN Fantasy Football API configuration (test-friendly defaults)
# ---------------------------------------------------------------------
# We call the same underlying endpoint that the espn-fantasy-football-api
# JS client wraps:
#
#   https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/{YEAR}/players?view=players_wl
#
# plus an X-Fantasy-Filter header to:
#   * increase the limit (default is small)
#   * filter to active players only
#
# To keep things "test sized" while you build, we allow tuning via env:
#   ESPN_SEASON            -> season year (default 2025)
#   ESPN_MAX_PLAYERS       -> max players to pull (default 400)
#   ESPN_MIN_PERCENT_OWNED -> min percentOwned to be considered "relevant"
#
# If anything fails (network, ESPN changes, etc.), we fall back to
# DEFAULT_PLAYERS from models.py.
# ---------------------------------------------------------------------

ESPN_SEASON: int = int(os.getenv("ESPN_SEASON", "2025"))
ESPN_MAX_PLAYERS: int = int(os.getenv("ESPN_MAX_PLAYERS", "400"))
ESPN_MIN_PERCENT_OWNED: float = float(os.getenv("ESPN_MIN_PERCENT_OWNED", "20.0"))

ESPN_S2 = os.getenv("ESPN_S2")       # optional cookie, if needed later
ESPN_SWID = os.getenv("ESPN_SWID")   # optional cookie, if needed later

# Global player pool, loaded at import time
PLAYER_POOL: List[Player] = []

# Fantasy scoring weights (same pattern as before)
USAGE_WEIGHT = 0.03
SOS_WEIGHT = 0.10


# ---------------------------------------------------------------------
# ESPN helper utilities
# ---------------------------------------------------------------------


def _map_position_id(pos_id: Optional[int]) -> Optional[str]:
    """
    Map ESPN defaultPositionId -> our position abbreviations.

    Common mapping (community-documented):
        1: QB, 2: RB, 3: WR, 4: TE, 5: K, 16: DST

    We only care about QB/RB/WR/TE for this app.
    """
    mapping = {
        1: "QB",
        2: "RB",
        3: "WR",
        4: "TE",
        5: "K",
        16: "DST",
    }
    pos = mapping.get(pos_id or 0)
    if pos in {"K", "DST"}:
        return None
    return pos


def _position_defaults(position: str) -> dict:
    """
    Heuristic defaults for fantasy fields when ESPN doesn't give us
    direct projections. These keep ROS math stable and "reasonable".
    """
    position = position.upper()
    if position == "QB":
        return {"fppg": 18.0, "usage": 0.75, "sos": 0.50, "remaining_games": 5}
    if position == "RB":
        return {"fppg": 14.0, "usage": 0.70, "sos": 0.50, "remaining_games": 5}
    if position == "WR":
        return {"fppg": 13.0, "usage": 0.70, "sos": 0.50, "remaining_games": 5}
    if position == "TE":
        return {"fppg": 10.0, "usage": 0.65, "sos": 0.50, "remaining_games": 5}
    return {"fppg": 10.0, "usage": 0.60, "sos": 0.50, "remaining_games": 5}


def _fetch_espn_players_raw() -> List[dict]:
    """
    Call the ESPN Fantasy players endpoint in a test-friendly way:
      * Season = ESPN_SEASON (default 2025)
      * Limit to ESPN_MAX_PLAYERS
      * Only active players (filterActive)
    """
    season = ESPN_SEASON
    url = (
        f"https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/"
        f"seasons/{season}/players"
    )

    params = {
        "view": "players_wl",
        "scoringPeriodId": 0,  # preseason / full pool
    }

    fantasy_filter = {
        "players": {"limit": ESPN_MAX_PLAYERS},
        "filterActive": {"value": True},
    }

    headers = {
        "Accept": "application/json",
        "X-Fantasy-Filter": json.dumps(fantasy_filter),
    }

    cookies = {}
    if ESPN_S2:
        cookies["espn_s2"] = ESPN_S2
    if ESPN_SWID:
        cookies["SWID"] = ESPN_SWID

    logger.info(
        "Loading players from ESPN Fantasy API (season=%s, max_players=%s, min_owned=%s)",
        season,
        ESPN_MAX_PLAYERS,
        ESPN_MIN_PERCENT_OWNED,
    )

    resp = requests.get(
        url,
        params=params,
        headers=headers,
        cookies=cookies or None,
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()

    if not isinstance(data, list):
        raise ValueError("Unexpected ESPN players payload format (expected list)")

    return data


def _load_players_from_espn() -> List[Player]:
    """
    Convert ESPN player JSON into our Player objects, with a filter that
    approximates "fantasy-relevant players":

      - defaultPositionId in {QB, RB, WR, TE}
      - ownership.percentOwned >= ESPN_MIN_PERCENT_OWNED
    """
    raw_players = _fetch_espn_players_raw()

    players: List[Player] = []
    min_owned = ESPN_MIN_PERCENT_OWNED

    for item in raw_players:
        try:
            pos = _map_position_id(item.get("defaultPositionId"))
            if not pos:
                # Skip K/DST/unknown for this app
                continue

            full_name = item.get("fullName")
            if not full_name:
                continue

            ownership = item.get("ownership") or {}
            percent_owned = float(ownership.get("percentOwned") or 0.0)
            if percent_owned < min_owned:
                # Treat "relevant" as "owned in at least X% of leagues"
                continue

            pro_team_id = item.get("proTeamId")
            # For now, just label by team ID; you can map IDs -> abbreviations later if you want.
            team_label = f"Team {pro_team_id}" if pro_team_id is not None else "NFL"

            defaults = _position_defaults(pos)

            player = Player(
                id=str(item.get("id")),
                name=str(full_name),
                team=team_label,
                position=pos,
                fppg=defaults["fppg"],
                usage=defaults["usage"],
                sos=defaults["sos"],
                remaining_games=defaults["remaining_games"],
            )
            players.append(player)
        except Exception as inner_exc:
            logger.debug("Skipping ESPN player due to parse error: %s", inner_exc)
            continue

    if not players:
        raise RuntimeError("ESPN API returned 0 usable players after filtering")

    logger.info("Loaded %d relevant players from ESPN Fantasy API", len(players))
    return players


def _init_player_pool() -> List[Player]:
    """
    Try to load from ESPN; on any failure, fall back to DEFAULT_PLAYERS.
    """
    try:
        players = _load_players_from_espn()
        logger.info("Using ESPN Fantasy player pool.")
        return players
    except Exception as exc:
        logger.warning(
            "Failed to load players from ESPN Fantasy API (%s). "
            "Falling back to DEFAULT_PLAYERS.",
            exc,
        )
        return DEFAULT_PLAYERS


# Initialize global PLAYER_POOL at import time
PLAYER_POOL = _init_player_pool()


# ---------------------------------------------------------------------
# Fantasy math / ROS + trade logic (compatible with existing main.py)
# ---------------------------------------------------------------------


def calculate_ros_points(player: Player) -> float:
    """
    Compute rest-of-season fantasy points for a player based on:
    - FPPG (fantasy points per game)
    - remaining games
    - usage (0–1 "share" of offense)
    - strength of schedule (sos, 0–1 where ~0.5 is neutral)
    """
    base_ros = player.fppg * player.remaining_games

    # Usage: boost high-usage players
    usage_bonus_factor = 1 + (USAGE_WEIGHT * (player.usage * 10))

    # SOS: adjust slightly for easier/harder schedule
    sos_factor = 1 + (SOS_WEIGHT * (0.5 - player.sos))

    ros_points = base_ros * usage_bonus_factor * sos_factor
    return round(ros_points, 2)


def get_players_by_position(position: Optional[str] = None) -> List[Player]:
    """
    Return all players or only those with a matching position (QB/RB/WR/TE).
    """
    if position is None:
        return PLAYER_POOL
    position = position.upper()
    return [p for p in PLAYER_POOL if p.position.upper() == position]


def get_ros_rankings(position: Optional[str] = None) -> List[ROSResult]:
    """
    Return ROS rankings, optionally filtered by position.
    """
    players = get_players_by_position(position)
    results: List[ROSResult] = []

    for p in players:
        ros = calculate_ros_points(p)
        results.append(ROSResult(player=p, ros_points=ros, tier="UNASSIGNED"))

    # sort by ROS descending
    results.sort(key=lambda r: r.ros_points, reverse=True)

    # assign tiers
    for idx, r in enumerate(results):
        if idx < 12:
            r.tier = "Tier 1 (Elite)"
        elif idx < 24:
            r.tier = "Tier 2 (Starter)"
        else:
            r.tier = "Tier 3 (Bench)"

    return results


def _build_player_index() -> Dict[str, Player]:
    return {p.id: p for p in PLAYER_POOL}


def _verdict_from_delta(delta_a: float) -> str:
    if abs(delta_a) < 10:
        return "Fair trade for both sides."
    if 10 <= delta_a < 30:
        return "Slight edge for Team A."
    if delta_a >= 30:
        return "Big win for Team A."
    if -30 < delta_a <= -10:
        return "Slight edge for Team B."
    if delta_a <= -30:
        return "Big win for Team B."
    return "Balanced trade."


def analyze_trade(team_a_ids: List[str], team_b_ids: List[str]) -> TradeAnalysis:
    """
    Analyze the trade from Team A's perspective.
    This signature matches what main.py expects.

    - team_a_ids: players Team A is giving up
    - team_b_ids: players Team B is giving up
    """
    index = _build_player_index()

    def total(ids: List[str]) -> float:
        return sum(
            calculate_ros_points(index[player_id])
            for player_id in ids
            if player_id in index
        )

    team_a_total = total(team_a_ids)
    team_b_total = total(team_b_ids)

    value_a_out = team_a_total
    value_a_in = team_b_total
    delta_a = round(value_a_in - value_a_out, 2)
    verdict = _verdict_from_delta(delta_a)

    return TradeAnalysis(
        team_a_total=team_a_total,
        team_b_total=team_b_total,
        delta_a=delta_a,
        verdict=verdict,
    )
