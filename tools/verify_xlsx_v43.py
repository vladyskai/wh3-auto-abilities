#!/usr/bin/env python3
"""Verify docs/WH3_abilities_master_v43_2026-11-15.xlsx (round 157) from disk: the v38 verifier's structural checks
re-pointed at v43 with the round-157 counts (877 implemented, 822 entries, 82 families, the bombardment block at
row 128, 26 target-class rows, v1-v42 byte-unchanged), the round-156 rows still in place, plus the 12 round-157 rows
on their families with their texts."""
import os
import runpy
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openpyxl  # noqa: E402

T = os.path.dirname(os.path.abspath(__file__))
V38 = open(os.path.join(T, "verify_xlsx_v38.py"), encoding="utf-8").read()
R = [
    (r'docs\WH3_abilities_master_v38_2026-11-14.xlsx"', r'docs\WH3_abilities_master_v43_2026-11-15.xlsx"', 1),
    (r'PREV = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v37_2026-11-13.xlsx"',
     r'PREV = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v42_2026-11-15.xlsx"', 1),
    (r"backups\round150\pre_v38_workbook_md5.txt", r"backups\round157\pre_v43_workbook_md5.txt", 1),
    ('PACK_MD5 = "49a0903d999768b3b1123379db5a4268"', 'PACK_MD5 = "c387bc7df174378acbaaa443eabe9894"', 1),
    ('"A1: %d rows in v38, %d in v37"', '"A1: %d rows in v43, %d in v42"', 1),
    ("check(len(impl_rows) == 854 and len(impl_keys) == 854,", "check(len(impl_rows) == 877 and len(impl_keys) == 877,", 1),
    ('"; target class: " in str(r[21])) == 23, "B6: the target-class rows are not 23")',
     '"; target class: " in str(r[21])) == 26, "B6: the target-class rows are not 26")', 1),
    ("check(len(entries) == 799 and len(mod_keys) == 854,", "check(len(entries) == 822 and len(mod_keys) == 877,", 1),
    ("range(44, 119)", "range(44, 126)", 3),
    ('check(len(te) == 75 and all(isinstance(x, int) for x in te), "F1: trigger table is not 75 integer rows")',
     'check(len(te) == 82 and all(isinstance(x, int) for x in te), "F1: trigger table is not 82 integer rows")', 1),
    ("check(sum(te) == cell(119, 3) == 799 and sum(tk) == cell(119, 4) == 854,",
     "check(sum(te) == cell(126, 3) == 822 and sum(tk) == cell(126, 4) == 877,", 1),
    ('check(cell(121, 1) == "Bombardment set (COMPLETE - round 108)" and cell(123, 3) == 131, "F3: bombardment block not at row 121")',
     'check(cell(128, 1) == "Bombardment set (COMPLETE - round 108)" and cell(130, 3) == 131, "F3: bombardment block not at row 128")', 1),
    ('check(cell(13, 3) == 854 and cell(14, 3) == 269, "F6: Numbers headline moved")',
     'check(cell(13, 3) == 877 and cell(14, 3) == 246, "F6: Numbers headline moved")', 1),
    ('startswith("DEFINITIONS - WH3 ability master v38"), "G1: title")',
     'startswith("DEFINITIONS - WH3 ability master v43"), "G1: title")', 1),
    ('startswith("35. ROUND 150")', 'startswith("40. ROUND 157")', 1),
    ('"G2: section 35 missing"', '"G2: section 40 missing"', 1),
    ('== "v38" and PACK_MD5', '== "v43" and PACK_MD5', 1),
    ('"G3: changelog v38 row or pack md5 missing"', '"G3: changelog v43 row or pack md5 missing"', 1),
    ("check(len(pre) == 70 and not changed,", "check(len(pre) == 80 and not changed,", 1),
    ('print("XLSX v38 VERIFY: %d FAILURE(S)" % len(fails))', 'print("XLSX v43 VERIFY (structural checks): %d FAILURE(S)" % len(fails))', 1),
    ('print("XLSX v38 VERIFY OK")', 'print("XLSX v43 VERIFY (structural checks) OK")', 1),
    ('print("  1,800 rows = 1,123 + 677; 854 implemented; 27 skipped; 23 target-class rows")',
     'print("  1,800 rows = 1,123 + 677; 877 implemented; 27 skipped; 26 target-class rows")', 1),
    ('print("  join: 799 entries / 854 keys, every family matching; trigger table 75 families / 799 / 854;',
     'print("  join: 822 entries / 877 keys, every family matching; trigger table 82 families / 822 / 877;', 1),
    ('print("  v1-v37: %d files byte-unchanged" % len(pre))', 'print("  v1-v42: %d files byte-unchanged" % len(pre))', 1),
]
for a, b, n in R:
    assert V38.count(a) == n, (a[:70], V38.count(a))
    V38 = V38.replace(a, b)
tmp = os.path.join(T, "_verify_v43_base.py")
open(tmp, "w", encoding="utf-8", newline="\n").write(V38)
try:
    runpy.run_path(tmp, run_name="__main__")
except SystemExit as e:
    if e.code not in (None, 0):
        raise
finally:
    os.remove(tmp)

wb = openpyxl.load_workbook(r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v43_2026-11-15.xlsx", read_only=True)
ws = wb["Abilities"]
DR = "enemy_single_drain"
WANT = {"wh2_dlc09_spell_death_spirit_leech_bound": (DR, "charge hold 45 s (2 uses)"),
        "wh3_dlc25_spell_bound_spirit_leech": (DR, "within 70 m"),
        "wh3_dlc25_spell_bound_spirit_leech_gunnery_school": (DR, "in-flight hold 3 s"),
        "wh3_main_spell_bound_spirit_leech": (DR, "STANDING STILL"),
        "wh3_twa08_spell_bound_spirit_leech_great_unclean_one_ror": (DR, "no friendly-fire margin"),
        "wh2_main_item_abilities_the_liber_bubonicus": (DR, "charge hold 120 s (2 uses)"),
        "wh3_dlc25_item_abilities_deaths_timekeeper": (DR, "within 70 m"),
        "wh3_main_spell_bound_rancid_visitations": (DR, "in-flight hold 5 s"),
        "wh_dlc06_character_abilities_effagee_of_da_git": (DR, "within 70 m"),
        "wh3_dlc29_item_abilities_punch_dagger": (DR, "within 10 m"),
        "wh3_dlc24_lord_abilities_the_emperors_executioner": ("enemy_execute", "target class: Lord/Hero only"),
        "wh3_dlc24_lord_abilities_the_emperors_executioner_upgrade": ("enemy_execute", "execute line 33%")}
OLD = {"wh2_dlc10_item_bound_blast": "enemy_large_shot", "wh3_dlc26_character_abilities_dead_eye": "enemy_single_shot",
       "wh_dlc05_weapon_abilities_spear_of_kurnous": "enemy_melee_or_shooting"}
got = old = 0
for row in ws.iter_rows(min_row=2, values_only=True):
    k = str(row[2]).split(";")[0].strip()
    if k in WANT:
        fam, tok = WANT[k]
        good = (str(row[19]) == "IMPLEMENTED" and str(row[20]) == fam and str(row[21]).startswith(fam + ":")
                and tok in str(row[21]) and "\u2014" not in str(row[21]))
        got += 1 if good else 0
        if not good:
            print("  - round-157 row wrong:", k)
    if k in OLD and str(row[20]) == OLD[k] and str(row[21]).startswith(OLD[k] + ":"):
        old += 1
nums = wb["Numbers"]
fams = {str(nums.cell(row=r, column=2).value): nums.cell(row=r, column=3).value for r in range(44, 126)}
fam_ok = fams.get("enemy_single_drain") == 10 and fams.get("enemy_execute") == 2 and fams.get("enemy_large_shot") == 5
print("round-157 rows: %d / 12; round-156 rows kept: %d / 3; the new families in the trigger table: %s" % (got, old, fam_ok))
good_all = got == 12 and old == 3 and fam_ok
print("XLSX v43 VERIFY OK" if good_all else "XLSX v43 VERIFY: round-157 checks FAILED")
sys.exit(0 if good_all else 1)
