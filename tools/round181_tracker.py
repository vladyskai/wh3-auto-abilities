#!/usr/bin/env python3
"""Round 181: the tracker's status cells (Land Mine, Surprise Squig!, the range-fixed rows), section 10.59; the marks on
rows 28 and 98 of the score-3 review."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_xlsx_v64 as A  # noqa: E402

P = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_ability_tracker.md"
REV = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_score3_review_2026-11-18.md"
STATUS = {k: "`implemented (%s, round 181)`" % f for k, f in A.FAMILY.items()}
for k in A.NOTE:
    STATUS[k] = None   # the status stays; the range fix is in section 10.59
SECTION = """
### 10.59 Round 181 - Land Mine, Surprise Squig!, the range fixes (2026-11-20)

**Ruling (user, 2026-11-20):** "Row 98, Land Mine: A / Fix the range mismatches / 28 Surprise Squig! implement blob with
clearance". Round document `docs\\WH3_round181_landmine_squig.md`.

**Changes:** Land Mine on NEW melee_clear_block (in melee, none of ours within its 25 m blast + 10 m, and at least 60
enemy soldiers inside the blast); Surprise Squig! on NEW enemy_summon_blob (the standing enemy infantry block worth the
most inside the summoned squig's 21 m explosion, none of ours within 31 m, the squig placed on that block's ground;
GENERATED SUMMON_BLAST from the game data). The range fixes (rule 3): Curse of Khsar 35 -> 100 m, Ravaging Swarm x2
30 -> 100 m, Lord of Undeath split (five 50 m keys 200 -> 50; the 200 m key on its own entry). The every-key range scan is
now a build gate (0 mismatches).

**Arithmetic:** 936 entries / 989 keys / 135 families. Harness 180 full suite **7,663 checks / 0 failures**, twice
byte-identical; RED 20/20. Pack md5 `3e567bc557f624b8298378fb8107d156`; workbook v64.
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
assert not (set(STATUS) - done), set(STATUS) - done
s = "\n".join(lines)
assert "### 10.59 " not in s
s = s.rstrip("\n") + "\n" + SECTION
open(P, "w", encoding="utf-8", newline="\n").write(s)
print("tracker: %d rows, section 10.59" % len(done))

rl = open(REV, encoding="utf-8").read().split("\n")
TAG = {28: "**BUILT round 181: blob with clearance (21 m explosion)**", 98: "**BUILT round 181: option A (60 soldiers)**"}
marked = set()
for i, l in enumerate(rl):
    for n, t in TAG.items():
        if l.startswith("| %d | " % n):
            cells = l.split("|")
            cells[2] = cells[2].rstrip() + " (" + t + ") "
            rl[i] = "|".join(cells)
            marked.add(n)
assert marked == set(TAG)
open(REV, "w", encoding="utf-8", newline="\n").write("\n".join(rl))
print("review: rows 28 and 98 marked")
