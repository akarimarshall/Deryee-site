#!/usr/bin/env python3
"""扫描全站 HTML，生成 sitemap.xml 与 robots.txt"""
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOMAIN = "https://deryee.pro"


def main():
    urls = []
    for html_path in sorted(ROOT.rglob("index.html")):
        rel = html_path.relative_to(ROOT)
        if "templates" in rel.parts:
            continue
        if str(rel) == "index.html":
            loc = DOMAIN + "/"
            pri = "1.0"
        else:
            loc = DOMAIN + "/" + str(rel.parent).replace("\\", "/") + "/"
            pri = "0.8"
        if rel.parts[0] in ("search.html",) or "search" in str(rel):
            continue
        urls.append((loc, pri))

    urls.append((DOMAIN + "/search.html", "0.3"))

    today = date.today().isoformat()
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, pri in urls:
        lines.append(f"  <url><loc>{loc}</loc><lastmod>{today}</lastmod><priority>{pri}</priority></url>")
    lines.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(lines), encoding="utf-8")

    robots = f"""User-agent: *
Allow: /
Disallow: /dashboard/

Sitemap: {DOMAIN}/sitemap.xml
"""
    (ROOT / "robots.txt").write_text(robots, encoding="utf-8")
    print(f"OK: sitemap.xml ({len(urls)} URLs) + robots.txt")


if __name__ == "__main__":
    main()
