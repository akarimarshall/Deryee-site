# -*- coding: utf-8 -*-
"""把所有页面的 footer 注入社交图标行 + 引入 social.js"""
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

    # 1) 注入脚本
    if "assets/social.js" not in src:
        m = re.search(r'([ \t]*)<script src="([^"]*?)assets/nav\.js"([^"]*)" defer></script>\n', src)
        if m:
            indent, base = m.group(1), m.group(2)
            inject = '%s<script src="%sassets/social.js" defer></script>\n' % (indent, base)
            src = src[:m.end()] + inject + src[m.end():]
        elif re.search(r'assets/reveal\.js', src) or True:
            # 没有 nav.js 的页面（如 404）插到 body 结尾前
            src = src.replace("</body>", '  <script src="./assets/social.js" defer></script>\n</body>')

    # 2) 注入容器：插到 footer__inner 之前
    if 'id="social-row"' not in src:
        m = re.search(r'([ \t]*)<div class="footer__inner">', src)
        if m:
            indent = m.group(1)
            inject = '%s<div class="social-row" id="social-row"></div>\n' % indent
            src = src[:m.start()] + inject + src[m.start():]

    if src != orig:
        io.open(f, "w", encoding="utf-8", newline="").write(src)
        changed.append(os.path.relpath(f, ROOT))

print("changed: %d" % len(changed))
for c in changed:
    print("  " + c)
