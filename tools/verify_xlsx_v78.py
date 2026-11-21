#!/usr/bin/env python3
"""Verify docs/WH3_abilities_master_v78_2026-11-22.xlsx (round 199), re-opened from disk, against v77: v77
byte-unchanged; Abilities equal except column 22 of the planned rows (v77 text + its sentence); Cards equal except
column 5 of the ten ally-arm cards; Numbers equal except the date line; Transforms unchanged; Definitions section 75;
one v78 Changelog row with the installed md5. Usage: verify_xlsx_v78.py <v77 md5> <installed pack md5>"""
import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openpyxl  # noqa: E402

import make_xlsx_v78 as M  # noqa: E402

V77_MD5 = sys.argv[1]
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


ok("v77 byte-unchanged (md5 %s)" % V77_MD5, hashlib.md5(open(M.SRC, "rb").read()).hexdigest() == V77_MD5)
plan, cards, counts = M.plan()
want = {r: (t, n) for r, k, t, n in plan}
ok("the plan: 8 ally arm + 2 ally only + %d bombardment keys, 10 cards" % counts[2],
   counts[0] == 8 and counts[1] == 2 and counts[2] >= 30 and len(cards) == 10 and len(want) == sum(counts))
a77, a78 = rows(M.SRC, "Abilities"), rows(M.DST, "Abilities")
bad = []
for i, (x, y) in enumerate(zip(a77, a78), start=1):
    for j, (p, q) in enumerate(zip(x, y), start=1):
        if j == 22 and i in want:
            if p != want[i][0] or q != want[i][1] or not (q.endswith(M.ARM) or q.endswith(M.ONLY) or q.endswith(M.INF)):
                bad.append((i, j))
        elif p != q:
            bad.append((i, j))
ok("Abilities: same rows, every cell equal except the extended trigger texts (%d off)" % len(bad),
   len(a77) == len(a78) == 1803 and not bad)
by = {str(x[2]).split(";")[0].strip(): x for x in a78[1:]}
ok("Spite of Da Bad Moon carries the ally arm", by["wh_dlc06_lord_abilities_spite_of_da_bad_moon"][21].endswith(M.ARM))
ok("Wild Abandon is ally only", by["wh3_dlc26_lord_abilities_wild_abandon"][21].endswith(M.ONLY))
ok("Assault of Stone carries the infantry sentence", by["wh2_dlc10_item_bound_assault_of_stone"][21].endswith(M.INF))
ok("no semicolon and no em dash in the new sentences",
   all(";" not in s and "—" not in s for s in (M.ARM, M.ONLY, M.INF, M.CARD_TAIL, M.CARD_ONLY)))
cw = {r: (t, n) for r, m, t, n in cards}
c77, c78 = rows(M.SRC, "Cards"), rows(M.DST, "Cards")
cbad = []
for i, (x, y) in enumerate(zip(c77, c78), start=1):
    for j, (p, q) in enumerate(zip(x, y), start=1):
        if j == 5 and i in cw:
            if p != cw[i][0] or q != cw[i][1]:
                cbad.append((i, j))
        elif p != q:
            cbad.append((i, j))
ok("Cards: same rows, every cell equal except the 10 restated cards (%d off)" % len(cbad), len(c77) == len(c78) and not cbad)
for sheet, allow in (("Numbers", {7}), ("Transforms", set())):
    x, y = rows(M.SRC, sheet), rows(M.DST, sheet)
    diff = [i for i, (p, q) in enumerate(zip(x, y), start=1) if p != q]
    ok("%s: same rows, changed only %s (%s)" % (sheet, sorted(allow) or "none", diff), len(x) == len(y) and set(diff) <= allow)
d = rows(M.DST, "Definitions")
ok("Definitions: title v78 and section 75", d[0][0] == "DEFINITIONS - WH3 ability master v78 (2026-11-22)"
   and any(str(r[0]).startswith("75. ROUND 199") for r in d))
h77, h78 = rows(M.SRC, "Changelog"), rows(M.DST, "Changelog")
ok("Changelog: one v78 row with the installed md5", len(h78) == len(h77) + 1 and h78[-1][1] == "v78"
   and PACK_MD5 in h78[-1][2] and h78[:-1] == h77)
print("XLSX v78 VERIFY OK" if good else "XLSX v78 VERIFY FAILED")
sys.exit(0 if good else 1)
