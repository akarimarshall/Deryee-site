# 更新日志 Changelog

本项目的所有显著变更都会记录在本文件。
格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [未发布]

### Changed（shosho 风格全站改版 + 交互修复）
- **全站边距对齐 shosho.tw（响应式）**：`--gutter` 改为 `clamp(20px,6vw,88px)`、`--maxw` 1040px、`--maxw-wide` 1280px，手机端自动收到 20px
- **站内搜索改为同页浮层**：新增 `.search-overlay`（`z-index:900`，导航栏 `z-index:1000` 保持在上方）；`nav.js` 捕获所有 `a[href$="search.html"]` 触发浮层，复用 `search-index.json` 打分/渲染；`search.html` 保留为无 JS / SEO 兜底
- **删除「关于我」页**：`about/index.html` 与 `zh-tw/about/index.html` 已删；导航/页脚/hero 的「关于我」经 `nav.js` 全局拦截器改为「回首页顶端」（首页内平滑滚动、子页跳回首页）；`system` 页「联系我」改指向 `contact`；`sitemap.xml`、`search-index.json`、各页 JSON-LD `url` 同步清理
- **页脚图标行与底部间距拉开**：`.footer` padding-bottom 72px→112px，`.footer .social-row` 补 margin-bottom
- **二维码修复**：`social.js` 中 qr 路径由根绝对 `/assets/qr/...` 改为相对 `assets/qr/...`，各页深均可加载（PNG 占位图已就绪）
- **邮件链接修复**：`resolve()` 增加协议头判断（`mailto:` 原样返回），页脚邮件图标正确唤起邮件 App
- **FlowUs 图标改为文字**：社交栏 FlowUs 入口渲染英文「FlowUs」文字（原 SVG 仅用 viewBox ~21% 高度显小）
- **首页 CTA**：「发邮件联系我」→「访问宝库→」，链接至 Flowus（deryee.flowus.cn）（简繁同步）
- 小红书链接保持 `xhslink.cn`（500 为第三方短链服务问题，非本站代码）

### Changed（首页与全站体验批量改版）
- **修复「大标题版块位置错误」根因**：`styles.css` 维护页规则块末尾有一个孤儿 `}`，导致 CSS 解析器吞掉整条 `.hero` 规则（padding-top 变 0，eyebrow 被导航栏遮住）。已修复结构并把 `.nav__mobile .nav__link` 归位到移动端媒体查询内
- **我的故事**：改为左文右图双栏（`.story`），右侧新增 9:16 竖版照片位（`<img>` 直接放入即自动裁切）；按钮「了解我的体系」→「**了解我的宝库**」（全站统一，含 3 篇文章与模板）；印章占位填入关键词「**德益**」
- **我的文章与知识点**：整版改为参考图风格——分类 chips（全部分类 / 短视频教学 / 商业思维 / 超级专业体 / 好书分享）+ 3×3 封面卡片（渐变封面、类型标签、标题、首句摘要），点击分类即时筛选；3 篇真实文章归入「超级专业体」，6 张筹备中占位卡
- **CTA**：标题改为「了解我的体系请访问 德益师兄的宝库」，副文案「商业合作及咨询请发送邮件至：deryee.deyi@gmail.com」（mailto 链接）
- **能力档案**：`wrap-wide` → `wrap`，左右边距与其他栏目对齐
- **页脚社交图标行居中**（`.footer .social-row { justify-content:center }`）

### Fixed（简繁切换）
- **修复镜像子页切不回简体**：`/zh-tw/*` 为服务器预转换页面，无浏览器内快照，原 `deryeeSetLang("zh-Hans")` 只做快照还原（空操作）→ 点击「簡」后页面仍是繁体。现在改为**真实跳转**到对应简体页
- 修复非镜像页切回简体时网址未还原的问题（新增 `ORIGIN` 记录原始地址，切换时 `replaceState` 回正确路径）
- 新增 `NO_MIRROR` 机制（`window.DERYEE_NO_MIRROR = true`）：无繁体镜像的页面支持就地切换且不改写网址、不做首访自动跳转
- **维护页接入简繁切换**：引入 `lang.js` + NO_MIRROR 标记，导航右上角出现「繁/簡」按钮，双向切换实测通过

### Changed（品牌与文案）
- **全站移除「跨境股权架构师」头衔信息**：index/contact/resources 各页 title、og:title、meta description、JSON-LD `jobTitle` 全部清除；`WORKFLOW.md` 署名规则新增「不使用『股权架构师』等职业头衔表述」；繁体镜像与搜索索引同步重建
- **FlowUs 图标重绘为官方造型**：按官方 favicon 矢量（斜杠 / 实心方块 / 笑脸圆形 / 三角形）等比缩放，单色 currentColor + 蒙版镂空笑脸，深浅色主题均可见
- **维护页**：移除错误的「DEYEE.PRO」eyebrow；文案改为「我正在加班加点为你提供更好的内容 / 稍等片刻，很快就会回来。/ 维护期间，你还可以通过下面的方式找到我：」；图标行居中

### Added
- **全站简繁切换（简体 ↔ 台湾繁体）**
  - 导航右上角新增「繁 / 簡」按钮（主题按钮旁），**无刷新即时转换** + `history.replaceState` 同步网址
  - 新增 `/zh-tw/` 繁体镜像站 11 个静态页（Python 预转，供搜索引擎收录）+ `hreflang` 三向标注 + sitemap 双份 URL 互指（对外法务页 `privacy/` `ip/` 暂不镜像）
  - 首次访问跟随浏览器语言自动判断繁体偏好；`localStorage` 记忆选择
  - 词典本地内置（`assets/lang-table.js`，约 79KB / gzip 约 25KB），离线可用，未引入任何第三方 CDN
  - 新增文件：`assets/lang.js`、`assets/lang-table.js`、`tools/_s2t.py`、`tools/build_lang_dict.py`、`tools/gen_zh_tw.py`、`tools/lang_protect.txt`、`tools/lang_overrides.txt`、`tools/lang-table.json`、`tools/lang/dict/*.txt`（OpenCC 官方词典，Apache-2.0）
  - 站内搜索支持简繁通吃（查询词与索引文本统一归一化后再比对）；繁体镜像使用独立的 `zh-tw/assets/search-index.json`
- 新增 `/resources/` 资料下载页：独立聚合页，含下载卡、使用说明、转化 CTA；导航栏与页脚加入口
- 新增 `/contact/` 联系方式页：全平台入口汇聚页（图标行 + 三张说明卡 + 转化 CTA）
- 新增社交图标导航组件：`assets/social.js` + `assets/social-icons.js` + `assets/icons/*.svg`（8 枚 24×24 单色图标）
  - 覆盖：工作邮箱、微信工作号、微信公众号、视频号、抖音、小红书、B站、FlowUs
  - 支持一页多容器（任意 id 以 `social-row` 开头的元素）
  - 全站页脚均已注入；真实平台链接已接入（B站 `space.bilibili.com/637598`、小红书 `xhslink.cn/o/3MUeoSyXO9E`、抖音用户页、FlowUs `deryee.flowus.cn`、工作邮箱 `deryee.deyi@gmail.com` mailto）；微信工作号 / 微信公众号 / 视频号以二维码弹窗呈现，二维码图已落位 `assets/qr/{wechat-work,wechat-mp,channels}.png`（当前为占位图，替换为真实二维码即可，文件名保持不变）
- 新增微信系二维码弹窗 `.qr-modal`（毛玻璃遮罩 + 卡片，支持点背景 / ✕ / Esc 关闭）
- 新增 `assets/qr/` 二维码目录与说明 `README.md`
- 新增工具脚本 `tools/build_social_icons.py`（把 SVG 打包成内联 JS 表，规避 fetch 限制）
- 新增一键重建脚本 `tools/build_all.py`：一次跑完「词典 → 繁体镜像 → 搜索索引 → sitemap」，中文文案或页面增删后只需跑这一条命令

### Changed（署名与法务页）
- 全站署名统一为「德益师兄」：移除 `index.html`、`contact/index.html`、文章列表与 3 篇详情页、`knowledge/`、`resources/`、文章模板中的真实姓名；`tools/lang_protect.txt` 移除 `MarshallHan`
- `WORKFLOW.md` 署名规则更新：拥有者/管理者一律表述为「德益师兄」，不再出现真实姓名或个人账号
- `privacy/` 与 `ip/` 对外法务页退出简繁镜像：已移除其注入的 `lang.js` + hreflang，`gen_zh_tw.py` 加 `EXCLUDE_PATHS`、`gen_sitemap.py` 加 `NO_MIRROR`（sitemap 25 → 23 条 URL）
- 繁体镜像页数 13 → 11；`sitemap.xml` 重新生成

### Added（维护模式）
- 新增独立维护页 `maintenance/index.html`：`noindex`、保留左上角「德益师兄 Deryee」品牌（复用 `nav.js`）、居中显示「网站正在升级中，很快就会回来」、下方一排 8 个平台图标（复用 `social.js`，功能与全站一致：App 唤起 / 微信系弹二维码 / mailto）
- 新增 `api/maintenance.mjs`（Vercel Edge Function，`.mjs` 即 ESM，零构建）：读取环境变量 `MAINTENANCE_MODE`，为 `true` 时把**任意路径（含子地址、`/zh-tw/` 子地址）** 307 重定向到 `/maintenance/`；维护页本身与 `/assets/`、`/api/` 直接放行，避免死循环
- `vercel.json` 用 legacy `routes`（运行于 **beforeFiles** 阶段，可覆盖静态文件）做 catch-all：PCRE 负向前瞻排除 `/maintenance/`、`/assets/`、`/api/`、favicon/robots/sitemap 及静态后缀，命中则 `dest` 到 Edge Function
  - **关键**：普通 `rewrites` 跑在文件系统检查之后、会被真实存在的 HTML 文件绕过（导致维护模式挡不住 `/about/` 等真实页面），所以必须用 `routes`（beforeFiles）
- 维护开关改为**站内自助**：Vercel 后台改 `MAINTENANCE_MODE` 变量值即生效，无需改代码、无需对话、通常无需重部署
- `gen_zh_tw.py` `EXCLUDE_PATHS` 加 `maintenance/index.html`；`gen_sitemap.py` 加 `SKIP_SITEMAP` 与 robots `Disallow: /maintenance/`；`build_index.py` 跳过 `maintenance`
- `sitemap.xml` 由 24 → **23** 条 URL（维护页不收录）

### Changed（法务页署名）
- `ip/index.html` 两处「韩德灵」→「德益师兄」（用户已放开此前冻结）；重建搜索索引刷新 `assets/search-index.json` 摘要缓存
- 全站 `grep -r 韩德灵` 现已为 0 处

### Fixed（部署失败根因）
- 修复 Vercel 部署报 "Deployment failed / Invalid route source pattern"：原 `vercel.json` 在 `rewrites` 里用了 `routes` 风格的裸负向前瞻 `/(?!...)/`（还混了 `:path` 命名参数修饰符），Vercel 的 path-to-regexp 拒绝该写法 → 部署中断
- 改走 legacy `routes` + PCRE 裸负向前瞻（Vercel 官方维护示例同款写法），并把 Edge Function 由 `.js` 改 `.mjs`（避免纯静态项目里 ESM 语法被当 CommonJS 解析而导入失败）
- 用 path-to-regexp v6（与 Vercel 同代引擎）与 Node 原生 RegExp（锚定全路径）双重验证 `routes.src` 合法且 14 条关键路径匹配正确

### Fixed（508 维护关闭循环）
- 修复部署成功但全站报 **`508 INFINITE_LOOP_DETECTED`**：原 `api/maintenance.mjs` 在维护**关闭**分支用 `fetch(request)` 透传原始 URL。Vercel 会对 Edge Function 的子请求再次套用 `vercel.json` 的 `routes`，页面路径永远命中本函数 → 函数递归调用自己无限循环 → 508
- 根因：Vercel 的「自动递归保护」只覆盖 Node.js 运行时的 `http`/`fetch` Serverless 函数，不拦截这种由 `routes` 触发的路由循环；且不存在任何「跳过路由」的官方响应头
- 解法：维护关闭分支不再 `fetch` 原始 URL，而是把目录式路径**映射成真实文件**（`/about/` → `/about/index.html`）再去 `fetch`。`vercel.json` 的 `routes.src` 已把 `.html` 排除在匹配之外，该子请求直接命中静态文件，**物理上不可能再次进入本函数**，循环被打断
  - 同时把 `cleanUrls` 由 `true` 改为 `false`：否则 `/about/index.html` 会被 308 重定向回 `/about/`，重新进入函数
  - `routes.src` 排除列表新增 `html?`，确保任何 `.html`/`.htm` 子请求都不会路由到函数
- 验证：15 条真实页面路径（含 `/`、`/about/`、`/articles/*`、`/zh-tw/*` 等）全部映射为真实存在的 `index.html` 且均被 `routes` 排除（无循环可能）；`node --check` 确认 ESM 语法 OK

### Changed
- 导航栏新增「资料下载」入口（共 5 项）
- 全站页脚规范化：补「资料下载 / 联系方式」链接；首页占位「社交入口」列改为「联系」列
- `WORKFLOW.md` 升级至 v1.1：新增铁律 0（需求澄清闸门）、红线清单、推送前自测清单、定期维护节奏
- `social.js` 改为内联图标表 + 多容器模式，移除 fetch 逻辑
- 重画「抖音」图标：弃用手绘音符，改用对标原版的官方轮廓路径（single-color）
- 重画「FlowUs」图标：按品牌实际 logo 重绘为「圆角方框 + 笑脸（双点眼 + 弧线嘴）」，弃用旧 F 字形

### Fixed
- 修复子页面导航链接相对路径错误（nav.js 改为按路径深度自动推算 base，此前 /about/ 等页面点导航会 404）

### Removed
- 移除 `styles.css` 中重复的 `.resource` 样式块（旧 grid 版与新 flex 版冲突，保留与 index.html 一致的 grid 版）
- 移除图标目录与 tools 下的临时下载日志、raw 中间文件

### Changed
- `nav.js` / `social.js` / `dock.js` / `search.js` 的中文文案统一走 `T()` 包装，运行时注入的内容（导航、社交图标、知识页播放器、搜索结果）随语言自动切换
- `social.js` 二维码图片改用站点绝对路径，避免切换后网址变化导致取图失败
- `build_index.py` 新增 `--mirror` 模式并排除 `zh-tw/`；`gen_sitemap.py` 输出 23 条 URL 并带 `xhtml:link` hreflang（法务页不参与互指）

### Changed（上一批）
- 导航栏品牌名由「Deryee.pro」改为「德益师兄Deryee」
- 首页新增「资料下载」板块与 `.resource` 下载卡组件；`downloads/` 目录含示例 PDF
- 新增 `/privacy/` 隐私政策页、`/ip/` 知识产权声明页
- 新增 `WORKFLOW.md` 项目工作规则、本更新日志与 `.gitignore`

## [1.0.0] - 2026-09-18

### Added
- 站点首发：首页 / 关于我 / 我的体系 / 文章（含 3 篇占位详情页）/ 知识栏目（Project Cairn 排版复刻）/ 站内搜索 / 404
- 苹果风设计系统 `styles.css`（毛玻璃导航、深浅色、滚动淡入、下载卡、档案面板、dock 播放器）
- 注入式导航 `assets/nav.js`、主题 `theme.js`、滚动动画 `reveal.js`、知识页播放器 `dock.js`
- SEO/GEO 基建：sitemap.xml、robots.txt、search-index.json、JSON-LD（Person/WebSite/FAQPage/CollectionPage/Article）
- 工具脚本：tools/build_index.py、tools/gen_sitemap.py、tools/new_article.py
- 部署：Vercel（vercel.json，纯静态无构建），仓库 akarimarshall/Deryee-site
