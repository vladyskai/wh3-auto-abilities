# -*- coding: utf-8 -*-
"""ROUND h95 IMPLEMENTATION: the user's STANDING 70% RANGE RULE.

Adds the rule constant FOURTH.RANGE_FRACTION = 0.70 and re-derives EVERY
trigger-range constant as floor(real game-data range * 0.70), rounded down.
Snapshots the current files first (pre95_*.lua) as the RED CONTROL target.

THE USER'S RULING (verbatim): "for abilities that include a range, we should
always specify 70% of the actual range to avoid such things" - the symptom
being the Witch Hunter WALKING because a cast was offered at a target inside
the game's intercept reach but outside a comfortable cast range. Ruled
ABSOLUTE afterwards: "...No exceptions." - so the old field-tuned 25 m
Glorious Death gate is REPLACED by 38 m too.

Applies the SAME logical change to the LIVE mod and the ANNOTATED reading copy
(each in its own idiom; the annotated copy returns booleans and is log-free).
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
write(HERE + "/pre95_live.lua", live)
write(HERE + "/pre95_ann.lua", ann)
print("wrote pre95_live.lua", len(live), "bytes")
print("wrote pre95_ann.lua", len(ann), "bytes")

RULE = (
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
"FOURTH.RANGE_FRACTION = 0.70\n")

RULE_A = (
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
"FOURTH.RANGE_FRACTION = 0.70\n")

# ---------------------------------------------------------------------------
# LIVE
# ---------------------------------------------------------------------------
L_TBL_OLD = ("\t-- ui id -> (marker -> true), nested and miss-safe like armed /\n"
             "\t-- last_attempt_at (a read never builds an inner table).\n"
             "\tmissing_logged = {},\n}")
L_TBL_NEW = L_TBL_OLD + "\n\n" + RULE
live = sub(live, L_TBL_OLD, L_TBL_NEW, "L-rule")

# GLORIOUS DEATH: 55 -> 38
L_GD_OLD = (
"-- GLORIOUS DEATH'S TRIGGER RANGE (this round) - DELIBERATELY CONSERVATIVE.\n"
"-- The ability's wiki effects line reads \"Effect range: 55m\" (kept here for\n"
"-- reference), but the user's FIELD TESTING showed a 55 m trigger fired too\n"
"-- early, so the gate is set to a TIGHTER, deliberately conservative trigger\n"
"-- range: GLORIOUS_DEATH_RANGE_M is BELOW the ability's 55 m wiki aura on\n"
"-- purpose. The range gate below offers, and re-checks just before the cast,\n"
"-- an in-melee Slayer ally only when the owner is within GLORIOUS_DEATH_RANGE_M\n"
"-- metres of it. ONE place to tune the gate.\n"
"local GLORIOUS_DEATH_RANGE_M = 25")
L_GD_NEW = (
"-- GLORIOUS DEATH'S TRIGGER RANGE (this round) - THE STANDING 70% RULE.\n"
"-- REAL range 55.0000 m = effect_range (unit_spec_abil.tsv,\n"
"-- wh3_dlc25_lord_abilities_glorious_death) - the ability's own aura.\n"
"-- 55 * 0.70 = 38.5 -> 38 m (FLOORED, FOURTH.RANGE_FRACTION). The gate below\n"
"-- offers, and re-checks just before the cast, an in-melee Slayer ally only\n"
"-- when the owner is within GLORIOUS_DEATH_RANGE_M metres of it. ONE place to\n"
"-- tune the gate. (HISTORY: harness 87 shipped a FIELD-TUNED 25 m here because\n"
"-- the 55 m aura fired too early; the user then ruled the 70% rule ABSOLUTE -\n"
"-- \"...No exceptions.\" - so 25 m was REPLACED by 38 m at his direction.)\n"
"local GLORIOUS_DEATH_RANGE_M = 38")
live = sub(live, L_GD_OLD, L_GD_NEW, "L-gd")

# VERMINKING: 35 -> 24
L_VM_OLD = (
"-- WILL OF THE VERMINKING'S TRIGGER RANGE (this round) - DELIBERATELY\n"
"-- CONSERVATIVE, stored on the FOURTH bag (no new chunk local). The ability's\n"
"-- GAME DATA gives a 35 m ally aura (unit_spec_abil.tsv: effect_range =\n"
"-- 35.0000, ai_usage = augment_melee); following the FIELD-PROVEN conservative\n"
"-- pattern used for Glorious Death (25 m vs its 55 m wiki aura) the trigger\n"
"-- radius here is a deliberately conservative 25 m - 10 m INSIDE the 35 m\n"
"-- aura. The ally arm fires only while the OWNER is within\n"
"-- FOURTH.VERMINKING_RANGE_M of the wavering ally. ONE place to tune.\n"
"FOURTH.VERMINKING_RANGE_M = 25")
L_VM_NEW = (
"-- WILL OF THE VERMINKING'S TRIGGER RANGE (this round) - THE STANDING 70% RULE.\n"
"-- REAL range 35.0000 m = effect_range (unit_spec_abil.tsv,\n"
"-- wh3_dlc29_lord_abilities_will_of_the_verminking, ai_usage = augment_melee).\n"
"-- 35 * 0.70 = 24.5 -> 24 m (FLOORED, FOURTH.RANGE_FRACTION). Stored on the\n"
"-- FOURTH bag (no new chunk local). The ally arm fires only while the OWNER is\n"
"-- within FOURTH.VERMINKING_RANGE_M of the wavering ally. ONE place to tune.\n"
"FOURTH.VERMINKING_RANGE_M = 24")
live = sub(live, L_VM_OLD, L_VM_NEW, "L-vm")

# METALLURGY: 35 -> 24
L_MT_OLD = (
"-- ENCHANTED METALLURGY'S TRIGGER RANGE (this round) - DELIBERATELY\n"
"-- CONSERVATIVE, stored on the FOURTH bag (no new chunk local). The ability's\n"
"-- GAME DATA gives a 35 m ally aura (unit_spec_abil.tsv: effect_range =\n"
"-- 35.0000 for all four keys, ai_usage = augment_melee); following the\n"
"-- FIELD-PROVEN conservative pattern used for Glorious Death and Will of the\n"
"-- Verminking (25 m against a larger aura) the trigger radius here is a\n"
"-- deliberately conservative 25 m - 10 m INSIDE the 35 m aura. The ally arm\n"
"-- fires only while the OWNER is within FOURTH.METALLURGY_RANGE_M of the\n"
"-- in-melee ally. ONE place to tune.\n"
"FOURTH.METALLURGY_RANGE_M = 25")
L_MT_NEW = (
"-- ENCHANTED METALLURGY'S TRIGGER RANGE (this round) - THE STANDING 70% RULE.\n"
"-- REAL range 35.0000 m = effect_range (unit_spec_abil.tsv, for all four keys\n"
"-- wh3_main_character_abilities_enchanted_metallurgy[_flaming|_piercing|\n"
"-- _poison], ai_usage = augment_melee). 35 * 0.70 = 24.5 -> 24 m (FLOORED,\n"
"-- FOURTH.RANGE_FRACTION). Stored on the FOURTH bag (no new chunk local). The\n"
"-- ally arm fires only while the OWNER is within FOURTH.METALLURGY_RANGE_M of\n"
"-- the in-melee ally. ONE place to tune.\n"
"FOURTH.METALLURGY_RANGE_M = 24")
live = sub(live, L_MT_OLD, L_MT_NEW, "L-mt")

# WAVERING: 35 -> 24
L_WV_OLD = (
"-- WAVERING SELF-OR-ALLY (Fury of Ulric / the redesigned Commanding Presence):\n"
"-- fire when the OWNER is wavering, OR a friendly in-melee WAVERING ally lies\n"
"-- within the conservative trigger range; cast ON SELF (the effect is a\n"
"-- self-centred aura). THE TRIGGER RANGE is DELIBERATELY CONSERVATIVE against\n"
"-- the game-data 35 m aura (unit_spec_abil.tsv effect_range 35.0000 for both\n"
"-- keys). THE SAME SAFETY PATTERN as Glorious Death / Verminking / Metallurgy:\n"
"-- the CLOSEST qualifying in-melee wavering ally is chosen, the gap is\n"
"-- RE-CHECKED immediately before the cast and the cast is SKIPPED on drift. The\n"
"-- self-wavering arm leaves FOURTH.ws_ally nil - never gated.\n"
"FOURTH.WAVERING_RANGE_M = 25")
L_WV_NEW = (
"-- WAVERING SELF-OR-ALLY (Fury of Ulric / the redesigned Commanding Presence):\n"
"-- fire when the OWNER is wavering, OR a friendly in-melee WAVERING ally lies\n"
"-- within the trigger range; cast ON SELF (the effect is a self-centred aura).\n"
"-- THE TRIGGER RANGE (this round) - THE STANDING 70% RULE. REAL range 35.0000 m\n"
"-- = effect_range (unit_spec_abil.tsv) for all three keys that ride it -\n"
"-- wh3_dlc29_lord_active_commanding_presence, wh3_dlc29_spell_bound_prayer_\n"
"-- fury_of_ulric and wh2_dlc09_character_abilities_stay_here_ill_get_help.\n"
"-- 35 * 0.70 = 24.5 -> 24 m (FLOORED, FOURTH.RANGE_FRACTION). THE SAME SAFETY\n"
"-- PATTERN as Glorious Death / Verminking / Metallurgy: the CLOSEST qualifying\n"
"-- in-melee wavering ally is chosen, the gap is RE-CHECKED immediately before\n"
"-- the cast and the cast is SKIPPED on drift. The self-wavering arm leaves\n"
"-- FOURTH.ws_ally nil - never gated.\n"
"FOURTH.WAVERING_RANGE_M = 24")
live = sub(live, L_WV_OLD, L_WV_NEW, "L-wv")

# BLOOD SACRIFICE: 100 -> 70
L_BS_OLD = (
"-- BLOOD SACRIFICE'S TRIGGER RANGE (this round) - deliberately conservative.\n"
"FOURTH.BLOOD_SACRIFICE_RANGE_M = 25")
L_BS_NEW = (
"-- BLOOD SACRIFICE'S TRIGGER RANGE (this round) - THE STANDING 70% RULE. The\n"
"-- ability has NO aura (effect_range = 0.0000, num_effected_friendly_units = 1),\n"
"-- so its REAL game-data range is its target_intercept_range = 100.0000 m\n"
"-- (unit_spec_abil.tsv, wh3_dlc26_lord_abilities_blood_sacrifice).\n"
"-- 100 * 0.70 = 70.0 -> 70 m (FLOORED, FOURTH.RANGE_FRACTION).\n"
"FOURTH.BLOOD_SACRIFICE_RANGE_M = 70")
live = sub(live, L_BS_OLD, L_BS_NEW, "L-bs")

# EAT DA RUNTS: 100 -> 70
L_ED_OLD = (
"-- EAT DA RUNTS!'S TRIGGER RANGE (this round) - deliberately conservative.\n"
"FOURTH.EAT_DA_RUNTS_RANGE_M = 25")
L_ED_NEW = (
"-- EAT DA RUNTS!'S TRIGGER RANGE (this round) - THE STANDING 70% RULE. The\n"
"-- ability has NO aura (effect_range = 0.0000, num_effected_friendly_units = 1),\n"
"-- so its REAL game-data range is its target_intercept_range = 100.0000 m\n"
"-- (unit_spec_abil.tsv, wh3_dlc26_unit_abilities_eat_da_runts).\n"
"-- 100 * 0.70 = 70.0 -> 70 m (FLOORED, FOURTH.RANGE_FRACTION).\n"
"FOURTH.EAT_DA_RUNTS_RANGE_M = 70")
live = sub(live, L_ED_OLD, L_ED_NEW, "L-ed")

# ACCUSATION: 75 -> 52
L_AC_OLD = (
"-- ACCUSATION'S TRIGGER RANGE - the ability's own target_intercept_range (75 m),\n"
"-- the reach the round-4 probe named. DELIBERATELY a named constant.\n"
"FOURTH.ACCUSATION_RANGE_M = 75")
L_AC_NEW = (
"-- ACCUSATION'S TRIGGER RANGE (this round) - THE STANDING 70% RULE. REAL range\n"
"-- 75.0000 m = the ability's own target_intercept_range (unit_spec_abil.tsv,\n"
"-- wh_main_hero_abilities_accusation; effect_range = 0.0000, so the intercept\n"
"-- reach is the real range). 75 * 0.70 = 52.5 -> 52 m (FLOORED,\n"
"-- FOURTH.RANGE_FRACTION). SET TO 52 AFTER THE CASTER WAS SEEN TO WALK toward\n"
"-- an enemy that sat inside the 75 m reach but outside a comfortable cast range\n"
"-- - the very symptom this rule exists to remove.\n"
"FOURTH.ACCUSATION_RANGE_M = 52")
live = sub(live, L_AC_OLD, L_AC_NEW, "L-ac")

# ---------------------------------------------------------------------------
# ANN (the reading copy)
# ---------------------------------------------------------------------------
A_TBL_OLD = ("\t-- ui id -> (marker -> true): one line per pair for a cast with no target.\n"
             "\tmissing_logged = {},\n}")
A_TBL_NEW = A_TBL_OLD + "\n\n" + RULE_A
ann = sub(ann, A_TBL_OLD, A_TBL_NEW, "A-rule")

A_GD_OLD = (
"-- GLORIOUS DEATH'S TRIGGER RANGE (this round) - DELIBERATELY CONSERVATIVE.\n"
"-- The ability's wiki effects line reads \"Effect range: 55m\" (reference only);\n"
"-- the user's FIELD TESTING showed a 55 m trigger fired too early, so this is\n"
"-- a TIGHTER, deliberately conservative trigger range - GLORIOUS_DEATH_RANGE_M\n"
"-- is BELOW the ability's 55 m wiki aura on purpose. The gate below offers,\n"
"-- and re-checks just before the cast, an in-melee Slayer ally only when the\n"
"-- owner is within GLORIOUS_DEATH_RANGE_M metres of it.\n"
"local GLORIOUS_DEATH_RANGE_M = 25")
A_GD_NEW = (
"-- GLORIOUS DEATH'S TRIGGER RANGE (this round) - THE STANDING 70% RULE. REAL\n"
"-- range 55.0000 m = effect_range (unit_spec_abil.tsv,\n"
"-- wh3_dlc25_lord_abilities_glorious_death). 55 * 0.70 = 38.5 -> 38 m (FLOORED,\n"
"-- FOURTH.RANGE_FRACTION). The gate offers, and re-checks just before the cast,\n"
"-- an in-melee Slayer ally only when the owner is within GLORIOUS_DEATH_RANGE_M\n"
"-- metres of it. (HISTORY: a FIELD-TUNED 25 m shipped here; the user ruled the\n"
"-- 70% rule ABSOLUTE - \"...No exceptions.\" - so it is now 38 m.)\n"
"local GLORIOUS_DEATH_RANGE_M = 38")
ann = sub(ann, A_GD_OLD, A_GD_NEW, "A-gd")

A_VM_OLD = (
"-- WILL OF THE VERMINKING'S TRIGGER RANGE (this round) - DELIBERATELY\n"
"-- CONSERVATIVE, stored on the FOURTH bag (no new chunk local). The ability's\n"
"-- GAME DATA gives a 35 m ally aura (unit_spec_abil.tsv: effect_range =\n"
"-- 35.0000, ai_usage = augment_melee); following the FIELD-PROVEN conservative\n"
"-- pattern used for Glorious Death (25 m vs its 55 m wiki aura) the trigger\n"
"-- radius here is a deliberately conservative 25 m - 10 m INSIDE the 35 m\n"
"-- aura. The ally arm fires only while the OWNER is within\n"
"-- FOURTH.VERMINKING_RANGE_M of the wavering ally. ONE place to tune.\n"
"FOURTH.VERMINKING_RANGE_M = 25")
A_VM_NEW = (
"-- WILL OF THE VERMINKING'S TRIGGER RANGE (this round) - THE STANDING 70% RULE.\n"
"-- REAL range 35.0000 m = effect_range (unit_spec_abil.tsv,\n"
"-- wh3_dlc29_lord_abilities_will_of_the_verminking, ai_usage = augment_melee).\n"
"-- 35 * 0.70 = 24.5 -> 24 m (FLOORED, FOURTH.RANGE_FRACTION). Stored on the\n"
"-- FOURTH bag (no new chunk local). The ally arm fires only while the OWNER is\n"
"-- within FOURTH.VERMINKING_RANGE_M of the wavering ally. ONE place to tune.\n"
"FOURTH.VERMINKING_RANGE_M = 24")
ann = sub(ann, A_VM_OLD, A_VM_NEW, "A-vm")

A_MT_OLD = (
"-- ENCHANTED METALLURGY'S TRIGGER RANGE (this round) - DELIBERATELY\n"
"-- CONSERVATIVE, stored on the FOURTH bag (no new chunk local). The ability's\n"
"-- GAME DATA gives a 35 m ally aura (unit_spec_abil.tsv: effect_range =\n"
"-- 35.0000 for all four keys, ai_usage = augment_melee); following the\n"
"-- FIELD-PROVEN conservative pattern used for Glorious Death and Will of the\n"
"-- Verminking (25 m against a larger aura) the trigger radius here is a\n"
"-- deliberately conservative 25 m - 10 m INSIDE the 35 m aura. ONE place to tune.\n"
"FOURTH.METALLURGY_RANGE_M = 25")
A_MT_NEW = (
"-- ENCHANTED METALLURGY'S TRIGGER RANGE (this round) - THE STANDING 70% RULE.\n"
"-- REAL range 35.0000 m = effect_range (unit_spec_abil.tsv, for all four keys,\n"
"-- ai_usage = augment_melee). 35 * 0.70 = 24.5 -> 24 m (FLOORED,\n"
"-- FOURTH.RANGE_FRACTION). Stored on the FOURTH bag (no new chunk local). The\n"
"-- ally arm fires only while the OWNER is within FOURTH.METALLURGY_RANGE_M of\n"
"-- the in-melee ally. ONE place to tune.\n"
"FOURTH.METALLURGY_RANGE_M = 24")
ann = sub(ann, A_MT_OLD, A_MT_NEW, "A-mt")

A_WV_OLD = (
"-- WAVERING SELF-OR-ALLY (Fury of Ulric / redesigned Commanding Presence): the\n"
"-- OWNER is wavering, OR a friendly in-melee wavering ally is within the\n"
"-- conservative trigger range; cast on self. THE TRIGGER RANGE is DELIBERATELY\n"
"-- CONSERVATIVE against the game-data 35 m aura (unit_spec_abil.tsv effect_range\n"
"-- 35.0000). Same safety pattern as Glorious Death / Verminking / Metallurgy:\n"
"-- closest ally, pre-cast gap re-check, skip on drift.\n"
"FOURTH.WAVERING_RANGE_M = 25")
A_WV_NEW = (
"-- WAVERING SELF-OR-ALLY (Fury of Ulric / redesigned Commanding Presence): the\n"
"-- OWNER is wavering, OR a friendly in-melee wavering ally is within the\n"
"-- trigger range; cast on self. THE TRIGGER RANGE (this round) - THE STANDING\n"
"-- 70% RULE. REAL range 35.0000 m = effect_range (unit_spec_abil.tsv) for the\n"
"-- three keys that ride it. 35 * 0.70 = 24.5 -> 24 m (FLOORED,\n"
"-- FOURTH.RANGE_FRACTION). Same safety pattern as Glorious Death / Verminking /\n"
"-- Metallurgy: closest ally, pre-cast gap re-check, skip on drift.\n"
"FOURTH.WAVERING_RANGE_M = 24")
ann = sub(ann, A_WV_OLD, A_WV_NEW, "A-wv")

A_BS_OLD = ("FOURTH.BLOOD_SACRIFICE_RANGE_M = 25")
A_BS_NEW = (
"-- BLOOD SACRIFICE'S TRIGGER RANGE (this round) - THE STANDING 70% RULE. No\n"
"-- aura (effect_range = 0.0000), so the REAL range is target_intercept_range =\n"
"-- 100.0000 m (unit_spec_abil.tsv). 100 * 0.70 = 70.0 -> 70 m (FLOORED,\n"
"-- FOURTH.RANGE_FRACTION).\n"
"FOURTH.BLOOD_SACRIFICE_RANGE_M = 70")
ann = sub(ann, A_BS_OLD, A_BS_NEW, "A-bs")

A_ED_OLD = ("FOURTH.EAT_DA_RUNTS_RANGE_M = 25")
A_ED_NEW = (
"-- EAT DA RUNTS!'S TRIGGER RANGE (this round) - THE STANDING 70% RULE. No aura\n"
"-- (effect_range = 0.0000), so the REAL range is target_intercept_range =\n"
"-- 100.0000 m (unit_spec_abil.tsv). 100 * 0.70 = 70.0 -> 70 m (FLOORED,\n"
"-- FOURTH.RANGE_FRACTION).\n"
"FOURTH.EAT_DA_RUNTS_RANGE_M = 70")
ann = sub(ann, A_ED_OLD, A_ED_NEW, "A-ed")

A_AC_OLD = (
"-- ACCUSATION'S TRIGGER RANGE - the ability's own target_intercept_range (75 m).\n"
"FOURTH.ACCUSATION_RANGE_M = 75")
A_AC_NEW = (
"-- ACCUSATION'S TRIGGER RANGE (this round) - THE STANDING 70% RULE. REAL range\n"
"-- 75.0000 m = target_intercept_range (unit_spec_abil.tsv; effect_range 0.0000).\n"
"-- 75 * 0.70 = 52.5 -> 52 m (FLOORED, FOURTH.RANGE_FRACTION). 52 m after the\n"
"-- caster was seen to WALK toward an enemy inside the 75 m reach.\n"
"FOURTH.ACCUSATION_RANGE_M = 52")
ann = sub(ann, A_AC_OLD, A_AC_NEW, "A-ac")

# ---------------------------------------------------------------------------
# sanity
# ---------------------------------------------------------------------------
assert "FOURTH.RANGE_FRACTION = 0.70" in live and "FOURTH.RANGE_FRACTION = 0.70" in ann
assert "local GLORIOUS_DEATH_RANGE_M = 38" in live and "local GLORIOUS_DEATH_RANGE_M = 38" in ann
assert "local GLORIOUS_DEATH_RANGE_M = 25" not in live and "local GLORIOUS_DEATH_RANGE_M = 25" not in ann
for tok in ("FOURTH.VERMINKING_RANGE_M = 24", "FOURTH.METALLURGY_RANGE_M = 24",
            "FOURTH.WAVERING_RANGE_M = 24", "FOURTH.BLOOD_SACRIFICE_RANGE_M = 70",
            "FOURTH.EAT_DA_RUNTS_RANGE_M = 70", "FOURTH.ACCUSATION_RANGE_M = 52"):
    assert tok in live, "live missing " + tok
    assert tok in ann, "ann missing " + tok
# nothing of the old values signed with a range name remains
for bad in ("FOURTH.VERMINKING_RANGE_M = 25", "FOURTH.METALLURGY_RANGE_M = 25",
            "FOURTH.WAVERING_RANGE_M = 25", "FOURTH.BLOOD_SACRIFICE_RANGE_M = 25",
            "FOURTH.EAT_DA_RUNTS_RANGE_M = 25", "FOURTH.ACCUSATION_RANGE_M = 75"):
    assert bad not in live, "live still has " + bad
    assert bad not in ann, "ann still has " + bad
# unchanged: the charge-window pair, the ability table, the cast-target writes
for s in (live, ann):
    assert 'CHARGE_MIN_DISTANCE_M    = 12' in s
for s in (live, ann):
    assert 'CHARGE_MAX_DISTANCE_M    = 60' in s
assert live.count("\t{ marker = ") == 579 and ann.count("\t{ marker = ") == 579
assert live.count("FOURTH.cast_target = unit") == 2 and ann.count("FOURTH.cast_target = unit") == 2
# the reading copy stays log-free and find-free
assert "log(" not in ann, "annotated copy gained a log() call"
assert "string.find" not in ann, "annotated copy gained a string.find call"

write(LIVE, live)
write(ANN, ann)
print("wrote", LIVE, len(live), "bytes")
print("wrote", ANN, len(ann), "bytes")
print("OK: RANGE_FRACTION added; GD=38 VM=24 MT=24 WV=24 BS=70 EDR=70 ACC=52")
