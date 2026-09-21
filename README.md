# Deryee-site

deryee.pro — 个人 IP 品牌 + 知识博客站点。纯静态 HTML，无构建，Vercel 托管。

## 本地预览

```bash
python -m http.server 8080
# 浏览器打开 http://localhost:8080
```

（搜索页的 fetch 需要 http 环境，file:// 打开会失败。）

## 发布流程

**⚠️ 推送前必须先读 [`WORKFLOW.md`](./WORKFLOW.md)。**

核心原则：本地改 → 本地自测 → 写 `CHANGELOG.md` 的 `[未发布]` → 给项目所有者看变更说明 → **明确确认后**才 `git push`。

```bash
# 2. 确认后推送
git add -A
git commit -m "feat: 简述本次变更"
git push origin main
# Vercel 自动部署 → 线上抽查 → 打 tag
git tag v1.x.x && git push --tags
```

每次变更的记录写在 [`CHANGELOG.md`](./CHANGELOG.md)。

## 新增文章

```bash
python tools/new_article.py <slug> "<标题>" "<分类>" "<SEO描述>"
```

会自动生成 `articles/<slug>/index.html` 并重建搜索索引和 sitemap。

## 内容更新后

```bash
python tools/build_index.py   # 重建搜索索引
python tools/gen_sitemap.py   # 重建 sitemap.xml / robots.txt
```

## 资料下载（PDF）

完全支持：静态站点直接把文件发出去，不需要后端或数据库。

1. 把 PDF（建议单文件 ≤10MB）放进 `downloads/` 目录；
2. 在页面里加一行即可：

```html
<a class="btn btn--primary" href="./downloads/你的文件.pdf" download>下载 <span class="btn-arrow">↓</span></a>
```

- 根目录页面用 `./downloads/xxx.pdf`，子目录页面用 `../downloads/xxx.pdf`。
- `download` 属性会让浏览器直接下载而不是尝试预览。
- 若要「留邮箱后下载」的闭环，需要再加一个表单 + Serverless Function，目前站点是纯静态，暂不支持。

## 简繁切换

- 手动切换：导航右上角「繁 / 簡」按钮，无刷新即时转换 + 网址同步到 `/zh-tw/…`。
- 自动判断：首次访问按浏览器语言决定，之后记在 `localStorage` 的 `deryee-lang`。
- 静态镜像：`/zh-tw/` 下的 13 个页面由 `tools/gen_zh_tw.py` 预转生成，供搜索引擎收录（含 hreflang）。

**改了任何中文文案后必须跑：**

```bash
python tools/gen_zh_tw.py     # 重建词典子集 + 繁体镜像 + 繁体搜索索引
python tools/gen_sitemap.py   # 重建 sitemap（含 hreflang）
```

用词纠偏改 `tools/lang_overrides.txt`（`简体<TAB>繁体`）；不要直接手改 `zh-tw/` 里的页面。

## 社交图标导航

全站页脚自动注入一行平台图标（见 `assets/social.js`）。修改链接或图标：

1. **改链接**：编辑 `assets/social.js` 顶部的 `PLATFORMS` 数组；
2. **改图标**：替换 `assets/icons/<key>.svg`（24×24 viewBox、单色、`currentColor`），然后运行
   ```bash
   python tools/build_social_icons.py   # 重新打包成 assets/social-icons.js
   ```
3. **放二维码**：把 `wechat-work.png` / `wechat-mp.png` / `channels.png` 放进 `assets/qr/`（详见该目录 README）。

跳转逻辑：

| 平台类型 | 行为 |
|---|---|
| 抖音 / B站 / 小红书 / FlowUs | 直接 `href`，手机端由系统自动唤起 App，未装则落网页 |
| 微信工作号 / 公众号 / 视频号 | 无法外部深链 → 弹二维码，扫码添加 |
| 工作邮箱 | `mailto:`，唤起系统邮件 App |

想在同一页多处显示图标行，加一个 `id` 以 `social-row` 开头的空 `div` 即可。

## 目录

- `index.html` 首页 · `about/` 关于我 · `system/` 我的体系
- `articles/` 文章 · `knowledge/` 知识栏目（排版复刻 Project Cairn）
- `resources/` 资料下载 · `contact/` 联系方式 · `privacy/` 隐私政策 · `ip/` 知识产权声明
- `downloads/` PDF 资源 · `assets/icons/` 社交 SVG 源 · `assets/qr/` 二维码位
- `styles.css` 唯一共享样式 · `assets/` 共享脚本
- `tools/` 索引、sitemap、图标打包脚本 · `templates/` 文章模板
- `WORKFLOW.md` 项目工作规则（必读） · `CHANGELOG.md` 版本记录
