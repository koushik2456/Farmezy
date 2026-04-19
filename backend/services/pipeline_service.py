"""
Pipeline service for ingestion + ML recomputation.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Dict

from backend.core.database import SessionLocal
from backend.models.schema import Crop, PriceData
from backend.data.crop_catalog import CROP_MARKET_MAP
from backend.services.agmarknet_client import fetch_prices
from backend.services.ml_service import generate_and_save_forecasts, recompute_crop_risk

logger = logging.getLogger(__name__)

PIPELINE_STATS: Dict[str, object] = {
    "total_runs": 0,
    "failed_runs": 0,
    "last_run_at": None,
    "last_success_at": None,
    "last_error": None,
}


def get_pipeline_stats() -> Dict[str, object]:
    return dict(PIPELINE_STATS)


def refresh_crop_pipeline(crop_id: int) -> dict:
    """
    Fetch latest mandi data, insert records, then recompute risk + forecasts.
    Uses its own DB session so it is safe to run as background task.
    """
    PIPELINE_STATS["total_runs"] = int(PIPELINE_STATS["total_runs"]) + 1
    PIPELINE_STATS["last_run_at"] = datetime.utcnow().isoformat()
    db = SessionLocal()
    try:
        crop = db.query(Crop).filter(Crop.id == crop_id).first()
        if not crop:
            return {"message": f"Crop {crop_id} not found", "new_rows": 0}

        state, city = CROP_MARKET_MAP.get(crop.name, ("", ""))
        if not state:
            return {"message": f"No Agmarknet config for {crop.name}", "new_rows": 0}

        records = fetch_prices(crop.name, state, city)
        new_count = 0
        for rec in records:
            if not rec.date:
                continue
            rec_date = rec.date.date()
            exists = (
                db.query(PriceData)
                .filter(
                    PriceData.crop_id == crop_id,
                    PriceData.date == rec_date,
                    PriceData.is_forecast.is_(False),
                )
                .first()
            )
            if exists:
                continue

            db.add(
                PriceData(
                    crop_id=crop_id,
                    date=rec_date,
                    price=rec.modal_price,
                    is_forecast=False,
                )
            )
            new_count += 1

        db.commit()
        recompute_crop_risk(crop_id, db)
        generate_and_save_forecasts(crop_id, db)
        PIPELINE_STATS["last_success_at"] = datetime.utcnow().isoformat()
        PIPELINE_STATS["last_error"] = None
        return {
            "message": f"Fetched {len(records)} records for {crop.name}",
            "new_rows": new_count,
        }
    except Exception as exc:
        db.rollback()
        logger.exception("Refresh pipeline failed for crop %s: %s", crop_id, exc)
        PIPELINE_STATS["failed_runs"] = int(PIPELINE_STATS["failed_runs"]) + 1
        PIPELINE_STATS["last_error"] = str(exc)
        return {"message": f"Refresh failed: {exc}", "new_rows": 0}
    finally:
        db.close()


def refresh_all_crops_pipeline() -> Dict[str, int]:
    db = SessionLocal()
    try:
        crop_ids = [c.id for c in db.query(Crop.id).all()]
    finally:
        db.close()

    processed = 0
    for crop_id in crop_ids:
        refresh_crop_pipeline(crop_id)
        processed += 1
    return {"processed_crops": processed}
