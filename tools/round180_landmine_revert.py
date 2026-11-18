#!/usr/bin/env python3
"""Round 180: NOT shipping review row 98 (Land Mine, "improve"). The doc's option ("half a packed block of enemies inside
the blast") was written for 5-10 m blasts; Land Mine's blast in the game data (VORTEX_R) is 25 m, so the line is
round(0.5 x pi x 25^2 / 2.368) = 415 soldiers: it would almost never fire. Land Mine stays on melee_clear; the user gets
options. This removes melee_clear_block (entry, evaluator, wiring, label, card) from both copies."""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"
R = [
    ('\t-- ROUND 180 (score-3 review): melee_clear_block\n\t{ marker = "land_mine", name = "Land Mine", trigger = "melee_clear_block",',
     '\t{ marker = "land_mine", name = "Land Mine", trigger = "melee_clear",'),
    ('--   melee_clear_block (Land Mine, "improve"): melee_clear, and at least half a packed block of enemy soldiers inside\n'
     '--     the blast centred on the caster (BLOB_FRACTION x pi r^2 / PACKED_M2), so 3 charges do not go into one small fight.\n',
     ''),
    ('\tmelee_clear_block = FOURTH.evaluate_melee_clear_block,   -- ROUND 180\n\thealth_aura_ally_rule = FOURTH.evaluate_health_aura_ally_rule,\n',
     '\thealth_aura_ally_rule = FOURTH.evaluate_health_aura_ally_rule,   -- ROUND 180\n'),
    ('\tmelee_clear_block = "When armed, fires in melee when none of our other units is inside its blast and the blast covers half a packed block of enemies",   -- ROUND 180\n'
     '\thealth_aura_ally_rule = "When armed,',
     '\thealth_aura_ally_rule = "When armed,'),
    ('\tmelee_clear_block = "Fires in melee unless wavering[, clear of allies{FF}], on a packed enemy block",   -- ROUND 180\n'
     '\thealth_aura_ally_rule = "Fires',
     '\thealth_aura_ally_rule = "Fires'),
]


def cut_fn(s, name):
    a = "function FOURTH.%s(" % name
    assert s.count(a) == 1, name
    i = s.index(a)
    j = s.index("\nend\n", i) + len("\nend\n")
    if s[j:j + 1] == "\n":
        j += 1
    return s[:i] + s[j:]


for path in (SRC, ANN):
    s = open(path, encoding="utf-8", newline="").read()
    for a, b in R:
        assert s.count(a) == 1, (path[-12:], a[:80], s.count(a))
        s = s.replace(a, b)
    s = cut_fn(s, "blast_soldiers_all")
    s = cut_fn(s, "evaluate_melee_clear_block")
    assert "melee_clear_block" not in s and "blast_soldiers_all" not in s
    open(path, "w", encoding="utf-8", newline="").write(s)
    print(path[-36:], "Land Mine reverted")
