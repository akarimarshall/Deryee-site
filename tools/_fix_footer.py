# -*- coding: utf-8 -*-
"""规范化全站 footer 栏目：补 资料下载 / 联系方式，清理占位社交列"""
import os, re, io

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

files = []
for dirpath, dirnames, filenames in os.walk(ROOT):
    if ".git" in dirpath or "templates" in dirpath:
        continue
    for fn in filenames:
        if fn.endswith(".html"):
            files.append(os.path.join(dirpath, fn))

changed = []
for f in sorted(files):
    src = io.open(f, encoding="utf-8").read()
    orig = src
    rel = os.path.relpath(f, ROOT)
    base = "./" if os.sep not in rel else "../"

    # 清理 index 首页的占位「社交入口」列 → 换成 联系方式 / 资料下载
    src = re.sub(
        r'<div class="footer__col">\s*<h4>此处填写：社交入口</h4>.*?</div>',
        '<div class="footer__col">\n'
        '        <h4>联系</h4>\n'
        '        <a href="' + base + 'contact/">联系方式</a>\n'
        '        <a href="' + base + 'resources/">资料下载</a>\n'
        '      </div>',
        src, flags=re.S)

    # 「内容」列补资料下载
    if ('<h4>内容</h4>' in src) and ('resources/">资料下载' not in src):
        src = re.sub(
            r'(<div class="footer__col">\s*<h4>内容</h4>\s*)',
            r'\1<a href="' + base + 'resources/">资料下载</a>\n        ',
            src, count=1)

    if src != orig:
        io.open(f, "w", encoding="utf-8", newline="").write(src)
        changed.append(rel)

print("changed: %d" % len(changed))
for c in changed:
    print("  " + c)
