# **FFTradeWizard: A Full-Stack Fantasy Football Ranking & Trade Analysis System**

### **Final Project Submission — EE-160: Programming for Engineers**

**Student:** Kawika Reveira
**University of Hawaiʻi at Mānoa — College of Engineering**

---

# **1. Introduction**

For my EE-160 final project, I designed and implemented **FFTradeWizard**, a fully deployed, full-stack fantasy football analytics platform.
The application calculates live Rest-of-Season (ROS) player rankings and evaluates the fairness of fantasy football trades using real sports data.

The project integrates:

* **Python FastAPI backend** (hosted on Render)
* **React frontend** (hosted on Netlify)
* **Docker containerization** for portability and deployment
* **ESPN Fantasy Football API** for live player data
* **Custom fantasy analytics & trade evaluation engine**

This report documents all systems, design decisions, technical challenges, and the engineering processes used to build the final product.

---

# **2. Motivation and Objectives**

The goals of this project were:

1. Build a fully functional, multi-service engineering project.
2. Apply real-world software engineering workflows (APIs, deployment, containerization).
3. Produce a polished, user-facing system appropriate for a professional portfolio.
4. Develop a tool useful for fantasy football players to:

   * Rank players dynamically
   * Understand weekly projections
   * Evaluate the fairness of player trades

The project successfully meets all of these objectives.

---

# **3. High-Level Architecture Overview**

FFTradeWizard consists of four connected systems:

1. **FastAPI Backend** — computes rankings and trade analysis.
2. **React Frontend** — displays rankings and interactive trade tools.
3. **ESPN Fantasy API Integration** — provides real NFL player data.
4. **Docker Containerization** — ensures consistent deployment across environments.

```
Browser (React UI)
        ↓
Netlify (Static App Hosting)
        ↓
FastAPI Backend (Render Cloud Server)
        ↓
Docker Container (Python App Environment)
        ↓
ESPN Fantasy API (Real-time Data Source)
```

This forms a robust, cloud-based, scalable system.

---

# **4. Backend System (FastAPI)**

## **4.1 Responsibilities**

The backend handles all heavy lifting:

* Fetches data from ESPN’s public API
* Normalizes complex JSON structures
* Computes fantasy analytics
* Exposes REST endpoints for the frontend

## **4.2 Key Endpoints**

| Endpoint         | Description                            |
| ---------------- | -------------------------------------- |
| `/health`        | Deployment / status check              |
| `/rankings/ros`  | Returns list of ROS-ranked players     |
| `/players`       | Returns player pool for trade analyzer |
| `/trade/analyze` | Computes trade fairness                |

## **4.3 Player Data Pipeline**

The backend performs:

1. **Raw data fetch from ESPN**
2. **Player metadata extraction**
3. **Season point & projection extraction**
4. **Matchup parsing from schedule API**
5. **ROS scoring computation**
6. **Tiering algorithm assignment**

## **4.4 ROS Scoring Algorithm**

The ROS score integrates:

* Season-to-date points
* Projected total season points
* Usage rate
* Opponent difficulty via SOS
* Remaining games

```
ros_score = base_ros * usage_factor * matchup_factor
```

This provides a realistic metric for comparing players across positions.

---

# **5. Frontend System (React)**

## **5.1 Components**

* **RosRankings.jsx** — displays live leaderboard
* **TradeAnalyzer.jsx** — allows building trades & viewing results
* **api.js** — centralized API communication layer

## **5.2 UI Features**

* Position filtering
* Loading & error states
* Scrollable ranking view
* Add/remove players for each trade side
* Automated trade verdict display

---

# **6. Integration with ESPN Fantasy Football API**

Because ESPN provides no formal documentation, I reverse-engineered responses and implemented defensive parsing strategies. Key extracted fields:

* Player identity & metadata
* Team ID → team abbreviation mapping
* Weekly projections
* Season-to-date fantasy scoring
* Percent owned / percent started
* Schedule-based matchup strings

Robust parsing ensures stability even when ESPN changes response structures.

---

# **7. Docker Containerization (New Section)**

Docker was a critical part of the project because it ensures:

* **Consistency:** The backend runs identically on your machine, Render’s cloud servers, or any Linux environment.
* **Isolation:** Avoids issues with Python versioning, missing system packages, etc.
* **Portability:** The entire backend can be deployed with a single command.

---

## **7.1 Why Docker Was Necessary**

Render.com can deploy Python services without Docker, but using Docker gives:

### **✓ Predictable Runtime Environment**

No dependency mismatch between local development and cloud deployment.

### **✓ Controlled Install Process**

The Dockerfile explicitly states:

* Python version
* System-level dependencies
* Installed pip packages
* Working directory
* Startup command (`uvicorn`)

### **✓ Fast Redeployment**

Once built, Render only needs to pull the updated container instead of reconstructing the environment.

---

## **7.2 Docker Architecture for This Project**

### **Core Files Used:**

#### **Dockerfile**

Defines how the backend container is built:

* Base image: `python:3.12-slim`
* Install packages from `requirements.txt`
* Copy source code into container
* Command to run FastAPI via Uvicorn:

```
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000"]
```

#### **Render Build Command**

Render uses the Dockerfile to:

1. Build the image
2. Start the FastAPI server inside the container
3. Expose that port to the public (`fftradewizard.onrender.com`)

---

## **7.3 Docker Workflow Used in Development**

### **Local Testing**

You can build and test the backend locally:

```
docker build -t fftradewizard-backend .
docker run -p 8000:10000 fftradewizard-backend
```

Then visit:

```
http://localhost:8000/health
```

### **Deployment via Render**

Render simply reuses:

* Your Dockerfile
* Automatic build triggers on GitHub push

This ensures the backend always deploys successfully and behaves exactly the same way locally and in production.

---

# **8. Full Deployment Pipeline**

### **Frontend (Netlify)**

* Builds React + Vite into optimized static files
* Serves UI globally via CDN
* Uses environment variable for backend URL
* Communicates with backend over HTTPS

### **Backend (Render)**

* Runs inside a Docker container
* Serves JSON API to the frontend
* Logs all ESPN calls and errors
* Handles all scoring and calculations

### **Cross-Origin Resource Sharing (CORS)**

Configured on FastAPI to allow:

* Netlify → Render communication
* Local development environments

This resolved earlier issues where browser fetch requests were blocked.

---

# **9. Engineering Challenges & Resolutions**

### **1. Undocumented ESPN API**

Solved with:

* Reverse engineering
* Defensive parsing
* Logging unknown structures

### **2. CORS Blocking Frontend Requests**

Solved with:

```
allow_origins=["*"]
```

during development, then locked down in production.

### **3. Player stats coming back as zero**

Solved by:

* Fixing stat ID interpretation
* Ensuring correct scoring period ID
* Adjusting ESPN projection logic

### **4. Render import errors**

Solved by:

* Correcting import paths
* Moving `TradeRequest` to `schemas.py`
* Adding missing functions like `get_player_pool`

### **5. Docker not executing correctly**

Solved by:

* Fixing Uvicorn startup path
* Adjusting EXPOSE port
* Updating Render service settings

---

# **10. Final System Capabilities**

FFTradeWizard provides:

### ✔ Live ROS rankings

### ✔ Weekly projection display

### ✔ Season-to-date fantasy scoring

### ✔ Matchup difficulty indicators

### ✔ Position filtering

### ✔ Trade analyzer with automated verdict

### ✔ Cloud deployment through Docker & Render

### ✔ Production-ready UI on Netlify

This far exceeds requirements for an introductory engineering course and demonstrates full-stack proficiency.

---

# **11. Educational Outcomes**

This project allowed me to apply concepts from:

### **Software Engineering**

* Modular architecture
* Data modeling
* REST API development
* Containerization

### **Systems Programming**

* Docker
* Dependency management
* Cloud orchestration

### **Web Development**

* React component design
* State management
* API integration

### **Algorithm Design**

* Weighted scoring systems
* Data ranking algorithms
* Trade fairness evaluation

### **Problem Solving**

* Debugging multi-layer systems
* Interpreting undocumented APIs
* Managing state across backend & frontend

This project significantly elevated my confidence in building real-world software and deploying production-level systems.

---

# **12. Conclusion**

FFTradeWizard is a sophisticated analytics platform built on robust engineering principles, modern web technologies, and cloud deployment best practices.

The integration of:

* **FastAPI**
* **React**
* **ESPN Data**
* **Custom Algorithms**
* **Docker**
* **Render Deployment**

…shows a level of technical depth well beyond the typical expectations of an introductory engineering course.

This project stands as a portfolio-quality demonstration of full-stack engineering proficiency and practical software development capability.

