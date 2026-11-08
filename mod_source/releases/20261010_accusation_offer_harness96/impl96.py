# -*- coding: utf-8 -*-
"""ROUND h96 (THE MOVE-ORDER ROOT CAUSE) IMPLEMENTATION.

THE BUG (proven live by the passive observer probe zz_probe_dist, tick 59):
    CAND-FIRST ... dist=81.3m first_passing_test=engine
        engine_unit_in_range=t our_52_test=f our_75_test=f
The Accusation OFFER test trusted the engine's own loose `unit_in_range(enemy)`
reach read, which reported TRUE at 81.3 m while BOTH of the mod's own bounds
(52 m and 75 m) said FALSE. The mod therefore offered - and cast at - a target
81.3 m away; the engine accepted the cast and WALKED the caster in: the move
order the user reported. The mod's log label was also static ("within 52m"),
so it could not show the real distance and could not reveal the discrepancy.

THE FIX:
  * the offer test is the 70% CONSTANT ONLY:
        unit:unit_distance(enemy) <= FOURTH.ACCUSATION_RANGE_M   (52 m)
    The engine's `unit_in_range(enemy)` reach read is REMOVED from the offer
    path entirely (it is looser than our bound and is what caused the early
    cast). In-melee preference, closest-among-equals, the fresh-handle
    bench_fresh cast, the pre-cast re-check and the hold are all untouched.
  * the LOG now prints the REAL computed distance to one decimal at BOTH the
    target choice and the pre-cast re-check (and in the lapse-skip line), with
    the bound beside it:  `... distance=48.7m bound=52m`.
  * the primitive is `unit:unit_distance(other)` - EDGE-TO-EDGE (bounding-box
    aware) per battle_unit.lua:160 - so the number in the log IS exactly the
    number the test compared.

BASE: this round reverts the incomplete h96 "contact range" attempt (impl96.py
in releases/20261010_contact_range_harness96, which had already been applied to
the source but was never harnessed, built or installed) back to the SHIPPED
h95 source and applies the fix above. pre96_live.lua/pre96_ann.lua ARE the
shipped h95 source (sha256 ea48ca6dc6bf8e3657a179dfd869e7c876b4d2cf3dfb096f1821d957ba09b704)
and are the RED CONTROL target. The superseded attempt is preserved as
pre96_POST96_attempt_{live,ann}.lua.

The SAME logical change is applied to the LIVE mod and the ANNOTATED reading
copy (the annotated copy returns booleans and is log-free / find-free).
"""
import io
import os

ROOT = "C:/Users/vlady/Desktop/WH3_mod/mod_source"
LIVE = ROOT + "/script/battle/mod/zz_test_deadly_onslaught.lua"
ANN = "C:/Users/vlady/Desktop/WH3_mod/docs/WH3_auto_ability_annotated.lua"
HERE = os.path.dirname(os.path.abspath(__file__))
NL = chr(10)
T = chr(9)


def read(p):
    return io.open(p, encoding="utf-8", newline="").read()


def write(p, s):
    io.open(p, "w", encoding="utf-8", newline="").write(s)


def sub(text, old, new, label, count=1):
    n = text.count(old)
    assert n == count, "%s: %d matches (want %d)" % (label, n, count)
    return text.replace(old, new, count)


def L(*lines):
    return NL.join(lines)


live = read(os.path.join(HERE, "pre96_live.lua"))
ann = read(os.path.join(HERE, "pre96_ann.lua"))

# ===========================================================================
# LIVE
# ===========================================================================

# --- L1: the Accusation intro "RANGE SOURCE" paragraph ---------------------
L1_OLD = L(
    "--   THE RANGE SOURCE: Accusation's own target_intercept_range in",
    "--   unit_spec_abil.tsv = 75.0000 m - the exact reach the round-4 probe named",
    "--   and used. The enemy is offered only while unit:unit_in_range(enemy) is",
    "--   true, else while unit:unit_distance(enemy) <= FOURTH.ACCUSATION_RANGE_M,",
    "--   else while the caster itself is in melee. CONSERVATIVE: the value is a",
    "--   named constant - ONE place to tune.")
L1_NEW = L(
    "--   THE RANGE SOURCE (harness 96 - THE MOVE-ORDER ROOT CAUSE FIXED):",
    "--   Accusation's own target_intercept_range in unit_spec_abil.tsv = 75.0000 m;",
    "--   the standing 70% rule stores floor(75 * 0.70) = 52 m as the named",
    "--   FOURTH.ACCUSATION_RANGE_M. The enemy is offered ONLY while",
    "--   FOURTH.eg_enemy_within_bound is true - i.e. while the engine's distance",
    "--   `unit:unit_distance(enemy)` (EDGE-TO-EDGE metres, battle_unit.lua:160) is",
    "--   <= FOURTH.ACCUSATION_RANGE_M. THE ENGINE'S OWN LOOSER unit_in_range reach",
    "--   read IS NOT USED: the observer probe proved the offer fired at 81.3 m with",
    "--   the engine flag true while our 52 m test was false, and the engine then",
    "--   WALKED the caster in - the reported move order. The bound is a named",
    "--   constant - ONE place to tune.")
live = sub(live, L1_OLD, L1_NEW, "L1 acc prose")

# --- L2: the eg_enemy_gap comment (THE DISTANCE PRIMITIVE) -----------------
L2_OLD = L(
    "-- the gap in metres from the OWNER to a candidate enemy - the SAME",
    "-- battle_unit:unit_distance primitive the charge detector and every ally",
    "-- trigger already use. nil when the read cannot be taken.")
L2_NEW = L(
    "-- THE DISTANCE PRIMITIVE (harness 96): the gap in metres from the OWNER to a",
    "-- candidate enemy is `unit:unit_distance(enemy)` - an ENGINE-PROVIDED read",
    "-- returning the STRAIGHT-LINE distance in METRES. It is EDGE-TO-EDGE",
    "-- (bounding-box aware), per battle_unit.lua:160 - so the number the log prints",
    "-- IS exactly the number the offer test compared. The charge detector and every",
    "-- ally-range trigger already use this same primitive. nil when the read cannot",
    "-- be taken.")
live = sub(live, L2_OLD, L2_NEW, "L2 gap comment")

# --- L3: the range test function (unit_in_range -> the constant ONLY) ------
L3_OLD = L(
    "-- true while the enemy is inside the ability's own reach. unit_in_range is the",
    "-- engine's reach read (the probe logged in_range=yes(unit_in_range)); a",
    "-- readable distance is the fallback; caster-in-melee is the last resort. A",
    "-- wholly unreadable reach is treated as OUT of range (fail-safe: never offer an",
    "-- enemy the ability may not cover).",
    "function FOURTH.eg_enemy_in_range(unit, enemy)",
    T + "local okr, inr = pcall(function() return unit:unit_in_range(enemy) end)",
    T + "if okr and inr == true then return true end",
    T + "if okr and inr == false then return false end",
    T + "local gap = FOURTH.eg_enemy_gap(unit, enemy)",
    T + "if gap ~= nil then return gap <= FOURTH.ACCUSATION_RANGE_M end",
    T + "local okm, m = pcall(function() return unit:is_in_melee() end)",
    T + "return (okm and m == true)",
    "end")
L3_NEW = L(
    "-- true while the enemy lies within Accusation's 70% bound (harness 96 - THE",
    "-- FIX FOR THE MOVE ORDER). THE OFFER TEST IS THE CONSTANT ONLY:",
    "--   FOURTH.eg_enemy_gap(unit, enemy) <= FOURTH.ACCUSATION_RANGE_M",
    "-- where the gap is `unit:unit_distance(enemy)` - the engine's EDGE-TO-EDGE",
    "-- distance in metres (bounding-box aware, battle_unit.lua:160). The engine's",
    "-- own looser unit_in_range reach read is NOT consulted: the probe saw it TRUE",
    "-- at 81.3 m where our 52 m test was FALSE, and trusting it made the mod offer a",
    "-- target the engine then WALKED the caster toward. A wholly unreadable",
    "-- distance is treated as OUT of range (fail-safe: never offer an enemy the",
    "-- ability may not cover).",
    "function FOURTH.eg_enemy_within_bound(unit, enemy)",
    T + "local gap = FOURTH.eg_enemy_gap(unit, enemy)",
    T + "if gap == nil then return false end",
    T + "return gap <= FOURTH.ACCUSATION_RANGE_M",
    "end")
live = sub(live, L3_OLD, L3_NEW, "L3 range fn")

# --- L4: the offer-gate call site -----------------------------------------
live = sub(live,
    T * 8 + "and FOURTH.eg_enemy_in_range(unit, enemy) then",
    T * 8 + "and FOURTH.eg_enemy_within_bound(unit, enemy) then",
    "L4 offer gate")

# --- L5: the target-choice log (REAL distance + bound) ---------------------
L5_OLD = L(
    T * 5 + 'log("  accusation target: \'" .. etype .. "\' is the chosen enemy (" .. tostring(best_arm)',
    T * 6 + '.. ") within " .. tostring(FOURTH.ACCUSATION_RANGE_M) .. "m")')
L5_NEW = L(
    T * 5 + 'log("  accusation target: \'" .. etype .. "\' is the chosen enemy (" .. tostring(best_arm)',
    T * 6 + '.. ") distance=" .. ((best_gap ~= nil) and string.format("%.1f", best_gap) or "?")',
    T * 6 + '.. "m bound=" .. tostring(FOURTH.ACCUSATION_RANGE_M) .. "m")')
live = sub(live, L5_OLD, L5_NEW, "L5 target log")

# --- L6: the pre-cast re-check comment ------------------------------------
L6_OLD = L(
    T + "-- ACCUSATION ENEMY RE-CHECK (this round): the enemy trigger chose an ENEMY",
    T + "-- unit and left it in FOURTH.eg_enemy (the cast target is the same unit,",
    T + "-- in FOURTH.cast_target); RE-READ the condition NOW, immediately before the",
    T + "-- cast - the enemy must still be ALIVE and still IN MELEE or UNDER FIRE and",
    T + "-- still IN RANGE. If it lapsed the cast is wasted, so SKIP it rather than",
    T + "-- spend it. The chosen enemy is the CAST TARGET - NEVER the owner.")
L6_NEW = L(
    T + "-- ACCUSATION ENEMY RE-CHECK (harness 96): the enemy trigger chose an ENEMY",
    T + "-- unit and left it in FOURTH.eg_enemy (the cast target is the same unit,",
    T + "-- in FOURTH.cast_target); RE-READ the condition NOW, immediately before the",
    T + "-- cast - the enemy must still be ALIVE and still IN MELEE or UNDER FIRE and",
    T + "-- still within the 70% bound, which is RE-READ here via the engine's",
    T + "-- `unit:unit_distance(enemy)` (EDGE-TO-EDGE metres, battle_unit.lua:160) and",
    T + "-- whose REAL value is logged. If it lapsed the cast is wasted, so SKIP it",
    T + "-- rather than spend it. The chosen enemy is the CAST TARGET - NEVER the",
    T + "-- owner.")
live = sub(live, L6_OLD, L6_NEW, "L6 recheck comment")

# --- L7: the re-check gate + the lapse-skip log (REAL distance) ------------
L7_OLD = L(
    T * 2 + 'local alive_now = (ok_alive and type(alive) == "number" and alive > 0)',
    T * 2 + "local in_range_now = FOURTH.eg_enemy_in_range(unit, enemy)",
    T * 2 + "if not alive_now or not (still_melee or still_shot) or not in_range_now then",
    T * 3 + 'log("  accusation SKIPPED: the chosen enemy lapsed before the cast"',
    T * 4 + '.. " (alive=" .. tostring(alive_now) .. " melee=" .. tostring(still_melee)',
    T * 4 + '.. " shot=" .. tostring(still_shot) .. " in_range=" .. tostring(in_range_now)',
    T * 4 + '.. ") - cast not spent")')
L7_NEW = L(
    T * 2 + 'local alive_now = (ok_alive and type(alive) == "number" and alive > 0)',
    T * 2 + "-- RE-READ the bound NOW via the engine's edge-to-edge distance and log",
    T * 2 + "-- its REAL value (the same primitive the offer test used).",
    T * 2 + "local gap_now = FOURTH.eg_enemy_gap(unit, enemy)",
    T * 2 + "local in_bound_now = (gap_now ~= nil and gap_now <= FOURTH.ACCUSATION_RANGE_M)",
    T * 2 + "if not alive_now or not (still_melee or still_shot) or not in_bound_now then",
    T * 3 + 'log("  accusation SKIPPED: the chosen enemy lapsed before the cast"',
    T * 4 + '.. " (alive=" .. tostring(alive_now) .. " melee=" .. tostring(still_melee)',
    T * 4 + '.. " shot=" .. tostring(still_shot)',
    T * 4 + '.. ((gap_now ~= nil) and (" distance=" .. string.format("%.1f", gap_now) .. "m") or " distance=?")',
    T * 4 + '.. " bound=" .. tostring(FOURTH.ACCUSATION_RANGE_M) .. "m) - cast not spent")')
live = sub(live, L7_OLD, L7_NEW, "L7 recheck skip")

# --- L8: the re-check firing log (REAL distance) --------------------------
L8_OLD = L(
    T * 2 + 'log("  accusation pre-cast re-check: target still engaged (" .. tostring(FOURTH.eg_arm)',
    T * 3 + '.. ", melee=" .. tostring(still_melee) .. " shot=" .. tostring(still_shot)',
    T * 3 + '.. ", in_range=" .. tostring(in_range_now) .. ") - firing")')
L8_NEW = L(
    T * 2 + 'log("  accusation pre-cast re-check: target still engaged (" .. tostring(FOURTH.eg_arm)',
    T * 3 + '.. ", melee=" .. tostring(still_melee) .. " shot=" .. tostring(still_shot)',
    T * 3 + '.. ", distance=" .. ((gap_now ~= nil) and string.format("%.1f", gap_now) or "?")',
    T * 3 + '.. "m bound=" .. tostring(FOURTH.ACCUSATION_RANGE_M) .. "m) - firing")')
live = sub(live, L8_OLD, L8_NEW, "L8 recheck fire")

# ===========================================================================
# ANNOTATED (the reading copy: booleans, log-free, find-free)
# ===========================================================================

# --- A1: the Accusation intro "RANGE SOURCE" paragraph --------------------
A1_OLD = L(
    "--   THE RANGE SOURCE: Accusation's own target_intercept_range (unit_spec_abil",
    "--   .tsv = 75.0000 m), stored as the named FOURTH.ACCUSATION_RANGE_M.")
A1_NEW = L(
    "--   THE RANGE SOURCE (harness 96 - THE MOVE-ORDER ROOT CAUSE FIXED): the",
    "--   ability's own target_intercept_range = 75.0000 m; the 70% rule stores",
    "--   floor(75 * 0.70) = 52 m as FOURTH.ACCUSATION_RANGE_M. The enemy is offered",
    "--   ONLY while the engine's distance `unit:unit_distance(enemy)` (EDGE-TO-EDGE",
    "--   metres, battle_unit.lua:160) is <= FOURTH.ACCUSATION_RANGE_M. The engine's",
    "--   own looser unit_in_range reach read is NOT used.")
ann = sub(ann, A1_OLD, A1_NEW, "A1 acc prose")

# --- A2: the gap comment --------------------------------------------------
A2_OLD = "-- the gap in metres from the OWNER to a candidate enemy."
A2_NEW = L(
    "-- THE DISTANCE PRIMITIVE (harness 96): the gap in metres from the OWNER to a",
    "-- candidate enemy is `unit:unit_distance(enemy)` - an ENGINE-PROVIDED read",
    "-- (EDGE-TO-EDGE, bounding-box aware, battle_unit.lua:160).")
ann = sub(ann, A2_OLD, A2_NEW, "A2 gap comment")

# --- A3: the range test function ------------------------------------------
A3_OLD = L(
    "-- true while the enemy is inside the ability's own reach: unit_in_range first,",
    "-- a readable distance next, caster-in-melee last. A wholly unreadable reach is",
    "-- treated as OUT of range (fail-safe).",
    "function FOURTH.eg_enemy_in_range(unit, enemy)",
    T + "local okr, inr = pcall(function() return unit:unit_in_range(enemy) end)",
    T + "if okr and inr == true then return true end",
    T + "if okr and inr == false then return false end",
    T + "local gap = FOURTH.eg_enemy_gap(unit, enemy)",
    T + "if gap ~= nil then return gap <= FOURTH.ACCUSATION_RANGE_M end",
    T + "local okm, m = pcall(function() return unit:is_in_melee() end)",
    T + "return (okm and m == true)",
    "end")
A3_NEW = L(
    "-- true while the enemy lies within Accusation's 70% bound (harness 96 - THE",
    "-- MOVE-ORDER FIX). The test is the CONSTANT ONLY: the engine's distance",
    "-- `unit:unit_distance(enemy)` (EDGE-TO-EDGE metres, battle_unit.lua:160) <=",
    "-- FOURTH.ACCUSATION_RANGE_M. The engine's own looser unit_in_range reach read",
    "-- is NOT used; an unreadable distance is OUT of range (fail-safe).",
    "function FOURTH.eg_enemy_within_bound(unit, enemy)",
    T + "local gap = FOURTH.eg_enemy_gap(unit, enemy)",
    T + "if gap == nil then return false end",
    T + "return gap <= FOURTH.ACCUSATION_RANGE_M",
    "end")
ann = sub(ann, A3_OLD, A3_NEW, "A3 range fn")

# --- A4: the offer-gate call site -----------------------------------------
ann = sub(ann,
    T * 8 + "and FOURTH.eg_enemy_in_range(unit, enemy) then",
    T * 8 + "and FOURTH.eg_enemy_within_bound(unit, enemy) then",
    "A4 offer gate")

# --- A5: the re-check comment ---------------------------------------------
A5_OLD = L(
    T + "-- ACCUSATION ENEMY RE-CHECK (this round): re-read the chosen enemy's",
    T + "-- condition immediately before the cast - it must still be ALIVE and still",
    T + "-- IN MELEE or UNDER FIRE and still IN RANGE, or the cast is SKIPPED. The",
    T + "-- chosen enemy is the CAST TARGET - never the owner.")
A5_NEW = L(
    T + "-- ACCUSATION ENEMY RE-CHECK (harness 96): re-read the chosen enemy's",
    T + "-- condition immediately before the cast - it must still be ALIVE and still",
    T + "-- IN MELEE or UNDER FIRE and still WITHIN the 70% bound (re-read here via",
    T + "-- the engine's `unit:unit_distance(enemy)`, EDGE-TO-EDGE metres,",
    T + "-- battle_unit.lua:160), or the cast is SKIPPED. The chosen enemy is the CAST",
    T + "-- TARGET - never the owner.")
ann = sub(ann, A5_OLD, A5_NEW, "A5 recheck comment")

# --- A6: the re-check gate ------------------------------------------------
A6_OLD = L(
    T * 2 + 'local alive_now = (ok_alive and type(alive) == "number" and alive > 0)',
    T * 2 + "local in_range_now = FOURTH.eg_enemy_in_range(unit, enemy)",
    T * 2 + "if not alive_now or not (still_melee or still_shot) or not in_range_now then")
A6_NEW = L(
    T * 2 + 'local alive_now = (ok_alive and type(alive) == "number" and alive > 0)',
    T * 2 + "local gap_now = FOURTH.eg_enemy_gap(unit, enemy)",
    T * 2 + "local in_bound_now = (gap_now ~= nil and gap_now <= FOURTH.ACCUSATION_RANGE_M)",
    T * 2 + "if not alive_now or not (still_melee or still_shot) or not in_bound_now then")
ann = sub(ann, A6_OLD, A6_NEW, "A6 recheck gate")

# ===========================================================================
# sanity
# ===========================================================================
for s, nm in ((live, "live"), (ann, "ann")):
    assert "function FOURTH.eg_enemy_within_bound(unit, enemy)" in s, nm + ": new fn missing"
    assert "and FOURTH.eg_enemy_within_bound(unit, enemy) then" in s, nm + ": gate not wired"
    assert "function FOURTH.eg_enemy_in_range(unit, enemy)" not in s, nm + ": old fn still present"
    assert "unit_in_range(" not in s, nm + ": an engine unit_in_range CALL is still present"
    assert "FOURTH.ACCUSATION_RANGE_M = 52" in s, nm + ": the 70% constant is not 52"
    assert "battle_unit.lua:160" in s, nm + ": the primitive citation is missing"
# the constant is USED by both the offer test and the re-check
for s, nm in ((live, "live"), (ann, "ann")):
    assert s.count("FOURTH.ACCUSATION_RANGE_M") >= 4, nm + ": the constant is not used by both tests"
# live-only: the REAL-distance logs
assert '") distance="' in live and '", distance="' in live and '" distance="' in live, \
    "the real-distance log fragments are missing"
assert '.. "m bound=" .. tostring(FOURTH.ACCUSATION_RANGE_M) .. "m")' in live, \
    "the target-choice bound print is missing"
assert '.. "m) - firing")' in live, "the firing line is missing"
assert "accusation target: '" in live and "accusation pre-cast re-check:" in live
assert "accusation SKIPPED: the chosen enemy lapsed before the cast" in live
# the table and the other 70% constants are untouched
assert live.count(T + "{ marker = ") == 579, "the table is not 579 entries"
assert "FOURTH.RANGE_FRACTION = 0.70" in live and "FOURTH.RANGE_FRACTION = 0.70" in ann
assert "FOURTH.BLOOD_SACRIFICE_RANGE_M = 70" in live
assert "FOURTH.EAT_DA_RUNTS_RANGE_M = 70" in live
assert "local GLORIOUS_DEATH_RANGE_M = 38" in live
assert "FOURTH.VERMINKING_RANGE_M = 24" in live
assert "FOURTH.METALLURGY_RANGE_M = 24" in live
assert "FOURTH.WAVERING_RANGE_M = 24" in live
# the annotated copy stays log-free and find-free
assert "log(" not in ann, "annotated copy gained a log() call"
assert "string.find" not in ann, "annotated copy gained a string.find call"
# LF only
assert live.count(chr(13)) == 0 and ann.count(chr(13)) == 0, "CRLF leaked into a source"

write(LIVE, live)
write(ANN, ann)
print("wrote", LIVE, len(live), "bytes")
print("wrote", ANN, len(ann), "bytes")
print("OK: Accusation offer = unit_distance(enemy) <= FOURTH.ACCUSATION_RANGE_M (52 m) ONLY;")
print("    unit_in_range removed from the offer path; real distance logged at choice + re-check.")
