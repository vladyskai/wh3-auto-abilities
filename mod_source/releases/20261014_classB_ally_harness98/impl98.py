# -*- coding: utf-8 -*-
"""ROUND h98 - CLASS B (ally-targeted effects cast on self).

The audit's Class B (34 entries, derived programmatically from WH3_audit_report.md)
is implemented on the mod's OWN ally picker (the blood_sacrifice / eat_da_runts
shape) extended with the Class-A round's FRESH-HANDLE discipline.

Per the user's standing rule 10, the ARMY-BAR entries are SKIPPED (not
implemented, marked `skipped (army-bar ability)` in the tracker). Entries whose
audit note does not clearly fit an established trigger family, or that rule 14
flags (Rampage / drawback), or whose real range is undefined, are LEFT AS-IS and
reported as NEEDING A RULING.

Writes the LIVE source and the ANNOTATED reading copy.  Every edit is asserted.
"""
import io, os, re, json

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

# ===========================================================================
# THE DECISION TABLE (my reading of each audit note). The KEY LIST comes from
# the report (programmatic); this table records the per-entry RULING.
# family: heal / heal_melee / wavering / buff   (the four ally families)
# ===========================================================================
IMPLEMENTED = {
    # marker            : (trigger,            real,  entry_number)
    "da_boss_as_a_plan":        ("ally_melee_buff",  150, 204),
    "favour_of_the_fay":        ("ally_melee_buff",  100, 209),
    "helping_hand":             ("ally_melee_buff",   50, 220),
    "inspired_assault_i":       ("ally_melee_buff",  100, 222),
    "inspired_assault_ii":      ("ally_melee_buff",  100, 223),
    "inspired_assault_iii":     ("ally_melee_buff",  100, 224),
    "inspired_defence_i":       ("ally_melee_buff",  100, 225),
    "inspired_defence_ii":      ("ally_melee_buff",  100, 226),
    "inspired_defence_iii":     ("ally_melee_buff",  100, 227),
    "orcs_are_da_best":         ("ally_melee_buff",  150, 238),
    "hellish_vigour":           ("ally_melee_buff",   75, 349),
    "elfish_healing_herbs":     ("ally_heal",         50, 534),
    "patch_up":                 ("ally_heal",        100, 543),
    "revivification_crystal":   ("ally_heal",        100, 553),
    "captain_of_the_phoenix_guard": ("ally_heal_melee", 50, 199),
    "shock_collar":             ("ally_wavering",    100, 439),
    "were_you_goin":            ("ally_wavering",    100, 508),
}
# the ONE entry whose ally pick already shipped: the cast target is wired here
EXISTING = {"stay_here_ill_get_help": ("wavering_ally_range", 60, 250)}
ARMY_BAR = {"butcher": (198, "Meat Feast")}
NEEDS_RULING = {
    "fury_of_khaine":         (214, "rule 14: applies Rampage!; the note keeps charge_or_melee, which is not one of the ally families"),
    "overseer_of_the_unseen": (239, "needs a non-commander / non-large TARGET-CLASS filter (no existing family)"),
    "slezuzus_voice":         (305, "the note itself says 'flag for the user'"),
    "gruts_sickle":           (343, "rule 14: carries a health COST (drawback); the note says 'flag for the user'"),
    "inspired_marksmanship_i":  (361, "needs a missile-capability target gate (no existing family)"),
    "inspired_marksmanship_ii": (362, "needs a missile-capability target gate (no existing family)"),
    "inspired_marksmanship_iii":(363, "needs a missile-capability target gate (no existing family)"),
    "iron_hand_captain":      (364, "needs a 'morale at or below broken' target gate (no existing family)"),
    "merciws_monstrous_regiment": (383, "target_intercept_range = -1.0 (no real range) - no defensible 70% bound"),
    "verminous_fury":         (495, "rule 14: applies Rampage! (also Unbreakable - the Rampage flag wins)"),
    "whiplash":               (511, "needs a non-commander / beast TARGET-CLASS filter (no existing family)"),
    "makaissons_persuader":   (540, "needs a war-machine / artillery TARGET-CLASS filter (no existing family)"),
    "reforge":                (548, "needs a Hell-Forged TARGET-CLASS filter (no existing family)"),
    "remouldered":            (551, "needs a monster TARGET-CLASS filter (no existing family)"),
    "restore":                (552, "needs a construct TARGET-CLASS filter (no existing family)"),
}

joined = json.load(io.open(ROOT + "/WH3_audit/_classB_joined.json", encoding="utf-8"))
all_markers = set()
for x in joined:
    for m in x["mod_markers"]:
        all_markers.add(m)
covered = set(IMPLEMENTED) | set(EXISTING) | set(ARMY_BAR) | set(NEEDS_RULING)
assert all_markers == covered, "decision table mismatch: %s" % (all_markers ^ covered)
print("Class B: %d entries / %d markers; implemented %d, existing %d, army-bar %d, needs-ruling %d"
      % (len(joined), len(all_markers), len(IMPLEMENTED), len(EXISTING), len(ARMY_BAR), len(NEEDS_RULING)))

BOUND = lambda real: int(real * 0.70 + 1e-9)
CONST_OF = {50: "FOURTH.ALLY_CAST_R50", 60: "FOURTH.ALLY_CAST_R60", 75: "FOURTH.ALLY_CAST_R75",
            100: "FOURTH.ALLY_CAST_R100", 150: "FOURTH.ALLY_CAST_R150"}
plan = []
for m, (trig, real, num) in sorted(IMPLEMENTED.items(), key=lambda kv: kv[1][2]):
    plan.append({"marker": m, "num": num, "trigger": trig, "real": real, "bound": BOUND(real)})
for m, (trig, real, num) in EXISTING.items():
    plan.append({"marker": m, "num": num, "trigger": trig, "real": real, "bound": BOUND(real), "existing": True})
json.dump(plan, io.open(ROOT + "/WH3_audit/_classB_impl_plan.json", "w", encoding="utf-8"), indent=1)
from collections import Counter
print("constants used:", dict(Counter(CONST_OF[p["real"]] + "=" + str(p["bound"]) for p in plan)))
print("trigger counts (new/edited):", dict(Counter(p["trigger"] for p in plan)))

live = read(HERE + "/pre98_live.lua")
ann  = read(HERE + "/pre98_ann.lua")

# ===========================================================================
# 1. THE ALLY-CAST CONSTANTS (both files) - inserted after the ENEMY_CAST map.
# ===========================================================================
ANCHOR = L("\t[500] = FOURTH.ENEMY_CAST_R500,", "}", NL)
CONSTS = L(
    NL,
    NL,
    "-- ============================================================================",
    "-- THE ALLY-TARGETED CAST BOUNDS (Class B, harness 98). ONE named constant per",
    "-- REAL target_intercept_range (unit_spec_abil.tsv) - several abilities that",
    "-- share a real range SHARE the constant (stated per line below). The VALUE is",
    "-- the trigger bound = floor(real * FOURTH.RANGE_FRACTION) (70%), rounded DOWN",
    "-- to a whole metre (the +1e-9 epsilon mirrors the build assertion's floor).",
    "-- The offer test is unit:unit_distance(ally) (EDGE-TO-EDGE metres,",
    "-- battle_unit.lua:160) - NEVER the engine's own unit_in_range reach read.",
    "--   real  50.0 m ->  35  (shared: captain_of_the_phoenix_guard, helping_hand,",
    "--                          elfish_healing_herbs)",
    "--   real  60.0 m ->  42  (stay_here_ill_get_help)",
    "--   real  75.0 m ->  52  (hellish_vigour)",
    "--   real 100.0 m ->  70  (shared: favour_of_the_fay, inspired_assault_i/_ii/",
    "--                          _iii, inspired_defence_i/_ii/_iii, shock_collar,",
    "--                          were_you_goin, patch_up, revivification_crystal)",
    "--   real 150.0 m -> 105  (shared: da_boss_as_a_plan, orcs_are_da_best)",
    "-- ============================================================================",
    "FOURTH.ALLY_CAST_R50  = 35",
    "FOURTH.ALLY_CAST_R60  = 42",
    "FOURTH.ALLY_CAST_R75  = 52",
    "FOURTH.ALLY_CAST_R100 = 70",
    "FOURTH.ALLY_CAST_R150 = 105",
    "",
    "-- the ability's REAL target_intercept_range -> its named 70% ALLY bound, for",
    "-- the load-time per-ability lookup (each Class-B entry carries ally_range_real).",
    "FOURTH.ALLY_CAST = {",
    "\t[50]  = FOURTH.ALLY_CAST_R50,",
    "\t[60]  = FOURTH.ALLY_CAST_R60,",
    "\t[75]  = FOURTH.ALLY_CAST_R75,",
    "\t[100] = FOURTH.ALLY_CAST_R100,",
    "\t[150] = FOURTH.ALLY_CAST_R150,",
    "}",
)
live = sub(live, ANCHOR, ANCHOR + CONSTS, "live ally constants")
ann  = sub(ann,  ANCHOR, ANCHOR + CONSTS, "ann ally constants")

# ===========================================================================
# 2. THE ALLY PICKER + THE FOUR FAMILY EVALUATORS (both files), inserted
#    immediately before the ACCUSATION section.
# ===========================================================================
ACC_ANCHOR = "-- ACCUSATION (this round) - the FIRST ENEMY-TARGETED trigger, and the first"
assert live.count(ACC_ANCHOR) == 1 and ann.count(ACC_ANCHOR) == 1

HEADER = L(
    "-- ============================================================================",
    "-- CLASS B (harness 98) - ALLY-TARGETED EFFECTS CAST ON SELF.",
    "--   The audit's Class B: abilities the game aims at ANOTHER friendly unit while",
    "--   the mod self-casts, so the declared recipient never receives the effect.",
    "--   THE MECHANISM is the mod's OWN ally-targeting shape - the blood_sacrifice /",
    "--   eat_da_runts picker (a friendly unit other than the caster, chosen by a",
    "--   per-family rule, range-tested against a conservative named bound, the gap",
    "--   RE-READ immediately before the cast) - extended with the Class-A round's",
    "--   FRESH-HANDLE discipline: the CASTER's controller AND the chosen ALLY are",
    "--   re-enumerated from the local player's army list on the SAME tick",
    "--   (FOURTH.ab_fresh_friend_su) and the cast is issued as",
    "--   caster_su.uc:perform_special_ability(key, ally_su.unit). A controller held",
    "--   from an earlier poll silently no-ops, so the fresh fetch is what makes the",
    "--   ally-targeted cast LAND. The chosen ally still rides FOURTH.cast_target, so",
    "--   the established dispatch passes it unchanged.",
    "--   THE FOUR FAMILIES (each its own evaluator):",
    "--     ally_heal        - a PURE HEAL: pick the LOWEST-health ally in range at or",
    "--                        below 75% health (the health-only trigger family);",
    "--     ally_heal_melee  - a heal that ALSO grants armour/defence: the same pick,",
    "--                        but the OWNER must be in melee (the melee+health gate);",
    "--     ally_wavering    - an Unbreakable / morale-recovery effect: pick the",
    "--                        CLOSEST WAVERING ally in range (the wavering family);",
    "--     ally_melee_buff  - the default in-melee/not-routing shape: pick the",
    "--                        CLOSEST ally in range.",
    "--   THE RANGE: every entry carries its own REAL target_intercept_range",
    "--   (ally_range_real) mapped at load to ONE named 70% constant per real range",
    "--   (FOURTH.ALLY_CAST). The offer test is the per-ability constant ONLY - the",
    "--   gap is unit:unit_distance(ally), the engine's EDGE-TO-EDGE distance in",
    "--   metres (bounding-box aware, battle_unit.lua:160) - and NEVER the engine's",
    "--   looser unit_in_range reach read. The REAL distance is logged.",
    "--   THE LOCAL CEILING: every helper / constant / state is a FIELD of the FOURTH",
    "--   bag - NO new chunk-level locals.",
    "-- ============================================================================",
    "",
    "-- the chosen ally, the FRESH caster/ally script_units, and the current",
    "-- ability's own 70% ally bound + marker + family - all cleared before every",
    "-- evaluate, so no ability can inherit a stale ally.",
    "FOURTH.ab_ally = nil",
    "FOURTH.ab_caster_su = nil",
    "FOURTH.ab_ally_su = nil",
    "FOURTH.ab_range_m = nil",
    "FOURTH.ab_marker = nil",
    "FOURTH.ab_family = nil",
)

FRESH_HELPER = L(
    "-- re-fetch a FRIENDLY script_unit FRESH from the local player's army list THIS",
    "-- tick (never a script_unit held from an earlier poll - the Class-A lesson: a",
    "-- stale controller silently no-ops). nil when the army or the matching unit",
    "-- cannot be found.",
    "function FOURTH.ab_fresh_friend_su(unit)",
    "\tlocal ok_coll, coll = pcall(function()",
    "\t\treturn bm:get_scriptunits_for_local_players_army()",
    "\tend)",
    "\tif not ok_coll or coll == nil then return nil end",
    "\tlocal ok_n, n = pcall(function() return coll:count() end)",
    "\tif not ok_n or type(n) ~= \"number\" then return nil end",
    "\tlocal want = nil",
    "\tpcall(function() want = tostring(unit:unique_ui_id()) end)",
    "\tif want == nil then return nil end",
    "\tfor i = 1, n do",
    "\t\tlocal ok_su, su = pcall(function() return coll:item(i) end)",
    "\t\tif ok_su and su ~= nil then",
    "\t\t\tlocal u = nil",
    "\t\t\tpcall(function() u = su.unit end)",
    "\t\t\tif u ~= nil then",
    "\t\t\t\tlocal id = nil",
    "\t\t\t\tpcall(function() id = u:unique_ui_id() end)",
    "\t\t\t\tif id ~= nil and tostring(id) == want then return su end",
    "\t\t\tend",
    "\t\tend",
    "\tend",
    "\treturn nil",
    "end",
    "",
    "-- the gap in metres from the OWNER to a candidate ally - the SAME",
    "-- battle_unit:unit_distance primitive the charge detector and every ally-range",
    "-- trigger already use. nil when the read cannot be taken.",
    "function FOURTH.ab_ally_gap(unit, ally)",
    "\tlocal ok, gap = pcall(function() return ally:unit_distance(unit) end)",
    "\tif ok and type(gap) == \"number\" then return gap end",
    "\treturn nil",
    "end",
    "",
    "-- true when a gap lies within the CURRENT ability's 70% ally bound. An",
    "-- UNREADABLE gap (nil) is treated as IN range (fail-open); so is a missing",
    "-- bound (a non-ally ability never reaches here).",
    "function FOURTH.ab_gap_ok(gap)",
    "\tif gap == nil then return true end",
    "\tlocal bound = FOURTH.ab_range_m",
    "\tif bound == nil then return true end",
    "\treturn gap <= bound",
    "end",
    "",
    "-- true while the ally lies within the CURRENT ability's 70% ally bound.",
    "function FOURTH.ab_ally_in_range(unit, ally)",
    "\treturn FOURTH.ab_gap_ok(FOURTH.ab_ally_gap(unit, ally))",
    "end",
    "",
    "-- the chosen ally is STILL valid: in range AND (for a heal) still at or below",
    "-- 75% health. An unreadable health read is treated as still-valid (fail-open).",
    "function FOURTH.ab_ally_valid(unit, ally)",
    "\tif ally == nil then return false end",
    "\tif not FOURTH.ab_ally_in_range(unit, ally) then return false end",
    "\tif FOURTH.ab_family == \"heal\" then",
    "\t\tlocal hp = FOURTH.context_value(ally, \"HealthPercent\")",
    "\t\treturn (type(hp) ~= \"number\") or (hp <= 75)",
    "\tend",
    "\treturn true",
    "end",
)

# ---- the LIVE picker (returns a reason string, logs the REAL distance) ----
PICK_LIVE = L(
    "-- THE SHARED ALLY PICKER (Class B): walk the tracked friendly units and keep",
    "-- the ones that are ALIVE, NOT the caster and NOT routing; the family rule then",
    "-- chooses - \"heal\" = the LOWEST-health ally at or below 75%, \"wavering\" = the",
    "-- CLOSEST wavering ally, \"buff\" = the CLOSEST ally. The chosen ally rides",
    "-- FOURTH.cast_target (the CAST TARGET), FOURTH.ab_ally (the pre-cast re-check",
    "-- slot) and the FRESH caster/ally script_units. Returns the reason string, or",
    "-- nil when nothing qualifies. The OWNER is NEVER the target.",
    "function FOURTH.ab_pick_ally(unit, routing, family)",
    "\tFOURTH.ab_family = family",
    "\tlocal best_ally, best_gap, best_hp = nil, nil, nil",
    "\tif not routing then",
    "\t\tlocal self_id = tostring(unit:unique_ui_id())",
    "\t\tfor i = 1, #tracked_units do",
    "\t\t\tlocal other = tracked_units[i] and tracked_units[i].unit",
    "\t\t\tif other ~= nil and other ~= unit and other:number_of_men_alive() > 0 then",
    "\t\t\t\tif tostring(other:unique_ui_id()) ~= self_id and not unit_is_routing(other) then",
    "\t\t\t\t\tlocal eligible = false",
    "\t\t\t\t\tlocal hp = nil",
    "\t\t\t\t\tif family == \"heal\" then",
    "\t\t\t\t\t\thp = FOURTH.context_value(other, \"HealthPercent\")",
    "\t\t\t\t\t\teligible = (type(hp) == \"number\" and hp <= 75)",
    "\t\t\t\t\telseif family == \"wavering\" then",
    "\t\t\t\t\t\teligible = (FOURTH.wavering(other) == true)",
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
    "\t\t\t\t\t\t\telse",
    "\t\t\t\t\t\t\t\tbetter = (gap ~= nil and (best_gap == nil or gap < best_gap))",
    "\t\t\t\t\t\t\tend",
    "\t\t\t\t\t\t\tif better then",
    "\t\t\t\t\t\t\t\tbest_ally, best_gap, best_hp = other, gap, hp",
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
    "\t\t.. tostring(family) .. \") distance=\"",
    "\t\t.. ((best_gap ~= nil) and string.format(\"%.1f\", best_gap) or \"?\")",
    "\t\t.. \"m bound=\" .. tostring(FOURTH.ab_range_m) .. \"m\")",
    "\tFOURTH.ab_ally = best_ally",
    "\tFOURTH.ab_caster_su = FOURTH.ab_fresh_friend_su(unit)",
    "\tFOURTH.ab_ally_su = FOURTH.ab_fresh_friend_su(best_ally)",
    "\tFOURTH.cast_target = best_ally",
    "\tif family == \"heal\" then",
    "\t\treturn string.format(\"%s: lowest-health ally %d%% (<= 75%%), cast on ally\",",
    "\t\t\ttostring(FOURTH.ab_marker or \"ally\"), math.floor(best_hp or 0))",
    "\telseif family == \"wavering\" then",
    "\t\treturn tostring(FOURTH.ab_marker or \"ally\") .. \": wavering ally in range, cast on ally\"",
    "\telse",
    "\t\treturn tostring(FOURTH.ab_marker or \"ally\") .. \": closest ally in range, cast on ally\"",
    "\tend",
    "end",
)
# ---- the ANNOTATED picker (log-free, boolean) ----
PICK_ANN = L(
    "-- THE SHARED ALLY PICKER (Class B): walk the tracked friendly units and keep",
    "-- the ones that are ALIVE, NOT the caster and NOT routing; the family rule then",
    "-- chooses - \"heal\" = the LOWEST-health ally at or below 75%, \"wavering\" = the",
    "-- CLOSEST wavering ally, \"buff\" = the CLOSEST ally. The chosen ally rides",
    "-- FOURTH.cast_target, FOURTH.ab_ally and the FRESH caster/ally script_units.",
    "-- Returns true when an ally was chosen. The OWNER is NEVER the target.",
    "function FOURTH.ab_pick_ally(unit, routing, family)",
    "\tFOURTH.ab_family = family",
    "\tlocal best_ally, best_gap, best_hp = nil, nil, nil",
    "\tif not routing then",
    "\t\tlocal self_id = tostring(unit:unique_ui_id())",
    "\t\tfor i = 1, #tracked_units do",
    "\t\t\tlocal other = tracked_units[i] and tracked_units[i].unit",
    "\t\t\tif other ~= nil and other ~= unit and other:number_of_men_alive() > 0 then",
    "\t\t\t\tif tostring(other:unique_ui_id()) ~= self_id and not unit_is_routing(other) then",
    "\t\t\t\t\tlocal eligible = false",
    "\t\t\t\t\tlocal hp = nil",
    "\t\t\t\t\tif family == \"heal\" then",
    "\t\t\t\t\t\thp = FOURTH.context_value(other, \"HealthPercent\")",
    "\t\t\t\t\t\teligible = (type(hp) == \"number\" and hp <= 75)",
    "\t\t\t\t\telseif family == \"wavering\" then",
    "\t\t\t\t\t\teligible = (FOURTH.wavering(other) == true)",
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
    "\t\t\t\t\t\t\telse",
    "\t\t\t\t\t\t\t\tbetter = (gap ~= nil and (best_gap == nil or gap < best_gap))",
    "\t\t\t\t\t\t\tend",
    "\t\t\t\t\t\t\tif better then",
    "\t\t\t\t\t\t\t\tbest_ally, best_gap, best_hp = other, gap, hp",
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
    "end",
)

EV_LIVE = L(
    "-- ally_heal: a PURE HEAL - the health-only trigger family. Fires when a",
    "-- friendly unit other than the caster is at or below 75% health within the",
    "-- ability's own 70% bound; the LOWEST-health such ally is the CAST TARGET.",
    "function FOURTH.evaluate_ally_heal(unit, routing)",
    "\treturn FOURTH.ab_pick_ally(unit, routing, \"heal\")",
    "end",
    "",
    "-- ally_heal_melee: a heal that ALSO grants armour/defence - the melee+health",
    "-- gate (the Potion-of-Toughness pattern). The OWNER must be in melee; the",
    "-- LOWEST-health ally at or below 75% within the bound is the CAST TARGET.",
    "function FOURTH.evaluate_ally_heal_melee(unit, routing)",
    "\tif routing or not unit:is_in_melee() then return nil end",
    "\tlocal reason = FOURTH.ab_pick_ally(unit, routing, \"heal\")",
    "\tif reason ~= nil then",
    "\t\treason = \"in melee, \" .. reason",
    "\tend",
    "\treturn reason",
    "end",
    "",
    "-- ally_wavering: an Unbreakable / morale-recovery effect - the wavering family.",
    "-- The CLOSEST WAVERING ally within the bound is the CAST TARGET. The owner need",
    "-- not be in melee and need not be wavering.",
    "function FOURTH.evaluate_ally_wavering(unit, routing)",
    "\treturn FOURTH.ab_pick_ally(unit, routing, \"wavering\")",
    "end",
    "",
    "-- ally_melee_buff: the DEFAULT in-melee/not-routing shape. The OWNER must be in",
    "-- melee and neither routing nor wavering (fail-open morale); the CLOSEST ally",
    "-- within the bound is the CAST TARGET.",
    "function FOURTH.evaluate_ally_melee_buff(unit, routing)",
    "\tif routing or not unit:is_in_melee() then return nil end",
    "\tif FOURTH.wavering(unit) == true then return nil end",
    "\treturn FOURTH.ab_pick_ally(unit, routing, \"buff\")",
    "end",
)
EV_ANN = L(
    "-- ally_heal: a PURE HEAL - the health-only trigger family. Fires when a",
    "-- friendly unit other than the caster is at or below 75% health within the",
    "-- ability's own 70% bound; the LOWEST-health such ally is the CAST TARGET.",
    "function FOURTH.evaluate_ally_heal(unit, routing)",
    "\treturn FOURTH.ab_pick_ally(unit, routing, \"heal\")",
    "end",
    "",
    "-- ally_heal_melee: a heal that ALSO grants armour/defence - the melee+health",
    "-- gate. The OWNER must be in melee; the LOWEST-health ally at or below 75%",
    "-- within the bound is the CAST TARGET.",
    "function FOURTH.evaluate_ally_heal_melee(unit, routing)",
    "\tif routing or not unit:is_in_melee() then return false end",
    "\treturn FOURTH.ab_pick_ally(unit, routing, \"heal\")",
    "end",
    "",
    "-- ally_wavering: an Unbreakable / morale-recovery effect - the wavering family.",
    "-- The CLOSEST WAVERING ally within the bound is the CAST TARGET.",
    "function FOURTH.evaluate_ally_wavering(unit, routing)",
    "\treturn FOURTH.ab_pick_ally(unit, routing, \"wavering\")",
    "end",
    "",
    "-- ally_melee_buff: the DEFAULT in-melee/not-routing shape. The OWNER must be in",
    "-- melee and neither routing nor wavering (fail-open morale); the CLOSEST ally",
    "-- within the bound is the CAST TARGET.",
    "function FOURTH.evaluate_ally_melee_buff(unit, routing)",
    "\tif routing or not unit:is_in_melee() then return false end",
    "\tif FOURTH.wavering(unit) == true then return false end",
    "\treturn FOURTH.ab_pick_ally(unit, routing, \"buff\")",
    "end",
)

LIVE_BLOCK = HEADER + NL + NL + FRESH_HELPER + NL + NL + PICK_LIVE + NL + NL + EV_LIVE + NL + NL
ANN_BLOCK  = HEADER + NL + NL + FRESH_HELPER + NL + NL + PICK_ANN  + NL + NL + EV_ANN  + NL + NL
live = sub(live, ACC_ANCHOR, LIVE_BLOCK + ACC_ANCHOR, "live classB block")
ann  = sub(ann,  ACC_ANCHOR, ANN_BLOCK  + ACC_ANCHOR, "ann classB block")

# ===========================================================================
# 3. THE FRESH-HANDLE CAST BRANCH (attempt_activation, both files).
# ===========================================================================
UC_LIVE_OLD = L(
    "\tlocal uc = script_unit.uc",
    "\tif FOURTH.eg_enemy ~= nil and FOURTH.eg_caster_su ~= nil and FOURTH.eg_caster_su.uc ~= nil then",
    "\t\tuc = FOURTH.eg_caster_su.uc",
    "\tend")
UC_NEW_LIVE = UC_LIVE_OLD + NL + L(
    "\t-- CLASS B (harness 98): the ALLY-TARGETED cast uses the FRESH caster",
    "\t-- controller AND the FRESH ally unit, both re-enumerated from the local",
    "\t-- player's army list THIS tick - a controller held from an earlier poll",
    "\t-- silently no-ops. The chosen ally is the CAST TARGET - NEVER the owner.",
    "\tif FOURTH.ab_ally ~= nil then",
    "\t\tif FOURTH.ab_caster_su ~= nil and FOURTH.ab_caster_su.uc ~= nil then",
    "\t\t\tuc = FOURTH.ab_caster_su.uc",
    "\t\tend",
    "\t\tif FOURTH.ab_ally_su ~= nil and FOURTH.ab_ally_su.unit ~= nil then",
    "\t\t\ttarget = FOURTH.ab_ally_su.unit",
    "\t\tend",
    "\tend")
live = sub(live, UC_LIVE_OLD, UC_NEW_LIVE, "live fresh-handle branch")

UC_ANN_OLD = L(
    "\tlocal uc = script_unit.uc   -- the unit's order controller",
    "\tif FOURTH.eg_enemy ~= nil and FOURTH.eg_caster_su ~= nil and FOURTH.eg_caster_su.uc ~= nil then",
    "\t\tuc = FOURTH.eg_caster_su.uc",
    "\tend")
UC_NEW_ANN = UC_ANN_OLD + NL + L(
    "\t-- CLASS B (harness 98): the ALLY-TARGETED cast uses the FRESH caster",
    "\t-- controller AND the FRESH ally unit, both re-enumerated THIS tick.",
    "\tif FOURTH.ab_ally ~= nil then",
    "\t\tif FOURTH.ab_caster_su ~= nil and FOURTH.ab_caster_su.uc ~= nil then",
    "\t\t\tuc = FOURTH.ab_caster_su.uc",
    "\t\tend",
    "\t\tif FOURTH.ab_ally_su ~= nil and FOURTH.ab_ally_su.unit ~= nil then",
    "\t\t\ttarget = FOURTH.ab_ally_su.unit",
    "\t\tend",
    "\tend")
ann = sub(ann, UC_ANN_OLD, UC_NEW_ANN, "ann fresh-handle branch")

# ===========================================================================
# 4. THE PRE-CAST ALLY RE-CHECK (both files) - inserted after the bs/edr pair.
# ===========================================================================
RC_LIVE_OLD = L(
    "\tif FOURTH.edr_ally ~= nil and not FOURTH.edr_ally_valid(unit, FOURTH.edr_ally) then",
    "\t\tlog(\"  eat_da_runts SKIPPED: the chosen ally drifted out of range or healed above 75%\"",
    "\t\t\t.. \" before the cast - cast not spent\")",
    "\t\tFOURTH.edr_ally = nil",
    "\t\tif RELEASE_CONTROL_AFTER and took_control then",
    "\t\t\tlocal ok_release, err_release = pcall(function() uc:release_control() end)",
    "\t\t\tlog(\"  release_control         : ok=\" .. tostring(ok_release)",
    "\t\t\t\t.. (ok_release and \"\" or (\"  ERROR: \" .. tostring(err_release))))",
    "\t\tend",
    "\t\treturn \"held\"",
    "\tend")
RC_LIVE_NEW = RC_LIVE_OLD + NL + L(
    "",
    "\t-- CLASS B ALLY-TARGETED RE-CHECK (harness 98): the ally trigger chose a",
    "\t-- friendly unit and left it in FOURTH.ab_ally (the cast target is the same",
    "\t-- unit, in FOURTH.cast_target); RE-READ the condition NOW, immediately",
    "\t-- before the cast - the ally must still be ALIVE and still WITHIN the",
    "\t-- ability's 70% bound, which is RE-READ here via the engine's",
    "\t-- `unit:unit_distance(ally)` (EDGE-TO-EDGE metres, battle_unit.lua:160) and",
    "\t-- whose REAL value is logged. If it lapsed the cast is wasted, so SKIP it",
    "\t-- rather than spend it. The chosen ally is the CAST TARGET - NEVER the owner.",
    "\tif FOURTH.ab_ally ~= nil then",
    "\t\tlocal ab_marker_now = FOURTH.ab_marker or \"ally\"",
    "\t\tlocal ab_bound_now = FOURTH.ab_range_m",
    "\t\tlocal ally = FOURTH.ab_ally",
    "\t\tlocal ok_alive, alive = pcall(function() return ally:number_of_men_alive() end)",
    "\t\tlocal alive_now = (ok_alive and type(alive) == \"number\" and alive > 0)",
    "\t\tlocal gap_now = FOURTH.ab_ally_gap(unit, ally)",
    "\t\tlocal in_bound_now = FOURTH.ab_gap_ok(gap_now)",
    "\t\tlocal hp_ok_now = true",
    "\t\tif FOURTH.ab_family == \"heal\" then",
    "\t\t\tlocal hp = FOURTH.context_value(ally, \"HealthPercent\")",
    "\t\t\thp_ok_now = (type(hp) ~= \"number\") or (hp <= 75)",
    "\t\tend",
    "\t\tif not alive_now or not in_bound_now or not hp_ok_now then",
    "\t\t\tlog(\"  \" .. ab_marker_now .. \" SKIPPED: the chosen ally lapsed before the cast\"",
    "\t\t\t\t.. \" (alive=\" .. tostring(alive_now) .. \" healthy=\" .. tostring(hp_ok_now)",
    "\t\t\t\t.. ((gap_now ~= nil) and (\" distance=\" .. string.format(\"%.1f\", gap_now) .. \"m\") or \" distance=?\")",
    "\t\t\t\t.. \" bound=\" .. tostring(ab_bound_now) .. \"m) - cast not spent\")",
    "\t\t\tFOURTH.ab_ally = nil",
    "\t\t\tif RELEASE_CONTROL_AFTER and took_control then",
    "\t\t\t\tlocal ok_release, err_release = pcall(function() uc:release_control() end)",
    "\t\t\t\tlog(\"  release_control         : ok=\" .. tostring(ok_release)",
    "\t\t\t\t\t.. (ok_release and \"\" or (\"  ERROR: \" .. tostring(err_release))))",
    "\t\t\tend",
    "\t\t\treturn \"held\"",
    "\t\tend",
    "\t\tlog(\"  \" .. ab_marker_now .. \" pre-cast re-check: the chosen ally is still valid (\"",
    "\t\t\t.. tostring(FOURTH.ab_family) .. \", distance=\"",
    "\t\t\t.. ((gap_now ~= nil) and string.format(\"%.1f\", gap_now) or \"?\")",
    "\t\t\t.. \"m bound=\" .. tostring(ab_bound_now) .. \"m) - firing\")",
    "\tend")
live = sub(live, RC_LIVE_OLD, RC_LIVE_NEW, "live ally re-check")

RC_ANN_OLD = L(
    "\tif FOURTH.edr_ally ~= nil and not FOURTH.edr_ally_valid(unit, FOURTH.edr_ally) then",
    "\t\tFOURTH.edr_ally = nil",
    "\t\treturn \"held\"",
    "\tend")
RC_ANN_NEW = RC_ANN_OLD + NL + L(
    "",
    "\t-- CLASS B ALLY-TARGETED RE-CHECK (harness 98): re-read the chosen ally's",
    "\t-- condition immediately before the cast - it must still be ALIVE and still",
    "\t-- WITHIN the ability's 70% bound (re-read here via the engine's",
    "\t-- `unit:unit_distance(ally)`, EDGE-TO-EDGE metres, battle_unit.lua:160), or",
    "\t-- the cast is SKIPPED. The chosen ally is the CAST TARGET - never the owner.",
    "\tif FOURTH.ab_ally ~= nil then",
    "\t\tlocal ab_bound_now = FOURTH.ab_range_m",
    "\t\tlocal ally = FOURTH.ab_ally",
    "\t\tlocal ok_alive, alive = pcall(function() return ally:number_of_men_alive() end)",
    "\t\tlocal alive_now = (ok_alive and type(alive) == \"number\" and alive > 0)",
    "\t\tlocal gap_now = FOURTH.ab_ally_gap(unit, ally)",
    "\t\tlocal in_bound_now = FOURTH.ab_gap_ok(gap_now)",
    "\t\tlocal hp_ok_now = true",
    "\t\tif FOURTH.ab_family == \"heal\" then",
    "\t\t\tlocal hp = FOURTH.context_value(ally, \"HealthPercent\")",
    "\t\t\thp_ok_now = (type(hp) ~= \"number\") or (hp <= 75)",
    "\t\tend",
    "\t\tif not alive_now or not in_bound_now or not hp_ok_now then",
    "\t\t\tFOURTH.ab_ally = nil",
    "\t\t\tif RELEASE_CONTROL_AFTER and took_control then",
    "\t\t\t\tpcall(function() uc:release_control() end)",
    "\t\t\tend",
    "\t\t\treturn \"held\"",
    "\t\tend",
    "\tend")
ann = sub(ann, RC_ANN_OLD, RC_ANN_NEW, "ann ally re-check")

# ===========================================================================
# 5. THE STAY-HERE CAST-TARGET FIX + per-ability bound (both files).
# ===========================================================================
WAIR_OLD = L(
    "function FOURTH.wa_ally_in_range(unit, ally)",
    "\tlocal gap = FOURTH.wa_ally_gap(unit, ally)",
    "\treturn (gap == nil) or (gap <= FOURTH.WAVERING_RANGE_M)",
    "end")
WAIR_NEW = L(
    "function FOURTH.wa_ally_in_range(unit, ally)",
    "\tlocal gap = FOURTH.wa_ally_gap(unit, ally)",
    "\tif gap == nil then return true end",
    "\t-- CLASS B (harness 98): the per-ability 70% ALLY bound when the poll set one",
    "\t-- (Stay Here, I'll Get Help! carries ally_range_real = 60 -> 42 m); otherwise",
    "\t-- the shared conservative wavering constant.",
    "\tlocal bound = FOURTH.ab_range_m or FOURTH.WAVERING_RANGE_M",
    "\treturn gap <= bound",
    "end")
ann = sub(ann, WAIR_OLD, WAIR_NEW, "ann wa_ally_in_range")
live = sub(live, WAIR_OLD, WAIR_NEW, "live wa_ally_in_range")

WAEV_LIVE_OLD = L(
    "function FOURTH.evaluate_wavering_ally_range(unit, routing)",
    "\tlocal reason = nil",
    "\tif not routing then",
    "\t\tlocal self_id = tostring(unit:unique_ui_id())",
    "\t\tlocal best_ally = nil",
    "\t\tlocal best_gap = nil",
    "\t\tfor i = 1, #tracked_units do",
    "\t\t\tlocal other = tracked_units[i] and tracked_units[i].unit",
    "\t\t\tif other ~= nil and other ~= unit and other:number_of_men_alive() > 0 then",
    "\t\t\t\tif tostring(other:unique_ui_id()) ~= self_id",
    "\t\t\t\t\tand not unit_is_routing(other)",
    "\t\t\t\t\tand FOURTH.wavering(other) == true then",
    "\t\t\t\t\tlocal gap = FOURTH.wa_ally_gap(unit, other)",
    "\t\t\t\t\tif (gap == nil) or (gap <= FOURTH.WAVERING_RANGE_M) then",
    "\t\t\t\t\t\tif best_ally == nil then",
    "\t\t\t\t\t\t\tbest_ally, best_gap = other, gap",
    "\t\t\t\t\t\telseif gap ~= nil and (best_gap == nil or gap < best_gap) then",
    "\t\t\t\t\t\t\tbest_ally, best_gap = other, gap",
    "\t\t\t\t\t\tend",
    "\t\t\t\t\tend",
    "\t\t\t\tend",
    "\t\t\tend",
    "\t\tend",
    "\t\tif best_ally ~= nil then",
    "\t\t\tif best_gap ~= nil then",
    "\t\t\t\tlog(\"  wavering_ally_range ally: ui \" .. tostring(best_ally:unique_ui_id())",
    "\t\t\t\t\t.. \" at \" .. string.format(\"%.1f\", best_gap) .. \"m is the CLOSEST\"",
    "\t\t\t\t\t.. \" wavering ally within \" .. tostring(FOURTH.WAVERING_RANGE_M) .. \"m\")",
    "\t\t\tend",
    "\t\t\tFOURTH.wa_ally = best_ally",
    "\t\t\treason = \"wavering ally in range (self-cast)\"",
    "\t\tend",
    "\tend",
    "\treturn reason",
    "end")
WAEV_LIVE_NEW = L(
    "function FOURTH.evaluate_wavering_ally_range(unit, routing)",
    "\tlocal reason = nil",
    "\tif not routing then",
    "\t\t-- CLASS B (harness 98): the per-ability 70% ALLY bound when the poll set",
    "\t\t-- one (ally_range_real = 60 -> 42 m); otherwise the shared constant.",
    "\t\tlocal bound = FOURTH.ab_range_m or FOURTH.WAVERING_RANGE_M",
    "\t\tlocal self_id = tostring(unit:unique_ui_id())",
    "\t\tlocal best_ally = nil",
    "\t\tlocal best_gap = nil",
    "\t\tfor i = 1, #tracked_units do",
    "\t\t\tlocal other = tracked_units[i] and tracked_units[i].unit",
    "\t\t\tif other ~= nil and other ~= unit and other:number_of_men_alive() > 0 then",
    "\t\t\t\tif tostring(other:unique_ui_id()) ~= self_id",
    "\t\t\t\t\tand not unit_is_routing(other)",
    "\t\t\t\t\tand FOURTH.wavering(other) == true then",
    "\t\t\t\t\tlocal gap = FOURTH.wa_ally_gap(unit, other)",
    "\t\t\t\t\tif (gap == nil) or (gap <= bound) then",
    "\t\t\t\t\t\tif best_ally == nil then",
    "\t\t\t\t\t\t\tbest_ally, best_gap = other, gap",
    "\t\t\t\t\t\telseif gap ~= nil and (best_gap == nil or gap < best_gap) then",
    "\t\t\t\t\t\t\tbest_ally, best_gap = other, gap",
    "\t\t\t\t\t\tend",
    "\t\t\t\t\tend",
    "\t\t\t\tend",
    "\t\t\tend",
    "\t\tend",
    "\t\tif best_ally ~= nil then",
    "\t\t\tif best_gap ~= nil then",
    "\t\t\t\tlog(\"  wavering_ally_range ally: ui \" .. tostring(best_ally:unique_ui_id())",
    "\t\t\t\t\t.. \" at \" .. string.format(\"%.1f\", best_gap) .. \"m is the CLOSEST\"",
    "\t\t\t\t\t.. \" wavering ally within \" .. tostring(bound) .. \"m\")",
    "\t\t\tend",
    "\t\t\tFOURTH.wa_ally = best_ally",
    "\t\t\t-- CLASS B (harness 98): the cast is now issued ON THE CHOSEN ALLY, not",
    "\t\t\t-- on the owner - the ally rides FOURTH.cast_target and the FRESH",
    "\t\t\t-- caster/ally script_units (the fresh-handle discipline).",
    "\t\t\tFOURTH.cast_target = best_ally",
    "\t\t\tFOURTH.ab_ally = best_ally",
    "\t\t\tFOURTH.ab_caster_su = FOURTH.ab_fresh_friend_su(unit)",
    "\t\t\tFOURTH.ab_ally_su = FOURTH.ab_fresh_friend_su(best_ally)",
    "\t\t\tFOURTH.ab_family = \"buff\"",
    "\t\t\treason = \"wavering ally in range, cast on ally\"",
    "\t\tend",
    "\tend",
    "\treturn reason",
    "end")
live = sub(live, WAEV_LIVE_OLD, WAEV_LIVE_NEW, "live stay-here evaluator")

WAEV_ANN_OLD = L(
    "function FOURTH.evaluate_wavering_ally_range(unit, routing)",
    "\tif not routing then",
    "\t\tlocal self_id = tostring(unit:unique_ui_id())",
    "\t\tlocal best_ally = nil",
    "\t\tlocal best_gap = nil",
    "\t\tfor i = 1, #tracked_units do",
    "\t\t\tlocal other = tracked_units[i] and tracked_units[i].unit",
    "\t\t\tif other ~= nil and other ~= unit and other:number_of_men_alive() > 0 then",
    "\t\t\t\tif tostring(other:unique_ui_id()) ~= self_id",
    "\t\t\t\t\tand not unit_is_routing(other)",
    "\t\t\t\t\tand FOURTH.wavering(other) == true then",
    "\t\t\t\t\tlocal gap = FOURTH.wa_ally_gap(unit, other)",
    "\t\t\t\t\tif (gap == nil) or (gap <= FOURTH.WAVERING_RANGE_M) then",
    "\t\t\t\t\t\tif best_ally == nil then",
    "\t\t\t\t\t\t\tbest_ally, best_gap = other, gap",
    "\t\t\t\t\t\telseif gap ~= nil and (best_gap == nil or gap < best_gap) then",
    "\t\t\t\t\t\t\tbest_ally, best_gap = other, gap",
    "\t\t\t\t\t\tend",
    "\t\t\t\t\tend",
    "\t\t\t\tend",
    "\t\t\tend",
    "\t\tend",
    "\t\tif best_ally ~= nil then",
    "\t\t\tFOURTH.wa_ally = best_ally",
    "\t\t\treturn true",
    "\t\tend",
    "\tend",
    "\treturn false",
    "end")
WAEV_ANN_NEW = L(
    "function FOURTH.evaluate_wavering_ally_range(unit, routing)",
    "\tif not routing then",
    "\t\tlocal bound = FOURTH.ab_range_m or FOURTH.WAVERING_RANGE_M",
    "\t\tlocal self_id = tostring(unit:unique_ui_id())",
    "\t\tlocal best_ally = nil",
    "\t\tlocal best_gap = nil",
    "\t\tfor i = 1, #tracked_units do",
    "\t\t\tlocal other = tracked_units[i] and tracked_units[i].unit",
    "\t\t\tif other ~= nil and other ~= unit and other:number_of_men_alive() > 0 then",
    "\t\t\t\tif tostring(other:unique_ui_id()) ~= self_id",
    "\t\t\t\t\tand not unit_is_routing(other)",
    "\t\t\t\t\tand FOURTH.wavering(other) == true then",
    "\t\t\t\t\tlocal gap = FOURTH.wa_ally_gap(unit, other)",
    "\t\t\t\t\tif (gap == nil) or (gap <= bound) then",
    "\t\t\t\t\t\tif best_ally == nil then",
    "\t\t\t\t\t\t\tbest_ally, best_gap = other, gap",
    "\t\t\t\t\t\telseif gap ~= nil and (best_gap == nil or gap < best_gap) then",
    "\t\t\t\t\t\t\tbest_ally, best_gap = other, gap",
    "\t\t\t\t\t\tend",
    "\t\t\t\t\tend",
    "\t\t\t\tend",
    "\t\t\tend",
    "\t\tend",
    "\t\tif best_ally ~= nil then",
    "\t\t\tFOURTH.wa_ally = best_ally",
    "\t\t\tFOURTH.cast_target = best_ally",
    "\t\t\tFOURTH.ab_ally = best_ally",
    "\t\t\tFOURTH.ab_caster_su = FOURTH.ab_fresh_friend_su(unit)",
    "\t\t\tFOURTH.ab_ally_su = FOURTH.ab_fresh_friend_su(best_ally)",
    "\t\t\tFOURTH.ab_family = \"buff\"",
    "\t\t\treturn true",
    "\t\tend",
    "\tend",
    "\treturn false",
    "end")
ann = sub(ann, WAEV_ANN_OLD, WAEV_ANN_NEW, "ann stay-here evaluator")

# ===========================================================================
# 6. THE POLL SLOTS (both files).
# ===========================================================================
POLL_CLR_OLD = "\t\t\t\t\tFOURTH.eg_ground = nil"
POLL_CLR_NEW = L(
    "\t\t\t\t\tFOURTH.eg_ground = nil",
    "\t\t\t\t\tFOURTH.ab_ally = nil",
    "\t\t\t\t\tFOURTH.ab_caster_su = nil",
    "\t\t\t\t\tFOURTH.ab_ally_su = nil",
    "\t\t\t\t\tFOURTH.ab_family = nil")
live = sub(live, POLL_CLR_OLD, POLL_CLR_NEW, "live poll clear")
ann  = sub(ann,  POLL_CLR_OLD, POLL_CLR_NEW, "ann poll clear")

POLL_SET_OLD = "\t\t\t\t\tFOURTH.eg_marker = ability.marker"
POLL_SET_NEW = L(
    "\t\t\t\t\tFOURTH.eg_marker = ability.marker",
    "\t\t\t\t\t-- CLASS B (harness 98): the CURRENT ability's own 70% ALLY bound and",
    "\t\t\t\t\t-- its marker, so the shared ally picker tests and logs against THIS",
    "\t\t\t\t\tFOURTH.ab_range_m = ability.range_m",
    "\t\t\t\t\tFOURTH.ab_marker = ability.marker")
live = sub(live, POLL_SET_OLD, POLL_SET_NEW, "live poll set")
ann  = sub(ann,  POLL_SET_OLD, POLL_SET_NEW, "ann poll set")

# ===========================================================================
# 7. THE EVALUATORS MAP + TRIGGER_TIP + THE LOAD LOOP (both files).
# ===========================================================================
MAP_OLD = L(
    "\tenemy_ground_area = FOURTH.evaluate_enemy_ground_area,",
    "}")
MAP_NEW = L(
    "\tenemy_ground_area = FOURTH.evaluate_enemy_ground_area,",
    "\t-- CLASS B (harness 98): the four ally-targeted families.",
    "\tally_heal = FOURTH.evaluate_ally_heal,",
    "\tally_heal_melee = FOURTH.evaluate_ally_heal_melee,",
    "\tally_wavering = FOURTH.evaluate_ally_wavering,",
    "\tally_melee_buff = FOURTH.evaluate_ally_melee_buff,",
    "}")
live = sub(live, MAP_OLD, MAP_NEW, "live evaluators map")
ann  = sub(ann,  MAP_OLD, MAP_NEW, "ann evaluators map")

TIP_OLD = L(
    "\tenemy_ground_area = \"When armed, fires when an enemy in range is in melee or under missile fire and the area hex is placed on its ground\",",
    "}")
TIP_NEW = L(
    "\tenemy_ground_area = \"When armed, fires when an enemy in range is in melee or under missile fire and the area hex is placed on its ground\",",
    "\tally_heal = \"When armed, fires on the lowest-health ally in range when it is at or below 75% health\",",
    "\tally_heal_melee = \"When armed, fires when this unit is in melee, on the lowest-health ally in range at or below 75% health\",",
    "\tally_wavering = \"When armed, fires on a wavering ally in range\",",
    "\tally_melee_buff = \"When armed, fires when this unit is in melee, on an ally in range\",",
    "}")
live = sub(live, TIP_OLD, TIP_NEW, "live tips")
ann  = sub(ann,  TIP_OLD, TIP_NEW, "ann tips")

LOAD_OLD = L(
    "\tif ability.range_real ~= nil then",
    "\t\tability.range_m = FOURTH.ENEMY_CAST[ability.range_real]",
    "\tend",
    "end")
LOAD_NEW = L(
    "\tif ability.range_real ~= nil then",
    "\t\tability.range_m = FOURTH.ENEMY_CAST[ability.range_real]",
    "\tend",
    "\t-- CLASS B (harness 98): an ally-targeted entry's REAL target_intercept_range",
    "\t-- (ally_range_real) maps to its own named 70% ALLY bound (FOURTH.ALLY_CAST).",
    "\tif ability.ally_range_real ~= nil then",
    "\t\tability.range_m = FOURTH.ALLY_CAST[ability.ally_range_real]",
    "\tend",
    "end")
live = sub(live, LOAD_OLD, LOAD_NEW, "live load loop")
ann  = sub(ann,  LOAD_OLD, LOAD_NEW, "ann load loop")

# ===========================================================================
# 8. THE ENTRIES: move each trigger + add its own ally_range_real field.
# ===========================================================================
def edit_entries(text, label):
    for m, (trig, real, num) in sorted(IMPLEMENTED.items(), key=lambda kv: kv[1][2]):
        pat = re.compile(
            r'(\t\{ marker = "' + re.escape(m) + r'", name = "(?:[^"\\]|\\.)*", trigger = )'
            r'"[^"]+"(,\n\t\tbadge = "zz_auto_badge_[^"]*",\n\t\tkeys = \{[^}]*\},\n)'
            r'(\t\tox = 0, oy = 0 \},)')
        new = r'\1"' + trig + r'"\2\t\tally_range_real = ' + str(real) + r',\n\3'
        text, n = pat.subn(new, text)
        assert n == 1, "%s entry %s: %d matches (want 1)" % (label, m, n)
    # the existing-trigger entry only gains its own ally_range_real field
    for m, (trig, real, num) in EXISTING.items():
        pat = re.compile(
            r'(\t\{ marker = "' + re.escape(m) + r'", name = "(?:[^"\\]|\\.)*", trigger = )'
            r'"[^"]+"(,\n\t\tbadge = "zz_auto_badge_[^"]*",\n\t\tkeys = \{[^}]*\},\n)'
            r'(\t\tox = 0, oy = 0 \},)')
        new = r'\1"' + trig + r'"\2\t\tally_range_real = ' + str(real) + r',\n\3'
        text, n = pat.subn(new, text)
        assert n == 1, "%s existing entry %s: %d matches (want 1)" % (label, m, n)
    return text
live = edit_entries(live, "live")
ann  = edit_entries(ann,  "ann")

# ===========================================================================
# 9. SANITY (both files).
# ===========================================================================
n_new = len(IMPLEMENTED); n_ex = len(EXISTING)
for s, nm in ((live, "live"), (ann, "ann")):
    assert s.count(T + "{ marker = ") == 579, nm + ": table not 579 entries"
    assert s.count('trigger = "melee_unwavering"') == 383 - 10, nm + ": melee_unwavering count moved wrong"
    assert s.count('trigger = "charge_or_melee"') == 29 - 3, nm + ": charge_or_melee count moved wrong"
    assert s.count('trigger = "ushoran_health"') == 41 - 3, nm + ": ushoran_health count moved wrong"
    assert s.count('trigger = "melee_health75"') == 2 - 1, nm + ": melee_health75 count moved wrong"
    assert s.count('trigger = "wavering_ally_range"') == 1, nm + ": stay-here trigger moved"
    assert s.count('trigger = "ally_heal"') == 3, nm + ": ally_heal count wrong"
    assert s.count('trigger = "ally_heal_melee"') == 1, nm + ": ally_heal_melee count wrong"
    assert s.count('trigger = "ally_wavering"') == 2, nm + ": ally_wavering count wrong"
    assert s.count('trigger = "ally_melee_buff"') == 11, nm + ": ally_melee_buff count wrong"
    assert s.count(T + T + "ally_range_real = ") == n_new + n_ex, nm + ": ally_range_real fields wrong"
    assert "FOURTH.ALLY_CAST = {" in s, nm + ": ally bound map missing"
    assert s.count("FOURTH.ALLY_CAST_R") == 10, nm + ": ally constant refs wrong"
    assert "ability.range_m = FOURTH.ALLY_CAST[ability.ally_range_real]" in s, nm + ": load loop missing"
    assert "function FOURTH.ab_pick_ally(unit, routing, family)" in s, nm + ": ally picker missing"
    assert "function FOURTH.ab_fresh_friend_su(unit)" in s, nm + ": fresh-friend helper missing"
    assert "function FOURTH.ab_ally_valid(unit, ally)" in s, nm + ": ally validity missing"
    assert "function FOURTH.evaluate_ally_heal(unit, routing)" in s, nm + ": ally_heal eval missing"
    assert "function FOURTH.evaluate_ally_heal_melee(unit, routing)" in s, nm + ": ally_heal_melee eval missing"
    assert "function FOURTH.evaluate_ally_wavering(unit, routing)" in s, nm + ": ally_wavering eval missing"
    assert "function FOURTH.evaluate_ally_melee_buff(unit, routing)" in s, nm + ": ally_melee_buff eval missing"
    assert "ally_heal = FOURTH.evaluate_ally_heal," in s, nm + ": ally_heal not wired"
    assert "ally_melee_buff = FOURTH.evaluate_ally_melee_buff," in s, nm + ": ally_melee_buff not wired"
    assert "FOURTH.ab_range_m = ability.range_m" in s and "FOURTH.ab_marker = ability.marker" in s, nm + ": poll slots missing"
    assert "uc = FOURTH.ab_caster_su.uc" in s and "target = FOURTH.ab_ally_su.unit" in s, nm + ": fresh-handle branch missing"
    assert "FOURTH.ab_ally = nil" in s, nm + ": no poll clear for ab_ally"
    assert "SKIPPED: the chosen ally lapsed before the cast" in s or nm == "ann", nm + ": lapse skip missing"
    assert s.count("FOURTH.cast_target = unit") == 2, nm + ": Glorious Death cast-target write moved"
    assert s.count("FOURTH.wa_ally = nil") == 3, nm + ": wa_ally=nil count moved"
    assert "FOURTH.WAVERING_RANGE_M = 24" in s, nm + ": the shared wavering constant moved"
    assert "FOURTH.RANGE_FRACTION = 0.70" in s, nm + ": 70% rule missing"
    assert s.count(chr(13)) == 0, nm + ": CRLF leaked"
if "log(" in ann:
    raise SystemExit("annotated copy gained a log()")
if "string.find" in ann:
    raise SystemExit("annotated copy gained a string.find()")

write(LIVE, live); write(ANN, ann)
print("wrote", LIVE, len(live))
print("wrote", ANN, len(ann))
print("OK: %d Class-B entries implemented on the ally picker (+%d existing wired); "
      "%d army-bar skipped; %d need a ruling." % (n_new, n_ex, len(ARMY_BAR), len(NEEDS_RULING)))
