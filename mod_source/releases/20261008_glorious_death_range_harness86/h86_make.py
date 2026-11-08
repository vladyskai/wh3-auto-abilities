# -*- coding: utf-8 -*-
"""Assemble harness86.lua from the SHIPPED harness85.lua.

The round-86 job: the GLORIOUS DEATH RANGE GATE.

Patches:
  P1  env rename H85 -> H86
  P2  the red-mode banner re-pointed at this round
  P3  the mock unit:unit_distance gains a dist_seq (a per-call SEQUENCE) so a
      world can model the ally DRIFTING out of range between decide and cast
  P4  splice the new HARNESS 86 section before the final find check
  P5  the final find-check wording names harness 82-85 too
"""
import io, os

HERE = os.path.dirname(os.path.abspath(__file__))
RELEASE_85 = os.path.join(HERE, "..", "20261005_glorious_death_selfcast_block3_harness85")
src = io.open(os.path.join(RELEASE_85, "harness85.lua"), encoding="utf-8").read()
section = io.open(os.path.join(HERE, "h86_section.lua"), encoding="utf-8").read()

def sub(old, new, label, count=1):
    global src
    n = src.count(old)
    assert n == count, "patch %s: %d matches (want %d)" % (label, n, count)
    src = src.replace(old, new, count)
    print("patch %s: applied" % label)

def cut(start, end, new, label):
    global src
    a = src.count(start)
    assert a == 1, "%s: start x%d" % (label, a)
    i = src.index(start)
    j = src.index(end, i)
    src = src[:i] + new + src[j:]
    print("patch %s: applied (cut %d chars)" % (label, j - i))

# ---- P1 env
sub('-- HARNESS 85 (this round): the env pair is now H85_LIVE / H85_ANN.\n'
    'local LIVE = os.getenv("H85_LIVE") or "C:/Users/vlady/Desktop/WH3_mod/mod_source/script/battle/mod/zz_test_deadly_onslaught.lua"\n'
    'local ANN  = os.getenv("H85_ANN")  or "C:/Users/vlady/Desktop/WH3_mod/docs/WH3_auto_ability_annotated.lua"\n'
    'local RED_MODE = (os.getenv("H85_LIVE") ~= nil) or (os.getenv("H85_ANN") ~= nil)',
    '-- HARNESS 86 (this round): the env pair is now H86_LIVE / H86_ANN.\n'
    'local LIVE = os.getenv("H86_LIVE") or "C:/Users/vlady/Desktop/WH3_mod/mod_source/script/battle/mod/zz_test_deadly_onslaught.lua"\n'
    'local ANN  = os.getenv("H86_ANN")  or "C:/Users/vlady/Desktop/WH3_mod/docs/WH3_auto_ability_annotated.lua"\n'
    'local RED_MODE = (os.getenv("H86_LIVE") ~= nil) or (os.getenv("H86_ANN") ~= nil)',
    "P1 env")

# ---- P2 banner
banner = (
'if RED_MODE then\n'
'  print("   *** RED CONTROL MODE: pre-edit snapshot(s) in use - the GLORIOUS-DEATH RANGE GATE (harness-86) checks are")\n'
'  print("   *** the ones EXPECTED to fail: the section-0i gate tokens in BOTH files (the wiki GLORIOUS_DEATH_RANGE_M")\n'
'  print("   *** constant, the gd_ally_gap / gd_ally_in_range helpers, the chosen-ally field), the live-only SKIPPED and")\n'
'  print("   *** chosen-ally log lines, and every R1-R5 world. On the snapshot the beyond-55m ally still FIRES (the")\n'
'  print("   *** reported bug, R2), the drifting ally still fires (R5) and no chosen-ally line exists (R3.live). Every")\n'
'  print("   *** other harness-85-era check PASSES: the snapshot already carries the Slayer list, the self-cast target,")\n'
'  print("   *** the 102-entry table and the no-hysteresis Ushoran rule. ***")'
)
cut('if RED_MODE then\n  print("   *** RED CONTROL MODE:', '\nend\nprint()\n', banner, "P2 banner")

# ---- P3 the mock unit:unit_distance (dist_seq)
sub('    function u:unit_distance(o) touch(); if def.dist ~= nil then return def.dist end return -1 end\n',
    '    function u:unit_distance(o)\n'
    '      touch()\n'
    '      -- HARNESS 86: the range gate RE-READS the gap immediately before the\n'
    '      -- cast, so a world can model DRIFT by giving a SEQUENCE: dist_seq[i] is\n'
    '      -- the i-th call\'s answer, and the LAST value repeats thereafter. A plain\n'
    '      -- def.dist (or no dist at all) behaves EXACTLY as before.\n'
    '      if def.dist_seq ~= nil then\n'
    '        def.dist_i = (def.dist_i or 0) + 1\n'
    '        local v = def.dist_seq[def.dist_i]\n'
    '        if v == nil then v = def.dist_seq[#def.dist_seq] end\n'
    '        return v\n'
    '      end\n'
    '      if def.dist ~= nil then return def.dist end\n'
    '      return -1\n'
    '    end\n',
    "P3 dist_seq")

# ---- P6 re-base the older rounds' red aggregates (their snapshot advanced one round)
sub("""    -- LINEAGE ADAPTATION (harness 85): this round's red snapshot (pre85)
    -- already carries the block-1 batch + item 8 and the grown table, so every
    -- C-world passes by design EXCEPT C6 (whose full-table count pin moved
    -- 64 -> 102, so its world result is false on the snapshot).
    check("RED CONTROL (harness 82): N/A for the harness-85 round - the pre-edit snapshot already carries the "
      .. "block-1 batch + item 8 and the grown table, so every C-world passes by design except C6 (its count "
      .. "pin moved 64 -> 102) (" .. n_ok .. "/16 world results, want 14)", n_ok == 14)""",
"""    -- LINEAGE ADAPTATION (harness 86): this round's red snapshot (the shipped
    -- harness-85 build) already carries BLOCK 3 too, so its full-table count pin
    -- (102) now MATCHES - every C-world passes by design.
    check("RED CONTROL (harness 82): N/A for the harness-86 round - the pre-edit snapshot already carries the "
      .. "block-1 batch + item 8 and block 3's grown 102-entry table, so every C-world passes by design ("
      .. n_ok .. "/16 world results, want 16)", n_ok == 16)""",
    "P6a h82 red")

sub("""    -- LINEAGE ADAPTATION (harness 85): this round's red snapshot (pre85)
    -- already carries BLOCK 2 + the harness-84 corrections, so S1/E1/F1/S2/U1
    -- pass by design and G2's ANNOTATED self arm already self-cast - only the
    -- rewritten self-cast G1 and the LIVE half of G2 fail.
    check("RED CONTROL (harness 83): N/A for the harness-85 round - the pre-edit snapshot already carries "
      .. "block 2 + the harness-84 corrections, so S1/E1/F1/S2/U1 pass by design and G2's annotated self arm "
      .. "already self-cast, while the rewritten self-cast G1 and the live half of G2 fail: " .. n_ok
      .. "/14 world results pass (want 11); the round's section-0h checks and the adapted count/reason pins also fail",
      n_ok == 11)""",
"""    -- LINEAGE ADAPTATION (harness 86): this round's red snapshot (the shipped
    -- harness-85 build) already carries BLOCK 2 + the harness-84 corrections AND
    -- the harness-85 self-cast fix, so every G-world passes by design.
    check("RED CONTROL (harness 83): N/A for the harness-86 round - the pre-edit snapshot already carries "
      .. "block 2 + the harness-84 corrections and the harness-85 self-cast fix, so S1/E1/F1/S2/U1 and the "
      .. "rewritten self-cast G1/G2 all pass by design: " .. n_ok
      .. "/14 world results pass (want 14)",
      n_ok == 14)""",
    "P6b h83 red")

sub("""    check("RED CONTROL (harness 84): on the pre-edit snapshot the Slayer list + the no-hysteresis Ushoran rule "
      .. "ALREADY SHIP, so W0 and the shared-SILENT worlds W3/W5 pass by design, and W2's annotated self arm already "
      .. "self-cast - only the REWRITTEN self-cast W1/W4 and the live half of W2 fail - " .. n_ok
      .. "/12 world results pass (want 7), new fires " .. RED84.fires .. ", new claims " .. RED84.claims,
      n_ok == 7)""",
"""    check("RED CONTROL (harness 84): on the pre-edit snapshot the Slayer list + the no-hysteresis Ushoran rule "
      .. "AND the harness-85 self-cast fix ALREADY SHIP, so every W-world passes by design - " .. n_ok
      .. "/12 world results pass (want 12), new fires " .. RED84.fires .. ", new claims " .. RED84.claims,
      n_ok == 12)""",
    "P6c h84 red")

sub("""    check("RED CONTROL (harness 85): on the pre-edit snapshot the round's changes are ABSENT - the block-3 "
      .. "entries are missing (S3/F3 fail), Glorious Death still casts on the Slayer ally (X1/X2 fail, and X3's "
      .. "live reason), and the count pins still read 64/70 while the adapted pins expect 102/108. X3's ANNOTATED "
      .. "result passes by design (the pre-edit self arm already self-cast) - " .. n_ok
      .. "/10 world results pass (want 1), new fires " .. RED85.fires .. ", new claims " .. RED85.claims,
      n_ok == 1)""",
"""    check("RED CONTROL (harness 85): N/A for the harness-86 round - this round's red snapshot IS the shipped "
      .. "harness-85 build, so the block-3 entries, the self-cast target and the 102/108 count pins are ALREADY "
      .. "SHIP - every X1/X2/X3/S3/F3 world passes by design - " .. n_ok
      .. "/10 world results pass (want 10), new fires " .. RED85.fires .. ", new claims " .. RED85.claims,
      n_ok == 10)""",
    "P6d h85 red")

# ---- P4 splice the new section before the final find check
sub('run_h85()\n\ncheck("ZERO search calls by the mod across everything, harness 71, 72, 73, 74, 75, 76, 77, 78, 79, 80 and 81\'s worlds included',
    'run_h85()\n\n' + section + '\ncheck("ZERO search calls by the mod across everything, harness 71, 72, 73, 74, 75, 76, 77, 78, 79, 80 and 81\'s worlds included',
    "P4 splice section")

# ---- P5 the final find-check wording
sub("harness 71, 72, 73, 74, 75, 76, 77, 78, 79, 80 and 81's worlds included",
    "harness 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84 and 85's worlds included",
    "P5 find-check wording")

out = os.path.join(HERE, "harness86.lua")
io.open(out, "w", encoding="utf-8", newline="\n").write(src)
print("harness86.lua written:", len(src), "bytes,", src.count("\n"), "lines")
