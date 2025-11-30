import logging
import os
from typing import List, Dict

import requests

from .schemas import Player, ROSResult, TradeAnalysis
from .models import DEFAULT_PLAYERS

logger = logging.getLogger(__name__)

BALLDONTLIE_API_KEY = os.getenv("BALLDONTLIE_API_KEY")
BALLDONTLIE_BASE_URL = "https://api.balldontlie.io/nfl/v1"

# We’ll populate this at import time.
PLAYER_POOL: List[Player] = []


# ---------- External API integration ----------

def _position_defaults(position_abbr: str) -> dict:
    """
    Simple heuristics for fantasy fields when using real players.
    These are NOT real fantasy stats; just reasonable defaults per position.
    """
    position_abbr = position_abbr.upper()

    if position_abbr == "QB":
        return {"fppg": 18.0, "usage": 35.0, "sos": 5.0, "remaining_games": 8}
    if position_abbr == "RB":
        return {"fppg": 14.0, "usage": 18.0, "sos": 5.0, "remaining_games": 8}
    if position_abbr == "WR":
        return {"fppg": 13.0, "usage": 8.0, "sos": 5.0, "remaining_games": 8}
    if position_abbr == "TE":
        return {"fppg": 9.0, "usage": 6.0, "sos": 5.0, "remaining_games": 8}

    # K, DEF, etc.
    return {"fppg": 7.0, "usage": 1.0, "sos": 5.0, "remaining_games": 8}


def _load_players_from_api() -> List[Player]:
    """
    Load NFL players from the BALLDONTLIE NFL API.

    NOTE:
    - Free tier can use /players but NOT /players/active.
    - Auth format is: Authorization: YOUR_API_KEY (no 'Bearer ').
    """
    if not BALLDONTLIE_API_KEY:
        raise RuntimeError("BALLDONTLIE_API_KEY env var is not set.")

    url = f"{BALLDONTLIE_BASE_URL}/players"

    # 🔐 Per docs: Authorization: YOUR_API_KEY
    headers = {"Authorization": BALLDONTLIE_API_KEY}

    params = {
        "per_page": 100,  # first 100 players
    }

    resp = requests.get(url, headers=headers, params=params, timeout=10)
    resp.raise_for_status()
    payload = resp.json()

    data = payload.get("data", [])
    players: List[Player] = []

    for item in data:
        pos_abbr = (item.get("position_abbreviation") or "").upper()
        # Focus on fantasy-relevant positions.
        if pos_abbr not in {"QB", "RB", "WR", "TE"}:
            continue

        team_obj = item.get("team") or {}
        team_abbr = team_obj.get("abbreviation", "").upper()

        first = item.get("first_name") or ""
        last = item.get("last_name") or ""
        name = f"{first} {last}".strip()

        defaults = _position_defaults(pos_abbr)

        player = Player(
            id=str(item.get("id")),
            name=name,
            team=team_abbr,
            position=pos_abbr,
            fppg=defaults["fppg"],
            usage=defaults["usage"],
            sos=defaults["sos"],
            remaining_games=defaults["remaining_games"],
        )
        players.append(player)

    if not players:
        raise RuntimeError("No suitable players returned from API.")

    logger.info("Loaded %d players from BALLDONTLIE API.", len(players))
    return players


def _init_player_pool() -> List[Player]:
    """
    Try to load real players from the external API.
    If anything fails, fall back to DEFAULT_PLAYERS.
    """
    try:
        return _load_players_from_api()
    except Exception as exc:
        logger.warning(
            "Failed to load players from BALLDONTLIE API (%s). "
            "Falling back to DEFAULT_PLAYERS.",
            exc,
        )
        return DEFAULT_PLAYERS


# Initialize global player pool at import time.
PLAYER_POOL = _init_player_pool()


# ---------- Fantasy math / trade logic ----------

USAGE_WEIGHT = 0.03
SOS_WEIGHT = 0.10


def calculate_ros_points(player: Player) -> float:
    """
    Compute rest-of-season fantasy points for a player based on:
    - FPPG (real or heuristic)
    - remaining games
    - usage (targets/carries)
    - strength of schedule (sos)
    """
    base_ros = player.fppg * player.remaining_games

    usage_bonus_factor = 1 + (USAGE_WEIGHT * player.usage)

    # sos is 1–10, where 5 is neutral
    sos_factor = 1 + (SOS_WEIGHT * (player.sos - 5) / 5)

    ros_points = base_ros * usage_bonus_factor * sos_factor
    return round(ros_points, 2)


def get_players_by_position(position: str | None = None) -> List[Player]:
    if position is None:
        return PLAYER_POOL
    return [p for p in PLAYER_POOL if p.position.upper() == position.upper()]


def get_ros_rankings(position: str | None = None) -> List[ROSResult]:
    """
    Return ROS rankings for either all players or a single position.
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


def analyze_trade(team_a_ids: list[str], team_b_ids: list[str]) -> TradeAnalysis:
    """
    Analyze the trade from Team A's perspective using the current PLAYER_POOL,
    which may come from the external API or fallback static data.
    """
    index = _build_player_index()

    def total(ids: list[str]) -> float:
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
