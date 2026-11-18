# Round 178: the score-3 review, rows 23-55 (sign-off round)

Date: 2026-11-18. Harness: `harness177.lua`. Release folder: `mod_source\releases\20261118_score3_rows2_harness177\`.

## 1. The ruling

User, 2026-11-18: "Approve rows 23-55. Row 56 stays the same." (`docs\WH3_score3_review_2026-11-18.md`.) The doc was
re-read from disk (git diff against its last commit). The user's RULED lines in it decide these rows:

- Row 23 (and 24, 29): "should not be unused if there are less models in the unit. Maybe preference for numerous
  entities units" and "a minimum of 16 units for both".
- Row 36 (for 36-41): "Yes pls", no melee arm.
- Row 44 (and 45): "makes sense to also add root".
- Row 49: "almost no damage value, so we keep it the same without need for clearance".
- Row 53: "the below 20% highest value unit that is not a lord or hero".

## 2. What changed (what you will see in battle)

| Row | Ability | Before | Now |
|---|---|---|---|
| 23, 24, 29 | Chain Lightning x2, The Soulstealer | the blob attack / an enemy in melee | NEW **enemy_most_models:** the visible enemy unit with the most soldiers, counted up to the ability's own count (75 / 25: a unit at or above it ranks as full, then the most value per soldier wins), never below 16 soldiers; the caster standing still |
| 30, 31 | Whip of Misery, Word of Pain x2 | in melee or under fire | **enemy_melee_or_shooting** (exists): the closest enemy in melee, else the closest one that is shooting; Whip keeps its large-only rule |
| 36-41 | Gilellion's Soulnetter, Net of Amyntok, Spiderweb Attack, Warp Gaze, Warpstiletto, Pack Trap | in melee or under fire | **enemy_fast_near_ally** (exists): only a fast enemy closing within 40 m of our units; the root stops the charge. Never on a unit already in melee |
| 42, 43 | Prey of Anath Raema, Net Dem Up! | in melee or under fire | NEW **enemy_fast_fire_melee:** a fast enemy closing, else the closest enemy our missiles are hitting, else the closest in melee |
| 44, 45 | Glory Seeker x2 | in melee or under fire | NEW **enemy_fast_or_melee:** an enemy Lord or Hero charging at us, else one in melee |
| 46 | Prey of the Blood God | in melee or under fire | **enemy_commander_value** (exists): the most valuable visible Lord or Hero in range |
| 47, 48, 50, 51 | Void Pendulum, Word of Change, Dweomer Leach Orb, Slann Gold | Lord/Hero stand-in | **enemy_spellcaster** (exists): the most valuable visible enemy spellcaster (the round-174 list) |
| 53 | Eye of Khorne | the lowest-health enemy below 20% | the MOST VALUABLE enemy below 20% (then the lower health, then the closer); never a Lord or Hero |
| 54 | Trophy Heads (2 keys) | one entry, Lords/Heroes in melee | split: the base key keeps Lords/Heroes in melee; the Daemon Wings key (no such rule in the game data) fires on the closest enemy in melee |
| 25-27, 32-35, 49, 52, 56 | | | unchanged (keep, your earlier rulings, or your word) |
| 55 | Siegebreaker | | unchanged: the game data shows its projectile deals 100 + 100 armour-piercing damage to the unit it hits, so it does harm units in a field battle |
| 28 | Surprise Squig! | | **NOT BUILT.** The proposal called it an explosion at the enemy's feet; the game data shows it SUMMONS Explosive Squigs (`wh3_twa03_def_inf_squig_explosive_0`). It needs a new proposal |

- **A real bug, fixed on the way:** in the two fast-first families, a failed fast arm left the pre-cast re-check in
  "fast" mode, so the fallback cast (fire or melee) was cancelled. The fallback now resets the mode.
- **Defaults:** every moved entry came from a family that does not start armed; nothing changes.
- **Counts:** 938 entries (Trophy Heads split) / 992 keys; 123 families (+3).

## 3. The mistake I made, and how it was caught

The FIRST build of this round followed the doc's FIRST proposals for rows 23-24, 29, 36-41 and 44-45: plain area drain
(needs 75 soldiers), the roots with a melee fallback, Glory Seeker in melee only. Your RULED texts for those rows were
already in the doc, committed with round 177. The same mistake as round 171. It was caught while marking the doc, before
any commit. That build had been installed (md5 `bb0b9fe7ab975f68862c3b4680ca9150`); it is archived as
`archive\packs\zz_test_deadly_onslaught_20261118_round178_firstpass_never_committed.pack`, and its sources are kept in
`docs\backups\round178\first178_*.lua` as a second RED control. If you fought a battle with it, the three rows above
behaved the old way.

## 4. The proof

| Run | Checks | Failures | File |
|---|---:|---:|---|
| FULL, run 1 | 7,476 | 0 | `h177_run1.txt` |
| FULL, run 2 | 7,476 | 0, byte-identical | `h177_run2.txt` |
| RED, pre-178 snapshot | 7,474 | 0; RED 36/36 | `h177_red.txt` |
| RED, the first pass (`H177_RED2=1`) | 7,474 | 0; RED 36/36 | `h177_red2.txt` |

**Section 177 (both files), 17 worlds and the cards:**
- The Soulstealer fires on an idle 120-man block (pre-178: none, it needed melee).
- Chain Lightning: between an 80-man block (value 800) and a 120-man block (value 600) it takes the 80 (both count as
  75, more value per soldier); it fires on a 20-man block alone (FIRST PASS: none, it asked 75); never on 12 men.
- Word of Pain fires on an enemy in melee, and on a shooting Handgunner unit (pre-178: none).
- Net of Amyntok: a fast enemy 25 m away beats one in melee 15 m away; only an enemy in melee: no cast (pre-178 and
  FIRST PASS: one).
- Prey of Anath Raema: the enemy under our fire beats the one in melee.
- Glory Seeker: silent on a Captain merely under fire; fires on a charging Captain (pre-178 and FIRST PASS: none) and
  on one in melee.
- Prey of the Blood God fires on an idle Captain; Void Pendulum on an idle Fire Wizard, never on a Captain.
- Eye of Khorne takes the 400-value unit at 15% over a 50-value remnant at 10%.
- Trophy Heads (Daemon Wings) fires on Swordsmen in melee.
- The cards: Glory Seeker "Fires at a charging enemy, else at one in melee; Lords and Heroes only"; the roots "Fires on
  a fast enemy closing on allies"; Chain Lightning "Fires when standing still, on the enemy unit with the most soldiers,
  16 at least"; Eye of Khorne "Fires on the most valuable enemy below 20% health, not Lords or Heroes".

## 5. Pins rebased (harness 177 vs 176)

| Pin | Old | New | Why |
|---|---|---|---|
| entries (every '937') | 937 | 938 | Trophy Heads split |
| enemy_engaged_or_shot (5 + es) | 37 | 22 | 15 moved |
| enemy_ground_melee (2 + 2 EXP) | 75 | 74 | The Soulstealer moved |
| enemy_melee (3) | 34 | 35 | the Daemon Wings Trophy Heads entry |
| enemy_fast_near_ally (2) | 9 | 15 | the 6 roots |
| target_class lines (3) | 58 | 54 | the 4 spellcaster moves dropped the commander stand-in |
| range_real (2 + EXP) | 417 | 418 | the Daemon Wings entry |
| enemy_blob (2) | 71 | 69 | Chain Lightning x2 |
| enemy_commander_value (3) | 5 | 4 | Dweomer Leach Orb and Slann Gold out, Prey of the Blood God in |
| enemy_melee_or_shooting (1) | 1 | 3 | Whip of Misery, Word of Pain |
| h93 TIP mirror | - | + 3 labels; Eye of Khorne's label | new families |
| h142 0zn, SS1 | The Soulstealer on enemy_ground_melee, 1 cast | enemy_most_models, 0 casts | it needs a visible map now (its firing world is SO1) |
| h137 P2 | Void Pendulum casts on a Lord | 0 casts | spellcasters only now (its firing world is VP1) |

**Builder:** the same counts; the AREA-table gate reads the area drains AND enemy_most_models (the 11 caps); the ROUND
178 gate checks the 3 families, the moves, the split, value-first, fire-first and the 16-model floor.

## 6. Build, install, documents

- **Installed pack:** md5 **`b8622a7b2b6c9bb6ed1c8c5844cac5bf`**, 1,520,627 bytes; `IDENTICAL True`; `MATCHES SOURCE:
  True` four times; the COMPILE gate and the ROUND 123 to 178 gates passed.
- **Archived:** `archive\packs\zz_test_deadly_onslaught_20261118_round178.pack`; `archive\mod_source\round178\` (source
  md5 `7b26435c867f34b57abccd62dd44621a`).
- **Workbook:** `docs\WH3_abilities_master_v61_2026-11-18.xlsx` plus `.ods`; `XLSX v61 VERIFY OK` (22 moved rows, earlier
  notes kept; Trophy Heads rows split; v1-v60 byte-unchanged).
- **Tracker:** 23 rows, section 10.56. **Database, audits (0 candidates on every rule), progress page:** regenerated.

## 7. Not done

- **Not seen in game.** The next battle starts from byte 822,999,135 (the log grew since round 177's 822,669,876).
- Row 28 (Surprise Squig) needs a new proposal. Row 23 of the LAST review and its section 7 (finishers) are still not
  built. Rows 57-114 wait for rulings; rows 115-134 are approved (round 179).
