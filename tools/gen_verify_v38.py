#!/usr/bin/env python3
"""Write tools/verify_xlsx_v38.py from verify_xlsx_v37.py (round 150)."""
T = r"C:\Users\vlady\Desktop\WH3_mod\tools"
s = open(T + r"\verify_xlsx_v37.py", encoding="utf-8").read()
ADD = ('import round150_value_target as _R150\n'
       'EXPECT.update({k: "when_ready" for k in _R150.WINDS})\n'
       'assert len(_R150.WINDS) == 21\n')
R = [
    (r'docs\WH3_abilities_master_v37_2026-11-13.xlsx"', r'docs\WH3_abilities_master_v38_2026-11-14.xlsx"'),
    (r'PREV = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v36_2026-11-13.xlsx"',
     r'PREV = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v37_2026-11-13.xlsx"'),
    (r"backups\round146\pre_v37_workbook_md5.txt", r"backups\round150\pre_v38_workbook_md5.txt"),
    ('PACK_MD5 = "1d2b92d73019956836328a35dd2ade5c"', 'PACK_MD5 = "49a0903d999768b3b1123379db5a4268"'),
    ("KEEP_GATES = {", ADD + "KEEP_GATES = {"),
    ('"A1: %d rows in v37, %d in v36"', '"A1: %d rows in v38, %d in v37"'),
    ("te = [cell(r, 3) for r in range(44, 118)]", "te = [cell(r, 3) for r in range(44, 119)]"),
    ("tk = [cell(r, 4) for r in range(44, 118)]", "tk = [cell(r, 4) for r in range(44, 119)]"),
    ("names = [str(cell(r, 2)) for r in range(44, 118)]", "names = [str(cell(r, 2)) for r in range(44, 119)]"),
    ('len(te) == 74 and all(isinstance(x, int) for x in te), "F1: trigger table is not 74 integer rows")',
     'len(te) == 75 and all(isinstance(x, int) for x in te), "F1: trigger table is not 75 integer rows")'),
    ("sum(te) == cell(118, 3) == 799 and sum(tk) == cell(118, 4) == 854,",
     "sum(te) == cell(119, 3) == 799 and sum(tk) == cell(119, 4) == 854,"),
    ('cell(120, 1) == "Bombardment set (COMPLETE - round 108)" and cell(122, 3) == 131, "F3: bombardment block not at row 120")',
     'cell(121, 1) == "Bombardment set (COMPLETE - round 108)" and cell(123, 3) == 131, "F3: bombardment block not at row 121")'),
    ('"melee_unwavering": 309,', '"melee_unwavering": 288, "when_ready": 21,'),
    ('startswith("DEFINITIONS - WH3 ability master v37"), "G1: title")',
     'startswith("DEFINITIONS - WH3 ability master v38"), "G1: title")'),
    ('startswith("34. ROUND 146")', 'startswith("35. ROUND 150")'),
    ('"G2: section 34 missing"', '"G2: section 35 missing"'),
    ('== "v37" and PACK_MD5', '== "v38" and PACK_MD5'),
    ('"G3: changelog v37 row or pack md5 missing"', '"G3: changelog v38 row or pack md5 missing"'),
    ("check(len(pre) == 68 and not changed,", "check(len(pre) == 70 and not changed,"),
    ('print("XLSX v37 VERIFY: %d FAILURE(S)" % len(fails))', 'print("XLSX v38 VERIFY: %d FAILURE(S)" % len(fails))'),
    ('print("XLSX v37 VERIFY OK")', 'print("XLSX v38 VERIFY OK")'),
    ("trigger table 74 families / 799 / 854", "trigger table 75 families / 799 / 854"),
    ('the 77 blob attacks on their family")', 'the 77 blob attacks and the 21 when_ready rows on their families")'),
    ('print("  v1-v36: %d files byte-unchanged" % len(pre))', 'print("  v1-v37: %d files byte-unchanged" % len(pre))'),
]
for a, b in R:
    assert s.count(a) == 1, (a[:70], s.count(a))
    s = s.replace(a, b)
open(T + r"\verify_xlsx_v38.py", "w", encoding="utf-8", newline="\n").write(s)
print("verifier written")
