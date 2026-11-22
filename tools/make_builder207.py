#!/usr/bin/env python3
"""Build the round-207 build script from the round-206 one (tuning, the afternoon code review).
ROUND 207 GATE: the wave evaluator sets FOURTH.ww_still_only, the per-entry reset clears it, ww_path_value honours it,
and a ground-only wave without an aim holds."""

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261122_standing_harness204\build_and_install206.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261122_review_harness205\build_and_install207.py"
ANCHOR = 'print("ROUND 206 GATE OK: an exact wave\'s value counts enemy soldiers that stand still")\n'
ADD = ANCHOR + r'''# ROUND 207 (tuning, the afternoon code review): the drifting waves count standing enemies only, no orientation-0 wave.
assert script_txt.count("\tFOURTH.ww_still_only = free   -- ROUND 207") == 1 \
    and script_txt.count("\tFOURTH.ww_still_only = nil   -- ROUND 207") == 1 \
    and script_txt.count("\t\t\tif not still_only or o.still then v = v + (o.value or 0) end\n") == 1 \
    and script_txt.count("FOURTH.ww_still_only") == 4, \
    "BUILD REFUSED (round 207): the standing-only slot is not set by the wave evaluator alone and cleared per entry"
assert "\tif free and row.ground and aim == nil then return nil end\n\tFOURTH.ww_take(unit, best, row, aim)\n" in _b203, \
    "BUILD REFUSED (round 207): a ground-only wave without an aim must hold"
print("ROUND 207 GATE OK: the drifting waves count standing enemies only; a ground-only wave without an aim holds")
'''


def main():
    src = open(SRC, encoding="utf-8").read()
    assert src.count(ANCHOR) == 1, src.count(ANCHOR)
    src = src.replace(ANCHOR, ADD).replace("20261122_standing_harness204", "20261122_review_harness205")
    open(DST, "w", encoding="utf-8", newline="\n").write(src)
    print("wrote", DST)


if __name__ == "__main__":
    main()
