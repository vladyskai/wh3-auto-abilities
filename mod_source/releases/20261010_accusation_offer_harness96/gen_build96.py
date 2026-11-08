# -*- coding: utf-8 -*-
"""Generate build_and_install96.py from the shipped build_and_install95.py.

Changes: the v96 docstring note; and a new block asserting the Accusation
MOVE-ORDER FIX (the constant-only offer test, the engine unit_in_range call
GONE, the real-distance log lines, the primitive citation). The build/pack/
install machinery is unchanged.
"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
H95 = "C:/Users/vlady/Desktop/WH3_mod/mod_source/releases/20261010_range_rule_harness95"
NL = chr(10)

src = io.open(H95 + "/build_and_install95.py", encoding="utf-8", newline="").read()


def sub(old, new, label, count=1):
    global src
    n = src.count(old)
    assert n == count, "%s: %d matches (want %d)" % (label, n, count)
    src = src.replace(old, new, count)
    print("patch %s: applied" % label)


# --- docstring -----------------------------------------------------------------
DA = "direction. The rule ships as FOURTH.RANGE_FRACTION = 0.70." + NL + '"""'
DN = ("direction. The rule ships as FOURTH.RANGE_FRACTION = 0.70." + NL + NL
      + "ROUND v96: THE ACCUSATION MOVE-ORDER ROOT CAUSE. The observer probe" + NL
      + "(zz_probe_dist, tick 59) proved the offer test trusted the engine's loose" + NL
      + "unit_in_range reach read: 'CAND-FIRST ... dist=81.3m first_passing_test=engine" + NL
      + "engine_unit_in_range=t our_52_test=f our_75_test=f' - the mod offered and cast" + NL
      + "at 81.3 m, so the engine WALKED the caster in. The offer test is now the 70%" + NL
      + "CONSTANT ONLY (unit:unit_distance(enemy) <= FOURTH.ACCUSATION_RANGE_M = 52 m)," + NL
      + "the engine helper is REMOVED from the offer path, and the log prints the REAL" + NL
      + "edge-to-edge distance (unit:unit_distance, battle_unit.lua:160) at the target" + NL
      + "choice and the pre-cast re-check." + NL + '"""')
sub(DA, DN, "docstring")

# --- the v96 gates (inserted just before the is_firing assert) -----------------
ANCHOR = ('assert "is_firing" not in script_txt and "is_shooting" not in script_txt, \\' + NL
          + '    "an invented firing predicate is in the mod"')
GATES = (NL
         + "# ROUND v96: THE ACCUSATION MOVE-ORDER ROOT CAUSE (nothing above is loosened)." + NL
         + "# The offer test is the 70% CONSTANT ONLY and never the engine's unit_in_range;" + NL
         + "# the chosen-target and pre-cast re-check logs print the REAL distance." + NL
         + 'assert "function FOURTH.eg_enemy_within_bound(unit, enemy)" in script_txt, \\' + NL
         + '    "the constant-only offer test is missing"' + NL
         + 'assert "and FOURTH.eg_enemy_within_bound(unit, enemy) then" in script_txt, \\' + NL
         + '    "the offer gate is not wired to the constant-only test"' + NL
         + 'assert "function FOURTH.eg_enemy_in_range(unit, enemy)" not in script_txt, \\' + NL
         + '    "the old engine-helper offer test is back"' + NL
         + 'assert "unit_in_range(" not in script_txt, \\' + NL
         + '    "the engine unit_in_range call is back in the offer path"' + NL
         + 'assert "return gap <= FOURTH.ACCUSATION_RANGE_M" in script_txt, \\' + NL
         + '    "the offer test does not compare the gap to the 70% constant"' + NL
         + 'assert "battle_unit.lua:160" in script_txt, \\' + NL
         + '    "the distance-primitive citation is missing"' + NL
         + 'assert \'") distance="\' in script_txt, \\' + NL
         + '    "the target-choice log does not print the real distance"' + NL
         + 'assert \'.. "m bound=" .. tostring(FOURTH.ACCUSATION_RANGE_M) .. "m")\' in script_txt, \\' + NL
         + '    "the target-choice log does not print the bound"' + NL
         + 'assert \'", distance="\' in script_txt, \\' + NL
         + '    "the pre-cast re-check log does not print the real distance"' + NL
         + 'assert \'.. ") within "\' not in script_txt, \\' + NL
         + '    "the misleading static within-Nm log label is back"' + NL)
sub(ANCHOR, GATES + ANCHOR, "v96 gates")

io.open(HERE + "/build_and_install96.py", "w", encoding="utf-8", newline="").write(src)
print("wrote build_and_install96.py", len(src), "bytes")
