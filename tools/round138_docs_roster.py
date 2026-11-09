#!/usr/bin/env python3
"""Round 138: the tracker rows and section 10.20, and the database family text for enemy_missile_shooting."""
TRACKER = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_ability_tracker.md"
DBB = r"C:\Users\vlady\Desktop\WH3_mod\tools\build_ability_database.py"
NOTE = " · **round 138 (2026-11-09):** %s"
ROWS = {
    "wh3_dlc29_lord_abilities_gaze_of_usirian": (None, None, "the target must not be undead (the game's own target rule; a generated undead list)."),
    "wh2_dlc10_character_abilities_entangle": (None, None, "the target must not be flying (the game's own target rule; live read)."),
    "wh3_main_item_abilities_void_pendulum": (None, None, "the target must be a Lord or Hero (the closest approximation of the game's spellcaster rule; user ruling)."),
    "wh3_main_daemon_head_abilities_word_of_change": (None, None, "the target must be a Lord or Hero (the closest approximation of the game's spellcaster rule; user ruling)."),
    "wh3_dlc24_unit_bound_missile_mirror": ("implemented (enemy-targeted: enemy missile unit shooting: enemy_missile_shooting)",
        "When armed, fires at the closest enemy missile unit in range that is shooting (its ammunition dropping) and not in melee.",
        "user ruling \"Missile enemy shooting\"; missile units only (the game's own target rule). The enemy ammunition read is unproven until a battle: an unreadable read never fires."),
}
SECTION = """

### 10.20 Round 138 - the rarer target filters and Missile Mirror (2026-11-09)

**Rulings (2026-11-09).**

- **Void Pendulum and Word of Change, "Lords/Heroes only":** no read or data list can tell a spellcaster.
- **Missile Mirror, "Missile enemy shooting":** NEW `enemy_missile_shooting`. An enemy missile unit inside the 70%
  bound, not in melee, whose `ammo_left()` dropped between two polls within the firing-flag window.
- **The game's own target rules:**
  - Eternal Gaze: not undead (a GENERATED undead list, 355 unit types);
  - Entangle: not flying (live read);
  - Missile Mirror: missile units only.

**Arithmetic.**

- **The mod:** 698 entries / 750 keys; 58 -> **59** families; enemy_engaged_or_shot 47 -> 46; target classes
  16 -> 21.
- **Tests:** harness 137 full suite **5,995 checks / 0 failures**, run twice byte-identical. RED 8/8.
- **Install:** pack md5 `4d69206141c5d9eb89506fd0ed1064bd`.
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
assert done == set(ROWS), sorted(set(ROWS) - done)
s = "\n".join(lines)
assert "### 10.20" not in s
s = s.rstrip("\n") + SECTION
assert "\u2014" not in SECTION
open(TRACKER, "w", encoding="utf-8", newline="").write(s)
print("tracker: %d rows + section 10.20" % len(done))
d = open(DBB, encoding="utf-8", newline="").read()
OLD = '        "wavering_aura": '
NEW = ('        "enemy_missile_shooting": "An ENEMY missile unit in range that is SHOOTING (its `ammo_left()` dropped between '
       'two polls within the firing-flag window) and not in melee. Casts on that enemy.",\n' + OLD)
assert d.count(OLD) == 1
open(DBB, "w", encoding="utf-8", newline="").write(d.replace(OLD, NEW))
print("database builder: 1 family text")
