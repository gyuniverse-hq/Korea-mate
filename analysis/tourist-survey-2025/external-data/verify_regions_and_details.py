"""Korea Mate: bounded TourAPI region/detail audit and Seoul sample comparison.

No event rows, titles, IDs, addresses, URLs, coordinates or keys are persisted,
logged or committed. ONLY aggregate counts and source/quality statuses are saved.
The Seoul sample uses the public, deliberately limited `sample` key over HTTP;
NEVER put private credentials in the Seoul URL.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import date, datetime, timezone
import json
import math
import os
from pathlib import Path
import random
import re
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from collect_all_festivals import (
    ENDPOINT, fetch_all_pages, normalized_key, parse_day, parse_page,
    region_from_address, is_present,
)

BASE = "https://apis.data.go.kr/B551011/KorService2"
SEOUL_SAMPLE = "http://openapi.seoul.go.kr:8088/sample/json/culturalEventInfo/1/5/"
COMMON_PARAMS = {"MobileOS": "ETC", "MobileApp": "KoreaMate", "_type": "json"}


def safe_api(endpoint: str, key: str, extra: dict, timeout: int = 18) -> tuple[list[dict], str]:
    """Return rows plus sanitized status; NEVER leak key or response body."""
    params = urlencode({"serviceKey": key, **COMMON_PARAMS, **extra})
    req = Request(f"{BASE}/{endpoint}?{params}", headers={"User-Agent": "KoreaMate-EDA-Audit/1.0"})
    try:
        with urlopen(req, timeout=timeout) as resp:
            if resp.status != 200:
                return [], f"http_{resp.status}"
            raw = resp.read(1_500_000)
        data = json.loads(raw)
        rows, _ = parse_page(data)
        return rows, "ok"
    except HTTPError as e:
        return [], f"http_{e.code}"
    except (URLError, TimeoutError, OSError) as e:
        return [], "network_" + type(e).__name__
    except (json.JSONDecodeError, UnicodeDecodeError, ValueError, TypeError):
        return [], "invalid_schema_or_json"


def official_regions(ldong_rows: list[dict]) -> dict[str, str]:
    """Use TourAPI ldongCode2, with a normalized source city/province name."""
    result: dict[str, str] = {}
    for row in ldong_rows:
        code = str(row.get("code") or row.get("lDongRegnCd") or "").strip()
        value = row.get("lDongRegnNm") or row.get("name") or ""
        region = region_from_address(value)
        if code and region != "주소지역미분류" and region != "주소없음":
            result[code] = region
    return result


def region_audit(rows: list[dict], region_code_map: dict[str, str]) -> dict:
    coverage = Counter()
    comparisons = Counter()
    code_values = Counter()
    for row in rows:
        code = str(row.get("lDongRegnCd", "")).strip()
        subcode = str(row.get("lDongSignguCd", "")).strip()
        if code:
            coverage["ldong_region_present"] += 1
            code_values[code] += 1
        if subcode:
            coverage["ldong_sigungu_present"] += 1
        if is_present(row.get("areacode")):
            coverage["old_areacode_present"] += 1
        by_addr = region_from_address(row.get("addr1"))
        mapped = region_code_map.get(code)
        if mapped:
            comparisons["official_code_mapped"] += 1
            if by_addr in {"주소지역미분류", "주소없음"}:
                comparisons["code_rescues_unclassified_address"] += 1
            elif by_addr == mapped:
                comparisons["code_vs_address_agree"] += 1
            else:
                comparisons["code_vs_address_disagree"] += 1
        elif code:
            comparisons["code_unmapped"] += 1
        if by_addr in {"주소지역미분류", "주소없음"}:
            comparisons["address_unclassified"] += 1
    return {
        "records": len(rows),
        "coverage_counts": dict(coverage),
        "distinct_region_codes": len(code_values),
        "official_ldong_regions_resolved": len(region_code_map),
        "comparisons": dict(comparisons),
        "code_coverage_pct": round(100*coverage["ldong_region_present"]/len(rows), 1) if rows else None,
        "code_address_agreement_pct": (
            round(100*comparisons["code_vs_address_agree"]/
                 (comparisons["code_vs_address_agree"]+comparisons["code_vs_address_disagree"]), 1)
            if comparisons["code_vs_address_agree"]+comparisons["code_vs_address_disagree"] else None),
        "note": "Code mapped via ldongCode2; address only heuristic; coordinate range alone is NOT precise geocoding.",
    }


def haversine_m(a: dict, b: dict) -> float | None:
    try:
        lon1, lat1 = float(a["mapx"]), float(a["mapy"])
        lon2, lat2 = float(b["mapx"]), float(b["mapy"])
    except (KeyError, TypeError, ValueError):
        return None
    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)
    h = math.sin(dlat/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlon/2)**2
    return 2*6371000*math.asin(min(1, math.sqrt(h)))


def choose_sample(rows: list[dict], as_of: date, limit=12) -> list[dict]:
    # Fixed selection makes audits reproducible without exposing IDs.
    eligible = []
    for row in rows:
        begin, end = parse_day(row.get("eventstartdate")), parse_day(row.get("eventenddate"))
        if (begin and end and end >= as_of and begin <= end and
            is_present(row.get("contentid"))):
            eligible.append(row)
    rng = random.Random(20261016)
    rng.shuffle(eligible)
    return eligible[:limit]


def detail_audit(selected: list[dict], request_fn) -> dict:
    q=Counter()
    common_fields = ("homepage", "overview", "mapx", "mapy", "addr1", "modifiedtime", "title", "lDongRegnCd")
    intro_fields = ("eventplace", "playtime", "usetimefestival", "bookingplace", "eventstartdate", "eventenddate", "sponsor1tel")
    q["selection"] = len(selected)
    for row in selected:
        cid = str(row.get("contentid", "")).strip()
        contenttype = str(row.get("contenttypeid", "15") or "15")
        common, stat_common = request_fn("detailCommon2", {"contentId": cid, "numOfRows":"1", "pageNo":"1"})
        intro, stat_intro = request_fn("detailIntro2", {"contentId": cid, "contentTypeId": contenttype,
                                                        "numOfRows":"1", "pageNo":"1"})
        q["common_status_" + stat_common] += 1
        q["intro_status_" + stat_intro] += 1
        if common:
            d=common[0]
            q["common_nonempty"] += 1
            for f in common_fields:
                if is_present(d.get(f)): q["common_"+f] += 1
            metres = haversine_m(d, row)
            if metres is not None:
                q["common_coordinate_compared"] += 1
                if metres > 100: q["common_coordinate_diff_over_100m"] += 1
                if metres > 500: q["common_coordinate_diff_over_500m"] += 1
        if intro:
            d=intro[0]
            q["intro_nonempty"] += 1
            for f in intro_fields:
                if is_present(d.get(f)): q["intro_"+f] += 1
            if is_present(d.get("eventstartdate")) and is_present(d.get("eventenddate")):
                q["intro_dates_comparable"] += 1
                if str(d["eventstartdate"]) != str(row.get("eventstartdate")) or str(d["eventenddate"]) != str(row.get("eventenddate")):
                    q["intro_dates_differ_from_listing"] += 1
    return {"n_selected": len(selected), "counters": dict(q),
            "bookable_verified": False,"actual_operating_verified": False,
            "interpretation": "Fields appear in provider listing/detail; no organizer/booking confirmation was performed"}


def seoul_sample_fetch(timeout=12) -> tuple[list[dict], dict]:
    # PUBLIC sample key only, and never use a privately provisioned key over HTTP.
    req=Request(SEOUL_SAMPLE, headers={"User-Agent":"KoreaMate-EDA-Audit/1.0"})
    try:
        with urlopen(req,timeout=timeout) as resp:
            data=json.loads(resp.read(1_000_000))
        obj=data.get("culturalEventInfo",{}) if isinstance(data,dict) else {}
        rows=obj.get("row",[]) if isinstance(obj,dict) else []
        if isinstance(rows,dict):rows=[rows]
        if not isinstance(rows,list):rows=[]
        return [x for x in rows if isinstance(x,dict)], {"status":"ok", "total_count":obj.get("list_total_count")}
    except HTTPError as e:
        return [], {"status":f"http_{e.code}"}
    except (URLError,TimeoutError,OSError) as e:
        return [], {"status":"network_"+type(e).__name__}
    except (ValueError,TypeError,AttributeError):
        return [], {"status":"invalid_json_or_schema"}


def canon_title(text: str)->str:
    return re.sub(r"[^가-힣A-Za-z0-9]", "", str(text or "")).lower()


def seoul_audit(sample: list[dict], status: dict, tour_rows: list[dict]) -> dict:
    title_set = {canon_title(x.get("title")):x for x in tour_rows if canon_title(x.get("title"))}
    fields=("TITLE","STRTDATE","END_DATE","PLACE","GUNAME","LOT","LAT","ORG_LINK","HMPG_ADDR")
    coverage=Counter()
    quality=Counter()
    for row in sample:
        for f in fields:
            if is_present(row.get(f)):coverage[f]+=1
        try:
            lot,lat=float(row["LOT"]),float(row["LAT"])
            if 124<=lot<=133 and 32<=lat<=39.5:quality["plausible_coordinates"]+=1
        except(KeyError,ValueError,TypeError):pass
        t=canon_title(row.get("TITLE"))
        if t and t in title_set:
            quality["title_match"]+=1
            q=title_set[t]
            sd=re.sub(r"[^0-9]","",str(row.get("STRTDATE","")))[:8]
            if sd and sd==str(q.get("eventstartdate","")):
                quality["title_and_date_match"]+=1
    return {"provider":"seoul_cultural_public_sample", "status":status.get("status"),
            "sample_rows":len(sample),"reported_total":status.get("total_count"),
            "field_coverage_counts":dict(coverage), "comparisons":dict(quality),
            "comparison_limit":"At most 5 provider-selected sample rows, not representative; zero matches does not establish no overlap",
            "http_public_sample_only":True}


def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("--as-of",type=date.fromisoformat,default=date(2026,10,16))
    p.add_argument("--start-date",default="20260717")
    p.add_argument("--out",type=Path,default=Path("reports/tourapi_followup_qa.json"))
    p.add_argument("--details",type=int,default=12)
    args=p.parse_args()
    if not 0<=args.details<=24:raise SystemExit("Details sample must be 0..24")
    key=normalized_key(os.getenv("TOURAPI_SERVICE_KEY", ""))
    if not key:
        print("REGION_QA_STATUS=secret_missing")
        return 2
    try:
        rows,pages=fetch_all_pages(key,start_date=args.start_date,page_size=100,max_pages=12)
        if not pages["pagination_complete"]:
            print("REGION_QA_STATUS=pagination_incomplete")
            return 1
        ldong, code_status=safe_api("ldongCode2",key,{"lDongListYn":"N", "numOfRows":"100", "pageNo":"1"})
        mapping=official_regions(ldong)
        selected=choose_sample(rows,args.as_of,limit=args.details)
        details=detail_audit(selected, lambda endpoint,extra:safe_api(endpoint,key,extra))
    except ValueError as err:
        print("REGION_QA_STATUS=collection_failed",str(err)[:60])
        return 1
    finally:
        key=""
    samples,seoul_status=seoul_sample_fetch()
    output={
        "schema_version":"koreamate.eda5.followup.v1",
        "checked_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "as_of":args.as_of.isoformat(),"start_filter":args.start_date,
        "pagination":{"complete":pages["pagination_complete"],"rows":len(rows),"pages":pages["pages_requested"]},
        "ldong_lookup_status":code_status,
        "ldong_response_schema": {"row_count":len(ldong), "field_names": sorted({k for item in ldong for k in item}), "region_map_count":len(mapping)},
        "region":region_audit(rows,mapping),
        "detail_sample":details,
        "seoul_sample":seoul_audit(samples,seoul_status,rows),
        "source_rows_persisted":False,
        "secret_persisted":False,
        "limitations":[
            "Official province codes were checked against address prefixes, NOT independent verified GPS polygons",
            "TourAPI detail fields do NOT establish organizer-confirmed operation or bookability",
            "Seoul API sample (if reached) permits only a few rows, not cross-provider overlap rate inference",
            "Historical one-day snapshot; results may change and do not establish year-round coverage",
        ],
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    mini={"status":"success", "n":len(rows),"region":output["region"],
          "ldong_lookup_status":code_status, "ldong_schema": output["ldong_response_schema"], "detail":details,"seoul":output["seoul_sample"]}
    print("KOREAMATE_EDA5_FOLLOWUP="+json.dumps(mini,ensure_ascii=False,sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())