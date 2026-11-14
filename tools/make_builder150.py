#!/usr/bin/env python3
"""Build the round-150 build script from the round-149 one.

Gates rebased: melee_unwavering 309 -> 288 (4 gates; the 21 Winds of Magic abilities moved to when_ready).
Adds one gate: the value rule, the armour rule (50), the standstill gate, the 21 when_ready entries, the WINDS row, and
the round-150 damage / defence tables REGENERATED from the game data and found in the script."""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261114_revert_probes_harness148\build_and_install149.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261114_value_target_harness149\build_and_install150.py"
ANCHOR = 'print("ROUND 149 GATE OK: no address field and no memreader code")\n'
ADD = ANCHOR + r'''# ROUND 150: the blob target destroys the most value; never while moving; Winds of Magic when ready; the WINDS row.
assert script_txt.count('trigger = "when_ready"') == 21 and "when_ready = FOURTH.evaluate_when_ready," in script_txt, \
    "the 21 Winds of Magic abilities are not on when_ready"
assert "FOURTH.BLOB_AP_ARMOUR_MIN = 50 " in script_txt and "function FOURTH.blob_value(tgt, m, r, dmg)" in script_txt \
    and "function FOURTH.blob_still(unit)" in script_txt and "if not FOURTH.blob_still(unit) then" in script_txt, \
    "the value rule, the armour rule or the standstill gate is missing"
assert '"WINDS t=" .. t' in script_txt, "the WINDS map row is missing"
import gen_blob_tables as _g150
assert _g150.lua_block_value(_g150.damage_table(_g150.keys_in(script_txt)), _g150.defence_table()) in script_txt, \
    "BUILD REFUSED (round 150): the damage / defence tables differ from the game data"
print("ROUND 150 GATE OK: value rule, armour 50, standstill, 21 when_ready, WINDS row; the tables match the game")
'''
RULES = [
    ("count('trigger = \"melee_unwavering\"') == 309", "count('trigger = \"melee_unwavering\"') == 288", 4),
]
src = open(SRC, encoding="utf-8").read()
assert src.count(ANCHOR) == 1
src = src.replace(ANCHOR, ADD)
for a, b, n in RULES:
    assert src.count(a) == n, (a[:60], src.count(a))
    src = src.replace(a, b)
    print("rebased %d x: %s" % (n, a[:60]))
src = src.replace("20261114_revert_probes_harness148", "20261114_value_target_harness149")
assert "os.remove(GAME_PACK)" not in src
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST)
