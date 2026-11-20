#!/usr/bin/env python3
"""Write verify_xlsx_v67.py from verify_xlsx_v66.py (round 184): every v66 target re-pointed at v67, 955 entries / 1,008
keys, implemented 1,008 / not implemented 115, the 138-family table (the TOTAL at row 182, the bombardment block at 184),
the Cards / workbook reads on the v67 module, the round-184 rows expected on their families, and the round-184 row checks
appended."""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\tools\verify_xlsx_v66.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\tools\verify_xlsx_v67.py"
R = [
    ('"""Verify docs/WH3_abilities_master_v66_2026-11-20.xlsx (round 183; cloned from the v65 verifier)',
     '"""Verify docs/WH3_abilities_master_v67_2026-11-20.xlsx (round 184; cloned from the v66 verifier)', 1),
    ('SUB = [("v49_2026-11-17", "v66_2026-11-20"), ("v48_2026-11-16", "v65_2026-11-20"),',
     'SUB = [("v49_2026-11-17", "v67_2026-11-20"), ("v48_2026-11-16", "v66_2026-11-20"),', 1),
    ('("len(impl_rows) == 1003 and len(impl_keys) == 1003", "len(impl_rows) == 998 and len(impl_keys) == 998")',
     '("len(impl_rows) == 1003 and len(impl_keys) == 1003", "len(impl_rows) == 1008 and len(impl_keys) == 1008")', 1),
    ('"check(len(entries) == 945 and len(mod_keys) == 998,"', '"check(len(entries) == 955 and len(mod_keys) == 1008,"', 1),
    ('("range(44, 139)", "range(44, 180)"), ("len(te) == 95 and", "len(te) == 136 and"), ("is not 95 integer rows", "is not 136 integer rows"),',
     '("range(44, 139)", "range(44, 182)"), ("len(te) == 95 and", "len(te) == 138 and"), ("is not 95 integer rows", "is not 138 integer rows"),', 1),
    ('"cell(180, 3) == 945 and sum(tk) == cell(180, 4) == 998"', '"cell(182, 3) == 955 and sum(tk) == cell(182, 4) == 1008"', 1),
    ('"cell(182, 1) == \\"Bombardment set (COMPLETE - round 108)\\" and cell(184, 3) == 131"',
     '"cell(184, 1) == \\"Bombardment set (COMPLETE - round 108)\\" and cell(186, 3) == 131"', 1),
    ('"bombardment block not at row 182"', '"bombardment block not at row 184"', 1),
    ('"cell(13, 3) == 998 and cell(14, 3) == 125"', '"cell(13, 3) == 1008 and cell(14, 3) == 115"', 1),
    ('"998 implemented; 50 skipped"', '"1008 implemented; 50 skipped"', 1),
    ('"945 entries / 998 keys, every family matching; trigger table 136 families / 945 / 998"',
     '"955 entries / 1008 keys, every family matching; trigger table 138 families / 955 / 1008"', 1),
    ('"round183\\\\pre_v66_workbook_md5"', '"round184\\\\pre_v67_workbook_md5"', 1),
    ('"bde9bc18a104768c685084b70d274fa7"', '"18aac090ab99114b1ac3c83eb483dd8c"', 1),
    ('"rows in v66, %d in v65"', '"rows in v67, %d in v66"', 1), ('"master v66"', '"master v67"', 1),
    ('"63. ROUND 183"', '"64. ROUND 184"', 1), ('"section 63"', '"section 64"', 1), ("""'"v66" and'""", """'"v67" and'""", 1),
    ('"changelog v66"', '"changelog v67"', 1), ('"== 126 and"', '"== 128 and"', 1), ('"XLSX v66"', '"XLSX v67"', 1),
    ('"v1-v65"', '"v1-v66"', 1),
    ("""          'import make_xlsx_v66 as _M183\\n'
          'EXPECT.update(_M183.FAMILY)\\n', 1))""",
     """          'import make_xlsx_v66 as _M183\\n'
          'EXPECT.update(_M183.FAMILY)\\n'
          'import make_xlsx_v67 as _M184\\n'
          'EXPECT.update(_M184.FAMILY)\\n', 1))""", 1),
    ("import make_xlsx_v66 as M66  # noqa: E402   (round 183: the v66 module: RUN and DST)",
     "import make_xlsx_v66 as M66  # noqa: E402   (round 183: its rows)\n"
     "import make_xlsx_v67 as M67  # noqa: E402   (round 184: the v67 module: RUN and DST)", 1),
    ("for line in open(M66.RUN, encoding=\"utf-8\"):", "for line in open(M67.RUN, encoding=\"utf-8\"):", 1),
    ("wb = openpyxl.load_workbook(M66.DST, read_only=True)", "wb = openpyxl.load_workbook(M67.DST, read_only=True)", 1),
    ("the harness-182 run", "the harness-183 run", 1),
    ("good = (len(rows) == 945 and same == 945 and whole == 945 and", "good = (len(rows) == 955 and same == 955 and whole == 955 and", 1),
    ('print("XLSX v66 VERIFY OK" if good else "XLSX v66 VERIFY: round-183 checks FAILED")',
     '''# round 184: the rule-shut review rows 10-19 are IMPLEMENTED on their ruled family with their text
nw184 = sum(1 for k, f in M67.FAMILY.items() if by1[k][19] == "IMPLEMENTED" and by1[k][20] == f
            and by1[k][21] == M67.text_of(k))
print("round 184: new rows %d / %d" % (nw184, len(M67.FAMILY)))
good = good and nw184 == len(M67.FAMILY) == 10
print("XLSX v67 VERIFY OK" if good else "XLSX v67 VERIFY: round-184 checks FAILED")''', 1),
]
s = open(SRC, encoding="utf-8").read()
for a, b, n in R:
    assert s.count(a) == n, (a[:80], s.count(a))
    s = s.replace(a, b)
open(DST, "w", encoding="utf-8", newline="\n").write(s)
print("wrote", DST)
