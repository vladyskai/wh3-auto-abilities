-- ============================================================================
-- ROUND 114 - THE AIR-DROP RULE IS ONE COMPARISON: THE ENGINE'S EDGE GAP < 0.1 m
--
-- THE USER'S RULING, verbatim:
--   "1. I want the trigger to be checked much more frequently when armed and
--    less than 30 meters from a valid enemy unit.
--    2. Valid units are those who have more than 10 entities.
--    3. I trigger the moment distance between edges is below 0.1 meters.
--    That's it."
-- and, on this round's two follow-ups:
--   "1. Remove the 'and it is infantry'. No need for it now.
--    2. Current count 3. Let's try with 0.2 s for now."
--
-- THE RULE, IN FULL - nothing else decides:
--   candidate = ALIVE (number_of_men_alive() > 0) and
--               number_of_men_alive() > AIR_DROP_MIN_MEN (10)
--   valid     = that candidate's edge-to-edge unit_distance() is READABLE
--   chosen    = the NEAREST valid candidate by that distance
--   FIRE      = unit_distance(caster, chosen) < AIR_DROP_EDGE_M (0.10 m)
-- plus the caster-side usage restrictions the ability's own row declares
-- (air_only / no_melee), the self-centred cast on the OWNER, and fail-closed
-- reads. Nothing else: no infantry test, no single-entity test, no projection.
--
-- battle_unit:unit_distance() is "the shortest distance in metres between this
-- unit and a supplied unit, taking into account their bounding box rather than
-- just working out the centre-to-centre distance" (battle_unit.lua:160). It is
-- the number the user asked for, so it is the number that decides.
--
-- WHAT ROUND 114 DELETED FROM THIS EVALUATOR:
--   * the infantry filter (the old class test) - the user's ruling 1; every
--     OTHER evaluator keeps its own class filters untouched;
--   * the single-entity exclusion via initial_number_of_men() (a one-model
--     unit fails the > 10 test by itself);
--   * the four projection dials AIR_DROP_DELAY_S / AIR_DROP_ENEMY_LEAD /
--     AIR_DROP_CASTER_DELAY_S / AIR_DROP_CASTER_LEAD and AIR_DROP_INHERIT;
--   * AIR_DROP_CENTER_M and the derived frontage credit
--     (AIR_DROP_MODEL_RADIUS_M / AIR_DROP_RANKS / AIR_DROP_FRONTAGE_MIN_M /
--     AIR_DROP_FRONTAGE_MAX_M);
--   * the path SEGMENT test (ad_seg_dist), the velocity reads (ad_velocity) and
--     every projected point (ad_lead / ad_project);
--   * the helpers ad_frontage, ad_frontage_text, ad_seg_dist, ad_velocity,
--     ad_lead, ad_project, ad_dial_text, ad_single_say, ad_single_clear,
--     ad_centre_gap, ad_pos, ad_sep, ad_vec_text. Nothing else in the file used
--     any of them.
--   Kept: ad_tag, ad_say, ad_nearest, ad_pick.
--
-- THE FAST PASS (FOURTH.ad_fast_pass, registered beside the poll): the SAME
-- ad_pick every AIR_DROP_FAST_S = 0.2 s, for ALIVE units ARMED for an air-drop
-- marker, and only while a VALID enemy is inside AIR_DROP_NEAR_M = 30 m. The
-- global poll (POLL_MS) and every other ability's cadence are untouched, and the
-- cast goes through the same FOURTH.try_pair the poll uses.
--
-- THE FOUR CONSTANTS:
--   AIR_DROP_EDGE_M  = 0.10 m  FIRE below this edge-to-edge gap
--   AIR_DROP_MIN_MEN = 10      a candidate needs MORE alive models than this
--   AIR_DROP_NEAR_M  = 30 m    the fast pass runs while a valid enemy is closer
--   AIR_DROP_FAST_S  = 0.2 s   the fast pass interval
FOURTH.AIR_DROP_EDGE_M = 0.1
FOURTH.AIR_DROP_MIN_MEN = 10
FOURTH.AIR_DROP_NEAR_M = 30
FOURTH.AIR_DROP_FAST_S = 0.2
FOURTH.ad_note = {}
FOURTH.ad_fast_on = {}
FOURTH.ad_fast_abilities = {}

-- THE UNIT TAG: every air-drop line names the caster's engine ui id
-- (unique_ui_id); an unreadable id prints [?] rather than dropping the line.
function FOURTH.ad_tag(unit)
	local ok_id, id = pcall(function() return unit:unique_ui_id() end)
	if not ok_id or id == nil then return "[?] " end
	return "[" .. tostring(id) .. "] "
end

-- One line per (unit, marker), and again only when the note CHANGES. (In the
-- live build this writes the decision line; the reading copy only records the
-- change so the shape of the evaluator stays reviewable.)
function FOURTH.ad_say(unit, marker, note)
	local ok_id, id = pcall(function() return unit:unique_ui_id() end)
	if not ok_id or id == nil then return end
	local slot = tostring(id)
	local per = FOURTH.ad_note[slot]
	if per == nil then per = {}; FOURTH.ad_note[slot] = per end
	if per[marker] == note then return end
	per[marker] = note
end

-- ONE CANDIDATE SCAN, ONE MEASUREMENT - the whole filter, in one place, so the
-- picker and the fast pass cannot disagree about who is valid. Returns the
-- nearest valid enemy, its edge gap in metres, its CURRENT model count and its
-- type key; nil when no valid candidate exists or the enemy army is unreadable.
function FOURTH.ad_nearest(unit)
	local ok_coll, coll = pcall(function()
		return bm:get_scriptunits_for_main_enemy_army_to_local_player()
	end)
	if not ok_coll or coll == nil then return nil end
	local ok_n, n = pcall(function() return coll:count() end)
	if not ok_n or type(n) ~= "number" then return nil end
	local best, best_d, best_men, best_type = nil, nil, nil, nil
	for i = 1, n do
		local ok_su, su = pcall(function() return coll:item(i) end)
		if ok_su and su ~= nil then
			local enemy = nil
			pcall(function() enemy = su.unit end)
			if enemy ~= nil then
				local ok_alive, alive = pcall(function() return enemy:number_of_men_alive() end)
				if ok_alive and type(alive) == "number" and alive > FOURTH.AIR_DROP_MIN_MEN then
					local d = FOURTH.eg_enemy_gap(unit, enemy)
					if d ~= nil and (best_d == nil or d < best_d) then
						best, best_d, best_men = enemy, d, alive
						best_type = FOURTH.type_plain(enemy)
					end
				end
			end
		end
	end
	if best == nil then return nil end
	return best, best_d, best_men, best_type
end

-- THE AIR-DROP EVALUATOR. ONE comparison decides - the NEAREST valid enemy's
-- edge gap against AIR_DROP_EDGE_M - after the caster-side usage checks the
-- ability's own row declares. (The live build writes, on EVERY decision, the
-- distance, the entity count, the enemy type and the caster's ui id:
--     [1003] sky_junk_bomb nearest valid:'<key>' entities=N edge=0.04m
--            (need < 0.10m) -> NOT YET / FIRING)
function FOURTH.ad_pick(unit, routing)
	if routing then return nil end
	local marker = FOURTH.ad_marker or "air_drop"
	if FOURTH.ad_air_only then
		local ok_fly, flying = pcall(function() return unit:is_currently_flying() end)
		if not ok_fly or flying ~= true then
			FOURTH.ad_say(unit, marker, "airborne check: is_currently_flying() = "
				.. (ok_fly and tostring(flying) or "UNREADABLE")
				.. " -> HOLDING (this ability's row is air-only)")
			return nil
		end
	end
	if FOURTH.ad_no_melee then
		local ok_m, m = pcall(function() return unit:is_in_melee() end)
		if not ok_m then
			FOURTH.ad_say(unit, marker, "melee check: is_in_melee() UNREADABLE -> HOLDING (fail-closed)")
			return nil
		end
		if m == true then
			FOURTH.ad_say(unit, marker, "melee check: the caster is fighting in melee -> HOLDING"
				.. " (the row declares engaged_in_melee)")
			return nil
		end
	end
	local enemy, dist, men, etype = FOURTH.ad_nearest(unit)
	if enemy == nil then return nil end
	etype = etype or "enemy"
	local edge_text = string.format("%.2f", dist)
	local need = string.format("%.2f", FOURTH.AIR_DROP_EDGE_M)
	if dist >= FOURTH.AIR_DROP_EDGE_M then
		FOURTH.ad_say(unit, marker, "nearest valid:'" .. etype .. "' entities="
			.. tostring(men) .. " edge=" .. edge_text .. "m (need < " .. need .. "m) -> NOT YET")
		return nil
	end
	FOURTH.ad_enemy = enemy
	FOURTH.ad_caster_su = FOURTH.eg_fresh_caster_su(unit)
	return "nearest valid '" .. etype .. "' has " .. tostring(men) .. " models and its EDGE gap is "
		.. edge_text .. "m, under the " .. need .. "m line (unit_distance, edge-to-edge)"
end

-- THE TRIGGER NAME STAYS `air_drop_on_infantry` (the entries, the tooltip map and
-- every harness pin key on it); only the RULE behind it changed.
function FOURTH.evaluate_air_drop_on_infantry(unit, routing)
	return FOURTH.ad_pick(unit, routing)
end
