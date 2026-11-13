#!/usr/bin/env python3
"""Round 142 (harness 141): open batch 1 (shooting buffs and ammo refills) and Blooood! when moving.

User rulings 2026-11-13:
  * More Powder!, Restock! (gunnery school): "Same as Restock!" -> ally_ammo_low, 100 m -> 70 m;
  * Master of Mists (2 keys): "Before range (Farsight-like)" -> NEW ground_ally_before_range: the ground under the
    closest friendly missile unit (the caster included) within 175 m (70% of 250 m) that has NO enemy inside its
    own missile range but one inside range x 1.35 (the 70% rule on the +50% range bonus);
  * Of Warp and Ruin: "Shooting, not into melee" -> NEW self_shooting_clear (shooting past its cast point and its
    current target readable and NOT in melee: its shots can hurt friendly units);
  * Ominous Powder: "Shooting, health above 50%" -> NEW self_shooting_healthy (it damages its carrier);
  * Blooood!: QA battles showed a Hellcannon never runs (is_moving_fast always false); "When moving" -> NEW
    self_moving (is_moving() exactly true). self_running keeps its evaluator with no entry.
5 new entries / 6 keys. No string.find. Every helper is a FOURTH field.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"


def sub(s, a, b):
    assert s.count(a) == 1, (a[:80], s.count(a))
    return s.replace(a, b)


RESTOCK = '\t{ marker = "restock", name = "Restock!", trigger = "ally_ammo_low",'
NEW_ENTRIES = (
    '\t{ marker = "more_powder", name = "More Powder!", trigger = "ally_ammo_low",\n'
    '\t\tbadge = "zz_auto_badge_more_powder",\n'
    '\t\tkeys = { "wh2_dlc11_hero_abilities_more_powder" },\n'
    '\t\tally_range_real = 100,\n'
    '\t\tox = 0, oy = 0 },\n'
    '\t{ marker = "restock_gunnery_school", name = "Restock!", trigger = "ally_ammo_low",\n'
    '\t\tbadge = "zz_auto_badge_restock_gunnery_school",\n'
    '\t\tkeys = { "wh3_dlc25_abilities_restock_gunnery_school" },\n'
    '\t\tally_range_real = 100,\n'
    '\t\tox = 0, oy = 0 },\n'
    '\t{ marker = "master_of_mists", name = "Master of Mists", trigger = "ground_ally_before_range",\n'
    '\t\tbadge = "zz_auto_badge_master_of_mists",\n'
    '\t\tkeys = { "wh3_dlc27_character_abilities_master_of_mists",\n'
    '\t\t\t"wh3_dlc27_character_abilities_master_of_mists_custom" },\n'
    '\t\tally_range_real = 250,\n'
    '\t\tox = 0, oy = 0 },\n'
    '\t{ marker = "of_warp_and_ruin", name = "Of Warp and Ruin", trigger = "self_shooting_clear",\n'
    '\t\tbadge = "zz_auto_badge_of_warp_and_ruin",\n'
    '\t\tkeys = { "wh3_dlc29_unit_abilities_of_warp_and_ruin" },\n'
    '\t\tox = 0, oy = 0 },\n'
    '\t{ marker = "ominous_powder", name = "Ominous Powder", trigger = "self_shooting_healthy",\n'
    '\t\tbadge = "zz_auto_badge_ominous_powder",\n'
    '\t\tkeys = { "wh3_dlc25_item_abilities_ominous_powder" },\n'
    '\t\tox = 0, oy = 0 },\n')
BLOO_OLD = 'name = "Blooood!", trigger = "self_running",'
BLOO_NEW = 'name = "Blooood!", trigger = "self_moving",'
RANGE_OLD = "FOURTH.ALLY_CAST_R200 = 140"
RANGE_NEW = ("FOURTH.ALLY_CAST_R200 = 140\n"
             "FOURTH.ALLY_CAST_R250 = 175   -- ROUND 142: Master of Mists, 250 m -> floor(250 x 0.70)")
MAP_R_OLD = "\t[200] = FOURTH.ALLY_CAST_R200,\n"
MAP_R_NEW = MAP_R_OLD + "\t[250] = FOURTH.ALLY_CAST_R250,\n"
HOLD_OLD = "\thold_s = {\n"
HOLD_NEW = HOLD_OLD + ("\t\t-- ROUND 142: More Powder! 4 uses / gunnery-school Restock! 2 uses, 60 s; Master of Mists 2 uses, 120 s.\n"
                       "\t\t[\"wh2_dlc11_hero_abilities_more_powder\"] = 60,\n"
                       "\t\t[\"wh3_dlc25_abilities_restock_gunnery_school\"] = 60,\n"
                       "\t\t[\"wh3_dlc27_character_abilities_master_of_mists\"] = 120,\n"
                       "\t\t[\"wh3_dlc27_character_abilities_master_of_mists_custom\"] = 120,\n")
GROUND_OLD = "\tground_keys = {\n"
GROUND_NEW = GROUND_OLD + ("\t\t-- ROUND 142: Master of Mists is placed on the ground (under the chosen unit).\n"
                           "\t\t[\"wh3_dlc27_character_abilities_master_of_mists\"] = true,\n"
                           "\t\t[\"wh3_dlc27_character_abilities_master_of_mists_custom\"] = true,\n")
HP_OLD = '\t\tlocal hp_ok = (type(hp_now) ~= "number") or (hp_now <= 75)\n'
HP_NEW = HP_OLD + ('\t\t-- ROUND 142: Master of Mists re-checks its own condition, not health\n'
                   '\t\tif FOURTH.ah_mode == "mist" then\n'
                   '\t\t\thp_ok = (FOURTH.before_range(chosen, FOURTH.MIST_BAND) ~= nil)\n'
                   '\t\tend\n')
CLEAR_OLD = "\t\t\t\t\tFOURTH.ah_selfaura = false\n"
CLEAR_NEW = CLEAR_OLD + "\t\t\t\t\tFOURTH.ah_mode = nil\n"

COMMON = """-- ============================================================================
-- ROUND 142 - OPEN BATCH 1 (shooting buffs, ammo refills) AND BLOOOOD!.
--   ground_ally_before_range (Master of Mists): the ground under the closest
--     friendly missile unit (the caster included) within the 70% bound that has
--     no enemy inside its own missile range but one inside range x MIST_BAND
--     (1 + 0.50 x 0.70 = 1.35); re-checked before the cast (ah_mode "mist").
--   self_shooting_clear (Of Warp and Ruin): shooting past its cast point and its
--     current target readable and NOT in melee.
--   self_shooting_healthy (Ominous Powder): shooting past its cast point and its
--     own health readable and above 50%.
--   self_moving (Blooood!): is_moving() exactly true (a Hellcannon never runs).
-- ============================================================================
FOURTH.MIST_BONUS = 0.50   -- Master of Mists: "Range: +50%" (the game's own phase stat)
FOURTH.MIST_BAND = 1 + FOURTH.MIST_BONUS * FOURTH.RANGE_FRACTION   -- 1.35
FOURTH.ah_mode = nil

-- nearest, range when u is a missile unit out of melee with ammunition, NO enemy
-- inside its own missile range and the nearest one inside range x band; nil otherwise
function FOURTH.before_range(u, band)
	local ok_mel, mel = pcall(function() return u:is_in_melee() end)
	if not ok_mel or mel ~= false then return nil end
	local ok_am, am = pcall(function() return u:ammo_left() end)
	if not ok_am or type(am) ~= "number" or am <= 0 then return nil end
	local ok_r, r = pcall(function() return u:missile_range() end)
	if not ok_r or type(r) ~= "number" or r <= 0 then return nil end
	local nearest, any_in = FOURTH.nearest_enemy_gap(u, r)
	if nearest == nil or any_in or nearest > r * band then return nil end
	return nearest, r
end

-- true / false / nil: is the unit's current target in melee?
function FOURTH.target_in_melee(unit)
	local ok_t, t = pcall(function() return unit:current_target() end)
	if not ok_t or t == nil then return nil end
	local ok_m, m = pcall(function() return t:is_in_melee() end)
	if not ok_m then return nil end
	return m == true
end

"""
EVAL_LIVE = """function FOURTH.evaluate_ground_ally_before_range(unit, routing)
	if routing then return nil end
	FOURTH.ah_mode = "mist"
	local best, best_gap, best_near, best_r = nil, nil, nil, nil
	local function try(u, gap)
		local near, r = FOURTH.before_range(u, FOURTH.MIST_BAND)
		if near ~= nil and (best == nil or gap < best_gap) then
			best, best_gap, best_near, best_r = u, gap, near, r
		end
	end
	try(unit, 0)
	local self_id = tostring(unit:unique_ui_id())
	for i = 1, #(tracked_units or {}) do
		local other = tracked_units[i] and tracked_units[i].unit
		if other ~= nil and other ~= unit then
			local ok_m, men = pcall(function() return other:number_of_men_alive() end)
			local ok_i, oid = pcall(function() return tostring(other:unique_ui_id()) end)
			if ok_m and type(men) == "number" and men > 0 and ok_i and oid ~= self_id and not unit_is_routing(other) then
				local gap = FOURTH.ab_ally_gap(unit, other)
				if gap ~= nil and FOURTH.ab_range_m ~= nil and gap <= FOURTH.ab_range_m then try(other, gap) end
			end
		end
	end
	if best == nil then return nil end
	FOURTH.ah_chosen = best
	FOURTH.ah_ground = true
	FOURTH.ah_caster_su = FOURTH.ab_fresh_friend_su(unit)
	local who = "the caster"
	if best ~= unit then
		FOURTH.ah_ally = best
		FOURTH.ah_ally_su = FOURTH.ab_fresh_friend_su(best)
		who = string.format("a friendly unit %.1fm away", best_gap)
	end
	return string.format("%s has no enemy inside its missile range %.1fm; the nearest is at %.1fm, inside range x %.2f = %.1fm - cast on the ground under it",
		who, best_r, best_near, FOURTH.MIST_BAND, best_r * FOURTH.MIST_BAND)
end

function FOURTH.evaluate_self_shooting_clear(unit, routing)
	if routing or not FOURTH.shooting_past_cast_point(unit) then return nil end
	if FOURTH.target_in_melee(unit) ~= false then return nil end
	return "the unit is shooting past its cast point at a target that is not in melee, cast on self"
end

function FOURTH.evaluate_self_shooting_healthy(unit, routing)
	if routing or not FOURTH.shooting_past_cast_point(unit) then return nil end
	local hp = FOURTH.health_pct(unit)
	if type(hp) ~= "number" or hp <= 50 then return nil end
	return string.format("the unit is shooting past its cast point at %d%% health (> 50%%), cast on self", math.floor(hp))
end

function FOURTH.evaluate_self_moving(unit, routing)
	if routing then return nil end
	local ok, m = pcall(function() return unit:is_moving() end)
	if ok and m == true then return "moving (is_moving), cast on self" end
	return nil
end

"""
EVAL_ANN = """function FOURTH.evaluate_ground_ally_before_range(unit, routing)
	if routing then return false end
	FOURTH.ah_mode = "mist"
	local best, best_gap = nil, nil
	local function try(u, gap)
		if FOURTH.before_range(u, FOURTH.MIST_BAND) ~= nil and (best == nil or gap < best_gap) then
			best, best_gap = u, gap
		end
	end
	try(unit, 0)
	local self_id = tostring(unit:unique_ui_id())
	for i = 1, #(tracked_units or {}) do
		local other = tracked_units[i] and tracked_units[i].unit
		if other ~= nil and other ~= unit then
			local ok_m, men = pcall(function() return other:number_of_men_alive() end)
			local ok_i, oid = pcall(function() return tostring(other:unique_ui_id()) end)
			if ok_m and type(men) == "number" and men > 0 and ok_i and oid ~= self_id and not unit_is_routing(other) then
				local gap = FOURTH.ab_ally_gap(unit, other)
				if gap ~= nil and FOURTH.ab_range_m ~= nil and gap <= FOURTH.ab_range_m then try(other, gap) end
			end
		end
	end
	if best == nil then return false end
	FOURTH.ah_chosen = best
	FOURTH.ah_ground = true
	FOURTH.ah_caster_su = FOURTH.ab_fresh_friend_su(unit)
	if best ~= unit then
		FOURTH.ah_ally = best
		FOURTH.ah_ally_su = FOURTH.ab_fresh_friend_su(best)
	end
	return true
end

function FOURTH.evaluate_self_shooting_clear(unit, routing)
	if routing or not FOURTH.shooting_past_cast_point(unit) then return false end
	return FOURTH.target_in_melee(unit) == false
end

function FOURTH.evaluate_self_shooting_healthy(unit, routing)
	if routing or not FOURTH.shooting_past_cast_point(unit) then return false end
	local hp = FOURTH.health_pct(unit)
	return type(hp) == "number" and hp > 50
end

function FOURTH.evaluate_self_moving(unit, routing)
	if routing then return false end
	local ok, m = pcall(function() return unit:is_moving() end)
	return ok and m == true
end

"""
MAP_OLD = "\tmelee_self_or_ally = FOURTH.evaluate_melee_self_or_ally,\n"
MAP_NEW = MAP_OLD + ("\t-- ROUND 142\n"
                     "\tground_ally_before_range = FOURTH.evaluate_ground_ally_before_range,\n"
                     "\tself_shooting_clear = FOURTH.evaluate_self_shooting_clear,\n"
                     "\tself_shooting_healthy = FOURTH.evaluate_self_shooting_healthy,\n"
                     "\tself_moving = FOURTH.evaluate_self_moving,\n")
TIP_OLD = '\tmelee_self_or_ally = "When armed, fires when this unit or a friendly unit near it is in melee",\n'
TIP_NEW = TIP_OLD + (
    '\tground_ally_before_range = "When armed, fires under a friendly missile unit when the enemy is just out of its range",\n'
    '\tself_shooting_clear = "When armed, fires when this unit is shooting at a target that is not in melee",\n'
    '\tself_shooting_healthy = "When armed, fires when this unit is shooting and above half health",\n'
    '\tself_moving = "When armed, fires when this unit is moving",\n')
ANCHOR = "FOURTH.evaluators = {\n"

for path, ev in ((SRC, EVAL_LIVE), (ANN, EVAL_ANN)):
    s = open(path, encoding="utf-8", newline="").read()
    assert "ground_ally_before_range" not in s
    before = s.count("\t{ marker = ")
    s = sub(s, RESTOCK, NEW_ENTRIES + RESTOCK)
    s = sub(s, BLOO_OLD, BLOO_NEW)
    s = sub(s, RANGE_OLD, RANGE_NEW)
    s = sub(s, MAP_R_OLD, MAP_R_NEW)
    s = sub(s, HOLD_OLD, HOLD_NEW)
    s = sub(s, GROUND_OLD, GROUND_NEW)
    s = sub(s, HP_OLD, HP_NEW)
    s = sub(s, CLEAR_OLD, CLEAR_NEW)
    s = sub(s, MAP_OLD, MAP_NEW)
    s = sub(s, TIP_OLD, TIP_NEW)
    s = sub(s, ANCHOR, COMMON + ev + ANCHOR)
    assert s.count("\t{ marker = ") == before + 5
    open(path, "w", encoding="utf-8", newline="").write(s)
    print(path, "entries", before, "->", before + 5)

# the generated lock table now covers the new keys: re-derive it from the patched source and replace the block
import gen_recharge_keys as G  # noqa: E402
new_block = G.lua_block(G.derive())
pat = re.compile(r"-- GENERATED by tools/gen_recharge_keys\.py.*?\nFOURTH\.load_recharge\(\)\n", re.S)
for path in (SRC, ANN):
    s = open(path, encoding="utf-8", newline="").read()
    assert len(pat.findall(s)) == 1
    s = pat.sub(lambda m: new_block, s)
    open(path, "w", encoding="utf-8", newline="").write(s)
print("lock table re-derived:", len(G.derive()), "keys")
