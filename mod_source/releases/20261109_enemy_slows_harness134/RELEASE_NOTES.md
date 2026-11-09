# Round 135: audit batch 4, the enemy slows and the target filters (sign-off round)

Date: 2026-11-09. Harness: `harness134.lua`. Release folder:
`mod_source\releases\20261109_enemy_slows_harness134\`. Audit group R4 of
`docs\WH3_trigger_audit_2026-11-09.md`.

## 1. The rulings (user, 2026-11-09)

- **Slow plus a melee-stat cut (11), "Enemy in melee":** Acquiescence, El Syf, Frost Shard Glaive, Hidden Huntress
  (both keys), Hornswaggle, Marked for Eatin', Taunt, Titan Headsman, You're Next!, Tendrils of the Sea.
- **Pure slows (Mither, Rune of Slowness, Master Rune of Slowness, Whispering Mist), the user's own design:**
  *"Enemy moving close to an ally that has at least cavalry speed. The idea would be to automatically slow down
  any fast enemy with mass that is a threat. No need to detect if the enemy charges or not. But it should be
  useful, so the enemy cannot be far from the ally units."* Settings asked afterwards: **5 m/s or more**, within
  **40 m** of one of our units.
- **Looming Dread, Book of Secrets, Fecund Rebirth:** *"Keep as is, but make sure the trigger filters for the enemy
  unit type."*
- **Hunter of Champions:** the round-123 ruling kept (*"Hunter of champions is okay for enemy_engaged_or_shot"*).
- **Target filters:** *"Yes, all 15 now."*
- **Earlier decisions:** questionnaire approvals only; nothing rejected or skipped.

## 2. The change

| Family | Abilities | Fires when | Cast |
|---|---|---|---|
| `enemy_melee` (3 -> 14) | the 11 slows with a melee-stat cut | the closest enemy within the 70% bound is IN MELEE | that enemy |
| `enemy_fast_near_ally` (NEW, 4) | the 4 pure slows | the enemy closest to our units that is inside the 70% bound, moving, with a run speed of 5 m/s or more, within 40 m of one of our units | that enemy |
| `enemy_engaged_or_shot` (85 -> 70) | unchanged for the rest, the 4 kept above included | in melee or under missile fire | that enemy |

**The fast-enemy reads.**
- **Speed:** `is_moving()` must be exactly true, and the speed is the unit's live run speed, `fast_speed()`. In the
  2026-10 log, Boris Todbringer's horse read about 7.8 m/s, the same scale as the game's `run_speed` column.
- **Closeness:** the distance is `unit_distance` from each of our living units, the caster included. A distance the
  engine cannot read, or a negative one, never counts.
- **Last check:** the shared pre-cast re-check asks again: is the enemy still fast, moving and close? If not, the
  cast is skipped and not spent.
- **The two settings:** `FOURTH.FAST_ENEMY_MPS = 5` and `FOURTH.FAST_ENEMY_NEAR_M = 40`. Both are your values, not
  ability ranges; the cast bound stays the 70% rule.

**What 5 m/s catches** (run speed from the game data, before any buffs; mounted units use their mount):

| Unit type | Catches |
|---|---|
| cavalry | 179 of 183 |
| chariots | 63 of 88 |
| infantry | 363 of 942 |
| Lord/Hero | 878 of 1,403 |

So a running fast infantry unit near your line also counts. 7 m/s would keep the cavalry and drop almost all
infantry, if you want it narrower after the battle.

**The target filters (15 entries, 17 workbook rows).** The game's own rule, `special_ability_to_invalid_target_flags`,
says who each ability can hit:
- **Lord/Hero only (12):** El Syf, You're Next!, Hunter of Champions, Looming Dread, Assassin's Trophy, Glory Seeker
  (both), Headhunt, Prey of the Blood God, They Needs Stabbin', Trophy Heads, the Transfix hex.
- **Large only (2):** Tendrils of the Sea, Whip of Misery.
- **Large single entity (1):** Fecund Rebirth.

Until now the mod ignored this and could pick an enemy the ability cannot hit. Each entry now carries `target_class`,
and the shared enemy picker and its pre-cast re-check skip an enemy outside it. An enemy whose type cannot be read is
never offered.

**How "large" and "single entity" are decided.** No battle API reads them. Following rule 4, they are generated
from the game data by `tools\gen_unit_size_keys.py`:
- **large (980 unit types):** the man entity or the mount entity has size large or very_large, so a Lord on a dragon
  counts.
- **single (1,479 unit types):** num_men is 1.

The build refuses a pack whose embedded tables differ from the game data. Two tables were added to the game-data
extract for this: `mounts.tsv` (405 rows) and a live `battle_entities.tsv` (1,341 rows). Every other extracted table
was byte-unchanged.

## 3. The proof

| Run | Checks | Failures | File |
|---|---:|---:|---|
| harness133 on the new source (before the rebase) | 5,785 | 35: count pins, the tooltip mirror, and 4 worlds whose stand-in enemy was not a Lord | (not kept) |
| FULL, run 1 | 5,852 | 0 | `h134_run1.txt` |
| FULL, run 2 | 5,852 | 0, byte-identical | `h134_run2.txt` |
| LIGHT | 2,671 | 0 | `h134_light.txt` |
| RED, pre-135 snapshot (light) | 2,625 | 0; RED 10/10 | `h134_red.txt` |

Section 134 (30 worlds):
- **The fast-enemy trigger:**
  - F1: an enemy moving at 7 m/s, 30 m away: one cast at it, with the reason logged.
  - F2: 4.5 m/s: no cast.
  - F3: not moving: no cast.
  - F4: 50 m from the caster but 30 m from an ally: one cast.
  - F5: no unit of ours within 40 m: no cast.
  - F6: outside the 52 m cast bound: no cast.
  - F7: exactly 5.0 m/s: one cast.
- **The target filters:**
  - L1: Looming Dread at a non-Lord: no cast. L2: at a Lord: one cast.
  - L3: Tendrils of the Sea at an Ushabti (large): one cast. L4: at infantry: no cast.
  - L5: Fecund Rebirth at an Ushabti (large, several models): no cast. L6: at a Giant: one cast.
- **Acquiescence:**
  - M1: an enemy only being shot: no cast.
  - M2: an enemy in melee: one cast.

**RED** (the round-134 build):
- F1 and F4 cast nothing.
- L1 (Looming Dread at a non-Lord), L5 (Fecund Rebirth at a multi-model unit) and M1 (Acquiescence at an enemy only
  being shot) all cast. Those are the bugs this round fixes.

## 4. Pins and worlds rebased (old -> new, why)

| Pin | Old | New | Why |
|---|---:|---:|---|
| `enemy_engaged_or_shot` (harness, 4 lines; builder, 3 gates) | 85 | 70 | 11 to enemy_melee, 4 to the new family |
| `enemy_melee` (harness; builder) | 3 | 14 | +11 |
| tooltip mirror | - | + `enemy_fast_near_ally` | the new wording |

Four older worlds aimed a Lord/Hero-only ability at a stand-in enemy that is not a Lord. The new filter refuses that
target, correctly, so these worlds now use a real Lord key (`wh2_dlc09_tmb_cha_arkhan_0`):
- harness 97 FAM INSIDE r150 and FRESH (Headhunt);
- harness 122 E2 (the Transfix hex; its reason check names whatever enemy it was given);
- harness 122 H (Hunter of Champions).

The behaviour each of these worlds tests is otherwise unchanged.

## 5. Build and install

- **`build_and_install135.py`** (from `tools\make_builder135.py`):
  - ROUND 123 to 135 gates OK;
  - size tables match the game data (980 large, 1,479 single);
  - `MATCHES SOURCE: True` for all five files.
- **Installed pack:** md5 **`79c8ffb8f6b0e052cc0feb337b87dde4`**, 1,312,940 bytes, `IDENTICAL True`. The pack is
  131 KB larger, because of the two size tables.
- **A builder weakness found this round:** the first build attempt stopped at an old `== 85` gate. By then the builder
  had already removed the installed pack, which it does early, before the content gates. So for a few minutes the game
  had no mod pack. The rebuild restored it. Moving the
  stale-pack removal after the gates is a follow-up.

Archived:
- `archive\packs\zz_test_deadly_onslaught_20261109_round135.pack`;
- `archive\mod_source\round135\` (source md5 `baf0ed43e774e9efc18f942bfa9b5fcc`, annotated md5
  `7f72847fb21105cc87054518d08dd1c9`).

## 6. Roster documents

- **Tracker:** 29 rows updated, plus section 10.16.
- **Database:** the new family text; `DATABASE VERIFY OK`.
- **Workbook:** `docs\WH3_abilities_master_v27_2026-11-09.xlsx` plus `.ods`.
  - Checked by `XLSX v27 VERIFY OK`.
  - 57 families; the bombardment block is now at row 103.
  - v1 to v26 are byte-unchanged (48 files).
- **Wheel audit:** OK.
- **Progress page:** rebuilt.
- **Trigger audit:** R4 is empty. Its 4 kept abilities are listed under "kept by the user's ruling", with the
  rulings quoted.
- **Candidates left:** R3 (23), R6 (25).

## 7. Not done

- **Not tested in the game.** The first battle will show:
  - whether `fast_speed()` and `is_moving()` read on enemy units the way they read on ours;
  - whether the large set matches the engine's own idea of "large".
- **6 rarer target filters remain unhandled:**
  - undead only (Eternal Gaze);
  - not flying (Spearfisher's Net, Entangle);
  - missile units (Missile Mirror);
  - spellcasters (Void Pendulum, Word of Change).
- **The builder's stale-pack removal** should move after the content gates.
