#!/usr/bin/env python3
"""Write verify_xlsx_v68.py from verify_xlsx_v67.py (round 185): every v67 target re-pointed at v68, 988 entries / 1,041
keys, implemented 1,041 / not implemented 82, 62 skipped, the 140-family table (the TOTAL at row 184, the bombardment
block at 186), melee_unwavering 281, the Cards / workbook reads on the v68 module, the round-185 rows expected on their
families, and the round-185 row checks appended (33 built, 12 closed)."""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\tools\verify_xlsx_v67.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\tools\verify_xlsx_v68.py"
R = [
    ('"""Verify docs/WH3_abilities_master_v67_2026-11-20.xlsx (round 184; cloned from the v66 verifier)',
     '"""Verify docs/WH3_abilities_master_v68_2026-11-20.xlsx (round 185; cloned from the v67 verifier)', 1),
    ('SUB = [("v49_2026-11-17", "v67_2026-11-20"), ("v48_2026-11-16", "v66_2026-11-20"),',
     'SUB = [("v49_2026-11-17", "v68_2026-11-20"), ("v48_2026-11-16", "v67_2026-11-20"),', 1),
    ("""('"melee_unwavering": 299', '"melee_unwavering": 268')""", """('"melee_unwavering": 299', '"melee_unwavering": 281')""", 1),
    ('("len(impl_rows) == 1003 and len(impl_keys) == 1003", "len(impl_rows) == 1008 and len(impl_keys) == 1008")',
     '("len(impl_rows) == 1003 and len(impl_keys) == 1003", "len(impl_rows) == 1041 and len(impl_keys) == 1041")', 1),
    ("""'== "SKIPPED (user decision)") == 50, "B5: skipped count is not 50")'""",
     """'== "SKIPPED (user decision)") == 62, "B5: skipped count is not 62")'""", 1),
    ('"check(len(entries) == 955 and len(mod_keys) == 1008,"', '"check(len(entries) == 988 and len(mod_keys) == 1041,"', 1),
    ('("range(44, 139)", "range(44, 182)"), ("len(te) == 95 and", "len(te) == 138 and"), ("is not 95 integer rows", "is not 138 integer rows"),',
     '("range(44, 139)", "range(44, 184)"), ("len(te) == 95 and", "len(te) == 140 and"), ("is not 95 integer rows", "is not 140 integer rows"),', 1),
    ('"cell(182, 3) == 955 and sum(tk) == cell(182, 4) == 1008"', '"cell(184, 3) == 988 and sum(tk) == cell(184, 4) == 1041"', 1),
    ('"cell(184, 1) == \\"Bombardment set (COMPLETE - round 108)\\" and cell(186, 3) == 131"',
     '"cell(186, 1) == \\"Bombardment set (COMPLETE - round 108)\\" and cell(188, 3) == 131"', 1),
    ('"bombardment block not at row 184"', '"bombardment block not at row 186"', 1),
    ('"cell(13, 3) == 1008 and cell(14, 3) == 115"', '"cell(13, 3) == 1041 and cell(14, 3) == 82"', 1),
    ('"1008 implemented; 50 skipped"', '"1041 implemented; 62 skipped"', 1),
    ('"955 entries / 1008 keys, every family matching; trigger table 138 families / 955 / 1008"',
     '"988 entries / 1041 keys, every family matching; trigger table 140 families / 988 / 1041"', 1),
    ('"round184\\\\pre_v67_workbook_md5"', '"round185\\\\pre_v68_workbook_md5"', 1),
    ('"18aac090ab99114b1ac3c83eb483dd8c"', '"0779eb3ef6eaf41e929b86d890270e4e"', 1),
    ('"rows in v67, %d in v66"', '"rows in v68, %d in v67"', 1), ('"master v67"', '"master v68"', 1),
    ('"64. ROUND 184"', '"65. ROUND 185"', 1), ('"section 64"', '"section 65"', 1), ("""'"v67" and'""", """'"v68" and'""", 1),
    ('"changelog v67"', '"changelog v68"', 1), ('"== 128 and"', '"== 130 and"', 1), ('"XLSX v67"', '"XLSX v68"', 1),
    ('"v1-v66"', '"v1-v67"', 1),
    # the family counts the v38 base pins: self_last_stand 2 -> 3 (the Black Gem of Gnar), enemy_fast_near_ally 19 -> 20
    # (Mirror of Knowledge), self_recharging 5 -> 6 (Mad Cap Mushrooms), charge_only 4 -> 5 (Swiftness of Itzl)
    ("""R.append(('"self_last_stand": 1,', '"self_last_stand": 2,', 1))""",
     """R.append(('"self_last_stand": 1,', '"self_last_stand": 3,', 1))   # round 185: + the Black Gem of Gnar
R.append(('"self_recharging": 5,', '"self_recharging": 6,', 1))   # round 185: + Mad Cap Mushrooms
R.append(('"charge_only": 4,', '"charge_only": 5,', 1))   # round 185: + Swiftness of Itzl""", 1),
    ("""'"enemy_fast_near_ally": 9', '"enemy_fast_near_ally": 19'""", """'"enemy_fast_near_ally": 9', '"enemy_fast_near_ally": 20'""", 1),
    ("""          'import make_xlsx_v67 as _M184\\n'
          'EXPECT.update(_M184.FAMILY)\\n', 1))""",
     """          'import make_xlsx_v67 as _M184\\n'
          'EXPECT.update(_M184.FAMILY)\\n'
          'import make_xlsx_v68 as _M185\\n'
          'EXPECT.update(_M185.FAMILY)\\n', 1))""", 1),
    ("import make_xlsx_v67 as M67  # noqa: E402   (round 184: the v67 module: RUN and DST)",
     "import make_xlsx_v67 as M67  # noqa: E402   (round 184: its rows)\n"
     "import make_xlsx_v68 as M68  # noqa: E402   (round 185: the v68 module: RUN and DST)", 1),
    ("for line in open(M67.RUN, encoding=\"utf-8\"):", "for line in open(M68.RUN, encoding=\"utf-8\"):", 1),
    ("wb = openpyxl.load_workbook(M67.DST, read_only=True)", "wb = openpyxl.load_workbook(M68.DST, read_only=True)", 1),
    ("the harness-183 run", "the harness-184 run", 1),
    ("good = (len(rows) == 955 and same == 955 and whole == 955 and", "good = (len(rows) == 988 and same == 988 and whole == 988 and", 1),
    ('print("XLSX v67 VERIFY OK" if good else "XLSX v67 VERIFY: round-184 checks FAILED")',
     '''print("XLSX v67 rows still right" if good else "XLSX v67 rows: FAILED")
# round 185: the rule-shut review rows 20-64: 33 IMPLEMENTED on their ruled family with their text, 12 closed
nw185 = sum(1 for k, f in M68.FAMILY.items() if by1[k][19] == "IMPLEMENTED" and by1[k][20] == f
            and by1[k][21] == M68.text_of(k))
cl185 = sum(1 for k in M68.CLOSED if by1[k][19] == "SKIPPED (user decision)" and by1[k][20] == "-"
            and by1[k][18] == M68.closed_reason(k))
print("round 185: new rows %d / %d; closed rows %d / %d" % (nw185, len(M68.FAMILY), cl185, len(M68.CLOSED)))
good = good and nw185 == len(M68.FAMILY) == 33 and cl185 == len(M68.CLOSED) == 12
print("XLSX v68 VERIFY OK" if good else "XLSX v68 VERIFY: round-185 checks FAILED")''', 1),
]
s = open(SRC, encoding="utf-8").read()
for a, b, n in R:
    assert s.count(a) == n, (a[:80], s.count(a))
    s = s.replace(a, b)
open(DST, "w", encoding="utf-8", newline="\n").write(s)
print("wrote", DST)
