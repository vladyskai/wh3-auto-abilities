#!/usr/bin/env python3
"""Round 130 (harness 129): the first three triggers on the firing flag.

User rulings 2026-11-01: "Please implement the both recommended options" (Restock! option A,
Ballistics Calibration option A) and Skjalandir's Fall "Shooting into melee" (its melee trigger
stays). Game rows (gamedata/wh3/unit_spec_abil.tsv):
  Restock!  wh2_dlc17_hero_abilities_more_powder_generic  friends, reach 100 m (bound 70 m),
            4 uses, recharge 60 s, active 10 s, wind-up 0; effect "Replenishes ammo: 0.3000".
  Ballistics Calibration  wh_main_hero_abilities_ballistics_calibration  ground, effect_range 55 m
            (bound 38 m), affect_self, recharge 90 s, active 22 s, wind-up 0.
  Skjalandir's Fall  wh3_dlc23_character_abilities_skjalandirs_fall  self, active 39 s, recharge 120 s.
No string.find (the standing ban). Every helper is a FOURTH field (the 200-local ceiling).
"""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"

ENTRIES_ANCHOR = ('\t{ marker = "entrenchment", name = "Entrenchment", trigger = "melee_unwavering",\n'
                  '\t\tbadge = "zz_auto_badge_entrenchment",\n'
                  '\t\tkeys = { "wh_main_unit_abilities_entrenchment" },\n'
                  '\t\tox = 0, oy = 0 },\n')
ENTRIES = ('\t-- ROUND 130: the first two abilities on the firing flag (user ruling 2026-11-01).\n'
           '\t{ marker = "restock", name = "Restock!", trigger = "ally_ammo_low",\n'
           '\t\tbadge = "zz_auto_badge_restock",\n'
           '\t\tkeys = { "wh2_dlc17_hero_abilities_more_powder_generic" },\n'
           '\t\tally_range_real = 100,\n'
           '\t\tox = 0, oy = 0 },\n'
           '\t{ marker = "ballistics_calibration", name = "Ballistics Calibration", trigger = "allies_firing_aura",\n'
           '\t\tbadge = "zz_auto_badge_ballistics_calibration",\n'
           '\t\tkeys = { "wh_main_hero_abilities_ballistics_calibration" },\n'
           '\t\taura_real = 55,\n'
           '\t\tox = 0, oy = 0 },\n')

SKJ_OLD = '\t{ marker = "skjalandirs_fall", name = "Skjalandir\'s Fall", trigger = "melee_unwavering",\n'
SKJ_NEW = '\t{ marker = "skjalandirs_fall", name = "Skjalandir\'s Fall", trigger = "melee_or_shooting_into_melee",\n'

CHARGE_OLD = "local charge_gate = {\n\thold_s = {\n"
CHARGE_NEW = CHARGE_OLD + ("\t\t-- ROUND 130: Restock! - 4 uses, 60 s recharge.\n"
                           "\t\t[\"wh2_dlc17_hero_abilities_more_powder_generic\"] = 60,\n")

GROUND_OLD = '\tground_keys = {\n\t\t["wh3_dlc24_character_abilities_tacticians_stand_your_ground"] = true,\n'
GROUND_NEW = GROUND_OLD + ('\t\t-- ROUND 130: Ballistics Calibration, placed at the caster\'s own feet.\n'
                           '\t\t["wh_main_hero_abilities_ballistics_calibration"] = true,\n')

# the pre-cast re-check of the chosen ally (Class B)
RECHECK_OLD = ('\t\tlocal hp_ok_now = true\n\t\tif FOURTH.ab_family == "heal" then\n'
               '\t\t\tlocal hp = FOURTH.health_pct(ally)\n\t\t\thp_ok_now = (type(hp) ~= "number") or (hp <= 75)\n\t\tend\n')
RECHECK_NEW = RECHECK_OLD + ('\t\t-- ROUND 130: Restock! - the ally must still be shooting and still at or\n'
                             '\t\t-- below the line (a refill on a unit that stopped is wasted).\n'
                             '\t\tif FOURTH.ab_family == "ammo" then\n'
                             '\t\t\tlocal fr = FOURTH.ammo_fraction_if_firing(ally)\n'
                             '\t\t\thp_ok_now = (fr ~= nil) and (fr <= FOURTH.RESTOCK_AT_FRACTION)\n'
                             '\t\tend\n')

VALID_OLD = ('\tif FOURTH.ab_family == "heal" then\n\t\tlocal hp = FOURTH.health_pct(ally)\n'
             '\t\treturn (type(hp) ~= "number") or (hp <= 75)\n\tend\n')
VALID_NEW = VALID_OLD + ('\tif FOURTH.ab_family == "ammo" then\n'
                         '\t\tlocal fr = FOURTH.ammo_fraction_if_firing(ally)\n'
                         '\t\treturn (fr ~= nil) and (fr <= FOURTH.RESTOCK_AT_FRACTION)\n\tend\n')

ELIG_OLD = ('\t\t\t\t\telseif family == "winds" then\n'
            '\t\t\t\t\t\tval = FOURTH.context_value(other, "HealthValue")\n'
            '\t\t\t\t\t\teligible = (type(val) == "number")\n')
ELIG_NEW = ELIG_OLD + ('\t\t\t\t\telseif family == "ammo" then\n'
                       '\t\t\t\t\t\t-- ROUND 130: Restock! - shooting now, at or below the line\n'
                       '\t\t\t\t\t\tval = FOURTH.ammo_fraction_if_firing(other)\n'
                       '\t\t\t\t\t\teligible = (val ~= nil and val <= FOURTH.RESTOCK_AT_FRACTION)\n')

BETTER_OLD = ('\t\t\t\t\t\t\telseif family == "winds" then\n'
              '\t\t\t\t\t\t\t\tbetter = (type(val) == "number" and (type(best_val) ~= "number" or val > best_val))\n')
BETTER_NEW = BETTER_OLD + ('\t\t\t\t\t\t\telseif family == "ammo" then\n'
                           '\t\t\t\t\t\t\t\tbetter = (type(best_val) ~= "number" or val < best_val)\n')

# live: the reason text; annotated: the claim only
RET_LIVE_OLD = '\telseif family == "winds" then\n\t\treturn string.format("%s: highest-hit-point ally %d hp (HealthValue), cast on ally",\n'
RET_LIVE_NEW = ('\telseif family == "ammo" then\n'
                '\t\tpcall(function() FOURTH.ammo_claim_id = tostring(best_ally:unique_ui_id()) end)\n'
                '\t\treturn string.format("%s: shooting ally with the least ammunition left, %d%% (<= %d%%), cast on ally",\n'
                '\t\t\ttostring(FOURTH.ab_marker or "ally"), math.floor((best_val or 0) * 100),\n'
                '\t\t\tmath.floor(FOURTH.RESTOCK_AT_FRACTION * 100 + 0.5))\n') + RET_LIVE_OLD
RET_ANN_OLD = '\tFOURTH.cast_target = best_ally\n\treturn true\nend\n'
RET_ANN_NEW = ('\tFOURTH.cast_target = best_ally\n'
               '\tif family == "ammo" then\n'
               '\t\tpcall(function() FOURTH.ammo_claim_id = tostring(best_ally:unique_ui_id()) end)\n'
               '\tend\n\treturn true\nend\n')

FIRED_OLD = '\t\t\t\telseif outcome == "fired" then\n\t\t\t\t\t-- a real fire ends the cooldown episode\n'
FIRED_NEW = FIRED_OLD + ('\t\t\t\t\t-- ROUND 130: Restock! - the refilled ally is skipped by every caster\n'
                         '\t\t\t\t\t-- for RESTOCK_CLAIM_S, so two casters never refill it twice.\n'
                         '\t\t\t\t\tif FOURTH.ammo_claim_id ~= nil then\n'
                         '\t\t\t\t\t\tFOURTH.ammo_claimed[FOURTH.ammo_claim_id] = tick_count\n'
                         '\t\t\t\t\t\tFOURTH.ammo_claim_id = nil\n'
                         '\t\t\t\t\tend\n')

CLEAR_OLD = '\t\t\t\t\tFOURTH.ab_infinite = nil\n'
CLEAR_NEW = CLEAR_OLD + ('\t\t\t\t\t-- ROUND 130: the Restock! pick and the aura bound, cleared/set per entry\n'
                         '\t\t\t\t\tFOURTH.ammo_claim_id = nil\n'
                         '\t\t\t\t\tFOURTH.fa_bound_m = ability.aura_m\n')

EVAL_OLD = '\tally_missile = FOURTH.evaluate_ally_missile,\n'
EVAL_NEW = EVAL_OLD + ('\t-- ROUND 130: the firing-flag triggers.\n'
                       '\tally_ammo_low = FOURTH.evaluate_ally_ammo_low,\n'
                       '\tallies_firing_aura = FOURTH.evaluate_allies_firing_aura,\n'
                       '\tmelee_or_shooting_into_melee = FOURTH.evaluate_melee_or_shooting_into_melee,\n')

TIP_OLD = '\tally_missile = "When armed, fires on a missile-capable ally in range",\n'
TIP_NEW = TIP_OLD + ('\tally_ammo_low = "When armed, fires on a shooting ally in range with 70% or less of its ammunition left (the lowest first)",\n'
                     '\tallies_firing_aura = "When armed, fires when at least 2 friendly units near this unit are shooting, placed on the ground at its feet",\n'
                     '\tmelee_or_shooting_into_melee = "When armed, fires when this unit is in melee, or is shooting at an enemy that is in melee",\n')

PROBE_OLD = '\t\t\t\tFOURTH.ammo[su] = st\n'
PROBE_NEW = PROBE_OLD + ('\t\t\t\t-- ROUND 130: the same state by ui id, for the firing-flag triggers\n'
                         '\t\t\t\tpcall(function() FOURTH.ammo_by_id[tostring(u:unique_ui_id())] = st end)\n')

CP_OLD = '(nothing is cast in this round) %s",'
CP_NEW = '(the firing-flag triggers may cast from here) %s",'

HEADER = """-- ============================================================================
-- ROUND 130 - THE FIRST TRIGGERS ON THE FIRING FLAG (user rulings 2026-11-01:
-- Restock! and Ballistics Calibration "both recommended options"; Skjalandir's
-- Fall "shooting into melee"). The firing flag (round 126, FOURTH.ammo_probe) is
-- read per unit through FOURTH.ammo_by_id, which the probe fills on the same poll,
-- before any trigger runs.
--   restock (Restock!): an ally within the 70 m bound that is SHOOTING (firing
--     flag on) with RESTOCK_AT_FRACTION (70%) or less of its ammunition left; the
--     one with the least left is the cast target. 70% = 100% - the 30% the
--     ability refills, so no refill is wasted. An ally refilled in the last
--     RESTOCK_CLAIM_S is skipped, so two casters never refill the same unit.
--   ballistics_calibration: at least BALLISTICS_MIN_FIRING allies within the
--     aura bound (38 m = 70% of 55 m) are shooting and past their cast point;
--     cast on the ground at the caster's own feet (no move order).
--   skjalandirs_fall: the melee trigger it had, OR the unit itself is shooting,
--     past its cast point, at a target that is in melee.
-- ============================================================================
FOURTH.RESTOCK_AT_FRACTION = 0.70   -- 1 - the 0.30 the ability refills ("Replenishes ammo: 0.3000")
FOURTH.RESTOCK_CLAIM_S = 12         -- the ability's active_time (10 s) + IN_FLIGHT_SETTLE_SECONDS (2 s)
FOURTH.BALLISTICS_MIN_FIRING = 2    -- allies shooting inside the aura bound (user, 2026-11-01: option A)
FOURTH.ammo_by_id = {}              -- ui id (string) -> that unit's firing-flag state
FOURTH.ammo_claimed = {}            -- ui id (string) -> the poll a Restock! was cast on it
FOURTH.ammo_claim_id = nil          -- the ally the current Restock! pick chose
FOURTH.fa_bound_m = nil             -- the current entry's aura bound (set per entry by the poll)

-- the firing-flag state of a unit, and its ui id (nil when unknown)
function FOURTH.firing_state(unit)
	local id = nil
	pcall(function() id = tostring(unit:unique_ui_id()) end)
	if id == nil then return nil, nil end
	return FOURTH.ammo_by_id[id], id
end

-- the ammunition fraction left (0..1) of a unit that is SHOOTING now; nil when it
-- is not shooting, has no ammunition read, or was refilled in the last
-- RESTOCK_CLAIM_S.
function FOURTH.ammo_fraction_if_firing(unit)
	local st, id = FOURTH.firing_state(unit)
	if st == nil or st.firing ~= true or type(st.start) ~= "number" or st.start <= 0
		or type(st.last) ~= "number" then
		return nil
	end
	local at = FOURTH.ammo_claimed[id]
	if at ~= nil and (tick_count - at) < math.floor((FOURTH.RESTOCK_CLAIM_S * 1000) / POLL_MS) then
		return nil
	end
	return st.last / st.start
end

-- true while the unit is shooting AND past its cast point (first shot + 0.5 x reload)
function FOURTH.shooting_past_cast_point(unit)
	local st = FOURTH.firing_state(unit)
	return st ~= nil and st.firing == true and st.cast_point_passed == true
end

-- ally_ammo_low (Restock!): the shared ally picker, family "ammo".
function FOURTH.evaluate_ally_ammo_low(unit, routing)
	return FOURTH.ab_pick_ally(unit, routing, "ammo")
end

-- the number of OTHER friendly units (alive, not routing) within the current
-- entry's aura bound of `unit` that are shooting past their cast point. An
-- unreadable distance does not count (fail-closed).
function FOURTH.count_allies_firing_near(unit)
	local bound = FOURTH.fa_bound_m
	if bound == nil or tracked_units == nil then return 0, bound end
	local self_id = tostring(unit:unique_ui_id())
	local n = 0
	for i = 1, #tracked_units do
		local other = tracked_units[i] and tracked_units[i].unit
		if other ~= nil and other ~= unit then
			local ok_m, men = pcall(function() return other:number_of_men_alive() end)
			local ok_i, oid = pcall(function() return tostring(other:unique_ui_id()) end)
			if ok_m and type(men) == "number" and men > 0 and ok_i and oid ~= self_id
				and not unit_is_routing(other) and FOURTH.shooting_past_cast_point(other) then
				local gap = FOURTH.ab_ally_gap(unit, other)
				if gap ~= nil and gap <= bound then n = n + 1 end
			end
		end
	end
	return n, bound
end
"""

TAIL_LIVE = """
-- allies_firing_aura (Ballistics Calibration): enough shooting allies around the
-- caster; the cast is the ground form at the caster's own position (ground_keys).
function FOURTH.evaluate_allies_firing_aura(unit, routing)
	if routing then return nil end
	local n, bound = FOURTH.count_allies_firing_near(unit)
	if n < FOURTH.BALLISTICS_MIN_FIRING then return nil end
	return string.format("%s: %d allies within %sm are shooting past their cast point (need %d), cast on the ground at the caster's own position",
		tostring(FOURTH.ab_marker or "aura"), n, tostring(bound), FOURTH.BALLISTICS_MIN_FIRING)
end

-- melee_or_shooting_into_melee (Skjalandir's Fall): the in-melee self trigger it
-- had, OR the unit is shooting (past its cast point) at a target that is in
-- melee. Not while routing or wavering.
function FOURTH.evaluate_melee_or_shooting_into_melee(unit, routing)
	local r = FOURTH.evaluate_in_melee_self(unit, routing)
	if r ~= nil then return r end
	if routing or FOURTH.wavering(unit) == true then return nil end
	if not FOURTH.shooting_past_cast_point(unit) then return nil end
	local ok_t, t = pcall(function() return unit:current_target() end)
	if not ok_t or t == nil then return nil end
	local ok_m, m = pcall(function() return t:is_in_melee() end)
	if not ok_m or m ~= true then return nil end
	return "shooting past its cast point at a target that is in melee, cast on self"
end

"""

TAIL_ANN = """
-- allies_firing_aura (Ballistics Calibration): enough shooting allies around the
-- caster; the cast is the ground form at the caster's own position (ground_keys).
function FOURTH.evaluate_allies_firing_aura(unit, routing)
	if routing then return false end
	local n = FOURTH.count_allies_firing_near(unit)
	return n >= FOURTH.BALLISTICS_MIN_FIRING
end

-- melee_or_shooting_into_melee (Skjalandir's Fall): the in-melee self trigger it
-- had, OR the unit is shooting (past its cast point) at a target that is in
-- melee. Not while routing or wavering.
function FOURTH.evaluate_melee_or_shooting_into_melee(unit, routing)
	if FOURTH.evaluate_in_melee_self(unit, routing) then return true end
	if routing or FOURTH.wavering(unit) == true then return false end
	if not FOURTH.shooting_past_cast_point(unit) then return false end
	local ok_t, t = pcall(function() return unit:current_target() end)
	if not ok_t or t == nil then return false end
	local ok_m, m = pcall(function() return t:is_in_melee() end)
	return ok_m and m == true
end

"""

EVALS_ANCHOR = "FOURTH.evaluators = {\n"

COMMON = [(ENTRIES_ANCHOR, ENTRIES_ANCHOR + ENTRIES), (SKJ_OLD, SKJ_NEW), (CHARGE_OLD, CHARGE_NEW),
          (GROUND_OLD, GROUND_NEW), (RECHECK_OLD, RECHECK_NEW), (VALID_OLD, VALID_NEW),
          (ELIG_OLD, ELIG_NEW), (BETTER_OLD, BETTER_NEW), (FIRED_OLD, FIRED_NEW), (CLEAR_OLD, CLEAR_NEW),
          (EVAL_OLD, EVAL_NEW), (TIP_OLD, TIP_NEW), (PROBE_OLD, PROBE_NEW)]
PLAN = {
    SRC: COMMON + [(RET_LIVE_OLD, RET_LIVE_NEW), (CP_OLD, CP_NEW),
                   (EVALS_ANCHOR, HEADER + TAIL_LIVE + EVALS_ANCHOR)],
    ANN: COMMON + [(RET_ANN_OLD, RET_ANN_NEW), (EVALS_ANCHOR, HEADER + TAIL_ANN + EVALS_ANCHOR)],
}

if __name__ == "__main__":
    import sys
    dry = "--dry" in sys.argv
    for path, edits in PLAN.items():
        s = open(path, encoding="utf-8", newline="").read()
        assert "\r\n" not in s and "RESTOCK_AT_FRACTION" not in s, path
        for i, (a, b) in enumerate(edits, 1):
            n = s.count(a)
            assert n == 1, (path.split("\\")[-1], "edit", i, a[:60], "anchor count", n)
            s = s.replace(a, b, 1)
        added = "".join(b for _, b in edits)
        assert "\u2014" not in added and "string.find" not in added
        if path == ANN:
            assert "log(" not in TAIL_ANN + HEADER
        if not dry:
            open(path, "w", encoding="utf-8", newline="").write(s)
        print(("checked" if dry else "applied") + " %d edits:" % len(edits), path.split("\\")[-1])
