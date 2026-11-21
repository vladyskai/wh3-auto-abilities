#!/usr/bin/env python3
"""Round 192, part 2 (user 2026-11-21 on the Moulder unit set: "do it"), both copies: Shock Collar and Remouldered only
take a Clan Moulder monster as their target (the game's rule unit_is_moulder_monster, code M).

1. The generated rule-set block gains FOURTH.MOULDER_TEXT (tools/gen_rule_sets.py derive_moulder: 28 units).
2. FOURTH.ab_atarget_ok honours code M; the M/A card names the rule.
3. The ATARGET table is regenerated afterwards (tools/round171_regen_tables.py; gen_usage_keys.TARGET has M)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_rule_sets as GR  # noqa: E402

LIVE = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"

EDITS = [
    ('\tif a.T and not FOURTH.class_member(unit, "tiger") then return false end    -- ROUND 180: the Mantras\n',
     '\tif a.T and not FOURTH.class_member(unit, "tiger") then return false end    -- ROUND 180: the Mantras\n'
     '\tif a.M and not FOURTH.class_member(unit, "moulder") then return false end  -- ROUND 192: Shock Collar, Remouldered\n'),
    ('P = "missile allies only", Z = "Lizardmen allies only", T = "Tiger Warrior allies only" }   -- ROUND 180\n',
     'P = "missile allies only", Z = "Lizardmen allies only", T = "Tiger Warrior allies only",   -- ROUND 180\n'
     '\tM = "Clan Moulder monster allies only" }   -- ROUND 192\n'),
    ('FOURTH.CARD_ATARGET_ORDER = { "C", "c", "L", "l", "F", "U", "u", "S", "P", "Z", "T" }\n',
     'FOURTH.CARD_ATARGET_ORDER = { "C", "c", "L", "l", "F", "U", "u", "S", "P", "Z", "T", "M" }\n'),
]


def patch(path):
    s = open(path, encoding="utf-8", newline="").read()
    assert "FOURTH.MOULDER_TEXT" not in s, "already patched: " + path
    old = GR.lua_block_180()
    assert s.count(old) == 1, path
    s = s.replace(old, GR.lua_block())
    for a, b in EDITS:
        assert s.count(a) == 1, (path, a[:60])
        s = s.replace(a, b)
    open(path, "w", encoding="utf-8", newline="").write(s)
    print("patched", path, "moulder", len(GR.derive_moulder()))


if __name__ == "__main__":
    patch(LIVE)
    patch(ANN)
