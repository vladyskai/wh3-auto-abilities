# Round 136: audit batch 5, the melee hexes (sign-off round)

Date: 2026-11-09. Harness: `harness135.lua`. Release folder:
`mod_source\releases\20261109_melee_hexes_harness135\`. Audit group R3 of `docs\WH3_trigger_audit_2026-11-09.md`.

## 1. The rulings (user, 2026-11-09, all as recommended)

- **The pure melee hexes (14), "Enemy in melee":** Assassin's Trophy, Lord of Dragons, Master of Beguilement, Oath of
  Vengeance, Otto's Scythe, The Averland Runefang, The Dark Master, The Enfeebling Foe, The Hammer of Karak Drazh,
  Torment Blade, Trophy Heads, Willing Prey, Whip of Agony, Fermented Fungi.
- **The spreading melee-defence hexes (6), "Enemy in melee":** Blight Swarm, Virulent Contagion and Upgraded, Ravaging
  Swarm and Upgraded, Pestilent Potions.
- **The immobilisers (3), "Fast enemy near us":** Gaze of Fate (14 s), Sadistic Snare (33 s, 14 m bound), Spearfisher's
  Net (18 s). These use the round-135 trigger: moving, run speed 5 m/s or more, within 40 m of one of our units.
- **Spearfisher's Net's not-flying filter, "Yes, add it now":** the game refuses a target that is flying at that moment.
- **Earlier decisions:** questionnaire approvals only. The round-123 example ruling applies to the melee hexes: *"The
  one with effect only -40 melee defense makes sense only when the enemy is in melee. It does not make sense to activate
  it when the enemy is shot (please learn from this example)."*

## 2. The change

| Family | Change |
|---|---|
| `enemy_melee` | 14 -> 34 (+20) |
| `enemy_fast_near_ally` | 4 -> 7 (+3) |
| `enemy_engaged_or_shot` | 70 -> 47 |
| target classes | 15 -> 16: `not_flying` on Spearfisher's Net |

The new class reads `enemy:is_currently_flying()` live. Only an exact `false` passes; true, nil or a raising read means
the enemy is not offered. The picker and the pre-cast re-check both apply it. The Lord/Hero filter on Assassin's Trophy
and Trophy Heads stays.

**What this means in battle.**
- The 20 hexes fire only at an enemy that is fighting in melee, never at one that is only being shot.
- The three immobilisers fire at a fast enemy closing on your units, rooting it before contact. Their melee cut is
  mostly wasted, by your choice.
- Spearfisher's Net is never thrown at a flying unit.

## 3. The proof

| Run | Checks | Failures | File |
|---|---:|---:|---|
| harness134 on the new source (before the rebase) | 5,852 | 13: count pins and the Sadistic Snare range world | (not kept) |
| FULL, run 1 | 5,901 | 0 | `h135_run1.txt` |
| FULL, run 2 | 5,901 | 0, byte-identical | `h135_run2.txt` |
| LIGHT | 2,720 | 0 | `h135_light.txt` |
| RED, pre-136 snapshot (light) | 2,692 | 0; RED 10/10 | `h135_red.txt` |

Section 135 (22 worlds):
- **Gaze of Fate:**
  - G1: an enemy moving at 7 m/s: one cast at it.
  - G2: an enemy standing in melee: no cast.
- **Sadistic Snare:** S1: a fast enemy 10 m away: one cast.
- **Spearfisher's Net:**
  - N1: a fast enemy on the ground: one cast.
  - N2: the enemy is flying: no cast.
  - N3: the flight read raises: no cast.
- **Torment Blade:**
  - H1: the enemy is only being shot: no cast.
  - H2: in melee: one cast.
- **Virulent Contagion:**
  - V1: the enemy is only being shot: no cast.
  - V2: in melee: one cast.
- **Trophy Heads:** T1: a Lord in melee: one cast.

**RED** (the round-135 build):
- G1 and N1 cast nothing.
- G2 (immobiliser in melee), H1 and V1 (melee hexes at shot enemies) cast. This is the old behaviour.

## 4. Pins and worlds rebased

| Pin | Old | New |
|---|---:|---:|
| `enemy_engaged_or_shot` (harness; builder, 4 gates) | 70 | 47 |
| `enemy_melee` | 14 | 34 |
| `enemy_fast_near_ally` | 4 | 7 |
| target classes | 15 | 16 |

The harness-97 FAM INSIDE r20 world (Sadistic Snare, now on the fast-enemy trigger) gives its enemy `moving = true`,
so it still proves an in-bound cast at the enemy. The enemy runs at 7 m/s by default and is 9 m from the caster.

## 5. Build and install

- **`build_and_install136.py`** (from `tools\make_builder136.py`, cloned from the order-fixed round-135 builder):
  - ROUND 123 to 136 gates OK;
  - size tables match the game data;
  - `MATCHES SOURCE: True` for all five files.
- **Installed pack:** md5 **`104c049b22f675b1487f425eeb7fdb2e`**, 1,313,294 bytes, `IDENTICAL True`.

Archived:
- `archive\packs\zz_test_deadly_onslaught_20261109_round136.pack`;
- `archive\mod_source\round136\` (source md5 `cf759b400690e68b2ba42c33c77e6bf1`, annotated md5
  `c8e31afa873e791346957c4cf8c6b7bb`).

## 6. Roster documents

- **Tracker:** 27 rows updated, plus section 10.17.
- **Database:** `DATABASE VERIFY OK`.
- **Workbook:** `docs\WH3_abilities_master_v28_2026-11-09.xlsx` plus `.ods`.
  - Checked by `XLSX v28 VERIFY OK`.
  - v1 to v27 are byte-unchanged (50 files).
  - Two checks of my own new verifier were wrong on the first run and were corrected; the workbook was right. The
    target-class rows are now 18, with Spearfisher's Net. The enemy_engaged_or_shot rows are 52, not 47, because
    multi-key entries take two rows.
- **Wheel audit:** OK.
- **Progress page:** rebuilt.
- **Trigger audit:** R3 is empty. R6 (morale, 25) is the last group.

## 7. Not done

- **Not tested in the game.**
- **Five rarer target filters remain:**
  - undead only (Eternal Gaze);
  - not flying (Entangle, a ground-area hex);
  - missile units (Missile Mirror);
  - spellcasters (Void Pendulum, Word of Change).
- **The last audit group:** R6 (morale effects, 25).
