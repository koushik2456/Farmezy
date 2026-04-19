"""
Tracked crops + default state/market for data.gov.in Daily Price API queries.
Expand COMMODITY_ALIASES in agmarknet_client.py if a name does not match the portal.
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

from backend.models.schema import RiskLevel, Trend

# (crop_name, state, apmc/market city hint) — must match portal spellings where possible.
CROP_MARKET_MAP: Dict[str, Tuple[str, str]] = {
    # Original set
    "Wheat": ("Delhi", "Delhi"),
    "Rice": ("Tamil Nadu", "Chennai"),
    "Onion": ("Maharashtra", "Lasalgaon"),
    "Tomato": ("Maharashtra", "Mumbai"),
    "Potato": ("Karnataka", "Bangalore"),
    "Cotton": ("Telangana", "Hyderabad"),
    "Soybean": ("Maharashtra", "Pune"),
    "Sugarcane": ("Uttar Pradesh", "Muzaffarnagar"),
    # Vegetables & fruit (major mandis; adjust if your API returns 0 rows)
    "Brinjal": ("Maharashtra", "Mumbai"),
    "Cabbage": ("Delhi", "Delhi"),
    "Cauliflower": ("Delhi", "Delhi"),
    "Bhindi": ("Maharashtra", "Mumbai"),
    "Green Chilli": ("Maharashtra", "Mumbai"),
    "Garlic": ("Maharashtra", "Lasalgaon"),
    "Ginger": ("Karnataka", "Bangalore"),
    "Carrot": ("Delhi", "Delhi"),
    "Spinach": ("Delhi", "Delhi"),
    "Coriander": ("Delhi", "Delhi"),
    "Methi": ("Delhi", "Delhi"),
    "Cucumber": ("Karnataka", "Bangalore"),
    "Bitter Gourd": ("Maharashtra", "Mumbai"),
    "Bottle Gourd": ("Delhi", "Delhi"),
    "Ridge Gourd": ("Tamil Nadu", "Chennai"),
    "Pumpkin": ("Maharashtra", "Mumbai"),
    "Sweet Potato": ("Karnataka", "Bangalore"),
    "Drumstick": ("Tamil Nadu", "Chennai"),
    "Lemon": ("Maharashtra", "Mumbai"),
    "Banana": ("Tamil Nadu", "Chennai"),
    "Papaya": ("Karnataka", "Bangalore"),
    "Water Melon": ("Delhi", "Delhi"),
    "Peas": ("Delhi", "Delhi"),
    "Beans": ("Maharashtra", "Mumbai"),
    "Radish": ("Delhi", "Delhi"),
    "Yam": ("Tamil Nadu", "Chennai"),
    "Colocasia": ("Delhi", "Delhi"),
    "Tinda": ("Delhi", "Delhi"),
    "Mango": ("Maharashtra", "Mumbai"),
    "Orange": ("Maharashtra", "Mumbai"),
    "Grapes": ("Maharashtra", "Mumbai"),
    "Guava": ("Karnataka", "Bangalore"),
    "Capsicum": ("Maharashtra", "Mumbai"),
    "Mushroom": ("Delhi", "Delhi"),
    "Cherry": ("Himachal Pradesh", "Shimla"),
    "Strawberry": ("Maharashtra", "Mumbai"),
}

# Rows for seeder (mirrors prior mockData-style defaults)
def build_crops_seed() -> List[Dict[str, Any]]:
    specs: List[Tuple[str, str | None, float, RiskLevel, float, float, Trend, str | None]] = [
        ("Wheat", "गेहूं", 2150, RiskLevel.low, 2.5, 15, Trend.up, "Rabi"),
        ("Rice", "चावल", 3200, RiskLevel.medium, -3.2, 45, Trend.down, "Kharif"),
        ("Onion", "प्याज", 1800, RiskLevel.high, -12.5, 75, Trend.down, "Rabi & Kharif"),
        ("Tomato", "टमाटर", 2500, RiskLevel.high, -15.8, 82, Trend.down, "Kharif"),
        ("Potato", "आलू", 1200, RiskLevel.low, 1.8, 20, Trend.stable, "Rabi"),
        ("Cotton", "कपास", 6500, RiskLevel.medium, -5.5, 50, Trend.down, "Kharif"),
        ("Soybean", "सोयाबीन", 4200, RiskLevel.low, 3.2, 18, Trend.up, "Kharif"),
        ("Sugarcane", "गन्ना", 310, RiskLevel.low, 0.5, 12, Trend.stable, "Year-round"),
        ("Brinjal", "बैंगन", 2800, RiskLevel.medium, -2.0, 40, Trend.down, "Year-round"),
        ("Cabbage", "पत्ता गोभी", 1800, RiskLevel.low, 1.0, 22, Trend.stable, "Winter"),
        ("Cauliflower", "फूल गोभी", 2200, RiskLevel.medium, -4.0, 38, Trend.down, "Winter"),
        ("Bhindi", "भिंडी", 3500, RiskLevel.high, -8.0, 55, Trend.down, "Summer"),
        ("Green Chilli", "हरी मिर्च", 9000, RiskLevel.high, -10.0, 60, Trend.down, "Year-round"),
        ("Garlic", "लहसुन", 12000, RiskLevel.medium, 2.0, 35, Trend.up, "Year-round"),
        ("Ginger", "अदरक", 14000, RiskLevel.medium, -3.0, 42, Trend.down, "Year-round"),
        ("Carrot", "गाजर", 2500, RiskLevel.low, 1.5, 20, Trend.stable, "Winter"),
        ("Spinach", "पालक", 800, RiskLevel.low, 0.5, 15, Trend.stable, "Winter"),
        ("Coriander", "धनिया", 4000, RiskLevel.medium, -2.5, 30, Trend.down, "Year-round"),
        ("Methi", "मेथी", 1200, RiskLevel.low, 1.0, 18, Trend.stable, "Winter"),
        ("Cucumber", "खीरा", 2000, RiskLevel.low, -1.0, 25, Trend.down, "Year-round"),
        ("Bitter Gourd", "करेला", 3500, RiskLevel.medium, -5.0, 40, Trend.down, "Monsoon"),
        ("Bottle Gourd", "लौकी", 1800, RiskLevel.low, 0.5, 20, Trend.stable, "Monsoon"),
        ("Ridge Gourd", "तोरी", 2500, RiskLevel.low, -1.0, 22, Trend.down, "Monsoon"),
        ("Pumpkin", "कद्दू", 1500, RiskLevel.low, 1.0, 18, Trend.stable, "Year-round"),
        ("Sweet Potato", "शकरकंद", 2200, RiskLevel.low, 0.8, 19, Trend.stable, "Year-round"),
        ("Drumstick", "सहजन", 6000, RiskLevel.medium, -3.0, 35, Trend.down, "Year-round"),
        ("Lemon", "नींबू", 4500, RiskLevel.medium, -4.0, 32, Trend.down, "Year-round"),
        ("Banana", "केला", 2800, RiskLevel.low, 1.2, 20, Trend.stable, "Year-round"),
        ("Papaya", "पपीता", 2200, RiskLevel.low, 0.5, 18, Trend.stable, "Year-round"),
        ("Water Melon", "तरबूज", 1800, RiskLevel.low, -2.0, 28, Trend.down, "Summer"),
        ("Peas", "मटर", 5000, RiskLevel.medium, -3.0, 36, Trend.down, "Winter"),
        ("Beans", "बीन्स", 4500, RiskLevel.medium, -2.5, 34, Trend.down, "Year-round"),
        ("Radish", "मूली", 1500, RiskLevel.low, 0.5, 16, Trend.stable, "Winter"),
        ("Yam", "करु", 3500, RiskLevel.low, 1.0, 21, Trend.stable, "Year-round"),
        ("Colocasia", "अरबी", 2800, RiskLevel.low, -1.0, 24, Trend.down, "Monsoon"),
        ("Tinda", "टिंडा", 4000, RiskLevel.medium, -3.0, 33, Trend.down, "Summer"),
        ("Mango", "आम", 8000, RiskLevel.medium, 2.0, 30, Trend.up, "Summer"),
        ("Orange", "संतरा", 4500, RiskLevel.low, 1.0, 22, Trend.stable, "Winter"),
        ("Grapes", "अंगूर", 5500, RiskLevel.medium, -2.0, 38, Trend.down, "Year-round"),
        ("Guava", "अमरूद", 3500, RiskLevel.low, 0.8, 20, Trend.stable, "Year-round"),
        ("Capsicum", "शिमला मिर्च", 6500, RiskLevel.high, -6.0, 48, Trend.down, "Year-round"),
        ("Mushroom", "मशरूम", 12000, RiskLevel.medium, -2.0, 35, Trend.down, "Year-round"),
        ("Cherry", "चेरी", 800, RiskLevel.low, 0.5, 15, Trend.stable, "Summer"),
        ("Strawberry", "स्ट्रॉबेरी", 450, RiskLevel.low, 1.0, 14, Trend.stable, "Winter"),
    ]
    out: List[Dict[str, Any]] = []
    for name, hindi, price, risk, pch, shock, tr, season in specs:
        out.append(
            {
                "name": name,
                "name_hindi": hindi,
                "current_price": float(price),
                "risk_level": risk,
                "price_change": float(pch),
                "predicted_shock": float(shock),
                "trend": tr,
                "season": season,
            }
        )
    return out


def agmarknet_fetch_pairs() -> List[Tuple[str, str, str]]:
    """(crop_name, state, market_city) for live price seeding."""
    return [(name, CROP_MARKET_MAP[name][0], CROP_MARKET_MAP[name][1]) for name in CROP_MARKET_MAP]
