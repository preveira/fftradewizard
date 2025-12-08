# backend/app/main.py

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

# Only import the models that actually exist in app/models.py
from .models import TradeAnalysis, TradeRequest
from .services import get_ros_rankings, get_players, analyze_trade

app = FastAPI(title="FFTradeWizard API")

# ---------- CORS SETUP ----------

# For class-project simplicity, you can allow everything.
# If you prefer to be stricter, replace ["*"] with a list of exact URLs.
origins = [
    "http://localhost:5173",              # Vite dev
    "http://localhost:8080",              # docker dev
    "https://fftradewizard.netlify.app",  # your frontend host (adjust if needed)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,      # or ["*"] if you want totally open
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- ROUTES ----------


@app.get("/rankings/ros")
def rankings_ros(position: str | None = Query(default=None)):
    """
    Rest-of-season rankings endpoint.
    Optional ?position=QB/RB/WR/TE/K/DST filter.
    """
    return get_ros_rankings(position_filter=position)


@app.get("/players")
def list_players(position: str | None = Query(default=None)):
    """
    Flat player pool used by the Trade Analyzer.
    """
    return get_players(position_filter=position)


@app.post("/trade/analyze", response_model=TradeAnalysis)
def trade_analyze(payload: TradeRequest):
    """
    Analyze a proposed trade using ROS scores.
    """
    return analyze_trade(payload)
