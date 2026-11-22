#!/usr/bin/env python3
"""Round 212 (2026-11-22): A TRANSFORMED UNIT IS A NEW UNIT. THE WATCH LIST COMES FROM THE ARMY'S OWN UNIT LIST.

FIELD (the round-211 raw probe, archive/logs/battle_20261122_r211_rawprobe.txt): after Tz'arkan the army's own list
(bm:alliances() -> armies() -> units()) holds ONE unit with a NEW id (1002, type wh2_dlc14_def_cha_malus_darkblade_
tzarkan_0, the keys Bloodstorm and Reaper of Souls, moving, in melee). The script-unit list the mod has always read
(bm:get_scriptunits_for_local_players_army()) keeps answering the old unit 1001, frozen.

THE FIX. The periodic re-list builds its items from bm:get_player_army():units():
  - a unit the script-unit list also has (the same id) keeps its script unit, exactly as before
  - a unit only the army lists (a transformed unit, a summon in the player's army) gets a script unit made by the mod:
    { unit, uc = army:create_unit_controller() with the unit added }. No controller, no unit: it is left out
  - a script unit whose id the army no longer lists is a GHOST: it is left out, so the existing drop removes it (it no
    longer casts, and no longer counts as one of our units in the friendly-fire tests)
  - an unreadable or empty army list changes nothing: the script units alone, as before
The fresh-handle fetchers (FOURTH.eg_fresh_caster_su, FOURTH.ab_fresh_friend_su) fall back to the mod-made script unit.
The re-list also runs 2 s after any cast (the mod's or the player's), so a transformation is picked up at once
instead of at the next 10 s boundary.
Backups: docs/backups/round212/pre212_{live,ann}.lua."""
import os
import shutil
import sys

LIVE = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"
BK = r"C:\Users\vlady\Desktop\WH3_mod\docs\backups\round212"

A_KEYS = "\nlocal ALL_ABILITY_KEYS = {}\n"
N_RAW = """
-- ============================================================================
-- ROUND 212 - THE WATCH LIST COMES FROM THE ARMY'S OWN UNIT LIST. A transformed
-- unit is a NEW unit with a new id (field 2026-11-22: Malus Darkblade 1001 ->
-- Tz'arkan 1002). The army's own list has it, the script-unit list keeps the
-- old one, frozen. cast_gate.raw_items answers the script units to watch:
--   the same id in both lists -> the game's script unit, as before
--   only in the army's list   -> a script unit made here (the unit + a new
--                                controller); without a controller it is left out
--   only in the script units  -> a ghost: left out, the re-list drops it
-- An unreadable or empty army list -> the script units alone, as before.
-- (These live on cast_gate because the watch-list builder sits above the
-- FOURTH table and the main chunk has no room for another local.)
-- ============================================================================
cast_gate.raw_sunits = {}   -- unit id (text) -> the script unit made here
cast_gate.ghosts = {}       -- unit id (text) -> true once the army's own list no longer had it
function cast_gate.raw_items(sunits, total)
	local items, revive, by_id = {}, {}, {}
	for i = 1, total do
		local su = sunits:item(i)
		items[i] = su
		pcall(function() by_id[tostring(su.unit:unique_ui_id())] = su end)
	end
	local raw = nil
	pcall(function()
		local army = bm:get_player_army()
		local units = army:units()
		local n = units:count()
		local list = {}
		for u = 1, n do
			local x = units:item(u)
			list[u] = { unit = x, id = tostring(x:unique_ui_id()), army = army }
		end
		if n >= 1 then raw = list end
	end)
	if raw == nil then return items, revive end
	local out, seen = {}, {}
	for u = 1, #raw do
		local r = raw[u]
		seen[r.id] = true
		local su = by_id[r.id]
		if su ~= nil and cast_gate.ghosts[r.id] ~= true then
			out[#out + 1] = su
		else
			local made = cast_gate.raw_sunits[r.id]
			if made == nil then
				pcall(function()
					local uc = r.army:create_unit_controller()
					uc:add_units(r.unit)
					made = { unit = r.unit, uc = uc, zz_raw = true }
				end)
				if made ~= nil then cast_gate.raw_sunits[r.id] = made end
			end
			if made ~= nil then
				out[#out + 1] = made
				-- an id that was dropped as a ghost and is back alive in the army's list may be watched again
				if cast_gate.ghosts[r.id] == true then
					local ok_m, men = pcall(function() return r.unit:number_of_men_alive() end)
					if ok_m and type(men) == "number" and men > 0 then revive[#revive + 1] = r.id end
				end
			end
		end
	end
	for id, _ in pairs(by_id) do
		if seen[id] ~= true then cast_gate.ghosts[id] = true end
	end
	return out, revive
end
""" + A_KEYS

A_LOOP_LIVE = "\tfor i = 1, total do\n\t\tlocal script_unit = sunits:item(i)\n"
A_LOOP_ANN = "\tfor i = 1, total do\n\t\tlocal script_unit = sunits:item(i)   -- one script unit: the unit + its order controller\n"
N_LOOP = ("\t-- ROUND 212: the units to watch come from the army's own list (a transformed unit is a new unit there)\n"
          "\tlocal items, revive = cast_gate.raw_items(sunits, total)\n"
          "\tfor r = 1, #revive do gone_units[revive[r]] = nil end\n"
          "\tfor i = 1, #items do\n\t\tlocal script_unit = items[i]\n")

A_FETCH = "if id ~= nil and tostring(id) == want then return su end\n\t\t\tend\n\t\tend\n\tend\n\treturn nil\nend\n"
N_FETCH = ("if id ~= nil and tostring(id) == want then return su end\n\t\t\tend\n\t\tend\n\tend\n"
           "\treturn cast_gate.raw_sunits[want]   -- ROUND 212: a unit only the army's own list has (nil when unknown)\nend\n")

A_RELIST = "\tif (tick_count % RELIST_EVERY_N_POLLS) == 0 then\n\t\trebuild_unit_list()\n\tend\n"
N_RELIST = A_RELIST + ("\t-- ROUND 212: and 2 s after any cast (it may have been a transformation: the unit is then a new one)\n"
                       "\tif FOURTH.relist_at ~= nil and tick_count >= FOURTH.relist_at then\n"
                       "\t\tFOURTH.relist_at = nil\n"
                       "\t\trebuild_unit_list()\n"
                       "\tend\n")
A_SOON = "function FOURTH.rescan_soon(id_text)\n\tif id_text == nil then return end\n"
N_SOON = "function FOURTH.rescan_soon(id_text)\n\tFOURTH.relist_at = tick_count + 8   -- ROUND 212: the watch list too\n\tif id_text == nil then return end\n"


def one(s, a, b, what):
    assert s.count(a) == 1, (what, s.count(a))
    return s.replace(a, b)


def patch(path, live):
    s = open(path, encoding="utf-8", newline="").read()
    assert "ROUND 212" not in s, "already patched: " + path
    s = one(s, A_KEYS, N_RAW, "raw items")
    s = one(s, A_LOOP_LIVE if live else A_LOOP_ANN, N_LOOP, "loop")
    assert s.count(A_FETCH) == 2
    s = s.replace(A_FETCH, N_FETCH)
    s = one(s, A_RELIST, N_RELIST, "relist")
    s = one(s, A_SOON, N_SOON, "soon")
    open(path, "w", encoding="utf-8", newline="").write(s)
    print("patched", path)


def main():
    os.makedirs(BK, exist_ok=True)
    for src, name in ((LIVE, "pre212_live.lua"), (ANN, "pre212_ann.lua")):
        dst = os.path.join(BK, name)
        if not os.path.exists(dst):
            shutil.copy2(src, dst)
        elif "--again" in sys.argv:
            shutil.copy2(dst, src)
    patch(LIVE, True)
    patch(ANN, False)


if __name__ == "__main__":
    main()
