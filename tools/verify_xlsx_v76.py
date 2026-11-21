#!/usr/bin/env python3
"""Verify docs/WH3_abilities_master_v76_2026-11-21.xlsx (round 197), re-opened from disk, against v75: v75
byte-unchanged; Abilities equal except column 22 of the planned rows (v75 text + the sentence); Numbers equal except the
date line; Cards and Transforms unchanged; Definitions section 73; one v76 Changelog row with the installed md5."""
import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openpyxl  # noqa: E402

import make_xlsx_v76 as M  # noqa: E402

V75_MD5 = sys.argv[1]
PACK_MD5 = "febf51077902ccef857d0ac42cc872d7"
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


ok("v75 byte-unchanged (md5 %s)" % V75_MD5, hashlib.md5(open(M.SRC, "rb").read()).hexdigest() == V75_MD5)
plan = M.plan()
want = {r: (t, n) for r, k, t, n in plan}
ok("the plan extends %d rows (every blob-family key)" % len(want), len(want) == len(M.keys()) and len(want) >= 70)
a75, a76 = rows(M.SRC, "Abilities"), rows(M.DST, "Abilities")
bad = []
for i, (x, y) in enumerate(zip(a75, a76), start=1):
    for j, (p, q) in enumerate(zip(x, y), start=1):
        if j == 22 and i in want:
            if p != want[i][0] or q != want[i][1] or not q.endswith(M.SENTENCE):
                bad.append((i, j))
        elif p != q:
            bad.append((i, j))
ok("Abilities: same rows, every cell equal except the extended trigger texts (%d off)" % len(bad),
   len(a75) == len(a76) == 1803 and not bad)
by = {str(x[2]).split(";")[0].strip(): x for x in a76[1:]}
ok("Arrow of Kurnous carries the sentence", by["wh_dlc05_hero_abilities_arrow_of_kurnous"][21].endswith(M.SENTENCE))
for sheet, allow in (("Numbers", {7}), ("Cards", set()), ("Transforms", set())):
    x, y = rows(M.SRC, sheet), rows(M.DST, sheet)
    diff = [i for i, (p, q) in enumerate(zip(x, y), start=1) if p != q]
    ok("%s: same rows, changed only %s (%s)" % (sheet, sorted(allow) or "none", diff), len(x) == len(y) and set(diff) <= allow)
d = rows(M.DST, "Definitions")
ok("Definitions: title v76 and section 73", d[0][0] == "DEFINITIONS - WH3 ability master v76 (2026-11-21)"
   and any(str(r[0]).startswith("73. ROUND 197") for r in d))
c75, c76 = rows(M.SRC, "Changelog"), rows(M.DST, "Changelog")
ok("Changelog: one v76 row with the installed md5", len(c76) == len(c75) + 1 and c76[-1][1] == "v76"
   and PACK_MD5 in c76[-1][2] and c76[:-1] == c75)
print("XLSX v76 VERIFY OK" if good else "XLSX v76 VERIFY FAILED")
sys.exit(0 if good else 1)
