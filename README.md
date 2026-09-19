# Deryee-site

deryee.pro — 个人 IP 品牌 + 知识博客站点。纯静态 HTML，无构建，Vercel 托管。

## 本地预览

```bash
python -m http.server 8080
# 浏览器打开 http://localhost:8080
```

（搜索页的 fetch 需要 http 环境，file:// 打开会失败。）

## 发布流程

1. 改内容 → `git push` → Vercel 自动部署。

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

## 目录

- `index.html` 首页 · `about/` 关于我 · `system/` 我的体系
- `articles/` 文章 · `knowledge/` 知识栏目（排版复刻 Project Cairn）
- `styles.css` 唯一共享样式 · `assets/` 共享脚本
- `tools/` 索引与 sitemap 生成脚本 · `templates/` 文章模板
