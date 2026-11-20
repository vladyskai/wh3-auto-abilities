#!/usr/bin/env python3
"""Round 183: the tracker's status cells for the rule-shut review rows 1-9, section 10.61; rows 1-9 of the review doc
marked BUILT; the open-points doc updated."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_xlsx_v66 as A  # noqa: E402

P = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_ability_tracker.md"
REV = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_rule_shut_review_2026-11-20.md"
OPN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_open_points.md"
STATUS = {k: "`implemented (%s, round 183)`" % f for k, f in A.FAMILY.items()}
SECTION = """
### 10.61 Round 183 - the rule-shut review, rows 1-9 (2026-11-20)

**Ruling (user, 2026-11-20):** "You may start implementing #1-9 for now". The rulings are read from the Claude Docs
review "Rule-shut abilities review" (rev 44) and its comment threads: rows 1-4 "Recommended" (B), row 5 "B" ("the heal
is considerable, we shouldn't waste it"), row 6 "Recommended" = C ("just in melee and less that 75% health"), rows 7-8
"A", row 9 "Other": "Melee_unwavering". Round document `docs\\WH3_round183_ruleshut1.md`.

**Finding:** the 2026-10-09 "own-troop damage" rule was wrong for all 19 of its rows: every damage phase targets enemies
only (`phase_junc`).

**Changes:** 9 NEW entries on existing families: Defiling Deluge, Murderous Exhortations, Rod of Corruption, Wail of
Malice on `enemy_melee_near` (35 m aura, 24 m bound); Plaguereaper, Reaper of Souls on `melee_health75`; Shard Blade, Web
of Shadows, Warp-Quake on `melee_unwavering`. 6 multi-use keys held for their recharge.

**Arithmetic:** 945 entries / 998 keys / 136 families. Harness 182 full suite **7,721 checks / 0 failures**, twice
byte-identical; RED 16/16. Pack md5 `bde9bc18a104768c685084b70d274fa7`; workbook v66.
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
assert "### 10.61 " not in s
s = s.rstrip("\n") + "\n" + SECTION
open(P, "w", encoding="utf-8", newline="\n").write(s)
print("tracker: %d rows, section 10.61" % len(done))

rl = open(REV, encoding="utf-8").read().split("\n")
hit = 0
for i, l in enumerate(rl):
    for n in range(1, 10):
        pre = "| %d | " % n
        if l.startswith(pre) and "BUILT round 183" not in l:
            cells = l.split(" | ")
            cells[1] = cells[1] + " (**BUILT round 183: %s**)" % A.T[[k for k in A.T if ("`%s`" % k) in l][0]][0]
            rl[i] = " | ".join(cells)
            hit += 1
assert hit == 9, hit
open(REV, "w", encoding="utf-8", newline="\n").write("\n".join(rl))
print("review: rows 1-9 marked")

o = open(OPN, encoding="utf-8").read()
a = "| IN REVIEW | `docs\\WH3_rule_shut_review_2026-11-20.md`"
assert o.count(a) == 1
o = o.replace(a, "| IN REVIEW (rows 1-9 BUILT, round 183) | `docs\\WH3_rule_shut_review_2026-11-20.md`")
open(OPN, "w", encoding="utf-8", newline="").write(o)
print("open points: item 3 updated")
