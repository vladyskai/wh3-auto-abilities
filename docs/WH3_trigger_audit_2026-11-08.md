# Trigger audit, 2026-11-08

Every automated ability (700 entries) checked against the rules below by `tools/audit_triggers.py`. The effect is the game's own data; a flagged row is a candidate for review, not a decision.

| Rule | Candidates |
|---|---:|
| R1. Shooting-only buffs on a trigger with no shooting arm | 1 |
| R2. Melee AND shooting buffs on a melee-only trigger (the user asked to review these) | 12 |
| R3. Melee-only debuffs on a trigger with a missile arm (rule 10) | 23 |
| R4. Enemy slows on a trigger that is neither melee nor charge (rule 10) | 19 |
| R5. Protection against shots on a melee-only trigger | 7 |
| R6. Morale effects on a trigger with no morale read | 25 |
| R7. Speed buffs on the unit itself on a melee-only trigger | 14 |

## R1. Shooting-only buffs on a trigger with no shooting arm

| Ability | Marker | Trigger now | Effect (game data) |
|---|---|---|---|
| Boom! | `boom` | `melee_unwavering` | Armour-Piercing Explosive Damage: +20%; Base Explosive Damage: +25% (to self) |

## R2. Melee AND shooting buffs on a melee-only trigger (the user asked to review these)

| Ability | Marker | Trigger now | Effect (game data) |
|---|---|---|---|
| Embers of the Phoenix | `embers_of_the_phoenix` | `melee_unwavering` | Base Missile Damage: +25%; Base Weapon Damage: +30%; Imbues ignition: 10; Imbues magical attacks (to self and allies in range) |
| Enchanted Metallurgy | `enchanted_metallurgy` | `metallurgy_melee` | Base Missile Damage: +25%; Base Weapon Damage: +30%; Imbues magical attacks (to self and allies in range) |
| Enchanted Metallurgy: Flaming | `enchanted_metallurgy_flaming` | `metallurgy_melee` | Base Missile Damage: +50%; Base Weapon Damage: +60%; Imbues ignition: 10; Imbues magical attacks (to self and allies in range) |
| Enchanted Metallurgy: Piercing | `enchanted_metallurgy_piercing` | `metallurgy_melee` | Armour-Piercing Missile Damage: +25%; Base Missile Damage: +25%; Armour-Piercing Weapon Damage: +25%; Base Weapon Damage: +25%; Imbues magical attacks (to self and allies in range) |
| Enchanted Metallurgy: Poison | `enchanted_metallurgy_poison` | `metallurgy_melee` | Base Missile Damage: +25%; Base Weapon Damage: +30%; Imbues its target's attacks on contact: wh_main_unit_contact_poison; Imbues magical attacks (to self and allies in range) |
| Harmonic Convergence | `harmonic_convergence` | `melee_unwavering` | Melee Attack: +24; Melee Defence: +24; Reload Skill: +20 (to self and allies in range) |
| Horn of Vaul | `horn_of_vaul` | `melee_unwavering` | Base Missile Damage: +25%; Base Weapon Damage: +30% (to self and allies in range) |
| Master of Alchemy | `master_of_alchemy` | `metallurgy_melee` | Base Missile Damage: +25%; Base Weapon Damage: +30%; Imbues magical attacks (to self and allies in range) |
| Master of Alchemy: Flaming | `master_of_alchemy_flaming` | `metallurgy_melee` | Base Missile Damage: +50%; Base Weapon Damage: +60%; Imbues ignition: 10; Imbues magical attacks (to self and allies in range) |
| Master of Alchemy: Piercing | `master_of_alchemy_piercing` | `metallurgy_melee` | Armour-Piercing Missile Damage: +25%; Base Missile Damage: +25%; Armour-Piercing Weapon Damage: +25%; Base Weapon Damage: +25%; Imbues magical attacks (to self and allies in range) |
| Master of Alchemy: Poison | `master_of_alchemy_poison` | `metallurgy_melee` | Base Missile Damage: +25%; Base Weapon Damage: +30%; Imbues its target's attacks on contact: wh_main_unit_contact_poison; Imbues magical attacks (to self and allies in range) |
| The Seerstaff of Saphery | `the_seerstaff_of_saphery` | `melee_unwavering` | Melee Attack: +24; Reload Skill: +40 (to self and allies in range) |

## R3. Melee-only debuffs on a trigger with a missile arm (rule 10)

| Ability | Marker | Trigger now | Effect (game data) |
|---|---|---|---|
| Assassin's Trophy | `assassins_trophy` | `enemy_engaged_or_shot` | Melee Attack: -24; Melee Defence: -24 (to enemies in range) |
| Blight Swarm | `blight_swarm` | `enemy_engaged_or_shot` | Melee Defence: -20; Spreading area: wh3_main_lord_abilities_blight_swarm (to enemies in range); Will spread to enemies within the Spread Range metres of affected unit (positive); Affects up to five units (positive) |
| Fermented Fungi | `fermented_fungi` | `enemy_engaged_or_shot` | Melee Defence: -24; Rampage (positive) (to enemies in range) |
| Gaze of Fate | `gaze_of_fate` | `enemy_engaged_or_shot` | Melee Attack: -40; Cannot move (to enemies in range) |
| Lord of Dragons | `lord_of_dragons` | `enemy_engaged_or_shot` | Melee Attack: -40; Melee Defence: -24 (to enemies in range) |
| Master of Beguilement | `beguile` | `enemy_engaged_or_shot` | Melee Attack: -40 (to enemies in range) |
| Oath of Vengeance | `oath_of_vengeance` | `enemy_engaged_or_shot` | Melee Defence: -24 (to enemies in range) |
| Otto's Scythe | `ottos_scythe` | `enemy_engaged_or_shot` | Melee Attack: -40; Leadership: -24; Expert Charge Defence (negative); Charge Defence vs. Large (negative); Charge Reflection (negative) (to enemies in range) |
| Pestilent Potions | `pestilent_potions` | `enemy_engaged_or_shot` | Melee Attack: -24; Armour-Piercing Weapon Damage: -25%; Base Weapon Damage: -25%; Spreading area: wh3_dlc20_item_abilities_pestilent_potions (to enemies in range); Will spread to enemies within the Spread Range metres of |
| Ravaging Swarm | `dispatch_the_swarm_attack` | `enemy_engaged_or_shot` | Melee Defence: -24; Fatigue: 0.01; Spreading area: wh3_dlc29_hero_active_dispatch_the_swarm_attack (to enemies in range); Will spread to enemies within the Spread Range metres of affected unit (positive); Affects up to f |
| Ravaging Swarm Upgraded | `dispatch_the_swarm_attack_upgraded` | `enemy_engaged_or_shot` | Melee Defence: -40; Damage: 4 per hit (max 10 entities); Fatigue: 0.04; Spreading area: wh3_dlc29_hero_active_dispatch_the_swarm_attack (to enemies in range); Will spread to enemies within the Spread Range metres of affe |
| Sadistic Snare | `sadistic_snare` | `enemy_engaged_or_shot` | Melee Defence: -24; Cannot move (to enemies in range) |
| Spearfisher's Net | `spearfishers_net` | `enemy_engaged_or_shot` | Melee Defence: -24; Cannot move (to enemies in range) |
| The Averland Runefang | `averland_runefang` | `enemy_engaged_or_shot` | Melee Attack: -40; Base Weapon Damage: -60% (to enemies in range) |
| The Dark Master | `the_dark_master` | `enemy_engaged_or_shot` | Melee Attack: -40 (to enemies in range) |
| The Enfeebling Foe | `enfeebling_foe` | `enemy_engaged_or_shot` | Melee Attack: -24; Melee Defence: -24 (to enemies in range) |
| The Hammer of Karak Drazh | `the_hammer_of_karak_drazh` | `enemy_engaged_or_shot` | Melee Attack: -40; Base Weapon Damage: -30% (to enemies in range) |
| Torment Blade | `torment_blade` | `enemy_engaged_or_shot` | Melee Attack: -24; Armour-Piercing Weapon Damage: -25%; Base Weapon Damage: -25% (to enemies in range) |
| Trophy Heads | `trophy_heads` | `enemy_engaged_or_shot` | Melee Attack: -24; Melee Defence: -40 (to enemies in range) |
| Virulent Contagion | `virulent_contagion` | `enemy_engaged_or_shot` | Melee Defence: -40; Spreading area: wh3_main_lord_abilities_virulent_contagion (to enemies in range); Will spread to enemies within the Spread Range metres of affected unit (positive); Affects up to five units (positive) |
| Virulent Contagion Upgraded | `virulent_contagion_upgraded` | `enemy_engaged_or_shot` | Melee Defence: -50; Spreading area: wh3_main_lord_abilities_virulent_contagion (to enemies in range); Will spread to enemies within the Spread Range metres of affected unit (positive); Affects up to five units (positive) |
| Whip of Agony | `whip_of_agony` | `enemy_engaged_or_shot` | Melee Defence: -24; Causes Fear (negative); Causes Terror (negative) (to enemies in range) |
| Willing Prey | `willing_prey` | `enemy_engaged_or_shot` | Melee Attack: -24; Melee Defence: -40 (to enemies in range) |

## R4. Enemy slows on a trigger that is neither melee nor charge (rule 10)

| Ability | Marker | Trigger now | Effect (game data) |
|---|---|---|---|
| Acquiescence | `acquiescence` | `enemy_engaged_or_shot` | Speed: -25%; Melee Defence: -24 (to enemies in range) |
| Book of Secrets | `book_of_secrets` | `enemy_engaged_or_shot` | Damage: 10 per hit (max 25 entities) (to enemies in range); Speed: -25%; Weakness to Fire Damage: -20 (to enemies in range); Melee Attack: -24; Melee Defence: -24 (to enemies in range) |
| El Syf | `el_syf` | `enemy_engaged_or_shot` | Speed: -45%; Melee Defence: -40; Physical Resistance: -20 (to enemies in range) |
| Fecund Rebirth | `mark_of_the_monster` | `enemy_engaged_or_shot` | Charge Speed: -50%; Speed: -50%; Incoming Healing Modifier: -100%; Damage: 38 per hit (max 1 entities) (to enemies in range); Causes damage to combatants (positive); Strong vs a single combatant (positive) |
| Frost Shard Glaive | `frost_shard_glaive` | `enemy_engaged_or_shot` | Speed: -45%; Melee Defence: -40 (to enemies in range) |
| Hidden Huntress | `hidden_huntress` | `enemy_engaged_or_shot` | Speed: -25%; Melee Defence: -24 (to enemies in range) |
| Hidden Huntress Upgraded | `hidden_huntress_upgraded` | `enemy_engaged_or_shot` | Speed: -25%; Armour: -30; Melee Defence: -40 (to enemies in range) |
| Hornswaggle | `hornswaggle` | `enemy_engaged_or_shot` | Speed: -25%; Armour: -30; Melee Defence: -24 (to enemies in range) |
| Hunter of Champions | `hunter_of_champions` | `enemy_engaged_or_shot` | Speed: -45%; Armour: -60; Melee Defence: -40 (to enemies in range) |
| Looming Dread | `looming_dread` | `enemy_engaged_or_shot` | Speed: -45%; Melee Defence: -24; Missile Resistance: -20 (to enemies in range) |
| Marked for Eatin' | `marked_for_eatin` | `enemy_engaged_or_shot` | Speed: -25%; Armour: -30; Melee Defence: -40 (to enemies in range) |
| Master Rune of Slowness | `master_rune_of_slowness` | `enemy_engaged_or_shot` | Charge Speed: -60%; Speed: -60%; Charge Bonus: -40% (to enemies in range); Greater effect on speed (magic); Extended effect duration (magic) |
| Mither | `mither` | `enemy_engaged_or_shot` | Charge Speed: -60%; Speed: -60% (to enemies in range) |
| Rune of Slowness | `rune_of_slowness` | `enemy_engaged_or_shot` | Charge Speed: -45%; Speed: -45%; Charge Bonus: -40% (to enemies in range) |
| Taunt | `taunt` | `enemy_engaged_or_shot` | Speed: -25%; Armour: -30; Melee Defence: -24 (to enemies in range) |
| Tendrils of the Sea | `tendrils_of_the_sea` | `enemy_engaged_or_shot` | Charge Speed: -60%; Speed: -60%; Mass: -20%; Melee Attack: -40 (to enemies in range) |
| Titan Headsman | `titan_headsman` | `enemy_engaged_or_shot` | Speed: -45%; Melee Defence: -24 (to enemies in range) |
| Whispering Mist | `whispering_mist` | `enemy_engaged_or_shot` | Charge Speed: -45%; Speed: -45%; Fatigue: 0.01 (to enemies in range) |
| You're Next! | `youre_next` | `enemy_engaged_or_shot` | Speed: -45%; Melee Attack: -24; Melee Defence: -40 (to enemies in range) |

## R5. Protection against shots on a melee-only trigger

| Ability | Marker | Trigger now | Effect (game data) |
|---|---|---|---|
| Blessed Helm of the Oblast | `blessed_helm_of_the_oblast` | `melee_unwavering` | Armour: +60; Missile Resistance: +20 (to self and allies in range) |
| Charmed Shield | `charmed_shield` | `melee_unwavering` | Missile Block Chance: +25; Damage Resistance: +20 (to self) |
| Glacial Defence | `glacial_defence` | `melee_unwavering` | Speed: -25%; Armour: +60; Missile Resistance: +20 (to self) |
| Shield of Chaqua | `shield_of_chaqua` | `melee_unwavering` | Missile Resistance: +40 (to self and allies in range) |
| The Bane Shield | `the_bane_shield` | `melee_unwavering` | Armour: +30; Missile Block Chance: +24 (to self and allies in range) |
| The Golden Eye of Tzeentch | `the_golden_eye_of_tzeentch` | `melee_unwavering` | Missile Resistance: +40; Barrier restore: 0.008 (to self) |
| The Lion's Shield | `lions_shield` | `melee_unwavering` | Spell Resistance: +40; Missile Resistance: +40 (to self) |

## R6. Morale effects on a trigger with no morale read

| Ability | Marker | Trigger now | Effect (game data) |
|---|---|---|---|
| Axe of Men | `axe_of_men` | `melee_unwavering` | Causes Terror (positive); Unbreakable (positive) (to self) |
| Call of Violence | `call_of_violence` | `melee_unwavering` | Leadership: +16 (to self and allies in range) |
| Change or Die! | `change_or_die` | `melee_unwavering` | Leadership: +16; Damage Resistance: +20 (to self and allies in range) |
| Cold-Blooded | `cold_blooded` | `melee_unwavering` | Leadership: +16; Rampage (negative) (to self and allies in range) |
| Crown of Command | `crown_of_command` | `melee_unwavering` | Unbreakable (positive) (to self and allies in range) |
| Daemonic Whispers | `slezuzus_voice` | `ally_melee_buff` | Leadership: +16; Causes Fear (positive); Causes Terror (positive) (to allies in range) |
| Doom Lord | `doom_lord` | `melee_unwavering` | Cannot Die (positive); Rampage (negative); Unbreakable (positive) (to self and allies in range) |
| Get Back 'Ere! | `get_back_ere` | `melee_unwavering` | Leadership: +16 (to self and allies in range) |
| Ghoul King of Ushoran | `ghoul_king_of_ushoran` | `ushoran_health` | Leadership: +8; Heals: 0.008 per tick every 1 s (to self); Replenishes hit points of combatants (positive) |
| Gulyas | `gulyas` | `health_aura_ground` | Leadership: +4; Heals: 0.0008 per tick every 1 s; Fatigue: -0.01 (to self and allies in range) |
| Magical Animus | `magical_animus` | `melee_unwavering` | Leadership: +16 (to self and allies in range) |
| Mirror (Cold-Blooded) | `mimic_cold_blooded` | `melee_unwavering` | Leadership: +16; Rampage (negative); Fatigue: -0.1 (to self and allies in range) |
| Pearl of Infinite Bleakness | `pearl_of_infinite_bleakness` | `melee_unwavering` | Leadership: +8; Immune to Psychology (positive) (to self and allies in range) |
| Pilgrimage of Skulls | `pilgrimage_of_skulls` | `melee_unwavering` | Unbreakable (positive); Fatigue: -0.01 (to self and allies in range) |
| Purge the Weak! | `purge_the_weak` | `charge_or_melee` | Speed: +30%; Leadership: +6; Fatigue: -0.02 (to self) |
| Rally! | `rally` | `melee_unwavering` | Leadership: +16 (to self and allies in range) |
| Reanimate | `tomb_king_rally` | `melee_unwavering` | Leadership: +16 (to self and allies in range) |
| Reanimate Upgraded | `tomb_king_rally_upgraded` | `melee_unwavering` | Leadership: +16; Heals: 0.008 per tick every 1 s (to self and allies in range); Replenishes hit points of combatants (positive) |
| Rot or Die! | `rot_or_die` | `melee_unwavering` | Melee Damage Reflection: +20; Leadership: +16; Spreading area: wh3_dlc25_lord_abilities_rot_or_die (to self and allies in range); Will spread to friends within the Spread Range metres of affected unit (positive) |
| Scrying Stone | `scrying_stone` | `melee_unwavering` | Leadership: +8; Damage Resistance: +20 (to self) |
| Shield of the Old Ones | `shield_of_the_old_ones` | `melee_unwavering` | Leadership: +8; Damage Resistance: +20 (to self and allies in range) |
| Tacticians, Rally! | `tacticians_rally` | `melee_unwavering` | Leadership: +16 (to self and allies in range); Extended cast range (magic) |
| The Liber Mortis | `the_liber_mortis` | `melee_unwavering` | Leadership: +8; Physical Resistance: +40 (to self and allies in range) |
| Unholy Clamour | `unholy_clamour` | `melee_unwavering` | Leadership: +16; Fatigue: -0.01 (to self and allies in range) |
| Verminous Fury | `verminous_fury` | `ally_melee_buff` | Rampage (positive); Unbreakable (positive); Unyielding Assault (positive) (to allies in range) |

## R7. Speed buffs on the unit itself on a melee-only trigger

| Ability | Marker | Trigger now | Effect (game data) |
|---|---|---|---|
| Apocalyptic Charge | `apocalyptic_charge` | `melee_unwavering` | Charge Speed: +10%; Charge Bonus: +20% (to self and allies in range) |
| Blooood! | `blooood` | `melee_unwavering` | Acceleration: +18%; Speed: +25%; Fatigue: -0.02 (to self) |
| Book of Arkhan | `book_of_arkhan` | `melee_unwavering` | Speed: +25%; Melee Attack: +24 (to self and allies in range) |
| Lightning Reflexes | `lightning_reflexes` | `melee_unwavering` | Speed: +25%; Damage Resistance: +20 (to self) |
| Master Rune of Speed | `master_rune_of_speed` | `melee_unwavering` | Speed: +45%; Melee Attack: +24 (to self and allies in range); Extended effect duration (magic) |
| Master of the Skies | `master_of_the_skies` | `melee_unwavering` | Speed: +25%; Melee Defence: +40 (to self) |
| Pendant of Slaanesh | `pendant_of_slaanesh` | `melee_unwavering` | Speed: +25%; Melee Attack: +40 (to self) |
| Potion of Speed | `potion_of_speed` | `melee_unwavering` | Charge Speed: +25%; Acceleration: +18%; Speed: +25%; Fatigue: -0.01 (to self) |
| Rune of Speed | `rune_of_speed` | `melee_unwavering` | Speed: +45%; Melee Attack: +24 (to self and allies in range) |
| Slippery | `slippery` | `melee_unwavering` | Speed: +25%; Melee Defence: +24 (to self) |
| Thunderburner | `thunderburner` | `melee_unwavering` | Turn Speed: -70%; Speed: +150%; Damage: 30 per hit (max 1 entities) (to self) |
| Thunderburner Upgraded | `thunderburner_upgraded` | `melee_unwavering` | Turn Speed: -70%; Speed: +200%; Damage: 10 per hit (max 1 entities) (to self) |
| Transfix | `transfix` | `melee_unwavering` | Speed: +25%; Damage Resistance: +20; Imbues its target's attacks on contact: wh_dlc06_unit_contact_discouraged (to self) |
| Twilight Horn I | `twilight_horn_i` | `melee_unwavering` | Charge Speed: +25%; Speed: +25%; Charge Bonus: +20% (to self and allies in range) |
