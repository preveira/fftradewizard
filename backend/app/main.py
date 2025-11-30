from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional

from .schemas import Player, ROSResult, TradeRequest, TradeAnalysis
from .services import get_ros_rankings, analyze_trade, PLAYER_POOL

app = FastAPI(title="FFTradeWizard Backend")

origins = [
    "http://localhost:5173",  # Vite dev
    "http://localhost:3000",  # CRA, if ever used
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/players", response_model=List[Player])
def list_players(position: Optional[str] = None):
    """
    Return players from the current PLAYER_POOL (API-backed or fallback),
    optionally filtered by position.
    """
    if position:
        return [p for p in PLAYER_POOL if p.position.upper() == position.upper()]
    return PLAYER_POOL


@app.get("/rankings/ros", response_model=List[ROSResult])
def ros_rankings(position: Optional[str] = None):
    return get_ros_rankings(position)


@app.post("/trade/analyze", response_model=TradeAnalysis)
def trade_analyze(trade_request: TradeRequest):
    return analyze_trade(trade_request.team_a, trade_request.team_b)
