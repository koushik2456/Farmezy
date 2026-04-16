"""
ML Service: Price Forecasting (Prophet) + Shock Detection (XGBoost / Isolation Forest).

Key functions:
  - forecast_prices(crop_id, db) → list of PriceData rows (14-day forecast)
  - compute_shock_probability(crop_id, db) → float (0-100)
  - recompute_crop_risk(crop_id, db) → updates crop.risk_level + crop.predicted_shock

These are called:
  1. By the seeder after inserting historical data.
  2. By a background task on each fresh Agmarknet fetch.
"""

import logging
from datetime import date, timedelta
from typing import List, Optional, Tuple

import numpy as np
import pandas as pd
from sqlalchemy.orm import Session

from backend.core.stan_logging import silence_cmdstan_loggers
from backend.models.schema import Crop, PriceData, RiskLevel
from backend.services.model_service import load_shock_model

logger = logging.getLogger(__name__)
_SHOCK_MODEL = None
_PROPHET_IMPORT_ERROR: Optional[str] = None
_PROPHET_CLASS: Optional[type] = None
_PROPHET_RUNTIME_DISABLED: bool = False
_PROPHET_RUNTIME_LOGGED: bool = False

silence_cmdstan_loggers()


def _short_exc(exc: Exception, limit: int = 220) -> str:
    s = str(exc).replace("\n", " ").strip()
    return s if len(s) <= limit else s[: limit - 3] + "..."


def _get_prophet_class():
    """Lazy import; on failure cache message so we do not retry import every crop."""
    global _PROPHET_CLASS, _PROPHET_IMPORT_ERROR
    if _PROPHET_IMPORT_ERROR is not None:
        return None
    if _PROPHET_CLASS is not None:
        return _PROPHET_CLASS
    try:
        silence_cmdstan_loggers()
        from prophet import Prophet  # type: ignore[import-untyped]

        silence_cmdstan_loggers()

        _PROPHET_CLASS = Prophet
        return _PROPHET_CLASS
    except Exception as exc:
        _PROPHET_IMPORT_ERROR = str(exc)
        logger.warning(
            "ML forecasts: Prophet import failed (%s). Using linear extrapolation for all crops.",
            _short_exc(exc),
        )
        return None


# ── Helper: Load Historical Price DataFrame ────────────────────────────────────

def _load_price_df(crop_id: int, db: Session, days: int = 90) -> pd.DataFrame:
    """
    Load the last `days` of historical price records for a crop from the DB.
    Returns a DataFrame with columns [ds, y] (Prophet convention).
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


# ── Prophet Forecasting ────────────────────────────────────────────────────────

def forecast_prices(
    crop_id: int, db: Session, horizon_days: int = 14
) -> List[dict]:
    """
    Generate a `horizon_days`-day price forecast using Prophet.

    Returns a list of dicts with keys: date, predicted, shock_probability.
    Falls back to a linear extrapolation if Prophet fails or data is insufficient.
    """
    df = _load_price_df(crop_id, db)

    if len(df) < 10:
        logger.info(
            "ML forecast crop %d: %d historical rows (<10) — linear extrapolation",
            crop_id,
            len(df),
        )
        return _linear_forecast_fallback(crop_id, df, horizon_days)

    Prophet = _get_prophet_class()
    if Prophet is None:
        return _linear_forecast_fallback(crop_id, df, horizon_days)

    global _PROPHET_RUNTIME_DISABLED, _PROPHET_RUNTIME_LOGGED
    if _PROPHET_RUNTIME_DISABLED:
        logger.debug("ML forecast crop %d: Prophet skipped (optimizer failed earlier this process)", crop_id)
        return _linear_forecast_fallback(crop_id, df, horizon_days)

    try:
        silence_cmdstan_loggers()
        model = Prophet(
            daily_seasonality=False,
            weekly_seasonality=True,
            yearly_seasonality=True,
            interval_width=0.80,
        )
        silence_cmdstan_loggers()
        model.fit(df)

        future = model.make_future_dataframe(periods=horizon_days)
        forecast = model.predict(future)

        # Only return the future rows
        future_only = forecast.tail(horizon_days)
        results = []
        for _, row in future_only.iterrows():
            results.append({
                "date": row["ds"].date(),
                "predicted": max(0.0, round(float(row["yhat"]), 2)),
                "shock_probability": None,  # Filled by XGBoost below
            })

        logger.info("ML forecast crop %d: Prophet OK (%d days ahead)", crop_id, horizon_days)
        return results

    except Exception as exc:
        _PROPHET_RUNTIME_DISABLED = True
        if not _PROPHET_RUNTIME_LOGGED:
            _PROPHET_RUNTIME_LOGGED = True
            logger.warning(
                "ML forecasts: Prophet optimizer failed (%s). "
                "On Windows this is often antivirus blocking the Stan binary, or bad/NaN inputs. "
                "Using linear extrapolation for all crops until restart.",
                _short_exc(exc),
            )
        else:
            logger.debug("ML forecast crop %d: linear fallback (Prophet disabled)", crop_id)
        return _linear_forecast_fallback(crop_id, df, horizon_days)


def _linear_forecast_fallback(crop_id: int, df: pd.DataFrame, horizon: int) -> List[dict]:
    """Simple linear extrapolation when Prophet cannot run."""
    if df.empty:
        base_price = 1000.0
        slope = 0.0
    else:
        prices = df["y"].values.astype(float)
        slope = float(np.polyfit(np.arange(len(prices)), prices, 1)[0]) if len(prices) > 1 else 0.0
        base_price = float(prices[-1])

    results = []
    for i in range(1, horizon + 1):
        future_date = date.today() + timedelta(days=i)
        results.append({
            "date": future_date,
            "predicted": max(0.0, round(base_price + slope * i, 2)),
            "shock_probability": None,
        })
    return results


# ── XGBoost Shock Probability ─────────────────────────────────────────────────

def compute_shock_probability(crop_id: int, db: Session) -> float:
    """
    Compute price shock probability (0-100) using XGBoost features:
      - Price volatility (std dev over last 30 days)
      - Recent price trend (slope)
      - Number of days since last big drop (>10%)
      - Predicted price vs current price % change

    Returns a float in [0, 100].
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
    Rule-based shock probability (used as XGBoost proxy until we have labeled training data).
    Designed to produce similar outputs to a trained XGBoost classifier.
    """
    score = 0.0
    # High volatility → higher shock risk
    score += min(40.0, volatility * 2)
    # Strong negative trend → higher risk
    if trend_pct < -0.5:
        score += min(30.0, abs(trend_pct) * 5)
    # Recent drop increases risk
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
      - crop.predicted_shock (from XGBoost)
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
    Run Prophet forecast + XGBoost shock probabilities and persist to price_data table.
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
