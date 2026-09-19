/* deryee.pro — 注入式共享导航 + 移动端菜单 + 主题切换 */
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
  var themeIcon = function () {
    var cur = document.documentElement.getAttribute("data-theme") ||
      (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
    return cur === "dark" ? "☀️" : "🌙";
  };

  var links = [
    { href: base + "about/", label: "关于我", key: "about" },
    { href: base + "system/", label: "我的体系", key: "system" },
    { href: base + "articles/", label: "文章", key: "articles" },
    { href: base + "knowledge/", label: "知识栏目", key: "knowledge" }
  ];

  var html = '' +
    '<div class="nav__inner">' +
    '  <a class="nav__brand" href="' + base + '"><span class="brand-dot"></span>德益师兄<span style="color:var(--ink-3)">Deryee</span></a>' +
    '  <nav class="nav__links" aria-label="主导航">' +
    links.map(function (l) {
      return '<a class="nav__link' + (page === l.key ? " is-active" : "") + '" href="' + l.href + '">' + l.label + "</a>";
    }).join("") +
    '  </nav>' +
    '  <a class="nav__search" href="' + base + 'search.html">搜索</a>' +
    '  <button class="nav__theme" id="themeToggle" aria-label="切换深浅色">' + themeIcon() + "</button>" +
    '  <button class="nav__burger" id="navBurger" aria-label="打开菜单">☰</button>' +
    "</div>" +
    '<nav class="nav__mobile" id="navMobile" aria-label="移动端导航">' +
    links.map(function (l) {
      return '<a class="nav__link' + (page === l.key ? " is-active" : "") + '" href="' + l.href + '">' + l.label + "</a>";
    }).join("") +
    '  <a class="nav__link" href="' + base + 'search.html">搜索</a>' +
    "</nav>";

  var host = document.getElementById("site-nav");
  if (!host) { document.body.insertAdjacentHTML("afterbegin", '<header class="nav" id="site-nav">' + html + "</header>"); }
  else { host.className = "nav"; host.innerHTML = html; }

  // 主题切换
  var toggle = document.getElementById("themeToggle");
  if (toggle) {
    toggle.addEventListener("click", function () {
      var cur = document.documentElement.getAttribute("data-theme") ||
        (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
      var next = cur === "dark" ? "light" : "dark";
      document.documentElement.setAttribute("data-theme", next);
      try { localStorage.setItem("deryee-theme", next); } catch (e) {}
      toggle.textContent = next === "dark" ? "☀️" : "🌙";
    });
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
})();
