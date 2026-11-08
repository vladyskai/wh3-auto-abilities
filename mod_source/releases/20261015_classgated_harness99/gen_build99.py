# -*- coding: utf-8 -*-
"""Assemble build_and_install99.py from the round-98 build script: re-base the
count pins the round-99 moves changed, and add the ROUND v99 assertions."""
import io

SRC = "build_and_install99_base.py"
DST = "build_and_install99.py"
s = io.open(SRC, encoding="utf-8", newline="").read()

def sub(old, new, label, count=1):
    global s
    n = s.count(old)
    assert n == count, "%s: %d matches (want %d)" % (label, n, count)
    s = s.replace(old, new, count)

sub("assert script_txt.count('trigger = \"melee_unwavering\"') == 373, \\",
    "assert script_txt.count('trigger = \"melee_unwavering\"') == 363, \\", "mu pin", count=2)
sub("assert script_txt.count('trigger = \"charge_or_melee\"') == 26, \\",
    "assert script_txt.count('trigger = \"charge_or_melee\"') == 25, \\", "com pin")
sub("assert script_txt.count('trigger = \"ushoran_health\"') == 38, ",
    "assert script_txt.count('trigger = \"ushoran_health\"') == 34, ", "ush pin")
sub("assert script_txt.count('trigger = \"ally_melee_buff\"') == 11, ",
    "assert script_txt.count('trigger = \"ally_melee_buff\"') == 14, ", "buff pin")
sub("assert script_txt.count(\"\\t\\tally_range_real = \") == 18, ",
    "assert script_txt.count(\"\\t\\tally_range_real = \") == 32, ", "ally_real pin")

# add the ROUND v99 assertion block before the HOUSEKEEPING block
ANCHOR = "# HOUSEKEEPING 20261004: the two throwaway experiment probes were RETIRED from the"
BLOCK = '''# ROUND v99: THE TARGET-CLASS-GATED CLASS-B ENTRIES (nothing above is loosened).
# The 15 NEEDS-RULING rows ship as ALLY-TARGETED casts: the 7 derived class-key
# lists, the class reader/gate helpers, the 200 m ally constant, the infinite
# bound text, the ten new evaluators + their map/TIP wiring, the winds (max-hp)
# pick rule and the fresh-handle/hold/lapse machinery.
assert "FOURTH.class_keys = {" in script_txt, "the derived class-key tables are missing"
for _nm, _sz in (("beast", 55), ("monster", 235), ("warmachine", 68), ("construct", 29),
                 ("hellforged", 13), ("missile", 493), ("overseer", 918)):
    _i = script_txt.find(_nm + " = {")
    assert _i >= 0, "the " + _nm + " class list is missing"
    _j = script_txt.find("},", _i)
    assert script_txt[_i:_j].count("] = true,") == _sz, "the " + _nm + " list size is not " + str(_sz)
assert "function FOURTH.class_member(unit, name)" in script_txt, "the class reader is missing"
assert "function FOURTH.ab_filter_ok(unit)" in script_txt, "the class gate is missing"
assert "function FOURTH.morale_broken(unit)" in script_txt, "the morale-broken read is missing"
assert "function FOURTH.ab_bound_text()" in script_txt, "the bound-text helper is missing"
assert "if FOURTH.ab_infinite then return true end" in script_txt, "the infinite bound is not honoured"
assert "none (infinite range per wiki)" in script_txt, "the infinite-range log text is missing"
assert script_txt.count("FOURTH.ab_filter = nil") == 2, "the class-gate slot is not defined+cleared"
assert script_txt.count("FOURTH.ab_infinite = nil") == 2, "the infinite slot is not defined+cleared"
assert "FOURTH.ALLY_CAST_R200 = 140" in script_txt, "the 70% ally-cast constant is missing: FOURTH.ALLY_CAST_R200 = 140"
assert "\\t[200] = FOURTH.ALLY_CAST_R200," in script_txt, "the 200 m ally map entry is missing"
assert 'family == "winds"' in script_txt, "the winds (max-hp) family is missing"
assert 'FOURTH.context_value(other, "HealthValue")' in script_txt, "the HealthValue read is missing"
for _f in ("overseer", "beast", "broken", "missile", "warmachine_heal", "hellforged_heal",
           "monster_heal", "construct_heal", "infinite_buff", "winds"):
    assert "function FOURTH.evaluate_ally_" + _f + "(unit, routing)" in script_txt, \\
        "the ally_" + _f + " evaluator is missing"
    assert "ally_" + _f + " = FOURTH.evaluate_ally_" + _f + "," in script_txt, \\
        "the ally_" + _f + " trigger is not wired"
assert script_txt.count('trigger = "ally_overseer"') == 1 and script_txt.count('trigger = "ally_beast"') == 1, \\
    "the overseer/beast trigger counts are wrong"
assert script_txt.count('trigger = "ally_broken"') == 1 and script_txt.count('trigger = "ally_missile"') == 3, \\
    "the broken/missile trigger counts are wrong"
assert script_txt.count('trigger = "ally_warmachine_heal"') == 1 and \\
    script_txt.count('trigger = "ally_hellforged_heal"') == 1 and \\
    script_txt.count('trigger = "ally_monster_heal"') == 1 and \\
    script_txt.count('trigger = "ally_construct_heal"') == 1, "a class-heal trigger count is wrong"
assert script_txt.count('trigger = "ally_infinite_buff"') == 1 and script_txt.count('trigger = "ally_winds"') == 1, \\
    "the infinite/winds trigger counts are wrong"
assert "unit_in_range(" not in script_txt, "the engine unit_in_range call is back"


'''
sub(ANCHOR, BLOCK + ANCHOR, "v99 block")

io.open(DST, "w", encoding="utf-8", newline="").write(s)
print("wrote", DST, len(s), "bytes")
