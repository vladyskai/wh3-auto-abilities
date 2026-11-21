#!/usr/bin/env python3
"""Verify docs/WH3_abilities_master_v70_2026-11-21.xlsx (round 188: the range rule), re-opened from disk.

v70 is v69 plus a deterministic rewrite, so the proof is a cell-by-cell comparison with v69 (which its own verifier,
verify_xlsx_v69.py, still passes byte-unchanged):
  1. every sheet has the same rows; v69 is byte-unchanged (md5 recorded before the build);
  2. Abilities: every cell equals v69 except column 22 (trigger text) of exactly the rows make_xlsx_v70.rewrite()
     changes, and those hold exactly the rewritten text;
  3. the rewritten texts carry no old bound of a changed real range (except the two history notes and the wave
     length listed in ALLOWED), and the spot rows read right: Focused Shot 230 m, Accusation 55 m, Warpstorm 80 m,
     Blood Sacrifice 80 m, the Executioner 230 m;
  4. Numbers: unchanged except the date line (no roster change: 988 entries / 1,041 keys / 141 families);
  5. Definitions: title v70 and section 67; Changelog: one new v70 row carrying the installed md5.
"""
import hashlib
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openpyxl  # noqa: E402

import make_xlsx_v70 as M70  # noqa: E402

V69_MD5 = "7d1a0eaf59a1f59e42b5f374f7332c84"
PACK_MD5 = "c478299540ea6704a364d16083145f57"
ALLOWED = {"bound 21 -> 70 m", "70 m long"}
good = True


def ok(name, cond):
    global good
    print(("OK   " if cond else "FAIL ") + name)
    good = good and bool(cond)


def rows(path, sheet):
    wb = openpyxl.load_workbook(path, read_only=True)
    out = [list(r) for r in wb[sheet].iter_rows(values_only=True)]
    wb.close()
    return out


ok("v69 byte-unchanged (md5 %s)" % V69_MD5, hashlib.md5(open(M70.SRC, "rb").read()).hexdigest() == V69_MD5)
plan = M70.plan()
want = {r: (t, n) for r, k, e, t, n in plan if t != n}
ok("the rewrite changes 359 rows", len(want) == 359)
a69, a70 = rows(M70.SRC, "Abilities"), rows(M70.DST, "Abilities")
ok("Abilities: same data-row count (%d)" % (len(a70) - 1), len(a69) == len(a70) == 1801)
bad = []
for i, (x, y) in enumerate(zip(a69, a70), start=1):
    for j, (p, q) in enumerate(zip(x, y), start=1):
        if j == 22 and i in want:
            if p != want[i][0] or q != want[i][1]:
                bad.append((i, j))
        elif p != q:
            bad.append((i, j))
ok("Abilities: every cell equals v69 except the %d rewritten trigger texts, which hold the rewrite (%d off%s)"
   % (len(want), len(bad), (": " + str(bad[:3])) if bad else ""), not bad)
res = []
for r, k, e, t, n in plan:
    for h in M70.residual(n, e):
        if not any(a in h for a in ALLOWED):
            res.append((k, h))
ok("no old bound left in a changed row (%d%s)" % (len(res), (": " + str(res[:2])) if res else ""), not res)
by = {str(x[2]).split(";")[0].strip(): x for x in a70[1:]}
spots = (("wh2_dlc13_lord_abilities_kill_shot", "within 230 m (max(70%, real - 20) of the ability's 250 m"),
         ("wh_main_hero_abilities_accusation", "bound: 55 m (max(70%, real - 20) of the ability's 75 m"),
         ("wh2_main_item_abilities_warpstorm_scroll", "within 80 m (max(70%, real - 20) of the game's 100 m)"),
         ("wh3_dlc26_lord_abilities_blood_sacrifice", "unit_distance <= 80 m"),
         ("wh2_dlc13_lord_abilities_executioner", "max(70%, real - 20): 230 m."))
for k, s in spots:
    ok("spot row %s reads %r" % (k, s), s in (by[k][21] or ""))
for sheet, allow in (("Numbers", {7}), ("Cards", set()), ("Transforms", set())):
    x, y = rows(M70.SRC, sheet), rows(M70.DST, sheet)
    diff = [i for i, (p, q) in enumerate(zip(x, y), start=1) if p != q]
    ok("%s: same rows (%d), changed only %s (%s)" % (sheet, len(y), sorted(allow) or "none", diff),
       len(x) == len(y) and set(diff) <= allow)
num = rows(M70.DST, "Numbers")
ok("Numbers: the totals still read 988 / 1041 (row 185)", num[184][2] == 988 and num[184][3] == 1041)
ok("Numbers: the date line says v70 / round 188", "v70 - ROUND 188" in str(num[6][0]))
d = rows(M70.DST, "Definitions")
ok("Definitions: title v70", d[0][0] == "DEFINITIONS - WH3 ability master v70 (2026-11-21)")
ok("Definitions: section 67", any(r[0] == "67. ROUND 188 - THE RANGE RULE (v70)" for r in d))
c69, c70 = rows(M70.SRC, "Changelog"), rows(M70.DST, "Changelog")
ok("Changelog: one new row, v70, with the installed md5", len(c70) == len(c69) + 1 and c70[-1][1] == "v70"
   and PACK_MD5 in c70[-1][2] and c70[:-1] == c69)
print("XLSX v70 VERIFY OK" if good else "XLSX v70 VERIFY FAILED")
sys.exit(0 if good else 1)
