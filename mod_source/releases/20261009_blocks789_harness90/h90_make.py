# -*- coding: utf-8 -*-
"""Assemble harness90.lua from the SHIPPED harness89.lua.

The round-90 job: BLOCKS 7-9 - FIVE new trigger types (charge_only,
wavering_self, wavering_self_or_ally, charge_or_wavering, wavering_ally_range)
plus the redesigned pair and 69 new entries / 73 keys. The table grows
193 -> 262 entries (199 -> 272 keys), so the table-size pins in the earlier
body sections are ADAPTED (A4 386->524, B4/H68/C6c/S1/M6 193->262, 199->272),
the one "and not routing" guard count 7 -> 8, the red aggregates re-pointed at
the new pre-edit snapshot, and a new HARNESS-90 section appended before the
final find check.
"""
import io, os

HERE = os.path.dirname(os.path.abspath(__file__))
src = io.open(os.path.join(HERE, "harness89.lua"), encoding="utf-8").read()
section = io.open(os.path.join(HERE, "h90_section.lua"), encoding="utf-8").read()

NL = chr(10)


def L(*lines):
    return NL.join(lines)


def sub(old, new, label, count=1):
    global src
    n = src.count(old)
    assert n == count, "patch %s: %d matches (want %d)" % (label, n, count)
    src = src.replace(old, new, count)
    print("patch %s: applied" % label)


# ---- P1 env
sub(L('-- HARNESS 89 (this round): the env pair is now H89_LIVE / H89_ANN.',
      'local LIVE = os.getenv("H89_LIVE") or "C:/Users/vlady/Desktop/WH3_mod/mod_source/script/battle/mod/zz_test_deadly_onslaught.lua"',
      'local ANN  = os.getenv("H89_ANN")  or "C:/Users/vlady/Desktop/WH3_mod/docs/WH3_auto_ability_annotated.lua"',
      'local RED_MODE = (os.getenv("H89_LIVE") ~= nil) or (os.getenv("H89_ANN") ~= nil)'),
    L('-- HARNESS 90 (this round): the env pair is now H90_LIVE / H90_ANN.',
      'local LIVE = os.getenv("H90_LIVE") or "C:/Users/vlady/Desktop/WH3_mod/mod_source/script/battle/mod/zz_test_deadly_onslaught.lua"',
      'local ANN  = os.getenv("H90_ANN")  or "C:/Users/vlady/Desktop/WH3_mod/docs/WH3_auto_ability_annotated.lua"',
      'local RED_MODE = (os.getenv("H90_LIVE") ~= nil) or (os.getenv("H90_ANN") ~= nil)'),
    "P1 env")

# ---- P2 banner
sub(L('  print("   *** RED CONTROL MODE: pre-edit snapshot(s) in use - the ENCHANTED METALLURGY family (harness-89)")',
      '  print("   *** checks + the ADAPTED TABLE-SIZE COUNT PINS are the ones EXPECTED to fail: the section-0m tokens,")',
      '  print("   *** the M worlds (the new entries and evaluator are simply absent on the 189-entry snapshot), and")',
      '  print("   *** the pins that now read the grown table (A4 193 per pass, B4 193, H68 193/199, C6c 193)")',
      '  print("   *** plus the run_h88 S1 world (193/199). Every earlier world passes by design.***")'),
    L('  print("   *** RED CONTROL MODE: pre-edit snapshot(s) in use - BLOCKS 7-9 (harness-90)")',
      '  print("   *** checks + the ADAPTED TABLE-SIZE COUNT PINS are the ones EXPECTED to fail: the section-0n tokens,")',
      '  print("   *** the N worlds (the new entries/evaluators are simply absent on the 193-entry snapshot), and")',
      '  print("   *** the pins that now read the grown table (A4 262 per pass, B4 262, H68 262/272, C6c 262,")',
      '  print("   *** S1 262/272, M6 262/272, 0c guards 8). Every earlier world passes by design.***")'),
    "P2 banner")

# ---- P3 the adapted count pins
sub('    a = (it == 386)', '    a = (it == 524)', "P3 A4a value")
sub('FULL 193-entry table (', 'FULL 262-entry table (', "P3 A4a text")
sub('iterations, 193 per pass - ROUND h89 grew the table again',
    'iterations, 262 per pass - ROUND h90 grew the table again', "P3 A4a tail")
sub('    b = ((it / 2) == 193)', '    b = ((it / 2) == 262)', "P3 A4b value")
sub('A4b: 193 abilities per pass, no shortened set', 'A4b: 262 abilities per pass, no shortened set', "P3 A4b text")
sub('    a = (POLL_ITERS == 193)', '    a = (POLL_ITERS == 262)', "P3 B4 value")
sub(', want 193 - the FULL 193-entry table after round h89)',
    ', want 262 - the FULL 262-entry table after round h90)', "P3 B4 text")
sub('(ABIL and #ABIL or -1) .. " entries)", ABIL ~= nil and #ABIL == 193)',
    '(ABIL and #ABIL or -1) .. " entries)", ABIL ~= nil and #ABIL == 262)', "P3 H68 #ABIL")
sub('the static key->marker map has all 199 keys (marker_by_key, ',
    'the static key->marker map has all 272 keys (marker_by_key, ', "P3 H68 map text")
sub('MK ~= nil and n_mk == 199)', 'MK ~= nil and n_mk == 272)', "P3 H68 map value")
sub('AKEYS == nil or #AKEYS == 199)', 'AKEYS == nil or #AKEYS == 272)', "P3 H68 array value")
sub('", table of 193 after round h89)", ABIL ~= nil and wired_n == 193 and total == 193)',
    '", table of 262 after round h90)", ABIL ~= nil and wired_n == 262 and total == 262)', "P3 C6c")
sub('    return exists == 6 and m_n == 6 and a_n == 2 and m2_n == 4 and wired_n == 193 and two and four',
    '    return exists == 6 and m_n == 6 and a_n == 2 and m2_n == 4 and wired_n == 262 and two and four',
    "P3 C6 return")
# the run_h88 S1 pins (the h88 section reads the grown table)
sub('check(TAG .. "S1c: the abilities table has 193 entries (" .. n_e .. ")", n_e == 193)',
    'check(TAG .. "S1c: the abilities table has 262 entries (" .. n_e .. ")", n_e == 262)', "P3 S1c")
sub('check(TAG .. "S1d: the static key->marker map has 199 keys (" .. n_k .. ")", n_k == 199)',
    'check(TAG .. "S1d: the static key->marker map has 272 keys (" .. n_k .. ")", n_k == 272)', "P3 S1d")
sub('    return armed_n == #samples and all_fired and (n_e == 193) and (n_k == 199)',
    '    return armed_n == #samples and all_fired and (n_e == 262) and (n_k == 272)', "P3 S1 return")
# the run_h89 M6 pins (the h89 section reads the grown table)
sub('check(TAG .. "M6c: the abilities table has 193 entries (" .. n_e .. ")", n_e == 193)',
    'check(TAG .. "M6c: the abilities table has 262 entries (" .. n_e .. ")", n_e == 262)', "P3 M6c")
sub('check(TAG .. "M6d: the static key->marker map has 199 keys (" .. n_k .. ")", n_k == 199)',
    'check(TAG .. "M6d: the static key->marker map has 272 keys (" .. n_k .. ")", n_k == 272)', "P3 M6d")
sub('    return armed_n == #ALL4 and all_fired and (n_e == 193) and (n_k == 199)',
    '    return armed_n == #ALL4 and all_fired and (n_e == 262) and (n_k == 272)', "P3 M6 return")
# the 0c not-routing guard count: the charge_only evaluator adds one guard
sub('  check(nm .. "the not-routing condition sits on every trigger path (and not routing x " .. guards .. ", want 7)", guards == 7)',
    '  check(nm .. "the not-routing condition sits on every trigger path (and not routing x " .. guards .. ", want 8 - block 7-9 adds the charge-only guard)", guards == 8)',
    "P3 0c guards")
sub(L('  -- Potion-of-Toughness evaluator adds ONE more in-melee guard, so the pin',
      '  -- is now 7 (on the pre-edit snapshot it still reads 6 - see the red control).'),
    L('  -- Potion-of-Toughness evaluator adds ONE more in-melee guard (pin 7).',
      '  -- HARNESS 90 ADAPTED: the charge-only evaluator adds ONE more "and not',
      '  -- routing" guard, so the pin is now 8 (on the pre-edit snapshot it reads 7).'),
    "P3 0c guards comment")
# the h82 C6 red-aggregate text (grown table)
sub('EXCEPT C6, whose wired-entry pin now reads the grown 193-entry table (the snapshot still has 189) - ',
    'EXCEPT C6, whose wired-entry pin now reads the grown 262-entry table (the snapshot still has 193) - ',
    "P3 h82 red aggregate")
# the earlier sections' trigger-count pins (the table grew again)
sub(L('    check("0h " .. nm .. ": the melee_unwavering entry count grew to 171 (got " .. mu .. ")",',
      '      mu == 171)'),
    L('    check("0h " .. nm .. ": the melee_unwavering entry count grew to 216 (got " .. mu .. ")",',
      '      mu == 216)'),
    "P3 0h melee_unwavering")
sub(L('    check("0h " .. nm .. ": the charge_or_melee entry count grew to 9 (got " .. cm .. ")",',
      '      cm == 9)'),
    L('    check("0h " .. nm .. ": the charge_or_melee entry count grew to 15 (got " .. cm .. ")",',
      '      cm == 15)'),
    "P3 0h charge_or_melee")
sub(L('    check("0m " .. nm .. ": the melee_unwavering entry count is 171 (got " .. cp(s, \'trigger = "melee_unwavering"\') .. ")",',
      '      cp(s, \'trigger = "melee_unwavering"\') == 171)'),
    L('    check("0m " .. nm .. ": the melee_unwavering entry count is 216 (got " .. cp(s, \'trigger = "melee_unwavering"\') .. ")",',
      '      cp(s, \'trigger = "melee_unwavering"\') == 216)'),
    "P3 0m melee_unwavering")
sub(L('    check("0m " .. nm .. ": the charge_or_melee entry count is 9 (got " .. cp(s, \'trigger = "charge_or_melee"\') .. ")",',
      '      cp(s, \'trigger = "charge_or_melee"\') == 9)'),
    L('    check("0m " .. nm .. ": the charge_or_melee entry count is 15 (got " .. cp(s, \'trigger = "charge_or_melee"\') .. ")",',
      '      cp(s, \'trigger = "charge_or_melee"\') == 15)'),
    "P3 0m charge_or_melee")
sub(L('    check("0m " .. nm .. ": the metallurgy_melee trigger count is 4 (got "',
      '      .. cp(s, \'trigger = "metallurgy_melee"\') .. ")", cp(s, \'trigger = "metallurgy_melee"\') == 4)'),
    L('    check("0m " .. nm .. ": the metallurgy_melee trigger count is 8 (4 Enchanted Metallurgy + 4 Master of Alchemy) (got "',
      '      .. cp(s, \'trigger = "metallurgy_melee"\') .. ")", cp(s, \'trigger = "metallurgy_melee"\') == 8)'),
    "P3 0m metallurgy")
sub(L('    check("0m " .. nm .. ": the melee_unwavering / charge_or_melee counts are untouched (171 / 9)",',
      '      cp(s, \'trigger = "melee_unwavering"\') == 171 and cp(s, \'trigger = "charge_or_melee"\') == 9)'),
    L('    check("0m " .. nm .. ": the melee_unwavering / charge_or_melee counts grew to (216 / 15)",',
      '      cp(s, \'trigger = "melee_unwavering"\') == 216 and cp(s, \'trigger = "charge_or_melee"\') == 15)'),
    "P3 0m counts untouched")

sub(L('    check("RED CONTROL (harness 87): N/A for the harness-89 round - this round\'s pre-edit snapshot IS the "',
      '      .. "shipped harness-88 build (the 25 m gate already ships), so every R1-R7 world passes by design - "'),
    L('    check("RED CONTROL (harness 87): N/A for the harness-90 round - this round\'s pre-edit snapshot IS the "',
      '      .. "shipped harness-89 build (the 25 m gate already ships), so every R1-R7 world passes by design - "'),
    "P3 h87 red aggregate")
sub(L('    check("RED CONTROL (harness 89): on the pre-edit snapshot (the shipped harness-88 build, 189 entries) "',
      '      .. "the grown-table pins and this HARNESS-89 section fail; the SILENT/SKIP worlds pass trivially because "',
      '      .. "the ability is simply absent on the snapshot (M3 / M4 both files + the ANNOTATED drift world M5, whose "',
      '      .. "log-based legs pass vacuously in the reading copy) - " .. n_ok',
      '      .. "/12 world results pass (want 5), fires " .. RED89.fires',
      '      .. ", claims " .. RED89.claims, n_ok == 5)'),
    L('    check("RED CONTROL (harness 89): on the pre-edit snapshot (the shipped harness-89 build, 193 entries) "',
      '      .. "the Enchanted Metallurgy abilities ALREADY SHIP, so the SILENT/SKIP worlds (M3 / M4 both files + the "',
      '      .. "ANNOTATED drift world M5, whose log-based legs pass vacuously in the reading copy) and the firing M1/M2 "',
      '      .. "worlds all pass; only the grown-table pins M6c/M6d fail (the snapshot has 193/199, the pin reads 262/272) - "',
      '      .. n_ok .. "/12 world results pass (want 10), fires " .. RED89.fires',
      '      .. ", claims " .. RED89.claims, n_ok == 10)'),
    "P3 h89 red aggregate")

# ---- P4 append the HARNESS-90 section before the final find check
FIND_ANCHOR = 'check("ZERO search calls by the mod across everything, harness 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87 and 88\'s worlds included (counted " .. find_calls .. ")",'
assert src.count(FIND_ANCHOR) == 1, "find anchor"
src = src.replace(FIND_ANCHOR, section + NL + FIND_ANCHOR, 1)
print("patch P4 section: applied")

# ---- P5 find-check wording
sub("harness 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87 and 88's worlds included",
    "harness 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88 and 89's worlds included",
    "P5 find wording")

assert "run_h90()" in src, "the h90 runner is missing"
assert 'os.getenv("H89_LIVE")' not in src and 'os.getenv("H90_LIVE")' in src, "env rename incomplete"
assert 'n_e == 262' in src and 'n_k == 272' in src, "the S1/M6 pins were not adapted"
assert 'wired_n == 262' in src, "the C6 pin was not adapted"

out = os.path.join(HERE, "harness90.lua")
io.open(out, "w", encoding="utf-8", newline="\n").write(src)
print("harness90.lua written:", len(src), "bytes,", src.count(NL), "lines")
