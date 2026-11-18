#!/usr/bin/env python3
"""Round 178: mark rows 23-56 of the score-3 review with what was built (the same form as rows 1-22)."""
P = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_score3_review_2026-11-18.md"
TAG = {}
for n in (23, 24, 29, 30, 31, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 50, 51, 53, 54):
    TAG[n] = "**BUILT round 178**"
for n in (25, 26, 27, 32, 33, 34, 35, 52):
    TAG[n] = "**KEPT round 178**"
TAG[49] = "**KEPT round 178 (user: keep)**"
TAG[55] = "**KEPT round 178 (the data: 100 + 100 AP to units, so it harms units)**"
TAG[56] = "**KEPT round 178 (user: stays the same)**"
TAG[28] = "**NOT BUILT round 178: the data shows it SUMMONS Explosive Squigs; a new proposal follows**"
lines = open(P, encoding="utf-8").read().split("\n")
done = set()
for i, l in enumerate(lines):
    for n, t in TAG.items():
        head = "| %d | " % n
        if l.startswith(head):
            cells = l.split("|")
            assert "round 17" not in cells[2], (n, cells[2])
            cells[2] = cells[2].rstrip() + " (" + t + ") "
            lines[i] = "|".join(cells)
            done.add(n)
assert done == set(TAG), set(TAG) - done
open(P, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
print("marked", len(done))
