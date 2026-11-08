# Slice 10 — ABILITIES entries 523–579 (last 57 of 579)

Audited: 57 entries (523–579). Flagged: 10. Clean: 47.
Source of truth for game data: the extracted db tables (`unit_spec_abil.tsv`, `phase_junc.tsv`, `phases.tsv`, `unit_abilities.tsv/.loc.tsv`, `special_ability_to_invalid_target_flags_tables.tsv`) and the `uieff` tables (`special_ability_phase_stat_effects.tsv`, ui-effect bullets, phase displays). Mod logic read from `zz_test_deadly_onslaught.lua` (entries as written; cast path is `perform_special_ability(key, target or unit)` — every entry that sets no `cast_target` casts on the unit ITSELF).

## FLAGGED

**You're Next! — `wh2_dlc15_lord_abilities_youre_next` (entry 523, marker `youre_next`)**
- Current logic: trigger `melee_unwavering` — fires when the unit is in melee and not wavering, then casts on itself (`perform_special_ability(key, unit)`; the badge tooltip reads "fires when this unit is in melee").
- Game declares: `wh_type_hex`, `target_enemies = true` only, `num_effected_enemy_units = 1` — a single-unit ENEMY hex: −24 melee attack, −40 melee defence, speed ×0.55 for 24 s; its invalid-target gate `unit_is_not_commander_class` further restricts the target to a commander-class enemy character.
- Why it makes no sense: the game's target is an enemy unit (a character), never the caster — a self-cast hands the engine a target the ability rejects and, even if accepted, would debuff the wrong side; the tracker's own intended rule was "cast at the enemy it is fighting".
- Feasibility: NOT implementable as-is — there is no enemy-unit read (no card, no id, no health) and enemy-targeted casts cannot be aimed by the mod; the engine form the mod uses cannot auto-pick the unit's current enemy either.

**Elvish Healing Herbs — `wh3_dlc27_unit_abilities_elfish_healing_herbs` (entry 534, marker `elfish_healing_herbs`)**
- Current logic: trigger `ushoran_health` — fires when the unit's own health ≤75% and casts on itself.
- Game declares: single-target friendly heal (27 s regen at ~0.6%/s, −1% fatigue); `target_friends = true`, `only_affect_target = true`, and NO `target_self` / `affect_self` / `always_affect_self` — the target must be ANOTHER friendly unit.
- Why it makes no sense: self is not a legal target for this ability, so the mod's self-cast cannot heal anything (the tracker's intended rule was "cast on the hurt friendly unit").
- Feasibility: an ally-targeted version is buildable (friendly units/health/distance are readable — the `blood_sacrifice` pattern), but as wired on the self-health trigger the cast targets the caster.

**Makaisson's Persuader — `wh3_dlc25_weapon_abilities_makaissons_persuader` (entry 540, marker `makaissons_persuader`)**
- Current logic: trigger `ushoran_health` — fires at the unit's own ≤75% health and casts on itself.
- Game declares: single-target repair — "a damaged War Machine can be returned to working order", effect HP regen + `replenish_ammo = 0.3` (ammo exists only on war machines), and its invalid-target gate `unit_is_not_artillery_or_war_machine` (the same gate carried by Malakai's/Chaos Dwarf war-machine passives) restricts the legal target to an artillery/war-machine friendly unit.
- Why it makes no sense: the carrier is a character (the ability is granted by the Makaisson's Persuader weapon), not a war machine — the self-cast points the repair at a unit the ability's own gate excludes and that has no ammo to replenish.
- Feasibility: a friendly-target version is buildable (friendly reads exist; the war-machine class could be derived from the game's data like the Slayer list), but the current self-cast cannot land.

**Patch Up — `wh2_dlc13_character_abilities_patch_up` (entry 543, marker `patch_up`)**
- Current logic: trigger `ushoran_health` — fires at the unit's own ≤75% health and casts on itself.
- Game declares: single-target friendly heal (7 s regen at 1.6%/s) — "swiftly dress the wounds of targeted friendly units"; `target_friends = true` with no self target and no self effect (no `target_self`/`affect_self`/`always_affect_self`).
- Why it makes no sense: the ability can only be pointed at another friendly unit; a self-cast targets the caster, which the ability cannot affect, so the heal can never land.
- Feasibility: ally-targeting is buildable (readable friendlies), but not as wired on this self-cast trigger.

**Reforge — `wh3_dlc23_character_abilities_reforge` (entry 548, marker `reforge`)**
- Current logic: trigger `ushoran_health` — fires at the unit's own ≤75% health and casts on itself.
- Game declares: restores the hitpoints of "units with the Hell-Forged attribute" (UiEffect bullet verbatim: "Restores the hitpoints of units with the Hell-Forged attribute"); its invalid-target gate `unit_is_not_hellforged` encodes the same restriction, and the ability's owners are Daemonsmith Sorcerers — flesh-and-blood casters, not Hell-Forged units.
- Why it makes no sense: the Daemonsmith is not Hell-Forged, so a self-cast targets a unit the ability's own gate excludes (the row's `target_self = true` is contradicted by the effect bullet and the gate that CA ships for this key); no healing happens.
- Feasibility: could be re-scoped to target a friendly Hell-Forged unit (friendly reads exist; attribute keys derivable from game data), but the current self-cast cannot land.

**Remouldered — `wh2_dlc16_lord_abilities_remouldered` (entry 551, marker `remouldered`)**
- Current logic: trigger `ushoran_health` — fires at the unit's own ≤75% health and casts on itself.
- Game declares: single-target friendly heal plus a 24 s combat buff (+24 melee attack, +8 morale) for a wounded MONSTER ("keep wounded monsters alive and keen"); `target_friends = true` with NO `target_self` — the exact target shape of Throt's Shock Collar, which is cast on his beasts, not himself.
- Why it makes no sense: the caster (Throt) is not the declared target of this ability; casting it at itself hands the engine a target the data does not declare (the tracker's intended rule was "cast on the hurt friendly unit"), so the heal/buff does not land where the ability is designed to go.
- Feasibility: an ally-targeted version is buildable (friendly reads exist; the monster-class gate could be derived from game data), but the current self-cast is wrong.

**Restore — `wh2_dlc09_character_abilities_restore` (entry 552, marker `restore`)**
- Current logic: trigger `ushoran_health` — fires at the unit's own ≤75% health and casts on itself.
- Game declares: single-target friendly heal (24 s regen) whose invalid-target gate `unit_is_not_construct` restricts the target to a Tomb Kings CONSTRUCT; `target_friends = true` with no self target or self effect; the owner is a Necrotect.
- Why it makes no sense: the Necrotect is not a construct and self is not a declared target — the mod's self-cast can never apply the heal.
- Feasibility: a friendly-construct target is in principle selectable (readable friendlies; construct keys derivable), but not as wired.

**Revivification Crystal — `wh2_main_unit_abilities_revivification_crystal` (entry 553, marker `revivification_crystal`)**
- Current logic: trigger `ushoran_health` — fires at the unit's own ≤75% health and casts on itself.
- Game declares: single-target friendly heal plus resurrect (20 s, 0.5%/s); `target_friends = true` with no self target and no self effect; the owner is a Bastiladon whose crystal restores "supplicants" — other units — from the point of death.
- Why it makes no sense: the caster cannot be the target of its own crystal; the self-cast heals/resurrects nothing.
- Feasibility: ally-targeting is buildable (readable friendlies), but not as wired.

**Scroll of Power — `wh_main_item_abilities_scroll_of_power` (entry 556, marker `scroll_of_power`)**
- Current logic: trigger `ushoran_health` — fires when the unit's own health ≤75% and casts on itself (single use).
- Game declares: a one-use item effect ("runes to boost the power of a single spell"): 57 s positive phase with `ability_recharge_change = −60` and NO heal amount anywhere — it is an ability-recharge/spell-power boost, not a heal.
- Why it makes no sense: the entry rides the health-gated heal family, but the effect has nothing to do with the unit's health; the trigger cannot fit the effect, and firing it at ≤75% health wastes its one use at an arbitrary moment.
- Feasibility: no readable condition in the mod matches the ability's purpose (no magic-power or per-ability cooldown reads exist; only the engine's own readiness gate), so it should not ride this trigger at all.

**Eat da Runts! — `wh3_dlc26_unit_abilities_eat_da_runts` (entry 575, marker `eat_da_runts`)**
- Current logic: bespoke `eat_da_runts` trigger — self ≤75% health → cast on SELF; otherwise the lowest-health in-range ally ≤75% → cast on that ALLY (both arms are described in-file as "ally-targeting HEALS").
- Game declares: the target is a friendly unit that gets EATEN — the ally phase deals `damage_amount = 144` ("Causes damage to allies" UiEffect bullet; the initiative text: feed gobbo-fodder to the hungry big'un), while the CASTER heals (1.5%/s self phase). `target_friends = true` with no self target — the ally is the meal, not the patient.
- Why it makes no sense: the mod inverts the effect — the "heal the ally" arm spends the cast to damage the ally it was trying to save (the lowest-health one, where 144 damage likely kills models), and the self arm targets a unit (the caster) the ability cannot take as a target.
- Feasibility: the ability deliberately damages a friendly unit; "which ally is expendable" is not a decidable read and the current direction is backwards — do not keep this as an ally-heal.

## CLEAN

- berry_wine (524)
- blood_chalice (525)
- blood_chalice_of_bathori (526)
- undeath_morkharn_breath_of_darkness (527)
- undeath_morkharn_breath_of_darkness_upgraded (528)
- bugmans_xxxxxx (529)
- dreaming_ring_i (530)
- dreaming_ring_ii (531)
- dreaming_ring_iii (532)
- earth_blood (533)
- fleshy_abundance (535)
- hieratic_jar (536)
- immortal_will (537)
- invocation_of_nehek (538)
- locus_of_fecundity (539)
- neuroparasites (541)
- necrotic_phylactry (542)
- pestilent_regeneration (544)
- potion_of_charoi (545)
- potion_of_healing (546)
- radiant_gem_of_hoeth (547)
- regenerating_flesh (549)
- regrowth (550)
- saint_annushkas_finger_bone (554)
- salyaks_lullaby (555)
- skalm (557)
- skars_kraken_killer (558)
- trollguts (559)
- bloodthirst (560)
- colossal_strike (561)
- crimson_juggernaut (562)
- daemonic_onslaught (563)
- deadly_onslaught (564)
- full_power (565)
- guiding_strike (566)
- locus_of_fury (567)
- locus_of_swiftness (568)
- mastered_strike (569)
- more_power (570)
- purge_the_weak (571)
- shield_of_thorns (572)
- storm_hammer (573)
- blood_sacrifice (574)
- locus_of_virulence (576)
- the_dance_of_dreaming (577)
- the_waltz_of_lethargy (578)
- ultimate_verdict (579)
