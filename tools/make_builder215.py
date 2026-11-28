#!/usr/bin/env python3
"""Build the round-215 build script from the round-214 one (tuning: the mod's own cost).
ROUND 215 GATE: FOURTH.boot_due and FOURTH.cards_due exist once and are used once each, the old lines stay, the 5 s
safety net stays."""

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261128_perfprobe_harness212\build_and_install214.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261128_owncost_harness213\build_and_install215.py"
ANCHOR = 'print("ROUND 214 GATE OK: the timing probe measures nine places, in the development build only")\n'
ADD = ANCHOR + r'''# ROUND 215 (tuning): no walk storm before the first selection, the unit cards 5 times a second.
assert script_txt.count("\nfunction FOURTH.boot_due(t, window_end, walk)\n") == 1 \
    and script_txt.count("\nfunction FOURTH.cards_due(t)\n") == 1 \
    and "\t\t\t\twalk_now = (ui_ticks % 2) == 0\n\t\t\t\twalk_now = FOURTH.boot_due(ui_ticks, brisk_walk_until, walk_now)" in script_txt \
    and "\tif FOURTH.cards_due(ui_ticks) then   -- ROUND 215: 5 times a second once the selection events arrive\n" \
        "\tpcall(fast_card_selection)\n\tend\n" in script_txt \
    and "\tif window_end >= 0 or t <= 40 then return walk end\n\treturn (t % 100) == 0\n" in script_txt \
    and "\tif selection_callback_alive ~= true then return true end\n\treturn (t % 4) == 0\n" in script_txt, \
    "BUILD REFUSED (round 215): the walk before the first selection or the card cadence is not wired as measured"
print("ROUND 215 GATE OK: no HUD walk storm before the first selection; the unit cards are read 5 times a second "
      "once the selection events arrive")
'''


def main():
    src = open(SRC, encoding="utf-8").read()
    assert src.count(ANCHOR) == 1, src.count(ANCHOR)
    src = src.replace(ANCHOR, ADD).replace("20261128_perfprobe_harness212", "20261128_owncost_harness213")
    open(DST, "w", encoding="utf-8", newline="\n").write(src)
    print("wrote", DST)


if __name__ == "__main__":
    main()
