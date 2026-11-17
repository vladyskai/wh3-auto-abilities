#!/usr/bin/env python3
"""Build harness167.lua from harness166.lua for round 168 (the cast animation decides the stand-still rule; the older
pickers skip hidden enemies). Older harnesses are never edited.

Rebases (user ruling 2026-11-17, "Option A, animation decides all"):
  * h149 MV1 (Fireball while the caster moves): GREEN 0 -> 1. Fireball has no cast animation (wind_up_stance empty),
    so its cast does not stop the caster and may fire on the move. The animated case is harness 167 AN1.
  * h161 WV4 (Wrath of Manann, the caster moving): GREEN 0 -> 1, the same reason (no cast animation).
  * h165 SC2 (Banishment's card): 'Fires when it and the target stand still' -> 'Fires when the target stands still'
    (Banishment has no cast animation).
"""
import os

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261117_periods_risky_harness166\harness166.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261117_anim_visibility_harness167\harness167.lua"
SECTION = open(r"C:\Users\vlady\Desktop\WH3_mod\tools\h167_section.lua", encoding="utf-8").read()
BANNER = """-- ============================================================================
-- HARNESS 167 - ROUND 168: THE CAST ANIMATION DECIDES THE STAND-STILL RULE, AND
--   THE OLDER ENEMY PICKERS SKIP HIDDEN ENEMIES.
--   Edited vs harness166: this banner, the rebases listed in tools/make_harness167.py
--   (MV1, WV4, SC2 Banishment), run_h167 and its call.
--   RED control: H167_LIVE / H167_ANN on docs/backups/round168/pre168_*.lua.
-- ============================================================================
"""
R = [
    ('    { "MV1. Fireball while the caster MOVES -> no cast",\n'
     '      function(b) return { caster(b, FB, true) }, { block(b + 5, GG, 120, 0, 150) }, { [tostring(b + 5)] = 850 } end,\n'
     '      "spell_bound_fireball", FB, 0, 1, nil, 5 },\n',
     '    { "MV1. Fireball while the caster MOVES -> ONE cast (HARNESS 167: no cast animation, the cast does not stop it)",\n'
     '      function(b) return { caster(b, FB, true) }, { block(b + 5, GG, 120, 0, 150) }, { [tostring(b + 5)] = 850 } end,\n'
     '      "spell_bound_fireball", FB, 1, 1, 5, 5 },\n'),
    ('    { "WV4. Wrath of Manann: the caster is moving -> no cast",\n'
     '      function(b) return { caster(b, WM, { moving = true }) }, { block(b + 5, GG, 0, 60) },\n'
     '        { [tostring(b + 5)] = 800 } end, "wrath_of_manann", WM, 0, nil, nil },\n',
     '    { "WV4. Wrath of Manann: the caster is moving -> ONE cast (HARNESS 167: no cast animation)",\n'
     '      function(b) return { caster(b, WM, { moving = true }) }, { block(b + 5, GG, 0, 60) },\n'
     '        { [tostring(b + 5)] = 800 } end, "wrath_of_manann", WM, 1, nil, nil },\n'),
    ('        and by.banishment == "Fires when it and the target stand still, where the blast hurts the enemy most, clear of allies"\n',
     '        and by.banishment == "Fires when the target stands still, where the blast hurts the enemy most, clear of allies"   -- HARNESS 167\n'),
]
src = open(SRC, encoding="utf-8").read()
for a, b in R:
    assert src.count(a) == 1, (a[:80], src.count(a))
    src = src.replace(a, b)
RUNNER_ANCHOR = "\n-- THE RUNNER. The air-drop sections always run;"
assert src.count(RUNNER_ANCHOR) == 1
src = src.replace(RUNNER_ANCHOR, "\n" + SECTION + RUNNER_ANCHOR)
assert src.count("\nrun_h166()\n") == 1
src = src.replace("\nrun_h166()\n", "\nrun_h166()\nrun_h167()\n")
src = BANNER + src
assert "\u2014" not in BANNER + SECTION
os.makedirs(os.path.dirname(DST), exist_ok=True)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST, len(src), "bytes")
