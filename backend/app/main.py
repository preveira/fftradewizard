# app/main.py

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .services import get_ros_rankings, get_player_pool, analyze_trade
from .models import TradeRequest

app = FastAPI(
    title="FFTradeWizard API",
    version="0.1.0",
    description="Backend API for FFTradeWizard: ROS rankings + trade analyzer.",
)

# CORS – TEMP: allow all origins for testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # <-- open CORS for now (Netlify + any other origin)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    """Simple health check endpoint."""
    return {"status": "ok"}


@app.get("/rankings/ros")
async def rankings_ros(
    position: str | None = Query(
        default=None,
        description="Optional position filter: QB, RB, WR, TE, etc.",
    )
):
    """
    Return rest-of-season rankings.
    Delegates to services.get_ros_rankings(position).
    """
    try:
        players = await get_ros_rankings(position)
        return players
    except Exception:
        # You can add logging here if you want more detail
        raise HTTPException(status_code=500, detail="Failed to load ROS rankings")


@app.get("/players")
async def players(
    position: str | None = Query(
        default=None,
        description="Optional position filter for player pool.",
    )
):
    """
    Return the player pool used by the Trade Analyzer.
    Delegates to services.get_player_pool(position).
    """
    try:
        players = await get_player_pool(position)
        return players
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to load player pool")


@app.post("/trade/analyze")
async def trade_analyze(payload: TradeRequest):
    """
    Analyze a trade based on ROS scores.
    Delegates to services.analyze_trade(team_a_ids, team_b_ids).
    """
    try:
        result = await analyze_trade(payload.team_a_ids, payload.team_b_ids)
        return result
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to analyze trade")
