#!/usr/bin/env python3
"""Build the round-217 build script from the round-216 one (tuning: the group walk, the card cadence).
ROUND 217 GATE: the group rule exists once and is used once, the registration flag is set where the game accepts a
callback, the cards keep the every-tick read where no callback was accepted."""

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261128_walkscope_harness214\build_and_install216.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261128_groupcards_harness215\build_and_install217.py"
ANCHOR = ('print("ROUND 216 GATE OK: the HUD walk starts at the ability dial (the whole HUD when the dial is not found, on the "\n'
          '      "5 s net, and when a selected unit still waits); no walk while no selected unit owns one of our abilities")\n')
ADD = ANCHOR + r'''# ROUND 217 (tuning): a group's wheel shows only shared abilities, the cards 5 times a second once a callback is accepted.
assert script_txt.count("\nfunction FOURTH.walk_group_waiting()\n") == 1 \
    and script_txt.count("\t\twaiting = FOURTH.walk_group_waiting()") == 1 \
    and script_txt.count("cast_gate.sel_registered = true") == 1 \
    and "\t\t\t\t\t\tselection_callbacks_by_ui_id[tostring(ui_id)] = true\n\t\t\t\t\t\tcast_gate.sel_registered = true" in script_txt \
    and "\tif selection_callback_alive ~= true and cast_gate.sel_registered ~= true then return true end" in script_txt \
    and "\tif selection_callback_alive == true and #selected_ui_ids > 1 then\n" in script_txt, \
    "BUILD REFUSED (round 217): the group rule or the card cadence is not wired as tested"
print("ROUND 217 GATE OK: with several units selected the whole-HUD walk waits only for an ability every selected unit "
      "owns; the unit cards are read 5 times a second once the game accepted a selection callback")
'''


def main():
    src = open(SRC, encoding="utf-8").read()
    assert src.count(ANCHOR) == 1, src.count(ANCHOR)
    # REBASE: the round-215 gate pinned the card line that round 217 changes (the registration flag joins it)
    old = r'''    and "\tif selection_callback_alive ~= true then return true end\n\treturn (t % 4) == 0\n" in script_txt, \
'''
    new = r'''    and "\tif selection_callback_alive ~= true and cast_gate.sel_registered ~= true then return true end   -- ROUND 217\n\treturn (t % 4) == 0\n" in script_txt, \
'''
    assert src.count(old) == 1, src.count(old)
    src = src.replace(old, new)
    src = src.replace(ANCHOR, ADD).replace("20261128_walkscope_harness214", "20261128_groupcards_harness215")
    open(DST, "w", encoding="utf-8", newline="\n").write(src)
    print("wrote", DST)


if __name__ == "__main__":
    main()
