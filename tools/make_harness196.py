#!/usr/bin/env python3
"""Build harness196.lua from harness195.lua for round 197 (the blob family's whole-army fallback). Older harnesses are
never edited. Edits: the banner, load_world's ZZ_AUTO_TEST_NO_BLOB_FALLBACK line (older worlds list only the enemies
they show, so the fallback stays off there), run_h196 and its call. No pin rebased."""
import os

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261121_mctlabel_harness195\harness195.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261121_blobfallback_harness196\harness196.lua"
SECTION = open(r"C:\Users\vlady\Desktop\WH3_mod\tools\h196_section.lua", encoding="utf-8").read()
BANNER = """-- ============================================================================
-- HARNESS 196 - ROUND 197: THE BLOB FAMILY'S WHOLE-ARMY FALLBACK (no living enemy unit, visible or hidden, passes the
--   armour and trash rules -> the best visible target without them).
--   Edited vs harness195: this banner, load_world's ZZ_AUTO_TEST_NO_BLOB_FALLBACK line, run_h196 and its call.
--   RED control: H196_LIVE / H196_ANN on docs/backups/round197/pre197_*.lua.
-- ============================================================================
"""
LOADW = "  ZZ_AUTO_TEST_REMEMBER_FILE = W.remember_file\n"
LOADW_NEW = (LOADW +
             "  -- ROUND 197: older worlds list only the enemies they show; they run without the whole-army fallback.\n"
             "  ZZ_AUTO_TEST_NO_BLOB_FALLBACK = (W.blob_fallback_on ~= true)\n")


def main():
    src = open(SRC, encoding="utf-8").read()
    assert src.count(LOADW) == 1
    src = src.replace(LOADW, LOADW_NEW)
    anchor = "\n-- THE RUNNER. The air-drop sections always run;"
    assert src.count(anchor) == 1
    src = src.replace(anchor, "\n" + SECTION + anchor)
    assert src.count("\nrun_h195()\n") == 1
    src = src.replace("\nrun_h195()\n", "\nrun_h195()\nrun_h196()\n")
    src = BANNER + src
    assert "\u2014" not in BANNER + SECTION
    os.makedirs(os.path.dirname(DST), exist_ok=True)
    open(DST, "w", encoding="utf-8", newline="\n").write(src)
    print("wrote", DST, len(src), "bytes")


if __name__ == "__main__":
    main()
