#!/usr/bin/env python3
"""Verify docs/WH3_abilities_master_v41_2026-11-15.xlsx (round 153) from disk: the v38 verifier's structural checks
re-pointed at v41 (row count, families, Numbers reconciliation, older versions byte-unchanged), plus the round-153
texts (and the round-152 texts still in place)."""
import os
import runpy
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openpyxl  # noqa: E402
import gen_blob_tables as GB  # noqa: E402

T = os.path.dirname(os.path.abspath(__file__))
V38 = open(os.path.join(T, "verify_xlsx_v38.py"), encoding="utf-8").read()
R = [
    (r'docs\WH3_abilities_master_v38_2026-11-14.xlsx"', r'docs\WH3_abilities_master_v41_2026-11-15.xlsx"'),
    (r'PREV = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v37_2026-11-13.xlsx"',
     r'PREV = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v40_2026-11-15.xlsx"'),
    (r"backups\round150\pre_v38_workbook_md5.txt", r"backups\round153\pre_v41_workbook_md5.txt"),
    ('PACK_MD5 = "49a0903d999768b3b1123379db5a4268"', 'PACK_MD5 = "04ed9fcfe08ef13b800d6810f61e4629"'),
    ('"A1: %d rows in v38, %d in v37"', '"A1: %d rows in v41, %d in v40"'),
    ('startswith("DEFINITIONS - WH3 ability master v38"), "G1: title")',
     'startswith("DEFINITIONS - WH3 ability master v41"), "G1: title")'),
    ('startswith("35. ROUND 150")', 'startswith("38. ROUND 153")'),
    ('"G2: section 35 missing"', '"G2: section 38 missing"'),
    ('== "v38" and PACK_MD5', '== "v41" and PACK_MD5'),
    ('"G3: changelog v38 row or pack md5 missing"', '"G3: changelog v41 row or pack md5 missing"'),
    ("check(len(pre) == 70 and not changed,", "check(len(pre) == 76 and not changed,"),
    ('print("XLSX v38 VERIFY: %d FAILURE(S)" % len(fails))', 'print("XLSX v41 VERIFY (structural checks): %d FAILURE(S)" % len(fails))'),
    ('print("XLSX v38 VERIFY OK")', 'print("XLSX v41 VERIFY (structural checks) OK")'),
    ('print("  v1-v37: %d files byte-unchanged" % len(pre))', 'print("  v1-v40: %d files byte-unchanged" % len(pre))'),
]
for a, b in R:
    assert V38.count(a) == 1, (a[:70], V38.count(a))
    V38 = V38.replace(a, b)
tmp = os.path.join(T, "_verify_v41_base.py")
open(tmp, "w", encoding="utf-8", newline="\n").write(V38)
try:
    runpy.run_path(tmp, run_name="__main__")
except SystemExit as e:
    if e.code not in (None, 0):
        raise
finally:
    os.remove(tmp)

ws = openpyxl.load_workbook(r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v41_2026-11-15.xlsx",
                            read_only=True)["Abilities"]
src = open(r"C:/Users/vlady/Desktop/WH3_mod/mod_source/script/battle/mod/zz_test_deadly_onslaught.lua", encoding="utf-8").read()
keys = set(GB.keys_in(src))
trash = nohold = held = 0
for row in ws.iter_rows(min_row=2, values_only=True):
    k = str(row[2]).split(";")[0].strip()
    t = str(row[21])
    if "cast is HELD" in t:
        held += 1
    if k in keys:
        if "ROUND 153 TRASH" in t:
            trash += 1
        if "NO hold" in t:
            nohold += 1
ok = (trash == 77 and nohold == 53 and held == 0)
print("round-153 texts: trash %d / 77; round-152 no-hold still %d / 53; held left %d" % (trash, nohold, held))
print("XLSX v41 VERIFY OK" if ok else "XLSX v41 VERIFY: texts FAILED")
sys.exit(0 if ok else 1)
