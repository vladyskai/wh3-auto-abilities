#!/usr/bin/env python3
"""Verify docs/WH3_abilities_master_v84_2026-11-22.xlsx (round 210), re-opened from disk, against v83: v83
byte-unchanged; the same 1,802 data rows; Abilities equal except the 9 planned cells (the Loons' columns 21 and 22, the
five breaths' column 22); Cards equal except the two Loons cards, which equal the mod's own (harness run); Numbers equal
except the date line, the family note and the two family counts, and still reconciling; Transforms unchanged; the
tracker carries the round; Definitions section 81; one v84 Changelog row with the installed md5.
Usage: verify_xlsx_v84.py <v83 md5> <installed pack md5>"""
import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openpyxl  # noqa: E402

import make_xlsx_v74 as V74  # noqa: E402
import make_xlsx_v84 as M  # noqa: E402

V83_MD5 = sys.argv[1]
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


ok("v83 byte-unchanged (md5 %s)" % V83_MD5, hashlib.md5(open(M.SRC, "rb").read()).hexdigest() == V83_MD5)
plan = M.plan()
want = {(r, c): new for r, c, old, new in plan}
a83, a84 = rows(M.SRC, "Abilities"), rows(M.DST, "Abilities")
ok("the same data-row count as v83 (%d)" % (len(a84) - 1), len(a83) == len(a84) == 1803)
diff = {(i, j): q for i, (x, y) in enumerate(zip(a83, a84), start=1) for j, (p, q) in enumerate(zip(x, y), start=1) if p != q}
ok("Abilities: exactly the 9 planned cells changed (%d)" % len(diff), diff == want and len(want) == 9)
by = {str(x[2]).split(";")[0].strip(): x for x in a84[1:]}
ok("the Loons read enemy_wave_charge with the user's rule, the five breaths carry the FROM THE CASTER sentence",
   all(by[k][20] == "enemy_wave_charge" and by[k][21] == M.LOON_TRIG for k in M.LOONS)
   and all(by[k][20] == "enemy_cone" and by[k][21].endswith(M.CONE_ADD) for k in M.CONES))
ok("no semicolon and no em dash in the new texts", all(";" not in s and "\u2014" not in s for s in (M.LOON_TRIG, M.CONE_ADD)))
entries, fc = M.family_counts()
fam = {e["marker"]: e["trigger"] for e in entries}
ok("the mod source: the Loons on enemy_wave_charge (2 entries), 72 on enemy_ground_melee, 5 on enemy_cone",
   fam["spinning_loons"] == fam["loons_of_eight_peaks"] == "enemy_wave_charge" and fc["enemy_wave_charge"] == [2, 2]
   and fc["enemy_ground_melee"][0] == 72 and fc["enemy_cone"] == [5, 5])
st = V74.source_types()
tot, exc, inc, n_impl, car, ex = V74.counts(a84[1:], st)
nm83, nm84 = rows(M.SRC, "Numbers"), rows(M.DST, "Numbers")
ok("Numbers still reconcile to the rows (1,802 / 687 / 1,115 / 1,035)",
   [nm84[r - 1][2] for r in range(10, 14)] == [tot, exc, inc, n_impl] and (tot, exc, inc, n_impl) == (1802, 687, 1115, 1035))
ndiff = [i for i, (p, q) in enumerate(zip(nm83, nm84), start=1) if p != q]
famrows = {r[1]: (r[2], r[3]) for r in nm84[43:184] if r[1]}
ok("Numbers: changed only the date line, the family note and the two family rows (%s)" % ndiff,
   len(nm83) == len(nm84) and len(ndiff) == 4 and 7 in ndiff and 42 in ndiff
   and all(list(famrows[f]) == fc[f] for f in famrows))
c83, c84 = rows(M.SRC, "Cards"), rows(M.DST, "Cards")
cards = M.read_cards()
cdiff = [y[0] for x, y in zip(c83, c84) if x != y]
ok("Cards: only the two Loons cards changed and every card equals the mod's (%s)" % cdiff,
   len(c83) == len(c84) and sorted(cdiff) == sorted(M.MARKERS) and all(r[4] == cards[r[0]] and r[2] == fam[r[0]] for r in c84[1:] if r[0]))
ok("the Loons' card names the new rule",
   cards["spinning_loons"].startswith("Fires when standing still at enemy infantry approaching the unit, the path clear of allies"))
t83, t84 = rows(M.SRC, "Transforms"), rows(M.DST, "Transforms")
ok("Transforms unchanged", t83 == t84)
trk = open(r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_ability_tracker.md", encoding="utf-8").read()
ok("the tracker carries the round (section 10.87)", "### 10.87 Round 210" in trk)
d = rows(M.DST, "Definitions")
ok("Definitions: title v84 and section 81", d[0][0] == "DEFINITIONS - WH3 ability master v84 (2026-11-22)"
   and any(str(r[0]).startswith("81. ROUND 210") for r in d))
h83, h84 = rows(M.SRC, "Changelog"), rows(M.DST, "Changelog")
ok("Changelog: one v84 row with the installed md5", len(h84) == len(h83) + 1 and h84[-1][1] == "v84"
   and PACK_MD5 in h84[-1][2] and "PENDING" not in h84[-1][2] and h84[:-1] == h83)
print("XLSX v84 VERIFY OK" if good else "XLSX v84 VERIFY FAILED")
sys.exit(0 if good else 1)
