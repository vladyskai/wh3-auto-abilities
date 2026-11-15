#!/usr/bin/env python3
"""Round 158 (harness 157): open batch 6 - the last 12 group B attacks (12 entries / 12 keys; 2 new families).

User rulings 2026-11-15 (earlier status "excluded (impossible: no enemy-unit read)", not user decisions):
  * the area drains (Blood Statuette of Spite, Darkened Mist, The Fate of Bjuna x2, Maelstrom of Change, Otherworldly
    Pestilence, Staff of Masks; the game's max_damaged_entities = 25 / 15): "Most valuable infantry" -> NEW
    enemy_area_drain: the visible enemy infantry in range with at least the ability's own model count left (GENERATED
    AREA table) and the highest live value per soldier; the caster standing still; no safety margin (a direct effect).
  * the slows: "Rule 10: melee or charge" -> enemy_melee_or_fast: Ethrac's Brazier, and Storm of the Night with the NEW
    class "flying" (the game's ground_unit rule: is_currently_flying() exactly true).
  * the morale hexes: "Horns melee, Trance waver" -> Preyton Horns on enemy_melee, The Amber Trance on enemy_wavering.
  * Dweomer Leach Orb (the game: spellcasters only; no read): "Lord/Hero proxy" -> NEW enemy_commander_value: the most
    valuable visible enemy Lord or Hero in range (target class commander).
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_shot_tables as GS  # noqa: E402

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"


def sub(s, a, b, n=1):
    assert s.count(a) == n, (a[:80], s.count(a))
    return s.replace(a, b)


def entry(marker, name, trig, key, extra):
    lines = ['\t{ marker = "%s", name = "%s", trigger = "%s",' % (marker, name, trig),
             '\t\tbadge = "zz_auto_badge_%s",' % marker,
             '\t\tkeys = { "%s" },' % key]
    lines += ["\t\t%s," % e for e in extra]
    lines += ["\t\tox = 0, oy = 0 },"]
    return "\n".join(lines) + "\n"


AD = "enemy_area_drain"
ROWS = [
    ("blood_statuette_of_spite", "Blood Statuette of Spite", AD, "wh2_main_item_abilities_blood_statuette_of_spite",
     ["range_real = 100"]),
    ("darkened_mist", "Darkened Mist", AD, "wh3_dlc23_item_abilities_darkened_mist", ["range_real = 30"]),
    ("fate_of_bjuna_dlc25", "The Fate of Bjuna", AD, "wh3_dlc25_spell_bound_the_fate_of_bjuna", ["range_real = 100"]),
    ("fate_of_bjuna", "The Fate of Bjuna", AD, "wh3_main_spell_bound_the_fate_of_bjuna", ["range_real = 100"]),
    ("maelstrom_of_change", "Maelstrom of Change", AD, "wh3_dlc24_unit_abilities_maelstrom_of_change",
     ["range_real = 200"]),
    ("otherworldly_pestilence", "Otherworldly Pestilence", AD, "wh3_dlc29_lord_abilities_otherworldly_pestilence",
     ["range_real = 100"]),
    ("staff_of_masks", "Staff of Masks", AD, "wh3_dlc27_item_abilities_staff_of_the_masque", ["range_real = 50"]),
    ("ethracs_brazier", "Ethrac's Brazier", "enemy_melee_or_fast", "wh3_dlc29_item_active_ethracs_brazier",
     ["range_real = 100"]),
    ("storm_of_the_night", "Storm of the Night", "enemy_melee_or_fast", "wh2_dlc11_lord_abilities_storm_of_the_night",
     ["range_real = 150", 'target_class = "flying"']),
    ("preyton_horns", "Preyton Horns", "enemy_melee", "wh3_dlc27_item_abilities_preyton_horns", ["range_real = 100"]),
    ("the_amber_trance", "The Amber Trance", "enemy_wavering", "wh2_dlc10_item_abilities_the_amber_trance",
     ["range_real = 100"]),
    ("dweomer_leach_orb", "Dweomer Leach Orb", "enemy_commander_value", "wh3_dlc23_item_abilities_dweomer_leach_orb",
     ["range_real = 200", 'target_class = "commander"']),
]
KEYS = [r[3] for r in ROWS]
AREA_KEYS = [r[3] for r in ROWS if r[2] == AD]
NEW_ENTRIES = "".join(entry(*r) for r in ROWS)
WIND = [("wh3_dlc23_item_abilities_darkened_mist", "3"), ("wh3_dlc25_spell_bound_the_fate_of_bjuna", "5"),
        ("wh3_main_spell_bound_the_fate_of_bjuna", "5"), ("wh3_dlc29_item_active_ethracs_brazier", "3")]
HOLD = [("wh2_main_item_abilities_blood_statuette_of_spite", 60), ("wh3_dlc23_item_abilities_darkened_mist", 120),
        ("wh3_dlc24_unit_abilities_maelstrom_of_change", 60), ("wh3_dlc27_item_abilities_staff_of_the_masque", 120),
        ("wh2_dlc11_lord_abilities_storm_of_the_night", 90)]

RESTOCK = '\t{ marker = "restock", name = "Restock!", trigger = "ally_ammo_low",'
WIND_OLD = "\twind_up_s = {\n"
WIND_NEW = WIND_OLD + "\t\t-- ROUND 158: the area drains' and Ethrac's Brazier's wind-ups (unit_spec_abil wind_up_time)\n" + "".join(
    '\t\t["%s"] = %s,\n' % (k, v) for k, v in WIND)
HOLD_OLD = "\thold_s = {\n"
HOLD_NEW = HOLD_OLD + "\t\t-- ROUND 158: the round-158 abilities with more than one use (recharge_time)\n" + "".join(
    '\t\t["%s"] = %d,\n' % (k, v) for k, v in HOLD)

FLY_OLD = ('\tif cls == "not_flying" then\n'
           '\t\tlocal ok_f, fly = pcall(function() return enemy:is_currently_flying() end)\n'
           '\t\treturn ok_f and fly == false\n'
           '\tend\n')
FLY_NEW = FLY_OLD + ('\t-- ROUND 158: Storm of the Night (the game\'s ground_unit rule: flying targets only) - read live; only an\n'
                     '\t-- exact true passes, an unreadable flight never qualifies\n'
                     '\tif cls == "flying" then\n'
                     '\t\tlocal ok_f, fly = pcall(function() return enemy:is_currently_flying() end)\n'
                     '\t\treturn ok_f and fly == true\n'
                     '\tend\n')
LIST_OLD = '\tif kind == "armour" or kind == "infantry" then list = m.enemies end\n'
LIST_NEW = '\tif kind == "armour" or kind == "infantry" or kind == "area" then list = m.enemies end   -- ROUND 158: area\n'
KIND_OLD = ('\t\telseif kind == "execute" then\n'
            '\t\t\tok_kind = FOURTH.exec_ok(e)\n'
            '\t\t\ts1 = e.value or 0\n')
KIND_NEW = KIND_OLD + ('\t\telseif kind == "area" then   -- ROUND 158: enough soldiers left for every strike\n'
                       '\t\t\tok_kind = (e.men >= FOURTH.area_min())\n'
                       '\t\t\ts1 = e.vps or 0\n'
                       '\t\telseif kind == "value" then   -- ROUND 158: any enemy the class allows, the most valuable\n'
                       '\t\t\ts1 = e.value or 0\n')
PICK_OLD = "-- ROUND 157: kinds \"drain\" (as \"single\") and \"execute\"; nosafe skips the safety test\n"
PICK_NEW = ('-- ROUND 158: the current entry\'s model count per tick (the GENERATED AREA table; 25 when unknown)\n'
            'function FOURTH.area_min()\n'
            '\tlocal key = FOURTH.rc_self_keys and FOURTH.rc_self_keys[1]\n'
            '\treturn (key and FOURTH.AREA_N[key]) or 25\n'
            'end\n\n' + PICK_OLD)
STILL_OLD = ('\tif kind == "drain" then\n'
             '\t\tif not FOURTH.blob_still(unit) then return false end   -- ROUND 157: standing still, melee allowed\n'
             '\telseif kind ~= "execute" then\n')
STILL_NEW = ('\tif kind == "drain" or kind == "area" then\n'
             '\t\tif not FOURTH.blob_still(unit) then return false end   -- ROUND 157: standing still, melee allowed\n'
             '\telseif kind ~= "execute" and kind ~= "value" then   -- ROUND 158: value has no caster gate\n')
STILL2_OLD = '\t\t\tif kind == "execute" and not FOURTH.exec_ok(e) then return false end   -- ROUND 157\n'
STILL2_NEW = STILL2_OLD + '\t\t\tif kind == "area" and e.men < FOURTH.area_min() then return false end   -- ROUND 158\n'

EVALS = r'''-- ============================================================================
-- ROUND 158 - THE AREA DRAINS AND THE LORD/HERO PROXY (open batch 6, user rulings 2026-11-15).
--   enemy_area_drain ("Most valuable infantry"; Blood Statuette of Spite,
--     Darkened Mist, The Fate of Bjuna x2, Maelstrom of Change, Otherworldly
--     Pestilence, Staff of Masks): the visible enemy infantry in range with at
--     least the ability's own model count left (the GENERATED AREA table: the
--     game's max_damaged_entities, 25 or 15) and the highest live value per
--     soldier; the caster standing still; no safety margin (a direct effect).
--   enemy_commander_value ("Lord/Hero proxy"; Dweomer Leach Orb: the game allows
--     spellcasters only and there is no read): the most valuable visible enemy
--     Lord or Hero in range (target class commander).
-- ============================================================================
function FOURTH.evaluate_enemy_area_drain(unit, routing)
	FOURTH.eg_mode = "shot"
	FOURTH.shot_kind = nil
	if routing or not FOURTH.blob_still(unit) then return %NO% end
	local m = FOURTH.blob_map(false)
	local e, s = FOURTH.shot_pick(unit, m, "area", false, true)
	if e == nil then return %NO% end
	FOURTH.shot_take(unit, e, "area", true, true)
	%RET_AREA%
end

function FOURTH.evaluate_enemy_commander_value(unit, routing)
	FOURTH.eg_mode = "shot"
	FOURTH.shot_kind = nil
	if routing then return %NO% end
	local m = FOURTH.blob_map(false)
	local e, s = FOURTH.shot_pick(unit, m, "value", false, true)
	if e == nil then return %NO% end
	FOURTH.shot_take(unit, e, "value", false, true)
	%RET_VALUE%
end

'''
LIVE_RET = {
    "%NO%": "nil",
    "%RET_AREA%": ('return FOURTH.shot_reason(unit, e, "most valuable enemy infantry, standing still (an area drain)",\n'
                   '\t\tstring.format("value %.1f per soldier, %d soldiers, %d hit per tick", s, e.men, FOURTH.area_min()))'),
    "%RET_VALUE%": ('return FOURTH.shot_reason(unit, e, "most valuable enemy Lord or Hero (the spellcaster proxy)",\n'
                    '\t\tstring.format("value %.0f", s))'),
}
ANN_RET = {"%NO%": "false", "%RET_AREA%": "return true", "%RET_VALUE%": "return true"}


def render(tpl, rep):
    for k, v in rep.items():
        tpl = tpl.replace(k, v)
    assert "%NO%" not in tpl and "%RET_" not in tpl
    return tpl


FAMS = ["enemy_area_drain", "enemy_commander_value"]
MAP_OLD = "\tenemy_execute = FOURTH.evaluate_enemy_execute,\n"
MAP_NEW = MAP_OLD + "\t-- ROUND 158\n" + "".join("\t%s = FOURTH.evaluate_%s,\n" % (f, f) for f in FAMS)
TIP_OLD = ('\tenemy_execute = "When armed, fires on the most valuable enemy in range whose health is at or below the execute '
           'line",\n')
TIP_NEW = TIP_OLD + (
    '\tenemy_area_drain = "When armed and standing still, fires on the enemy infantry in range worth the most per '
    'soldier, with enough soldiers for every strike",\n'
    '\tenemy_commander_value = "When armed, fires on the most valuable enemy lord or hero in range",\n')
ANCHOR = "FOURTH.evaluators = {\n"
GEN = re.compile(r"-- GENERATED by tools/gen_shot_tables\.py from unit_spec_abil.*?\nFOURTH\.load_exec_table\(\)\n", re.S)

for path, live in ((SRC, True), (ANN, False)):
    s = open(path, encoding="utf-8", newline="").read()
    assert "evaluate_enemy_area_drain" not in s and "FOURTH.AREA_TEXT" not in s
    before = s.count("\t{ marker = ")
    s = sub(s, RESTOCK, NEW_ENTRIES + RESTOCK)
    s = sub(s, WIND_OLD, WIND_NEW)
    s = sub(s, HOLD_OLD, HOLD_NEW)
    s = sub(s, FLY_OLD, FLY_NEW)
    s = sub(s, LIST_OLD, LIST_NEW, 2)
    s = sub(s, KIND_OLD, KIND_NEW)
    s = sub(s, PICK_OLD, PICK_NEW)
    s = sub(s, STILL_OLD, STILL_NEW)
    s = sub(s, STILL2_OLD, STILL2_NEW)
    s = sub(s, MAP_OLD, MAP_NEW)
    s = sub(s, TIP_OLD, TIP_NEW)
    s = sub(s, ANCHOR, render(EVALS, LIVE_RET if live else ANN_RET) + ANCHOR)
    assert s.count("\t{ marker = ") == before + 12
    open(path, "w", encoding="utf-8", newline="").write(s)
    print(path, "entries", before, "->", before + 12)

src_now = open(SRC, encoding="utf-8").read()
ks = GS.keys_in(src_now)
assert len(ks) == 33, len(ks)
block = (GS.lua_block(GS.derive(ks)) + GS.exec_block(GS.exec_rows(set(ks)))
         + GS.area_block(GS.area_rows(set(AREA_KEYS))))
for path in (SRC, ANN):
    s = open(path, encoding="utf-8", newline="").read()
    assert len(GEN.findall(s)) == 1
    s = GEN.sub(lambda m: block, s)
    open(path, "w", encoding="utf-8", newline="").write(s)
print("SHOT table re-derived (33 keys) + EXEC + AREA (7 keys)")

import gen_recharge_keys as G  # noqa: E402
new_block = G.lua_block(G.derive())
pat = re.compile(r"-- GENERATED by tools/gen_recharge_keys\.py.*?\nFOURTH\.load_recharge\(\)\n", re.S)
for path in (SRC, ANN):
    s = open(path, encoding="utf-8", newline="").read()
    assert len(pat.findall(s)) == 1
    s = pat.sub(lambda m: new_block, s)
    open(path, "w", encoding="utf-8", newline="").write(s)
print("lock table re-derived:", len(G.derive()), "keys")
