#!/usr/bin/env python3
"""Write tools/verify_xlsx_v32.py from verify_xlsx_v31.py (round 140)."""
T = r"C:\Users\vlady\Desktop\WH3_mod\tools"
s = open(T + r"\verify_xlsx_v31.py", encoding="utf-8").read()
ADD = 'EXPECT["wh_main_unit_abilities_blooood"] = "self_running"\n'
CHK = ('check("MOVING RULE (round 140" in str(by_key["wh_main_unit_abilities_boom"][21]), "B13: Boom! lacks the moving rule")\n')
R = [
    (r'docs\WH3_abilities_master_v31_2026-11-09.xlsx"', r'docs\WH3_abilities_master_v32_2026-11-13.xlsx"'),
    (r'PREV = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v30_2026-11-09.xlsx"',
     r'PREV = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v31_2026-11-09.xlsx"'),
    (r"backups\round139\pre_v31_workbook_md5.txt", r"backups\round140\pre_v32_workbook_md5.txt"),
    ('PACK_MD5 = "55f3263e09fedd951d1bcd8ee9ce9351"', 'PACK_MD5 = "76cc9ff49ac96ac6ee89fa12372576b1"'),
    ("KEEP_GATES = {", ADD + "KEEP_GATES = {"),
    ('"A1: %d rows in v31, %d in v30"', '"A1: %d rows in v32, %d in v31"'),
    ('check("bound: 24 m (70% of the ability\'s 35 m effect_range)" in str(by_key["wh_main_character_abilities_rally"][21])',
     CHK + 'check("bound: 24 m (70% of the ability\'s 35 m effect_range)" in str(by_key["wh_main_character_abilities_rally"][21])'),
    ("te = [cell(r, 3) for r in range(44, 103)]", "te = [cell(r, 3) for r in range(44, 104)]"),
    ("tk = [cell(r, 4) for r in range(44, 103)]", "tk = [cell(r, 4) for r in range(44, 104)]"),
    ("names = [str(cell(r, 2)) for r in range(44, 103)]", "names = [str(cell(r, 2)) for r in range(44, 104)]"),
    ('len(te) == 59 and all(isinstance(x, int) for x in te), "F1: trigger table is not 59 integer rows")',
     'len(te) == 60 and all(isinstance(x, int) for x in te), "F1: trigger table is not 60 integer rows")'),
    ("sum(te) == cell(103, 3) == 698 and sum(tk) == cell(103, 4) == 750,",
     "sum(te) == cell(104, 3) == 698 and sum(tk) == cell(104, 4) == 750,"),
    ('cell(105, 1) == "Bombardment set (COMPLETE - round 108)" and cell(107, 3) == 131, "F3: bombardment block not at row 105")',
     'cell(106, 1) == "Bombardment set (COMPLETE - round 108)" and cell(108, 3) == 131, "F3: bombardment block not at row 106")'),
    ('"charge_only": 5,', '"charge_only": 4, "self_running": 1,'),
    ('startswith("DEFINITIONS - WH3 ability master v31"), "G1: title")',
     'startswith("DEFINITIONS - WH3 ability master v32"), "G1: title")'),
    ('startswith("28. ROUND 139")', 'startswith("29. ROUND 140")'),
    ('"G2: section 28 missing"', '"G2: section 29 missing"'),
    ('== "v31" and PACK_MD5', '== "v32" and PACK_MD5'),
    ('"G3: changelog v31 row or pack md5 missing"', '"G3: changelog v32 row or pack md5 missing"'),
    ("check(len(pre) == 56 and not changed,", "check(len(pre) == 58 and not changed,"),
    ('print("XLSX v31 VERIFY: %d FAILURE(S)" % len(fails))', 'print("XLSX v32 VERIFY: %d FAILURE(S)" % len(fails))'),
    ('print("XLSX v31 VERIFY OK")', 'print("XLSX v32 VERIFY OK")'),
    ("trigger table 59 families", "trigger table 60 families"),
    ('Stand Your Ground on its new family")', 'Blooood! on self_running, the moving rule on the shooting rows")'),
    ('print("  v1-v30: %d files byte-unchanged" % len(pre))', 'print("  v1-v31: %d files byte-unchanged" % len(pre))'),
]
for a, b in R:
    assert s.count(a) == 1, (a[:70], s.count(a))
    s = s.replace(a, b)
open(T + r"\verify_xlsx_v32.py", "w", encoding="utf-8", newline="\n").write(s)
print("verifier written")
