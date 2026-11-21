# Round 189 release: the line of fire (2026-11-21)

User ruling: "I would just do the check for terrain on all 35 and units on all 35. Just let's be safe, and if it doesn't
fire, that's okay."

- The 35 abilities the game marks "Requires line of sight to the target" (Focused Shot, Dead Eye, the Executioner, the
  breaths, the fireballs, the volleys ...) only fire at an enemy whose straight line from the caster is clear of every
  other unit (ours and the enemy's) and of the ground. A blocked enemy is skipped; the next best clear one is taken.
- Every unreadable read blocks (fail-closed); a failing ground read is logged once per battle.
- Harness 188: 7,921 checks / 0 failures (twice); RED control on the pre-189 code reproduces the Wulfhart case.
- Installed pack md5 `dab056dfb3b0508d31575de3b78e8a95`, 1,598,851 bytes.
- Workbook v71 (35 trigger texts). Round document: `docs\WH3_round189_lineoffire.md`.
- Not seen in game yet. Next battle from log byte 860,397,883.
