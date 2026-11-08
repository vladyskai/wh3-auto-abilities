# -*- coding: utf-8 -*-
"""ROUND h99 - THE TARGET-CLASS-GATED CLASS-B ENTRIES + the Rampage pair + Merciw
+ the two mid-flight entries (Daemonic Whispers, Grut's Sickle).

Writes the LIVE source and the ANNOTATED reading copy. Every edit is asserted.

The 15 entries implemented (the audit's 15 NEEDS-RULING rows):
  class-gated (10):
    overseer_of_the_unseen   -> ally_overseer        (non-commander / non-large)  real 100 -> 70
    whiplash                 -> ally_beast           (beast)                      real 100 -> 70
    iron_hand_captain        -> ally_broken          (morale broken)              real 200 -> 140
    inspired_marksmanship_i  -> ally_missile         (missile-capable)            real 100 -> 70
    inspired_marksmanship_ii -> ally_missile                                       real 100 -> 70
    inspired_marksmanship_iii-> ally_missile                                       real 100 -> 70
    makaissons_persuader     -> ally_warmachine_heal (war machine)                real 100 -> 70
    reforge                  -> ally_hellforged_heal (Hell-Forged)                real 100 -> 70
    remouldered              -> ally_monster_heal    (monster)                    real 100 -> 70
    restore                  -> ally_construct_heal  (construct)                  real 100 -> 70
  rampage pair (2):
    fury_of_khaine           -> ally_melee_buff                                   real 100 -> 70
    verminous_fury           -> ally_melee_buff                                   real 200 -> 140
  Merciw's Monstrous Regiment (1):
    merciws_monstrous_regiment -> ally_infinite_buff (NO distance bound)          real  -1 -> INFINITE
  mid-flight (2):
    slezuzus_voice           -> ally_melee_buff                                   real 200 -> 140
    gruts_sickle             -> ally_winds (HIGHEST hit points)                    real 100 -> 70
"""
import io, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = "C:/Users/vlady/Desktop"
LIVE = ROOT + "/WH3_mod/mod_source/script/battle/mod/zz_test_deadly_onslaught.lua"
ANN  = ROOT + "/WH3_auto_ability_annotated.lua"
NL = chr(10); T = chr(9)

def read(p): return io.open(p, encoding="utf-8", newline="").read()
def write(p, s): io.open(p, "w", encoding="utf-8", newline="").write(s)
def L(*ls): return NL.join(ls)

def sub(text, old, new, label, count=1):
    n = text.count(old)
    assert n == count, "%s: %d matches (want %d)" % (label, n, count)
    return text.replace(old, new, count)

def replace_block(text, start, end, new, label):
    i = text.find(start)
    assert i >= 0, label + ": start not found"
    assert text.find(start, i + 1) < 0, label + ": start not unique"
    j = text.find(end, i)
    assert j >= 0, label + ": end not found"
    return text[:i] + new + text[j + len(end):]

BOUND = lambda real: int(real * 0.70 + 1e-9)

# ---------------------------------------------------------------- the 15 entries
# marker -> (trigger, real_or_None_for_infinite, entry_number)
PLAN = {
    "overseer_of_the_unseen":    ("ally_overseer",         100, 239),
    "whiplash":                  ("ally_beast",            100, 511),
    "iron_hand_captain":         ("ally_broken",           200, 364),
    "inspired_marksmanship_i":   ("ally_missile",          100, 361),
    "inspired_marksmanship_ii":  ("ally_missile",          100, 362),
    "inspired_marksmanship_iii": ("ally_missile",          100, 363),
    "makaissons_persuader":      ("ally_warmachine_heal",  100, 540),
    "reforge":                   ("ally_hellforged_heal",  100, 548),
    "remouldered":               ("ally_monster_heal",     100, 551),
    "restore":                   ("ally_construct_heal",   100, 552),
    "fury_of_khaine":            ("ally_melee_buff",       100, 214),
    "verminous_fury":            ("ally_melee_buff",       200, 495),
    "merciws_monstrous_regiment":("ally_infinite_buff",   None, 383),
    "slezuzus_voice":            ("ally_melee_buff",       200, 305),
    "gruts_sickle":              ("ally_winds",            100, 343),
}
print("entries: %d" % len(PLAN))
from collections import Counter
print("triggers:", dict(Counter(v[0] for v in PLAN.values())))
print("constants:", dict(Counter("R%d=%d" % (v[1], BOUND(v[1])) for v in PLAN.values() if v[1] is not None)))

CLSFRAG = read(HERE + "/classes_frag.lua").rstrip(NL)

live = read(HERE + "/pre99_live.lua")
ann  = read(HERE + "/pre99_ann.lua")

# ===========================================================================
# 1. THE 200 m ALLY CONSTANT (both files).
# ===========================================================================
live = sub(live, "FOURTH.ALLY_CAST_R150 = 105", "FOURTH.ALLY_CAST_R150 = 105" + NL + "FOURTH.ALLY_CAST_R200 = 140",
    "live R200 const")
ann  = sub(ann,  "FOURTH.ALLY_CAST_R150 = 105", "FOURTH.ALLY_CAST_R150 = 105" + NL + "FOURTH.ALLY_CAST_R200 = 140",
    "ann R200 const")
live = sub(live, "\t[150] = FOURTH.ALLY_CAST_R150,", "\t[150] = FOURTH.ALLY_CAST_R150," + NL + "\t[200] = FOURTH.ALLY_CAST_R200,",
    "live R200 map")
ann  = sub(ann,  "\t[150] = FOURTH.ALLY_CAST_R150,", "\t[150] = FOURTH.ALLY_CAST_R150," + NL + "\t[200] = FOURTH.ALLY_CAST_R200,",
    "ann R200 map")

# ===========================================================================
# 2. THE CLASS-KEY TABLES + the class-gate helpers (both files), inserted
#    immediately BEFORE the shared ally picker.
# ===========================================================================
HELPERS = L(
    "",
    "-- THE TARGET-CLASS GATE (harness 99): the CURRENT entry's required class, or",
    "-- \"broken\" for the morale gate, or nil for a plain ally pick. Set by the",
    "-- entry's own evaluator and cleared by the poll before every evaluate.",
    "FOURTH.ab_filter = nil",
    "-- true when THIS entry's cast carries NO distance bound (Merciw's Monstrous",
    "-- Regiment - infinite range per the wiki).",
    "FOURTH.ab_infinite = nil",
    "",
    "-- the printed bound text: \"none (infinite range per wiki)\" for an unbounded",
    "-- entry, otherwise the ability's own named 70% constant in metres.",
    "function FOURTH.ab_bound_text()",
    "\tif FOURTH.ab_infinite then return \"none (infinite range per wiki)\" end",
    "\treturn tostring(FOURTH.ab_range_m) .. \"m\"",
    "end",
    "",
    "-- MORALE-BROKEN read for the Iron-Handed Captain gate: the engine's per-unit",
    "-- MoraleState context string; only the exact state name \"broken\" counts",
    "-- (fail-closed: an unreadable read is NOT broken).",
    "function FOURTH.morale_broken(unit)",
    "\tlocal ok, st = pcall(function() return FOURTH.context_value(unit, \"MoraleState\") end)",
    "\tif not ok then return false end",
    "\treturn st == \"broken\"",
    "end",
    "",
    "-- true when `unit` passes THIS entry's TARGET-CLASS gate (FOURTH.ab_filter).",
    "-- nil filter -> every unit passes; a class name -> the unit's type() key must",
    "-- be a member of that derived list; \"broken\" -> its morale must be broken.",
    "-- A missing / unreadable read FAILS CLOSED (the unit is not offered).",
    "function FOURTH.ab_filter_ok(unit)",
    "\tlocal f = FOURTH.ab_filter",
    "\tif f == nil then return true end",
    "\tif f == \"broken\" then return FOURTH.morale_broken(unit) end",
    "\treturn FOURTH.class_member(unit, f)",
    "end",
    "",
)
BLOCK_NEW = CLSFRAG + NL + NL + HELPERS
PICKER_START = "-- THE SHARED ALLY PICKER (Class B): walk the tracked friendly units and keep"
live = sub(live, PICKER_START, BLOCK_NEW + PICKER_START, "live class block")
ann  = sub(ann,  PICKER_START, BLOCK_NEW + PICKER_START, "ann class block")

# ===========================================================================
# 3. ab_gap_ok honours the infinite flag (both files).
# ===========================================================================
GAP_OLD = L(
    "function FOURTH.ab_gap_ok(gap)",
    "\tif gap == nil then return true end",
    "\tlocal bound = FOURTH.ab_range_m",
    "\tif bound == nil then return true end",
    "\treturn gap <= bound",
    "end")
GAP_NEW = L(
    "function FOURTH.ab_gap_ok(gap)",
    "\t-- Merciw's Monstrous Regiment: NO distance bound at all (infinite range",
    "\t-- per the wiki).",
    "\tif FOURTH.ab_infinite then return true end",
    "\tif gap == nil then return true end",
    "\tlocal bound = FOURTH.ab_range_m",
    "\tif bound == nil then return true end",
    "\treturn gap <= bound",
    "end")
live = sub(live, GAP_OLD, GAP_NEW, "live ab_gap_ok")
ann  = sub(ann,  GAP_OLD, GAP_NEW, "ann ab_gap_ok")

# ===========================================================================
# 4. THE SHARED PICKER - replaced wholesale (both files): adds the class gate,
#    the "winds" max-HP pick rule, the infinite bound and the bound text.
# ===========================================================================
PICK_LIVE = L(
    "-- THE SHARED ALLY PICKER (Class B): walk the tracked friendly units and keep",
    "-- the ones that are ALIVE, NOT the caster and NOT routing; a TARGET-CLASS gate",
    "-- (FOURTH.ab_filter, harness 99) is applied to every candidate FIRST; the",
    "-- family rule then chooses - \"heal\" = the LOWEST-health ally at or below 75%,",
    "-- \"wavering\" = the CLOSEST wavering ally, \"winds\" = the ally with the MOST",
    "-- ABSOLUTE HIT POINTS REMAINING (max HealthValue - the recipient of Grut's",
    "-- Sickle pays a health cost, so the sturdiest unit can best afford it),",
    "-- \"buff\" = the CLOSEST ally. The chosen ally rides FOURTH.cast_target (the",
    "-- CAST TARGET), FOURTH.ab_ally (the pre-cast re-check slot) and the FRESH",
    "-- caster/ally script_units. Returns the reason string, or nil when nothing",
    "-- qualifies. The OWNER is NEVER the target.",
    "function FOURTH.ab_pick_ally(unit, routing, family)",
    "\tFOURTH.ab_family = family",
    "\tlocal best_ally, best_gap, best_hp, best_val = nil, nil, nil, nil",
    "\tif not routing then",
    "\t\tlocal self_id = tostring(unit:unique_ui_id())",
    "\t\tfor i = 1, #tracked_units do",
    "\t\t\tlocal other = tracked_units[i] and tracked_units[i].unit",
    "\t\t\tif other ~= nil and other ~= unit and other:number_of_men_alive() > 0 then",
    "\t\t\t\tif tostring(other:unique_ui_id()) ~= self_id and not unit_is_routing(other)",
    "\t\t\t\t\tand FOURTH.ab_filter_ok(other) then",
    "\t\t\t\t\tlocal eligible = false",
    "\t\t\t\t\tlocal hp = nil",
    "\t\t\t\t\tlocal val = nil",
    "\t\t\t\t\tif family == \"heal\" then",
    "\t\t\t\t\t\thp = FOURTH.context_value(other, \"HealthPercent\")",
    "\t\t\t\t\t\teligible = (type(hp) == \"number\" and hp <= 75)",
    "\t\t\t\t\telseif family == \"wavering\" then",
    "\t\t\t\t\t\teligible = (FOURTH.wavering(other) == true)",
    "\t\t\t\t\telseif family == \"winds\" then",
    "\t\t\t\t\t\tval = FOURTH.context_value(other, \"HealthValue\")",
    "\t\t\t\t\t\teligible = (type(val) == \"number\")",
    "\t\t\t\t\telse",
    "\t\t\t\t\t\teligible = true",
    "\t\t\t\t\tend",
    "\t\t\t\t\tif eligible then",
    "\t\t\t\t\t\tlocal gap = FOURTH.ab_ally_gap(unit, other)",
    "\t\t\t\t\t\tif FOURTH.ab_gap_ok(gap) then",
    "\t\t\t\t\t\t\tlocal better = false",
    "\t\t\t\t\t\t\tif best_ally == nil then",
    "\t\t\t\t\t\t\t\tbetter = true",
    "\t\t\t\t\t\t\telseif family == \"heal\" then",
    "\t\t\t\t\t\t\t\tbetter = (type(hp) == \"number\" and type(best_hp) == \"number\" and hp < best_hp)",
    "\t\t\t\t\t\t\telseif family == \"winds\" then",
    "\t\t\t\t\t\t\t\tbetter = (type(val) == \"number\" and (type(best_val) ~= \"number\" or val > best_val))",
    "\t\t\t\t\t\t\telse",
    "\t\t\t\t\t\t\t\tbetter = (gap ~= nil and (best_gap == nil or gap < best_gap))",
    "\t\t\t\t\t\t\tend",
    "\t\t\t\t\t\t\tif better then",
    "\t\t\t\t\t\t\t\tbest_ally, best_gap, best_hp, best_val = other, gap, hp, val",
    "\t\t\t\t\t\t\tend",
    "\t\t\t\t\t\tend",
    "\t\t\t\t\tend",
    "\t\t\t\tend",
    "\t\t\tend",
    "\t\tend",
    "\tend",
    "\tif best_ally == nil then return nil end",
    "\tlocal atype = \"ally\"",
    "\tpcall(function() atype = tostring(best_ally:type()) end)",
    "\tlog(\"  \" .. (FOURTH.ab_marker or \"ally\") .. \" ally: '\" .. atype .. \"' is the chosen ally (\"",
    "\t\t.. tostring(family)",
    "\t\t.. ((FOURTH.ab_filter ~= nil) and (\", gate=\" .. tostring(FOURTH.ab_filter)) or \"\")",
    "\t\t.. \") distance=\"",
    "\t\t.. ((best_gap ~= nil) and string.format(\"%.1f\", best_gap) or \"?\")",
    "\t\t.. \"m bound=\" .. FOURTH.ab_bound_text())",
    "\tFOURTH.ab_ally = best_ally",
    "\tFOURTH.ab_caster_su = FOURTH.ab_fresh_friend_su(unit)",
    "\tFOURTH.ab_ally_su = FOURTH.ab_fresh_friend_su(best_ally)",
    "\tFOURTH.cast_target = best_ally",
    "\tif family == \"heal\" then",
    "\t\treturn string.format(\"%s: lowest-health ally %d%% (<= 75%%), cast on ally\",",
    "\t\t\ttostring(FOURTH.ab_marker or \"ally\"), math.floor(best_hp or 0))",
    "\telseif family == \"wavering\" then",
    "\t\treturn tostring(FOURTH.ab_marker or \"ally\") .. \": wavering ally in range, cast on ally\"",
    "\telseif family == \"winds\" then",
    "\t\treturn string.format(\"%s: highest-hit-point ally %d hp (HealthValue), cast on ally\",",
    "\t\t\ttostring(FOURTH.ab_marker or \"ally\"), math.floor(best_val or 0))",
    "\telseif FOURTH.ab_infinite then",
    "\t\treturn tostring(FOURTH.ab_marker or \"ally\")",
    "\t\t\t.. \": closest ally in range, no distance bound (infinite range per wiki), cast on ally\"",
    "\telseif FOURTH.ab_filter ~= nil then",
    "\t\treturn tostring(FOURTH.ab_marker or \"ally\") .. \": closest \"",
    "\t\t\t.. tostring(FOURTH.ab_filter) .. \"-class ally in range, cast on ally\"",
    "\tend",
    "\treturn tostring(FOURTH.ab_marker or \"ally\") .. \": closest ally in range, cast on ally\"",
    "end")
live = replace_block(live, PICKER_START, NL + "end" + NL, PICK_LIVE + NL, "live picker")

PICK_ANN = L(
    "-- THE SHARED ALLY PICKER (Class B): walk the tracked friendly units and keep",
    "-- the ones that are ALIVE, NOT the caster and NOT routing; a TARGET-CLASS gate",
    "-- (FOURTH.ab_filter) is applied to every candidate FIRST; the family rule then",
    "-- chooses - \"heal\" = the LOWEST-health ally at or below 75%, \"wavering\" = the",
    "-- CLOSEST wavering ally, \"winds\" = the ally with the MOST ABSOLUTE HIT POINTS",
    "-- REMAINING (max HealthValue), \"buff\" = the CLOSEST ally. The chosen ally rides",
    "-- FOURTH.cast_target, FOURTH.ab_ally and the FRESH caster/ally script_units.",
    "-- Returns true when an ally was chosen. The OWNER is NEVER the target.",
    "function FOURTH.ab_pick_ally(unit, routing, family)",
    "\tFOURTH.ab_family = family",
    "\tlocal best_ally, best_gap, best_hp, best_val = nil, nil, nil, nil",
    "\tif not routing then",
    "\t\tlocal self_id = tostring(unit:unique_ui_id())",
    "\t\tfor i = 1, #tracked_units do",
    "\t\t\tlocal other = tracked_units[i] and tracked_units[i].unit",
    "\t\t\tif other ~= nil and other ~= unit and other:number_of_men_alive() > 0 then",
    "\t\t\t\tif tostring(other:unique_ui_id()) ~= self_id and not unit_is_routing(other)",
    "\t\t\t\t\tand FOURTH.ab_filter_ok(other) then",
    "\t\t\t\t\tlocal eligible = false",
    "\t\t\t\t\tlocal hp = nil",
    "\t\t\t\t\tlocal val = nil",
    "\t\t\t\t\tif family == \"heal\" then",
    "\t\t\t\t\t\thp = FOURTH.context_value(other, \"HealthPercent\")",
    "\t\t\t\t\t\teligible = (type(hp) == \"number\" and hp <= 75)",
    "\t\t\t\t\telseif family == \"wavering\" then",
    "\t\t\t\t\t\teligible = (FOURTH.wavering(other) == true)",
    "\t\t\t\t\telseif family == \"winds\" then",
    "\t\t\t\t\t\tval = FOURTH.context_value(other, \"HealthValue\")",
    "\t\t\t\t\t\teligible = (type(val) == \"number\")",
    "\t\t\t\t\telse",
    "\t\t\t\t\t\teligible = true",
    "\t\t\t\t\tend",
    "\t\t\t\t\tif eligible then",
    "\t\t\t\t\t\tlocal gap = FOURTH.ab_ally_gap(unit, other)",
    "\t\t\t\t\t\tif FOURTH.ab_gap_ok(gap) then",
    "\t\t\t\t\t\t\tlocal better = false",
    "\t\t\t\t\t\t\tif best_ally == nil then",
    "\t\t\t\t\t\t\t\tbetter = true",
    "\t\t\t\t\t\t\telseif family == \"heal\" then",
    "\t\t\t\t\t\t\t\tbetter = (type(hp) == \"number\" and type(best_hp) == \"number\" and hp < best_hp)",
    "\t\t\t\t\t\t\telseif family == \"winds\" then",
    "\t\t\t\t\t\t\t\tbetter = (type(val) == \"number\" and (type(best_val) ~= \"number\" or val > best_val))",
    "\t\t\t\t\t\t\telse",
    "\t\t\t\t\t\t\t\tbetter = (gap ~= nil and (best_gap == nil or gap < best_gap))",
    "\t\t\t\t\t\t\tend",
    "\t\t\t\t\t\t\tif better then",
    "\t\t\t\t\t\t\t\tbest_ally, best_gap, best_hp, best_val = other, gap, hp, val",
    "\t\t\t\t\t\t\tend",
    "\t\t\t\t\t\tend",
    "\t\t\t\t\tend",
    "\t\t\t\tend",
    "\t\t\tend",
    "\t\tend",
    "\tend",
    "\tif best_ally == nil then return false end",
    "\tFOURTH.ab_ally = best_ally",
    "\tFOURTH.ab_caster_su = FOURTH.ab_fresh_friend_su(unit)",
    "\tFOURTH.ab_ally_su = FOURTH.ab_fresh_friend_su(best_ally)",
    "\tFOURTH.cast_target = best_ally",
    "\treturn true",
    "end")
ann  = replace_block(ann, PICKER_START, NL + "end" + NL, PICK_ANN + NL, "ann picker")

# ===========================================================================
# 5. THE TEN NEW TARGET-CLASS EVALUATORS (both files), inserted after the
#    existing ally_melee_buff evaluator.
# ===========================================================================
MB_START = "-- ally_melee_buff: the DEFAULT in-melee/not-routing shape."
MB_END = "\treturn FOURTH.ab_pick_ally(unit, routing, \"buff\")" + NL + "end" + NL

EV_LIVE = L(
    "",
    "-- TARGET-CLASS GATED ALLY FAMILIES (harness 99). Each sets FOURTH.ab_filter",
    "-- to its required class (or \"broken\" for the morale gate) and rides the",
    "-- SHARED ally picker. The ONLY offer gates are: the ally is ALIVE, NOT the",
    "-- caster, NOT routing, PASSES the class gate, and lies within the ability's",
    "-- OWN 70% bound (SKIPPED entirely for Merciw's - infinite range per the wiki).",
    "-- The CAST TARGET is ALWAYS the qualifying ally - NEVER the caster.",
    "function FOURTH.evaluate_ally_overseer(unit, routing)",
    "\tFOURTH.ab_filter = \"overseer\"",
    "\treturn FOURTH.ab_pick_ally(unit, routing, \"buff\")",
    "end",
    "",
    "-- whiplash: the target must be a BEAST (FOURTH.class_keys.beast).",
    "function FOURTH.evaluate_ally_beast(unit, routing)",
    "\tFOURTH.ab_filter = \"beast\"",
    "\treturn FOURTH.ab_pick_ally(unit, routing, \"buff\")",
    "end",
    "",
    "-- iron_hand_captain: the target's morale must be BROKEN.",
    "function FOURTH.evaluate_ally_broken(unit, routing)",
    "\tFOURTH.ab_filter = \"broken\"",
    "\treturn FOURTH.ab_pick_ally(unit, routing, \"buff\")",
    "end",
    "",
    "-- inspired_marksmanship i/ii/iii: the target must be MISSILE-CAPABLE.",
    "function FOURTH.evaluate_ally_missile(unit, routing)",
    "\tFOURTH.ab_filter = \"missile\"",
    "\treturn FOURTH.ab_pick_ally(unit, routing, \"buff\")",
    "end",
    "",
    "-- makaissons_persuader: the target must be a WAR MACHINE (a repair).",
    "function FOURTH.evaluate_ally_warmachine_heal(unit, routing)",
    "\tFOURTH.ab_filter = \"warmachine\"",
    "\treturn FOURTH.ab_pick_ally(unit, routing, \"heal\")",
    "end",
    "",
    "-- reforge: the target must carry the HELL-FORGED attribute (a repair).",
    "function FOURTH.evaluate_ally_hellforged_heal(unit, routing)",
    "\tFOURTH.ab_filter = \"hellforged\"",
    "\treturn FOURTH.ab_pick_ally(unit, routing, \"heal\")",
    "end",
    "",
    "-- remouldered: the target must be a MONSTER (a heal + combat buff).",
    "function FOURTH.evaluate_ally_monster_heal(unit, routing)",
    "\tFOURTH.ab_filter = \"monster\"",
    "\treturn FOURTH.ab_pick_ally(unit, routing, \"heal\")",
    "end",
    "",
    "-- restore: the target must be a CONSTRUCT (a heal).",
    "function FOURTH.evaluate_ally_construct_heal(unit, routing)",
    "\tFOURTH.ab_filter = \"construct\"",
    "\treturn FOURTH.ab_pick_ally(unit, routing, \"heal\")",
    "end",
    "",
    "-- merciws_monstrous_regiment: an ally-targeted buff with NO distance bound.",
    "-- INFINITE RANGE per the wiki (target_intercept_range = -1.0 = no real range),",
    "-- so the offer test is skipped ENTIRELY - the chosen ally is the closest",
    "-- qualifying one, however far. The REAL distance is still logged for",
    "-- diagnosis (the picker and the pre-cast re-check both print it).",
    "function FOURTH.evaluate_ally_infinite_buff(unit, routing)",
    "\tFOURTH.ab_infinite = true",
    "\treturn FOURTH.ab_pick_ally(unit, routing, \"buff\")",
    "end",
    "",
    "-- gruts_sickle: ally-targeted, but the PICK RULE is the ally with the",
    "-- HIGHEST ABSOLUTE HIT POINTS REMAINING (max HealthValue), not the lowest -",
    "-- the recipient pays a health COST for the winds recharge, so the sturdiest",
    "-- unit can best afford it. No health-percentage gate.",
    "function FOURTH.evaluate_ally_winds(unit, routing)",
    "\treturn FOURTH.ab_pick_ally(unit, routing, \"winds\")",
    "end",
    "",
)
EV_ANN = EV_LIVE
live = sub(live, MB_END, MB_END + EV_LIVE, "live evaluators")
ann  = sub(ann,  MB_END, MB_END + EV_ANN, "ann evaluators")

# ===========================================================================
# 6. THE RE-CHECK BOUND TEXT (live only - the ann copy is log-free).
# ===========================================================================
live = sub(live, '.. " bound=" .. tostring(ab_bound_now) .. "m) - cast not spent")',
    '.. " bound=" .. FOURTH.ab_bound_text() .. ") - cast not spent")', "live lapse log")
live = sub(live, '.. "m bound=" .. tostring(ab_bound_now) .. "m) - firing")',
    '.. " bound=" .. FOURTH.ab_bound_text() .. ") - firing")', "live recheck log")

# ===========================================================================
# 7. THE POLL CLEAR (both files): also clear the class gate + infinite flag.
# ===========================================================================
POLL_OLD = L(
    "\t\t\t\t\tFOURTH.ab_ally = nil",
    "\t\t\t\t\tFOURTH.ab_caster_su = nil",
    "\t\t\t\t\tFOURTH.ab_ally_su = nil",
    "\t\t\t\t\tFOURTH.ab_family = nil")
POLL_NEW = POLL_OLD + NL + L(
    "\t\t\t\t\tFOURTH.ab_filter = nil",
    "\t\t\t\t\tFOURTH.ab_infinite = nil")
live = sub(live, POLL_OLD, POLL_NEW, "live poll clear")
ann  = sub(ann,  POLL_OLD, POLL_NEW, "ann poll clear")

# ===========================================================================
# 8. THE EVALUATORS MAP + THE TIP MAP (both files).
# ===========================================================================
MAP_OLD = L("\tally_melee_buff = FOURTH.evaluate_ally_melee_buff,", "}")
MAP_NEW = L(
    "\tally_melee_buff = FOURTH.evaluate_ally_melee_buff,",
    "\t-- THE TARGET-CLASS GATED FAMILIES (harness 99) + the unbounded / winds forms.",
    "\tally_overseer = FOURTH.evaluate_ally_overseer,",
    "\tally_beast = FOURTH.evaluate_ally_beast,",
    "\tally_broken = FOURTH.evaluate_ally_broken,",
    "\tally_missile = FOURTH.evaluate_ally_missile,",
    "\tally_warmachine_heal = FOURTH.evaluate_ally_warmachine_heal,",
    "\tally_hellforged_heal = FOURTH.evaluate_ally_hellforged_heal,",
    "\tally_monster_heal = FOURTH.evaluate_ally_monster_heal,",
    "\tally_construct_heal = FOURTH.evaluate_ally_construct_heal,",
    "\tally_infinite_buff = FOURTH.evaluate_ally_infinite_buff,",
    "\tally_winds = FOURTH.evaluate_ally_winds,",
    "}")
live = sub(live, MAP_OLD, MAP_NEW, "live map")
ann  = sub(ann,  MAP_OLD, MAP_NEW, "ann map")

TIP_OLD = L("\tally_melee_buff = \"When armed, fires when this unit is in melee, on an ally in range\",", "}")
TIP_NEW = L(
    "\tally_melee_buff = \"When armed, fires when this unit is in melee, on an ally in range\",",
    "\tally_overseer = \"When armed, fires on a non-commander, non-large ally in range\",",
    "\tally_beast = \"When armed, fires on a beast ally in range\",",
    "\tally_broken = \"When armed, fires on a broken-morale ally in range\",",
    "\tally_missile = \"When armed, fires on a missile-capable ally in range\",",
    "\tally_warmachine_heal = \"When armed, fires on the lowest-health war machine ally in range that is at or below 75% health\",",
    "\tally_hellforged_heal = \"When armed, fires on the lowest-health Hell-Forged ally in range that is at or below 75% health\",",
    "\tally_monster_heal = \"When armed, fires on the lowest-health monster ally in range that is at or below 75% health\",",
    "\tally_construct_heal = \"When armed, fires on the lowest-health construct ally in range that is at or below 75% health\",",
    "\tally_infinite_buff = \"When armed, fires on an ally anywhere on the field (infinite range), cast on that ally\",",
    "\tally_winds = \"When armed, fires on the ally with the most hit points remaining, cast on that ally\",",
    "}")
live = sub(live, TIP_OLD, TIP_NEW, "live tips")
ann  = sub(ann,  TIP_OLD, TIP_NEW, "ann tips")

# ===========================================================================
# 9. THE ENTRIES: move each trigger + add its own ally_range_real.
# ===========================================================================
def edit_entries(text, label):
    for m, (trig, real, num) in sorted(PLAN.items(), key=lambda kv: kv[1][2]):
        pat = re.compile(
            r'(\t\{ marker = "' + re.escape(m) + r'", name = "(?:[^"\\]|\\.)*", trigger = )'
            r'"[^"]+"(,\n\t\tbadge = "zz_auto_badge_[^"]*",\n\t\tkeys = \{[^}]*\},\n)'
            r'(\t\tox = 0, oy = 0 \},)')
        if real is None:
            new = r'\1"' + trig + r'"\2\3'
        else:
            new = r'\1"' + trig + r'"\2\t\tally_range_real = ' + str(real) + r',\n\3'
        text, n = pat.subn(new, text)
        assert n == 1, "%s entry %s: %d matches (want 1)" % (label, m, n)
    return text
live = edit_entries(live, "live")
ann  = edit_entries(ann,  "ann")

# ===========================================================================
# 10. SANITY (both files).
# ===========================================================================
NEW_ALLY_TRIG = ["ally_overseer", "ally_beast", "ally_broken", "ally_missile",
                 "ally_warmachine_heal", "ally_hellforged_heal", "ally_monster_heal",
                 "ally_construct_heal", "ally_infinite_buff", "ally_winds"]
for s, nm in ((live, "live"), (ann, "ann")):
    assert s.count(T + "{ marker = ") == 579, nm + ": table not 579 entries"
    assert s.count('badge = "') == 579, nm + ": badge count moved"
    assert s.count('trigger = "melee_unwavering"') == 373 - 10, nm + ": melee_unwavering moved wrong"
    assert s.count('trigger = "charge_or_melee"') == 26 - 1, nm + ": charge_or_melee moved wrong"
    assert s.count('trigger = "ushoran_health"') == 38 - 4, nm + ": ushoran_health moved wrong"
    assert s.count('trigger = "melee_health75"') == 1, nm + ": melee_health75 moved"
    assert s.count('trigger = "ally_melee_buff"') == 11 + 3, nm + ": ally_melee_buff count wrong"
    assert s.count('trigger = "ally_heal"') == 3, nm + ": ally_heal count wrong"
    assert s.count('trigger = "ally_heal_melee"') == 1, nm + ": ally_heal_melee count wrong"
    assert s.count('trigger = "ally_wavering"') == 2, nm + ": ally_wavering count wrong"
    for t in NEW_ALLY_TRIG:
        want = 3 if t == "ally_missile" else 1
        assert s.count('trigger = "%s"' % t) == want, nm + ": %s count wrong" % t
    assert s.count(T + T + "ally_range_real = ") == 18 + 14, nm + ": ally_range_real fields wrong"
    assert s.count("FOURTH.ALLY_CAST_R200 = 140") == 1, nm + ": R200 const missing"
    assert "\t[200] = FOURTH.ALLY_CAST_R200," in s, nm + ": R200 map missing"
    assert "FOURTH.class_keys = {" in s, nm + ": class tables missing"
    for cname, sz in (("beast", 55), ("monster", 235), ("warmachine", 68), ("construct", 29),
                      ("hellforged", 13), ("missile", 493), ("overseer", 918)):
        blk = s.split(cname + " = {", 1)[1].split("},", 1)[0]
        assert blk.count("] = true,") == sz, nm + ": %s list size wrong" % cname
    assert "function FOURTH.class_member(unit, name)" in s, nm + ": class_member missing"
    assert "function FOURTH.ab_filter_ok(unit)" in s, nm + ": ab_filter_ok missing"
    assert "function FOURTH.ab_bound_text()" in s, nm + ": ab_bound_text missing"
    assert "function FOURTH.morale_broken(unit)" in s, nm + ": morale_broken missing"
    assert 'if FOURTH.ab_infinite then return true end' in s, nm + ": infinite gate missing"
    assert "none (infinite range per wiki)" in s, nm + ": infinite log text missing"
    assert "family == \"winds\"" in s, nm + ": winds family missing"
    assert 'FOURTH.context_value(other, "HealthValue")' in s, nm + ": HealthValue read missing"
    for f in ("overseer", "beast", "broken", "missile", "warmachine_heal", "hellforged_heal",
              "monster_heal", "construct_heal", "infinite_buff", "winds"):
        assert "ally_" + f + " = FOURTH.evaluate_ally_" + f + "," in s, nm + ": %s not wired" % f
    assert s.count("FOURTH.ab_filter = nil") == 2, nm + ": ab_filter=nil count (def+clear) wrong"
    assert s.count("FOURTH.ab_infinite = nil") == 2, nm + ": ab_infinite=nil count wrong"
    assert "unit_in_range(" not in s, nm + ": the banned engine reach read came back"
    assert "string.find(" not in s, nm + ": a string.find CALL came back"
    assert s.count(chr(13)) == 0, nm + ": CRLF leaked"
if "log(" in ann:
    raise SystemExit("annotated copy gained a log()")

write(LIVE, live); write(ANN, ann)
print("wrote", LIVE, len(live))
print("wrote", ANN, len(ann))
print("OK: %d entries implemented" % len(PLAN))
