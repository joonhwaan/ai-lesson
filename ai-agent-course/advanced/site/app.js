/* ============================================================
   AI 강의 사이트 — 렌더 엔진 (두 사이트 공유)
   marked.js 렌더 + 콜아웃/형광/칩/KPI/Mermaid/Chart 후처리.
   marked, hljs, mermaid, Chart 는 각 HTML에서 CDN으로 로드.
   ============================================================ */
(function () {
  "use strict";

  var CALLOUT = {
    TIP: { cls: "tip", ico: "💡", label: "TIP" },
    NOTE: { cls: "note", ico: "📝", label: "NOTE" },
    WARNING: { cls: "warning", ico: "⚠️", label: "주의" },
    IMPORTANT: { cls: "important", ico: "📌", label: "중요" },
    EXAMPLE: { cls: "example", ico: "🧪", label: "예시" },
    DANGER: { cls: "danger", ico: "🚫", label: "경고" },
    CAUTION: { cls: "danger", ico: "⚠️", label: "주의" }
  };

  /* ---- marked 확장: ==형광== 과 [[chip:라벨]] ---- */
  function installMarkedExtensions() {
    if (!window.marked || !marked.use) return;
    marked.use({
      extensions: [
        {
          name: "highlight", level: "inline",
          start: function (src) { return src.indexOf("=="); },
          tokenizer: function (src) {
            var m = /^==(?!=)([\s\S]+?)==/.exec(src);
            // 인라인 자식 토큰은 tokenizer 컨텍스트(this.lexer)에서 생성한다.
            if (m) return { type: "highlight", raw: m[0], text: m[1], tokens: this.lexer.inlineTokens(m[1]) };
          },
          renderer: function (t) { return "<mark>" + this.parser.parseInline(t.tokens) + "</mark>"; }
        },
        {
          name: "chip", level: "inline",
          start: function (src) { return src.indexOf("[[chip"); },
          tokenizer: function (src) {
            var m = /^\[\[chip(?::([a-z]+))?:\s*([^\]]+)\]\]/.exec(src);
            if (m) return { type: "chip", raw: m[0], variant: m[1] || "", text: m[2] };
          },
          renderer: function (t) {
            var v = t.variant ? " " + t.variant : "";
            return '<span class="chip' + v + '">' + t.text + "</span>";
          }
        }
      ]
    });
  }

  /* ---- blockquote → 콜아웃 변환 ----
     GitHub식: 첫 줄이 [!TIP] 등. 또는 기존 이모지(💡/⚠️/✅/📌/🧪) 시작도 매핑. */
  var EMOJI_MAP = { "💡": "TIP", "⚠️": "WARNING", "✅": "TIP", "📌": "IMPORTANT", "🧪": "EXAMPLE", "🚫": "DANGER", "📝": "NOTE" };

  function transformCallouts(root) {
    root.querySelectorAll("blockquote").forEach(function (bq) {
      var first = bq.querySelector("p");
      if (!first) return;
      var html = first.innerHTML;
      var text = first.textContent.trim();
      var type = null, titleOverride = null;

      var gh = /^\[!(TIP|NOTE|WARNING|IMPORTANT|EXAMPLE|DANGER|CAUTION)\]\s*/i.exec(text);
      if (gh) {
        type = gh[1].toUpperCase();
        html = html.replace(/^\s*\[!(TIP|NOTE|WARNING|IMPORTANT|EXAMPLE|DANGER|CAUTION)\]\s*/i, "");
        var rest = text.replace(/^\[![A-Za-z]+\]\s*/, "");
        if (rest && rest.length < 40 && bq.children.length > 1) titleOverride = rest, html = "";
      } else {
        var key = Object.keys(EMOJI_MAP).find(function (e) { return text.indexOf(e) === 0; });
        if (key) { type = EMOJI_MAP[key]; html = html.replace(key, "").replace(/^\s+/, ""); }
      }
      if (!type) return;

      var c = CALLOUT[type];
      var box = document.createElement("div");
      box.className = "callout " + c.cls;
      var titleEl = document.createElement("div");
      titleEl.className = "callout-title";
      titleEl.innerHTML = '<span class="ico">' + c.ico + "</span><span>" + (titleOverride || c.label) + "</span>";
      box.appendChild(titleEl);

      if (html.trim()) first.innerHTML = html; else first.remove();
      while (bq.firstChild) box.appendChild(bq.firstChild);
      bq.replaceWith(box);
    });
  }

  /* ---- ```kpi 펜스 → KPI 카드 그리드 ---- */
  function transformKpi(root) {
    root.querySelectorAll("pre > code.language-kpi").forEach(function (code) {
      var grid = document.createElement("div");
      grid.className = "kpi-grid";
      code.textContent.split("\n").forEach(function (line) {
        line = line.trim(); if (!line) return;
        var parts = line.split("|").map(function (s) { return s.trim(); });
        var card = document.createElement("div");
        card.className = "kpi-card";
        card.innerHTML =
          '<div class="kpi-value"></div><div class="kpi-label"></div>' +
          (parts[2] ? '<div class="kpi-sub"></div>' : "");
        card.querySelector(".kpi-value").textContent = parts[0] || "";
        card.querySelector(".kpi-label").textContent = parts[1] || "";
        if (parts[2]) card.querySelector(".kpi-sub").textContent = parts[2];
        grid.appendChild(card);
      });
      code.closest("pre").replaceWith(grid);
    });
  }

  /* ---- ```chart 펜스 → Chart.js ---- */
  function transformCharts(root) {
    if (!window.Chart) return;
    var i = 0;
    root.querySelectorAll("pre > code.language-chart").forEach(function (code) {
      var box = document.createElement("div");
      box.className = "chart-box";
      var canvas = document.createElement("canvas");
      canvas.id = "chart-" + (i++);
      box.appendChild(canvas);
      var pre = code.closest("pre");
      try {
        var cfg = JSON.parse(code.textContent);
        var caption = cfg.caption;
        if (caption) { delete cfg.caption; var cap = document.createElement("div"); cap.className = "chart-caption"; cap.textContent = caption; }
        if (cfg.options == null) cfg.options = {};
        if (cfg.options.responsive == null) cfg.options.responsive = true;
        pre.replaceWith(box);
        new Chart(canvas.getContext("2d"), cfg);
        if (cap) box.appendChild(cap);
      } catch (e) {
        box.innerHTML = '<div class="render-error">차트 렌더 실패: ' + (e.message || e) + "</div>";
        pre.replaceWith(box);
      }
    });
  }

  /* ---- ```mermaid 펜스 → mermaid 다이어그램 ---- */
  function transformMermaid(root) {
    var blocks = root.querySelectorAll("pre > code.language-mermaid");
    if (!blocks.length) return;
    blocks.forEach(function (code) {
      var box = document.createElement("div");
      box.className = "diagram";
      var inner = document.createElement("div");
      inner.className = "mermaid";
      inner.textContent = code.textContent;
      box.appendChild(inner);
      code.closest("pre").replaceWith(box);
    });
    if (window.mermaid) {
      try {
        mermaid.initialize({ startOnLoad: false, theme: "neutral", securityLevel: "loose" });
        mermaid.run({ querySelector: ".content .mermaid" });
      } catch (e) { /* fallback: 원본 텍스트 유지 */ }
    }
  }

  /* ---- 일반 코드블록 하이라이트 (mermaid/chart/kpi 제외) ---- */
  function highlightCode(root) {
    if (!window.hljs) return;
    root.querySelectorAll("pre code").forEach(function (block) {
      if (/language-(mermaid|chart|kpi)/.test(block.className)) return;
      try { hljs.highlightElement(block); } catch (e) {}
    });
  }

  /* ---- 제목 → id(slug) 부여 ----
     build.py 와 *동일한* slugify 규칙을 써야 본문 용어 링크의 #앵커가 일치한다.
     같은 문서 내 중복 제목은 -2, -3 ... 접미사를 등장 순서대로 붙인다. */
  function slugify(text) {
    return String(text).toLowerCase()
      .replace(/[^0-9a-z가-힣]+/g, "-")
      .replace(/^-+|-+$/g, "");
  }
  function addHeadingIds(root) {
    var seen = {};
    root.querySelectorAll("h1, h2, h3, h4").forEach(function (h) {
      if (h.id) return;
      var base = slugify(h.textContent || "");
      if (!base) return;
      seen[base] = (seen[base] || 0) + 1;
      h.id = seen[base] > 1 ? base + "-" + seen[base] : base;
    });
  }

  /* ---- 상호참조 자동 링크 ----
     build.py 가 페이지마다 주입한 window.XREF([[표시텍스트, href], ...])를 보고
     본문 텍스트에서 "세션 0N" · "S3" · "레슨 05" 같은 참조를 클릭 가능한 링크로 만든다.
     - 코드/링크/다이어그램/칩 내부는 건드리지 않는다(오탐·이중링크 방지).
     - window.XREF 가 없거나 비면 아무 것도 하지 않는다(basics 등 안전). */
  function escapeRe(s) { return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"); }
  function isAsciiKey(s) { return /^[A-Za-z0-9 ]+$/.test(s); }

  function linkifyXrefs(root) {
    var xref = window.XREF;
    if (!xref || !xref.length) return;
    var selfPage = window.SLUG ? window.SLUG + ".html" : null;

    // 글로벌 맵(다른 페이지 정의 섹션) — 대소문자 무시 → 소문자 키
    var entries = xref.slice();
    var hrefOf = {};
    entries.forEach(function (e) { hrefOf[e[0].toLowerCase()] = e[1]; });

    // 로컬 맵(같은 문서 #앵커: 용어 정의 섹션 / §N 참조). [key, "#anchor", defSecId|null]
    var localList = window.XREF_LOCAL || [];
    var localMap = {};
    localList.forEach(function (e) { localMap[e[0].toLowerCase()] = { a: e[1], d: e[2] }; });

    // 정규식: 글로벌 + 로컬(§N 등) 키 합집합, 긴 것 우선(부분 겹침 방지)
    var allKeys = entries.map(function (e) { return e[0]; })
      .concat(localList.map(function (e) { return e[0]; }))
      .sort(function (a, b) { return b.length - a.length; });
    var combined = new RegExp(allKeys.map(escapeRe).join("|"), "gi");

    var SKIP = { A: 1, CODE: 1, PRE: 1, BUTTON: 1 };
    function inSkip(node) {
      for (var el = node.parentNode; el && el !== root; el = el.parentNode) {
        if (el.nodeType !== 1) continue;
        if (SKIP[el.tagName]) return true;
        var c = el.className;
        if (typeof c === "string" && /\b(mermaid|diagram|chip|chart-box|kpi-card)\b/.test(c)) return true;
      }
      return false;
    }
    // 매치 경계 검증: 숫자 확장(세션 1↔세션 10) 금지, ASCII 키는 앞뒤 영숫자 금지(S2↔OS2/S2B)
    function valid(key, before, after) {
      if (/[A-Za-z0-9]/.test(before)) return false;
      if (/[0-9]/.test(after)) return false;
      if (isAsciiKey(key) && /[A-Za-z]/.test(after)) return false;
      return true;
    }

    // 문서 순서대로 순회하며 현재 섹션(가장 가까운 앞 heading id)을 추적
    var targets = [], cur = null;
    var walker = document.createTreeWalker(root, NodeFilter.SHOW_ELEMENT | NodeFilter.SHOW_TEXT, null);
    for (var n = walker.nextNode(); n; n = walker.nextNode()) {
      if (n.nodeType === 1) {
        if (/^H[1-4]$/.test(n.tagName) && n.id) cur = n.id;
        continue;
      }
      if (n.nodeValue && !inSkip(n)) {
        combined.lastIndex = 0;
        if (combined.test(n.nodeValue)) targets.push({ node: n, sec: cur });
      }
    }

    targets.forEach(function (t) {
      var text = t.node.nodeValue, sec = t.sec, last = 0, m;
      var frag = document.createDocumentFragment(), changed = false;
      combined.lastIndex = 0;
      while ((m = combined.exec(text))) {
        var key = m[0], i = m.index;
        var before = i > 0 ? text[i - 1] : "";
        var after = i + key.length < text.length ? text[i + key.length] : "";
        if (!valid(key, before, after)) continue;
        var lc = key.toLowerCase(), href = null;
        var loc = localMap[lc];
        if (loc) {
          // 같은 문서: 정의 섹션(또는 §의 대상 섹션) 안에서는 링크하지 않음
          var skipSec = loc.d || loc.a.slice(1);
          if (sec && sec === skipSec) continue;
          href = loc.a;                                  // "#앵커" (같은 페이지)
        } else {
          href = hrefOf[lc];                             // 다른 페이지 정의 섹션
          if (!href || (selfPage && href.split("#")[0] === selfPage)) continue;
        }
        if (i > last) frag.appendChild(document.createTextNode(text.slice(last, i)));
        var a = document.createElement("a");
        a.className = "xref"; a.href = href; a.textContent = key;
        frag.appendChild(a);
        last = i + key.length; changed = true;
      }
      if (!changed) return;
      if (last < text.length) frag.appendChild(document.createTextNode(text.slice(last)));
      t.node.parentNode.replaceChild(frag, t.node);
    });
  }

  /* ---- 표를 스크롤 래퍼로 감싸기 ---- */
  function wrapTables(root) {
    root.querySelectorAll("table").forEach(function (tb) {
      if (tb.parentElement && tb.parentElement.classList.contains("table-wrap")) return;
      var w = document.createElement("div"); w.className = "table-wrap";
      tb.replaceWith(w); w.appendChild(tb);
    });
  }

  /* ---- 부팅 ---- */
  function render() {
    var src = document.getElementById("md-src");
    var target = document.getElementById("content");
    if (src && target && window.marked) {
      // 1) 마크다운 렌더 (확장 실패 시에도 본문은 반드시 표시 — 빈 화면 방지)
      try {
        installMarkedExtensions();
        marked.setOptions({ gfm: true, breaks: false });
        target.innerHTML = marked.parse(src.textContent);
      } catch (e) {
        try { target.innerHTML = marked.parse(src.textContent); }
        catch (e2) { target.textContent = src.textContent; }
      }
      // 2) 후처리: 각 단계가 독립 try/catch — 하나가 실패해도 나머지는 진행
      [transformKpi, transformMermaid, transformCharts, transformCallouts, wrapTables, addHeadingIds, linkifyXrefs, highlightCode]
        .forEach(function (fn) { try { fn(target); } catch (e) {} });
    }
    var toggle = document.querySelector(".menu-toggle");
    var sidebar = document.querySelector(".sidebar");
    if (toggle && sidebar) {
      toggle.addEventListener("click", function () { sidebar.classList.toggle("open"); });
      document.querySelectorAll(".sidebar nav a").forEach(function (a) {
        a.addEventListener("click", function () { sidebar.classList.remove("open"); });
      });
    }
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", render);
  else render();
})();
