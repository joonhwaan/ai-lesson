에이전트 맞춤 설정
코딩 에이전트는 별도의 맞춤 설정 없이도 매우 뛰어난 지능을 가집니다. 검증된 소프트웨어 엔지니어링 방식에 대한 이해도가 높고, 일반적으로 올바른 결정을 내립니다.

하지만 에이전트는 팀이 소프트웨어를 어떻게 작성하는지, 선호하는 도구가 무엇인지, 비즈니스의 구체적인 맥락이 무엇인지 알지 못합니다. 그래서 맞춤 설정이 필요합니다. 에이전트를 조정해 더 효과적으로 작업하고 더 높은 품질의 결과물을 만들도록 할 수 있습니다.

Cursor는 새 팀원을 온보딩할 때와 비슷하게 두 가지 단계의 커스터마이징을 제공합니다. 항상 알고 있어야 하는 내용을 위한 rules, 그리고 필요할 때 불러올 수 있는 전문 지식을 위한 skills입니다.

Rules: 정적 컨텍스트
Rules는 모든 대화가 시작될 때마다 에이전트가 읽는 .cursor/rules/ 디렉터리에 저장된 마크다운 파일입니다. 항상 적용되는 지침으로, 에이전트가 코드와 어떻게 상호작용할지 결정합니다.

좋은 Rules 파일은 짧고 구체적이며, 예시를 그대로 복사하기보다는 예시를 가리키도록 작성합니다.


# 명령어
- `npm run build`: 프로젝트 빌드
- `npm run typecheck`: 타입 체커 실행
- `npm run test`: 테스트 실행 (속도를 위해 단일 테스트 파일 선호)
# 코드 스타일
- CommonJS(require)가 아닌 ES 모듈(import/export) 사용
- 구조 분해 import 사용: `import { foo } from 'bar'`
- 표준 컴포넌트 구조는 `components/Button.tsx` 참조
# 워크플로우
- 일련의 코드 변경 후 항상 타입 체크 수행
- API 라우트는 기존 패턴을 따라 `app/api/`에 배치
규칙은 다음과 같은 용도에 가장 적합합니다:

에이전트가 알고 있어야 하는 빌드 및 테스트 명령어
에이전트가 따라야 하는 코드 컨벤션
코드베이스에서 기준이 되는 예제에 대한 안내
가드레일(수정하면 안 되는 파일, 피해야 할 패턴 등)
규칙에서 피해야 할 점
전체 스타일 가이드를 그대로 복사하지 마세요. 대신 린터를 사용하세요. 규칙은 도구를 대체하는 게 아니라 보완해야 합니다.
모든 명령을 일일이 문서화하지 마세요. 에이전트는 일반적인 도구는 이미 알고 있습니다. 프로젝트 전용 명령만 추가하세요.
간단하게 시작하세요. 규칙은 모든 대화에 포함되므로 계속 쌓입니다. 에이전트가 같은 실수를 반복하는 것이 보일 때만 규칙을 추가하고, 짧게 유지하세요.
규칙을 git에 커밋해 팀 전체가 이 공유된 지식을 함께 활용할 수 있게 하세요.

스킬: 동적 컨텍스트
스킬은 특화된 지식과 워크플로로 에이전트가 할 수 있는 일을 확장합니다. 규칙과 달리 스킬은 동적으로 로드됩니다. 에이전트는 현재 작업을 바탕으로 언제 스킬을 사용할지 결정합니다.

스킬은 SKILL.md 파일에 정의되며, 도메인 지식, 커스텀 워크플로, 그리고 에이전트가 실행할 수 있는 스크립트와 코드를 포함할 수 있습니다.


---
description: Deploy to staging. Use when the user asks to deploy, ship, or push to staging.
---
# Deploy to staging
## Steps
1. Run `npm run build` and confirm it succeeds
2. Run `npm run test` and confirm all tests pass
3. Run `npm run deploy:staging`
4. Verify the deployment by checking https://staging.example.com/health
5. Report the deployment status and URL
규칙과 스킬의 핵심 차이점:

Rules (규칙)	Skills (스킬)
When loaded	모든 대화	관련이 있을 때만
Purpose	항상 적용되는 규약	특화된 워크플로
Context cost	항상 컨텍스트 공간을 사용	호출될 때만 전체 컨텍스트를 사용
Best for	에이전트가 항상 알아야 하는 것	요청받았을 때 에이전트가 할 수 있는 것
에이전트가 ES 모듈 import 대신 계속 CommonJS require()를 사용하고 있습니다. 가장 좋은 해결 방법은 무엇인가요?


그럴 때마다 각 대화에서 바로잡는다.

규칙을 추가한다: 'Use ES modules (import/export), not CommonJS (require).'

require()를 import 구문으로 변환하는 스킬을 만든다.
Check
Reset
MCP: 외부 도구에 연결하기
MCP (Model Context Protocol)는 에이전트가 외부 도구에 연결하고 관련 컨텍스트를 가져올 수 있게 해줍니다. MCP 서버는 이 컨텍스트와 에이전트가 필요할 때 사용할 수 있는 동작을 제공합니다.

예를 들어, 에이전트를 다음에 연결할 수 있습니다:

Slack에서 메시지를 읽고 업데이트를 게시
Datadog에서 프로덕션 로그를 분석
Sentry에서 에러 세부 정보와 스택 트레이스를 조회
Databases에서 데이터를 직접 쿼리
Figma에서 디자인 토큰과 컴포넌트 스펙 가져오기
Marketplace를 살펴보고 사용하는 도구용 서버를 찾아보세요.

에이전트 기능으로서의 CLI 도구
MCP 외에도 에이전트는 터미널에 설치된 모든 CLI 도구를 실행할 수 있습니다. gh, aws, kubectl, docker 같은 도구는 추가 설정 없이 동작하며, 에이전트가 이를 직접 실행합니다.

규칙을 통해 에이전트가 사용할 유용한 도구를 지정하세요:


- Use `gh` for all GitHub operations (issues, PRs, CI checks)
- Use `aws s3` for file storage operations
이 기능은 디버깅에도 유용합니다. CI 상태를 확인하거나 이슈를 찾아보기 위해 브라우저로 전환하는 대신 에이전트에게 이렇게 요청할 수 있습니다: "gh를 사용해서 이 PR에서 CI가 실패한 이유를 확인해줘." 그러면 에이전트가 명령을 실행하고 출력 결과를 읽은 뒤, 이를 바탕으로 후속 작업을 수행합니다.

재사용 가능한 워크플로 저장
에이전트 입력창에서 /를 사용해 필요할 때마다 skills를 실행할 수도 있습니다. 이렇게 하면 skills가 이름으로 호출하는 재사용 가능한 워크플로가 되어, 하루에도 여러 번 수행하는 작업에 적합합니다.

예를 들어, 커밋하고 푸시한 뒤 풀 리퀘스트를 여는 /pr skill이 있을 수 있습니다:


---
description: 현재 변경 사항에 대한 풀 리퀘스트를 생성합니다.
---
1. `git diff`로 스테이징된 변경 사항과 스테이징되지 않은 변경 사항을 확인합니다
2. 변경된 내용을 기반으로 명확한 커밋 메시지를 작성합니다
3. 현재 브랜치에 커밋하고 푸시합니다
4. `gh pr create`를 사용하여 제목/설명과 함께 풀 리퀘스트를 생성합니다
5. 완료되면 PR URL을 반환합니다
pr: # Create a pull request Create a pull request for the current changes. ## Steps 1. Look at the staged and unstaged changes with `git diff` 2. Write a clear commit message based on what changed 3. Commit and push to the current branch 4. Use `gh pr create` to open a pull request with title and description 5. Return the PR URL when done

Add to Cursor
스킬로 쓰기 좋은 다른 워크플로 예시:

/fix-issue [number]: gh issue view로 이슈 상세를 가져오고, 관련 코드를 찾은 뒤 버그를 고치고 PR을 연다
/review: 린터를 실행하고, 흔한 문제를 점검하며, 주의가 필요한 부분을 요약한다
/update-deps: 오래된 의존성을 확인하고 하나씩 업데이트하면서, 매번 테스트를 실행한다
이 스킬들을 git에 커밋해 두면 팀 전체가 함께 실행할 수 있다.

전후 비교
실제 커스터마이징이 어떻게 동작하는지 살펴보세요. Next.js, Tailwind, Vitest를 사용하는 팀을 가정해 봅시다:

규칙 추가 전: 에이전트는 jest로 테스트를 진행하고(훈련 데이터에 더 자주 등장하기 때문에), CSS Modules로 컴포넌트를 만들며, API 라우트를 무작위 위치에 배치합니다.

세 가지 규칙을 추가한 후:


- 테스트는 Jest가 아닌 Vitest를 사용합니다. 패턴은 `src/__tests__/example.test.ts`를 참조하세요.
- Tailwind 유틸리티 클래스로 스타일링합니다. CSS 모듈이나 styled-components는 사용하지 않습니다.
- API 라우트는 기존 패턴을 따라 `app/api/[resource]/route.ts`에 배치합니다.
이제 에이전트는 기본적으로 팀의 관례를 따릅니다. 더 이상 대화할 때마다 같은 실수를 고쳐 줄 필요가 없습니다.

흔한 실패 패턴: 규칙을 과도하게 설계하기
모든 것에 대해 규칙을 만들고 싶어질 수 있습니다. 그러지 마세요. 규칙이 너무 많으면 불필요하게 컨텍스트를 소모하고 에이전트를 혼란스럽게 만들 수 있습니다.

규칙은 최소한으로 유지하되 품질은 높게 유지하세요. 규칙은 팀이 계속해서 업데이트하는 공유 자산이어야 합니다. 가끔만 필요한 내용이라면, 규칙 대신 스킬에 넣으세요.

다음 단계
이제 에이전트를 팀의 작업 방식에 맞게 커스터마이징했습니다. 마지막 장에서는 이 코스에서 배운 모든 내용을 적용하는 엔드 투 엔드 예제를 통해 지금까지의 내용을 모두 정리해 보겠습니다.