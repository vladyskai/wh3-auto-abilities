#!/usr/bin/env python3
"""Assemble harness115.lua from harness114.lua.

* renames H114_LIVE/H114_ANN -> H115_LIVE/H115_ANN (the red-control env hooks);
* rebases the ONE static pin the tooltip change flips, in BOTH copies' section 0
  and in harness 93's TIP map, plus the ad_tag site count (6 -> 7: the dwell
  event helper is a new site);
* answers harness 114's A-J worlds N/A (88 check slots, count preserved) - they
  asserted the round-114 rule as an INSTANT comparison, which the 1-second dwell
  replaces by design;
* answers round 107's three air-drop serialisation assertions N/A (S2a/S2b/S3a)
  for the same reason, through a renamed check call (count preserved);
* splices the round-115 section before the final summary.
"""
import sys

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261018_airdrop_edgesimple_harness114\harness114.lua"
SEC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261018_airdrop_dwell_harness115\h115_section.lua"
OUT = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261018_airdrop_dwell_harness115\harness115.lua"


def rd(p):
    with open(p, "rb") as f:
        return f.read().decode("utf-8")


def must(s, old, new, count=1):
    n = s.count(old)
    assert n == count, "replace %r matched %d (want %d)" % (old[:70], n, count)
    return s.replace(old, new)


s = rd(SRC)

# ---- 1. the red-control env hooks ------------------------------------------
s = s.replace("H114_LIVE", "H115_LIVE").replace("H114_ANN", "H115_ANN")

# ---- 2. harness 93's TIP map: the air-drop sentence now states the dwell ----
OLD_TIP = ('air_drop_on_infantry = "When armed, fires when the nearest enemy unit with more '
           'than 10 models is within 0.1 m of this unit\'s edge, airborne where the ability '
           'requires it",')
NEW_TIP = ('air_drop_on_infantry = "When armed, fires when the nearest enemy unit with more '
           'than 10 models stays within 0.1 m of this unit\'s edge for 1 second, airborne '
           'where the ability requires it",')
s = must(s, OLD_TIP, NEW_TIP)

# ---- 3. the harness-114 section-0 pins the round flips ----------------------
s = must(s,
         'models is within 0.1 m", 1, true) ~= nil)',
         'models stays within 0.1 m", 1, true) ~= nil)',
         2)
s = must(s, 'check("0 live: every decision + transition line carries the caster ui id (ad_tag definition + 5 sites)",\n        cp(s2, "FOURTH.ad_tag(unit)") == 6)',
         'check("0 live: every decision + transition line carries the caster ui id (ad_tag definition + 6 sites)",\n        cp(s2, "FOURTH.ad_tag(unit)") == 7)')

# ---- 4. round 107's serialisation assertions -> N/A (count preserved) ------
s = must(s, """  local function check107na(a, b)
    check("HARNESS 107 (round 114 supersession) N/A: " .. tostring(a), true)
  end""",
"""  local function check107na(a, b)
    check("HARNESS 107 (round 114 supersession) N/A: " .. tostring(a), true)
  end
  -- ROUND 115: round 107's air-drop serialisation worlds fired on ONE poll
  -- (round 114's instant comparison). Under the 1-second dwell a single poll
  -- cannot fire at all and a same-marker repeat has to earn a FRESH dwell, so
  -- their three assertions answer N/A here; the gate chain they exercised is
  -- re-proved for real by the harness-115 section (worlds H1-H5).
  local function check115s(a, b)
    check("HARNESS 107 air-drop serialisation (round 115 supersession) N/A: " .. tostring(a), true)
  end""")
s = must(s, '        check(TAG .. "S2a: the SAME ability repeats after its own 2 s guard (fires " .. #W.fires .. ")",',
         '        check115s(TAG .. "S2a: the SAME ability repeats after its own 2 s guard (fires " .. #W.fires .. ")",')
s = must(s, '        check(TAG .. "S2b: exactly 8 polls apart - the unit window adds nothing to a same-marker repeat",',
         '        check115s(TAG .. "S2b: exactly 8 polls apart - the unit window adds nothing to a same-marker repeat",')
s = must(s, '        check(TAG .. "S3a: BOTH casters fire in the same poll - the window is per unit, not global (" .. n .. ")",',
         '        check115s(TAG .. "S3a: BOTH casters fire in the same poll - the window is per unit, not global (" .. n .. ")",')

# ---- 5. harness 114's A-J worlds -> 88 N/A slots ---------------------------
a = s.index('  print("== HARNESS 114 - A: 0.09 m FIRES')
b = s.index('  if red114 then')
NA = '''  -- ==========================================================================
  -- ROUND 115 SUPERSESSION. Harness 114's A-J worlds asserted the round-114
  -- rule as an INSTANT comparison: one poll at 0.09 m fired. Under the
  -- 1-second dwell a single poll cannot fire at all, so those worlds are
  -- answered N/A here with the SAME 88 check slots (the running count and every
  -- later boundary pin are unchanged). The rule they proved - the candidate
  -- filter, the nearest-by-unit_distance pick, the air-only / no-melee holds,
  -- the fail-closed reads and the pre-cast re-check - is re-proved dwell and
  -- all by the harness-115 worlds A-F below.
  -- ==========================================================================
  for _ = 1, 88 do
    check("HARNESS 114 A-J world (round 115 supersession) N/A - the instant-fire worlds"
      .. " were replaced by the 1-second dwell, re-proved in the harness-115 section", true)
  end

'''
s = s[:a] + NA + s[b:]

# ---- 6. the seam -----------------------------------------------------------
old_tail = '\nrun_h112()\nrun_h114()\n\nprint("checks: "'
assert s.count(old_tail) == 1, s.count(old_tail)
sec = rd(SEC)
s = s.replace(old_tail, "\n" + sec + "\nrun_h112()\nrun_h114()\nrun_h115()\n\nprint(\"checks: \"")

with open(OUT, "wb") as f:
    f.write(s.encode("utf-8"))
print("wrote %s  %d bytes  %d lines  check( calls %d" %
      (OUT, len(s.encode("utf-8")), s.count("\n") + 1, s.count("check(")))
