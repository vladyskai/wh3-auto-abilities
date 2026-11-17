#!/usr/bin/env python3
"""Build the round-170 build script from the round-169 one (Potion of Foolhardiness on charge_or_wavering).

Gate rebases (the entry moved family, user ruling 2026-11-17 "Charge or wavering"):
  * the four melee_unwavering entry-count pins: 299 -> 298;
  * the charge_or_wavering entry-count pin: 1 -> 2.
ROUND 170 GATE: the entry rides charge_or_wavering with start_armed = true, and the default rule reads start_armed."""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261117_sensor_visibility_harness168\build_and_install169.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261117_foolhardiness_harness169\build_and_install170.py"
R = [
    ("""assert script_txt.count('trigger = "melee_unwavering"') == 299""",
     """assert script_txt.count('trigger = "melee_unwavering"') == 298""", 4),
    ("""assert script_txt.count('trigger = "charge_or_wavering"') == 1, "the charge_or_wavering entry count is not 1\"""",
     """assert script_txt.count('trigger = "charge_or_wavering"') == 2, "the charge_or_wavering entry count is not 2 (round 170)\"""", 1),
]
ANCHOR = """print("ROUND 169 GATE OK: the air drop, the 'just beyond range' read and the contact set skip hidden enemies")\n"""
ADD = ANCHOR + r'''# ROUND 170: Potion of Foolhardiness on charge_or_wavering, still armed by default (2026-11-17).
assert ('{ marker = "potion_of_foolhardiness", name = "Potion of Foolhardiness", trigger = "charge_or_wavering",\n'
        '\t\tbadge = "zz_auto_badge_potion_of_foolhardiness",\n'
        '\t\tkeys = { "wh_main_item_abilities_potion_of_foolhardiness" },\n'
        '\t\tstart_armed = true,\n') in script_txt, "BUILD REFUSED (round 170): Foolhardiness is not on charge_or_wavering"
assert "or ability.start_armed == true)   -- ROUND 170\n" in script_txt, \
    "BUILD REFUSED (round 170): the default rule does not read start_armed"
assert script_txt.count("\t\tstart_armed = true,\n") == 1, "BUILD REFUSED (round 170): start_armed is on another entry"
print("ROUND 170 GATE OK: Potion of Foolhardiness fires on its charge or when wavering, and still starts armed")
'''
src = open(SRC, encoding="utf-8").read()
for a, b, n in R:
    assert src.count(a) == n, (a[:70], src.count(a))
    src = src.replace(a, b)
assert src.count(ANCHOR) == 1
src = src.replace(ANCHOR, ADD)
assert "os.remove(GAME_PACK)" not in src
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST)
