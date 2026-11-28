#!/usr/bin/env python3
"""Verify docs/WH3_abilities_master_v85_2026-11-28.xlsx (round 219), re-opened from disk, against v84: v84
byte-unchanged; the same 1,802 data rows; Abilities equal except the 41 planned cells (column 22 of the enemy_wander
rows); Cards unchanged and equal to the mod's own (harness run); Numbers equal except the date line, and still
reconciling; Transforms unchanged; the tracker carries the round; Definitions section 82; one v85 Changelog row with
the installed md5.
Usage: verify_xlsx_v85.py <v84 md5> <installed pack md5>"""
import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openpyxl  # noqa: E402

import make_xlsx_v74 as V74  # noqa: E402
import make_xlsx_v85 as M  # noqa: E402

V84_MD5 = sys.argv[1]
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


ok("v84 byte-unchanged (md5 %s)" % V84_MD5, hashlib.md5(open(M.SRC, "rb").read()).hexdigest() == V84_MD5)
plan = M.plan()
want = {(r, c): new for r, c, old, new in plan}
a84, a85 = rows(M.SRC, "Abilities"), rows(M.DST, "Abilities")
ok("the same data-row count as v84 (%d)" % (len(a85) - 1), len(a84) == len(a85) == 1803)
diff = {(i, j): q for i, (x, y) in enumerate(zip(a84, a85), start=1) for j, (p, q) in enumerate(zip(x, y), start=1) if p != q}
ok("Abilities: exactly the 41 planned cells changed (%d)" % len(diff), diff == want and len(want) == 41)
wander = [x for x in a85[1:] if x[20] == "enemy_wander"]
ok("the 41 enemy_wander rows end with the COVER sentence, no other row carries it",
   len(wander) == 41 and all(x[21].endswith(M.COVER_ADD) for x in wander)
   and sum(1 for x in a85[1:] if M.COVER_ADD in str(x[21])) == 41)
ok("Brass Orb's row is one of them",
   any(str(x[2]).split(";")[0].strip() == "wh2_dlc12_character_abilities_brass_orb" for x in wander))
ok("no semicolon and no em dash in the new text", ";" not in M.COVER_ADD and "\u2014" not in M.COVER_ADD)
entries, fc = M.family_counts()
fam = {e["marker"]: e["trigger"] for e in entries}
ok("the mod source: 41 entries on enemy_wander, 982 entries", fc["enemy_wander"][0] == 41 and len(entries) == 982)
src = open(r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua", encoding="utf-8").read()
ok("the mod source carries the numbers the text names (half, 20, a 16 x 8 grid, 10 riders)",
   "FOURTH.COVER_FRACTION = 0.50\n" in src and "FOURTH.COVER_MIN_MEN = 20\n" in src
   and "\tfor i = 1, 16 do\n" in src and "\treturn e.men * hit / 128\n" in src and "FOURTH.BLOB_MIN_MEN = 10" in src)
st = V74.source_types()
tot, exc, inc, n_impl, car, ex = V74.counts(a85[1:], st)
nm84, nm85 = rows(M.SRC, "Numbers"), rows(M.DST, "Numbers")
ok("Numbers still reconcile to the rows (1,802 / 687 / 1,115 / 1,035)",
   [nm85[r - 1][2] for r in range(10, 14)] == [tot, exc, inc, n_impl] and (tot, exc, inc, n_impl) == (1802, 687, 1115, 1035))
ndiff = [i for i, (p, q) in enumerate(zip(nm84, nm85), start=1) if p != q]
famrows = {r[1]: (r[2], r[3]) for r in nm85[43:184] if r[1]}
ok("Numbers: changed only the date line (%s), every family row equals the mod" % ndiff,
   len(nm84) == len(nm85) and ndiff == [7] and all(list(famrows[f]) == fc[f] for f in famrows))
c84, c85 = rows(M.SRC, "Cards"), rows(M.DST, "Cards")
cards = M.read_cards()
ok("Cards: unchanged, and every card equals the mod's (harness 217 run)",
   c84 == c85 and all(r[4] == cards[r[0]] and r[2] == fam[r[0]] for r in c85[1:] if r[0]))
t84, t85 = rows(M.SRC, "Transforms"), rows(M.DST, "Transforms")
ok("Transforms unchanged", t84 == t85)
trk = open(r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_ability_tracker.md", encoding="utf-8").read()
ok("the tracker carries the round (section 10.96)", "### 10.96 Round 219" in trk)
d = rows(M.DST, "Definitions")
ok("Definitions: title v85 and section 82", d[0][0] == "DEFINITIONS - WH3 ability master v85 (2026-11-28)"
   and any(str(r[0]).startswith("82. ROUND 219") for r in d))
h84, h85 = rows(M.SRC, "Changelog"), rows(M.DST, "Changelog")
ok("Changelog: one v85 row with the installed md5", len(h85) == len(h84) + 1 and h85[-1][1] == "v85"
   and PACK_MD5 in h85[-1][2] and "PENDING" not in h85[-1][2] and h85[:-1] == h84)
print("XLSX v85 VERIFY OK" if good else "XLSX v85 VERIFY FAILED")
sys.exit(0 if good else 1)
