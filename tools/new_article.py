#!/usr/bin/env python3
"""从 templates/article-template.html 生成新文章详情页并重建索引。
用法：python tools/new_article.py <slug> <标题> <分类> <SEO描述>
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TPL = ROOT / "templates" / "article-template.html"


def main():
    if len(sys.argv) < 5:
        print("用法: python tools/new_article.py <slug> <标题> <分类> <SEO描述>")
        sys.exit(1)
    slug, title, cat, desc = sys.argv[1:5]
    html = TPL.read_text(encoding="utf-8")
    html = (html.replace("{{SLUG}}", slug)
                .replace("{{TITLE}}", title)
                .replace("{{CAT}}", cat)
                .replace("{{DESC}}", desc))
    out_dir = ROOT / "articles" / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "index.html").write_text(html, encoding="utf-8")
    print(f"OK: articles/{slug}/index.html")
    subprocess.run([sys.executable, str(ROOT / "tools" / "build_index.py")], check=True)
    subprocess.run([sys.executable, str(ROOT / "tools" / "gen_sitemap.py")], check=True)


if __name__ == "__main__":
    main()
