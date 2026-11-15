#!/usr/bin/env python3
"""Verify docs/WH3_abilities_master_v42_2026-11-15.xlsx (round 156) from disk: the v38 verifier's structural checks
re-pointed at v42 with the round-156 counts (865 implemented, 810 entries, 80 families, the bombardment block at
row 126, 25 target-class rows, v1-v41 byte-unchanged), plus the 11 magic-missile rows on their families with their
texts."""
import os
import runpy
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openpyxl  # noqa: E402
import gen_shot_tables as GS  # noqa: E402

T = os.path.dirname(os.path.abspath(__file__))
V38 = open(os.path.join(T, "verify_xlsx_v38.py"), encoding="utf-8").read()
R = [
    (r'docs\WH3_abilities_master_v38_2026-11-14.xlsx"', r'docs\WH3_abilities_master_v42_2026-11-15.xlsx"', 1),
    (r'PREV = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v37_2026-11-13.xlsx"',
     r'PREV = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v41_2026-11-15.xlsx"', 1),
    (r"backups\round150\pre_v38_workbook_md5.txt", r"backups\round156\pre_v42_workbook_md5.txt", 1),
    ('PACK_MD5 = "49a0903d999768b3b1123379db5a4268"', 'PACK_MD5 = "4075645f56fcec8c08d10d53106fcf00"', 1),
    ('"A1: %d rows in v38, %d in v37"', '"A1: %d rows in v42, %d in v41"', 1),
    ("check(len(impl_rows) == 854 and len(impl_keys) == 854,", "check(len(impl_rows) == 865 and len(impl_keys) == 865,", 1),
    ('"; target class: " in str(r[21])) == 23, "B6: the target-class rows are not 23")',
     '"; target class: " in str(r[21])) == 25, "B6: the target-class rows are not 25")', 1),
    ("check(len(entries) == 799 and len(mod_keys) == 854,", "check(len(entries) == 810 and len(mod_keys) == 865,", 1),
    ("range(44, 119)", "range(44, 124)", 3),
    ('check(len(te) == 75 and all(isinstance(x, int) for x in te), "F1: trigger table is not 75 integer rows")',
     'check(len(te) == 80 and all(isinstance(x, int) for x in te), "F1: trigger table is not 80 integer rows")', 1),
    ("check(sum(te) == cell(119, 3) == 799 and sum(tk) == cell(119, 4) == 854,",
     "check(sum(te) == cell(124, 3) == 810 and sum(tk) == cell(124, 4) == 865,", 1),
    ('check(cell(121, 1) == "Bombardment set (COMPLETE - round 108)" and cell(123, 3) == 131, "F3: bombardment block not at row 121")',
     'check(cell(126, 1) == "Bombardment set (COMPLETE - round 108)" and cell(128, 3) == 131, "F3: bombardment block not at row 126")', 1),
    ('check(cell(13, 3) == 854 and cell(14, 3) == 269, "F6: Numbers headline moved")',
     'check(cell(13, 3) == 865 and cell(14, 3) == 258, "F6: Numbers headline moved")', 1),
    ('startswith("DEFINITIONS - WH3 ability master v38"), "G1: title")',
     'startswith("DEFINITIONS - WH3 ability master v42"), "G1: title")', 1),
    ('startswith("35. ROUND 150")', 'startswith("39. ROUND 156")', 1),
    ('"G2: section 35 missing"', '"G2: section 39 missing"', 1),
    ('== "v38" and PACK_MD5', '== "v42" and PACK_MD5', 1),
    ('"G3: changelog v38 row or pack md5 missing"', '"G3: changelog v42 row or pack md5 missing"', 1),
    ("check(len(pre) == 70 and not changed,", "check(len(pre) == 78 and not changed,", 1),
    ('print("XLSX v38 VERIFY: %d FAILURE(S)" % len(fails))', 'print("XLSX v42 VERIFY (structural checks): %d FAILURE(S)" % len(fails))', 1),
    ('print("XLSX v38 VERIFY OK")', 'print("XLSX v42 VERIFY (structural checks) OK")', 1),
    ('print("  1,800 rows = 1,123 + 677; 854 implemented; 27 skipped; 23 target-class rows")',
     'print("  1,800 rows = 1,123 + 677; 865 implemented; 27 skipped; 25 target-class rows")', 1),
    ('print("  join: 799 entries / 854 keys, every family matching; trigger table 75 families / 799 / 854;',
     'print("  join: 810 entries / 865 keys, every family matching; trigger table 80 families / 810 / 865;', 1),
    ('print("  v1-v37: %d files byte-unchanged" % len(pre))', 'print("  v1-v41: %d files byte-unchanged" % len(pre))', 1),
]
for a, b, n in R:
    assert V38.count(a) == n, (a[:70], V38.count(a))
    V38 = V38.replace(a, b)
tmp = os.path.join(T, "_verify_v42_base.py")
open(tmp, "w", encoding="utf-8", newline="\n").write(V38)
try:
    runpy.run_path(tmp, run_name="__main__")
except SystemExit as e:
    if e.code not in (None, 0):
        raise
finally:
    os.remove(tmp)

wb = openpyxl.load_workbook(r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v42_2026-11-15.xlsx", read_only=True)
ws = wb["Abilities"]
src = open(r"C:/Users/vlady/Desktop/WH3_mod/mod_source/script/battle/mod/zz_test_deadly_onslaught.lua", encoding="utf-8").read()
keys = set(GS.keys_in(src))
WANT = {"wh2_dlc10_item_bound_blast": ("enemy_large_shot", "within 70 m"),
        "wh3_main_weapon_abilities_godkiller_pistol": ("enemy_large_shot", "charge hold 120 s (2 uses)"),
        "wh_dlc03_weapon_abilities_hunting_spear": ("enemy_large_shot", "within 140 m"),
        "wh2_dlc17_rune_abilities_master_rune_of_flight": ("enemy_large_shot", "min_range 5 m"),
        "wh3_dlc27_item_abilities_schalkains_teeth": ("enemy_large_shot", "charge hold 90 s (2 uses)"),
        "wh3_dlc26_character_abilities_dead_eye": ("enemy_single_shot", "target class: single entity only"),
        "wh2_dlc13_lord_abilities_kill_shot": ("enemy_single_shot", "a LARGE single-entity enemy first"),
        "wh3_main_character_abilities_crippling_throw": ("enemy_melee_or_fast", "within 84 m"),
        "wh2_dlc17_weapon_abilities_the_golden_blowpipe_of_ptoohee": ("enemy_melee_or_fast", "min_range 5 m"),
        "wh_dlc05_weapon_abilities_spear_of_kurnous": ("enemy_melee_or_shooting", "shooting and not in melee"),
        "wh3_main_weapon_abilities_nuku_chos_crossbow": ("enemy_infantry_shot", "within 175 m")}
ok = (keys == set(WANT))
got = 0
for row in ws.iter_rows(min_row=2, values_only=True):
    k = str(row[2]).split(";")[0].strip()
    if k in WANT:
        fam, tok = WANT[k]
        good = (str(row[19]) == "IMPLEMENTED" and str(row[20]) == fam and str(row[21]).startswith(fam + ":")
                and tok in str(row[21]) and "\u2014" not in str(row[21]))
        got += 1 if good else 0
        if not good:
            print("  - round-156 row wrong:", k)
nums = wb["Numbers"]
fams = {str(nums.cell(row=r, column=2).value): nums.cell(row=r, column=3).value for r in range(44, 124)}
fam_ok = (fams.get("enemy_large_shot") == 5 and fams.get("enemy_single_shot") == 2 and fams.get("enemy_infantry_shot") == 1
          and fams.get("enemy_melee_or_fast") == 2 and fams.get("enemy_melee_or_shooting") == 1)
print("round-156 rows: %d / 11 on their families with their texts; the 5 new families in the trigger table: %s"
      % (got, fam_ok))
good_all = ok and got == 11 and fam_ok
print("XLSX v42 VERIFY OK" if good_all else "XLSX v42 VERIFY: round-156 checks FAILED")
sys.exit(0 if good_all else 1)
