#!/usr/bin/env python3
"""Round 173 (harness 172): close Null Stone and Rock Eye (user, 2026-11-18: "Close Null stone, Rock Eye.").
Review rows 18 and 16 of docs\\WH3_low_score_review_2026-11-17.md. Both rode melee_unwavering. Null Stone (3 uses) also
had a charge-gate hold row; a closed ability leaves no quoted key behind (the round-171/173 build gates)."""

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"
CUT = [
    '\t{ marker = "null_stone", name = "Null Stone", trigger = "melee_unwavering",\n'
    '\t\tbadge = "zz_auto_badge_null_stone",\n'
    '\t\tkeys = { "wh3_dlc27_item_abilities_null_stone" },\n'
    '\t\tox = 0, oy = 0 },\n',
    '\t{ marker = "item_passive_rock_eye", name = "Rock Eye", trigger = "melee_unwavering",\n'
    '\t\tbadge = "zz_auto_badge_item_passive_rock_eye",\n'
    '\t\tkeys = { "wh3_main_item_passive_rock_eye" },\n'
    '\t\tox = 0, oy = 0 },\n',
    '\t\t["wh3_dlc27_item_abilities_null_stone"] = 120,\n',
]
for path in (SRC, ANN):
    s = open(path, encoding="utf-8", newline="").read()
    for c in CUT:
        assert s.count(c) == 1, (path[-12:], c[:60], s.count(c))
        s = s.replace(c, "")
    open(path, "w", encoding="utf-8", newline="").write(s)
    print(path, "closed 2")
