"""Korea Mate EDA v5: bounded, read-only TourAPI festival census.

Reads the key from the environment. Outputs *only aggregates*, never original
records, API keys, titles, URLs, event IDs, addresses, or coordinates.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import date, datetime, timezone
import json
import math
import os
from pathlib import Path
import re
import statistics
import sys
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, unquote
from urllib.request import Request, urlopen

ENDPOINT = "https://apis.data.go.kr/B551011/KorService2/searchFestival2"
KST = timezone.utc  # As-of date is passed explicitly; never infer from runner UTC.
FIELDS = (
    "contentid", "title", "addr1", "areacode", "mapx", "mapy",
    "eventstartdate", "eventenddate", "modifiedtime", "firstimage",
    "contenttypeid", "cat1", "tel", "zipcode",
)
REGION_PREFIXES = {
    "서울": "서울", "부산": "부산", "대구": "대구", "인천": "인천", "광주": "광주",
    "대전": "대전", "울산": "울산", "세종": "세종", "경기": "경기", "강원": "강원",
    "충북": "충북", "충청북도": "충북", "충남": "충남", "충청남도": "충남",
    "전북": "전북", "전라북도": "전북", "전북특별자치도": "전북",
    "전남": "전남", "전라남도": "전남", "경북": "경북", "경상북도": "경북",
    "경남": "경남", "경상남도": "경남", "제주": "제주",
}
KNOWN_REGIONS = ("서울", "부산", "대구", "인천", "광주", "대전", "울산", "세종", "경기", "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주")


def normalized_key(raw_key: str) -> str:
    """Decode percent escapes once before urlencode encodes request parameters."""
    return unquote(raw_key.strip())


def is_present(value: Any) -> bool:
    return value is not None and str(value).strip() not in ("", "None", "null")


def parse_day(value: Any) -> date | None:
    s = str(value or "").strip()
    if not re.fullmatch(r"\d{8}", s):
        return None
    try:
        return datetime.strptime(s, "%Y%m%d").date()
    except ValueError:
        return None


def parse_modified(value: Any) -> date | None:
    """Modified time can be YYYYMMDD or YYYYMMDDhhmmss."""
    s = str(value or "").strip()
    if not re.fullmatch(r"\d{8}(?:\d{6})?", s):
        return None
    return parse_day(s[:8])


def region_from_address(value: Any) -> str:
    """Rough 17-province label from address; not a reverse geocoder."""
    text = str(value or "").strip()
    if not text:
        return "주소없음"
    text = re.sub(r"^\(?\d{5}\)?\s+", "", text)
    head = text.split()[0] if text.split() else ""
    if head in REGION_PREFIXES:
        return REGION_PREFIXES[head]
    # Accept official full province names and abbreviated metropolitan names.
    for prefix, region in sorted(REGION_PREFIXES.items(), key=lambda x: -len(x[0])):
        if head.startswith(prefix) and (len(head) > len(prefix)):
            suffix = head[len(prefix):]
            if suffix.startswith(("특별", "광역", "자치", "도", "시")):
                return region
    return "주소지역미분류"


def parse_page(payload: Any) -> tuple[list[dict], int]:
    if not isinstance(payload, dict):
        raise ValueError("Response is not a JSON object")
    top = payload.get("response")
    if not isinstance(top, dict):
        raise ValueError("response container missing")
    header = top.get("header", {})
    if not isinstance(header, dict):
        raise ValueError("header object missing")
    result = str(header.get("resultCode", "missing"))
    if result not in {"0000", "00", "0"}:
        # Never print a provider error message or URL; they might reflect credentials.
        raise ValueError("provider_result_code:" + re.sub(r"[^A-Za-z0-9_-]", "", result)[:25])
    body = top.get("body", {})
    if not isinstance(body, dict):
        raise ValueError("body object missing")
    count = body.get("totalCount")
    try:
        total = int(count)
    except (ValueError, TypeError, OverflowError) as e:
        raise ValueError("missing_or_invalid_total_count") from e
    if total < 0 or total > 1_000_000:
        raise ValueError("total_count_out_of_range")
    items = body.get("items") or {}
    if isinstance(items, dict):
        rows = items.get("item", [])
    elif isinstance(items, list):
        rows = items
    else:
        raise ValueError("items_container_invalid")
    if isinstance(rows, dict):
        rows = [rows]
    if rows is None:
        rows = []
    if not isinstance(rows, list) or any(not isinstance(item, dict) for item in rows):
        raise ValueError("invalid_items_array")
    return rows, total


def page_request(key: str, *, start_date: str, page_no: int, page_size: int, timeout: int = 25) -> tuple[list[dict], int]:
    query = urlencode({
        "serviceKey": key,
        "MobileOS": "ETC",
        "MobileApp": "KoreaMate",
        "_type": "json",
        "eventStartDate": start_date,
        "numOfRows": str(page_size),
        "pageNo": str(page_no),
    })
    # The full URL, raw body and exception string must never appear in logs.
    url = ENDPOINT + "?" + query
    request = Request(url, headers={"User-Agent": "KoreaMate-Research-QA/1.0"})
    for attempt in range(3):
        try:
            with urlopen(request, timeout=timeout) as response:
                payload = response.read(3_000_000)
                if response.status != 200:
                    raise ValueError("non_200_http")
            data = json.loads(payload)
            return parse_page(data)
        except HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and attempt < 2:
                time.sleep(2 ** attempt)
                continue
            raise ValueError(f"http_error_{e.code}") from None
        except (URLError, TimeoutError, OSError):
            if attempt < 2:
                time.sleep(2 ** attempt)
                continue
            raise ValueError("network_failure_after_retries") from None
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise ValueError("invalid_json_payload") from None
    raise ValueError("retry_exhausted")


def fetch_all_pages(key: str, *, start_date: str, page_size: int = 100, max_pages: int = 12,
                    request_fn=page_request) -> tuple[list[dict], dict]:
    """Stop on the counted final page, guard against count drift and truncation."""
    if not key:
        raise ValueError("secret_not_set")
    if not parse_day(start_date):
        raise ValueError("invalid_start_date")
    all_rows: list[dict] = []
    total_counts: list[int] = []
    per_page: list[int] = []
    last_page = None
    for page in range(1, max_pages + 1):
        items, total = request_fn(key, start_date=start_date, page_no=page, page_size=page_size)
        total_counts.append(total)
        per_page.append(len(items))
        all_rows.extend(items)
        if len(items) == 0 or len(all_rows) >= total or len(items) < page_size:
            last_page = page
            break
        time.sleep(0.12)
    expected = total_counts[0] if total_counts else 0
    drift = len(set(total_counts)) > 1
    page_count_expected = math.ceil(expected / page_size) if expected else 0
    complete = bool(last_page is not None and len(all_rows) == expected and not drift)
    if expected == 0 and len(all_rows) == 0 and last_page == 1 and not drift:
        complete = True
    meta = {
        "provider_total_count_initial": expected,
        "provider_total_count_last": total_counts[-1] if total_counts else None,
        "provider_total_count_drifted": drift,
        "pages_requested": len(per_page),
        "pages_expected_initial": page_count_expected,
        "per_page_counts": per_page,
        "raw_row_count": len(all_rows),
        "pagination_complete": complete,
        "pagination_limit_hit": last_page is None,
    }
    return all_rows, meta


def summarize(rows: list[dict], *, as_of: date, start_date: str, pagination: dict) -> dict:
    n = len(rows)
    ids = [str(r.get("contentid")) for r in rows if is_present(r.get("contentid"))]
    duplicates = sum(c - 1 for c in Counter(ids).values() if c > 1)
    field_present = Counter()
    status = Counter()
    geo = Counter()
    regions = Counter()
    modification_lag_days: list[int] = []
    modified_days = []
    unknown = set()
    event_candidates = 0
    ending_soon_candidates = 0
    for row in rows:
        unknown.update(row)
        for name in FIELDS:
            if is_present(row.get(name)):
                field_present[name] += 1
        region = region_from_address(row.get("addr1"))
        regions[region] += 1
        start, end = parse_day(row.get("eventstartdate")), parse_day(row.get("eventenddate"))
        if start is None or end is None:
            status["invalid_or_missing_date"] += 1
            event_state = "invalid"
        elif end < start:
            status["end_before_start"] += 1
            event_state = "invalid"
        elif end < as_of:
            status["ended_before_as_of"] += 1
            event_state = "ended"
        elif start > as_of:
            status["not_started_by_as_of"] += 1
            event_state = "future"
        else:
            status["within_published_date_range"] += 1
            event_state = "in_window"
        try:
            x = float(row.get("mapx"))
            y = float(row.get("mapy"))
            if 124 <= x <= 133 and 32 <= y <= 39.5:
                geo["plausible_korean_coordinate_range"] += 1
                coord_ok = True
            elif 124 <= y <= 133 and 32 <= x <= 39.5:
                geo["possible_lat_lon_swap"] += 1
                coord_ok = False
            else:
                geo["outside_bounding_range"] += 1
                coord_ok = False
        except (TypeError, ValueError, OverflowError):
            geo["missing_or_non_numeric"] += 1
            coord_ok = False
        if event_state in ("future", "in_window") and coord_ok and is_present(row.get("title")):
            event_candidates += 1
            if event_state == "in_window" and 0 <= (end - as_of).days <= 7:
                ending_soon_candidates += 1
        modified = parse_modified(row.get("modifiedtime"))
        if modified:
            modified_days.append(modified)
            modification_lag_days.append((as_of - modified).days)
        elif is_present(row.get("modifiedtime")):
            status["invalid_modifiedtime_format"] += 1

    all_fields = sorted(unknown)
    coverage = {k: round(100 * field_present[k] / n, 1) if n else None for k in FIELDS}
    result = {
        "schema_version": "koreamate.eda5.tourapi.qa.v1",
        "dataset": "KTO TourAPI KorService2/searchFestival2",
        "scope": "Full paginated snapshot for fixed eventStartDate; NOT all festivals in Korea",
        "as_of_local_date": as_of.isoformat(),
        "start_date_filter": start_date,
        "collected_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "pagination": pagination,
        "records_evaluated": n,
        "unique_nonempty_contentid_count": len(set(ids)),
        "missing_contentid_count": n - len(ids),
        "duplicate_contentid_occurrences": duplicates,
        "field_coverage_percent": coverage,
        "field_names_returned": all_fields,
        "event_period_status_counts": dict(sorted(status.items())),
        "coordinate_quality_counts": dict(sorted(geo.items())),
        "event_candidate_with_coordinates_count": event_candidates,
        "ending_within_7_days_candidate_count": ending_soon_candidates,
        "region_from_address_counts": dict(sorted(regions.items())),
        "region_from_address_method": "Approximate prefix of addr1, not authoritative 17-region mapping",
        "region_from_areacode_count": field_present["areacode"],
        "modified_date_coverage_percent": coverage["modifiedtime"],
        "modified_date_min": min(modified_days).isoformat() if modified_days else None,
        "modified_date_max": max(modified_days).isoformat() if modified_days else None,
        "modified_lag_days_median": round(statistics.median(modification_lag_days), 1) if modification_lag_days else None,
        "modified_lag_days_p90": sorted(modification_lag_days)[math.ceil(0.9*len(modification_lag_days)) - 1] if modification_lag_days else None,
        "modified_over_30_days_count": sum(v > 30 for v in modification_lag_days),
        "modified_in_future_count": sum(v < 0 for v in modification_lag_days),
        "open_now_verified": False,
        "bookable_verified": False,
        "individual_records_or_ids_persisted": False,
        "source_url": ENDPOINT,
        "methodological_limits": [
            "Published dates are not verified operating hours, tickets, booking or cancellation status",
            "Single fixed-date, single-API response; sampling windows and actual database can change",
            "TourAPI address prefixes are approximate and cannot substitute coordinate reverse geocoding",
            "Modifiedtime is record timestamp, not proof of actual field-level freshness",
        ],
    }
    return result


def render_summary(r: dict) -> str:
    p = r["pagination"]
    dates = r["event_period_status_counts"]
    lines = [
        "## Korea Mate · TourAPI complete pagination audit",
        "",
        f"- Status: **{'COMPLETE' if p['pagination_complete'] else 'INCOMPLETE'}**",
        f"- Snapshot date (KST): **{r['as_of_local_date']}**; eventStartDate filter: **{r['start_date_filter']}**",
        f"- Records: **{r['records_evaluated']}** / initial provider total **{p['provider_total_count_initial']}**",
        f"- Pages: **{p['pages_requested']}** (row counts: {', '.join(str(x) for x in p['per_page_counts'])})",
        f"- Unique IDs: {r['unique_nonempty_contentid_count']}, duplicates: {r['duplicate_contentid_occurrences']}",
        f"- Event dates: ended {dates.get('ended_before_as_of', 0)}, in-date-window {dates.get('within_published_date_range', 0)}, future {dates.get('not_started_by_as_of', 0)}, invalid/missing {dates.get('invalid_or_missing_date',0)+dates.get('end_before_start',0)}",
        f"- Location candidates (dates+plausible coords+title): **{r['event_candidate_with_coordinates_count']}** / {r['records_evaluated']} (not verified operating/bookable)",
        f"- Coordinate range plausible: {r['coordinate_quality_counts'].get('plausible_korean_coordinate_range',0)}",
        f"- Region field areacode coverage: {r['field_coverage_percent']['areacode']}% (address-prefix classification is approximate)",
        f"- Modifiedtime age median/p90: {r['modified_lag_days_median']} / {r['modified_lag_days_p90']} days (not a freshness guarantee)",
        "",
        "### Region by *address prefix* only (not true reverse-geocoded region)",
        "| Region | Records |",
        "|---|---:|",
    ]
    for region, count in sorted(r['region_from_address_counts'].items(), key=lambda kv: (-kv[1], kv[0])):
        lines.append(f"| {region} | {count} |")
    lines.extend(["", "**Data sharing:** only aggregate metrics were saved, no raw TourAPI rows, titles, IDs, addresses, coordinates or credentials.", ""])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--as-of", default="2026-10-16", type=date.fromisoformat)
    parser.add_argument("--start-date", default="20260717")
    parser.add_argument("--page-size", type=int, default=100)
    parser.add_argument("--max-pages", type=int, default=12)
    parser.add_argument("--out", type=Path, default=Path("tourapi_full_qa.json"))
    parser.add_argument("--summary", type=Path, default=Path("tourapi_full_qa.md"))
    args = parser.parse_args()
    if not 1 <= args.page_size <= 1000 or not 1 <= args.max_pages <= 20:
        raise SystemExit("Invalid safe page limits")
    key = normalized_key(os.getenv("TOURAPI_SERVICE_KEY", ""))
    if not key:
        print("QA_STATUS=blocked_missing_secret")
        return 2
    try:
        rows, pagination = fetch_all_pages(key, start_date=args.start_date, page_size=args.page_size, max_pages=args.max_pages)
    except ValueError as err:
        # Only our sanitized exception strings are logged.
        print("QA_STATUS=collection_failed", "reason=" + str(err)[:50])
        return 1
    finally:
        key = ""  # Never write token or a credential-bearing request URL.
    result = summarize(rows, as_of=args.as_of, start_date=args.start_date, pagination=pagination)
    result["collection_outcome"] = "complete" if pagination["pagination_complete"] else "incomplete"
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.summary.write_text(render_summary(result), encoding="utf-8")
    # Single line includes aggregates only; GitHub Actions logs can be read for verification.
    print("KOREAMATE_TOURAPI_FULL_QA_JSON=" + json.dumps({
        "complete": result["collection_outcome"],
        "n": result["records_evaluated"],
        "pagination": result["pagination"],
        "date_status": result["event_period_status_counts"],
        "geo_status": result["coordinate_quality_counts"],
        "region_counts": result["region_from_address_counts"],
        "coverage": result["field_coverage_percent"],
        "modified_lag_median": result["modified_lag_days_median"],
        "candidate_count": result["event_candidate_with_coordinates_count"],
        "ending_soon_count": result["ending_within_7_days_candidate_count"],
        "duplicate_content_ids": result["duplicate_contentid_occurrences"],
    }, ensure_ascii=False, sort_keys=True))
    return 0 if pagination["pagination_complete"] else 1


if __name__ == "__main__":
    sys.exit(main())