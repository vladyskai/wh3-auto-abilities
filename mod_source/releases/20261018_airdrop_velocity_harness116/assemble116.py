#!/usr/bin/env python3
"""Assemble harness116.lua from harness115.lua.

* renames H115_LIVE/H115_ANN -> H116_LIVE/H116_ANN (the red-control env hooks);
* rewrites the air-drop tooltip sentence in harness 93's TIP map (the wording
  the entries are validated against) and the two prefix pins that quote it;
* rebases the harness-115 section-0 pins that the round-116 change flips (the
  two dynamic constants, the pair row's new evidence, the stamp call and the
  annotated copy's helper signature);
* splices the round-116 section before the final summary.
"""
import sys

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261018_airdrop_dwell_harness115\harness115.lua"
SEC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261018_airdrop_velocity_harness116\h116_section.lua"
OUT = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261018_airdrop_velocity_harness116\harness116.lua"


def rd(p):
    with open(p, "rb") as f:
        return f.read().decode("utf-8")


def must(s, old, new, count=1):
    n = s.count(old)
    assert n == count, "replace %r matched %d (want %d)" % (old[:70], n, count)
    return s.replace(old, new)


s = rd(SRC)

# ---- 1. the red-control env hooks ------------------------------------------
s = s.replace("H115_LIVE", "H116_LIVE").replace("H115_ANN", "H116_ANN")

# ---- 2. the tooltip sentence (harness 93's TIP map + its two prefix pins) --
OLD_FULL = ('air_drop_on_infantry = "When armed, fires when the nearest enemy unit with more '
            'than 10 models stays within 0.1 m of this unit\'s edge for 1 second, airborne '
            'where the ability requires it",')
NEW_FULL = ('air_drop_on_infantry = "When armed, fires when the nearest enemy unit with more '
            'than 10 models closes to 0.1 m of this unit\'s edge, after a wait measured from '
            'that enemy\'s velocity at the moment of contact: 0 s if it is running at this '
            'unit, 1 s if it is stationary or crossing, 2 s if it is running away, airborne '
            'where the ability requires it",')
s = must(s, OLD_FULL, NEW_FULL)

s = must(s, 'models stays within 0.1 m"', 'models closes to 0.1 m"', 3)
s = must(s, '      and raw_find(s2, "stays within 0.1 m of this unit\'s edge for 1 second", 1, true) ~= nil)',
         '      and raw_find(s2, "after a wait measured from that enemy\'s velocity", 1, true) ~= nil)')

# ---- 3. harness 115's section-0 pins the round flips -----------------------
# 3a. the annotated copy's helper signature
s = must(s,
         '        and raw_find(s2, "function FOURTH.ad_pair_stamp(cid, eid)", 1, true) ~= nil',
         '        and raw_find(s2, "function FOURTH.ad_pair_stamp(cid, eid, delay, proj, src)", 1, true) ~= nil')

# 3b. the span head for the stamp
s = must(s,
         '    local stamp = span(s2, "function FOURTH.ad_pair_stamp(cid, eid)", "\\nend")',
         '    local stamp = span(s2, "function FOURTH.ad_pair_stamp(cid, eid, delay, proj, src)", "\\nend")')

# 3c. the two constants
s = must(s,
         '''    check("0 " .. nm .. ": the TWO dwell constants are defined EXACTLY ONCE (1.0 s dwell / 0.3 s floor)",
      cp(s2, "\\nFOURTH.AIR_DROP_DWELL_S = 1.0\\n") == 1
      and cp(s2, "\\nFOURTH.AIR_DROP_MIN_CONTACT_S = 0.3\\n") == 1)''',
         '''    check("0 " .. nm .. ": the TWO dynamic-delay constants are defined EXACTLY ONCE (1.0 s mid / 1.0 s swing)",
      cp(s2, "\\nFOURTH.AIR_DROP_DWELL_MID_S = 1.0\\n") == 1
      and cp(s2, "\\nFOURTH.AIR_DROP_DWELL_SWING_S = 1.0\\n") == 1
      and cp(s2, "\\nFOURTH.AIR_DROP_MIN_CONTACT_S = 0.3\\n") == 1)''')

# 3d. the pair row now carries the measurement
s = must(s,
         '''    check("0 " .. nm .. ": the pair state is NESTED (no composite key) and carries ONE timestamp",
      cp(s2, "FOURTH.ad_pair = {}\\n") == 1
      and cp(s2, "function FOURTH.ad_pair_key(unit, enemy)") == 1
      and stamp ~= nil and raw_find(stamp, "per[eid] = { first = tick_count }", 1, true) ~= nil
      and raw_find(s2, '.. "|" ..', 1, true) == nil)''',
         '''    check("0 " .. nm .. ": the pair state is NESTED (no composite key) and carries the measurement",
      cp(s2, "FOURTH.ad_pair = {}\\n") == 1
      and cp(s2, "function FOURTH.ad_pair_key(unit, enemy)") == 1
      and stamp ~= nil
      and raw_find(stamp, "per[eid] = { first = tick_count, delay = delay, proj = proj, src = src }", 1, true) ~= nil
      and raw_find(s2, '.. "|" ..', 1, true) == nil)''')

# 3e. the stamp call carries the measurement
s = must(s,
         '      and raw_find(pick, "FOURTH.ad_pair_stamp(cid, eid)", 1, true) ~= nil',
         '      and raw_find(pick, "FOURTH.ad_pair_stamp(cid, eid, delay, proj, vsrc)", 1, true) ~= nil')

# 3f. (the tooltip pin is already rebased by step 2: its prefix quotes the new
# sentence and its second fragment now asks for "after a wait measured from
# that enemy's velocity")

# ---- 4. the seam -----------------------------------------------------------
old_tail = '\nrun_h112()\nrun_h114()\nrun_h115()\n\nprint("checks: "'
assert s.count(old_tail) == 1, s.count(old_tail)
sec = rd(SEC)
s = s.replace(old_tail, "\n" + sec + "\nrun_h112()\nrun_h114()\nrun_h115()\nrun_h116()\n\nprint(\"checks: \"")

with open(OUT, "wb") as f:
    f.write(s.encode("utf-8"))
print("wrote %s  %d bytes  %d lines  check( calls %d" %
      (OUT, len(s.encode("utf-8")), s.count("\n") + 1, s.count("check(")))
