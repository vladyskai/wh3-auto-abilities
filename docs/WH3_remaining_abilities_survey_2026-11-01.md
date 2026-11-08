# The 362 abilities not yet automated: what the firing flag changes (survey, 2026-11-01)

Source: workbook v22 (`docs\WH3_abilities_master_v22_2026-11-01.xlsx`), every IN-WHEEL row that is not IMPLEMENTED, joined to the tracker's own decision for each key (rule 11). Carriers come from `land_abil.tsv` and the spell-group junctions; abilities granted only by an item or a skill have no carrier row in the data, so whether their bearer shoots is unknown from the tables. Nothing here is decided: every trigger needs the user's ruling.

| Group | Rows | What it is |
|---|---:|---|
| A | 6 | missile buffs or ammo refills, not yet automated: the firing flag is exactly their trigger |
| B | 112 | attack projectiles cast at an enemy (magic missiles, bombs, breaths); the old reasons ('no enemy-unit read', 'explosive projectile') no longer hold |
| C | 24 | other out-of-date exclusions (stats now known, enemy-ground and ground casts now exist, summons now exist) |
| D | 187 | your own decisions (rejected, skipped, and the 2026-10-09 friendly-fire / stealth family decisions): they stand unless you reopen them |
| E | 33 | self-centred explosions and vortices that hurt nearby troops, and one magic-scope row: no change proposed |
| total | 362 | |

## Group A: missile buffs and refills (6)

- **Master of Mists** `wh3_dlc27_character_abilities_master_of_mists`: Armour-Piercing Missile Damage: +25%; Base Missile Damage: +25%; Range: +50%; Reload Skill: +20; Snipe (positive); Stalk (positive). Range: target_intercept_range 250 m; effect_range 35 m; targets ground. Decision: `excluded (auto: ground-target-only)`.
- **Master of Mists** `wh3_dlc27_character_abilities_master_of_mists_custom`: Armour-Piercing Missile Damage: +25%; Base Missile Damage: +25%; Range: +50%; Reload Skill: +20; Snipe (positive); Stalk (positive). Range: target_intercept_range 250 m; effect_range 35 m; targets ground. Decision: `excluded (auto: ground-target-only)`.
- **More Powder!** `wh2_dlc11_hero_abilities_more_powder`: -. Range: target_intercept_range 100 m. Decision: `excluded (auto: no ammo-low read (ammo replenish))`.
- **Of Warp and Ruin** `wh3_dlc29_unit_abilities_of_warp_and_ruin`: Armour-Piercing Explosive Damage: +40%; Base Explosive Damage: +40%; scalar_missile_explosion_radius: +20%; Reload Skill: +30. Range: no range column (unlimited / self). Decision: `excluded (auto: no effect text available (unsourceable))`.
- **Ominous Powder** `wh3_dlc25_item_abilities_ominous_powder`: Armour-Piercing Missile Damage: +40%; Base Missile Damage: +40%; Reload Skill: +40; Armour-Piercing Missile Damage: +80%; Base Missile Damage: +80%; Reload Skill: +80. Range: no range column (unlimited / self). Decision: `excluded (auto: no effect text available (unsourceable))`.
- **Restock!** `wh3_dlc25_abilities_restock_gunnery_school`: -. Range: target_intercept_range 100 m. Decision: `excluded (auto: no ammo-low read (ammo replenish))`.

## Group B: attack projectiles at an enemy (112)

Carrier check: 'shoots' = every unit in the data that carries it has a missile weapon.

**Every carrier shoots (14):** Arrow of Aqshy, Arrow of Kurnous (explosive), Big Boom (explosive), Bomb-Throw (explosive), Cackle Fruit (explosive), Cinderblast Cluster Bomb (explosive), Crippling Throw (explosive), Focused Shot, Mercurial Shot, Spear of Grungni, Spirit Bear, Taal's Judgement, Volley of Dark Arrows (explosive), Volley of High Arrows (explosive).

**Some carriers shoot (6):** Death Shriek (explosive), Flaming Breath (explosive), Moon Dragon's Breath (explosive), Noxious Breath (explosive), Soporific Breath (explosive), Star Dragon's Breath (explosive).

**No carrier shoots (36):** 'Effagee' of da Git, Bellow of Endless Fury (explosive), Bellow of Fury (explosive), Bilespurt (explosive), Copious Vomit (explosive), Coruscating Blast (explosive), Damned Pistol, Dark Fire of Chaos (explosive), Dead Eye, Doomrocket (explosive), Elemental Breath (explosive), Fiery Breath (explosive), Fire Breath (explosive), Flaming Breath (explosive), Frost Breath (explosive), Gordinar's Dragon Breath (explosive), Ice Shard (explosive), Lamentation of Despairs (Empowered) (explosive), Lamentation of Despairs (explosive), Maelstrom of Change, Otherworldly Pestilence, Pestilent Torrent (explosive), Pestilential Breath (explosive), Preyton Horns, Shackolot's Noxious Breath (explosive), Shadowblood, Shem's Burning Gaze, Spirit Leech, Storm of the Night, Sun Dragon's Breath (explosive), Swamp Breath, The Emperor's Executioner, The Gaze of Dust, Unspeakable Foulness (explosive).

**Item or skill only (carrier unknown) (56):** Amber Bow, Blast (explosive), Blood Statuette of Spite, Bolt Storm (explosive), Bow of the Seafarer (explosive), Burning Wrath, Chain Lightning, Cinderblast Shell (explosive), Cracklebomb (explosive), Darkened Mist, Dart of Doom, Death's Timekeeper, Dire Spirit Bear, Dweomer Leach Orb, Eagle Quiver, Ethrac's Brazier, Executioner, Experimental Explosive (explosive), Fireball, Fireball Upgraded, Gaze of Nagash, Goggly Glare, Hail of Doom Arrow, Hand of Gods, Hunting Spear (explosive), Ice Breath (explosive), Master Rune of Flight (explosive), Punch-Dagger, Pyromaniac (explosive), Quiver of Aqshy, Rancid Visitations, Reaver Bow (explosive), Schalkain's Teeth, Skarsnik's Prodder (explosive), Spear of Kurnous, Spirit Leech, Staff of Masks, Sting of Snagla, Storm Daemon (explosive), The Amber Spear (explosive), The Amber Trance, The Emperor's Executioner, The Fate of Bjuna, The Golden Blowpipe of P'Toohee, The Liber Bubonicus, The Moonbow (explosive), The Venom Staff (explosive), The Windblade, Vindictive Glare, Volley of Kurnous, Warp-Fireball, Wind Bow.

## Group C: other out-of-date exclusions (24)

- **Soulblight** `wh3_dlc29_spell_bound_soulblight` (Augment · targeting: self (always affect): -. Decision: `excluded (auto: ground-target-only)`.
- **Spinning Loons** `wh_main_unit_abilities_spinning_loons` (Vortex · targeting: ground (area placed)): -. Decision: `excluded (auto: summon)`.
- **The Loons of Eight Peaks** `wh_dlc06_unit_abilities_the_loons_of_eight_peaks` (Vortex · targeting: ground (area placed)): -. Decision: `excluded (auto: summon)`.
- **Curse of Djaf** `wh2_dlc09_character_abilities_curse_of_djaf` (Hex (Area) · targeting: ground (area pla): Rampage (positive). Decision: `excluded (auto: ground-target-only)`.
- **Soulblight** `wh2_dlc10_spell_bound_soulblight` (Hex (Area) · targeting: ground (area pla): Armour: -30; Armour-Piercing Weapon Damage: -25%; Base Weapon Damage: -25%. Decision: `excluded (auto: ground-target-only)`.
- **The Curse of Anraheir** `wh2_dlc16_spell_bound_the_curse_of_anraheir` (Hex · targeting: ground (area placed) + ): Speed: -25%; Accuracy: -30; Melee Attack: -24; Melee Defence: -24. Decision: `excluded (auto: ground-target-only)`.
- **The Curse of Anraheir** `wh3_main_spell_bound_the_curse_of_anraheir` (Hex · targeting: ground (area placed) + ): Speed: -25%; Accuracy: -30; Melee Attack: -24; Melee Defence: -24. Decision: `excluded (auto: ground-target-only)`.
- **The Curse of Anraheir** `wh_dlc05_spell_bound_the_curse_of_anraheir` (Hex · targeting: ground (area placed) + ): Speed: -25%; Accuracy: -30; Melee Attack: -24; Melee Defence: -24. Decision: `excluded (auto: ground-target-only)`.
- **Transmutation of Lead** `wh3_main_spell_bound_transmutation_of_lead` (Hex (Area) · targeting: ground (area pla): Melee Attack: -24; Base Weapon Damage: -30%. Decision: `excluded (auto: ground-target-only)`.
- **Icon of the King** `wh3_dlc29_item_abilities_icon_of_the_king` (Regeneration · targeting: self (always a): Heals: 0.008 per tick every 1 s. Decision: `excluded (auto: no effect text available (unsourceable))`.
- **Cloak of the Dunes** `wh2_dlc09_item_abilities_cloak_of_the_dunes` (Hiding · targeting: self (always affects): Stalk (positive); Unspottable (positive). Decision: `excluded (auto: no effect text available (unsourceable))`.
- **Hag's Denial** `wh3_dlc24_unit_abilities_hags_denial` (Ward Save · targeting: self (always affe): Damage Resistance: +40; Cannot Die (positive). Decision: `excluded (auto: no effect text available (unsourceable))`.
- **Hunter's Call** `wh2_dlc13_character_ability_hunters_call` (Augment (Area) · targeting: self (always): Melee Defence: +24; Unbreakable (positive). Decision: `excluded (auto: no effect text available (unsourceable))`.
- **Rock Bottom** `wh2_dlc15_unit_abilities_rock_bottom` (Augment · targeting: self (always affect): -. Decision: `excluded (auto: no effect text available (unsourceable))`.
- **Ruinshelter** `wh2_dlc15_unit_abilities_mimic_ruinshelter` (Augment · targeting: self (always affect): Speed: -60%; Armour: +45; Melee Attack: +8; Melee Defence: +10. Decision: `excluded (auto: no effect text available (unsourceable))`.
- **Storm of Blades** `wh_dlc05_unit_abilities_storm_of_blades` (Augment · targeting: self (always affect): Melee Attack: +24; Melee Defence: -24. Decision: `excluded (auto: no effect text available (unsourceable))`.
- **The Gold Standard** `wh3_dlc25_item_abilities_the_gold_standard` (Augment · targeting: allies + self): Invulnerable (positive). Decision: `excluded (auto: no effect text available (unsourceable))`.
- **Whirling Death** `wh2_dlc16_unit_abilities_whirling_death` (Augment · targeting: self (always affect): Armour-Piercing Weapon Damage: -10; Base Weapon Damage: +25. Decision: `excluded (auto: no effect text available (unsourceable))`.
- **Banner of Hellfire** `wh3_main_banner_abilities_banner_of_hellfire` (Direct Damage (Area) · targeting: no exp): -. Decision: `excluded (auto: no effect text available (unsourceable))`.
- **Ghostly Howl** `wh3_dlc29_hero_active_ghostly_howl` (Direct Damage · targeting: enemy units): Leadership: -16. Decision: `excluded (auto: no effect text available (unsourceable))`.
- **Morikhane, the Black Armour** `wh3_dlc29_item_abilities_morikhane_the_black_armour` (Hex (Area) · targeting: no explicit targ): -. Decision: `excluded (auto: no effect text available (unsourceable))`.
- **Petrifying Gaze** `wh3_dlc24_unit_passive_petrifying_gaze` (Hex · targeting: enemy units): Speed: -25%; Speed: -50%; Speed: -75%. Decision: `excluded (auto: no effect text available (unsourceable))`.
- **Squig Thinkin'** `wh3_dlc26_character_abilities_squig_thinkin` (Summon Unit · targeting: ground (area pl): -. Decision: `excluded (auto: summon)`.
- **The Soulstealer** `wh3_dlc29_spell_bound_undeath_khizaar_the_soulstealer` (Direct Damage (Area) · targeting: ground): -. Decision: `excluded (auto: enemy-ground placement (no placement path))`.

## Group D: your decisions (187)

- `excluded (auto: vortex / wandering wind (friendly fire, family decision 2026-10-09))` (34): Arnzipal's Black Horror, Banishment, Bound Fiery Convocation, Burning Alignment, Fiery Convocation, Flame Storm, Gehenna's Golden Globe, Gehenna's Golden Hounds, Gilded Horn of Galon Konook, Heaven's Gate, Hell Hammer, Hounds of Orion, Lesser Banishment, Lesser Chain Lightning, Nightmaw, Sandstorm, Seafang, Soul-slaying Hunger, Sword of Khaine, The Abyssal Swarm, The Burning Head, The Dwellers Below, The Gem of Sunfire, The Penumbral Pendulum, The Purple Sun of Xereus, The Ruination of Cities, Wall of Wind & Fire, Wind of Death, Wrath of Manann.
- `excluded (auto: placed / static area damage (friendly fire, family decision 2026-10-09))` (28): Acorns of the Oak of Ages, Arcane Vassal, Befuddlement of Mischiefs, Blight Boil, Boiling Cauldron, Brass Orb, Brass Orb Upgraded, Chain Lightning, Crackleblaze, Frost Fang, Infernal Gateway, Irresistible Plague!, Lamprey's Bite, Magma Storm, Master Rune of Wrath & Ruin, Pit of Shades, Plaguemaster, Rubric of Dark Dimensions, Rune of Wrath & Ruin, Siegebreaker, Simmering Pot, The Hammer of Smednir, Viletide, Warp Junction, Winged Staff.
- `excluded (auto: breath / cone damage (friendly fire, family decision 2026-10-09))` (28): Bangstick, Black Dragon Egg, Blue Fire of Chaos, Blue Fire of Chaos Upgraded, Da Boss' Loons, Disembowelling Sweep, Fiery Ring of Thori, Fishy Breath, Flesh-eating Scarabs, Gaze of Malice, Jade Lion's Breath, Kovsh Breath, Lash of Slaanesh, Pestilent Breath, Pink Fire of Tzeentch, Scorch, Shatter, Skabscrath, Stream of Corruption, Sunfang, The Spear Slaupnir, Tidecall, Wind Blast.
- `excluded (auto: own-troop-damage AoE (friendly fire by design, family decision 2026-10-09))` (19): Defiling Deluge, Flock of Doom, Murderous Exhortations, Plaguereaper, Raging Tornado, Reaper of Souls, Ring of Corin, Rod of Corruption, Shard Blade, Soul Stealer, Sword of Daith, Wail of Malice, Warp-Quake, Warpstorm Scroll, Web of Shadows, Zefet-nebtar, the Mortis Blade.
- `skipped (unsuitable: vortex)` (17): Alakanash, the Staff of Power, Ark of Sotek, Celestial Sweep, Cellular Instability, Destruction, Eruption, Ferocious Destruction, Glacial Blast, Kill for Khorne!, Sonic Boom, Splode da Big 'Un!, The Hammer of Harry, Thundermace, Venom Wave, Whirlwind of Death, Whirlwind of Death Upgraded, Wrath of Ptra.
- `skipped (user decision 2026-10-17: no automation wanted)` (12): Burrow, Formless Horror, Surface, Transformation of the Dragon.
- `skipped (revisit)` (9): Beastlord's Gaze, Fog of the Damned, Locus of Contagion, Mad Cap Mushrooms, Mirror of Knowledge, Offering to the Gods, Seismic Snare, The Black Gem of Gnar.
- `excluded (auto: flanking / ambush (stealth/escape, family decision 2026-10-09))` (7): Armour of the Stars, Concealment Bombs, From the Shadows, Hidden in Time, Loec's Shroud, Mirror (Loec's Shroud).
- `excluded (impossible: already rejected by user (tactical escape/stealth))` (7): Eagle Bow, Envelop in Mist, Loec's Blessing, Perfect Predator, Skitterleap, Speed of Lykos, Tricksy Traps.
- `rejected (auto: mutual exclusivity)` (5): Bastion of the Great Cities, Disdain of the Dragon Emperor, Fury of the Falling Blade, Harbinger of Pestilence, Healing Elixirs.
- `rejected (drawback)` (4): Daggerdance, Dance of Destruction, Dinner Bell, Harvestman's Scythe.
- `skipped (unsuitable: movement)` (3): Battle Howl, Twilight Horn II.
- `rejected (friendly fire)` (3): Acidic Musk Glands, Endless Whirlwind of Death, Endless Whirlwind of Death Upgraded.
- `rejected (tactical escape)` (2): Epidemic Outbreak, Epidemic Outburst.
- `excluded (auto: bombardment / ground artillery (friendly fire, family decision 2026-10-09))` (2): Bonecrusher, Master Rune of Immolation.
- `skipped (not achievable)` (1): Enkhil's Kanopi.
- `rejected (stealth/escape effect)` (1): From the Shadows.
- `rejected (rampage)` (1): In the Name of War.
- `skipped (unsuitable: charge-only)` (1): Silver Horn of Vengeance.
- `skipped (magic scope + self-damage)` (1): Skull of Katam.
- `skipped (unsuitable: movement/vortex)` (1): Swiftness of Itzl.
- `rejected (only useful just before a friendly spell)` (1): Daemonic Possession.

## Group E: no change proposed (33)

- `excluded (auto: vortex)` (26): Acid Burps, Arsebelcher, Blood-Forged Armour, Bloodbeast, Burning Rage, Burp of Grom, Daemon Flask of Ashak, Deathmaster's Sigil, Deep Tunneling, Emergency Vent, Feaster of Souls, Groundbreaker, Heaven's Flash, Hurricane of Death, Maneater Smoke Bomb, Mist Form, Necrotic Explosion, Shadowstrider, Slime Smoothie, Spurting Bile-Blood, Verminous Valour, Violent Wind, Whirl of Weeping Blades, Whirlwind of Pleasure.
- `excluded (auto: explosive / breath attack)` (6): Ancient Chaos Frost Dragon Scale, Emberstorm, Land Mine, Moon Flare, Slann Gold, Unidentified Hydra Head.
- `excluded (magic scope)` (1): Sword of Teclis.

## Already automated, but on a melee trigger although they only help shooting

Found in the same pass (the implemented rows whose stats are missile-only). In melee a unit does not shoot, so these buffs are spent where they do nothing. They were approved as in-melee in the 2026-10 questionnaire blocks, before the mod could tell that a unit was shooting.

- **Deranged Munitions (2 keys)**: Missile damage +50% (cast on an ally).
- **Enchanted Ballistics**: Accuracy +60, Reload Skill +20.
- **Funnel of Flame**: Reload Skill +30.
- **Hail of Fire**: Reload Skill +30.
- **The Guiding Eye**: AP missile damage +20%.
- **Morgrim's Eye**: AP missile damage +25%, Accuracy +60.
- **Locus of Change**: missile damage +25%.
- **Potion of Farsight**: Range +30% (1 use).
- **Master Predator**: Range +20%, Snipe, Unspottable, Speed -25%.
- **Entrenchment**: AP missile damage +40%, Physical Resistance +20, cannot move (mixed).

Mixed melee and missile buffs (they help both; the melee trigger is not wrong, a shooting arm could be added): Embers of the Phoenix, Horn of Vaul, Harmonic Convergence, The Seerstaff of Saphery, the eight Enchanted Metallurgy / Master of Alchemy keys. Inspired Marksmanship I/II/III (Accuracy and Reload to an ally) picks the closest missile-capable ally whether or not it is shooting.
