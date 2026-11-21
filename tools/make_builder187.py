#!/usr/bin/env python3
"""Build the round-187 build script from the round-186 one (the badges follow the wheel at any resolution or UI scale).

Gate rebases: see R. ROUND 187 GATE: the UI shift block (the tuned references, the 2 s interval), its call in the ui
tick, the badge and ALL offsets carrying ui_dx / ui_dy, and no new find_uicomponent call."""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261120_warpstorm_harness185\build_and_install186.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261121_uiscale_harness186\build_and_install187.py"
R = [
    # round 152's gate: the ALL badge keeps the user's tuned spot (-923, 0), now with the live UI correction added
    ('''assert "FOURTH.ALL_OX, FOURTH.ALL_OY = -923, 0" in script_txt and "st.badge:SetDockOffset(FOURTH.ALL_OX, FOURTH.ALL_OY)" in script_txt, \\''',
     '''assert "FOURTH.ALL_OX, FOURTH.ALL_OY = -923, 0" in script_txt and "st.badge:SetDockOffset(FOURTH.ALL_OX + FOURTH.ui_dx, FOURTH.ALL_OY + FOURTH.ui_dy)" in script_txt, \\''', 1),
]
ANCHOR = 'print("ROUND 186 GATE OK: Warpstorm Scroll on enemy_most_valuable (flying only, 100 m -> 70 m)")\n'
ADD = ANCHOR + r'''# ROUND 187: the badges follow the wheel at any resolution or UI scale (user 2026-11-21: "we need to fix the UI scale").
for _t187 in ("\nfunction FOURTH.ui_shift_tick()\n", "\tpcall(FOURTH.ui_shift_tick)   -- ROUND 187",
              'FOURTH.UI_WHEEL_REFS = { { "ability_parent", 42, 893 }, { "button_ability", 96, 845 } }',
              'FOURTH.UI_CENTRE_REFS = { { "orders_parent", 691, 1055 }, { "behaviour_parent", 1021, 1055 }, { "button_parent", 1072, 1052 } }',
              "FOURTH.UI_SHIFT_EVERY = 40", "FOURTH.ui_replace = replace_all_badges",
              "(slot[1] - WHEEL_TOP_X) + FOURTH.ui_dx", "BADGE_X + ability.ox + FOURTH.ui_dx"):
    assert script_txt.count(_t187) == 1, "BUILD REFUSED (round 187): missing %r" % _t187
assert script_txt.count("FOURTH.ALL_OX + FOURTH.ui_dx, FOURTH.ALL_OY + FOURTH.ui_dy") == 2 \
    and script_txt.count("SetDockOffset(FOURTH.ALL_OX, FOURTH.ALL_OY)") == 0, \
    "BUILD REFUSED (round 187): the ALL button must carry the UI shift"
_pre187 = open(r"C:\Users\vlady\Desktop\WH3_mod\docs\backups\round187\pre187_live.lua", encoding="utf-8").read()
assert script_txt.count("find_uicomponent(") == _pre187.count("find_uicomponent("), \
    "BUILD REFUSED (round 187): the UI shift must not call find_uicomponent"
print("ROUND 187 GATE OK: the badges and the ALL button follow the wheel (live shift, 2 s)")
'''
src = open(SRC, encoding="utf-8").read()
for a, b, n in R:
    assert src.count(a) == n, (a[:80], src.count(a))
    src = src.replace(a, b)
assert src.count(ANCHOR) == 1
src = src.replace(ANCHOR, ADD)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST)
