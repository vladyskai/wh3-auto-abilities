# Round 152: no whole-map hold, no flying large targets, 90 degrees for every central attack (sign-off round)

Date: 2026-11-15. Harness: `harness151.lua`. Release folder: `mod_source\releases\20261115_no_hold_harness151\`.

## 1. The field battle (round 151, High Elves vs Vampire Counts)

Log from byte 618,416,228, archived as `archive\logs\battle_20261115_r151.txt`.

- **"Start armed is working."** The default-armed badges showed **A** from the start (Star Lance, Dragonhorn, Talisman
  of Loec, Book of Hoeth, Colossal Strike, Starwood Staff).
- **The hold silenced the breaths all battle.** The log repeated "HOLD: a large enemy (Zombie Dragon) is worth more
  than the best infantry target (value 15-19)", and no breath was ever cast at the dragon by the mod. The miss the user
  saw must have been a hand-cast breath. The dragon was also fighting the user's own dragon, so it was never safe to
  hit.
- **The ALL badge was created, but off-screen** at offset (-1007, -105): 48 px left of a wheel slot that already sits
  at the screen's left edge.
- **Volley of High Arrows hit Grave Guard three times** (value 152, 193 and 239) through the value rule. The
  90-degree rule only covered the 20 breaths then, so it did not apply to the Volley.

## 2. The rulings (user, 2026-11-15)

| Topic | Ruling |
|---|---|
| Start armed | "Foe-Seeker + tired": Foe-Seeker and Dazh's Song of Winter Sunlight |
| The hold | "let's do not hold for a large unit in the whole map" |
| Large targets | "Large first, skip fliers" |
| 90 degrees | "All 53 central attacks" |
| The ALL badge | below the portrait, right of the camera button (the user's screenshot) |

## 3. The change (what you will see in battle)

- **No whole-map hold:** with no safe, non-flying large enemy in range, a prefer-central attack takes the best infantry
  target as usual.
- **Large first, but never a flying large enemy:** `is_currently_flying()` must read exactly false (an unreadable
  read skips it), on the pick and again just before the cast.
- **90 degrees for all 53 prefer-central attacks**, breaths included: among infantry targets within 20% of the best
  value, the side-on one.
- **Start armed:** the `tired` family joins (28 families, 434 entries).
- **The ALL badge:** offset (-880, 8), docked bottom-centre. It was calibrated from the user's screenshot, using the
  top-slot badge at (-865, -209) and the bottom-right-slot badge at (-799, -37). It may need a small nudge.

## 4. The proof

| Run | Checks | Failures | File |
|---|---:|---:|---|
| FULL, run 1 | 6,446 | 0 | `h151_run1.txt` |
| FULL, run 2 | 6,446 | 0, byte-identical | `h151_run2.txt` |
| LIGHT | 3,265 | 0 | `h151_light.txt` |
| RED, pre-152 snapshot (light) | 3,263 | 0; RED 10/10 | `h151_red.txt` |

Section 151:

| World | Situation | Result |
|---|---|---|
| NH1 | Soporific: the dragon 200 m away, Grave Guard in range | one cast at the Grave Guard |
| FL1 | a FLYING dragon and Grave Guard both in range | the Grave Guard |
| AN1 | Fireball (central, not a breath): a facing block (listed first) and an equal side-on block | the side-on one |
| TI1 | Foe-Seeker, defaults on, no click, Tired | one cast |
| AP1 | the ALL badge | at (-880, 8), dock 8 |

**RED:** on the round-151 source, NH1 is held, FL1 hits the flying dragon, AN1 hits the facing block, TI1 stays
silent, and the ALL badge sits at (-1007, -105).

## 5. Pins rebased

| Pin | Old | New | Why |
|---|---|---|---|
| section 150 world LG2 | no cast (the hold) | one cast at the Grave Guard | the hold is removed by the user's ruling |
| section 150 token 0zw | blob_large_hold | blob_not_flying | the hold function is gone |
| builder round-151 gate | blob_large_hold; 27 default families | blob_not_flying; 28 families | same |

## 6. Build and install

- **The first install attempt failed** with "file in use": the game was running and held the pack open. The installed
  pack stayed at round 151, and the archive rule skipped it (md5 unchanged). After the user closed the game, the same
  builder ran clean.
- **`build_and_install152.py`:** ROUND 123 to 152 gates OK; `MATCHES SOURCE: True` for all five files.
- **Installed pack:** md5 **`0cc4a722865e4b5514e4716c9813b232`**, 1,584,500 bytes, `IDENTICAL True`.
- Archived: `archive\packs\zz_test_deadly_onslaught_20261115_round152.pack`; `archive\mod_source\round152\` (source md5
  `346957d06633df0fff7d854408f6dbf1`, annotated md5 `c03ae3555393bc8d97b95073486dd120`).

## 7. Roster documents

- **Workbook:** `docs\WH3_abilities_master_v40_2026-11-15.xlsx` plus `.ods`; `XLSX v40 VERIFY OK` (structural checks,
  plus no-hold 53 / 53, held text left 0, 90-degree 53 / 53, tired default 5 / 5); v1 to v39 byte-unchanged (74 files).
- **Tracker:** section 10.30. **Database:** the enemy_blob text; `DATABASE VERIFY OK`.
- **Audits:** the wheel audit is OK; R1 to R8 are empty. **Progress:** 68 open.

## 8. Not done

- **Not tested in the game.** The next battle starts at log byte **641,639,500**.
- **Check in the game:** whether the ALL badge sits where the user circled.
