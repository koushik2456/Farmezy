"""
FastAPI Application Entry Point.
Configures CORS for Vite frontend and includes all API routers.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler

from backend.core.config import settings
from backend.core.database import create_all_tables
from backend.core.stan_logging import silence_cmdstan_loggers
from backend.api import crops, markets, alerts, admin
from backend.services.agmarknet_client import log_agmarknet_startup_status
from backend.services.pipeline_service import refresh_all_crops_pipeline

app = FastAPI(
    title="Crop Price Prediction API",
    description="Backend API for crop price monitoring, risk alerts, and ML-based price shock prediction.",
    version="1.0.0",
)
scheduler = BackgroundScheduler()

# ----- CORS Middleware -----
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----- Startup: ensure all tables exist -----
@app.on_event("startup")
def on_startup():
    silence_cmdstan_loggers()

    create_all_tables()
    log_agmarknet_startup_status()
    if not scheduler.running:
        scheduler.add_job(_scheduled_refresh, "interval", minutes=60, id="hourly_refresh", replace_existing=True)
        scheduler.start()


@app.on_event("shutdown")
def on_shutdown():
    if scheduler.running:
        scheduler.shutdown(wait=False)


def _scheduled_refresh() -> None:
    refresh_all_crops_pipeline()


# ----- Health check -----
@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "message": "Crop Price Prediction API is running.",
        "docs": "/docs",
        "hint": "The React UI is separate: in project root run `npm run dev`, then open http://localhost:5173",
    }


# ----- API Routers -----
app.include_router(crops.router,   prefix="/api/crops",   tags=["Crops"])
app.include_router(markets.router, prefix="/api/markets", tags=["Markets"])
app.include_router(alerts.router,  prefix="/api/alerts",  tags=["Alerts"])
app.include_router(admin.router,   prefix="/api/admin",   tags=["Admin"])

