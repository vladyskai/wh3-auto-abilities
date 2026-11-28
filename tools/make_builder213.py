#!/usr/bin/env python3
"""Build the round-213 build script from the round-212 one (tuning: the cost of a selection).
ROUND 213 GATE: FOURTH.brisk_due exists once, is used once (the missing-claim branch), the two old cadences and the
5 s safety net are still there."""

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261122_transform_harness210\build_and_install212.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261128_selectcost_harness211\build_and_install213.py"
ANCHOR = '      "copy dropped), with the script units as the fallback")\n'
ADD = ANCHOR + r'''# ROUND 213 (tuning): a unit whose button never came is remembered, its later selections retry once.
assert script_txt.count("\nfunction FOURTH.brisk_due(t, window_end, walk)\n") == 1 \
    and script_txt.count("FOURTH.brisk_due(") == 2 \
    and "\t\t\t\twalk_now = (ui_ticks % 4) == 0\n\t\t\t\twalk_now = FOURTH.brisk_due(ui_ticks, brisk_walk_until, walk_now)" in script_txt \
    and script_txt.count("walk_now = (ui_ticks % 2) == 0") == 1 \
    and script_txt.count("walk_now = (ui_ticks % 100) == 0") == 3 \
    and "\tif t == window_end then FOURTH.walk_quiet[id] = true end\n" in script_txt, \
    "BUILD REFUSED (round 213): the walk memory is not wired, or a cadence or the safety net moved"
print("ROUND 213 GATE OK: a unit whose button never came in a whole window retries once on later selections")
'''


def main():
    src = open(SRC, encoding="utf-8").read()
    assert src.count(ANCHOR) == 1, src.count(ANCHOR)
    src = src.replace(ANCHOR, ADD).replace("20261122_transform_harness210", "20261128_selectcost_harness211")
    open(DST, "w", encoding="utf-8", newline="\n").write(src)
    print("wrote", DST)


if __name__ == "__main__":
    main()
