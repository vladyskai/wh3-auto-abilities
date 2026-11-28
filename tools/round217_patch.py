#!/usr/bin/env python3
"""Round 217 (2026-11-28, tuning: the two costs the round-216 battle left). No cast decision changes.

FIELD (the round-216 build, archive/logs/battle_20261128_r216_perf.txt, 139 s, 21 units): 62 ms of every second. The
game's Find answers SA_dial: a dial walk visits 12 components (empty) or 52 (a wheel), not 770. But 40 times the whole
HUD followed the dial walk and 39 of those found nothing: all on GROUPS (8 units, 21 units, the two owners together).
A group's wheel shows only the abilities EVERY selected unit owns, so the letter the mod waited for could not come.
The unit cards cost 33 to 85 ms per second for the 57 s before the first selection event, then 10 to 30.

1. FOURTH.walk_again: with several units selected, the whole-HUD walk follows the dial walk only for an ability that
   EVERY selected unit owns and that has no letter yet (FOURTH.walk_group_waiting).
2. FOURTH.cards_due: the unit cards are read every 4th UI tick as soon as the game ACCEPTED a selection callback
   (cast_gate.sel_registered, set where the registration is accepted), not only after the first event arrived. Where
   the game has no selection API the cards are read on every tick as before.
Backups: docs/backups/round217/pre217_{live,ann}.lua."""
import os
import shutil
import sys

LIVE = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"
BK = r"C:\Users\vlady\Desktop\WH3_mod\docs\backups\round217"

A_REG = "\t\t\t\t\t\tselection_callbacks_by_ui_id[tostring(ui_id)] = true\n"
N_REG = A_REG + "\t\t\t\t\t\tcast_gate.sel_registered = true   -- ROUND 217: the game took a selection callback\n"

A_CARDS = "\tif selection_callback_alive ~= true then return true end\n\treturn (t % 4) == 0\n"
N_CARDS = ("\tif selection_callback_alive ~= true and cast_gate.sel_registered ~= true then return true end   -- ROUND 217\n"
           "\treturn (t % 4) == 0\n")

A_WAIT = ("\tif selection_callback_alive == true then\n"
          "\t\tfor i = 1, #selected_ui_ids do\n"
          "\t\t\tif FOURTH.walk_waiting(selected_ui_ids[i]) then waiting = true end\n"
          "\t\tend\n")
N_WAIT = ("\tif selection_callback_alive == true and #selected_ui_ids > 1 then\n"
          "\t\twaiting = FOURTH.walk_group_waiting()   -- ROUND 217: a group's wheel shows only what every unit owns\n"
          "\telseif selection_callback_alive == true then\n"
          "\t\tfor i = 1, #selected_ui_ids do\n"
          "\t\t\tif FOURTH.walk_waiting(selected_ui_ids[i]) then waiting = true end\n"
          "\t\tend\n")

A_FN = "function FOURTH.walk_start(hud)\n"
N_FN = """-- ROUND 217: several units selected. The wheel of a group shows only the abilities EVERY selected unit owns, so
-- only such an ability with no letter yet is worth the whole-HUD walk. A unit whose abilities are not read yet
-- counts as waiting (the old behaviour).
function FOURTH.walk_group_waiting()
	local n = #selected_ui_ids
	local seen = {}
	for i = 1, n do
		local list = owned_abilities_by_unit[tostring(selected_ui_ids[i])]
		if list == nil then
			if owned_keys_by_unit[tostring(selected_ui_ids[i])] == nil then return true end
			return false
		end
		for j = 1, #list do
			local m = list[j].marker
			seen[m] = (seen[m] or 0) + 1
			if i == n and seen[m] == n and ability_state[m].button == nil then return true end
		end
	end
	return false
end
""" + A_FN


def one(s, a, b, what):
    assert s.count(a) == 1, (what, s.count(a))
    return s.replace(a, b)


def patch(path):
    s = open(path, encoding="utf-8", newline="").read()
    assert "ROUND 217" not in s, "already patched: " + path
    s = one(s, A_REG, N_REG, "registration")
    s = one(s, A_CARDS, N_CARDS, "cards")
    s = one(s, A_WAIT, N_WAIT, "waiting")
    s = one(s, A_FN, N_FN, "function")
    open(path, "w", encoding="utf-8", newline="").write(s)
    print("patched", path)


def main():
    os.makedirs(BK, exist_ok=True)
    for src, name in ((LIVE, "pre217_live.lua"), (ANN, "pre217_ann.lua")):
        dst = os.path.join(BK, name)
        if not os.path.exists(dst):
            shutil.copy2(src, dst)
        elif "--again" in sys.argv:
            shutil.copy2(dst, src)
    patch(LIVE)
    patch(ANN)


if __name__ == "__main__":
    main()
