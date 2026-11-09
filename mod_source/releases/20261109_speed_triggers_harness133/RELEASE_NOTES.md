# Round 134: audit batch 3, the speed buffs (sign-off round)

Date: 2026-11-09. Harness: `harness133.lua`. Release folder:
`mod_source\releases\20261109_speed_triggers_harness133\`. Audit group R7 of
`docs\WH3_trigger_audit_2026-11-08.md`.

## 1. The rulings (user, 2026-11-09, all three as recommended)

- **Speed and charge buffs with no melee stat, "Charge only":**
  - Apocalyptic Charge (charge speed +10%, charge bonus +20%, aura);
  - Twilight Horn I (charge speed and speed +25%, charge bonus +20%, aura);
  - Potion of Speed (charge speed and speed +25%, 1 use);
  - Blooood! (Hellcannon speed +25%).
- **Speed plus a melee stat, "Charge, else in melee":**
  - Book of Arkhan (+24 melee attack, aura);
  - Rune of Speed and Master Rune of Speed (speed +45%, +24 melee attack, aura);
  - Lightning Reflexes (+20 damage resistance);
  - Master of the Skies (+40 melee defence);
  - Pendant of Slaanesh (+40 melee attack);
  - Slippery (+24 melee defence);
  - Transfix (+20 damage resistance).
- **Thunderburner and Thunderburner Upgraded, "Stop automating":** speed x2.5 / x3 with turning cut to 30%.
  The game data gives no end time (-1), so it is a movement mode the player switches.
- **Earlier decisions:** the 2026-10 questionnaire put each one on "in melee"; no later ruling.

## 2. The change

| Family (existing) | Abilities | Fires when | Cast |
|---|---|---|---|
| `charge_only` (1 -> 5) | the 4 charge buffs | the charge window only | the caster |
| `charge_or_melee` (28 -> 36) | the 8 speed + melee-stat buffs | the charge window, else in melee | the caster |
| removed | Thunderburner, Thunderburner Upgraded | never (no letter) | - |

**The charge window** is the existing detector, the one Ferocious Battle Howl and Fangspike already use:
- the unit is running (`is_moving_fast()`) and is not in melee;
- it has an attack target 12 to 60 m away;
- impact is 4 s away or less.

There is no new code. The script `tools\round134_speed_triggers.py` changed the 12 trigger names and deleted the two
Thunderburner entries and their two wind-up rows, in both the source and the annotated copy.

**What this means in battle.**
- The charge-only four fire as the unit charges in and never in melee. A charge the detector misses means no cast;
  ordering an attack from 12 to 60 m away is what makes it fire.
- The other eight fire on the charge when one is seen. Otherwise they fire once the unit is in melee, as before.
- Thunderburner has no badge letter any more.

## 3. The proof

| Run | Checks | Failures | File |
|---|---:|---:|---|
| harness132 on the new source (before the rebase) | 5,738 | 116, all count pins plus the harness-85 S3 reason count | (not kept) |
| FULL, run 1 | 5,785 | 0 | `h133_run1.txt` |
| FULL, run 2 | 5,785 | 0, byte-identical | `h133_run2.txt` |
| LIGHT | 2,604 | 0 | `h133_light.txt` |
| RED, pre-134 snapshot (light) | 2,578 | 0; RED 10/10 | `h133_red.txt` |

Section 133 (47 checks, 20 worlds):

- **Apocalyptic Charge:**
  - C1: charging, it casts with the charge-only reason.
  - C2: in melee, it does not cast.
- **Potion of Speed:** C3: charging, it casts.
- **Blooood!:** C4: in melee, it does not cast.
- **Twilight Horn I:** C5: charging, it casts.
- **Pendant of Slaanesh:**
  - G1: charging, it casts.
  - G2: in melee, it casts with the charge-or-melee reason.
- **Rune of Speed:** G3: charging, it casts.
- **Transfix:** G4: in melee, it casts.
- **Book of Arkhan:** G5: walking (not running) toward a target 20 m away, it does not cast.
- **Tokens:** Thunderburner is absent from both files, and the counts are 328 / 5 / 36 / 698.

**RED** (round-133 build):
- C1, C3 and G1 (charging) cast nothing.
- C2 and G2 (melee) cast. This is the old melee-only behaviour.

## 4. Pins rebased (old -> new, why)

| Pin | Old | New | Why |
|---|---:|---:|---|
| entries | 700 | 698 | Thunderburner x2 removed |
| keys | 752 | 750 | the same |
| `melee_unwavering` | 342 | 328 | 12 moved, 2 removed |
| `charge_or_melee` | 28 | 36 | +8 |
| `charge_only` | 1 | 5 | +4 |
| wind-up keys | 164 | 162 | the two Thunderburner rows |
| full-table iterations | 1,400 | 1,396 | 2 x 698 |
| harness-85 S3c reason count | 35 | 32 + 3 | Lightning Reflexes, Master of the Skies and Pendant of Slaanesh now give the charge-or-melee in-melee reason |

69 code lines in all, listed by `tools\make_harness133.py`. The builder (`tools\make_builder134.py`):
- the entries, `melee_unwavering`, `charge_or_melee` and `charge_only` gates rebased the same way;
- the AUTO327 list 302 -> 300 entries / 317 -> 315 keys;
- one new gate: `ROUND 134 GATE OK`.

## 5. Build and install

- **`build_and_install134.py`:**
  - ARMY-BAR GATE OK and the reload table matches;
  - ROUND 123 to 134 gates OK;
  - `MATCHES SOURCE: True` for all five files.
- **Installed pack:**
  - md5 **`ecc56210716b57f8d5ab53dc442c263c`**, 1,181,512 bytes, `IDENTICAL True`;
  - "thunderburner" appears 0 times in the installed pack;
  - the new Blooood! line is present.

Archived:
- `archive\packs\zz_test_deadly_onslaught_20261109_round134.pack`;
- `archive\mod_source\round134\` (source md5 `757b2cc330537229c06d764034ec9af8`, annotated md5
  `87d01711b2c322883ee01d019767a42e`).

## 6. Roster documents

- **Tracker:** 14 rows updated, plus section 10.15.
- **Database:** `DATABASE VERIFY OK`.
- **Workbook:** `docs\WH3_abilities_master_v26_2026-11-09.xlsx` plus `.ods`.
  - Checked by `XLSX v26 VERIFY OK`.
  - Counts: 750 implemented, 373 not implemented, 24 skipped.
  - v1 to v25 are byte-unchanged (46 files).
- **Wheel audit:** OK.
- **Progress page:** rebuilt. 750 automated, 263 seen firing.
- **Trigger audit:** re-run, `docs\WH3_trigger_audit_2026-11-09.md`. R7 is empty; 67 candidates remain (R3 23, R4 19, R6 25).

## 7. Not done

- **Not tested in the game.**
  - The charge-only four depend on the charge detector seeing the charge.
  - The under-fire triggers of round 133 also still need their first battle.
- **The QA army list** is not written yet.
- **Next audit batches:**
  - R4 (enemy slows, 19);
  - R3 (melee debuffs with a missile arm, 23);
  - R6 (morale, 25).
