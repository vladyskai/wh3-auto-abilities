# Restriction audit (night of 2026-11-16 / 17)

Every game restriction flag on every automated key (946 entries), against what the mod enforces. Flags the mod does not honour are listed below by flag. Siege flags (walls, platforms, manning equipment) and battle-phase flags are not modelled and are not listed.

| Kind | Flag | Unhandled keys |
|---|---|---:|
| usage | `morale_is_broken_or_lower` | 7 |
| target | `hp_replenish_cap_reached` | 6 |
| target | `cannot_perform_missile_attack` | 5 |
| target | `unit_is_commander_class` | 4 |
| target | `unit_is_not_tiger_warrior` | 3 |
| usage | `health_below_25%` | 3 |
| target | `living_unit` | 3 |
| target | `unit_is_large` | 2 |
| target | `unit_is_not_commander_class` | 2 |
| target | `flying_currently` | 2 |
| usage | `cannot_perform_missile_attack` | 2 |
| target | `unit_is_not_a_lizard_unit` | 2 |
| usage | `health_above_50%` | 2 |
| target | `morale_is_higher_than_half_of_base_morale` | 2 |
| usage | `flying_currently` | 2 |
| target | `unit_is_moulder_monster` | 2 |
| usage | `health_below_50%` | 1 |
| usage | `ground_unit` | 1 |
| usage | `unit_is_not_large` | 1 |
| target | `unit_is_not_slayer` | 1 |
| target | `unit_is_not_squig` | 1 |
| usage | `engaged_in_melee` | 1 |
| target | `unit_is_artillery_or_war_machine` | 1 |
| target | `morale_is_higher_than_broken` | 1 |
| target | `unit_is_not_skaven` | 1 |
| usage | `flying_unit` | 1 |
| usage | `enemies_in_intercept_range` | 1 |
| target | `unit_is_not_artillery_or_war_machine` | 1 |
| usage | `hp_replenish_cap_reached` | 1 |
| target | `unit_is_not_hellforged` | 1 |
| target | `unit_is_not_construct` | 1 |
| target | `health_above_20%` | 1 |

## usage `morale_is_broken_or_lower` (7)

| Family | Marker | Key |
|---|---|---|
| `ally_heal` | `revivification_crystal` | `wh2_main_unit_abilities_revivification_crystal` |
| `enemy_area_drain` | `staff_of_masks` | `wh3_dlc27_item_abilities_staff_of_the_masque` |
| `melee_health75` | `potion_of_toughness` | `wh_main_item_abilities_potion_of_toughness` |
| `ushoran_health` | `immortal_will` | `wh_main_hero_abilities_immortal_will` |
| `ushoran_health` | `potion_of_healing` | `wh_main_item_abilities_potion_of_healing` |
| `ushoran_health` | `regenerating_flesh` | `wh_main_item_abilities_regenerating_flesh` |
| `ushoran_health` | `skalm` | `wh2_main_item_abilities_skalm` |

## target `hp_replenish_cap_reached` (6)

| Family | Marker | Key |
|---|---|---|
| `health_aura_ally` | `earth_blood` | `wh2_dlc16_spell_bound_earth_blood` |
| `health_aura_ally` | `regrowth` | `wh2_dlc16_spell_bound_regrowth` |
| `ushoran_health` | `invocation_of_nehek` | `wh3_dlc29_spell_bound_invocation_of_nehek` |
| `ushoran_health` | `neuroparasites` | `wh2_dlc16_unit_abilities_neuroparasites` |
| `ushoran_health` | `undeath_morkharn_breath_of_darkness` | `wh3_dlc29_spell_bound_undeath_morkharn_breath_of_darkness` |
| `ushoran_health` | `undeath_morkharn_breath_of_darkness_upgraded` | `wh3_dlc29_spell_bound_undeath_morkharn_breath_of_darkness_upgraded` |

## target `cannot_perform_missile_attack` (5)

| Family | Marker | Key |
|---|---|---|
| `allies_firing_aura` | `deranged_munitions_upgraded` | `wh3_dlc25_lord_abilities_deranged_munitions_upgraded` |
| `ally_missile` | `inspired_marksmanship_i` | `wh3_main_lord_abilities_inspired_marksmanship_i` |
| `ally_missile` | `inspired_marksmanship_ii` | `wh3_main_lord_abilities_inspired_marksmanship_ii` |
| `ally_missile` | `inspired_marksmanship_iii` | `wh3_main_lord_abilities_inspired_marksmanship_iii` |
| `self_or_ally_shooting` | `deranged_munitions` | `wh3_dlc25_lord_abilities_deranged_munitions` |

## target `unit_is_commander_class` (4)

| Family | Marker | Key |
|---|---|---|
| `ally_beast` | `whiplash` | `wh2_dlc14_lord_abilities_whiplash` |
| `ally_heal_melee` | `captain_of_the_phoenix_guard` | `wh3_dlc27_character_abilities_captain_of_the_phoenix_guard` |
| `ally_overseer` | `overseer_of_the_unseen` | `wh3_dlc29_hero_active_overseer_of_the_unseen` |
| `enemy_low_health_noncommander` | `eye_of_khorne` | `wh3_dlc26_lord_abilities_eye_of_khorne` |

## target `unit_is_not_tiger_warrior` (3)

| Family | Marker | Key |
|---|---|---|
| `melee_unwavering` | `offense_prayer` | `wh3_cp1_character_abilities_offense_prayer` |
| `melee_unwavering` | `predatory_instincts` | `wh3_cp1_lord_abilities_predatory_instincts` |
| `ushoran_health` | `protection_prayer` | `wh3_cp1_character_abilities_protection_prayer` |

## usage `health_below_25%` (3)

| Family | Marker | Key |
|---|---|---|
| `enemy_ground_melee` | `loons_of_eight_peaks` | `wh_dlc06_unit_abilities_the_loons_of_eight_peaks` |
| `enemy_ground_melee` | `spinning_loons` | `wh_main_unit_abilities_spinning_loons` |
| `melee_unwavering` | `favoured_by_the_matriarch` | `wh3_dlc27_hero_abilities_favoured_by_the_matriarch` |

## target `living_unit` (3)

| Family | Marker | Key |
|---|---|---|
| `health_aura_self_undead` | `icon_of_the_king` | `wh3_dlc29_item_abilities_icon_of_the_king` |
| `ushoran_health` | `undeath_morkharn_breath_of_darkness` | `wh3_dlc29_spell_bound_undeath_morkharn_breath_of_darkness` |
| `ushoran_health` | `undeath_morkharn_breath_of_darkness_upgraded` | `wh3_dlc29_spell_bound_undeath_morkharn_breath_of_darkness_upgraded` |

## target `unit_is_large` (2)

| Family | Marker | Key |
|---|---|---|
| `ally_heal_melee` | `captain_of_the_phoenix_guard` | `wh3_dlc27_character_abilities_captain_of_the_phoenix_guard` |
| `ally_overseer` | `overseer_of_the_unseen` | `wh3_dlc29_hero_active_overseer_of_the_unseen` |

## target `unit_is_not_commander_class` (2)

| Family | Marker | Key |
|---|---|---|
| `ally_melee_buff` | `helping_hand` | `wh2_pro08_character_abilities_helping_hand` |
| `ushoran_health` | `blood_chalice_of_bathori` | `wh_pro02_item_abilities_blood_chalice_of_bathori` |

## target `flying_currently` (2)

| Family | Marker | Key |
|---|---|---|
| `ally_overseer` | `overseer_of_the_unseen` | `wh3_dlc29_hero_active_overseer_of_the_unseen` |
| `melee_or_self_or_ally_shooting` | `entrenchment` | `wh_main_unit_abilities_entrenchment` |

## usage `cannot_perform_missile_attack` (2)

| Family | Marker | Key |
|---|---|---|
| `self_moving` | `blooood` | `wh_main_unit_abilities_blooood` |
| `self_shooting` | `boom` | `wh_main_unit_abilities_boom` |

## target `unit_is_not_a_lizard_unit` (2)

| Family | Marker | Key |
|---|---|---|
| `melee_unwavering` | `focus_instincts` | `wh2_dlc12_lord_abilities_focus_instincts` |
| `wavering_ally_range` | `cold_blooded` | `wh2_main_character_abilities_cold_blooded` |

## usage `health_above_50%` (2)

| Family | Marker | Key |
|---|---|---|
| `enemy_ground_area` | `curse_of_khsar` | `wh2_dlc09_character_abilities_curse_of_khsar` |
| `enemy_ground_shooting` | `curse_of_djaf` | `wh2_dlc09_character_abilities_curse_of_djaf` |

## target `morale_is_higher_than_half_of_base_morale` (2)

| Family | Marker | Key |
|---|---|---|
| `enemy_melee` | `transfix_hex` | `wh3_dlc29_lord_abilities_transfix` |
| `enemy_wavering` | `ghostly_howl` | `wh3_dlc29_hero_active_ghostly_howl` |

## usage `flying_currently` (2)

| Family | Marker | Key |
|---|---|---|
| `melee_unwavering` | `daemon_flask_of_ashak` | `wh3_dlc23_item_abilities_daemon_flask_of_ashak` |
| `melee_unwavering` | `feaster_of_souls` | `wh3_dlc29_mount_abilities_feaster_of_souls` |

## target `unit_is_moulder_monster` (2)

| Family | Marker | Key |
|---|---|---|
| `ally_monster_heal` | `remouldered` | `wh2_dlc16_lord_abilities_remouldered` |
| `ally_wavering` | `shock_collar` | `wh2_dlc16_hero_abilities_shock_collar` |

## usage `health_below_50%` (1)

| Family | Marker | Key |
|---|---|---|
| `melee_unwavering` | `entice` | `wh3_dlc29_unit_abilities_entice` |

## usage `ground_unit` (1)

| Family | Marker | Key |
|---|---|---|
| `melee_unwavering` | `eye_of_the_storm` | `wh3_main_lord_abilities_eye_of_the_storm` |

## usage `unit_is_not_large` (1)

| Family | Marker | Key |
|---|---|---|
| `melee_unwavering` | `eye_of_the_storm` | `wh3_main_lord_abilities_eye_of_the_storm` |

## target `unit_is_not_slayer` (1)

| Family | Marker | Key |
|---|---|---|
| `glorious_death` | `glorious_death` | `wh3_dlc25_lord_abilities_glorious_death` |

## target `unit_is_not_squig` (1)

| Family | Marker | Key |
|---|---|---|
| `melee_unwavering` | `empowering_shrooms` | `wh3_dlc26_character_abilities_empowering_shrooms` |

## usage `engaged_in_melee` (1)

| Family | Marker | Key |
|---|---|---|
| `wavering_ally_range` | `stay_here_ill_get_help` | `wh2_dlc09_character_abilities_stay_here_ill_get_help` |

## target `unit_is_artillery_or_war_machine` (1)

| Family | Marker | Key |
|---|---|---|
| `under_fire` | `morikhane` | `wh3_dlc29_item_abilities_morikhane_the_black_armour` |

## target `morale_is_higher_than_broken` (1)

| Family | Marker | Key |
|---|---|---|
| `ally_broken` | `iron_hand_captain` | `wh3_dlc27_character_abilities_iron_hand_captain` |

## target `unit_is_not_skaven` (1)

| Family | Marker | Key |
|---|---|---|
| `wavering_aura` | `unholy_clamour` | `wh2_main_mount_abilities_unholy_clamour` |

## usage `flying_unit` (1)

| Family | Marker | Key |
|---|---|---|
| `melee_unwavering` | `wrath_of_the_storm` | `wh3_main_lord_abilities_wrath_of_the_storm` |

## usage `enemies_in_intercept_range` (1)

| Family | Marker | Key |
|---|---|---|
| `ushoran_health` | `bugmans_xxxxxx` | `wh3_dlc26_item_abilities_bugmans_xxxxxx` |

## target `unit_is_not_artillery_or_war_machine` (1)

| Family | Marker | Key |
|---|---|---|
| `ally_warmachine_heal` | `makaissons_persuader` | `wh3_dlc25_weapon_abilities_makaissons_persuader` |

## usage `hp_replenish_cap_reached` (1)

| Family | Marker | Key |
|---|---|---|
| `ushoran_health` | `potion_of_healing` | `wh_main_item_abilities_potion_of_healing` |

## target `unit_is_not_hellforged` (1)

| Family | Marker | Key |
|---|---|---|
| `ally_hellforged_heal` | `reforge` | `wh3_dlc23_character_abilities_reforge` |

## target `unit_is_not_construct` (1)

| Family | Marker | Key |
|---|---|---|
| `ally_construct_heal` | `restore` | `wh2_dlc09_character_abilities_restore` |

## target `health_above_20%` (1)

| Family | Marker | Key |
|---|---|---|
| `enemy_low_health_noncommander` | `eye_of_khorne` | `wh3_dlc26_lord_abilities_eye_of_khorne` |

