#!/usr/bin/env python3
"""Round 164 (harness 163): the friendly-fire breaths (28 entries / 28 keys; 3 new families), user rulings 2026-11-16.
Earlier status: "excluded (auto: breath / cone damage (friendly fire, family decision 2026-10-09))", a RULE.

  * 18 target-launched breaths: "Wave rule" -> enemy_wave.
  * Tidecall, Wind Blast (their slows, rule 10): "Charge, clear path" -> NEW enemy_wave_charge: a fast enemy closing on
    our units, the caster standing, the wave's path from the caster through that enemy clear of ours.
  * 5 breaths from the caster's front (Fishy Breath, Pestilent Breath x2, Shatter, Skabscrath): "Clear cone, most value"
    -> NEW enemy_cone: a standing enemy in range; the zone from the caster through it to offset + path holds none of our
    other units (radius + 10 m wide); the most enemy value in it.
  * Disembowelling Sweep, Flesh-eating Scarabs: "Sweeps clear" -> NEW enemy_sweep: the caster in melee and not wavering,
    none of our other units within the sweep's reach + 10 m of the caster, cast at the closest enemy in melee in range.
  * Da Boss' Loons: "Loons as wanderer" -> enemy_wander kind 6 (released at the caster: the ring is the caster's).
  * "Caster doesn't count": a caster's own wave never blocks its cast (round 162's waves included).
  * The game's engaged_in_melee usage rule (Blue Fire of Chaos): the WW families' caster gate (GENERATED WW_NOMELEE).
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_ww_tables as GW  # noqa: E402
import gamedata_paths as GP  # noqa: E402

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"
WV, CH, CN, SW, WN = "enemy_wave", "enemy_wave_charge", "enemy_cone", "enemy_sweep", "enemy_wander"
ROWS = [
    ("bangstick", "Bangstick", WV, "wh3_main_item_abilities_bangstick"),
    ("black_dragon_egg", "Black Dragon Egg", WV, "wh2_main_item_abilities_black_dragon_egg"),
    ("blue_fire", "Blue Fire of Chaos", WV, "wh3_main_daemon_arms_abilities_blue_fire"),
    ("blue_fire_upgraded", "Blue Fire of Chaos Upgraded", WV, "wh3_main_daemon_arms_abilities_blue_fire_upgraded"),
    ("fiery_ring_of_thori", "Fiery Ring of Thori", WV, "wh_main_item_abilities_fiery_ring_of_thori"),
    ("gaze_of_malice", "Gaze of Malice", WV, "wh2_main_lord_abilities_gaze_of_malice"),
    ("jade_lions_breath", "Jade Lion's Breath", WV, "wh3_dlc24_unit_abilities_jade_dragons_breath"),
    ("kovsh_breath", "Kovsh Breath", WV, "wh3_main_item_abilities_kovsh_breath"),
    ("lash_of_slaanesh_dlc27", "Lash of Slaanesh", WV, "wh3_dlc27_spell_bound_lash_of_slaanesh"),
    ("lash_of_slaanesh", "Lash of Slaanesh", WV, "wh3_main_spell_bound_lash_of_slaanesh"),
    ("lash_of_slaanesh_keeper", "Lash of Slaanesh", WV, "wh3_main_spell_bound_lash_of_slaanesh_keeper_of_secrets"),
    ("pink_fire_dlc20", "Pink Fire of Tzeentch", WV, "wh3_dlc20_spell_bound_pink_fire_of_tzeentch"),
    ("pink_fire", "Pink Fire of Tzeentch", WV, "wh3_main_spell_tzeentch_pink_fire_of_tzeentch_bound"),
    ("scorch", "Scorch", WV, "wh2_main_mount_bound_scorch"),
    ("stream_of_corruption_dlc20", "Stream of Corruption", WV, "wh3_dlc20_spell_bound_stream_of_corruption"),
    ("stream_of_corruption", "Stream of Corruption", WV, "wh3_main_spell_nurgle_stream_of_corruption_bound"),
    ("sunfang", "Sunfang", WV, "wh2_main_weapon_abilities_sunfang"),
    ("spear_slaupnir", "The Spear Slaupnir", WV, "wh3_dlc20_weapon_abilities_the_spear_slaupnir"),
    ("tidecall", "Tidecall", CH, "wh2_dlc11_spell_bound_tidecall"),
    ("wind_blast", "Wind Blast", CH, "wh2_dlc11_spell_bound_wind_blast"),
    ("fishy_breath", "Fishy Breath", CN, "wh2_dlc15_character_abilities_fishy_breathe"),
    ("pestilent_breath_mount", "Pestilent Breath", CN, "wh2_main_mount_bound_pestilent_breath"),
    ("pestilent_breath", "Pestilent Breath", CN, "wh3_main_spell_bound_pestilent_breath"),
    ("shatter", "Shatter", CN, "wh2_dlc13_character_ability_shatter"),
    ("skabscrath", "Skabscrath", CN, "wh_main_weapon_abilities_skabscrath"),
    ("disembowelling_sweep", "Disembowelling Sweep", SW, "wh3_dlc29_unit_active_ripping_blades"),
    ("flesh_eating_scarabs", "Flesh-eating Scarabs", SW, "wh3_dlc29_unit_abilities_flesh_eating_scarabs"),
    ("da_boss_loons", "Da Boss' Loons", WN, "wh2_dlc15_lord_abilities_da_boss_loons"),
]
assert len(ROWS) == 28 and len(set(r[0] for r in ROWS)) == 28 and len(set(r[3] for r in ROWS)) == 28


def tsv(n):
    f = open(os.path.join(GP.GAMEDATA, n), encoding="utf-8-sig")
    h = f.readline().rstrip("\n").split("\t")
    f.readline()
    return [dict(zip(h, l.rstrip("\n").split("\t"))) for l in f]


USA = {r["key"]: r for r in tsv("unit_spec_abil.tsv")}
INV = {}
for r in tsv("special_ability_to_invalid_target_flags_tables.tsv"):
    INV.setdefault(r["special_ability"], set()).add(r["invalid_target"])


def num(v):
    f = float(v)
    return str(int(f)) if f == int(f) else ("%.3f" % f).rstrip("0").rstrip(".")


def entry(marker, name, trig, key):
    rng = float(USA[key]["target_intercept_range"])
    assert rng > 0, key
    lines = ['\t{ marker = "%s", name = "%s", trigger = "%s",' % (marker, name, trig),
             '\t\tbadge = "zz_auto_badge_%s",' % marker,
             '\t\tkeys = { "%s" },' % key,
             '\t\trange_real = %s,' % num(rng)]
    if "flying_currently" in INV.get(key, set()):
        lines.append('\t\ttarget_class = "not_flying",')
    lines.append("\t\tox = 0, oy = 0 },")
    return "\n".join(lines) + "\n"


NEW_ENTRIES = "".join(entry(*r) for r in ROWS)
KEYS = [r[3] for r in ROWS]
HOLD = [(k, num(USA[k]["recharge_time"])) for k in KEYS if int(float(USA[k]["num_uses"])) > 1]
WIND = [(k, num(USA[k]["wind_up_time"])) for k in KEYS if float(USA[k]["wind_up_time"]) > 0]
NF = sum(1 for k in KEYS if "flying_currently" in INV.get(k, set()))
print("multi-use:", len(HOLD), "wind-up:", len(WIND), "not_flying classes:", NF, "range_real:", len(KEYS))


def between(s, head, tail):
    i = s.index(head)
    j = s.index(tail, i)
    return s[i:j]


RESTOCK = '\t{ marker = "restock", name = "Restock!", trigger = "ally_ammo_low",'
WIND_OLD = "\twind_up_s = {\n"
WIND_NEW = WIND_OLD + "\t\t-- ROUND 164: the breaths' wind-ups (unit_spec_abil wind_up_time)\n" + "".join(
    '\t\t["%s"] = %s,\n' % (k, v) for k, v in WIND)
HOLD_OLD = "\thold_s = {\n"
HOLD_NEW = HOLD_OLD + "\t\t-- ROUND 164: the breaths with more than one use (recharge_time)\n" + "".join(
    '\t\t["%s"] = %s,\n' % (k, v) for k, v in HOLD)

WAVE_VALUE_NEW = r'''function FOURTH.ww_wave_value(unit, e, m, row, moving_ok)
	-- ROUND 164: moving_ok = the charge arm (Tidecall, Wind Blast: the target is a charging enemy)
	if not (FOURTH.eg_class_ok(e.unit) and FOURTH.eg_enemy_within_bound(unit, e.unit)
		and (moving_ok or FOURTH.ww_target_still(e))) then
		return nil
	end
	local sx, sz, ex, ez = FOURTH.ww_wave_line(unit, e, row)
	if sx == nil then return nil end
	if row.allies then
		-- the drift grows from 0 at the start to the 95% value at the end (it grows slower than a straight line, so
		-- this cone is on the safe side): the margin for a unit is taken at its farthest point along the path.
		-- ROUND 164 (user ruling 2026-11-16, "Caster doesn't count"): the caster's own wave never blocks it
		local l2 = (ex - sx) ^ 2 + (ez - sz) ^ 2
		local self_id = nil
		pcall(function() self_id = tostring(unit:unique_ui_id()) end)
		for i = 1, #m.ours do
			local o = m.ours[i]
			local oid = nil
			pcall(function() oid = tostring(o.unit:unique_ui_id()) end)
			if oid == nil or oid ~= self_id then
				local tmax = 0
				if l2 > 0 then
					for k = 1, #o.pts do
						local t = ((o.pts[k][1] - sx) * (ex - sx) + (o.pts[k][2] - sz) * (ez - sz)) / l2
						if t > tmax then tmax = t end
					end
				end
				local need = row.r + FOURTH.SHOT_SAFE_M + row.buf * math.min(1, tmax)
				if FOURTH.ww_pt_seg(o.x, o.z, sx, sz, ex, ez) - o.half <= need
					and FOURTH.ww_seg_rect_gap(sx, sz, ex, ez, o) <= need then
					return nil
				end
			end
		end
	end
	return FOURTH.ww_path_value(m, row, sx, sz, ex, ez)
end

-- ROUND 164: the enemy value a path touches (every visible enemy within the radius of the segment)
function FOURTH.ww_path_value(m, row, sx, sz, ex, ez)
	local v = 0
	for i = 1, #m.all do
		local o = m.all[i]
		if FOURTH.ww_pt_seg(o.x, o.z, sx, sz, ex, ez) - o.half <= row.r
			and FOURTH.ww_seg_rect_gap(sx, sz, ex, ez, o) <= row.r then
			v = v + (o.value or 0)
		end
	end
	return v
end

'''
WANDER_SAFE_OLD = ('\tif row.allies then\n'
                   '\t\tlocal need = row.r + row.buf + FOURTH.SHOT_SAFE_M\n'
                   '\t\tif row.kind == 3 then need = need + (e.half or 0) end\n'
                   '\t\tfor i = 1, #m.ours do\n'
                   '\t\t\tif FOURTH.blob_rect_gap(e.x, e.z, m.ours[i]) <= need then return nil end\n'
                   '\t\tend\n'
                   '\tend\n')
WANDER_SAFE_NEW = ('\tif row.allies and row.kind == 6 then\n'
                   '\t\t-- ROUND 164: released at the caster (Da Boss\' Loons): none of our OTHER units within radius + reach\n'
                   '\t\t-- + SHOT_SAFE_M of the caster\n'
                   '\t\tif not FOURTH.self_clear(unit, row.r + row.buf) then return nil end\n'
                   '\telseif row.allies then\n'
                   '\t\tlocal need = row.r + row.buf + FOURTH.SHOT_SAFE_M\n'
                   '\t\tif row.kind == 3 then need = need + (e.half or 0) end\n'
                   '\t\tfor i = 1, #m.ours do\n'
                   '\t\t\tif FOURTH.blob_rect_gap(e.x, e.z, m.ours[i]) <= need then return nil end\n'
                   '\t\tend\n'
                   '\tend\n')
STILL_NEW = r'''function FOURTH.ww_still_ok(enemy, unit)
	local row = FOURTH.ww_row()
	if row == nil then return false end
	-- ROUND 164: a sweep needs its caster in melee and still clear; every other kind its caster standing (and out of
	-- melee when the game says so)
	if row.kind == 7 then
		if not FOURTH.evaluate_in_melee_self(unit, false) then return false end
		if not FOURTH.self_clear(unit, row.r) then return false end
	elseif not FOURTH.ww_caster_ok(unit) then
		return false
	end
	local m = FOURTH.blob_map(true)
	local id = nil
	pcall(function() id = tostring(enemy:unique_ui_id()) end)
	if id == nil then return false end
	local list = (row.kind == 2 or row.kind == 3 or row.kind == 6) and m.enemies or m.all
	for i = 1, #list do
		local e = list[i]
		local eid = nil
		pcall(function() eid = tostring(e.unit:unique_ui_id()) end)
		if eid == id then
			if row.kind == 1 then
				if FOURTH.ww_charge == true and FOURTH.fast_enemy_near(e.unit, unit) == nil then return false end
				return FOURTH.ww_wave_value(unit, e, m, row, FOURTH.ww_charge == true) ~= nil
			end
			if row.kind == 4 then return FOURTH.ww_strike_value(unit, e, m, row) ~= nil end   -- ROUND 163
			if row.kind == 5 then return FOURTH.ww_cone_value(unit, e, m, row) ~= nil end   -- ROUND 164
			if row.kind == 7 then return FOURTH.ww_sweep_ok(unit, e) end   -- ROUND 164
			return FOURTH.ww_wander_value(unit, e, m, row) ~= nil
		end
	end
	return false
end

'''
GUARDS = [
    ("\tFOURTH.eg_mode = \"ww\"\n\tlocal row = FOURTH.ww_row()\n"
     "\tif routing or row == nil or row.kind ~= 1 or not FOURTH.blob_still(unit) then return %NO% end\n",
     "\tFOURTH.eg_mode = \"ww\"\n\tFOURTH.ww_charge = false   -- ROUND 164\n\tlocal row = FOURTH.ww_row()\n"
     "\tif routing or row == nil or row.kind ~= 1 or not FOURTH.ww_caster_ok(unit) then return %NO% end\n"),
    ("\tif routing or row == nil or row.kind == 1 or row.kind == 4 or not FOURTH.blob_still(unit) then return %NO% end\n",
     "\tif routing or row == nil or (row.kind ~= 2 and row.kind ~= 3 and row.kind ~= 6) or not FOURTH.ww_caster_ok(unit) then\n"
     "\t\treturn %NO%\n\tend\n"),
    ("\tif routing or row == nil or row.kind ~= 4 or not FOURTH.blob_still(unit) then return %NO% end\n",
     "\tif routing or row == nil or row.kind ~= 4 or not FOURTH.ww_caster_ok(unit) then return %NO% end\n"),
]

EVALS = r'''-- ============================================================================
-- ROUND 164 - THE FRIENDLY-FIRE BREATHS (user rulings 2026-11-16; earlier a 2026-10-09 family RULE).
--   The 18 target-launched breaths ride enemy_wave. "Caster doesn't count": a
--   caster's own wave never blocks its cast. The game's engaged_in_melee usage
--   rule (GENERATED WW_NOMELEE: Blue Fire of Chaos) joins the caster gate.
--   enemy_wave_charge (Tidecall, Wind Blast: slows, rule 10): a FAST enemy
--     closing on our units, the caster standing, the wave's path from the caster
--     through it clear of ours; the most enemy value on the path.
--   enemy_cone (breaths from the caster's front): a standing enemy in range; the
--     zone from the caster through it, offset + path long, radius + 10 m wide,
--     holds none of our OTHER units; the most enemy value in it.
--   enemy_sweep (Disembowelling Sweep, Flesh-eating Scarabs): the caster in melee
--     and not wavering, none of our OTHER units within the sweep's reach + 10 m;
--     the closest enemy in range that is fighting in melee.
--   enemy_wander kind 6 (Da Boss' Loons): the safety ring is around the caster.
-- ============================================================================
-- the WW caster gate: standing still, and out of melee when the game refuses the cast in melee
function FOURTH.ww_caster_ok(unit)
	if not FOURTH.blob_still(unit) then return false end
	local key = FOURTH.rc_self_keys and FOURTH.rc_self_keys[1]
	if key ~= nil and FOURTH.WW_NOMELEE[key] == true then
		local ok, mel = pcall(function() return unit:is_in_melee() end)
		if not (ok and mel == false) then return false end
	end
	return true
end

-- a cone candidate: the enemy value in the zone from the caster through e, or nil when not allowed or not safe
function FOURTH.ww_cone_value(unit, e, m, row)
	if not (FOURTH.eg_class_ok(e.unit) and FOURTH.eg_enemy_within_bound(unit, e.unit) and FOURTH.ww_target_still(e)) then
		return nil
	end
	local cx, cz = FOURTH.self_xz(unit)
	if cx == nil then return nil end
	local dx, dz = e.x - cx, e.z - cz
	local len = math.sqrt(dx * dx + dz * dz)
	if len < 0.5 then return nil end
	local L = row.off + row.path
	local ex, ez = cx + dx / len * L, cz + dz / len * L
	if row.allies then
		local need = row.r + row.buf + FOURTH.SHOT_SAFE_M
		local self_id = nil
		pcall(function() self_id = tostring(unit:unique_ui_id()) end)
		for i = 1, #m.ours do
			local o = m.ours[i]
			local oid = nil
			pcall(function() oid = tostring(o.unit:unique_ui_id()) end)
			if (oid == nil or oid ~= self_id) and FOURTH.ww_pt_seg(o.x, o.z, cx, cz, ex, ez) - o.half <= need
				and FOURTH.ww_seg_rect_gap(cx, cz, ex, ez, o) <= need then
				return nil
			end
		end
	end
	return FOURTH.ww_path_value(m, row, cx, cz, ex, ez)
end

-- a sweep target: allowed, in range and fighting in melee (an exact true)
function FOURTH.ww_sweep_ok(unit, e)
	if not (FOURTH.eg_class_ok(e.unit) and FOURTH.eg_enemy_within_bound(unit, e.unit)) then return false end
	local ok, mel = pcall(function() return e.unit:is_in_melee() end)
	return ok and mel == true
end

function FOURTH.evaluate_enemy_wave_charge(unit, routing)
	FOURTH.eg_mode = "ww"
	FOURTH.ww_charge = true
	local row = FOURTH.ww_row()
	if routing or row == nil or row.kind ~= 1 or not FOURTH.ww_caster_ok(unit) then return %NO% end
	local m = FOURTH.blob_map(false)
	local best, bv, bsp = nil, nil, nil
	for i = 1, #m.all do
		local e = m.all[i]
		local gap, sp = FOURTH.fast_enemy_near(e.unit, unit)
		if gap ~= nil then
			local v = FOURTH.ww_wave_value(unit, e, m, row, true)
			if v ~= nil and (bv == nil or v > bv) then best, bv, bsp = e, v, sp end
		end
	end
	if best == nil then return %NO% end
	FOURTH.ww_take(unit, best, row)
	%RET_CHARGE%
end

function FOURTH.evaluate_enemy_cone(unit, routing)
	FOURTH.eg_mode = "ww"
	local row = FOURTH.ww_row()
	if routing or row == nil or row.kind ~= 5 or not FOURTH.ww_caster_ok(unit) then return %NO% end
	local m = FOURTH.blob_map(false)
	local best, bv = nil, nil
	for i = 1, #m.all do
		local e = m.all[i]
		local v = FOURTH.ww_cone_value(unit, e, m, row)
		if v ~= nil and (bv == nil or v > bv) then best, bv = e, v end
	end
	if best == nil then return %NO% end
	FOURTH.ww_take(unit, best, row)
	%RET_CONE%
end

function FOURTH.evaluate_enemy_sweep(unit, routing)
	FOURTH.eg_mode = "ww"
	local row = FOURTH.ww_row()
	if routing or row == nil or row.kind ~= 7 then return %NO% end
	if not FOURTH.evaluate_in_melee_self(unit, routing) then return %NO% end
	local ok, txt = FOURTH.self_clear(unit, row.r)
	if not ok then return %NO% end
	local m = FOURTH.blob_map(false)
	local best, bg = nil, nil
	for i = 1, #m.all do
		local e = m.all[i]
		if FOURTH.ww_sweep_ok(unit, e) then
			local g = FOURTH.eg_enemy_gap(unit, e.unit)
			if g ~= nil and (bg == nil or g < bg) then best, bg = e, g end
		end
	end
	if best == nil then return %NO% end
	FOURTH.ww_take(unit, best, row)
	%RET_SWEEP%
end

'''
LIVE_RET = {
    "%NO%": "nil",
    "%RET_CHARGE%": ('local etype = "enemy"\n'
                     '\tpcall(function() etype = tostring(best.unit:type()) end)\n'
                     '\treturn string.format("charging enemy (targeting %s, %.1f m/s): value on the %sm wave path %.0f; none of our "\n'
                     '\t\t.. "other units within %sm of it; bound %sm", etype, bsp or 0, tostring(row.path), bv,\n'
                     '\t\ttostring(row.r + FOURTH.SHOT_SAFE_M), tostring(FOURTH.eg_range_m))'),
    "%RET_CONE%": ('local etype = "enemy"\n'
                   '\tpcall(function() etype = tostring(best.unit:type()) end)\n'
                   '\treturn string.format("breath from the caster (targeting %s, standing): value in the %sm cone %.0f; none of "\n'
                   '\t\t.. "our other units within %sm of it; bound %sm", etype, tostring(row.off + row.path), bv,\n'
                   '\t\ttostring(row.r + row.buf + FOURTH.SHOT_SAFE_M), tostring(FOURTH.eg_range_m))'),
    "%RET_SWEEP%": ('local etype = "enemy"\n'
                    '\tpcall(function() etype = tostring(best.unit:type()) end)\n'
                    '\treturn string.format("melee sweep at the closest enemy in melee (%s, %.1fm); ", etype, bg) .. txt'),
}
ANN_RET = {"%NO%": "false", "%RET_CHARGE%": "return true", "%RET_CONE%": "return true", "%RET_SWEEP%": "return true"}


def render(tpl, rep):
    for k, v in rep.items():
        tpl = tpl.replace(k, v)
    assert "%NO%" not in tpl and "%RET_" not in tpl
    return tpl


FAMS = ["enemy_wave_charge", "enemy_cone", "enemy_sweep"]
MAP_OLD = "\tally_blast = FOURTH.evaluate_ally_blast,\n"
MAP_NEW = MAP_OLD + "\t-- ROUND 164\n" + "".join("\t%s = FOURTH.evaluate_%s,\n" % (f, f) for f in FAMS)
TIP_ANCHOR = '\tally_blast = "When armed, fires on the friendly unit (or itself) with the most enemy value around it",\n'
TIP_NEW = TIP_ANCHOR + (
    '\tenemy_wave_charge = "When armed and standing still, fires its wave at a charging enemy whose path holds none of our '
    'units",\n'
    '\tenemy_cone = "When armed and standing still, breathes at a standing enemy when the cone holds the most enemy value '
    'and none of our other units",\n'
    '\tenemy_sweep = "When armed, sweeps the closest enemy in melee when none of our other units are within its reach",\n')
ANCHOR = "FOURTH.evaluators = {\n"
WW_GEN = re.compile(r"-- GENERATED by tools/gen_ww_tables\.py from unit_spec_abil.*?\nFOURTH\.load_ww_table\(\)\n", re.S)

for path, live in ((SRC, True), (ANN, False)):
    s = open(path, encoding="utf-8", newline="").read()
    assert "function FOURTH.evaluate_enemy_cone(" not in s and "WW_NOMELEE" not in s
    for r in ROWS:
        assert ('marker = "%s"' % r[0]) not in s, r[0]
    no = "nil" if live else "false"
    before = s.count("\t{ marker = ")
    old_wave = between(s, "function FOURTH.ww_wave_value(unit, e, m, row)\n", "-- a wanderer candidate:")
    old_still = between(s, "function FOURTH.ww_still_ok(enemy, unit)\n", "function FOURTH.evaluate_enemy_wave(")
    reps = [(RESTOCK, NEW_ENTRIES + RESTOCK), (WIND_OLD, WIND_NEW), (HOLD_OLD, HOLD_NEW),
            (old_wave, WAVE_VALUE_NEW), (WANDER_SAFE_OLD, WANDER_SAFE_NEW), (old_still, STILL_NEW),
            (MAP_OLD, MAP_NEW), (TIP_ANCHOR, TIP_NEW), (ANCHOR, render(EVALS, LIVE_RET if live else ANN_RET) + ANCHOR)]
    reps += [(a.replace("%NO%", no), b.replace("%NO%", no)) for a, b in GUARDS]
    for a, b in reps:
        assert s.count(a) == 1, (path[-12:], a[:70], s.count(a))
        s = s.replace(a, b)
    assert s.count("\t{ marker = ") == before + 28
    open(path, "w", encoding="utf-8", newline="").write(s)
    print(path, "entries", before, "->", before + 28)

src_now = open(SRC, encoding="utf-8").read()
kf = GW.keys_in(src_now)
assert len(kf) == 84, len(kf)
ww_block = GW.lua_block(GW.derive(kf)) + GW.nomelee_block(kf)
print("WW_NOMELEE:", GW.nomelee(kf))
for path in (SRC, ANN):
    s = open(path, encoding="utf-8", newline="").read()
    assert len(WW_GEN.findall(s)) == 1
    s = WW_GEN.sub(lambda m: ww_block, s)
    open(path, "w", encoding="utf-8", newline="").write(s)
print("WW table (84 keys) + WW_NOMELEE re-derived")

import gen_recharge_keys as G  # noqa: E402
new_block = G.lua_block(G.derive())
pat = re.compile(r"-- GENERATED by tools/gen_recharge_keys\.py.*?\nFOURTH\.load_recharge\(\)\n", re.S)
for path in (SRC, ANN):
    s = open(path, encoding="utf-8", newline="").read()
    assert len(pat.findall(s)) == 1
    s = pat.sub(lambda m: new_block, s)
    open(path, "w", encoding="utf-8", newline="").write(s)
print("lock table re-derived:", len(G.derive()), "keys")
