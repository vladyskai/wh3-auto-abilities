#!/usr/bin/env python3
"""Write verify_xlsx_v61.py from verify_xlsx_v60.py (round 178): every v60 target re-pointed at v61, the counts the
round-178 moves change, and the round-178 row checks appended to the tail."""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\tools\verify_xlsx_v60.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\tools\verify_xlsx_v61.py"
R = [
    ('"""Verify docs/WH3_abilities_master_v60_2026-11-18.xlsx (round 177; cloned from the v59 verifier)',
     '"""Verify docs/WH3_abilities_master_v61_2026-11-18.xlsx (round 178; cloned from the v60 verifier)', 1),
    ('("v49_2026-11-17", "v60_2026-11-18"), ("v48_2026-11-16", "v59_2026-11-18")',
     '("v49_2026-11-17", "v61_2026-11-18"), ("v48_2026-11-16", "v60_2026-11-18")', 1),
    ('"check(len(entries) == 937 and len(mod_keys) == 992,"', '"check(len(entries) == 938 and len(mod_keys) == 992,"', 1),
    ('("range(44, 139)", "range(44, 164)")', '("range(44, 139)", "range(44, 167)")', 1),
    ('("len(te) == 95 and", "len(te) == 120 and"), ("is not 95 integer rows", "is not 120 integer rows")',
     '("len(te) == 95 and", "len(te) == 123 and"), ("is not 95 integer rows", "is not 123 integer rows")', 1),
    ('("\\"enemy_blob\\": 77", "\\"enemy_blob\\": 71")', '("\\"enemy_blob\\": 77", "\\"enemy_blob\\": 69")', 0),
    ("""('"enemy_blob": 77', '"enemy_blob": 71'), ('"enemy_engaged_or_shot": 46', '"enemy_engaged_or_shot": 37'),""",
     """('"enemy_blob": 77', '"enemy_blob": 69'), ('"enemy_engaged_or_shot": 46', '"enemy_engaged_or_shot": 22'),""", 1),
    ("""('"enemy_melee": 35', '"enemy_melee": 34'),""", """('"enemy_melee": 35', '"enemy_melee": 35'),""", 1),
    ('"cell(164, 3) == 937 and sum(tk) == cell(164, 4) == 992"', '"cell(167, 3) == 938 and sum(tk) == cell(167, 4) == 992"', 1),
    ('"cell(166, 1) == \\"Bombardment set (COMPLETE - round 108)\\" and cell(168, 3) == 131"',
     '"cell(169, 1) == \\"Bombardment set (COMPLETE - round 108)\\" and cell(171, 3) == 131"', 1),
    ('"bombardment block not at row 166"', '"bombardment block not at row 169"', 1),
    ('"937 entries / 992 keys, every family matching; trigger table 120 families / 937 / 992"',
     '"938 entries / 992 keys, every family matching; trigger table 123 families / 938 / 992"', 1),
    ('"round177\\\\pre_v60_workbook_md5"', '"round178\\\\pre_v61_workbook_md5"', 1),
    ('"9efbf06698578da06329293ecdaee9b5"', '"b8622a7b2b6c9bb6ed1c8c5844cac5bf"', 1),
    # round 178: the 6 plain roots (rows 36-41) joined enemy_fast_near_ally (9 -> 15)
    ("""('"melee_unwavering": 299', '"melee_unwavering": 265'),""",
     """('"melee_unwavering": 299', '"melee_unwavering": 265'), ('"enemy_fast_near_ally": 9', '"enemy_fast_near_ally": 15'),""", 1),
    ('"rows in v60, %d in v59"', '"rows in v61, %d in v60"', 1), ('"master v60"', '"master v61"', 1),
    ('"57. ROUND 177"', '"58. ROUND 178"', 1), ('"section 57"', '"section 58"', 1), ("""'"v60" and'""", """'"v61" and'""", 1),
    ('"changelog v60"', '"changelog v61"', 1), ('"== 114 and"', '"== 116 and"', 1), ('"XLSX v60"', '"XLSX v61"', 1),
    ('"v1-v59"', '"v1-v60"', 1),
    # round 178: The Soulstealer left enemy_ground_melee (75 -> 74 entries)
    ("""('"melee_unwavering": 299', '"melee_unwavering": 265'),""",
     """('"melee_unwavering": 299', '"melee_unwavering": 265'), ('"enemy_ground_melee": 75', '"enemy_ground_melee": 74'),""", 1),
    # round 178: 6 rows lost their class (4 spellcaster moves, the Trophy Heads Daemon Wings key, ...), Whip kept its
    # class (55 -> 50); enemy_engaged_or_shot 42 -> 26 rows (22 entries)
    ("""'== 55, "B6: the target-class rows are not 55")', 1))""", """'== 50, "B6: the target-class rows are not 50")', 1))""", 1),
    ("""'== 42, "B10: enemy_engaged_or_shot rows are not 42 (37 entries; some span two rows)")', 1))""",
     """'== 26, "B10: enemy_engaged_or_shot rows are not 26 (22 entries; some span two rows)")', 1))
# round 178: Void Pendulum targets spellcasters now (its Lord/Hero class text is gone)
R.append(('and "target class: Lord/Hero only" in str(by_key["wh3_main_item_abilities_void_pendulum"][21]),',
          'and "spellcaster" in str(by_key["wh3_main_item_abilities_void_pendulum"][21]),   # round 178', 1))""", 1),
    ("""R.append(("assert len(_K37) == 77, len(_K37)", "assert len(_K37) == 71, len(_K37)", 1))""",
     """R.append(("assert len(_K37) == 77, len(_K37)", "assert len(_K37) == 69, len(_K37)", 1))   # round 178: 69""", 1),
    ("""R.append(('"enemy_blob": 77', '"enemy_blob": 71', 1))""", """R.append(('"enemy_blob": 77', '"enemy_blob": 69', 1))""", 1),
    ("""R.append(('"enemy_engaged_or_shot": 46', '"enemy_engaged_or_shot": 37', 1))""",
     """R.append(('"enemy_engaged_or_shot": 46', '"enemy_engaged_or_shot": 22', 1))""", 1),
    ("""          'import make_xlsx_v60 as _M177\\n'
          'EXPECT.update({k: v[0] for k, v in _M177.MOVED.items()})\\n', 1))""",
     """          'import make_xlsx_v60 as _M177\\n'
          'EXPECT.update({k: v[0] for k, v in _M177.MOVED.items()})\\n'
          'import make_xlsx_v61 as _M178\\n'
          'EXPECT.update({k: v[0] for k, v in _M178.MOVED.items()})\\n', 1))""", 1),
    ("import make_xlsx_v60 as M58  # noqa: E402   (round 177: the v60 module: RUN and DST)",
     "import make_xlsx_v60 as M60  # noqa: E402   (round 177: its moves)\n"
     "import make_xlsx_v61 as M58  # noqa: E402   (round 178: the v61 module: RUN and DST)", 1),
    ("mv177 = sum(1 for k, v in M58.MOVED.items()", "mv177 = sum(1 for k, v in M60.MOVED.items()", 1),
    ('print("round 177: moved rows %d / %d" % (mv177, len(M58.MOVED)))',
     'print("round 177: moved rows %d / %d" % (mv177, len(M60.MOVED)))', 1),
    ("mv177 == len(M58.MOVED) == 15", "mv177 == len(M60.MOVED) == 15", 1),
    ("the harness-176 run", "the harness-177 run", 1),
    ("good = (len(rows) == 937 and same == 937 and whole == 937", "good = (len(rows) == 938 and same == 938 and whole == 938", 1),
    ('print("XLSX v60 VERIFY OK" if good else "XLSX v60 VERIFY: round-177 checks FAILED")',
     '''# round 178: the 22 moved keys carry their family and text; the Trophy Heads rows are split; Eye of Khorne value-first
_old60 = {str(r[2]).split(";")[0].strip(): str(r[21] or "") for r in openpyxl.load_workbook(M58.SRC, read_only=True)["Abilities"].iter_rows(min_row=2, values_only=True)}
by1 = {str(r[2]).split(";")[0].strip(): r for r in ws.iter_rows(min_row=2, values_only=True)}
mv178 = sum(1 for k, v in M58.MOVED.items() if by1[k][19] == "IMPLEMENTED" and by1[k][20] == v[0]
            and by1[k][21] == M58.text_of(k, _old60[k]))
tr178 = (str(by[M58.TROPHY[0]][2]).strip() == M58.TROPHY[0] and str(by[M58.TROPHY[1]][2]).strip() == M58.TROPHY[1]
         and by[M58.TROPHY[1]][21] == M58.TROPHY_DW_TEXT and by[M58.TROPHY[0]][20] == by[M58.TROPHY[1]][20] == "enemy_melee")
ek178 = "highest live value" in str(by["wh3_dlc26_lord_abilities_eye_of_khorne"][21])
print("round 178: moved rows %d / %d; Trophy Heads split %s; Eye of Khorne value-first %s"
      % (mv178, len(M58.MOVED), tr178, ek178))
good = good and mv178 == len(M58.MOVED) == 22 and tr178 and ek178
print("XLSX v61 VERIFY OK" if good else "XLSX v61 VERIFY: round-178 checks FAILED")''', 1),
]
s = open(SRC, encoding="utf-8").read()
for a, b, n in R:
    assert s.count(a) == n, (a[:80], s.count(a))
    if n:
        s = s.replace(a, b)
open(DST, "w", encoding="utf-8", newline="\n").write(s)
print("wrote", DST)
