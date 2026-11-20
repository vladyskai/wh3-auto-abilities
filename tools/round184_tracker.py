#!/usr/bin/env python3
"""Round 184: the tracker's status cells for the rule-shut review rows 10-19, section 10.62; rows 10-19 of the review
doc marked BUILT; the open-points doc updated."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_xlsx_v67 as A  # noqa: E402

P = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_ability_tracker.md"
REV = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_rule_shut_review_2026-11-20.md"
OPN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_open_points.md"
STATUS = {k: "`implemented (%s, round 184)`" % f for k, f in A.FAMILY.items()}
SECTION = """
### 10.62 Round 184 - the rule-shut review, rows 10-19 (2026-11-20)

**Ruling (user, 2026-11-20):** "Up to #19 ruled". Read from the Claude Docs review "Rule-shut abilities review" (rev 83)
and its threads: rows 10-12 "Recommended" = A2 (the enemy need not stand still), 13-15 and 18-19 "Recommended", row 14
without clearance ("if not damage, then no need for clearance check"), row 16 "B with the 75% gate", row 17 "same as
#16". Round document `docs\\WH3_round184_ruleshut2.md`.

**Finding:** `enemy_area_drain` never required the enemy to stand still (its standing-still gate is the caster's, for
animated casts only), so A2 is the shipped rule. A reply in the doc's thread had said otherwise.

**Changes:** 10 NEW entries: Flock of Doom x3, Sword of Daith, Zefet-nebtar on `enemy_area_drain`; Ring of Corin,
Warpstorm Scroll (`target_class = "flying"`) on `enemy_single_drain`; Soul Stealer x2 on NEW `enemy_area_drain_hurt`
(the area drain at 75% health or less); Raging Tornado on NEW `enemy_ground_melee_cluster` (on the ground under the
thickest melee of enemies; its key joins `enemy_ground_keys`). 7 multi-use holds, 3 wind-ups.

**Arithmetic:** 955 entries / 1,008 keys / 138 families. Harness 183 full suite **7,762 checks / 0 failures**, twice
byte-identical; RED 20/20. Pack md5 `18aac090ab99114b1ac3c83eb483dd8c`; workbook v67.
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
assert "### 10.62 " not in s
s = s.rstrip("\n") + "\n" + SECTION
open(P, "w", encoding="utf-8", newline="\n").write(s)
print("tracker: %d rows, section 10.62" % len(done))

rl = open(REV, encoding="utf-8").read().split("\n")
hit = 0
for i, l in enumerate(rl):
    for n in range(10, 20):
        pre = "| %d | " % n
        if l.startswith(pre) and "BUILT round 184" not in l:
            ks = [k for k in A.T if ("`%s`" % k) in l]
            assert len(ks) == 1, (n, ks)
            cells = l.split(" | ")
            cells[1] = cells[1] + " (**BUILT round 184: %s**)" % A.T[ks[0]][0]
            rl[i] = " | ".join(cells)
            hit += 1
assert hit == 10, hit
open(REV, "w", encoding="utf-8", newline="\n").write("\n".join(rl))
print("review: rows 10-19 marked")

o = open(OPN, encoding="utf-8").read()
a = "| IN REVIEW (rows 1-9 BUILT, round 183) |"
assert o.count(a) == 1
o = o.replace(a, "| IN REVIEW (rows 1-9 BUILT round 183, rows 10-19 BUILT round 184) |")
open(OPN, "w", encoding="utf-8", newline="").write(o)
print("open points: item 3 updated")
