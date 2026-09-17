/* deryee.pro — 站内搜索（纯前端，读 search-index.json） */
(function () {
  var input = document.getElementById("q");
  var out = document.getElementById("results");
  var INDEX = [];
  var base = window.SITE_BASE || "./";

  fetch(base + "assets/search-index.json")
    .then(function (r) { return r.json(); })
    .then(function (data) { INDEX = data; })
    .catch(function () {
      if (out) out.innerHTML = '<p style="color:var(--ink-3)">索引加载失败，请通过 http 访问本页。</p>';
    });

  function score(item, kw) {
    var s = 0;
    if (item.title && item.title.toLowerCase().indexOf(kw) > -1) s += 3;
    if (item.desc && item.desc.toLowerCase().indexOf(kw) > -1) s += 2;
    if (item.text && item.text.toLowerCase().indexOf(kw) > -1) s += 1;
    return s;
  }

  function render(kw) {
    if (!out) return;
    if (!kw) { out.innerHTML = ""; return; }
    var hits = INDEX.map(function (it) { return { it: it, s: score(it, kw) }; })
      .filter(function (x) { return x.s > 0; })
      .sort(function (a, b) { return b.s - a.s; })
      .slice(0, 20);
    if (!hits.length) {
      out.innerHTML = '<p style="color:var(--ink-3)">没有找到「' + kw + '」相关内容。</p>';
      return;
    }
    out.innerHTML = '<div class="post-list">' + hits.map(function (h) {
      return '<a class="post-item" href="' + h.it.url + '">' +
        '<span class="post-item__tag">' + (h.it.category || "页面") + '</span>' +
        '<div class="post-item__title">' + h.it.title + '</div>' +
        '<p class="post-item__excerpt">' + (h.it.desc || "") + '</p></a>';
    }).join("") + "</div>";
  }

  if (input) {
    input.addEventListener("input", function () { render(input.value.trim().toLowerCase()); });
    input.addEventListener("keydown", function (e) { if (e.key === "Enter") render(input.value.trim().toLowerCase()); });
    input.focus();
  }
})();
