/* deryee.pro — 主题初始化（放在 <head> 内联调用，防闪烁） */
(function () {
  try {
    var saved = localStorage.getItem("deryee-theme");
    if (saved === "dark" || saved === "light") {
      document.documentElement.setAttribute("data-theme", saved);
    }
  } catch (e) { /* localStorage 不可用时跟随系统 */ }
})();
