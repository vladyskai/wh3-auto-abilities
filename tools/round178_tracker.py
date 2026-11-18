#!/usr/bin/env python3
"""Round 178: the tracker's status cells for the 22 moved keys, the Trophy Heads split and Eye of Khorne's value-first
pick, plus section 10.56."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_xlsx_v61 as A  # noqa: E402

P = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_ability_tracker.md"
STATUS = {k: "`implemented (%s, round 178)`" % fam for k, (fam, _) in A.MOVED.items()}
STATUS["wh3_dlc26_lord_abilities_eye_of_khorne"] = "`implemented (enemy_low_health_noncommander, value first, round 178)`"
STATUS["wh3_main_daemon_wings_abilities_trophy_heads"] = "`implemented (enemy_melee, own unclassed entry, round 178)`"
SECTION = """
### 10.56 Round 178 - the score-3 review, rows 23-55 (2026-11-18)

**Ruling (user, 2026-11-18):** "Approve rows 23-55. Row 56 stays the same." (`docs\\WH3_score3_review_2026-11-18.md`,
re-read from disk first: rows 49 and 53 carry the user's RULED lines). Round document `docs\\WH3_round178_score3_rows2.md`.

**Changes:** Chain Lightning x2 and The Soulstealer (row 23 RULED, "a minimum of 16 units for both": NEW
enemy_most_models, the visible enemy unit with the most models, counted up to the ability's own count, then the most
value per soldier; never below 16 models; standing still); Whip of Misery and Word of Pain x2 (enemy_melee_or_shooting:
the closest enemy in melee, else a shooting enemy; Whip keeps its large class); Soulnetter, Net of Amyntok, Spiderweb
Attack, Warp Gaze, Warpstiletto, Pack Trap (row 36 RULED, "Yes pls", no melee arm: the existing enemy_fast_near_ally);
Prey of Anath Raema, Net Dem Up (NEW enemy_fast_fire_melee: fast, else under our fire, else in melee); Glory Seeker x2
(row 44 RULED, "makes sense to also add root": NEW enemy_fast_or_melee, a charging Lord or Hero first, else one in
melee); Prey of the Blood God (enemy_commander_value); Void Pendulum, Word of Change, Dweomer Leach Orb, Slann Gold
(enemy_spellcaster, the spellcaster list); Eye of Khorne (row 53 RULED: the most valuable enemy below 20%, never a Lord
or Hero); Trophy Heads split (the Daemon Wings key has no Lord/Hero rule in the game data: its own unclassed entry).
Kept: Oil Flask (row 49 RULED: keep), Siegebreaker (row 55: its projectile deals 100 + 100 AP to units), row 56 (the
user's word). NOT BUILT: Surprise Squig (row 28): the game data shows it SUMMONS Explosive Squigs; the proposal misread
it, a new proposal follows. A real bug fixed on the way: the fast arm left FOURTH.eg_mode = "fast", so a fallback
cast was cancelled at the pre-cast re-check.

**The same mistake as round 171, caught before the commit:** the first build of this round followed the doc's FIRST
proposals for rows 23-24, 29, 36-41 and 44-45, although the user's RULED texts were already in the doc (committed with
round 177). It was installed (md5 `bb0b9fe7ab975f68862c3b4680ca9150`) but never committed; the second pass rebuilt the
rows from the RULED texts. A second RED control runs the harness against that first pass
(`docs\\backups\\round178\\first178_*.lua`, `H177_RED2=1`): 36/36, it reproduces each defect (Chain Lightning silent on
a 20-man unit, Net of Amyntok firing on a unit only in melee, Glory Seeker ignoring a charging Captain).

**Arithmetic:** 938 entries / 992 keys / 123 families. Harness 177 full suite **7,476 checks / 0 failures**, twice
byte-identical; RED 36/36 against pre-178 and 36/36 against the first pass. Pack md5
`b8622a7b2b6c9bb6ed1c8c5844cac5bf`; workbook v61.
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
assert "### 10.56 " not in s
s = s.rstrip("\n") + "\n" + SECTION
open(P, "w", encoding="utf-8", newline="\n").write(s)
print("tracker: %d rows, section 10.56" % len(done))
