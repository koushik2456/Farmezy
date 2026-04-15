"""
Markets API Router.
Endpoints:
  GET /api/markets          → list all markets
  GET /api/markets/{id}     → market detail
"""

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.models.schema import Market, Crop
from backend.schemas.pydantic_models import (
    MarketResponse,
    CropResponse,
    MarketCropComparisonResponse,
    MarketComparisonBundle,
)

logger = logging.getLogger(__name__)
router = APIRouter()

# Approximate one-way road distance (km) from Chennai, Tamil Nadu, to each mandi / hub city.
# Used so FPO / farmer scenarios “shipping from Chennai” see consistent distance + transport estimates.
DISTANCE_FROM_CHENNAI_KM: dict[str, int] = {
    "Koyambedu Market": 8,  # Chennai wholesale cluster
    "Binnypet Market": 348,  # Bengaluru
    "Gaddiannaram Market": 627,  # Hyderabad area
    "Vashi APMC": 1285,  # Navi Mumbai
    "Lasalgaon Market": 1360,  # Nashik district (major onion mandi)
    "Azadpur Mandi": 2190,  # Delhi NCR
}


def _distance_km_from_chennai(market_name: str) -> int:
    if market_name in DISTANCE_FROM_CHENNAI_KM:
        return DISTANCE_FROM_CHENNAI_KM[market_name]
    logger.warning("No Chennai-distance mapping for market %r — using default 500 km", market_name)
    return 500


def _transport_cost_per_quintal(distance_km: int) -> float:
    """Illustrative: base loading + per-km haul (₹/quintal). Not a live freight quote."""
    return round(25.0 + distance_km * 0.095, 2)


MARKET_CROP_MAP = {
    "Azadpur Mandi": ["Wheat", "Rice", "Onion", "Tomato", "Potato", "Cotton"],
    "Vashi APMC": ["Rice", "Onion", "Tomato", "Potato", "Soybean"],
    "Koyambedu Market": ["Rice", "Tomato"],
    "Lasalgaon Market": ["Onion"],
    "Binnypet Market": ["Wheat", "Onion", "Tomato", "Potato", "Sugarcane"],
    "Gaddiannaram Market": ["Rice", "Wheat", "Potato", "Cotton"],
}


@router.get("/", response_model=List[MarketResponse], summary="List all markets")
def list_markets(db: Session = Depends(get_db)):
    """Return all markets with aggregated risk levels."""
    return db.query(Market).order_by(Market.state, Market.name).all()


@router.get("/{market_id}", response_model=MarketResponse, summary="Get market by ID")
def get_market(market_id: int, db: Session = Depends(get_db)):
    """Return a single market by ID."""
    market = db.query(Market).filter(Market.id == market_id).first()
    if not market:
        raise HTTPException(status_code=404, detail=f"Market {market_id} not found")
    return market


@router.get("/{market_id}/crops", response_model=List[CropResponse], summary="List crops for a market")
def list_market_crops(market_id: int, db: Session = Depends(get_db)):
    market = db.query(Market).filter(Market.id == market_id).first()
    if not market:
        raise HTTPException(status_code=404, detail=f"Market {market_id} not found")

    crop_names = MARKET_CROP_MAP.get(market.name, [])
    if not crop_names:
        return []

    crops = db.query(Crop).filter(Crop.name.in_(crop_names)).order_by(Crop.name).all()
    return crops


@router.get("/comparison/{crop_id}", response_model=MarketComparisonBundle, summary="Compare crop across markets (from Chennai)")
def compare_crop_across_markets(crop_id: int, db: Session = Depends(get_db)):
    crop = db.query(Crop).filter(Crop.id == crop_id).first()
    if not crop:
        raise HTTPException(status_code=404, detail=f"Crop {crop_id} not found")

    markets = db.query(Market).order_by(Market.name).all()
    rows: List[MarketCropComparisonResponse] = []
    for market in markets:
        volatility_factor = abs(market.average_price_change) / 100.0
        base_adjustment = 1 + (market.average_price_change / 100.0) * 0.35
        price = max(1.0, crop.current_price * base_adjustment)
        shock = min(100.0, max(0.0, crop.predicted_shock + market.high_risk_crops * 2.5))
        distance_km = _distance_km_from_chennai(market.name)
        transport_cost = _transport_cost_per_quintal(distance_km)
        demand_level = "high" if market.risk_level.value == "low" else "medium" if market.risk_level.value == "medium" else "low"
        trend = crop.trend
        if volatility_factor > 0.08 and crop.trend.value == "stable":
            trend = type(crop.trend).down

        rows.append(
            MarketCropComparisonResponse(
                market_id=market.id,
                market_name=market.name,
                state=market.state,
                current_price=round(price, 2),
                risk_level=market.risk_level.value,
                predicted_shock=round(shock, 1),
                price_change=round(crop.price_change + market.average_price_change * 0.2, 2),
                distance_km=distance_km,
                transport_cost=transport_cost,
                demand_level=demand_level,
                storage_available=market.risk_level.value != "high",
                trend=trend.value,
            )
        )
    return MarketComparisonBundle(markets=rows)
