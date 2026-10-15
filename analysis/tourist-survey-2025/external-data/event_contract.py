"""Korea Mate EDA 5: source-specific cultural event normalization and quality rules.

No key or individual-level survey data is stored. A record being within its
published date range is NEVER treated as verified opening or bookability.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass
from datetime import date, datetime, timezone
from hashlib import sha256
from typing import Any, Iterable
import json
import re
from urllib.parse import urlparse


SOURCES = {"seoul_cultural", "tourapi_festival"}
SEOUL_DECLARED_FIELDS = (
    "CODENAME GUNAME TITLE DATE PLACE ORG_NAME USE_TRGT USE_FEE INQUIRY "
    "PLAYER PROGRAM ETC_DESC ORG_LINK MAIN_IMG RGSTDATE TICKET STRTDATE "
    "END_DATE THEMECODE LOT LAT IS_FREE HMPG_ADDR PRO_TIME"
).split()


def _clean(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _date_parse(value: Any) -> date | None:
    """Only parse known API date layouts. Unparsable dates remain unknown."""
    if isinstance(value, date):
        return value
    s = _clean(value)
    if not s:
        return None
    m = re.match(r"^(\d{4})-?(\d{2})-?(\d{2})(?:$|[T\s])", s)
    if m:
        try:
            return date(*(int(x) for x in m.groups()))
        except ValueError:
            return None
    return None


def _coordinates(lon_value: Any, lat_value: Any) -> tuple[float | None, float | None, str]:
    try:
        lon, lat = float(lon_value), float(lat_value)
    except (TypeError, ValueError):
        return None, None, "missing_or_non_numeric"
    # Broad Korean peninsula + islands check; not a geocoder or authoritative boundary.
    if 124.0 <= lon <= 132.0 and 32.0 <= lat <= 39.5:
        return lon, lat, "plausible_korea"
    if 32.0 <= lon <= 39.5 and 124.0 <= lat <= 132.0:
        return None, None, "swapped_coordinates_suspected"
    return None, None, "out_of_range"


def _is_web_url(value: Any) -> bool:
    s = _clean(value)
    if not s:
        return False
    p = urlparse(s)
    return p.scheme in ("http", "https") and bool(p.hostname)


@dataclass
class Event:
    provider: str
    identifier: str
    title: str
    category: str | None
    venue_name: str | None
    locality: str | None
    start_date: str | None
    end_date: str | None
    longitude: float | None
    latitude: float | None
    source_url: str | None
    source_record_date: str | None
    fetched_at_utc: str
    date_window_status: str
    coordinates_status: str
    location_candidate: bool
    ending_soon_candidate: bool
    bookable: None
    operating_now: None
    quality_flags: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def normalize_event(provider: str, row: dict[str, Any], *, today: date,
                    fetched_at: datetime | None = None) -> Event:
    if provider not in SOURCES:
        raise ValueError("Unknown provider")
    if not isinstance(row, dict):
        raise TypeError("Each API row must be a dictionary")

    if provider == "seoul_cultural":
        title = _clean(row.get("TITLE"))
        start_raw, end_raw = row.get("STRTDATE"), row.get("END_DATE")
        lon_raw, lat_raw = row.get("LOT"), row.get("LAT")
        category = _clean(row.get("CODENAME")) or None
        venue = _clean(row.get("PLACE")) or None
        locality = _clean(row.get("GUNAME")) or None
        link_raw = row.get("HMPG_ADDR") or row.get("ORG_LINK")
        # RGSTDATE is registration date, NOT a proof of last update.
        source_record_date = _clean(row.get("RGSTDATE")) or None
        original_id = _clean(row.get("HMPG_ADDR"))
    else:
        title = _clean(row.get("title"))
        start_raw, end_raw = row.get("eventstartdate"), row.get("eventenddate")
        lon_raw, lat_raw = row.get("mapx"), row.get("mapy")
        category = _clean(row.get("contenttypeid")) or None
        venue = _clean(row.get("addr1")) or None
        locality = _clean(row.get("areacode")) or None
        link_raw = None  # contentid is not an official booking URL.
        source_record_date = _clean(row.get("modifiedtime")) or None
        original_id = _clean(row.get("contentid"))

    start, end = _date_parse(start_raw), _date_parse(end_raw)
    lon, lat, coord_status = _coordinates(lon_raw, lat_raw)
    flags = []
    if not title:
        flags.append("missing_title")
    if not start or not end:
        flags.append("date_missing_or_invalid")
        window = "unknown"
    elif end < start:
        flags.append("end_before_start")
        window = "invalid"
    elif today > end:
        window = "expired"
    elif today < start:
        window = "future"
    else:
        window = "within_date_window_only"

    if coord_status != "plausible_korea":
        flags.append(coord_status)
    if not _is_web_url(link_raw):
        flags.append("detail_url_unavailable")

    detail_url = _clean(link_raw) if _is_web_url(link_raw) else None
    identifier = original_id or sha256(
        f"{provider}|{title}|{venue}|{_clean(start_raw)}".encode("utf-8")
    ).hexdigest()[:20]
    fetched = fetched_at or datetime.now(timezone.utc)
    if fetched.tzinfo is None:
        raise ValueError("fetched_at must contain a timezone")
    # No status here asserts the event is operating or reservable.
    eligible = bool(title and lon is not None and window in ("future", "within_date_window_only"))
    ending_soon = bool(window == "within_date_window_only" and end and 0 <= (end - today).days <= 7)
    return Event(
        provider=provider, identifier=identifier, title=title, category=category,
        venue_name=venue, locality=locality,
        start_date=start.isoformat() if start else None,
        end_date=end.isoformat() if end else None,
        longitude=lon, latitude=lat, source_url=detail_url,
        source_record_date=source_record_date,
        fetched_at_utc=fetched.astimezone(timezone.utc).isoformat(),
        date_window_status=window, coordinates_status=coord_status,
        location_candidate=eligible, ending_soon_candidate=ending_soon,
        bookable=None, operating_now=None, quality_flags=flags,
    )


def extract_rows(provider: str, payload: dict[str, Any]) -> list[dict[str, Any]]:
    if provider == "seoul_cultural":
        body = payload.get("culturalEventInfo")
        if not isinstance(body, dict):
            raise ValueError("No culturalEventInfo object in Seoul response")
        code = (body.get("RESULT") or {}).get("CODE")
        if code not in ("INFO-000", None):
            raise ValueError(f"Seoul API application response code: {code}")
        rows = body.get("row", [])
    elif provider == "tourapi_festival":
        outer = payload.get("response", {})
        header = outer.get("header", {})
        if _clean(header.get("resultCode")) not in ("", "0000", "00"):
            raise ValueError("TourAPI application error: " + _clean(header.get("resultCode")))
        items = (outer.get("body", {}).get("items") or {}).get("item", [])
        rows = [items] if isinstance(items, dict) else items
    else:
        raise ValueError("Unknown provider")
    if not isinstance(rows, list) or any(not isinstance(x, dict) for x in rows):
        raise ValueError("Malformed API rows")
    return rows


def quality_summary(provider: str, rows: Iterable[dict[str, Any]], *, today: date,
                    fetched_at: datetime | None = None) -> dict[str, Any]:
    events = [normalize_event(provider, x, today=today, fetched_at=fetched_at) for x in rows]
    flags = Counter(f for e in events for f in e.quality_flags)
    date_status = Counter(e.date_window_status for e in events)
    ids = [(e.provider, e.identifier) for e in events]
    return {
        "provider": provider,
        "scope": "schema/quality validation, NOT actual operating or booking availability",
        "row_count": len(events),
        "distinct_source_ids": len(set(ids)),
        "duplicate_source_ids": len(ids) - len(set(ids)),
        "date_status_counts": dict(date_status),
        "coordinate_valid_count": sum(e.longitude is not None for e in events),
        "detail_url_valid_count": sum(e.source_url is not None for e in events),
        "location_candidate_count": sum(e.location_candidate for e in events),
        "ending_soon_candidate_count": sum(e.ending_soon_candidate for e in events),
        "quality_flags": dict(flags),
        "operating_now_confirmed_count": None,
        "bookable_confirmed_count": None,
        "items": [e.to_dict() for e in events],
    }