#!/usr/bin/env python3
"""Build harness193.lua from harness192.lua for round 194 (remembered M/A states, the optional MCT reset). Older
harnesses are never edited.

Edits: the banner, load_world's two TEST-ONLY remember lines (older worlds remember nothing, so no world leaks a
switch into the next one), run_h193 and its call. No pin rebased (no roster change)."""
import os

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261121_preshot_harness192\harness192.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261121_remember_harness193\harness193.lua"
SECTION = open(r"C:\Users\vlady\Desktop\WH3_mod\tools\h193_section.lua", encoding="utf-8").read()
BANNER = """-- ============================================================================
-- HARNESS 193 - ROUND 194: REMEMBERED M/A STATES PER UNIT TYPE AND ABILITY (a small text file next to the game), the
--   reset through an optional MCT settings script.
--   Edited vs harness192: this banner, load_world's ZZ_AUTO_TEST_NO_REMEMBER / ZZ_AUTO_TEST_REMEMBER_FILE lines,
--   run_h193 and its call.
--   RED control: H193_LIVE / H193_ANN on docs/backups/round194/pre194_*.lua.
-- ============================================================================
"""
LOADW = "  ZZ_AUTO_TEST_NO_CLOSING = (W.closing_on ~= true)\n"
LOADW_NEW = (LOADW +
             "  -- ROUND 194: older worlds remember nothing (a remembered switch would leak into the next world). A world\n"
             "  -- that tests it sets W.remember_on and its own W.remember_file.\n"
             "  ZZ_AUTO_TEST_NO_REMEMBER = (W.remember_on ~= true)\n"
             "  ZZ_AUTO_TEST_REMEMBER_FILE = W.remember_file\n")


def main():
    src = open(SRC, encoding="utf-8").read()
    assert src.count(LOADW) == 1
    src = src.replace(LOADW, LOADW_NEW)
    anchor = "\n-- THE RUNNER. The air-drop sections always run;"
    assert src.count(anchor) == 1
    src = src.replace(anchor, "\n" + SECTION + anchor)
    assert src.count("\nrun_h192()\n") == 1
    src = src.replace("\nrun_h192()\n", "\nrun_h192()\nrun_h193()\n")
    src = BANNER + src
    assert "\u2014" not in BANNER + SECTION
    os.makedirs(os.path.dirname(DST), exist_ok=True)
    open(DST, "w", encoding="utf-8", newline="\n").write(src)
    print("wrote", DST, len(src), "bytes")


if __name__ == "__main__":
    main()
