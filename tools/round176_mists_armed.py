#!/usr/bin/env python3
"""Round 176 (harness 175): Master of Mists starts armed (A) (user, 2026-11-18: "Start it on A"). Its family
(ground_ally_before_range) does not start armed, so the entry gets start_armed = true (round 170's per-entry field). It is
not risky (no rampage, no self-damage), so the default rule arms it."""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"
OLD = ('\t{ marker = "master_of_mists", name = "Master of Mists", trigger = "ground_ally_before_range",\n'
       '\t\tbadge = "zz_auto_badge_master_of_mists",\n'
       '\t\tkeys = { "wh3_dlc27_character_abilities_master_of_mists",\n'
       '\t\t\t"wh3_dlc27_character_abilities_master_of_mists_custom" },\n'
       '\t\tally_range_real = 250,\n'
       '\t\tox = 0, oy = 0 },\n')
NEW = ('\t-- ROUND 176: starts armed (user, 2026-11-18: "Start it on A")\n'
       '\t{ marker = "master_of_mists", name = "Master of Mists", trigger = "ground_ally_before_range",\n'
       '\t\tbadge = "zz_auto_badge_master_of_mists",\n'
       '\t\tkeys = { "wh3_dlc27_character_abilities_master_of_mists",\n'
       '\t\t\t"wh3_dlc27_character_abilities_master_of_mists_custom" },\n'
       '\t\tally_range_real = 250,\n'
       '\t\tstart_armed = true,\n'
       '\t\tox = 0, oy = 0 },\n')
for path in (SRC, ANN):
    s = open(path, encoding="utf-8", newline="").read()
    assert s.count(OLD) == 1, path
    s = s.replace(OLD, NEW)
    open(path, "w", encoding="utf-8", newline="").write(s)
    print(path[-30:], "patched;", s.count("\t\tstart_armed = true,\n"), "plain start_armed lines")
