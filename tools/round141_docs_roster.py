#!/usr/bin/env python3
"""Round 141: the tracker rows for the nine recharge reducers and section 10.23, and the database family texts."""
TRACKER = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_ability_tracker.md"
DBB = r"C:\Users\vlady\Desktop\WH3_mod\tools\build_ability_database.py"
NOTE = " · **round 141 (2026-11-13):** the recharge reducers, one by one: user ruling \"%s\"."
R1 = ("implemented (1+ of its abilities recharging: self_recharging)",
      "When armed, fires when another ability of this unit that the mod cast is still recharging: cast on self.", "1 ability recharging")
ROWS = {
    "wh_main_item_abilities_scroll_of_power": ("implemented (2+ of its abilities recharging: self_recharging_2)",
        "When armed, fires when two other abilities of this unit that the mod cast are still recharging: cast on self.",
        "2+ abilities recharging"),
    "wh2_dlc09_item_abilities_staff_of_nagash": R1, "wh3_main_weapon_abilities_staff_of_tomorrow": R1,
    "wh_dlc04_item_abilities_the_liber_noctus": R1, "wh_main_item_abilities_channelling_staff": R1,
    "wh3_dlc29_weapon_abilities_aken_seth_the_staff_of_pain": R1,
    "wh2_dlc15_item_abilities_armour_of_caledor": ("implemented (in melee, health 75% or less: melee_health75)",
        "When armed, fires when this unit is in melee at 75% health or less: cast on self.", "In melee + health <= 75%"),
    "wh_dlc08_item_abilities_terrorgheist_skull": ("implemented (the caster or an ally in melee: melee_self_or_ally)",
        "When armed, fires when this unit is in melee (cast on self), else on the closest friendly unit within 70 m in melee.",
        "Self or ally in melee"),
    "wh3_dlc23_weapon_abilities_spell_wrought_sceptre": ("implemented (the caster or an ally recharging: recharging_in_reach)",
        "When armed, fires when this unit has an ability recharging (cast on self), else on the closest friendly unit within 70 m that has.",
        "Recharging unit in reach"),
}
SECTION = """

### 10.23 Round 141 - the nine recharge reducers, one by one (2026-11-13)

**Rulings (2026-11-13).**

- **Scroll of Power:** "2+ abilities recharging".
- **Staff of Nagash, Staff of Tomorrow, The Liber Noctus, Channelling Staff, Aken-seth:** "1 ability recharging".
- **Armour of Caledor:** "In melee + health <= 75%".
- **Terrorgheist Skull:** "Self or ally in melee".
- **Spell-Wrought Sceptre:** "Recharging unit in reach".

**How "recharging" is known.** The mod remembers each cast the game accepted and its lock: effect plus recharge, from
the GENERATED `FOURTH.RECHARGE_S` (618 keys; the game starts a recharge when the effect ENDS). It cannot see spells or
abilities the player clicks, nor campaign recharge bonuses.

**New families.** `self_recharging` (5), `self_recharging_2` (1), `recharging_in_reach` (1), `melee_self_or_ally` (1).

**Arithmetic.**

- **Rows / families:** 750 rows / keys, unchanged; 64 families.
- **Tests:** harness 140 full suite **6,088 checks / 0 failures**, run twice byte-identical. RED 6/6.
- **Install:** pack md5 `2eafed987e269c47af570cf4670865cb`.
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
assert "### 10.23" not in s
s = s.rstrip("\n") + SECTION
assert "\u2014" not in SECTION
open(TRACKER, "w", encoding="utf-8", newline="").write(s)
print("tracker: %d rows + section 10.23" % len(done))
d = open(DBB, encoding="utf-8", newline="").read()
OLD = '        "self_running": '
NEW = ('        "self_recharging": "At least one other ability of this unit, cast by the mod, still recharging (effect + recharge from the game data). Casts on the unit itself.",\n'
       '        "self_recharging_2": "At least two other abilities of this unit, cast by the mod, still recharging. Casts on the unit itself.",\n'
       '        "recharging_in_reach": "The unit itself has an ability recharging (cast on itself), else the closest ally in range that has (cast on that ally).",\n'
       '        "melee_self_or_ally": "The unit itself in melee (cast on itself), else the closest ally in range in melee (cast on that ally).",\n' + OLD)
assert d.count(OLD) == 1
open(DBB, "w", encoding="utf-8", newline="").write(d.replace(OLD, NEW))
print("database builder: 4 family texts")
