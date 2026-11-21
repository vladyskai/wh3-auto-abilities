# Round 192 release: the closing check, the Moulder rule, Grombrindal Has No Fear, the spell-bar runes (2026-11-21)

- A fast enemy counts only while it RUNS (is_moving_fast) and CLOSES on our units (the gap shrinks 3 m/s over 1 s):
  enemy_fast_near_ally and every fast arm. Riding past, walking or running away no longer triggers the slows.
- Shock Collar and Remouldered: Clan Moulder monsters only (the game's rule; GENERATED set of 28 units).
- NEW: Grombrindal Has No Fear on melee_or_wavering_aura (55 m aura -> 38 m).
- REMOVED: Rune of Breaking, Negation, Slowness, Speed, Oath & Steel (right-hand spell bar). 984 entries / 1,037 keys.
- Harness 191: 8,010 checks / 0 failures (twice, identical); RED reproduces the old behaviour.
- Installed pack md5 `1a12ea1543904e6ae0fc01799d3a905d`, 1,603,485 bytes. Workbook v74 (1,802 rows; Scry-Orb open).
- Round document: `docs\WH3_round192_closing.md`. Next battle from log byte 881,292,588.
