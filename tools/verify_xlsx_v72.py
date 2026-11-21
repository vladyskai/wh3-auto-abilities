#!/usr/bin/env python3
"""Verify docs/WH3_abilities_master_v72_2026-11-21.xlsx (round 190: the animation decides in the shot triggers),
re-opened from disk. v72 is v71 plus 8 appended sentences, so the proof is a cell-by-cell comparison with v71:
  1. v71 is byte-unchanged; every sheet has the same rows;
  2. Abilities: every cell equals v71 except column 22 of exactly the 8 rows, which hold v71's text plus the sentence;
     spot rows: Amber Bow and The Black Tongue carry it, Hunting Spear (same trigger, no animation) does not;
  3. Numbers: unchanged except the date line; 4. Definitions: title v72 and section 69; Changelog: one v72 row with
     the installed md5."""
import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openpyxl  # noqa: E402

import make_xlsx_v72 as M  # noqa: E402

V71_MD5 = "4bc66fed4900a6bd3af34dc6a94367b5"
PACK_MD5 = "1b749a4d7c6815722a94db93f420eff0"
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


ok("v71 byte-unchanged (md5 %s)" % V71_MD5, hashlib.md5(open(M.SRC, "rb").read()).hexdigest() == V71_MD5)
plan = M.plan()
want = {r: (t, n) for r, k, t, n in plan}
ok("the plan extends 8 rows", len(want) == 8)
a71, a72 = rows(M.SRC, "Abilities"), rows(M.DST, "Abilities")
ok("Abilities: same data-row count (%d)" % (len(a72) - 1), len(a71) == len(a72) == 1801)
bad = []
for i, (x, y) in enumerate(zip(a71, a72), start=1):
    for j, (p, q) in enumerate(zip(x, y), start=1):
        if j == 22 and i in want:
            if p != want[i][0] or q != want[i][1] or not q.endswith(M.SENTENCE):
                bad.append((i, j))
        elif p != q:
            bad.append((i, j))
ok("Abilities: every cell equals v71 except the 8 extended trigger texts (%d off%s)"
   % (len(bad), (": " + str(bad[:3])) if bad else ""), not bad)
by = {str(x[2]).split(";")[0].strip(): x for x in a72[1:]}
for k, has in (("wh2_dlc13_weapon_abilities_amber_bow", True), ("wh3_dlc27_character_abilities_the_black_tongue", True),
               ("wh_dlc03_weapon_abilities_hunting_spear", False)):
    ok("spot row %s %s the sentence" % (k, "carries" if has else "lacks"), ((M.SENTENCE in (by[k][21] or "")) == has))
for sheet, allow in (("Numbers", {7}), ("Cards", set()), ("Transforms", set())):
    x, y = rows(M.SRC, sheet), rows(M.DST, sheet)
    diff = [i for i, (p, q) in enumerate(zip(x, y), start=1) if p != q]
    ok("%s: same rows (%d), changed only %s (%s)" % (sheet, len(y), sorted(allow) or "none", diff),
       len(x) == len(y) and set(diff) <= allow)
num = rows(M.DST, "Numbers")
ok("Numbers: the totals still read 988 / 1041 (row 185)", num[184][2] == 988 and num[184][3] == 1041)
ok("Numbers: the date line says v72 / round 190", "v72 - ROUND 190" in str(num[6][0]))
d = rows(M.DST, "Definitions")
ok("Definitions: title v72", d[0][0] == "DEFINITIONS - WH3 ability master v72 (2026-11-21)")
ok("Definitions: section 69", any(str(r[0]).startswith("69. ROUND 190") for r in d))
c71, c72 = rows(M.SRC, "Changelog"), rows(M.DST, "Changelog")
ok("Changelog: one new row, v72, with the installed md5", len(c72) == len(c71) + 1 and c72[-1][1] == "v72"
   and PACK_MD5 in c72[-1][2] and c72[:-1] == c71)
print("XLSX v72 VERIFY OK" if good else "XLSX v72 VERIFY FAILED")
sys.exit(0 if good else 1)
