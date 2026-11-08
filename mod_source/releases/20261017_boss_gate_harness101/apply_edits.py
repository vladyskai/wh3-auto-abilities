# -*- coding: utf-8 -*-
"""Round 101 source edits: remove the 5 boss-only entries, add Gate of Khorne.

Binary read/write (LF preserved). Both files: live mod + annotated copy.
"""
import io, sys, os

ROOT = r"C:\Users\vlady\Desktop\WH3_mod"
LIVE = ROOT + r"\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = ROOT + r"\docs\WH3_auto_ability_annotated.lua"

BOSS = ["grand_faiths_bastion", "bitter_sting", "frenzied_challenge",
        "visions_of_madness", "guttural_roar"]

def rd(p): return io.open(p, "rb").read().decode("utf-8")
def wr(p, s):
    assert "\r" not in s, "CR found in " + p
    io.open(p, "wb").write(s.encode("utf-8"))

def cut_entry(s, marker):
    start = '\t{ marker = "%s"' % marker
    i = s.find(start)
    assert i >= 0, "entry not found: " + marker
    assert s.find(start, i + 1) < 0, "duplicate entry: " + marker
    j = s.find("\t\tox = 0, oy = 0 },\n", i)
    assert j > i, "entry end not found: " + marker
    j += len("\t\tox = 0, oy = 0 },\n")
    return s[:i] + s[j:]

def once(s, old, new, label):
    n = s.count(old)
    assert n == 1, "%s: %d matches" % (label, n)
    return s.replace(old, new, 1)

for path, kind in ((LIVE, "live"), (ANN, "ann")):
    s = rd(path)
    before = s.count("\t{ marker = ")
    for m in BOSS:
        s = cut_entry(s, m)
    after = s.count("\t{ marker = ")
    assert after == before - 5, (kind, before, after)

    # ---- Gate of Khorne entry, alphabetically before gaze_of_khaine
    gate = ('\t{ marker = "gate_of_khorne", name = "Gate of Khorne", trigger = "enemy_ground_melee",\n'
            '\t\tbadge = "zz_auto_badge_gate_of_khorne",\n'
            '\t\tkeys = { "wh3_main_character_abilities_gate_of_khorne" },\n'
            '\t\trange_real = 50,\n'
            '\t\tox = 0, oy = 0 },\n')
    anchor = '\t{ marker = "gaze_of_khaine"'
    assert s.count(anchor) == 1
    s = s.replace(anchor, gate + anchor, 1)

    # ---- the key's ground-form registration
    gk = '\t\t["wh3_dlc24_character_abilities_tacticians_stand_your_ground"] = true,\n'
    s = once(s, gk, gk + '\t\t-- GATE OF KHORNE (harness 101): target_friends + target_ground, a SUMMON\n'
                          '\t\t-- placed on the chosen FIGHTING enemy\'s ground - the ground form with the\n'
                          '\t\t-- ENEMY\'s position, never the caster\'s.\n'
                          '\t\t["wh3_main_character_abilities_gate_of_khorne"] = true,\n', kind + " ground key")

    # ---- the melee-only slot
    slot_anchor = ("FOURTH.eg_ground = nil\n\n-- one-time notice" if kind == "live"
                   else "FOURTH.eg_ground = nil\n\n-- THE DISTANCE PRIMITIVE")
    s = once(s, slot_anchor,
             "FOURTH.eg_ground = nil\n"
             "-- THE MELEE-ONLY FLAG (harness 101, Gate of Khorne): set by its OWN\n"
             "-- evaluator before the shared picker runs, so the picker keeps ONLY\n"
             "-- enemies that are FIGHTING (in melee) and the pre-cast re-check\n"
             "-- demands the same. Every other enemy trigger leaves it nil.\n"
             "FOURTH.eg_melee_only = nil\n"
             "\n" + slot_anchor.split("\n\n", 1)[1], kind + " slot")

    # ---- the picker: melee-only read
    s = once(s, "\tFOURTH.eg_ground = ground\n\tif not routing then",
             "\tFOURTH.eg_ground = ground\n"
             "\t-- THE MELEE-ONLY ARM (harness 101): Gate of Khorne's trigger says the enemy\n"
             "\t-- must be FIGHTING - in melee - so this form never accepts the\n"
             "\t-- under-missile-fire arm. Every other enemy trigger leaves it unset.\n"
             "\tlocal melee_only = (FOURTH.eg_melee_only == true)\n"
             "\tif not routing then", kind + " picker head")
    s = once(s, "\t\t\t\t\t\t\telseif FOURTH.eg_under_missile_attack(enemy) then",
             "\t\t\t\t\t\t\telseif (not melee_only) and FOURTH.eg_under_missile_attack(enemy) then",
             kind + " picker arm")

    if kind == "live":
        # ---- the reason string (live only: the annotated copy is log-free)
        old_tail = ('\t\t\t\t\tFOURTH.cast_target = best_enemy\n'
                    '\t\t\t\t\tif ground then\n')
        new_tail = ('\t\t\t\t\tFOURTH.cast_target = best_enemy\n'
                    '\t\t\t\t\tif melee_only then\n'
                    '\t\t\t\t\t\t-- GATE OF KHORNE\'S OWN REASON: names the chosen enemy\'s type and\n'
                    '\t\t\t\t\t\t-- the REAL edge-to-edge distance the offer test measured.\n'
                    '\t\t\t\t\t\treason = "closest fighting (in-melee) enemy within bound (targeting "\n'
                    '\t\t\t\t\t\t\t.. etype .. ", distance="\n'
                    '\t\t\t\t\t\t\t.. ((best_gap ~= nil) and string.format("%.1f", best_gap) or "?")\n'
                    '\t\t\t\t\t\t\t.. "m)"\n'
                    '\t\t\t\t\telseif ground then\n')
        s = once(s, old_tail, new_tail, "live reason")

        # ---- pre-cast re-check: melee-only demands still_melee
        s = once(s, "\t\tlocal eg_bound_now = FOURTH.eg_range_m or FOURTH.ACCUSATION_RANGE_M\n"
                    "\t\tlocal ok_alive, alive = pcall(function() return enemy:number_of_men_alive() end)\n"
                    "\t\tlocal ok_melee, melee = pcall(function() return enemy:is_in_melee() end)\n"
                    "\t\tlocal still_melee = (ok_melee and melee == true)\n"
                    "\t\tlocal still_shot = false\n"
                    "\t\tif not still_melee then\n",
                    "\t\tlocal eg_bound_now = FOURTH.eg_range_m or FOURTH.ACCUSATION_RANGE_M\n"
                    "\t\t-- GATE OF KHORNE (harness 101): a melee-only choice must STILL be\n"
                    "\t\t-- fighting; the missile arm is never a substitute for it.\n"
                    "\t\tlocal eg_melee_only_now = (FOURTH.eg_melee_only == true)\n"
                    "\t\tlocal ok_alive, alive = pcall(function() return enemy:number_of_men_alive() end)\n"
                    "\t\tlocal ok_melee, melee = pcall(function() return enemy:is_in_melee() end)\n"
                    "\t\tlocal still_melee = (ok_melee and melee == true)\n"
                    "\t\tlocal still_shot = false\n"
                    "\t\tif (not still_melee) and (not eg_melee_only_now) then\n", "live recheck")
        s = once(s, '.. " (alive=" .. tostring(alive_now) .. " melee=" .. tostring(still_melee)\n'
                    '\t\t\t\t.. " shot=" .. tostring(still_shot)\n',
                 '.. " (alive=" .. tostring(alive_now) .. " melee=" .. tostring(still_melee)\n'
                 '\t\t\t\t.. " shot=" .. tostring(still_shot)\n'
                 '\t\t\t\t.. " melee_only=" .. tostring(eg_melee_only_now)\n', "live skip line")
        s = once(s, '\t\t\t.. ", melee=" .. tostring(still_melee) .. " shot=" .. tostring(still_shot)\n',
                 '\t\t\t.. ", melee=" .. tostring(still_melee) .. " shot=" .. tostring(still_shot)\n'
                 '\t\t\t.. " melee_only=" .. tostring(eg_melee_only_now)\n', "live ok line")
    else:
        # annotated: the re-check has no log lines and no marker/bound locals
        old = ("\t\tlocal still_melee = (ok_melee and melee == true)\n"
               "\t\tlocal still_shot = false\n"
               "\t\tif not still_melee then\n")
        new = ("\t\t-- GATE OF KHORNE (harness 101): a melee-only choice must STILL be\n"
               "\t\t-- fighting; the missile arm is never a substitute for it.\n"
               "\t\tlocal eg_melee_only_now = (FOURTH.eg_melee_only == true)\n"
               "\t\tlocal still_melee = (ok_melee and melee == true)\n"
               "\t\tlocal still_shot = false\n"
               "\t\tif (not still_melee) and (not eg_melee_only_now) then\n")
        s = once(s, old, new, "ann recheck")

    # ---- the evaluator (both files; return shape differs)
    if kind == "live":
        ev = ("-- THE MELEE-ONLY ENEMY-GROUND EVALUATOR (harness 101, Gate of Khorne).\n"
              "-- THE USER'S TRIGGER, verbatim: \"The trigger will place it on the closest\n"
              "-- enemy that is in range of the ability and fighting.\" So: among ENEMY units\n"
              "-- within the ability's OWN 70% bound (50 m real -> floor(50 * 0.70) = 35 m,\n"
              "-- FOURTH.ENEMY_CAST_R50), keep those FIGHTING (in melee), pick the CLOSEST,\n"
              "-- and place the summon on THAT ENEMY'S GROUND via the ground form. The\n"
              "-- under-missile-fire arm is deliberately NOT accepted - \"fighting\" is read as\n"
              "-- in-melee, the strictest reading of the user's word. The chosen enemy is the\n"
              "-- CAST TARGET - NEVER the owner.\n"
              "function FOURTH.evaluate_enemy_ground_melee(unit, routing)\n"
              "\tFOURTH.eg_melee_only = true\n"
              "\treturn FOURTH.eg_pick_enemy(unit, routing, true)\n"
              "end\n\n")
    else:
        ev = ("-- THE MELEE-ONLY ENEMY-GROUND trigger (harness 101, Gate of Khorne): the\n"
              "-- user's rule - place it on the CLOSEST enemy within the ability's 70% bound\n"
              "-- (50 m -> 35 m) that is FIGHTING (in melee). The under-missile-fire arm is\n"
              "-- not accepted. The cast is placed on the chosen enemy's ground, never the\n"
              "-- owner's.\n"
              "function FOURTH.evaluate_enemy_ground_melee(unit, routing)\n"
              "\tFOURTH.eg_melee_only = true\n"
              "\treturn FOURTH.eg_pick_enemy(unit, routing, true)\n"
              "end\n\n")
    anchor = "-- THE UNIT-FORM EVALUATOR:" if kind == "live" else "-- THE UNIT-FORM trigger:"
    assert s.count(anchor) == 1, kind + " evaluator anchor"
    s = s.replace(anchor, ev + anchor, 1)

    # ---- registration + tooltip
    s = once(s, "\tenemy_ground_area = FOURTH.evaluate_enemy_ground_area,\n",
             "\tenemy_ground_area = FOURTH.evaluate_enemy_ground_area,\n"
             "\t-- GATE OF KHORNE (harness 101): closest FIGHTING enemy, summon on its ground.\n"
             "\tenemy_ground_melee = FOURTH.evaluate_enemy_ground_melee,\n", kind + " map")
    s = once(s, '\tenemy_ground_area = "When armed, fires when an enemy in range is in melee or under missile fire and the area hex is placed on its ground",\n',
             '\tenemy_ground_area = "When armed, fires when an enemy in range is in melee or under missile fire and the area hex is placed on its ground",\n'
             '\tenemy_ground_melee = "When armed, fires when an enemy in range is fighting in melee and the summon is placed on its ground",\n',
             kind + " tip")

    # ---- the poll clears the flag before every evaluate
    old_clear = "\t\t\t\t\tFOURTH.eg_ground = nil\n"
    new_clear = ("\t\t\t\t\tFOURTH.eg_ground = nil\n"
                 "\t\t\t\t\tFOURTH.eg_melee_only = nil\n")
    s = once(s, old_clear, new_clear, kind + " clear")

    wr(path, s)
    print(kind, "entries", s.count("\t{ marker = "), "keys", s.count("keys = {"))
print("OK")
