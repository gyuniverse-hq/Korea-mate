# KoreaMate · UX/서비스 경험 재설계
> 개인 기획·디자인 초안 · **팀 합의 전** · 2026-10-18

## 이번 재정비 전체 순서와 현재 위치

> **현재: 01 핵심 경험 P0 기준 초안 작성 완료 → 다음: 02 메인 정보 구조** · 2026-10-18 KST  
> [핵심 경험 P0 기준과 재정비 실행 순서](./core-experience-p0-v1.0.md)

| 순서 | 이번 작업 | 상태 |
|---|---|---|
| **01** | **KoreaMate 핵심 경험 P0 기준** | **초안 작성 완료 / 팀 합의 전** |
| **02** | **메인 정보 구조(IA)** | **다음 실행** |
| 03 | PC·모바일 화면 초안 | 대기 |
| 04 | 시각 시안 | 대기 |
| 05 | 체험형 HTML | 대기 |
| 06 | 사용자 흐름과 기술 검증 | 대기 |

기존 v0.9 시안·HTML과 아래의 01~08단계 이력을 바탕으로 진행하는 재정비다. 원안의 다섯 핵심 경험을 중심에 두고, 전문 아이템은 사용자가 있는 상태를 가정한 인기 결과와 독립 진입으로 연결한다.

## 기존 v0.9 화면과 디자인 평가 패키지 v1.0

> **기존 화면·평가 자료:** [UI/UX 디자인 평가 패키지 README](./evaluation/README.md)에서 현재 HTML 상태와 알려진 문제를 확인한다.  
> **이번 재정비의 제품 우선순위:** 위의 [핵심 경험 P0 기준](./core-experience-p0-v1.0.md)을 우선 적용한다.  
> **최신 메인 화면:** v0.9 고충실도 참조 시안 + 브라우저 HTML 비교. 팀 확정 전이며 과거 v0.7/v0.8은 디자인 탐색 기록.

- [브랜드·화면 평가 시작하기](./evaluation/README.md)
- [메인 화면설계 명세 HOME-001](./evaluation/02-home-screen-spec.md)
- [시각적 차이와 알려진 문제](./evaluation/03-visual-audit.md)
- [평가 기준표](./evaluation/04-evaluation-rubric.md)
- [외부 AI용 복사용 평가 요청문](./evaluation/05-reviewer-request.md)
- [v0.9 디자인 시안과 실제 HTML 이미지 비교](./assets/v0.9/target-vs-html-v0.9.webp)
- [v0.9 단일 HTML](./previews/d-main-hifi-v0.9.html)

## 목표
KoreaMate의 원래 핵심(See it → Live it / Scan Anything / Korea Pulse / For You / Korea 101 / Help Me Now / Plan B)을 지키면서, 팀원의 Kravel·K-Season·K-Beauty·K-Class·GG Korea 등 아이디어가 **고유한 경험을 가진 전문 서비스**로 살아 있도록 설계한다. '많은 카드가 한 화면에 있다'와 '여러 기능이 협력해 결과가 나아진다'는 다르다.

## 전체 작업 순서
| 단계 | 목표 | 현재 |
|---|---|---|
| 01 출처·원안 대조 | Notion 원안 및 Discord 아이디어 검토 | 완료 |
| 02 서비스 경험 구조 | 공통 경험/전문 경험/별도 사용자군 구분 | 초안 |
| 03 대표 경험 | 각 기능의 대표 조작·결과·독립성 | 초안 |
| 04 정보 구조(IA) | 메인과 전문 화면, 현장 도움, 일정 흐름 | 초안 |
| 05 디자인 방향·시스템 | A/B/C 화면 구조와 D 통합안 + 4브랜드 시각 탐색 | **초안 검토 중** |
| 06 고충실도 시안 | 메인/Scan/Kravel/K-Season/Beauty | **메인 v0.9 제작 · 다른 전문 화면 미착수** |
| 07 체험형 HTML | 시안 준수 인터랙티브 프로토타입 | **메인 v0.9 시연 · 다른 전문 화면 미착수** |
| 08 사용자·기술 검증 | 증분 가치/정보 근거/오류 복구 검증 | 대기 |

02~04는 팀 확정본이 아니라 **검토 가능한 기준 초안**이다.

## 문서
- [v0.8: D안 + 브랜드 시각 정체성 4종 비교](./brand-direction-study-v0.8.md)
- [v0.8: 네 가지 테마 전환형 메인 HTML](./previews/d-home-four-styles-v0.8.html)

- [v0.5: 서비스 경험·대표 체험·IA](./service-experience-v0.5.md)
- [편집 가능한 경험 구조도](./experience-map.md)
- [v0.7: 메인 세 가지 방향 비교 및 평가](./home-options-v0.7.md)
- [A/B/C 체험형 비교 HTML](./previews/main-options-v0.7.html)
- [이전 융합 시나리오 평가 v0.3](./archive/fusion-scenarios-v0.3.md)
- [이전 인터랙티브 데모 검토 v0.4](./archive/prototype-review-v0.4.md)
- [개인 원안 v0.2 (Notion)](https://app.notion.com/p/3fae94b44d078180a459c5ed57b97aed)
- [Discord 브레인스토밍](https://discord.com/channels/1557589116303056927/1560468600186470510)

## 협업·버전 관리
- 개발 코드와 main/develop은 이 브랜치에서 수정하지 않는다.
- 산출물은 문서 초안 → 이미지 검토 → 화면 구현 → 검증 순으로 단계별 commit한다.
- 기능을 제외·확정하거나 담당자를 배정하는 결정은 **팀 리뷰 및 별도 의사결정 기록**을 거친다.
- 실시간 행사·지도·예약·AR/AI 성능을 모의 화면으로 실제 구현한 것처럼 주장하지 않는다.
- GitHub에는 설계 자료만 저장하며 원자료, 개인정보, 토큰은 저장하지 않는다.
