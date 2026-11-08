#!/usr/bin/env python3
"""Verify docs/WH3_abilities_master_v21_2026-10-28.xlsx from disk (no in-memory state).

  A. shape and counts: 1,800 = 1,123 + 677; 759 implemented rows / keys; same
     data-row count as v20;
  B. the 21 rows: IMPLEMENTED, the trigger family the mod gives their key, and
     the trigger text of that family (enemy_melee rows: the melee-only text with
     their own bound; the two 3-use hexes: their charge hold);
  C. Daemonic Possession SKIPPED (user decision), and in no mod entry;
  D. the gates: no IN-WHEEL row carries an army_spec key; reasons well-formed;
  E. the join: mod 707 entries / 759 keys <-> sheet 759 implemented keys;
  F. Numbers: every block re-derived and tying, 46-family trigger table;
  G. bookkeeping: autofilter, Definitions v21 + section 18, Changelog v21 with
     the pack md5; and v1-v20 byte-unchanged against the pre-build hash list.
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

XLSX = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v21_2026-10-28.xlsx"
V20 = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v20_2026-10-20.xlsx"
ARMY_SPEC = GP.ARMY_SPEC
PRE_MD5 = r"C:\Users\vlady\Desktop\WH3_mod\docs\backups\signoff_v21\pre_v21_workbook_md5.txt"
PACK_MD5 = "88890ada80776c18ba5e142eeb3d9ced"

MU, CM, EM, EG = "melee_unwavering", "charge_or_melee", "enemy_melee", "enemy_engaged_or_shot"
EXPECT = {
    "wh3_main_daemon_head_abilities_call_for_power": MU, "wh3_main_weapon_abilities_ursuns_claws": MU,
    "wh3_dlc23_weapon_abilities_black_hammer_of_hashut": MU, "wh3_dlc23_weapon_abilities_the_graven_sceptre": MU,
    "wh3_cp1_weapon_abilities_tyrants_talon": MU, "wh3_dlc29_item_abilities_crimson_blade": MU,
    "wh2_dlc14_lord_abilities_bloodstorm": MU, "wh3_dlc23_hero_abilities_crooked_dice": MU,
    "wh3_dlc20_lord_abilities_temptator": MU, "wh3_dlc27_unit_abilities_consuming_hatred": MU,
    "wh2_main_item_abilities_rival_hide_talisman": MU, "wh3_main_lord_abilities_seductive_glory": MU,
    "wh2_dlc15_item_abilities_vine_dragon_scale": MU, "wh3_dlc23_weapon_abilities_dark_mace": MU,
    "wh2_dlc11_lord_abilities_seduction": CM, "wh2_dlc11_lord_abilities_song_of_enthrallment": CM,
    "wh_dlc06_unit_abilities_smoke_bomb": CM,
    "wh3_main_character_abilities_no_escape": EM, "wh3_dlc29_lord_abilities_transfix": EM,
    "wh_pro01_lord_abilities_flash_bomb": EM,
    "wh2_dlc17_character_abilities_hunter_of_champions_upgraded": EG,
}
BOUNDS = {"wh3_main_character_abilities_no_escape": "bound: 70 m (70% of the ability's 100 m",
          "wh3_dlc29_lord_abilities_transfix": "bound: 70 m (70% of the ability's 100 m",
          "wh_pro01_lord_abilities_flash_bomb": "bound: 52 m (70% of the ability's 75 m",
          "wh2_dlc17_character_abilities_hunter_of_champions_upgraded": "bound: 70 m (70% of the ability's 100 m"}
HOLDS = {"wh3_main_character_abilities_no_escape": "charge hold 90 s (3 uses",
         "wh3_dlc29_lord_abilities_transfix": "charge hold 120 s (3 uses"}
DP = "wh3_main_lord_abilities_daemonic_possession"

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
v20 = openpyxl.load_workbook(V20, read_only=True)["Abilities"]
n20 = sum(1 for _ in v20.iter_rows(min_row=2, values_only=True))
check(N == n20 == 1800, "A1: %d rows in v21, %d in v20, expected 1,800 both" % (N, n20))
check([r[0] for r in rows] == list(range(1, N + 1)), "A2: Item # is not 1..1800 in order")
st = collections.Counter(str(r[17]) for r in rows)
check(st == {"IN-WHEEL": 1123, "EXCLUDED": 677}, "A3: status counts %s" % dict(st))
impl_rows = [r for r in rows if str(r[19]) == "IMPLEMENTED"]
impl_keys = set(k for r in impl_rows for k in ident(r))
check(len(impl_rows) == 759 and len(impl_keys) == 759, "A4: %d implemented rows / %d keys, expected 759 / 759"
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
    if fam == EM:
        check("the under-missile-fire arm is OFF" in str(r[21]) and "still in melee and still within the bound"
              in str(r[21]), "B4: `%s` enemy_melee text is not the melee-only rule" % k)
    if k in BOUNDS:
        check(BOUNDS[k] in str(r[21]), "B5: `%s` trigger text does not carry its bound" % k)
    if k in HOLDS:
        check(HOLDS[k] in str(r[21]), "B6: `%s` trigger text does not carry its charge hold" % k)

# C
r = by_key[DP]
check(str(r[19]) == "SKIPPED (user decision)" and str(r[18]).startswith("skipped (user decision 2026-10-27"),
      "C1: Daemonic Possession reads %s / %s" % (r[19], str(r[18])[:60]))
check(DP not in fam_by_key, "C2: Daemonic Possession is in the mod")

# D
check(not [r[0] for r in rows if str(r[17]) == "IN-WHEEL" and any(k in army for k in ident(r))],
      "D1: an IN-WHEEL row carries an army_spec key")
for r in rows:
    if str(r[17]) == "IN-WHEEL":
        check(str(r[18]).startswith(("carrier family:", "skipped ")),
              "D2: IN-WHEEL row %s has an unexplained reason: %s" % (r[0], str(r[18])[:80]))

# E
mod_keys = set(fam_by_key)
check(len(entries) == 707 and len(mod_keys) == 759, "E1: mod %d entries / %d keys, expected 707 / 759"
      % (len(entries), len(mod_keys)))
check(not (mod_keys & army), "E2: army_spec keys in the mod")
check(impl_keys == mod_keys, "E3: rows-only %s, mod-only %s"
      % (sorted(impl_keys - mod_keys)[:5], sorted(mod_keys - impl_keys)[:5]))

# F
n = wb["Numbers"]
cell = lambda r, c: n.cell(row=r, column=c).value
for (r, want, lbl) in ((10, 1800, "inventory"), (11, 677, "excluded"), (12, 1123, "included"),
                       (13, 759, "implemented"), (14, 364, "not-implemented-included"), (16, 759, "all implemented")):
    check(cell(r, 3) == want, "F1: Numbers %s cell %s, expected %s" % (lbl, cell(r, 3), want))
check(cell(13, 3) + cell(14, 3) == cell(12, 3), "F2: implemented + not != included")
check(sum(cell(r, 3) for r in range(20, 28)) == cell(28, 3) == 1123, "F3: family block included does not tie")
check(sum(cell(r, 4) for r in range(20, 28)) == cell(28, 4) == 759, "F4: family block implemented does not tie")
check(sum(cell(r, 3) for r in range(32, 38)) == cell(38, 3) == 677, "F5: exclusion block does not tie")
te = [cell(r, 3) for r in range(44, 90)]
tk = [cell(r, 4) for r in range(44, 90)]
names = [str(cell(r, 2)) for r in range(44, 90)]
check(len(te) == 46 and all(isinstance(x, int) for x in te), "F6: trigger table is not 46 integer rows")
check(sum(te) == cell(90, 3) == 707 and sum(tk) == cell(90, 4) == 759, "F7: trigger table sums %s/%s vs %s/%s"
      % (sum(te), sum(tk), cell(90, 3), cell(90, 4)))
want_counts = {MU: 374, CM: 28, EM: 3, EG: 85}
for fam, cnt in want_counts.items():
    check(fam in names and te[names.index(fam)] == cnt, "F8: %s is not %d entries in the trigger table" % (fam, cnt))
check("v21" in str(cell(7, 1)) and "759" in str(cell(7, 1)), "F9: the date line is not the v21 line")

# G
check(ws.auto_filter.ref == "A1:W%d" % ws.max_row, "G1: autofilter %s" % ws.auto_filter.ref)
d = wb["Definitions"]
check(str(d.cell(row=1, column=1).value).startswith("DEFINITIONS - WH3 ability master v21"), "G2: title not v21")
check(any(str(d.cell(row=r, column=1).value or "").startswith("18. ROUNDS 122 AND 123")
          for r in range(1, d.max_row + 1)), "G3: Definitions section 18 missing")
ch = wb["Changelog"]
last = str(ch.cell(row=ch.max_row, column=3).value)
check(str(ch.cell(row=ch.max_row, column=2).value) == "v21", "G4: last changelog row is not v21")
check(PACK_MD5 in last and "PENDING" not in last, "G5: the v21 changelog does not carry the pack md5")
pre = {}
for line in open(PRE_MD5, encoding="utf-8"):
    h, p = line.strip().split(" ", 1)
    pre[p.lstrip("*")] = h
changed = []
for p, h in pre.items():
    full = os.path.normpath(os.path.join(r"C:\Users\vlady\Desktop\WH3_mod\tools", p))
    if hashlib.md5(open(full, "rb").read()).hexdigest() != h:
        changed.append(p)
check(len(pre) == 36 and not changed, "G6: older workbook versions changed: %s (of %d hashed)" % (changed, len(pre)))

if fails:
    print("XLSX v21 VERIFY: %d FAILURE(S)" % len(fails))
    for f in fails:
        print("  -", f)
    sys.exit(1)
print("XLSX v21 VERIFY OK")
print("  rows 1,800 (= v20) = 1,123 IN-WHEEL + 677 EXCLUDED; 759 implemented rows / 759 keys; 364 not implemented")
print("  21 rows on their mod family with the family's text (bounds and charge holds checked); Daemonic Possession SKIPPED")
print("  join: mod 707 entries / 759 keys = 759 implemented rows, 0 unmatched, 0 army_spec keys")
print("  Numbers: family block 1,123 / 759, exclusions 677, trigger table 46 families / 707 / 759")
print("  v1-v20: %d files byte-unchanged" % len(pre))
