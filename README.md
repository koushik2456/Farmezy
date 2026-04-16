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
2. Copy `backend/.env.example` to `backend/.env` and set `DATABASE_URL`, `AGMARKNET_API_KEY`, and `FRONTEND_ORIGIN` as needed.
3. Start development stack:

```powershell
.\run-dev.ps1 -SeedData:$false -TrainModel:$false -OpenBrowser:$false -InstallDeps:$false
```

Frontend runs on `http://localhost:5173` and backend on `http://localhost:8000`.

## Backend with Conda (recommended — Prophet / CmdStan)

Prophet uses CmdStan. On Windows, **Store Python + plain pip** often hits `Operation not permitted` on Stan binaries. Use **Conda** with `backend/environment.yml`: it pulls **cmdstan** from conda-forge and installs the rest via pip.

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

### 7. If Prophet still cannot find Stan

With `conda activate sepm-crop`, note `CONDA_PREFIX` (e.g. `echo %CONDA_PREFIX%` in cmd). Add to `backend/.env` a line like (path varies slightly by install):

```env
CMDSTAN=C:\Users\YOU\miniconda3\envs\sepm-crop\Library\lib\cmdstan
```

Use the folder that actually contains the CmdStan install (search under `%CONDA_PREFIX%` for a directory named `cmdstan` if needed). Restart uvicorn after saving.

### Git / CI

- `backend/.env` is **gitignored**; only `backend/.env.example` is committed.
- **`.github/workflows/backend.yml`** installs `backend/requirements.txt` on Ubuntu on push/PR when backend files change.
