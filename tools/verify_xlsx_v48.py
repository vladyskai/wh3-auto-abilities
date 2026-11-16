#!/usr/bin/env python3
"""Verify docs/WH3_abilities_master_v48_2026-11-16.xlsx (round 164) from disk: the v38 verifier's structural checks
re-pointed at v48 with the round-164 counts (1,003 implemented, 36 skipped, 946 entries, 95 families, the bombardment
block at row 141, 53 target-class rows, v1-v47 byte-unchanged), the earlier rounds' rows still in place, the 28
round-164 rows on their families with their texts, and the 12 round-162 waves reworded (the caster does not count)."""
import os
import runpy
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openpyxl  # noqa: E402

T = os.path.dirname(os.path.abspath(__file__))
V38 = open(os.path.join(T, "verify_xlsx_v38.py"), encoding="utf-8").read()
R = [
    (r'docs\WH3_abilities_master_v38_2026-11-14.xlsx"', r'docs\WH3_abilities_master_v48_2026-11-16.xlsx"', 1),
    (r'PREV = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v37_2026-11-13.xlsx"',
     r'PREV = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v47_2026-11-16.xlsx"', 1),
    (r"backups\round150\pre_v38_workbook_md5.txt", r"backups\round164\pre_v48_workbook_md5.txt", 1),
    ('PACK_MD5 = "49a0903d999768b3b1123379db5a4268"', 'PACK_MD5 = "b4ff0c03c8246166b426bb881c2012aa"', 1),
    ('"A1: %d rows in v38, %d in v37"', '"A1: %d rows in v48, %d in v47"', 1),
    ("check(len(impl_rows) == 854 and len(impl_keys) == 854,", "check(len(impl_rows) == 1003 and len(impl_keys) == 1003,", 1),
    ('== "SKIPPED (user decision)") == 27, "B5: skipped count is not 27")',
     '== "SKIPPED (user decision)") == 36, "B5: skipped count is not 36")', 1),
    ('"; target class: " in str(r[21])) == 23, "B6: the target-class rows are not 23")',
     '"; target class: " in str(r[21])) == 53, "B6: the target-class rows are not 53")', 1),
    ("check(len(entries) == 799 and len(mod_keys) == 854,", "check(len(entries) == 946 and len(mod_keys) == 1003,", 1),
    ("range(44, 119)", "range(44, 139)", 3),
    ('check(len(te) == 75 and all(isinstance(x, int) for x in te), "F1: trigger table is not 75 integer rows")',
     'check(len(te) == 95 and all(isinstance(x, int) for x in te), "F1: trigger table is not 95 integer rows")', 1),
    ("check(sum(te) == cell(119, 3) == 799 and sum(tk) == cell(119, 4) == 854,",
     "check(sum(te) == cell(139, 3) == 946 and sum(tk) == cell(139, 4) == 1003,", 1),
    ('check(cell(121, 1) == "Bombardment set (COMPLETE - round 108)" and cell(123, 3) == 131, "F3: bombardment block not at row 121")',
     'check(cell(141, 1) == "Bombardment set (COMPLETE - round 108)" and cell(143, 3) == 131, "F3: bombardment block not at row 141")', 1),
    ('"melee_unwavering": 288', '"melee_unwavering": 299', 1),
    ('"enemy_ground_melee": 74', '"enemy_ground_melee": 75', 1),
    ('"charge_or_melee": 36', '"charge_or_melee": 37', 1),
    ('"enemy_melee": 34', '"enemy_melee": 35', 1),
    ('"enemy_wavering": 1', '"enemy_wavering": 2', 1),
    ('"enemy_fast_near_ally": 8', '"enemy_fast_near_ally": 9', 1),
    ('check(cell(13, 3) == 854 and cell(14, 3) == 269, "F6: Numbers headline moved")',
     'check(cell(13, 3) == 1003 and cell(14, 3) == 120, "F6: Numbers headline moved")', 1),
    ('startswith("DEFINITIONS - WH3 ability master v38"), "G1: title")',
     'startswith("DEFINITIONS - WH3 ability master v48"), "G1: title")', 1),
    ('startswith("35. ROUND 150")', 'startswith("45. ROUND 164")', 1),
    ('"G2: section 35 missing"', '"G2: section 45 missing"', 1),
    ('== "v38" and PACK_MD5', '== "v48" and PACK_MD5', 1),
    ('"G3: changelog v38 row or pack md5 missing"', '"G3: changelog v48 row or pack md5 missing"', 1),
    ("check(len(pre) == 70 and not changed,", "check(len(pre) == 90 and not changed,", 1),
    ('print("XLSX v38 VERIFY: %d FAILURE(S)" % len(fails))', 'print("XLSX v48 VERIFY (structural checks): %d FAILURE(S)" % len(fails))', 1),
    ('print("XLSX v38 VERIFY OK")', 'print("XLSX v48 VERIFY (structural checks) OK")', 1),
    ('print("  1,800 rows = 1,123 + 677; 854 implemented; 27 skipped; 23 target-class rows")',
     'print("  1,800 rows = 1,123 + 677; 1003 implemented; 36 skipped; 53 target-class rows")', 1),
    ('print("  join: 799 entries / 854 keys, every family matching; trigger table 75 families / 799 / 854;',
     'print("  join: 946 entries / 1003 keys, every family matching; trigger table 95 families / 946 / 1003;', 1),
    ('print("  v1-v37: %d files byte-unchanged" % len(pre))', 'print("  v1-v47: %d files byte-unchanged" % len(pre))', 1),
]
for a, b, n in R:
    assert V38.count(a) == n, (a[:70], V38.count(a))
    V38 = V38.replace(a, b)
tmp = os.path.join(T, "_verify_v48_base.py")
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
NEW_FAMS = {"enemy_wave_charge", "enemy_cone", "enemy_sweep"}
WANT = {k: f for k, f in KF.items() if f in NEW_FAMS}
WANT["wh2_dlc15_lord_abilities_da_boss_loons"] = "enemy_wander"
for k in """wh3_main_item_abilities_bangstick wh2_main_item_abilities_black_dragon_egg wh3_main_daemon_arms_abilities_blue_fire
wh3_main_daemon_arms_abilities_blue_fire_upgraded wh_main_item_abilities_fiery_ring_of_thori
wh2_main_lord_abilities_gaze_of_malice wh3_dlc24_unit_abilities_jade_dragons_breath wh3_main_item_abilities_kovsh_breath
wh3_dlc27_spell_bound_lash_of_slaanesh wh3_main_spell_bound_lash_of_slaanesh
wh3_main_spell_bound_lash_of_slaanesh_keeper_of_secrets wh3_dlc20_spell_bound_pink_fire_of_tzeentch
wh3_main_spell_tzeentch_pink_fire_of_tzeentch_bound wh2_main_mount_bound_scorch wh3_dlc20_spell_bound_stream_of_corruption
wh3_main_spell_nurgle_stream_of_corruption_bound wh2_main_weapon_abilities_sunfang
wh3_dlc20_weapon_abilities_the_spear_slaupnir""".split():
    assert KF.get(k) == "enemy_wave", k
    WANT[k] = "enemy_wave"
assert len(WANT) == 28
TOK = {"enemy_wave": "Wave rule", "enemy_wave_charge": "Charge, clear path", "enemy_cone": "Clear cone, most value",
       "enemy_sweep": "Sweeps clear", "enemy_wander": "Loons as wanderer"}
wb = openpyxl.load_workbook(r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v48_2026-11-16.xlsx", read_only=True)
ws = wb["Abilities"]
got = waves162 = stale = 0
for row in ws.iter_rows(min_row=2, values_only=True):
    k = str(row[2]).split(";")[0].strip()
    t = str(row[21])
    if k in WANT:
        fam = WANT[k]
        good = (str(row[19]) == "IMPLEMENTED" and str(row[20]) == fam and t.startswith(fam + ":") and TOK[fam] in t
                and "\u2014" not in t)
        got += 1 if good else 0
        if not good:
            print("  - round-164 row wrong:", k, t[:160])
    elif str(row[20]) == "enemy_wave" and "the caster's own wave does not count: round 164" in t:
        waves162 += 1
    if str(row[20]) == "enemy_wave" and "the caster counting" in t:   # other families use the phrase legitimately
        stale += 1
nums = wb["Numbers"]
fams = {str(nums.cell(row=r, column=2).value): nums.cell(row=r, column=3).value for r in range(44, 139)}
fam_ok = (fams.get("enemy_wave") == 30 and fams.get("enemy_wave_charge") == 2 and fams.get("enemy_cone") == 5
          and fams.get("enemy_sweep") == 2 and fams.get("enemy_wander") == 43 and fams.get("enemy_strike") == 1)
print("round-164 rows: %d / 28; round-162 waves reworded: %d / 12; stale 'caster counting' texts: %d; families: %s"
      % (got, waves162, stale, fam_ok))
good_all = got == 28 and waves162 == 12 and stale == 0 and fam_ok
print("XLSX v48 VERIFY OK" if good_all else "XLSX v48 VERIFY: round-164 checks FAILED")
sys.exit(0 if good_all else 1)
