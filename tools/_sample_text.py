# -*- coding: utf-8 -*-
"""抽取全站真实中文片段作为一致性测试样本"""
import io, os, re, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = []
for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in {".git", "tools", "assets", "zh-tw", "downloads"}]
    for fn in sorted(filenames):
        if not fn.endswith(".html"):
            continue
        html = io.open(os.path.join(dirpath, fn), encoding="utf-8").read()
        # 取出所有标签之间的文本片段
        for seg in re.findall(r">([^<>]+)<", html):
            s = seg.strip()
            if not s or not re.search(r"[\u4e00-\u9fff]", s):
                continue
            out.append(re.sub(r"\s+", " ", s))
# JS 中的中文串
for fn in ("nav.js", "social.js", "dock.js", "search.js"):
    p = os.path.join(ROOT, "assets", fn)
    if not os.path.exists(p):
        continue
    src = io.open(p, encoding="utf-8").read()
    for m in re.findall(r'"([^"\n]*[\u4e00-\u9fff][^"\n]*)"', src):
        out.append(m)
seen = set()
uniq = []
for s in out:
    if s not in seen:
        seen.add(s)
        uniq.append(s)
io.open(sys.argv[1], "w", encoding="utf-8", newline="\n").write("\n".join(uniq))
print("samples: %d" % len(uniq))
