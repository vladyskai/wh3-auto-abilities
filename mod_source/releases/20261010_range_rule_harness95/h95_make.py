# -*- coding: utf-8 -*-
"""HARNESS 95 build: assemble harness95.lua from the SHIPPED harness94.lua.

The round-95 job: the user's STANDING 70% RANGE RULE. Adds FOURTH.RANGE_FRACTION
= 0.70 and re-derives every trigger-range constant as floor(real * 0.70). The
harness-94 pin values/labels move (GD 25->38, VM/MT/WV 25->24, BS/EDR 25->70,
ACC 75->52) and the boundary worlds that sat on the old 25 m threshold are
re-based so the suite stays consistent; a NEW section 0s proves the rule with
per-constant 70%-boundary worlds (inside fires, 70-100% silent) plus a red
control. The pre95_*.lua snapshots (written by impl95.py) are the RED target.
"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
NL = chr(10)


def read(p):
    return io.open(p, encoding="utf-8", newline="").read()


def write(p, s):
    io.open(p, "w", encoding="utf-8", newline="").write(s)


src = read(os.path.join(HERE, "harness94_base.lua"))


def sub(old, new, label, count=1):
    global src
    n = src.count(old)
    assert n == count, "patch %s: %d matches (want %d)" % (label, n, count)
    src = src.replace(old, new, count)
    print("patch %s: applied" % label)


def L(*lines):
    return NL.join(lines)


# --------------------------------------------------------------------------
# 0. env pair H94 -> H95
# --------------------------------------------------------------------------
sub(L('-- HARNESS 94 (this round): the env pair is now H94_LIVE / H94_ANN.',
      'local LIVE = os.getenv("H94_LIVE") or "C:/Users/vlady/Desktop/WH3_mod/mod_source/script/battle/mod/zz_test_deadly_onslaught.lua"',
      'local ANN  = os.getenv("H94_ANN")  or "C:/Users/vlady/Desktop/WH3_mod/docs/WH3_auto_ability_annotated.lua"',
      'local RED_MODE = (os.getenv("H94_LIVE") ~= nil) or (os.getenv("H94_ANN") ~= nil)'),
    L('-- HARNESS 95 (this round): the env pair is now H95_LIVE / H95_ANN.',
      'local LIVE = os.getenv("H95_LIVE") or "C:/Users/vlady/Desktop/WH3_mod/mod_source/script/battle/mod/zz_test_deadly_onslaught.lua"',
      'local ANN  = os.getenv("H95_ANN")  or "C:/Users/vlady/Desktop/WH3_mod/docs/WH3_auto_ability_annotated.lua"',
      'local RED_MODE = (os.getenv("H95_LIVE") ~= nil) or (os.getenv("H95_ANN") ~= nil)'),
    "P1 env")

# --------------------------------------------------------------------------
# 1. the banner
# --------------------------------------------------------------------------
sub(L('  print("   *** RED CONTROL MODE: pre-edit snapshot(s) in use - ACCUSATION ENEMY TRIGGER (harness-94)")',
      '  print("   *** checks EXPECTED to fail: the section-0r tokens (no enemy evaluator, Accusation still on")',
      '  print("   *** melee_unwavering) and the moved trigger-count pin (melee_unwavering is 481 on the snapshot,")',
      '  print("   *** 480 here). Only the SILENT N-worlds pass by design. Every earlier world passes except the")',
      '  print("   *** documented melee_unwavering pin.***")'),
    L('  print("   *** RED CONTROL MODE: pre-edit snapshot(s) in use - THE STANDING 70% RANGE RULE (harness-95)")',
      '  print("   *** checks EXPECTED to fail: the section-0s tokens (no FOURTH.RANGE_FRACTION, the old range")',
      '  print("   *** values still in place) and the half of the boundary worlds that sit INSIDE the NEW bound,")',
      '  print("   *** plus every earlier pin whose value moved (GD 25->38, VM/MT/WV 25->24, BS/EDR 25->70,")',
      '  print("   *** ACC 75->52). Every earlier WORLD passes by design.***")'),
    "P1b banner")

# --------------------------------------------------------------------------
# 2. the moved pins (labels + first raw_find token)
# --------------------------------------------------------------------------
sub(L('  print("== HARNESS 87 - section 0i: the GLORIOUS DEATH TRIGGER RANGE (25 m) in BOTH files ==")'),
    L('  print("== HARNESS 87 - section 0i: the GLORIOUS DEATH TRIGGER RANGE (70% = 38 m) in BOTH files ==")'),
    "0i print")

sub(L('    check("0i " .. nm .. ": the range constant is the tightened 25 (local GLORIOUS_DEATH_RANGE_M = 25)",',
      '      raw_find(s, "local GLORIOUS_DEATH_RANGE_M = 25", 1, true) ~= nil)'),
    L('    check("0i " .. nm .. ": the range constant is the 70% value 38 (local GLORIOUS_DEATH_RANGE_M = 38)",',
      '      raw_find(s, "local GLORIOUS_DEATH_RANGE_M = 38", 1, true) ~= nil)'),
    "0i GD pin")

sub(L('    check("0i " .. nm .. ": the constant is commented as a DELIBERATELY CONSERVATIVE trigger",',
      '      raw_find(s, "DELIBERATELY CONSERVATIVE", 1, true) ~= nil)',
      '    check("0i " .. nm .. ": the comment notes it is TIGHTER than the ability\'s 55 m wiki aura (the wiki range kept for reference)",',
      '      raw_find(s, "55 m wiki aura", 1, true) ~= nil',
      '      and raw_find(s, "Effect range: 55m", 1, true) ~= nil)'),
    L('    check("0i " .. nm .. ": the constant is commented with the STANDING 70% RANGE RULE",',
      '      raw_find(s, "THE STANDING 70% RULE", 1, true) ~= nil)',
      '    check("0i " .. nm .. ": the comment names the real 55 m game-data range and the 70% derivation",',
      '      raw_find(s, "55.0000 m = effect_range", 1, true) ~= nil',
      '      and raw_find(s, "55 * 0.70 = 38.5 -> 38", 1, true) ~= nil)'),
    "0i GD comment")

sub(L('    check("0m " .. nm .. ": the Verminking range is a DELIBERATELY CONSERVATIVE 25 m (FOURTH.VERMINKING_RANGE_M = 25)",',
      '      raw_find(s, "FOURTH.VERMINKING_RANGE_M = 25", 1, true) ~= nil)',
      '    check("0m " .. nm .. ": the range constant\'s comment names the game-data 35 m aura (the source of the number)",',
      '      raw_find(s, "effect_range =", 1, true) ~= nil',
      '      and raw_find(s, "35 m", 1, true) ~= nil)'),
    L('    check("0m " .. nm .. ": the Verminking range is the 70% value 24 m (FOURTH.VERMINKING_RANGE_M = 24)",',
      '      raw_find(s, "FOURTH.VERMINKING_RANGE_M = 24", 1, true) ~= nil)',
      '    check("0m " .. nm .. ": the range constant\'s comment names the game-data 35 m range and the 70% derivation",',
      '      raw_find(s, "35.0000 m = effect_range", 1, true) ~= nil',
      '      and raw_find(s, "35 * 0.70 = 24.5 -> 24", 1, true) ~= nil)'),
    "0m VM pin")

sub(L('    check("0m " .. nm .. ": the range is a DELIBERATELY CONSERVATIVE 25 m (FOURTH.METALLURGY_RANGE_M = 25)",',
      '      raw_find(s, "FOURTH.METALLURGY_RANGE_M = 25", 1, true) ~= nil)',
      '    check("0m " .. nm .. ": the range constant\'s comment names the game-data 35 m aura (the source of the number)",',
      '      raw_find(s, "effect_range =", 1, true) ~= nil and raw_find(s, "35 m", 1, true) ~= nil)'),
    L('    check("0m " .. nm .. ": the range is the 70% value 24 m (FOURTH.METALLURGY_RANGE_M = 24)",',
      '      raw_find(s, "FOURTH.METALLURGY_RANGE_M = 24", 1, true) ~= nil)',
      '    check("0m " .. nm .. ": the range constant\'s comment names the game-data 35 m range and the 70% derivation",',
      '      raw_find(s, "35.0000 m = effect_range", 1, true) ~= nil and raw_find(s, "35 * 0.70 = 24.5 -> 24", 1, true) ~= nil)'),
    "0m MT pin")

sub(L('    check("0n " .. nm .. ": the wavering trigger range is a DELIBERATELY CONSERVATIVE 25 m (FOURTH.WAVERING_RANGE_M = 25), "',
      '      .. "the game-data 35 m aura named in the comment",',
      '      raw_find(s, "FOURTH.WAVERING_RANGE_M = 25", 1, true) ~= nil',
      '      and raw_find(s, "effect_range", 1, true) ~= nil and raw_find(s, "35 m", 1, true) ~= nil)'),
    L('    check("0n " .. nm .. ": the wavering trigger range is the 70% value 24 m (FOURTH.WAVERING_RANGE_M = 24), "',
      '      .. "the game-data 35 m range named in the comment",',
      '      raw_find(s, "FOURTH.WAVERING_RANGE_M = 24", 1, true) ~= nil',
      '      and raw_find(s, "effect_range", 1, true) ~= nil and raw_find(s, "35.0000 m", 1, true) ~= nil)'),
    "0n WV pin")

sub(L('    check("0p " .. nm .. ": the conservative named 25 m range constants exist",',
      '      raw_find(s, "FOURTH.BLOOD_SACRIFICE_RANGE_M = 25", 1, true) ~= nil',
      '      and raw_find(s, "FOURTH.EAT_DA_RUNTS_RANGE_M = 25", 1, true) ~= nil)'),
    L('    check("0p " .. nm .. ": the 70% named range constants exist (70 m each)",',
      '      raw_find(s, "FOURTH.BLOOD_SACRIFICE_RANGE_M = 70", 1, true) ~= nil',
      '      and raw_find(s, "FOURTH.EAT_DA_RUNTS_RANGE_M = 70", 1, true) ~= nil)'),
    "0p BS/EDR pin")

sub(L('    check("0r " .. nm .. ": the conservative named range constant exists (75 m)",',
      '      raw_find(s, "FOURTH.ACCUSATION_RANGE_M = 75", 1, true) ~= nil)'),
    L('    check("0r " .. nm .. ": the 70% named range constant exists (52 m)",',
      '      raw_find(s, "FOURTH.ACCUSATION_RANGE_M = 52", 1, true) ~= nil)'),
    "0r ACC pin")

# --------------------------------------------------------------------------
# 3. re-base the worlds that sat on the OLD 25 m GD / BS / EDR thresholds
# --------------------------------------------------------------------------
# GD R6 (24 m, inside both) - label only
sub(L('  -- R6 (vi). BOUNDARY, just UNDER the gate: 24 m (one metre inside 25) -> the',
      '  --     ally IS in range and the ability FIRES. Pairs with R7 to pin the',
      '  --     threshold exactly at GLORIOUS_DEATH_RANGE_M.'),
    L('  -- R6 (vi). BOUNDARY, well UNDER the gate: 24 m (inside the 38 m bound) ->',
      '  --     the ally IS in range and the ability FIRES. Pairs with R7 to pin the',
      '  --     threshold at GLORIOUS_DEATH_RANGE_M (70% of the 55 m aura).'),
    "R6 comment")
sub(L('    print("== " .. TAG .. "R6. GLORIOUS DEATH BOUNDARY: 24m (just UNDER 25) is IN range -> FIRES == ")'),
    L('    print("== " .. TAG .. "R6. GLORIOUS DEATH BOUNDARY: 24m (inside the 38m bound) is IN range -> FIRES == ")'),
    "R6 print")
sub(L('    check(TAG .. "R6a: the ally at 24m is 1m INSIDE the 25m gate, so the owner FIRES ("'),
    L('    check(TAG .. "R6a: the ally at 24m is INSIDE the 38m gate, so the owner FIRES ("'),
    "R6a label")

# GD R7 (26 -> 39 m, now OUTSIDE the 38 m bound)
sub(L('  -- R7 (vii). BOUNDARY, just OVER the gate: 26 m (one metre outside 25) -> the',
      '  --     ally is OUT of range and the ability stays SILENT. Pairs with R6.'),
    L('  -- R7 (vii). BOUNDARY, just OVER the gate: 39 m (one metre outside 38) -> the',
      '  --     ally is OUT of range and the ability stays SILENT. Pairs with R6.'),
    "R7 comment")
sub('{ name = SL_UNIT,   uid = 9962, owns = {}, melee = true, dist = 26 }',
    '{ name = SL_UNIT,   uid = 9962, owns = {}, melee = true, dist = 39 }',
    "R7 dist")
sub(L('    print("== " .. TAG .. "R7. GLORIOUS DEATH BOUNDARY: 26m (just OVER 25) is OUT of range -> SILENT == ")'),
    L('    print("== " .. TAG .. "R7. GLORIOUS DEATH BOUNDARY: 39m (just OVER 38) is OUT of range -> SILENT == ")'),
    "R7 print")
sub(L('    check(TAG .. "R7a: the ally at 26m is 1m OUTSIDE the 25m gate, so the owner stays SILENT ("'),
    L('    check(TAG .. "R7a: the ally at 39m is 1m OUTSIDE the 38m gate, so the owner stays SILENT ("'),
    "R7a label")

# h87 headline + the run header print
sub(L('  print("== HARNESS 87 - GLORIOUS DEATH\'s TRIGGER RANGE = 25 m (conservative) ==")'),
    L('  print("== HARNESS 87 - GLORIOUS DEATH\'s TRIGGER RANGE = 38 m (70% of the 55 m aura) ==")'),
    "h87 header print")
sub(L('    check("HEADLINE (harness 87): GLORIOUS DEATH\'s trigger range is tightened from the ability\'s 55 m wiki aura to a "',
      '      .. "DELIBERATELY CONSERVATIVE 25 m (GLORIOUS_DEATH_RANGE_M), after field testing showed 55 m fired too early. "',
      '      .. "The ally arm fires only when the in-melee Slayer ally is WITHIN 25 m (R1 20 m fires; R2 55 m is silent; the "',
      '      .. "24 m/26 m BOUNDARY pair pins the threshold: 24 m fires, 26 m silent). The CLOSEST in-range Slayer is chosen "'),
    L('    check("HEADLINE (harness 87): GLORIOUS DEATH\'s trigger range is the STANDING 70% RULE value - floor(0.70 x the "',
      '      .. "ability\'s 55 m aura) = 38 m (GLORIOUS_DEATH_RANGE_M; the old field-tuned 25 m was replaced, NO exceptions). "',
      '      .. "The ally arm fires only when the in-melee Slayer ally is WITHIN 38 m (R1 20 m fires; R2 55 m is silent; the "',
      '      .. "24 m/39 m BOUNDARY pair pins the threshold: 24 m fires, 39 m silent). The CLOSEST in-range Slayer is chosen "'),
    "h87 headline")

# BS P3 (25 m, inside 70) - label/comments only
sub(L('  -- P3. BLOOD SACRIFICE, RANGE BOUNDARY (inside): the ally is exactly at the',
      '  --     25 m trigger radius -> still IN range -> FIRES.'),
    L('  -- P3. BLOOD SACRIFICE, RANGE BOUNDARY (inside): the ally is exactly at the',
      '  --     70 m trigger radius (70% of the 100 m intercept range) -> IN range -> FIRES.'),
    "P3 comment")
sub(L('    print("== " .. TAG .. "P3. BLOOD SACRIFICE: the ally is exactly at 25 m -> FIRES (boundary in) == ")'),
    L('    print("== " .. TAG .. "P3. BLOOD SACRIFICE: the ally is exactly at 70 m -> FIRES (boundary in) == ")'),
    "P3 print")
sub(L('    check(TAG .. "P3a: the 25.0 m ally is WITHIN the 25 m trigger range -> FIRES (" .. fire_detail(W) .. ")", a)'),
    L('    check(TAG .. "P3a: the 70.0 m ally is WITHIN the 70 m trigger range -> FIRES (" .. fire_detail(W) .. ")", a)'),
    "P3a label")

# BS P4 (26 -> 71 m, now OUTSIDE the 70 m bound)
sub(L('  -- P4. BLOOD SACRIFICE, RANGE BOUNDARY (outside): the ally is at 26 m -> OUT',
      '  --     of the 25 m trigger range -> SILENT.'),
    L('  -- P4. BLOOD SACRIFICE, RANGE BOUNDARY (outside): the ally is at 71 m -> OUT',
      '  --     of the 70 m trigger range -> SILENT.'),
    "P4 comment")
sub('{ name = "ally", uid = 9332, owns = {}, melee = false, health_percent = 40, dist = 26 }',
    '{ name = "ally", uid = 9332, owns = {}, melee = false, health_percent = 40, dist = 71 }',
    "P4 dist")
sub(L('    print("== " .. TAG .. "P4. BLOOD SACRIFICE: the ally is at 26 m -> SILENT (boundary out) == ")'),
    L('    print("== " .. TAG .. "P4. BLOOD SACRIFICE: the ally is at 71 m -> SILENT (boundary out) == ")'),
    "P4 print")
sub(L('    check(TAG .. "P4a: the 26 m ally is OUT of the 25 m trigger range -> NO cast (" .. fire_detail(W) .. ")", a)'),
    L('    check(TAG .. "P4a: the 71 m ally is OUT of the 70 m trigger range -> NO cast (" .. fire_detail(W) .. ")", a)'),
    "P4a label")

# BS P5 drift: out-at-cast distance must exceed the NEW 70 m bound
sub(L('  -- P5. BLOOD SACRIFICE, DRIFT: the ally is in range at DECIDE (15 m) but out',
      '  --     at CAST (60 m) -> the cast is SKIPPED rather than wasted.'),
    L('  -- P5. BLOOD SACRIFICE, DRIFT: the ally is in range at DECIDE (15 m) but out',
      '  --     at CAST (80 m, beyond the 70 m bound) -> the cast is SKIPPED not wasted.'),
    "P5 comment")
sub('{ name = "ally", uid = 9342, owns = {}, melee = false, health_percent = 40, dist_seq = { 15, 60 } }',
    '{ name = "ally", uid = 9342, owns = {}, melee = false, health_percent = 40, dist_seq = { 15, 80 } }',
    "P5 dist_seq")

# EDR P9 drift: same re-base
sub(L('  -- P9. EAT DA RUNTS!, DRIFT (ally arm): the ally is in range at DECIDE (15 m)',
      '  --     but out at CAST (60 m) -> the cast is SKIPPED.'),
    L('  -- P9. EAT DA RUNTS!, DRIFT (ally arm): the ally is in range at DECIDE (15 m)',
      '  --     but out at CAST (80 m, beyond the 70 m bound) -> the cast is SKIPPED.'),
    "P9 comment")
sub('{ name = "ally", uid = 9382, owns = {}, melee = false, health_percent = 50, dist_seq = { 15, 60 } }',
    '{ name = "ally", uid = 9382, owns = {}, melee = false, health_percent = 50, dist_seq = { 15, 80 } }',
    "P9 dist_seq")

# --------------------------------------------------------------------------
# 4. a couple of headline wordings that state a value (cosmetic, but keep true)
# --------------------------------------------------------------------------
sub('"(the owner wavering OR an in-melee wavering ally within the conservative 25 m FOURTH.WAVERING_RANGE_M - the "',
    '"(the owner wavering OR an in-melee wavering ally within the 70% value 24 m FOURTH.WAVERING_RANGE_M - the "',
    "h90 headline wavering")
sub('"`enemy_engaged_or_shot` - an enemy unit within the ability\'s conservative 75 m reach is a valid target "',
    '"`enemy_engaged_or_shot` - an enemy unit within the ability\'s 70% value 52 m reach is a valid target "',
    "h94 headline accusation")
sub('"conservative 25 m FOURTH.VERMINKING_RANGE_M (game data 35 m aura) of the owner, cast ON SELF, with the "',
    '"70% value 24 m FOURTH.VERMINKING_RANGE_M (game data 35 m aura) of the owner, cast ON SELF, with the "',
    "h88 headline verminking")
sub('"trigger casts on the CHOSEN ALLY, uses a conservative named 25 m range constant, and RE-CHECKS the gap "',
    '"trigger casts on the CHOSEN ALLY, uses the 70% named range constant (70 m), and RE-CHECKS the gap "',
    "h92 headline heals")

# --------------------------------------------------------------------------
# 4b. re-base the HARNESS-94 section's red branch (its old snapshot is now the
#     PRE-95 snapshot, which already carries the enemy evaluator -> N/A form).
# --------------------------------------------------------------------------
sub(L('  else',
      '    check("RED CONTROL (harness 94): on the pre-edit snapshot (the shipped harness-93 build: no enemy evaluator, "',
      '      .. "Accusation still on melee_unwavering = 481) the 0r section tokens fail and every FIRING N-world fires "',
      '      .. "nothing - only the SILENT worlds pass (N3/N4 both files = 4) plus the ANNOTATED leg of the lapse world N5 "',
      '      .. "(the unreadable-read world N6 fails on the snapshot too, its mock is never asked): " .. n_ok .. "/"',
      '      .. #results .. " world results pass (want 5), fires "',
      '      .. RED94.fires .. ", claims " .. RED94.claims, n_ok == 5)',
      '  end'),
    L('  else',
      '    check("RED CONTROL (harness 94): N/A for the harness-95 round - the harness-95 red snapshot (the shipped "',
      '      .. "harness-94 build) already carries the enemy evaluator, so every N-world passes by design: " .. n_ok .. "/"',
      '      .. #results .. " world results pass (want " .. #results .. "), fires "',
      '      .. RED94.fires .. ", claims " .. RED94.claims, n_ok == #results)',
      '  end'),
    "h94 red rebase")

# --------------------------------------------------------------------------
# 5. append the new HARNESS-95 section after run_h94(), and extend the tail list
# --------------------------------------------------------------------------
section = read(os.path.join(HERE, "h95_section.lua")).lstrip(NL)
sub(NL + "run_h94()" + NL,
    NL + "run_h94()" + NL + NL + section + NL,
    "P5 append section")
sub("89, 90, 91, 92 AND 93's worlds included",
    "89, 90, 91, 92, 93 AND 94's worlds included",
    "P6 tail list")

write(os.path.join(HERE, "harness95.lua"), src)
print("wrote harness95.lua", len(src), "bytes")
