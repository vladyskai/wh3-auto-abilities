#!/usr/bin/env python3
"""Verify docs/WH3_abilities_master_v22_2026-11-01.xlsx from disk (no in-memory state).

  A. shape and counts: 1,800 = 1,123 + 677; 761 implemented rows / keys; same
     data-row count as v21;
  B. the 3 rows: IMPLEMENTED, the trigger family the mod gives their key, and
     the trigger text of that family (bounds and the Restock! charge hold);
  C. Skjalandir's Fall is on melee_or_shooting_into_melee in the sheet and the mod;
  D. the gates: no IN-WHEEL row carries an army_spec key; reasons well-formed;
  E. the join: mod 709 entries / 761 keys <-> sheet 761 implemented keys;
  F. Numbers: every block re-derived and tying, 49-family trigger table, the
     bombardment block moved intact to row 95;
  G. bookkeeping: autofilter, Definitions v22 + section 19, Changelog v22 with
     the pack md5; and v1-v21 byte-unchanged against the pre-build hash list.
"""
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import gamedata_paths as GP
import collections
import hashlib
import os
import sys

import openpyxl

sys.path.insert(0, r"C:\Users\vlady\Desktop\WH3_mod\tools")
import build_ability_database as bd

XLSX = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v22_2026-11-01.xlsx"
V21 = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v21_2026-10-28.xlsx"
ARMY_SPEC = GP.ARMY_SPEC
PRE_MD5 = r"C:\Users\vlady\Desktop\WH3_mod\docs\backups\round130\pre_v22_workbook_md5.txt"
PACK_MD5 = "0e786a41ce6a2a6f566f3b6c9b5172cd"

MU, AL, AF, MS = "melee_unwavering", "ally_ammo_low", "allies_firing_aura", "melee_or_shooting_into_melee"
RK = "wh2_dlc17_hero_abilities_more_powder_generic"
BK = "wh_main_hero_abilities_ballistics_calibration"
SK = "wh3_dlc23_character_abilities_skjalandirs_fall"
EXPECT = {RK: AL, BK: AF, SK: MS}
BOUNDS = {RK: "bound: 70 m (70% of the ability's 100 m", BK: "bound: 38 m (70% of the ability's 55 m"}
HOLDS = {RK: "charge hold 60 s (4 uses"}

fails = []


def check(cond, msg):
    if not cond:
        fails.append(msg)


army = set()
with open(ARMY_SPEC, encoding="utf-8", errors="replace") as f:
    f.readline()
    for line in f:
        c = line.rstrip("\n").split("\t")
        if c and c[0].strip() and not line.startswith("#"):
            army.add(c[0].strip())

wb = openpyxl.load_workbook(XLSX, data_only=True)
ws = wb["Abilities"]
rows = [tuple(ws.cell(row=r, column=c).value for c in range(1, 24)) for r in range(2, ws.max_row + 1)]
N = len(rows)
ident = lambda r: [x.strip() for x in str(r[2] or "").split(";") if x.strip()]
by_key = {k: r for r in rows for k in ident(r)}

# A
v21 = openpyxl.load_workbook(V21, read_only=True)["Abilities"]
n21 = sum(1 for _ in v21.iter_rows(min_row=2, values_only=True))
check(N == n21 == 1800, "A1: %d rows in v22, %d in v21, expected 1,800 both" % (N, n21))
check([r[0] for r in rows] == list(range(1, N + 1)), "A2: Item # is not 1..1800 in order")
st = collections.Counter(str(r[17]) for r in rows)
check(st == {"IN-WHEEL": 1123, "EXCLUDED": 677}, "A3: status counts %s" % dict(st))
impl_rows = [r for r in rows if str(r[19]) == "IMPLEMENTED"]
impl_keys = set(k for r in impl_rows for k in ident(r))
check(len(impl_rows) == 761 and len(impl_keys) == 761, "A4: %d implemented rows / %d keys, expected 761 / 761"
      % (len(impl_rows), len(impl_keys)))

# B
entries, consts, tips = bd.mod_entries()
fam_by_key = {k: e["trigger"] for e in entries for k in e["keys"]}
for k, fam in EXPECT.items():
    r = by_key.get(k)
    check(r is not None, "B0: `%s` has no row" % k)
    if r is None:
        continue
    check(str(r[19]) == "IMPLEMENTED", "B1: `%s` reads %s" % (k, r[19]))
    check(str(r[20]) == fam == fam_by_key.get(k), "B2: `%s` family sheet=%s want=%s mod=%s"
          % (k, r[20], fam, fam_by_key.get(k)))
    check(str(r[21]).startswith(fam + ":"), "B3: `%s` trigger text does not start with its family" % k)
    if k in BOUNDS:
        check(BOUNDS[k] in str(r[21]), "B5: `%s` trigger text does not carry its bound" % k)
    if k in HOLDS:
        check(HOLDS[k] in str(r[21]), "B6: `%s` trigger text does not carry its charge hold" % k)

# C
check(fam_by_key.get(SK) == MS and str(by_key[SK][20]) == MS, "C1: Skjalandir's Fall is not on %s" % MS)

# D
check(not [r[0] for r in rows if str(r[17]) == "IN-WHEEL" and any(k in army for k in ident(r))],
      "D1: an IN-WHEEL row carries an army_spec key")
for r in rows:
    if str(r[17]) == "IN-WHEEL":
        check(str(r[18]).startswith(("carrier family:", "skipped ")),
              "D2: IN-WHEEL row %s has an unexplained reason: %s" % (r[0], str(r[18])[:80]))

# E
mod_keys = set(fam_by_key)
check(len(entries) == 709 and len(mod_keys) == 761, "E1: mod %d entries / %d keys, expected 709 / 761"
      % (len(entries), len(mod_keys)))
check(not (mod_keys & army), "E2: army_spec keys in the mod")
check(impl_keys == mod_keys, "E3: rows-only %s, mod-only %s"
      % (sorted(impl_keys - mod_keys)[:5], sorted(mod_keys - impl_keys)[:5]))

# F
n = wb["Numbers"]
cell = lambda r, c: n.cell(row=r, column=c).value
for (r, want, lbl) in ((10, 1800, "inventory"), (11, 677, "excluded"), (12, 1123, "included"),
                       (13, 761, "implemented"), (14, 362, "not-implemented-included"), (16, 761, "all implemented")):
    check(cell(r, 3) == want, "F1: Numbers %s cell %s, expected %s" % (lbl, cell(r, 3), want))
check(cell(13, 3) + cell(14, 3) == cell(12, 3), "F2: implemented + not != included")
check(sum(cell(r, 3) for r in range(20, 28)) == cell(28, 3) == 1123, "F3: family block included does not tie")
check(sum(cell(r, 4) for r in range(20, 28)) == cell(28, 4) == 761, "F4: family block implemented does not tie")
check(sum(cell(r, 3) for r in range(32, 38)) == cell(38, 3) == 677, "F5: exclusion block does not tie")
te = [cell(r, 3) for r in range(44, 93)]
tk = [cell(r, 4) for r in range(44, 93)]
names = [str(cell(r, 2)) for r in range(44, 93)]
check(len(te) == 49 and all(isinstance(x, int) for x in te), "F6: trigger table is not 49 integer rows")
check(sum(te) == cell(93, 3) == 709 and sum(tk) == cell(93, 4) == 761, "F7: trigger table sums %s/%s vs %s/%s"
      % (sum(te), sum(tk), cell(93, 3), cell(93, 4)))
check(cell(95, 1) == "Bombardment set (COMPLETE - round 108)" and cell(97, 3) == 131,
      "F7b: the bombardment block did not move intact to row 95")
want_counts = {MU: 373, AL: 1, AF: 1, MS: 1, "charge_or_melee": 28, "enemy_engaged_or_shot": 85, "enemy_melee": 3}
for fam, cnt in want_counts.items():
    check(fam in names and te[names.index(fam)] == cnt, "F8: %s is not %d entries in the trigger table" % (fam, cnt))
check("v22" in str(cell(7, 1)) and "761" in str(cell(7, 1)), "F9: the date line is not the v22 line")

# G
check(ws.auto_filter.ref == "A1:W%d" % ws.max_row, "G1: autofilter %s" % ws.auto_filter.ref)
d = wb["Definitions"]
check(str(d.cell(row=1, column=1).value).startswith("DEFINITIONS - WH3 ability master v22"), "G2: title not v22")
check(any(str(d.cell(row=r, column=1).value or "").startswith("19. ROUND 130")
          for r in range(1, d.max_row + 1)), "G3: Definitions section 19 missing")
ch = wb["Changelog"]
last = str(ch.cell(row=ch.max_row, column=3).value)
check(str(ch.cell(row=ch.max_row, column=2).value) == "v22", "G4: last changelog row is not v22")
check(PACK_MD5 in last and "PENDING" not in last, "G5: the v22 changelog does not carry the pack md5")
pre = {}
for line in open(PRE_MD5, encoding="utf-8"):
    h, p = line.strip().split(" ", 1)
    pre[p.lstrip("*")] = h
changed = []
for p, h in pre.items():
    full = os.path.normpath(os.path.join(r"C:\Users\vlady\Desktop\WH3_mod\tools", p))
    if hashlib.md5(open(full, "rb").read()).hexdigest() != h:
        changed.append(p)
check(len(pre) == 38 and not changed, "G6: older workbook versions changed: %s (of %d hashed)" % (changed, len(pre)))

if fails:
    print("XLSX v22 VERIFY: %d FAILURE(S)" % len(fails))
    for f in fails:
        print("  -", f)
    sys.exit(1)
print("XLSX v22 VERIFY OK")
print("  rows 1,800 (= v21) = 1,123 IN-WHEEL + 677 EXCLUDED; 761 implemented rows / 761 keys; 362 not implemented")
print("  3 rows on their mod family with the family's text (bounds and the Restock! charge hold checked)")
print("  join: mod 709 entries / 761 keys = 761 implemented rows, 0 unmatched, 0 army_spec keys")
print("  Numbers: family block 1,123 / 761, exclusions 677, trigger table 49 families / 709 / 761")
print("  v1-v21: %d files byte-unchanged" % len(pre))
