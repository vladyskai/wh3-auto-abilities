#!/usr/bin/env python3
"""Round 139: the tracker rows and section 10.21, and the database family text for melee_or_wavering_aura."""
TRACKER = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_ability_tracker.md"
DBB = r"C:\Users\vlady\Desktop\WH3_mod\tools\build_ability_database.py"
ST = "implemented (the General or an ally within 24 m in melee or wavering: melee_or_wavering_aura)"
PR = "When armed, fires when this unit, or a friendly unit within 24 m (70% of the 35 m aura), is in melee or wavering: cast on self (the aura)."
NOTE = (" · **round 139 (2026-11-09):** QA battle 1 showed it fired only when the General himself wavered (232 s) while "
        "the Spearmen around him had wavered from 177 s; user ruling \"The general or any friendly unit within 24m is in "
        "melee or wavering.\"")
KEYS = ["wh_main_character_abilities_stand_your_ground", "wh3_dlc24_character_abilities_tacticians_stand_your_ground"]
SECTION = """

### 10.21 Round 139 - QA battle 1 and Stand Your Ground (2026-11-09)

**QA battle 1** (Empire: General, Witch Hunter, 7 Spearmen, 7 Archers; against Beastmen).

- **Charmed Shield** fired under missile fire (2 attempts) and in melee (4). The user: *"The charmed shield worked
  really well."*
- **Slippery** fired on a charge (12.6 m, 3.7 s to contact) and in melee.
- **Accusation, Runefang, Opal Amulet and Foe-Seeker** fired on their triggers.
- **Stand Your Ground** fired once, when the General himself was in melee and wavering (232 s). The Spearmen had been
  wavering since 177 s; the second waver (254 s) fell inside the 90 s recharge.
- **Not testable in skirmish:** Potion of Speed (not offered), and the Huntsman General with the General (one Lord).

**Ruling (2026-11-09):** *"The general or any friendly unit within 24m is in melee or wavering."* This is the NEW
`melee_or_wavering_aura` (Stand Your Ground only); `melee_low_morale` keeps its evaluator with no entry.

**Arithmetic.**

- **Rows / families:** 750 rows / keys, unchanged; 59 families.
- **Tests:** harness 138 full suite **6,018 checks / 0 failures**, run twice byte-identical. RED 4/4.
- **Install:** pack md5 `55f3263e09fedd951d1bcd8ee9ce9351`.
"""
s = open(TRACKER, encoding="utf-8", newline="").read()
lines = s.split("\n")
done = set()
for i, l in enumerate(lines):
    if not l.startswith("| "):
        continue
    first = l.split("|")[1].strip()
    for k in KEYS:
        if first.endswith("`%s`" % k):
            assert k not in done, k
            c = [x.strip() for x in l.strip().strip("|").split("|")]
            c[1] = "`%s`" % ST
            c[2] = "self"
            c[3] = PR
            c[4] = c[4] + NOTE
            lines[i] = "| " + " | ".join(c) + " |"
            done.add(k)
assert done == set(KEYS), sorted(set(KEYS) - done)
s = "\n".join(lines)
assert "### 10.21" not in s
s = s.rstrip("\n") + SECTION
assert "\u2014" not in SECTION
open(TRACKER, "w", encoding="utf-8", newline="").write(s)
print("tracker: %d rows + section 10.21" % len(done))
d = open(DBB, encoding="utf-8", newline="").read()
OLD = '        "enemy_missile_shooting": '
NEW = ('        "melee_or_wavering_aura": "The unit itself in melee or WAVERING, or a friendly unit inside the aura bound '
       'in melee or wavering. Casts on the unit itself.",\n' + OLD)
assert d.count(OLD) == 1
open(DBB, "w", encoding="utf-8", newline="").write(d.replace(OLD, NEW))
print("database builder: 1 family text")
