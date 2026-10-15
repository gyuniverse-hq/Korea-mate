# Korea Mate 협업 가이드

이 저장소의 기본 협업 흐름은 **작업 브랜치 → `develop` → `main`** 입니다.

> ⚠️ 현재 저장소는 Private이고 GitHub 브랜치 보호 기능은 아직 강제되지 않습니다. 직접 push나 잘못된 대상 PR을 시스템이 완전히 막는다고 가정하지 마세요. 팀원 모두 아래 규칙을 따라야 합니다.

## 1. 브랜치 역할

| 브랜치 | 용도 | PR 대상 |
|---|---|---|
| `main` | 안정/발표/배포 기준 | `develop`에서만 PR |
| `develop` | 기능 통합·테스트 | 작업 브랜치의 기본 PR 대상 |
| `feat/*` | 신규 기능 | `develop` |
| `fix/*` | 버그 수정 | `develop` |
| `docs/*` | 문서 | `develop` |
| `research/*` | EDA·실험·분석 | `develop` |
| `refactor/*`, `test/*`, `chore/*` | 리팩터링·테스트·설정 | `develop` |

기능 작업은 **최신 `develop`에서 새 브랜치를 만들어 시작**합니다. `main`·`develop`에 직접 push하거나 force push하지 않습니다.

## 2. 작업 시작

```bash
git clone https://github.com/gyuniverse-hq/Korea-mate.git
cd Korea-mate
git fetch origin
git switch develop
git pull --ff-only origin develop

# 이름은 작업 목적에 맞게 변경
git switch -c feat/example-feature
```

이미 로컬 저장소가 있다면 `clone` 단계는 생략하세요.

## 3. 작업 후 PR

```bash
git add <변경한 파일>
git commit -m "feat: implement example feature"
git push -u origin feat/example-feature
```

GitHub **Pull requests → New pull request**에서 반드시 다음을 확인합니다.

- **base:** `develop`
- **compare:** 내 작업 브랜치
- PR 설명에 **무엇을/왜 변경했는지, 테스트 결과, 팀원에게 확인받을 부분**을 작성합니다.
- 완료 전에는 **Draft PR**로 공유하고, 검토 가능한 상태에서 **Ready for review**로 전환합니다.
- 가능하면 작성자 외 1명 이상의 팀원에게 리뷰를 요청합니다.
- 리뷰 후 `develop`으로 **Squash and merge**를 우선 권장합니다. 팀에서 이력 보존 방식을 합의했다면 예외로 합니다.
- 병합한 작업 브랜치는 삭제할 수 있습니다.

## 4. develop → main

- 통합 기능이 실제로 실행되는지 검증하고 발표·배포할 시점에 **base: `main`, compare: `develop`** PR을 생성합니다.
- 주요 기능, DB 마이그레이션, 환경변수 변경, 배포 영향, 남은 이슈를 기록합니다.
- 통합 테스트와 리뷰가 완료된 후 **Create a merge commit** 방식을 우선 권장합니다. `develop`의 이력을 `main`에서도 추적하기 쉽습니다.
- 병합 후 `main`에 태그를 붙이는 방법을 사용할 수 있습니다(`v0.1.0` 등).

긴급 수정도 가능하면 `develop`에서 재현·수정·검증한 후 `main`으로 올립니다. 별도 긴급 패치가 꼭 필요하다면 팀에서 처리 및 역반영 방법을 먼저 합의하세요.

## 5. 커밋 메시지와 보안

예시: `feat: add culture recommendation API`, `fix: correct activity mapping`, `docs: update EDA report`, `research: compare recommendation baselines`.

- `.env`, API 키, 개인정보, 응답자 단위 관광조사 원자료·CSV/XLSX는 커밋하지 않습니다.
- 분석 결과는 **출처/분모/가중치/방법/제약**을 기록합니다.
- 사용자가 체감하는 전환율과 오프라인 ML 지표는 구분합니다.
- `git push --force`는 공유 브랜치에서 사용하지 않습니다.
- 리뷰 없이 개인 브랜치에 작업을 무기한 쌓아두기보다는 작은 PR로 수시 공유합니다.

더 자세한 규칙과 예외는 [협업 절차](docs/collaboration/git-workflow.md)에서 확인하세요. 브랜치 보호 관련 실제 적용 상태는 [보호 설정 안내](docs/collaboration/branch-protection.md)를 확인하세요.
