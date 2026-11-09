#!/usr/bin/env python3
"""Write tools/verify_xlsx_v29.py from verify_xlsx_v28.py (round 137: the 14 morale rows, 58 families, the
bombardment block at row 104)."""
T = r"C:\Users\vlady\Desktop\WH3_mod\tools"
s = open(T + r"\verify_xlsx_v28.py", encoding="utf-8").read()
ADD = ('EXPECT.update({k: "wavering_aura" for k in ("wh_main_character_abilities_rally", '
       '"wh2_main_mount_abilities_unholy_clamour", "wh2_dlc15_unit_abilities_mimic_cold_blooded")})\n'
       'EXPECT.update({k: "wavering_ally_range" for k in ("wh_main_item_abilities_crown_of_command", '
       '"wh3_dlc24_character_abilities_tacticians_rally")})\n')
CHK = ('check("bound: 24 m (70% of the ability\'s 35 m effect_range)" in str(by_key["wh_main_character_abilities_rally"][21])\n'
       '      and "whole army" in str(by_key["wh2_main_mount_abilities_unholy_clamour"][21])\n'
       '      and "bound: 70 m (70% of the ability\'s 100 m ally cast reach)" in str(by_key["wh_main_item_abilities_crown_of_command"][21]),\n'
       '      "B11: the morale bound texts are wrong")\n')
R = [
    (r'docs\WH3_abilities_master_v28_2026-11-09.xlsx"', r'docs\WH3_abilities_master_v29_2026-11-09.xlsx"'),
    (r'PREV = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v27_2026-11-09.xlsx"',
     r'PREV = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v28_2026-11-09.xlsx"'),
    (r"backups\round136\pre_v28_workbook_md5.txt", r"backups\round137\pre_v29_workbook_md5.txt"),
    ('PACK_MD5 = "104c049b22f675b1487f425eeb7fdb2e"', 'PACK_MD5 = "c719e140ddff4f0525889c1388bb3fd8"'),
    ("KEEP_GATES = {", ADD + "KEEP_GATES = {"),
    ('"A1: %d rows in v28, %d in v27"', '"A1: %d rows in v29, %d in v28"'),
    ('check("bound: 24 m (70% of', CHK + 'check("bound: 24 m (70% of'),
    ("te = [cell(r, 3) for r in range(44, 101)]", "te = [cell(r, 3) for r in range(44, 102)]"),
    ("tk = [cell(r, 4) for r in range(44, 101)]", "tk = [cell(r, 4) for r in range(44, 102)]"),
    ("names = [str(cell(r, 2)) for r in range(44, 101)]", "names = [str(cell(r, 2)) for r in range(44, 102)]"),
    ('len(te) == 57 and all(isinstance(x, int) for x in te), "F1: trigger table is not 57 integer rows")',
     'len(te) == 58 and all(isinstance(x, int) for x in te), "F1: trigger table is not 58 integer rows")'),
    ("sum(te) == cell(101, 3) == 698 and sum(tk) == cell(101, 4) == 750,",
     "sum(te) == cell(102, 3) == 698 and sum(tk) == cell(102, 4) == 750,"),
    ('cell(103, 1) == "Bombardment set (COMPLETE - round 108)" and cell(105, 3) == 131, "F3: bombardment block not at row 103")',
     'cell(104, 1) == "Bombardment set (COMPLETE - round 108)" and cell(106, 3) == 131, "F3: bombardment block not at row 104")'),
    ('{"melee_unwavering": 328,', '{"melee_unwavering": 314, "wavering_aura": 9, "wavering_ally_range": 6,'),
    ('startswith("DEFINITIONS - WH3 ability master v28"), "G1: title")',
     'startswith("DEFINITIONS - WH3 ability master v29"), "G1: title")'),
    ('startswith("25. ROUND 136")', 'startswith("26. ROUND 137")'),
    ('"G2: section 25 missing"', '"G2: section 26 missing"'),
    ('== "v28" and PACK_MD5', '== "v29" and PACK_MD5'),
    ('"G3: changelog v28 row or pack md5 missing"', '"G3: changelog v29 row or pack md5 missing"'),
    ("check(len(pre) == 50 and not changed,", "check(len(pre) == 52 and not changed,"),
    ('print("XLSX v28 VERIFY: %d FAILURE(S)" % len(fails))', 'print("XLSX v29 VERIFY: %d FAILURE(S)" % len(fails))'),
    ('print("XLSX v28 VERIFY OK")', 'print("XLSX v29 VERIFY OK")'),
    ("trigger table 57 families", "trigger table 58 families"),
    ('23 more enemy rows on their families")', '14 morale rows on their families")'),
    ('print("  v1-v27: %d files byte-unchanged" % len(pre))', 'print("  v1-v28: %d files byte-unchanged" % len(pre))'),
]
for a, b in R:
    assert s.count(a) == 1, (a[:70], s.count(a))
    s = s.replace(a, b)
open(T + r"\verify_xlsx_v29.py", "w", encoding="utf-8", newline="\n").write(s)
print("verifier written")
