"""
Agmarknet price fetcher.

1) Local scraper (optional): http://127.0.0.1:5000/request?commodity=&state=&market=
2) data.gov.in Daily Price API (optional): set AGMARKNET_API_KEY in backend/.env

If neither returns data, callers get an empty list (run seeder once DB has history, or set API key).
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, List, Optional

import httpx

from backend.core.config import settings

logger = logging.getLogger(__name__)

LOCAL_SCRAPER_URL = "http://127.0.0.1:5000/request"
_local_scraper_logged = False
_datagov_403_logged = False
COMMODITY_ALIASES: dict[str, list[str]] = {
    "Rice": ["Paddy(Dhan)(Common)", "Paddy(Dhan)", "Rice"],
    "Cotton": ["Cotton", "Cotton(Capasia)"],
    "Soybean": ["Soyabean", "Soyabean Yellow", "Soybean"],
    "Sugarcane": ["Sugar Cane", "Sugarcane", "Gur(Sugar)"],
}


class AgmarknetRecord:
    """Parsed record from scraper or normalized data.gov row."""

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


def _fetch_prices_local_scraper(
    commodity: str, state: str, market: str, timeout: float
) -> List[AgmarknetRecord]:
    global _local_scraper_logged
    params = {"commodity": commodity, "state": state, "market": market}
    try:
        with httpx.Client(timeout=timeout) as client:
            response = client.get(LOCAL_SCRAPER_URL, params=params)
            response.raise_for_status()
            raw_list: list = response.json()

        records = [AgmarknetRecord(r) for r in raw_list if isinstance(r, dict)]
        logger.info(
            "Agmarknet local: %d records for %s @ %s, %s",
            len(records), commodity, market, state,
        )
        return records

    except httpx.ConnectError:
        if not _local_scraper_logged:
            logger.warning(
                "Local Agmarknet scraper not reachable at %s — "
                "set AGMARKNET_API_KEY in backend/.env to use data.gov.in, or start your scraper.",
                LOCAL_SCRAPER_URL,
            )
            _local_scraper_logged = True
        else:
            logger.debug("Local Agmarknet scraper still unreachable")
        return []
    except httpx.HTTPStatusError as exc:
        logger.error("Local Agmarknet HTTP %s for %s", exc.response.status_code, params)
        return []
    except Exception as exc:
        logger.exception("Local Agmarknet error: %s", exc)
        return []


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
    # data.gov.in resource endpoints may work as /resource/<id> (preferred),
    # while some docs/examples mention /resource/<id>.json. Try both.
    url_variants: list[str] = [base]
    if not base.endswith(".json"):
        url_variants.append(f"{base}.json")

    params_base: dict[str, Any] = {
        "limit": 1000,
        "offset": 0,
        "format": "json",
        "filters[commodity]": commodity,
    }

    # Try strict filters first; if no rows, fall back to commodity-only query.
    query_variants: list[dict[str, Any]] = [{**params_base, "filters[state]": state}, params_base]

    # data.gov.in historically uses `api-key`; some clients/docs use `api_key`. Try both.
    auth_variants: list[tuple[str, str]] = [
        ("api-key", key),
        ("api_key", key),
    ]

    body: dict | None = None
    saw_valid_empty = False
    last_status: int | None = None
    last_snippet = ""
    saw_timeout = False

    with httpx.Client(timeout=timeout) as client:
        for query in query_variants:
            for url in url_variants:
                for auth_key, auth_value in auth_variants:
                    params = {**query, auth_key: auth_value}
                    try:
                        response = client.get(url, params=params)
                    except httpx.TimeoutException as exc:
                        saw_timeout = True
                        last_snippet = str(exc)[:400]
                        continue
                    except Exception as exc:
                        last_snippet = str(exc)[:400]
                        continue

                    last_status = response.status_code
                    text = (response.text or "")[:400]
                    last_snippet = text
                    if response.status_code == 403:
                        continue
                    try:
                        response.raise_for_status()
                    except httpx.HTTPStatusError:
                        continue
                    try:
                        parsed = response.json()
                    except Exception:
                        continue
                    if isinstance(parsed, dict) and parsed.get("error"):
                        # Some error payloads still return 200
                        last_snippet = str(parsed.get("error", parsed))[:400]
                        continue

                    records_raw = parsed.get("records") if isinstance(parsed, dict) else None
                    if isinstance(records_raw, list) and records_raw:
                        body = parsed
                        break
                    if isinstance(records_raw, list):
                        # Valid response but no rows for this query variant.
                        saw_valid_empty = True
                        body = parsed
                        continue
                if body is not None and (body.get("records") or []):
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


def fetch_prices(
    commodity: str,
    state: str,
    market: str,
    timeout: float = 10.0,
) -> List[AgmarknetRecord]:
    """
    Try local scraper first, then data.gov.in (if API key configured).
    """
    local = _fetch_prices_local_scraper(commodity, state, market, timeout=timeout)
    if local:
        return local

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
