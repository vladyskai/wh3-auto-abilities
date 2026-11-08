# -*- coding: utf-8 -*-
"""ROUND h96 IMPLEMENTATION: fix the remaining move order on Accusation by
correcting the RANGE SOURCE, and LOG the REAL computed distance.

ROOT CAUSE (found in the live battle log): the h95 70% rule still derived
Accusation's trigger range from unit_spec_abil.tsv `target_intercept_range`
(75 -> 52 m). That column is the reach at which a unit INTERRUPTS what it is
doing to WALK AND INTERCEPT a target - a PURSUIT range, not a cast range - so
basing a trigger on it invites the very movement the rule was meant to remove.
Accusation's real `effect_range` is 0.0000 (no aura) and its ai_usage is
hex_melee: it is a MELEE-CONTACT hex.

THE CORRECTED RULE (documented beside the constants):
  * an ability's trigger range comes from its own `effect_range`;
  * `target_intercept_range` is NEVER used (pursuit range -> movement);
  * an ability whose effect_range is 0 has no aura and no cast-range column, so
    its trigger is the documented small melee-contact bound
    FOURTH.CONTACT_BOUND_M = 10 m (NOT a cast range); Accusation additionally
    requires the chosen enemy to be in melee contact WITH THE CASTER (the
    distance primitive <= the bound).
Applied to Accusation (enemy hex - the reported symptom), Blood Sacrifice and
Eat da Runts (the two other effect_range-0 targeted abilities - both re-derived
from the intercept-derived 70 m to the contact bound).

LOGGING: the static "within Nm" label is replaced by the ACTUAL computed
distance to ONE decimal, at SELECTION and again at the PRE-CAST RE-CHECK. The
primitive is `unit:unit_distance(other)` - ENGINE-PROVIDED, the STRAIGHT-LINE
distance in METRES between the two units - documented in the code beside it.

Applies the SAME logical change to the LIVE mod and the ANNOTATED reading copy
(each in its own idiom; the annotated copy returns booleans and is log-free).
Snapshots pre96_live.lua / pre96_ann.lua first as the RED CONTROL target.
"""
import io
import os

ROOT = "C:/Users/vlady/Desktop/WH3_mod/mod_source"
LIVE = ROOT + "/script/battle/mod/zz_test_deadly_onslaught.lua"
ANN = "C:/Users/vlady/Desktop/WH3_mod/docs/WH3_auto_ability_annotated.lua"
HERE = os.path.dirname(os.path.abspath(__file__))


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
write(HERE + "/pre96_live.lua", live)
write(HERE + "/pre96_ann.lua", ann)
print("wrote pre96_live.lua", len(live), "bytes")
print("wrote pre96_ann.lua", len(ann), "bytes")

# ===========================================================================
# THE CORRECTED RANGE SOURCE block (appended to the STANDING RANGE RULE) and
# the CONTACT_BOUND_M constant.
# ===========================================================================
CORRECTED = (
"--\n"
"-- THE CORRECTED RANGE SOURCE (harness 96 - this round). The REAL range of an\n"
"-- ability comes from its own `effect_range` (the aura / effect radius) - NEVER\n"
"-- from `target_intercept_range`, which is the reach at which the unit\n"
"-- INTERRUPTS what it is doing to WALK AND INTERCEPT a target: a PURSUIT range,\n"
"-- not a cast range. Basing a trigger on it invites exactly the walking this\n"
"-- project fights (the reported Accusation move order survived the 70% rule\n"
"-- because 52 m was still 70% of a PURSUIT reach). An ability whose\n"
"-- `effect_range` is 0 has NO aura and NO cast-range column, so its trigger is\n"
"-- a MELEE-CONTACT gate instead of a distance: the target must lie within\n"
"-- FOURTH.CONTACT_BOUND_M (a documented small contact bound, NOT a cast range)\n"
"-- of the caster.\n"
"-- ============================================================================\n"
"FOURTH.RANGE_FRACTION = 0.70\n"
"-- THE MELEE-CONTACT BOUND (harness 96): the documented small bound (10 m) used\n"
"-- as the trigger for an ability whose effect_range is 0 - it has no aura radius\n"
"-- and no cast-range column, and target_intercept_range is a PURSUIT range that\n"
"-- causes movement, so it is NEVER used. A target beyond this bound is a\n"
"-- movement-prone offer and is NOT made. Applied to Accusation (enemy hex),\n"
"-- Blood Sacrifice and Eat da Runts (the two single-target heals).\n"
"FOURTH.CONTACT_BOUND_M = 10")

# ---------------------------------------------------------------------------
# LIVE
# ---------------------------------------------------------------------------
L_RULE_OLD = (
"-- ============================================================================\n"
"-- THE STANDING RANGE RULE (this round, set by the user). EVERY trigger-range\n"
"-- constant in this file MUST be AT MOST 70% of the ability's REAL game-data\n"
"-- range, rounded DOWN to a whole metre. The user's words: \"for abilities that\n"
"-- include a range, we should always specify 70% of the actual range to avoid\n"
"-- such things\" - and, ruling it absolute, \"...No exceptions.\" The symptom is\n"
"-- the caster WALKING toward a target that sat inside the ability's own reach\n"
"-- but outside a comfortable cast range. FOURTH.RANGE_FRACTION is that 70%;\n"
"-- every range constant below names its real range, its source, and the\n"
"-- floor(real * FOURTH.RANGE_FRACTION) derivation in the comment beside it.\n"
"-- ============================================================================\n"
"FOURTH.RANGE_FRACTION = 0.70")
live = sub(live, L_RULE_OLD, CORRECTED, "L-rule")

# --- heals intro block ---
L_HEALS_OLD = (
"--   THE TRIGGER RANGE is a DELIBERATELY CONSERVATIVE named constant. The game\n"
"--   data (unit_spec_abil.tsv) gives these two SINGLE-ally heals NO aura radius\n"
"--   (effect_range = 0.0000; num_effected_friendly_units = 1) and a\n"
"--   target_intercept_range of 100.0000 m, so - following the file's field-proven\n"
"--   conservative pattern (25 m against larger auras) - the trigger radius is a\n"
"--   25 m constant. ONE place to tune.")
L_HEALS_NEW = (
"--   THE TRIGGER RANGE (harness 96 - CORRECTED RANGE SOURCE): the game data\n"
"--   (unit_spec_abil.tsv) gives these two SINGLE-ally heals NO aura radius\n"
"--   (effect_range = 0.0000; num_effected_friendly_units = 1) and no cast-range\n"
"--   column; their target_intercept_range (100.0000 m) is a PURSUIT range and is\n"
"--   NOT used. The trigger radius is therefore the documented melee-contact\n"
"--   bound FOURTH.CONTACT_BOUND_M (10 m). ONE place to tune.")
live = sub(live, L_HEALS_OLD, L_HEALS_NEW, "L-heals-intro")

# --- BLOOD SACRIFICE constant ---
live = sub(live,
    "-- BLOOD SACRIFICE'S TRIGGER RANGE (this round) - THE STANDING 70% RULE. The\n"
    "-- ability has NO aura (effect_range = 0.0000, num_effected_friendly_units = 1),\n"
    "-- so its REAL game-data range is its target_intercept_range = 100.0000 m\n"
    "-- (unit_spec_abil.tsv, wh3_dlc26_lord_abilities_blood_sacrifice).\n"
    "-- 100 * 0.70 = 70.0 -> 70 m (FLOORED, FOURTH.RANGE_FRACTION).\n"
    "FOURTH.BLOOD_SACRIFICE_RANGE_M = 70",
    "-- BLOOD SACRIFICE'S TRIGGER RANGE (harness 96) - THE CORRECTED RANGE SOURCE.\n"
    "-- The ability has NO aura (effect_range = 0.0000, num_effected_friendly_units\n"
    "-- = 1) and no cast-range column; its target_intercept_range (100.0000 m) is a\n"
    "-- PURSUIT range and is NOT used. The trigger is the documented melee-contact\n"
    "-- bound: the chosen ally must lie within FOURTH.CONTACT_BOUND_M of the caster.\n"
    "FOURTH.BLOOD_SACRIFICE_RANGE_M = FOURTH.CONTACT_BOUND_M",
    "L-bs")

# --- EAT DA RUNTS constant ---
live = sub(live,
    "-- EAT DA RUNTS!'S TRIGGER RANGE (this round) - THE STANDING 70% RULE. The\n"
    "-- ability has NO aura (effect_range = 0.0000, num_effected_friendly_units = 1),\n"
    "-- so its REAL game-data range is its target_intercept_range = 100.0000 m\n"
    "-- (unit_spec_abil.tsv, wh3_dlc26_unit_abilities_eat_da_runts).\n"
    "-- 100 * 0.70 = 70.0 -> 70 m (FLOORED, FOURTH.RANGE_FRACTION).\n"
    "FOURTH.EAT_DA_RUNTS_RANGE_M = 70",
    "-- EAT DA RUNTS!'S TRIGGER RANGE (harness 96) - THE CORRECTED RANGE SOURCE.\n"
    "-- The ability has NO aura (effect_range = 0.0000) and no cast-range column;\n"
    "-- its target_intercept_range (100.0000 m) is a PURSUIT range and is NOT used.\n"
    "-- The trigger is the documented melee-contact bound: the chosen ally must lie\n"
    "-- within FOURTH.CONTACT_BOUND_M of the caster.\n"
    "FOURTH.EAT_DA_RUNTS_RANGE_M = FOURTH.CONTACT_BOUND_M",
    "L-edr")

# --- ACCUSATION intro prose (THE RANGE SOURCE paragraph) ---
live = sub(live,
    "--   THE RANGE SOURCE: Accusation's own target_intercept_range in\n"
    "--   unit_spec_abil.tsv = 75.0000 m - the exact reach the round-4 probe named\n"
    "--   and used. The enemy is offered only while unit:unit_in_range(enemy) is\n"
    "--   true, else while unit:unit_distance(enemy) <= FOURTH.ACCUSATION_RANGE_M,\n"
    "--   else while the caster itself is in melee. CONSERVATIVE: the value is a\n"
    "--   named constant - ONE place to tune.",
    "--   THE RANGE SOURCE (harness 96 - CORRECTED): Accusation's effect_range in\n"
    "--   unit_spec_abil.tsv is 0.0000 (NO aura) and its ai_usage is hex_melee, so\n"
    "--   it is a MELEE-CONTACT hex. Its target_intercept_range (75.0000 m) is a\n"
    "--   PURSUIT range - the reach at which the caster WALKS to intercept - and is\n"
    "--   NOT used: basing the trigger on it caused the reported move order. The\n"
    "--   enemy is offered only while unit:unit_distance(enemy) <= CONTACT_BOUND_M\n"
    "--   (the documented melee-contact bound, 10 m). No engine unit_in_range reach\n"
    "--   read and no intercept-derived constant is used.",
    "L-acc-prose")

# --- ACCUSATION constant block ---
live = sub(live,
    "-- ACCUSATION'S TRIGGER RANGE (this round) - THE STANDING 70% RULE. REAL range\n"
    "-- 75.0000 m = the ability's own target_intercept_range (unit_spec_abil.tsv,\n"
    "-- wh_main_hero_abilities_accusation; effect_range = 0.0000, so the intercept\n"
    "-- reach is the real range). 75 * 0.70 = 52.5 -> 52 m (FLOORED,\n"
    "-- FOURTH.RANGE_FRACTION). SET TO 52 AFTER THE CASTER WAS SEEN TO WALK toward\n"
    "-- an enemy that sat inside the 75 m reach but outside a comfortable cast range\n"
    "-- - the very symptom this rule exists to remove.\n"
    "FOURTH.ACCUSATION_RANGE_M = 52",
    "-- ACCUSATION'S TRIGGER GATE (harness 96) - THE CORRECTED RANGE SOURCE. The\n"
    "-- game data (unit_spec_abil.tsv, wh_main_hero_abilities_accusation) gives this\n"
    "-- ability effect_range = 0.0000 (NO aura), ai_usage = hex_melee, target_enemies\n"
    "-- = true and num_effected_enemy_units = 1: a MELEE-CONTACT hex. Its\n"
    "-- target_intercept_range is 75.0000 m, but that column is the PURSUIT reach the\n"
    "-- engine walks the caster to intercept - NOT a cast range - and the old\n"
    "-- 70%-of-intercept 52 m still produced the reported MOVE ORDER. The trigger is\n"
    "-- therefore a MELEE-CONTACT gate against the documented FOURTH.CONTACT_BOUND_M\n"
    "-- (10 m): the chosen enemy must lie within it. NO distance is derived from\n"
    "-- target_intercept_range anywhere in this file, and NO separate Accusation\n"
    "-- range constant exists - the trigger reads FOURTH.CONTACT_BOUND_M directly.",
    "L-acc-const")

# --- eg_enemy_gap comment (THE DISTANCE PRIMITIVE) ---
live = sub(live,
    "-- the gap in metres from the OWNER to a candidate enemy - the SAME\n"
    "-- battle_unit:unit_distance primitive the charge detector and every ally\n"
    "-- trigger already use. nil when the read cannot be taken.",
    "-- THE DISTANCE PRIMITIVE (harness 96): the gap in metres from the OWNER to a\n"
    "-- candidate enemy is `unit:unit_distance(enemy)` - an ENGINE-PROVIDED read that\n"
    "-- returns the STRAIGHT-LINE distance in METRES between the two units (the same\n"
    "-- primitive the charge detector and every ally-range trigger already use). The\n"
    "-- trigger and its pre-cast re-check BOTH use it, so the log and the gate agree.\n"
    "-- nil when the read cannot be taken.",
    "L-gap-comment")

# --- eg_enemy_in_range -> eg_enemy_within_contact ---
live = sub(live,
    "-- true while the enemy is inside the ability's own reach. unit_in_range is the\n"
    "-- engine's reach read (the probe logged in_range=yes(unit_in_range)); a\n"
    "-- readable distance is the fallback; caster-in-melee is the last resort. A\n"
    "-- wholly unreadable reach is treated as OUT of range (fail-safe: never offer an\n"
    "-- enemy the ability may not cover).\n"
    "function FOURTH.eg_enemy_in_range(unit, enemy)\n"
    "\tlocal okr, inr = pcall(function() return unit:unit_in_range(enemy) end)\n"
    "\tif okr and inr == true then return true end\n"
    "\tif okr and inr == false then return false end\n"
    "\tlocal gap = FOURTH.eg_enemy_gap(unit, enemy)\n"
    "\tif gap ~= nil then return gap <= FOURTH.ACCUSATION_RANGE_M end\n"
    "\tlocal okm, m = pcall(function() return unit:is_in_melee() end)\n"
    "\treturn (okm and m == true)\n"
    "end",
    "-- true while the enemy lies within the MELEE-CONTACT BOUND of the caster\n"
    "-- (harness 96). THE DISTANCE PRIMITIVE is FOURTH.eg_enemy_gap's\n"
    "-- `unit:unit_distance(enemy)` - the ENGINE-PROVIDED straight-line distance in\n"
    "-- metres between the two units; the gate is that distance <=\n"
    "-- FOURTH.CONTACT_BOUND_M. The old engine `unit_in_range(enemy)` reach read is\n"
    "-- NOT used (it reports the ability's own reach - the same intercept/pursuit\n"
    "-- reach that walked the caster), and a wholly unreadable distance is treated as\n"
    "-- OUT of contact (fail-safe: never offer an enemy the ability may not cover at\n"
    "-- contact range).\n"
    "function FOURTH.eg_enemy_within_contact(unit, enemy)\n"
    "\tlocal gap = FOURTH.eg_enemy_gap(unit, enemy)\n"
    "\tif gap == nil then return false end\n"
    "\treturn gap <= FOURTH.CONTACT_BOUND_M\n"
    "end",
    "L-within-contact")

# --- evaluator gate ---
live = sub(live,
    "\t\t\t\t\t\t\t\tand FOURTH.eg_enemy_in_range(unit, enemy) then",
    "\t\t\t\t\t\t\t\tand FOURTH.eg_enemy_within_contact(unit, enemy) then",
    "L-eval-gate")

# --- evaluator chosen-target log: REAL distance ---
live = sub(live,
    "\t\t\t\t\tlog(\"  accusation target: '\" .. etype .. \"' is the chosen enemy (\" .. tostring(best_arm)\n"
    "\t\t\t\t\t\t.. \") within \" .. tostring(FOURTH.ACCUSATION_RANGE_M) .. \"m\")",
    "\t\t\t\t\tlog(\"  accusation target: '\" .. etype .. \"' chosen (\" .. tostring(best_arm)\n"
    "\t\t\t\t\t\t.. \") distance=\" .. ((best_gap ~= nil) and string.format(\"%.1f\", best_gap) or \"?\")\n"
    "\t\t\t\t\t\t.. \"m range=\" .. tostring(FOURTH.CONTACT_BOUND_M) .. \"m\")",
    "L-target-log")

# --- pre-cast re-check comment ---
live = sub(live,
    "\t-- ACCUSATION ENEMY RE-CHECK (this round): the enemy trigger chose an ENEMY\n"
    "\t-- unit and left it in FOURTH.eg_enemy (the cast target is the same unit,\n"
    "\t-- in FOURTH.cast_target); RE-READ the condition NOW, immediately before the\n"
    "\t-- cast - the enemy must still be ALIVE and still IN MELEE or UNDER FIRE and\n"
    "\t-- still IN RANGE. If it lapsed the cast is wasted, so SKIP it rather than\n"
    "\t-- spend it. The chosen enemy is the CAST TARGET - NEVER the owner.",
    "\t-- ACCUSATION ENEMY RE-CHECK (harness 96): the enemy trigger chose an ENEMY\n"
    "\t-- unit and left it in FOURTH.eg_enemy (the cast target is the same unit,\n"
    "\t-- in FOURTH.cast_target); RE-READ the condition NOW, immediately before the\n"
    "\t-- cast - the enemy must still be ALIVE and still IN MELEE or UNDER FIRE and\n"
    "\t-- still WITHIN the melee-contact bound, which is RE-READ here via the\n"
    "\t-- engine's unit:unit_distance (straight-line metres) and its REAL value is\n"
    "\t-- logged. If it lapsed the cast is wasted, so SKIP it rather than spend it.\n"
    "\t-- The chosen enemy is the CAST TARGET - NEVER the owner.",
    "L-recheck-comment")

# --- pre-cast re-check: distance re-read + logs ---
live = sub(live,
    "\t\tlocal in_range_now = FOURTH.eg_enemy_in_range(unit, enemy)\n"
    "\t\tif not alive_now or not (still_melee or still_shot) or not in_range_now then\n"
    "\t\t\tlog(\"  accusation SKIPPED: the chosen enemy lapsed before the cast\"\n"
    "\t\t\t\t.. \" (alive=\" .. tostring(alive_now) .. \" melee=\" .. tostring(still_melee)\n"
    "\t\t\t\t.. \" shot=\" .. tostring(still_shot) .. \" in_range=\" .. tostring(in_range_now)\n"
    "\t\t\t\t.. \") - cast not spent\")",
    "\t\t-- RE-READ the contact distance NOW - the engine's unit:unit_distance\n"
    "\t\t-- (straight-line metres) - and log its REAL value.\n"
    "\t\tlocal gap_now = FOURTH.eg_enemy_gap(unit, enemy)\n"
    "\t\tlocal in_contact_now = (gap_now ~= nil and gap_now <= FOURTH.CONTACT_BOUND_M)\n"
    "\t\tif not alive_now or not (still_melee or still_shot) or not in_contact_now then\n"
    "\t\t\tlog(\"  accusation SKIPPED: the chosen enemy lapsed before the cast\"\n"
    "\t\t\t\t.. \" (alive=\" .. tostring(alive_now) .. \" melee=\" .. tostring(still_melee)\n"
    "\t\t\t\t.. \" shot=\" .. tostring(still_shot)\n"
    "\t\t\t\t.. (gap_now ~= nil and (\" distance=\" .. string.format(\"%.1f\", gap_now) .. \"m\") or \" distance=?\")\n"
    "\t\t\t\t.. \" range=\" .. tostring(FOURTH.CONTACT_BOUND_M) .. \"m) - cast not spent\")",
    "L-recheck-skip")
live = sub(live,
    "\t\tlog(\"  accusation pre-cast re-check: target still engaged (\" .. tostring(FOURTH.eg_arm)\n"
    "\t\t\t.. \", melee=\" .. tostring(still_melee) .. \" shot=\" .. tostring(still_shot)\n"
    "\t\t\t.. \", in_range=\" .. tostring(in_range_now) .. \") - firing\")",
    "\t\tlog(\"  accusation pre-cast re-check: target still engaged (\" .. tostring(FOURTH.eg_arm)\n"
    "\t\t\t.. \", melee=\" .. tostring(still_melee) .. \" shot=\" .. tostring(still_shot)\n"
    "\t\t\t.. \", distance=\" .. string.format(\"%.1f\", gap_now) .. \"m range=\"\n"
    "\t\t\t.. tostring(FOURTH.CONTACT_BOUND_M) .. \"m) - firing\")",
    "L-recheck-fire")

# ===========================================================================
# ANN (the reading copy)
# ===========================================================================
A_RULE_OLD = (
"-- ============================================================================\n"
"-- THE STANDING RANGE RULE (this round, set by the user). EVERY trigger-range\n"
"-- constant in this file MUST be AT MOST 70% of the ability's REAL game-data\n"
"-- range, rounded DOWN to a whole metre. The user's words: \"for abilities that\n"
"-- include a range, we should always specify 70% of the actual range to avoid\n"
"-- such things\" - and, ruling it absolute, \"...No exceptions.\" The symptom is\n"
"-- the caster WALKING toward a target inside the ability's reach but outside a\n"
"-- comfortable cast range. FOURTH.RANGE_FRACTION is that 70%; every constant\n"
"-- below names its real range, its source, and the floor(real * 0.70)\n"
"-- derivation in the comment beside it.\n"
"-- ============================================================================\n"
"FOURTH.RANGE_FRACTION = 0.70")
A_CORRECTED = (
"-- THE CORRECTED RANGE SOURCE (harness 96): an ability's REAL range comes from\n"
"-- its own `effect_range` (aura / effect radius) - NEVER from\n"
"-- `target_intercept_range`, the PURSUIT reach at which the unit WALKS to\n"
"-- intercept a target (it caused the reported move order). An ability whose\n"
"-- effect_range is 0 has no aura and no cast-range column, so its trigger is a\n"
"-- MELEE-CONTACT gate against the documented small bound FOURTH.CONTACT_BOUND_M\n"
"-- (NOT a cast range).\n"
"-- ============================================================================\n"
"FOURTH.RANGE_FRACTION = 0.70\n"
"-- THE MELEE-CONTACT BOUND (harness 96): the documented small bound (10 m) used\n"
"-- as the trigger for an ability whose effect_range is 0 (no aura, no cast-range\n"
"-- column; target_intercept_range is a PURSUIT range and is NEVER used). A\n"
"-- target beyond this bound is a movement-prone offer and is NOT made. Applied\n"
"-- to Accusation, Blood Sacrifice and Eat da Runts.\n"
"FOURTH.CONTACT_BOUND_M = 10")
ann = sub(ann, A_RULE_OLD, A_CORRECTED, "A-rule")

ann = sub(ann,
    "--   THE TRIGGER RANGE is a DELIBERATELY CONSERVATIVE 25 m named constant (the\n"
    "--   game data gives these single-ally heals no aura radius, effect_range\n"
    "--   0.0000, with target_intercept_range 100.0000 m). NO new chunk-level locals.",
    "--   THE TRIGGER RANGE (harness 96 - CORRECTED RANGE SOURCE): the game data\n"
    "--   gives these single-ally heals no aura radius (effect_range 0.0000) and no\n"
    "--   cast-range column; target_intercept_range (100.0000 m) is a PURSUIT range\n"
    "--   and is NOT used. The trigger is the documented melee-contact bound\n"
    "--   FOURTH.CONTACT_BOUND_M. NO new chunk-level locals.",
    "A-heals-intro")

ann = sub(ann,
    "-- BLOOD SACRIFICE'S TRIGGER RANGE (this round) - THE STANDING 70% RULE. No\n"
    "-- aura (effect_range = 0.0000), so the REAL range is target_intercept_range =\n"
    "-- 100.0000 m (unit_spec_abil.tsv). 100 * 0.70 = 70.0 -> 70 m (FLOORED,\n"
    "-- FOURTH.RANGE_FRACTION).\n"
    "FOURTH.BLOOD_SACRIFICE_RANGE_M = 70",
    "-- BLOOD SACRIFICE'S TRIGGER RANGE (harness 96) - THE CORRECTED RANGE SOURCE.\n"
    "-- effect_range = 0.0000 (no aura) and no cast-range column; the\n"
    "-- target_intercept_range (100.0000 m) is a PURSUIT range and is NOT used. The\n"
    "-- trigger is the documented melee-contact bound: the chosen ally must lie\n"
    "-- within FOURTH.CONTACT_BOUND_M of the caster.\n"
    "FOURTH.BLOOD_SACRIFICE_RANGE_M = FOURTH.CONTACT_BOUND_M",
    "A-bs")

ann = sub(ann,
    "-- EAT DA RUNTS!'S TRIGGER RANGE (this round) - THE STANDING 70% RULE. No aura\n"
    "-- (effect_range = 0.0000), so the REAL range is target_intercept_range =\n"
    "-- 100.0000 m (unit_spec_abil.tsv). 100 * 0.70 = 70.0 -> 70 m (FLOORED,\n"
    "-- FOURTH.RANGE_FRACTION).\n"
    "FOURTH.EAT_DA_RUNTS_RANGE_M = 70",
    "-- EAT DA RUNTS!'S TRIGGER RANGE (harness 96) - THE CORRECTED RANGE SOURCE.\n"
    "-- effect_range = 0.0000 (no aura) and no cast-range column; the\n"
    "-- target_intercept_range (100.0000 m) is a PURSUIT range and is NOT used. The\n"
    "-- trigger is the documented melee-contact bound: the chosen ally must lie\n"
    "-- within FOURTH.CONTACT_BOUND_M of the caster.\n"
    "FOURTH.EAT_DA_RUNTS_RANGE_M = FOURTH.CONTACT_BOUND_M",
    "A-edr")

ann = sub(ann,
    "--   enemy script units; keep those that are valid and alive AND inside the\n"
    "--   ability's own reach; of those pick one that is IN MELEE or UNDER MISSILE",
    "--   enemy script units; keep those that are valid and alive AND within the\n"
    "--   melee-contact bound; of those pick one that is IN MELEE or UNDER MISSILE",
    "A-acc-intro-1")

ann = sub(ann,
    "--   THE RANGE SOURCE: Accusation's own target_intercept_range (unit_spec_abil\n"
    "--   .tsv = 75.0000 m), stored as the named FOURTH.ACCUSATION_RANGE_M.",
    "--   THE RANGE SOURCE (harness 96 - CORRECTED): Accusation's effect_range is\n"
    "--   0.0000 (NO aura) and its ai_usage is hex_melee - a MELEE-CONTACT hex. Its\n"
    "--   target_intercept_range (75.0000 m) is a PURSUIT range and is NOT used; the\n"
    "--   enemy must lie within FOURTH.CONTACT_BOUND_M (the documented bound, 10 m).",
    "A-acc-intro-2")

ann = sub(ann,
    "--   THE SAFETY PATTERN: the chosen enemy rides FOURTH.eg_enemy; the condition\n"
    "--   (alive + still in melee/under fire + still in range) is RE-CHECKED",
    "--   THE SAFETY PATTERN: the chosen enemy rides FOURTH.eg_enemy; the condition\n"
    "--   (alive + still in melee/under fire + still in contact) is RE-CHECKED",
    "A-acc-intro-3")

ann = sub(ann,
    "-- ACCUSATION'S TRIGGER RANGE (this round) - THE STANDING 70% RULE. REAL range\n"
    "-- 75.0000 m = target_intercept_range (unit_spec_abil.tsv; effect_range 0.0000).\n"
    "-- 75 * 0.70 = 52.5 -> 52 m (FLOORED, FOURTH.RANGE_FRACTION). 52 m after the\n"
    "-- caster was seen to WALK toward an enemy inside the 75 m reach.\n"
    "FOURTH.ACCUSATION_RANGE_M = 52",
    "-- ACCUSATION'S TRIGGER GATE (harness 96) - THE CORRECTED RANGE SOURCE. The game\n"
    "-- data gives it effect_range = 0.0000 (NO aura), ai_usage = hex_melee,\n"
    "-- target_enemies = true, num_effected_enemy_units = 1: a MELEE-CONTACT hex. Its\n"
    "-- target_intercept_range (75.0000 m) is a PURSUIT range and is NOT used. The\n"
    "-- trigger is a MELEE-CONTACT gate against the documented FOURTH.CONTACT_BOUND_M.",
    "A-acc-const")

ann = sub(ann,
    "-- the gap in metres from the OWNER to a candidate enemy.",
    "-- THE DISTANCE PRIMITIVE (harness 96): the gap in metres from the OWNER to a\n"
    "-- candidate enemy is `unit:unit_distance(enemy)` - an ENGINE-PROVIDED read that\n"
    "-- returns the STRAIGHT-LINE distance in METRES between the two units.",
    "A-gap-comment")

ann = sub(ann,
    "-- true while the enemy is inside the ability's own reach: unit_in_range first,\n"
    "-- a readable distance next, caster-in-melee last. A wholly unreadable reach is\n"
    "-- treated as OUT of range (fail-safe).\n"
    "function FOURTH.eg_enemy_in_range(unit, enemy)\n"
    "\tlocal okr, inr = pcall(function() return unit:unit_in_range(enemy) end)\n"
    "\tif okr and inr == true then return true end\n"
    "\tif okr and inr == false then return false end\n"
    "\tlocal gap = FOURTH.eg_enemy_gap(unit, enemy)\n"
    "\tif gap ~= nil then return gap <= FOURTH.ACCUSATION_RANGE_M end\n"
    "\tlocal okm, m = pcall(function() return unit:is_in_melee() end)\n"
    "\treturn (okm and m == true)\n"
    "end",
    "-- true while the enemy lies within the MELEE-CONTACT BOUND of the caster. The\n"
    "-- distance primitive is `unit:unit_distance(enemy)` (straight-line metres); the\n"
    "-- gate is that distance <= FOURTH.CONTACT_BOUND_M. The old unit_in_range reach\n"
    "-- read (the intercept/pursuit reach that walked the caster) is NOT used, and an\n"
    "-- unreadable distance is treated as OUT of contact (fail-safe).\n"
    "function FOURTH.eg_enemy_within_contact(unit, enemy)\n"
    "\tlocal gap = FOURTH.eg_enemy_gap(unit, enemy)\n"
    "\tif gap == nil then return false end\n"
    "\treturn gap <= FOURTH.CONTACT_BOUND_M\n"
    "end",
    "A-within-contact")

ann = sub(ann,
    "\t\t\t\t\t\t\t\tand FOURTH.eg_enemy_in_range(unit, enemy) then",
    "\t\t\t\t\t\t\t\tand FOURTH.eg_enemy_within_contact(unit, enemy) then",
    "A-eval-gate")

ann = sub(ann,
    "\t-- ACCUSATION ENEMY RE-CHECK (this round): re-read the chosen enemy's\n"
    "\t-- condition immediately before the cast - it must still be ALIVE and still\n"
    "\t-- IN MELEE or UNDER FIRE and still IN RANGE, or the cast is SKIPPED. The\n"
    "\t-- chosen enemy is the CAST TARGET - never the owner.",
    "\t-- ACCUSATION ENEMY RE-CHECK (harness 96): re-read the chosen enemy's\n"
    "\t-- condition immediately before the cast - it must still be ALIVE and still\n"
    "\t-- IN MELEE or UNDER FIRE and still WITHIN the melee-contact bound (re-read\n"
    "\t-- here via unit:unit_distance, straight-line metres), or the cast is SKIPPED.\n"
    "\t-- The chosen enemy is the CAST TARGET - never the owner.",
    "A-recheck-comment")

ann = sub(ann,
    "\t\tlocal in_range_now = FOURTH.eg_enemy_in_range(unit, enemy)\n"
    "\t\tif not alive_now or not (still_melee or still_shot) or not in_range_now then",
    "\t\tlocal gap_now = FOURTH.eg_enemy_gap(unit, enemy)\n"
    "\t\tlocal in_contact_now = (gap_now ~= nil and gap_now <= FOURTH.CONTACT_BOUND_M)\n"
    "\t\tif not alive_now or not (still_melee or still_shot) or not in_contact_now then",
    "A-recheck-gate")

# ---------------------------------------------------------------------------
# sanity
# ---------------------------------------------------------------------------
assert "FOURTH.RANGE_FRACTION = 0.70" in live and "FOURTH.RANGE_FRACTION = 0.70" in ann
assert "FOURTH.CONTACT_BOUND_M = 10" in live and "FOURTH.CONTACT_BOUND_M = 10" in ann
assert "FOURTH.BLOOD_SACRIFICE_RANGE_M = FOURTH.CONTACT_BOUND_M" in live and \
    "FOURTH.BLOOD_SACRIFICE_RANGE_M = FOURTH.CONTACT_BOUND_M" in ann
assert "FOURTH.EAT_DA_RUNTS_RANGE_M = FOURTH.CONTACT_BOUND_M" in live and \
    "FOURTH.EAT_DA_RUNTS_RANGE_M = FOURTH.CONTACT_BOUND_M" in ann
assert "function FOURTH.eg_enemy_within_contact(unit, enemy)" in live and \
    "function FOURTH.eg_enemy_within_contact(unit, enemy)" in ann
# the old names / intercept-derived values are GONE
for bad in ("FOURTH.ACCUSATION_RANGE_M", "FOURTH.ACCUSATION_CONTACT_M", "eg_enemy_in_range",
            "FOURTH.BLOOD_SACRIFICE_RANGE_M = 70", "FOURTH.EAT_DA_RUNTS_RANGE_M = 70"):
    assert bad not in live, "live still has " + bad
    assert bad not in ann, "ann still has " + bad
# unchanged: the charge-window pair, the ability table, the self-cast writes
for s in (live, ann):
    assert 'CHARGE_MIN_DISTANCE_M    = 12' in s
    assert 'CHARGE_MAX_DISTANCE_M    = 60' in s
assert live.count("\t{ marker = ") == 579 and ann.count("\t{ marker = ") == 579
assert live.count("FOURTH.cast_target = unit") == 2 and ann.count("FOURTH.cast_target = unit") == 2
# the moved range constants for the effect_range abilities stay (70% rule)
for s in (live, ann):
    assert "local GLORIOUS_DEATH_RANGE_M = 38" in s
    assert "FOURTH.VERMINKING_RANGE_M = 24" in s
    assert "FOURTH.METALLURGY_RANGE_M = 24" in s
    assert "FOURTH.WAVERING_RANGE_M = 24" in s
# the reading copy stays log-free and find-free
assert "log(" not in ann, "annotated copy gained a log() call"
assert "string.find" not in ann, "annotated copy gained a string.find call"
# the real-distance log lines exist in the live source
assert "distance=\" .. ((best_gap ~= nil) and string.format(\"%.1f\", best_gap) or \"?\")" in live
assert "distance=\" .. string.format(\"%.1f\", gap_now) .. \"m range=\"" in live

write(LIVE, live)
write(ANN, ann)
print("wrote", LIVE, len(live), "bytes")
print("wrote", ANN, len(ann), "bytes")
print("OK: RANGE SOURCE corrected -> CONTACT_BOUND_M = 10 for ACC/BS/EDR; distances logged")
