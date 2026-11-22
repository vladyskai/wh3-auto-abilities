#!/usr/bin/env python3
"""Build harness210.lua from harness209.lua for round 212 (a transformed unit is a new unit: the watch list comes from
the army's own unit list). Older harnesses are never edited. Edits: the banner, run_h210 and its call, and the rebased
pins listed in PINS (each is documented in the round document).
With DEV=<path> it writes a development copy that runs ONLY run_h210 (never used as proof)."""
import os
import re

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261122_rawprobe_harness209\harness209.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261122_transform_harness210\harness210.lua"
SECTION = open(r"C:\Users\vlady\Desktop\WH3_mod\tools\h210_section.lua", encoding="utf-8").read()
BANNER = """-- ============================================================================
-- HARNESS 210 - ROUND 212: A TRANSFORMED UNIT IS A NEW UNIT (the watch list comes from the army's own unit list).
--   Edited vs harness209: this banner, run_h210 and its call, the rebased pins (see the round document).
--   RED control: H210_LIVE / H210_ANN on docs/backups/round212/pre212_*.lua.
-- ============================================================================
"""
# the pins rebased in this round: (old text, new text, how many times it occurs)
PINS = [
    # the poll now also re-lists 2 s after a cast: one more call site of rebuild_unit_list() in each file
    ('for _, f in ipairs({ { name = "annotated", src = ann_src, relist_calls = 3 },\n'
     '                     { name = "live", src = live_src, relist_calls = 4 } }) do',
     'for _, f in ipairs({ { name = "annotated", src = ann_src, relist_calls = 4 },   -- HARNESS 210\n'
     '                     { name = "live", src = live_src, relist_calls = 5 } }) do', 1),
    # harness 66 H2: the dead unit cast at tick 1, so the re-list 2 s later (tick 9) drops it, not the one at tick 40
    ("W.routing_calls[1002] == 39 and #W.fires == 5)", "W.routing_calls[1002] == 8 and #W.fires == 1)   -- HARNESS 210", 1),
]


def main():
    src = open(SRC, encoding="utf-8").read()
    anchor = "\n-- THE RUNNER. The air-drop sections always run;"
    assert src.count(anchor) == 1
    src = src.replace(anchor, "\n" + SECTION + anchor)
    assert src.count("\nrun_h209()\n") == 1
    src = src.replace("\nrun_h209()\n", "\nrun_h209()\nrun_h210()\n")
    for old, new, n in PINS:
        assert src.count(old) == n, (old, src.count(old))
        src = src.replace(old, new)
    src = BANNER + src
    assert "\u2014" not in BANNER + SECTION
    dst = DST
    dev = os.environ.get("DEV")
    if dev:
        head, tail = src.split(anchor)
        tail = re.sub(r"\nrun_h(?!210)\d+\(\)", "", tail)
        src = head + anchor + tail
        dst = dev
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    open(dst, "w", encoding="utf-8", newline="\n").write(src)
    print("wrote", dst, len(src), "bytes")


if __name__ == "__main__":
    main()
