# FFTradeWizard Backend

Backend service for **FFTradeWizard**, built with **Python** and **FastAPI**.

## Tech Stack

- Python
- FastAPI
- Pydantic
- Uvicorn

## Running Locally

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
``

The API will be available at `http://localhost:8000`.

### Useful Endpoints

- `GET /health`
- `GET /players`
- `GET /rankings/ros?position=WR`
- `POST /trade/analyze`

## Docker

```bash
cd backend
docker build -t fftradewizard-backend .
docker run -p 8000:8000 fftradewizard-backend
```
