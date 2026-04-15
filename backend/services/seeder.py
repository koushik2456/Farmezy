"""
Database Seeder — Step 2.
Seeds the PostgreSQL database with:
  1. Crops from mockData.ts (as starting point)
  2. Markets from mockData.ts
  3. Alerts from mockData.ts
  4. Historical PriceData pulled live from the Agmarknet local scraper

Run: python -m backend.services.seeder
"""

import logging
import sys
from datetime import datetime, date

# Make sure project root is on path when running directly
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from backend.core.database import SessionLocal, create_all_tables
from backend.models.schema import Crop, Market, Alert, PriceData, RiskLevel, Trend
from backend.services.agmarknet_client import fetch_prices

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# ── Seed Data (mirrors app/data/mockData.ts) ──────────────────────────────────

CROPS_SEED = [
    {"name": "Wheat",      "name_hindi": "गेहूं",    "current_price": 2150, "risk_level": RiskLevel.low,    "price_change": 2.5,   "predicted_shock": 15, "trend": Trend.up,     "season": "Rabi"},
    {"name": "Rice",       "name_hindi": "चावल",    "current_price": 3200, "risk_level": RiskLevel.medium, "price_change": -3.2,  "predicted_shock": 45, "trend": Trend.down,   "season": "Kharif"},
    {"name": "Onion",      "name_hindi": "प्याज",   "current_price": 1800, "risk_level": RiskLevel.high,   "price_change": -12.5, "predicted_shock": 75, "trend": Trend.down,   "season": "Rabi & Kharif"},
    {"name": "Tomato",     "name_hindi": "टमाटर",   "current_price": 2500, "risk_level": RiskLevel.high,   "price_change": -15.8, "predicted_shock": 82, "trend": Trend.down,   "season": "Kharif"},
    {"name": "Potato",     "name_hindi": "आलू",     "current_price": 1200, "risk_level": RiskLevel.low,    "price_change": 1.8,   "predicted_shock": 20, "trend": Trend.stable, "season": "Rabi"},
    {"name": "Cotton",     "name_hindi": "कपास",    "current_price": 6500, "risk_level": RiskLevel.medium, "price_change": -5.5,  "predicted_shock": 50, "trend": Trend.down,   "season": "Kharif"},
    {"name": "Soybean",    "name_hindi": "सोयाबीन", "current_price": 4200, "risk_level": RiskLevel.low,    "price_change": 3.2,   "predicted_shock": 18, "trend": Trend.up,     "season": "Kharif"},
    {"name": "Sugarcane",  "name_hindi": "गन्ना",   "current_price": 310,  "risk_level": RiskLevel.low,    "price_change": 0.5,   "predicted_shock": 12, "trend": Trend.stable, "season": "Year-round"},
]

MARKETS_SEED = [
    {"name": "Azadpur Mandi",      "state": "Delhi",       "risk_level": RiskLevel.high,   "high_risk_crops": 3, "total_crops": 12, "average_price_change": -8.5},
    {"name": "Vashi APMC",         "state": "Maharashtra", "risk_level": RiskLevel.medium, "high_risk_crops": 2, "total_crops": 15, "average_price_change": -4.2},
    {"name": "Koyambedu Market",   "state": "Tamil Nadu",  "risk_level": RiskLevel.medium, "high_risk_crops": 2, "total_crops": 18, "average_price_change": -3.8},
    {"name": "Lasalgaon Market",   "state": "Maharashtra", "risk_level": RiskLevel.high,   "high_risk_crops": 4, "total_crops": 8,  "average_price_change": -11.2},
    {"name": "Binnypet Market",    "state": "Karnataka",   "risk_level": RiskLevel.low,    "high_risk_crops": 1, "total_crops": 14, "average_price_change": 1.5},
    {"name": "Gaddiannaram Market","state": "Telangana",   "risk_level": RiskLevel.low,    "high_risk_crops": 0, "total_crops": 10, "average_price_change": 2.8},
]

# Agmarknet live fetch config: (crop_name, state, city)
AGMARKNET_FETCH_CONFIG = [
    ("Potato",    "Karnataka",   "Bangalore"),
    ("Tomato",    "Maharashtra", "Mumbai"),
    ("Onion",     "Maharashtra", "Lasalgaon"),
    ("Wheat",     "Delhi",       "Delhi"),
    ("Rice",      "Tamil Nadu",  "Chennai"),
    ("Cotton",    "Telangana",   "Hyderabad"),
    ("Soybean",   "Maharashtra", "Pune"),
    ("Sugarcane", "Uttar Pradesh", "Muzaffarnagar"),
]


# ── Seeder Functions ──────────────────────────────────────────────────────────

def seed_crops(db) -> dict[str, int]:
    """Insert crops, return name→id map."""
    crop_map: dict[str, int] = {}
    for data in CROPS_SEED:
        existing = db.query(Crop).filter(Crop.name == data["name"]).first()
        if existing:
            crop_map[data["name"]] = existing.id
            logger.info("Crop already exists: %s", data["name"])
            continue
        crop = Crop(**data)
        db.add(crop)
        db.flush()
        crop_map[data["name"]] = crop.id
        logger.info("Seeded crop: %s (id=%d)", crop.name, crop.id)
    db.commit()
    return crop_map


def seed_markets(db) -> dict[str, int]:
    """Insert markets, return name→id map."""
    market_map: dict[str, int] = {}
    for data in MARKETS_SEED:
        existing = db.query(Market).filter(Market.name == data["name"]).first()
        if existing:
            market_map[data["name"]] = existing.id
            continue
        market = Market(**data)
        db.add(market)
        db.flush()
        market_map[data["name"]] = market.id
        logger.info("Seeded market: %s (id=%d)", market.name, market.id)
    db.commit()
    return market_map


def seed_alerts(db, crop_map: dict, market_map: dict) -> None:
    """Insert static alerts (mirrors mockData.ts)."""
    alerts_data = [
        {"crop": "Tomato",  "market": "Azadpur Mandi",   "risk_level": RiskLevel.high,   "message": "High price shock risk detected for Tomato in next 7 days",          "date": date(2026, 2, 23), "is_read": False, "recommendation": "Consider storing produce or selling in nearby markets with better prices"},
        {"crop": "Onion",   "market": "Lasalgaon Market", "risk_level": RiskLevel.high,   "message": "Sudden supply increase expected - price drop likely",                 "date": date(2026, 2, 23), "is_read": False, "recommendation": "Sell immediately or arrange cold storage facilities"},
        {"crop": "Rice",    "market": "Vashi APMC",       "risk_level": RiskLevel.medium, "message": "Moderate price fluctuation expected due to seasonal factors",         "date": date(2026, 2, 22), "is_read": True,  "recommendation": "Monitor market for next 3-4 days before making selling decision"},
        {"crop": "Cotton",  "market": "Azadpur Mandi",   "risk_level": RiskLevel.medium, "message": "Weather conditions may affect prices in coming week",                 "date": date(2026, 2, 22), "is_read": True,  "recommendation": "Wait for weather stabilization or explore alternative markets"},
        {"crop": "Wheat",   "market": "Binnypet Market", "risk_level": RiskLevel.low,    "message": "Stable prices expected - good time to sell",                        "date": date(2026, 2, 21), "is_read": True,  "recommendation": "Current market conditions are favorable for selling"},
    ]
    for data in alerts_data:
        crop_id = crop_map.get(data["crop"])
        market_id = market_map.get(data["market"])
        if not crop_id or not market_id:
            logger.warning("Skipping alert — crop/market not found: %s / %s", data["crop"], data["market"])
            continue
        existing = db.query(Alert).filter(
            Alert.crop_id == crop_id,
            Alert.market_id == market_id,
            Alert.date == data["date"],
        ).first()
        if existing:
            continue
        alert = Alert(
            crop_id=crop_id,
            market_id=market_id,
            risk_level=data["risk_level"],
            message=data["message"],
            recommendation=data["recommendation"],
            date=data["date"],
            is_read=data["is_read"],
        )
        db.add(alert)
        logger.info("Seeded alert: %s @ %s", data["crop"], data["market"])
    db.commit()


def seed_price_history(db, crop_map: dict) -> None:
    """
    Fetch real historical prices from the Agmarknet local scraper and insert into price_data.
    Falls back gracefully if the scraper is not running.
    """
    for crop_name, state, city in AGMARKNET_FETCH_CONFIG:
        crop_id = crop_map.get(crop_name)
        if not crop_id:
            logger.warning("Crop not in DB, skipping: %s", crop_name)
            continue

        records = fetch_prices(crop_name, state, city)
        if not records:
            logger.warning("No Agmarknet data for %s @ %s, %s — skipping price history", crop_name, city, state)
            continue

        inserted = 0
        for rec in records:
            if not rec.date:
                continue
            rec_date = rec.date.date()
            # Avoid duplicates
            existing = db.query(PriceData).filter(
                PriceData.crop_id == crop_id,
                PriceData.date == rec_date,
                PriceData.is_forecast == False,
            ).first()
            if existing:
                continue
            pd = PriceData(
                crop_id=crop_id,
                date=rec_date,
                price=rec.modal_price,
                predicted=None,
                shock_probability=None,
                is_forecast=False,
            )
            db.add(pd)
            inserted += 1

        db.commit()
        logger.info("Seeded %d price records for %s", inserted, crop_name)


def run_seed():
    """Main seeder entry point."""
    logger.info("Creating tables if they do not exist...")
    create_all_tables()

    db = SessionLocal()
    try:
        logger.info("--- Seeding Crops ---")
        crop_map = seed_crops(db)

        logger.info("--- Seeding Markets ---")
        market_map = seed_markets(db)

        logger.info("--- Seeding Alerts ---")
        seed_alerts(db, crop_map, market_map)

        logger.info("--- Fetching & Seeding Price History from Agmarknet ---")
        seed_price_history(db, crop_map)

        logger.info("✅ Database seeding complete.")
    except Exception:
        db.rollback()
        logger.exception("Seeding failed — rolled back.")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
