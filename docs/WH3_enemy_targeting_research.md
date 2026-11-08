# WH3 — Enemy targeting from a battle script: can a script obtain a handle to an ENEMY unit?

**Research task 1 of 2** · 2026-10-09 · read-only (no mod edits, no build)
**Scope question:** how does the AI/engine cast hexes and other enemy-targeted abilities, and can a battle script legally obtain a handle to an enemy unit? This decides whether the ~97 abilities the triage auto-excluded as "no enemy-unit read" (`WH3_remaining_triage.md` §1a, 76 rows + friends) can actually be fixed.

## ⚠ ROUND-4 CORRECTION (2026-10-10) — read this before the TL;DR

The TL;DR below is right about the **reconnaissance** (the enemy units *do* enumerate and read; the API *does* accept an enemy target argument) but it was **wrong about the conclusion for the script path**. Round 3's live battle proved that `uc:perform_special_ability(key, enemy_battle_unit)` returns `accepted=true err=-` and is nevertheless a **silent no-op**: the target's active-effect count never moves, the caster's never moves, and `can_perform_special_ability` stays `true` afterwards (no cooldown consumed). Passing a `script_unit` or `nil` is a Lua type error. So "the benchmark casts at enemies with this call" needed to be re-tested properly, not assumed.

In response this document was extended with **Round 4 — an exhaustive route sweep**: every remaining candidate call form is enumerated from the API dumps, the game's own battle UI is quoted for the manual click path, and the probe was rebuilt to try each surviving candidate as its own **labelled route** with paired caster/target effect-count deltas and a machine-checked `landed=yes|no`. See **§ROUND 4** at the end.

---

## TL;DR

**The prior finding is wrong at the script layer.** "An enemy unit has no card and no id, so there is no enemy-unit read" is true only of the **UI-card layer**. The **script layer has a first-class, engine-supported enemy enumerator and enemy reads**, and the engine's own shipped core script uses them:

- `battle_manager:get_scriptunits_for_main_enemy_army_to_local_player()` — a `script_units` collection of the enemy army (the exact analogue of `get_scriptunits_for_local_players_army()`).
- `battle_manager:get_scriptunits_for_army(alliance_id, army_id)` — **any** army by alliance index.
- `battle_army:units()` → `battle_units` with `:count()` / `:item(i)` → enemy `battle_unit`s you can read (`is_commanding_unit`, `is_routing`, `is_shattered`, `number_of_men_alive`, `unary_hitpoints`, `is_in_melee`, `position`, `is_valid_target`, …). **The engine's own `lib_battle_manager.lua` reads enemy units exactly this way.**
- `battle_unit:current_target()` — **the mod already calls this today** and gets the enemy our unit is fighting.
- `battle_unitcontroller:perform_special_ability(ability_key, target_unit)` accepts a **`battle_unit`** target, and vanilla benchmark scripts cast enemy-targeted abilities (ice sheet, hailstorm, burning head) **at enemy units** with exactly this call.

**VERDICT: enemy targeting IS achievable from a battle script.** Details, evidence and confidences per question below.

---

## Sources inspected

| Source | Path |
|---|---|
| Battle-script API dumps | `%LOCALAPPDATA%\Temp\wh3\` : `battle_unit.lua`, `battle_unitcontroller.lua`, `battle_manager.lua`, `script_unit.lua`, `battle_army.lua`, `battle.lua`, `ai_planner.lua` |
| Extracted vanilla scripts (901 .lua) | `C:\Users\vlady\Desktop\WH3_mod\archive\research\WH3-scripts\` (incl. the two implementation libs `script/_lib/lib_battle_manager.lua`, `script/_lib/lib_battle_script_unit.lua`) |
| Ability DB tables | `C:\Users\vlady\Desktop\WH3_mod\archive\research\wh3\unit_spec_abil.tsv` (the real `unit_special_abilities` table); `%LOCALAPPDATA%\Temp\wh3\special_ability_to_invalid_target_flags_tables.tsv`, `special_ability_to_invalid_usage_flags_tables.tsv` |
| The mod under study (read-only) | `C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua` |

Note: the mod's triage references the table as "`unit_spec_abil`"; the file on disk is `...\research\wh3\unit_spec_abil.tsv`. There is no `unit_spec_abil.tsv` under `%TEMP%\wh3` (that dir holds `land_abil.tsv`, which is the ability→unit **ownership** table, a different thing).

---

## Q1. Is there an enemy-script-unit enumerator analogous to `get_scriptunits_for_local_players_army()`?

**Answer: YES — three of them, plus the raw `battle_units` collection.** Return type is `script_units` (a collection of `script_unit`), and each `script_unit` exposes `.unit` (the `battle_unit`) and `.uc` (its controller), so every `battle_unit` read works on an enemy exactly as on a friendly.

**Evidence — the API dump `battle_manager.lua`:**

```
39  --- Returns the automatically-generated script_units collection object, containing a script_unit for every unit, corresponding to the local player's army.
41  function battle_manager:get_scriptunits_for_local_players_army() end
42  --- Returns the automatically-generated script_units collection object, containing a script_unit for every unit, for the local player's primary enemy army.
44  function battle_manager:get_scriptunits_for_main_enemy_army_to_local_player() end
```
and the general form:
```
14  --- Gets an automatically-generated script_units collection object containing a script_unit for every unit in the specified army. If no scriptunits collection can be found ... then false is returned.
15  ---@param alliance_id number #Alliance id. Alliances are specified by 1-based index, currently either 1 or 2.
16  ---@param army_id number #Army id, specified by 1-based index ...
19  function battle_manager:get_scriptunits_for_army(alliance_id, army_id, reinforcement_units_id) end
```

**Evidence — the shipped implementation `script/_lib/lib_battle_manager.lua`:**
```
450   function battle_manager:get_scriptunits_for_main_enemy_army_to_local_player()
451       return self:get_scriptunits_for_army(self:get_non_player_alliance_num(), 1);
```
```
810   return self:alliances():item(self:get_non_player_alliance_num());   -- get_non_player_alliance()
834   return self:get_non_player_alliance():armies():item(1);             -- get_first_non_player_army()
```
So the enemy collection is literally `get_scriptunits_for_army(<non-player alliance>, 1)` — i.e. it is *the same object type* the mod already consumes for its own army, just for the other alliance. `get_scriptunits_for_army` validates indices and returns `false` if the army is absent (`lib_battle_manager.lua:332-372`).

**Evidence — each `script_unit` exposes `.unit` and `.uc` (`script/_lib/lib_battle_script_unit.lua`):**
```
176   su.unit = unit;
177   su.uc   = create_unitcontroller(unit);
```
and the documented contract (`script_unit.lua` dump):
> "The scriptunit interface provides direct access to the @battle_unit and @battle_unitcontroller interfaces related to the unit at the unit (`<sunit_obj>.unit`) and uc (`<sunit_obj>.uc`) elements respectively."

**Evidence — everything you want to READ is on `battle_unit` and is side-agnostic** (`battle_unit.lua` dump; the doc text never qualifies by alliance except `is_visible_to_alliance`):
```
199  function battle_unit:is_valid_target() end                 -- "whether this unit is currently a valid target for enemies"
220  function battle_unit:is_in_melee() end
232  function battle_unit:number_of_men_alive() end
258  function battle_unit:unary_hitpoints() end
262  function battle_unit:is_wavering() end
266  function battle_unit:is_routing() end
278  function battle_unit:is_shattered() end
116  function battle_unit:position() end
158  function battle_unit:unit_in_range(target_unit) end
163  function battle_unit:unit_distance(target_unit) end
212  function battle_unit:is_visible_to_alliance(alliance) end
```

**Evidence — THE ENGINE'S OWN CORE SCRIPT READS ENEMY UNITS THIS WAY** (`script/_lib/lib_battle_manager.lua`, inside `start_engagement_monitor`; `main_enemy_army = self:get_first_non_player_army()` at line 4531):
```
4687    local enemy_units = main_enemy_army:units();
4689    for i = 1, enemy_units:count() do
4690        local current_unit = enemy_units:item(i);
4691        if current_unit:is_commanding_unit() then
4692            if current_unit:is_routing() or current_unit:is_shattered() then
```
and across *all* enemy armies:
```
4774    local enemy_armies = enemy_alliance:armies();
4776    for i = 1, enemy_armies:count() do
4777        local enemy_units = enemy_armies:item(i):units();
4779        for j = 1, enemy_units:count() do
4780            local current_unit = enemy_units:item(j);
4781            if not current_unit:is_commanding_unit() then ...
```
(`enemy_alliance = self:get_non_player_alliance()` at 4525.) The alternative enumerator `battle_army:units()` returns a `battle_units` collection (`battle_army.lua`: *"Creates and returns a battle_units object listing all units in the army"*), used above with `:count()`/`:item(i)`.

**Confidence: VERY HIGH (0.97).** Multiple independent confirmations: API dump, shipped implementation, and the engine's own use of the enemy read. Only the exact `battle_units` class doc page is not among the extracted dumps (see *Uncertainties*), but its two methods (`count`/`item`) and the `battle_unit` element type are proven by the engine's use at `lib_battle_manager.lua:4687-4697`.

---

## Q2. `perform_special_ability(key, target)` — what target types are accepted; can it be an enemy handle; how do you get one?

**Answer: YES.** The second argument is a **`battle_unit`** ("An optional unit target may be specified"). It is `nil`-optional and defaults to `nil`. It accepts **any** `battle_unit`, an enemy included — the engine applies the ability's own target rules (`target_enemies`, invalid-target flags) to decide legality, not the argument's side.

**Evidence — `battle_unitcontroller.lua` dump:**
```
85  --- Issues an order to the units associated with this unitcontroller to perform the supplied special ability. Special abilities are listed in the unit_special_abilities table. An optional unit target may be specified.
86  ---@param ability_key string #ability key
87  ---@param target_unit battle_unit? #optional, default value=nil target unit
88  function battle_unitcontroller:perform_special_ability(ability_key, target_unit) end
```
Queued form: `perform_special_ability_q(ability_key, target_unit)` (same doc). Ground form: `perform_special_ability_ground(ability_key, position, orientation_in_degrees, width_in_m)`.

**Evidence — VANILLA CASTS AT AN ENEMY UNIT WITH EXACTLY THIS CALL.** In `script/benchmarks/siege_benchmark/siege_benchmark.lua`, `sunit_ksl_*` are alliance 1 (Kislev) and `sunit_ogr_*` are alliance 2 (Ogres, the enemy) — built from `alliances:item(1)/:item(2)` → `:armies():item(1)` → `script_unit:new_by_reference(army, "ogr_04")`:
```
314     sunit_ksl_01.uc:perform_special_ability("wh3_main_spell_ice_ice_sheet", sunit_ogr_04.unit);
323     sunit_ksl_21.uc:perform_special_ability("wh3_main_spell_tempest_hailstorm", sunit_ogr_35.unit);
```
More enemy-targeted vanilla casts:
```
battle_benchmark/battle_benchmark.lua:381      sunit_ksl_01.uc:perform_special_ability("wh3_main_spell_ice_ice_sheet", sunit_kho_04.unit);
battle_benchmark_old/battle_benchmark.lua:278 sunit_kho_21.uc:perform_special_ability("wh3_main_character_abilities_gate_of_khorne", sunit_ksl_18.unit);
mom_benchmark/blackfire_pass.lua:210         sunit_tze_02.uc:perform_special_ability("wh_main_spell_fire_the_burning_head", sunit_grn_05.unit);
```
`sunit_kho_04.unit` is a `battle_unit` belonging to the *other* alliance. **This is the model to copy.**

**How an enemy handle is legally obtained (three routes, all legal):**
1. **Global enumerator** (Q1): `local e = bm:get_scriptunits_for_main_enemy_army_to_local_player(); ... e:item(i).unit`
   or `bm:get_scriptunits_for_army(bm:get_non_player_alliance_num(), k):item(i).unit`
   or `bm:get_first_non_player_army():units():item(i)`.
2. **Our own unit's live target** (Q3): `unit:current_target()` → the enemy `battle_unit` (already used by the mod today).
3. **The script_units collection itself** so you can iterate `:count()`/`:item(i)`.

**The `can_perform_special_ability` analogue:** the read lives on the **caster's** `battle_unit` (`battle_unit.lua`):
```
352  --- Returns whether the unit can perform the specified special ability. Valid special abilities are defined in the unit_special_abilities database table.
355  function battle_unit:can_perform_special_ability(special_ability_key_) end
```
It takes only the **key** (no target argument) and gates the caster's ownership/state — the mod already uses it in its readiness gate. So the fire is: check `unit:can_perform_special_ability(key)` on the caster, then `uc:perform_special_ability(key, enemy_unit)`.

**Confidence: VERY HIGH (0.95).** Signature is explicit; cross-alliance vanilla casts are on disk. Residual uncertainty only about whether some *specific* abilities add a hidden side/position precondition (see Q6).

---

## Q3. Does `battle_unit:current_target()` expose the enemy our unit is fighting — and is it reachable without a global enumerator?

**Answer: YES to both — and the mod already calls it.**

**Evidence — `battle_unit.lua` dump:**
```
312  --- Returns the battle_unit this unit is targeting. If no unit is being targeted then no value is returned.
313  ---@return battle_unit #target unit
314  function battle_unit:current_target() end
```
Doc wording ("no value is returned" when idle) matches the observed behaviour below: it returns the enemy `battle_unit` while the unit is attacking/fighting, `nil` otherwise.

**Evidence — the mod already uses it, live, in `measure_charge` (`zz_test_deadly_onslaught.lua`):**
```
3458    local ok_target, target = pcall(function() return unit:current_target() end)
3459    if ok_target and target ~= nil then
3460        m.has_target = true
...
3471        local ok_dist, dist = pcall(function() return unit:unit_distance(target) end)
```
So a `battle_unit` handle to the unit's current enemy target is **already successfully produced and even measured (`unit_distance`) inside the shipped mod**, and the mod's own comment confirms the interpretation:
```
2649 --   3. current_target()      - it has an enemy unit as its target
```
This kills the "no enemy-unit read" premise on its own: the read the mod needs is **already in the mod's hands** and is simply discarded after `m.has_target` is set.

Caveat: `current_target()` is only populated once the unit has an attack order / is engaged. It does **not** give a target at range before the order, and it does **not** enumerate all enemies. For "cast a hex on the nearest enemy" the global enumerator (Q1) is the right source; for "cast a hex on the enemy I am fighting" `current_target()` is the cheapest and is sufficient.

**Confidence: VERY HIGH (0.95)** for the API; **HIGH (0.9)** that it returns a fully usable enemy handle in-battle (proven by the mod's existing `unit_distance(target)` — the same handle flows straight into `perform_special_ability`).

---

## Q4. The AI's own ability-casting call chain (quoted), when it hexes a player unit

**Answer:** the *real-time tactical AI* that fires hexes is **native engine code, not Lua** — there is **no `perform_special_ability` call anywhere in the AI's Lua planner**. What the data tables prove is that the engine selects abilities by the `ai_usage` column; what the vanilla Lua proves is the exact **cast call the engine uses when scripting must fire an ability**, which is the pattern the mod can copy.

**4a. The engine's own ability-AI is data-driven — `unit_spec_abil.tsv` column `ai_usage` (col 33).** Every ability carries the engine's usage class. Counts over the 3 174 rows:

```
ai_usage == hex_melee        119
ai_usage == hex_melee_area    62
ai_usage == hex_morale        19
ai_usage == hex_speed_*       27+
ai_usage == hex_ranged_summon 43
ai_usage == aoe_bombardment  111
ai_usage == vortex_wind       33   ...
```
Among `target_enemies = true` rows the top classes are `hex_melee` (97), `aoe_bombardment` (89), `vortex_breath` (39), `hex_ranged_summon` (37), `hex_melee_area` (33), `hex_morale` (19)… **`hex_melee` alone = 97 — the "~98 broken abilities" are exactly the engine's `hex_melee` family.** The engine's AI decides *when/where* from these classes in C++; that code is not shipped as Lua and cannot be quoted.

**4b. The AI-planner Lua does movement/attack targeting, NOT ability casting.** `%TEMP%\wh3\ai_planner.lua` exposes only: `add_units`, `remove_units`, `defend_position`, `attack_unit`, `rush_unit`, `move_to_position`, `clear_objective` — **no ability method.** Its engine-side targeting model is mirrored in `script/_lib/lib_battle_script_ai_planner.lua`, which acquires the closest enemy and orders an attack (this is the "how does the AI pick a target" chain, quoted):
```
647   local closest_enemy = nil
648   local closest_enemy_dist = 5000
652       local curr_enemy_sunit = enemy_force[i];                 -- enemy_force: script_units / table of script_unit
655           local closest_standing_unit = get_closest_standing_unit(self.sunit_list, curr_enemy_sunit.unit:position());
661               closest_enemy = curr_enemy_sunit;                -- picks a script_unit of the ENEMY
...
700   self.current_target = closest_enemy;
```
and the attack order itself:
```
971   function script_ai_planner:attack_unit(unit, reorder)
988       self.planner:attack_unit(unit);        -- engine ai_planner:attack_unit(target battle_unit)
```
So the AI's "I have a handle to an enemy unit" is the same `enemy_scriptunit.unit` a script would read.

**4c. The engine's shipped Lua cast chain for abilities is the `uc:perform_special_ability(key, target_unit)` call** — the benchmarks (Q2) are the canonical examples. The **army-ability** variant targets a *position*, not a unit (`battle_army.lua`):
```
--- Instructs the army to target a special ability at a supplied position.
---@param key string #Key of the special ability, from the army_special_abilities database table.
---@param position battle_vector #Position to target the special ability at.
function battle_army:use_special_ability(key, position, bearing, width) end
```
called from the shipped framework (`script/_lib/lib_generated_battle.lua`):
```
3484    army:use_special_ability(special_ability_key, position, orientation, width);
```

**Named functions in the AI/engine chain:** `battle_manager:get_first_non_player_army()` → `battle_alliance:armies()` → `battle_army:units()` → `battle_units:item(i)` (enemy `battle_unit`); for Lua-side AI targeting, `script_ai_planner:attack_unit/rush_unit` → `ai_planner:attack_unit(target)`; for an actual cast, `battle_unitcontroller:perform_special_ability(key, target_unit)` (or `battle_army:use_special_ability(key, position, …)`).

**Confidence: HIGH (0.9)** that the ability-casting AI is native C++ (proven by *absence* of any cast call in `ai_planner.lua` / `lib_battle_script_ai_planner.lua`, plus the `ai_usage` column existing precisely to parameterise that native AI). **VERY HIGH (0.97)** on the Lua cast call the mod should copy.

---

## Q5. Is there an aim/use path on the unit controller that takes an enemy target and that scripts may call?

**Answer: YES — several, on `battle_unitcontroller` (reached via `script_unit.uc` or `battle_army:create_unit_controller()`):**

```
battle_unitcontroller.lua
 87  function battle_unitcontroller:perform_special_ability(ability_key, target_unit) end          -- unit target (nil-optional)
 93  function battle_unitcontroller:perform_special_ability_q(ability_key, target_unit) end        -- queued
100  function battle_unitcontroller:perform_special_ability_ground(ability_key, position, orientation_in_degrees, width_in_m) end
231  function battle_unitcontroller:attack_unit(target_unit, use_primary_attack, move_fast) end     -- target_unit battle_unit
237  function battle_unitcontroller:attack_unit_q(target_unit, use_primary_attack, move_fast) end
```
`attack_unit` is the clearest "aim at this enemy" primitive and its enemy use is also demonstrated in vanilla:
```
siege_benchmark.lua:314     sunit_ogr_20.uc:attack_unit(sunit_ksl_06.unit, true, true);   -- cross-alliance
battle_benchmark.lua:292-293 sunit_ksl_19.uc:attack_unit(sunit_kho_04.unit, true, true);
01_prologue_intro/battle_declarations.lua:722  current_sunit.uc:attack_unit(current_sunit.initial_attack_target.unit, true, true);
```
At the script_unit level there is also a self-driven enemy attack:
```
script_unit.lua:375  function script_unit:start_attack_closest_enemy(interval, debug) end
      -- "Instructs this scriptunit to attack the closest enemy unit under full script control."
```
and a collection-level one at `lib_battle_script_unit.lua:3886/3898` (`controlled_sunit.uc:attack_unit(enemy_sunit.unit, true, should_run)`).

**There is no separate `set_target`/`aim` method** — the "aim" is the `target_unit` argument of `perform_special_ability` / `attack_unit`. `battle_unit:current_target()` is the **read** side of the same relationship.

**Confidence: VERY HIGH (0.96).**

---

## Q6. Restrictions — what the game refuses, and the targeting-column semantics

**Answer: the restrictions are per-ability properties, not a "scripts may not target enemies" rule.** The engine validates the *target* against the ability's own DB flags; a wrong target is refused (the engine's refusal text is the `..."does not support this special ability"` family the mod already logs), but the argument being an *enemy* is exactly what `target_enemies` abilities are for.

**6a. The targeting columns (`unit_spec_abil.tsv`, header quoted):**
```
key  active_time  recharge_time  num_uses  effect_range  affect_self  num_effected_friendly_units
num_effected_enemy_units  update_targets_every_frame  initial_recharge  activated_projectile
target_friends  target_enemies  target_ground  target_intercept_range  always_affect_self
only_affect_target  wind_up_time  passive  unique_id ... (target_ground_under_allies, target_ground_under_enemies, ...)
```
Column number (1-based, as in the header above) → meaning:

| col | column | meaning for us |
|---|---|---|
| 8 | `num_effected_enemy_units` | −1 = "all enemies in range", 0 = none, >0 = up to N |
| 12 | `target_friends` | may it be aimed at a friendly unit? |
| **13** | **`target_enemies`** | **may it be aimed at an enemy unit?** |
| 14 | `target_ground` | may it be aimed at a ground point? |
| 15 | `target_intercept_range` | intercept/seek range for the target |
| 17 | `only_affect_target` | single-target vs area |
| 42 / 43 | `target_ground_under_allies` / `_under_enemies` | ground casts that must sit under an army |
| 33 | `ai_usage` | engine AI class (`hex_melee`, `hex_melee_area`, `aoe_bombardment`, `vortex_wind`, `debuff_unit`, `buff_self`, …) |

Headline counts over the table: **`target_enemies=true`: 830 rows; `target_friends=true`: 368; `target_ground=true`: 753; of the 354 `ai_usage=hex_*` rows, 252 are `target_enemies`.** Worked examples (values at the columns above):
```
wh3_main_spell_ice_ice_sheet         target_friends=false target_enemies=false target_ground=true  (ai_usage=hex_speed_area, ground_under_enemies=true)
wh3_main_spell_tempest_hailstorm     target_friends=false target_enemies=true  target_ground=true  (ai_usage=aoe_bombardment)
wh_main_spell_fire_the_burning_head  target_friends=false target_enemies=true  target_ground=true  (ai_usage=vortex_wind)
wh2_dlc09_character_abilities_curse_of_djaf  target_enemies=true target_ground=true (ai_usage=hex_melee_area)
wh_main_character_abilities_deadly_onslaught target_enemies=false target_ground=false affect_self=true (ai_usage=augment_charge_self) -- a SELF buff, not a hex
```
**Consequence:** abilities with `target_enemies=true` (and/or `target_ground=true` with `target_ground_under_enemies=true`) are the ones that need an enemy unit / enemy-ground point; `target_enemies=false, target_ground=false, affect_self=true` are self-casts (what the mod already does). The triage's "enemy *unit*" reading (row 29-31 of `WH3_remaining_triage.md`) is too strict: ground-under-enemies casts only need an enemy **position**, which `enemy_unit:position()` supplies directly.

**6b. Invalid-target flags (`special_ability_to_invalid_target_flags_tables.tsv`, 10 000+ rows) — these govern the TARGET, and the engine once enabled the ability only when the target satisfies them:**
```
invalid_target                  special_ability
ground_unit                     wh2_main_spell_high_magic_tempest
flying_currently                wh3_main_spell_ice_ice_sheet
on_a_platform                   wh3_main_spell_ice_ice_sheet
flying_currently                wh_main_spell_fire_the_burning_head
```
i.e. ice sheet cannot be aimed at a currently-flying unit; tempest/hailstorm requires a ground unit; etc. These are exactly the constraints the engine applies to whatever `target_unit` you pass — so passing the *wrong kind* of enemy yields a refusal, passing a valid one is accepted.

**6c. Invalid-usage flags (`special_ability_to_invalid_usage_flags_tables.tsv`)** cover caster-state preconditions (`enemies_in_intercept_range`, `cannot_find_enemies_in_intercept_range`, `allies_in_intercept_range`, …) — again per-ability, not a blanket script restriction.

**6d. Ownership.** A cast only works for an ability the **casting unit owns** (`unit_special_abilities` / the mod's existing `can_perform_special_ability` + `owned_*_special_abilities` path; `land_abil.tsv` maps ability→unit). This is unchanged by target side.

**6e. Control.** `perform_special_ability` is an order issued through *the caster's* controller. The mod already fires its own units' abilities this way (it only takes control for the ally-targeting block; `RELEASE_CONTROL_AFTER`). You do **not** need control of — or any handle to — the *enemy's* controller; the enemy only appears as the **argument**. (Confirmed by the benchmarks, which cast with the caster's own `sunit.uc` and pass the other alliance's unit.)

**Confidence: HIGH (0.9).** The column semantics are unambiguous from header + worked examples + `ai_usage` classes. Residual: the exact engine error string for a *side*-wrong target is not separately captured (only the `does not support this special ability` text is proven in the mod's logs); a probe (below) settles it.

---

## VERDICT

**Enemy targeting IS achievable from a battle script.**

The script layer exposes an enemy-script-unit enumerator (`get_scriptunits_for_main_enemy_army_to_local_player`, `get_scriptunits_for_army`, `get_first_non_player_army():units()`) whose items are fully readable `battle_unit`s; `perform_special_ability(key, target_unit)` accepts a `battle_unit` target and vanilla casts enemy-targeted spells at the enemy with exactly that call; `current_target()` already hands the mod its enemy. The prior "no enemy-unit read" limit applies only to the **UI-card** layer and should be corrected in the triage: the group-A auto-exclusion reason (97 rows) is invalid at the script layer.

### Concrete recipe (exact calls, in order)

```lua
-- 0) once per battle (conflict phase or later; collections are built during setup_battle):
local enemy_sunits = bm:get_scriptunits_for_main_enemy_army_to_local_player()
--   (or, for any enemy army: bm:get_scriptunits_for_army(bm:get_non_player_alliance_num(), k))

-- 1) per (firing unit, hex key):
local caster = unit                      -- the battle_unit we are casting FROM
if not caster:can_perform_special_ability(key) then return end   -- caster-side readiness (unchanged)

-- 2) choose the enemy target handle, cheapest first:
local target = caster:current_target()                  -- the enemy it is already fighting (mod already reads this)
if target == nil and enemy_sunits and enemy_sunits:count() > 0 then
    target = enemy_sunits:item(1).unit                  -- or nearest by :position():distance(...)
end
if target == nil then return end                        -- no enemy -> no cast (fail-open, as today)

-- 3) fire at the enemy unit (unit-targeted hex):
local ok, err = pcall(function()
    caster_uc:perform_special_ability(key, target)      -- caster_uc = the CASTER's controller (script_unit.uc)
end)

-- 3b) for a ground-under-enemies hex (target_ground + target_ground_under_enemies=true), aim at the ENEMY's position:
--     caster_uc:perform_special_ability_ground(key, target:position(), 0, 0)
```

**Where this plugs into the existing mod:** `attempt_activation(script_unit, unit, ability_key, reason, ui_id, marker, quiet, target)` (`zz_test_deadly_onslaught.lua:4156`) **already takes a `target` and already does `uc:perform_special_ability(ability_key, target or unit)` (line 4342)**. `measure_charge` already computes `unit:current_target()` (line 3458) and then discards it. The minimal change is: for a `target_enemies`/`target_ground_under_enemies` key, populate that `target` from `current_target()` (or the enemy collection) instead of only from the ally evaluator. The ground path also already exists (`FOURTH.ground_cast`, `FOURTH.is_ground_key`, line 4127) and would only need to pass `target:position()` instead of the caster's own position.

### Cheapest in-battle probe (throwaway, one file — NOT built here)

Per the project's throwaway-probe convention (`script/battle/mod/zz_probe_<topic>.lua`, own log beside `Warhammer3.exe`, console hook on shift+F3 plus a periodic safety pass, hard pass cap), design `zz_probe_enemy_target.lua`:

- Register `bm:repeat_callback(probe_tick, 1000, "zz_probe_enemy_target_poll")`; arm the first time `bm:is_conflict_phase()` is true; hard-stop after 25 polls. Read everything through `pcall`; log names via `safe_len`/copy-first idioms.
- Each poll writes exactly these lines (one block per poll):
  1. `probe: enemy_collection table=<t|f> count=<n or ERR>`  ← from `bm:get_scriptunits_for_main_enemy_army_to_local_player()` (`false` means "no collection" — a real result, log it).
  2. `probe: E1 type=<battle_unit:type()> men=<number_of_men_alive> hp=<unary_hitpoints> melee=<is_in_melee> valid=<is_valid_target> x=<position()> living=<n>`
  3. `probe: M1 type=<battle_unit:type()> target_type=<current_target():type() or nil> target_dist=<unit_distance(target) or -1>`  ← proves `current_target()` yields the enemy.
  4. For the first enemy-targeted key the caster owns: `probe: CAST key=<key> target_type=<...> accepted=<t|f> err=<err or ->`  ← `pcall(uc:perform_special_ability(key, enemy_target))`. To pick the key, iterate `unit:owned_non_passive_special_abilities()` and try each; one `CAST` line per key, cap 4.
  5. `probe: controls enemy_read=<t|f> current_target=<t|f> enemy_cast_accepted=<t|f>`
- **Success criterion:** line 1 `table=true count>=1`; line 2 a full enemy read stack (non-`ERR`); line 3 `target_type` non-nil while the unit is engaged; line 4 at least one `accepted=true` with `err=-` for a `target_enemies` key against the enemy handle.
- One manual hook `zz_probe_enemy_target()` to re-run all 25 polls from the console.

### What remains uncertain

1. **The `battle_units` class page is not among the extracted dumps.** `:count()`/`:item(i)` and element type `battle_unit` are proven by the engine's own use (`lib_battle_manager.lua:4687-4697`), but I could not quote the class doc itself (no `battle_alliance.lua`/`battle_units.lua` in `%TEMP%\wh3` or the archive). If `battle_army:units()` ever returns something odd, prefer the `script_units` enumerator (`get_scriptunits_for_main_enemy_army_to_local_player`), which is fully documented.
2. **The exact engine error string for a *side*-wrong target is not in hand** — only the "does not support this special ability" refusal (a cooldown/ownership gate) is proven in the mod's logs. The probe's `err=<...>` line captures it.
3. **Whether every `target_enemies` ability also constrains the target further** (invalid-target flags: flying/on-platform/ground-unit, etc., Q6b) — expected, per-ability, and not a blocker: just pick a legal target (the probe reveals refusals).
4. **`get_scriptunits_for_main_enemy_army_to_local_player()` returns only the enemy alliance's army #1** at the moment it is called (reinforcing/extra enemy armies need `get_scriptunits_for_army` iterated over the non-player alliance's armies). Not a correctness risk if the code pages through `battle_alliance:armies():count()`.
5. **Timing:** the collections exist once `setup_battle` has built them; call in conflict phase (or later) — the shipped Lua guards against a too-early call with a `script_error` (`lib_battle_manager.lua:351`). The probe arms on conflict phase, which avoids this.

---
---

# §ROUND 4 — EXHAUSTIVE ROUTE SWEEP (2026-10-10)

**Question:** *every* documented script route by which an enemy-targeted ability could be made to land — enumerated, then each surviving candidate fired as its own labelled route with paired caster/target effect-count deltas and a machine-checked `landed=yes|no`.

**Starting facts (proven live, rounds 1-3, not re-established):**
`uc:perform_special_ability(key, enemy_battle_unit)` → `accepted=true err=-` yet **inert**; the target's and the caster's active-effect counts never move; `can_perform_special_ability` stays `true` (no cooldown consumed); `script_unit`/`nil` targets are Lua **type errors**; `perform_special_ability_ground(key, enemy_pos, 0, 0)` is likewise inert; **no cooldown read exists** anywhere on the unit or controller; the user's **manual** cast of the same ability works.

---

## Lead 1 — the vanilla benchmark's exact cast form (confidence: HIGH it is the same form; LOW-MED it differs)

The benchmark casts at an enemy by passing a **`battle_unit` obtained from a `script_unit`**:

```
siege_benchmark.lua:314   sunit_ksl_01.uc:perform_special_ability("wh3_main_spell_ice_ice_sheet", sunit_ogr_04.unit);
siege_benchmark.lua:323   sunit_ksl_21.uc:perform_special_ability("wh3_main_spell_tempest_hailstorm", sunit_ogr_35.unit);
```
`ksl_*` are alliance 1, `ogr_*` alliance 2 (the enemy). The handles come from the generated-battle framework:
```
siege_benchmark.lua:21    sunit_ksl_01 = script_unit:new_by_reference(army_ksl_01, "ksl_01");
siege_benchmark.lua:51    sunit_ogr_04 = script_unit:new_by_reference(army_ogr_01, "ogr_04");
```
More enemy-targeted vanilla casts (same call, cross-alliance):
```
battle_benchmark/battle_benchmark.lua:381        sunit_ksl_01.uc:perform_special_ability("wh3_main_spell_ice_ice_sheet", sunit_kho_04.unit);
battle_benchmark_old/battle_benchmark.lua:278    sunit_kho_21.uc:perform_special_ability("wh3_main_character_abilities_gate_of_khorne", sunit_ksl_18.unit);
mom_benchmark/blackfire_pass.lua:210             sunit_tze_02.uc:perform_special_ability("wh_main_spell_fire_the_burning_head", sunit_grn_05.unit);
skaven_benchmark/skaven_benchmark.lua:246        sunit_skv_21.uc:perform_special_ability("wh2_main_spell_plague_plague", sunit_lzd_05.unit);
fallen_gates/battle_benchmark.lua:217            sunit_hef_17.uc:perform_special_ability("wh2_main_unit_abilities_hef_sundragon_breath", sunit_lzd_02.unit);
```
**Benchmark form, distilled:** caster's `script_unit.uc` + target's `script_unit.unit`, where the caster `script_unit` came from the framework (`script_unit:new_by_reference(army, ref)` → `.uc = create_unitcontroller(unit)`, `lib_battle_script_unit.lua:176-177`).

**Two candidate differences were therefore isolated and tested as R1:**
1. the **controller provenance** — the benchmark's `.uc` is created by the `script_unit` framework, while round 3 used the auto-generated collection's `su.uc`; and
2. a **fresh `script_unit` wrapper** on the *target* (`script_unit:new(enemy_battle_unit).unit`), mirroring `sunit_ogr_04.unit`.
R1 re-fetches the caster from `bm:get_scriptunits_for_local_players_army()` **immediately before the cast** (a stale controller being a prime suspect) and passes a freshly wrapped target unit.

*Note:* the round-3 probe already re-read `su.uc`/`su.unit` from the enumerator each poll, so the **only** genuinely new variable R1 adds is the fresh wrapper + same-tick fetch. Confidence that R1 alone explains the inertness: **LOW (~0.15)** — but it is the explicit benchmark mirror and had to be run.

---

## Lead 2 — `perform_special_ability_q` (the queued form) — confidence MED (~0.3)

Documented signature (`battle_unitcontroller.lua`):
```
 89  --- Issues a queued order to the units associated with this unitcontroller to perform the supplied special ability. ...
 90  --- An optional unit target may be specified with the second argument.
 91  ---@param ability_key string #ability key
 92  ---@param target_unit battle_unit? #optional, default value=nil target unit
 93  function battle_unitcontroller:perform_special_ability_q(ability_key, target_unit) end
```
Identical argument contract to the synchronous form, but the order starts *after the current order completes*. Plausible that the synchronous form's order is immediately superseded by the unit's existing order/AI state, whereas a queued order survives to execute. **Tested as R2** — `uc:perform_special_ability_q(key, enemy_battle_unit)`.

---

## Lead 3 — `battle_army:use_special_ability(key, position, …)` — confidence MED (~0.35 that it even applies to a unit ability)

Documented signature (`battle_army.lua:122-127`):
```
122  --- Instructs the army to target a special ability at a supplied position.
123  ---@param key string #Key of the special ability, from the army_special_abilities database table.
124  ---@param position battle_vector #Position to target the special ability at.
125  ---@param bearing number? #optional ... not required for all abilities.
126  ---@param width number? #optional ... not required for all abilities.
127  function battle_army:use_special_ability(key, position, bearing, width) end
```
It is the **army-ability** entry point (the right-hand army-ability bar), and the whole shipped call path is the framework wrapper (`lib_generated_battle.lua:3425-3495`, `generated_army:use_army_special_ability_on_message`), whose own doc says the key is from `army_special_abilities`:
```
3484   army:use_special_ability(special_ability_key, position, orientation, width);
```
It takes a **position, not a unit**, so it is a poor fit for `wh_main_hero_abilities_accusation` (a *unit* ability whose `unit_spec_abil` row has `target_ground=false`). It is nevertheless a documented, distinct route and had to be tried. **Tested as R3** — `caster.unit:army():use_special_ability(key, enemy_position, 0, 0)`.

---

## Lead 4 — EVERY ability/target/order/cast method on the three interfaces (exhaustive enumeration)

Enumerated from `battle_unitcontroller.lua`, `battle_unit.lua`, `script_unit.lua` (+ `battle_army.lua`, `battle_manager.lua`, `battle.lua`). "Route" column names the round-4 route that exercised it; "—" = not a cast/targeting entry point, or a write deliberately NOT called.

**`battle_unitcontroller`** (reached via `script_unit.uc`, `battle_army:create_unit_controller()`, `script_units:get_unitcontroller()`):

| line | method | signature | route |
|---|---|---|---|
| 87 | `perform_special_ability` | `(ability_key, target_unit battle_unit?)` | R1/R4/R5/R6 (+ inert control in r3) |
| 93 | `perform_special_ability_q` | `(ability_key, target_unit battle_unit?)` | **R2** |
| 100 | `perform_special_ability_ground` | `(ability_key, position, orientation_in_degrees?, width_in_m?)` | inert in r3 |
| 104 | `reset_ability_cooldown` | `(ability_key)` | **forbidden write — never called** |
| 108 | `reset_ability_number_of_uses` | `(ability_key)` | forbidden write |
| 112/117 | `change_shot_type` / `_q` | `(shot_type)` | not a cast |
| 122 | `change_behaviour_active` | `(behaviour_key, is_active)` | not a cast |
| 126/130 | `melee` / `fire_at_will` | `(bool)` | not a cast |
| 133/136/139 | `halt` / `withdraw` / `withdraw_q` | — | not a cast |
| 169-194 | `goto_location*`, `teleport_to_location` | `(position, …)` | forbidden (movement) |
| **231/237** | **`attack_unit` / `attack_unit_q`** | **`(target_unit battle_unit, use_primary_attack=true, move_fast=false)` — "must be an enemy unit"** | **R5** |
| 243-286 | `attack_building*`, `interact_with_deployable*`, `besiege_building*`, `defend_building*`, `leave_building` | — | n/a |
| 291/296 | `attack_location` / `_q` | `(position, move_fast)` | n/a |
| 302/309 | `attack_line` / `_q` | `(position_a, position_b, move_fast)` | n/a |
| 7-24 | `clear_all`, `add_all_units`, `add_units`, `add_group`, `take_control`, `release_control` | — | **R4 uses `take_control`/`release_control`** |

**`battle_unit`** (every ability/target read + the writes):

| line | method | route |
|---|---|---|
| **355** | `can_perform_special_ability(special_ability_key_)` — **readiness gate, key only** | read on every route (CANPOST) |
| 372/376/380/384 | `owned_passive_special_abilities`, `owned_non_passive_special_abilities`, `owned_special_abilities`, `num_special_abilities` | read (key discovery) |
| 509 | `can_use_magic()` | read |
| 359/363/368 | `disable_passive_special_abilities`, `disable_non_passive_special_abilities`, `disable_special_ability` | forbidden writes |
| 513 | `set_special_abilities_flags(flag_key)` | forbidden write |
| **314** | `current_target()` → enemy `battle_unit` | read (R6 candidates) |
| **158/163** | `unit_in_range(target)`, `unit_distance(target)` | read (R6 reach test) |
| 199 | `is_valid_target()` | read |
| 300/304/308 | `left_flank_threat`, `right_flank_threat`, `rear_threat` | read (unused) |
| 552 | `select_in_ui()` | forbidden write |

**`script_unit` — there is NO ability method on `script_unit` itself** (casts always go through `.uc`). The targeting/order methods are:

| line | method | route |
|---|---|---|
| 233/236 | `take_control()` / `release_control()` | R4 (via `uc`) |
| **375** | `start_attack_closest_enemy(interval=10000, debug=false)` — "attack the closest enemy unit under full script control … continually re-acquire" | **R5 motif** |
| 379 | `stop_attack_closest_enemy(reason)` | — |
| 685/688 | (`script_units`) `attack_enemy_scriptunits` / `stop_attack_enemy_scriptunits` | — |
| 677/680 | (`script_units`) `start_kill_aura` / `stop_kill_aura` | — |

**`battle_army`:** 36 `create_unit_controller()`; **127 `use_special_ability(key, position, bearing, width)`** → R3.
**`battle_manager`:** 19 `get_scriptunits_for_army`, 41 `get_scriptunits_for_local_players_army`, 44 `get_scriptunits_for_main_enemy_army_to_local_player`; **227 `register_command_handler_callback(command, callback, callback_name)`** → the command-event instrument.
**`battle`:** **135 `"Special Ability"` command event** ("A command to use a special ability has been issued"; `event:get_string1()` = ability name); 573 `set_special_abilities_flags`; 578/581 `disable_all_abilities`/`enable_all_abilities`; 150 `register_command_handler`; 91 `register_input_handler`.

**Confidence that this list is complete for "ability/target/order/cast": VERY HIGH (0.95)** — it is a straight read of the three generated interface dumps, and the only cast entry points anywhere are the three `perform_special_ability*` methods plus `battle_army:use_special_ability`.

---

## Lead 5 — the manual click path (which provably works): quoted ground truth

The player's manual cast is **not Lua script — it is the compiled UI binding a button to a C++ context callback.** The interface layout that draws and wires the button (`…\research\wh3_layouts\ui\battle ui\hud_battle.twui.xml`) is explicit:

```
3985   id="button_ability"
3994   <callbackwithcontextlist>
3995       <callback_with_context
3996           callback_id="BattleSpecialAbilityButton"
3997           context_object_id="CcoBattleAbility"/>
```
So clicking an ability icon fires the engine callback **`BattleSpecialAbilityButton`** against the **`CcoBattleAbility`** context object. The button *parent* (the wheel) binds `BattleAbilityHolder`, and the army-ability parent binds `BattleArmyAbilityHolder`:
```
748    <callback_with_context callbacks...>
749        <callback_with_context callback_id="BattleAbilityHolder"/>          (ability_parent)
1144       <callback_with_context callback_id="BattleArmyAbilityHolder"/>      (army_ability_parent)
```
The layout also carries the *targeting-state* sub-components the engine drives while the player aims — `label_invalid_ability_target`, `invalid_target_docker`, `icon_target_self` (hud_battle.twui.xml:266, 310, 417) — i.e. the engine itself decides legality and paints the cursor.

The **script-visible** edge of this path is only the *identification* of a button, never its trigger (`lib_battle_ui.lua:990`):
```
990    if uic_button and string.len(tostring(uic_button:InterfaceFunction("AbilityKeyForScript"))) > 3 then
           pulse_uicomponent(uic_button, value, pulse_strength or self.button_pulse_strength);
```
`uicomponent.lua` does expose `SimulateLClick`/`SimulateRClick` — but those **synthesise a mouse input**, which would re-enter the same C++ callback and is a *UI write*, not an ability API; the probe deliberately does not use them.

**Conclusion (confidence VERY HIGH, 0.96):** the manual path resolves through the native `CcoBattleAbility` / `BattleSpecialAbilityButton` binding and **has no Lua call equivalent**. The nearest thing to it that a script can call is exactly the benchmark form (Lead 1). So the manual cast proves the *ability* is fine but tells us nothing about a *script* entry point beyond what the benchmarks already show — which is why every script form is being swept.

---

## Lead 6 — attack-order / legitimisation helpers, and the command-event instrument (confidence HIGH, 0.85)

`Accusation` is `ai_usage = hex_melee` with `target_intercept_range = 75` and `target_ground = false` (`unit_spec_abil.tsv`). A melee-classed hex plausibly needs the caster **ordered in on the target** before it will apply. The shipped engine's own "acquire a nearby enemy and attack it" loop is:
```
lib_battle_script_ai_planner.lua / lib_battle_script_unit.lua:1928   self.uc:attack_unit(enemy_unit, true, true);
```
and the unit-controller doc for `attack_unit` (battle_unitcontroller.lua:227-231) says the target **"must be an enemy unit"** — a first-class enemy-targeting order that *provably* works. Two routes follow from this:
- **R5** — `uc:attack_unit(enemy, true, true)` then `uc:perform_special_ability(key, enemy)`.
- **R6** — cast only once `unit:unit_in_range(enemy)`/`unit_distance ≤ 75`/in-melee is true, i.e. the target is inside the ability's own 75 m intercept range (round 3 fired ~50-80 m out, at the edge of that window).

**The command-event instrument.** `battle.lua:135` documents a `"Special Ability"` command event fired when *the player or script* issues an ability command, carrying the ability name; `battle_manager:register_command_handler_callback("Special Ability", cb, name)` (battle_manager.lua:227) subscribes to it. The probe registers it, so the log will contain `CMD event=SpecialAbility key=…` **iff the engine genuinely registered an ability command** — including the user's manual cast. This separates "the call reached the engine" from "the call was swallowed", independently of the effect-count signal.

---

## The Round-4 probe — six labelled routes, one cast each

Probe: `script\battle\mod\zz_probe_enemy_target.lua` (round 3 → round 4). Same discipline: conflict-phase gate (logs name **and** boolean), ≥15 s between casts, ≤6 casts, `pcall` around every engine touch, own flushed log, console hook `zz_probe_enemy_target_status()`, **no** forbidden write. The old log is rotated aside before a run.

| route | kind | what it tests (the distinct call) | hypothesis prior |
|---|---|---|---|
| `bench_fresh` | `unit` | caster **re-fetched this instant** from `get_scriptunits_for_local_players_army()`; its `.uc`/`.unit`; target = `script_unit:new(enemy).unit` — the benchmark mirror | low |
| `queued_q` | `q` | `uc:perform_special_ability_q(key, enemy_battle_unit)` — the queued form | med |
| `army_use` | `army` | `caster.unit:army():use_special_ability(key, enemy_pos, 0, 0)` — the army-level form | med |
| `take_control` | `takecast` | the main mod's **own proven working shape**: `uc:take_control()` → cast → `uc:release_control()` | **med-high** |
| `attack_then_cast` | `attackcast` | `uc:attack_unit(enemy,true,true)` **then** `uc:perform_special_ability(key, enemy)` (hex_melee legitimisation) | med |
| `in_range_cast` | `incast` | fire only while the enemy is inside the ability's own reach (`unit_in_range` / `unit_distance ≤ 75` / in melee); defers up to 40 s | med |

Per cast the probe writes, and the log is machine-checkable:
```
TRY   route=<l> kind=<k> key=<key> target=<desc> can=<b> accepted=<b> err=<..>
ORDER route=<l> issued=<take_control|attack_unit|release_control> ok=<b> err=<..>     (R4/R5 only)
CANPOST route=<l> can_after=<b>            (false ⇒ the cast consumed the cooldown)
SELF  route=<l> before=<n> after=<n> delta=<n> state=".."
EFF   route=<l> key=.. target=.. before=<n> after=<n> delta=<n> effstate=.. hp=..->.. men=..->..
RESULT route=<l> landed=<yes|no> self_delta=<n> target_delta=<n> can_after=<b>
CMD   event=SpecialAbility key=<name>      (the engine's own ability-command event)
```
`landed=yes` ⇔ the **target enemy's** `ActiveEffectList(true).Size` changed (or `hp`/`men` moved); a self-move is reported separately. **Only two routes issue one legitimate ORDER each** (`take_control`, `attack_unit`) — that order *is* the variable under test; the forbidden-write family (reset cooldown, select, context, kill/heal/teleport) is never called and a trip counter guards it.

**Offline validation:** `mock_et4_prelude.lua` + `smoke_probe_et4.py` drive all 6 routes against mock handles — **SMOKE TEST PASSED** (all 6 routes fire once; `landed=yes` on the enemy and `landed=no` both produced; the SELF delta and the `in_range` defer path exercised; the command-event listener registered and fired; **zero forbidden writes**).

---

## Build provenance

| item | value |
|---|---|
| probe pack | `zz_probe_enemy_target.pack` (Movie, one file `script/battle/mod/zz_probe_enemy_target.lua`, 40 481 B) |
| **new pack md5 (round 4)** | **`e21411bdd306db0e520f4e0b19a0244a`** (dist + installed identical) |
| previous pack md5 (round 3) | `5b016e666c58a1f8eab6683f6907f408` |
| **main mod pack md5 before → after** | `d83c5f93539d770fd6003cf91ce73e2d` → `d83c5f93539d770fd6003cf91ce73e2d` (**unchanged**) |
| main mod source md5 before → after | `a95832601f6223fcafdb02fd8eb13cf4` → `a95832601f6223fcafdb02fd8eb13cf4` (**unchanged**) |
| probe source md5 | `d54a09bc7657ef302cd4bbc7cecb6b4d` |
| installed to | `…\Total War WARHAMMER III\data\zz_probe_enemy_target.pack` |

Installed-pack independent verification (`verify_probe_enemy_target_installed.py`): pack contains **only** the probe file, byte-identical to source, all round-4 tokens present, no main-mod path — **VERIFY OK**.

---

## Run instructions (user)

1. **Rotate / start clean** — the previous log is already moved to `zz_probe_enemy_target_log_round3.txt`. The probe will create a fresh `zz_probe_enemy_target_log.txt`.
2. **Fully exit the game and the launcher**, then relaunch (the pack in `data/` changed).
3. Start a battle and bring it to the **conflict phase** ("Deployed"): a **Witch Hunter with Accusation** against **mixed enemy units** (a character plus infantry is ideal — the routes cycle enemy #1/#2/#3).
4. **Let it run ~2 minutes** (the probe polls every 2 s; the six casts land at ~0 s, 15 s, 30 s, 45 s, 60 s and 75 s, the last one deferring up to 40 s until the enemy is in range).
5. Optional: **also manually click Accusation on an enemy** during that window — the probe's command-event listener will log a `CMD event=SpecialAbility …` line for your manual cast, giving a control against the scripted ones.
6. Read `zz_probe_enemy_target_log.txt` next to `Warhammer3.exe`. Console hook: `zz_probe_enemy_target_status()`.

**How to read the result:** for each route, `RESULT route=<name> landed=yes|no`. A `landed=yes` on any route is the answer — that route's call form works and the mod can adopt it. `CMD event=SpecialAbility` with no `landed=yes` means the engine accepted the command but did not apply it for that key/target. All six `landed=no` means no cheap script route lands this particular unit-targeted hex — and the *reason* will show in the paired deltas (target inert vs. cast self-applied vs. no command raised).

### Confidence summary for the round-4 leads
- Enemy enumeration/reads reaching a real `battle_unit`: **VERY HIGH (0.97)** (proven live).
- The benchmark's cast *form* is the correct shape to compare against: **VERY HIGH (0.95)**; that it alone fixes the inertness: **LOW (~0.15)**.
- `perform_special_ability_q` is a genuinely different, untested route: **HIGH (0.9)** it is different; **MED (~0.3)** it lands.
- `battle_army:use_special_ability` applies to a *unit* ability: **LOW (~0.2)** (it is position/army-scoped).
- `take_control`-then-cast is the strongest candidate: **MED-HIGH (~0.45)** (it is the main mod's own proven shape for its working self-casts).
- `attack_unit`-then-cast / in-range casting for a `hex_melee` key: **MED (~0.35)** each.
- The manual click path has no Lua equivalent: **VERY HIGH (0.96)**.
