#!/usr/bin/env python3
"""Round 180: the score-3 review, rows 87-114 and 128 (user, 2026-11-18: "Row 128 set A / Rows 57-86 do not touch /
Rows 87-90 implement without melee / Row 91-96 implement as in the doc / Row 98 improve / Rows 99-114 implement /
107 Mantra of Invigoration I like the option"), built from the CURRENT text of each row on disk.

  87-90  the ground roots: the existing enemy_fast_near_ally (no melee arm); their range_real was their AREA (15 / 35 m),
         now the game's target_intercept_range (100 m -> 70 m bound).
  92     Heaven's Gate CLOSED.  91, 93, 95, 96: the 80% simulated reach (tools/gen_ww_tables.py Q80).  94: kept (the data
         says the fanatics hit our units).
  98     Land Mine: NEW melee_clear_block (melee_clear + at least half a packed block of enemy soldiers in the blast).
  99     Shield of Thorns: melee_self_or_ally (200 m -> 140 m).
  100-101 Snowflake Pendant, Stave of Avelorn CLOSED.   102-103, 109, 113: kept.
  104, 105, 107 Blood Chalice of Bathori, Breath of Darkness x2, Mantra of Invigoration: NEW health_aura_ally_rule (the
         lowest unit the game's target rule allows, the caster included, at or below 75%, cast on it; the rule codes
         C / U and the NEW T (tiger set) through FOURTH.ab_atarget_ok).
  106    Bugman's XXXXXX: NEW self_heal_clear (75% and no visible enemy within 38 m = 70% of its 55 m).
  108, 110 Potion of Charoi, Skar's Kraken-Killer: NEW self_hurt_attacked (75% and in melee or under missile fire).
  111    Foe-Seeker: NEW charge_or_tired.
  112    Rock Bottom: self_out_of_ammo AND above 50% health.
  114    Eat da Runts!: the caster at or below 75%, cast on the cheapest ally above 75% (expendable first, then the
         lowest value per soldier); no self arm.
  128    Cold-Blooded: the NEW Z code (lizard set, 'set A') honoured by wavering_ally_range.
"""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"
import os  # noqa: E402
import sys  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_rule_sets as GS  # noqa: E402

# marker, name, old family, new family, extra lines, start_armed (the old family started armed, the new one does not)
MOVES = [
    ("entangle", "Entangle", "enemy_ground_area", "enemy_fast_near_ally", "", False),
    ("get_em", "Get 'Em!", "enemy_ground_area", "enemy_fast_near_ally", "", False),
    ("hunters_snare", "Hunter's Snare", "enemy_ground_area", "enemy_fast_near_ally", "", False),
    ("hunters_trap", "Hunter's Trap", "enemy_ground_area", "enemy_fast_near_ally", "", False),
    ("land_mine", "Land Mine", "melee_clear", "melee_clear_block", "", False),
    ("shield_of_thorns", "Shield of Thorns", "charge_or_melee", "melee_self_or_ally", "\t\tally_range_real = 200,\n", True),
    ("blood_chalice_of_bathori", "Blood Chalice of Bathori", "ushoran_health", "health_aura_ally_rule", "\t\tally_range_real = 60,\n", True),
    ("undeath_morkharn_breath_of_darkness", "Breath of Darkness", "ushoran_health", "health_aura_ally_rule", "\t\tally_range_real = 200,\n", True),
    ("undeath_morkharn_breath_of_darkness_upgraded", "Breath of Darkness Upgraded", "ushoran_health", "health_aura_ally_rule", "\t\tally_range_real = 200,\n", True),
    ("protection_prayer", "Mantra of Invigoration", "ushoran_health", "health_aura_ally_rule", "\t\tally_range_real = 100,\n", True),
    ("bugmans_xxxxxx", "Bugman's XXXXXX", "ushoran_health", "self_heal_clear", "", True),
    ("potion_of_charoi", "Potion of Charoi", "ushoran_health", "self_hurt_attacked", "", True),
    ("skars_kraken_killer", "Skar's Kraken-Killer", "ushoran_health", "self_hurt_attacked", "", True),
    ("foe_seeker", "Foe-Seeker", "tired", "charge_or_tired", "", True),
]
RANGE_FIX = {"entangle": ("\t\trange_real = 15,\n", "\t\trange_real = 100,\n"),
             "get_em": ("\t\trange_real = 35,\n", "\t\trange_real = 100,\n"),
             "hunters_snare": ("\t\trange_real = 35,\n", "\t\trange_real = 100,\n"),
             "hunters_trap": ("\t\trange_real = 35,\n", "\t\trange_real = 100,\n")}
CUT = [
    '\t{ marker = "heavens_gate", name = "Heaven\'s Gate", trigger = "enemy_wander",\n',
    '\t{ marker = "snowflake_pendant", name = "Snowflake Pendant", trigger = "when_ready",\n',
    '\t{ marker = "stave_of_avelorn", name = "Stave of Avelorn", trigger = "when_ready",\n',
]
CUT_LINES = ['\t\t["wh3_cp1_item_abilities_heavens_gate"] = 2,\n']


def move_entry(s, marker, name, old, new, extra, armed):
    head = '\t{ marker = "%s", name = "%s", trigger = "%s",' % (marker, name, old)
    assert s.count(head) == 1, (marker, s.count(head))
    i = s.index(head)
    j = s.index("\n\t\tox = ", i) + 1
    block = s[i:j]
    assert "start_armed" not in block, marker
    nb = ('\t-- ROUND 180 (score-3 review): %s\n' % new) + block.replace(head, '\t{ marker = "%s", name = "%s", trigger = "%s",' % (marker, name, new), 1)
    if marker in RANGE_FIX:
        a, b = RANGE_FIX[marker]
        assert nb.count(a) == 1, marker
        nb = nb.replace(a, b)
    nb += extra + ("\t\tstart_armed = true,\n" if armed else "")
    return s[:i] + nb + s[j:]


def cut_entry(s, head):
    assert s.count(head) == 1, head
    i = s.index(head)
    j = s.index("\t\tox = 0, oy = 0 },\n", i) + len("\t\tox = 0, oy = 0 },\n")
    return s[:i] + s[j:]


def cut_function(s, name):
    a = "function FOURTH.%s(unit, routing)\n" % name
    assert s.count(a) == 1, name
    i = s.index(a)
    j = s.index("\nend\n", i) + len("\nend\n")
    return s[:i] + "@@%s@@\n" % name + s[j:]


LIVE_FN = {
    "evaluate_eat_da_runts": '''-- ROUND 180 (user, 2026-11-18: "A: cheapest ally"): the ally TAKES the damage and the caster heals, so the caster
-- must be hurt (at or below 75%) and the target is the CHEAPEST healthy ally in range: an expendable unit first, then
-- the lowest live value per soldier; never an ally at or below 75%. No self arm (the heal comes from the ally).
function FOURTH.evaluate_eat_da_runts(unit, routing)
	if routing then return nil end
	local hp = FOURTH.health_pct(unit)
	if type(hp) ~= "number" or hp > 75 then return nil end
	local self_id = tostring(unit:unique_ui_id())
	local best, best_exp, best_vps, best_gap = nil, nil, nil, nil
	for i = 1, #tracked_units do
		local other = tracked_units[i] and tracked_units[i].unit
		if other ~= nil and other ~= unit and other:number_of_men_alive() > 0
			and tostring(other:unique_ui_id()) ~= self_id and not unit_is_routing(other) then
			local ahp = FOURTH.health_pct(other)
			local gap = FOURTH.edr_ally_gap(unit, other)
			if type(ahp) == "number" and ahp > 75 and gap ~= nil and gap <= FOURTH.EAT_DA_RUNTS_RANGE_M then
				local t = FOURTH.type_plain(other)
				local exp = (t ~= nil and FOURTH.class_keys.expendable[t] == true)
				local men = other:number_of_men_alive()
				local v = FOURTH.unit_value(other)
				local vps = (type(v) == "number" and men > 0) and (v / men) or math.huge
				if best == nil or (exp and not best_exp) or (exp == best_exp and vps < best_vps) then
					best, best_exp, best_vps, best_gap = other, exp, vps, gap
				end
			end
		end
	end
	if best == nil then return nil end
	log("  eat_da_runts ally: ui " .. tostring(best:unique_ui_id()) .. " at " .. string.format("%.1f", best_gap)
		.. "m is the cheapest healthy ally (" .. (best_exp and "expendable" or "lowest value per soldier") .. ") within "
		.. tostring(FOURTH.EAT_DA_RUNTS_RANGE_M) .. "m")
	FOURTH.cast_target = best
	FOURTH.edr_ally = best
	return string.format("eat da runts: self health %d%% (<= 75%%), cast on the cheapest healthy ally", math.floor(hp))
end
''',
    "evaluate_self_out_of_ammo": '''FOURTH.ROCK_BOTTOM_PCT = 50   -- ROUND 180 (user, 2026-11-18: "option above 50% health"): the refill costs 350 hp
function FOURTH.evaluate_self_out_of_ammo(unit, routing)
	if routing then return nil end
	local ok, a = pcall(function() return unit:ammo_left() end)
	if not (ok and type(a) == "number" and a <= 0) then return nil end
	local hp = FOURTH.health_pct(unit)
	if type(hp) ~= "number" or hp <= FOURTH.ROCK_BOTTOM_PCT then return nil end
	return string.format("no ammunition left (ammo_left 0) and health %d%% (> %d%%), cast on self", math.floor(hp),
		FOURTH.ROCK_BOTTOM_PCT)
end
''',
}
ANN_FN = {
    "evaluate_eat_da_runts": LIVE_FN["evaluate_eat_da_runts"].replace(
        '''	log("  eat_da_runts ally: ui " .. tostring(best:unique_ui_id()) .. " at " .. string.format("%.1f", best_gap)
		.. "m is the cheapest healthy ally (" .. (best_exp and "expendable" or "lowest value per soldier") .. ") within "
		.. tostring(FOURTH.EAT_DA_RUNTS_RANGE_M) .. "m")
''', "").replace('\treturn string.format("eat da runts: self health %d%% (<= 75%%), cast on the cheapest healthy ally", math.floor(hp))\n',
                 "\treturn true\n").replace("\tif routing then return nil end\n\tlocal hp", "\tif routing then return false end\n\tlocal hp").replace(
        '\tif type(hp) ~= "number" or hp > 75 then return nil end\n\tlocal self_id', '\tif type(hp) ~= "number" or hp > 75 then return false end\n\tlocal self_id').replace(
        "\tif best == nil then return nil end\n\tFOURTH.cast_target", "\tif best == nil then return false end\n\tFOURTH.cast_target"),
    "evaluate_self_out_of_ammo": LIVE_FN["evaluate_self_out_of_ammo"],
}
NEW_FNS = '''
-- ============================================================================
-- ROUND 180 - THE SCORE-3 REVIEW, ROWS 87-114 AND 128 (user, 2026-11-18).
--   melee_clear_block (Land Mine, "improve"): melee_clear, and at least half a packed block of enemy soldiers inside
--     the blast centred on the caster (BLOB_FRACTION x pi r^2 / PACKED_M2), so 3 charges do not go into one small fight.
--   health_aura_ally_rule (Blood Chalice of Bathori, Breath of Darkness x2, Mantra of Invigoration): the lowest unit
--     (the caster included) at or below 75% that the game's own target rule allows (Lord/Hero, undead, Tiger
--     Warrior: FOURTH.ab_atarget_ok), within the 70% ally bound; cast on it.
--   self_heal_clear (Bugman's XXXXXX): at or below 75% and no visible enemy within BUGMAN_CLEAR_M (the game refuses it
--     with an enemy inside its 55 m intercept range).
--   self_hurt_attacked (Potion of Charoi, Skar's Kraken-Killer): at or below 75% AND in melee or under missile fire.
--   charge_or_tired (Foe-Seeker; user: "include charge. Do not include melee, tired is enough in melee").
-- ============================================================================
function FOURTH.blast_soldiers_all(tgt, m, r)
	local share = math.pi * r * r / #FOURTH.BLOB_RING
	local got = 0
	for k = 1, #FOURTH.BLOB_RING do
		local px = tgt.x + FOURTH.BLOB_RING[k][1] * r
		local pz = tgt.z + FOURTH.BLOB_RING[k][2] * r
		for i = 1, #m.all do
			local e = m.all[i]
			if FOURTH.blob_rect_gap(px, pz, e) == 0 then got = got + e.density * share end
		end
	end
	return got
end

function FOURTH.evaluate_melee_clear_block(unit, routing)
	local why = FOURTH.evaluate_melee_clear(unit, routing)
	if not why then return nil end
	local r = FOURTH.entry_blast_r()
	local x, z = FOURTH.self_xz(unit)
	if r == nil or x == nil then return nil end
	local got = FOURTH.blast_soldiers_all({ x = x, z = z }, FOURTH.blob_map(false), r)
	local need = math.floor(FOURTH.BLOB_FRACTION * math.pi * r * r / FOURTH.PACKED_M2 + 0.5)
	if got < need then return nil end
	@@BLOCK_RETURN@@
end

function FOURTH.evaluate_health_aura_ally_rule(unit, routing)
	local chosen, hp, gap = FOURTH.ah_pick_where(unit, routing, FOURTH.ab_atarget_ok)
	if chosen == nil then return nil end
	FOURTH.ah_chosen = chosen
	FOURTH.ah_caster_su = FOURTH.ab_fresh_friend_su(unit)
	if chosen == unit then
		return string.format("health %d%% (<= 75%%), a unit the ability may target", math.floor(hp))
	end
	FOURTH.ah_ally = chosen
	FOURTH.ah_ally_su = FOURTH.ab_fresh_friend_su(chosen)
	FOURTH.cast_target = chosen
	@@RULE_RETURN@@
end

FOURTH.BUGMAN_CLEAR_M = 38   -- floor(55 * 0.70): Bugman's XXXXXX's own 55 m intercept range (target_intercept_range)
function FOURTH.evaluate_self_heal_clear(unit, routing)
	if routing then return nil end
	local hp = FOURTH.health_pct(unit)
	if type(hp) ~= "number" or hp > 75 then return nil end
	local ok_c, coll = pcall(function() return bm:get_scriptunits_for_main_enemy_army_to_local_player() end)
	if not ok_c or coll == nil then return nil end
	local ok_n, n = pcall(function() return coll:count() end)
	if not ok_n or type(n) ~= "number" then return nil end
	for i = 1, n do
		local e = nil
		pcall(function() e = coll:item(i).unit end)
		if e ~= nil then
			local ok_a, men = pcall(function() return e:number_of_men_alive() end)
			if ok_a and type(men) == "number" and men > 0 and FOURTH.enemy_not_hidden(e) then
				local ok_g, g = pcall(function() return unit:unit_distance(e) end)
				-- an unreadable gap fails closed: the game would refuse the cast with an enemy inside its range
				if not (ok_g and type(g) == "number") or g <= FOURTH.BUGMAN_CLEAR_M then return nil end
			end
		end
	end
	return string.format("health %d%% (<= 75%%) and no visible enemy within %dm", math.floor(hp), FOURTH.BUGMAN_CLEAR_M)
end

FOURTH.HURT_ATTACKED_PCT = 75   -- user, 2026-11-18 (review row 110: "caster at 75% and in melee or being shot at")
function FOURTH.evaluate_self_hurt_attacked(unit, routing)
	if routing then return nil end
	local hp = FOURTH.health_pct(unit)
	if type(hp) ~= "number" or hp > FOURTH.HURT_ATTACKED_PCT then return nil end
	local melee = (FOURTH.ah_in_melee(unit) == true)
	if not melee and not FOURTH.under_fire(unit) then return nil end
	return string.format("hurt and under attack: health %d%% (<= %d%%) while %s, cast on self", math.floor(hp),
		FOURTH.HURT_ATTACKED_PCT, melee and "in melee" or "under missile fire")
end

function FOURTH.evaluate_charge_or_tired(unit, routing)
	local r = FOURTH.evaluate_charge_only(unit, routing)
	if r then return r end
	return FOURTH.evaluate_tired(unit, routing)
end
'''
BLOCK_RETURN_LIVE = ('return why .. string.format("; %.0f enemy soldiers inside the %sm blast (needs %d, half a packed block)",\n'
                     '\t\tgot, tostring(r), need)')
RULE_RETURN_LIVE = ('FOURTH.ah_log_ally(chosen, hp, gap, "cast on that ally (the game\'s target rule allows it)")\n'
                    '\treturn string.format("%s: lowest-health unit the ability may target is an ALLY at %d%% (<= 75%%), distance %s of %sm %s - cast on the ally",\n'
                    '\t\ttostring(FOURTH.ah_marker or "ally"), math.floor(hp), ((gap ~= nil) and string.format("%.1f", gap) or "?"),\n'
                    '\t\ttostring(FOURTH.ah_range_m), tostring(FOURTH.ah_range_word))')
R = [
    # the target-rule codes
    ('\tif a.P and not FOURTH.class_member(unit, "missile") then return false end\n',
     '\tif a.P and not FOURTH.class_member(unit, "missile") then return false end\n'
     '\tif a.Z and not FOURTH.class_member(unit, "lizard") then return false end   -- ROUND 180: Cold-Blooded, set A\n'
     '\tif a.T and not FOURTH.class_member(unit, "tiger") then return false end    -- ROUND 180: the Mantras\n'),
    ('\tP = "missile allies only" }\n', '\tP = "missile allies only", Z = "Lizardmen allies only", T = "Tiger Warrior allies only" }   -- ROUND 180\n'),
    ('FOURTH.CARD_ATARGET_ORDER = { "C", "c", "L", "l", "F", "U", "u", "S", "P" }',
     'FOURTH.CARD_ATARGET_ORDER = { "C", "c", "L", "l", "F", "U", "u", "S", "P", "Z", "T" }'),
    ('\tally_squig_melee = true, self_or_ally_fire_melee = true }   -- ROUND 177\n',
     '\tally_squig_melee = true, self_or_ally_fire_melee = true,   -- ROUND 177\n'
     '\twavering_ally_range = true, health_aura_ally_rule = true }   -- ROUND 180: Cold-Blooded; the rule heals\n'),
    # Cold-Blooded: the wavering ally picker honours the game's target rule
    ('\t\t\t\t\tand FOURTH.wavering(other) == true then\n\t\t\t\t\tlocal gap = FOURTH.wa_ally_gap(unit, other)',
     '\t\t\t\t\tand FOURTH.wavering(other) == true and FOURTH.ab_atarget_ok(other) then   -- ROUND 180\n'
     '\t\t\t\t\tlocal gap = FOURTH.wa_ally_gap(unit, other)'),
    # Eat da Runts!: the chosen ally must still be healthy at the cast
    ('\tif not FOURTH.edr_ally_in_range(unit, ally) then return false end\n\tlocal hp = FOURTH.health_pct(ally)\n'
     '\treturn (type(hp) ~= "number") or (hp <= 75)\n',
     '\tif not FOURTH.edr_ally_in_range(unit, ally) then return false end\n\tlocal hp = FOURTH.health_pct(ally)\n'
     '\treturn (type(hp) ~= "number") or (hp > 75)   -- ROUND 180: never a hurt ally\n'),
    # wiring
    ('\tally_charge_or_melee = FOURTH.evaluate_ally_charge_or_melee,   -- ROUND 179\n',
     '\tmelee_clear_block = FOURTH.evaluate_melee_clear_block,   -- ROUND 180\n'
     '\thealth_aura_ally_rule = FOURTH.evaluate_health_aura_ally_rule,\n'
     '\tself_heal_clear = FOURTH.evaluate_self_heal_clear,\n'
     '\tself_hurt_attacked = FOURTH.evaluate_self_hurt_attacked,\n'
     '\tcharge_or_tired = FOURTH.evaluate_charge_or_tired,\n'
     '\tally_charge_or_melee = FOURTH.evaluate_ally_charge_or_melee,   -- ROUND 179\n'),
    ('\tally_charge_or_melee = "When armed, fires on the nearest ally charging, else just in contact, else in melee (never a missile unit)",   -- ROUND 179\n',
     '\tmelee_clear_block = "When armed, fires in melee when none of our other units is inside its blast and the blast covers half a packed block of enemies",   -- ROUND 180\n'
     '\thealth_aura_ally_rule = "When armed, fires when this unit or a friendly unit it may target is at or below 75% health, cast on it",\n'
     '\tself_heal_clear = "When armed, fires at or below 75% health with no visible enemy near",\n'
     '\tself_hurt_attacked = "When armed, fires at or below 75% health while in melee or under missile fire",\n'
     '\tcharge_or_tired = "When armed, fires when charging or tired",\n'
     '\tally_charge_or_melee = "When armed, fires on the nearest ally charging, else just in contact, else in melee (never a missile unit)",   -- ROUND 179\n'),
    ('\tally_charge_or_melee = "Fires on an ally charging, else just in contact, else in melee; no missile units",   -- ROUND 179\n',
     '\tmelee_clear_block = "Fires in melee unless wavering[, clear of allies{FF}], on a packed enemy block",   -- ROUND 180\n'
     '\thealth_aura_ally_rule = "Fires on the most hurt unit nearby it may target, below 75% health",\n'
     '\tself_heal_clear = "Fires below 75% health with no enemy near",\n'
     '\tself_hurt_attacked = "Fires below 75% health while fighting or shot at",\n'
     '\tcharge_or_tired = "Fires when charging or tired",\n'
     '\tally_charge_or_melee = "Fires on an ally charging, else just in contact, else in melee; no missile units",   -- ROUND 179\n'),
    ('\teat_da_runts = "When armed, fires when this unit is at or below 75% health, otherwise on the lowest-health ally in range",',
     '\teat_da_runts = "When armed, fires when this unit is at or below 75% health, on the cheapest healthy ally in range",   -- ROUND 180'),
    ('\teat_da_runts = "Fires on itself, else the most hurt nearby ally, below 75% health",',
     '\teat_da_runts = "Fires below 75% health, on the cheapest healthy ally",   -- ROUND 180'),
    ('\tself_out_of_ammo = "When armed, fires when this unit has no ammunition left",',
     '\tself_out_of_ammo = "When armed, fires when this unit has no ammunition left and is above 50% health",   -- ROUND 180'),
    ('\tself_out_of_ammo = "Fires when out of ammo",', '\tself_out_of_ammo = "Fires when out of ammo, above 50% health",   -- ROUND 180'),
]
SET_ANCHOR = "FOURTH.load_squigs()\n"
FN_ANCHOR = "\n-- ============================================================================\n-- ROUND 179 - THE SCORE-3 REVIEW, ROWS 115-134"

for path in (SRC, ANN):
    live = (path == SRC)
    s = open(path, encoding="utf-8", newline="").read()
    for a, b in R:
        assert s.count(a) == 1, (path[-12:], a[:90], s.count(a))
        s = s.replace(a, b)
    for m in MOVES:
        s = move_entry(s, *m)
    for h in CUT:
        s = cut_entry(s, h)
    for c in CUT_LINES:
        assert s.count(c) == 1, c
        s = s.replace(c, "")
    for fn in ("evaluate_eat_da_runts", "evaluate_self_out_of_ammo"):
        s = cut_function(s, fn)
        body = (LIVE_FN if live else ANN_FN)[fn]
        s = s.replace("@@%s@@\n" % fn, body)
    assert s.count(SET_ANCHOR) == 1
    s = s.replace(SET_ANCHOR, SET_ANCHOR + GS.lua_block())
    fns = NEW_FNS.replace("@@BLOCK_RETURN@@", BLOCK_RETURN_LIVE if live else "return true").replace(
        "@@RULE_RETURN@@", RULE_RETURN_LIVE if live else "return true")
    if not live:
        fns = fns.replace("\tlocal why = FOURTH.evaluate_melee_clear(unit, routing)\n\tif not why then return nil end\n",
                          "\tif not FOURTH.evaluate_melee_clear(unit, routing) then return false end\n")
    assert s.count(FN_ANCHOR) == 1, path
    s = s.replace(FN_ANCHOR, "\n" + fns.strip("\n") + "\n" + FN_ANCHOR, 1)
    assert "@@" not in s
    open(path, "w", encoding="utf-8", newline="").write(s)
    print(path[-36:], "patched")
