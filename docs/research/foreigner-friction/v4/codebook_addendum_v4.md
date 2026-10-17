# KoreaMate v4.0 · 분류·원문 확인 보완 코드북
기존 v1/v2/v3 코드북은 수정하지 않으며 본 Addendum은 신규 관측 범주와 1인 원문 대조 방법만 추가.
| 코드 | 정의 | 주의 |
|---|---|---|
| SERVICE_SUPPORT | 카드·예약·통신 등 문제가 생겼을 때 고객센터/직원에게서 도움받지 못하는 과업 단계 | 실제 고객지원 실패인지 작성자의 기대 차이인지 원문에 따름 |
| ACCOMMODATION | 숙소 입실·출입·객실 설비 등의 실제 이용 문제 | 사용자 체감 안전 걱정으로 객관적 범죄를 주장하지 않음 |
| TRUST_AND_REVIEW | 높은 리뷰·추천 점수와 관광객의 실제 방문 만족 차이 | 후기 조작을 객관적 사실로 단정하지 않음 |
| CURRENCY_OR_TICKET_PROCESSES | 관광객 관점에서 구별하기 어려운 결제/인증/예약/환급 단계는 기존 PAYMENT/IDENTITY/BOOKING/TAX_REFUND에 관측 직접 중단 기준으로 코딩 | 현행 규정은 공급자 확인 필요 |
## 사건 결과 판정
- FAILED/BLOCKED = 작성자의 과업이 실제 중단. QUESTION+CONCERN은 문제를 걱정하는 상태, 결과 UNKNOWN.
- WORKAROUND = 당사자가 다른 경로로 **해당 중단 단계**를 돌파한 경우. 최종 입장/탑승을 별도로 확인하지 않았다면 요약에 그 한계를 정확히 기록.
- POSITIVE/SUCCEEDED = 이미 해결된 경험/유용한 기존 서비스를 같은 분류 단계에서 기록.
- USER_TYPE `TOURIST`=`방문 중/관광 후임을 직접 진술`; `PLANNING_VISIT`=`방문 계획을 직접 진술`; `UNKNOWN`=`근거 없으면 추정하지 않음`.
- 댓글 위치와 게시글을 구별하며 서로 다른 댓글 작성자의 같은 종류 사건은 source_id 공유/다른 case_id; 같은 작성자의 연속 메시지는 한 사건의 후속으로 정정.
## 원문 검증 상태
- `PUBLIC_PAGE_FULL_BODY` : 실제 공개 본문 및 선택 댓글 열람
- `INDEXED_POST_COMMENTS` : 검색 서비스에서 공개된 해당 게시글 본문 및 관련 댓글의 표시 범위
- `INDEXED_ORIGINAL_BODY`: PTT/Yahoo/Pantip 원문 검색 색인 텍스트, 전체 본문/댓글 접근 보장 아님
- `MIRROR_FULL_COMMENTS`: 원본 게시물을 보존한 공개 미러의 본문 및 관련 댓글 (원문과 미러 동등성 주의)
- 이 단계는 `SECOND_CODER_VERIFIED`, `CURRENT_PROVIDER_POLICY_CHECKED`, `LIVE_TASK_VALIDATED`를 뜻하지 않음.
## 시간·중복
- 원문 게시일과 여행 당시 발생일을 별개로 보관. 댓글 작성일 불확실한 경우 원문 게시일만 `post_date`로 기록, 시계열 분석에서 제외 가능.
- 신규 2024년 자료는 `HISTORICAL_ONLY`; 2025–26 원문도 정책이 갱신되면 최신 사실로 재해석 불가.
