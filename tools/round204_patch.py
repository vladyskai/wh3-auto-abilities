#!/usr/bin/env python3
"""Round 204 (user ruling 2026-11-22, after the Skeleton battle in which free aim still never fired), both copies:

  "I think the safety makes no sense for this ability. ... the safety was meant for abilities that have a deviation from
   their path. But this ability's path is deterministic. ... We only need to know that in the path of the ability, there
   is very little of our units. Or should I say very little of our soldiers. And in this case, we should ignore single
   entities because the damage to our single entities would be not relevant. Also, please implement for tight call and
   wind blast. The slow effect is irrelevant in this case."

1. AN EXACT WAVE (no sideways drift: the WW row's buf = 0, 27 of the 32 keys) drops the round-162 safety distance. Its
   friendly test is: our SOLDIERS under the wave (inside its radius along the path) are at most FOURTH.WAVE_OWN_MAX.
   Our single entities are not counted. A wave WITH drift (5 keys) keeps the round-162 rule and the round-203 aim.
2. An exact wave's value is the enemy VALUE UNDER the wave (each unit's live value x the share of its soldiers inside
   the radius), no longer the whole value of every unit the path touches.
3. SIDEWAYS SHIFTS: every heading is also tested with the path moved FOURTH.FREE_AIM_SHIFTS metres to its right or left
   (a path along the enemy's rear ranks, away from our line).
4. An exact wave always goes out as an aimed ground order (the caster's own line included): the round-202 probe showed
   where that lands, the unit form's path was never checked in a battle.
5. The search runs once per FOURTH.FREE_AIM_EVERY polls per caster and ability (it tests 24 x 7 paths per enemy).
6. TIDECALL and WIND BLAST move from enemy_wave_charge to enemy_wave (the family stays, empty).
TEST-ONLY: ZZ_AUTO_TEST_NO_FREE_AIM keeps older worlds on the pre-203 rule (the safety distance, the caster's line).
Backups: docs/backups/round204/pre204_{live,ann}.lua."""
import os
import shutil

LIVE = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"
BK = r"C:\Users\vlady\Desktop\WH3_mod\docs\backups\round204"

SPAN_A = "-- a free-aim path across e along the heading (hx, hz): its value and its start, or nil when the start is out of the\n"
SPAN_B = "-- ROUND 164: the enemy value a path touches (every visible enemy within the radius of the segment)\n"
SPAN_NEW = """-- ============================================================================
-- ROUND 204 - AN EXACT WAVE NEEDS NO SAFETY DISTANCE (user ruling 2026-11-22:
-- "the safety was meant for abilities that have a deviation from their path.
-- But this ability's path is deterministic ... We only need to know that in the
-- path of the ability, there is very little of our ... soldiers. And in this
-- case, we should ignore single entities"). A wave whose table row has no
-- sideways drift (buf = 0) is EXACT: its friendly test counts OUR SOLDIERS under
-- the wave (single entities are not counted) against WAVE_OWN_MAX, its value is
-- the enemy value under the wave, and every heading is also tested moved
-- sideways (FREE_AIM_SHIFTS). A wave with drift keeps the round-162 distance.
-- ============================================================================
FOURTH.FREE_AIM_SHIFTS = { 0, 6, -6, 12, -12, 18, -18 }   -- ROUND 204: metres to the right (+) or left (-) of the heading
FOURTH.WAVE_OWN_MAX = 5         -- ROUND 204: at most this many of OUR soldiers under an exact wave
FOURTH.FREE_AIM_EVERY = 4       -- ROUND 204: the search runs once per this many polls per caster and ability
FOURTH.aim_next = {}

-- an exact wave: no sideways drift in its table row (and free aim not switched off by the harness)
function FOURTH.ww_exact(row)
	return row.buf == 0 and ZZ_AUTO_TEST_NO_FREE_AIM ~= true
end

-- the share (0..1) of a unit's soldiers under a wave of radius r along S-E: a grid of points over its rectangle
-- (one every 3 m or so, at most 10 x 6); a single entity is its centre
function FOURTH.wave_cover(s, sx, sz, ex, ez, r)
	if FOURTH.ww_pt_seg(s.x, s.z, sx, sz, ex, ez) - s.half > r then return 0 end
	if s.men <= 1 then
		if FOURTH.ww_pt_seg(s.x, s.z, sx, sz, ex, ez) <= r then return 1 end
		return 0
	end
	local na = math.max(1, math.min(10, math.floor(s.w / 3 + 0.5)))
	local nc = math.max(1, math.min(6, math.floor(s.d / 3 + 0.5)))
	local hit = 0
	for i = 1, na do
		local a = (i - 0.5) / na - 0.5
		for j = 1, nc do
			local c = (j - 0.5) / nc - 0.5
			local px = s.x + s.rx * a * s.w + s.fx * c * s.d
			local pz = s.z + s.rz * a * s.w + s.fz * c * s.d
			if FOURTH.ww_pt_seg(px, pz, sx, sz, ex, ez) <= r then hit = hit + 1 end
		end
	end
	return hit / (na * nc)
end

-- a free-aim path across e along the heading (hx, hz), moved <shift> metres to the heading's right: its value and its
-- start, or nil when the start is out of the caster's bound or the friendly test fails. NO gate on the enemy itself.
function FOURTH.ww_aim_value(unit, e, m, row, hx, hz, shift)
	shift = shift or 0
	local back = row.off + (e.half or 0)
	local sx, sz = e.x - hx * back + hz * shift, e.z - hz * back - hx * shift
	local cx, cz = FOURTH.self_xz(unit)
	if cx == nil then return nil end
	if FOURTH.eg_no_bound ~= true then
		local bound = FOURTH.eg_range_m
		if bound == nil or math.sqrt((sx - cx) ^ 2 + (sz - cz) ^ 2) > bound then return nil end
	end
	local val = FOURTH.ww_line_value(unit, m, row, sx, sz, sx + hx * row.path, sz + hz * row.path)
	if val == nil then return nil end
	return val, sx, sz
end

-- the pre-cast text of a free aim (the live copy's reason line)
function FOURTH.ww_aim_text()
	local a = FOURTH.ww_aim
	if a == nil then return "" end
	return string.format("; FREE AIM: the wave starts at (%.1f,%.1f) and rolls on bearing %.0f (moved %s m sideways)",
		a.x, a.z, a.deg, tostring(a.shift or 0))
end

-- THE FREE-AIM CAST HELPER: the ground form at the path's start with the heading as orientation. The point is built
-- with the game's own v(x, height, z) on the terrain height; anything unreadable -> no_target (the caller holds).
function FOURTH.aim_cast(uc, ability_key, aim)
	local pos = nil
	pcall(function()
		local h = bm:get_terrain_height(aim.x, aim.z)
		if type(h) == "number" then pos = v(aim.x, h, aim.z) end
	end)
	if pos == nil then return nil, nil, true end
	local ok_call, err_call = pcall(function()
		uc:perform_special_ability_ground(ability_key, pos, aim.deg, 0)
	end)
	return ok_call, err_call, false
end

-- a wave candidate: the enemy value its path touches, or nil when it is not allowed or not safe
-- ROUND 203: with a heading (hx, hz) the path is the free-aim one (and its start comes back too)
function FOURTH.ww_wave_value(unit, e, m, row, moving_ok, hx, hz, shift)
	-- ROUND 164: moving_ok = the charge arm (Tidecall, Wind Blast: the target is a charging enemy)
	if not (FOURTH.eg_class_ok(e.unit) and FOURTH.eg_enemy_within_bound(unit, e.unit)
		and (moving_ok or FOURTH.ww_target_still(e))) then
		return nil
	end
	if hx ~= nil then return FOURTH.ww_aim_value(unit, e, m, row, hx, hz, shift) end
	local sx, sz, ex, ez = FOURTH.ww_wave_line(unit, e, row)
	if sx == nil then return nil end
	local val = FOURTH.ww_line_value(unit, m, row, sx, sz, ex, ez)
	if val == nil then return nil end
	return val, sx, sz
end

-- ROUND 203: the friendly test and the value of ONE path S-E (nil when the friendly test fails)
function FOURTH.ww_line_value(unit, m, row, sx, sz, ex, ez)
	if FOURTH.ww_exact(row) then
		-- ROUND 204: an exact wave. OUR SOLDIERS under it (single entities not counted, the caster never), then
		-- the enemy value under it
		if row.allies then
			local self_id = nil
			pcall(function() self_id = tostring(unit:unique_ui_id()) end)
			local own = 0
			for i = 1, #m.ours do
				local o = m.ours[i]
				if o.men > 1 then
					local oid = nil
					pcall(function() oid = tostring(o.unit:unique_ui_id()) end)
					if oid == nil or oid ~= self_id then
						own = own + o.men * FOURTH.wave_cover(o, sx, sz, ex, ez, row.r)
						if own > FOURTH.WAVE_OWN_MAX then return nil end
					end
				end
			end
		end
		local val = 0
		for i = 1, #m.all do
			local o = m.all[i]
			local c = FOURTH.wave_cover(o, sx, sz, ex, ez, row.r)
			if c > 0 then val = val + (o.value or 1) * c end
		end
		if val <= 0 then return nil end   -- nothing under the wave
		return val
	end
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

"""

OLD_STILL = "						val, sx, sz = FOURTH.ww_wave_value(unit, e, m, row, false, a.hx, a.hz)\n"
NEW_STILL = "						val, sx, sz = FOURTH.ww_wave_value(unit, e, m, row, false, a.hx, a.hz, a.shift)\n"

OLD_FREE = """	local free = (ZZ_AUTO_TEST_NO_FREE_AIM ~= true)   -- ROUND 203
	local cx, cz = FOURTH.self_xz(unit)
"""
NEW_FREE = """	local free = (ZZ_AUTO_TEST_NO_FREE_AIM ~= true)   -- ROUND 203
	local cx, cz = FOURTH.self_xz(unit)
	local exact = FOURTH.ww_exact(row)   -- ROUND 204
	local shifts = exact and FOURTH.FREE_AIM_SHIFTS or { 0 }
	if free then
		-- ROUND 204: the search is heavy (24 headings x the shifts per enemy): once per FREE_AIM_EVERY polls
		local id = "?"
		pcall(function() id = tostring(unit:unique_ui_id()) end)
		local key = tostring(FOURTH.rc_self_keys and FOURTH.rc_self_keys[1])
		local per = FOURTH.aim_next[id]
		if per == nil then
			per = {}
			FOURTH.aim_next[id] = per
		end
		if (per[key] or 0) > tick_count then return %s end
		per[key] = tick_count + FOURTH.FREE_AIM_EVERY
	end
"""
OLD_LEGACY = "			if free and row.ground and cx ~= nil then\n"
NEW_LEGACY = "			if free and (row.ground or exact) and cx ~= nil then   -- ROUND 204: an exact wave is always aimed\n"
OLD_HEAD = """				local v2, ax, az = FOURTH.ww_aim_value(unit, e, m, row, hx, hz)
				if v2 ~= nil and (bv == nil or v2 > bv) then
					best, bv = e, v2
					aim = { x = ax, z = az, hx = hx, hz = hz, deg = k * 360 / FOURTH.FREE_AIM_STEPS }
				end
"""
NEW_HEAD = """				for q = 1, #shifts do
					local v2, ax, az = FOURTH.ww_aim_value(unit, e, m, row, hx, hz, shifts[q])
					if v2 ~= nil and (bv == nil or v2 > bv) then
						best, bv = e, v2
						aim = { x = ax, z = az, hx = hx, hz = hz, deg = k * 360 / FOURTH.FREE_AIM_STEPS, shift = shifts[q] }
					end
				end
"""
OLD_ENTRIES = [
    '\t{ marker = "tidecall", name = "Tidecall", trigger = "enemy_wave_charge",\n',
    '\t{ marker = "wind_blast", name = "Wind Blast", trigger = "enemy_wave_charge",\n',
]


def one(s, a, b, what):
    assert s.count(a) == 1, (what, s.count(a))
    return s.replace(a, b)


def patch(path, live):
    s = open(path, encoding="utf-8", newline="").read()
    assert "ROUND 204 - AN EXACT WAVE" not in s, "already patched: " + path
    i, j = s.index(SPAN_A), s.index(SPAN_B)
    assert 0 < i < j and s.count(SPAN_A) == 1 and s.count(SPAN_B) == 1
    s = s[:i] + SPAN_NEW + s[j:]
    s = one(s, OLD_STILL, NEW_STILL, "still")
    s = one(s, OLD_FREE, NEW_FREE % ("nil" if live else "false"), "free")
    s = one(s, OLD_LEGACY, NEW_LEGACY, "legacy")
    s = one(s, OLD_HEAD, NEW_HEAD, "headings")
    for e in OLD_ENTRIES:
        s = one(s, e, e.replace('trigger = "enemy_wave_charge"', 'trigger = "enemy_wave"'), "entry")
    open(path, "w", encoding="utf-8", newline="").write(s)
    print("patched", path)


def main():
    os.makedirs(BK, exist_ok=True)
    for src, name in ((LIVE, "pre204_live.lua"), (ANN, "pre204_ann.lua")):
        dst = os.path.join(BK, name)
        if not os.path.exists(dst):
            shutil.copy2(src, dst)
    patch(LIVE, True)
    patch(ANN, False)


if __name__ == "__main__":
    main()
