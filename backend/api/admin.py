"""
Admin API for monitoring pipeline health and model lifecycle.
"""

from __future__ import annotations

from datetime import date
from typing import Dict, List

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.models.schema import Crop, PriceData
from backend.services.agmarknet_client import get_agmarknet_config_status
from backend.services.model_service import train_and_save_shock_model
from backend.services.pipeline_service import get_pipeline_stats, refresh_all_crops_pipeline

router = APIRouter()


@router.get("/status", summary="Get pipeline and data freshness status")
def get_status(db: Session = Depends(get_db)):
    stats = get_pipeline_stats()
    latest_actual = (
        db.query(PriceData.crop_id, func.max(PriceData.date).label("latest_date"))
        .filter(PriceData.is_forecast.is_(False))
        .group_by(PriceData.crop_id)
        .all()
    )
    crop_map = {c.id: c.name for c in db.query(Crop).all()}

    freshness: List[Dict[str, object]] = []
    for row in latest_actual:
        latest_date = row.latest_date
        freshness.append(
            {
                "crop_id": row.crop_id,
                "crop_name": crop_map.get(row.crop_id, f"Crop {row.crop_id}"),
                "latest_actual_date": latest_date.isoformat() if latest_date else None,
                "days_since_update": (date.today() - latest_date).days if latest_date else None,
            }
        )

    stale_count = len([f for f in freshness if (f.get("days_since_update") or 0) > 2])
    return {
        "pipeline": stats,
        "agmarknet": get_agmarknet_config_status(),
        "freshness": freshness,
        "stale_crops": stale_count,
        "total_crops": len(freshness),
    }


@router.post("/refresh-all", summary="Refresh all crops in background")
def refresh_all(background_tasks: BackgroundTasks):
    background_tasks.add_task(refresh_all_crops_pipeline)
    return {"message": "Refresh-all queued"}


@router.post("/train-shock-model", summary="Train and persist shock model")
def train_shock_model(db: Session = Depends(get_db)):
    return train_and_save_shock_model(db)
