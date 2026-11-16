#!/usr/bin/env python3
"""Build the round-160 build script from the round-159 one. No roster change, so no count gate moves.
Adds one gate: when_ready skips a routing unit; an instant entry holds its unit for one poll (the 2.5 s minimum stays
for the entries with a wind-up); the wind-up table still equals the game data (every mod key with wind_up_time > 0 is
listed with its own value, and no other key)."""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261115_group_e_harness158\build_and_install159.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261116_beastmen_fixes_harness159\build_and_install160.py"
ANCHOR = ('print("ROUND 159 GATE OK: group E on its families (5 melee_clear, 2 fly_dive, 1 last_stand_clear, 1 enemy_blob_vortex), "\n'
          '      "the Sigil\'s commander_ground class; the VORTEX table matches the game (10 keys)")\n')
ADD = ANCHOR + r'''# ROUND 160: the Beastmen-battle fixes (user ruling 2026-11-16).
assert 'function FOURTH.evaluate_when_ready(unit, routing)\n\t-- ROUND 160' in script_txt \
    and "\tif routing then return nil end\n\treturn \"when ready (Winds of Magic), cast on self\"" in script_txt, \
    "when_ready does not skip a routing unit"
assert "FOURTH.SERIAL_MIN_HOLD_SECONDS = 2.5\n" in script_txt and "FOURTH.SERIAL_INSTANT_HOLD_SECONDS = POLL_MS / 1000\n" in script_txt, \
    "the per-unit hold constants are missing"
assert "if ability.wind_up_s == nil then\n\t\t\t\t\t\tunit_hold_s = FOURTH.SERIAL_INSTANT_HOLD_SECONDS\n" in script_txt, \
    "the instant one-poll hold is missing"
import re as _re160
import os as _os160
_blk160 = script_txt.split("\twind_up_s = {", 1)[1].split("\n\t}", 1)[0]
_tab160 = dict((k, float(v)) for k, v in _re160.findall(r'\["([^"]+)"\] = ([\d.]+)', _blk160))
_keys160 = set()
for _m160 in _re160.finditer(r"\t\tkeys = \{(.*?)\}", script_txt, _re160.S):
    _keys160.update(_re160.findall(r'"([^"]+)"', _m160.group(1)))
import gamedata_paths as _gp160
_f160 = open(_os160.path.join(_gp160.GAMEDATA, "unit_spec_abil.tsv"), encoding="utf-8-sig")
_h160 = _f160.readline().rstrip("\n").split("\t"); _f160.readline()
_wu160 = {}
for _l160 in _f160:
    _d160 = dict(zip(_h160, _l160.rstrip("\n").split("\t")))
    if _d160["key"] in _keys160 and float(_d160["wind_up_time"] or 0) > 0:
        _wu160[_d160["key"]] = float(_d160["wind_up_time"])
assert len(_keys160) == 917 and _wu160 == _tab160, \
    "BUILD REFUSED (round 160): the wind-up table differs from the game data (an instant ability would be mis-held)"
print("ROUND 160 GATE OK: when_ready skips a routing unit; instant abilities hold their unit one poll; the wind-up "
      "table matches the game (%d of 917 keys have a wind-up)" % len(_wu160))
'''
src = open(SRC, encoding="utf-8").read()
assert src.count(ANCHOR) == 1, src.count(ANCHOR)
src = src.replace(ANCHOR, ADD)
assert "os.remove(GAME_PACK)" not in src
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST)
