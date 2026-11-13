#!/usr/bin/env python3
"""Round 140: the tracker row for Blooood!, section 10.22 (the QA battles of 2026-11-13), and the database family
text for self_running."""
TRACKER = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_ability_tracker.md"
DBB = r"C:\Users\vlady\Desktop\WH3_mod\tools\build_ability_database.py"
KEY = "wh_main_unit_abilities_blooood"
ST = "implemented (running: self_running)"
PR = "When armed, fires whenever this unit runs: cast on self."
NOTE = (" · **round 140 (2026-11-13):** QA battle 3: an attack order that is not a missile attack cannot be given to a "
        "Hellcannon, so the charge trigger could never fire; user ruling \"Running, any time\".")
SECTION = """

### 10.22 Round 140 - the QA battles of 2026-11-13: shooting and moving; Blooood! (2026-11-13)

**QA battles read** (the log cut from byte 446,198,331, four sessions).

- **Battle 2 (Skaven):** Rally! fired for a wavering Clanrat unit 11 m away (157 s) and when the Warlord himself
  wavered (226 s). Unholy Clamour: no DLC.
- **Battle 3, fought twice (Warriors of Chaos):** Boom! cast on its cast point both times. In the first battle it also
  cast at 159 s while the Hellcannon ran: its last shot was at 135 s and the firing flag stays on for max(2 x reload,
  20 s). Blooood! could not fire: a Hellcannon cannot receive a non-missile attack order.
- **Battle 4 (Cathay):** no DLC.
- **Battle 5 (Tomb Kings):**
  - The Necrotect's Restore heals constructs only (the game's `unit_is_not_construct` rule).
  - It cast at 208 s (Sepulchral Stalkers at 74%, 35 m). At 268 s the Stalkers were at 12% and 40.7 m away (inside the
    70 m bound), but the game refused "on cooldown": the 60 s recharge starts after the 24 s effect, so it was ready
    only at about 292 s, and the Stalkers were gone by 274 s.
  - The cooldown reducer the user saw misused is Staff of Nagash (-30 s), which fires in melee.

**Rulings (2026-11-13).**

- *"Unless the unit can fire while moving, shooting and moving are incompatible."* Every firing-flag read now
  requires the unit not to be moving, unless its type is in the GENERATED fire_move set (233 types, unit attribute
  `mounted_fire_move`).
- **Blooood!:** "Running, any time" -> NEW `self_running`.
- **The 9 recharge reducers:** *"We should go one by one, maybe the other effects of those active abilities are more
  important."* This is a review for a later round.

**Arithmetic.**

- **Rows / families:** 750 rows / keys, unchanged; 60 families; charge_only 5 -> 4.
- **Tests:** harness 139 full suite **6,049 checks / 0 failures**, run twice byte-identical. RED 8/8.
- **Install:** pack md5 `76cc9ff49ac96ac6ee89fa12372576b1`.
"""
s = open(TRACKER, encoding="utf-8", newline="").read()
lines = s.split("\n")
done = 0
for i, l in enumerate(lines):
    if l.startswith("| ") and l.split("|")[1].strip().endswith("`%s`" % KEY):
        c = [x.strip() for x in l.strip().strip("|").split("|")]
        c[1] = "`%s`" % ST
        c[2] = "self"
        c[3] = PR
        c[4] = c[4] + NOTE
        lines[i] = "| " + " | ".join(c) + " |"
        done += 1
assert done == 1, done
s = "\n".join(lines)
assert "### 10.22" not in s
s = s.rstrip("\n") + SECTION
assert "\u2014" not in SECTION
open(TRACKER, "w", encoding="utf-8", newline="").write(s)
print("tracker: 1 row + section 10.22")
d = open(DBB, encoding="utf-8", newline="").read()
OLD = '        "melee_or_wavering_aura": '
NEW = '        "self_running": "The unit itself RUNNING (`is_moving_fast()`). Casts on the unit itself.",\n' + OLD
assert d.count(OLD) == 1
open(DBB, "w", encoding="utf-8", newline="").write(d.replace(OLD, NEW))
print("database builder: 1 family text")
