# Round 143: open batch 2 (ground curses, Curse of Djaf, Soulblight, the fanatic releases) (sign-off round)

Date: 2026-11-13. Harness: `harness142.lua`. Release folder: `mod_source\releases\20261113_open_batch2_harness142\`.

## 1. The rulings (user, 2026-11-13)

**Earlier status of the batch:** out-of-date auto-exclusions (from before the enemy-ground form and the enemy
ammunition read existed), not user decisions. The 2026-10 questionnaire had only proposed "when in melee: on the
ground under its target" for the curses.

| Ability | Kind | Ruling | Family | Bound |
|---|---|---|---|---|
| The Curse of Anraheir (3 keys) | ground-target curse | Fighting enemy, all four | `enemy_ground_melee` | 140 m (of 200 m) |
| Transmutation of Lead | ground-target curse | Fighting enemy, all four | `enemy_ground_melee` | 140 m (of 200 m) |
| Soulblight (Doomfire Warlocks) | ground-target curse | Fighting enemy, all four | `enemy_ground_melee` | 140 m (of 200 m) |
| The Soulstealer | ground-target spell | Fighting enemy, all four | `enemy_ground_melee` | 70 m (of 100 m) |
| Curse of Djaf | ground-target curse | Shooting enemy | `enemy_ground_shooting` (NEW) | 70 m (of 100 m) |
| Soulblight (Lahmian Handmaidens) | self contact buff | In melee | `melee_unwavering` | self |
| Squig Thinkin' | summon on the ground | Fighting enemy, all three | `enemy_ground_melee` | 52 m (of 75 m) |
| Spinning Loons | fanatic release | Fighting enemy, all three | `enemy_ground_melee`, not flying | 17 m (of 25 m) |
| The Loons of Eight Peaks | fanatic release | Fighting enemy, all three | `enemy_ground_melee`, not flying | 17 m (of 25 m) |

## 2. The change (what you will see in battle)

- **9 new entries / 11 keys**, each with its own badge (`M` until you click it to `A`).
- **The seven "fighting enemy" abilities:** when armed, they wait until an enemy inside the bound is in melee, then
  place the spell or the summon on the ground under the CLOSEST such enemy. They never fire at an enemy that is just
  walking past.
- **Curse of Djaf:** when armed, it waits for an enemy missile unit that is shooting (its ammunition is dropping), is
  not in melee and is within 70 m, and places the curse on the ground under it. It reuses Missile Mirror's enemy
  ammunition read (round 138); its one new piece is "on the ground under it" instead of "on the unit".
- **Soulblight (Handmaidens):** fires on the unit itself when it is in melee and not wavering.
- **The two fanatic releases:** the game says they cannot target a flying unit, so they carry `target_class =
  "not_flying"` (a flying or unreadable enemy is skipped). Their 25 m reach needed a new bound:
  `FOURTH.ENEMY_CAST_R25 = 17` (floor(25 x 0.70)) and its `[25]` map entry; the build asserts the arithmetic.
- **Tables:**
  - the 10 ground-target keys joined `enemy_ground_keys` (the Handmaidens' Soulblight is a self buff and is NOT in it;
    the build checks that);
  - wind-ups: Transmutation of Lead 5 s, Soulblight (Doomfire) 3 s, The Soulstealer 3 s, Soulblight (Handmaidens) 1 s;
  - charge holds for the multi-use keys: Soulblight (Doomfire) 90 s, Soulblight (Handmaidens) 45 s, the two fanatic
    releases 30 s each;
  - the round-141 lock table was re-derived from the game data: 624 -> 628 keys.

## 3. The proof

| Run | Checks | Failures | File |
|---|---:|---:|---|
| harness141 on the new source (before the rebase) | - | 135: entry/key counts and the trigger-count pins they cascade into | (not kept) |
| FULL, run 1 | 6,194 | 0 | `h142_run1.txt` |
| FULL, run 2 | 6,194 | 0, byte-identical | `h142_run2.txt` |
| LIGHT | 3,013 | 0 | `h142_light.txt` |
| RED, pre-143 snapshot (light) | 2,971 | 0; RED 8/8 | `h142_red.txt` |

Section 142 (14 worlds, run on both files = 28):
- **AN1:** an enemy in melee 30 m away: one ground cast under it. **AN2:** the enemy is not fighting: no cast.
- **TL1, SB1, SS1, SQ1:** an enemy in melee inside each bound: one ground cast under it.
- **DJ1:** enemy Handgunners shooting 30 m away, not in melee: one ground cast under them. **DJ2:** a fighting enemy
  that is not a missile unit: no cast.
- **HM1:** the Handmaidens in melee: one cast on themselves. **HM2:** not in melee: no cast.
- **LO1:** an enemy in melee 10 m away (bound 17 m): one ground cast. **LO2:** 25 m away: no cast. **LO3:** the enemy
  is flying: no cast. **LE1:** The Loons of Eight Peaks, like LO1.

**RED:** on the round-142 build, AN1, DJ1, HM1 and LO1 cast nothing (the entries do not exist there).

## 4. Pins rebased

| Pin | Old | New |
|---|---:|---:|
| entries (harness; builder 11 gates) | 703 | 712 |
| keys | 756 | 767 |
| full-table iterations | 1,406 | 1,424 |
| `melee_unwavering` (harness; builder 4 gates) | 306 | 307 |
| `enemy_ground_melee` (harness; builder) | 67 | 74 |
| `range_real` fields (harness; builder 2 gates) | 207 | 215 |
| target classes (harness; builder) | 21 | 24 |
| wind-up keys (harness 0a) | 162 | 166 |
| `enemy_ground_keys` entries (builder) | 115 | 125 |
| tooltip mirror | - | + 1 wording |

One rule in `make_harness142.py` also moved a pin labelled `(RED_MODE and 0 or 169)` to 173 (the multi-use charge-gate
count: 4 new multi-use keys). It passes on the new source.

## 5. Build and install

- **`build_and_install143.py`:** ROUND 123 to 143 gates OK; `MATCHES SOURCE: True` for all five files.
- **Installed pack:** md5 **`c2168f7908cb3e2403d7dbfbd94c017e`**, 1,402,523 bytes, `IDENTICAL True`; the new
  evaluator name is in the installed pack.

Archived (only after the md5 changed and the marker was found):
- `archive\packs\zz_test_deadly_onslaught_20261113_round143.pack`;
- `archive\mod_source\round143\` (source md5 `76165a50b3425a6a7bcd295cb942ddb8`, annotated md5
  `79e4a52d675ee99460e173a2b0923fd8`).

## 6. Roster documents

- **Tracker:** 11 rows updated, plus section 10.25.
- **Database:** 1 family text (`enemy_ground_shooting`); `DATABASE VERIFY OK`.
- **Workbook:** `docs\WH3_abilities_master_v35_2026-11-13.xlsx` plus `.ods`.
  - Checked by `XLSX v35 VERIFY OK`.
  - 767 implemented, 356 not implemented, 68 families.
  - v1 to v34 are byte-unchanged (64 files).
- **Wheel audit:** OK.
- **Trigger audit:** R1 to R8 all empty.
- **Progress page:** 158 still open.

## 7. Not done

- **Not tested in the game.**
- **The next open batch:** the rest of group C (the "no effect text" ones), then group B, attacks cast at an enemy.
