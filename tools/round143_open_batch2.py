#!/usr/bin/env python3
"""Round 143 (harness 142): open batch 2 - the ground curses, Curse of Djaf, the Handmaidens' Soulblight, and the
summons / fanatic releases (9 entries / 11 keys).

User rulings 2026-11-13 (earlier status: auto-exclusions; the 2026-10 questionnaire only PROPOSED "when in melee: on
the ground under its target"):
  * The Curse of Anraheir (3 keys), Transmutation of Lead, Soulblight (Doomfire Warlocks), The Soulstealer:
    "Fighting enemy, all four" -> enemy_ground_melee;
  * Curse of Djaf: "Shooting enemy" -> NEW enemy_ground_shooting: on the ground under the closest enemy MISSILE unit
    that is shooting (the round-138 enemy ammunition read; target_class "missile");
  * Soulblight (Lahmian Handmaidens of Death, a self contact buff): "In melee" -> melee_unwavering;
  * Squig Thinkin', Spinning Loons, The Loons of Eight Peaks: "Fighting enemy, all three" -> enemy_ground_melee (the
    loons with target_class "not_flying"; 25 m -> the new ENEMY_CAST_R25 = 17).
Every enemy-ground key joins enemy_ground_keys; wind-ups (Soulblight 3 s / 1 s, Soulstealer 3 s, Transmutation 5 s)
join cast_gate.wind_up_s; multi-use keys join charge_gate.hold_s. No string.find. Every helper is a FOURTH field.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"


def sub(s, a, b):
    assert s.count(a) == 1, (a[:80], s.count(a))
    return s.replace(a, b)


def entry(marker, name, trig, keys, extra):
    k = ",\n\t\t\t".join('"%s"' % x for x in keys)
    lines = ['\t{ marker = "%s", name = "%s", trigger = "%s",' % (marker, name, trig),
             '\t\tbadge = "zz_auto_badge_%s",' % marker,
             "\t\tkeys = { %s }," % k]
    lines += ["\t\t%s," % e for e in extra]
    lines += ["\t\tox = 0, oy = 0 },"]
    return "\n".join(lines) + "\n"


ANR = ["wh2_dlc16_spell_bound_the_curse_of_anraheir", "wh3_main_spell_bound_the_curse_of_anraheir",
       "wh_dlc05_spell_bound_the_curse_of_anraheir"]
NEW_ENTRIES = (
    entry("curse_of_anraheir", "The Curse of Anraheir", "enemy_ground_melee", ANR, ["range_real = 200"])
    + entry("transmutation_of_lead", "Transmutation of Lead", "enemy_ground_melee",
            ["wh3_main_spell_bound_transmutation_of_lead"], ["range_real = 200"])
    + entry("soulblight", "Soulblight", "enemy_ground_melee", ["wh2_dlc10_spell_bound_soulblight"], ["range_real = 200"])
    + entry("the_soulstealer", "The Soulstealer", "enemy_ground_melee",
            ["wh3_dlc29_spell_bound_undeath_khizaar_the_soulstealer"], ["range_real = 100"])
    + entry("curse_of_djaf", "Curse of Djaf", "enemy_ground_shooting", ["wh2_dlc09_character_abilities_curse_of_djaf"],
            ["range_real = 100", 'target_class = "missile"'])
    + entry("soulblight_handmaidens", "Soulblight", "melee_unwavering", ["wh3_dlc29_spell_bound_soulblight"], [])
    + entry("squig_thinkin", "Squig Thinkin'", "enemy_ground_melee", ["wh3_dlc26_character_abilities_squig_thinkin"],
            ["range_real = 75"])
    + entry("spinning_loons", "Spinning Loons", "enemy_ground_melee", ["wh_main_unit_abilities_spinning_loons"],
            ["range_real = 25", 'target_class = "not_flying"'])
    + entry("loons_of_eight_peaks", "The Loons of Eight Peaks", "enemy_ground_melee",
            ["wh_dlc06_unit_abilities_the_loons_of_eight_peaks"], ["range_real = 25", 'target_class = "not_flying"']))
GROUND_KEYS = ANR + ["wh3_main_spell_bound_transmutation_of_lead", "wh2_dlc10_spell_bound_soulblight",
                     "wh3_dlc29_spell_bound_undeath_khizaar_the_soulstealer", "wh2_dlc09_character_abilities_curse_of_djaf",
                     "wh3_dlc26_character_abilities_squig_thinkin", "wh_main_unit_abilities_spinning_loons",
                     "wh_dlc06_unit_abilities_the_loons_of_eight_peaks"]
WIND = {"wh2_dlc10_spell_bound_soulblight": 3, "wh3_dlc29_spell_bound_soulblight": 1,
        "wh3_dlc29_spell_bound_undeath_khizaar_the_soulstealer": 3, "wh3_main_spell_bound_transmutation_of_lead": 5}
HOLD = {"wh2_dlc10_spell_bound_soulblight": 90, "wh3_dlc29_spell_bound_soulblight": 45,
        "wh_main_unit_abilities_spinning_loons": 30, "wh_dlc06_unit_abilities_the_loons_of_eight_peaks": 30}

RESTOCK = '\t{ marker = "restock", name = "Restock!", trigger = "ally_ammo_low",'
EGK_OLD = "enemy_ground_keys = {\n"
EGK_NEW = EGK_OLD + "\t\t-- ROUND 143: open batch 2 (placed on the chosen enemy's ground)\n" + "".join(
    '\t\t["%s"] = true,\n' % k for k in GROUND_KEYS)
WIND_OLD = "\twind_up_s = {\n"
WIND_NEW = WIND_OLD + "\t\t-- ROUND 143: open batch 2 wind-ups (unit_spec_abil wind_up_time)\n" + "".join(
    '\t\t["%s"] = %d,\n' % (k, v) for k, v in WIND.items())
HOLD_OLD = "\thold_s = {\n"
HOLD_NEW = HOLD_OLD + "\t\t-- ROUND 143: open batch 2 multi-use keys (recharge_time)\n" + "".join(
    '\t\t["%s"] = %d,\n' % (k, v) for k, v in HOLD.items())
R_OLD = "FOURTH.ENEMY_CAST_R20  = 14\n"
R_NEW = R_OLD + "FOURTH.ENEMY_CAST_R25  = 17   -- ROUND 143: the fanatic releases, 25 m -> floor(25 x 0.70)\n"
RM_OLD = "\t[150] = FOURTH.ENEMY_CAST_R150,\n"
RM_NEW = "\t[25]  = FOURTH.ENEMY_CAST_R25,\n" + RM_OLD

EVAL_LIVE = """-- ROUND 143: Curse of Djaf - the Missile Mirror pick (an enemy missile unit shooting, not in melee, inside the bound),
-- placed on that enemy's GROUND (the key is an enemy-ground key)
function FOURTH.evaluate_enemy_ground_shooting(unit, routing)
	local r = FOURTH.evaluate_enemy_missile_shooting(unit, routing)
	if r == nil then return nil end
	FOURTH.eg_ground = true
	return r .. " - on the ground under it"
end

"""
EVAL_ANN = """-- ROUND 143: Curse of Djaf - the Missile Mirror pick, placed on that enemy's GROUND
function FOURTH.evaluate_enemy_ground_shooting(unit, routing)
	if not FOURTH.evaluate_enemy_missile_shooting(unit, routing) then return false end
	FOURTH.eg_ground = true
	return true
end

"""
MAP_OLD = "\tself_moving = FOURTH.evaluate_self_moving,\n"
MAP_NEW = MAP_OLD + "\t-- ROUND 143\n\tenemy_ground_shooting = FOURTH.evaluate_enemy_ground_shooting,\n"
TIP_OLD = '\tself_moving = "When armed, fires when this unit is moving",\n'
TIP_NEW = TIP_OLD + '\tenemy_ground_shooting = "When armed, fires on the ground under the closest enemy missile unit in range that is shooting",\n'
ANCHOR = "FOURTH.evaluators = {\n"

for path, ev in ((SRC, EVAL_LIVE), (ANN, EVAL_ANN)):
    s = open(path, encoding="utf-8", newline="").read()
    assert "enemy_ground_shooting" not in s
    before = s.count("\t{ marker = ")
    s = sub(s, RESTOCK, NEW_ENTRIES + RESTOCK)
    s = sub(s, EGK_OLD, EGK_NEW)
    s = sub(s, WIND_OLD, WIND_NEW)
    s = sub(s, HOLD_OLD, HOLD_NEW)
    s = sub(s, R_OLD, R_NEW)
    s = sub(s, RM_OLD, RM_NEW)
    s = sub(s, MAP_OLD, MAP_NEW)
    s = sub(s, TIP_OLD, TIP_NEW)
    s = sub(s, ANCHOR, ev + ANCHOR)
    assert s.count("\t{ marker = ") == before + 9
    open(path, "w", encoding="utf-8", newline="").write(s)
    print(path, "entries", before, "->", before + 9)

import gen_recharge_keys as G  # noqa: E402
new_block = G.lua_block(G.derive())
pat = re.compile(r"-- GENERATED by tools/gen_recharge_keys\.py.*?\nFOURTH\.load_recharge\(\)\n", re.S)
for path in (SRC, ANN):
    s = open(path, encoding="utf-8", newline="").read()
    assert len(pat.findall(s)) == 1
    s = pat.sub(lambda m: new_block, s)
    open(path, "w", encoding="utf-8", newline="").write(s)
print("lock table re-derived:", len(G.derive()), "keys")
