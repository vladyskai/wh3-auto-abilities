#!/usr/bin/env python3
"""Build harness195.lua from harness194.lua for round 196 (the MCT label: the long original text again, still no
tooltip; user 2026-11-21: "Now it is not clear what the button does. I liked the previous text, just not the misaligned
'?'."). Older harnesses are never edited.

Edits: the banner, one rebase (harness 194 MC4a pinned a one-line label of at most 15 characters: it now pins the user's
text), run_h195 and its call."""
import os

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261121_mctpage_harness194\harness194.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261121_mctlabel_harness195\harness195.lua"
BANNER = """-- ============================================================================
-- HARNESS 195 - ROUND 196: THE MCT LABEL IS THE LONG ORIGINAL TEXT AGAIN ("Forget the remembered M/A choices"), STILL
--   WITHOUT A TOOLTIP (so no "?" marker). Edited vs harness194: this banner, the MC4a rebase, run_h195 and its call.
-- ============================================================================
"""
REBASE = ("local a_layout = ok4 and o ~= nil and o.kind == \"action\" and o.tip == nil and o.text ~= nil and #o.text <= 15",
          "local a_layout = ok4 and o ~= nil and o.kind == \"action\" and o.tip == nil and o.text == \"Forget the remembered M/A choices\"   -- HARNESS 195: the user's text")
SECTION = r'''-- ============================================================================
-- HARNESS 195 (round 196): MC6 the MCT page's action label is "Forget the remembered M/A choices" and the page sets no
--   tooltip anywhere (no "?" marker). RED: H195_MCT on docs/backups/round196/pre196_mct.lua (the short label).
-- ============================================================================
function run_h195()
  local MCT = os.getenv("H195_MCT") or "C:/Users/vlady/Desktop/WH3_mod/mod_source/script/mct/settings/smart_ability_autocast.lua"
  local RED195 = os.getenv("H195_MCT") ~= nil
  local s = read_file(MCT)
  local long = raw_find(s, 'add_new_action("reset_remembered", "Forget the remembered M/A choices", pressed)', 1, true) ~= nil
  local tip = raw_find(s, "set_tooltip_text(", 1, true) ~= nil
  if RED195 then
    check("MC6 (RED): the round-195 page has the short label", (not long) and (not tip))
  else
    check("MC6: the label is the user's text and the page sets no tooltip", long and (not tip))
  end
end
'''


def main():
    src = open(SRC, encoding="utf-8").read()
    assert src.count(REBASE[0]) == 1
    src = src.replace(REBASE[0], REBASE[1])
    anchor = "\n-- THE RUNNER. The air-drop sections always run;"
    assert src.count(anchor) == 1
    src = src.replace(anchor, "\n" + SECTION + anchor)
    assert src.count("\nrun_h194()\n") == 1
    src = src.replace("\nrun_h194()\n", "\nrun_h194()\nrun_h195()\n")
    src = BANNER + src
    os.makedirs(os.path.dirname(DST), exist_ok=True)
    open(DST, "w", encoding="utf-8", newline="\n").write(src)
    print("wrote", DST, len(src), "bytes")


if __name__ == "__main__":
    main()
