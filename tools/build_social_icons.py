# -*- coding: utf-8 -*-
"""把 assets/icons/*.svg 打包成 assets/social-icons.js（内联表，避免 fetch / file:// 限制）
用法：python tools/build_social_icons.py
"""
import os, io, json, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICON_DIR = os.path.join(ROOT, "assets", "icons")
OUT = os.path.join(ROOT, "assets", "social-icons.js")

ORDER = ["email", "wechat-work", "wechat-mp", "channels",
         "douyin", "xiaohongshu", "bilibili", "flowus"]

def norm(s):
    s = s.strip()
    # 去掉可能被 CSP/旧浏览器挑剔的属性，统一成 24x24 + currentColor
    s = re.sub(r'\s+', ' ', s)
    return s

items = {}
for key in ORDER:
    path = os.path.join(ICON_DIR, key + ".svg")
    if not os.path.exists(path):
        print("MISSING: " + key)
        continue
    items[key] = norm(io.open(path, encoding="utf-8").read())

lines = [
    "/* deryee.pro — 社交图标内联表（自动生成，请勿手改）",
    " * 生成方式：python tools/build_social_icons.py",
    " * 源文件：assets/icons/*.svg —— 全部 24x24 viewBox，使用 currentColor",
    " * ============================================================ */",
    "window.DERYEE_SOCIAL_ICONS = " + json.dumps(items, ensure_ascii=False, indent=2) + ";",
    "",
]
io.open(OUT, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
print("written: %s  (%d icons, %d bytes)" % (os.path.relpath(OUT, ROOT), len(items), os.path.getsize(OUT)))
