# Market Price Shock Predictor - Full Implementation Plan

## Phase 1: Core Platform Backbone
- Finalize FastAPI + React integration with consistent API contracts.
- Ensure startup table creation and environment-driven config.
- Seed initial crops, markets, and alerts.

## Phase 2: Data Pipeline and Real-Time Refresh
- Integrate Agmarknet fetch pipeline for crop-wise live mandi data.
- Add background-safe refresh execution per crop.
- Schedule hourly refresh jobs for all crops.
- Persist refreshed historical observations in `price_data`.

## Phase 3: ML and Risk Scoring
- Compute engineered features (volatility, trend slope, recent shocks).
- Generate shock probability with rule/XGBoost-compatible pipeline.
- Classify into low/medium/high risk thresholds.
- Persist 14-day forecasts and crop risk metadata.

## Phase 4: API Surface Completion
- `GET /api/crops`, `GET /api/crops/{id}`, `GET /api/crops/{id}/history`.
- `POST /api/crops/{id}/refresh` (async pipeline trigger).
- `GET /api/markets`, `GET /api/markets/{id}`, `GET /api/markets/{id}/crops`.
- `GET /api/markets/comparison/{crop_id}` for multi-market crop comparison.
- `GET /api/alerts`, `PATCH /api/alerts/{id}/read`.

## Phase 5: Frontend End-to-End Features
- Dashboard: risk stats + alerts + top risky crops.
- Crop analysis: filterable crop grid and risk summaries.
- Detailed analysis: historical + forecast chart with advisories.
- Market analysis: market-level risk view and filters.
- Market comparison: backend-driven comparison with recommendation.
- Alerts: read/unread workflow and risk-level filtering.

## Phase 6: Admin and Reliability Enhancements
- Add data freshness indicators and last-updated timestamps.
- Add API error states/retry UI.
- Add admin monitoring page for pipeline health and failures.
- Add alert history retention policies.

## Phase 7: Production Readiness
- Containerize frontend and backend.
- Add CI tests for API contracts and core prediction logic.
- Add observability (structured logs + metrics + health checks).
- Secure secrets/config and support PostgreSQL deployment profile.

## Current Implementation Status
- Implemented and working: core APIs, data refresh pipeline, hourly scheduler, risk/forecast persistence, alert read flow, and backend-driven market comparison.
- Verified: frontend production build succeeds and backend Python modules compile successfully.
