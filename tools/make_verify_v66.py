#!/usr/bin/env python3
"""Write verify_xlsx_v66.py from verify_xlsx_v65.py (round 183): every v65 target re-pointed at v66, 945 entries / 998
keys, implemented 998 / not implemented 125, melee_unwavering 268, the Cards / workbook reads on the v66 module, the
round-183 rows expected on their families, and the round-183 row checks appended."""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\tools\verify_xlsx_v65.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\tools\verify_xlsx_v66.py"
R = [
    ('"""Verify docs/WH3_abilities_master_v65_2026-11-20.xlsx (round 182; cloned from the v64 verifier)',
     '"""Verify docs/WH3_abilities_master_v66_2026-11-20.xlsx (round 183; cloned from the v65 verifier)', 1),
    ('SUB = [("v49_2026-11-17", "v65_2026-11-20"), ("v48_2026-11-16", "v64_2026-11-20"),',
     'SUB = [("v49_2026-11-17", "v66_2026-11-20"), ("v48_2026-11-16", "v65_2026-11-20"),', 1),
    ("""('"melee_unwavering": 299', '"melee_unwavering": 265')""", """('"melee_unwavering": 299', '"melee_unwavering": 268')""", 1),
    ('("len(impl_rows) == 1003 and len(impl_keys) == 1003", "len(impl_rows) == 989 and len(impl_keys) == 989")',
     '("len(impl_rows) == 1003 and len(impl_keys) == 1003", "len(impl_rows) == 998 and len(impl_keys) == 998")', 1),
    ('"check(len(entries) == 936 and len(mod_keys) == 989,"', '"check(len(entries) == 945 and len(mod_keys) == 998,"', 1),
    ('"cell(180, 3) == 936 and sum(tk) == cell(180, 4) == 989"', '"cell(180, 3) == 945 and sum(tk) == cell(180, 4) == 998"', 1),
    ('"cell(13, 3) == 989 and cell(14, 3) == 134"', '"cell(13, 3) == 998 and cell(14, 3) == 125"', 1),
    ('"989 implemented; 50 skipped"', '"998 implemented; 50 skipped"', 1),
    ('"936 entries / 989 keys, every family matching; trigger table 136 families / 936 / 989"',
     '"945 entries / 998 keys, every family matching; trigger table 136 families / 945 / 998"', 1),
    ('"round182\\\\pre_v65_workbook_md5"', '"round183\\\\pre_v66_workbook_md5"', 1),
    ('"d4d805f72cb520f034d0928ee0522ece"', '"bde9bc18a104768c685084b70d274fa7"', 1),
    ('"rows in v65, %d in v64"', '"rows in v66, %d in v65"', 1), ('"master v65"', '"master v66"', 1),
    ('"62. ROUND 182"', '"63. ROUND 183"', 1), ('"section 62"', '"section 63"', 1), ("""'"v65" and'""", """'"v66" and'""", 1),
    ('"changelog v65"', '"changelog v66"', 1), ('"== 124 and"', '"== 126 and"', 1), ('"XLSX v65"', '"XLSX v66"', 1),
    ('"v1-v64"', '"v1-v65"', 1),
    ("""          'import make_xlsx_v65 as _M182\\n'
          'EXPECT.update(_M182.FAMILY)\\n', 1))""",
     """          'import make_xlsx_v65 as _M182\\n'
          'EXPECT.update(_M182.FAMILY)\\n'
          'import make_xlsx_v66 as _M183\\n'
          'EXPECT.update(_M183.FAMILY)\\n', 1))""", 1),
    ("import make_xlsx_v65 as M65  # noqa: E402   (round 182: the v65 module: RUN and DST)",
     "import make_xlsx_v65 as M65  # noqa: E402   (round 182: its moves)\n"
     "import make_xlsx_v66 as M66  # noqa: E402   (round 183: the v66 module: RUN and DST)", 1),
    ("for line in open(M65.RUN, encoding=\"utf-8\"):", "for line in open(M66.RUN, encoding=\"utf-8\"):", 1),
    ("wb = openpyxl.load_workbook(M65.DST, read_only=True)", "wb = openpyxl.load_workbook(M66.DST, read_only=True)", 1),
    ("the harness-181 run", "the harness-182 run", 1),
    ("good = (len(rows) == 936 and same == 936 and whole == 936 and", "good = (len(rows) == 945 and same == 945 and whole == 945 and", 1),
    ('print("XLSX v65 VERIFY OK" if good else "XLSX v65 VERIFY: round-182 checks FAILED")',
     '''# round 183: the rule-shut review rows 1-9 are IMPLEMENTED on their ruled family with their text
nw183 = sum(1 for k, f in M66.FAMILY.items() if by1[k][19] == "IMPLEMENTED" and by1[k][20] == f
            and by1[k][21] == M66.text_of(k))
print("round 183: new rows %d / %d" % (nw183, len(M66.FAMILY)))
good = good and nw183 == len(M66.FAMILY) == 9
print("XLSX v66 VERIFY OK" if good else "XLSX v66 VERIFY: round-183 checks FAILED")''', 1),
]
s = open(SRC, encoding="utf-8").read()
for a, b, n in R:
    assert s.count(a) == n, (a[:80], s.count(a))
    s = s.replace(a, b)
open(DST, "w", encoding="utf-8", newline="\n").write(s)
print("wrote", DST)
