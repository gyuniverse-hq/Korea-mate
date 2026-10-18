#!/usr/bin/env python3
"""Read-only validation of generated month/type CSVs and baseline GitHub summaries."""
import csv
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parent.parent
P=ROOT/"processed"/"generated"
def read(name):
    with (P/name).open(encoding="utf-8-sig",newline="") as f:
        return list(csv.DictReader(f))
def main():
    lang, region, monthly = read("month_language_type.csv"),read("month_region_type.csv"),read("monthly_totals.csv")
    assert len(lang)==1281 and len(region)==2271
    a=Counter(); b=Counter(); m=Counter()
    for r in lang:a[r["period"]]+=int(r["count"])
    for r in region:b[r["period"]]+=int(r["count"])
    for r in monthly:m[r["period"]]+=int(r["count"])
    expected={"2025":692437,"2026_01_09":456684}
    assert dict(a)==dict(b)==dict(m)==expected,(a,b,m)
    assert len(monthly)==21
    print("PASS - 21 monthly totals; 1281 language-type & 2271 region-type rows; annual totals match")
if __name__=="__main__":
    main()
