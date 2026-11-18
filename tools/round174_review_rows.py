#!/usr/bin/env python3
"""Round 174 (harness 173): rows 24-50 of docs\\WH3_low_score_review_2026-11-17.md (user, 2026-11-18: "You may implement
items 24 to 50"), plus read F, the spellcaster class (side-session ruling 2026-11-18: "Okay, then let's use the caster
list"; GENERATED FOURTH.SPELLCASTER_TEXT, tools/gen_spellcaster_keys.py).

  24 Amber Bow, 25 Gaze of Nagash                    -> enemy_large_shot (exists)
  26 Hand of Gods, 27 Shem's Burning Gaze,
  28 Goggly Glare, 29 Vindictive Glare               -> NEW enemy_large_value_shot (large first, else the most valuable
                                                         infantry per soldier; never the armour fallback)
  30 Don't Even Try It, 31 Muster of Malevolents     -> enemy_single_drain (exists)
  32 Cube of Darkness, 33 Scroll of Leeching,
  34 The Vortex Shard, 39 The Black Tongue           -> NEW enemy_spellcaster (the most valuable visible enemy spellcaster)
  35 The Trickster's Pendant, 36 Trickster's Shard   -> NEW enemy_ground_spellcasters (the ground under the enemy
                                                         spellcaster with the most other spellcasters within 24 m)
  37 Silence the Prey, 38 Power Siphon               -> enemy_commander_value (exists) + target_class commander
  40 Pageant of Shrikes                              -> NEW enemy_missile_value (the most valuable shooting missile unit)
  41 Chalice of Dark Rain                            -> NEW enemy_ground_shooters (the ground under the shooting enemy
                                                         with the most shooting value within 24 m)
  42 Transfix (wh3_dlc29)                            -> NEW enemy_commander_wavering (a wavering or routing Lord/Hero,
                                                         in melee first, then the most valuable)
  43 The Hammer of Smednir                           -> unchanged (the round-163 ruling)
  44 Fury of Khaine                                  -> NEW ally_charge_melee (charging first, else fresh contact; never
                                                         a missile unit)
  45 Verminous Fury                                  -> NEW ally_wavering_melee (the most valuable non-missile ally in
                                                         melee and wavering)
  46 Helping Hand                                    -> NEW ally_lord_melee (the closest Lord/Hero ally in melee; the
                                                         caster need not fight; keeps its default)
  47 Inspired Marksmanship I-III                     -> NEW ally_missile_shooting (the most valuable shooting missile ally)
  48 Overseer of the Unseen                          -> NEW ally_melee_risk (the most valuable eligible ally in melee,
                                                         wavering or at or below 50% health)
  49 Whiplash!                                       -> NEW ally_beast_charge (a beast ally charging first, else fresh
                                                         contact)
  50 Iron-Handed Captain                             -> NEW ally_routing (the most valuable routing ally; the picker no
                                                         longer skips routing units for this family)
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_spellcaster_keys as GS  # noqa: E402

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"

MOVES = {
    "weapon_abilities_amber_bow": ("enemy_blob", "enemy_large_shot"),
    "spell_bound_gaze_of_nagash": ("enemy_blob", "enemy_large_shot"),
    "spell_bound_hand_of_gods": ("enemy_blob", "enemy_large_value_shot"),
    "spell_light_shems_burning_gaze_bound": ("enemy_blob", "enemy_large_value_shot"),
    "character_abilities_goggly_glare": ("enemy_blob", "enemy_large_value_shot"),
    "spell_bound_vindictive_glare": ("enemy_blob", "enemy_large_value_shot"),
    "dont_even_try_it": ("enemy_engaged_or_shot", "enemy_single_drain"),
    "muster_of_malevolents": ("enemy_engaged_or_shot", "enemy_single_drain"),
    "cube_of_darkness": ("enemy_engaged_or_shot", "enemy_spellcaster"),
    "scroll_of_leeching": ("enemy_engaged_or_shot", "enemy_spellcaster"),
    "the_vortex_shard": ("enemy_engaged_or_shot", "enemy_spellcaster"),
    "the_black_tongue": ("enemy_engaged_or_shot", "enemy_spellcaster"),
    "the_tricksters_pendant": ("enemy_ground_area", "enemy_ground_spellcasters"),
    "tricksters_shard": ("enemy_ground_area", "enemy_ground_spellcasters"),
    "silence_the_prey": ("enemy_engaged_or_shot", "enemy_commander_value"),
    "power_siphon": ("enemy_engaged_or_shot", "enemy_commander_value"),
    "pageant_of_shrikes": ("enemy_engaged_or_shot", "enemy_missile_value"),
    "chalice_of_dark_rain": ("enemy_ground_area", "enemy_ground_shooters"),
    "transfix_hex": ("enemy_melee", "enemy_commander_wavering"),
    "fury_of_khaine": ("ally_melee_buff", "ally_charge_melee"),
    "verminous_fury": ("ally_melee_buff", "ally_wavering_melee"),
    "helping_hand": ("ally_melee_buff", "ally_lord_melee"),
    "inspired_marksmanship_i": ("ally_missile", "ally_missile_shooting"),
    "inspired_marksmanship_ii": ("ally_missile", "ally_missile_shooting"),
    "inspired_marksmanship_iii": ("ally_missile", "ally_missile_shooting"),
    "overseer_of_the_unseen": ("ally_overseer", "ally_melee_risk"),
    "whiplash": ("ally_beast", "ally_beast_charge"),
    "iron_hand_captain": ("ally_broken", "ally_routing"),
}
ADD_COMMANDER = ("silence_the_prey", "power_siphon")
ADD_ARMED = ("helping_hand",)   # ally_melee_buff started armed (round 161); Fury of Khaine / Verminous Fury are risky

ENEMY_NEW = ["enemy_large_value_shot", "enemy_spellcaster", "enemy_ground_spellcasters", "enemy_missile_value",
             "enemy_ground_shooters", "enemy_commander_wavering"]
ALLY_NEW = ["ally_charge_melee", "ally_wavering_melee", "ally_lord_melee", "ally_missile_shooting", "ally_melee_risk",
            "ally_beast_charge", "ally_routing"]

TIP = {
    "enemy_large_value_shot": "When armed, fires at the most valuable large enemy, else at the most valuable enemy infantry per soldier",
    "enemy_spellcaster": "When armed, fires at the most valuable visible enemy spellcaster in range",
    "enemy_ground_spellcasters": "When armed, fires on the ground under the enemy spellcaster with the most other spellcasters near it",
    "enemy_missile_value": "When armed, fires at the most valuable enemy missile unit that is shooting",
    "enemy_ground_shooters": "When armed, fires on the ground under the shooting enemy with the most shooting value near it",
    "enemy_commander_wavering": "When armed, fires at a wavering or routing enemy Lord or Hero, one in melee first",
    "ally_charge_melee": "When armed, fires on the nearest charging ally, else one that just made contact, never a missile unit",
    "ally_wavering_melee": "When armed, fires on the most valuable wavering ally in melee, never a missile unit",
    "ally_lord_melee": "When armed, fires on the nearest Lord or Hero ally in melee",
    "ally_missile_shooting": "When armed, fires on the most valuable missile ally that is shooting",
    "ally_melee_risk": "When armed, fires on the most valuable ally in melee that wavers or is at or below 50% health",
    "ally_beast_charge": "When armed, fires on the nearest charging beast ally, else one that just made contact",
    "ally_routing": "When armed, fires on the most valuable routing ally",
}
CARD = {
    "enemy_large_value_shot": "Fires at the most valuable large enemy, else at the best infantry",
    "enemy_spellcaster": "Fires at the most valuable enemy spellcaster",
    "enemy_ground_spellcasters": "Fires under the thickest group of enemy spellcasters",
    "enemy_missile_value": "Fires at the most valuable enemy missile unit while it shoots",
    "enemy_ground_shooters": "Fires under the thickest group of shooting enemies",
    "enemy_commander_wavering": "Fires at a wavering enemy, one in melee first",
    "ally_charge_melee": "Fires on a charging ally, never a missile unit",
    "ally_wavering_melee": "Fires on a wavering ally in melee, never a missile unit",
    "ally_lord_melee": "Fires on the nearest ally in melee",
    "ally_missile_shooting": "Fires on the most valuable shooting missile ally",
    "ally_melee_risk": "Fires on an ally in melee that wavers or is badly hurt",
    "ally_beast_charge": "Fires on a charging beast ally",
    "ally_routing": "Fires on the most valuable routing ally",
}

CODE = r'''
-- ============================================================================
-- ROUND 174 - THE SCORE 1-2 REVIEW, ROWS 24-50 (user, 2026-11-18: "You may implement items 24 to 50").
--   READ F, THE SPELLCASTER CLASS (side-session ruling 2026-11-18: "Okay, then let's use the caster list"): a land
--     unit the game gives a spell lore, or the battle unit of a character whose campaign skill tree grants a lore or
--     a lore spell (GENERATED FOURTH.SPELLCASTER_TEXT, tools/gen_spellcaster_keys.py).
--   enemy_large_value_shot: the most valuable large enemy, else the most valuable infantry per soldier.
--   enemy_spellcaster: the most valuable visible enemy spellcaster in range (a direct effect: no safety margin).
--   enemy_ground_spellcasters / enemy_ground_shooters: the ground under the enemy (a spellcaster / a shooting missile
--     unit not in melee) in range with the most of its kind within CLUSTER_M of it (spellcasters: the count, then
--     their value; shooters: their value).
--   enemy_missile_value: the most valuable enemy missile unit in range that is shooting and not in melee.
--   enemy_commander_wavering: a visible enemy Lord or Hero in range that is wavering or routing (the closest read to
--     the game's "half its base morale"; ASSUMPTION), one in melee first, then the most valuable.
--   The ally families (rows 44-50) ride the shared ally picker with a SCORE per ally (FOURTH.ab_rank): charging 2,
--     fresh contact 1 (the closest on a tie), or the live strategic value.
-- ============================================================================
-- GENERATED by tools/gen_spellcaster_keys.py from special_ability_groups_to_units_junctions and the campaign skill
-- trees (the build refuses a pack whose table differs from the game data). Do not hand-edit.
FOURTH.SPELLCASTER_TEXT = "%SPELLCASTER%"
FOURTH.class_keys.spellcaster = {}
function FOURTH.load_spellcasters()   -- a function, so the loop adds no main-chunk locals
	for k in string.gmatch(FOURTH.SPELLCASTER_TEXT, "[^;]+") do FOURTH.class_keys.spellcaster[k] = true end
end
FOURTH.load_spellcasters()

-- the effect radius around the spot of The Trickster's Pendant / Shard and the Chalice of Dark Rain (35 m, the game's
-- phase data), at the 70% rule
FOURTH.CLUSTER_REAL_M = 35
FOURTH.CLUSTER_M = math.floor(FOURTH.CLUSTER_REAL_M * 0.70)

-- the live strategic value of a unit (0 when unreadable)
function FOURTH.unit_value(u)
	local ok, v = pcall(function() return u:strategic_value() end)
	if ok and type(v) == "number" then return v end
	return 0
end

-- an enemy wavering (exact true) or routing
function FOURTH.enemy_waver_ok(u)
	if FOURTH.wavering(u) == true then return true end
	local ok, r = pcall(function() return u:is_routing() end)
	return ok and r == true
end

function FOURTH.evaluate_enemy_large_value_shot(unit, routing)
	FOURTH.eg_mode = "shot"
	FOURTH.shot_kind = nil
	if routing or not FOURTH.shot_caster_ok(unit, false) then return nil end
	local m = FOURTH.blob_map(false)
	local e, s = FOURTH.shot_pick(unit, m, "large", false)
	if e ~= nil then
		FOURTH.shot_take(unit, e, "large", false)
		return FOURTH.shot_reason(unit, e, "most valuable large enemy", string.format("value %.0f", s))
	end
	e, s = FOURTH.shot_pick(unit, m, "infantry", false)
	if e == nil then return nil end
	FOURTH.shot_take(unit, e, "infantry", false)
	return FOURTH.shot_reason(unit, e, "no large target: most valuable enemy infantry",
		string.format("value %.1f per soldier", s))
end

function FOURTH.evaluate_enemy_spellcaster(unit, routing)
	FOURTH.eg_mode = "shot"
	FOURTH.shot_kind = nil
	FOURTH.eg_class = "spellcaster"
	if routing then return nil end
	local m = FOURTH.blob_map(false)
	local e, s = FOURTH.shot_pick(unit, m, "value", false, true)
	if e == nil then return nil end
	FOURTH.shot_take(unit, e, "value", false, true)
	return FOURTH.shot_reason(unit, e, "most valuable enemy spellcaster", string.format("value %.0f", s))
end

function FOURTH.evaluate_enemy_commander_wavering(unit, routing)
	FOURTH.eg_mode = "shot"
	FOURTH.shot_kind = nil
	FOURTH.eg_class = "commander"
	if routing then return nil end
	local m = FOURTH.blob_map(false)
	local e, s = FOURTH.shot_pick(unit, m, "waver", false, true)
	if e == nil then return nil end
	FOURTH.shot_take(unit, e, "waver", false, true)
	return FOURTH.shot_reason(unit, e, "enemy Lord or Hero wavering or routing" .. ((s == 1) and ", in melee" or ""),
		string.format("value %.0f", FOURTH.unit_value(e.unit)))
end

-- the visible living enemies (the entry's class) that pass test(e): { unit, value }
function FOURTH.enemy_list(test)
	local out = {}
	local ok_coll, coll = pcall(function() return bm:get_scriptunits_for_main_enemy_army_to_local_player() end)
	if not ok_coll or coll == nil then return out end
	local ok_n, n = pcall(function() return coll:count() end)
	if not ok_n or type(n) ~= "number" then return out end
	for i = 1, n do
		local e = nil
		pcall(function() e = coll:item(i).unit end)
		if e ~= nil then
			local ok_a, men = pcall(function() return e:number_of_men_alive() end)
			local valid = FOURTH.eg_enemy_valid(e)
			if ok_a and type(men) == "number" and men > 0 and (valid == nil or valid == true)
				and FOURTH.eg_class_ok(e) and test(e) then
				out[#out + 1] = { unit = e, value = FOURTH.unit_value(e) }
			end
		end
	end
	return out
end

-- an enemy missile unit shooting and not in melee (the Missile Mirror read)
function FOURTH.enemy_shooting_free(e)
	local shooting = FOURTH.enemy_shooting(e)
	local ok_m, melee = pcall(function() return e:is_in_melee() end)
	return shooting and not (ok_m and melee == true)
end

-- the candidate in the bound with the most of its kind within CLUSTER_M (itself included): by_count = the count
-- first, then the value; otherwise the summed value. Returns the candidate, its count and its summed value.
function FOURTH.cluster_pick(unit, list, by_count)
	local best, bn, bv = nil, nil, nil
	for i = 1, #list do
		local c = list[i]
		if FOURTH.eg_enemy_within_bound(unit, c.unit) then
			local n, v = 0, 0
			for j = 1, #list do
				local o = list[j]
				local near = (i == j)
				if not near then
					local ok_g, g = pcall(function() return c.unit:unit_distance(o.unit) end)
					near = (ok_g and type(g) == "number" and g <= FOURTH.CLUSTER_M)
				end
				if near then n, v = n + 1, v + o.value end
			end
			local better = false
			if best == nil then
				better = true
			elseif by_count then
				better = (n > bn) or (n == bn and v > bv)
			else
				better = (v > bv)
			end
			if better then best, bn, bv = c, n, v end
		end
	end
	return best, bn, bv
end

function FOURTH.evaluate_enemy_ground_spellcasters(unit, routing)
	FOURTH.eg_mode = "shot"
	FOURTH.shot_kind = nil
	FOURTH.eg_class = "spellcaster"
	if routing then return nil end
	local best, n, v = FOURTH.cluster_pick(unit, FOURTH.enemy_list(function() return true end), true)
	if best == nil then return nil end
	FOURTH.shot_take(unit, best, "value", false, true)
	FOURTH.eg_ground = true
	return FOURTH.shot_reason(unit, best, "enemy spellcaster with the most spellcasters near it - on the ground under it",
		string.format("%d spellcaster(s) within %dm, value %.0f", n, FOURTH.CLUSTER_M, v))
end

function FOURTH.evaluate_enemy_ground_shooters(unit, routing)
	FOURTH.eg_mode = "shoot"
	if routing then return nil end
	local best, n, v = FOURTH.cluster_pick(unit, FOURTH.enemy_list(FOURTH.enemy_shooting_free), false)
	if best == nil then return nil end
	FOURTH.eg_enemy = best.unit
	FOURTH.eg_arm = "shoot"
	FOURTH.eg_caster_su = FOURTH.eg_fresh_caster_su(unit)
	FOURTH.cast_target = best.unit
	FOURTH.eg_ground = true
	local etype = "enemy"
	pcall(function() etype = tostring(best.unit:type()) end)
	return string.format("the shooting enemy with the most shooting value near it (%s: %d shooter(s), value %.0f within %dm)"
		.. " - on the ground under it", etype, n, v, FOURTH.CLUSTER_M)
end

function FOURTH.evaluate_enemy_missile_value(unit, routing)
	FOURTH.eg_mode = "shoot"
	if routing then return nil end
	local best, bv = nil, nil
	local list = FOURTH.enemy_list(FOURTH.enemy_shooting_free)
	for i = 1, #list do
		local c = list[i]
		if FOURTH.eg_enemy_within_bound(unit, c.unit) and (best == nil or c.value > bv) then best, bv = c, c.value end
	end
	if best == nil then return nil end
	FOURTH.eg_enemy = best.unit
	FOURTH.eg_arm = "shoot"
	FOURTH.eg_caster_su = FOURTH.eg_fresh_caster_su(unit)
	FOURTH.cast_target = best.unit
	local etype = "enemy"
	pcall(function() etype = tostring(best.unit:type()) end)
	local d = FOURTH.eg_enemy_gap(unit, best.unit)
	return string.format("most valuable enemy missile unit shooting (targeting %s, value %.0f, distance %sm, bound %sm)",
		etype, bv, (d ~= nil) and string.format("%.1f", d) or "?", tostring(FOURTH.eg_range_m))
end

-- THE ALLY SCORES (rows 44-50): the family's description; FOURTH.ab_rank gives each ally its score (nil: not
-- eligible). The highest score wins, the closest on a tie.
FOURTH.AB_RANKED = {
	charge_first = "the closest ally charging, else in fresh contact",
	value_melee_wavering = "the most valuable ally in melee and wavering",
	value_shooting = "the most valuable ally shooting past its cast point",
	value_melee_risk = "the most valuable ally in melee, wavering or at or below 50% health",
	routing = "the most valuable routing ally",
}
function FOURTH.ab_rank(u, family)
	if family == "charge_first" then
		local w = FOURTH.charge_moment(u)
		if w == "charging" then return 2 end
		if w ~= nil then return 1 end
		return nil
	end
	if family == "routing" then
		if unit_is_routing(u) or FOURTH.morale_broken(u) then return FOURTH.unit_value(u) end
		return nil
	end
	if family == "value_shooting" then
		if FOURTH.shooting_past_cast_point(u) then return FOURTH.unit_value(u) end
		return nil
	end
	local ok_m, m = pcall(function() return u:is_in_melee() end)
	if not (ok_m and m == true) then return nil end
	if family == "value_melee_wavering" then
		if FOURTH.wavering(u) == true then return FOURTH.unit_value(u) end
		return nil
	end
	if family == "value_melee_risk" then
		local hp = FOURTH.health_pct(u)
		if FOURTH.wavering(u) == true or (type(hp) == "number" and hp <= 50) then return FOURTH.unit_value(u) end
		return nil
	end
	return nil
end

function FOURTH.evaluate_ally_charge_melee(unit, routing)
	FOURTH.ab_filter = "not_missile"
	return FOURTH.ab_pick_ally(unit, routing, "charge_first")
end
function FOURTH.evaluate_ally_beast_charge(unit, routing)
	FOURTH.ab_filter = "beast"
	return FOURTH.ab_pick_ally(unit, routing, "charge_first")
end
function FOURTH.evaluate_ally_wavering_melee(unit, routing)
	FOURTH.ab_filter = "not_missile"
	return FOURTH.ab_pick_ally(unit, routing, "value_melee_wavering")
end
-- Helping Hand: the game's own rule (FOURTH.ATARGET_TEXT: Lord or Hero only) filters the allies
function FOURTH.evaluate_ally_lord_melee(unit, routing)
	return FOURTH.ab_pick_ally(unit, routing, "melee")
end
function FOURTH.evaluate_ally_missile_shooting(unit, routing)
	FOURTH.ab_filter = "missile"
	return FOURTH.ab_pick_ally(unit, routing, "value_shooting")
end
function FOURTH.evaluate_ally_melee_risk(unit, routing)
	FOURTH.ab_filter = "overseer"
	return FOURTH.ab_pick_ally(unit, routing, "value_melee_risk")
end
-- Iron-Handed Captain: the caster may cast while the ally routs; the picker keeps routing allies for this family
function FOURTH.evaluate_ally_routing(unit, routing)
	return FOURTH.ab_pick_ally(unit, routing, "routing")
end
'''

R = [
    # the spellcaster class in the enemy class gate
    ('\tif cls == "not_undead" then return FOURTH.class_keys.undead[t] ~= true end\n',
     '\tif cls == "not_undead" then return FOURTH.class_keys.undead[t] ~= true end\n'
     '\tif cls == "spellcaster" then return FOURTH.class_keys.spellcaster[t] == true end   -- ROUND 174 (read F)\n'),
    # the shot picker: the wavering Lord / Hero kind
    ('\t\telseif kind == "value" then   -- ROUND 158',
     '\t\telseif kind == "waver" then   -- ROUND 174: a wavering or routing enemy, one in melee first, then the value\n'
     '\t\t\tok_kind = FOURTH.enemy_waver_ok(e.unit)\n'
     '\t\t\tlocal ok_m, mel = pcall(function() return e.unit:is_in_melee() end)\n'
     '\t\t\ts1 = (ok_m and mel == true) and 1 or 0\n'
     '\t\t\ts2 = e.value or 0\n'
     '\t\telseif kind == "value" then   -- ROUND 158'),
    ('\telseif kind ~= "execute" and kind ~= "value" then',
     '\telseif kind ~= "execute" and kind ~= "value" and kind ~= "waver" then   -- ROUND 174: waver has no caster gate'),
    ('\t\t\tif kind == "area" and e.men < FOURTH.area_min() then return false end',
     '\t\t\tif kind == "area" and e.men < FOURTH.area_min() then return false end\n'
     '\t\t\tif kind == "waver" and not FOURTH.enemy_waver_ok(e.unit) then return false end   -- ROUND 174'),
    # the ally filter: never a missile unit
    ('\tif f == "broken" then return FOURTH.morale_broken(unit) end\n',
     '\tif f == "broken" then return FOURTH.morale_broken(unit) end\n'
     '\tif f == "not_missile" then return not FOURTH.class_member(unit, "missile") end   -- ROUND 174\n'),
    # the ally picker: routing allies for the routing family, the scores, the ordering, the reason
    ('\t\t\t\tif tostring(other:unique_ui_id()) ~= self_id and not unit_is_routing(other)\n'
     '\t\t\t\t\tand FOURTH.ab_filter_ok(other) then',
     '\t\t\t\tif tostring(other:unique_ui_id()) ~= self_id\n'
     '\t\t\t\t\tand (family == "routing" or not unit_is_routing(other))   -- ROUND 174: Iron-Handed Captain\n'
     '\t\t\t\t\tand FOURTH.ab_filter_ok(other) then'),
    ('\t\t\t\t\telseif family == "charging" then\n',
     '\t\t\t\t\telseif FOURTH.AB_RANKED[family] then\n'
     '\t\t\t\t\t\t-- ROUND 174: the review rows 44-50 - a score per ally (nil: not eligible)\n'
     '\t\t\t\t\t\tval = FOURTH.ab_rank(other, family)\n'
     '\t\t\t\t\t\teligible = (val ~= nil)\n'
     '\t\t\t\t\telseif family == "charging" then\n'),
    ('\t\t\t\t\t\t\telseif family == "ammo" then\n\t\t\t\t\t\t\t\tbetter = (type(best_val) ~= "number" or val < best_val)\n',
     '\t\t\t\t\t\t\telseif FOURTH.AB_RANKED[family] then   -- ROUND 174: the highest score, the closest on a tie\n'
     '\t\t\t\t\t\t\t\tbetter = (val > best_val) or (val == best_val and gap ~= nil and (best_gap == nil or gap < best_gap))\n'
     '\t\t\t\t\t\t\telseif family == "ammo" then\n\t\t\t\t\t\t\t\tbetter = (type(best_val) ~= "number" or val < best_val)\n'),
    ('\telseif FOURTH.ab_infinite then\n',
     '\telseif FOURTH.AB_RANKED[family] then   -- ROUND 174\n'
     '\t\treturn string.format("%s: %s (score %.0f), cast on ally", tostring(FOURTH.ab_marker or "ally"),\n'
     '\t\t\tFOURTH.AB_RANKED[family], best_val or 0)\n'
     '\telseif FOURTH.ab_infinite then\n'),
    # the two ally re-checks
    ('\t\tif FOURTH.ab_family == "charging" then   -- ROUND 171\n\t\t\thp_ok_now = (FOURTH.charge_moment(ally) ~= nil)\n\t\tend\n',
     '\t\tif FOURTH.ab_family == "charging" then   -- ROUND 171\n\t\t\thp_ok_now = (FOURTH.charge_moment(ally) ~= nil)\n\t\tend\n'
     '\t\tif FOURTH.AB_RANKED[FOURTH.ab_family] then   -- ROUND 174\n'
     '\t\t\thp_ok_now = (FOURTH.ab_rank(ally, FOURTH.ab_family) ~= nil)\n\t\tend\n'),
    ('\tif FOURTH.ab_family == "charging" then   -- ROUND 171\n\t\treturn FOURTH.charge_moment(ally) ~= nil\n\tend\n',
     '\tif FOURTH.ab_family == "charging" then   -- ROUND 171\n\t\treturn FOURTH.charge_moment(ally) ~= nil\n\tend\n'
     '\tif FOURTH.AB_RANKED[FOURTH.ab_family] then   -- ROUND 174\n'
     '\t\treturn FOURTH.ab_rank(ally, FOURTH.ab_family) ~= nil\n\tend\n'),
    # the new code (after the expendable class loads; before the evaluator map)
    ("FOURTH.load_expendable()\n", "FOURTH.load_expendable()\n" + "%CODE%"),
    # the evaluator wiring, the labels, the cards, the ally-picker family set
    ("\tcontact_melee = FOURTH.evaluate_contact_melee,\n",
     "\tcontact_melee = FOURTH.evaluate_contact_melee,\n"
     + "".join("\t%s = FOURTH.evaluate_%s,%s\n" % (f, f, "   -- ROUND 174" if i == 0 else "")
               for i, f in enumerate(ENEMY_NEW + ALLY_NEW))),
    ('\tcontact_melee = "When armed, fires in melee against an enemy whose blows carry a contact effect",\n',
     '\tcontact_melee = "When armed, fires in melee against an enemy whose blows carry a contact effect",\n'
     + "".join('\t%s = "%s",%s\n' % (f, TIP[f], "   -- ROUND 174" if i == 0 else "")
               for i, f in enumerate(ENEMY_NEW + ALLY_NEW))),
    ('\tcontact_melee = "Fires in melee unless wavering, against an enemy with contact effects",\n',
     '\tcontact_melee = "Fires in melee unless wavering, against an enemy with contact effects",\n'
     + "".join('\t%s = "%s",%s\n' % (f, CARD[f], "   -- ROUND 174" if i == 0 else "")
               for i, f in enumerate(ENEMY_NEW + ALLY_NEW))),
    ("\tself_or_ally_charge = true }   -- ROUND 171\n",
     "\tself_or_ally_charge = true,   -- ROUND 171\n\t"
     + ", ".join("%s = true" % f for f in ALLY_NEW) + " }   -- ROUND 174\n"),
]


def move_entries(s):
    for m, (old, new) in MOVES.items():
        pat = re.compile(r'(\t\{ marker = "%s", name = "[^"]+", trigger = )"%s",\n' % (re.escape(m), re.escape(old)))
        assert len(pat.findall(s)) == 1, (m, old, len(pat.findall(s)))
        s = pat.sub(lambda x: x.group(1) + '"%s",\n' % new, s)
        if m in ADD_COMMANDER or m in ADD_ARMED:
            pat2 = re.compile(r'(\t\{ marker = "%s", name = "[^"]+", trigger = "%s",\n\t\tbadge = "[^"]+",\n'
                              r'\t\tkeys = \{[^}]*\},\n(?:\t\t[a-z_]+ = [^\n]+,\n)*?)(\t\tox = 0, oy = 0 \},\n)'
                              % (re.escape(m), re.escape(new)))
            assert len(pat2.findall(s)) == 1, (m, "add", len(pat2.findall(s)))
            add = '\t\ttarget_class = "commander",   -- ROUND 174\n' if m in ADD_COMMANDER else \
                '\t\tstart_armed = true,   -- ROUND 174: keeps its default (ally_melee_buff started armed)\n'
            s = pat2.sub(lambda x: x.group(1) + add + x.group(2), s)
    return s


def main():
    code = CODE.replace("%SPELLCASTER%", GS.text(GS.derive()))
    for path in (SRC, ANN):
        s = open(path, encoding="utf-8", newline="").read()
        if "ROUND 174" in s:
            print(path, "already patched")
            continue
        s = move_entries(s)
        for o, n in R:
            n = n.replace("%CODE%", code)
            if path == ANN and o == "\telseif FOURTH.ab_infinite then\n":
                continue   # the reading copy's picker answers true / false, it has no reason chain
            assert s.count(o) == 1, (path[-12:], o[:80], s.count(o))
            s = s.replace(o, n)
        assert "\u2014" not in s
        open(path, "w", encoding="utf-8", newline="").write(s)
        print(path, "patched")


if __name__ == "__main__":
    main()
