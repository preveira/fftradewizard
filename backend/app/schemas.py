from pydantic import BaseModel
from typing import List


class Player(BaseModel):
    id: str
    name: str
    team: str
    position: str
    fppg: float  # fantasy points per game
    usage: float  # usage metric, e.g., targets or carries per game
    sos: float  # strength of schedule score 1–10
    remaining_games: int


class ROSResult(BaseModel):
    player: Player
    ros_points: float
    tier: str


class TradeRequest(BaseModel):
    team_a: List[str]
    team_b: List[str]


class TradeAnalysis(BaseModel):
    team_a_total: float
    team_b_total: float
    delta_a: float
    verdict: str
