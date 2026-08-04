# 프로젝트 요약 (AI Agent 강의 콘텐츠)

## 개요
- **대상/형태**: 중상급 개발자 대상 10세션 심화 과정 + 초보자용 입문 과정(레슨 00~13)
- **진행 흐름**: 원리(raw API) → 추상화(LangChain/LangGraph) → 운영(멀티에이전트·평가)
- **공통 데모**: 동일한 토이 태스크(리서치 어시스턴트)를 전 세션에서 점진 심화

## 주요 구성
```
ai-agent-course/
├─ README.md               # 전체 인덱스
├─ index.html              # 통합 포털(입문+심화)
├─ graph.html              # 지식 그래프
├─ shared-assets/          # 공통 디자인 시스템(style.css, app.js, DESIGN.md)
├─ basics/                 # 입문 과정
│  ├─ lessons/             # 정제된 레슨(00~13)
│  ├─ source/              # 원천 자료(정제 전)
│  └─ site/                # 생성된 입문 HTML 사이트
└─ advanced/               # 심화 5주 과정(10세션)
   ├─ sessions/            # 세션별 강의 원본(md)
   ├─ demos/               # 데모 코드(raw → langchain → langgraph)
   ├─ handouts/            # 1페이지 요약/토론 카드/용어집
   ├─ shared/              # 공통 데모 스펙
   └─ site/                # 생성된 심화 HTML 사이트
```

## 심화 과정 커리큘럼(10세션)
| 주차 | 세션 | 주제 |
|------|------|------|
| 1 | 1 | AI 에이전트 개요 & 패러다임 |
| 1 | 2 | Tool Use / Function Calling |
| 2 | 3 | 추론 & 계획 패턴 |
| 2 | 4 | 메모리 & 컨텍스트 관리 |
| 3 | 5 | RAG 심화 · 검색 증강 생성 |
| 3 | 6 | LangChain 아키텍처 |
| 4 | 7 | LangGraph 상태 그래프 |
| 4 | 8 | 멀티 에이전트 & 오케스트레이션 |
| 5 | 9 | 평가·관찰가능성·프로덕션 |
| 5 | 10 | 하네스 & 컨텍스트 엔지니어링 |

## 입문 과정 구성
- **1부 (레슨 00~06)**: AI 멘탈 모델, 환각/컨텍스트/도구 호출 등 기초 개념
- **2부 (레슨 07~12)**: 코딩 에이전트 활용(코드 이해/구현/디버깅/리뷰/맞춤화)
- **레슨 13**: 전체 정리 및 심화 과정 로드맵

## 데모 코드
| 파일 | 세션 | 내용 |
|------|------|------|
| advanced/demos/01_raw_agent_loop.py | 2 | raw API + while 루프 에이전트 |
| advanced/demos/02_langchain_agent.py | 6 | LangChain 버전 |
| advanced/demos/03_langgraph_agent.py | 7 | LangGraph 버전 |

## 보기/빌드 방법
- **통합 포털**: `ai-agent-course/index.html` 더블클릭
- **심화 사이트**: `advanced/site/index.html` (재빌드: `python advanced/site/build.py`)
- **입문 사이트**: `basics/site/index.html` (재빌드: `python basics/site/build.py`)

## 공통 형식(심화 세션)
1) 복습 & 동기부여 → 2) 개념 강의(다이어그램 중심) → 3) 데모/코드 워크스루 → 4) 토론 & 정리
