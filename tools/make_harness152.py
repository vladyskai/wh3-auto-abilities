#!/usr/bin/env python3
"""Build harness152.lua from harness151.lua for round 153. Older harnesses are never edited.

Pin rebases (documented in docs/WH3_round153_trash_all.md):
  * active-list walks 6 -> 5: the ALL badge no longer walks the ability list (it follows the selected units' owned
    abilities instead);
  * section 151's ALL spot: (-880, 8) -> (-855, -28) (token 0zx and world AP1a);
  * the mock component gains SetTooltipText (records rec.tooltip) for the new tooltip.
"""
import os

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261115_no_hold_harness151\harness151.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261115_trash_all_harness152\harness152.lua"
SECTION = open(r"C:\Users\vlady\Desktop\WH3_mod\tools\h152_section.lua", encoding="utf-8").read()
BANNER = """-- ============================================================================
-- HARNESS 152 - ROUND 153: NO TRASH TARGETS UNLESS A BIG BLOB; THE ALL BADGE
--   FOR ANY SELECTION, IN THE MIDDLE OF THE CLOTH, WITH A TOOLTIP.
--   Edited vs harness151: this banner, the rebases in tools/make_harness152.py,
--   the mock's SetTooltipText, run_h152 and its call.
--   RED control: H152_LIVE / H152_ANN on docs/backups/round153/pre153_*.lua.
-- ============================================================================
"""
src = open(SRC, encoding="utf-8").read()
R = [
    ('    .. loops .. ", want 6 = badge build, show/hide, both letter refreshes, all_buttons_found() and (round 151) the ALL'
     ' badge\'s shown test)", loops == 6)\n',
     '    .. loops .. ", want 5 = badge build, show/hide, both letter refreshes, all_buttons_found(); round 153: the ALL'
     ' badge no longer walks the list)", loops == 5)\n'),
    ('        and raw_find(s, "FOURTH.ALL_OX, FOURTH.ALL_OY = -880, 8", 1, true) ~= nil)\n',
     '        and raw_find(s, "FOURTH.ALL_OX, FOURTH.ALL_OY = -855, -28", 1, true) ~= nil)   -- ROUND 153: the new spot\n'),
    ('          a = (rec ~= nil and ox == -880 and oy == 8 and rec.dock == 8)\n',
     '          a = (rec ~= nil and ox == -855 and oy == -28 and rec.dock == 8)   -- ROUND 153: the new spot\n'),
    ('    function b:SetText(t) rec.calls_total = rec.calls_total + 1; rec.text = t; rec.settext_calls = rec.settext_calls + 1 end\n',
     '    function b:SetText(t) rec.calls_total = rec.calls_total + 1; rec.text = t; rec.settext_calls = rec.settext_calls + 1 end\n'
     '    function b:SetTooltipText(t, all) rec.tooltip = t end   -- ROUND 153: the ALL badge tooltip\n'),
]
for a, b in R:
    assert src.count(a) == 1, (a[:70], src.count(a))
    src = src.replace(a, b)
RUNNER_ANCHOR = "\n-- THE RUNNER. The air-drop sections always run;"
assert src.count(RUNNER_ANCHOR) == 1
src = src.replace(RUNNER_ANCHOR, "\n" + SECTION + RUNNER_ANCHOR)
assert src.count("\nrun_h151()\n") == 1
src = src.replace("\nrun_h151()\n", "\nrun_h151()\nrun_h152()\n")
src = BANNER + src
assert "\u2014" not in BANNER + SECTION
os.makedirs(os.path.dirname(DST), exist_ok=True)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST, len(src), "bytes")
