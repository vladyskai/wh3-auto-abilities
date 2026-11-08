# Class-C target-type check — Empowering Shrooms, Gaze of Khaine, Gulyas, Massacre

**Question:** do these four areas-of-augments apply only to a certain unit type or attribute?
**Answer, one line:** only **Empowering Shrooms** carries a unit-type filter — `unit_is_not_squig`
(squig-attribute units only). The other three carry **no unit-type restriction found**.

Read-only check of the extracted game data — nothing in the mod, the tracker or the annotated copy was
touched, and nothing was built.

---

## Data sources read (`%LOCALAPPDATA%\Temp\wh3\`)

| File | Game table | What it gives |
|---|---|---|
| `unit_spec_abil.tsv` | `unit_special_abilities_tables` (71 cols) | targeting / affect flags, `num_effected_*`, ranges |
| `phase_junc.tsv` | `special_ability_to_special_ability_phase_junctions_tables` | **who the phase applies to**: `target_self` / `target_friends` / `target_enemies` |
| `phases.tsv` | `special_ability_phases_tables` | duration, `affects_allies` / `affects_enemies`, heal, fatigue |
| `special_ability_to_invalid_target_flags_tables.tsv` | same name | **the unit-type filters** (`invalid_target` × `special_ability`) |
| `special_ability_to_invalid_usage_flags_tables.tsv`, `special_ability_to_auto_deactivate_flags_tables.tsv` | same names | caster/usage conditions |
| `flags.tsv` | `special_ability_invalid_usage_flags_tables` | the declared flag vocabulary |
| `db_unit_attributes.tsv`, `db_unit_attributes_to_groups_junctions.tsv`, `db_land_units.tsv` | unit attributes | proves which flags are real attributes and which units carry them |
| `uieff/special_ability_phase_stat_effects.tsv`, `phase_attribute_effects.tsv`, `unit_abilities_to_ui_effects_juncs.tsv`, `phases_to_ui_effects_juncs.tsv`, `unit_abilities_additional_ui_effects*` | UI-effect tables | any player-facing qualifier text |
| `unit_abilities.loc.tsv`, `character_skills.loc.tsv` | localisation | effect/name/flavour strings |
| `unit_abilities.tsv`, `land_abil.tsv`, `army_ab_faction.tsv`, `sag_to_abilities.tsv`, `uset_ability.tsv`, `unit_sets.tsv` | ownership / indexing | caster, unit-set gating |

**Every one of the four ability keys was searched in all of the above** (plus a whole-directory scan for
each key). The only non-empty unit-type hit in the entire corpus is the one row below.

### How the filter flags read (established from the corpus, not assumed)

`special_ability_to_invalid_target_flags_tables.tsv` holds **unit predicates**: if the named condition is
true for a candidate unit, that unit is an invalid target. The `unit_is_not_X` names are keyed to the unit
**attribute** vocabulary in `db_unit_attributes.tsv`, and the polarity is confirmed by four independent
same-table examples:

* `unit_is_not_slayer` → `wh3_dlc25_lord_abilities_glorious_death` (project already treats Glorious Death as Slayer-only — same row, same mechanism).
* `unit_is_not_construct` → `wh2_dlc09_character_abilities_restore`, `wh2_dlc09_character_passive_stone_shaper` (Restore / Stone Shaper are Tomb Kings **construct** effects — only constructs valid).
* `unit_is_not_artillery_or_war_machine` → `wh3_dlc25_character_passive_artillery_master`, `wh3_dlc25_character_passive_master_of_ballistics` (war-machine buffs).
* `unit_is_not_commander_class` → `wh2_dlc09_unit_passive_guardian`, `wh2_dlc10_unit_passive_guardian` (Guardian buffs the **character** it guards).

So `unit_is_not_<attr>` ≡ “**only units carrying `<attr>` may be targeted/affected**”. The opposite-polarity
twins (`unit_is_squig`, `unit_is_slayer`, `unit_is_large`, …) also exist as declared keys in `flags.tsv`,
which is why both polarities are spelled out separately.

---

## 1. Empowering Shrooms — `wh3_dlc26_character_abilities_empowering_shrooms`

**UNIT-TYPE FILTER FOUND.**

```
special_ability_to_invalid_target_flags_tables.tsv
  invalid_target = unit_is_not_squig   special_ability = wh3_dlc26_character_abilities_empowering_shrooms
```

* `unit_is_not_squig` is a declared flag key (`flags.tsv` line 217) and **`squig` is a real unit attribute** (`db_unit_attributes.tsv`). It is the row's *only* invalid-target flag — no other filter of any kind (no `unit_is_large`, no `unit_is_commander_class`, no attribute requirement, no invalid-**usage** flag, no auto-deactivate flag).
* **What it restricts:** the affected/targetable units — only units carrying the **`squig`** attribute. The `squig`-attribute roster in this data (10 land units) is: `wh_dlc06_grn_inf_squig_herd_0`, `wh_dlc06_grn_inf_squig_explosive_0`, `wh_dlc06_grn_cav_squig_hoppers_0`, `wh_dlc06_grn_cav_durkits_squigs_0`, `wh2_dlc15_grn_cav_squig_hoppers_waaagh_0`, `wh3_dlc26_grn_cav_mangler_squig`, `wh3_dlc26_grn_inf_squig_herd_0_summoned`, `wh3_dlc26_grn_mon_colossal_squig`, `wh3_dlc26_grn_mon_colossal_squig_ror`, `wh_twa03_def_inf_squig_explosive_0`.
* Targeting shape (`unit_spec_abil.tsv`): `target_friends = true`, `target_ground = true`, `target_enemies = false`, `target_self = false`, `only_affect_target = false`, `only_affect_owned_units = false`, `num_effected_friendly_units = -1` (uncapped), `num_effected_enemy_units = 0`, `effect_range = 35.0`, `target_intercept_range = 100.0`, `always_affect_self = false`, `affect_self = true`.
* **Phase junction** (`phase_junc.tsv`): `target_self = false`, `target_friends = true`, `target_enemies = false` → **the phase’s audience excludes the caster.** (Matches the master list’s own effect text “to allies in range”.)
* Phase (`phases.tsv`): 35 s, positive, `affects_allies = true`. Stats: `stat_melee_attack +24`, `stat_morale +16`; attribute effect `rampage` with `attribute_type = negative` (= removes Rampage, i.e. “Stops Rampage!”).
* Owner (`land_abil.tsv`): `wh3_dlc26_grn_cha_night_goblin_big_boss_squig` and `wh3_dlc26_grn_cha_night_goblin_big_boss`. **Neither carries the `squig` attribute** — even the Great-Cave-Squig-mounted variant has only `encourages, guerrilla_deploy, hide_forest, immune_to_psychology`.
* Localisation: name “Empowering Shrooms”; tooltip text is flavour only (“The fact that Squigs and gobbos love them should serve as a warning…”). **No qualifier string anywhere** in `unit_abilities.loc.tsv`, `special_ability_phases__.loc.tsv`, the UI-effect junction tables or `unit_abilities_additional_ui_effects*` — no “Squig units only” text is shipped to the player.
* Minor field note: `affect_self = true` (ability level) disagrees with the junction’s `target_self = false`. The junction gates the phase’s audience and agrees with the project’s own effect text, so treat it as no-self; the disagreement is recorded in case a field test is wanted.

**Can it affect self? No** (junction `target_self = false`; and the caster is not `squig`-flagged, so it fails the target filter regardless).
**Trigger implication:** *not* a `self + allies` buff — it is a **squig-only ally buff**. A self-cast (the mod’s current shape) buys nothing for the caster and nothing for a non-squig army; the cast is only meaningful when a `squig`-attribute unit is inside the 35 m aura, and the target the engine will accept is that squig unit.

---

## 2. Gaze of Khaine — `wh2_dlc10_lord_abilities_gaze_of_khaine`

**No unit-type restriction found.** No row in `special_ability_to_invalid_target_flags_tables.tsv`, none in the invalid-**usage** or auto-deactivate tables, no attribute requirement, no `unit_is_*` flag of any kind.

* Targeting shape: `target_ground = true`, `target_friends = false`, `target_enemies = false`, `target_self = false`, `target_ground_under_allies = true`, `only_affect_target = false`, `only_affect_owned_units = false`, `num_effected_friendly_units = -1` (uncapped), `num_effected_enemy_units = 0`, `effect_range = 35.0`, `target_intercept_range = 100.0`, `num_uses = 3`, `affect_self = false`, `always_affect_self = false`. (Ground-target only, as the audit said; no unit can be clicked as the target, so the invalid-target table has nothing to bite on.)
* **Phase junction: `target_self = true`, `target_friends = true`, `target_enemies = false`** → **self + all friendly units** in the aura.
* Phase: 28 s, positive, `affects_allies = true` (and `affects_enemies = true` at phase level — the junction’s `target_enemies = false` is the operative audience, so no enemy effect). Stats: `stat_melee_attack +24`, `stat_melee_damage_ap ×1.25`, `stat_melee_damage_base ×1.25`, `stat_morale +8`; attribute effect `rampage` with `attribute_type = positive` (= **applies** Rampage!, cf. the audit’s standing rule 7).
* Localisation: name “Gaze of Khaine”; tooltip flavour only (“Those who fall under the glare of Hellebron…”). **No qualifier string.**
* Owner: Crone Hellebron (`wh2_dlc10_def_cha_crone_0/1/4/5`). Index type `wh_type_area_of_augments`.

**Can it affect self? Yes** (junction `target_self = true`; the pattern matches the master list’s “to self and allies”).
**Trigger implication:** a plain 35 m `self + allies` area augment over **any friendly unit type** — the current cast-at-own-feet shape is valid and the caster is genuinely in the affected set.

---

## 3. Gulyas — `wh3_dlc24_lord_abilities_gulyas`

**No unit-type restriction found.** No invalid-target row, no invalid-usage or auto-deactivate flag.

* Targeting shape: `target_ground = true`, `target_friends = false`, `target_enemies = false`, `target_self = false`, `target_ground_under_allies = true`, `affect_self = true`, `always_affect_self = false`, `only_affect_target = false`, `only_affect_owned_units = false`, **`num_effected_friendly_units = 5` (the only cap of the four)**, `num_effected_enemy_units = 0`, `effect_range = 35.0`, `target_intercept_range = 200.0`, `wind_up_time = 3.0`.
* **Phase junction: `target_self = true`, `target_friends = true`, `target_enemies = false`** → **self + up to 5 friendly units** (any type).
* Phase: 23 s, positive, `affects_allies = true`, `heal_amount = 0.0008` (0.08 % per tick), `hp_change_frequency = 1.0`, `fatigue_change_ratio = -0.01` (-1 %/s); stat `stat_morale +4`. No attribute effect (so no `unit_is_*` hook anywhere in its chain).
* Localisation: name “Gulyas”; tooltip flavour only. **No qualifier string.**
* Owner: Mother Ostankya (`wh3_dlc24_ksl_cha_mother_ostankya`). Index type `wh_type_area_of_regeneration`.

**Can it affect self? Yes** (`affect_self = true` and junction `target_self = true` — the two agree here).
**Trigger implication:** `self + up to 5 allies`, no unit-type filter; a self-cast at own feet always includes the caster, so the health-gated self trigger is sound. The only “type” nuance is the count cap (5 friendly units), not a unit type.

---

## 4. Massacre — `wh3_main_prisoners_massacre`

**No unit-type restriction found.** No invalid-target row, no invalid-usage flag, no auto-deactivate flag, no attribute requirement.

* Targeting shape: `target_friends = true`, `target_ground = true`, `target_enemies = false`, `target_self = false`, `affect_self = false`, `always_affect_self = false`, `only_affect_target = false`, `only_affect_owned_units = false`, `num_effected_friendly_units = -1` (uncapped), `num_effected_enemy_units = 0`, `effect_range = 35.0`, `target_intercept_range = -1.0` (none set), `target_ground_under_allies = false`.
* **Phase junction: `target_self = false`, `target_friends = true`, `target_enemies = false`** → **friends in range only; the caster is not in the affected set** (matches the master list’s “to allies in range”).
* Phase: 17 s, positive, `affects_allies = true`. Stats: `stat_melee_attack +24`, `stat_melee_damage_ap ×1.25`, `stat_melee_damage_base ×1.25`.
* It is an **army ability** (`unit_abilities.tsv source_type = 'army'`; `army_ab_faction.tsv` maps it to all Ogre factions; index type `wh_type_area_of_augments`). Minor quirk, AI-hint only: `autoresolver_usage = 'debuff_unit'` although the phase is positive and friend-only.
* Localisation: name “Massacre”; tooltip flavour only (“When there’s fresh meat in the offing…”). **No qualifier string.**

**Can it affect self? No** (junction `target_self = false`).
**Trigger implication:** any friendly unit type counts, but the **caster never benefits** — a self-cast at own feet only buffs allies inside 35 m, so the trigger’s only requirement is having non-routing allies in range.

---

## Side-by-side

| Ability | Unit-type filter | Exact flag | Self affected? | Audience |
|---|---|---|---|---|
| Empowering Shrooms | **yes** | `unit_is_not_squig` (invalid_target) | **no** | squig-attribute units only, uncapped |
| Gaze of Khaine | **no unit-type restriction found** | — | **yes** | self + all friends in 35 m |
| Gulyas | **no unit-type restriction found** | — | **yes** | self + up to 5 friends in 35 m |
| Massacre | **no unit-type restriction found** | — | **no** | friends in 35 m only |

Shared, non-restrictive values (all four): `target_enemies = false`, `num_effected_enemy_units = 0`, `only_affect_target = false`, `only_affect_owned_units = false`, `passive = false`, `affect_siege_equipment = true` (the augment also touches siege equipment attached to units — a scope, not a unit-type limit), `target_ground_under_enemies = false`. There is **no** `affect_only_*` column family in `unit_special_abilities_tables`; the closest fields are `only_affect_target` and `only_affect_owned_units`, both false everywhere here.

## Bounds on this answer (stated so the finding is not over-read)

* The `invalid_target` flags are the engine’s **target-validity** table. What is directly readable is that a non-squig unit is not a valid target of Empowering Shrooms; whether the engine additionally re-checks the flag against each *recipient* inside the 35 m area is not observable from the tables. For Empowering Shrooms both paths lead to the same practical restriction, because `target_friends = true` is the only route to a squig unit and `unit_is_not_squig` is what narrows that route.
* `phases.tsv` `affects_allies` / `affects_enemies` are phase-level capabilities and are broader than the junction; the junction is the audience that matters (all four have `target_enemies = false`, so none of them hexes enemies despite Gaze of Khaine’s and Gulyas’ `affects_enemies = true`).
* Unrelated to this task but noticed while cross-checking: the `slayer` **attribute** set (15 land units — includes `wh2_pro08_neu_cha_gotrek`, `wh_main_dwf_cha_ungrim_ironfist`, `wh3_dlc25_dwf_cha_garagrim_ironfist`, `wh3_dlc25_dwf_cha_malakai_makaisson`, `wh3_dlc25_dwf_art_goblin_hewer`) is a superset of the project’s 10 key-derived `FOURTH.slayer_keys`, which the tracker already documents as an under-approximation. Flagged only as a possible future refinement; no change made.
