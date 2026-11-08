# HARNESS 94 / ACCUSATION'S ENEMY-TARGETED TRIGGER — release notes

## What shipped
Accusation (`wh_main_hero_abilities_accusation`) now **fires automatically on an enemy** — the
**FIRST ENEMY-TARGETED trigger** in the mod. The round-4 probe's log-confirmed enemy-targeting
route (`bench_fresh`) is now wired into the main mod.

**New reusable evaluator `enemy_engaged_or_shot`** (`FOURTH.evaluate_enemy_engaged_or_shot`), written
for reuse (Accusation is the first ability on it; the other ~97 enemy-aimed abilities can follow):

> Per poll, for a unit that owns an enemy-targeted key: enumerate the enemy script units
> (`bm:get_scriptunits_for_main_enemy_army_to_local_player()`); keep those that are **(a)** alive and
> valid and **(b)** inside the ability's own reach; of those pick one that is **`is_in_melee()` OR
> `is_under_missile_attack()`** — **prefer in-melee; among equals the closest**. If none qualifies, do
> nothing. The chosen enemy is the **CAST TARGET — never the owner.**

* **Range source**: the ability's own `target_intercept_range` (`unit_spec_abil.tsv` = **75.0000 m**),
  stored as the named constant **`FOURTH.ACCUSATION_RANGE_M = 75`**. The enemy is offered while
  `unit:unit_in_range(enemy)` is true, else `unit:unit_distance(enemy) <= 75`, else the caster is in melee.
* **Cast route (the proven fresh-handle route)**: the CASTER's `script_unit` is re-fetched FRESH from
  the friendly enumerator each tick (`FOURTH.eg_fresh_caster_su`) and the enemy is re-fetched FRESH
  from the enemy enumerator the same tick, then
  `caster_su.uc:perform_special_ability(key, enemy_su.unit)` — the `bench_fresh` shape that landed in
  the probe. (`TAKE_CONTROL_FIRST` is off, matching the winning route.)
* **Pre-cast re-check**: the chosen enemy is re-read immediately before the cast; if it is no longer
  alive / in melee / under fire / in range, the cast is **SKIPPED** (not spent).
* **HOLD**: the existing per-pair guard + cooldown hold — it never fires every tick.
* **Fail-safe read**: `is_under_missile_attack()` exists but was never probed on an enemy — an
  unreadable read is treated as **FALSE**, with ONE log line for the whole battle. (It was readable on
  the harness enemy; the mod never invents a firing predicate — no `is_firing` / `is_shooting`.)

### Distinct log lines (live build)
| Situation | Line |
|---|---|
| in-melee arm fires | `ATTEMPT accusation '...' on '<caster>' ui id <n> \| reason: enemy in melee (targeting <enemy type>) \| armed=ON` |
| under-fire arm fires | `... \| reason: enemy under missile fire (targeting <enemy type>) ...` |
| target chosen | `  accusation target: '<type>' is the chosen enemy (melee\|missile) within 75m` |
| pre-cast OK | `  accusation pre-cast re-check: target still engaged (<arm>, melee=<b> shot=<b>, in_range=<b>) - firing` |
| lapsed | `  accusation SKIPPED: the chosen enemy lapsed before the cast (alive=<b> melee=<b> shot=<b> in_range=<b>) - cast not spent` |
| unreadable missile read | `accusation: enemy is_under_missile_attack read UNAVAILABLE (raised) - treated as FALSE (fail-safe). One-time notice.` |

### Tooltip wording (per-entry, from `FOURTH.TRIGGER_TIP`)
`enemy_engaged_or_shot = "When armed, fires when an enemy unit in range is in melee or under missile fire"`

## Counts
* abilities table: **579 -> 579 entries** (**605 -> 605 keys**) — Accusation already existed; only its
  **trigger moved**: `melee_unwavering` **481 -> 480**, `enemy_engaged_or_shot` **0 -> 1**.
* NO new chunk-level locals (every helper/constant/slot rides the `FOURTH` bag); no `string.find`.

## Harness 94
* **GREEN: 2772 checks / 0 failures** (both the live source and the annotated reading copy).
* **RED: 2739 checks / 62 failures** — the baseline snapshot is `pre94_live.lua` / `pre94_ann.lua`
  (the **shipped harness-93 build**: no enemy evaluator, Accusation still on `melee_unwavering = 481`).
  Every red failure is DESIGNED:
  * the moved `melee_unwavering` pin (sections 0h/0m/0n/0o/0p) — **12** (6 pins x 2 files);
  * the harness-93 wording-presence check (the new wording is absent on the snapshot) — **2**;
  * the new **section-0r** tokens (evaluator / wiring / tooltip / trigger move / range constant /
    enumerator / fresh-caster helper / fail-safe missile read / slot counts / reason strings) — **23**;
  * the firing N-world legs (the enemy evaluator is absent, so nothing fires) — **25**.
  * The RED CONTROL (harness 94) aggregate **passes** (5/18 world results, exactly the SILENT worlds
    N3/N4 both files plus the ANNOTATED leg of the lapse world N5).

### The N-worlds (each run against live AND annotated = 18 world results)
| World | Proves | Green |
|---|---|---|
| N1 | enemy in melee in range -> **FIRES at that enemy**; caster re-fetched fresh | 1 fire |
| N2 | enemy under missile fire in range -> **FIRES** (distance-fallback range) | 1 fire |
| N3 | enemy in range, neither melee nor under fire -> **SILENT** | 0 fires |
| N4 | enemy in melee but **out of range** -> **SILENT** | 0 fires |
| N5 | condition **lapses** between pick and cast -> **SKIPPED** (skip line) | 0 fires |
| N6 | unreadable `is_under_missile_attack` -> treated **FALSE** + one-time log | 0 fires |
| N7 | **self-cast regression guard**: the target IS the enemy, is NOT the owner | 1 fire |
| N8 | **prefer in-melee** over under-fire | melee enemy chosen |
| N9 | **closest among equals** | nearer enemy chosen |

Green N-worlds: **18/18 passed, 5 fires** (live). Red N-worlds: 5/18 (the silent worlds).

## Unreadable enemy reads
* `is_under_missile_attack()` — the harness models it readable (`def.missile`); the **unreadable** case
  (raise) is exercised in N6 and handled fail-safe (treated FALSE, one-time log). It was NEVER probed
  on a live enemy in round 4, so this path is by construction, not by live measurement.
* All other enemy reads used (`type()`, `number_of_men_alive()`, `is_in_melee()`, `is_valid_target()`,
  `unit_in_range()` / `unit_distance()`) were readable in the harness; `is_valid_target()`/`is_valid()`
  are tried in that order and an unreadable validity **fail-opens** (never blocks).

## Files
    script/battle/mod/zz_test_deadly_onslaught.lua   (live)  sha256 26ebfddf4f89578c6b9a63427b5baa95f6b9f0df7754e150bd0f29626c833ea2
    WH3_auto_ability_annotated.lua                   (reading copy) sha256 518dae3524aa9565453426434f0e37b53af1125b65e1d203625319b70137fd51

## Build + install (RPFM WebSocket ws://127.0.0.1:45127, server started then stopped)
    All 5 ship files MATCHES SOURCE: True (per-file sha256 gate).
    Main mod byte-identical (untouched by the packer): True.
    installed md5 65e66f6a87547268ae6d4c2c116558fa   (dist == installed, IDENTICAL True)

## Interference note
The throwaway probe pack **`zz_probe_enemy_target.pack` (md5 `e21411bdd306db0e520f4e0b19a0244a`)** is
STILL installed in the game's `data/` folder from the round-4 probe and is **NOT part of this ship**.
It runs its own 6-route enemy-cast sweep every battle and WILL interfere with field-testing — delete
it (and `zz_probe_enemy_target_log.txt`) before testing. This round did not touch it.
