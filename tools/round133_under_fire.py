#!/usr/bin/env python3
"""Round 133 (harness 132): audit batch 2 - protection against shots fires when under fire.

User rulings 2026-11-08 (audit group R5, both as recommended):
  * pure missile protection - Shield of Chaqua (aura 55 m), The Golden Eye of Tzeentch, The Lion's
    Shield: "When under fire" (no melee arm);
  * mixed protection - The Blessed Helm of the Oblast (aura 35 m), The Bane Shield (aura 35 m),
    Charmed Shield, Glacial Defence: "In melee or under fire".
The read: battle_unit:is_under_missile_attack(), already used on enemies; only an exact true counts
(fail-closed). No string.find. Every helper is a FOURTH field.
"""
import sys

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"

RETRIGGER = {
    "shield_of_chaqua": ("under_fire", "aura_real = 55"),
    "the_golden_eye_of_tzeentch": ("under_fire", None),
    "lions_shield": ("under_fire", None),
    "blessed_helm_of_the_oblast": ("melee_or_under_fire", "aura_real = 35"),
    "the_bane_shield": ("melee_or_under_fire", "aura_real = 35"),
    "charmed_shield": ("melee_or_under_fire", None),
    "glacial_defence": ("melee_or_under_fire", None),
}


def apply_roster(s):
    for m, (trig, extra) in RETRIGGER.items():
        tag = '\t{ marker = "%s",' % m
        assert s.count(tag) == 1, m
        a = s.index(tag)
        b = s.index("ox = 0, oy = 0 },\n", a) + len("ox = 0, oy = 0 },\n")
        block = s[a:b]
        assert block.count("\n") <= 5 and 'trigger = "melee_unwavering",' in block, (m, block)
        nb = block.replace('trigger = "melee_unwavering",', 'trigger = "%s",' % trig)
        if extra:
            nb = nb.replace("\t\tox = 0, oy = 0 },\n", "\t\t%s,\n\t\tox = 0, oy = 0 },\n" % extra)
        s = s[:a] + nb + s[b:]
    return s


BLOCK_COMMON = """-- ============================================================================
-- ROUND 133 - AUDIT BATCH 2: PROTECTION AGAINST SHOTS (user rulings 2026-11-08).
--   under_fire (Shield of Chaqua, The Golden Eye of Tzeentch, The Lion's Shield):
--     the caster under missile fire; for an aura (Shield of Chaqua) also any
--     friendly unit within the aura bound (70% of the effect_range). No melee arm.
--   melee_or_under_fire (The Blessed Helm of the Oblast, The Bane Shield, Charmed
--     Shield, Glacial Defence): the caster in melee (not wavering) or under fire;
--     for an aura also any friendly unit within the bound in melee or under fire.
--   The read is battle_unit:is_under_missile_attack() (the enemy picker's read);
--   only an exact true counts. Cast on the caster.
-- ============================================================================

-- true only when the engine answers exactly true
function FOURTH.under_fire(unit)
	local ok, v = pcall(function() return unit:is_under_missile_attack() end)
	return ok and v == true
end

-- the closest OTHER friendly unit (alive, not routing) within the current entry's
-- aura bound that passes test(u); nil when the entry has no aura or none passes.
-- An unreadable distance does not count.
function FOURTH.ally_in_aura(unit, test)
	local bound = FOURTH.fa_bound_m
	if bound == nil or tracked_units == nil then return nil, nil end
	local self_id = tostring(unit:unique_ui_id())
	local best, best_gap = nil, nil
	for i = 1, #tracked_units do
		local other = tracked_units[i] and tracked_units[i].unit
		if other ~= nil and other ~= unit then
			local ok_m, men = pcall(function() return other:number_of_men_alive() end)
			local ok_i, oid = pcall(function() return tostring(other:unique_ui_id()) end)
			if ok_m and type(men) == "number" and men > 0 and ok_i and oid ~= self_id
				and not unit_is_routing(other) and test(other) then
				local gap = FOURTH.ab_ally_gap(unit, other)
				if gap ~= nil and gap <= bound and (best_gap == nil or gap < best_gap) then
					best, best_gap = other, gap
				end
			end
		end
	end
	return best, best_gap
end

function FOURTH.melee_now(u)
	local ok, v = pcall(function() return u:is_in_melee() end)
	return ok and v == true
end

function FOURTH.melee_or_under_fire(u)
	return FOURTH.melee_now(u) or FOURTH.under_fire(u)
end

"""
EVALS_LIVE = """function FOURTH.evaluate_under_fire(unit, routing)
	if routing then return nil end
	if FOURTH.under_fire(unit) then return "the caster is under missile fire, cast on self" end
	local ally, gap = FOURTH.ally_in_aura(unit, FOURTH.under_fire)
	if ally == nil then return nil end
	return string.format("a friendly unit %.1fm away (bound %sm) is under missile fire, cast centred on the caster",
		gap, tostring(FOURTH.fa_bound_m))
end

function FOURTH.evaluate_melee_or_under_fire(unit, routing)
	local r = FOURTH.evaluate_in_melee_self(unit, routing)
	if r ~= nil then return r .. ", cast on self" end
	if routing then return nil end
	if FOURTH.under_fire(unit) then return "the caster is under missile fire, cast on self" end
	local ally, gap = FOURTH.ally_in_aura(unit, FOURTH.melee_or_under_fire)
	if ally == nil then return nil end
	return string.format("a friendly unit %.1fm away (bound %sm) is in melee or under missile fire, cast centred on the caster",
		gap, tostring(FOURTH.fa_bound_m))
end

"""
EVALS_ANN = """function FOURTH.evaluate_under_fire(unit, routing)
	if routing then return false end
	if FOURTH.under_fire(unit) then return true end
	return FOURTH.ally_in_aura(unit, FOURTH.under_fire) ~= nil
end

function FOURTH.evaluate_melee_or_under_fire(unit, routing)
	if FOURTH.evaluate_in_melee_self(unit, routing) then return true end
	if routing then return false end
	if FOURTH.under_fire(unit) then return true end
	return FOURTH.ally_in_aura(unit, FOURTH.melee_or_under_fire) ~= nil
end

"""
EVALS_ANCHOR = "FOURTH.evaluators = {\n"
MAP_OLD = "\tself_shooting = FOURTH.evaluate_self_shooting,\n"
MAP_NEW = MAP_OLD + ("\t-- ROUND 133\n"
                     "\tunder_fire = FOURTH.evaluate_under_fire,\n"
                     "\tmelee_or_under_fire = FOURTH.evaluate_melee_or_under_fire,\n")
TIP_OLD = '\tself_shooting = "When armed, fires when this unit is shooting",\n'
TIP_NEW = TIP_OLD + (
    '\tunder_fire = "When armed, fires when this unit (or, for an aura, a friendly unit near it) is under missile fire",\n'
    '\tmelee_or_under_fire = "When armed, fires when this unit (or, for an aura, a friendly unit near it) is in melee or under missile fire",\n')

COMMON = [(MAP_OLD, MAP_NEW), (TIP_OLD, TIP_NEW)]
PLAN = {SRC: COMMON + [(EVALS_ANCHOR, BLOCK_COMMON + EVALS_LIVE + EVALS_ANCHOR)],
        ANN: COMMON + [(EVALS_ANCHOR, BLOCK_COMMON + EVALS_ANN + EVALS_ANCHOR)]}

if __name__ == "__main__":
    dry = "--dry" in sys.argv
    for path, edits in PLAN.items():
        s = open(path, encoding="utf-8", newline="").read()
        assert "\r\n" not in s and "evaluate_under_fire" not in s, path
        s = apply_roster(s)
        for i, (a, b) in enumerate(edits, 1):
            n = s.count(a)
            assert n == 1, (path.split("\\")[-1], "edit", i, a[:60], "anchor count", n)
            s = s.replace(a, b, 1)
        added = "".join(b for _, b in edits)
        assert "\u2014" not in added and "string.find" not in added and "and not routing" not in added
        if path == ANN:
            assert "log(" not in EVALS_ANN + BLOCK_COMMON
        if not dry:
            open(path, "w", encoding="utf-8", newline="").write(s)
        print(("checked" if dry else "applied") + " %d edits + roster:" % len(edits), path.split("\\")[-1])
