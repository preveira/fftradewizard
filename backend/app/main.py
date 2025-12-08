from typing import List, Optional

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .services import (
    get_players_by_position,
    get_ros_rankings,
    analyze_trade,
)


class TradeRequest(BaseModel):
    team_a: List[str]
    team_b: List[str]


app = FastAPI(title="FFTradeWizard API")

# CORS: allow both local dev and Dockerized frontend
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/players")
async def players(position: Optional[str] = Query(default=None)):
    """
    Optional query param:
      - /players
      - /players?position=RB
    """
    return get_players_by_position(position)


@app.get("/rankings/ros")
async def rankings(position: Optional[str] = Query(default=None)):
    """
    Optional query param:
      - /rankings/ros
      - /rankings/ros?position=WR
    """
    return get_ros_rankings(position)


@app.post("/trade/analyze")
async def trade(request: TradeRequest):
    """
    Body shape (matches frontend api.js):

    {
      "team_a": ["player_id_1", "player_id_2"],
      "team_b": ["player_id_3"]
    }
    """
    result = analyze_trade(request.team_a, request.team_b)
    return result
