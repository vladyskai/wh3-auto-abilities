#!/usr/bin/env python3
"""Build the round-216 build script from the round-215 one (tuning: the cost of the HUD walk).
ROUND 216 GATE: FOURTH.walk_useful, walk_start and walk_again exist once and are used once each, the whole-HUD walk
stays as the fallback, the 5 s safety net always walks the whole HUD."""

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261128_owncost_harness213\build_and_install215.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261128_walkscope_harness214\build_and_install216.py"
ANCHOR = ('print("ROUND 215 GATE OK: no HUD walk storm before the first selection; the unit cards are read 5 times a second "\n'
          '      "once the selection events arrive")\n')
ADD = ANCHOR + r'''# ROUND 216 (tuning): the walk starts at the ability dial, no walk while nothing of ours can be on the dial.
assert script_txt.count("\nfunction FOURTH.walk_useful(walk, t)\n") == 1 \
    and script_txt.count("\nfunction FOURTH.walk_start(hud)\n") == 1 \
    and script_txt.count("\nfunction FOURTH.walk_again()\n") == 1 \
    and script_txt.count("\t\tscan_component(FOURTH.walk_start(hud), 0)   -- ROUND 216: the dial first\n"
                         "\t\tif FOURTH.walk_again() then\n\t\tscan_component(hud, 0)\n\t\tend\n") == 1 \
    and script_txt.count("\t\twalk_now = FOURTH.walk_useful(walk_now, ui_ticks)") == 1 \
    and "\tFOURTH.walk_net = ((t % 100) == 0)\n\tif walk ~= true or FOURTH.walk_net then return walk end\n" in script_txt \
    and "\tif net == true then return hud end\n" in script_txt \
    and 'local raw = core:get_ui_root():Find("SA_dial", false)' in script_txt \
    and "\tif not ok or dial == nil then return hud end\n" in script_txt, \
    "BUILD REFUSED (round 216): the dial walk, its whole-HUD fallback or the 5 s safety net is not wired as tested"
print("ROUND 216 GATE OK: the HUD walk starts at the ability dial (the whole HUD when the dial is not found, on the "
      "5 s net, and when a selected unit still waits); no walk while no selected unit owns one of our abilities")
'''


def main():
    src = open(SRC, encoding="utf-8").read()
    assert src.count(ANCHOR) == 1, src.count(ANCHOR)
    src = src.replace(ANCHOR, ADD).replace("20261128_owncost_harness213", "20261128_walkscope_harness214")
    open(DST, "w", encoding="utf-8", newline="\n").write(src)
    print("wrote", DST)


if __name__ == "__main__":
    main()
