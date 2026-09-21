# -*- coding: utf-8 -*-
"""构建简→繁映射表（唯一数据源），同时产出 Python 端与浏览器端两个消费文件

    tools/lang/dict/*.txt  (OpenCC 官方词典，入库)
        + tools/lang_protect.txt / lang_overrides.txt
                    │
                    ▼
    tools/lang-table.json      ← canonical（Python 生成器读）
    assets/lang-table.js       ← 内嵌同一份 JSON（浏览器读），构建后断言逐字节相同

用法： python tools/build_lang_dict.py
"""
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DICT_DIR = os.path.join(ROOT, "tools", "lang", "dict")
TABLE_JSON = os.path.join(ROOT, "tools", "lang-table.json")
TABLE_JS = os.path.join(ROOT, "assets", "lang-table.js")

SITE = "https://deryee.pro"
SKIP_DIRS = {".git", "tools", "assets", "downloads", "zh-tw", "node_modules"}
CORPUS_EXT = {".html", ".js", ".json", ".txt", ".md"}
CORPUS_SKIP_NAMES = {"lang-table.js", "search-index.json"}


def read_dict(name):
    """解析 OpenCC 词典 txt：key\tv1 v2 …，取第一个值"""
    path = os.path.join(DICT_DIR, name)
    out = {}
    if not os.path.exists(path):
        print("  ! 缺少词典文件：%s" % name)
        return out
    with io.open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) < 2:
                continue
            key = parts[0].strip()
            vals = parts[1].split()
            if key and vals:
                out[key] = vals[0]
    return out


def build_corpus():
    """扫描全站语料，用于裁剪 STPhrases"""
    chunks = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if fn in CORPUS_SKIP_NAMES:
                continue
            if os.path.splitext(fn)[1].lower() not in CORPUS_EXT:
                continue
            try:
                chunks.append(io.open(os.path.join(dirpath, fn), encoding="utf-8").read())
            except Exception:
                pass
    # assets 下只取含中文的 JS（词典产物本身已排除）
    for fn in ("nav.js", "social.js", "dock.js", "search.js"):
        p = os.path.join(ROOT, "assets", fn)
        if os.path.exists(p):
            chunks.append(io.open(p, encoding="utf-8").read())
    p = os.path.join(ROOT, "assets", "search-index.json")
    if os.path.exists(p):
        chunks.append(io.open(p, encoding="utf-8").read())
    return u"\n".join(chunks)


def prune(mapping, corpus):
    """只保留键在语料中实际出现过的条目（遍历语料而非词典，速度快）"""
    if not mapping:
        return {}
    maxlen = max(len(k) for k in mapping)
    used = set()
    n = len(corpus)
    i = 0
    while i < n:
        upper = maxlen if maxlen < (n - i) else (n - i)
        for L in range(upper, 1, -1):
            k = mapping.get(corpus[i:i + L])
            if k is not None:
                used.add(corpus[i:i + L])
                break
        i += 1
    return {k: mapping[k] for k in used}


def read_pairs(name):
    path = os.path.join(ROOT, "tools", name)
    out = {}
    if not os.path.exists(path):
        return out
    with io.open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            if "\t" in line:
                k, v = line.split("\t", 1)
                if k.strip() and v.strip():
                    out[k.strip()] = v.strip()
    return out


def read_list(name):
    path = os.path.join(ROOT, "tools", name)
    out = []
    if not os.path.exists(path):
        return out
    with io.open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                out.append(line)
    return out


def maxlen_of(mapping):
    return max((len(k) for k in mapping), default=0)


def main():
    print("deryee.pro · 构建简繁映射表")

    chars_all = read_dict("STCharacters.txt")
    st_all = read_dict("STPhrases.txt")
    tw_all = read_dict("TWPhrases.txt")
    twv_all = read_dict("TWVariants.txt")
    twvp_all = read_dict("TWVariantsPhrases.txt")
    print("  词典载入：单字 %d · 简繁词组 %d · 台湾词组 %d · 异体 %d+%d"
          % (len(chars_all), len(st_all), len(tw_all), len(twv_all), len(twvp_all)))

    corpus = build_corpus()
    print("  语料长度：%d 字符" % len(corpus))

    st_used = prune(st_all, corpus)
    print("  词组裁剪：%d → %d（按语料实际出现）" % (len(st_all), len(st_used)))

    tw = dict(tw_all)
    tw.update(twvp_all)
    twv = dict(twv_all)
    twv.update(twvp_all)

    overrides = read_pairs("lang_overrides.txt")
    protect = read_list("lang_protect.txt")

    table = {
        "version": 1,
        "protect": protect,
        "overrides": overrides,
        "maxOverrideLen": maxlen_of(overrides),
        "s2tPhrases": st_used,
        "maxS2tLen": maxlen_of(st_used),
        "chars": chars_all,
        "twPhrases": tw,
        "maxTwLen": maxlen_of(tw),
        "twVariants": twv,
    }

    payload = json.dumps(table, ensure_ascii=False, separators=(",", ":"))

    with io.open(TABLE_JSON, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(table, ensure_ascii=False, indent=1))

    js = (u"/* deryee.pro — 简繁转换映射表（自动生成，请勿手改）\n"
          u" * 生成方式：python tools/build_lang_dict.py\n"
          u" * 数据源：tools/lang-table.json（与 Python 端共用同一份，构建时断言一致）\n"
          u" * 词典来源：OpenCC（Apache-2.0）\n"
          u" * ============================================================ */\n"
          u"window.DERYEE_LANG_TABLE = " + payload + u";\n")
    with io.open(TABLE_JS, "w", encoding="utf-8", newline="\n") as f:
        f.write(js)

    # 断言：JS 内嵌片段与 JSON 产物逐字节相同
    if payload not in io.open(TABLE_JS, encoding="utf-8").read():
        print("  ✗ 断言失败：lang-table.js 内嵌内容与 lang-table.json 不一致")
        return 1

    print("  产出 tools/lang-table.json  %d bytes" % os.path.getsize(TABLE_JSON))
    print("  产出 assets/lang-table.js   %d bytes (gzip 前)" % os.path.getsize(TABLE_JS))
    print("  覆盖词 %d 条 · 保护词 %d 条" % (len(overrides), len(protect)))

    # 自检
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    from _s2t import S2T
    conv = S2T(table)
    samples = ["德益师兄的宝库", "视频号", "微信公众号", "知识产权声明",
               "此处填写：资料名称", "项目启动", "税务居民身份判断", "软件与网络数据"]
    print("  自检：")
    for s in samples:
        print("    %s  →  %s" % (s, conv.convert(s)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
