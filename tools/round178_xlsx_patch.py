#!/usr/bin/env python3
"""One-off: re-point make_xlsx_v61.py at the corrected round 178 (3 new families, 123 rows)."""
P = r"C:\Users\vlady\Desktop\WH3_mod\tools\make_xlsx_v61.py"
s = open(P, encoding="utf-8").read()
R = [
    ("(2) Numbers: the trigger table re-counted; the 2 new families appended: 120 -> 122 rows (total row 164 -> 166, the",
     "(2) Numbers: the trigger table re-counted; the 3 new families appended: 120 -> 123 rows (total row 164 -> 167, the"),
    ("    for r in range(44, 166):", "    for r in range(44, 167):"),
    ('    assert n.cell(row=166, column=2).value == "TOTAL (120 families)"\n    n.cell(row=166, column=2).value = "TOTAL (122 families)"',
     '    assert n.cell(row=167, column=2).value == "TOTAL (120 families)"\n    n.cell(row=167, column=2).value = "TOTAL (123 families)"'),
    ("    n.cell(row=166, column=3).value = sum(n.cell(row=r, column=3).value for r in range(44, 166))",
     "    n.cell(row=167, column=3).value = sum(n.cell(row=r, column=3).value for r in range(44, 167))"),
    ("    n.cell(row=166, column=4).value = sum(n.cell(row=r, column=4).value for r in range(44, 166))",
     "    n.cell(row=167, column=4).value = sum(n.cell(row=r, column=4).value for r in range(44, 167))"),
    ("    assert (n.cell(row=166, column=3).value, n.cell(row=166, column=4).value) == (938, 992)",
     "    assert (n.cell(row=167, column=3).value, n.cell(row=167, column=4).value) == (938, 992)"),
    ('    assert all(n.cell(row=r, column=3).value > 0 for r in range(44, 166)), "an empty family is listed"',
     '    assert all(n.cell(row=r, column=3).value > 0 for r in range(44, 167)), "an empty family is listed"'),
    ('    assert n.cell(row=168, column=1).value == "Bombardment set (COMPLETE - round 108)"',
     '    assert n.cell(row=169, column=1).value == "Bombardment set (COMPLETE - round 108)"'),
    ("re-counted from the mod's own ABILITIES table: 122 families / 938 entries / ",
     "re-counted from the mod's own ABILITIES table: 123 families / 938 entries / "),
    ('"992 keys. Round 178 (the score-3 review, rows 23-55): 2 NEW families; Trophy Heads split; enemy_engaged_or_shot "',
     '"992 keys. Round 178 (the score-3 review, rows 23-55): 3 NEW families; Trophy Heads split; enemy_engaged_or_shot "'),
    ("The mod: 938 entries / 992 keys / 122 trigger families.)", "The mod: 938 entries / 992 keys / 123 trigger families.)"),
    ('''           ("NEW FAMILIES", "enemy_fast_or_melee (the roots: a charging enemy first, else one in melee), "
            "enemy_fast_fire_melee (roots that open the target to missiles: fast, else under our fire, else in melee)."),''',
     '''           ("NEW FAMILIES", "enemy_fast_or_melee (Glory Seeker x2: a charging Lord or Hero first, else one in melee), "
            "enemy_fast_fire_melee (roots that open the target to missiles: fast, else under our fire, else in melee), "
            "enemy_most_models (Chain Lightning x2, The Soulstealer: the most models, counted up to the ability's own "
            "count, 16 at least)."),
           ("THE PLAIN ROOTS", "Rows 36-41 (user: 'Yes pls', no melee arm): on the existing enemy_fast_near_ally."),'''),
    ('"ROUND 178. The score-3 review, rows 23-55: 21 keys on their approved triggers, 2 new families, Trophy Heads split. "',
     '"ROUND 178. The score-3 review, rows 23-55: 22 keys on their ruled triggers, 3 new families, Trophy Heads split. "'),
    ("harness 177 full suite 7,452 checks / 0 failures.", "harness 177 full suite 7,476 checks / 0 failures."),
]
for a, b in R:
    assert s.count(a) == 1, (a[:70], s.count(a))
    s = s.replace(a, b)
open(P, "w", encoding="utf-8", newline="\n").write(s)
print("patched")
