# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요

`ai-agent-course/` 는 AI 에이전트 커리큘럼을 위한 정적 HTML 지식 사이트입니다: 입문 14레슨
(`basics/`)과 심화 8세션 (`advanced/`). 콘텐츠는 마크다운 + Python 데모로 작성하고, 두 개의
`build.py` 스크립트가 HTML로 조립하며, GitHub Pages가 서빙합니다. package.json·테스트 스위트·
외부 Python 의존성이 없습니다 — 빌더는 표준 라이브러리만 사용하고, 모든 JS 라이브러리는 CDN에서
로드합니다.

## 빌드 & 실행

```bash
python ai-agent-course/advanced/site/build.py   # advanced/site/*.html + 통합 포털 index.html + graph.html 재생성
python ai-agent-course/basics/site/build.py     # basics/site/*.html 재생성
```

미리보기는 `ai-agent-course/index.html` 을 직접 열면 됩니다 — `file://` 로도 동작합니다(CDN 접속 필요).

## 핵심 작업 규칙

**`.md` 소스를 수정해도 해당 `build.py` 를 실행하고 재생성된 `.html` 을 커밋하기 전에는 화면에
아무 변화가 없습니다.** CI(`.github/workflows/deploy-pages.yml`)는 `main` 푸시 시 `ai-agent-course/`
디렉터리를 **있는 그대로** 배포할 뿐, 빌더를 실행하지 **않습니다**. 따라서 작업 루프는:
마크다운 수정 → `build.py` 실행 → 소스와 생성된 HTML을 **둘 다** 커밋.

- `*/site/` 아래의 생성된 HTML을 직접 수정하지 마세요 — 다음 빌드 때 덮어쓰여집니다.
- `shared-assets/{style.css,app.js}` 가 디자인 시스템의 단일 출처입니다. 두 빌더 모두 이를 각
  `site/` 로 복사하고 MD5 해시(`_asset_ver()`)로 캐시 버스팅하므로, 복사본이 아니라 이곳을 수정하세요.

## 아키텍처

- 마크다운은 `marked.js` 가 **클라이언트 측에서** 렌더링합니다. `build.py` 는 마크다운을 HTML로
  변환하지 **않으며**, 페이지 셸·사이드바·상호 링크 메타데이터만 조립하고 원본 마크다운을 임베드해
  브라우저가 렌더링하게 합니다.
- 상호 링크는 `advanced/site/build.py` 상단의 메타데이터 테이블이 구동합니다: `SESSIONS`, `DOCS`,
  `SCRIPTS`, `DEMOS`, 세션 관계 테이블, 용어집 자동 링커(용어 → `glossary.html` 정의 앵커),
  basics↔advanced 브리지 맵. **세션/문서를 추가하거나 이름을 바꾸려면** 파일만 추가할 게 아니라
  이 튜플들을 수정해야 합니다.
- `advanced/site/build.py` 는 전체 과정용 통합 포털 `index.html` 과 지식 그래프 `graph.html` 도
  생성합니다.
- 커스텀 마크다운 마크업은 `shared-assets/app.js` 에서 후처리되며 `shared-assets/DESIGN.md` 에
  문서화되어 있습니다: `[!TIP]/[!NOTE]/...` 콜아웃, `==하이라이트==`, `[[chip:label]]`, 그리고
  펜스 코드블록 ` ```kpi ` / ` ```mermaid ` / ` ```chart `. 새 콘텐츠는 이 마크업을 사용해 작성하세요.
- 브라우저 Python 플레이그라운드(`advanced/site/playground.html`)는 Pyodide + Monaco로
  `advanced/demos/01_raw_agent_loop.py` 를 임베드합니다. 공통 "Research Assistant" 데모 과제
  (`advanced/shared/demo-task-spec.md`)는 세션 2→5→6(raw API → LangChain → LangGraph)에 걸쳐
  이어집니다. 모든 도구는 목(mock)이므로 API 키가 필요 없습니다.

## 콘텐츠 구성

- `basics/lessons/*.md` — 입문 14레슨 (소스)
- `advanced/sessions/*.md` — 심화 8세션 (소스)
- `advanced/scripts/*.md` — 강사용 구어체 강의 대본 (세션당 1개)
- `advanced/handouts/*.md` — 1페이지 요약, 토론 카드, 용어집
- `advanced/demos/*.py` — 데모 코드 (01 raw / 02 LangChain / 03 LangGraph)

## 작업규칙
1. 코딩하기 전에 생각하세요
추측하지 마세요. 혼란스러운 점을 숨기지 마세요. 장단점을 명확히 드러내세요.

실행하기 전에:

가정한 내용을 명확하게 밝히세요. 확실하지 않으면 질문하세요.
여러 가지 해석이 가능하다면, 묵묵히 선택하지 말고 모두 제시하십시오.
더 간단한 방법이 있다면 언급하십시오. 필요하다면 반박하십시오.
이해가 안 되는 부분이 있으면 멈추세요. 무엇이 헷갈리는지 말하고 질문하세요.
2. 단순함이 최우선
문제를 해결하는 데 필요한 최소한의 코드만 작성하세요. 추측성 코드는 일절 포함하지 마세요.

요청하신 기능 외에는 추가 기능이 없습니다.
일회용 코드에는 추상화가 필요 없습니다.
요청하지 않은 "유연성"이나 "설정 가능성"은 없습니다.
불가능한 시나리오에 대한 오류 처리가 없습니다.
200줄을 썼는데 50줄로 줄일 수 있다면 다시 쓰세요.
스스로에게 "선임 엔지니어가 이것이 지나치게 복잡하다고 말할까?"라고 질문해 보세요. 만약 그렇다면, 단순화하세요.

3. 수술적 변화
꼭 필요한 것만 만지세요. 자신이 저지른 일은 스스로 수습하세요.

기존 코드를 편집할 때:

인접한 코드, 주석 또는 서식을 "개선"하지 마십시오.
멀쩡한 것을 굳이 리팩토링하지 마세요.
기존 스타일과 일치시키세요. 비록 당신이 다르게 표현하더라도 말입니다.
관련 없는 사용되지 않는 코드를 발견하면 삭제하지 말고 언급해 주세요.
변경 사항으로 인해 고아 파일이 생성되는 경우:

사용자가 변경하여 더 이상 사용되지 않게 된 임포트/변수/함수를 제거하세요.
요청받지 않는 한 기존의 사용되지 않는 코드를 삭제하지 마십시오.
테스트: 변경된 모든 줄은 사용자의 요청과 직접적으로 연결되어야 합니다.

4. 목표 중심적 실행
성공 기준을 정의합니다. 기준이 충족될 때까지 반복합니다.

과제를 검증 가능한 목표로 전환하세요:

"유효성 검사 추가" → "유효하지 않은 입력에 대한 테스트를 작성하고, 해당 테스트를 통과하도록 만들기"
"버그 수정" → "버그를 재현하는 테스트를 작성하고, 테스트를 통과시키세요"
"X 리팩토링" → "리팩토링 전후에 테스트 통과 확인"
여러 단계를 거치는 작업의 경우, 간략한 계획을 제시하십시오.

1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
명확한 성공 기준은 독립적인 반복 작업을 가능하게 합니다. 반면, 모호한 기준("그냥 작동하게 하라")은 지속적인 명확화를 요구합니다.


