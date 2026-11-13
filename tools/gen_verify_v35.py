#!/usr/bin/env python3
"""Write tools/verify_xlsx_v35.py from verify_xlsx_v34.py (round 143)."""
T = r"C:\Users\vlady\Desktop\WH3_mod\tools"
s = open(T + r"\verify_xlsx_v34.py", encoding="utf-8").read()
ADD = ('EXPECT.update({k: "enemy_ground_melee" for k in ("wh2_dlc16_spell_bound_the_curse_of_anraheir", '
       '"wh3_main_spell_bound_the_curse_of_anraheir", "wh_dlc05_spell_bound_the_curse_of_anraheir", '
       '"wh3_main_spell_bound_transmutation_of_lead", "wh2_dlc10_spell_bound_soulblight", '
       '"wh3_dlc29_spell_bound_undeath_khizaar_the_soulstealer", "wh3_dlc26_character_abilities_squig_thinkin", '
       '"wh_main_unit_abilities_spinning_loons", "wh_dlc06_unit_abilities_the_loons_of_eight_peaks")})\n'
       'EXPECT.update({"wh2_dlc09_character_abilities_curse_of_djaf": "enemy_ground_shooting", '
       '"wh3_dlc29_spell_bound_soulblight": "melee_unwavering"})\n')
R = [
    (r'docs\WH3_abilities_master_v34_2026-11-13.xlsx"', r'docs\WH3_abilities_master_v35_2026-11-13.xlsx"'),
    (r'PREV = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v33_2026-11-13.xlsx"',
     r'PREV = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v34_2026-11-13.xlsx"'),
    (r"backups\round142\pre_v34_workbook_md5.txt", r"backups\round143\pre_v35_workbook_md5.txt"),
    ('PACK_MD5 = "d4b0ebaef4476414ecea798c9b599a32"', 'PACK_MD5 = "c2168f7908cb3e2403d7dbfbd94c017e"'),
    ("KEEP_GATES = {", ADD + "KEEP_GATES = {"),
    ('"A1: %d rows in v34, %d in v33"', '"A1: %d rows in v35, %d in v34"'),
    ("check(len(impl_rows) == 756 and len(impl_keys) == 756,", "check(len(impl_rows) == 767 and len(impl_keys) == 767,"),
    ("check(len(entries) == 703 and len(mod_keys) == 756,", "check(len(entries) == 712 and len(mod_keys) == 767,"),
    ("te = [cell(r, 3) for r in range(44, 111)]", "te = [cell(r, 3) for r in range(44, 112)]"),
    ("tk = [cell(r, 4) for r in range(44, 111)]", "tk = [cell(r, 4) for r in range(44, 112)]"),
    ("names = [str(cell(r, 2)) for r in range(44, 111)]", "names = [str(cell(r, 2)) for r in range(44, 112)]"),
    ('len(te) == 67 and all(isinstance(x, int) for x in te), "F1: trigger table is not 67 integer rows")',
     'len(te) == 68 and all(isinstance(x, int) for x in te), "F1: trigger table is not 68 integer rows")'),
    ("sum(te) == cell(111, 3) == 703 and sum(tk) == cell(111, 4) == 756,",
     "sum(te) == cell(112, 3) == 712 and sum(tk) == cell(112, 4) == 767,"),
    ('cell(113, 1) == "Bombardment set (COMPLETE - round 108)" and cell(115, 3) == 131, "F3: bombardment block not at row 113")',
     'cell(114, 1) == "Bombardment set (COMPLETE - round 108)" and cell(116, 3) == 131, "F3: bombardment block not at row 114")'),
    ('"melee_unwavering": 306,', '"melee_unwavering": 307, "enemy_ground_melee": 74, "enemy_ground_shooting": 1,'),
    ("check(cell(13, 3) == 756 and cell(14, 3) == 367,", "check(cell(13, 3) == 767 and cell(14, 3) == 356,"),
    ('startswith("DEFINITIONS - WH3 ability master v34"), "G1: title")',
     'startswith("DEFINITIONS - WH3 ability master v35"), "G1: title")'),
    ('startswith("31. ROUND 142")', 'startswith("32. ROUND 143")'),
    ('"G2: section 31 missing"', '"G2: section 32 missing"'),
    ('== "v34" and PACK_MD5', '== "v35" and PACK_MD5'),
    ('"G3: changelog v34 row or pack md5 missing"', '"G3: changelog v35 row or pack md5 missing"'),
    ("check(len(pre) == 62 and not changed,", "check(len(pre) == 64 and not changed,"),
    ('print("XLSX v34 VERIFY: %d FAILURE(S)" % len(fails))', 'print("XLSX v35 VERIFY: %d FAILURE(S)" % len(fails))'),
    ('print("XLSX v34 VERIFY OK")', 'print("XLSX v35 VERIFY OK")'),
    ("756 implemented; 24 skipped", "767 implemented; 24 skipped"),
    ("join: 703 entries / 756 keys, every family matching; trigger table 67 families / 703 / 756",
     "join: 712 entries / 767 keys, every family matching; trigger table 68 families / 712 / 767"),
    ('open batch 1 and Blooood! on their families")', 'open batch 2 on their families")'),
    ('print("  v1-v33: %d files byte-unchanged" % len(pre))', 'print("  v1-v34: %d files byte-unchanged" % len(pre))'),
]
for a, b in R:
    assert s.count(a) == 1, (a[:70], s.count(a))
    s = s.replace(a, b)
open(T + r"\verify_xlsx_v35.py", "w", encoding="utf-8", newline="\n").write(s)
print("verifier written")
