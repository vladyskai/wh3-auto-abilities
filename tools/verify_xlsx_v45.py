#!/usr/bin/env python3
"""Verify docs/WH3_abilities_master_v45_2026-11-15.xlsx (round 159) from disk: the v38 verifier's structural checks
re-pointed at v45 with the round-159 counts (917 implemented, 32 skipped, 860 entries, 88 families, the bombardment block
at row 134, 30 target-class rows, melee_unwavering 299, enemy_ground_melee 75, charge_or_melee 37, enemy_melee 35,
enemy_wavering 2, v1-v44 byte-unchanged), the round-156/157/158 rows still in place, plus the 28 round-159 rows on their
families with their texts and the 5 rows the user closed."""
import os
import runpy
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openpyxl  # noqa: E402

T = os.path.dirname(os.path.abspath(__file__))
V38 = open(os.path.join(T, "verify_xlsx_v38.py"), encoding="utf-8").read()
R = [
    (r'docs\WH3_abilities_master_v38_2026-11-14.xlsx"', r'docs\WH3_abilities_master_v45_2026-11-15.xlsx"', 1),
    (r'PREV = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v37_2026-11-13.xlsx"',
     r'PREV = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v44_2026-11-15.xlsx"', 1),
    (r"backups\round150\pre_v38_workbook_md5.txt", r"backups\round159\pre_v45_workbook_md5.txt", 1),
    ('PACK_MD5 = "49a0903d999768b3b1123379db5a4268"', 'PACK_MD5 = "23b088aada7c4f68ab59601e6aabc1df"', 1),
    ('"A1: %d rows in v38, %d in v37"', '"A1: %d rows in v45, %d in v44"', 1),
    ("check(len(impl_rows) == 854 and len(impl_keys) == 854,", "check(len(impl_rows) == 917 and len(impl_keys) == 917,", 1),
    ('== "SKIPPED (user decision)") == 27, "B5: skipped count is not 27")',
     '== "SKIPPED (user decision)") == 32, "B5: skipped count is not 32")', 1),
    ('"; target class: " in str(r[21])) == 23, "B6: the target-class rows are not 23")',
     '"; target class: " in str(r[21])) == 30, "B6: the target-class rows are not 30")', 1),
    ("check(len(entries) == 799 and len(mod_keys) == 854,", "check(len(entries) == 860 and len(mod_keys) == 917,", 1),
    ("range(44, 119)", "range(44, 132)", 3),
    ('check(len(te) == 75 and all(isinstance(x, int) for x in te), "F1: trigger table is not 75 integer rows")',
     'check(len(te) == 88 and all(isinstance(x, int) for x in te), "F1: trigger table is not 88 integer rows")', 1),
    ("check(sum(te) == cell(119, 3) == 799 and sum(tk) == cell(119, 4) == 854,",
     "check(sum(te) == cell(132, 3) == 860 and sum(tk) == cell(132, 4) == 917,", 1),
    ('check(cell(121, 1) == "Bombardment set (COMPLETE - round 108)" and cell(123, 3) == 131, "F3: bombardment block not at row 121")',
     'check(cell(134, 1) == "Bombardment set (COMPLETE - round 108)" and cell(136, 3) == 131, "F3: bombardment block not at row 134")', 1),
    ('"melee_unwavering": 288', '"melee_unwavering": 299', 1),
    ('"enemy_ground_melee": 74', '"enemy_ground_melee": 75', 1),
    ('"charge_or_melee": 36', '"charge_or_melee": 37', 1),
    ('"enemy_melee": 34', '"enemy_melee": 35', 1),
    ('"enemy_wavering": 1', '"enemy_wavering": 2', 1),
    ('check(cell(13, 3) == 854 and cell(14, 3) == 269, "F6: Numbers headline moved")',
     'check(cell(13, 3) == 917 and cell(14, 3) == 206, "F6: Numbers headline moved")', 1),
    ('startswith("DEFINITIONS - WH3 ability master v38"), "G1: title")',
     'startswith("DEFINITIONS - WH3 ability master v45"), "G1: title")', 1),
    ('startswith("35. ROUND 150")', 'startswith("42. ROUND 159")', 1),
    ('"G2: section 35 missing"', '"G2: section 42 missing"', 1),
    ('== "v38" and PACK_MD5', '== "v45" and PACK_MD5', 1),
    ('"G3: changelog v38 row or pack md5 missing"', '"G3: changelog v45 row or pack md5 missing"', 1),
    ("check(len(pre) == 70 and not changed,", "check(len(pre) == 84 and not changed,", 1),
    ('print("XLSX v38 VERIFY: %d FAILURE(S)" % len(fails))', 'print("XLSX v45 VERIFY (structural checks): %d FAILURE(S)" % len(fails))', 1),
    ('print("XLSX v38 VERIFY OK")', 'print("XLSX v45 VERIFY (structural checks) OK")', 1),
    ('print("  1,800 rows = 1,123 + 677; 854 implemented; 27 skipped; 23 target-class rows")',
     'print("  1,800 rows = 1,123 + 677; 917 implemented; 32 skipped; 30 target-class rows")', 1),
    ('print("  join: 799 entries / 854 keys, every family matching; trigger table 75 families / 799 / 854;',
     'print("  join: 860 entries / 917 keys, every family matching; trigger table 88 families / 860 / 917;', 1),
    ('print("  v1-v37: %d files byte-unchanged" % len(pre))', 'print("  v1-v44: %d files byte-unchanged" % len(pre))', 1),
]
for a, b, n in R:
    assert V38.count(a) == n, (a[:70], V38.count(a))
    V38 = V38.replace(a, b)
tmp = os.path.join(T, "_verify_v45_base.py")
open(tmp, "w", encoding="utf-8", newline="\n").write(V38)
try:
    runpy.run_path(tmp, run_name="__main__")
except SystemExit as e:
    if e.code not in (None, 0):
        raise
finally:
    os.remove(tmp)

wb = openpyxl.load_workbook(r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v45_2026-11-15.xlsx", read_only=True)
ws = wb["Abilities"]
MU, MC, FD = "melee_unwavering", "melee_clear", "fly_dive"
WANT = {
    "wh2_dlc15_character_abilities_burp_of_grom_0": (MU, "25 m"), "wh2_dlc15_character_abilities_burp_of_grom_1": (MU, "25 m"),
    "wh2_dlc15_character_abilities_burp_of_grom_2": (MU, "25 m"), "wh2_dlc15_item_abilities_blood_forged_armour": (MU, "15 m"),
    "wh3_dlc23_item_abilities_daemon_flask_of_ashak": (MU, "Like Bloodstorm"),
    "wh3_dlc29_mount_abilities_feaster_of_souls": (MU, "charge hold 120 s (3 uses)"),
    "wh3_dlc27_item_abilities_spurting_bile_blood": (MU, "10 m"), "wh3_main_character_abilities_arsebelcher": (MU, "7 m"),
    "wh3_dlc20_unit_abilities_violent_wind": (MU, "7 m"), "wh3_dlc27_lord_abilities_whirlwind_of_pleasure": (MU, "6 m"),
    "wh2_dlc14_weapon_abilities_whirl_of_weeping_blades": (MU, "5 m"),
    "wh3_dlc25_character_abilities_hurricane_of_death": (MU, "5 m"), "wh3_dlc26_unit_abilities_acid_vomit": (MU, "5 m"),
    "wh3_main_character_abilities_groundbreaker": (MC, "within 20 m"), "wh3_main_lord_abilities_burning_rage": (MC, "within 25 m"),
    "wh2_dlc17_lord_abilities_bloodbeast": (MC, "within 25 m"), "wh2_dlc13_unit_abilities_emergency_vent": (MC, "within 25 m"),
    "wh3_dlc25_unit_abilities_marienburg_land_mines": (MC, "within 35 m"),
    "wh2_dlc15_unit_abilities_emberstorm": (FD, "within 7 m"), "wh3_dlc24_unit_abilities_moon_flare": (FD, "within 20 m"),
    "wh3_dlc26_unit_abilities_maneater_smoke_bomb": ("charge_or_melee", "+24 melee defence"),
    "wh2_main_character_abilities_verminous_valour": ("wavering_self", "+8 morale"),
    "wh3_main_unit_abilities_stun_bomb": ("enemy_ground_melee", "within 52 m"),
    "wh2_dlc15_character_abilities_slimy_smoothie": ("health_aura_ground", "within 24 m"),
    "wh2_dlc11_item_abilities_slann_gold": ("enemy_commander_value", "target class: Lord/Hero only"),
    "wh2_dlc14_lord_abilities_deathmasters_sigil": ("enemy_commander_value", "target class: Lord/Hero not flying"),
    "wh_dlc08_item_abilities_ancient_frost_wyrm_scale": ("enemy_blob_vortex", "within 21 m"),
    "wh3_main_unit_abilities_necrotic_explosion": ("last_stand_clear", "within 25 m"),
}
CLOSED = ("wh3_dlc29_lord_abilities_mist_form", "wh3_dlc29_lord_abilities_warp_step", "wh3_dlc27_unit_abilities_burrow",
          "wh2_main_weapon_abilities_sword_of_teclis", "wh2_dlc10_quest_abilities_unidentified_hydra_head")
OLD = {"wh2_dlc10_item_bound_blast": "enemy_large_shot", "wh3_main_spell_bound_spirit_leech": "enemy_single_drain",
       "wh3_dlc24_lord_abilities_the_emperors_executioner": "enemy_execute",
       "wh3_dlc23_item_abilities_dweomer_leach_orb": "enemy_commander_value",
       "wh3_dlc27_item_abilities_staff_of_the_masque": "enemy_area_drain"}
got = old = closed = 0
for row in ws.iter_rows(min_row=2, values_only=True):
    k = str(row[2]).split(";")[0].strip()
    if k in WANT:
        fam, tok = WANT[k]
        good = (str(row[19]) == "IMPLEMENTED" and str(row[20]) == fam and str(row[21]).startswith(fam + ":")
                and tok in str(row[21]) and "\u2014" not in str(row[21]))
        got += 1 if good else 0
        if not good:
            print("  - round-159 row wrong:", k, str(row[21])[:160])
    if k in CLOSED:
        good = (str(row[19]) == "SKIPPED (user decision)" and str(row[20]) == "-"
                and "Close 5, Necrotic last" in str(row[21]) and "Close 5, Necrotic last" in str(row[18]))
        closed += 1 if good else 0
        if not good:
            print("  - closed row wrong:", k)
    if k in OLD and str(row[20]) == OLD[k] and str(row[21]).startswith(OLD[k] + ":"):
        old += 1
nums = wb["Numbers"]
fams = {str(nums.cell(row=r, column=2).value): nums.cell(row=r, column=3).value for r in range(44, 132)}
fam_ok = (fams.get("melee_clear") == 5 and fams.get("fly_dive") == 2 and fams.get("last_stand_clear") == 1
          and fams.get("enemy_blob_vortex") == 1 and fams.get("enemy_commander_value") == 3
          and fams.get("melee_unwavering") == 299 and fams.get("enemy_area_drain") == 7)
print("round-159 rows: %d / 28; closed rows: %d / 5; earlier rows kept: %d / 5; the families in the trigger table: %s"
      % (got, closed, old, fam_ok))
good_all = got == 28 and closed == 5 and old == 5 and fam_ok
print("XLSX v45 VERIFY OK" if good_all else "XLSX v45 VERIFY: round-159 checks FAILED")
sys.exit(0 if good_all else 1)
