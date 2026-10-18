# 1330 관광안내 원본·정제·검증 자료

**KoreaMate 연구 브랜치 전용** · 자료 수집일 2026-10-18 · 데이터 출처: [한국관광 데이터랩 → 관광 VOC 현황 → 관광안내](https://datalab.visitkorea.or.kr/datalab/portal/bzm/getTursmCnsel.do)

## 저장 상태

| 자료 | 브랜치 저장 | 의미 |
|---|---|---|
| 2025·2026 관광안내 월별/유형별/언어별/지역별 요약 CSV 5개 | **완료**, `processed/summaries/` | 기존 v5.2 검증 파일의 Git blob을 재사용해 복사 |
| 원본 ZIP 식별·SHA256, 10개 원본 CSV 멤버 SHA/행 수 | **완료**, `source_manifest.json` | 다운로드 원천 출처와 재현성 추적 |
| 정제 재생성·검증 코드 | **완료**, `scripts/` | Python 표준 라이브러리, 로컬 정식 다운로드 ZIP 사용 |
| 월×어권×유형/월×지역×유형 정제 **전체** CSV | **코드로 생성 가능** | `processed/generated/`에 생성; 연구 브랜치 원격에는 아직 직접 저장하지 않음 |
| 원본 ZIP·원본 CSV | **공개 GitHub 보관 보류** | 해당 공식 다운로드 자료의 재배포 허락 조건 미확인, 팀 전용 별도 인계 ZIP에 원본 보관 |
| 종합 Excel | 기존 채팅 분석 산출물에 존재 | 공개 GitHub 원격 미저장 |

### 왜 원본 ZIP이 GitHub에 없나?

**공식 다운로드가 가능하다는 것과 공개 GitHub에서 재배포할 권한은 별개**다. 해당 1330 개별 다운로드 자료의 재배포 조건을 아직 확인하지 못했으므로 원본 ZIP 및 원형 CSV를 공개 브랜치에 게시하지 않았다. 원본 두 ZIP은 사용자에게 제공한 별도 데이터 묶음에 바이트 그대로 보존되어 있으며 정확한 SHA256을 남겼다. 정책은 [한국관광 데이터랩 약관](https://datalab.visitkorea.or.kr/datalab/portal/mbr/getMbrJoinForm.do)과 저작권 안내에서 확인할 것.

## 재현 방법

1. 공식 관광안내 화면에서 다음 조건으로 **전체 다운로드 → CSV**를 각각 실행한다.
   - 2025-01~2025-12
   - 2026-01~2026-09
2. 두 원본 ZIP을 `data/official/1330/raw/downloads/` 경로에 두고 `source_manifest.json`의 파일명과 SHA256을 확인한다.
3. 저장소 루트에서 실행한다.

```bash
python data/official/1330/scripts/build_processed.py
python data/official/1330/scripts/verify_processed.py
```

정제 결과는 `data/official/1330/processed/generated/`에 생성된다. v5.2 원본 보고서와 다른 코드가 아니다: `전체` 롤업을 제거하고, 반복되는 `기타` 월·어권·유형 키는 삭제하지 않고 합산하며, 지역명 `서울/서울특별시` 등의 차이를 대조한다. **2026년 의료관광 분류 미표시는 0건이 아니다.**

### 집계 결과 (실측 관광안내 접수 건수)

| 기간 | 총건수 | 수집 기간 |
|---|---:|---|
| 2025년 | 692,437 | 12개월 |
| 2026년 | 456,684 | 1~9월 |

`전체`를 세부 유형과 같이 SUM 하면 원본 상세 테이블이 2배로 집계된다. 1330 상담 건수는 고유 관광객 수/관광 불편 발생 건수가 아니며 한국어 상담도 포함한다. 2025 12개월과 2026 9개월 원시 합계를 증감률로 직접 비교하지 않는다.

## 기존 연구 연결

- [v5.2 공식 통계 심층 보고서](../../../docs/research/foreigner-friction/v5_2/official_cross_analysis_v5_2.md)
- [v5.3 사례·공식 통계 교차 분석](../../../docs/research/foreigner-friction/v5_3/research_findings_v5_3.md)
- [v5.4 주장 근거 신뢰성 검토](../../../docs/research/foreigner-friction/v5_4/audit_findings_v5_4.md)

**기획·디자인·P0·기존 407행에는 변경 없음.**
