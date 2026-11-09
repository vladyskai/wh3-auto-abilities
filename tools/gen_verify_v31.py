#!/usr/bin/env python3
"""Write tools/verify_xlsx_v31.py from verify_xlsx_v30.py (round 139)."""
T = r"C:\Users\vlady\Desktop\WH3_mod\tools"
s = open(T + r"\verify_xlsx_v30.py", encoding="utf-8").read()
ADD = 'EXPECT["wh_main_character_abilities_stand_your_ground"] = "melee_or_wavering_aura"\n'
R = [
    (r'docs\WH3_abilities_master_v30_2026-11-09.xlsx"', r'docs\WH3_abilities_master_v31_2026-11-09.xlsx"'),
    (r'PREV = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v29_2026-11-09.xlsx"',
     r'PREV = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v30_2026-11-09.xlsx"'),
    (r"backups\round138\pre_v30_workbook_md5.txt", r"backups\round139\pre_v31_workbook_md5.txt"),
    ('PACK_MD5 = "4d69206141c5d9eb89506fd0ed1064bd"', 'PACK_MD5 = "55f3263e09fedd951d1bcd8ee9ce9351"'),
    ("KEEP_GATES = {", ADD + "KEEP_GATES = {"),
    ('"A1: %d rows in v30, %d in v29"', '"A1: %d rows in v31, %d in v30"'),
    ('"enemy_missile_shooting": 1,', '"enemy_missile_shooting": 1, "melee_or_wavering_aura": 1,'),
    ('startswith("DEFINITIONS - WH3 ability master v30"), "G1: title")',
     'startswith("DEFINITIONS - WH3 ability master v31"), "G1: title")'),
    ('startswith("27. ROUND 138")', 'startswith("28. ROUND 139")'),
    ('"G2: section 27 missing"', '"G2: section 28 missing"'),
    ('== "v30" and PACK_MD5', '== "v31" and PACK_MD5'),
    ('"G3: changelog v30 row or pack md5 missing"', '"G3: changelog v31 row or pack md5 missing"'),
    ("check(len(pre) == 54 and not changed,", "check(len(pre) == 56 and not changed,"),
    ('print("XLSX v30 VERIFY: %d FAILURE(S)" % len(fails))', 'print("XLSX v31 VERIFY: %d FAILURE(S)" % len(fails))'),
    ('print("XLSX v30 VERIFY OK")', 'print("XLSX v31 VERIFY OK")'),
    ('5 round-138 rows checked")', 'Stand Your Ground on its new family")'),
    ('print("  v1-v29: %d files byte-unchanged" % len(pre))', 'print("  v1-v30: %d files byte-unchanged" % len(pre))'),
]
for a, b in R:
    assert s.count(a) == 1, (a[:70], s.count(a))
    s = s.replace(a, b)
open(T + r"\verify_xlsx_v31.py", "w", encoding="utf-8", newline="\n").write(s)
print("verifier written")
