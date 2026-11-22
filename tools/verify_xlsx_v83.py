#!/usr/bin/env python3
"""Verify docs/WH3_abilities_master_v83_2026-11-22.xlsx (round 209), re-opened from disk, against v82: v82
byte-unchanged; the same 1,802 data rows; Abilities equal except the 4 planned cells (the Loons' column 22, Lamprey's
Bite columns 21 and 22); Cards equal except the three cards, which equal the mod's own (harness run); Numbers equal
except the date line, the family note and the two family counts, and still reconciling; Transforms unchanged; the
tracker carries the round; Definitions section 80; one v83 Changelog row with the installed md5.
Usage: verify_xlsx_v83.py <v82 md5> <installed pack md5>"""
import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openpyxl  # noqa: E402

import make_xlsx_v74 as V74  # noqa: E402
import make_xlsx_v83 as M  # noqa: E402

V82_MD5 = sys.argv[1]
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


ok("v82 byte-unchanged (md5 %s)" % V82_MD5, hashlib.md5(open(M.SRC, "rb").read()).hexdigest() == V82_MD5)
plan = M.plan()
want = {(r, c): new for r, c, old, new in plan}
a82, a83 = rows(M.SRC, "Abilities"), rows(M.DST, "Abilities")
ok("the same data-row count as v82 (%d)" % (len(a83) - 1), len(a82) == len(a83) == 1803)
diff = {(i, j): q for i, (x, y) in enumerate(zip(a82, a83), start=1) for j, (p, q) in enumerate(zip(x, y), start=1) if p != q}
ok("Abilities: exactly the 4 planned cells changed (%d)" % len(diff), diff == want and len(want) == 4)
by = {str(x[2]).split(";")[0].strip(): x for x in a83[1:]}
ok("the Loons carry the RING sentence after their old text, Lamprey's Bite reads enemy_wave",
   all(by[k][21].endswith(M.RING) and by[k][20] == "enemy_ground_melee" for k in M.LOONS)
   and by[M.LAMP][20] == "enemy_wave" and by[M.LAMP][21] == M.LAMP_TRIG)
ok("no semicolon and no em dash in the new texts", all(";" not in s and "\u2014" not in s for s in (M.RING, M.LAMP_TRIG)))
entries, fc = M.family_counts()
fam = {e["marker"]: e["trigger"] for e in entries}
ok("the mod source: the Loons on enemy_ground_melee, Lamprey's Bite on enemy_wave, 33 waves, 41 wanderers",
   fam["spinning_loons"] == fam["loons_of_eight_peaks"] == "enemy_ground_melee" and fam["lampreys_bite"] == "enemy_wave"
   and fc["enemy_wave"] == [33, 33] and fc["enemy_wander"] == [41, 41])
st = V74.source_types()
tot, exc, inc, n_impl, car, ex = V74.counts(a83[1:], st)
nm82, nm83 = rows(M.SRC, "Numbers"), rows(M.DST, "Numbers")
ok("Numbers still reconcile to the rows (1,802 / 687 / 1,115 / 1,035)",
   [nm83[r - 1][2] for r in range(10, 14)] == [tot, exc, inc, n_impl] and (tot, exc, inc, n_impl) == (1802, 687, 1115, 1035))
ndiff = [i for i, (p, q) in enumerate(zip(nm82, nm83), start=1) if p != q]
famrows = {r[1]: (r[2], r[3]) for r in nm83[43:184] if r[1]}
ok("Numbers: changed only the date line, the family note and the two family rows (%s)" % ndiff,
   len(nm82) == len(nm83) and len(ndiff) == 4 and 7 in ndiff and 42 in ndiff
   and famrows["enemy_wave"] == (33, 33) and famrows["enemy_wander"] == (41, 41)
   and all(list(famrows[f]) == fc[f] for f in famrows))
c82, c83 = rows(M.SRC, "Cards"), rows(M.DST, "Cards")
cards = M.read_cards()
cdiff = [y[0] for x, y in zip(c82, c83) if x != y]
ok("Cards: only the three cards changed and every card equals the mod's (%s)" % cdiff,
   len(c82) == len(c83) and sorted(cdiff) == sorted(M.MARKERS) and all(r[4] == cards[r[0]] and r[2] == fam[r[0]] for r in c83[1:] if r[0]))
ok("the Loons' card names the friendly rule",
   cards["spinning_loons"].startswith("Fires at the nearest enemy in melee when none of our other units is near"))
t82, t83 = rows(M.SRC, "Transforms"), rows(M.DST, "Transforms")
ok("Transforms unchanged", t82 == t83)
trk = open(r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_ability_tracker.md", encoding="utf-8").read()
ok("the tracker carries the round (section 10.86)", "### 10.86 Round 209" in trk)
d = rows(M.DST, "Definitions")
ok("Definitions: title v83 and section 80", d[0][0] == "DEFINITIONS - WH3 ability master v83 (2026-11-22)"
   and any(str(r[0]).startswith("80. ROUND 209") for r in d))
h82, h83 = rows(M.SRC, "Changelog"), rows(M.DST, "Changelog")
ok("Changelog: one v83 row with the installed md5", len(h83) == len(h82) + 1 and h83[-1][1] == "v83"
   and PACK_MD5 in h83[-1][2] and "PENDING" not in h83[-1][2] and h83[:-1] == h82)
print("XLSX v83 VERIFY OK" if good else "XLSX v83 VERIFY FAILED")
sys.exit(0 if good else 1)
