#!/usr/bin/env python3
"""Round 158: the tracker rows (12 implemented) and section 10.36, and the database family texts."""
TRACKER = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_ability_tracker.md"
DBB = r"C:\Users\vlady\Desktop\WH3_mod\tools\build_ability_database.py"
NOTE = " · **round 158 (2026-11-15):** the last group B attacks, user ruling \"%s\"."
AD = ("implemented (most valuable infantry, standing still: enemy_area_drain)",
      "When armed and standing still, casts on the enemy infantry within %d m worth the most per soldier that still has "
      "at least %d soldiers (every strike lands).", "Most valuable infantry")
ROWS = {
    "wh2_main_item_abilities_blood_statuette_of_spite": (AD[0], AD[1] % (70, 25), AD[2]),
    "wh3_dlc23_item_abilities_darkened_mist": (AD[0], AD[1] % (21, 25), AD[2]),
    "wh3_dlc25_spell_bound_the_fate_of_bjuna": (AD[0], AD[1] % (70, 25), AD[2]),
    "wh3_main_spell_bound_the_fate_of_bjuna": (AD[0], AD[1] % (70, 25), AD[2]),
    "wh3_dlc24_unit_abilities_maelstrom_of_change": (AD[0], AD[1] % (140, 25), AD[2]),
    "wh3_dlc29_lord_abilities_otherworldly_pestilence": (AD[0], AD[1] % (70, 25), AD[2]),
    "wh3_dlc27_item_abilities_staff_of_the_masque": (AD[0], AD[1] % (35, 15), AD[2]),
    "wh3_dlc29_item_active_ethracs_brazier": (
        "implemented (enemy in melee or charging: enemy_melee_or_fast)",
        "When armed, casts on the closest enemy within 70 m that is fighting in melee, otherwise on a fast enemy closing "
        "on our units (it slows the target).", "Rule 10: melee or charge"),
    "wh2_dlc11_lord_abilities_storm_of_the_night": (
        "implemented (flying enemy in melee or charging: enemy_melee_or_fast, flying only)",
        "When armed, casts on a FLYING enemy within 105 m that is fighting in melee or closing fast on our units (the "
        "game allows flying targets only).", "Rule 10: melee or charge"),
    "wh3_dlc27_item_abilities_preyton_horns": (
        "implemented (enemy in melee: enemy_melee)",
        "When armed, casts on the closest enemy within 70 m that is fighting in melee (enemies near it -8 morale, ours "
        "+8).", "Horns melee, Trance waver"),
    "wh2_dlc10_item_abilities_the_amber_trance": (
        "implemented (wavering enemy: enemy_wavering)",
        "When armed, casts on the closest wavering enemy within 70 m (one use: tip it into a rout).",
        "Horns melee, Trance waver"),
    "wh3_dlc23_item_abilities_dweomer_leach_orb": (
        "implemented (most valuable Lord/Hero, the spellcaster proxy: enemy_commander_value)",
        "When armed, casts on the most valuable enemy Lord or Hero within 140 m (the game allows spellcasters only; a "
        "non-caster is refused by the engine).", "Lord/Hero proxy"),
}
SECTION = """

### 10.36 Round 158 - open batch 6: the last group B attacks (2026-11-15)

**Earlier status:** "excluded (impossible: no enemy-unit read)", written before the round-145 map; no user decision.
Group B is now closed.

**Rulings (2026-11-15).**

- **Area drains** (Blood Statuette of Spite, Darkened Mist, The Fate of Bjuna x2, Maelstrom of Change, Otherworldly
  Pestilence, Staff of Masks; up to 25 models hit per tick, 15 for the Staff): "Most valuable infantry" -> NEW
  `enemy_area_drain`, standing still, no margin.
- **The slows:** "Rule 10: melee or charge" -> `enemy_melee_or_fast` for Ethrac's Brazier, and for Storm of the Night
  with the NEW class `flying` (the game allows flying targets only).
- **Morale hexes:** "Horns melee, Trance waver" -> Preyton Horns on `enemy_melee`, The Amber Trance on
  `enemy_wavering`.
- **Dweomer Leach Orb** (spellcasters only; no read): "Lord/Hero proxy" -> NEW `enemy_commander_value`.

**Arithmetic.**

- **Rows:** implemented 877 + 12 = **889 rows / keys**; not implemented among the included 246 - 12 = **234**
  (27 skipped).
- **The mod:** 822 + 12 = **834 entries / 889 keys**; **84** families.
- **Tests:** harness 157 full suite **6,677 checks / 0 failures**, run twice byte-identical. RED 12/12.
- **Install:** pack md5 `326b37332e8f0b94bffeacea5fb6a966`.
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
assert "### 10.36" not in s
s = s.rstrip("\n") + SECTION
assert "\u2014" not in SECTION
open(TRACKER, "w", encoding="utf-8", newline="").write(s)
print("tracker: %d rows + section 10.36" % len(done))
d = open(DBB, encoding="utf-8", newline="").read()
OLD = '        "enemy_wavering": '
NEW = ('        "enemy_area_drain": "The caster STANDING STILL; the visible enemy infantry in range with at least the '
       'ability\'s own model count left (the generated max_damaged_entities) and the highest live value per soldier; no '
       'friendly-fire margin (a direct effect). Casts on that enemy; re-checked before the cast.",\n'
       '        "enemy_commander_value": "The most valuable visible enemy Lord or Hero in range (the spellcaster proxy: the '
       'game allows casters only and there is no read). Casts on that enemy; re-checked before the cast.",\n' + OLD)
assert d.count(OLD) == 1 and "enemy_area_drain" not in d
d = d.replace(OLD, NEW)
open(DBB, "w", encoding="utf-8", newline="").write(d)
print("database builder: 2 family texts")
