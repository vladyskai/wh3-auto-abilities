#!/usr/bin/env python3
"""Verify docs/WH3_abilities_master_v77_2026-11-22.xlsx (round 198), re-opened from disk, against v76: v76
byte-unchanged; Abilities equal except column 22 of the 10 planned rows; Cards equal except column 5 of the 3 planned
rows; Numbers equal except the date line; Transforms unchanged; Definitions section 74; one v77 Changelog row with the
installed md5. Usage: verify_xlsx_v77.py <v76 md5> <installed pack md5>"""
import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openpyxl  # noqa: E402

import make_xlsx_v77 as M  # noqa: E402

V76_MD5 = sys.argv[1]
PACK_MD5 = sys.argv[2]
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


ok("v76 byte-unchanged (md5 %s)" % V76_MD5, hashlib.md5(open(M.SRC, "rb").read()).hexdigest() == V76_MD5)
plan, cards = M.plan()
want = {r: (t, n) for r, k, t, n in plan}
ok("the plan restates 10 trigger texts and 3 cards", len(want) == 10 and len(cards) == 3)
a76, a77 = rows(M.SRC, "Abilities"), rows(M.DST, "Abilities")
bad = []
for i, (x, y) in enumerate(zip(a76, a77), start=1):
    for j, (p, q) in enumerate(zip(x, y), start=1):
        if j == 22 and i in want:
            if p != want[i][0] or q != want[i][1] or p == q:
                bad.append((i, j))
        elif p != q:
            bad.append((i, j))
ok("Abilities: same rows, every cell equal except the 10 restated trigger texts (%d off)" % len(bad),
   len(a76) == len(a77) == 1803 and not bad)
by = {str(x[2]).split(";")[0].strip(): x for x in a77[1:]}
ok("Bugman's XXXXXX says 55 m", "no visible enemy within 55 m" in by["wh3_dlc26_item_abilities_bugmans_xxxxxx"][21])
ok("Favour of the Fay says never on the caster", "NEVER on the caster" in by["wh_dlc07_lord_abilities_favour_of_the_fay"][21])
ok("The Rock of Inevitability says RUNNING and CLOSING",
   "RUNNING and CLOSING" in by["wh3_main_item_abilities_the_rock_of_inevitability"][21])
ok("no semicolon and no em dash in the new pieces",
   all(";" not in n and "—" not in n for o, n in M.TEXTS.values() if o is not M.SNARE[0]))
cw = {r: (t, n) for r, m, t, n in cards}
c76, c77 = rows(M.SRC, "Cards"), rows(M.DST, "Cards")
cbad = []
for i, (x, y) in enumerate(zip(c76, c77), start=1):
    for j, (p, q) in enumerate(zip(x, y), start=1):
        if j == 5 and i in cw:
            if p != cw[i][0] or q != cw[i][1]:
                cbad.append((i, j))
        elif p != q:
            cbad.append((i, j))
ok("Cards: same rows, every cell equal except the 3 restated cards (%d off)" % len(cbad), len(c76) == len(c77) and not cbad)
for sheet, allow in (("Numbers", {7}), ("Transforms", set())):
    x, y = rows(M.SRC, sheet), rows(M.DST, sheet)
    diff = [i for i, (p, q) in enumerate(zip(x, y), start=1) if p != q]
    ok("%s: same rows, changed only %s (%s)" % (sheet, sorted(allow) or "none", diff), len(x) == len(y) and set(diff) <= allow)
d = rows(M.DST, "Definitions")
ok("Definitions: title v77 and section 74", d[0][0] == "DEFINITIONS - WH3 ability master v77 (2026-11-22)"
   and any(str(r[0]).startswith("74. ROUND 198") for r in d))
h76, h77 = rows(M.SRC, "Changelog"), rows(M.DST, "Changelog")
ok("Changelog: one v77 row with the installed md5", len(h77) == len(h76) + 1 and h77[-1][1] == "v77"
   and PACK_MD5 in h77[-1][2] and h77[:-1] == h76)
print("XLSX v77 VERIFY OK" if good else "XLSX v77 VERIFY FAILED")
sys.exit(0 if good else 1)
