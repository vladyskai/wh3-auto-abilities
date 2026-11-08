# Release 2026-10-17 — THE SUMMON ROUND (harness 102 / v102)

Base: `releases/20261017_boss_gate_harness101` (the shipped harness-101 build).

## What shipped

| class | what | entries | keys | trigger |
|---|---|---|---|---|
| A | the rest of the `wh_type_summon_unit` class — in-wheel, non-illusion, GROUND-CASTABLE | 57 | 68 | `enemy_ground_melee` (Gate of Khorne's) |
| D | the nine unlabelled real spawners | 9 | 9 | `enemy_ground_melee` |
| B | Nurgling Tide — **self-target only** | 1 | 1 | **`self_summon_melee`** (NEW) |
| E | Eye of Khorne — a **finisher** | 1 | 1 | **`enemy_low_health_noncommander`** (NEW) |
| F | The Dreaded Thirteenth (four keys, one entry) | 1 | 4 | **`enemy_melee_noncommander`** (NEW) |
| C | the four illusion summons | 0 | 0 | **EXCLUDED** (none was ever implemented) |

**Counts:** ABILITIES **573 → 642 entries** (573 + 69), **599 → 682 keys** (599 + 83).
`melee_unwavering` 360, `enemy_engaged_or_shot` 86, `enemy_ground_area` 9 unchanged;
`enemy_ground_melee` **1 → 67**; the three new triggers 1 each. `range_real` 96 → 163.
`enemy_ground_keys` 10 → 91.

## The derivation (no hand-typed list)

`tools/derive_summon_plan.py` → `audit/_summon_round_plan.json`:
`spawned_unit` set AND `type = wh_type_summon_unit` AND `spawn_is_decoy` false AND `target_ground = true` AND
in-wheel (`source_type` unit-side, `icon_name`, `is_hidden_in_ui = false`, not the army/quest family) AND not
boss-only (grant junctions) AND not already implemented.

* **One** row of the label set cannot take a ground point: **Nurgling Tide** (`target_intercept_range` 0, no target
  flags, `affect_self` true) — implemented in (B).
* **One** entry has no real range: **The Tallyman's Blades Upgraded** (`target_intercept_range` -1.0) →
  `unbounded = true`, no distance test.
* **One** boss-only exclusion in the label set: `wh3_dlc26_character_abilities_squig_thinkin` (granted only to
  `_boss` units) — stays out.

## The Lord/Hero predicate (E and F)

`FOURTH.commander_keys` = every `land_units` key with `class = "com"` ∪ every key reached from a `main_units` row
with `caste ∈ {lord, hero}` → **1,409 keys**, matched by EXACT equality against `battle_unit:type()`.
`battle_unit:unit_class() == "com"` is the fallback; both unreadable → FAIL CLOSED (treated as a commander).
Corroboration: Eye of Khorne's own invalid-target flags are `health_above_20%` and `unit_is_commander_class`.

FIELD NOTE: the finisher's health read is `common.get_context_value("CcoBattleUnit", <enemy ui id>, "HealthPercent")`
- the same call Class B proved on allies, keyed by an enemy ui id (proven readable by the enemy-target probes).
An unreadable enemy health fails CLOSED (that enemy is never offered). First battle confirms from the `health=NN%` lines.

## Harness 102

* GREEN **3525 checks / 0 failures** (live + annotated).
* RED (pre-102 snapshot = the shipped harness-101 build) **3458 checks / 70 designed failures**: every summon world
  fires nothing (unit 0, ground 0); the failures are the table-size pins (573/599/1/96 → 642/682/67/163), the three
  new tooltip wordings, the 0z static gates for code the snapshot lacks, and earlier rounds' inherited red branches.
* Harness 101 (unmodified) against the new source: **81 failures**, all designed pins — 58 table-size/entry/key,
  8 aggregate world tallies that contain them, 4 trigger-count, 3 tooltip-coverage, 2 `range_real`, 2 pre-cast log
  tokens (the line now prints `eg_bound_text` so an unbounded entry can say `bound=none`), 2 picker-set counts
  (`FOURTH.eg_enemy = best_enemy` is now set by BOTH pickers), 2 A4b per-pass pins.

## Build

All **5 ship files byte-identical** to source (script 661,255 bytes). Installed md5
`a49471940389cf429d5b21aaeac84959`; `dist` == installed, independently re-opened and byte-compared
(`verify_installed102.py`). `zz_probe_dist.pack` untouched.

## Files

* `pre102_live.lua`, `pre102_ann.lua` — pre-edit snapshots (red control)
* `harness102.lua`, `h102_section.lua`, `h102_green.txt`, `h102_red.txt`, `h102_run1..3.txt`
* `build_and_install102.py`, `build102_out.txt`, `verify_installed102.py`
* `tracker_pre102.md`
