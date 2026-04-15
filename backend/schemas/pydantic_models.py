"""
Pydantic Schemas for API Request/Response Validation.
These schemas correspond 1:1 with the SQLAlchemy models in models/schema.py
and match the TypeScript interfaces in app/data/mockData.ts.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional
from enum import Enum

from pydantic import BaseModel, ConfigDict


# ── Enums (match TypeScript union types) ─────────────────────────────────────

class RiskLevelEnum(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class TrendEnum(str, Enum):
    up = "up"
    down = "down"
    stable = "stable"


# ── PriceData Schemas ─────────────────────────────────────────────────────────

class PriceDataBase(BaseModel):
    date: date
    price: Optional[float] = None
    predicted: Optional[float] = None
    shock_probability: Optional[float] = None
    is_forecast: bool = False


class PriceDataCreate(PriceDataBase):
    crop_id: int


class PriceDataResponse(PriceDataBase):
    id: int
    crop_id: int

    model_config = ConfigDict(from_attributes=True)


# ── Crop Schemas ──────────────────────────────────────────────────────────────

class CropBase(BaseModel):
    name: str
    name_hindi: Optional[str] = None
    current_price: float
    unit: str = "₹/quintal"
    risk_level: RiskLevelEnum = RiskLevelEnum.low
    price_change: float = 0.0
    predicted_shock: float = 0.0
    trend: TrendEnum = TrendEnum.stable
    season: Optional[str] = None


class CropCreate(CropBase):
    pass


class CropUpdate(BaseModel):
    current_price: Optional[float] = None
    risk_level: Optional[RiskLevelEnum] = None
    price_change: Optional[float] = None
    predicted_shock: Optional[float] = None
    trend: Optional[TrendEnum] = None


class CropResponse(CropBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class CropWithHistory(CropResponse):
    """Crop detail view with full price history (90 days past + 14 days predicted)."""
    price_history: List[PriceDataResponse] = []


# ── Market Schemas ────────────────────────────────────────────────────────────

class MarketBase(BaseModel):
    name: str
    state: str
    risk_level: RiskLevelEnum = RiskLevelEnum.low
    high_risk_crops: int = 0
    total_crops: int = 0
    average_price_change: float = 0.0


class MarketCreate(MarketBase):
    pass


class MarketResponse(MarketBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class MarketCropComparisonResponse(BaseModel):
    """
    Computed crop view per market used on the market comparison screen.
    """
    market_id: int
    market_name: str
    state: str
    current_price: float
    risk_level: RiskLevelEnum
    predicted_shock: float
    price_change: float
    distance_km: int
    transport_cost: float
    demand_level: str
    storage_available: bool
    trend: TrendEnum


class MarketComparisonBundle(BaseModel):
    """
    Multi-market comparison for one crop. Distances are approximate road km from the reference origin (Chennai).
    """
    origin_city: str = "Chennai"
    origin_state: str = "Tamil Nadu"
    origin_note: str = (
        "Distances and transport costs are estimated from Chennai, Tamil Nadu, "
        "as a reference point for farmers / FPOs based in the Chennai region."
    )
    markets: List[MarketCropComparisonResponse]


# ── Alert Schemas ─────────────────────────────────────────────────────────────

class AlertBase(BaseModel):
    risk_level: RiskLevelEnum
    message: str
    recommendation: Optional[str] = None
    date: date
    is_read: bool = False


class AlertCreate(AlertBase):
    crop_id: int
    market_id: int


class AlertMarkRead(BaseModel):
    is_read: bool = True


class AlertResponse(AlertBase):
    id: int
    crop_id: int
    market_id: int
    # Nested names for convenience (mirrors TypeScript Alert.crop / Alert.market strings)
    crop_name: Optional[str] = None
    market_name: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
