# -*- coding: utf-8 -*-
"""Assemble harness91.lua from the SHIPPED harness90.lua.

The round-91 job: THE 327 AUTO-ACCEPTED ABILITIES - a BULK DATA APPEND riding
THREE EXISTING evaluators (no new trigger types). 311 new entries / 327 new
keys; the table grows 262 -> 573 entries (272 -> 599 keys). So the table-size
pins in the earlier body sections are ADAPTED (A4 524->1146 / 262->573, B4
262->573, H68 262->573 & 272->599, C6c 262->573, S1 262/272->573/599, M6 same,
N13 same, 0h/0m 216->477 & 15->29, 0n 216/15->477/29), the harness-82 red
aggregate is re-pointed at the new pre-edit snapshot, and a new HARNESS-91
section is appended before the final find check.
"""
import io, os

HERE = os.path.dirname(os.path.abspath(__file__))
src = io.open(os.path.join(HERE, "harness90.lua"), encoding="utf-8").read()
section = io.open(os.path.join(HERE, "h91_section.lua"), encoding="utf-8").read()
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
sub(L('-- HARNESS 90 (this round): the env pair is now H90_LIVE / H90_ANN.',
      'local LIVE = os.getenv("H90_LIVE") or "C:/Users/vlady/Desktop/WH3_mod/mod_source/script/battle/mod/zz_test_deadly_onslaught.lua"',
      'local ANN  = os.getenv("H90_ANN")  or "C:/Users/vlady/Desktop/WH3_mod/docs/WH3_auto_ability_annotated.lua"',
      'local RED_MODE = (os.getenv("H90_LIVE") ~= nil) or (os.getenv("H90_ANN") ~= nil)'),
    L('-- HARNESS 91 (this round): the env pair is now H91_LIVE / H91_ANN.',
      'local LIVE = os.getenv("H91_LIVE") or "C:/Users/vlady/Desktop/WH3_mod/mod_source/script/battle/mod/zz_test_deadly_onslaught.lua"',
      'local ANN  = os.getenv("H91_ANN")  or "C:/Users/vlady/Desktop/WH3_mod/docs/WH3_auto_ability_annotated.lua"',
      'local RED_MODE = (os.getenv("H91_LIVE") ~= nil) or (os.getenv("H91_ANN") ~= nil)'),
    "P1 env")

# ---- P2 banner
sub(L('  print("   *** RED CONTROL MODE: pre-edit snapshot(s) in use - BLOCKS 7-9 (harness-90)")',
      '  print("   *** checks + the ADAPTED TABLE-SIZE COUNT PINS are the ones EXPECTED to fail: the section-0n tokens,")',
      '  print("   *** the N worlds (the new entries/evaluators are simply absent on the 193-entry snapshot), and")',
      '  print("   *** the pins that now read the grown table (A4 262 per pass, B4 262, H68 262/272, C6c 262,")',
      '  print("   *** S1 262/272, M6 262/272, 0c guards 8). Every earlier world passes by design.***")'),
    L('  print("   *** RED CONTROL MODE: pre-edit snapshot(s) in use - THE 327 AUTO-ACCEPTED ABILITIES (harness-91)")',
      '  print("   *** checks + the ADAPTED TABLE-SIZE COUNT PINS are the ones EXPECTED to fail: the section-0o tokens,")',
      '  print("   *** the O worlds (the new entries are simply absent on the 262-entry snapshot), and the pins that")',
      '  print("   *** now read the grown table (A4 573 per pass, B4 573, H68 573/599, C6c 573, S1 573/599, M6 573/599,")',
      '  print("   *** N13 573/599, 0h/0m 477/29, 0n 477/29). Every earlier world passes by design.***")'),
    "P2 banner")

# ---- P3 A4
sub(L('    a = (it == 524)',
      '    check(TAG .. "A4a: with no information the badge paths walked the FULL 262-entry table ("',
      '      .. it .. " iterations, 262 per pass - ROUND h90 grew the table again)", a)',
      '    b = ((it / 2) == 262)',
      '    check(TAG .. "A4b: 262 abilities per pass, no shortened set (per pass = " .. (it / 2) .. ")", b)'),
    L('    a = (it == 1146)',
      '    check(TAG .. "A4a: with no information the badge paths walked the FULL 573-entry table ("',
      '      .. it .. " iterations, 573 per pass - ROUND h91 grew the table again)", a)',
      '    b = ((it / 2) == 573)',
      '    check(TAG .. "A4b: 573 abilities per pass, no shortened set (per pass = " .. (it / 2) .. ")", b)'),
    "P3 A4")

# ---- P8b the h90 red branch (re-based for the harness-91 snapshot)
sub(L('    check("RED CONTROL (harness 90): on the pre-edit snapshot (the shipped harness-89 build, 193 entries) the "',
      '      .. "grown-table pins and this HARNESS-90 section fail; the SILENT worlds pass trivially because the new "',
      '      .. "abilities are simply absent on the snapshot (N2 / N4 / N7 / N9 / N14 / N16 both files = 12, plus the "',
      '      .. "ANNOTATED drift worlds N10 / N15 (their log legs are live-only, so they pass vacuously in the reading copy) "',
      '      .. "= 2) - " .. n_ok',
      '      .. "/32 world results pass (want 14), fires " .. RED90.fires',
      '      .. ", claims " .. RED90.claims, n_ok == 14)'),
    L('    check("RED CONTROL (harness 90): N/A for the harness-91 round - the harness-91 red snapshot already carries "',
      '      .. "blocks 7-9 (the shipped harness-90 build), so the N-worlds fire by design; only the grown-table pins "',
      '      .. "N13d / N13e fail (the snapshot has 262/272, the pin reads 573/599) - " .. n_ok',
      '      .. "/32 world results pass (want 30), fires " .. RED90.fires',
      '      .. ", claims " .. RED90.claims, n_ok == 30)'),
    "P8b h90 red branch")

# ---- P4 B4
sub(L('    a = (POLL_ITERS == 262)',
      '    check(TAG .. "B4a: an UNKNOWN owned-key cache falls back to the FULL table (got " .. POLL_ITERS',
      '      .. ", want 262 - the FULL 262-entry table after round h90)", a)'),
    L('    a = (POLL_ITERS == 573)',
      '    check(TAG .. "B4a: an UNKNOWN owned-key cache falls back to the FULL table (got " .. POLL_ITERS',
      '      .. ", want 573 - the FULL 573-entry table after round h91)", a)'),
    "P4 B4")

# ---- P5 H68
sub(L('  check(TAG .. "H68: the abilities table is reachable (" ..',
      '    (ABIL and #ABIL or -1) .. " entries)", ABIL ~= nil and #ABIL == 262)'),
    L('  check(TAG .. "H68: the abilities table is reachable (" ..',
      '    (ABIL and #ABIL or -1) .. " entries)", ABIL ~= nil and #ABIL == 573)'),
    "P5 H68 entries")
sub(L('  check(TAG .. "H68: the static key->marker map has all 272 keys (marker_by_key, " .. n_mk .. ")",',
      '    MK ~= nil and n_mk == 272)'),
    L('  check(TAG .. "H68: the static key->marker map has all 599 keys (marker_by_key, " .. n_mk .. ")",',
      '    MK ~= nil and n_mk == 599)'),
    "P5 H68 map")
sub('    AKEYS == nil or #AKEYS == 272)', '    AKEYS == nil or #AKEYS == 599)', "P5 H68 akeys")

# ---- P6 C6c
sub('      .. ", table of 262 after round h90)", ABIL ~= nil and wired_n == 262 and total == 262)',
    '      .. ", table of 573 after round h91)", ABIL ~= nil and wired_n == 573 and total == 573)',
    "P6 C6c")

# ---- P7 C6 return
sub('    return exists == 6 and m_n == 6 and a_n == 2 and m2_n == 4 and wired_n == 262 and two and four',
    '    return exists == 6 and m_n == 6 and a_n == 2 and m2_n == 4 and wired_n == 573 and two and four',
    "P7 C6 return")

# ---- P8 the h82 red aggregate (re-pointed at the new snapshot)
sub(L('    -- LINEAGE ADAPTATION (harness 86): this round\'s red snapshot (the shipped',
      '    -- harness-85 build) already carries BLOCK 3 too, so its full-table count pin',
      '    -- (102) now MATCHES - every C-world passes by design.',
      '    check("RED CONTROL (harness 82): on the harness-89 pre-edit snapshot the harness-82 C-worlds still pass "',
      '      .. "EXCEPT C6, whose wired-entry pin now reads the grown 262-entry table (the snapshot still has 193) - "',
      '      .. n_ok .. "/16 world results, want 14)", n_ok == 14)'),
    L('    -- LINEAGE ADAPTATION (harness 91): this round\'s red snapshot (the shipped',
      '    -- harness-90 build, 262 entries) already carries everything through blocks 7-9,',
      '    -- so every C-world passes EXCEPT C6, whose wired-entry pin now reads the grown',
      '    -- 573-entry table (the snapshot still has 262).',
      '    check("RED CONTROL (harness 82): on the harness-91 pre-edit snapshot the harness-82 C-worlds still pass "',
      '      .. "EXCEPT C6, whose wired-entry pin now reads the grown 573-entry table (the snapshot still has 262) - "',
      '      .. n_ok .. "/16 world results, want 14)", n_ok == 14)'),
    "P8 h82 red aggregate")

# ---- P9 0h counts
sub(L('    check("0h " .. nm .. ": the melee_unwavering entry count grew to 216 (got " .. mu .. ")",',
      '      mu == 216)'),
    L('    check("0h " .. nm .. ": the melee_unwavering entry count grew to 477 (got " .. mu .. ")",',
      '      mu == 477)'),
    "P9 0h mu")
sub(L('    check("0h " .. nm .. ": the charge_or_melee entry count grew to 15 (got " .. cm .. ")",',
      '      cm == 15)'),
    L('    check("0h " .. nm .. ": the charge_or_melee entry count grew to 29 (got " .. cm .. ")",',
      '      cm == 29)'),
    "P9 0h cm")

# ---- P10 0m counts
sub(L('    check("0m " .. nm .. ": the melee_unwavering entry count is 216 (got " .. cp(s, \'trigger = "melee_unwavering"\') .. ")",',
      '      cp(s, \'trigger = "melee_unwavering"\') == 216)'),
    L('    check("0m " .. nm .. ": the melee_unwavering entry count is 477 (got " .. cp(s, \'trigger = "melee_unwavering"\') .. ")",',
      '      cp(s, \'trigger = "melee_unwavering"\') == 477)'),
    "P10 0m mu")
sub(L('    check("0m " .. nm .. ": the charge_or_melee entry count is 15 (got " .. cp(s, \'trigger = "charge_or_melee"\') .. ")",',
      '      cp(s, \'trigger = "charge_or_melee"\') == 15)'),
    L('    check("0m " .. nm .. ": the charge_or_melee entry count is 29 (got " .. cp(s, \'trigger = "charge_or_melee"\') .. ")",',
      '      cp(s, \'trigger = "charge_or_melee"\') == 29)'),
    "P10 0m cm")

# ---- P11 S1
sub(L('    check(TAG .. "S1c: the abilities table has 262 entries (" .. n_e .. ")", n_e == 262)',
      '    check(TAG .. "S1d: the static key->marker map has 272 keys (" .. n_k .. ")", n_k == 272)'),
    L('    check(TAG .. "S1c: the abilities table has 573 entries (" .. n_e .. ")", n_e == 573)',
      '    check(TAG .. "S1d: the static key->marker map has 599 keys (" .. n_k .. ")", n_k == 599)'),
    "P11 S1 cd")
sub('    return armed_n == #samples and all_fired and (n_e == 262) and (n_k == 272)',
    '    return armed_n == #samples and all_fired and (n_e == 573) and (n_k == 599)',
    "P11 S1 return")

# ---- P12 0m counts grew
sub(L('    check("0m " .. nm .. ": the melee_unwavering / charge_or_melee counts grew to (216 / 15)",',
      '      cp(s, \'trigger = "melee_unwavering"\') == 216 and cp(s, \'trigger = "charge_or_melee"\') == 15)'),
    L('    check("0m " .. nm .. ": the melee_unwavering / charge_or_melee counts grew to (477 / 29)",',
      '      cp(s, \'trigger = "melee_unwavering"\') == 477 and cp(s, \'trigger = "charge_or_melee"\') == 29)'),
    "P12 0m grew")

# ---- P13 M6
sub(L('    check(TAG .. "M6c: the abilities table has 262 entries (" .. n_e .. ")", n_e == 262)',
      '    check(TAG .. "M6d: the static key->marker map has 272 keys (" .. n_k .. ")", n_k == 272)'),
    L('    check(TAG .. "M6c: the abilities table has 573 entries (" .. n_e .. ")", n_e == 573)',
      '    check(TAG .. "M6d: the static key->marker map has 599 keys (" .. n_k .. ")", n_k == 599)'),
    "P13 M6 cd")
sub('    return armed_n == #ALL4 and all_fired and (n_e == 262) and (n_k == 272)',
    '    return armed_n == #ALL4 and all_fired and (n_e == 573) and (n_k == 599)',
    "P13 M6 return")

# ---- P14 0n counts
sub(L('    check("0n " .. nm .. ": the trigger counts are right (melee_unwavering 216, charge_or_melee 15, charge_only 1, "',
      '      .. "wavering_self 3, wavering_self_or_ally 2, charge_or_wavering 1, wavering_ally_range 1, tired 2)",',
      '      cp(s, \'trigger = "melee_unwavering"\') == 216 and cp(s, \'trigger = "charge_or_melee"\') == 15'),
    L('    check("0n " .. nm .. ": the trigger counts are right (melee_unwavering 477, charge_or_melee 29, charge_only 1, "',
      '      .. "wavering_self 3, wavering_self_or_ally 2, charge_or_wavering 1, wavering_ally_range 1, tired 2)",',
      '      cp(s, \'trigger = "melee_unwavering"\') == 477 and cp(s, \'trigger = "charge_or_melee"\') == 29'),
    "P14 0n counts")

# ---- P15 N13
sub(L('    check(TAG .. "N13d: the abilities table has 262 entries (" .. n_e .. ")", n_e == 262)',
      '    check(TAG .. "N13e: the static key->marker map has 272 keys (" .. n_k .. ")", n_k == 272)'),
    L('    check(TAG .. "N13d: the abilities table has 573 entries (" .. n_e .. ")", n_e == 573)',
      '    check(TAG .. "N13e: the static key->marker map has 599 keys (" .. n_k .. ")", n_k == 599)'),
    "P15 N13 cd")
sub('    return a and lg(TAG, b) and lg(TAG, c) and (n_e == 262) and (n_k == 272)',
    '    return a and lg(TAG, b) and lg(TAG, c) and (n_e == 573) and (n_k == 599)',
    "P15 N13 return")
sub('  -- N13. THE REDESIGNED PAIR + the grown table (262 entries / 272 keys):',
    '  -- N13. THE REDESIGNED PAIR + the grown table (now 573 entries / 599 keys):',
    "P15 N13 comment")

# ---- P16 append the HARNESS-91 section after the run_h90() CALL (before the find check)
CALL = "\nrun_h90()\n"
assert src.count(CALL) == 1, ("run_h90() call anchor x%d" % src.count(CALL))
src = src.replace(CALL, CALL + section, 1)
print("patch P16 section: applied")

# ---- P17 find-check wording
sub("harness 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88 and 89's worlds included",
    "harness 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89 and 90's worlds included",
    "P17 find wording")

assert "run_h91()" in src, "the h91 runner is missing"
assert 'os.getenv("H90_LIVE")' not in src and 'os.getenv("H91_LIVE")' in src, "env rename incomplete"
assert 'n_e == 573' in src and 'n_k == 599' in src, "the S1/M6/N13 pins were not adapted"
assert '== 1146' in src and 'wired_n == 573' in src, "the A4/C6 pins were not adapted"

out = os.path.join(HERE, "harness91.lua")
io.open(out, "w", encoding="utf-8", newline="\n").write(src)
print("harness91.lua written:", len(src), "bytes,", src.count(NL), "lines")
