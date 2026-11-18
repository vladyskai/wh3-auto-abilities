#!/usr/bin/env python3
"""Write verify_xlsx_v63.py from verify_xlsx_v62.py (round 180): every v62 target re-pointed at v63, the counts the
round-180 moves and closures change, the Cards / workbook reads on the v63 module, the closed keys out of EXPECT, and
the round-180 row checks appended."""
import re

SRC = r"C:\Users\vlady\Desktop\WH3_mod\tools\verify_xlsx_v62.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\tools\verify_xlsx_v63.py"
R = [
    ('"""Verify docs/WH3_abilities_master_v62_2026-11-18.xlsx (round 179; cloned from the v61 verifier)',
     '"""Verify docs/WH3_abilities_master_v63_2026-11-18.xlsx (round 180; cloned from the v62 verifier)', 1),
    ('SUB = [("v49_2026-11-17", "v62_2026-11-18"), ("v48_2026-11-16", "v61_2026-11-18"),',
     'SUB = [("v49_2026-11-17", "v63_2026-11-18"), ("v48_2026-11-16", "v62_2026-11-18"),', 1),
    ('"len(impl_rows) == 992 and len(impl_keys) == 992"', '"len(impl_rows) == 989 and len(impl_keys) == 989"', 1),
    ("""'== "SKIPPED (user decision)") == 47, "B5: skipped count is not 47")'""",
     """'== "SKIPPED (user decision)") == 50, "B5: skipped count is not 50")'""", 1),
    ('"check(len(entries) == 938 and len(mod_keys) == 992,"', '"check(len(entries) == 935 and len(mod_keys) == 989,"', 1),
    ('("range(44, 139)", "range(44, 173)"), ("len(te) == 95 and", "len(te) == 129 and"), ("is not 95 integer rows", "is not 129 integer rows"),',
     '("range(44, 139)", "range(44, 177)"), ("len(te) == 95 and", "len(te) == 133 and"), ("is not 95 integer rows", "is not 133 integer rows"),', 1),
    ('"cell(173, 3) == 938 and sum(tk) == cell(173, 4) == 992"', '"cell(177, 3) == 935 and sum(tk) == cell(177, 4) == 989"', 1),
    ('"cell(175, 1) == \\"Bombardment set (COMPLETE - round 108)\\" and cell(177, 3) == 131"',
     '"cell(179, 1) == \\"Bombardment set (COMPLETE - round 108)\\" and cell(181, 3) == 131"', 1),
    ('"bombardment block not at row 175"', '"bombardment block not at row 179"', 1),
    ('"cell(13, 3) == 992 and cell(14, 3) == 131"', '"cell(13, 3) == 989 and cell(14, 3) == 134"', 1),
    ('"992 implemented; 47 skipped"', '"989 implemented; 50 skipped"', 1),
    ('"938 entries / 992 keys, every family matching; trigger table 129 families / 938 / 992"',
     '"935 entries / 989 keys, every family matching; trigger table 133 families / 935 / 989"', 1),
    ('"round179\\\\pre_v62_workbook_md5"', '"round180\\\\pre_v63_workbook_md5"', 1),
    ('"d7588fbfd32a951c9c65b4b1b052c284"', '"6fbdf834e0a2e7cee83d529d7a3c3700"', 1),
    ('"rows in v62, %d in v61"', '"rows in v63, %d in v62"', 1), ('"master v62"', '"master v63"', 1),
    ('"59. ROUND 179"', '"60. ROUND 180"', 1), ('"section 59"', '"section 60"', 1), ("""'"v62" and'""", """'"v63" and'""", 1),
    ('"changelog v62"', '"changelog v63"', 1), ('"== 118 and"', '"== 120 and"', 1), ('"XLSX v62"', '"XLSX v63"', 1),
    ('"v1-v61"', '"v1-v62"', 1),
    # the counts the round-180 moves change
    ("""R.append(('"when_ready": 21', '"when_ready": 22', 1))""", """R.append(('"when_ready": 21', '"when_ready": 20', 1))   # round 180: 2 closed""", 1),
    ("""R.append(('"melee_self_or_ally": 1,', '"melee_self_or_ally": 2,', 1))""",
     """R.append(('"melee_self_or_ally": 1,', '"melee_self_or_ally": 3,', 1))   # round 180: + Shield of Thorns""", 1),
    ("""('"enemy_fast_near_ally": 9', '"enemy_fast_near_ally": 15')""", """('"enemy_fast_near_ally": 9', '"enemy_fast_near_ally": 19'), ('"charge_or_melee": 37', '"charge_or_melee": 36')""", 1),
    # the closed keys leave EXPECT after the winds list fills it
    ("for a, b, n in R:\n    assert V38.count(a) == n,",
     "R.append(('EXPECT.update({k: \"when_ready\" for k in _R150.WINDS})\\n',\n"
     "          'EXPECT.update({k: \"when_ready\" for k in _R150.WINDS})\\n'\n"
     "          'import make_xlsx_v63 as _M180c\\n'\n"
     "          'EXPECT = {k: v for k, v in EXPECT.items() if k not in _M180c.CLOSED}   # round 180: closed\\n', 1))\n"
     "for a, b, n in R:\n    assert V38.count(a) == n,", 1),
    ("""          'import make_xlsx_v62 as _M179\\n'
          'EXPECT.update({k: v[0] for k, v in _M179.MOVED.items()})\\n', 1))""",
     """          'import make_xlsx_v62 as _M179\\n'
          'EXPECT.update({k: v[0] for k, v in _M179.MOVED.items()})\\n'
          'import make_xlsx_v63 as _M180\\n'
          'EXPECT.update(_M180.FAMILY)\\n'
          'EXPECT = {k: v for k, v in EXPECT.items() if k not in _M180.CLOSED}\\n', 1))""", 1),
    ("import make_xlsx_v62 as M62  # noqa: E402   (round 179: the v62 module: RUN and DST)",
     "import make_xlsx_v62 as M62  # noqa: E402   (round 179: its moves)\n"
     "import make_xlsx_v63 as M63  # noqa: E402   (round 180: the v63 module: RUN and DST)", 1),
    ("for line in open(M62.RUN, encoding=\"utf-8\"):", "for line in open(M63.RUN, encoding=\"utf-8\"):", 1),
    ("wb = openpyxl.load_workbook(M62.DST, read_only=True)", "wb = openpyxl.load_workbook(M63.DST, read_only=True)", 1),
    ("the harness-178 run", "the harness-179 run", 1),
    ("good = (len(rows) == 938 and same == 938 and whole == 938", "good = (len(rows) == 935 and same == 935 and whole == 935", 1),
    # a closed row carries no note any more (Heaven's Gate had a round-165 note)
    ("and noted165 == set(M49.NOTES) and", "and noted165 == set(M49.NOTES) - set(M63.CLOSED) and", 1),
    ('print("XLSX v62 VERIFY OK" if good else "XLSX v62 VERIFY: round-179 checks FAILED")',
     '''# round 180: the moved / re-ruled rows carry their family and text; the closed rows are SKIPPED; the WW notes
_old62 = {str(r[2]).split(";")[0].strip(): str(r[21] or "") for r in openpyxl.load_workbook(M63.SRC, read_only=True)["Abilities"].iter_rows(min_row=2, values_only=True)}
mv180 = sum(1 for k, f in M63.FAMILY.items() if by1[k][19] == "IMPLEMENTED" and by1[k][20] == f
            and by1[k][21] == M63.text_of(k, _old62[k]))
cl180 = sum(1 for k in M63.CLOSED if by1[k][19] == "SKIPPED (user decision)" and by1[k][20] == "-")
ww180 = sum(1 for k in M63.WW_NOTE if by1[k][21] == M63.ww_text(k, _old62[k]))
print("round 180: moved / re-ruled rows %d / %d; closed %d / 3; WW notes %d / 5" % (mv180, len(M63.FAMILY), cl180, ww180))
good = good and mv180 == len(M63.FAMILY) == 16 and cl180 == 3 and ww180 == 5
print("XLSX v63 VERIFY OK" if good else "XLSX v63 VERIFY: round-180 checks FAILED")''', 1),
]
s = open(SRC, encoding="utf-8").read()
for a, b, n in R:
    assert s.count(a) == n, (a[:80], s.count(a))
    s = s.replace(a, b)
open(DST, "w", encoding="utf-8", newline="\n").write(s)
print("wrote", DST)
