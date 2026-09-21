/* deryee.pro — 简繁切换运行时
 * 在 <head> 同步加载（防闪烁），职责：
 *   1. 语种判定（localStorage → 浏览器语言）
 *   2. 首访若偏好繁体且不在镜像页 → location.replace 到 /zh-tw/（<body> 解析前完成，零闪烁）
 *   3. 手动切换：懒加载词典 → 无刷新即时转换 DOM + history.replaceState 同步网址
 *   4. 暴露 T()：供 nav/social/dock/search 在生成文案时调用，运行时注入内容自动跟随
 *
 * 算法与 tools/_s2t.py 逐字对应，共用 assets/lang-table.js 同一份映射表。
 * ============================================================ */
(function () {
  var KEY = "deryee-lang";
  var SITE_HOST = "https://deryee.pro";
  var path = location.pathname;
  var isMirror = /^\/zh-tw(\/|$)/.test(path);
  var NO_TOGGLE = /^\/(404|icon-preview)\.html$/;

  /* ---------- 路径与 base ---------- */
  function plainPath() {
    var p = path.replace(/^\/zh-tw(?=\/|$)/, "");
    return p || "/";
  }
  var depth = (path.match(/\//g) || []).length - 1;          // /zh-tw/about/ -> 2
  var up = function (n) { return n <= 0 ? "./" : new Array(n + 1).join("../"); };
  var ASSET = up(depth);                                     // 站点根（CSS/JS/图片）
  var LINK = isMirror ? up(depth - 1) : up(depth);           // 站内互链根（镜像页留在镜像内）

  window.DERYEE_ASSET_BASE = ASSET;
  window.SITE_BASE = LINK;                                   // nav.js / search.js 使用

  var TARGET = NO_TOGGLE.test(path) ? null
    : (isMirror ? plainPath() : "/zh-tw" + (path === "/" ? "/" : path)) + location.search + location.hash;
  window.DERYEE_TOGGLE_URL = TARGET;

  /* ---------- 偏好判定 ---------- */
  function wantsHant() {
    var langs = navigator.languages || [navigator.language || ""];
    for (var i = 0; i < langs.length; i++) {
      var l = String(langs[i] || "").toLowerCase();
      if (/^zh\b/.test(l)) {
        if (/-hant|-(tw|hk|mo)\b/.test(l)) return true;
        return false;                                        // 显式简体即停
      }
    }
    return false;
  }
  var pref = null;
  try { pref = localStorage.getItem(KEY); } catch (e) {}
  if (pref !== "zh-Hans" && pref !== "zh-Hant") {
    pref = wantsHant() ? "zh-Hant" : "zh-Hans";
    try { localStorage.setItem(KEY, pref); } catch (e) {}
  }

  /* ---------- 首访自动进入镜像（零闪烁） ---------- */
  if (pref === "zh-Hant" && !isMirror && TARGET) {
    var bounces = 0;
    try { bounces = parseInt(sessionStorage.getItem("deryee-lang-bounce") || "0", 10); } catch (e) {}
    if (bounces < 2) {
      try { sessionStorage.setItem("deryee-lang-bounce", String(bounces + 1)); } catch (e) {}
      location.replace(TARGET);
      return;
    }
  }

  window.DERYEE_LANG = isMirror ? "zh-Hant" : "zh-Hans";

  /* ---------- 转换核心（与 Python 端一致） ---------- */
  var SENT = "\uE000";
  function phrases(s, map, maxlen) {
    if (!map || maxlen < 2) return s;
    var out = "", i = 0, n = s.length;
    while (i < n) {
      var hitLen = 0, hitVal = null;
      var upper = maxlen < (n - i) ? maxlen : (n - i);
      for (var L = upper; L > 1; L--) {
        var v = map[s.substr(i, L)];
        if (v !== undefined) { hitLen = L; hitVal = v; break; }
      }
      if (hitLen) { out += hitVal; i += hitLen; } else { out += s.charAt(i); i++; }
    }
    return out;
  }
  function chars(s, map) {
    if (!map) return s;
    var out = "", i;
    for (i = 0; i < s.length; i++) {
      var c = s.charAt(i);
      out += (map[c] !== undefined ? map[c] : c);
    }
    return out;
  }
  function convert(s) {
    var t = window.DERYEE_LANG_TABLE;
    if (!t || !s) return s;
    var store = [], i, ph, word;
    /* 1. protect 掩码 */
    var prot = (t.protect || []).slice().sort(function (a, b) { return b.length - a.length; });
    for (i = 0; i < prot.length; i++) {
      word = prot[i];
      if (word && s.indexOf(word) > -1) {
        ph = SENT + i + SENT;
        store.push([ph, word]);
        s = s.split(word).join(ph);
      }
    }
    /* 2. overrides（结果立即冻结，防止被台湾词组二次改写） */
    s = phrases(s, t.overrides, t.maxOverrideLen || 0);
    var vals = [], seen = {};
    for (var k in t.overrides) {
      if (t.overrides.hasOwnProperty(k) && !seen[t.overrides[k]]) {
        seen[t.overrides[k]] = 1;
        vals.push(t.overrides[k]);
      }
    }
    vals.sort(function (a, b) { return b.length - a.length; });
    for (i = 0; i < vals.length; i++) {
      word = vals[i];
      if (word && s.indexOf(word) > -1) {
        ph = SENT + (prot.length + i) + SENT;
        store.push([ph, word]);
        s = s.split(word).join(ph);
      }
    }
    /* 3-6 词典链 */
    s = phrases(s, t.s2tPhrases, t.maxS2tLen || 0);
    s = chars(s, t.chars);
    s = phrases(s, t.twPhrases, t.maxTwLen || 0);
    s = chars(s, t.twVariants);
    /* 7. 还原 */
    for (i = 0; i < store.length; i++) s = s.split(store[i][0]).join(store[i][1]);
    return s;
  }

  /* ---------- T()：未加载词典或简体态时恒等 ---------- */
  window.T = function (s) {
    if (!s || typeof s !== "string") return s;
    if (window.DERYEE_LANG !== "zh-Hant") return s;
    if (!window.DERYEE_LANG_TABLE) return s;
    return convert(s);
  };

  /* ---------- 懒加载词典 ---------- */
  window.deryeeLoadTable = function (cb) {
    if (window.DERYEE_LANG_TABLE) { if (cb) cb(); return; }
    var s = document.createElement("script");
    s.src = ASSET + "assets/lang-table.js";
    s.onload = function () { if (cb) cb(); };
    document.head.appendChild(s);
  };

  /* ---------- 无刷新即时切换 ---------- */
  var ATTRS = ["title", "aria-label", "alt", "placeholder"];
  var SKIP_TAGS = { SCRIPT: 1, STYLE: 1, CODE: 1, PRE: 1, SVG: 1, NOSCRIPT: 1, TEXTAREA: 1 };
  var snapshot = null;                                       // 已转换时保存的原文

  function skipNode(node) {
    var p = node.parentNode;
    while (p && p !== document.body) {
      if (SKIP_TAGS[p.nodeName]) return true;
      p = p.parentNode;
    }
    return false;
  }

  function toHant() {
    var texts = [], attrs = [];
    var tw = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, null, false);
    while (tw.nextNode()) {
      var n = tw.currentNode;
      if (!n.nodeValue || !n.nodeValue.trim()) continue;
      if (skipNode(n)) continue;
      texts.push(n);
    }
    var els = document.body.querySelectorAll("[" + ATTRS.join("],[") + "]");
    for (var i = 0; i < els.length; i++) attrs.push(els[i]);

    snapshot = { texts: [], attrs: [], title: document.title };
    texts.forEach(function (n) {
      snapshot.texts.push([n, n.nodeValue]);
      n.nodeValue = convert(n.nodeValue);
    });
    attrs.forEach(function (el) {
      ATTRS.forEach(function (a) {
        if (!el.hasAttribute(a)) return;
        var v = el.getAttribute(a);
        snapshot.attrs.push([el, a, v]);
        el.setAttribute(a, convert(v));
      });
    });
    document.title = convert(document.title);
  }

  function toHans() {
    if (!snapshot) return;
    snapshot.texts.forEach(function (p) { p[0].nodeValue = p[1]; });
    snapshot.attrs.forEach(function (p) { p[0].setAttribute(p[1], p[2]); });
    document.title = snapshot.title;
    snapshot = null;
  }

  function fire(lang) {
    try {
      document.dispatchEvent(new CustomEvent("deryee:lang", { detail: { lang: lang } }));
    } catch (e) {}
  }

  window.deryeeSetLang = function (lang) {
    var wantHant = lang === "zh-Hant";
    try { localStorage.setItem(KEY, wantHant ? "zh-Hant" : "zh-Hans"); } catch (e) {}

    if (wantHant) {
      window.deryeeLoadTable(function () {
        if (window.DERYEE_LANG !== "zh-Hant") toHant();
        window.DERYEE_LANG = "zh-Hant";
        if (TARGET) { try { history.replaceState(null, "", TARGET); } catch (e) {} }
        fire("zh-Hant");
      });
    } else {
      toHans();
      window.DERYEE_LANG = "zh-Hans";
      if (TARGET) { try { history.replaceState(null, "", TARGET); } catch (e) {} }
      fire("zh-Hans");
    }
  };

  /* 供 nav.js 判断是否显示按钮 */
  window.DERYEE_CAN_TOGGLE = !!TARGET;
  window.DERYEE_MIRROR_HOST = SITE_HOST;
})();
