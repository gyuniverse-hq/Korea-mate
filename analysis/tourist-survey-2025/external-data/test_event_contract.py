import json
from datetime import date, datetime, timezone
from pathlib import Path
import unittest

from event_contract import normalize_event, extract_rows, quality_summary, _date_parse
from probe_open_apis import probe

ROOT = Path(__file__).parent
TODAY = date(2026, 10, 16)
FIXED_TIME = datetime(2026, 10, 16, 0, 0, 0, tzinfo=timezone.utc)


def rows(source, filename):
    payload = json.loads((ROOT / "fixtures" / filename).read_text(encoding="utf-8"))
    assert payload["NOTICE"].startswith("SYNTHETIC")
    return extract_rows(source, payload)


class TestEventContract(unittest.TestCase):
    def test_seoul_valid_date_window_not_open_or_bookable(self):
        row = rows("seoul_cultural", "seoul_synthetic.json")[0]
        e = normalize_event("seoul_cultural", row, today=TODAY, fetched_at=FIXED_TIME)
        self.assertEqual((e.longitude, e.latitude), (126.978, 37.5665))
        self.assertEqual(e.date_window_status, "within_date_window_only")
        self.assertTrue(e.location_candidate)
        self.assertTrue(e.ending_soon_candidate)
        self.assertIsNone(e.bookable)
        self.assertIsNone(e.operating_now)
        self.assertEqual(e.source_record_date, "2026-09-10")

    def test_expired_not_candidate(self):
        row = rows("seoul_cultural", "seoul_synthetic.json")[1]
        e = normalize_event("seoul_cultural", row, today=TODAY)
        self.assertEqual(e.date_window_status, "expired")
        self.assertFalse(e.location_candidate)

    def test_swapped_coordinates_flagged(self):
        row = rows("seoul_cultural", "seoul_synthetic.json")[2]
        e = normalize_event("seoul_cultural", row, today=TODAY)
        self.assertEqual(e.coordinates_status, "swapped_coordinates_suspected")
        self.assertFalse(e.location_candidate)
        self.assertIsNone(e.latitude)

    def test_inverted_dates_flagged(self):
        row = rows("seoul_cultural", "seoul_synthetic.json")[3]
        e = normalize_event("seoul_cultural", row, today=TODAY)
        self.assertIn("end_before_start", e.quality_flags)
        self.assertEqual(e.date_window_status, "invalid")

    def test_tourapi_yymmdd(self):
        row = rows("tourapi_festival", "tourapi_synthetic.json")[0]
        e = normalize_event("tourapi_festival", row, today=TODAY)
        self.assertEqual(e.start_date, "2026-10-20")
        self.assertEqual(e.date_window_status, "future")
        self.assertTrue(e.location_candidate)
        self.assertIsNone(e.bookable)

    def test_tourapi_missing_coordinate(self):
        row = rows("tourapi_festival", "tourapi_synthetic.json")[1]
        e = normalize_event("tourapi_festival", row, today=TODAY)
        self.assertEqual(e.coordinates_status, "missing_or_non_numeric")
        self.assertFalse(e.location_candidate)

    def test_no_data_and_unparseable_date(self):
        self.assertIsNone(_date_parse("2026-99-99"))
        e = normalize_event("seoul_cultural", {"TITLE": "가상"}, today=TODAY)
        self.assertEqual(e.date_window_status, "unknown")

    def test_quality_report(self):
        qs = quality_summary("seoul_cultural", rows("seoul_cultural", "seoul_synthetic.json"), today=TODAY, fetched_at=FIXED_TIME)
        self.assertEqual(qs["row_count"], 4)
        self.assertEqual(qs["coordinate_valid_count"], 3)
        self.assertEqual(qs["location_candidate_count"], 1)
        self.assertIsNone(qs["bookable_confirmed_count"])
        self.assertEqual(qs["ending_soon_candidate_count"], 1)

    def test_no_key_skips_live(self):
        a = probe("tourapi_festival", key=None, today=TODAY, live=True)
        self.assertEqual(a["status"], "skipped_no_key")
        b = probe("seoul_cultural", key="sample", today=TODAY, live=False)
        self.assertEqual(b["status"], "not_executed_no_live_flag")

    def test_requires_explicit_insecure_permission(self):
        res = probe("seoul_cultural", key="test_not_real", today=TODAY, live=True)
        self.assertEqual(res["status"], "private_seoul_key_requires_https_gateway")

    def test_no_fake_url_for_tourapi(self):
        r = normalize_event("tourapi_festival", {"title": "가상", "contentid": "111", "eventstartdate": "20261020", "eventenddate": "20261021"}, today=TODAY)
        self.assertIsNone(r.source_url)
        self.assertIn("detail_url_unavailable", r.quality_flags)


if __name__ == "__main__":
    unittest.main()