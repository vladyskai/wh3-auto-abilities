#!/usr/bin/env python3
"""Round 180: every entry's range_real / ally_range_real against the game's target_intercept_range (rule 3). Prints the
mismatches (marker, family, field, value, intercept, effect_range). Read-only."""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gamedata_paths as GP  # noqa: E402

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
s = open(SRC, encoding="utf-8").read()
usa = {}
with open(os.path.join(GP.GAMEDATA, "unit_spec_abil.tsv"), encoding="utf-8-sig") as f:
    h = f.readline().rstrip("\n").split("\t")
    f.readline()
    for line in f:
        d = dict(zip(h, line.rstrip("\n").split("\t")))
        usa[d["key"]] = d
bad = 0
for m in re.finditer(r'\t\{ marker = "([^"]+)", name = "[^"]+", trigger = "([^"]+)",(.*?)\t\tox = ', s, re.S):
    marker, fam, body = m.group(1), m.group(2), m.group(3)
    keys = re.findall(r'"([^"]+)"', re.search(r"keys = \{(.*?)\}", body, re.S).group(1))
    for field in ("range_real", "ally_range_real"):
        fm = re.search(r"\t\t%s = (\d+)," % field, body)
        if not fm:
            continue
        v = int(fm.group(1))
        for k in keys:   # every key of the entry (round 181: Lord of Undeath mixes 50 m and 200 m keys)
            d = usa.get(k)
            if d is None:
                continue
            ir = float(d["target_intercept_range"] or 0)
            er = float(d["effect_range"] or 0)
            if abs(ir - v) > 0.5:
                bad += 1
                print("%-45s %-28s %-15s %4d  intercept %6.1f  effect %6.1f  %s" % (marker, fam, field, v, ir, er, k))
print(bad, "mismatches")
