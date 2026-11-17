#!/usr/bin/env python3
"""Round 169 (harness 168): every enemy read skips hidden enemies (user, 2026-11-17: "Yes, those too; I don't see the
reason you kept them different").

Round 168 put FOURTH.enemy_not_hidden into the target pickers. Three enemy reads that pick no target still saw hidden
enemies; they now use the same test (only an exact false from is_visible_to_alliance hides an enemy):
  * FOURTH.ad_nearest        the air drop's nearest enemy underfoot;
  * FOURTH.nearest_enemy_gap the Potion of Farsight / Mist 'no enemy in range, one just beyond' read;
  * FOURTH.engagement_set    the enemies in contact (the 'unless fighting only Lords or Heroes' rule).
The map probe (read-only log rows) keeps reading every unit: it reports, it decides nothing.
"""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"
R = [
    ("\t\t\t\tif ok_alive and type(alive) == \"number\" and alive > FOURTH.AIR_DROP_MIN_MEN then\n",
     "\t\t\t\tif ok_alive and type(alive) == \"number\" and alive > FOURTH.AIR_DROP_MIN_MEN\n"
     "\t\t\t\t\tand FOURTH.enemy_not_hidden(enemy) then   -- ROUND 169: never a hidden enemy\n"),
    ("\t\t\tif ok_a and type(alive) == \"number\" and alive > 0 and ok_g and type(gap) == \"number\" and gap >= 0 then\n",
     "\t\t\tif ok_a and type(alive) == \"number\" and alive > 0 and ok_g and type(gap) == \"number\" and gap >= 0\n"
     "\t\t\t\tand FOURTH.enemy_not_hidden(enemy) then   -- ROUND 169: never a hidden enemy\n"),
    ("\t\t\t\tif ok_alive and type(alive) == \"number\" and alive > 0\n\t\t\t\t\tand ok_melee and melee == true\n",
     "\t\t\t\tif ok_alive and type(alive) == \"number\" and alive > 0\n\t\t\t\t\tand ok_melee and melee == true\n"
     "\t\t\t\t\tand FOURTH.enemy_not_hidden(enemy)   -- ROUND 169: never a hidden enemy\n"),
]


def main():
    for path in (SRC, ANN):
        s = open(path, encoding="utf-8", newline="").read()
        assert "ROUND 169" not in s
        for o, n in R:
            assert s.count(o) == 1, (path[-12:], o[:70], s.count(o))
            s = s.replace(o, n)
        open(path, "w", encoding="utf-8", newline="").write(s)
        print(path, "patched")


if __name__ == "__main__":
    main()
