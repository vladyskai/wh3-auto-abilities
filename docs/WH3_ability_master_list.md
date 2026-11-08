**SUPERSEDED (2026-10-16):** `docs/WH3_ability_database_master.md` is now the master reference —
it carries the same 1,797 rows PLUS the freshly extracted game data (targeting flags, real range
columns, `ai_usage`, and the invalid-target / invalid-usage / auto-deactivate RESTRICTION flag
names). This file is kept as the earlier merged list and as a cross-check.

# WARHAMMER III — Ability Master List

One consolidated, printable reference of **every ability in the project** (1,797 abilities on one row each): name, game key, mechanical effect, final status, and the logic described in plain English for a reader who cannot read Lua.

**Sources merged (nothing invented).** The authoritative inventory `WH3_ability_tracker.md` §3a/3b/3c (1,797 rows); the one-line auto-classification effects and exclude reasons in `WH3_auto_classification_report.md` (Appendices A/B/C); the family and individual effects in `WH3_remaining_triage.md`; and the block 7–9 effect lines in `WH3_blocks_7-8-9_review.md`. Where none of those carries a real mechanical effect line, the line is taken from the game's own effect tables (`%LOCALAPPDATA%\Temp\wh3\uieff\`). The **trigger family** each implemented ability rides is read directly from the mod's `ABILITIES` table (`zz_test_deadly_onslaught.lua`).

**How EFFECTS is filled.** Mechanical effect text is taken (in order) from the game's own effect tables, then the block 7–9 review effect lines, then the classification report's one-line effects. The game-data line is used first because it is the actual mechanical effect text (the report's “one-line effect” for the auto-accepted items is only a category).

**Status legend.** `implemented` = shipping in the mod today. `excluded` = no automatic logic, with the reason. `impossible` = the engine cannot support it. `rejected` = the user rejected it. `skipped` = deferred or unsuitable (not a rejection, but no code).

---

## Section 1 — Summary

### 1.1 Counts by final status

| Final status | Abilities | Share |
|---|---:|---:|
| implemented | 605 | 33.7% |
| excluded (no auto logic) | 1004 | 55.9% |
| impossible (engine limit) | 97 | 5.4% |
| rejected | 19 | 1.1% |
| skipped | 72 | 4.0% |
| **TOTAL** | **1797** | **100%** |

### 1.2 Implemented abilities — counts by trigger family

| Trigger family (Lua name) | Plain English | Abilities |
|---|---|---:|
| `melee_unwavering` | Melee — in melee and not routing/wobbling (self) | 499 |
| `ushoran_health` | Own health at or below 75%, no melee gate (self) | 42 |
| `charge_or_melee` | Charge window OR melee (self) | 31 |
| `metallurgy_melee` | Owner in melee OR a friendly unit in range in melee (self) | 8 |
| `tired` | Fatigue — Tired or worse (self) | 5 |
| `wavering_self` | Owner wavering (self) | 3 |
| `melee` | Melee — plain in-melee (self) | 2 |
| `melee_health75` | Melee AND own health at or below 75% (self) | 2 |
| `melee_low_morale` | Melee + low morale (self) | 2 |
| `wavering_self_or_ally` | Owner OR an in-melee ally in range wavering (self) | 2 |
| `barrier_broken` | Barrier broken (self) | 1 |
| `blood_sacrifice` | Custom — health-based ally heal at a cost | 1 |
| `charge` | Charge window OR melee (self) | 1 |
| `charge_only` | Charge window only (self) | 1 |
| `charge_or_wavering` | Charge window OR wavering (self) | 1 |
| `eat_da_runts` | Custom — health-based self/ally heal at a cost | 1 |
| `glorious_death` | A Slayer ally in melee (Slayer-only, self/ally) | 1 |
| `verminking_wavering` | An ally in range is in melee AND wavering (self) | 1 |
| `wavering_ally_range` | A wavering ally in range, no melee gate (ally) | 1 |
| **TOTAL** | | **605** |

### 1.3 Excluded / impossible / rejected / skipped — counts by reason family

| Reason family | Abilities |
|---|---:|
| Spell / Winds-of-Magic / Cataclysm ability | 434 |
| Vortex / wandering wind (friendly fire) | 99 |
| Army-bar ability | 99 |
| Summon | 74 |
| Bombardment / ground artillery (friendly fire) | 63 |
| Explosive projectile (friendly fire) | 52 |
| Placed / static area damage (friendly fire) | 42 |
| Breath / cone damage (friendly fire) | 30 |
| Explosive / breath attack (friendly fire) | 29 |
| Own-troop-damage AoE (friendly fire by design) | 26 |
| No effect text available (unsourceable) | 26 |
| Ground-target-only | 14 |
| Flanking / ambush (stealth/escape) | 7 |
| Summon / transform | 4 |
| No ammo-low read (ammo replenish) | 3 |
| Magic scope | 1 |
| Enemy-ground placement (no placement path) | 1 |
| Impossible — no enemy-unit read | 76 |
| Impossible — no transform/shapechange support | 11 |
| Impossible — already rejected by user (tactical escape/stealth | 10 |
| Rejected — mutual exclusivity | 5 |
| Rejected — drawback | 5 |
| Rejected — rampage | 3 |
| Rejected — friendly fire | 3 |
| Rejected — stealth / tactical escape | 3 |
| Skipped — army-bar ability | 18 |
| Skipped — unsuitable (vortex) | 17 |
| Skipped — revisit later | 15 |
| Skipped — unsuitable (spawned / ranged) | 13 |
| Skipped — unsuitable (movement) | 5 |
| Skipped — not achievable | 1 |
| Skipped — unsuitable (charge-only) | 1 |
| Skipped — magic scope + self-damage | 1 |
| Skipped — unsuitable (movement / vortex) | 1 |
| **TOTAL non-implemented** | **1192** |

---

## Section 2 — IMPLEMENTED ABILITIES (grouped by trigger family)

Each family below is headed by a plain-English description of the trigger it rides; the **Logic** column gives the short rule per ability. All of these cast automatically in the live mod.

### Melee — in melee and not routing/wobbling (self)  —  `melee_unwavering`  (499 abilities)

Fires when the engine says the unit is in melee AND the unit is neither routing nor wavering (an unreadable morale read fails open and rides the plain in-melee condition). Casts on itself. This is the default family: the base in-melee self trigger.

| Ability | Key | Effects | Logic |
|---|---|---|---|
| Accusation | `wh_main_hero_abilities_accusation` | Armour: -30 (to enemies in range); Melee Defence: -24 (to enemies in range); Missile Resistance: -20 (to enemies in range); Physical Resistance: -20 (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Acquiescence | `wh3_dlc27_spell_bound_acquiescence` | Speed: -25% (to enemies in range); Melee Defence: -24 (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Aether Sword | `wh3_dlc20_weapon_abilities_aether_sword` | Armour-Piercing Weapon Damage: +25%; Base Weapon Damage: +25%; Magical Attacks; Imbuement: Sundered Armour | In melee, not routing/wobbling → cast on self |
| Aken-seth, the Staff of Pain | `wh3_dlc29_weapon_abilities_aken_seth_the_staff_of_pain` | Spell Mastery: +60%; Ability recharge: -15s | In melee, not routing/wobbling → cast on self |
| Alchemist's Elixir of Iron Skin | `wh3_main_item_abilities_alchemists_elixir_of_iron_skin` | Armour: +90 (to self and allies) | In melee, not routing/wobbling → cast on self |
| Alchemist's Elixir of Puissance | `wh3_main_item_abilities_alchemists_elixir_of_puissance` | Melee Attack: +40 (to self and allies) | In melee, not routing/wobbling → cast on self |
| Alchemist's Elixir of Venom | `wh3_main_item_abilities_alchemists_elixir_of_venom` | Imbuement: Slow Death! Damage over time (to self and allies) | In melee, not routing/wobbling → cast on self |
| All Hands Hoay! | `wh2_dlc11_character_abilities_all_hands_hoay` | Armour-Piercing Weapon Damage: +25% (to self and allies); Base Weapon Damage: +25% (to self and allies); Leadership: +16 (to self and allies) | In melee, not routing/wobbling → cast on self |
| Amulet of Itzl | `wh2_main_item_abilities_amulet_of_itzl` | Damage Resistance: +60 | In melee, not routing/wobbling → cast on self |
| Amulet of Pha-Stah | `wh2_dlc09_item_abilities_amulet_of_phastah` | Armour: -30 (to enemies in range); Missile Block Chance: -48 (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Apocalyptic Charge | `wh_pro04_unit_abilities_apocalyptic_charge` | Charge Speed: +10% (to self and allies); Charge Bonus: +20% (to self and allies) | In melee, not routing/wobbling → cast on self |
| Apocalyptic Vision | `wh_dlc03_character_abilities_apocalyptic_vision` | Melee Attack: +24 (to self and allies); Leadership: +16 (to self and allies) | In melee, not routing/wobbling → cast on self |
| Arcane Hymn | `wh3_cp1_character_abilities_magic_prayer` | Power Recharge: +130%; Reserves Per Second: +0.20 | In melee, not routing/wobbling → cast on self |
| Armour of Caledor | `wh2_dlc15_item_abilities_armour_of_caledor` | Vigour per second: -10%; Heals: +1.6% per tick; Ability recharge: -120s | In melee, not routing/wobbling → cast on self |
| Armour of Gazrakh | `wh3_dlc23_item_abilities_armour_of_gazrakh` | Damage Resistance: +30 | In melee, not routing/wobbling → cast on self |
| Armour of the Barrows | `wh3_dlc29_item_abilities_armour_of_the_burrows` | Armour-Piercing Weapon Damage: -25% (to enemies in range); Base Weapon Damage: -25% (to enemies in range); Removes magical attacks (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Assassin's Trophy | `wh2_main_character_abilities_assassins_trophy` | Melee Attack: -24 (to enemies in range); Melee Defence: -24 (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Aura of Inertia | `wh2_dlc13_lord_abilities_aura_of_inertia` | Speed: -25% (to enemies in range); Leadership: -8 (to enemies in range); Vigour per second: +1% (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Aura of Quetzl | `wh2_main_item_abilities_aura_of_quetzl` | Armour: +30 (to self and allies); Melee Defence: +24 (to self and allies) | In melee, not routing/wobbling → cast on self |
| Avast Ye! | `wh2_dlc11_character_abilities_avast_ye` | Armour-Piercing Weapon Damage: +25% (to self and allies); Base Weapon Damage: +25% (to self and allies); Leadership: +8 (to self and allies) | In melee, not routing/wobbling → cast on self |
| Axe of Dargo | `wh_main_weapon_abilities_axe_of_dargo` | Bonus vs. Large: +32; Armour-Piercing Weapon Damage: +50% | In melee, not routing/wobbling → cast on self |
| Axe of Grom | `wh2_dlc15_weapon_abilities_axe_of_grom` | Armour-Piercing Weapon Damage: +50%; Base Weapon Damage: +50%; Imbuement: Sundered Armour | In melee, not routing/wobbling → cast on self |
| Axe of Men | `wh_dlc03_weapon_abilities_axe_of_men` | Can Cause Terror; Unbreakable | In melee, not routing/wobbling → cast on self |
| Axes of Kadrin | `wh3_dlc25_weapon_abilities_axes_of_kadrin` | Bonus vs. Infantry: +16; Armour-Piercing Weapon Damage: +75%; Base Weapon Damage: +75% | In melee, not routing/wobbling → cast on self |
| Azhag's 'Ard Armour | `wh2_dlc15_item_abilities_azhags_ard_armour` | Armour: +30 (to self and allies); Melee Defence: +24 (to self and allies) | In melee, not routing/wobbling → cast on self |
| Ballet of Blows | `wh3_main_lord_abilities_ballet_of_blows` | Melee Attack: +12; Armour-Piercing Weapon Damage: +12%; Base Weapon Damage: +12%; Melee Attack: +24; Armour-Piercing Weapon Damage: +24%; Base Weapon Damage: +24%; Melee Attack: +39; Armour-Piercing Weapon Damage: +36%; Base Weapon Damage: +36% | In melee, not routing/wobbling → cast on self |
| Barbed-Knuckle Boxing | `wh2_dlc17_lord_abilities_barbed_knuckle_boxing` | Melee Attack: +24; Armour-Piercing Weapon Damage: +25%; Base Weapon Damage: +25% | In melee, not routing/wobbling → cast on self |
| Bastet | `wh3_dlc29_lord_abilities_bastet` | Armour: -60 (to enemies in range); Melee Defence: -40 (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Bastion's Defenders | `wh3_dlc24_character_abilities_bastions_defenders` | Melee Defence: +24 (to self and allies); Immune to Flanking (to self and allies) | In melee, not routing/wobbling → cast on self |
| Battle of Wills | `wh3_dlc29_unit_abilities_battle_of_wills` | Melee Attack: -24 (to enemies in range); Leadership: -8 (to enemies in range); Reload Skill: -40 (to enemies in range); Must Resist (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Bear Fang Talisman | `wh3_dlc27_item_abilities_bear_fang_talisman` | Damage Resistance: +40 | In melee, not routing/wobbling → cast on self |
| Beastslaver | `wh2_dlc14_lord_abilities_beastslaver` | Bonus vs. Large: +16; Armour-Piercing Weapon Damage: +25%; Base Weapon Damage: +25% | In melee, not routing/wobbling → cast on self |
| Bitter Sting | `wh3_dlc27_qb_unit_abilities_bitter_sting` | Melee Attack: -24 (to enemies in range); Melee Defence: -24 (to enemies in range); Cannot Run (to enemies in range); Can fly (to enemies in range); Vigour per second: +0.5% (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Black Lotus | `wh2_main_character_abilities_black_lotus` | Imbuement: Discouraged! | In melee, not routing/wobbling → cast on self |
| Black Periapt | `wh_main_item_abilities_black_periapt` | Power Recharge: +160%; Reserves Per Second: +0.20 | In melee, not routing/wobbling → cast on self |
| Black Staff | `wh2_main_spell_bound_black_staff` | Power Recharge: +80% (to self and allies); Reserves Per Second: +0.70 (to self and allies); Damage: 33 every 1s (to self and allies) | In melee, not routing/wobbling → cast on self |
| Blade of Bel-Korhadris | `wh2_main_item_abilities_blade_of_bel_korhadris` | Melee Attack: +24; Armour-Piercing Weapon Damage: +25% | In melee, not routing/wobbling → cast on self |
| Blade of Setep | `wh2_dlc09_weapon_abilities_blade_of_setep` | Armour: -30 (to enemies in range); Physical Resistance: -20 (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Blades of Shang-Yang | `wh3_cp1_weapon_abilities_blades_of_shang_yang` | Melee Attack: +24; Armour-Piercing Weapon Damage: +30%; Base Weapon Damage: +30%; Imbuement: Flammable! | In melee, not routing/wobbling → cast on self |
| Blessed Helm of the Oblast | `wh3_dlc24_item_abilities_blessed_helm_of_the_oblast` | Armour: +60 (to self and allies); Missile Resistance: +20 (to self and allies) | In melee, not routing/wobbling → cast on self |
| Blight of Terrors | `wh2_dlc16_character_abilities_blight_of_terrors` | Leadership: -16 (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Blight Swarm | `wh3_main_lord_abilities_blight_swarm` | Melee Defence: -20 (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Blood Lust | `wh_dlc03_character_abilities_blood_lust` | Armour-Piercing Weapon Damage: +25% (to self and allies) | In melee, not routing/wobbling → cast on self |
| Blood Lust | `wh_main_character_abilities_blood_lust` | Armour-Piercing Weapon Damage: +25% (to self and allies) | In melee, not routing/wobbling → cast on self |
| Blood Omens | `wh3_dlc29_unit_abilities_blood_omens` | Charge Speed: -25% (to enemies in range); Speed: -25% (to enemies in range); Reveals Unit (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Bloodstorm Blades | `wh3_dlc26_weapon_abilities_bloodstorm_blades` | Bonus vs. Infantry: +16; Armour-Piercing Weapon Damage: +75%; Base Weapon Damage: +75% | In melee, not routing/wobbling → cast on self |
| Bloody Onslaught | `wh3_dlc26_character_abilities_bloody_onslaught` | Armour: -30 (to enemies in range); Melee Defence: -24 (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Blooood! | `wh_main_unit_abilities_blooood` | Acceleration: +18%; Speed: +25%; Vigour per second: -2% | In melee, not routing/wobbling → cast on self |
| Book of Arkhan | `wh_main_spell_bound_book_of_arkhan` | Speed: +25% (to self and allies); Melee Attack: +24 (to self and allies) | In melee, not routing/wobbling → cast on self |
| Book of Hoeth | `wh2_main_item_abilities_book_of_hoeth` | Power Recharge: +160% | In melee, not routing/wobbling → cast on self |
| Book of Secrets | `wh3_dlc24_item_abilities_book_of_secrets` | Damage: 10 every 1s (to enemies in range); Speed: -25% (to enemies in range); Weakness to Fire Damage: -20 (to enemies in range); Melee Attack: -24 (to enemies in range); Melee Defence: -24 (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Boom! | `wh_main_unit_abilities_boom` | Armour-Piercing Explosive Damage: +20%; Base Explosive Damage: +25% | In melee, not routing/wobbling → cast on self |
| Brass Body | `wh2_dlc17_lord_abilities_brass_body` | Melee Defence: +24; Damage Resistance: +40 | In melee, not routing/wobbling → cast on self |
| Breath of Hatred | `wh3_dlc23_bound_abilities_breath_of_hatred` | Melee Attack: +24 (to self and allies); Flaming Attacks (to self and allies); Imbuement: Sundered Armour (to self and allies) | In melee, not routing/wobbling → cast on self |
| Breath of Hatred | `wh3_dlc23_character_abilities_breath_of_hatred` | Melee Attack: +24 (to self and allies); Flaming Attacks (to self and allies); Imbuement: Sundered Armour (to self and allies) | In melee, not routing/wobbling → cast on self |
| Call of Violence | `wh_dlc03_character_abilities_call_of_violence` | Leadership: +16 (to self and allies) | In melee, not routing/wobbling → cast on self |
| Cascading Fire Cloak | `wh3_main_spell_bound_cascading_fire_cloak` | Armour-Piercing Weapon Damage: +25% (to self and allies); Melee Defence: +24 (to self and allies) | In melee, not routing/wobbling → cast on self |
| Chalice of Dark Rain | `wh_dlc03_item_abilities_chalice_of_dark_rain` | Accuracy: -30 (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Change or Die! | `wh3_dlc24_character_abilities_change_or_die` | Leadership: +16 (to self and allies); Damage Resistance: +20 (to self and allies) | In melee, not routing/wobbling → cast on self |
| Channelling Staff | `wh_main_item_abilities_channelling_staff` | Ability recharge: -15s | In melee, not routing/wobbling → cast on self |
| Chanson of Caging | `wh3_dlc27_lord_abilities_chanson_of_caging` | Speed: -15% (to enemies in range); Vigour per second: +1.3% (to enemies in range); Charge Speed: +15% (to self and allies); Speed: +15% (to self and allies); Missile Resistance: +10 (to self and allies) | In melee, not routing/wobbling → cast on self |
| Charmed Shield | `wh_main_weapon_abilities_charmed_shield` | Missile Block Chance: +25; Damage Resistance: +20 | In melee, not routing/wobbling → cast on self |
| Claws of Mourkain | `wh2_dlc11_lord_abilities_claws_of_mourkain` | Armour-Piercing Weapon Damage: +50% | In melee, not routing/wobbling → cast on self |
| Cloak of Mists & Shadows | `wh_main_item_abilities_cloak_of_mists_and_shadows` | Physical Resistance: +75; Strider; Magical Attacks | In melee, not routing/wobbling → cast on self |
| Coat in Blood | `wh3_dlc29_hero_abilities_coat_in_blood` | Melee Attack: +24; Armour-Piercing Weapon Damage: +50%; Base Weapon Damage: +50%; Flaming Attacks | In melee, not routing/wobbling → cast on self |
| Cold-Blooded | `wh2_main_character_abilities_cold_blooded` | Leadership: +16 (to self and allies); Stops Rampage! (to self and allies) | In melee, not routing/wobbling → cast on self |
| Creature-Killer | `wh2_dlc16_weapon_abilities_creature_killer` | Bonus vs. Large: +16 (to self and allies) | In melee, not routing/wobbling → cast on self |
| Crown of Command | `wh_main_item_abilities_crown_of_command` | Unbreakable (to self and allies) | In melee, not routing/wobbling → cast on self |
| Cube of Darkness | `wh2_main_item_abilities_cube_of_darkness` | Power Recharge: -40% (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Curse of Khsar | `wh2_dlc09_character_abilities_curse_of_khsar` | Armour: -60 (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Curse of Years | `wh3_dlc29_spell_bound_curse_of_years` | Imbuement: wh3_dlc29_unit_contact_curse_of_years | In melee, not routing/wobbling → cast on self |
| Da Boss 'as a Plan! | `wh3_dlc26_character_abilities_da_boss_as_a_plan` | Melee Defence: +24 (to allies in range); Leadership: +8 (to allies in range); Expert Charge Defence (to allies in range) | In melee, not routing/wobbling → cast on self |
| Da Great 'Un Iz 'Ere! | `wh2_dlc15_lord_abilities_da_great_un_iz_ere` | Melee Attack: +24 (to self and allies); Base Weapon Damage: +30% (to self and allies); Leadership: +8 (to self and allies) | In melee, not routing/wobbling → cast on self |
| Daemonblade | `wh3_dlc20_weapon_abilities_daemonblade` | Armour-Piercing Weapon Damage: +25%; Base Weapon Damage: +25%; Imbuement: Discouraged! | In melee, not routing/wobbling → cast on self |
| Daemonic Strength | `wh_main_item_abilities_daemonic_strength` | Armour-Piercing Weapon Damage: +50%; Base Weapon Damage: +50% | In melee, not routing/wobbling → cast on self |
| Daemonic Whispers | `wh3_dlc27_character_abilities_slezuzus_voice` | Leadership: +16 (to allies in range); Can Cause Fear (to allies in range); Can Cause Terror (to allies in range) | In melee, not routing/wobbling → cast on self |
| Daemonshield | `wh3_dlc20_item_abilities_daemonshield` | Invulnerable | In melee, not routing/wobbling → cast on self |
| Dagger of Malice | `wh3_dlc23_weapon_abilities_dagger_of_malice` | Melee Attack: +40; Base Weapon Damage: +100%; Imbuement: Poison! | In melee, not routing/wobbling → cast on self |
| Dark Fortune | `wh_main_item_abilities_dark_fortune` | Damage Resistance: +20 | In melee, not routing/wobbling → cast on self |
| Dark Protection | `wh2_dlc11_lord_abilities_dark_protection` | Melee Defence: +24; Damage Resistance: +20 | In melee, not routing/wobbling → cast on self |
| Dark Venom | `wh2_main_character_abilities_dark_venom` | Base Weapon Damage: +90% | In melee, not routing/wobbling → cast on self |
| Darkwalker | `wh3_dlc25_lord_abilities_darkwalker` | Physical Resistance: +40; Strider | In melee, not routing/wobbling → cast on self |
| Death Frenzy | `wh2_dlc16_spell_bound_death_frenzy` | Melee Attack: +24 (to self and allies); Armour-Piercing Weapon Damage: +30% (to self and allies); Base Weapon Damage: +30% (to self and allies); Immune to Psychology (to self and allies) | In melee, not routing/wobbling → cast on self |
| Deathbringer | `wh3_main_lord_abilities_deathbringer` | Armour-Piercing Weapon Damage: +50%; Base Weapon Damage: +50% | In melee, not routing/wobbling → cast on self |
| Deathbringer Upgraded | `wh3_main_lord_abilities_deathbringer_upgraded` | Armour-Piercing Weapon Damage: +100%; Base Weapon Damage: +100% | In melee, not routing/wobbling → cast on self |
| Deranged Munitions | `wh3_dlc25_lord_abilities_deranged_munitions` | Armour-Piercing Missile Damage: +50% (to self and allies); Base Missile Damage: +50% (to self and allies); Magical Attacks (to self and allies) | In melee, not routing/wobbling → cast on self |
| Deranged Munitions Upgraded | `wh3_dlc25_lord_abilities_deranged_munitions_upgraded` | Armour-Piercing Missile Damage: +50% (to self and allies); Base Missile Damage: +50% (to self and allies); Magical Attacks (to self and allies) | In melee, not routing/wobbling → cast on self |
| Desertstrike | `wh2_dlc09_character_abilities_strike_of_nehekhara` | Melee Attack: +40; Base Weapon Damage: +60%; Can Cause Terror | In melee, not routing/wobbling → cast on self |
| Dolorous Blade | `wh_dlc07_hero_abilities_dolorous_blade` | Melee Attack: +24; Armour-Piercing Weapon Damage: +50% | In melee, not routing/wobbling → cast on self |
| Don't Even Try It | `wh2_dlc15_lord_abilities_dont_even_try_it` | Damage: 144 every 2s (to enemies in range); Ability recharge: +15s (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Doom & Darkness | `wh3_dlc25_spell_Bound_doom_and_darkness_gunnery_school` | Leadership: -16 (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Doom & Darkness | `wh3_dlc27_spell_bound_runecaller_death_doom_and_darkness` | Leadership: -16 (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Doom & Darkness | `wh_dlc08_spell_bound_death_doom_and_darkness` | Leadership: -16 (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Doom Glaive | `wh3_dlc29_item_abilities_doom_glaive` | Armour-Piercing Weapon Damage: +75%; Base Weapon Damage: +75%; Executioner | In melee, not routing/wobbling → cast on self |
| Doom Lord | `wh3_dlc29_lord_abilities_doom_lord` | Cannot Die (to self and allies); Stops Rampage! (to self and allies); Unbreakable (to self and allies) | In melee, not routing/wobbling → cast on self |
| Dragon Spear | `wh2_dlc16_weapon_abilities_dragon_spear` | Armour-Piercing Weapon Damage: +100 (to self and allies) | In melee, not routing/wobbling → cast on self |
| Dragonhorn | `wh2_dlc15_lord_abilities_dragonhorn` | Melee Attack: +24 (to self and allies); Can Cause Fear (to self and allies) | In melee, not routing/wobbling → cast on self |
| Dreaded Duellist | `wh2_dlc11_lord_abilities_dreaded_duelist` | Melee Attack: +24; Melee Defence: +24 | In melee, not routing/wobbling → cast on self |
| Dwarf Gouger | `wh2_main_weapon_abilities_dwarf_gouger` | Melee Attack: +24; Armour-Piercing Weapon Damage: +50%; Base Weapon Damage: +50% | In melee, not routing/wobbling → cast on self |
| Earthing Rod | `wh_main_item_abilities_earthing_rod` | Miscast Chance: -100% | In melee, not routing/wobbling → cast on self |
| El Syf | `wh_dlc05_weapon_abilities_el_syf` | Speed: -45% (to enemies in range); Melee Defence: -40 (to enemies in range); Physical Resistance: -20 (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Elixir of Damnation | `wh3_dlc27_item_abilities_elixir_of_damnation` | Imbuement: {{tr:ancillaries_onscreen_name_wh3_dlc27_anc_enchanted_item_elixir_of_damnation}} | In melee, not routing/wobbling → cast on self |
| Elixir of Might | `wh2_dlc09_item_abilities_elixir_of_might` | Melee Attack: +24 (to self and allies); Base Weapon Damage: +60% (to self and allies) | In melee, not routing/wobbling → cast on self |
| Embers of the Phoenix | `wh2_main_spell_bound_embers_of_the_phoenix` | Base Missile Damage: +25% (to self and allies); Base Weapon Damage: +30% (to self and allies); Magical Attacks (to self and allies); Flaming Attacks (to self and allies) | In melee, not routing/wobbling → cast on self |
| Empowering Shrooms | `wh3_dlc26_character_abilities_empowering_shrooms` | Melee Attack: +24 (to allies in range); Leadership: +16 (to allies in range); Stops Rampage! (to allies in range) | In melee, not routing/wobbling → cast on self |
| Enchanted Ballistics | `wh2_dlc11_character_abilities_ballistic_enchantment` | Accuracy: +60 (to self and allies); Reload Skill: +20 (to self and allies) | In melee, not routing/wobbling → cast on self |
| Enhanced Skavenbrew | `wh3_dlc29_item_abilities_enhanced_skavenbrew` | Armour: -40 (to self and allies); Mass: +25% (to self and allies); Melee Attack: +50 (to self and allies); Base Weapon Damage: +50% (to self and allies); Can Cause Terror (to self and allies) | In melee, not routing/wobbling → cast on self |
| Enrage | `wh_pro04_unit_abilities_enrage` | Damage Resistance: +40 | In melee, not routing/wobbling → cast on self |
| Entangle | `wh2_dlc10_character_abilities_entangle` | Weakness to Fire Damage: -20 (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Entice | `wh3_dlc29_unit_abilities_entice` | Melee Defence: +24; Imbuement: Euphoric! | In melee, not routing/wobbling → cast on self |
| Entrenchment | `wh_main_unit_abilities_entrenchment` | Armour-Piercing Missile Damage: +40% (to self and allies); Physical Resistance: +20 (to self and allies) | In melee, not routing/wobbling → cast on self |
| Eternal Gaze | `wh3_dlc29_lord_abilities_gaze_of_usirian` | Vigour per second: +2% (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Eternal Vigour | `wh3_dlc29_character_abilities_eternal_vigour` | Melee Defence: +24 (to allies in range); Physical Resistance: +20 (to allies in range) | In melee, not routing/wobbling → cast on self |
| Everyone Has Their Price | `wh3_main_lord_abilities_everyone_has_their_price` | Melee Attack: -24 (to enemies in range); Leadership: -8 (to enemies in range); Rampage! (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Evisceration | `wh2_dlc16_hero_abilities_evisceration` | Huge, stationary area of effect; Good against armour; Strong vs multiple units | In melee, not routing/wobbling → cast on self |
| Extra Ingredients | `wh3_main_character_abilities_extra_ingredients` | Power Recharge: +160%; Reserves Per Second: +0.20 | In melee, not routing/wobbling → cast on self |
| Eye for an Eye | `wh3_dlc29_spell_bound_eye_jabber` | Armour-Piercing Weapon Damage: +25%; Base Weapon Damage: +25%; Imbuement: Blinded! | In melee, not routing/wobbling → cast on self |
| Eye Gouger | `wh3_dlc29_spell_bound_eye_gouger` | Melee Attack: +24; Armour-Piercing Weapon Damage: +50%; Base Weapon Damage: +50%; Imbuement: Blinded! | In melee, not routing/wobbling → cast on self |
| Eye of the Storm | `wh3_main_lord_abilities_eye_of_the_storm` | Melee Attack: +24; Armour-Piercing Weapon Damage: +50%; Base Weapon Damage: +50% | In melee, not routing/wobbling → cast on self |
| Faith's Bastion | `wh_main_hero_abilities_faiths_bastion` | Damage Resistance: +20 | In melee, not routing/wobbling → cast on self |
| Fangsword of Eltharion | `wh2_dlc15_weapon_abilities_fangsword_of_eltharion` | Armour-Piercing Weapon Damage: +25%; Base Weapon Damage: +25%; Physical Resistance: +40; Magical Attacks | In melee, not routing/wobbling → cast on self |
| Favour of the Fay | `wh_dlc07_lord_abilities_favour_of_the_fay` | Melee Attack: +40 (to self and allies) | In melee, not routing/wobbling → cast on self |
| Favoured by the Matriarch | `wh3_dlc27_hero_abilities_favoured_by_the_matriarch` | Melee Attack: +24 (to self and allies); Leadership: +8 (to self and allies) | In melee, not routing/wobbling → cast on self |
| Fear of Aramar | `wh2_dlc10_item_abilities_fear_of_aramar` | Leadership: -24 (to enemies in range); Vigour per second: +1% (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Fearsome Roar | `wh3_dlc24_unit_abilities_fearsome_roar` | Leadership: -8 (to enemies in range); Removes Immune to Psychology (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Fecund Rebirth | `wh3_dlc29_character_active_mark_of_the_monster` | Charge Speed: -50% (to enemies in range); Speed: -50% (to enemies in range); Incoming Healing Modifier: -100% (to enemies in range); Damage: 38 every 1s (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Feint & Riposte | `wh2_main_lord_abilities_feint_and_reposte` | Melee Attack: +24; Melee Defence: +24; Physical Resistance: +20 | In melee, not routing/wobbling → cast on self |
| Fermented Fungi | `wh2_dlc15_lord_abilities_fermented_fungi` | Melee Defence: -24 (to enemies in range); Rampage! (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Ferocious Winter’s Chill | `wh3_dlc29_spell_bound_prayer_ferocious_winters_chill` | Melee Attack: -24 (to enemies in range); Armour-Piercing Weapon Damage: -30% (to enemies in range); Base Weapon Damage: -30% (to enemies in range); Melee Defence: -24 (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Fight or Die! | `wh_dlc08_lord_abilities_fight_or_die` | Melee Attack: +24 (to self and allies); Leadership: +16 (to self and allies) | In melee, not routing/wobbling → cast on self |
| Filth Mace | `wh_main_weapon_abilities_filth_mace` | Armour-Piercing Weapon Damage: +25%; Base Weapon Damage: +25%; Can Cause Terror; Imbuement: Corroded Armour | In melee, not routing/wobbling → cast on self |
| Fistful of Laurels | `wh3_main_item_abilities_fistful_of_laurels` | Melee Attack: +40 (to self and allies); Leadership: +16 (to self and allies) | In melee, not routing/wobbling → cast on self |
| Flame Incarnate | `wh3_main_character_abilities_flame_incarnate` | Melee Damage Reflection: +14 | In melee, not routing/wobbling → cast on self |
| Flesh to Stone | `wh2_dlc16_spell_bound_flesh_to_stone` | Physical Resistance: +60 (to self and allies) | In melee, not routing/wobbling → cast on self |
| Fluid Injection! | `wh2_dlc16_unit_abilities_fluid_injection` | Melee Attack: +24; Armour-Piercing Weapon Damage: +25%; Base Weapon Damage: +25%; Rampage! | In melee, not routing/wobbling → cast on self |
| Focus Instincts | `wh2_dlc12_lord_abilities_focus_instincts` | Stops Rampage! (to self and allies) | In melee, not routing/wobbling → cast on self |
| Forbidden Rod | `wh_main_item_abilities_forbidden_rod` | Power Recharge: +160%; Reserves Per Second: +0.20; Damage: 33 every 1s | In melee, not routing/wobbling → cast on self |
| Frenzied Challenge | `wh3_dlc27_qb_unit_abilities_frenzied_challenge` | Speed: +25% (to enemies in range); Melee Defence: -24 (to enemies in range); Rampage! (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Frost Shard Glaive | `wh3_main_weapon_abilities_frost_shard_glaive` | Speed: -45% (to enemies in range); Melee Defence: -40 (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Funnel of Flame | `wh2_dlc13_lord_abilities_funnel_of_flame` | Reload Skill: +30 (to self and allies); Flaming Attacks (to self and allies) | In melee, not routing/wobbling → cast on self |
| Fury of the Blood God | `wh3_dlc26_lord_abilities_gaze_of_khorne` | Causes moderate magical damage; Causes severe disruption to enemy formations; Strong vs multiple combatants | In melee, not routing/wobbling → cast on self |
| Fury of the Land | `wh3_dlc24_character_abilities_fury_of_the_land` | Can Cause Fear (to allies in range); Strider (to allies in range); Magical Attacks (to allies in range) | In melee, not routing/wobbling → cast on self |
| Fury of Ursun | `wh3_main_lord_abilities_fury_of_ursun` | Armour-Piercing Weapon Damage: +25%; Base Weapon Damage: +25%; Can Cause Terror; Rampage! | In melee, not routing/wobbling → cast on self |
| Gaze of Fate | `wh3_main_lord_abilities_gaze_of_fate` | Melee Attack: -40 (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Gaze of Khaine | `wh2_dlc10_lord_abilities_gaze_of_khaine` | Melee Attack: +24 (to self and allies); Armour-Piercing Weapon Damage: +25% (to self and allies); Base Weapon Damage: +25% (to self and allies); Leadership: +8 (to self and allies); Rampage! (to self and allies) | In melee, not routing/wobbling → cast on self |
| Get 'Em! | `wh3_dlc25_character_abilities_get_em` | enemy speed debuff (hex, under fire) | In melee, not routing/wobbling → cast on self |
| Get Back 'Ere! | `wh_main_character_abilities_get_back_ere` | Leadership: +16 (to self and allies) | In melee, not routing/wobbling → cast on self |
| Ghal Maraz | `wh_main_weapon_abilities_ghal_maraz` | Bonus vs. Large: +16; Armour-Piercing Weapon Damage: +50% | In melee, not routing/wobbling → cast on self |
| Giant Leap | `wh3_dlc24_character_abilities_giant_leap` | Causes moderate magical damage; Causes severe disruption to enemy formations; Strong vs multiple combatants | In melee, not routing/wobbling → cast on self |
| Gilellion's Soulnetter | `wh3_main_weapon_abilities_soulnetter` | enemy melee debuff (hex) | In melee, not routing/wobbling → cast on self |
| Gitsnik | `wh_main_weapon_abilities_gitsnik` | Melee Attack: +24; Armour-Piercing Weapon Damage: +50%; Base Weapon Damage: +50% | In melee, not routing/wobbling → cast on self |
| Glacial Defence | `wh3_twa08_unit_abilities_glacial_defence` | Speed: -25%; Armour: +60; Missile Resistance: +20 | In melee, not routing/wobbling → cast on self |
| Glory Seeker | `wh3_dlc29_hero_active_glory_seeker` | Incoming Healing Modifier: -100% (to enemies in range); Melee Defence: -24 (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Glory Seeker Upgraded | `wh3_dlc29_hero_active_glory_seeker_upgraded` | Incoming Healing Modifier: -100% (to enemies in range); Melee Defence: -36 (to enemies in range); Removes Expert Charge Defence (to enemies in range); Removes Charge Defence vs Large (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Gotrek's Doom | `wh2_pro08_character_abilities_gotrek_doom` | Melee Defence: +40; Damage Resistance: +40 | In melee, not routing/wobbling → cast on self |
| Grand Shield of Faith | `wh_dlc04_spell_bound_shield_of_faith_upgraded` | Damage Resistance: +20 (to self and allies) | In melee, not routing/wobbling → cast on self |
| Great Gutgouger | `wh3_dlc26_weapon_abilities_great_gutgouger` | Melee Attack: +24; Armour-Piercing Weapon Damage: +50%; Base Weapon Damage: +50%; Can Cause Terror; Imbuement: Monstrous Impact | In melee, not routing/wobbling → cast on self |
| Greater Faith Bastion | `wh_dlc06_quest_abilities_grand_faiths_bastion` | Damage Resistance: +90 (to self and allies) | In melee, not routing/wobbling → cast on self |
| Grut's Sickle | `wh3_main_item_abilities_gruts_sickle` | Power Recharge: +80% (to allies in range); Reserves Per Second: +0.40 (to allies in range); Damage: 33 every 1s (to allies in range) | In melee, not routing/wobbling → cast on self |
| Guttural Roar | `wh3_dlc27_qb_unit_abilities_guttural_roar` | Base Weapon Damage: -15% (to enemies in range); Melee Defence: -16 (to enemies in range); Leadership: -24 (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Hagtree Fetish | `wh_dlc03_item_abilities_hagtree_fetish` | Miscast Chance: -75% | In melee, not routing/wobbling → cast on self |
| Hail of Fire | `wh2_dlc13_lord_abilities_hail_of_fire` | Reload Skill: +30 (to self and allies); Flaming Attacks (to self and allies) | In melee, not routing/wobbling → cast on self |
| Halo of Maidenly Wrath | `wh2_dlc14_lord_abilities_halo_of_maidenly_wrath` | Explosion does not affect friendly troops; Poor against large combatants | In melee, not routing/wobbling → cast on self |
| Hammer-axe of Skoll | `wh3_dlc29_weapon_active_hammer_axe_of_skoll` | Melee Attack: +24; Armour-Piercing Weapon Damage: +75%; Base Weapon Damage: +75% | In melee, not routing/wobbling → cast on self |
| Harmonic Convergence | `wh3_main_spell_bound_harmonic_convergence` | Melee Attack: +24 (to self and allies); Melee Defence: +24 (to self and allies); Reload Skill: +20 (to self and allies) | In melee, not routing/wobbling → cast on self |
| Headhunt | `wh3_dlc26_character_abilities_headhunt` | Melee Defence: -40 (to enemies in range); Missile Resistance: -20 (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Hellfire Sword | `wh_main_weapon_abilities_hellfire_sword` | Armour-Piercing Weapon Damage: +50%; Base Weapon Damage: +50%; Flaming Attacks | In melee, not routing/wobbling → cast on self |
| Hellish Vigour | `wh3_dlc29_lord_abilities_hellish_vigour` | Melee Damage Reflection: +20 (to allies in range); Vigour per second: -2% (to allies in range) | In melee, not routing/wobbling → cast on self |
| Hellish Vigour Upgraded | `wh3_dlc29_lord_abilities_hellish_vigour_upgraded` | Melee Damage Reflection: +20 (to allies in range); Vigour per second: -2% (to allies in range) | In melee, not routing/wobbling → cast on self |
| Helm of Discord | `wh_main_weapon_abilities_helm_of_discord` | Melee Attack: -24 (to enemies in range); Melee Defence: -24 (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Helm of Many Eyes | `wh_dlc01_item_passive_helm_of_many_eyes` | Melee Defence: +54 | In melee, not routing/wobbling → cast on self |
| Helping Hand | `wh2_pro08_character_abilities_helping_hand` | Melee Attack: +40 (to allies in range); Damage Resistance: +40 (to allies in range) | In melee, not routing/wobbling → cast on self |
| Heroic Killing Blow | `wh3_main_pro_character_abilities_heroic_killing_blow_2` | Armour-Piercing Weapon Damage: +100%; Base Weapon Damage: +100% | In melee, not routing/wobbling → cast on self |
| Heroic Killing Blow | `wh_dlc07_character_abilities_heroic_killing_blow` | Armour-Piercing Weapon Damage: +50%; Base Weapon Damage: +50% | In melee, not routing/wobbling → cast on self |
| Heroic Killing Blow | `wh_main_character_abilities_heroic_killing_blow` | Armour-Piercing Weapon Damage: +50%; Base Weapon Damage: +50% | In melee, not routing/wobbling → cast on self |
| Hidden Huntress | `wh3_cp1_lord_abilities_hidden_huntress` | Speed: -25% (to enemies in range); Melee Defence: -24 (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Hidden Huntress Upgraded | `wh3_cp1_lord_abilities_hidden_huntress_upgraded` | Speed: -25% (to enemies in range); Armour: -30 (to enemies in range); Melee Defence: -40 (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Horn of the Wild Hunt | `wh_dlc05_item_abilities_horn_of_the_wild_hunt` | Charge Bonus: +60% (to self and allies) | In melee, not routing/wobbling → cast on self |
| Horn of Vaul | `wh2_main_item_abilities_dragonhorn` | Base Missile Damage: +25% (to self and allies); Base Weapon Damage: +30% (to self and allies) | In melee, not routing/wobbling → cast on self |
| Hornswaggle | `wh2_dlc11_character_abilities_hornswaggle` | Speed: -25% (to enemies in range); Armour: -30 (to enemies in range); Melee Defence: -24 (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Howl of the Great Beast | `wh3_dlc24_unit_abilities_howl_of_the_great_beast` | Speed: -25% (to enemies in range); Leadership: -8 (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Hunter of Champions | `wh_dlc08_character_abilities_hunter_of_champions` | Speed: -45% (to enemies in range); Armour: -60 (to enemies in range); Melee Defence: -40 (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Hunter's Snare | `wh2_dlc13_lord_abilities_hunters_snare` | enemy speed debuff (hex, area) | In melee, not routing/wobbling → cast on self |
| Hunter's Trap | `wh2_dlc13_lord_abilities_hunters_trap` | enemy speed debuff (hex, area) | In melee, not routing/wobbling → cast on self |
| Hydra Blade | `wh2_main_weapon_abilities_hydra_blade` | Armour-Piercing Weapon Damage: +50%; Base Weapon Damage: +50% | In melee, not routing/wobbling → cast on self |
| Hysterical Frenzy | `wh3_main_spell_slaanesh_hysterical_frenzy_bound` | Melee Attack: +40 (to self and allies); Armour-Piercing Weapon Damage: +25% (to self and allies); Base Weapon Damage: +25% (to self and allies) | In melee, not routing/wobbling → cast on self |
| Immovable Bulwark | `wh3_dlc26_unit_abilities_immovable_bulwark` | Melee Attack: -24; Melee Defence: +24 | In melee, not routing/wobbling → cast on self |
| Inevitable Horror | `wh3_dlc26_character_abilities_inevitable_horror` | Leadership: -8 (to enemies in range); Vigour per second: +1% (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Inspired Defence I | `wh3_main_lord_abilities_inspired_defence_i` | Melee Defence: +24 (to allies in range); Leadership: +16 (to allies in range) | In melee, not routing/wobbling → cast on self |
| Inspired Defence II | `wh3_main_lord_abilities_inspired_defence_ii` | Melee Defence: +24 (to allies in range); Leadership: +16 (to allies in range); Expert Charge Defence (to allies in range) | In melee, not routing/wobbling → cast on self |
| Inspired Defence III | `wh3_main_lord_abilities_inspired_defence_iii` | Melee Defence: +40 (to allies in range); Leadership: +16 (to allies in range); Expert Charge Defence (to allies in range) | In melee, not routing/wobbling → cast on self |
| Inspired Marksmanship I | `wh3_main_lord_abilities_inspired_marksmanship_i` | Accuracy: +30 (to allies in range); Reload Skill: +20 (to allies in range) | In melee, not routing/wobbling → cast on self |
| Inspired Marksmanship II | `wh3_main_lord_abilities_inspired_marksmanship_ii` | Accuracy: +60 (to allies in range); Reload Skill: +20 (to allies in range) | In melee, not routing/wobbling → cast on self |
| Inspired Marksmanship III | `wh3_main_lord_abilities_inspired_marksmanship_iii` | Accuracy: +60 (to allies in range); Reload Skill: +40 (to allies in range) | In melee, not routing/wobbling → cast on self |
| Iron-Handed Captain | `wh3_dlc27_character_abilities_iron_hand_captain` | Leadership: +100 (to allies in range); Rally (to allies in range) | In melee, not routing/wobbling → cast on self |
| Jagged Dagger | `wh_dlc03_item_abilities_jagged_dagger` | Power Recharge: +160% | In melee, not routing/wobbling → cast on self |
| Karaghul | `wh2_pro08_weapon_abilities_karaghul` | Bonus vs. Infantry: +32; Melee Attack: +40; Flaming Attacks | In melee, not routing/wobbling → cast on self |
| Killing Blow | `wh3_main_pro_character_abilities_heroic_killing_blow_1` | Armour-Piercing Weapon Damage: +50%; Base Weapon Damage: +50% | In melee, not routing/wobbling → cast on self |
| Killing Blow | `wh_main_unit_abilities_killing_blow` | Armour-Piercing Weapon Damage: +25%; Base Weapon Damage: +25% | In melee, not routing/wobbling → cast on self |
| Legbiter | `wh3_dlc29_weapon_abilities_legbiter` | Melee Attack: +24; Armour-Piercing Weapon Damage: +25%; Base Weapon Damage: +25%; Imbuement: Legbiter | In melee, not routing/wobbling → cast on self |
| Liarsbane | `wh3_dlc25_weapon_abilities_liarsbane` | Melee Attack: +40; Melee Defence: +24 | In melee, not routing/wobbling → cast on self |
| Lightning Reflexes | `wh2_dlc11_lord_abilities_lightning_reflexes` | Speed: +25%; Damage Resistance: +20 | In melee, not routing/wobbling → cast on self |
| Locus of Abjuration | `wh3_main_character_abilities_locus_of_abjuration` | Spell Resistance: +65 (to self and allies) | In melee, not routing/wobbling → cast on self |
| Locus of Beguilement | `wh3_main_character_abilities_locus_of_beguilement` | Melee Defence: -24 (to enemies in range); Leadership: -8 (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Locus of Change | `wh3_main_character_abilities_locus_of_change` | Armour-Piercing Missile Damage: +25% (to self and allies); Base Missile Damage: +25% (to self and allies) | In melee, not routing/wobbling → cast on self |
| Locus of Conjuration | `wh3_main_character_abilities_locus_of_conjuration` | Power Recharge: +160% (to self and allies) | In melee, not routing/wobbling → cast on self |
| Locus of Grace | `wh3_main_character_abilities_locus_of_grace` | Melee Defence: +24 (to self and allies); Physical Resistance: +22 (to self and allies) | In melee, not routing/wobbling → cast on self |
| Locus of Virulence | `wh3_main_character_abilities_locus_of_virulence` | Melee Attack: +24 (to self and allies); Armour-Piercing Weapon Damage: +25% (to self and allies); Base Weapon Damage: +25% (to self and allies) | In melee, not routing/wobbling → cast on self |
| Locus of Wrath | `wh3_main_character_abilities_locus_of_wrath` | Melee Attack: +40 (to self and allies) | In melee, not routing/wobbling → cast on self |
| Looming Dread | `wh2_dlc14_lord_abilities_looming_dread` | Speed: -45% (to enemies in range); Melee Defence: -24 (to enemies in range); Missile Resistance: -20 (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Lord of Dragons | `wh2_dlc15_lord_abilities_lord_of_dragons` | Melee Attack: -40 (to enemies in range); Melee Defence: -24 (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Lord of Grand Cathay | `wh3_dlc24_lord_abilities_lord_of_grand_cathay` | Melee Defence: +40 (to self and allies); Physical Resistance: +20 (to self and allies) | In melee, not routing/wobbling → cast on self |
| Lucky Banner | `wh2_dlc15_item_abilities_lucky_banner` | Melee Attack: +24; Damage Resistance: +40 | In melee, not routing/wobbling → cast on self |
| Mace of Ulumak | `wh2_dlc13_weapon_abilities_mace_of_ulumak` | Melee Attack: +40; Armour-Piercing Weapon Damage: +50%; Base Weapon Damage: +50%; Imbuement: Dazed! | In melee, not routing/wobbling → cast on self |
| Magical Animus | `wh_main_character_abilities_magical_animus` | Leadership: +16 (to self and allies) | In melee, not routing/wobbling → cast on self |
| Manann's Luck | `wh2_dlc11_lord_abilities_mananns_luck` | Melee Defence: +24; Damage Resistance: +20 | In melee, not routing/wobbling → cast on self |
| Mantra of Righteousness | `wh3_cp1_character_abilities_offense_prayer` | Melee Attack: +24 (to self and allies); Armour-Piercing Weapon Damage: +25% (to self and allies); Base Weapon Damage: +25% (to self and allies); Imbuement: Sundered Armour (to self and allies) | In melee, not routing/wobbling → cast on self |
| Mark of the Plague Fleet | `wh3_dlc29_item_active_mark_of_the_plague_fleet` | Incoming Healing Modifier: -50% (to enemies in range); Damage Resistance: -20 (to enemies in range); Spell Resistance: -20 (to enemies in range); Physical Resistance: -20 (to enemies in range); Vigour per second: +2% (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Mark of Yin | `wh3_dlc24_unit_abilities_mark_of_yin` | Armour: -30 (to enemies in range); Missile Block Chance: -25 (to enemies in range); Missile Resistance: -20 (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Marked by Ulthar | `wh_dlc06_unit_abilities_marked_by_ulthar` | Armour: -30 (to enemies in range); Missile Block Chance: -25 (to enemies in range); Missile Resistance: -20 (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Marked for Eatin' | `wh3_dlc26_unit_abilities_marked_for_eatin` | Speed: -25% (to enemies in range); Armour: -30 (to enemies in range); Melee Defence: -40 (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Massacre | `wh3_main_prisoners_massacre` | Melee Attack: +24 (to allies in range); Armour-Piercing Weapon Damage: +25% (to allies in range); Base Weapon Damage: +25% (to allies in range) | In melee, not routing/wobbling → cast on self |
| Master of Beguilement | `wh_dlc04_lord_abilities_beguile` | Melee Attack: -40 (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Master of the Black Arts | `wh_main_lord_abilities_master_of_the_black_arts` | Spell Mastery: +60% | In melee, not routing/wobbling → cast on self |
| Master of the Skies | `wh2_dlc12_lord_abilities_master_of_the_skies` | Speed: +25%; Melee Defence: +40 | In melee, not routing/wobbling → cast on self |
| Master Predator | `wh2_dlc17_lord_abilities_master_predator` | Charge Speed: -25%; Range: +20%; Speed: -25%; Snipe; Unspottable | In melee, not routing/wobbling → cast on self |
| Master Rune of Breaking | `wh2_dlc17_rune_abilities_master_rune_of_breaking` | Armour-Piercing Weapon Damage: +25% (to self and allies); Base Weapon Damage: +25% (to self and allies); Imbuement: Sundered Armour (to self and allies) | In melee, not routing/wobbling → cast on self |
| Master Rune of Negation | `wh_dlc06_rune_abilities_master_rune_of_negation` | Damage Resistance: +40 (to self and allies) | In melee, not routing/wobbling → cast on self |
| Master Rune of Oath & Steel | `wh_dlc06_rune_abilities_master_rune_of_oath_and_steel` | Armour: +60 (to self and allies) | In melee, not routing/wobbling → cast on self |
| Master Rune of Slowness | `wh2_dlc17_rune_abilities_master_rune_of_slowness` | Charge Speed: -60% (to enemies in range); Speed: -60% (to enemies in range); Charge Bonus: -40% (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Master Rune of Speed | `wh2_dlc17_rune_abilities_master_rune_of_speed` | Speed: +45% (to self and allies); Melee Attack: +24 (to self and allies) | In melee, not routing/wobbling → cast on self |
| Maw Shard | `wh3_main_item_abilities_maw_shard` | Spell Mastery: +60% (to self and allies) | In melee, not routing/wobbling → cast on self |
| Merciw's Monstrous Regiment | `wh3_dlc20_cataclysm_bound_merciws_monstrous_regiment` | Melee Attack: +40 (to allies in range); Armour-Piercing Weapon Damage: +50% (to allies in range); Base Weapon Damage: +50% (to allies in range); Physical Resistance: +20 (to allies in range) | In melee, not routing/wobbling → cast on self |
| Merciw's Monstrous Regiment | `wh3_dlc27_cataclysm_bound_merciws_monstrous_regiment` | Melee Attack: +40 (to allies in range); Armour-Piercing Weapon Damage: +50% (to allies in range); Base Weapon Damage: +50% (to allies in range); Physical Resistance: +20 (to allies in range) | In melee, not routing/wobbling → cast on self |
| Miasma of Despair | `wh2_dlc13_lord_abilities_miasma_of_despair` | Speed: -25% (to enemies in range); Leadership: -8 (to enemies in range); Vigour per second: +1% (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Mighty Oath Stone | `wh_dlc06_lord_abilities_mighty_oath_stone` | Melee Defence: +24 (to self and allies); Expert Charge Defence (to self and allies) | In melee, not routing/wobbling → cast on self |
| Mighty Roar | `wh2_dlc15_unit_abilities_mighty_roar` | Speed: -25% (to enemies in range); Leadership: -8 (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Mirror (Cold-Blooded) | `wh2_dlc15_unit_abilities_mimic_cold_blooded` | Leadership: +16 (to self and allies); Stops Rampage! (to self and allies); Vigour per second: -10% (to self and allies) | In melee, not routing/wobbling → cast on self |
| Mirror (Feint & Riposte) | `wh2_dlc15_unit_abilities_mimic_feint_and_riposte` | Melee Attack: +24; Melee Defence: +24; Physical Resistance: +20 | In melee, not routing/wobbling → cast on self |
| Mirror (Grand Hammer of Faith) | `wh2_dlc15_unit_abilities_mimic_grand_hammer_of_faith` | Melee Attack: +24; Damage Resistance: +20 | In melee, not routing/wobbling → cast on self |
| Mirror (Grom's Big Waaagh!) | `wh2_dlc15_unit_abilities_mimic_grom_waaagh` | Melee Attack: +40; Armour-Piercing Weapon Damage: +25%; Base Weapon Damage: +25%; Immune to Psychology; Heals: +0.8% per tick | In melee, not routing/wobbling → cast on self |
| Mirror (Waaagh!) | `wh2_dlc15_unit_abilities_mimic_waaagh` | Melee Attack: +24; Armour-Piercing Weapon Damage: +25%; Base Weapon Damage: +25%; Immune to Psychology | In melee, not routing/wobbling → cast on self |
| Missile Mirror | `wh3_dlc24_unit_bound_missile_mirror` | Redirects projectiles back towards the firing unit | In melee, not routing/wobbling → cast on self |
| Mither | `wh2_dlc15_hero_abilities_mither` | Charge Speed: -60% (to enemies in range); Speed: -60% (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Monstrous Strength | `wh2_dlc13_lord_abilities_monstrous_strength` | Bonus vs. Infantry: +16; Armour-Piercing Weapon Damage: +25%; Base Weapon Damage: +25% | In melee, not routing/wobbling → cast on self |
| Moonshine | `wh2_dlc11_item_abilities_moonshine` | Armour-Piercing Weapon Damage: +25%; Base Weapon Damage: +25%; Flame Resistance: -40; Unbreakable; Heals: +0.8% per tick | In melee, not routing/wobbling → cast on self |
| Morgrim's Eye | `wh3_dlc23_item_abilities_morgrims_eye` | Armour-Piercing Missile Damage: +25% (to self and allies); Accuracy: +60 (to self and allies) | In melee, not routing/wobbling → cast on self |
| Mortal Blow | `wh3_main_daemon_arms_abilities_mortal_blow` | Armour-Piercing Weapon Damage: +35%; Base Weapon Damage: +35% | In melee, not routing/wobbling → cast on self |
| Mortal Blow Upgraded | `wh3_main_daemon_arms_abilities_mortal_blow_upgraded` | Armour-Piercing Weapon Damage: +50%; Base Weapon Damage: +50%; Imbuement: Sundered Armour | In melee, not routing/wobbling → cast on self |
| Mumbo-Jumbo Chant | `wh3_dlc26_character_abilities_mumbo_jumbo_chant` | Melee Attack: +24 (to allies in range); Armour-Piercing Weapon Damage: +25% (to allies in range); Base Weapon Damage: +25% (to allies in range); Leadership: +16 (to allies in range) | In melee, not routing/wobbling → cast on self |
| Muster of Malevolents | `wh2_dlc16_character_abilities_muster_of_malevolents` | Vigour per second: +100% (to enemies in range); Damage: 144 every 2s (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Necrostrike | `wh2_dlc09_character_abilities_strike_of_nagash` | Base Weapon Damage: +90%; Can Cause Terror | In melee, not routing/wobbling → cast on self |
| Neferra's Scrolls of Mighty Incantations | `wh2_dlc09_item_abilities_neferras_scrolls_of_mighty_incantations` | Power Recharge: +160%; Reserves Per Second: +0.20 | In melee, not routing/wobbling → cast on self |
| Net Dem Up! | `wh3_dlc26_unit_abilities_net_dem_up` | Missile Block Chance: -50 (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Net of Amyntok | `wh_dlc04_spell_bound_net_of_amyntok` | enemy speed debuff (hex, under fire) | In melee, not routing/wobbling → cast on self |
| Null Stone | `wh3_dlc27_item_abilities_null_stone` | Silenced (to allies and enemies in range); Removes magical attacks (to allies and enemies in range) | In melee, not routing/wobbling → cast on self |
| Nurgle's Favoured Son | `wh3_dlc25_lord_abilities_nurgles_favoured_son` | Melee Defence: +24; Damage Resistance: +20 | In melee, not routing/wobbling → cast on self |
| Oath of Vengeance | `wh2_dlc10_lord_abilities_oath_of_vengeance` | Melee Defence: -24 (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Oil Flask | `wh2_dlc13_lord_abilities_oil_flask` | Speed: -45%; Weakness to Fire Damage: -40 | In melee, not routing/wobbling → cast on self |
| Okkam's Mindrazor | `wh3_dlc29_spell_bound_okkams_mindrazor` | Armour-Piercing Weapon Damage: +50%; Base Weapon Damage: +50%; Magical Attacks | In melee, not routing/wobbling → cast on self |
| Opal Amulet | `wh_main_item_abilities_opal_amulet` | Damage Resistance: +20 | In melee, not routing/wobbling → cast on self |
| Oracle of Eternity | `wh3_main_lord_abilities_oracle_of_eternity` | Damage Resistance: +44 | In melee, not routing/wobbling → cast on self |
| Orcs are da Best! | `wh3_dlc26_character_abilities_orcs_are_da_best` | Melee Attack: +24 (to allies in range); Armour-Piercing Weapon Damage: +50% (to allies in range); Base Weapon Damage: +50% (to allies in range) | In melee, not routing/wobbling → cast on self |
| Otto's Scythe | `wh3_dlc29_item_active_ottos_scythe` | Melee Attack: -40 (to enemies in range); Leadership: -24 (to enemies in range); Removes Expert Charge Defence (to enemies in range); Removes Charge Defence vs Large (to enemies in range); Removes Charge Reflection (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Overseer of the Unseen | `wh3_dlc29_hero_active_overseer_of_the_unseen` | Melee Attack: +40 (to allies in range); Cannot Die (to allies in range); Unbreakable (to allies in range) | In melee, not routing/wobbling → cast on self |
| Pack Trap | `wh3_dlc24_unit_abilities_pack_trap` | Vigour per second: +3% (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Pageant of Shrikes | `wh2_dlc16_character_abilities_pageant_of_shrikes` | Range: -20% (to enemies in range); Reload Skill: -20 (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Pearl of Infinite Bleakness | `wh2_main_item_abilities_pearl_of_infinite_bleakness` | Leadership: +8 (to self and allies); Immune to Psychology (to self and allies) | In melee, not routing/wobbling → cast on self |
| Pendant of Slaanesh | `wh_main_item_abilities_pendant_of_slaanesh` | Speed: +25%; Melee Attack: +40 | In melee, not routing/wobbling → cast on self |
| Pestilent Potions | `wh3_dlc20_item_abilities_pestilent_potions` | Melee Attack: -24 (to enemies in range); Armour-Piercing Weapon Damage: -25% (to enemies in range); Base Weapon Damage: -25% (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Pha's Protection | `wh3_main_spell_bound_phas_protection` | Armour: +30 (to self and allies); Melee Defence: +24 (to self and allies) | In melee, not routing/wobbling → cast on self |
| Pilgrimage of Skulls | `wh3_dlc26_lord_abilities_pilgrimage_of_skulls` | Unbreakable (to self and allies); Vigour per second: -1% (to self and allies) | In melee, not routing/wobbling → cast on self |
| Plague of Rust | `wh3_main_spell_bound_plague_of_rust` | Armour: -30 (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Plaguefather's Oration | `wh3_main_lord_abilities_plaguefathers_oration` | Melee Defence: +24 (to self and allies); Leadership: +16 (to self and allies) | In melee, not routing/wobbling → cast on self |
| Plaque of Dominion | `wh2_main_item_abilities_plaque_of_dominion` | Leadership: -8 (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Potion of Farsight | `wh3_main_item_abilities_potion_of_farsight` | Range: +30%; Forest Spotting: +100%; stat_spotting_scrub: +100%; Imbuement: Sundered Armour | In melee, not routing/wobbling → cast on self |
| Potion of Foolhardiness | `wh_main_item_abilities_potion_of_foolhardiness` | Charge Bonus: +40%; Unbreakable | In melee, not routing/wobbling → cast on self |
| Potion of Speed | `wh_main_item_abilities_potion_of_speed` | Charge Speed: +25%; Acceleration: +18%; Speed: +25%; Vigour per second: -1% | In melee, not routing/wobbling → cast on self |
| Potion of Strength | `wh_main_item_abilities_potion_of_strength` | Armour-Piercing Weapon Damage: +50%; Base Weapon Damage: +50% | In melee, not routing/wobbling → cast on self |
| Power Familiar | `wh3_dlc27_item_abilities_power_familiar` | Spell Mastery: +20% | In melee, not routing/wobbling → cast on self |
| Power Siphon | `wh2_dlc11_lord_abilities_power_siphon` | Vigour per second: +1% (to enemies in range); Ability recharge: +15s (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Power Stone | `wh_main_item_abilities_power_stone` | Power Recharge: +80%; Reserves Per Second: +0.10 | In melee, not routing/wobbling → cast on self |
| Predatory Instincts | `wh3_cp1_lord_abilities_predatory_instincts` | Melee Attack: +24 (to self and allies); Armour-Piercing Weapon Damage: +25% (to self and allies); Base Weapon Damage: +25% (to self and allies); Can Cause Fear (to self and allies) | In melee, not routing/wobbling → cast on self |
| Prey of Anath Raema | `wh_dlc05_character_abilities_prey_of_anath_raema` | Missile Resistance: -20 (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Prey of the Blood God | `wh3_pro12_hero_abilities_prey_of_the_blood_god` | Damage: 33 every 1s (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Primal Roar | `wh2_dlc13_lord_abilities_primal_roar` | Melee Attack: +40 (to self and allies); Physical Resistance: +20 (to self and allies); Rampage! (to self and allies) | In melee, not routing/wobbling → cast on self |
| Primeval Roar | `wh2_dlc17_unit_abilities_primeval_roar` | Melee Attack: +24 (to self and allies) | In melee, not routing/wobbling → cast on self |
| Prismatic Amplifier | `wh3_main_item_abilities_prismatic_amplifier` | Power Recharge: +160% | In melee, not routing/wobbling → cast on self |
| Puncture | `wh3_dlc26_character_abilities_puncture` | Melee Attack: +24; Imbuement: Sundered Armour | In melee, not routing/wobbling → cast on self |
| Quickblood | `wh3_dlc29_lord_abilities_lightning_reflexes` | Melee Attack: +24; Executioner | In melee, not routing/wobbling → cast on self |
| Quicksilver Strike | `wh3_dlc27_lord_abilities_quicksilver_strike` | Melee Attack: +40; Armour-Piercing Weapon Damage: +50%; Base Weapon Damage: +50% | In melee, not routing/wobbling → cast on self |
| Rage Embodied | `wh3_main_lord_abilities_rage_embodied` | Rampage! (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Rage Incarnate | `wh3_main_lord_abilities_rage_incarnate` | Rampage! (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Rally! | `wh_main_character_abilities_rally` | Leadership: +16 (to self and allies) | In melee, not routing/wobbling → cast on self |
| Rapier of Ecstasy | `wh3_dlc20_weapon_abilities_rapier_of_ecstasy` | Melee Attack: +24; Imbuement: Euphoric! | In melee, not routing/wobbling → cast on self |
| Ravaging Swarm | `wh3_dlc29_hero_active_dispatch_the_swarm_attack` | Melee Defence: -24 (to enemies in range); Vigour per second: +1% (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Ravaging Swarm Upgraded | `wh3_dlc29_hero_active_dispatch_the_swarm_attack_upgraded` | Melee Defence: -40 (to enemies in range); Vigour per second: +4% (to enemies in range); Damage: 4 every 1s (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Reanimate | `wh2_dlc09_character_abilities_tomb_king_rally` | Leadership: +16 (to self and allies) | In melee, not routing/wobbling → cast on self |
| Reanimate Upgraded | `wh2_dlc09_character_abilities_tomb_king_rally_upgraded` | Leadership: +16 (to self and allies); Heals: +0.8% per tick (to self and allies) | In melee, not routing/wobbling → cast on self |
| Red Fury | `wh_main_character_abilities_red_fury` | Charge Bonus: +20% (to self and allies); Armour-Piercing Weapon Damage: +25% (to self and allies); Vigour per second: -1% (to self and allies) | In melee, not routing/wobbling → cast on self |
| Red Ruin | `wh2_dlc10_lord_abilities_red_ruin` | Armour-Piercing Weapon Damage: +75%; Base Weapon Damage: +75%; Melee Defence: -24 | In melee, not routing/wobbling → cast on self |
| Refuse to Die | `wh2_dlc12_unit_abilities_refuse_to_die` | Cannot Die | In melee, not routing/wobbling → cast on self |
| Revenge Incarnate | `wh_dlc06_lord_abilities_revenge_incarnate` | Melee Attack: +40; Base Weapon Damage: +60% | In melee, not routing/wobbling → cast on self |
| Rock Eye | `wh3_main_item_passive_rock_eye` | Forest Spotting: +10% (to self and allies); stat_spotting_scrub: +10% (to self and allies) | In melee, not routing/wobbling → cast on self |
| Rok of Itza | `wh2_dlc13_lord_abilities_rock_of_itza` | Physical Resistance: +40; Vigour per second: -3% | In melee, not routing/wobbling → cast on self |
| Rot or Die! | `wh3_dlc25_lord_abilities_rot_or_die` | Melee Damage Reflection: +20 (to self and allies); Leadership: +16 (to self and allies) | In melee, not routing/wobbling → cast on self |
| Rot-pocked Axe | `wh3_dlc29_item_active_rot_pocked_axe` | Melee Attack: +24; Imbuement: Weakened; Armour-Piercing Weapon Damage: +25% (to allies in range); Base Weapon Damage: +25% (to allies in range) | In melee, not routing/wobbling → cast on self |
| Rune Axe of Gotrek | `wh2_pro08_weapon_abilities_rune_axe_of_gotrek` | Armour-Piercing Weapon Damage: +50%; Imbuement: Dampen! Removes Magical Attacks | In melee, not routing/wobbling → cast on self |
| Rune Axe of Grombrindal | `wh_pro01_weapon_abilities_rune_axe_of_grombrindal` | Armour-Piercing Weapon Damage: +50%; Imbuement: Discouraged! | In melee, not routing/wobbling → cast on self |
| Rune of Breaking | `wh2_dlc17_rune_abilities_rune_of_breaking` | Armour-Piercing Weapon Damage: +25% (to self and allies); Base Weapon Damage: +25% (to self and allies); Imbuement: Sundered Armour (to self and allies) | In melee, not routing/wobbling → cast on self |
| Rune of Doom | `wh2_dlc17_lord_abilities_rune_of_doom` | Melee Attack: +24 (to self and allies); Can Cause Fear (to self and allies) | In melee, not routing/wobbling → cast on self |
| Rune of Negation | `wh_main_rune_abilities_rune_of_negation` | Damage Resistance: +40 (to self and allies) | In melee, not routing/wobbling → cast on self |
| Rune of Oath & Steel | `wh_main_rune_abilities_rune_of_oath_and_steel` | Armour: +30 (to self and allies) | In melee, not routing/wobbling → cast on self |
| Rune of Slowness | `wh2_dlc17_rune_abilities_rune_of_slowness` | Charge Speed: -45% (to enemies in range); Speed: -45% (to enemies in range); Charge Bonus: -40% (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Rune of Speed | `wh2_dlc17_rune_abilities_rune_of_speed` | Speed: +45% (to self and allies); Melee Attack: +24 (to self and allies) | In melee, not routing/wobbling → cast on self |
| Rune of Thungni | `wh3_dlc23_item_abilities_rune_of_thungni` | Armour-Piercing Weapon Damage: +25% (to self and allies); Base Weapon Damage: +25% (to self and allies); Imbuement: Sundered Armour (to self and allies) | In melee, not routing/wobbling → cast on self |
| Runefang | `wh_main_weapon_abilities_runefang` | Splash Attack Power: +50%; Armour-Piercing Weapon Damage: +50%; Base Weapon Damage: +50% | In melee, not routing/wobbling → cast on self |
| Sacred Spawning of Xhotl | `wh2_main_lord_abilities_sacred_spawning_of_xhotl` | Physical Resistance: +20; Vigour per second: -1% | In melee, not routing/wobbling → cast on self |
| Sadistic Snare | `wh3_dlc23_lord_abilities_sadistic_snare` | Melee Defence: -24 (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Sands of Sickness | `wh3_dlc25_character_abilities_sands_of_sickness` | Speed: -25% (to enemies in range); Melee Defence: -24 (to enemies in range); Melee Damage Reflection: +20 (to self and allies); Vigour per second: -1% (to self and allies) | In melee, not routing/wobbling → cast on self |
| Scales of the Celestial Court | `wh3_main_item_abilities_scales_of_the_celestial_court` | Physical Resistance: +75; Strider | In melee, not routing/wobbling → cast on self |
| Sceptre of Stability | `wh_main_item_abilities_sceptre_of_stability` | Spell Resistance: +40 (to self and allies) | In melee, not routing/wobbling → cast on self |
| Sceptre of Titans | `wh3_main_weapon_abilities_sceptre_of_titans` | Bonus vs. Large: +24; Armour-Piercing Weapon Damage: +75% | In melee, not routing/wobbling → cast on self |
| Scourge | `wh_dlc03_weapon_abilities_scourge` | Splash Attack Power: +50%; Bonus vs. Infantry: +32; Armour-Piercing Weapon Damage: +25%; Base Weapon Damage: +25% | In melee, not routing/wobbling → cast on self |
| Scroll of Destiny | `wh3_main_item_abilities_scroll_of_destiny` | Reserves Per Second: +0.40 | In melee, not routing/wobbling → cast on self |
| Scroll of Leeching | `wh_main_item_abilities_scroll_of_leeching` | Power Recharge: -40% (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Scroll of Shielding | `wh_main_item_abilities_scroll_of_shielding` | Damage Resistance: +20 (to self and allies) | In melee, not routing/wobbling → cast on self |
| Scrying Stone | `wh2_main_item_abilities_scrying_stone` | Leadership: +8; Damage Resistance: +20 | In melee, not routing/wobbling → cast on self |
| Seduction of the Serpent | `wh_dlc08_lord_abilities_seduction_of_the_serpent` | Melee Defence: +24; Leadership: +16; Imbuement: Discouraged! | In melee, not routing/wobbling → cast on self |
| Shadow Shroud | `wh3_main_lord_abilities_shadow_shroud` | Damage Resistance: +60 | In melee, not routing/wobbling → cast on self |
| Shield of Aeons | `wh2_dlc13_item_abilities_shield_of_aeons` | Armour: +60 (to self and allies); Expert Charge Defence (to self and allies); Charge Reflection (to self and allies) | In melee, not routing/wobbling → cast on self |
| Shield of Chaqua | `wh2_dlc12_unit_abilities_shield_of_chaqua` | Missile Resistance: +40 (to self and allies) | In melee, not routing/wobbling → cast on self |
| Shield of Faith | `wh_main_spell_bound_shield_of_faith` | Damage Resistance: +20 (to self and allies) | In melee, not routing/wobbling → cast on self |
| Shield of the Old Ones | `wh2_main_character_abilities_shield_of_the_old_ones` | Leadership: +8 (to self and allies); Damage Resistance: +20 (to self and allies) | In melee, not routing/wobbling → cast on self |
| Shielding Swarm | `wh3_dlc29_hero_active_dispatch_the_swarm_protect` | Melee Defence: +24 (to self and allies); Missile Block Chance: +36 (to self and allies) | In melee, not routing/wobbling → cast on self |
| Shielding Swarm Upgraded | `wh3_dlc29_hero_active_dispatch_the_swarm_protect_upgraded` | Melee Defence: +36 (to self and allies); Missile Block Chance: +48 (to self and allies); 360 Missile Block (to self and allies) | In melee, not routing/wobbling → cast on self |
| Shock Collar | `wh2_dlc16_hero_abilities_shock_collar` | Melee Attack: +24 (to self and allies); Leadership: +16 (to self and allies); Immune to Psychology (to self and allies) | In melee, not routing/wobbling → cast on self |
| Silence the Prey | `wh3_main_character_abilities_silence_the_prey` | Ability recharge: +30s (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Silver Dagger | `wh3_dlc23_weapon_abilities_silver_dagger` | Armour-Piercing Weapon Damage: +25%; Base Weapon Damage: +25%; Magical Attacks | In melee, not routing/wobbling → cast on self |
| Skavenbrew | `wh2_main_item_abilities_skavenbrew` | Armour: -30 (to self and allies); Melee Attack: +40 (to self and allies); Base Weapon Damage: +30% (to self and allies); Immune to Psychology (to self and allies) | In melee, not routing/wobbling → cast on self |
| Skjalandir's Fall | `wh3_dlc23_character_abilities_skjalandirs_fall` | Accuracy: +90; Imbuement: Blinded! | In melee, not routing/wobbling → cast on self |
| Skull of Rarkos | `wh_dlc03_item_abilities_skull_of_rarkos` | Reserves Per Second: +0.40 | In melee, not routing/wobbling → cast on self |
| Skull Wand of Kaloth | `wh_main_item_abilities_skull_wand_of_kaloth` | Melee Attack: +24; Base Weapon Damage: +60%; Imbuement: Discouraged! | In melee, not routing/wobbling → cast on self |
| Slayer for Chaos | `wh3_dlc23_item_abilities_slayer_for_chaos` | Melee Attack: +12; Cannot Die; Can Cause Terror; Unbreakable | In melee, not routing/wobbling → cast on self |
| Slippery | `wh_main_hero_abilities_slippery` | Speed: +25%; Melee Defence: +24 | In melee, not routing/wobbling → cast on self |
| Sliverslash | `wh3_dlc20_weapon_abilities_sliverslash` | Armour-Piercing Weapon Damage: +50%; Base Weapon Damage: +50%; Magical Attacks; Imbuement: Sundered Armour | In melee, not routing/wobbling → cast on self |
| Smash 'Em Faster | `wh2_dlc15_lord_abilities_smash_em_faster` | Melee Attack: +24 (to self and allies); Leadership: +16 (to self and allies) | In melee, not routing/wobbling → cast on self |
| Snowflake Pendant | `wh3_main_item_abilities_snowflake_pendant` | Miscast Chance: -50% (to self and allies); Power Recharge: +160% (to self and allies) | In melee, not routing/wobbling → cast on self |
| Spearfisher's Net | `wh2_dlc11_lord_abilities_spearfishers_net` | Melee Defence: -24 (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Spell-Wrought Sceptre | `wh3_dlc23_weapon_abilities_spell_wrought_sceptre` | Ability recharge: -30s (to self and allies) | In melee, not routing/wobbling → cast on self |
| Spiderweb Attack | `wh3_dlc26_character_abilities_spider_web_attack` | enemy melee debuff (hex) | In melee, not routing/wobbling → cast on self |
| Spite of Da Bad Moon | `wh_dlc06_lord_abilities_spite_of_da_bad_moon` | Bonus vs. Large: +16 (to self and allies); Armour-Piercing Weapon Damage: +25% (to self and allies); Base Weapon Damage: +25% (to self and allies) | In melee, not routing/wobbling → cast on self |
| Staff of Damnation | `wh_main_spell_bound_staff_of_damnation` | Melee Attack: +40 (to self and allies) | In melee, not routing/wobbling → cast on self |
| Staff of Nagash | `wh2_dlc09_item_abilities_staff_of_nagash` | Power Recharge: +160%; Ability recharge: -30s | In melee, not routing/wobbling → cast on self |
| Staff of Tomorrow | `wh3_main_weapon_abilities_staff_of_tomorrow` | Ability recharge: -120s | In melee, not routing/wobbling → cast on self |
| Staff of Volans | `wh_main_item_abilities_staff_of_volans` | Miscast Chance: -50%; Power Recharge: +240% | In melee, not routing/wobbling → cast on self |
| Staff of Wu Xing | `wh3_main_item_abilities_staff_of_wu_xing` | Power Recharge: +240%; Reserves Per Second: +0.30 | In melee, not routing/wobbling → cast on self |
| Stand or Die! | `wh_main_character_abilities_stand_or_die` | Melee Defence: +24 (to self and allies); Leadership: +16 (to self and allies) | In melee, not routing/wobbling → cast on self |
| Starcrusher | `wh_dlc01_weapon_abilities_starcrusher` | Splash Attack Power: +50%; Armour-Piercing Weapon Damage: +50%; Base Weapon Damage: +50% | In melee, not routing/wobbling → cast on self |
| Starwood Staff | `wh2_main_item_abilities_starwood_staff` | Reserves Per Second: +0.40 | In melee, not routing/wobbling → cast on self |
| Stave of Avelorn | `wh2_dlc10_item_abilities_stave_of_avelorn` | Miscast Chance: -100%; Power Recharge: +160% | In melee, not routing/wobbling → cast on self |
| Steppe Hunter's Horn | `wh3_main_item_abilities_steppe_hunters_horn` | Bonus vs. Large: +100% (to self and allies); Charge Defence vs. Large (to self and allies) | In melee, not routing/wobbling → cast on self |
| Stinky Giant Club | `wh_dlc08_weapon_abilities_stinky_giant_club` | Melee Attack: +24; Base Weapon Damage: +60% | In melee, not routing/wobbling → cast on self |
| Supreme Shield of the Old Ones | `wh2_dlc12_character_abilities_supreme_shield_of_the_old_ones` | Damage Resistance: +40 (to self and allies) | In melee, not routing/wobbling → cast on self |
| Sword of Anti-Heroes | `wh_main_weapon_abilities_sword_of_anti_heroes` | Armour-Piercing Weapon Damage: +50%; Base Weapon Damage: +50% | In melee, not routing/wobbling → cast on self |
| Sword of Filth | `wh3_dlc25_weapon_abilities_sword_of_filth` | Armour: -30 (to enemies in range); Melee Defence: -24 (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Sword of Torgald | `wh_dlc08_weapon_abilities_sword_of_torgald` | Armour-Piercing Weapon Damage: +50%; Base Weapon Damage: +50%; Magical Attacks; Imbuement: Inevitable End! | In melee, not routing/wobbling → cast on self |
| Tacticians, Rally! | `wh3_dlc24_character_abilities_tacticians_rally` | Leadership: +16 (to self and allies) | In melee, not routing/wobbling → cast on self |
| Talisman of Loec | `wh2_main_item_abilities_talisman_of_loec` | Melee Attack: +24; Base Weapon Damage: +30% | In melee, not routing/wobbling → cast on self |
| Taunt | `wh2_dlc11_character_abilities_taunt` | Speed: -25% (to enemies in range); Armour: -30 (to enemies in range); Melee Defence: -24 (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Tendrils of the Sea | `wh3_dlc29_hero_active_tendrils_of_the_sea` | Charge Speed: -60% (to enemies in range); Speed: -60% (to enemies in range); Mass: -20% (to enemies in range); Melee Attack: -40 (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Tenebrous Forge-Hammer | `wh3_dlc27_weapon_abilities_tenebrous_forge_hammer` | Armour-Piercing Weapon Damage: +20% (to self and allies); Base Weapon Damage: +20% (to self and allies) | In melee, not routing/wobbling → cast on self |
| Terrorgheist Skull | `wh_dlc08_item_abilities_terrorgheist_skull` | Imbuement: Blinded! (to self and allies); Ability recharge: -60s (to self and allies) | In melee, not routing/wobbling → cast on self |
| The Armour of Morkar | `wh3_dlc20_item_abilities_the_armour_of_morkar` | Melee Defence: +24 (to self and allies); Charge Reflection (to self and allies) | In melee, not routing/wobbling → cast on self |
| The Averland Runefang | `wh2_dlc13_weapon_abilities_averland_runefang` | Melee Attack: -40 (to enemies in range); Base Weapon Damage: -60% (to enemies in range) | In melee, not routing/wobbling → cast on self |
| The Bane Shield | `wh2_main_item_abilities_the_bane_shield` | Armour: +30 (to self and allies); Missile Block Chance: +24 (to self and allies) | In melee, not routing/wobbling → cast on self |
| The Bane Spear | `wh3_main_weapon_abilities_banespear` | Damage: 10 every 1s (to enemies in range) | In melee, not routing/wobbling → cast on self |
| The Black Axe of Krell | `wh3_dlc29_item_abilities_black_axe_of_krell` | Melee Attack: +24; Armour-Piercing Weapon Damage: +30%; Base Weapon Damage: +30%; Imbuement: Disembowelled! | In melee, not routing/wobbling → cast on self |
| The Black Cleaver | `wh3_dlc25_weapon_abilities_the_black_cleaver` | Melee Attack: +24 (to self and allies); Armour-Piercing Weapon Damage: +25% (to self and allies); Base Weapon Damage: +25% (to self and allies); Magical Attacks (to self and allies) | In melee, not routing/wobbling → cast on self |
| The Black Tongue | `wh3_dlc27_character_abilities_the_black_tongue` | Silenced (to enemies in range) | In melee, not routing/wobbling → cast on self |
| The Blessed Blade of Ptra | `wh2_dlc09_weapon_abilities_blessed_blade_of_ptra` | Magical Attacks; Flaming Attacks; Imbuement: Blinded! | In melee, not routing/wobbling → cast on self |
| The Blood Price | `wh2_dlc14_lord_abilities_the_blood_price` | Armour-Piercing Weapon Damage: +60%; Base Weapon Damage: +60%; Damage Resistance: +20; Damage: 60 every 2s | In melee, not routing/wobbling → cast on self |
| The Carstein Ring | `wh_dlc04_item_abilities_the_carstein_ring` | Damage Resistance: +60 | In melee, not routing/wobbling → cast on self |
| The Chromatic Tome | `wh3_main_item_abilities_the_chromatic_tome` | Power Recharge: +80% (to self and allies); Reserves Per Second: +0.10 (to self and allies) | In melee, not routing/wobbling → cast on self |
| The Daemon's Curse | `wh2_dlc14_lord_abilities_the_daemons_curse` | Melee Defence: -24 (to enemies in range); Leadership: -10 (to enemies in range) | In melee, not routing/wobbling → cast on self |
| The Dance of Dreaming | `wh3_dlc27_lord_abilities_the_dance_of_dreaming` | Leadership: -6 (to enemies in range); Damage: 4 every 1s (to enemies in range) | In melee, not routing/wobbling → cast on self |
| The Dancing Blade | `wh3_dlc23_character_abilities_sword_dance` | Melee Attack: -24 (to enemies in range); Melee Defence: +24; Physical Resistance: +40 | In melee, not routing/wobbling → cast on self |
| The Dark Master | `wh3_main_lord_abilities_the_dark_master` | Melee Attack: -40 (to enemies in range) | In melee, not routing/wobbling → cast on self |
| The Dragon's Fang | `wh3_dlc24_weapon_abilities_dragons_fang` | Melee Attack: +40; Armour-Piercing Weapon Damage: +50%; Base Weapon Damage: +50%; Executioner | In melee, not routing/wobbling → cast on self |
| The Drakwald Runefang | `wh2_dlc13_weapon_abilities_drakwald_runefang` | Physical Resistance: +40; Vigour per second: -3% | In melee, not routing/wobbling → cast on self |
| The Enfeebling Foe | `wh3_dlc23_spell_bound_enfeebling_foe` | Melee Attack: -24 (to enemies in range); Melee Defence: -24 (to enemies in range) | In melee, not routing/wobbling → cast on self |
| The Enfeebling Foe | `wh3_dlc27_spell_bound_enfeebling_foe` | Melee Attack: -24 (to enemies in range); Melee Defence: -24 (to enemies in range) | In melee, not routing/wobbling → cast on self |
| The Enfeebling Foe | `wh3_main_spell_bound_enfeebling_foe` | Melee Attack: -24 (to enemies in range); Melee Defence: -24 (to enemies in range) | In melee, not routing/wobbling → cast on self |
| The Enfeebling Foe | `wh3_twa08_spell_bound_enfeebling_foe_keeper_of_secrets_ror` | Melee Attack: -24 (to enemies in range); Melee Defence: -24 (to enemies in range) | In melee, not routing/wobbling → cast on self |
| The Eternal Blade | `wh3_main_weapon_abilities_the_eternal_blade` | Melee Attack: +40 (to self and allies); Armour-Piercing Weapon Damage: +50% (to self and allies); Base Weapon Damage: +50% (to self and allies) | In melee, not routing/wobbling → cast on self |
| The Father of Blades | `wh3_dlc25_weapon_abilities_the_father_of_blades` | Melee Attack: -24 (to enemies in range); Armour-Piercing Weapon Damage: +25% | In melee, not routing/wobbling → cast on self |
| The Golden Eye of Tzeentch | `wh3_dlc24_item_abilities_the_golden_eye_of_tzeentch` | Missile Resistance: +40; Restores barrier | In melee, not routing/wobbling → cast on self |
| The Guiding Eye | `wh2_main_item_abilities_the_guiding_eye` | Armour-Piercing Missile Damage: +20% (to self and allies) | In melee, not routing/wobbling → cast on self |
| The Hammer of Karak Drazh | `wh_main_weapon_abilities_the_hammer_of_karak_drazh` | Melee Attack: -40 (to enemies in range); Base Weapon Damage: -30% (to enemies in range) | In melee, not routing/wobbling → cast on self |
| The Hand of Dust | `wh3_dlc29_spell_bound_undeath_sulekhim_hand_of_dust` | Armour-Piercing Weapon Damage: +50% (to self and allies); Magical Attacks (to self and allies) | In melee, not routing/wobbling → cast on self |
| The Hochland Runefang | `wh2_dlc13_weapon_abilities_hochland_runefang` | Armour: -60 (to enemies in range); Melee Defence: -24 (to enemies in range) | In melee, not routing/wobbling → cast on self |
| The Liber Mortis | `wh2_dlc09_lord_abilities_the_liber_mortis` | Leadership: +8 (to self and allies); Physical Resistance: +40 (to self and allies) | In melee, not routing/wobbling → cast on self |
| The Liber Noctus | `wh_dlc04_item_abilities_the_liber_noctus` | Power Recharge: +240%; Reserves Per Second: +0.30; Damage: 33 every 1s; Ability recharge: -30s | In melee, not routing/wobbling → cast on self |
| The Lion's Shield | `wh_dlc07_lord_abilities_lions_shield` | Spell Resistance: +40; Missile Resistance: +40 | In melee, not routing/wobbling → cast on self |
| The Mace of Helsturm | `wh_main_weapon_abilities_the_mace_of_helsturm` | Armour-Piercing Weapon Damage: +50%; Base Weapon Damage: +50%; Flaming Attacks | In melee, not routing/wobbling → cast on self |
| The Nordland Runefang | `wh2_dlc13_weapon_abilities_nordland_runefang` | Damage: 5 every 1s (to enemies in range) | In melee, not routing/wobbling → cast on self |
| The Ostermark Runefang | `wh2_dlc13_weapon_abilities_ostermark_runefang` | Bonus vs. Large: +32 (to self and allies); Charge Defence vs. Large (to self and allies) | In melee, not routing/wobbling → cast on self |
| The Ostland Runefang | `wh2_dlc13_weapon_abilities_ostland_runefang` | Armour-Piercing Weapon Damage: +50%; Base Weapon Damage: +50% | In melee, not routing/wobbling → cast on self |
| The Phoenix Blade | `wh3_dlc27_weapon_abilities_the_phoenix_blade` | Bonus vs. Large: +16; Armour-Piercing Weapon Damage: +50%; Base Weapon Damage: +50%; Imbuement: Flammable! | In melee, not routing/wobbling → cast on self |
| The Praise of Slaanesh | `wh3_dlc27_lord_abilities_the_praise_of_slaanesh` | Melee Attack: -36; Melee Defence: +36; Missile Block Chance: +36; 360 Missile Block | In melee, not routing/wobbling → cast on self |
| The Reikland Runefang | `wh_main_weapon_abilities_the_reikland_runefang` | Melee Attack: +24 (to self and allies); Leadership: +8 (to self and allies) | In melee, not routing/wobbling → cast on self |
| The Rock of Inevitability | `wh3_main_item_abilities_the_rock_of_inevitability` | Charge Speed: -25% (to enemies in range); Speed: -25% (to enemies in range); Melee Defence: -26 (to enemies in range) | In melee, not routing/wobbling → cast on self |
| The Rotaxes | `wh3_dlc29_item_active_the_rotaxes` | Melee Attack: +24; Armour-Piercing Weapon Damage: +50%; Base Weapon Damage: +50%; Executioner | In melee, not routing/wobbling → cast on self |
| The Seerstaff of Saphery | `wh2_main_spell_bound_the_seerstaff_of_saphery` | Melee Attack: +24 (to self and allies); Reload Skill: +40 (to self and allies) | In melee, not routing/wobbling → cast on self |
| The Shadow's Coil | `wh_dlc05_unit_abilities_the_shadows_coil` | Melee Attack: -24; Melee Defence: +24 | In melee, not routing/wobbling → cast on self |
| The Slayer of Kings | `wh_dlc01_weapon_abilities_the_slayer_of_kings` | Splash Attack Power: +50%; Armour-Piercing Weapon Damage: +75%; Base Weapon Damage: +75% | In melee, not routing/wobbling → cast on self |
| The Slayer Sword | `wh3_dlc26_weapon_abilities_the_slayer_sword` | Melee Attack: +24; Armour-Piercing Weapon Damage: +50%; Base Weapon Damage: +50%; Imbuement: Weakened | In melee, not routing/wobbling → cast on self |
| The Sword of Couronne | `wh_main_weapon_abilities_the_sword_of_couronne` | Armour: -30 (to enemies in range); Melee Defence: -24 (to enemies in range) | In melee, not routing/wobbling → cast on self |
| The Sword of Lyonesse | `wh2_dlc14_weapon_abilities_sword_of_lyonesse` | Melee Attack: +40; Armour-Piercing Weapon Damage: +50%; Base Weapon Damage: +50% | In melee, not routing/wobbling → cast on self |
| The Talabecland Runefang | `wh2_dlc13_weapon_abilities_talabecland_runefang` | Melee Attack: +40; Imbuement: Sundered Armour | In melee, not routing/wobbling → cast on self |
| The Tenderiser | `wh3_main_weapon_abilities_the_tenderiser` | Armour-Piercing Weapon Damage: +50% (to self and allies); Base Weapon Damage: +50% (to self and allies) | In melee, not routing/wobbling → cast on self |
| The Trickster's Pendant | `wh2_main_item_abilities_the_tricksters_pendant` | Miscast Chance: +100% (to enemies in range) | In melee, not routing/wobbling → cast on self |
| The Vial of Hashut | `wh3_dlc23_item_abilities_the_vial_of_hashut` | Armour: -60 (to enemies in range); Weakness to Fire Damage: -20 (to enemies in range) | In melee, not routing/wobbling → cast on self |
| The Vortex Shard | `wh2_main_item_abilities_the_vortex_shard` | Power Recharge: -80% (to enemies in range) | In melee, not routing/wobbling → cast on self |
| The Waltz of Lethargy | `wh3_dlc27_lord_abilities_the_waltz_of_lethargy` | Melee Attack: -6 (to enemies in range); Melee Attack: +6 (to self and allies); Unyielding Assault (to self and allies) | In melee, not routing/wobbling → cast on self |
| The Wintertooth Crown | `wh_dlc08_item_abilities_the_wintertooth_crown` | Melee Defence: +24 (to self and allies); Unbreakable (to self and allies) | In melee, not routing/wobbling → cast on self |
| The Wissenland Runefang | `wh2_dlc13_weapon_abilities_wissenland_runefang` | Speed: -45% (to enemies in range); Vigour per second: +1% (to enemies in range) | In melee, not routing/wobbling → cast on self |
| The Withering | `wh3_dlc23_spell_bound_the_withering` | Armour: -30 (to enemies in range); Leadership: -8 (to enemies in range) | In melee, not routing/wobbling → cast on self |
| The Withering | `wh3_twa08_spell_bound_the_withering` | Armour: -30 (to enemies in range); Leadership: -8 (to enemies in range) | In melee, not routing/wobbling → cast on self |
| They Needs Stabbin’ | `wh2_dlc15_character_abilities_they_needs_stabbin` | Armour: -30 (to enemies in range); Melee Defence: -24 (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Thorn's Aura | `wh3_dlc24_hero_abilities_thorns_aura` | Melee Damage Reflection: +14 (to self and allies) | In melee, not routing/wobbling → cast on self |
| Thunderburner | `wh3_dlc25_unit_abilities_thunderburner` | Turn Speed: -70%; Speed: +150%; Damage: 30 every 0.2s | In melee, not routing/wobbling → cast on self |
| Thunderburner Upgraded | `wh3_dlc25_unit_abilities_thunderburner_upgraded` | Turn Speed: -70%; Speed: +200%; Damage: 10 every 0.2s | In melee, not routing/wobbling → cast on self |
| Titan Headsman | `wh3_dlc25_hero_abilities_titan_headsman` | Speed: -45% (to enemies in range); Melee Defence: -24 (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Toad Rage | `wh2_dlc12_unit_abilities_toad_rage` | Armour-Piercing Weapon Damage: +50%; Base Weapon Damage: +50%; Rampage! | In melee, not routing/wobbling → cast on self |
| Tombstrike | `wh2_dlc09_character_abilities_strike_of_tombs` | Melee Attack: +24; Base Weapon Damage: +30%; Can Cause Terror | In melee, not routing/wobbling → cast on self |
| Tor's Battle Hymn | `wh3_main_character_abilities_tors_battle_hymn` | Melee Attack: +40 (to self and allies) | In melee, not routing/wobbling → cast on self |
| Torment Blade | `wh3_main_weapon_abilities_torment_blade` | Melee Attack: -24 (to enemies in range); Armour-Piercing Weapon Damage: -25% (to enemies in range); Base Weapon Damage: -25% (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Tormentor Sword | `wh_main_weapon_abilities_tormentor_sword` | Melee Attack: -24 (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Transfix | `wh2_dlc11_lord_abilities_transfix` | Speed: +25%; Damage Resistance: +20; Imbuement: Discouraged! | In melee, not routing/wobbling → cast on self |
| Trickster's Shard | `wh_main_item_abilities_tricksters_shard` | Miscast Chance: +100% (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Trophy Heads | `wh2_main_lord_abilities_trophy_heads` | Melee Attack: -24 (to enemies in range); Melee Defence: -40 (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Trophy Heads | `wh3_main_daemon_wings_abilities_trophy_heads` | Melee Attack: -30 (to enemies in range); Melee Defence: -30 (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Twilight Horn I | `wh2_dlc16_item_abilities_twilight_horn_i` | Charge Speed: +25% (to self and allies); Speed: +25% (to self and allies); Charge Bonus: +20% (to self and allies) | In melee, not routing/wobbling → cast on self |
| Ultimate Verdict | `wh3_cp1_character_abilities_terrifying_presence` | Melee Defence: -24 (to enemies in range); Can Cause Terror; Executioner | In melee, not routing/wobbling → cast on self |
| Undeath Resurgent | `wh_main_character_abilities_undeath_resurgent` | Melee Defence: +24 (to self and allies); Leadership: +16 (to self and allies) | In melee, not routing/wobbling → cast on self |
| Unholy Clamour | `wh2_main_mount_abilities_unholy_clamour` | Leadership: +16 (to self and allies); Vigour per second: -1% (to self and allies) | In melee, not routing/wobbling → cast on self |
| Unlimited Power! | `wh2_dlc12_lord_abilities_unlimited_power` | Power Recharge: +160%; Reserves Per Second: +0.20 | In melee, not routing/wobbling → cast on self |
| Unstoppable Choppas | `wh3_dlc26_unit_abilities_unstoppable_choppas` | Armour-Piercing Weapon Damage: +50%; Base Weapon Damage: +50%; Melee Defence: -24 | In melee, not routing/wobbling → cast on self |
| Unyielding Defence | `wh3_main_character_abilities_unyielding_defender` | Melee Defence: +24; Unbreakable | In melee, not routing/wobbling → cast on self |
| Ursun's Claw | `wh3_dlc24_weapon_abilities_ursuns_claw` | Armour-Piercing Weapon Damage: +50%; Base Weapon Damage: +50%; Imbuement: Frozen! | In melee, not routing/wobbling → cast on self |
| Ursun's Mighty Roar | `wh3_main_pro_character_abilities_ursuns_roar_2` | Melee Attack: +40 (to self and allies); Leadership: +16 (to self and allies) | In melee, not routing/wobbling → cast on self |
| Ursun's Roar | `wh3_main_character_abilities_ursuns_roar` | Charge Bonus: +36% (to self and allies); Leadership: +8 (to self and allies) | In melee, not routing/wobbling → cast on self |
| Ursun's Roar | `wh3_main_pro_character_abilities_ursuns_roar` | Melee Attack: +40 (to self and allies) | In melee, not routing/wobbling → cast on self |
| Ursun's Roar | `wh3_main_pro_character_abilities_ursuns_roar_1` | Melee Attack: +20 (to self and allies); Leadership: +16 (to self and allies) | In melee, not routing/wobbling → cast on self |
| Ursun's Roar | `wh3_main_pro_character_abilities_ursuns_roar_3` | Melee Attack: +60 (to self and allies); Leadership: +16 (to self and allies) | In melee, not routing/wobbling → cast on self |
| Van Horstmann's Speculum | `wh_main_item_abilities_van_horstmanns_speculum` | Melee Attack: -24 (to enemies in range); Base Weapon Damage: -30% (to enemies in range); Melee Defence: -24 (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Verminous Fury | `wh3_dlc29_lord_abilities_verminous_fury` | Rampage! (to allies in range); Unbreakable (to allies in range); Unyielding Assault (to allies in range) | In melee, not routing/wobbling → cast on self |
| Virulent Contagion | `wh3_main_lord_abilities_virulent_contagion` | Melee Defence: -40 (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Virulent Contagion Upgraded | `wh3_main_lord_abilities_virulent_contagion_upgraded` | Melee Defence: -50 (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Visions of Madness | `wh3_dlc27_qb_unit_abilities_visions_of_madness` | Leadership: -16 (to enemies in range); Rampage! (to enemies in range); Vigour per second: +2.5% (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Void Pendulum | `wh3_main_item_abilities_void_pendulum` | Power Recharge: -40% (to enemies in range); Reserves Per Second: -0.10 (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Vorozheja's Foresight | `wh3_dlc24_hero_abilities_vorozhejas_foresight` | Armour: -12 (to enemies in range); Missile Block Chance: -12 (to enemies in range); Missile Resistance: -10 (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Waaagh! | `wh3_dlc26_unit_abilities_waaagh_in_combat` | Melee Attack: +24; Armour-Piercing Weapon Damage: +25%; Base Weapon Damage: +25%; Immune to Psychology | In melee, not routing/wobbling → cast on self |
| Waaagh! | `wh_main_character_abilities_waaagh` | Speed: +25% (to self and allies); Charge Bonus: +20% (to self and allies); Melee Attack: +20 (to self and allies) | In melee, not routing/wobbling → cast on self |
| Wand of Jet | `wh_main_item_abilities_wand_of_jet` | Power Recharge: +80%; Ability recharge: +15s | In melee, not routing/wobbling → cast on self |
| Warden's Cage | `wh2_dlc15_character_abilities_wardens_cage` | Armour: -60 (to enemies in range); Melee Defence: -48 (to enemies in range); Damage: 20 every 1s (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Warp Frenzy | `wh2_dlc16_hero_abilities_warp_frenzy` | Melee Attack: +24; Armour-Piercing Weapon Damage: +25%; Base Weapon Damage: +25% | In melee, not routing/wobbling → cast on self |
| Warp Gaze | `wh_pro04_unit_abilities_warp_gaze` | enemy speed debuff (hex, under fire) | In melee, not routing/wobbling → cast on self |
| Warpstiletto | `wh3_dlc29_item_abilities_warpstiletto` | enemy speed debuff (hex, under fire) | In melee, not routing/wobbling → cast on self |
| Warpstone Addiction | `wh3_dlc29_lord_abilities_warpstone_addiction` | Damage Resistance: +33 | In melee, not routing/wobbling → cast on self |
| Warpstone Tokens | `wh3_dlc29_item_abilities_warpstone_tokens` | Miscast Chance: -50%; Power Recharge: +80%; Reserves Per Second: +0.50 | In melee, not routing/wobbling → cast on self |
| Warrior Familiar | `wh3_dlc27_item_abilities_warrior_familiar` | Melee Attack: +24; Melee Defence: +24 | In melee, not routing/wobbling → cast on self |
| Warrior's Crest | `wh2_dlc12_lord_abilities_warriors_crest` | Melee Attack: +40; Melee Defence: +24 | In melee, not routing/wobbling → cast on self |
| Watched by the Watcher | `wh3_dlc24_character_abilities_watched_by_the_watcher` | Reveals Unit (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Where You Goin!? | `wh3_dlc26_character_abilities_were_you_goin` | Unbreakable (to allies in range) | In melee, not routing/wobbling → cast on self |
| Whip of Agony | `wh2_twa03_weapon_abilities_whip_of_agony` | Melee Defence: -24 (to enemies in range); Removes Fear (to enemies in range); Removes Terror (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Whip of Misery | `wh2_main_spell_bound_whip_of_agony` | Accuracy: -30 (to enemies in range); Melee Attack: -24 (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Whiplash! | `wh2_dlc14_lord_abilities_whiplash` | Charge Speed: +25% (to allies in range); Charge Bonus: +20% (to allies in range); Armour-Piercing Weapon Damage: +50% (to allies in range); Base Weapon Damage: +50% (to allies in range) | In melee, not routing/wobbling → cast on self |
| Whispering Mist | `wh3_dlc29_hero_abilities_whispering_mist` | Charge Speed: -45% (to enemies in range); Speed: -45% (to enemies in range); Vigour per second: +1% (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Whispering Skull | `wh3_dlc29_item_abilities_whispering_skull` | Miscast Chance: -50%; Spell Mastery: +15%; Power Recharge: +240% | In melee, not routing/wobbling → cast on self |
| Wild Abandon | `wh3_dlc26_lord_abilities_wild_abandon` | Melee Attack: +40 (to self and allies); Melee Defence: -24 (to self and allies); Cannot Die (to self and allies) | In melee, not routing/wobbling → cast on self |
| Willing Prey | `wh3_main_lord_abilities_willing_prey` | Melee Attack: -24 (to enemies in range); Melee Defence: -40 (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Winds of Change | `wh3_main_daemon_body_abilities_winds_of_change` | Miscast Chance: -50%; Power Recharge: +160% | In melee, not routing/wobbling → cast on self |
| Winter’s Chill | `wh3_dlc29_ability_bound_prayer_winters_chill` | Melee Attack: -24 (to enemies in range); Armour-Piercing Weapon Damage: -30% (to enemies in range); Base Weapon Damage: -30% (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Winter’s Chill | `wh3_dlc29_spell_bound_prayer_winters_chill` | Melee Attack: -24 (to enemies in range); Armour-Piercing Weapon Damage: -30% (to enemies in range); Base Weapon Damage: -30% (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Witchbrew | `wh2_main_character_abilities_witchbrew` | Melee Attack: +24; Armour-Piercing Weapon Damage: +50%; Base Weapon Damage: +50%; Rampage! | In melee, not routing/wobbling → cast on self |
| Witchbrew | `wh3_dlc24_unit_abilities_witchbrew` | Melee Attack: +24; Armour-Piercing Weapon Damage: +50%; Base Weapon Damage: +50%; Rampage! | In melee, not routing/wobbling → cast on self |
| Witstealer Sword | `wh3_main_weapon_abilities_witstealer_sword` | Armour-Piercing Weapon Damage: +100%; Base Weapon Damage: +100% | In melee, not routing/wobbling → cast on self |
| Word of Change | `wh3_main_daemon_head_abilities_word_of_change` | Miscast Chance: +100% (to enemies in range); Power Recharge: -80% (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Word of Pain | `wh2_dlc10_spell_bound_word_of_pain` | Accuracy: -30 (to enemies in range); Melee Attack: -40 (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Word of Pain | `wh3_dlc27_spell_dark_magic_word_of_pain_bound_1use` | Accuracy: -30 (to enemies in range); Melee Attack: -40 (to enemies in range) | In melee, not routing/wobbling → cast on self |
| World's Edge Armour | `wh2_main_item_abilities_worlds_edge_armour` | Armour: +60 | In melee, not routing/wobbling → cast on self |
| Woven Mist | `wh_dlc05_unit_abilities_woven_mist` | Melee Defence: -24; Missile Resistance: +40 | In melee, not routing/wobbling → cast on self |
| Wrath of the Storm | `wh3_main_lord_abilities_wrath_of_the_storm` | Melee Attack: +24 (to self and allies); Immune to Psychology (to self and allies); Magical Attacks (to self and allies) | In melee, not routing/wobbling → cast on self |
| Wrathful Reaper | `wh3_main_lord_abilities_wrathful_reaper` | Armour-Piercing Weapon Damage: +50%; Base Weapon Damage: +50%; Rampage! | In melee, not routing/wobbling → cast on self |
| Wristbands of Black Gold | `wh3_dlc29_item_abilities_wristbands_of_black_gold` | Damage Resistance: +20 | In melee, not routing/wobbling → cast on self |
| You're Next! | `wh2_dlc15_lord_abilities_youre_next` | Speed: -45% (to enemies in range); Melee Attack: -24 (to enemies in range); Melee Defence: -40 (to enemies in range) | In melee, not routing/wobbling → cast on self |
| Znarkharja's Ward | `wh3_dlc24_hero_abilities_znarkharjas_ward` | Damage Resistance: +10 (to self and allies) | In melee, not routing/wobbling → cast on self |

### Own health at or below 75%, no melee gate (self)  —  `ushoran_health`  (42 abilities)

Fires when the owner's health is at or below 75% — there is NO melee requirement (heals / defensive buffs). Casts on itself.

| Ability | Key | Effects | Logic |
|---|---|---|---|
| Berry Wine | `wh2_dlc16_item_abilities_berry_wine` | Vigour per second: -10% (to self and allies); Heals: +1.6% per tick (to self and allies) | Own health ≤ 75% → cast on self |
| Blood Chalice | `wh3_dlc29_hero_abilities_blood_chalice` | Heals: +1.6% per tick | Own health ≤ 75% → cast on self |
| Blood Chalice of Bathori | `wh_pro02_item_abilities_blood_chalice_of_bathori` | Vigour per second: -2% (to self and allies); Heals: +1.6% per tick (to self and allies) | Own health ≤ 75% → cast on self |
| Breath of Darkness | `wh3_dlc29_spell_bound_undeath_morkharn_breath_of_darkness` | Vigour per second: -1% (to self and allies); Heals: +0.8% per tick (to self and allies) | Own health ≤ 75% → cast on self |
| Breath of Darkness Upgraded | `wh3_dlc29_spell_bound_undeath_morkharn_breath_of_darkness_upgraded` | Vigour per second: -1% (to self and allies); Heals: +0.8% per tick (to self and allies) | Own health ≤ 75% → cast on self |
| Bugman's XXXXXX | `wh3_dlc26_item_abilities_bugmans_xxxxxx` | Vigour per second: -1%; Heals: +1.7% per tick | Own health ≤ 75% → cast on self |
| Dreaming Ring I | `wh2_dlc16_item_abilities_dreaming_ring_i` | Heals: +0.8% per tick (to self and allies) | Own health ≤ 75% → cast on self |
| Dreaming Ring II | `wh2_dlc16_item_abilities_dreaming_ring_ii` | Heals: +1.6% per tick (to self and allies) | Own health ≤ 75% → cast on self |
| Dreaming Ring III | `wh2_dlc16_item_abilities_dreaming_ring_iii` | Vigour per second: -10% (to self and allies); Heals: +1.6% per tick (to self and allies) | Own health ≤ 75% → cast on self |
| Earth Blood | `wh2_dlc16_spell_bound_earth_blood` | Heals: +0.8% per tick (to self and allies) | Own health ≤ 75% → cast on self |
| Earth Blood | `wh3_main_spell_bound_earth_blood` | Heals: +0.8% per tick (to self and allies) | Own health ≤ 75% → cast on self |
| Elvish Healing Herbs | `wh3_dlc27_unit_abilities_elfish_healing_herbs` | Vigour per second: -1% (to allies in range); Heals: +0.6% per tick (to allies in range) | Own health ≤ 75% → cast on self |
| Fleshy Abundance | `wh3_dlc20_spell_bound_fleshy_abundance` | Heals: +1.6% per tick (to self and allies) | Own health ≤ 75% → cast on self |
| Ghoul King of Ushoran | `wh2_dlc11_lord_abilities_ghoul_king_of_ushoran` | Leadership: +8; Heals: +0.8% per tick | Own health ≤ 75% → cast on self |
| Gulyas | `wh3_dlc24_lord_abilities_gulyas` | Leadership: +4 (to self and allies); Vigour per second: -1% (to self and allies); Heals: +0.08% per tick (to self and allies) | Own health ≤ 75% → cast on self |
| Hieratic Jar | `wh2_dlc09_item_abilities_hieratic_jar` | Heals: +0.8% per tick | Own health ≤ 75% → cast on self |
| Immortal Will | `wh_main_hero_abilities_immortal_will` | Heals: +0.8% per tick | Own health ≤ 75% → cast on self |
| Invocation of Nehek | `wh3_dlc29_spell_bound_invocation_of_nehek` | Heals: +0.8% per tick | Own health ≤ 75% → cast on self |
| Locus of Fecundity | `wh3_main_character_abilities_locus_of_fecundity` | Vigour per second: -1% (to self and allies); Heals: +0.8% per tick (to self and allies) | Own health ≤ 75% → cast on self |
| Makaisson's Persuader | `wh3_dlc25_weapon_abilities_makaissons_persuader` | Heals: +1% per tick (to allies in range); Replenishes ammunition (to allies in range) | Own health ≤ 75% → cast on self |
| Mantra of Invigoration | `wh3_cp1_character_abilities_protection_prayer` | Vigour per second: -1% (to self and allies); Heals: +0.52% per tick (to self and allies) | Own health ≤ 75% → cast on self |
| Meat Feast | `wh3_main_prisoners_butcher` | Vigour per second: -3% (to allies in range); Heals: +2.8% per tick (to allies in range) | Own health ≤ 75% → cast on self |
| Necroparasites | `wh2_dlc16_unit_abilities_neuroparasites` | Heals: +1.6% per tick | Own health ≤ 75% → cast on self |
| Necrotic Phylactery | `wh3_dlc25_item_abilities_necrotic_phylactry` | Spell Resistance: +15 (to self and allies); Immune to Contact Effects (to self and allies) | Own health ≤ 75% → cast on self |
| Patch Up | `wh2_dlc13_character_abilities_patch_up` | Heals: +1.6% per tick (to allies in range) | Own health ≤ 75% → cast on self |
| Pestilent Regeneration | `wh3_main_daemon_head_abilities_pestilent_regeneration` | Heals: +0.4% per tick | Own health ≤ 75% → cast on self |
| Potion of Charoi | `wh2_main_lord_abilities_potion_of_charoi` | Damage Resistance: +40; Heals: +0.8% per tick; Ability recharge: +30s | Own health ≤ 75% → cast on self |
| Potion of Healing | `wh_main_item_abilities_potion_of_healing` | Heals: +0.8% per tick | Own health ≤ 75% → cast on self |
| Radiant Gem of Hoeth | `wh2_main_spell_bound_radiant_gem_of_hoeth` | Heals: +0.8% per tick (to self and allies) | Own health ≤ 75% → cast on self |
| Reforge | `wh3_dlc23_character_abilities_reforge` | Heals: +0.8% per tick (to allies in range) | Own health ≤ 75% → cast on self |
| Regenerating Flesh | `wh_main_item_abilities_regenerating_flesh` | Heals: +0.8% per tick | Own health ≤ 75% → cast on self |
| Regrowth | `wh2_dlc16_spell_bound_regrowth` | Vigour per second: -1% (to self and allies); Heals: +0.8% per tick (to self and allies) | Own health ≤ 75% → cast on self |
| Remouldered | `wh2_dlc16_lord_abilities_remouldered` | Melee Attack: +24 (to self and allies); Leadership: +8 (to self and allies); Heals: +0.5% per tick (to self and allies) | Own health ≤ 75% → cast on self |
| Restore | `wh2_dlc09_character_abilities_restore` | Heals: +0.8% per tick (to allies in range) | Own health ≤ 75% → cast on self |
| Revivification Crystal | `wh2_main_unit_abilities_revivification_crystal` | Heals: +0.5% per tick (to self and allies) | Own health ≤ 75% → cast on self |
| Saint Annushka's Finger Bone | `wh3_main_item_abilities_saint_annushkas_finger_bone` | Heals: +0.2% per tick (to self and allies) | Own health ≤ 75% → cast on self |
| Salyak's Lullaby | `wh3_main_character_abilities_salyaks_lullaby` | Heals: +0.8% per tick (to self and allies) | Own health ≤ 75% → cast on self |
| Scroll of Power | `wh_main_item_abilities_scroll_of_power` | Ability recharge: -60s (to self and allies) | Own health ≤ 75% → cast on self |
| Skalm | `wh2_main_item_abilities_skalm` | Heals: +0.8% per tick | Own health ≤ 75% → cast on self |
| Skar's Kraken-Killer | `wh3_main_weapon_abilities_skars_kraken_killer` | Invulnerable; Vigour per second: -2%; Heals: +1.6% per tick | Own health ≤ 75% → cast on self |
| Star of Avelorn | `wh2_dlc10_item_abilities_star_of_avelorn` | Heals: +0.8% per tick (to self and allies) | Own health ≤ 75% → cast on self |
| Trollguts | `wh3_dlc26_spell_bound_trollguts` | Heals: +0.8% per tick (to self and allies) | Own health ≤ 75% → cast on self |

### Charge window OR melee (self)  —  `charge_or_melee`  (31 abilities)

Fires in the split second of the charge window OR once the unit is already in melee (the two arms exclude each other). Casts on itself.

| Ability | Key | Effects | Logic |
|---|---|---|---|
| Birona's Timewarp | `wh_main_spell_bound_bironas_timewarp` | Charge Speed: +25% (to self and allies); Speed: +25% (to self and allies); Melee Attack: +24 (to self and allies) | Charging OR in melee → cast on self |
| Bloodthirst | `wh3_main_lord_abilities_bloodthirst` | Charge Speed: +25%; Speed: +25%; Charge Bonus: +40% | Charging OR in melee → cast on self |
| Cash Cascade | `wh3_dlc26_character_abilities_cash_cascade` | Charge Bonus: +25% (to self and allies); Melee Attack: +24 (to self and allies); Leadership: +8 (to self and allies) | Charging OR in melee → cast on self |
| Colossal Strike | `wh3_dlc24_character_abilities_colossal_strike` | Bonus vs. Large: +16; Armour-Piercing Weapon Damage: +25%; Base Weapon Damage: +25%; Immune to Psychology | Charging OR in melee → cast on self |
| Colossal Strike | `wh3_dlc24_character_abilities_colossal_strike_summoned` | Bonus vs. Large: +16; Armour-Piercing Weapon Damage: +25%; Base Weapon Damage: +25%; Immune to Psychology | Charging OR in melee → cast on self |
| Crimson Juggernaut | `wh3_dlc26_character_abilities_crimson_juggernaut` | Charge Speed: +50%; Speed: +25%; Charge Bonus: +40%; Glorious Charge | Charging OR in melee → cast on self |
| Daemonic Onslaught | `wh3_main_daemon_legs_abilities_daemonic_onslaught` | Charge Bonus: +60%; Armour-Piercing Weapon Damage: +25%; Base Weapon Damage: +25% | Charging OR in melee → cast on self |
| Deadly Onslaught | `wh_dlc03_character_abilities_deadly_onslaught` | Charge Bonus: +60%; Armour-Piercing Weapon Damage: +25%; Base Weapon Damage: +25% | Charging OR in melee → cast on self |
| Fangspike | `wh3_dlc26_weapon_abilities_fangspike` | Charge Bonus: +40%; Armour-Piercing Weapon Damage: +50%; Base Weapon Damage: +50% | Charging OR in melee → cast on self |
| Full Power! | `wh3_dlc25_unit_abilities_full_power` | Acceleration: +100%; Turn Speed: -70%; Speed: +50% | Charging OR in melee → cast on self |
| Fury of Khaine | `wh2_main_unit_abilities_fury_of_khaine` | Melee Attack: +24 (to allies in range); Armour-Piercing Weapon Damage: +50% (to allies in range); Base Weapon Damage: +50% (to allies in range); Rampage! (to allies in range) | Charging OR in melee → cast on self |
| Guiding Strike | `wh3_cp1_lord_abilities_guiding_strike` | Melee Attack: +24; Imbuement: Weakened | Charging OR in melee → cast on self |
| Heart Piercing | `wh2_dlc11_lord_abilities_heart_piercing` | Charge Bonus: +40%; Armour-Piercing Weapon Damage: +50%; Imbuement: Sundered Armour | Charging OR in melee → cast on self |
| Horn of the First Beast | `wh_dlc03_item_abilities_horn_of_the_first_beast` | Charge Bonus: +20% (to self and allies); Melee Attack: +24 (to self and allies); Leadership: +8 (to self and allies) | Charging OR in melee → cast on self |
| Inspired Assault I | `wh3_main_lord_abilities_inspired_assault_i` | Charge Bonus: +20% (to allies in range); Melee Attack: +24 (to allies in range) | Charging OR in melee → cast on self |
| Inspired Assault II | `wh3_main_lord_abilities_inspired_assault_ii` | Charge Bonus: +40% (to allies in range); Melee Attack: +24 (to allies in range) | Charging OR in melee → cast on self |
| Inspired Assault III | `wh3_main_lord_abilities_inspired_assault_iii` | Charge Bonus: +40% (to allies in range); Melee Attack: +40 (to allies in range) | Charging OR in melee → cast on self |
| Locus of Fury | `wh3_main_character_abilities_locus_of_fury` | Charge Bonus: +40% (to self and allies); Armour-Piercing Weapon Damage: +25% (to self and allies); Base Weapon Damage: +25% (to self and allies) | Charging OR in melee → cast on self |
| Locus of Swiftness | `wh3_main_character_abilities_locus_of_swiftness` | Charge Speed: +25% (to self and allies); Speed: +25% (to self and allies); Charge Bonus: +40% (to self and allies) | Charging OR in melee → cast on self |
| Masterful Strike | `wh3_cp1_lord_abilities_mastered_strike` | Bonus vs. Large: +16; Melee Attack: +26; Armour-Piercing Weapon Damage: +25%; Base Weapon Damage: +25%; Imbuement: Weakened | Charging OR in melee → cast on self |
| More Power! | `wh3_dlc23_unit_abilities_more_power` | Acceleration: +200%; Speed: +25%; Mass: +50% | Charging OR in melee → cast on self |
| Morglor the Mangler | `wh3_dlc26_weapon_abilities_morglor_the_mangler` | Charge Speed: +25%; Charge Bonus: +20%; Armour-Piercing Weapon Damage: +75%; Base Weapon Damage: +75% | Charging OR in melee → cast on self |
| Purge the Weak! | `wh3_main_daemon_wings_abilities_purge_the_weak` | Speed: +30%; Leadership: +6; Vigour per second: -2% | Charging OR in melee → cast on self |
| Shield of Thorns | `wh2_dlc17_spell_bound_shield_of_thorns` | Melee Damage Reflection: +20 (to self and allies) | Charging OR in melee → cast on self |
| Shield of Thorns | `wh_dlc05_spell_bound_shield_of_thorns` | Melee Damage Reflection: +20 (to self and allies) | Charging OR in melee → cast on self |
| Star Lance | `wh2_dlc15_weapon_abilities_star_lance` | Charge Speed: +20%; Charge Bonus: +60%; Armour-Piercing Weapon Damage: +25%; Flaming Attacks; Imbuement: Flammable! | Charging OR in melee → cast on self |
| Storm Hammer | `wh3_dlc29_spell_bound_storm_hammer` | Charge Bonus: +40%; Melee Attack: +40; Imbuement: Dazed! | Charging OR in melee → cast on self |
| Storm Rage | `wh3_dlc20_unit_abilities_storm_rage` | Charge Bonus: +20%; Melee Attack: +24; Armour-Piercing Weapon Damage: +25%; Base Weapon Damage: +25% | Charging OR in melee → cast on self |
| Stormlance | `wh3_dlc25_item_abilities_stormlance` | Charge Bonus: +40%; Armour-Piercing Weapon Damage: +75%; Base Weapon Damage: +75%; Flaming Attacks | Charging OR in melee → cast on self |
| Tempest Rage | `wh3_dlc20_lord_abilities_tempest_rage` | Charge Bonus: +20% (to self and allies); Melee Attack: +24 (to self and allies); Armour-Piercing Weapon Damage: +25% (to self and allies); Base Weapon Damage: +25% (to self and allies) | Charging OR in melee → cast on self |
| The Horn of Kygor | `wh2_main_item_abilities_the_horn_of_kygor` | Charge Bonus: +20% (to self and allies); Melee Attack: +24 (to self and allies); Leadership: +8 (to self and allies) | Charging OR in melee → cast on self |

### Owner in melee OR a friendly unit in range in melee (self)  —  `metallurgy_melee`  (8 abilities)

Fires when the owner is in melee OR a friendly unit other than the caster is in melee within the conservative 25 m check; casts on itself.

| Ability | Key | Effects | Logic |
|---|---|---|---|
| Enchanted Metallurgy | `wh3_main_character_abilities_enchanted_metallurgy` | Base Missile Damage: +25% (to self and allies); Base Weapon Damage: +30% (to self and allies); Magical Attacks (to self and allies) | Owner or a friendly unit in range in melee → cast on self |
| Enchanted Metallurgy: Flaming | `wh3_main_character_abilities_enchanted_metallurgy_flaming` | Base Missile Damage: +50% (to self and allies); Base Weapon Damage: +60% (to self and allies); Magical Attacks (to self and allies); Flaming Attacks (to self and allies) | Owner or a friendly unit in range in melee → cast on self |
| Enchanted Metallurgy: Piercing | `wh3_main_character_abilities_enchanted_metallurgy_piercing` | Armour-Piercing Missile Damage: +25% (to self and allies); Base Missile Damage: +25% (to self and allies); Armour-Piercing Weapon Damage: +25% (to self and allies); Base Weapon Damage: +25% (to self and allies); Magical Attacks (to self and allies) | Owner or a friendly unit in range in melee → cast on self |
| Enchanted Metallurgy: Poison | `wh3_main_character_abilities_enchanted_metallurgy_poison` | Base Missile Damage: +25% (to self and allies); Base Weapon Damage: +30% (to self and allies); Magical Attacks (to self and allies); Imbuement: Poison! (to self and allies) | Owner or a friendly unit in range in melee → cast on self |
| Master of Alchemy | `wh3_main_lord_abilities_master_of_alchemy` | Base Missile Damage: +25% (to self and allies); Base Weapon Damage: +30% (to self and allies); Magical Attacks (to self and allies) | Owner or a friendly unit in range in melee → cast on self |
| Master of Alchemy: Flaming | `wh3_main_lord_abilities_master_of_alchemy_flaming` | Base Missile Damage: +50% (to self and allies); Base Weapon Damage: +60% (to self and allies); Magical Attacks (to self and allies); Flaming Attacks (to self and allies) | Owner or a friendly unit in range in melee → cast on self |
| Master of Alchemy: Piercing | `wh3_main_lord_abilities_master_of_alchemy_piercing` | Armour-Piercing Missile Damage: +25% (to self and allies); Base Missile Damage: +25% (to self and allies); Armour-Piercing Weapon Damage: +25% (to self and allies); Base Weapon Damage: +25% (to self and allies); Magical Attacks (to self and allies) | Owner or a friendly unit in range in melee → cast on self |
| Master of Alchemy: Poison | `wh3_main_lord_abilities_master_of_alchemy_poison` | Base Missile Damage: +25% (to self and allies); Base Weapon Damage: +30% (to self and allies); Magical Attacks (to self and allies); Imbuement: Poison! (to self and allies) | Owner or a friendly unit in range in melee → cast on self |

### Fatigue — Tired or worse (self)  —  `tired`  (5 abilities)

Fires when the unit's fatigue state is Tired or worse (tired / very tired / exhausted); winded and above hold it back. Casts on itself.

| Ability | Key | Effects | Logic |
|---|---|---|---|
| Dazh's Song of Winter Sunlight | `wh3_main_character_abilities_dazs_song_of_winter_sunlight` | Vigour per second: -100% (to self and allies) | Fatigue Tired or worse → cast on self |
| Dazh's Song of Winter Sunlight | `wh3_twa06_unit_abilities_dazs_song_of_winter_sunlight` | Vigour per second: -100% (to self and allies) | Fatigue Tired or worse → cast on self |
| Foe-Seeker | `wh_dlc03_character_abilities_foe_seeker` | Charge Speed: +25%; Speed: +25%; Vigour per second: -1% | Fatigue Tired or worse → cast on self |
| Foe-Seeker | `wh_main_character_abilities_foe_seeker` | Charge Speed: +25%; Speed: +25%; Vigour per second: -1% | Fatigue Tired or worse → cast on self |
| Foe-Seeker | `wh_main_character_abilities_foe_seeker_summoned` | Charge Speed: +25%; Speed: +25%; Vigour per second: -1% | Fatigue Tired or worse → cast on self |

### Owner wavering (self)  —  `wavering_self`  (3 abilities)

Fires only while the owner is wavering; casts on itself.

| Ability | Key | Effects | Logic |
|---|---|---|---|
| Ferocious Fury of Ulric | `wh3_dlc29_spell_bound_prayer_ferocious_fury_of_ulric` | Can Cause Fear (to self and allies); Unbreakable (to self and allies) | Owner wavering → cast on self |
| Helm of Yvresse | `wh2_dlc15_item_abilities_helm_of_yvresse` | Cannot Die (to self and allies); Unbreakable (to self and allies) | Owner wavering → cast on self |
| Vial of Troll Blood | `wh_dlc08_item_abilities_vial_of_troll_blood` | Unbreakable (to self and allies) | Owner wavering → cast on self |

### Melee — plain in-melee (self)  —  `melee`  (2 abilities)

Fires whenever the engine says the unit is in melee. Casts on itself.

| Ability | Key | Effects | Logic |
|---|---|---|---|
| Grand Hammer of Sigmar | `wh_dlc04_spell_bound_hammer_of_sigmar_upgraded` | Melee Attack: +24 (to self and allies) | In melee → cast on self |
| Hammer of Sigmar | `wh_main_spell_bound_hammer_of_sigmar` | Melee Attack: +24 (to self and allies) | In melee → cast on self |

### Melee AND own health at or below 75% (self)  —  `melee_health75`  (2 abilities)

Fires when the owner is in melee AND at or below 75% health (used where the ability also grants a melee-relevant effect). Casts on itself.

| Ability | Key | Effects | Logic |
|---|---|---|---|
| Captain of the Phoenix Guard | `wh3_dlc27_character_abilities_captain_of_the_phoenix_guard` | Physical Resistance: +30 (to allies in range); Heals: +0.5% per tick (to allies in range) | In melee AND health ≤ 75% → cast on self |
| Potion of Toughness | `wh_main_item_abilities_potion_of_toughness` | Armour: +30; Melee Defence: +24; Heals: +0.8% per tick | In melee AND health ≤ 75% → cast on self |

### Melee + low morale (self)  —  `melee_low_morale`  (2 abilities)

Fires when the unit is in melee AND its morale is at or below the wavering threshold (fails open to the plain in-melee condition if morale can't be read). Casts on itself.

| Ability | Key | Effects | Logic |
|---|---|---|---|
| Stand Your Ground! | `wh_main_character_abilities_stand_your_ground` | Melee Defence: +24 (to self and allies); Leadership: +16 (to self and allies) | In melee with morale at/below wavering → cast on self |
| Tacticians, Stand Your Ground! | `wh3_dlc24_character_abilities_tacticians_stand_your_ground` | Melee Defence: +24 (to self and allies); Leadership: +16 (to self and allies) | In melee with morale at/below wavering → cast on self |

### Owner OR an in-melee ally in range wavering (self)  —  `wavering_self_or_ally`  (2 abilities)

Fires when the owner is wavering OR an in-melee ally within range is wavering (conservative 25 m check), casts on itself.

| Ability | Key | Effects | Logic |
|---|---|---|---|
| Commanding Presence | `wh3_dlc29_lord_active_commanding_presence` | Leadership: +8 (to self and allies); Immune to Psychology (to self and allies) | Owner or an in-melee wavering ally in range → cast on self |
| Fury of Ulric | `wh3_dlc29_spell_bound_prayer_fury_of_ulric` | Leadership: +8 (to self and allies); Can Cause Fear (to self and allies) | Owner or an in-melee wavering ally in range → cast on self |

### Barrier broken (self)  —  `barrier_broken`  (1 abilities)

Fires when the unit's barrier / missile ward is broken. Casts on itself.

| Ability | Key | Effects | Logic |
|---|---|---|---|
| Eagle-Feather Torc | `wh3_dlc27_item_abilities_eagle_feather_torc` | Restores barrier | Barrier broken → cast on self |

### Custom — health-based ally heal at a cost  —  `blood_sacrifice`  (1 abilities)

Custom health trigger: when the owner's health is at or below 75%, heals the lowest-health ally in range at a cost. Casts on that ally.

| Ability | Key | Effects | Logic |
|---|---|---|---|
| Blood Sacrifice | `wh3_dlc26_lord_abilities_blood_sacrifice` | Heals: +1% per tick (to allies in range); Damage: 144 every 1s | Health ≤ 75% → heal lowest-health ally in range (cost) |

### Charge window OR melee (self)  —  `charge`  (1 abilities)

Fires in the split second of the charge window OR once the unit is already in melee (the two arms exclude each other). Casts on itself.

| Ability | Key | Effects | Logic |
|---|---|---|---|
| Deadly Onslaught | `wh_main_character_abilities_deadly_onslaught` | Charge Bonus: +60%; Armour-Piercing Weapon Damage: +25%; Base Weapon Damage: +25% | Charging OR in melee → cast on self |

### Charge window only (self)  —  `charge_only`  (1 abilities)

Fires only in the split second of the charge window (no melee arm). Casts on itself.

| Ability | Key | Effects | Logic |
|---|---|---|---|
| Ferocious Battle Howl | `wh3_dlc29_spell_bound_prayer_ferocious_battle_howl` | Charge Speed: +50% (to self and allies); Speed: +25% (to self and allies); Charge Bonus: +40% (to self and allies); Mass: +50% (to self and allies) | Charging (window only) → cast on self |

### Charge window OR wavering (self)  —  `charge_or_wavering`  (1 abilities)

Fires in the charge window OR while the unit is wavering. Casts on itself.

| Ability | Key | Effects | Logic |
|---|---|---|---|
| Bangers & Smash | `wh2_dlc15_character_abilities_sausage_busta` | Charge Bonus: +20% (to self and allies); Leadership: +12 (to self and allies) | Charging OR wavering → cast on self |

### Custom — health-based self/ally heal at a cost  —  `eat_da_runts`  (1 abilities)

Custom health trigger: when the owner's health is at or below 75%, heals self or the nearest ally at a cost.

| Ability | Key | Effects | Logic |
|---|---|---|---|
| Eat da Runts! | `wh3_dlc26_unit_abilities_eat_da_runts` | Damage: 144 every 1s (to allies in range); Vigour per second: -1.5%; Heals: +1.5% per tick | Health ≤ 75% → heal self / nearest ally (cost) |

### A Slayer ally in melee (Slayer-only, self/ally)  —  `glorious_death`  (1 abilities)

Fires when a Slayer unit is in melee: the lowest-health Slayer ally is preferred; otherwise the owner casts on self only if the owner is itself a Slayer and in melee. A non-Slayer ally is never targeted.

| Ability | Key | Effects | Logic |
|---|---|---|---|
| Glorious Death | `wh3_dlc25_lord_abilities_glorious_death` | Cannot Die (to self and allies) | A Slayer ally in melee (or owner is a Slayer in melee) → cast on the Slayer |

### An ally in range is in melee AND wavering (self)  —  `verminking_wavering`  (1 abilities)

Fires when an ally within range is in melee and wavering; casts on itself.

| Ability | Key | Effects | Logic |
|---|---|---|---|
| Will of the Verminking | `wh3_dlc29_lord_abilities_will_of_the_verminking` | Unbreakable (to allies in range); Leadership: -16 (to enemies in range) | An in-melee wavering ally in range → cast on self |

### A wavering ally in range, no melee gate (ally)  —  `wavering_ally_range`  (1 abilities)

Fires when a wavering ally is within range — the owner need not be wavering and the ally need not be in melee. Casts on that ally.

| Ability | Key | Effects | Logic |
|---|---|---|---|
| "Stay Here, I'll Get Help!" | `wh2_dlc09_character_abilities_stay_here_ill_get_help` | Leadership: +16 (to allies in range); Stalk; Unspottable | A wavering ally in range → cast on that ally |

---

## Section 3 — EXCLUDED ABILITIES (grouped by reason family)

No automatic logic. The reason is stated once per group; each member follows.

### Spell / Winds-of-Magic / Cataclysm ability  (434 abilities)

Out of scope by the user's earlier standing decision (tracker §3c).

| Ability | Key | Effects |
|---|---|---|
| 'Eadbutt | `wh_main_spell_big_waaagh_eadbutt` | Short, wide, expanding, tear-shaped attack; Strong vs a single unit |
| 'Eadbutt Upgraded | `wh_main_spell_big_waaagh_eadbutt_upgraded` | Increased damage; Short, wide, expanding, tear-shaped attack; Strong vs a single unit |
| 'Ere We Go | `wh_main_spell_big_waaagh_ere_we_go` | Melee Attack: +40 (to self and allies) |
| Acquiescence | `wh3_main_spell_slaanesh_acquiescence` | Speed: -25% (to enemies in range); Melee Defence: -24 (to enemies in range) |
| Acquiescence Upgraded | `wh3_main_spell_slaanesh_acquiescence_upgraded` | Speed: -45% (to enemies in range); Melee Defence: -24 (to enemies in range) |
| Ancestral Warriors | `wh3_main_spell_yin_ancestral_warriors` | Summons a unit of Ancestral Warriors; Summoned units degrade over time |
| Ancestral Warriors Upgraded | `wh3_main_spell_yin_ancestral_warriors_upgraded` | Extended cast range; Summons a unit of Ancestral Warriors; Summoned units degrade over time |
| Apotheosis | `wh2_main_spell_high_magic_apotheosis` | Can Cause Fear (to self and allies); Heals: +0.8% per tick (to self and allies) |
| Apotheosis Upgraded | `wh2_main_spell_high_magic_apotheosis_upgraded` | Can Cause Fear (to self and allies); Heals: +0.8% per tick (to self and allies) |
| Arcane Unforging | `wh2_main_spell_high_magic_arcane_unforging` | Damage: 67 every 1s (to enemies in range); Ability recharge: +30s (to enemies in range) |
| Arcane Unforging Upgraded | `wh2_main_spell_high_magic_arcane_unforging_upgraded` | Damage: 67 every 1s (to enemies in range); Ability recharge: +45s (to enemies in range) |
| Armour of Darkness | `wh2_dlc14_spell_stealth_armour_of_darkness` | Armour: +60 (to self and allies); Missile Resistance: +20 (to self and allies) |
| Armour of Darkness Upgraded | `wh2_dlc14_spell_stealth_armour_of_darkness_upgraded` | Armour: +60 (to self and allies); Missile Resistance: +20 (to self and allies) |
| Ash Storm | `wh3_dlc23_spell_hashut_ash_storm` | Speed: -25% (to enemies in range); Weakness to Fire Damage: -20 (to enemies in range) |
| Ash Storm Upgraded | `wh3_dlc23_spell_hashut_ash_storm_upgraded` | Speed: -25% (to enemies in range); Weakness to Fire Damage: -20 (to enemies in range) |
| Ashes & Dust | `wh3_dlc25_cataclysm_death_ashes_and_dust_com` | Damage: 25 every 1s (to enemies in range); Damage: 500 every 1s (to enemies in range) |
| Ashes & Dust | `wh3_main_cataclysm_death_ashes_and_dust` | Damage: 25 every 1s (to enemies in range); Damage: 500 every 1s (to enemies in range) |
| Aspect of the Dread Knight | `wh_dlc08_spell_death_aspect_of_the_dreadknight_arzik` | Leadership: +8 (to self and allies); Can Cause Fear (to self and allies); Can Cause Terror (to self and allies); Magical Attacks (to self and allies) |
| Aspect of the Dread Knight | `wh_main_spell_death_aspect_of_the_dreadknight` | Leadership: +8 (to self and allies); Can Cause Fear (to self and allies); Can Cause Terror (to self and allies); Magical Attacks (to self and allies) |
| Aspect of the Dread Knight Upgraded | `wh_main_spell_death_aspect_of_the_dreadknight_upgraded` | Leadership: +8 (to self and allies); Can Cause Fear (to self and allies); Can Cause Terror (to self and allies); Magical Attacks (to self and allies) |
| Awaken from the Grave | `wh_dlc04_spell_vampires_raise_dead_helman` | Summons a unit of Grave Guard; Good at melee combat; Summoned units degrade over time |
| Awaken from the Grave Upgraded | `wh_dlc04_spell_vampires_raise_dead_upgraded_helman` | Summons a Wight King; Good at melee combat; Summoned units degrade over time |
| Awakening of the Wood | `wh_dlc05_spell_life_awakening_of_the_wood` | Speed: -45% |
| Awakening of the Wood | `wh_dlc05_spell_life_awakening_the_wood_branchwraith` | Large explosion area |
| Banishment | `wh_main_spell_light_banishment` | Huge, randomly-moving area of effect; Good against armour; Strong vs multiple units |
| Banishment Upgraded | `wh_main_spell_light_banishment_upgraded` | Increased damage; Huge, randomly-moving area of effect; Good against armour; Strong vs multiple units |
| Birona's Timewarp | `wh_main_spell_light_bironas_timewarp` | Charge Speed: +25% (to self and allies); Speed: +25% (to self and allies); Melee Attack: +24 (to self and allies) |
| Birona's Timewarp Upgraded | `wh_main_spell_light_bironas_timewarp_upgraded` | Charge Speed: +25% (to self and allies); Speed: +25% (to self and allies); Melee Attack: +24 (to self and allies) |
| Biting Wind | `wh3_main_spell_tempest_biting_wind` | Expanding, forward-moving area of effect |
| Biting Wind | `wh3_main_spell_tempest_biting_wind_army` | Expanding, forward-moving area of effect |
| Biting Wind Upgraded | `wh3_main_spell_tempest_biting_wind_upgraded` | Increased armour-piercing damage; Expanding, forward-moving area of effect |
| Black Whirlwind | `wh2_dlc14_spell_stealth_black_whirlwind` | Huge, stationary area of effect; Good against armour; Strong vs multiple units |
| Black Whirlwind Upgraded | `wh2_dlc14_spell_stealth_black_whirlwind_upgraded` | Huge, stationary area of effect; Good against armour; Strong vs multiple units |
| Bladewind | `wh2_main_spell_dark_magic_bladewind` | Large, randomly-moving area of effect; Strong vs multiple units |
| Bladewind Upgraded | `wh2_main_spell_dark_magic_bladewind_upgraded` | Extended effect duration; Large, randomly-moving area of effect; Strong vs multiple units |
| Bless with Filth | `wh2_main_spell_plague_bless_with_filth` | Imbuement: Poison! (to self and allies) |
| Bless with Filth Upgraded | `wh2_main_spell_plague_bless_with_filth_upgraded` | Imbuement: Poison! (to self and allies) |
| Blessed Cauldron | `wh3_dlc24_spell_hags_cursed_cauldron_upgraded` | Spell cannot harm friendly troops; Causes major magical damage; Medium strike area; Good against armour; Strong vs a single unit |
| Blessing of the Ancient Witch | `wh3_dlc24_spell_hags_curse_of_the_ancient_witch_upgraded` | Armour-Piercing Missile Damage: +25% (to self and allies); Base Missile Damage: +25% (to self and allies); Reload Skill: +20 (to self and allies); Magical Attacks (to self and allies) |
| Blight Boil | `wh3_main_spell_nurgle_pestilent_pustule` | Huge explosion area |
| Blight Boil Upgraded | `wh3_main_spell_nurgle_pestilent_pustule_upgraded` | Increased explosion damage; Huge explosion area |
| Blizzard | `wh3_main_spell_tempest_blizzard` | Large explosion area |
| Blizzard Upgraded | `wh3_main_spell_tempest_blizzard_upgraded` | Increased armour-piercing damage; Increased damage; Large explosion area |
| Blossom Wind | `wh3_main_spell_yin_blossom_wind` | Medium, forward-moving area of effect |
| Blossom Wind Upgraded | `wh3_main_spell_yin_blossom_wind_upgraded` | Increased armour-piercing damage; Medium, forward-moving area of effect |
| Blue Fire of Tzeentch | `wh3_main_spell_tzeentch_blue_fire_of_tzeentch` | Good against large combatants; Poor penetration; Requires line of sight to the target |
| Blue Fire of Tzeentch Upgraded | `wh3_main_spell_tzeentch_blue_fire_of_tzeentch_upgraded` | Increased armour-piercing damage; Good against large combatants; Poor penetration; Requires line of sight to the target |
| Bonecrusher | `wh3_main_spell_great_maw_bonecrusher` | Small strike area |
| Bonecrusher Upgraded | `wh3_main_spell_great_maw_bonecrusher_upgraded` | Greater armour-piercing explosion damage; Small strike area |
| Brain Bursta | `wh_main_spell_big_waaagh_brain_bursta` | Large explosion area; Strong vs a single unit; Weak vs a single combatant |
| Brain Bursta Upgraded | `wh_main_spell_big_waaagh_brain_bursta_upgraded` | Greater armour-piercing explosion damage; Large explosion area; Strong vs a single unit; Weak vs a single combatant |
| Braingobbler | `wh3_main_spell_great_maw_braingobbler` | Leadership: -16 (to enemies in range) |
| Braingobbler Upgraded | `wh3_main_spell_great_maw_braingobbler_upgraded` | Leadership: -16 (to enemies in range) |
| Bray-Scream | `wh_dlc03_spell_wild_bray_scream` | Short, wide, expanding, tear-shaped attack; Good against armour; Strong vs multiple units; Weak vs a single combatant |
| Bray-Scream Upgraded | `wh_dlc03_spell_wild_bray_scream_upgraded` | Extended cast range; Increased damage; Short, wide, expanding, tear-shaped attack; Strong vs multiple units; Weak vs a single combatant |
| Breath of Darkness | `wh3_dlc29_spell_undeath_morkharn_breath_of_darkness` | Vigour per second: -1% (to self and allies); Heals: +0.8% per tick (to self and allies) |
| Breath of Darkness Upgraded | `wh3_dlc29_spell_undeath_morkharn_breath_of_darkness_upgraded` | Vigour per second: -1% (to self and allies); Heals: +0.8% per tick (to self and allies) |
| Brittle Bone | `wh2_dlc14_spell_stealth_brittle_bone` | Speed: -25% (to enemies in range); Melee Defence: -40 (to enemies in range); Vigour per second: +1% (to enemies in range) |
| Brittle Bone Upgrade | `wh2_dlc14_spell_stealth_brittle_bone_upgraded` | Speed: -25% (to enemies in range); Melee Defence: -40 (to enemies in range); Vigour per second: +1% (to enemies in range) |
| Bullgorger | `wh3_main_spell_great_maw_bullgorger` | Melee Attack: +24 (to self and allies); Armour-Piercing Weapon Damage: +25% (to self and allies) |
| Bullgorger Upgraded | `wh3_main_spell_great_maw_bullgorger_upgraded` | Melee Attack: +24 (to self and allies); Armour-Piercing Weapon Damage: +25% (to self and allies) |
| Burning Wrath | `wh3_dlc23_spell_hashut_burning_wrath` | Causes moderate magical & fire damage; Spawns a moving area of effect; Strong vs multiple combatants; Effective at long range; Requires line of sight to the target |
| Burning Wrath Upgraded | `wh3_dlc23_spell_hashut_burning_wrath_upgraded` | Spawns additional areas of effect; Causes moderate magical & fire damage; Spawns three moving areas of effect; Strong vs multiple combatants; Effective at long range; Requires line of sight to the target |
| Cascading Fire Cloak | `wh_main_spell_fire_cascading_fire_cloak` | Armour-Piercing Weapon Damage: +25% (to self and allies); Melee Defence: +24 (to self and allies) |
| Chain Lightning | `wh2_dlc15_spell_bound_chain_lightning` | Large, randomly-moving area of effect; Good against armour; Strong vs multiple units; Weak vs a single combatant |
| Chain Lightning | `wh3_dlc27_spell_heavens_chain_lightning` | Damage: 4 every 1s (to enemies in range) |
| Chain Lightning | `wh_main_spell_heavens_chain_lightning` | Large, randomly-moving area of effect; Good against armour; Strong vs multiple units; Weak vs a single combatant |
| Chillwind | `wh2_main_spell_dark_magic_chillwind` | Speed: -25% |
| Chillwind | `wh3_dlc27_spell_dark_magic_chillwind_bound` | Small, forward-moving area of effect; Good against armour; Strong vs multiple units |
| Chillwind Upgraded | `wh2_main_spell_dark_magic_chillwind_upgraded` | Speed: -45%; Reload Skill: -20 |
| Cloak of Jet | `wh3_main_spell_yin_cloak_of_jet` | Snipe (to self and allies); Stalk (to self and allies); Unspottable (to self and allies) |
| Cloak of Jet Upgraded | `wh3_main_spell_yin_cloak_of_jet_upgraded` | Snipe (to self and allies); Stalk (to self and allies); Unspottable (to self and allies) |
| Comet of Casandora | `wh2_dlc17_spell_heavens_comet_of_casandora_bound_skink_oracle` | Causes massive magical damage; Huge explosion area; Large strike area; Good against armour; Strong vs multiple units; Causes damage to self |
| Comet of Casandora | `wh_main_spell_heavens_comet_of_casandora` | Causes massive magical damage; Huge explosion area; Large strike area; Good against armour; Strong vs multiple units |
| Comet of Casandora | `wh_main_spell_heavens_comet_of_casandora_summoned` | Spell / Winds-of-Magic / Cataclysm ability. |
| Comet of Casandora Upgraded | `wh_main_spell_heavens_comet_of_casandora_upgraded` | Greater armour-piercing explosion damage; Causes massive magical damage; Huge explosion area; Large strike area; Good against armour; Strong vs multiple units |
| Command of the Unliving | `wh_dlc04_spell_vampires_raise_dead_strigoi` | Summons a unit of Crypt Ghouls; Good at flanking enemies; Summoned units degrade over time |
| Command of the Unliving Upgraded | `wh_dlc04_spell_vampires_raise_dead_upgraded_strigoi` | Summons a unit of Crypt Horrors; Good at flanking enemies; Summoned units degrade over time |
| Constellation of the Dragon | `wh3_main_spell_yang_constellation_of_the_dragon` | Spell / Winds-of-Magic / Cataclysm ability. |
| Constellation of the Dragon Upgraded | `wh3_main_spell_yang_constellation_of_the_dragon_upgraded` | Greater armour-piercing explosion damage; Increased damage |
| Crack's Call | `wh2_main_spell_ruin_cracks_call` | Medium, forward-moving area of effect; Good against armour; Strong vs multiple units; Weak vs a single combatant |
| Crack's Call Upgraded | `wh2_main_spell_ruin_cracks_call_upgraded` | Increased damage; Medium, forward-moving area of effect; Strong vs multiple units; Weak vs a single combatant |
| Crystal Sanctuary | `wh3_main_spell_ice_crystal_sanctuary` | Damage Resistance: +80 (to self and allies) |
| Crystal Sanctuary Upgraded | `wh3_main_spell_ice_crystal_sanctuary_upgraded` | Damage Resistance: +80 (to self and allies) |
| Curse of Da Bad Moon | `wh_main_spell_lil_waaagh_curse_of_da_bad_moon` | Speed: -25%; Armour: -30; Melee Defence: -24 |
| Curse of Da Bad Moon Upgraded | `wh_main_spell_lil_waaagh_curse_of_da_bad_moon_upgraded` | Speed: -25%; Armour: -30; Melee Defence: -24 |
| Curse of Hashut | `wh3_dlc23_spell_hashut_curse_of_hashut` | Damage: 67 every 1s (to enemies in range) |
| Curse of Hashut Upgraded | `wh3_dlc23_spell_hashut_curse_of_hashut_upgraded` | Damage: 67 every 1s (to enemies in range) |
| Curse of the Ancient Witch | `wh3_dlc24_spell_hags_curse_of_the_ancient_witch` | Armour: -60 (to enemies in range); Missile Block Chance: -50 (to enemies in range) |
| Curse of the Leper | `wh3_main_spell_nurgle_curse_of_the_leper` | Armour: +30 (to self and allies); Melee Damage Reflection: +14 (to self and allies) |
| Curse of the Leper Upgraded | `wh3_main_spell_nurgle_curse_of_the_leper_upgraded` | Armour: +60 (to self and allies); Melee Damage Reflection: +28 (to self and allies) |
| Curse of the Midnight Wind | `wh_main_spell_heavens_curse_of_the_midnight_wind` | Armour: -30 (to enemies in range); Melee Attack: -24 (to enemies in range) |
| Curse of the Midnight Wind Upgraded | `wh_main_spell_heavens_curse_of_the_midnight_wind_upgraded` | Armour: -30 (to enemies in range); Melee Attack: -24 (to enemies in range) |
| Curse of Years | `wh_dlc04_spell_vampires_curse_of_years_helman` | Speed: -25% (to enemies in range); Melee Attack: -24 (to enemies in range); Silenced (to enemies in range) |
| Curse of Years | `wh_main_spell_vampires_curse_of_years` | Speed: -25% (to enemies in range); Melee Attack: -24 (to enemies in range); Silenced (to enemies in range) |
| Cursed Cauldron | `wh3_dlc24_spell_hags_cursed_cauldron` | Causes major magical damage; Medium strike area; Good against armour; Strong vs a single unit |
| Dance of Despair | `wh3_dlc25_cataclysm_shadow_dance_of_despair_com` | Leadership: -24 (to enemies in range); Removes Bound Fire Daemon attribute (to enemies in range); Removes Construct attribute (to enemies in range); Removes Daemonic attribute (to enemies in range); Removes Elemental attribute (to enemies in range); Removes Unbreakable (to enemies in range); Removes Undead attribute (to enemies in range) |
| Dance of Despair | `wh3_main_cataclysm_shadow_dance_of_despair` | Leadership: -24 (to enemies in range); Removes Bound Fire Daemon attribute (to enemies in range); Removes Construct attribute (to enemies in range); Removes Daemonic attribute (to enemies in range); Removes Elemental attribute (to enemies in range); Removes Unbreakable (to enemies in range); Removes Undead attribute (to enemies in range) |
| Dark Subjugation | `wh3_dlc23_spell_hashut_dark_subjugation` | Melee Defence: -24 (to enemies in range); Leadership: -8 (to enemies in range) |
| Dark Subjugation Upgraded | `wh3_dlc23_spell_hashut_dark_subjugation_upgraded` | Melee Defence: -24 (to enemies in range); Leadership: -8 (to enemies in range) |
| Death Frenzy | `wh2_main_spell_ruin_death_frenzy` | Melee Attack: +24 (to self and allies); Armour-Piercing Weapon Damage: +30% (to self and allies); Base Weapon Damage: +30% (to self and allies); Immune to Psychology (to self and allies) |
| Death Frenzy Upgraded | `wh2_main_spell_ruin_death_frenzy_upgraded` | Melee Attack: +24 (to self and allies); Armour-Piercing Weapon Damage: +30% (to self and allies); Base Weapon Damage: +30% (to self and allies); Immune to Psychology (to self and allies) |
| Death Frost | `wh3_main_spell_ice_death_frost` | Damage: 67 every 1s (to enemies in range) |
| Death Frost Upgraded | `wh3_main_spell_ice_death_frost_upgraded` | Damage: 67 every 1s (to enemies in range) |
| Deliverance of Itza I | `wh2_dlc12_spell_kroak_deliverance_of_itza_1` | Explosion does not affect friendly troops; Large explosion area; Strong vs a single unit |
| Deliverance of Itza II | `wh2_dlc12_spell_kroak_deliverance_of_itza_2` | Explosion does not affect friendly troops; Huge explosion area; Strong vs multiple units |
| Deliverance of Itza III | `wh2_dlc12_spell_kroak_deliverance_of_itza_3` | Explosion does not affect friendly troops; Huge explosion area; Good against armour; Strong vs multiple units |
| Denizens of the Deep | `wh2_dlc11_spell_deep_denizens_of_the_deep` | Summons a unit of Rotting Prometheans; Summoned units degrade over time |
| Devolve | `wh_dlc03_spell_wild_devolve` | Charge Speed: -25% (to enemies in range); Speed: -25% (to enemies in range); Melee Attack: -24 (to enemies in range); Leadership: -8 (to enemies in range) |
| Devolve Upgraded | `wh_dlc03_spell_wild_devolve_upgraded` | Charge Speed: -25% (to enemies in range); Speed: -25% (to enemies in range); Melee Attack: -24 (to enemies in range); Leadership: -8 (to enemies in range) |
| Djaf's Incantation of Cursed Blades | `wh2_dlc09_spell_nehekhara_djafs_incantation_of_cursed_blades` | Armour-Piercing Weapon Damage: +25% (to self and allies); Base Weapon Damage: +25% (to self and allies) |
| Djaf's Incantation of Cursed Blades Upgraded | `wh2_dlc09_spell_nehekhara_djafs_incantation_of_cursed_blades_upgraded` | Bonus vs. Large: +16 (to self and allies); Armour-Piercing Weapon Damage: +25% (to self and allies); Base Weapon Damage: +25% (to self and allies) |
| Doom & Darkness | `wh_dlc04_spell_death_doom_and_darkness_strigoi` | Leadership: -16 (to enemies in range) |
| Doom & Darkness | `wh_main_spell_death_doom_and_darkness` | Leadership: -16 (to enemies in range) |
| Doom & Darkness Upgraded | `wh3_dlc27_spell_death_doom_and_darkness_summoned` | Leadership: -16 (to enemies in range) |
| Doom & Darkness Upgraded | `wh_main_spell_death_doom_and_darkness_upgraded` | Leadership: -16 (to enemies in range) |
| Doombolt | `wh2_main_spell_dark_magic_doombolt` | Causes major magical damage; Medium strike area; Good against armour; Strong vs a single combatant; Strong vs a single unit |
| Doombolt Upgraded | `wh2_main_spell_dark_magic_doombolt_upgraded` | Increased armour-piercing damage; Causes major magical damage; Medium strike area; Good against armour; Strong vs a single combatant; Strong vs a single unit |
| Dragon's Breath | `wh3_main_spell_yang_dragons_breath` | Spell / Winds-of-Magic / Cataclysm ability. |
| Dragon's Breath Upgraded | `wh3_main_spell_yang_dragons_breath_upgraded` | Increased damage |
| Drowned Dead | `wh2_dlc11_spell_vampires_drowned_dead` | Summons a unit of Zombie Pirate Deckhands Mob; Good at defending spellcaster; Summoned units degrade over time |
| Drowned Dead | `wh3_dlc24_spell_the_changeling_drowned_dead` | Summons a unit of Bloated Corpse; Good at flanking enemies; Summoned units degrade over time |
| Drowned Dead Upgraded | `wh2_dlc11_spell_vampires_drowned_dead_upgraded` | Summons a unit of Zombie Pirate Gunnery Mob; Good at flanking enemies; Summoned units degrade over time |
| Earth Blood | `wh_dlc05_spell_life_earth_blood` | Heals: +0.8% per tick (to self and allies) |
| Earth Blood | `wh_dlc05_spell_life_earth_blood_branchwraith` | Heals: +0.8% per tick (to self and allies) |
| Earth Blood Upgraded | `wh_dlc05_spell_life_earth_blood_upgraded` | Heals: +0.8% per tick (to self and allies) |
| Fiery Convocation | `wh2_main_spell_high_magic_fiery_convocation` | Causes major magical & fire damage; Medium, forward-moving area of effect; Good against armour; Strong vs multiple units; Weak vs a single combatant |
| Fiery Convocation Upgraded | `wh2_main_spell_high_magic_fiery_convocation_upgraded` | Increased armour-piercing damage; Causes major magical & fire damage; Medium, forward-moving area of effect; Good against armour; Strong vs multiple units; Weak vs a single combatant |
| Final Transmutation | `wh_dlc08_spell_metal_final_transmutation_arzik` | Damage: 133 every 1s (to enemies in range) |
| Final Transmutation | `wh_main_spell_metal_final_transmutation` | Damage: 133 every 1s (to enemies in range) |
| Final Transmutation Upgraded | `wh3_dlc27_spell_metal_final_transmutation_summoned` | Damage: 133 every 1s (to enemies in range) |
| Final Transmutation Upgraded | `wh_main_spell_metal_final_transmutation_upgraded` | Damage: 133 every 1s (to enemies in range) |
| Fireball | `wh_dlc08_spell_fire_fireball_kihar` | Causes moderate magical & fire damage; Powerful explosion; Strong vs multiple combatants; Effective at long range |
| Fireball | `wh_main_spell_fire_fireball` | Causes moderate magical & fire damage; Powerful explosion; Strong vs multiple combatants; Effective at long range; Requires line of sight to the target |
| Fireball Upgraded | `wh3_dlc27_spell_fire_fireball_summoned` | Greater armour-piercing explosion damage; Increased armour-piercing damage; Increased damage; Causes moderate magical & fire damage; Powerful explosion; Strong vs multiple combatants; Effective at long range; Requires line of sight to the target |
| Fireball Upgraded | `wh_main_spell_fire_fireball_upgraded` | Greater armour-piercing explosion damage; Increased armour-piercing damage; Increased damage; Causes moderate magical & fire damage; Powerful explosion; Strong vs multiple combatants; Effective at long range; Requires line of sight to the target |
| Fists of Gork | `wh_main_spell_big_waaagh_fists_of_gork` | Melee Attack: +24 (to self and allies); Melee Defence: +24 (to self and allies); Magical Attacks (to self and allies) |
| Flame Storm | `wh_main_spell_fire_flame_storm` | Causes major magical & fire damage; Medium, randomly-moving area of effect; Strong vs multiple units; Weak vs a single combatant |
| Flame Storm Upgraded | `wh3_dlc27_spell_fire_flame_storm_summoned` | Increased damage; Extended effect duration; Causes major magical & fire damage; Large, randomly-moving area of effect; Strong vs multiple units; Weak vs a single combatant |
| Flame Storm Upgraded | `wh_main_spell_fire_flame_storm_upgraded` | Increased damage; Extended effect duration; Causes major magical & fire damage; Large, randomly-moving area of effect; Strong vs multiple units; Weak vs a single combatant |
| Flames of Azgorh | `wh3_dlc23_spell_hashut_flames_of_azgorh` | Causes major magical damage; Medium strike area; Good against armour; Strong vs a single unit |
| Flames of Azgorh Upgraded | `wh3_dlc23_spell_hashut_flames_of_azgorh_upgraded` | Increased number of missiles; Causes major magical & fire damage; Medium strike area; Good against armour; Strong vs a single unit |
| Flaming Sword of Rhuin | `wh_dlc08_spell_fire_flaming_sword_of_rhuin_kihar` | Base Missile Damage: +25% (to self and allies); Base Weapon Damage: +30% (to self and allies); Magical Attacks (to self and allies); Flaming Attacks (to self and allies) |
| Flaming Sword of Rhuin | `wh_main_spell_fire_flaming_sword_of_rhuin` | Base Missile Damage: +25% (to self and allies); Base Weapon Damage: +30% (to self and allies); Magical Attacks (to self and allies); Flaming Attacks (to self and allies) |
| Flaming Sword of Rhuin Upgraded | `wh_main_spell_fire_flaming_sword_of_rhuin_upgraded` | Base Missile Damage: +25% (to self and allies); Base Weapon Damage: +30% (to self and allies); Magical Attacks (to self and allies); Flaming Attacks (to self and allies) |
| Flensing Haar | `wh3_dlc27_spell_mists_flensing_haar` | Armour: -30 (to enemies in range); Missile Block Chance: -36 (to enemies in range) |
| Flensing Haar Upgraded | `wh3_dlc27_spell_mists_flensing_haar_upgraded` | Armour: -30 (to enemies in range); Missile Block Chance: -36 (to enemies in range) |
| Flensing Ruin | `wh2_dlc14_spell_ruin_flensing_ruin` | Armour: -30 (to enemies in range); Damage: 100 every 2s (to enemies in range) |
| Flensing Ruin Upgraded | `wh2_dlc14_spell_ruin_flensing_ruin_upgraded` | Armour: -30 (to enemies in range); Damage: 100 every 2s (to enemies in range) |
| Flesh to Stone | `wh_dlc05_spell_life_flesh_to_stone` | Physical Resistance: +60 (to self and allies) |
| Flesh to Stone Upgraded | `wh_dlc05_spell_life_flesh_to_stone_upgraded` | Physical Resistance: +60 (to self and allies) |
| Fleshy Abundance | `wh3_main_spell_nurgle_fleshy_abundance` | Heals: +1.6% per tick (to self and allies) |
| Fleshy Abundance Upgraded | `wh3_main_spell_nurgle_fleshy_abundance_upgraded` | Heals: +1.6% per tick (to self and allies) |
| Flock of Doom | `wh_dlc03_spell_beasts_flock_of_doom` | Damage: 5 every 1s (to enemies in range) |
| Flock of Doom Upgraded | `wh_dlc03_spell_beasts_flock_of_doom_upgraded` | Damage: 5 every 1s (to enemies in range) |
| Fog of the Damned | `wh2_dlc11_spell_deep_fog_of_the_damned` | Melee Attack: -24 (to enemies in range); Leadership: -8 (to enemies in range) |
| Fog of the Damned Upgraded | `wh2_dlc11_spell_deep_fog_of_the_damned_upgraded` | Melee Attack: -40 (to enemies in range); Leadership: -8 (to enemies in range) |
| Foot of Gork | `wh_main_spell_big_waaagh_foot_of_gork` | Huge explosion area; Strong vs multiple units; Weak vs a single combatant |
| Foot of Gork Upgraded | `wh_main_spell_big_waaagh_foot_of_gork_upgraded` | Greater armour-piercing explosion damage; Increased explosion damage; Huge explosion area; Strong vs multiple units; Weak vs a single combatant |
| Frost Blades | `wh3_main_spell_ice_frost_blades` | Melee Attack: +24 (to self and allies); Armour-Piercing Weapon Damage: +25% (to self and allies); Base Weapon Damage: +25% (to self and allies); Magical Attacks (to self and allies) |
| Frost Blades Upgraded | `wh3_main_spell_ice_frost_blades_upgraded` | Melee Attack: +24 (to self and allies); Armour-Piercing Weapon Damage: +50% (to self and allies); Base Weapon Damage: +50% (to self and allies); Magical Attacks (to self and allies) |
| Gaze of Mork | `wh_main_spell_big_waaagh_gaze_of_mork` | Causes moderate magical damage; Good against large combatants; Strong vs a single combatant; Requires line of sight to the target |
| Gaze of Mork Upgraded | `wh_main_spell_big_waaagh_gaze_of_mork_upgraded` | Increased damage; Causes moderate magical damage; Good against large combatants; Strong vs a single combatant; Requires line of sight to the target |
| Gaze of Nagash | `wh_dlc04_spell_vampires_gaze_of_nagash_helman` | Causes moderate magical damage; Good against armour; Good against large combatants; Strong vs a single combatant |
| Gaze of Nagash | `wh_dlc04_spell_vampires_gaze_of_nagash_strigoi` | Causes moderate magical damage; Good against armour; Good against large combatants; Strong vs a single combatant |
| Gaze of Nagash | `wh_main_spell_vampires_gaze_of_nagash` | Causes moderate magical damage; Good against armour; Good against large combatants; Strong vs a single combatant; Requires line of sight to the target |
| Gaze of Nagash Upgraded | `wh_main_spell_vampires_gaze_of_nagash_upgraded` | Increased number of missiles; Causes moderate magical damage; Good against armour; Good against large combatants; Strong vs a single combatant; Requires line of sight to the target |
| Gehenna's Golden Globe | `wh3_dlc25_cataclysm_metal_gehennas_golden_globe_com` | Medium, forward-moving area of effect; Strong vs multiple units; Weak vs a single combatant |
| Gehenna's Golden Globe | `wh3_main_cataclysm_metal_gehennas_golden_globe` | Medium, forward-moving area of effect; Strong vs multiple units; Weak vs a single combatant |
| Gehenna's Golden Hounds | `wh_dlc08_spell_metal_gehennas_golden_hounds_arzik` | Medium, randomly-moving area of effect; Strong vs multiple units; Weak vs a single combatant |
| Gehenna's Golden Hounds | `wh_main_spell_metal_gehennas_golden_hounds` | Medium, randomly-moving area of effect; Strong vs multiple units; Weak vs a single combatant |
| Gehenna's Golden Hounds Upgraded | `wh3_dlc27_spell_metal_gehennas_golden_hounds_summoned` | Extended effect duration; Large, randomly-moving area of effect; Strong vs multiple units; Weak vs a single combatant |
| Gehenna's Golden Hounds Upgraded | `wh_main_spell_metal_gehennas_golden_hounds_upgraded` | Extended effect duration; Large, randomly-moving area of effect; Strong vs multiple units; Weak vs a single combatant |
| Glean Magic | `wh3_main_spell_tzeentch_glean_magic` | Silenced (to enemies in range); Power Recharge: -40% (to enemies in range); Reserves Per Second: -0.10 (to enemies in range); Spell Mastery: +15%; Power Recharge: +80%; Reserves Per Second: +0.10 |
| Glean Magic Upgraded | `wh3_main_spell_tzeentch_glean_magic_upgraded` | Silenced (to enemies in range); Power Recharge: -40% (to enemies in range); Reserves Per Second: -0.10 (to enemies in range); Spell Mastery: +15%; Power Recharge: +80%; Reserves Per Second: +0.10 |
| Glittering Robe | `wh_main_spell_metal_glittering_robe` | Armour: +60 (to self and allies) |
| Glittering Robe Upgraded | `wh_main_spell_metal_glittering_robe_upgraded` | Armour: +60 (to self and allies) |
| Gork'll Fix It | `wh_main_spell_lil_waaagh_gorkll_fix_it` | Charge Speed: -45% (to enemies in range); Speed: -45% (to enemies in range); Charge Bonus: -20% (to enemies in range) |
| Gust of True Flight | `wh3_main_spell_tempest_gust_of_true_flight` | Range: +30% (to self and allies); Accuracy: +30 (to self and allies) |
| Gust of True Flight Upgraded | `wh3_main_spell_tempest_gust_of_true_flight_upgraded` | Range: +30% (to self and allies); Accuracy: +30 (to self and allies) |
| Hailstorm | `wh3_main_spell_tempest_hailstorm` | Medium strike area |
| Hailstorm Upgraded | `wh3_main_spell_tempest_hailstorm_upgraded` | Extended effect duration; Increased number of missiles; Medium strike area |
| Hand of Glory | `wh2_main_spell_high_magic_hand_of_glory` | Melee Attack: +24 (to self and allies); Reload Skill: +40 (to self and allies) |
| Hand of Glory Upgraded | `wh2_main_spell_high_magic_hand_of_glory_upgraded` | Melee Attack: +24 (to self and allies); Reload Skill: +60 (to self and allies) |
| Harmonic Convergence | `wh_main_spell_heavens_harmonic_convergence` | Melee Attack: +24 (to self and allies); Melee Defence: +24 (to self and allies); Reload Skill: +20 (to self and allies) |
| Harmonic Convergence Upgraded | `wh_main_spell_heavens_harmonic_convergence_upgraded` | Armour: +30 (to self and allies); Melee Attack: +24 (to self and allies); Melee Defence: +24 (to self and allies); Reload Skill: +20 (to self and allies) |
| Hawks of Miska | `wh3_main_spell_tempest_hawks_of_miska` | Leadership: -16 |
| Hawks of Miska Upgraded | `wh3_main_spell_tempest_hawks_of_miska_upgraded` | Leadership: -16 |
| Heart of Winter | `wh3_main_spell_ice_heart_of_winter` | Speed: -10% (to enemies in range); Damage: 2 every 1s (to enemies in range); Speed: -25% (to enemies in range); Damage: 4 every 1s (to enemies in range); Speed: -40% (to enemies in range); Damage: 6 every 1s (to enemies in range); Speed: -60% (to enemies in range); Damage: 8 every 1s (to enemies in range) |
| Heart of Winter | `wh3_twa08_spell_bound_heart_of_winter_elemental_bear_ror` | Speed: -10% (to enemies in range); Damage: 2 every 1s (to enemies in range); Speed: -25% (to enemies in range); Damage: 4 every 1s (to enemies in range); Speed: -40% (to enemies in range); Damage: 6 every 1s (to enemies in range); Speed: -60% (to enemies in range); Damage: 8 every 1s (to enemies in range) |
| Heart of Winter Upgraded | `wh3_main_spell_ice_heart_of_winter_upgraded` | Speed: -10% (to enemies in range); Damage: 3 every 1s (to enemies in range); Speed: -25% (to enemies in range); Damage: 6 every 1s (to enemies in range); Speed: -40% (to enemies in range); Damage: 9 every 1s (to enemies in range); Speed: -60% (to enemies in range); Damage: 12 every 1s (to enemies in range) |
| Hell Hammer | `wh3_dlc23_spell_hashut_hell_hammer` | Small, forward-moving area of effect; Strong vs multiple units; Weak vs a single combatant |
| Hell Hammer Upgraded | `wh3_dlc23_spell_hashut_hell_hammer_upgraded` | Extended effect duration; Small, forward-moving area of effect; Strong vs multiple units; Weak vs a single combatant |
| Howling Warpgale | `wh2_main_spell_ruin_howling_warpgale` | Spell / Winds-of-Magic / Cataclysm ability. |
| Howling Warpgale Upgraded | `wh2_main_spell_ruin_howling_warpgale_upgraded` | Extended effect duration |
| Hysterical Frenzy | `wh3_main_spell_slaanesh_hysterical_frenzy` | Melee Attack: +40 (to self and allies); Armour-Piercing Weapon Damage: +25% (to self and allies); Base Weapon Damage: +25% (to self and allies) |
| Hysterical Frenzy Upgraded | `wh3_main_spell_slaanesh_hysterical_frenzy_upgraded` | Melee Attack: +40 (to self and allies); Armour-Piercing Weapon Damage: +25% (to self and allies); Base Weapon Damage: +25% (to self and allies) |
| Ice Maiden's Kiss | `wh3_main_spell_ice_ice_maidens_kiss` | Short, wide, expanding, tear-shaped attack |
| Ice Maiden's Kiss Upgraded | `wh3_main_spell_ice_ice_maidens_kiss_upgraded` | Increased damage; Short, wide, expanding, tear-shaped attack |
| Ice Sheet | `wh3_main_spell_ice_ice_sheet` | Charge Speed: -25% (to enemies in range); Acceleration: -25% (to enemies in range); Speed: -25% (to enemies in range) |
| Incantation of Mania | `wh3_dlc24_spell_hags_malediction_of_madness_upgraded` | Melee Attack: +24 (to self and allies); Armour-Piercing Weapon Damage: +50% (to self and allies); Base Weapon Damage: +50% (to self and allies); Rampage! (to self and allies) |
| Infernal Gateway | `wh3_main_spell_tzeentch_infernal_gateway` | Huge, stationary area of effect |
| Infernal Gateway Upgraded | `wh3_main_spell_tzeentch_infernal_gateway_upgraded` | Increased armour-piercing damage; Huge, stationary area of effect |
| Invocation of Nehek | `wh_dlc04_spell_vampires_invocation_of_nehek_helman` | Heals: +0.8% per tick (to self and allies) |
| Invocation of Nehek | `wh_dlc04_spell_vampires_invocation_of_nehek_strigoi` | Heals: +0.8% per tick (to self and allies) |
| Invocation of Nehek | `wh_main_spell_vampires_invocation_of_nehek` | Heals: +0.8% per tick (to self and allies) |
| Invocation of Nehek Upgraded | `wh_main_spell_vampires_invocation_of_nehek_upgraded` | Heals: +0.8% per tick (to self and allies) |
| Itchy Nuisance | `wh_main_spell_lil_waaagh_itchy_nuisance` | Melee Attack: -24 (to enemies in range); Base Weapon Damage: -30% (to enemies in range) |
| Jade Shield | `wh3_main_spell_yang_jade_shield` | Damage Resistance: +44 (to self and allies) |
| Jade Shield Upgraded | `wh3_main_spell_yang_jade_shield_upgraded` | Damage Resistance: +44 (to self and allies) |
| Kraken's Pull | `wh2_dlc11_spell_deep_krakens_pull` | Speed: -45% |
| Kraken's Pull Upgraded | `wh2_dlc11_spell_deep_krakens_pull_upgraded` | Extended effect duration; Huge, stationary area of effect; Good against armour; Strong vs multiple units |
| Ladrielle's Shroud | `wh3_dlc27_spell_mists_ladrielles_shroud` | Immune to Contact Effects (to self and allies); Vigour per second: -3% (to self and allies) |
| Ladrielle's Shroud Upgraded | `wh3_dlc27_spell_mists_ladrielles_shroud_upgraded` | Immune to Contact Effects (to self and allies); Vigour per second: -3% (to self and allies); Heals: +0.5% per tick (to self and allies) |
| Lash of Slaanesh | `wh3_main_spell_slaanesh_lash_of_slaanesh` | Expanding tear-shaped attack |
| Lash of Slaanesh Upgraded | `wh3_main_spell_slaanesh_lash_of_slaanesh_upgraded` | Increased armour-piercing damage; Expanding tear-shaped attack |
| Lesser Awakening from the Grave | `wh3_dlc29_bound_spell_vampires_raise_dead_upgraded` | Summons a unit of Grave Guard; Good at melee combat; Summoned units degrade over time |
| Light of Battle | `wh_main_spell_light_light_of_battle` | Unbreakable (to self and allies) |
| Light of Battle Upgraded | `wh_main_spell_light_light_of_battle_upgraded` | Unbreakable (to self and allies) |
| Magma Storm | `wh3_dlc25_cataclysm_fire_magma_storm_com` | Causes major magical damage; Medium strike area; Good against armour; Strong vs a single unit |
| Magma Storm | `wh3_main_cataclysm_fire_magma_storm` | Causes major magical damage; Medium strike area; Good against armour; Strong vs a single unit |
| Malediction of Madness | `wh3_dlc24_spell_hags_malediction_of_madness` | Melee Attack: -24 (to enemies in range); Armour-Piercing Weapon Damage: -50% (to enemies in range); Base Weapon Damage: -50% (to enemies in range); Rampage! (to enemies in range) |
| Mantle of Ghorok | `wh_dlc03_spell_wild_mantle_of_ghorok` | Armour: -30 (to self and allies); Melee Attack: +40 (to self and allies); Armour-Piercing Weapon Damage: +50% (to self and allies); Base Weapon Damage: +50% (to self and allies) |
| Mantle of Ghorok Upgraded | `wh2_dlc17_spell_wild_mantle_of_ghorok_upgraded` | Armour: -30 (to self and allies); Melee Attack: +40 (to self and allies); Armour-Piercing Weapon Damage: +50% (to self and allies); Base Weapon Damage: +50% (to self and allies) |
| Mathlann’s Spite | `wh3_dlc27_spell_mists_mathlanns_spite` | Speed: -30% (to enemies in range); Vigour per second: +1% (to enemies in range); Damage: 30 every 1s (to enemies in range) |
| Mathlann’s Spite Upgraded | `wh3_dlc27_spell_mists_mathlanns_spite_upgraded` | Speed: -45% (to enemies in range); Vigour per second: +1% (to enemies in range); Damage: 30 every 1s (to enemies in range) |
| Melkoth's Mystifying Miasma | `wh3_dlc27_spell_shadow_melkoths_mystifying_miasma_bound` | Speed: -25% (to enemies in range); Damage: 5 every 1s (to enemies in range) |
| Melkoth's Mystifying Miasma | `wh_dlc05_spell_shadow_melkoths_mystifying_miasma` | Speed: -25% (to enemies in range); Damage: 5 every 1s (to enemies in range) |
| Melkoth's Mystifying Miasma | `wh_dlc05_spell_shadow_melkoths_mystifying_miasma_branchwraith` | Speed: -25% (to enemies in range); Damage: 5 every 1s (to enemies in range) |
| Melkoth's Mystifying Miasma Upgraded | `wh_dlc05_spell_shadow_melkoths_mystifying_miasma_upgraded` | Speed: -25% (to enemies in range); Damage: 5 every 1s (to enemies in range) |
| Merciw's Monstrous Regiment | `wh3_dlc25_cataclysm_beasts_merciws_monstrous_regiment_com` | Melee Attack: +40 (to allies in range); Armour-Piercing Weapon Damage: +50% (to allies in range); Base Weapon Damage: +50% (to allies in range); Physical Resistance: +20 (to allies in range) |
| Merciw's Monstrous Regiment | `wh3_main_cataclysm_beasts_merciws_monstrous_regiment` | Melee Attack: +40 (to allies in range); Armour-Piercing Weapon Damage: +50% (to allies in range); Base Weapon Damage: +50% (to allies in range); Physical Resistance: +20 (to allies in range) |
| Miasma of Pestilence | `wh3_main_spell_nurgle_miasma_of_pestilence` | Charge Bonus: -40% (to enemies in range); Melee Attack: -24 (to enemies in range) |
| Miasma of Pestilence Upgraded | `wh3_main_spell_nurgle_miasma_of_pestilence_upgraded` | Charge Bonus: -40% (to enemies in range); Melee Attack: -24 (to enemies in range) |
| Might of Heaven & Earth | `wh3_main_spell_yang_might_of_heaven_and_earth` | Melee Attack: +24 (to self and allies); Armour-Piercing Weapon Damage: +25% (to self and allies); Base Weapon Damage: +25% (to self and allies); Magical Attacks (to self and allies); Flaming Attacks (to self and allies) |
| Might of Heaven & Earth Upgraded | `wh3_main_spell_yang_might_of_heaven_and_earth_upgraded` | Melee Attack: +40 (to self and allies); Armour-Piercing Weapon Damage: +50% (to self and allies); Base Weapon Damage: +50% (to self and allies); Magical Attacks (to self and allies); Flaming Attacks (to self and allies) |
| Missile Mirror | `wh3_main_spell_yin_missile_mirror` | Redirects projectiles back towards the firing unit |
| Missile Mirror Upgraded | `wh3_main_spell_yin_missile_mirror_upgraded` | Redirects projectiles back towards the firing unit; Extended cast range; Extended effect duration |
| Mistress of the Deeps | `wh3_dlc27_spell_mists_mistress_of_the_deeps` | Summons a unit of Oceanids; Summoned units degrade over time |
| Neru's Incantation of Protection | `wh2_dlc09_spell_nehekhara_nerus_incantation_of_protection` | Physical Resistance: +40 (to self and allies) |
| Neru's Incantation of Protection Upgraded | `wh2_dlc09_spell_nehekhara_nerus_incantation_of_protection_upgraded` | Physical Resistance: +40 (to self and allies) |
| Net of Amyntok | `wh_main_spell_light_net_of_amyntok` | Spell / Winds-of-Magic / Cataclysm ability. |
| Net of Amyntok Upgraded | `wh_main_spell_light_net_of_amyntok_upgraded` | Added effect area |
| Night Shroud | `wh_main_spell_lil_waaagh_night_shroud` | Stalk (to self and allies); Unspottable (to self and allies) |
| Night Shroud Upgraded | `wh_main_spell_lil_waaagh_night_shroud_upgraded` | Stalk (to self and allies); Unspottable (to self and allies) |
| Okkam's Mindrazor | `wh_dlc05_spell_shadow_okkams_mindrazor` | Armour-Piercing Weapon Damage: +50% (to self and allies); Base Weapon Damage: +50% (to self and allies); Magical Attacks (to self and allies) |
| Okkam's Mindrazor Upgraded | `wh_dlc05_spell_shadow_okkams_mindrazor_upgraded` | Armour-Piercing Weapon Damage: +50% (to self and allies); Base Weapon Damage: +50% (to self and allies); Magical Attacks (to self and allies) |
| Omen of Spirits | `wh3_dlc24_spell_hags_vengeance_of_spirits_upgraded` | Spell Mastery: +60% (to self and allies); Power Recharge: +60% (to self and allies); Damage: 33 every 1s (to self and allies) |
| Pann's Impenetrable Pelt | `wh_dlc03_spell_beasts_panns_impenetrable_pelt` | Speed: +25% (to self and allies); Melee Defence: +24 (to self and allies); Physical Resistance: +20 (to self and allies) |
| Pann's Impenetrable Pelt | `wh_dlc03_spell_beasts_panns_impenetrable_pelt_summoned` | Speed: +25% (to self and allies); Melee Defence: +24 (to self and allies); Physical Resistance: +20 (to self and allies) |
| Pann's Impenetrable Pelt Upgraded | `wh_dlc03_spell_beasts_panns_impenetrable_pelt_upgraded` | Speed: +25% (to self and allies); Melee Defence: +24 (to self and allies); Physical Resistance: +20 (to self and allies) |
| Pavane of Slaanesh | `wh3_main_spell_slaanesh_pavane_of_slaanesh` | Vigour per second: +3% (to enemies in range); Damage: 5 every 1s (to enemies in range); Rampage! (to enemies in range) |
| Pavane of Slaanesh Upgraded | `wh3_main_spell_slaanesh_pavane_of_slaanesh_upgraded` | Vigour per second: +3% (to enemies in range); Damage: 10 every 1s (to enemies in range); Rampage! (to enemies in range) |
| Pestilent Birth | `wh2_main_spell_plague_pestilent_birth` | Summons a unit of Plague Monks; Good at flanking enemies; Summoned units degrade over time |
| Pestilent Breath | `wh2_main_spell_plague_pestilent_breath` | Expanding tear-shaped attack; Strong vs multiple units |
| Pestilent Breath Upgraded | `wh2_main_spell_plague_pestilent_breath_upgraded` | Additional poison contact effect; Expanding tear-shaped attack; Strong vs multiple units |
| Pha's Protection | `wh_main_spell_light_phas_protection` | Armour: +30 (to self and allies); Melee Defence: +24 (to self and allies) |
| Pha's Protection Upgraded | `wh_main_spell_light_phas_protection_upgraded` | Armour: +30 (to self and allies); Melee Defence: +24 (to self and allies) |
| Phantasmagoria | `wh3_main_spell_slaanesh_phantasmagoria` | Leadership: -16 (to enemies in range) |
| Phantasmagoria Upgraded | `wh3_main_spell_slaanesh_phantasmagoria_upgraded` | Leadership: -16 (to enemies in range) |
| Piercing Bolts of Burning | `wh_main_spell_fire_piercing_bolts_of_burning` | Causes major magical & fire damage; Medium strike area; Good against armour; Strong vs a single unit |
| Piercing Bolts of Burning Upgraded | `wh_main_spell_fire_piercing_bolts_of_burning_upgraded` | Increased number of missiles; Wider strike area; Causes major magical & fire damage; Large strike area; Good against armour; Strong vs a single unit |
| Pink Fire of Tzeentch | `wh3_main_spell_tzeentch_pink_fire_of_tzeentch` | Expanding tear-shaped attack |
| Pink Fire of Tzeentch Upgraded | `wh3_main_spell_tzeentch_pink_fire_of_tzeentch_upgraded` | Increased damage; Expanding tear-shaped attack |
| Pit of Shades | `wh_dlc05_spell_shadow_pit_of_shades` | Huge, stationary area of effect; Good against armour; Strong vs multiple units |
| Pit of Shades | `wh_dlc08_spell_shadow_pit_of_shades_kihar` | Huge, stationary area of effect; Good against armour; Strong vs multiple units |
| Pit of Shades Upgraded | `wh_dlc05_spell_shadow_pit_of_shades_upgraded` | Increased armour-piercing damage; Huge, stationary area of effect; Good against armour; Strong vs multiple units |
| Plague | `wh2_main_spell_plague_plague` | Large, expanding area of effect; Good against armour; Strong vs multiple units; Weak vs a single combatant |
| Plague of Rust | `wh_dlc08_spell_metal_plague_of_rust_kihar` | Armour: -30 (to enemies in range) |
| Plague of Rust | `wh_main_spell_metal_plague_of_rust` | Armour: -30 (to enemies in range) |
| Plague of Rust Upgraded | `wh_main_spell_metal_plague_of_rust_upgraded` | Armour: -60 (to enemies in range) |
| Plague Upgraded | `wh2_main_spell_plague_plague_upgraded` | Increased armour-piercing damage; Large, expanding area of effect; Good against armour; Strong vs multiple units; Weak vs a single combatant |
| Power of Darkness | `wh2_main_spell_dark_magic_power_of_darkness` | Power Recharge: +80% (to self and allies); Reserves Per Second: +0.70 (to self and allies); Damage: 33 every 1s (to self and allies) |
| Ptra's Incantation of Righteous Smiting | `wh2_dlc09_spell_nehekhara_ptras_incantation_of_righteous_smiting` | Armour-Piercing Missile Damage: +40% (to self and allies); Base Missile Damage: +40% (to self and allies) |
| Ptra's Incantation of Righteous Smiting Upgraded | `wh2_dlc09_spell_nehekhara_ptras_incantation_of_righteous_smiting_upgraded` | Armour-Piercing Missile Damage: +40% (to self and allies); Base Missile Damage: +40% (to self and allies); Reload Skill: +40 (to self and allies) |
| Raise Dead | `wh_main_spell_vampires_raise_dead` | Summons a unit of Zombies; Good at defending spellcaster; Summoned units degrade over time |
| Raise Dead (Skeleton Warriors) | `wh3_dlc29_bound_spell_vampires_raise_dead` | Spell / Winds-of-Magic / Cataclysm ability. |
| Raise Dead Upgraded | `wh_main_spell_vampires_raise_dead_upgraded` | Summons a unit of Skeleton Warriors; Good at defending spellcaster; Summoned units degrade over time |
| Rancid Visitations | `wh3_main_spell_nurgle_rancid_visitations` | Damage: 133 every 1s (to enemies in range) |
| Rancid Visitations Upgraded | `wh3_main_spell_nurgle_rancid_visitations_upgraded` | Damage: 133 every 1s (to enemies in range) |
| Regrowth | `wh_dlc05_spell_life_regrowth` | Vigour per second: -1% (to self and allies); Heals: +0.8% per tick (to self and allies) |
| Regrowth Upgraded | `wh_dlc05_spell_life_regrowth_upgraded` | Vigour per second: -1% (to self and allies); Heals: +1.2% per tick (to self and allies) |
| Sakhmet's Incantation of the Skullstorm | `wh2_dlc09_spell_nehekhara_sakhmets_incantation_of_the_skullstorm` | Medium, randomly-moving area of effect; Strong vs multiple units; Weak vs a single combatant |
| Sakhmet's Incantation of the Skullstorm Upgraded | `wh2_dlc09_spell_nehekhara_sakhmets_incantation_of_the_skullstorm_upgraded` | Increased effect area; Medium, randomly-moving area of effect; Strong vs multiple units; Weak vs a single combatant |
| Savage Dominion | `wh_dlc03_spell_wild_savage_dominion` | Summons a Cygor; Summoned units degrade over time |
| Scorch | `wh2_main_spell_ruin_scorch` | Causes major magical & fire damage; Long, thin, expanding, tear-shaped attack; Strong vs multiple units; Weak vs a single combatant |
| Scorch Upgraded | `wh2_main_spell_ruin_scorch_upgraded` | Extended cast range; Extended effect duration; Causes major magical & fire damage; Long, thin, expanding, tear-shaped attack; Strong vs multiple units; Weak vs a single combatant |
| Searing Doom | `wh_dlc08_spell_metal_searing_doom_arzik` | Causes moderate magical damage; Medium strike area; Strong vs a single unit; Weak vs a single combatant |
| Searing Doom | `wh_main_spell_metal_searing_doom` | Causes moderate magical damage; Medium strike area; Strong vs a single unit; Weak vs a single combatant |
| Searing Doom Upgraded | `wh3_dlc27_spell_metal_searing_doom_summoned` | Increased number of missiles; Wider strike area; Causes moderate magical damage; Large strike area; Strong vs a single unit; Weak vs a single combatant |
| Searing Doom Upgraded | `wh_main_spell_metal_searing_doom_upgraded` | Increased number of missiles; Wider strike area; Causes moderate magical damage; Large strike area; Strong vs a single unit; Weak vs a single combatant |
| Shem's Burning Gaze | `wh_main_spell_light_shems_burning_gaze` | Causes minor magical & fire damage; Good against armour; Good against large combatants; Strong vs a single combatant; Requires line of sight to the target |
| Shem's Burning Gaze Upgraded | `wh_main_spell_light_shems_burning_gaze_upgraded` | Increased armour-piercing damage; Causes minor magical & fire damage; Good against armour; Good against large combatants; Strong vs a single combatant; Requires line of sight to the target |
| Shield of Thorns | `wh_dlc05_spell_life_shield_of_thorns` | Melee Damage Reflection: +20 (to self and allies) |
| Shield of Thorns | `wh_dlc05_spell_life_shield_of_thorns_branchwraith` | Melee Damage Reflection: +20 (to self and allies) |
| Shield of Thorns Upgraded | `wh_dlc05_spell_life_shield_of_thorns_upgraded` | Melee Damage Reflection: +32 (to self and allies) |
| Skitterleap | `wh2_main_spell_ruin_skitterleap` | Speed: +25% (to self and allies); Stalk (to self and allies); Unspottable (to self and allies) |
| Skitterleap Upgraded | `wh2_main_spell_ruin_skitterleap_upgraded` | Speed: +25% (to self and allies); Stalk (to self and allies); Unspottable (to self and allies) |
| Slicing Shards | `wh3_main_spell_slaanesh_slicing_shards` | Large strike area |
| Slicing Shards Upgraded | `wh3_main_spell_slaanesh_slicing_shards_upgraded` | Increased armour-piercing damage; Large strike area |
| Sneaky Stabbin' | `wh_main_spell_lil_waaagh_sneaky_stabbin` | Melee Attack: +24 (to self and allies); Armour-Piercing Weapon Damage: +25% (to self and allies) |
| Soul Quench | `wh2_main_spell_high_magic_soul_quench` | Causes moderate magical damage; Causes damage to combatants; Powerful explosion; Strong vs multiple combatants; Effective at long range; Requires line of sight to the target |
| Soul Quench Upgraded | `wh2_main_spell_high_magic_soul_quench_upgraded` | Increased damage; Causes moderate magical damage; Causes damage to combatants; Powerful explosion; Strong vs multiple combatants; Effective at long range; Requires line of sight to the target |
| Soul Stealer | `wh2_main_spell_dark_magic_soul_stealer` | Damage: 75 every 1s (to enemies in range); Heals: +0.8% per tick |
| Soulblight | `wh_dlc04_spell_death_soulblight_strigoi` | Armour: -30 (to enemies in range); Armour-Piercing Weapon Damage: -25% (to enemies in range); Base Weapon Damage: -25% (to enemies in range) |
| Soulblight | `wh_dlc08_spell_death_soulblight_arzik` | Armour: -30 (to enemies in range); Armour-Piercing Weapon Damage: -25% (to enemies in range); Base Weapon Damage: -25% (to enemies in range) |
| Soulblight | `wh_main_spell_death_soulblight` | Armour: -30 (to enemies in range); Armour-Piercing Weapon Damage: -25% (to enemies in range); Base Weapon Damage: -25% (to enemies in range) |
| Soulblight Upgraded | `wh_main_spell_death_soulblight_upgraded` | Armour: -30 (to enemies in range); Armour-Piercing Weapon Damage: -25% (to enemies in range); Base Weapon Damage: -25% (to enemies in range) |
| Spirit Leech | `wh_dlc04_spell_death_spirit_leech_strigoi` | Damage: 67 every 1s (to enemies in range) |
| Spirit Leech | `wh_main_spell_death_spirit_leech` | Damage: 67 every 1s (to enemies in range) |
| Spirit Leech Upgraded | `wh3_dlc27_spell_death_spirit_leech_summoned` | Damage: 67 every 1s (to enemies in range) |
| Spirit Leech Upgraded | `wh_main_spell_death_spirit_leech_upgraded` | Damage: 67 every 1s (to enemies in range) |
| Spiteful Shot | `wh2_dlc11_spell_deep_spiteful_shot` | Accuracy: +90 (to self and allies); Magical Attacks (to self and allies) |
| Spiteful Shot Upgraded | `wh2_dlc11_spell_deep_spiteful_shot_upgraded` | Accuracy: +90 (to self and allies); Magical Attacks (to self and allies) |
| Stone Ground Stance | `wh3_main_spell_yang_stone_ground_stance` | Mass: +100% (to self and allies); Leadership: +8 (to self and allies); Expert Charge Defence (to self and allies) |
| Stone Ground Stance Upgraded | `wh3_main_spell_yang_stone_ground_stance_upgraded` | Mass: +100% (to self and allies); Leadership: +8 (to self and allies); Expert Charge Defence (to self and allies) |
| Storm of Renewal | `wh3_dlc25_cataclysm_life_storm_of_renewal_com` | Vigour per second: -10% (to allies in range); Heals: +1% per tick (to allies in range) |
| Storm of Renewal | `wh3_main_cataclysm_life_storm_of_renewal` | Vigour per second: -10% (to allies in range); Heals: +1% per tick (to allies in range) |
| Storm of Shadows | `wh3_main_spell_yin_storm_of_shadows` | Charge Speed: -45% (to enemies in range); Speed: -45% (to enemies in range) |
| Storm of Shadows Upgraded | `wh3_main_spell_yin_storm_of_shadows_upgraded` | Charge Speed: -45% (to enemies in range); Speed: -45% (to enemies in range) |
| Stream of Corruption | `wh3_main_spell_nurgle_stream_of_corruption` | Long, thin, expanding, tear-shaped attack |
| Stream of Corruption Upgraded | `wh3_main_spell_nurgle_stream_of_corruption_upgraded` | Increased armour-piercing damage; Long, thin, expanding, tear-shaped attack |
| Swiftwing | `wh3_main_spell_tempest_swiftwing` | Charge Speed: +25% (to self and allies); Speed: +25% (to self and allies); Charge Bonus: +40% (to self and allies) |
| Swiftwing Upgraded | `wh3_main_spell_tempest_swiftwing_upgraded` | Charge Speed: +25% (to self and allies); Speed: +25% (to self and allies); Charge Bonus: +40% (to self and allies) |
| Talons of Night | `wh3_main_spell_yin_talons_of_night` | Huge, stationary area of effect |
| Talons of Night Upgraded | `wh3_main_spell_yin_talons_of_night_upgraded` | Increased armour-piercing damage; Huge, stationary area of effect |
| Tempest | `wh2_main_spell_high_magic_tempest` | Speed: -60% (to enemies in range); Damage: 67 every 1s (to enemies in range) |
| Tempest Upgraded | `wh2_main_spell_high_magic_tempest_upgraded` | Speed: -60% (to enemies in range); Damage: 133 every 1s (to enemies in range) |
| The Abyssal Swarm | `wh3_dlc29_spell_undeath_razkhar_the_abyssal_swarm` | Does not affect friendly troops; Large, randomly-moving area of effect |
| The Abyssal Swarm Upgraded | `wh3_dlc29_spell_undeath_razkhar_the_abyssal_swarm_upgraded` | Increased damage; Does not affect friendly troops; Large, randomly-moving area of effect |
| The Amber Spear | `wh_dlc03_spell_beasts_the_amber_spear` | Causes moderate magical damage; Good against armour; Effective at all ranges; Good penetration; Requires line of sight to the target |
| The Amber Spear Upgraded | `wh_dlc03_spell_beasts_the_amber_spear_upgraded` | Increased armour-piercing damage; Greater armour-piercing explosion damage; Causes moderate magical damage; Good against armour; Effective at all ranges; Can cause damage to friendly combatants; Requires line of sight to the target |
| The Burning Head | `wh_main_spell_fire_the_burning_head` | Causes major magical & fire damage; Medium, forward-moving area of effect; Small, forward-moving area of effect; Strong vs multiple units |
| The Burning Head Upgraded | `wh3_dlc27_spell_fire_the_burning_head_summoned` | Increased effect area; Increased damage; Causes major magical & fire damage; Medium, forward-moving area of effect; Strong vs multiple units |
| The Burning Head Upgraded | `wh_main_spell_fire_the_burning_head_upgraded` | Increased effect area; Increased damage; Causes major magical & fire damage; Medium, forward-moving area of effect; Strong vs multiple units |
| The Curse of Anraheir | `wh_dlc03_spell_beasts_the_curse_of_anraheir` | Speed: -25% (to enemies in range); Accuracy: -30 (to enemies in range); Melee Attack: -24 (to enemies in range); Melee Defence: -24 (to enemies in range) |
| The Curse of Anraheir Upgraded | `wh_dlc03_spell_beasts_the_curse_of_anraheir_upgraded` | Speed: -25% (to enemies in range); Accuracy: -30 (to enemies in range); Melee Attack: -24 (to enemies in range); Melee Defence: -24 (to enemies in range) |
| The Dark Riders | `wh3_dlc29_spell_undeath_akararan_the_dark_riders` | Medium, forward-moving area of effect; Good against armour; Strong vs multiple units; Weak vs a single combatant |
| The Dark Riders Upgraded | `wh3_dlc29_spell_undeath_akararan_the_dark_riders_upgraded` | Increased damage; Medium, forward-moving area of effect; Strong vs multiple units; Weak vs a single combatant |
| The Dreaded Thirteenth Spell | `wh2_dlc14_spell_grey_seer_the_dreaded_thirteenth_spell_upgraded` | Summons a unit of Stormvermin (Sword & Shield); Huge explosion area; Strong vs multiple units; Summoned units degrade over time |
| The Dreaded Thirteenth Spell | `wh2_main_spell_grey_seer_the_dreaded_thirteenth_spell` | Summons a unit of Stormvermin; Huge explosion area; Strong vs multiple units; Summoned units degrade over time |
| The Dwellers Below | `wh_dlc05_spell_life_the_dwellers_below` | Speed: -25% |
| The Dwellers Below Upgraded | `wh_dlc05_spell_life_the_dwellers_below_upgraded` | Speed: -50% |
| The Enfeebling Foe | `wh_dlc05_spell_shadow_the_enfeebling_foe` | Melee Attack: -24 (to enemies in range); Melee Defence: -24 (to enemies in range) |
| The Enfeebling Foe Upgraded | `wh_dlc05_spell_shadow_the_enfeebling_foe_upgraded` | Melee Attack: -24 (to enemies in range); Melee Defence: -24 (to enemies in range) |
| The Fate of Bjuna | `wh_dlc08_spell_death_the_fate_of_bjuna_arzik` | Damage: 10 every 1s (to enemies in range) |
| The Fate of Bjuna | `wh_main_spell_death_the_fate_of_bjuna` | Damage: 10 every 1s (to enemies in range) |
| The Forbidden Fens | `wh3_dlc24_spell_hags_the_forbidden_fens` | Charge Speed: -25% (to enemies in range); Speed: -25% (to enemies in range); Vigour per second: +1% (to enemies in range) |
| The Hand of Dust | `wh3_dlc29_spell_undeath_sulekhim_hand_of_dust` | Armour-Piercing Weapon Damage: +50% (to self and allies); Magical Attacks (to self and allies) |
| The Hand of Dust Upgraded | `wh3_dlc29_spell_undeath_sulekhim_hand_of_dust_upgraded` | Armour-Piercing Weapon Damage: +50% (to self and allies); Magical Attacks (to self and allies) |
| The Harbinger | `wh3_dlc29_spell_undeath_kandorak_the_harbinger` | Summons a Zombie Dragon; Summoned units degrade over time |
| The Maw | `wh3_main_spell_great_maw_the_maw` | Huge explosion area |
| The Maw Upgraded | `wh3_main_spell_great_maw_the_maw_upgraded` | Greater armour-piercing explosion damage; Huge explosion area |
| The Penumbral Pendulum | `wh_dlc05_spell_shadow_the_penumbral_pendulum` | Small, forward-moving area of effect; Strong vs multiple units; Weak vs a single combatant |
| The Penumbral Pendulum | `wh_dlc05_spell_shadow_the_penumbral_pendulum_branchwraith` | Small, forward-moving area of effect; Strong vs multiple units; Weak vs a single combatant |
| The Penumbral Pendulum | `wh_dlc08_spell_shadow_the_penumbral_pendulum_kihar` | Small, forward-moving area of effect; Strong vs multiple units; Weak vs a single combatant |
| The Penumbral Pendulum Upgraded | `wh_dlc05_spell_shadow_the_penumbral_pendulum_upgraded` | Increased armour-piercing damage; Small, forward-moving area of effect; Strong vs multiple units; Weak vs a single combatant |
| The Purple Sun of Xereus | `wh_main_spell_death_the_purple_sun_of_xereus` | Huge, randomly-moving area of effect; Good against armour; Strong vs multiple units |
| The Purple Sun of Xereus Upgraded | `wh3_dlc27_spell_death_the_purple_sun_of_xereus_summoned` | Extended effect duration; Huge, randomly-moving area of effect; Good against armour; Strong vs multiple units |
| The Purple Sun of Xereus Upgraded | `wh_main_spell_death_the_purple_sun_of_xereus_upgraded` | Extended effect duration; Huge, randomly-moving area of effect; Good against armour; Strong vs multiple units |
| The Soulstealer | `wh3_dlc29_spell_undeath_khizaar_the_soulstealer` | Vigour per second: +1% (to enemies in range); Damage: 4 every 1s (to enemies in range) |
| The Soulstealer Upgraded | `wh3_dlc29_spell_undeath_khizaar_the_soulstealer_upgraded` | Vigour per second: +1% (to enemies in range); Damage: 4 every 1s (to enemies in range) |
| The Withering | `wh_dlc05_spell_shadow_the_withering` | Armour: -30 (to enemies in range); Leadership: -8 (to enemies in range) |
| The Withering | `wh_dlc05_spell_shadow_the_withering_branchwraith` | Armour: -30 (to enemies in range); Leadership: -8 (to enemies in range) |
| The Withering Upgraded | `wh_dlc05_spell_shadow_the_withering_upgraded` | Armour: -30 (to enemies in range); Leadership: -8 (to enemies in range) |
| The Writhing Mist | `wh3_dlc27_spell_mists_the_writhing_mist` | Missile Block Chance: +30 (to self and allies); 360 Missile Block (to self and allies); Snipe (to self and allies); Stalk (to self and allies); Melee Defence: -24 (to enemies in range); Leadership: -8 (to enemies in range) |
| The Writhing Mist | `wh3_dlc27_spell_mists_the_writhing_mist_bound` | Missile Block Chance: +30 (to self and allies); 360 Missile Block (to self and allies); Snipe (to self and allies); Stalk (to self and allies); Melee Defence: -24 (to enemies in range); Leadership: -8 (to enemies in range) |
| The Writhing Mist Upgraded | `wh3_dlc27_spell_mists_the_writhing_mist_upgraded` | Missile Block Chance: +30 (to self and allies); 360 Missile Block (to self and allies); Snipe (to self and allies); Stalk (to self and allies); Melee Defence: -24 (to enemies in range); Leadership: -8 (to enemies in range) |
| Thorsen's Thunderstorm | `wh3_dlc25_cataclysm_heavens_thorsens_thunderstorm_com` | Causes massive magical damage; Huge explosion area; Large strike area; Good against armour; Strong vs multiple units |
| Thorsen's Thunderstorm | `wh3_main_cataclysm_heavens_thorsens_thunderstorm` | Causes massive magical damage; Huge explosion area; Large strike area; Good against armour; Strong vs multiple units |
| Tidecall | `wh2_dlc11_spell_deep_tidecall` | Speed: -25% |
| Tidecall Upgraded | `wh2_dlc11_spell_deep_tidecall_upgraded` | Increased armour-piercing damage; Expanding tear-shaped attack |
| Time Amok | `wh3_dlc25_cataclysm_light_time_amok_com` | Speed: +40% (to allies in range); Charge Bonus: +20% (to allies in range) |
| Time Amok | `wh3_main_cataclysm_light_time_amok` | Speed: +40% (to allies in range); Charge Bonus: +20% (to allies in range) |
| Toothcracker | `wh3_main_spell_great_maw_toothcracker` | Armour: +30 (to self and allies); Missile Resistance: +22 (to self and allies) |
| Toothcracker Upgraded | `wh3_main_spell_great_maw_toothcracker_upgraded` | Armour: +30 (to self and allies); Missile Resistance: +22 (to self and allies) |
| Traitor-Kin | `wh_dlc03_spell_wild_traitor_kin` | Speed: -25% (to enemies in range); Damage: 67 every 1s (to enemies in range) |
| Traitor-Kin Upgraded | `wh_dlc03_spell_wild_traitor_kin_upgraded` | Speed: -25% (to enemies in range); Damage: 100 every 1s (to enemies in range) |
| Transformation of Kadon | `wh2_dlc11_spell_beasts_transformation_of_kadon` | Summons a Varghulf |
| Transformation of Kadon | `wh2_dlc15_spell_beasts_transformation_of_kadon` | Summons a Great Eagle unit; Powerful unit ideal for combat; Summoned units degrade over time; Spawned unit fights in this battle only |
| Transformation of Kadon | `wh2_dlc16_army_abilities_transformation_of_kadon` | Summons a Manticore; Powerful unit ideal for combat; Summoned units degrade over time; Spawned unit fights in this battle only |
| Transformation of Kadon | `wh3_cp1_spell_beasts_transformation_of_kadon` | Summons a Celestial Lion; Powerful unit ideal for combat; Summoned units degrade over time; Spawned unit fights in this battle only |
| Transformation of Kadon | `wh_dlc03_spell_beasts_transformation_of_kadon` | Summons a Manticore; Powerful unit ideal for combat; Summoned units degrade over time; Spawned unit fights in this battle only |
| Transmutation of Lead | `wh_dlc08_spell_metal_transmutation_of_lead_kihar` | Melee Attack: -24 (to enemies in range); Base Weapon Damage: -30% (to enemies in range) |
| Transmutation of Lead | `wh_main_spell_metal_transmutation_of_lead` | Melee Attack: -24 (to enemies in range); Base Weapon Damage: -30% (to enemies in range) |
| Transmutation of Lead Upgraded | `wh_main_spell_metal_transmutation_of_lead_upgraded` | Melee Attack: -24 (to enemies in range); Base Weapon Damage: -60% (to enemies in range) |
| Treason of Tzeentch | `wh3_main_spell_tzeentch_treason_of_tzeentch` | Leadership: -16 (to enemies in range) |
| Treason of Tzeentch Upgraded | `wh3_main_spell_tzeentch_treason_of_tzeentch_upgraded` | Melee Attack: -24 (to enemies in range); Leadership: -16 (to enemies in range) |
| Trollguts | `wh3_main_spell_great_maw_trollguts` | Heals: +0.8% per tick (to self and allies) |
| Trollguts Upgraded | `wh3_main_spell_great_maw_trollguts_upgraded` | Heals: +0.8% per tick (to self and allies) |
| Tzeentch's Firestorm | `wh3_main_spell_tzeentch_tzeentchs_firestorm` | Small, randomly-moving area of effect; Three damaging rifts spreading outwards |
| Tzeentch's Firestorm Upgraded | `wh3_main_spell_tzeentch_tzeentchs_firestorm_upgraded` | Increased armour-piercing damage; Small, randomly-moving area of effect; Three damaging rifts spreading outwards |
| Urannon's Thunderbolt | `wh_main_spell_heavens_urannons_thunderbolt` | Causes major magical damage; Small strike area; Good against armour; Good against artillery pieces; Strong vs multiple combatants |
| Urannon's Thunderbolt Upgraded | `wh_main_spell_heavens_urannons_thunderbolt_upgraded` | Greater armour-piercing explosion damage; Increased armour-piercing damage; Causes major magical damage; Small strike area; Good against armour; Good against artillery pieces; Strong vs multiple combatants |
| Usekhp's Incantation of Desiccation | `wh2_dlc09_spell_nehekhara_usekhps_incantation_of_desiccation` | Melee Attack: -24 (to enemies in range); Melee Defence: -24 (to enemies in range) |
| Usekhp's Incantation of Desiccation Upgraded | `wh2_dlc09_spell_nehekhara_usekhps_incantation_of_desiccation_upgraded` | Melee Attack: -40 (to enemies in range); Melee Defence: -24 (to enemies in range) |
| Usirian's Incantation of Vengeance | `wh2_dlc09_spell_nehekhara_usirians_incantation_of_vengeance` | Speed: -25% (to enemies in range); Damage: 5 every 1s (to enemies in range) |
| Usirian's Incantation of Vengeance Upgraded | `wh2_dlc09_spell_nehekhara_usirians_incantation_of_vengeance_upgraded` | Speed: -45% (to enemies in range); Damage: 5 every 1s (to enemies in range) |
| Vangheist's Revenge | `wh2_dlc11_spell_deep_ghost_ship` | Medium, forward-moving area of effect; Strong vs multiple units; Weak vs a single combatant |
| Vangheist's Revenge Upgraded | `wh2_dlc11_spell_deep_ghost_ship_upgraded` | Increased armour-piercing damage; Medium, forward-moving area of effect; Strong vs multiple units; Weak vs a single combatant |
| Vanhel's Danse Macabre | `wh_dlc04_spell_vampires_vanhels_danse_macabre_helman` | Speed: +25% (to self and allies); Melee Attack: +24 (to self and allies) |
| Vanhel's Danse Macabre | `wh_main_spell_vampires_vanhels_danse_macabre` | Speed: +25% (to self and allies); Melee Attack: +24 (to self and allies) |
| Vanhel's Danse Macabre Upgraded | `wh_main_spell_vampires_vanhels_danse_macabre_upgraded` | Speed: +25% (to self and allies); Melee Attack: +24 (to self and allies) |
| Veil of Shadows | `wh2_dlc14_spell_stealth_veil_of_shadows` | Speed: -45%; Leadership: -8; Silenced |
| Veil of Shadows Upgraded | `wh2_dlc14_spell_stealth_veil_of_shadows_upgraded` | Added contact effect; Causes no damage; Does not affect friendly troops; Pushes enemies out of the area of effect, creating openings; Huge, stationary area of effect |
| Vengeance of Spirits | `wh3_dlc24_spell_hags_vengeance_of_spirits` | Silenced (to enemies in range); Damage: 5 every 1s (to enemies in range) |
| Vermintide | `wh2_main_spell_plague_vermintide` | Summons a unit of Clanrats; Good at defending spellcaster; Summoned units degrade over time |
| Viletide | `wh_dlc03_spell_wild_viletide` | Large explosion area; Strong vs a single unit |
| Viletide Upgraded | `wh_dlc03_spell_wild_viletide_upgraded` | Increased armour-piercing damage; Large explosion area; Strong vs a single unit |
| Vindictive Glare | `wh_main_spell_lil_waaagh_vindictive_glare` | Causes moderate magical damage; Good against large combatants; Strong vs a single combatant; Requires line of sight to the target |
| Vindictive Glare Upgraded | `wh_main_spell_lil_waaagh_vindictive_glare_upgraded` | Increased armour-piercing damage; Increased number of missiles; Causes moderate magical damage; Good against armour; Good against large combatants; Strong vs a single combatant; Requires line of sight to the target |
| Walk Between Worlds | `wh3_dlc27_spell_mists_walk_between_worlds` | Speed: +25% (to self and allies); Physical Resistance: +55 (to self and allies); Strider (to self and allies) |
| Walk Between Worlds | `wh3_dlc27_spell_mists_walk_between_worlds_upgraded` | Speed: +25% (to self and allies); Physical Resistance: +55 (to self and allies); Strider (to self and allies) |
| Wall of Wind & Fire | `wh3_main_spell_yang_wall_of_wind_and_fire` | Medium, forward-moving area of effect |
| Wall of Wind & Fire Upgraded | `wh3_main_spell_yang_wall_of_wind_and_fire_upgraded` | Increased armour-piercing damage; Medium, forward-moving area of effect |
| Warp Lightning | `wh2_main_spell_ruin_warp_lightning` | Causes moderate magical damage; Medium strike area; Good against armour; Strong vs multiple combatants; Weak vs a single combatant |
| Warp Lightning Upgraded | `wh2_main_spell_ruin_warp_lightning_upgraded` | Increased number of missiles; Causes moderate magical damage; Medium strike area; Good against armour; Strong vs multiple combatants; Weak vs a single combatant |
| Warp Stars | `wh2_dlc14_spell_stealth_warp_stars` | Causes moderate magical damage; Good against armour; Strong vs a single unit; Requires line of sight to the target |
| Warp Stars Upgraded | `wh2_dlc14_spell_stealth_warp_stars_upgraded` | Increased number of missiles; Causes moderate magical damage; Good against armour; Strong vs a single unit; Requires line of sight to the target |
| Whispers in the Woods | `wh3_dlc24_spell_hags_the_forbidden_fens_upgraded` | Charge Speed: +25% (to self and allies); Speed: +25% (to self and allies); Strider (to self and allies); Unspottable (to self and allies); Vigour per second: -1% (to self and allies) |
| Wind Blast | `wh_main_spell_heavens_wind_blast` | Expanding tear-shaped attack; Strong vs multiple units |
| Wind Blast | `wh_main_spell_heavens_wind_blast_summoned` | Spell / Winds-of-Magic / Cataclysm ability. |
| Wind Blast Upgraded | `wh_main_spell_heavens_wind_blast_upgraded` | Increased armour-piercing damage; Expanding tear-shaped attack; Strong vs multiple units; Weak vs a single combatant |
| Wind of Death | `wh_dlc04_spell_vampires_wind_of_death_helman` | Medium, forward-moving area of effect; Good against armour; Strong vs multiple units; Weak vs a single combatant |
| Wind of Death | `wh_main_spell_vampires_wind_of_death` | Medium, forward-moving area of effect; Good against armour; Strong vs multiple units; Weak vs a single combatant |
| Wind of Death Upgraded | `wh_main_spell_vampires_wind_of_death_upgraded` | Increased damage; Medium, forward-moving area of effect; Strong vs multiple units; Weak vs a single combatant |
| Witchbrew | `wh3_dlc24_spell_hags_witchbrew` | Expanding tear-shaped attack; Strong vs multiple units |
| Witchbroth | `wh3_dlc24_spell_hags_witchbrew_upgraded` | Replenishes hit points of combatants; Expanding tear-shaped attack; Strong vs multiple units |
| Wither | `wh2_main_spell_plague_wither` | Armour: -30 (to enemies in range) |
| Wither Upgraded | `wh2_main_spell_plague_wither_upgraded` | Armour: -60 (to enemies in range) |
| Word of Pain | `wh2_main_spell_dark_magic_word_of_pain` | Accuracy: -30 (to enemies in range); Melee Attack: -40 (to enemies in range) |
| Word of Pain Upgraded | `wh2_main_spell_dark_magic_word_of_pain_upgraded` | Accuracy: -30 (to enemies in range); Melee Attack: -40 (to enemies in range); Melee Defence: -24 (to enemies in range) |
| Wyssan's Wildform | `wh_dlc03_spell_beasts_wyssans_wildform` | Armour: +30 (to self and allies); Armour-Piercing Weapon Damage: +25% (to self and allies); Base Weapon Damage: +25% (to self and allies) |
| Wyssan's Wildform Upgraded | `wh_dlc03_spell_beasts_wyssans_wildform_upgraded` | Armour: +30 (to self and allies); Armour-Piercing Weapon Damage: +25% (to self and allies); Base Weapon Damage: +25% (to self and allies) |

### Vortex / wandering wind (friendly fire)  (99 abilities)

A damage vortex/wind travels the battlefield on its own path, damaging every unit it touches; no read exists to aim or time it — friendly fire is guaranteed. Family decision 2026-10-09: EXCLUDE.

| Ability | Key | Effects |
|---|---|---|
| Acid Burps | `wh3_dlc26_unit_abilities_acid_vomit` | Leaves a trail of explosions behind |
| Arnzipal's Black Horror | `wh2_dlc10_item_bound_arnizipals_black_horror` | Medium, forward-moving area of effect; Strong vs multiple units |
| Arsebelcher | `wh3_main_character_abilities_arsebelcher` | Releases a damage vortex/wind that travels the battlefield, damaging every unit it touches. |
| Asur Fire I | `wh3_dlc27_army_abilities_asuryans_rage` | Causes fire damage; Huge, stationary area of effect; Causes damage to allies; Weak vs a single combatant |
| Asur Fire II | `wh3_dlc27_army_abilities_asuryans_fury` | Causes fire damage; Huge, stationary area of effect; Causes damage to allies; Weak vs a single combatant |
| Asur Fire III | `wh3_dlc27_army_abilities_asuryans_wrath` | Causes fire damage; Huge, stationary area of effect; Causes damage to allies; Weak vs a single combatant |
| Banishment | `wh3_main_spell_bound_banishment` | Releases a damage vortex/wind that travels the battlefield, damaging every unit it touches. |
| Banishment | `wh_dlc04_spell_bound_banishment` | Huge, randomly-moving area of effect; Good against armour; Strong vs multiple units |
| Banishment | `wh_dlc04_spell_bound_banishment_innate` | Huge, randomly-moving area of effect; Good against armour; Strong vs multiple units |
| Blood-Forged Armour | `wh2_dlc15_item_abilities_blood_forged_armour` | Armour: +30 |
| Bloodbeast | `wh2_dlc17_lord_abilities_bloodbeast` | Causes fire damage; Good against armour; Strong vs a single unit |
| Bloodstorm | `wh2_dlc14_lord_abilities_bloodstorm` | Damage Resistance: +20 |
| Bound Fiery Convocation | `wh2_main_spell_bound_khaines_ring_of_fury` | Causes major magical & fire damage; Medium, forward-moving area of effect; Good against armour; Strong vs multiple units; Weak vs a single combatant |
| Burning Alignment | `wh2_dlc12_unit_abilities_burning_alignment` | Causes moderate magical & fire damage; Medium, forward-moving area of effect; Good against armour; Strong vs multiple units |
| Burning Rage | `wh3_main_lord_abilities_burning_rage` | Releases a damage vortex/wind that travels the battlefield, damaging every unit it touches. |
| Burp of Grom | `wh2_dlc15_character_abilities_burp_of_grom_0` | Releases a damage vortex/wind that travels the battlefield, damaging every unit it touches. |
| Burp of Grom | `wh2_dlc15_character_abilities_burp_of_grom_1` | Releases a damage vortex/wind that travels the battlefield, damaging every unit it touches. |
| Burp of Grom | `wh2_dlc15_character_abilities_burp_of_grom_2` | Releases a damage vortex/wind that travels the battlefield, damaging every unit it touches. |
| Daemon Flask of Ashak | `wh3_dlc23_item_abilities_daemon_flask_of_ashak` | Releases a damage vortex/wind that travels the battlefield, damaging every unit it touches. |
| Deathmaster's Sigil | `wh2_dlc14_lord_abilities_deathmasters_sigil` | Good against armour |
| Deep Tunneling | `wh3_dlc27_unit_abilities_burrow` | The Dread Maw can use this ability to quickly move through movement blockers like walls or rocks |
| Diabolical Puppetry | `wh3_pro10_army_abilities_diabolical_puppetry` | Does not affect friendly troops; Moderate, stationary area of effect; Strong vs multiple combatants; Holds entities in mid-air |
| Diabolical Puppetry | `wh3_pro10_army_abilities_diabolical_puppetry_upgrade_1` | Does not affect friendly troops; Moderate, stationary area of effect; Strong vs multiple combatants; Holds entities in mid-air |
| Diabolical Puppetry | `wh3_pro10_army_abilities_diabolical_puppetry_upgrade_2` | Does not affect friendly troops; Moderate, stationary area of effect; Strong vs multiple combatants; Holds entities in mid-air |
| Diabolical Puppetry | `wh3_pro10_army_abilities_diabolical_puppetry_upgrade_3` | Does not affect friendly troops; Moderate, stationary area of effect; Strong vs multiple combatants; Holds entities in mid-air |
| Emergency Vent | `wh2_dlc13_unit_abilities_emergency_vent` | Causes fire damage; Good against armour; Strong vs a single unit |
| Feaster of Souls | `wh3_dlc29_mount_abilities_feaster_of_souls` | Damage: 18 every 1s (to enemies in range) |
| Fiery Convocation | `wh2_dlc10_quest_abilities_magic_fiery_convocation` | Releases a damage vortex/wind that travels the battlefield, damaging every unit it touches. |
| Fiery Convocation | `wh2_dlc10_spell_bound_magic_fiery_convocation` | Causes major magical & fire damage; Medium, forward-moving area of effect; Good against armour; Strong vs multiple units; Weak vs a single combatant |
| Flame Storm | `wh2_dlc10_quest_abilities_flame_storm` | Releases a damage vortex/wind that travels the battlefield, damaging every unit it touches. |
| Flame Storm | `wh3_dlc20_spell_bound_flame_storm` | Causes major magical & fire damage; Medium, randomly-moving area of effect; Strong vs multiple units; Weak vs a single combatant |
| Flame Storm | `wh3_main_spell_bound_flame_storm` | Releases a damage vortex/wind that travels the battlefield, damaging every unit it touches. |
| Flash Bomb | `wh_pro01_lord_abilities_flash_bomb` | Charge Speed: -60% (to enemies in range); Speed: -60% (to enemies in range); Melee Defence: -24 (to enemies in range) |
| Gehenna's Golden Globe | `wh3_dlc20_cataclysm_bound_gehennas_golden_globe` | Medium, forward-moving area of effect; Strong vs multiple units; Weak vs a single combatant |
| Gehenna's Golden Globe | `wh3_dlc27_cataclysm_bound_gehennas_golden_globe` | Releases a damage vortex/wind that travels the battlefield, damaging every unit it touches. |
| Gehenna's Golden Globe | `wh3_pro10_cataclysm_metal_gehennas_golden_globe_bound` | Medium, forward-moving area of effect; Strong vs multiple units; Weak vs a single combatant |
| Gehenna's Golden Hounds | `wh3_dlc20_spell_bound_gehennas_golden_hounds` | Medium, randomly-moving area of effect; Strong vs multiple units; Weak vs a single combatant |
| Gilded Horn of Galon Konook | `wh2_main_item_bound_gilded_horn_of_galon_konook` | Medium, randomly-moving area of effect; Strong vs multiple units; Weak vs a single combatant |
| Great Invocation of Sotek | `wh2_dlc12_army_abilities_great_invocation_of_sotek` | Medium, forward-moving area of effect; Good against armour |
| Groundbreaker | `wh3_main_character_abilities_groundbreaker` | Releases a damage vortex/wind that travels the battlefield, damaging every unit it touches. |
| Guns of Zharr | `wh3_dlc23_army_abilities_guns_of_zharr` | Small, forward-moving area of effect; Good against armour |
| Heaven's Flash | `wh3_main_unit_abilities_stun_bomb` | Melee Attack: -24 (to enemies in range); Melee Defence: -24 (to enemies in range) |
| Heaven's Gate | `wh3_cp1_item_abilities_heavens_gate` | Bhashiva will teleport to the selected location within range; Bhashiva will strike enemy combatants upon arrival; Causes severe disruption to enemy formations |
| Hell Hammer | `wh3_dlc23_spell_bound_hell_hammer` | Releases a damage vortex/wind that travels the battlefield, damaging every unit it touches. |
| Hounds of Orion | `wh_dlc05_lord_ablities_grey_wolves` | Medium, randomly-moving area of effect; Strong vs multiple units; Weak vs a single combatant |
| Hurricane of Death | `wh3_dlc25_character_abilities_hurricane_of_death` | Huge, stationary area of effect; Good against armour; Strong vs multiple units |
| Inevitable Fate | `wh3_pro10_army_abilities_inevitable_fate` | Does not affect friendly troops; Causes severe disruption to enemy formations; Strong vs multiple combatants |
| Inevitable Fate | `wh3_pro10_army_abilities_inevitable_fate_upgrade_1` | Does not affect friendly troops; Causes severe disruption to enemy formations; Strong vs multiple combatants |
| Inevitable Fate | `wh3_pro10_army_abilities_inevitable_fate_upgrade_2` | Does not affect friendly troops; Causes severe disruption to enemy formations; Strong vs multiple combatants |
| Inevitable Fate | `wh3_pro10_army_abilities_inevitable_fate_upgrade_3` | Does not affect friendly troops; Causes severe disruption to enemy formations; Strong vs multiple combatants |
| Jungle Swarm | `wh2_dlc12_army_abilities_jungle_swarm` | Does not affect friendly troops; Moderate, stationary area of effect |
| Legionary Barrage | `wh2_dlc09_army_abilities_barrage_of_the_legion` | Medium, forward-moving area of effect; Good against armour; Strong vs multiple units |
| Lesser Banishment | `wh2_dlc17_spell_bound_lesser_banishment` | Huge, randomly-moving area of effect; Good against armour; Strong vs multiple units |
| Lesser Chain Lightning | `wh2_dlc17_spell_bound_lesser_chain_lightning` | Large, randomly-moving area of effect; Good against armour; Strong vs multiple units; Weak vs a single combatant |
| Man the Cannons! | `wh2_dlc13_army_abilities_amber_bow_cannons` | Small, forward-moving area of effect; Good against armour |
| Maneater Smoke Bomb | `wh3_dlc26_unit_abilities_maneater_smoke_bomb` | Speed: +25%; Melee Defence: +24; Unspottable |
| Mist Form | `wh3_dlc29_lord_abilities_mist_form` | The character will teleport to the selected location within range |
| Necrotic Explosion | `wh3_main_unit_abilities_necrotic_explosion` | Damage: 26600 every 0.2s |
| Nightmaw | `wh3_dlc27_character_abilities_nightmaw` | Small, forward-moving area of effect; Good against armour; Strong vs multiple units; Weak vs a single combatant |
| Norse Roar | `wh2_dlc11_army_abilities_norse_roar` | Causes moderate magical & fire damage; Reduce enemy leadership; Small, forward-moving area of effect; Good against armour |
| Sandstorm | `wh2_dlc09_lord_abilities_sand_storm` | Huge, randomly-moving area of effect; Good against armour |
| Seafang | `wh_dlc08_lord_abilities_seafang` | Small, forward-moving area of effect; Strong vs multiple units |
| Shadowstrider | `wh3_dlc29_lord_abilities_warp_step` | Skreech will teleport to the selected location within range; A deadly warp-beam will damage enemies upon arrival |
| Skurvy Guns | `wh3_dlc29_endgame_crisis_the_vermintide_enemy_clan_skurvy_guns_hidden` | Releases a damage vortex/wind that travels the battlefield, damaging every unit it touches. |
| Slime Smoothie | `wh2_dlc15_character_abilities_slimy_smoothie` | Heals: +1.6% per tick |
| Smoke Bomb | `wh_dlc06_unit_abilities_smoke_bomb` | Charge Speed: -60% (to enemies in range); Speed: -60% (to enemies in range) |
| Sotek's Sanctum | `wh2_dlc17_army_abilities_soteks_sanctum` | Does not affect friendly troops; Moderate, stationary area of effect |
| Soul-slaying Hunger | `wh3_dlc29_unit_abilities_soul_slaying_hunger` | Good against armour; Spawns three moving areas of effect |
| Spurting Bile-Blood | `wh3_dlc27_item_abilities_spurting_bile_blood` | Strong vs multiple combatants |
| Storm of Xholankha | `wh2_dlc13_army_abilities_storm_of_xholankha_upgraded` | Spawns six forward-moving areas of effect; Good against armour; Strong vs multiple units |
| Sword of Khaine | `wh2_dlc10_weapon_abilities_sword_of_khaine` | Huge, randomly-moving area of effect; Good against armour; Strong vs multiple units |
| Tempest of Blue Flame | `wh3_pro10_army_abilities_tempest_of_blue_flame` | Does not affect friendly troops; Huge, randomly-moving area of effect; Strong vs multiple combatants |
| Tempest of Blue Flame | `wh3_pro10_army_abilities_tempest_of_blue_flame_upgrade_1` | Does not affect friendly troops; Huge, randomly-moving area of effect; Strong vs multiple combatants; Small increase to tornado speed; Reduced amount of random movement |
| Tempest of Blue Flame | `wh3_pro10_army_abilities_tempest_of_blue_flame_upgrade_2` | Does not affect friendly troops; Huge, randomly-moving area of effect; Strong vs multiple combatants; Medium increase to tornado speed; Reduced amount of random movement |
| Tempest of Blue Flame | `wh3_pro10_army_abilities_tempest_of_blue_flame_upgrade_3` | Does not affect friendly troops; Huge, randomly-moving area of effect; Strong vs multiple combatants; Large increase to tornado speed; Reduced amount of random movement |
| The Abyssal Swarm | `wh3_dlc29_spell_bound_undeath_the_abyssal_swarm` | Does not affect friendly troops; Large, randomly-moving area of effect |
| The Burning Head | `wh3_dlc25_spell_bound_fire_the_burning_head` | Causes major magical & fire damage; Medium, forward-moving area of effect; Small, forward-moving area of effect; Strong vs multiple units |
| The Burning Head | `wh3_dlc29_spell_bound_fire_skull_of_flaming_death` | Causes major magical & fire damage; Medium, forward-moving area of effect; Small, forward-moving area of effect; Strong vs multiple units |
| The Dwellers Below | `wh3_main_spell_bound_the_dwellers_below` | Releases a damage vortex/wind that travels the battlefield, damaging every unit it touches. |
| The Dwellers Below | `wh_dlc08_spell_bound_the_dwellers_below` | Causes severe damage to combatants; Multiple, expanding areas of effect; Strong vs multiple combatants; Weak vs a single combatant |
| The Gem of Sunfire | `wh2_main_spell_bound_the_gem_of_sunfire` | Causes major magical & fire damage; Medium, randomly-moving area of effect; Strong vs multiple units; Weak vs a single combatant |
| The Matterless Earth | `wh3_dlc27_army_abilities_eternal_dance_tempo_3_carver_of_ways` | Causes armour-piercing damage; Expanding, forward-moving area of effect; Strong vs multiple units |
| The Penumbral Pendulum | `wh3_dlc20_spell_bound_the_penumbral_pendulum` | Small, forward-moving area of effect; Strong vs multiple units; Weak vs a single combatant |
| The Purple Eclipse | `wh3_dlc25_army_abilities_purple_eclipse` | Releases a damage vortex/wind that travels the battlefield, damaging every unit it touches. |
| The Purple Sun of Xereus | `wh2_dlc11_spell_bound_the_purple_sun_of_xereus` | Huge, randomly-moving area of effect; Good against armour; Strong vs multiple units |
| The Ruination of Cities | `wh2_main_lord_abilities_the_ruination_of_cities` | Three damaging rifts spreading outwards; Strong vs multiple units; Random launch directions; Weak vs a single combatant |
| The Solid Airs | `wh3_dlc27_army_abilities_eternal_dance_tempo_3_tempest_of_depravity` | Huge, stationary area of effect; Large explosion area; Strong vs multiple units |
| Thunder Charge | `wh3_main_army_abilities_thunder_charge` | Releases a damage vortex/wind that travels the battlefield, damaging every unit it touches. |
| Tyrant's Talon | `wh3_cp1_weapon_abilities_tyrants_talon` | Melee Attack: +24; Armour-Piercing Weapon Damage: +25%; Base Weapon Damage: +25%; Imbuement: Brutal Wounds! |
| Verminous Valour | `wh2_main_character_abilities_verminous_valour` | Speed: +25%; Leadership: +8 |
| Violent Wind | `wh3_dlc20_unit_abilities_violent_wind` | Releases a damage vortex/wind that travels the battlefield, damaging every unit it touches. |
| Wall of Wind & Fire | `wh3_main_spell_bound_wall_of_wind_and_fire` | Medium, forward-moving area of effect |
| Whirl of Weeping Blades | `wh2_dlc14_weapon_abilities_whirl_of_weeping_blades` | Huge, stationary area of effect; Good against armour; Strong vs multiple units |
| Whirlwind of Pleasure | `wh3_dlc27_lord_abilities_whirlwind_of_pleasure` | Good against armour; Strong vs multiple combatants; Weak vs a single combatant |
| Wind of Death | `wh2_dlc15_spell_bound_wind_of_death` | Medium, forward-moving area of effect; Good against armour; Strong vs multiple units; Weak vs a single combatant |
| Wrath of Manann | `wh_dlc07_item_abilities_wrath_of_manann` | Medium, forward-moving area of effect; Good against armour; Strong vs multiple units |
| Wrath of Zharr | `wh3_dlc23_army_abilities_wrath_of_zharr` | Small, forward-moving area of effect; Good against armour |
| Zhufbar 42-Pounders | `wh2_dlc11_army_abilities_zhufbar_42_pounders` | Small, forward-moving area of effect; Good against armour |
| Zhufbar 42-Pounders | `wh2_dlc17_army_abilities_zhufbar_42_pounders_engineer` | Small, forward-moving area of effect; Good against armour |

### Army-bar ability  (99 abilities)

Belongs to the ARMY BAR, not a unit's own dial; excluded by standing rule 10 (“Skip all army bar abilities”).

| Ability | Key | Effects |
|---|---|---|
| A Joyous Deliquescence | `wh3_dlc27_army_abilities_eternal_dance_tempo_3_denial_of_death` | Invulnerable (to self and allies) |
| Ancestral Rune of Valaya | `wh2_dlc17_army_abilities_ancestral_rune_of_valaya` | Vigour per second: -10% (to allies in range); Heals: +1.6% per tick (to allies in range) |
| Ancestral Warriors | `wh3_main_army_abilities_ancestral_warriors` | Summons a unit of Ancestral Warriors; Summoned units degrade over time |
| Apotheosis | `wh3_dlc27_army_high_magic_apotheosis` | Can Cause Fear (to self and allies); Heals: +0.8% per tick (to self and allies) |
| Arcane Surge | `wh3_main_army_abilities_arcane_surge` | Power Recharge: +80% (to allies in range); Reserves Per Second: +0.15 (to allies in range) |
| Beasts of Itzl | `wh2_dlc13_army_abilities_beasts_of_itzl` | Summons a Razordon Hunting Pack; Powerful unit ideal for combat; Summoned units degrade over time; Spawned unit fights in this battle only |
| Beasts of Itzl | `wh2_dlc13_army_abilities_beasts_of_itzl_upgraded` | Summons a Razordon Hunting Pack; Powerful unit ideal for combat; Summoned units degrade over time; Spawned unit fights in this battle only |
| Blood & Fireborn | `wh3_dlc23_lord_abilities_blood_and_fireborn` | Summons a unit of K'daai Fireborn; Summoned units degrade over time |
| Blood God's Shackles | `wh3_dlc26_army_abilities_blood_gods_shackles` | Melee Defence: -24 (to enemies in range) |
| Blood God's Shackles Upgraded | `wh3_dlc26_army_abilities_blood_gods_shackles_upgraded` | Melee Defence: -40 (to enemies in range) |
| Call of the Wild | `wh3_dlc25_army_abilities_call_of_the_wild` | Summons an Incarnate Elemental of Beasts; Powerful unit ideal for combat; Spawned unit fights in this battle only |
| Call the Miners | `wh3_dlc25_army_abilities_summon_miners` | Summons a unit of Miners (Blasting Charges) |
| Call to Ceithin-Har | `wh2_dlc16_army_abilities_call_to_ceithin_har` | Summons Ceithin-Har |
| Channelling Spire | `wh2_main_army_abilities_channeling_spire` | Power Recharge: +80% (to allies in range); Reserves Per Second: +0.10 (to allies in range) |
| Clanrats Below | `wh3_dlc29_endgame_crisis_the_vermintide_the_menace_below_hidden` | Army-bar ability (cast from the army bar). |
| Curse of the Slug | `wh3_main_army_abilities_curse_of_the_slug` | Charge Speed: -45% (to enemies in range); Speed: -45% (to enemies in range) |
| Cut da Chainz | `wh3_dlc26_army_abilities_cut_da_chains` | Summons a Feral Wyvern; Powerful unit ideal for combat; Summoned units degrade over time; Spawned unit fights in this battle only |
| Dark Conduit | `wh2_main_army_abilities_dark_conduit` | Vigour per second: +100% (to allies in range); Ability recharge: +90s (to allies in range) |
| Dismember | `wh3_main_prisoners_dismember` | Speed: -60% (to enemies in range); Damage: 3 every 1s (to enemies in range) |
| Eagle Sanctuary | `wh2_main_army_abilities_eagle_sanctuary` | Summons a Great Eagle unit; Powerful unit ideal for combat; Spawned unit fights in this battle only |
| Engineer's Gyrocopter Bomb | `wh3_dlc25_army_abilities_gyrocopter_bomb` | Army-bar ability (cast from the army bar). |
| Fascination | `wh3_main_army_abilities_fascination` | Rampage! (to enemies in range); Damage: 10 every 1s (to enemies in range) |
| Fecundity | `wh3_main_army_abilities_fecundity` | Vigour per second: -1% (to allies in range); Heals: +0.8% per tick (to allies in range) |
| Feral Cold Ones | `wh2_main_army_abilities_feral_cold_ones` | Summons a unit of Feral Cold Ones; Powerful unit ideal for combat; Summoned units degrade over time; Spawned unit fights in this battle only |
| Feral Cold Ones | `wh2_main_army_abilities_feral_cold_ones_qb_scripted` | Army-bar ability (cast from the army bar). |
| Frozen on the Pyre | `wh3_dlc27_army_abilities_eternal_dance_tempo_3_submission_to_the_prince` | Armour: -60 (to enemies in range); Melee Defence: -40 (to enemies in range); Removes Expert Charge Defence (to enemies in range); Removes Charge Defence vs Large (to enemies in range) |
| Geomantic Nexus | `wh2_main_army_abilities_geomantic_nexus` | Summons a Skink Priest; Magical unit that can cast spells; Summoned units degrade over time; Spawned unit fights in this battle only |
| Gluttony | `wh3_main_army_abilities_gluttony` | Heals: +1% per tick (to allies in range) |
| Hand of Glory | `wh3_dlc27_army_high_magic_hand_of_glory` | Melee Attack: +24 (to self and allies); Reload Skill: +60 (to self and allies) |
| Holy Stela | `wh2_main_army_abilities_holy_stela` | Base Missile Damage: -25% (to enemies in range); Accuracy: -30 (to enemies in range) |
| Iron Reinforcements | `wh3_cp1_army_abilities_tiger_warrior_reinforcements` | Summons a unit of Iron Claw Tiger Warriors; Summoned units degrade over time |
| Launch Gyrocopters | `wh3_dlc25_army_abilities_launch_gyrocopters` | Summons a unit of Gyrocopters; Summoned units degrade over time |
| Lure of the Pale Queen | `wh2_main_army_abilities_lure_of_the_pale_queen` | Army-bar ability (cast from the army bar). |
| Mislead | `wh2_dlc14_final_battle_ability_summon_snikch` | Army-bar ability (cast from the army bar). |
| Moulder Clanstone | `wh2_main_army_abilities_moulder_clanstone` | Heals: +0.8% per tick (to allies in range) |
| Murderous Libations | `wh3_dlc27_army_abilities_eternal_dance_tempo_3_nectar_of_the_daemonette` | Melee Attack: +36 (to self and allies); Armour-Piercing Weapon Damage: +75% (to self and allies); Base Weapon Damage: +75% (to self and allies); Melee Defence: +36 (to self and allies); Unbreakable (to self and allies); Heals: +1.5% per tick (to self and allies) |
| Narcissism | `wh3_main_army_abilities_narcissism` | Silenced (to enemies in range) |
| Oblast Outriders | `wh3_main_abilities_call_horse_archers` | Summons a unit of Horse Archers; Causes no damage; Does not affect friendly troops; Short, wide, expanding, tear-shaped attack |
| ph | `wh2_main_army_abilities_carnosaur_qb_scripted` | Army-bar ability (cast from the army bar). |
| ph | `wh2_main_army_abilities_stegadon_qb_scripted` | Army-bar ability (cast from the army bar). |
| Plague Monks Below | `wh3_dlc29_endgame_crisis_the_vermintide_pestilent_birth_hidden` | Army-bar ability (cast from the army bar). |
| Protection of Quetzl | `wh2_dlc13_army_abilities_protection_of_quetzl` | Invulnerable (to self and allies); Unbreakable (to self and allies) |
| Protection of Quetzl | `wh2_dlc13_army_abilities_protection_of_quetzl_upgraded` | Invulnerable (to self and allies); Unbreakable (to self and allies) |
| Rat Ogres Below | `wh3_dlc29_endgame_crisis_the_vermintide_beast_pack_hidden` | Army-bar ability (cast from the army bar). |
| Realm of Souls Ushabti | `wh2_dlc09_army_abilities_realm_of_souls_ushabti` | Unlocks when the Realm of Souls is full; Summons a unit of Ushabti; Good at melee combat; Summoned units degrade over time |
| Relentless Rage | `wh3_main_army_abilities_relentless_rage` | Cannot Die (to allies in range); Unbreakable (to allies in range); Unyielding Assault (to allies in range) |
| Rot, Glorious Rot | `wh3_main_army_abilities_rot_glorious_rot` | Damage: 5 every 1s (to enemies in range) |
| Roused to Wrath | `wh2_dlc16_lord_abilities_roused_to_wrath_3` | Summons a unit of Malevolent Dryads |
| Ryze: Crypt Horrors | `wh3_dlc29_army_abilities_ryze_the_grave_call_crypt_horrors` | Summons a unit of Crypt Horrors; Summoned units degrade over time |
| Ryze: Grave Guard | `wh3_dlc29_army_abilities_ryze_the_grave_call_grave_guard` | {{tr:unit_abilities_additional_ui_effects_localised_text_wh_dlc04_all_summon_graveguard}}; Summoned units degrade over time |
| Ryze: Grave Guard Upgraded | `wh3_dlc29_army_abilities_ryze_the_grave_call_grave_guard_endless` | Summoned unit will not degrade until the end of the battle.; {{tr:unit_abilities_additional_ui_effects_localised_text_wh_dlc04_all_summon_graveguard}} |
| Ryze: Khemrian Warsphinx | `wh3_dlc29_army_abilities_ryze_the_grave_call_khemrian_warsphinx` | Summons a Khemrian Warsphinx; Summoned units degrade over time |
| Ryze: Khemric Titan | `wh3_dlc29_army_abilities_ryze_the_grave_call_khemric_titan` | Summons a Khemric Titan; Summoned units degrade over time |
| Ryze: Khemric Titan Upgraded | `wh3_dlc29_army_abilities_ryze_the_grave_call_khemric_titan_endless` | Summoned unit will not degrade until the end of the battle.; Summons a Khemric Titan |
| Ryze: Mournguls | `wh3_dlc29_army_abilities_ryze_the_grave_call_mournguls` | Summons a unit of Mournguls; Summoned units degrade over time |
| Ryze: Necrofex Colossus | `wh3_dlc29_army_abilities_ryze_the_grave_call_necrofex_colossus` | Summons a Necrofex Colossus; Summoned units degrade over time |
| Ryze: Nehekharan Warriors | `wh3_dlc29_army_abilities_ryze_the_grave_call_nehekharan_warriors` | Summons a unit of Nehekharan Warriors; Summoned units degrade over time |
| Ryze: Rotting Prometheans (Gunnery Mob) | `wh3_dlc29_army_abilities_ryze_the_grave_call_rotting_prometheans_gunnery_mob` | Summons a unit of Rotting Prometheans (Gunnery Mob); Summoned units degrade over time |
| Ryze: Rotting Prometheans (Gunnery Mob) Upgraded | `wh3_dlc29_army_abilities_ryze_the_grave_call_rotting_prometheans_gunnery_mob_endless` | Summoned unit will not degrade until the end of the battle.; Summons a unit of Rotting Prometheans (Gunnery Mob) |
| Ryze: Spirit Host | `wh3_dlc29_army_abilities_ryze_the_grave_call_spirit_host` | Summons a unit of Spirit Host; Summoned units degrade over time |
| Ryze: Terrorgheist | `wh3_dlc29_army_abilities_ryze_the_grave_call_terrorgheist` | Summons a Terrorgheist; Summoned units degrade over time |
| Ryze: Ushabti | `wh3_dlc29_army_abilities_ryze_the_grave_call_ushabti` | Summons a unit of Ushabti; Summoned units degrade over time |
| Ryze: Zombie Pirate Gunnery Mob (Bombers) | `wh3_dlc29_army_abilities_ryze_the_grave_call_zombie_pirate_gunnery_mob_bombers` | Summons a unit of Zombie Pirate Gunnery Mob (Bombers); Summoned units degrade over time |
| Scruten Clanstone | `wh3_dlc29_army_abilities_scruten_clanstone` | Missile Resistance: +60 (to allies in range) |
| Shamanistic Ritual (Death) | `wh3_dlc27_army_abilities_sayl_manipulations_spawn_shaman_death` | Summons a Shaman Sorcerer; Magical unit that can cast spells; Has access to empowered spells; Summoned units degrade over time |
| Shamanistic Ritual (Fire) | `wh3_dlc27_army_abilities_sayl_manipulations_spawn_shaman_fire` | Summons a Shaman Sorcerer; Magical unit that can cast spells; Has access to empowered spells; Summoned units degrade over time |
| Shamanistic Ritual (Metal) | `wh3_dlc27_army_abilities_sayl_manipulations_spawn_shaman_metal` | Summons a Shaman Sorcerer; Magical unit that can cast spells; Has access to empowered spells; Summoned units degrade over time |
| Shield of the Old Ones | `wh2_dlc13_final_battle_abilities_shield_of_the_old_ones` | Leadership: +8 (to self and allies); Damage Resistance: +20 (to self and allies) |
| Ships of the Line | `wh3_dlc27_army_abilities_ships_of_the_line` | Replenishes ammunition (to allies in range) |
| Skryre Clanstone | `wh2_main_army_abilities_skryre_clanstone` | Spell Resistance: -44 (to enemies in range) |
| Spirit of Grungni | `wh3_dlc25_army_abilities_spirit_of_grungni` | Summons the Spirit of Grungni (Thunderbarge); Summoned units degrade over time |
| Stormvermin Below | `wh3_dlc29_endgame_crisis_the_vermintide_stormvermin_menace_below_hidden` | Army-bar ability (cast from the army bar). |
| Summon Plague Drones | `wh3_dlc29_army_abilities_rotborne_summon_plague_drones` | Summons a unit of Plague Drones; Powerful unit ideal for combat; Summoned units degrade over time |
| Summon Plague Drones (Death's heads) | `wh3_dlc29_army_abilities_rotborne_summon_plague_drones_1` | Summons a unit of Plague Drones (Death's Heads); Powerful unit ideal for combat; Summoned units degrade over time |
| Summon the Sentinels | `wh2_dlc15_army_abilities_summon_the_sentinels` | Causes no damage; Does not affect friendly troops; Summons a unit of Sentinels of Astaril; Short, wide, expanding, tear-shaped attack |
| Summon the Sentinels Upgraded | `wh2_dlc15_army_abilities_summon_the_sentinels_upgraded` | Does not affect friendly troops; Summons a unit of Sentinels of Astaril; Short, wide, expanding, tear-shaped attack; Strong vs multiple units |
| Summoned from Beyond | `wh3_main_army_abilities_summoned_from_beyond_daemon_prince` | Summons a unit of Chaos Furies; Summoned units degrade over time |
| Summoned from Beyond | `wh3_main_army_abilities_summoned_from_beyond_khorne` | Summons a unit of Bloodletters; Summoned units degrade over time |
| Summoned from Beyond | `wh3_main_army_abilities_summoned_from_beyond_nurgle` | Summons a unit of Plaguebearers; Summoned units degrade over time |
| Summoned from Beyond | `wh3_main_army_abilities_summoned_from_beyond_slaanesh` | Summons a unit of Daemonettes; Summoned units degrade over time |
| Summoned from Beyond | `wh3_main_army_abilities_summoned_from_beyond_tzeentch` | Summons a unit of Pink Horrors; Summoned units degrade over time |
| Sweet Sorrow | `wh3_main_army_abilities_sweet_sorrow` | Charge Speed: +40% (to allies in range); Speed: +40% (to allies in range); Vigour per second: -4% (to allies in range) |
| Temple of Mists | `wh2_main_army_abilities_temple_of_mists` | Base Missile Damage: -25% (to enemies in range); Accuracy: -30 (to enemies in range) |
| The Bitter End | `wh3_dlc27_army_abilities_eternal_dance_tempo_3_poisonous_aroma` | Damage: 100 every 1s (to enemies in range); Executes below 20% HP (to enemies in range) |
| The Bitterness of Winter | `wh3_main_army_abilities_the_bitterness_of_winter` | Speed: -25% (to enemies in range); Leadership: -8 (to enemies in range); Vigour per second: +1% (to enemies in range) |
| The Effulgent Incense | `wh3_dlc27_army_abilities_eternal_dance_tempo_3_path_of_indulgence` | Vigour per second: -1% (to self and allies); Heals: +0.8% per tick (to self and allies) |
| The Land Awakened | `wh3_main_army_abilities_the_land_awakened` | Summons an Elemental Bear |
| The Menace Below | `wh2_dlc29_army_abilities_the_menace_below_qb` | Army-bar ability (cast from the army bar). |
| The Menace Below | `wh2_main_army_abilities_the_menace_below` | Summons a unit of Clanrats; Summoned units degrade over time |
| The Menace Below (Stormvermin) | `wh3_dlc29_army_abilities_stormvermin_menace_below` | Summons a unit of Stormvermin; Summoned units degrade over time |
| Titanic Exultation | `wh3_dlc27_army_abilities_decadence_in_praise_of_sla_i` | Summons a Giant Chaos Spawn of Slaanesh; Summoned units degrade over time |
| Touched by the Moon | `wh2_dlc17_army_abilities_touched_by_the_moon` | Melee Attack: +40 (to allies in range); Armour-Piercing Weapon Damage: +50% (to allies in range); Base Weapon Damage: +50% (to allies in range); Physical Resistance: +40 (to allies in range); Unbreakable (to allies in range); Damage: 1500 every 0.2s (to allies in range) |
| Tzcatli's Sanctum | `wh2_dlc17_army_abilities_tzcatlis_sanctum` | Summons a unit of Chameleon Stalkers |
| Unleash | `wh3_dlc29_army_abilities_unleash` | Summons a unit of {{tr:land_units_onscreen_name_wh2_main_skv_mon_hell_pit_abomination}}; Summoned units degrade over time |
| Unleash the Winds | `wh2_dlc15_army_abilities_unleash_the_winds` | Miscast Chance: +100% (to allies in range); Power Recharge: +320% (to allies in range); Reserves Per Second: +0.40 (to allies in range); Ability recharge: -30s (to allies in range) |
| Vortical Enrichment | `wh2_main_army_abilities_vortic_enrichment` | Creates healing burst from source; Explosion does not affect friendly troops; Powerful explosion |
| War Supplies | `wh3_dlc27_army_abilities_war_supplies` | Replenishes ammunition (to allies in range) |
| Warpbomb | `wh2_main_army_abilities_warpbomb` | Powerful explosion; Sacrifice a weak unit to destroy foes |
| Wrath of the Bear | `wh3_main_army_abilities_wrath_of_the_bear` | Armour-Piercing Weapon Damage: +50% (to allies in range); Base Weapon Damage: +50% (to allies in range) |

### Summon  (74 abilities)

Summons new units; not auto-fireable under the standing scope rules.

| Ability | Key | Effects |
|---|---|---|
| Ancestral Vengeance | `wh3_dlc23_item_abilities_ancestral_vengeance` | Summons a unit of K'daai Fireborn; Summoned units degrade over time |
| Ancestral Warriors | `wh3_main_spell_bound_ancestral_warriors` | Summons a unit of Ancestral Warriors; Summoned units degrade over time |
| Arachnarok Eggs | `wh_dlc08_item_abilities_arachnarok_eggs` | Summons a unit of Spider Hatchlings; Good at defending the summoner; Summoned units degrade over time |
| Beast Pack | `wh2_dlc16_lord_abilities_beast_pack` | Summons a unit of Rat Ogres; Summoned units degrade over time |
| Beyond the Realm | `wh2_dlc11_character_abilities_beyond_the_realm` | Summons a unit of Damned Knights of the Realm; Summoned units degrade over time |
| Blacktoof's Conjuration | `wh2_dlc15_item_abilities_blacktoofs_conjuration` | Summons a Rogue Idol; Summoned units degrade over time |
| Burrow | `wh3_dlc27_unit_abilities_dread_maw_underground` | The Dread Maw will burrow underground; Cannot be targeted and will be able to move like a normal unit; It will not be able to make melee or ranged attacks |
| Call of the Shadow Dancer | `wh2_dlc10_lord_abilities_deadly_mislead` | Snipe; Stalk; Unspottable |
| Call to Ceithin-Har | `wh2_dlc16_lord_abilities_call_to_ceithin_har` | Summons Ceithin-Har |
| Call to Gwindalor | `wh2_dlc16_lord_abilities_call_to_gwindalor` | Summons Gwindalor |
| Captain Roth's Moondial | `wh2_dlc11_item_abilities_captain_roths_moondial` | Summons a unit of Zombie Pirate Deckhands Mob; Summoned units degrade over time |
| Children of the Forest | `wh3_dlc25_character_abilities_children_of_the_forest` | Summons a unit of Giant Spiders |
| Deceiving Shadows | `wh3_dlc24_lord_item_deceiving_shadows` | Spell Mastery: +25%; Snipe; Stalk; Unspottable |
| Doppelgang | `wh2_dlc14_unit_abilities_doppelgang` | Unspottable |
| Dreaming Cloak I | `wh2_dlc16_item_abilities_dreaming_cloak_i` | Summons a unit of Glade Guard |
| Dreaming Cloak II | `wh2_dlc16_item_abilities_dreaming_cloak_ii` | Summons a unit of Deepwood Scouts |
| Dreaming Cloak III | `wh2_dlc16_item_abilities_dreaming_cloak_iii` | Summons a unit of Waywatchers |
| Eye of Khorne | `wh3_dlc26_lord_abilities_eye_of_khorne` | Damage: 2660 every 1s (to enemies in range) |
| Gate of Chaos | `wh3_main_daemon_arms_abilities_gate_of_chaos` | Summons a unit of Blue Horrors; Summoned units degrade over time |
| Gate of Chaos Upgraded | `wh3_main_daemon_arms_abilities_gate_of_chaos_upgraded` | Summons a Lord of Change; Summoned units degrade over time |
| Gate of Tzeentch | `wh3_main_character_abilities_gate_of_tzeentch` | Summons a unit of Pink Horrors; Summoned units degrade over time |
| Ghosts of the Past | `wh2_dlc11_character_abilities_ghosts_of_the_past_0` | Summons a unit of Damned Knights Errant; Summoned units degrade over time |
| Ghosts of the Past | `wh2_dlc11_character_abilities_ghosts_of_the_past_1` | Summons a unit of Damned Knights Errant; Summoned units degrade over time |
| Ghosts of the Past | `wh2_dlc11_character_abilities_ghosts_of_the_past_2` | Summons a unit of Damned Knights Errant; Summoned units degrade over time |
| Gorger Onslaught | `wh3_main_lord_abilities_gorger_onslaught` | Summons a unit of Gorgers; Summoned units degrade over time |
| Gorger Onslaught Upgraded | `wh3_dlc26_lord_abilities_gorger_onslaught_upgraded` | Summons a unit of Gorgers |
| Guardian Call | `wh3_main_character_abilities_guardian_call` | Summons a Snow Leopard; Summoned units degrade over time |
| Guardian Call II | `wh3_main_character_abilities_guardian_call_ii` | Summons a Snow Leopard; Summoned unit has increased melee attack and melee defence; Summoned units degrade over time |
| Guardian Call III | `wh3_main_character_abilities_guardian_call_iii` | Summons a Snow Leopard; Summoned unit has greatly increased melee attack and melee defence; Summoned units degrade over time |
| Guardian of the Forest | `wh3_dlc25_character_abilities_guardian_of_the_forest` | Summons an Arachnarok Spider |
| Horn of the Ancestors | `wh2_dlc10_item_abilities_horn_of_the_ancestors` | Summons an Ancestral spirit; Summoned units degrade over time |
| Inventory of Hatchlings | `wh3_dlc26_character_abilities_inventory_of_hatchlings` | Summons a unit of Spider Hatchlings; Good at defending the summoner; Summoned units degrade over time |
| Inventory of Hatchlings Upgraded | `wh3_dlc26_character_abilities_inventory_of_hatchlings_upgraded` | Summons a unit of Spider Hatchlings; Good at defending the summoner; Summoned units will not degrade |
| Invocation of the Lichemaster | `wh3_dlc29_character_abilities_invocation_of_the_lichemaster` | Summons a unit of Cairn Wraiths |
| Invocation of the Lichemaster | `wh3_dlc29_character_abilities_invocation_of_the_lichemaster_0` | Summons a unit of Cairn Wraiths; Cairn Wraiths have increased melee attack and charge bonus; Cairn Wraiths will degrade at half speed |
| Invocation of the Lichemaster | `wh3_dlc29_character_abilities_invocation_of_the_lichemaster_1` | Summons a unit of Cairn Wraiths; Cairn Wraiths have increased melee attack and charge bonus; Cairn Wraiths will not degrade |
| Kettle's Call | `wh3_dlc25_character_abilities_kettles_call` | Summons a unit of Giant Hawks; Powerful unit ideal for combat; Spawned unit fights in this battle only |
| Koldunja's Spirit | `wh3_dlc24_hero_abilities_koldunjas_spirit` | Summons a unit of Things in the Woods; Summoned units degrade over time |
| Lesser Raise Dead | `wh2_dlc16_spell_bound_vampires_lesser_raise_dead` | Summons a unit of Zombies; Good at defending spellcaster; Summoned units degrade over time |
| Locus of Transmogrification | `wh3_main_character_abilities_locus_of_transmogrification` | Summons a unit of Blue Horrors; Summoned units degrade over time |
| Lord of Undeath | `wh_pro03_lord_abilities_lord_of_undeath` | Summons Krell; Summoned units degrade over time |
| Lord of Undeath | `wh_pro03_lord_abilities_lord_of_undeath_0` | Summons Krell; Krell will degrade at half-speed; Summoned units degrade over time |
| Lord of Undeath | `wh_pro03_lord_abilities_lord_of_undeath_1` | Summons Krell; Krell will degrade at half-speed; Summoned units degrade over time |
| Lord of Undeath | `wh_pro03_lord_abilities_lord_of_undeath_2` | Summons Krell; Krell will degrade at half-speed; Summoned units degrade over time |
| Lord of Undeath | `wh_pro03_lord_abilities_lord_of_undeath_3` | Summons Krell; Krell will not degrade |
| Lord of Undeath | `wh_pro03_lord_abilities_lord_of_undeath_4` | Krell's combat power is greatly enhanced; Summons Krell; Krell will not degrade |
| Mask of the Merlord | `wh3_dlc27_item_abilities_mask_of_the_merlord` | Summons a Merwyrm |
| Master of Souls | `wh_dlc08_quest_abilities_master_of_souls` | Summons a unit of Skeletons |
| Maternal Instinct | `wh_dlc06_unit_abilities_maternal_instinct` | Summons a unit of Spider Hatchlings; Good at defending the summoner; Summoned units degrade over time |
| Mislead | `wh2_dlc10_lord_abilities_mislead` | Snipe; Stalk; Unspottable |
| Nurgling Birth | `wh3_dlc29_hero_active_nurgling_birth` | Summons a unit of Nurglings; Summoned units degrade over time |
| Nurgling Birth Upgraded | `wh3_dlc29_hero_active_nurgling_birth_upgraded` | Summons a unit of Nurglings; Summoned units will not degrade |
| Nurgling Tide | `wh3_main_lord_abilities_nurgling_tide` | Summons a unit of Infested Nurglings; Summoned unit can self-destruct in an explosion; Summoned units degrade over time |
| Ritual of the Beast | `wh3_dlc24_item_abilities_ritual_of_the_beast` | Summons an Elemental Incarnate of Beasts; Summoned units degrade over time |
| Roused to Wrath | `wh2_dlc16_lord_abilities_roused_to_wrath` | Summons a unit of Malevolent Dryads; Summoned units degrade over time |
| Roused to Wrath | `wh2_dlc16_lord_abilities_roused_to_wrath_2` | Summons a unit of Malevolent Dryads |
| Sacrilege | `wh2_dlc11_character_abilities_sacrilege` | Summons a unit of Damned Questing Knights; Summoned units degrade over time |
| Savage Dominion | `wh2_dlc17_spell_bound_savage_dominion` | Summons a Cygor; Summoned units degrade over time |
| Savage Predators | `wh3_dlc26_hero_abilities_savage_predators` | Summons a unit of Sabretusk Pack |
| Servants of Nagash | `wh_dlc04_quest_abilities_servant_of_nagash` | Damage: 266 every 1s (to self and allies) |
| Spinning Loons | `wh_main_unit_abilities_spinning_loons` | Causes armour-piercing damage; Small moving area of effect; Strong vs multiple units; Weak vs a single combatant; Unpredictable release from unit |
| Squig Thinkin' | `wh3_dlc26_character_abilities_squig_thinkin` | Summons a Squig Herd unit; Summoned units degrade over time |
| Stave of Ruinous Corruption | `wh_dlc05_weapon_abilities_stave_of_ruinous_corruption` | Summons a unit of Chaos Spawn; Good at melee combat; Summoned units degrade over time |
| Surface | `wh3_dlc27_unit_abilities_dread_maw_surface` | The Dread Maw will surface from underground; Can make both melee and ranged attacks; It will become attackable and will not be able to move normally |
| Surprise Squig! | `wh3_dlc25_character_abilities_surprise_squig` | Summons an Explosive Squig |
| Sword of Change | `wh_dlc01_weapon_abilities_sword_of_change` | Summons a unit of Chaos Spawn; Summoned units degrade over time |
| The Awakening | `wh3_dlc29_lord_abilities_the_awakening` | Summons a larger unit of Skeleton Warriors |
| The Loons of Eight Peaks | `wh_dlc06_unit_abilities_the_loons_of_eight_peaks` | Causes armour-piercing damage; Small moving area of effect; Strong vs multiple units; Weak vs a single combatant; Unpredictable release from unit |
| The Tomb Blade of Arkhan | `wh2_dlc09_weapon_abilities_tomb_blade_of_arkhan` | Summons a larger unit of Skeleton Warriors; Good at defending spellcaster; Summoned units degrade over time |
| Tide of Death | `wh2_dlc16_hero_abilities_tide_of_death` | Summons a unit of Wolf Rats; Summoned units degrade over time |
| Tide of Pox | `wh2_dlc16_hero_abilities_tide_of_pox` | Summons a unit of Wolf Rats (Poison); Summoned units degrade over time |
| Undeath to All | `wh3_dlc29_lord_abilities_raise_legion` | Summons a larger unit of Zombies; Summoned units degrade over time |
| Undeath to All Upgraded | `wh3_dlc29_lord_abilities_raise_legion_upgraded` | Summons a larger unit of Skeleton Warriors; Summoned units degrade over time |
| Wake Da Idol | `wh3_main_item_abilities_zak_aloooog` | Summons a Rogue Idol; Summoned units degrade over time |

### Bombardment / ground artillery (friendly fire)  (63 abilities)

A strike is called down on a chosen ground point; placing it usefully needs an enemy read the engine lacks — blind placement lands on your own line. Family decision 2026-10-09: EXCLUDE.

| Ability | Key | Effects |
|---|---|---|
| Ancestral Rune of Grimnir | `wh2_dlc17_army_abilities_ancestral_rune_of_grimnir` | Large strike area; Good against armour; Strong vs multiple units |
| Arachneruption | `wh2_dlc15_unit_abilities_arachneruption` | Bombards the area around the caster; Most effective when surrounded; Ignores armour |
| Assault of Stone | `wh2_dlc10_item_bound_assault_of_stone` | Causes major magical damage; Medium strike area; Strong vs a single unit; Weak vs a single combatant |
| Axe of Tor | `wh3_main_weapon_abilities_axe_of_tor` | Medium strike area |
| Bjuna Bombard | `wh3_dlc25_army_abilities_bjuna_bombard` | Damage: 5 every 1s |
| Bloodwrack Cauldron | `wh2_main_army_abilities_bloodwrack_cauldron` | Good armour-piercing damage & explosion damage; Good damage & explosion damage; Causes magical damage; Strong vs multiple units; Weak vs a single combatant |
| Bonecrusher | `wh3_dlc26_spell_bound_bonecrusher` | Small strike area |
| Brazen Cauldron | `wh2_main_army_abilities_brazen_cauldron` | Good armour-piercing damage; Good damage; Causes magical damage; Strong vs multiple units; Weak vs a single combatant |
| Bubonic Broadside | `wh3_dlc29_army_abilities_pestilential_bombardment` | Explosion damages enemies within range |
| Celestial Comet | `wh3_main_mount_bound_celestial_comet` | Calls a strike down on a chosen ground point. |
| Celestial Intervention | `wh3_main_army_abilities_celestial_intervention` | Calls a strike down on a chosen ground point. |
| Celestial Lightning | `wh3_main_mount_bound_celestial_lightning` | Calls a strike down on a chosen ground point. |
| Chalice of Potions | `wh_dlc07_item_abilities_chalice_of_potions` | Causes massive magical damage; Huge explosion area; Large strike area; Good against armour; Strong vs multiple units |
| Comet of Casandora | `wh3_main_spell_bound_comet_of_casandora` | Calls a strike down on a chosen ground point. |
| Doom Diver Strike | `wh2_dlc15_army_abilities_doom_diver_strike` | Medium strike area; Strong vs a single unit; Weak vs a single combatant |
| Doom of Hashut | `wh3_dlc23_army_abilities_doom_of_hashut` | Causes major magical & fire damage; Strong vs multiple units; Weak vs a single combatant |
| Doomrocket | `wh3_dlc29_endgame_crisis_the_vermintide_enemy_clan_skryre_doomrocket_hidden` | Calls a strike down on a chosen ground point. |
| Dragon Ogre's Great Horn | `wh_dlc08_item_abilities_great_horn_of_dragon_ogre` | Causes magical damage; Small strike area; Strong vs multiple combatants; Weak vs a single combatant |
| Dragonship Assault | `wh3_dlc27_army_abilities_dragonship_assault` | Good damage; Medium strike area; Good against armour |
| Dragonship Blitz | `wh3_dlc27_army_abilities_dragonship_blitz` | Good damage; Large strike area; Good against armour |
| Dragonship Volley | `wh3_dlc27_army_abilities_dragonship_volley` | Good damage; Small strike area; Good against armour |
| Dreadquake Battery | `wh3_dlc23_army_abilities_tower_ballistics` | Large explosion area; Good against armour; Explosion damages enemies within range |
| Dreadquake Battery Upgraded | `wh3_dlc23_army_abilities_tower_ballistics_upgraded_toz` | Large explosion area; Good against armour; Explosion damages enemies within range |
| Flame & Shadow | `wh3_dlc23_lord_abilities_flame_and_shadow` | Causes moderate magical & fire damage; Strong vs multiple units; Weak vs a single combatant |
| Fly at da Smoke! | `wh3_dlc26_army_abilities_fly_at_da_smoke` | Medium strike area; Strong vs a single unit; Weak vs a single combatant |
| Hawk's Talon | `wh_dlc05_weapon_abilities_hawks_talon` | Causes moderate magical damage; Medium strike area; Good against armour; Strong vs a single unit; Weak vs a single combatant |
| Isha's Rain | `wh2_dlc13_character_ability_ishas_rain` | Causes moderate magical damage; Medium strike area; Strong vs multiple combatants; Enemies hit by the bombardment are slowed for a short time; Weak vs a single combatant |
| Khaine's Flail | `wh2_main_army_abilities_khaines_flail` | Two bolts of magical lightning; Small strike area; Good against artillery pieces; Strong vs multiple combatants; Weak vs a single combatant |
| Khaine's Lash | `wh2_main_army_abilities_khaines_lash` | A single bolt of magical lightning; Small strike area; Good against artillery pieces; Strong vs multiple combatants; Weak vs a single combatant |
| Khaine's Scourge | `wh2_main_army_abilities_khaines_scourge` | Three bolts of magical lightning; Small strike area; Good against artillery pieces; Strong vs multiple combatants; Weak vs a single combatant |
| Klad Brakak | `wh2_dlc17_spell_bound_urannons_thunderbolt_upgraded` | Causes major magical damage; Small strike area; Good against armour; Good against artillery pieces; Strong vs multiple combatants |
| Lightning Strike | `wh3_dlc29_unit_abilities_lightning_strike` | Calls a strike down on a chosen ground point. |
| Lord of the Storm | `wh_main_lord_abilities_lord_of_the_storm` | Causes magical damage; Small strike area; Strong vs multiple combatants; Weak vs a single combatant |
| Master of Lightning | `wh3_dlc29_spell_bound_warp_lightning` | Causes moderate magical damage; Medium strike area; Good against armour; Strong vs multiple combatants; Weak vs a single combatant |
| Master Rune of Immolation | `wh2_dlc17_rune_abilities_master_rune_of_immolation` | Bombards the area around the caster; Most effective when surrounded; Ignores armour |
| Meteor Strike | `wh3_dlc29_unit_abilities_meteor_strike` | Calls a strike down on a chosen ground point. |
| Nemesis Crown | `wh3_dlc25_lord_abilities_nemesis_crown` | Causes moderate magical damage; Medium strike area; Strong vs a single unit; Can cause damage to friendly combatants |
| Pandemicium | `wh3_dlc25_army_abilities_pandemicium` | Calls a strike down on a chosen ground point. |
| Piercing Bolts of Burning | `wh_main_spell_bound_piercing_bolts_of_burning` | Causes major magical & fire damage; Medium strike area; Good against armour; Strong vs a single unit |
| Pigeon Bomb | `wh3_dlc25_character_abilities_pigeon_bomb` | Medium strike area; Strong vs a single unit; Weak vs a single combatant |
| Rod of the Storm | `wh2_dlc11_army_abilities_rod_of_the_storm` | Causes massive magical damage; Small strike area; Good against armour; Good against artillery pieces; Strong vs multiple combatants |
| Rod of the Storm | `wh2_main_spell_bound_rod_of_the_storm` | Causes major magical damage; Small strike area; Good against armour; Good against artillery pieces; Strong vs multiple combatants |
| Sceptre of Stone | `wh2_dlc10_item_abilities_sceptre_of_stone` | Causes major magical damage; Medium strike area; Strong vs a single unit; Weak vs a single combatant |
| Searing Doom | `wh3_twa08_spell_bound_searing_doom` | Causes moderate magical damage; Medium strike area; Strong vs a single unit; Weak vs a single combatant |
| Sky Cauldron | `wh2_main_army_abilities_sky_cauldron` | Causes magical damage; Strong vs multiple units; Weak vs a single combatant |
| Slicing Shards | `wh3_dlc20_spell_bound_slicing_shards` | Large strike area |
| Soul Rain | `wh2_main_army_abilities_soul_rain` | A small cluster of magical souls; Large strike area; Strong vs a single unit; Weak vs a single combatant |
| Soul Storm | `wh2_main_army_abilities_soul_storm` | A huge cluster of magical souls; Large strike area; Strong vs a single unit; Weak vs a single combatant |
| Soul Torrent | `wh2_main_army_abilities_soul_torrent` | A large cluster of magical souls; Large strike area; Strong vs a single unit; Weak vs a single combatant |
| Storm of Fire | `wh3_main_army_abilities_storm_of_fire` | Large strike area |
| The Bow of Loren | `wh_dlc05_weapon_abilities_the_bow_of_loren` | Causes magical damage; Large strike area; Strong vs a single unit; Weak vs a single combatant |
| The Dreaded Thirteenth Spell | `wh3_dlc29_spell_bound_the_dreaded_thirteenth` | Summons a unit of Stormvermin; Huge explosion area; Strong vs multiple units; Summoned units degrade over time |
| The Dreaded Thirteenth Spell | `wh3_dlc29_spell_bound_the_dreaded_thirteenth_1` | Summons a unit of Stormvermin; Huge explosion area; Strong vs multiple units; Summoned units degrade over time |
| The Dreaded Thirteenth Spell | `wh3_dlc29_spell_bound_the_dreaded_thirteenth_thanquol` | Summons a unit of Stormvermin; Huge explosion area; Strong vs multiple units; Summoned units degrade over time |
| The Dreaded Thirteenth Spell | `wh3_dlc29_spell_bound_the_dreaded_thirteenth_thanquol_1` | Summons a unit of Stormvermin; Huge explosion area; Strong vs multiple units; Summoned units degrade over time |
| Thorsen's Thunderstorm | `wh3_dlc20_cataclysm_bound_thorsens_thunderstorm` | Causes massive magical damage; Huge explosion area; Large strike area; Good against armour; Strong vs multiple units |
| Thorsen's Thunderstorm | `wh3_dlc27_cataclysm_bound_thorsens_thunderstorm` | Calls a strike down on a chosen ground point. |
| Urannon's Thunderbolt | `wh2_dlc17_spell_bound_urannons_thunderbolt` | Causes major magical damage; Small strike area; Good against armour; Good against artillery pieces; Strong vs multiple combatants |
| Warp Lightning Rod | `wh2_dlc16_unit_abilities_warp_lightning_rod` | Bombards the area around the unit; Bombardment also damages allies; Causes moderate magical damage; Medium strike area; Good against armour; Strong vs multiple combatants; Weak vs a single combatant |
| Warpstorm Doomrocket | `wh2_dlc12_army_abilities_warpstorm_doomrocket` | Damage: 5 every 1s |
| Warpstorm Doomrocket | `wh2_dlc12_army_abilities_warpstorm_doomrocket_upgraded` | Good armour-piercing damage & explosion damage; Good damage & explosion damage; Causes damage to combatants; Causes magical damage; Strong vs multiple units; Weak vs a single combatant |
| Warpstorm Doomrocket | `wh3_dlc24_tze_changeling_theatre_scheme_grand_cathay_doom_rocket` | Calls a strike down on a chosen ground point. |
| Xapati's Sanctum | `wh2_dlc17_army_abilities_xapatis_sanctum` | Small strike area; Strong vs a single combatant; Weak vs a single unit |

### Explosive projectile (friendly fire)  (52 abilities)

An explosive projectile that can catch nearby friendly units; excluded under the friendly-fire rules.

| Ability | Key | Effects |
|---|---|---|
| Arrow of Kurnous | `wh_dlc05_hero_abilities_arrow_of_kurnous` | Causes armour-piercing damage; Effective at long range |
| Bellow of Endless Fury | `wh3_main_lord_abilities_bellow_of_endless_fury` | Fires an explosive projectile. |
| Bellow of Fury | `wh3_main_lord_abilities_bellow_of_fury` | Fires an explosive projectile. |
| Big Boom | `wh2_dlc13_character_abilities_big_boom` | Causes damage to combatants; Requires line of sight to the target |
| Bilespurt | `wh3_dlc29_hero_active_bilespurter` | Large explosion area; Good against armour; Inaccurate at short range |
| Blast | `wh2_dlc10_item_bound_blast` | Causes moderate magical & fire damage; Good against armour; Effective at close range; Good penetration; Requires line of sight to the target |
| Bolt Storm | `wh3_main_weapon_abilities_nuku_chos_crossbow` | Fires an explosive projectile. |
| Bomb-Throw | `wh2_dlc11_hero_abilities_bomb_throw` | Armour-Piercing Missile Damage: +20%; Damage: 5 every 1s |
| Bow of the Seafarer | `wh2_main_weapon_abilities_bow_of_the_seafarer` | Causes magical damage; Good against large combatants; Strong vs a single combatant; Poor penetration; Requires line of sight to the target |
| Cackle Fruit | `wh2_dlc11_character_abilities_cackle_fruit` | Speed: -45% |
| Cinderblast Cluster Bomb | `wh3_dlc25_lord_abilities_cinderblast_cluster_bomb` | Causes fire damage; Powerful explosion; Strong vs multiple combatants |
| Cinderblast Shell | `wh2_dlc17_hero_abilities_cinderblast_shell` | Causes fire damage; Powerful explosion; Strong vs multiple combatants |
| Copious Vomit | `wh_dlc08_lord_abilities_copious_vomit` | Powerful explosion; Good against armour; Strong vs a single unit |
| Coruscating Blast | `wh3_dlc25_unit_abilities_coruscating_blast` | Powerful explosion; Strong vs a single combatant |
| Cracklebomb | `wh2_dlc14_character_abilities_cracklebomb` | Causes magical & fire damage; Powerful explosion; Requires line of sight to the target |
| Crippling Throw | `wh3_main_character_abilities_crippling_throw` | Speed: -25%; Melee Defence: -24 |
| Dark Fire of Chaos | `wh2_main_unit_abilities_dark_fire_of_chaos` | Causes fire damage; Powerful explosion; Good against armour; Good against large combatants; Strong vs a single unit |
| Death Shriek | `wh2_main_unit_abilities_death_shriek` | Causes magical damage; Powerful explosion; Good against armour; Strong vs a single unit |
| Doomrocket | `wh2_main_hero_abilities_doomrocket` | Splits into multiple projectiles mid-air; Causes magical & fire damage; Strong vs multiple combatants; Effective at long range; Weak vs a single combatant; Requires line of sight to the target |
| Elemental Breath | `wh3_main_unit_abilities_elemental_breath` | Requires line of sight to the target |
| Experimental Explosive | `wh3_dlc25_weapon_abilities_experimental_explosive` | Powerful explosion; Requires line of sight to the target |
| Fiery Breath | `wh2_main_unit_abilities_fiery_breath` | Causes fire damage; Powerful explosion; Strong vs a single unit; Weak vs a single combatant |
| Fire Breath | `wh3_main_character_abilities_fire_breath` | Requires line of sight to the target |
| Flaming Breath | `wh3_dlc23_unit_abilities_flaming_breath` | Causes fire damage; Good against armour; Strong vs multiple units |
| Flaming Breath | `wh3_dlc27_unit_abilities_flaming_breath` | Causes fire damage; Good against armour; Strong vs multiple units |
| Frost Breath | `wh2_dlc10_unit_abilities_frost_breath` | Powerful explosion; Strong vs a single unit; Weak vs a single combatant; Requires line of sight to the target |
| Frost Breath | `wh2_dlc10_unit_abilities_frost_wyrm_breath` | Powerful explosion; Strong vs a single unit; Weak vs a single combatant |
| Gordinar's Dragon Breath | `wh2_dlc15_unit_abilities_sun_dragon_breath_imrik` | Causes fire damage; Powerful explosion; Strong vs a single unit; Weak vs a single combatant |
| Hunting Spear | `wh_dlc03_weapon_abilities_hunting_spear` | Causes armour-piercing damage; Effective at all ranges; Good penetration |
| Ice Breath | `wh3_dlc24_unit_abilities_ice_breath` | Fires an explosive projectile. |
| Ice Shard | `wh3_main_character_abilities_ice_shard` | Requires line of sight to the target |
| Lamentation of Despairs | `wh_dlc05_lord_abilities_lamentation_of_despair` | Causes armour-piercing damage; Strong vs a single unit; Weak vs a single combatant; Strikes any combatants in its path |
| Lamentation of Despairs (Empowered) | `wh3_dlc29_lord_abilities_lamentation_of_despair_upgraded` | Causes armour-piercing damage; Strong vs a single unit; Weak vs a single combatant; Strikes any combatants in its path |
| Master Rune of Flight | `wh2_dlc17_rune_abilities_master_rune_of_flight` | Causes moderate magical & fire damage; Good against armour; Effective at close range; Good penetration |
| Moon Dragon's Breath | `wh2_main_unit_abilities_moon_dragons_breath` | Causes fire damage; Powerful explosion; Good against large combatants; Strong vs a single unit |
| Noxious Breath | `wh2_main_unit_abilities_noxious_breath` | Powerful explosion; Strong vs a single unit |
| Pestilent Torrent | `wh3_dlc29_lord_active_pestilent_torrent` | Good against armour; Strong vs multiple units |
| Pestilential Breath | `wh2_main_unit_abilities_pestilential_breath` | Powerful explosion; Good against large combatants; Strong vs a single unit |
| Pyromaniac | `wh2_dlc11_character_abilities_pyromaniac` | Damage: 5 every 1s |
| Reaver Bow | `wh2_main_weapon_bound_reaver_bow` | Large area of effect; Powerful explosion; Strong vs multiple units; Weak vs a single combatant; Requires line of sight to the target |
| Shackolot's Noxious Breath | `wh2_dlc15_unit_abilities_noxious_breath_imrik` | Reduce enemy leadership; Powerful explosion; Strong vs a single unit |
| Skarsnik's Prodder | `wh_dlc06_weapon_abilities_skarsniks_prodder` | Shoots shrapnel on impact; Powerful explosion; Strong vs multiple combatants; Effective at long range; Weak vs multiple units; Requires line of sight to the target |
| Soporific Breath | `wh2_main_unit_abilities_soporific_breath` | Powerful explosion; Good against large combatants; Strong vs a single unit |
| Star Dragon's Breath | `wh2_main_unit_abilities_star_dragons_breath` | Causes fire damage; Powerful explosion; Good against armour; Good against large combatants |
| Storm Daemon | `wh2_dlc12_weapon_abilities_storm_daemon` | Causes major magical damage; Good against armour; Effective at all ranges; Good penetration; Requires line of sight to the target |
| Sun Dragon's Breath | `wh2_main_unit_abilities_sun_dragons_breath` | Causes fire damage; Powerful explosion; Strong vs a single unit; Weak vs a single combatant |
| The Amber Spear | `wh_dlc03_spell_bound_the_amber_spear` | Causes moderate magical damage; Good against armour; Effective at all ranges; Good penetration |
| The Moonbow | `wh2_dlc10_weapon_abilities_the_moonbow` | Causes armour-piercing damage; Powerful explosion; Strong vs a single unit; Effective at long range; Requires line of sight to the target |
| The Venom Staff | `wh2_dlc09_weapon_abilities_venom_staff` | Shoots shrapnel on impact; Strong vs multiple units; Effective at long range; Weak vs a single combatant |
| Unspeakable Foulness | `wh3_dlc25_unit_abilities_unspeakable_foulness` | Fires an explosive projectile. |
| Volley of Dark Arrows | `wh2_main_character_abilities_volley_of_dark_arrows` | Causes armour-piercing damage; Effective at long range; Good penetration; Requires line of sight to the target |
| Volley of High Arrows | `wh2_main_character_abilities_volley_of_high_arrows` | Causes armour-piercing damage; Effective at long range; Good penetration; Requires line of sight to the target |

### Placed / static area damage (friendly fire)  (42 abilities)

A static area-damage field centred on a point (often self); no enemy read to place it, and a self-centred field hits friendlies. Family decision 2026-10-09: EXCLUDE.

| Ability | Key | Effects |
|---|---|---|
| Acorns of the Oak of Ages | `wh2_dlc16_item_abilities_acorns_of_the_oak_of_ages` | Causes armour-piercing damage; Large explosion area |
| Arcane Vassal | `wh2_main_character_abilities_arcane_vassal` | Creates magical burst from source; Explosion does not affect friendly troops; Weak vs a single combatant |
| Befuddlement of Mischiefs | `wh2_dlc16_character_abilities_befuddlement_of_mischiefs` | Places a static area-damage field centred on a point. |
| Blade of Khorne | `wh3_main_army_abilities_blade_of_khorne` | Huge explosion area |
| Blight Boil | `wh3_dlc29_endgame_crisis_the_vermintide_enemy_clan_morbidus_pestilent_pustule_hidden` | Places a static area-damage field centred on a point. |
| Blight Boil | `wh3_main_item_abilities_deaths_head` | Huge explosion area |
| Boiling Cauldron | `wh3_dlc26_army_abilities_boiling_cauldron` | Huge, stationary area of effect; Good against armour; Strong vs multiple units |
| Boiling Cauldron | `wh3_dlc26_lord_abilities_boiling_cauldron` | Huge, stationary area of effect; Good against armour; Strong vs multiple units |
| Brass Orb | `wh2_dlc12_character_abilities_brass_orb` | Damage: 5 every 1s |
| Brass Orb | `wh2_dlc12_character_abilities_brass_orb_tech_lab_doom_flayer` | Huge, stationary area of effect; Good against armour; Strong vs multiple units |
| Brass Orb Upgraded | `wh2_dlc12_character_abilities_brass_orb_upgrade` | Damage: 5 every 1s (to enemies in range) |
| Chain Lightning | `wh_main_spell_bound_chain_lightning_ror` | Large, randomly-moving area of effect; Good against armour; Strong vs multiple units; Weak vs a single combatant |
| Copious Phlegm | `wh3_dlc27_qb_unit_abilities_copious_phlegm` | Huge explosion area |
| Crackleblaze | `wh3_main_item_abilities_crackleblaze` | Places a static area-damage field centred on a point. |
| Foot of Gork | `wh3_dlc26_army_abilities_da_plan_foot_of_gork` | Huge explosion area; Strong vs multiple units; Weak vs a single combatant |
| Frost Fang | `wh3_main_weapon_abilities_frost_fang` | Places a static area-damage field centred on a point. |
| Infernal Gateway | `wh3_dlc20_spell_bound_infernal_gateway` | Huge, stationary area of effect |
| Invocation of Ending | `wh2_dlc15_army_abilities_invocation_of_ending` | Ability recharge: +30s (to enemies in range) |
| Irresistible Plague! | `wh3_dlc29_spell_bound_plague` | Places a static area-damage field centred on a point. |
| Lamprey's Bite | `wh3_dlc24_unit_abilities_lampreys_bite` | Places a static area-damage field centred on a point. |
| Magma Storm | `wh3_dlc20_cataclysm_bound_magma_storm` | Causes major magical damage; Medium strike area; Good against armour; Strong vs a single unit |
| Magma Storm | `wh3_dlc27_cataclysm_bound_magma_storm` | Places a static area-damage field centred on a point. |
| Magma Storm | `wh3_pro10_cataclysm_fire_magma_storm_bound` | Causes major magical damage; Medium strike area; Good against armour; Strong vs a single unit |
| Master Rune of Wrath & Ruin | `wh_dlc06_rune_abilities_master_rune_of_wrath_and_ruin` | Charge Speed: -60%; Speed: -60% |
| Pit of Shades | `wh3_dlc27_spell_bound_pit_of_shades` | Places a static area-damage field centred on a point. |
| Pit of Shades | `wh3_main_spell_bound_pit_of_shades` | Places a static area-damage field centred on a point. |
| Pit of Shades | `wh_dlc05_spell_shadow_pit_of_shades_bound` | Huge, stationary area of effect; Good against armour; Strong vs multiple units |
| Plaguemaster | `wh3_dlc29_spell_bound_plaguemaster` | Large, expanding area of effect; Good against armour; Strong vs multiple units; Weak vs a single combatant |
| Rubric of Dark Dimensions | `wh2_main_spell_bound_rubric_of_dark_dimensions` | Huge explosion area; Good against armour; Strong vs multiple units |
| Rune of Wrath & Ruin | `wh_main_rune_abilities_rune_of_wrath_and_ruin` | Charge Speed: -60%; Speed: -60% |
| Shatterstone | `wh2_dlc17_army_abilities_shatterstone` | Powerful explosion; Affects city walls and siege equipment; Siege battles may be launched instantly |
| Siegebreaker | `wh3_main_weapon_abilities_siegebreaker` | Powerful explosion; Destroys buildings and siege vehicles |
| Simmering Pot | `wh3_dlc26_lord_abilities_simmering_pot` | Huge, stationary area of effect; Good against armour; Strong vs multiple units |
| Stoneshaker | `wh3_main_army_abilities_stoneshaker` | Destroys buildings and siege vehicles |
| The Hammer of Smednir | `wh3_dlc23_item_abilities_hammer_of_smednir` | Charge Speed: -60%; Speed: -60% |
| Vaul's Hammer | `wh2_main_army_abilities_vauls_hammer` | Powerful explosion; Affects city walls and siege equipment; Siege battles may be launched instantly |
| Vile Entropy | `wh2_dlc17_army_abilities_vile_entropy` | Range: -50% (to enemies in range) |
| Viletide | `wh_dlc03_spell_bound_viletide` | Large explosion area; Strong vs a single unit |
| Viletide Upgraded | `wh2_dlc17_army_abilities_viletide` | Large explosion area; Strong vs a single unit |
| Vortical Blast | `wh2_main_army_abilities_vortic_blast` | Creates magical burst from source; Powerful explosion |
| Warp Junction | `wh3_dlc29_lord_abilities_warp_junction` | After use, the vortex emits an explosion.; Huge, stationary area of effect; Good against armour; Strong vs multiple units |
| Winged Staff | `wh2_main_weapon_bound_winged_staff` | Damage: 5 every 1s (to enemies in range) |

### Breath / cone damage (friendly fire)  (30 abilities)

A forward cone of damage from the caster; the cone sweeps friendly units in the arc. Family decision 2026-10-09: EXCLUDE.

| Ability | Key | Effects |
|---|---|---|
| Bangstick | `wh3_main_item_abilities_bangstick` | Powerful explosion |
| Black Dragon Egg | `wh2_main_item_abilities_black_dragon_egg` | Long, thin, expanding, tear-shaped attack; Good against armour; Strong vs multiple units |
| Blue Fire of Chaos | `wh3_main_daemon_arms_abilities_blue_fire` | Expanding tear-shaped attack; Poor penetration |
| Blue Fire of Chaos Upgraded | `wh3_main_daemon_arms_abilities_blue_fire_upgraded` | Increased damage; Good against large combatants; Poor penetration |
| Da Boss' Loons | `wh2_dlc15_lord_abilities_da_boss_loons` | Causes armour-piercing damage; Small moving area of effect; Strong vs multiple units; Weak vs a single combatant; Unpredictable release from unit |
| Disembowelling Sweep | `wh3_dlc29_unit_active_ripping_blades` | Breathes a forward cone of damage. |
| Fiery Ring of Thori | `wh_main_item_abilities_fiery_ring_of_thori` | Causes major magical & fire damage; Long, thin, expanding, tear-shaped attack; Strong vs multiple units |
| Fishy Breath | `wh2_dlc15_character_abilities_fishy_breathe` | Expanding tear-shaped attack; Strong vs multiple units |
| Flesh-eating Scarabs | `wh3_dlc29_unit_abilities_flesh_eating_scarabs` | Causes armour-piercing damage; Reduce enemy leadership; Is activated at melee range |
| Gaze of Malice | `wh2_main_lord_abilities_gaze_of_malice` | Short, wide, expanding, tear-shaped attack; Strong vs multiple units |
| Jade Lion's Breath | `wh3_dlc24_unit_abilities_jade_dragons_breath` | Breathes a forward cone of damage. |
| Kovsh Breath | `wh3_main_item_abilities_kovsh_breath` | Short, wide, expanding, tear-shaped attack |
| Lash of Slaanesh | `wh3_dlc27_spell_bound_lash_of_slaanesh` | Breathes a forward cone of damage. |
| Lash of Slaanesh | `wh3_main_spell_bound_lash_of_slaanesh` | Expanding tear-shaped attack |
| Lash of Slaanesh | `wh3_main_spell_bound_lash_of_slaanesh_keeper_of_secrets` | Breathes a forward cone of damage. |
| Pestilent Breath | `wh2_main_mount_bound_pestilent_breath` | Expanding tear-shaped attack; Strong vs multiple units |
| Pestilent Breath | `wh3_main_spell_bound_pestilent_breath` | Breathes a forward cone of damage. |
| Pink Fire of Tzeentch | `wh3_dlc20_spell_bound_pink_fire_of_tzeentch` | Long, thin, expanding, tear-shaped attack |
| Pink Fire of Tzeentch | `wh3_main_spell_tzeentch_pink_fire_of_tzeentch_bound` | Breathes a forward cone of damage. |
| Sartosa Grapeshot | `wh2_dlc11_army_abilities_sartosa_grapeshot` | Long, thin, expanding, tear-shaped attack; Strong vs multiple units; Weak vs a single combatant |
| Scorch | `wh2_main_mount_bound_scorch` | Causes major magical & fire damage; Long, thin, expanding, tear-shaped attack; Strong vs multiple units; Weak vs a single combatant |
| Shadows of Anlec | `wh2_main_army_abilities_shadows_of_anlec` | Causes magical & fire damage; Expanding tear-shaped attack; Strong vs multiple units; Weak vs a single combatant |
| Shatter | `wh2_dlc13_character_ability_shatter` | Causes damage to combatants; Causes severe damage to combatants; Strong vs a single combatant; Strong vs multiple units; Weak vs a single combatant |
| Skabscrath | `wh_main_weapon_abilities_skabscrath` | Causes major magical & fire damage; Long, thin, expanding, tear-shaped attack; Strong vs multiple units |
| Stream of Corruption | `wh3_dlc20_spell_bound_stream_of_corruption` | Long, thin, expanding, tear-shaped attack |
| Stream of Corruption | `wh3_main_spell_nurgle_stream_of_corruption_bound` | Breathes a forward cone of damage. |
| Sunfang | `wh2_main_weapon_abilities_sunfang` | Causes major magical & fire damage; Expanding tear-shaped attack; Strong vs multiple units; Weak vs a single combatant |
| The Spear Slaupnir | `wh3_dlc20_weapon_abilities_the_spear_slaupnir` | Small, forward-moving area of effect; Strong vs multiple units; Weak vs a single combatant |
| Tidecall | `wh2_dlc11_spell_bound_tidecall` | Breathes a forward cone of damage. |
| Wind Blast | `wh2_dlc11_spell_bound_wind_blast` | Expanding tear-shaped attack; Strong vs multiple units |

### Explosive / breath attack (friendly fire)  (29 abilities)

A damage cone/explosion; the arc sweeps friendly units with no way to check it is clear. Family decision: EXCLUDE.

| Ability | Key | Effects |
|---|---|---|
| Ancient Chaos Frost Dragon Scale | `wh_dlc08_item_abilities_ancient_frost_wyrm_scale` | Large, moving area of effect; Weak vs a single combatant |
| Breath of the Hydra | `wh2_dlc10_quest_abilities_fiery_head` | Explosive / breath attack. |
| Death from Above | `wh2_dlc09_unit_abilities_death_from_above` | Large strike area; Strong vs multiple combatants; Weak vs a single combatant |
| Drop Rocks | `wh2_dlc12_unit_abilities_drop_rocks_character` | Small strike area; Strong vs multiple combatants; Weak vs a single combatant |
| Drop Rocks | `wh2_main_unit_abilities_drop_rocks` | Small strike area; Strong vs multiple combatants; Weak vs a single combatant |
| Drop Rocks of Chotec | `wh2_dlc12_unit_abilities_drop_rocks_of_chotec` | Small strike area; Strong vs multiple combatants; Weak vs a single combatant |
| Drop Rocks of Sundering | `wh2_dlc12_unit_abilities_drop_rocks_of_sundering` | Small strike area; Strong vs multiple combatants; Weak vs a single combatant |
| Drop Sphere of Tepok | `wh2_dlc12_lord_abilities_drop_sphere_of_tepok` | Speed: -60% |
| Drop Sphere of Tepok Upgraded | `wh2_dlc12_lord_abilities_drop_sphere_of_tepok_upgraded` | Small strike area; Strong vs multiple combatants; Enemies hit by explosion are slowed (30s); Weak vs a single combatant |
| Emberstorm | `wh2_dlc15_unit_abilities_emberstorm` | Causes major magical & fire damage; Moderate, stationary area of effect |
| Eye of Rejuvenation | `wh2_dlc10_quest_abilities_regenerating_head` | Heals: +100% per tick (to self and allies) |
| Fire Bombs | `wh3_dlc25_unit_abilities_gyrobomber_fire_bomb` | Leaves a pool of fire on strike zone; Powerful explosion; Strong vs multiple combatants; Weak vs a single combatant |
| Fire Bombs | `wh3_dlc25_unit_abilities_thunderbarge_fire_bomb` | Leaves a pool of fire on strike zone; Powerful explosion; Strong vs multiple combatants; Weak vs a single combatant |
| Gyrobomber Bomb | `wh_main_unit_abilities_gyrobomber_bomb` | Small strike area; Powerful explosion; Strong vs multiple combatants; Weak vs a single combatant |
| Gyrocopter Bomb | `wh_main_unit_abilities_gyrocopter_bomb` | Small strike area; Powerful explosion; Strong vs multiple combatants; Weak vs a single combatant |
| Gyrocopter Bomb (Trollhammer) | `wh3_dlc25_unit_abilities_gyrocopter_bomb_anti_large` | Small strike area; Powerful explosion; Good against large combatants; Strong vs multiple combatants |
| Howling Winter | `wh_dlc08_quest_abilities_howling_winter` | Large, moving area of effect; Weak vs a single combatant |
| Land Mine | `wh3_dlc25_unit_abilities_marienburg_land_mines` | Small strike area; Powerful explosion; Strong vs multiple combatants; Weak vs a single combatant |
| Moon Flare | `wh3_dlc24_unit_abilities_moon_flare` | Explosive / breath attack. |
| Nan-Gau Grenades | `wh3_dlc24_unit_abilities_nan_gau_grenades` | Small strike area; Powerful explosion; Strong vs multiple combatants; Weak vs a single combatant |
| Searing Torrent | `wh3_twa07_unit_abilities_searing_torrent` | Small strike area; Strong vs multiple combatants; Weak vs a single combatant |
| Sky-Junk Bomb | `wh3_main_unit_abilities_sky_junk_bomb` | Explosive / breath attack. |
| Skyhammer Bomb | `wh_dlc06_unit_abilities_skyhammer_bomb` | Large strike area; Powerful explosion; Strong vs multiple combatants; Weak vs a single combatant |
| Skyhammer Fire Bomb | `wh_dlc06_unit_abilities_skyhammer_fire_bomb` | Leaves a pool of fire on strike zone; Large strike area; Powerful explosion; Strong vs multiple combatants |
| Slann Gold | `wh2_dlc11_item_abilities_slann_gold` | Power Recharge: -80% (to enemies in range) |
| Song of Enthrallment | `wh2_dlc11_lord_abilities_song_of_enthrallment` | Speed: -45% (to enemies in range); Melee Attack: -24 (to enemies in range) |
| Undeath from Above | `wh3_dlc29_unit_abilities_undeath_from_above` | Large strike area; Strong vs multiple combatants; Weak vs a single combatant |
| Unidentified Hydra Head | `wh2_dlc10_quest_abilities_unidentified_hydra_head` | Flame Resistance: +80; Heals: +0.8% per tick |
| Wake of Fire | `wh2_main_unit_abilities_wake_of_fire` | Small strike area; Powerful explosion; Strong vs multiple combatants; Weak vs a single combatant |

### Own-troop-damage AoE (friendly fire by design)  (26 abilities)

The ability deliberately damages your own units as part of its effect (self-nova / sacrifice AoE). Family decision 2026-10-09: EXCLUDE.

| Ability | Key | Effects |
|---|---|---|
| Ashes & Dust | `wh3_dlc20_cataclysm_bound_ashes_and_dust` | Damage: 25 every 1s (to enemies in range); Damage: 500 every 1s (to enemies in range) |
| Ashes & Dust | `wh3_dlc27_cataclysm_bound_ashes_and_dust` | Damage: 25 every 1s (to enemies in range); Damage: 500 every 1s (to enemies in range) |
| Defiling Deluge | `wh3_twa08_unit_abilities_defiling_deluge` | Damage: 5 every 1s (to enemies in range); Heals: +0.8% per tick |
| Descent Into Dissolution | `wh3_dlc27_army_abilities_eternal_dance_tempo_3_jesters_laughter` | Charge Bonus: -50% (to enemies in range); Rampage! (to enemies in range); Damage: 6 every 1s (to enemies in range) |
| Eshin Clanstone | `wh2_main_army_abilities_eshin_clanstone` | Damage: 5 every 1s (to enemies in range) |
| Flock of Doom | `wh3_dlc27_spell_bound_runecaller_flock_of_doom` | Damage: 5 every 1s (to enemies in range) |
| Flock of Doom | `wh3_main_spell_bound_flock_of_doom` | Damage: 5 every 1s (to enemies in range) |
| Flock of Doom | `wh_dlc08_spell_bound_flock_of_doom` | Damage: 5 every 1s (to enemies in range) |
| Gust of the Grave | `wh3_dlc29_unit_abilities_lesser_tomb_swarm` | Damage: 4 every 1s (to enemies in range) |
| Murderous Exhortations | `wh3_dlc26_lord_abilities_murderous_exhortations` | Leadership: -8 (to enemies in range); Damage: 5 every 1s (to enemies in range) |
| Plaguereaper | `wh3_dlc29_item_abilities_plaguereaper` | Damage: 12 every 1s (to enemies in range); Heals: +0.8% per tick |
| Raging Tornado | `wh3_dlc29_unit_abilities_raging_tornado` | Speed: -10% (to enemies in range); Damage: 2 every 1s (to enemies in range); Speed: -25% (to enemies in range); Damage: 4 every 1s (to enemies in range); Speed: -40% (to enemies in range); Damage: 6 every 1s (to enemies in range); Speed: -60% (to enemies in range); Damage: 8 every 1s (to enemies in range) |
| Reaper of Souls | `wh2_dlc14_lord_abilities_reaper_of_souls` | Damage: 96 every 1s (to enemies in range); Heals: +0.8% per tick |
| Ring of Corin | `wh2_main_spell_bound_ring_of_corin` | Damage: 67 every 1s (to enemies in range); Ability recharge: +30s (to enemies in range) |
| Rod of Corruption | `wh2_main_item_abilities_rod_of_corruption` | Damage: 10 every 1s (to enemies in range) |
| Shard Blade | `wh3_main_weapon_abilities_shard_blade` | Speed: -45% (to enemies in range); Damage: 67 every 1s (to enemies in range) |
| Soul Stealer | `wh2_dlc10_spell_bound_soul_stealer_ror` | Damage: 75 every 1s (to enemies in range); Heals: +0.8% per tick |
| Soul Stealer | `wh3_dlc27_spell_bound_soul_stealer` | Damage: 75 every 1s (to enemies in range); Heals: +0.8% per tick |
| Sword of Daith | `wh_dlc05_weapon_abilities_daiths_sword` | Armour: -30 (to enemies in range); Damage: 5 every 1s (to enemies in range) |
| The Divestment | `wh3_dlc27_army_abilities_eternal_dance_tempo_3_insidious_allure` | Armour: -50 (to enemies in range); Damage: 6 every 1s (to enemies in range) |
| Tomb Swarm | `wh2_dlc09_army_abilities_tomb_swarm` | Damage: 6 every 1s (to enemies in range) |
| Wail of Malice | `wh2_dlc14_unit_abilities_wail_of_malice` | Damage: 10 every 1s (to enemies in range) |
| Warp-Quake | `wh2_dlc14_unit_abilities_warp_quake` | Speed: -25% (to enemies in range); Damage: 5 every 0.5s (to enemies in range) |
| Warpstorm Scroll | `wh2_main_item_abilities_warpstorm_scroll` | Speed: -45% (to enemies in range); Damage: 67 every 1s (to enemies in range) |
| Web of Shadows | `wh2_main_weapon_abilities_web_of_shadows` | Speed: -25% (to enemies in range); Damage: 67 every 1s (to enemies in range) |
| Zefet-nebtar, the Mortis Blade | `wh3_dlc29_item_abilities_zefet_nebtar_the_mortis_blade` | Damage: 50 every 1s (to enemies in range) |

### No effect text available (unsourceable)  (26 abilities)

No sourceable mechanical effect text exists for the ability, so it cannot be classified (and is excluded).

| Ability | Key | Effects |
|---|---|---|
| Banner of Hellfire | `wh3_main_banner_abilities_banner_of_hellfire` | Damage: 5 every 1s (to enemies in range) |
| Battlefield Resupply | `wh2_dlc11_quest_battle_supply` | Speed: +25% (to allies in range); Vigour per second: -1% (to allies in range); Heals: +0.8% per tick (to allies in range); Replenishes ammunition (to allies in range) |
| Black Hammer of Hashut | `wh3_dlc23_weapon_abilities_black_hammer_of_hashut` | Armour-Piercing Weapon Damage: +50%; Base Weapon Damage: +50%; Imbuement: Flammable! |
| Cloak of the Dunes | `wh2_dlc09_item_abilities_cloak_of_the_dunes` | Stalk; Unspottable |
| Crooked Dice | `wh3_dlc23_hero_abilities_crooked_dice` | Armour: +60; Physical Resistance: +40; Damage Resistance: +40 |
| Dark Mace | `wh3_dlc23_weapon_abilities_dark_mace` | Armour: -30 (to enemies in range); Vigour per second: +1% (to enemies in range) |
| Ghostly Howl | `wh3_dlc29_hero_active_ghostly_howl` | Leadership: -16 (to enemies in range); Damage: 16 every 1s (to enemies in range) |
| Hag's Denial | `wh3_dlc24_unit_abilities_hags_denial` | Damage Resistance: +40; Cannot Die |
| Hunter of Champions | `wh2_dlc17_character_abilities_hunter_of_champions_upgraded` | Armour: -60 (to enemies in range); Melee Defence: -40 (to enemies in range) |
| Hunter's Call | `wh2_dlc13_character_ability_hunters_call` | Melee Defence: +24 (to self and allies); Unbreakable (to self and allies) |
| Icon of the King | `wh3_dlc29_item_abilities_icon_of_the_king` | Vigour per second: -1% (to self and allies); Heals: +0.8% per tick (to self and allies) |
| Morikhane, the Black Armour | `wh3_dlc29_item_abilities_morikhane_the_black_armour` | (no sourceable effect text) |
| Of Warp and Ruin | `wh3_dlc29_unit_abilities_of_warp_and_ruin` | Armour-Piercing Explosive Damage: +40%; Base Explosive Damage: +40%; scalar_missile_explosion_radius: +20%; Reload Skill: +30 |
| Ominous Powder | `wh3_dlc25_item_abilities_ominous_powder` | Damage: 26 every 1s; Armour-Piercing Missile Damage: +40%; Base Missile Damage: +40%; Reload Skill: +40; Magical Attacks; Armour-Piercing Missile Damage: +80%; Base Missile Damage: +80%; Reload Skill: +80; Magical Attacks |
| Petrifying Gaze | `wh3_dlc24_unit_passive_petrifying_gaze` | Speed: -25% (to enemies in range); Speed: -50% (to enemies in range); Speed: -75% (to enemies in range) |
| Rock Bottom | `wh2_dlc15_unit_abilities_rock_bottom` | Damage: 350 every 1s; Replenishes ammunition |
| Ruinshelter | `wh2_dlc15_unit_abilities_mimic_ruinshelter` | Speed: -60%; Armour: +45; Melee Attack: +8; Melee Defence: +10 |
| Seduction | `wh2_dlc11_lord_abilities_seduction` | Speed: -25% (to enemies in range); Melee Attack: -24 (to enemies in range) |
| Storm of Blades | `wh_dlc05_unit_abilities_storm_of_blades` | Melee Attack: +24; Melee Defence: -24 |
| Temptator | `wh3_dlc20_lord_abilities_temptator` | Melee Damage Reflection: +25; Damage Resistance: +20 |
| The Crimson Blade | `wh3_dlc29_item_abilities_crimson_blade` | Magical Attacks; Imbuement: Disembowelled!; Magical Attacks; Imbuement: Disrupted!; Executioner; Magical Attacks; Imbuement: Crippled! |
| The Gold Standard | `wh3_dlc25_item_abilities_the_gold_standard` | Invulnerable (to self and allies) |
| The Graven Sceptre | `wh3_dlc23_weapon_abilities_the_graven_sceptre` | Melee Attack: +24; Armour-Piercing Weapon Damage: +25%; Base Weapon Damage: +25%; Magical Attacks |
| Transfix | `wh3_dlc29_lord_abilities_transfix` | Melee Defence: -40 (to enemies in range); Silenced (to enemies in range) |
| Vine Dragon Scale | `wh2_dlc15_item_abilities_vine_dragon_scale` | Melee Defence: -24 (to enemies in range) |
| Whirling Death | `wh2_dlc16_unit_abilities_whirling_death` | Armour-Piercing Weapon Damage: -10; Base Weapon Damage: +25 |

### Ground-target-only  (14 abilities)

Must be placed on a ground point with no safe automatic placement; excluded.

| Ability | Key | Effects |
|---|---|---|
| Ballistics Calibration | `wh_main_hero_abilities_ballistics_calibration` | Reload Skill: +20 (to self and allies) |
| Curse of Djaf | `wh2_dlc09_character_abilities_curse_of_djaf` | Rampage! (to enemies in range) |
| Dance of Despair | `wh3_dlc20_cataclysm_bound_dance_of_despair` | Leadership: -24 (to enemies in range); Removes Bound Fire Daemon attribute (to enemies in range); Removes Construct attribute (to enemies in range); Removes Daemonic attribute (to enemies in range); Removes Elemental attribute (to enemies in range); Removes Unbreakable (to enemies in range); Removes Undead attribute (to enemies in range) |
| Dance of Despair | `wh3_dlc27_cataclysm_bound_dance_of_despair` | Leadership: -24 (to enemies in range); Removes Bound Fire Daemon attribute (to enemies in range); Removes Construct attribute (to enemies in range); Removes Daemonic attribute (to enemies in range); Removes Elemental attribute (to enemies in range); Removes Unbreakable (to enemies in range); Removes Undead attribute (to enemies in range) |
| Master of Mists | `wh3_dlc27_character_abilities_master_of_mists` | Armour-Piercing Missile Damage: +25% (to self and allies); Base Missile Damage: +25% (to self and allies); Range: +50% (to self and allies); Reload Skill: +20 (to self and allies); Snipe (to self and allies); Stalk (to self and allies) |
| Master of Mists | `wh3_dlc27_character_abilities_master_of_mists_custom` | Armour-Piercing Missile Damage: +25% (to self and allies); Base Missile Damage: +25% (to self and allies); Range: +50% (to self and allies); Reload Skill: +20 (to self and allies); Snipe (to self and allies); Stalk (to self and allies) |
| Soulblight | `wh3_dlc29_spell_bound_soulblight` | Imbuement: Soulblight |
| Soulblight | `wh2_dlc10_spell_bound_soulblight` | Armour: -30 (to enemies in range); Armour-Piercing Weapon Damage: -25% (to enemies in range); Base Weapon Damage: -25% (to enemies in range) |
| Storm of Renewal | `wh3_dlc20_cataclysm_bound_storm_of_renewal` | Vigour per second: -10% (to allies in range); Heals: +1% per tick (to allies in range) |
| Storm of Renewal | `wh3_dlc27_cataclysm_bound_storm_of_renewal` | Vigour per second: -10% (to allies in range); Heals: +1% per tick (to allies in range) |
| The Curse of Anraheir | `wh2_dlc16_spell_bound_the_curse_of_anraheir` | Speed: -25% (to enemies in range); Accuracy: -30 (to enemies in range); Melee Attack: -24 (to enemies in range); Melee Defence: -24 (to enemies in range) |
| The Curse of Anraheir | `wh3_main_spell_bound_the_curse_of_anraheir` | Speed: -25% (to enemies in range); Accuracy: -30 (to enemies in range); Melee Attack: -24 (to enemies in range); Melee Defence: -24 (to enemies in range) |
| The Curse of Anraheir | `wh_dlc05_spell_bound_the_curse_of_anraheir` | Speed: -25% (to enemies in range); Accuracy: -30 (to enemies in range); Melee Attack: -24 (to enemies in range); Melee Defence: -24 (to enemies in range) |
| Transmutation of Lead | `wh3_main_spell_bound_transmutation_of_lead` | Melee Attack: -24 (to enemies in range); Base Weapon Damage: -30% (to enemies in range) |

### Flanking / ambush (stealth/escape)  (7 abilities)

Hide / ambush / reposition effects; the stealth/escape family the user already rejected. Family decision 2026-10-09: EXCLUDE.

| Ability | Key | Effects |
|---|---|---|
| Armour of the Stars | `wh2_main_item_abilities_armour_of_the_stars` | Stalk; Unspottable |
| Concealment Bombs | `wh2_main_character_abilities_concealment_bombs` | Stalk; Unspottable |
| Concealment Bombs | `wh2_main_unit_abilities_concealment_bombs` | Stalk; Unspottable |
| From the Shadows | `wh3_main_character_abilities_from_the_shadows` | Speed: +45%; Stalk; Unspottable |
| Hidden in Time | `wh3_main_lord_abilities_hidden_in_time` | Stalk; Unspottable |
| Loec's Shroud | `wh_pro04_unit_abilities_loecs_shroud` | Speed: +25%; Stalk; Unspottable |
| Mirror (Loec's Shroud) | `wh2_dlc15_unit_abilities_mimic_loecs_shroud` | Speed: +25%; Stalk; Unspottable |

### Summon / transform  (4 abilities)

Summons or swaps unit forms, which the battle-script API cannot drive.

| Ability | Key | Effects |
|---|---|---|
| Bloodstone | `wh3_main_item_abilities_bloodstone` | Summons a unit of Bloodletters |
| Get Tha Gitz! | `wh3_dlc23_hero_abilities_get_tha_gitz!` | Summons a unit of Hobgoblin Cutthroats; Summoned units degrade over time |
| Karanak's Howl | `wh3_pro12_hero_abilities_karanaks_howl` | Summons a unit of Flesh Hounds; Summoned units degrade over time |
| The Portalglyph | `wh3_main_item_abilities_the_portalglyph` | Summons a unit of Chaos Furies |

### No ammo-low read (ammo replenish)  (3 abilities)

Replenishes ammunition; the engine exposes no per-unit ammo-low read to trigger it.

| Ability | Key | Effects |
|---|---|---|
| More Powder! | `wh2_dlc11_hero_abilities_more_powder` | Replenishes ammunition (to self and allies) |
| Restock! | `wh2_dlc17_hero_abilities_more_powder_generic` | Replenishes ammunition (to allies in range) |
| Restock! | `wh3_dlc25_abilities_restock_gunnery_school` | Replenishes ammunition (to allies in range) |

### Magic scope  (1 abilities)

Excluded as a spell-scope ability.

| Ability | Key | Effects |
|---|---|---|
| Sword of Teclis | `wh2_main_weapon_abilities_sword_of_teclis` | Spell Mastery: +30%; Reserves Per Second: +0.20 |

### Enemy-ground placement (no placement path)  (1 abilities)

Must be placed on enemy ground and there is no automatic placement path to do so; excluded.

| Ability | Key | Effects |
|---|---|---|
| The Soulstealer | `wh3_dlc29_spell_bound_undeath_khizaar_the_soulstealer` | Vigour per second: +1% (to enemies in range); Damage: 4 every 1s (to enemies in range) |

---

## Section 4 — IMPOSSIBLE, REJECTED and SKIPPED

### 4A. IMPOSSIBLE — the engine cannot support it

#### Impossible — no enemy-unit read  (76 abilities)

The ability must target, react to, or measure an enemy unit, and the battle-script API exposes no enemy-unit read (an enemy unit has no card and no id).

| Ability | Key | Effects |
|---|---|---|
| 'Effagee' of da Git | `wh_dlc06_character_abilities_effagee_of_da_git` | Damage: 67 every 1s (to enemies in range) |
| Amber Bow | `wh2_dlc13_weapon_abilities_amber_bow` | Causes major magical damage; Good against large combatants; Strong vs a single combatant; Effective at long range; Requires line of sight to the target |
| Arrow of Aqshy | `wh2_dlc13_lord_abilities_fire_arrow` | Causes fire damage; Powerful explosion; Strong vs multiple combatants; Requires line of sight to the target |
| Blood Statuette of Spite | `wh2_main_item_abilities_blood_statuette_of_spite` | Damage: 5 every 1s (to enemies in range) |
| Bolt of Change | `wh3_main_army_abilities_bolt_of_change` | Medium strike area |
| Bolt of Spite | `wh2_main_army_abilities_bolt_of_spite` | Magical homing-missile; Small strike area; Strong vs a single combatant |
| Burning Wrath | `wh3_dlc23_spell_bound_burning_wrath` | Requires targeting / reacting to an enemy unit. |
| Chain Lightning | `wh3_dlc27_spell_heavens_chain_lightning_bound` | Damage: 4 every 1s (to enemies in range) |
| Chain Lightning | `wh3_dlc27_spell_heavens_chain_lightning_bound_unit` | Damage: 4 every 1s (to enemies in range) |
| Daemonic Possession | `wh3_main_lord_abilities_daemonic_possession` | Spell Resistance: -25 (to enemies in range); Vigour per second: +1% (to enemies in range) |
| Damned Pistol | `wh3_main_weapon_abilities_godkiller_pistol` | Requires targeting / reacting to an enemy unit. |
| Darkened Mist | `wh3_dlc23_item_abilities_darkened_mist` | Damage: 7 every 1s (to enemies in range) |
| Dart of Doom | `wh2_dlc16_item_abilities_dart_of_doom` | Weapon Strength on contact; Causes armour-piercing damage; Causes magical damage |
| Dead Eye | `wh3_dlc26_character_abilities_dead_eye` | Strong against lightly armoured characters; Strong against small entities; Requires line of sight to the target |
| Death's Timekeeper | `wh3_dlc25_item_abilities_deaths_timekeeper` | Damage: 67 every 1s (to enemies in range); Heals: +1% per tick |
| Dire Spirit Bear | `wh3_dlc24_lord_abilities_spirit_bear_upgrade` | Causes moderate magical & fire damage; Powerful explosion; Strong vs multiple combatants; Requires line of sight to the target |
| Dissolving Bone | `wh3_dlc27_qb_unit_abilities_dissolving_bone` | Damage: 732 every 1s (to enemies in range); Executes below 33% HP (to enemies in range) |
| Dweomer Leach Orb | `wh3_dlc23_item_abilities_dweomer_leach_orb` | Power Recharge: -60% (to enemies in range); Reserves Per Second: -0.10 (to enemies in range); Power Recharge: +100%; Reserves Per Second: +0.20 |
| Eagle Quiver | `wh2_dlc16_item_abilities_eagle_quiver` | Causes armour-piercing damage; Effective at long range; Good penetration |
| Ethrac's Brazier | `wh3_dlc29_item_active_ethracs_brazier` | Charge Speed: -25% (to enemies in range); Speed: -25% (to enemies in range); Damage: 4 every 1s (to enemies in range) |
| Executioner | `wh2_dlc13_lord_abilities_executioner` | Scaled projectile damage against combatants with missing health; Causes moderate magical damage; Good against armour; Good against large combatants; Requires line of sight to the target |
| Fireball | `wh_main_spell_bound_fireball` | Causes moderate magical & fire damage; Powerful explosion; Strong vs multiple combatants; Effective at long range; Requires line of sight to the target |
| Fireball Upgraded | `wh3_dlc27_spell_bound_fireball_upgraded` | Causes moderate magical & fire damage; Powerful explosion; Strong vs multiple combatants; Effective at long range; Requires line of sight to the target |
| Focused Shot | `wh2_dlc13_lord_abilities_kill_shot` | Scaled projectile damage against combatants with missing health; Causes moderate magical damage; Good against armour; Good against large combatants; Requires line of sight to the target |
| Gaze of Nagash | `wh2_dlc15_spell_bound_gaze_of_nagash` | Causes moderate magical damage; Good against armour; Good against large combatants; Strong vs a single combatant |
| Goggly Glare | `wh2_dlc15_character_abilities_goggly_glare` | Causes moderate magical damage; Good against large combatants; Strong vs a single combatant; Requires line of sight to the target |
| Hail of Doom Arrow | `wh_dlc05_item_abilities_hail_of_doom_arrow` | Large area of effect; Powerful explosion; Strong vs multiple units; Weak vs a single combatant |
| Hand of Gods | `wh2_main_spell_bound_hand_of_gods` | Causes major magical & fire damage; Good against armour; Good against large combatants; Strong vs a single combatant |
| Khorne's Wrath | `wh3_dlc26_army_abilities_khornes_wrath` | Causes major magical damage; Medium strike area; Good against armour; Strong vs a single combatant; Strong vs a single unit |
| Lesser Doombolt | `wh2_dlc10_spell_bound_lesser_doombolt` | Causes moderate magical damage; Good against armour; Strong vs a single unit |
| Maelstrom of Change | `wh3_dlc24_unit_abilities_maelstrom_of_change` | Damage: 10 every 1s (to enemies in range) |
| Mercurial Shot | `wh3_dlc25_character_abilities_mercurial_shot` | Causes fire damage; Powerful explosion; Strong vs multiple combatants; Requires line of sight to the target |
| No Escape | `wh3_main_character_abilities_no_escape` | Melee Defence: -40 (to enemies in range) |
| Otherworldly Pestilence | `wh3_dlc29_lord_abilities_otherworldly_pestilence` | Damage: 5 every 1s (to enemies in range) |
| Preyton Horns | `wh3_dlc27_item_abilities_preyton_horns` | Leadership: -8 (to enemies in range); Leadership: +8 (to allies in range) |
| Punch-Dagger | `wh3_dlc29_item_abilities_punch_dagger` | Damage: 125 every 1s (to enemies in range) |
| Quiver of Aqshy | `wh2_dlc13_lord_abilities_arrows_of_aqshy` | Causes fire damage; Powerful explosion; Strong vs multiple combatants; Requires line of sight to the target |
| Rancid Visitations | `wh3_main_spell_bound_rancid_visitations` | Damage: 133 every 1s (to enemies in range) |
| Rod of Torment | `wh3_dlc20_item_abilities_rod_of_torment` | Causes moderate magical damage; Good against armour; Strong vs a single unit |
| Schalkain's Teeth | `wh3_dlc27_item_abilities_schalkains_teeth` | Causes massive magical damage; Good against armour; Strong vs a single combatant; Weak vs multiple combatants; Requires line of sight to the target |
| Shadowblood | `wh3_dlc29_lord_abilities_shadowblood` | Damage: 500 every 1s |
| Shem's Burning Gaze | `wh_main_spell_light_shems_burning_gaze_bound` | Causes minor magical & fire damage; Good against armour; Good against large combatants; Strong vs a single combatant |
| Spear of Grungni | `wh3_dlc25_unit_abilities_spear_of_grungni` | Causes armour-piercing damage; Good against large combatants; Requires line of sight to the target |
| Spear of Kurnous | `wh_dlc05_weapon_abilities_spear_of_kurnous` | Causes armour-piercing damage; Effective at all ranges; Good penetration; Can cause damage to friendly combatants |
| Spirit Barrage | `wh3_dlc25_army_abilities_spirit_barrage` | Damage: 600 every 1s |
| Spirit Bear | `wh3_dlc24_lord_abilities_spirit_bear` | Causes moderate magical & fire damage; Powerful explosion; Strong vs multiple combatants; Requires line of sight to the target |
| Spirit Leech | `wh2_dlc09_spell_death_spirit_leech_bound` | Damage: 67 every 1s (to enemies in range) |
| Spirit Leech | `wh3_dlc25_spell_bound_spirit_leech` | Damage: 67 every 1s (to enemies in range) |
| Spirit Leech | `wh3_dlc25_spell_bound_spirit_leech_gunnery_school` | Damage: 67 every 1s (to enemies in range) |
| Spirit Leech | `wh3_main_spell_bound_spirit_leech` | Damage: 67 every 1s (to enemies in range) |
| Spirit Leech | `wh3_twa08_spell_bound_spirit_leech_great_unclean_one_ror` | Damage: 67 every 1s (to enemies in range) |
| Staff of Masks | `wh3_dlc27_item_abilities_staff_of_the_masque` | Vigour per second: +1% (to enemies in range); Damage: 5 every 1s (to enemies in range); Vigour per second: -1%; Heals: +0.5% per tick |
| Sting of Snagla | `wh3_dlc26_character_abilities_sting_of_snagla` | Melee Attack: -24; Melee Defence: -40 |
| Storm of the Night | `wh2_dlc11_lord_abilities_storm_of_the_night` | Speed: -60% (to enemies in range); Damage: 67 every 1s (to enemies in range) |
| Swamp Breath | `wh2_dlc15_hero_abilities_swamp_breath` | Powerful explosion; Good against armour; Strong vs a single unit |
| Taal's Judgement | `wh3_dlc24_lord_abilities_taals_judgement` | Requires targeting / reacting to an enemy unit. |
| Tempest | `wh3_dlc27_army_high_magic_tempest` | Speed: -60% (to enemies in range); Damage: 133 every 1s (to enemies in range) |
| Terrible Malice | `wh3_dlc27_qb_unit_abilities_terrible_malice` | Damage: 732 every 1s (to enemies in range); Executes below 20% HP (to enemies in range) |
| The Amber Trance | `wh2_dlc10_item_abilities_the_amber_trance` | Leadership: -16 (to enemies in range); Leadership: +16 |
| The Emperor's Executioner | `wh3_dlc24_lord_abilities_the_emperors_executioner` | Damage: 732 every 1s (to enemies in range); Executes below 20% HP (to enemies in range) |
| The Emperor's Executioner | `wh3_dlc24_lord_abilities_the_emperors_executioner_upgrade` | Damage: 732 every 1s (to enemies in range); Executes below 33% HP (to enemies in range) |
| The Fate of Bjuna | `wh3_dlc25_spell_bound_the_fate_of_bjuna` | Damage: 10 every 1s (to enemies in range) |
| The Fate of Bjuna | `wh3_main_spell_bound_the_fate_of_bjuna` | Damage: 10 every 1s (to enemies in range) |
| The Gaze of Dust | `wh3_dlc29_unit_abilities_the_gaze_of_dust` | Causes armour-piercing damage; Effective at long range |
| The Golden Blowpipe of P'Toohee | `wh2_dlc17_weapon_abilities_the_golden_blowpipe_of_ptoohee` | Good armour-piercing damage; Strong vs a single combatant; Effective at close range; Poor penetration |
| The Liber Bubonicus | `wh2_main_item_abilities_the_liber_bubonicus` | Damage: 67 every 1s (to enemies in range) |
| The Windblade | `wh3_dlc24_hero_abilities_windblade` | Spawns a moving area of effect; Strong vs multiple combatants |
| Tome of Furion | `wh2_main_spell_bound_tome_of_furion` | Causes major magical damage; Medium strike area; Strong vs a single combatant; Strong vs a single unit |
| Vindictive Glare | `wh_dlc06_spell_bound_vindictive_glare` | Causes moderate magical damage; Good against large combatants; Strong vs a single combatant |
| Volley of Kurnous | `wh2_dlc16_unit_abilities_volley_of_kurnous` | Causes armour-piercing damage; Effective at long range; Good penetration |
| Wand of the Kharaidon | `wh2_main_spell_bound_wand_of_the_kharaidon` | Causes major magical damage; Medium strike area; Strong vs a single combatant; Strong vs a single unit |
| Warp-Fireball | `wh2_dlc14_spell_bound_warpfireball` | Causes moderate magical & fire damage; Powerful explosion; Strong vs multiple combatants; Effective at long range; Requires line of sight to the target |
| Wind Bow | `wh3_dlc24_item_abilities_wind_bow` | Causes moderate magical damage; Strong vs multiple combatants; Effective at long range; Requires line of sight to the target |
| Wolf's Howl | `wh3_main_weapon_abilities_the_traitors_sword` | Medium strike area |
| Wraith Storm | `wh2_dlc11_army_abilities_wraith_storm` | Causes moderate magical damage; Good against armour; Strong vs a single unit |
| Wraith Storm | `wh2_dlc11_lord_abilities_wraith_storm` | Causes moderate magical damage; Good against armour; Strong vs a single unit |

#### Impossible — no transform/shapechange support  (11 abilities)

The battle-script API cannot swap a unit's form, so transform / shapechange effects have no implementation.

| Ability | Key | Effects |
|---|---|---|
| Formless Horror | `wh3_dlc24_lord_abilities_formless_horror_changeling` | Transforms / swaps the unit's form. |
| Formless Horror | `wh3_dlc24_lord_abilities_formless_horror_quest_battle_changeling_form` | Transforms / swaps the unit's form. |
| Transformation of Kadon | `wh3_dlc27_spell_bound_transformation_of_kadon` | Summons a Manticore; Powerful unit ideal for combat; Summoned units degrade over time; Spawned unit fights in this battle only |
| Transformation of the Dragon | `wh3_dlc24_lord_abilities_jade_dragon_human_form` | Transform to human form; Form offers a stronger Harmony multiplier and a small size; Enables full spell usage |
| Transformation of the Dragon | `wh3_main_lord_abilities_iron_dragon_human_form` | Transform to human form; Form offers a stronger Harmony multiplier and a small size; Enables full spell usage |
| Transformation of the Dragon | `wh3_main_lord_abilities_storm_dragon_human_form` | Transform to human form; Form offers a stronger Harmony multiplier and a small size; Enables full spell usage |
| Tz'arkan | `wh2_dlc14_lord_abilities_tzarkan` | Becomes possessed by Tz'arkan; Possession causes health loss over time; Health and fatigue are restored; Innate abilities replaced |
| Tz'arkan | `wh2_dlc14_lord_abilities_tzarkan_mp` | Becomes possessed by Tz'arkan; Possession causes health loss over time; Health and fatigue are restored; Innate abilities replaced |
| Tz'arkan | `wh2_dlc14_lord_abilities_tzarkan_snikch` | Becomes possessed by Tz'arkan; Possession causes health loss over time; Health and fatigue are restored; Innate abilities replaced |
| Tz'arkan | `wh2_dlc14_lord_abilities_tzarkan_spite` | Becomes possessed by Tz'arkan; Possession causes health loss over time; Health and fatigue are restored; Innate abilities replaced |
| Tz'arkan | `wh2_dlc14_lord_abilities_tzarkan_spite_mp` | Becomes possessed by Tz'arkan; Possession causes health loss over time; Health and fatigue are restored; Innate abilities replaced |

#### Impossible — already rejected by user (tactical escape/stealth)  (10 abilities)

The user already rejected this as a tactical escape / stealth effect.

| Ability | Key | Effects |
|---|---|---|
| Eagle Bow | `wh2_dlc16_weapon_abilities_eagle_bow` | Charge Speed: +25% (to self and allies); Speed: +25% (to self and allies) |
| Envelop in Mist | `wh2_dlc15_army_abilities_envelop_in_mist` | Snipe (to allies in range); Stalk (to allies in range); Unspottable (to allies in range) |
| Envelop in Mist | `wh3_dlc27_character_abilities_envelop_in_mist_bound` | Snipe (to allies in range); Stalk (to allies in range); Unspottable (to allies in range) |
| Loec's Blessing | `wh2_dlc16_lord_abilities_loecs_blessing` | Speed: +25% (to self and allies); Stalk (to self and allies); Unspottable (to self and allies) |
| Perfect Predator | `wh3_dlc27_unit_abilities_perfect_predator` | Stalk; Heals: +0.35% per tick |
| Rival Hide Talisman | `wh2_main_item_abilities_rival_hide_talisman` | Melee Attack: -40 (to enemies in range) |
| Sand Veil | `wh2_dlc09_army_abilities_sand_veil` | Turn Speed: +25% (to self and allies); Stalk (to self and allies); Unspottable (to self and allies) |
| Skitterleap | `wh3_dlc29_spell_bound_skitterleap` | Speed: +25%; Stalk; Unspottable |
| Speed of Lykos | `wh2_dlc10_item_abilities_speed_of_lykos` | Speed: +25% (to self and allies); Stalk (to self and allies); Unspottable (to self and allies) |
| Tricksy Traps | `wh_dlc06_lord_abilities_tricksy_traps` | Speed: +25% (to self and allies); Stalk (to self and allies); Unspottable (to self and allies) |

### 4B. REJECTED — the user rejected it (no automatic logic)

#### Rejected — mutual exclusivity  (5 abilities)

Auto-rejected: mutually exclusive with another ability (standing rule 8).

| Ability | Key | Effects |
|---|---|---|
| Bastion of the Great Cities | `wh3_dlc24_unit_abilities_bastion_of_the_great_cities` | Armour: +24 (to self and allies); Expert Charge Defence (to self and allies) |
| Disdain of the Dragon Emperor | `wh3_dlc24_unit_abilities_disdain_of_the_dragon_emperor` | Melee Attack: +8 (to self and allies); Reload Skill: +10 (to self and allies); Immune to Psychology (to self and allies) |
| Fury of the Falling Blade | `wh3_dlc24_unit_abilities_fury_of_the_falling_blade` | Armour-Piercing Weapon Damage: +15% (to self and allies); Base Weapon Damage: +15% (to self and allies); Can Cause Fear (to self and allies); Magical Attacks (to self and allies) |
| Harbinger of Pestilence | `wh3_dlc20_lord_abilities_harbinger_of_pestilence` | Damage: 4 every 1s (to enemies in range) |
| Healing Elixirs | `wh3_dlc20_lord_abilities_healing_elixirs` | Heals: +0.1% per tick (to self and allies) |

#### Rejected — drawback  (5 abilities)

User rejected: a meaningful drawback; the player should decide.

| Ability | Key | Effects |
|---|---|---|
| All-Consuming Hatred | `wh3_dlc27_unit_abilities_consuming_hatred` | Melee Damage Reflection: +40; Melee Defence: -12 |
| Daggerdance | `wh3_dlc27_lord_abilities_daggerdance` | Armour: +40; Bonus vs. Infantry: -15; Armour-Piercing Weapon Damage: -25%; Base Weapon Damage: -25%; Damage Resistance: +25 |
| Dance of Destruction | `wh3_dlc27_lord_abilities_dance_of_destruction` | Melee Attack: +36; Armour-Piercing Weapon Damage: +25%; Base Weapon Damage: +25%; Melee Defence: -24; Unyielding Assault |
| Dinner Bell | `wh3_dlc26_character_abilities_dinner_bell` | Ability recharge: -35s |
| Harvestman's Scythe | `wh3_dlc29_item_active_harvestmans_scythe` | Bonus vs. Infantry: -100%; Bonus vs. Large: +45; Armour-Piercing Weapon Damage: +50% |

#### Rejected — rampage  (3 abilities)

User rejected: causes Rampage; left to the player.

| Ability | Key | Effects |
|---|---|---|
| Call for Power | `wh3_main_daemon_head_abilities_call_for_power` | Splash Attack Power: +50%; Base Weapon Damage: +50%; Rampage! |
| In the Name of War | `wh3_dlc29_lord_abilities_in_the_name_of_war` | Melee Defence: -20 (to enemies in range); Rampage! (to enemies in range) |
| Manus of Ursun | `wh3_main_weapon_abilities_ursuns_claws` | Base Weapon Damage: +12% (to self and allies); Can Cause Terror (to self and allies); Rampage! (to self and allies) |

#### Rejected — friendly fire  (3 abilities)

User rejected: potential for friendly fire; no automatic logic.

| Ability | Key | Effects |
|---|---|---|
| Acidic Musk Glands | `wh2_dlc16_unit_abilities_acidic_musk_glands` | Armour: -30 (all units in range); Damage: 9 every 1s (all units in range) |
| Endless Whirlwind of Death | `wh3_dlc25_unit_abilities_whirlwind_of_death_ror` | (no automatic logic — left to the player) |
| Endless Whirlwind of Death Upgraded | `wh3_dlc25_unit_abilities_whirlwind_of_death_ror_upgraded` | (no automatic logic — left to the player) |

#### Rejected — stealth / tactical escape  (3 abilities)

User rejected: tactical escape / stealth effect; left to the player.

| Ability | Key | Effects |
|---|---|---|
| Epidemic Outbreak | `wh3_dlc25_character_abilties_epidemic_outbreak_improved` | Explosion does not affect friendly troops; Allows chance to escape melee; Strong vs multiple combatants; Poor against large combatants |
| Epidemic Outburst | `wh3_dlc25_character_abilties_epidemic_outbreak` | Explosion does not affect friendly troops; Allows chance to escape melee; Strong vs multiple combatants; Poor against large combatants |
| From the Shadows | `wh2_dlc14_character_abilities_from_the_shadows` | Snipe (to self and allies); Stalk (to self and allies); Unspottable (to self and allies) |

### 4C. SKIPPED — deferred or unsuitable (not a rejection, but no code)

#### Skipped — army-bar ability  (18 abilities)

Army-bar ability; skipped by standing rule 10.

| Ability | Key | Effects |
|---|---|---|
| Ancestral Rune of Grungni | `wh2_dlc17_army_abilities_ancestral_rune_of_grungni` | Melee Attack: +24 (to allies in range); Unbreakable (to allies in range) |
| Armour of Contempt | `wh3_dlc23_army_abilities_armour_of_contempt` | Armour: +30 (to allies in range); Melee Defence: +24 (to allies in range); Immune to Psychology (to allies in range) |
| Basking in Our Flame | `wh3_dlc27_army_abilities_eternal_dance_tempo_3_needful_caress` | Missile Block Chance: +30 (to self and allies); Damage Resistance: +20 (to self and allies); 360 Missile Block (to self and allies); Immune to Contact Effects (to self and allies) |
| Horn of Khorne | `wh3_main_army_abilities_horn_of_khorne` | Melee Attack: +24 (to allies in range) |
| Mors Clanstone | `wh2_main_army_abilities_mors_clanstone` | Armour-Piercing Weapon Damage: +50% (to allies in range) |
| Oath of Replenishment | `wh2_dlc15_army_abilities_oath_of_replenishment` | Leadership: +8 (to allies in range); Vigour per second: -9% (to allies in range); Replenishes ammunition (to allies in range) |
| Oath of Replenishment Upgraded | `wh2_dlc15_army_abilities_oath_of_replenishment_upgraded` | Armour-Piercing Missile Damage: +25% (to allies in range); Base Missile Damage: +25% (to allies in range); Perfect Vigour (to allies in range); Unbreakable (to allies in range); Replenishes ammunition (to allies in range) |
| Pestilens Clanstone | `wh2_main_army_abilities_pestilens_clanstone` | Imbuement: Poison! (to allies in range) |
| Rictus Clanstone | `wh2_dlc09_army_abilities_rictus_clanstone` | Bonus vs. Large: +32 (to self and allies) |
| Shanty: First Verse | `wh2_dlc11_army_abilities_shanty_verse_1` | Melee Defence: +20 (to allies in range); Reload Skill: +20 (to allies in range) |
| Shanty: First Verse | `wh2_dlc11_army_abilities_shanty_verse_1_ai` | Melee Defence: +20 (to allies in range); Reload Skill: +20 (to allies in range) |
| Shanty: Second Verse | `wh2_dlc11_army_abilities_shanty_verse_2` | Melee Defence: +30 (to allies in range); Reload Skill: +30 (to allies in range) |
| Shanty: Second Verse | `wh2_dlc11_army_abilities_shanty_verse_2_ai` | Melee Defence: +30 (to allies in range); Reload Skill: +30 (to allies in range) |
| Shanty: Third Verse | `wh2_dlc11_army_abilities_shanty_verse_3` | Melee Defence: +40 (to allies in range); Reload Skill: +40 (to allies in range) |
| Shanty: Third Verse | `wh2_dlc11_army_abilities_shanty_verse_3_ai` | Melee Defence: +40 (to allies in range); Reload Skill: +40 (to allies in range) |
| The Airless Fires | `wh3_dlc27_army_abilities_eternal_dance_tempo_3_revelry_and_madness` | Armour-Piercing Weapon Damage: +40% (to self and allies); Base Weapon Damage: +40% (to self and allies); Unyielding Assault (to self and allies); Imbuement: Mad! (to self and allies) |
| The Burning Waters | `wh3_dlc27_army_abilities_eternal_dance_tempo_3_streams_of_euphoria` | Splash Attack Power: +50% (to self and allies); Bonus vs. Infantry: +16 (to self and allies); Melee Attack: +16 (to self and allies); Imbuement: Euphoric! (to self and allies) |
| The Unmasking | `wh3_dlc27_army_abilities_eternal_dance_tempo_3_fate_of_desperation` | Armour-Piercing Weapon Damage: -35% (to enemies in range); Base Weapon Damage: -35% (to enemies in range); Melee Defence: -24 (to enemies in range); Silenced (to enemies in range) |

#### Skipped — unsuitable (vortex)  (17 abilities)

Vortex ability; unsuitable for the in-melee self automation.

| Ability | Key | Effects |
|---|---|---|
| Alakanash, the Staff of Power | `wh3_dlc29_item_abilities_alakanash_the_staff_of_power` | Damage: 4 every 0.2s (to enemies in range) |
| Ark of Sotek | `wh2_dlc12_unit_abilities_ark_of_sotek` | Does not affect friendly troops; Moderate, stationary area of effect |
| Celestial Sweep | `wh3_dlc24_lord_abilities_celestial_sweep` | (no automatic logic) |
| Cellular Instability | `wh2_dlc16_unit_abilities_cellular_instability` | Damage: 50 every 0.5s |
| Destruction | `wh3_dlc29_spell_bound_prayer_destruction` | (no automatic logic) |
| Eruption | `wh3_main_character_abilities_eruption` | (no automatic logic) |
| Ferocious Destruction | `wh3_dlc29_spell_bound_prayer_ferocious_destruction` | (no automatic logic) |
| Glacial Blast | `wh3_main_character_abilities_glacial_blast` | (no automatic logic) |
| Kill for Khorne! | `wh3_dlc26_character_abilities_kill_for_khorne` | (no automatic logic) |
| Sonic Boom | `wh3_main_daemon_head_abilities_sonic_boom` | Causes severe disruption to enemy formations; Strong vs multiple combatants; Inflicts minimal damage |
| Splode da Big 'Un! | `wh3_dlc26_unit_abilities_splode_da_big_one` | Damage: 26600 every 0.2s |
| The Hammer of Harry | `wh3_pro11_weapon_abilities_the_hammer_of_harry` | Causes moderate magical damage; Causes severe disruption to enemy formations; Strong vs multiple combatants |
| Thundermace | `wh3_main_weapon_abilities_thundermace` | Powerful explosion |
| Venom Wave | `wh2_dlc09_lord_abilities_venom_wave` | Explosion does not affect friendly troops; Large explosion area; Strong vs a single unit |
| Whirlwind of Death | `wh3_dlc25_unit_abilities_whirlwind_of_death` | (no automatic logic) |
| Whirlwind of Death Upgraded | `wh3_dlc25_unit_abilities_whirlwind_of_death_upgraded` | (no automatic logic) |
| Wrath of Ptra | `wh2_dlc09_lord_abilities_wrath_of_ptra` | Explosion does not affect friendly troops; Causes moderate magical & fire damage; Large explosion area |

#### Skipped — revisit later  (15 abilities)

The user chose to skip for now (not a rejection); to revisit in a later block.

| Ability | Key | Effects |
|---|---|---|
| Beastlord's Gaze | `wh2_twa03_lord_abilities_beastlords_gaze` | Leadership: +16 (to self and allies); Damage Resistance: +10 (to self and allies); Stops Rampage! (to self and allies) |
| Fog of the Damned | `wh3_dlc29_bound_deep_fog_of_the_damned` | Melee Attack: -24 (to enemies in range); Leadership: -8 (to enemies in range) |
| Formless Horror | `wh3_dlc24_lord_abilities_formless_horror` | <unknown> (other source) |
| Formless Horror | `wh3_dlc24_lord_abilities_formless_horror_quest_battle` | <unknown> (other source) |
| Locus of Contagion | `wh3_main_character_abilities_locus_of_contagion` | Damage: 5 every 1s (to enemies in range) |
| Mad Cap Mushrooms | `wh_main_hero_abilities_mad_cap_mushrooms` | Ability recharge: -30s |
| Mirror of Knowledge | `wh3_dlc24_item_abilities_mirror_of_knowledge` | Speed: -25% (to enemies in range); Reveals Unit (to enemies in range) |
| Offering to the Gods | `wh3_dlc27_lord_abilities_offering_to_the_gods` | Damage: 400 every 1s (to allies in range); Melee Attack: +40 (to allies in range); Armour-Piercing Weapon Damage: +20% (to allies in range); Base Weapon Damage: +20% (to allies in range); Leadership: +16 (to allies in range) |
| Seductive Glory | `wh3_main_lord_abilities_seductive_glory` | Melee Defence: -24 (to enemies in range); Rampage! (to enemies in range) |
| Seismic Snare | `wh2_dlc14_unit_abilities_seismic_snare` | (no automatic logic) |
| Seismic Snare | `wh3_dlc29_unit_abilities_stormfiend_seismic_snare` | (no automatic logic) |
| The Black Gem of Gnar | `wh3_dlc23_item_abilities_black_gem_of_gnar` | Melee Attack: -100%; Invulnerable |
| Transformation of the Dragon | `wh3_dlc24_lord_abilities_jade_dragon_dragon_form` | Transform to Dragon form; Form offers powerful melee attacks and flight; Restricted spell availability and reduction in Harmony multiplier |
| Transformation of the Dragon | `wh3_main_lord_abilities_iron_dragon_dragon_form` | Transform to Dragon form; Form offers powerful melee attacks and flight; Restricted spell availability and reduction in Harmony multiplier |
| Transformation of the Dragon | `wh3_main_lord_abilities_storm_dragon_dragon_form` | Transform to Dragon form; Form offers powerful melee attacks and flight; Restricted spell availability and reduction in Harmony multiplier |

#### Skipped — unsuitable (spawned / ranged)  (13 abilities)

Spawned or ranged ability; unsuitable for the in-melee self automation.

| Ability | Key | Effects |
|---|---|---|
| Call of Tor | `wh3_twa07_spell_bound_call_of_tor` | Does not affect friendly troops; Causes moderate magical damage; Large strike area; Weak vs a single combatant |
| Gate of Khorne | `wh3_main_character_abilities_gate_of_khorne` | Summons a unit of Bloodletters; Summoned units degrade over time |
| Gate of Nurgle | `wh3_main_character_abilities_gate_of_nurgle` | Summons a unit of Plaguebearers; Summoned units degrade over time |
| Gate of Slaanesh | `wh3_main_character_abilities_gate_of_slaanesh` | Summons a unit of Daemonettes; Summoned units degrade over time |
| Grand Soulfire | `wh_dlc04_spell_bound_soulfire_upgraded` | Increased effect area; Increased number of missiles; Does not affect friendly troops; Causes moderate magical damage; Large strike area; Weak vs a single combatant |
| Greater Gate of Khorne | `wh3_main_cataclysm_khorne_greater_gate_of_khorne` | Summons a Bloodthirster; Summoned units degrade over time |
| Greater Gate of Khorne | `wh3_main_character_abilities_greater_gate_of_khorne` | Summons a Bloodthirster; Summoned units degrade over time |
| Greater Gate of Nurgle | `wh3_main_character_abilities_greater_gate_of_nurgle` | Summons a Great Unclean One; Summoned units degrade over time |
| Greater Gate of Slaanesh | `wh3_main_character_abilities_greater_gate_of_slaanesh` | Summons a Keeper of Secrets; Summoned units degrade over time |
| Greater Gate of Tzeentch | `wh3_main_character_abilities_greater_gate_of_tzeentch` | Summons a Lord of Change; Summoned units degrade over time |
| Soulfire | `wh_main_spell_bound_soulfire` | Does not affect friendly troops; Causes moderate magical damage; Large strike area; Weak vs a single combatant |
| The Tallyman's Blades | `wh3_dlc25_character_abilities_tallymans_blades` | Summons a unit of Exalted Plaguebearers; Summoned units degrade over time |
| The Tallyman's Blades Upgraded | `wh3_dlc25_character_abilities_tallymans_blades_2` | Summons a unit of Exalted Plaguebearers |

#### Skipped — unsuitable (movement)  (5 abilities)

Movement ability; unsuitable for the in-melee self automation.

| Ability | Key | Effects |
|---|---|---|
| Battle Howl | `wh3_dlc29_ability_bound_prayer_battle_howl` | Charge Speed: +25% (to self and allies); Speed: +25% (to self and allies); Charge Bonus: +20% (to self and allies) |
| Battle Howl | `wh3_dlc29_spell_bound_prayer_battle_howl` | Charge Speed: +25% (to self and allies); Speed: +25% (to self and allies); Charge Bonus: +20% (to self and allies) |
| Time Amok | `wh3_dlc20_cataclysm_bound_time_amok` | Speed: +40% (to allies in range); Charge Bonus: +20% (to allies in range) |
| Time Amok | `wh3_dlc27_cataclysm_bound_time_amok` | Speed: +40% (to allies in range); Charge Bonus: +20% (to allies in range) |
| Twilight Horn II | `wh2_dlc16_item_abilities_twilight_horn_ii` | Charge Speed: +25% (to self and allies); Speed: +25% (to self and allies); Charge Bonus: +20% (to self and allies) |

#### Skipped — not achievable  (1 abilities)

Approved in principle but not achievable with the current engine hooks.

| Ability | Key | Effects |
|---|---|---|
| Enkhil's Kanopi | `wh2_dlc09_item_abilities_enkhils_kanopi` | Spell Resistance: +60 (to self and allies) |

#### Skipped — unsuitable (charge-only)  (1 abilities)

Charge-only ability; unsuitable for the in-melee self automation.

| Ability | Key | Effects |
|---|---|---|
| Silver Horn of Vengeance | `wh_main_item_abilities_silver_horn_of_vengeance` | Charge Bonus: +12 (to self and allies) |

#### Skipped — magic scope + self-damage  (1 abilities)

Magic-scope ability that also damages the caster; skipped.

| Ability | Key | Effects |
|---|---|---|
| Skull of Katam | `wh_main_item_abilities_skull_of_katam` | Spell Mastery: +60%; Damage: 66 every 1s |

#### Skipped — unsuitable (movement / vortex)  (1 abilities)

Movement / vortex ability; unsuitable for the in-melee self automation.

| Ability | Key | Effects |
|---|---|---|
| Swiftness of Itzl | `wh2_main_character_abilities_swiftness_of_itzl` | Speed: +25% |

---

## Reconciliation

- Section 2 (implemented): **605** abilities.
- Section 3 (excluded, non-impossible): **1004** abilities.
- Section 4 (impossible 97 + rejected 19 + skipped 72): **188** abilities.
- **Total: 1797** — equals the tracker inventory total of **1,797**.
- Implemented keys: **605** — equals the mod's `ABILITIES` key count of **605**.

_Generated from the project's own tracker, reports and mod table; no ability rows were added or dropped._
