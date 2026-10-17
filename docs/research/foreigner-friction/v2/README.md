# KoreaMate · 방한 외국인 불편 기반 데이터 구축 v2.0

**기준 2026-10-18 / 증언 원문 대조 연구 패키지.** 기존 47건은 별도 원본으로 보존. 연구 대상은 여행자 과업과 미해결 요구이며, UI·P0를 확정하지 않음.

## 수집 현황

- 기존 47건 = 형식 검사·1인 기존 코딩, **전건 원문 독립 재검수 미완료**.
- 새 27건 = 출처 20개, 공개 게시글/해당 댓글 원문 대조·한국어 사건 코딩. **발생 사실의 독립 확인/현행 정책 검증/2차 코더 검증을 마친 건수는 0**.
- 누적 **74건 / 고유 UGC 원문 66개**. 새 증거 언어 en 14 / zh-Hant 7 / ja 6.
- 300/500 목표 미완료. 영상 본문 확인 0, 추가 언어 검증 0.

## 전체순서 / 현재순서

| 번호 | 작업 | 지금 상태 | 단계 완료 기준 |
|---|---|---|---|
| 1 | 기존 47건 품질 검사 | **진행 중** | 독립원문확인·이견표 및 관광 범위 판정 완료 |
| 2 | 공식 자료 4종 | **부분 진행** | 4종 모두 조사 시점·분모·제외유형 확인 |
| 3 | 다국어 커뮤니티·유튜브 | **진행 중** | 300건(선택 확대 500건) 검증 가능한 사건, 다언어 균형 확인 |
| 4 | 정제·중복·코딩 품질 | **부분 진행** | 중복·분모·다중코더 합의표 통과 |
| 5 | 불편 유형 분석 | **대기** | 여정×원인×영향×해결 비교표 + 불확실성 |
| 6 | 공식/정성 교차 검토 | **대기** | 모수·측정단위 구별해 자료 교차검토 |
| 7 | 문제·기회 지도 | **초안** | 공식 연결 가능/추천/실측 검증 분리 |
| 8 | 연구 보고·GitHub 인계 | **진행 중** | 재현검증과 PR 검토, 팀 합의 없이 P0 변경 금지 |

**현재 순서: 1 기존 47건 독립 품질 재검수 + 3 신규 사건 확대 수집 병행.** 단계 2는 메타데이터 확인만 일부 진행.

## 파일 및 사용법

1. [cases_cumulative_v2.csv](cases_cumulative_v2.csv): 원본 47행을 그대로 유지하고 신규 행 추가. 엑셀 편집 시 UTF-8 BOM 적용.
2. [new_cases_2026-10-18.csv](new_cases_2026-10-18.csv): 신규 공개원문 대조 결과만 별도 추출.
3. [legacy_quality_audit_2026-10-18.csv](legacy_quality_audit_2026-10-18.csv): 기존 전건에 대한 구조/범위/추가 검토 플래그. 완료 재코딩 아님.
4. [source_register_additions_v2.csv](source_register_additions_v2.csv): 신규 원문 등록부.
5. [source_register_cumulative_v2.csv](source_register_cumulative_v2.csv): 기존 소스+신규 소스 일괄 등록.
6. [research_protocol_v2.md](research_protocol_v2.md): 새 질문·검색 전략·표본 편향·검증 수준.
7. [codebook_addendum_v2.md](codebook_addendum_v2.md): 기존 코드북의 판정 규칙 추가.
8. [quality_report_v2.md](quality_report_v2.md): 스키마/중복/관측 분모/재검수 대기.
9. [official_source_review_v2.md](official_source_review_v2.md): 공식 4종의 측정 단위와 추가 분석 질문.
10. [problem_opportunity_map_v2.md](problem_opportunity_map_v2.md): 관측→미해결 상태→가능 지원→외부 검증. 최종 기능 확정 금지.

## 이후 진행과 안전장치

- `docs/research/foreigner-friction/pilot_cases.csv`, `source_register.csv`, `codebook.md` 등 v1 파일은 **수정/삭제하지 않음**.
- `main`, `develop`, `docs/koreamate-experience-redesign` 및 2025 EDA 브랜치 수정하지 않음.
- `FIRSTHAND`는 게시자 자기진술이며 거짓 여부나 서비스 규정이 검증됐다는 보장은 아님. 원문의 '질문'을 실제 실패로 바꾸지 않음.
- 장기간 거주자·학생 사례는 별도 모집단으로 보류. 영상을 검토하지 않았으면 사건에 넣지 않음.
- 다음 차례는 기존 47건 2인 원문 검수 후 *문제 발견·현장 실행·복구·성공 사례*를 중심으로 다양한 언어의 사건 추가 확보.

[원래 기획](https://app.notion.com/p/3fae94b44d078180a459c5ed57b97aed) · [기존 EDA](https://github.com/gyuniverse-hq/Korea-mate/tree/research/eda-2025-survey) · [공식 4종 자료](official_source_review_v2.md)
