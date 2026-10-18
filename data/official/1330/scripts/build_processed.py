#!/usr/bin/env python3
"""1330 official ZIP -> normalized month×language/type and month×region/type.
Pure stdlib. Reads only official ZIP downloads (no API/scraping). Keeps them unchanged.
"""
import csv
import hashlib
import io
import json
import pathlib
import zipfile
from collections import defaultdict, Counter

ROOT = pathlib.Path(__file__).resolve().parent.parent
RAW = ROOT / "raw" / "downloads"
OUT = ROOT / "processed" / "generated"
PERIODS = {
    "2025": ("20261018213628__202501-202512_데이터랩_다운로드.zip",
             "fc8b9f12bd05c821447f0c0ae1492a35417653a0eefed4bfddadfda412273289", 12, 692437),
    "2026_01_09": ("20261018213802__202601-202609_데이터랩_다운로드.zip",
                   "6c5b9ec0f03c5fc84f82e08d4f0162be39af1bda7f6a4c1f61b191dc3c031948", 9, 456684),
}
SUFFIXES = {
    "region": "관광안내 지도.csv",
    "type": "유형별 안내 건수.csv",
    "language": "어권별 안내 건수.csv",
    "month_region_type": "지역별, 유형별 안내.csv",
    "month_language_type": "어권별, 유형별 안내.csv",
}
REGION = dict(zip(
    "서울 부산 대구 인천 광주 대전 울산 세종 경기 충북 충남 전남 경북 경남 제주 강원 전북".split(),
    "서울특별시 부산광역시 대구광역시 인천광역시 광주광역시 대전광역시 울산광역시 세종특별자치시 경기도 충청북도 충청남도 전라남도 경상북도 경상남도 제주특별자치도 강원특별자치도 전북특별자치도".split(),
))

def decode(blob):
    return [{k.strip(): (v or "").strip() for k,v in r.items()}
            for r in csv.DictReader(io.StringIO(blob.decode("utf-8-sig")))]

def csv_out(name, keys, records):
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / name).open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(records)

def main():
    lang = defaultdict(int)
    region = defaultdict(int)
    duplicate = Counter()
    year_summaries = {}
    for period,(zip_name, expected_sha, n_months, expected_total) in PERIODS.items():
        zpath = RAW / zip_name
        if not zpath.is_file():
            raise FileNotFoundError(
                f"공식 원본 ZIP 없음: {zpath}\n"
                "한국관광 데이터랩 관광안내에서 공식 전체 CSV 다운로드 후 raw/downloads/에 보관하세요.")
        assert hashlib.sha256(zpath.read_bytes()).hexdigest() == expected_sha, "ZIP SHA256 mismatch"
        with zipfile.ZipFile(zpath) as z:
            parts = {}
            for typ,suffix in SUFFIXES.items():
                names = [n for n in z.namelist() if n.endswith("_"+suffix)]
                assert len(names)==1,(typ,names)
                parts[typ] = decode(z.read(names[0]))
        summary = {}
        summary["region"] = {REGION[r["광역자치단체명"]]:int(r["안내 건수"]) for r in parts["region"]}
        summary["language"] = {r["어권명"]:int(r["안내 건수"]) for r in parts["language"]}
        summary["type"] = {r["안내유형명"]:int(r["안내 건수"]) for r in parts["type"]}
        for key,items in summary.items():
            assert sum(items.values())==expected_total,(period,key)
        year_summaries[period] = summary
        months = set()
        for r in parts["month_language_type"]:
            y,m,t,n = period,r["기준연월"],r["안내유형명"],int(r["안내 건수"])
            months.add(m)
            if t != "전체":
                lang[(y,m,r["언어구분명"],t)] += n
                duplicate[(y,m,r["언어구분명"],t)] += 1
        assert len(months)==n_months, (period,months)
        for r in parts["month_region_type"]:
            if r["안내유형명"] != "전체":
                region[(period,r["기준연월"],r["시도명"],r["안내유형명"])] += int(r["안내 건수"])
        assert sum(v for (p,*_),v in lang.items() if p==period)==expected_total
        assert sum(v for (p,*_),v in region.items() if p==period)==expected_total
        for kind, expected in summary["type"].items():
            assert sum(v for (p,m,x,t),v in lang.items() if p==period and t==kind)==expected
        for language,expected in summary["language"].items():
            assert sum(v for (p,m,l,t),v in lang.items() if p==period and l==language)==expected
        for area,expected in summary["region"].items():
            assert sum(v for (p,m,r,t),v in region.items() if p==period and r==area)==expected
        for month in months:
            left = sum(v for (p,m,*_),v in lang.items() if p==period and m==month)
            right = sum(v for (p,m,*_),v in region.items() if p==period and m==month)
            assert left==right,(period,month,left,right)
    csv_out("month_language_type.csv",["period","year_month","language","type","count"],
            [dict(zip(["period","year_month","language","type","count"],[p,m,l,t,n]))
             for (p,m,l,t),n in sorted(lang.items())])
    csv_out("month_region_type.csv",["period","year_month","region","type","count"],
            [dict(zip(["period","year_month","region","type","count"],[p,m,r,t,n]))
             for (p,m,r,t),n in sorted(region.items())])
    monthly = defaultdict(int)
    for (p,m,l,t),n in lang.items():monthly[(p,m)]+=n
    csv_out("monthly_totals.csv",["period","year_month","count"],
            [dict(period=p,year_month=m,count=n) for (p,m),n in sorted(monthly.items())])
    csv_out("duplicate_other_keys.csv",
            ["period","year_month","language","type","source_rows_for_key"],
            [dict(period=p,year_month=m,language=l,type=t,source_rows_for_key=n)
             for (p,m,l,t),n in sorted(duplicate.items()) if n>1])
    print(f"PASS: 2025=692437, 2026.01-09=456684; {len(lang)} language-type, "
          f"{len(region)} region-type rows; {sum(n>1 for n in duplicate.values())} duplicate keys merged")
    print(f"Saved to {OUT}")

if __name__=="__main__":
    main()
