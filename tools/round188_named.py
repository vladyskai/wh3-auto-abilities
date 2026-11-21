#!/usr/bin/env python3
"""Round 188, step 2: the three hand-named cast bounds that come from a real target_intercept_range above 66 m follow
the new rule (max(floor(real x 0.70), real - 20)): Blood Sacrifice and Eat da Runts! (100 m: 70 -> 80), Accusation
(75 m: 52 -> 55). The aura-derived constants (24 from 35 m, 38 from 55 m) and Bugman's 38 (55 m) keep their values:
there 70% is the larger. Run after round188_range_rule.py."""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"
R = [
    ("FOURTH.BLOOD_SACRIFICE_RANGE_M = 70\n",
     "FOURTH.BLOOD_SACRIFICE_RANGE_M = 80   -- ROUND 188: max(70%, 100 - 20) (was 70)\n"),
    ("FOURTH.EAT_DA_RUNTS_RANGE_M = 70\n",
     "FOURTH.EAT_DA_RUNTS_RANGE_M = 80   -- ROUND 188: max(70%, 100 - 20) (was 70)\n"),
    ("FOURTH.ACCUSATION_RANGE_M = 52\n",
     "FOURTH.ACCUSATION_RANGE_M = 55   -- ROUND 188: max(70%, 75 - 20) (was 52; see the walk note above)\n"),
]
for path in (SRC, ANN):
    s = open(path, encoding="utf-8", newline="").read()
    assert "FOURTH.RANGE_MARGIN_M = 20" in s
    for a, b in R:
        assert s.count(a) == 1, (path, a, s.count(a))
        s = s.replace(a, b)
    open(path, "w", encoding="utf-8", newline="").write(s)
    print(path.split("\\")[-1], "3 named bounds updated")
