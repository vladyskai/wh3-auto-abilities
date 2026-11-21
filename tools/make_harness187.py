#!/usr/bin/env python3
"""Build harness187.lua from harness186.lua for round 188 (the range rule: every cast-range bound is
max(floor(real x 0.70), real - 20 m); user ruling 2026-11-21). Older harnesses are never edited.

Rebases (R): every pin that named an old 70% bound now names the new one, and every edge world keeps its meaning
by moving its distance to just past (or just inside) the NEW bound:
  - the named bounds: Blood Sacrifice / Eat da Runts! 70 -> 80, Accusation 52 -> 55 (0p, 0r, 0s, 0t, R4b, R4c,
    the harness-95 boundary worlds B1/B2/E1/E2/A1, P4 71 -> 81 m, the P5/P9 drift 80 -> 90 m);
  - the cast constants: the harness-97 list (0u) and its FAM worlds, the harness-98 ally list (0v, its 70% formula
    becomes the new rule), R200 ally 140 -> 180 (0w, AB-U3 at 200 m, Star of Avelorn S1c/S1d/S11 at 190 m),
    R300 210 -> 280 (0x), R250 175 -> 230 (0zm, 0zr), R600 420 -> 580 (0zr), R120 84 -> 100 (0zz3);
  - the edge worlds: W7 bound=80m, F3 Assault of Stone 190 m (bound 180), the harness-122 EM table (no_escape and
    transfix 80, flash_bomb 55), Restock R2 90 m, Deranged Munitions D3 90 m, Seerstaff S2 190 m, Terrorgheist
    Skull T2 90 m, Eat da Runts! ED3 85 m (each real range 100 or 200 m, bound 80 or 180 m).
New: run_h187 (tools/h187_section.lua)."""
import os

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261121_uiscale_harness186\harness186.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261121_rangerule_harness187\harness187.lua"
SECTION = open(r"C:\Users\vlady\Desktop\WH3_mod\tools\h187_section.lua", encoding="utf-8").read()
BANNER = """-- ============================================================================
-- HARNESS 187 - ROUND 188: THE RANGE RULE (user ruling 2026-11-21: "C. Your rule, the larger of 70% and
--   real minus 20 m, everywhere."). Every cast-range bound is max(floor(real x 0.70), real - 20).
--   Edited vs harness186: this banner, the rebases listed in tools/make_harness187.py,
--   run_h187 and its call.
--   RED control: H187_LIVE / H187_ANN on docs/backups/round188/pre188_*.lua.
-- ============================================================================
"""
R = [
    # the named bounds (tokens)
    ('"FOURTH.BLOOD_SACRIFICE_RANGE_M = 70"', '"FOURTH.BLOOD_SACRIFICE_RANGE_M = 80"', 2),
    ('"FOURTH.EAT_DA_RUNTS_RANGE_M = 70"', '"FOURTH.EAT_DA_RUNTS_RANGE_M = 80"', 2),
    ('"FOURTH.ACCUSATION_RANGE_M = 52"', '"FOURTH.ACCUSATION_RANGE_M = 55"', 3),
    ('the 70% named range constants exist (70 m each)', 'the named range constants exist (80 m each, ROUND 188)', 1),
    ('the 70% named range constant exists (52 m)', 'the named range constant exists (55 m, ROUND 188)', 1),
    ('BLOOD SACRIFICE = 70 (100 * 0.70)', 'BLOOD SACRIFICE = 80 (ROUND 188: 100 - 20)', 1),
    ('EAT DA RUNTS = 70 (100 * 0.70)', 'EAT DA RUNTS = 80 (ROUND 188: 100 - 20)', 1),
    ('ACCUSATION = 52 (75 * 0.70, floored)', 'ACCUSATION = 55 (ROUND 188: 75 - 20)', 1),
    ('(the 52 m 70% value)', '(the 55 m bound, ROUND 188)', 1),
    ('bound=52m', 'bound=55m', 4),
    ('and the 52 m bound [live log]', 'and the 55 m bound [live log]', 1),
    # the harness-95 boundary worlds
    ('run_all(world_bs,  70, true,  "B1")   -- just inside 70 -> FIRES',
     'run_all(world_bs,  80, true,  "B1")   -- just inside 80 (ROUND 188) -> FIRES', 1),
    ('run_all(world_bs,  71, false, "B2")   -- between 70 and 100 -> SILENT',
     'run_all(world_bs,  81, false, "B2")   -- between 80 and 100 (ROUND 188) -> SILENT', 1),
    ('run_all(world_ed,  70, true,  "E1")', 'run_all(world_ed,  80, true,  "E1")', 1),
    ('run_all(world_ed,  71, false, "E2")', 'run_all(world_ed,  81, false, "E2")', 1),
    ('run_all(world_acc, 52, true,  "A1")   -- just inside 52 -> FIRES',
     'run_all(world_acc, 55, true,  "A1")   -- just inside 55 (ROUND 188) -> FIRES', 1),
    ('(bound 70) ==', '(bound 80) ==', 2),
    ('(bound 52) ==', '(bound 55) ==', 1),
    # the harness-92 worlds
    ('health_percent = 40, dist = 71 }', 'health_percent = 40, dist = 81 }', 1),
    ('P4. BLOOD SACRIFICE: the ally is at 71 m -> SILENT', 'P4. BLOOD SACRIFICE: the ally is at 81 m -> SILENT', 1),
    ('P4a: the 71 m ally is OUT of the 70 m trigger range', 'P4a: the 81 m ally is OUT of the 80 m trigger range', 1),
    ('dist_seq = { 15, 80 }', 'dist_seq = { 15, 90 }', 2),
    # the harness-97 constants and FAM worlds
    ('{"FOURTH.ENEMY_CAST_R70  = 49", "70", "49"}', '{"FOURTH.ENEMY_CAST_R70  = 50", "70", "50"}', 1),
    ('{"FOURTH.ENEMY_CAST_R75  = 52", "75", "52"}', '{"FOURTH.ENEMY_CAST_R75  = 55", "75", "55"}', 1),
    ('{"FOURTH.ENEMY_CAST_R100 = 70", "100", "70"}', '{"FOURTH.ENEMY_CAST_R100 = 80", "100", "80"}', 1),
    ('{"FOURTH.ENEMY_CAST_R150 = 105", "150", "105"}', '{"FOURTH.ENEMY_CAST_R150 = 130", "150", "130"}', 1),
    ('{"FOURTH.ENEMY_CAST_R180 = 126", "180", "126"}', '{"FOURTH.ENEMY_CAST_R180 = 160", "180", "160"}', 1),
    ('{"FOURTH.ENEMY_CAST_R200 = 140", "200", "140"}', '{"FOURTH.ENEMY_CAST_R200 = 180", "200", "180"}', 1),
    ('{"FOURTH.ENEMY_CAST_R500 = 350", "500", "350"}', '{"FOURTH.ENEMY_CAST_R500 = 480", "500", "480"}', 1),
    ('{ real = 100, bound = 70,  marker = "dispatch_the_swarm_attack"', '{ real = 100, bound = 80,  marker = "dispatch_the_swarm_attack"', 1),
    ('{ real = 70,  bound = 49,  marker = "oil_flask"', '{ real = 70,  bound = 50,  marker = "oil_flask"', 1),
    ('{ real = 75,  bound = 52,  marker = "accusation"', '{ real = 75,  bound = 55,  marker = "accusation"', 1),
    ('{ real = 100, bound = 70,  marker = "blade_of_setep"', '{ real = 100, bound = 80,  marker = "blade_of_setep"', 1),
    ('{ real = 150, bound = 105, marker = "headhunt"', '{ real = 150, bound = 130, marker = "headhunt"', 1),
    ('{ real = 180, bound = 126, marker = "mark_of_yin"', '{ real = 180, bound = 160, marker = "mark_of_yin"', 1),
    ('{ real = 200, bound = 140, marker = "acquiescence"', '{ real = 200, bound = 180, marker = "acquiescence"', 1),
    ('{ real = 100, bound = 70,  marker = "amulet_of_phastah"', '{ real = 100, bound = 80,  marker = "amulet_of_phastah"', 1),
    ('{ real = 500, bound = 350, marker = "tricksters_shard"', '{ real = 500, bound = 480, marker = "tricksters_shard"', 1),
    ('all 12 named 70% enemy-cast constants are present with their values',
     'all 12 named enemy-cast constants are present with their values (ROUND 188 rule)', 1),
    # the harness-98 ally constants
    ('{ "FOURTH.ALLY_CAST_R75  = 52", 75, 52 }, { "FOURTH.ALLY_CAST_R100 = 70", 100, 70 },',
     '{ "FOURTH.ALLY_CAST_R75  = 55", 75, 55 }, { "FOURTH.ALLY_CAST_R100 = 80", 100, 80 },', 1),
    ('{ "FOURTH.ALLY_CAST_R150 = 105", 150, 105 } }', '{ "FOURTH.ALLY_CAST_R150 = 130", 150, 130 } }', 1),
    ('if math.floor(CONSTS[i][2] * 0.70 + 1e-9) ~= CONSTS[i][3] then allc = false end',
     'if math.max(math.floor(CONSTS[i][2] * 0.70 + 1e-9), CONSTS[i][2] - 20) ~= CONSTS[i][3] then allc = false end   -- ROUND 188', 1),
    ('all 5 named 70% ally-cast constants are present with their values',
     'all 5 named ally-cast constants are present with their values (ROUND 188 rule)', 1),
    ('marker = "slezuzus_voice", bound = 140 }', 'marker = "slezuzus_voice", bound = 180 }', 1),
    ('AB-U3: an ally BEYOND the 140 m bound stays SILENT', 'AB-U3: an ally BEYOND the 180 m bound stays SILENT', 1),
    ('cuid = 9904, auid = 9905, cmelee = true, adist = 160,', 'cuid = 9904, auid = 9905, cmelee = true, adist = 200,', 1),
    # 0w, W7, Star of Avelorn
    ('FOURTH.ALLY_CAST_R200 = 140', 'FOURTH.ALLY_CAST_R200 = 180', 2),
    ('the 70% bound of the 100 m row is logged as 70m', 'the bound of the 100 m row is logged as 80m (ROUND 188)', 1),
    ('count_log(W, "bound=70m") >= 1)', 'count_log(W, "bound=80m") >= 1)', 1),
    ('distance 7.0m of 140m cast bound', 'distance 7.0m of 180m cast bound', 1),
    ('distance 7.0 of 140m - cast under the ally', 'distance 7.0 of 180m - cast under the ally', 1),
    ('dist_seq = { 7, 150 } } },   -- HARNESS 178: past the 140 m cast bound',
     'dist_seq = { 7, 190 } } },   -- HARNESS 187: past the 180 m cast bound (round 188)', 1),
    ('a chosen ally that drifted to 150 m (', 'a chosen ally that drifted to 190 m (', 1),
    # 0x, F3
    ('the 300 m range maps to the 210 m bound (the 70% rule)', 'the 300 m range maps to the 280 m bound (ROUND 188 rule)', 1),
    ('FOURTH.ENEMY_CAST_R300 = 210', 'FOURTH.ENEMY_CAST_R300 = 280', 1),
    ('-- F3: the only infantry is BEYOND the 70% bound (140 m of the real 200).',
     '-- F3: the only infantry is BEYOND the bound (180 m of the real 200, round 188).', 1),
    ('dist_by_target = { [11621] = 150.0 } }', 'dist_by_target = { [11621] = 190.0 } }', 1),
    ('F3a: 150 m is outside the 140 m bound', 'F3a: 190 m is outside the 180 m bound', 1),
    # the harness-122 EM table
    ('{ "no_escape", "wh3_main_character_abilities_no_escape", 70 },', '{ "no_escape", "wh3_main_character_abilities_no_escape", 80 },', 1),
    ('{ "transfix_hex", "wh3_dlc29_lord_abilities_transfix", 70 },', '{ "transfix_hex", "wh3_dlc29_lord_abilities_transfix", 80 },', 1),
    ('{ "flash_bomb", "wh_pro01_lord_abilities_flash_bomb", 52 },', '{ "flash_bomb", "wh_pro01_lord_abilities_flash_bomb", 55 },', 1),
    # harness 129-131, 140, 179 edge worlds
    ('a shooting 60% ally at 80 m -> no cast', 'a shooting 60% ally at 90 m -> no cast', 1),
    ('shooter(HG, 13013, 100, 60, 80)', 'shooter(HG, 13013, 100, 60, 90)', 1),
    ('the only shooting ally is 80 m away (bound 70 m) -> no cast', 'the only shooting ally is 90 m away (bound 80 m) -> no cast', 1),
    ('shooter(HG, 13152, 80)', 'shooter(HG, 13152, 90)', 1),
    ('the in-melee ally is 150 m away -> no cast', 'the in-melee ally is 190 m away -> no cast', 1),
    ('owns = {}, melee = true, dist = 150 } },', 'owns = {}, melee = true, dist = 190 } },', 1),
    ('T2. Terrorgheist Skull: the ally in melee is 80 m away -> no cast', 'T2. Terrorgheist Skull: the ally in melee is 90 m away -> no cast', 1),
    ('owns = {}, melee = true, dist = 80 } } end,', 'owns = {}, melee = true, dist = 90 } } end,', 1),
    ('a healthy ally 75 m away -> no cast",', 'a healthy ally 85 m away -> no cast",', 1),
    ('ally(b + 5, SW, { dist = 75 })', 'ally(b + 5, SW, { dist = 85 })', 1),
    ('a healthy ally 75 m away (beyond 70 m) -> no cast', 'a healthy ally 85 m away (beyond 80 m) -> no cast', 1),
    # the later token sections
    ('FOURTH.ALLY_CAST_R250 = 175', 'FOURTH.ALLY_CAST_R250 = 230', 1),
    ('FOURTH.ENEMY_CAST_R250 = 175', 'FOURTH.ENEMY_CAST_R250 = 230', 1),
    ('"FOURTH.ENEMY_CAST_R120 = 84 "', '"FOURTH.ENEMY_CAST_R120 = 100 "', 1),
    ('FOURTH.ENEMY_CAST_R600 = 420', 'FOURTH.ENEMY_CAST_R600 = 580', 1),
]
src = open(SRC, encoding="utf-8").read()
for a, b, n in R:
    assert src.count(a) == n, (a[:80], src.count(a))
    src = src.replace(a, b)
RUNNER_ANCHOR = "\n-- THE RUNNER. The air-drop sections always run;"
assert src.count(RUNNER_ANCHOR) == 1
src = src.replace(RUNNER_ANCHOR, "\n" + SECTION + RUNNER_ANCHOR)
assert src.count("\nrun_h186()\n") == 1
src = src.replace("\nrun_h186()\n", "\nrun_h186()\nrun_h187()\n")
src = BANNER + src
assert "\u2014" not in BANNER + SECTION
os.makedirs(os.path.dirname(DST), exist_ok=True)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST, len(src), "bytes")
