# FFTradeWizard Frontend

React frontend for **FFTradeWizard**, a fantasy football trade & ROS analyzer.

## Tech Stack

- React
- JavaScript
- Vite
- Fetch API to call FastAPI backend

## Running Locally (Dev)

```bash
cd frontend
npm install
npm run dev
```

By default Vite serves at `http://localhost:5173`.

Make sure the backend is running at `http://localhost:8000`.

## Docker

```bash
cd frontend
docker build -t fftradewizard-frontend .
docker run -p 8080:80 fftradewizard-frontend
```
