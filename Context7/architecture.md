# Context7 - Backend Architecture & Design Decisions

## 1. Project Goals
- Transform the existing mock-data-driven frontend into a fully functional system powered by a robust backend.
- Provide a reliable, compute-intensive backend (Python/FastAPI) to handle price computations, risk analysis, and alert generation.
- Ensure seamless communication between the Vite/React frontend and the backend via RESTful APIs.

## 2. Design Decisions & System Flow

Role Split:
- **Client (Frontend)**: React + Vite, fetches and displays crop data, markets, historical trends, and reads alerts.
- **Server (Backend)**: Python (FastAPI). Selected for its high performance, asynchronous support, and seamless integration with any potential Machine Learning libraries for price predictions.
- **Database**: PostgreSQL with SQLAlchemy ORM. Suitable for relational data (Markets, Crops) and time-series data (Price History).
- **Compute Layer**: Daily/Hourly chron jobs (e.g., Celery or APScheduler) to compute price shocks, trends, and generate new alerts.

## 3. Folder Structure (Backend)

We will create a new directory for the backend alongside the frontend:
```text
/Sepm_project
├── app/                  # (Existing) Frontend React App
├── Context7/             # Architecture and Design decisions
└── backend/              # [NEW] FastAPI Backend
    ├── main.py           # Application entry point
    ├── core/             # Config, security, database setup
    ├── models/           # SQLAlchemy DB models (Crop, Market, Alert, PriceData)
    ├── schemas/          # Pydantic schemas for request/response validation
    ├── api/              # API routers and endpoints
    ├── services/         # Business logic and computations (Price shock, Risk levels)
    └── requirements.txt  # Python dependencies
```

## 4. APIs & Data Paths

### Crops API
- `GET /api/crops`: List all crops with current prices and risk levels.
- `GET /api/crops/{crop_id}`: Detail view for a specific crop.
- `GET /api/crops/{crop_id}/history`: Fetch price history and future predictions (up to 90 days past, 14 days future).

### Markets API
- `GET /api/markets`: List all markets and aggregated risk levels.
- `GET /api/markets/{market_id}/crops`: List crops available in a specific market.

### Alerts API
- `GET /api/alerts`: Fetch active alerts.
- `PATCH /api/alerts/{alert_id}/read`: Mark an alert as read.

## 5. Implementation Steps for Builder (Claude)

**Step 1: Scaffolding the Backend**
- Initialize the `backend/` folder.
- Create `requirements.txt` containing `fastapi[all]`, `uvicorn`, `sqlalchemy`, `psycopg2-binary`.
- Setup `main.py` with basic CORS middleware allowing updates from the frontend.

**Step 2: Database Models & Schemas**
- Create SQLAlchemy models reflecting the interfaces in `mockData.ts` (Crop, Market, Alert, PriceData).
- Create corresponding Pydantic schemas.

**Step 3: Business Logic & Mock Data Migration**
- Create a script to seed the database with the mock data from `mockData.ts`.
- Implement basic services to fetch this data from the DB.

**Step 4: API Endpoints**
- Build routers for `/api/crops`, `/api/markets`, and `/api/alerts`.
- Wire the endpoints to the frontend, updating the `fetch` calls in React.

## 6. Risks & Optimizations
- **Risk**: Price computation logic might be slow if run synchronously on API requests.
- **Optimization**: Background tasks or cron jobs should pre-compute the 14-day predictions overnight and save them to the DB.
- **Risk**: CORS issues between the local Vite dev server and the FastAPI server.
- **Optimization**: Builder must configure FastAPI CORS middleware correctly for `localhost:5173`.

## 6. External Data APIs & Machine Learning Models

### External Live Data API
To move away from mock data, we will integrate a live agricultural API:
- **Primary Choice**: **Agmarknet API (via data.gov.in)**. This is the official and free Indian government portal for Mandi prices across 3000+ markets.
- **Alternative Choice**: **APIFarmer** or **eNAM API** for real-time commodity pricing.

### Machine Learning Models
To compute "price trends" and "predicted shocks", the backend will utilize:
- **Price Forecasting (Next 14 days)**: **Prophet** (by Meta). Highly optimized for time-series forecasting with strong seasonal mapping (perfect for Rabi/Kharif crop seasons).
- **Price Shock/Risk Detection**: **XGBoost Classifier** or **Isolation Forest** (Anomaly Detection). These models will analyze historical price volatility and external factors (like sudden supply changes) to trigger "high risk" crop alerts.

## 7. Missing Inputs (Need User Confirmation)
- Do you approve using the **Agmarknet API (data.gov.in)** for fetching live mandi prices?
- Do you approve using **Prophet** for forecasting and **XGBoost/Isolation Forest** for price shock detection?
- Once confirmed, Claude (Builder) can begin step 1.
