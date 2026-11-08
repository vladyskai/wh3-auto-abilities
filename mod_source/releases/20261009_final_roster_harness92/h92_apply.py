# -*- coding: utf-8 -*-
"""FINAL ROSTER BUILD - apply the 7 built individuals to the LIVE mod and the
ANNOTATED reading copy.

The 12 triage individuals resolve as (per WH3_remaining_triage.md section 3):
  BUILT (7):  Blood Sacrifice, Eat da Runts!, Locus of Virulence,
              The Dance of Dreaming, The Waltz of Lethargy, Ultimate Verdict,
              Touched by the Moon
  EXCLUDED (5): More Powder!, Ominous Powder, Restock! (x2), The Soulstealer

Touched by the Moon carries an `army_abilities` game key, which the repo's
STANDING RULE 10 / army-bar exclusion (and the four hard army-bar checks in the
harness plus the build script's own assertion) forbid shipping. It is therefore
resolved as `excluded (auto: army-bar ability (standing rule 10))` - the same
settled status the other 98 army-bar rows already carry - so the built set is
SIX entries:

  Blood Sacrifice        -> NEW trigger blood_sacrifice   (ally-heal, <=75%)
  Eat da Runts!          -> NEW trigger eat_da_runts      (self-or-ally heal, <=75%)
  Locus of Virulence     -> melee_unwavering  (in-melee self)
  The Dance of Dreaming  -> melee_unwavering  (in-melee self)
  The Waltz of Lethargy  -> melee_unwavering  (in-melee self)
  Ultimate Verdict       -> melee_unwavering  (in-melee self)

6 new entries / 6 new keys -> the abilities table grows 573 -> 579 entries
(599 -> 605 keys); melee_unwavering 477 -> 481; two NEW triggers
(blood_sacrifice 1, eat_da_runts 1). NO new chunk-level locals (the chunk sits
at Lua's 200-local ceiling) and NO string.find. LF only.
"""
import io, os, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
DESK = "C:/Users/vlady/Desktop"
LIVE = DESK + "/WH3_mod/mod_source/script/battle/mod/zz_test_deadly_onslaught.lua"
ANN = DESK + "/WH3_auto_ability_annotated.lua"

# ----------------------------------------------------------------------------
# 1. the 6 new ABILITIES entries (appended after the last entry, storm_hammer)
# ----------------------------------------------------------------------------
ENTRIES = [
    ("blood_sacrifice", "Blood Sacrifice",
     "wh3_dlc26_lord_abilities_blood_sacrifice", "blood_sacrifice"),
    ("eat_da_runts", "Eat da Runts!",
     "wh3_dlc26_unit_abilities_eat_da_runts", "eat_da_runts"),
    ("locus_of_virulence", "Locus of Virulence",
     "wh3_main_character_abilities_locus_of_virulence", "melee_unwavering"),
    ("the_dance_of_dreaming", "The Dance of Dreaming",
     "wh3_dlc27_lord_abilities_the_dance_of_dreaming", "melee_unwavering"),
    ("the_waltz_of_lethargy", "The Waltz of Lethargy",
     "wh3_dlc27_lord_abilities_the_waltz_of_lethargy", "melee_unwavering"),
    ("ultimate_verdict", "Ultimate Verdict",
     "wh3_cp1_character_abilities_terrifying_presence", "melee_unwavering"),
]


def entries_lua():
    out = ["\n"]
    out.append("\t-- ============================================================================\n")
    out.append("\t-- THE FINAL ROSTER ROUND (this round) - the SIX built individual\n")
    out.append("\t-- abilities from the remaining-abilities triage (WH3_remaining_triage.md\n")
    out.append("\t-- section 3 INDIVIDUAL table). Blood Sacrifice and Eat da Runts! ride\n")
    out.append("\t-- the TWO NEW ally-heal triggers (blood_sacrifice / eat_da_runts, each\n")
    out.append("\t-- its own evaluator, section 7g); the four melee ones ride the EXISTING\n")
    out.append("\t-- shared melee_unwavering evaluator (in-melee self). Base + DLC twins\n")
    out.append("\t-- ride one entry where a name repeats (none here - one key each).\n")
    out.append("\t-- ============================================================================\n")
    for marker, name, key, trig in ENTRIES:
        out.append('\t{ marker = "%s", name = "%s", trigger = "%s",\n' % (marker, name, trig))
        out.append('\t\tbadge = "zz_auto_badge_%s",\n' % marker)
        out.append('\t\tkeys = { "%s" },\n' % key)
        out.append("\t\tox = 0, oy = 0 },\n")
    return "".join(out)


ENTRIES_BLOCK = entries_lua()
assert ENTRIES_BLOCK.count("\t{ marker = ") == 6

TABLE_ANCHOR = (
    '\t{ marker = "storm_hammer", name = "Storm Hammer", trigger = "charge_or_melee",\n'
    '\t\tbadge = "zz_auto_badge_storm_hammer",\n'
    '\t\tkeys = { "wh3_dlc29_spell_bound_storm_hammer" },\n'
    '\t\tox = 0, oy = 0 },\n'
    '}\n'
)
TABLE_REPL = TABLE_ANCHOR[:-2] + ENTRIES_BLOCK + "}\n"

# ----------------------------------------------------------------------------
# 2. the TWO new evaluators + helpers (LIVE shape: reason strings + log lines)
# ----------------------------------------------------------------------------
NEW_EVALUATORS_LIVE = r'''
-- ============================================================================
-- THE FINAL ROSTER ROUND (this round) - TWO new ALLY-HEAL evaluators for the
--   two built individuals that need a new trigger:
--     BLOOD SACRIFICE - cast on the LOWEST-health ally in range at or below 75%;
--     EAT DA RUNTS!   - cast on self at or below 75%, ELSE on the lowest-health
--                       ally in range at or below 75%.
--   Both are ally-targeting HEALS: the cast target is the CHOSEN ALLY (unlike
--   the self-centred auras, whose cast target is always the owner), so the
--   chosen ally rides FOURTH.cast_target AND a per-trigger slot (FOURTH.bs_ally
--   / FOURTH.edr_ally) so the cast can RE-CHECK the gap AND the ally's health
--   immediately before firing and SKIP on drift (the field-proven Glorious
--   Death / Verminking safety pattern). The self arm of Eat da Runts! writes NO
--   cast_target (the default target or unit = the owner), exactly the
--   Verminking convention - so the self-cast writes stay exactly two.
--   THE TRIGGER RANGE is a DELIBERATELY CONSERVATIVE named constant. The game
--   data (unit_spec_abil.tsv) gives these two SINGLE-ally heals NO aura radius
--   (effect_range = 0.0000; num_effected_friendly_units = 1) and a
--   target_intercept_range of 100.0000 m, so - following the file's field-proven
--   conservative pattern (25 m against larger auras) - the trigger radius is a
--   25 m constant. ONE place to tune.
--   THE LOCAL CEILING: every helper / constant / state is a FIELD of the FOURTH
--   bag - NO new chunk-level locals.
-- ============================================================================

-- BLOOD SACRIFICE'S TRIGGER RANGE (this round) - deliberately conservative.
FOURTH.BLOOD_SACRIFICE_RANGE_M = 25
FOURTH.bs_ally = nil
function FOURTH.bs_ally_gap(unit, ally)
	local ok, gap = pcall(function() return ally:unit_distance(unit) end)
	if ok and type(gap) == "number" then return gap end
	return nil
end
function FOURTH.bs_ally_in_range(unit, ally)
	local gap = FOURTH.bs_ally_gap(unit, ally)
	return (gap == nil) or (gap <= FOURTH.BLOOD_SACRIFICE_RANGE_M)
end
-- the chosen ally is STILL a valid heal target: in range AND still at or below
-- 75% health (an unreadable health read is treated as still-valid, fail-open,
-- exactly how the range gate treats an unknown distance).
function FOURTH.bs_ally_valid(unit, ally)
	if ally == nil then return false end
	if not FOURTH.bs_ally_in_range(unit, ally) then return false end
	local hp = FOURTH.context_value(ally, "HealthPercent")
	return (type(hp) ~= "number") or (hp <= 75)
end
-- BLOOD SACRIFICE: fire when a friendly unit other than the caster is at or
-- below 75% health within the conservative trigger range; CAST ON THE
-- LOWEST-HEALTH such ally. Silent when no in-range ally is hurt.
function FOURTH.evaluate_blood_sacrifice(unit, routing)
	local reason = nil
	if not routing then
		local self_id = tostring(unit:unique_ui_id())
		local best_ally = nil
		local best_gap = nil
		local best_hp = nil
		for i = 1, #tracked_units do
			local other = tracked_units[i] and tracked_units[i].unit
			if other ~= nil and other ~= unit and other:number_of_men_alive() > 0 then
				if tostring(other:unique_ui_id()) ~= self_id and not unit_is_routing(other) then
					local hp = FOURTH.context_value(other, "HealthPercent")
					if type(hp) == "number" and hp <= 75 then
						local gap = FOURTH.bs_ally_gap(unit, other)
						if (gap == nil) or (gap <= FOURTH.BLOOD_SACRIFICE_RANGE_M) then
							if best_ally == nil or (type(best_hp) == "number" and hp < best_hp) then
								best_ally, best_gap, best_hp = other, gap, hp
							end
						end
					end
				end
			end
		end
		if best_ally ~= nil then
			if best_gap ~= nil then
				log("  blood_sacrifice ally: ui " .. tostring(best_ally:unique_ui_id())
					.. " at " .. string.format("%.1f", best_gap) .. "m is the LOWEST-health in-range ally"
					.. " within " .. tostring(FOURTH.BLOOD_SACRIFICE_RANGE_M) .. "m")
			end
			FOURTH.cast_target = best_ally
			FOURTH.bs_ally = best_ally
			reason = string.format("blood sacrifice: lowest-health ally %d%% (<= 75%%), cast on ally", math.floor(best_hp))
		end
	end
	return reason
end

-- EAT DA RUNTS!'S TRIGGER RANGE (this round) - deliberately conservative.
FOURTH.EAT_DA_RUNTS_RANGE_M = 25
FOURTH.edr_ally = nil
function FOURTH.edr_ally_gap(unit, ally)
	local ok, gap = pcall(function() return ally:unit_distance(unit) end)
	if ok and type(gap) == "number" then return gap end
	return nil
end
function FOURTH.edr_ally_in_range(unit, ally)
	local gap = FOURTH.edr_ally_gap(unit, ally)
	return (gap == nil) or (gap <= FOURTH.EAT_DA_RUNTS_RANGE_M)
end
-- a nil ally (the SELF arm) is always valid - never gated.
function FOURTH.edr_ally_valid(unit, ally)
	if ally == nil then return true end
	if not FOURTH.edr_ally_in_range(unit, ally) then return false end
	local hp = FOURTH.context_value(ally, "HealthPercent")
	return (type(hp) ~= "number") or (hp <= 75)
end
-- EAT DA RUNTS!: fire when the OWNER itself is at or below 75% health (cast on
-- self), ELSE when a friendly unit other than the caster is at or below 75%
-- within the conservative trigger range (cast on the LOWEST-health such ally).
function FOURTH.evaluate_eat_da_runts(unit, routing)
	local reason = nil
	if not routing then
		local hp = FOURTH.context_value(unit, "HealthPercent")
		if type(hp) == "number" and hp <= 75 then
			reason = string.format("eat da runts: self health %d%% (<= 75%%), cast on self", math.floor(hp))
		else
			local self_id = tostring(unit:unique_ui_id())
			local best_ally = nil
			local best_gap = nil
			local best_hp = nil
			for i = 1, #tracked_units do
				local other = tracked_units[i] and tracked_units[i].unit
				if other ~= nil and other ~= unit and other:number_of_men_alive() > 0 then
					if tostring(other:unique_ui_id()) ~= self_id and not unit_is_routing(other) then
						local ahp = FOURTH.context_value(other, "HealthPercent")
						if type(ahp) == "number" and ahp <= 75 then
							local gap = FOURTH.edr_ally_gap(unit, other)
							if (gap == nil) or (gap <= FOURTH.EAT_DA_RUNTS_RANGE_M) then
								if best_ally == nil or (type(best_hp) == "number" and ahp < best_hp) then
									best_ally, best_gap, best_hp = other, gap, ahp
								end
							end
						end
					end
				end
			end
			if best_ally ~= nil then
				if best_gap ~= nil then
					log("  eat_da_runts ally: ui " .. tostring(best_ally:unique_ui_id())
						.. " at " .. string.format("%.1f", best_gap) .. "m is the LOWEST-health in-range ally"
						.. " within " .. tostring(FOURTH.EAT_DA_RUNTS_RANGE_M) .. "m")
				end
				FOURTH.cast_target = best_ally
				FOURTH.edr_ally = best_ally
				reason = string.format("eat da runts: lowest-health ally %d%% (<= 75%%), cast on ally", math.floor(best_hp))
			end
		end
	end
	return reason
end


'''

# annotated: FIRE / DON'T FIRE, no reason strings, no log lines
NEW_EVALUATORS_ANN = r'''
-- ============================================================================
-- THE FINAL ROSTER ROUND (this round) - TWO new ALLY-HEAL evaluators for the
--   two built individuals that need a new trigger: BLOOD SACRIFICE (cast on
--   the LOWEST-health ally in range at or below 75%) and EAT DA RUNTS! (cast
--   on self at or below 75%, ELSE on the lowest-health ally in range at or
--   below 75%). Each answers FIRE / DON'T FIRE; the LIVE build carries its own
--   distinct reason text (the reading copy keeps no text). The chosen ally
--   rides FOURTH.cast_target + a per-trigger slot so the cast can re-check the
--   gap and the ally's health before firing (the Glorious-Death safety shape).
--   THE TRIGGER RANGE is a DELIBERATELY CONSERVATIVE 25 m named constant (the
--   game data gives these single-ally heals no aura radius, effect_range
--   0.0000, with target_intercept_range 100.0000 m). NO new chunk-level locals.
-- ============================================================================
FOURTH.BLOOD_SACRIFICE_RANGE_M = 25
FOURTH.bs_ally = nil
function FOURTH.bs_ally_gap(unit, ally)
	local ok, gap = pcall(function() return ally:unit_distance(unit) end)
	if ok and type(gap) == "number" then return gap end
	return nil
end
function FOURTH.bs_ally_in_range(unit, ally)
	local gap = FOURTH.bs_ally_gap(unit, ally)
	return (gap == nil) or (gap <= FOURTH.BLOOD_SACRIFICE_RANGE_M)
end
function FOURTH.bs_ally_valid(unit, ally)
	if ally == nil then return false end
	if not FOURTH.bs_ally_in_range(unit, ally) then return false end
	local hp = FOURTH.context_value(ally, "HealthPercent")
	return (type(hp) ~= "number") or (hp <= 75)
end
function FOURTH.evaluate_blood_sacrifice(unit, routing)
	if not routing then
		local self_id = tostring(unit:unique_ui_id())
		local best_ally = nil
		local best_gap = nil
		local best_hp = nil
		for i = 1, #tracked_units do
			local other = tracked_units[i] and tracked_units[i].unit
			if other ~= nil and other ~= unit and other:number_of_men_alive() > 0 then
				if tostring(other:unique_ui_id()) ~= self_id and not unit_is_routing(other) then
					local hp = FOURTH.context_value(other, "HealthPercent")
					if type(hp) == "number" and hp <= 75 then
						local gap = FOURTH.bs_ally_gap(unit, other)
						if (gap == nil) or (gap <= FOURTH.BLOOD_SACRIFICE_RANGE_M) then
							if best_ally == nil or (type(best_hp) == "number" and hp < best_hp) then
								best_ally, best_gap, best_hp = other, gap, hp
							end
						end
					end
				end
			end
		end
		if best_ally ~= nil then
			FOURTH.cast_target = best_ally
			FOURTH.bs_ally = best_ally
			return true
		end
	end
	return false
end
FOURTH.EAT_DA_RUNTS_RANGE_M = 25
FOURTH.edr_ally = nil
function FOURTH.edr_ally_gap(unit, ally)
	local ok, gap = pcall(function() return ally:unit_distance(unit) end)
	if ok and type(gap) == "number" then return gap end
	return nil
end
function FOURTH.edr_ally_in_range(unit, ally)
	local gap = FOURTH.edr_ally_gap(unit, ally)
	return (gap == nil) or (gap <= FOURTH.EAT_DA_RUNTS_RANGE_M)
end
function FOURTH.edr_ally_valid(unit, ally)
	if ally == nil then return true end
	if not FOURTH.edr_ally_in_range(unit, ally) then return false end
	local hp = FOURTH.context_value(ally, "HealthPercent")
	return (type(hp) ~= "number") or (hp <= 75)
end
function FOURTH.evaluate_eat_da_runts(unit, routing)
	if not routing then
		local hp = FOURTH.context_value(unit, "HealthPercent")
		if type(hp) == "number" and hp <= 75 then
			return true
		end
		local self_id = tostring(unit:unique_ui_id())
		local best_ally = nil
		local best_gap = nil
		local best_hp = nil
		for i = 1, #tracked_units do
			local other = tracked_units[i] and tracked_units[i].unit
			if other ~= nil and other ~= unit and other:number_of_men_alive() > 0 then
				if tostring(other:unique_ui_id()) ~= self_id and not unit_is_routing(other) then
					local ahp = FOURTH.context_value(other, "HealthPercent")
					if type(ahp) == "number" and ahp <= 75 then
						local gap = FOURTH.edr_ally_gap(unit, other)
						if (gap == nil) or (gap <= FOURTH.EAT_DA_RUNTS_RANGE_M) then
							if best_ally == nil or (type(best_hp) == "number" and ahp < best_hp) then
								best_ally, best_gap, best_hp = other, gap, ahp
							end
						end
					end
				end
			end
		end
		if best_ally ~= nil then
			FOURTH.cast_target = best_ally
			FOURTH.edr_ally = best_ally
			return true
		end
	end
	return false
end


'''

# ----------------------------------------------------------------------------
# 3. the two pre-cast re-check blocks (LIVE: log + release; ANN: bare skip)
# ----------------------------------------------------------------------------
RECHECK_ANCHOR = "\t-- THE CALL. Ordinary keys (self- or unit-targeted) use the proven\n"
assert True

RECHECK_LIVE = '''	-- BLOOD SACRIFICE / EAT DA RUNTS ALLY RE-CHECK (this round): the same
	-- safety pattern as Glorious Death / Verminking / Metallurgy. The ally arm
	-- chose a LOW-HEALTH ally and left it in FOURTH.bs_ally / FOURTH.edr_ally;
	-- RE-READ the gap AND the ally's health NOW, immediately before the cast.
	-- If the ally has drifted out of range or healed above the 75% line the cast
	-- is wasted, so SKIP it rather than spend it. The Eat-da-Runts self arm
	-- leaves FOURTH.edr_ally nil - never gated (casting on self is always in
	-- range).
	if FOURTH.bs_ally ~= nil and not FOURTH.bs_ally_valid(unit, FOURTH.bs_ally) then
		log("  blood_sacrifice SKIPPED: the chosen ally drifted out of range or healed above 75%"
			.. " before the cast - cast not spent")
		FOURTH.bs_ally = nil
		if RELEASE_CONTROL_AFTER and took_control then
			local ok_release, err_release = pcall(function() uc:release_control() end)
			log("  release_control         : ok=" .. tostring(ok_release)
				.. (ok_release and "" or ("  ERROR: " .. tostring(err_release))))
		end
		return "held"
	end
	if FOURTH.edr_ally ~= nil and not FOURTH.edr_ally_valid(unit, FOURTH.edr_ally) then
		log("  eat_da_runts SKIPPED: the chosen ally drifted out of range or healed above 75%"
			.. " before the cast - cast not spent")
		FOURTH.edr_ally = nil
		if RELEASE_CONTROL_AFTER and took_control then
			local ok_release, err_release = pcall(function() uc:release_control() end)
			log("  release_control         : ok=" .. tostring(ok_release)
				.. (ok_release and "" or ("  ERROR: " .. tostring(err_release))))
		end
		return "held"
	end

'''

RECHECK_ANN = '''	-- BLOOD SACRIFICE / EAT DA RUNTS ALLY RE-CHECK (this round): re-read the
	-- chosen ally's gap AND health immediately before the cast; skip when it has
	-- drifted out of range or healed above the 75% line. The Eat-da-Runts self
	-- arm leaves FOURTH.edr_ally nil - never gated.
	if FOURTH.bs_ally ~= nil and not FOURTH.bs_ally_valid(unit, FOURTH.bs_ally) then
		FOURTH.bs_ally = nil
		return "held"
	end
	if FOURTH.edr_ally ~= nil and not FOURTH.edr_ally_valid(unit, FOURTH.edr_ally) then
		FOURTH.edr_ally = nil
		return "held"
	end

'''

# ----------------------------------------------------------------------------
# 4. poll clearing block additions
# ----------------------------------------------------------------------------
POLL_ANCHOR = ("\t\t\t\t\tFOURTH.cast_target = nil\n"
               "\t\t\t\t\tFOURTH.gd_ally = nil\n"
               "\t\t\t\t\tFOURTH.vm_ally = nil\n"
               "\t\t\t\t\tFOURTH.mtl_ally = nil\n"
               "\t\t\t\t\tFOURTH.ws_ally = nil\n"
               "\t\t\t\t\tFOURTH.wa_ally = nil\n")
POLL_REPL = (POLL_ANCHOR
             + "\t\t\t\t\tFOURTH.bs_ally = nil\n"
             + "\t\t\t\t\tFOURTH.edr_ally = nil\n")

# ----------------------------------------------------------------------------
# 5. evaluator-map additions
# ----------------------------------------------------------------------------
MAP_ANCHOR = "\twavering_ally_range = FOURTH.evaluate_wavering_ally_range,\n}"
MAP_REPL = ("\twavering_ally_range = FOURTH.evaluate_wavering_ally_range,\n"
            "\t-- THE FINAL ROSTER ROUND (this round): the two ally-heal triggers.\n"
            "\tblood_sacrifice = FOURTH.evaluate_blood_sacrifice,\n"
            "\teat_da_runts = FOURTH.evaluate_eat_da_runts,\n"
            "}")


def rd(p):
    with io.open(p, encoding="utf-8") as f:
        s = f.read()
    assert "\r" not in s, ("CRLF in " + p)
    return s


def count(s, tok):
    n, at = 0, 1
    while True:
        i = s.find(tok, at)
        if i < 0:
            return n
        n += 1
        at = i + 1


def sub_once(s, old, new, label):
    n = s.count(old)
    assert n == 1, "%s: %d matches (want 1)" % (label, n)
    return s.replace(old, new, 1)


def apply(path, is_live):
    s = rd(path)
    s = sub_once(s, TABLE_ANCHOR, TABLE_REPL, "table " + path)
    ev = NEW_EVALUATORS_LIVE if is_live else NEW_EVALUATORS_ANN
    s = sub_once(s, "FOURTH.evaluators = {", ev + "FOURTH.evaluators = {", "eval " + path)
    s = sub_once(s, RECHECK_ANCHOR, (RECHECK_LIVE if is_live else RECHECK_ANN) + RECHECK_ANCHOR,
                 "recheck " + path)
    s = sub_once(s, POLL_ANCHOR, POLL_REPL, "poll " + path)
    s = sub_once(s, MAP_ANCHOR, MAP_REPL, "map " + path)
    return s


def post(name, s, is_live):
    assert count(s, "\t{ marker = ") == 579, (name, "entries", count(s, "\t{ marker = "))
    assert count(s, 'trigger = "melee_unwavering"') == 481, name
    assert count(s, 'trigger = "blood_sacrifice"') == 1, name
    assert count(s, 'trigger = "eat_da_runts"') == 1, name
    assert count(s, "FOURTH.cast_target = unit") == 2, (name, "cast_target=unit")
    assert count(s, "FOURTH.bs_ally = nil") == 3, name
    assert count(s, "FOURTH.edr_ally = nil") == 3, name
    for marker, nm, key, trig in ENTRIES:
        assert 'marker = "%s"' % marker in s, name + " missing marker " + marker
        assert 'badge = "zz_auto_badge_%s"' % marker in s, name + " missing badge " + marker
        assert '"%s"' % key in s, name + " missing key " + key
    assert "function FOURTH.evaluate_blood_sacrifice(unit, routing)" in s, name
    assert "function FOURTH.evaluate_eat_da_runts(unit, routing)" in s, name
    assert "function FOURTH.bs_ally_valid(unit, ally)" in s, name
    assert "function FOURTH.edr_ally_valid(unit, ally)" in s, name
    assert "blood_sacrifice = FOURTH.evaluate_blood_sacrifice," in s, name
    assert "eat_da_runts = FOURTH.evaluate_eat_da_runts," in s, name
    assert count(s, "string.find(") == 0, name
    if is_live:
        assert "blood_sacrifice SKIPPED:" in s, name
        assert "eat_da_runts SKIPPED:" in s, name
        assert "blood_sacrifice ally: ui" in s, name
        assert "eat_da_runts ally: ui" in s, name
        assert 'string.format("blood sacrifice: lowest-health ally %d%% (<= 75%%), cast on ally"' in s, name
        assert 'string.format("eat da runts: self health %d%% (<= 75%%), cast on self"' in s, name
    else:
        assert count(s, "log(") == 0, (name, "annotated has log()")


live0 = rd(LIVE)
ann0 = rd(ANN)
# the pre-edit snapshots for the red control (the CURRENT shipped harness-91 build)
io.open(os.path.join(HERE, "pre92_live.lua"), "w", encoding="utf-8", newline="\n").write(live0)
io.open(os.path.join(HERE, "pre92_ann.lua"), "w", encoding="utf-8", newline="\n").write(ann0)
print("pre92 snapshots:", len(live0), len(ann0), "bytes")

live = apply(LIVE, True)
post("LIVE", live, True)
ann = apply(ANN, False)
post("ANN", ann, False)

with io.open(LIVE, "w", encoding="utf-8", newline="\n") as f:
    f.write(live)
with io.open(ANN, "w", encoding="utf-8", newline="\n") as f:
    f.write(ann)
assert "\r" not in open(LIVE, "rb").read().decode("utf-8"), "CRLF written LIVE"
assert "\r" not in open(ANN, "rb").read().decode("utf-8"), "CRLF written ANN"

print("LIVE %d -> %d bytes" % (len(live0), len(live)))
print("ANN  %d -> %d bytes" % (len(ann0), len(ann)))
print("sha256 LIVE", hashlib.sha256(live.encode("utf-8")).hexdigest())
print("sha256 ANN ", hashlib.sha256(ann.encode("utf-8")).hexdigest())
print("ALL EDIT POSTCONDITIONS OK")
