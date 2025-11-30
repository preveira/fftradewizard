from typing import List
from .schemas import Player

# Static fallback player data for development or when
# the external API is unavailable.
DEFAULT_PLAYERS: List[Player] = [
    Player(
        id="p1",
        name="Justin Jefferson",
        team="MIN",
        position="WR",
        fppg=18.5,
        usage=10.2,        # targets per game
        sos=7.5,           # strength of schedule 1–10
        remaining_games=7,
    ),
    Player(
        id="p2",
        name="Ja'Marr Chase",
        team="CIN",
        position="WR",
        fppg=17.3,
        usage=9.8,
        sos=6.0,
        remaining_games=7,
    ),
    Player(
        id="p3",
        name="Christian McCaffrey",
        team="SF",
        position="RB",
        fppg=21.7,
        usage=20.0,        # touches per game
        sos=5.0,
        remaining_games=7,
    ),
    # 👉 You can add more static players here if you like.
]
