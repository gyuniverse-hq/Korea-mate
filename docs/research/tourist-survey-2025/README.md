# Korea Mate · 2025 외래관광객조사 연구

**상태: 최종 프로젝트 주제 미확정 / Korea Mate 후보 검증 중**

이 디렉터리는 2025년 외래관광객조사 원자료 기반 탐색적 데이터 분석(EDA) 결과를 관리합니다. 분석은 **원자료 → 관측 → 가설 → 추가 검증 → 제품 판단**으로 이어지며 주제·기능을 확정하지 않습니다.

## 단계별 보고서

| 단계 | 문서 | 핵심 내용 |
|---|---|---|
| EDA 1차 | [eda-v1.md](eda-v1.md) | WHO·WHAT·HOW·FRICTION, 사전 고려와 실제 참여 비교 |
| EDA 2차 | [eda-v2.md](eda-v2.md) | 활동 연관성, 탐색적 군집, 인기순 대비 개인화 ML |
| 중간검토 | [eda-midreview-2026-10-15.md](eda-midreview-2026-10-15.md) | 근거 수준·입력정보 최소화·모델 강건성 |
| EDA 3차 | [eda-v3.md](eda-v3.md) | 방문경험별 통제분석, 정보 부족 유형·만족도 |
| **EDA 4차** | **[eda-v4-qa-when-where.md](eda-v4-qa-when-where.md)** | **기존 지표 재현 검사, 월별·지역별·국적별 방문 차이** |
| 공통 기준 | [methodology.md](methodology.md) | 분모·가중치·한계와 데이터 재현성 |
| 다음 단계 | [next-steps.md](next-steps.md) | 분석 확장·직접 사용자 과제·팀 의사결정 |

## EDA 4차에서 추가 확인

- 응답자 16,110명, 408개 변수, 유효 가중치, 중복 ID 없음, 월·분기·지역 선택 코드 유효
- EDA 1~3 대표 지표 일치 / EDA v2 전체 결과 JSON, EDA v3 통제분석 JSON **원자료 재실행 결과 일치**
- EDA v3 로지스틱 회귀 효과 추정치 동일(최적화 반복 횟수 메타데이터 2건만 상이)
- 여가·친지 방문 집단 12,339명에서 서울 방문 78.49%, 부산 17.22%, 제주 11.13%; 2개 지역 이상 방문 26.22%
- **조사 월별 차이는 1개 연도 관찰이므로 실시간 트렌드로 해석하지 않음**
- **Q9 방문 지역과 Q8 관광활동은 활동이 발생한 정확한 장소로 연결되지 않음**

## 자료 위치와 공유 범위

- [분석 Python 및 재현 안내](../../../analysis/tourist-survey-2025/README.md)
- [비식별 집계 CSV/JSON](../../../analysis/tourist-survey-2025/outputs/)
- [GitHub 열람용 시각화 WebP 12개](figures/)
- [개인화 추천 도입 ADR 초안](../../decisions/ADR-001-cold-start-recommendation.md)

**원자료 ZIP·XLSX, 코드북 원본 및 응답자 행별 CSV는 GitHub에 포함하지 않았습니다.** 본 분석의 PDF·결과 엑셀은 별도 공유 파일로 전달하며, 서비스 효과·최종 주제를 입증했다고 주장하지 않습니다.

**출처:** [2025년 외래관광객조사 원자료 안내](https://touraz.kr/statistics?bbsSeq=310809_1127&boardMode=V).
