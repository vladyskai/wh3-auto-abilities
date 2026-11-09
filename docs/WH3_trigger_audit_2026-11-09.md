# Trigger audit, 2026-11-09

Every automated ability (698 entries) checked against the rules below by `tools/audit_triggers.py`. The effect is the game's own data; a flagged row is a candidate for review, not a decision.

| Rule | Candidates |
|---|---:|
| R1. Shooting-only buffs on a trigger with no shooting arm | 0 |
| R2. Melee AND shooting buffs on a melee-only trigger (the user asked to review these) | 0 |
| R3. Melee-only debuffs on a trigger with a missile arm (rule 10) | 0 |
| R4. Enemy slows on a trigger that is neither melee nor charge (rule 10) | 0 |
| R5. Protection against shots on a melee-only trigger | 0 |
| R6. Morale effects on a trigger with no morale read | 0 |
| R7. Speed buffs on the unit itself on a melee-only trigger | 0 |
| R8. Vigour restorers not on a fatigue trigger (the user's one-by-one review) | 0 |

## R1. Shooting-only buffs on a trigger with no shooting arm

None.

## R2. Melee AND shooting buffs on a melee-only trigger (the user asked to review these)

None.

## R3. Melee-only debuffs on a trigger with a missile arm (rule 10)

None.

## R4. Enemy slows on a trigger that is neither melee nor charge (rule 10)

None.

## R5. Protection against shots on a melee-only trigger

None.

## R6. Morale effects on a trigger with no morale read

None.

## R7. Speed buffs on the unit itself on a melee-only trigger

None.

## R8. Vigour restorers not on a fatigue trigger (the user's one-by-one review)

None.

## R4: kept by the user's ruling (not candidates)

| Ability | Marker | Trigger | Ruling |
|---|---|---|---|
| Book of Secrets | `book_of_secrets` | `enemy_engaged_or_shot` | round 135: 'Keep as is' (no target filter in the game data) |
| Fecund Rebirth | `mark_of_the_monster` | `enemy_engaged_or_shot` | round 135: 'Keep as is' (large single-entity filter) |
| Hunter of Champions | `hunter_of_champions` | `enemy_engaged_or_shot` | round 123: 'Hunter of champions is okay for enemy_engaged_or_shot' |
| Looming Dread | `looming_dread` | `enemy_engaged_or_shot` | round 135: 'Keep as is, but make sure the trigger filters for the enemy unit type' (Lord/Hero filter) |

## R6: kept by the user's ruling (not candidates)

| Ability | Marker | Trigger | Ruling |
|---|---|---|---|
| Axe of Men | `axe_of_men` | `melee_unwavering` | round 137: kept (morale plus a combat stat, 'Keep in melee') |
| Change or Die! | `change_or_die` | `melee_unwavering` | round 137: kept (morale plus a combat stat, 'Keep in melee') |
| Daemonic Whispers | `slezuzus_voice` | `ally_melee_buff` | round 137: kept (dedicated trigger, 'Keep all 5 for now') |
| Ghoul King of Ushoran | `ghoul_king_of_ushoran` | `ushoran_health` | round 137: kept (dedicated trigger, 'Keep all 5 for now') |
| Gulyas | `gulyas` | `health_aura_ground` | round 137: kept (dedicated trigger, 'Keep all 5 for now') |
| Purge the Weak! | `purge_the_weak` | `charge_or_melee` | round 137: kept (dedicated trigger, 'Keep all 5 for now') |
| Rot or Die! | `rot_or_die` | `melee_unwavering` | round 137: kept (morale plus a combat stat, 'Keep in melee') |
| Scrying Stone | `scrying_stone` | `melee_unwavering` | round 137: kept (morale plus a combat stat, 'Keep in melee') |
| Shield of the Old Ones | `shield_of_the_old_ones` | `melee_unwavering` | round 137: kept (morale plus a combat stat, 'Keep in melee') |
| The Liber Mortis | `the_liber_mortis` | `melee_unwavering` | round 137: kept (morale plus a combat stat, 'Keep in melee') |
| Verminous Fury | `verminous_fury` | `ally_melee_buff` | round 137: kept (dedicated trigger, 'Keep all 5 for now') |

## R8: kept by the user's ruling (not candidates)

| Ability | Marker | Trigger | Ruling |
|---|---|---|---|
| Armour of Caledor | `armour_of_caledor` | `melee_unwavering` | 2026-11-09: no vigour trigger ('Skip the exercise ... there is no need to add this trigger'); keeps its current trigger |
| Berry Wine | `berry_wine` | `health_aura_ally` | 2026-11-09: no vigour trigger ('Skip the exercise ... there is no need to add this trigger'); keeps its current trigger |
| Blood Chalice of Bathori | `blood_chalice_of_bathori` | `ushoran_health` | 2026-11-09: no vigour trigger ('Skip the exercise ... there is no need to add this trigger'); keeps its current trigger |
| Blooood! | `blooood` | `charge_only` | 2026-11-09: no vigour trigger ('Skip the exercise ... there is no need to add this trigger'); keeps its current trigger |
| Breath of Darkness | `undeath_morkharn_breath_of_darkness` | `ushoran_health` | 2026-11-09: no vigour trigger ('Skip the exercise ... there is no need to add this trigger'); keeps its current trigger |
| Breath of Darkness Upgraded | `undeath_morkharn_breath_of_darkness_upgraded` | `ushoran_health` | 2026-11-09: no vigour trigger ('Skip the exercise ... there is no need to add this trigger'); keeps its current trigger |
| Bugman's XXXXXX | `bugmans_xxxxxx` | `ushoran_health` | 2026-11-09: no vigour trigger ('Skip the exercise ... there is no need to add this trigger'); keeps its current trigger |
| Dreaming Ring III | `dreaming_ring_iii` | `health_aura_ally` | 2026-11-09: no vigour trigger ('Skip the exercise ... there is no need to add this trigger'); keeps its current trigger |
| Eat da Runts! | `eat_da_runts` | `eat_da_runts` | 2026-11-09: no vigour trigger ('Skip the exercise ... there is no need to add this trigger'); keeps its current trigger |
| Elvish Healing Herbs | `elfish_healing_herbs` | `ally_heal` | 2026-11-09: no vigour trigger ('Skip the exercise ... there is no need to add this trigger'); keeps its current trigger |
| Gulyas | `gulyas` | `health_aura_ground` | 2026-11-09: no vigour trigger ('Skip the exercise ... there is no need to add this trigger'); keeps its current trigger |
| Hellish Vigour | `hellish_vigour` | `ally_melee_buff` | 2026-11-09: no vigour trigger ('Skip the exercise ... there is no need to add this trigger'); keeps its current trigger |
| Hellish Vigour Upgraded | `hellish_vigour_upgraded` | `melee_unwavering` | 2026-11-09: no vigour trigger ('Skip the exercise ... there is no need to add this trigger'); keeps its current trigger |
| Locus of Fecundity | `locus_of_fecundity` | `health_aura_self` | 2026-11-09: no vigour trigger ('Skip the exercise ... there is no need to add this trigger'); keeps its current trigger |
| Mantra of Invigoration | `protection_prayer` | `ushoran_health` | 2026-11-09: no vigour trigger ('Skip the exercise ... there is no need to add this trigger'); keeps its current trigger |
| Mirror (Cold-Blooded) | `mimic_cold_blooded` | `wavering_aura` | 2026-11-09: no vigour trigger ('Skip the exercise ... there is no need to add this trigger'); keeps its current trigger |
| Pilgrimage of Skulls | `pilgrimage_of_skulls` | `wavering_ally_range` | 2026-11-09: no vigour trigger ('Skip the exercise ... there is no need to add this trigger'); keeps its current trigger |
| Potion of Speed | `potion_of_speed` | `charge_only` | 2026-11-09: no vigour trigger ('Skip the exercise ... there is no need to add this trigger'); keeps its current trigger |
| Purge the Weak! | `purge_the_weak` | `charge_or_melee` | 2026-11-09: no vigour trigger ('Skip the exercise ... there is no need to add this trigger'); keeps its current trigger |
| Red Fury | `red_fury` | `melee_unwavering` | 2026-11-09: no vigour trigger ('Skip the exercise ... there is no need to add this trigger'); keeps its current trigger |
| Regrowth | `regrowth` | `health_aura_ally` | 2026-11-09: no vigour trigger ('Skip the exercise ... there is no need to add this trigger'); keeps its current trigger |
| Rok of Itza | `rock_of_itza` | `melee_unwavering` | 2026-11-09: no vigour trigger ('Skip the exercise ... there is no need to add this trigger'); keeps its current trigger |
| Sacred Spawning of Xhotl | `sacred_spawning_of_xhotl` | `melee_unwavering` | 2026-11-09: no vigour trigger ('Skip the exercise ... there is no need to add this trigger'); keeps its current trigger |
| Sands of Sickness | `sands_of_sickness` | `melee_unwavering` | 2026-11-09: no vigour trigger ('Skip the exercise ... there is no need to add this trigger'); keeps its current trigger |
| Skar's Kraken-Killer | `skars_kraken_killer` | `ushoran_health` | 2026-11-09: no vigour trigger ('Skip the exercise ... there is no need to add this trigger'); keeps its current trigger |
| The Drakwald Runefang | `drakwald_runefang` | `melee_unwavering` | 2026-11-09: no vigour trigger ('Skip the exercise ... there is no need to add this trigger'); keeps its current trigger |
| Unholy Clamour | `unholy_clamour` | `wavering_aura` | 2026-11-09: no vigour trigger ('Skip the exercise ... there is no need to add this trigger'); keeps its current trigger |
