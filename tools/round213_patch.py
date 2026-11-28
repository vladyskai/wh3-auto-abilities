#!/usr/bin/env python3
"""Round 213 (2026-11-28, tuning: the cost of a selection). No cast decision changes.

FIELD (a Workshop comment, 2026-11-26): "it does add quite a bit of framerate lag ... when selecting any own unit or
unit groups during ongoing battle", on a setup with overhauls and an ability-wheel UI mod.

WHAT THE MOD DID ON A SELECTION. Every selection change walks the whole battle HUD (600+ components, several reads
each) to find the ability buttons. While one ability of the selected unit has no button (a key the wheel does not
show, or a wheel another mod rebuilt), the walk is repeated every 4th UI tick for 48 ticks: 12 more full walks in
2.4 s, on EVERY selection of that unit, for the whole battle.

THE CHANGE. A unit whose button was still missing at the END of a whole 48-tick window is remembered
(FOURTH.walk_quiet). Its later selections walk at once and retry once, 4 ticks later: 2 walks instead of 13. The
first window of every unit, the immediate walk on the event and the 5 s safety net are unchanged, so a letter that
appears late is found exactly as before.
Backups: docs/backups/round213/pre213_{live,ann}.lua."""
import os
import shutil
import sys

LIVE = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"
BK = r"C:\Users\vlady\Desktop\WH3_mod\docs\backups\round213"

A_TICK = "local function ui_tick()\n"
N_FN = """-- ============================================================================
-- ROUND 213 - THE COST OF A SELECTION (a Workshop comment, 2026-11-26: lag when
-- selecting units). While a button of the selected unit is missing, the HUD
-- walk is repeated every 4th UI tick for the 48-tick window after the
-- selection: 12 full walks, on every selection of that unit. A unit whose
-- button was still missing on the LAST tick of a window is remembered
-- (FOURTH.walk_quiet): from then on a selection of it retries once, 4 ticks
-- after the event. The first window, the immediate walk and the 5 s safety net
-- are unchanged.
-- ============================================================================
FOURTH.walk_quiet = {}
function FOURTH.brisk_due(t, window_end, walk)
	if window_end < 0 then return walk end
	local id = tostring(selected_unit_id)
	if FOURTH.walk_quiet[id] == true then return (t - (window_end - 48)) == 4 end
	if t == window_end then FOURTH.walk_quiet[id] = true end
	return walk
end

""" + A_TICK

A_OWN = "\t\t\t\twalk_now = (ui_ticks % 4) == 0\n"
N_OWN = A_OWN + ("\t\t\t\twalk_now = FOURTH.brisk_due(ui_ticks, brisk_walk_until, walk_now)   -- ROUND 213: a unit whose "
                 "button never came retries once\n")


def one(s, a, b, what):
    assert s.count(a) == 1, (what, s.count(a))
    return s.replace(a, b)


def patch(path):
    s = open(path, encoding="utf-8", newline="").read()
    assert "ROUND 213" not in s, "already patched: " + path
    s = one(s, A_TICK, N_FN, "function")
    s = one(s, A_OWN, N_OWN, "unclaimed cadence")
    open(path, "w", encoding="utf-8", newline="").write(s)
    print("patched", path)


def main():
    os.makedirs(BK, exist_ok=True)
    for src, name in ((LIVE, "pre213_live.lua"), (ANN, "pre213_ann.lua")):
        dst = os.path.join(BK, name)
        if not os.path.exists(dst):
            shutil.copy2(src, dst)
        elif "--again" in sys.argv:
            shutil.copy2(dst, src)
    patch(LIVE)
    patch(ANN)


if __name__ == "__main__":
    main()
