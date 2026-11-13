#!/usr/bin/env python3
"""Round 142: the tracker rows (6 new keys + Blooood!) and section 10.24, and the database family texts."""
TRACKER = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_ability_tracker.md"
DBB = r"C:\Users\vlady\Desktop\WH3_mod\tools\build_ability_database.py"
NOTE = " · **round 142 (2026-11-13):** open batch 1, user ruling \"%s\"."
AM = ("implemented (ammo refill: ally_ammo_low)",
      "When armed, refills the friendly unit within 70 m that is shooting with 70% or less ammunition left (the least first).",
      "Same as Restock!")
MI = ("implemented (ground under a unit just out of range: ground_ally_before_range)",
      "When armed, placed on the ground under the closest friendly missile unit within 175 m that has no enemy in its range but one within range x 1.35.",
      "Before range (Farsight-like)")
ROWS = {
    "wh2_dlc11_hero_abilities_more_powder": AM,
    "wh3_dlc25_abilities_restock_gunnery_school": AM,
    "wh3_dlc27_character_abilities_master_of_mists": MI,
    "wh3_dlc27_character_abilities_master_of_mists_custom": MI,
    "wh3_dlc29_unit_abilities_of_warp_and_ruin": ("implemented (shooting, target not in melee: self_shooting_clear)",
        "When armed, fires when the unit is shooting at a target that is not in melee (its shots can hurt friendly units): cast on self.",
        "Shooting, not into melee"),
    "wh3_dlc25_item_abilities_ominous_powder": ("implemented (shooting above half health: self_shooting_healthy)",
        "When armed, fires when the unit is shooting and above 50% health (it damages its carrier): cast on self.",
        "Shooting, health above 50%"),
    "wh_main_unit_abilities_blooood": ("implemented (moving: self_moving)",
        "When armed, fires whenever the unit moves: cast on self.",
        "When moving (a Hellcannon never runs)"),
}
SECTION = """

### 10.24 Round 142 - open batch 1 (shooting buffs and ammo refills) and Blooood! (2026-11-13)

**Earlier status:** auto-exclusions ("no ammo-low read", "ground-target-only", "no effect text"), not user decisions.
CLAUDE.md noted that More Powder! and the gunnery-school Restock! have Restock!'s effect but were not in the round-130
ruling.

**Rulings (2026-11-13).**

- **More Powder!, Restock! (gunnery school):** "Same as Restock!" -> `ally_ammo_low`.
- **Master of Mists (2 keys):** "Before range (Farsight-like)" -> NEW `ground_ally_before_range`. It is placed on the
  ground under the closest friendly missile unit within 175 m (70% of 250 m) that has no enemy in range but one within
  range x 1.35.
- **Of Warp and Ruin:** "Shooting, not into melee" -> NEW `self_shooting_clear`.
- **Ominous Powder:** "Shooting, health above 50%" -> NEW `self_shooting_healthy`.
- **Blooood!:** the QA battles showed a Hellcannon never runs (`is_moving_fast()` always false). "When moving" -> NEW
  `self_moving`.

**Arithmetic.**

- **Rows:** implemented 750 + 6 = **756 rows / keys**; not implemented among the included 373 - 6 = **367**.
- **The mod:** 698 + 5 = **703 entries / 756 keys**; **67** families.
- **Tests:** harness 141 full suite **6,135 checks / 0 failures**, run twice byte-identical. RED 10/10.
- **Install:** pack md5 `d4b0ebaef4476414ecea798c9b599a32`.
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
assert "### 10.24" not in s
s = s.rstrip("\n") + SECTION
assert "\u2014" not in SECTION
open(TRACKER, "w", encoding="utf-8", newline="").write(s)
print("tracker: %d rows + section 10.24" % len(done))
d = open(DBB, encoding="utf-8", newline="").read()
OLD = '        "self_recharging": '
NEW = ('        "ground_ally_before_range": "The closest friendly missile unit in range with NO enemy inside its own missile range but one inside range x 1.35. Placed on the ground under that unit.",\n'
       '        "self_shooting_clear": "The unit itself shooting past its cast point at a target that is not in melee. Casts on the unit itself.",\n'
       '        "self_shooting_healthy": "The unit itself shooting past its cast point and above 50% health. Casts on the unit itself.",\n'
       '        "self_moving": "The unit itself MOVING (`is_moving()`). Casts on the unit itself.",\n' + OLD)
assert d.count(OLD) == 1
open(DBB, "w", encoding="utf-8", newline="").write(d.replace(OLD, NEW))
print("database builder: 4 family texts")
