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
        usage=0.30,        # ~30% team target share
        sos=0.5,           # mid difficulty schedule
        remaining_games=7,
    ),
    Player(
        id="p2",
        name="Ja'Marr Chase",
        team="CIN",
        position="WR",
        fppg=17.3,
        usage=0.28,
        sos=0.55,
        remaining_games=7,
    ),
    Player(
        id="p3",
        name="Christian McCaffrey",
        team="SF",
        position="RB",
        fppg=21.7,
        usage=0.40,        # very high usage RB
        sos=0.45,          # slightly easier schedule
        remaining_games=7,
    ),
    # 👉 You can add more static players here if you like.
]
