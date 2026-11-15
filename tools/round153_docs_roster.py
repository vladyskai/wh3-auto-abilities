#!/usr/bin/env python3
"""Round 153: tracker section 10.31 and the database's enemy_blob text (no row changes status or family)."""
TRACKER = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_ability_tracker.md"
DBB = r"C:\Users\vlady\Desktop\WH3_mod\tools\build_ability_database.py"
SECTION = """

### 10.31 Round 153 - no trash targets unless a big blob; the ALL badge for any selection (2026-11-15)

**Field (round 152, High Elves vs Vampire Counts, log from byte 641,639,500):**
- 7 breath casts hit The Tithe (value 0.8-1.0 per soldier, 15-19 value destroyed per cast); the Grave Guard casts
  destroyed 72-178.
- The ALL badge was visible below the portrait, but it hid when two selected units shared no ability.

**Rulings (2026-11-15).**
- "ignore trash units ... Unless there is a big blob": trash = live value below 2 per soldier ("Value below 2"; the
  bottom 4% of infantry).
- A big blob = 3 packed blocks in the blast ("3 packed blocks"; about 100 soldiers in a 5 m blast). Claude's option
  text wrongly equated this with "3 x the density line (51+)"; the line is half a packed block, so the literal 3 packed
  blocks was built and the user told.
- The ALL badge: always there for a selection that owns any ability of ours; more centred and higher (the middle of
  the cloth); a hover tooltip.

**Arithmetic.** No count change. Harness 152: 6,473 checks / 0 failures, twice byte-identical; RED 6/6. Pack md5
`04ed9fcfe08ef13b800d6810f61e4629`.
"""
s = open(TRACKER, encoding="utf-8", newline="").read()
assert "### 10.31" not in s
s = s.rstrip("\n") + SECTION
assert "\u2014" not in SECTION
open(TRACKER, "w", encoding="utf-8", newline="").write(s)
print("tracker: section 10.31")
d = open(DBB, encoding="utf-8", newline="").read()
a = d.index('        "enemy_blob": ')
b = d.index("\n", a)
d = d[:a] + ('        "enemy_blob": "With the caster STANDING STILL and the game\'s usage rules met (flying where it must not be '
             'grounded, out of melee where it must be): the 53 prefer_central_targets attacks hit a safe visible LARGE enemy '
             'in range first (the most value lost), never a FLYING one, and never hold for one out of range; otherwise the '
             'safe visible enemy INFANTRY unit whose blast destroys the most value (at least half a packed block in the '
             'blast; TRASH below 2 value per soldier only when the blast covers 3 packed blocks; AP-heavy attacks never at '
             'armour below 50; the prefer-central attacks and breaths prefer a side-on target within 20% of the best '
             'value). Casts on that enemy; re-checked before the cast.",') + d[b:]
open(DBB, "w", encoding="utf-8", newline="").write(d)
print("database builder: enemy_blob text")
