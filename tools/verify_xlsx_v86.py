#!/usr/bin/env python3
"""Verify docs/WH3_abilities_master_v86_2026-11-28.xlsx (round 220), re-opened from disk, against v85: v85
byte-unchanged; the same 1,802 data rows; Abilities equal except the 51 planned cells (column 22 of the placed keys);
Cards equal except the 39 that changed in the mod, every card equal to the mod's own (harness run); Numbers equal
except the date line, and still reconciling; Transforms unchanged; the tracker carries the round; Definitions section
83; one v86 Changelog row with the installed md5.
Usage: verify_xlsx_v86.py <v85 md5> <installed pack md5>"""
import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openpyxl  # noqa: E402

import gen_anim_keys as GA  # noqa: E402
import make_xlsx_v74 as V74  # noqa: E402
import make_xlsx_v86 as M  # noqa: E402

V85_MD5 = sys.argv[1]
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


ok("v85 byte-unchanged (md5 %s)" % V85_MD5, hashlib.md5(open(M.SRC, "rb").read()).hexdigest() == V85_MD5)
plan = M.plan()
want = {(r, c): new for r, c, old, new in plan}
a85, a86 = rows(M.SRC, "Abilities"), rows(M.DST, "Abilities")
ok("the same data-row count as v85 (%d)" % (len(a86) - 1), len(a85) == len(a86) == 1803)
diff = {(i, j): q for i, (x, y) in enumerate(zip(a85, a86), start=1) for j, (p, q) in enumerate(zip(x, y), start=1) if p != q}
ok("Abilities: exactly the 51 planned cells changed (%d)" % len(diff), diff == want and len(want) == 51)
gone = M.placed()
carry = [x for x in a86[1:] if M.PLACED_ADD in str(x[21])]
ok("the PLACED sentence sits on exactly the rows of the 51 placed keys",
   len(carry) == 51 and len(gone) == 51 and all(str(x[2]).split(";")[0].strip() in gone for x in carry)
   and all(str(x[21]).endswith(M.PLACED_ADD) for x in carry))
by = {str(x[2]).split(";")[0].strip(): x for x in a86[1:]}
ok("Brass Orb carries it, Amber Bow (a projectile) does not",
   M.PLACED_ADD in by["wh2_dlc12_character_abilities_brass_orb"][21]
   and M.PLACED_ADD not in str(by["wh2_dlc13_weapon_abilities_amber_bow"][21]))
ok("no semicolon and no em dash in the new text", ";" not in M.PLACED_ADD and "\u2014" not in M.PLACED_ADD)
src = open(M.LIVE, encoding="utf-8").read()
anim = set(GA.derive(src))
ok("the mod source: the ANIM set is the generator's, 183 keys, none of the 51 placed keys in it",
   ('\nFOURTH.ANIM_TEXT = "%s"\n' % GA.text(sorted(anim))) in src and len(anim) == 183 and not (anim & gone))
entries, fc = M.family_counts()
fam = {e["marker"]: e["trigger"] for e in entries}
st = V74.source_types()
tot, exc, inc, n_impl, car, ex = V74.counts(a86[1:], st)
nm85, nm86 = rows(M.SRC, "Numbers"), rows(M.DST, "Numbers")
ok("Numbers still reconcile to the rows (1,802 / 687 / 1,115 / 1,035)",
   [nm86[r - 1][2] for r in range(10, 14)] == [tot, exc, inc, n_impl] and (tot, exc, inc, n_impl) == (1802, 687, 1115, 1035))
ndiff = [i for i, (p, q) in enumerate(zip(nm85, nm86), start=1) if p != q]
famrows = {r[1]: (r[2], r[3]) for r in nm86[43:184] if r[1]}
ok("Numbers: changed only the date line (%s), every family row equals the mod" % ndiff,
   len(nm85) == len(nm86) and ndiff == [7] and all(list(famrows[f]) == fc[f] for f in famrows))
c85, c86 = rows(M.SRC, "Cards"), rows(M.DST, "Cards")
cards = M.read_cards()
cdiff = sorted(y[0] for x, y in zip(c85, c86) if x != y)
ok("Cards: exactly the 39 cards the mod changed (%d), every card equals the mod's (harness 218 run)" % len(cdiff),
   len(c85) == len(c86) and cdiff == M.changed_cards() and len(cdiff) == 39
   and all(r[4] == cards[r[0]] and r[2] == fam[r[0]] for r in c86[1:] if r[0]))
ok("none of the changed cards asks the caster to stand still any more",
   all("it and the target stand" not in cards[m] and "when standing still" not in cards[m] for m in cdiff))
t85, t86 = rows(M.SRC, "Transforms"), rows(M.DST, "Transforms")
ok("Transforms unchanged", t85 == t86)
trk = open(r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_ability_tracker.md", encoding="utf-8").read()
ok("the tracker carries the round (section 10.97)", "### 10.97 Round 220" in trk)
d = rows(M.DST, "Definitions")
ok("Definitions: title v86 and section 83", d[0][0] == "DEFINITIONS - WH3 ability master v86 (2026-11-28)"
   and any(str(r[0]).startswith("83. ROUND 220") for r in d))
h85, h86 = rows(M.SRC, "Changelog"), rows(M.DST, "Changelog")
ok("Changelog: one v86 row with the installed md5", len(h86) == len(h85) + 1 and h86[-1][1] == "v86"
   and PACK_MD5 in h86[-1][2] and "PENDING" not in h86[-1][2] and h86[:-1] == h85)
print("XLSX v86 VERIFY OK" if good else "XLSX v86 VERIFY FAILED")
sys.exit(0 if good else 1)
