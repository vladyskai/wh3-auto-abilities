#!/usr/bin/env python3
"""Build the round-145 build script from the round-144 one. No count gate moves (no entry added).
Adds one gate: the read-only battlefield map probe is present, called once per poll through pcall, and its code casts
nothing and touches no trigger state."""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261113_open_batch3_harness143\build_and_install144.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261113_map_probe_harness144\build_and_install145.py"
ANCHOR = 'print("ROUND 144 GATE OK: 10 new entries / 10 keys; 5 new families; 3 skipped abilities absent")\n'
ADD = ANCHOR + r'''# ROUND 145: the read-only battlefield map probe.
assert "FOURTH.MAP_EVERY_S = 2" in script_txt and script_txt.count("pcall(FOURTH.map_tick, tick_count)") == 1, \
    "the map probe is missing or called more than once per poll"
_m0 = script_txt.find("function FOURTH.map_num(f, fmt)")
_m1 = script_txt.find("FOURTH.evaluators = {", _m0)
assert 0 < _m0 < _m1, "the map probe block is missing"
_mspan = script_txt[_m0:_m1]
for _bad in ("perform_special_ability", "cast_target", "eg_enemy", "ah_ally", "string.find"):
    assert _bad not in _mspan, "the map probe is not read-only: " + _bad
print("ROUND 145 GATE OK: the map probe is read-only and pcall'd once per poll")
'''
src = open(SRC, encoding="utf-8").read()
assert src.count(ANCHOR) == 1
src = src.replace(ANCHOR, ADD)
src = src.replace("20261113_open_batch3_harness143", "20261113_map_probe_harness144")
assert "os.remove(GAME_PACK)" not in src
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST)
