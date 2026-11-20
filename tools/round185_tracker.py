#!/usr/bin/env python3
"""Round 185: the tracker's status cells for the rule-shut review rows 20-64 (33 built, 12 closed), section 10.63; rows
20-64 of the review doc marked; the open-points doc updated."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_xlsx_v68 as A  # noqa: E402

P = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_ability_tracker.md"
REV = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_rule_shut_review_2026-11-20.md"
OPN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_open_points.md"
STATUS = {k: "`implemented (%s, round 185)`" % f for k, f in A.FAMILY.items()}
STATUS.update({k: "`%s`" % A.closed_reason(k) for k in A.CLOSED})
SECTION = """
### 10.63 Round 185 - the rule-shut review, rows 20-64 (2026-11-20)

**Ruling (user, 2026-11-20):** "Review ended, implement pls". Read from the Claude Docs review "Rule-shut abilities
review" (rev 127) and its threads: rows 20-36 "Recommended" (thread: "set all as recomended"), 37-40 "B", 41
"Recommended", 42-48 "rule as recommended" (keep shut), 49-53 "rule as recommended" (parked with the stances), 54
"Recommended", 55 "Last stand", 56 and 58-64 "Recommended", 57 "A". Round document `docs\\WH3_round185_ruleshut3.md`.

**Built (33 entries):** 13 safe self-centred blasts on `melee_unwavering`; Glacial Blast, Thundermace on `melee_clear`;
Cellular Instability on `melee_clear_block`; Splode da Big 'Un! and the Master Rune of Immolation on `last_stand_clear`
(the rune's bombardment radius is now read by `gen_vortex_tables`: 10 m); Battle Howl x2 and the Silver Horn of
Vengeance on NEW `aura_charge_only`; Twilight Horn II on `self_or_ally_charge`; Swiftness of Itzl on `charge_only`;
Bonecrusher on `enemy_blob_vortex`; Beastlord's Gaze on `ally_melee_risk`; Fog of the Damned on
`enemy_ground_melee_cluster`; Locus of Contagion on `enemy_melee_near`; Mad Cap Mushrooms on `self_recharging`; Mirror
of Knowledge on `enemy_fast_near_ally` (unbounded, ground); Offering to the Gods on NEW `ally_offering` (30+ men); the
Seismic Snares on `slow_aura`; the Black Gem of Gnar on `self_last_stand`.

**Closed (12):** the 7 stealth abilities and the 5 mutually exclusive ones (Zhangu War Drum x3, Festus x2).

**Arithmetic:** 988 entries / 1,041 keys / 140 families. Harness 184 full suite **7,831 checks / 0 failures**, twice
byte-identical; RED 34/34. Pack md5 `0779eb3ef6eaf41e929b86d890270e4e`; workbook v68.
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
assert "### 10.63 " not in s
s = s.rstrip("\n") + "\n" + SECTION
open(P, "w", encoding="utf-8", newline="\n").write(s)
print("tracker: %d rows, section 10.63" % len(done))

rl = open(REV, encoding="utf-8").read().split("\n")
hit = 0
for i, l in enumerate(rl):
    for n in range(20, 65):
        pre = "| %d | " % n
        if l.startswith(pre) and "round 185" not in l:
            ks = [k for k in list(A.T) + list(A.CLOSED) if ("`%s`" % k) in l]
            assert len(ks) == 1, (n, ks)
            k = ks[0]
            tag = ("BUILT round 185: %s" % A.T[k][0]) if k in A.T else "CLOSED round 185: user decision"
            cells = l.split(" | ")
            cells[1] = cells[1] + " (**%s**)" % tag
            rl[i] = " | ".join(cells)
            hit += 1
assert hit == 45, hit
open(REV, "w", encoding="utf-8", newline="\n").write("\n".join(rl))
print("review: rows 20-64 marked")

o = open(OPN, encoding="utf-8").read()
for a, b in (("| IN REVIEW (rows 1-9 BUILT round 183, rows 10-19 BUILT round 184) |",
              "| DONE (rounds 183-185: 51 built, 1 left as built with a question, 12 closed) |"),
             ('| 4 | **Your 9 "skipped (revisit)" abilities.** | IN REVIEW | Same doc, section 7. |',
              '| 4 | **Your 9 "skipped (revisit)" abilities.** | DONE (round 185: all 9 built) | Same doc, section 7. |'),
             ("| IN REVIEW | Silver Horn is row 40 of the review doc. |",
              "| DONE | Silver Horn built in round 185 (row 40, 'B'); Grombrindal Has No Fear still deferred. |")):
    assert o.count(a) == 1, a
    o = o.replace(a, b)
open(OPN, "w", encoding="utf-8", newline="").write(o)
print("open points: items 3, 4, 6 updated")
