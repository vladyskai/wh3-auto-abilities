# WARHAMMER III — SUMMON ABILITIES: COUNT, GATE OF KHORNE, ONE-TRIGGER DESIGN, PLAYABILITY

Research only. Nothing in the mod, tracker, spreadsheet or annotated copy was modified.
All numbers below were recomputed from the sources listed in §0; nothing is copied from an earlier document.

---

## 0. Sources and method

| Source | Path | What was taken |
|---|---|---|
| Master workbook | `docs/WH3_abilities_master_v1_2026-10-17.xlsx` (sheet `Abilities`, 1,797 rows × 23 columns) | Inventory, Status (IN-WHEEL / EXCLUDED), Implementation, Trigger family, Restrictions, tooltip fields |
| Unit special abilities | `%LOCALAPPDATA%\Temp\wh3\unit_spec_abil.tsv` (3,173 rows) | **the spawn signal**: `spawned_unit`, `spawn_type`, `spawn_is_transformation`, `spawn_is_decoy`, `target_ground`, `target_self/friends/enemies`, `target_intercept_range`, `min_range`, `num_uses`, `recharge_time`, `initial_recharge`, `wind_up_time`, `ai_usage`, `additional_melee_cp` |
| Phases | `phases.tsv` (2,526 rows) + `phase_junc.tsv` (2,730 rows) | phase durations, damage, `resurrect`, `affects_allies/enemies`, phase→ability junctions |
| Flag tables | `special_ability_to_invalid_target_flags_tables.tsv`, `…_invalid_usage_flags…`, `…_auto_deactivate_flags…` | the engine's own refusal flags, quoted by name |
| Ability registry | `unit_abilities.tsv` (3,179 rows) | `type` (e.g. `wh_type_summon_unit`), `source_type`, `uniqueness`, `is_unit_upgrade`, `requires_effect_enabling` |
| Grant graph | `land_abil.tsv` (9,687 rows), `uset_ability.tsv` (727), `sag_to_abilities.tsv` (1,480), `army_ab_faction.tsv` (374), `ui_coll_junc.tsv` (26) | who can actually hold each ability |
| Units | `db_main_units.tsv`, `db_land_units.tsv`, `db_unit_attributes_to_groups_junctions.tsv` | men per unit, caps, attributes (invulnerable / unbreakable / …) |
| Mod source | `mod_source/script/battle/mod/zz_test_deadly_onslaught.lua` (11,270 lines) | the existing ground-cast path and evaluator inventory |

> **Workbook version note.** The analysis was run on `WH3_abilities_master_v1_2026-10-17.xlsx`.
> A `…_v2_2026-10-17.xlsx` appeared in `docs/` while this was being written; it was re-checked and its
> Status counts are **identical** (1,158 IN-WHEEL / 639 EXCLUDED, 1,797 rows, 0 status differences).
> v2 changes only the Implementation label of the two outside-rule Ogre army abilities to
> `REMOVED (outside rule)`. Every number below is unchanged in v2.

**Rule of evidence:** an ability is called a summon only if the game's own data says a unit is spawned
(`unit_special_abilities.spawned_unit` is non-empty). Key names, tooltip words and the workbook's
"Summon Unit" category were used only as cross-checks, never as the identification rule.

---

## 1. How a summon is identified — and why the obvious alternatives are wrong

### 1.1 The signal that works: `spawned_unit`

`unit_special_abilities` carries a dedicated spawn block:

```
spawned_unit | spawn_type | spawn_proxy_vfx | spawn_is_transformation | spawn_is_decoy
             | spawn_shares_health_and_fatigue
```

3,173 ability rows; **214 carry a `spawned_unit`**. That is the entire spawn population.
`spawn_type` takes only three values: `unit_position_offset` (69), `unit_position` (26) and blank (119 —
blank is the default placement, not "no spawn"). 158 distinct unit keys are spawned.

### 1.2 `phases` / `phase_junc` do NOT identify summons

- `phase_junc` has no spawn column at all (`order, special_ability, target_self, target_friends, target_enemies, phase`).
- The only summon-adjacent field in `phases` is `resurrect`: 24 phase rows across 32 abilities.
  Every one of those is **model replenishment**, not unit creation — Invocation of Nehek and its
  variants, Realm of Souls tier passives, the Hieratic Jar, the Revivification Crystal, the Curse of
  Undeath lore passive. Using `resurrect` as a summon signal would have added 32 false positives and
  zero true ones.
- **78 of the 89 in-wheel spawn abilities have no phase row at all.** Their whole effect is the spawn;
  there is nothing to read in `phases`. Any phase-based method finds almost nothing.

So: `spawned_unit` is the only usable game-data signal, and it is exact.

### 1.3 Three sub-classes that must be separated

| Sub-class | Field | Rows | What it is |
|---|---|---:|---|
| Transformation | `spawn_is_transformation = true` | 16 | The caster **becomes** the unit (Tz'arkan ×5, Transformation of the Dragon ×6, Formless Horror ×3, Burrow, Surface). Not a summon. |
| Illusion / decoy | `spawn_is_decoy = true` | 4 | Mislead, Call of the Shadow Dancer, Doppelgang, Deceiving Shadows — a fake duplicate that does no damage. A unit does appear, but it is not a reinforcement. |
| Real summon | neither flag | **170** | The ability adds a real unit to the battle. |

---

## 2. QUESTION 1 — the summon count

### 2.1 Counts

| Layer | Rows | Keys | Distinct names |
|---|---:|---:|---:|
| Whole inventory (all statuses) | 1,797 | 1,865 | — |
| Inventory rows carrying a `spawned_unit` | **190** | — | — |
| … of which transformation (`spawn_is_transformation`) | 16 | — | — |
| … of which illusion (`spawn_is_decoy`) | 4 | — | — |
| **Real summons in the inventory** | **170** | 170 | — |
| Real summons **IN-WHEEL** | **85** | **85** | **71** |
| Real summons **EXCLUDED** | 85 | 85 | — |
| Real summons **IMPLEMENTED** | **0** | 0 | 0 |
| Illusion summons IN-WHEEL (if counted) | +4 | +4 | +4 |
| **IN-WHEEL total including illusions** | **89** | 89 | 75 |

The 85 excluded summons split by the workbook's own reason column:
**59 army-bar** (`excluded family: army - army-bar ability`) and **26 spellbook**
(`excluded family: spell - spell (lore-group, cast from the spellbook)`).

**Answer for the three numbers asked for:**

| Question | Answer |
|---|---|
| (a) summon abilities in the inventory | **170** real summons (174 counting the 4 illusions; 190 if the 16 transformations are lumped in) |
| (b) IN-WHEEL under the single rule | **85** (89 counting illusions) |
| (c) not yet implemented | **85 of 85** — not one in-wheel summon is implemented, and none of the 170 either |

### 2.2 Reconciliation against the user's 72 — the 72 is real, but it is a different measurement

The 72 is exactly reproducible: it is the number of **IN-WHEEL rows whose `unit_abilities.type` is
`wh_type_summon_unit`** — the game's own ability-type label.

```
IN-WHEEL rows with type = wh_type_summon_unit : 72
of those, also a real spawn by spawned_unit  : 71
of those, actually an illusion (decoy)       :  1   (Deceiving Shadows)
```

So the 72 is a *labelling* count, not a *spawn* count. It differs from the spawn count in both directions:

**The 72 includes one non-summon.** Deceiving Shadows (`wh3_dlc24_lord_item_deceiving_shadows`) is
typed `wh_type_summon_unit` but carries `spawn_is_decoy = true` — it spawns an illusion of the Changeling,
not a fighting unit.

**The 72 misses fourteen real spawners**, because their type label describes the *delivery*, not the spawn:

| Ability | Key | `unit_abilities.type` | Spawns |
|---|---|---|---|
| Eye of Khorne | `wh3_dlc26_lord_abilities_eye_of_khorne` | `wh_type_direct_damage` | Spawn of Khorne |
| Beast Pack | `wh2_dlc16_lord_abilities_beast_pack` | `wh_type_augment` | Rat Ogres |
| Blacktoof's Conjuration | `wh2_dlc15_item_abilities_blacktoofs_conjuration` | `wh_type_augment` | Rogue Idol |
| Call to Gwindalor | `wh2_dlc16_lord_abilities_call_to_gwindalor` | `wh_type_augment` | Great Eagle |
| Lesser Raise Dead | `wh2_dlc16_spell_bound_vampires_lesser_raise_dead` | `wh_type_augment` | Zombies |
| Savage Dominion | `wh2_dlc17_spell_bound_savage_dominion` | `wh_type_augment` | Cygor |
| Savage Predators | `wh3_dlc26_hero_abilities_savage_predators` | `wh_type_augment` | Sabretusk pack |
| Tide of Death | `wh2_dlc16_hero_abilities_tide_of_death` | `wh_type_augment` | Wolf Rats |
| Tide of Pox | `wh2_dlc16_hero_abilities_tide_of_pox` | `wh_type_augment` | Wolf Rats (pox) |
| Wake Da Idol | `wh3_main_item_abilities_zak_aloooog` | `wh_type_augment` | Rogue Idol |
| The Dreaded Thirteenth Spell (×4 keys) | `wh3_dlc29_spell_bound_the_dreaded_thirteenth…` | `wh_type_explosion` | Stormvermin |

**Reconciliation in one line:** 72 = 71 real summons + 1 illusion; the full spawn count is 85 =
71 + 14 real spawners whose type label is augment/explosion/direct-damage.

**Which number to use:** 85 for "how many summons are in the wheel", 89 if the four illusion
abilities are meant to be automated too, 72 only as "how many the game labels Summon Unit".

### 2.3 Two data notes

- 24 ability keys in `unit_spec_abil.tsv` carry a `spawned_unit` but are **not in the 1,797-row
  inventory**: **16 passives** (Gift of Chaos, Nurgling Emergence, the four Gift of the Father tiers,
  Spirit Essence of Chaos…), **3 quest-battle scripted summons**
  (`wh2_dlc17_army_abilities_{chaos_spawn,cygor,ghorgon}_summon_qb_scripted`), and **5 active/hidden
  variants** (The Rats Overwhelm, the Liche Priest Vizier's Kanopi item, Realm of Souls Ushabti
  "hidden", Morghast Archai, Spirit Essence of Eternal Chaos). They are outside the inventory by
  construction, so they change no count — the Kanopi is flagged only because it is a real item ability
  that the inventory does not list.

---

## 3. QUESTION 2 — Gate of Khorne, complete row

Key: `wh3_main_character_abilities_gate_of_khorne` (workbook Item #461).

### 3.1 The raw row (`unit_spec_abil.tsv`, every non-empty column)

| Column | Value |
|---|---|
| `active_time` | 10.0000 |
| `recharge_time` | 120.0000 |
| `num_uses` | **1** |
| `initial_recharge` | 60.0000 |
| `effect_range` | 0.0000 |
| `affect_self` / `always_affect_self` | false / false |
| `target_self` | **false** |
| `target_friends` | **true** |
| `target_enemies` | **false** |
| `target_ground` | **true** |
| `target_intercept_range` | **50.0000** |
| `min_range` | 0.0000 |
| `num_effected_friendly_units` / `num_effected_enemy_units` | 0 / 0 |
| `only_affect_target` / `only_affect_owned_units` | false / false |
| `wind_up_time` | 5.0000 |
| `passive` | false |
| `spawned_unit` | **`wh3_main_kho_inf_bloodletters_summoned_0`** |
| `spawn_type` | **`unit_position_offset`** |
| `spawn_is_transformation` / `spawn_is_decoy` | false / false |
| `spawn_shares_health_and_fatigue` | false |
| `targetting_aoe` / `passive_aoe` | `wh_abilities_generic_spawn` / same |
| `miscast_chance` | 0.0000 |
| `ai_usage` | **`hex_melee`** |
| `additional_melee_cp` | **200.0000** |
| `composite_scene_group_on_wind_up` | `wh3_main_khorne_gate` |
| `audio_switch_ui_override` | Khorne |

From `unit_abilities.tsv`: `type = wh_type_summon_unit`, `source_type = active`,
`uniqueness = wh_main_anc_group_rare`, `is_unit_upgrade = true`, `is_hidden_in_ui = false`,
`requires_effect_enabling = true`, `icon_name = wh3_main_character_abilities_gate_of_khorne`.
(`requires_effect_enabling = true` is not a blocker: 320 of the 603 already-implemented abilities carry
the same flag and fire normally.)

### 3.2 What it summons

One unit of **`wh3_main_kho_inf_bloodletters_summoned_0`** — **100 men**, caste `melee_infantry`,
morale 75, melee attack 34, melee defence 26, charge bonus 30, bonus HP 72, attributes
`causes_fear` + `daemonic` + `hide_forest`. Those are the *same* combat stats as the recruitable
`wh3_main_kho_inf_bloodletters_0` (34 / 26 / 30); the summoned variant differs only in
`multiplayer_cap 0`, `recruitment_cost 0`, `upkeep_cost 0`. So it is a full-strength 100-model
Bloodletter regiment, not a weakened token.

**Duration.** There are **no phase rows** for this ability — `phase_junc.tsv` contains no row for
`wh3_main_character_abilities_gate_of_khorne`. The only duration in the data is `active_time = 10 s`,
which is the ability's own active window (the gate/VFX), **not a proven unit lifetime**. No table in
this extraction carries a "summoned unit lifetime" or "decay" column (`db_unit_attributes.tsv` has 87
attributes; none is `summoned`/`decay`/`temporary`). **The decay time of the Bloodletters is therefore
unknown from data and must be observed in a battle.**

**Cap.** There is no active-instance, max-alive or "one at a time" column anywhere in
`unit_special_abilities`. The only limits that exist are:
`num_uses = 1` (one cast per battle per unit), `recharge_time = 120 s`, `initial_recharge = 60 s`.
`num_effected_friendly_units = 0` and `only_affect_target = false` — no target-count cap.

### 3.3 Targeting and restrictions

- Targeting (from the workbook's own field): *"Summon Unit · targeting: ground (area placed) + allies"*,
  range *"target_intercept_range 50 m; targets ground"*.
- **invalid-target:** `climbing_manning_eq_on_platform` — refused while the caster is climbing, manning
  a siege engine, or on a platform/wall.
- **invalid-usage:** none.
- **auto-deactivate:** none.
- Tactical Overview (the game's own category sentence): *"Spawns a unit to join the battle."*
- Game text: *"Khorne's loyal Cultist forces open the gate to allow His vicious, chosen Bloodletters to
  surge through and consume the inauspicious enemy."*

### 3.4 Can it be cast at a GROUND POINT via `perform_special_ability_ground`?

**Yes on the data, with one unproven step.**

- `target_ground = true`, `min_range = 0`, `target_intercept_range = 50` — a point at the caster's own
  feet is inside the ability's own reach, and nothing in the row forbids a close point.
- The ground form exists in the mod already:
  `uc:perform_special_ability_ground(ability_key, pos, 0, 0)` inside `FOURTH.ground_cast`
  (`zz_test_deadly_onslaught.lua:4362-4371`), and the file records the API shape as
  *"battle_unitcontroller:perform_special_ability_ground(ability_key, position, orientation_in_degrees, width_in_m) — 'on a specified position'"*.
- The precedent key is `wh3_dlc24_character_abilities_tacticians_stand_your_ground`, which is also
  `target_friends = true` + `target_ground = true` — the same targeting shape as Gate of Khorne — and
  fires through that helper.
- **Caveat, quoted from the mod's own comment:** *"Vanilla passes a UNIT to perform_special_ability at
  all 26 of its call sites and never calls the _ground form, so the API documentation is the evidence
  for the ground path."* And the proven ground key is a **buff**; no **spawn** ability has ever been
  fired through the ground form in this project. That is the one item on the battle-confirmation list.

### 3.5 What the game's own AI usage says about when it uses it

`ai_usage = hex_melee`. In this project's own reading of that column
(`WH3_ability_strategy_report.md` §2), `hex_melee` means *"as the fight starts, on the enemy you are
engaged with"*. The AI therefore places the gate **on the melee hex — the enemy it is fighting**, not
at its own feet. `additional_melee_cp = 200` is the highest value any summon carries (30 of 85 sit at
200); it is the engine's own valuation when the AI scores the cast — a separate scale from a unit's
`melee_cp` (the Bloodletter unit's is 800), so it says "high-value cast", not "one unit's worth".

**Owners** (`land_abil.tsv`, 3 units): `wh3_main_kho_cha_cultist_0`, `wh3_main_kho_cha_cultist_1`,
`wh3_dlc20_kho_cha_cultist_mkho_warshrine` — all `class = com`.

---

## 4. QUESTION 3 — one trigger for all summons

### 4.1 The targeting landscape (85 real summons)

| Property | Count | Notes |
|---|---:|---|
| `target_ground = true` | **81** | ground-castable |
| `target_ground = false` | **4** | see below |
| ground **and** `target_enemies = true` | **16** | *place on the enemy's ground* |
| ground and not enemy-targeted | **65** | *place near self / allies* |
| `target_friends = true` | 52 | |
| `target_self = true` | 49 | |
| `target_enemies = true` (any) | 17 | 16 of them are also ground |
| `min_range > 0` | **0** | no summon has a minimum cast distance |
| `target_intercept_range < 0` (no range) | 2 | Greater Gate of Khorne (cataclysm), Tallyman's Blades Upgraded |
| `effect_range ≠ 0` | **0** | no aura radius on any summon |

**The four that cannot take a ground point at all:**

| Ability | Key | Targeting | Why it matters |
|---|---|---|---|
| Eye of Khorne | `wh3_dlc26_lord_abilities_eye_of_khorne` | `target_enemies` only, 50 m | needs an **enemy unit**; also `health_above_20%` + `unit_is_commander_class` |
| Master of Souls | `wh_dlc08_quest_abilities_master_of_souls` | `target_self` + `target_friends`, **600 m**, no ground | unit cast, not ground |
| Servants of Nagash | `wh_dlc04_quest_abilities_servant_of_nagash` | `target_self` + `target_friends`, **600 m**, no ground | unit cast, not ground |
| Nurgling Tide | `wh3_main_lord_abilities_nurgling_tide` | all four flags **false**, intercept **0** | no target at all — a plain self cast |

### 4.2 Placement restrictions the engine actually ships

| Flag | Type | Count (of 85) | Meaning |
|---|---|---:|---|
| `climbing_manning_eq_on_platform` | invalid-target | 38 | refused while climbing / manning a siege engine / on a platform |
| `climbing` | invalid-usage | 14 | refused while climbing |
| `on_a_platform` | invalid-target | 6 | refused on a platform |
| `on_a_platform` | invalid-usage | 1 | Nurgling Tide |
| `phase_is_deployment` | invalid-usage | 4 | Guardian Call I/II/III, Lesser Raise Dead — deployment-only |
| `health_above_20%` | invalid-target | 3 | Eye of Khorne, Master of Souls, Servants of Nagash — target must be **at or below 20 % health** |
| `unit_is_commander_class` | invalid-target | 2 | Eye of Khorne, Master of Souls — cannot target lords/heroes |
| `engaged_in_melee` | invalid-usage | **0 of the 85** — but **4 of the 4 illusions** | the decoys cannot be cast in melee at all |
| auto-deactivate flags | — | **0** | no summon carries one |

The `engaged_in_melee` result is the important one for the user's design: **no real summon is blocked
in melee**, but **all four illusion abilities are blocked in melee and only in melee** — the exact
opposite of the proposed trigger.

### 4.3 Caps, uses and timing (why a mistimed cast is expensive)

| Property | Distribution |
|---|---|
| `num_uses` | **1 use: 58** · 2: 13 · 3: 5 · 5: 7 · 15: 1 (Servants of Nagash) · 40: 1 (Master of Souls) |
| `recharge_time` | 120 s: 52 · 90 s: 13 · 60 s: 5 · 0 s: 5 · 52 s: 4 (Dreaded Thirteenth) · 300 s: 3 · 45 s, 8 s, 5 s: 1 each |
| `wind_up_time` | **5 s: 31** · 0 s: 28 · 3 s: 15 · 1 s: 11 |
| `spawn_type` | blank: 48 · `unit_position_offset`: 36 · `unit_position`: 1 |
| `additional_melee_cp` | 100: 39 · 200: 30 · 150: 5 · 75: 5 · 0: 3 · 66/50/25: 1 each |

Two consequences:
1. **58 of 85 are single-use.** A summon fired at the wrong moment is gone for the battle. This argues
   for a trigger that fires when the bodies will matter, not merely when melee starts.
2. **31 of 85 have a 5-second wind-up.** An "in melee" cast therefore *lands* five seconds into the
   fight. That is fine for a grind and too late to block a charge.

There is **no "one at a time" active limit** in the data — the ability either has charges or it does
not. Repeated firing is only wasteful in the sense that it burns charges: for 58 abilities the second
cast cannot happen, and for the rest the recharge (mostly 120 s) paces it.

### 4.4 What the game's own AI does with them (`ai_usage`, 85 rows)

| `ai_usage` | Count | Reading (project glossary) |
|---|---:|---|
| `threatened` | **57** | "fire when engaged" |
| `hex_melee` | 12 | the melee hex — the enemy you are fighting |
| `hex_ranged_summon` | 4 | when the unit has a target |
| `artillery_opportunity` | 4 | when a good artillery target exists |
| `aoe_bombardment` | 4 | placed on a clump |
| `assault_opportunity` | 2 | when an opportunity attack exists |
| (blank) | 1 | Mask of the Merlord |
| `qb_master_of_souls` | 1 | a bespoke quest-battle template (unique in the whole 3,173-row table) |

**69 of 85 carry an engagement-driven tag** (`threatened` + `hex_melee`). The user's instinct — fire
when the fight is on — is the same instinct the engine ships. The disagreement is not *when* but
*where*.

### 4.5 Evaluation of the proposed rule: "target the ground below self when in melee"

**What is right about it**

- The **condition** matches the data: 69/85 AI tags are engagement-driven, and `is_in_melee()` is
  already the mod's dominant, proven read (363 entries ride the `melee_unwavering` evaluator).
- The **cast form** is legal for 81/85: `target_ground = true`, `min_range = 0` everywhere, so a point
  at the caster's own feet is inside every ground ability's own reach.
- The **call already exists** in the mod (`FOURTH.ground_cast`), so there is no new API risk beyond
  proving it on a spawn ability.
- 65/85 are self/allies-oriented ground placements — for those, "under self" is exactly what the
  ability expects.

**Where it breaks**

1. **4/85 cannot take a ground point** (Eye of Khorne, Master of Souls, Servants of Nagash,
   Nurgling Tide). A single ground-only rule silently never fires for them. Three of the four also
   carry `health_above_20%` or no target flags, so they need a different cast form *and* a different
   condition.
2. **16/85 are enemy-ground abilities.** The game's AI tags for them are `hex_melee` (Arachnarok Eggs,
   Eye of Khorne), `hex_ranged_summon` (Get Tha Gitz!, The Portalglyph),
   `aoe_bombardment` (The Dreaded Thirteenth ×4). Placing them under the caster summons the unit on
   your own side of the fight instead of the enemy's — mechanically accepted, tactically inverted.
3. **4/85 are illusions that are refused in melee.** If the wheel includes them, "in melee" is the one
   state in which they can never fire (`engaged_in_melee` invalid-usage, all four).
4. **31/85 have a 5 s wind-up**, so an in-melee cast resolves after the moment it was needed; and
   **58/85 are single-use**, so the miss is permanent.
5. **`climbing_manning_eq_on_platform` (38) and `climbing` (14)** mean the rule will try and be refused
   whenever the caster is on a wall, a ladder or a siege engine — the mod's guard/back-off absorbs it,
   but it is wasted polling.

**Verdict:** the *trigger* is right, the *cast point* is only right for 65 of the 81 ground abilities.
"Ground below self" is a good default, not a universal rule.

### 4.6 Three candidate triggers, with evidence

#### Candidate A — "in melee, cast on the ground under self" (the user's proposal)

| For | Against |
|---|---|
| 69/85 AI tags are engagement-driven (`threatened` 57, `hex_melee` 12) | 4/85 not ground-castable; 3 of them need a ≤20 % health target |
| 81/85 accept a point at the caster's feet (`min_range = 0`) | 16/85 are enemy-ground — own feet inverts the design |
| `is_in_melee()` already proven in the mod (363 entries) | the 4 illusions are refused in melee |
| cast call already built (`FOURTH.ground_cast`) | 5 s wind-up on 31/85; 58/85 single-use |
| 65/85 are self/ally ground placements — exactly this shape | refused while climbing/manning/platform on 38+14 |

#### Candidate B — "charge window OR in melee" (the existing `charge_or_melee` evaluator)

The charge arm is already implemented: `is_moving_fast()` and not `is_in_melee()` and
`current_target() ≠ nil` and target distance 12–60 m and `distance / fast_speed ≤ 4 s`; the melee arm is
plain `is_in_melee()`; the charge arm is tested first and wins.

| For | Against |
|---|---|
| Matches the strategy report's stated perfect moment for summons: *"block a charge, plug a gap, add flank pressure"* | for 31/85 with a 5 s wind-up the unit still lands after contact |
| Reuses a tested evaluator already carrying 25 entries | a stationary summoner never fires the charge arm (the melee arm still covers it) |
| Covers both the pre-contact body-block and the grind — the two uses the data actually describes | needs `current_target()` to be readable, which the mod already relies on elsewhere |
| Fires earlier than A, which matters for single-use abilities | — |

#### Candidate C — "a friendly unit is lost / a friendly unit is below 20 % health"

| For | Against |
|---|---|
| Master of Souls and Servants of Nagash **literally require** a target at ≤20 % health (`health_above_20%` invalid-target) — the game itself designed two summons as "consume the dying" | only 2/85 carry that gate; nothing ties the other 83 to a health event |
| Summons are reinforcements — replacing a lost unit is the natural use | the mod has no "unit lost" event read; it would have to infer a vanished unit (new machinery) |
| The mod already has the ally-picking evaluators (`ally_heal`, `ally_wavering`) to build on | 3 self/friend summons need a unit-target cast form, so C needs the same per-ability branch as B |

### 4.7 Recommendation

**Adopt B as the condition, and make the cast point a property of the ability rather than a constant.**

One evaluator, `summon_engaged`:
1. **Condition** — charge window first, then in melee (the existing `charge_or_melee` logic, so the
   body-block cast happens before contact and the grind cast happens during it). This is the single
   trigger; the two arms are one condition, not two rules.
2. **Cast point — dispatched from the ability's own columns** (a lookup table exactly like the existing
   `FOURTH.ground_keys` / `FOURTH.enemy_ground_keys`):

| Ability's own flags | Cast form | Abilities |
|---|---|---:|
| `target_ground && target_enemies` | `perform_special_ability_ground(key, enemy:position(), 0, 0)` | 16 |
| `target_ground` (not enemy) | `perform_special_ability_ground(key, unit:position(), 0, 0)` — the user's rule | 65 |
| `target_self` or `target_friends`, no ground | `perform_special_ability(key, unit)` | 2 |
| `target_enemies` only | `perform_special_ability(key, enemy)` + a ≤20 % health enemy pick | 1 |
| no target flag at all | `perform_special_ability(key, unit)` | 1 (Nurgling Tide) |

16 + 65 + 2 + 1 + 1 = 85.

3. **Exclusions from this evaluator:** the four illusions (they are `engaged_in_melee`-refused and
   belong to an out-of-contact trigger); the four `phase_is_deployment` abilities (Guardian Call I/II/III,
   Lesser Raise Dead — they are meant for deployment); and, until the target-picking rule is built,
   the two 600 m self/friend summons (Master of Souls, Servants of Nagash — both need a friendly target
   at ≤20 % health). Nurgling Tide has no target flags at all and takes the plain unit cast.

**Why B over A:** it costs nothing extra (the evaluator exists), it fires early enough to matter for
single-use summons, and it matches the one sentence the project already wrote about summons
(*"block a charge, plug a gap, add flank pressure"*). **Why the cast-point table over "always under
self":** it removes the 16 enemy-ground inversions at the cost of one lookup, and it makes the 4
non-ground abilities possible at all.

**If the user wants the absolute minimum v1:** keep A exactly as proposed ("in melee → ground under
self") and arm only the 65 self/ally ground keys. That is coherent, needs no new evaluator, and is the
subset where the rule is unambiguously correct. The 16 enemy-ground + 4 non-ground + 4 illusions stay
off the badge until the mapping is built.

---

## 5. QUESTION 4 — playability

### 5.1 Master of Souls — **non-playable, HIGH confidence**

| Evidence | Value |
|---|---|
| Key namespace | `wh_dlc08_quest_abilities_master_of_souls` |
| Granted by (`land_abil.tsv`) | **exactly one unit**: `wh_dlc08_vmp_mon_terrorgheist_boss` |
| That unit | on-screen name **"The Abyssal Shrieker"**; attributes `invulnerable`, `unbreakable`, `undead`, `flying`, `causes_fear`, `causes_terror`; `campaign_cap 1` |
| Other grants | `uset_ability` 0 · `sag_to_abilities` 0 · `army_ab_faction` 0 · `ui_coll_junc` 0 |
| `ai_usage` | **`qb_master_of_souls` — the only row with that tag in all 3,173 abilities** |
| Workbook status | IN-WHEEL, NOT IMPLEMENTED |

`invulnerable` + `unbreakable` + a bespoke `qb_*` AI template is a scripted set-piece boss. Nothing a
player can recruit, equip, learn or spend a rite on holds this ability in any table available here.

### 5.2 Servants of Nagash — **non-playable, MEDIUM-HIGH confidence**

| Evidence | Value |
|---|---|
| Key namespace | `wh_dlc04_quest_abilities_servant_of_nagash` |
| Granted by | **exactly one unit**: `wh_dlc04_vmp_cha_strigoi_ghoul_king_0_boss` |
| That unit | `multiplayer_cap 0`, `in_encyclopedia false`, `concealed_name` empty, attributes only `causes_fear`/`encourages`/`undead` — a `_boss` variant, but not flagged invulnerable |
| Other grants | ×0 in all four other junction tables |
| `ai_usage` | `threatened` (generic — no bespoke template) |

Same shape as Master of Souls except the boss is not marked `invulnerable`, so the inference rests on
the `_boss` variant + the `quest_abilities` namespace + the absence of any other grant. It is the same
class of ability, one notch less provable. **Confidence: medium-high, not certain** — campaign
recruitment tables (`building_units_allowed` and the quest-battle scripts) are not part of this
extraction, so the negative cannot be closed absolutely.

### 5.3 The same check across the whole inventory

**A full audit is not possible with this data.** 544 of the 1,158 IN-WHEEL abilities have **no grant in
any of the five junction tables**, and the list is dominated by item and weapon abilities (Aether Sword,
Alakanash, Amulet of Itzl, Axe of Dargo …) whose grants live in ancillary/effect tables that were never
extracted. Absence of a grant here is therefore *not* evidence of unobtainability in general.

What **can** be reported is the narrow, defensible finding: **in-wheel abilities whose only granting
unit is a `_boss` variant** — 15 of them, including the two asked about:

| Ability | Key | Implementation | Only owner |
|---|---|---|---|
| Greater Faith Bastion | `wh_dlc06_quest_abilities_grand_faiths_bastion` | **IMPLEMENTED** | `wh_dlc06_emp_cha_arch_lector_0_boss` |
| Bitter Sting | `wh3_dlc27_qb_unit_abilities_bitter_sting` | **IMPLEMENTED** | `wh3_dlc27_chs_feral_manticore_boss` |
| Frenzied Challenge | `wh3_dlc27_qb_unit_abilities_frenzied_challenge` | **IMPLEMENTED** | `wh3_dlc27_bst_mon_ghorgon_boss` |
| Visions of Madness | `wh3_dlc27_qb_unit_abilities_visions_of_madness` | **IMPLEMENTED** | `wh3_dlc27_bst_mon_jabberslythe_boss` |
| Guttural Roar | `wh3_dlc27_qb_unit_abilities_guttural_roar` | **IMPLEMENTED** | `wh3_dlc27_cth_mon_celestial_lion_boss` |
| Breath of the Hydra | `wh2_dlc10_quest_abilities_fiery_head` | not implemented | `wh2_dlc10_def_mon_war_hydra_boss` |
| Eye of Rejuvenation | `wh2_dlc10_quest_abilities_regenerating_head` | not implemented | `wh2_dlc10_def_mon_war_hydra_boss` |
| Howling Winter | `wh_dlc08_quest_abilities_howling_winter` | not implemented | `wh_dlc08_nor_mon_frost_wyrm_boss` |
| **Master of Souls** | `wh_dlc08_quest_abilities_master_of_souls` | not implemented | `wh_dlc08_vmp_mon_terrorgheist_boss` |
| **Servants of Nagash** | `wh_dlc04_quest_abilities_servant_of_nagash` | not implemented | `wh_dlc04_vmp_cha_strigoi_ghoul_king_0_boss` |
| Dissolving Bone | `wh3_dlc27_qb_unit_abilities_dissolving_bone` | not implemented | `wh3_dlc27_tmb_mon_carrion_boss` |
| Terrible Malice | `wh3_dlc27_qb_unit_abilities_terrible_malice` | not implemented | `wh3_dlc27_sla_mon_preyton_boss` |
| Copious Phlegm | `wh3_dlc27_qb_unit_abilities_copious_phlegm` | not implemented | `wh3_dlc27_nur_mon_toad_dragon_boss` |
| Fiery Convocation | `wh2_dlc10_quest_abilities_magic_fiery_convocation` | not implemented | `wh2_dlc10_nor_mon_phoenix_flamespyre_boss` |
| Flame Storm | `wh2_dlc10_quest_abilities_flame_storm` | not implemented | `wh2_dlc10_nor_mon_phoenix_flamespyre_boss` |

**The headline for the project:** five abilities the mod already auto-fires are granted only to
quest-battle bosses. They are harmless (the badge only arms a unit that owns the key, and no
player-obtainable unit in the extracted data does), but they are dead entries — no player unit will ever trigger them. That is worth knowing before
the next round of counting "implemented" as progress.

**A second, lower-confidence finding:** 17 IN-WHEEL `cataclysm_bound_*` keys have **no grant in any
extracted table** — Time Amok ×2, Dance of Despair ×2, Storm of Renewal ×2, Ashes & Dust ×2, Gehenna's
Golden Globe ×2, Magma Storm ×2, Thorsen's Thunderstorm ×2, Merciw's Monstrous Regiment ×2 (already
IMPLEMENTED), Greater Gate of Khorne ×1. These are the DLC20/DLC27 duplicate pairs of the same bound
spell; most likely one copy per pair is live and the other is a dangling reference, or they are enabled
by the Cataclysm mode's own rules rather than a unit junction. **Confidence: low** — do not act on this
without the mode's grant tables.

**One more observation, not a playability claim:** `wh3_main_cataclysm_khorne_greater_gate_of_khorne`
is classified IN-WHEEL by the workbook even though its key says `cataclysm`. The workbook's rule keys
off `unit_abilities.source_type`, and that row's `source_type` is `active` (not `cataclysm`), so the
classification is consistent with the rule — the key name is what is misleading, not the status.

---

## 6. What I would need to confirm in a battle

1. **Does `perform_special_ability_ground(key, unit:position(), 0, 0)` actually fire a *spawn* ability?**
   The only proven ground key is a buff (Tactician's Stand Your Ground). Gate of Khorne would be the
   first spawn fired through it. Watch for: accepted call, gate VFX, Bloodletters on the field.
2. **Where do the Bloodletters land relative to the clicked point?** `spawn_type = unit_position_offset`
   — the offset distance/direction is not in the data. If the offset is large, "under self" is not
   actually under self.
3. **Do summoned units decay, and over what time?** No lifetime column exists in the extraction. Time
   the Bloodletters from spawn to disappearance in a clean test.
4. **Does the ground form refuse a point occupied by models?** Cast into the middle of a melee blob and
   see whether the engine silently drops the cast or displaces the spawn.
5. **Is a refused ground cast free?** With `num_uses = 1`, a refusal that consumes the charge would be
   catastrophic. Cast at an invalid point (e.g. while climbing a wall) and check the charge count.
6. **Does `can_perform_special_ability` stay true while the ground call is refused?** The project
   already knows the readiness read can lie during cooldown; confirm it also lies for an invalid point,
   because that is what the trigger polls.
7. **For the 4 non-ground summons:** does `perform_special_ability(key, unit)` work for
   Master of Souls / Servants of Nagash at 600 m, and does Nurgling Tide (no target flags) accept the
   unit form at all?
8. **For the 16 enemy-ground summons:** does `perform_special_ability_ground(key, enemy:position(), 0, 0)`
   place the unit on the enemy — and for The Dreaded Thirteenth, does the explosion damage the caster's
   own units if placed at their feet? (Its `type = wh_type_explosion`, `ai_usage = aoe_bombardment`,
   but it has no phase rows, so the damage numbers are in a bombardment definition that was not extracted.)

---

## Appendix A — the 85 IN-WHEEL real summons

Columns: name · key · uses · recharge (s) · `target_ground` · `target_enemies` · `ai_usage` · spawned unit.

| Ability | Key | Uses | Recharge (s) | Ground | Enemies | `ai_usage` | Spawned unit |
|---|---|---:|---:|---|---|---|---|
| Ancestral Vengeance | `wh3_dlc23_item_abilities_ancestral_vengeance` | 2 | 120 | true | false | threatened | `wh3_dlc23_chd_mon_kdaai_fireborn_summoned` |
| Ancestral Warriors | `wh3_main_spell_bound_ancestral_warriors` | 2 | 120 | true | false | assault_opportunity | `wh3_main_cth_inf_ancestral_warriors_summoned_0` |
| Arachnarok Eggs | `wh_dlc08_item_abilities_arachnarok_eggs` | 5 | 60 | true | true | hex_melee | `wh_dlc06_grn_mon_spider_hatchlings_0_summoned` |
| Beast Pack | `wh2_dlc16_lord_abilities_beast_pack` | 1 | 120 | true | false | threatened | `wh2_dlc16_skv_mon_rat_ogres_summoned` |
| Beyond the Realm | `wh2_dlc11_character_abilities_beyond_the_realm` | 2 | 120 | true | false | threatened | `wh2_dlc11_cst_cav_knights_of_the_realm` |
| Blacktoof's Conjuration | `wh2_dlc15_item_abilities_blacktoofs_conjuration` | 1 | 300 | true | false | threatened | `wh2_dlc15_grn_mon_rogue_idol_summoned_0` |
| Bloodstone | `wh3_main_item_abilities_bloodstone` | 1 | 120 | true | false | hex_ranged_summon | `wh3_main_kho_inf_bloodletters_summoned_0` |
| Call to Ceithin-Har | `wh2_dlc16_lord_abilities_call_to_ceithin_har` | 1 | 120 | true | false | threatened | `wh2_dlc16_wef_mon_ceithin_har_summoned` |
| Call to Gwindalor | `wh2_dlc16_lord_abilities_call_to_gwindalor` | 1 | 120 | true | false | threatened | `wh2_dlc16_wef_mon_gwindalor_summoned` |
| Captain Roth's Moondial | `wh2_dlc11_item_abilities_captain_roths_moondial` | 2 | 120 | true | false | threatened | `wh2_dlc11_cst_inf_zombie_deckhands_mob_summoned_0` |
| Children of the Forest | `wh3_dlc25_character_abilities_children_of_the_forest` | 5 | 90 | true | false | threatened | `wh2_dlc16_wef_mon_giant_spiders_0` |
| Dreaming Cloak I | `wh2_dlc16_item_abilities_dreaming_cloak_i` | 1 | 120 | true | false | artillery_opportunity | `wh_dlc05_wef_inf_glade_guard_0` |
| Dreaming Cloak II | `wh2_dlc16_item_abilities_dreaming_cloak_ii` | 1 | 120 | true | false | artillery_opportunity | `wh_dlc05_wef_inf_deepwood_scouts_0` |
| Dreaming Cloak III | `wh2_dlc16_item_abilities_dreaming_cloak_iii` | 1 | 120 | true | false | artillery_opportunity | `wh_dlc05_wef_inf_waywatchers_0` |
| Eye of Khorne | `wh3_dlc26_lord_abilities_eye_of_khorne` | 1 | 120 | false | true | hex_melee | `wh3_dlc26_kho_mon_spawn_of_khorne_0_summoned` |
| Gate of Chaos | `wh3_main_daemon_arms_abilities_gate_of_chaos` | 2 | 120 | true | false | threatened | `wh3_main_tze_inf_blue_horrors_summoned_0` |
| Gate of Chaos Upgraded | `wh3_main_daemon_arms_abilities_gate_of_chaos_upgraded` | 2 | 120 | true | false | threatened | `wh3_main_tze_mon_lord_of_change_summoned_0` |
| Gate of Khorne | `wh3_main_character_abilities_gate_of_khorne` | 1 | 120 | true | false | hex_melee | `wh3_main_kho_inf_bloodletters_summoned_0` |
| Gate of Nurgle | `wh3_main_character_abilities_gate_of_nurgle` | 1 | 120 | true | false | hex_melee | `wh3_main_nur_inf_plaguebearers_summoned_0` |
| Gate of Slaanesh | `wh3_main_character_abilities_gate_of_slaanesh` | 1 | 120 | true | false | hex_melee | `wh3_main_sla_inf_daemonette_summoned_0` |
| Gate of Tzeentch | `wh3_main_character_abilities_gate_of_tzeentch` | 1 | 120 | true | false | threatened | `wh3_main_tze_inf_pink_horrors_summoned_0` |
| Get Tha Gitz! | `wh3_dlc23_hero_abilities_get_tha_gitz!` | 3 | 120 | true | true | hex_ranged_summon | `wh3_dlc23_chd_inf_hobgoblin_cutthroats_summoned` |
| Ghosts of the Past | `wh2_dlc11_character_abilities_ghosts_of_the_past_0` | 1 | 120 | true | false | threatened | `wh2_dlc11_cst_cav_knights_errant_0` |
| Ghosts of the Past | `wh2_dlc11_character_abilities_ghosts_of_the_past_1` | 2 | 120 | true | false | threatened | `wh2_dlc11_cst_cav_knights_errant_1` |
| Ghosts of the Past | `wh2_dlc11_character_abilities_ghosts_of_the_past_2` | 2 | 120 | true | false | threatened | `wh2_dlc11_cst_cav_knights_errant_2` |
| Gorger Onslaught | `wh3_main_lord_abilities_gorger_onslaught` | 1 | 60 | true | true | threatened | `wh3_main_ogr_mon_gorgers_summoned_0` |
| Gorger Onslaught Upgraded | `wh3_dlc26_lord_abilities_gorger_onslaught_upgraded` | 3 | 90 | true | true | threatened | `wh3_main_ogr_mon_gorgers_0` |
| Greater Gate of Khorne | `wh3_main_cataclysm_khorne_greater_gate_of_khorne` | 1 | 0 | true | false | hex_melee | `wh3_main_kho_mon_bloodthirster_summoned_0` |
| Greater Gate of Khorne | `wh3_main_character_abilities_greater_gate_of_khorne` | 1 | 120 | true | false | hex_melee | `wh3_main_kho_mon_bloodthirster_summoned_0` |
| Greater Gate of Nurgle | `wh3_main_character_abilities_greater_gate_of_nurgle` | 1 | 120 | true | false | hex_melee | `wh3_main_nur_mon_great_unclean_one_summoned_0` |
| Greater Gate of Slaanesh | `wh3_main_character_abilities_greater_gate_of_slaanesh` | 1 | 120 | true | false | hex_melee | `wh3_main_sla_mon_keeper_of_secrets_summoned_0` |
| Greater Gate of Tzeentch | `wh3_main_character_abilities_greater_gate_of_tzeentch` | 1 | 120 | true | false | hex_melee | `wh3_main_tze_mon_lord_of_change_summoned_0` |
| Guardian Call | `wh3_main_character_abilities_guardian_call` | 1 | 0 | true | true | threatened | `wh3_main_ksl_mon_snow_leopard_summoned_0` |
| Guardian Call II | `wh3_main_character_abilities_guardian_call_ii` | 1 | 0 | true | true | threatened | `wh3_main_ksl_mon_snow_leopard_summoned_1` |
| Guardian Call III | `wh3_main_character_abilities_guardian_call_iii` | 1 | 0 | true | true | threatened | `wh3_main_ksl_mon_snow_leopard_summoned_2` |
| Guardian of the Forest | `wh3_dlc25_character_abilities_guardian_of_the_forest` | 1 | 120 | true | false | threatened | `wh_main_grn_mon_arachnarok_spider_0` |
| Horn of the Ancestors | `wh2_dlc10_item_abilities_horn_of_the_ancestors` | 1 | 120 | true | false | threatened | `wh2_dlc10_dwf_cha_thane_ghost_summoned_0` |
| Inventory of Hatchlings | `wh3_dlc26_character_abilities_inventory_of_hatchlings` | 3 | 120 | true | true | threatened | `wh_dlc06_grn_mon_spider_hatchlings_0_summoned` |
| Inventory of Hatchlings Upgraded | `wh3_dlc26_character_abilities_inventory_of_hatchlings_upgraded` | 5 | 60 | true | true | threatened | `wh_dlc06_grn_mon_spider_hatchlings_0` |
| Invocation of the Lichemaster | `wh3_dlc29_character_abilities_invocation_of_the_lichemaster` | 1 | 90 | true | false | threatened | `wh_dlc29_vmp_inf_cairn_wraiths_summoned` |
| Invocation of the Lichemaster | `wh3_dlc29_character_abilities_invocation_of_the_lichemaster_0` | 1 | 90 | true | false | threatened | `wh_dlc29_vmp_inf_cairn_wraiths_summoned_upgraded_0` |
| Invocation of the Lichemaster | `wh3_dlc29_character_abilities_invocation_of_the_lichemaster_1` | 1 | 90 | true | false | threatened | `wh_dlc29_vmp_inf_cairn_wraiths_summoned_upgraded_1` |
| Karanak's Howl | `wh3_pro12_hero_abilities_karanaks_howl` | 1 | 120 | true | false | hex_ranged_summon | `wh3_pro12_kho_inf_flesh_hounds_of_khorne_summoned` |
| Kettle's Call | `wh3_dlc25_character_abilities_kettles_call` | 2 | 120 | true | false | threatened | `wh3_dlc25_emp_mon_hawks_summoned` |
| Koldunja's Spirit | `wh3_dlc24_hero_abilities_koldunjas_spirit` | 1 | 120 | true | false | threatened | `wh3_dlc24_ksl_mon_the_things_in_the_woods_summoned` |
| Lesser Raise Dead | `wh2_dlc16_spell_bound_vampires_lesser_raise_dead` | 1 | 0 | true | false | threatened | `wh_main_vmp_inf_zombie_summoned` |
| Locus of Transmogrification | `wh3_main_character_abilities_locus_of_transmogrification` | 2 | 90 | true | false | threatened | `wh3_main_tze_inf_blue_horrors_summoned_0` |
| Lord of Undeath | `wh_pro03_lord_abilities_lord_of_undeath` | 1 | 120 | true | false | threatened | `wh_pro03_vmp_cha_krell_0` |
| Lord of Undeath | `wh_pro03_lord_abilities_lord_of_undeath_0` | 1 | 120 | true | false | threatened | `wh_pro03_vmp_cha_krell_campaign_0` |
| Lord of Undeath | `wh_pro03_lord_abilities_lord_of_undeath_1` | 1 | 120 | true | false | threatened | `wh_pro03_vmp_cha_krell_campaign_1` |
| Lord of Undeath | `wh_pro03_lord_abilities_lord_of_undeath_2` | 1 | 120 | true | false | threatened | `wh_pro03_vmp_cha_krell_campaign_2` |
| Lord of Undeath | `wh_pro03_lord_abilities_lord_of_undeath_3` | 1 | 120 | true | false | threatened | `wh_pro03_vmp_cha_krell_campaign_3` |
| Lord of Undeath | `wh_pro03_lord_abilities_lord_of_undeath_4` | 1 | 120 | true | false | threatened | `wh_pro03_vmp_cha_krell_campaign_4` |
| Mask of the Merlord | `wh3_dlc27_item_abilities_mask_of_the_merlord` | 1 | 120 | true | false | - | `wh3_dlc27_hef_mon_merwyrm_summoned` |
| Master of Souls | `wh_dlc08_quest_abilities_master_of_souls` | 40 | 5 | false | false | qb_master_of_souls | `wh_main_vmp_inf_skeleton_warriors_1` |
| Maternal Instinct | `wh_dlc06_unit_abilities_maternal_instinct` | 5 | 60 | true | true | threatened | `wh_dlc06_grn_mon_spider_hatchlings_0_summoned` |
| Nurgling Birth | `wh3_dlc29_hero_active_nurgling_birth` | 3 | 90 | true | false | threatened | `wh3_dlc25_nur_inf_nurglings_summoned` |
| Nurgling Birth Upgraded | `wh3_dlc29_hero_active_nurgling_birth_upgraded` | 5 | 90 | true | false | threatened | `wh3_main_nur_inf_nurglings_0` |
| Nurgling Tide | `wh3_main_lord_abilities_nurgling_tide` | 3 | 90 | false | false | threatened | `wh3_main_nur_inf_nurglings_summoned_0` |
| Ritual of the Beast | `wh3_dlc24_item_abilities_ritual_of_the_beast` | 1 | 300 | true | false | threatened | `wh3_dlc24_ksl_mon_incarnate_elemental_of_beasts_summoned` |
| Roused to Wrath | `wh2_dlc16_lord_abilities_roused_to_wrath` | 1 | 90 | true | false | threatened | `wh2_dlc16_wef_inf_dryads_0_summoned` |
| Roused to Wrath | `wh2_dlc16_lord_abilities_roused_to_wrath_2` | 2 | 90 | true | false | threatened | `wh2_dlc16_wef_inf_malicious_dryads_0` |
| Sacrilege | `wh2_dlc11_character_abilities_sacrilege` | 2 | 120 | true | false | threatened | `wh2_dlc11_cst_cav_questing_knights_0` |
| Savage Dominion | `wh2_dlc17_spell_bound_savage_dominion` | 2 | 120 | true | false | artillery_opportunity | `wh_dlc03_bst_inf_cygor_0_summoned` |
| Savage Predators | `wh3_dlc26_hero_abilities_savage_predators` | 1 | 120 | true | false | threatened | `wh3_dlc26_ogr_mon_sabretusk_pack_0_summoned` |
| Servants of Nagash | `wh_dlc04_quest_abilities_servant_of_nagash` | 15 | 8 | false | false | threatened | `wh_main_vmp_inf_grave_guard_0` |
| Squig Thinkin' | `wh3_dlc26_character_abilities_squig_thinkin` | 1 | 90 | true | false | threatened | `wh3_dlc26_grn_inf_squig_herd_0_summoned` |
| Stave of Ruinous Corruption | `wh_dlc05_weapon_abilities_stave_of_ruinous_corruption` | 1 | 120 | true | true | threatened | `wh_dlc03_bst_mon_chaos_spawn_0_summoned` |
| Surprise Squig! | `wh3_dlc25_character_abilities_surprise_squig` | 5 | 60 | true | false | threatened | `wh_twa03_def_inf_squig_explosive_0` |
| Sword of Change | `wh_dlc01_weapon_abilities_sword_of_change` | 1 | 90 | true | false | threatened | `wh_main_chs_mon_chaos_spawn_summoned` |
| The Awakening | `wh3_dlc29_lord_abilities_the_awakening` | 1 | 120 | true | false | threatened | `wh3_dlc29_vmp_inf_skeleton_warriors_0_the_awakening` |
| The Dreaded Thirteenth Spell | `wh3_dlc29_spell_bound_the_dreaded_thirteenth` | 1 | 52 | true | true | aoe_bombardment | `wh2_main_skv_inf_stormvermin_0_summoned` |
| The Dreaded Thirteenth Spell | `wh3_dlc29_spell_bound_the_dreaded_thirteenth_1` | 1 | 52 | true | true | aoe_bombardment | `wh2_main_skv_inf_stormvermin_0_summoned` |
| The Dreaded Thirteenth Spell | `wh3_dlc29_spell_bound_the_dreaded_thirteenth_thanquol` | 1 | 52 | true | true | aoe_bombardment | `wh2_main_skv_inf_stormvermin_0_summoned` |
| The Dreaded Thirteenth Spell | `wh3_dlc29_spell_bound_the_dreaded_thirteenth_thanquol_1` | 1 | 52 | true | true | aoe_bombardment | `wh2_main_skv_inf_stormvermin_0_summoned` |
| The Portalglyph | `wh3_main_item_abilities_the_portalglyph` | 1 | 120 | true | true | hex_ranged_summon | `wh3_main_dae_inf_chaos_furies_summoned_0` |
| The Tallyman's Blades | `wh3_dlc25_character_abilities_tallymans_blades` | 1 | 120 | true | false | hex_melee | `wh3_main_nur_inf_plaguebearers_1_summoned` |
| The Tallyman's Blades Upgraded | `wh3_dlc25_character_abilities_tallymans_blades_2` | 1 | 120 | true | false | hex_melee | `wh3_main_nur_inf_plaguebearers_1` |
| The Tomb Blade of Arkhan | `wh2_dlc09_weapon_abilities_tomb_blade_of_arkhan` | 5 | 120 | true | false | assault_opportunity | `wh2_dlc09_tmb_inf_skeleton_warriors_0_summoned` |
| Tide of Death | `wh2_dlc16_hero_abilities_tide_of_death` | 1 | 120 | true | false | threatened | `wh2_dlc16_skv_mon_wolf_rats_0_summoned` |
| Tide of Pox | `wh2_dlc16_hero_abilities_tide_of_pox` | 1 | 120 | true | false | threatened | `wh2_dlc16_skv_mon_wolf_rats_1_summoned` |
| Transformation of Kadon | `wh3_dlc27_spell_bound_transformation_of_kadon` | 1 | 45 | true | false | threatened | `wh3_main_ogr_feral_manticore_summoned` |
| Undeath to All | `wh3_dlc29_lord_abilities_raise_legion` | 1 | 120 | true | false | threatened | `wh3_dlc29_vmp_inf_zombies_raise_legion` |
| Undeath to All Upgraded | `wh3_dlc29_lord_abilities_raise_legion_upgraded` | 1 | 120 | true | false | threatened | `wh3_dlc29_vmp_inf_skeleton_warriors_0_raise_legion` |
| Wake Da Idol | `wh3_main_item_abilities_zak_aloooog` | 1 | 300 | true | false | threatened | `wh2_dlc15_grn_mon_rogue_idol_summoned_0` |

---

## Appendix B — the 4 illusion summons (not counted in the 85)

| Ability | Key | Uses | Recharge | Ground | `engaged_in_melee` | Spawns |
|---|---|---:|---:|---|---|---|
| Mislead | `wh2_dlc10_lord_abilities_mislead` | 3 | 90 | true | **yes** | Alith Anar decoy |
| Call of the Shadow Dancer | `wh2_dlc10_lord_abilities_deadly_mislead` | 3 | 90 | true | **yes** | Alith Anar decoy (upgraded) |
| Doppelgang | `wh2_dlc14_unit_abilities_doppelgang` | 2 | 90 | true | **yes** | Eshin Triads decoy |
| Deceiving Shadows | `wh3_dlc24_lord_item_deceiving_shadows` | 3 | 120 | true | **yes** | Changeling decoy |

All four also carry `climbing`, `manning_equipment` and `on_a_platform` as invalid-usage flags: they are
designed to be cast **out of contact, on open ground** — the exact inverse of the proposed trigger.

---

## Appendix C — the 16 transformation abilities (excluded from every summon count)

| Ability | Key | Becomes |
|---|---|---|
| Formless Horror | `wh3_dlc24_lord_abilities_formless_horror_quest_battle` | Grimgor Ironhide (quest battle) |
| Formless Horror | `wh3_dlc24_lord_abilities_formless_horror_changeling` | the Changeling |
| Formless Horror | `wh3_dlc24_lord_abilities_formless_horror_quest_battle_changeling_form` | the Changeling (quest battle) |
| Transformation of the Dragon | `wh3_dlc24_lord_abilities_jade_dragon_dragon_form` | Yuan Bo, dragon form |
| Transformation of the Dragon | `wh3_dlc24_lord_abilities_jade_dragon_human_form` | Yuan Bo, human form |
| Transformation of the Dragon | `wh3_main_lord_abilities_iron_dragon_dragon_form` | Iron Dragon, dragon form |
| Transformation of the Dragon | `wh3_main_lord_abilities_iron_dragon_human_form` | Iron Dragon, human form |
| Transformation of the Dragon | `wh3_main_lord_abilities_storm_dragon_dragon_form` | Storm Dragon, dragon form |
| Transformation of the Dragon | `wh3_main_lord_abilities_storm_dragon_human_form` | Storm Dragon, human form |
| Burrow | `wh3_dlc27_unit_abilities_dread_maw_underground` | Dread Maw, underground |
| Surface | `wh3_dlc27_unit_abilities_dread_maw_surface` | Dread Maw, surfaced |
| Tz'arkan | `wh2_dlc14_lord_abilities_tzarkan` | Malus Darkblade, Tz'arkan |
| Tz'arkan | `wh2_dlc14_lord_abilities_tzarkan_mp` | same (multiplayer) |
| Tz'arkan | `wh2_dlc14_lord_abilities_tzarkan_snikch` | Snikch, Tz'arkan |
| Tz'arkan | `wh2_dlc14_lord_abilities_tzarkan_spite` | Malus, spite form |
| Tz'arkan | `wh2_dlc14_lord_abilities_tzarkan_spite_mp` | same (multiplayer) |

These spawn a unit **in place of the caster**. They are shape-changes, not reinforcements, and they must
never ride a summon trigger. (A seventeenth row, `wh3_dlc24_lord_abilities_formless_horror`, carries the
transformation flag with no `spawned_unit`; it is excluded for the same reason.)

Note the name collision that makes this list necessary: **Transformation of Kadon**
(`wh3_dlc27_spell_bound_transformation_of_kadon`) is a *real* summon — it spawns a Feral Manticore and
does **not** carry the transformation flag — while "Transformation of the Dragon" is a shape-change.
