#!/usr/bin/env python3
"""Build the round-164 build script from the round-163 one.

Gates rebased: entries 918 -> 946 (11 gates); range_real fields 389 -> 417; target classes 47 -> 56; the round-160 key
count 975 -> 1003; the round-162 gate's enemy_wave 12 -> 30, enemy_wander 42 -> 43 and WW keys 56 -> 84.
Adds one gate: the three new families wired and unarmed by default, the caster no longer blocking its own wave, the
ww caster gate, and the WW_NOMELEE list REGENERATED from the game data."""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261116_placed_areas_harness162\build_and_install163.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261116_breaths_harness163\build_and_install164.py"
ANCHOR = ('print("ROUND 163 GATE OK: the strike and the vassal wired and unarmed, the expendable / cheap skip; the EXPENDABLE "\n'
          '      "table matches the game (48 units)")\n')
ADD = ANCHOR + r'''# ROUND 164: the friendly-fire breaths (user rulings 2026-11-16).
_def164 = script_txt.split("FOURTH.DEFAULT_ON_TRIGGERS = {", 1)[1].split("\n}", 1)[0]
for _f164, _n164 in (("enemy_wave_charge", 2), ("enemy_cone", 5), ("enemy_sweep", 2)):
    assert script_txt.count('trigger = "%s"' % _f164) == _n164, "%s does not carry %d entries" % (_f164, _n164)
    assert ("%s = FOURTH.evaluate_%s," % (_f164, _f164)) in script_txt, "family %s is not wired" % _f164
    assert ("\n\t%s = true," % _f164) not in _def164, "%s must start unarmed (M)" % _f164
assert "if oid == nil or oid ~= self_id then" in script_txt and "function FOURTH.ww_caster_ok(unit)" in script_txt, \
    "the caster exclusion or the ww caster gate is missing"
import gen_ww_tables as _g164
_kf164 = _g164.keys_in(script_txt)
assert len(_kf164) == 84 and _g164.nomelee_block(_kf164) in script_txt, \
    "BUILD REFUSED (round 164): the WW_NOMELEE list differs from the game data"
print("ROUND 164 GATE OK: the charge waves, the cones and the sweeps wired and unarmed; the caster no longer blocks its "
      "own wave; WW_NOMELEE matches the game")
'''
RULES = [
    ('script_txt.count("\\t{ marker = ") == 918, "the abilities table is not 918 entries"',
     'script_txt.count("\\t{ marker = ") == 946, "the abilities table is not 946 entries"'),
    ('count("\\t\\trange_real = ") == 389', 'count("\\t\\trange_real = ") == 417'),
    ('script_txt.count("\\t\\ttarget_class = ") == 47', 'script_txt.count("\\t\\ttarget_class = ") == 56'),
    ("assert len(_keys160) == 975 and _wu160 == _tab160,", "assert len(_keys160) == 1003 and _wu160 == _tab160,"),
    ('"table matches the game (%d of 975 keys have a wind-up)"', '"table matches the game (%d of 1003 keys have a wind-up)"'),
    ("script_txt.count('trigger = \"enemy_wave\"') == 12", "script_txt.count('trigger = \"enemy_wave\"') == 30"),
    ("script_txt.count('trigger = \"enemy_wander\"') == 42", "script_txt.count('trigger = \"enemy_wander\"') == 43"),
    ("assert len(_kf162) == 56 and", "assert len(_kf162) == 84 and"),
]
src = open(SRC, encoding="utf-8").read()
assert src.count(ANCHOR) == 1, src.count(ANCHOR)
src = src.replace(ANCHOR, ADD)
for a, b in RULES:
    n = src.count(a)
    assert n >= 1, (a[:70], n)
    src = src.replace(a, b)
    print("rebased %d x: %s" % (n, a[:70]))
assert "os.remove(GAME_PACK)" not in src
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST)
