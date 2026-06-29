# -*- coding: utf-8 -*-
"""
AI Agent 강의 정적 사이트 빌더.

sessions/*.md, handouts/*.md, shared/demo-task-spec.md 를 읽어
site/ 아래에 HTML 페이지로 변환하고,
demos/*.py 를 Pyodide 기반 플레이그라운드(playground.html)에 임베드한다.

마크다운 렌더링은 클라이언트(marked.js)에서 수행하므로
파이썬 외부 라이브러리가 필요 없고, file:// 로 열어도 동작한다(인터넷 필요: CDN).

재실행 가능:  python site/build.py
"""
import hashlib
import json
import pathlib
import re
import shutil

ROOT = pathlib.Path(__file__).resolve().parent.parent   # advanced/ (심화 과정 루트)
REPO = ROOT.parent                                       # ai-agent-course/ (저장소 루트)
SITE = ROOT / "site"
ASSETS = REPO / "shared-assets"                          # 공유 디자인 시스템 소스


def _asset_ver():
    """style.css/app.js 내용 해시 → 캐시 버스팅 버전(브라우저 stale 캐시 방지)."""
    h = hashlib.md5()
    for n in ("style.css", "app.js"):
        p = ASSETS / n
        if p.exists():
            h.update(p.read_bytes())
    return h.hexdigest()[:8]


ASSET_VER = _asset_ver()

# CDN
MARKED = "https://cdn.jsdelivr.net/npm/marked@12/marked.min.js"
HLJS = "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"
HLJS_CSS = "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github.min.css"
PYODIDE = "https://cdn.jsdelivr.net/pyodide/v0.26.4/full/pyodide.js"
MERMAID = "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"
CHARTJS = "https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js"

# (slug, 소스 md 경로, 제목, 주차, 카드 설명)
SESSIONS = [
    ("session-01", "sessions/session-01-intro.md",      "AI 에이전트 개요 & 패러다임",        "1주차 · 1회", "LLM 호출 vs 에이전트, 구성요소, Workflow vs Agent 스펙트럼"),
    ("session-02", "sessions/session-02-tool-use.md",   "Tool Use / Function Calling의 본질", "1주차 · 2회", "도구 스키마, 에이전트 루프를 raw API로 직접 구현"),
    ("session-03", "sessions/session-03-reasoning.md",  "추론 & 계획 패턴",                   "2주차 · 1회", "ReAct, Plan-and-Execute, Reflection, trade-off"),
    ("session-04", "sessions/session-04-memory.md",     "메모리 & 컨텍스트 관리",             "2주차 · 2회", "단기/장기 기억, 압축·요약, RAG 개요, state 관리"),
    ("session-05", "sessions/session-05-rag.md",        "RAG 심화 · 검색 증강 생성",          "3주차 · 1회", "청킹·임베딩·벡터DB, top-k/재랭킹/하이브리드, Agentic RAG·검색 평가"),
    ("session-06", "sessions/session-06-langchain.md",  "LangChain 아키텍처",                "3주차 · 2회", "LCEL, Runnable, 추상화의 비용/이점"),
    ("session-07", "sessions/session-07-langgraph.md",  "LangGraph 상태 그래프",             "4주차 · 1회", "State/Node/Edge, 순환, Human-in-the-loop"),
    ("session-08", "sessions/session-08-multiagent.md", "멀티 에이전트 & 오케스트레이션",     "4주차 · 2회", "Supervisor/Swarm, 핸드오프, RAG 심화"),
    ("session-09", "sessions/session-09-eval-ops.md",   "평가·관찰가능성·프로덕션",           "5주차 · 1회", "eval, tracing, 가드레일, 캡스톤"),
    ("session-10", "sessions/session-10-harness.md",   "하네스 & 컨텍스트 엔지니어링",        "5주차 · 2회", "모델 vs 하네스, 컨텍스트 조립·컴팩션·서브에이전트, 컨텍스트 엔지니어링·실패 모드"),
]

DOCS = [
    ("spec",                "shared/demo-task-spec.md",      "공통 데모 예제 명세"),
    ("handout-one-pagers",  "handouts/one-pagers.md",        "회차별 1페이지 요약"),
    ("handout-discussion",  "handouts/discussion-cards.md",  "토론 질문 카드"),
    ("glossary",            "handouts/glossary.md",          "용어집(Glossary)"),
]

# 강사 해설 스크립트(구어체 강의 대본): (slug, 소스 md, 사이드바 제목)
SCRIPTS = [
    (f"script-{i:02d}", f"scripts/session-{i:02d}-script.md", f"세션 {i} 해설 스크립트")
    for i in range(1, 11)
]

# 데모 코드: (파일, 라벨, 브라우저 실행 가능 여부)
DEMOS = [
    ("demos/01_raw_agent_loop.py",  "01 · raw 루프 (브라우저 실행 가능)", True),
    ("demos/02_langchain_agent.py", "02 · LangChain (읽기 전용)",         False),
    ("demos/03_langgraph_agent.py", "03 · LangGraph (읽기 전용)",         False),
]


# ---- 상호 연결(관계) 단일 출처 ----
# 세션 짧은 라벨(그래프·박스용)
SHORT = {
    "session-01": "개념·패러다임",
    "session-02": "도구·Function Calling",
    "session-03": "추론·계획",
    "session-04": "메모리·컨텍스트",
    "session-05": "RAG·검색증강",
    "session-06": "LangChain",
    "session-07": "LangGraph",
    "session-08": "멀티에이전트",
    "session-09": "평가·운영",
    "session-10": "하네스·컨텍스트",
}

# 세션별 관계: forward = 이 세션과 이어지는/참조하는 세션, back = 이 세션을 참조하는 세션
RELATIONS = {
    "session-01": {"forward": ["session-02"],
                   "back": ["session-02", "session-09"]},
    "session-02": {"forward": ["session-01", "session-03"],
                   "back": ["session-06", "session-07", "session-09", "session-10"]},
    "session-03": {"forward": ["session-02", "session-04"],
                   "back": ["session-04", "session-09"]},
    "session-04": {"forward": ["session-03", "session-05", "session-06", "session-07"],
                   "back": ["session-05", "session-07", "session-08", "session-09", "session-10"]},
    "session-05": {"forward": ["session-04", "session-08", "session-09"],
                   "back": ["session-04", "session-08", "session-09"]},
    "session-06": {"forward": ["session-02", "session-07"],
                   "back": ["session-07", "session-08", "session-09"]},
    "session-07": {"forward": ["session-02", "session-04", "session-06", "session-08"],
                   "back": ["session-08", "session-09"]},
    "session-08": {"forward": ["session-05", "session-06", "session-07", "session-09"],
                   "back": ["session-09", "session-10"]},
    "session-09": {"forward": ["session-01", "session-02", "session-03", "session-04",
                               "session-05", "session-06", "session-07", "session-08"],
                   "back": ["session-10"]},
    "session-10": {"forward": ["session-02", "session-04", "session-08", "session-09"],
                   "back": []},
}

# 개념 ↔ 세션 매트릭스(용어집 축약). (개념, [세션슬러그...], 한줄설명)
CONCEPTS = [
    ("Agentic Loop (관찰→추론→행동)", ["session-01", "session-02"], "에이전트 제어 흐름의 심장"),
    ("Tool Use / Function Calling",   ["session-02", "session-06"], "도구 스키마·호출·결과 재주입"),
    ("ReAct",                          ["session-01", "session-03"], "추론과 행동을 교차 생성"),
    ("Plan-and-Execute / Reflection",  ["session-03"],               "계획 분리·자기비평 루프"),
    ("Memory (단기/장기)",             ["session-04"],               "컨텍스트 재주입의 엔지니어링"),
    ("RAG (검색 증강)",                ["session-04", "session-05", "session-08"], "외부 지식을 생성에 결합"),
    ("임베딩 / 벡터DB",                ["session-05"],               "의미 벡터화·ANN 근사 최근접 검색"),
    ("청킹 / 재랭킹·하이브리드 검색",  ["session-05"],               "검색 단위 분할·정확도 향상 기법"),
    ("Agentic RAG (쿼리 재작성·self-RAG)", ["session-05"],           "검색 여부·횟수를 에이전트가 결정"),
    ("LCEL / Runnable",                ["session-06"],               "선언적 합성·공통 실행 인터페이스"),
    ("State Graph (State/Node/Edge)",  ["session-07"],               "while 루프의 1급 시민화"),
    ("Human-in-the-loop",              ["session-07", "session-09"], "고위험 동작 전 사람 승인"),
    ("Supervisor / Handoff",           ["session-08"],               "작업 분해·위임·제어권 이양"),
    ("평가·Trajectory / LLM-as-Judge", ["session-09"],               "결과+경로 평가·관찰가능성"),
    ("가드레일 / Prompt Injection",    ["session-02", "session-09"], "외부 데이터=신뢰 불가, 안전장치"),
    ("하네스 (에이전트 스캐폴드)",      ["session-10"],               "모델을 감싸 에이전트로 만드는 바깥 껍데기"),
    ("컨텍스트 엔지니어링 / 컴팩션",    ["session-04", "session-10"], "토큰 예산·압축·검색 주입·실패 모드 관리"),
]


# ---- 본문 용어 자동 링크(용어집 → 정의 세션 섹션) ----
# 용어집 표제어에 한국어 별칭이 괄호로 없을 때 보강(본문 등장 빈도 확인됨)
ALIASES = {
    "Prompt Injection": ["프롬프트 인젝션"],
    "State Graph": ["상태 그래프"],
    "Reflection": ["자기비판"],
    "Tracing": ["관찰가능성"],
    "Human-in-the-loop": ["휴먼 게이트", "휴먼 승인 게이트"],
    "MAX_TURNS": ["max_steps", "recursion_limit"],
}
SKIP_FORMS = {"Network"}   # 너무 일반적 → 제외(Swarm만 사용)


def slugify(text):
    """app.js 의 slugify 와 **동일 규칙**(앵커 일치 보장)."""
    t = text.lower()
    t = re.sub(r"[^0-9a-z가-힣]+", "-", t)
    return t.strip("-")


def _heading_text(raw):
    """마크다운 제목 → 브라우저 textContent 와 동일한 평문."""
    t = raw.lstrip("#").strip()
    t = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", t)   # [텍스트](url) → 텍스트
    t = t.replace("`", "").replace("**", "").replace("*", "")
    return t.strip()


def _term_forms(headword):
    """용어집 표제어 → 본문에서 찾을 표면형 목록."""
    if "(" in headword:
        base = headword.split("(", 1)[0].strip()
        paren = headword.split("(", 1)[1].split(")", 1)[0].strip()
    else:
        base, paren = headword.strip(), ""
    forms = []
    for b in re.split(r"\s*[/,]\s*", base):
        if b.strip():
            forms.append(b.strip())
    for p in re.split(r"\s*[/,]\s*", paren):
        p = p.strip()
        if not p:
            continue
        if re.search(r"[가-힣]", p):                       # 한국어 별칭
            forms.append(p)
        elif " " not in p and re.match(r"^[A-Za-z][A-Za-z0-9-]*$", p):  # 약어/동의어
            forms.append(p)
    return forms


# 용어가 "정의"되지 않고 단순 나열되는 보일러플레이트 섹션 — 본문 폴백 시 회피
BOILERPLATE = re.compile(r"학습\s*목표|타임라인|복습|다음\s*시간|강사\s*노트|토론|체크리스트|관련\s*세션|목차")


def parse_glossary():
    """handouts/glossary.md → [(surface_forms, candidate_slugs)]."""
    terms = []
    for line in read("handouts/glossary.md").split("\n"):
        m = re.match(r"^- \*\*(.+?)\*\*", line)
        if not m:
            continue
        headword = m.group(1)
        forms = _term_forms(headword)
        for key, extra in ALIASES.items():
            if key in headword:
                forms += extra
        forms = [f for f in dict.fromkeys(forms)            # 순서보존 중복제거
                 if f not in SKIP_FORMS and len(f) >= 3]
        if not forms:
            continue
        snums = sorted(set(int(x) for x in re.findall(r"S(\d+)", line)))
        candidates = [f"session-{n:02d}" for n in snums]
        terms.append((forms, candidates))
    return terms


def _scan_sections(slug):
    """세션 md → [(kind, heading_id, text_lower, is_boilerplate)] (코드펜스 제외)."""
    src = next((s[1] for s in SESSIONS if s[0] == slug), None)
    if not src:
        return []
    rows, seen, cur_id, fenced, boiler = [], {}, None, False, False
    for line in read(src).split("\n"):
        if line.strip().startswith("```"):
            fenced = not fenced
            continue
        if fenced:
            continue
        hm = re.match(r"^(#{1,4})\s+(.*)$", line)
        if hm:
            txt = _heading_text(hm.group(2))
            base = slugify(txt)
            if base:
                seen[base] = seen.get(base, 0) + 1
                cur_id = base if seen[base] == 1 else f"{base}-{seen[base]}"
            boiler = bool(BOILERPLATE.search(txt))
            rows.append(("h", cur_id, txt.lower(), boiler))
        else:
            rows.append(("b", cur_id, line.lower(), boiler))
    return rows


def term_target(forms, candidates):
    """용어 → 정의 섹션 #앵커. (1) 제목에 용어가 든 섹션 (2) 비보일러플레이트 본문 (3) 본문."""
    lowforms = [f.lower() for f in forms]
    scans = {c: _scan_sections(c) for c in candidates}

    def hit(text):
        return any(f in text for f in lowforms)

    # 1) 제목 자체에 용어가 등장하는 섹션(가장 강한 "정의" 신호) — 후보 세션 순
    for c in candidates:
        for kind, cid, text, _b in scans[c]:
            if kind == "h" and cid and hit(text):
                return f"{c}.html#{cid}"
    # 2) 보일러플레이트(학습목표/타임라인 등)가 아닌 본문 첫 등장
    for c in candidates:
        for kind, cid, text, boiler in scans[c]:
            if kind == "b" and not boiler and cid and hit(text):
                return f"{c}.html#{cid}"
    # 3) 그래도 없으면 본문 어디든 첫 등장
    for c in candidates:
        for kind, cid, text, _b in scans[c]:
            if kind == "b" and cid and hit(text):
                return f"{c}.html#{cid}"
    return "glossary.html"


def glossary_term_pairs():
    """[표면형, 대상href] — 본문 용어 자동 링크용."""
    pairs, used = [], set()
    for forms, candidates in parse_glossary():
        if not candidates:
            continue
        href = term_target(forms, candidates)
        for f in forms:
            if f.lower() in used:
                continue
            used.add(f.lower())
            pairs.append([f, href])
    return pairs


GLOBAL_TERM_HREF = None   # main()에서 1회: form.lower() -> 글로벌 href


def local_anchors(slug, md_text):
    """페이지별 같은-문서 링크: [표시텍스트, "#앵커", 정의섹션id_or_None].

    - §N / §N-M / §N.M 섹션 참조 → 같은 문서의 번호 섹션 헤딩.
    - 이 페이지에 정의 섹션이 있는 용어 → 그 섹션(정의 섹션 안에서는 app.js가 skip).
    """
    page = slug + ".html"
    headings, seen, fenced = [], {}, False     # (id, number_label, text_lower)
    for line in md_text.split("\n"):
        if line.strip().startswith("```"):
            fenced = not fenced
            continue
        if fenced:
            continue
        hm = re.match(r"^(#{1,4})\s+(.*)$", line)
        if not hm:
            continue
        txt = _heading_text(hm.group(2))
        base = slugify(txt)
        if not base:
            continue
        seen[base] = seen.get(base, 0) + 1
        hid = base if seen[base] == 1 else f"{base}-{seen[base]}"
        nm = re.match(r"^(\d+(?:\.\d+)?)", txt)          # 선두 번호 3 / 1.1
        headings.append((hid, nm.group(1) if nm else None, txt.lower()))

    num2id = {num: hid for hid, num, _t in headings if num}
    entries, used = [], set()

    def add(key, anchor, defsec):
        if key.lower() in used:
            return
        used.add(key.lower())
        entries.append([key, f"#{anchor}", defsec])

    # 1) §N 섹션 참조(본문에 등장 + 해석 가능한 것만 — 허위 앵커 금지)
    #    §N.M 헤딩이 없으면 상위 §N으로 폴백.
    for ref in sorted(set(re.findall(r"§(\d+(?:[.\-]\d+)?)", md_text))):
        norm = ref.replace("-", ".")
        hid = num2id.get(norm) or num2id.get(norm.split(".")[0])
        if hid:
            add(f"§{ref}", hid, None)

    # 2) 이 페이지에 정의 섹션이 있는 용어
    for forms, _candidates in parse_glossary():
        lowforms = [f.lower() for f in forms]
        anchor = None
        for hid, _num, htext in headings:                 # (a) 헤딩에 표면형
            if any(f in htext for f in lowforms):
                anchor = hid
                break
        if not anchor:                                    # (b) 글로벌 정의가 이 페이지
            for f in lowforms:
                href = (GLOBAL_TERM_HREF or {}).get(f, "")
                if href.split("#")[0] == page and "#" in href:
                    anchor = href.split("#", 1)[1]
                    break
        if not anchor:
            continue
        for f in forms:
            add(f, anchor, anchor)
    return entries


def xref_pairs():
    """본문 자동 링크용 [표시텍스트, href] 목록(긴 것 우선은 클라이언트에서 정렬)."""
    pairs = []
    for i, (slug, *_rest) in enumerate(SESSIONS, start=1):
        href = f"{slug}.html"
        pairs.append([f"세션 {i:02d}", href])   # 세션 02
        pairs.append([f"세션 {i}", href])        # 세션 2
        pairs.append([f"세션{i:02d}", href])     # 세션02
        pairs.append([f"세션{i}", href])         # 세션2
        pairs.append([f"S{i}", href])            # S2 / 용어집 (S2) 태그
    pairs += glossary_term_pairs()               # 본문 용어 → 정의 세션 섹션
    for num in BASICS_LESSON_NUMS:               # 입문 과정으로의 역링크(다른 사이트)
        href = f"../../basics/site/lesson-{num}.html"
        n = int(num)
        for txt in (f"레슨 {num}", f"레슨{num}", f"레슨 {n}", f"레슨{n}"):
            pairs.append([txt, href])
    return pairs


XREF_JSON = None  # main()에서 1회 계산


def session_title(slug):
    for s in SESSIONS:
        if s[0] == slug:
            return s[2]
    return slug


def related_box_md(slug):
    """세션 페이지 하단에 붙일 '관련 세션' 박스(실제 링크 HTML)."""
    rel = RELATIONS.get(slug)
    if not rel:
        return ""
    def items(slugs):
        seen, lis = set(), []
        for sg in slugs:
            if sg == slug or sg in seen:
                continue
            seen.add(sg)
            n = int(sg.split("-")[1])
            lis.append(f'<li><a href="{sg}.html">세션 {n:02d} · {SHORT.get(sg, session_title(sg))}</a></li>')
        return "\n".join(lis)

    fwd = items(rel.get("forward", []))
    back = items(rel.get("back", []))
    parts = ['\n<div class="related-box">',
             '<div class="related-title">🔗 관련 세션</div>']
    if fwd:
        parts.append("<p><b>이 세션과 이어지는 곳</b></p>")
        parts.append(f"<ul>\n{fwd}\n</ul>")
    if back:
        parts.append("<p><b>이 세션을 참조하는 세션</b></p>")
        parts.append(f"<ul>\n{back}\n</ul>")
    parts.append("</div>\n")
    return "\n".join(parts)


# ---- 입문(basics) 과정 연결 (lesson-13 capstone 브리지 표의 역방향) ----
BASICS_LESSON_TITLE = {
    "00": "AI 시대 이해하기", "01": "AI 모델은 어떻게 동작하나", "02": "환각과 한계",
    "03": "토큰 & 요금제", "04": "컨텍스트", "05": "도구 호출", "06": "에이전트",
    "07": "에이전트 활용하기", "08": "코드베이스 이해하기", "09": "기능 구현하기",
    "10": "버그 발견 및 수정", "11": "코드 리뷰 및 테스트", "12": "에이전트 맞춤 설정",
    "13": "전체 정리 & 다음 단계",
}
BASICS_MAP = {
    "session-01": ["01", "06", "07"],
    "session-02": ["05", "08"],
    "session-03": ["09", "10"],
    "session-04": ["03", "04", "07"],
    "session-05": ["04", "07"],
    "session-06": ["12"],
    "session-07": ["12"],
    "session-08": ["06"],
    "session-09": ["02", "11", "12"],
    "session-10": ["04", "12"],
}
BASICS_LESSON_NUMS = [f"{i:02d}" for i in range(14)]   # 역링크용


def basics_box_md(slug):
    """세션 하단 '입문 과정 연결' 박스 — 대응 입문 레슨으로(다른 사이트, 상대경로)."""
    nums = BASICS_MAP.get(slug)
    if not nums:
        return ""
    lis = "\n".join(
        f'<li><a href="../../basics/site/lesson-{num}.html">레슨 {num} · '
        f'{BASICS_LESSON_TITLE.get(num, "")}</a></li>'
        for num in nums
    )
    return ('\n<div class="related-box">'
            '\n<div class="related-title">🎓 입문 과정 연결</div>'
            '\n<p>이 세션의 토대가 되는 입문 레슨(개념·활용):</p>'
            f'\n<ul>\n{lis}\n</ul>'
            '\n</div>\n')


def read(rel):
    return (ROOT / rel).read_text(encoding="utf-8")


def sidebar(active_slug):
    """모든 페이지 공통 좌측 내비게이션 HTML 생성."""
    def link(href, label, slug, num=None):
        cls = ' class="active"' if slug == active_slug else ""
        numhtml = f'<span class="num">{num}</span>' if num else ""
        return f'      <a href="{href}"{cls}>{numhtml}{label}</a>'

    rows = []
    rows.append('  <div class="brand"><a href="index.html"><h1>AI Agent 개발</h1>'
                '<p>약 5주 · 총 10세션</p></a></div>')
    rows.append('  <div class="nav-group-title">강의</div>')
    rows.append("  <nav>")
    for i, (slug, _src, title, _wk, _desc) in enumerate(SESSIONS, start=1):
        rows.append(link(f"{slug}.html", title, slug, num=f"{i:02d}"))
    rows.append("  </nav>")
    rows.append('  <div class="nav-group-title">해설 스크립트</div>')
    rows.append("  <nav>")
    for i, (slug, _src, _title) in enumerate(SCRIPTS, start=1):
        rows.append(link(f"{slug}.html", f"세션 {i} 해설", slug, num=f"{i:02d}"))
    rows.append("  </nav>")
    rows.append('  <div class="nav-group-title">실습</div>')
    rows.append("  <nav>")
    rows.append(link("playground.html", "Python 플레이그라운드", "playground"))
    rows.append("  </nav>")
    rows.append('  <div class="nav-group-title">자료</div>')
    rows.append("  <nav>")
    rows.append(link("map.html", "🗺️ 관계 지도", "map"))
    for slug, _src, title in DOCS:
        rows.append(link(f"{slug}.html", title, slug))
    rows.append("  </nav>")
    rows.append('  <div class="nav-group-title">과정</div>')
    rows.append("  <nav>")
    rows.append(link("../../index.html", "🏠 통합 포털", "_portal"))
    rows.append(link("../../graph.html", "🕸️ 지식 그래프", "_graph"))
    rows.append(link("../../basics/site/index.html", "🎓 입문 과정", "_basics"))
    rows.append(link("../../practical/site/index.html", "🛠️ 실전 활용", "_practical"))
    rows.append("  </nav>")
    return '<aside class="sidebar">\n' + "\n".join(rows) + "\n</aside>"


def page_shell(title, active_slug, body, head_extra="", scripts=""):
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} · AI Agent 강의</title>
<link rel="stylesheet" href="style.css?v={ASSET_VER}">
<link rel="stylesheet" href="{HLJS_CSS}">
{head_extra}
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


def render_md_page(slug, md, title):
    """주어진 마크다운 문자열을 HTML 페이지로 렌더(상호참조 맵 주입 포함)."""
    local = json.dumps(local_anchors(slug, md), ensure_ascii=False)   # 같은-문서 링크
    md = md.replace("</script", "<\\/script")  # script 조기 종료 방지
    body = '<main class="content md" id="content"></main>'
    xref = XREF_JSON if XREF_JSON is not None else json.dumps(xref_pairs(), ensure_ascii=False)
    scripts = (
        f'<script type="text/markdown" id="md-src">{md}</script>\n'
        f'<script>window.XREF={xref};window.XREF_LOCAL={local};window.SLUG="{slug}";</script>\n'
        f'<script src="{MARKED}"></script>\n'
        f'<script src="{HLJS}"></script>\n'
        f'<script src="{MERMAID}"></script>\n'
        f'<script src="{CHARTJS}"></script>\n'
        f'<script src="app.js?v={ASSET_VER}"></script>'
    )
    html = page_shell(title, slug, body, scripts=scripts)
    (SITE / f"{slug}.html").write_text(html, encoding="utf-8")


def script_box_md(slug):
    """세션 하단 '해설 스크립트' 박스 — 대응 강의 대본 페이지로."""
    n = int(slug.split("-")[1])
    return ('\n<div class="related-box">'
            '\n<div class="related-title">🎙️ 강의 해설 스크립트</div>'
            '\n<p>이 세션을 말로 풀어 설명하는 강사 대본(쉬운 풀이·비유·예상 질문):</p>'
            f'\n<ul>\n<li><a href="script-{n:02d}.html">세션 {n} 해설 스크립트</a></li>\n</ul>'
            '\n</div>\n')


def build_md_page(slug, src_rel, title):
    md = read(src_rel)
    if slug in RELATIONS:               # 세션 페이지: 하단에 '관련 세션' + '입문 연결' + '해설 스크립트' 박스
        md = (md.rstrip() + "\n\n" + related_box_md(slug) + "\n"
              + basics_box_md(slug) + "\n" + script_box_md(slug) + "\n")
    render_md_page(slug, md, title)


def build_map():
    """세션·개념이 어떻게 연결되는지 한눈에 보는 '관계 지도' 페이지."""
    # 학습 경로 + '같은 예제 진화' 스레드 + 주요 역참조 (mermaid, 노드 클릭 시 이동)
    nodes = "\n".join(
        f'  {slug.replace("-", "").upper()}["S{int(slug.split("-")[1])} {SHORT[slug]}"]'
        for slug, *_ in SESSIONS
    )
    flow = "\n".join(
        f'  SESSION{i:02d} --> SESSION{i+1:02d}' for i in range(1, len(SESSIONS))
    )
    clicks = "\n".join(
        f'  click {slug.replace("-", "").upper()} "{slug}.html"' for slug, *_ in SESSIONS
    )
    # 개념 ↔ 세션 매트릭스 표
    rows = []
    for term, slugs, desc in CONCEPTS:
        links = " · ".join(
            f'[S{int(sg.split("-")[1])}]({sg}.html)' for sg in slugs
        )
        rows.append(f"| {term} | {links} | {desc} |")
    matrix = "\n".join(rows)

    md = f"""# 🗺️ 관계 지도 — 세션은 어떻게 이어지는가

이 과정은 **하나의 예제(리서치 어시스턴트)**가 raw 루프 → LangChain → LangGraph로
진화하며 10개 세션을 관통한다. 아래 지도로 세션 간 연결과 핵심 개념의 위치를 한눈에 볼 수 있다.
(다이어그램의 각 노드, 표의 `S#` 링크를 클릭하면 해당 세션으로 이동한다. 본문 곳곳의
`세션 0N`·`S#` 표기도 자동으로 링크가 걸려 있다.)

## 학습 경로 & 연결

```mermaid
graph LR
{nodes}
{flow}
  SESSION02 -. 같은 예제 진화 .-> SESSION06
  SESSION06 -. 진화 .-> SESSION07
  SESSION07 -. state 관리 .-> SESSION04
  SESSION10 -. 종합 정리 .-> SESSION01
  classDef thread fill:#eef0fe,stroke:#4f46e5,stroke-width:2px;
  class SESSION02,SESSION06,SESSION07 thread;
{clicks}
```

> [!NOTE]
> 실선 화살표 = 강의 진행 순서. 점선 = 같은 예제의 **진화**(세션 02→06→07)와 주요 **역참조**(마지막 하네스 세션이 전체를 종합).

## 핵심 개념 ↔ 세션 매트릭스

| 개념 | 다루는 세션 | 한 줄 설명 |
|------|------------|-----------|
{matrix}

> 더 자세한 정의는 [용어집(Glossary)](glossary.html)을, 회차 요약은 [회차별 1페이지 요약](handout-one-pagers.html)을 참고하세요.
"""
    render_md_page("map", md, "관계 지도")


def build_portal():
    """입문·심화를 묶는 최상위 통합 포털 (ROOT/index.html). 사이드바 없는 단독 랜딩."""
    def sid(slug):
        return slug.replace("-", "").upper()

    cards = (
        '<div class="cards">\n'
        '  <a class="card" href="basics/site/index.html"><div class="week">입문 · 14레슨</div>'
        '<div class="title">🎓 AI 에이전트 입문</div>'
        '<div class="desc">AI가 어떻게·왜 동작하는지 + 코딩 에이전트 실전 활용. 개념·멘탈 모델 중심.</div></a>\n'
        '  <a class="card" href="advanced/site/index.html"><div class="week">심화 · 10세션</div>'
        '<div class="title">🚀 AI Agent 개발 (약 5주)</div>'
        '<div class="desc">raw API → LangChain → LangGraph로 에이전트를 직접 빌드. 하나의 예제로 관통.</div></a>\n'
        '  <a class="card" href="practical/site/index.html"><div class="week">실전 · 7세션</div>'
        '<div class="title">🛠️ 코딩 에이전트 실전 활용</div>'
        '<div class="desc">자주 쓰는 명령·스킬·멀티 에이전트·커스터마이징. 오늘 바로 쓰는 실전 워크플로.</div></a>\n'
        '  <a class="card" href="graph.html"><div class="week">시각화</div>'
        '<div class="title">🕸️ 지식 그래프</div>'
        '<div class="desc">세션·레슨·용어가 어떻게 연결되는지 옵시디언식 그래프로 탐색.</div></a>\n'
        '</div>'
    )
    snodes = "\n".join(
        f'  {sid(sl)}["S{i} {SHORT[sl]}"]' for i, (sl, *_r) in enumerate(SESSIONS, 1)
    )
    sflow = " --> ".join(sid(sl) for sl, *_r in SESSIONS)
    sclicks = "\n".join(f'  click {sid(sl)} "advanced/site/{sl}.html"' for sl, *_r in SESSIONS)
    rows = []
    for i, (sl, _src, _t, _wk, _d) in enumerate(SESSIONS, 1):
        lessons = " · ".join(f"레슨 {n}" for n in BASICS_MAP.get(sl, []))
        rows.append(f"| {lessons or '— (추상화 맛보기)'} | 세션 {i} — {SHORT[sl]} |")
    bridge = "\n".join(rows)

    md = f"""# 🧭 AI 에이전트 마스터 — 통합 과정 지도

두 과정이 하나로 이어집니다. **입문**에서 *왜 그렇게 동작하고 어떻게 활용하나*를 익히고,
**심화**에서 *그래서 어떻게 직접 만드나*(raw API → LangChain → LangGraph)를 빌드합니다.

{cards}

## 통합 로드맵

```mermaid
graph LR
  B["🎓 입문 14레슨<br/>개념·활용"]
{snodes}
  B ==> {sid(SESSIONS[0][0])}
  {sflow}
  click B "basics/site/index.html"
{sclicks}
```

> [!NOTE]
> 입문(개념·활용)을 마치면 심화(직접 빌드)로 이어집니다. 노드를 클릭하면 해당 과정으로 이동합니다.

## 입문 ↔ 심화 브리지

각 심화 세션은 입문에서 다진 개념 위에 선다. 아래 `세션 N`·`레슨 NN`은 모두 클릭됩니다.

| 입문에서 배운 것 (개념·활용) | 심화에서 깊게 (직접 빌드) |
|------------------------------|---------------------------|
{bridge}

> 처음이라면 **입문 과정**부터, 직접 구현이 목표라면 **심화 과정**으로 바로 시작하세요.
"""
    md = md.replace("</script", "<\\/script")
    portal_xref = []
    for i in range(1, 11):
        href = f"advanced/site/session-{i:02d}.html"
        for txt in (f"세션 {i:02d}", f"세션 {i}", f"세션{i:02d}", f"세션{i}"):
            portal_xref.append([txt, href])
    for num in BASICS_LESSON_NUMS:
        href = f"basics/site/lesson-{num}.html"
        n = int(num)
        for txt in (f"레슨 {num}", f"레슨{num}", f"레슨 {n}", f"레슨{n}"):
            portal_xref.append([txt, href])
    xref = json.dumps(portal_xref, ensure_ascii=False)
    scripts = (
        f'<script type="text/markdown" id="md-src">{md}</script>\n'
        f'<script>window.XREF={xref};window.SLUG="_portal";</script>\n'
        f'<script src="{MARKED}"></script>\n'
        f'<script src="{HLJS}"></script>\n'
        f'<script src="{MERMAID}"></script>\n'
        f'<script src="{CHARTJS}"></script>\n'
        f'<script src="advanced/site/app.js?v={ASSET_VER}"></script>'
    )
    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AI 에이전트 마스터 · 통합 포털</title>
<link rel="stylesheet" href="advanced/site/style.css?v={ASSET_VER}">
<link rel="stylesheet" href="{HLJS_CSS}">
</head>
<body>
<div class="layout">
<main class="content md" id="content"></main>
</div>
{scripts}
</body>
</html>
"""
    (REPO / "index.html").write_text(html, encoding="utf-8")


GRAPH_PAGE = r"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>지식 그래프 · AI 에이전트 마스터</title>
<link rel="stylesheet" href="advanced/site/style.css?v=__VER__">
<style>
  html, body { height: 100%; margin: 0; overflow: hidden; }
  .gtoolbar { display: flex; align-items: center; gap: 14px; flex-wrap: wrap;
    padding: 10px 16px; border-bottom: 1px solid var(--border); background: var(--panel);
    font-size: 13.5px; position: relative; z-index: 5; }
  .gtoolbar strong { font-size: 15px; }
  .gtoolbar a.gback { color: var(--accent); text-decoration: none; font-weight: 600; }
  .glegend { display: inline-flex; gap: 12px; align-items: center; color: var(--text-dim); }
  .glegend i { display: inline-block; width: 11px; height: 11px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }
  .gtoolbar label { color: var(--text-dim); cursor: pointer; user-select: none; }
  .ghint { color: var(--text-faint); margin-left: auto; }
  #g { display: block; background:
    radial-gradient(circle at 50% 40%, #ffffff, var(--bg)); cursor: grab; }
  #g:active { cursor: grabbing; }
  #g text { font-family: -apple-system, "Malgun Gothic", "Noto Sans KR", sans-serif; }
</style>
</head>
<body>
<div class="gtoolbar">
  <a class="gback" href="index.html">← 포털</a>
  <strong>🕸️ 지식 그래프</strong>
  <span class="glegend"><span><i style="background:#4f46e5"></i>심화 세션</span>
    <span><i style="background:#16a34a"></i>입문 레슨</span>
    <span><i style="background:#ea580c"></i>실전 세션</span>
    <span><i style="background:#7c3aed"></i>용어</span></span>
  <label><input type="checkbox" data-toggle="lesson" checked> 입문 레슨</label>
  <label><input type="checkbox" data-toggle="practical" checked> 실전 세션</label>
  <label><input type="checkbox" data-toggle="term" checked> 용어</label>
  <span class="ghint">노드 클릭=이동 · 드래그=이동 · 휠=확대/축소 · 호버=이웃 강조</span>
</div>
<svg id="g"></svg>
<script src="https://cdn.jsdelivr.net/npm/d3@7"></script>
<script>
const GRAPH = __DATA__;
const COLORS = { session: "#4f46e5", lesson: "#16a34a", practical: "#ea580c", term: "#7c3aed" };
const tb = () => document.querySelector(".gtoolbar").offsetHeight;
const W = () => window.innerWidth, H = () => window.innerHeight - tb();

const svg = d3.select("#g").attr("width", W()).attr("height", H());
const g = svg.append("g");
const RAW = GRAPH.links;                       // {source,target,kind} (문자열 id)
const nodes = GRAPH.nodes.map(d => Object.assign({}, d));   // 위치 유지를 위해 보존
const deg = {};
RAW.forEach(l => { deg[l.source] = (deg[l.source] || 0) + 1; deg[l.target] = (deg[l.target] || 0) + 1; });
nodes.forEach(n => n.r = 6 + Math.min(15, (deg[n.id] || 0) * 1.6));
const adj = {}; nodes.forEach(n => adj[n.id] = new Set([n.id]));
RAW.forEach(l => { adj[l.source].add(l.target); adj[l.target].add(l.source); });

const active = { session: true, lesson: true, practical: true, term: true };
let link, node, label, sim;

function build() {
  const ns = nodes.filter(n => active[n.type]);
  const ids = new Set(ns.map(n => n.id));
  const ls = RAW.filter(l => ids.has(l.source) && ids.has(l.target))
                .map(l => ({ source: l.source, target: l.target, kind: l.kind }));
  g.selectAll("*").remove();
  link = g.append("g").attr("stroke", "#c3cad8").attr("stroke-opacity", 0.55)
    .selectAll("line").data(ls).join("line")
    .attr("stroke-width", d => (d.kind === "path" || d.kind === "lpath" || d.kind === "ppath") ? 2.2 : 1);
  node = g.append("g").selectAll("circle").data(ns).join("circle")
    .attr("r", d => d.r).attr("fill", d => COLORS[d.type])
    .attr("stroke", "#fff").attr("stroke-width", 1.5).style("cursor", "pointer")
    .call(drag()).on("mouseover", hoverOn).on("mouseout", hoverOff)
    .on("click", (e, d) => { if (d.href) window.location.href = d.href; });
  node.append("title").text(d => d.label + (d.href ? "  →  열기" : ""));
  label = g.append("g").selectAll("text").data(ns).join("text")
    .text(d => d.label).attr("font-size", d => d.type === "term" ? 10 : 12.5)
    .attr("font-weight", d => d.type === "term" ? 400 : 600)
    .attr("dx", d => d.r + 3).attr("dy", 4).attr("fill", "#1f2533")
    .style("pointer-events", "none").style("opacity", d => d.type === "term" ? 0 : 1);
  sim = d3.forceSimulation(ns)
    .force("link", d3.forceLink(ls).id(d => d.id).distance(d => d.kind === "term" ? 55 : 95).strength(0.35))
    .force("charge", d3.forceManyBody().strength(-240))
    .force("center", d3.forceCenter(W() / 2, H() / 2))
    .force("collide", d3.forceCollide().radius(d => d.r + 6))
    .on("tick", ticked);
}
function ticked() {
  link.attr("x1", d => d.source.x).attr("y1", d => d.source.y)
      .attr("x2", d => d.target.x).attr("y2", d => d.target.y);
  node.attr("cx", d => d.x).attr("cy", d => d.y);
  label.attr("x", d => d.x).attr("y", d => d.y);
}
function hoverOn(e, d) {
  const nb = adj[d.id];
  node.style("opacity", n => nb.has(n.id) ? 1 : 0.12);
  link.style("opacity", l => (l.source.id === d.id || l.target.id === d.id) ? 0.9 : 0.04);
  label.style("opacity", n => nb.has(n.id) ? 1 : 0.05);
}
function hoverOff() {
  node.style("opacity", 1);
  link.style("opacity", 0.55);
  label.style("opacity", n => n.type === "term" ? 0 : 1);
}
function drag() {
  return d3.drag()
    .on("start", (e, d) => { if (!e.active) sim.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; })
    .on("drag", (e, d) => { d.fx = e.x; d.fy = e.y; })
    .on("end", (e, d) => { if (!e.active) sim.alphaTarget(0); d.fx = null; d.fy = null; });
}
svg.call(d3.zoom().scaleExtent([0.2, 4]).on("zoom", e => g.attr("transform", e.transform)));
window.addEventListener("resize", () => {
  svg.attr("width", W()).attr("height", H());
  if (sim) { sim.force("center", d3.forceCenter(W() / 2, H() / 2)); sim.alpha(0.3).restart(); }
});
document.querySelectorAll("[data-toggle]").forEach(cb =>
  cb.addEventListener("change", () => { active[cb.dataset.toggle] = cb.checked; build(); }));
build();
</script>
</body>
</html>
"""


# ---- 실전(practical) 트랙 — 지식 그래프 편입용 메타 (자체 빌더는 practical/site/build.py) ----
PRACTICAL = [
    ("01", "워크플로"),
    ("02", "명령·슬래시"),
    ("03", "스킬"),
    ("04", "서브·멀티에이전트"),
    ("05", "커스터마이징"),
    ("06", "실전 E2E"),
    ("07", "안전·가드레일"),
]
# 실전 세션 ↔ (심화 세션 슬러그 / 입문 레슨 번호) 연결 — 그래프 브리지
PRACTICAL_BRIDGE = {
    "01": {"sessions": ["session-10"], "lessons": ["07", "08"]},
    "02": {"sessions": [],             "lessons": ["12"]},
    "03": {"sessions": [],             "lessons": ["12"]},
    "04": {"sessions": ["session-08", "session-10"], "lessons": ["08"]},
    "05": {"sessions": ["session-09"], "lessons": ["12"]},
    "06": {"sessions": ["session-09"], "lessons": ["09", "13"]},
    "07": {"sessions": ["session-09", "session-10"], "lessons": ["12"]},
}


def build_graph():
    """옵시디언 그래프 뷰 같은 force-directed 지식 그래프 (입문+심화+실전+용어 통합)."""
    nodes, links = [], []
    # 세션 노드 + 학습 경로/참조 엣지
    for i, (slug, _src, _t, _wk, _desc) in enumerate(SESSIONS, 1):
        nodes.append({"id": slug, "label": f"S{i} {SHORT[slug]}",
                      "type": "session", "href": f"advanced/site/{slug}.html"})
    for i in range(1, 10):
        links.append({"source": f"session-{i:02d}", "target": f"session-{i+1:02d}", "kind": "path"})
    for slug, rel in RELATIONS.items():
        for t in rel.get("forward", []):
            if t != slug:
                links.append({"source": slug, "target": t, "kind": "ref"})
    # 입문 레슨 노드 + 순서 엣지 + 세션 브리지
    for num in BASICS_LESSON_NUMS:
        nodes.append({"id": f"lesson-{num}", "label": f"L{num} {BASICS_LESSON_TITLE[num]}",
                      "type": "lesson", "href": f"basics/site/lesson-{num}.html"})
    for i in range(13):
        links.append({"source": f"lesson-{i:02d}", "target": f"lesson-{i+1:02d}", "kind": "lpath"})
    for slug, lnums in BASICS_MAP.items():
        for num in lnums:
            links.append({"source": f"lesson-{num}", "target": slug, "kind": "bridge"})
    # 실전(practical) 트랙 노드 + 순서 엣지 + 심화/입문 브리지
    for num, short in PRACTICAL:
        nodes.append({"id": f"pr-{num}", "label": f"P{int(num)} {short}",
                      "type": "practical", "href": f"practical/site/session-{num}.html"})
    for i in range(1, len(PRACTICAL)):
        links.append({"source": f"pr-{i:02d}", "target": f"pr-{i+1:02d}", "kind": "ppath"})
    for num, bridge in PRACTICAL_BRIDGE.items():
        for sslug in bridge.get("sessions", []):
            links.append({"source": f"pr-{num}", "target": sslug, "kind": "bridge"})
        for lnum in bridge.get("lessons", []):
            links.append({"source": f"pr-{num}", "target": f"lesson-{lnum}", "kind": "bridge"})
    # 용어 노드 + 정의 세션 엣지
    term_href = {f.lower(): h for f, h in glossary_term_pairs()}
    for idx, (forms, candidates) in enumerate(parse_glossary()):
        cands = [c for c in candidates if c in SHORT]
        if not cands:
            continue
        tid = f"term-{idx}"
        href = term_href.get(forms[0].lower(), "")
        href = ("advanced/site/" + href) if href else f"advanced/site/{cands[0]}.html"
        nodes.append({"id": tid, "label": forms[0], "type": "term", "href": href})
        for c in cands:
            links.append({"source": tid, "target": c, "kind": "term"})
    # 무향 중복 엣지 제거
    seen, dedup = set(), []
    for l in links:
        key = tuple(sorted([l["source"], l["target"]]))
        if key in seen:
            continue
        seen.add(key)
        dedup.append(l)
    data = json.dumps({"nodes": nodes, "links": dedup}, ensure_ascii=False)
    page = GRAPH_PAGE.replace("__DATA__", data).replace("__VER__", ASSET_VER)
    (REPO / "graph.html").write_text(page, encoding="utf-8")


def build_index():
    cards = []
    for i, (slug, _src, title, wk, desc) in enumerate(SESSIONS, start=1):
        cards.append(
            f'    <a class="card" href="{slug}.html">'
            f'<div class="week">{wk}</div>'
            f'<div class="title">{i:02d}. {title}</div>'
            f'<div class="desc">{desc}</div></a>'
        )
    cards_html = "\n".join(cards)
    body = f"""<main class="content">
  <div class="hero">
    <h1>AI Agent 개발 강의</h1>
    <p>중상급 개발자 대상 · 이론/개념 중심 · 세션당 1~1.5시간</p>
    <div class="badges">
      <span class="badge">raw API → LangChain → LangGraph</span>
      <span class="badge">하나의 예제로 관통</span>
      <span class="badge">브라우저 Python 실습</span>
    </div>
  </div>

  <div class="notice">
    전 과정이 하나의 토이 태스크 <b>“리서치 어시스턴트”</b>로 이어집니다.
    raw 루프(세션 2) → LangChain(세션 6) → LangGraph(세션 7)로 같은 예제가 진화합니다.
    <a href="spec.html">공통 예제 명세 보기 →</a>
  </div>

  <h2 style="border-bottom:1px solid var(--border);padding-bottom:.25em;">커리큘럼</h2>
  <div class="cards">
{cards_html}
  </div>

  <h2 style="border-bottom:1px solid var(--border);padding-bottom:.25em;">실습 & 자료</h2>
  <div class="cards">
    <a class="card" href="map.html"><div class="week">자료</div>
      <div class="title">🗺️ 관계 지도</div>
      <div class="desc">세션이 어떻게 이어지는지 + 핵심 개념↔세션 매트릭스를 한눈에</div></a>
    <a class="card" href="playground.html"><div class="week">실습</div>
      <div class="title">Python 플레이그라운드</div>
      <div class="desc">브라우저에서 raw 에이전트 루프를 직접 실행하고 trace를 관찰</div></a>
    <a class="card" href="handout-one-pagers.html"><div class="week">자료</div>
      <div class="title">회차별 1페이지 요약</div>
      <div class="desc">10개 세션 핵심 정리 + 자가 점검 질문</div></a>
    <a class="card" href="handout-discussion.html"><div class="week">자료</div>
      <div class="title">토론 질문 카드</div>
      <div class="desc">세션별 개방형 토론 + 강사용 촉진 포인트</div></a>
  </div>
</main>"""
    html = page_shell("홈", "index", body)
    (SITE / "index.html").write_text(html, encoding="utf-8")


def build_playground():
    demo_sources = {}
    options = []
    for path, label, runnable in DEMOS:
        src = read(path)
        key = pathlib.Path(path).name
        demo_sources[key] = {"code": src, "runnable": runnable}
        options.append(f'<option value="{key}">{label}</option>')
    options_html = "\n        ".join(options)
    data_json = json.dumps(demo_sources, ensure_ascii=False)

    body = f"""<main class="content pg-wrap">
  <h1>Python 플레이그라운드</h1>
  <p style="color:var(--text-dim)">
    브라우저에서 바로 Python을 실행합니다(<b>Pyodide</b> · WebAssembly).
    <code>01_raw_agent_loop.py</code>는 표준 라이브러리와 mock 모델만 쓰므로 그대로 실행됩니다.
    코드를 직접 고쳐가며 에이전트 루프 trace를 관찰해 보세요.
  </p>

  <div class="pg-toolbar">
    <select id="demo-select">
        {options_html}
    </select>
    <button class="pg-btn run" id="run-btn">▶ 실행</button>
    <button class="pg-btn" id="reset-btn">↺ 원본 복원</button>
    <span class="pg-status" id="status">Pyodide 준비됨(첫 실행 시 로드)</span>
  </div>

  <div id="warn" class="notice warn" style="display:none">
    이 데모는 <b>langchain / langgraph</b> 설치가 필요해 브라우저에서는 실행되지 않습니다.
    아래 코드는 <b>읽기용</b>입니다. 라이브 실행은 <code>01</code> 데모로 시연하세요.
  </div>

  <textarea id="editor" spellcheck="false"></textarea>
  <div class="pg-output" id="output"><span class="sys"># 출력이 여기에 표시됩니다</span></div>
</main>"""

    scripts = f"""<script>
const DEMOS = {data_json};
let pyodide = null, loading = false;

const editor = document.getElementById('editor');
const select = document.getElementById('demo-select');
const runBtn = document.getElementById('run-btn');
const resetBtn = document.getElementById('reset-btn');
const statusEl = document.getElementById('status');
const outEl = document.getElementById('output');
const warnEl = document.getElementById('warn');

function loadDemo(key) {{
  editor.value = DEMOS[key].code;
  const runnable = DEMOS[key].runnable;
  warnEl.style.display = runnable ? 'none' : 'block';
  runBtn.disabled = !runnable;
  outEl.innerHTML = '<span class="sys"># 출력이 여기에 표시됩니다</span>';
}}

function appendOut(text, cls) {{
  if (outEl.querySelector('.sys')) outEl.innerHTML = '';
  const span = document.createElement('span');
  if (cls) span.className = cls;
  span.textContent = text;
  outEl.appendChild(span);
}}

select.addEventListener('change', () => loadDemo(select.value));
resetBtn.addEventListener('click', () => loadDemo(select.value));

async function ensurePyodide() {{
  if (pyodide) return pyodide;
  if (loading) return null;
  loading = true;
  statusEl.textContent = 'Pyodide 로딩 중...';
  pyodide = await loadPyodide();
  statusEl.textContent = 'Pyodide 준비 완료';
  loading = false;
  return pyodide;
}}

runBtn.addEventListener('click', async () => {{
  const py = await ensurePyodide();
  if (!py) return;
  outEl.innerHTML = '';
  py.setStdout({{ batched: (s) => appendOut(s + '\\n') }});
  py.setStderr({{ batched: (s) => appendOut(s + '\\n', 'err') }});
  runBtn.disabled = true;
  statusEl.textContent = '실행 중...';
  try {{
    await py.runPythonAsync(editor.value);
    statusEl.textContent = '완료';
  }} catch (e) {{
    appendOut('\\n' + e.message, 'err');
    statusEl.textContent = '오류 발생';
  }} finally {{
    runBtn.disabled = false;
  }}
}});

loadDemo(select.value);
</script>
<script src="{PYODIDE}"></script>
<script src="app.js?v={ASSET_VER}"></script>"""

    html = page_shell("Python 플레이그라운드", "playground", body, scripts=scripts)
    (SITE / "playground.html").write_text(html, encoding="utf-8")


def copy_assets():
    """공유 디자인 시스템(shared-assets/)을 사이트로 복사."""
    SITE.mkdir(exist_ok=True)
    for name in ("style.css", "app.js"):
        shutil.copy(ASSETS / name, SITE / name)


def main():
    global XREF_JSON, GLOBAL_TERM_HREF
    GLOBAL_TERM_HREF = {f.lower(): href for f, href in glossary_term_pairs()}
    XREF_JSON = json.dumps(xref_pairs(), ensure_ascii=False)
    SITE.mkdir(exist_ok=True)
    copy_assets()
    for slug, src, title, _wk, _desc in SESSIONS:
        build_md_page(slug, src, title)
    for slug, src, title in DOCS:
        build_md_page(slug, src, title)
    for slug, src, title in SCRIPTS:
        build_md_page(slug, src, title)
    build_map()
    build_index()
    build_playground()
    build_portal()
    build_graph()
    out = sorted(p.name for p in SITE.glob("*.html"))
    print("생성된 HTML 페이지:")
    for name in out:
        print("  -", name)
    print(f"총 {len(out)}개 페이지. 엔트리: site/index.html")


if __name__ == "__main__":
    main()
