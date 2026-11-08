# -*- coding: utf-8 -*-
"""Assemble harness88.lua from the SHIPPED harness87.lua.

The round-88 job: THE BIG IMPLEMENTATION ROUND - blocks 4, 5 and 6 (87 new
ability entries) plus the two new trigger types (Will of the Verminking,
Potion of Toughness). The table grows 102 -> 189 entries (108 -> 195 keys),
so the table-size count pins in the earlier body sections are ADAPTED, and a
new HARNESS-88 section is appended before the final find check.

Patches:
  P1  env rename H87 -> H88
  P2  the red-mode banner re-pointed at this round
  P3  the adapted count pins (A4, B4, H68, C6c, 0h, 0c)
  P4  INSERT the HARNESS-88 section before the final find check
  P5  the final find-check wording names harness 87 too
"""
import io, os

HERE = os.path.dirname(os.path.abspath(__file__))
src = io.open(os.path.join(HERE, "harness87_source.lua"), encoding="utf-8").read()
section = io.open(os.path.join(HERE, "h88_section.lua"), encoding="utf-8").read()


def sub(old, new, label, count=1):
    global src
    n = src.count(old)
    assert n == count, "patch %s: %d matches (want %d)" % (label, n, count)
    src = src.replace(old, new, count)
    print("patch %s: applied" % label)


# ---- P1 env
sub('-- HARNESS 87 (this round): the env pair is now H87_LIVE / H87_ANN.\n'
    'local LIVE = os.getenv("H87_LIVE") or "C:/Users/vlady/Desktop/WH3_mod/mod_source/script/battle/mod/zz_test_deadly_onslaught.lua"\n'
    'local ANN  = os.getenv("H87_ANN")  or "C:/Users/vlady/Desktop/WH3_mod/docs/WH3_auto_ability_annotated.lua"\n'
    'local RED_MODE = (os.getenv("H87_LIVE") ~= nil) or (os.getenv("H87_ANN") ~= nil)',
    '-- HARNESS 88 (this round): the env pair is now H88_LIVE / H88_ANN.\n'
    'local LIVE = os.getenv("H88_LIVE") or "C:/Users/vlady/Desktop/WH3_mod/mod_source/script/battle/mod/zz_test_deadly_onslaught.lua"\n'
    'local ANN  = os.getenv("H88_ANN")  or "C:/Users/vlady/Desktop/WH3_mod/docs/WH3_auto_ability_annotated.lua"\n'
    'local RED_MODE = (os.getenv("H88_LIVE") ~= nil) or (os.getenv("H88_ANN") ~= nil)',
    "P1 env")

# ---- P2 banner
banner = (
'if RED_MODE then\n'
'  print("   *** RED CONTROL MODE: pre-edit snapshot(s) in use - the BLOCK 4/5/6 + NEW-TRIGGER (harness-88)")\n'
'  print("   *** checks + the ADAPTED TABLE-SIZE COUNT PINS are the ones EXPECTED to fail: the section-0m tokens,")\n'
'  print("   *** the V/Q/S worlds (the new entries and evaluators are simply absent on the 102-entry snapshot), and")\n'
'  print("   *** the pins that now read the grown table (A4 189 per pass, B4 189, H68 189/195, C6c 189, 0h")\n'
'  print("   *** melee_unwavering 171 / charge_or_melee 9, 0c guards 7). Every earlier world passes by design.***")\n'
'end\n'
'print()\n'
)
cut_start = 'if RED_MODE then\n  print("   *** RED CONTROL MODE:'
cut_end = '\nend\nprint()\n'
assert src.count(cut_start) == 1, "banner start anchor"
i = src.index(cut_start)
j = src.index(cut_end, i) + len(cut_end)
src = src[:i] + banner + src[j:]
print("patch P2 banner: applied")

# ---- P3 the adapted count pins
# A4 (badge paths walk the full table on the bootstrap)
sub('    a = (it == 204)', '    a = (it == 378)', "P3 A4a value")
sub('    check(TAG .. "A4a: with no information the badge paths walked the FULL 102-entry table ("',
    '    check(TAG .. "A4a: with no information the badge paths walked the FULL 189-entry table ("', "P3 A4a text")
sub('      .. it .. " iterations, 102 per pass - BLOCK 3 grew the table again)", a)',
    '      .. it .. " iterations, 189 per pass - BLOCK 4/5/6 grew the table again)", a)', "P3 A4a tail")
sub('    b = ((it / 2) == 102)', '    b = ((it / 2) == 189)', "P3 A4b value")
sub('    check(TAG .. "A4b: 102 abilities per pass, no shortened set (per pass = " .. (it / 2) .. ")", b)',
    '    check(TAG .. "A4b: 189 abilities per pass, no shortened set (per pass = " .. (it / 2) .. ")", b)', "P3 A4b text")
# B4 (unknown-cache full-table fallback)
sub('    a = (POLL_ITERS == 102)', '    a = (POLL_ITERS == 189)', "P3 B4 value")
sub('      .. ", want 102 - the FULL 102-entry table after BLOCK 3)", a)',
    '      .. ", want 189 - the FULL 189-entry table after BLOCK 4/5/6)", a)', "P3 B4 text")
# H68 table size + marker map + key array
sub('    (ABIL and #ABIL or -1) .. " entries)", ABIL ~= nil and #ABIL == 102)',
    '    (ABIL and #ABIL or -1) .. " entries)", ABIL ~= nil and #ABIL == 189)', "P3 H68 #ABIL")
sub('  check(TAG .. "H68: the static key->marker map has all 108 keys (marker_by_key, " .. n_mk .. ")",',
    '  check(TAG .. "H68: the static key->marker map has all 195 keys (marker_by_key, " .. n_mk .. ")",', "P3 H68 map text")
sub('    MK ~= nil and n_mk == 108)', '    MK ~= nil and n_mk == 195)', "P3 H68 map value")
sub('    AKEYS == nil or #AKEYS == 108)', '    AKEYS == nil or #AKEYS == 195)', "P3 H68 array value")
# C6c wired-entry count (+ the C6 world return)
sub('      .. ", table of 102 after BLOCK 3)", ABIL ~= nil and wired_n == 102 and total == 102)',
    '      .. ", table of 189 after BLOCK 4/5/6)", ABIL ~= nil and wired_n == 189 and total == 189)', "P3 C6c")
sub('    return exists == 6 and m_n == 6 and a_n == 2 and m2_n == 4 and wired_n == 102 and two and four',
    '    return exists == 6 and m_n == 6 and a_n == 2 and m2_n == 4 and wired_n == 189 and two and four', "P3 C6 return")
# 0h trigger counts
sub('    check("0h " .. nm .. ": the melee_unwavering entry count grew to 91 (got " .. mu .. ")",',
    '    check("0h " .. nm .. ": the melee_unwavering entry count grew to 171 (got " .. mu .. ")",', "P3 0h mu text")
sub('      mu == 91)', '      mu == 171)', "P3 0h mu value")
sub('    check("0h " .. nm .. ": the charge_or_melee entry count grew to 4 (got " .. cm .. ")",',
    '    check("0h " .. nm .. ": the charge_or_melee entry count grew to 9 (got " .. cm .. ")",', "P3 0h cm text")
sub('      cm == 4)', '      cm == 9)', "P3 0h cm value")
# 0c not-routing guard count
sub('  check(nm .. "the not-routing condition sits on every trigger path (and not routing x " .. guards .. ", want 6)", guards == 6)',
    '  check(nm .. "the not-routing condition sits on every trigger path (and not routing x " .. guards .. ", want 7)", guards == 7)',
    "P3 0c guards")
sub('  -- forces; the other trigger paths are untouched (on the pre-edit snapshot\n'
    '  -- this pin still reads 7 - see the red control).',
    '  -- forces; the other trigger paths are untouched. HARNESS 88 ADAPTED: the\n'
    '  -- Potion-of-Toughness evaluator adds ONE more in-melee guard, so the pin\n'
    '  -- is now 7 (on the pre-edit snapshot it still reads 6 - see the red control).',
    "P3 0c comment")
# 0z owner-melee guard count (the potion evaluator adds one)
sub('      .. og .. ", want 3: the three other trigger paths)", og == 3)',
    '      .. og .. ", want 4: the three other trigger paths + the potion in-melee guard)", og == 4)',
    "P3 0z guard")
# older rounds' red-branch aggregates, re-pointed at THIS round's snapshot
sub('    check("RED CONTROL (harness 82): N/A for the harness-86 round - the pre-edit snapshot already carries the "\n'
    '      .. "block-1 batch + item 8 and block 3\'s grown 102-entry table, so every C-world passes by design ("\n'
    '      .. n_ok .. "/16 world results, want 16)", n_ok == 16)',
    '    check("RED CONTROL (harness 82): on the harness-88 pre-edit snapshot the harness-82 C-worlds still pass "\n'
    '      .. "EXCEPT C6, whose wired-entry pin now reads the grown 189-entry table (the snapshot still has 102) - "\n'
    '      .. n_ok .. "/16 world results, want 14)", n_ok == 14)',
    "P3 h82 red aggregate")
sub('    check("RED CONTROL (harness 87): on the pre-edit snapshot (the shipped harness-86 build, constant still 55) ONLY "\n'
    '      .. "the section-0i tokens pinning the NEW value/comment fail (the 25 value, the \'no longer 55\' and the "\n'
    '      .. "conservative-trigger / 55 m wiki-aura comment) and ONLY the worlds whose verdict differs at 55 m fail: R2 "\n'
    '      .. "(the 55 m ally FIRES on the snapshot - the field-test complaint), R5 (its 55 m cast leg is still in range on "\n'
    '      .. "the snapshot, so no skip) and R7 (the 26 m ally fires on the snapshot). R1/R3/R4/R6 pass by design - "\n'
    '      .. n_ok .. "/14 world results pass (want 8), fires " .. RED87.fires\n'
    '      .. ", claims " .. RED87.claims, n_ok == 8)',
    '    check("RED CONTROL (harness 87): N/A for the harness-88 round - this round\'s pre-edit snapshot IS the "\n'
    '      .. "shipped harness-87 build (the 25 m gate already ships), so every R1-R7 world passes by design - "\n'
    '      .. n_ok .. "/14 world results pass (want 14), fires " .. RED87.fires\n'
    '      .. ", claims " .. RED87.claims, n_ok == 14)',
    "P3 h87 red aggregate")

# ---- P4 append the HARNESS-88 section before the final find check
FIND_ANCHOR = ("check(\"ZERO search calls by the mod across everything, harness 71, 72, 73, 74, 75, 76, 77, 78, 79, "
               "80, 81, 82, 83, 84, 85 and 86's worlds included (counted \" .. find_calls .. \")\",")
assert src.count(FIND_ANCHOR) == 1, "find anchor"
src = src.replace(FIND_ANCHOR, section + "\n" + FIND_ANCHOR, 1)
print("patch P4 section: applied")

# ---- P5 find-check wording
sub("harness 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85 and 86's worlds included",
    "harness 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86 and 87's worlds included",
    "P5 find wording")

assert "run_h88()" in src, "the h88 runner is missing"
assert 'os.getenv("H87_LIVE")' not in src and 'os.getenv("H88_LIVE")' in src, "env rename incomplete"
assert 'and not routing x " .. guards .. ", want 7)"' in src, "the 0c pin was not adapted"

out = os.path.join(HERE, "harness88.lua")
io.open(out, "w", encoding="utf-8", newline="\n").write(src)
print("harness88.lua written:", len(src), "bytes,", src.count("\n"), "lines")
