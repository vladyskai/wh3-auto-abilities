#!/usr/bin/env python3
"""Round 170 (harness 169): Potion of Foolhardiness on charge_or_wavering (user ruling 2026-11-17, after a test with two
Empire Captains: the armed potion fired only at contact, "reason: in melee, morale not wavering").

Effect (game data): the caster only, charge bonus x1.4 + Unbreakable, 31 s, ONE use. The charge bonus pays on its own
charge; Unbreakable pays when it wavers. Ruling: "Charge or wavering" (the review's row 2).

It keeps starting ARMED, as on its old family (melee_unwavering starts armed): a new entry field start_armed = true
joins the family default (charge_or_wavering itself does not start armed; Bangers & Smash is unchanged). The round-167
risky rule and the test-only ZZ_AUTO_TEST_NO_DEFAULTS still win.
"""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"
R = [
    ('\t{ marker = "potion_of_foolhardiness", name = "Potion of Foolhardiness", trigger = "melee_unwavering",\n'
     '\t\tbadge = "zz_auto_badge_potion_of_foolhardiness",\n'
     '\t\tkeys = { "wh_main_item_abilities_potion_of_foolhardiness" },\n'
     '\t\tox = 0, oy = 0 },\n',
     '\t-- ROUND 170 (user ruling 2026-11-17, "Charge or wavering"): the charge bonus on its own charge, Unbreakable when\n'
     '\t-- it wavers; it keeps starting armed (start_armed), as on its old in-melee family\n'
     '\t{ marker = "potion_of_foolhardiness", name = "Potion of Foolhardiness", trigger = "charge_or_wavering",\n'
     '\t\tbadge = "zz_auto_badge_potion_of_foolhardiness",\n'
     '\t\tkeys = { "wh_main_item_abilities_potion_of_foolhardiness" },\n'
     '\t\tstart_armed = true,\n'
     '\t\tox = 0, oy = 0 },\n'),
    ("\tability.default_on = (FOURTH.DEFAULT_ON_TRIGGERS[ability.trigger] == true)\n",
     "\tability.default_on = (FOURTH.DEFAULT_ON_TRIGGERS[ability.trigger] == true or ability.start_armed == true)   -- ROUND 170\n"),
]


def main():
    for path in (SRC, ANN):
        s = open(path, encoding="utf-8", newline="").read()
        assert "ROUND 170" not in s
        for o, n in R:
            assert s.count(o) == 1, (path[-12:], o[:70], s.count(o))
            s = s.replace(o, n)
        open(path, "w", encoding="utf-8", newline="").write(s)
        print(path, "patched")


if __name__ == "__main__":
    main()
