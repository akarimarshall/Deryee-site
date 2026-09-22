/* deryee.pro — 注入式共享导航 + 移动端菜单 + 主题切换 + 简繁切换 */
(function () {
  // 按当前路径深度自动推算相对根路径：/ → ./ ；/about/ → ../ ；/articles/xx/ → ../../
  var autoBase = (function () {
    var p = location.pathname.replace(/index\.html$/, "");
    var depth = (p.match(/\//g) || []).length - 1;
    if (depth < 1) return "./";
    return new Array(depth + 1).join("../");
  })();
  var base = window.SITE_BASE || autoBase;
  var page = document.body.getAttribute("data-page") || "";

  // T()：lang.js 提供；简体态恒等
  var T = window.T || function (s) { return s; };

  var themeIcon = function () {
    var cur = document.documentElement.getAttribute("data-theme") ||
      (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
    return cur === "dark" ? "☀️" : "🌙";
  };

  var links = [
    { href: base, label: T("关于我"), key: "about", cls: "js-home-top" },
    { href: base + "system/", label: T("我的体系"), key: "system" },
    { href: base + "articles/", label: T("文章"), key: "articles" },
    { href: base + "knowledge/", label: T("知识栏目"), key: "knowledge" },
    { href: base + "resources/", label: T("资料下载"), key: "resources" }
  ];

  // 简繁切换按钮（无对应镜像的页面不渲染）
  var langHtml = "";
  if (window.DERYEE_CAN_TOGGLE !== false && window.deryeeSetLang) {
    var isHant = window.DERYEE_LANG === "zh-Hant";
    langHtml = '<button class="nav__lang" id="langToggle" aria-label="' +
      T(isHant ? "切换为简体中文" : "切换为繁体中文") + '" title="' +
      T(isHant ? "切换为简体中文" : "切换为繁体中文") + '">' +
      (isHant ? "簡" : "繁") + "</button>";
  }

  var html = '' +
    '<div class="nav__inner">' +
    '  <a class="nav__brand" href="' + base + '"><span class="brand-dot"></span>' + T("德益师兄") + '<span style="color:var(--ink-3)">Deryee</span></a>' +
    '  <nav class="nav__links" aria-label="主导航">' +
    links.map(function (l) {
      return '<a class="nav__link' + (page === l.key ? " is-active" : "") + (l.cls ? " " + l.cls : "") + '" href="' + l.href + '">' + l.label + "</a>";
    }).join("") +
    '  </nav>' +
    '  <a class="nav__search" href="' + base + 'search.html">' + T("搜索") + '</a>' +
    '  <button class="nav__theme" id="themeToggle" aria-label="' + T("切换深浅色") + '">' + themeIcon() + "</button>" +
    langHtml +
    '  <button class="nav__burger" id="navBurger" aria-label="' + T("打开菜单") + '">☰</button>' +
    "</div>" +
    '<nav class="nav__mobile" id="navMobile" aria-label="移动端导航">' +
    links.map(function (l) {
      return '<a class="nav__link' + (page === l.key ? " is-active" : "") + (l.cls ? " " + l.cls : "") + '" href="' + l.href + '">' + l.label + "</a>";
    }).join("") +
    '  <a class="nav__link" href="' + base + 'search.html">' + T("搜索") + "</a>" +
    "</nav>";

  var host = document.getElementById("site-nav");
  if (!host) { document.body.insertAdjacentHTML("afterbegin", '<header class="nav" id="site-nav">' + html + "</header>"); }
  else { host.className = "nav"; host.innerHTML = html; }

  // 主题切换
  var toggle = document.getElementById("themeToggle");
  if (toggle) {
    toggle.addEventListener("click", function () {
      var cur = document.documentElement.getAttribute("data-theme") ||
        (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
      var next = cur === "dark" ? "light" : "dark";
      document.documentElement.setAttribute("data-theme", next);
      try { localStorage.setItem("deryee-theme", next); } catch (e) {}
      toggle.textContent = next === "dark" ? "☀️" : "🌙";
    });
  }

  // 简繁切换
  var langBtn = document.getElementById("langToggle");
  function syncLangBtn(lang) {
    if (!langBtn) return;
    var isHant = lang === "zh-Hant";
    langBtn.textContent = isHant ? "簡" : "繁";
    var label = T(isHant ? "切换为简体中文" : "切换为繁体中文");
    langBtn.setAttribute("aria-label", label);
    langBtn.setAttribute("title", label);
  }
  if (langBtn) {
    langBtn.addEventListener("click", function () {
      window.deryeeSetLang(window.DERYEE_LANG === "zh-Hant" ? "zh-Hans" : "zh-Hant");
    });
    document.addEventListener("deryee:lang", function (e) { syncLangBtn(e.detail.lang); });
  }

  // 移动端菜单
  var burger = document.getElementById("navBurger");
  var mobile = document.getElementById("navMobile");
  if (burger && mobile) {
    burger.addEventListener("click", function () {
      mobile.classList.toggle("is-open");
      burger.textContent = mobile.classList.contains("is-open") ? "✕" : "☰";
    });
  }

  /* ---------- 关于我：回首页顶端（不跳转到已删除的 about 页） ---------- */
  function goHomeOrScroll(e) {
    e.preventDefault();
    if (page === "home") {
      window.scrollTo({ top: 0, behavior: "smooth" });
    } else {
      window.location.href = new URL(base, location.href).href;
    }
  }
  document.addEventListener("click", function (e) {
    var el = e.target.closest && e.target.closest('.js-home-top, a[href$="about/"]');
    if (el) goHomeOrScroll(e);
  });

  /* ---------- 站内搜索：同页浮层（导航栏保持在上方） ---------- */
  var searchIndexUrl = base + (location.pathname.indexOf("/zh-tw/") === 0 ? "zh-tw/assets/search-index.json" : "assets/search-index.json");
  var searchIndex = [];
  function buildSearchOverlay() {
    if (document.getElementById("searchOverlay")) return;
    var box = document.createElement("div");
    box.className = "search-overlay";
    box.id = "searchOverlay";
    box.setAttribute("aria-hidden", "true");
    box.innerHTML =
      '<div class="search-overlay__backdrop"></div>' +
      '<div class="search-overlay__panel" role="dialog" aria-modal="true" aria-label="' + T("站内搜索") + '">' +
      '  <input class="search-input search-overlay__input" id="searchOverlayInput" type="search" placeholder="' + T("输入关键词，回车搜索…") + '" autocomplete="off">' +
      '  <div class="search-overlay__results" id="searchOverlayResults"></div>' +
      '  <p class="search-overlay__hint">' + T("Esc 或点击空白处关闭") + '</p>' +
      "</div>";
    document.body.appendChild(box);
    var input = box.querySelector("#searchOverlayInput");
    var out = box.querySelector("#searchOverlayResults");
    fetch(searchIndexUrl)
      .then(function (r) { return r.json(); })
      .then(function (data) { searchIndex = data; })
      .catch(function () { if (out) out.innerHTML = '<p style="color:var(--ink-3)">' + T("索引加载失败，请通过 http 访问本站。") + "</p>"; });
    function score(item, kw) {
      var s = 0, k = T(kw);
      if (item.title && T(item.title).toLowerCase().indexOf(k) > -1) s += 3;
      if (item.desc && T(item.desc).toLowerCase().indexOf(k) > -1) s += 2;
      if (item.text && T(item.text).toLowerCase().indexOf(k) > -1) s += 1;
      return s;
    }
    function render(kw) {
      if (!out) return;
      if (!kw) { out.innerHTML = ""; return; }
      var hits = searchIndex.map(function (it) { return { it: it, s: score(it, kw) }; })
        .filter(function (x) { return x.s > 0; })
        .sort(function (a, b) { return b.s - a.s; })
        .slice(0, 20);
      if (!hits.length) { out.innerHTML = '<p style="color:var(--ink-3)">' + T("没有找到「") + kw + T("」相关内容。") + "</p>"; return; }
      out.innerHTML = '<div class="post-list">' + hits.map(function (h) {
        return '<a class="post-item" href="' + h.it.url + '">' +
          '<span class="post-item__tag">' + (h.it.category || T("页面")) + '</span>' +
          '<div class="post-item__title">' + h.it.title + '</div>' +
          '<p class="post-item__excerpt">' + (h.it.desc || "") + '</p></a>';
      }).join("") + "</div>";
    }
    input.addEventListener("input", function () { render(input.value.trim().toLowerCase()); });
    input.addEventListener("keydown", function (e) { if (e.key === "Enter") render(input.value.trim().toLowerCase()); });
    box.querySelector(".search-overlay__backdrop").addEventListener("click", closeSearch);
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") closeSearch(); });
    out.addEventListener("click", function (e) { if (e.target.closest(".post-item")) closeSearch(); });
  }
  function openSearch() {
    buildSearchOverlay();
    var box = document.getElementById("searchOverlay");
    if (!box) return;
    box.classList.add("is-open");
    box.setAttribute("aria-hidden", "false");
    var input = box.querySelector("#searchOverlayInput");
    if (input) { input.value = ""; var out = box.querySelector("#searchOverlayResults"); if (out) out.innerHTML = ""; setTimeout(function () { input.focus(); }, 30); }
  }
  function closeSearch() {
    var box = document.getElementById("searchOverlay");
    if (box) { box.classList.remove("is-open"); box.setAttribute("aria-hidden", "true"); }
  }
  document.addEventListener("click", function (e) {
    var el = e.target.closest && e.target.closest('a[href$="search.html"]');
    if (el) { e.preventDefault(); openSearch(); }
  });
})();
