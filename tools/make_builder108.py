# -*- coding: utf-8 -*-
"""Build build_and_install108.py from the harness-107 builder.

Only the CONTENT GATES move (the pack/install machinery is untouched):
  * the table pins: 688 -> 689 entries
  * the melee_skip_commanders pin: 3 -> 4 entries (Warp Lightning Rod joins it)
  * the air-drop bound pin: 7 -> 1 m, plus the bypass wiring
  * Warp Lightning Rod is now IN the table (the old "must not be implemented"
    assert is replaced by its implementation gates)
  * a new ROUND 108 assertion block
"""
import os

ROOT = r"C:\Users\vlady\Desktop\WH3_mod"
REL107 = os.path.join(ROOT, "mod_source", "releases", "20261019_bombardment_harness107")
REL108 = os.path.join(ROOT, "mod_source", "releases", "20261020_airdrops_wlr_harness108")
SRC = os.path.join(REL107, "build_and_install107.py")
DST = os.path.join(REL108, "build_and_install108.py")


def read(p):
    with open(p, "rb") as f:
        return f.read().decode("utf-8")


def write(p, s):
    data = s.encode("utf-8")
    assert b"\r" not in data
    with open(p, "wb") as f:
        f.write(data)


def rep(s, old, new, n):
    c = s.count(old)
    assert c == n, "count %d (want %d): %r" % (c, n, old[:120])
    return s.replace(old, new)


s = read(SRC)

# ---------------------------------------------------------------- table pins
s = rep(s, 'assert script_txt.count("\\t{ marker = ") == 688, "the abilities table is not 688 entries"',
        'assert script_txt.count("\\t{ marker = ") == 689, "the abilities table is not 689 entries"',
        s.count('assert script_txt.count("\\t{ marker = ") == 688, "the abilities table is not 688 entries"'))
s = rep(s, """assert script_txt.count('trigger = "melee_skip_commanders"') == 3, \\
    "Soulfire + Arachneruption + Call of Tor are not the three melee_skip_commanders entries\"""",
        """assert script_txt.count('trigger = "melee_skip_commanders"') == 4, \\
    "Soulfire + Arachneruption + Call of Tor + Warp Lightning Rod are not the four melee_skip_commanders entries\"""",
        s.count("""assert script_txt.count('trigger = "melee_skip_commanders"') == 3, \\
    "Soulfire + Arachneruption + Call of Tor are not the three melee_skip_commanders entries\""""))

# ---------------------------------------------------------------- item 1 pins
s = rep(s, 'assert "FOURTH.AIR_DROP_BOUND_M = 7" in script_txt, "the air-drop bound constant is missing"',
        'assert "FOURTH.AIR_DROP_BOUND_M = 1" in script_txt, "the air-drop bound constant is not the 1 m user value"\n'
        'assert "FOURTH.AIR_DROP_BOUND_M = 7" not in script_txt, "the old 7 m air-drop bound is still in the file"\n'
        'assert "if ability.evaluate == FOURTH.evaluate_air_drop_on_infantry then" in script_txt, \\\n'
        '    "the air-drop family does not bypass the 70% map"', 1)

# ---------------------------------------------------------------- item 2 pins
s = rep(s, """assert '"wh2_dlc16_unit_abilities_warp_lightning_rod"' not in script_txt, \\
    "Warp Lightning Rod has no enemy target and must not be implemented\"""",
        """assert '"wh2_dlc16_unit_abilities_warp_lightning_rod"' in script_txt, \\
    "Warp Lightning Rod is missing from the table"
assert 'marker = "warp_lightning_rod", name = "Warp Lightning Rod", trigger = "melee_skip_commanders"' in script_txt, \\
    "Warp Lightning Rod is not on Soulfire's trigger"
assert '["wh2_dlc16_unit_abilities_warp_lightning_rod"] = 60,' in script_txt, \\
    "Warp Lightning Rod's 60 s charge-gate row is missing"
assert '["wh2_dlc16_unit_abilities_warp_lightning_rod"] = 1,' in script_txt, \\
    "Warp Lightning Rod's 1 s wind-up row is missing"
assert "Clan Moulder" in script_txt and "LOBOTOMY" in script_txt, \\
    "the Clan Moulder Lobotomy mutation note is missing\"""",
        1)

# ------------------------------------------------- the ROUND 108 gate block
BLOCK = (
    "\n\n# ============================================================================\n"
    "# ROUND 108 (2026-10-18): THE 1 m AIR-DROP TEST BOUND + WARP LIGHTNING ROD.\n"
    "#\n"
    "#   (1) the air-drop overlap bound is 1 m - the user's own test value, NOT\n"
    "#       floor(10 x 0.70) = 7 m - carried by ONE constant and wired by an\n"
    "#       evaluator-identity bypass of the 70% map.\n"
    "#   (2) Warp Lightning Rod (wh2_dlc16_unit_abilities_warp_lightning_rod) on\n"
    "#       melee_skip_commanders, exactly like Soulfire / Call of Tor, with its\n"
    "#       Clan Moulder Lobotomy mutation note (the missing carrier junction).\n"
    "# ============================================================================\n"
    "assert script_txt.count('trigger = \"air_drop_on_infantry\"') == 12, \\\n"
    "    \"the air-drop family is not 12 entries\"\n"
    "assert script_txt.count(\"\\nFOURTH.AIR_DROP_BOUND_M = 1\\n\") == 1, \\\n"
    "    \"the 1 m air-drop bound constant is not defined exactly once\"\n"
    "assert script_txt.count(\"if ability.evaluate == FOURTH.evaluate_air_drop_on_infantry then\") == 1, \\\n"
    "    \"the air-drop bound bypass is not wired exactly once\"\n"
    "assert script_txt.count(\"ability.range_m = FOURTH.AIR_DROP_BOUND_M\") == 1, \\\n"
    "    \"the air-drop entries do not take the one constant\"\n"
    "assert \"MUCH TIGHTER\" in script_txt and \"USER-CHOSEN TEST\" in script_txt, \\\n"
    "    \"the source does not state that 1 m is a user-chosen test value\"\n"
    "assert \"EDGE-TO-EDGE\" in script_txt and \"0-5 m\" in script_txt, \\\n"
    "    \"the source does not state the edge-to-edge read (a unit on top reads 0-5 m)\"\n"
    "assert \"never fires in the field\" in script_txt and \"ONE constant\" in script_txt, \\\n"
    "    \"the source does not say the 1 m value is one constant to bump\"\n"
    "assert \"wh2_main_unit_abilities_drop_rocks\" in script_txt, \\\n"
    "    \"the field-tested row (Drop Rocks) is missing from the air-drop family\"\n"
    "\n"
    "assert script_txt.count('trigger = \"melee_skip_commanders\"') == 4, \\\n"
    "    \"melee_skip_commanders is not four entries\"\n"
    "assert 'marker = \"warp_lightning_rod\", name = \"Warp Lightning Rod\", trigger = \"melee_skip_commanders\"' in script_txt, \\\n"
    "    \"Warp Lightning Rod is not on Soulfire's trigger\"\n"
    "assert 'keys = { \"wh2_dlc16_unit_abilities_warp_lightning_rod\" },' in script_txt, \\\n"
    "    \"Warp Lightning Rod's single key is missing\"\n"
    "assert '[\"wh2_dlc16_unit_abilities_warp_lightning_rod\"] = 60,' in script_txt, \\\n"
    "    \"Warp Lightning Rod's 60 s charge gate is missing\"\n"
    "assert '[\"wh2_dlc16_unit_abilities_warp_lightning_rod\"] = 1,' in script_txt, \\\n"
    "    \"Warp Lightning Rod's 1 s wind-up is missing\"\n"
    "assert \"NO carrier\" in script_txt and \"NOT a default\" in script_txt, \\\n"
    "    \"the missing-carrier explanation is missing\"\n"
    "# WLR is SELF-CENTRED: it must never be in the ground-key set nor carry the\n"
    "# air-drop usage flags\n"
    "_g0 = script_txt.find(\"enemy_ground_keys = {\")\n"
    "_g1 = script_txt.find(\"\\t},\\n\", _g0)\n"
    "assert _g0 > 0 and _g1 > _g0\n"
    "assert '[\"wh2_dlc16_unit_abilities_warp_lightning_rod\"] = true,' not in script_txt[_g0:_g1], \\\n"
    "    \"Warp Lightning Rod was put in the ground-key set\"\n"
    "assert script_txt.count('(\"warp_lightning_rod\", \"Warp Lightning Rod\"') == 0, \\\n"
    "    \"Warp Lightning Rod must not ride the air-drop helper table\"\n"
    "\n"
)

anchor = "# the main mod must be byte-identical (untouched by this work)"
assert s.count(anchor) == 1
s = s.replace(anchor, BLOCK + anchor)

write(DST, s)
print("wrote", DST, os.path.getsize(DST), "bytes")
