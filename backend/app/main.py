# backend/app/main.py
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from .models import ROSResult, TradeAnalysis, TradeRequest, PlayerBase
from .services import get_ros_rankings, analyze_trade, get_players

app = FastAPI(title="FFTradeWizard API")

# --- CORS SETUP ---

# OPTION A (safe & explicit): list the actual frontend domains
origins = [
    "http://localhost:5173",              # Vite dev
    "http://localhost:8080",              # Docker/Vite dev
    "https://fftradewizard.netlify.app",  # your Netlify URL (adjust if different)
]

# OPTION B (easier for a class project): allow everything
# origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # or ["*"] if you choose Option B
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ROUTES ---

@app.get("/rankings/ros", response_model=list[ROSResult])
def rankings_ros(position: str | None = Query(default=None)):
    """
    Rest-of-season rankings endpoint.
    Optional ?position=QB/RB/WR/TE/K/DST filter.
    """
    return get_ros_rankings(position_filter=position)


@app.get("/players", response_model=list[PlayerBase])
def list_players(position: str | None = Query(default=None)):
    """
    Flat player pool (used internally / earlier versions).
    """
    return get_players(position_filter=position)


@app.post("/trade/analyze", response_model=TradeAnalysis)
def trade_analyze(payload: TradeRequest):
    """
    Analyze a proposed trade using ROS scores.
    """
    return analyze_trade(payload)
