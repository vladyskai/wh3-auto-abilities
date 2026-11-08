# -*- coding: utf-8 -*-
"""ROUND h95b: fix the remaining stale in-function comments that still name the
OLD range value (GD's 25 m gate is now 38 m). Comment-only; no logic change.
"""
import io
import os

ROOT = "C:/Users/vlady/Desktop/WH3_mod/mod_source"
LIVE = ROOT + "/script/battle/mod/zz_test_deadly_onslaught.lua"
ANN = "C:/Users/vlady/Desktop/WH3_mod/docs/WH3_auto_ability_annotated.lua"


def read(p):
    return io.open(p, encoding="utf-8", newline="").read()


def write(p, s):
    io.open(p, "w", encoding="utf-8", newline="").write(s)


def sub(text, old, new, label, count=1):
    n = text.count(old)
    assert n == count, "%s: %d matches (want %d)" % (label, n, count)
    return text.replace(old, new, count)


live = read(LIVE)
ann = read(ANN)

live = sub(live,
    "\t-- cast. If the ally has drifted beyond the conservative 25 m trigger\n"
    "\t-- range the cast is wasted, so SKIP it rather than spend it.",
    "\t-- cast. If the ally has drifted beyond the 38 m trigger range (70% of\n"
    "\t-- the ability's 55 m aura) the cast is wasted, so SKIP it rather than spend it.",
    "L-gd-recheck")
live = sub(live,
    "-- true when the gap is within the conservative 25 m trigger range. An\n"
    "-- UNREADABLE gap (nil) is treated as IN range (fail-open) - exactly how the",
    "-- true when the gap is within the GD trigger range (38 m = 70% of the 55 m\n"
    "-- aura). An UNREADABLE gap (nil) is treated as IN range (fail-open) - exactly how the",
    "L-gd-inrange")
live = sub(live,
    "-- THE RANGE GATE (this round, the reported bug fix): the ally arm only counts\n"
    "-- while the owner is WITHIN the conservative trigger range\n"
    "-- (GLORIOUS_DEATH_RANGE_M = 25 m, deliberately tighter than the ability's\n"
    "-- 55 m wiki aura) of the ally - otherwise the cast is wasted. The CLOSEST",
    "-- THE RANGE GATE (this round, the reported bug fix): the ally arm only counts\n"
    "-- while the owner is WITHIN GLORIOUS_DEATH_RANGE_M (38 m = 70% of the\n"
    "-- ability's 55 m aura, FOURTH.RANGE_FRACTION) of the ally - otherwise the\n"
    "-- cast is wasted. The CLOSEST",
    "L-gd-gate")

ann = sub(ann,
    "\t-- conservative 25 m trigger range. The\n"
    "\t-- owner-in-melee self arm leaves FOURTH.gd_ally nil - never gated.",
    "\t-- 38 m trigger range (70% of the 55 m aura). The\n"
    "\t-- owner-in-melee self arm leaves FOURTH.gd_ally nil - never gated.",
    "A-gd-recheck")
ann = sub(ann,
    "-- true when the gap is within the conservative 25 m trigger range; an\n"
    "-- UNREADABLE gap (nil) is treated as IN range (fail-open).",
    "-- true when the gap is within the GD trigger range (38 m = 70% of the 55 m\n"
    "-- aura); an UNREADABLE gap (nil) is treated as IN range (fail-open).",
    "A-gd-inrange")
ann = sub(ann,
    "-- owner is within the conservative trigger range GLORIOUS_DEATH_RANGE_M\n"
    "-- (25 m, deliberately tighter than the ability's 55 m wiki aura) of",
    "-- owner is within GLORIOUS_DEATH_RANGE_M (38 m = 70% of the ability's 55 m\n"
    "-- aura, FOURTH.RANGE_FRACTION) of",
    "A-gd-gate")

# sanity: no stale numeric claims remain next to the constant name
for _s, _nm in ((live, "live"), (ann, "ann")):
    assert "conservative 25 m" not in _s, _nm + " still has a stale 'conservative 25 m'"
    assert "= 25 m, deliberately" not in _s, _nm + " still has a stale '= 25 m'"
assert ann.count("log(") == 0 and "string.find" not in ann
assert live.count("FOURTH.RANGE_FRACTION = 0.70") == 1
assert ann.count("FOURTH.RANGE_FRACTION = 0.70") == 1

write(LIVE, live)
write(ANN, ann)
print("wrote", LIVE, len(live), "chars")
print("wrote", ANN, len(ann), "chars")
print("OK: stale GD comments now name 38 m")
