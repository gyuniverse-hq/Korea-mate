# Codebook Addendum v2.0 · 기존 20열 보존

기존 `codebook.md`는 수정하지 않음. 사건 전체는 기존 20개 열을 유지하고 신규 분석 메타데이터만 누적.

## 추가 장벽 코드

| 코드 | 정의 | 판정 경계 | 사례 |
|---|---|---|---|
| `EMERGENCY_RECOVERY` | 여권 분실·현지 돌발 상황 후 공식 긴급 복구 경로 접근 | 일반 교통/행정 준비와 분리. 특정 공관 절차는 국가별·시점별 | 신규 050, 052 |
| `TAX_REFUND` | 환급 eligibility·시내/공항 절차·증빙 및 처리상태 | 카드 승인 문제 PAYMENT와 분리 | 신규 063~065 |
| `CULTURAL_RULES` | 음식 제공·식당 규범·생활 관행의 사전 이해 부족 | 인지 부족/질문을 객관적 장애나 피해로 오인하지 않음 | 신규 071 |

## 신규 열

- `research_scope_status`: `IN_SCOPE`(관광 사건), `LEGACY_PENDING`, `SCOPE_REVIEW`(범위 재심사).
- `source_access_status`: `ORIGINAL_BODY_VISIBLE`(공개 본문/선택 댓글 확인), `PILOT_POST_OR_EXCERPT`, `SOURCE_BODY_SPOTCHECKED`. **접근 수준만 의미**.
- `verification_status`: `PRIMARY_SOURCE_TEXT_REVIEWED_NOT_CORROBORATED` 또는 `NOT_INDEPENDENTLY_ADJUDICATED`. **보고 사실을 재현했다는 뜻이 아님.**
- `verified_at`: 공개 원문 대조 실시일(사건 발생일이 아님).
- `user_type_evidence`: `TOURIST`(방문중/완료를 본문에서 명시), `PLANNING_VISIT`(예정 명시), `UNKNOWN`(추정 금지).
- `source_position`: post / comment / answer, 원천의 댓글과 게시글 구분.
- `current_policy_verified`: 공식 공급자 현행 정책 확인 여부, 현재 신규값 모두 `NO`.
- `incident_date`: 원문에서 정확한 발생일 확인한 경우만 입력.
- `dedup_relation`: 동일 글에서의 다른 사건 관계 표시, 같은 URL이라는 이유로 삭제하지 않음.

## 신규 상태/선택 댓글 기준

`SINGLE_REVIEW_V2`은 일인 공개원문 대조이며 DOUBLE_CODED가 아니다. `post_and_selected_comments`는 본문과 해당되는 일부 답변 확인, 전체 댓글 재독해를 주장하지 않는다. `COMMENT_FIRSTHAND`는 Reddit 댓글뿐 아니라 PTT 댓글/Yahoo 질의 답변 중 독립된 본인 경험에 적용. 원 글과 다른 사람의 성공을 원 글 작성자의 해결로 취급하면 오류.

## 오류 사례

- 앱 A·B·C가 모두 한 번의 배달 목표에서 막혔다는 단일 진술: 3사건으로 부풀리지 않음.
- 공항 출국장 밖 세금 환급기 사용을 '환급 실패 확정'으로 만들지 않음.
- 현장 식당이 두렵다는 경험: 식당이 실제 입장을 거절했다고 확정하지 않음.
- 사용자가 복수 경로를 통해 해결했으면 원 최초 실패와 최종 해결을 `WORKAROUND`로 기록.
- 비자/여권/고액 환급/의료 같은 영역에서 생성형 AI 추측을 사실과 동일시하지 않음.
