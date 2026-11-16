#!/usr/bin/env python3
"""Verify docs/WH3_abilities_master_v47_2026-11-16.xlsx (round 163) from disk: the v38 verifier's structural checks
re-pointed at v47 with the round-163 counts (975 implemented, 36 skipped, 918 entries, 92 families, the bombardment block
at row 138, 44 target-class rows, melee_unwavering 299, enemy_ground_melee 75, charge_or_melee 37, enemy_melee 35,
enemy_wavering 2, v1-v46 byte-unchanged), the earlier rounds' rows still in place, plus the 26 round-163 rows on their
families with their texts and the 2 rows the user closed."""
import os
import runpy
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openpyxl  # noqa: E402

T = os.path.dirname(os.path.abspath(__file__))
V38 = open(os.path.join(T, "verify_xlsx_v38.py"), encoding="utf-8").read()
R = [
    (r'docs\WH3_abilities_master_v38_2026-11-14.xlsx"', r'docs\WH3_abilities_master_v47_2026-11-16.xlsx"', 1),
    (r'PREV = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v37_2026-11-13.xlsx"',
     r'PREV = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v46_2026-11-16.xlsx"', 1),
    (r"backups\round150\pre_v38_workbook_md5.txt", r"backups\round163\pre_v47_workbook_md5.txt", 1),
    ('PACK_MD5 = "49a0903d999768b3b1123379db5a4268"', 'PACK_MD5 = "66cb4f7ca1ddde52d5af56937ec740d4"', 1),
    ('"A1: %d rows in v38, %d in v37"', '"A1: %d rows in v47, %d in v46"', 1),
    ("check(len(impl_rows) == 854 and len(impl_keys) == 854,", "check(len(impl_rows) == 975 and len(impl_keys) == 975,", 1),
    ('== "SKIPPED (user decision)") == 27, "B5: skipped count is not 27")',
     '== "SKIPPED (user decision)") == 36, "B5: skipped count is not 36")', 1),
    ('"; target class: " in str(r[21])) == 23, "B6: the target-class rows are not 23")',
     '"; target class: " in str(r[21])) == 44, "B6: the target-class rows are not 44")', 1),
    ("check(len(entries) == 799 and len(mod_keys) == 854,", "check(len(entries) == 918 and len(mod_keys) == 975,", 1),
    ("range(44, 119)", "range(44, 136)", 3),
    ('check(len(te) == 75 and all(isinstance(x, int) for x in te), "F1: trigger table is not 75 integer rows")',
     'check(len(te) == 92 and all(isinstance(x, int) for x in te), "F1: trigger table is not 92 integer rows")', 1),
    ("check(sum(te) == cell(119, 3) == 799 and sum(tk) == cell(119, 4) == 854,",
     "check(sum(te) == cell(136, 3) == 918 and sum(tk) == cell(136, 4) == 975,", 1),
    ('check(cell(121, 1) == "Bombardment set (COMPLETE - round 108)" and cell(123, 3) == 131, "F3: bombardment block not at row 121")',
     'check(cell(138, 1) == "Bombardment set (COMPLETE - round 108)" and cell(140, 3) == 131, "F3: bombardment block not at row 138")', 1),
    ('"melee_unwavering": 288', '"melee_unwavering": 299', 1),
    ('"enemy_ground_melee": 74', '"enemy_ground_melee": 75', 1),
    ('"charge_or_melee": 36', '"charge_or_melee": 37', 1),
    ('"enemy_melee": 34', '"enemy_melee": 35', 1),
    ('"enemy_wavering": 1', '"enemy_wavering": 2', 1),
    ('"enemy_fast_near_ally": 8', '"enemy_fast_near_ally": 9', 1),
    ('check(cell(13, 3) == 854 and cell(14, 3) == 269, "F6: Numbers headline moved")',
     'check(cell(13, 3) == 975 and cell(14, 3) == 148, "F6: Numbers headline moved")', 1),
    ('startswith("DEFINITIONS - WH3 ability master v38"), "G1: title")',
     'startswith("DEFINITIONS - WH3 ability master v47"), "G1: title")', 1),
    ('startswith("35. ROUND 150")', 'startswith("44. ROUND 163")', 1),
    ('"G2: section 35 missing"', '"G2: section 44 missing"', 1),
    ('== "v38" and PACK_MD5', '== "v47" and PACK_MD5', 1),
    ('"G3: changelog v38 row or pack md5 missing"', '"G3: changelog v47 row or pack md5 missing"', 1),
    ("check(len(pre) == 70 and not changed,", "check(len(pre) == 88 and not changed,", 1),
    ('print("XLSX v38 VERIFY: %d FAILURE(S)" % len(fails))', 'print("XLSX v47 VERIFY (structural checks): %d FAILURE(S)" % len(fails))', 1),
    ('print("XLSX v38 VERIFY OK")', 'print("XLSX v47 VERIFY (structural checks) OK")', 1),
    ('print("  1,800 rows = 1,123 + 677; 854 implemented; 27 skipped; 23 target-class rows")',
     'print("  1,800 rows = 1,123 + 677; 975 implemented; 36 skipped; 44 target-class rows")', 1),
    ('print("  join: 799 entries / 854 keys, every family matching; trigger table 75 families / 799 / 854;',
     'print("  join: 918 entries / 975 keys, every family matching; trigger table 92 families / 918 / 975;', 1),
    ('print("  v1-v37: %d files byte-unchanged" % len(pre))', 'print("  v1-v46: %d files byte-unchanged" % len(pre))', 1),
]
for a, b, n in R:
    assert V38.count(a) == n, (a[:70], V38.count(a))
    V38 = V38.replace(a, b)
tmp = os.path.join(T, "_verify_v47_base.py")
open(tmp, "w", encoding="utf-8", newline="\n").write(V38)
try:
    runpy.run_path(tmp, run_name="__main__")
except SystemExit as e:
    if e.code not in (None, 0):
        raise
finally:
    os.remove(tmp)

import gen_ww_tables as GW  # noqa: E402
SRC_TXT = open(r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua",
               encoding="utf-8").read()
KF = GW.keys_in(SRC_TXT)   # the round's keys come from the MOD SOURCE, never from the workbook just written
WANT = {k: f for k, f in KF.items() if f in ("enemy_strike", "ally_blast")}
for k in """wh2_dlc16_item_abilities_acorns_of_the_oak_of_ages wh3_main_item_abilities_deaths_head
wh3_main_weapon_abilities_frost_fang wh3_dlc23_item_abilities_hammer_of_smednir wh_dlc03_spell_bound_viletide
wh3_main_item_abilities_crackleblaze wh3_dlc24_unit_abilities_lampreys_bite wh3_dlc26_lord_abilities_boiling_cauldron
wh3_dlc26_lord_abilities_simmering_pot wh2_dlc12_character_abilities_brass_orb
wh2_dlc12_character_abilities_brass_orb_tech_lab_doom_flayer wh2_dlc12_character_abilities_brass_orb_upgrade
wh3_dlc20_spell_bound_infernal_gateway wh3_dlc27_spell_bound_pit_of_shades wh3_main_spell_bound_pit_of_shades
wh_dlc05_spell_shadow_pit_of_shades_bound wh2_main_spell_bound_rubric_of_dark_dimensions wh3_dlc29_spell_bound_plague
wh3_dlc29_spell_bound_plaguemaster wh3_dlc29_lord_abilities_warp_junction wh3_pro10_cataclysm_fire_magma_storm_bound
wh_main_spell_bound_chain_lightning_ror""".split():
    assert KF.get(k) == "enemy_wander", k
    WANT[k] = "enemy_wander"
WANT["wh2_dlc16_character_abilities_befuddlement_of_mischiefs"] = "enemy_fast_near_ally"
WANT["wh2_main_weapon_bound_winged_staff"] = "enemy_area_drain"
assert len(WANT) == 26
TOK = {"enemy_wander": "STANDING STILL", "enemy_strike": "single-entity", "ally_blast": "Most enemies around",
       "enemy_fast_near_ally": "Any fast enemy", "enemy_area_drain": "Area drain rule"}
wb = openpyxl.load_workbook(r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v47_2026-11-16.xlsx", read_only=True)
ws = wb["Abilities"]
CLOSED = ("wh_main_rune_abilities_rune_of_wrath_and_ruin", "wh_dlc06_rune_abilities_master_rune_of_wrath_and_ruin")
OLD = {"wh2_dlc10_item_bound_blast": "enemy_large_shot", "wh3_main_lord_abilities_burning_rage": "melee_clear",
       "wh_dlc07_item_abilities_wrath_of_manann": "enemy_wave", "wh3_main_spell_bound_banishment": "enemy_wander",
       "wh3_dlc27_item_abilities_staff_of_the_masque": "enemy_area_drain"}
got = old = closed = 0
for row in ws.iter_rows(min_row=2, values_only=True):
    k = str(row[2]).split(";")[0].strip()
    if k in WANT:
        fam = WANT[k]
        good = (str(row[19]) == "IMPLEMENTED" and str(row[20]) == fam and str(row[21]).startswith(fam + ":")
                and TOK[fam] in str(row[21]) and "\u2014" not in str(row[21]))
        got += 1 if good else 0
        if not good:
            print("  - round-163 row wrong:", k, str(row[21])[:160])
    if k in CLOSED:
        good = (str(row[19]) == "SKIPPED (user decision)" and str(row[20]) == "-"
                and "Close the runes" in str(row[21]) and "Close the runes" in str(row[18]))
        closed += 1 if good else 0
        if not good:
            print("  - closed row wrong:", k)
    if k in OLD and str(row[20]) == OLD[k] and str(row[21]).startswith(OLD[k] + ":"):
        old += 1
nums = wb["Numbers"]
fams = {str(nums.cell(row=r, column=2).value): nums.cell(row=r, column=3).value for r in range(44, 136)}
fam_ok = (fams.get("enemy_wander") == 42 and fams.get("enemy_strike") == 1 and fams.get("ally_blast") == 1
          and fams.get("enemy_wave") == 12 and fams.get("enemy_area_drain") == 8 and fams.get("enemy_fast_near_ally") == 9)
print("round-163 rows: %d / 26; closed rows: %d / 2; earlier rows kept: %d / 5; the families in the trigger table: %s"
      % (got, closed, old, fam_ok))
good_all = got == 26 and closed == 2 and old == 5 and fam_ok
print("XLSX v47 VERIFY OK" if good_all else "XLSX v47 VERIFY: round-163 checks FAILED")
sys.exit(0 if good_all else 1)
