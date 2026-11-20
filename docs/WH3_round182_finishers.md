# Round 182: the finishers (sign-off round)

Date: 2026-11-20. Harness: `harness181.lua`. Release folder: `mod_source\releases\20261120_finishers_harness181\`.

## 1. The rulings

- 2026-11-17 (`docs\WH3_low_score_review_2026-11-17.md`, row 23 and section 7): "No need for a max-hit-points table,
  let's just rely on percentages ... All of them should have priority, if possible, for the entity with the lowest
  health percentage".
- 2026-11-20, the Executioner's range: "In this case let's do 90%, as with large entities we don't have the problem of
  edge-to-edge distance calculation making the caster move to do the cast."
- 2026-11-20, the Emperor's Executioner: "it would make sense for the highest health % first that is below the 20/33%
  threshold".
- 2026-11-20, Skjalandir's Fall: "Do what you think is more adequate" (with the effect list found online).

## 2. What changed (what you will see in battle)

| Ability | Before | Now |
|---|---|---|
| Executioner | the blob rule (the most value in its 1 m blast), within 175 m | NEW **enemy_finisher:** the visible single-entity enemy (Lord, Hero or monster) with the LOWEST health %, the most valuable on a tie, none of ours within 10 m, the caster standing still; within **225 m** (90% of 250) |
| The Emperor's Executioner (base 20%, upgrade 33%) | the most valuable enemy at or below the line | the enemy at or below the line with the HIGHEST health % left (the most valuable on a tie) |
| Skjalandir's Fall | in melee, or shooting at an enemy that is in melee | NEW **melee_or_self_shooting:** in melee (not wavering) or shooting at anything |

- **Skjalandir's Fall, from the game data:** its 39 s phase gives +90 accuracy (your source says +100: probably an older
  patch) and `imbue_contact` = Blinded!, so EVERY hit Ulrika lands, melee or shot, applies Blinded! (x0.5 speed, -25
  melee attack, melee defence, missile block, accuracy; 26 s in the data, 25 s in your source). Every part of the debuff
  pays on any target (the slow against movers, the accuracy cut against shooters, the melee cuts in a fight), so the
  "into melee" limit only cost uptime. The kill-shot projectile in the data is not linked to the ability.
- **The 90% exception** is a named constant (`FOURTH.SINGLE_RANGE_FRACTION = 0.90`) on the Executioner's entry alone
  (`range_frac = 0.90`); the build refuses it on any other entry. It is the second documented exception to the 70% rule
  (the first is the air-drop test value). The reasoning holds: the mod measures edge to edge, and for a single man or
  monster the edge and the centre are a few metres apart, so 225 m leaves a 25 m margin.
- **Counts:** 936 entries / 989 keys; 136 families (+2, and melee_or_shooting_into_melee is now empty). The SHOT table
  covers the Executioner (61 keys); the blob tables lose it (68).

## 3. The proof

| Run | Checks | Failures | File |
|---|---:|---:|---|
| FULL, run 1 | 7,688 | 0 | `h181_run1.txt` |
| FULL, run 2 | 7,688 | 0, byte-identical | `h181_run2.txt` |
| RED, pre-182 snapshot | 7,686 | 0; RED 12/12 | `h181_red.txt` |

**Section 181 (both files), 5 worlds and the cards:** the Executioner takes the hero at 30% over the one at 80% (pre-182:
not it), reaches a hero 210 m away (pre-182: none), and holds with our Swordsmen 5 m from the target; the Emperor's
Executioner takes the Lord at 15% over the one at 5% (pre-182: the more valuable 5% one); Skjalandir's Fall casts while
shooting at a target that is not in melee (pre-182: none).

## 4. Pins rebased (harness 181 vs 180)

| Pin | Old | New | Why |
|---|---|---|---|
| enemy_blob (2) | 69 | 68 | the Executioner left |
| h129 0y | Skjalandir on melee_or_shooting_into_melee | melee_or_self_shooting | the move |
| h129 S1b | the "into melee" reason | the plain shooting reason | the move |
| h129 S2 | shooting at a target not in melee: no cast | it casts (24 polls: the mock accepts repeats, so "at least one") | every shot blinds |
| h93 TIP mirror | - | + 2 labels; the Emperor's Executioner's label | new families |

**Builder:** enemy_blob 69 -> 68; the SHOT key gates 60 -> 61; the round-130 gate names Skjalandir's new family; the
ROUND 182 gate.

## 5. Build, install, documents

- **Installed pack:** md5 **`d4d805f72cb520f034d0928ee0522ece`**, 1,551,894 bytes; `IDENTICAL True`; `MATCHES SOURCE:
  True` four times; the COMPILE gate and the ROUND 123 to 182 gates passed.
- **Archived:** `archive\packs\zz_test_deadly_onslaught_20261120_round182.pack`; `archive\mod_source\round182\` (source
  md5 `a2e41aef164713221b5defed5f63d7f7`).
- **Workbook:** `docs\WH3_abilities_master_v65_2026-11-20.xlsx` plus `.ods`; `XLSX v65 VERIFY OK` (4 rows; v1-v64
  byte-unchanged).
- **Tracker:** section 10.60. **Database, audits (0 candidates), progress page:** regenerated.

## 6. Not done

- **Not seen in game.** The next battle starts from byte 822,999,135. No battle has been read since round 175.
