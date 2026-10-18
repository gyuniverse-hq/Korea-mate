# KoreaMate v5 second-reviewer source audit

Date: 2026-10-18 UTC. Baseline untouched. No GitHub, login, payment, contact, or external edits.

## Coverage and interpretation
- 61 existing cases attempted; source text recovered and assessed for 46/229 cases (20.09%); 15 remain VERIFICATION_PENDING
- 39 assessed through original-URL page bodies/selected comments returned by the web tool; 7 assessed through indexed original text; neither means live UI or all comments examined
- All 14 legacy-pending cases attempted: 012, 022, 026, 030, 042 recovered; 017, 019, 052, 053, 056, 057, 059, 060, 061 still unavailable
- Reviewed languages: English 20, traditional Chinese 16, Japanese 6, Thai 4
- This is a second-reviewer source audit. Baseline labels were seen, and cases were selected purposively by language, evidence type and outcome risk, then supplemented from recovered sources. It is NOT blinded independent coding, an unbiased disagreement sample, or a population reliability statistic. Source clustering is substantial. No kappa is reported
- Every row separates source claim fidelity from independent incident truth and provider policy. Both latter checks remain false

## Material proposed coding changes (9 cases)
1. 012: SUCCEEDED → PARTIAL for ordering appropriate portions. Author reports repeated over-ordering. Eating enjoyable food does not establish success at the stated portion goal. [Original](https://www.reddit.com/r/koreatravel/comments/1l7udwm)
2. 031: Narrow goal to continued account access after reservation. Author says locks occur after booking/screen change; this does not prove the reservation itself failed. [Indexed original](https://www.ptt.cc/bbs/Korea_Travel/M.1756046653.A.8D5.html)
3. 036: PARTIAL → WORKAROUND only for finding hidden foreign-card choices; narrow goal accordingly. Author found the scroll control; final payment remains unconfirmed. [Indexed original](https://www.ptt.cc/bbs/Korea_Travel/M.1766325755.A.D44.html)
4. 115: SUCCEEDED → UNKNOWN for completed airport refund. A 30-minute queue is reported, but receipt of refund is not. [Indexed original](https://www.ptt.cc/bbs/Korea_Travel/M.1788754903.A.0A6.html)
5. 153: QUESTION → FIRSTHAND, keeping BLOCKED. Author describes actually being unable to book while passport number was unavailable. [Original](https://detail.chiebukuro.yahoo.co.jp/qa/question_detail/q14325836689)
6. 160: WORKAROUND → PARTIAL. Extra walking and treating it as a photo opportunity are described; no alternate route/tool or successful rerouting is reported. [Original](https://www.reddit.com/r/koreatravel/comments/1q4rgo0/)
7. 226: Keep success only after narrowing goal to discovering card stock at T2 CU. The comment says the store had cards, not explicitly that the author purchased one. If purchase remains the goal, use UNKNOWN. [Original](https://www.reddit.com/r/koreatravel/comments/1tqmaa1/things_we_learnt_on_our_trip/)
8. 228: Narrow success to login using KakaoTalk and an American number; taxi ride/use is unreported. Same original as 226
9. 229: WORKAROUND → UNKNOWN. Author reports Korean-only menus but describes using translation apps as advice to readers, without explicitly reporting a completed translated order. Same original as 226

## Other consequential qualifications
- 035: Baseline “only considered Trip” is too categorical. Author's later 06/10 13:10 reply says they finally gave Trip the fee and supplies two images. Those images could not be fetched. Preserve the reported switch, keep final purchase/seat outcome UNKNOWN pending transaction evidence. [Original and follow-ups](https://www.ptt.cc/bbs/Korea_Travel/M.1717939225.A.772.html)
- 118: 手機機型 refers to phone/handset models, not necessarily kiosk models. Correct the ambiguity in the summary. [Original](https://www.ptt.cc/bbs/Korea_Travel/M.1757945404.A.88F.html)
- 068: Comment dates from August 2025, but author places incident at the preceding Christmas, so the incident is historical 2024. Do not date the incident by thread publication
- 065, 067, 068: Exact comment timestamps recovered and stored separately; thread post_date is earlier than these comments
- 129: Initial intended day was blocked, but the answerer later bought tickets and travelled. BLOCKED is correct only for the same-day goal. Incident date unknown. [Indexed original](https://detail.chiebukuro.yahoo.co.jp/qa/question_detail/q13316424698)
- 135: Actual failed registration supported; replying that the mystery is solved does not prove successful registration. Tourist status/planned visit is not explicit in retrieved question. [Original](https://detail.chiebukuro.yahoo.co.jp/qa/question_detail/q11302106301)
- 021: Wi-Fi recovered ticket access; final train boarding remains unconfirmed. IP restriction is an author inference, not independently verified cause. [Original](https://www.reddit.com/r/koreatravel/comments/1wo1rf3/korailcom_app_not_working/)
- 047: Retain exclusion from tourist denominator: remote shopping/video-app access from Japan rather than a stated Korea visit. [Original](https://detail.chiebukuro.yahoo.co.jp/qa/question_detail/q11323471496)
- 154–157: 2023 historical Thai trip, not 2026 entry-policy evidence. [Original](https://pantip.com/topic/42330614)
- 011: secondary_barrier contains a same-source annotation rather than a controlled barrier code; move that note to dedup metadata

## Remaining evidence gaps
15 unavailable: 017, 019, 052, 053, 056, 057, 059, 060, 061, 088, 128, 168, 222, 223, 224. No inferred text was supplied for these. Pantip 222/223 returned an unsafe/non-retryable redirect; no bypass was attempted.

Reddit exact calendar dates remain unconfirmed where only relative dates were exposed. Several comment permalinks were obtained from original-page links, but direct link fetches missed cache; their text was reviewed in the parent thread. PTT comments have author+timestamp locators but not stable individual URLs. Missing locators are listed per record.

## Deliverable
`independent_review.json` contains baseline coding, proposed goal/evidence/barrier/outcome/scope, field assessments, observed access tier, author, source/selected-comment locator, short verbatim anchor, exact dates where available, missing locators, and uncertainty flags. Suggested changes have not been applied to the baseline. Review decisions should be reconciled explicitly before promoting a v5 dataset.
