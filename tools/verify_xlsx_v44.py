#!/usr/bin/env python3
"""Verify docs/WH3_abilities_master_v44_2026-11-15.xlsx (round 158) from disk: the v38 verifier's structural checks
re-pointed at v44 with the round-158 counts (889 implemented, 834 entries, 84 families, the bombardment block at
row 130, 28 target-class rows, enemy_melee 35, enemy_wavering 2, v1-v43 byte-unchanged), the round-156/157 rows still
in place, plus the 12 round-158 rows on their families with their texts."""
import os
import runpy
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openpyxl  # noqa: E402

T = os.path.dirname(os.path.abspath(__file__))
V38 = open(os.path.join(T, "verify_xlsx_v38.py"), encoding="utf-8").read()
R = [
    (r'docs\WH3_abilities_master_v38_2026-11-14.xlsx"', r'docs\WH3_abilities_master_v44_2026-11-15.xlsx"', 1),
    (r'PREV = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v37_2026-11-13.xlsx"',
     r'PREV = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v43_2026-11-15.xlsx"', 1),
    (r"backups\round150\pre_v38_workbook_md5.txt", r"backups\round158\pre_v44_workbook_md5.txt", 1),
    ('PACK_MD5 = "49a0903d999768b3b1123379db5a4268"', 'PACK_MD5 = "326b37332e8f0b94bffeacea5fb6a966"', 1),
    ('"A1: %d rows in v38, %d in v37"', '"A1: %d rows in v44, %d in v43"', 1),
    ("check(len(impl_rows) == 854 and len(impl_keys) == 854,", "check(len(impl_rows) == 889 and len(impl_keys) == 889,", 1),
    ('"; target class: " in str(r[21])) == 23, "B6: the target-class rows are not 23")',
     '"; target class: " in str(r[21])) == 28, "B6: the target-class rows are not 28")', 1),
    ("check(len(entries) == 799 and len(mod_keys) == 854,", "check(len(entries) == 834 and len(mod_keys) == 889,", 1),
    ("range(44, 119)", "range(44, 128)", 3),
    ('check(len(te) == 75 and all(isinstance(x, int) for x in te), "F1: trigger table is not 75 integer rows")',
     'check(len(te) == 84 and all(isinstance(x, int) for x in te), "F1: trigger table is not 84 integer rows")', 1),
    ("check(sum(te) == cell(119, 3) == 799 and sum(tk) == cell(119, 4) == 854,",
     "check(sum(te) == cell(128, 3) == 834 and sum(tk) == cell(128, 4) == 889,", 1),
    ('check(cell(121, 1) == "Bombardment set (COMPLETE - round 108)" and cell(123, 3) == 131, "F3: bombardment block not at row 121")',
     'check(cell(130, 1) == "Bombardment set (COMPLETE - round 108)" and cell(132, 3) == 131, "F3: bombardment block not at row 130")', 1),
    ('"enemy_melee": 34', '"enemy_melee": 35', 1),
    ('"enemy_wavering": 1', '"enemy_wavering": 2', 1),
    ('check(cell(13, 3) == 854 and cell(14, 3) == 269, "F6: Numbers headline moved")',
     'check(cell(13, 3) == 889 and cell(14, 3) == 234, "F6: Numbers headline moved")', 1),
    ('startswith("DEFINITIONS - WH3 ability master v38"), "G1: title")',
     'startswith("DEFINITIONS - WH3 ability master v44"), "G1: title")', 1),
    ('startswith("35. ROUND 150")', 'startswith("41. ROUND 158")', 1),
    ('"G2: section 35 missing"', '"G2: section 41 missing"', 1),
    ('== "v38" and PACK_MD5', '== "v44" and PACK_MD5', 1),
    ('"G3: changelog v38 row or pack md5 missing"', '"G3: changelog v44 row or pack md5 missing"', 1),
    ("check(len(pre) == 70 and not changed,", "check(len(pre) == 82 and not changed,", 1),
    ('print("XLSX v38 VERIFY: %d FAILURE(S)" % len(fails))', 'print("XLSX v44 VERIFY (structural checks): %d FAILURE(S)" % len(fails))', 1),
    ('print("XLSX v38 VERIFY OK")', 'print("XLSX v44 VERIFY (structural checks) OK")', 1),
    ('print("  1,800 rows = 1,123 + 677; 854 implemented; 27 skipped; 23 target-class rows")',
     'print("  1,800 rows = 1,123 + 677; 889 implemented; 27 skipped; 28 target-class rows")', 1),
    ('print("  join: 799 entries / 854 keys, every family matching; trigger table 75 families / 799 / 854;',
     'print("  join: 834 entries / 889 keys, every family matching; trigger table 84 families / 834 / 889;', 1),
    ('print("  v1-v37: %d files byte-unchanged" % len(pre))', 'print("  v1-v43: %d files byte-unchanged" % len(pre))', 1),
]
for a, b, n in R:
    assert V38.count(a) == n, (a[:70], V38.count(a))
    V38 = V38.replace(a, b)
tmp = os.path.join(T, "_verify_v44_base.py")
open(tmp, "w", encoding="utf-8", newline="\n").write(V38)
try:
    runpy.run_path(tmp, run_name="__main__")
except SystemExit as e:
    if e.code not in (None, 0):
        raise
finally:
    os.remove(tmp)

wb = openpyxl.load_workbook(r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v44_2026-11-15.xlsx", read_only=True)
ws = wb["Abilities"]
AD = "enemy_area_drain"
WANT = {"wh2_main_item_abilities_blood_statuette_of_spite": (AD, "at least 25 soldiers"),
        "wh3_dlc23_item_abilities_darkened_mist": (AD, "within 21 m"),
        "wh3_dlc25_spell_bound_the_fate_of_bjuna": (AD, "in-flight hold 7 s"),
        "wh3_main_spell_bound_the_fate_of_bjuna": (AD, "STANDING STILL"),
        "wh3_dlc24_unit_abilities_maelstrom_of_change": (AD, "within 140 m"),
        "wh3_dlc29_lord_abilities_otherworldly_pestilence": (AD, "no friendly-fire margin"),
        "wh3_dlc27_item_abilities_staff_of_the_masque": (AD, "at least 15 soldiers"),
        "wh3_dlc29_item_active_ethracs_brazier": ("enemy_melee_or_fast", "rule 10"),
        "wh2_dlc11_lord_abilities_storm_of_the_night": ("enemy_melee_or_fast", "target class: flying only"),
        "wh3_dlc27_item_abilities_preyton_horns": ("enemy_melee", "-8 morale"),
        "wh2_dlc10_item_abilities_the_amber_trance": ("enemy_wavering", "is_wavering()"),
        "wh3_dlc23_item_abilities_dweomer_leach_orb": ("enemy_commander_value", "target class: Lord/Hero only")}
OLD = {"wh2_dlc10_item_bound_blast": "enemy_large_shot", "wh3_main_spell_bound_spirit_leech": "enemy_single_drain",
       "wh3_dlc24_lord_abilities_the_emperors_executioner": "enemy_execute"}
got = old = 0
for row in ws.iter_rows(min_row=2, values_only=True):
    k = str(row[2]).split(";")[0].strip()
    if k in WANT:
        fam, tok = WANT[k]
        good = (str(row[19]) == "IMPLEMENTED" and str(row[20]) == fam and str(row[21]).startswith(fam + ":")
                and tok in str(row[21]) and "\u2014" not in str(row[21]))
        got += 1 if good else 0
        if not good:
            print("  - round-158 row wrong:", k)
    if k in OLD and str(row[20]) == OLD[k] and str(row[21]).startswith(OLD[k] + ":"):
        old += 1
nums = wb["Numbers"]
fams = {str(nums.cell(row=r, column=2).value): nums.cell(row=r, column=3).value for r in range(44, 128)}
fam_ok = (fams.get("enemy_area_drain") == 7 and fams.get("enemy_commander_value") == 1
          and fams.get("enemy_melee_or_fast") == 4 and fams.get("enemy_single_drain") == 10)
print("round-158 rows: %d / 12; earlier rows kept: %d / 3; the families in the trigger table: %s" % (got, old, fam_ok))
good_all = got == 12 and old == 3 and fam_ok
print("XLSX v44 VERIFY OK" if good_all else "XLSX v44 VERIFY: round-158 checks FAILED")
sys.exit(0 if good_all else 1)
