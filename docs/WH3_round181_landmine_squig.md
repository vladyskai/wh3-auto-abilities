# Round 181: Land Mine, Surprise Squig!, the range fixes (sign-off round)

Date: 2026-11-20. Harness: `harness180.lua`. Release folder: `mod_source\releases\20261120_landmine_squig_harness180\`.

## 1. The ruling

User, 2026-11-20: "Row 98, Land Mine: A / Fix the range mismatches / 28 Surprise Squig! implement blob with clearance".
The review doc was re-read from disk first (no new edits since round 180).

## 2. What changed (what you will see in battle)

| Ability | Before | Now |
|---|---|---|
| Land Mine | in melee, none of ours within its 25 m blast + 10 m | the same, AND at least 60 enemy soldiers inside the 25 m blast (option A) |
| Surprise Squig! | summoned on the ground under an enemy in melee | summoned under the standing enemy infantry block worth the most inside the squig's 21 m explosion, none of ours within 31 m |
| Curse of Khsar | enemies within 24 m (its 35 m AREA was used as its range) | enemies within 70 m (its real 100 m) |
| Ravaging Swarm x2 | enemies within 21 m (30 m) | enemies within 70 m (its real 100 m) |
| Lord of Undeath | every key on 140 m (200 m) | five keys on their real 50 m (35 m bound); the sixth key (`_4`, 200 m) has its own entry and keeps 140 m |

- **The squig's explosion:** the game data gives Surprise Squig no blast of its own. It SUMMONS Explosive Squigs, whose
  passive "Squigs Go Boom" is a bombardment of radius 1 m + a 20 m blast = 21 m, marked as hitting allies. A NEW GENERATED
  table (`tools\gen_summon_blast.py`) reads this from the game.
- **No density line for the squig.** Your row-28 rule ("the most value in the blast, none of ours within blast + 10 m")
  has none, and the old blob rule's "half a packed block" would be 292 soldiers at 21 m (the Land Mine problem again).
  The squig needs a standing block (one that has not moved) with some value inside the explosion.
- **Counting soldiers in a big blast:** the old 19-point sampling counted a 30-man unit as about 43 men in a 25 m blast.
  The new count (`FOURTH.blast_cover`) caps each enemy unit at its own strength.
- **The range scan is now a build gate:** every key of every entry is compared with the game's target_intercept_range;
  the build refuses a mismatch (0 today).
- **Counts:** 936 entries (the Lord of Undeath split) / 989 keys; 135 families (+2).

## 3. The proof

| Run | Checks | Failures | File |
|---|---:|---:|---|
| FULL, run 1 | 7,663 | 0 | `h180_run1.txt` |
| FULL, run 2 | 7,663 | 0, byte-identical | `h180_run2.txt` |
| RED, pre-181 snapshot | 7,661 | 0; RED 20/20 | `h180_red.txt` |

**Section 180 (both files), 9 worlds and the cards:** Land Mine fires inside a 240-man block and not against a 30-man
unit (pre-181: it fired); the squig lands under the block worth 1,200 rather than the one worth 600 (pre-181: none), not
with our Swordsmen 15 m from the block, not on a moving block; Ravaging Swarm and Curse of Khsar reach an enemy 60 m away
(pre-181: none); the 50 m Lord of Undeath key does not reach 60 m (pre-181: it did); the 200 m key does, on its own
entry. The test world for Curse of Khsar uses a hurt caster: the game refuses Curse of Khsar above 50% health (the mod
honours that rule).

## 4. Pins rebased (harness 180 vs 179)

| Pin | Old | New | Why |
|---|---|---|---|
| entries (every 935) | 935 | 936 | the Lord of Undeath split |
| melee_clear (1) | 5 | 4 | Land Mine |
| range_real (2 + EXP) | 417 | 418 | the split |
| h179 CA8 | Land Mine's old card | its card with the 60-soldier line | row 98 |
| h179 0zz28 | "Land Mine NOT moved" | Land Mine on melee_clear_block | row 98 built |
| h97 the r30 family | Ravaging Swarm, 30 m / 21 m | Ravaging Swarm, 100 m / 70 m | its real range |

**Builder:** the same counts; the round-159 VORTEX generator now includes melee_clear_block (Land Mine keeps its 25 m
radius); the round-178 gate names Surprise Squig's new family; the ROUND 181 gate.

## 5. Build, install, documents

- **Installed pack:** md5 **`3e567bc557f624b8298378fb8107d156`**, 1,548,820 bytes; `IDENTICAL True`; `MATCHES SOURCE:
  True` four times; the COMPILE gate and the ROUND 123 to 181 gates passed.
- **Archived:** `archive\packs\zz_test_deadly_onslaught_20261120_round181.pack`; `archive\mod_source\round181\` (source
  md5 `f6a2995bad6e1d64a5bfc8d4eccafabe`).
- **Workbook:** `docs\WH3_abilities_master_v64_2026-11-20.xlsx` plus `.ods`; `XLSX v64 VERIFY OK` (2 moved rows, 9 range
  notes; v1-v63 byte-unchanged).
- **Tracker:** section 10.59. **Database, audits (0 candidates), progress page:** regenerated.

## 6. Not done

- **Not seen in game.** The next battle starts from byte 822,999,135.
- The last review's row 23 and its finishers section are still not built.
