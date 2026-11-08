#!/usr/bin/env python3
"""Build the round-125 build script from the round-124 one.

No ABILITIES change, so no count pin moves. The round-124 gate (the spell-bar
badge TEST must be in the source) is REPLACED: round 125 removes that test, so
the gate now requires the spell-bar RULE (never claim a 'button_spell...'
button), requires the read-only ammo probe, and refuses the old test code.
army_spec is read from gamedata\\wh3 (since round 124).
"""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261101_spellbar_test_harness123\build_and_install124.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261103_spellbar_rule_ammo_probe_harness124\build_and_install125.py"

OLD_GATE = ('# ROUND 124: the spell-bar badge test (switch + claim branch + offset branch).\n'
            'assert "FOURTH.SPELLBAR_BADGES = true" in script_txt, "the spell-bar test switch is missing"\n'
            'assert \'string.sub(id, 1, 12) == "button_spell"\' in script_txt, "the spell-bar claim branch is missing"\n'
            'assert \'return BADGE_X + (px - WHEEL_TOP_X), BADGE_Y + (py - WHEEL_TOP_Y), "spell", px, py\' in script_txt, \\\n'
            '    "the spell-bar offset branch is missing"\n'
            'print("ROUND 124 GATE OK: the spell-bar badge test is in the source")\n')
NEW_GATE = ('# ROUND 125: the spell-bar RULE replaces the round-124 placement test, and the\n'
            '# read-only ammo probe is in (user rulings 2026-11-03).\n'
            'assert "SPELLBAR_BADGES" not in script_txt and "spellbar_id" not in script_txt, \\\n'
            '    "the removed round-124 spell-bar placement test is back in the source"\n'
            'assert "if state.button == nil and not on_spell_bar and key_is_ours(ability, key) then" in script_txt, \\\n'
            '    "the spell-bar rule (never claim a button_spell button) is missing"\n'
            'assert "function FOURTH.ammo_probe(units)" in script_txt and \\\n'
            '    script_txt.count("pcall(FOURTH.ammo_probe, tracked_units)") == 1, "the ammo probe is missing or called twice"\n'
            'print("ROUND 125 GATE OK: spell-bar buttons are never claimed; the ammo probe is in")\n')

src = open(SRC, encoding="utf-8").read()
for a, b in [(OLD_GATE, NEW_GATE),
             ("ROUND 124: the spell-bar badge test (no roster change; army_spec read from gamedata\\\\wh3).\n",
              "ROUND 125: the spell-bar rule and the read-only ammo probe (no roster change).\n"
              "ROUND 124: the spell-bar badge test (no roster change; army_spec read from gamedata\\\\wh3).\n")]:
    assert src.count(a) == 1, (a[:70], src.count(a))
    src = src.replace(a, b)
assert "AppData/Local/Temp" not in src
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST)
