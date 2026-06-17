# 세션 07 해설 스크립트 — LangGraph: 상태 그래프 기반 에이전트

> 🎙️ 이 문서는 강사가 그대로 읽거나 참고해 설명할 수 있는 해설 대본입니다. 본문: [세션 7 강의 자료](session-07.html)

## [복습 · 5분] LCEL의 벽

🎙️ 시작하기 전에 한 문장만 챙겨갈게요. 세션 02의 그 `while` 루프는 사실 상태 머신이었어요. LangGraph는 그 상태 머신을 눈에 보이는 그래프로 그리게 해줘요. 오늘은 이 한 문장을 코드로 풀어가는 거예요.

지난 세션 06에서 LCEL 체인 `prompt | llm | parser`는 한 방향 파이프라고 했죠. 그런데 우리 리서치 어시스턴트는 본질적으로 루프예요. 화면 보시면, LLM에서 도구로 결과로, 다시 LLM으로 도구로 결과로, 이게 몇 번 돌지 모르는 채로 반복되다가 답으로 끝나죠.

쉽게 말하면 "몇 번 돌지 모름" 더하기 "도구를 쓸지 말지 매번 LLM이 결정", 이게 반복 더하기 조건분기예요. 직선 파이프로는 못 그려요. 세션 06의 `AgentExecutor`는 이 루프를 블랙박스 안에 숨겼어요. LangGraph는 그 루프를 밖으로 꺼내서 그래프로 명시해요. 숨겼던 걸 드러내는 거예요.

💬 예상 질문 — "AgentExecutor로 이미 돌아갔는데 왜 또 LangGraph예요?" AgentExecutor는 루프를 잘 숨겨주지만, 숨어 있어서 분기를 추가하거나 중간에 멈추거나 시각화하기가 어려워요. LangGraph는 그 흐름을 그림으로 꺼내 놓기 때문에 그런 일들이 쉬워져요. 오늘 그 차이를 보여드릴게요.

## [개념 강의 ① · 20분] 왜 그래프인가 + 핵심 개념 5종

🎙️ 먼저 "왜 그래프인가"부터요. 화면 표를 같이 봐요. 흐름 유형별로 LCEL 파이프랑 그래프를 비교한 거예요.

직선, A에서 B에서 C로 가는 건 파이프도 자연스럽고 그래프도 가능해요. 그런데 조건분기, A에서 B로 갈 수도 C로 갈 수도 있는 건 파이프로는 어색하고 그래프는 Conditional Edge로 깔끔하게 돼요. 반복, A에서 B에서 다시 A로 도는 건 파이프로는 아예 불가능하고 그래프는 사이클 엣지로 돼요. 중단하고 재개하는 것, 중간에 개입하는 것도 파이프는 안 되고 그래프는 체크포인트랑 Human-in-the-loop로 돼요.

쉽게 말하면 그래프는 "무엇을 하나"인 노드랑 "다음에 어디로 가나"인 엣지를 분리해요. 지하철 노선도 같은 거예요. 역이 노드고 역 사이 선로가 엣지죠. 그래서 도구를 쓸지 말지 같은 분기랑, 다시 LLM으로 돌아가는 반복을 선언적으로 표현할 수 있어요. 제어 흐름이 코드 안에 숨지 않고 그림으로 드러나요. 이게 핵심 가치예요.

자 이제 핵심 개념 5종을 볼게요. State, Node, Edge, Conditional Edge, 그리고 컴파일.

첫째, State. 그래프를 흐르는 단일 자료구조예요. 모든 노드가 읽고 쓰는 공유 상태죠. 세션 02의 `messages` 리스트가 여기로 승격돼요. 화면 코드 보시면 `AgentState`라는 TypedDict 안에 `messages: Annotated[list, add_messages]`가 있죠. 이 `add_messages`가 중요해요. 쉽게 말하면 "노드가 반환한 메시지를 덮어쓰지 말고 누적하라"는 규칙, reducer 지정이에요. 세션 02의 `messages.append`가 상태 정의로 올라온 거예요. 화이트보드 비유로 하면, 노드가 글을 쓸 때 칠판을 지우고 새로 쓰는 게 아니라 아래에 이어 쓰는 거예요.

둘째, Node. 상태를 받아서 상태를 갱신하는 함수예요. 화면 보시면 `call_model`이 `state["messages"]`로 LLM을 부르고 `{"messages": [response]}`를 반환하죠. 노드는 그냥 파이썬 함수예요. state를 받아서 갱신할 부분만 dict로 돌려줘요. 전체를 돌려주는 게 아니라 갱신분만요.

셋째, Edge. 노드 간 고정 연결이에요. `graph.add_edge("tools", "agent")`, 도구 실행 후엔 항상 agent로 가라. 고정된 선로예요.

넷째, Conditional Edge. 분기예요. 화면 보시면 `should_continue` 함수가 마지막 메시지에 tool_calls가 있으면 "tools"를, 없으면 "end"를 반환하죠. 그리고 `add_conditional_edges`로 그 결과에 따라 갈 곳을 매핑해요. 쉽게 말하면 "마지막 LLM 응답에 도구 호출이 있으면 tools로, 없으면 종료"예요. 세션 02의 `if resp.has_tool_call:`이 엣지로 외부화된 거예요. 코드 안에 숨어 있던 if가 그래프 위 갈림길로 나온 거죠.

다섯째, 컴파일. 그래프를 실행 가능한 객체로 만드는 거예요. `graph.compile(checkpointer=memory)`를 하면 검증하고 최적화하고 Runnable로 만들어줘요. 어, Runnable. 세션 06의 그 인터페이스가 다시 나왔죠? 그래서 컴파일된 그래프는 `.invoke`랑 `.stream`을 그대로 써요.

💬 예상 질문 — "reducer 없이 그냥 list 쓰면 안 돼요?" 안 돼요. reducer를 안 주면 노드 반환값이 상태를 덮어써요. 누적이 아니라요. 그러면 이전 도구 결과가 날아가서 루프가 망가져요. 세션 02의 `append`가 왜 reducer로 표현돼야 하는지, 바로 이거예요.

## [개념 강의 ② · 20분] while 루프 ↔ 그래프 대응, 제어 흐름

🎙️ 자 이제 그래프 그림을 우리 리서치 어시스턴트로 그려볼게요. 화면 다이어그램 보세요. START에서 agent 노드로 가고, agent에서 should_continue로 가서, tool_calls가 있으면 tools 노드로, 없으면 END로. 그리고 tools에서 다시 agent로 돌아오는 사이클 엣지가 있죠.

이 그래프에 세션 02 루프의 모든 부품이 다 보여요. agent 노드가 LLM 호출 ①, should_continue가 도구 파싱이랑 판단 ②와 ⑤의 조건, tools 노드가 도구 디스패치랑 실행 ③, 그리고 tools에서 agent로 가는 엣지가 결과 주입 후 반복 ④와 ⑤예요.

이제 오늘 세션의 심장이에요. while 루프랑 그래프를 1:1로 대응시켜 볼게요. 화면 대응표를 같이 읽어요. `messages = [...]`는 `AgentState.messages`에 add_messages 붙인 거. `while True:`는 사이클 엣지, tools에서 agent로. `resp = client.chat(msgs)`는 agent 노드, call_model. `if resp.has_tool_call:`은 conditional edge, should_continue. `result = TOOLS[name]()`은 tools 노드, ToolNode. `messages.append(result)`는 add_messages reducer가 누적. `continue`는 `add_edge("tools","agent")`. `else: return final`은 분기의 end 경로, END로.

쉽게 말하면 세션 02는 제어가 코드 안에 숨어 있었어요. 흐름이 `if`랑 `while`에 암묵적으로요. 세션 07은 제어가 그래프로 드러나요. 흐름이 노드랑 엣지로 명시적이에요. 그래서 중단이랑 재개를 직접 구현하던 걸 체크포인트가 공짜로 주고, 중간 개입이 어렵던 걸 interrupt로 Human-in-the-loop이 되고, 시각화가 없던 걸 `draw_mermaid()`로 그림 출력해요.

핵심 메시지는 이거예요. LangGraph는 새로운 마법이 아니에요. 세션 02의 상태 머신을 1급 시민으로 끌어올린 거예요. 같은 리서치 어시스턴트, 같은 도구 `web_search`랑 `calculator`, 표현만 그래프예요.

자 이제 그래프가 열어주는 제어 흐름 네 가지를 볼게요.

첫째, 분기. Conditional Edge죠. "도구를 쓸까 답을 낼까"뿐 아니라 "어떤 도구로 갈까", "재시도할까 포기할까"도 분기 함수로 표현해요. 여기서 재밌는 비교가 있어요. 화면에 같은 분기를 두 가지로 표현한 다이어그램 보세요. 왼쪽은 노드 내부 `if`예요. 분기가 agent 노드 코드 안에 숨어 있죠. 그래프엔 엣지가 하나만 보여요. 제어 흐름이 불투명해요. 오른쪽은 Conditional Edge예요. agent에서 should_continue로 가서 tools냐 END냐 갈래가 그대로 드러나죠.

표로 정리하면, 노드 내부 if는 분기가 노드 코드 안에 캡슐화되고 그래프엔 엣지 1개만 보이고 디버깅이랑 HITL이랑 재사용이 어려워요. Conditional Edge는 분기가 그래프 위 엣지에 있고 갈래가 그대로 보이고 디버깅이 쉬워요. 두 표현은 동작이 같아요. 그런데 conditional edge는 제어 흐름을 그래프로 외부화해서 디버깅이랑 HITL이랑 재사용이 쉬워요. 노드 내부 if는 캡슐화는 되지만 흐름이 숨어서 그래프만 봐선 갈래를 알 수 없어요.

둘째, 반복. 사이클이에요. `tools → agent` 엣지가 사이클을 만들죠. 무한 루프 방지는 `recursion_limit`로 해요. 세션 02의 "최대 step 수"가 컴파일 옵션으로 승격된 거예요.

셋째, 체크포인트. Checkpointer예요. 화면 보시면 `compile(checkpointer=MemorySaver())`로 컴파일하고, `invoke`할 때 `config`에 `thread_id`를 줘요. 각 노드 실행 후 상태를 저장해서, 중단된 대화를 thread_id로 재개할 수 있어요. 비유하면 게임 세이브 포인트예요. 그리고 이게 세션 04 메모리랑 직접 연결돼요. thread_id가 곧 그 대화의 기억 보따리인 셈이죠.

넷째, Human-in-the-loop, 개입지점이에요. `interrupt_before=["tools"]`로 컴파일하면, 도구를 실행하기 직전에 멈춰서 사람의 승인을 받아요. 화면 다이어그램 보시면 agent에서 tool_calls가 나오면 interrupt에서 멈추고, 승인하면 tools로, 거부하면 END로, 수정 후 재개도 가능하죠. 결제나 삭제 같은 위험한 도구 앞에 게이트를 세우는 표준 패턴이에요.

💬 예상 질문 — "노드 내부 if랑 Conditional Edge, 동작 같으면 아무거나 써도 되죠?" 동작은 같아요. 그런데 conditional edge로 빼면 분기가 그래프에 드러나서 나중에 디버깅하거나, 그 지점에서 사람 승인을 받거나, 재사용하기가 훨씬 쉬워요. 토론 질문의 "재시도 분기"도 결국 분기를 어디에 둘지의 문제예요.

## [데모 · 25분] `demos/03_langgraph_agent.py` — ReAct 에이전트 시각화·추적

🎙️ 자 이제 데모예요. 세션 02랑 05랑 동일한 리서치 어시스턴트인데, 이번엔 그래프로 그리고 실행을 시각화하고 추적할 거예요.

먼저 상태랑 도구. 화면 보시면 `AgentState`에 `messages: Annotated[list, add_messages]`가 있고, `@tool`로 `web_search`랑 `calculator`를 정의하고, `tools` 리스트를 만들고, `llm.bind_tools(tools)`로 도구를 묶어요. 아까 본 부품들이 그대로 코드로 나온 거죠.

다음 노드 정의. `agent_node`는 `llm_with_tools.invoke(state["messages"])`의 결과를 `{"messages": [...]}`로 반환해요. `should_continue`는 마지막 메시지에 tool_calls가 있으면 "tools", 없으면 END를 반환하고요. 그리고 `tool_node = ToolNode(tools)`. 도구 디스패치를 프레임워크가 제공해요. 세션 02에서 손으로 짜던 `TOOLS[name](**args)`가 이 ToolNode 한 줄로 끝나요.

그래프 조립이랑 컴파일. 화면 보세요. `StateGraph(AgentState)`로 그래프를 만들고, agent 노드랑 tools 노드를 추가하고, START에서 agent로 엣지를 걸고, agent에서 should_continue로 conditional edge를 걸고, 그리고 `add_edge("tools", "agent")`. 이 마지막 줄이 사이클, 반복이에요. 그리고 `g.compile()`로 컴파일.

자 이제 시각화랑 추적 실행이에요. `app.get_graph().draw_ascii()`로 그래프 그림을 출력해요. 칠판이나 슬라이드에 그대로 쓸 수 있어요. 그리고 `app.stream`으로 각 노드 통과를 추적해요. 질문은 똑같죠. "2024년 노벨 물리학상 수상자가 누구이고, 받은 상금을 3으로 나누면 얼마야?"

stream 출력을 보면 순서가 이렇게 찍혀요. agent가 web_search 호출을 결정하고, tools가 web_search를 실행하고, agent가 수상자를 파악한 다음 calculator를 결정하고, tools가 calculator로 `11000000 / 3`을 실행하고, 마지막에 agent가 최종 자연어 답을 내요. agent에서 tools로 agent로 tools로 agent로, 그리고 END까지가 순서대로 보여요.

여기서 꼭 짚을 게 있어요. 이 그래프 경로가 demo-task-spec의 표준 시나리오 기대 흐름, 1에서 2에서 3에서 4로 가는 그 흐름이랑 정확히 일치해요. 세션 06에서 verbose 로그로 봤던 그 ①부터 ⑤까지의 흐름이, 이번엔 그래프 경로로 눈에 보이게 그려진 거예요. 같은 본질, 더 투명한 표현이죠.

💬 예상 질문 — "이게 세션 02 while 루프랑 결국 같은 거면 왜 굳이 LangGraph를 써요?" 같은 본질 맞아요. 그런데 그래프는 네 가지를 공짜로 줘요. 하나, 시각화. 둘, 체크포인트랑 재개. 셋, Human-in-the-loop. 넷, 분기 추가의 용이함. raw 루프에 이걸 다 직접 넣으면, 결국 LangGraph를 재발명하게 돼요. 추상화 뒤를 아는 사람이 그래프를 쓰면 강력하다는 게 결론이에요.

## [토론 · 15분] 우리 워크플로를 노드/엣지로 모델링

🎙️ 마지막으로 같이 손으로 그려보는 시간이에요. 토론 질문 몇 개 던질게요.

첫째, 세션 02의 `while`이랑 `if`를, LangGraph의 사이클 엣지랑 conditional edge랑 비교해보세요. 제어 흐름이 "코드 안에 숨는 것"과 "그래프로 드러나는 것"의 실무적 차이가 뭘까요? 아까 노드 내부 if 대 Conditional Edge 비교가 힌트예요.

둘째, 우리 리서치 어시스턴트에 "검색 결과가 비면 다른 쿼리로 재시도"를 추가한다면, 어떤 노드랑 엣지를 더해야 할까요? 직접 그림으로 그려보세요. 어디에 분기를 두느냐가 관건이에요.

셋째, `interrupt_before=["tools"]`로 calculator는 그냥 통과시키되 web_search만 사람 승인을 받게 하려면 그래프를 어떻게 바꿔야 할까요? 도구마다 게이트가 달라야 하는 상황이죠.

넷째, 체크포인터의 `thread_id`는 세션 04에서 배운 장기 단기 메모리랑 어떻게 연결될까요? 아까 세이브 포인트 비유 기억하시죠.

다섯째, 여러분 실무 워크플로 하나를 골라서 노드랑 엣지랑 분기랑 사이클로 모델링해 보세요. 어디가 분기고 어디가 반복인가요?

💬 예상 질문 — "LangGraph는 LangChain 상위호환이라 LCEL을 대체하는 거죠?" 아니에요. 둘은 층위가 달라요. LCEL은 직선 데이터 변환이고, LangGraph는 상태 있는 제어 흐름이에요. 그리고 노드 내부에서는 여전히 LCEL 체인을 써요. 대체가 아니라 보완 관계예요.

🎙️ 오늘 정리하면, 왜 순환이랑 조건분기 흐름에 그래프가 적합한지, State와 Node와 Edge와 Conditional Edge와 컴파일을 구분하는 것, 세션 02의 while 루프를 노드랑 엣지로 1:1 대응시키는 것, Conditional Edge랑 노드 내부 if의 차이 즉 제어 흐름의 외부화, 그리고 Checkpointer랑 interrupt로 영속화랑 Human-in-the-loop을 설계하는 것까지 봤어요. 다음 시간 세션 08에서는 단일 에이전트 그래프를 넘어서, 여러 에이전트가 협업하는 Multi-Agent 시스템을 다뤄요. 노드 하나가 또 다른 그래프가 되는 거예요. 수고하셨습니다.
