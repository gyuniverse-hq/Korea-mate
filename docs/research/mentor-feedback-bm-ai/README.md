# KoreaMate 멘토 피드백 대응 연구 패키지 v0.1

- 작성: 2026-10-18
- 상태: **검토용 초안 / 팀 합의 전 / 실증 결과 아님**
- 범위: 사업모델(BM), 경쟁 서비스, AI 기술 역할, 후속 효과 평가
- 원안: 한국을 몰라도 한국 문화를 발견하고 실제로 경험하게 돕는 KoreaMate. 기존 다섯 핵심 경험(Korea Pulse / For You+New to You / Korea 101 / See it→Live it / Scan Anything)을 없애거나 Scan으로 통합하는 제안이 아니다.

## 읽는 순서

1. [경쟁·시장·BM](./01-competitive-market-bm-v0.1.md): 직접 경쟁사 5개, 별도 비교기업 1개, 공개 매출과 적용 범위, 기존 파이/신규 파이, 수익 실험
2. [AI 역할·데이터 전략](./02-ai-data-coldstart-v0.1.md): 기존 EDA 활용, 서비스별 AI 기능, 콜드스타트, 데이터 수집/학습 구분, 논문
3. [실험·평가·작업 순서](./03-validation-experiments-v0.1.md): 기존 서비스 대비 검증 설계, 서비스 전후 데이터, 운영 로그, 단계별 완료 조건
4. [사용자 과제 초안](./04-task-bank-v0.1.csv): 사용자 시연과 모델 평가를 위한 시나리오 목록. **실제 관찰 기록이나 정답 데이터가 아니다.**

## 우선 판단

- **확인된 사실:** KoreaMate의 2025 외래관광객조사 기반 활동 추천은 인기순 대비 오프라인 점수가 개선되었다. 다만 실제 콘텐츠 클릭·예약·방문 향상은 미검증이다.
- **경쟁 환경:** Creatrip Buddy, Trazy K-pop Concierge, Trip.com TripGenie 등은 여행 지원·예약 장벽·AI 여행 안내를 이미 제공한다. '여행 도우미'라는 기능 자체는 독점적 차별점이 아니다.
- **검증 가설:** 여러 서비스에서 흩어진 정보를 *한국 문화 특화 맥락*에서 연결하고, 운영·자격·동선 등의 제약을 근거로 점검하며, 실패 시 실행 가능한 대안을 제공하면 과제 성공률을 높일 수 있다.
- **BM:** 예약 제휴·파트너 서비스·구독·전문 서비스·집계 인사이트 등 여러 후보를 열어두되, 누가 지불하며 실제 전환이 가능한지 분리 검증한다.
- **주의:** 연합학습/분할학습은 콜드스타트의 필수 해법이 아니다. 별도의 데이터 분산·협력 요구가 확인된 뒤 도입 여부를 판단한다.

## 원래 작업과의 관계

- 기획 기준: [핵심 경험 P0](../../product/experience-redesign/core-experience-p0-v1.0.md) — 원문은 docs/koreamate-experience-redesign 브랜치에 있음. 이 브랜치에는 해당 문서가 없을 수 있으므로 아래 참조 링크 우선.
- 원안: https://github.com/gyuniverse-hq/Korea-mate/blob/docs/koreamate-experience-redesign/docs/product/experience-redesign/core-experience-p0-v1.0.md
- EDA: https://github.com/gyuniverse-hq/Korea-mate/blob/research/eda-2025-survey/docs/research/tourist-survey-2025/eda-midreview-2026-10-15.md
- 외국인 불편 조사: research/foreigner-friction-discovery 및 별도 진행 중인 심층 조사. **여기서 조사 사례 건수를 새로 확정하지 않으며 기존 연구 브랜치를 수정하지 않는다.**

## 상태 및 다음 결정

- [x] 기획·EDA 전제 확인
- [x] 경쟁 서비스/공개 재무 1차 수집
- [x] BM 후보·AI 파이프라인·검증 설계 초안
- [ ] 동일 과제로 경쟁 서비스 직접 사용 비교(사실확인 및 기능 검증)
- [ ] 실제 외국인 불편 사례 분류 결과 병합
- [ ] 사용자 인터뷰/사용성 과제 수행
- [ ] 1개 이상 AI 흐름 구현 후 정량·정성 비교
- [ ] BM 파트너·수익 조건 확인 및 단위경제성 재계산

이 문서의 제안·목표치는 **제품 가설과 임시 평가 기준**이며 실현된 성과가 아니다.
