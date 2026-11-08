# -*- coding: utf-8 -*-
"""Assemble harness89.lua from the SHIPPED harness88.lua.

The round-89 job: THE ENCHANTED METALLURGY FAMILY - ONE new trigger
(metallurgy_melee) across four keys. The table grows 189 -> 193 entries
(195 -> 199 keys), so the table-size count pins in the earlier body sections
are ADAPTED (A4/B4/H68/C6c and the run_h88 S1 world), the red aggregates are
re-pointed at the new pre-edit snapshot, and a new HARNESS-89 section is
appended before the final find check.
"""
import io, os

HERE = os.path.dirname(os.path.abspath(__file__))
src = io.open(os.path.join(HERE, "harness88.lua"), encoding="utf-8").read()
section = io.open(os.path.join(HERE, "h89_section.lua"), encoding="utf-8").read()

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
sub(L('-- HARNESS 88 (this round): the env pair is now H88_LIVE / H88_ANN.',
      'local LIVE = os.getenv("H88_LIVE") or "C:/Users/vlady/Desktop/WH3_mod/mod_source/script/battle/mod/zz_test_deadly_onslaught.lua"',
      'local ANN  = os.getenv("H88_ANN")  or "C:/Users/vlady/Desktop/WH3_mod/docs/WH3_auto_ability_annotated.lua"',
      'local RED_MODE = (os.getenv("H88_LIVE") ~= nil) or (os.getenv("H88_ANN") ~= nil)'),
    L('-- HARNESS 89 (this round): the env pair is now H89_LIVE / H89_ANN.',
      'local LIVE = os.getenv("H89_LIVE") or "C:/Users/vlady/Desktop/WH3_mod/mod_source/script/battle/mod/zz_test_deadly_onslaught.lua"',
      'local ANN  = os.getenv("H89_ANN")  or "C:/Users/vlady/Desktop/WH3_mod/docs/WH3_auto_ability_annotated.lua"',
      'local RED_MODE = (os.getenv("H89_LIVE") ~= nil) or (os.getenv("H89_ANN") ~= nil)'),
    "P1 env")

# ---- P2 banner
sub(L('if RED_MODE then',
      '  print("   *** RED CONTROL MODE: pre-edit snapshot(s) in use - the BLOCK 4/5/6 + NEW-TRIGGER (harness-88)")',
      '  print("   *** checks + the ADAPTED TABLE-SIZE COUNT PINS are the ones EXPECTED to fail: the section-0m tokens,")',
      '  print("   *** the V/Q/S worlds (the new entries and evaluators are simply absent on the 102-entry snapshot), and")',
      '  print("   *** the pins that now read the grown table (A4 189 per pass, B4 189, H68 189/195, C6c 189, 0h")',
      '  print("   *** melee_unwavering 171 / charge_or_melee 9, 0c guards 7). Every earlier world passes by design.***")',
      'end'),
    L('if RED_MODE then',
      '  print("   *** RED CONTROL MODE: pre-edit snapshot(s) in use - the ENCHANTED METALLURGY family (harness-89)")',
      '  print("   *** checks + the ADAPTED TABLE-SIZE COUNT PINS are the ones EXPECTED to fail: the section-0m tokens,")',
      '  print("   *** the M worlds (the new entries and evaluator are simply absent on the 189-entry snapshot), and")',
      '  print("   *** the pins that now read the grown table (A4 193 per pass, B4 193, H68 193/199, C6c 193)")',
      '  print("   *** plus the run_h88 S1 world (193/199). Every earlier world passes by design.***")',
      'end'),
    "P2 banner")

# ---- P3 the adapted count pins
sub('    a = (it == 378)', '    a = (it == 386)', "P3 A4a value")
sub('FULL 189-entry table (', 'FULL 193-entry table (', "P3 A4a text")
sub('iterations, 189 per pass - BLOCK 4/5/6 grew the table again',
    'iterations, 193 per pass - ROUND h89 grew the table again', "P3 A4a tail")
sub('    b = ((it / 2) == 189)', '    b = ((it / 2) == 193)', "P3 A4b value")
sub('A4b: 189 abilities per pass, no shortened set', 'A4b: 193 abilities per pass, no shortened set', "P3 A4b text")
sub('    a = (POLL_ITERS == 189)', '    a = (POLL_ITERS == 193)', "P3 B4 value")
sub(', want 189 - the FULL 189-entry table after BLOCK 4/5/6)',
    ', want 193 - the FULL 193-entry table after round h89)', "P3 B4 text")
sub('(ABIL and #ABIL or -1) .. " entries)", ABIL ~= nil and #ABIL == 189)',
    '(ABIL and #ABIL or -1) .. " entries)", ABIL ~= nil and #ABIL == 193)', "P3 H68 #ABIL")
sub('the static key->marker map has all 195 keys (marker_by_key, ',
    'the static key->marker map has all 199 keys (marker_by_key, ', "P3 H68 map text")
sub('MK ~= nil and n_mk == 195)', 'MK ~= nil and n_mk == 199)', "P3 H68 map value")
sub('AKEYS == nil or #AKEYS == 195)', 'AKEYS == nil or #AKEYS == 199)', "P3 H68 array value")
sub('", table of 189 after BLOCK 4/5/6)", ABIL ~= nil and wired_n == 189 and total == 189)',
    '", table of 193 after round h89)", ABIL ~= nil and wired_n == 193 and total == 193)', "P3 C6c")
sub('    return exists == 6 and m_n == 6 and a_n == 2 and m2_n == 4 and wired_n == 189 and two and four',
    '    return exists == 6 and m_n == 6 and a_n == 2 and m2_n == 4 and wired_n == 193 and two and four',
    "P3 C6 return")
sub('check(TAG .. "S1c: the abilities table has 189 entries (" .. n_e .. ")", n_e == 189)',
    'check(TAG .. "S1c: the abilities table has 193 entries (" .. n_e .. ")", n_e == 193)', "P3 S1c")
sub('check(TAG .. "S1d: the static key->marker map has 195 keys (" .. n_k .. ")", n_k == 195)',
    'check(TAG .. "S1d: the static key->marker map has 199 keys (" .. n_k .. ")", n_k == 199)', "P3 S1d")
sub('    return armed_n == #samples and all_fired and (n_e == 189) and (n_k == 195)',
    '    return armed_n == #samples and all_fired and (n_e == 193) and (n_k == 199)', "P3 S1 return")
sub(L('    check("RED CONTROL (harness 82): on the harness-88 pre-edit snapshot the harness-82 C-worlds still pass "',
      '      .. "EXCEPT C6, whose wired-entry pin now reads the grown 189-entry table (the snapshot still has 102) - "',),
    L('    check("RED CONTROL (harness 82): on the harness-89 pre-edit snapshot the harness-82 C-worlds still pass "',
      '      .. "EXCEPT C6, whose wired-entry pin now reads the grown 193-entry table (the snapshot still has 189) - "',),
    "P3 h82 red aggregate")
sub(L("    check(\"RED CONTROL (harness 87): N/A for the harness-88 round - this round's pre-edit snapshot IS the \"",
      '      .. "shipped harness-87 build (the 25 m gate already ships), so every R1-R7 world passes by design - "'),
    L("    check(\"RED CONTROL (harness 87): N/A for the harness-89 round - this round's pre-edit snapshot IS the \"",
      '      .. "shipped harness-88 build (the 25 m gate already ships), so every R1-R7 world passes by design - "'),
    "P3 h87 red aggregate")
sub(L('    check("RED CONTROL (harness 88): on the pre-edit snapshot (the shipped harness-87 build, 102 entries) the "',
      '      .. "adapted count pins and this HARNESS-88 section fail; the SILENT worlds pass trivially because the "',
      '      .. "ability is simply absent on the snapshot (V2/V3/Q2/Q3 both files + the annotated drift world V4) - "',
      '      .. n_ok .. "/18 world results pass (want 9), fires " .. RED88.fires',
      '      .. ", claims " .. RED88.claims, n_ok == 9)'),
    L('    check("RED CONTROL (harness 88): on the pre-edit snapshot (the shipped harness-88 build, 189 entries) "',
      "      .. \"this HARNESS-88 section's grown-table pin fails (S1 reads 193/199, the snapshot has 189/195); the \"",
      '      .. "V/Q worlds all pass by design (their abilities already ship) - "',
      '      .. n_ok .. "/18 world results pass (want 16), fires " .. RED88.fires',
      '      .. ", claims " .. RED88.claims, n_ok == 16)'),
    "P3 h88 red branch")

# ---- P4 append the HARNESS-89 section before the final find check
FIND_ANCHOR = 'check("ZERO search calls by the mod across everything, harness 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86 and 87\'s worlds included (counted " .. find_calls .. ")",'
assert src.count(FIND_ANCHOR) == 1, "find anchor"
src = src.replace(FIND_ANCHOR, section + NL + FIND_ANCHOR, 1)
print("patch P4 section: applied")

# ---- P5 find-check wording
sub("harness 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86 and 87's worlds included",
    "harness 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87 and 88's worlds included",
    "P5 find wording")

assert "run_h89()" in src, "the h89 runner is missing"
assert 'os.getenv("H88_LIVE")' not in src and 'os.getenv("H89_LIVE")' in src, "env rename incomplete"
assert 'n_e == 193' in src and 'n_k == 199' in src, "the run_h88 S1 pins were not adapted"
assert 'wired_n == 193' in src, "the C6 pin was not adapted"

out = os.path.join(HERE, "harness89.lua")
io.open(out, "w", encoding="utf-8", newline="\n").write(src)
print("harness89.lua written:", len(src), "bytes,", src.count(NL), "lines")
