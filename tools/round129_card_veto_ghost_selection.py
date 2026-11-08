#!/usr/bin/env python3
"""Round 129 (harness 128): the unit cards veto a ghost selection.

Field battle 3, 2026-11-03 (docs/WH3_round128_field_analysis.md): the user box-selected
seven characters, then clicked Kalara alone. The engine's selection callback never sent the
six "deselected" events, so 1006 and 1007 stayed in selected_ui_ids for the rest of the
battle ("1003, 1006, 1007"). Fix A needs exactly one selected unit, so it never released
Isha's Rain's hold (about 155 s of a ready ability unused). The unit cards were right the
whole time: 1006 and 1007 read 'active'. User ruling 2026-11-03: "Selection fix only".

The change: in the card reconciliation, an id in the selected set whose card is FOUND and
reads a known UNSELECTED state (active, hover, inactive, taking_damage, wavering: every
unselected state seen in battle) for at least CARD_DESELECT_CONFIRM_POLLS polls is dropped.
No string.find (the mod's standing ban) and no dial walk (the dial already shows the real
selection; the walk-path pin stays at 7). The short confirmation keeps a fresh
selection whose card has not caught up yet. A card not found, or an unreadable state, is
no evidence and drops nothing.
"""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"

CONST_ANCHOR = "local function read_tracked_card_states()\n"
CONST = """-- ROUND 129: the cards veto a ghost selection (see the reconciliation below).
FOURTH.CARD_DESELECT_CONFIRM_POLLS = 2   -- 2 x 250 ms: a card must read unselected this long
FOURTH.card_unselected_since = {}        -- id -> the poll its card first read unselected
-- The card states that mean "NOT selected" (every one seen in the 2026-11-03
-- battles). Any other state (the selected ones, '?', or one never seen) drops nothing.
FOURTH.CARD_UNSELECTED_STATES = { active = true, hover = true, inactive = true, taking_damage = true, wavering = true }

"""


def veto(with_log):
    lg = ""
    if with_log:
        lg = """
						log(string.format("selection: card %s reads '%s' - the game never sent its deselection; dropped from the selected set (%d selected now)",
							tostring(id), st, #selected_ui_ids))"""
    return """			-- ROUND 129: THE CARDS VETO A GHOST SELECTION. After a box
			-- selection the engine may never send the "deselected" events
			-- (field battle 2026-11-03: seven selected, then one clicked,
			-- two ghosts stayed for the rest of the battle and fix A never
			-- saw "exactly one selected"). A unit whose own card reads a
			-- known UNSELECTED state for CARD_DESELECT_CONFIRM_POLLS polls
			-- is not selected: drop it. A card not found, or any other
			-- state, is no evidence and drops nothing.
			for i = #selected_ui_ids, 1, -1 do
				local id = selected_ui_ids[i]
				local st = states[id]
				if st ~= nil and FOURTH.CARD_UNSELECTED_STATES[st] == true then
					local since = FOURTH.card_unselected_since[id]
					if since == nil then
						FOURTH.card_unselected_since[id] = tick_count
					elseif (tick_count - since) >= FOURTH.CARD_DESELECT_CONFIRM_POLLS then
						table.remove(selected_ui_ids, i)
						FOURTH.card_unselected_since[id] = nil
						reconciled_card_ids[id] = nil
						selection_set_dirty = true""" + lg + """
					end
				else
					FOURTH.card_unselected_since[id] = nil
				end
			end
"""


TAIL = ("\t\t\t\t\t\tif selected_ui_ids[i] == id then\n\t\t\t\t\t\t\ttable.remove(selected_ui_ids, i)\n"
        "\t\t\t\t\t\t\tselection_set_dirty = true\n\t\t\t\t\t\tend\n\t\t\t\t\tend\n\t\t\t\tend\n\t\t\tend\n")
SRC_TAIL = TAIL + "\t\tend\n\tend\n\n\treturn ordered, found, states, selected\nend\n"
ANN_TAIL = TAIL + "\t\tend\n\tend\n\n\treturn selected\nend\n"

ANN_STATES_OLD = "\tlocal selected = {}\n\tfor i = 1, #ordered do\n"
ANN_STATES_NEW = "\tlocal states = {}     -- ROUND 129: id -> the card's state, for the ghost veto\n" + ANN_STATES_OLD
ANN_STATE_OLD = "\t\t\tif ok_s and type(s) == \"string\" then state = s end\n\t\t\tif state == \"selected\" then\n"
ANN_STATE_NEW = "\t\t\tif ok_s and type(s) == \"string\" then state = s end\n\t\t\tstates[ui_id] = state\n\t\t\tif state == \"selected\" then\n"

PLAN = {
    SRC: [(CONST_ANCHOR, CONST + CONST_ANCHOR),
          (SRC_TAIL, TAIL + veto(True) + SRC_TAIL[len(TAIL):])],
    ANN: [(CONST_ANCHOR, CONST + CONST_ANCHOR), (ANN_STATES_OLD, ANN_STATES_NEW), (ANN_STATE_OLD, ANN_STATE_NEW),
          (ANN_TAIL, TAIL + veto(False) + ANN_TAIL[len(TAIL):])],
}
for path, edits in PLAN.items():
    s = open(path, encoding="utf-8", newline="").read()
    assert "\r\n" not in s and "CARD_DESELECT_CONFIRM_POLLS" not in s, path
    for i, (a, b) in enumerate(edits, 1):
        n = s.count(a)
        assert n == 1, (path.split("\\")[-1], "edit", i, "anchor count", n)
        s = s.replace(a, b, 1)
    assert "\u2014" not in "".join(b for _, b in edits)
    if path == ANN:
        assert "log(" not in veto(False)
    open(path, "w", encoding="utf-8", newline="").write(s)
    print("applied %d edits:" % len(edits), path.split("\\")[-1])
