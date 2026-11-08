#!/usr/bin/env python3
"""Round 122 (harness 121): add ten self-cast melee buffs to the ABILITIES table
on the EXISTING shared melee_unwavering evaluator, in the live source AND the
annotated copy (edited identically).

User ruling 2026-10-27, verbatim: "Approved as recommended: Group A on
melee_unwavering, Group B on melee_unwavering. Implement as a tuning round."

All ten keys: IN-WHEEL in v20, not implemented, not in army_spec, self-only
(no range column, so no 70% range constant), unlimited uses, timed duration.
Table: 687 entries / 738 keys -> 697 / 748; melee_unwavering 360 -> 370.
"""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"
ARMY = r"C:\Users\vlady\AppData\Local\Temp\wh3\army_spec.tsv"

NEW = [
    # (marker, name, key)  -- GROUP A, melee damage
    ("call_for_power", "Call for Power", "wh3_main_daemon_head_abilities_call_for_power"),
    ("manus_of_ursun", "Manus of Ursun", "wh3_main_weapon_abilities_ursuns_claws"),
    ("black_hammer_of_hashut", "Black Hammer of Hashut", "wh3_dlc23_weapon_abilities_black_hammer_of_hashut"),
    ("the_graven_sceptre", "The Graven Sceptre", "wh3_dlc23_weapon_abilities_the_graven_sceptre"),
    ("tyrants_talon", "Tyrant's Talon", "wh3_cp1_weapon_abilities_tyrants_talon"),
    ("the_crimson_blade", "The Crimson Blade", "wh3_dlc29_item_abilities_crimson_blade"),
    # GROUP B, melee survival
    ("bloodstorm", "Bloodstorm", "wh2_dlc14_lord_abilities_bloodstorm"),
    ("crooked_dice", "Crooked Dice", "wh3_dlc23_hero_abilities_crooked_dice"),
    ("temptator", "Temptator", "wh3_dlc20_lord_abilities_temptator"),
    ("all_consuming_hatred", "All-Consuming Hatred", "wh3_dlc27_unit_abilities_consuming_hatred"),
]

HEADER = """
	-- ============================================================================
	-- ROUND 122 (harness 121): TEN SELF-CAST MELEE BUFFS on the EXISTING shared
	-- melee_unwavering evaluator (user ruling 2026-10-27: Group A and Group B
	-- both on melee_unwavering, tuning round). Fires when the unit is in melee
	-- and not wavering; cast on the unit itself. All ten are in the wheel, none
	-- is in the army_spec junction, all are self-only (no range column, so no
	-- 70% range constant), unlimited uses, timed duration (no toggle stances).
	--   GROUP A, melee damage: Call for Power, Manus of Ursun, Black Hammer of
	--     Hashut, The Graven Sceptre, Tyrant's Talon, The Crimson Blade.
	--   GROUP B, melee survival: Bloodstorm, Crooked Dice, Temptator,
	--     All-Consuming Hatred.
	-- Table: 687 entries / 738 keys -> 697 / 748; melee_unwavering 360 -> 370.
	-- ============================================================================
"""

ANCHOR = """	{ marker = "ultimate_verdict", name = "Ultimate Verdict", trigger = "melee_unwavering",
		badge = "zz_auto_badge_ultimate_verdict",
		keys = { "wh3_cp1_character_abilities_terrifying_presence" },
		ox = 0, oy = 0 },
"""


def block():
    out = HEADER
    for marker, name, key in NEW:
        out += ('\t{ marker = "%s", name = "%s", trigger = "melee_unwavering",\n'
                '\t\tbadge = "zz_auto_badge_%s",\n'
                '\t\tkeys = { "%s" },\n'
                '\t\tox = 0, oy = 0 },\n') % (marker, name, marker, key)
    return out


army = set()
with open(ARMY, encoding="utf-8", errors="replace") as f:
    f.readline()
    for ln in f:
        c = ln.rstrip("\n").split("\t")
        if c and c[0].strip() and not ln.startswith("#"):
            army.add(c[0].strip())
hits = [k for _, _, k in NEW if k in army]
assert not hits, ("army-bar key in the batch", hits)

for path in (SRC, ANN):
    s = open(path, encoding="utf-8", newline="").read()
    assert "\r\n" not in s, path
    assert s.count(ANCHOR) == 1, (path, s.count(ANCHOR))
    for marker, _, key in NEW:
        assert ('"%s"' % key) not in s, (path, "key already present", key)
        assert ('marker = "%s"' % marker) not in s, (path, "marker already present", marker)
    before = s.count("\t{ marker = ")
    mu = s.count('trigger = "melee_unwavering"')
    s = s.replace(ANCHOR, ANCHOR + block(), 1)
    assert s.count("\t{ marker = ") == before + 10
    assert s.count('trigger = "melee_unwavering"') == mu + 10
    open(path, "w", encoding="utf-8", newline="").write(s)
    print("%s: entries %d -> %d, melee_unwavering %d -> %d" % (
        path.split("\\")[-1], before, before + 10, mu, mu + 10))
