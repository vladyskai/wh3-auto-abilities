# Round 131: the shooting buffs leave the melee trigger; the stances leave the mod (sign-off round)

Date: 2026-11-01. Harness: `harness130.lua`. Release folder:
`mod_source\releases\20261101_shooting_triggers_harness130\`. Survey that led here:
`docs\WH3_remaining_abilities_survey_2026-11-01.md`. Field check of round 130:
`archive\logs\2026-11-01_round130_battle.txt` (4 Restock! casts, each refilled exactly 30%;
Ballistics Calibration cast twice, its repeats refused on cooldown).

## 1. The rulings (user, 2026-11-01)

- **Shooting trigger:** Deranged Munitions, Enchanted Ballistics, Funnel of Flame, Hail of Fire, The
  Guiding Eye, Morgrim's Eye and Locus of Change. Entrenchment as well, "but also, could be used when in
  melee ... because of the physical resistance".
- **The auras:** "Fires when at least 1 ally (caster counts) inside the aura's 70% bound is shooting.
  Actually, the previous trigger where the trigger was required 2 allies should be redone."
- **One-target buffs** (Deranged Munitions base, Entrenchment): "Self, else a shooting ally".
- **Potion of Farsight**, the user's own design: activate only when no enemy is inside the unit's range,
  but at least one would be inside it with the potion. The outer band is range x 1.21 (the 70% rule
  applied to the +30%).
- **Stances:** "For now, all stances should not have any automation. That is a last priority, as the
  stance logic should evaluate all the available mutually exclusive stances to the unit and decide which
  to activate based on the situation." Asked whether to remove the 9 stances now, the user chose "Remove
  all 9 now".

## 2. The change

| Ability | Was | Now | Fires when |
|---|---|---|---|
| Enchanted Ballistics, Funnel of Flame, Hail of Fire, The Guiding Eye, Locus of Change | in melee | `allies_firing_aura` (38 m of 55 m) | the caster, or any unit within 38 m, is shooting past its cast point |
| Morgrim's Eye, Deranged Munitions Upgraded | in melee | `allies_firing_aura` (24 m of 35 m) | the same, within 24 m |
| Ballistics Calibration | 2 allies within 38 m | `allies_firing_aura`, 1 shooter, the caster counts | the same, within 38 m; still cast on the ground at the caster's feet |
| Deranged Munitions | in melee | `self_or_ally_shooting` (NEW, 70 m of 100 m) | the caster shooting: on itself; otherwise on the closest shooting ally |
| Entrenchment | in melee | `melee_or_self_or_ally_shooting` (NEW, 105 m of 150 m) | in melee: on itself; otherwise as Deranged Munitions. The target cannot move for 44 s |
| Potion of Farsight | in melee | `no_enemy_in_range_within_boost` (NEW) | not in melee, has ammunition, no enemy inside its missile range, nearest enemy within range x 1.21 |

Notes on the change:

- **"Shooting"** is the firing flag past the cast point (first shot + half the unit's reload), the same
  rule as round 130's triggers.
- **Ally picks** are checked again just before the cast (still alive, in range and shooting).
- **The Farsight band** is `FOURTH.FARSIGHT_BAND = 1 + 0.30 x RANGE_FRACTION`. The distance is the same
  edge-to-edge measure the firing flag's in-range read uses.
- **Removed (9 stances):** Master Predator, Immovable Bulwark, Unstoppable Choppas, The Shadow's Coil,
  Woven Mist, Chanson of Caging, The Dance of Dreaming, The Praise of Slaanesh, The Waltz of Lethargy.
  Their entries and their 5 wind-up rows are gone, so their badges no longer appear.
- **Kept:** Thunderburner also has no fixed duration, but it is a speed burst, not a stance.

## 3. The proof

| Run | Checks | Failures | File |
|---|---:|---:|---|
| harness129 on the new source (before the rebase) | 5,577 | 125, every one a pin listed in section 4 | (not kept) |
| FULL, run 1 | 5,638 | 0 | `h130_run1.txt` |
| FULL, run 2 | 5,638 | 0, byte-identical | `h130_run2.txt` |
| LIGHT | 2,457 | 0 | `h130_light.txt` |
| RED, pre-131 snapshot (light) | 2,413 | 0; the RED checks reproduce "only in melee" | `h130_red.txt` |

Section 130 (61 checks, live and annotated, 24 worlds):

- **Hail of Fire:**
  - T1: the caster shooting alone casts on its cast point (poll 28).
  - T2: a shooting ally 30 m away triggers it.
  - T3: a shooting ally 45 m away does not.
- **Deranged Munitions:**
  - D1: the caster shooting casts on itself.
  - D2: allies at 50 m and 20 m both shooting; the 20 m one gets it.
  - D3: an ally 80 m away does not.
- **Entrenchment:**
  - E1: cast in melee.
  - E2: cast on a shooting ally 100 m away.
- **Potion of Farsight:**
  - F1: nearest enemy at 170 m with a 150 m range: cast.
  - F2: one enemy at 140 m is already in range: no cast.
  - F3: nearest enemy at 190 m: no cast.
  - F4: in melee: no cast.
- **0zb:** no stance name is left anywhere in either file.

**RED** (round-130 build): T2, D2 and F1 cast nothing, and E1 still casts (8/8).

**Harness correction during the round:** my world total was 26; the section has 24 worlds.

## 4. Pins rebased (old -> new, why)

| Pin | Old | New | Why |
|---|---:|---:|---|
| ABILITIES entries | 709 | 700 | 9 stances removed |
| ability keys | 761 | 752 | the same |
| `melee_unwavering` | 373 | 354 | 10 moved, 9 stances removed |
| `ally_range_real` fields | 42 | 44 | Deranged Munitions 100 m, Entrenchment 150 m |
| wind-up keys | 170 | 165 | the 5 stance keys with a wind-up row |
| full-table iterations | 1,418 | 1,400 | 2 x 700 |
| harness-104 0p dance markers | present | absent | the two Slaanesh dances are stances |
| harness-129 0y | `BALLISTICS_MIN_FIRING = 2` | `FIRING_AURA_MIN = 1` | the user's aura ruling |
| harness-129 B1b reason text | "2 allies ... (need 2)" | "2 unit(s) ... (2 allies + the caster not shooting; need 1)" | the same |
| harness-129 B2a | no cast | casts | one shooter within 38 m is enough now |
| tooltip mirror | 49 wordings | 52, `allies_firing_aura` reworded | the new triggers |

Builder gates rebased:

- the entry count (11 gates, 709 -> 700);
- `melee_unwavering` (4 gates, 373 -> 354);
- `ally_range_real` (1 gate, 42 -> 44);
- the roster lists drop the 9 stance rows: BLOCK789 66 -> 62 entries and 70 -> 66 keys, AUTO327 305
  -> 302 and 320 -> 317, FINAL6 6 -> 4.

## 5. Build and install

`build_and_install131.py` adds the round-131 gate. Results:

- `ARMY-BAR GATE OK` (752 keys).
- `RELOAD TABLE MATCHES the game data`.
- ROUND 123 to 131 gates OK.
- `MATCHES SOURCE: True` for all five files.
- Installed pack md5 **`b7efc16df23c1a00f71eb7880dc244ca`**, 1,173,792 bytes, `IDENTICAL True`.
- Both new log reasons are in the installed pack.

Archived: `archive\packs\zz_test_deadly_onslaught_20261101_round131.pack` and
`archive\mod_source\round131\` (source md5 `7bb9b349f57b51cdd277fc87700f8fbc`, annotated md5
`67369889c5f1b9a0037baa0823ead3c1`). Pre-round snapshots: `docs\backups\round131\`.

## 6. Roster documents

- **Tracker:** 20 rows updated, plus section 10.12.
- **Database:** regenerated, `DATABASE VERIFY OK` (752 keys).
- **Workbook:** `docs\WH3_abilities_master_v23_2026-11-01.xlsx` plus `.ods`, checked by
  `XLSX v23 VERIFY OK`.
  - Rows: 1,800 = 1,123 + 677; 752 implemented; 371 not implemented (22 skipped by user decision).
  - Families: 52, with 700 entries and 752 keys.
  - Older versions: v1 to v22 byte-unchanged (40 files).
- **Wheel audit:** `WHEEL-STATUS AUDIT OK`.

## 7. Not done

- **Not field-tested.**
- **The mock engine accepts repeat casts,** so only a battle shows the one-cast-per-recharge behaviour.
- **Next, by the user's plan:** after this battle test, propose triggers for Embers of the Phoenix, Horn
  of Vaul and the 8 Enchanted Metallurgy / Master of Alchemy keys (melee and missile buffs on a melee
  trigger). Then the next survey group.
