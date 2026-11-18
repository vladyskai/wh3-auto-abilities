#!/usr/bin/env python3
"""Build harness178.lua from harness177.lua for round 179 (the score-3 review, rows 115-134). Older harnesses are never
edited.

Rebases: see R (each names the pin and why)."""
import os

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261118_score3_rows2_harness177\harness177.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261118_score3_rows3_harness178\harness178.lua"
SECTION = open(r"C:\Users\vlady\Desktop\WH3_mod\tools\h178_section.lua", encoding="utf-8").read()
BANNER = """-- ============================================================================
-- HARNESS 178 - ROUND 179: THE SCORE-3 REVIEW, ROWS 115-134 (6 new families, 12 entries
--   moved, Grut's Sickle on low winds, the wavering pair without its melee condition).
--   Edited vs harness177: this banner, the rebases listed in tools/make_harness178.py,
--   run_h178 and its call.
--   RED control: H178_LIVE / H178_ANN on docs/backups/round179/pre179_*.lua.
-- ============================================================================
"""
LABELS = (
    '    ally_charge_or_melee = "When armed, fires on the nearest ally charging, else just in contact, else in melee (never a missile unit)",\n'
    '    ally_melee_wavering_first = "When armed, fires on the nearest ally in melee, a wavering one first",\n'
    '    ally_value_melee = "When armed, fires on the most valuable ally in melee (never a missile unit)",\n'
    '    ally_in_melee = "When armed, fires on the nearest ally in melee",\n'
    '    health_aura_ally_deep = "When armed, fires when this unit or a friendly unit in range is at or below 55% health, cast on it",\n'
    '    heal_ground_best = "When armed, fires on the ground under the hurt unit (75% or less) with the most hurt units around it",\n')
DAB_OLD = 'local DAB   = { key = "wh3_dlc26_character_abilities_da_boss_as_a_plan", marker = "da_boss_as_a_plan", bound = 105 }'
R = [
    # the TIP mirror: the 6 new labels; Grut's Sickle's label
    ('    enemy_most_models = "When armed and standing still, fires on the enemy unit in range with the most soldiers (16 at least)",\n',
     '    enemy_most_models = "When armed and standing still, fires on the enemy unit in range with the most soldiers (16 at least)",\n'
     '    -- HARNESS 178: the round-179 labels\n' + LABELS, 1),
    ('    ally_winds = "When armed, fires on the ally with the most hit points remaining, cast on that ally",\n',
     '    ally_winds = "When armed and the winds run low, fires on the expendable ally with the most hit points, else on the cheapest ally above 75% health",   -- HARNESS 178\n', 1),
    # the counts the 12 moves change
    ("""'trigger = "ally_melee_buff"') == 11""", """'trigger = "ally_melee_buff"') == 1""", 2),
    ("""'trigger = "health_aura_ally"') == 9""", """'trigger = "health_aura_ally"') == 8""", 5),
    ("""'trigger = "health_aura_ground"') == 3""", """'trigger = "health_aura_ground"') == 2""", 5),
    ("""'trigger = "melee_self_or_ally"') == 1""", """'trigger = "melee_self_or_ally"') == 2""", 1),
    ('ally_range_real = ") == 62', 'ally_range_real = ") == 63', 3),   # + Star of Avelorn (its 200 m cast range)
    ('start_armed = true,\\n") == 21', 'start_armed = true,\\n") == 33', 2),   # the 12 moved entries keep their default
    # h98 AB worlds: Da Boss left ally_melee_buff; Daemonic Whispers (the family's last entry, 140 m bound) stands in
    (DAB_OLD, 'local DAB   = { key = "wh3_dlc27_character_abilities_slezuzus_voice", marker = "slezuzus_voice", bound = 140 }   -- HARNESS 178: Da Boss moved', 1),
    ('"AB-U3: an ally BEYOND the 105 m bound stays SILENT though the engine said in-range",\n'
     '      key = DAB.key, marker = DAB.marker, cuid = 9904, auid = 9905, cmelee = true, adist = 130, expect = "silent" })',
     '"AB-U3: an ally BEYOND the 140 m bound stays SILENT though the engine said in-range",\n'
     '      key = DAB.key, marker = DAB.marker, cuid = 9904, auid = 9905, cmelee = true, adist = 160, expect = "silent" })', 1),
    # h99 GS1/GS2: Grut's Sickle waits for low winds now (round 179; its firing worlds are h178 GR2, GR3)
    ('"GS1: Grut\'s Sickle picks the ally with the HIGHEST hit points",', '"GS1: Grut\'s Sickle with NO winds read stays SILENT (two allies)",', 1),
    ('    expect = "fire_ally", target = 9752 }) end)', '    expect = "silent" }) end)   -- HARNESS 178: low winds needed', 1),
    ('"GS2: Grut\'s Sickle CASTS ON A LONE ally",', '"GS2: Grut\'s Sickle with NO winds read stays SILENT (a lone ally)",', 1),
    ('    expect = "fire_ally", target = 9754 }) end)', '    expect = "silent" }) end)   -- HARNESS 178: low winds needed', 1),
    # h104 S-worlds: Star of Avelorn reaches its 140 m cast bound now and logs the spot (round 179)
    ('"star_of_avelorn ally: \'swordsmen\' is the chosen unit (health 60%, distance 7.0m of 10m aura) - cast on the ground under that ally"',
     '"star_of_avelorn ally: \'swordsmen\' is the chosen spot (health 60%, distance 7.0m of 140m cast bound, 0 other hurt unit(s) within 10m) - cast on the ground under that ally"', 1),
    ('"reason: star_of_avelorn: lowest-health unit in the aura is an ALLY at 60% (<= 75%), distance 7.0 of 10m aura - cast under the ally"',
     '"reason: heal spot: an ally at 60% (<= 75%), 0 other hurt unit(s) within 10m, distance 7.0 of 140m - cast under the ally"', 1),
    ('      check("S3: a 60% ally at 12 m is OUTSIDE the 10 m aura - nothing fires ("\n'
     '        .. #W.ground_fires .. " ground, " .. #W.fires .. " unit)",\n'
     '        #W.ground_fires == 0 and #W.fires == 0)',
     '      check("S3: a 60% ally at 12 m is inside the 140 m cast bound - ONE ground cast (HARNESS 178) ("\n'
     '        .. #W.ground_fires .. " ground, " .. #W.fires .. " unit)",\n'
     '        #W.ground_fires == 1 and #W.fires == 0)', 1),
    ('lg104(count_log(W, "reason: health 60% (<= 75%)") == 1))',
     'lg104(count_log(W, "reason: heal spot: the caster at 60% (<= 75%), 0 other hurt unit(s) within 10m - cast at its feet") == 1))   -- HARNESS 178', 1),
    ('dist_seq = { 7, 15 } } },', 'dist_seq = { 7, 150 } } },   -- HARNESS 178: past the 140 m cast bound', 1),
    ('"S11a: the pre-cast re-check refuses a chosen ally that drifted to 15 m ("',
     '"S11a: the pre-cast re-check refuses a chosen ally that drifted to 150 m ("', 1),
]
# the suite boundaries after the h99 worlds: GS1 and GS2 went from 2 checks to 1 in both files (-4)
for old, new, var in ((3433, 3429, "pre102"), (3516, 3512, "pre103"), (3560, 3556, "pre104"), (3641, 3637, "pre105"),
                      (3693, 3689, "pre106"), (3803, 3799, "pre107"), (4480, 4476, "pre114")):
    R.append(('.. %s .. ", want %d)", %s == %d)   -- HARNESS 173: CG9 -2' % (var, old, var, old),
              '.. %s .. ", want %d)", %s == %d)   -- HARNESS 178: GS1/GS2 -4' % (var, new, var, new), 1))
R.append(('.. pre115 .. ")", pre115 == 4602)   -- HARNESS 173: CG9 -2', '.. pre115 .. ")", pre115 == 4598)   -- HARNESS 178: GS1/GS2 -4', 1))
for old, new, var, lo in ((4674, 4670, "pre116", 200), (4690, 4686, "pre117", 250), (4706, 4702, "pre118", 250)):
    R.append(('.. %s .. ")", (LIGHT and (%s >= %d)) or (%s == %d))   -- HARNESS 173: CG9 -2' % (var, var, lo, var, old),
              '.. %s .. ")", (LIGHT and (%s >= %d)) or (%s == %d))   -- HARNESS 178: GS1/GS2 -4' % (var, var, lo, var, new), 1))
src = open(SRC, encoding="utf-8").read()
for a, b, n in R:
    assert src.count(a) == n, (a[:80], src.count(a))
    src = src.replace(a, b)
RUNNER_ANCHOR = "\n-- THE RUNNER. The air-drop sections always run;"
assert src.count(RUNNER_ANCHOR) == 1
src = src.replace(RUNNER_ANCHOR, "\n" + SECTION + RUNNER_ANCHOR)
assert src.count("\nrun_h177()\n") == 1
src = src.replace("\nrun_h177()\n", "\nrun_h177()\nrun_h178()\n")
src = BANNER + src
assert "\u2014" not in BANNER + SECTION
os.makedirs(os.path.dirname(DST), exist_ok=True)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST, len(src), "bytes")
