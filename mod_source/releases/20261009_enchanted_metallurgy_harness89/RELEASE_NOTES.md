# Release 2026-10-09 — BLOCK 8 ENCHANTED METALLURGY IMPLEMENTATION ROUND — harness89

## Shipped source
`script/battle/mod/zz_test_deadly_onslaught.lua`  sha256 `e500c2e7b2ce4cda00a2ca11277564a2cad8c8349602d2a8c1b45d5624d710cb` (298655 bytes)
`WH3_auto_ability_annotated.lua` (Desktop reading copy)  sha256 `34a24c56f226b8136e7478222b6eec29110eb6c032ade76f06bd7b655befe4de` (206499 bytes)
Pack installed to `.../Total War WARHAMMER III/data/zz_test_deadly_onslaught.pack`
installed md5 `b82ca4856919cb1866da239ad27a54c6`, size 633785; pack sha256
`7791d56d51a9dd9c14e121f36c82080768da26c3b82bd73537b95f73517971b1`.
Per-file sha256 gate (build): all 5 shipped files MATCHES SOURCE True.
Independent `verify_cleaned_independent.py`: **RESULT PASS** — 5/5 files byte-identical, dist == installed, no probe paths.

## THE CHANGE
**The abilities table grows 189 → 193 entries (195 → 199 keys).** Four new entries, all on ONE new trigger:

| ability | key | trigger |
|---|---|---|
| Enchanted Metallurgy | `wh3_main_character_abilities_enchanted_metallurgy` | `metallurgy_melee` |
| Enchanted Metallurgy: Flaming | `wh3_main_character_abilities_enchanted_metallurgy_flaming` | `metallurgy_melee` |
| Enchanted Metallurgy: Piercing | `wh3_main_character_abilities_enchanted_metallurgy_piercing` | `metallurgy_melee` |
| Enchanted Metallurgy: Poison | `wh3_main_character_abilities_enchanted_metallurgy_poison` | `metallurgy_melee` |

### The user's trigger (verbatim, same answer for all four keys)
*"When self or ally in range in melee. When ally in range is shooting."* — these are dual-purpose buffs
(+weapon damage and +missile damage), which is why both halves were requested.

### MELEE half — SHIPPED (`FOURTH.evaluate_metallurgy_melee`)
Fire when the **OWNER itself is in melee**, OR any **friendly unit other than the caster is in melee
within a conservative radius**; **CAST ON SELF** (self-centred buff that also reaches nearby allies —
the default `target or unit`, no `cast_target` write). New constant **`FOURTH.METALLURGY_RANGE_M = 25`**
— the game data gives a **35 m** ally aura (`unit_spec_abil.tsv`: `effect_range = 35.0000` for all four
keys, `ai_usage = augment_melee`), so 25 m is a **DELIBERATELY CONSERVATIVE** trigger **10 m inside** the
aura (the same field-proven pattern as `GLORIOUS_DEATH_RANGE_M = 25` vs its 55 m and
`FOURTH.VERMINKING_RANGE_M = 25` vs its 35 m); the source of the number is in the constant's comment.
Shipped with the **Glorious-Death / Verminking safety pattern**: the **CLOSEST** qualifying in-melee ally
is chosen, the gap is **re-checked immediately before the cast** and the cast is **SKIPPED on drift**
(`enchanted_metallurgy SKIPPED:`). The owner-in-melee self arm leaves `FOURTH.mtl_ally` nil — never gated.
New evaluator `FOURTH.evaluate_metallurgy_melee` + helpers `FOURTH.mtl_ally_gap` / `FOURTH.mtl_ally_in_range`
/ field `FOURTH.mtl_ally`. **NO new chunk-level locals** (everything rides the `FOURTH` bag).

### SHOOTING half — COULD NOT BE BUILT (API research complete; no proxy invented)
**RESEARCH FIRST — the battle-script API (game dump `battle_unit.lua`) exposes NO per-unit
"is firing / is shooting" read.** The only missile-related reads are:
* `battle_unit:is_under_missile_attack()` — *"Returns whether the unit is currently taking fire."*
  **DEFENSIVE (the unit RECEIVING fire), the WRONG direction** — the closest but unusable.
* `battle_unit:current_target()` — returns the unit's target; a **melee unit has one too**, so it proves
  nothing about firing (the closest *mocked* read; rejected as insufficient, not a firing predicate).
* `battle_unit:ammo_left()` / `starting_ammo()` — a *"has fired at some point this battle"* count, not
  *"is firing now"*; `battle_unit:missile_range()` — a **static** ranged-capable property.
* `battle_manager:get_num_units_under_fire()` / `get_proportion_under_fire()` — **battle-level** and also
  count units **UNDER** fire; require `start_engagement_monitor`.
The engine's own flag vocabulary (`flags.tsv`: `is_missile_unit`, `is_under_missile_fire`,
`is_under_bow_fire`/`is_under_gun_fire`, `cannot_perform_missile_attack`, `have_ammo_below_threshold`) is a
**DATA-TABLE** construct for the ability auto-activate/deactivate system, **not a Lua script read** — and
even it contains no "the unit is firing" flag (only unit-type / under-fire).
**Trust class:** the field-proven booleans we use safely (`is_routing`, `is_wavering`, `is_in_melee`,
`is_moving_fast`) are same-class `battle_unit` boolean reads; **no same-class "is firing" read exists**.
Per the task's rule, **no proxy was invented** — the melee half ships alone.

## Harness 89
Built from the SHIPPED harness88.lua (env pair now `H89_LIVE` / `H89_ANN`). New section 0m tokens +
SIX worlds, each run `[annotated]` + `[live]`:
* **M1** owner in melee → FIRES, cast on self.
* **M2** in-melee ally WITHIN 25 m (20 m), owner NOT in melee → FIRES, cast on the OWNER; closest ally chosen.
* **M3** in-melee ally at 55 m (beyond 25 m) → SILENT.
* **M4** nobody in melee → SILENT.
* **M5** drift: ally 20 m at decide, 55 m at cast → cast SKIPPED.
* **M6** the four new entries all fire on in-melee alone; also asserts the grown table (193 entries / 199 keys).

GREEN: **checks: 2369, failures: 0**.

RED (pre-edit snapshot `pre89_live.lua` / `pre89_ann.lua` = the shipped harness-88 build, 189 entries):
**checks 2339, failures 56** — every one a designed delta: the adapted table-size pins (A4a 386 /
A4a-b 193 per pass, B4 193, H68 193/199, C6c 193, the two A/B world aggregates, the run_h88 S1 world
193/199), and the whole HARNESS-89 section (its 0m tokens + the M1/M2/M5/M6 firing legs; the SILENT/SKIP
worlds M3/M4 both files + the annotated drift world M5 pass trivially on the snapshot → 5/12).

## Tracker
The four Enchanted Metallurgy keys are marked **`approved (melee self-or-ally / shooting ally in range)`**
(the requested string) in §2 (#307–#310) and §3a, with the added note that the **MELEE self-or-ally half is
IMPLEMENTED (harness89)** and the **SHOOTING half is NOT built (no per-unit is-firing/is-shooting read in
the battle API)**. The legend entry and the §9/block-8 summary were updated to record the completed
research; a new header-log entry "Update 2026-10-09 (block 8 Enchanted Metallurgy IMPLEMENTATION ROUND —
harness89)" was added. The four **Master of Alchemy** keys (same trigger request) remain `approved`.
