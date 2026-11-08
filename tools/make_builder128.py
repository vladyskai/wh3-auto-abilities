#!/usr/bin/env python3
"""Build the round-128 build script from the round-127 one. No count pin moves.
Adds one gate: fix A (a charge hold released only for the one engine-selected
unit whose button reads READY) and the read-only NOT FIRING snapshot are in."""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261103_off_window_target_lost_harness126\build_and_install127.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261103_ready_on_screen_harness127\build_and_install128.py"

ANCHOR = 'print("ROUND 127 GATE OK: OFF = max(2 x reload, 20 s); a lost target is logged, not formatted")\n'
ADD = ANCHOR + '''# ROUND 128: fix A (dropped multi-use casts) and the NOT FIRING snapshot.
assert "function FOURTH.charge_hold_ready_on_screen(ui_id, ability, held_until)" in script_txt \\
    and "if #selected_ui_ids ~= 1 or tostring(selected_ui_ids[1]) ~= tostring(ui_id) then return false end" in script_txt, \\
    "fix A is missing, or it trusts something other than the engine's single live selection"
assert "function FOURTH.not_firing_snapshot(u, st, now_s, inr, d, r)" in script_txt, "the NOT FIRING snapshot is missing"
print("ROUND 128 GATE OK: fix A (engine-selected unit, READY button) and the NOT FIRING snapshot are in")
'''
src = open(SRC, encoding="utf-8").read()
assert src.count(ANCHOR) == 1
src = src.replace(ANCHOR, ADD)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST)
