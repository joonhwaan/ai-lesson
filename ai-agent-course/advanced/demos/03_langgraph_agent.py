"""
================================================================================
 세션 6 데모: LangGraph 로 구현한 동일한 리서치 어시스턴트
================================================================================

이 파일은 세션 2(raw 루프) / 세션 5(LangChain)와 **완전히 동일한 토이 태스크**를
LangGraph 의 상태 그래프(State Graph)로 다시 구현한 것이다.
(명세: shared/demo-task-spec.md — "리서치 어시스턴트"가 진화하는 모습)

  세션 2: 직접 짠 while 루프      → 루프의 본질
  세션 5: LangChain             → 추상화가 무엇을 감추는가
  세션 6: LangGraph (이 파일)    → "루프 = 상태 그래프"  ★

★ 핵심 통찰: FILE 1 의 while 루프를 "그래프"로 펼친 것이 LangGraph 다.
  - State(messages)         = FILE 1 의 messages 리스트 (대화/도구결과 누적)
  - agent 노드              = FILE 1 의 call_model() 호출
  - tools 노드              = FILE 1 의 dispatch_tool() (도구 실행)
  - should_continue 엣지    = FILE 1 의 "tool_calls 있나?" 분기 (= 정지 조건)
  - tools → agent 로 되돌아가는 엣지 = while 루프가 "다시 위로" 가는 것
  - END 로 가는 엣지        = FILE 1 의 return final_text (루프 탈출)

┌────────────────── 그래프 구조 (ASCII) ──────────────────┐
│                                                          │
│   START                                                  │
│     │                                                    │
│     ▼                                                    │
│  ┌───────┐   should_continue                             │
│  │ agent │──────────────┐                                │
│  └───────┘              │                                │
│     ▲                   ▼                                │
│     │            ┌─────────────┐                         │
│     │  (yes:     │ tool 호출?   │                         │
│     │   도구실행 후 │             │                         │
│     │   되돌아옴)  └──┬───────┬──┘                         │
│     │               │ yes   │ no                         │
│     │               ▼       ▼                            │
│     │           ┌───────┐  END  (최종 텍스트 → 종료)       │
│     └───────────│ tools │                                │
│                 └───────┘                                │
│                                                          │
└──────────────────────────────────────────────────────────┘

────────────────────────────────────────────────────────────────────────────
 참고: 실행하려면 아래 패키지가 필요하다 (이 강의 환경엔 없을 수 있음).
   pip install langgraph langchain-openai
 그리고 OPENAI_API_KEY 환경변수가 있어야 실제 모델 호출이 된다.
 패키지가 없으면 import 단계에서 안내 메시지를 출력하고 종료한다.
────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import math
from typing import Annotated, TypedDict

# ──────────────────────────────────────────────────────────────────────────
# import 가드: LangGraph 미설치 환경에서도 파일이 컴파일/읽기 가능하도록 보호.
# ──────────────────────────────────────────────────────────────────────────
try:
    from langchain_core.messages import BaseMessage, ToolMessage
    from langchain_core.tools import tool
    from langchain_openai import ChatOpenAI
    from langgraph.graph import END, START, StateGraph
    from langgraph.graph.message import add_messages

    LANGGRAPH_AVAILABLE = True
except ImportError:  # pragma: no cover - 미설치 환경 안내용
    LANGGRAPH_AVAILABLE = False

    # 미설치 환경에서도 타입 힌트/데코레이터가 깨지지 않도록 더미를 둔다.
    def tool(func):  # type: ignore
        return func

    def add_messages(a, b):  # type: ignore
        return (a or []) + (b or [])

    BaseMessage = object  # type: ignore


# ==============================================================================
# 1) 도구 정의 — FILE 1/2 와 동일 (명세의 web_search / calculator)
# ==============================================================================
@tool
def web_search(query: str) -> list[dict]:
    """주어진 검색어로 웹을 검색해 상위 결과 스니펫을 반환한다.

    Args:
        query: 검색어
    """
    # [MOCK] 고정 결과 — API 키 없이 강의 가능.
    return [
        {
            "title": "2024 Nobel Prize in Physics",
            "snippet": (
                "The 2024 Nobel Prize in Physics was awarded to John J. Hopfield "
                "and Geoffrey E. Hinton for foundational discoveries enabling "
                "machine learning with artificial neural networks. The prize "
                "amount was 11,000,000 SEK."
            ),
            "url": "https://www.nobelprize.org/prizes/physics/2024/summary/",
        }
    ]


@tool
def calculator(expression: str) -> dict:
    """수식 문자열을 계산해 결과를 반환한다 (예: '1234 * 5.5').

    Args:
        expression: 계산할 수식 문자열
    """
    # [REAL] 안전 eval (FILE 1/2 와 동일).
    allowed_names = {
        name: getattr(math, name) for name in dir(math) if not name.startswith("_")
    }
    allowed_names.update({"abs": abs, "round": round, "min": min, "max": max})
    result = eval(expression, {"__builtins__": {}}, allowed_names)  # noqa: S307
    return {"result": float(result)}


TOOLS = [web_search, calculator]
# 이름 → 도구 매핑. FILE 1 의 TOOL_REGISTRY 와 같은 역할(도구 디스패치).
TOOLS_BY_NAME = {t.name: t for t in TOOLS} if LANGGRAPH_AVAILABLE else {}


# ==============================================================================
# 2) State 정의 — TypedDict
# ==============================================================================
# State 는 그래프의 노드들이 공유하며 갱신하는 "메모리"다.
# messages 하나만 둔다 = FILE 1 의 messages 리스트와 동일한 개념.
# Annotated[..., add_messages] 는 "새 메시지는 덮어쓰지 말고 누적(append)하라"
# 는 리듀서 지정이다. (FILE 1 에서 messages.append(...) 하던 것을 자동화)
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


# ==============================================================================
# 3) 노드(Node) 정의
# ==============================================================================
def build_graph():
    """리서치 어시스턴트 상태 그래프를 빌드해 반환한다."""

    # 모델에 도구 스키마를 bind = FILE 1 에서 call_model(messages, TOOLS_SCHEMA)
    # 호출 시 tools 를 넘기던 것에 해당.
    llm = ChatOpenAI(model="gpt-4o", temperature=0).bind_tools(TOOLS)

    # ── agent 노드: 모델을 호출한다 (FILE 1 의 call_model). ──────────────────
    def agent_node(state: AgentState) -> dict:
        # 현재까지의 메시지를 모델에 넘겨 "다음 행동"(도구 호출 or 최종 답)을 받는다.
        response = llm.invoke(state["messages"])
        # 반환값은 State 의 messages 에 '누적'된다 (add_messages 리듀서 덕분).
        return {"messages": [response]}

    # ── tools 노드: 도구를 실행한다 (FILE 1 의 dispatch_tool 루프). ──────────
    def tool_node(state: AgentState) -> dict:
        last = state["messages"][-1]  # 직전 assistant 메시지(도구 호출 포함)
        tool_messages = []
        for call in last.tool_calls:  # 모델이 요청한 도구 호출들
            selected = TOOLS_BY_NAME[call["name"]]
            observation = selected.invoke(call["args"])
            # 도구 결과를 ToolMessage 로 만들어 State 에 추가
            # (FILE 1 에서 role="tool" 메시지를 messages 에 append 하던 것).
            tool_messages.append(
                ToolMessage(content=str(observation), tool_call_id=call["id"])
            )
        return {"messages": tool_messages}

    # ── 조건부 엣지: 계속할지 멈출지 결정 (FILE 1 의 정지 조건). ─────────────
    def should_continue(state: AgentState) -> str:
        last = state["messages"][-1]
        # 직전 assistant 메시지에 도구 호출이 있으면 → tools 노드로 (계속)
        # 없으면(=최종 텍스트) → END (종료). 명세의 stop condition 과 동일.
        if getattr(last, "tool_calls", None):
            return "tools"
        return END

    # ── 그래프 조립 ─────────────────────────────────────────────────────────
    graph = StateGraph(AgentState)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", tool_node)

    graph.add_edge(START, "agent")  # 시작 → agent
    # agent 다음은 should_continue 결과에 따라 분기:
    #   "tools" → 도구 실행,  END → 종료
    graph.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
    graph.add_edge("tools", "agent")  # 도구 실행 후 다시 agent 로 (= while 루프 반복!)

    # recursion_limit 이 FILE 1 의 MAX_TURNS 안전장치 역할을 한다(실행 시 설정).
    return graph.compile()


# ==============================================================================
# 4) 실행 진입점 — 명세의 표준 시나리오
# ==============================================================================
def run() -> None:
    STANDARD_SCENARIO = (
        "2024년 노벨 물리학상 수상자가 누구이고, 그 사람들 수가 받은 상금을 "
        "3으로 나누면 얼마야?"
    )

    if not LANGGRAPH_AVAILABLE:
        print("[안내] LangGraph 미설치 — 실행하려면 다음을 설치하세요:")
        print("       pip install langgraph langchain-openai")
        print("       그리고 OPENAI_API_KEY 환경변수를 설정하세요.")
        return

    from langchain_core.messages import HumanMessage, SystemMessage

    app = build_graph()
    initial_state = {
        "messages": [
            SystemMessage(
                content=(
                    "너는 리서치 어시스턴트다. 필요하면 web_search 와 calculator "
                    "도구를 사용해 답하고, 마지막에 한국어로 요약해 답하라."
                )
            ),
            HumanMessage(content=STANDARD_SCENARIO),
        ]
    }

    # stream 으로 각 노드 실행을 단계별로 출력 → FILE 1 의 turn 트레이스와 유사.
    # recursion_limit=12 ≈ MAX_TURNS(6) * 2 (agent+tools 노드 쌍 기준).
    for step in app.stream(initial_state, config={"recursion_limit": 12}):
        for node_name, node_output in step.items():
            print(f"===== NODE: {node_name} =====")
            for msg in node_output["messages"]:
                print(msg)
            print()


if __name__ == "__main__":
    run()
