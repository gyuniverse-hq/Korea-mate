# v5 데이터 읽기와 판정 규칙

## 파일과 열
- cases_cumulative_v5.csv는 v4 원열을 보존하고 신규178행·v5_열을 더한 인계본이다
- 분석에는 v5_user_goal, v5_evidence_type, v5_reported_outcome, v5_outcome_normalized, v5_analysis_group을 사용한다. 구형 research_scope_status만 필터링하면 과거 보류 상태가 섞인다
- source_url은 원게시물, v5_access_url은 실제 접근 미러/아카이브가 있을 때 해당 주소, v5_locator는 게시물 안의 위치다. v5_transcript_url은 영상 전사의 접근 주소다
- v5_original_id와 v5_origin은 신규 수집묶음의 안정적 추적키다. case_id는 누적 ID다
- source_cluster_key/rows는 출처 군집을 나타낸다. 사건수와 인원수를 분리한다
- 빈 날짜는0이나 게시일이 아니다. UNKNOWN·approximate 등 원래 불확실성을 유지한다

## 사건 단위
한 사용자의 한 목표에 대한 시도·막힘·회복·결과를 한 사건으로 센다. 같은 예약을 여러 번 누른 것, 문제를 올리고 후속 댓글로 해결한 것, 동일 영상을 여러 번 설명한 것은 새 사건이 아니다. 같은 여행기의 별도 목표는 나눌 수 있으나 출처 군집을 보존한다. 일반적인 좋다/나쁘다 감상만으로 무리하게 별도 과업을 만들지 않는다.

## 근거와 결과
- FIRSTHAND/COMMENT_FIRSTHAND: 작성자 자신의 구체적 행동·관찰. 질문 문법이어도 실제 시도가 있으면 해당할 수 있다
- QUESTION_DEMAND: 아직 시도하지 않은 질문·우려. 유효한 수요 자료지만 실패 사례가 아니다
- SECONDHAND_CONTEXT: 다른 사람의 경험·전언
- SUCCEEDED: 명시한 목표가 완료됨
- WORKAROUND: 대체 경로·도움으로 명시한 목표 완료. 단순 제안은 해당하지 않음
- PARTIAL: 목표 일부만 달성 또는 구체적인 범위가 남음
- BLOCKED: 명시한 목표를 달성하지 못한 보고. 도덕적·기술적 원인 확정 아님
- UNKNOWN: 완료 결과가 없음. 조언, 로그인, 대기, 신고만으로 최종 구매·탑승·회수를 추론하지 않음

신규 원코드 FAILED→BLOCKED, PARTIAL_FAILURE→PARTIAL, UNRESOLVED→UNKNOWN, SUCCESS→SUCCEEDED를 v5_outcome_normalized에만 대응한다. SUCCEEDED_WITH_FRICTION은 명시적 목표 완료가 있을 때 SUCCEEDED로 정규화하고 불편은 case_kind/한계에 남긴다. 희망 스타일을 다르게 전달한 사례는 먼저 PARTIAL로 재판정했다. DISCOVERY는 새로운 실패원인으로 사용하지 않고 문화·서비스 발견의 긍정 관찰로 해석한다.

## 접근 강도
ORIGINAL_BODY_OR_AUTHOR_ARCHIVE는 도구가 원 URL이나 작성자 자신의 아카이브에서 반환한 본문·선택댓글이다. 실시간 UI·전체 댓글을 모두 보았다는 뜻은 아니다. INDEXED_OR_MIXED는 색인 텍스트 또는 이전 버전에서 원문/색인 구분이 혼합된 기록이다. PUBLIC_MIRROR는 별도 미러. PARTIAL_OR_PROVISIONAL은 짧은 발췌·검증되지 않은 전사, UNAVAILABLE은 이번 조회불가다.

직접경험 예비303건은 충분한 사건 문맥을 갖춘 자기보고를 포함한다. 게시물 전체 무결성, 저자 본인, 실제 거래, 현재 정책을 모두 검증한 집합이 아니다. SOURCE_CLAIM_SUPPORT와 현장 진실을 혼동하지 않는다.

## 보존·공유·재사용
원문 전문·댓글 원문을 대량 복제하지 않고 짧은 요약과 위치를 저장했다. 계정·여권·연락처·건강 세부정보 등 연구에 불필요한 개인 정보는 수집하지 않는다. 공개된 작성자의 경험을 제품의 고객 명단으로 쓰지 않는다. 원게시물 및 외부 데이터의 이용조건은 별도로 존중해야 하며 이 사례집이 원문 재배포 권한을 부여하지 않는다.

시장 규모·발생률·기능 순위는 비확률 표본의 행수로 산출하지 않는다. 공식 통계와 연결할 때 기간·모집단·문항 분모·측정단위를 확인한다. 정책 확인 시 사건 시점과 확인 시점을 각각 적는다.
