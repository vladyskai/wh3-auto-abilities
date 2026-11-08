# Round 109 — the air drop is a horizontal CENTRE test, not an edge gap

Date: 2026-10-18 · Harness 109 · Installed pack md5 `74d71679cda995b9e4e9f4ce9daa3fb5`

The user's second field report: *"I tested again and because the distance is calculated edge to
edge, it still drops the rocks too soon. Is there a way to know when another unit is below the
Terradon Riders?"*

This document answers the research questions from the API dump and the decompiled vanilla scripts,
states what was implemented, and records how it was proved.

---

## R1. What `battle_unit` exposes for a position

`battle_unit.lua` (the generated API dump), lines 114-116, verbatim:

```
--- Returns the centre position of the main squad of the unit.
---@return battle_vector #position 
function battle_unit:position() end
```

Related position reads in the same file:

| line | signature | doc |
|---|---|---|
| 114 | `battle_unit:position()` | "the centre position of the main squad of the unit" |
| 118 | `battle_unit:ordered_position()` | "the position to which the unit has been ordered to move to … if the unit is attacking … the current position" |
| 129 | `battle_unit:bearing()` | "the current orientation of the main squad of the unit in degrees" |
| 137 | `battle_unit:ordered_width()` | "the width of the position to which the unit has been ordered in metres" |
| 141 | `battle_unit:position_of_officer()` | "the position of the commanding officer of the unit" |

**Coordinate space: world metres.** `battle_vector.lua`:

```
--- Returns the x co-ordinate stored by the vector. This is the east-west position.
function battle_vector:get_x() end

--- Returns the y co-ordinate stored by the vector. This is the height of the vector position from
--- the water plane.
function battle_vector:get_y() end

--- Returns the z co-ordinate stored by the vector. This is the north-south position.
function battle_vector:get_z() end

--- Returns the distance from a supplied vector to the subject vector in metres, but disregarding
--- any height difference.
function battle_vector:distance_xz(vector) end
```

**Consequence — the ground plane is X/Z, not X/Y.** `get_y()` is HEIGHT above the water plane; a
3D `distance()` from a flyer 40 m up to a unit directly underneath reads 40 m. `distance_xz()` is
the engine's own horizontal distance. The implementation therefore reads `get_x()`/`get_z()` and
uses `distance_xz()` when it answers, with a `sqrt(dx²+dz²)` fallback.

Vanilla proves the shape: `lib_bsu.lua:407-409` builds offsets from `self.unit:position():get_x()`
and `get_z()`, and `lib_bsu.lua:673-676` measures with `position():distance_xz(cached_pos)`.

---

## R2. Is there a radius / footprint / bounding box / size read?

**No per-unit one exists.** `battle_unit.lua` has exactly 106 functions (full list checked); none is
`radius`, `unit_radius`, `bounding_box`, `bbox`, `size`, `unit_size` or `footprint`. The same is true
of `battle_army.lua` (33 methods), `battle_manager.lua`'s unit section and `script_unit.lua`'s
single-unit class.

Every candidate that turned up, with its exact signature and whether vanilla uses it:

| candidate | signature | what it really is | vanilla use |
|---|---|---|---|
| `battle_unit:ordered_width()` | `battle_unit.lua:137`, returns number (metres) | the **formation width** of the *ordered* position — ONE axis, no depth, and it describes the destination order, not the live footprint | **yes, 23 call sites** (`lib_bsu.lua:198,442,480,547,596,690` plus the intro battles) — always to re-issue a move/teleport with the same frontage |
| `script_unit:get_cached_width()` | `script_unit.lua:110` / `lib_bsu.lua:616-619`, returns number (metres) | the width last cached by `script_unit:cache_location()` — the same `ordered_width()` value, behind a cache write | **no call site** in the whole decompiled tree (only the definition) |
| `script_units:radius()` | `script_unit.lua:487` / `lib_bsu.lua:2600-2614`, returns number (metres) | the **collection's** spread: the distance from the mean centre (`centre_point()`) to the furthest unit. It describes how spread out an ARMY is, not one unit's footprint | **yes, but only for camera framing** — the intro battles, e.g. `battle_declarations.lua:474` `local furthest_unit = sunits_player_start:radius();` |
| `script_units:width()` | `script_unit.lua:491` / `lib_bsu.lua:2622+` | the **sum** of the collection's unit widths — an army frontage, not a unit's | yes (intro battles) |
| `battle_entities.radius` | game DATA column (`db_battle_entities.tsv`, joined from `land_units.man_entity`) | the **collision radius of ONE MODEL**: Terradon Riders = `wh2_main_lzd_inf_skink_360_blood_dismembers`, `radius = 0.6` (m), `size = small`. A 10-model unit (`main_units.num_men = 10`, `rank_depth = 2`) is a 5×2 formation; the unit's footprint is the FORMATION, which no column carries | n/a — data, not a script read |

So: **the only real geometric reads at battle time are `position()`, `ordered_position()`,
`unit_distance()` and `unit_in_range()`** — and only the first is a centre.

### Why `ordered_width()` was not used as the radius

A half-width radius would have to come from the ENEMY's formation too, and an infantry block's
`ordered_width` is easily 40-60 m. `(r_caster + r_enemy) * fraction` would then be 15-25 m — looser
than the 7 m proxy that already fired too early, i.e. it would reproduce the user's complaint with
more arithmetic. A width is also one axis only (no depth), and for a wide line the perpendicular
offset is the one that matters. It is documented here as the nearest real footprint read, and left
out of the test deliberately.

---

## R3. Is there an engine helper for "is unit A over unit B" / point-in-area?

**No.** Searched the full dump and the decompiled tree for `is_in_area`, `unit_in_area`,
`point_in_circle`, `in_circle`, `inside`, `is_over`, `above`: no function of that shape exists on
`battle_unit`, `battle_manager`, `battle`, `script_unit` or `script_units`. The complete set of
geometric reads is:

* `battle_unit:unit_distance(target)` — **edge-to-edge**, bounding-box aware (`battle_unit.lua:160`)
* `battle_unit:unit_in_range(target)` — the engine's loose missile reach (the project already
  banned this as a trigger gate: it answered TRUE at 81.3 m where the ability's bound was 52 m)
* `battle_unit:position()` / `ordered_position()` / `position_of_officer()`
* `battle_vector:distance()` (3D) and `battle_vector:distance_xz()` (horizontal)
* `script_units:centre_point()` / `radius()` / `width()` — collection aggregates

The engine *does* evaluate an "over" condition internally — the special-ability usage-flag list in
`battle_unit.lua:391-508` carries `flying_over_platform`, `flying_over_invalid_location`,
`enemies_in_intercept_range` and `enemies_in_intercept_range_large` — but those are flags script can
**set** via `set_special_abilities_flags(flag_key)` for the ability rows to test; there is no read
that answers them for a given pair of units.

---

## R4. How the game's own air-drop / bombing validity is implemented

The 19 keys of the family, from `unit_spec_abil.tsv` (verbatim values): `target_friends`,
`target_enemies`, `target_ground`, `target_self` **all false**, `effect_range 0`,
`target_intercept_range 10`, `bombardment` = the ability's own key, `ai_usage
always_use_only_land`, `num_effected_enemy_units 0`, `update_targets_every_frame false`. Examples:
`wh2_main_unit_abilities_drop_rocks` (5 s recharge, 1 use), `wh2_dlc09_unit_abilities_death_from_above`
(0.1 s, 1 use), `wh_main_unit_abilities_gyrobomber_bomb` (0.1 s, 11 uses).

**There is no Lua-side validity test at all.** A grep of the entire decompiled script tree for the
family's keys returns exactly one scripted use, and it is not a drop test —
`battle/quest_battles/malakai/vampires_empowered/battle_script.lua:272`:

```lua
if unit:can_perform_special_ability("wh3_dlc25_unit_abilities_gyrobomber_fire_bomb")
   or unit:can_perform_special_ability("wh_main_unit_abilities_gyrobomber_bomb")
   or unit:can_perform_special_ability("wh_dlc06_unit_abilities_skyhammer_bomb") then
    ... sunit.uc:reset_ability_number_of_uses(...)
```

— a reload trigger that refills bomb uses near a reload point. `battle_unitcontroller.lua` offers
only `perform_special_ability(ability_key, target_unit)` (line 87), `perform_special_ability_q`
(93) and `perform_special_ability_ground(ability_key, position, orientation_in_degrees,
width_in_m)` (100). The ordnance itself is spawned by the engine (C++) at the caster; the script
layer's only decision is **when to press the button**. The engine's own refusal vocabulary is the
invalid-usage flag list (`grounded`, `flying_currently`, `engaged_in_melee`, …), which script cannot
query as a predicate for a target.

So the mod's trigger is, and must remain, a heuristic on the reads in R1-R3.

---

## Implementation

`FOURTH.AIR_DROP_BOUND_M = 1` (edge gap) is **retired**. The replacement:

```lua
FOURTH.AIR_DROP_CENTER_M = 6

function FOURTH.ad_centre_gap(unit, enemy)      -- returns d, x1, z1, x2, z2
    local ok_a, a = pcall(function() return unit:position() end)
    local ok_b, b = pcall(function() return enemy:position() end)
    ... get_x()/get_z() on both, then a:distance_xz(b) with a sqrt fallback ...
end
```

The picker tests `gap <= bound` where `gap` is the horizontal centre distance; the pre-cast re-check
runs the same helper again immediately before the cast. Everything else is kept: the family's 70%
map bypass (now `ability.range_m = FOURTH.AIR_DROP_CENTER_M`), `air_only` / `no_melee` as declared
per row, the self-centred cast on the OWNER, and fail-closed behaviour (an unreadable position means
"not under the caster").

**Which path was used: the documented CONSTANT.** No radius read exists (R2), so the threshold is
`6 m` of horizontal centre distance — one value to tune, `FOURTH.AIR_DROP_CENTER_M`. It is tighter
than the standing 70% rule's 7 m, and much tighter than the geometry the edge test was measuring.

### The log lines

Fired:

```
  drop_rocks target: 'wh2_main_lzd_inf_skink_skirmishers_0' is UNDER the caster
  (caster=(123.4, 567.8) enemy=(125.1, 567.1) centre=1.9m edge=0.0m bound=6m
   radius=none (constant stands in) air_only=true)
```

Not fired, one line per change:

```
  drop_rocks watch: nearest INFANTRY 'wh2_main_lzd_inf_skink_skirmishers_0' is centre=~10m
  vs bound=6m -> NOT under the caster
```

Two brakes keep that line out of the log's way: it is written only when the nearest infantry is
**inside 30 m** (further away, "not under" is obvious and would write a line on every poll of every
approach), and the distance is reported in **5 m bands**, so an approach writes a handful of lines
rather than one per 0.1 m. The exact number is on the target line and on the pre-cast re-check.

Pre-cast re-check (fires):

```
  drop_rocks pre-cast re-check: still over an INFANTRY enemy (caster_alive=true flying=true
  melee=false infantry=true, centre=1.9m bound=6m) - firing
```

Lapsed at the re-check:

```
  drop_rocks SKIPPED: the drop lapsed before the cast (caster_alive=true flying=true melee=false
  enemy_alive=true infantry=true centre=9.0m bound=6m) - cast not spent
```

`edge=` is printed for comparison with the old log and is **not** part of the test.

---

## Harness 109

**4104 checks / 0 failures**, run twice with byte-identical output, against the live source and the
annotated copy. Red control (H109_LIVE/H109_ANN → `docs/backups/round109/pre109_*.lua`): **36
failures, all in the new section, all accounted for** — including `B2a` (10 m centre offset fires on
the old build), `B3a` (15 m centre with 0.5 m box edges fires on the old build) and `B10b` (6.1 m
fires on the old build).

| world | fixture | expectation | result |
|---|---|---|---|
| B1 | caster and enemy at the same ground point; edges 0.4 m | fires, on the owner; log prints both positions + `centre=0.0m` | green (red: fires too) |
| B2 | 10 m centre offset, edges 0.5 m | **silent** + `watch: … centre=10.0m` | green (**red: fires** — the bug) |
| B3 | **15 m centre offset, edges 0.5 m** | **silent** | green (**red: fires** — the exact report) |
| B4 | no radius method on either handle | fires, log says `radius=none` | green |
| B5 | caster 60 m up, enemy beneath (3D distance 60 m) | fires, `centre=0.0m` | green |
| B6 | two infantry at 5 m and 2 m | fires, names the 2 m one | green |
| B7 | cavalry directly under | silent | green |
| B8 | enemy drifts 2 m → 9 m between pick and re-check | skipped, cast not spent, `centre=9.0m` | green (red: fires) |
| B9 | unreadable `position()` | silent, no crash | green (red: fires) |
| B10 | 6.0 m / 6.1 m | fires / silent | green (red: 6.1 m fires) |
| B11 | nearest infantry 40 m away | silent AND no watch line (the 30 m brake) | green |

Static gates (both files): the 6 m constant, the helper, X/Z only (no `get_y()` inside the helper),
`distance_xz` + `sqrt` fallback, the picker's `gap <= bound`, the same helper in the re-check, the
70% bypass, and the log tokens.

Round-107/108 worlds adapted by design (same check counts): A5 now models an 8 m centre offset as
"outside"; the round-108 B1/B2/B3 worlds now use ground positions (B1 same point, B2 10 m, B3 6.0 m)
because "3 m away" is genuinely *under* the flyer now.

A mock change was needed and is documented in the harness: `vec()` carries real x/y/z and answers
`get_x/get_y/get_z/distance/distance_xz`; `position()` honours `def.pos` (and `def.pos_seq` for the
drift world). Older worlds that set no position read (0,0,0) exactly as before.

---

## Spreadsheet v10 and tracker

`docs/WH3_abilities_master_v10_2026-10-18.xlsx` (+ `.ods`): v10 supersedes v9; v1-v9 are
byte-unchanged. All 19 `air_drop_on_infantry` rows carry the new rule text, the Definitions glossary
row is rewritten, the Numbers header names round 109, and the Changelog has a v10 row.

**Counts unchanged and reconciled from the workbook itself:** 1,797 inventory / 1,141 in-wheel /
658 excluded; 742 implemented; the 46 trigger families sum to **689 entries / 742 keys**;
`air_drop_on_infantry` = **12 entries / 19 keys**. Nothing moved — this is a behaviour change.

`docs/WH3_ability_tracker.md`: a new harness-109 update line, the 19 rows and the trigger glossary
row now describe the centre rule.

---

## How to retest

1. Start a battle with a Drop Rocks carrier (Terradon Riders) — arm the ability from its wheel icon
   as usual.
2. Fly the unit towards an infantry unit and watch for:
   * `drop_rocks watch: nearest INFANTRY '…' is centre=~NNm vs bound=6m -> NOT under the caster` —
     the band tells you roughly how far the *centres* are (it appears only inside 30 m); it fires
     when the exact centre distance is **6.0 m or less**.
   * `drop_rocks target: '…' is UNDER the caster (caster=(x, z) enemy=(x, z) centre=N.Nm …)` — the
     cast fires in that same poll.
3. If it still releases early, **lower** `FOURTH.AIR_DROP_CENTER_M` (one constant, one line, nothing
   else changes). If it never fires even when the flyer looks squarely on top, **raise** it — and
   send the `watch:` lines: they carry the real centre distance at the moment of the decision.

## In plain words: why edge-to-edge failed

`unit_distance` does not measure "how far apart are these two units". It measures **the gap between
their outlines** — the shortest distance from any part of one unit's footprint to any part of the
other's. A flying formation 20 m wide and an infantry block 40 m wide, passing side by side, have
their outlines half a metre apart while their **middles** are 15 m apart. A 1 m test on that number
says "they are touching" — and the bomb drops while the flyer is still beside the enemy, not over
it. The fix measures the distance between the two **middles**, which is what "below the Terradon
Riders" actually means, and 6 m is the width of that window.
