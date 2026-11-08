# -*- coding: utf-8 -*-
"""Assemble harness87.lua from the SHIPPED harness86.lua.

The round-87 job: GLORIOUS DEATH's trigger range 55 m -> 25 m (conservative).

Patches:
  P1  env rename H86 -> H87
  P2  the red-mode banner re-pointed at this round
  P3  REPLACE the spliced HARNESS-86 range-gate section with the re-baselined
      HARNESS-87 section (worlds re-based for the 25 m threshold + the 24/26 m
      boundary pair). The mock dist_seq added in round 86 is kept as-is.
  P4  the final find-check wording names harness 86 too
"""
import io, os

HERE = os.path.dirname(os.path.abspath(__file__))
src = io.open(os.path.join(HERE, "harness86_source.lua"), encoding="utf-8").read()
section = io.open(os.path.join(HERE, "h87_section.lua"), encoding="utf-8").read()

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
    j = src.index(end, i) + len(end)   # the end marker is REPLACED too
    src = src[:i] + new + src[j:]
    print("patch %s: applied (cut %d chars)" % (label, j - i))

# ---- P1 env
sub('-- HARNESS 86 (this round): the env pair is now H86_LIVE / H86_ANN.\n'
    'local LIVE = os.getenv("H86_LIVE") or "C:/Users/vlady/Desktop/WH3_mod/mod_source/script/battle/mod/zz_test_deadly_onslaught.lua"\n'
    'local ANN  = os.getenv("H86_ANN")  or "C:/Users/vlady/Desktop/WH3_mod/docs/WH3_auto_ability_annotated.lua"\n'
    'local RED_MODE = (os.getenv("H86_LIVE") ~= nil) or (os.getenv("H86_ANN") ~= nil)',
    '-- HARNESS 87 (this round): the env pair is now H87_LIVE / H87_ANN.\n'
    'local LIVE = os.getenv("H87_LIVE") or "C:/Users/vlady/Desktop/WH3_mod/mod_source/script/battle/mod/zz_test_deadly_onslaught.lua"\n'
    'local ANN  = os.getenv("H87_ANN")  or "C:/Users/vlady/Desktop/WH3_mod/docs/WH3_auto_ability_annotated.lua"\n'
    'local RED_MODE = (os.getenv("H87_LIVE") ~= nil) or (os.getenv("H87_ANN") ~= nil)',
    "P1 env")

# ---- P2 banner (replaces the whole banner block INCLUDING its end/print tail)
banner = (
'if RED_MODE then\n'
'  print("   *** RED CONTROL MODE: pre-edit snapshot(s) in use - the GLORIOUS-DEATH TRIGGER-RANGE (harness-87) checks")\n'
'  print("   *** are the ones EXPECTED to fail: the section-0i tokens that pin the NEW 25 m value and its")\n'
'  print("   *** conservative-trigger comment, plus the worlds whose verdict differs at the OLD 55 m - R2 (the")\n'
'  print("   *** 55 m ally still FIRES on the snapshot = the field-test complaint), R5 (its 55 m cast leg is still")\n'
'  print("   *** in range, so no skip) and R7 (the 26 m boundary ally fires). R1/R3/R4/R6 pass by design - the")\n'
'  print("   *** snapshot already carries the range gate, the closest-ally choice and the drift re-check, just at")\n'
'  print("   *** 55 m, and every other harness-85-era check passes too. ***")\n'
'end\n'
'print()\n'
)
cut('if RED_MODE then\n  print("   *** RED CONTROL MODE:', '\nend\nprint()\n', banner, "P2 banner")

# ---- P3 replace the HARNESS 86 section with the re-baselined HARNESS 87 section
cut('-- ============================================================================\n'
    '-- HARNESS 86 - THE GLORIOUS DEATH RANGE GATE',
    '\nrun_h86()\n',
    section, "P3 splice section")

# ---- P4 the final find-check wording
sub("harness 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84 and 85's worlds included",
    "harness 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85 and 86's worlds included",
    "P4 find-check wording")

assert "run_h86" not in src, "a stale run_h86 reference survives"
assert "HARNESS 86 - THE GLORIOUS DEATH RANGE GATE" not in src, "the old section header survives"

out = os.path.join(HERE, "harness87.lua")
io.open(out, "w", encoding="utf-8", newline="\n").write(src)
print("harness87.lua written:", len(src), "bytes,", src.count("\n"), "lines")
