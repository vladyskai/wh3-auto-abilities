#!/usr/bin/env python3
"""Verify docs/WH3_abilities_master_v74_2026-11-21.xlsx (round 192), re-opened from disk, against v73:
  1. v73 is byte-unchanged;
  2. Abilities: v73's 1,800 rows unchanged except the planned cells (5 runes x 5 cells, 30 CLOSING texts, 2 MOULDER
     texts); exactly two new rows (#1801 Grombrindal Has No Fear IMPLEMENTED, #1802 Scry-Orb NOT IMPLEMENTED);
     every IMPLEMENTED key equals the mod's own key list (1,037);
  3. Numbers: 1,802 = 1,120 + 682; 1,037 + 83 = 1,120; the carrier table and the exclusions table tie to the headline;
     the family table totals 984 / 1,037; Cards and Transforms unchanged;
  4. Definitions: title v74, section 71; Changelog: one v74 row with the installed md5."""
import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openpyxl  # noqa: E402

import build_ability_database as bd  # noqa: E402
import make_xlsx_v74 as M  # noqa: E402

V73_MD5 = "2f95a22e886c3a6d0d418bb8347923d2"
PACK_MD5 = "1a12ea1543904e6ae0fc01799d3a905d"
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


ok("v73 byte-unchanged (md5 %s)" % V73_MD5, hashlib.md5(open(M.SRC, "rb").read()).hexdigest() == V73_MD5)
wb73 = openpyxl.load_workbook(M.SRC)
plan, fast_keys = M.plan(wb73["Abilities"])
want = {(r, c): (o, n) for r, c, o, n in plan}
ok("the plan: 57 cells (25 rune cells, 30 CLOSING, 2 MOULDER)", len(want) == 57
   and sum(1 for v in want.values() if str(v[1]).endswith(M.FAST_SENTENCE)) == 30
   and sum(1 for v in want.values() if str(v[1]).endswith(M.MOULDER_SENTENCE)) == 2)
a73, a74 = rows(M.SRC, "Abilities"), rows(M.DST, "Abilities")
ok("Abilities: 1,800 -> 1,802 data rows", len(a73) == 1801 and len(a74) == 1803)
bad = []
for i, (x, y) in enumerate(zip(a73, a74), start=1):
    for j, (p, q) in enumerate(zip(x, y), start=1):
        if (i, j) in want:
            if p != want[(i, j)][0] or q != want[(i, j)][1]:
                bad.append((i, j))
        elif p != q:
            bad.append((i, j))
ok("Abilities: every v73 cell unchanged except the planned ones (%d off%s)" % (len(bad), (": " + str(bad[:3])) if bad else ""),
   not bad)
new = a74[-2:]
ok("new row #1801 Grombrindal Has No Fear: IN-WHEEL, IMPLEMENTED, melee_or_wavering_aura",
   new[0][0] == 1801 and new[0][2] == M.GHNF and new[0][17] == "IN-WHEEL" and new[0][19] == "IMPLEMENTED"
   and new[0][20] == "melee_or_wavering_aura")
ok("new row #1802 Scry-Orb: IN-WHEEL, NOT IMPLEMENTED", new[1][0] == 1802 and new[1][2] == M.SCRY
   and new[1][17] == "IN-WHEEL" and new[1][19] == "NOT IMPLEMENTED")
by = {str(x[2]).split(";")[0].strip(): x for x in a74[1:]}
ok("the five runes: EXCLUDED, REMOVED (spell bar)", all(by[k][17] == "EXCLUDED" and by[k][19] == M.RUNE_IMPL for k in M.RUNES))
ok("Mither carries the CLOSING sentence", by["wh2_dlc15_hero_abilities_mither"][21].endswith(M.FAST_SENTENCE))
ok("Shock Collar / Remouldered carry the MOULDER sentence", all(by[k][21].endswith(M.MOULDER_SENTENCE) for k in M.MOULDER))
entries, _, _ = bd.mod_entries()
mod_keys = {k for e in entries for k in e["keys"]}
impl = {k for k, x in by.items() if x[19] == "IMPLEMENTED"}
ok("IMPLEMENTED keys == the mod's keys (%d)" % len(mod_keys), impl == mod_keys and len(mod_keys) == 1037)
num = rows(M.DST, "Numbers")
c = [num[i][2] for i in range(9, 16)]
ok("Numbers headline 1,802 / 682 / 1,120 / 1,037 / 83 / 0 / 1,037", c == [1802, 682, 1120, 1037, 83, 0, 1037])
car = num[19:28]
ok("carrier table ties (sum %d / %d) and row 29 holds the total" % (sum(r[2] for r in car), sum(r[3] for r in car)),
   sum(r[2] for r in car) == 1120 and sum(r[3] for r in car) == 1037 and num[28][2] == 1120 and num[28][3] == 1037)
ex = num[31:38]
ok("exclusions table ties (sum %d) and row 39 holds the total" % sum(r[2] for r in ex),
   sum(r[2] for r in ex) == 682 and num[38][2] == 682 and ex[-1][2] == 5)
ok("family table totals 984 / 1,037", num[184][2] == 984 and num[184][3] == 1037
   and sum(num[i][2] for i in range(43, 184)) == 984)
x, y = rows(M.SRC, "Transforms"), rows(M.DST, "Transforms")
ok("Transforms unchanged", x == y)
cs = rows(M.DST, "Cards")
cards = M.read_cards()
ok("Cards: 984 entries, each the card the mod composed in the harness-191 run; no rune left; Grombrindal Has No Fear "
   "listed; Shock Collar names the Moulder rule",
   len(cs) == 985 and all(cards[r[0]] == r[4] for r in cs[1:]) and {r[0] for r in cs[1:]} == {e["marker"] for e in entries}
   and not any(r[0] in ("rune_of_breaking", "rune_of_negation", "rune_of_slowness", "rune_of_speed", "rune_of_oath_and_steel")
               for r in cs[1:])
   and any(r[0] == "grombrindal_has_no_fear" for r in cs[1:])
   and "Clan Moulder monster allies only" in cards["shock_collar"])
d = rows(M.DST, "Definitions")
ok("Definitions: title v74 and section 71", d[0][0] == "DEFINITIONS - WH3 ability master v74 (2026-11-21)"
   and any(str(r[0]).startswith("71. ROUND 192") for r in d))
c73, c74 = rows(M.SRC, "Changelog"), rows(M.DST, "Changelog")
ok("Changelog: one new row, v74, with the installed md5", len(c74) == len(c73) + 1 and c74[-1][1] == "v74"
   and PACK_MD5 in c74[-1][2] and c74[:-1] == c73)
print("XLSX v74 VERIFY OK" if good else "XLSX v74 VERIFY FAILED")
sys.exit(0 if good else 1)
