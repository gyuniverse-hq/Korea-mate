# Korea Mate EDA 5 · 외부 관광·행사 데이터 검증

2026-10-16 기준 관광공사 TourAPI / 서울시 문화행사 API의 공식 필드와 이용 조건을 확인하고, 응답 정규화 및 품질 검증의 최소 기준을 구현했습니다. **실제 API 레코드 품질 검증은 인증키/네트워크 제약으로 미완료**입니다.

## 파일

- `EDA_v5_external_data_feasibility_2026-10-16.md`: 공식 출처, 가설 검증 경계, 연계 판단 및 후속 실험
- `event_contract.py`: 표준 필드 매핑, 날짜/좌표 검증, 품질 플래그
- `probe_open_apis.py`: 실제 키가 있을 때만 수행하는 선택적 라이브 조회; 키는 로그/보고서에 노출하지 않음
- `test_event_contract.py`: 합성 픽스처 기반 단위 테스트 **11건**
- `fixtures/seoul_synthetic.json`, `fixtures/tourapi_synthetic.json`: 모두 **실제 API 데이터가 아닌 가상 값**
- `live_probe_status.json`: 실제 서울 샘플 요청의 네트워크 실패 및 TourAPI 키 부재 상태
- `seoul_synthetic_quality.json`, `tourapi_synthetic_quality.json`: 합성 데이터에서만 계산한 QA 결과(실측으로 해석 금지)

## 실행

```bash
cd analysis/tourist-survey-2025/external-data
python -m unittest -v
python probe_open_apis.py --date 2026-10-16
# 서울시 공개 sample 키로만 HTTP 연결을 시험하는 경우(민감한 발급키 절대 사용하지 않음)
SEOUL_OPEN_API_KEY=sample python probe_open_apis.py --live --allow-http-seoul --date 2026-10-16
# TourAPI 키 사용(HTTPS)
TOURAPI_SERVICE_KEY=... python probe_open_apis.py --live --date 2026-10-16
```

## 안전한 해석

API에서 반환된 행사 기간 안에 있다는 것은 '운영 중', '예약 가능', '지금 입장 가능'이 아닙니다. 원본 상세 공지/예약 경로로 추가 확인해야 합니다. 서울시 API의 `LOT`은 경도, `LAT`은 위도입니다.

작업 브랜치는 `research/eda-2025-survey`, 기존 PR #1의 대상은 `develop`입니다. Korea Mate가 최종 프로젝트 주제로 확정됐다는 뜻은 아닙니다.