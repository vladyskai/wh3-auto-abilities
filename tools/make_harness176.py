#!/usr/bin/env python3
"""Build harness176.lua from harness175.lua for round 177 (the score-3 review, rows 1-22). Older harnesses are never
edited.

Rebases: see R (each names the pin and why)."""
import os

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261118_mists_armed_harness175\harness175.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261118_score3_rows_harness176\harness176.lua"
SECTION = open(r"C:\Users\vlady\Desktop\WH3_mod\tools\h176_section.lua", encoding="utf-8").read()
BANNER = """-- ============================================================================
-- HARNESS 176 - ROUND 177: THE SCORE-3 REVIEW, ROWS 1-22 (9 new families, the squig set,
--   15 entries moved).
--   Edited vs harness175: this banner, the rebases listed in tools/make_harness176.py,
--   run_h176 and its call.
--   RED control: H176_LIVE / H176_ANN on docs/backups/round177/pre177_*.lua.
-- ============================================================================
"""
LABELS = (
    '    slow_army = "When armed, fires when a fast enemy closes on any of our units, or this unit is in melee",\n'
    '    melee_vs_large = "When armed, fires when this unit or one in its aura is fighting a large enemy",\n'
    '    ally_squig_melee = "When armed, fires on the nearest squig ally in melee",\n'
    '    enemy_melee_near = "When armed, fires when this unit, or an enemy in its aura, is in melee",\n'
    '    aura_charge_or_melee = "When armed, fires when this unit or a unit in its aura charges, has just made contact, or fights",\n'
    '    melee_health25 = "When armed, fires in melee at or below 25% health",\n'
    '    guard_aura = "When armed, fires in melee or under missile fire, or when a fast enemy enters the aura",\n'
    '    self_or_ally_fire_melee = "When armed, fires on this unit in melee or under fire, else on an ally under fire, else on an ally in melee",\n'
    '    melee_healthy = "When armed, fires in melee while above 50% health",\n')
R = [
    ('    ally_routing = "When armed, fires on the most valuable routing ally",\n',
     '    ally_routing = "When armed, fires on the most valuable routing ally",\n'
     '    -- HARNESS 176: the round-177 labels\n' + LABELS, 1),
    # the counts the 15 moved entries change
    ("== 280", "== 265", 15),
    ("mu = 280,", "mu = 265,", 2),
    ('start_armed = true,\\n") == 9', 'start_armed = true,\\n") == 21', 2),
    ('ally_range_real = ") == 59', 'ally_range_real = ") == 62', 3),
    # h82 C-worlds and C8, h83 S1: three of their plain in-melee examples left melee_unwavering (Creature-Killer,
    # Everyone Has Their Price, Fury of the Land); clean in-melee stand-ins keep the worlds' meaning
    ('    { "creature_killer", { "wh2_dlc16_weapon_abilities_creature_killer" } },\n',
     '    { "banespear", { "wh3_main_weapon_abilities_banespear" } },   -- HARNESS 176: Creature-Killer moved (round 177)\n', 1),
    ('owns = { KEY_OF["creature_killer"] }', 'owns = { KEY_OF["banespear"] }', 1),
    ('{ id = "b4", key = KEY_OF["creature_killer"] },', '{ id = "b4", key = KEY_OF["banespear"] },', 1),
    ('"darkwalker", "creature_killer", "daemonshield" }', '"darkwalker", "banespear", "daemonshield" }', 1),
    ('    { "everyone_has_their_price", "wh3_main_lord_abilities_everyone_has_their_price" },\n',
     '    { "drakwald_runefang", "wh2_dlc13_weapon_abilities_drakwald_runefang" },   -- HARNESS 176: stand-in (round 177)\n', 1),
    ('    { "fury_of_the_land", "wh3_dlc24_character_abilities_fury_of_the_land" },\n',
     '    { "dragons_fang", "wh3_dlc24_weapon_abilities_dragons_fang" },   -- HARNESS 176: stand-in (round 177)\n', 1),
]
src = open(SRC, encoding="utf-8").read()
for a, b, n in R:
    assert src.count(a) == n, (a[:70], src.count(a))
    src = src.replace(a, b)
RUNNER_ANCHOR = "\n-- THE RUNNER. The air-drop sections always run;"
assert src.count(RUNNER_ANCHOR) == 1
src = src.replace(RUNNER_ANCHOR, "\n" + SECTION + RUNNER_ANCHOR)
assert src.count("\nrun_h175()\n") == 1
src = src.replace("\nrun_h175()\n", "\nrun_h175()\nrun_h176()\n")
src = BANNER + src
assert "\u2014" not in BANNER + SECTION
os.makedirs(os.path.dirname(DST), exist_ok=True)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST, len(src), "bytes")
