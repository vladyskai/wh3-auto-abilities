#!/usr/bin/env python3
"""Write tools/verify_xlsx_v30.py from verify_xlsx_v29.py (round 138)."""
T = r"C:\Users\vlady\Desktop\WH3_mod\tools"
s = open(T + r"\verify_xlsx_v29.py", encoding="utf-8").read()
ADD = 'EXPECT["wh3_dlc24_unit_bound_missile_mirror"] = "enemy_missile_shooting"\n'
CHK = ('check("target class: not undead" in str(by_key["wh3_dlc29_lord_abilities_gaze_of_usirian"][21])\n'
       '      and "target class: not flying" in str(by_key["wh2_dlc10_character_abilities_entangle"][21])\n'
       '      and "target class: Lord/Hero only" in str(by_key["wh3_main_item_abilities_void_pendulum"][21]),\n'
       '      "B12: a round-138 class text is missing")\n')
R = [
    ('== 18, "B6: the target-class rows are not 18")', '== 23, "B6: the target-class rows are not 23")'),
    ('== 52, "B10: enemy_engaged_or_shot rows are not 52 (47 entries; some span two rows)")',
     '== 51, "B10: enemy_engaged_or_shot rows are not 51 (46 entries; some span two rows)")'),
    (r'docs\WH3_abilities_master_v29_2026-11-09.xlsx"', r'docs\WH3_abilities_master_v30_2026-11-09.xlsx"'),
    (r'PREV = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v28_2026-11-09.xlsx"',
     r'PREV = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v29_2026-11-09.xlsx"'),
    (r"backups\round137\pre_v29_workbook_md5.txt", r"backups\round138\pre_v30_workbook_md5.txt"),
    ('PACK_MD5 = "c719e140ddff4f0525889c1388bb3fd8"', 'PACK_MD5 = "4d69206141c5d9eb89506fd0ed1064bd"'),
    ("KEEP_GATES = {", ADD + "KEEP_GATES = {"),
    ('"A1: %d rows in v29, %d in v28"', '"A1: %d rows in v30, %d in v29"'),
    ('check("bound: 24 m (70% of the ability\'s 35 m effect_range)" in str(by_key["wh_main_character_abilities_rally"][21])',
     CHK + 'check("bound: 24 m (70% of the ability\'s 35 m effect_range)" in str(by_key["wh_main_character_abilities_rally"][21])'),
    ("te = [cell(r, 3) for r in range(44, 102)]", "te = [cell(r, 3) for r in range(44, 103)]"),
    ("tk = [cell(r, 4) for r in range(44, 102)]", "tk = [cell(r, 4) for r in range(44, 103)]"),
    ("names = [str(cell(r, 2)) for r in range(44, 102)]", "names = [str(cell(r, 2)) for r in range(44, 103)]"),
    ('len(te) == 58 and all(isinstance(x, int) for x in te), "F1: trigger table is not 58 integer rows")',
     'len(te) == 59 and all(isinstance(x, int) for x in te), "F1: trigger table is not 59 integer rows")'),
    ("sum(te) == cell(102, 3) == 698 and sum(tk) == cell(102, 4) == 750,",
     "sum(te) == cell(103, 3) == 698 and sum(tk) == cell(103, 4) == 750,"),
    ('cell(104, 1) == "Bombardment set (COMPLETE - round 108)" and cell(106, 3) == 131, "F3: bombardment block not at row 104")',
     'cell(105, 1) == "Bombardment set (COMPLETE - round 108)" and cell(107, 3) == 131, "F3: bombardment block not at row 105")'),
    ('"enemy_engaged_or_shot": 47,', '"enemy_engaged_or_shot": 46, "enemy_missile_shooting": 1,'),
    ('startswith("DEFINITIONS - WH3 ability master v29"), "G1: title")',
     'startswith("DEFINITIONS - WH3 ability master v30"), "G1: title")'),
    ('startswith("26. ROUND 137")', 'startswith("27. ROUND 138")'),
    ('"G2: section 26 missing"', '"G2: section 27 missing"'),
    ('== "v29" and PACK_MD5', '== "v30" and PACK_MD5'),
    ('"G3: changelog v29 row or pack md5 missing"', '"G3: changelog v30 row or pack md5 missing"'),
    ("check(len(pre) == 52 and not changed,", "check(len(pre) == 54 and not changed,"),
    ('print("XLSX v29 VERIFY: %d FAILURE(S)" % len(fails))', 'print("XLSX v30 VERIFY: %d FAILURE(S)" % len(fails))'),
    ('print("XLSX v29 VERIFY OK")', 'print("XLSX v30 VERIFY OK")'),
    ("24 skipped; 18 target-class rows", "24 skipped; 23 target-class rows"),
    ("trigger table 58 families", "trigger table 59 families"),
    ('14 morale rows on their families")', '5 round-138 rows checked")'),
    ('print("  v1-v28: %d files byte-unchanged" % len(pre))', 'print("  v1-v29: %d files byte-unchanged" % len(pre))'),
]
for a, b in R:
    assert s.count(a) == 1, (a[:70], s.count(a))
    s = s.replace(a, b)
open(T + r"\verify_xlsx_v30.py", "w", encoding="utf-8", newline="\n").write(s)
print("verifier written")
