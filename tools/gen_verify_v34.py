#!/usr/bin/env python3
"""Write tools/verify_xlsx_v34.py from verify_xlsx_v33.py (round 142)."""
T = r"C:\Users\vlady\Desktop\WH3_mod\tools"
s = open(T + r"\verify_xlsx_v33.py", encoding="utf-8").read()
ADD = ('EXPECT.update({"wh2_dlc11_hero_abilities_more_powder": "ally_ammo_low", '
       '"wh3_dlc25_abilities_restock_gunnery_school": "ally_ammo_low", '
       '"wh3_dlc27_character_abilities_master_of_mists": "ground_ally_before_range", '
       '"wh3_dlc29_unit_abilities_of_warp_and_ruin": "self_shooting_clear", '
       '"wh3_dlc25_item_abilities_ominous_powder": "self_shooting_healthy", '
       '"wh_main_unit_abilities_blooood": "self_moving"})\n')
R = [
    (r'docs\WH3_abilities_master_v33_2026-11-13.xlsx"', r'docs\WH3_abilities_master_v34_2026-11-13.xlsx"'),
    (r'PREV = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v32_2026-11-13.xlsx"',
     r'PREV = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v33_2026-11-13.xlsx"'),
    (r"backups\round141\pre_v33_workbook_md5.txt", r"backups\round142\pre_v34_workbook_md5.txt"),
    ('PACK_MD5 = "2eafed987e269c47af570cf4670865cb"', 'PACK_MD5 = "d4b0ebaef4476414ecea798c9b599a32"'),
    ("KEEP_GATES = {", ADD + "KEEP_GATES = {"),
    ('"A1: %d rows in v33, %d in v32"', '"A1: %d rows in v34, %d in v33"'),
    ("check(len(impl_rows) == 750 and len(impl_keys) == 750,", "check(len(impl_rows) == 756 and len(impl_keys) == 756,"),
    ("check(len(entries) == 698 and len(mod_keys) == 750,", "check(len(entries) == 703 and len(mod_keys) == 756,"),
    ("te = [cell(r, 3) for r in range(44, 108)]", "te = [cell(r, 3) for r in range(44, 111)]"),
    ("tk = [cell(r, 4) for r in range(44, 108)]", "tk = [cell(r, 4) for r in range(44, 111)]"),
    ("names = [str(cell(r, 2)) for r in range(44, 108)]", "names = [str(cell(r, 2)) for r in range(44, 111)]"),
    ('len(te) == 64 and all(isinstance(x, int) for x in te), "F1: trigger table is not 64 integer rows")',
     'len(te) == 67 and all(isinstance(x, int) for x in te), "F1: trigger table is not 67 integer rows")'),
    ("sum(te) == cell(108, 3) == 698 and sum(tk) == cell(108, 4) == 750,",
     "sum(te) == cell(111, 3) == 703 and sum(tk) == cell(111, 4) == 756,"),
    ('cell(110, 1) == "Bombardment set (COMPLETE - round 108)" and cell(112, 3) == 131, "F3: bombardment block not at row 110")',
     'cell(113, 1) == "Bombardment set (COMPLETE - round 108)" and cell(115, 3) == 131, "F3: bombardment block not at row 113")'),
    ('"self_running": 1,', '"self_moving": 1, "ground_ally_before_range": 1, "self_shooting_clear": 1, "self_shooting_healthy": 1,'),
    ("check(cell(13, 3) == 750 and cell(14, 3) == 373,", "check(cell(13, 3) == 756 and cell(14, 3) == 367,"),
    ('startswith("DEFINITIONS - WH3 ability master v33"), "G1: title")',
     'startswith("DEFINITIONS - WH3 ability master v34"), "G1: title")'),
    ('startswith("30. ROUND 141")', 'startswith("31. ROUND 142")'),
    ('"G2: section 30 missing"', '"G2: section 31 missing"'),
    ('== "v33" and PACK_MD5', '== "v34" and PACK_MD5'),
    ('"G3: changelog v33 row or pack md5 missing"', '"G3: changelog v34 row or pack md5 missing"'),
    ("check(len(pre) == 60 and not changed,", "check(len(pre) == 62 and not changed,"),
    ('print("XLSX v33 VERIFY: %d FAILURE(S)" % len(fails))', 'print("XLSX v34 VERIFY: %d FAILURE(S)" % len(fails))'),
    ('print("XLSX v33 VERIFY OK")', 'print("XLSX v34 VERIFY OK")'),
    ("750 implemented; 24 skipped", "756 implemented; 24 skipped"),
    ("join: 698 entries / 750 keys, every family matching; trigger table 64 families / 698 / 750",
     "join: 703 entries / 756 keys, every family matching; trigger table 67 families / 703 / 756"),
    ('the nine recharge reducers on their families")', 'open batch 1 and Blooood! on their families")'),
    ('print("  v1-v32: %d files byte-unchanged" % len(pre))', 'print("  v1-v33: %d files byte-unchanged" % len(pre))'),
]
for a, b in R:
    assert s.count(a) == 1, (a[:70], s.count(a))
    s = s.replace(a, b)
open(T + r"\verify_xlsx_v34.py", "w", encoding="utf-8", newline="\n").write(s)
print("verifier written")
