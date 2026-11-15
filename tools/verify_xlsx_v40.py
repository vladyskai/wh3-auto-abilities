#!/usr/bin/env python3
"""Verify docs/WH3_abilities_master_v40_2026-11-15.xlsx (round 152) from disk: the v38 verifier's structural checks
re-pointed at v40 (row count, families, Numbers reconciliation, older versions byte-unchanged), plus the round-152
texts."""
import os
import runpy
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openpyxl  # noqa: E402
import build_ability_database as bd  # noqa: E402
import gen_blob_tables as GB  # noqa: E402

T = os.path.dirname(os.path.abspath(__file__))
V38 = open(os.path.join(T, "verify_xlsx_v38.py"), encoding="utf-8").read()
R = [
    (r'docs\WH3_abilities_master_v38_2026-11-14.xlsx"', r'docs\WH3_abilities_master_v40_2026-11-15.xlsx"'),
    (r'PREV = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v37_2026-11-13.xlsx"',
     r'PREV = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v39_2026-11-14.xlsx"'),
    (r"backups\round150\pre_v38_workbook_md5.txt", r"backups\round152\pre_v40_workbook_md5.txt"),
    ('PACK_MD5 = "49a0903d999768b3b1123379db5a4268"', 'PACK_MD5 = "0cc4a722865e4b5514e4716c9813b232"'),
    ('"A1: %d rows in v38, %d in v37"', '"A1: %d rows in v40, %d in v39"'),
    ('startswith("DEFINITIONS - WH3 ability master v38"), "G1: title")',
     'startswith("DEFINITIONS - WH3 ability master v40"), "G1: title")'),
    ('startswith("35. ROUND 150")', 'startswith("37. ROUND 152")'),
    ('"G2: section 35 missing"', '"G2: section 37 missing"'),
    ('== "v38" and PACK_MD5', '== "v40" and PACK_MD5'),
    ('"G3: changelog v38 row or pack md5 missing"', '"G3: changelog v40 row or pack md5 missing"'),
    ("check(len(pre) == 70 and not changed,", "check(len(pre) == 74 and not changed,"),
    ('print("XLSX v38 VERIFY: %d FAILURE(S)" % len(fails))', 'print("XLSX v40 VERIFY (structural checks): %d FAILURE(S)" % len(fails))'),
    ('print("XLSX v38 VERIFY OK")', 'print("XLSX v40 VERIFY (structural checks) OK")'),
    ('print("  v1-v37: %d files byte-unchanged" % len(pre))', 'print("  v1-v39: %d files byte-unchanged" % len(pre))'),
]
for a, b in R:
    assert V38.count(a) == 1, (a[:70], V38.count(a))
    V38 = V38.replace(a, b)
tmp = os.path.join(T, "_verify_v40_base.py")
open(tmp, "w", encoding="utf-8", newline="\n").write(V38)
try:
    runpy.run_path(tmp, run_name="__main__")
except SystemExit as e:
    if e.code not in (None, 0):
        raise
finally:
    os.remove(tmp)

ws = openpyxl.load_workbook(r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v40_2026-11-15.xlsx",
                            read_only=True)["Abilities"]
src = open(r"C:/Users/vlady/Desktop/WH3_mod/mod_source/script/battle/mod/zz_test_deadly_onslaught.lua", encoding="utf-8").read()
shot = GB.shot_table(GB.keys_in(src))
entries, _, _ = bd.mod_entries()
tired = {k for e in entries if e["trigger"] == "tired" for k in e["keys"]}
nohold = held = angle = tdef = 0
for row in ws.iter_rows(min_row=2, values_only=True):
    k = str(row[2]).split(";")[0].strip()
    t = str(row[21])
    if "cast is HELD" in t:
        held += 1
    if k in shot and shot[k][4] == 1:
        if "ROUND 152 (user rulings 2026-11-15): NO hold" in t:
            nohold += 1
        if "ROUND 151 BREATH" in t or "All 53 central attacks" in t:
            angle += 1
    if k in tired and "DEFAULT (round 152" in t:
        tdef += 1
ok = (nohold == 53 and held == 0 and angle == 53 and tdef == len(tired))
print("round-152 texts: no-hold %d / 53, held left %d, 90-degree %d / 53, tired default %d / %d"
      % (nohold, held, angle, tdef, len(tired)))
print("XLSX v40 VERIFY OK" if ok else "XLSX v40 VERIFY: round-152 texts FAILED")
sys.exit(0 if ok else 1)
