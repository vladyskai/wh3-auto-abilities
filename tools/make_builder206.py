#!/usr/bin/env python3
"""Build the round-206 build script from the round-205 one (tuning: an exact wave's value counts standing enemies only).
ROUND 206 GATE: the value loop reads each enemy's standing state once per map and counts only standing units."""

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261122_cone_harness203\build_and_install205.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261122_standing_harness204\build_and_install206.py"
ANCHOR_HEAD = 'print("ROUND 205 GATE OK: %d growing waves carry their real cone'
ADD = r'''# ROUND 206 (tuning, the user's Sunfang battle 2026-11-22): a walking enemy is not counted in an exact wave's value.
assert "\t\t\tif o.still == nil then o.still = FOURTH.ww_target_still(o) end\n" in _b204 \
    and "\t\t\t\tif c > 0 and o.still then val = val + (o.value or 1) * c end\n" in _b204, \
    "BUILD REFUSED (round 206): an exact wave's value must count standing enemies only"
print("ROUND 206 GATE OK: an exact wave's value counts enemy soldiers that stand still")
'''


def main():
    src = open(SRC, encoding="utf-8").read()
    i = src.index(ANCHOR_HEAD)
    j = src.index("% len(_cone205))\n", i) + len("% len(_cone205))\n")
    src = src[:j] + ADD + src[j:]
    src = src.replace("20261122_cone_harness203", "20261122_standing_harness204")
    open(DST, "w", encoding="utf-8", newline="\n").write(src)
    print("wrote", DST)


if __name__ == "__main__":
    main()
