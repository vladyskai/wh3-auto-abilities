#!/usr/bin/env python3
"""Build harness181.lua from harness180.lua for round 182 (the finishers). Older harnesses are never edited.

Rebases: see R (each names the pin and why)."""
import os

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261120_landmine_squig_harness180\harness180.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261120_finishers_harness181\harness181.lua"
SECTION = open(r"C:\Users\vlady\Desktop\WH3_mod\tools\h181_section.lua", encoding="utf-8").read()
BANNER = """-- ============================================================================
-- HARNESS 181 - ROUND 182: THE FINISHERS (the Executioner on the lowest health %, 90% bound;
--   the Emperor's Executioner on the highest health % below the line; Skjalandir's Fall in
--   melee or shooting).
--   Edited vs harness180: this banner, the rebases listed in tools/make_harness181.py,
--   run_h181 and its call.
--   RED control: H181_LIVE / H181_ANN on docs/backups/round182/pre182_*.lua.
-- ============================================================================
"""
LABELS = (
    '    enemy_finisher = "When armed and standing still, fires on the single-entity enemy in range with the lowest health, none of yours near it",\n'
    '    melee_or_self_shooting = "When armed, fires when this unit is in melee or shooting",\n')
R = [
    # the TIP mirror: the 2 new labels; the Emperor's Executioner's label
    ('    melee_clear_block = "When armed, fires in melee when none of our other units is inside its blast and at least 60 enemy soldiers are",\n',
     '    melee_clear_block = "When armed, fires in melee when none of our other units is inside its blast and at least 60 enemy soldiers are",\n'
     '    -- HARNESS 181: the round-182 labels\n' + LABELS, 1),
    ('    enemy_execute = "When armed, fires on the most valuable enemy in range whose health is at or below the execute line",\n',
     '    enemy_execute = "When armed, fires on the enemy in range with the most health left at or below the execute line",   -- HARNESS 181\n', 1),
    # the counts
    ("""'trigger = "enemy_blob"') == 69""", """'trigger = "enemy_blob"') == 68""", 2),   # the Executioner left
    # h129 0y: Skjalandir's Fall left melee_or_shooting_into_melee (round 182: every hit blinds)
    ("""        and raw_find(s, 'trigger = "melee_or_shooting_into_melee",', 1, true) ~= nil)""",
     """        and raw_find(s, 'trigger = "melee_or_self_shooting",', 1, true) ~= nil)   -- HARNESS 181""", 1),
    # h129 S1b: the shooting arm's reason is the plain self-shooting one now
    ('count_log(Ws, "shooting past its cast point at a target that is in melee, cast on self") == 1',
     'count_log(Ws, "the unit is shooting past its cast point, cast on self") == 1', 1),
    # h129 S2: a target NOT in melee is enough now (round 182: every shot blinds)
    ('      local Ws2 = world("S2. Skjalandir\'s Fall: shooting at a target NOT in melee -> no cast",',
     '      local Ws2 = world("S2. Skjalandir\'s Fall: shooting at a target NOT in melee -> ONE cast (round 182)",', 1),
    ('        { { 13061, "skjalandirs_fall" } }, { SK }, f.path, TAG, 24)\n      if Ws2 ~= nil then\n'
     '        local a = (fires_of(Ws2, SK) == 0)\n        check(TAG .. "S2a: no cast (" .. fires_of(Ws2, SK) .. ")", a)',
     '        { { 13061, "skjalandirs_fall" } }, { SK }, f.path, TAG, 24)\n      if Ws2 ~= nil then\n'
     '        local a = (fires_of(Ws2, SK) >= 1)   -- HARNESS 181: every shot blinds (24 polls: the mock accepts repeats)\n'
     '        check(TAG .. "S2a: it casts (" .. fires_of(Ws2, SK) .. ")", a)', 1),
]
src = open(SRC, encoding="utf-8").read()
for a, b, n in R:
    assert src.count(a) == n, (a[:80], src.count(a))
    src = src.replace(a, b)
RUNNER_ANCHOR = "\n-- THE RUNNER. The air-drop sections always run;"
assert src.count(RUNNER_ANCHOR) == 1
src = src.replace(RUNNER_ANCHOR, "\n" + SECTION + RUNNER_ANCHOR)
assert src.count("\nrun_h180()\n") == 1
src = src.replace("\nrun_h180()\n", "\nrun_h180()\nrun_h181()\n")
src = BANNER + src
assert "\u2014" not in BANNER + SECTION
os.makedirs(os.path.dirname(DST), exist_ok=True)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST, len(src), "bytes")
