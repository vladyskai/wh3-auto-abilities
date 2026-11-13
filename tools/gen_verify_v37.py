#!/usr/bin/env python3
"""Write tools/verify_xlsx_v37.py from verify_xlsx_v36.py (round 146)."""
T = r"C:\Users\vlady\Desktop\WH3_mod\tools"
s = open(T + r"\verify_xlsx_v36.py", encoding="utf-8").read()
ADD = ('import gen_blob_tables as _GB37\n'
       '_K37 = _GB37.keys_in(open(r"C:/Users/vlady/Desktop/WH3_mod/mod_source/script/battle/mod/zz_test_deadly_onslaught.lua", '
       'encoding="utf-8").read())\n'
       'assert len(_K37) == 77, len(_K37)\n'
       'EXPECT.update({k: "enemy_blob" for k in _K37})\n')
R = [
    (r'docs\WH3_abilities_master_v36_2026-11-13.xlsx"', r'docs\WH3_abilities_master_v37_2026-11-13.xlsx"'),
    (r'PREV = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v35_2026-11-13.xlsx"',
     r'PREV = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v36_2026-11-13.xlsx"'),
    (r"backups\round144\pre_v36_workbook_md5.txt", r"backups\round146\pre_v37_workbook_md5.txt"),
    ('PACK_MD5 = "826ef8834fbc437c35ecc86a298b931e"', 'PACK_MD5 = "1d2b92d73019956836328a35dd2ade5c"'),
    ("KEEP_GATES = {", ADD + "KEEP_GATES = {"),
    ('"A1: %d rows in v36, %d in v35"', '"A1: %d rows in v37, %d in v36"'),
    ("check(len(impl_rows) == 777 and len(impl_keys) == 777,", "check(len(impl_rows) == 854 and len(impl_keys) == 854,"),
    ("check(len(entries) == 722 and len(mod_keys) == 777,", "check(len(entries) == 799 and len(mod_keys) == 854,"),
    ("te = [cell(r, 3) for r in range(44, 117)]", "te = [cell(r, 3) for r in range(44, 118)]"),
    ("tk = [cell(r, 4) for r in range(44, 117)]", "tk = [cell(r, 4) for r in range(44, 118)]"),
    ("names = [str(cell(r, 2)) for r in range(44, 117)]", "names = [str(cell(r, 2)) for r in range(44, 118)]"),
    ('len(te) == 73 and all(isinstance(x, int) for x in te), "F1: trigger table is not 73 integer rows")',
     'len(te) == 74 and all(isinstance(x, int) for x in te), "F1: trigger table is not 74 integer rows")'),
    ("sum(te) == cell(117, 3) == 722 and sum(tk) == cell(117, 4) == 777,",
     "sum(te) == cell(118, 3) == 799 and sum(tk) == cell(118, 4) == 854,"),
    ('cell(119, 1) == "Bombardment set (COMPLETE - round 108)" and cell(121, 3) == 131, "F3: bombardment block not at row 119")',
     'cell(120, 1) == "Bombardment set (COMPLETE - round 108)" and cell(122, 3) == 131, "F3: bombardment block not at row 120")'),
    ('"melee_unwavering": 309,', '"melee_unwavering": 309, "enemy_blob": 77,'),
    ("check(cell(13, 3) == 777 and cell(14, 3) == 346,", "check(cell(13, 3) == 854 and cell(14, 3) == 269,"),
    ('startswith("DEFINITIONS - WH3 ability master v36"), "G1: title")',
     'startswith("DEFINITIONS - WH3 ability master v37"), "G1: title")'),
    ('startswith("33. ROUND 144")', 'startswith("34. ROUND 146")'),
    ('"G2: section 33 missing"', '"G2: section 34 missing"'),
    ('== "v36" and PACK_MD5', '== "v37" and PACK_MD5'),
    ('"G3: changelog v36 row or pack md5 missing"', '"G3: changelog v37 row or pack md5 missing"'),
    ("check(len(pre) == 66 and not changed,", "check(len(pre) == 68 and not changed,"),
    ('print("XLSX v36 VERIFY: %d FAILURE(S)" % len(fails))', 'print("XLSX v37 VERIFY: %d FAILURE(S)" % len(fails))'),
    ('print("XLSX v36 VERIFY OK")', 'print("XLSX v37 VERIFY OK")'),
    ("777 implemented; 27 skipped", "854 implemented; 27 skipped"),
    ("join: 722 entries / 777 keys, every family matching; trigger table 73 families / 722 / 777",
     "join: 799 entries / 854 keys, every family matching; trigger table 74 families / 799 / 854"),
    ('open batch 3 on their families")', 'the 77 blob attacks on their family")'),
    ('print("  v1-v35: %d files byte-unchanged" % len(pre))', 'print("  v1-v36: %d files byte-unchanged" % len(pre))'),
]
for a, b in R:
    assert s.count(a) == 1, (a[:70], s.count(a))
    s = s.replace(a, b)
open(T + r"\verify_xlsx_v37.py", "w", encoding="utf-8", newline="\n").write(s)
print("verifier written")
