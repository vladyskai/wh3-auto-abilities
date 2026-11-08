#!/usr/bin/env python3
"""Verify docs/WH3_abilities_master_v24_2026-11-08.xlsx from disk (no in-memory state).

  A. shape: 1,800 rows (= v23) = 1,123 IN-WHEEL + 677 EXCLUDED; 752 implemented rows / keys;
  B. the 13 retriggered rows: IMPLEMENTED, the family the mod gives their key, the family's text,
     and their earlier GATES clause kept;
  C. the patch-9.0.5 rows: Eternal Gaze 35 m, Aken-seth's 120 s hold, Okkam's Mindrazor without an
     in-flight hold, Overseer's flier note;
  D. no IN-WHEEL row carries an army_spec key;
  E. the join: mod 700 entries / 752 keys = the sheet's 752 implemented keys, every family matching;
  F. Numbers: the 54-family trigger table sums to 700 / 752; the bombardment block moved to row 100;
  G. Definitions v24 + section 21, Changelog v24 with the pack md5, v1-v23 byte-unchanged.
"""
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import gamedata_paths as GP
import collections
import hashlib
import os
import sys

import openpyxl

import build_ability_database as bd

XLSX = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v24_2026-11-08.xlsx"
PREV = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v23_2026-11-01.xlsx"
PRE_MD5 = r"C:\Users\vlady\Desktop\WH3_mod\docs\backups\round132\pre_v24_workbook_md5.txt"
PACK_MD5 = "47efd2465d26047dde59f0fed6d03e51"
MA, MS, SS = "melee_or_shooting_aura", "melee_or_shooting_self_or_ally", "self_shooting"
EXPECT = {k: MA for k in (
    "wh3_main_character_abilities_enchanted_metallurgy", "wh3_main_character_abilities_enchanted_metallurgy_flaming",
    "wh3_main_character_abilities_enchanted_metallurgy_piercing", "wh3_main_character_abilities_enchanted_metallurgy_poison",
    "wh3_main_lord_abilities_master_of_alchemy", "wh3_main_lord_abilities_master_of_alchemy_flaming",
    "wh3_main_lord_abilities_master_of_alchemy_piercing", "wh3_main_lord_abilities_master_of_alchemy_poison",
    "wh2_main_spell_bound_embers_of_the_phoenix", "wh2_main_item_abilities_dragonhorn")}
EXPECT["wh2_main_spell_bound_the_seerstaff_of_saphery"] = MS
EXPECT["wh3_main_spell_bound_harmonic_convergence"] = MS
EXPECT["wh_main_unit_abilities_boom"] = SS
KEEP_GATES = {"wh2_main_spell_bound_the_seerstaff_of_saphery": "charge hold 60 s (4 uses"}

fails = []


def check(cond, msg):
    if not cond:
        fails.append(msg)


army = set()
with open(GP.ARMY_SPEC, encoding="utf-8", errors="replace") as f:
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

prev = openpyxl.load_workbook(PREV, read_only=True)["Abilities"]
nprev = sum(1 for _ in prev.iter_rows(min_row=2, values_only=True))
check(N == nprev == 1800, "A1: %d rows in v24, %d in v23" % (N, nprev))
st = collections.Counter(str(r[17]) for r in rows)
check(st == {"IN-WHEEL": 1123, "EXCLUDED": 677}, "A2: status counts %s" % dict(st))
impl_rows = [r for r in rows if str(r[19]) == "IMPLEMENTED"]
impl_keys = set(k for r in impl_rows for k in ident(r))
check(len(impl_rows) == 752 and len(impl_keys) == 752, "A3: %d / %d implemented" % (len(impl_rows), len(impl_keys)))

entries, consts, tips = bd.mod_entries()
fam_by_key = {k: e["trigger"] for e in entries for k in e["keys"]}
for k, fam in EXPECT.items():
    r = by_key.get(k)
    check(r is not None and str(r[19]) == "IMPLEMENTED" and str(r[20]) == fam == fam_by_key.get(k)
          and str(r[21]).startswith(fam + ":"), "B1: `%s` is not on %s with its text" % (k, fam))
    if k in KEEP_GATES:
        check(KEEP_GATES[k] in str(r[21]), "B2: `%s` lost its GATES clause" % k)
check("bound: 24 m (70% of the ability's 35 m effect_range)" in str(by_key["wh3_main_character_abilities_enchanted_metallurgy"][21]),
      "B3: the aura text does not carry its 24 m bound")

t = str(by_key["wh3_dlc29_lord_abilities_gaze_of_usirian"][21])
check("bound: 35 m (70% of the ability's 50 m" in t and "bound: 70 m" not in t, "C1: Eternal Gaze text is not 35 m")
check("charge hold 120 s (3 uses" in str(by_key["wh3_dlc29_weapon_abilities_aken_seth_the_staff_of_pain"][21]),
      "C2: Aken-seth has no 120 s hold text")
t = str(by_key["wh3_dlc29_spell_bound_okkams_mindrazor"][21])
check("in-flight hold 3 s" not in t and "removed the 1 s wind-up" in t, "C3: Okkam's Mindrazor still shows the in-flight hold")
check("a flying ally is skipped" in str(by_key["wh3_dlc29_hero_active_overseer_of_the_unseen"][21]), "C4: Overseer flier note missing")

check(not [r[0] for r in rows if str(r[17]) == "IN-WHEEL" and any(k in army for k in ident(r))], "D1: army_spec key IN-WHEEL")

mod_keys = set(fam_by_key)
check(len(entries) == 700 and len(mod_keys) == 752, "E1: mod %d / %d" % (len(entries), len(mod_keys)))
check(impl_keys == mod_keys, "E2: implemented keys and mod keys differ")
bad = [ident(r)[0] for r in impl_rows if str(r[20]) != fam_by_key.get(ident(r)[0])]
check(not bad, "E3: %d implemented rows name a family the mod does not use for them: %s" % (len(bad), bad[:5]))

n = wb["Numbers"]
cell = lambda r, c: n.cell(row=r, column=c).value
te = [cell(r, 3) for r in range(44, 98)]
tk = [cell(r, 4) for r in range(44, 98)]
names = [str(cell(r, 2)) for r in range(44, 98)]
check(len(te) == 54 and all(isinstance(x, int) for x in te), "F1: trigger table is not 54 integer rows")
check(sum(te) == cell(98, 3) == 700 and sum(tk) == cell(98, 4) == 752, "F2: trigger table sums %s/%s" % (sum(te), sum(tk)))
check(cell(100, 1) == "Bombardment set (COMPLETE - round 108)" and cell(102, 3) == 131, "F3: bombardment block not at row 100")
for fam, cnt in {"melee_unwavering": 349, MA: 10, MS: 2, SS: 1, "allies_firing_aura": 8}.items():
    check(fam in names and te[names.index(fam)] == cnt, "F4: %s is not %d" % (fam, cnt))
check("metallurgy_melee" not in names, "F5: an empty family is listed in the trigger table")
check(cell(13, 3) == 752 and cell(14, 3) == 371, "F6: Numbers headline moved")

d = wb["Definitions"]
check(str(d.cell(row=1, column=1).value).startswith("DEFINITIONS - WH3 ability master v24"), "G1: title")
check(any(str(d.cell(row=r, column=1).value or "").startswith("21. ROUND 132") for r in range(1, d.max_row + 1)),
      "G2: section 21 missing")
ch = wb["Changelog"]
check(str(ch.cell(row=ch.max_row, column=2).value) == "v24" and PACK_MD5 in str(ch.cell(row=ch.max_row, column=3).value),
      "G3: changelog v24 row or pack md5 missing")
pre = {}
for line in open(PRE_MD5, encoding="utf-8"):
    h, p = line.strip().split(" ", 1)
    pre[p.lstrip("*")] = h
changed = [p for p, h in pre.items()
           if hashlib.md5(open(os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), p)), "rb").read()).hexdigest() != h]
check(len(pre) == 42 and not changed, "G4: older versions changed: %s (of %d)" % (changed, len(pre)))

if fails:
    print("XLSX v24 VERIFY: %d FAILURE(S)" % len(fails))
    for f in fails:
        print("  -", f)
    sys.exit(1)
print("XLSX v24 VERIFY OK")
print("  1,800 rows = 1,123 + 677; 752 implemented; 13 rows on their new families (gates kept); 4 patch rows corrected")
print("  join: 700 entries / 752 keys, every family matching; trigger table 54 families / 700 / 752")
print("  v1-v23: %d files byte-unchanged" % len(pre))
