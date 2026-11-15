#!/usr/bin/env python3
"""Build the round-154 build script from the round-153 one.

Gates rebased: the round-152 gate pinned the ALL spot (-855, -28); it now pins (-855, -21).
Adds one gate: the ALL control is the game's round toggle button with the abilities icon, the pressed sync and the
Lua Console hooks are present, and the template and the icon the mod names EXIST in the installed game's own UI packs
(read-only: the packs are memory-mapped and searched, never opened for writing)."""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261115_trash_all_harness152\build_and_install153.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261115_all_button_harness153\build_and_install154.py"
ANCHOR = 'print("ROUND 153 GATE OK: trash below 2 per soldier unless 3 packed blocks; ALL shown for any owner; spot; tooltip")\n'
ADD = ANCHOR + r'''# ROUND 154: the ALL control is the game's own round toggle button with the abilities icon; console hooks.
assert 'FOURTH.ALL_TEMPLATE = "ui/templates/round_small_button_toggle"' in script_txt \
    and 'FOURTH.ALL_ICON = "ui/skins/default/icon_abilities.png"' in script_txt \
    and "badge_parent:CreateComponent(FOURTH.ALL_BADGE_ID, FOURTH.ALL_TEMPLATE)" in script_txt \
    and "st.badge:SetImagePath(FOURTH.ALL_ICON, 0)" in script_txt, "the ALL control is not the round button"
assert 'write_badge_letter(st, "ALL")' not in script_txt, "the ALL control still writes letters"
assert "if any then FOURTH.all_sync_pressed(st) end" in script_txt, "the pressed sync is missing"
assert "function zz_all_nudge(dx, dy)" in script_txt and "function zz_all_set(x, y)" in script_txt \
    and "function zz_all_where()" in script_txt, "the Lua Console hooks are missing"
import mmap as _mmap
def _in_pack(pack, needle):
    with open(r"C:/Program Files (x86)/Steam/steamapps/common/Total War WARHAMMER III/data/" + pack, "rb") as fh:
        mm = _mmap.mmap(fh.fileno(), 0, access=_mmap.ACCESS_READ)
        try:
            return mm.find(needle) >= 0
        finally:
            mm.close()
assert _in_pack("ui3.pack", b"templates\\round_small_button_toggle.twui.xml") \
    or _in_pack("ui3.pack", b"templates/round_small_button_toggle.twui.xml"), "the game has no round_small_button_toggle"
assert _in_pack("ui2.pack", b"default\\icon_abilities.png") \
    or _in_pack("ui2.pack", b"default/icon_abilities.png"), "the game has no icon_abilities.png"
print("ROUND 154 GATE OK: the ALL control is the game's round toggle button (template and icon found in the game's"
      " packs); pressed sync; zz_all_nudge / zz_all_set / zz_all_where")
'''
RULES = [
    ('assert "FOURTH.ALL_OX, FOURTH.ALL_OY = -855, -28" in script_txt',
     'assert "FOURTH.ALL_OX, FOURTH.ALL_OY = -855, -21" in script_txt', 1),
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
