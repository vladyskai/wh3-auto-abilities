#!/usr/bin/env python3
"""Build harness154.lua from harness153.lua for round 155. Older harnesses are never edited.

Pin rebases (documented in docs/WH3_round155_all_spot.md): the ALL spot (-855, -21) -> (-923, 0), the spot the user
tuned by hand in battle, in sections 151 (0zx, AP1a), 152 (0zy, AP2a) and 153 (0zz, BT1a); BT3a's nudge from the
base spot: zz_all_nudge(5, -3) now lands at -918,-3 (was -850,-24)."""
import os

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261115_all_button_harness153\harness153.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261115_all_spot_harness154\harness154.lua"
SECTION = open(r"C:\Users\vlady\Desktop\WH3_mod\tools\h154_section.lua", encoding="utf-8").read()
BANNER = """-- ============================================================================
-- HARNESS 154 - ROUND 155: THE ALL BUTTON AT THE SPOT THE USER TUNED BY HAND
--   IN BATTLE, (-923, 0).
--   Edited vs harness153: this banner, the rebases in tools/make_harness154.py,
--   run_h154 and its call.
--   RED control: H154_LIVE / H154_ANN on docs/backups/round155/pre155_*.lua.
-- ============================================================================
"""
src = open(SRC, encoding="utf-8").read()
R = [
    ('raw_find(s, "FOURTH.ALL_OX, FOURTH.ALL_OY = -855, -21", 1, true) ~= nil)   -- ROUND 154: the round button\n',
     'raw_find(s, "FOURTH.ALL_OX, FOURTH.ALL_OY = -923, 0", 1, true) ~= nil)   -- ROUND 155: the hand-tuned spot\n', 1),
    ('a = (rec ~= nil and ox == -855 and oy == -21 and rec.dock == 8)   -- ROUND 154: the round button\n',
     'a = (rec ~= nil and ox == -923 and oy == 0 and rec.dock == 8)   -- ROUND 155: the hand-tuned spot\n', 1),
    ('raw_find(s, "FOURTH.ALL_OX, FOURTH.ALL_OY = -855, -21", 1, true) ~= nil   -- ROUND 154\n',
     'raw_find(s, "FOURTH.ALL_OX, FOURTH.ALL_OY = -923, 0", 1, true) ~= nil   -- ROUND 155\n', 1),
    ('local a = (rec ~= nil and rec.offset[1] == -855 and rec.offset[2] == -21 and rec.tooltip ~= nil   -- ROUND 154\n',
     'local a = (rec ~= nil and rec.offset[1] == -923 and rec.offset[2] == 0 and rec.tooltip ~= nil   -- ROUND 155\n', 1),
    ('raw_find(s, "FOURTH.ALL_OX, FOURTH.ALL_OY = -855, -21\\n", 1, true) ~= nil\n',
     'raw_find(s, "FOURTH.ALL_OX, FOURTH.ALL_OY = -923, 0\\n", 1, true) ~= nil   -- ROUND 155\n', 1),
    ('and rec.resize_calls == 0 and rec.offset[1] == -855 and rec.offset[2] == -21 and rec.dock == 8\n',
     'and rec.resize_calls == 0 and rec.offset[1] == -923 and rec.offset[2] == 0 and rec.dock == 8   -- ROUND 155\n', 1),
    ('local a = (okn and m1 == "ALL POS -850,-24" and rec ~= nil and rec.offset[1] == -850 and rec.offset[2] == -24)\n',
     'local a = (okn and m1 == "ALL POS -918,-3" and rec ~= nil and rec.offset[1] == -918 and rec.offset[2] == -3)   -- ROUND 155\n', 1),
]
for a, b, n in R:
    assert src.count(a) == n, (a[:70], src.count(a))
    src = src.replace(a, b)
RUNNER_ANCHOR = "\n-- THE RUNNER. The air-drop sections always run;"
assert src.count(RUNNER_ANCHOR) == 1
src = src.replace(RUNNER_ANCHOR, "\n" + SECTION + RUNNER_ANCHOR)
assert src.count("\nrun_h153()\n") == 1
src = src.replace("\nrun_h153()\n", "\nrun_h153()\nrun_h154()\n")
src = BANNER + src
assert "\u2014" not in BANNER + SECTION
os.makedirs(os.path.dirname(DST), exist_ok=True)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST, len(src), "bytes")
