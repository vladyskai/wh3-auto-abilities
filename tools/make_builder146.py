#!/usr/bin/env python3
"""Build the round-146 build script from the round-145 one.

Gates rebased: entries 722 -> 799 (11 gates); range_real fields 217 -> 294 (2); target classes 24 -> 26; the round-145
read-only span now ends at the round-146 block.
Adds one gate: 77 entries on enemy_blob, the two excluded single-entity snipes absent, the user's settings, the eight new
70% constants, and the blast / spacing tables REGENERATED from the game data and found in the script."""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261113_map_probe_harness144\build_and_install145.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261113_blob_trigger_harness145\build_and_install146.py"
ANCHOR = 'print("ROUND 145 GATE OK: the map probe is read-only and pcall\'d once per poll")\n'
ADD = ANCHOR + r'''# ROUND 146: the blob trigger.
assert script_txt.count('trigger = "enemy_blob"') == 77, "the blob trigger does not carry the 77 exploding attacks"
for _k in ("wh3_dlc26_character_abilities_dead_eye", "wh2_dlc13_lord_abilities_kill_shot"):
    assert _k not in script_txt, "a single-entity-only snipe is on the blob trigger: " + _k
assert "FOURTH.BLOB_MARGIN_M = 10 " in script_txt and "FOURTH.BLOB_FRACTION = 0.5 " in script_txt, \
    "the user's blob settings (10 m, half a packed block) are missing"
for _r in (55, 60, 80, 130, 250, 350, 400, 600):
    assert ("FOURTH.ENEMY_CAST_R%-3d = %d " % (_r, int(_r * 0.70 + 1e-9))) in script_txt, "70%% rule broken for %d m" % _r
assert 'elseif eg_mode_now == "blob" then' in script_txt and "enemy_blob = FOURTH.evaluate_enemy_blob," in script_txt, \
    "the blob evaluator or its pre-cast re-check is missing"
import gen_blob_tables as _g146
assert _g146.lua_block(_g146.blast_table(_g146.keys_in(script_txt)), _g146.spacing_table()) in script_txt, \
    "BUILD REFUSED (round 146): the blast / spacing tables differ from the game data"
print("ROUND 146 GATE OK: 77 blob entries; the tables match the game; 10 m margin; half a packed block")
'''
RULES = [
    ('script_txt.count("\\t{ marker = ") == 722, "the abilities table is not 722 entries"',
     'script_txt.count("\\t{ marker = ") == 799, "the abilities table is not 799 entries"', 11),
    ('count("\\t\\trange_real = ") == 217', 'count("\\t\\trange_real = ") == 294', 2),
    ('script_txt.count("\\t\\ttarget_class = ") == 24', 'script_txt.count("\\t\\ttarget_class = ") == 26', 1),
    ('_m1 = script_txt.find("FOURTH.evaluators = {", _m0)', '_m1 = script_txt.find("-- ROUND 146 - THE BLOB TRIGGER", _m0)', 1),
]
src = open(SRC, encoding="utf-8").read()
assert src.count(ANCHOR) == 1
src = src.replace(ANCHOR, ADD)
for a, b, n in RULES:
    assert src.count(a) == n, (a[:60], src.count(a))
    src = src.replace(a, b)
    print("rebased %d x: %s" % (n, a[:60]))
src = src.replace("20261113_map_probe_harness144", "20261113_blob_trigger_harness145")
assert "os.remove(GAME_PACK)" not in src
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST)
