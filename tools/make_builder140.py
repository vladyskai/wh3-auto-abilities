#!/usr/bin/env python3
"""Build the round-140 build script from the round-139 one.

Gates rebased: charge_only 5 -> 4 (Blooood! moved to self_running).
Adds one gate: the moving rule guards every firing-flag read, Blooood! rides self_running, and BUILD REFUSED when the
embedded fire_move table differs from the game data (tools/gen_fire_move_keys.py)."""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261109_stand_your_ground_harness138\build_and_install139.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261113_moving_running_harness139\build_and_install140.py"
ANCHOR = 'print("ROUND 139 GATE OK: Stand Your Ground on melee_or_wavering_aura")\n'
ADD = ANCHOR + r'''# ROUND 140: shooting and moving are incompatible unless the unit fires on the move; Blooood! when running.
assert "st.cast_point_passed == true and FOURTH.can_shoot_now(unit)" in script_txt \
    and "st.firing ~= true or not FOURTH.can_shoot_now(unit)" in script_txt \
    and "if not FOURTH.can_shoot_now(enemy) then return false end" in script_txt \
    and 'name = "Blooood!", trigger = "self_running",' in script_txt \
    and "self_running = FOURTH.evaluate_self_running," in script_txt, \
    "the round-140 moving rule or Blooood!'s running trigger is missing"
import gen_fire_move_keys as _g140
assert _g140.lua_block(_g140.derive()) in script_txt, \
    "BUILD REFUSED (round 140): the fire_move table differs from the game data"
print("ROUND 140 GATE OK: the moving rule guards every firing-flag read; Blooood! on self_running; fire_move matches the game")
'''
RULES = [("script_txt.count('trigger = \"charge_only\"') == 5", "script_txt.count('trigger = \"charge_only\"') == 4")]
src = open(SRC, encoding="utf-8").read()
assert src.count(ANCHOR) == 1
src = src.replace(ANCHOR, ADD)
for a, b in RULES:
    n = src.count(a)
    assert n >= 1, a
    src = src.replace(a, b)
    print("rebased %d x: %s" % (n, a[:60]))
assert "os.remove(GAME_PACK)" not in src
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST)
