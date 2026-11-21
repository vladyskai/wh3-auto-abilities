#!/usr/bin/env python3
"""Build the round-198 build script from the round-197 one (the overnight review's fixes, user 2026-11-22: "fix" on
rows 1, 2, 3, 6, 7, 8, 11). ROUND 198 GATE: the entry reset is ONE function called by the poll and the fast pass, the
closed serial window is re-armed and yields, Get Tha Gitz! has its hold row, the Necromancer's land key is in the
Lord/Hero list, the two auras use the round-192 read, the three target_self = false entries carry no_self and the
game's table agrees, Bugman's keep-out distance is the game's 55 m. Rebased: the round-180 Bugman gate (38 -> 55).
NEW: the script must also compile on Lua 5.1 (the game's Lua), not only on lupa's default."""

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261121_blobfallback_harness196\build_and_install197.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261122_reviewfixes_harness197\build_and_install198.py"
ANCHOR = 'print("ROUND 197 GATE OK: the whole-army fallback (flag set by the blob evaluation, 6 wrapped rule uses, fail-closed)")\n'
ADD = ANCHOR + r'''# ROUND 198 (user 2026-11-22, the overnight review: "fix" on rows 1, 2, 3, 6, 7, 8, 11).
assert script_txt.count("\nfunction FOURTH.entry_reset(ability, unit)\n") == 1 \
    and script_txt.count("FOURTH.entry_reset(ability, unit)") == 3, \
    "BUILD REFUSED (round 198): the entry reset must be one function, called by the poll and by the fast pass"
_i198 = script_txt.index("\nfunction FOURTH.ad_fast_pass()")
_f198 = script_txt[_i198:script_txt.index("\nbm:repeat_callback(poll, POLL_MS, POLL_NAME)", _i198)]
assert "FOURTH.entry_reset(ability, unit)" in _f198 and "FOURTH.ad_enemy = nil" not in _f198, \
    "BUILD REFUSED (round 198): the fast pass must reset every slot through FOURTH.entry_reset"
assert script_txt.count("\t\t\t\t\tcast_gate.unit_marker[ui_id] = nil\n") == 1 \
    and script_txt.count("cast_gate.unit_waiting[ui_id] == true") == 1 \
    and script_txt.count("cast_gate.unit_waiting[") == 5, \
    "BUILD REFUSED (round 198): the closed serial window must be re-armed by a repeat, and yield to a waiter"
assert script_txt.count('\t\t["wh3_dlc23_hero_abilities_get_tha_gitz!"] = 120,\n') == 1, \
    "BUILD REFUSED (round 198): Get Tha Gitz! (3 uses) has no charge-hold row"
assert script_txt.count('\t\t["wh3_dlc29_vmp_cha_necromancer_undeath_nightmare"] = true,') == 1, \
    "BUILD REFUSED (round 198): the Necromancer on a Nightmare (land_units key) is not in the Lord/Hero list"
for _fn198 in ("evaluate_slow_aura", "evaluate_guard_aura"):
    _a198 = script_txt.index("\nfunction FOURTH." + _fn198 + "(")
    _b198 = script_txt[_a198:script_txt.index("\nend\n", _a198)]
    assert "FOURTH.fast_enemy_near(" in _b198 and "is_moving()" not in _b198, \
        "BUILD REFUSED (round 198): " + _fn198 + " must use the round-192 fast-enemy read (running and closing)"
# every multi-use key of the mod has a hold row, and no_self equals the game's target_self = false on the two families
import csv as _csv198
import re as _re198
import gamedata_paths as _gp198
_rows198 = list(_csv198.reader(open(_gp198.GAMEDATA + "\\unit_spec_abil.tsv", encoding="utf-8"), delimiter="\t"))
_h198 = {n: i for i, n in enumerate(_rows198[0])}
_game198 = {r[0]: r for r in _rows198[1:]}
_ab0 = script_txt.index("local ABILITIES = {")
_ab1 = script_txt.index("local charge_gate = {")
_hold198 = script_txt[_ab1:script_txt.index("\n\tuntil_tick = {}", _ab1)]
_bad198 = []
for _m in _re198.finditer(r'\n\t\{ marker = "([^"]+)", name = "[^"]*", trigger = "([^"]+)",(.*?)(?=\n\t\{ marker = |\n\t-- |\n\}\n)',
                          script_txt[_ab0:_ab1], _re198.S):
    _mk, _tr, _body = _m.group(1), _m.group(2), _m.group(3)
    _keys = _re198.findall(r'"(wh[0-9a-z_!]*[^"]*)"', _body.split("keys = {")[1].split("}")[0])
    # an entry takes the largest hold of its keys, so ONE row is enough for an entry
    _multi = [_k for _k in _keys if int(_game198[_k][_h198["num_uses"]]) > 1]
    if _multi and _tr != "air_drop_on_infantry" and not any(('["' + _k + '"] = ') in _hold198 for _k in _keys):
        _bad198.append("no hold row: " + _mk)
    if _tr in ("melee_self_or_ally", "self_or_ally_fire_melee"):
        _noself = all(_game198[_k][_h198["target_self"]] == "false" for _k in _keys)
        if _noself != ("\t\tno_self = true," in _body):
            _bad198.append("no_self differs from the game's target_self: " + _mk)
assert not _bad198, "BUILD REFUSED (round 198): " + "; ".join(_bad198)
assert script_txt.count("\t\tno_self = true,") == 3 and "FOURTH.CARD_TIP_NOSELF[ability.trigger]" in script_txt, \
    "BUILD REFUSED (round 198): the no_self entries or their card are missing"
assert "\nFOURTH.BUGMAN_CLEAR_M = 55 " in script_txt, "BUILD REFUSED (round 198): Bugman's keep-out distance is the game's 55 m"
# the game runs Lua 5.1: the shipped script must compile there too (lupa's default is a newer Lua)
from lupa import lua51 as _lua51_198
_c198 = _lua51_198.LuaRuntime().eval("function(s) local f, e = loadstring(s, '=zz_test_deadly_onslaught.lua'); return tostring(e) end")(script_txt)
assert _c198 == "nil", "BUILD REFUSED (round 198): the script does not compile on Lua 5.1: " + str(_c198)
print("ROUND 198 GATE OK: the entry reset shared with the fast pass, the re-armed serial window, every multi-use key held, "
      "no_self = the game's target_self, the two auras on the round-192 read, Bugman's 55 m, compiles on Lua 5.1")
'''

REBASE = (
    'assert "\\nFOURTH.BUGMAN_CLEAR_M = 38" in script_txt and 38 == int(55 * 0.70), "BUILD REFUSED (round 180): Bugman\'s bound"',
    'assert "\\nFOURTH.BUGMAN_CLEAR_M = 55" in script_txt, "BUILD REFUSED (round 180): Bugman\'s bound"   # ROUND 198 rebase: '
    'the whole 55 m (a keep-out distance)',
)


# ROUND 198 rebase: the round-189 gate pinned two lines of the poll's reset block with their 5 tabs; the block is now
# the body of FOURTH.entry_reset (1 tab).
REBASE189 = [
    (r'"\t\t\t\t\tFOURTH.eg_caster = unit   -- ROUND 189: the caster the line of fire is drawn from\n",',
     r'"\tFOURTH.eg_caster = unit   -- ROUND 189: the caster the line of fire is drawn from\n",'),
    (r'''"\t\t\t\t\tFOURTH.eg_los = (ability.los == true)   -- ROUND 189: the game's 'Requires line of sight'\n",''',
     r'''"\tFOURTH.eg_los = (ability.los == true)   -- ROUND 189: the game's 'Requires line of sight'\n",'''),
]


def main():
    src = open(SRC, encoding="utf-8").read()
    assert src.count(REBASE[0]) == 1, src.count(REBASE[0])
    src = src.replace(REBASE[0], REBASE[1])
    for a, b in REBASE189:
        assert src.count(a) == 1, (a, src.count(a))
        src = src.replace(a, b)
    assert src.count(ANCHOR) == 1
    src = src.replace(ANCHOR, ADD).replace("20261121_blobfallback_harness196", "20261122_reviewfixes_harness197")
    open(DST, "w", encoding="utf-8", newline="\n").write(src)
    print("wrote", DST)


if __name__ == "__main__":
    main()
