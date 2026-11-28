#!/usr/bin/env python3
"""Round 216 (2026-11-28, tuning: the cost of the HUD walk, measured). No cast decision changes.

FIELD (the round-215 build, archive/logs/battle_20261128_r215_perf.txt, 123 s, 21 units): the mod took 71 ms of every
second (124 before). 157 HUD walks at 18.3 ms each (770 components), the worst UI ticks 60 to 63 ms. 142 of the 159
logged walks found NOTHING: 43 ran right after the selection became empty, about 20 after selecting a unit that owns
none of our abilities, 26 on a group.

1. THE WALK STARTS AT THE ABILITY DIAL (FOURTH.walk_start): root:Find("SA_dial", false), the pattern the inventory
   sweep has used in every battle. When the dial is not found, on the 5 s safety net, and when the dial walk claimed
   nothing while a selected unit still waits for a letter (FOURTH.walk_again), the whole hud_battle is walked as
   before. The test build logs 'scan scope: dial' once per battle and 'scan scope: the whole HUD after the dial'.
2. NO WALK WHEN NOTHING OF OURS CAN BE ON THE DIAL (FOURTH.walk_useful): once the game's selection events are alive,
   a walk is skipped while no selected unit owns one of our abilities (an empty selection included). The 5 s safety
   net stays. A selected unit whose abilities are not read yet keeps the walk.
Backups: docs/backups/round216/pre216_{live,ann}.lua."""
import os
import shutil
import sys

LIVE = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"
BK = r"C:\Users\vlady\Desktop\WH3_mod\docs\backups\round216"

A_TICK = "local function ui_tick()\n"
N_FN = """-- ============================================================================
-- ROUND 216 - THE COST OF THE HUD WALK (measured on the round-215 build: 157
-- walks in 123 s at 18 ms each, 142 of 159 found nothing).
-- FOURTH.walk_useful: once the game's selection events are alive, no walk while
-- no selected unit owns one of our abilities (the 5 s safety net stays).
-- FOURTH.walk_start: the walk starts at the ability dial (SA_dial), found with
-- the engine's own Find, the way the inventory sweep finds it. The whole HUD is
-- walked when the dial is not found, on the safety net, and (FOURTH.walk_again)
-- when the dial walk claimed nothing while a selected unit waits for a letter.
-- ============================================================================
function FOURTH.walk_useful(walk, t)
	FOURTH.walk_net = ((t % 100) == 0)
	if walk ~= true or FOURTH.walk_net then return walk end
	if selection_callback_alive ~= true then return walk end
	for i = 1, #selected_ui_ids do
		local id = tostring(selected_ui_ids[i])
		if owned_keys_by_unit[id] == nil then return walk end
		local list = owned_abilities_by_unit[id]
		if list ~= nil and #list > 0 then return walk end
	end
	return false
end
function FOURTH.walk_claims()
	local n = 0
	local list = active_abilities_list()
	for i = 1, #list do   -- no ipairs here: harness 78 counts the paths that iterate the active list
		local state = ability_state[list[i].marker]
		if state ~= nil and state.button ~= nil then n = n + 1 end
	end
	return n
end
function FOURTH.walk_waiting(id)
	local list = owned_abilities_by_unit[tostring(id)]
	if list == nil then return false end
	for _, ability in ipairs(list) do
		if ability_state[ability.marker].button == nil then return true end
	end
	return false
end
function FOURTH.walk_start(hud)
	local net = FOURTH.walk_net
	FOURTH.walk_net = nil
	FOURTH.walk_scoped = false
	FOURTH.walk_before = FOURTH.walk_claims()
	if net == true then return hud end
	local ok, dial = pcall(function()
		local raw = core:get_ui_root():Find("SA_dial", false)   -- false = do not assert when missing
		if raw == nil or raw == false then return nil end
		local d = UIComponent(raw)
		if d == nil or d:Id() ~= "SA_dial" then return nil end
		return d
	end)
	if not ok or dial == nil then return hud end
	FOURTH.walk_scoped = true
@LOG1@
	return dial
end
function FOURTH.walk_again()
	if FOURTH.walk_scoped ~= true then return false end
	FOURTH.walk_scoped = false
	if FOURTH.walk_claims() > FOURTH.walk_before then return false end
	local waiting = false
	if selection_callback_alive == true then
		for i = 1, #selected_ui_ids do
			if FOURTH.walk_waiting(selected_ui_ids[i]) then waiting = true end
		end
	elseif selected_unit_id ~= nil then
		waiting = FOURTH.walk_waiting(selected_unit_id)
	end   -- nothing selected that we know of: no wheel is shown, the dial walk was enough (the 5 s net walks it all)
@LOG2@
	return waiting
end

""" + A_TICK
LOG1_LIVE = ('\tif FOURTH.walk_scope_said ~= true then\n'
             '\t\tFOURTH.walk_scope_said = true\n'
             '\t\tlog("scan scope: dial (the walk starts at SA_dial, the whole HUD only as a fallback)")\n'
             '\tend')
LOG1_ANN = "\t-- (the live copy logs 'scan scope: dial' once per battle here)"
LOG2_LIVE = '\tif waiting then log("scan scope: the whole HUD after the dial (a selected unit still waits for a letter)") end'
LOG2_ANN = "\t-- (the live copy logs 'scan scope: the whole HUD after the dial' here)"

A_SCAN = "\t\tscan_component(hud, 0)\n"
N_SCAN = ("\t\tscan_component(FOURTH.walk_start(hud), 0)   -- ROUND 216: the dial first\n"
          "\t\tif FOURTH.walk_again() then\n"
          "\t\tscan_component(hud, 0)\n"
          "\t\tend\n")
A_GATE = "\t\t\twalk_now = (ui_ticks % 100) == 0\n\t\tend\n\t\tif walk_now then\n"
N_GATE = ("\t\t\twalk_now = (ui_ticks % 100) == 0\n\t\tend\n"
          "\t\twalk_now = FOURTH.walk_useful(walk_now, ui_ticks)   -- ROUND 216: no walk while nothing of ours can be on the dial\n"
          "\t\tif walk_now then\n")


def one(s, a, b, what):
    assert s.count(a) == 1, (what, s.count(a))
    return s.replace(a, b)


def patch(path, live):
    s = open(path, encoding="utf-8", newline="").read()
    assert "ROUND 216" not in s, "already patched: " + path
    fn = N_FN.replace("@LOG1@", LOG1_LIVE if live else LOG1_ANN).replace("@LOG2@", LOG2_LIVE if live else LOG2_ANN)
    s = one(s, A_TICK, fn, "functions")
    s = one(s, A_SCAN, N_SCAN, "scan")
    s = one(s, A_GATE, N_GATE, "gate")
    open(path, "w", encoding="utf-8", newline="").write(s)
    print("patched", path)


def main():
    os.makedirs(BK, exist_ok=True)
    for src, name in ((LIVE, "pre216_live.lua"), (ANN, "pre216_ann.lua")):
        dst = os.path.join(BK, name)
        if not os.path.exists(dst):
            shutil.copy2(src, dst)
        elif "--again" in sys.argv:
            shutil.copy2(dst, src)
    patch(LIVE, True)
    patch(ANN, False)


if __name__ == "__main__":
    main()
