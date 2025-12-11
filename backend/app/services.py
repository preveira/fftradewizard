import json
import logging
import os
from typing import Dict, List, Optional

import requests

from .schemas import Player, ROSResult, TradeAnalysis
from .models import DEFAULT_PLAYERS

logger = logging.getLogger(__name__)

# ESPN Fantasy API base for football
ESPN_BASE_URL = "https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl"

ESPN_SEASON = int(os.getenv("ESPN_SEASON", "2025"))
ESPN_SCORING_PERIOD = int(os.getenv("ESPN_SCORING_PERIOD", "1"))
ESPN_MAX_PLAYERS = int(os.getenv("ESPN_MAX_PLAYERS", "2000"))
ESPN_MIN_PERCENT_OWNED = float(os.getenv("ESPN_MIN_PERCENT_OWNED", "0.0"))

# Global map of NFL proTeamIds to abbreviations
TEAM_MAP: Dict[int, str] = {
    1: "ATL", 2: "BUF", 3: "CHI", 4: "CIN", 5: "CLE", 6: "DAL", 7: "DEN",
    8: "DET", 9: "GB", 10: "TEN", 11: "IND", 12: "KC", 13: "LV", 14: "LAR",
    15: "MIAMI", 16: "MIN", 17: "NE", 18: "NO", 19: "NYG", 20: "NYJ",
    21: "PHI", 22: "ARI", 23: "PIT", 24: "LAC", 25: "SF", 26: "SEA",
    27: "TB", 28: "WSH", 29: "CAR", 30: "JAX", 33: "BAL", 34: "HOU"
}

# Weights for ROS scoring
USAGE_WEIGHT = 0.20       # how much usage bumps/lowers score
SOS_WEIGHT = 0.15         # how much schedule / matchup difficulty matters


def _fetch_espn_players_raw() -> Optional[List[dict]]:
    """
    Get raw player objects from ESPN's public fantasy API.

    Uses X-Fantasy-Filter so we can:
      - pull more than the default 50 players
      - restrict to active players only
    """
    url = f"{ESPN_BASE_URL}/seasons/{ESPN_SEASON}/players"
    params = {
        "scoringPeriodId": 0,
        "view": "players_wl",
    }

    fantasy_filter = {
        "players": {
            "limit": ESPN_MAX_PLAYERS,
        },
        "filterActive": {
            "value": True,
        },
    }

    headers = {
        "X-Fantasy-Filter": json.dumps(fantasy_filter),
    }

    try:
        resp = requests.get(url, params=params, headers=headers, timeout=15)
        logger.info(
            "ESPN players request: %s %s -> %s",
            resp.request.method,
            resp.url,
            resp.status_code,
        )
        resp.raise_for_status()
        data = resp.json()

        if not isinstance(data, list):
            logger.warning(
                "Unexpected ESPN players payload shape (type=%s)", type(data)
            )
            return None

        logger.info("ESPN returned %d raw players", len(data))
        return data
    except Exception as exc:
        logger.error("Failed to load players from ESPN: %s", exc)
        return None


def _fetch_team_matchups() -> Dict[str, str]:
    """
    Best-effort mapping of team abbrev -> matchup string like '@ KC' or 'vs DAL'
    for the configured scoring period.

    If ESPN changes their structure or we can't parse it, we just return an
    empty dict and leave matchup undefined.
    """
    url = f"{ESPN_BASE_URL}/seasons/{ESPN_SEASON}"
    params = {"view": "proTeamSchedules_wl"}

    matchups: Dict[str, str] = {}
    try:
        resp = requests.get(url, params=params, timeout=15)
        logger.info(
            "ESPN schedules request: %s %s -> %s",
            resp.request.method,
            resp.url,
            resp.status_code,
        )
        resp.raise_for_status()
        data = resp.json()

        teams = []
        if isinstance(data, dict):
            settings = data.get("settings") or {}
            teams = settings.get("proTeams") or data.get("proTeams") or []
        elif isinstance(data, list):
            # Very defensive: look for first dict with proTeams/settings
            for item in data:
                if isinstance(item, dict) and ("proTeams" in item or "settings" in item):
                    settings = item.get("settings") or {}
                    teams = settings.get("proTeams") or item.get("proTeams") or []
                    break

        if not isinstance(teams, list):
            logger.warning("Unexpected proTeamSchedules payload (no proTeams list)")
            return {}

        key = str(ESPN_SCORING_PERIOD)

        for t in teams:
            try:
                team_id = t.get("id")
                if not isinstance(team_id, int):
                    continue
                abbrev = t.get("abbrev") or TEAM_MAP.get(team_id)
                if not abbrev:
                    continue

                games_by_period = t.get("proGamesByScoringPeriod") or {}
                games = games_by_period.get(key) or games_by_period.get(int(key), [])
                if not games:
                    continue

                game = games[0]
                home_id = game.get("homeProTeamId")
                away_id = game.get("awayProTeamId")
                if home_id is None or away_id is None:
                    continue

                is_home = home_id == team_id
                opp_id = away_id if is_home else home_id
                opp_abbrev = TEAM_MAP.get(opp_id, "UNK")

                matchup_str = f"vs {opp_abbrev}" if is_home else f"@ {opp_abbrev}"
                matchups[abbrev] = matchup_str
            except Exception:
                continue

        logger.info(
            "Built %d team matchups for scoringPeriod=%d",
            len(matchups),
            ESPN_SCORING_PERIOD,
        )
    except Exception as exc:
        logger.warning("Failed to load team schedules from ESPN: %s", exc)

    return matchups


def _extract_basic_info(raw: dict) -> Optional[Player]:
    """
    Build basic Player metadata from an ESPN player payload.
    """
    player_info = raw.get("player") or raw

    full_name = player_info.get("fullName") or player_info.get("name")
    default_pos_id = player_info.get("defaultPositionId")
    pro_team_id = player_info.get("proTeamId")

    if not full_name:
        return None

    espn_id = str(raw.get("id") or player_info.get("id") or full_name)

    if isinstance(default_pos_id, int):
        position_map = {1: "QB", 2: "RB", 3: "WR", 4: "TE", 5: "K", 16: "D/ST"}
        position = position_map.get(default_pos_id, "FLEX")
    else:
        position = "FLEX"

    if isinstance(pro_team_id, int):
        team = TEAM_MAP.get(pro_team_id, "FA")
    else:
        team = "FA"

    ownership = raw.get("ownership", {}) or {}
    percent_owned = ownership.get("percentOwned")
    percent_started = ownership.get("percentStarted")

    if isinstance(percent_owned, (int, float)):
        fppg = float(percent_owned) / 10.0
    else:
        fppg = 0.0

    if isinstance(percent_started, (int, float)):
        usage = float(percent_started) / 100.0
    else:
        usage = 0.5

    sos = 0.5
    remaining_games = 8

    return Player(
        id=espn_id,
        name=full_name,
        team=team,
        position=position,
        fppg=round(fppg, 2),
        usage=usage,
        sos=sos,
        remaining_games=remaining_games,
    )


def _extract_fantasy_totals(raw: dict, current_week: int) -> Dict[str, float]:
    """
    Extract season-to-date fantasy points and projections.
    """
    stats = raw.get("stats", [])
    if not isinstance(stats, list):
        return {
            "season_points": 0.0,
            "projected_season": 0.0,
            "week_projection": 0.0,
        }

    season_points = 0.0
    projected_season = 0.0
    week_projection = 0.0

    for s in stats:
        try:
            source = s.get("statSourceId")
            split = s.get("statSplitTypeId")
            scoring_period = s.get("scoringPeriodId")
            applied_total = float(s.get("appliedTotal", 0.0))

            # Actual season-to-date
            if source == 0 and split == 1:
                season_points = max(season_points, applied_total)

            # Projected full-season total
            if source == 1 and split == 1:
                projected_season = max(projected_season, applied_total)

            # Projected points for the configured week
            if (
                source == 1
                and split == 0
                and scoring_period == current_week
            ):
                week_projection = max(week_projection, applied_total)
        except Exception:
            continue

    return {
        "season_points": round(season_points, 2),
        "projected_season": round(projected_season, 2),
        "week_projection": round(week_projection, 2),
    }


def _load_players_from_espn() -> List[Player]:
    """
    Build the PLAYER_POOL from ESPN, enriched with fantasy totals.

    Requirements for inclusion:
      - Player has a valid name
      - Player is on an NFL team (team != 'FA')
      - Player has percentOwned > 0 (on some fantasy roster)
      - Optional extra filter: percentOwned >= ESPN_MIN_PERCENT_OWNED (env)
    """
    raw_list = _fetch_espn_players_raw()
    if not raw_list:
        logger.warning("No usable ESPN player payload; will fall back to defaults.")
        return []

    matchups = _fetch_team_matchups()

    players: List[Player] = []
    total_raw = len(raw_list)
    filtered_out = 0

    for raw in raw_list:
        base_player = _extract_basic_info(raw)
        if not base_player:
            filtered_out += 1
            continue

        # Skip unassigned / FA
        if base_player.team == "FA":
            filtered_out += 1
            continue

        ownership = raw.get("ownership", {}) or {}
        percent_owned = ownership.get("percentOwned")
        po_val = float(percent_owned) if isinstance(percent_owned, (int, float)) else 0.0

        # Must be on some fantasy roster, and optionally above MIN_PERCENT_OWNED
        if po_val <= 0.0 or po_val < ESPN_MIN_PERCENT_OWNED:
            filtered_out += 1
            continue

        totals = _extract_fantasy_totals(raw, current_week=ESPN_SCORING_PERIOD)

        enriched = base_player.copy(
            update=dict(
                season_points=totals["season_points"],
                projected_season=totals["projected_season"],
                week_projection=totals["week_projection"],
                matchup=matchups.get(base_player.team),
            )
        )
        players.append(enriched)

    logger.info(
        "ESPN raw players: %d, kept: %d, filtered_out: %d (min_owned=%.1f, require >0%%)",
        total_raw,
        len(players),
        filtered_out,
        ESPN_MIN_PERCENT_OWNED,
    )

    if not players:
        logger.warning(
            "ESPN returned %d players, but all were filtered or invalid. "
            "Check ESPN_MIN_PERCENT_OWNED (currently %.1f) and filters.",
            total_raw,
            ESPN_MIN_PERCENT_OWNED,
        )

    return players


def _init_player_pool() -> List[Player]:
    espn_players = _load_players_from_espn()
    if espn_players:
        logger.info("Loaded %d players from ESPN", len(espn_players))
        return espn_players

    logger.warning("Falling back to DEFAULT_PLAYERS")
    return list(DEFAULT_PLAYERS)


PLAYER_POOL: List[Player] = _init_player_pool()


def _build_player_index() -> Dict[str, Player]:
    return {p.id: p for p in PLAYER_POOL}


def compute_matchup_factor(player: Player) -> float:
    """
    Very simple difficulty factor for now, using sos as a proxy.
    """
    sos_adjust = 0.5 - player.sos
    return 1.0 + SOS_WEIGHT * sos_adjust


def calculate_ros_score(player: Player) -> float:
    """
    Enhanced ROS metric combining:
      - season points already scored
      - projected rest-of-season points
      - usage
      - matchup difficulty
    """
    if player.projected_season > 0 and player.season_points > 0:
        projected_rest = max(player.projected_season - player.season_points, 0.0)
        base_ros = player.season_points + projected_rest
    elif player.projected_season > 0:
        base_ros = player.projected_season
    else:
        base_ros = player.fppg * max(player.remaining_games, 0)

    usage_factor = 1.0 + (USAGE_WEIGHT * (player.usage - 0.5))
    matchup_factor = compute_matchup_factor(player)

    ros_score = base_ros * usage_factor * matchup_factor
    return round(ros_score, 2)


def tier_for_rank(index: int, total: int) -> str:
    """
    Dynamic tiering based on rank percentile:
      - Top 10%: S
      - Next 20%: A
      - Next 30%: B
      - Next 25%: C
      - Rest: D
    """
    if total <= 0:
        return "D"
    percentile = (index + 1) / total
    if percentile <= 0.10:
        return "S"
    if percentile <= 0.30:
        return "A"
    if percentile <= 0.60:
        return "B"
    if percentile <= 0.85:
        return "C"
    return "D"


def get_players_by_position(position: Optional[str] = None) -> List[Player]:
    if not position or position.upper() == "ALL":
        return PLAYER_POOL
    pos = position.upper()
    return [p for p in PLAYER_POOL if p.position.upper() == pos]


# NEW: this is what main.py will import and await
async def get_player_pool(position: Optional[str] = None) -> List[Player]:
    """
    Async wrapper to fetch the player pool, optionally filtered by position.
    Currently just returns the in-memory PLAYER_POOL (already built at startup).
    """
    return get_players_by_position(position)


async def get_ros_rankings(position: Optional[str] = None) -> List[ROSResult]:
    """
    Return ROS rankings including:
      - Player, team, position
      - Total points scored so far
      - Current week projection
      - Matchup string (e.g., '@ KC' / 'vs DAL')
      - Dynamic tier label (S/A/B/C/D)
    """
    players = get_players_by_position(position)

    results: List[ROSResult] = []
    for p in players:
        ros_score = calculate_ros_score(p)
        result = ROSResult(
            player=p,
            ros_points=ros_score,
            ros_score=ros_score,
            season_points=p.season_points,
            week_projection=p.week_projection,
            matchup=p.matchup,
            tier="",  # will be assigned after sorting
        )
        results.append(result)

    results.sort(key=lambda r: r.ros_score, reverse=True)

    total = len(results)
    for idx, r in enumerate(results):
        r.tier = tier_for_rank(idx, total)

    return results


async def analyze_trade(team_a_ids: List[str], team_b_ids: List[str]) -> TradeAnalysis:
    """
    Evaluate a trade using the SAME enhanced ROS score used by rankings.

    For each side:
      - Look up each player.
      - Compute calculate_ros_score(player).
      - Sum the ROS values to get a total for Team A and Team B.

    This keeps trade fairness perfectly aligned with the rankings page.
    """
    index = _build_player_index()

    def total(ids: List[str]) -> float:
        return round(
            sum(
                calculate_ros_score(index[player_id])
                for player_id in ids
                if player_id in index
            ),
            2,
        )

    team_a_total = total(team_a_ids)
    team_b_total = total(team_b_ids)
    delta_a = round(team_b_total - team_a_total, 2)

    if abs(delta_a) < 5:
        verdict = "Very even trade"
    elif delta_a > 0:
        verdict = "Good for Team A"
    else:
        verdict = "Good for Team B"

    return TradeAnalysis(
        team_a_total=team_a_total,
        team_b_total=team_b_total,
        delta_a=delta_a,
        verdict=verdict,
    )
