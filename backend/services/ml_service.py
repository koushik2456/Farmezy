"""
ML Service: Price forecasting (sklearn Ridge + seasonality) + shock probability (RandomForest / rules).

Key functions:
  - forecast_prices(crop_id, db) → list of dicts (14-day forecast)
  - compute_shock_probability(crop_id, db) → float (0-100)
  - recompute_crop_risk(crop_id, db) → updates crop.risk_level + crop.predicted_shock

These are called:
  1. By the seeder after inserting historical data.
  2. By a background task on each fresh Agmarknet fetch.
"""

import logging
from datetime import date, timedelta
from typing import List, Optional

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sqlalchemy.orm import Session

from backend.models.schema import Crop, PriceData, RiskLevel
from backend.services.model_service import load_shock_model

logger = logging.getLogger(__name__)
_SHOCK_MODEL = None


def _short_exc(exc: Exception, limit: int = 220) -> str:
    s = str(exc).replace("\n", " ").strip()
    return s if len(s) <= limit else s[: limit - 3] + "..."


# ── Helper: Load Historical Price DataFrame ────────────────────────────────────

def _load_price_df(crop_id: int, db: Session, days: int = 90) -> pd.DataFrame:
    """
    Load the last `days` of historical price records for a crop from the DB.
    Returns a DataFrame with columns [ds, y].
    """
    cutoff = date.today() - timedelta(days=days)
    rows = (
        db.query(PriceData)
        .filter(
            PriceData.crop_id == crop_id,
            PriceData.is_forecast == False,
            PriceData.price.isnot(None),
            PriceData.date >= cutoff,
        )
        .order_by(PriceData.date)
        .all()
    )
    if not rows:
        return pd.DataFrame(columns=["ds", "y"])

    df = pd.DataFrame(
        {"ds": [r.date for r in rows], "y": [r.price for r in rows]}
    )
    df["ds"] = pd.to_datetime(df["ds"])
    return df


def _features_time(t: np.ndarray) -> np.ndarray:
    """Trend + weak weekly seasonality (mandi-style weekly rhythm), no external deps."""
    t = t.astype(float)
    return np.column_stack(
        [
            t,
            t**2,
            np.sin(2.0 * np.pi * t / 7.0),
            np.cos(2.0 * np.pi * t / 7.0),
        ]
    )


# ── Sklearn forecasting (Windows-safe, no Stan) ───────────────────────────────

def forecast_prices(
    crop_id: int, db: Session, horizon_days: int = 14
) -> List[dict]:
    """
    Generate a `horizon_days`-day price forecast using Ridge regression on
    time features (trend + weekly harmonics). Falls back to linear extrapolation
    if data is thin or the regressor fails.
    """
    df = _load_price_df(crop_id, db)

    if len(df) < 10:
        logger.info(
            "ML forecast crop %d: %d historical rows (<10) — linear extrapolation",
            crop_id,
            len(df),
        )
        return _linear_forecast_fallback(crop_id, df, horizon_days)

    try:
        n = len(df)
        t = np.arange(n, dtype=float)
        X = _features_time(t)
        y = df["y"].values.astype(float)
        model = Ridge(alpha=2.0)
        model.fit(X, y)

        last_ts = df["ds"].max()
        last_d = last_ts.date() if hasattr(last_ts, "date") else date.fromisoformat(str(last_ts)[:10])

        results = []
        for k in range(horizon_days):
            tn = float(n + k)
            xf = _features_time(np.array([tn]))
            pred = float(model.predict(xf)[0])
            future_date = last_d + timedelta(days=k + 1)
            results.append({
                "date": future_date,
                "predicted": max(0.0, round(pred, 2)),
                "shock_probability": None,
            })

        logger.info(
            "ML forecast crop %d: Ridge+seasonal OK (%d days ahead)",
            crop_id,
            horizon_days,
        )
        return results

    except Exception as exc:
        logger.warning(
            "ML forecast crop %d: Ridge forecast failed (%s). Using linear fallback.",
            crop_id,
            _short_exc(exc),
        )
        return _linear_forecast_fallback(crop_id, df, horizon_days)


def _linear_forecast_fallback(crop_id: int, df: pd.DataFrame, horizon: int) -> List[dict]:
    """Simple linear extrapolation when the main forecaster cannot run."""
    if df.empty:
        base_price = 1000.0
        slope = 0.0
        last_d = date.today()
    else:
        prices = df["y"].values.astype(float)
        slope = float(np.polyfit(np.arange(len(prices)), prices, 1)[0]) if len(prices) > 1 else 0.0
        base_price = float(prices[-1])
        last_ts = df["ds"].max()
        last_d = last_ts.date() if hasattr(last_ts, "date") else date.fromisoformat(str(last_ts)[:10])

    results = []
    for i in range(1, horizon + 1):
        future_date = last_d + timedelta(days=i)
        results.append({
            "date": future_date,
            "predicted": max(0.0, round(base_price + slope * i, 2)),
            "shock_probability": None,
        })
    return results


# ── Shock probability (trained RandomForest or rule fallback) ─────────────────

def compute_shock_probability(crop_id: int, db: Session) -> float:
    """
    Compute price shock probability (0-100) using features:
      - Price volatility (std dev over last 30 days)
      - Recent price trend (slope)
      - Number of days since last big drop (>10%)
      - Window length

    Uses RandomForest `predict_proba` when `shock_model.pkl` exists; else rules.
    """
    df = _load_price_df(crop_id, db, days=60)

    if len(df) < 5:
        return 50.0  # Default uncertainty

    prices = df["y"].values.astype(float)

    # Feature engineering
    volatility = float(np.std(prices[-30:]) / (np.mean(prices[-30:]) + 1e-9) * 100)
    trend_slope = float(np.polyfit(np.arange(len(prices[-30:])), prices[-30:], 1)[0])
    trend_pct = (trend_slope / (prices[-1] + 1e-9)) * 100

    # Days since last price drop > 10%
    returns = np.diff(prices) / (prices[:-1] + 1e-9)
    big_drops = np.where(returns < -0.10)[0]
    days_since_drop = int(len(prices) - big_drops[-1]) if len(big_drops) > 0 else 60
    features = np.array([[volatility, trend_pct, days_since_drop, len(prices)]], dtype=float)

    global _SHOCK_MODEL
    if _SHOCK_MODEL is None:
        _SHOCK_MODEL = load_shock_model()

    if _SHOCK_MODEL is not None and hasattr(_SHOCK_MODEL, "predict_proba"):
        try:
            proba = float(_SHOCK_MODEL.predict_proba(features)[0][1]) * 100.0
            return round(min(100.0, max(0.0, proba)), 1)
        except Exception as exc:
            logger.warning("Persisted model inference failed for crop %d: %s", crop_id, exc)

    return round(min(100.0, max(0.0, _rule_based_shock(volatility, trend_pct, days_since_drop))), 1)


def _rule_based_shock(volatility: float, trend_pct: float, days_since_drop: int) -> float:
    """
    Rule-based shock probability (used when no trained classifier is available).
    """
    score = 0.0
    score += min(40.0, volatility * 2)
    if trend_pct < -0.5:
        score += min(30.0, abs(trend_pct) * 5)
    if days_since_drop < 7:
        score += 30.0
    elif days_since_drop < 14:
        score += 15.0
    return score


def _rule_based_shock_from_df(df: pd.DataFrame) -> float:
    prices = df["y"].values.astype(float)
    if len(prices) < 2:
        return 30.0
    volatility = float(np.std(prices) / (np.mean(prices) + 1e-9) * 100)
    return min(90.0, volatility * 2.5)


# ── Risk Level Updater ────────────────────────────────────────────────────────

def recompute_crop_risk(crop_id: int, db: Session) -> None:
    """
    After new data is fetched, recompute and persist:
      - crop.predicted_shock (from trained model or rules)
      - crop.risk_level     (derived from shock probability)
      - crop.trend          (derived from recent prices)
      - crop.price_change   (% change over last 7 days)
    """
    crop: Optional[Crop] = db.query(Crop).filter(Crop.id == crop_id).first()
    if not crop:
        return

    df = _load_price_df(crop_id, db, days=14)
    if df.empty:
        return

    prices = df["y"].values.astype(float)
    shock_prob = compute_shock_probability(crop_id, db)

    # Update risk level thresholds
    if shock_prob >= 60:
        risk = RiskLevel.high
    elif shock_prob >= 35:
        risk = RiskLevel.medium
    else:
        risk = RiskLevel.low

    # Trend from last 7 days
    from backend.models.schema import Trend
    if len(prices) >= 2:
        slope = float(np.polyfit(np.arange(len(prices)), prices, 1)[0])
        if slope > 5:
            trend = Trend.up
        elif slope < -5:
            trend = Trend.down
        else:
            trend = Trend.stable
    else:
        trend = Trend.stable

    # Price change % over last 7 days
    price_change = 0.0
    if len(prices) >= 7:
        price_change = round(((prices[-1] - prices[-7]) / (prices[-7] + 1e-9)) * 100, 2)
    elif len(prices) >= 2:
        price_change = round(((prices[-1] - prices[0]) / (prices[0] + 1e-9)) * 100, 2)

    crop.predicted_shock = shock_prob
    crop.risk_level = risk
    crop.trend = trend
    crop.price_change = price_change
    crop.current_price = float(prices[-1])

    db.commit()
    logger.info(
        "Recomputed risk for crop %d: shock=%.1f%%, risk=%s, trend=%s, price_change=%.1f%%",
        crop_id, shock_prob, risk.value, trend.value, price_change,
    )


# ── Forecast + Persist ─────────────────────────────────────────────────────────

def generate_and_save_forecasts(crop_id: int, db: Session) -> None:
    """
    Run price forecast + shock probabilities and persist to price_data table.
    Clears old forecasts first to avoid stale predictions.
    """
    # Delete old forecasts for this crop
    db.query(PriceData).filter(
        PriceData.crop_id == crop_id,
        PriceData.is_forecast == True,
    ).delete()
    db.commit()

    forecasts = forecast_prices(crop_id, db)
    shock_prob = compute_shock_probability(crop_id, db)

    for i, f in enumerate(forecasts):
        # Shock probability ramps up towards the most likely shock window
        adjusted_shock = min(100.0, shock_prob * (1 + i * 0.05))

        pd_row = PriceData(
            crop_id=crop_id,
            date=f["date"],
            price=None,
            predicted=f["predicted"],
            shock_probability=round(adjusted_shock, 1),
            is_forecast=True,
        )
        db.add(pd_row)

    db.commit()
    logger.info("Saved %d forecast rows for crop %d", len(forecasts), crop_id)
