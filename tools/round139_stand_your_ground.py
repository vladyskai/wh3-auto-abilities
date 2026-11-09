#!/usr/bin/env python3
"""Round 139 (harness 138): Stand Your Ground fires for the allies it protects (QA battle 1 finding).

QA battle 1 (2026-11-09): Stand Your Ground (Melee Defence +24, Leadership +16 to the caster and allies within
35 m) fired ONCE, at 232 s, when the General himself was in melee and wavering (melee_low_morale); the Spearmen
around him had been wavering since 177 s. User ruling, verbatim: "The general or any friendly unit within 24m is
in melee or wavering." -> the NEW melee_or_wavering_aura: the caster in melee or wavering, or a friendly unit
(alive, not routing) within the 70% aura bound (35 m -> 24 m) in melee or wavering; cast on the caster.
Only an exact true counts for wavering. melee_low_morale keeps its evaluator with no entry.
"""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"


def sub(s, a, b):
    assert s.count(a) == 1, (a[:80], s.count(a))
    return s.replace(a, b)


ENTRY_OLD = ('\t{ marker = "stand_your_ground", name = "Stand Your Ground", trigger = "melee_low_morale",\n'
             '\t\tbadge = "zz_auto_badge_syg",\n'
             '\t\tkeys = { "wh_main_character_abilities_stand_your_ground",\n'
             '\t\t\t"wh3_dlc24_character_abilities_tacticians_stand_your_ground" },\n'
             '\t\tox = 66, oy = 172 },\n')
ENTRY_NEW = ('\t{ marker = "stand_your_ground", name = "Stand Your Ground", trigger = "melee_or_wavering_aura",\n'
             '\t\tbadge = "zz_auto_badge_syg",\n'
             '\t\tkeys = { "wh_main_character_abilities_stand_your_ground",\n'
             '\t\t\t"wh3_dlc24_character_abilities_tacticians_stand_your_ground" },\n'
             '\t\taura_real = 35,\n'
             '\t\tox = 66, oy = 172 },\n')

COMMON = """-- ============================================================================
-- ROUND 139 - STAND YOUR GROUND FIRES FOR THE ALLIES IT PROTECTS (QA battle 1).
--   melee_or_wavering_aura (NEW): the caster is in melee or wavering, or a
--   friendly unit (alive, not routing) inside the aura's 70% bound (35 m ->
--   24 m) is in melee or wavering; cast on the caster. User ruling 2026-11-09:
--   "The general or any friendly unit within 24m is in melee or wavering."
--   Wavering counts only on an exact true (FOURTH.wavering).
-- ============================================================================
function FOURTH.melee_or_wavering(u)
	local ok, m = pcall(function() return u:is_in_melee() end)
	if ok and m == true then return true end
	return FOURTH.wavering(u) == true
end

"""
EVAL_LIVE = """function FOURTH.evaluate_melee_or_wavering_aura(unit, routing)
	if routing then return nil end
	local ok, m = pcall(function() return unit:is_in_melee() end)
	if ok and m == true then
		return "melee or wavering aura: the caster is in melee, cast centred on the caster"
	end
	if FOURTH.wavering(unit) == true then
		return "melee or wavering aura: the caster is wavering, cast centred on the caster"
	end
	local ally, gap = FOURTH.ally_in_aura(unit, FOURTH.melee_or_wavering)
	if ally == nil then return nil end
	return string.format("melee or wavering aura: a friendly unit %.1fm away (bound %dm) is in melee or wavering, cast centred on the caster",
		gap, FOURTH.fa_bound_m)
end

"""
EVAL_ANN = """function FOURTH.evaluate_melee_or_wavering_aura(unit, routing)
	if routing then return false end
	if FOURTH.melee_or_wavering(unit) then return true end
	return FOURTH.ally_in_aura(unit, FOURTH.melee_or_wavering) ~= nil
end

"""
MAP_OLD = "\tenemy_missile_shooting = FOURTH.evaluate_enemy_missile_shooting,\n"
MAP_NEW = MAP_OLD + "\t-- ROUND 139\n\tmelee_or_wavering_aura = FOURTH.evaluate_melee_or_wavering_aura,\n"
TIP_OLD = '\tenemy_missile_shooting = "When armed, fires on the closest enemy missile unit in range that is shooting",\n'
TIP_NEW = TIP_OLD + '\tmelee_or_wavering_aura = "When armed, fires when this unit or a friendly unit near it is in melee or wavering",\n'
ANCHOR = "FOURTH.evaluators = {\n"
# the annotated copy carries a trailing comment on the ox line, so the entry is patched in two narrow places
ENTRY_LINE_OLD = '\t{ marker = "stand_your_ground", name = "Stand Your Ground", trigger = "melee_low_morale",\n'
ENTRY_LINE_NEW = '\t{ marker = "stand_your_ground", name = "Stand Your Ground", trigger = "melee_or_wavering_aura",\n'
OX_OLD = "\t\tox = 66, oy = 172 },"
OX_NEW = "\t\taura_real = 35,\n\t\tox = 66, oy = 172 },"

for path, ev in ((SRC, EVAL_LIVE), (ANN, EVAL_ANN)):
    s = open(path, encoding="utf-8", newline="").read()
    assert "melee_or_wavering_aura" not in s
    s = sub(s, ENTRY_LINE_OLD, ENTRY_LINE_NEW)
    s = sub(s, OX_OLD, OX_NEW)
    s = sub(s, MAP_OLD, MAP_NEW)
    s = sub(s, TIP_OLD, TIP_NEW)
    s = sub(s, ANCHOR, COMMON + ev + ANCHOR)
    assert s.count('trigger = "melee_low_morale"') == 0 and s.count('trigger = "melee_or_wavering_aura"') == 1
    open(path, "w", encoding="utf-8", newline="").write(s)
    print(path, "Stand Your Ground -> melee_or_wavering_aura")
