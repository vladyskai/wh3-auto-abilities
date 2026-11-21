#!/usr/bin/env python3
"""Verify docs/WH3_abilities_master_v73_2026-11-21.xlsx (round 191: the animation decides in group 1),
re-opened from disk. v73 is v72 plus 50 appended sentences, so the proof is a cell-by-cell comparison with v72:
  1. v72 is byte-unchanged; every sheet has the same rows;
  2. Abilities: every cell equals v72 except column 22 of exactly the 50 rows, which hold v72's text plus the sentence;
     spot rows: Oil Flask and Celestial Comet carry it, Accusation (same trigger, no animation) does not;
  3. Numbers: unchanged except the date line; 4. Definitions: title v73 and section 70; Changelog: one v73 row with
     the installed md5."""
import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openpyxl  # noqa: E402

import make_xlsx_v73 as M  # noqa: E402

V71_MD5 = "a7676157de249e65c4ecfbca2107f026"
PACK_MD5 = "ffd2f85006fd334d245a2710d3449656"
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


ok("v72 byte-unchanged (md5 %s)" % V71_MD5, hashlib.md5(open(M.SRC, "rb").read()).hexdigest() == V71_MD5)
plan = M.plan()
want = {r: (t, n) for r, k, t, n in plan}
ok("the plan extends 50 rows", len(want) == 50)
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
ok("Abilities: every cell equals v72 except the 50 extended trigger texts (%d off%s)"
   % (len(bad), (": " + str(bad[:3])) if bad else ""), not bad)
by = {str(x[2]).split(";")[0].strip(): x for x in a72[1:]}
for k, has in (("wh2_dlc13_lord_abilities_oil_flask", True), ("wh3_main_mount_bound_celestial_comet", True),
               ("wh_main_hero_abilities_accusation", False)):
    ok("spot row %s %s the sentence" % (k, "carries" if has else "lacks"), ((M.SENTENCE in (by[k][21] or "")) == has))
for sheet, allow in (("Numbers", {7}), ("Cards", set()), ("Transforms", set())):
    x, y = rows(M.SRC, sheet), rows(M.DST, sheet)
    diff = [i for i, (p, q) in enumerate(zip(x, y), start=1) if p != q]
    ok("%s: same rows (%d), changed only %s (%s)" % (sheet, len(y), sorted(allow) or "none", diff),
       len(x) == len(y) and set(diff) <= allow)
num = rows(M.DST, "Numbers")
ok("Numbers: the totals still read 988 / 1041 (row 185)", num[184][2] == 988 and num[184][3] == 1041)
ok("Numbers: the date line says v73 / round 191", "v73 - ROUND 191" in str(num[6][0]))
d = rows(M.DST, "Definitions")
ok("Definitions: title v73", d[0][0] == "DEFINITIONS - WH3 ability master v73 (2026-11-21)")
ok("Definitions: section 70", any(str(r[0]).startswith("70. ROUND 191") for r in d))
c71, c72 = rows(M.SRC, "Changelog"), rows(M.DST, "Changelog")
ok("Changelog: one new row, v73, with the installed md5", len(c72) == len(c71) + 1 and c72[-1][1] == "v73"
   and PACK_MD5 in c72[-1][2] and c72[:-1] == c71)
print("XLSX v73 VERIFY OK" if good else "XLSX v73 VERIFY FAILED")
sys.exit(0 if good else 1)
