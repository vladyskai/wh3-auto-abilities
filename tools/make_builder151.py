#!/usr/bin/env python3
"""Build the round-151 build script from the round-150 one. No count gate moves (no trigger changed).
Adds one gate: large first + hold, the usage rules, the breath band, the 27 default-armed families (with the test-only
switch), the ALL badge, and the round-151 shot / large tables REGENERATED from the game data and found in the script."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import round151_large_defaults as R151  # noqa: E402

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261114_value_target_harness149\build_and_install150.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261114_large_defaults_harness150\build_and_install151.py"
ANCHOR = 'print("ROUND 150 GATE OK: value rule, armour 50, standstill, 21 when_ready, WINDS row; the tables match the game")\n'
ADD = ANCHOR + r'''# ROUND 151: large first + hold, usage rules, breaths at 90 degrees, default-armed families, the ALL badge.
for _f in ("function FOURTH.blob_pick_large(unit, m, r, key)", "function FOURTH.blob_large_hold(m, key, inf_value)",
           "function FOURTH.blob_usage_ok(unit, key)", "FOURTH.BREATH_VALUE_BAND = 0.8 ",
           'FOURTH.ALL_BADGE_ID = "zz_auto_badge_all"', "function FOURTH.all_click()", "function FOURTH.armed_slot(slot, marker)"):
    assert _f in script_txt, "round-151 piece missing: " + _f
assert script_txt.count("pcall(FOURTH.all_badge_tick)") == 1, "the ALL badge tick is not called exactly once"
_d0 = script_txt.find("FOURTH.DEFAULT_ON_TRIGGERS = {")
_d1 = script_txt.find("}", _d0)
_fams = set(l.strip().split(" = ")[0] for l in script_txt[_d0:_d1].split("\n")[1:] if " = true" in l)
assert _fams == set(%r), "the default-armed families differ from the user's ruling"
assert "and ZZ_AUTO_TEST_NO_DEFAULTS ~= true" in script_txt, "the default switch is missing"
import gen_blob_tables as _g151
_k151 = _g151.keys_in(script_txt)
assert _g151.lua_block_large(_g151.shot_table(_k151), _g151.large_def_table()) in script_txt, \
    "BUILD REFUSED (round 151): the shot / large tables differ from the game data"
print("ROUND 151 GATE OK: large first + hold, usage rules, breath band 0.8, 27 default-armed families, ALL badge; tables match")
''' % (sorted(R151.DEFAULT_ON),)
src = open(SRC, encoding="utf-8").read()
assert src.count(ANCHOR) == 1
src = src.replace(ANCHOR, ADD)
src = src.replace("20261114_value_target_harness149", "20261114_large_defaults_harness150")
assert "os.remove(GAME_PACK)" not in src
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST)
