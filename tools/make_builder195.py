#!/usr/bin/env python3
"""Build the round-195 build script from the round-194 one (the MCT page fix, user 2026-11-21 screenshot).
ROUND 195 GATE: the MCT page sets no tooltip (MCT's "?" marker), names its section, and gives the Done / Forgotten
feedback after Reset."""

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261121_remember_harness193\build_and_install194.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261121_mctpage_harness194\build_and_install195.py"
ANCHOR = 'print("ROUND 194 GATE OK: remembered states (one write, two reads, the hook); the MCT page compiles and is optional")\n'
ADD = ANCHOR + r'''# ROUND 195 (user 2026-11-21, screenshot: "the '?' is in the middle. Also, there is no feedback to the player").
assert "set_tooltip_text(" not in _mct194, "BUILD REFUSED (round 195): the MCT page sets a tooltip (MCT's '?' marker)"
assert 'mod:add_new_section("remembered", "Remembered M/A choices")' in _mct194, \
    "BUILD REFUSED (round 195): the MCT page must name its section"
assert 'txt:SetStateText("Done")' in _mct194 and 'label:SetStateText("Forgotten")' in _mct194 \
    and 'btn:SetState("inactive")' in _mct194, "BUILD REFUSED (round 195): the Reset button gives no feedback"
print("ROUND 195 GATE OK: the MCT page has no tooltip marker, a named section and the Done / Forgotten feedback")
'''


def main():
    src = open(SRC, encoding="utf-8").read()
    assert src.count(ANCHOR) == 1
    src = src.replace(ANCHOR, ADD)
    src = src.replace("20261121_remember_harness193", "20261121_mctpage_harness194")
    open(DST, "w", encoding="utf-8", newline="\n").write(src)
    print("wrote", DST)


if __name__ == "__main__":
    main()
