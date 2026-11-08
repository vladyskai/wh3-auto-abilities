# Round 109 — the air drop is a horizontal CENTRE test (not an edge gap)

Date: 2026-10-18 · Harness 109 · Installed pack md5 `74d71679cda995b9e4e9f4ce9daa3fb5`

The user's second field report, verbatim: *"I tested again and because the distance is calculated
edge to edge, it still drops the rocks too soon. Is there a way to know when another unit is below
the Terradon Riders?"*

One behaviour fix ships. No counts change.

---

## 1. What was wrong

`battle_unit:unit_distance()` is **edge-to-edge**, and the dump says so in its own words
(`battle_unit.lua:160`):

> *Returns the shortest distance in metres between this unit and a supplied unit, taking into
> account their bounding box rather than just working out the centre-to-centre distance.*

It is the gap between the two **outlines**. Two wide formations passing side by side have their
outlines half a metre apart while their **centres** are 15 m apart — so a 1 m bound on that number
still fires while the flyer is nowhere near over the target. That is exactly the reported symptom:
the round-108 log printed 6.9 m and 6.0 m **edge** gaps and released the rocks early.

## 2. The new rule

Fire when an enemy INFANTRY unit is **UNDER** the caster: the **horizontal centre-to-centre**
distance is inside **`FOURTH.AIR_DROP_CENTER_M = 6`**.

* Position: `battle_unit:position()` — *"the centre position of the main squad of the unit"*
  (`battle_unit.lua:114`).
* Ground plane: **X/Z**. `battle_vector:get_y()` is *"the height of the vector position from the
  water plane"* and `get_z()` is north-south, so the horizontal distance is the engine's own
  `battle_vector:distance_xz()` (*"disregarding any height difference"*), with a `sqrt(dx²+dz²)`
  fallback. The 3D distance is never used — a flyer 40 m up would read 40 m from a unit directly
  beneath it.
* **No radius read exists** anywhere in the API (`battle_unit.lua`'s 106 methods; `ordered_width()`
  is the *ordered* formation width on one axis; `script_units:radius()` is a **collection's** spread
  radius, called by vanilla only to frame the camera on an army; `battle_entities.radius = 0.6 m` is
  **one model's** collision radius). So 6 m is a **documented constant standing in for the
  formation footprint** — the drop families carry 10 models in a rank_depth-2 formation (a frontage
  of roughly 15–20 m), and 6 m keeps the enemy under the **middle** of it. It is **one value to
  tune**: lower it if the drop is still early, raise it if it never fires.

Kept exactly as before: the family's **70% map exemption** (now `ability.range_m =
FOURTH.AIR_DROP_CENTER_M`), `air_only` / `no_melee` per row, the self-centred cast on the OWNER, the
logged pre-cast re-check (which now re-reads the **centre** distance), and **fail-closed** behaviour
— an unreadable position means "not under the caster".

## 3. What the log now answers

```
  drop_rocks target: 'wh2_main_lzd_inf_skink_skirmishers_0' is UNDER the caster
  (caster=(123.4, 567.8) enemy=(125.1, 567.1) centre=1.9m edge=0.0m bound=6m
   radius=none (constant stands in) air_only=true)

  drop_rocks watch: nearest INFANTRY '…' is centre=~10m vs bound=6m -> NOT under the caster
```

Both positions, the centre distance, the (diagnostic-only) edge gap, the threshold and — when it
holds — the number that failed. `edge=` exists so the old log can be compared directly; it is not
part of the test. The watch line has two brakes so it cannot flood: it appears only when the nearest
infantry is **inside 30 m**, and the distance is banded at **5 m** (one line per band, not per 0.1 m).

## 4. Harness 109

* **Green: 4104 checks, 0 failures**, run twice with byte-identical output (`h109_run1.txt` =
  `h109_run2.txt`), against the LIVE source AND the annotated copy.
* **Red control** (`H109_LIVE`/`H109_ANN` → `docs/backups/round109/pre109_*.lua`): **36 failures, all
  in the new section, all accounted for** — the old build fires at a 10 m centre offset, at a 15 m
  centre offset with 0.5 m box edges (the exact report), at 6.1 m, on the drift world and on the
  unreadable-position world.
* Worlds: B1 centre-under fires · B2 10 m offset silent · B3 **15 m offset with close box edges
  silent** · B4 no-radius constant path · B5 60 m-high caster fires (`centre=0.0m`) · B6 closest of
  two · B7 non-infantry silent · B8 drift 2→9 m skipped · B9 unreadable silent · B10 6.0 fires /
  6.1 silent · B11 a 40 m nearest enemy writes NO watch line (the 30 m brake).
* Static gates on both files: the 6 m constant, the helper, **X/Z only** (no `get_y()` in the
  helper), `distance_xz` + `sqrt` fallback, the picker's `gap <= bound`, the same helper in the
  re-check, the 70% bypass, and the log tokens.
* Designed deltas inside the older sections (check counts unchanged): round-107's A5 world now models
  an 8 m centre offset as "outside" (3 m is genuinely *under* the flyer now), and round-108's B1/B2/B3
  worlds use ground positions (same point / 10 m / 6.0 m).
* Mock: `vec()` carries real x/y/z and answers `get_x/get_y/get_z/distance/distance_xz`;
  `position()` honours `def.pos` and `def.pos_seq` (the drift world). Worlds that set no position read
  (0,0,0) as before.

## 5. Counts, files, hashes

* ABILITIES: **689 entries / 742 keys** (unchanged), **46 evaluators** (unchanged),
  `air_drop_on_infantry` **12 entries / 19 keys** (unchanged) — behaviour only.
* Spreadsheet `docs/WH3_abilities_master_v10_2026-10-18.xlsx` (+ `.ods`); v10 supersedes v9;
  **v1-v9 byte-unchanged**. 19 air-drop rows rewritten, Definitions glossary row rewritten, Numbers
  header + reconciliation updated, Changelog v10 row added. Numbers re-checked from the workbook:
  1,797 / 1,141 / 658 / 742 and the 46 families summing to 689 / 742.
* Tracker `docs/WH3_ability_tracker.md`: new harness-109 update line, 19 rows, glossary row.
* Research `docs/WH3_round109_airdrop_centre.md` (R1-R4 with the dump evidence).
* Build: 5 ship files **MATCHES SOURCE: True** (per-file sha256), pack byte-identical to source;
  **installed md5 `74d71679cda995b9e4e9f4ce9daa3fb5`** (built == installed).
* `zz_probe_dist.pack` left installed (md5 `d4e67cfb8bc562c7d6f0ff742909c13d`).

## 6. Retest

Arm Drop Rocks on Terradon Riders, fly at an infantry unit, and read the log:

* `watch: … centre=NN.Nm vs bound=6m -> NOT under the caster` — it fires when that number is ≤ 6.0.
* `target: … is UNDER the caster (… centre=N.Nm …)` — the cast fires in the same poll.

If it is still early, **lower** `FOURTH.AIR_DROP_CENTER_M`; if it never fires, **raise** it. Send the
`watch:` lines with the report — they carry the exact centre distance at the decision.
