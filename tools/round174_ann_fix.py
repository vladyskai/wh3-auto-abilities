#!/usr/bin/env python3
"""Round 174: the reading copy has no FOURTH.shot_reason (it carries no log text; its evaluators answer true / false).
The five new shot-picker returns become 'return true' there, as its own evaluators do."""
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"
R = [
    ('\t\treturn FOURTH.shot_reason(unit, e, "most valuable large enemy", string.format("value %.0f", s))\n\tend\n'
     '\te, s = FOURTH.shot_pick(unit, m, "infantry", false)',
     '\t\treturn true\n\tend\n\te, s = FOURTH.shot_pick(unit, m, "infantry", false)'),
    ('\treturn FOURTH.shot_reason(unit, e, "no large target: most valuable enemy infantry",\n'
     '\t\tstring.format("value %.1f per soldier", s))\n', '\treturn true\n'),
    ('\treturn FOURTH.shot_reason(unit, e, "most valuable enemy spellcaster", string.format("value %.0f", s))\n',
     '\treturn true\n'),
    ('\treturn FOURTH.shot_reason(unit, e, "enemy Lord or Hero wavering or routing" .. ((s == 1) and ", in melee" or ""),\n'
     '\t\tstring.format("value %.0f", FOURTH.unit_value(e.unit)))\n', '\treturn true\n'),
    ('\treturn FOURTH.shot_reason(unit, best, "enemy spellcaster with the most spellcasters near it - on the ground under it",\n'
     '\t\tstring.format("%d spellcaster(s) within %dm, value %.0f", n, FOURTH.CLUSTER_M, v))\n', '\treturn true\n'),
]
s = open(ANN, encoding="utf-8", newline="").read()
assert "function FOURTH.shot_reason" not in s
for a, b in R:
    assert s.count(a) == 1, a[:60]
    s = s.replace(a, b)
assert "shot_reason" not in s.split("-- ROUND 174 - THE SCORE 1-2 REVIEW, ROWS 24-50", 1)[1].split("function FOURTH.evaluate_ally_routing", 1)[0]
open(ANN, "w", encoding="utf-8", newline="").write(s)
print("reading copy: 5 returns fixed")
