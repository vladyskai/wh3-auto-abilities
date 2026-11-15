#!/usr/bin/env python3
"""Round 156 (harness 155): open batch 4 - the 11 non-exploding magic missiles (11 entries / 11 keys; 5 new families).

User rulings 2026-11-15 (earlier status "excluded (impossible: no enemy-unit read)" / "excluded (auto: explosive
projectile)", not user decisions; the map of round 145 removed the old block):
  * AP shots (Blast, Damned Pistol, Hunting Spear, Master Rune of Flight, Schalkain's Teeth): "Large first, then
    armour" -> NEW enemy_large_shot: the visible LARGE enemy in range with the highest live value, none of ours within
    10 m of it, the caster out of melee; otherwise the most armoured safe enemy infantry in range.
  * Snipers (Dead Eye, Focused Shot): "Most valuable single" -> NEW enemy_single_shot: the single-entity enemy (the
    game's unit_is_not_single_entity rule, new class "single") in range with the highest live value, the caster
    standing still and out of melee, none of ours within 10 m; Focused Shot (bonus v large) takes a large one first.
  * Debuff throws: "Split by effect" -> NEW enemy_melee_or_fast (Crippling Throw, the Golden Blowpipe: the closest
    enemy in melee, else a fast enemy closing on our units) and NEW enemy_melee_or_shooting (Spear of Kurnous: the
    closest enemy in melee, else the closest enemy missile unit that is shooting).
  * Bolt Storm: "Most valuable infantry" -> NEW enemy_infantry_shot: the visible enemy infantry in range with the
    highest live value per soldier, none of ours within 10 m, the caster standing still and out of melee.
The game's own usage rule engaged_in_melee (Bolt Storm, Crippling Throw) and min_range (Master Rune of Flight, the
Blowpipe: 5 m) come from the GENERATED SHOT table (tools/gen_shot_tables.py).
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


ROWS = [
    ("blast", "Blast", "enemy_large_shot", "wh2_dlc10_item_bound_blast", ["range_real = 100"]),
    ("damned_pistol", "Damned Pistol", "enemy_large_shot", "wh3_main_weapon_abilities_godkiller_pistol",
     ["range_real = 100"]),
    ("hunting_spear", "Hunting Spear", "enemy_large_shot", "wh_dlc03_weapon_abilities_hunting_spear",
     ["range_real = 200"]),
    ("master_rune_of_flight", "Master Rune of Flight", "enemy_large_shot",
     "wh2_dlc17_rune_abilities_master_rune_of_flight", ["range_real = 100"]),
    ("schalkains_teeth", "Schalkain's Teeth", "enemy_large_shot", "wh3_dlc27_item_abilities_schalkains_teeth",
     ["range_real = 200"]),
    ("dead_eye", "Dead Eye", "enemy_single_shot", "wh3_dlc26_character_abilities_dead_eye",
     ["range_real = 150", 'target_class = "single"']),
    ("focused_shot", "Focused Shot", "enemy_single_shot", "wh2_dlc13_lord_abilities_kill_shot",
     ["range_real = 250", 'target_class = "single"']),
    ("crippling_throw", "Crippling Throw", "enemy_melee_or_fast", "wh3_main_character_abilities_crippling_throw",
     ["range_real = 120"]),
    ("golden_blowpipe", "The Golden Blowpipe of P'Toohee", "enemy_melee_or_fast",
     "wh2_dlc17_weapon_abilities_the_golden_blowpipe_of_ptoohee", ["range_real = 200"]),
    ("spear_of_kurnous", "Spear of Kurnous", "enemy_melee_or_shooting", "wh_dlc05_weapon_abilities_spear_of_kurnous",
     ["range_real = 200"]),
    ("bolt_storm", "Bolt Storm", "enemy_infantry_shot", "wh3_main_weapon_abilities_nuku_chos_crossbow",
     ["range_real = 250"]),
]
KEYS = [r[3] for r in ROWS]
NEW_ENTRIES = "".join(entry(*r) for r in ROWS)
WIND = [("wh3_main_weapon_abilities_nuku_chos_crossbow", "1"), ("wh3_main_character_abilities_crippling_throw", "3"),
        ("wh3_main_weapon_abilities_godkiller_pistol", "2.3"), ("wh3_dlc26_character_abilities_dead_eye", "5"),
        ("wh2_dlc13_lord_abilities_kill_shot", "5"), ("wh2_dlc17_weapon_abilities_the_golden_blowpipe_of_ptoohee", "2.5")]
HOLD = [("wh3_main_character_abilities_crippling_throw", 90), ("wh3_main_weapon_abilities_godkiller_pistol", 120),
        ("wh2_dlc13_lord_abilities_kill_shot", 120), ("wh3_dlc27_item_abilities_schalkains_teeth", 90)]

RESTOCK = '\t{ marker = "restock", name = "Restock!", trigger = "ally_ammo_low",'
WIND_OLD = "\twind_up_s = {\n"
WIND_NEW = WIND_OLD + "\t\t-- ROUND 156: the magic missiles' wind-ups (unit_spec_abil wind_up_time)\n" + "".join(
    '\t\t["%s"] = %s,\n' % (k, v) for k, v in WIND)
HOLD_OLD = "\thold_s = {\n"
HOLD_NEW = HOLD_OLD + "\t\t-- ROUND 156: the magic missiles with more than one use (recharge_time)\n" + "".join(
    '\t\t["%s"] = %d,\n' % (k, v) for k, v in HOLD)

R120_OLD = "FOURTH.ENEMY_CAST_R600 = 420   -- ROUND 146: blob attacks, floor(600 x 0.70)\n"
R120_NEW = R120_OLD + "FOURTH.ENEMY_CAST_R120 = 84   -- ROUND 156: Crippling Throw, floor(120 x 0.70)\n"
MAP120_OLD = "\t[600]  = FOURTH.ENEMY_CAST_R600,\n"
MAP120_NEW = MAP120_OLD + "\t[120]  = FOURTH.ENEMY_CAST_R120,\n"

CLASS_OLD = '\tif cls == "large" then return FOURTH.class_keys.large[t] == true end\n'
CLASS_NEW = CLASS_OLD + ('\t-- ROUND 156: Dead Eye and Focused Shot (the game\'s unit_is_not_single_entity): the GENERATED single set\n'
                         '\tif cls == "single" then return FOURTH.class_keys.single[t] == true end\n')

SHAPE_OLD = '\tif ok_v and type(sv) == "number" and sv > 0 then s.vps = sv / men end\n'
SHAPE_NEW = SHAPE_OLD + '\tif ok_v and type(sv) == "number" then s.value = sv end   -- ROUND 156: the whole unit\'s live value\n'
MAPT_OLD = "\tlocal m = { ours = {}, enemies = {}, large = {}, alliance = (alliance ~= nil) }\n"
MAPT_NEW = ("\t-- ROUND 156: m.all = EVERY visible enemy shape (flying ones too), for the magic-missile pickers\n"
            "\tlocal m = { ours = {}, enemies = {}, large = {}, all = {}, alliance = (alliance ~= nil) }\n")
MAPA_OLD = "\t\t\t\t\t\tlocal s = FOURTH.blob_shape(e)\n"
MAPA_NEW = MAPA_OLD + "\t\t\t\t\t\tif s ~= nil then m.all[#m.all + 1] = s end   -- ROUND 156\n"

EG_OLD = ('\t\telseif eg_mode_now == "blob" then\n'
          '\t\t\t-- ROUND 146: the blob trigger - the map is rebuilt and the target must still be safe and dense\n'
          '\t\t\tcond_now = FOURTH.blob_still_ok(enemy, unit)\n')
EG_NEW = EG_OLD + ('\t\telseif eg_mode_now == "shot" then\n'
                   '\t\t\t-- ROUND 156: the magic missiles - the map is rebuilt; the target must still qualify and be safe\n'
                   '\t\t\tcond_now = FOURTH.shot_still_ok(enemy, unit)\n')

HELPERS = r'''-- ============================================================================
-- ROUND 156 - THE MAGIC MISSILES (open batch 4, user rulings 2026-11-15).
--   enemy_large_shot ("Large first, then armour"; Blast, Damned Pistol, Hunting
--     Spear, Master Rune of Flight, Schalkain's Teeth): the visible LARGE enemy
--     in range with the highest live value (strategic_value); when none
--     qualifies, the visible enemy infantry with the highest armour (the
--     GENERATED UNIT_DEF table; an unknown armour never qualifies; ties: the
--     higher value per soldier). Caster out of melee.
--   enemy_single_shot ("Most valuable single"; Dead Eye, Focused Shot): the
--     single-entity enemy (lords, heroes, single monsters) in range with the
--     highest live value; a shot whose projectile has more bonus against large
--     than against infantry (Focused Shot) takes a LARGE one first. Caster
--     standing still (5 s wind-up) and out of melee.
--   enemy_infantry_shot ("Most valuable infantry"; Bolt Storm): the visible
--     enemy infantry (10+ men, not flying) in range with the highest live value
--     per soldier. Caster standing still and out of melee.
--   Every map target is SAFE: none of our units' rectangles within SHOT_SAFE_M
--     of its rectangle (the shots can hit our own units: can_damage_allies).
--   enemy_melee_or_fast ("Split by effect"; Crippling Throw, the Golden
--     Blowpipe: they slow the target, rule 10): the closest enemy in range that
--     is fighting in melee, else a fast enemy closing on our units.
--   enemy_melee_or_shooting (Spear of Kurnous: blinded, accuracy and melee
--     stats): the closest enemy in melee, else the closest shooting enemy
--     missile unit.
--   The game's own engaged_in_melee usage rule and min_range come from the
--   GENERATED SHOT table. The pick is re-checked before the cast.
-- ============================================================================
FOURTH.SHOT_SAFE_M = 10   -- user ruling 2026-11-15: none of our units within 10 m of the target (not a range constant)
FOURTH.shot_kind = nil
FOURTH.shot_still_needed = nil
''' + "%SHOT_BLOCK%" + r'''
-- the current entry's SHOT row { no_melee, prefer_large, min_range } (nil when it has none)
function FOURTH.shot_info()
	local key = FOURTH.rc_self_keys and FOURTH.rc_self_keys[1]
	return key and FOURTH.SHOT[key]
end

-- the caster may cast: out of melee (an exact false), and standing still when the family needs it
function FOURTH.shot_caster_ok(unit, still)
	local ok, mel = pcall(function() return unit:is_in_melee() end)
	if not (ok and mel == false) then return false end
	if still and not FOURTH.blob_still(unit) then return false end
	return true
end

-- the game's min_range: an enemy closer than it cannot be targeted (an unreadable distance fails)
function FOURTH.shot_min_ok(unit, enemy)
	local info = FOURTH.shot_info()
	if info == nil or info[3] <= 0 then return true end
	local gap = FOURTH.eg_enemy_gap(unit, enemy)
	return gap ~= nil and gap >= info[3]
end

-- a map candidate: the entry's class, in the bound, past the minimum range, and safe
function FOURTH.shot_cand_ok(unit, e, m)
	if not (FOURTH.eg_class_ok(e.unit) and FOURTH.eg_enemy_within_bound(unit, e.unit)
		and FOURTH.shot_min_ok(unit, e.unit)) then
		return false
	end
	local g = FOURTH.blob_friend_gap(e, m, FOURTH.SHOT_SAFE_M)
	return g == nil or g > FOURTH.SHOT_SAFE_M
end

-- the best map target of one kind ("large", "armour", "single", "infantry"); large_only limits "single" to large
-- units. Returns the shape and its score (value, armour or value per soldier).
function FOURTH.shot_pick(unit, m, kind, large_only)
	local list = m.all
	if kind == "armour" or kind == "infantry" then list = m.enemies end
	local best, bs, bs2 = nil, nil, nil
	for i = 1, #list do
		local e = list[i]
		local ok_kind, s1, s2 = true, 0, 0
		if kind == "large" then
			ok_kind = (e.t ~= nil and FOURTH.class_keys.large[e.t] == true)
			s1 = e.value or 0
		elseif kind == "single" then
			ok_kind = (e.t ~= nil and FOURTH.class_keys.single[e.t] == true)
				and (not large_only or FOURTH.class_keys.large[e.t] == true)
			s1 = e.value or 0
		elseif kind == "armour" then
			local def = e.t and FOURTH.UNIT_DEF[e.t]
			ok_kind = (def ~= nil)
			s1 = def and def[1] or 0
			s2 = e.vps or 0
		else
			s1 = e.vps or 0
		end
		if ok_kind and FOURTH.shot_cand_ok(unit, e, m) then
			if best == nil or s1 > bs or (s1 == bs and s2 > bs2) then best, bs, bs2 = e, s1, s2 end
		end
	end
	return best, bs
end

-- the chosen map target becomes the cast target (the pre-cast re-check reads shot_kind / shot_still_needed)
function FOURTH.shot_take(unit, e, kind, still)
	FOURTH.shot_kind = kind
	FOURTH.shot_still_needed = still
	FOURTH.eg_enemy = e.unit
	FOURTH.eg_arm = "shot"
	FOURTH.eg_caster_su = FOURTH.eg_fresh_caster_su(unit)
	FOURTH.cast_target = e.unit
end

-- the pre-cast re-check: the caster still may cast, and the chosen enemy is still a safe target of the same kind
function FOURTH.shot_still_ok(enemy, unit)
	local kind = FOURTH.shot_kind
	if kind == nil then return false end
	if not FOURTH.shot_caster_ok(unit, FOURTH.shot_still_needed) then return false end
	local m = FOURTH.blob_map(true)
	local id = nil
	pcall(function() id = tostring(enemy:unique_ui_id()) end)
	if id == nil then return false end
	local list = m.all
	if kind == "armour" or kind == "infantry" then list = m.enemies end
	for i = 1, #list do
		local e = list[i]
		local eid = nil
		pcall(function() eid = tostring(e.unit:unique_ui_id()) end)
		if eid == id then
			if kind == "large" and not (e.t ~= nil and FOURTH.class_keys.large[e.t] == true) then return false end
			if kind == "single" and not (e.t ~= nil and FOURTH.class_keys.single[e.t] == true) then return false end
			if kind == "armour" and not (e.t ~= nil and FOURTH.UNIT_DEF[e.t] ~= nil) then return false end
			return FOURTH.shot_cand_ok(unit, e, m)
		end
	end
	return false
end

-- the game's engaged_in_melee usage rule for the throws (the caster must be out of melee)
function FOURTH.shot_usage_ok(unit)
	local info = FOURTH.shot_info()
	if info == nil or info[1] ~= 1 then return true end
	local ok, mel = pcall(function() return unit:is_in_melee() end)
	return ok and mel == false
end

-- clear a pick a later arm overrides
function FOURTH.shot_clear()
	FOURTH.eg_enemy, FOURTH.eg_arm, FOURTH.eg_caster_su, FOURTH.cast_target = nil, nil, nil, nil
end

'''

LIVE_REASON = r'''-- the ATTEMPT reason for a map pick
function FOURTH.shot_reason(unit, e, what, score)
	local etype = "enemy"
	pcall(function() etype = tostring(e.unit:type()) end)
	local d = FOURTH.eg_enemy_gap(unit, e.unit)
	return string.format("%s (targeting %s, %s); none of ours within %dm; distance %sm bound %sm", what, etype, score,
		FOURTH.SHOT_SAFE_M, (d ~= nil) and string.format("%.1f", d) or "?", tostring(FOURTH.eg_range_m))
end

'''

EVALS = r'''function FOURTH.evaluate_enemy_large_shot(unit, routing)
	FOURTH.eg_mode = "shot"
	FOURTH.shot_kind = nil
	if routing or not FOURTH.shot_caster_ok(unit, false) then return %NO% end
	local m = FOURTH.blob_map(false)
	local e, s = FOURTH.shot_pick(unit, m, "large", false)
	local kind = "large"
	if e == nil then
		e, s = FOURTH.shot_pick(unit, m, "armour", false)
		kind = "armour"
	end
	if e == nil then return %NO% end
	FOURTH.shot_take(unit, e, kind, false)
	%RET_LARGE%
end

function FOURTH.evaluate_enemy_single_shot(unit, routing)
	FOURTH.eg_mode = "shot"
	FOURTH.shot_kind = nil
	if routing or not FOURTH.shot_caster_ok(unit, true) then return %NO% end
	local m = FOURTH.blob_map(false)
	local info = FOURTH.shot_info()
	local e, s = nil, nil
	if info ~= nil and info[2] == 1 then e, s = FOURTH.shot_pick(unit, m, "single", true) end
	if e == nil then e, s = FOURTH.shot_pick(unit, m, "single", false) end
	if e == nil then return %NO% end
	FOURTH.shot_take(unit, e, "single", true)
	%RET_SINGLE%
end

function FOURTH.evaluate_enemy_infantry_shot(unit, routing)
	FOURTH.eg_mode = "shot"
	FOURTH.shot_kind = nil
	if routing or not FOURTH.shot_caster_ok(unit, true) then return %NO% end
	local m = FOURTH.blob_map(false)
	local e, s = FOURTH.shot_pick(unit, m, "infantry", false)
	if e == nil then return %NO% end
	FOURTH.shot_take(unit, e, "infantry", true)
	%RET_INF%
end

-- Crippling Throw and the Golden Blowpipe: the closest enemy in melee, else a fast enemy closing on our units
function FOURTH.evaluate_enemy_melee_or_fast(unit, routing)
	if routing or not FOURTH.shot_usage_ok(unit) then return %NO% end
	local r = FOURTH.evaluate_enemy_melee(unit, routing)
	if r and FOURTH.shot_min_ok(unit, FOURTH.eg_enemy) then return r end
	FOURTH.shot_clear()
	FOURTH.eg_melee_only = nil
	r = FOURTH.evaluate_enemy_fast_near_ally(unit, routing)
	if r and FOURTH.shot_min_ok(unit, FOURTH.eg_enemy) then return r end
	FOURTH.shot_clear()
	return %NO%
end

-- Spear of Kurnous: the closest enemy in melee, else the closest shooting enemy missile unit
function FOURTH.evaluate_enemy_melee_or_shooting(unit, routing)
	if routing or not FOURTH.shot_usage_ok(unit) then return %NO% end
	local r = FOURTH.evaluate_enemy_melee(unit, routing)
	if r and FOURTH.shot_min_ok(unit, FOURTH.eg_enemy) then return r end
	FOURTH.shot_clear()
	FOURTH.eg_melee_only = nil
	r = FOURTH.evaluate_enemy_missile_shooting(unit, routing)
	if r and FOURTH.shot_min_ok(unit, FOURTH.eg_enemy) then return r end
	FOURTH.shot_clear()
	return %NO%
end

'''
LIVE_RET = {
    "%NO%": "nil",
    "%RET_LARGE%": ('if kind == "large" then\n'
                    '\t\treturn FOURTH.shot_reason(unit, e, "most valuable large enemy", string.format("value %.0f", s))\n'
                    '\tend\n'
                    '\treturn FOURTH.shot_reason(unit, e, "no large target: most armoured enemy infantry",\n'
                    '\t\tstring.format("armour %.0f", s))'),
    "%RET_SINGLE%": ('return FOURTH.shot_reason(unit, e, "most valuable single-entity enemy, standing still",\n'
                     '\t\tstring.format("value %.0f", s))'),
    "%RET_INF%": ('return FOURTH.shot_reason(unit, e, "most valuable enemy infantry, standing still",\n'
                  '\t\tstring.format("value %.1f per soldier", s))'),
}
ANN_RET = {"%NO%": "false", "%RET_LARGE%": "return true", "%RET_SINGLE%": "return true", "%RET_INF%": "return true"}


def render(tpl, rep):
    for k, v in rep.items():
        tpl = tpl.replace(k, v)
    assert "%" not in re.sub(r'string\.format\("[^"]*"', "", tpl).replace("%d", "").replace("%s", ""), "placeholder left"
    return tpl


FAMS = ["enemy_large_shot", "enemy_single_shot", "enemy_infantry_shot", "enemy_melee_or_fast", "enemy_melee_or_shooting"]
MAP_OLD = "\tenemy_ground_shooting = FOURTH.evaluate_enemy_ground_shooting,\n"
MAP_NEW = MAP_OLD + "\t-- ROUND 156\n" + "".join("\t%s = FOURTH.evaluate_%s,\n" % (f, f) for f in FAMS)
TIP_OLD = ('\tenemy_ground_shooting = "When armed, fires on the ground under the closest enemy missile unit in range that '
           'is shooting",\n')
TIP_NEW = TIP_OLD + (
    '\tenemy_large_shot = "When armed, fires on the most valuable large enemy in range with none of yours near it, '
    'otherwise on the most armoured enemy infantry",\n'
    '\tenemy_single_shot = "When armed and standing still, fires on the most valuable single-entity enemy in range '
    '(lord, hero or monster) with none of yours near it",\n'
    '\tenemy_infantry_shot = "When armed and standing still, fires on the enemy infantry in range worth the most per '
    'soldier, with none of yours near it",\n'
    '\tenemy_melee_or_fast = "When armed, fires on the closest enemy in range that is fighting in melee, otherwise on a '
    'fast enemy closing on your units",\n'
    '\tenemy_melee_or_shooting = "When armed, fires on the closest enemy in range that is fighting in melee, otherwise on '
    'the closest enemy missile unit that is shooting",\n')
ANCHOR = "FOURTH.evaluators = {\n"

shot_block = GS.lua_block(GS.derive(KEYS))
helpers = HELPERS.replace("%SHOT_BLOCK%", shot_block)
EV_LIVE = helpers + LIVE_REASON + render(EVALS, LIVE_RET)
EV_ANN = helpers + render(EVALS, ANN_RET)

for path, ev in ((SRC, EV_LIVE), (ANN, EV_ANN)):
    s = open(path, encoding="utf-8", newline="").read()
    assert "evaluate_enemy_large_shot" not in s and "FOURTH.SHOT " not in s and "FOURTH.SHOT_TEXT" not in s
    before = s.count("\t{ marker = ")
    s = sub(s, RESTOCK, NEW_ENTRIES + RESTOCK)
    s = sub(s, WIND_OLD, WIND_NEW)
    s = sub(s, HOLD_OLD, HOLD_NEW)
    s = sub(s, R120_OLD, R120_NEW)
    s = sub(s, MAP120_OLD, MAP120_NEW)
    s = sub(s, CLASS_OLD, CLASS_NEW)
    s = sub(s, SHAPE_OLD, SHAPE_NEW)
    s = sub(s, MAPT_OLD, MAPT_NEW)
    s = sub(s, MAPA_OLD, MAPA_NEW)
    s = sub(s, EG_OLD, EG_NEW)
    s = sub(s, MAP_OLD, MAP_NEW)
    s = sub(s, TIP_OLD, TIP_NEW)
    s = sub(s, ANCHOR, ev + ANCHOR)
    assert s.count("\t{ marker = ") == before + 11
    assert "string.find" not in ev + NEW_ENTRIES
    assert "\u2014" not in ev + NEW_ENTRIES
    open(path, "w", encoding="utf-8", newline="").write(s)
    print(path, "entries", before, "->", before + 11)

src_now = open(SRC, encoding="utf-8").read()
assert GS.keys_in(src_now) == sorted(KEYS), GS.keys_in(src_now)

import gen_recharge_keys as G  # noqa: E402
new_block = G.lua_block(G.derive())
pat = re.compile(r"-- GENERATED by tools/gen_recharge_keys\.py.*?\nFOURTH\.load_recharge\(\)\n", re.S)
for path in (SRC, ANN):
    s = open(path, encoding="utf-8", newline="").read()
    assert len(pat.findall(s)) == 1
    s = pat.sub(lambda m: new_block, s)
    open(path, "w", encoding="utf-8", newline="").write(s)
print("lock table re-derived:", len(G.derive()), "keys")
