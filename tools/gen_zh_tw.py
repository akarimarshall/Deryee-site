# -*- coding: utf-8 -*-
"""生成 /zh-tw/ 繁体镜像站（单入口）

  1. 构建词典（tools/build_lang_dict.py）—— 若 lang-table.json 不存在则自动调用
  2. 把 13 个简体页面转成繁体写入 zh-tw/**
  3. 给简体源页幂等注入 hreflang + lang.js
  4. 生成繁体搜索索引 zh-tw/assets/search-index.json

用法： python tools/gen_zh_tw.py
"""
import io
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from _s2t import S2T  # noqa: E402

SITE = "https://deryee.pro"
MIRROR_PREFIX = "/zh-tw"
TABLE_JSON = os.path.join(ROOT, "tools", "lang-table.json")

EXCLUDE_FILES = {"404.html", "icon-preview.html"}
# 法务页暂不参与镜像：站主后续单独出版本（改这里即可放开）
EXCLUDE_PATHS = {"privacy/index.html", "ip/index.html", "maintenance/index.html"}
EXCLUDE_DIRS = {".git", "templates", "zh-tw", "downloads", "tools", "assets"}
# 需要转换的 JSON-LD 字段白名单
CONV_KEYS = {"name", "alternateName", "headline", "description",
             "jobTitle", "knowsAbout", "text", "articleSection"}
CONV_ATTRS = ("title", "aria-label", "alt", "placeholder")

TOKEN_RE = re.compile(
    r"(?P<comment><!--.*?-->)"
    r"|(?P<ldjson><script\b[^>]*type=['\"]application/ld\+json['\"][^>]*>.*?</script>)"
    r"|(?P<script><script\b.*?</script>)"
    r"|(?P<style><style\b.*?</style>)"
    r"|(?P<raw><(?:pre|code|svg)\b.*?</(?:pre|code|svg)>)"
    r"|(?P<tag><[^>]+>)"
    r"|(?P<text>[^<]+)",
    re.S | re.I)

REL_RE = re.compile(r'(href="|src=")(\.\.?/)')


def deepen(m):
    """./x -> ../x ； ../x -> ../../x"""
    return m.group(1) + ("../" if m.group(2) == "./" else "../../")


def asset_prefix(site_path):
    """从镜像页访问站点根目录所需的相对前缀"""
    depth = site_path.count("/") - 1
    return "./" if depth <= 0 else "../" * depth


def to_site_path(rel):
    """"about/index.html" -> "/about/" ; "index.html" -> "/" ; "search.html" -> "/search.html" """
    rel = rel.replace("\\", "/")
    if rel == "index.html":
        return "/"
    if rel.endswith("/index.html"):
        return "/" + rel[:-len("/index.html")] + "/"
    return "/" + rel


def mirror_url(site_url):
    if not site_url.startswith(SITE):
        return site_url
    if MIRROR_PREFIX in site_url:
        return site_url
    rest = site_url[len(SITE):]
    if rest in ("", "/"):
        return SITE + MIRROR_PREFIX + "/"
    return SITE + MIRROR_PREFIX + rest


class Generator(object):
    def __init__(self):
        self.conv = S2T(json.load(io.open(TABLE_JSON, encoding="utf-8")))
        self.warn = []

    # ---------- 文本 ----------
    def t(self, s):
        return self.conv.convert(s)

    # ---------- 标签 ----------
    def conv_tag(self, tag):
        # 1) 相对路径再上溯一层
        tag = REL_RE.sub(deepen, tag)
        # 1b) og:url 指向镜像页
        if re.search(r'property="og:url"', tag, re.I):
            tag = re.sub(r'(content=")(https://deryee\.pro[^"]*)(")',
                         lambda m: m.group(1) + mirror_url(m.group(2)) + m.group(3), tag, count=1)
            return tag
        # 2) html lang
        if re.match(r"<html\b", tag, re.I):
            if 'lang="' in tag:
                tag = re.sub(r'lang="[^"]*"', 'lang="zh-Hant-TW"', tag, count=1)
            else:
                tag = tag.replace("<html", '<html lang="zh-Hant-TW"', 1)
        # 3) meta / og 的 content
        if re.match(r"<meta\b", tag, re.I):
            is_desc = (re.search(r'name="(description|keywords)"', tag, re.I)
                       or re.search(r'property="og:(title|description|site_name)"', tag, re.I)
                       or re.search(r'name="twitter:(title|description)"', tag, re.I))
            if is_desc:
                tag = self._sub_attr(tag, "content")
        # 4) 通用可转属性
        for a in CONV_ATTRS:
            tag = self._sub_attr(tag, a)
        return tag

    def _sub_attr(self, tag, attr):
        pat = re.compile(attr + r'="([^"]*)"', re.I)

        def rep(m):
            val = self.t(m.group(1)).replace('"', "&quot;")
            return '%s="%s"' % (attr, val)
        return pat.sub(rep, tag)

    # ---------- JSON-LD ----------
    def conv_ldjson(self, block):
        m = re.match(r"(<script\b[^>]*>)(.*?)(</script>)", block, re.S | re.I)
        if not m:
            return block
        head, body, tail = m.group(1), m.group(2), m.group(3)
        try:
            data = json.loads(body)
        except Exception:
            self.warn.append("JSON-LD 解析失败，原样保留")
            return block
        return head + json.dumps(self._conv_json(data), ensure_ascii=False, indent=2) + tail

    def _conv_json(self, obj):
        if isinstance(obj, dict):
            out = {}
            for k, v in obj.items():
                if k == "inLanguage" and isinstance(v, str):
                    out[k] = "zh-Hant"
                elif k == "url" and isinstance(v, str):
                    out[k] = mirror_url(v)
                elif k in CONV_KEYS:
                    out[k] = self._conv_val(v)
                else:
                    out[k] = self._conv_json(v)
            return out
        if isinstance(obj, list):
            return [self._conv_json(x) for x in obj]
        return obj

    def _conv_val(self, v):
        if isinstance(v, str):
            return self.t(v)
        if isinstance(v, list):
            return [self.t(x) if isinstance(x, str) else self._conv_json(x) for x in v]
        return self._conv_json(v)

    # ---------- 整页 ----------
    def convert_html(self, html):
        out = []
        pos = 0
        for m in TOKEN_RE.finditer(html):
            if m.start() > pos:
                out.append(html[pos:m.start()])
            pos = m.end()
            kind = m.lastgroup
            chunk = m.group()
            if kind == "text":
                out.append(self.t(chunk))
            elif kind == "tag":
                out.append(self.conv_tag(chunk))
            elif kind == "ldjson":
                out.append(self.conv_ldjson(chunk))
            elif kind == "script":
                # 外链脚本（空内容）也需要上溯一层路径，但内容不参与转换
                if re.match(r"<script\b[^>]*\bsrc=", chunk, re.I):
                    inner = re.sub(r"^<script\b[^>]*>", "", chunk, flags=re.I)
                    inner = inner[: -len("</script>")] if inner.endswith("</script>") else inner
                    if not inner.strip():
                        chunk = REL_RE.sub(deepen, chunk)
                out.append(chunk)
            else:
                out.append(chunk)
        if pos < len(html):
            out.append(html[pos:])
        return "".join(out)

    # ---------- head 注入 ----------
    def inject_mirror_head(self, html, site_url, mir_url):
        ap = asset_prefix(mir_url.replace(SITE, ""))
        hreflang = (
            '<link rel="alternate" hreflang="zh-Hans" href="%s">\n'
            '    <link rel="alternate" hreflang="zh-Hant" href="%s">\n'
            '    <link rel="alternate" hreflang="x-default" href="%s">'
        ) % (site_url, mir_url, site_url)
        if 'rel="canonical"' in html:
            html = re.sub(r'(<link rel="canonical" href=")[^"]*(">)',
                          lambda m: m.group(1) + mir_url + m.group(2), html, count=1)
        if 'hreflang="zh-Hant"' not in html:
            if 'rel="canonical"' in html:
                html = re.sub(r'(<link rel="canonical"[^>]*>)',
                              lambda m: m.group(1) + "\n    " + hreflang, html, count=1)
            else:
                html = html.replace("</head>", "    %s\n</head>" % hreflang, 1)

        if "assets/lang.js" not in html:
            html = self._after_theme(html, '<script src="%sassets/lang.js"></script>' % ap)
        if "assets/lang-table.js" not in html:
            html = self._after_theme(html,
                                     '<script src="%sassets/lang-table.js" defer></script>' % ap)
        return html

    @staticmethod
    def _after_theme(html, snippet):
        """插到 head 里最后一个 theme.js / lang.js 之后，保证 lang.js 在 lang-table.js 之前"""
        pat = re.compile(r'([ \t]*)(<script src="[^"]*assets/(?:theme\.js|lang\.js)"[^>]*></script>)')
        ms = list(pat.finditer(html))
        if ms:
            m = ms[-1]
            return html[:m.end()] + "\n" + m.group(1) + snippet + html[m.end():]
        return html.replace("</head>", "    %s\n</head>" % snippet, 1)

    @staticmethod
    def inject_source_head(html, site_url, mir_url):
        """简体源页：幂等注入 hreflang + lang.js（不改正文）"""
        if 'hreflang="zh-Hant"' in html:
            return html
        rel = site_url.replace(SITE, "")
        ap = asset_prefix(rel if rel else "/")
        hreflang = (
            '<link rel="alternate" hreflang="zh-Hans" href="%s">\n'
            '    <link rel="alternate" hreflang="zh-Hant" href="%s">\n'
            '    <link rel="alternate" hreflang="x-default" href="%s">'
        ) % (site_url, mir_url, site_url)
        if 'rel="canonical"' in html:
            html = re.sub(r'(<link rel="canonical"[^>]*>)',
                          lambda m: m.group(1) + "\n    " + hreflang, html, count=1)
        else:
            html = html.replace("</head>", "    %s\n</head>" % hreflang, 1)
        if "assets/lang.js" not in html:
            html = re.sub(r'([ \t]*)(<script src="[^"]*assets/theme\.js"[^>]*></script>)',
                          lambda m: m.group(1) + m.group(2) + "\n"
                          + m.group(1) + '<script src="%sassets/lang.js"></script>' % ap,
                          html, count=1)
        return html


def collect_pages():
    pages = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = sorted(d for d in dirnames if d not in EXCLUDE_DIRS)
        for fn in sorted(filenames):
            if not fn.endswith(".html") or fn in EXCLUDE_FILES:
                continue
            rel = os.path.relpath(os.path.join(dirpath, fn), ROOT).replace("\\", "/")
            if rel in EXCLUDE_PATHS:
                continue
            pages.append(rel)
    return pages


def main():
    print("deryee.pro · 生成繁体镜像")

    if not os.path.exists(TABLE_JSON):
        print("  词典不存在，先构建…")
        subprocess.check_call([sys.executable, os.path.join(ROOT, "tools", "build_lang_dict.py")])

    gen = Generator()
    pages = collect_pages()
    print("  待处理页面：%d" % len(pages))

    for rel in pages:
        src_path = os.path.join(ROOT, rel)
        site_url = SITE + to_site_path(rel)
        mir_url = mirror_url(site_url)
        html = io.open(src_path, encoding="utf-8").read()

        # 1) 繁体镜像
        out = gen.convert_html(html)
        out = gen.inject_mirror_head(out, site_url, mir_url)
        dst = os.path.join(ROOT, "zh-tw", rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        io.open(dst, "w", encoding="utf-8", newline="\n").write(out)

        # 2) 源页注入（幂等）
        new_src = Generator.inject_source_head(html, site_url, mir_url)
        if new_src != html:
            io.open(src_path, "w", encoding="utf-8", newline="\n").write(new_src)

        print("    %-38s -> %s" % (rel, mir_url.replace(SITE, "")))

    # 3) 繁体搜索索引
    idx = os.path.join(ROOT, "tools", "build_index.py")
    subprocess.check_call([sys.executable, idx, "--mirror"])
    print("  繁体搜索索引已生成")

    for w in gen.warn:
        print("  ! " + w)
    return 0


if __name__ == "__main__":
    sys.exit(main())
