# -*- coding: utf-8 -*-
"""Generate build_and_install98.py from the shipped build_and_install97.py.

Changes: the v98 docstring note; RE-BASED v97 asserts (the moved trigger counts
and the Stay Here reason token); and a new block asserting CLASS B (the 5 named
70% ally-cast constants, the ally real->bound map, the 18 ally_range_real
fields, the load-loop wiring, the fresh-friend helper, the shared ally picker,
the four family evaluators, the fresh-handle cast branch and the poll slots),
plus that the army-bar Meat Feast entry is UNCHANGED and that unit_in_range( is
still GONE. The build/pack/install machinery is unchanged.
"""
import io, os

HERE = os.path.dirname(os.path.abspath(__file__))
NL = chr(10)
BS = chr(92)  # a lone backslash (the Lua line continuation in the asserts)

src = io.open(HERE + "/build_and_install97_base.py", encoding="utf-8", newline="").read()


def sub(old, new, label, count=1):
    global src
    n = src.count(old)
    assert n == count, "%s: %d matches (want %d)" % (label, n, count)
    src = src.replace(old, new, count)
    print("patch %s: applied" % label)


# --- docstring -----------------------------------------------------------------
DA = ("offer test is unit:unit_distance(enemy) <= that constant ONLY - never the" + NL
      + "engine's unit_in_range. melee_unwavering 480 -> 383." + NL + '"""')
DN = ("offer test is unit:unit_distance(enemy) <= that constant ONLY - never the" + NL
      + "engine's unit_in_range. melee_unwavering 480 -> 383." + NL + NL
      + "ROUND v98: CLASS B (ally-targeted effects cast on self). 17 of the 34" + NL
      + "Class-B entries from the audit now cast ON THE CHOSEN ALLY across four new" + NL
      + "families (ally_melee_buff 11 / ally_heal 3 / ally_heal_melee 1 / ally_wavering" + NL
      + "2); Stay Here, I'll Get Help! (whose ally pick already shipped) gains the cast" + NL
      + "target and its own 70% bound; Meat Feast is an ARMY-BAR ability and is SKIPPED" + NL
      + "(standing rule 10); 15 entries need a user ruling. Each implemented entry" + NL
      + "carries its own REAL target_intercept_range (ally_range_real) mapped at load to" + NL
      + "ONE named 70% constant per real range (5 constants, floor(real*0.70)); the offer" + NL
      + "test is unit:unit_distance(ally) <= that constant ONLY - never the engine's" + NL
      + "unit_in_range - and the cast goes through the FRESH caster controller AND the" + NL
      + "FRESH ally unit, re-enumerated the SAME tick. melee_unwavering 383 -> 373," + NL
      + "charge_or_melee 29 -> 26, ushoran_health 41 -> 38, melee_health75 2 -> 1." + NL
      + '"""')
sub(DA, DN, "docstring")

# --- RE-BASE the v97 counts -----------------------------------------------------
sub("== 383, " + BS, "== 373, " + BS, "melee count pins", count=2)
sub("the melee_unwavering entry count is not 383 (97 Class-A entries moved to the enemy triggers)",
    "the melee_unwavering entry count is not 373 (10 Class-B entries moved to the ally families)",
    "melee message")
sub("the melee_unwavering count is not 383", "the melee_unwavering count is not 373", "melee message 2")
sub("== 29, " + BS, "== 26, " + BS, "charge_or_melee count")
sub("the charge_or_melee entry count is not 29",
    "the charge_or_melee entry count is not 26 (3 Class-B entries moved to ally_melee_buff)",
    "charge_or_melee message")
sub('== 41, "the ushoran_health entry count is not 41"',
    '== 38, "the ushoran_health entry count is not 38 (3 Class-B heals moved to ally_heal)"',
    "ushoran count")
sub('== 2, "the melee_health75 entry count is not 2"',
    '== 1, "the melee_health75 entry count is not 1 (Captain of the Phoenix Guard moved to ally_heal_melee)"',
    "melee_health75 count")
sub('''assert 'reason = "wavering ally in range (self-cast)"' in script_txt, "the wavering-ally-in-range reason is missing"''',
    '''assert 'reason = "wavering ally in range, cast on ally"' in script_txt, "the wavering-ally-in-range reason is missing"''',
    "stay-here reason")

# --- the v98 gates (inserted just before the is_firing assert) -----------------
ANCHOR = ('assert "is_firing" not in script_txt and "is_shooting" not in script_txt, ' + BS + NL
          + '    "an invented firing predicate is in the mod"')
assert src.count(ANCHOR) == 1, "the is_firing anchor count moved: %d" % src.count(ANCHOR)
CONSTS = [("FOURTH.ALLY_CAST_R50  = 35", 50, 35), ("FOURTH.ALLY_CAST_R60  = 42", 60, 42),
          ("FOURTH.ALLY_CAST_R75  = 52", 75, 52), ("FOURTH.ALLY_CAST_R100 = 70", 100, 70),
          ("FOURTH.ALLY_CAST_R150 = 105", 150, 105)]
G = [NL]
G.append("# ROUND v98: CLASS B (ally-targeted effects cast on self). The five named 70%")
G.append("# ally-cast constants, the ally real->bound map, the 18 ally_range_real fields,")
G.append("# the load-loop wiring, the fresh-friend helper, the shared ally picker, the four")
G.append("# family evaluators, the fresh-handle cast branch and the poll slots.")
G.append('assert "FOURTH.ALLY_CAST = {" in script_txt, "the ally real->bound map is missing"')
G.append('assert "ability.range_m = FOURTH.ALLY_CAST[ability.ally_range_real]" in script_txt, ' + BS)
G.append('    "the load-loop ally real->bound mapping is missing"')
G.append('assert script_txt.count("\\t\\tally_range_real = ") == 18, "the ally_range_real fields are not 18"')
for tok, real, want in CONSTS:
    assert int(real * 0.70 + 1e-9) == want, "the documented 70% ally target is wrong for " + tok
    G.append('assert "%s" in script_txt, "the 70%% ally-cast constant is missing: %s"' % (tok, tok))
G.append('assert "function FOURTH.ab_fresh_friend_su(unit)" in script_txt, ' + BS)
G.append('    "the fresh-friend helper is missing"')
G.append('assert "function FOURTH.ab_pick_ally(unit, routing, family)" in script_txt, ' + BS)
G.append('    "the shared ally picker is missing"')
G.append('assert "function FOURTH.ab_ally_valid(unit, ally)" in script_txt, ' + BS)
G.append('    "the ally validity helper is missing"')
G.append('assert "FOURTH.ab_caster_su = FOURTH.ab_fresh_friend_su(unit)" in script_txt and ' + BS)
G.append('    "FOURTH.ab_ally_su = FOURTH.ab_fresh_friend_su(best_ally)" in script_txt, ' + BS)
G.append('    "the fresh caster/ally re-fetch is missing"')
G.append('assert "uc = FOURTH.ab_caster_su.uc" in script_txt and "target = FOURTH.ab_ally_su.unit" in script_txt, ' + BS)
G.append('    "the fresh-handle ally cast branch is missing"')
G.append('assert "FOURTH.ab_range_m = ability.range_m" in script_txt and ' + BS)
G.append('    "FOURTH.ab_marker = ability.marker" in script_txt, ' + BS)
G.append('    "the poll does not set the current ability ally bound/marker"')
for fn in ("ally_heal", "ally_heal_melee", "ally_wavering", "ally_melee_buff"):
    G.append('assert "function FOURTH.evaluate_%s(unit, routing)" in script_txt, "the %s evaluator is missing"' % (fn, fn))
    G.append('assert "%s = FOURTH.evaluate_%s," in script_txt, "the %s trigger is not wired"' % (fn, fn, fn))
G.append("assert script_txt.count('trigger = \"ally_melee_buff\"') == 11, \"the ally_melee_buff count is not 11\"")
G.append("assert script_txt.count('trigger = \"ally_heal\"') == 3, \"the ally_heal count is not 3\"")
G.append("assert script_txt.count('trigger = \"ally_heal_melee\"') == 1, \"the ally_heal_melee count is not 1\"")
G.append("assert script_txt.count('trigger = \"ally_wavering\"') == 2, \"the ally_wavering count is not 2\"")
G.append("# the ARMY-BAR entry (Meat Feast, standing rule 10) is NOT given ally logic")
G.append("assert 'marker = \"butcher\", name = \"Meat Feast\", trigger = \"ushoran_health\"' in script_txt, " + BS)
G.append('    "the army-bar Meat Feast entry was changed"')
G.append('assert "unit_in_range(" not in script_txt, "the engine unit_in_range call is back"')
GATES = NL.join(G)
sub(ANCHOR, GATES + NL + ANCHOR, "v98 gates")

io.open(HERE + "/build_and_install98.py", "w", encoding="utf-8", newline="").write(src)
print("wrote build_and_install98.py", len(src), "bytes")
