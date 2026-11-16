#!/usr/bin/env python3
"""Round 162 (harness 161): the wandering winds (32 entries / 32 keys; 2 new families), user rulings 2026-11-16.

Earlier status: "excluded (auto: vortex / wandering wind (friendly fire, family decision 2026-10-09))", a RULE, never
a ruling on these abilities one by one. The rulings:
  * the 12 straight WAVES: "Clear path, most value and not currently moving" -> NEW enemy_wave: the caster standing
    still; among the visible enemies in range that are standing still, the one whose wave path (from offset + the
    target's half extent before its centre, along the caster-to-target heading, for speed x duration metres) has none of
    our units within radius + the simulated 95% sideways drift + 10 m, and the most enemy value touched by the path.
  * the 16 WANDERERS: worst-case reach, refined by "some abilities are more random than others" -> "Simulated 95%":
    NEW enemy_wander: the caster standing still; the visible enemy infantry in range, standing still, whose blast
    (radius) covers the blob density line and the most value, with none of our units within radius + the simulated 95%
    distance from the start + 10 m of the target.
  * the other 6, "Blob rule; close 2": Heaven's Gate and The Abyssal Swarm (cannot hurt our units: no friendly test)
    and The Dwellers Below x2 (static: radius + 10 m) ride enemy_wander; Gehenna's Golden Globe and Wall of Wind &
    Fire are closed (their heading is not in the data).
  * "Simulated 95%" (the buffer), "Automate with the big buffer" (The Burning Head x2, Arnzipal's Black Horror).
The per-key numbers come from the GENERATED FOURTH.WW_TEXT (tools/gen_ww_tables.py).
"""
import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_ww_tables as GW  # noqa: E402
import gamedata_paths as GP  # noqa: E402

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"
WAVE, WANDER = "enemy_wave", "enemy_wander"
ROWS = [
    ("wrath_of_manann", "Wrath of Manann", WAVE, "wh_dlc07_item_abilities_wrath_of_manann"),
    ("wind_of_death", "Wind of Death", WAVE, "wh2_dlc15_spell_bound_wind_of_death"),
    ("seafang", "Seafang", WAVE, "wh_dlc08_lord_abilities_seafang"),
    ("the_burning_head", "The Burning Head", WAVE, "wh3_dlc25_spell_bound_fire_the_burning_head"),
    ("burning_head_skull", "The Burning Head", WAVE, "wh3_dlc29_spell_bound_fire_skull_of_flaming_death"),
    ("khaines_ring_of_fury", "Bound Fiery Convocation", WAVE, "wh2_main_spell_bound_khaines_ring_of_fury"),
    ("fiery_convocation", "Fiery Convocation", WAVE, "wh2_dlc10_spell_bound_magic_fiery_convocation"),
    ("burning_alignment", "Burning Alignment", WAVE, "wh2_dlc12_unit_abilities_burning_alignment"),
    ("hell_hammer", "Hell Hammer", WAVE, "wh3_dlc23_spell_bound_hell_hammer"),
    ("nightmaw", "Nightmaw", WAVE, "wh3_dlc27_character_abilities_nightmaw"),
    ("penumbral_pendulum", "The Penumbral Pendulum", WAVE, "wh3_dlc20_spell_bound_the_penumbral_pendulum"),
    ("arnizipals_black_horror", "Arnzipal's Black Horror", WAVE, "wh2_dlc10_item_bound_arnizipals_black_horror"),
    ("banishment", "Banishment", WANDER, "wh3_main_spell_bound_banishment"),
    ("banishment_dlc04", "Banishment", WANDER, "wh_dlc04_spell_bound_banishment"),
    ("banishment_innate", "Banishment", WANDER, "wh_dlc04_spell_bound_banishment_innate"),
    ("lesser_banishment", "Lesser Banishment", WANDER, "wh2_dlc17_spell_bound_lesser_banishment"),
    ("lesser_chain_lightning", "Lesser Chain Lightning", WANDER, "wh2_dlc17_spell_bound_lesser_chain_lightning"),
    ("flame_storm_dlc20", "Flame Storm", WANDER, "wh3_dlc20_spell_bound_flame_storm"),
    ("flame_storm", "Flame Storm", WANDER, "wh3_main_spell_bound_flame_storm"),
    ("gem_of_sunfire", "The Gem of Sunfire", WANDER, "wh2_main_spell_bound_the_gem_of_sunfire"),
    ("gehennas_golden_hounds", "Gehenna's Golden Hounds", WANDER, "wh3_dlc20_spell_bound_gehennas_golden_hounds"),
    ("gilded_horn", "Gilded Horn of Galon Konook", WANDER, "wh2_main_item_bound_gilded_horn_of_galon_konook"),
    ("hounds_of_orion", "Hounds of Orion", WANDER, "wh_dlc05_lord_ablities_grey_wolves"),
    ("sandstorm", "Sandstorm", WANDER, "wh2_dlc09_lord_abilities_sand_storm"),
    ("soul_slaying_hunger", "Soul-slaying Hunger", WANDER, "wh3_dlc29_unit_abilities_soul_slaying_hunger"),
    ("sword_of_khaine", "Sword of Khaine", WANDER, "wh2_dlc10_weapon_abilities_sword_of_khaine"),
    ("purple_sun_of_xereus", "The Purple Sun of Xereus", WANDER, "wh2_dlc11_spell_bound_the_purple_sun_of_xereus"),
    ("ruination_of_cities", "The Ruination of Cities", WANDER, "wh2_main_lord_abilities_the_ruination_of_cities"),
    ("dwellers_below", "The Dwellers Below", WANDER, "wh3_main_spell_bound_the_dwellers_below"),
    ("dwellers_below_dlc08", "The Dwellers Below", WANDER, "wh_dlc08_spell_bound_the_dwellers_below"),
    ("heavens_gate", "Heaven's Gate", WANDER, "wh3_cp1_item_abilities_heavens_gate"),
    ("abyssal_swarm", "The Abyssal Swarm", WANDER, "wh3_dlc29_spell_bound_undeath_the_abyssal_swarm"),
]
assert len(ROWS) == 32 and len(set(r[0] for r in ROWS)) == 32 and len(set(r[3] for r in ROWS)) == 32


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
print("multi-use:", len(HOLD), "wind-up:", len(WIND), "not_flying classes:", NF)

RESTOCK = '\t{ marker = "restock", name = "Restock!", trigger = "ally_ammo_low",'
WIND_OLD = "\twind_up_s = {\n"
WIND_NEW = WIND_OLD + "\t\t-- ROUND 162: the wandering winds' wind-ups (unit_spec_abil wind_up_time)\n" + "".join(
    '\t\t["%s"] = %s,\n' % (k, v) for k, v in WIND)
HOLD_OLD = "\thold_s = {\n"
HOLD_NEW = HOLD_OLD + "\t\t-- ROUND 162: the wandering winds with more than one use (recharge_time)\n" + "".join(
    '\t\t["%s"] = %s,\n' % (k, v) for k, v in HOLD)
RECHECK_OLD = ('\t\telseif eg_mode_now == "shot" then\n'
               '\t\t\t-- ROUND 156: the magic missiles - the map is rebuilt; the target must still qualify and be safe\n'
               '\t\t\tcond_now = FOURTH.shot_still_ok(enemy, unit)\n')
RECHECK_NEW = RECHECK_OLD + ('\t\telseif eg_mode_now == "ww" then\n'
                             '\t\t\t-- ROUND 162: the wandering winds - the map is rebuilt; the caster and the target still\n'
                             '\t\t\t-- standing, the path or the area still clear of our units\n'
                             '\t\t\tcond_now = FOURTH.ww_still_ok(enemy, unit)\n')

EVALS = r'''-- ============================================================================
-- ROUND 162 - THE WANDERING WINDS (user rulings 2026-11-16; earlier a 2026-10-09 family RULE, never ruled one by one).
--   enemy_wave (12 straight waves: they start offset + the target's half extent
--     before its centre and roll speed x duration metres along the caster-to-
--     target heading): the caster STANDING STILL; among the visible enemies in
--     range that are STANDING STILL (the 3-5 s cast: a moving target walks out of
--     the computed path), the one whose path has none of our units (the caster
--     counting) within radius + SHOT_SAFE_M at its start, widening to radius +
--     the simulated 95% sideways drift + SHOT_SAFE_M at its end (a wave cannot
--     drift where it starts), and the most enemy value touched by the path.
--   enemy_wander (16 wanderers, The Dwellers Below x2, Heaven's Gate, The
--     Abyssal Swarm): the caster STANDING STILL; the visible enemy infantry in
--     range, STANDING STILL, whose blast covers the blob density line and the most
--     value, with none of our units within radius + the simulated 95% distance
--     from the start + SHOT_SAFE_M of the target (+ its half extent when the
--     vortex starts at its near edge); no friendly test when the game marks the
--     vortex as not affecting allies.
--   The numbers per key: the GENERATED FOURTH.WW_TEXT (tools/gen_ww_tables.py).
--   Every read fails closed.
-- ============================================================================
function FOURTH.ww_row()
	local key = FOURTH.rc_self_keys and FOURTH.rc_self_keys[1]
	return key and FOURTH.WW[key]
end

-- the target standing still: is_moving() must read exactly false
function FOURTH.ww_target_still(e)
	local ok, mv = pcall(function() return e.unit:is_moving() end)
	return ok and mv == false
end

-- the distance from a point to the segment S-E
function FOURTH.ww_pt_seg(px, pz, sx, sz, ex, ez)
	local vx, vz = ex - sx, ez - sz
	local l2 = vx * vx + vz * vz
	local t = 0
	if l2 > 0 then t = math.max(0, math.min(1, ((px - sx) * vx + (pz - sz) * vz) / l2)) end
	local qx, qz = sx + vx * t, sz + vz * t
	return math.sqrt((px - qx) ^ 2 + (pz - qz) ^ 2)
end

-- the gap between a shape's rectangle and the segment S-E (0 when the segment crosses it): a clip test, else the
-- smallest of the two ends to the rectangle and the four corners to the segment (exact for a convex rectangle)
function FOURTH.ww_seg_rect_gap(sx, sz, ex, ez, s)
	local a0 = (sx - s.x) * s.rx + (sz - s.z) * s.rz
	local c0 = (sx - s.x) * s.fx + (sz - s.z) * s.fz
	local a1 = (ex - s.x) * s.rx + (ez - s.z) * s.rz
	local c1 = (ex - s.x) * s.fx + (ez - s.z) * s.fz
	local hw, hd = s.w / 2, s.d / 2
	local da, dc = a1 - a0, c1 - c0
	local t0, t1, hit = 0, 1, true
	local P = { -da, da, -dc, dc }
	local Q = { a0 + hw, hw - a0, c0 + hd, hd - c0 }
	for i = 1, 4 do
		local p, q = P[i], Q[i]
		if p == 0 then
			if q < 0 then hit = false end
		else
			local r = q / p
			if p < 0 then
				if r > t1 then hit = false elseif r > t0 then t0 = r end
			else
				if r < t0 then hit = false elseif r < t1 then t1 = r end
			end
		end
	end
	if hit and t0 <= t1 then return 0 end
	local best = math.min(FOURTH.blob_rect_gap(sx, sz, s), FOURTH.blob_rect_gap(ex, ez, s))
	for _, ac in ipairs({ { -hw, -hd }, { hw, -hd }, { -hw, hd }, { hw, hd } }) do
		local g = FOURTH.ww_pt_seg(s.x + s.rx * ac[1] + s.fx * ac[2], s.z + s.rz * ac[1] + s.fz * ac[2], sx, sz, ex, ez)
		if g < best then best = g end
	end
	return best
end

-- the wave's straight path for target shape e: start S = offset + the target's half extent before its centre on the
-- caster-to-target heading, end E = S + path along it; nil when the caster's position is unreadable
function FOURTH.ww_wave_line(unit, e, row)
	local cx, cz = FOURTH.self_xz(unit)
	if cx == nil then return nil end
	local dx, dz = e.x - cx, e.z - cz
	local len = math.sqrt(dx * dx + dz * dz)
	if len < 0.5 then return nil end
	local hx, hz = dx / len, dz / len
	local back = row.off + (e.half or 0)
	local sx, sz = e.x - hx * back, e.z - hz * back
	return sx, sz, sx + hx * row.path, sz + hz * row.path
end

-- a wave candidate: the enemy value its path touches, or nil when it is not allowed or not safe
function FOURTH.ww_wave_value(unit, e, m, row)
	if not (FOURTH.eg_class_ok(e.unit) and FOURTH.eg_enemy_within_bound(unit, e.unit) and FOURTH.ww_target_still(e)) then
		return nil
	end
	local sx, sz, ex, ez = FOURTH.ww_wave_line(unit, e, row)
	if sx == nil then return nil end
	if row.allies then
		-- the drift grows from 0 at the start to the 95% value at the end (it grows slower than a straight line, so
		-- this cone is on the safe side): the margin for a unit is taken at its farthest point along the path
		local l2 = (ex - sx) ^ 2 + (ez - sz) ^ 2
		for i = 1, #m.ours do
			local o = m.ours[i]
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

-- a wanderer candidate: the blob value its blast destroys (and the soldiers covered), or nil
function FOURTH.ww_wander_value(unit, e, m, row)
	if not (FOURTH.eg_class_ok(e.unit) and FOURTH.eg_enemy_within_bound(unit, e.unit) and FOURTH.ww_target_still(e)) then
		return nil
	end
	if row.allies then
		local need = row.r + row.buf + FOURTH.SHOT_SAFE_M
		if row.kind == 3 then need = need + (e.half or 0) end
		for i = 1, #m.ours do
			if FOURTH.blob_rect_gap(e.x, e.z, m.ours[i]) <= need then return nil end
		end
	end
	local sc = FOURTH.blob_score(e, m, row.r)
	if sc < FOURTH.blob_need(row.r) or not FOURTH.blob_trash_ok(e, sc, row.r) then return nil end
	return FOURTH.blob_value(e, m, row.r, nil), sc
end

-- the chosen target becomes the cast target (a ground-only ability casts on the ground under it)
function FOURTH.ww_take(unit, e, row)
	FOURTH.eg_enemy = e.unit
	FOURTH.eg_arm = "ww"
	FOURTH.eg_caster_su = FOURTH.eg_fresh_caster_su(unit)
	FOURTH.cast_target = e.unit
	if row.ground then FOURTH.eg_ground = true end
end

-- the pre-cast re-check: the caster still standing; the same enemy, rebuilt from a fresh map, still qualifies
function FOURTH.ww_still_ok(enemy, unit)
	local row = FOURTH.ww_row()
	if row == nil or not FOURTH.blob_still(unit) then return false end
	local m = FOURTH.blob_map(true)
	local id = nil
	pcall(function() id = tostring(enemy:unique_ui_id()) end)
	if id == nil then return false end
	local list = (row.kind == 1) and m.all or m.enemies
	for i = 1, #list do
		local e = list[i]
		local eid = nil
		pcall(function() eid = tostring(e.unit:unique_ui_id()) end)
		if eid == id then
			if row.kind == 1 then return FOURTH.ww_wave_value(unit, e, m, row) ~= nil end
			return FOURTH.ww_wander_value(unit, e, m, row) ~= nil
		end
	end
	return false
end

function FOURTH.evaluate_enemy_wave(unit, routing)
	FOURTH.eg_mode = "ww"
	local row = FOURTH.ww_row()
	if routing or row == nil or row.kind ~= 1 or not FOURTH.blob_still(unit) then return %NO% end
	local m = FOURTH.blob_map(false)
	local best, bv = nil, nil
	for i = 1, #m.all do
		local e = m.all[i]
		local v = FOURTH.ww_wave_value(unit, e, m, row)
		if v ~= nil and (bv == nil or v > bv) then best, bv = e, v end
	end
	if best == nil then return %NO% end
	FOURTH.ww_take(unit, best, row)
	%RET_WAVE%
end

function FOURTH.evaluate_enemy_wander(unit, routing)
	FOURTH.eg_mode = "ww"
	local row = FOURTH.ww_row()
	if routing or row == nil or row.kind == 1 or not FOURTH.blob_still(unit) then return %NO% end
	local m = FOURTH.blob_map(false)
	local best, bv, bs = nil, nil, nil
	for i = 1, #m.enemies do
		local e = m.enemies[i]
		local v, sc = FOURTH.ww_wander_value(unit, e, m, row)
		if v ~= nil and (bv == nil or v > bv) then best, bv, bs = e, v, sc end
	end
	if best == nil then return %NO% end
	FOURTH.ww_take(unit, best, row)
	%RET_WANDER%
end

'''
LIVE_RET = {
    "%NO%": "nil",
    "%RET_WAVE%": ('local etype = "enemy"\n'
                   '\tpcall(function() etype = tostring(best.unit:type()) end)\n'
                   '\tlocal d = FOURTH.eg_enemy_gap(unit, best.unit)\n'
                   '\treturn string.format("wave path clear (targeting %s, standing): value on the %sm path %.0f; none of ours "\n'
                   '\t\t.. "within %sm of its start growing to %sm at its end (radius %s + 95%% drift %s + %s); distance %sm bound %sm",\n'
                   '\t\tetype, tostring(row.path), bv, tostring(row.r + FOURTH.SHOT_SAFE_M), tostring(row.r + row.buf + FOURTH.SHOT_SAFE_M),\n'
                   '\t\ttostring(row.r), tostring(row.buf), tostring(FOURTH.SHOT_SAFE_M),\n'
                   '\t\t(d ~= nil) and string.format("%.1f", d) or "?", tostring(FOURTH.eg_range_m))'),
    "%RET_WANDER%": ('local etype = "enemy"\n'
                     '\tpcall(function() etype = tostring(best.unit:type()) end)\n'
                     '\tlocal d = FOURTH.eg_enemy_gap(unit, best.unit)\n'
                     '\tlocal safe = "it cannot hit our units"\n'
                     '\tif row.allies then\n'
                     '\t\tsafe = string.format("none of ours within %sm (radius %s + 95%% reach %s + %s)",\n'
                     '\t\t\ttostring(row.r + row.buf + FOURTH.SHOT_SAFE_M), tostring(row.r), tostring(row.buf), tostring(FOURTH.SHOT_SAFE_M))\n'
                     '\tend\n'
                     '\treturn string.format("wandering blast on a standing blob (targeting %s): value %.0f, %d soldiers in the %sm "\n'
                     '\t\t.. "blast (line %d); %s; distance %sm bound %sm", etype, bv, math.floor(bs + 0.5), tostring(row.r),\n'
                     '\t\tFOURTH.blob_need(row.r), safe, (d ~= nil) and string.format("%.1f", d) or "?", tostring(FOURTH.eg_range_m))'),
}
ANN_RET = {"%NO%": "false", "%RET_WAVE%": "return true", "%RET_WANDER%": "return true"}


def render(tpl, rep):
    for k, v in rep.items():
        tpl = tpl.replace(k, v)
    assert "%NO%" not in tpl and "%RET_" not in tpl
    return tpl


MAP_OLD = "\tenemy_blob_vortex = FOURTH.evaluate_enemy_blob,\n"
MAP_NEW = MAP_OLD + "\t-- ROUND 162\n\tenemy_wave = FOURTH.evaluate_enemy_wave,\n\tenemy_wander = FOURTH.evaluate_enemy_wander,\n"
TIP_ANCHOR = ('\tenemy_blob_vortex = "When armed and standing still, fires at the enemy infantry where the blast destroys the '
              'most value, when it hits enough soldiers and none of ours are near",\n')
TIP_NEW = TIP_ANCHOR + (
    '\tenemy_wave = "When armed and standing still, fires its wave at a standing enemy whose path holds the most enemy value '
    'and none of our units",\n'
    '\tenemy_wander = "When armed and standing still, fires at a standing enemy blob worth the most, with none of our units '
    'within the blast\'s wandering reach",\n')
ANCHOR = "FOURTH.evaluators = {\n"
VORTEX_END = "FOURTH.load_vortex_table()\n"

for path, live in ((SRC, True), (ANN, False)):
    s = open(path, encoding="utf-8", newline="").read()
    assert "function FOURTH.evaluate_enemy_wave(" not in s and "FOURTH.WW_TEXT" not in s
    before = s.count("\t{ marker = ")
    s = s.replace(RESTOCK, NEW_ENTRIES + RESTOCK, 1) if s.count(RESTOCK) == 1 else None
    assert s is not None
    for a, b in ((WIND_OLD, WIND_NEW), (HOLD_OLD, HOLD_NEW), (RECHECK_OLD, RECHECK_NEW), (MAP_OLD, MAP_NEW),
                 (TIP_ANCHOR, TIP_NEW), (ANCHOR, render(EVALS, LIVE_RET if live else ANN_RET) + ANCHOR)):
        assert s.count(a) == 1, (a[:70], s.count(a))
        s = s.replace(a, b)
    assert s.count("\t{ marker = ") == before + 32
    open(path, "w", encoding="utf-8", newline="").write(s)
    print(path, "entries", before, "->", before + 32)

src_now = open(SRC, encoding="utf-8").read()
kf = GW.keys_in(src_now)
assert len(kf) == 32, len(kf)
block = GW.lua_block(GW.derive(kf))
for path in (SRC, ANN):
    s = open(path, encoding="utf-8", newline="").read()
    assert s.count(VORTEX_END) == 1
    s = s.replace(VORTEX_END, VORTEX_END + block)
    open(path, "w", encoding="utf-8", newline="").write(s)
print("WW table generated (32 keys)")

import gen_recharge_keys as G  # noqa: E402
new_block = G.lua_block(G.derive())
pat = re.compile(r"-- GENERATED by tools/gen_recharge_keys\.py.*?\nFOURTH\.load_recharge\(\)\n", re.S)
for path in (SRC, ANN):
    s = open(path, encoding="utf-8", newline="").read()
    assert len(pat.findall(s)) == 1
    s = pat.sub(lambda m: new_block, s)
    open(path, "w", encoding="utf-8", newline="").write(s)
print("lock table re-derived:", len(G.derive()), "keys")
