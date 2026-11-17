#!/usr/bin/env python3
"""Build harness166.lua from harness165.lua for round 167 (no final period, the safer defaults). Older harnesses are
never edited.

Rebases (the user's ruling 2026-11-17: "Do you need to put a point at the end of a sentence when there is no sentence
after it? Please remove the point. Check the other tooltips also."):
  * h152 AP2a and h153 BT1a: the ALL tooltip is searched for without the final period.
  * h164 CD1 and h165 SC1: a card must NOT end with '.' (it had to).
  * h164 CD2, h165 SC2 and TT2: the pinned card texts lose their final period.
  * h165 0zz13 and AL2: the bare return reads 'table.concat(parts, "; ")' and the ALL text has no period.
"""
import os
import re

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261117_short_cards_harness165\harness165.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261117_periods_risky_harness166\harness166.lua"
SECTION = open(r"C:\Users\vlady\Desktop\WH3_mod\tools\h166_section.lua", encoding="utf-8").read()
BANNER = """-- ============================================================================
-- HARNESS 166 - ROUND 167: NO FINAL PERIOD ON THE TOOLTIPS, AND THE SAFER
--   DEFAULTS (rampage and self-damage abilities start on M).
--   Edited vs harness165: this banner, the rebases listed in tools/make_harness166.py
--   (AP2a, BT1a, CD1, CD2, SC1, SC2, TT2, 0zz13, AL2), run_h166 and its call.
--   RED control: H166_LIVE / H166_ANN on docs/backups/round167/pre167_*.lua.
-- ============================================================================
"""
ALL_OLD = "Arm or disarm every automatic ability of the selected unit(s)."
ALL_NEW = "Arm or disarm every automatic ability of the selected unit(s)"
R = [
    ('raw_find(rec.tooltip, "%s", 1, true) ~= nil)   -- HARNESS 165: the short ALL text\n' % ALL_OLD,
     'raw_find(rec.tooltip, "%s", 1, true) ~= nil)   -- HARNESS 166: no final period\n' % ALL_NEW, 2),
    ('          and c:sub(-1) == "." and raw_find(c, "{", 1, true) == nil and raw_find(c, "[", 1, true) == nil\n',
     '          and c:sub(-1) ~= "." and raw_find(c, "{", 1, true) == nil and raw_find(c, "[", 1, true) == nil   -- HARNESS 166\n', 1),
    ('        local ok = type(c) == "string" and c:sub(1, 6) == "Fires " and c:sub(-1) == "." and #c <= 160\n',
     '        local ok = type(c) == "string" and c:sub(1, 6) == "Fires " and c:sub(-1) ~= "." and #c <= 160   -- HARNESS 166\n', 1),
    ('  local ALL_NEW = "%s"\n' % ALL_OLD, '  local ALL_NEW = "%s"   -- HARNESS 166: no final period\n' % ALL_NEW, 1),
    ("        and cp(s, '\\treturn table.concat(parts, \"; \") .. \".\"') == 1\n",
     "        and cp(s, '\\treturn table.concat(parts, \"; \")   -- ROUND 166') == 1   -- HARNESS 166: no final period\n", 1),
]
src = open(SRC, encoding="utf-8").read()
for a, b, n in R:
    assert src.count(a) == n, (a[:80], src.count(a))
    src = src.replace(a, b)


def strip_block(s, start, stop):
    """drop the final period of every card literal between start and the next stop"""
    i = s.index(start)
    j = s.index(stop, i)
    blk = s[i:j]
    new = re.sub(r'\.(")', r"\1", blk)   # '...text."' -> '...text"'
    assert new != blk
    return s[:i] + new + s[j:], blk.count('."') - new.count('."')


# the two exact blocks (h164 CD2, h165 SC2) and the h165 TT2 line
src, n1 = strip_block(src, '      local exact = by.deadly_onslaught == "Fires when charging or in melee."\n        and by.entice == "Fires in melee unless wavering; not below 50% health."\n        and by.bloodbeast == "Fires in melee unless wavering, clear of allies."\n        and has(',
                      'check(TAG .. "CD2')
src, n2 = strip_block(src, '      local exact = by.deadly_onslaught == "Fires when charging or in melee."\n        and by.entice == "Fires in melee unless wavering; not below 50% health."\n        and by.bloodbeast == "Fires in melee unless wavering, clear of allies."\n        and by.heavens_gate',
                      'check(TAG .. "SC2')
TT_OLD = 'tip == by.entice and tip == "Fires in melee unless wavering; not below 50% health.")'
assert src.count(TT_OLD) == 1
src = src.replace(TT_OLD, 'tip == by.entice and tip == "Fires in melee unless wavering; not below 50% health")')
print("periods dropped:", n1, n2)
RUNNER_ANCHOR = "\n-- THE RUNNER. The air-drop sections always run;"
assert src.count(RUNNER_ANCHOR) == 1
src = src.replace(RUNNER_ANCHOR, "\n" + SECTION + RUNNER_ANCHOR)
assert src.count("\nrun_h165()\n") == 1
src = src.replace("\nrun_h165()\n", "\nrun_h165()\nrun_h166()\n")
src = BANNER + src
assert "\u2014" not in BANNER + SECTION
os.makedirs(os.path.dirname(DST), exist_ok=True)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST, len(src), "bytes")
