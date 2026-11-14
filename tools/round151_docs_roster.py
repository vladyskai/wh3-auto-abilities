#!/usr/bin/env python3
"""Round 151: tracker section 10.29 and the database's enemy_blob family text (no row changes status or family)."""
TRACKER = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_ability_tracker.md"
DBB = r"C:\Users\vlady\Desktop\WH3_mod\tools\build_ability_database.py"
SECTION = """

### 10.29 Round 151 - large first, usage rules, breaths at 90 degrees, default armed, the ALL badge (2026-11-14)

**Field (High Elves vs Vampire Counts, log from byte 604,674,328):** round 150 worked. 19 of 25 blob casts went at
Grave Guard (estimated value destroyed 72-160), the Tithe only when no Grave Guard was a safe option. The winds reads
work (current 12, reserve 68, recharge 0.752/s at the start). A Zombie Dragon was on the field and no blob attack could
target it.

**Rulings (2026-11-14).**

- **Soporific Breath and every prefer_central_targets attack (53):** "Large first, but also include a hold when there
  is a valuable large unit in the battlefield (not only in range)"; valuable = "Worth more than infantry".
- **Breaths (20):** "Prefer 90 now, no need to log. I know this is better from experience." Among infantry targets
  within 20% of the best value, the one whose side faces the breath.
- **Default armed:** "The 21 when ready, but also ... all of the ones that trigger in melee or in charge", plus
  protection & last stand, morale saves, heals and ammo refills: 27 trigger families, 432 entries.
- **"ALL badge per unit".**
- Also built (the game's own rule, like the target flags): 12 blob attacks need a flying caster (grounded) and 26 an
  out-of-melee caster.

**Arithmetic.** No count change: 854 implemented / 269 not implemented (27 skipped); 799 entries / 854 keys; 75
families. Harness 150: 6,423 checks / 0 failures, twice byte-identical; RED 14/14. Pack md5
`929621699dcf172b415c2e27d20c4a78`.
"""
s = open(TRACKER, encoding="utf-8", newline="").read()
assert "### 10.29" not in s
s = s.rstrip("\n") + SECTION
assert "\u2014" not in SECTION
open(TRACKER, "w", encoding="utf-8", newline="").write(s)
print("tracker: section 10.29")
d = open(DBB, encoding="utf-8", newline="").read()
a = d.index('        "enemy_blob": ')
b = d.index("\n", a)
d = d[:a] + ('        "enemy_blob": "With the caster STANDING STILL and the game\'s usage rules met (flying where it must not be '
             'grounded, out of melee where it must be): the 53 prefer_central_targets attacks hit a safe visible LARGE enemy '
             'in range first (the most value lost) and HOLD while a large enemy anywhere is worth more than the best '
             'infantry target; otherwise the safe visible enemy INFANTRY unit whose blast destroys the most value (at least '
             'half a packed block in the blast; AP-heavy attacks never at armour below 50; breaths prefer a side-on target '
             'within 20% of the best value). Casts on that enemy; re-checked before the cast.",') + d[b:]
open(DBB, "w", encoding="utf-8", newline="").write(d)
print("database builder: enemy_blob text")
