#!/usr/bin/env python3
"""扫描全站 HTML，生成 sitemap.xml 与 robots.txt

每个页面输出简体 + /zh-tw/ 繁体两条 URL，并带 xhtml:link hreflang 互指
（zh-Hans / zh-Hant / x-default），符合 Google 多语言站点规范。
"""
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOMAIN = "https://deryee.pro"
MIRROR = "/zh-tw"


# 法务页暂不参与简繁镜像，sitemap 里只出简体一条、不带 hreflang
NO_MIRROR = {"privacy", "ip"}
# 系统/维护页不进 sitemap（页面本身 noindex，且 robots 已 Disallow）
SKIP_SITEMAP = {"maintenance"}


def collect():
    """返回 [(site_path, priority, has_mirror)]，site_path 形如 "/" 或 "/about/" """
    out = []
    for html_path in sorted(ROOT.rglob("index.html")):
        rel = html_path.relative_to(ROOT)
        parts = rel.parts
        if "templates" in parts or "zh-tw" in parts:
            continue
        if parts[0] in SKIP_SITEMAP:
            continue
        if str(rel) == "index.html":
            out.append(("/", "1.0", True))
        else:
            seg = parts[0]
            out.append(("/" + str(rel.parent).replace("\\", "/") + "/", "0.8", seg not in NO_MIRROR))
    return out


def alternates(site_path):
    hans = DOMAIN + site_path
    hant = DOMAIN + MIRROR + site_path
    return hans, hant


def url_block(loc, pri, today, hans, hant):
    return (
        f"  <url>\n"
        f"    <loc>{loc}</loc>\n"
        f"    <lastmod>{today}</lastmod>\n"
        f"    <priority>{pri}</priority>\n"
        f'    <xhtml:link rel="alternate" hreflang="zh-Hans" href="{hans}"/>\n'
        f'    <xhtml:link rel="alternate" hreflang="zh-Hant" href="{hant}"/>\n'
        f'    <xhtml:link rel="alternate" hreflang="x-default" href="{hans}"/>\n'
        f"  </url>"
    )


def main():
    today = date.today().isoformat()
    blocks = []
    for site_path, pri, has_mirror in collect():
        hans, hant = alternates(site_path)
        if not has_mirror:
            blocks.append(
                f"  <url>\n    <loc>{hans}</loc>\n"
                f"    <lastmod>{today}</lastmod>\n    <priority>{pri}</priority>\n  </url>"
            )
            continue
        blocks.append(url_block(hans, pri, today, hans, hant))
        blocks.append(url_block(hant, "0.6" if pri != "1.0" else "0.8", today, hans, hant))

    # 搜索页：noindex，只列简体一条，不带 hreflang
    blocks.append(
        f"  <url>\n    <loc>{DOMAIN}/search.html</loc>\n"
        f"    <lastmod>{today}</lastmod>\n    <priority>0.3</priority>\n  </url>"
    )

    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"'
             ' xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    lines += blocks
    lines.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(lines) + "\n", encoding="utf-8")

    robots = f"""User-agent: *
Allow: /
Disallow: /dashboard/
Disallow: /maintenance/

Sitemap: {DOMAIN}/sitemap.xml
"""
    (ROOT / "robots.txt").write_text(robots, encoding="utf-8")
    print(f"OK: sitemap.xml ({len(blocks)} URLs, 含 hreflang) + robots.txt")


if __name__ == "__main__":
    main()
