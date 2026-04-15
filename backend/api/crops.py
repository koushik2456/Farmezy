"""
Crops API Router.
Endpoints:
  GET  /api/crops               → list all crops
  GET  /api/crops/{id}          → crop detail
  GET  /api/crops/{id}/history  → price history + 14-day forecast
  POST /api/crops/{id}/refresh  → fetch latest Agmarknet data + recompute ML
"""

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.models.schema import Crop, PriceData
from backend.schemas.pydantic_models import CropResponse, CropWithHistory, PriceDataResponse
from backend.services.pipeline_service import refresh_crop_pipeline

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/", response_model=List[CropResponse], summary="List all crops")
def list_crops(db: Session = Depends(get_db)):
    """Return all crops with current prices and risk metrics."""
    return db.query(Crop).order_by(Crop.name).all()


@router.get("/{crop_id}", response_model=CropResponse, summary="Get crop by ID")
def get_crop(crop_id: int, db: Session = Depends(get_db)):
    """Return a single crop by ID."""
    crop = db.query(Crop).filter(Crop.id == crop_id).first()
    if not crop:
        raise HTTPException(status_code=404, detail=f"Crop {crop_id} not found")
    return crop


@router.get(
    "/{crop_id}/history",
    response_model=CropWithHistory,
    summary="Get crop with price history and forecast",
)
def get_crop_history(crop_id: int, db: Session = Depends(get_db)):
    """
    Return crop detail + merged price history (historical + 14-day forecast).
    Historical rows have `price` set; forecast rows have `predicted` set.
    """
    crop = db.query(Crop).filter(Crop.id == crop_id).first()
    if not crop:
        raise HTTPException(status_code=404, detail=f"Crop {crop_id} not found")

    history = (
        db.query(PriceData)
        .filter(PriceData.crop_id == crop_id)
        .order_by(PriceData.date)
        .all()
    )
    # Build response manually to attach history
    result = CropWithHistory.model_validate(crop)
    result.price_history = [PriceDataResponse.model_validate(h) for h in history]
    return result


@router.post(
    "/{crop_id}/refresh",
    summary="Refresh crop data from Agmarknet + recompute ML",
)
def refresh_crop(
    crop_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Trigger a live Agmarknet fetch for this crop, insert new price records,
    and schedule ML forecast recomputation in the background.
    """
    crop = db.query(Crop).filter(Crop.id == crop_id).first()
    if not crop:
        raise HTTPException(status_code=404, detail=f"Crop {crop_id} not found")

    # Run full pipeline in background with a fresh DB session.
    background_tasks.add_task(refresh_crop_pipeline, crop_id)

    return {"message": f"Refresh queued for {crop.name}", "crop_id": crop_id, "crop_name": crop.name}
