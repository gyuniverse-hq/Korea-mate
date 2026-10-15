"""Offline tests. No external API calls and no credentials."""
import unittest
from datetime import date
from collect_all_festivals import parse_page, fetch_all_pages, summarize, region_from_address, normalized_key


def fixture(i, **kw):
    result = {"contentid": str(i), "title": f"SYNTHETIC event {i}",
              "addr1": "서울특별시 종로구 가상동 1", "mapx": "126.9", "mapy": "37.5",
              "eventstartdate": "20261001", "eventenddate": "20261030", "modifiedtime": "20261001090000"}
    result.update(kw)
    return result


class FullPaginationTests(unittest.TestCase):
    def test_encode_decode_once(self):
        self.assertEqual(normalized_key("abc%2Bdef%3D"), "abc+def=")
        self.assertEqual(normalized_key("abc+def="), "abc+def=")

    def test_parse_response_array_and_single(self):
        for items, n in [([fixture(1)], 1), (fixture(1), 1)]:
            response = {"response": {"header": {"resultCode": "0000"},
                         "body": {"totalCount": 1, "items": {"item": items}}}}
            got, count = parse_page(response)
            self.assertEqual(len(got), n)
            self.assertEqual(count, 1)

    def test_reject_invalid_service_result(self):
        with self.assertRaises(ValueError):
            parse_page({"response": {"header": {"resultCode": "9999"}, "body": {"totalCount": 1}}})

    def test_seven_records_from_three_pages(self):
        seen = []
        def mock(key, start_date, page_no, page_size):
            seen.append(page_no)
            return [fixture(i) for i in range((page_no-1)*3+1, min(page_no*3+1,8))],7
        all_rows, meta = fetch_all_pages("DUMMY", start_date="20260717", page_size=3, max_pages=6, request_fn=mock)
        self.assertEqual(seen, [1,2,3])
        self.assertEqual(meta["per_page_counts"], [3,3,1])
        self.assertTrue(meta["pagination_complete"])
        self.assertEqual(len(all_rows),7)

    def test_detect_incomplete_maxpages(self):
        def mock(key, start_date, page_no, page_size):
            return [fixture(i) for i in range(page_size)], 30
        _, meta = fetch_all_pages("DUMMY", start_date="20260717", page_size=10, max_pages=2, request_fn=mock)
        self.assertFalse(meta["pagination_complete"])
        self.assertTrue(meta["pagination_limit_hit"])

    def test_detect_provider_count_drift(self):
        def mock(key, start_date, page_no, page_size):
            return ([fixture(1), fixture(2)] if page_no==1 else [fixture(3)]), (3 if page_no==1 else 4)
        _, meta = fetch_all_pages("DUMMY", start_date="20260717", page_size=2, max_pages=3, request_fn=mock)
        self.assertTrue(meta["provider_total_count_drifted"])
        self.assertFalse(meta["pagination_complete"])

    def test_region_aliases(self):
        self.assertEqual(region_from_address("전북특별자치도 전주시 가상로"), "전북")
        self.assertEqual(region_from_address("강원특별자치도 춘천시 가상로"), "강원")
        self.assertEqual(region_from_address("부산광역시 해운대구 가상로"), "부산")
        self.assertEqual(region_from_address(""), "주소없음")

    def test_summary_counts_without_raw_identifiers(self):
        rows = [fixture(1), fixture(2, eventenddate="20261010"), fixture(2, mapx="37.5", mapy="126.9"), fixture(4, addr1="전북특별자치도 전주시 가상동 1", eventstartdate="20261101", eventenddate="20261130")]
        info = {"provider_total_count_initial":4,"provider_total_count_last":4,"per_page_counts":[4],"pages_requested":1,"pages_expected_initial":1,"pagination_complete":True,"provider_total_count_drifted":False,"pagination_limit_hit":False,"raw_row_count":4}
        summary = summarize(rows,as_of=date(2026,10,16),start_date="20260717",pagination=info)
        self.assertEqual(summary["event_period_status_counts"]["ended_before_as_of"],1)
        self.assertEqual(summary["event_period_status_counts"]["within_published_date_range"],2)
        self.assertEqual(summary["event_period_status_counts"]["not_started_by_as_of"],1)
        self.assertEqual(summary["duplicate_contentid_occurrences"],1)
        self.assertEqual(summary["coordinate_quality_counts"]["possible_lat_lon_swap"],1)
        self.assertEqual(summary["region_from_address_counts"]["전북"],1)
        self.assertEqual(summary["event_candidate_with_coordinates_count"],2)
        serialized = str(summary)
        self.assertNotIn("SYNTHETIC event",serialized)
        self.assertNotIn("가상동",serialized)
        self.assertFalse(summary["bookable_verified"])

if __name__ == '__main__':
    unittest.main()