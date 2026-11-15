#!/usr/bin/env python3
"""Build the round-153 build script from the round-152 one.

Gates rebased: the round-152 gate pinned the ALL spot (-880, 8); it now pins (-855, -28).
Adds one gate: the trash rule (2 per soldier, 3 packed blocks), the ALL badge shown for any owner, its tooltip."""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261115_no_hold_harness151\build_and_install152.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261115_trash_all_harness152\build_and_install153.py"
ANCHOR = 'print("ROUND 152 GATE OK: no hold, fliers skipped, 90 degrees for 53 central attacks, tired armed, ALL badge on screen")\n'
ADD = ANCHOR + r'''# ROUND 153: no trash targets unless a big blob; the ALL badge for any selection, in the middle of the cloth, a tooltip.
assert "FOURTH.TRASH_VPS = 2\n" in script_txt and "FOURTH.TRASH_BLOCKS = 3\n" in script_txt \
    and script_txt.count("FOURTH.blob_trash_ok(e, sc, r)") == 3, "the trash rule is missing (definition, pick and re-check)"
assert "local any = FOURTH.all_selection_has_ours()" in script_txt, "the ALL badge still follows the ability badges"
assert "st.badge:SetTooltipText(FOURTH.ALL_TIP, true)" in script_txt, "the ALL tooltip is missing"
print("ROUND 153 GATE OK: trash below 2 per soldier unless 3 packed blocks; ALL shown for any owner; spot; tooltip")
'''
RULES = [
    ('assert "FOURTH.ALL_OX, FOURTH.ALL_OY = -880, 8" in script_txt',
     'assert "FOURTH.ALL_OX, FOURTH.ALL_OY = -855, -28" in script_txt', 1),
]
src = open(SRC, encoding="utf-8").read()
assert src.count(ANCHOR) == 1
src = src.replace(ANCHOR, ADD)
for a, b, n in RULES:
    assert src.count(a) == n, (a[:60], src.count(a))
    src = src.replace(a, b)
src = src.replace("20261115_no_hold_harness151", "20261115_trash_all_harness152")
assert "os.remove(GAME_PACK)" not in src
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST)
