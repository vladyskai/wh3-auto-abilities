#!/usr/bin/env python3
"""Round 180: the tracker's status cells (moved, re-ruled, closed, the 80% WW keys), section 10.58; the marks on rows
87-114 and 128 of the score-3 review."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_xlsx_v63 as A  # noqa: E402

P = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_ability_tracker.md"
REV = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_score3_review_2026-11-18.md"
STATUS = {k: "`implemented (%s, round 180)`" % f for k, f in A.FAMILY.items()}
STATUS["wh_dlc03_character_abilities_foe_seeker"] = "`implemented (charge_or_tired, round 180)`"
STATUS["wh_main_character_abilities_foe_seeker_summoned"] = "`implemented (charge_or_tired, round 180)`"
STATUS["wh_dlc05_spell_bound_shield_of_thorns"] = "`implemented (melee_self_or_ally, round 180)`"
for k in A.WW_NOTE:
    STATUS[k] = None   # the cell keeps its status; the 80% note goes into section 10.58
for k, why in A.CLOSED.items():
    STATUS[k] = "`skipped (user decision 2026-11-18: closed, %s)`" % why.split(",")[0]
SECTION = """
### 10.58 Round 180 - the score-3 review, rows 87-114 and 128 (2026-11-18)

**Ruling (user, 2026-11-18):** "Row 128 set A / Rows 57-86 do not touch / Rows 87-90 implement without melee / Row 91-96
implement as in the doc / Row 98 improve / Rows 99-114 implement / 107 Mantra of Invigoration I like the option"
(`docs\\WH3_score3_review_2026-11-18.md`, every row's current text read from disk first). Round document
`docs\\WH3_round180_score3_rows4.md`.

**Changes:** the 4 ground roots (Entangle, Get 'Em!, Hunter's Snare, Hunter's Trap) on the existing fast-enemy pick, no
melee arm, and on their REAL 100 m cast range (they carried their 15 / 35 m AREA as their range); Shield of Thorns on
melee_self_or_ally; Blood Chalice of Bathori, Breath of Darkness x2, Mantra of Invigoration on NEW health_aura_ally_rule
(the lowest unit the game's own target rule allows: Lords/Heroes, undead, Tiger Warriors); Bugman's XXXXXX on NEW
self_heal_clear (no visible enemy within 38 m); Potion of Charoi and Skar's Kraken-Killer on NEW self_hurt_attacked;
Foe-Seeker on NEW charge_or_tired; Rock Bottom above 50% health only; Eat da Runts! on the cheapest healthy ally (no self
arm); Cold-Blooded on Lizardmen only (GENERATED '_lzd_' set, 'set A'). The 80% simulated reach for Sandstorm (46 -> 41
m), The Burning Head x2 (109 -> 78 m), Arnzipal's Black Horror (64 -> 44 m); Lamprey's Bite unchanged (a straight path).
CLOSED: Heaven's Gate (row 92), Snowflake Pendant (row 100), Stave of Avelorn (row 101). Kept: 94 (the data: the Loons
hit our units), 97 (not in the ruling), 102, 103, 109, 113.

**NOT BUILT, row 98 Land Mine:** its blast is 25 m in the game data; "half a packed block" over 25 m is 415 soldiers,
so it would almost never fire. Options go to the user.

**Arithmetic:** 935 entries / 989 keys / 133 families. Harness 179 full suite **7,622 checks / 0 failures**, twice
byte-identical; RED 42/42. Pack md5 `6fbdf834e0a2e7cee83d529d7a3c3700`; workbook v63.
"""
lines = open(P, encoding="utf-8").read().split("\n")
done = set()
for i, l in enumerate(lines):
    if not l.startswith("| "):
        continue
    cells = l.split("|")
    for k, st in STATUS.items():
        if ("`" + k + "`") in cells[1]:
            if st is not None:
                cells[2] = " " + st + " "
                lines[i] = "|".join(cells)
            done.add(k)
missing = set(STATUS) - done
assert not missing, missing
s = "\n".join(lines)
assert "### 10.58 " not in s
s = s.rstrip("\n") + "\n" + SECTION
open(P, "w", encoding="utf-8", newline="\n").write(s)
print("tracker: %d rows, section 10.58" % len(done))

TAG = {n: "**BUILT round 180**" for n in (87, 88, 89, 90, 91, 93, 95, 96, 99, 104, 105, 106, 107, 108, 110, 111, 112,
                                         114, 128)}
TAG[92] = "**CLOSED round 180**"
TAG[100] = "**CLOSED round 180**"
TAG[101] = "**CLOSED round 180**"
TAG[94] = "**KEPT round 180: the data says the fanatics hit our units**"
TAG[98] = "**NOT BUILT round 180: the blast is 25 m, half a packed block = 415 soldiers; options to the user**"
for n in (102, 103, 109, 113):
    TAG[n] = "**KEPT round 180**"
rl = open(REV, encoding="utf-8").read().split("\n")
marked = set()
for i, l in enumerate(rl):
    for n, t in TAG.items():
        if l.startswith("| %d | " % n):
            cells = l.split("|")
            if "round 180" in cells[2]:
                continue
            cells[2] = cells[2].rstrip() + " (" + t + ") "
            rl[i] = "|".join(cells)
            marked.add(n)
assert marked == set(TAG), set(TAG) - marked
open(REV, "w", encoding="utf-8", newline="\n").write("\n".join(rl))
print("review: %d rows marked" % len(marked))
