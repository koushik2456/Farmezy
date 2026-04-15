"""
SQLAlchemy ORM Models.
These models map directly to the TypeScript interfaces in app/data/mockData.ts:
  - Crop     → crops table
  - Market   → markets table
  - Alert    → alerts table
  - PriceData → price_data table
"""

import enum
from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import relationship

from backend.core.database import Base


# ── Enum: mirrors TypeScript  RiskLevel = "low" | "medium" | "high"  ──────────
class RiskLevel(enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"


# ── Enum: mirrors TypeScript  trend: "up" | "down" | "stable"  ───────────────
class Trend(enum.Enum):
    up = "up"
    down = "down"
    stable = "stable"


# ─────────────────────────────────────────────────────────────────────────────
class Crop(Base):
    """
    Mirrors the TypeScript `Crop` interface.
    Stores crop identity, current market price, and risk metrics.
    """
    __tablename__ = "crops"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    name_hindi = Column(String(100), nullable=True)
    current_price = Column(Float, nullable=False)
    unit = Column(String(50), nullable=False, default="₹/quintal")
    risk_level = Column(Enum(RiskLevel), nullable=False, default=RiskLevel.low)
    price_change = Column(Float, nullable=False, default=0.0)   # % change
    predicted_shock = Column(Float, nullable=False, default=0.0) # 0-100 probability
    trend = Column(Enum(Trend), nullable=False, default=Trend.stable)
    season = Column(String(50), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    price_history = relationship("PriceData", back_populates="crop", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="crop_rel", cascade="all, delete-orphan")


# ─────────────────────────────────────────────────────────────────────────────
class Market(Base):
    """
    Mirrors the TypeScript `Market` interface.
    Represents an APMC/Mandi market and its aggregated risk profile.
    """
    __tablename__ = "markets"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(200), nullable=False, unique=True, index=True)
    state = Column(String(100), nullable=False)
    risk_level = Column(Enum(RiskLevel), nullable=False, default=RiskLevel.low)
    high_risk_crops = Column(Integer, nullable=False, default=0)
    total_crops = Column(Integer, nullable=False, default=0)
    average_price_change = Column(Float, nullable=False, default=0.0)  # % avg change
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    alerts = relationship("Alert", back_populates="market_rel", cascade="all, delete-orphan")


# ─────────────────────────────────────────────────────────────────────────────
class Alert(Base):
    """
    Mirrors the TypeScript `Alert` interface.
    Represents a generated risk alert for a crop in a market.
    """
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    crop_id = Column(Integer, ForeignKey("crops.id"), nullable=False)
    market_id = Column(Integer, ForeignKey("markets.id"), nullable=False)
    risk_level = Column(Enum(RiskLevel), nullable=False)
    message = Column(String(500), nullable=False)
    recommendation = Column(String(500), nullable=True)
    date = Column(Date, nullable=False, default=date.today)
    is_read = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    crop_rel = relationship("Crop", back_populates="alerts")
    market_rel = relationship("Market", back_populates="alerts")


# ─────────────────────────────────────────────────────────────────────────────
class PriceData(Base):
    """
    Mirrors the TypeScript `PriceData` interface.
    Stores both historical observed prices and future ML-predicted prices.
    A null `price` with a non-null `predicted` means this row is a forecast point.
    """
    __tablename__ = "price_data"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    crop_id = Column(Integer, ForeignKey("crops.id"), nullable=False)
    date = Column(Date, nullable=False, index=True)
    price = Column(Float, nullable=True)           # Observed/historical price
    predicted = Column(Float, nullable=True)       # ML-predicted price (forecast)
    shock_probability = Column(Float, nullable=True)  # 0–100 % shock probability
    is_forecast = Column(Boolean, nullable=False, default=False)

    # Relationship
    crop = relationship("Crop", back_populates="price_history")
