# Round 142: open batch 1 (shooting buffs and ammo refills) and Blooood! when moving (sign-off round)

Date: 2026-11-13. Harness: `harness141.lua`. Release folder: `mod_source\releases\20261113_open_batch1_harness141\`.

## 1. The two QA battles fought during round 141 (the log cut from byte 491,273,109)

Both ran the round-141 build (the pack was installed at 20:42).

- **Tomb Kings with Arkhan:**
  - Staff of Nagash fired at 98 s, two seconds after Tomb Blade, with the reason "1 of the caster's abilities
    recharging".
  - It fired again at 228 s, after Tomb Blade (203 s) and Liber Mortis (206 s), with "2 recharging". It no longer
    fires on simply entering melee.
  - Restore: accepted at 214 s, refused "on cooldown" at 274 s, accepted at 292 s (a real lock of about 78 s against
    the table's 84 s; the one early attempt is harmless).
- **Warriors of Chaos with the Hellcannon:**
  - Boom! cast once while shooting (85.5 s), never while moving.
  - **Blooood! never fired:** all 116 readings of `is_moving_fast()` were false. A Hellcannon never runs; it only walks
    (`moving=yes`). The user: *"I realized Hellcannon cannot run, so we need to change trigger for Blooood!"*

## 2. The rulings (user, 2026-11-13)

**Earlier status of the batch:** auto-exclusions from before the firing flag and the ground form existed, not user
decisions.

| Ability | Effect (game data) | Ruling | Family |
|---|---|---|---|
| More Powder! (Gunnery Wight) | 30% ammo to one friendly unit, 4 uses, 60 s | Same as Restock! | `ally_ammo_low` |
| Restock! (gunnery school) | 30% ammo, 2 uses, 60 s | Same as Restock! | `ally_ammo_low` |
| Master of Mists (Aislinn, 2 keys) | 35 m ground area up to 250 m: missile damage +25%, range +50%, reload +20 | Before range (Farsight-like) | `ground_ally_before_range` (NEW) |
| Of Warp and Ruin (Warp-Doom cannon) | explosive damage +40%, blast +20%, reload +30; can hit friends | Shooting, not into melee | `self_shooting_clear` (NEW) |
| Ominous Powder | missile damage +40/+80%, reload; 26 damage to its carrier | Shooting, health above 50% | `self_shooting_healthy` (NEW) |
| Blooood! | speed +25%, acceleration +18% | When moving | `self_moving` (NEW) |

## 3. The change

- **5 new entries / 6 keys.** The two refills use `ally_range_real = 100` (70 m). Master of Mists uses
  `ally_range_real = 250`: the new `FOURTH.ALLY_CAST_R250 = 175` and its `[250]` map entry, with the build asserting
  floor(250 x 0.70) = 175.
- **Charge holds:** More Powder! 60 s, gunnery-school Restock! 60 s, Master of Mists 120 s (both keys).
- **Master of Mists is a ground key.**
- **`ground_ally_before_range`:**
  - It checks the caster first, then every ally within 175 m, for `FOURTH.before_range(u, MIST_BAND)`: out of melee,
    ammunition left, no enemy inside its own `missile_range()`, and the nearest enemy inside range x 1.35
    (1 + 0.50 x 0.70).
  - The closest qualifying unit wins.
  - The cast goes on the ground under it, through the Star of Avelorn ground path (`ah_ground`).
  - That path's pre-cast re-check now re-checks this condition (`ah_mode = "mist"`) instead of health.
- **`self_shooting_clear`:** shooting past the cast point AND `current_target()` readable and not in melee.
- **`self_shooting_healthy`:** shooting past the cast point AND health readable and above 50%.
- **`self_moving`:** `is_moving()` exactly true. `self_running` keeps its evaluator with no entry.
- **The lock table** (round 141) was re-derived to include the new keys: 618 -> 624.

## 4. The proof

| Run | Checks | Failures | File |
|---|---:|---:|---|
| harness140 on the new source (before the rebase) | 6,088 | 91: entry/key count pins, the multi-use and ally-range counts, the round-140 Blooood! token, the tooltip mirror | (not kept) |
| FULL, run 1 | 6,135 | 0 | `h141_run1.txt` |
| FULL, run 2 | 6,135 | 0, byte-identical | `h141_run2.txt` |
| LIGHT | 2,954 | 0 | `h141_light.txt` |
| RED, pre-142 snapshot (light) | 2,928 | 0; RED 10/10 | `h141_red.txt` |

Section 141 (22 worlds):
- **More Powder!:**
  - MP1: Handgunners at 60% ammunition: one cast on them.
  - MP2: at 90%: no cast.
- **Restock! (gunnery school):** RG1: at 60%: one cast on them.
- **Master of Mists:**
  - MM1: nearest enemy 190 m, range 150 m: one ground cast under the Handgunners.
  - MM2: enemy at 140 m (in range): no cast.
  - MM3: enemy at 220 m: no cast.
- **Of Warp and Ruin:**
  - WR1: target not in melee: a cast.
  - WR2: target in melee: no cast.
- **Ominous Powder:**
  - OP1: at 80% health: a cast.
  - OP2: at 40%: no cast.
- **Blooood!:** BL1: the Hellcannon walking: one cast.

**RED:** on the round-141 build, MP1, MM1, WR1, OP1 and BL1 cast nothing.

## 5. Pins rebased

| Pin | Old | New |
|---|---:|---:|
| entries (harness; builder 11 gates) | 698 | 703 |
| keys | 750 | 756 |
| full-table iterations | 1,396 | 1,406 |
| multi-use charge-gate keys | 165 | 169 |
| `ally_range_real` fields (harness; builder) | 53 | 56 |
| the round-140 Blooood! token (harness; builder) | self_running | self_moving |
| tooltip mirror | - | + 4 wordings |

## 6. Build and install

- **The first build attempt was refused** at the old `ally_range_real == 53` gate. Thanks to the 2026-11-09 order fix,
  the installed pack stayed untouched (still round 141's `2eafed98`).
- **My own mistake:** my command still copied that unchanged pack into the archive under the round-142 name. The copy
  was compared byte for byte with the round-141 archive and deleted. The command now archives only when the installed
  md5 changed and the new marker is in the pack.
- **`build_and_install142.py`:** ROUND 123 to 142 gates OK; `MATCHES SOURCE: True` for all five files.
- **Installed pack:** md5 **`d4b0ebaef4476414ecea798c9b599a32`**, 1,398,164 bytes, `IDENTICAL True`.

Archived:
- `archive\packs\zz_test_deadly_onslaught_20261113_round142.pack`;
- `archive\mod_source\round142\` (source md5 `8c5b3c055b94310657727a5219c3578e`, annotated md5
  `c77ca974aad4ed1b6f9acfc4256221ee`).

## 7. Roster documents

- **Tracker:** 7 rows updated, plus section 10.24.
- **Database:** 4 family texts; `DATABASE VERIFY OK`.
- **Workbook:** `docs\WH3_abilities_master_v34_2026-11-13.xlsx` plus `.ods`.
  - Checked by `XLSX v34 VERIFY OK`.
  - 756 implemented, 367 not implemented, 67 families.
  - v1 to v33 are byte-unchanged (62 files).
- **Wheel audit:** OK.
- **Progress page:** 169 still open.
- **Trigger audit:** the three new shooting families were added to its shooting list, so R1 is empty again.

## 8. Not done

- **Not tested in the game.**
- **The next open batch:** group C, the out-of-date exclusions (24), including 7 ground-target curses and spells.
  Then group B, attacks cast at an enemy (112).
