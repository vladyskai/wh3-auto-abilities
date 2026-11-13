#!/usr/bin/env python3
"""Round 140 (harness 139): QA battles 3/5 findings - shooting and moving are incompatible; Blooood! when running.

QA battle 3 (2026-11-13): Boom! cast at 159 s while the Hellcannon was running - its last shot was at 135 s and the
firing flag stays ON for max(2 x reload, 20 s) after the last shot. User rulings, verbatim:
  * "Unless the unit can fire while moving, shooting and moving are incompatible." -> every firing-flag read
    (FOURTH.shooting_past_cast_point, FOURTH.ammo_fraction_if_firing, Missile Mirror's FOURTH.enemy_shooting) also
    requires the unit NOT to be moving, unless its type is in the GENERATED fire_move set (unit attribute
    mounted_fire_move, tools/gen_fire_move_keys.py). An unreadable is_moving() keeps today's behaviour.
  * Blooood!: "Running, any time" -> the NEW self_running: is_moving_fast() exactly true, not routing; cast on self.
No string.find. Every helper is a FOURTH field.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_fire_move_keys as G  # noqa: E402

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"


def sub(s, a, b):
    assert s.count(a) == 1, (a[:80], s.count(a))
    return s.replace(a, b)


SHOOT_OLD = "\treturn st ~= nil and st.firing == true and st.cast_point_passed == true\n"
SHOOT_NEW = ("\t-- ROUND 140: shooting and moving are incompatible unless the unit can fire on the move\n"
             "\treturn st ~= nil and st.firing == true and st.cast_point_passed == true and FOURTH.can_shoot_now(unit)\n")
FRAC_OLD = "\tif st == nil or st.firing ~= true or type(st.start) ~= \"number\" or st.start <= 0\n"
FRAC_NEW = ("\t-- ROUND 140: a unit that moves (and cannot fire on the move) is not shooting\n"
            "\tif st == nil or st.firing ~= true or not FOURTH.can_shoot_now(unit) or type(st.start) ~= \"number\" or st.start <= 0\n")
ENEMY_OLD = "\tif st.last_drop_s == nil then return false end\n"
ENEMY_NEW = ("\tif st.last_drop_s == nil then return false end\n"
             "\t-- ROUND 140: a moving enemy that cannot fire on the move is not shooting\n"
             "\tif not FOURTH.can_shoot_now(enemy) then return false end\n")
ENTRY_OLD = '\t{ marker = "blooood", name = "Blooood!", trigger = "charge_only",'
ENTRY_NEW = '\t{ marker = "blooood", name = "Blooood!", trigger = "self_running",'

COMMON = """-- ============================================================================
-- ROUND 140 - QA BATTLE 3: SHOOTING AND MOVING; BLOOOOD! WHEN RUNNING.
--   can_shoot_now: false while the unit is moving, unless its type can fire on
--   the move (the GENERATED fire_move set, unit attribute mounted_fire_move).
--   An unreadable is_moving() answers true (today's behaviour). Every
--   firing-flag read goes through it (user ruling 2026-11-13: "Unless the unit
--   can fire while moving, shooting and moving are incompatible.").
--   self_running (NEW, Blooood!): is_moving_fast() exactly true, not routing;
--   cast on self (user ruling: "Running, any time").
-- ============================================================================
function FOURTH.can_shoot_now(unit)
	local ok, mv = pcall(function() return unit:is_moving() end)
	if not (ok and mv == true) then return true end
	local t = FOURTH.type_plain(unit)
	return t ~= nil and FOURTH.class_keys.fire_move[t] == true
end

"""
EVAL_LIVE = """function FOURTH.evaluate_self_running(unit, routing)
	if routing then return nil end
	local ok, f = pcall(function() return unit:is_moving_fast() end)
	if ok and f == true then return "running (is_moving_fast), cast on self" end
	return nil
end

"""
EVAL_ANN = """function FOURTH.evaluate_self_running(unit, routing)
	if routing then return false end
	local ok, f = pcall(function() return unit:is_moving_fast() end)
	return ok and f == true
end

"""
MAP_OLD = "\tmelee_or_wavering_aura = FOURTH.evaluate_melee_or_wavering_aura,\n"
MAP_NEW = MAP_OLD + "\t-- ROUND 140\n\tself_running = FOURTH.evaluate_self_running,\n"
TIP_OLD = '\tmelee_or_wavering_aura = "When armed, fires when this unit or a friendly unit near it is in melee or wavering",\n'
TIP_NEW = TIP_OLD + '\tself_running = "When armed, fires when this unit is running",\n'
ANCHOR = "FOURTH.evaluators = {\n"

FM = G.lua_block(G.derive()) + "\n"
for path, ev in ((SRC, EVAL_LIVE), (ANN, EVAL_ANN)):
    s = open(path, encoding="utf-8", newline="").read()
    assert "self_running" not in s and "FOURTH.class_keys.fire_move" not in s
    s = sub(s, SHOOT_OLD, SHOOT_NEW)
    s = sub(s, FRAC_OLD, FRAC_NEW)
    s = sub(s, ENEMY_OLD, ENEMY_NEW)
    s = sub(s, ENTRY_OLD, ENTRY_NEW)
    s = sub(s, MAP_OLD, MAP_NEW)
    s = sub(s, TIP_OLD, TIP_NEW)
    s = sub(s, ANCHOR, FM + COMMON + ev + ANCHOR)
    assert s.count('trigger = "self_running"') == 1 and s.count('trigger = "charge_only"') == 4
    open(path, "w", encoding="utf-8", newline="").write(s)
    print(path, "moving rule + Blooood! on self_running")
