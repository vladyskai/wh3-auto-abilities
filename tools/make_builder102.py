"""Clone build_and_install101.py into the summon round's builder and re-base its
content gates onto 642 entries / 682 keys + the round's new tokens."""
import os

REL = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases"
SRC = os.path.join(REL, "20261017_boss_gate_harness101", "build_and_install101.py")
DST_DIR = os.path.join(REL, "20261017_summon_harness102")
DST = os.path.join(DST_DIR, "build_and_install102.py")
GEN = os.path.join(os.path.expandvars(r"%LOCALAPPDATA%\Temp"), "gen")

import json
plan = json.load(open(os.path.join(GEN, "plan.json"), encoding="utf-8"))

s = open(SRC, encoding="utf-8").read()

def must(old, new, n=1, tag=""):
    global s
    c = s.count(old)
    assert c == n, "anchor %r hit %d (want %d) %s" % (old[:60], c, n, tag)
    s = s.replace(old, new)

DOC = '''
ROUND v102 (2026-10-17): THE SUMMON ROUND.
(A) THE REST OF THE SUMMON CLASS - every in-wheel, non-illusion,
    GROUND-CASTABLE `wh_type_summon_unit` row derived from the game's own data
    (spawned_unit set + type wh_type_summon_unit + spawn_is_decoy false +
    target_ground true + in-wheel + not boss-only + not implemented): 57 entries
    / 68 keys. They ride the PROVEN `enemy_ground_melee` trigger (Gate of
    Khorne's): the closest FIGHTING enemy inside the ability's own 70% bound,
    the summon placed on THAT ENEMY's ground. ONE of them (The Tallyman's
    Blades Upgraded) declares target_intercept_range = -1.0 - NO real range -
    so it carries `unbounded = true` and skips the distance test.
(D) THE NINE unlabelled real spawners (Beast Pack, Blacktoof's Conjuration,
    Call to Gwindalor, Lesser Raise Dead, Savage Dominion, Savage Predators,
    Tide of Death, Tide of Pox, Wake Da Idol): 9 entries / 9 keys on the same
    trigger and the same enemy-ground form.
(B) Nurgling Tide gets its OWN trigger `self_summon_melee` - the user's rule,
    verbatim: "that one should only trigger when the caster himself is in
    melee." Owner alive + not routing + is_in_melee() true; the cast goes on
    the OWNER through the unit form, with a freshly re-fetched caster
    controller, a hold and a pre-cast re-check of the same state. NO RANGE
    BOUND: a self cast has no distance to measure (its row has
    target_intercept_range = 0, no target flags at all, affect_self = true).
(E) Eye of Khorne is a FINISHER on the NEW `enemy_low_health_noncommander`
    trigger: any enemy inside its 70% bound (50 m -> 35 m) BELOW 20% HEALTH
    that is NOT a Lord or Hero; the LOWEST-health one wins (closest as the
    tiebreak). It casts through the UNIT form (target_enemies = true,
    target_ground = false).
(F) The Dreaded Thirteenth (FOUR keys, ONE entry) rides the NEW
    `enemy_melee_noncommander` trigger: the closest non-commander enemy in
    melee inside its 70% bound (100 m -> 70 m), placed on that enemy's ground.
(THE LORD/HERO TEST) FOURTH.commander_keys is DERIVED from the game's own
    class/caste columns: every land_units key whose `class` is "com" (the
    engine's commander class - its own invalid-target flags are named
    unit_is_commander_class / unit_is_not_commander_class) UNION every
    land_units key reached from a main_units row whose `caste` is "lord" or
    "hero" (which catches the six Krell variants still marked inf_mel). It is
    matched by EXACT WHOLE-KEY equality against battle_unit:type(); 
    battle_unit:unit_class() == "com" is the fallback; neither readable ->
    FAIL CLOSED (treated as a commander).
(C) THE FOUR ILLUSIONS stay EXCLUDED (spawn_is_decoy; engine-refused while
    engaged in melee) - none was ever in the mod, and the gate below proves all
    four keys are absent.
COUNTS: 573 -> 642 entries (573 + 69), 599 -> 682 keys (599 + 83);
    melee_unwavering stays 360, enemy_engaged_or_shot stays 86,
    enemy_ground_area stays 9, enemy_ground_melee 1 -> 67.
'''
must('import hashlib\n', '"""\n' + DOC + '"""\nimport hashlib\n', 1, "docstring")

s = s.replace('assert script_txt.count("\\t{ marker = ") == 573, "the abilities table is not 573 entries"',
              'assert script_txt.count("\\t{ marker = ") == 642, "the abilities table is not 642 entries"')

GATES = '''
# ---------------------------------------------------------------------------
# ROUND v102: THE SUMMON ROUND.
# ---------------------------------------------------------------------------
NURG = "wh3_main_lord_abilities_nurgling_tide"
EYE = "wh3_dlc26_lord_abilities_eye_of_khorne"
D13 = "wh3_dlc29_spell_bound_the_dreaded_thirteenth"
assert script_txt.count("\\t{ marker = ") == 642, "the abilities table is not 642 entries"
assert script_txt.count('trigger = "enemy_ground_melee"') == 67, \\
    "enemy_ground_melee is not 67 (1 gate + 57 A + 9 D)"
assert script_txt.count('trigger = "self_summon_melee"') == 1, "the self-summon trigger is missing"
assert script_txt.count('trigger = "enemy_low_health_noncommander"') == 1, "the finisher trigger is missing"
assert script_txt.count('trigger = "enemy_melee_noncommander"') == 1, "the D13 trigger is missing"
assert script_txt.count('trigger = "melee_unwavering"') == 360, "melee_unwavering moved"
assert script_txt.count('trigger = "enemy_engaged_or_shot"') == 86, "enemy_engaged_or_shot moved"
for _mk, _trig, _key in (
        ("nurgling_tide", "self_summon_melee", NURG),
        ("eye_of_khorne", "enemy_low_health_noncommander", EYE),
        ("the_dreaded_thirteenth", "enemy_melee_noncommander", D13),
        ("gate_of_nurgle", "enemy_ground_melee", "wh3_main_character_abilities_gate_of_nurgle"),
        ("beast_pack", "enemy_ground_melee", "wh2_dlc16_lord_abilities_beast_pack"),
        ("wake_da_idol", "enemy_ground_melee", "wh3_main_item_abilities_zak_aloooog")):
    assert 'marker = "%s"' % _mk in script_txt, "summon marker missing: " + _mk
    assert 'badge = "zz_auto_badge_%s"' % _mk in script_txt, "summon badge missing: " + _mk
    assert 'trigger = "%s"' % _trig in script_txt, "summon trigger missing: " + _trig
    assert '"%s"' % _key in script_txt, "summon key missing: " + _key
# every A/D/F key sits in the enemy-ground set (91 entries: 10 prior + 81 new)
_g0 = script_txt.find("enemy_ground_keys = {")
_g1 = script_txt.find("\\t},\\n", _g0)
assert _g0 > 0 and _g1 > _g0
assert script_txt[_g0:_g1].count('"] = true,') == 91, "enemy_ground_keys is not 91 entries"
for _k in ("wh2_dlc16_hero_abilities_tide_of_death", "wh2_dlc16_hero_abilities_tide_of_pox",
           "wh2_dlc15_item_abilities_blacktoofs_conjuration",
           "wh2_dlc16_spell_bound_vampires_lesser_raise_dead",
           "wh2_dlc17_spell_bound_savage_dominion",
           "wh3_dlc26_hero_abilities_savage_predators",
           "wh2_dlc16_lord_abilities_call_to_gwindalor",
           D13, D13 + "_1", D13 + "_thanquol", D13 + "_thanquol_1"):
    assert '["%s"] = true,' % _k in script_txt[_g0:_g1], "ground key missing from the set: " + _k
# the self-summon is NOT a ground key, and Eye of Khorne is NOT either
assert '["%s"] = true,' % NURG not in script_txt[_g0:_g1], "Nurgling Tide must not be a ground key"
assert EYE not in script_txt[_g0:_g1], "Eye of Khorne must not be an enemy-ground key"
# the four illusions stay out
for _k in ("wh2_dlc10_lord_abilities_deadly_mislead", "wh3_dlc24_lord_item_deceiving_shadows",
           "wh2_dlc14_unit_abilities_doppelgang", "wh2_dlc10_lord_abilities_mislead"):
    assert _k not in script_txt, "an illusion summon is in the mod: " + _k
# the commander test
assert "FOURTH.commander_keys = {" in script_txt, "the derived commander key set is missing"
_c0 = script_txt.find("FOURTH.commander_keys = {")
_c1 = script_txt.find("\\n}\\n", _c0)
assert script_txt[_c0:_c1].count('"] = true,') >= 1400, "the commander key set is too small"
assert '["wh3_main_kho_cha_skarbrand_0"] = true,' in script_txt[_c0:_c1], "a known Lord is missing"
assert '["wh2_dlc09_tmb_inf_skeleton_warriors_0"] = true,' not in script_txt[_c0:_c1], \\
    "a line unit is in the commander set"
assert "function FOURTH.enemy_is_commander(enemy)" in script_txt, "the commander test is missing"
assert "enemy:unit_class()" in script_txt, "the unit_class fallback is missing"
assert "FOURTH.HEALTH_LINE_PCT = 20" in script_txt, "the 20% finisher line is missing"
assert "hp < FOURTH.HEALTH_LINE_PCT" in script_txt, "the finisher is not strictly below the line"
assert script_txt.count("\\t\\trange_real = ") == 163, "range_real count is not 163"
assert script_txt.count("\\t\\tunbounded = true,") == 1, "the one unbounded entry is not flagged"
assert "FOURTH.eg_no_bound == true then return true end" in script_txt, "the no-bound test is missing"
assert "function FOURTH.evaluate_self_summon_melee(unit, routing)" in script_txt, "the self-summon evaluator is missing"
assert "function FOURTH.evaluate_enemy_low_health_noncommander(unit, routing)" in script_txt, "the finisher evaluator is missing"
assert "function FOURTH.evaluate_enemy_melee_noncommander(unit, routing)" in script_txt, "the D13 evaluator is missing"
assert "self_summon_melee = FOURTH.evaluate_self_summon_melee," in script_txt
assert "enemy_low_health_noncommander = FOURTH.evaluate_enemy_low_health_noncommander," in script_txt
assert "enemy_melee_noncommander = FOURTH.evaluate_enemy_melee_noncommander," in script_txt
assert 'self_summon_melee = "When armed, fires when this unit itself is fighting in melee' in script_txt
assert 'enemy_low_health_noncommander = "When armed, fires on the lowest-health enemy' in script_txt
assert 'enemy_melee_noncommander = "When armed, fires on the closest enemy' in script_txt
assert "SKIPPED: the caster left melee before the self cast" in script_txt
assert "pre-cast re-check: the caster is still in melee" in script_txt
assert "lowest-health non-commander enemy below" in script_txt
assert 'reason = "closest non-commander enemy in melee within bound (targeting "' in script_txt
assert "FOURTH.ss_self = nil" in script_txt and "FOURTH.eg_noncommander = nil" in script_txt
assert "FOURTH.ENEMY_CAST_R45  = 31" in script_txt and "FOURTH.ENEMY_CAST_R90  = 63" in script_txt
assert "unit_in_range(" not in script_txt, "a unit_in_range call is back"
assert "string.find(" not in script_txt, "a string.find call is back"

'''
anchor = "# HOUSEKEEPING 20261004: the two throwaway experiment probes were RETIRED from the"
assert s.count(anchor) == 1
s = s.replace(anchor, GATES + anchor)

open(DST_DIR + "/../20261017_summon_harness102/build_and_install102.py", "w", encoding="utf-8", newline="\n").write(s)
print("builder written:", len(s))
