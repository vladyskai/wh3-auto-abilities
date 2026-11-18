#!/usr/bin/env python3
"""Build harness171.lua from harness170.lua for round 172 (rows 1, 3 and 5 of the low score review as RULED in the doc).
Older harnesses are never edited.

Rebases (every one follows the doc's rulings on purpose):
  * h93 TIP mirror: army_charge and aura_charge get their new labels; the new army_charge_or_melee label is added;
  * h170 AC2 'the caster and 1 ally charging -> no cast': under the ruling an army of 2 now fires ("every living unit of
    ours when the army has fewer than 3"), so the world gets a third, idle unit and keeps its meaning (2 of 3 charging
    -> no cast);
  * h170 CA2: the Horn and Ursun's Roar cards carry their new sentences.
"""
import os

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261117_review_rows_harness170\harness170.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261118_ruled_rows_harness171\harness171.lua"
SECTION = open(r"C:\Users\vlady\Desktop\WH3_mod\tools\h171_section.lua", encoding="utf-8").read()
BANNER = """-- ============================================================================
-- HARNESS 171 - ROUND 172: ROWS 1, 3 AND 5 OF THE LOW SCORE REVIEW AS RULED IN THE DOC
--   (Horn of the Wild Hunt: every living unit in a smaller army; Waaagh!: army charge OR
--   army melee; Ursun's Roar: one unit charging or wavering).
--   Edited vs harness170: this banner, the rebases listed in tools/make_harness171.py,
--   run_h171 and its call.
--   RED control: H171_LIVE / H171_ANN on docs/backups/round172/pre172_*.lua.
-- ============================================================================
"""
R = [
    ('    army_charge = "When armed, fires when 3 or more of our units charge or have just made contact",\n'
     '    aura_charge = "When armed, fires when this unit, or 2 or more units in its aura, charge or have just made contact",\n',
     '    -- HARNESS 171: the round-172 labels (the doc\'s rulings)\n'
     '    army_charge = "When armed, fires when 3 or more of our units (every unit in a smaller army) charge or have just made contact",\n'
     '    army_charge_or_melee = "When armed, fires when 3 or more of our units (every unit in a smaller army) charge, have just made contact, or fight in melee",\n'
     '    aura_charge = "When armed, fires when this unit or a unit in its aura charges, has just made contact, or wavers",\n', 1),
    ('    { "AC2. Horn: the caster and 1 ally charging -> no cast",\n'
     '      function(b) return { caster(b, HORN, CH), ally(b + 1, CH) } end, "horn_of_the_wild_hunt", HORN, 0, 0 },\n',
     '    -- HARNESS 171: a third, idle unit (an army of 2 now fires under the ruling: every living unit)\n'
     '    { "AC2. Horn: the caster and 1 ally charging, a third unit idle -> no cast",\n'
     '      function(b) return { caster(b, HORN, CH), ally(b + 1, CH), ally(b + 2) } end, "horn_of_the_wild_hunt", HORN, 0, 0 },\n', 1),
    ('          local c_ok = by.horn_of_the_wild_hunt == "Fires when 3+ of your units charge at once"\n'
     '            and by.ursuns_roar_charge == "Fires when charging, or when 2+ nearby allies charge"\n',
     '          -- HARNESS 171: the Horn and Ursun\'s Roar cards follow the round-172 rulings\n'
     '          local c_ok = by.horn_of_the_wild_hunt == "Fires when 3+ of your units charge at once (all of them in a smaller army)"\n'
     '            and by.ursuns_roar_charge == "Fires when it or a nearby ally charges or wavers"\n', 1),
]
src = open(SRC, encoding="utf-8").read()
for a, b, n in R:
    assert src.count(a) == n, (a[:70], src.count(a))
    src = src.replace(a, b)
RUNNER_ANCHOR = "\n-- THE RUNNER. The air-drop sections always run;"
assert src.count(RUNNER_ANCHOR) == 1
src = src.replace(RUNNER_ANCHOR, "\n" + SECTION + RUNNER_ANCHOR)
assert src.count("\nrun_h170()\n") == 1
src = src.replace("\nrun_h170()\n", "\nrun_h170()\nrun_h171()\n")
src = BANNER + src
assert "\u2014" not in BANNER + SECTION
os.makedirs(os.path.dirname(DST), exist_ok=True)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST, len(src), "bytes")
