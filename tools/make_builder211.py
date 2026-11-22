#!/usr/bin/env python3
"""Build the round-211 build script from the round-210 one (tuning: the read-only raw unit probe of the test build).
ROUND 211 GATE: the probe exists once, is called once (from the map probe), and its body orders nothing and writes no
mod state."""

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261122_replies2_harness208\build_and_install210.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261122_rawprobe_harness209\build_and_install211.py"
ANCHOR = '''      "cones from the caster; slow units can charge; a unit's abilities are read again after a cast")\n'''
ADD = ANCHOR + r'''# ROUND 211 (tuning): the read-only raw unit probe of the test build.
_i211 = script_txt.index("\nfunction FOURTH.raw_probe(tick)\n")
_b211 = script_txt[_i211:script_txt.index("\nfunction FOURTH.map_tick(tick)\n", _i211)]
assert script_txt.count("\nfunction FOURTH.raw_probe(tick)\n") == 1 \
    and script_txt.count("FOURTH.raw_probe(") == 1 and script_txt.count("pcall(FOURTH.raw_probe, tick)") == 1 \
    and "function FOURTH.map_tick(tick)\n\tpcall(FOURTH.raw_probe, tick)   -- ROUND 211: read-only\n" in script_txt, \
    "BUILD REFUSED (round 211): the raw probe must be called once, from the map probe"
for _t211 in ("perform_special_ability", "cast_gate", "owned_keys_by_unit", "owned_abilities_by_unit", "target_key_by_unit",
              "tracked_units", "armed["):
    assert _t211 not in _b211, "BUILD REFUSED (round 211): the raw probe touches '%s' (it must only read and log)" % _t211
print("ROUND 211 GATE OK: the raw unit probe is read-only and runs from the map probe")
'''


def main():
    src = open(SRC, encoding="utf-8").read()
    assert src.count(ANCHOR) == 1, src.count(ANCHOR)
    src = src.replace(ANCHOR, ADD).replace("20261122_replies2_harness208", "20261122_rawprobe_harness209")
    open(DST, "w", encoding="utf-8", newline="\n").write(src)
    print("wrote", DST)


if __name__ == "__main__":
    main()
