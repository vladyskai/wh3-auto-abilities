#!/usr/bin/env python3
"""Build harness172.lua from harness171.lua for round 173 (Null Stone and Rock Eye closed). Older harnesses are never
edited.

Rebases (the user's closures, 2026-11-18):
  * the table: 939 -> 937 entries (every occurrence of the number); 994 -> 992 keys (the key-count comparisons);
  * melee_unwavering 282 -> 280 (both rode it); h105 A4a iterations 1,878 -> 1,874 (2 x 937);
  * h103 charge-gate rows 327 -> 326 (Null Stone's hold row, 3 uses, is removed);
  * h127 H1-H4 (the round-128 hold release) used Null Stone as its 3-use, 120 s, no-wind-up subject. It now uses Doom
    Glaive (wh3_dlc29_item_abilities_doom_glaive: 3 uses, 120 s recharge, no wind-up, melee_unwavering, a hold row),
    so the worlds keep their meaning.
"""
import os
import re

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261118_ruled_rows_harness171\harness171.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261118_close_two_harness172\harness172.lua"
SECTION = open(r"C:\Users\vlady\Desktop\WH3_mod\tools\h172_section.lua", encoding="utf-8").read()
BANNER = """-- ============================================================================
-- HARNESS 172 - ROUND 173: NULL STONE AND ROCK EYE CLOSED BY THE USER.
--   Edited vs harness171: this banner, the rebases listed in tools/make_harness172.py,
--   run_h172 and its call.
--   RED control: H172_LIVE / H172_ANN on docs/backups/round173/pre173_*.lua.
-- ============================================================================
"""
R = [
    ("    a = (it == 1878)   -- HARNESS 170: 2 x 939\n", "    a = (it == 1874)   -- HARNESS 172: 2 x 937\n", 1),
    ("""cp103(blk, '"] = ') == (RED_MODE and 0 or 327))   -- HARNESS 170: Watched by the Watcher closed""",
     """cp103(blk, '"] = ') == (RED_MODE and 0 or 326))   -- HARNESS 172: Null Stone closed too""", 1),
    ("n_mk == 994", "n_mk == 992", 1),
    ("#AKEYS == 994", "#AKEYS == 992", 1),
    ("n_k == 994", "n_k == 992", 6),
    ("keys = 994,", "keys = 992,", 3),
    ("== 282", "== 280", 15),
    ("mu = 282,", "mu = 280,", 2),
    ('  local NS = "wh3_dlc27_item_abilities_null_stone"\n',
     '  local NS = "wh3_dlc29_item_abilities_doom_glaive"   -- HARNESS 172: Null Stone is closed; Doom Glaive (3 uses, 120 s)\n', 2),
    ('click(W, "zz_auto_badge_null_stone")', 'click(W, "zz_auto_badge_doom_glaive")', 2),
    ('"charge gate null_stone: unit 12', '"charge gate doom_glaive: unit 12', 2),
]
src = open(SRC, encoding="utf-8").read()
for a, b, n in R:
    assert src.count(a) == n, (a[:70], src.count(a))
    src = src.replace(a, b)
n939 = len(re.findall(r"(?<!\d)939(?!\d)", src))
src = re.sub(r"(?<!\d)939(?!\d)", "937", src)
print("939 -> 937:", n939)
RUNNER_ANCHOR = "\n-- THE RUNNER. The air-drop sections always run;"
assert src.count(RUNNER_ANCHOR) == 1
src = src.replace(RUNNER_ANCHOR, "\n" + SECTION + RUNNER_ANCHOR)
assert src.count("\nrun_h171()\n") == 1
src = src.replace("\nrun_h171()\n", "\nrun_h171()\nrun_h172()\n")
src = BANNER + src
assert "\u2014" not in BANNER + SECTION
os.makedirs(os.path.dirname(DST), exist_ok=True)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST, len(src), "bytes")
