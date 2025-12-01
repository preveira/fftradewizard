🚀 FFTradeWizard
Fantasy Football ROS Rankings + Trade Analyzer
<p align="center"> <img src="https://img.shields.io/badge/Frontend-React%20(Vite)-61DAFB?logo=react" /> <img src="https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi" /> <img src="https://img.shields.io/badge/API-ESPN%20Fantasy%20API-blue?logo=espn" /> <img src="https://img.shields.io/badge/Language-JavaScript-yellow?logo=javascript" /> <img src="https://img.shields.io/badge/Language-Python-blue?logo=python" /> <img src="https://img.shields.io/badge/Style-Blue%20%26%20Silver-1d4ed8" /> </p> <p align="center"> <strong>FFTradeWizard helps fantasy football players evaluate trades and view rest-of-season rankings powered by ESPN’s Fantasy API (test mode).</strong> </p>
✨ Features

🏆 Rest-of-Season Rankings (scrollable leaderboard)

🔄 Trade Analyzer (Team A vs Team B with ROS valuation)

🌐 Live ESPN player pool (test mode)

🎨 Blue & Silver modern UI

📱 Responsive layout + collapsible sidebar

⚡ FastAPI backend + React frontend

🐍 Python virtual environment support

🔒 Automatic fallback player list if ESPN is unreachable

📸 Screenshots

(Add your real screenshots later; these are placeholders you can replace.)

<p align="center"> <img src="https://via.placeholder.com/800x450?text=FFTradeWizard+-+Rankings+View" /> </p> <p align="center"> <img src="https://via.placeholder.com/800x450?text=FFTradeWizard+-+Trade+Analyzer" /> </p>
📦 Installation & Setup

This guide works for:

Windows (Git Bash, PowerShell, cmd)

macOS Terminal

Linux Bash

🧱 1. Clone the Repository
git clone https://github.com/YOUR_USERNAME/fftradewizard.git
cd fftradewizard


Or download the ZIP and extract it.

🖥 2. Backend Setup (FastAPI + Python)
🔹 Step 2.1 — Create & Activate Virtual Environment
Git Bash / macOS / Linux:
cd backend
python -m venv .venv
source .venv/Scripts/activate        # Windows Git Bash
# OR
source .venv/bin/activate            # macOS/Linux

PowerShell:
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1

🔹 Step 2.2 — Install Dependencies
pip install -r requirements.txt

🔹 Step 2.3 — Create .env

Inside backend/.env:

ESPN_SEASON=2025
ESPN_MAX_PLAYERS=300
ESPN_MIN_PERCENT_OWNED=25.0

🔹 Step 2.4 — Start Backend
python -m uvicorn app.main:app --reload --env-file .env


If successful:

Uvicorn running on http://127.0.0.1:8000

🌐 3. Frontend Setup (React + Vite)

Open a new terminal window, then:

cd frontend
npm install
npm run dev


Vite will display:

Local: http://127.0.0.1:5173/


Open that address in your browser.

🚀 4. How to Use FFTradeWizard
🏆 Rankings Page

Filter by position

Scroll through the player leaderboard

View ROS points & tier labels

🔄 Trade Analyzer

Add players to Team A or Team B

Click Analyze Trade

View:

🧮 ROS totals

➕ Value difference

🏅 Verdict (“Fair”, “Slight Edge”, “Big Win”, etc.)

🎨 UI

Blue & Silver color theme

Modern cards, shadows, gradients

Intuitive sidebar navigation

Responsive for laptop + tablet

🧩 Project Structure
fftradewizard/
│
├── backend/
│   ├── app/
│   ├── main.py
│   ├── services.py
│   ├── .env
│   └── requirements.txt
│
└── frontend/
    ├── src/
    ├── index.html
    ├── package.json
    └── vite.config.js

🔧 Troubleshooting
❌ Styling Not Loading?

Make sure this is in frontend/src/main.jsx:

import "./index.css";

❌ Backend not reading .env?

Use:

--env-file .env

❌ "Module not found" errors?

You forgot:

source .venv/Scripts/activate


or:

.venv\Scripts\Activate.ps1

❌ Frontend blank/white screen?

Reset:

rm -rf node_modules
npm install
npm run dev

🛑 Stop Servers
Backend

Press CTRL + C

Frontend

Press CTRL + C

🎯 Tech Stack

Frontend: React (Vite), JSX, CSS

Backend: FastAPI, Uvicorn

Language: Python + JavaScript

API: ESPN Fantasy Football API (test mode)

UI: Custom Blue & Silver theme

Tools: Git, Node, Python venv

📝 License

MIT License
Feel free to fork, improve, and contribute.