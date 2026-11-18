#!/usr/bin/env python3
"""Build harness177.lua from harness176.lua for round 178 (the score-3 review, rows 23-55). Older harnesses are never
edited.

Rebases: see R (each names the pin and why); every '937' (the entry count) becomes 938 (Trophy Heads split)."""
import os
import re

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261118_score3_rows_harness176\harness176.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261118_score3_rows2_harness177\harness177.lua"
SECTION = open(r"C:\Users\vlady\Desktop\WH3_mod\tools\h177_section.lua", encoding="utf-8").read()
BANNER = """-- ============================================================================
-- HARNESS 177 - ROUND 178: THE SCORE-3 REVIEW, ROWS 23-55 (2 new families, 20 entries
--   moved, Trophy Heads split).
--   Edited vs harness176: this banner, the rebases listed in tools/make_harness177.py,
--   run_h177 and its call.
--   RED control: H177_LIVE / H177_ANN on docs/backups/round178/pre178_*.lua.
-- ============================================================================
"""
LABELS = (
    '    enemy_fast_or_melee = "When armed, fires at a fast enemy closing on our units, else at the closest enemy in melee",\n'
    '    enemy_fast_fire_melee = "When armed, fires at a fast enemy closing on our units, else at an enemy under our fire, else at one in melee",\n'
    '    enemy_most_models = "When armed and standing still, fires on the enemy unit in range with the most soldiers (16 at least)",\n')
R = [
    ('    melee_healthy = "When armed, fires in melee while above 50% health",\n',
     '    melee_healthy = "When armed, fires in melee while above 50% health",\n'
     '    -- HARNESS 177: the round-178 labels\n' + LABELS, 1),
    # Eye of Khorne's family now ranks the value first (the user's ruling): its label
    ('    enemy_low_health_noncommander = "When armed, fires on the lowest-health enemy in range that is below 20% health and is not a Lord or Hero",\n',
     '    enemy_low_health_noncommander = "When armed, fires on the most valuable enemy in range that is below 20% health and is not a Lord or Hero",   -- HARNESS 177\n', 1),
    ("""raw_find(s, 'enemy_low_health_noncommander = "When armed, fires on the lowest-health enemy', 1, true) ~= nil""",
     """raw_find(s, 'enemy_low_health_noncommander = "When armed, fires on the most valuable enemy', 1, true) ~= nil   -- HARNESS 177""", 1),
    # the counts the 20 moves and the Trophy Heads split change
    ("""'trigger = "enemy_engaged_or_shot"') == 37""", """'trigger = "enemy_engaged_or_shot"') == 22""", 5),
    ("mu = 265, es = 37,", "mu = 265, es = 22,", 1),
    ("""'trigger = "enemy_ground_melee"') == 75""", """'trigger = "enemy_ground_melee"') == 74""", 2),
    ("RED_MODE and 1 or 75", "RED_MODE and 1 or 74", 1),
    ("EXP.sum and 75 or 1", "EXP.sum and 74 or 1", 1),
    ("""'trigger = "enemy_melee"') == 34""", """'trigger = "enemy_melee"') == 35""", 3),   # + Trophy Heads (Daemon Wings)
    ('"\\t\\ttarget_class = ") == 58', '"\\t\\ttarget_class = ") == 54', 3),
    # the 6 plain roots (rows 36-41, user: "Yes pls", no melee arm) joined the fast-enemy family
    ("""'trigger = "enemy_fast_near_ally"') == 9""", """'trigger = "enemy_fast_near_ally"') == 15""", 2),
    ('range_real = ") == 417', 'range_real = ") == 418', 2),
    ("""'trigger = "enemy_blob"') == 71""", """'trigger = "enemy_blob"') == 69""", 2),
    ("""'trigger = "enemy_commander_value"') == 5""", """'trigger = "enemy_commander_value"') == 4""", 3),
    ("""'trigger = "enemy_melee_or_shooting"') == 1""", """'trigger = "enemy_melee_or_shooting"') == 3""", 1),
    ("    a = (it == 1874)   -- HARNESS 172: 2 x 937\n", "    a = (it == 1876)   -- HARNESS 177: 2 x 938\n", 1),
    ('cp102(s, "\\t\\trange_real = ") == (EXP.sum and 417 or 96))',
     'cp102(s, "\\t\\trange_real = ") == (EXP.sum and 418 or 96))   -- HARNESS 177: + Trophy Heads (Daemon Wings)', 1),
    # h142 0zn: The Soulstealer left enemy_ground_melee for enemy_most_models (round 178)
    ("""        and raw_find(s, '{ marker = "the_soulstealer", name = "The Soulstealer", trigger = "enemy_ground_melee",', 1, true) ~= nil\n""",
     """        and raw_find(s, '{ marker = "the_soulstealer", name = "The Soulstealer", trigger = "enemy_most_models",', 1, true) ~= nil   -- HARNESS 177\n""", 1),
    # h142 SS1: the Soulstealer now waits for a visible block of 25+ soldiers with the caster standing (round 178; its
    # firing world is h177 SO1): an enemy merely in melee, with no visible map, gets no cast
    ('      function(b) return one(b, SS, 30) end, "the_soulstealer", SS, 1, nil, false, "ground" },\n',
     '      function(b) return one(b, SS, 30) end, "the_soulstealer", SS, 0, nil, false, "ground" },   -- HARNESS 177: area drain now\n', 1),
    # h137 P2: Void Pendulum now targets enemy SPELLCASTERS (round 178; its firing world is h177 VP1): a Lord who cannot
    # cast is not the game's target
    ('      function(b) return one(b, VOID, 20, { name = CMDR }) end, "void_pendulum", VOID, 1, nil, nil },\n',
     '      function(b) return one(b, VOID, 20, { name = CMDR }) end, "void_pendulum", VOID, 0, nil, nil },   -- HARNESS 177: spellcasters only now\n', 1),
]
src = open(SRC, encoding="utf-8").read()
for a, b, n in R:
    assert src.count(a) == n, (a[:70], src.count(a))
    src = src.replace(a, b)
n937 = len(re.findall(r"(?<!\d)937(?!\d)", src))
src = re.sub(r"(?<!\d)937(?!\d)", "938", src)
print("937 -> 938:", n937)
RUNNER_ANCHOR = "\n-- THE RUNNER. The air-drop sections always run;"
assert src.count(RUNNER_ANCHOR) == 1
src = src.replace(RUNNER_ANCHOR, "\n" + SECTION + RUNNER_ANCHOR)
assert src.count("\nrun_h176()\n") == 1
src = src.replace("\nrun_h176()\n", "\nrun_h176()\nrun_h177()\n")
src = BANNER + src
assert "\u2014" not in BANNER + SECTION
os.makedirs(os.path.dirname(DST), exist_ok=True)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST, len(src), "bytes")
