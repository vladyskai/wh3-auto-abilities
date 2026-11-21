#!/usr/bin/env python3
"""Verify docs/WH3_abilities_master_v71_2026-11-21.xlsx (round 189: the line of fire), re-opened from disk.

v71 is v70 plus 35 appended sentences, so the proof is a cell-by-cell comparison with v70:
  1. every sheet has the same rows; v70 is byte-unchanged (md5 recorded before the build);
  2. Abilities: every cell equals v70 except column 22 of exactly the 35 line-of-sight rows, which hold v70's text plus
     the sentence; spot rows: Focused Shot, Cackle Fruit, the Executioner carry it, Gaze of Nagash (not tagged) not;
  3. Numbers: unchanged except the date line (988 entries / 1,041 keys);
  4. Definitions: title v71 and section 68; Changelog: one new v71 row carrying the installed md5."""
import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openpyxl  # noqa: E402

import make_xlsx_v71 as M  # noqa: E402

V70_MD5 = "5b420d3c5bd87bd74596b2203fc4d261"
PACK_MD5 = "dab056dfb3b0508d31575de3b78e8a95"
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


ok("v70 byte-unchanged (md5 %s)" % V70_MD5, hashlib.md5(open(M.SRC, "rb").read()).hexdigest() == V70_MD5)
plan = M.plan()
want = {r: (t, n) for r, k, t, n in plan}
ok("the plan extends 35 rows", len(want) == 35)
a70, a71 = rows(M.SRC, "Abilities"), rows(M.DST, "Abilities")
ok("Abilities: same data-row count (%d)" % (len(a71) - 1), len(a70) == len(a71) == 1801)
bad = []
for i, (x, y) in enumerate(zip(a70, a71), start=1):
    for j, (p, q) in enumerate(zip(x, y), start=1):
        if j == 22 and i in want:
            if p != want[i][0] or q != want[i][1] or not q.endswith(M.SENTENCE):
                bad.append((i, j))
        elif p != q:
            bad.append((i, j))
ok("Abilities: every cell equals v70 except the 35 extended trigger texts (%d off%s)"
   % (len(bad), (": " + str(bad[:3])) if bad else ""), not bad)
by = {str(x[2]).split(";")[0].strip(): x for x in a71[1:]}
for k, has in (("wh2_dlc13_lord_abilities_kill_shot", True), ("wh2_dlc11_character_abilities_cackle_fruit", True),
               ("wh2_dlc13_lord_abilities_executioner", True), ("wh2_dlc15_spell_bound_gaze_of_nagash", False)):
    ok("spot row %s %s the sentence" % (k, "carries" if has else "lacks"), ((M.SENTENCE in (by[k][21] or "")) == has))
for sheet, allow in (("Numbers", {7}), ("Cards", set()), ("Transforms", set())):
    x, y = rows(M.SRC, sheet), rows(M.DST, sheet)
    diff = [i for i, (p, q) in enumerate(zip(x, y), start=1) if p != q]
    ok("%s: same rows (%d), changed only %s (%s)" % (sheet, len(y), sorted(allow) or "none", diff),
       len(x) == len(y) and set(diff) <= allow)
num = rows(M.DST, "Numbers")
ok("Numbers: the totals still read 988 / 1041 (row 185)", num[184][2] == 988 and num[184][3] == 1041)
ok("Numbers: the date line says v71 / round 189", "v71 - ROUND 189" in str(num[6][0]))
d = rows(M.DST, "Definitions")
ok("Definitions: title v71", d[0][0] == "DEFINITIONS - WH3 ability master v71 (2026-11-21)")
ok("Definitions: section 68", any(r[0] == "68. ROUND 189 - THE LINE OF FIRE (v71)" for r in d))
c70, c71 = rows(M.SRC, "Changelog"), rows(M.DST, "Changelog")
ok("Changelog: one new row, v71, with the installed md5", len(c71) == len(c70) + 1 and c71[-1][1] == "v71"
   and PACK_MD5 in c71[-1][2] and c71[:-1] == c70)
print("XLSX v71 VERIFY OK" if good else "XLSX v71 VERIFY FAILED")
sys.exit(0 if good else 1)
