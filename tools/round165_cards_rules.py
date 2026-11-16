#!/usr/bin/env python3
"""Round 165 (harness 164): the night audit of 2026-11-16/17 (user request: "Does the ability card note ... correctly
reflect how the ability is triggered when armed? If not, please fix" and "if it only applies to flying units, and we do
not check for that, we should add the check").

  * THE CARD: the per-family sentence (FOURTH.TRIGGER_TIP -> ability.tip, round 93) was never shown anywhere: the only
    text on an ability card is the static twui line. NEW FOURTH.CARD_TIP: one corrected sentence per family with
    tokens for the entry's own numbers (its 70% range and aura bounds, blast clearances, charge window, constants);
    FOURTH.compose_card(ability) fills them at load and appends the target-class, caster-rule and ally-target clauses.
    The text goes on the ability's own M/A badge as its hover tooltip (a pcall'd SetTooltipText, the ALL badge's
    proven call). TRIGGER_TIP stays as the internal family label (old pins quote it).
  * THE CASTER RULES: GENERATED FOURTH.USAGE_TEXT (tools/gen_usage_keys.py: special_ability_to_invalid_usage_flags,
    the flags with a live read). FOURTH.usage_ok skips an attempt the game would refuse: in melee, on the ground, in
    flight, moving, wavering, below / above a health line, not a large unit. Applied per entry to the rules ALL its keys
    share. New in effect for 10 keys (Entice, Favoured by the Matriarch, both Loons, Curse of Khsar, Curse of Djaf,
    Daemon Flask of Ashak, Feaster of Souls, Eye of the Storm, Stay Here I'll Get Help); the other 50 were already
    honoured by their families.
  * THE ALLY TARGET RULES: GENERATED FOURTH.ATARGET_TEXT (special_ability_to_invalid_target_flags). The shared ally
    picker skips an ally the game would refuse: Helping Hand Lords and Heroes only; Captain of the Phoenix Guard never a
    Lord, Hero or large unit; Entrenchment never a flying unit; Whiplash never a Lord or Hero.
  * THE GROUND CAST FIX (a round 162-164 defect found by the audit): the 7 ground-only WW keys (Blue Fire of Chaos x2,
    Siegebreaker, Heaven's Gate, Lamprey's Bite, Flesh-eating Scarabs, Magma Storm) were cast in the UNIT form:
    ww_take set FOURTH.eg_ground and nothing read it. The dispatch now sends a WW pick with a ground row through the
    enemy-ground form (perform_special_ability_ground at the chosen enemy's position).
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_usage_keys as GU  # noqa: E402

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"

CARD = r'''-- ============================================================================
-- ROUND 165 - THE CARD (night audit 2026-11-17; user: "Does the ability card note
-- ... correctly reflect how the ability is triggered when armed? If not, please
-- fix. The text must be 'sufficient and necessary' style, no fillers.")
-- FOURTH.TRIGGER_TIP above was never shown anywhere (ability.tip has no reader;
-- the only card text is the static twui line), and several of its sentences hid
-- conditions. FOURTH.CARD_TIP is the corrected sentence per family. Tokens are
-- the entry's OWN numbers, filled at load by FOURTH.compose_card:
--   {IN_R} its 70% cast bound ("within N m", or "at any range" when unbounded)
--   {IN_A} its 70% aura bound ("anywhere on the field" for an army-wide aura)
--   {IN_REACH} the aura bound, else the cast bound (the health pickers' reach)
--   {CLEAR} its blast radius + SHOT_SAFE_M; {DIVE} 70% of the blast radius
--   {W1} / {W2} the WW clearance at the start / end (radius + 10 m, + the drift)
--   {WHERE} the WW ring's centre; {EXEC} / {AREA} the execute line, the strikes
--   other tokens: the named constants the evaluators test.
-- A [bracketed] part is kept only when every token in it has a value (no aura,
-- or a blast that cannot hurt our units, drops it). The finished card is the
-- ability's name, the sentence and the clauses; it is the hover tooltip of the
-- ability's own M/A badge (create_badge, STEP 5b).
-- ============================================================================
FOURTH.CARD_TIP = {
	charge = "fires when this unit runs at the enemy it is attacking, {CMIN} to {CMAX} m away and at most {CTTC} s from contact, or when it is in melee",
	charge_or_melee = "fires when this unit runs at the enemy it is attacking, {CMIN} to {CMAX} m away and at most {CTTC} s from contact, or when it is in melee",
	charge_only = "fires when this unit runs at the enemy it is attacking, {CMIN} to {CMAX} m away and at most {CTTC} s from contact",
	charge_or_wavering = "fires when this unit runs at the enemy it is attacking, {CMIN} to {CMAX} m away and at most {CTTC} s from contact, or when it is wavering",
	tired = "fires when this unit is tired, very tired or exhausted",
	melee = "fires when this unit is in melee",
	melee_low_morale = "fires when this unit is in melee and wavering",
	melee_unwavering = "fires when this unit is in melee and not wavering",
	melee_health75 = "fires when this unit is in melee and at or below 75% health",
	melee_skip_commanders = "fires when this unit is in melee, unless every enemy within {ENG} m of it (with none that close: its current target) is a Lord or Hero",
	melee_self_or_ally = "fires on this unit when it is in melee, else on the closest friendly unit {IN_R} that is in melee",
	self_summon_melee = "fires when this unit is in melee",
	barrier_broken = "fires when this unit's barrier is broken",
	ushoran_health = "fires when this unit is at or below 75% health",
	health_below_15 = "fires when this unit is below 15% health",
	self_last_stand = "fires when this unit is at or below {LS}% health while in melee or under missile fire",
	health_aura_ground = "fires on the ground under the lowest-health unit, this one or a friendly unit {IN_REACH}, once it is at or below 75% health",
	health_aura_ally = "fires on the lowest-health unit, this one or a friendly unit {IN_REACH}, once it is at or below 75% health",
	health_aura_self = "fires on this unit when it, or a friendly unit {IN_REACH}, is at or below 75% health",
	health_aura_self_undead = "fires on this unit when it, or a friendly unit {IN_REACH}, is undead and at or below 75% health",
	ally_hurt_melee = "fires on the lowest-health unit in melee, this one or a friendly unit {IN_REACH}, once it is at or below 75% health",
	glorious_death = "fires when a Slayer friendly unit within {GD} m is in melee, or when this unit is a Slayer in melee",
	verminking_wavering = "fires when a friendly unit within {VK} m is in melee and wavering",
	metallurgy_melee = "fires when this unit, or a friendly unit within {MET} m, is in melee",
	wavering_self = "fires when this unit is wavering",
	wavering_self_or_ally = "fires when this unit is wavering, or a friendly unit within {WR} m is in melee and wavering",
	wavering_ally_range = "fires on the closest wavering friendly unit {IN_R}",
	wavering_aura = "fires when this unit[, or a friendly unit {IN_A},] is wavering",
	melee_or_wavering_aura = "fires when this unit[, or a friendly unit {IN_A},] is in melee or wavering",
	blood_sacrifice = "fires on the lowest-health other friendly unit within {BS} m once it is at or below 75% health",
	eat_da_runts = "fires on this unit when it is at or below 75% health, else on the lowest-health other friendly unit within {ED} m at or below 75%",
	ally_heal = "fires on the lowest-health other friendly unit {IN_R} once it is at or below 75% health",
	ally_heal_melee = "fires when this unit is in melee, on the lowest-health other friendly unit {IN_R} at or below 75% health",
	ally_warmachine_heal = "fires on the lowest-health friendly war machine {IN_R} once it is at or below 75% health",
	ally_hellforged_heal = "fires on the lowest-health friendly Hell-Forged unit {IN_R} once it is at or below 75% health",
	ally_monster_heal = "fires on the lowest-health friendly monster {IN_R} once it is at or below 75% health",
	ally_construct_heal = "fires on the lowest-health friendly construct {IN_R} once it is at or below 75% health",
	ally_wavering = "fires on the closest wavering friendly unit {IN_R}",
	ally_melee_buff = "fires when this unit is in melee and not wavering, on the closest friendly unit {IN_R}",
	ally_overseer = "fires on the closest friendly unit {IN_R} that Overseer of the Unseen may target",
	ally_beast = "fires on the closest friendly beast unit {IN_R}",
	ally_broken = "fires on the closest friendly unit {IN_R} whose morale is broken",
	ally_missile = "fires on the closest friendly missile unit {IN_R}",
	ally_infinite_buff = "fires on the closest friendly unit, at any range",
	ally_winds = "fires on the other friendly unit {IN_R} with the most hit points left",
	ally_ammo_low = "fires on the shooting friendly unit {IN_R} with the least ammunition, once it is at or below {AMMO}% and was not refilled in the last {RC} s",
	ally_blast = "fires on the friendly unit {IN_R} (this one included) with the most enemy value inside its blast, when the blast covers enough soldiers",
	allies_firing_aura = "fires when this unit[, or a friendly unit {IN_A},] has been shooting for half a reload",
	self_or_ally_shooting = "fires on this unit when it has been shooting for half a reload, else on the closest friendly unit {IN_R} that has",
	melee_or_self_or_ally_shooting = "fires on this unit when it is in melee and not wavering, or has been shooting for half a reload; else on the closest friendly unit {IN_R} that has been shooting for half a reload",
	melee_or_shooting_self_or_ally = "fires on this unit when it is in melee and not wavering, or has been shooting for half a reload; else on the closest friendly unit {IN_R} that is in melee or has been shooting",
	melee_or_shooting_aura = "fires when this unit, or a friendly unit within {MET} m, is in melee, or when this unit[ or a friendly unit {IN_A}] has been shooting for half a reload",
	melee_or_shooting_into_melee = "fires when this unit is in melee and not wavering, or has been shooting for half a reload at an enemy in melee",
	self_shooting = "fires when this unit has been shooting for half a reload",
	self_shooting_clear = "fires when this unit has been shooting for half a reload at a target that is not in melee",
	self_shooting_healthy = "fires when this unit has been shooting for half a reload and is above 50% health",
	self_out_of_ammo = "fires when this unit has no ammunition left",
	self_moving = "fires when this unit is moving",
	self_running = "fires when this unit is running",
	no_enemy_in_range_within_boost = "fires when this unit, out of melee and with ammunition, has no enemy within its missile range but one within {FSB} times that range",
	ground_ally_before_range = "fires on the ground under the closest friendly missile unit {IN_R} (this one included) that is out of melee, has ammunition, and has no enemy within its range but one within {MIST} times it",
	under_fire = "fires when this unit[, or a friendly unit {IN_A},] is under missile fire",
	melee_or_under_fire = "fires when this unit is in melee and not wavering, or is under missile fire[, or when a friendly unit {IN_A} is in melee or under missile fire]",
	self_recharging = "fires while another ability the mod cast on this unit is active or recharging",
	self_recharging_2 = "fires while two other abilities the mod cast on this unit are active or recharging",
	recharging_in_reach = "fires while this unit, or a friendly unit {IN_R}, has an ability the mod cast still active or recharging",
	when_ready = "fires as soon as it is ready",
	enemy_engaged_or_shot = "fires on the closest enemy {IN_R} in melee, else on the closest one under missile fire",
	enemy_ground_area = "fires on the ground under the closest enemy {IN_R} in melee, else under the closest one under missile fire",
	enemy_melee = "fires on the closest enemy {IN_R} that is in melee",
	enemy_ground_melee = "fires at the closest enemy {IN_R} that is in melee",
	enemy_ground_melee_infantry = "fires at the closest enemy infantry unit {IN_R} that is in melee, never a Lord or Hero",
	enemy_melee_noncommander = "fires on the closest enemy {IN_R} in melee, never a Lord or Hero",
	enemy_low_health_noncommander = "fires on the lowest-health enemy {IN_R} below {HL}% health, never a Lord or Hero",
	enemy_wavering = "fires on the closest wavering enemy {IN_R}",
	enemy_missile_shooting = "fires on the closest enemy missile unit {IN_R} that is shooting and not in melee",
	enemy_ground_shooting = "fires on the ground under the closest enemy missile unit {IN_R} that is shooting and not in melee",
	enemy_melee_or_shooting = "fires on the closest enemy {IN_R} in melee, else on the closest enemy missile unit that is shooting",
	enemy_fast_near_ally = "fires on a moving enemy {IN_R} with a run speed of {FAST} m/s or more that is within {NEAR} m of one of your units",
	enemy_melee_or_fast = "fires on the closest enemy {IN_R} in melee, else on a moving enemy with a run speed of {FAST} m/s or more within {NEAR} m of your units",
	enemy_commander_value = "fires on the most valuable visible enemy Lord or Hero {IN_R}",
	enemy_single_drain = "fires, while this unit stands still, on the most valuable visible single-entity enemy {IN_R}",
	enemy_execute = "fires on the most valuable visible enemy {IN_R} at or below {EXEC}% health",
	enemy_area_drain = "fires, while this unit stands still, on the visible enemy infantry {IN_R} worth the most per soldier that has at least {AREA} soldiers",
	enemy_large_shot = "fires on the most valuable visible large enemy {IN_R} with none of your units within {SAFE} m of it, else on the most armoured enemy infantry",
	enemy_single_shot = "fires, while this unit stands still, on the most valuable visible single-entity enemy {IN_R} with none of your units within {SAFE} m of it",
	enemy_infantry_shot = "fires, while this unit stands still, on the visible enemy infantry {IN_R} worth the most per soldier, with none of your units within {SAFE} m of it",
	enemy_blob = "fires, while this unit stands still, at the visible enemy {IN_R} where the blast destroys the most value, when it covers enough soldiers and none of your units are within {CLEAR} m of the target",
	enemy_blob_vortex = "fires, while this unit stands still, at the visible enemy {IN_R} where the blast destroys the most value, when it covers enough soldiers and none of your units are within {CLEAR} m of the target",
	enemy_wave = "fires its wave, while this unit and the target stand still, at the visible enemy {IN_R} whose path holds the most enemy value[, with none of your other units {WPATH}]",
	enemy_wave_charge = "fires its wave, while this unit stands still, at a moving enemy {IN_R} with a run speed of {FAST} m/s or more within {NEAR} m of your units[, with none of your other units {WPATH}]",
	enemy_wander = "fires, while this unit and the target stand still, at the visible enemy {IN_R} where the blast destroys the most value[, with none of your units within {W2} m of {WHERE}]",
	enemy_strike = "strikes, while this unit stands still, the ground under the most valuable standing single-entity enemy {IN_R}[, with none of your units within {W1} m of it]",
	enemy_cone = "breathes, while this unit stands still, through the standing visible enemy {IN_R} whose cone holds the most enemy value[, with none of your other units within {W2} m of the cone]",
	enemy_sweep = "fires when this unit is in melee and not wavering, at the closest enemy in melee {IN_R}, with none of your other units within {W1} m of this unit",
	melee_clear = "fires when this unit is in melee and not wavering, with none of your other units within {CLEAR} m of it",
	fly_dive = "fires when this unit is flying with an enemy within {DIVE} m of its centre and none of your other units within {CLEAR} m",
	last_stand_clear = "fires when this unit is at or below {LS}% health in melee, with none of your other units within {CLEAR} m",
	air_drop_on_infantry = "fires when the centre of the nearest enemy with more than {ADMEN} soldiers is within {AD} m of this unit's centre",
}
-- the entry's enemy target class (round 135 onward), as a clause
FOURTH.CARD_CLASS = {
	commander = "Lords and Heroes only",
	commander_ground = "Lords and Heroes on the ground only[, none of your units within {CLEAR} m of it]",
	large = "large targets only",
	large_single = "single large targets only (monsters, mounted characters)",
	single = "single-entity targets only",
	not_flying = "never a flying target",
	flying = "flying targets only",
	not_undead = "never an undead target",
	missile = "missile units only",
}
-- a clause the family's sentence already states is left out
FOURTH.CARD_SKIP = { enemy_commander_value = { commander = true }, enemy_single_shot = { single = true },
	enemy_single_drain = { single = true }, fly_dive = { G = true } }
-- the families whose target is chosen by the shared ally picker (ab_pick_ally): the only ones the ally target
-- rules apply to
FOURTH.CARD_ALLY_FAMILY = { ally_heal = true, ally_heal_melee = true, ally_wavering = true, ally_melee_buff = true,
	ally_overseer = true, ally_beast = true, ally_broken = true, ally_missile = true, ally_warmachine_heal = true,
	ally_hellforged_heal = true, ally_monster_heal = true, ally_construct_heal = true, ally_infinite_buff = true,
	ally_winds = true, ally_ammo_low = true, self_or_ally_shooting = true, melee_or_shooting_self_or_ally = true,
	recharging_in_reach = true, melee_self_or_ally = true, melee_or_self_or_ally_shooting = true }
-- the game's caster rules (FOURTH.USAGE_TEXT) and ally target rules (FOURTH.ATARGET_TEXT), as clauses
FOURTH.CARD_USAGE = { M = "not while this unit is in melee", G = "only while this unit flies",
	F = "not while this unit flies", V = "not while this unit moves", W = "not while this unit wavers",
	L = "only when this unit is a large unit" }
FOURTH.CARD_ATARGET = { C = "the ally must be a Lord or Hero", c = "never on a Lord or Hero",
	L = "large allies only", l = "never on a large unit", F = "never on a flying unit", U = "undead allies only",
	u = "never on an undead unit", S = "single-entity allies only", P = "missile allies only" }
-- the clause order on the card (pairs() order is not fixed)
FOURTH.CARD_USAGE_ORDER = { "M", "G", "F", "V", "W", "L" }
FOURTH.CARD_ATARGET_ORDER = { "C", "c", "L", "l", "F", "U", "u", "S", "P" }

function FOURTH.card_num(v)
	if type(v) ~= "number" then return nil end
	if v == math.floor(v) then return string.format("%d", v) end
	return string.format("%.1f", v)
end

function FOURTH.card_within(m)
	if type(m) ~= "number" then return nil end
	if m < 0 then return "anywhere on the field" end
	return "within " .. FOURTH.card_num(m) .. " m"
end

-- the entry's token values (nil = not available for this entry)
function FOURTH.card_tokens(ability)
	local t = {}
	local key = ability.keys and ability.keys[1]
	if ability.range_m ~= nil then t.IN_R = FOURTH.card_within(ability.range_m)
	elseif ability.unbounded == true then t.IN_R = "at any range" end
	t.IN_A = FOURTH.card_within(ability.aura_m)
	t.IN_REACH = FOURTH.card_within(ability.aura_m or ability.range_m)
	local blast = key and (FOURTH.BLAST_R[key] or FOURTH.VORTEX_R[key])
	if blast ~= nil then
		t.CLEAR = FOURTH.card_num(blast + FOURTH.SHOT_SAFE_M)
		t.DIVE = FOURTH.card_num(math.floor(blast * FOURTH.RANGE_FRACTION + 1e-9))
	end
	local row = key and FOURTH.WW[key]
	if row ~= nil and row.allies then
		t.W1 = FOURTH.card_num(math.floor(row.r + FOURTH.SHOT_SAFE_M + 0.5))
		t.W2 = FOURTH.card_num(math.floor(row.r + row.buf + FOURTH.SHOT_SAFE_M + 0.5))
		t.WHERE = (row.kind == 6) and "this unit" or "the target"
		if t.W1 == t.W2 then
			t.WPATH = "within " .. t.W1 .. " m of the path"
		else
			t.WPATH = "within " .. t.W1 .. " m of the path at its start, widening to " .. t.W2 .. " m at its end"
		end
	end
	if key and FOURTH.EXEC[key] then t.EXEC = FOURTH.card_num(math.floor(FOURTH.EXEC[key] * 100 + 0.5)) end
	if key then t.AREA = FOURTH.card_num(FOURTH.AREA_N[key] or 25) end
	t.CMIN, t.CMAX = FOURTH.card_num(CHARGE_MIN_DISTANCE_M), FOURTH.card_num(CHARGE_MAX_DISTANCE_M)
	t.CTTC = FOURTH.card_num(CHARGE_TIME_TO_CONTACT_S)
	t.GD = FOURTH.card_num(GLORIOUS_DEATH_RANGE_M)
	t.VK, t.WR = FOURTH.card_num(FOURTH.VERMINKING_RANGE_M), FOURTH.card_num(FOURTH.WAVERING_RANGE_M)
	t.MET = FOURTH.card_num(FOURTH.METALLURGY_RANGE_M)
	t.BS, t.ED = FOURTH.card_num(FOURTH.BLOOD_SACRIFICE_RANGE_M), FOURTH.card_num(FOURTH.EAT_DA_RUNTS_RANGE_M)
	t.LS, t.HL = FOURTH.card_num(FOURTH.LAST_STAND_PCT), FOURTH.card_num(FOURTH.HEALTH_LINE_PCT)
	t.AD, t.ADMEN = FOURTH.card_num(FOURTH.AIR_DROP_CENTER_M), FOURTH.card_num(FOURTH.AIR_DROP_MIN_MEN)
	t.ENG = FOURTH.card_num(FOURTH.ENGAGE_CONTACT_M)
	t.RC = FOURTH.card_num(FOURTH.RESTOCK_CLAIM_S)
	t.AMMO = FOURTH.card_num(math.floor(FOURTH.RESTOCK_AT_FRACTION * 100 + 0.5))
	t.FAST, t.NEAR = FOURTH.card_num(FOURTH.FAST_ENEMY_MPS), FOURTH.card_num(FOURTH.FAST_ENEMY_NEAR_M)
	t.SAFE = FOURTH.card_num(FOURTH.SHOT_SAFE_M)
	t.FSB = string.format("%.2f", FOURTH.FARSIGHT_BAND)
	t.MIST = string.format("%.2f", FOURTH.MIST_BAND)
	return t
end

-- fill one template: [parts] with a missing token are dropped; a missing token outside brackets stays visible
function FOURTH.card_fill(tpl, t)
	local s = string.gsub(tpl, "%[([^%]]*)%]", function(part)
		local ok = true
		string.gsub(part, "{([%u_%d]+)}", function(n) if t[n] == nil then ok = false end end)
		if not ok then return "" end
		return part
	end)
	s = string.gsub(s, "{([%u_%d]+)}", function(n) return t[n] end)
	return s
end

function FOURTH.compose_card(ability)
	local tpl = FOURTH.CARD_TIP[ability.trigger]
	if tpl == nil then return nil end
	local t = FOURTH.card_tokens(ability)
	local parts = { FOURTH.card_fill(tpl, t) }
	local skip = FOURTH.CARD_SKIP[ability.trigger] or {}
	if ability.target_class ~= nil and FOURTH.CARD_CLASS[ability.target_class] ~= nil
		and not skip[ability.target_class] then
		parts[#parts + 1] = FOURTH.card_fill(FOURTH.CARD_CLASS[ability.target_class], t)
	end
	local u = ability.usage
	if u ~= nil then
		for _, c in ipairs(FOURTH.CARD_USAGE_ORDER) do
			if u[c] and not skip[c] then parts[#parts + 1] = FOURTH.CARD_USAGE[c] end
		end
		if u.hmin ~= nil then parts[#parts + 1] = "not below " .. FOURTH.card_num(u.hmin) .. "% health" end
		if u.hmax ~= nil then parts[#parts + 1] = "only at or below " .. FOURTH.card_num(u.hmax) .. "% health" end
	end
	local a = ability.atarget
	if a ~= nil then
		for _, c in ipairs(FOURTH.CARD_ATARGET_ORDER) do
			if a[c] then parts[#parts + 1] = FOURTH.CARD_ATARGET[c] end
		end
	end
	return tostring(ability.name) .. " on A: " .. table.concat(parts, "; ") .. "."
end

for _, ability in ipairs(ABILITIES) do
	ability.usage = FOURTH.entry_usage(ability)
	ability.atarget = FOURTH.CARD_ALLY_FAMILY[ability.trigger] and FOURTH.entry_codes(ability, FOURTH.ATARGET_BY_KEY) or nil
	ability.card = FOURTH.compose_card(ability)
end

'''

RULES_HEAD = r'''-- ============================================================================
-- ROUND 165 - THE GAME'S CASTER RULES AND ALLY TARGET RULES (night audit
-- 2026-11-17; user: "if it only applies to flying units, and we do not check for
-- that, we should add the check").
--   USAGE (special_ability_to_invalid_usage_flags): the states in which the game
--     refuses the cast. FOURTH.usage_ok (called first in FOURTH.try_pair) skips
--     the attempt while the live read says the caster is in such a state. Codes:
--     M in melee, G on the ground (only while flying), F flying, V moving,
--     W wavering, hN below N% health, HN above N% health, L not a large unit.
--   ATARGET (special_ability_to_invalid_target_flags): the shared ally picker
--     (ab_filter_ok) skips an ally the game would refuse. Codes: C must be a Lord
--     or Hero, c never one, L must be large, l never large, F never flying,
--     U must be undead, u never undead, S single entity, P missile unit.
--   An entry applies only the rules ALL its keys share (a variant's own rule is
--   not forced on the others). Unreadable reads never block (the game still has
--   the last word), except L, which needs the GENERATED large set.
-- ============================================================================
'''

RULES_TAIL = r'''FOURTH.USAGE_BY_KEY, FOURTH.ATARGET_BY_KEY = {}, {}
function FOURTH.load_rule_tables()   -- a function, so the loops add no main-chunk locals
	for k, c in string.gmatch(FOURTH.USAGE_TEXT, "([^;=]+)=([^;]+)") do FOURTH.USAGE_BY_KEY[k] = c end
	for k, c in string.gmatch(FOURTH.ATARGET_TEXT, "([^;=]+)=([^;]+)") do FOURTH.ATARGET_BY_KEY[k] = c end
end
FOURTH.load_rule_tables()

-- the codes every key of the entry carries (nil when none is shared)
function FOURTH.entry_codes(ability, by_key)
	local common = nil
	for _, k in ipairs(ability.keys) do
		local set = {}
		for c in string.gmatch(by_key[k] or "", "[^%.]+") do set[c] = true end
		if common == nil then
			common = set
		else
			for c in pairs(common) do
				if not set[c] then common[c] = nil end
			end
		end
	end
	if common == nil or next(common) == nil then return nil end
	return common
end

-- the entry's caster rules: the shared codes, with the health lines as numbers (hmin: refused below, hmax: above)
function FOURTH.entry_usage(ability)
	local codes = FOURTH.entry_codes(ability, FOURTH.USAGE_BY_KEY)
	if codes == nil then return nil end
	local u = {}
	for c in pairs(codes) do
		local head = string.sub(c, 1, 1)
		if head == "h" then
			u.hmin = tonumber(string.sub(c, 2))
		elseif head == "H" then
			u.hmax = tonumber(string.sub(c, 2))
		else
			u[c] = true
		end
	end
	return u
end

-- the reason the game would refuse this caster now, or nil
function FOURTH.usage_block(unit, u)
	if u.M then
		local ok, v = pcall(function() return unit:is_in_melee() end)
		if ok and v == true then return "in melee" end
	end
	if u.G then
		local ok, v = pcall(function() return unit:is_currently_flying() end)
		if ok and v == false then return "on the ground (it must fly)" end
	end
	if u.F then
		local ok, v = pcall(function() return unit:is_currently_flying() end)
		if ok and v == true then return "flying" end
	end
	if u.V then
		local ok, v = pcall(function() return unit:is_moving() end)
		if ok and v == true then return "moving" end
	end
	if u.W and FOURTH.wavering(unit) == true then return "wavering" end
	if u.L and not FOURTH.class_member(unit, "large") then return "not a large unit" end
	if u.hmin ~= nil or u.hmax ~= nil then
		local hp = FOURTH.health_pct(unit)
		if type(hp) == "number" then
			if u.hmin ~= nil and hp < u.hmin then
				return string.format("at %d%% health (refused below %d%%)", math.floor(hp), u.hmin)
			end
			if u.hmax ~= nil and hp > u.hmax then
				return string.format("at %d%% health (refused above %d%%)", math.floor(hp), u.hmax)
			end
		end
	end
	return nil
end

FOURTH.usage_said = {}
function FOURTH.usage_ok(unit, ability, ui_id)
	local u = ability.usage
	if u == nil then return true end
	local why = FOURTH.usage_block(unit, u)
	local per = FOURTH.usage_said[tostring(ui_id)]
	if per == nil then
		per = {}
		FOURTH.usage_said[tostring(ui_id)] = per
	end
	if why == nil then
		per[ability.marker] = nil
		return true
	end
	if per[ability.marker] ~= why then
		per[ability.marker] = why
		log("  usage rule " .. tostring(ability.marker) .. " on ui id " .. tostring(ui_id) .. ": the game refuses it while the caster is " .. why .. " - not attempted")
	end
	return false
end

-- the shared ally picker's target rules for the CURRENT entry (FOURTH.ab_atarget, set by the poll)
FOURTH.ab_atarget = nil
function FOURTH.ab_atarget_ok(unit)
	local a = FOURTH.ab_atarget
	if a == nil then return true end
	if a.C or a.c then
		local cmd = FOURTH.enemy_is_commander(unit)
		if a.C and not cmd then return false end
		if a.c and cmd then return false end
	end
	if a.L and not FOURTH.class_member(unit, "large") then return false end
	if a.l and FOURTH.class_member(unit, "large") then return false end
	if a.F then
		local ok, v = pcall(function() return unit:is_currently_flying() end)
		if ok and v == true then return false end
	end
	if a.U and not FOURTH.class_member(unit, "undead") then return false end
	if a.u and FOURTH.class_member(unit, "undead") then return false end
	if a.S and not FOURTH.class_member(unit, "single") then return false end
	if a.P and not FOURTH.class_member(unit, "missile") then return false end
	return true
end

'''


def strip_logs(block):
    """the annotated reading copy carries no log calls: drop the log statements of a block"""
    out = [line for line in block.split("\n") if not line.strip().startswith("log(")]
    return "\n".join(out)


TIP_ANCHOR = "-- THE TOOLTIP LINE (this round): the short sentence the mod appends to an\n"
LOOP_END = "\t\tability.aura_m = math.floor(ability.aura_real * FOURTH.RANGE_FRACTION + 1e-9)\n\tend\nend\n"
TRY_HEAD = "function FOURTH.try_pair(script_unit, unit, ability, ui_id, ability_key, reason, gone_ids)\n"
TRY_NEW = TRY_HEAD + ("\t\t-- ROUND 165: the game's caster rules (FOURTH.USAGE_TEXT): an attempt the game would refuse is\n"
                      "\t\t-- not made (the shared gates below never see it).\n"
                      "\t\tif not FOURTH.usage_ok(unit, ability, ui_id) then return nil end\n")
AB_SLOT = "\t\t\t\t\tFOURTH.ab_marker = ability.marker\n"
AB_SLOT_NEW = AB_SLOT + "\t\t\t\t\tFOURTH.ab_atarget = ability.atarget   -- ROUND 165: the game's ally target rules\n"
FILTER_OLD = "function FOURTH.ab_filter_ok(unit)\n\tlocal f = FOURTH.ab_filter\n\tif f == nil then return true end\n"
FILTER_NEW = ("function FOURTH.ab_filter_ok(unit)\n"
              "\t-- ROUND 165: the game's ally target rules for this entry (FOURTH.ATARGET_TEXT) come first\n"
              "\tif not FOURTH.ab_atarget_ok(unit) then return false end\n"
              "\tlocal f = FOURTH.ab_filter\n\tif f == nil then return true end\n")
GROUND_OLD = "\telseif FOURTH.enemy_ground_keys[ability_key] == true then\n"
GROUND_NEW = ("\t-- ROUND 165: a WW pick whose row is ground-only (Blue Fire of Chaos x2, Siegebreaker, Heaven's Gate, Lamprey's\n"
              "\t-- Bite, Flesh-eating Scarabs, Magma Storm) is placed on the chosen enemy's ground too: ww_take sets\n"
              "\t-- FOURTH.eg_ground, which nothing read before (rounds 162-164 cast them in the unit form).\n"
              "\telseif FOURTH.enemy_ground_keys[ability_key] == true\n"
              "\t\tor (FOURTH.eg_arm == \"ww\" and FOURTH.eg_ground == true) then\n")
STEP6 = "\t-- STEP 6 - place"
STEP5B = ("\t-- STEP 5b (ROUND 165) - THE CARD: the ability's own trigger text (FOURTH.compose_card) as the badge's\n"
          "\t-- hover tooltip, through the ALL badge's proven pcall'd SetTooltipText. A template that shows no\n"
          "\t-- tooltip simply shows none; a raise never fails the badge.\n"
          "\tif ability.card ~= nil then\n"
          "\t\tlocal ok_tip, tip_err = pcall(function() state.badge:SetTooltipText(ability.card, true) end)\n"
          "\t\tlog(\"   badge [\" .. marker .. \"] card tooltip ok=\" .. tostring(ok_tip)\n"
          "\t\t\t.. (ok_tip and \"\" or (\" (\" .. tostring(tip_err) .. \")\")))\n"
          "\tend\n\n")


def main():
    src_txt = open(SRC, encoding="utf-8").read()
    usage = GU.derive(src_txt)
    atarget = GU.derive_target(src_txt)
    gen = GU.lua_block(usage) + ("-- GENERATED by tools/gen_usage_keys.py from special_ability_to_invalid_target_flags (round\n"
                                 "-- 165, the game's ally target rules); the build refuses a pack whose table differs.\n"
                                 "FOURTH.ATARGET_TEXT = \"%s\"\n" % GU.target_text(atarget))
    print("usage keys", len(usage), "target keys", len(atarget))
    for path, live in ((SRC, True), (ANN, False)):
        s = open(path, encoding="utf-8", newline="").read()
        assert "FOURTH.CARD_TIP" not in s and "USAGE_TEXT" not in s
        rules = RULES_HEAD + gen + RULES_TAIL
        card = CARD
        step5b = STEP5B
        if not live:
            rules = strip_logs(rules)
            step5b = ("\t-- STEP 5b (ROUND 165) - THE CARD: the ability's own trigger text as the badge's hover tooltip.\n"
                      "\tif ability.card ~= nil then\n"
                      "\t\tpcall(function() state.badge:SetTooltipText(ability.card, true) end)\n"
                      "\tend\n\n")
        assert "log(" not in rules or live
        reps = [(TIP_ANCHOR, rules + TIP_ANCHOR), (LOOP_END, LOOP_END + "\n" + card), (TRY_HEAD, TRY_NEW),
                (AB_SLOT, AB_SLOT_NEW), (FILTER_OLD, FILTER_NEW), (GROUND_OLD, GROUND_NEW), (STEP6, step5b + STEP6)]
        for a, b in reps:
            assert s.count(a) == 1, (path[-12:], a[:60], s.count(a))
            s = s.replace(a, b)
        assert "\u2014" not in s
        open(path, "w", encoding="utf-8", newline="").write(s)
        print(path, "patched")


if __name__ == "__main__":
    main()
