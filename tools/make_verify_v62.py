#!/usr/bin/env python3
"""Write verify_xlsx_v62.py from verify_xlsx_v61.py (round 179): every v61 target re-pointed at v62, the counts the
round-179 moves change, the Cards / workbook reads on the v62 module, and the round-179 row checks appended."""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\tools\verify_xlsx_v61.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\tools\verify_xlsx_v62.py"
R = [
    ('"""Verify docs/WH3_abilities_master_v61_2026-11-18.xlsx (round 178; cloned from the v60 verifier)',
     '"""Verify docs/WH3_abilities_master_v62_2026-11-18.xlsx (round 179; cloned from the v61 verifier)', 1),
    ('SUB = [("v49_2026-11-17", "v61_2026-11-18"), ("v48_2026-11-16", "v60_2026-11-18"),',
     'SUB = [("v49_2026-11-17", "v62_2026-11-18"), ("v48_2026-11-16", "v61_2026-11-18"), (\'"melee_self_or_ally": 1\', \'"melee_self_or_ally": 2\'),', 1),
    ('("range(44, 139)", "range(44, 167)"), ("len(te) == 95 and", "len(te) == 123 and"), ("is not 95 integer rows", "is not 123 integer rows"),',
     '("range(44, 139)", "range(44, 173)"), ("len(te) == 95 and", "len(te) == 129 and"), ("is not 95 integer rows", "is not 129 integer rows"),', 1),
    ('"cell(167, 3) == 938 and sum(tk) == cell(167, 4) == 992"', '"cell(173, 3) == 938 and sum(tk) == cell(173, 4) == 992"', 1),
    ('"cell(169, 1) == \\"Bombardment set (COMPLETE - round 108)\\" and cell(171, 3) == 131"',
     '"cell(175, 1) == \\"Bombardment set (COMPLETE - round 108)\\" and cell(177, 3) == 131"', 1),
    ('"bombardment block not at row 169"', '"bombardment block not at row 175"', 1),
    ("trigger table 123 families / 938 / 992", "trigger table 129 families / 938 / 992", 1),
    ('"round178\\\\pre_v61_workbook_md5"', '"round179\\\\pre_v62_workbook_md5"', 1),
    ('"b8622a7b2b6c9bb6ed1c8c5844cac5bf"', '"d7588fbfd32a951c9c65b4b1b052c284"', 1),
    ('"rows in v61, %d in v60"', '"rows in v62, %d in v61"', 1), ('"master v61"', '"master v62"', 1),
    ('"58. ROUND 178"', '"59. ROUND 179"', 1), ('"section 58"', '"section 59"', 1), ("""'"v61" and'""", """'"v62" and'""", 1),
    ('"changelog v61"', '"changelog v62"', 1), ('"== 116 and"', '"== 118 and"', 1), ('"XLSX v61"', '"XLSX v62"', 1),
    ('"v1-v60"', '"v1-v61"', 1),
    ("""R.append(('"self_last_stand": 1,', '"self_last_stand": 2,', 1))""",
     """R.append(('"self_last_stand": 1,', '"self_last_stand": 2,', 1))
R.append(('"melee_self_or_ally": 1,', '"melee_self_or_ally": 2,', 1))   # round 179: Favour of the Fay""", 1),
    ("""          'import make_xlsx_v61 as _M178\\n'
          'EXPECT.update({k: v[0] for k, v in _M178.MOVED.items()})\\n', 1))""",
     """          'import make_xlsx_v61 as _M178\\n'
          'EXPECT.update({k: v[0] for k, v in _M178.MOVED.items()})\\n'
          'import make_xlsx_v62 as _M179\\n'
          'EXPECT.update({k: v[0] for k, v in _M179.MOVED.items()})\\n', 1))""", 1),
    ("import make_xlsx_v61 as M58  # noqa: E402   (round 178: the v61 module: RUN and DST)",
     "import make_xlsx_v61 as M58  # noqa: E402   (round 178: its moves)\n"
     "import make_xlsx_v62 as M62  # noqa: E402   (round 179: the v62 module: RUN and DST)", 1),
    ("for line in open(M58.RUN, encoding=\"utf-8\"):", "for line in open(M62.RUN, encoding=\"utf-8\"):", 1),
    ("wb = openpyxl.load_workbook(M58.DST, read_only=True)", "wb = openpyxl.load_workbook(M62.DST, read_only=True)", 1),
    ("the harness-177 run", "the harness-178 run", 1),
    ('print("XLSX v61 VERIFY OK" if good else "XLSX v61 VERIFY: round-178 checks FAILED")',
     '''# round 179: the 12 moved keys and the 3 same-family keys carry their family and text
_old61 = {str(r[2]).split(";")[0].strip(): str(r[21] or "") for r in openpyxl.load_workbook(M62.SRC, read_only=True)["Abilities"].iter_rows(min_row=2, values_only=True)}
_all179 = dict((k, v[0]) for k, v in M62.MOVED.items())
_all179.update((k, v[0]) for k, v in M62.SAME.items())
mv179 = sum(1 for k, f in _all179.items() if by1[k][19] == "IMPLEMENTED" and by1[k][20] == f
            and by1[k][21] == M62.text_of(k, _old61[k]))
print("round 179: moved / re-ruled rows %d / %d" % (mv179, len(_all179)))
good = good and mv179 == len(_all179) == 15
print("XLSX v62 VERIFY OK" if good else "XLSX v62 VERIFY: round-179 checks FAILED")''', 1),
]
s = open(SRC, encoding="utf-8").read()
for a, b, n in R:
    assert s.count(a) == n, (a[:80], s.count(a))
    s = s.replace(a, b)
open(DST, "w", encoding="utf-8", newline="\n").write(s)
print("wrote", DST)
