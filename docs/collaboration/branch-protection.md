# GitHub 브랜치 보호 규칙 설정 안내

**확인일:** 2026-10-15
**저장소:** `gyuniverse-hq/Korea-mate` (Organization / Private)

## 실제 확인된 상태

- `main` 및 `develop`: GitHub Branch API `protected: false`.
- Rulesets API: HTTP **403**, 메시지 `Upgrade to GitHub Pro or make this repository public to enable this feature.`.
- Branch protection 조회 API: HTTP **403**, `Resource not accessible by integration`.
- GitHub 연결 도구에는 보호 규칙 생성·수정 쓰기 작업이 제공되지 않습니다.
- 따라서 **보호 규칙은 이번 PR로 실제 활성화되지 않습니다.**

공식 문서: [GitHub - Managing protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches).

## 지원 플랜/권한일 때 권장 설정

관리자는 [Repository → Settings → Branches](https://github.com/gyuniverse-hq/Korea-mate/settings/branches)에서 **Add classic branch protection rule**을 이용할 수 있습니다. 조직 소유 비공개 저장소는 지원되는 GitHub 조직 플랜과 관리자 권한이 필요할 수 있습니다.

### main
- Branch name pattern: `main`
- **Require a pull request before merging**: ON
- Required approving reviews: **1 이상**
- **Require conversation resolution before merging**: ON
- **Do not allow bypassing the above settings**: 가능하면 ON
- **Allow force pushes / Allow deletions**: OFF
- **Require status checks to pass before merging**: 통과 가능한 CI가 먼저 확인된 뒤 필수 체크로 설정

### develop
- Branch name pattern: `develop`
- **Require a pull request before merging**: ON
- Required approving reviews: **1 이상** (운영 상황에 따라 조정)
- **Require conversation resolution before merging**: ON
- **Allow force pushes / Allow deletions**: OFF
- CI가 안정화되기 전에는 존재하지 않는 체크 이름을 필수로 지정하지 않음

> 주의: GitHub의 일반적인 브랜치 보호 기능은 `main`으로의 PR 출처가 반드시 `develop`인지 직접 필터링하는 기능과는 다릅니다. 대상 경로 확인용 워크플로와 팀 리뷰를 함께 사용하세요. 워크플로가 필수 상태 검사로 지정되어야 병합을 차단할 수 있습니다.

## 비용과 대안

- 현재 **Private 저장소 유지**: 문서·PR 템플릿·자율 리뷰 및 선택적 가벼운 CI로 진행. 보호 규칙 강제는 되지 않을 수 있습니다.
- 지원되는 GitHub 조직 유료 플랜: 현재 비공개를 유지하면서 보호 규칙을 적용할 수 있습니다.
- 저장소 공개: GitHub Free에서도 브랜치 보호 사용 가능하지만 **코드·문서·기존 커밋 전체 공개 가능성을 충분히 검토**해야 합니다. 보호 규칙을 위해 즉시 공개 전환하는 것은 추천하지 않습니다.

## 현재 사용자가 직접 할 작업

1. [Branches 설정](https://github.com/gyuniverse-hq/Korea-mate/settings/branches)에 들어가 **보호 규칙 생성 가능 여부**를 확인합니다.
2. 가능하면 위 `main`·`develop` 설정을 별도로 생성합니다.
3. 접근이 막힌다면 조직 플랜 및 GitHub App 권한 문제를 구분합니다. 비용·공개 범위 변경은 팀에서 결정합니다.
4. 적용 후 테스트용 PR에서 리뷰 없는 병합/직접 푸시가 실제 차단되는지 검증합니다.

현재 GitHub **기본 브랜치는 `main`을 유지**합니다. 새 PR 생성 때 `base: develop`을 명시적으로 선택해야 합니다.
