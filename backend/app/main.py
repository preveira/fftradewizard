# backend/app/main.py

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from .models import PlayerBase, TradeAnalysis, TradeRequest
from .services import get_ros_rankings, analyze_trade, get_players

app = FastAPI(title="FFTradeWizard API")

# ---------- CORS SETUP ----------

# For your project you can safely allow all origins
# If you want to lock it down, replace ["*"] with a list of specific URLs.
origins = [
    "http://localhost:5173",              # Vite dev
    "http://localhost:8080",              # docker dev
    "https://fftradewizard.netlify.app",  # your frontend host (adjust if different)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,      # or ["*"] if you want it fully open
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


@app.get("/players", response_model=list[PlayerBase])
def list_players(position: str | None = Query(default=None)):
  """
  Flat player pool (used by the Trade Analyzer / legacy pool).
  """
  return get_players(position_filter=position)


@app.post("/trade/analyze", response_model=TradeAnalysis)
def trade_analyze(payload: TradeRequest):
  """
  Analyze a proposed trade using ROS scores.
  """
  return analyze_trade(payload)
