# Korea Mate 문서 인덱스

현재 최종 프로젝트 주제는 확정되지 않았으며, 이 저장소는 Korea Mate 후보의 검증 산출물을 관리하는 공간입니다. **주제 확정·기능 결정은 팀의 별도 검토가 필요합니다.**

| 영역 | 문서 | 상태 |
|---|---|---|
| 관광객 분석 | [2025 외래관광객조사 EDA](research/tourist-survey-2025/README.md) | 1·2차·중간검토·3차 연구 브랜치 PR |
| 분석 방법 | [원자료 분모·가중치·검증](research/tourist-survey-2025/methodology.md) | 연구 브랜치 |
| 개인화 추천 | [ADR-001](decisions/ADR-001-cold-start-recommendation.md) | 제안, 확정 아님 |
| 프로젝트 기획 | `project/` | 주제 결정 후 |
| 제품 기획 | `product/` | 사용자 문제 검증 후 |
| 시스템 설계 | `architecture/` | 기술 구상 단계 |
| 협업 | 별도 [협업 PR #2](https://github.com/gyuniverse-hq/Korea-mate/pull/2) | Draft |

## 작성 원칙

1. 관측된 결과, 해석, 제품 가설, 팀에서 최종 합의한 결정을 분리합니다.
2. 연구는 자료 출처, 기간, 모집단, 문항 분모, 가중치와 평가 방법을 기록합니다.
3. 원자료 및 응답자별 데이터를 커밋하지 않습니다.
4. 개인화 오프라인 예측 지표를 앱 사용자의 전환 향상으로 주장하지 않습니다.
5. PR은 기본적으로 작업 브랜치에서 `develop`으로 보내고, 통합 후 발표·배포할 때 `develop → main`을 검토합니다.
