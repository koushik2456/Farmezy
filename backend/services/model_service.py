"""
Model training and persistence for shock classification.
"""

from __future__ import annotations

import json
import os
import pickle
from datetime import datetime
from typing import Dict, Optional, Tuple

import numpy as np
from sqlalchemy.orm import Session

from backend.models.schema import Crop, PriceData

ARTIFACT_DIR = os.path.join("backend", "artifacts")
MODEL_PATH = os.path.join(ARTIFACT_DIR, "shock_model.pkl")
META_PATH = os.path.join(ARTIFACT_DIR, "shock_model_meta.json")


def _ensure_artifact_dir() -> None:
    os.makedirs(ARTIFACT_DIR, exist_ok=True)


def load_shock_model() -> Optional[object]:
    if not os.path.exists(MODEL_PATH):
        return None
    with open(MODEL_PATH, "rb") as f:
        return pickle.load(f)


def _build_training_dataset(db: Session) -> Tuple[np.ndarray, np.ndarray]:
    features = []
    labels = []
    crops = db.query(Crop).all()

    for crop in crops:
        rows = (
            db.query(PriceData)
            .filter(
                PriceData.crop_id == crop.id,
                PriceData.is_forecast.is_(False),
                PriceData.price.isnot(None),
            )
            .order_by(PriceData.date)
            .all()
        )
        prices = np.array([float(r.price) for r in rows], dtype=float)
        if len(prices) < 35:
            continue

        for i in range(30, len(prices) - 1):
            window = prices[i - 30 : i]
            current = prices[i]
            nxt = prices[i + 1]

            volatility = float(np.std(window) / (np.mean(window) + 1e-9) * 100)
            trend_slope = float(np.polyfit(np.arange(len(window)), window, 1)[0])
            trend_pct = float((trend_slope / (current + 1e-9)) * 100)
            day_return = float((current - prices[i - 1]) / (prices[i - 1] + 1e-9) * 100)
            label = 1 if ((nxt - current) / (current + 1e-9)) <= -0.10 else 0

            features.append([volatility, trend_pct, day_return, len(window)])
            labels.append(label)

    if not features:
        return np.array([]), np.array([])
    return np.array(features, dtype=float), np.array(labels, dtype=int)


def train_and_save_shock_model(db: Session) -> Dict[str, object]:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import accuracy_score
    from sklearn.model_selection import train_test_split

    X, y = _build_training_dataset(db)
    if len(X) < 80:
        return {"trained": False, "message": "Not enough labeled rows to train model"}

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=250,
        random_state=42,
        class_weight="balanced",
        max_depth=8,
        min_samples_leaf=2,
    )
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    accuracy = float(accuracy_score(y_test, preds))

    _ensure_artifact_dir()
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)

    meta = {
        "trained_at": datetime.utcnow().isoformat(),
        "samples": int(len(X)),
        "positive_labels": int(y.sum()),
        "accuracy": round(accuracy, 4),
    }
    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    return {"trained": True, **meta}
