# 2025 외래관광객조사 분석 코드 및 비식별 집계

[전체 EDA 문서 인덱스](../../docs/research/tourist-survey-2025/README.md)

## 구성

- `scripts/analyze_koreamate_v2.py`: 활동 연관성·군집·인기순 대비 추천 ML
- `scripts/koreamate_midreview_*.py`: 중간검토, 강건성/모델 비교
- `scripts/koreamate_eda_v3_controls.py`: 국적·연령 등을 통제한 행동·정보 부족 분석
- `scripts/koreamate_v3_logit_sensitivity.py`: 로지스틱 민감도 검산
- `scripts/koreamate_step9_10_audit.py`: **EDA v4 원자료 구조/가중치 검증 및 월·지역 집계 생성**
- `scripts/create_eda_charts.py`: **EDA v4 지역·월별 차트 생성**
- `outputs/*.csv`, `outputs/*.json`: 응답자별 기록 없는 **집계** 결과
- `requirements.txt`: 기존 v2/v3 패키지 범위(정확한 잠금 파일 아님)

## 기본 실행

공식 원자료를 별도로 확보하고 408개 변수 헤더의 `2025_eda_raw.csv`를 로컬에서 준비합니다. 절대로 GitHub에 업로드하지 않습니다.

```bash
python -m venv .venv
# 운영체제에 맞게 가상환경 활성화
python -m pip install -r analysis/tourist-survey-2025/requirements.txt

# 아래 기존 스크립트는 scripts 폴더에 원자료가 있다고 가정
cd analysis/tourist-survey-2025/scripts
python analyze_koreamate_v2.py
python koreamate_eda_v3_controls.py
python koreamate_v3_logit_sensitivity.py
```

## EDA v4 추가 실행

EDA v4는 `--input`으로 원자료를 외부 경로에서 읽도록 만들었습니다. **실행할 때는 저장소 루트 기준**입니다.

```bash
python analysis/tourist-survey-2025/scripts/koreamate_step9_10_audit.py \
  --input /PRIVATE/2025_eda_raw.csv \
  --out analysis/tourist-survey-2025/outputs
```

시각화 생성기는 보고서 공유 폴더 기준으로 작성되었으므로, 저장소에서는 생성기 내부의 `ROOT/OUT/FIG` 경로를 실제 출력 폴더에 맞게 조정해야 합니다. 현재 GitHub에 있는 WebP 4장은 **검증된 생성 차트의 압축본**입니다.

## 재현 검증 상태 (2026-10-16)

- EDA v2 추천·군집 전체 집계 JSON: **원자료 재실행 및 정확한 수치 일치**
- EDA v3 통제분석 집계 JSON: **정확한 수치 일치**
- EDA v3 로지스틱 효과 추정치: **일치**(최적화 반복 횟수 2개는 다름)
- EDA v4 16,110명·408개 변수, 중복·가중치·월/분기·코드 및 과거 대표 지표 대조: **통과**
- 복합표본 공식 표준오차 계산/외부 데이터 API 실호출·계절성 장기 검증: **미진행**

## 데이터 해석과 공유 제한

- 원자료 ZIP, 코드북 XLSX, 개별 설문 CSV 및 개인 식별값은 공개하지 않습니다.
- `Q9_2a01~17`은 지역 복수응답이며 `D_MON`은 조사 월입니다.
- 관광 활동(`Q8`)을 방문지역(`Q9`)에서 했다고 해석하지 않습니다.
- 국적×지역, 월×지역 집계는 방문 응답 수 **30명 미만**인 셀을 가립니다.
- 개인화 NDCG@3은 **과거 실제 참여 활동 예측의 오프라인 지표**입니다.
