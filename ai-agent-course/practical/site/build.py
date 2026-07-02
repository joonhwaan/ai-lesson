# -*- coding: utf-8 -*-
"""
코딩 에이전트 실전 활용 — 정적 사이트 빌더 (제3 트랙).

practical/sessions/*.md 를 읽어 practical/site/ 아래에 HTML 페이지로 변환한다.
입문(basics)·심화(advanced)와 동일한 패턴: 마크다운 렌더링은 클라이언트(marked.js)에서
수행하므로 외부 파이썬 라이브러리가 필요 없고, file:// 로도 동작한다(인터넷 필요: CDN).

재실행 가능:  python practical/site/build.py
"""
import hashlib
import json
import pathlib
import shutil

ROOT = pathlib.Path(__file__).resolve().parent.parent   # practical/
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
# 파일럿 단계: session-01 만 활성. 세션 2~6 은 콘텐츠 완성 시 주석 해제(.md 가 있어야 빌드됨).
SESSIONS = [
    ("01", "session-01", "sessions/session-01-workflow.md",    "워크플로 손에 익히기",      "탐색→계획→실행→검증 루프, /clear·/compact, 스코프 관리, 프롬프트 패턴"),
    ("02", "session-02", "sessions/session-02-commands.md",    "자주 쓰는 명령 & 슬래시 커맨드", "내장 명령, ! 셸·첨부, 커스텀 슬래시 커맨드, 레시피"),
    ("03", "session-03", "sessions/session-03-skills.md",       "스킬(Skills) 만들고 쓰기",   "규칙 vs 스킬, 자동 발동, 직접 작성, 팀 공유"),
    ("04", "session-04", "sessions/session-04-multiagent.md",   "서브에이전트 & 멀티 에이전트", "Task 병렬·격리, 배치 전략, 역할 분담, 통합 검증"),
    ("05", "session-05", "sessions/session-05-customizing.md",  "커스터마이징: 규칙·훅·MCP",   "CLAUDE.md 규칙, 훅 자동화, MCP 연결, 권한 모드"),
    ("06", "session-06", "sessions/session-06-e2e.md",          "실전 시나리오 E2E",         "구현·디버깅·리팩터·리뷰를 한 흐름으로"),
    ("07", "session-07", "sessions/session-07-guardrails.md",   "안전하게 운영하기 (가드레일)", "settings.json 권한·PreToolUse 훅·샌드박스·저장소 게이트로 안전을 환경으로 강제"),
]

# 강좌 총 세션 수(설계 확정값) — 사이드바/인덱스 표기에 사용. 활성 페이지 수와 무관.
TOTAL_SESSIONS = 7

# 강사 해설 스크립트(구어체 대본): 활성 세션마다 scripts/session-NN-script.md 가 있으면 페이지화.
SCRIPTS = [
    (f"script-{num}", f"scripts/session-{num}-script.md", f"세션 {int(num)} 해설 스크립트", num)
    for num, *_rest in SESSIONS
]


def read(rel):
    return (ROOT / rel).read_text(encoding="utf-8")


def sidebar(active_slug):
    def link(href, label, slug, num=None):
        cls = ' class="active"' if slug == active_slug else ""
        numhtml = f'<span class="num">{num}</span>' if num else ""
        return f'      <a href="{href}"{cls}>{numhtml}{label}</a>'

    rows = []
    rows.append('  <div class="brand"><a href="index.html"><h1>코딩 에이전트 실전</h1>'
                f'<p>실전 활용 · {TOTAL_SESSIONS}세션</p></a></div>')
    rows.append('  <div class="nav-group-title">세션</div>')
    rows.append("  <nav>")
    for num, slug, _src, title, _desc in SESSIONS:
        rows.append(link(f"{slug}.html", title, slug, num=num))
    rows.append("  </nav>")
    if SCRIPTS:
        rows.append('  <div class="nav-group-title">해설 스크립트</div>')
        rows.append("  <nav>")
        for sslug, _src, _title, num in SCRIPTS:
            rows.append(link(f"{sslug}.html", f"세션 {int(num)} 해설", sslug, num=num))
        rows.append("  </nav>")
    rows.append('  <div class="nav-group-title">과정</div>')
    rows.append("  <nav>")
    rows.append(link("../../index.html", "🏠 통합 포털", "_portal"))
    rows.append(link("../../graph.html", "🕸️ 지식 그래프", "_graph"))
    rows.append(link("../../basics/site/index.html", "🎓 입문 과정", "_basics"))
    rows.append(link("../../advanced/site/index.html", "🚀 심화 과정", "_deep"))
    rows.append("  </nav>")
    return '<aside class="sidebar">\n' + "\n".join(rows) + "\n</aside>"


def page_shell(title, active_slug, body, scripts=""):
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} · 코딩 에이전트 실전</title>
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
    """본문 자동 링크: 트랙 내 '세션 N'(활성 세션만 — 죽은 링크 방지) + 입문 '레슨 NN'.

    심화 트랙도 자체 단위를 '세션 N'으로 부르므로(표면형 충돌), 심화로의 교차링크는
    auto-link 하지 않고 본문에서 '심화 과정의 …'로 풀어 쓴다.
    """
    pairs = []
    for num, slug, *_rest in SESSIONS:        # 활성(존재하는) 세션만 → 404 방지
        href = f"{slug}.html"
        n = int(num)
        for txt in (f"세션 {num}", f"세션{num}", f"세션 {n}", f"세션{n}"):
            pairs.append([txt, href])
    for i in range(14):                       # 입문 과정으로의 교차 링크(다른 사이트 → 상대경로)
        num = f"{i:02d}"
        href = f"../../basics/site/lesson-{num}.html"
        for txt in (f"레슨 {num}", f"레슨{num}", f"레슨 {i}", f"레슨{i}"):
            pairs.append([txt, href])
    return pairs


def script_box_md(num):
    """세션 하단 '해설 스크립트' 박스 — 대응 강의 대본 페이지로."""
    return ('\n\n<div class="related-box">'
            '\n<div class="related-title">🎙️ 강의 해설 스크립트</div>'
            '\n<p>이 세션을 말로 풀어 설명하는 강사 대본(쉬운 풀이·비유·예상 질문):</p>'
            f'\n<ul>\n<li><a href="script-{num}.html">세션 {int(num)} 해설 스크립트</a></li>\n</ul>'
            '\n</div>\n')


def build_md_page(slug, src_rel, title, tail_md=""):
    md = (read(src_rel).rstrip() + tail_md).replace("</script", "<\\/script")
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
    for num, slug, _src, title, desc in SESSIONS:
        cards.append(
            f'    <a class="card" href="{slug}.html">'
            f'<div class="num">SESSION {num}</div>'
            f'<div class="title">{title}</div>'
            f'<div class="desc">{desc}</div></a>'
        )
    cards_html = "\n".join(cards)
    body = f"""<main class="content">
  <div class="hero">
    <h1>코딩 에이전트 실전 활용</h1>
    <p>"읽고 끝"이 아니라 오늘 바로 쓰는 명령·스킬·멀티 에이전트 워크플로</p>
    <div class="badges">
      <span class="badge">실전 활용 중심</span>
      <span class="badge">복붙해 쓰는 예시</span>
      <span class="badge">총 {TOTAL_SESSIONS}세션</span>
    </div>
  </div>

  <div class="notice">
    입문(개념)·심화(직접 빌드)에 이은 <b>제3 트랙</b>입니다.
    Claude Code 같은 코딩 에이전트를 <b>실제로 어떻게 굴리는가</b> —
    자주 쓰는 명령, 슬래시 커맨드, 스킬, 서브·멀티 에이전트, 커스터마이징을 다룹니다.
    <br><b>기준 시점: 2026-06.</b> 도구 사용법은 빠르게 바뀌니 원리와 함께 익히세요.
  </div>

  <h2>세션 목록</h2>
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
    have_script = {num for _s, src, _t, num in SCRIPTS if (ROOT / src).exists()}
    for num, slug, src, title, _desc in SESSIONS:
        tail = script_box_md(num) if num in have_script else ""
        build_md_page(slug, src, title, tail_md=tail)
    for sslug, src, stitle, num in SCRIPTS:          # 대본 페이지(있는 것만)
        if num in have_script:
            build_md_page(sslug, src, stitle)
    build_index()
    out = sorted(p.name for p in SITE.glob("*.html"))
    print("생성된 HTML 페이지:")
    for name in out:
        print("  -", name)
    print(f"총 {len(out)}개 페이지. 엔트리: practical/site/index.html")


if __name__ == "__main__":
    main()
