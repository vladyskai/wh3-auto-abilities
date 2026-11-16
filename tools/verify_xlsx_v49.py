#!/usr/bin/env python3
"""Verify docs/WH3_abilities_master_v49_2026-11-17.xlsx (round 165) from disk: the v38 verifier's structural checks
re-pointed at v49 (the round-164 counts are unchanged: 1,003 implemented, 36 skipped, 946 entries, 95 families, the
bombardment block at row 141, 53 target-class rows; v1-v48 byte-unchanged, 92 files), then the round-165 checks: the
Cards sheet holds 946 rows equal to the harness-164 CARD lines, every card whole (no token, no bracket, no em dash),
and the 22 changed keys carry their round-165 note."""
import os
import runpy
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openpyxl  # noqa: E402

T = os.path.dirname(os.path.abspath(__file__))
V38 = open(os.path.join(T, "verify_xlsx_v38.py"), encoding="utf-8").read()
R = [
    (r'docs\WH3_abilities_master_v38_2026-11-14.xlsx"', r'docs\WH3_abilities_master_v49_2026-11-17.xlsx"', 1),
    (r'PREV = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v37_2026-11-13.xlsx"',
     r'PREV = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v48_2026-11-16.xlsx"', 1),
    (r"backups\round150\pre_v38_workbook_md5.txt", r"backups\round165\pre_v49_workbook_md5.txt", 1),
    ('PACK_MD5 = "49a0903d999768b3b1123379db5a4268"', 'PACK_MD5 = "df53a1b19192d4afecf132049cecb6e0"', 1),
    ('"A1: %d rows in v38, %d in v37"', '"A1: %d rows in v49, %d in v48"', 1),
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
     'startswith("DEFINITIONS - WH3 ability master v49"), "G1: title")', 1),
    ('startswith("35. ROUND 150")', 'startswith("46. ROUND 165")', 1),
    ('"G2: section 35 missing"', '"G2: section 46 missing"', 1),
    ('== "v38" and PACK_MD5', '== "v49" and PACK_MD5', 1),
    ('"G3: changelog v38 row or pack md5 missing"', '"G3: changelog v49 row or pack md5 missing"', 1),
    ("check(len(pre) == 70 and not changed,", "check(len(pre) == 92 and not changed,", 1),
    ('print("XLSX v38 VERIFY: %d FAILURE(S)" % len(fails))', 'print("XLSX v49 VERIFY (structural checks): %d FAILURE(S)" % len(fails))', 1),
    ('print("XLSX v38 VERIFY OK")', 'print("XLSX v49 VERIFY (structural checks) OK")', 1),
    ('print("  1,800 rows = 1,123 + 677; 854 implemented; 27 skipped; 23 target-class rows")',
     'print("  1,800 rows = 1,123 + 677; 1003 implemented; 36 skipped; 53 target-class rows")', 1),
    ('print("  join: 799 entries / 854 keys, every family matching; trigger table 75 families / 799 / 854;',
     'print("  join: 946 entries / 1003 keys, every family matching; trigger table 95 families / 946 / 1003;', 1),
    ('print("  v1-v37: %d files byte-unchanged" % len(pre))', 'print("  v1-v48: %d files byte-unchanged" % len(pre))', 1),
]
for a, b, n in R:
    assert V38.count(a) == n, (a[:70], V38.count(a))
    V38 = V38.replace(a, b)
tmp = os.path.join(T, "_verify_v49_base.py")
open(tmp, "w", encoding="utf-8", newline="\n").write(V38)
try:
    runpy.run_path(tmp, run_name="__main__")
except SystemExit as e:
    if e.code not in (None, 0):
        raise
finally:
    os.remove(tmp)

import make_xlsx_v49 as M  # noqa: E402  (the NOTES list and the run file; nothing is written on import)
RUN_CARDS = {}
for line in open(M.RUN, encoding="utf-8"):
    if line.startswith("CARD "):
        m, c = line[5:].rstrip("\n").split(": ", 1)
        RUN_CARDS[m] = c
wb = openpyxl.load_workbook(M.DST, read_only=True)
cs = wb["Cards"]
rows = list(cs.iter_rows(min_row=2, values_only=True))
same = sum(1 for r in rows if RUN_CARDS.get(r[0]) == r[4])
whole = sum(1 for r in rows if r[4] and "{" not in r[4] and "[" not in r[4] and "\u2014" not in r[4]
            and r[4].startswith(str(r[1]) + " on A: ") and r[4].endswith("."))
ws = wb["Abilities"]
noted = set()
for row in ws.iter_rows(min_row=2, values_only=True):
    for k in str(row[2]).split(";"):
        k = k.strip()
        if k in M.NOTES and ("ROUND 165 (night audit): " + M.NOTES[k] + ".") in str(row[21]):
            noted.add(k)
print("Cards: %d rows, %d equal to the harness run, %d whole; round-165 notes: %d / %d"
      % (len(rows), same, whole, len(noted), len(M.NOTES)))
good = len(rows) == 946 and same == 946 and whole == 946 and noted == set(M.NOTES)
print("XLSX v49 VERIFY OK" if good else "XLSX v49 VERIFY: round-165 checks FAILED")
sys.exit(0 if good else 1)
