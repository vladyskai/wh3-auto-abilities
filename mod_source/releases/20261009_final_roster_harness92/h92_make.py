# -*- coding: utf-8 -*-
"""Assemble harness92.lua from the SHIPPED harness91.lua.

The round-92 job: THE FINAL ROSTER BUILD - the SIX built individual abilities
from the remaining-abilities triage. TWO NEW ally-heal triggers (blood_sacrifice,
eat_da_runts), each its own evaluator, plus FOUR entries riding the EXISTING
shared melee_unwavering evaluator. The table grows 573 -> 579 entries (599 -> 605
keys); melee_unwavering 477 -> 481; two new triggers (blood_sacrifice 1,
eat_da_runts 1).

So the table-size pins in the earlier body sections are ADAPTED (A4 1146->1158
& 573->579, B4 573->579, H68 573/599->579/605, C6c 573->579, C6 573->579,
S1 573/599->579/605, M6 same, N13 same, 0h/0m/0n 477->481, and the run_h91 0o
tokens likewise), the harness-82/harness-90 red aggregates are re-pointed at the
new pre-edit snapshot, the env pair becomes H92_LIVE / H92_ANN, and the new
HARNESS-92 section is appended before the final find check.
"""
import io, os

HERE = os.path.dirname(os.path.abspath(__file__))
src = io.open(os.path.join(HERE, "harness91.lua"), encoding="utf-8").read()
section = io.open(os.path.join(HERE, "h92_section.lua"), encoding="utf-8").read()
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
sub(L('-- HARNESS 91 (this round): the env pair is now H91_LIVE / H91_ANN.',
      'local LIVE = os.getenv("H91_LIVE") or "C:/Users/vlady/Desktop/WH3_mod/mod_source/script/battle/mod/zz_test_deadly_onslaught.lua"',
      'local ANN  = os.getenv("H91_ANN")  or "C:/Users/vlady/Desktop/WH3_mod/docs/WH3_auto_ability_annotated.lua"',
      'local RED_MODE = (os.getenv("H91_LIVE") ~= nil) or (os.getenv("H91_ANN") ~= nil)'),
    L('-- HARNESS 92 (this round): the env pair is now H92_LIVE / H92_ANN.',
      'local LIVE = os.getenv("H92_LIVE") or "C:/Users/vlady/Desktop/WH3_mod/mod_source/script/battle/mod/zz_test_deadly_onslaught.lua"',
      'local ANN  = os.getenv("H92_ANN")  or "C:/Users/vlady/Desktop/WH3_mod/docs/WH3_auto_ability_annotated.lua"',
      'local RED_MODE = (os.getenv("H92_LIVE") ~= nil) or (os.getenv("H92_ANN") ~= nil)'),
    "P1 env")

# ---- P2 banner
sub(L('  print("   *** RED CONTROL MODE: pre-edit snapshot(s) in use - THE 327 AUTO-ACCEPTED ABILITIES (harness-91)")',
      '  print("   *** checks + the ADAPTED TABLE-SIZE COUNT PINS are the ones EXPECTED to fail: the section-0o tokens,")',
      '  print("   *** the O worlds (the new entries are simply absent on the 262-entry snapshot), and the pins that")',
      '  print("   *** now read the grown table (A4 573 per pass, B4 573, H68 573/599, C6c 573, S1 573/599, M6 573/599,")',
      '  print("   *** N13 573/599, 0h/0m 477/29, 0n 477/29). Every earlier world passes by design.***")'),
    L('  print("   *** RED CONTROL MODE: pre-edit snapshot(s) in use - THE FINAL ROSTER BUILD (harness-92)")',
      '  print("   *** checks + the ADAPTED TABLE-SIZE COUNT PINS are the ones EXPECTED to fail: the section-0p tokens,")',
      '  print("   *** the P worlds (the new entries are simply absent on the 573-entry snapshot), and the pins that")',
      '  print("   *** now read the grown table (A4 579 per pass, B4 579, H68 579/605, C6c 579, S1 579/605, M6 579/605,")',
      '  print("   *** N13 579/605, 0h/0m 481/29, 0n 481/29). Every earlier world passes by design.***")'),
    "P2 banner")

# ---- P3 A4
sub(L('    a = (it == 1146)',
      '    check(TAG .. "A4a: with no information the badge paths walked the FULL 573-entry table ("',
      '      .. it .. " iterations, 573 per pass - ROUND h91 grew the table again)", a)',
      '    b = ((it / 2) == 573)',
      '    check(TAG .. "A4b: 573 abilities per pass, no shortened set (per pass = " .. (it / 2) .. ")", b)'),
    L('    a = (it == 1158)',
      '    check(TAG .. "A4a: with no information the badge paths walked the FULL 579-entry table ("',
      '      .. it .. " iterations, 579 per pass - ROUND h92 grew the table again)", a)',
      '    b = ((it / 2) == 579)',
      '    check(TAG .. "A4b: 579 abilities per pass, no shortened set (per pass = " .. (it / 2) .. ")", b)'),
    "P3 A4")

# ---- P4 B4
sub(L('    a = (POLL_ITERS == 573)',
      '    check(TAG .. "B4a: an UNKNOWN owned-key cache falls back to the FULL table (got " .. POLL_ITERS',
      '      .. ", want 573 - the FULL 573-entry table after round h91)", a)'),
    L('    a = (POLL_ITERS == 579)',
      '    check(TAG .. "B4a: an UNKNOWN owned-key cache falls back to the FULL table (got " .. POLL_ITERS',
      '      .. ", want 579 - the FULL 579-entry table after round h92)", a)'),
    "P4 B4")

# ---- P5 H68
sub(L('  check(TAG .. "H68: the abilities table is reachable (" ..',
      '    (ABIL and #ABIL or -1) .. " entries)", ABIL ~= nil and #ABIL == 573)'),
    L('  check(TAG .. "H68: the abilities table is reachable (" ..',
      '    (ABIL and #ABIL or -1) .. " entries)", ABIL ~= nil and #ABIL == 579)'),
    "P5 H68 entries")
sub(L('  check(TAG .. "H68: the static key->marker map has all 599 keys (marker_by_key, " .. n_mk .. ")",',
      '    MK ~= nil and n_mk == 599)'),
    L('  check(TAG .. "H68: the static key->marker map has all 605 keys (marker_by_key, " .. n_mk .. ")",',
      '    MK ~= nil and n_mk == 605)'),
    "P5 H68 map")
sub('    AKEYS == nil or #AKEYS == 599)', '    AKEYS == nil or #AKEYS == 605)', "P5 H68 akeys")

# ---- P6 C6c
sub('      .. ", table of 573 after round h91)", ABIL ~= nil and wired_n == 573 and total == 573)',
    '      .. ", table of 579 after round h92)", ABIL ~= nil and wired_n == 579 and total == 579)',
    "P6 C6c")

# ---- P7 C6 return
sub('    return exists == 6 and m_n == 6 and a_n == 2 and m2_n == 4 and wired_n == 573 and two and four',
    '    return exists == 6 and m_n == 6 and a_n == 2 and m2_n == 4 and wired_n == 579 and two and four',
    "P7 C6 return")

# ---- P8 the h82 red aggregate (re-pointed at the new snapshot)
sub(L('    -- LINEAGE ADAPTATION (harness 91): this round\'s red snapshot (the shipped',
      '    -- harness-90 build, 262 entries) already carries everything through blocks 7-9,',
      '    -- so every C-world passes EXCEPT C6, whose wired-entry pin now reads the grown',
      '    -- 573-entry table (the snapshot still has 262).',
      '    check("RED CONTROL (harness 82): on the harness-91 pre-edit snapshot the harness-82 C-worlds still pass "',
      '      .. "EXCEPT C6, whose wired-entry pin now reads the grown 573-entry table (the snapshot still has 262) - "',
      '      .. n_ok .. "/16 world results, want 14)", n_ok == 14)'),
    L('    -- LINEAGE ADAPTATION (harness 92): this round\'s red snapshot (the shipped',
      '    -- harness-91 build, 573 entries) already carries everything through the auto-327',
      '    -- sweep, so every C-world passes EXCEPT C6, whose wired-entry pin now reads the',
      '    -- grown 579-entry table (the snapshot still has 573).',
      '    check("RED CONTROL (harness 82): on the harness-92 pre-edit snapshot the harness-82 C-worlds still pass "',
      '      .. "EXCEPT C6, whose wired-entry pin now reads the grown 579-entry table (the snapshot still has 573) - "',
      '      .. n_ok .. "/16 world results, want 14)", n_ok == 14)'),
    "P8 h82 red aggregate")

# ---- P8b the h90 red branch (re-based for the harness-92 snapshot)
sub(L('    check("RED CONTROL (harness 90): N/A for the harness-91 round - the harness-91 red snapshot already carries "',
      '      .. "blocks 7-9 (the shipped harness-90 build), so the N-worlds fire by design; only the grown-table pins "',
      '      .. "N13d / N13e fail (the snapshot has 262/272, the pin reads 573/599) - " .. n_ok',
      '      .. "/32 world results pass (want 30), fires " .. RED90.fires',
      '      .. ", claims " .. RED90.claims, n_ok == 30)'),
    L('    check("RED CONTROL (harness 90): N/A for the harness-92 round - the harness-92 red snapshot already carries "',
      '      .. "the auto-327 sweep (the shipped harness-91 build), so the N-worlds fire by design; only the grown-table "',
      '      .. "pins N13d / N13e fail (the snapshot has 573/599, the pin reads 579/605) - " .. n_ok',
      '      .. "/32 world results pass (want 30), fires " .. RED90.fires',
      '      .. ", claims " .. RED90.claims, n_ok == 30)'),
    "P8b h90 red branch")

# ---- P9 0h counts
sub(L('    check("0h " .. nm .. ": the melee_unwavering entry count grew to 477 (got " .. mu .. ")",',
      '      mu == 477)'),
    L('    check("0h " .. nm .. ": the melee_unwavering entry count grew to 481 (got " .. mu .. ")",',
      '      mu == 481)'),
    "P9 0h mu")
sub(L('    check("0h " .. nm .. ": the charge_or_melee entry count grew to 29 (got " .. cm .. ")",',
      '      cm == 29)'),
    L('    check("0h " .. nm .. ": the charge_or_melee entry count grew to 29 (got " .. cm .. ")",',
      '      cm == 29)'),
    "P9 0h cm")

# ---- P10 0m counts
sub(L('    check("0m " .. nm .. ": the melee_unwavering entry count is 477 (got " .. cp(s, \'trigger = "melee_unwavering"\') .. ")",',
      '      cp(s, \'trigger = "melee_unwavering"\') == 477)'),
    L('    check("0m " .. nm .. ": the melee_unwavering entry count is 481 (got " .. cp(s, \'trigger = "melee_unwavering"\') .. ")",',
      '      cp(s, \'trigger = "melee_unwavering"\') == 481)'),
    "P10 0m mu")
sub(L('    check("0m " .. nm .. ": the charge_or_melee entry count is 29 (got " .. cp(s, \'trigger = "charge_or_melee"\') .. ")",',
      '      cp(s, \'trigger = "charge_or_melee"\') == 29)'),
    L('    check("0m " .. nm .. ": the charge_or_melee entry count is 29 (got " .. cp(s, \'trigger = "charge_or_melee"\') .. ")",',
      '      cp(s, \'trigger = "charge_or_melee"\') == 29)'),
    "P10 0m cm")

# ---- P11 S1
sub(L('    check(TAG .. "S1c: the abilities table has 573 entries (" .. n_e .. ")", n_e == 573)',
      '    check(TAG .. "S1d: the static key->marker map has 599 keys (" .. n_k .. ")", n_k == 599)'),
    L('    check(TAG .. "S1c: the abilities table has 579 entries (" .. n_e .. ")", n_e == 579)',
      '    check(TAG .. "S1d: the static key->marker map has 605 keys (" .. n_k .. ")", n_k == 605)'),
    "P11 S1 cd")
sub('    return armed_n == #samples and all_fired and (n_e == 573) and (n_k == 599)',
    '    return armed_n == #samples and all_fired and (n_e == 579) and (n_k == 605)',
    "P11 S1 return")

# ---- P12 0m counts grew
sub(L('    check("0m " .. nm .. ": the melee_unwavering / charge_or_melee counts grew to (477 / 29)",',
      '      cp(s, \'trigger = "melee_unwavering"\') == 477 and cp(s, \'trigger = "charge_or_melee"\') == 29)'),
    L('    check("0m " .. nm .. ": the melee_unwavering / charge_or_melee counts grew to (481 / 29)",',
      '      cp(s, \'trigger = "melee_unwavering"\') == 481 and cp(s, \'trigger = "charge_or_melee"\') == 29)'),
    "P12 0m grew")

# ---- P13 M6
sub(L('    check(TAG .. "M6c: the abilities table has 573 entries (" .. n_e .. ")", n_e == 573)',
      '    check(TAG .. "M6d: the static key->marker map has 599 keys (" .. n_k .. ")", n_k == 599)'),
    L('    check(TAG .. "M6c: the abilities table has 579 entries (" .. n_e .. ")", n_e == 579)',
      '    check(TAG .. "M6d: the static key->marker map has 605 keys (" .. n_k .. ")", n_k == 605)'),
    "P13 M6 cd")
sub('    return armed_n == #ALL4 and all_fired and (n_e == 573) and (n_k == 599)',
    '    return armed_n == #ALL4 and all_fired and (n_e == 579) and (n_k == 605)',
    "P13 M6 return")

# ---- P14 0n counts
sub(L('    check("0n " .. nm .. ": the trigger counts are right (melee_unwavering 477, charge_or_melee 29, charge_only 1, "',
      '      .. "wavering_self 3, wavering_self_or_ally 2, charge_or_wavering 1, wavering_ally_range 1, tired 2)",',
      '      cp(s, \'trigger = "melee_unwavering"\') == 477 and cp(s, \'trigger = "charge_or_melee"\') == 29',
      '      and cp(s, \'trigger = "charge_only"\') == 1 and cp(s, \'trigger = "wavering_self"\') == 3',
      '      and cp(s, \'trigger = "wavering_self_or_ally"\') == 2 and cp(s, \'trigger = "charge_or_wavering"\') == 1',
      '      and cp(s, \'trigger = "wavering_ally_range"\') == 1 and cp(s, \'trigger = "tired"\') == 2)'),
    L('    check("0n " .. nm .. ": the trigger counts are right (melee_unwavering 481, charge_or_melee 29, charge_only 1, "',
      '      .. "wavering_self 3, wavering_self_or_ally 2, charge_or_wavering 1, wavering_ally_range 1, tired 2)",',
      '      cp(s, \'trigger = "melee_unwavering"\') == 481 and cp(s, \'trigger = "charge_or_melee"\') == 29',
      '      and cp(s, \'trigger = "charge_only"\') == 1 and cp(s, \'trigger = "wavering_self"\') == 3',
      '      and cp(s, \'trigger = "wavering_self_or_ally"\') == 2 and cp(s, \'trigger = "charge_or_wavering"\') == 1',
      '      and cp(s, \'trigger = "wavering_ally_range"\') == 1 and cp(s, \'trigger = "tired"\') == 2)'),
    "P14 0n counts")

# ---- P15 N13
sub(L('    check(TAG .. "N13d: the abilities table has 573 entries (" .. n_e .. ")", n_e == 573)',
      '    check(TAG .. "N13e: the static key->marker map has 599 keys (" .. n_k .. ")", n_k == 599)'),
    L('    check(TAG .. "N13d: the abilities table has 579 entries (" .. n_e .. ")", n_e == 579)',
      '    check(TAG .. "N13e: the static key->marker map has 605 keys (" .. n_k .. ")", n_k == 605)'),
    "P15 N13 cd")
sub('    return a and lg(TAG, b) and lg(TAG, c) and (n_e == 573) and (n_k == 599)',
    '    return a and lg(TAG, b) and lg(TAG, c) and (n_e == 579) and (n_k == 605)',
    "P15 N13 return")
sub('  -- N13. THE REDESIGNED PAIR + the grown table (now 573 entries / 599 keys):',
    '  -- N13. THE REDESIGNED PAIR + the grown table (now 579 entries / 605 keys):',
    "P15 N13 comment")

# ---- P15b the run_h91 0o table pins (adapted to the final roster table)
sub(L('    check("0o " .. nm .. ": the grown table is 573 entries (each with a badge field)",',
      '      cp(s, "\\t{ marker = ") == 573 and cp(s, \'badge = "\') == 573)'),
    L('    check("0o " .. nm .. ": the grown table is 579 entries (each with a badge field)",',
      '      cp(s, "\\t{ marker = ") == 579 and cp(s, \'badge = "\') == 579)'),
    "P15b 0o entries")
sub(L('    check("0o " .. nm .. ": the trigger counts grew to (melee_unwavering 477, ushoran_health 41, charge_or_melee 29) "',
      '      .. "and every other trigger is UNCHANGED (charge_only 1, wavering_self 3, wavering_self_or_ally 2, "',
      '      .. "charge_or_wavering 1, wavering_ally_range 1, tired 2, metallurgy_melee 8, melee_health75 2)",',
      '      cp(s, \'trigger = "melee_unwavering"\') == 477 and cp(s, \'trigger = "ushoran_health"\') == 41',
      '      and cp(s, \'trigger = "charge_or_melee"\') == 29 and cp(s, \'trigger = "charge_only"\') == 1',
      '      and cp(s, \'trigger = "wavering_self"\') == 3 and cp(s, \'trigger = "wavering_self_or_ally"\') == 2',
      '      and cp(s, \'trigger = "charge_or_wavering"\') == 1 and cp(s, \'trigger = "wavering_ally_range"\') == 1',
      '      and cp(s, \'trigger = "tired"\') == 2 and cp(s, \'trigger = "metallurgy_melee"\') == 8',
      '      and cp(s, \'trigger = "melee_health75"\') == 2)'),
    L('    check("0o " .. nm .. ": the trigger counts grew to (melee_unwavering 481, ushoran_health 41, charge_or_melee 29, "',
      '      .. "blood_sacrifice 1, eat_da_runts 1) and every other trigger is UNCHANGED (charge_only 1, wavering_self 3, "',
      '      .. "wavering_self_or_ally 2, charge_or_wavering 1, wavering_ally_range 1, tired 2, metallurgy_melee 8, "',
      '      .. "melee_health75 2)",',
      '      cp(s, \'trigger = "melee_unwavering"\') == 481 and cp(s, \'trigger = "ushoran_health"\') == 41',
      '      and cp(s, \'trigger = "charge_or_melee"\') == 29 and cp(s, \'trigger = "charge_only"\') == 1',
      '      and cp(s, \'trigger = "wavering_self"\') == 3 and cp(s, \'trigger = "wavering_self_or_ally"\') == 2',
      '      and cp(s, \'trigger = "charge_or_wavering"\') == 1 and cp(s, \'trigger = "wavering_ally_range"\') == 1',
      '      and cp(s, \'trigger = "tired"\') == 2 and cp(s, \'trigger = "metallurgy_melee"\') == 8',
      '      and cp(s, \'trigger = "melee_health75"\') == 2 and cp(s, \'trigger = "blood_sacrifice"\') == 1',
      '      and cp(s, \'trigger = "eat_da_runts"\') == 1)'),
    "P15b 0o triggers")

# ---- P15c re-base the run_h91 red branch for the harness-92 snapshot (the
# harness-92 red snapshot is the shipped harness-91 build, which already carries
# the auto-327 sweep, so every HARNESS-91 world fires by design).
sub(L('check("RED CONTROL (harness 91): on the pre-edit snapshot (the shipped harness-90 build, 262 entries) the " ',
      '      .. "grown-table pins and this HARNESS-91 section fail; the SILENT worlds pass trivially because the new " ',
      '      .. "abilities are simply absent on the snapshot (O2 / U2 both files = 4, plus the ANNOTATED legs of the " ',
      '      .. "live-only log checks) - " .. n_ok .. "/16 world results pass (want 6), fires " .. RED91.fires ',
      '      .. ", claims " .. RED91.claims, n_ok == 6)'),
    L('check("RED CONTROL (harness 91): N/A for the harness-92 round - the harness-92 red snapshot already carries the " ',
      '      .. "auto-327 sweep (the shipped harness-91 build), so every HARNESS-91 world fires by design; only the grown-" ',
      '      .. "table pins (section 0o) fail - " .. n_ok .. "/16 world results pass (want 16), fires " .. RED91.fires ',
      '      .. ", claims " .. RED91.claims, n_ok == 16)'),
    "P15c h91 red branch")

# ---- P16 append the HARNESS-92 section after the run_h91() CALL
CALL = "\nrun_h91()\n"
assert src.count(CALL) == 1, ("run_h91() call anchor x%d" % src.count(CALL))
src = src.replace(CALL, CALL + section, 1)
print("patch P16 section: applied")

# ---- P17 find-check wording
sub("harness 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89 and 90's worlds included",
    "harness 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90 and 91's worlds included",
    "P17 find wording")

assert "run_h92()" in src, "the h92 runner is missing"
assert 'os.getenv("H91_LIVE")' not in src and 'os.getenv("H92_LIVE")' in src, "env rename incomplete"
assert 'n_e == 579' in src and 'n_k == 605' in src, "the S1/M6/N13 pins were not adapted"
assert '== 1158' in src and 'wired_n == 579' in src, "the A4/C6 pins were not adapted"

out = os.path.join(HERE, "harness92.lua")
io.open(out, "w", encoding="utf-8", newline="\n").write(src)
print("harness92.lua written:", len(src), "bytes,", src.count(NL), "lines")
