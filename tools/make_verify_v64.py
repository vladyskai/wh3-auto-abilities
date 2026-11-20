#!/usr/bin/env python3
"""Write verify_xlsx_v64.py from verify_xlsx_v63.py (round 181): every v63 target re-pointed at v64, 936 entries, the
135-family table, the Cards / workbook reads on the v64 module, and the round-181 row checks appended."""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\tools\verify_xlsx_v63.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\tools\verify_xlsx_v64.py"
R = [
    ('"""Verify docs/WH3_abilities_master_v63_2026-11-18.xlsx (round 180; cloned from the v62 verifier)',
     '"""Verify docs/WH3_abilities_master_v64_2026-11-20.xlsx (round 181; cloned from the v63 verifier)', 1),
    ('SUB = [("v49_2026-11-17", "v63_2026-11-18"), ("v48_2026-11-16", "v62_2026-11-18"),',
     'SUB = [("v49_2026-11-17", "v64_2026-11-20"), ("v48_2026-11-16", "v63_2026-11-18"),', 1),
    ('"check(len(entries) == 935 and len(mod_keys) == 989,"', '"check(len(entries) == 936 and len(mod_keys) == 989,"', 1),
    ('("range(44, 139)", "range(44, 177)"), ("len(te) == 95 and", "len(te) == 133 and"), ("is not 95 integer rows", "is not 133 integer rows"),',
     '("range(44, 139)", "range(44, 179)"), ("len(te) == 95 and", "len(te) == 135 and"), ("is not 95 integer rows", "is not 135 integer rows"),', 1),
    ('"cell(177, 3) == 935 and sum(tk) == cell(177, 4) == 989"', '"cell(179, 3) == 936 and sum(tk) == cell(179, 4) == 989"', 1),
    ('"cell(179, 1) == \\"Bombardment set (COMPLETE - round 108)\\" and cell(181, 3) == 131"',
     '"cell(181, 1) == \\"Bombardment set (COMPLETE - round 108)\\" and cell(183, 3) == 131"', 1),
    ('"bombardment block not at row 179"', '"bombardment block not at row 181"', 1),
    ('"935 entries / 989 keys, every family matching; trigger table 133 families / 935 / 989"',
     '"936 entries / 989 keys, every family matching; trigger table 135 families / 936 / 989"', 1),
    ('"round180\\\\pre_v63_workbook_md5"', '"round181\\\\pre_v64_workbook_md5"', 1),
    ('"6fbdf834e0a2e7cee83d529d7a3c3700"', '"3e567bc557f624b8298378fb8107d156"', 1),
    ('"rows in v63, %d in v62"', '"rows in v64, %d in v63"', 1), ('"master v63"', '"master v64"', 1),
    ('"60. ROUND 180"', '"61. ROUND 181"', 1), ('"section 60"', '"section 61"', 1), ("""'"v63" and'""", """'"v64" and'""", 1),
    ('"changelog v63"', '"changelog v64"', 1), ('"== 120 and"', '"== 122 and"', 1), ('"XLSX v63"', '"XLSX v64"', 1),
    ('"v1-v62"', '"v1-v63"', 1),
    ("""          'EXPECT = {k: v for k, v in EXPECT.items() if k not in _M180.CLOSED}\\n', 1))""",
     """          'EXPECT = {k: v for k, v in EXPECT.items() if k not in _M180.CLOSED}\\n'
          'import make_xlsx_v64 as _M181\\n'
          'EXPECT.update(_M181.FAMILY)\\n', 1))""", 1),
    ("import make_xlsx_v63 as M63  # noqa: E402   (round 180: the v63 module: RUN and DST)",
     "import make_xlsx_v63 as M63  # noqa: E402   (round 180: its moves)\n"
     "import make_xlsx_v64 as M64  # noqa: E402   (round 181: the v64 module: RUN and DST)", 1),
    ("for line in open(M63.RUN, encoding=\"utf-8\"):", "for line in open(M64.RUN, encoding=\"utf-8\"):", 1),
    ("wb = openpyxl.load_workbook(M63.DST, read_only=True)", "wb = openpyxl.load_workbook(M64.DST, read_only=True)", 1),
    ("the harness-179 run", "the harness-180 run", 1),
    ("good = (len(rows) == 935 and same == 935 and whole == 935", "good = (len(rows) == 936 and same == 936 and whole == 936", 1),
    # round 180's checks compare against the v63 texts; the range-fix notes of round 181 append to rows round 180 never
    # touched, so those checks stand
    ('print("XLSX v63 VERIFY OK" if good else "XLSX v63 VERIFY: round-180 checks FAILED")',
     '''# round 181: Land Mine and Surprise Squig! carry their family and text; the range-fixed rows carry their note
_old63 = {str(r[2]).split(";")[0].strip(): str(r[21] or "") for r in openpyxl.load_workbook(M64.SRC, read_only=True)["Abilities"].iter_rows(min_row=2, values_only=True)}
mv181 = sum(1 for k, f in M64.FAMILY.items() if by1[k][19] == "IMPLEMENTED" and by1[k][20] == f
            and by1[k][21] == M64.text_of(k, _old63[k]))
nt181 = sum(1 for k in M64.NOTE if by1[k][21] == M64.note_text(k, _old63[k]))
print("round 181: moved rows %d / 2; range notes %d / %d" % (mv181, nt181, len(M64.NOTE)))
good = good and mv181 == 2 and nt181 == len(M64.NOTE) == 9
print("XLSX v64 VERIFY OK" if good else "XLSX v64 VERIFY: round-181 checks FAILED")''', 1),
]
s = open(SRC, encoding="utf-8").read()
for a, b, n in R:
    assert s.count(a) == n, (a[:80], s.count(a))
    s = s.replace(a, b)
open(DST, "w", encoding="utf-8", newline="\n").write(s)
print("wrote", DST)
