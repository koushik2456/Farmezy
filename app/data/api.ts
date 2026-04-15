/**
 * api.ts — Frontend API client for the FastAPI backend.
 * Replaces the static exports from mockData.ts with live HTTP fetches.
 *
 * Backend base URL: http://localhost:8000
 */

const BASE_URL = "http://localhost:8000";

// ── Types (mirroring backend Pydantic schemas and mockData.ts interfaces) ─────

export type RiskLevel = "low" | "medium" | "high";
export type TrendType = "up" | "down" | "stable";

export interface Crop {
  id: number;
  name: string;
  name_hindi: string | null;
  current_price: number;
  unit: string;
  risk_level: RiskLevel;
  price_change: number;
  predicted_shock: number;
  trend: TrendType;
  season: string | null;
}

export interface PriceData {
  id: number;
  crop_id: number;
  date: string;          // ISO date string "YYYY-MM-DD"
  price: number | null;          // Observed historical price
  predicted: number | null;      // ML-predicted price (forecast)
  shock_probability: number | null;
  is_forecast: boolean;
}

export interface CropWithHistory extends Crop {
  price_history: PriceData[];
}

export interface Market {
  id: number;
  name: string;
  state: string;
  risk_level: RiskLevel;
  high_risk_crops: number;
  total_crops: number;
  average_price_change: number;
}

export interface MarketCropComparison {
  market_id: number;
  market_name: string;
  state: string;
  current_price: number;
  risk_level: RiskLevel;
  predicted_shock: number;
  price_change: number;
  distance_km: number;
  transport_cost: number;
  demand_level: "high" | "medium" | "low";
  storage_available: boolean;
  trend: TrendType;
}

/** Multi-market comparison; distances are from Chennai (see origin_note). */
export interface MarketComparisonBundle {
  origin_city: string;
  origin_state: string;
  origin_note: string;
  markets: MarketCropComparison[];
}

export interface AdminPipelineStats {
  total_runs: number;
  failed_runs: number;
  last_run_at: string | null;
  last_success_at: string | null;
  last_error: string | null;
}

export interface AdminFreshnessRow {
  crop_id: number;
  crop_name: string;
  latest_actual_date: string | null;
  days_since_update: number | null;
}

export interface AdminStatus {
  pipeline: AdminPipelineStats;
  freshness: AdminFreshnessRow[];
  stale_crops: number;
  total_crops: number;
}

export interface Alert {
  id: number;
  crop_id: number;
  market_id: number;
  crop_name: string | null;
  market_name: string | null;
  risk_level: RiskLevel;
  message: string;
  recommendation: string | null;
  date: string;          // ISO date string
  is_read: boolean;
}

// ── Generic Fetch Helper ──────────────────────────────────────────────────────

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    const error = await response.text();
    throw new Error(`API error ${response.status}: ${error}`);
  }
  return response.json() as Promise<T>;
}

// ── Crops ─────────────────────────────────────────────────────────────────────

/** Fetch all crops */
export const getCrops = (): Promise<Crop[]> =>
  apiFetch<Crop[]>("/api/crops/");

/** Fetch a single crop by ID */
export const getCrop = (id: number): Promise<Crop> =>
  apiFetch<Crop>(`/api/crops/${id}`);

/** Fetch crop with full price history + ML forecast */
export const getCropHistory = (id: number): Promise<CropWithHistory> =>
  apiFetch<CropWithHistory>(`/api/crops/${id}/history`);

/** Trigger a live Agmarknet refresh for a crop */
export const refreshCrop = (id: number): Promise<{ message: string }> =>
  apiFetch<{ message: string }>(`/api/crops/${id}/refresh`, { method: "POST" });

// ── Markets ───────────────────────────────────────────────────────────────────

/** Fetch all markets */
export const getMarkets = (): Promise<Market[]> =>
  apiFetch<Market[]>("/api/markets/");

/** Fetch a single market by ID */
export const getMarket = (id: number): Promise<Market> =>
  apiFetch<Market>(`/api/markets/${id}`);

/** Fetch crops available in a market */
export const getMarketCrops = (id: number): Promise<Crop[]> =>
  apiFetch<Crop[]>(`/api/markets/${id}/crops`);

/** Compare one crop across all markets (distances from Chennai reference). */
export const getMarketComparison = (cropId: number): Promise<MarketComparisonBundle> =>
  apiFetch<MarketComparisonBundle>(`/api/markets/comparison/${cropId}`);

// ── Alerts ────────────────────────────────────────────────────────────────────

/** Fetch all alerts. Pass `unreadOnly=true` to filter. */
export const getAlerts = (unreadOnly = false): Promise<Alert[]> =>
  apiFetch<Alert[]>(`/api/alerts/?unread_only=${unreadOnly}`);

/** Mark an alert as read */
export const markAlertRead = (id: number): Promise<Alert> =>
  apiFetch<Alert>(`/api/alerts/${id}/read`, {
    method: "PATCH",
    body: JSON.stringify({ is_read: true }),
  });

// ── Admin ─────────────────────────────────────────────────────────────────────

export const getAdminStatus = (): Promise<AdminStatus> =>
  apiFetch<AdminStatus>("/api/admin/status");

export const refreshAllCrops = (): Promise<{ message: string }> =>
  apiFetch<{ message: string }>("/api/admin/refresh-all", { method: "POST" });

export const trainShockModel = (): Promise<Record<string, unknown>> =>
  apiFetch<Record<string, unknown>>("/api/admin/train-shock-model", { method: "POST" });
