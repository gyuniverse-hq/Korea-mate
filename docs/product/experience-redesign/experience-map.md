# KoreaMate 서비스 경험 구조도 v0.5

```mermaid
flowchart TB
    Traveler["사용자 · 문화 탐색 / 여행 준비 / 현장 도움"]
    Traveler --> Discover["Discover: For You · Korea Pulse · Korea 101 · New to You"]
    Traveler --> Entry["Ask · Scan · Share"]
    Traveler --> Direct["전문 체험 직접 진입"]
    Discover --> Mate["KoreaMate: 개인화 · 맥락 공유 · Help Me Now · Plan B"]
    Entry --> Mate
    Direct --> Studios

    subgraph Studios["전문 경험: 각각의 독립적 대표 화면"]
        KRV["Kravel · 작품→촬영지 코스"]
        KSE["K-Season · 기간·행사·캘린더"]
        KBE["K-Beauty · AR 룩·제품"]
        KCL["K-Class · 영상·한국어"]
        GGF["GG Korea Fan · 경기·팬 경험"]
        FOO["Food/History/Lifestyle · 문화·체험"]
    end
    Mate --> Studios
    KRV <-->|"일정 충돌 확인·재계획"| KSE
    GGF <-->|"경기·행사 조건"| KSE
    Studios --> Plan["My Korea · 명시적 저장·일정·기억"]

    Other["별도 전문 목표: Tutor / Pro Path / B2B Food Market / 의료·웰니스"]
    Other -.->|"선택적 연계 · 독립성 유지"| Mate
```

## 판정 기준
- 직접 진입: KoreaMate Scan을 거치지 않고 Kravel·Beauty 등으로 바로 들어갈 수 있다.
- 융합: 링크를 연결한 수준이 아니라 **여행 일정·의사결정 등 사용자 결과가 실제로 개선**된다.
- 디자인: 각 전문 기능의 화면을 동일 템플릿으로 획일화하지 않는다.
- 관련성이 약한 별도 사용자군은 무리하게 여행자용 메인에 편입하지 않는다.
- 이 다이어그램은 구조 초안이며 실제 데이터 흐름·성능·제휴 확정 표시가 아니다.
