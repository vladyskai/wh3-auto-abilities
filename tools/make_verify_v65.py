#!/usr/bin/env python3
"""Write verify_xlsx_v65.py from verify_xlsx_v64.py (round 182): every v64 target re-pointed at v65, the 136-family
table, enemy_blob 69 -> 68, the Cards / workbook reads on the v65 module, and the round-182 row checks appended."""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\tools\verify_xlsx_v64.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\tools\verify_xlsx_v65.py"
R = [
    ('"""Verify docs/WH3_abilities_master_v64_2026-11-20.xlsx (round 181; cloned from the v63 verifier)',
     '"""Verify docs/WH3_abilities_master_v65_2026-11-20.xlsx (round 182; cloned from the v64 verifier)', 1),
    ('SUB = [("v49_2026-11-17", "v64_2026-11-20"), ("v48_2026-11-16", "v63_2026-11-18"),',
     'SUB = [("v49_2026-11-17", "v65_2026-11-20"), ("v48_2026-11-16", "v64_2026-11-20"),', 1),
    ('("range(44, 139)", "range(44, 179)"), ("len(te) == 95 and", "len(te) == 135 and"), ("is not 95 integer rows", "is not 135 integer rows"),',
     '("range(44, 139)", "range(44, 180)"), ("len(te) == 95 and", "len(te) == 136 and"), ("is not 95 integer rows", "is not 136 integer rows"),', 1),
    ('"cell(179, 3) == 936 and sum(tk) == cell(179, 4) == 989"', '"cell(180, 3) == 936 and sum(tk) == cell(180, 4) == 989"', 1),
    ('"cell(181, 1) == \\"Bombardment set (COMPLETE - round 108)\\" and cell(183, 3) == 131"',
     '"cell(182, 1) == \\"Bombardment set (COMPLETE - round 108)\\" and cell(184, 3) == 131"', 1),
    ('"bombardment block not at row 181"', '"bombardment block not at row 182"', 1),
    ('"936 entries / 989 keys, every family matching; trigger table 135 families / 936 / 989"',
     '"936 entries / 989 keys, every family matching; trigger table 136 families / 936 / 989"', 1),
    ('"round181\\\\pre_v64_workbook_md5"', '"round182\\\\pre_v65_workbook_md5"', 1),
    ('"3e567bc557f624b8298378fb8107d156"', '"d4d805f72cb520f034d0928ee0522ece"', 1),
    ('"rows in v64, %d in v63"', '"rows in v65, %d in v64"', 1), ('"master v64"', '"master v65"', 1),
    ('"61. ROUND 181"', '"62. ROUND 182"', 1), ('"section 61"', '"section 62"', 1), ("""'"v64" and'""", """'"v65" and'""", 1),
    ('"changelog v64"', '"changelog v65"', 1), ('"== 122 and"', '"== 124 and"', 1), ('"XLSX v64"', '"XLSX v65"', 1),
    ('"v1-v63"', '"v1-v64"', 1),
    # the Executioner left enemy_blob (69 -> 68)
    ("""('"enemy_blob": 77', '"enemy_blob": 69'), ('"enemy_engaged_or_shot": 46', '"enemy_engaged_or_shot": 22'),""",
     """('"enemy_blob": 77', '"enemy_blob": 68'), ('"enemy_engaged_or_shot": 46', '"enemy_engaged_or_shot": 22'),""", 1),
    ("""R.append(("assert len(_K37) == 77, len(_K37)", "assert len(_K37) == 69, len(_K37)", 1))""",
     """R.append(("assert len(_K37) == 77, len(_K37)", "assert len(_K37) == 68, len(_K37)", 1))   # round 182: 68""", 1),
    ("""R.append(('"enemy_blob": 77', '"enemy_blob": 69', 1))""", """R.append(('"enemy_blob": 77', '"enemy_blob": 68', 1))""", 1),
    ("""          'import make_xlsx_v64 as _M181\\n'
          'EXPECT.update(_M181.FAMILY)\\n', 1))""",
     """          'import make_xlsx_v64 as _M181\\n'
          'EXPECT.update(_M181.FAMILY)\\n'
          'import make_xlsx_v65 as _M182\\n'
          'EXPECT.update(_M182.FAMILY)\\n', 1))""", 1),
    ("import make_xlsx_v64 as M64  # noqa: E402   (round 181: the v64 module: RUN and DST)",
     "import make_xlsx_v64 as M64  # noqa: E402   (round 181: its moves)\n"
     "import make_xlsx_v65 as M65  # noqa: E402   (round 182: the v65 module: RUN and DST)", 1),
    ("for line in open(M64.RUN, encoding=\"utf-8\"):", "for line in open(M65.RUN, encoding=\"utf-8\"):", 1),
    ("wb = openpyxl.load_workbook(M64.DST, read_only=True)", "wb = openpyxl.load_workbook(M65.DST, read_only=True)", 1),
    ("the harness-180 run", "the harness-181 run", 1),
    ('print("XLSX v64 VERIFY OK" if good else "XLSX v64 VERIFY: round-181 checks FAILED")',
     '''# round 182: the finishers carry their family and text
_old64 = {str(r[2]).split(";")[0].strip(): str(r[21] or "") for r in openpyxl.load_workbook(M65.SRC, read_only=True)["Abilities"].iter_rows(min_row=2, values_only=True)}
mv182 = sum(1 for k, f in M65.FAMILY.items() if by1[k][19] == "IMPLEMENTED" and by1[k][20] == f
            and by1[k][21] == M65.text_of(k, _old64[k]))
print("round 182: finisher rows %d / %d" % (mv182, len(M65.FAMILY)))
good = good and mv182 == len(M65.FAMILY) == 4
print("XLSX v65 VERIFY OK" if good else "XLSX v65 VERIFY: round-182 checks FAILED")''', 1),
]
s = open(SRC, encoding="utf-8").read()
for a, b, n in R:
    assert s.count(a) == n, (a[:80], s.count(a))
    s = s.replace(a, b)
open(DST, "w", encoding="utf-8", newline="\n").write(s)
print("wrote", DST)
