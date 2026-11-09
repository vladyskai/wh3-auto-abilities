#!/usr/bin/env python3
"""Build the round-139 build script from the round-138 one. No gate is rebased (no builder gate pins Stand Your
Ground's trigger). Adds one gate: Stand Your Ground rides melee_or_wavering_aura with its 35 m aura."""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261109_rare_filters_harness137\build_and_install138.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261109_stand_your_ground_harness138\build_and_install139.py"
ANCHOR = 'print("ROUND 138 GATE OK: 21 target classes, enemy_missile_shooting 1, the undead table matches the game")\n'
ADD = ANCHOR + r'''# ROUND 139: Stand Your Ground fires for the allies it protects (QA battle 1).
assert 'name = "Stand Your Ground", trigger = "melee_or_wavering_aura",' in script_txt \
    and "melee_or_wavering_aura = FOURTH.evaluate_melee_or_wavering_aura," in script_txt \
    and 'trigger = "melee_low_morale"' not in script_txt, \
    "Stand Your Ground's round-139 trigger is missing"
print("ROUND 139 GATE OK: Stand Your Ground on melee_or_wavering_aura")
'''
src = open(SRC, encoding="utf-8").read()
assert src.count(ANCHOR) == 1
src = src.replace(ANCHOR, ADD)
assert "os.remove(GAME_PACK)" not in src
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST)
