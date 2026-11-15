#!/usr/bin/env python3
"""Round 152: tracker section 10.30 and the database's enemy_blob / tired texts (no row changes status or family)."""
TRACKER = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_ability_tracker.md"
DBB = r"C:\Users\vlady\Desktop\WH3_mod\tools\build_ability_database.py"
SECTION = """

### 10.30 Round 152 - no whole-map hold, no flying large targets, 90 degrees for every central attack (2026-11-15)

**Field (round 151, High Elves vs Vampire Counts, log from byte 618,416,228):**
- "Start armed is working."
- The whole-map HOLD kept all three breaths silent the whole battle ("a large enemy (Zombie Dragon) is worth more than
  the best infantry target"); the mod never cast at the dragon.
- The ALL badge was created but off-screen, at offset (-1007, -105).
- Volley of High Arrows hit Grave Guard three times (value 152-239) through the value rule; the 90-degree rule did
  not cover it then.

**Rulings (2026-11-15).**
- "let's do not hold for a large unit in the whole map" (breaths miss flying single entities).
- "Large first, skip fliers".
- 90 degrees: "All 53 central attacks".
- Start armed: "Foe-Seeker + tired" (Foe-Seeker, Dazh's Song of Winter Sunlight).
- The ALL badge: below the portrait, right of the camera button (the user's screenshot).

**Arithmetic.** No count change; 28 families / 434 entries start armed. Harness 151: 6,446 checks / 0 failures, twice
byte-identical; RED 10/10. Pack md5 `0cc4a722865e4b5514e4716c9813b232`.
"""
s = open(TRACKER, encoding="utf-8", newline="").read()
assert "### 10.30" not in s
s = s.rstrip("\n") + SECTION
assert "\u2014" not in SECTION
open(TRACKER, "w", encoding="utf-8", newline="").write(s)
print("tracker: section 10.30")
d = open(DBB, encoding="utf-8", newline="").read()
a = d.index('        "enemy_blob": ')
b = d.index("\n", a)
d = d[:a] + ('        "enemy_blob": "With the caster STANDING STILL and the game\'s usage rules met (flying where it must not be '
             'grounded, out of melee where it must be): the 53 prefer_central_targets attacks hit a safe visible LARGE enemy '
             'in range first (the most value lost), never a FLYING one, and never hold for one out of range; otherwise the '
             'safe visible enemy INFANTRY unit whose blast destroys the most value (at least half a packed block in the '
             'blast; AP-heavy attacks never at armour below 50; the prefer-central attacks and breaths prefer a side-on '
             'target within 20% of the best value). Casts on that enemy; re-checked before the cast.",') + d[b:]
open(DBB, "w", encoding="utf-8", newline="").write(d)
print("database builder: enemy_blob text")
