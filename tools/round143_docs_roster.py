#!/usr/bin/env python3
"""Round 143: the tracker rows (11 new keys) and section 10.25, and the database family text."""
TRACKER = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_ability_tracker.md"
DBB = r"C:\Users\vlady\Desktop\WH3_mod\tools\build_ability_database.py"
NOTE = " · **round 143 (2026-11-13):** open batch 2, user ruling \"%s\"."


def egm(bound, real, extra=""):
    return ("implemented (fighting enemy, on its ground: enemy_ground_melee)",
            "When armed, placed on the ground under the closest enemy within %d m (70%% of %d m) that is fighting in "
            "melee%s." % (bound, real, extra))


F4 = "Fighting enemy, all four"
F3 = "Fighting enemy, all three"
NF = ", never a flying one"
ROWS = {
    "wh2_dlc16_spell_bound_the_curse_of_anraheir": egm(140, 200) + (F4,),
    "wh3_main_spell_bound_the_curse_of_anraheir": egm(140, 200) + (F4,),
    "wh_dlc05_spell_bound_the_curse_of_anraheir": egm(140, 200) + (F4,),
    "wh3_main_spell_bound_transmutation_of_lead": egm(140, 200) + (F4,),
    "wh2_dlc10_spell_bound_soulblight": egm(140, 200) + (F4,),
    "wh3_dlc29_spell_bound_undeath_khizaar_the_soulstealer": egm(70, 100) + (F4,),
    "wh2_dlc09_character_abilities_curse_of_djaf": (
        "implemented (shooting enemy, on its ground: enemy_ground_shooting)",
        "When armed, placed on the ground under the closest enemy missile unit within 70 m that is shooting and not in melee.",
        "Shooting enemy"),
    "wh3_dlc29_spell_bound_soulblight": ("implemented (in melee: melee_unwavering)",
                                         "When armed, fires when the unit is in melee and not wavering: cast on self.",
                                         "In melee"),
    "wh3_dlc26_character_abilities_squig_thinkin": egm(52, 75) + (F3,),
    "wh_main_unit_abilities_spinning_loons": egm(17, 25, NF) + (F3,),
    "wh_dlc06_unit_abilities_the_loons_of_eight_peaks": egm(17, 25, NF) + (F3,),
}
SECTION = """

### 10.25 Round 143 - open batch 2: ground curses, Curse of Djaf, Soulblight, the fanatic releases (2026-11-13)

**Earlier status:** out-of-date auto-exclusions (from before the ground form and the enemy ammunition read existed),
not user decisions. The 2026-10 questionnaire had only proposed "when in melee: on the ground under its target" for the
curses.

**Rulings (2026-11-13).**

- **The Curse of Anraheir (3 keys), Transmutation of Lead, Soulblight (Doomfire Warlocks), The Soulstealer:**
  "Fighting enemy, all four" -> `enemy_ground_melee` (bounds 140 m, 140 m, 140 m, 70 m).
- **Curse of Djaf:** "Shooting enemy" -> NEW `enemy_ground_shooting`: the Missile Mirror pick (an enemy missile unit
  shooting, not in melee, within 70 m), placed on the ground under it.
- **Soulblight (Lahmian Handmaidens of Death):** "In melee" -> `melee_unwavering` (a self contact buff).
- **Squig Thinkin', Spinning Loons, The Loons of Eight Peaks:** "Fighting enemy, all three" -> `enemy_ground_melee`.
  The loons' 25 m reach gives the new `FOURTH.ENEMY_CAST_R25 = 17`, and the game's target rule (not flying) gives
  them `target_class = "not_flying"`.

**Arithmetic.**

- **Rows:** implemented 756 + 11 = **767 rows / keys**; not implemented among the included 367 - 11 = **356**.
- **The mod:** 703 + 9 = **712 entries / 767 keys**; **68** families.
- **Tests:** harness 142 full suite **6,194 checks / 0 failures**, run twice byte-identical. RED 8/8.
- **Install:** pack md5 `c2168f7908cb3e2403d7dbfbd94c017e`.
"""
s = open(TRACKER, encoding="utf-8", newline="").read()
lines = s.split("\n")
done = set()
for i, l in enumerate(lines):
    if not l.startswith("| "):
        continue
    first = l.split("|")[1].strip()
    for k, (st, pr, rule) in ROWS.items():
        if first.endswith("`%s`" % k):
            assert k not in done, k
            c = [x.strip() for x in l.strip().strip("|").split("|")]
            c[1] = "`%s`" % st
            c[3] = pr
            c[4] = c[4] + NOTE % rule
            lines[i] = "| " + " | ".join(c) + " |"
            done.add(k)
assert done == set(ROWS), sorted(set(ROWS) - done)
s = "\n".join(lines)
assert "### 10.25" not in s
s = s.rstrip("\n") + SECTION
assert "\u2014" not in SECTION
open(TRACKER, "w", encoding="utf-8", newline="").write(s)
print("tracker: %d rows + section 10.25" % len(done))
d = open(DBB, encoding="utf-8", newline="").read()
OLD = '        "self_recharging": '
NEW = ('        "enemy_ground_shooting": "The closest enemy MISSILE unit in range that is shooting (its ammunition '
       'dropping) and not in melee. Placed on the ground under that enemy.",\n' + OLD)
assert d.count(OLD) == 1 and "enemy_ground_shooting" not in d
open(DBB, "w", encoding="utf-8", newline="").write(d.replace(OLD, NEW))
print("database builder: 1 family text")
