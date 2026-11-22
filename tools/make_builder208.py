#!/usr/bin/env python3
"""Build the round-208 build script from the round-207 one (tuning: the cost of the free-aim search).
ROUND 208 GATE: the search poll depends on the unit id and the search is skipped while the ability cannot be cast."""

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261122_review_harness205\build_and_install207.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261122_searchcost_harness206\build_and_install208.py"
ANCHOR = 'print("ROUND 207 GATE OK: the drifting waves count standing enemies only; a ground-only wave without an aim holds")\n'
ADD = ANCHOR + r'''# ROUND 208 (tuning): the cost of the free-aim search. No cast decision changes.
assert "\t\tif (tick_count + idn) % FOURTH.FREE_AIM_EVERY ~= 0 then return nil end\n" in _b203 \
    and "\t\tif ok_can and can == false then return nil end\n" in _b203 \
    and "per[key] = tick_count + FOURTH.FREE_AIM_EVERY" not in script_txt, \
    "BUILD REFUSED (round 208): the search must be spread by unit id and skipped while the ability cannot be cast"
print("ROUND 208 GATE OK: the free-aim search is spread over the polls by unit id and skipped while the ability cannot be cast")
'''


def main():
    src = open(SRC, encoding="utf-8").read()
    assert src.count(ANCHOR) == 1, src.count(ANCHOR)
    src = src.replace(ANCHOR, ADD).replace("20261122_review_harness205", "20261122_searchcost_harness206")
    open(DST, "w", encoding="utf-8", newline="\n").write(src)
    print("wrote", DST)


if __name__ == "__main__":
    main()
