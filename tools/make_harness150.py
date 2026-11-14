#!/usr/bin/env python3
"""Build harness150.lua from harness149.lua for round 151 (large first + hold, usage rules, breaths at 90 degrees, 432
abilities armed by default, the ALL badge). Older harnesses are never edited.

Harness changes (documented in docs/WH3_round151_large_defaults.md):
  * load_world sets the TEST-ONLY global ZZ_AUTO_TEST_NO_DEFAULTS = true unless the world asks for the defaults
    (W.defaults_on): every older world arms by clicking a badge, which would DISARM a default-armed ability.
  * pin rebases listed in PIN_RULES / R below (the ALL badge adds one created component where badges are counted).
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261114_value_target_harness149\harness149.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261114_large_defaults_harness150\harness150.lua"
SECTION_FILE = r"C:\Users\vlady\Desktop\WH3_mod\tools\h150_section.lua"

BANNER = """-- ============================================================================
-- HARNESS 150 - ROUND 151: LARGE FIRST + HOLD, USAGE RULES, BREATHS AT 90
--   DEGREES, 432 ABILITIES ARMED BY DEFAULT, THE ALL BADGE.
--   Edited vs harness149: this banner, the default-arming test switch in
--   load_world, the pin rebases in tools/make_harness150.py, run_h150 and its
--   call. RED control: H150_LIVE / H150_ANN on docs/backups/round151/pre151_*.lua.
-- ============================================================================
"""

PIN_RULES = []   # (regex, replacement, guard) - filled after the first diagnostic run
src = open(SRC, encoding="utf-8").read()
R = [
    ('  local chunk = loadfile(path)\n  if chunk == nil then error("loadfile returned nil for " .. tostring(path), 0) end\n',
     '  -- ROUND 151: older worlds arm by clicking, which would DISARM a default-armed ability; they run with the\n'
     '  -- family defaults OFF. A world that tests the defaults sets W.defaults_on.\n'
     '  ZZ_AUTO_TEST_NO_DEFAULTS = (W.defaults_on ~= true)\n'
     '  local chunk = loadfile(path)\n  if chunk == nil then error("loadfile returned nil for " .. tostring(path), 0) end\n'),
    # the active-list walk count: the ALL badge's "is any ability badge shown?" walk is the sixth path
    ('    .. loops .. ", want 5 = badge build, show/hide, both letter refreshes, and all_buttons_found())", loops == 5)\n',
     '    .. loops .. ", want 6 = badge build, show/hide, both letter refreshes, all_buttons_found() and (round 151) the ALL'
     ' badge\'s shown test)", loops == 6)\n'),
    # the armed read: still nil-guarded, now with the family default after it
    ('    raw_find(s, "return per ~= nil and per[marker] == true", 1, true) ~= nil)\n',
     '    raw_find(s, "if per ~= nil and per[marker] ~= nil then return per[marker] == true end", 1, true) ~= nil)'
     '   -- ROUND 151: the default follows\n'),
]
for a, b in R:
    assert src.count(a) == 1, (a[:70], src.count(a))
    src = src.replace(a, b)
# the mock counts the ALL badge on its own (W.all_badge_created): the older per-ability component counts keep meaning
CC_OLD = "  function hud_battle:CreateComponent(name, layout)\n    W.create_calls = W.create_calls + 1\n"
CC_NEW = "  local function create_impl(self, name, layout)\n    W.create_calls = W.create_calls + 1\n"
assert src.count(CC_OLD) == 1
at = src.index(CC_OLD)
src = src.replace(CC_OLD, CC_NEW)
END = "    return b\n  end\n"
e = src.index(END, at) + len(END)
WRAP = ('  -- ROUND 151: the ALL badge is counted on its own (W.all_badge_created) and never takes a forced "returned\n'
        '  -- nothing", so every older per-ability component count keeps its meaning\n'
        '  function hud_battle:CreateComponent(name, layout)\n'
        '    if name == "zz_auto_badge_all" then\n'
        '      local c1, c2, c3, nb = W.create_calls, W.create_attempts, W.created_n, W.create_nil_budget\n'
        '      W.create_nil_budget = 0\n'
        '      local r = create_impl(self, name, layout)\n'
        '      W.create_calls, W.create_attempts, W.created_n, W.create_nil_budget = c1, c2, c3, nb\n'
        '      W.all_badge_created = (W.all_badge_created or 0) + 1\n'
        '      return r\n'
        '    end\n'
        '    return create_impl(self, name, layout)\n'
        '  end\n')
src = src[:e] + WRAP + src[e:]
lines = src.split("\n")
for i, ln in enumerate(lines):
    if ln.lstrip().startswith("--"):
        continue
    for a, b, guard in PIN_RULES:
        if guard is None or guard in ln:
            lines[i] = re.sub(a, b, lines[i])
src = "\n".join(lines)
if os.path.exists(SECTION_FILE):
    SECTION = open(SECTION_FILE, encoding="utf-8").read()
    RUNNER_ANCHOR = "\n-- THE RUNNER. The air-drop sections always run;"
    assert src.count(RUNNER_ANCHOR) == 1
    src = src.replace(RUNNER_ANCHOR, "\n" + SECTION + RUNNER_ANCHOR)
    assert src.count("\nrun_h149()\n") == 1
    src = src.replace("\nrun_h149()\n", "\nrun_h149()\nrun_h150()\n")
    assert "\u2014" not in SECTION
src = BANNER + src
os.makedirs(os.path.dirname(DST), exist_ok=True)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST, len(src), "bytes")
