#!/usr/bin/env python3
"""Round 211 (2026-11-22, tuning, a READ-ONLY probe in the test build).

FIELD (archive/logs/battle_20261122_r210_malus.txt): after Tz'arkan the mod's handle on Malus Darkblade is FROZEN: the
MAP rows show the same position, hp 1.00 and melee=0 from the transformation to the end of the battle, while the user
fought with the transformed Lord. The unit's ability list read through that handle never changes, so round 210's
re-read finds nothing. The live transformed unit is not reachable through the handle the mod holds.

THE RAW UNIT PROBE (live copy only, log only, called from the map probe, which the release build removes): every 2 s
it walks the game's own lists (bm:alliances() -> armies() -> units()) and writes one RAW line per unit of a
player-controlled army (or of an army whose flag cannot be read), and for any unit whose id the mod tracks: id, type,
position, men, health, melee, whether the object is the SAME one the mod holds, and its keys of ours. Every read is
guarded. It casts nothing and changes no state.
Backups: docs/backups/round211/pre211_live.lua."""
import os
import shutil
import sys

LIVE = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
BK = r"C:\Users\vlady\Desktop\WH3_mod\docs\backups\round211"

A_TICK = "function FOURTH.map_tick(tick)\n"
N_PROBE = """-- ============================================================================
-- ROUND 211 - THE RAW UNIT PROBE (read-only, test build: it runs from the map
-- probe, which the release build removes). After a transformation the handle
-- the mod holds on the unit is frozen (field 2026-11-22, Malus Darkblade: the
-- same position, full health and melee=0 for the rest of the battle). This
-- walks the game's own alliance / army / unit lists every 2 s and writes what
-- it finds, so the next log shows where the transformed unit lives.
-- ============================================================================
FOURTH.raw_probe_failed = false
function FOURTH.raw_read(f)
	local ok, v = pcall(f)
	if ok and v ~= nil then return tostring(v) end
	return "?"
end
function FOURTH.raw_probe(tick)
	if tick % 8 ~= 0 or bm.alliances == nil then return end
	local t = tick * POLL_MS / 1000
	local ok, err = pcall(function()
		local als = bm:alliances()
		for a = 1, als:count() do
			local armies = als:item(a):armies()
			for r = 1, armies:count() do
				local army = armies:item(r)
				local flag = FOURTH.raw_read(function() return army:is_player_controlled() end)
				local units = army:units()
				local n = units:count()
				log(string.format("RAW_ARMY t=%.1f alliance=%d army=%d player=%s units=%d", t, a, r, flag, n))
				for u = 1, n do
					local x = units:item(u)
					local id = FOURTH.raw_read(function() return x:unique_ui_id() end)
					local held = units_by_ui_id[id]
					if flag ~= "false" or held ~= nil then
						local keys = {}
						pcall(function()
							for _, k in pairs(x:owned_special_abilities()) do
								if ALL_ABILITY_KEYS_SET[k] then keys[#keys + 1] = k end
							end
						end)
						log("RAW t=" .. string.format("%.1f", t) .. " alliance=" .. a .. " army=" .. r .. " unit=" .. u
							.. " id=" .. id
							.. " type=" .. FOURTH.raw_read(function() return x:type() end)
							.. " x=" .. FOURTH.raw_read(function() return string.format("%.1f", x:position():get_x()) end)
							.. " z=" .. FOURTH.raw_read(function() return string.format("%.1f", x:position():get_z()) end)
							.. " men=" .. FOURTH.raw_read(function() return x:number_of_men_alive() end)
							.. " hp=" .. FOURTH.raw_read(function() return string.format("%.2f", x:unary_hitpoints()) end)
							.. " melee=" .. FOURTH.raw_read(function() return x:is_in_melee() end)
							.. " held=" .. ((held == nil) and "none" or ((held == x) and "same" or "OTHER"))
							.. " obj=" .. tostring(x) .. " held_obj=" .. tostring(held)
							.. " keys=" .. table.concat(keys, ","))
					end
				end
			end
		end
	end)
	if not ok and not FOURTH.raw_probe_failed then
		FOURTH.raw_probe_failed = true
		log("RAW probe failed (said once): " .. tostring(err))
	end
end

""" + A_TICK + "\tpcall(FOURTH.raw_probe, tick)   -- ROUND 211: read-only\n"


def main():
    os.makedirs(BK, exist_ok=True)
    dst = os.path.join(BK, "pre211_live.lua")
    if not os.path.exists(dst):
        shutil.copy2(LIVE, dst)
    elif "--again" in sys.argv:
        shutil.copy2(dst, LIVE)
    s = open(LIVE, encoding="utf-8", newline="").read()
    assert "ROUND 211" not in s
    assert s.count(A_TICK) == 1
    s = s.replace(A_TICK, N_PROBE)
    open(LIVE, "w", encoding="utf-8", newline="").write(s)
    print("patched", LIVE)


if __name__ == "__main__":
    main()
