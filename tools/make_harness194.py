#!/usr/bin/env python3
"""Build harness194.lua from harness193.lua for round 195 (the MCT page: a named section, a one-line label, no tooltip,
feedback after Reset). Older harnesses are never edited. Edits: the banner, run_h194 and its call. No pin rebased."""
import os

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261121_remember_harness193\harness193.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261121_mctpage_harness194\harness194.lua"
SECTION = open(r"C:\Users\vlady\Desktop\WH3_mod\tools\h194_section.lua", encoding="utf-8").read()
BANNER = """-- ============================================================================
-- HARNESS 194 - ROUND 195: THE MCT PAGE (a named section, a one-line label, no tooltip "?" marker, feedback after
--   Reset: the button reads Done and greys out, the label reads Forgotten).
--   Edited vs harness193: this banner, run_h194 and its call.
--   RED control: H194_MCT on docs/backups/round195/pre195_mct.lua.
-- ============================================================================
"""


def main():
    src = open(SRC, encoding="utf-8").read()
    anchor = "\n-- THE RUNNER. The air-drop sections always run;"
    assert src.count(anchor) == 1
    src = src.replace(anchor, "\n" + SECTION + anchor)
    assert src.count("\nrun_h193()\n") == 1
    src = src.replace("\nrun_h193()\n", "\nrun_h193()\nrun_h194()\n")
    src = BANNER + src
    assert "\u2014" not in BANNER + SECTION
    os.makedirs(os.path.dirname(DST), exist_ok=True)
    open(DST, "w", encoding="utf-8", newline="\n").write(src)
    print("wrote", DST, len(src), "bytes")


if __name__ == "__main__":
    main()
