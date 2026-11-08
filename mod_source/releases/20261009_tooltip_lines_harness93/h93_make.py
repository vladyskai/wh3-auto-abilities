# -*- coding: utf-8 -*-
"""HARNESS 93 build: assemble harness93.lua from the SHIPPED harness92.lua, and
write the pre-edit snapshots the RED CONTROL points at.

The round-93 job: THE PER-ABILITY TOOLTIP LINE. The mod used to append ONE
generic sentence ("this ability fires by itself while the unit charges ...") to
every implemented ability's tooltip; most abilities do not fire on a charge.
The line is now COMPOSED per entry from the trigger the entry actually rides
(FOURTH.TRIGGER_TIP[trigger] -> ability.tip), and the old sentence is removed.

What this script does:
  1. pre93_live.lua / pre93_ann.lua  = the shipped harness-92 build (579
     entries, NO TRIGGER_TIP, NO ability.tip wiring) - the RED snapshot.
     pre93_twui.xml                    = the shipped twui.xml with the OLD line.
     These are the current files with THIS round's edits REVERSED.
  2. harness93.lua = harness92.lua with the env pair H92->H93 (+ H93_TWUI),
     the red banner reworded, the ABILITIES-capture hook added to the ipairs
     wrapper, and the new HARNESS-93 section appended after run_h92().
"""
import io, os, re, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = "C:/Users/vlady/Desktop/WH3_mod/mod_source"
LIVE_SRC = ROOT + "/script/battle/mod/zz_test_deadly_onslaught.lua"
ANN_SRC  = "C:/Users/vlady/Desktop/WH3_mod/docs/WH3_auto_ability_annotated.lua"
TWUI_SRC = ROOT + "/ui/common ui/special_ability_tooltip.twui.xml"

NL = chr(10)


def L(*lines):
    return NL.join(lines)


def read(p):
    return io.open(p, encoding="utf-8").read()


def write(p, s):
    io.open(p, "w", encoding="utf-8", newline="").write(s)


# --------------------------------------------------------------------------
# 1. THE PRE-EDIT SNAPSHOTS (reverse this round's edits)
# --------------------------------------------------------------------------
_block_re = re.compile(
    r"\n\n-- THE TOOLTIP LINE \(this round\).*?\n\}\n"
    r"for _, ability in ipairs\(ABILITIES\) do\n"
    r"\tability\.evaluate = FOURTH\.evaluators\[ability\.trigger\]\n"
    r"\tability\.tip = FOURTH\.TRIGGER_TIP\[ability\.trigger\]\nend", re.S)
_revert_loop = ("\nfor _, ability in ipairs(ABILITIES) do\n"
                "\tability.evaluate = FOURTH.evaluators[ability.trigger]\nend")

for src_path, out_name in ((LIVE_SRC, "pre93_live.lua"), (ANN_SRC, "pre93_ann.lua")):
    s = read(src_path)
    s2, n = _block_re.subn(_revert_loop, s, count=1)
    assert n == 1, "snapshot revert failed for %s (%d)" % (src_path, n)
    assert "FOURTH.TRIGGER_TIP" not in s2, "TRIGGER_TIP survived the revert"
    assert "ability.tip" not in s2, "ability.tip survived the revert"
    write(os.path.join(HERE, out_name), s2)
    print("wrote", out_name, len(s2), "bytes")

_s = read(TWUI_SRC)
_s2 = _s.replace(
    'text="Automatic: click the M/A badge to switch automatic use on or off"',
    'text="Automatic: this ability fires by itself while the unit charges - '
    'click the M/A badge to switch automatic use on or off"', 1)
assert _s2 != _s, "twui revert failed"
write(os.path.join(HERE, "pre93_twui.xml"), _s2)
print("wrote pre93_twui.xml", len(_s2), "bytes")

# --------------------------------------------------------------------------
# 2. harness93.lua from harness92.lua
# --------------------------------------------------------------------------
src = read(os.path.join(HERE, "harness92.lua"))
section = read(os.path.join(HERE, "h93_section.lua")).lstrip(NL)


def sub(old, new, label, count=1):
    global src
    n = src.count(old)
    assert n == count, "patch %s: %d matches (want %d)" % (label, n, count)
    src = src.replace(old, new, count)
    print("patch %s: applied" % label)


# P1: env pair (LIVE / ANN / RED_MODE; the twui path rides H93_TWUI inside the
# section, so the harness main chunk gains NO local - it sits at the 200 ceiling)
sub(L('-- HARNESS 92 (this round): the env pair is now H92_LIVE / H92_ANN.',
      'local LIVE = os.getenv("H92_LIVE") or "%s/script/battle/mod/zz_test_deadly_onslaught.lua"' % ROOT,
      'local ANN  = os.getenv("H92_ANN")  or "C:/Users/vlady/Desktop/WH3_mod/docs/WH3_auto_ability_annotated.lua"',
      'local RED_MODE = (os.getenv("H92_LIVE") ~= nil) or (os.getenv("H92_ANN") ~= nil)'),
    L('-- HARNESS 93 (this round): the env pair is now H93_LIVE / H93_ANN (the',
      '-- tooltip path rides H93_TWUI, read inside the section).',
      'local LIVE = os.getenv("H93_LIVE") or "%s/script/battle/mod/zz_test_deadly_onslaught.lua"' % ROOT,
      'local ANN  = os.getenv("H93_ANN")  or "C:/Users/vlady/Desktop/WH3_mod/docs/WH3_auto_ability_annotated.lua"',
      'local RED_MODE = (os.getenv("H93_LIVE") ~= nil) or (os.getenv("H93_ANN") ~= nil)'),
    "P1 env")

# P2: red banner reworded
sub(L('  print("   *** RED CONTROL MODE: pre-edit snapshot(s) in use - THE FINAL ROSTER BUILD (harness-92)")',
      '  print("   *** checks + the ADAPTED TABLE-SIZE COUNT PINS are the ones EXPECTED to fail: the section-0p tokens,")',
      '  print("   *** the P worlds (the new entries are simply absent on the 573-entry snapshot), and the pins that")',
      '  print("   *** now read the grown table (A4 579 per pass, B4 579, H68 579/605, C6c 579, S1 579/605, M6 579/605,")',
      '  print("   *** N13 579/605, 0h/0m 481/29, 0n 481/29). Every earlier world passes by design.***")'),
    L('  print("   *** RED CONTROL MODE: pre-edit snapshot(s) in use - THE PER-ABILITY TOOLTIP LINE (harness-93)")',
      '  print("   *** checks EXPECTED to fail: the section-0q map/wiring tokens, the D1 non-empty line, the D2 per-entry")',
      '  print("   *** match over the whole table and the D4b twui old-sentence check. The table size (579) and the")',
      '  print("   *** trigger-wording coverage pass on the snapshot by design (same table, same triggers).")',
      '  print("   *** Every earlier world passes by design.***")'),
    "P2 banner")

# P3: the ABILITIES-capture hook. The harness main chunk is at Lua's 200-local
# ceiling, so the capture rides the EXISTING OH77 table (OH77.cap) - no new local.
sub('  local is_marker = (type(first) == "table" and first.marker ~= nil)',
    L('  local is_marker = (type(first) == "table" and first.marker ~= nil)',
      '  -- HARNESS 93: the largest marker-bearing table ever passed to ipairs is',
      '  -- the ABILITIES table itself - captured for the per-entry tooltip check.',
      '  if is_marker and (OH77.cap == nil or #t > #OH77.cap) then OH77.cap = t end'),
    "P3 capture set")

# P4: RE-BASE the earlier rounds' red-branch aggregates for the advanced
# snapshot. The harness-93 red snapshot is the shipped harness-92 build (579
# entries), which already carries everything through round 92 - so every world
# of harnesses 82 / 88 / 89 / 90 / 92 now PASSES, and their old "expect some to
# fail" aggregates must become the N/A form (exactly as harness 92 re-based the
# harness-90 / 91 aggregates). No unexpected red-branch self-failures.

# P4a harness 82
sub(L('    -- LINEAGE ADAPTATION (harness 92): this round\'s red snapshot (the shipped',
      '    -- harness-91 build, 573 entries) already carries everything through the auto-327',
      '    -- sweep, so every C-world passes EXCEPT C6, whose wired-entry pin now reads the',
      '    -- grown 579-entry table (the snapshot still has 573).',
      '    check("RED CONTROL (harness 82): on the harness-92 pre-edit snapshot the harness-82 C-worlds still pass "',
      '      .. "EXCEPT C6, whose wired-entry pin now reads the grown 579-entry table (the snapshot still has 573) - "',
      '      .. n_ok .. "/16 world results, want 14)", n_ok == 14)'),
    L('    -- LINEAGE ADAPTATION (harness 93): this round\'s red snapshot (the shipped',
      '    -- harness-92 build, 579 entries) already carries everything through round 92,',
      '    -- so every harness-82 C-world passes - including C6, whose wired-entry pin',
      '    -- now reads the 579-entry table the snapshot actually has.',
      '    check("RED CONTROL (harness 82): N/A for the harness-93 round - the harness-93 red snapshot already "',
      '      .. "carries the grown 579-entry table, so C6 passes and every C-world passes - "',
      '      .. n_ok .. "/16 world results pass (want 16)", n_ok == 16)'),
    "P4a harness82 rebase")

# P4b harness 88
sub(L('    check("RED CONTROL (harness 88): on the pre-edit snapshot (the shipped harness-88 build, 189 entries) "',
      '      .. "this HARNESS-88 section\'s grown-table pin fails (S1 reads 193/199, the snapshot has 189/195); the "',
      '      .. "V/Q worlds all pass by design (their abilities already ship) - "',
      '      .. n_ok .. "/18 world results pass (want 16), fires " .. RED88.fires',
      '      .. ", claims " .. RED88.claims, n_ok == 16)'),
    L('    check("RED CONTROL (harness 88): N/A for the harness-93 round - the harness-93 red snapshot (the "',
      '      .. "shipped harness-92 build, 579 entries) already carries the grown table, so the S1 pin and every "',
      '      .. "V/Q world pass - "',
      '      .. n_ok .. "/18 world results pass (want 18), fires " .. RED88.fires',
      '      .. ", claims " .. RED88.claims, n_ok == 18)'),
    "P4b harness88 rebase")

# P4c harness 89
sub(L('    check("RED CONTROL (harness 89): on the pre-edit snapshot (the shipped harness-89 build, 193 entries) "',
      '      .. "the Enchanted Metallurgy abilities ALREADY SHIP, so the SILENT/SKIP worlds (M3 / M4 both files + the "',
      '      .. "ANNOTATED drift world M5, whose log-based legs pass vacuously in the reading copy) and the firing M1/M2 "',
      '      .. "worlds all pass; only the grown-table pins M6c/M6d fail (the snapshot has 193/199, the pin reads 262/272) - "',
      '      .. n_ok .. "/12 world results pass (want 10), fires " .. RED89.fires',
      '      .. ", claims " .. RED89.claims, n_ok == 10)'),
    L('    check("RED CONTROL (harness 89): N/A for the harness-93 round - the harness-93 red snapshot (the "',
      '      .. "shipped harness-92 build, 579 entries) already carries the Enchanted Metallurgy abilities AND the "',
      '      .. "grown table, so the M6c/M6d pins and every M-world pass - "',
      '      .. n_ok .. "/12 world results pass (want 12), fires " .. RED89.fires',
      '      .. ", claims " .. RED89.claims, n_ok == 12)'),
    "P4c harness89 rebase")

# P4d harness 90
sub(L('    check("RED CONTROL (harness 90): N/A for the harness-92 round - the harness-92 red snapshot already carries "',
      '      .. "the auto-327 sweep (the shipped harness-91 build), so the N-worlds fire by design; only the grown-table "',
      '      .. "pins N13d / N13e fail (the snapshot has 573/599, the pin reads 579/605) - " .. n_ok',
      '      .. "/32 world results pass (want 30), fires " .. RED90.fires',
      '      .. ", claims " .. RED90.claims, n_ok == 30)'),
    L('    check("RED CONTROL (harness 90): N/A for the harness-93 round - the harness-93 red snapshot (the shipped "',
      '      .. "harness-92 build, 579 entries) already carries the grown table, so the N13d/N13e pins and every "',
      '      .. "N-world pass - " .. n_ok',
      '      .. "/32 world results pass (want 32), fires " .. RED90.fires',
      '      .. ", claims " .. RED90.claims, n_ok == 32)'),
    "P4d harness90 rebase")

# P4e harness 92
sub(L('    check("RED CONTROL (harness 92): on the pre-edit snapshot (the shipped harness-91 build, 573 entries) the "',
      '      .. "grown-table pins and this HARNESS-92 section fail; the SILENT worlds pass trivially because the new "',
      '      .. "abilities are simply absent on the snapshot (P2 / P4 / P8 both files = 6) plus the ANNOTATED legs of the "',
      '      .. "drift worlds P5 / P9 (their live-only skip-log legs are masked in the reading copy) = 8 - " .. n_ok',
      '      .. "/20 world results pass (want 8), fires " .. RED92.fires .. ", claims " .. RED92.claims, n_ok == 8)'),
    L('    check("RED CONTROL (harness 92): N/A for the harness-93 round - the harness-93 red snapshot (the shipped "',
      '      .. "harness-92 build) already carries the round-92 roster, so the grown-table pins and every P-world pass - "',
      '      .. n_ok',
      '      .. "/20 world results pass (want 20), fires " .. RED92.fires .. ", claims " .. RED92.claims, n_ok == 20)'),
    "P4e harness92 rebase")

# P5: append the section after run_h92(), update the zero-search check text
sub('check("ZERO search calls by the mod across everything, harness 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90 and 91\'s worlds included (counted " .. find_calls .. ")',
    section + NL + 'check("ZERO search calls by the mod across everything, harness 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91 AND 92\'s worlds included (counted " .. find_calls .. ")',
    "P5 append section")

write(os.path.join(HERE, "harness93.lua"), src)
print("wrote harness93.lua", len(src), "bytes")
