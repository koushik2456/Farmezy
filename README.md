# Farmezy

Farmezy is a crop price monitoring and risk analysis platform with:

- a FastAPI backend for data ingestion, forecasting, and alerts
- a Vite + React frontend for dashboards and admin controls
- Agmarknet/data.gov.in integration for mandi price data

## Tech Stack

- Frontend: React, Vite, TypeScript, Tailwind
- Backend: FastAPI, SQLAlchemy, Pydantic, APScheduler
- ML: scikit-learn (Ridge + weekly seasonality for price curves; RandomForest for shock probability)

## Project Structure

- `app/` - frontend application
- `backend/` - API, data services, and ML logic
- `styles/` - shared styling assets
- `run-dev.ps1` / `run-den.ps1` - local development launcher (same script; `run-den` is a typo-friendly alias)

## Run Locally

1. Install Node and Python dependencies.
2. Copy `backend/.env.example` to `backend/.env` and set `DATABASE_URL`, `AGMARKNET_API_KEY`, and `FRONTEND_ORIGIN` as needed.
3. Start development stack.

**Windows PowerShell** does not run scripts from the current folder unless you prefix them with `.\`. Use **`.\run-dev.ps1`** (not `run-dev.ps1`). Alternatively run **`run-dev.cmd`** from the same folder, or double-click `run-dev.cmd` in File Explorer.

```powershell
.\run-dev.ps1 -SeedData:$false -TrainModel:$false -OpenBrowser:$false -InstallDeps:$false
```

Frontend runs on `http://localhost:5173` and backend on `http://localhost:8000`.

## Backend with Conda (optional)

You can use a plain **venv + pip** (`python -m venv .venv` then `pip install -r backend/requirements.txt`). **Conda** is optional; `backend/environment.yml` only pins Python 3.11 and installs the same `requirements.txt` — no Stan or Prophet.

### 1. Install Conda

Install [Miniconda](https://docs.conda.io/en/latest/miniconda.html) or Anaconda. Open **Anaconda Prompt** (Windows) or a terminal where `conda` works.

### 2. Go to the repo root

The directory that contains the `backend` folder (example: `cd Desktop\Sepm_project`).

### 3. Create and activate the environment

```bash
conda env create -f backend/environment.yml
conda activate sepm-crop
```

Recreate from scratch if you change the yml:

```bash
conda env remove -n sepm-crop -y
conda env create -f backend/environment.yml
conda activate sepm-crop
```

### 4. Configure `backend/.env`

Copy `backend/.env.example` to `backend/.env` and set at least `DATABASE_URL`, `AGMARKNET_API_KEY`, and `FRONTEND_ORIGIN`.

### 5. Set `PYTHONPATH` to the repo root

**PowerShell (Windows):**

```powershell
$env:PYTHONPATH = (Get-Location).Path
```

**Command Prompt:**

```cmd
set PYTHONPATH=%CD%
```

**macOS / Linux:**

```bash
export PYTHONPATH="$(pwd)"
```

### 6. Run the API

```bash
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

Open `http://127.0.0.1:8000/docs`.

### Git / CI

- `backend/.env` is **gitignored**; only `backend/.env.example` is committed.
- **`.github/workflows/backend.yml`** installs `backend/requirements.txt` on Ubuntu on push/PR when backend files change.
