# Hecleas Grand Strategy — battle-side review for the ability-automation mod

**Purpose:** find reusable battle-Lua technique for `mod_source/script/battle/mod/zz_test_deadly_onslaught.lua`.
**Method:** located the pack on disk, read the changelog's BATTLE AI section, extracted the pack with RPFM
(`tools/rpfm/rpfm_server.exe`, ws 45127), read every battle Lua file, and **diffed the mod's battle AI
tables against vanilla `db.pack`** to see exactly what was changed.
**Date of pack:** workshop `timeupdated` 1791802142 → 2026-10-12.

---

## 1. Identification

| | |
|---|---|
| Folder | `C:\Program Files (x86)\Steam\steamapps\workshop\content\1142710\3575054982\` |
| Workshop id | **3575054982** |
| Pack | `!!!hecleas_grand_strategy.pack` — **17,922,503 bytes** (18.6 MB per `appworkshop_1142710.acf`) |
| Installed to `data\`? | No. Not listed in `used_mods.txt` (subscribed + downloaded, not enabled). |
| Contents | 513 files: **354 `.tsv` DB tables (148 table dirs, 44,313 lines)**, 62 `.lua` (46,624 lines), 54 png, 28 xml, 13 cco |
| Battle Lua | **4 files, 557 lines total** — `hecleas_auto_end_battle.lua` (46), `hecleas_disable_building_system.lua` (42), `hecleas_legendary_slow_mo.lua` (67), `pwd5032_ammo_devastation_battle.lua` (402) |
| Extracted to | `archive/hecleas_extract/` (vanilla comparisons in `archive/hecleas_vanilla*`, vanilla scripts in `archive/vanilla_script`) |

**The headline, before anything else: this mod contains no ability-scripting Lua at all.** Not one line of it
calls `perform_special_ability`, reads a `battle_unit`, or picks a target. Its entire "BATTLE AI" section is a
**data-only re-weighting of the engine's own AI ability-scoring model** plus a rewrite of the
`ai_usage` column that assigns each ability to one of those scoring templates.

---

## 2. What the BATTLE AI section claims (changelog lines 17–129)

Fetched from `.../export?format=txt` (265,528 bytes, 3,384 lines). The BATTLE AI part is short and entirely
behavioural prose; it names exactly one mechanic:

| Claim (abridged, in the doc's words) | Named mechanic |
|---|---|
| "Tactical Error Prevention … intervenes only to avoid critical mistakes … when isolated units are about to throw themselves into certain death … when lone lords or heroes choose catastrophic engagements … when repeated movement loops create pointless exposure … Rare, Lightweight, **Event-based**" | none named |
| "**Spellcaster Awareness** — Casters now better recognize: Isolated clustered targets / Multi-blob formations / High-impact spell opportunities" | none named |
| "**AI Unit Utilization** — Reworked usage groups: … line infantry, fast units, skirmishers, monsters, artillery" | `ai_usage_groups` (named by implication) |
| "**AI Ability Usage** — Area spells (AoE, bombardments, vortexes, breaths): **evaluates number of enemies, leadership, and armor before casting**"; buffs "when its units are in melee, under missile fire, or being charged"; debuffs "slow a charging enemy unit, reduce the armor of clustered enemies"; healing "on units that have already lost a significant amount of HP"; special projectiles "low armor, numerous enemy troops, tight formations" | none named |
| "**Magic Management** — Mana saving threshold (**`mana_saving_threshold`**) adjusted … the AI hoards less mana" | **`mana_saving_threshold`** — the only literal key in the section |
| "Removal of Hidden AI Bonuses … leadership & other phantom bonuses reset to zero" | none |

So the changelog's own vocabulary ("number of enemies, leadership, armor", "clustered", "tight formations",
"under missile fire", "in melee") is a **restatement of the vanilla parameter names** listed in §4 — the
author is describing a weights table in prose. No new mechanic, no script, no event.

---

## 3. The mechanism, verified by diff

Vanilla `db.pack` ships a three-level, data-driven ability-scoring model:

```
battle_ai_abilities_usage_group_names          (template groups; vanilla only has test_group_1/2)
battle_ai_abilities_usage_groups_to_templates  (group -> template)
battle_ai_abilities_usage_template_names       (92 templates)
battle_ai_abilities_usage_params               (73 params + a NORMALISATION multiplier each)
battle_ai_abilities_usage_templates_to_params  (224 (param, template, weight) rows)
_kv_battle_ai_ability_usage_variables          (5 global knobs)
```

and each ability row in `unit_special_abilities_tables` carries **`ai_usage`** — the template the AI uses when
deciding whether/when/where to fire that specific ability.

What Hecleas changed:

| Table | Vanilla | Mod | Change |
|---|---|---|---|
| `_kv_battle_ai_ability_usage_variables` | `mana_saving_threshold 0.1000`, `mana_saving_max_added_amount 0.1500`, `battle_currency_saving_threshold 1.0`, `min_score_for_activation 0.5000` | `mana_saving_threshold **1.0000**`, `mana_saving_max_added_amount **0.0100**`, currency 1.0, `min_score_for_activation 0.5000` | 2 of 5 knobs; `min_score_for_activation` **unchanged** |
| `battle_ai_abilities_usage_template_names` | 92 templates | **58 new template names, all `*_cerb` / `*_cerb_large` variants** (`aoe_spell_cerb`, `aoe_bombardment_spell_cerb_large`, `vortex_wind_ap_spell_cerb`, …), all `factor_bias = 1.0`; **zero of the 90 vanilla names redefined** | additive template names |
| `battle_ai_abilities_usage_templates_to_params` | 224 pairs | **547** pairs | **135 weights changed on vanilla templates** + ~280 new `_cerb` pairs + 64 new params bolted onto vanilla templates |
| `unit_special_abilities_tables` | 3,173 rows | 425 rows overridden | **407 rows change `ai_usage`**; 18 others change `mana_cost`(45), `active_time`(18), `target_intercept_range`(7), `bombardment`(2), `target_ground`(1), `vortex`-adjacent cols … |
| `ai_usage_groups` | 12 groups | new groups (`ranged_cav`, `flying_melee_shock_highvalue`, `gyrocopter`, `hybrid_melee`, …) with 18 flag columns (`melee, ranged_indirect, fast, flanker, high_value, bomber, shock, harasser, building_breaker, artillery, …`) | usage-group taxonomy |

Representative weight deltas (vanilla → mod, from the diff):

```
augment_melee_area          bool_in_melee                 1.00 -> 2.00
augment_ranged_area         bool_shooting                 1.00 -> 2.00
augment_defense_ranged_area bool_under_fire               1.00 -> 2.00
hex_armour                  value_armour                 30.00 -> 5.00
hex_armour_area             value_enemy_units_in_area     1.50 -> 2.00
hex_ranged_area             value_enemy_units_in_area     3.00 -> 1.00
vortex                      value_enemy_units_in_area     4.00 -> 1.50
vortex_breath               value_enemy_units_in_cone     4.00 -> 2.00
aoe_bombardment             value_enemy_units_in_area     2.00 -> 3.00
projectile_explosive(_ap)   value_speed_current_inverse   (new)  3.00
vortex_wind_ap              value_enemy_units_in_cone     4.00 -> 1.00
```

The claim "no artificial difficulty" is corroborated structurally: **`min_score_for_activation` is untouched**
(0.5) and no ability got a flat power buff — the changes are re-weightings of *when* to fire, plus `mana_cost`
and duration rebalances. But note the changelog's "hoards less mana" claim against the data:
`mana_saving_threshold` went **0.1 → 1.0**, a tenfold *increase*. That is only "hoards less" if the field means
"fraction of the pool the AI is willing to spend"; if it means "reserve to keep", the data says the opposite.
Either way the changelog's description is not verifiable from the name alone — treat that one line as unproven.

---

## 4. Findings, graded

Grades: **(i)** reusable in our mod as-is · **(ii)** reusable with adaptation (what is stated) ·
**(iii)** interesting, not applicable (why stated).

### 4.1 Battle Lua API surface used by the mod

Every battle-API call in all 557 lines of its battle Lua, with file:line. "Ours?" = does `zz_test_deadly_onslaught.lua` call it today (count of occurrences).

| # | Call (exact, as written) | Where | Ours? | Grade | Note |
|---|---|---|---|---|---|
| A1 | `bm:alliances()` → `alliances:count()` / `alliances:item(a)` → `army:armies()` → `army:units()` / `army:get_reinforcement_units(t)` / `army:num_reinforcement_units()` | `pwd5032_ammo_devastation_battle.lua:103-114`, `:225-235`, `:348-353` | **0** | **(i)** | **Full battlefield enumeration incl. reinforcement waves and allied armies. We only ever read `bm:get_scriptunits_for_main_enemy_army_to_local_player()` — which vanilla defines as `get_scriptunits_for_army(non_player_alliance, 1)`, i.e. the *primary* army only, no `reinforcement_units_index` (`lib_battle_manager.lua:450-452`).** |
| A2 | `bm:get_scriptunits_for_army(alliance_id, army_id, reinforcement_units_index)` (vanilla helper over the same thing), plus `bm:num_alliances()`, `bm:num_armies_in_alliance(id)` | vanilla `script/_lib/lib_battle_manager.lua:332`, `:385`, `:394` | 0 | **(i)** | Cleaner form of A1: `bm:num_alliances()` → `bm:num_armies_in_alliance(i)` → `bm:get_scriptunits_for_army(i, j, k)`; `k = nil` → main army, `k = 1..n` → reinforcement wave. |
| A3 | `bm:watch(cond_fn, interval_ms, action_fn)` — also with a 4th id arg in vanilla | `hecleas_auto_end_battle.lua:43` (`bm:watch(check_victory_phase, 2500, terminate_battle)`); vanilla `script/battle/intro_battles/dark_elves/first/battle_main.lua:68-77` (`bm:watch(fn, 0, fn, "movie_finished")`) | **0** | **(ii)** | One-shot condition→action callback. `0` = every tick. We poll with `bm:repeat_real_callback(ui_tick, 50, …)`. Adaptation: use for one-shot latched triggers ("fire once when X first true") instead of `GUARD_TICKS`/`next_at` arithmetic; keep the 50 ms repeater for continuous rule evaluation. |
| A4 | `bm:callback(fn, delay_ms)` | `hecleas_legendary_slow_mo.lua:14`, `:58` | **0** | **(ii)** | Engine-side delayed callback. Adaptation: replaces our tick-count delays (`HOLD_TICKS`, `next_at = tick_count + GUARD_TICKS`) for *single* deferred actions; immune to poll-interval changes. Not a substitute for the guard bookkeeping, which must stay in ticks. |
| A5 | `bm:register_command_handler_callback("Unit Left Battlefield", function(event) … event:get_unit() … end, "pwd_ammo_devastation_unit_left_handler")` | `pwd5032:203-217` | 0 for this command (we use `"Special Ability"` at `:14230`) | **(i)** | Per-unit event instead of discovering disappearance by re-listing. Adaptation is trivial: same registration form we already use, new command string, `event:get_unit()`. |
| A6 | `army:winds_of_magic_current()` + `army:winds_of_magic_reserve()` | `pwd5032:390`; vanilla precedent `script/benchmarks/mom_benchmark/blackfire_pass.lua:183` (`army_tze_01:winds_of_magic_current();`) | **0** (we have zero mana logic) | **(ii)** | Only useful for *prioritisation*, not gating: `can_perform_special_ability` almost certainly already refuses unaffordable casts. Adaptation: when two spells are ready on the same caster, spend the pool where the score is highest instead of first-ready-wins. |
| A7 | `unit:missile_range()`, `unit:starting_ammo()`, `unit:ammo_left()`, `unit:set_current_ammo_unary(x)` | `pwd5032:180-183`, `:211`, `:244` | 0 (mentioned only in a comment at `:7091-7093`) | **(ii)** / (iii) for the setter | `missile_range() ~= 0` is a **static "is this a ranged-capable unit" property** — a predicate we do not have (we lean on `unit_class`/`is_infantry`). `ammo_left() / starting_ammo()` is a "has fired / is dry" progress read, not "is firing now". **Caveat: `missile_range` has zero occurrences in vanilla Lua** — it ships in a working mod but is unproven in the same trust class as `is_in_melee`. `set_current_ammo_unary` is a write — (iii), we never restore state. |
| A8 | `bm:battle_type()` → `"settlement_unfortified"` / `"settlement_standard"` | `hecleas_disable_building_system.lua:29` | 0 | **(i)** | One-line battle-type gate; lets ability rules be enabled/disabled per battle type without probing phase/UI. |
| A9 | `bm:is_victory_countdown_phase()` + `bm:end_battle()` | `hecleas_auto_end_battle.lua:31`, `:39` | 0 | **(ii)** | `is_victory_countdown_phase()` is a distinct flag from `get_current_phase_name()` — a cheap "stop casting, battle is decided" gate for 742 auto-firing rules. `end_battle()` is (iii) for us. |
| A10 | `bm:toggle_system()` → `toggle_system:allow_army_interaction(false)` | `hecleas_disable_building_system.lua:38-41` | 0 | (iii) | Siege building system; irrelevant to abilities. |
| A11 | `bm:camera()` → `cam:disable_anchor_to_army()` | `hecleas_legendary_slow_mo.lua:35-36` | 0 | (iii) | Camera only. |
| A12 | `bm:register_phase_change_callback("Deployed" / "Complete", fn)` | `auto_end:9`, `disable_building:9`, `pwd5032:220`, `:385` | 3 (same API) | — | Already ours. Note they use `"Deployed"` (we use `"Deployed"` + `"Deployment"`). |
| A13 | `unit:type()` used as a composition multiset key to identify which campaign army a battle army is; `unit:unique_ui_id()` as the dictionary key | `pwd5032:142/174`, `:177/241` | both yes | (iii) | Matching technique for cross-VM state; we do not need army identity. |

### 4.2 The ability-selection model (the actual "AI" in the claim)

| # | Finding | Where | Grade | Note |
|---|---|---|---|---|
| B1 | **Per-ability `ai_usage` template column** — the engine's own tactical label for all 3,173 abilities: `aoe`, `aoe_ap`, `aoe_bombardment`, `vortex`, `vortex_ap`, `vortex_breath`, `vortex_wind`, `vortex_flying_only`, `direct_damage_single_entity`, `projectile_explosive(_ap)`, `projectile_homing`, `healing`/`healing_area`, `augment_melee(_area)`, `hex_*`, `threatened`, `full_hide`, `artillery_opportunity`, `assault_opportunity`, `flanking_opportunity`, `ammo_replenish`, `always_use_only_land`, `tzarkan` … Hecleas repointed **407 of 425** of its overridden rows to these | `db/unit_special_abilities_tables/!ai_ability_updates.tsv` col 33 (`ai_usage`), diff vs vanilla col 33 | **(ii)** | **This is the answer to "target-class filters derived from key sets."** We hand-maintain families of ability keys; the DB already carries a per-ability semantic class, authored by CA, covering every ability in the game. Adaptation: export `key, ai_usage, target_ground, vortex, bombardment, targeting_aoe, target_intercept_range` in the build step we already run for `unit_spec_abil.tsv`, and derive our family membership from those columns, keeping the key lists only as overrides. |
| B2 | **Ability-shape columns** the mod edits to change behaviour: `target_ground` (`true→false` for `wh3_dlc29_spell_undeath_sulekhim_hand_of_dust_upgraded`), `bombardment` (repointed to `wh3_dlc27_spell_heavens_urannons_thunderbolt*_v2`), `target_intercept_range` (200→100 for viletide, 200→300 for flock of doom), `update_targets_every_frame` (`true→false` for pit of shades), `num_effected_enemy_units`, `targetting_aoe`, `passive_aoe` | same file, columns `target_ground`(col 14), `bombardment`(col 21), `target_intercept_range`(col 15), `vortex`(col 30), `targetting_aoe`(col 26) | **(ii)** | Same export as B1 but for *shape*: `bombardment ≠ ""` ⇒ true bombard (delayed impact), `vortex ≠ ""` ⇒ moving vortex, `target_ground = true` ⇒ needs `perform_special_ability_ground`, `target_intercept_range` ⇒ the engine's own lead/prediction distance. Replaces guessing "which of the 742 are ground/air-drop" from key names. |
| B3 | **Ground/AoE scoring templates and their weights** (the only place in the whole mod that expresses *how to choose a cast point*): `aoe_spell_cerb_large` = `value_friendly_units_in_area_inverse` **6.0**, `value_enemy_units_in_area` 3.0, `value_num_men` 2.0, `bool_standing_still` 1.5, `value_total_cp` 1.5, `value_armour_inverse` 1.0, `value_damage_resist_magic_inverse` 0.75, `bool_flying_currently` **0.0**; `aoe_bombardment_spell_cerb_large` = `bool_standing_still` **4.0**, friendly-inverse 6.0, enemy-in-area 2.0, **`value_armour` 1.0 (not inverse)**, no speed term; `aoe_bombardment_spell_cerb` = friendly-inverse 3.0 > enemy-in-area **1.0**; `vortex_breath` = `value_num_men` 2.5, **`value_enemy_units_in_cone` 2.0**, `value_armour_inverse` 1.5 | `db/battle_ai_abilities_usage_templates_to_params_tables/data__.tsv` | **(ii)** | Three transferable design rules, all computable from `position()` alone: (1) **friendly-fire veto dominates** — the highest weight in every AoE template is *avoid friendlies in the blast* (6.0 vs 2–3.0 for enemies); our ground casts have no friendly check at all. (2) **bombardments want stationary targets** (`bool_standing_still` 4.0, the single highest weight in the bombardment template) — i.e. prefer blobs that are not moving, which is exactly our `ordered_position` vs `position` test. (3) **breaths are cone-scored, not radius-scored** (`value_enemy_units_in_cone`), a test we do not have and can build with a dot product of relative positions. |
| B4 | **`battle_ai_abilities_usage_params` normalisation multipliers** — the divisor that turns each raw signal into a 0..1-ish score: `value_num_men 0.0055` (≈180 men = 1.0), `value_enemy_units_in_area 0.25`, `value_friendly_units_in_area 0.25`, `value_armour 0.01`, `value_total_cp 0.001`, `value_melee_cp/missle_cp 0.001`, `value_winds_of_magic_amount 0.03`, `value_winds_of_magic_recharge 5.0`, `value_hitpoint_damage_taken 0.0001`, `value_spacing_horizontal/vertical 0.2`, `value_formation_rows 0.2`, `bool_ammo_under_threshold 0.1` | `db/battle_ai_abilities_usage_params_tables/data__.tsv` (73 rows) | **(ii)** | A ready-made **scoring scale**: instead of boolean triggers, score = Σ(weight × raw × multiplier) and fire above a threshold (`min_score_for_activation` 0.5). Directly gives us defensible constants for "how many men is a lot" (0.0055/man ≈ 180), "how many units in an area is a blob" (0.25/unit ≈ 4 units). |
| B5 | **Full 73-param vocabulary** the engine can score on, incl. reads we believe do not exist in Lua: `bool_shooting`, `bool_shooting_at_me`, `bool_charging_at_me`, `bool_threatened`, `bool_threatening_me`, `bool_contesting_victory_point`, `bool_on_wall_near_siege_attack_focus`, `value_enemy_units_in_cone`, `value_spacing_horizontal`, `value_spacing_vertical`, `value_formation_rows`, `value_enemy_to_friendly_ratio`, `value_homing_projectile_ratio`, `value_ability_final_use`, `bool_has_abilities_costing_mana`, `bool_ability_active` | `db/battle_ai_abilities_usage_params_tables/data__.tsv` | **(iii)** as API, useful as **negative evidence** | Confirms our existing note (`zz_test…lua:7086-7100`): the engine *does* model "is shooting", "is charging at me", unit spacing and formation rows — **internally, exposed only to the AI scorer, never to battle Lua**. Our "no is-firing predicate" conclusion stands; stop looking for one in Lua, and do not try to proxy it. `bool_ability_final_use` / `value_hitpoint_damage_taken` **are** buildable by us (cooldown bookkeeping, HP delta) and are worth having. |
| B6 | `ai_usage_template_group` column exists in `unit_special_abilities` (col 69) and `battle_ai_abilities_usage_groups_to_templates` maps groups → templates; the mod rewrites `ai_usage_groups` with 18 boolean role flags | `db/ai_usage_groups_tables/!cerb_ai_changes.tsv` | (iii) | Pure AI unit-role assignment; the AI's own army, not ours. |
| B7 | The mod ships **no** script that computes a cast point, no centroid, no clustering, no radius read, no per-unit bounding box, no "is below" test, no velocity — nothing | all 4 battle files | — | Every "smart targeting" behaviour it claims is the **engine's** C++ scorer being re-weighted. It did not solve any of the problems we are stuck on; it sidestepped them by making the AI's existing solver prefer different inputs. |

### 4.3 Non-ability, noted for completeness

| # | Finding | Where | Grade |
|---|---|---|---|
| C1 | Cross-VM bridge: campaign↔battle are separate Lua VMs (MCT unavailable in battle), so the mod persists state through a **text file** (`pwd_ammo_devastation_svr.txt`) with a cached parse + `svr_load/save/flush`, plus integer encoding (`AMMO_PRECISION = 10000`, `"v2;"` prefix) to dodge locale-sensitive `tostring`/`tonumber` | `script/_lib/mod/pwd_ammo_devastation_lib.lua:54-160`, `pwd5032:18` | (iii) — we are battle-only |
| C2 | The locale-safe integer encoding trick for any persisted float | same | (iii) — no persistence in our mod |
| C3 | `pwd_ad_lib.create_ui_component(parent, name, template)` | lib `:172` | (iii) — we already build badges |

---

## 5. Against what we do today

| Need | Our current read/call | What Hecleas has | Gap |
|---|---|---|---|
| Enemy set | `bm:get_scriptunits_for_main_enemy_army_to_local_player()` (4 call sites) | `bm:alliances()` → armies → `units()` + `get_reinforcement_units(t)` | **Reinforcement waves and allied armies are invisible to us today** (0 occurrences of `reinforcement`/`alliance` in 15,682 lines) |
| Our own side | `bm:get_scriptunits_for_local_players_army()` | same alliance walk | Same blind spot for allied/reinforcing friendlies |
| Position | `unit:position()`, `get_x()`, `get_z()`, `distance_xz()`, `unit_distance()` | `unit:position()` only, for ammo bookkeeping | No change |
| Cast point | a unit's own `position()` — caster (`ground_cast`), enemy (`enemy_ground_cast`), ally (`ally_ground_cast`); `FOURTH.ground_keys` is a hand-built table | n/a (engine does it) | **No centroid, no cluster scoring, no friendly-fire check** |
| Area/ground classification | `FOURTH.is_ground_key(key)` over a hand-maintained set | `ai_usage` + `target_ground`/`vortex`/`bombardment` columns | Data-driven alternative exists |
| Readiness | `can_perform_special_ability(key)` + own back-off (`GUARD_TICKS`, `HOLD_TICKS`, `next_at`) | n/a — engine gate only | Nothing to copy; theirs is the engine's |
| Multi-ability on one unit | per-ability `next_at`, serialised attempts in one 50 ms tick | n/a | Nothing to copy |
| Mana | none | `army:winds_of_magic_current()/reserve()` | Read exists; low value (see A6) |
| Enemy state | `number_of_men_alive`, `HealthPercent`/`unary_hitpoints`, `unit_class`, `is_infantry`, `is_routing`, `is_wavering`, `fatigue_state`, `is_under_missile_attack`, `current_target`, `is_currently_flying` | nothing beyond `type()`/`unique_ui_id()` | Nothing new; B5 tells us where to stop looking |
| Cast calls | `uc:perform_special_ability(key, unit)`, `uc:perform_special_ability_ground(key, pos, 0, 0)` | **never calls either** | No new cast API |

---

## 6. Worth trying in our mod — ranked, max five

1. **Battlefield-wide unit enumeration (A1/A2) — directly reusable, highest value.**
   `bm:num_alliances()` → `bm:num_armies_in_alliance(i)` → `bm:get_scriptunits_for_army(i, j, k)` for
   `k = nil, 1..n`, or the raw form used by the mod:
   `bm:alliances():item(a):armies():item(n):units()` and `:get_reinforcement_units(t)` /
   `:num_reinforcement_units()`. Today every rule in our mod is blind to reinforcing armies — a ≥30 % coverage
   hole on any battle with reinforcements, at the cost of one loop. Paste-ready, no new failure mode (wrap in
   `pcall` as our other reads are).

2. **A friendly-fire veto plus cluster scoring for ground casts (B3 + B4) — needs adaptation, biggest
   behavioural win.** For every `perform_special_ability_ground` we already have the caster's and candidate's
   positions; adding "count friendly units within R of the chosen point; veto if > 0, or subtract
   `6.0 × friendlies − 2.0 × enemies`" reproduces the engine's own priority ranking, whose *highest* weight in
   every AoE template is avoiding friendlies. Our airdrop/bombardment rules currently cast on the nearest
   enemy's centre with no such test, so every mis-aimed drop lands on our own line. One helper, reusing
   `FOURTH.ad_centre_gap`'s position reads.

3. **Derive the ability families from the DB instead of key sets (B1 + B2) — needs adaptation, removes a whole
   class of maintenance.** Export `ai_usage`, `target_ground`, `vortex`, `bombardment`, `targetting_aoe`,
   `target_intercept_range` alongside the `unit_spec_abil.tsv` slice the build already reads, then set
   `FOURTH.ground_keys` / the AoE family from `target_ground = true` or `ai_usage` ∈ {`aoe*`, `vortex*`,
   `*_bombardment*`} with the existing key list kept as an override table. 3,173 abilities are already labelled
   by CA; our 742 do not need hand-classification.

4. **`bm:register_command_handler_callback("Unit Left Battlefield", fn, id)` (A5) — directly reusable, small.**
   `function(event) local u = event:get_unit() … end` replaces re-list-based disappearance detection
   (`gone_units`) with a per-unit event; stops us from firing at a unit that has left the field in the tick
   before the re-list catches it. Same registration shape we already use for `"Special Ability"`.

5. **`bm:watch(cond, 0|ms, action[, id])` for one-shot latched triggers (A3) — needs adaptation, cheap.**
   Vanilla-proven (`battle_main.lua:68`). Replaces `next_at = tick_count + GUARD_TICKS` bookkeeping for the
   "fire exactly once when X first becomes true" rules; keep `repeat_real_callback(ui_tick, 50, …)` for
   continuous evaluation.

*Runners-up, deliberately not in the five:* `unit:missile_range() ~= 0` as a ranged-unit predicate (A7 — useful
but zero vanilla Lua precedent, so it needs a probe first); `army:winds_of_magic_current()` (A6 — probably
already covered by `can_perform_special_ability`); `bm:is_victory_countdown_phase()` (A9 — cheap, but a
nice-to-have next to the existing phase reads).

---

## 7. Verdict

**Roughly 90 % of the "BATTLE AI" claim is a weights table, and the remaining 10 % is prose.** There is no
battle-AI script in the pack: 4 battle Lua files, 557 lines, none of which touch abilities, targeting, or
enemy state in any way we do not already do better. The mod's actual contribution is 135 re-weighted
`(param, template)` rows, 58 new `_cerb` template names built from vanilla's own parameter vocabulary, one
`ai_usage` rewrite covering 407 abilities, and two of five `_kv` knobs — i.e. it makes the **engine's** AI
ability solver prefer different inputs. It is not an example of scripting technique; it is an example of
*data-driven* AI tuning.

What is genuinely useful to us is not its code but two artefacts it exposes: **(1)** the engine's canonical
ability-classification columns (`ai_usage` and the ability-shape flags), which solve our "target classes from
key sets" problem, and **(2)** the engine's scoring vocabulary with its normalisation constants, which is a
ready-made, CA-authored priority model for *where* to put a ground cast — above all its weighting of
friendly-fire avoidance over enemy density, which our current nearest-enemy cast-point choice ignores.

Its battle Lua contributes three small, real API wins: full-battlefield/reinforcement enumeration, the
"Unit Left Battlefield" command hook, and `bm:watch`/`bm:callback` as one-shot scheduling primitives.

---

## 8. Reproduction

```bash
# 1. pack is here (subscribed, not enabled):
#    .../workshop/content/1142710/3575054982/!!!hecleas_grand_strategy.pack
cd /c/Users/vlady/Desktop/WH3_mod/tools/rpfm && ./rpfm_server.exe      # background, ws 45127
cd /c/Users/vlady/Desktop/WH3_mod/tools
python inspect_pack.py "C:/Program Files (x86)/Steam/steamapps/workshop/content/1142710/3575054982/!!!hecleas_grand_strategy.pack" \
                       "C:/Users/vlady/Desktop/WH3_mod/archive/hecleas_extract"
# 2. vanilla comparisons (db.pack holds the DB, data.pack does not):
python _dump_vanilla_ai_tables.py     # -> archive/hecleas_vanilla{,2}
python _dump_vanilla_scripts.py       # -> archive/vanilla_script (900 vanilla lua files)
# 3. changelog text: curl -sL "https://docs.google.com/document/d/<id>/export?format=txt"
```
Requires `pip install websockets` (done). `rpfm_server.exe` exits when the last WebSocket session disconnects —
restart it before each extraction.
