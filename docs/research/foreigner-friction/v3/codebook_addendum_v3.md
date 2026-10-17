# KoreaMate 코드북 보완 v3.0

기존 `codebook.md` 및 `codebook_addendum_v2.md` 보존. 추가 유형/QA 처리 규칙만 설명.

| 새로운 원인 코드 | 관찰 대상 | 기존 코드와 경계 |
|---|---|---|
| TRUST_AND_REVIEW | 리뷰·사진·홍보 내용과 실제 소비 만족의 괴리, 믿을 만한 장소 선택 과정 | CULTURE_DISCOVERY의 '새 경험 찾기'와 구분; 업계 전반의 리뷰 조작 확정 금지 |
| LOGISTICS | 짐 운반·보관·일행 구성·시설 가용성 | TRANSPORT는 탈 것·노선·예약, LOGISTICS는 동반 짐·현장 장비/보관 |
| ACCESSIBILITY | 지하철 계단, 이동 약자·큰 짐에 따른 물리 경로 | 특정 장애인 등급을 근거 없이 추정하지 않음 |
| PLAN_RECOVERY | 항공 지연/막차·폐관·날씨 취소 후 일정 복구 | OPERATING_INFO는 정보 부족, PLAN_RECOVERY는 실제 일정 변경·손실과 대안 재계획 |
| CONNECTIVITY | eSIM 로밍·지도·메시지 실제 연결 문제 | PREPARATION(상품 고르기) vs 현지 통신 서비스 불능 |
| CONSUMER_DISPUTE | 택시 요금·결제금액 상이·보증금 분쟁 | PAYMENT(기술적 거래 승인)과 다름. 위법성 단정 금지 |

## 업데이트된 판정 원칙

- `reported_outcome`은 **당사자가 완료했다고 명시한 과업의 최종 상태**. 다른 사이트를 검토한 사실은 `WORKAROUND` 성공으로 처리하지 않음.
- 화면에서 필요한 선택지를 **찾은 것**과 **최종 결제·발권을 마친 것**은 다름. 전자는 `PARTIAL`.
- `SECONDHAND`는 댓글 작성자가 다른 사람의 행동을 전하는 것, COMMENT_FIRSTHAND와 다름.
- 처음부터 관광 문제 범위가 아닌 온라인 구매·장기거주 문제는 `OUT_OF_SCOPE_ADJACENT`, 삭제하지 않고 분모에서 제외.
- 같은 글에서 작성자 다른 댓글 경험은 별도 사건 가능. 같은 작성자가 같은 원인으로 다른 앱을 비교한 건 목적 1개면 한 사건.
- 코로나 이전/오래된 글은 `HISTORICAL_ONLY`, 현행 관광 이용 정책에 재사용 금지.
- 원문 신뢰 상태와 현행 사업자 정책 검증은 서로 다른 축. `v3_source_recheck`는 **본문을 다시 봤다**는 기록에 불과.
