#!/usr/bin/env python3
"""Build the round-186 build script from the round-185 one (Warpstorm Scroll as a damage dealer).

Gate rebases: see R. ROUND 186 GATE: enemy_most_valuable wired and ridden once, by Warpstorm Scroll with its flying class
and its game range."""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261120_ruleshut3_harness184\build_and_install185.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261120_warpstorm_harness185\build_and_install186.py"
R = [
    # Warpstorm Scroll left enemy_single_drain (14 -> 13)
    ("""assert script_txt.count('trigger = "enemy_single_drain"') == 14 and""",
     """assert script_txt.count('trigger = "enemy_single_drain"') == 13 and""", 1),
    # the round-184 gate's row for Warpstorm Scroll names its round-186 family
    ('    ("warpstorm_scroll", "enemy_single_drain", "wh2_main_item_abilities_warpstorm_scroll", 100, "flying"),',
     '    ("warpstorm_scroll", "enemy_most_valuable", "wh2_main_item_abilities_warpstorm_scroll", 100, "flying"),   # ROUND 186', 1),
]
ANCHOR = ('print("ROUND 185 GATE OK: 33 entries on the ruled families; 2 families wired; the 30-men floor; 2 ground keys; "\n'
          '      "the rune\'s 10 m bombardment")\n')
ADD = ANCHOR + r'''# ROUND 186: Warpstorm Scroll as a damage dealer (user 2026-11-20: "No need to enforce single-entity. No need to enforce
# charge, treat it just as a damage dealer").
assert "\tenemy_most_valuable = FOURTH.evaluate_enemy_most_valuable," in script_txt, \
    "BUILD REFUSED (round 186): enemy_most_valuable not wired"
assert script_txt.count('trigger = "enemy_most_valuable"') == 1, "BUILD REFUSED (round 186): enemy_most_valuable is not ridden once"
_i186 = script_txt.index('{ marker = "warpstorm_scroll", name = "Warpstorm Scroll", trigger = "enemy_most_valuable",')
assert '\t\trange_real = 100,\n\t\ttarget_class = "flying",\n' in script_txt[_i186:_i186 + 300], \
    "BUILD REFUSED (round 186): Warpstorm Scroll must keep the game's range and its flying-only rule"
print("ROUND 186 GATE OK: Warpstorm Scroll on enemy_most_valuable (flying only, 100 m -> 70 m)")
'''
src = open(SRC, encoding="utf-8").read()
for a, b, n in R:
    assert src.count(a) == n, (a[:80], src.count(a))
    src = src.replace(a, b)
assert src.count(ANCHOR) == 1
src = src.replace(ANCHOR, ADD)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST)
