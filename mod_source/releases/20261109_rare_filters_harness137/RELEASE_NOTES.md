# Round 138: the rarer target filters and Missile Mirror's shooting trigger (sign-off round)

Date: 2026-11-09. Harness: `harness137.lua`. Release folder: `mod_source\releases\20261109_rare_filters_harness137\`.

## 1. The request and rulings (user, 2026-11-09)

"Rarer target filters": the five enemy-targeted abilities whose game target rule (round 135 found 15, round 136
added Spearfisher's Net) was still unhandled.

| Ability | Game rule (invalid target flag) | Filter |
|---|---|---|
| Eternal Gaze | `undead_unit` | NEW class `not_undead`: a GENERATED undead set (355 unit types) |
| Entangle | `flying_currently` | `not_flying` (live `is_currently_flying()`, exact false only) |
| Missile Mirror | `is_not_missile_unit` | NEW class `missile` (the existing generated missile set) |
| Void Pendulum, Word of Change | `hasnt_casting_ability` | `commander` (user ruling "Lords/Heroes only": no battle read or data list can tell a spellcaster, because Lords and Heroes learn spells through campaign skills) |

**Missile Mirror's trigger (user ruling "Missile enemy shooting").** It was firing at an enemy in melee or under fire,
but a missile unit in melee is not shooting. It moves to the NEW `enemy_missile_shooting`:
- the closest enemy missile unit inside the 70% bound (140 m) that is not in melee;
- and is SHOOTING: its `ammo_left()` dropped between two samples no more than `ENEMY_AMMO_FRESH_S = 2` s apart;
- with the last drop inside the round-126 firing-flag window, max(2 x its reload, 20 s).

The pre-cast re-check asks again: still shooting, not in melee, within the bound.

**Unproven:** the enemy ammunition read has never been seen on an enemy in a battle. It fails closed: no read means
no cast. The live log writes one line the first time it cannot be read: `missile mirror: an enemy's ammo_left()
cannot be read`.

## 2. The undead set

`tools\gen_undead_keys.py` takes every land unit whose `attribute_group` carries the unit attribute `undead`. That
link lives in `unit_attributes_to_groups_junctions`, extracted live this round as `gamedata\wh3\unit_attr_groups.tsv`
(8,562 rows). The older frozen dump has 280 undead rows, the live table 276. The build refuses a pack whose embedded
table differs from the game data.

## 3. The proof

| Run | Checks | Failures | File |
|---|---:|---:|---|
| harness136 on the new source (before the rebase) | 5,948 | 21: count pins, the tooltip mirror, the Entangle range world | (not kept) |
| FULL, run 1 | 5,995 | 0 | `h137_run1.txt` |
| FULL, run 2 | 5,995 | 0, byte-identical | `h137_run2.txt` |
| LIGHT | 2,814 | 0 | `h137_light.txt` |
| RED, pre-138 snapshot (light) | 2,784 | 0; RED 8/8 | `h137_red.txt` |

Section 137 (22 worlds):
- **Eternal Gaze:**
  - E1: an undead enemy in melee: no cast.
  - E2: a living enemy in melee: one cast.
- **Void Pendulum:**
  - P1: a regular enemy unit: no cast.
  - P2: an enemy Lord: one cast.
- **Entangle:**
  - G1: an enemy on the ground: one ground cast.
  - G2: a flying enemy: no cast.
  - G3: no flight read: no cast.
- **Missile Mirror:**
  - M1: handgunners whose ammunition drops every poll, not in melee: one cast.
  - M2: handgunners whose ammunition never drops: no cast.
  - M3: a non-missile unit whose ammunition drops: no cast.
  - M4: shooting handgunners in melee: no cast.

**RED** (the round-137 build):
- E1, P1 and G3 cast, because the old build ignored the target rules.
- M1 casts nothing, because the old build never saw a shooting enemy.

## 4. Pins and worlds rebased

| Pin | Old | New |
|---|---:|---:|
| `enemy_engaged_or_shot` (harness; builder 4 gates) | 47 | 46 |
| target classes | 16 | 21 |
| tooltip mirror | - | + `enemy_missile_shooting` |

The harness-97 FAM INSIDE r15 world (Entangle) gives its enemy `is_currently_flying() = false`, so it still proves
the ground cast on the enemy.

## 5. Build and install

- **`build_and_install138.py`** (from `tools\make_builder138.py`, order-fixed):
  - ROUND 123 to 138 gates OK;
  - the undead table matches the game data;
  - `MATCHES SOURCE: True` for all five files.
- **Installed pack:** md5 **`4d69206141c5d9eb89506fd0ed1064bd`**, 1,340,319 bytes, `IDENTICAL True`.

Archived:
- `archive\packs\zz_test_deadly_onslaught_20261109_round138.pack`;
- `archive\mod_source\round138\` (source md5 `9c4aebc3d2e0bbd366acd55f853d5ef3`, annotated md5
  `6f6f92fd91f9a08bba748c3089aecd5c`).

## 6. Roster documents

- **Tracker:** 5 rows updated, plus section 10.20.
- **Database:** the new family text; `DATABASE VERIFY OK`.
- **Workbook:** `docs\WH3_abilities_master_v30_2026-11-09.xlsx` plus `.ods`.
  - Checked by `XLSX v30 VERIFY OK`.
  - 59 families; the bombardment block is now at row 105; 23 target-class rows.
  - v1 to v29 are byte-unchanged (54 files).
  - My own verifier first expected 22 target-class rows. Missile Mirror's new text also names its class, so 23 is
    right; the check was corrected.
- **Wheel audit:** OK.
- **Progress page:** rebuilt.
- **Trigger audit:** every group is empty.

## 7. Not done

- **Not tested in the game.** In particular, the enemy `ammo_left()` read, and whether a non-caster Lord picked by
  Void Pendulum or Word of Change is refused cleanly.
- **Every automated enemy-targeted ability now honours its game target rule.** The siege-platform flags (casting
  while on a wall) are not modelled; they only matter in sieges.
