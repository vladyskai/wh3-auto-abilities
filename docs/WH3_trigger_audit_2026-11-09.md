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
| R8. Vigour restorers not on a fatigue trigger (the user's one-by-one review) | 27 |

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

| Ability | Marker | Trigger now | Effect (game data) |
|---|---|---|---|
| Armour of Caledor | `armour_of_caledor` | `melee_unwavering` | Heals: 0.016 per tick every 1 s; Fatigue: -0.1; Cannot move; Own ability recharge: -120 s (to self) |
| Berry Wine | `berry_wine` | `health_aura_ally` | Heals: 0.016 per tick every 0.5 s; Fatigue: -0.1 (to self and allies in range) |
| Blood Chalice of Bathori | `blood_chalice_of_bathori` | `ushoran_health` | Heals: 0.016 per tick every 1 s; Fatigue: -0.02 (to self and allies in range); Greatly replenishes hit points of combatants (positive) |
| Blooood! | `blooood` | `charge_only` | Acceleration: +18%; Speed: +25%; Fatigue: -0.02 (to self) |
| Breath of Darkness | `undeath_morkharn_breath_of_darkness` | `ushoran_health` | Heals: 0.008 per tick every 1 s; Resurrects models; Fatigue: -0.01 (to self and allies in range) |
| Breath of Darkness Upgraded | `undeath_morkharn_breath_of_darkness_upgraded` | `ushoran_health` | Heals: 0.008 per tick every 1 s; Resurrects models; Fatigue: -0.01 (to self and allies in range) |
| Bugman's XXXXXX | `bugmans_xxxxxx` | `ushoran_health` | Heals: 0.017 per tick every 1 s; Fatigue: -0.01 (to self); Replenishes hit points of combatants (positive) |
| Dreaming Ring III | `dreaming_ring_iii` | `health_aura_ally` | Heals: 0.016 per tick every 0.5 s; Fatigue: -0.1 (to self and allies in range) |
| Eat da Runts! | `eat_da_runts` | `eat_da_runts` | Damage: 144 per hit (max 1 entities) (to allies in range); Heals: 0.015 per tick every 1 s; Fatigue: -0.015 (to self and allies in range); Causes damage to allies (negative) |
| Elvish Healing Herbs | `elfish_healing_herbs` | `ally_heal` | Heals: 0.006 per tick every 1 s; Fatigue: -0.01 (to allies in range) |
| Gulyas | `gulyas` | `health_aura_ground` | Leadership: +4; Heals: 0.0008 per tick every 1 s; Fatigue: -0.01 (to self and allies in range) |
| Hellish Vigour | `hellish_vigour` | `ally_melee_buff` | Melee Damage Reflection: +20; Fatigue: -0.02 (to allies in range) |
| Hellish Vigour Upgraded | `hellish_vigour_upgraded` | `melee_unwavering` | Melee Damage Reflection: +20; Fatigue: -0.02 (to allies in range) |
| Locus of Fecundity | `locus_of_fecundity` | `health_aura_self` | Heals: 0.008 per tick every 1 s; Fatigue: -0.01 (to self and allies in range); Replenishes hit points of combatants (positive) |
| Mantra of Invigoration | `protection_prayer` | `ushoran_health` | Heals: 0.0052 per tick every 0.8 s; Fatigue: -0.01 (to self and allies in range) |
| Mirror (Cold-Blooded) | `mimic_cold_blooded` | `wavering_aura` | Leadership: +16; Rampage (negative); Fatigue: -0.1 (to self and allies in range) |
| Pilgrimage of Skulls | `pilgrimage_of_skulls` | `wavering_ally_range` | Unbreakable (positive); Fatigue: -0.01 (to self and allies in range) |
| Potion of Speed | `potion_of_speed` | `charge_only` | Charge Speed: +25%; Acceleration: +18%; Speed: +25%; Fatigue: -0.01 (to self) |
| Purge the Weak! | `purge_the_weak` | `charge_or_melee` | Speed: +30%; Leadership: +6; Fatigue: -0.02 (to self) |
| Red Fury | `red_fury` | `melee_unwavering` | Charge Bonus: +20%; Armour-Piercing Weapon Damage: +25%; Fatigue: -0.01 (to self and allies in range) |
| Regrowth | `regrowth` | `health_aura_ally` | Heals: 0.008 per tick every 1 s; Fatigue: -0.01 (to self and allies in range) |
| Rok of Itza | `rock_of_itza` | `melee_unwavering` | Physical Resistance: +40; Fatigue: -0.03 (to self) |
| Sacred Spawning of Xhotl | `sacred_spawning_of_xhotl` | `melee_unwavering` | Physical Resistance: +20; Fatigue: -0.01 (to self) |
| Sands of Sickness | `sands_of_sickness` | `melee_unwavering` | Speed: -25%; Melee Defence: -24; Spreading area: wh3_dlc25_item_abilities_sands_of_sickness_enemy (to enemies in range); Melee Damage Reflection: +20; Fatigue: -0.01; Spreading area: wh3_dlc25_item_abilities_sands_of_sic |
| Skar's Kraken-Killer | `skars_kraken_killer` | `ushoran_health` | Invulnerable (positive); Heals: 0.016 per tick every 1 s; Fatigue: -0.02 (to self) |
| The Drakwald Runefang | `drakwald_runefang` | `melee_unwavering` | Physical Resistance: +40; Fatigue: -0.03 (to self) |
| Unholy Clamour | `unholy_clamour` | `wavering_aura` | Leadership: +16; Fatigue: -0.01 (to self and allies in range) |

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
