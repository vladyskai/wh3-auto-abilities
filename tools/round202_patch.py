#!/usr/bin/env python3
"""Round 202 (user 2026-11-22: "Yes, build the probe"), both copies: THE WAVE PROBE, a console command of the TEST build.

    zz_wave(deg, fwd, side, key)

orders the ONE selected unit to cast its wave ability in the GROUND form at a point near the nearest visible enemy, with
the ORIENTATION argument the mod has always passed as 0:  uc:perform_special_ability_ground(key, point, deg, 0).
It answers (and logs) one WAVE PROBE line: the key, the caster, the target, the point, the compass bearing from the
caster to the target and the orientation it sent. Nothing calls it: it changes no trigger. The release build removes it
(tools/build_release.py DEBUG_GLOBALS).
Backups: docs/backups/round202/pre202_{live,ann}.lua."""
import os
import shutil

LIVE = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"
BK = r"C:\Users\vlady\Desktop\WH3_mod\docs\backups\round202"

ANCHOR = """function zz_all_where()
	return zz_all_set(FOURTH.ALL_OX, FOURTH.ALL_OY)
end
"""
NEW = ANCHOR + """
-- ============================================================================
-- ROUND 202 - THE WAVE PROBE (user 2026-11-22: "Yes, build the probe"). A console
-- command of the TEST build, called by nothing:
--     zz_wave(deg, fwd, side, key)
-- The ONE selected unit casts its wave ability in the GROUND form at a point near
-- the nearest enemy we can see, with the ORIENTATION argument the mod has always
-- sent as 0. The question it answers in a battle: does that argument steer the
-- wave, and where does the wave start relative to the point?
--   deg   the orientation sent (compass degrees; nil = the bearing from the caster
--         to the target, which the answer line prints)
--   fwd   metres to move the point along the caster-to-target line (+ = further)
--   side  metres to move the point to the right of that line
--   key   an ability key (nil = the first ready key of the wave table the unit owns)
-- The answer is one WAVE PROBE line (also written to the log).
-- ============================================================================
function zz_wave(deg, fwd, side, key)
	local function say(m)
		FOURTH.all_said(m)
		return m
	end
	local targets = FOURTH.all_targets()
	if #targets ~= 1 then return say("WAVE PROBE: select exactly ONE unit (" .. tostring(#targets) .. " selected)") end
	local want = tostring(targets[1])
	local su = nil
	pcall(function()
		local coll = bm:get_scriptunits_for_local_players_army()
		for i = 1, coll:count() do
			local s = coll:item(i)
			if s ~= nil and s.unit ~= nil and tostring(s.unit:unique_ui_id()) == want then su = s end
		end
	end)
	if su == nil or su.uc == nil then return say("WAVE PROBE: unit " .. want .. " was not found in our army") end
	if key == nil then
		-- the unit's OWN entries only (the engine answers "can perform" loosely): the first ready key of the wave table
		local list = owned_abilities_by_unit[want] or {}
		for i = 1, #list do
			for j = 1, #(list[i].keys or {}) do
				local k = list[i].keys[j]
				if key == nil and FOURTH.WW[k] ~= nil then
					local ok, can = pcall(function() return su.unit:can_perform_special_ability(k) end)
					if ok and can == true then key = k end
				end
			end
		end
	end
	if key == nil then return say("WAVE PROBE: unit " .. want .. " has no ready ability of the wave table") end
	local cx, cz = FOURTH.self_xz(su.unit)
	if cx == nil then return say("WAVE PROBE: the caster's position is unreadable") end
	local m = FOURTH.blob_map(true)
	local best, bd = nil, nil
	for i = 1, #m.all do
		local e = m.all[i]
		local d = math.sqrt((e.x - cx) ^ 2 + (e.z - cz) ^ 2)
		if bd == nil or d < bd then best, bd = e, d end
	end
	if best == nil or bd < 0.5 then return say("WAVE PROBE: no enemy in sight") end
	local hx, hz = (best.x - cx) / bd, (best.z - cz) / bd
	local bearing = math.deg((math.atan2 or math.atan)(hx, hz))
	if bearing < 0 then bearing = bearing + 360 end
	fwd, side = tonumber(fwd) or 0, tonumber(side) or 0
	deg = tonumber(deg) or bearing
	local px = best.x + hx * fwd + hz * side
	local pz = best.z + hz * fwd - hx * side
	local pos, how = nil, "the enemy's own position"
	if fwd == 0 and side == 0 then
		pcall(function() pos = best.unit:position() end)
	else
		how = "a built point"
		local h = 0
		pcall(function() h = bm:get_terrain_height(px, pz) end)
		pcall(function() pos = v(px, tonumber(h) or 0, pz) end)
	end
	if pos == nil then return say("WAVE PROBE: the point could not be built (" .. how .. ")") end
	local etype = "?"
	pcall(function() etype = tostring(best.unit:type()) end)
	local ok, err = pcall(function() su.uc:perform_special_ability_ground(key, pos, deg, 0) end)
	return say(string.format("WAVE PROBE: %s by unit %s at (%.1f,%.1f) -> %s at (%.1f,%.1f), %.1f m away; point (%.1f,%.1f) = %s; "
		.. "bearing caster->target %.0f; ORIENTATION SENT %.0f; order %s",
		tostring(key), want, cx, cz, etype, best.x, best.z, bd, px, pz, how, bearing, deg,
		ok and "accepted" or ("REFUSED: " .. tostring(err))))
end
"""


def patch(path):
    s = open(path, encoding="utf-8", newline="").read()
    assert "function zz_wave(" not in s, "already patched: " + path
    assert s.count(ANCHOR) == 1, (path, s.count(ANCHOR))
    s = s.replace(ANCHOR, NEW)
    open(path, "w", encoding="utf-8", newline="").write(s)
    print("patched", path)


def main():
    os.makedirs(BK, exist_ok=True)
    for src, name in ((LIVE, "pre202_live.lua"), (ANN, "pre202_ann.lua")):
        dst = os.path.join(BK, name)
        if not os.path.exists(dst):
            shutil.copy2(src, dst)
    patch(LIVE)
    patch(ANN)


if __name__ == "__main__":
    main()
