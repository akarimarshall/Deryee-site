#!/usr/bin/env python3
"""扫描全站 HTML，生成 assets/search-index.json

用法：
    python tools/build_index.py             # 简体索引（排除 zh-tw/）
    python tools/build_index.py --mirror    # 繁体索引 -> zh-tw/assets/search-index.json
"""
import io
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "search-index.json"
MIRROR = "--mirror" in sys.argv
if MIRROR:
    OUT = ROOT / "zh-tw" / "assets" / "search-index.json"

# 繁体索引需要转换标题/摘要/正文
_CONV = None


def conv():
    global _CONV
    if _CONV is None:
        sys.path.insert(0, str(ROOT / "tools"))
        from _s2t import S2T
        _CONV = S2T(json.load(io.open(str(ROOT / "tools" / "lang-table.json"), encoding="utf-8")))
    return _CONV


class Extractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ""
        self.desc = ""
        self.h1 = ""
        self.h2s = []
        self.paras = []
        self._stack = []
        self._cur = None
        self._buf = []

    def handle_starttag(self, tag, attrs):
        self._stack.append(tag)
        if tag in ("title", "h1", "h2", "p") and tag not in [s for s in self._stack[:-1]]:
            self._cur = tag
            self._buf = []

    def handle_endtag(self, tag):
        if self._cur == tag and self._buf:
            text = re.sub(r"\s+", "", "".join(self._buf))
            if tag == "title" and not self.title:
                self.title = "".join(self._buf).strip()
            elif tag == "h1" and not self.h1:
                self.h1 = text
            elif tag == "h2":
                self.h2s.append(text)
            elif tag == "p" and len(self.paras) < 6:
                self.paras.append("".join(self._buf).strip())
            self._cur = None
        if self._stack and self._stack[-1] == tag:
            self._stack.pop()

    def handle_data(self, data):
        if self._cur:
            self._buf.append(data)


def meta_desc(html: str) -> str:
    m = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', html)
    return m.group(1) if m else ""


def page_category(rel: Path) -> str:
    parts = [p for p in rel.parts if p != "zh-tw"]
    if len(parts) == 1:
        return "核心页"
    return parts[0]


def main():
    items = []
    scan_root = ROOT / "zh-tw" if MIRROR else ROOT
    for html_path in sorted(scan_root.rglob("index.html")):
        rel = html_path.relative_to(ROOT)
        parts = rel.parts
        if "templates" in parts:
            continue
        if "maintenance" in parts:
            continue
        if MIRROR and parts[0] != "zh-tw":
            continue
        if not MIRROR and "zh-tw" in parts:
            continue
        html = html_path.read_text(encoding="utf-8")
        ex = Extractor()
        try:
            ex.feed(html)
        except Exception:
            pass
        desc = meta_desc(html)
        title = ex.title or ex.h1 or str(rel)
        parent = rel.parent
        if MIRROR:
            parent = Path(*[p for p in parent.parts if p != "zh-tw"]) if "zh-tw" in parent.parts else parent
        url = "https://deryee.pro/" + ("/zh-tw" if MIRROR else "") + (
            str(parent).replace("\\", "/") + "/" if str(parent) != "." else "/")
        text = " ".join(ex.h2s + ex.paras)[:600]
        cat = page_category(rel)
        if MIRROR:
            c = conv()
            title, desc, text, cat = c.convert(title), c.convert(desc), c.convert(text), c.convert(cat)
        items.append({
            "title": title,
            "desc": desc,
            "text": text,
            "url": url,
            "category": cat,
        })
    # search.html 本身
    title, desc, cat = "站内搜索", "全站关键词搜索", "工具"
    if MIRROR:
        c = conv()
        title, desc, cat = c.convert(title), c.convert(desc), c.convert(cat)
    items.append({
        "title": title,
        "desc": desc,
        "text": "",
        "url": "https://deryee.pro/" + ("/zh-tw" if MIRROR else "") + "/search.html",
        "category": cat,
    })
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(items, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"OK: {len(items)} 条索引 -> {OUT}")


if __name__ == "__main__":
    main()
