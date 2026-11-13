#!/usr/bin/env python3
"""Round 144 (harness 143): open batch 3 - the rest of group C (10 entries / 10 keys; 3 abilities decided as skipped).

User rulings 2026-11-13 (earlier status: "excluded (auto: no effect text available)", not user decisions):
  * Hag's Denial: "10%, melee or fire" -> NEW self_last_stand: own health at or below 10% while in melee or under fire;
  * Ruinshelter: in melee -> melee_unwavering;   * Banner of Hellfire: in melee -> melee_unwavering;
  * Rock Bottom (Rogue Idol RoR): "wait until no ammo left" -> NEW self_out_of_ammo (ammo_left() reads 0);
  * Morikhane, the Black Armour: under fire -> under_fire (self only);
  * Hunter's Call: like Stand Your Ground -> melee_or_wavering_aura (aura 35 m -> 24 m);
  * Icon of the King: the game excludes LIVING units -> NEW health_aura_self_undead (the generated undead set);
  * The Gold Standard: the lowest-health ally IN MELEE at or below 75% -> NEW ally_hurt_melee (70 m of 100 m);
  * Ghostly Howl: the game only targets an enemy below half morale -> NEW enemy_wavering (52 m of 75 m);
  * Petrifying Gaze: the immobiliser ruling -> enemy_fast_near_ally (35 m of 50 m).
  Skipped (no entry): Storm of Blades and Whirling Death (stances), Cloak of the Dunes (stealth, 2026-10-09).
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


def entry(marker, name, trig, key, extra):
    lines = ['\t{ marker = "%s", name = "%s", trigger = "%s",' % (marker, name, trig),
             '\t\tbadge = "zz_auto_badge_%s",' % marker,
             '\t\tkeys = { "%s" },' % key]
    lines += ["\t\t%s," % e for e in extra]
    lines += ["\t\tox = 0, oy = 0 },"]
    return "\n".join(lines) + "\n"


NEW_ENTRIES = (
    entry("hags_denial", "Hag's Denial", "self_last_stand", "wh3_dlc24_unit_abilities_hags_denial", [])
    + entry("ruinshelter", "Ruinshelter", "melee_unwavering", "wh2_dlc15_unit_abilities_mimic_ruinshelter", [])
    + entry("rock_bottom", "Rock Bottom", "self_out_of_ammo", "wh2_dlc15_unit_abilities_rock_bottom", [])
    + entry("morikhane", "Morikhane, the Black Armour", "under_fire",
            "wh3_dlc29_item_abilities_morikhane_the_black_armour", [])
    + entry("hunters_call", "Hunter's Call", "melee_or_wavering_aura", "wh2_dlc13_character_ability_hunters_call",
            ["aura_real = 35"])
    + entry("icon_of_the_king", "Icon of the King", "health_aura_self_undead", "wh3_dlc29_item_abilities_icon_of_the_king",
            ["aura_real = 35"])
    + entry("the_gold_standard", "The Gold Standard", "ally_hurt_melee", "wh3_dlc25_item_abilities_the_gold_standard",
            ["ally_range_real = 100"])
    + entry("banner_of_hellfire", "Banner of Hellfire", "melee_unwavering", "wh3_main_banner_abilities_banner_of_hellfire", [])
    + entry("ghostly_howl", "Ghostly Howl", "enemy_wavering", "wh3_dlc29_hero_active_ghostly_howl", ["range_real = 75"])
    + entry("petrifying_gaze", "Petrifying Gaze", "enemy_fast_near_ally", "wh3_dlc24_unit_passive_petrifying_gaze",
            ["range_real = 50"]))
WIND = {"wh2_dlc15_unit_abilities_rock_bottom": 1, "wh3_dlc29_item_abilities_morikhane_the_black_armour": 1,
        "wh3_dlc29_hero_active_ghostly_howl": 3}
HOLD = {"wh2_dlc13_character_ability_hunters_call": 120, "wh3_dlc29_item_abilities_icon_of_the_king": 120,
        "wh3_dlc24_unit_passive_petrifying_gaze": 120}

RESTOCK = '\t{ marker = "restock", name = "Restock!", trigger = "ally_ammo_low",'
WIND_OLD = "\twind_up_s = {\n"
WIND_NEW = WIND_OLD + "\t\t-- ROUND 144: open batch 3 wind-ups (unit_spec_abil wind_up_time)\n" + "".join(
    '\t\t["%s"] = %d,\n' % (k, v) for k, v in WIND.items())
HOLD_OLD = "\thold_s = {\n"
HOLD_NEW = HOLD_OLD + "\t\t-- ROUND 144: open batch 3 multi-use keys (recharge_time)\n" + "".join(
    '\t\t["%s"] = %d,\n' % (k, v) for k, v in HOLD.items())

# the enemy pre-cast re-check: Ghostly Howl's own condition
EG_OLD = ('\t\telseif eg_mode_now == "shoot" then\n'
          '\t\t\t-- ROUND 138: Missile Mirror - still shooting and not in melee\n'
          '\t\t\tcond_now = (not still_melee) and FOURTH.enemy_shooting(enemy)\n'
          '\t\tend\n')
EG_NEW = EG_OLD[:-len('\t\tend\n')] + ('\t\telseif eg_mode_now == "wavering" then\n'
                                       '\t\t\t-- ROUND 144: Ghostly Howl - the enemy is still wavering\n'
                                       '\t\t\tcond_now = (FOURTH.wavering(enemy) == true)\n'
                                       '\t\tend\n')
# the ally-health pre-cast re-check: The Gold Standard (still in melee) and Icon of the King (still non-living)
AH_OLD = ('\t\tif FOURTH.ah_mode == "mist" then\n'
          '\t\t\thp_ok = (FOURTH.before_range(chosen, FOURTH.MIST_BAND) ~= nil)\n'
          '\t\tend\n')
AH_NEW = AH_OLD + ('\t\t-- ROUND 144: The Gold Standard - the chosen ally must still be in melee\n'
                   '\t\tif FOURTH.ah_mode == "melee" then\n'
                   '\t\t\thp_ok = hp_ok and (FOURTH.ah_in_melee(chosen) == true)\n'
                   '\t\tend\n'
                   '\t\t-- ROUND 144: Icon of the King - the chosen unit must still be a non-living one\n'
                   '\t\tif FOURTH.ah_mode == "undead" then\n'
                   '\t\t\thp_ok = hp_ok and (FOURTH.ah_is_undead(chosen) == true)\n'
                   '\t\tend\n')

HELPERS = r'''-- ============================================================================
-- ROUND 144 - OPEN BATCH 3 (user rulings 2026-11-13).
--   self_last_stand (Hag's Denial: Cannot Die, ONE use): own health at or below
--     LAST_STAND_PCT while in melee or under missile fire. Fail-closed health.
--   self_out_of_ammo (Rock Bottom): the unit's own ammo_left() reads 0.
--   health_aura_self_undead (Icon of the King: the game excludes LIVING units):
--     the health_aura_self pick limited to units in the GENERATED undead set.
--   ally_hurt_melee (The Gold Standard): the lowest-health unit (owner or ally in
--     range) at or below 75% that is IN MELEE; cast on it.
--   enemy_wavering (Ghostly Howl: the game targets only an enemy below half
--     morale): the closest enemy in range whose is_wavering() reads exactly true.
-- ============================================================================
FOURTH.LAST_STAND_PCT = 10   -- user ruling 2026-11-13 (Hag's Denial): "10%, melee or fire"

-- exact true / false / nil: the unit's own melee read
function FOURTH.ah_in_melee(u)
	local ok, m = pcall(function() return u:is_in_melee() end)
	if ok and m == true then return true end
	if ok and m == false then return false end
	return nil
end

-- a unit in the GENERATED undead set (an unreadable type never qualifies)
function FOURTH.ah_is_undead(u)
	local t = FOURTH.type_plain(u)
	return t ~= nil and FOURTH.class_keys.undead[t] == true
end

-- the ah_pick rule (owner or a friendly unit within FOURTH.ah_range_m, at or
-- below 75%, the lowest wins) with one extra test every candidate must pass
function FOURTH.ah_pick_where(unit, routing, test)
	if routing then return nil, nil, nil end
	local reach = FOURTH.ah_range_m
	local best, best_hp, best_gap = nil, nil, nil
	local self_hp = FOURTH.health_pct(unit)
	if type(self_hp) == "number" and self_hp <= 75 and test(unit) then
		best, best_hp, best_gap = unit, self_hp, 0
	end
	local self_id = tostring(unit:unique_ui_id())
	for i = 1, #tracked_units do
		local other = tracked_units[i] and tracked_units[i].unit
		if other ~= nil and other ~= unit and other:number_of_men_alive() > 0 then
			if tostring(other:unique_ui_id()) ~= self_id and not unit_is_routing(other) then
				local hp = FOURTH.health_pct(other)
				if type(hp) == "number" and hp <= 75 and test(other) then
					local gap = FOURTH.ab_ally_gap(unit, other)
					if reach == nil or gap == nil or gap <= reach then
						if best == nil or (type(best_hp) == "number" and hp < best_hp) then
							best, best_hp, best_gap = other, hp, gap
						end
					end
				end
			end
		end
	end
	return best, best_hp, best_gap
end

'''

EVAL_LIVE = HELPERS + r'''function FOURTH.evaluate_self_last_stand(unit, routing)
	if routing then return nil end
	local hp = FOURTH.health_pct(unit)
	if type(hp) ~= "number" or hp > FOURTH.LAST_STAND_PCT then return nil end
	local melee = (FOURTH.ah_in_melee(unit) == true)
	if not melee and not FOURTH.under_fire(unit) then return nil end
	return string.format("last stand: health %d%% (<= %d%%) while %s, cast on self", math.floor(hp),
		FOURTH.LAST_STAND_PCT, melee and "in melee" or "under missile fire")
end

function FOURTH.evaluate_self_out_of_ammo(unit, routing)
	if routing then return nil end
	local ok, a = pcall(function() return unit:ammo_left() end)
	if ok and type(a) == "number" and a <= 0 then return "no ammunition left (ammo_left 0), cast on self" end
	return nil
end

function FOURTH.evaluate_health_aura_self_undead(unit, routing)
	local chosen, hp, gap = FOURTH.ah_pick_where(unit, routing, FOURTH.ah_is_undead)
	if chosen == nil then return nil end
	FOURTH.ah_chosen = chosen
	FOURTH.ah_selfaura = true
	FOURTH.ah_mode = "undead"
	FOURTH.ah_caster_su = FOURTH.ab_fresh_friend_su(unit)
	if chosen == unit then
		return string.format("health %d%% (<= 75%%), a non-living unit", math.floor(hp))
	end
	FOURTH.ah_log_ally(chosen, hp, gap, "cast on the caster (the aura is centred on it; non-living units only)")
	return string.format("%s: lowest-health NON-LIVING unit in the aura is an ALLY at %d%% (<= 75%%),"
		.. " distance %s of %sm %s - cast on the caster",
		tostring(FOURTH.ah_marker or "ally"), math.floor(hp),
		((gap ~= nil) and string.format("%.1f", gap) or "?"),
		tostring(FOURTH.ah_range_m), tostring(FOURTH.ah_range_word))
end

function FOURTH.evaluate_ally_hurt_melee(unit, routing)
	local chosen, hp, gap = FOURTH.ah_pick_where(unit, routing, function(u) return FOURTH.ah_in_melee(u) == true end)
	if chosen == nil then return nil end
	FOURTH.ah_chosen = chosen
	FOURTH.ah_mode = "melee"
	FOURTH.ah_caster_su = FOURTH.ab_fresh_friend_su(unit)
	if chosen == unit then
		return string.format("health %d%% (<= 75%%) in melee, cast on self", math.floor(hp))
	end
	FOURTH.ah_ally = chosen
	FOURTH.ah_ally_su = FOURTH.ab_fresh_friend_su(chosen)
	FOURTH.cast_target = chosen
	FOURTH.ah_log_ally(chosen, hp, gap, "cast on that ally (it is in melee)")
	return string.format("%s: lowest-health unit IN MELEE in range is an ALLY at %d%% (<= 75%%),"
		.. " distance %s of %sm %s - cast on the ally",
		tostring(FOURTH.ah_marker or "ally"), math.floor(hp),
		((gap ~= nil) and string.format("%.1f", gap) or "?"),
		tostring(FOURTH.ah_range_m), tostring(FOURTH.ah_range_word))
end

function FOURTH.evaluate_enemy_wavering(unit, routing)
	FOURTH.eg_mode = "wavering"
	if routing then return nil end
	local ok_coll, coll = pcall(function() return bm:get_scriptunits_for_main_enemy_army_to_local_player() end)
	if not ok_coll or coll == nil then return nil end
	local ok_n, n = pcall(function() return coll:count() end)
	if not ok_n or type(n) ~= "number" then return nil end
	local best, best_gap = nil, nil
	for i = 1, n do
		local ok_su, su = pcall(function() return coll:item(i) end)
		local enemy = nil
		if ok_su and su ~= nil then pcall(function() enemy = su.unit end) end
		if enemy ~= nil then
			local ok_alive, alive = pcall(function() return enemy:number_of_men_alive() end)
			local valid = FOURTH.eg_enemy_valid(enemy)
			if ok_alive and type(alive) == "number" and alive > 0 and (valid == nil or valid == true)
				and FOURTH.wavering(enemy) == true
				and FOURTH.eg_class_ok(enemy) and FOURTH.eg_enemy_within_bound(unit, enemy) then
				local gap = FOURTH.eg_enemy_gap(unit, enemy)
				if best == nil or (gap ~= nil and (best_gap == nil or gap < best_gap)) then
					best, best_gap = enemy, gap
				end
			end
		end
	end
	if best == nil then return nil end
	local etype = "enemy"
	pcall(function() etype = tostring(best:type()) end)
	FOURTH.eg_enemy = best
	FOURTH.eg_arm = "wavering"
	FOURTH.eg_caster_su = FOURTH.eg_fresh_caster_su(unit)
	FOURTH.cast_target = best
	return string.format("wavering enemy in range (targeting %s, distance %sm bound %sm)", etype,
		(best_gap ~= nil) and string.format("%.1f", best_gap) or "?", tostring(FOURTH.eg_range_m))
end

'''
EVAL_ANN = HELPERS + r'''-- Hag's Denial: health at or below the line while in melee or under fire
function FOURTH.evaluate_self_last_stand(unit, routing)
	if routing then return false end
	local hp = FOURTH.health_pct(unit)
	if type(hp) ~= "number" or hp > FOURTH.LAST_STAND_PCT then return false end
	return FOURTH.ah_in_melee(unit) == true or FOURTH.under_fire(unit)
end

-- Rock Bottom: no ammunition left
function FOURTH.evaluate_self_out_of_ammo(unit, routing)
	if routing then return false end
	local ok, a = pcall(function() return unit:ammo_left() end)
	return ok and type(a) == "number" and a <= 0
end

-- Icon of the King: a hurt NON-LIVING unit in the aura; cast on the caster
function FOURTH.evaluate_health_aura_self_undead(unit, routing)
	local chosen = FOURTH.ah_pick_where(unit, routing, FOURTH.ah_is_undead)
	if chosen == nil then return false end
	FOURTH.ah_chosen = chosen
	FOURTH.ah_selfaura = true
	FOURTH.ah_mode = "undead"
	FOURTH.ah_caster_su = FOURTH.ab_fresh_friend_su(unit)
	return true
end

-- The Gold Standard: the lowest-health unit in range that is in melee; cast on it
function FOURTH.evaluate_ally_hurt_melee(unit, routing)
	local chosen = FOURTH.ah_pick_where(unit, routing, function(u) return FOURTH.ah_in_melee(u) == true end)
	if chosen == nil then return false end
	FOURTH.ah_chosen = chosen
	FOURTH.ah_mode = "melee"
	FOURTH.ah_caster_su = FOURTH.ab_fresh_friend_su(unit)
	if chosen ~= unit then
		FOURTH.ah_ally = chosen
		FOURTH.ah_ally_su = FOURTH.ab_fresh_friend_su(chosen)
		FOURTH.cast_target = chosen
	end
	return true
end

-- Ghostly Howl: the closest wavering enemy in range
function FOURTH.evaluate_enemy_wavering(unit, routing)
	FOURTH.eg_mode = "wavering"
	if routing then return false end
	local ok_coll, coll = pcall(function() return bm:get_scriptunits_for_main_enemy_army_to_local_player() end)
	if not ok_coll or coll == nil then return false end
	local ok_n, n = pcall(function() return coll:count() end)
	if not ok_n or type(n) ~= "number" then return false end
	local best, best_gap = nil, nil
	for i = 1, n do
		local ok_su, su = pcall(function() return coll:item(i) end)
		local enemy = nil
		if ok_su and su ~= nil then pcall(function() enemy = su.unit end) end
		if enemy ~= nil then
			local ok_alive, alive = pcall(function() return enemy:number_of_men_alive() end)
			local valid = FOURTH.eg_enemy_valid(enemy)
			if ok_alive and type(alive) == "number" and alive > 0 and (valid == nil or valid == true)
				and FOURTH.wavering(enemy) == true
				and FOURTH.eg_class_ok(enemy) and FOURTH.eg_enemy_within_bound(unit, enemy) then
				local gap = FOURTH.eg_enemy_gap(unit, enemy)
				if best == nil or (gap ~= nil and (best_gap == nil or gap < best_gap)) then
					best, best_gap = enemy, gap
				end
			end
		end
	end
	if best == nil then return false end
	FOURTH.eg_enemy = best
	FOURTH.eg_arm = "wavering"
	FOURTH.eg_caster_su = FOURTH.eg_fresh_caster_su(unit)
	FOURTH.cast_target = best
	return true
end

'''
FAMS = ["self_last_stand", "self_out_of_ammo", "health_aura_self_undead", "ally_hurt_melee", "enemy_wavering"]
MAP_OLD = "\tenemy_ground_shooting = FOURTH.evaluate_enemy_ground_shooting,\n"
MAP_NEW = MAP_OLD + "\t-- ROUND 144\n" + "".join("\t%s = FOURTH.evaluate_%s,\n" % (f, f) for f in FAMS)
TIP_OLD = ('\tenemy_ground_shooting = "When armed, fires on the ground under the closest enemy missile unit in range that '
           'is shooting",\n')
TIP_NEW = TIP_OLD + (
    '\tself_last_stand = "When armed, fires when this unit is at 10% health or less while in melee or under fire",\n'
    '\tself_out_of_ammo = "When armed, fires when this unit has no ammunition left",\n'
    '\thealth_aura_self_undead = "When armed, fires when this unit or a non-living friendly unit in its aura is hurt",\n'
    '\tally_hurt_melee = "When armed, fires on the most hurt friendly unit in range that is in melee",\n'
    '\tenemy_wavering = "When armed, fires on the closest wavering enemy in range",\n')
ANCHOR = "FOURTH.evaluators = {\n"

for path, ev in ((SRC, EVAL_LIVE), (ANN, EVAL_ANN)):
    s = open(path, encoding="utf-8", newline="").read()
    assert "evaluate_self_last_stand" not in s
    before = s.count("\t{ marker = ")
    s = sub(s, RESTOCK, NEW_ENTRIES + RESTOCK)
    s = sub(s, WIND_OLD, WIND_NEW)
    s = sub(s, HOLD_OLD, HOLD_NEW)
    s = sub(s, EG_OLD, EG_NEW)
    s = sub(s, AH_OLD, AH_NEW)
    s = sub(s, MAP_OLD, MAP_NEW)
    s = sub(s, TIP_OLD, TIP_NEW)
    s = sub(s, ANCHOR, ev + ANCHOR)
    assert s.count("\t{ marker = ") == before + 10
    assert "string.find" not in ev + NEW_ENTRIES + EG_NEW + AH_NEW
    open(path, "w", encoding="utf-8", newline="").write(s)
    print(path, "entries", before, "->", before + 10)

import gen_recharge_keys as G  # noqa: E402
new_block = G.lua_block(G.derive())
pat = re.compile(r"-- GENERATED by tools/gen_recharge_keys\.py.*?\nFOURTH\.load_recharge\(\)\n", re.S)
for path in (SRC, ANN):
    s = open(path, encoding="utf-8", newline="").read()
    assert len(pat.findall(s)) == 1
    s = pat.sub(lambda m: new_block, s)
    open(path, "w", encoding="utf-8", newline="").write(s)
print("lock table re-derived:", len(G.derive()), "keys")
