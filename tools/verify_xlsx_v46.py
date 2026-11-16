#!/usr/bin/env python3
"""Verify docs/WH3_abilities_master_v46_2026-11-16.xlsx (round 162) from disk: the v38 verifier's structural checks
re-pointed at v46 with the round-162 counts (949 implemented, 34 skipped, 892 entries, 90 families, the bombardment block
at row 136, 40 target-class rows, melee_unwavering 299, enemy_ground_melee 75, charge_or_melee 37, enemy_melee 35,
enemy_wavering 2, v1-v45 byte-unchanged), the earlier rounds' rows still in place, plus the 32 round-162 rows on their
families with their texts and the 2 rows the user closed."""
import os
import runpy
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openpyxl  # noqa: E402

T = os.path.dirname(os.path.abspath(__file__))
V38 = open(os.path.join(T, "verify_xlsx_v38.py"), encoding="utf-8").read()
R = [
    (r'docs\WH3_abilities_master_v38_2026-11-14.xlsx"', r'docs\WH3_abilities_master_v46_2026-11-16.xlsx"', 1),
    (r'PREV = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v37_2026-11-13.xlsx"',
     r'PREV = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v45_2026-11-15.xlsx"', 1),
    (r"backups\round150\pre_v38_workbook_md5.txt", r"backups\round162\pre_v46_workbook_md5.txt", 1),
    ('PACK_MD5 = "49a0903d999768b3b1123379db5a4268"', 'PACK_MD5 = "5792ffbeaa36c6110448037d38314a06"', 1),
    ('"A1: %d rows in v38, %d in v37"', '"A1: %d rows in v46, %d in v45"', 1),
    ("check(len(impl_rows) == 854 and len(impl_keys) == 854,", "check(len(impl_rows) == 949 and len(impl_keys) == 949,", 1),
    ('== "SKIPPED (user decision)") == 27, "B5: skipped count is not 27")',
     '== "SKIPPED (user decision)") == 34, "B5: skipped count is not 34")', 1),
    ('"; target class: " in str(r[21])) == 23, "B6: the target-class rows are not 23")',
     '"; target class: " in str(r[21])) == 40, "B6: the target-class rows are not 40")', 1),
    ("check(len(entries) == 799 and len(mod_keys) == 854,", "check(len(entries) == 892 and len(mod_keys) == 949,", 1),
    ("range(44, 119)", "range(44, 134)", 3),
    ('check(len(te) == 75 and all(isinstance(x, int) for x in te), "F1: trigger table is not 75 integer rows")',
     'check(len(te) == 90 and all(isinstance(x, int) for x in te), "F1: trigger table is not 90 integer rows")', 1),
    ("check(sum(te) == cell(119, 3) == 799 and sum(tk) == cell(119, 4) == 854,",
     "check(sum(te) == cell(134, 3) == 892 and sum(tk) == cell(134, 4) == 949,", 1),
    ('check(cell(121, 1) == "Bombardment set (COMPLETE - round 108)" and cell(123, 3) == 131, "F3: bombardment block not at row 121")',
     'check(cell(136, 1) == "Bombardment set (COMPLETE - round 108)" and cell(138, 3) == 131, "F3: bombardment block not at row 136")', 1),
    ('"melee_unwavering": 288', '"melee_unwavering": 299', 1),
    ('"enemy_ground_melee": 74', '"enemy_ground_melee": 75', 1),
    ('"charge_or_melee": 36', '"charge_or_melee": 37', 1),
    ('"enemy_melee": 34', '"enemy_melee": 35', 1),
    ('"enemy_wavering": 1', '"enemy_wavering": 2', 1),
    ('check(cell(13, 3) == 854 and cell(14, 3) == 269, "F6: Numbers headline moved")',
     'check(cell(13, 3) == 949 and cell(14, 3) == 174, "F6: Numbers headline moved")', 1),
    ('startswith("DEFINITIONS - WH3 ability master v38"), "G1: title")',
     'startswith("DEFINITIONS - WH3 ability master v46"), "G1: title")', 1),
    ('startswith("35. ROUND 150")', 'startswith("43. ROUND 162")', 1),
    ('"G2: section 35 missing"', '"G2: section 43 missing"', 1),
    ('== "v38" and PACK_MD5', '== "v46" and PACK_MD5', 1),
    ('"G3: changelog v38 row or pack md5 missing"', '"G3: changelog v46 row or pack md5 missing"', 1),
    ("check(len(pre) == 70 and not changed,", "check(len(pre) == 86 and not changed,", 1),
    ('print("XLSX v38 VERIFY: %d FAILURE(S)" % len(fails))', 'print("XLSX v46 VERIFY (structural checks): %d FAILURE(S)" % len(fails))', 1),
    ('print("XLSX v38 VERIFY OK")', 'print("XLSX v46 VERIFY (structural checks) OK")', 1),
    ('print("  1,800 rows = 1,123 + 677; 854 implemented; 27 skipped; 23 target-class rows")',
     'print("  1,800 rows = 1,123 + 677; 949 implemented; 34 skipped; 40 target-class rows")', 1),
    ('print("  join: 799 entries / 854 keys, every family matching; trigger table 75 families / 799 / 854;',
     'print("  join: 892 entries / 949 keys, every family matching; trigger table 90 families / 892 / 949;', 1),
    ('print("  v1-v37: %d files byte-unchanged" % len(pre))', 'print("  v1-v45: %d files byte-unchanged" % len(pre))', 1),
]
for a, b, n in R:
    assert V38.count(a) == n, (a[:70], V38.count(a))
    V38 = V38.replace(a, b)
tmp = os.path.join(T, "_verify_v46_base.py")
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
WW = GW.derive(KF)
assert len(KF) == 32
wb = openpyxl.load_workbook(r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v46_2026-11-16.xlsx", read_only=True)
ws = wb["Abilities"]
CLOSED = ("wh3_pro10_cataclysm_metal_gehennas_golden_globe_bound", "wh3_main_spell_bound_wall_of_wind_and_fire")
OLD = {"wh2_dlc10_item_bound_blast": "enemy_large_shot", "wh3_main_spell_bound_spirit_leech": "enemy_single_drain",
       "wh3_dlc24_lord_abilities_the_emperors_executioner": "enemy_execute",
       "wh3_dlc23_item_abilities_dweomer_leach_orb": "enemy_commander_value",
       "wh3_dlc27_item_abilities_staff_of_the_masque": "enemy_area_drain",
       "wh3_main_lord_abilities_burning_rage": "melee_clear"}
got = old = closed = 0
for row in ws.iter_rows(min_row=2, values_only=True):
    k = str(row[2]).split(";")[0].strip()
    if k in KF:
        fam = KF[k]
        kind, r, path, off, buf, allies, ground = WW[k]
        tok = ("widening to %g m at its end" % (r + buf + 10)) if fam == "enemy_wave" else (
            ("within %g m of the target" % (r + buf + 10)) if allies else "no friendly test")
        good = (str(row[19]) == "IMPLEMENTED" and str(row[20]) == fam and str(row[21]).startswith(fam + ":")
                and tok in str(row[21]) and "STANDING STILL" in str(row[21]) and "\u2014" not in str(row[21]))
        got += 1 if good else 0
        if not good:
            print("  - round-162 row wrong:", k, str(row[21])[:160])
    if k in CLOSED:
        good = (str(row[19]) == "SKIPPED (user decision)" and str(row[20]) == "-"
                and "Blob rule; close 2" in str(row[21]) and "Blob rule; close 2" in str(row[18]))
        closed += 1 if good else 0
        if not good:
            print("  - closed row wrong:", k)
    if k in OLD and str(row[20]) == OLD[k] and str(row[21]).startswith(OLD[k] + ":"):
        old += 1
nums = wb["Numbers"]
fams = {str(nums.cell(row=r, column=2).value): nums.cell(row=r, column=3).value for r in range(44, 134)}
fam_ok = (fams.get("enemy_wave") == 12 and fams.get("enemy_wander") == 20 and fams.get("melee_clear") == 5
          and fams.get("melee_unwavering") == 299 and fams.get("ally_melee_buff") == 14)
print("round-162 rows: %d / 32; closed rows: %d / 2; earlier rows kept: %d / 6; the families in the trigger table: %s"
      % (got, closed, old, fam_ok))
good_all = got == 32 and closed == 2 and old == 6 and fam_ok
print("XLSX v46 VERIFY OK" if good_all else "XLSX v46 VERIFY: round-162 checks FAILED")
sys.exit(0 if good_all else 1)
