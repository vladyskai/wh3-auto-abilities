# -*- coding: utf-8 -*-
"""HARNESS 96 build: assemble harness96.lua from the SHIPPED harness95.lua.

The round-96 job: the ACCUSATION MOVE-ORDER ROOT CAUSE. The offer test now
uses the 70% CONSTANT ONLY (unit:unit_distance(enemy) <= FOURTH.ACCUSATION_RANGE_M
= 52 m) and the engine's unit_in_range reach read is removed from the offer
path; the log prints the REAL computed distance at the target choice and the
pre-cast re-check. A NEW section 0t proves the state of the source and five R
worlds prove the behaviour (the 81.3 m regression, inside/outside the bound,
the real-distance log, and the engine-flag-false case), plus a red control.
The pre96_*.lua snapshots (the shipped harness-95 build) are the RED target;
harness-95's own boundary-count pin is re-based to the N/A form here.
"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
H95 = "C:/Users/vlady/Desktop/WH3_mod/mod_source/releases/20261010_range_rule_harness95"
NL = chr(10)


def read(p):
    return io.open(p, encoding="utf-8", newline="").read()


def write(p, s):
    io.open(p, "w", encoding="utf-8", newline="").write(s)


src = read(H95 + "/harness95.lua")


def sub(old, new, label, count=1):
    global src
    n = src.count(old)
    assert n == count, "%s: %d matches (want %d)" % (label, n, count)
    src = src.replace(old, new, count)
    print("patch %s: applied" % label)


def L(*lines):
    return NL.join(lines)


# --------------------------------------------------------------------------
# 1. env pair H95 -> H96
# --------------------------------------------------------------------------
sub(L('-- HARNESS 95 (this round): the env pair is now H95_LIVE / H95_ANN.',
      'local LIVE = os.getenv("H95_LIVE") or "C:/Users/vlady/Desktop/WH3_mod/mod_source/script/battle/mod/zz_test_deadly_onslaught.lua"',
      'local ANN  = os.getenv("H95_ANN")  or "C:/Users/vlady/Desktop/WH3_mod/docs/WH3_auto_ability_annotated.lua"',
      'local RED_MODE = (os.getenv("H95_LIVE") ~= nil) or (os.getenv("H95_ANN") ~= nil)'),
    L('-- HARNESS 96 (this round): the env pair is now H96_LIVE / H96_ANN.',
      'local LIVE = os.getenv("H96_LIVE") or "C:/Users/vlady/Desktop/WH3_mod/mod_source/script/battle/mod/zz_test_deadly_onslaught.lua"',
      'local ANN  = os.getenv("H96_ANN")  or "C:/Users/vlady/Desktop/WH3_mod/docs/WH3_auto_ability_annotated.lua"',
      'local RED_MODE = (os.getenv("H96_LIVE") ~= nil) or (os.getenv("H96_ANN") ~= nil)'),
    "env pair")

# --------------------------------------------------------------------------
# 2. the red-mode banner
# --------------------------------------------------------------------------
sub(L('  print("   *** RED CONTROL MODE: pre-edit snapshot(s) in use - THE STANDING 70% RANGE RULE (harness-95)")',
      '  print("   *** checks EXPECTED to fail: the section-0s tokens (no FOURTH.RANGE_FRACTION, the old range")',
      '  print("   *** values still in place) and the half of the boundary worlds that sit INSIDE the NEW bound,")',
      '  print("   *** plus every earlier pin whose value moved (GD 25->38, VM/MT/WV 25->24, BS/EDR 25->70,")',
      '  print("   *** ACC 75->52). Every earlier WORLD passes by design.***")'),
    L('  print("   *** RED CONTROL MODE: pre-edit snapshot(s) in use - THE ACCUSATION MOVE-ORDER ROOT CAUSE (harness-96)")',
      '  print("   *** checks EXPECTED to fail: the section-0t tokens (the offer test still trusts the engine\'s")',
      '  print("   *** unit_in_range) and the R worlds that need the constant-only test - R1 (the 81.3 m")',
      '  print("   *** regression FIRES on the snapshot), R5 (the engine flag false keeps it silent) and R4\'s")',
      '  print("   *** live log (no real distance). Every earlier WORLD passes by design (harness-95\'s own")',
      '  print("   *** boundary-count pin is re-based to the N/A form here).***")'),
    "banner")

# --------------------------------------------------------------------------
# 3. re-base harness-95's own boundary-count pin (its snapshot is now h95)
# --------------------------------------------------------------------------
sub(L('  else',
      '    check("RED CONTROL (harness 95): on the pre-edit snapshot (the shipped harness-94 build: GD 25, VM 25, MT 25, "',
      '      .. "WV 25, BS 25, EDR 25, ACC 75) the 0s tokens fail and only the worlds whose target sits OUTSIDE the OLD "',
      '      .. "bound pass by design (G2/V1/M1/W1/B2/E2/A1) - the worlds INSIDE the new bound fire nothing on the "',
      '      .. "snapshot: " .. n_ok .. "/" .. #res .. " world results pass (want 14), fires "',
      '      .. RED95.fires .. ", claims " .. RED95.claims, n_ok == 14)',
      '  end'),
    L('  else',
      '    check("RED CONTROL (harness 95): N/A for the harness-96 round - the harness-96 red snapshot (the shipped "',
      '      .. "harness-95 build) already IS the 70% range rule, so every boundary world passes by design: " .. n_ok',
      '      .. "/" .. #res .. " world results pass (want " .. #res .. "), fires "',
      '      .. RED95.fires .. ", claims " .. RED95.claims, n_ok == #res)',
      '  end'),
    "h95 boundary pin re-base")

# --------------------------------------------------------------------------
# 4. append the new HARNESS-96 section after run_h95()
# --------------------------------------------------------------------------
section = read(HERE + "/h96_section.lua").lstrip(NL)
sub(NL + "run_h95()" + NL,
    NL + "run_h95()" + NL + NL + section + NL,
    "append section")

# --------------------------------------------------------------------------
# 5. extend the tail token list
# --------------------------------------------------------------------------
sub("92, 93 AND 94's worlds included",
    "92, 93, 94 AND 95's worlds included",
    "tail list")

write(HERE + "/harness96.lua", src)
print("wrote harness96.lua", len(src), "bytes")
