# -*- coding: utf-8 -*-
"""ROUND h97 - THE REST OF CLASS A (enemy-targeted abilities).

Applies the PROVEN Accusation enemy-targeting mechanism to the other 97 Class-A
entries derived from WH3_audit_report.md (98 total; Accusation 263 already done):
  * 88 ride the EXISTING `enemy_engaged_or_shot` trigger (enemy-UNIT casts);
  *  9 ride a NEW `enemy_ground_area` trigger (enemy-GROUND area hexes) which
     casts through perform_special_ability_ground(key, ENEMY_POSITION, 0, 0).
Every entry carries its own 70% bound (FOURTH.ENEMY_CAST_R<real>) - one named
constant per REAL target_intercept_range (unit_spec_abil.tsv), shared where the
real range is shared. The offer test is unit:unit_distance(enemy) <= the bound
ONLY (never unit_in_range). Fresh handles, in-melee-preferred trigger, pre-cast
re-check, hold, cast target = the enemy, distinct log prefixes, real distance.
"""
import io, os, re, json

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = "C:/Users/vlady/Desktop/WH3_mod/mod_source"
LIVE = ROOT + "/script/battle/mod/zz_test_deadly_onslaught.lua"
ANN  = "C:/Users/vlady/Desktop/WH3_mod/docs/WH3_auto_ability_annotated.lua"
NL = chr(10); T = chr(9)

def read(p): return io.open(p, encoding="utf-8", newline="").read()
def write(p, s): io.open(p, "w", encoding="utf-8", newline="").write(s)
def L(*ls): return NL.join(ls)

def sub(text, old, new, label):
    n = text.count(old)
    assert n == 1, "%s: %d matches (want 1)" % (label, n)
    return text.replace(old, new, 1)

plan = json.load(open(ROOT + "/../WH3_audit/_classA_impl_plan.json", encoding="utf-8"))

live = read(HERE + "/pre97_live.lua")
ann  = read(HERE + "/pre97_ann.lua")

GKEYS = [k for p in plan if p['ground'] for k in p['keys']]

# ===========================================================================
# THE CONSTANT BLOCK (both files)
# ===========================================================================
CONST_OLD = L(
    "FOURTH.RANGE_FRACTION = 0.70",
    "",
    "",
    "-- true / false / nil - only exact true means \"morale below the threshold\".")
CONST_NEW = L(
    "FOURTH.RANGE_FRACTION = 0.70",
    "",
    "",
    "-- ============================================================================",
    "-- THE ENEMY-TARGETED CAST BOUNDS (Class A, harness 97). ONE named constant per",
    "-- REAL target_intercept_range (unit_spec_abil.tsv) - several abilities that",
    "-- share a real range SHARE the constant. The VALUE is the trigger bound =",
    "-- floor(real * FOURTH.RANGE_FRACTION) (70%), rounded DOWN to a whole metre",
    "-- (the +1e-9 epsilon mirrors the build assertion's floor). The R<N> suffix is",
    "-- the ability's REAL range in metres; the bound is the number",
    "-- unit:unit_distance(enemy) (EDGE-TO-EDGE metres, battle_unit.lua:160) is",
    "-- compared against - NEVER the engine's own unit_in_range reach read.",
    "--   real  15.0 m ->  10     real  75.0 m ->  52     real 180.0 m -> 126",
    "--   real  20.0 m ->  14     real 100.0 m ->  70     real 200.0 m -> 140",
    "--   real  30.0 m ->  21     real 150.0 m -> 105     real 500.0 m -> 350",
    "--   real  35.0 m ->  24     real  70.0 m ->  49",
    "--   real  50.0 m ->  35",
    "-- ============================================================================",
    "FOURTH.ENEMY_CAST_R15  = 10",
    "FOURTH.ENEMY_CAST_R20  = 14",
    "FOURTH.ENEMY_CAST_R30  = 21",
    "FOURTH.ENEMY_CAST_R35  = 24",
    "FOURTH.ENEMY_CAST_R50  = 35",
    "FOURTH.ENEMY_CAST_R70  = 49",
    "FOURTH.ENEMY_CAST_R75  = 52",
    "FOURTH.ENEMY_CAST_R100 = 70",
    "FOURTH.ENEMY_CAST_R150 = 105",
    "FOURTH.ENEMY_CAST_R180 = 126",
    "FOURTH.ENEMY_CAST_R200 = 140",
    "FOURTH.ENEMY_CAST_R500 = 350",
    "",
    "-- the ability's REAL target_intercept_range -> its named 70% bound, for the",
    "-- load-time per-ability lookup (each Class-A entry carries range_real).",
    "FOURTH.ENEMY_CAST = {",
    T + "[15]  = FOURTH.ENEMY_CAST_R15,",
    T + "[20]  = FOURTH.ENEMY_CAST_R20,",
    T + "[30]  = FOURTH.ENEMY_CAST_R30,",
    T + "[35]  = FOURTH.ENEMY_CAST_R35,",
    T + "[50]  = FOURTH.ENEMY_CAST_R50,",
    T + "[70]  = FOURTH.ENEMY_CAST_R70,",
    T + "[75]  = FOURTH.ENEMY_CAST_R75,",
    T + "[100] = FOURTH.ENEMY_CAST_R100,",
    T + "[150] = FOURTH.ENEMY_CAST_R150,",
    T + "[180] = FOURTH.ENEMY_CAST_R180,",
    T + "[200] = FOURTH.ENEMY_CAST_R200,",
    T + "[500] = FOURTH.ENEMY_CAST_R500,",
    "}",
    "",
    "",
    "-- true / false / nil - only exact true means \"morale below the threshold\".")
live = sub(live, CONST_OLD, CONST_NEW, "live constants")
ann  = sub(ann,  CONST_OLD, CONST_NEW, "ann constants")

# ===========================================================================
# THE ENEMY-GROUND KEY SET (both files)
# ===========================================================================
GKEYS_NEW = L(
    "-- THE ENEMY-GROUND AREA KEYS (Class A, harness 97): keys whose db row is",
    "-- target_enemies + target_ground - the cast is PLACED ON ENEMY GROUND, so the",
    "-- ground form perform_special_ability_ground(key, ENEMY_POSITION, 0, 0) is",
    "-- used (never the caster's own position). Exact keys, lowercase.",
    "enemy_ground_keys = {") + NL + NL.join(
    [T + T + '["' + k + '"] = true,' for k in GKEYS]) + NL + L(
    T + "},")

LIVE_TBL_OLD = L(
    T + "ground_keys = {",
    T * 2 + '["wh3_dlc24_character_abilities_tacticians_stand_your_ground"] = true,',
    T + "},",
    T + "-- One line per (unit, marker) for a targeted cast with no readable target:")
LIVE_TBL_NEW = L(
    T + "ground_keys = {",
    T * 2 + '["wh3_dlc24_character_abilities_tacticians_stand_your_ground"] = true,',
    T + "},",
    T + GKEYS_NEW,
    T + "-- One line per (unit, marker) for a targeted cast with no readable target:")
live = sub(live, LIVE_TBL_OLD, LIVE_TBL_NEW, "live enemy_ground_keys")

ANN_TBL_OLD = L(
    T + "ground_keys = {",
    T * 2 + '["wh3_dlc24_character_abilities_tacticians_stand_your_ground"] = true,',
    T + "},",
    T + "-- ui id -> (marker -> true): one line per pair for a cast with no target.")
ANN_TBL_NEW = L(
    T + "ground_keys = {",
    T * 2 + '["wh3_dlc24_character_abilities_tacticians_stand_your_ground"] = true,',
    T + "},",
    T + GKEYS_NEW,
    T + "-- ui id -> (marker -> true): one line per pair for a cast with no target.")
ann = sub(ann, ANN_TBL_OLD, ANN_TBL_NEW, "ann enemy_ground_keys")

# ===========================================================================
# THE ENEMY-GROUND CAST HELPER (both files)
# ===========================================================================
GC_OLD = L(
    "function FOURTH.ground_cast(uc, unit, ability_key)",
    T + "local ok_pos, pos = pcall(function() return unit:position() end)",
    T + "if not ok_pos or pos == nil then",
    T + T + "return nil, nil, true",
    T + "end",
    T + "local ok_call, err_call = pcall(function()",
    T + T + "uc:perform_special_ability_ground(ability_key, pos, 0, 0)",
    T + "end)",
    T + "return ok_call, err_call, false",
    "end")
GC_NEW = GC_OLD + NL + L(
    "",
    "-- THE ENEMY-GROUND CAST HELPER (Class A, harness 97): the same shape as",
    "-- ground_cast, but the position is the CHOSEN ENEMY's own ground position",
    "-- (enemy:position()) - the placement an enemy-GROUND area hex requires. The",
    "-- controller is the FRESH one (FOURTH.eg_caster_su.uc); a position that",
    "-- cannot be read returns no_target = true (the caller must not fire).",
    "function FOURTH.enemy_ground_cast(uc, enemy, ability_key)",
    T + "local ok_pos, pos = pcall(function() return enemy:position() end)",
    T + "if not ok_pos or pos == nil then",
    T + T + "return nil, nil, true",
    T + "end",
    T + "local ok_call, err_call = pcall(function()",
    T + T + "uc:perform_special_ability_ground(ability_key, pos, 0, 0)",
    T + "end)",
    T + "return ok_call, err_call, false",
    "end")
live = sub(live, GC_OLD, GC_NEW, "live enemy_ground_cast")
ann  = sub(ann,  GC_OLD, GC_NEW, "ann enemy_ground_cast")

# ===========================================================================
# THE ENEMY SLOTS (init): add range/marker/ground (both files)
# ===========================================================================
LIVE_INIT_OLD = L(
    "FOURTH.eg_enemy = nil",
    "FOURTH.eg_arm = nil",
    "FOURTH.eg_caster_su = nil")
LIVE_INIT_NEW = L(
    "FOURTH.eg_enemy = nil",
    "FOURTH.eg_arm = nil",
    "FOURTH.eg_caster_su = nil",
    "-- the CURRENT ability's 70% bound and its marker (set by the poll before every",
    "-- evaluate), and whether the current enemy trigger is the GROUND form.",
    "FOURTH.eg_range_m = nil",
    "FOURTH.eg_marker = nil",
    "FOURTH.eg_ground = nil")
live = sub(live, LIVE_INIT_OLD, LIVE_INIT_NEW, "live eg init")

ANN_INIT_OLD = L(
    "FOURTH.eg_enemy = nil",
    "FOURTH.eg_arm = nil",
    "FOURTH.eg_caster_su = nil")
ANN_INIT_NEW = L(
    "FOURTH.eg_enemy = nil",
    "FOURTH.eg_arm = nil",
    "FOURTH.eg_caster_su = nil",
    "-- the CURRENT ability's 70% bound and its marker (set by the poll before every",
    "-- evaluate), and whether the current enemy trigger is the GROUND form.",
    "FOURTH.eg_range_m = nil",
    "FOURTH.eg_marker = nil",
    "FOURTH.eg_ground = nil")
ann = sub(ann, ANN_INIT_OLD, ANN_INIT_NEW, "ann eg init")

# ===========================================================================
# eg_enemy_within_bound: per-ability bound (keep the ACCUSATION default literal)
# ===========================================================================
BW_OLD = L(
    "function FOURTH.eg_enemy_within_bound(unit, enemy)",
    T + "local gap = FOURTH.eg_enemy_gap(unit, enemy)",
    T + "if gap == nil then return false end",
    T + "return gap <= FOURTH.ACCUSATION_RANGE_M",
    "end")
BW_NEW = L(
    "function FOURTH.eg_enemy_within_bound(unit, enemy)",
    T + "local gap = FOURTH.eg_enemy_gap(unit, enemy)",
    T + "if gap == nil then return false end",
    T + "-- THE PER-ABILITY BOUND: FOURTH.eg_range_m is the current ability's own",
    T + "-- 70% constant, set by the poll before every evaluate. Accusation (and any",
    T + "-- caller that leaves it unset) falls back to FOURTH.ACCUSATION_RANGE_M.",
    T + "local bound = FOURTH.eg_range_m",
    T + "if bound == nil then",
    T + T + "return gap <= FOURTH.ACCUSATION_RANGE_M",
    T + "end",
    T + "return gap <= bound",
    "end")
live = sub(live, BW_OLD, BW_NEW, "live within_bound")
ann  = sub(ann,  BW_OLD, BW_NEW, "ann within_bound")

# ===========================================================================
# THE EVALUATOR: shared picker + two thin wrappers
# ===========================================================================
LIVE_EV_OLD = L(
    "-- THE EVALUATOR: fire when an ENEMY unit in range is in melee OR under missile",
    "-- fire. The chosen enemy rides FOURTH.cast_target (the CAST TARGET) and",
    "-- FOURTH.eg_enemy (the pre-cast re-check slot) - the owner is NEVER the target.",
    "-- Returns the ATTEMPT reason string, or nil when nothing qualifies.",
    "function FOURTH.evaluate_enemy_engaged_or_shot(unit, routing)",
    T + "local reason = nil",
    T + "if not routing then",
    T * 2 + "local ok_coll, coll = pcall(function()",
    T * 3 + "return bm:get_scriptunits_for_main_enemy_army_to_local_player()",
    T * 2 + "end)",
    T * 2 + "if ok_coll and coll ~= nil then",
    T * 3 + "local ok_n, n = pcall(function() return coll:count() end)",
    T * 3 + "if ok_n and type(n) == \"number\" then",
    T * 4 + "local best_enemy, best_gap, best_arm = nil, nil, nil",
    T * 4 + "for i = 1, n do",
    T * 5 + "local ok_su, su = pcall(function() return coll:item(i) end)",
    T * 5 + "if ok_su and su ~= nil then",
    T * 6 + "local enemy = nil",
    T * 6 + "pcall(function() enemy = su.unit end)",
    T * 6 + "if enemy ~= nil then",
    T * 7 + "local ok_alive, alive = pcall(function() return enemy:number_of_men_alive() end)",
    T * 7 + "local valid = FOURTH.eg_enemy_valid(enemy)",
    T * 7 + "local ok_melee, melee = pcall(function() return enemy:is_in_melee() end)",
    T * 7 + "local arm = nil",
    T * 7 + "if ok_melee and melee == true then",
    T * 8 + "arm = \"melee\"",
    T * 7 + "elseif FOURTH.eg_under_missile_attack(enemy) then",
    T * 8 + "arm = \"missile\"",
    T * 7 + "end",
    T * 7 + "if arm ~= nil",
    T * 8 + "and ok_alive and type(alive) == \"number\" and alive > 0",
    T * 8 + "and (valid == nil or valid == true)",
    T * 8 + "and FOURTH.eg_enemy_within_bound(unit, enemy) then",
    T * 8 + "local gap = FOURTH.eg_enemy_gap(unit, enemy)",
    T * 8 + "if best_enemy == nil",
    T * 9 + "or (arm == \"melee\" and best_arm ~= \"melee\")",
    T * 9 + "or (arm == best_arm and gap ~= nil and (best_gap == nil or gap < best_gap)) then",
    T * 9 + "best_enemy, best_gap, best_arm = enemy, gap, arm",
    T * 8 + "end",
    T * 7 + "end",
    T * 6 + "end",
    T * 5 + "end",
    T * 4 + "end",
    T * 4 + "if best_enemy ~= nil then",
    T * 5 + "local etype = \"enemy\"",
    T * 5 + "pcall(function() etype = tostring(best_enemy:type()) end)",
    T * 5 + "log(\"  accusation target: '\" .. etype .. \"' is the chosen enemy (\" .. tostring(best_arm)",
    T * 6 + ".. \") distance=\" .. ((best_gap ~= nil) and string.format(\"%.1f\", best_gap) or \"?\")",
    T * 6 + ".. \"m bound=\" .. tostring(FOURTH.ACCUSATION_RANGE_M) .. \"m\")",
    T * 5 + "FOURTH.eg_enemy = best_enemy",
    T * 5 + "FOURTH.eg_arm = best_arm",
    T * 5 + "FOURTH.eg_caster_su = FOURTH.eg_fresh_caster_su(unit)",
    T * 5 + "FOURTH.cast_target = best_enemy",
    T * 5 + "if best_arm == \"melee\" then",
    T * 6 + "reason = \"enemy in melee (targeting \" .. etype .. \")\"",
    T * 5 + "else",
    T * 6 + "reason = \"enemy under missile fire (targeting \" .. etype .. \")\"",
    T * 5 + "end",
    T * 4 + "end",
    T * 3 + "end",
    T * 2 + "end",
    T + "end",
    T + "return reason",
    "end")

LIVE_EV_NEW = L(
    "-- THE SHARED ENEMY PICKER (Class A, harness 97): fire when an ENEMY unit in",
    "-- range is in melee OR under missile fire. Used by BOTH enemy triggers - the",
    "-- unit form (ground = false) and the enemy-GROUND area form (ground = true).",
    "-- The chosen enemy rides FOURTH.cast_target (the CAST TARGET) and",
    "-- FOURTH.eg_enemy (the pre-cast re-check slot) - the owner is NEVER the target.",
    "-- Returns the ATTEMPT reason string, or nil when nothing qualifies.",
    "function FOURTH.eg_pick_enemy(unit, routing, ground)",
    T + "local reason = nil",
    T + "local marker = FOURTH.eg_marker or \"accusation\"",
    T + "local bound = FOURTH.eg_range_m or FOURTH.ACCUSATION_RANGE_M",
    T + "FOURTH.eg_ground = ground",
    T + "if not routing then",
    T * 2 + "local ok_coll, coll = pcall(function()",
    T * 3 + "return bm:get_scriptunits_for_main_enemy_army_to_local_player()",
    T * 2 + "end)",
    T * 2 + "if ok_coll and coll ~= nil then",
    T * 3 + "local ok_n, n = pcall(function() return coll:count() end)",
    T * 3 + "if ok_n and type(n) == \"number\" then",
    T * 4 + "local best_enemy, best_gap, best_arm = nil, nil, nil",
    T * 4 + "for i = 1, n do",
    T * 5 + "local ok_su, su = pcall(function() return coll:item(i) end)",
    T * 5 + "if ok_su and su ~= nil then",
    T * 6 + "local enemy = nil",
    T * 6 + "pcall(function() enemy = su.unit end)",
    T * 6 + "if enemy ~= nil then",
    T * 7 + "local ok_alive, alive = pcall(function() return enemy:number_of_men_alive() end)",
    T * 7 + "local valid = FOURTH.eg_enemy_valid(enemy)",
    T * 7 + "local ok_melee, melee = pcall(function() return enemy:is_in_melee() end)",
    T * 7 + "local arm = nil",
    T * 7 + "if ok_melee and melee == true then",
    T * 8 + "arm = \"melee\"",
    T * 7 + "elseif FOURTH.eg_under_missile_attack(enemy) then",
    T * 8 + "arm = \"missile\"",
    T * 7 + "end",
    T * 7 + "if arm ~= nil",
    T * 8 + "and ok_alive and type(alive) == \"number\" and alive > 0",
    T * 8 + "and (valid == nil or valid == true)",
    T * 8 + "and FOURTH.eg_enemy_within_bound(unit, enemy) then",
    T * 8 + "local gap = FOURTH.eg_enemy_gap(unit, enemy)",
    T * 8 + "if best_enemy == nil",
    T * 9 + "or (arm == \"melee\" and best_arm ~= \"melee\")",
    T * 9 + "or (arm == best_arm and gap ~= nil and (best_gap == nil or gap < best_gap)) then",
    T * 9 + "best_enemy, best_gap, best_arm = enemy, gap, arm",
    T * 8 + "end",
    T * 7 + "end",
    T * 6 + "end",
    T * 5 + "end",
    T * 4 + "end",
    T * 4 + "if best_enemy ~= nil then",
    T * 5 + "local etype = \"enemy\"",
    T * 5 + "pcall(function() etype = tostring(best_enemy:type()) end)",
    T * 5 + "log(\"  \" .. marker .. \" target: '\" .. etype .. \"' is the chosen enemy (\" .. tostring(best_arm)",
    T * 6 + ".. \") distance=\" .. ((best_gap ~= nil) and string.format(\"%.1f\", best_gap) or \"?\")",
    T * 6 + ".. \"m bound=\" .. tostring(bound) .. \"m\")",
    T * 5 + "FOURTH.eg_enemy = best_enemy",
    T * 5 + "FOURTH.eg_arm = best_arm",
    T * 5 + "FOURTH.eg_caster_su = FOURTH.eg_fresh_caster_su(unit)",
    T * 5 + "FOURTH.cast_target = best_enemy",
    T * 5 + "if ground then",
    T * 6 + "if best_arm == \"melee\" then",
    T * 7 + "reason = \"enemy-ground area in melee (targeting \" .. etype .. \")\"",
    T * 6 + "else",
    T * 7 + "reason = \"enemy-ground area under missile fire (targeting \" .. etype .. \")\"",
    T * 6 + "end",
    T * 5 + "else",
    T * 6 + "if best_arm == \"melee\" then",
    T * 7 + "reason = \"enemy in melee (targeting \" .. etype .. \")\"",
    T * 6 + "else",
    T * 7 + "reason = \"enemy under missile fire (targeting \" .. etype .. \")\"",
    T * 6 + "end",
    T * 5 + "end",
    T * 4 + "end",
    T * 3 + "end",
    T * 2 + "end",
    T + "end",
    T + "return reason",
    "end",
    "",
    "-- THE UNIT-FORM EVALUATOR: the FIRST ENEMY-TARGETED trigger - an enemy UNIT",
    "-- is the cast target.",
    "function FOURTH.evaluate_enemy_engaged_or_shot(unit, routing)",
    T + "return FOURTH.eg_pick_enemy(unit, routing, false)",
    "end",
    "",
    "-- THE ENEMY-GROUND AREA EVALUATOR (Class A): the same pick, but the cast is",
    "-- PLACED ON THE CHOSEN ENEMY'S GROUND (perform_special_ability_ground with the",
    "-- enemy's own position) instead of aimed at the enemy unit.",
    "function FOURTH.evaluate_enemy_ground_area(unit, routing)",
    T + "return FOURTH.eg_pick_enemy(unit, routing, true)",
    "end")
live = sub(live, LIVE_EV_OLD, LIVE_EV_NEW, "live evaluator")

ANN_EV_OLD = L(
    "-- THE EVALUATOR: fire when an ENEMY unit in range is in melee OR under missile",
    "-- fire; the chosen enemy is the CAST TARGET (never the owner). true = fire.",
    "function FOURTH.evaluate_enemy_engaged_or_shot(unit, routing)",
    T + "if not routing then",
    T * 2 + "local ok_coll, coll = pcall(function()",
    T * 3 + "return bm:get_scriptunits_for_main_enemy_army_to_local_player()",
    T * 2 + "end)",
    T * 2 + "if ok_coll and coll ~= nil then",
    T * 3 + "local ok_n, n = pcall(function() return coll:count() end)",
    T * 3 + "if ok_n and type(n) == \"number\" then",
    T * 4 + "local best_enemy, best_gap, best_arm = nil, nil, nil",
    T * 4 + "for i = 1, n do",
    T * 5 + "local ok_su, su = pcall(function() return coll:item(i) end)",
    T * 5 + "if ok_su and su ~= nil then",
    T * 6 + "local enemy = nil",
    T * 6 + "pcall(function() enemy = su.unit end)",
    T * 6 + "if enemy ~= nil then",
    T * 7 + "local ok_alive, alive = pcall(function() return enemy:number_of_men_alive() end)",
    T * 7 + "local valid = FOURTH.eg_enemy_valid(enemy)",
    T * 7 + "local ok_melee, melee = pcall(function() return enemy:is_in_melee() end)",
    T * 7 + "local arm = nil",
    T * 7 + "if ok_melee and melee == true then",
    T * 8 + "arm = \"melee\"",
    T * 7 + "elseif FOURTH.eg_under_missile_attack(enemy) then",
    T * 8 + "arm = \"missile\"",
    T * 7 + "end",
    T * 7 + "if arm ~= nil",
    T * 8 + "and ok_alive and type(alive) == \"number\" and alive > 0",
    T * 8 + "and (valid == nil or valid == true)",
    T * 8 + "and FOURTH.eg_enemy_within_bound(unit, enemy) then",
    T * 8 + "local gap = FOURTH.eg_enemy_gap(unit, enemy)",
    T * 8 + "if best_enemy == nil",
    T * 9 + "or (arm == \"melee\" and best_arm ~= \"melee\")",
    T * 9 + "or (arm == best_arm and gap ~= nil and (best_gap == nil or gap < best_gap)) then",
    T * 9 + "best_enemy, best_gap, best_arm = enemy, gap, arm",
    T * 8 + "end",
    T * 7 + "end",
    T * 6 + "end",
    T * 5 + "end",
    T * 4 + "end",
    T * 4 + "if best_enemy ~= nil then",
    T * 5 + "FOURTH.eg_enemy = best_enemy",
    T * 5 + "FOURTH.eg_arm = best_arm",
    T * 5 + "FOURTH.eg_caster_su = FOURTH.eg_fresh_caster_su(unit)",
    T * 5 + "FOURTH.cast_target = best_enemy",
    T * 5 + "return true",
    T * 4 + "end",
    T * 3 + "end",
    T * 2 + "end",
    T + "end",
    T + "return false",
    "end")
ANN_EV_NEW = L(
    "-- THE SHARED ENEMY PICKER (Class A, harness 97): an ENEMY unit in range that",
    "-- is in melee OR under missile fire; the chosen enemy is the CAST TARGET",
    "-- (never the owner). ground = true selects the enemy-GROUND area form. true =",
    "-- fire. The bound is the CURRENT ability's 70% constant (FOURTH.eg_range_m).",
    "function FOURTH.eg_pick_enemy(unit, routing, ground)",
    T + "FOURTH.eg_ground = ground",
    T + "if not routing then",
    T * 2 + "local ok_coll, coll = pcall(function()",
    T * 3 + "return bm:get_scriptunits_for_main_enemy_army_to_local_player()",
    T * 2 + "end)",
    T * 2 + "if ok_coll and coll ~= nil then",
    T * 3 + "local ok_n, n = pcall(function() return coll:count() end)",
    T * 3 + "if ok_n and type(n) == \"number\" then",
    T * 4 + "local best_enemy, best_gap, best_arm = nil, nil, nil",
    T * 4 + "for i = 1, n do",
    T * 5 + "local ok_su, su = pcall(function() return coll:item(i) end)",
    T * 5 + "if ok_su and su ~= nil then",
    T * 6 + "local enemy = nil",
    T * 6 + "pcall(function() enemy = su.unit end)",
    T * 6 + "if enemy ~= nil then",
    T * 7 + "local ok_alive, alive = pcall(function() return enemy:number_of_men_alive() end)",
    T * 7 + "local valid = FOURTH.eg_enemy_valid(enemy)",
    T * 7 + "local ok_melee, melee = pcall(function() return enemy:is_in_melee() end)",
    T * 7 + "local arm = nil",
    T * 7 + "if ok_melee and melee == true then",
    T * 8 + "arm = \"melee\"",
    T * 7 + "elseif FOURTH.eg_under_missile_attack(enemy) then",
    T * 8 + "arm = \"missile\"",
    T * 7 + "end",
    T * 7 + "if arm ~= nil",
    T * 8 + "and ok_alive and type(alive) == \"number\" and alive > 0",
    T * 8 + "and (valid == nil or valid == true)",
    T * 8 + "and FOURTH.eg_enemy_within_bound(unit, enemy) then",
    T * 8 + "local gap = FOURTH.eg_enemy_gap(unit, enemy)",
    T * 8 + "if best_enemy == nil",
    T * 9 + "or (arm == \"melee\" and best_arm ~= \"melee\")",
    T * 9 + "or (arm == best_arm and gap ~= nil and (best_gap == nil or gap < best_gap)) then",
    T * 9 + "best_enemy, best_gap, best_arm = enemy, gap, arm",
    T * 8 + "end",
    T * 7 + "end",
    T * 6 + "end",
    T * 5 + "end",
    T * 4 + "end",
    T * 4 + "if best_enemy ~= nil then",
    T * 5 + "FOURTH.eg_enemy = best_enemy",
    T * 5 + "FOURTH.eg_arm = best_arm",
    T * 5 + "FOURTH.eg_caster_su = FOURTH.eg_fresh_caster_su(unit)",
    T * 5 + "FOURTH.cast_target = best_enemy",
    T * 5 + "return true",
    T * 4 + "end",
    T * 3 + "end",
    T * 2 + "end",
    T + "end",
    T + "return false",
    "end",
    "",
    "-- THE UNIT-FORM trigger: an enemy UNIT is the cast target.",
    "function FOURTH.evaluate_enemy_engaged_or_shot(unit, routing)",
    T + "return FOURTH.eg_pick_enemy(unit, routing, false)",
    "end",
    "",
    "-- THE ENEMY-GROUND AREA trigger: the cast is placed on the chosen enemy's",
    "-- ground (perform_special_ability_ground with the enemy's own position).",
    "function FOURTH.evaluate_enemy_ground_area(unit, routing)",
    T + "return FOURTH.eg_pick_enemy(unit, routing, true)",
    "end")
ann = sub(ann, ANN_EV_OLD, ANN_EV_NEW, "ann evaluator")

# ===========================================================================
# evaluators map + TRIGGER_TIP (both files)
# ===========================================================================
MAP_OLD = L(
    T + "-- ACCUSATION (this round): the FIRST ENEMY-TARGETED trigger.",
    T + "enemy_engaged_or_shot = FOURTH.evaluate_enemy_engaged_or_shot,",
    "}")
MAP_NEW = L(
    T + "-- ACCUSATION (this round): the FIRST ENEMY-TARGETED trigger.",
    T + "enemy_engaged_or_shot = FOURTH.evaluate_enemy_engaged_or_shot,",
    T + "-- CLASS A (harness 97): the rest of the enemy-aimed casts - the unit form",
    T + "-- (shared with Accusation) and the enemy-GROUND area form.",
    T + "enemy_ground_area = FOURTH.evaluate_enemy_ground_area,",
    "}")
live = sub(live, MAP_OLD, MAP_NEW, "live evaluators")
ann  = sub(ann,  MAP_OLD, MAP_NEW, "ann evaluators")

TIP_OLD = L(
    T + "enemy_engaged_or_shot = \"When armed, fires when an enemy unit in range is in melee or under missile fire\",",
    "}")
TIP_NEW = L(
    T + "enemy_engaged_or_shot = \"When armed, fires when an enemy unit in range is in melee or under missile fire\",",
    T + "enemy_ground_area = \"When armed, fires when an enemy in range is in melee or under missile fire and the area hex is placed on its ground\",",
    "}")
live = sub(live, TIP_OLD, TIP_NEW, "live tips")
ann  = sub(ann,  TIP_OLD, TIP_NEW, "ann tips")

# ===========================================================================
# attempt_activation: generalize the enemy re-check + add the enemy-ground branch
# ===========================================================================
LIVE_RC_OLD = L(
    T + "-- ACCUSATION ENEMY RE-CHECK (harness 96): the enemy trigger chose an ENEMY",
    T + "-- unit and left it in FOURTH.eg_enemy (the cast target is the same unit,",
    T + "-- in FOURTH.cast_target); RE-READ the condition NOW, immediately before the",
    T + "-- cast - the enemy must still be ALIVE and still IN MELEE or UNDER FIRE and",
    T + "-- still within the 70% bound, which is RE-READ here via the engine's",
    T + "-- `unit:unit_distance(enemy)` (EDGE-TO-EDGE metres, battle_unit.lua:160) and",
    T + "-- whose REAL value is logged. If it lapsed the cast is wasted, so SKIP it",
    T + "-- rather than spend it. The chosen enemy is the CAST TARGET - NEVER the",
    T + "-- owner.",
    T + "if FOURTH.eg_enemy ~= nil then",
    T * 2 + "local enemy = FOURTH.eg_enemy",
    T * 2 + "local ok_alive, alive = pcall(function() return enemy:number_of_men_alive() end)",
    T * 2 + "local ok_melee, melee = pcall(function() return enemy:is_in_melee() end)",
    T * 2 + "local still_melee = (ok_melee and melee == true)",
    T * 2 + "local still_shot = false",
    T * 2 + "if not still_melee then",
    T * 3 + "still_shot = FOURTH.eg_under_missile_attack(enemy)",
    T * 2 + "end",
    T * 2 + "local alive_now = (ok_alive and type(alive) == \"number\" and alive > 0)",
    T * 2 + "-- RE-READ the bound NOW via the engine's edge-to-edge distance and log",
    T * 2 + "-- its REAL value (the same primitive the offer test used).",
    T * 2 + "local gap_now = FOURTH.eg_enemy_gap(unit, enemy)",
    T * 2 + "local in_bound_now = (gap_now ~= nil and gap_now <= FOURTH.ACCUSATION_RANGE_M)",
    T * 2 + "if not alive_now or not (still_melee or still_shot) or not in_bound_now then",
    T * 3 + "log(\"  accusation SKIPPED: the chosen enemy lapsed before the cast\"",
    T * 4 + ".. \" (alive=\" .. tostring(alive_now) .. \" melee=\" .. tostring(still_melee)",
    T * 4 + ".. \" shot=\" .. tostring(still_shot)",
    T * 4 + ".. ((gap_now ~= nil) and (\" distance=\" .. string.format(\"%.1f\", gap_now) .. \"m\") or \" distance=?\")",
    T * 4 + ".. \" bound=\" .. tostring(FOURTH.ACCUSATION_RANGE_M) .. \"m) - cast not spent\")",
    T * 3 + "FOURTH.eg_enemy = nil",
    T * 3 + "FOURTH.eg_arm = nil",
    T * 3 + "if RELEASE_CONTROL_AFTER and took_control then",
    T * 4 + "local ok_release, err_release = pcall(function() uc:release_control() end)",
    T * 4 + "log(\"  release_control         : ok=\" .. tostring(ok_release)",
    T * 5 + ".. (ok_release and \"\" or (\"  ERROR: \" .. tostring(err_release))))",
    T * 3 + "end",
    T * 3 + "return \"held\"",
    T * 2 + "end",
    T * 2 + "log(\"  accusation pre-cast re-check: target still engaged (\" .. tostring(FOURTH.eg_arm)",
    T * 3 + ".. \", melee=\" .. tostring(still_melee) .. \" shot=\" .. tostring(still_shot)",
    T * 3 + ".. \", distance=\" .. ((gap_now ~= nil) and string.format(\"%.1f\", gap_now) or \"?\")",
    T * 3 + ".. \"m bound=\" .. tostring(FOURTH.ACCUSATION_RANGE_M) .. \"m) - firing\")",
    T + "end")
assert live.count(LIVE_RC_OLD) == 1, "live recheck block not found exactly once"
LIVE_RC_NEW = LIVE_RC_OLD \
    .replace(
        T + "if FOURTH.eg_enemy ~= nil then" + NL + T * 2 + "local enemy = FOURTH.eg_enemy",
        T + "if FOURTH.eg_enemy ~= nil then" + NL + T * 2 + "local enemy = FOURTH.eg_enemy" + NL
        + T * 2 + "local eg_marker_now = FOURTH.eg_marker or \"accusation\"" + NL
        + T * 2 + "local eg_bound_now = FOURTH.eg_range_m or FOURTH.ACCUSATION_RANGE_M", 1) \
    .replace(
        T * 2 + "local in_bound_now = (gap_now ~= nil and gap_now <= FOURTH.ACCUSATION_RANGE_M)",
        T * 2 + "local in_bound_now = (gap_now ~= nil and gap_now <= eg_bound_now)", 1) \
    .replace(
        T * 3 + "log(\"  accusation SKIPPED: the chosen enemy lapsed before the cast\"",
        T * 3 + "log(\"  \" .. eg_marker_now .. \" SKIPPED: the chosen enemy lapsed before the cast\"", 1) \
    .replace(
        T * 4 + ".. \" bound=\" .. tostring(FOURTH.ACCUSATION_RANGE_M) .. \"m) - cast not spent\")",
        T * 4 + ".. \" bound=\" .. tostring(eg_bound_now) .. \"m) - cast not spent\")", 1) \
    .replace(
        T * 2 + "log(\"  accusation pre-cast re-check: target still engaged (\" .. tostring(FOURTH.eg_arm)",
        T * 2 + "log(\"  \" .. eg_marker_now .. \" pre-cast re-check: target still engaged (\" .. tostring(FOURTH.eg_arm)", 1) \
    .replace(
        T * 3 + ".. \"m bound=\" .. tostring(FOURTH.ACCUSATION_RANGE_M) .. \"m) - firing\")",
        T * 3 + ".. \"m bound=\" .. tostring(eg_bound_now) .. \"m) - firing\")", 1)
assert "eg_marker_now" in LIVE_RC_NEW and "eg_bound_now" in LIVE_RC_NEW
# refresh the RE-CHECK header comment to name the general shape
LIVE_RC_NEW = LIVE_RC_NEW.replace(
    T + "-- ACCUSATION ENEMY RE-CHECK (harness 96): the enemy trigger chose an ENEMY",
    T + "-- ENEMY-TARGETED RE-CHECK (Class A, harness 97): the enemy trigger chose an",
    1)
live = sub(live, LIVE_RC_OLD, LIVE_RC_NEW, "live recheck")

ANN_RC_OLD = L(
    T + "-- ACCUSATION ENEMY RE-CHECK (harness 96): re-read the chosen enemy's",
    T + "-- condition immediately before the cast - it must still be ALIVE and still",
    T + "-- IN MELEE or UNDER FIRE and still WITHIN the 70% bound (re-read here via",
    T + "-- the engine's `unit:unit_distance(enemy)`, EDGE-TO-EDGE metres,",
    T + "-- battle_unit.lua:160), or the cast is SKIPPED. The chosen enemy is the CAST",
    T + "-- TARGET - never the owner.",
    T + "if FOURTH.eg_enemy ~= nil then",
    T * 2 + "local enemy = FOURTH.eg_enemy",
    T * 2 + "local ok_alive, alive = pcall(function() return enemy:number_of_men_alive() end)",
    T * 2 + "local ok_melee, melee = pcall(function() return enemy:is_in_melee() end)",
    T * 2 + "local still_melee = (ok_melee and melee == true)",
    T * 2 + "local still_shot = false",
    T * 2 + "if not still_melee then",
    T * 3 + "still_shot = FOURTH.eg_under_missile_attack(enemy)",
    T * 2 + "end",
    T * 2 + "local alive_now = (ok_alive and type(alive) == \"number\" and alive > 0)",
    T * 2 + "local gap_now = FOURTH.eg_enemy_gap(unit, enemy)",
    T * 2 + "local in_bound_now = (gap_now ~= nil and gap_now <= FOURTH.ACCUSATION_RANGE_M)",
    T * 2 + "if not alive_now or not (still_melee or still_shot) or not in_bound_now then",
    T * 3 + "FOURTH.eg_enemy = nil",
    T * 3 + "FOURTH.eg_arm = nil",
    T * 3 + "if RELEASE_CONTROL_AFTER and took_control then",
    T * 4 + "pcall(function() uc:release_control() end)",
    T * 3 + "end",
    T * 3 + "return \"held\"",
    T * 2 + "end",
    T + "end")
assert ann.count(ANN_RC_OLD) == 1, "ann recheck block not found exactly once"
ANN_RC_NEW = ANN_RC_OLD.replace(
    T * 2 + "local gap_now = FOURTH.eg_enemy_gap(unit, enemy)",
    T * 2 + "local gap_now = FOURTH.eg_enemy_gap(unit, enemy)" + NL
    + T * 2 + "local eg_bound_now = FOURTH.eg_range_m or FOURTH.ACCUSATION_RANGE_M", 1).replace(
    T * 2 + "local in_bound_now = (gap_now ~= nil and gap_now <= FOURTH.ACCUSATION_RANGE_M)",
    T * 2 + "local in_bound_now = (gap_now ~= nil and gap_now <= eg_bound_now)", 1)
ann = sub(ann, ANN_RC_OLD, ANN_RC_NEW, "ann recheck")

# --- the enemy-ground cast branch -----------------------------------------
LIVE_CALL_OLD = L(
    T + "local ok_call, err_call, no_target",
    T + "if FOURTH.is_ground_key(ability_key) then",
    T * 2 + "ok_call, err_call, no_target = FOURTH.ground_cast(uc, unit, ability_key)",
    T * 2 + "if not quiet then",
    T * 3 + "log(\"  ground cast            : perform_special_ability_ground('\"",
    T * 4 + ".. tostring(ability_key) .. \"', <the unit's own position vector>) - the targeted form\")",
    T * 2 + "end",
    T + "else")
_ELSE_TAIL = NL + T + "else"
assert LIVE_CALL_OLD.endswith(_ELSE_TAIL), "live call head does not end with else"
LIVE_CALL_NEW = LIVE_CALL_OLD[:-len(_ELSE_TAIL)] + NL + L(
    T + "elseif FOURTH.enemy_ground_keys[ability_key] == true then",
    T * 2 + "-- ENEMY-GROUND AREA (Class A, harness 97): the cast is PLACED ON THE",
    T * 2 + "-- CHOSEN ENEMY'S GROUND. The controller is the FRESH one (uc above); the",
    T * 2 + "-- position is the enemy's own. NO enemy chosen -> FAIL-CLOSED (never a",
    T * 2 + "-- guessed or self target).",
    T * 2 + "if FOURTH.eg_enemy == nil then",
    T * 3 + "if not quiet then",
    T * 4 + "log(\"  enemy-ground cast SKIPPED: no enemy was chosen - not firing on a guessed target (fail-closed)\")",
    T * 3 + "end",
    T * 3 + "if RELEASE_CONTROL_AFTER and took_control then",
    T * 4 + "pcall(function() uc:release_control() end)",
    T * 3 + "end",
    T * 3 + "return \"held\"",
    T * 2 + "end",
    T * 2 + "ok_call, err_call, no_target = FOURTH.enemy_ground_cast(uc, FOURTH.eg_enemy, ability_key)",
    T * 2 + "if not quiet then",
    T * 3 + "log(\"  enemy-ground cast      : perform_special_ability_ground('\"",
    T * 4 + ".. tostring(ability_key) .. \"', <the chosen ENEMY's position vector>) - the enemy-ground form\")",
    T * 2 + "end") + _ELSE_TAIL
live = sub(live, LIVE_CALL_OLD, LIVE_CALL_NEW, "live ground branch")

ANN_CALL_OLD = L(
    T + "local ok_call, err_call, no_target",
    T + "if FOURTH.is_ground_key(ability_key) then",
    T * 2 + "ok_call, err_call, no_target = FOURTH.ground_cast(uc, unit, ability_key)",
    T + "else")
assert ANN_CALL_OLD.endswith(_ELSE_TAIL), "ann call head does not end with else"
ANN_CALL_NEW = ANN_CALL_OLD[:-len(_ELSE_TAIL)] + NL + L(
    T + "elseif FOURTH.enemy_ground_keys[ability_key] == true then",
    T * 2 + "-- ENEMY-GROUND AREA (Class A): the cast is placed on the CHOSEN ENEMY's",
    T * 2 + "-- ground; no enemy chosen -> fail-closed.",
    T * 2 + "if FOURTH.eg_enemy == nil then",
    T * 3 + "if RELEASE_CONTROL_AFTER and took_control then",
    T * 4 + "pcall(function() uc:release_control() end)",
    T * 3 + "end",
    T * 3 + "return \"held\"",
    T * 2 + "end",
    T * 2 + "ok_call, err_call, no_target = FOURTH.enemy_ground_cast(uc, FOURTH.eg_enemy, ability_key)") + _ELSE_TAIL
ann = sub(ann, ANN_CALL_OLD, ANN_CALL_NEW, "ann ground branch")

# ===========================================================================
# poll loop: set the current ability's bound + marker before every evaluate
# ===========================================================================
POLL_OLD = L(
    T * 5 + "FOURTH.eg_enemy = nil",
    T * 5 + "FOURTH.eg_caster_su = nil",
    T * 5 + "local reason = ability.evaluate(unit, routing)")
POLL_NEW = L(
    T * 5 + "FOURTH.eg_enemy = nil",
    T * 5 + "FOURTH.eg_arm = nil",
    T * 5 + "FOURTH.eg_caster_su = nil",
    T * 5 + "FOURTH.eg_ground = nil",
    T * 5 + "-- CLASS A (harness 97): the CURRENT ability's own 70% enemy-cast bound and",
    T * 5 + "-- its marker, so the shared enemy picker tests and logs against THIS entry's",
    T * 5 + "FOURTH.eg_range_m = ability.range_m",
    T * 5 + "FOURTH.eg_marker = ability.marker",
    T * 5 + "local reason = ability.evaluate(unit, routing)")
live = sub(live, POLL_OLD, POLL_NEW, "live poll slots")

ANN_POLL_OLD = L(
    T * 5 + "FOURTH.eg_enemy = nil",
    T * 5 + "FOURTH.eg_caster_su = nil",
    T * 5 + "local want_fire = ability.evaluate(unit, routing)")
ANN_POLL_NEW = L(
    T * 5 + "FOURTH.eg_enemy = nil",
    T * 5 + "FOURTH.eg_arm = nil",
    T * 5 + "FOURTH.eg_caster_su = nil",
    T * 5 + "FOURTH.eg_ground = nil",
    T * 5 + "-- CLASS A (harness 97): the CURRENT ability's own 70% enemy-cast bound and",
    T * 5 + "-- its marker, so the shared enemy picker tests and logs against THIS entry's",
    T * 5 + "FOURTH.eg_range_m = ability.range_m",
    T * 5 + "FOURTH.eg_marker = ability.marker",
    T * 5 + "local want_fire = ability.evaluate(unit, routing)")
ann = sub(ann, ANN_POLL_OLD, ANN_POLL_NEW, "ann poll slots")

# ===========================================================================
# THE 97 ENTRIES: move the trigger + add the per-entry 70% constant field
# ===========================================================================
def edit_entries(text, label):
    for p in plan:
        m = p['marker']; real = p['real']; trig = p['trigger']
        pat = re.compile(
            r'(\t\{ marker = "' + re.escape(m) + r'", name = "[^"]*", trigger = )'
            r'"melee_unwavering"(,\n\t\tbadge = "zz_auto_badge_[^"]*",\n\t\tkeys = \{[^}]*\},\n)'
            r'(\t\tox = 0, oy = 0 \},)')
        new = (r'\1"' + trig + r'"\2\t\trange_real = ' + str(real) + r',\n\3')
        text, n = pat.subn(new, text)
        assert n == 1, "%s entry %s: %d matches (want 1)" % (label, m, n)
    return text
live = edit_entries(live, "live")
ann  = edit_entries(ann,  "ann")

# Accusation's own entry gains the same per-ability real-range field (75 -> R75)
ACC_ENT_OLD = L(
    T + '{ marker = "accusation", name = "Accusation", trigger = "enemy_engaged_or_shot",',
    T * 2 + 'badge = "zz_auto_badge_accusation",',
    T * 2 + 'keys = { "wh_main_hero_abilities_accusation" },',
    T * 2 + "ox = 0, oy = 0 },")
ACC_ENT_NEW = L(
    T + '{ marker = "accusation", name = "Accusation", trigger = "enemy_engaged_or_shot",',
    T * 2 + 'badge = "zz_auto_badge_accusation",',
    T * 2 + 'keys = { "wh_main_hero_abilities_accusation" },',
    T * 2 + "range_real = 75,",
    T * 2 + "ox = 0, oy = 0 },")
live = sub(live, ACC_ENT_OLD, ACC_ENT_NEW, "live accusation range_real")
ann  = sub(ann,  ACC_ENT_OLD, ACC_ENT_NEW, "ann accusation range_real")

# the load loop maps each entry's REAL range to its named 70% bound
LOAD_OLD = L(
    "for _, ability in ipairs(ABILITIES) do",
    T + "ability.evaluate = FOURTH.evaluators[ability.trigger]",
    T + "ability.tip = FOURTH.TRIGGER_TIP[ability.trigger]",
    "end")
LOAD_NEW = L(
    "for _, ability in ipairs(ABILITIES) do",
    T + "ability.evaluate = FOURTH.evaluators[ability.trigger]",
    T + "ability.tip = FOURTH.TRIGGER_TIP[ability.trigger]",
    T + "-- CLASS A (harness 97): an entry's REAL target_intercept_range (range_real)",
    T + "-- maps to its own named 70% bound (FOURTH.ENEMY_CAST). Entries without it",
    T + "-- (the self/ally triggers) leave range_m nil - never read for them.",
    T + "if ability.range_real ~= nil then",
    T * 2 + "ability.range_m = FOURTH.ENEMY_CAST[ability.range_real]",
    T + "end",
    "end")
live = sub(live, LOAD_OLD, LOAD_NEW, "live load loop")
ann  = sub(ann,  LOAD_OLD, LOAD_NEW, "ann load loop")

# ===========================================================================
# sanity
# ===========================================================================
for s, nm in ((live, "live"), (ann, "ann")):
    assert s.count(T + "{ marker = ") == 579, nm + ": table not 579 entries"
    assert s.count('trigger = "melee_unwavering"') == 383, nm + ": melee_unwavering not 383"
    assert s.count('trigger = "enemy_engaged_or_shot"') == 89, nm + ": unit trigger not 89 (88 batch + accusation)"
    assert s.count('trigger = "enemy_ground_area"') == 9, nm + ": ground trigger not 9"
    assert s.count(T + T + "range_real = ") == 98, nm + ": range_real fields not 98"
    assert s.count("ability.range_m = FOURTH.ENEMY_CAST[ability.range_real]") == 1, nm + ": load-loop map missing"
    assert "function FOURTH.eg_pick_enemy(unit, routing, ground)" in s, nm + ": picker missing"
    assert "function FOURTH.evaluate_enemy_ground_area(unit, routing)" in s, nm + ": ground eval missing"
    assert "enemy_ground_area = FOURTH.evaluate_enemy_ground_area," in s, nm + ": ground wired"
    assert "enemy_ground_area = \"When armed," in s, nm + ": ground tip missing"
    assert "function FOURTH.enemy_ground_cast(uc, enemy, ability_key)" in s, nm + ": ground helper missing"
    assert s.count("FOURTH.eg_enemy = nil") == 3, nm + ": eg_enemy=nil count moved"
    assert s.count("FOURTH.eg_caster_su = nil") == 2, nm + ": eg_caster_su=nil count moved"
    assert "unit_in_range(" not in s, nm + ": an engine unit_in_range call leaked back"
    assert s.count("FOURTH.ENEMY_CAST_R") == 24, nm + ": enemy-cast constant refs wrong"
    assert "FOURTH.RANGE_FRACTION = 0.70" in s
    assert s.count(chr(13)) == 0, nm + ": CRLF leaked"
assert "log(" not in ann, "annotated copy gained a log()"
assert "string.find" not in ann, "annotated copy gained a string.find()"

write(LIVE, live); write(ANN, ann)
print("wrote", LIVE, len(live)); print("wrote", ANN, len(ann))
print("OK: 97 Class-A entries moved (88 unit + 9 ground); 12 named 70% constants; per-ability bound.")
