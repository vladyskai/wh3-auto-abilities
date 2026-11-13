#!/usr/bin/env python3
"""Write tools/verify_xlsx_v33.py from verify_xlsx_v32.py (round 141)."""
T = r"C:\Users\vlady\Desktop\WH3_mod\tools"
s = open(T + r"\verify_xlsx_v32.py", encoding="utf-8").read()
ADD = ('EXPECT.update({"wh_main_item_abilities_scroll_of_power": "self_recharging_2", '
       '"wh3_main_weapon_abilities_staff_of_tomorrow": "self_recharging", '
       '"wh2_dlc15_item_abilities_armour_of_caledor": "melee_health75", '
       '"wh_dlc08_item_abilities_terrorgheist_skull": "melee_self_or_ally", '
       '"wh3_dlc23_weapon_abilities_spell_wrought_sceptre": "recharging_in_reach"})\n')
R = [
    (r'docs\WH3_abilities_master_v32_2026-11-13.xlsx"', r'docs\WH3_abilities_master_v33_2026-11-13.xlsx"'),
    (r'PREV = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v31_2026-11-09.xlsx"',
     r'PREV = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v32_2026-11-13.xlsx"'),
    (r"backups\round140\pre_v32_workbook_md5.txt", r"backups\round141\pre_v33_workbook_md5.txt"),
    ('PACK_MD5 = "76cc9ff49ac96ac6ee89fa12372576b1"', 'PACK_MD5 = "2eafed987e269c47af570cf4670865cb"'),
    ("KEEP_GATES = {", ADD + "KEEP_GATES = {"),
    ('"A1: %d rows in v32, %d in v31"', '"A1: %d rows in v33, %d in v32"'),
    ("te = [cell(r, 3) for r in range(44, 104)]", "te = [cell(r, 3) for r in range(44, 108)]"),
    ("tk = [cell(r, 4) for r in range(44, 104)]", "tk = [cell(r, 4) for r in range(44, 108)]"),
    ("names = [str(cell(r, 2)) for r in range(44, 104)]", "names = [str(cell(r, 2)) for r in range(44, 108)]"),
    ('len(te) == 60 and all(isinstance(x, int) for x in te), "F1: trigger table is not 60 integer rows")',
     'len(te) == 64 and all(isinstance(x, int) for x in te), "F1: trigger table is not 64 integer rows")'),
    ("sum(te) == cell(104, 3) == 698 and sum(tk) == cell(104, 4) == 750,",
     "sum(te) == cell(108, 3) == 698 and sum(tk) == cell(108, 4) == 750,"),
    ('cell(106, 1) == "Bombardment set (COMPLETE - round 108)" and cell(108, 3) == 131, "F3: bombardment block not at row 106")',
     'cell(110, 1) == "Bombardment set (COMPLETE - round 108)" and cell(112, 3) == 131, "F3: bombardment block not at row 110")'),
    ('{"melee_unwavering": 314,', '{"melee_unwavering": 306, "self_recharging": 5, "self_recharging_2": 1, "recharging_in_reach": 1, "melee_self_or_ally": 1,'),
    ('startswith("DEFINITIONS - WH3 ability master v32"), "G1: title")',
     'startswith("DEFINITIONS - WH3 ability master v33"), "G1: title")'),
    ('startswith("29. ROUND 140")', 'startswith("30. ROUND 141")'),
    ('"G2: section 29 missing"', '"G2: section 30 missing"'),
    ('== "v32" and PACK_MD5', '== "v33" and PACK_MD5'),
    ('"G3: changelog v32 row or pack md5 missing"', '"G3: changelog v33 row or pack md5 missing"'),
    ("check(len(pre) == 58 and not changed,", "check(len(pre) == 60 and not changed,"),
    ('print("XLSX v32 VERIFY: %d FAILURE(S)" % len(fails))', 'print("XLSX v33 VERIFY: %d FAILURE(S)" % len(fails))'),
    ('print("XLSX v32 VERIFY OK")', 'print("XLSX v33 VERIFY OK")'),
    ("trigger table 60 families", "trigger table 64 families"),
    ('Blooood! on self_running, the moving rule on the shooting rows")', 'the nine recharge reducers on their families")'),
    ('print("  v1-v31: %d files byte-unchanged" % len(pre))', 'print("  v1-v32: %d files byte-unchanged" % len(pre))'),
]
for a, b in R:
    assert s.count(a) == 1, (a[:70], s.count(a))
    s = s.replace(a, b)
open(T + r"\verify_xlsx_v33.py", "w", encoding="utf-8", newline="\n").write(s)
print("verifier written")
