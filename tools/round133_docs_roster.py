#!/usr/bin/env python3
"""Round 133: the tracker rows and section 10.14, and the database family texts."""
TRACKER = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_ability_tracker.md"
DBB = r"C:\Users\vlady\Desktop\WH3_mod\tools\build_ability_database.py"

NOTE = " · **round 133 (2026-11-08):** audit batch 2, user ruling: \"%s\"."
UF = ("implemented (under missile fire: under_fire)", "When armed, fires when %s is under missile fire: cast on self.",
      "When under fire")
MUF = ("implemented (melee or under missile fire: melee_or_under_fire)",
       "When armed, fires when %s is in melee (not wavering) or under missile fire: cast on self.", "In melee or under fire")
ROWS = {
    "wh2_dlc12_unit_abilities_shield_of_chaqua": (UF, "the caster or a friendly unit within 38 m (70% of the 55 m aura)"),
    "wh3_dlc24_item_abilities_the_golden_eye_of_tzeentch": (UF, "the caster"),
    "wh_dlc07_lord_abilities_lions_shield": (UF, "the caster"),
    "wh3_dlc24_item_abilities_blessed_helm_of_the_oblast": (MUF, "the caster or a friendly unit within 24 m (70% of the 35 m aura)"),
    "wh2_main_item_abilities_the_bane_shield": (MUF, "the caster or a friendly unit within 24 m (70% of the 35 m aura)"),
    "wh_main_weapon_abilities_charmed_shield": (MUF, "the caster"),
    "wh3_twa08_unit_abilities_glacial_defence": (MUF, "the caster"),
}

SECTION = """

### 10.14 Round 133 - audit batch 2: protection against shots fires when under fire (2026-11-08)

**Rulings (2026-11-08), both as recommended.**

- **Pure missile protection, "When under fire":** Shield of Chaqua, The Golden Eye of Tzeentch, The
  Lion's Shield.
- **Mixed protection, "In melee or under fire":** The Blessed Helm of the Oblast, The Bane Shield,
  Charmed Shield, Glacial Defence.

**New families.**

- `under_fire` (3)
- `melee_or_under_fire` (4)

Both read `battle_unit:is_under_missile_attack()`; only an exact true counts. The read has never been
seen on the player's own units in a real battle, so the QA battle is its first field proof.

**Arithmetic.**

- **Rows:** implemented rows and keys unchanged at **752**.
- **The mod:** **700 entries / 752 keys**; families 54 -> **56**; melee_unwavering 349 -> 342.
- **Tests:** harness 132 full suite **5,738 checks / 0 failures**, run twice byte-identical. RED on the
  round-132 build: 8/8.
- **Install:** pack md5 `7045f8da3e5b20853eda75f92e46f489`.
"""

s = open(TRACKER, encoding="utf-8", newline="").read()
lines = s.split("\n")
done = set()
for i, l in enumerate(lines):
    if not l.startswith("| "):
        continue
    first = l.split("|")[1].strip()
    for k, ((st, pr, rule), who) in ROWS.items():
        if first.endswith("`%s`" % k):
            c = [x.strip() for x in l.strip().strip("|").split("|")]
            c[1] = "`%s`" % st
            c[2] = "self"
            c[3] = pr % who
            c[4] = c[4] + NOTE % rule
            lines[i] = "| " + " | ".join(c) + " |"
            done.add(k)
assert done == set(ROWS), sorted(set(ROWS) - done)
s = "\n".join(lines)
assert "### 10.14" not in s
s = s.rstrip("\n") + SECTION
assert "\u2014" not in SECTION
open(TRACKER, "w", encoding="utf-8", newline="").write(s)
print("tracker: %d rows + section 10.14" % len(done))

d = open(DBB, encoding="utf-8", newline="").read()
OLD = '        "self_shooting": "The unit itself shooting past its cast point. Casts on the unit itself.",\n'
NEW = OLD + ('        "under_fire": "The unit itself under missile fire (`is_under_missile_attack()` exactly true); for an aura also any friendly unit within the aura bound. Casts on the unit itself.",\n'
             '        "melee_or_under_fire": "The unit in melee (not wavering) or under missile fire; for an aura also any friendly unit within the aura bound in melee or under fire. Casts on the unit itself.",\n')
assert d.count(OLD) == 1
open(DBB, "w", encoding="utf-8", newline="").write(d.replace(OLD, NEW))
print("database builder: 2 family texts")
