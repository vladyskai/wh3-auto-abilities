#!/usr/bin/env python3
"""Round 137: the tracker rows and section 10.18, the database family text for wavering_aura, and the audit's
R6 rulings plus the new R8 (vigour) list for the user's one-by-one review."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_ability_database as bd  # noqa: E402

TRACKER = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_ability_tracker.md"
DBB = r"C:\Users\vlady\Desktop\WH3_mod\tools\build_ability_database.py"
AUD = r"C:\Users\vlady\Desktop\WH3_mod\tools\audit_triggers.py"

NOTE = " · **round 137 (2026-11-09):** audit batch 6: %s"
WA = ("implemented (morale: self or ally wavering: wavering_aura)",
      "When armed, fires when this unit, or a friendly unit inside the aura, is wavering: cast on self (the aura).",
      "user ruling \"Self or ally wavering\".")
WR = ("implemented (morale: cast on the wavering ally: wavering_ally_range)",
      "When armed, fires on the closest wavering friendly unit in range: cast on that ally.",
      "user ruling \"On the wavering ally\".")
TO_AURA = ["call_of_violence", "get_back_ere", "magical_animus", "rally", "tomb_king_rally", "tomb_king_rally_upgraded",
           "pearl_of_infinite_bleakness", "unholy_clamour", "mimic_cold_blooded"]
TO_ALLY = ["crown_of_command", "doom_lord", "cold_blooded", "pilgrimage_of_skulls", "tacticians_rally"]
EXTRA = {"unholy_clamour": " The aura covers the whole army.",
         "mimic_cold_blooded": " Self only (the effect reaches no ally).",
         "cold_blooded": " The rampage arm was dropped: no battle read exists for a rampaging unit.",
         "doom_lord": " The rampage arm was dropped: no battle read exists for a rampaging unit.",
         "pilgrimage_of_skulls": " The game forbids targeting the caster, so it is cast on the wavering ally.",
         "tacticians_rally": " The game forbids targeting the caster, so it is cast on the wavering ally."}

entries, _, _ = bd.mod_entries()
by_marker = {e["marker"]: e for e in entries}
ROWS = {}
for m in TO_AURA:
    for k in by_marker[m]["keys"]:
        ROWS[k] = (WA, EXTRA.get(m, ""))
for m in TO_ALLY:
    for k in by_marker[m]["keys"]:
        ROWS[k] = (WR, EXTRA.get(m, ""))

SECTION = """

### 10.18 Round 137 - audit batch 6: morale (2026-11-09)

**Rulings (2026-11-09).**

- **Morale-only auras, "Self or ally wavering":** Call of Violence, Get Back 'Ere!, Magical Animus, Rally!,
  Reanimate (both), Pearl of Infinite Bleakness, Unholy Clamour (whole army), Mirror (Cold-Blooded) (self only).
- **"On the wavering ally":** Crown of Command, Doom Lord, Cold-Blooded; and Tacticians, Rally! and Pilgrimage of
  Skulls (the game forbids targeting the caster).
- **Rampage:** the user asked that an ability which removes Rampage also fire on a rampaging ally. No battle read for
  rampage exists, so the user chose to drop that arm.
- **Kept:**
  - morale plus a combat stat (Change or Die!, Rot or Die!, Scrying Stone, Shield of the Old Ones, The Liber Mortis,
    Axe of Men), "Keep in melee";
  - the five on dedicated triggers (Ghoul King of Ushoran, Gulyas, Purge the Weak!, Daemonic Whispers, Verminous
    Fury).
- **Vigour:** *"the vigor buff is many times secondary to the other buffs. We should go one by one and decide what is
  more important."* "Tired or worse" is the line. The 27 vigour restorers are listed in the trigger audit as R8.

**New family.** `wavering_aura` (9).

**Arithmetic.**

- **Rows:** implemented 750 / 373 not implemented, unchanged.
- **The mod:** 698 entries / 750 keys / 58 families; melee_unwavering 328 -> 314, wavering_ally_range 1 -> 6.
- **Tests:** harness 136 full suite **5,948 checks / 0 failures**, run twice byte-identical. RED 6/6.
- **Install:** pack md5 `c719e140ddff4f0525889c1388bb3fd8`.
"""

s = open(TRACKER, encoding="utf-8", newline="").read()
lines = s.split("\n")
done = set()
for i, l in enumerate(lines):
    if not l.startswith("| "):
        continue
    first = l.split("|")[1].strip()
    for k, ((st, pr, note), extra) in ROWS.items():
        if first.endswith("`%s`" % k):
            assert k not in done, k
            c = [x.strip() for x in l.strip().strip("|").split("|")]
            c[1] = "`%s`" % st
            c[2] = "self" if st == WA[0] else "ally_unit"
            c[3] = pr
            c[4] = c[4] + NOTE % (note + extra)
            lines[i] = "| " + " | ".join(c) + " |"
            done.add(k)
assert done == set(ROWS), sorted(set(ROWS) - done)
s = "\n".join(lines)
assert "### 10.18" not in s
s = s.rstrip("\n") + SECTION
assert "\u2014" not in SECTION
open(TRACKER, "w", encoding="utf-8", newline="").write(s)
print("tracker: %d rows + section 10.18" % len(done))

d = open(DBB, encoding="utf-8", newline="").read()
OLD = '        "enemy_fast_near_ally": '
NEW = ('        "wavering_aura": "The unit itself WAVERING, or a friendly unit inside the aura bound wavering (the whole '
       'army for an army-wide aura; nobody else for a self-only effect). Casts on the unit itself.",\n' + OLD)
assert d.count(OLD) == 1
open(DBB, "w", encoding="utf-8", newline="").write(d.replace(OLD, NEW))
print("database builder: 1 family text")

a = open(AUD, encoding="utf-8").read()
R6_RULED = ('RULED["R6"] = {m: "round 137: kept (%s)" % why for m, why in (\n'
            '    ("change_or_die", "morale plus a combat stat, \'Keep in melee\'"),\n'
            '    ("rot_or_die", "morale plus a combat stat, \'Keep in melee\'"),\n'
            '    ("scrying_stone", "morale plus a combat stat, \'Keep in melee\'"),\n'
            '    ("shield_of_the_old_ones", "morale plus a combat stat, \'Keep in melee\'"),\n'
            '    ("the_liber_mortis", "morale plus a combat stat, \'Keep in melee\'"),\n'
            '    ("axe_of_men", "morale plus a combat stat, \'Keep in melee\'"),\n'
            '    ("ghoul_king_of_ushoran", "dedicated trigger, \'Keep all 5 for now\'"),\n'
            '    ("gulyas", "dedicated trigger, \'Keep all 5 for now\'"),\n'
            '    ("purge_the_weak", "dedicated trigger, \'Keep all 5 for now\'"),\n'
            '    ("slezuzus_voice", "dedicated trigger, \'Keep all 5 for now\'"),\n'
            '    ("verminous_fury", "dedicated trigger, \'Keep all 5 for now\'"))}\n')
A_OLD = "}}\n"
assert a.count(A_OLD) == 1
a = a.replace(A_OLD, A_OLD + R6_RULED)
for old, new in [
    ('"charge_or_wavering", "ally_broken", "verminking_wavering"}',
     '"charge_or_wavering", "ally_broken", "verminking_wavering", "wavering_aura"}'),
    ('            flags["R6"].append(row)\n',
     '            flags["R6" + ("_ruled" if e["marker"] in RULED["R6"] else "")].append(row)\n'
     '        # R8 (round 137): a vigour restorer (Fatigue minus, to self or allies) not on a fatigue trigger -\n'
     '        # the user\'s one-by-one review ("the vigor buff is many times secondary to the other buffs")\n'
     '        if re.search(r"Fatigue:\\s*-", eff or "") and not to_enemy and trig != "tired":\n'
     '            flags["R8"].append(row)\n'),
    ('        "R7": "R7. Speed buffs on the unit itself on a melee-only trigger",\n',
     '        "R7": "R7. Speed buffs on the unit itself on a melee-only trigger",\n'
     '        "R8": "R8. Vigour restorers not on a fatigue trigger (the user\'s one-by-one review)",\n'),
]:
    assert a.count(old) == 1, old[:60]
    a = a.replace(old, new)
open(AUD, "w", encoding="utf-8", newline="\n").write(a)
print("audit: R6 rulings + R8")
