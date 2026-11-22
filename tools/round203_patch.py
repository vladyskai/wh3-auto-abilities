#!/usr/bin/env python3
"""Round 203 (user rulings 2026-11-22: "A: but be careful. Dragon breaths always come from a caster. Other abilities
might also, check individually to be sure." then "All 30 placed"), both copies: FREE AIM for the straight waves.

The 30 enemy_wave entries (battle_vortexs.launch_source = target_near_edge: the game PLACES the wave) no longer test only
the line from the caster through the enemy. For every standing enemy in range the evaluator also tests
FOURTH.FREE_AIM_STEPS (24) compass headings, each path starting <offset + the target's half extent> before the enemy's
centre and rolling <path> metres along the heading. A path counts when its START POINT is inside the ability's own bound
from the caster and none of ours stands within the round-162 distances. The most enemy value wins; the caster's own line
is tested first and keeps a tie. When the caster's line wins the cast goes out as before (the unit form). When another
heading wins the cast goes out in the GROUND form at the path's start with the heading as ORIENTATION (the round-202
probe: the wave starts at the point and follows the orientation). A ground-only wave (Blue Fire of Chaos x2) always
goes out that way: before, it was placed on the enemy's centre with orientation 0.
The 2 charge waves and the 5 cones are untouched. TEST-ONLY: ZZ_AUTO_TEST_NO_FREE_AIM keeps older worlds on the old rule.
Backups: docs/backups/round203/pre203_{live,ann}.lua."""
import os
import shutil

LIVE = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"
BK = r"C:\Users\vlady\Desktop\WH3_mod\docs\backups\round203"

# 1. the wave candidate: the old function, split into the gate, the line and the line's value ------------------------
OLD_VALUE_HEAD = """-- a wave candidate: the enemy value its path touches, or nil when it is not allowed or not safe
function FOURTH.ww_wave_value(unit, e, m, row, moving_ok)
	-- ROUND 164: moving_ok = the charge arm (Tidecall, Wind Blast: the target is a charging enemy)
	if not (FOURTH.eg_class_ok(e.unit) and FOURTH.eg_enemy_within_bound(unit, e.unit)
		and (moving_ok or FOURTH.ww_target_still(e))) then
		return nil
	end
	local sx, sz, ex, ez = FOURTH.ww_wave_line(unit, e, row)
	if sx == nil then return nil end
	if row.allies then
"""
NEW_VALUE_HEAD = """-- ============================================================================
-- ROUND 203 - FREE AIM FOR THE STRAIGHT WAVES (user rulings 2026-11-22: "A: but
-- be careful. Dragon breaths always come from a caster. Other abilities might
-- also, check individually to be sure." and "All 30 placed"). The game PLACES
-- these waves (launch_source target_near_edge; the build checks every key), and
-- the round-202 probe showed that a ground-form order starts the wave at the
-- point and sends it along the ORIENTATION. So the evaluator no longer tests
-- only the line from the caster through the enemy: for each standing enemy in
-- range it also tests FREE_AIM_STEPS compass headings. A path counts when its
-- START is inside the ability's own bound from the caster (the caster never
-- walks) and none of ours stands within the round-162 distances. The most enemy
-- value wins; the caster's own line is tested first and keeps a tie.
-- TEST-ONLY: ZZ_AUTO_TEST_NO_FREE_AIM (the harness sets it for worlds written
-- before round 203) keeps the caster's line only.
-- ============================================================================
FOURTH.FREE_AIM_STEPS = 24      -- ROUND 203: one heading every 15 degrees
FOURTH.ww_aim = nil             -- ROUND 203: the chosen free aim { x, z, deg, hx, hz } (cleared by FOURTH.entry_reset)

-- the compass bearing (degrees, 0..360) of a heading on X/Z: a bearing b faces (sin b, cos b)
function FOURTH.ww_bearing(hx, hz)
	local b = math.deg((math.atan2 or math.atan)(hx, hz))
	if b < 0 then b = b + 360 end
	return b
end

-- a free-aim path across e along the heading (hx, hz): its value and its start, or nil when the start is out of the
-- caster's bound or one of ours is too close. NO gate on the enemy itself (the caller has asked it).
function FOURTH.ww_aim_value(unit, e, m, row, hx, hz)
	local back = row.off + (e.half or 0)
	local sx, sz = e.x - hx * back, e.z - hz * back
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
	return string.format("; FREE AIM: the wave starts at (%.1f,%.1f) and rolls on bearing %.0f", a.x, a.z, a.deg)
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
function FOURTH.ww_wave_value(unit, e, m, row, moving_ok, hx, hz)
	-- ROUND 164: moving_ok = the charge arm (Tidecall, Wind Blast: the target is a charging enemy)
	if not (FOURTH.eg_class_ok(e.unit) and FOURTH.eg_enemy_within_bound(unit, e.unit)
		and (moving_ok or FOURTH.ww_target_still(e))) then
		return nil
	end
	if hx ~= nil then return FOURTH.ww_aim_value(unit, e, m, row, hx, hz) end
	local sx, sz, ex, ez = FOURTH.ww_wave_line(unit, e, row)
	if sx == nil then return nil end
	local val = FOURTH.ww_line_value(unit, m, row, sx, sz, ex, ez)
	if val == nil then return nil end
	return val, sx, sz
end

-- ROUND 203: the friendly test and the value of ONE path S-E (nil when one of ours is too close)
function FOURTH.ww_line_value(unit, m, row, sx, sz, ex, ez)
	if row.allies then
"""

# 2. the chosen target carries its aim -------------------------------------------------------------------------------
OLD_TAKE = """function FOURTH.ww_take(unit, e, row)
	FOURTH.eg_enemy = e.unit
"""
NEW_TAKE = """function FOURTH.ww_take(unit, e, row, aim)
	FOURTH.ww_aim = aim   -- ROUND 203: nil = the caster's own line, cast as before
	FOURTH.eg_enemy = e.unit
"""

# 3. the pre-cast re-check follows the chosen heading ----------------------------------------------------------------
OLD_STILL = """				return FOURTH.ww_wave_value(unit, e, m, row, FOURTH.ww_charge == true) ~= nil
"""
NEW_STILL = """				if FOURTH.ww_aim ~= nil then
					-- ROUND 203: the same heading on the fresh map; the start follows the enemy
					local a = FOURTH.ww_aim
					local val, sx, sz
					if a.legacy then
						val, sx, sz = FOURTH.ww_wave_value(unit, e, m, row)
					else
						val, sx, sz = FOURTH.ww_wave_value(unit, e, m, row, false, a.hx, a.hz)
					end
					if val == nil then return false end
					a.x, a.z = sx, sz
					return true
				end
				return FOURTH.ww_wave_value(unit, e, m, row, FOURTH.ww_charge == true) ~= nil
"""

# 4. the evaluator's loop ---------------------------------------------------------------------------------------------
OLD_LOOP = """	local best, bv = nil, nil
	for i = 1, #m.all do
		local e = m.all[i]
		local v = FOURTH.ww_wave_value(unit, e, m, row)
		if v ~= nil and (bv == nil or v > bv) then best, bv = e, v end
	end
	if best == nil then return %s end
	FOURTH.ww_take(unit, best, row)
"""
NEW_LOOP = """	local best, bv, aim = nil, nil, nil
	local free = (ZZ_AUTO_TEST_NO_FREE_AIM ~= true)   -- ROUND 203
	local cx, cz = FOURTH.self_xz(unit)
	for i = 1, #m.all do
		local e = m.all[i]
		-- the caster's own line first: it keeps a tie
		local val, sx, sz = FOURTH.ww_wave_value(unit, e, m, row)
		if val ~= nil and (bv == nil or val > bv) then
			best, bv, aim = e, val, nil
			if free and row.ground and cx ~= nil then
				-- a ground-only wave has no unit form: its own line goes out as an aimed ground order too
				local dx, dz = e.x - cx, e.z - cz
				local len = math.sqrt(dx * dx + dz * dz)
				if len >= 0.5 then
					aim = { x = sx, z = sz, hx = dx / len, hz = dz / len, deg = FOURTH.ww_bearing(dx / len, dz / len), legacy = true }
				end
			end
		end
		if free and FOURTH.eg_class_ok(e.unit) and FOURTH.eg_enemy_within_bound(unit, e.unit) and FOURTH.ww_target_still(e) then
			for k = 0, FOURTH.FREE_AIM_STEPS - 1 do
				local ang = math.rad(k * 360 / FOURTH.FREE_AIM_STEPS)
				local hx, hz = math.sin(ang), math.cos(ang)
				local v2, ax, az = FOURTH.ww_aim_value(unit, e, m, row, hx, hz)
				if v2 ~= nil and (bv == nil or v2 > bv) then
					best, bv = e, v2
					aim = { x = ax, z = az, hx = hx, hz = hz, deg = k * 360 / FOURTH.FREE_AIM_STEPS }
				end
			end
		end
	end
	if best == nil then return %s end
	FOURTH.ww_take(unit, best, row, aim)
"""
OLD_REASON = """		(d ~= nil) and string.format("%.1f", d) or "?", tostring(FOURTH.eg_range_m))
end
"""
NEW_REASON = """		(d ~= nil) and string.format("%.1f", d) or "?", tostring(FOURTH.eg_range_m)) .. FOURTH.ww_aim_text()
end
"""

# 5. the cast ----------------------------------------------------------------------------------------------------------
CAST_ANCHOR = "\t-- ROUND 165: a WW pick whose row is ground-only (Blue Fire of Chaos x2, Siegebreaker, Heaven's Gate, Lamprey's\n"
CAST_NEW = """	-- ROUND 203: a FREE-AIM wave goes out in the ground form at its path's start, the heading as orientation
	elseif FOURTH.eg_arm == "ww" and FOURTH.ww_aim ~= nil then
		ok_call, err_call, no_target = FOURTH.aim_cast(uc, ability_key, FOURTH.ww_aim)
%s"""
CAST_LOG = """		if not quiet then
			log(string.format("  free-aim cast          : perform_special_ability_ground('%s', point (%.1f,%.1f), orientation %.0f, 0)",
				tostring(ability_key), FOURTH.ww_aim.x, FOURTH.ww_aim.z, FOURTH.ww_aim.deg))
		end
"""

# 6. the per-entry reset -------------------------------------------------------------------------------------------------
OLD_RESET = "\tFOURTH.eg_ground = nil\n\tFOURTH.eg_melee_only = nil\n"
NEW_RESET = "\tFOURTH.eg_ground = nil\n\tFOURTH.ww_aim = nil   -- ROUND 203: the free aim of a wave\n\tFOURTH.eg_melee_only = nil\n"


def one(s, a, b, what):
    assert s.count(a) == 1, (what, s.count(a))
    return s.replace(a, b)


def patch(path, live):
    s = open(path, encoding="utf-8", newline="").read()
    assert "ROUND 203 - FREE AIM" not in s, "already patched: " + path
    s = one(s, OLD_VALUE_HEAD, NEW_VALUE_HEAD, "value head")
    # the old function's tail: its friendly loop ends, then it returns the path value. The new ww_line_value keeps it.
    s = one(s, OLD_TAKE, NEW_TAKE, "take")
    s = one(s, OLD_STILL, NEW_STILL, "still")
    i = s.index("\nfunction FOURTH.evaluate_enemy_wave(unit, routing)\n")
    j = s.index("\nfunction FOURTH.evaluate_enemy_wander(unit, routing)\n", i)
    body = s[i:j]
    miss = "nil" if live else "false"
    body = one(body, OLD_LOOP % miss, NEW_LOOP % miss, "loop")
    if live:
        body = one(body, OLD_REASON, NEW_REASON, "reason")
    s = s[:i] + body + s[j:]
    s = one(s, CAST_ANCHOR, (CAST_NEW % (CAST_LOG if live else "")) + CAST_ANCHOR, "cast")
    s = one(s, OLD_RESET, NEW_RESET, "reset")
    open(path, "w", encoding="utf-8", newline="").write(s)
    print("patched", path)


def main():
    os.makedirs(BK, exist_ok=True)
    for src, name in ((LIVE, "pre203_live.lua"), (ANN, "pre203_ann.lua")):
        dst = os.path.join(BK, name)
        if not os.path.exists(dst):
            shutil.copy2(src, dst)
    patch(LIVE, True)
    patch(ANN, False)


if __name__ == "__main__":
    main()
