#!/usr/bin/env python3
"""Round 135: the tracker rows and section 10.16, and the database family text for enemy_fast_near_ally."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_ability_database as bd  # noqa: E402

TRACKER = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_ability_tracker.md"
DBB = r"C:\Users\vlady\Desktop\WH3_mod\tools\build_ability_database.py"

NOTE = " · **round 135 (2026-11-09):** audit batch 4: %s"
EM = ("implemented (enemy-targeted: in-melee only: enemy_melee)",
      "When armed, fires at the closest enemy in range that is fighting in melee (an enemy only being shot does not count).",
      "user ruling \"Enemy in melee\".")
FA = ("implemented (enemy-targeted: fast enemy near our units: enemy_fast_near_ally)",
      "When armed, fires at an enemy in range that is moving with a run speed of 5 m/s or more within 40 m of one of your units.",
      "the user's design (\"Enemy moving close to an ally that has at least cavalry speed\"), settings 5 m/s and 40 m.")
CLS_TXT = {"commander": "the target must be a Lord or Hero (the game's own target rule; filtered from round 135).",
           "large": "the target must be a large unit (the game's own target rule; filtered from round 135).",
           "large_single": "the target must be a large single-entity unit (the game's own target rule; filtered from round 135)."}
TO_MELEE = ["acquiescence", "el_syf", "frost_shard_glaive", "hidden_huntress", "hidden_huntress_upgraded",
            "hornswaggle", "marked_for_eatin", "taunt", "titan_headsman", "youre_next", "tendrils_of_the_sea"]
TO_FAST = ["mither", "rune_of_slowness", "master_rune_of_slowness", "whispering_mist"]

entries, _, _ = bd.mod_entries()
by_marker = {e["marker"]: e for e in entries}
src = open(r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua", encoding="utf-8").read()
cls_of = {}
for m, e in by_marker.items():
    tag = '\t{ marker = "%s",' % m
    a = src.index(tag)
    b = src.index("ox = 0, oy = 0 },\n", a)
    blk = src[a:b]
    if 'target_class = "' in blk:
        cls_of[m] = blk.split('target_class = "', 1)[1].split('"', 1)[0]
assert len(cls_of) == 15, len(cls_of)

ROWS = {}
for m in TO_MELEE:
    for k in by_marker[m]["keys"]:
        ROWS[k] = [EM[0], EM[1], EM[2]]
for m in TO_FAST:
    for k in by_marker[m]["keys"]:
        ROWS[k] = [FA[0], FA[1], FA[2]]
for m, c in cls_of.items():
    for k in by_marker[m]["keys"]:
        if k in ROWS:
            ROWS[k][2] = ROWS[k][2] + " " + CLS_TXT[c]
        else:
            ROWS[k] = [None, None, CLS_TXT[c]]

SECTION = """

### 10.16 Round 135 - audit batch 4: the enemy slows and the target filters (2026-11-09)

**Rulings (2026-11-09).**

- **Slow plus a melee-stat cut (11), "Enemy in melee":** Acquiescence, El Syf, Frost Shard Glaive, Hidden Huntress
  (both), Hornswaggle, Marked for Eatin', Taunt, Titan Headsman, You're Next!, Tendrils of the Sea.
- **Pure slows, the user's design:** *"Enemy moving close to an ally that has at least cavalry speed. The idea
  would be to automatically slow down any fast enemy with mass that is a threat. No need to detect if the enemy
  charges or not. But it should be useful, so the enemy cannot be far from the ally units."* Settings: 5 m/s run
  speed and 40 m. Mither, Rune of Slowness, Master Rune of Slowness, Whispering Mist.
- **Kept on enemy_engaged_or_shot:** Looming Dread, Book of Secrets, Fecund Rebirth (*"Keep as is, but make sure
  the trigger filters for the enemy unit type"*), Hunter of Champions (round-123 ruling kept).
- **Target filters, "Yes, all 15 now":** every automated enemy-targeted ability whose game row allows only a
  Lord/Hero (12), a large unit (2) or a large single entity (1).

**New family.** `enemy_fast_near_ally` (4).

**Arithmetic.**

- **Rows:** implemented 750 rows / 750 keys and 373 not implemented, unchanged.
- **The mod:** 698 entries / 750 keys; 56 -> **57** families; enemy_engaged_or_shot 85 -> 70, enemy_melee 3 -> 14.
- **Tests:** harness 134 full suite **5,852 checks / 0 failures**, run twice byte-identical. RED on the
  round-134 build: 10/10.
- **Install:** pack md5 `79c8ffb8f6b0e052cc0feb337b87dde4`.
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
            if st:
                c[1] = "`%s`" % st
                c[3] = pr
            c[4] = c[4] + NOTE % note
            lines[i] = "| " + " | ".join(c) + " |"
            done.add(k)
missing = set(ROWS) - done
assert not missing, sorted(missing)
s = "\n".join(lines)
assert "### 10.16" not in s
s = s.rstrip("\n") + SECTION
assert "\u2014" not in SECTION
open(TRACKER, "w", encoding="utf-8", newline="").write(s)
print("tracker: %d rows + section 10.16" % len(done))

d = open(DBB, encoding="utf-8", newline="").read()
OLD = '        "melee_or_under_fire": "The unit in melee (not wavering) or under missile fire; for an aura also any friendly unit within the aura bound in melee or under fire. Casts on the unit itself.",\n'
NEW = OLD + ('        "enemy_fast_near_ally": "An ENEMY unit in range that is MOVING with a run speed (`fast_speed()`) of 5 m/s or more '
             'and is within 40 m of one of our units (the user\'s settings, round 135). Casts on that enemy.",\n')
assert d.count(OLD) == 1
open(DBB, "w", encoding="utf-8", newline="").write(d.replace(OLD, NEW))
print("database builder: 1 family text")
