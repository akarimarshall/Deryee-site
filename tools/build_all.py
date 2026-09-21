#!/usr/bin/env python3
"""一键重建全站衍生内容（改了任何中文文案 / 增删页面后都跑这个）

    python tools/build_all.py

依次执行：
  1. tools/build_lang_dict.py  重建简繁映射表（按语料裁剪词典）
  2. tools/gen_zh_tw.py        重新生成 /zh-tw/ 繁体镜像 + 繁体搜索索引
                               （内部会自动调用 build_index.py --mirror）
  3. tools/build_index.py      重建简体搜索索引
  4. tools/gen_sitemap.py      重建 sitemap.xml（含 hreflang）与 robots.txt

说明：zh-tw/ 是「生成物」，不要手改；改简体源页后跑本脚本即可同步。
"""
import io
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(ROOT, "tools")

STEPS = [
    ("简繁映射表", "build_lang_dict.py"),
    ("繁体镜像 + 繁体索引", "gen_zh_tw.py"),
    ("简体搜索索引", "build_index.py"),
    ("sitemap / robots", "gen_sitemap.py"),
]


def main():
    print("deryee.pro · 一键重建\n")
    for name, script in STEPS:
        print("── %s …" % name)
        r = subprocess.call([sys.executable, os.path.join(TOOLS, script)])
        if r != 0:
            print("\n✗ 步骤失败：%s（退出码 %d），后续步骤已中止" % (script, r))
            return r
        print("")
    print("✓ 全部完成：简繁两版已同步")
    return 0


if __name__ == "__main__":
    sys.exit(main())
