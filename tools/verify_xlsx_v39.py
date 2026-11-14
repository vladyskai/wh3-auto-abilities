#!/usr/bin/env python3
"""Verify docs/WH3_abilities_master_v39_2026-11-14.xlsx (round 151) from disk: the v38 verifier's checks re-pointed at
v39 (same row count, families, Numbers reconciliation, older versions byte-unchanged), plus the round-151 texts."""
import glob
import hashlib
import os
import runpy
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openpyxl  # noqa: E402
import gen_blob_tables as GB  # noqa: E402
import build_ability_database as bd  # noqa: E402
import round151_large_defaults as R151  # noqa: E402

T = os.path.dirname(os.path.abspath(__file__))
V38 = open(os.path.join(T, "verify_xlsx_v38.py"), encoding="utf-8").read()
R = [
    (r'docs\WH3_abilities_master_v38_2026-11-14.xlsx"', r'docs\WH3_abilities_master_v39_2026-11-14.xlsx"'),
    (r'PREV = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v37_2026-11-13.xlsx"',
     r'PREV = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v38_2026-11-14.xlsx"'),
    (r"backups\round150\pre_v38_workbook_md5.txt", r"backups\round151\pre_v39_workbook_md5.txt"),
    ('PACK_MD5 = "49a0903d999768b3b1123379db5a4268"', 'PACK_MD5 = "929621699dcf172b415c2e27d20c4a78"'),
    ('"A1: %d rows in v38, %d in v37"', '"A1: %d rows in v39, %d in v38"'),
    ('startswith("DEFINITIONS - WH3 ability master v38"), "G1: title")',
     'startswith("DEFINITIONS - WH3 ability master v39"), "G1: title")'),
    ('startswith("35. ROUND 150")', 'startswith("36. ROUND 151")'),
    ('"G2: section 35 missing"', '"G2: section 36 missing"'),
    ('== "v38" and PACK_MD5', '== "v39" and PACK_MD5'),
    ('"G3: changelog v38 row or pack md5 missing"', '"G3: changelog v39 row or pack md5 missing"'),
    ("check(len(pre) == 70 and not changed,", "check(len(pre) == 72 and not changed,"),
    ('print("XLSX v38 VERIFY: %d FAILURE(S)" % len(fails))', 'print("XLSX v39 VERIFY (v38 checks): %d FAILURE(S)" % len(fails))'),
    ('print("XLSX v38 VERIFY OK")', 'print("XLSX v39 VERIFY (v38 checks) OK")'),
    ('print("  v1-v37: %d files byte-unchanged" % len(pre))', 'print("  v1-v38: %d files byte-unchanged" % len(pre))'),
]
for a, b in R:
    assert V38.count(a) == 1, (a[:70], V38.count(a))
    V38 = V38.replace(a, b)
tmp = os.path.join(T, "_verify_v39_base.py")
open(tmp, "w", encoding="utf-8", newline="\n").write(V38)
try:
    runpy.run_path(tmp, run_name="__main__")
finally:
    os.remove(tmp)

# the round-151 texts
ws = openpyxl.load_workbook(r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v39_2026-11-14.xlsx",
                            read_only=True)["Abilities"]
src = open(r"C:/Users/vlady/Desktop/WH3_mod/mod_source/script/battle/mod/zz_test_deadly_onslaught.lua", encoding="utf-8").read()
shot = GB.shot_table(GB.keys_in(src))
entries, _, _ = bd.mod_entries()
dkeys = {k for e in entries if e["trigger"] in set(R151.DEFAULT_ON) for k in e["keys"]}
large = breath = dflt = bad = 0
for row in ws.iter_rows(min_row=2, values_only=True):
    k = str(row[2]).split(";")[0].strip()
    t = str(row[21])
    if k in shot:
        if shot[k][4] and "ROUND 151 LARGE FIRST" in t:
            large += 1
        if shot[k][5] and "ROUND 151 BREATH" in t:
            breath += 1
    if k in dkeys:
        if "DEFAULT (round 151" in t:
            dflt += 1
        else:
            bad += 1
ok = (large == 53 and breath == 20 and dflt == len(dkeys) and bad == 0)
print("round-151 texts: large-first %d / 53, breath %d / 20, default-armed %d / %d" % (large, breath, dflt, len(dkeys)))
print("XLSX v39 VERIFY OK" if ok else "XLSX v39 VERIFY: round-151 texts FAILED")
sys.exit(0 if ok else 1)
