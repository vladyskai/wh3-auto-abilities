#!/usr/bin/env python3
"""Build the round-155 build script from the round-154 one.

Gates rebased: the round-152 gate pinned the ALL spot (-855, -21); it now pins the hand-tuned (-923, 0).
Adds one gate: the hand-tuned spot is in the shipped source."""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261115_all_button_harness153\build_and_install154.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261115_all_spot_harness154\build_and_install155.py"
ANCHOR = ('print("ROUND 154 GATE OK: the ALL control is the game\'s round toggle button (template and icon found in the game\'s"\n'
          '      " packs); pressed sync; zz_all_nudge / zz_all_set / zz_all_where")\n')
ADD = ANCHOR + r'''# ROUND 155: the ALL button at the spot the user tuned by hand in battle.
assert "FOURTH.ALL_OX, FOURTH.ALL_OY = -923, 0\n" in script_txt, "the hand-tuned ALL spot is missing"
print("ROUND 155 GATE OK: the ALL button at the hand-tuned (-923, 0)")
'''
RULES = [
    ('assert "FOURTH.ALL_OX, FOURTH.ALL_OY = -855, -21" in script_txt',
     'assert "FOURTH.ALL_OX, FOURTH.ALL_OY = -923, 0" in script_txt', 1),
]
src = open(SRC, encoding="utf-8").read()
assert src.count(ANCHOR) == 1
src = src.replace(ANCHOR, ADD)
for a, b, n in RULES:
    assert src.count(a) == n, (a[:60], src.count(a))
    src = src.replace(a, b)
assert "os.remove(GAME_PACK)" not in src
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST)
