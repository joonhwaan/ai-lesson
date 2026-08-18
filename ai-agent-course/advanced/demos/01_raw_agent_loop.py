"""
================================================================================
 세션 2 데모: 프레임워크 없는 "날것(raw)"의 에이전트 루프
================================================================================

이 파일은 강의 전체를 관통하는 동일한 토이 태스크 — "리서치 어시스턴트
(Research Assistant)" — 를 **아무 프레임워크도 없이** 순수 Python while 루프로
구현한 것이다. (명세: shared/demo-task-spec.md)

  세션 2: raw OpenAI/Claude API + while 루프  → 에이전트 루프의 "본질"
  세션 6: LangChain                          → 추상화가 무엇을 감추는가
  세션 7: LangGraph                          → 루프 = 상태 그래프

이 파일에서 학생이 봐야 할 핵심:
  1) 에이전트 루프의 정체 = "모델 호출 → 도구 호출이면 실행 → 결과를 메시지에
     덧붙임 → 다시 모델 호출 → 더 이상 도구를 안 부르면 종료" 의 while 루프.
  2) 메시지 기록(messages) 관리, 도구 디스패치, 정지 조건을 "직접" 손으로 짠다.
  3) 세션 6/7에서 LangChain·LangGraph가 "감추는" 것이 바로 이 코드라는 점.

이 파일은 모델 호출을 MOCK 으로 대체했기 때문에 API 키 없이 그대로 실행된다.
실제 API로 바꾸는 방법은 call_model() 아래 주석 참고.
================================================================================
"""

import json
import math
from typing import Any


# ==============================================================================
# 1) 도구 스키마(JSON) 정의  —  명세의 tool 정의를 그대로 사용
# ==============================================================================
# OpenAI / Claude 의 tool-calling 은 "이런 도구가 있다"를 JSON 스키마로 모델에게
# 알려준다. 모델은 이 스키마를 보고 어떤 도구를 어떤 인자로 부를지 스스로 정한다.
# (아래는 OpenAI function-calling 포맷 기준. Claude 도 거의 동일한 구조.)
TOOLS_SCHEMA: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "주어진 검색어로 웹을 검색해 상위 결과 스니펫을 반환한다",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "검색어",
                    }
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "수식 문자열을 계산해 결과를 반환한다 (예: '1234 * 5.5')",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "계산할 수식 문자열",
                    }
                },
                "required": ["expression"],
            },
        },
    },
]


# ==============================================================================
# 2) 실제 도구 구현
# ==============================================================================

def web_search(query: str) -> list[dict[str, str]]:
    """[MOCK] 웹 검색 도구.

    실제로는 검색 API(Bing/Google/Tavily 등)를 호출하지만, 강의에서는 API 키
    없이 돌아가도록 '고정 결과'를 반환한다. 명세의 표준 시나리오(2024 노벨
    물리학상)에 맞는 스니펫을 돌려준다.
    """
    # 데모이므로 query 내용과 무관하게 고정 결과를 반환한다.
    # (실전이라면 query 로 실제 검색을 수행한다.)
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


def calculator(expression: str) -> dict[str, float]:
    """[REAL] 계산기 도구 — 안전한 eval.

    파이썬 eval 은 위험하므로, __builtins__ 을 제거하고 math 모듈 함수만
    허용한 '샌드박스'에서 평가한다. (강의용 수준의 안전장치)
    """
    # 허용할 이름만 노출 (math 의 안전한 함수들 + 기본 수치 연산)
    allowed_names: dict[str, Any] = {
        name: getattr(math, name) for name in dir(math) if not name.startswith("_")
    }
    allowed_names.update({"abs": abs, "round": round, "min": min, "max": max})
    # __builtins__ 를 비워 임의 코드 실행을 차단한다.
    result = eval(expression, {"__builtins__": {}}, allowed_names)  # noqa: S307
    return {"result": float(result)}


# 도구 이름 → 실제 함수 매핑 (도구 디스패치 테이블).
# 모델이 "web_search 불러줘" 라고 하면 여기서 실제 함수를 찾아 실행한다.
TOOL_REGISTRY = {
    "web_search": web_search,
    "calculator": calculator,
}


def dispatch_tool(name: str, arguments: dict[str, Any]) -> Any:
    """모델이 요청한 도구 이름/인자를 받아 실제 함수를 실행한다."""
    if name not in TOOL_REGISTRY:
        return {"error": f"unknown tool: {name}"}
    func = TOOL_REGISTRY[name]
    return func(**arguments)


# ==============================================================================
# 3) 모델 호출  —  MOCK 구현 (스크립트된 시나리오)
# ==============================================================================
# 실제 모델은 messages + tools 를 받아 "다음에 무엇을 할지"를 정한다:
#   - 도구를 부르고 싶으면 tool_calls 를 담아 응답
#   - 끝났으면 최종 텍스트(content)를 응답
#
# 강의에서 API 키 없이도 루프가 끝까지 돌도록, 명세의 "표준 시나리오"를
# 그대로 흉내내는 스크립트된 응답을 단계별로 반환한다.
#
# ── 실제 API로 바꾸는 방법 (요지) ───────────────────────────────────────────
#   [OpenAI]
#     from openai import OpenAI
#     client = OpenAI()  # 환경변수 OPENAI_API_KEY 사용
#     def call_model(messages, tools):
#         resp = client.chat.completions.create(
#             model="gpt-4o", messages=messages, tools=tools)
#         return resp.choices[0].message  # tool_calls 또는 content 를 가짐
#
#   [Claude / Anthropic]
#     from anthropic import Anthropic
#     client = Anthropic()  # 환경변수 ANTHROPIC_API_KEY 사용
#     # Claude 는 tool schema/응답 포맷이 약간 다르므로 변환 레이어 필요
# ─────────────────────────────────────────────────────────────────────────────

# MOCK 응답이 몇 번째 호출인지 추적하는 카운터.
_mock_step = 0


def call_model(messages: list[dict[str, Any]], tools: list[dict[str, Any]]) -> dict[str, Any]:
    """[MOCK] 모델 호출.

    반환 형식은 OpenAI 의 assistant 메시지 모양을 단순화한 dict:
      - 도구 호출:  {"role": "assistant", "content": None,
                     "tool_calls": [{"id", "name", "arguments"}]}
      - 최종 답변:  {"role": "assistant", "content": "...", "tool_calls": None}

    명세의 표준 시나리오대로 3단계 응답을 순서대로 돌려준다:
      step 0: web_search 호출
      step 1: calculator 호출
      step 2: 최종 텍스트 답변 (도구 호출 없음 → 루프 종료)
    """
    global _mock_step
    step = _mock_step
    _mock_step += 1

    if step == 0:
        # 1단계: 수상자를 찾기 위해 웹 검색을 요청한다.
        return {
            "role": "assistant",
            "content": None,
            "tool_calls": [
                {
                    "id": "call_1",
                    "name": "web_search",
                    "arguments": {"query": "2024 Nobel Prize physics winners"},
                }
            ],
        }

    if step == 1:
        # 2단계: 검색 결과에서 상금(11,000,000)을 확인하고 3으로 나눈다.
        return {
            "role": "assistant",
            "content": None,
            "tool_calls": [
                {
                    "id": "call_2",
                    "name": "calculator",
                    "arguments": {"expression": "11000000 / 3"},
                }
            ],
        }

    # 3단계: 더 이상 도구가 필요 없으므로 최종 자연어 답변을 반환 → 루프 종료.
    return {
        "role": "assistant",
        "content": (
            "2024년 노벨 물리학상은 John J. Hopfield 와 Geoffrey E. Hinton 이 "
            "인공 신경망 기반 머신러닝의 기초를 마련한 공로로 공동 수상했습니다. "
            "상금은 11,000,000 SEK 였고, 이를 3으로 나누면 약 3,666,666.67 SEK 입니다."
        ),
        "tool_calls": None,
    }


# ==============================================================================
# 4) 에이전트 루프 (명세의 "에이전트 루프 패턴" 그대로)
# ==============================================================================
# while:
#   모델 호출 → 도구 호출이 있으면 실행하고 결과를 messages 에 덧붙임 →
#   다시 모델 호출 → 도구 호출이 없으면(=최종 텍스트) 종료.
# 안전장치: MAX_TURNS 초과 시 강제 종료.
MAX_TURNS = 6  # 명세의 안전장치 값


def run_agent(user_question: str) -> str:
    """리서치 어시스턴트 에이전트를 한 번 실행한다."""
    # 대화 기록. system 으로 역할을 주고, user 로 질문을 넣는다.
    messages: list[dict[str, Any]] = [
        {
            "role": "system",
            "content": (
                "너는 리서치 어시스턴트다. 필요하면 web_search 와 calculator "
                "도구를 사용해 답하고, 마지막에 한국어로 요약해 답하라."
            ),
        },
        {"role": "user", "content": user_question},
    ]

    print(f"[USER] {user_question}\n")

    for turn in range(1, MAX_TURNS + 1):
        print(f"===== TURN {turn} =====")

        # (1) 모델 호출 — "이번엔 도구를 부를까, 끝낼까?"
        assistant_msg = call_model(messages, TOOLS_SCHEMA)
        messages.append(assistant_msg)

        tool_calls = assistant_msg.get("tool_calls")

        # (2) 정지 조건: 도구 호출이 없으면 = 최종 텍스트 → 종료
        if not tool_calls:
            final_text = assistant_msg["content"]
            print(f"[ASSISTANT - FINAL]\n{final_text}\n")
            return final_text

        # (3) 도구 호출이 있으면 각각 실행하고 결과를 messages 에 덧붙인다.
        for call in tool_calls:
            name = call["name"]
            args = call["arguments"]
            print(f"[MODEL → TOOL] {name}({json.dumps(args, ensure_ascii=False)})")

            result = dispatch_tool(name, args)
            print(f"[TOOL → MODEL] {json.dumps(result, ensure_ascii=False)}\n")

            # 도구 실행 결과를 'tool' 역할 메시지로 기록 → 다음 모델 호출이 본다.
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call["id"],
                    "name": name,
                    "content": json.dumps(result, ensure_ascii=False),
                }
            )
        # 루프 처음으로 돌아가 다시 모델을 호출한다.

    # 안전장치: MAX_TURNS 를 넘기면 강제 종료.
    print("[STOP] MAX_TURNS 초과 — 강제 종료")
    return "최대 루프 횟수를 초과하여 종료되었습니다."


# ==============================================================================
# 5) 실행 진입점 — 명세의 "표준 시나리오"
# ==============================================================================
if __name__ == "__main__":
    STANDARD_SCENARIO = (
        "2024년 노벨 물리학상 수상자가 누구이고, 그 상금을 "
        "3으로 나누면 얼마야?"
    )
    print("=" * 70)
    print(" RAW 에이전트 루프 데모 (프레임워크 없음)")
    print("=" * 70 + "\n")
    run_agent(STANDARD_SCENARIO)
