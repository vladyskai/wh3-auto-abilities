#!/usr/bin/env python3
"""Build the round-126 build script from the round-125 one.

No ABILITIES change, so no count pin moves. One gate is added after the round-125
gate: the GENERATED reload table in the source must be byte-equal to what
tools/gen_reload_table.py produces from gamedata\\wh3 today (so nobody hand-edits it
and a stale table cannot ship), the round-125 measured-gap window must be gone, and
the cast-point and in-range code must be present.
"""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261103_spellbar_rule_ammo_probe_harness124\build_and_install125.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261103_firing_reload_table_harness125\build_and_install126.py"

ANCHOR = 'print("ROUND 125 GATE OK: spell-bar buttons are never claimed; the ammo probe is in")\n'
ADD = ANCHOR + '''# ROUND 126: the firing flag from the game's reload table (generated, never hand-typed).
import subprocess as _sp
_gen = _sp.run([sys.executable, r"C:/Users/vlady/Desktop/WH3_mod/tools/gen_reload_table.py", "--check",
                FILES[0][0]], capture_output=True, text=True)
assert _gen.returncode == 0, "BUILD REFUSED (round 126): " + (_gen.stdout + _gen.stderr).strip()
assert "AMMO_SAME_VOLLEY_S" not in script_txt and "st.gap_s" not in script_txt, \\
    "the deleted round-125 measured-gap window is back in the source"
assert "function FOURTH.ammo_in_range(u)" in script_txt and "FOURTH.AMMO_CAST_FRACTION = 0.5" in script_txt, \\
    "the cast point / in-range code is missing"
print("ROUND 126 GATE OK: " + _gen.stdout.strip())
'''

src = open(SRC, encoding="utf-8").read()
assert src.count(ANCHOR) == 1
src = src.replace(ANCHOR, ADD)
head = src.split("class Client")[0]
if "\nimport sys\n" not in head:
    src = src.replace("import json\n", "import json\nimport sys\n", 1)
assert "AppData/Local/Temp" not in src
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST)
