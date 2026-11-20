#!/usr/bin/env python3
"""Write verify_xlsx_v69.py from verify_xlsx_v68.py (round 186): every v68 target re-pointed at v69, the 141-family
table (the TOTAL at row 185, the bombardment block at 187), the round-184 row check without Warpstorm Scroll (it moved
in round 186), the Cards / workbook reads on the v69 module, the round-186 row expected on its family, and the round-186
check appended."""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\tools\verify_xlsx_v68.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\tools\verify_xlsx_v69.py"
R = [
    ('"""Verify docs/WH3_abilities_master_v68_2026-11-20.xlsx (round 185; cloned from the v67 verifier)',
     '"""Verify docs/WH3_abilities_master_v69_2026-11-20.xlsx (round 186; cloned from the v68 verifier)', 1),
    ('SUB = [("v49_2026-11-17", "v68_2026-11-20"), ("v48_2026-11-16", "v67_2026-11-20"),',
     'SUB = [("v49_2026-11-17", "v69_2026-11-20"), ("v48_2026-11-16", "v68_2026-11-20"),', 1),
    ('("range(44, 139)", "range(44, 184)"), ("len(te) == 95 and", "len(te) == 140 and"), ("is not 95 integer rows", "is not 140 integer rows"),',
     '("range(44, 139)", "range(44, 185)"), ("len(te) == 95 and", "len(te) == 141 and"), ("is not 95 integer rows", "is not 141 integer rows"),', 1),
    ('"cell(184, 3) == 988 and sum(tk) == cell(184, 4) == 1041"', '"cell(185, 3) == 988 and sum(tk) == cell(185, 4) == 1041"', 1),
    ('"cell(186, 1) == \\"Bombardment set (COMPLETE - round 108)\\" and cell(188, 3) == 131"',
     '"cell(187, 1) == \\"Bombardment set (COMPLETE - round 108)\\" and cell(189, 3) == 131"', 1),
    ('"bombardment block not at row 186"', '"bombardment block not at row 187"', 1),
    ('"988 entries / 1041 keys, every family matching; trigger table 140 families / 988 / 1041"',
     '"988 entries / 1041 keys, every family matching; trigger table 141 families / 988 / 1041"', 1),
    ('"round185\\\\pre_v68_workbook_md5"', '"round186\\\\pre_v69_workbook_md5"', 1),
    ('"0779eb3ef6eaf41e929b86d890270e4e"', '"8bf23234706e1647946a84cc0e33a969"', 1),
    ('"rows in v68, %d in v67"', '"rows in v69, %d in v68"', 1), ('"master v68"', '"master v69"', 1),
    ('"65. ROUND 185"', '"66. ROUND 186"', 1), ('"section 65"', '"section 66"', 1), ("""'"v68" and'""", """'"v69" and'""", 1),
    ('"changelog v68"', '"changelog v69"', 1), ('"== 130 and"', '"== 132 and"', 1), ('"XLSX v68"', '"XLSX v69"', 1),
    ('"v1-v67"', '"v1-v68"', 1),
    ("""          'import make_xlsx_v68 as _M185\\n'
          'EXPECT.update(_M185.FAMILY)\\n', 1))""",
     """          'import make_xlsx_v68 as _M185\\n'
          'EXPECT.update(_M185.FAMILY)\\n'
          'import make_xlsx_v69 as _M186\\n'
          'EXPECT.update(_M186.FAMILY)\\n', 1))""", 1),
    ("import make_xlsx_v68 as M68  # noqa: E402   (round 185: the v68 module: RUN and DST)",
     "import make_xlsx_v68 as M68  # noqa: E402   (round 185: its rows)\n"
     "import make_xlsx_v69 as M69  # noqa: E402   (round 186: the v69 module: RUN and DST)", 1),
    ("for line in open(M68.RUN, encoding=\"utf-8\"):", "for line in open(M69.RUN, encoding=\"utf-8\"):", 1),
    ("wb = openpyxl.load_workbook(M68.DST, read_only=True)", "wb = openpyxl.load_workbook(M69.DST, read_only=True)", 1),
    ("the harness-184 run", "the harness-185 run", 1),
    # round 184's rows: Warpstorm Scroll moved in round 186, so the round-184 check covers the other 9
    ("""nw184 = sum(1 for k, f in M67.FAMILY.items() if by1[k][19] == "IMPLEMENTED" and by1[k][20] == f""",
     """nw184 = sum(1 for k, f in M67.FAMILY.items() if k not in M69.FAMILY and by1[k][19] == "IMPLEMENTED" and by1[k][20] == f""", 1),
    ("good = good and nw184 == len(M67.FAMILY) == 10", "good = good and nw184 == len(M67.FAMILY) - 1 == 9   # round 186: Warpstorm moved", 1),
    ('print("XLSX v68 VERIFY OK" if good else "XLSX v68 VERIFY: round-185 checks FAILED")',
     '''print("XLSX v68 rows still right" if good else "XLSX v68 rows: FAILED")
# round 186: Warpstorm Scroll on enemy_most_valuable with its text
nw186 = sum(1 for k, f in M69.FAMILY.items() if by1[k][19] == "IMPLEMENTED" and by1[k][20] == f
            and by1[k][21] == M69.text_of(k))
print("round 186: moved rows %d / %d" % (nw186, len(M69.FAMILY)))
good = good and nw186 == len(M69.FAMILY) == 1
print("XLSX v69 VERIFY OK" if good else "XLSX v69 VERIFY: round-186 checks FAILED")''', 1),
]
s = open(SRC, encoding="utf-8").read()
for a, b, n in R:
    assert s.count(a) == n, (a[:80], s.count(a))
    s = s.replace(a, b)
open(DST, "w", encoding="utf-8", newline="\n").write(s)
print("wrote", DST)
