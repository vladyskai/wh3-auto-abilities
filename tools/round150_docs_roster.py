#!/usr/bin/env python3
"""Round 150: the tracker rows (77 blob rows get the value / standstill wording; 21 Winds of Magic rows move to
when_ready) and section 10.28; the database family texts."""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_blob_tables as GB  # noqa: E402
import round150_value_target as R150  # noqa: E402

TRACKER = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_ability_tracker.md"
DBB = r"C:\Users\vlady\Desktop\WH3_mod\tools\build_ability_database.py"
NOTE_B = (" · **round 150 (2026-11-14):** the target is the one whose blast destroys the most enemy value; never while "
          "the caster moves; user rulings \"Most value destroyed\", \"For now, only the Blob attacks\".")
NOTE_W = " · **round 150 (2026-11-14):** user ruling for the Winds of Magic abilities: \"All when ready\"."
src = open(r"C:/Users/vlady/Desktop/WH3_mod/mod_source/script/battle/mod/zz_test_deadly_onslaught.lua", encoding="utf-8").read()
keys = GB.keys_in(src)
blast = GB.blast_table(keys)
dmg = GB.damage_table(keys)
sa = {r["key"]: r for r in GB.tsv("unit_spec_abil.tsv")}
PM2 = GB.packed_m2()
ROWS = {}
for k in keys:
    bound = int(math.floor(float(sa[k]["target_intercept_range"]) * 0.70 + 1e-9))
    need = max(1, int(math.floor(0.5 * math.pi * blast[k] ** 2 / PM2 + 0.5)))
    ap = " Armour-piercing: never at armour below 50." if dmg[k][2] else ""
    ROWS[k] = ("implemented (infantry blob, most value destroyed: enemy_blob)",
               "When armed and standing still, fires at the visible enemy infantry within %d m where its %g m blast "
               "destroys the most enemy value (armour, hit points, live value), when it hits at least %d soldiers and "
               "none of ours are within %g m.%s" % (bound, blast[k], need, blast[k] + 10, ap), NOTE_B)
for k in R150.WINDS:
    ROWS[k] = ("implemented (Winds of Magic, when ready: when_ready)", "When armed, fires as soon as it is ready.", NOTE_W)
assert len(ROWS) == 98
SECTION = """

### 10.28 Round 150 - value targets, standstill, Winds of Magic when ready (2026-11-14)

**The field battle (High Elves vs Vampire Counts, 2026-11-14, log byte 576,158,537):**
- 15 blob casts: 9 on The Tithe, 6 on Grave Guard, always the densest safe target.
- Volley of High Arrows is 100% armour-piercing, so it was wasted on the Tithe (armour 15).
- The breaths are mostly base damage: by damage alone the Tithe was a fit target, but by value it was not (about 1 per
  soldier against about 7 for Grave Guard).
- Two casts stopped a moving caster (Volley of High Arrows, Soporific Breath).

**Rulings (2026-11-14).**

- **Blob target: "Most value destroyed".** Among the safe candidates that reach the density line, the one whose blast
  destroys the most enemy value wins: soldiers covered x the share of one soldier a hit kills (blast damage after
  armour, against hit points, generated from the game's tables) x the unit's live value per soldier. AP-heavy attacks
  (38) never target armour below 50.
- **Standstill: "For now, only the Blob attacks".** The 77 blob attacks wait until the caster's is_moving() reads
  false. **Charge abilities:** "Nothing".
- **Winds of Magic: "All when ready".** The 21 Winds of Magic abilities leave "in melee" for the NEW `when_ready`. The
  user corrected Claude's claim that the pool is usually full at battle start: his screenshot showed Power 12/100,
  reserve 68, "Recharge blocked". The map probe now logs the army's winds every 2 s.
- **Generalize:** the value rule applies to the enemy-targeted damage abilities implemented from now on.

**Arithmetic.** No count change: 854 implemented / 269 not implemented (27 skipped); 799 entries / 854 keys; 75
families (melee_unwavering 309 -> 288). Harness 149: 6,374 checks / 0 failures, twice byte-identical; RED 8/8. Pack md5
`49a0903d999768b3b1123379db5a4268`.
"""
s = open(TRACKER, encoding="utf-8", newline="").read()
lines = s.split("\n")
done = set()
for i, l in enumerate(lines):
    if not l.startswith("| "):
        continue
    first = l.split("|")[1].strip()
    for k, (st, pr, note) in ROWS.items():
        if first.endswith("`%s`" % k):
            assert k not in done, k
            c = [x.strip() for x in l.strip().strip("|").split("|")]
            c[1] = "`%s`" % st
            c[3] = pr
            c[4] = c[4] + note
            lines[i] = "| " + " | ".join(c) + " |"
            done.add(k)
assert done == set(ROWS), sorted(set(ROWS) - done)
s = "\n".join(lines)
assert "### 10.28" not in s
s = s.rstrip("\n") + SECTION
assert "\u2014" not in SECTION
open(TRACKER, "w", encoding="utf-8", newline="").write(s)
print("tracker: %d rows + section 10.28" % len(done))
d = open(DBB, encoding="utf-8", newline="").read()
a = d.index('        "enemy_blob": ')
b = d.index("\n", a)
d = d[:a] + ('        "enemy_blob": "With the caster STANDING STILL: among the safe visible enemy INFANTRY units in range (an '
             'inf_* class, not in the generated large set, not flying, at least 10 men; no soldier of ours within the blast '
             'radius + 10 m; the blast covering at least half of a packed block), the one whose blast destroys the most '
             'enemy VALUE (soldiers covered x the share of a soldier killed after armour, against hit points x live value '
             'per soldier). AP-heavy attacks never target armour below 50. Casts on that enemy; re-checked before the '
             'cast.",\n'
             '        "when_ready": "No condition: the shared gates (armed, ready, charge hold, 2 s guard) decide. Casts '
             'on the unit itself.",') + d[b:]
assert d.count('"enemy_blob": ') >= 1 and '"when_ready": "No condition' in d
open(DBB, "w", encoding="utf-8", newline="").write(d)
print("database builder: 2 family texts")
