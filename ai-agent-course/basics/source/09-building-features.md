기능 개발하기
이제 코드베이스를 이해했으니, 새로운 것을 만들어 볼 차례입니다.

에이전트를 사용해 기능을 배포할 때 핵심은 에이전트가 스스로 검증할 수 있는 단계로 작업을 나누는 것입니다. 모든 주요 기능은 먼저 계획을 세우는 것부터 시작하고, 에이전트가 스스로 실수를 발견하고 수정할 수 있도록 적절한 가드레일을 설정하세요.

계획부터 시작하기
에이전트는 코드를 작성하기 전에 무엇을 만들지 고민하는 데 도움이 됩니다.

코드를 작성하기 전에 고민해야 할 결정들이 많습니다. 기능에 대한 아이디어가 있다면, 먼저 간단한 버전을 만들고 나중에 이를 반복적으로 개선하고 싶을 수 있습니다. 또는 고려해야 할 구체적인 설계 결정이 있을 수도 있습니다.

코드를 작성하기 전에 코딩 에이전트를 사용해 이런 결정들을 함께 검토할 수 있습니다. Cursor의 Plan Mode를 사용하면, 에이전트가 코드베이스를 조사하고, 명확히 하기 위한 질문을 한 뒤, 사용자가 편집하고 수정할 수 있는 단계별 계획을 만들어 줍니다.

plan mode에 프롬프트를 제출하면, 에이전트가 먼저 요구사항을 파악할 수 있도록 질문합니다:

Questions


알림 환경설정은 어디에 저장해야 하나요?

1
데이터베이스 (UserPreferences 테이블)

2
localStorage (클라이언트 전용)

3
localStorage 캐시가 있는 데이터베이스
Skip
Continue
답변을 마치면, 에이전트는 기능을 구현하면서 검토하고 검증할 수 있는 마일스톤이 포함된 구조화된 계획을 생성합니다. 이 계획은 수정 가능하므로, 이상해 보이는 부분이 있으면 변경할 수 있습니다:

Plans
notification-preferences.md
Build
Notification preferences
Overview
Add a notification preferences page to user settings. Users can toggle email, push, and in-app notifications per category (marketing, product updates, security alerts). Preferences stored in the database with optimistic UI updates.

Approach
Follow the existing settings page layout in src/pages/Settings.tsx
Use the UserPreferences table with a JSONB column for notification config
Reuse our existing Toggle component from the UI library
5 Tasks
Add notification_preferences column to UserPreferences table
Create NotificationPreferences component following Settings.tsx patterns
Add API route at app/api/user/notifications/route.ts
Wire up optimistic updates using our existing useOptimistic hook
Add tests for preference toggling and API validation
Cursor는 더 큰 요청을 더 작고 독립적으로 검증 가능한 단계로 나누어 계획을 유용하게 만듭니다. 각 단계에서 에이전트는 진행 상황을 측정하고, 단계가 성공적으로 완료되었는지 확인한 뒤 다음으로 넘어갈 수 있습니다.

처음부터 다시 시작해야 할 때
가끔 에이전트가 기대와 다른 결과물을 만들 때가 있습니다. 후속 프롬프트로 고치려 하기보다는, 다시 계획으로 돌아가세요. 변경 사항을 되돌리고 계획을 더 구체적으로 다듬은 뒤, 다시 실행하세요.

예를 들어, 중요한 아키텍처나 시스템 설계 관련 메모를 놓쳤다면, 그 계획은 잘못된 결과물을 만들 수 있습니다. 계획 단계부터 다시 시작하는 것은 직관에 어긋나 보일 수 있지만, 처음부터 방향이 잘못된 접근법을 땜질하는 것보다 더 빠른 경우가 많습니다.

에이전트와 함께하는 테스트 주도 개발
에이전트는 자신의 코드가 올바른지 스스로 판단할 수 있을 때 가장 좋은 결과를 냅니다. 테스트가 실패하면, 에이전트는 무엇이 잘못됐는지 파악하고 다시 시도할 수 있습니다.

엔지니어들은 오래전부터 테스트 주도 개발을 사용해 왔지만, 항상 가장 인기 있는 코딩 방식이었던 것은 아닙니다. 에이전트를 사용하면 테스트를 먼저 작성하기가 훨씬 쉬워지고, 코드베이스가 커질수록 그 테스트가 큰 가치를 제공합니다.

먼저 테스트를 작성합니다. 에이전트에게 예상 입력과 출력에 기반해 테스트를 작성하라고 요청하세요. TDD를 하고 있다는 점을 분명히 알려, 아직 존재하지 않는 코드에 대한 mock 함수를 만들지 않도록 하세요.
테스트가 실패하는지 확인합니다. 에이전트에게 테스트를 실행해 보고 실패하는지 확인하라고 지시하세요. 이 시점에서는 기능 코드를 작성하려는 것이 아닙니다.
테스트를 커밋합니다. 테스트 커버리지와 품질에 만족하면 테스트를 커밋하세요. 이렇게 하면 에이전트가 이를 기준으로 기능을 구현해야 하는 요구사항이 고정됩니다.
에이전트에게 코드를 작성하게 합니다. 테스트를 수정하지 않고 모든 테스트를 통과시키도록 지시하세요. 전부 통과할 때까지 계속 반복하도록 두세요.
코드를 커밋합니다. 결과를 검토하고, 기대한 대로 동작하는지 확인한 뒤 커밋하세요.
Agent example: TDD: 먼저 테스트 작성
Write tests for a discountCode() function that:
•
Returns the discounted price when given a valid code
•
Throws InvalidCodeError for expired codes
•
Applies fixed-amount discounts correctly (e.g., "10OFF" = $10 off)
•
Never returns a negative price (floor at $0)
Follow the test patterns in 
src/__tests__/pricing.test.ts
. Do NOT write the function yet.

See Cursor's response
테스트를 커밋했으면 이제 에이전트에게 코드를 작성하도록 지시하세요. 테스트를 수정하지 않고 모든 테스트를 통과시켜야 한다는 점을 명확히 전달하세요.

Agent example: TDD: 테스트 통과시키기
Make all tests in 
src/__tests__/discountCode.test.ts
 pass. Follow the service patterns in 
src/services/PricingService.ts
. Do NOT modify the tests.

See Cursor's response
왜 이런 방식이 그렇게 잘 작동할까요? 에이전트가 테스트를 실행하고, 실패를 확인하고, 코드를 수정한 뒤 다시 시도할 수 있기 때문입니다. 각 테스트 실행이 에이전트에게 구체적인 피드백을 제공합니다. 테스트가 없으면, 에이전트는 자신이 한 코드 변경이 제대로 동작하는지 알 방법이 없습니다.

이 접근 방식은 특히 화면만으로는 정확성을 확인하기 어려운 백엔드 코드에서 유용합니다. 테스트에서 기대 동작을 서술하고, 에이전트는 그에 맞는 코드를 작성합니다.

에이전트와 함께하는 TDD 워크플로에서, 왜 에이전트에게 코드 작성을 요청하기 전에 테스트를 먼저 커밋해야 하나요?


git 히스토리를 더 깔끔하게 만들기 위해서입니다.

에이전트가 테스트를 쉽게 통과시키기 위해 테스트를 수정하지 못하게 하기 위해서입니다.

테스트는 CI를 위해 별도 커밋에 있어야 하기 때문입니다.
Check
Reset
디자인을 코드로
에이전트는 이미지를 처리하고 이해할 수 있습니다. 스크린샷이나 목업을 프롬프트 입력란에 바로 붙여넣으면 에이전트가 해당 이미지를 바탕으로 디자인에 맞춰 작업할 수 있습니다.

다음과 같은 용도로 사용할 수 있습니다:

목업: 와이어프레임이나 Figma 내보내기 파일을 붙여넣고 에이전트에게 컴포넌트를 구현해 달라고 요청
시각적 디버깅: 예상치 못한 UI 상태를 스크린샷으로 찍고 에이전트에게 원인을 조사해 달라고 요청
반복 개선: 현재 결과의 스크린샷을 찍고 무엇을 어떻게 바꿔야 하는지 설명
Figma MCP server를 연결하면 에이전트가 Figma 파일에서 디자인 토큰, 변수, 컴포넌트 스펙을 직접 가져올 수 있습니다.

integrated browser를 사용하면 에이전트가 적용하는 변경 사항을 바로 미리 볼 수 있습니다. 이 브라우저를 통해 에이전트는 페이지를 탐색하고, 스크린샷을 찍고, 자신의 시각적 출력을 검증할 수 있습니다. 덕분에 스크린샷을 직접 다시 에이전트에게 전달하는 수고를 덜 수 있습니다.

일반적인 실패 패턴: 검증 없이 구현하기
기능을 빠르게 구현할 때 가장 큰 위험은 검증 단계를 건너뛰는 것입니다. 에이전트는 많은 코드를 빠르게 생성할 수 있지만, 정확성 없는 속도는 결국 일을 줄이기보다는 나중에 더 많은 일을 만들 수 있습니다.

에이전트가 자신의 작업을 검증할 수 있도록 도와주는 구체적인 방법은 다음과 같습니다:

로직과 동작을 위한 테스트
구조적 정확성을 위한 타입 검사
코드 스타일과 패턴을 강제하기 위한 린터
UI 변경 사항에 대한 피드백을 수집하기 위한 브라우저 도구 또는 MCP 서버
에이전트가 자신의 출력을 검증할 수 없다면, 결국 더 많은 시간을 수정 작업에 쓰게 됩니다.

다음 단계
이미 기능을 배포했습니다. 하지만 소프트웨어에는 항상 버그가 있고, 그중 일부는 꽤 까다롭습니다. 다음 장에서는 에이전트를 활용해 버그를 체계적으로 찾고 수정하는 방법을 배웁니다.