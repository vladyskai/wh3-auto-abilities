#!/usr/bin/env python3
"""Build harness153.lua from harness152.lua for round 154. Older harnesses are never edited.

Pin rebases (documented in docs/WH3_round154_all_button.md):
  * the ALL spot (-855, -28) -> (-855, -21) in section 151 (token 0zx, world AP1a) and section 152 (token 0zy, world
    AP2a): the 38 x 38 round button keeps the 36 x 24 text badge's centre, 7 lower;
  * the mock component records image paths per index (rec.images) and a state (SetState; CurrentState returns it, or
    "default" as before when none was set).
"""
import os

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261115_trash_all_harness152\harness152.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261115_all_button_harness153\harness153.lua"
SECTION = open(r"C:\Users\vlady\Desktop\WH3_mod\tools\h153_section.lua", encoding="utf-8").read()
BANNER = """-- ============================================================================
-- HARNESS 153 - ROUND 154: THE ALL CONTROL IS THE GAME'S OWN ROUND TOGGLE
--   BUTTON (ABILITIES ICON, PRESSED WHILE ALL ARE ARMED) WITH LUA CONSOLE HOOKS.
--   Edited vs harness152: this banner, the rebases in tools/make_harness153.py,
--   the mock's images / SetState, run_h153 and its call.
--   RED control: H153_LIVE / H153_ANN on docs/backups/round154/pre154_*.lua.
-- ============================================================================
"""
src = open(SRC, encoding="utf-8").read()
R = [
    ('        and raw_find(s, "FOURTH.ALL_OX, FOURTH.ALL_OY = -855, -28", 1, true) ~= nil)   -- ROUND 153: the new spot\n',
     '        and raw_find(s, "FOURTH.ALL_OX, FOURTH.ALL_OY = -855, -21", 1, true) ~= nil)   -- ROUND 154: the round button\n'),
    ('          a = (rec ~= nil and ox == -855 and oy == -28 and rec.dock == 8)   -- ROUND 153: the new spot\n',
     '          a = (rec ~= nil and ox == -855 and oy == -21 and rec.dock == 8)   -- ROUND 154: the round button\n'),
    ('        and raw_find(s, "FOURTH.ALL_OX, FOURTH.ALL_OY = -855, -28", 1, true) ~= nil\n',
     '        and raw_find(s, "FOURTH.ALL_OX, FOURTH.ALL_OY = -855, -21", 1, true) ~= nil   -- ROUND 154\n'),
    ('          local a = (rec ~= nil and rec.offset[1] == -855 and rec.offset[2] == -28 and rec.tooltip ~= nil\n',
     '          local a = (rec ~= nil and rec.offset[1] == -855 and rec.offset[2] == -21 and rec.tooltip ~= nil   -- ROUND 154\n'),
    ('                  destroy_calls = 0, destroyed = false,\n',
     '                  destroy_calls = 0, destroyed = false, images = {}, state = nil,   -- ROUND 154: images, state\n'),
    ('    function b:SetImagePath(path, i) rec.calls_total = rec.calls_total + 1; rec.image_calls = rec.image_calls + 1 end\n',
     '    function b:SetImagePath(path, i) rec.calls_total = rec.calls_total + 1; rec.image_calls = rec.image_calls + 1;'
     ' rec.images[i or 0] = path end\n'
     '    function b:SetState(s) rec.state = s end   -- ROUND 154: the round button\'s pressed look\n'),
    ('    function b:CurrentState() return "default" end\n    -- THIS ROUND: the Destroy recorder.',
     '    function b:CurrentState() return rec.state or "default" end   -- ROUND 154: the last SetState, else as before\n'
     '    -- THIS ROUND: the Destroy recorder.'),
]
for a, b in R:
    assert src.count(a) == 1, (a[:70], src.count(a))
    src = src.replace(a, b)
RUNNER_ANCHOR = "\n-- THE RUNNER. The air-drop sections always run;"
assert src.count(RUNNER_ANCHOR) == 1
src = src.replace(RUNNER_ANCHOR, "\n" + SECTION + RUNNER_ANCHOR)
assert src.count("\nrun_h152()\n") == 1
src = src.replace("\nrun_h152()\n", "\nrun_h152()\nrun_h153()\n")
src = BANNER + src
assert "\u2014" not in BANNER + SECTION
os.makedirs(os.path.dirname(DST), exist_ok=True)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST, len(src), "bytes")
