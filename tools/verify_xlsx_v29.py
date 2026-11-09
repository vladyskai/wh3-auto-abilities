#!/usr/bin/env python3
"""Verify docs/WH3_abilities_master_v26_2026-11-09.xlsx (round 134: the v25 checks plus the 12 speed rows and the 2 skipped Thunderburner rows) - formerly (round 133: the v24 checks plus the 7 under-fire rows) from disk (no in-memory state).

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

XLSX = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v29_2026-11-09.xlsx"
PREV = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v28_2026-11-09.xlsx"
PRE_MD5 = r"C:\Users\vlady\Desktop\WH3_mod\docs\backups\round137\pre_v29_workbook_md5.txt"
PACK_MD5 = "c719e140ddff4f0525889c1388bb3fd8"
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
EXPECT.update({"wh2_dlc12_unit_abilities_shield_of_chaqua": "under_fire", "wh3_dlc24_item_abilities_the_golden_eye_of_tzeentch": "under_fire", "wh_dlc07_lord_abilities_lions_shield": "under_fire", "wh3_dlc24_item_abilities_blessed_helm_of_the_oblast": "melee_or_under_fire", "wh2_main_item_abilities_the_bane_shield": "melee_or_under_fire", "wh_main_weapon_abilities_charmed_shield": "melee_or_under_fire", "wh3_twa08_unit_abilities_glacial_defence": "melee_or_under_fire"})
EXPECT.update({k: "charge_only" for k in ("wh_pro04_unit_abilities_apocalyptic_charge", "wh2_dlc16_item_abilities_twilight_horn_i", "wh_main_item_abilities_potion_of_speed", "wh_main_unit_abilities_blooood")})
EXPECT.update({k: "charge_or_melee" for k in ("wh_main_spell_bound_book_of_arkhan", "wh2_dlc17_rune_abilities_rune_of_speed", "wh2_dlc17_rune_abilities_master_rune_of_speed", "wh2_dlc11_lord_abilities_lightning_reflexes", "wh2_dlc12_lord_abilities_master_of_the_skies", "wh_main_item_abilities_pendant_of_slaanesh", "wh_main_hero_abilities_slippery", "wh2_dlc11_lord_abilities_transfix")})
SKIPPED134 = ("wh3_dlc25_unit_abilities_thunderburner", "wh3_dlc25_unit_abilities_thunderburner_upgraded")
EXPECT.update({k: "enemy_melee" for k in ("wh3_dlc27_spell_bound_acquiescence", "wh_dlc05_weapon_abilities_el_syf", "wh3_main_weapon_abilities_frost_shard_glaive", "wh3_cp1_lord_abilities_hidden_huntress", "wh2_dlc11_character_abilities_hornswaggle", "wh3_dlc26_unit_abilities_marked_for_eatin", "wh2_dlc11_character_abilities_taunt", "wh3_dlc25_hero_abilities_titan_headsman", "wh2_dlc15_lord_abilities_youre_next", "wh3_dlc29_hero_active_tendrils_of_the_sea")})
EXPECT.update({k: "enemy_fast_near_ally" for k in ("wh2_dlc15_hero_abilities_mither", "wh2_dlc17_rune_abilities_rune_of_slowness", "wh2_dlc17_rune_abilities_master_rune_of_slowness", "wh3_dlc29_hero_abilities_whispering_mist")})
EXPECT.update({k: "enemy_melee" for k in ("wh3_main_weapon_abilities_torment_blade", "wh3_main_lord_abilities_virulent_contagion", "wh3_main_lord_abilities_virulent_contagion_upgraded", "wh2_main_lord_abilities_trophy_heads", "wh3_dlc29_hero_active_dispatch_the_swarm_attack")})
EXPECT.update({k: "enemy_fast_near_ally" for k in ("wh3_main_lord_abilities_gaze_of_fate", "wh3_dlc23_lord_abilities_sadistic_snare", "wh2_dlc11_lord_abilities_spearfishers_net")})
EXPECT.update({k: "wavering_aura" for k in ("wh_main_character_abilities_rally", "wh2_main_mount_abilities_unholy_clamour", "wh2_dlc15_unit_abilities_mimic_cold_blooded")})
EXPECT.update({k: "wavering_ally_range" for k in ("wh_main_item_abilities_crown_of_command", "wh3_dlc24_character_abilities_tacticians_rally")})
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
check(N == nprev == 1800, "A1: %d rows in v29, %d in v28" % (N, nprev))
st = collections.Counter(str(r[17]) for r in rows)
check(st == {"IN-WHEEL": 1123, "EXCLUDED": 677}, "A2: status counts %s" % dict(st))
impl_rows = [r for r in rows if str(r[19]) == "IMPLEMENTED"]
impl_keys = set(k for r in impl_rows for k in ident(r))
check(len(impl_rows) == 750 and len(impl_keys) == 750, "A3: %d / %d implemented" % (len(impl_rows), len(impl_keys)))

entries, consts, tips = bd.mod_entries()
fam_by_key = {k: e["trigger"] for e in entries for k in e["keys"]}
for k, fam in EXPECT.items():
    r = by_key.get(k)
    check(r is not None and str(r[19]) == "IMPLEMENTED" and str(r[20]) == fam == fam_by_key.get(k)
          and str(r[21]).startswith(fam + ":"), "B1: `%s` is not on %s with its text" % (k, fam))
    if k in KEEP_GATES:
        check(KEEP_GATES[k] in str(r[21]), "B2: `%s` lost its GATES clause" % k)
check(all(str(by_key[k][19]) == "SKIPPED (user decision)" and str(by_key[k][20]) == "-" for k in SKIPPED134),
      "B4: the Thunderburner rows are not SKIPPED")
check(sum(1 for r in rows if str(r[19]) == "SKIPPED (user decision)") == 24, "B5: skipped count is not 24")
check(sum(1 for r in rows if "; target class: " in str(r[21])) == 18, "B6: the target-class rows are not 18")
check("target class: Lord/Hero only" in str(by_key["wh2_dlc14_lord_abilities_looming_dread"][21])
      and "target class: large single entity only" in str(by_key["wh3_dlc29_character_active_mark_of_the_monster"][21]),
      "B7: Looming Dread / Fecund Rebirth lack their class text")
check("fast_speed() (the live run speed, m/s) >= FOURTH.FAST_ENEMY_MPS = 5" in str(by_key["wh2_dlc15_hero_abilities_mither"][21])
      and "40 m" in str(by_key["wh2_dlc15_hero_abilities_mither"][21]), "B8: the fast-enemy text is wrong")
check("target class: not flying" in str(by_key["wh2_dlc11_lord_abilities_spearfishers_net"][21]), "B9: Spearfisher's Net lacks its not-flying class")
check(sum(1 for r in rows if str(r[20]) == "enemy_engaged_or_shot") == 52, "B10: enemy_engaged_or_shot rows are not 52 (47 entries; some span two rows)")
check("bound: 24 m (70% of the ability's 35 m effect_range)" in str(by_key["wh_main_character_abilities_rally"][21])
      and "whole army" in str(by_key["wh2_main_mount_abilities_unholy_clamour"][21])
      and "bound: 70 m (70% of the ability's 100 m ally cast reach)" in str(by_key["wh_main_item_abilities_crown_of_command"][21]),
      "B11: the morale bound texts are wrong")
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
check(len(entries) == 698 and len(mod_keys) == 750, "E1: mod %d / %d" % (len(entries), len(mod_keys)))
check(impl_keys == mod_keys, "E2: implemented keys and mod keys differ")
bad = [ident(r)[0] for r in impl_rows if str(r[20]) != fam_by_key.get(ident(r)[0])]
check(not bad, "E3: %d implemented rows name a family the mod does not use for them: %s" % (len(bad), bad[:5]))

n = wb["Numbers"]
cell = lambda r, c: n.cell(row=r, column=c).value
te = [cell(r, 3) for r in range(44, 102)]
tk = [cell(r, 4) for r in range(44, 102)]
names = [str(cell(r, 2)) for r in range(44, 102)]
check(len(te) == 58 and all(isinstance(x, int) for x in te), "F1: trigger table is not 58 integer rows")
check(sum(te) == cell(102, 3) == 698 and sum(tk) == cell(102, 4) == 750, "F2: trigger table sums %s/%s" % (sum(te), sum(tk)))
check(cell(104, 1) == "Bombardment set (COMPLETE - round 108)" and cell(106, 3) == 131, "F3: bombardment block not at row 104")
for fam, cnt in {"melee_unwavering": 314, "wavering_aura": 9, "wavering_ally_range": 6, MA: 10, MS: 2, SS: 1, "allies_firing_aura": 8, "under_fire": 3, "melee_or_under_fire": 4, "charge_only": 5, "charge_or_melee": 36, "enemy_engaged_or_shot": 47, "enemy_melee": 34, "enemy_fast_near_ally": 7}.items():
    check(fam in names and te[names.index(fam)] == cnt, "F4: %s is not %d" % (fam, cnt))
check("metallurgy_melee" not in names, "F5: an empty family is listed in the trigger table")
check(cell(13, 3) == 750 and cell(14, 3) == 373, "F6: Numbers headline moved")

d = wb["Definitions"]
check(str(d.cell(row=1, column=1).value).startswith("DEFINITIONS - WH3 ability master v29"), "G1: title")
check(any(str(d.cell(row=r, column=1).value or "").startswith("26. ROUND 137") for r in range(1, d.max_row + 1)),
      "G2: section 26 missing")
ch = wb["Changelog"]
check(str(ch.cell(row=ch.max_row, column=2).value) == "v29" and PACK_MD5 in str(ch.cell(row=ch.max_row, column=3).value),
      "G3: changelog v29 row or pack md5 missing")
pre = {}
for line in open(PRE_MD5, encoding="utf-8"):
    h, p = line.strip().split(" ", 1)
    pre[p.lstrip("*")] = h
changed = [p for p, h in pre.items()
           if hashlib.md5(open(os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), p)), "rb").read()).hexdigest() != h]
check(len(pre) == 52 and not changed, "G4: older versions changed: %s (of %d)" % (changed, len(pre)))

if fails:
    print("XLSX v29 VERIFY: %d FAILURE(S)" % len(fails))
    for f in fails:
        print("  -", f)
    sys.exit(1)
print("XLSX v29 VERIFY OK")
print("  1,800 rows = 1,123 + 677; 750 implemented; 24 skipped; 18 target-class rows")
print("  join: 698 entries / 750 keys, every family matching; trigger table 58 families / 698 / 750; 14 morale rows on their families")
print("  v1-v28: %d files byte-unchanged" % len(pre))
