#!/usr/bin/env python3
"""Round 137 (harness 136): audit batch 6 - the morale abilities fire when morale is in danger.

User rulings 2026-11-09 (audit group R6):
  * the morale-only auras centred on the caster: "Self or ally wavering" -> the NEW wavering_aura: the caster,
    or any friendly unit inside the aura's 70% bound (the whole army for Unholy Clamour; nobody else for the
    self-only Mirror (Cold-Blooded)), is wavering; cast on the caster. Call of Violence, Get Back 'Ere!,
    Magical Animus, Rally!, Reanimate, Reanimate Upgraded, Pearl of Infinite Bleakness, Unholy Clamour,
    Mirror (Cold-Blooded);
  * the single-target Unbreakable / Leadership spells: "On the wavering ally" (Crown of Command, Doom Lord,
    Cold-Blooded) - the rampage arm was dropped (no battle read exists); Tacticians, Rally! and Pilgrimage of
    Skulls (the game forbids targeting the caster): "On the wavering ally" -> the existing wavering_ally_range,
    each with its own 70% ally bound;
  * morale plus a combat stat (6) and the five on dedicated triggers: kept (listed as ruled in the audit);
  * vigour: a one-by-one review later ("Tired or worse" is the line).
The morale read is the existing FOURTH.wavering (is_wavering()); only an exact true counts here.
No string.find. Every helper is a FOURTH field.
"""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"

# marker -> aura_real (effect_range from unit_spec_abil.tsv; -1 = the whole army; None = self only)
TO_AURA = {"call_of_violence": 35, "get_back_ere": 35, "magical_animus": 35, "rally": 35, "tomb_king_rally": 35,
           "tomb_king_rally_upgraded": 35, "pearl_of_infinite_bleakness": 35, "unholy_clamour": -1,
           "mimic_cold_blooded": None}
# marker -> ally_range_real (target_intercept_range)
TO_ALLY = {"crown_of_command": 100, "doom_lord": 200, "cold_blooded": 200, "pilgrimage_of_skulls": 100,
           "tacticians_rally": 100}


def entry_span(s, marker):
    tag = '\t{ marker = "%s",' % marker
    assert s.count(tag) == 1, marker
    a = s.index(tag)
    b = s.index("ox = 0, oy = 0 },\n", a) + len("ox = 0, oy = 0 },\n")
    block = s[a:b]
    assert block.count("\t{ marker = ") == 1 and 'trigger = "melee_unwavering",' in block, marker
    assert "aura_real" not in block and "range_real" not in block, marker
    return a, b, block


def sub(s, a, b):
    assert s.count(a) == 1, (a[:80], s.count(a))
    return s.replace(a, b)


COMMON = """-- ============================================================================
-- ROUND 137 - AUDIT BATCH 6: MORALE (user rulings 2026-11-09).
--   wavering_aura (NEW): the caster is wavering, or a friendly unit inside the
--     aura's 70% bound is wavering (aura_real -1 = the whole army; no aura_real
--     = the caster only); cast on the caster. The morale read is FOURTH.wavering
--     (is_wavering()); only an exact true counts, so an unreadable morale never
--     fires. A routing ally is not counted (its morale is already gone).
--   wavering_ally_range gains Crown of Command, Doom Lord, Cold-Blooded,
--     Pilgrimage of Skulls and Tacticians, Rally! (cast on the wavering ally).
-- ============================================================================

-- the closest OTHER friendly unit (alive, not routing) that is wavering and lies
-- inside the current entry's aura bound; a negative bound = the whole army; nil
-- bound = nobody (a self-only effect). An unreadable distance counts only for
-- the whole-army aura.
function FOURTH.wavering_ally_in_aura(unit)
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
				and not unit_is_routing(other) and FOURTH.wavering(other) == true then
				local gap = FOURTH.ab_ally_gap(unit, other)
				if bound < 0 and gap == nil then gap = 0 end
				if gap ~= nil and (bound < 0 or gap <= bound) and (best_gap == nil or gap < best_gap) then
					best, best_gap = other, gap
				end
			end
		end
	end
	return best, best_gap
end

"""

EVAL_LIVE = """function FOURTH.evaluate_wavering_aura(unit, routing)
	if routing then return nil end
	if FOURTH.wavering(unit) == true then
		return "wavering aura: the caster is wavering, cast centred on the caster"
	end
	local ally, gap = FOURTH.wavering_ally_in_aura(unit)
	if ally == nil then return nil end
	local atype = "ally"
	pcall(function() atype = tostring(ally:type()) end)
	if FOURTH.fa_bound_m < 0 then
		return "wavering aura: a friendly unit (" .. atype .. ") is wavering, the whole army is covered - cast centred on the caster"
	end
	return string.format("wavering aura: a friendly unit (%s) %.1fm away is wavering (bound %dm), cast centred on the caster",
		atype, gap, FOURTH.fa_bound_m)
end

"""

EVAL_ANN = """function FOURTH.evaluate_wavering_aura(unit, routing)
	if routing then return false end
	if FOURTH.wavering(unit) == true then return true end
	return FOURTH.wavering_ally_in_aura(unit) ~= nil
end

"""

MAP_OLD = "\tenemy_fast_near_ally = FOURTH.evaluate_enemy_fast_near_ally,\n"
MAP_NEW = MAP_OLD + "\t-- ROUND 137\n\twavering_aura = FOURTH.evaluate_wavering_aura,\n"
TIP_OLD = '\tenemy_fast_near_ally = "When armed, fires on a fast enemy unit moving close to your units",\n'
TIP_NEW = TIP_OLD + '\twavering_aura = "When armed, fires when this unit or a friendly unit near it is wavering",\n'
ANCHOR = "FOURTH.evaluators = {\n"

for path, ev in ((SRC, EVAL_LIVE), (ANN, EVAL_ANN)):
    s = open(path, encoding="utf-8", newline="").read()
    assert "wavering_aura" not in s
    before = (s.count('trigger = "melee_unwavering"'), s.count('trigger = "wavering_ally_range"'))
    for m, aura in TO_AURA.items():
        a, b, block = entry_span(s, m)
        nb = block.replace('trigger = "melee_unwavering",', 'trigger = "wavering_aura",')
        if aura is not None:
            nb = nb.replace("\t\tox = 0, oy = 0 },\n", "\t\taura_real = %d,\n\t\tox = 0, oy = 0 },\n" % aura)
        s = s[:a] + nb + s[b:]
    for m, rng in TO_ALLY.items():
        a, b, block = entry_span(s, m)
        nb = block.replace('trigger = "melee_unwavering",', 'trigger = "wavering_ally_range",')
        nb = nb.replace("\t\tox = 0, oy = 0 },\n", "\t\tally_range_real = %d,\n\t\tox = 0, oy = 0 },\n" % rng)
        s = s[:a] + nb + s[b:]
    s = sub(s, MAP_OLD, MAP_NEW)
    s = sub(s, TIP_OLD, TIP_NEW)
    s = sub(s, ANCHOR, COMMON + ev + ANCHOR)
    after = (s.count('trigger = "melee_unwavering"'), s.count('trigger = "wavering_ally_range"'),
             s.count('trigger = "wavering_aura"'))
    assert after == (before[0] - 14, before[1] + 5, 9), (before, after)
    open(path, "w", encoding="utf-8", newline="").write(s)
    print(path, before, "->", after)
