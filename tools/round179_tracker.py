#!/usr/bin/env python3
"""Round 179: the tracker's status cells for the 12 moved keys and the 3 re-ruled ones, plus section 10.57; and the
marks on rows 115-134 of the score-3 review."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_xlsx_v62 as A  # noqa: E402

P = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_ability_tracker.md"
REV = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_score3_review_2026-11-18.md"
STATUS = {k: "`implemented (%s, round 179)`" % v[0] for k, v in A.MOVED.items()}
STATUS["wh3_dlc29_lord_active_commanding_presence"] = "`implemented (wavering_self_or_ally, no melee condition, round 179)`"
STATUS["wh3_dlc29_spell_bound_prayer_fury_of_ulric"] = "`implemented (wavering_self_or_ally, no melee condition, round 179)`"
STATUS["wh3_main_item_abilities_gruts_sickle"] = "`implemented (ally_winds: low winds, expendable first, round 179)`"
SECTION = """
### 10.57 Round 179 - the score-3 review, rows 115-134 (2026-11-18)

**Ruling (user, 2026-11-18):** "Items 115-134 approved" (`docs\\WH3_score3_review_2026-11-18.md`; every row's current
text read from disk first: rows 126 and 132 KEEP, row 129 "the caster included", row 133 the user's Grut's Sickle rule).
Round document `docs\\WH3_round179_score3_rows3.md`.

**Changes:** Inspired Assault I-III (NEW ally_charge_or_melee: the nearest ally charging, else just in contact, else in
melee; never a missile unit); Inspired Defence I-III and Da Boss 'as a Plan! (NEW ally_melee_wavering_first: the
nearest ally in melee, a wavering one first); Favour of the Fay (melee_self_or_ally); Orcs are da Best! (NEW
ally_value_melee: the most valuable ally in melee, never a missile unit); Hellish Vigour (NEW ally_in_melee); Berry Wine
(NEW health_aura_ally_deep: 55%); Star of Avelorn (NEW heal_ground_best: the ground under the hurt unit with the most
hurt units within 10 m, within 140 m); Commanding Presence and Fury of Ulric (the hidden "ally in melee" condition
removed); Grut's Sickle (low winds only; an expendable ally first, else the cheapest ally above 75%). The 12 moved
entries keep their default (start_armed). Kept: 125, 126, 132, 134. Row 128 Cold-Blooded keeps its trigger; its
Lizardmen-only restriction waits (no lizard attribute in the game data: the set needs the user's look first).

**Found on the way:** the shared heal re-check tested the chosen ally against the AREA radius (10 m for Star of
Avelorn), so the new ground pick could never cast past 10 m; and Berry Wine's re-check still used 75%. Both fixed
(ah_mode "spot" / "deep"); harness world S3 caught it.

**Arithmetic:** 938 entries / 992 keys / 129 families. Harness 178 full suite **7,537 checks / 0 failures**, twice
byte-identical; RED 32/32. Pack md5 `d7588fbfd32a951c9c65b4b1b052c284`; workbook v62.
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
assert "### 10.57 " not in s
s = s.rstrip("\n") + "\n" + SECTION
open(P, "w", encoding="utf-8", newline="\n").write(s)
print("tracker: %d rows, section 10.57" % len(done))

TAG = {n: "**BUILT round 179**" for n in (115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 127, 129, 130, 131, 133)}
TAG.update({n: "**KEPT round 179**" for n in (125, 126, 132, 134)})
TAG[128] = "**KEPT round 179; the Lizardmen restriction waits for your look at the set**"
rl = open(REV, encoding="utf-8").read().split("\n")
marked = set()
for i, l in enumerate(rl):
    for n, t in TAG.items():
        if l.startswith("| %d | " % n):
            cells = l.split("|")
            assert "round 17" not in cells[2], (n, cells[2])
            cells[2] = cells[2].rstrip() + " (" + t + ") "
            rl[i] = "|".join(cells)
            marked.add(n)
assert marked == set(TAG), set(TAG) - marked
open(REV, "w", encoding="utf-8", newline="\n").write("\n".join(rl))
print("review: %d rows marked" % len(marked))
