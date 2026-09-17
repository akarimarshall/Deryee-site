#!/usr/bin/env python3
"""扫描全站 HTML，生成 assets/search-index.json"""
import json
import re
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "search-index.json"


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
    parts = rel.parts
    if len(parts) == 1:
        return "核心页"
    return parts[0]


def main():
    items = []
    for html_path in sorted(ROOT.rglob("index.html")):
        rel = html_path.relative_to(ROOT)
        if "templates" in rel.parts:
            continue
        html = html_path.read_text(encoding="utf-8")
        ex = Extractor()
        try:
            ex.feed(html)
        except Exception:
            pass
        desc = meta_desc(html)
        title = ex.title or ex.h1 or str(rel)
        url = "https://deryee.pro/" + (str(rel.parent).replace("\\", "/") + "/" if str(rel.parent) != "." else "")
        text = " ".join(ex.h2s + ex.paras)[:600]
        items.append({
            "title": title,
            "desc": desc,
            "text": text,
            "url": url,
            "category": page_category(rel),
        })
    # search.html 本身
    items.append({
        "title": "站内搜索",
        "desc": "全站关键词搜索",
        "text": "",
        "url": "https://deryee.pro/search.html",
        "category": "工具",
    })
    OUT.write_text(json.dumps(items, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"OK: {len(items)} 条索引 -> {OUT}")


if __name__ == "__main__":
    main()
