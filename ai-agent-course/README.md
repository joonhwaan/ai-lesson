# AI Agent 개발 강의 (4주 × 2회 = 총 8세션)

중상급 개발자 대상 · 이론/개념 중심 · 세션당 1~1.5시간

> 원리(raw API) → 추상화(LangChain/LangGraph) → 운영(멀티에이전트·평가)으로 점진 심화.
> 전 과정이 하나의 토이 태스크("리서치 어시스턴트")로 이어진다. → [advanced/shared/demo-task-spec.md](advanced/shared/demo-task-spec.md)

## 📺 HTML 사이트 (보기/설명용 — 추천)
브라우저로 강의 자료를 보고, **브라우저에서 직접 Python 데모를 실행**할 수 있습니다.

- **열기**: 통합 포털 `index.html`(또는 `advanced/site/index.html`)을 더블클릭. 인터넷 연결 필요(렌더링·Pyodide CDN).
- **다시 빌드**(md/코드 수정 후): `python advanced/site/build.py`
- **Python 플레이그라운드**: `advanced/site/playground.html` — `01_raw_agent_loop.py`를 브라우저에서 수정·실행하며 에이전트 루프 trace를 관찰. (`02`/`03`은 langchain/langgraph 필요로 읽기 전용)

> 정적 사이트라 별도 서버 없이 `file://`로 동작합니다. 마크다운은 페이지에 내장(embed)되어 렌더링되므로 CORS 문제가 없습니다.

## 폴더 구조
입문·심화 두 과정이 대칭으로 묶이고, 디자인 시스템은 `shared-assets/`가 단일 소스다.
```
ai-agent-course/
├─ README.md               ← 이 파일 (전체 인덱스)
├─ index.html              ← 통합 포털 (입문+심화 진입점, 생성물)
├─ graph.html              ← 지식 그래프 (생성물)
├─ shared-assets/          ← 공통 디자인 시스템 단일 소스 (style.css, app.js, DESIGN.md)
├─ advanced/               ← 심화 8주 과정
│  ├─ sessions/            ← 세션별 상세 강의 자료(8개, 원본 md)
│  ├─ shared/              ← 공유 기준 예제 명세 (demo-task-spec.md)
│  ├─ demos/               ← 진화하는 데모 코드 (raw → langchain → langgraph)
│  ├─ handouts/            ← 회차별 1페이지 요약 + 토론 질문 카드 + 용어집
│  └─ site/                ← 생성된 심화 HTML 사이트
│     ├─ build.py          ← md/코드 → HTML 변환 (재실행 가능; 포털·그래프도 생성)
│     ├─ index.html        ← 심화 사이트 진입점
│     ├─ playground.html   ← Pyodide Python 실습
│     └─ session-*.html …  ← 변환된 강의 페이지
└─ basics/                 ← 입문 과정 (별도 README)
   ├─ lessons/             ← 정제된 입문 강의(원본 md, 00~13)
   ├─ source/              ← 입문 원천 자료(정제 전, 01~13)
   └─ site/                ← 생성된 입문 HTML 사이트
```

## 커리큘럼 한눈에
| 주차 | 세션 | 주제 | 자료 |
|------|------|------|------|
| 1 | 1 | AI 에이전트 개요 & 패러다임 | [session-01](advanced/sessions/session-01-intro.md) |
| 1 | 2 | Tool Use / Function Calling의 본질 | [session-02](advanced/sessions/session-02-tool-use.md) |
| 2 | 3 | 추론 & 계획 패턴 | [session-03](advanced/sessions/session-03-reasoning.md) |
| 2 | 4 | 메모리 & 컨텍스트 관리 | [session-04](advanced/sessions/session-04-memory.md) |
| 3 | 5 | LangChain 아키텍처 | [session-05](advanced/sessions/session-05-langchain.md) |
| 3 | 6 | LangGraph 상태 그래프 | [session-06](advanced/sessions/session-06-langgraph.md) |
| 4 | 7 | 멀티 에이전트 & 오케스트레이션 | [session-07](advanced/sessions/session-07-multiagent.md) |
| 4 | 8 | 평가·관찰가능성·프로덕션 | [session-08](advanced/sessions/session-08-eval-ops.md) |

## 회차별 공통 포맷 (1~1.5시간)
1. 복습 & 동기부여 (5분)
2. 개념 강의 (40~55분, 다이어그램 중심)
3. 데모/코드 워크스루 (15~25분, 라이브 코딩 X)
4. 토론 & 정리 (10분)

## 데모 코드
| 파일 | 세션 | 내용 |
|------|------|------|
| [advanced/demos/01_raw_agent_loop.py](advanced/demos/01_raw_agent_loop.py) | 2 | raw API + while 루프 에이전트 |
| [advanced/demos/02_langchain_agent.py](advanced/demos/02_langchain_agent.py) | 5 | 동일 태스크를 LangChain으로 |
| [advanced/demos/03_langgraph_agent.py](advanced/demos/03_langgraph_agent.py) | 6 | 동일 태스크를 LangGraph 상태 그래프로 |
