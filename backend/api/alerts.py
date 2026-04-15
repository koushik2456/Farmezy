"""
Alerts API Router.
Endpoints:
  GET   /api/alerts               → list all alerts (optionally unread only)
  PATCH /api/alerts/{id}/read     → mark alert as read
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from backend.core.database import get_db
from backend.models.schema import Alert
from backend.schemas.pydantic_models import AlertResponse, AlertMarkRead

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=List[AlertResponse], summary="List alerts")
def list_alerts(
    unread_only: bool = Query(False, description="Return only unread alerts"),
    db: Session = Depends(get_db),
):
    """
    Return all alerts sorted by date descending.
    Use `?unread_only=true` to filter unread alerts only.
    """
    query = (
        db.query(Alert)
        .options(joinedload(Alert.crop_rel), joinedload(Alert.market_rel))
        .order_by(Alert.date.desc(), Alert.id.desc())
    )
    if unread_only:
        query = query.filter(Alert.is_read == False)

    alerts = query.all()

    # Build response including resolved crop_name and market_name
    results = []
    for alert in alerts:
        data = AlertResponse.model_validate(alert)
        data.crop_name = alert.crop_rel.name if alert.crop_rel else None
        data.market_name = alert.market_rel.name if alert.market_rel else None
        results.append(data)
    return results


@router.patch("/{alert_id}/read", response_model=AlertResponse, summary="Mark alert as read")
def mark_alert_read(
    alert_id: int,
    payload: AlertMarkRead,
    db: Session = Depends(get_db),
):
    """Mark a specific alert as read (or unread)."""
    alert = (
        db.query(Alert)
        .options(joinedload(Alert.crop_rel), joinedload(Alert.market_rel))
        .filter(Alert.id == alert_id)
        .first()
    )
    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")

    alert.is_read = payload.is_read
    db.commit()
    db.refresh(alert)

    result = AlertResponse.model_validate(alert)
    result.crop_name = alert.crop_rel.name if alert.crop_rel else None
    result.market_name = alert.market_rel.name if alert.market_rel else None
    return result
