#!/usr/bin/env python3
"""Round 131 (harness 130): the shooting buffs leave the melee trigger, Potion of Farsight's
out-of-range trigger, the firing aura counts the caster, and the nine stances leave the mod.

User rulings 2026-11-01:
  * shooting trigger for Deranged Munitions (both keys), Enchanted Ballistics, Funnel of Flame,
    Hail of Fire, The Guiding Eye, Morgrim's Eye, Locus of Change; Entrenchment "shooting, and
    also when in melee because of the physical resistance";
  * the auras: "Fires when at least 1 ally (caster counts) inside the aura's 70% bound is
    shooting. Actually, the previous trigger where the trigger was required 2 allies should be
    redone." (Ballistics Calibration 2 -> 1, the caster counts);
  * Deranged Munitions (base) and Entrenchment (one target): "Self, else a shooting ally";
  * Potion of Farsight: no enemy inside the unit's missile range AND at least one inside
    range x 1.21 (the 70% rule on the +30% bonus);
  * "For now, all stances should not have any automation" -> remove all 9 now.
No string.find. Every helper is a FOURTH field (the 200-local ceiling).
"""
import re

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"

STANCES = ["master_predator", "immovable_bulwark", "unstoppable_choppas", "the_shadows_coil", "woven_mist",
           "chanson_of_caging", "the_dance_of_dreaming", "the_praise_of_slaanesh", "the_waltz_of_lethargy"]
WINDUP_GONE = ["wh2_dlc17_lord_abilities_master_predator", "wh3_dlc26_unit_abilities_immovable_bulwark",
               "wh3_dlc26_unit_abilities_unstoppable_choppas", "wh_dlc05_unit_abilities_the_shadows_coil",
               "wh_dlc05_unit_abilities_woven_mist"]
# marker -> (new trigger, extra field line or None); effect_range / target_intercept_range from unit_spec_abil.tsv
RETRIGGER = {
    "deranged_munitions": ("self_or_ally_shooting", "ally_range_real = 100"),
    "deranged_munitions_upgraded": ("allies_firing_aura", "aura_real = 35"),
    "ballistic_enchantment": ("allies_firing_aura", "aura_real = 55"),
    "funnel_of_flame": ("allies_firing_aura", "aura_real = 55"),
    "hail_of_fire": ("allies_firing_aura", "aura_real = 55"),
    "the_guiding_eye": ("allies_firing_aura", "aura_real = 55"),
    "morgrims_eye": ("allies_firing_aura", "aura_real = 35"),
    "locus_of_change": ("allies_firing_aura", "aura_real = 55"),
    "potion_of_farsight": ("no_enemy_in_range_within_boost", None),
    "entrenchment": ("melee_or_self_or_ally_shooting", "ally_range_real = 150"),
}


def entry_span(s, marker):
    a = s.index('\t{ marker = "%s",' % marker)
    assert s.count('\t{ marker = "%s",' % marker) == 1, marker
    b = s.index("ox = 0, oy = 0 },\n", a) + len("ox = 0, oy = 0 },\n")
    block = s[a:b]
    assert block.count("\n") <= 5 and 'trigger = "melee_unwavering",' in block, (marker, block)
    return a, b, block


def apply_roster(s):
    for m in STANCES:
        a, b, block = entry_span(s, m)
        s = s[:a] + s[b:]
    for k in WINDUP_GONE:
        line = '\t\t["%s"] = 1,\n' % k
        assert s.count(line) == 1, k
        s = s.replace(line, "")
    for m, (trig, extra) in RETRIGGER.items():
        a, b, block = entry_span(s, m)
        nb = block.replace('trigger = "melee_unwavering",', 'trigger = "%s",' % trig)
        if extra:
            nb = nb.replace("\t\tox = 0, oy = 0 },\n", "\t\t%s,\n\t\tox = 0, oy = 0 },\n" % extra)
        s = s[:a] + nb + s[b:]
    return s


# ------------------------------------------------------------------ the aura now counts the caster
CONST_OLD = "FOURTH.BALLISTICS_MIN_FIRING = 2    -- allies shooting inside the aura bound (user, 2026-11-01: option A)\n"
CONST_NEW = ("FOURTH.FIRING_AURA_MIN = 1          -- units shooting inside the aura bound, the caster counting (user, round 131;\n"
             "                                    -- round 130 asked for 2 allies)\n")
HDR_OLD = ("--   ballistics_calibration: at least BALLISTICS_MIN_FIRING allies within the\n"
           "--     aura bound (38 m = 70% of 55 m) are shooting and past their cast point;\n"
           "--     cast on the ground at the caster's own feet (no move order).\n")
HDR_NEW = ("--   allies_firing_aura: at least FIRING_AURA_MIN units (ROUND 131: 1, the caster\n"
           "--     counting) within the aura bound (70% of the effect_range) are shooting and\n"
           "--     past their cast point. Ballistics Calibration is cast on the ground at the\n"
           "--     caster's own feet; the self-centred auras (round 131) on the caster.\n")
AURA_LIVE_OLD = """	local n, bound = FOURTH.count_allies_firing_near(unit)
	if n < FOURTH.BALLISTICS_MIN_FIRING then return nil end
	return string.format("%s: %d allies within %sm are shooting past their cast point (need %d), cast on the ground at the caster's own position",
		tostring(FOURTH.ab_marker or "aura"), n, tostring(bound), FOURTH.BALLISTICS_MIN_FIRING)
"""
AURA_LIVE_NEW = """	local n, bound = FOURTH.count_allies_firing_near(unit)
	-- ROUND 131: the caster counts too (user: "at least 1 ... caster counts")
	local own = FOURTH.shooting_past_cast_point(unit) and 1 or 0
	if n + own < FOURTH.FIRING_AURA_MIN then return nil end
	return string.format("%s: %d unit(s) within %sm are shooting past their cast point (%d allies + the caster %s; need %d), cast centred on the caster",
		tostring(FOURTH.ab_marker or "aura"), n + own, tostring(bound), n,
		(own == 1) and "shooting" or "not shooting", FOURTH.FIRING_AURA_MIN)
"""
AURA_ANN_OLD = """	local n = FOURTH.count_allies_firing_near(unit)
	return n >= FOURTH.BALLISTICS_MIN_FIRING
"""
AURA_ANN_NEW = """	local n = FOURTH.count_allies_firing_near(unit)
	-- ROUND 131: the caster counts too
	local own = FOURTH.shooting_past_cast_point(unit) and 1 or 0
	return n + own >= FOURTH.FIRING_AURA_MIN
"""
AURA_CMT_OLD = ("-- allies_firing_aura (Ballistics Calibration): enough shooting allies around the\n"
                "-- caster; the cast is the ground form at the caster's own position (ground_keys).\n")
AURA_CMT_NEW = ("-- allies_firing_aura (Ballistics Calibration and, from round 131, the self-centred\n"
                "-- shooting auras): enough units shooting around the caster, the caster counting;\n"
                "-- Ballistics Calibration is a ground key (cast at the caster's own position), the\n"
                "-- others are cast on the caster.\n")

# ------------------------------------------------------------------ the ally picker learns "shooting"
ELIG_OLD = ('\t\t\t\t\telseif family == "ammo" then\n'
            '\t\t\t\t\t\t-- ROUND 130: Restock! - shooting now, at or below the line\n')
ELIG_NEW = ('\t\t\t\t\telseif family == "shooting" then\n'
            '\t\t\t\t\t\t-- ROUND 131: Deranged Munitions / Entrenchment - an ally shooting\n'
            '\t\t\t\t\t\t-- past its cast point (the closest wins, the default rule below)\n'
            '\t\t\t\t\t\teligible = FOURTH.shooting_past_cast_point(other)\n') + ELIG_OLD
RET_LIVE_OLD = '\telseif family == "ammo" then\n\t\tpcall(function() FOURTH.ammo_claim_id = tostring(best_ally:unique_ui_id()) end)\n'
RET_LIVE_NEW = ('\telseif family == "shooting" then\n'
                '\t\treturn tostring(FOURTH.ab_marker or "ally") .. ": the caster is not shooting; the closest ally shooting past its cast point, cast on ally"\n') + RET_LIVE_OLD
RECHECK_OLD = ('\t\tif FOURTH.ab_family == "ammo" then\n'
               '\t\t\tlocal fr = FOURTH.ammo_fraction_if_firing(ally)\n'
               '\t\t\thp_ok_now = (fr ~= nil) and (fr <= FOURTH.RESTOCK_AT_FRACTION)\n'
               '\t\tend\n')
RECHECK_NEW = RECHECK_OLD + ('\t\t-- ROUND 131: the shooting family - the ally must still be shooting\n'
                             '\t\tif FOURTH.ab_family == "shooting" then\n'
                             '\t\t\thp_ok_now = FOURTH.shooting_past_cast_point(ally)\n'
                             '\t\tend\n')
VALID_OLD = ('\tif FOURTH.ab_family == "ammo" then\n'
             '\t\tlocal fr = FOURTH.ammo_fraction_if_firing(ally)\n'
             '\t\treturn (fr ~= nil) and (fr <= FOURTH.RESTOCK_AT_FRACTION)\n\tend\n')
VALID_NEW = VALID_OLD + ('\tif FOURTH.ab_family == "shooting" then\n'
                         '\t\treturn FOURTH.shooting_past_cast_point(ally)\n\tend\n')

# ------------------------------------------------------------------ the new evaluators
BLOCK_COMMON = """-- ============================================================================
-- ROUND 131 - THE SHOOTING BUFFS LEAVE THE MELEE TRIGGER (user rulings 2026-11-01).
--   self_or_ally_shooting (Deranged Munitions): the caster shooting past its cast
--     point -> cast on self; otherwise the closest ally within the 70% bound that
--     is shooting past its cast point -> cast on that ally ("Self, else a
--     shooting ally").
--   melee_or_self_or_ally_shooting (Entrenchment): in melee (as melee_unwavering:
--     the +20 physical resistance) -> self; otherwise as self_or_ally_shooting.
--     The target cannot move for 44 s (the user accepted rooting an ally).
--   no_enemy_in_range_within_boost (Potion of Farsight, 1 use): NO enemy inside
--     the unit's own live missile_range() AND at least one enemy inside
--     missile_range x FARSIGHT_BAND - the range the potion would give, with the
--     standing 70% rule applied to the +30% bonus (1 + 0.30 x 0.70 = 1.21). Not
--     in melee, ammunition left, every read fail-closed. unit_distance is edge to
--     edge, the same measure the firing flag's in-range read uses.
-- ============================================================================
FOURTH.FARSIGHT_BONUS = 0.30   -- Potion of Farsight: "Range: +30%" (the game's own phase stat)
FOURTH.FARSIGHT_BAND = 1 + FOURTH.FARSIGHT_BONUS * FOURTH.RANGE_FRACTION   -- 1.21

-- the nearest LIVE enemy's edge-to-edge gap from `unit`, and whether ANY live
-- enemy is within `inner` metres; nil when the enemy list cannot be read.
function FOURTH.nearest_enemy_gap(unit, inner)
	local ok_coll, coll = pcall(function()
		return bm:get_scriptunits_for_main_enemy_army_to_local_player()
	end)
	if not ok_coll or coll == nil then return nil, nil end
	local ok_n, n = pcall(function() return coll:count() end)
	if not ok_n or type(n) ~= "number" then return nil, nil end
	local best, any_inner = nil, false
	for i = 1, n do
		local ok_su, su = pcall(function() return coll:item(i) end)
		local enemy = nil
		if ok_su and su ~= nil then pcall(function() enemy = su.unit end) end
		if enemy ~= nil then
			local ok_a, alive = pcall(function() return enemy:number_of_men_alive() end)
			local ok_g, gap = pcall(function() return unit:unit_distance(enemy) end)
			if ok_a and type(alive) == "number" and alive > 0 and ok_g and type(gap) == "number" and gap >= 0 then
				if best == nil or gap < best then best = gap end
				if gap <= inner then any_inner = true end
			end
		end
	end
	return best, any_inner
end

"""
EVALS_LIVE = """function FOURTH.evaluate_self_or_ally_shooting(unit, routing)
	if routing then return nil end
	if FOURTH.shooting_past_cast_point(unit) then
		return "the caster is shooting past its cast point, cast on self"
	end
	return FOURTH.ab_pick_ally(unit, routing, "shooting")
end

function FOURTH.evaluate_melee_or_self_or_ally_shooting(unit, routing)
	local r = FOURTH.evaluate_in_melee_self(unit, routing)
	if r ~= nil then return r end
	return FOURTH.evaluate_self_or_ally_shooting(unit, routing)
end

function FOURTH.evaluate_no_enemy_in_range_within_boost(unit, routing)
	if routing then return nil end
	local ok_mel, mel = pcall(function() return unit:is_in_melee() end)
	if not ok_mel or mel ~= false then return nil end
	local ok_am, am = pcall(function() return unit:ammo_left() end)
	if not ok_am or type(am) ~= "number" or am <= 0 then return nil end
	local ok_r, r = pcall(function() return unit:missile_range() end)
	if not ok_r or type(r) ~= "number" or r <= 0 then return nil end
	local nearest, any_in_range = FOURTH.nearest_enemy_gap(unit, r)
	if nearest == nil or any_in_range then return nil end
	local outer = r * FOURTH.FARSIGHT_BAND
	if nearest > outer then return nil end
	return string.format("no enemy inside the missile range %.1fm; the nearest enemy is at %.1fm, inside range x %.2f = %.1fm, cast on self",
		r, nearest, FOURTH.FARSIGHT_BAND, outer)
end

"""
EVALS_ANN = """function FOURTH.evaluate_self_or_ally_shooting(unit, routing)
	if routing then return false end
	if FOURTH.shooting_past_cast_point(unit) then return true end
	return FOURTH.ab_pick_ally(unit, routing, "shooting")
end

function FOURTH.evaluate_melee_or_self_or_ally_shooting(unit, routing)
	if FOURTH.evaluate_in_melee_self(unit, routing) then return true end
	return FOURTH.evaluate_self_or_ally_shooting(unit, routing)
end

function FOURTH.evaluate_no_enemy_in_range_within_boost(unit, routing)
	if routing then return false end
	local ok_mel, mel = pcall(function() return unit:is_in_melee() end)
	if not ok_mel or mel ~= false then return false end
	local ok_am, am = pcall(function() return unit:ammo_left() end)
	if not ok_am or type(am) ~= "number" or am <= 0 then return false end
	local ok_r, r = pcall(function() return unit:missile_range() end)
	if not ok_r or type(r) ~= "number" or r <= 0 then return false end
	local nearest, any_in_range = FOURTH.nearest_enemy_gap(unit, r)
	if nearest == nil or any_in_range then return false end
	return nearest <= r * FOURTH.FARSIGHT_BAND
end

"""
EVALS_ANCHOR = "FOURTH.evaluators = {\n"
MAP_OLD = "\tmelee_or_shooting_into_melee = FOURTH.evaluate_melee_or_shooting_into_melee,\n"
MAP_NEW = MAP_OLD + ("\t-- ROUND 131\n"
                     "\tself_or_ally_shooting = FOURTH.evaluate_self_or_ally_shooting,\n"
                     "\tmelee_or_self_or_ally_shooting = FOURTH.evaluate_melee_or_self_or_ally_shooting,\n"
                     "\tno_enemy_in_range_within_boost = FOURTH.evaluate_no_enemy_in_range_within_boost,\n")
TIP_OLD = ('\tallies_firing_aura = "When armed, fires when at least 2 friendly units near this unit are shooting, '
           'placed on the ground at its feet",\n')
TIP_NEW = ('\tallies_firing_aura = "When armed, fires when this unit or a friendly unit near it is shooting",\n'
           '\tself_or_ally_shooting = "When armed, fires on this unit when it is shooting, otherwise on the closest friendly unit in range that is shooting",\n'
           '\tmelee_or_self_or_ally_shooting = "When armed, fires on this unit in melee or when it is shooting, otherwise on the closest friendly unit in range that is shooting",\n'
           '\tno_enemy_in_range_within_boost = "When armed, fires when no enemy is in this unit\'s missile range but one is just beyond it",\n')

COMMON = [(CONST_OLD, CONST_NEW), (HDR_OLD, HDR_NEW), (AURA_CMT_OLD, AURA_CMT_NEW), (ELIG_OLD, ELIG_NEW),
          (RECHECK_OLD, RECHECK_NEW), (VALID_OLD, VALID_NEW), (MAP_OLD, MAP_NEW), (TIP_OLD, TIP_NEW)]
PLAN = {
    SRC: COMMON + [(AURA_LIVE_OLD, AURA_LIVE_NEW), (RET_LIVE_OLD, RET_LIVE_NEW),
                   (EVALS_ANCHOR, BLOCK_COMMON + EVALS_LIVE + EVALS_ANCHOR)],
    ANN: COMMON + [(AURA_ANN_OLD, AURA_ANN_NEW), (EVALS_ANCHOR, BLOCK_COMMON + EVALS_ANN + EVALS_ANCHOR)],
}

if __name__ == "__main__":
    import sys
    dry = "--dry" in sys.argv
    for path, edits in PLAN.items():
        s = open(path, encoding="utf-8", newline="").read()
        assert "\r\n" not in s and "FARSIGHT_BAND" not in s, path
        s = apply_roster(s)
        for i, (a, b) in enumerate(edits, 1):
            n = s.count(a)
            assert n == 1, (path.split("\\")[-1], "edit", i, a[:60], "anchor count", n)
            s = s.replace(a, b, 1)
        added = "".join(b for _, b in edits)
        assert "\u2014" not in added and "string.find" not in added and "and not routing" not in added
        assert "BALLISTICS_MIN_FIRING" not in s, path
        if path == ANN:
            assert "log(" not in EVALS_ANN + BLOCK_COMMON
        if not dry:
            open(path, "w", encoding="utf-8", newline="").write(s)
        print(("checked" if dry else "applied") + " %d edits + roster:" % len(edits), path.split("\\")[-1])
