# 05 · GitHub 플러그인에 붙여 넣는 외부 디자인 평가 요청문

아래 메시지를 다른 ChatGPT/AI 서비스에서 **GitHub 플러그인 연결 후 그대로 요청**하면 된다. 연결 권한이 필요한 비공개 저장소다.

---

다음 GitHub 저장소의 **KoreaMate UI/UX 디자인 평가 패키지 v1.0**을 실제로 읽고 비판적으로 검토해 주세요.

- 저장소: `gyuniverse-hq/Korea-mate`
- 브랜치: `docs/koreamate-experience-redesign`
- 반드시 처음 읽을 파일: `docs/product/experience-redesign/evaluation/README.md`
- 같은 폴더의 `01-product-context.md`, `02-home-screen-spec.md`, `03-visual-audit.md`, `04-evaluation-rubric.md`를 순서대로 읽으세요.
- 현재 디자인 대상: `docs/product/experience-redesign/previews/d-main-hifi-v0.9.html`
- 화면 자료: `docs/product/experience-redesign/assets/v0.9/` 아래 `reference-v0.9.webp`, `browser-desktop-v0.9.webp`, `browser-mobile-v0.9.webp`, `target-vs-html-v0.9.webp`.
- 참고: `docs/product/experience-redesign/design-handoff-v0.9.md`, `service-experience-v0.5.md`, `experience-map.md`.

**중요한 배경**

KoreaMate는 외국인의 한국 문화 발견·사진/질문/콘텐츠 이해·여행 실행·현장 문제 해결을 이어주는 AI 여행 동반자입니다. Kravel(촬영지 여행), K-Season(축제/팝업), K-Beauty(메이크업 AR), GG Korea(팬 경험), K-Class(한국어 학습) 등 팀원 아이디어를 독립적인 체험으로 살리면서 KoreaMate의 원래 정체성도 유지하고 싶습니다.

현재 v0.9는 **메인 한 화면의 고충실도 디자인과 HTML 재현 시제품**입니다. 실제 LLM, 사진 인식, AR, 최신 행사/예약/동선 계산은 연결되어 있지 않습니다. v0.7/0.8은 이전 디자인 실험이므로 현재 메인으로 평가하지 마세요.

**평가 요청**

1. 초보 사용자의 시선으로 PC·모바일 첫 5초에 서비스 정체성과 주 행동이 전달되는지 판단하세요.
2. 시각 디자인이 정말 완성도 높은지, 왜 어색하거나 양산형 데모/관광 광고처럼 보이는지 **솔직하게** 평가하세요. 사진 배치, 색감, 글꼴, 그리드, 카드 정보량, 대비를 구체적으로 비판하세요.
3. KoreaMate 자체의 Ask/Scan/발견/현장 도움과 Kravel·K-Beauty·K-Season 등 전문 기능의 매력이 모두 살아 있는지 검토하세요. 억지로 연결된 요소를 지적하세요.
4. **목표 시안 이미지와 실제 브라우저 HTML 캡처를 비교**하고 가장 크게 다른 시각 요소를 찾아주세요.
5. 모바일 정보 구조·하단 내비게이션·첫 행동 접근성을 별도로 평가하세요.
6. 화면의 '지금', 추천, 2025년 시즌 콘텐츠가 실시간 정보인 것처럼 보이는 위험도 지적하세요.
7. 문제마다 `화면 위치 → 관찰 → 사용자 영향 → 개선 제안 → 우선순위(P0/P1/P2)`를 제공하고, **가장 시급한 5~10개**를 먼저 보여주세요.
8. 유지해야 할 강점 3개와 완전히 바꿔야 할 부분을 구분하고, 최종적으로 다음 디자인 수정 순서를 추천하세요.
9. `04-evaluation-rubric.md` 기준으로 점수도 제시하되, 이미지·HTML을 실제로 못 봤다면 그 사실을 명확히 밝히고 점수는 보류하세요. 막연한 칭찬이나 구현되지 않은 기능을 완성된 것으로 가정하지 마세요.

**접근 제약이 있으면** GitHub 플러그인으로 먼저 문서를 읽고, 이미지(WebP)를 실제로 볼 수 없는 경우 그 한계를 설명하고 이미지가 열리는 환경 또는 업로드된 화면 캡처로 시각 평가를 이어가 주세요. 파일명이나 Markdown 설명만 보고 이미지의 색감·품질을 단정하지 마세요.

**응답 순서**: 전체 총평 → 강점 3개 → 핵심 문제 5~10개(우선순위 포함) → PC·모바일 비교 → v0.9 시안 대 실제 구현 차이 → 개선 설계 제안 → 평가 보류/추가 확인 사항.

---

## 공유 팁

- GitHub README 링크를 함께 주면 평가자가 파일을 찾는 시간을 줄일 수 있다.
- WebP를 해석하는 데 제약이 있는 평가자에게는 사용자 측에서 이미지를 직접 첨부하거나 GitHub의 이미지 보기 화면을 함께 제시하면 좋다.
- 상대방에게 `main`이나 `develop`을 읽으라고 하면 이 평가 패키지는 보이지 않는다. **반드시 지정 브랜치를 사용**하도록 한다.