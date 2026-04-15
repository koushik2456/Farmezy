# Farmezy

Farmezy is a crop price monitoring and risk analysis platform with:

- a FastAPI backend for data ingestion, forecasting, and alerts
- a Vite + React frontend for dashboards and admin controls
- Agmarknet/data.gov.in integration for mandi price data

## Tech Stack

- Frontend: React, Vite, TypeScript, Tailwind
- Backend: FastAPI, SQLAlchemy, Pydantic, APScheduler
- ML: Prophet, scikit-learn, XGBoost

## Project Structure

- `app/` - frontend application
- `backend/` - API, data services, and ML logic
- `styles/` - shared styling assets
- `run-dev.ps1` - local development launcher

## Run Locally

1. Install Node and Python dependencies.
2. Configure `backend/.env` with required settings.
3. Start development stack:

```powershell
.\run-dev.ps1 -SeedData:$false -TrainModel:$false -OpenBrowser:$false -InstallDeps:$false
```

Frontend runs on `http://localhost:5173` and backend on `http://localhost:8000`.
