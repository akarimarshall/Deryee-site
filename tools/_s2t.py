# -*- coding: utf-8 -*-
"""简→繁转换器（读取 tools/lang-table.json）

算法与 assets/lang.js 中的 JS 实现**逐字对应**，两者共用同一份映射表，
保证「Python 生成的静态镜像」与「浏览器端即时转换」结果完全一致。

处理顺序：
  1. protect 掩码        —— 保护词原样冻结
  2. overrides           —— 覆盖词表（简体键，最长优先）
  3. s2tPhrases          —— 简体→繁体词组（最长优先）
  4. chars               —— 简体→繁体单字
  5. twPhrases           —— 繁体→台湾繁体词组（最长优先）
  6. twVariants          —— 台湾异体字
  7. 还原 protect
"""
import io
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TABLE_PATH = os.path.join(ROOT, "tools", "lang-table.json")

SENTINEL = u"\ue000%d\ue001"


class S2T(object):
    def __init__(self, table=None):
        if table is None:
            table = json.load(io.open(TABLE_PATH, encoding="utf-8"))
        self.t = table
        self.protect = sorted(table.get("protect", []), key=len, reverse=True)
        self.overrides = table.get("overrides", {})
        self.maxOverride = table.get("maxOverrideLen", 0)
        self.s2tPhrases = table.get("s2tPhrases", {})
        self.maxS2t = table.get("maxS2tLen", 0)
        self.chars = table.get("chars", {})
        self.twPhrases = table.get("twPhrases", {})
        self.maxTw = table.get("maxTwLen", 0)
        self.twVariants = table.get("twVariants", {})

    # ---------- 核心 ----------
    def convert(self, s):
        if not s:
            return s
        # 1. protect 掩码
        store = []
        for i, word in enumerate(self.protect):
            if word and word in s:
                ph = SENTINEL % i
                store.append((ph, word))
                s = s.replace(word, ph)
        # 2. overrides（其结果立即冻结，避免被后面的台湾词组二次改写）
        s = self._phrases(s, self.overrides, self.maxOverride)
        base = len(self.protect)
        vals = []
        for v in set(self.overrides.values()):
            vals.append(v)
        vals.sort(key=len, reverse=True)
        for j, v in enumerate(vals):
            if v and v in s:
                ph = SENTINEL % (base + j)
                store.append((ph, v))
                s = s.replace(v, ph)
        # 3. 简体→繁体词组
        s = self._phrases(s, self.s2tPhrases, self.maxS2t)
        # 4. 单字
        s = self._chars(s, self.chars)
        # 5. 繁体→台湾词组
        s = self._phrases(s, self.twPhrases, self.maxTw)
        # 6. 台湾异体字
        s = self._chars(s, self.twVariants)
        # 7. 还原
        for ph, word in store:
            s = s.replace(ph, word)
        return s

    # ---------- 工具 ----------
    @staticmethod
    def _phrases(s, mapping, maxlen):
        """从左到右贪心最长匹配。maxlen 为表中最长键长度。"""
        if not mapping or maxlen < 2:
            return s
        out = []
        i = 0
        n = len(s)
        while i < n:
            hit_len = 0
            hit_val = None
            upper = maxlen if maxlen < (n - i) else (n - i)
            for L in range(upper, 1, -1):
                v = mapping.get(s[i:i + L])
                if v is not None:
                    hit_len = L
                    hit_val = v
                    break
            if hit_len:
                out.append(hit_val)
                i += hit_len
            else:
                out.append(s[i])
                i += 1
        return u"".join(out)

    @staticmethod
    def _chars(s, mapping):
        if not mapping:
            return s
        return u"".join(mapping.get(c, c) for c in s)


def load():
    return S2T()
