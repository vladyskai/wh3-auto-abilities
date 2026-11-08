# Release 2026-10-08 — THE BIG IMPLEMENTATION ROUND — blocks 4, 5 and 6 + two new triggers — harness88

## Shipped source
`script/battle/mod/zz_test_deadly_onslaught.lua`  sha256 `9557d945e1f5b6fad4ee7daa7605e19a3a5854b76ae117f1ef8b2e7cead8babc` (290794 bytes)
`WH3_auto_ability_annotated.lua` (Desktop reading copy)  sha256 `ab992d77f08706e8a5adb51a39d694f9982eb29dabfd3883fef958863202550a` (200717 bytes)
Pack installed to `.../Total War WARHAMMER III/data/zz_test_deadly_onslaught.pack`
installed md5 `5d7f78de9e2e15db058a2ec648e09678` (dist == installed, IDENTICAL True; pack sha256
`9ee7ec38a9da2aec6e6a1f8659edc4a35549a820a9de4dd3c06903f0233d2edb`, size 625924);
per-file sha256 gate: all 5 shipped files MATCHES SOURCE True.
Independent `verify_cleaned_independent.py`: **RESULT PASS** — 5/5 files byte-identical, dist == installed, no probe paths.

## THE CHANGE
**The abilities table grows 102 → 189 entries (108 → 195 keys).** 87 new entries:

| group | trigger | count |
|---|---|---|
| block-4/5 `approved (in-melee self)` | `melee_unwavering` | 54 |
| block-5 `approved (in-melee self - auto, trivial)` | `melee_unwavering` | 15 |
| block-6 auto-accepted (standing rule 9) | `melee_unwavering` | 11 |
| block-4/5 `approved (charge and in-melee)` | `charge_or_melee` | 5 |
| **Will of the Verminking** (NEW trigger) | `verminking_wavering` | 1 |
| **Potion of Toughness** (NEW trigger) | `melee_health75` | 1 |

The key list was derived **programmatically** from `WH3_ability_tracker.md`: every §2/§3a row whose
status was an `approved (...)` status AND whose key was not already in the mod's ABILITIES table
(the 74 block-4/5 keys), plus block 6's 11 standing-rule-9 auto-accepts and the two user-designed
triggers. **No new evaluator for the 85 in-melee/charge entries** — they ride the existing shared
`melee_unwavering` / `charge_or_melee` evaluators. **NO new chunk-level locals** (the chunk compiles
at Lua's 200-local ceiling — everything new rides the `FOURTH` helper bag).

### NEW TRIGGER 1 — Will of the Verminking (`wh3_dlc29_lord_abilities_will_of_the_verminking`)
User: *"Trigger should be when an allie inside the range is wavering. Makes no sense to cast just
when in melee. Make sure the range is conservative (below the ability range in the tooltip, same as
with Glorious Death)."*
Fire when **ANY friendly unit other than the caster is in melee AND wavering AND within a
conservative radius** of the owner; **cast on SELF**. New constant **`FOURTH.VERMINKING_RANGE_M = 25`**
— the game data gives a **35 m** ally aura (`unit_spec_abil.tsv`: `effect_range = 35.0000`,
`ai_usage = augment_melee`), so 25 m is a **DELIBERATELY CONSERVATIVE** trigger **10 m inside** the
aura (mirroring `GLORIOUS_DEATH_RANGE_M = 25` vs its 55 m aura); the source of the number is in the
constant's comment. The **same safety pattern as Glorious Death**: the CLOSEST qualifying ally is
chosen, the gap is **re-checked immediately before the cast** and the cast is **SKIPPED on drift**
(`will_of_the_verminking SKIPPED:`). New evaluator `FOURTH.evaluate_verminking_wavering` + helpers
`FOURTH.vm_ally_gap` / `FOURTH.vm_ally_in_range` / field `FOURTH.vm_ally`.

### NEW TRIGGER 2 — Potion of Toughness (`wh_main_item_abilities_potion_of_toughness`)
User: *"Treat as a heal, since this is a one time activation. So activate when in melee and below
75 percent health."* New evaluator **`FOURTH.evaluate_potion_health`**: **owner in melee AND owner
health ≤ 75%**, reusing the shared live health read (`FOURTH.context_value(unit,"HealthPercent")`)
and the plain hysteresis-free threshold style (no second threshold). Trigger name `melee_health75`.

### ARMY-BAR EXCLUSION (standing rule 10)
User: *"Skip all army bar abilities."* Added as **standing rule 10** in the tracker (with the
`army-bar` keyword documented for the collection's exclusion filter). **Oath of Replenishment**
(base + `_upgraded`) and **Shanty: First/Second Verse** (+ `_ai` twins) are marked
`skipped (army-bar ability)`. The build asserts `army_abilities` never enters the mod.

## Harness 88
Built from the SHIPPED harness87.lua (env pair now `H88_LIVE` / `H88_ANN`). New section 0m tokens +
NINE worlds, each run `[annotated]` + `[live]`:
* **V1** ally in melee + WAVERING + 20 m → fires, cast target = OWNER (owner not in melee).
* **V2** wavering ally at 55 m (beyond 25 m) → SILENT.
* **V3** in-melee ally NOT wavering → SILENT.
* **V4** drift: ally 20 m at decide, 55 m at cast → cast SKIPPED.
* **V5** two wavering in-melee allies → the NEARER (8 m) chosen.
* **Q1** in melee + 70% health → FIRES. **Q2** in melee + 90% → SILENT. **Q3** not in melee + 70% → SILENT.
* **S1** a sample of 7 newly added entries (4 in-melee self, 1 charge-or-melee, 2 block-6 auto) all
  fire on in-melee alone; also asserts the grown table (189 entries / 195 keys).

GREEN: **checks: 2293, failures: 0** (was 2190). The h87 suite boundary holds (`checks == 2189`
after `run_h87()`).

RED (pre-edit snapshot `pre88_live.lua` / `pre88_ann.lua` = the shipped harness-87 build, 102
entries): **checks 2264, failures 77** — every one a designed delta:

| adapted pin (section) | old → new |
|---|---|
| A4a / A4b (badge paths walk the FULL table) | 204 → 378 ; per pass 102 → 189 |
| B4a (unknown-cache full-table fallback) | 102 → 189 |
| H68 #ABIL / marker map / key array | 102 → 189 ; 108 → 195 ; 108 → 195 |
| C6c (every entry wired) + the C6 world return | 102 → 189 |
| 0h `melee_unwavering` count | 91 → 171 |
| 0h `charge_or_melee` count | 4 → 9 |
| 0c not-routing guards | 6 → 7 (the potion evaluator adds one) |
| 0z owner-melee guard | 3 → 4 (the potion evaluator adds one) |
| harness-82 red aggregate | want 16 → 14 (C6c pin differs on the snapshot) |
| harness-87 red aggregate | want 8 → 14 (snapshot now carries the 25 m gate) |
| harness-88 red expectation | 0 → 9 (the SILENT worlds pass trivially on the snapshot) |
| env pair | H87 → H88 |

The non-pin red deltas are the whole HARNESS-88 section (its 0m tokens + the V/Q/S worlds) and the
two A/B world aggregates whose pinned worlds (A4/B4) now differ.

## Tracker
Every ability implemented in this round is marked: 74 block-4/5 entries → `implemented (...)` (their
`approved (...)` status), 11 block-6 auto-accepts → `implemented (in-melee self - auto, trivial)`,
the two new triggers → `implemented (verminking_wavering)` / `implemented (melee_health75)`, and the
six army-bar items → `skipped (army-bar ability)`. **No `approved (...)` row remains.** Added
standing rule 10, the legend entries and §9 (the implementation-round log).
