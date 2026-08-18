# -*- coding: utf-8 -*-
"""
AI 에이전트 입문(워밍업) 정적 사이트 빌더.

basics/lessons/*.md 를 읽어 basics/site/ 아래에 HTML 페이지로 변환한다.
마크다운 렌더링은 클라이언트(marked.js)에서 수행하므로 외부 파이썬 라이브러리가
필요 없고, file:// 로 열어도 동작한다(인터넷 필요: CDN). 플레이그라운드는 없다.

재실행 가능:  python basics/site/build.py
"""
import hashlib
import json
import pathlib
import shutil

ROOT = pathlib.Path(__file__).resolve().parent.parent   # basics/
SITE = ROOT / "site"
ASSETS = ROOT.parent / "shared-assets"                   # 공유 디자인 시스템 소스 (ai-agent-course/shared-assets)


def _asset_ver():
    """style.css/app.js 내용 해시 → 캐시 버스팅 버전(브라우저 stale 캐시 방지)."""
    h = hashlib.md5()
    for n in ("style.css", "app.js"):
        p = ASSETS / n
        if p.exists():
            h.update(p.read_bytes())
    return h.hexdigest()[:8]


ASSET_VER = _asset_ver()

MARKED = "https://cdn.jsdelivr.net/npm/marked@12/marked.min.js"
HLJS = "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"
HLJS_CSS = "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github.min.css"
MERMAID = "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"
CHARTJS = "https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js"

# (표시번호, slug, 소스 md, 제목, 카드 설명)
# 1부(00~06): AI 기초 멘탈 모델 · 2부(07~12): 코딩 에이전트 실전 · 13: 전체 정리
LESSONS = [
    ("00", "lesson-00", "lessons/00-ai-landscape.md",          "AI 시대 이해하기",        "AI 발전 방향, LLM, 모델 3사·코딩 에이전트 비교"),
    ("01", "lesson-01", "lessons/01-how-ai-works.md",          "AI 모델은 어떻게 동작하나", "결정론 vs 확률론, 다음 토큰 예측, 모델 선택"),
    ("02", "lesson-02", "lessons/02-hallucination.md",         "환각과 한계",              "환각의 원리, 지식 컷오프, 검증 중심 사고"),
    ("03", "lesson-03", "lessons/03-tokens-pricing.md",        "토큰 & 요금제",            "토큰 개념, 입력/출력 과금, 스트리밍"),
    ("04", "lesson-04", "lessons/04-context.md",               "컨텍스트",                 "시스템/사용자 프롬프트, 작업 메모리, 한도"),
    ("05", "lesson-05", "lessons/05-tool-calling.md",          "도구 호출",                "tool calling 4단계, 도구 3요소, MCP"),
    ("06", "lesson-06", "lessons/06-agents.md",                "에이전트",                 "반복 루프 속 도구 활용, 위임과 가드레일"),
    ("07", "lesson-07", "lessons/07-using-agents.md",          "에이전트 활용하기",        "하니스, 효과적 프롬프트, 컨텍스트 관리, 스코프 크리프"),
    ("08", "lesson-08", "lessons/08-understanding-codebase.md","코드베이스 이해하기",      "grep vs 시맨틱 검색, 좋은 질문, 서브에이전트, 다이어그램"),
    ("09", "lesson-09", "lessons/09-building-features.md",     "기능 구현하기",            "계획 우선, TDD 워크플로, 디자인→코드, 검증 가드레일"),
    ("10", "lesson-10", "lessons/10-debugging.md",             "버그 발견 및 수정",        "디버깅 6원칙, 증거 우선, 런타임 증거, 여러 모델"),
    ("11", "lesson-11", "lessons/11-review-and-testing.md",    "코드 리뷰 및 테스트",      "자체/동료 리뷰, 자동 리뷰, 안전망, 테스트 위임, 피드백 루프"),
    ("12", "lesson-12", "lessons/12-customizing-agents.md",    "에이전트 맞춤 설정",       "Rules vs Skills, MCP, CLI 도구, 재사용 워크플로"),
    ("13", "lesson-13", "lessons/13-capstone.md",              "전체 정리 & 다음 단계",    "할인코드 E2E 예제 + 12개 멘탈 모델 + 10세션 심화 로드맵"),
]


def read(rel):
    return (ROOT / rel).read_text(encoding="utf-8")


def sidebar(active_slug):
    def link(href, label, slug, num=None):
        cls = ' class="active"' if slug == active_slug else ""
        numhtml = f'<span class="num">{num}</span>' if num else ""
        return f'      <a href="{href}"{cls}>{numhtml}{label}</a>'

    rows = []
    rows.append('  <div class="brand"><a href="index.html"><h1>AI 에이전트 입문</h1>'
                '<p>기초 + 실전 · 14개 레슨</p></a></div>')
    rows.append('  <div class="nav-group-title">레슨</div>')
    rows.append("  <nav>")
    for num, slug, _src, title, _desc in LESSONS:
        rows.append(link(f"{slug}.html", title, slug, num=num))
    rows.append("  </nav>")
    rows.append('  <div class="nav-group-title">과정</div>')
    rows.append("  <nav>")
    rows.append(link("../../index.html", "🏠 통합 포털", "_portal"))
    rows.append(link("../../graph.html", "🕸️ 지식 그래프", "_graph"))
    rows.append(link("../../advanced/site/index.html", "🚀 심화 과정", "_deep"))
    rows.append(link("../../practical/site/index.html", "🛠️ 실전 활용", "_practical"))
    rows.append("  </nav>")
    return '<aside class="sidebar">\n' + "\n".join(rows) + "\n</aside>"


def page_shell(title, active_slug, body, scripts=""):
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} · AI 에이전트 입문</title>
<link rel="stylesheet" href="style.css?v={ASSET_VER}">
<link rel="stylesheet" href="{HLJS_CSS}">
</head>
<body>
<button class="menu-toggle" aria-label="menu">☰</button>
<div class="layout">
{sidebar(active_slug)}
{body}
</div>
{scripts}
</body>
</html>
"""


def xref_pairs():
    """본문 '레슨 NN'(동일 과정) · '세션 N'(심화 과정) 참조 자동 링크 목록."""
    pairs = []
    for num, slug, *_rest in LESSONS:
        href = f"{slug}.html"
        n = int(num)
        for txt in (f"레슨 {num}", f"레슨{num}", f"레슨 {n}", f"레슨{n}"):
            pairs.append([txt, href])
    # 심화 10세션 과정으로의 교차 링크(다른 사이트 → 상대경로). '심화 연결' 문구의 '세션 N'.
    for i in range(1, 9):
        href = f"../../advanced/site/session-{i:02d}.html"
        for txt in (f"세션 {i:02d}", f"세션 {i}", f"세션{i:02d}", f"세션{i}"):
            pairs.append([txt, href])
    return pairs


def build_md_page(slug, src_rel, title):
    md = read(src_rel).replace("</script", "<\\/script")
    body = '<main class="content md" id="content"></main>'
    xref = json.dumps(xref_pairs(), ensure_ascii=False)
    scripts = (
        f'<script type="text/markdown" id="md-src">{md}</script>\n'
        f'<script>window.XREF={xref};window.SLUG="{slug}";</script>\n'
        f'<script src="{MARKED}"></script>\n'
        f'<script src="{HLJS}"></script>\n'
        f'<script src="{MERMAID}"></script>\n'
        f'<script src="{CHARTJS}"></script>\n'
        f'<script src="app.js?v={ASSET_VER}"></script>'
    )
    (SITE / f"{slug}.html").write_text(page_shell(title, slug, body, scripts), encoding="utf-8")


def build_index():
    cards = []
    for num, slug, _src, title, desc in LESSONS:
        cards.append(
            f'    <a class="card" href="{slug}.html">'
            f'<div class="num">LESSON {num}</div>'
            f'<div class="title">{title}</div>'
            f'<div class="desc">{desc}</div></a>'
        )
    cards_html = "\n".join(cards)
    body = f"""<main class="content">
  <div class="hero">
    <h1>AI 에이전트 입문</h1>
    <p>비유와 그림으로 익히는 AI의 핵심 멘탈 모델 + 코딩 에이전트 실전 활용</p>
    <div class="badges">
      <span class="badge">초보자 친화</span>
      <span class="badge">개념 + 실전 예시</span>
      <span class="badge">10세션 심화 과정 준비</span>
    </div>
  </div>

  <div class="notice">
    이 과정은 두 부분으로 이어집니다.
    <b>1부(레슨 00~06)</b>는 AI가 <b>어떻게·왜 그렇게 동작하는지</b> 멘탈 모델을 익히고,
    <b>2부(레슨 07~12)</b>는 <b>코딩 에이전트로 실제 소프트웨어를 개발하는 실전 전략</b>을 다룹니다.
    마지막 레슨에서 전체를 정리하고 <b>10세션 심화 과정</b>으로 이어집니다.
  </div>

  <h2>레슨 목록</h2>
  <div class="cards">
{cards_html}
  </div>
</main>"""
    (SITE / "index.html").write_text(page_shell("홈", "index", body), encoding="utf-8")


def copy_assets():
    """공유 디자인 시스템(shared-assets/)을 사이트로 복사."""
    SITE.mkdir(exist_ok=True)
    for name in ("style.css", "app.js"):
        shutil.copy(ASSETS / name, SITE / name)


def main():
    SITE.mkdir(exist_ok=True)
    copy_assets()
    for _num, slug, src, title, _desc in LESSONS:
        build_md_page(slug, src, title)
    build_index()
    out = sorted(p.name for p in SITE.glob("*.html"))
    print("생성된 HTML 페이지:")
    for name in out:
        print("  -", name)
    print(f"총 {len(out)}개 페이지. 엔트리: basics/site/index.html")


if __name__ == "__main__":
    main()
