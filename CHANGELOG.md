# 更新日志 Changelog

本项目的所有显著变更都会记录在本文件。
格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [未发布]

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
  - 全站页脚均已注入；当前链接与二维码为占位，待填 `assets/qr/*.png`
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
- 新增 `api/maintenance.js`（Vercel Edge Function，零构建）：读取环境变量 `MAINTENANCE_MODE`，为 `true` 时把**任意路径（含子地址、`/zh-tw/` 子地址）** 307 重定向到 `/maintenance/`；维护页本身与 `/assets/` 直接放行，避免死循环
- `vercel.json` 新增 `rewrites` catch-all（负向前瞻排除 `/maintenance/`、`/assets/`、`/api/`、favicon/robots/sitemap 及静态后缀）
- 维护开关改为**站内自助**：Vercel 后台改 `MAINTENANCE_MODE` 变量值即生效，无需改代码、无需对话、通常无需重部署
- `gen_zh_tw.py` `EXCLUDE_PATHS` 加 `maintenance/index.html`；`gen_sitemap.py` 加 `SKIP_SITEMAP` 与 robots `Disallow: /maintenance/`；`build_index.py` 跳过 `maintenance`
- `sitemap.xml` 由 24 → **23** 条 URL（维护页不收录）

### Changed（法务页署名）
- `ip/index.html` 两处「韩德灵」→「德益师兄」（用户已放开此前冻结）；重建搜索索引刷新 `assets/search-index.json` 摘要缓存
- 全站 `grep -r 韩德灵` 现已为 0 处

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
