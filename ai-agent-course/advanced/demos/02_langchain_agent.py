"""
================================================================================
 세션 6 데모: LangChain 으로 구현한 동일한 리서치 어시스턴트
================================================================================

이 파일은 세션 2(01_raw_agent_loop.py)와 **완전히 동일한 토이 태스크**를
LangChain 의 tool-calling 에이전트로 다시 구현한 것이다.
(명세: shared/demo-task-spec.md — "리서치 어시스턴트"가 진화하는 모습)

  세션 2: 직접 짠 while 루프            → 루프의 본질
  세션 6: LangChain (이 파일)           → "추상화가 무엇을 감추는가"  ★
  세션 7: LangGraph                     → 루프 = 상태 그래프

★ 이 파일의 학습 포인트 — LangChain 이 "감추는" 것:
  - while 루프 자체            : AgentExecutor 가 내부적으로 돌린다.
  - messages 기록 관리         : 에이전트가 중간 단계(scratchpad)를 알아서 쌓는다.
  - 도구 디스패치(name→func)   : @tool 로 등록하면 LangChain 이 이름으로 찾아 실행.
  - 정지 조건 판단             : 모델이 도구를 더 안 부르면 AgentExecutor 가 종료.
  FILE 1 에서 손으로 짰던 그 코드들이 여기서는 전부 프레임워크 뒤로 사라진다.

────────────────────────────────────────────────────────────────────────────
 참고: 실행하려면 아래 패키지가 필요하다 (이 강의 환경엔 없을 수 있음).
   pip install langchain langchain-openai
 그리고 OPENAI_API_KEY 환경변수가 있어야 실제 모델 호출이 된다.
 패키지가 없으면 import 단계에서 안내 메시지를 출력하고 종료한다.
────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import math

# ──────────────────────────────────────────────────────────────────────────
# import 가드: LangChain 미설치 환경에서도 파일이 "읽기/컴파일" 가능하도록 보호.
# (강의에서는 코드를 읽으며 트레이스하는 게 목적이라 실행이 필수는 아니다.)
# ──────────────────────────────────────────────────────────────────────────
try:
    from langchain.agents import AgentExecutor, create_tool_calling_agent
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.tools import tool
    from langchain_openai import ChatOpenAI

    LANGCHAIN_AVAILABLE = True
except ImportError:  # pragma: no cover - 미설치 환경 안내용
    LANGCHAIN_AVAILABLE = False

    # @tool 데코레이터가 없어도 아래 함수 정의가 깨지지 않도록 no-op 더미를 둔다.
    def tool(func):  # type: ignore
        return func


# ==============================================================================
# 1) 도구 정의 — @tool 데코레이터
# ==============================================================================
# FILE 1 에서는 TOOLS_SCHEMA(JSON) 를 손으로 작성했지만, LangChain 은 함수의
# 시그니처 + docstring 을 읽어 스키마를 "자동 생성" 한다. 이것도 추상화의 일부.
# 도구 이름·시그니처는 명세(web_search / calculator)를 그대로 따른다.

@tool
def web_search(query: str) -> list[dict]:
    """주어진 검색어로 웹을 검색해 상위 결과 스니펫을 반환한다.

    Args:
        query: 검색어
    """
    # [MOCK] API 키 없이 강의 가능하도록 고정 결과 반환 (FILE 1 과 동일한 스니펫).
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
    # [REAL] FILE 1 과 동일한 안전 eval (builtins 제거 + math 함수만 허용).
    allowed_names = {
        name: getattr(math, name) for name in dir(math) if not name.startswith("_")
    }
    allowed_names.update({"abs": abs, "round": round, "min": min, "max": max})
    result = eval(expression, {"__builtins__": {}}, allowed_names)  # noqa: S307
    return {"result": float(result)}


# ==============================================================================
# 2) 에이전트 구성 + 실행
# ==============================================================================
def build_agent() -> "AgentExecutor":
    """LangChain tool-calling 에이전트를 구성한다.

    여기서 만들어지는 AgentExecutor 가 곧 FILE 1 의 while 루프에 해당한다.
    """
    # (a) 모델: FILE 1 의 call_model 자리. LangChain 이 tool 스키마 주입/파싱을 담당.
    llm = ChatOpenAI(model="gpt-4o", temperature=0)

    # (b) 프롬프트: system 역할 + 대화 + agent_scratchpad(중간 도구 호출 기록 자리).
    #     agent_scratchpad 가 바로 FILE 1 에서 messages 에 도구 결과를 append 하던
    #     부분을 LangChain 이 자동으로 채워주는 슬롯이다.
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "너는 리서치 어시스턴트다. 필요하면 web_search 와 calculator "
                "도구를 사용해 답하고, 마지막에 한국어로 요약해 답하라.",
            ),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ]
    )

    tools = [web_search, calculator]

    # (c) 에이전트 = 모델 + 도구 + 프롬프트. "다음에 뭘 할지" 결정하는 두뇌.
    agent = create_tool_calling_agent(llm, tools, prompt)

    # (d) AgentExecutor = FILE 1 의 while 루프 + 도구 디스패치 + 정지 조건.
    #     verbose=True 면 FILE 1 의 print 트레이스처럼 각 단계를 출력해 준다.
    #     max_iterations 가 FILE 1 의 MAX_TURNS 안전장치에 대응한다.
    return AgentExecutor(agent=agent, tools=tools, verbose=True, max_iterations=6)


def run() -> None:
    """명세의 표준 시나리오로 에이전트를 실행한다."""
    STANDARD_SCENARIO = (
        "2024년 노벨 물리학상 수상자가 누구이고, 그 상금을 "
        "3으로 나누면 얼마야?"
    )

    if not LANGCHAIN_AVAILABLE:
        print("[안내] LangChain 미설치 — 실행하려면 다음을 설치하세요:")
        print("       pip install langchain langchain-openai")
        print("       그리고 OPENAI_API_KEY 환경변수를 설정하세요.")
        return

    executor = build_agent()
    # invoke 한 번이 FILE 1 의 run_agent() 전체(while 루프 끝까지)에 해당한다.
    result = executor.invoke({"input": STANDARD_SCENARIO})
    print("\n[FINAL]\n" + result["output"])


if __name__ == "__main__":
    run()
