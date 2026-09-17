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

## 目录

- `index.html` 首页 · `about/` 关于我 · `system/` 我的体系
- `articles/` 文章 · `knowledge/` 知识栏目（排版复刻 Project Cairn）
- `styles.css` 唯一共享样式 · `assets/` 共享脚本
- `tools/` 索引与 sitemap 生成脚本 · `templates/` 文章模板
