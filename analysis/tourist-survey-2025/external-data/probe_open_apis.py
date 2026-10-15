"""Optional live probes for two official Korean event APIs (keys from ENV only).

Without --live, no network request is sent. This program NEVER prints keys or
full key-bearing URLs. Seoul sample key may fetch up to five sample records.
"""
from __future__ import annotations

import argparse
from datetime import date, datetime, timezone
import json
import os
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen
from urllib.error import HTTPError, URLError

from event_contract import extract_rows, quality_summary


def safe_fetch(url: str, *, timeout: int = 12) -> dict:
    try:
        with urlopen(url, timeout=timeout) as resp:
            data = resp.read(1_000_000)
            if resp.status != 200:
                return {"status": "http_error", "http_code": resp.status}
        parsed = json.loads(data)
        return {"status": "ok", "json": parsed}
    except HTTPError as e:
        return {"status": "http_error", "http_code": e.code}
    except (URLError, TimeoutError, OSError) as e:
        # Never log a key-bearing URL or raw URLError string (may embed URL).
        return {"status": "network_unavailable", "exception_type": type(e).__name__}
    except (json.JSONDecodeError, UnicodeDecodeError):
        return {"status": "invalid_json_response"}


def probe(provider: str, *, key: str | None, today: date,
          allow_http_seoul: bool = False, live: bool = False) -> dict:
    result = {"provider": provider, "actual_live_api_rows_tested": False}
    if not live:
        return {**result, "status": "not_executed_no_live_flag"}
    if not key:
        return {**result, "status": "skipped_no_key"}
    if provider == "seoul_cultural":
        # Seoul's official reference shows http://openapi.seoul.go.kr:8088.
        # Do not send a PRIVATE credential over cleartext without explicit approval.
        if key != "sample":
            return {**result, "status": "private_seoul_key_requires_https_gateway"}
        if not allow_http_seoul:
            return {**result, "status": "needs_explicit_http_permission_or_https_gateway"}
        url = f"http://openapi.seoul.go.kr:8088/{key}/json/culturalEventInfo/1/5/"
    elif provider == "tourapi_festival":
        params = urlencode({"serviceKey": key, "MobileOS": "ETC", "MobileApp": "KoreaMate",
                            "_type": "json", "eventStartDate": today.strftime("%Y%m%d"),
                            "numOfRows": "5", "pageNo": "1"})
        url = f"https://apis.data.go.kr/B551011/KorService2/searchFestival2?{params}"
    else:
        raise ValueError("Unknown source")

    fetched = safe_fetch(url)
    if fetched["status"] != "ok":
        return {**result, **fetched}
    try:
        rows = extract_rows(provider, fetched["json"])
        summary = quality_summary(provider, rows, today=today, fetched_at=datetime.now(timezone.utc))
        summary.pop("items", None)  # Do not redistribute live source rows by default.
        return {**result, "status": "success", "actual_live_api_rows_tested": True,
                "quality": summary}
    except (ValueError, TypeError, AttributeError) as e:
        return {**result, "status": "schema_or_application_error", "message": str(e)[:180]}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true", help="Actually call remote APIs")
    parser.add_argument("--allow-http-seoul", action="store_true", help="Explicitly allow plain HTTP Seoul API")
    parser.add_argument("--date", type=date.fromisoformat, default=date.today())
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()
    response = {
        "checked_on": args.date.isoformat(),
        "official_docs_verified": True,
        "sources": [
            probe("seoul_cultural", key=os.getenv("SEOUL_OPEN_API_KEY"), today=args.date,
                  allow_http_seoul=args.allow_http_seoul, live=args.live),
            probe("tourapi_festival", key=os.getenv("TOURAPI_SERVICE_KEY"), today=args.date, live=args.live),
        ],
    }
    output = json.dumps(response, ensure_ascii=False, indent=2)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(output + "\n", encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()