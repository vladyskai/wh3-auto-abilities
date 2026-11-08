# -*- coding: utf-8 -*-
"""ROUND h94 IMPLEMENTATION: Accusation's automatic activation.

Applies the SAME logical change to the LIVE mod and to the ANNOTATED reading
copy (each in its own idiom: the live build returns reason strings and logs;
the annotated copy returns booleans and is log-free). Snapshots the current
files first (pre94_*.lua) as the RED CONTROL target.

  1. a NEW reusable evaluator `enemy_engaged_or_shot` (+ its helpers/constant on
     the FOURTH bag): fire when an enemy unit in range is in melee OR under
     missile fire; the chosen enemy is the cast target (never the owner);
  2. Accusation's entry moves from trigger "melee_unwavering" to the new trigger;
  3. the tooltip wording entry;
  4. the poll clears the new slots before every evaluate;
  5. attempt_activation re-fetches the caster FRESH and re-checks the enemy
     immediately before the cast (the proven fresh-handle route).
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
write(HERE + "/pre94_live.lua", live)
write(HERE + "/pre94_ann.lua", ann)
print("wrote pre94_live.lua", len(live), "bytes")
print("wrote pre94_ann.lua", len(ann), "bytes")

blk_live = read(HERE + "/insert_ev_live.lua")
blk_ann = read(HERE + "/insert_ev_ann.lua")

MAP_OLD = ("\tblood_sacrifice = FOURTH.evaluate_blood_sacrifice,\n"
           "\teat_da_runts = FOURTH.evaluate_eat_da_runts,\n}")
MAP_NEW = ("\tblood_sacrifice = FOURTH.evaluate_blood_sacrifice,\n"
           "\teat_da_runts = FOURTH.evaluate_eat_da_runts,\n"
           "\t-- ACCUSATION (this round): the FIRST ENEMY-TARGETED trigger.\n"
           "\tenemy_engaged_or_shot = FOURTH.evaluate_enemy_engaged_or_shot,\n}")

TIP_OLD = ("\teat_da_runts = \"When armed, fires when this unit is at or below 75% health, "
           "otherwise on the lowest-health ally in range\",\n}")
TIP_NEW = ("\teat_da_runts = \"When armed, fires when this unit is at or below 75% health, "
           "otherwise on the lowest-health ally in range\",\n"
           "\tenemy_engaged_or_shot = \"When armed, fires when an enemy unit in range is in melee "
           "or under missile fire\",\n}")

ACC_OLD = "\t{ marker = \"accusation\", name = \"Accusation\", trigger = \"melee_unwavering\","
ACC_NEW = "\t{ marker = \"accusation\", name = \"Accusation\", trigger = \"enemy_engaged_or_shot\","

EY_EV_ANCHOR = "FOURTH.evaluators = {\n\tcharge = FOURTH.evaluate_charge,"

# ----- the caster fresh-fetch (attempt_activation) -----
L6A_OLD = "\tlocal uc = script_unit.uc\n\n\tif uc == nil then"
L6A_NEW = ("\t-- THE PROVEN FRESH-HANDLE ROUTE (Accusation, this round): when the enemy\n"
           "\t-- trigger chose a target, use the CASTER script_unit re-fetched FRESH from\n"
           "\t-- the friendly enumerator THIS tick (never a controller held from an\n"
           "\t-- earlier poll - the round-4 log-proven bench_fresh shape). Falls back to\n"
           "\t-- the poll's own script_unit if the fresh fetch failed.\n"
           "\tlocal uc = script_unit.uc\n"
           "\tif FOURTH.eg_enemy ~= nil and FOURTH.eg_caster_su ~= nil and FOURTH.eg_caster_su.uc ~= nil then\n"
           "\t\tuc = FOURTH.eg_caster_su.uc\n"
           "\tend\n\n"
           "\tif uc == nil then")

A6A_OLD = "\tlocal uc = script_unit.uc   -- the unit's order controller\n\tif uc == nil then"
A6A_NEW = ("\t-- THE PROVEN FRESH-HANDLE ROUTE (Accusation, this round): when the enemy\n"
           "\t-- trigger chose a target, use the CASTER script_unit re-fetched FRESH from\n"
           "\t-- the friendly enumerator THIS tick (never a controller held from an\n"
           "\t-- earlier poll). Falls back to the poll's own script_unit.\n"
           "\tlocal uc = script_unit.uc   -- the unit's order controller\n"
           "\tif FOURTH.eg_enemy ~= nil and FOURTH.eg_caster_su ~= nil and FOURTH.eg_caster_su.uc ~= nil then\n"
           "\t\tuc = FOURTH.eg_caster_su.uc\n"
           "\tend\n"
           "\tif uc == nil then")

# ----- the poll clear (adds the two enemy slots) -----
L5_OLD = ("\t\t\t\t\tFOURTH.bs_ally = nil\n"
          "\t\t\t\t\tFOURTH.edr_ally = nil\n"
          "\t\t\t\t\tlocal reason = ability.evaluate(unit, routing)")
L5_NEW = ("\t\t\t\t\tFOURTH.bs_ally = nil\n"
          "\t\t\t\t\tFOURTH.edr_ally = nil\n"
          "\t\t\t\t\tFOURTH.eg_enemy = nil\n"
          "\t\t\t\t\tFOURTH.eg_caster_su = nil\n"
          "\t\t\t\t\tlocal reason = ability.evaluate(unit, routing)")

A5_OLD = ("\t\t\t\t\tFOURTH.bs_ally = nil\n"
          "\t\t\t\t\tFOURTH.edr_ally = nil\n"
          "\t\t\t\t\tlocal want_fire = ability.evaluate(unit, routing)")
A5_NEW = ("\t\t\t\t\tFOURTH.bs_ally = nil\n"
          "\t\t\t\t\tFOURTH.edr_ally = nil\n"
          "\t\t\t\t\tFOURTH.eg_enemy = nil\n"
          "\t\t\t\t\tFOURTH.eg_caster_su = nil\n"
          "\t\t\t\t\tlocal want_fire = ability.evaluate(unit, routing)")

# ----- the enemy pre-cast re-check (attempt_activation) -----
L6B_ANCHOR = "\t-- THE CALL. Ordinary keys (self- or unit-targeted) use the proven"
L6B_BLOCK = ("\t-- ACCUSATION ENEMY RE-CHECK (this round): the enemy trigger chose an ENEMY\n"
             "\t-- unit and left it in FOURTH.eg_enemy (the cast target is the same unit,\n"
             "\t-- in FOURTH.cast_target); RE-READ the condition NOW, immediately before the\n"
             "\t-- cast - the enemy must still be ALIVE and still IN MELEE or UNDER FIRE and\n"
             "\t-- still IN RANGE. If it lapsed the cast is wasted, so SKIP it rather than\n"
             "\t-- spend it. The chosen enemy is the CAST TARGET - NEVER the owner.\n"
             "\tif FOURTH.eg_enemy ~= nil then\n"
             "\t\tlocal enemy = FOURTH.eg_enemy\n"
             "\t\tlocal ok_alive, alive = pcall(function() return enemy:number_of_men_alive() end)\n"
             "\t\tlocal ok_melee, melee = pcall(function() return enemy:is_in_melee() end)\n"
             "\t\tlocal still_melee = (ok_melee and melee == true)\n"
             "\t\tlocal still_shot = false\n"
             "\t\tif not still_melee then\n"
             "\t\t\tstill_shot = FOURTH.eg_under_missile_attack(enemy)\n"
             "\t\tend\n"
             "\t\tlocal alive_now = (ok_alive and type(alive) == \"number\" and alive > 0)\n"
             "\t\tlocal in_range_now = FOURTH.eg_enemy_in_range(unit, enemy)\n"
             "\t\tif not alive_now or not (still_melee or still_shot) or not in_range_now then\n"
             "\t\t\tlog(\"  accusation SKIPPED: the chosen enemy lapsed before the cast\"\n"
             "\t\t\t\t.. \" (alive=\" .. tostring(alive_now) .. \" melee=\" .. tostring(still_melee)\n"
             "\t\t\t\t.. \" shot=\" .. tostring(still_shot) .. \" in_range=\" .. tostring(in_range_now)\n"
             "\t\t\t\t.. \") - cast not spent\")\n"
             "\t\t\tFOURTH.eg_enemy = nil\n"
             "\t\t\tFOURTH.eg_arm = nil\n"
             "\t\t\tif RELEASE_CONTROL_AFTER and took_control then\n"
             "\t\t\t\tlocal ok_release, err_release = pcall(function() uc:release_control() end)\n"
             "\t\t\t\tlog(\"  release_control         : ok=\" .. tostring(ok_release)\n"
             "\t\t\t\t\t.. (ok_release and \"\" or (\"  ERROR: \" .. tostring(err_release))))\n"
             "\t\t\tend\n"
             "\t\t\treturn \"held\"\n"
             "\t\tend\n"
             "\t\tlog(\"  accusation pre-cast re-check: target still engaged (\" .. tostring(FOURTH.eg_arm)\n"
             "\t\t\t.. \", melee=\" .. tostring(still_melee) .. \" shot=\" .. tostring(still_shot)\n"
             "\t\t\t.. \", in_range=\" .. tostring(in_range_now) .. \") - firing\")\n"
             "\tend\n\n")

A6B_BLOCK = ("\t-- ACCUSATION ENEMY RE-CHECK (this round): re-read the chosen enemy's\n"
             "\t-- condition immediately before the cast - it must still be ALIVE and still\n"
             "\t-- IN MELEE or UNDER FIRE and still IN RANGE, or the cast is SKIPPED. The\n"
             "\t-- chosen enemy is the CAST TARGET - never the owner.\n"
             "\tif FOURTH.eg_enemy ~= nil then\n"
             "\t\tlocal enemy = FOURTH.eg_enemy\n"
             "\t\tlocal ok_alive, alive = pcall(function() return enemy:number_of_men_alive() end)\n"
             "\t\tlocal ok_melee, melee = pcall(function() return enemy:is_in_melee() end)\n"
             "\t\tlocal still_melee = (ok_melee and melee == true)\n"
             "\t\tlocal still_shot = false\n"
             "\t\tif not still_melee then\n"
             "\t\t\tstill_shot = FOURTH.eg_under_missile_attack(enemy)\n"
             "\t\tend\n"
             "\t\tlocal alive_now = (ok_alive and type(alive) == \"number\" and alive > 0)\n"
             "\t\tlocal in_range_now = FOURTH.eg_enemy_in_range(unit, enemy)\n"
             "\t\tif not alive_now or not (still_melee or still_shot) or not in_range_now then\n"
             "\t\t\tFOURTH.eg_enemy = nil\n"
             "\t\t\tFOURTH.eg_arm = nil\n"
             "\t\t\tif RELEASE_CONTROL_AFTER and took_control then\n"
             "\t\t\t\tpcall(function() uc:release_control() end)\n"
             "\t\t\tend\n"
             "\t\t\treturn \"held\"\n"
             "\t\tend\n"
             "\tend\n\n")

# =========================== LIVE ===========================
live = sub(live, EY_EV_ANCHOR, blk_live + "\n" + EY_EV_ANCHOR, "L1 evaluator block")
live = sub(live, MAP_OLD, MAP_NEW, "L2 map")
live = sub(live, TIP_OLD, TIP_NEW, "L3 tip")
live = sub(live, ACC_OLD, ACC_NEW, "L4 accusation trigger")
live = sub(live, L5_OLD, L5_NEW, "L5 poll clear")
live = sub(live, L6A_OLD, L6A_NEW, "L6a fresh caster")
live = sub(live, L6B_ANCHOR, L6B_BLOCK + L6B_ANCHOR, "L6b enemy re-check")

# =========================== ANN ===========================
ann = sub(ann, EY_EV_ANCHOR, blk_ann + "\n" + EY_EV_ANCHOR, "A1 evaluator block")
ann = sub(ann, MAP_OLD, MAP_NEW, "A2 map")
ann = sub(ann, TIP_OLD, TIP_NEW, "A3 tip")
ann = sub(ann, ACC_OLD, ACC_NEW, "A4 accusation trigger")
ann = sub(ann, A5_OLD, A5_NEW, "A5 poll clear")
ann = sub(ann, A6A_OLD, A6A_NEW, "A6a fresh caster")
ann = sub(ann, L6B_ANCHOR, A6B_BLOCK + L6B_ANCHOR, "A6b enemy re-check")

# sanity: the annotated copy stays log-free and find-free
assert "log(" not in ann, "annotated copy gained a log() call"
assert "string.find" not in ann, "annotated copy gained a string.find call"
assert ann.count("FOURTH.cast_target = unit") == 2
assert live.count("FOURTH.cast_target = unit") == 2
assert live.count('trigger = "melee_unwavering"') == 480, live.count('trigger = "melee_unwavering"')
assert ann.count('trigger = "melee_unwavering"') == 480
assert live.count('trigger = "enemy_engaged_or_shot"') == 1
assert ann.count('trigger = "enemy_engaged_or_shot"') == 1
assert live.count("\t{ marker = ") == 579
assert ann.count("\t{ marker = ") == 579

write(LIVE, live)
write(ANN, ann)
print("wrote", LIVE, len(live), "bytes")
print("wrote", ANN, len(ann), "bytes")
print("OK: live melee_unwavering=480 enemy_engaged_or_shot=1; ann same")
