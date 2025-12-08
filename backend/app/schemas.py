from typing import List, Optional

from pydantic import BaseModel


class Player(BaseModel):
    id: str
    name: str
    team: str
    position: str

    # Core scoring features we used originally
    fppg: float = 0.0
    usage: float = 0.0           # 0–1 scale: share of team volume
    sos: float = 0.5             # 0–1: lower = easier schedule
    remaining_games: int = 0

    # NEW: richer fantasy info (all optional-ish via defaults)
    season_points: float = 0.0           # total fantasy points scored so far
    projected_season: float = 0.0        # projected full-season total
    week_projection: float = 0.0         # projection for the upcoming week
    matchup: Optional[str] = None        # e.g. "@ KC", "vs CHI"


class ROSResult(BaseModel):
    player: Player

    # Old metric – still returned for compatibility
    ros_points: float

    # NEW: enhanced metric incorporating season_points + projection + difficulty
    ros_score: float

    # Convenience copies (frontend can read from here or from player.*)
    season_points: float
    week_projection: float
    matchup: Optional[str] = None

    tier: str


class TradeAnalysis(BaseModel):
    team_a_total: float
    team_b_total: float
    delta_a: float
    verdict: str
