코드 검토 및 테스트
코딩 에이전트는 많은 코드를 만들어낼 수 있고, 이는 기술 부채도 많이 만들어낼 수 있다는 뜻입니다. 빠르게 진행하는 건 좋지만, 품질 기준은 높게 유지해야 합니다. 코드가 사람이 직접 작성했든 에이전트가 작성했든, 무엇을 머지할지에 대한 기준은 동일해야 합니다.

AI가 생성한 코드는 겉보기에는 올바른 것처럼 보여도 미묘하게 틀릴 수 있습니다. 기존 패턴을 따르고, 컴파일도 되고, 여러분이 작성한 테스트도 통과할 수 있지만, 여전히 엣지 케이스를 놓치거나 보안 문제가 있거나, 코드베이스 어딘가에 이미 존재하는 로직을 중복 구현할 수 있습니다.

그래서 코드 리뷰가 매우 중요합니다. 높은 품질의 코드베이스를 유지하고 문제가 프로덕션에 도달하기 전에 잡을 수 있도록 적절한 프로세스를 마련해야 합니다. 엔지니어로서 코드 리뷰가 효과적으로 이루어지도록 투자하는 것은 여러분의 책임입니다.

자체 리뷰
코드를 다른 사람에게 리뷰해 달라고 요청하기 전에, 먼저 스스로 코드를 검토하세요.

에이전트가 작업하는 모습을 지켜보세요. diff 뷰에서 변경 사항이 실시간으로 표시됩니다. 에이전트가 잘못된 방향으로 가는 것이 보이면 Stop을 클릭하거나 
Ctrl Shift Backspace
를 눌러 취소하고 다시 지시하세요. 끝날 때까지 기다릴 필요는 없습니다. 보다 큰 수준의 방향 전환이 필요하다면, 변경 사항을 되돌린 뒤 다시 실행하기 전에 계획을 먼저 다듬으세요. 이 내용은 기능 개발에서 다뤘습니다.

에이전트에게 한 번에 모든 변경 사항을 리뷰해 달라고 요청하세요. 프롬프트에 @Branch를 태그해 현재 브랜치의 전체 diff를 에이전트에게 제공하세요. "이 브랜치의 변경 사항을 리뷰해 줘" 또는 "지금 내가 뭘 작업 중이야?"처럼 말해 에이전트에게 풍부한 맥락을 제공하고 여러 파일에 걸친 이슈를 잡을 수 있게 하세요.

예를 들어, 에이전트에게 자신의 작업을 리뷰해 달라고 요청할 수 있습니다:

Ask mode example: Self-review
Review the changes I've made to the discount code feature. Look for bugs, missing error handling, and anything that doesn't match our patterns in 
src/services/PricingService.ts

See Cursor's response
Ask mode example: Anticipate reviewer questions
What questions will reviewers have about these changes? What context should I include in the PR description?

See Cursor's response
동료 리뷰를 준비하세요
에이전트는 한 번에 코드를 많이 바꿀 수 있습니다. 그러면 변경된 줄이 수백 줄에 이르는 하나의 거대한 커밋이 생길 수 있고, 이는 누구라도 리뷰하기 어렵습니다.

작고 의미 있는 커밋을 만들고, 각 커밋에 명확한 설명을 다는 방식을 권장합니다. 각 커밋이 하나의 논리적인 변경을 나타나도록 하세요. 그러면 사람이 방대한 코드 변경 내역을 한 번에 해석하는 대신, 커밋 히스토리를 한 단계씩 따라가며 리뷰할 수 있습니다.

이런 커밋 정리는 직접 하기엔 번거롭지만, 에이전트는 잘 처리합니다. 예를 들면:

우선 자유롭게 기능을 구현합니다. 반복해서 수정하는 동안에는 커밋 정리에 신경 쓰지 마세요.
모든 것이 잘 동작하면, 에이전트에게 커밋 히스토리를 리뷰 가능한 단위로 재구성해 달라고 요청하세요.
에이전트는 main으로 리셋한 뒤 모든 변경 사항을 읽고, 설명이 잘 된 깔끔한 커밋을 만들 수 있는 논리적인 순서를 계획합니다.
최종 diff가 원래 변경 사항과 일치하는지 검증해, 어떤 변경도 빠지지 않도록 합니다.
이 프롬프트를 사용해 skill을(를) 만들면, 팀 누구든 기능을 마친 뒤 /rework-commits를 실행할 수 있습니다:

Create a skill file at .cursor/skills/rework-commits/SKILL.md with this content: # Split branch into reviewable commits Rework a branch into a sequence of small, semantic commits for review. ## Important - Prepend `GIT_EDITOR=true` to all git commands you run, especially ones looking at diffs, so you avoid getting blocked ## Instructions 1. **Check for uncommitted changes**: Abort if there are any. 2. **Check rebase status**: Verify the branch is rebased on top of `main`. Abort if not. 3. **Save recovery point**: Tell the user the current commit hash in case we need to `git reset --hard` to it later. 4. **Save the original diff**: Save the full git diff to `/tmp/original-diff.patch` before making changes. 5. **Reset to main**: Run `git reset main` to unstage all changes. 6. **Plan the commits**: Read through ALL changes carefully. Plan a logical breakdown into small, sequential, semantic commits. Write a TODO for each in `/tmp/split-todos.md`. Order: database/schema changes first, backend second, frontend last. 7. **Create the commits**: Work through the TODOs one by one. Write excellent commit descriptions for human reviewers. 8. **Validate**: Compare the current diff against `/tmp/original-diff.patch` to ensure no changes were lost or altered. 9. **Cleanup**: Delete temporary files once validation passes. ## Notes - If validation fails, tell the user and provide the original commit hash for recovery - Each commit should be self-contained and represent a logical unit of work - Commit messages should explain the "why" behind the changes

Try in Cursor
Agent Review
에이전트가 작업을 마친 후 Review를 클릭한 다음 Find Issues를 눌러 전용 코드 리뷰를 실행하세요. 에이전트가 제안된 수정 사항을 한 줄씩 분석하고 잠재적인 문제를 표시합니다.

모든 로컬 변경 사항에 대해 Source Control 탭을 열고 Agent Review를 실행해 메인 브랜치와 비교하세요. 이렇게 하면 전체 변경 사항 전반의 문제를 잡아낼 수 있습니다.

이는 에이전트에게 수동으로 변경 사항을 리뷰하도록 요청하는 것과 비슷합니다. 이를 효과적으로 수행할 수 있도록 프롬프트를 세심하게 구성했습니다.

풀 리퀘스트용 Bugbot
Bugbot은 소스 코드 관리 서비스와 연동되어 풀 리퀘스트를 자동으로 리뷰합니다. PR 자체에서 직접 피드백을 제공하는 도구들 가운데 하나이며, 이런 도구들은 점점 더 많아지고 있습니다.

Bugbot은 코드를 푸시할 때 PR을 리뷰합니다. 변경된 코드가 코드베이스의 나머지 부분과 어떻게 연결되는지까지 포함해 변경의 전체 컨텍스트를 읽고, 프로덕션까지 올라갈 수 있는 버그를 찾습니다. 포맷팅 문제만 잡아내는 린터와 달리, Bugbot은 널 포인터 예외, 레이스 컨디션, 누락된 에러 처리, 보안 문제와 같은 로직 오류를 찾아냅니다.

Bugbot이 문제를 발견하면 수정안도 제안할 수 있습니다. autofix를 활성화하면, 풀 리퀘스트의 댓글에서 바로 해당 수정을 커밋할 수 있습니다.

또한 추가 규칙을 제공해 Bugbot을 커스터마이징할 수도 있습니다. 이에 대해서는 다음 에이전트 커스터마이징 섹션에서 더 자세히 설명합니다.

검증 가능한 목표
코드의 정확성을 보장하는 데 도움이 되도록, 에이전트가 자신의 작업을 스스로 검증할 수 있게 하는 명확한 신호를 제공해야 합니다:

테스트는 동작 회귀를 잡아냅니다
타입 검사는 구조적 오류를 잡아냅니다
린팅은 스타일 및 패턴 위반을 잡아냅니다
이러한 검사를 더 많이 갖출수록 에이전트에게 더 자신 있게 작업을 맡길 수 있습니다. 에이전트와 함께 테스트 커버리지와 린팅 규칙을 갖춘 정적 타입 언어를 사용하는 것을 권장합니다.

어떤 조합이 AI가 생성한 코드에 가장 강력한 안전망을 제공하나요?


수동 코드 리뷰만.

자동 린팅만.

테스트, 타입 검사, 린팅, Bugbot을 사람의 리뷰와 함께 사용하는 것.
Check
Reset
에이전트에게 테스트를 맡기세요
과거에는 충분한 테스트 커버리지를 구축하는 데 상당한 노력이 필요했습니다. 대부분의 팀은 문제가 발생한 뒤에야 테스트를 추가하거나, 특정 커버리지 비율을 보장하기 위한 무거운 프로세스를 운영하곤 했습니다.

에이전트를 사용하면 테스트 작성이 훨씬 수월해집니다. 에이전트에게 테스트 작성을 요청하고, 올바른지 검증시키면 됩니다. 에이전트는 browser를 통해 수동 테스트도 대신 수행해서, 원래라면 직접 확인해야 했을 UI 상태나 플로우를 점검해 줄 수 있습니다.

Agent example: 에이전트가 작성한 테스트
discount code API endpoint용 통합 테스트와 checkout discount 플로우용 e2e 테스트를 작성해 주세요. 기존 테스트 패턴을 살펴보고 그 패턴에 맞춰 주세요.

See Cursor's response
이게 중요한 이유는, 고품질 테스트가 에이전트가 자율적으로 작업하고 회귀 없이 변경을 수행하도록 더 큰 확신을 주기 때문입니다.

테스트 생성을 위한 좋은 프롬프트 예시:

"checkout 플로우에 대해 e2e 커버리지를 어떻게 확보할지 계획해 주세요. 어떤 시나리오를 테스트해야 하나요?"
"payments API용 통합 테스트를 설정해 주세요. src/__tests__/에 있는 기존 테스트 인프라를 사용해 주세요."
"현재 discount 기능 테스트에서 커버되지 않은 엣지 케이스는 무엇인가요?"
"PaymentService.ts에서 우리가 수정한 버그에 대한 회귀 테스트를 작성해 주세요."
에이전트는 테스트 인프라를 처음부터 구축하는 것도 도와줄 수 있습니다. 웹 애플리케이션용 Playwright가 아직 설정되어 있지 않다면, 프로젝트 셋업, 설정 작성, 첫 번째 테스트 생성을 요청해 보세요.

Cloud agents
지금까지는 에디터에서 로컬로 실행되는 에이전트를 사용했습니다. Cloud agents는 원격 샌드박스에서 실행되므로, 노트북을 닫았다가 나중에 결과를 확인할 수 있습니다.

동작 방식은 다음과 같습니다.

작업을 설명하고 관련 컨텍스트를 제공합니다.
에이전트가 저장소를 클론하고 브랜치를 만듭니다.
에이전트가 알아서 작업을 진행하고, 완료되면 풀 리퀘스트를 엽니다.
작업이 끝나면 (Slack, 이메일, 또는 웹 인터페이스를 통해) 알림을 받습니다.
변경 사항을 검토하고 준비되면 머지합니다.
Cloud agents는 보통이라면 TODO 목록에 추가해 둘 작업에 특히 잘 맞습니다. 예를 들어 다른 작업 중에 발견한 버그 수정, 기존 코드에 대한 테스트 커버리지, 문서 업데이트, 리팩터링 등이 이에 해당합니다.

클라우드 에이전트를 활용한 대규모 테스트
강력한 패턴 중 하나는 클라우드 에이전트를 사용해 다양한 변형을 병렬로 테스트하는 것입니다. 여러 클라우드 에이전트를 실행해 애플리케이션 전반에 걸쳐 여러 엣지 케이스, 오류 조건, 입력 조합을 시도해 볼 수 있습니다.

예를 들어, 새로운 할인 코드 기능을 추가했다고 가정해 봅시다. 이때 클라우드 에이전트를 실행해 모든 할인 유형을 테스트하고, 잘못된 입력을 넣어 보고, 할인 중복 적용 같은 조합을 테스트하고, 엣지 케이스 경계값에서의 동작을 검증할 수 있습니다.

각 클라우드 에이전트는 자체 테스트 케이스와 결과가 포함된 브랜치를 생성합니다. 이후 실패 사례를 모아 재현 가능한 로컬 테스트 케이스로 만들고, 병합 전에 수정할 수 있습니다.

피드백 루프 가속하기
더 많은 코딩 에이전트를 쓰기 시작하면, 병목은 시스템에서 가장 느린 부분으로 옮겨 갑니다. 보통은 테스트 스위트가 끝나길 기다리거나, 코드베이스 전체에 타입/린트 검사를 돌리거나, CI 파이프라인의 다른 단계를 기다리는 부분입니다.

에이전트와의 모든 대화마다 이 비용을 치르게 됩니다. 테스트 실행에 10분이 걸리고 에이전트 10개를 병렬로 띄우면, 거의 두 시간을 기다려야 합니다. 테스트를 50% 빠르게 만들면 그때마다 거의 한 시간을 절약할 수 있습니다.

이런 개선은 모든 세션, 모든 브랜치, 모든 에이전트에서 반복적으로 효과를 발휘합니다. 효율이 큰 변경의 예시는 다음과 같습니다:

테스트 스위트 속도 높이기
의존성 트리 줄이기
CI 파이프라인 최적화하기
타입 체크 더 빠르게 만들기
빌드 시간 줄이기
이런 작업은 팀이 우선순위를 낮게 두기 쉽지만, 에이전트가 하루에도 수십 번씩 이런 명령을 실행하면 절감 효과가 눈덩이처럼 커집니다. 테스트를 빠르게 만드는 데 한 시간 투자해 두면, 시간이 지나며 수백 시간을 아낄 수 있습니다.

가장 좋은 점은, 이 일을 에이전트가 대신 해줄 수 있다는 것입니다. 에이전트에게 테스트를 프로파일링해서 가장 느린 테스트를 찾아 고치라고 시킬 수 있습니다. 사용되지 않는 의존성을 찾아 제거하도록 의존성 감사를 시킬 수도 있습니다. 이런 작업은 범위가 명확하고 결과가 검증 가능하며, 바로 이런 곳에서 에이전트가 가장 잘 동작합니다.

흔한 실패 패턴
테스트를 통과했다고 해서 코드가 제대로 동작한다는 보장은 없습니다. 테스트가 잘못된 동작을 검사하고 있을 수도 있습니다. 에이전트가 일반적인 경우(happy path)에서는 동작하는 코드를 작성했지만, 모든 예외/경계 상황(edge case)을 고려하지 않았을 수도 있습니다.

코드 변경 사항을 이해하는 것이 중요합니다. 변경 범위가 너무 커서 한 번에 검토하기 부담스럽다면, 여러분과 에이전트가 모두 검토하기 쉬운 더 작은 단위로 나누는 것을 고려해 보세요.

다음 단계
이제 새로운 기능을 배포하고, 문제가 생겼을 때 디버깅하며, 코드 리뷰를 통해 높은 품질을 보장하는 방법을 이해했습니다. 이제 남은 일은 에이전트가 사용 중인 코드베이스에 맞게 동작 방식을 맞춤 설정해, 워크플로를 더 빠르게 만드는 것입니다.