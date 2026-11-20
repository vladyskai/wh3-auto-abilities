#!/usr/bin/env python3
"""Round 184, step 2: Raging Tornado is a ground-only ability (unit_spec_abil: target_ground and
target_ground_under_enemies, no target_enemies), so its key joins FOURTH.enemy_ground_keys: the cast is placed on the
chosen enemy's ground (perform_special_ability_ground), never aimed at the unit (the game would refuse that). Found by
the harness-183 world RT1, which saw a unit-form cast."""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"
A = "enemy_ground_keys = {\n"
B = A + ('\t\t-- ROUND 184: Raging Tornado (target_ground only: placed under the chosen enemy in melee)\n'
         '\t\t["wh3_dlc29_unit_abilities_raging_tornado"] = true,\n')
for p in (SRC, ANN):
    s = open(p, encoding="utf-8", newline="").read()
    assert s.count(A) == 1, (p, s.count(A))
    assert '["wh3_dlc29_unit_abilities_raging_tornado"] = true,' not in s
    s = s.replace(A, B)
    open(p, "w", encoding="utf-8", newline="").write(s)
    print("ground key added:", p)
