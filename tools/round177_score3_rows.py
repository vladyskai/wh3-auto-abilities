#!/usr/bin/env python3
"""Round 177 (harness 176): rows 1-22 of docs\\WH3_score3_review_2026-11-18.md (user, 2026-11-18: "Implement all until
item 22, except the number 3 that should stay the same").

Changed (15 entries):
  1  Blood Omens              -> NEW slow_army (a fast enemy closing on any of ours, or the caster in melee)
  2  Creature-Killer          -> NEW melee_vs_large (the caster or a unit in its 24 m aura fighting a LARGE enemy)
  4  Empowering Shrooms       -> NEW ally_squig_melee (the nearest SQUIG ally in melee; GENERATED squig set)
  5  Everyone Has Their Price -> NEW enemy_melee_near (the caster in melee, or a visible enemy in its 24 m aura in melee)
  6  Fury of the Land         -> NEW aura_charge_or_melee (the caster or a unit in its 38 m aura charging, in fresh
                                 contact or in melee)
  11 Refuse to Die            -> NEW melee_health25 (in melee at or below 25% health)
  12 Rune of Oath & Steel     -> melee_or_under_fire (exists)
  14 Shield of Aeons          -> NEW guard_aura (in melee or under fire, or a visible fast enemy inside its 38 m aura)
  15, 16 Shielding Swarm x2   -> NEW self_or_ally_fire_melee (self in melee or under fire; else the most valuable ally
                                 under fire within 70 m; else the nearest ally in melee)
  17 Slayer for Chaos         -> self_last_stand (exists: 10%, in melee or under fire)
  18 Steppe Hunter's Horn     -> melee_vs_large (24 m)
  19 The Armour of Morkar     -> guard_aura (24 m)
  20 The Blood Price          -> NEW melee_healthy (in melee, not wavering, above 50% health; it starts on M: self-damage)
  21 The Ostermark Runefang   -> melee_vs_large (24 m)
Unchanged: 3 Daemonshield (the user's word), 7 Terrorgheist Skull and 13 Seductive Glory (ruled), 8 Primal Roar, 9 Rage
Embodied, 10 Rage Incarnate, 22 Toad Rage (keep). Every moved entry keeps its default (they all rode melee_unwavering,
which starts armed): start_armed where the new family does not start armed; The Blood Price stays on M (risky).
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_squig_keys as GQ  # noqa: E402

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"

# marker -> (new trigger, extra field lines, start_armed)
MOVES = {
    "blood_omens": ("slow_army", [], True),
    "creature_killer": ("melee_vs_large", ["aura_real = 35"], True),
    "empowering_shrooms": ("ally_squig_melee", ["ally_range_real = 100"], True),
    "everyone_has_their_price": ("enemy_melee_near", ["aura_real = 35"], True),
    "fury_of_the_land": ("aura_charge_or_melee", ["aura_real = 55"], True),
    "refuse_to_die": ("melee_health25", [], True),
    "rune_of_oath_and_steel": ("melee_or_under_fire", [], False),
    "shield_of_aeons": ("guard_aura", ["aura_real = 55"], True),
    "dispatch_the_swarm_protect": ("self_or_ally_fire_melee", ["ally_range_real = 100"], True),
    "dispatch_the_swarm_protect_upgraded": ("self_or_ally_fire_melee", ["ally_range_real = 100"], True),
    "slayer_for_chaos": ("self_last_stand", [], False),
    "steppe_hunters_horn": ("melee_vs_large", ["aura_real = 35"], True),
    "the_armour_of_morkar": ("guard_aura", ["aura_real = 35"], True),
    "the_blood_price": ("melee_healthy", [], False),
    "ostermark_runefang": ("melee_vs_large", ["aura_real = 35"], True),
}
NEW = ["slow_army", "melee_vs_large", "ally_squig_melee", "enemy_melee_near", "aura_charge_or_melee", "melee_health25",
       "guard_aura", "self_or_ally_fire_melee", "melee_healthy"]
TIP = {
    "slow_army": "When armed, fires when a fast enemy closes on any of our units, or this unit is in melee",
    "melee_vs_large": "When armed, fires when this unit or one in its aura is fighting a large enemy",
    "ally_squig_melee": "When armed, fires on the nearest squig ally in melee",
    "enemy_melee_near": "When armed, fires when this unit, or an enemy in its aura, is in melee",
    "aura_charge_or_melee": "When armed, fires when this unit or a unit in its aura charges, has just made contact, or fights",
    "melee_health25": "When armed, fires in melee at or below 25% health",
    "guard_aura": "When armed, fires in melee or under missile fire, or when a fast enemy enters the aura",
    "self_or_ally_fire_melee": "When armed, fires on this unit in melee or under fire, else on an ally under fire, else on an ally in melee",
    "melee_healthy": "When armed, fires in melee while above 50% health",
}
CARD = {
    "slow_army": "Fires when an enemy charges your army, or in melee",
    "melee_vs_large": "Fires when it or a nearby ally fights a large enemy",
    "ally_squig_melee": "Fires on a squig ally in melee",
    "enemy_melee_near": "Fires when it or a nearby enemy is in melee",
    "aura_charge_or_melee": "Fires when it or a nearby ally charges or fights",
    "melee_health25": "Fires in melee at 25% health or less",
    "guard_aura": "Fires in melee, under fire, or when an enemy charges in",
    "self_or_ally_fire_melee": "Fires on itself or an ally under fire, else on an ally in melee",
    "melee_healthy": "Fires in melee while above 50% health",
}

CODE = r'''
-- ============================================================================
-- ROUND 177 - THE SCORE-3 REVIEW, ROWS 1-22 (user, 2026-11-18: "Implement all until item 22, except the number 3").
--   slow_army: a visible fast enemy closing on any unit of ours (FOURTH.fast_enemy_near), or the caster in melee.
--   melee_vs_large: the caster, or a unit of ours inside the 70% aura, is in melee with a LARGE enemy (the engagement
--     set x the GENERATED large set).
--   ally_squig_melee: the shared ally picker, the GENERATED squig set (the game's unit_is_not_squig rule), "melee".
--   enemy_melee_near: the caster in melee, or a visible living enemy inside the 70% aura in melee.
--   aura_charge_or_melee: the caster, or a unit of ours inside the 70% aura, charging, in fresh contact or in melee.
--   melee_health25: in melee (exact true) at or below MELEE_LOW_PCT health.
--   guard_aura: in melee or under missile fire, or a visible fast enemy moving inside the 70% aura (an enemy charge).
--   self_or_ally_fire_melee: the caster in melee or under fire -> self; else the most valuable ally under fire; else the
--     nearest ally in melee (both within the 70% ally bound).
--   melee_healthy: in melee, not wavering, above MELEE_HEALTHY_PCT health (the item hurts its bearer).
-- ============================================================================
-- GENERATED by tools/gen_squig_keys.py from unit_attributes_to_groups_junctions and land_units (the game's 'squig'
-- attribute); the build refuses a pack whose table differs. Do not hand-edit.
FOURTH.SQUIG_TEXT = "%SQUIG%"
FOURTH.class_keys.squig = {}
function FOURTH.load_squigs()   -- a function, so the loop adds no main-chunk locals
	for k in string.gmatch(FOURTH.SQUIG_TEXT, "[^;]+") do FOURTH.class_keys.squig[k] = true end
end
FOURTH.load_squigs()
FOURTH.MELEE_LOW_PCT = 25       -- user approval 2026-11-18 (review row 11: Cannot Die near death)
FOURTH.MELEE_HEALTHY_PCT = 50   -- user approval 2026-11-18 (review row 20: the item hurts its bearer)

-- exact true / false: is u in melee?
function FOURTH.in_melee_now(u)
	local ok, m = pcall(function() return u:is_in_melee() end)
	return ok and m == true
end

-- the units of ours (not the caster, alive, not routing) inside the current entry's reach that pass test(u): the closest
function FOURTH.ours_in_reach(unit, test)
	local reach = FOURTH.ah_range_m
	if reach == nil or tracked_units == nil then return nil, nil end
	local self_id = nil
	pcall(function() self_id = tostring(unit:unique_ui_id()) end)
	local best, best_gap = nil, nil
	for i = 1, #tracked_units do
		local u = tracked_units[i] and tracked_units[i].unit
		if u ~= nil then
			local ok_id, id = pcall(function() return tostring(u:unique_ui_id()) end)
			local ok_a, men = pcall(function() return u:number_of_men_alive() end)
			if ok_id and id ~= self_id and ok_a and type(men) == "number" and men > 0 and not unit_is_routing(u) then
				local ok_g, g = pcall(function() return unit:unit_distance(u) end)
				if ok_g and type(g) == "number" and g <= reach and test(u) and (best == nil or g < best_gap) then
					best, best_gap = u, g
				end
			end
		end
	end
	return best, best_gap
end

-- the visible living enemies; test(e) picks; returns the first that passes and its gap to the caster
function FOURTH.enemy_where(unit, test)
	local ok_coll, coll = pcall(function() return bm:get_scriptunits_for_main_enemy_army_to_local_player() end)
	if not ok_coll or coll == nil then return nil end
	local ok_n, n = pcall(function() return coll:count() end)
	if not ok_n or type(n) ~= "number" then return nil end
	for i = 1, n do
		local e = nil
		pcall(function() e = coll:item(i).unit end)
		if e ~= nil and FOURTH.enemy_not_hidden(e) then
			local ok_a, men = pcall(function() return e:number_of_men_alive() end)
			if ok_a and type(men) == "number" and men > 0 then
				local ok, a, b = pcall(test, e)
				if ok and a then return e, a, b end
			end
		end
	end
	return nil
end

function FOURTH.evaluate_slow_army(unit, routing)
	if routing then return nil end
	if FOURTH.in_melee_now(unit) then return "in melee (army slow)" end
	local e, g, sp = FOURTH.enemy_where(unit, function(x) return FOURTH.fast_enemy_near(x, unit) end)
	if e == nil then return nil end
	return string.format("a fast enemy (run speed %.1f m/s) is closing, %.1fm from one of ours (army slow)", sp or 0, g or 0)
end

-- true when u is in melee with a LARGE enemy (the engagement set x the GENERATED large set)
function FOURTH.fights_large(u)
	if not FOURTH.in_melee_now(u) then return false end
	local members = FOURTH.engagement_set(u)
	if members == nil then return false end
	for i = 1, #members do
		local t = members[i].type
		if t ~= nil and FOURTH.class_keys.large[t] == true then return true end
	end
	return false
end

function FOURTH.evaluate_melee_vs_large(unit, routing)
	if routing then return nil end
	if FOURTH.fights_large(unit) then return "the caster is fighting a large enemy" end
	local u, g = FOURTH.ours_in_reach(unit, FOURTH.fights_large)
	if u == nil then return nil end
	return string.format("a unit of ours %.1fm away (aura %sm) is fighting a large enemy", g, tostring(FOURTH.ah_range_m))
end

function FOURTH.evaluate_ally_squig_melee(unit, routing)
	FOURTH.ab_filter = "squig"
	return FOURTH.ab_pick_ally(unit, routing, "melee")
end

function FOURTH.evaluate_enemy_melee_near(unit, routing)
	if routing then return nil end
	if FOURTH.in_melee_now(unit) then return "the caster is in melee" end
	local reach = FOURTH.ah_range_m
	if reach == nil then return nil end
	local e, g = FOURTH.enemy_where(unit, function(x)
		if not FOURTH.in_melee_now(x) then return nil end
		local ok_g, gap = pcall(function() return unit:unit_distance(x) end)
		if ok_g and type(gap) == "number" and gap <= reach then return gap end
		return nil
	end)
	if e == nil then return nil end
	return string.format("an enemy %.1fm away (aura %sm) is in melee", g, tostring(reach))
end

function FOURTH.evaluate_aura_charge_or_melee(unit, routing)
	if routing then return nil end
	local own = FOURTH.charge_moment(unit)
	if own ~= nil then return "the caster: " .. own end
	if FOURTH.in_melee_now(unit) then return "the caster is in melee" end
	local u, g = FOURTH.ours_in_reach(unit, function(x) return FOURTH.charge_moment(x) ~= nil or FOURTH.in_melee_now(x) end)
	if u == nil then return nil end
	return string.format("a unit of ours %.1fm away (aura %sm) is charging or fighting", g, tostring(FOURTH.ah_range_m))
end

function FOURTH.evaluate_melee_health25(unit, routing)
	if routing or not FOURTH.in_melee_now(unit) then return nil end
	local hp = FOURTH.health_pct(unit)
	if type(hp) ~= "number" or hp > FOURTH.MELEE_LOW_PCT then return nil end
	return string.format("in melee at %d%% health (<= %d%%)", math.floor(hp), FOURTH.MELEE_LOW_PCT)
end

function FOURTH.evaluate_guard_aura(unit, routing)
	if routing then return nil end
	if FOURTH.in_melee_now(unit) then return "in melee (guard)" end
	if FOURTH.under_fire(unit) then return "under missile fire (guard)" end
	local reach = FOURTH.ah_range_m
	if reach == nil then return nil end
	local e, g, sp = FOURTH.enemy_where(unit, function(x)
		local ok_mv, mv = pcall(function() return x:is_moving() end)
		local ok_sp, s = pcall(function() return x:fast_speed() end)
		local ok_g, gap = pcall(function() return unit:unit_distance(x) end)
		if ok_mv and mv == true and ok_sp and type(s) == "number" and s >= FOURTH.FAST_ENEMY_MPS
			and ok_g and type(gap) == "number" and gap <= reach then
			return gap, s
		end
		return nil
	end)
	if e == nil then return nil end
	return string.format("a fast enemy (run speed %.1f m/s) %.1fm away, inside the %sm aura (guard)", sp or 0, g, tostring(reach))
end

function FOURTH.evaluate_self_or_ally_fire_melee(unit, routing)
	if routing then return nil end
	if FOURTH.in_melee_now(unit) or FOURTH.under_fire(unit) then
		return "the caster is in melee or under missile fire, cast on self"
	end
	local r = FOURTH.ab_pick_ally(unit, routing, "value_under_fire")
	if r then return r end   -- the reading copy's picker answers false, the live one nil
	return FOURTH.ab_pick_ally(unit, routing, "melee")
end

function FOURTH.evaluate_melee_healthy(unit, routing)
	if routing or not FOURTH.in_melee_now(unit) then return nil end
	if FOURTH.wavering(unit) == true then return nil end
	local hp = FOURTH.health_pct(unit)
	if type(hp) ~= "number" or hp <= FOURTH.MELEE_HEALTHY_PCT then return nil end
	return string.format("in melee at %d%% health (> %d%%)", math.floor(hp), FOURTH.MELEE_HEALTHY_PCT)
end
'''

R = [
    # the new code after the round-174 ally families
    ('function FOURTH.evaluate_ally_routing(unit, routing)\n\treturn FOURTH.ab_pick_ally(unit, routing, "routing")\nend\n',
     'function FOURTH.evaluate_ally_routing(unit, routing)\n\treturn FOURTH.ab_pick_ally(unit, routing, "routing")\nend\n'
     + "%CODE%"),
    # the ally score: the most valuable ally under missile fire
    ('\trouting = "the most valuable routing ally",\n}\n',
     '\trouting = "the most valuable routing ally",\n'
     '\tvalue_under_fire = "the most valuable ally under missile fire",   -- ROUND 177\n}\n'),
    ('function FOURTH.ab_rank(u, family)\n',
     'function FOURTH.ab_rank(u, family)\n'
     '\tif family == "value_under_fire" then   -- ROUND 177: Shielding Swarm\n'
     '\t\tif FOURTH.under_fire(u) then return FOURTH.unit_value(u) end\n'
     '\t\treturn nil\n'
     '\tend\n'),
    # wiring, labels, cards, ally-picker families
    ("\tally_routing = FOURTH.evaluate_ally_routing,\n",
     "\tally_routing = FOURTH.evaluate_ally_routing,\n"
     + "".join("\t%s = FOURTH.evaluate_%s,%s\n" % (f, f, "   -- ROUND 177" if i == 0 else "") for i, f in enumerate(NEW))),
    ('\tally_routing = "When armed, fires on the most valuable routing ally",\n',
     '\tally_routing = "When armed, fires on the most valuable routing ally",\n'
     + "".join('\t%s = "%s",%s\n' % (f, TIP[f], "   -- ROUND 177" if i == 0 else "") for i, f in enumerate(NEW))),
    ('\tally_routing = "Fires on the most valuable routing ally",\n',
     '\tally_routing = "Fires on the most valuable routing ally",\n'
     + "".join('\t%s = "%s",%s\n' % (f, CARD[f], "   -- ROUND 177" if i == 0 else "") for i, f in enumerate(NEW))),
    ("ally_beast_charge = true, ally_routing = true }   -- ROUND 174\n",
     "ally_beast_charge = true, ally_routing = true,   -- ROUND 174\n"
     "\tally_squig_melee = true, self_or_ally_fire_melee = true }   -- ROUND 177\n"),
]


def move_entries(s):
    for m, (new, extra, armed) in MOVES.items():
        pat = re.compile(r'(\t\{ marker = "%s", name = "[^"]+", trigger = )"melee_unwavering",\n(\t\tbadge = "[^"]+",\n'
                         r'\t\tkeys = \{[^}]*\},\n)(\t\tox = 0, oy = 0 \},\n)' % re.escape(m))
        assert len(pat.findall(s)) == 1, (m, len(pat.findall(s)))
        add = "".join("\t\t%s,\n" % x for x in extra) + ("\t\tstart_armed = true,\n" if armed else "")
        s = pat.sub(lambda x: '\t-- ROUND 177 (score-3 review): %s\n' % new + x.group(1) + '"%s",\n' % new + x.group(2)
                    + add + x.group(3), s)
    return s


def main():
    code = CODE.replace("%SQUIG%", GQ.text(GQ.derive()))
    for path in (SRC, ANN):
        s = open(path, encoding="utf-8", newline="").read()
        if "ROUND 177" in s:
            print(path, "already patched")
            continue
        s = move_entries(s)
        for o, n in R:
            n = n.replace("%CODE%", code)
            assert s.count(o) == 1, (path[-12:], o[:80], s.count(o))
            s = s.replace(o, n)
        assert "\u2014" not in s
        open(path, "w", encoding="utf-8", newline="").write(s)
        print(path, "patched")


if __name__ == "__main__":
    main()
