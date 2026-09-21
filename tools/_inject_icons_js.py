# -*- coding: utf-8 -*-
"""在所有已引入 social.js 的页面前插入 social-icons.js"""
import os, re, io

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

files = []
for dirpath, dirnames, filenames in os.walk(ROOT):
    if ".git" in dirpath:
        continue
    for fn in filenames:
        if fn.endswith(".html"):
            files.append(os.path.join(dirpath, fn))

changed = []
for f in sorted(files):
    src = io.open(f, encoding="utf-8").read()
    orig = src
    if "assets/social.js" not in src or "assets/social-icons.js" in src:
        continue
    m = re.search(r'([ \t]*)<script src="([^"]*?)assets/social\.js"[^>]*></script>', src)
    if not m:
        continue
    indent, base = m.group(1), m.group(2)
    inject = '%s<script src="%sassets/social-icons.js"></script>\n' % (indent, base)
    src = src[:m.start()] + inject + src[m.start():]
    io.open(f, "w", encoding="utf-8", newline="").write(src)
    changed.append(os.path.relpath(f, ROOT))

print("changed: %d" % len(changed))
for c in changed:
    print("  " + c)
