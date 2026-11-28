#!/usr/bin/env python3
"""Round 215 (2026-11-28, tuning: the mod's own cost, measured). No cast decision changes.

FIELD (the round-214 timing probe, archive/logs/battle_20261128_r214_perf.txt, 147 s, 21 units): the mod took 124 ms
of every second. Before the first selection of the battle (46 s of deployment and start) the HUD walk ran 10 times a
second: 150 ms per second, 15 ms per walk, the worst tick 73 ms. After that the read of every unit card on every UI
tick cost 64 ms per second. The polls cost 5 ms per second.

1. NO WALK STORM BEFORE THE FIRST SELECTION. With nothing selected there is no ability wheel to find. The
   every-2nd-tick walk of the bootstrapping branch now runs for the first 40 UI ticks of the battle only (2 s), then
   falls to the 5 s safety net until a selection opens a window (FOURTH.boot_due).
2. THE UNIT CARDS ARE READ 5 TIMES A SECOND, not 20, once the game's own selection events have arrived
   (selection_callback_alive: the events are the primary source then, the cards are the safety net). Until an event
   has arrived the cards are read on every tick as before (FOURTH.cards_due).
Backups: docs/backups/round215/pre215_{live,ann}.lua."""
import os
import shutil
import sys

LIVE = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"
BK = r"C:\Users\vlady\Desktop\WH3_mod\docs\backups\round215"

A_TICK = "local function ui_tick()\n"
N_FN = """-- ============================================================================
-- ROUND 215 - THE MOD'S OWN COST (measured by the round-214 probe: 124 ms of
-- every second on a 21-unit army). FOURTH.boot_due: before the first selection
-- of a battle the every-2nd-tick HUD walk runs for the first 40 UI ticks only,
-- then the 5 s safety net (it was 10 walks a second for as long as nothing was
-- selected). FOURTH.cards_due: once the game's own selection events arrive, the
-- unit cards are read every 4th UI tick, not every tick.
-- ============================================================================
function FOURTH.boot_due(t, window_end, walk)
	if window_end >= 0 or t <= 40 then return walk end
	return (t % 100) == 0
end
function FOURTH.cards_due(t)
	if selection_callback_alive ~= true then return true end
	return (t % 4) == 0
end

""" + A_TICK
A_BOOT = "\t\t\t\twalk_now = (ui_ticks % 2) == 0\n"
N_BOOT = A_BOOT + ("\t\t\t\twalk_now = FOURTH.boot_due(ui_ticks, brisk_walk_until, walk_now)   -- ROUND 215: no walk storm "
                   "before the first selection\n")
A_CARDS = "\tpcall(fast_card_selection)\n"
N_CARDS = ("\tif FOURTH.cards_due(ui_ticks) then   -- ROUND 215: 5 times a second once the selection events arrive\n"
           "\tpcall(fast_card_selection)\n"
           "\tend\n")


def one(s, a, b, what):
    assert s.count(a) == 1, (what, s.count(a))
    return s.replace(a, b)


def patch(path):
    s = open(path, encoding="utf-8", newline="").read()
    assert "ROUND 215" not in s, "already patched: " + path
    s = one(s, A_TICK, N_FN, "functions")
    s = one(s, A_BOOT, N_BOOT, "boot")
    s = one(s, A_CARDS, N_CARDS, "cards")
    open(path, "w", encoding="utf-8", newline="").write(s)
    print("patched", path)


def main():
    os.makedirs(BK, exist_ok=True)
    for src, name in ((LIVE, "pre215_live.lua"), (ANN, "pre215_ann.lua")):
        dst = os.path.join(BK, name)
        if not os.path.exists(dst):
            shutil.copy2(src, dst)
        elif "--again" in sys.argv:
            shutil.copy2(dst, src)
    patch(LIVE)
    patch(ANN)


if __name__ == "__main__":
    main()
