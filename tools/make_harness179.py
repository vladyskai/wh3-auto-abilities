#!/usr/bin/env python3
"""Build harness179.lua from harness178.lua for round 180 (the score-3 review, rows 87-114 and 128). Older harnesses are
never edited.

Rebases: see R (each names the pin and why); every '938' (entries) becomes 935 and every '992' (keys) 989 (three closed:
Heaven's Gate, Snowflake Pendant, Stave of Avelorn)."""
import os
import re

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261118_score3_rows3_harness178\harness178.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261118_score3_rows4_harness179\harness179.lua"
SECTION = open(r"C:\Users\vlady\Desktop\WH3_mod\tools\h179_section.lua", encoding="utf-8").read()
BANNER = """-- ============================================================================
-- HARNESS 179 - ROUND 180: THE SCORE-3 REVIEW, ROWS 87-114 AND 128 (4 new families, 13 entries
--   moved, 3 closed, the roots' real range, the 80% WW buffers, the lizard / tiger rule sets).
--   Edited vs harness178: this banner, the rebases listed in tools/make_harness179.py,
--   run_h179 and its call.
--   RED control: H179_LIVE / H179_ANN on docs/backups/round180/pre180_*.lua.
-- ============================================================================
"""
LABELS = (
    '    health_aura_ally_rule = "When armed, fires when this unit or a friendly unit it may target is at or below 75% health, cast on it",\n'
    '    self_heal_clear = "When armed, fires at or below 75% health with no visible enemy near",\n'
    '    self_hurt_attacked = "When armed, fires at or below 75% health while in melee or under missile fire",\n'
    '    charge_or_tired = "When armed, fires when charging or tired",\n')
EDR_P = '\n      { name = "unit", uid = %d, owns = { EDR }, melee = false, health_percent = %d },\n'
R = [
    # the TIP mirror: the 5 new labels; the 2 re-ruled ones
    ('    heal_ground_best = "When armed, fires on the ground under the hurt unit (75% or less) with the most hurt units around it",\n',
     '    heal_ground_best = "When armed, fires on the ground under the hurt unit (75% or less) with the most hurt units around it",\n'
     '    -- HARNESS 179: the round-180 labels\n' + LABELS, 1),
    ('    eat_da_runts = "When armed, fires when this unit is at or below 75% health, otherwise on the lowest-health ally in range",\n',
     '    eat_da_runts = "When armed, fires when this unit is at or below 75% health, on the cheapest healthy ally in range",   -- HARNESS 179\n', 1),
    ('    self_out_of_ammo = "When armed, fires when this unit has no ammunition left",\n',
     '    self_out_of_ammo = "When armed, fires when this unit has no ammunition left and is above 50% health",   -- HARNESS 179\n', 1),
    # the counts the moves and closures change
    ("""'trigger = "charge_or_melee"') == 37""", """'trigger = "charge_or_melee"') == 36""", 9),   # Shield of Thorns
    ("\n      cm == 37)\n", "\n      cm == 36)   -- HARNESS 179: Shield of Thorns moved\n", 1),
    ("""'trigger = "enemy_fast_near_ally"') == 15""", """'trigger = "enemy_fast_near_ally"') == 19""", 2),   # the 4 roots
    ("""'trigger = "enemy_ground_area"') == 6""", """'trigger = "enemy_ground_area"') == 2""", 3),
    ("""'trigger = "enemy_wander"') == 43""", """'trigger = "enemy_wander"') == 42""", 3),   # Heaven's Gate closed
    ("""'trigger = "melee_self_or_ally"') == 2""", """'trigger = "melee_self_or_ally"') == 3""", 1),   # Shield of Thorns
    ("""'trigger = "tired"') == 2""", """'trigger = "tired"') == 1""", 3),   # Foe-Seeker
    ("""'trigger = "ushoran_health"') == 18""", """'trigger = "ushoran_health"') == 11""", 5),   # 7 heals moved
    ("""'trigger = "when_ready"') == 22""", """'trigger = "when_ready"') == 20""", 1),   # 2 closed
    ("ush = 18, present = false }", "ush = 11, present = false }", 1),
    ('range_real = ") == 418', 'range_real = ") == 417', 2),   # Heaven's Gate
    ("EXP.sum and 418 or 96))", "EXP.sum and 417 or 96))", 1),
    ('ally_range_real = ") == 63', 'ally_range_real = ") == 68', 3),   # Thorns, Chalice, Breath x2, Mantra
    ('start_armed = true,\\n") == 33', 'start_armed = true,\\n") == 42', 3),   # the 9 moved entries keep their default
    ("nkeys == 334)", "nkeys == 333)", 1),   # Heaven's Gate's wind-up row
    ("1876", "1870", 1),   # 2 x 935
    # h104 0w: Foe-Seeker left 'tired' for charge_or_tired (round 180)
    ("""      raw_find(src, '{ marker = "foe_seeker", name = "Foe-Seeker", trigger = "tired",', 1, true) ~= nil)""",
     """      raw_find(src, '{ marker = "foe_seeker", name = "Foe-Seeker", trigger = "charge_or_tired",', 1, true) ~= nil)   -- HARNESS 179""", 1),
    # h92 0p: Eat da Runts' chosen ally is now 'best' (the round-180 rewrite)
    ('cp(s, "FOURTH.edr_ally = best_ally") == 1', 'cp(s, "FOURTH.edr_ally = best\\n") == 1', 1),
    # h92 P6 / P7 / P9: Eat da Runts! - the caster must be hurt, the target a healthy ally, no self arm (round 180)
    (EDR_P % (9351, 70), EDR_P % (9351, 70), 1),
    ('    local a = (#W.fires == 1 and W.fires[1].uid == 9351 and W.fires[1].key == EDR)\n'
     '    check(TAG .. "P6a: the hurt owner fired eat_da_runts once (" .. fire_detail(W) .. ")", a)\n'
     '    local b = (fire_target_for(W, 9351) == caster)\n'
     '    check(TAG .. "P6b: the self arm casts on the OWNER itself", b)\n'
     '    local c = (count_log(W, "reason: eat da runts: self health 70% (<= 75%), cast on self") == 1)\n'
     '    check(TAG .. "P6c: the eat-da-runts self reason names the live percent [live log]", lg(TAG, c))\n',
     '    local a = (#W.fires == 0)   -- HARNESS 179: no self arm since round 180 (the heal comes from an ally)\n'
     '    check(TAG .. "P6a: the hurt owner ALONE stays SILENT (" .. fire_detail(W) .. ")", a)\n'
     '    local b = (fire_target_for(W, 9351) == nil)\n'
     '    check(TAG .. "P6b: no cast target at all (no self arm)", b)\n'
     '    local c = (count_log(W, "reason: eat da runts") == 0)\n'
     '    check(TAG .. "P6c: no eat-da-runts reason [live log]", lg(TAG, c))\n', 1),
    (EDR_P % (9361, 100) + '      { name = "ally", uid = 9362, owns = {}, melee = false, health_percent = 50, dist = 15 },\n',
     EDR_P % (9361, 70) + '      { name = "ally", uid = 9362, owns = {}, melee = false, health_percent = 100, dist = 15 },   -- HARNESS 179\n', 1),
    ('"P7a: the healthy owner fired eat_da_runts once for the hurt ally ("', '"P7a: the HURT owner fired eat_da_runts once for the healthy ally ("', 1),
    ('"P7b: the ally arm casts on the HURT ALLY"', '"P7b: the cast lands on the cheapest HEALTHY ALLY"', 1),
    ('count_log(W, "reason: eat da runts: lowest-health ally 50% (<= 75%), cast on ally") == 1',
     'count_log(W, "reason: eat da runts: self health 70% (<= 75%), cast on the cheapest healthy ally") == 1', 1),
    (EDR_P % (9381, 100) + '      { name = "ally", uid = 9382, owns = {}, melee = false, health_percent = 50, dist_seq = { 15, 80 } },\n',
     EDR_P % (9381, 70) + '      { name = "ally", uid = 9382, owns = {}, melee = false, health_percent = 100, dist_seq = { 15, 80 } },   -- HARNESS 179\n', 1),
    # h95 the Eat da Runts range world: a hurt owner and a healthy ally now (round 180)
    ('      { name = "unit", uid = 9851, owns = { EDK }, melee = false, health_percent = 100 },\n'
     '      { name = "ally", uid = 9852, owns = {}, melee = false, health_percent = 50, dist = dist },\n',
     '      { name = "unit", uid = 9851, owns = { EDK }, melee = false, health_percent = 70 },   -- HARNESS 179\n'
     '      { name = "ally", uid = 9852, owns = {}, melee = false, health_percent = 100, dist = dist },\n', 1),
    # h97 the r15 ground family: Entangle now rides the fast-enemy pick at 100 m; Amulet of Pha-Stah (ground, 100 m) stands in
    ('    { real = 15,  bound = 10,  marker = "entangle", key = "wh2_dlc10_character_abilities_entangle", ground = true },\n',
     '    { real = 100, bound = 70,  marker = "amulet_of_phastah", key = "wh2_dlc09_item_abilities_amulet_of_phastah", ground = true },   -- HARNESS 179: Entangle moved\n', 1),
    # h137 G1: Entangle fires only on a fast enemy now (round 180; its firing world is h179 RT1)
    ('      function(b) return one(b, ENT, 5, { name = LIVING }) end, "entangle", ENT, 1, nil, false },\n',
     '      function(b) return one(b, ENT, 5, { name = LIVING }) end, "entangle", ENT, 0, nil, false },   -- HARNESS 179: fast enemies only\n', 1),
    # h162 WN3: Heaven's Gate is closed (round 180): nothing to arm
    ('        { [tostring(b + 5)] = 1600 } end, "heavens_gate", HG, 1, 0, nil },\n',
     '        { [tostring(b + 5)] = 1600 } end, "heavens_gate", HG, 0, nil, nil },   -- HARNESS 179: closed\n', 1),
    # h165 SC2: Heaven's Gate has no card any more
    ('        and by.heavens_gate == "Fires when it and the target stand still, where the blast hurts the enemy most"\n',
     '        and by.heavens_gate == nil   -- HARNESS 179: closed\n', 1),
]
src = open(SRC, encoding="utf-8").read()
for a, b, n in R:
    assert src.count(a) == n, (a[:80], src.count(a))
    src = src.replace(a, b)
n938 = len(re.findall(r"(?<!\d)938(?!\d)", src))
src = re.sub(r"(?<!\d)938(?!\d)", "935", src)
n992 = len(re.findall(r"(?<!\d)992(?!\d)", src))
src = re.sub(r"(?<!\d)992(?!\d)", "989", src)
print("938 -> 935:", n938, " 992 -> 989:", n992)
RUNNER_ANCHOR = "\n-- THE RUNNER. The air-drop sections always run;"
assert src.count(RUNNER_ANCHOR) == 1
src = src.replace(RUNNER_ANCHOR, "\n" + SECTION + RUNNER_ANCHOR)
assert src.count("\nrun_h178()\n") == 1
src = src.replace("\nrun_h178()\n", "\nrun_h178()\nrun_h179()\n")
src = BANNER + src
assert "\u2014" not in BANNER + SECTION
os.makedirs(os.path.dirname(DST), exist_ok=True)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST, len(src), "bytes")
