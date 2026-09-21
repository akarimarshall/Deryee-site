/* deryee.pro — knowledge 页：视图切换 + T0–T8 时序播放器 + 详情抽屉 */
(function () {
  /* T()：lang.js 提供；简体态恒等。所有渲染出口都过一层，切繁后新生成的内容自动跟随 */
  var T = window.T || function (s) { return s; };

  /* ---------- 数据 ---------- */
  var STEPS = [
    { id: "T0", label: "项目启动", born: ["T0"] },
    { id: "T1", label: "元规则就位", born: ["T1"] },
    { id: "T2", label: "路线图确认", born: ["T2"] },
    { id: "T3", label: "方案生成", born: [] },
    { id: "T4", label: "过程留痕", born: ["T4"] },
    { id: "T5", label: "外部输入", born: ["T5"] },
    { id: "T6", label: "经验萃取", born: ["T6"] },
    { id: "T7", label: "入库归档", born: ["T7"] },
    { id: "T8", label: "知识回流", born: ["T8"] }
  ];

  var DETAILS = {
    agents: { title: "AGENTS.md · 元规则", rows: [["职责", "定义全项目角色分工与协作边界"], ["触发点", "项目启动时创建，变更需全员确认"], ["沉淀", "经验沉淀触发点写在本文件"]] },
    claude: { title: "CLAUDE.md · 主控配置", rows: [["职责", "主控 Agent 启动加载"], ["内容", "工具白名单、安全边界、语言偏好"]] },
    roadmap: { title: "ROADMAP.md · 里程碑", rows: [["职责", "记录阶段目标与当前进度"], ["更新", "每个里程碑完成时更新"]] },
    log: { title: "LOG/ · 时序目录", rows: [["职责", "按时序记录每一步做了什么、为什么"], ["命名", "T编号-事件名.md"], ["价值", "经验萃取的原料"]] },
    proc: { title: "PROC/ · 过程制品", rows: [["职责", "草稿与中间产物暂存"], ["清理", "项目结项时归档或删除"]] },
    topic: { title: "TOPIC.md · 主题笔记", rows: [["职责", "本项目萃取出的可复用知识"], ["去向", "结项时迁入知识库并登记索引"]] },
    ext: { title: "EXT/ · 外部输入", rows: [["职责", "存放用户提供的资料与外部参考"], ["规则", "只读，修改需登记"]] },
    ref: { title: "REF/ + CITED.md · 引用", rows: [["职责", "参考资料目录 + 引用登记表"], ["规则", "每条入库知识必须可追溯来源"]] },
    index: { title: "INDEX.md · 知识库索引", rows: [["职责", "全部主题笔记的总目录"], ["一致", "卡片数与索引数必须一致"]] },
    w1: { title: "经验萃取的四步法", rows: [["type", "method · stable"], ["步骤", "识别 → 提炼 → 卡片化 → 登记"], ["摘要", "从时序日志中识别高价值片段，四步萃取为知识卡。"]] },
    w2: { title: "引用登记规范", rows: [["type", "rule · stable"], ["规则", "无来源不入库"], ["摘要", "保证每条知识可追溯。"]] },
    w3: { title: "知识回流触发点", rows: [["type", "rule · stable"], ["节点", "新项目启动 / 方案评审 / 结项复盘"], ["摘要", "在固定节点强制检索既有知识。"]] },
    w4: { title: "卡片粒度原则", rows: [["type", "method · draft"], ["规则", "一卡一事，200 字以内"], ["摘要", "粒度决定复用率。"]] },
    w5: { title: "双链的意义", rows: [["type", "note · draft"], ["摘要", "用 [[双链]] 把卡片织成网而非树，检索靠关联而非目录。"]] }
  };

  /* ---------- 工具 ---------- */
  function $(s) { return document.querySelector(s); }
  function $all(s) { return Array.prototype.slice.call(document.querySelectorAll(s)); }
  var reduced = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------- 视图切换 ---------- */
  var tabIntro = $("#tabIntro"), tabDetail = $("#tabDetail");
  var viewIntro = $("#viewIntro"), viewDetail = $("#viewDetail");
  var btnView = $("#btnView");
  function setView(v) {
    var isIntro = v === "intro";
    viewIntro.style.display = isIntro ? "" : "none";
    viewDetail.style.display = isIntro ? "none" : "";
    tabIntro.classList.toggle("is-on", isIntro);
    tabDetail.classList.toggle("is-on", !isIntro);
    btnView.textContent = isIntro ? T("详情 ▴") : T("简介 ▾");
  }
  if (tabIntro && tabDetail) {
    tabIntro.addEventListener("click", function () { setView("intro"); });
    tabDetail.addEventListener("click", function () { setView("detail"); });
    if (btnView) btnView.addEventListener("click", function () {
      setView(viewDetail.style.display === "none" ? "detail" : "intro");
    });
  }

  /* ---------- 步骤条 ---------- */
  var stepsHost = $("#steps");
  var current = -1, playing = false, timer = null;
  if (stepsHost) {
    STEPS.forEach(function (s, i) {
      var b = document.createElement("button");
      b.className = "dock__step";
      b.textContent = s.id + " " + T(s.label);
      b.addEventListener("click", function () { stop(); go(i); });
      stepsHost.appendChild(b);
    });
  }
  function go(i) {
    current = i;
    $all(".dock__step").forEach(function (el, k) {
      el.classList.toggle("is-on", k === i);
      el.classList.toggle("is-done", k < i);
    });
    // 出生
    STEPS.forEach(function (s, k) {
      s.born.forEach(function (id) {
        var el = document.querySelector('[data-born="' + id + '"]');
        if (!el) return;
        if (k < i) { el.classList.remove("is-ghost"); el.classList.add("is-born"); }
      });
    });
    var step = STEPS[i];
    if (step) step.born.forEach(function (id) {
      var el = document.querySelector('[data-born="' + id + '"]');
      if (el) { el.classList.remove("is-ghost"); el.classList.add("is-born"); }
    });
    // 箭头点亮：T3-T7 经验流出，T8 回流
    var aGrad = $("#aGrad"), aPull = $("#aPull");
    if (aGrad) aGrad.classList.toggle("is-live", i >= 3 && i <= 7);
    if (aPull) aPull.classList.toggle("is-live", i === 8);
    // 流动光点
    $all(".flowdot").forEach(function (d) { d.classList.toggle("is-flowing", playing); });
  }
  function ghostAll() {
    $all(".born-target").forEach(function (el) { el.classList.add("is-ghost"); el.classList.remove("is-born"); });
  }
  function play() {
    playing = true;
    $("#btnPlay").textContent = T("❚❚ 暂停");
    ghostAll();
    go(0);
    timer = setInterval(function () {
      if (current >= STEPS.length - 1) { stop(); go(STEPS.length - 1); $all(".born-target").forEach(function (el) { el.classList.remove("is-ghost"); el.classList.add("is-born"); }); return; }
      go(current + 1);
    }, 1400);
  }
  function stop() {
    playing = false;
    clearInterval(timer);
    var b = $("#btnPlay"); if (b) b.textContent = T("▶ 播放");
    $all(".flowdot").forEach(function (d) { d.classList.remove("is-flowing"); });
    $all(".born-target").forEach(function (el) { el.classList.remove("is-ghost"); });
  }
  var btnPlay = $("#btnPlay");
  if (btnPlay) btnPlay.addEventListener("click", function () { playing ? stop() : play(); });

  /* ---------- 详情抽屉 ---------- */
  var drawer = $("#drawer"), drawerBody = $("#drawerBody");
  function showDetail(key) {
    var d = DETAILS[key];
    if (!d || !drawer) return;
    var html = "<h3>" + T(d.title) + "</h3><dl>";
    d.rows.forEach(function (r) { html += "<dt>" + T(r[0]) + "</dt><dd>" + T(r[1]) + "</dd>"; });
    html += "</dl>";
    drawerBody.innerHTML = html;
    drawer.classList.add("is-open");
    drawer.setAttribute("aria-hidden", "false");
  }
  $all("[data-detail]").forEach(function (b) {
    b.addEventListener("click", function () { showDetail(b.getAttribute("data-detail")); });
  });
  var dc = $("#drawerClose");
  if (dc) dc.addEventListener("click", function () { drawer.classList.remove("is-open"); drawer.setAttribute("aria-hidden", "true"); });
  window.showDetail = showDetail;

  /* ---------- 初始状态 ---------- */
  if (!reduced) {
    // 静态默认：全部可见；点播放才进入出生流程
    $all(".born-target").forEach(function (el) { el.classList.remove("is-ghost"); });
  }
})();
