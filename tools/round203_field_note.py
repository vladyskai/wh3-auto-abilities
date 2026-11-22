#!/usr/bin/env python3
"""After round 203: the field result of free aim and the sideways-shift proposal, into CLAUDE.md and open point 25."""
ROOT = "C:\\Users\\vlady\\Desktop\\WH3_mod\\"


def one(s, a, b):
    assert s.count(a) == 1, (a[:70], s.count(a))
    return s.replace(a, b)


def main():
    p = ROOT + "CLAUDE.md"
    s = open(p, encoding="utf-8", newline="").read()
    nl = "\r\n" if "\r\n" in s else "\n"
    a = "  headings. A heredoc broke two inline Python edits this round (again): edit tools with Edit / Write only."
    note = [
        a,
        "  FIELD 2026-11-22 (archive\\logs\\battle_20261122_r203_freeaim.txt, bytes 1,021,602,177-1,027,314,867: the Engineer",
        "  + 2 Miners vs 3 Skeleton Warriors): the ring STILL never fired, no FREE AIM line. CAUSE (tools\\replay_free_aim.py,",
        "  rectangles with an estimated depth): every round-203 path runs THROUGH THE ENEMY'S CENTRE, and an enemy in melee",
        "  with ours has its centre 6-10 m from our unit, inside the 16 m clearance. Through the centre at the 10 m margin: a",
        "  clear path in 0 of 21 snapshots here and 0 of 25 in the Zombie battle (Claude's claim that round 203 fixed the",
        "  Zombie battle was WRONG: the harness world had the Miners 30 m in front of the Zombies, not in melee). WITH",
        "  SIDEWAYS SHIFTS of the path (0, +-4 ... +-20 m: along the enemy's rear, what the user draws by hand) at the SAME",
        "  10 m margin: a clear path in 21 of 21 and 25 of 25, median 53 / 200 soldiers covered (margin 6 m: 108 / 310,",
        "  3 m: 191 / 381). PROPOSED, WAITING: sideways shifts + value by SOLDIERS COVERED (today a clipped unit counts whole)",
        "  + a minimum of 60 soldiers, and the user's choice of margin. Tidecall / Wind Blast are on the charge trigger by",
        "  the user's round-164 ruling \"Charge, clear path\" (speed x0.75 for 10 s, rule 10). Next battle from byte",
        "  1,027,314,867.",
    ]
    s = one(s, a, nl.join(note))
    open(p, "w", encoding="utf-8", newline="").write(s)
    print("CLAUDE.md updated")


if __name__ == "__main__":
    main()
