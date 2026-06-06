# AI 에이전트 개발 마스터 코스 — 용어집(Glossary)

> 8개 세션에 반복 등장하는 핵심 용어를 한 페이지로 모았다. 각 항목은 1~2줄 정의 + (처음/주로 다루는 세션) 표기.
> 공통 예제는 **리서치 어시스턴트**(도구: `web_search` · `calculator` · `fetch_url` · `summarize` · `cite`)다.

---

## A–M (영문)

- **AgentExecutor** — 도구 호출 루프를 실행하는 LangChain 런타임. 세션 2의 `while` 루프를 감싼 것. (S5)
- **Agentic Loop** — 관찰(Observe) → 추론(Think) → 행동(Act)을 목표/종료조건까지 반복하는 제어 흐름. 에이전트의 심장. (S1)
- **Autonomy(자율성)** — 인간 개입 없이 다음 행동을 모델이 스스로 정하는 정도. Workflow↔Agent 스펙트럼의 축. (S1)
- **Chain-of-Thought(CoT)** — 답 이전에 중간 추론 단계를 토큰으로 펼쳐(외재화) 정확도를 높이는 기법. (S3)
- **Checkpointer** — 그래프 상태를 저장해 중단/재개·HITL·time-travel 디버깅을 가능케 하는 영속화 계층. (S6)
- **Conditional Edge** — 상태값에 따라 다음 노드를 선택하는 동적 분기. 노드 내부 `if`와 달리 제어 흐름을 그래프로 외부화한다. (S6)
- **Context Window(컨텍스트 윈도우)** — 모델이 한 번에 볼 수 있는 토큰 한계. 유한·고비용이라 메모리 전략이 필요한 근본 이유. (S4)
- **Grounding** — 도구 결과 등 실제 데이터에 모델 출력을 근거시키는 것. (S2)
- **Guardrail(가드레일)** — 입력/출력/행동을 제약하는 안전·정책 장치(권한 최소화, 승인 게이트, 타임아웃 등). (S8)
- **Handoff(핸드오프)** — 한 에이전트가 다른 에이전트에게 "제어권 + 컨텍스트"를 넘기는 행위. (S7)
- **Hierarchical(계층형)** — 감독자 위에 또 감독자를 두는 다층 오케스트레이션 구조. (S7)
- **Human-in-the-loop(HITL)** — 비가역·고위험 동작 전에 사람의 승인을 받는 개입 지점. LangGraph는 `interrupt`로 구현. (S6·S8)
- **LCEL(LangChain Expression Language)** — `|` 파이프로 컴포넌트를 합성하는 선언적 표현 언어. 한 방향 파이프(루프는 표현 못 함). (S5)
- **LLM-as-a-Judge** — 다른 LLM에게 루브릭과 함께 출력을 채점시키는 평가 기법. 길이·위치·자기선호 편향에 주의. (S8)
- **Lost in the Middle** — 긴 컨텍스트의 중간에 놓인 정보가 잘 활용되지 않는 현상. 중요 정보는 앞/뒤 배치. (S4)
- **MAX_TURNS** — 에이전트 루프의 최대 반복 횟수 상한. 무한 루프 방지 안전장치. (S2)
- **MCP(Model Context Protocol)** — 에이전트를 외부 도구/데이터 소스에 연결하는 표준 프로토콜. (S2·S5)
- **Memory(단기/장기)** — 단기=세션 내 대화/scratchpad, 장기=외부 영속 저장(벡터DB 등). "기억"은 컨텍스트 재주입의 엔지니어링. (S4)

## N–Z (영문)

- **Network / Swarm** — 중앙 조율자 없이 에이전트들이 서로 직접 핸드오프하는 구조. 유연하지만 무한 위임 루프 위험. (S7)
- **Output Parser** — 모델의 raw 출력을 구조화된 형태(문자열/JSON/Pydantic)로 변환·검증하는 컴포넌트. (S5)
- **Plan-and-Execute** — 전체 계획 수립(planner)과 단계 실행(executor)을 분리한 아키텍처. 일관성·토큰 절약, 초기 계획 오류엔 취약. (S3)
- **Prompt Injection** — 외부 데이터(fetch한 웹페이지 등)에 숨은 지시를 모델이 명령으로 오인하는 공격. "외부 데이터=신뢰 불가". (S8)
- **RAG(Retrieval-Augmented Generation)** — 검색한 외부 지식을 생성에 결합. 에이전트 메모리의 한 형태. 청킹/재랭킹/하이브리드 검색은 개념 수준. (S4)
- **ReAct(Reason + Act)** — 추론(Thought)과 행동(Action)·관찰(Observation)을 교차 생성하는 패러다임. 탐색·도구 의존 과제에 강함. (S1·S3)
- **Reducer** — 노드가 반환한 부분 상태를 전체 상태에 병합하는 규칙(예: append). 멀티 worker의 동시 쓰기 충돌 방지. (S6·S7)
- **Reflection / Reflexion** — 자기 출력을 비평·재시도하는 루프. Reflexion은 실패 교훈을 언어적 메모리로 누적. (S3)
- **Runnable** — `invoke`/`stream`/`batch`를 제공하는 LangChain 공통 실행 인터페이스. 조합 가능성의 기반. (S5)
- **Scratchpad** — 추론 trace나 진행 메모를 컨텍스트 윈도우 안에 유지하는 단기 작업 공간. (S3·S4)
- **Self-Consistency** — 같은 질문에 여러 추론 경로를 샘플링해 다수결로 답을 고르는 기법. 답이 수렴하는 과제에 적합. (S3)
- **State Graph** — 상태를 공유하며 노드/엣지로 흐름을 정의하는 LangGraph 실행 모델. while 루프의 1급 시민화. (S6)
- **Stop Condition(정지 조건)** — 루프를 멈추는 조건. 도구를 더 안 부르고 최종 텍스트를 내거나 MAX_TURNS 초과 시. (S2)
- **Summarization Buffer(요약 메모리)** — 오래된 대화를 요약으로 압축해 보관하는 메모리. 수치·인용 누락(요약 손실) 위험. (S4)
- **Supervisor(Orchestrator)** — 작업을 분해·위임·통합하는 중앙 조정 에이전트. 명확하지만 병목·SPOF가 될 수 있음. (S7)
- **Tool Result** — 도구 실행 결과를 모델에게 되돌려주는 메시지. 실패도 모델이 읽을 형태로 줘야 자기수정 가능. (S2)
- **Tool Schema(도구 스키마)** — 도구의 이름/설명/입력 파라미터를 정의한 모델용 계약(JSON Schema). description이 곧 프롬프트. (S2)
- **ToolNode** — LangGraph에서 도구 실행을 담당하는 미리 만들어진 노드. 세션 2 루프의 도구 실행부를 그래프 노드로 1급화한 것. (S6)
- **Trajectory(궤적) 평가** — 최종 결과뿐 아니라 도구 호출 순서·인자 등 거쳐 간 경로를 평가. 효율성·비용 문제를 짚음. (S8)
- **Tracing / Observability** — 모든 LLM/도구 호출을 기록·시각화해 디버깅·개선을 가능케 함(LangSmith 등). (S8)
- **Tree-of-Thoughts(ToT)** — 추론을 트리로 확장해 분기를 탐색·평가·백트래킹. 강력하지만 호출 수가 곱으로 증가. (S3)
- **Workflow** — LLM 호출 경로가 코드로 고정된 결정적 파이프라인. 흐름을 개발자가 통제(Agent의 반대편). (S1)

---

> 더 자세한 맥락은 각 용어 옆 (S#) 세션의 원페이지 요약·본문을 참고하세요.
