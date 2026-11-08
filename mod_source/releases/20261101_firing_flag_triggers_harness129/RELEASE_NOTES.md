# Round 130: the first triggers on the firing flag (sign-off round)

Date: 2026-11-01 (the system clock and the file times say 2026-11-01; rounds 126 to 129 were written
as 2026-11-03, which looks like a wrong date in those documents). Harness: `harness129.lua`. Release
folder: `mod_source\releases\20261101_firing_flag_triggers_harness129\`. Field check that led here:
`docs\WH3_round129_field_check.md`.

## 1. The rulings (user, 2026-11-01)

- "Please implement the both recommended options." That is Restock! option A and Ballistics
  Calibration option A.
- Skjalandir's Fall, asked which shooting trigger: "Shooting into melee". Its melee trigger stays.
- Standing rule from the same message: do not argue from how often a unit acted in one battle. The
  user's orders set those conditions (Ulrika was ordered into melee on purpose).
- Earlier decisions: Restock! and Ballistics Calibration were on the deferred next-batch list
  (2026-11-01); neither was rejected or skipped. Skjalandir's Fall's ranged half was deferred in round
  124 until the ammo probe had field data.

## 2. The change

| Ability | Owners in the user's army | New trigger | Fires when | Cast |
|---|---|---|---|---|
| Restock! | Jorek Grimm, Engineer, Master Engineer | `ally_ammo_low` | an ally within 70 m (70% of 100 m) is shooting and has 70% or less of its ammunition left; the one with the least left | on that ally |
| Ballistics Calibration | Jorek Grimm | `allies_firing_aura` | at least 2 allies within 38 m (70% of the 55 m aura) are shooting past their cast point | on the ground at the caster's own feet |
| Skjalandir's Fall | Ulrika | `melee_or_shooting_into_melee` | in melee (as before), OR shooting past her cast point at an enemy that is in melee | on herself |

The details, in plain words:

- **"Shooting"** is the firing flag from round 126: the unit's `ammo_left()` dropped between two polls.
  The probe now also files each unit's state by its ui id (`FOURTH.ammo_by_id`), so a trigger can look
  up any unit on the same poll.
- **The cast point** is first shot + half the unit's reload (the generated reload table).
- **Restock!:**
  - 70% is 100% minus the 30% the ability refills, so a refill is never wasted
    (`FOURTH.RESTOCK_AT_FRACTION = 0.70`).
  - A unit that was just refilled is skipped by every caster for 12 s (the ability's 10 s active time
    plus 2 s, `FOURTH.RESTOCK_CLAIM_S`), so two Engineers never refill the same unit twice.
  - Each caster is held 60 s after a cast (4 uses, 60 s recharge: the charge gate).
  - Right before the cast, the mod checks again that the ally is still alive, in range, shooting and
    still at 70% or less. If not, the cast is skipped.
- **Ballistics Calibration** is cast at Jorek's own position, so it never gives him a move order. It
  counts only other units, not Jorek himself (`FOURTH.BALLISTICS_MIN_FIRING = 2`).
- **The CAST POINT log line** now ends with "(the firing-flag triggers may cast from here)" instead of
  "(nothing is cast in this round)".

## 3. The proof

| Run | Checks | Failures | File |
|---|---:|---:|---|
| harness128 on the new source (before the pin rebase) | 5,528 | 119, every one a count or text pin listed in section 4 | (not kept) |
| FULL, run 1 | 5,577 | 0 | `h129_run1.txt` |
| FULL, run 2 | 5,577 | 0, byte-identical | `h129_run2.txt` |
| LIGHT | 2,396 | 0 | `h129_light.txt` |
| RED, pre-130 snapshot (light) | 2,364 | 0; the RED checks reproduce "never casts" | `h129_red.txt` |

Section 129 (49 checks, live and annotated):

- **R1:** two shooting allies, one at 60% (50 m) and one at 80% (30 m). ONE Restock!, on the 60% ally,
  not on the closer one.
- **R2:** an ally at 60% that is not shooting, and a shooting ally at 60% at 80 m. No cast.
- **R3:** two casters and one ally at 50%. Exactly one cast in 10 s.
- **B1:** two allies within 38 m. ONE ground cast, at Jorek's own position, on poll 28 exactly. That is
  first shot (poll 2) + 6.5 s (26 polls), the handgunners' cast point.
- **B2:** one ally at 30 m and one at 45 m. No cast.
- **S1:** Ulrika shooting at a target in melee. ONE self cast, on her cast point (poll 16).
- **S2:** shooting at a target not in melee. No cast.
- **S3:** in melee, not shooting. ONE cast (the melee arm stays).

**RED** (round-129 build): R1, B1 and S1 cast nothing; S3 still casts (8/8).

**Harness corrections during the round** (harness-side only):

- B1 and S1 first expected the first shot on poll 3. It is read on poll 2, so the expected cast tick
  was one poll late.
- The mock engine never refuses a repeat cast on cooldown, so those two worlds now stop just after the
  cast point.
- A comment of mine said "alive and not routing", which moved a text-count pin from 8 to 9. I reworded
  the comment; the pin stays at 8.

## 4. Pins rebased (old value -> new value, why)

| Pin | Old | New | Why |
|---|---:|---:|---|
| ABILITIES entries | 707 | 709 | Restock!, Ballistics Calibration |
| ability keys | 759 | 761 | the same two keys |
| `melee_unwavering` entries | 374 | 373 | Skjalandir's Fall moved to its own trigger |
| `ally_range_real` fields | 41 | 42 | Restock! (100 m) |
| charge-gate keys | 163 | 164 | Restock! (60 s) |
| full-table iterations | 1,414 | 1,418 | 2 x 709 |
| harness-93 tooltip mirror | 46 wordings | 49 | the three new tooltip lines |
| harness-125 CAST POINT text | "(nothing is cast in this round)" | "(the firing-flag triggers may cast from here)" | the text was no longer true |

64 harness lines were rebased (listed by `tools\make_harness129.py` when it runs). In the builder, 16
gates were rebased: 11 entry counts, 4 `melee_unwavering` counts and 1 `ally_range_real` count.

## 5. Build and install

`build_and_install130.py` adds the round-130 gate. Results:

- `ARMY-BAR GATE OK` (761 keys, none in army_spec), `RELOAD TABLE MATCHES the game data`, ROUND 123 to
  130 gates OK, and `MATCHES SOURCE: True` for all five files.
- Installed pack md5 **`0e786a41ce6a2a6f566f3b6c9b5172cd`**, 1,170,079 bytes, `IDENTICAL True`.
- Both new log reasons are in the installed pack (grep count 1 each).

Archived: `archive\packs\zz_test_deadly_onslaught_20261101_round130.pack` and
`archive\mod_source\round130\` (source md5 `04d0699c2305239b0dc210ea88f8a365`, annotated md5
`c2f3cb73b85e0658217346ccd568b84d`). Pre-round snapshots (source, annotated, tracker, database,
database builder, workbook hashes): `docs\backups\round130\`. The round-129 battle log:
`archive\logs\2026-11-01_round129_battle.txt`.

## 6. Roster documents (same round)

- **Tracker:** 3 rows updated, plus section 10.11.
- **Database:** regenerated, `DATABASE VERIFY OK` (761 mod keys, each with an implemented line), with
  three new family texts in `tools\build_ability_database.py`.
- **Workbook:** `docs\WH3_abilities_master_v22_2026-11-01.xlsx` plus `.ods`, built by
  `tools\make_xlsx_v22.py`. `tools\verify_xlsx_v22.py` re-opens it from disk: `XLSX v22 VERIFY OK`.
  - Rows: 1,800 rows (same as v21) = 1,123 + 677; 761 implemented rows and keys; 362 not implemented.
  - Families: 49, with 709 entries and 761 keys.
  - Older versions: v1 to v21 are byte-unchanged (38 files hashed before the build).
- **Wheel audit:** `WHEEL-STATUS AUDIT OK`.

## 7. Not done

- **Not field-tested.**
- **Same-battle limit:** the harness's mock engine accepts every repeat cast, so it cannot show the real
  game's cooldown refusal. Only a battle shows that Restock! and Ballistics Calibration cast once per
  recharge.
- **Not built:** the other Restock-type keys (More Powder! `wh2_dlc11_hero_abilities_more_powder`,
  Restock! `wh3_dlc25_abilities_restock_gunnery_school`). They have the same effect but were not part
  of the ruling.
- **Next step (the user's plan):** casting before the first shot, if this works in battle.
