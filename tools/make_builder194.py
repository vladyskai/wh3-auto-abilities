#!/usr/bin/env python3
"""Build the round-194 build script from the round-193 one.

The pack gains a FIFTH file, the optional MCT page script/mct/settings/smart_ability_autocast.lua (user 2026-11-21:
"Do it the MCT route. MCT should not be a requirement for the mod to work, only needed for this button").
ROUND 194 GATE: the remembered-state block (file name, the one write, the two reads), the in-battle reset hook; the MCT
page compiles, starts with the no-MCT guard, issues no order and never names the battle script's internals except the
hook and the file."""

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261121_preshot_harness192\build_and_install193.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261121_remember_harness193\build_and_install194.py"
FILES_OLD = ('    (SRC_ROOT + "/ui/zz_auto/auto_badge.png",\n'
             '     "ui/zz_auto/auto_badge.png"),\n]\n')
FILES_NEW = ('    (SRC_ROOT + "/ui/zz_auto/auto_badge.png",\n'
             '     "ui/zz_auto/auto_badge.png"),\n'
             '    # ROUND 194: the optional MCT page (MCT alone loads script/mct/settings/; without MCT it never runs)\n'
             '    (SRC_ROOT + "/script/mct/settings/smart_ability_autocast.lua",\n'
             '     "script/mct/settings/smart_ability_autocast.lua"),\n]\n')
ANCHOR = 'print("ROUND 193 GATE OK: Scry-Orb on when_ready (hold %d s, %d uses); the pre-shot probe is read-only" % (_rec193, _use193))\n'
ADD = ANCHOR + r'''# ROUND 194 (user 2026-11-21): remembered M/A states per unit type and ability; the reset on an optional MCT page.
assert script_txt.count('\nFOURTH.REMEMBER_FILE = "smart_ability_autocast_settings.txt"\n') == 1, \
    "BUILD REFUSED (round 194): the remembered-state file name moved"
assert script_txt.count("FOURTH.remember(ui_id, marker, value)   -- ROUND 194: remembered for the unit's type") == 1 \
    and script_txt.count("local rv = FOURTH.remembered_value(slot, marker)   -- ROUND 194") == 1 \
    and script_txt.count("if a ~= nil and a.remembered ~= nil then   -- ROUND 194: the type's remembered switch comes first") == 1, \
    "BUILD REFUSED (round 194): the switch must write once and both readers must read the remembered state"
assert script_txt.count("\nfunction smart_ability_autocast_reset_remembered()\n") == 1, \
    "BUILD REFUSED (round 194): the in-battle reset hook is missing"
_mct194 = open(SRC_ROOT + "/script/mct/settings/smart_ability_autocast.lua", encoding="utf-8").read()
_code194 = [l for l in _mct194.split("\n") if l.strip() and not l.lstrip().startswith("--")]
assert _code194[0] == 'if type(get_mct) ~= "function" then return end', \
    "BUILD REFUSED (round 194): the MCT page must start with the no-MCT guard"
assert "perform_special_ability" not in _mct194 and "FOURTH" not in _mct194, \
    "BUILD REFUSED (round 194): the MCT page must not act on units or reach into the battle script"
assert '"smart_ability_autocast_settings.txt"' in _mct194 and "smart_ability_autocast_reset_remembered" in _mct194, \
    "BUILD REFUSED (round 194): the MCT page must empty the same file and call the battle hook"
_e194 = _lupa174.LuaRuntime().eval("function(s) local f, e = load(s, '=smart_ability_autocast.lua'); return tostring(e) end")(_mct194)
assert _e194 == "nil", "BUILD REFUSED (round 194): the MCT page does not compile: " + _e194
print("ROUND 194 GATE OK: remembered states (one write, two reads, the hook); the MCT page compiles and is optional")
'''


def main():
    src = open(SRC, encoding="utf-8").read()
    assert src.count(FILES_OLD) == 1
    src = src.replace(FILES_OLD, FILES_NEW)
    assert src.count(ANCHOR) == 1
    src = src.replace(ANCHOR, ADD)
    src = src.replace("20261121_preshot_harness192", "20261121_remember_harness193")
    open(DST, "w", encoding="utf-8", newline="\n").write(src)
    print("wrote", DST)


if __name__ == "__main__":
    main()
