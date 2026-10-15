import unittest
from datetime import date
from verify_regions_and_details import official_regions,region_audit,detail_audit,seoul_audit,choose_sample,canon_title

class Audit(unittest.TestCase):
    def test_region_mapping(self):
        src=[{"lDongRegnCd":"11","lDongRegnNm":"서울특별시"},{"lDongRegnCd":"26","lDongRegnNm":"부산광역시"}]
        self.assertEqual(official_regions(src),{"11":"서울","26":"부산"})
    def test_code_rescues_address(self):
        rows=[{"lDongRegnCd":"11","lDongSignguCd":"110", "addr1":"서울 중구"},
              {"lDongRegnCd":"26","addr1":"부산광역시 남구"},
              {"lDongRegnCd":"11","addr1":"알수없는주소"}]
        a=region_audit(rows,{"11":"서울","26":"부산"})
        self.assertEqual(a["comparisons"]["code_vs_address_agree"],2)
        self.assertEqual(a["comparisons"]["code_rescues_unclassified_address"],1)
    def test_disagreement_not_hidden(self):
        a=region_audit([{"lDongRegnCd":"11","addr1":"부산 해운대구"}],{"11":"서울"})
        self.assertEqual(a["comparisons"]["code_vs_address_disagree"],1)
    def test_region_no_denominator(self):
        self.assertIsNone(region_audit([], {})["code_address_agreement_pct"])
    def test_status_sample_deterministic(self):
        items=[{"contentid":str(i),"eventstartdate":"20261001","eventenddate":"20261020"} for i in range(40)]
        self.assertEqual(choose_sample(items,date(2026,10,16),12),choose_sample(items,date(2026,10,16),12))
        self.assertEqual(len(choose_sample(items,date(2026,10,16),12)),12)
    def test_expired_not_sampled(self):
        rows=[{"contentid":"1","eventstartdate":"20260101","eventenddate":"20260930"}]
        self.assertEqual(choose_sample(rows,date(2026,10,16)),[])
    def test_detail_empty_never_claim_booking(self):
        selected=[{"contentid":"1","contenttypeid":"15"}]
        q=detail_audit(selected, lambda endpoint, params:([],"http_404"))
        self.assertFalse(q["bookable_verified"])
        self.assertEqual(q["counters"]["common_status_http_404"],1)
    def test_detail_source_coordinates_compare(self):
        selected=[{"contentid":"1","contenttypeid":"15","mapx":"127.0","mapy":"37.0", "eventstartdate":"20261001","eventenddate":"20261020"}]
        def fake(endpoint, params):
            if endpoint=="detailCommon2":return ([{"mapx":"127.0","mapy":"37.0","homepage":"https://example.com"}],"ok")
            return ([{"eventplace":"공연장","usetimefestival":"무료","eventstartdate":"20261001","eventenddate":"20261020"}],"ok")
        q=detail_audit(selected,fake)
        self.assertEqual(q["counters"]["common_coordinate_compared"],1)
        self.assertEqual(q["counters"]["intro_dates_comparable"],1)
        self.assertNotIn("common_coordinate_diff_over_500m",q["counters"])
    def test_seoul_sample_no_overclaim(self):
        data=[{"TITLE":"Korea Fest","STRTDATE":"2026-10-01","LOT":"127.1","LAT":"37.5"}]
        out=seoul_audit(data,{"status":"ok","total_count":1222},[{"title":"Korea-Fest","eventstartdate":"20261001"}])
        self.assertEqual(out["comparisons"]["title_and_date_match"],1)
        self.assertEqual(out["sample_rows"],1)
        self.assertIn("not representative",out["comparison_limit"])
    def test_canon_title(self):
        self.assertEqual(canon_title(" K-Fest! 2026"),"kfest2026")

if __name__ == '__main__':unittest.main()