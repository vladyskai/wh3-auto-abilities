#!/usr/bin/env python3
"""Round 180: the harness-179 section and generator follow the Land Mine revert (row 98 not shipped), Foe-Seeker's legacy
badge (zz_auto_badge_fs) and the mock's ammo read (it needs ammo_start AND ammo_seq)."""
P = r"C:\Users\vlady\Desktop\WH3_mod\tools\h179_section.lua"
G = r"C:\Users\vlady\Desktop\WH3_mod\tools\make_harness179.py"
s = open(P, encoding="utf-8").read()
R = [
    ("--   LM1 Land Mine: in melee inside a 240-man block, no friend near -> ONE cast (RED: same).\n"
     "--   LM2 Land Mine: in melee against a 12-man unit -> no cast (half a packed block = 66 soldiers; RED: one).\n", ""),
    ("--   0zz28 the 5 new families wired, the moves,", "--   0zz28 the 4 new families wired, the moves (Land Mine NOT moved: row 98 waits),"),
    ("--   CA8 the cards of the 5 new families and the 2 re-ruled ones.", "--   CA8 the cards of the 4 new families and the 2 re-ruled ones."),
    ('      for _, fam in ipairs({ "melee_clear_block", "health_aura_ally_rule", "self_heal_clear", "self_hurt_attacked",\n'
     '                             "charge_or_tired" }) do',
     '      for _, fam in ipairs({ "health_aura_ally_rule", "self_heal_clear", "self_hurt_attacked", "charge_or_tired" }) do'),
    ('check("0zz28 " .. f.name .. ": 5 families wired (" .. wired .. "), 14 moved,',
     'check("0zz28 " .. f.name .. ": 4 families wired (" .. wired .. "), 13 moved, Land Mine kept,'),
    ('        wired == 5 and cp(s, "-- ROUND 180 (score-3 review): ") == 14 and',
     '        wired == 4 and cp(s, "-- ROUND 180 (score-3 review): ") == 13 and cp(s, "melee_clear_block") == 0 and'),
    ('    { "LM1. Land Mine: in melee inside a 240-man block, no friend near -> ONE cast",\n'
     '      function(b) return { caster(b, K.LM, { melee = true }) },\n'
     '        { enemy(b + 5, SW, { pos = { 0, 0, 0 }, melee = true, men_alive = 240, initial_men = 240 }) } end,\n'
     '      "land_mine", K.LM, 1, nil, "same" },\n'
     '    { "LM2. Land Mine: in melee against a 12-man unit -> no cast",\n'
     '      function(b) return { caster(b, K.LM, { melee = true }) },\n'
     '        { enemy(b + 5, SW, { pos = { 0, 0, 0 }, melee = true, men_alive = 12, initial_men = 12, width = 6 }) } end,\n'
     '      "land_mine", K.LM, 0, nil, "one" },\n', ''),
    ('end, "foe_seeker", K.FS, 1, nil, "none" },', 'end, "fs", K.FS, 1, nil, "none" },   -- the legacy badge zz_auto_badge_fs'),
    ("{ health_percent = 40, ammo_seq = { 0 } }", "{ health_percent = 40, ammo_start = 10, ammo_seq = { 0 } }"),
    ("{ health_percent = 90, ammo_seq = { 0 } }", "{ health_percent = 90, ammo_start = 10, ammo_seq = { 0 } }"),
    ('          local c_ok = by.land_mine == "Fires in melee unless wavering, clear of allies, on a packed enemy block"\n'
     '            and by.blood_chalice_of_bathori',
     '          local c_ok = by.land_mine == "Fires in melee unless wavering, clear of allies"\n'
     '            and by.blood_chalice_of_bathori'),
    ('"CA8: the cards of the 5 new families', '"CA8: the cards of the 4 new families'),
    ("      n_all == 46 and n_ok == 46)\n  else\n    check(\"HARNESS 179: every check behaved - \" .. n_ok .. \"/\" .. n_all, n_all == 46 and n_ok == 46)",
     "      n_all == 42 and n_ok == 42)\n  else\n    check(\"HARNESS 179: every check behaved - \" .. n_ok .. \"/\" .. n_all, n_all == 42 and n_ok == 42)"),
]
for a, b in R:
    assert s.count(a) == 1, ("sec", a[:70], s.count(a))
    s = s.replace(a, b)
open(P, "w", encoding="utf-8", newline="\n").write(s)
g = open(G, encoding="utf-8").read()
RG = [
    ("    '    melee_clear_block = \"When armed, fires in melee when none of our other units is inside its blast and the blast covers half a packed block of enemies\",\\n'\n", ""),
    ("""    (\"\"\"'trigger = "melee_clear"') == 5\"\"\", \"\"\"'trigger = "melee_clear"') == 4\"\"\", 1),   # Land Mine\n""", ""),
    ("-- HARNESS 179 - ROUND 180: THE SCORE-3 REVIEW, ROWS 87-114 AND 128 (5 new families, 14 entries",
     "-- HARNESS 179 - ROUND 180: THE SCORE-3 REVIEW, ROWS 87-114 AND 128 (4 new families, 13 entries"),
]
for a, b in RG:
    assert g.count(a) == 1, ("gen", a[:70], g.count(a))
    g = g.replace(a, b)
open(G, "w", encoding="utf-8", newline="\n").write(g)
print("fixed")
