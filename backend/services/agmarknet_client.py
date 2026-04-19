"""
Agmarknet price fetcher via data.gov.in Daily Price API.

Set AGMARKNET_API_KEY (and optionally AGMARKNET_BASE_URL) in backend/.env.
If the key or URL is missing, fetch_prices returns an empty list.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, List, Optional

import httpx

from backend.core.config import settings

logger = logging.getLogger(__name__)

_datagov_403_logged = False
_startup_status_logged = False
COMMODITY_ALIASES: dict[str, list[str]] = {
    "Rice": ["Paddy(Dhan)(Common)", "Paddy(Dhan)", "Rice"],
    "Cotton": ["Cotton", "Cotton(Capasia)"],
    "Soybean": ["Soyabean", "Soyabean Yellow", "Soybean"],
    "Sugarcane": ["Sugar Cane", "Sugarcane", "Gur(Sugar)"],
    "Bhindi": ["Bhindi(Lady finger)", "Bhindi"],
    "Bitter Gourd": ["Bitter gourd", "Bitter Gourd"],
    "Bottle Gourd": ["Bottle Gourd", "Bottle gourd"],
    "Ridge Gourd": ["Ridge gourd", "Ridge Gourd"],
    "Green Chilli": ["Green Chilli", "Green Chilly"],
    "Coriander": ["Coriander(Leaves)", "Coriander"],
    "Peas": ["Peas(Wet)", "Peas(Dry)", "Peas"],
    "Water Melon": ["Water Melon", "Watermelon"],
    "Mango": ["Mango(Raw)", "Mango"],
}


def _datagov_auth_attempts(api_key: str) -> list[tuple[dict[str, str], dict[str, str]]]:
    """
    Daily Price API on api.data.gov.in returns HTTP 400 if the key is not in the query string;
    Bearer-only attempts only add noise. Prefer query api-key first, then header fallbacks.
    """
    k = api_key.strip()
    return [
        ({}, {"api-key": k}),
        ({}, {"api_key": k}),
        ({"Authorization": f"Bearer {k}"}, {"api-key": k}),
        ({"Authorization": f"Bearer {k}"}, {}),
        ({"Authorization": k}, {}),
    ]


def _merge_params(base: dict[str, Any], auth_extra: dict[str, str]) -> dict[str, Any]:
    out = dict(base)
    for key, val in auth_extra.items():
        out[key] = val
    return out


def _datagov_get(
    client: httpx.Client,
    url: str,
    params_without_key: dict[str, Any],
    api_key: str,
) -> tuple[httpx.Response | None, str]:
    """
    Try GET with each auth style. Returns (response, error_snippet).
    Success = HTTP 200 and JSON with `records` key (list, possibly empty).
    """
    last_resp: httpx.Response | None = None
    last_err = ""
    for headers, auth_params in _datagov_auth_attempts(api_key):
        merged = _merge_params(params_without_key, auth_params)
        try:
            r = client.get(url, params=merged, headers=headers)
            last_resp = r
            if r.status_code == 429:
                return r, "HTTP 429 Too Many Requests"
            if r.status_code != 200:
                last_err = (r.text or "")[:300]
                continue
            try:
                data = r.json()
            except Exception:
                last_err = "invalid json"
                continue
            if not isinstance(data, dict):
                continue
            if data.get("error"):
                err = str(data.get("error", ""))
                last_err = err[:300]
                # try next auth style
                continue
            if "records" in data:
                return r, ""
        except Exception as exc:
            last_err = str(exc)[:300]
            continue
    return last_resp, last_err or "no successful auth style"


def get_agmarknet_config_status() -> dict[str, Any]:
    """Snapshot for health/admin: whether live price fetch is configured."""
    key = (settings.AGMARKNET_API_KEY or "").strip()
    base = (settings.AGMARKNET_BASE_URL or "").strip()
    return {
        "source": "data.gov.in",
        "api_key_configured": bool(key),
        "base_url_configured": bool(base),
        "ready": bool(key and base),
    }


def log_agmarknet_startup_status() -> None:
    """Log once at app startup so operators see Agmarknet configuration without digging."""
    global _startup_status_logged
    if _startup_status_logged:
        return
    _startup_status_logged = True
    st = get_agmarknet_config_status()
    if st["ready"]:
        logger.info(
            "Agmarknet: live prices enabled (data.gov.in; key set, base URL set).",
        )
    elif not st["api_key_configured"]:
        logger.warning(
            "Agmarknet: AGMARKNET_API_KEY is not set — live mandi fetches will return no rows. "
            "Add your key from https://data.gov.in/ to backend/.env.",
        )
    elif not st["base_url_configured"]:
        logger.warning(
            "Agmarknet: AGMARKNET_BASE_URL is empty — set it to the dataset resource JSON URL.",
        )
    else:
        logger.warning("Agmarknet: configuration incomplete (check .env).")


class AgmarknetRecord:
    """Parsed record from a normalized data.gov row."""

    def __init__(self, raw: dict):
        self.city: str = raw.get("City", "")
        self.commodity: str = raw.get("Commodity", "")
        self.min_price: float = self._parse_price(raw.get("Min Prize", "0"))
        self.max_price: float = self._parse_price(raw.get("Max Prize", "0"))
        self.modal_price: float = self._parse_price(raw.get("Model Prize", "0"))
        self.date: Optional[datetime] = self._parse_date(raw.get("Date", ""))

    @staticmethod
    def _parse_price(value: Any) -> float:
        try:
            return float(str(value).replace(",", "").strip())
        except (ValueError, TypeError):
            return 0.0

    @staticmethod
    def _parse_date(value: Any) -> Optional[datetime]:
        if value is None:
            return None
        s = str(value).strip()
        if not s:
            return None
        for fmt in ("%d %b %Y", "%d-%m-%Y", "%Y-%m-%d", "%d/%m/%Y", "%d-%m-%y", "%Y/%m/%d"):
            try:
                return datetime.strptime(s, fmt)
            except ValueError:
                continue
        return None


def _pick(row: dict, *keys: str) -> Any:
    for k in keys:
        if k in row and row[k] not in (None, ""):
            return row[k]
    lower_map = {str(k).lower(): v for k, v in row.items()}
    for k in keys:
        kl = k.lower()
        if kl in lower_map and lower_map[kl] not in (None, ""):
            return lower_map[kl]
    return None


def _market_matches_hint(market_field: str, market_hint: str) -> bool:
    if not market_hint:
        return True
    mf = (market_field or "").lower()
    hint = market_hint.lower()
    if hint in mf or mf in hint:
        return True
    aliases = (
        ("bangalore", ("bengaluru", "bangalore", "binny")),
        ("bengaluru", ("bengaluru", "bangalore", "binny")),
        ("chennai", ("chennai", "koyambedu")),
        ("mumbai", ("mumbai", "vashi")),
        ("delhi", ("delhi", "azadpur")),
        ("lasalgaon", ("lasalgaon", "nashik")),
        ("pune", ("pune",)),
        ("hyderabad", ("hyderabad", "gaddiannaram")),
    )
    for key, words in aliases:
        if key == hint or hint in key:
            return any(w in mf for w in words)
    return False


def _datagov_row_to_raw_dict(row: dict, commodity: str, market_hint: str) -> Optional[dict]:
    mkt = str(_pick(row, "market", "Market", "APMC", "market_name") or "")
    if market_hint and not _market_matches_hint(mkt, market_hint):
        return None
    date_raw = _pick(row, "arrival_date", "Arrival_Date", "price_date", "Price Date", "date", "Date")
    modal = _pick(row, "modal_price", "Modal_Price", "modal", "Model_Price")
    min_p = _pick(row, "min_price", "Min_Price", "min", "Min Price")
    max_p = _pick(row, "max_price", "Max_Price", "max", "Max Price")
    comm = _pick(row, "commodity", "Commodity") or commodity
    if modal is None and min_p is None:
        return None
    return {
        "City": mkt or market_hint,
        "Commodity": str(comm),
        "Min Prize": str(min_p or modal or 0),
        "Max Prize": str(max_p or modal or 0),
        "Model Prize": str(modal or min_p or 0),
        "Date": str(date_raw or ""),
    }


def _commodity_candidates(commodity: str) -> list[str]:
    base = (commodity or "").strip()
    if not base:
        return [commodity]
    aliases = COMMODITY_ALIASES.get(base, [])
    out: list[str] = []
    for value in [base, *aliases]:
        v = str(value).strip()
        if v and v not in out:
            out.append(v)
    return out


def _fetch_prices_datagov(
    commodity: str, state: str, market: str, timeout: float
) -> List[AgmarknetRecord]:
    global _datagov_403_logged
    key = (settings.AGMARKNET_API_KEY or "").strip()
    if not key:
        return []

    base = (settings.AGMARKNET_BASE_URL or "").strip().rstrip("/")
    if not base:
        return []
    # Single URL: format=json is already in params; .../resource/<uuid>.json returns 400 on this API.
    url_variants: list[str] = [base]

    params_base: dict[str, Any] = {
        "limit": 1000,
        "offset": 0,
        "format": "json",
        "filters[commodity]": commodity,
    }

    # Try strict filters first; if no rows, fall back to commodity-only query.
    query_variants: list[dict[str, Any]] = [
        {**params_base, "filters[state]": state},
        dict(params_base),
    ]

    body: dict | None = None
    saw_valid_empty = False
    last_status: int | None = None
    last_snippet = ""
    saw_timeout = False

    with httpx.Client(timeout=timeout) as client:
        for query in query_variants:
            for url in url_variants:
                try:
                    response, err = _datagov_get(client, url, query, key)
                except httpx.TimeoutException as exc:
                    saw_timeout = True
                    last_snippet = str(exc)[:400]
                    continue
                except Exception as exc:
                    last_snippet = str(exc)[:400]
                    continue

                if response is None:
                    last_snippet = err[:400] if err else last_snippet
                    continue

                last_status = response.status_code
                if response.status_code == 403:
                    last_snippet = (response.text or "")[:400]
                    continue
                if response.status_code != 200:
                    last_snippet = (response.text or "")[:400]
                    continue
                try:
                    parsed = response.json()
                except Exception:
                    continue
                if isinstance(parsed, dict) and parsed.get("error"):
                    last_snippet = str(parsed.get("error", parsed))[:400]
                    continue

                records_raw = parsed.get("records") if isinstance(parsed, dict) else None
                if isinstance(records_raw, list):
                    if records_raw:
                        body = parsed
                        break
                    saw_valid_empty = True
                    body = parsed
                    # Successful 200 with empty records — do not try alternate URLs for same query
                    break
            if body is not None and (body.get("records") or []):
                break

    if body is None:
        if saw_timeout:
            logger.warning(
                "data.gov.in request failed: timed out (timeout=%ss). Last detail: %s",
                timeout,
                last_snippet[:200],
            )
        if last_status == 403 or (
            last_snippet and "not authorised" in last_snippet.lower()
        ):
            if not _datagov_403_logged:
                _datagov_403_logged = True
                logger.warning(
                    "data.gov.in rejected the API key (403 / Key not authorised). "
                    "Fix: (1) Log in to https://data.gov.in/ → My account → copy the key exactly (no spaces). "
                    "(2) On the dataset page for this API, ensure your key is allowed / request API access if the portal asks. "
                    "(3) Confirm AGMARKNET_BASE_URL matches that dataset’s resource JSON URL. "
                    "Last response: %s",
                    last_snippet[:200],
                )
            else:
                logger.debug("data.gov.in still unauthorised (suppressing repeat warnings)")
        elif "Authorization" in last_snippet or "authori" in (last_snippet or "").lower():
            logger.warning(
                "data.gov.in auth failed (%s). Send your API key in backend/.env as AGMARKNET_API_KEY. "
                "The client tries Authorization: Bearer <key> and query api-key. Last detail: %s",
                last_status,
                last_snippet[:200],
            )
        else:
            logger.warning(
                "data.gov.in HTTP %s — check AGMARKNET_API_KEY and resource URL. Body: %s",
                last_status,
                last_snippet[:200],
            )
        return []

    records_raw = body.get("records") or []
    if not records_raw:
        if saw_valid_empty:
            logger.info("data.gov.in returned 0 records for commodity=%s state=%s", commodity, state)
        else:
            logger.warning(
                "data.gov.in returned no usable payload for commodity=%s state=%s; last response: %s",
                commodity,
                state,
                last_snippet[:200],
            )
        return []

    out: List[AgmarknetRecord] = []
    for row in records_raw:
        if not isinstance(row, dict):
            continue
        raw = _datagov_row_to_raw_dict(row, commodity, market)
        if not raw:
            continue
        rec = AgmarknetRecord(raw)
        if rec.date and rec.modal_price > 0:
            out.append(rec)

    # Prefer market hint matches; if none, retry without market filter on rows
    if not out and market:
        for row in records_raw:
            if not isinstance(row, dict):
                continue
            raw = _datagov_row_to_raw_dict(row, commodity, "")
            if not raw:
                continue
            rec = AgmarknetRecord(raw)
            if rec.date and rec.modal_price > 0:
                out.append(rec)

    out.sort(key=lambda r: r.date or datetime.min, reverse=True)
    logger.info("data.gov.in: %d usable records for %s / %s", len(out), commodity, state)
    return out


def fetch_unfiltered_records(
    offset: int = 0,
    limit: int = 1000,
    state: Optional[str] = None,
    timeout: float = 40.0,
) -> List[dict]:
    """
    Fetch one page of the dataset **without** a commodity filter (many vegetables in one response).
    Use after AGMARKNET_API_KEY works with Authorization header. Rate limits still apply.
    """
    key = (settings.AGMARKNET_API_KEY or "").strip()
    if not key:
        return []

    base = (settings.AGMARKNET_BASE_URL or "").strip().rstrip("/")
    if not base:
        return []

    url_variants: list[str] = [base]

    params: dict[str, Any] = {
        "limit": min(limit, 1000),
        "offset": offset,
        "format": "json",
    }
    if state:
        params["filters[state]"] = state

    with httpx.Client(timeout=timeout) as client:
        for url in url_variants:
            response, _err = _datagov_get(client, url, params, key)
            if response is None or response.status_code != 200:
                continue
            try:
                data = response.json()
            except Exception:
                continue
            if isinstance(data, dict) and isinstance(data.get("records"), list):
                raw = data["records"]
                return [r for r in raw if isinstance(r, dict)]
    return []


def fetch_prices(
    commodity: str,
    state: str,
    market: str,
    timeout: float = 10.0,
) -> List[AgmarknetRecord]:
    """
    Fetch mandi prices from data.gov.in when AGMARKNET_API_KEY is set.
    """
    for commodity_candidate in _commodity_candidates(commodity):
        gov = _fetch_prices_datagov(commodity_candidate, state, market, timeout=max(timeout, 25.0))
        if gov:
            if commodity_candidate != commodity:
                logger.info(
                    "Agmarknet alias matched: requested=%s, using=%s (%d rows)",
                    commodity,
                    commodity_candidate,
                    len(gov),
                )
            return gov
    return []


def get_latest_modal_price(
    commodity: str, state: str, market: str
) -> Optional[float]:
    records = fetch_prices(commodity, state, market)
    if not records:
        return None
    return records[0].modal_price
