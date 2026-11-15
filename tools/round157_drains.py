#!/usr/bin/env python3
"""Round 157 (harness 156): open batch 5 - the single-target drains and the Emperor's Executioner (12 entries / 12 keys;
2 new families).

User rulings 2026-11-15 (earlier status "excluded (impossible: no enemy-unit read)", not user decisions):
  * the drains (Spirit Leech x5, The Liber Bubonicus, Death's Timekeeper, Rancid Visitations, 'Effagee' of da Git,
    Punch-Dagger; the game's max_damaged_entities = 1): "Most valuable single" + "Standing still" -> NEW
    enemy_single_drain: the visible single-entity enemy in range with the highest live value, the caster standing
    still; NO friendly-fire margin (a direct effect cannot hit our units), so an enemy fighting ours qualifies.
  * The Emperor's Executioner (base: Lord/Hero only, executes at 20%; upgrade: any target, 33%): "At the execute line"
    -> NEW enemy_execute: the most valuable enemy in range whose health is at or below the line (the GENERATED EXEC
    table from execute_ratio); the base version keeps the game's commander class, the upgrade takes single entities.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_shot_tables as GS  # noqa: E402

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"


def sub(s, a, b):
    assert s.count(a) == 1, (a[:80], s.count(a))
    return s.replace(a, b)


def entry(marker, name, trig, key, extra):
    lines = ['\t{ marker = "%s", name = "%s", trigger = "%s",' % (marker, name, trig),
             '\t\tbadge = "zz_auto_badge_%s",' % marker,
             '\t\tkeys = { "%s" },' % key]
    lines += ["\t\t%s," % e for e in extra]
    lines += ["\t\tox = 0, oy = 0 },"]
    return "\n".join(lines) + "\n"


D = "enemy_single_drain"
ROWS = [
    ("spirit_leech_death_bound", "Spirit Leech", D, "wh2_dlc09_spell_death_spirit_leech_bound", ["range_real = 100"]),
    ("spirit_leech_dlc25", "Spirit Leech", D, "wh3_dlc25_spell_bound_spirit_leech", ["range_real = 100"]),
    ("spirit_leech_gunnery_school", "Spirit Leech", D, "wh3_dlc25_spell_bound_spirit_leech_gunnery_school",
     ["range_real = 100"]),
    ("spirit_leech", "Spirit Leech", D, "wh3_main_spell_bound_spirit_leech", ["range_real = 100"]),
    ("spirit_leech_guo_ror", "Spirit Leech", D, "wh3_twa08_spell_bound_spirit_leech_great_unclean_one_ror",
     ["range_real = 100"]),
    ("liber_bubonicus", "The Liber Bubonicus", D, "wh2_main_item_abilities_the_liber_bubonicus", ["range_real = 100"]),
    ("deaths_timekeeper", "Death's Timekeeper", D, "wh3_dlc25_item_abilities_deaths_timekeeper", ["range_real = 100"]),
    ("rancid_visitations", "Rancid Visitations", D, "wh3_main_spell_bound_rancid_visitations", ["range_real = 100"]),
    ("effagee_of_da_git", "'Effagee' of da Git", D, "wh_dlc06_character_abilities_effagee_of_da_git", ["range_real = 100"]),
    ("punch_dagger", "Punch-Dagger", D, "wh3_dlc29_item_abilities_punch_dagger", ["range_real = 15"]),
    ("emperors_executioner", "The Emperor's Executioner", "enemy_execute",
     "wh3_dlc24_lord_abilities_the_emperors_executioner", ["range_real = 50", 'target_class = "commander"']),
    ("emperors_executioner_upgrade", "The Emperor's Executioner", "enemy_execute",
     "wh3_dlc24_lord_abilities_the_emperors_executioner_upgrade", ["range_real = 50"]),
]
KEYS = [r[3] for r in ROWS]
NEW_ENTRIES = "".join(entry(*r) for r in ROWS)
WIND = [("wh2_dlc09_spell_death_spirit_leech_bound", "3"), ("wh3_dlc25_spell_bound_spirit_leech", "1"),
        ("wh3_dlc25_spell_bound_spirit_leech_gunnery_school", "1"), ("wh3_main_spell_bound_spirit_leech", "1"),
        ("wh3_twa08_spell_bound_spirit_leech_great_unclean_one_ror", "1"),
        ("wh3_main_spell_bound_rancid_visitations", "3"), ("wh3_dlc24_lord_abilities_the_emperors_executioner", "2"),
        ("wh3_dlc24_lord_abilities_the_emperors_executioner_upgrade", "2")]
HOLD = [("wh2_dlc09_spell_death_spirit_leech_bound", 45), ("wh3_dlc25_spell_bound_spirit_leech", 32),
        ("wh3_main_spell_bound_spirit_leech", 60), ("wh2_main_item_abilities_the_liber_bubonicus", 120),
        ("wh3_dlc25_item_abilities_deaths_timekeeper", 120), ("wh3_main_spell_bound_rancid_visitations", 90),
        ("wh_dlc06_character_abilities_effagee_of_da_git", 120), ("wh3_dlc29_item_abilities_punch_dagger", 120)]

RESTOCK = '\t{ marker = "restock", name = "Restock!", trigger = "ally_ammo_low",'
WIND_OLD = "\twind_up_s = {\n"
WIND_NEW = WIND_OLD + "\t\t-- ROUND 157: the drains' and the Executioner's wind-ups (unit_spec_abil wind_up_time)\n" + "".join(
    '\t\t["%s"] = %s,\n' % (k, v) for k, v in WIND)
HOLD_OLD = "\thold_s = {\n"
HOLD_NEW = HOLD_OLD + "\t\t-- ROUND 157: the drains with more than one use (recharge_time)\n" + "".join(
    '\t\t["%s"] = %d,\n' % (k, v) for k, v in HOLD)

CAND_OLD = '''-- a map candidate: the entry's class, in the bound, past the minimum range, and safe
function FOURTH.shot_cand_ok(unit, e, m)
	if not (FOURTH.eg_class_ok(e.unit) and FOURTH.eg_enemy_within_bound(unit, e.unit)
		and FOURTH.shot_min_ok(unit, e.unit)) then
		return false
	end
	local g = FOURTH.blob_friend_gap(e, m, FOURTH.SHOT_SAFE_M)
'''
CAND_NEW = '''-- a map candidate: the entry's class, in the bound, past the minimum range, and safe. ROUND 157: nosafe = a direct
-- effect that cannot hit our units (the drains, the Executioner) skips the safety test
function FOURTH.shot_cand_ok(unit, e, m, nosafe)
	if not (FOURTH.eg_class_ok(e.unit) and FOURTH.eg_enemy_within_bound(unit, e.unit)
		and FOURTH.shot_min_ok(unit, e.unit)) then
		return false
	end
	if nosafe then return true end
	local g = FOURTH.blob_friend_gap(e, m, FOURTH.SHOT_SAFE_M)
'''
PICK_OLD = '''function FOURTH.shot_pick(unit, m, kind, large_only)
'''
PICK_NEW = '''-- ROUND 157: the current entry's execute line in percent (the GENERATED EXEC table x 100; nil: none)
function FOURTH.exec_line()
	local key = FOURTH.rc_self_keys and FOURTH.rc_self_keys[1]
	local r = key and FOURTH.EXEC[key]
	if r == nil then return nil end
	return r * 100
end

-- ROUND 157: an execute candidate: health (the ONE reader, 0-100) at or below the line; a Lord/Hero-only entry relies
-- on its target class, any other must be a single entity
function FOURTH.exec_ok(e)
	local line = FOURTH.exec_line()
	if line == nil then return false end
	local hp = FOURTH.enemy_health_pct(e.unit)
	if type(hp) ~= "number" or hp > line then return false end
	if FOURTH.eg_class == "commander" then return true end
	return e.t ~= nil and FOURTH.class_keys.single[e.t] == true
end

-- ROUND 157: kinds "drain" (as "single") and "execute"; nosafe skips the safety test
function FOURTH.shot_pick(unit, m, kind, large_only, nosafe)
'''
KIND_OLD = '''		elseif kind == "single" then
			ok_kind = (e.t ~= nil and FOURTH.class_keys.single[e.t] == true)
				and (not large_only or FOURTH.class_keys.large[e.t] == true)
			s1 = e.value or 0
'''
KIND_NEW = '''		elseif kind == "single" or kind == "drain" then
			ok_kind = (e.t ~= nil and FOURTH.class_keys.single[e.t] == true)
				and (not large_only or FOURTH.class_keys.large[e.t] == true)
			s1 = e.value or 0
		elseif kind == "execute" then
			ok_kind = FOURTH.exec_ok(e)
			s1 = e.value or 0
'''
USE_OLD = "\t\tif ok_kind and FOURTH.shot_cand_ok(unit, e, m) then\n"
USE_NEW = "\t\tif ok_kind and FOURTH.shot_cand_ok(unit, e, m, nosafe) then\n"
TAKE_OLD = '''function FOURTH.shot_take(unit, e, kind, still)
	FOURTH.shot_kind = kind
	FOURTH.shot_still_needed = still
'''
TAKE_NEW = '''function FOURTH.shot_take(unit, e, kind, still, nosafe)
	FOURTH.shot_kind = kind
	FOURTH.shot_still_needed = still
	FOURTH.shot_nosafe = nosafe   -- ROUND 157
'''
STILL_OLD = '''	if kind == nil then return false end
	if not FOURTH.shot_caster_ok(unit, FOURTH.shot_still_needed) then return false end
	local m = FOURTH.blob_map(true)
'''
STILL_NEW = '''	if kind == nil then return false end
	if kind == "drain" then
		if not FOURTH.blob_still(unit) then return false end   -- ROUND 157: standing still, melee allowed
	elseif kind ~= "execute" then
		if not FOURTH.shot_caster_ok(unit, FOURTH.shot_still_needed) then return false end
	end
	local m = FOURTH.blob_map(true)
'''
STILL2_OLD = '''			if kind == "single" and not (e.t ~= nil and FOURTH.class_keys.single[e.t] == true) then return false end
			if kind == "armour" and not (e.t ~= nil and FOURTH.UNIT_DEF[e.t] ~= nil) then return false end
			return FOURTH.shot_cand_ok(unit, e, m)
'''
STILL2_NEW = '''			if (kind == "single" or kind == "drain") and not (e.t ~= nil and FOURTH.class_keys.single[e.t] == true) then
				return false
			end
			if kind == "armour" and not (e.t ~= nil and FOURTH.UNIT_DEF[e.t] ~= nil) then return false end
			if kind == "execute" and not FOURTH.exec_ok(e) then return false end   -- ROUND 157
			return FOURTH.shot_cand_ok(unit, e, m, FOURTH.shot_nosafe)
'''
REASON_OLD = '''	return string.format("%s (targeting %s, %s); none of ours within %dm; distance %sm bound %sm", what, etype, score,
		FOURTH.SHOT_SAFE_M, (d ~= nil) and string.format("%.1f", d) or "?", tostring(FOURTH.eg_range_m))
'''
REASON_NEW = '''	local safe = string.format("none of ours within %dm", FOURTH.SHOT_SAFE_M)
	if FOURTH.shot_nosafe then safe = "a direct effect (cannot hit our units)" end   -- ROUND 157
	return string.format("%s (targeting %s, %s); %s; distance %sm bound %sm", what, etype, score, safe,
		(d ~= nil) and string.format("%.1f", d) or "?", tostring(FOURTH.eg_range_m))
'''
SAFE_OLD = "FOURTH.shot_still_needed = nil\n"
SAFE_NEW = "FOURTH.shot_still_needed = nil\nFOURTH.shot_nosafe = nil   -- ROUND 157\n"

EVALS = r'''-- ============================================================================
-- ROUND 157 - THE DRAINS AND THE EXECUTIONER (open batch 5, user rulings 2026-11-15).
--   enemy_single_drain ("Most valuable single", "Standing still"; Spirit Leech
--     x5, The Liber Bubonicus, Death's Timekeeper, Rancid Visitations, 'Effagee'
--     of da Git, Punch-Dagger: the game's max_damaged_entities = 1): the visible
--     single-entity enemy in range with the highest live value; the caster
--     standing still; no friendly-fire margin (a direct effect cannot hit our
--     units), so an enemy fighting ours qualifies.
--   enemy_execute ("At the execute line"; The Emperor's Executioner): the most
--     valuable enemy in range whose health is at or below the GENERATED execute
--     line (base 20%, Lord/Hero only by the game's own class; upgrade 33%, single
--     entities).
-- ============================================================================
function FOURTH.evaluate_enemy_single_drain(unit, routing)
	FOURTH.eg_mode = "shot"
	FOURTH.shot_kind = nil
	if routing or not FOURTH.blob_still(unit) then return %NO% end
	local m = FOURTH.blob_map(false)
	local e, s = FOURTH.shot_pick(unit, m, "drain", false, true)
	if e == nil then return %NO% end
	FOURTH.shot_take(unit, e, "drain", true, true)
	%RET_DRAIN%
end

function FOURTH.evaluate_enemy_execute(unit, routing)
	FOURTH.eg_mode = "shot"
	FOURTH.shot_kind = nil
	if routing then return %NO% end
	local m = FOURTH.blob_map(false)
	local e, s = FOURTH.shot_pick(unit, m, "execute", false, true)
	if e == nil then return %NO% end
	FOURTH.shot_take(unit, e, "execute", false, true)
	%RET_EXEC%
end

'''
LIVE_RET = {
    "%NO%": "nil",
    "%RET_DRAIN%": ('return FOURTH.shot_reason(unit, e, "most valuable single-entity enemy, standing still (a drain)",\n'
                    '\t\tstring.format("value %.0f", s))'),
    "%RET_EXEC%": ('local hp = FOURTH.enemy_health_pct(e.unit)\n'
                   '\treturn FOURTH.shot_reason(unit, e, "enemy at or below the execute line",\n'
                   '\t\tstring.format("health %.0f%% <= %.0f%%, value %.0f", hp or -1, FOURTH.exec_line() or -1, s))'),
}
ANN_RET = {"%NO%": "false", "%RET_DRAIN%": "return true", "%RET_EXEC%": "return true"}


def render(tpl, rep):
    for k, v in rep.items():
        tpl = tpl.replace(k, v)
    assert "%NO%" not in tpl and "%RET_" not in tpl
    return tpl


FAMS = ["enemy_single_drain", "enemy_execute"]
MAP_OLD = "\tenemy_melee_or_shooting = FOURTH.evaluate_enemy_melee_or_shooting,\n"
MAP_NEW = MAP_OLD + "\t-- ROUND 157\n" + "".join("\t%s = FOURTH.evaluate_%s,\n" % (f, f) for f in FAMS)
TIP_OLD = ('\tenemy_melee_or_shooting = "When armed, fires on the closest enemy in range that is fighting in melee, otherwise on '
           'the closest enemy missile unit that is shooting",\n')
TIP_NEW = TIP_OLD + (
    '\tenemy_single_drain = "When armed and standing still, fires on the most valuable single-entity enemy in range '
    '(lord, hero or monster)",\n'
    '\tenemy_execute = "When armed, fires on the most valuable enemy in range whose health is at or below the execute '
    'line",\n')
ANCHOR = "FOURTH.evaluators = {\n"
GEN = re.compile(r"-- GENERATED by tools/gen_shot_tables\.py from unit_spec_abil.*?\nFOURTH\.load_shot_table\(\)\n", re.S)

for path, live in ((SRC, True), (ANN, False)):
    s = open(path, encoding="utf-8", newline="").read()
    assert "evaluate_enemy_single_drain" not in s and "FOURTH.EXEC_TEXT" not in s
    before = s.count("\t{ marker = ")
    s = sub(s, RESTOCK, NEW_ENTRIES + RESTOCK)
    s = sub(s, WIND_OLD, WIND_NEW)
    s = sub(s, HOLD_OLD, HOLD_NEW)
    for a, b in ((CAND_OLD, CAND_NEW), (PICK_OLD, PICK_NEW), (KIND_OLD, KIND_NEW), (USE_OLD, USE_NEW),
                 (TAKE_OLD, TAKE_NEW), (STILL_OLD, STILL_NEW), (STILL2_OLD, STILL2_NEW), (SAFE_OLD, SAFE_NEW)):
        s = sub(s, a, b)
    if live:
        s = sub(s, REASON_OLD, REASON_NEW)
    s = sub(s, MAP_OLD, MAP_NEW)
    s = sub(s, TIP_OLD, TIP_NEW)
    s = sub(s, ANCHOR, render(EVALS, LIVE_RET if live else ANN_RET) + ANCHOR)
    assert s.count("\t{ marker = ") == before + 12
    open(path, "w", encoding="utf-8", newline="").write(s)
    print(path, "entries", before, "->", before + 12)

src_now = open(SRC, encoding="utf-8").read()
ks = GS.keys_in(src_now)
assert len(ks) == 23, len(ks)
block = GS.lua_block(GS.derive(ks)) + GS.exec_block(GS.exec_rows(set(ks)))
for path in (SRC, ANN):
    s = open(path, encoding="utf-8", newline="").read()
    assert len(GEN.findall(s)) == 1
    s = GEN.sub(lambda m: block, s)
    open(path, "w", encoding="utf-8", newline="").write(s)
print("SHOT table re-derived (23 keys) + EXEC table")

import gen_recharge_keys as G  # noqa: E402
new_block = G.lua_block(G.derive())
pat = re.compile(r"-- GENERATED by tools/gen_recharge_keys\.py.*?\nFOURTH\.load_recharge\(\)\n", re.S)
for path in (SRC, ANN):
    s = open(path, encoding="utf-8", newline="").read()
    assert len(pat.findall(s)) == 1
    s = pat.sub(lambda m: new_block, s)
    open(path, "w", encoding="utf-8", newline="").write(s)
print("lock table re-derived:", len(G.derive()), "keys")
