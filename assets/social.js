/* deryee.pro — 社交图标导航（多容器）
 * 职责：注入图标行 + 智能跳转
 *   · 通用链接平台（抖音/B站/小红书/视频号/FlowUs）→ 直接 href，
 *     手机端由系统自动唤起 App，未安装则落到网页，无需额外 JS
 *   · 微信系（工作号/公众号/视频号）无法从外部深链跳转 → 弹二维码
 *   · 工作邮箱 → mailto:，系统自动唤起邮件 App
 * 容器：任意 id 以 "social-row" 开头的元素（支持一页多处）
 * 图标：内联 ICONS 表（24×24 viewBox，fill 用 currentColor）
 * ============================================================ */

(function () {
  /* T()：lang.js 提供；简体态恒等。二维码用站点绝对路径，
     这样在简繁切换改写了网址（history.replaceState）之后依然能正确取到。 */
  var T = window.T || function (s) { return s; };

  /* ---------- 平台配置：此处填写：正式链接 ---------- */
  var PLATFORMS = [
    { key: "email",        label: "工作邮箱",   href: "此处填写：邮箱地址（保持 mailto: 前缀）" },
    { key: "wechat-work",  label: "微信工作号", href: "#", qr: "/assets/qr/wechat-work.png" },
    { key: "wechat-mp",    label: "微信公众号", href: "#", qr: "/assets/qr/wechat-mp.png" },
    { key: "channels",     label: "视频号",     href: "此处填写：视频号主页链接", qr: "/assets/qr/channels.png" },
    { key: "douyin",       label: "抖音",       href: "此处填写：抖音主页链接" },
    { key: "xiaohongshu",  label: "小红书",     href: "此处填写：小红书主页链接" },
    { key: "bilibili",     label: "B站",        href: "此处填写：B站空间链接" },
    { key: "flowus",       label: "FlowUs",     href: "此处填写：FlowUs 链接" }
  ];

  var hosts = document.querySelectorAll('[id^="social-row"]');
  if (!hosts.length) return;

  /* ---------- base 推算（与 nav.js 同逻辑） ---------- */
  var base = (function () {
    var p = location.pathname.replace(/index\.html$/, "");
    var depth = (p.match(/\//g) || []).length - 1;
    return depth < 1 ? "./" : new Array(depth + 1).join("../");
  })();

  function resolve(path) {
    if (!path) return path;
    if (path.indexOf("://") > -1 || path.charAt(0) === "/") return path;   // 绝对地址原样
    return base + path;
  }

  /* ---------- 图标（内联，避免 fetch / file:// 限制） ---------- */
  var fallback = '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9" fill="currentColor" opacity=".35"/></svg>';

  var ICONS = window.DERYEE_SOCIAL_ICONS || {};

  /* ---------- 注入 ---------- */
  var html = PLATFORMS.map(function (p) {
    var href = resolve(p.href);
    var isMail = href.indexOf("mailto:") === 0;
    return '<a class="social-link" href="' + href + '"' +
      (p.qr ? ' data-qr="' + resolve(p.qr) + '" data-label="' + p.label + '"' : "") +
      ' aria-label="' + T(p.label) + '" title="' + T(p.label) + '"' +
      (isMail || p.qr ? "" : ' target="_blank" rel="noopener"') +
      ">" +
      '<span class="social-icon">' + (ICONS[p.key] || fallback) + "</span>" +
      "</a>";
  }).join("");

  hosts.forEach(function (host, i) {
    /* 容器内原有的说明文字保留在最前 */
    var keep = i === 0 ? host.innerHTML : "";
    host.innerHTML = keep + html;
  });

  /* ---------- 二维码弹窗 ---------- */
  var modal = document.createElement("div");
  modal.className = "qr-modal";
  modal.setAttribute("aria-hidden", "true");
  modal.innerHTML =
    '<div class="qr-modal__backdrop"></div>' +
    '<div class="qr-modal__card" role="dialog" aria-modal="true">' +
    '  <button class="qr-modal__close" aria-label="' + T("关闭") + '">✕</button>' +
    '  <h3 class="qr-modal__title"></h3>' +
    '  <div class="qr-modal__img"></div>' +
    '  <p class="qr-modal__tip">' + T("手机端：截图后打开对应 App「扫一扫」识别") + '<br>' +
    T("电脑端：用手机扫屏幕上的二维码") + "</p>" +
    "</div>";
  document.body.appendChild(modal);

  function openQr(label, qrSrc) {
    modal.querySelector(".qr-modal__title").textContent = T(label) + T(" · 扫码添加");
    var box = modal.querySelector(".qr-modal__img");
    box.innerHTML = "";
    var img = new Image();
    img.src = qrSrc;
    img.alt = T(label) + T("二维码");
    box.appendChild(img);
    modal.classList.add("is-open");
    modal.setAttribute("aria-hidden", "false");
  }
  function closeQr() {
    modal.classList.remove("is-open");
    modal.setAttribute("aria-hidden", "true");
  }
  modal.querySelector(".qr-modal__close").addEventListener("click", closeQr);
  modal.querySelector(".qr-modal__backdrop").addEventListener("click", closeQr);
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") closeQr(); });

  /* ---------- 点击分发 ---------- */
  document.addEventListener("click", function (e) {
    var link = e.target.closest && e.target.closest(".social-link");
    if (!link) return;
    if (!link.getAttribute("data-qr")) return;   // 其余平台走默认跳转
    e.preventDefault();
    openQr(link.getAttribute("data-label"), link.getAttribute("data-qr"));
  });
})();
