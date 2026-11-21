# Trigger audit, 2026-11-22

Every automated ability (985 entries) checked against the rules below by `tools/audit_triggers.py`. The effect is the game's own data; a flagged row is a candidate for review, not a decision.

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
| The Hammer of Smednir | `hammer_of_smednir` | `enemy_wander` | round 163: 'Keep the blast rule' (the x0.4 speed sits on the ability's self slot, possibly the wielder's drawback; the 15 m blast decides the trigger) |
| Warpstorm Scroll | `warpstorm_scroll` | `enemy_most_valuable` | round 186: 'No need to enforce charge, treat it just as a damage dealer. The slow is not so relevant in this case.' (enemy_most_valuable, flying only) |

## R6: kept by the user's ruling (not candidates)

| Ability | Marker | Trigger | Ruling |
|---|---|---|---|
| Axe of Men | `axe_of_men` | `melee_unwavering` | round 137: kept (morale plus a combat stat, 'Keep in melee') |
| Change or Die! | `change_or_die` | `melee_unwavering` | round 137: kept (morale plus a combat stat, 'Keep in melee') |
| Daemonic Whispers | `slezuzus_voice` | `ally_melee_buff` | round 137: kept (dedicated trigger, 'Keep all 5 for now') |
| Ghoul King of Ushoran | `ghoul_king_of_ushoran` | `ushoran_health` | round 137: kept (dedicated trigger, 'Keep all 5 for now') |
| Gulyas | `gulyas` | `health_aura_ground` | round 137: kept (dedicated trigger, 'Keep all 5 for now') |
| Preyton Horns | `preyton_horns` | `enemy_melee` | round 158: 'Horns melee, Trance waver' (enemy_melee: our fighting units +8, the enemy -8) |
| Purge the Weak! | `purge_the_weak` | `charge_or_melee` | round 137: kept (dedicated trigger, 'Keep all 5 for now') |
| Rot or Die! | `rot_or_die` | `melee_unwavering` | round 137: kept (morale plus a combat stat, 'Keep in melee') |
| Scrying Stone | `scrying_stone` | `melee_unwavering` | round 137: kept (morale plus a combat stat, 'Keep in melee') |
| Shield of the Old Ones | `shield_of_the_old_ones` | `melee_unwavering` | round 137: kept (morale plus a combat stat, 'Keep in melee') |
| The Liber Mortis | `the_liber_mortis` | `melee_unwavering` | round 137: kept (morale plus a combat stat, 'Keep in melee') |

## R8: kept by the user's ruling (not candidates)

| Ability | Marker | Trigger | Ruling |
|---|---|---|---|
| Armour of Caledor | `armour_of_caledor` | `melee_health75` | 2026-11-09: no vigour trigger ('Skip the exercise ... there is no need to add this trigger'); keeps its current trigger |
| Berry Wine | `berry_wine` | `health_aura_ally_deep` | 2026-11-09: no vigour trigger ('Skip the exercise ... there is no need to add this trigger'); keeps its current trigger |
| Blood Chalice of Bathori | `blood_chalice_of_bathori` | `health_aura_ally_rule` | 2026-11-09: no vigour trigger ('Skip the exercise ... there is no need to add this trigger'); keeps its current trigger |
| Blooood! | `blooood` | `self_moving` | 2026-11-09: no vigour trigger ('Skip the exercise ... there is no need to add this trigger'); keeps its current trigger |
| Breath of Darkness | `undeath_morkharn_breath_of_darkness` | `health_aura_ally_rule` | 2026-11-09: no vigour trigger ('Skip the exercise ... there is no need to add this trigger'); keeps its current trigger |
| Breath of Darkness Upgraded | `undeath_morkharn_breath_of_darkness_upgraded` | `health_aura_ally_rule` | 2026-11-09: no vigour trigger ('Skip the exercise ... there is no need to add this trigger'); keeps its current trigger |
| Bugman's XXXXXX | `bugmans_xxxxxx` | `self_heal_clear` | 2026-11-09: no vigour trigger ('Skip the exercise ... there is no need to add this trigger'); keeps its current trigger |
| Dreaming Ring III | `dreaming_ring_iii` | `health_aura_ally` | 2026-11-09: no vigour trigger ('Skip the exercise ... there is no need to add this trigger'); keeps its current trigger |
| Eat da Runts! | `eat_da_runts` | `eat_da_runts` | 2026-11-09: no vigour trigger ('Skip the exercise ... there is no need to add this trigger'); keeps its current trigger |
| Elvish Healing Herbs | `elfish_healing_herbs` | `ally_heal` | 2026-11-09: no vigour trigger ('Skip the exercise ... there is no need to add this trigger'); keeps its current trigger |
| Foe-Seeker | `foe_seeker` | `charge_or_tired` | 2026-11-09: no vigour trigger ('Skip the exercise ... there is no need to add this trigger'); keeps its current trigger |
| Gulyas | `gulyas` | `health_aura_ground` | 2026-11-09: no vigour trigger ('Skip the exercise ... there is no need to add this trigger'); keeps its current trigger |
| Hellish Vigour | `hellish_vigour` | `ally_in_melee` | 2026-11-09: no vigour trigger ('Skip the exercise ... there is no need to add this trigger'); keeps its current trigger |
| Hellish Vigour Upgraded | `hellish_vigour_upgraded` | `melee_unwavering` | 2026-11-09: no vigour trigger ('Skip the exercise ... there is no need to add this trigger'); keeps its current trigger |
| Icon of the King | `icon_of_the_king` | `health_aura_self_undead` | 2026-11-09: no vigour trigger ('Skip the exercise ... there is no need to add this trigger'); keeps its current trigger |
| Locus of Fecundity | `locus_of_fecundity` | `health_aura_self` | 2026-11-09: no vigour trigger ('Skip the exercise ... there is no need to add this trigger'); keeps its current trigger |
| Mantra of Invigoration | `protection_prayer` | `health_aura_ally_rule` | 2026-11-09: no vigour trigger ('Skip the exercise ... there is no need to add this trigger'); keeps its current trigger |
| Mirror (Cold-Blooded) | `mimic_cold_blooded` | `wavering_aura` | 2026-11-09: no vigour trigger ('Skip the exercise ... there is no need to add this trigger'); keeps its current trigger |
| Pilgrimage of Skulls | `pilgrimage_of_skulls` | `wavering_ally_range` | 2026-11-09: no vigour trigger ('Skip the exercise ... there is no need to add this trigger'); keeps its current trigger |
| Potion of Speed | `potion_of_speed` | `charge_only` | 2026-11-09: no vigour trigger ('Skip the exercise ... there is no need to add this trigger'); keeps its current trigger |
| Purge the Weak! | `purge_the_weak` | `charge_or_melee` | 2026-11-09: no vigour trigger ('Skip the exercise ... there is no need to add this trigger'); keeps its current trigger |
| Red Fury | `red_fury` | `self_or_ally_charge` | 2026-11-09: no vigour trigger ('Skip the exercise ... there is no need to add this trigger'); keeps its current trigger |
| Regrowth | `regrowth` | `health_aura_ally` | 2026-11-09: no vigour trigger ('Skip the exercise ... there is no need to add this trigger'); keeps its current trigger |
| Rok of Itza | `rock_of_itza` | `melee_unwavering` | 2026-11-09: no vigour trigger ('Skip the exercise ... there is no need to add this trigger'); keeps its current trigger |
| Sacred Spawning of Xhotl | `sacred_spawning_of_xhotl` | `melee_unwavering` | 2026-11-09: no vigour trigger ('Skip the exercise ... there is no need to add this trigger'); keeps its current trigger |
| Sands of Sickness | `sands_of_sickness` | `melee_unwavering` | 2026-11-09: no vigour trigger ('Skip the exercise ... there is no need to add this trigger'); keeps its current trigger |
| Skar's Kraken-Killer | `skars_kraken_killer` | `self_hurt_attacked` | 2026-11-09: no vigour trigger ('Skip the exercise ... there is no need to add this trigger'); keeps its current trigger |
| The Drakwald Runefang | `drakwald_runefang` | `melee_unwavering` | 2026-11-09: no vigour trigger ('Skip the exercise ... there is no need to add this trigger'); keeps its current trigger |
| Unholy Clamour | `unholy_clamour` | `wavering_aura` | 2026-11-09: no vigour trigger ('Skip the exercise ... there is no need to add this trigger'); keeps its current trigger |
