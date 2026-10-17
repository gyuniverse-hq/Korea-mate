# KoreaMate 외국인 관광객 불편 탐색 v4.0
**조사일 2026-10-18(KST)** · 기존 v1~v3.1 파일 보존 · 팀 확정 기능/디자인 변경 없음
## 전체순서 / 현재순서
| 순서 | 내용 | 상태 | 완료 기준 |
|---|---|---|---|
| 1 | 기존 74건 신뢰성 재판정 | **60/74 원문·검색 본문 재확인**, 14건 대기 | 74건 원문/댓글 확인과 제2코더 20%+ 검수 |
| 2 | 공식 자료 4종 재분석 | 일부 문서 검토 | 정확한 분모·갱신주기와 추가 집계 |
| 3 | 다국어 UGC·YouTube 수집 | **229/300건** | 직접 원문 근거와 중복 판정·영상 원문 확인 |
| 4 | 중복·코딩 품질 관리 | 구조 QA 통과, 독립 코딩 미완료 | ID/원천/중복/이견 검증 |
| 5 | 여정별 탐색 분석 | 문제별 초안 | 단계·원인·결과·반례 교차 |
| 6 | 공식 통계 교차 | 준비 | 조사 모집단 구분 및 대조 |
| 7 | 문제·기회 지도 | 초안 | 가능한 지원/추천/실증 구분 |
| 8 | 보고·인계 | 버전 v4 커밋 | 팀 검토 후 PR |
## 누적 결과
- 이전 157건 + **신규 72건** = 229개 사건, **고유 UGC 출처 URL 163개**.
- 신규 원문 URL 45개, 원천 등록부 전체 172행(공식+영상 후보 포함).
- 신규 언어: {"en":44,"zh-Hant":11,"ja":14,"th":3}. 사건 성격: {"FRICTION":24,"MIXED":11,"POSITIVE":13,"CONCERN":24}.
- **원문/검색 본문과 일인 코딩을 대조한 기록**이며 독립 작성자 본인확인, 법규·현행 서비스 정책, 실제 사용과업 재현, 두 번째 코더 검증 완료 **0건**.
- 대조·질문·성공을 함께 수집해 검색 키워드 편향을 보완하지만 비확률 표본의 시장 발생률/우선순위 해석은 금지.
## 파일
- [cases_cumulative_v4.csv](cases_cumulative_v4.csv) — 전체 229건, 버전별 QA 추가 열.
- [new_cases_batch4.csv](new_cases_batch4.csv) — 이번 실행 신규 72건만.
- [legacy_74_recheck_v4.csv](legacy_74_recheck_v4.csv) — 기존 74건의 출처 상태/결과 보정.
- [source_register_cumulative_v4.csv](source_register_cumulative_v4.csv) — 기존 출처 + 신규 원천.
- [source_register_additions_v4.csv](source_register_additions_v4.csv) — 신규 URL 45개만.
- [quality_report_v4.md](quality_report_v4.md) — 수집 분모, 실패/성공, URL 검증상태, 재판정 결과.
- [research_findings_v4.md](research_findings_v4.md) — 문제 → 관찰 → 반례 → 제품 가설 초안.
- [candidate_exclusions_v4.csv](candidate_exclusions_v4.csv) — 제외 사유/편향 방지.
- [codebook_addendum_v4.md](codebook_addendum_v4.md) — 추가 원인코드와 단계별 판정.
- [collection_search_log_v4.csv](collection_search_log_v4.csv) — 실제 검색어·언어·접근 방식.
## 다음 실행
- 미확인 레거시 14건 재조회(접근 제한은 그대로 보고) → 무작위·다언어 2차 독립 검수 계획
- Reddit 중심에서 PTT/일본/태국/베트남어 및 실제 영상(전사·댓글 접근 가능한 것만) 확대
- 같은 목표에 대해 실패한 사람과 성공한 사람의 **조건 차이**(로그인 방식/네트워크/지역/날짜) 비교
- 71건을 더 확보해야 1차 정량 수집 목표. 다만 건수보다 정확한 사건 정의와 출처 품질이 우선.
