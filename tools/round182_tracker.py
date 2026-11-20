#!/usr/bin/env python3
"""Round 182: the tracker's status cells for the finishers, section 10.60; the mark on row 23 of the last review."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_xlsx_v65 as A  # noqa: E402

P = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_ability_tracker.md"
REV = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_low_score_review_2026-11-17.md"
STATUS = {k: "`implemented (%s, round 182)`" % f for k, f in A.FAMILY.items()}
SECTION = """
### 10.60 Round 182 - the finishers (2026-11-20)

**Rulings (user):** 2026-11-17 (`docs\\WH3_low_score_review_2026-11-17.md`, row 23 and section 7): "All of them should
have priority, if possible, for the entity with the lowest health percentage". 2026-11-20: the Executioner on 90% of
its range ("as with large entities we don't have the problem of edge-to-edge distance calculation"); the Emperor's
Executioner on "the highest health % first that is below the 20/33% threshold"; Skjalandir's Fall "Do what you think is
more adequate". Round document `docs\\WH3_round182_finishers.md`.

**Changes:** the Executioner on NEW enemy_finisher (the visible single-entity enemy with the lowest health %, the most
valuable on a tie, none of ours within 10 m, the caster standing still; 225 m bound = 90% of 250, the documented
exception); the Emperor's Executioner x2 rank the highest health % at or below their line; Skjalandir's Fall on NEW
melee_or_self_shooting (the game's phase: +90 accuracy and every hit, melee or shot, applies Blinded!).
melee_or_shooting_into_melee is empty now.

**Arithmetic:** 936 entries / 989 keys / 136 families. Harness 181 full suite **7,688 checks / 0 failures**, twice
byte-identical; RED 12/12. Pack md5 `d4d805f72cb520f034d0928ee0522ece`; workbook v65.
"""
lines = open(P, encoding="utf-8").read().split("\n")
done = set()
for i, l in enumerate(lines):
    if not l.startswith("| "):
        continue
    cells = l.split("|")
    for k, st in STATUS.items():
        if ("`" + k + "`") in cells[1]:
            cells[2] = " " + st + " "
            lines[i] = "|".join(cells)
            done.add(k)
assert done == set(STATUS), set(STATUS) - done
s = "\n".join(lines)
assert "### 10.60 " not in s
s = s.rstrip("\n") + "\n" + SECTION
open(P, "w", encoding="utf-8", newline="\n").write(s)
print("tracker: %d rows, section 10.60" % len(done))

rl = open(REV, encoding="utf-8").read().split("\n")
hit = 0
for i, l in enumerate(rl):
    if l.startswith("| 23 | Executioner |"):
        rl[i] = l.replace("| 23 | Executioner |", "| 23 | Executioner (**BUILT round 182: 90% bound, user 2026-11-20**) |", 1)
        hit += 1
    if l.startswith("## 7. FINISHERS (user ruling 2026-11-17)"):
        rl[i] = l + " - BUILT round 182 (the execute: the highest health % below the line, user 2026-11-20; Skjalandir's Fall: in melee or shooting, every hit blinds)"
        hit += 1
assert hit == 2, hit
open(REV, "w", encoding="utf-8", newline="\n").write("\n".join(rl))
print("review: row 23 and section 7 marked")
