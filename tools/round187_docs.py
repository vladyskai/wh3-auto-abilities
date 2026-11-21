#!/usr/bin/env python3
"""Round 187: the open-points doc (the Wulfhart battle closes the charge test; Focused Shot's line of fire and the badge
alignment are new items), the tracker (section 10.65) and CLAUDE.md."""
OPN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_open_points.md"
TRK = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_ability_tracker.md"
CMD = r"C:\Users\vlady\Desktop\WH3_mod\CLAUDE.md"


def sub(s, a, b):
    assert s.count(a) == 1, (a[:70], s.count(a))
    return s.replace(a, b)


o = open(OPN, encoding="utf-8").read()
o = sub(o, "| DEFERRED | User 2026-11-20: \"We'll do the in-game tests later\". |",
        "| PARTLY SEEN | User 2026-11-20: \"We'll do the in-game tests later\". 2026-11-21: one Wulfhart battle (Focused Shot, "
        "Hunter's Snare; archive\\logs\\battle_20261121_r186_wulfhart.txt). Next battle from byte 845,604,523. |")
o = sub(o, "| WAITING (user) | Goes with item 1. |",
        "| DONE (2026-11-21) | User: \"Hunters snare seemed to have worked fine\". Log: ONE cast at t=76.75 s on Knights of the "
        "Realm charging at 8.4 m/s, 38.9 m from Markus, placed on the ground under them. One charge, caught; direction is "
        "still not read (item 7). |")
o = sub(o, "\n## Closed\n",
        "| 13 | **Focused Shot made Markus walk** (2026-11-21 battle). The first cast (t=67.25 s, the Bretonnian Lord 122 m away, "
        "inside 175 m) was accepted but never fired: Markus walked 25 m straight toward the Lord, past our own Swordsmen, "
        "and stopped; the mod's second cast (t=77 s, 58.8 m) fired. Our Swordsmen stood across the line of fire (Markus "
        "x=-182, Lord x=-183, the Swordsmen's 29 m frontage at z=12.9 between them). Focused Shot is a flat shot "
        "(trajectory_sight low) that can hurt our own units. ASSUMPTION: the game walks the shooter to a clear line. "
        "61 of the mod's 89 enemy projectile keys are flat shots. | NEEDS A RULING | Options given 2026-11-21: A a line-of-fire "
        "check for every flat shot (none of our units across the caster-to-target line), B the same for the snipers only, "
        "C keep. |\n"
        "| 14 | **The badges and the ALL button left the wheel at another resolution or UI scale.** | DONE (round 187) | "
        "They now follow the wheel (a live correction every 2 s). Not yet seen in game at UI scale 1.6. |\n"
        "\n## Closed\n")
open(OPN, "w", encoding="utf-8", newline="").write(o)
print("open points updated")

SECTION = """
### 10.65 Round 187 - the badges follow the wheel at any resolution or UI scale (2026-11-21)

**Request (user, 2026-11-21):** "we need to fix the UI scale ... when I change Resolution in the game, the A/M and the arm
all buttons are not aligned anymore" (screenshot: the "A" at the left edge, away from its icon). Round document
`docs\\WH3_round187_uiscale.md`.

**Cause:** the badges and the ALL button dock to the screen's bottom centre with offsets tuned on a 1984 x 1116 UI space;
the wheel hangs from the bottom-left corner. At UI scale 1.6 (1600 x 900) the centre moved 192 px left of the wheel.

**Fix:** `FOURTH.ui_shift_tick` reads the wheel (`ability_parent`) and the bottom centre (`orders_parent`) every 2 s and
moves every badge and the ALL button by the difference from the tuned frame. No roster change.

**Also from the 2026-11-21 battle:** Hunter's Snare caught a real charge (one cast); Focused Shot's first cast made
Markus walk past our own Swordsmen (line of fire), a ruling is pending.

**Proof:** harness 186 full suite **7,863 checks / 0 failures**, twice byte-identical; RED 8/8. Pack md5
`816abe086cd75efbb8297bd237a8470e`.
"""
t = open(TRK, encoding="utf-8").read()
assert "### 10.65 " not in t
open(TRK, "w", encoding="utf-8", newline="\n").write(t.rstrip("\n") + "\n" + SECTION)
print("tracker: section 10.65")

c = open(CMD, encoding="utf-8").read()
for a, b in (
    ("- Installed build: md5 `8bf23234706e1647946a84cc0e33a969`, 1,579,341 bytes\n"
     "  (round 186, 2026-11-20: Warpstorm Scroll as a damage dealer).",
     "- Installed build: md5 `816abe086cd75efbb8297bd237a8470e`, 1,582,433 bytes\n"
     "  (round 187, 2026-11-21: the badges follow the wheel at any resolution or UI scale)."),
    ("../mod_source/releases/20261120_warpstorm_harness185/build_and_install186.py",
     "../mod_source/releases/20261121_uiscale_harness186/build_and_install187.py"),
    ("(harness185: 7,844 checks; it takes about 10 s)", "(harness186: 7,863 checks; it takes about 10 s)"),
    ("  -123 (off screen); only the slot-2 badge peeks in at x = 5. Not fixed; waiting for the user.",
     "  -123 (off screen); only the slot-2 badge peeks in at x = 5. FIXED in round 187: FOURTH.ui_shift_tick moves every\n"
     "  badge and the ALL button by (wheel shift - bottom-centre shift) from the tuned 1984 x 1116 frame (refs\n"
     "  ability_parent 42,893 / orders_parent 691,1055; Position() only; every 40 ui ticks = 2 s; the ui tick runs every\n"
     "  50 ms). Not yet seen in game at 1.6."),
    ("- ROUND 186 (2026-11-20): Warpstorm Scroll",
     "- ROUND 187 (2026-11-21): the badges follow the wheel (see ENGINE FACTS, badge placement). The Wulfhart battle\n"
     "  (archive\\logs\\battle_20261121_r186_wulfhart.txt, bytes 822,999,135-845,604,523): Hunter's Snare caught a real\n"
     "  charge (open point 2 DONE); Focused Shot's first cast made Markus walk 25 m past our own Swordsmen standing across\n"
     "  the line of fire (flat shot, trajectory_sight low; the cast never fired, the second did): a line-of-fire check is\n"
     "  proposed (open point 13), NOT built. Next battle from byte 845,604,523.\n"
     "- ROUND 186 (2026-11-20): Warpstorm Scroll"),
):
    c = sub(c, a, b)
open(CMD, "w", encoding="utf-8", newline="").write(c)
print("CLAUDE.md updated")
