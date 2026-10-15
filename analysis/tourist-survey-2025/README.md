# 2025 외래관광객조사 분석 코드 및 비식별 집계

관련 연구 결과는 [EDA 문서 인덱스](../../docs/research/tourist-survey-2025/README.md)에서 확인할 수 있습니다.

## 등록된 파일

- `scripts/analyze_koreamate_v2.py`: 가중 활동 연관성, 군집, 시점 분리 추천 모델 평가
- `scripts/koreamate_midreview_*.py`: 중간검토 집계, 강건성, 온보딩 입력 축소·모델 비교
- `scripts/koreamate_eda_v3_controls.py`: 국적·연령 등을 통제한 방문횟수별 활동 및 정보 부족 비교
- `scripts/koreamate_v3_logit_sensitivity.py`: 로지스틱 회귀 민감도 검산
- `scripts/koreamate_eda_v3_figures.py`: v3 집계 그래프 생성
- `outputs/*.csv` / `outputs/*.json`: 응답자 단위 기록을 제외한 집계 결과

분석 그래프 WebP 8개는 [연구 이미지 폴더](../../docs/research/tourist-survey-2025/figures/)에 있습니다. 원본 PDF·엑셀(XLSX)은 별도 공유패키지로 관리하며, **GitHub에는 업로드하지 않았습니다.**

## 실행 안내

1. 공식 2025년 외래관광객조사 원자료·코드북을 합법적으로 확보합니다.
2. 사용자 보유 원자료를 기존 408개 변수 구조의 `2025_eda_raw.csv`로 준비합니다.
3. `scripts/2025_eda_raw.csv` 경로에 **로컬에서만** 둡니다. 이 파일은 `.gitignore`에 의해 제외됩니다.
4. 가상환경에서 의존성을 설치합니다.

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r analysis/tourist-survey-2025/requirements.txt

cd analysis/tourist-survey-2025/scripts
python analyze_koreamate_v2.py
python koreamate_eda_v3_controls.py
python koreamate_v3_logit_sensitivity.py
python koreamate_eda_v3_figures.py
```

일부 중간검토 스크립트는 별도 실험용이며 `analyze_koreamate_v2.py`의 함수 또는 생성물을 참조합니다. 코드는 **각 스크립트가 놓인 폴더를 기준으로 입력 CSV 및 출력 파일을 찾는 방식**으로 작성되었습니다. 실행 결과는 기본적으로 `scripts/`에 생성되며, 검토 후 `outputs/`의 집계 결과와 비교합니다. 원자료 없는 환경에서는 전체 ML 학습을 다시 실행할 수 없습니다.

## 검증 상태

- 2026-10-16 기준: 제공 원자료를 로컬에서 연결해 `koreamate_eda_v3_controls.py` 재실행 성공. 재생성한 v3 집계 JSON은 기존 v3 집계 JSON과 **값 전체가 일치**했습니다.
- `koreamate_v3_logit_sensitivity.py` 재실행 성공.
- 나머지 전체 EDA·추천 학습 스크립트의 신규 환경 재현 및 정확한 의존성 잠금은 **아직 미검증**입니다.
- 통계량은 설문 가중치를 반영했으나, 공식 복합표본 신뢰구간은 아닙니다. 오프라인 예측 결과는 실제 앱 전환효과가 아닙니다.

## 공유 및 재배포 원칙

응답자별 원자료와 개별 식별자는 저장소에 올리지 않습니다. 공유된 CSV/JSON은 집계값입니다. 미식별 집계라도 원자료 사용·재배포 조건은 출처 정책을 확인해야 합니다.
