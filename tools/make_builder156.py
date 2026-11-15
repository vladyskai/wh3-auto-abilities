#!/usr/bin/env python3
"""Build the round-156 build script from the round-155 one.

Gates rebased: entries 799 -> 810 (11 gates); range_real fields 294 -> 305 (2); target classes 26 -> 28; the
round-146 gate's "the two single-entity snipes are absent" becomes "they are not on enemy_blob" (they now ride
enemy_single_shot).
Adds one gate: the 11 magic missiles on their 5 families, the user's 10 m safety setting, the new 70% constant
(120 m -> 84 m), the single class, the re-check, and the SHOT table REGENERATED from the game data and found in the
script."""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261115_all_spot_harness154\build_and_install155.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261115_magic_missiles_harness155\build_and_install156.py"
ANCHOR = 'print("ROUND 155 GATE OK: the ALL button at the hand-tuned (-923, 0)")\n'
ADD = ANCHOR + r'''# ROUND 156: the magic missiles (user rulings 2026-11-15).
for _f, _n in (("enemy_large_shot", 5), ("enemy_single_shot", 2), ("enemy_infantry_shot", 1),
               ("enemy_melee_or_fast", 2), ("enemy_melee_or_shooting", 1)):
    assert script_txt.count('trigger = "%s"' % _f) == _n, "family %s does not carry %d entries" % (_f, _n)
    assert ("%s = FOURTH.evaluate_%s," % (_f, _f)) in script_txt, "family %s is not wired" % _f
assert "FOURTH.SHOT_SAFE_M = 10 " in script_txt, "the user's 10 m safety setting is missing"
assert "FOURTH.ENEMY_CAST_R120 = %d " % int(120 * 0.70 + 1e-9) in script_txt and "[120]  = FOURTH.ENEMY_CAST_R120," in script_txt, \
    "70% rule broken for 120 m"
assert 'if cls == "single" then return FOURTH.class_keys.single[t] == true end' in script_txt, "the single class is missing"
assert script_txt.count('\t\ttarget_class = "single",') == 2, "Dead Eye / Focused Shot do not honour the single-entity rule"
assert 'elseif eg_mode_now == "shot" then' in script_txt, "the magic-missile pre-cast re-check is missing"
import gen_shot_tables as _g156
_k156 = _g156.keys_in(script_txt)
assert len(_k156) == 11, "the magic-missile families do not carry 11 keys"
assert _g156.lua_block(_g156.derive(_k156)) in script_txt, \
    "BUILD REFUSED (round 156): the SHOT table differs from the game data"
print("ROUND 156 GATE OK: 11 magic missiles on 5 families; the SHOT table matches the game; 10 m; 120 m -> 84 m; single class")
'''
RULES = [
    ('script_txt.count("\\t{ marker = ") == 799, "the abilities table is not 799 entries"',
     'script_txt.count("\\t{ marker = ") == 810, "the abilities table is not 810 entries"', 11),
    ('count("\\t\\trange_real = ") == 294', 'count("\\t\\trange_real = ") == 305', 2),
    ('script_txt.count("\\t\\ttarget_class = ") == 26', 'script_txt.count("\\t\\ttarget_class = ") == 28', 1),
    ('for _k in ("wh3_dlc26_character_abilities_dead_eye", "wh2_dlc13_lord_abilities_kill_shot"):\n'
     '    assert _k not in script_txt, "a single-entity-only snipe is on the blob trigger: " + _k\n',
     'for _k in ("dead_eye", "focused_shot"):   # ROUND 156: they ride enemy_single_shot, never enemy_blob\n'
     '    assert (\'trigger = "enemy_blob",\\n\\t\\tbadge = "zz_auto_badge_%s"\' % _k) not in script_txt, \\\n'
     '        "a single-entity-only snipe is on the blob trigger: " + _k\n', 1),
]
src = open(SRC, encoding="utf-8").read()
assert src.count(ANCHOR) == 1
src = src.replace(ANCHOR, ADD)
for a, b, n in RULES:
    assert src.count(a) == n, (a[:60], src.count(a))
    src = src.replace(a, b)
    print("rebased %d x: %s" % (n, a[:60]))
assert "os.remove(GAME_PACK)" not in src
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST)
