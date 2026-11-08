# Warhammer III auto-ability mod — questionnaire blocks 7, 8, 9

_Prepared for review. Read this tomorrow, answer each item yes/no or with a variation,
and the answers become the implementation list for the next round._

## How this works

Each **questionnaire item** below is a melee ability proposed for automatic activation.
For each one you either:

- **Yes** — implement it exactly as the *Proposed activation* line says; or
- **No** — leave it to the player (no automatic logic); or
- **A variation** — write any different condition on the `Your answer:` line
  (e.g. “health ≤ 75%”, “charge window or melee”, “skip for now”).

Three standing filters have already been applied so they are **not** shown as questions:

- **Auto-accepted (trivial)** — a self-cast ability whose only positive effects are
  Melee Attack / Melee Defence / Weapon Strength / Splash Attack Power (imbuements and
  attributes ignored; standing rule 9). These are implemented with the standard
  in-melee self activation and are listed in **Appendix A** — no answer needed.
- **Excluded** — army-bar abilities (standing rule 10) and unsuitable abilities
  (vortex / ranged / movement / charge-utility). Listed in **Appendix B** with reasons.
- **Auto-rejected** — any mutually-exclusive ability (standing rule 8).

Source per item: the game's own effects, taken wiki-first
(`totalwarwarhammer.fandom.com/wiki/<Name>_(ability)`, the infobox `effects` line verbatim);
where no wiki page carries the ability, the line is reconstructed from the game-data
tables and marked **“(other source)”**.

## Summary

| Block | Items scanned | Questions to answer | Auto-accepted (trivial) | Excluded (skip) |
|---|---|---|---|---|
| **Block 7** (#254–#293) | 40 | **22** | 2 | 16 |
| **Block 8** (#294–#333) | 40 | **23** | 2 | 15 |
| **Block 9** (#334–#373) | 40 | **30** | 0 | 10 |
| **TOTAL** | **120** | **75** | **4** | **41** |

_The questions are numbered with their original tracker §2 number so you can cross-reference._

---

## Block 7 — questions (22 items)

_Tracker items §2 #254–#293._

### 255. Skull of Katam
- Key(s): `wh_main_item_abilities_skull_of_katam`
- Effects: Active Ability; Type: Hex of the Winds; Uses: 1; Damage Per Second: 16-33; Spell Mastery: +40%; Duration: 27s; Cooldown: 60s; Causes damage to self
- Owner: not unit-innate — item/weapon ability (equip-granted)
- Flags: none
- Proposed activation: when in melee and not fleeing - cast on self
- Your answer: _

### 256. Slayer for Chaos
- Key(s): `wh3_dlc23_item_abilities_slayer_for_chaos`
- Effects: Melee Attack: +12; Can Cause Terror; Unbreakable; Cannot Die
- Owner: not unit-innate — item/weapon ability (equip-granted)
- Flags: none
- Proposed activation: when in melee and not fleeing - cast on self
- Your answer: _

### 258. The Black Gem of Gnar
- Key(s): `wh3_dlc23_item_abilities_black_gem_of_gnar`
- Effects: Melee Attack: -100%; Invulnerable
- Owner: not unit-innate — item/weapon ability (equip-granted)
- Flags: drawback
- Proposed activation: when in melee and not fleeing - cast on self
- Your answer: _

### 261. Vial of Troll Blood
- Key(s): `wh_dlc08_item_abilities_vial_of_troll_blood`
- Effects: Unbreakable
- Owner: not unit-innate — item/weapon ability (equip-granted)
- Flags: none
- Proposed activation: when in melee and not fleeing - cast on self
- Your answer: _

### 262. Warpstone Addiction
- Key(s): `wh3_dlc29_lord_abilities_warpstone_addiction`
- Effects: Damage Resistance: +33 (other source)
- Owner: Thanquol
- Flags: none
- Proposed activation: when in melee and not fleeing - cast on self
- Your answer: _

### 265. Witchbrew
- Key(s): `wh2_main_character_abilities_witchbrew`, `wh3_dlc24_unit_abilities_witchbrew`
- Effects: Base Weapon Damage: +50%; Armour-Piercing Weapon Damage: +50%; Melee Attack: +24; Rampage!
- Owner: Crone Hellebron, Death Hag, Sisters of the Singing Doom (Witch Elves), Witch Elves
- Flags: rampage
- Proposed activation: when in melee and not fleeing - cast on self
- Your answer: _

### 266. World's Edge Armour
- Key(s): `wh2_main_item_abilities_worlds_edge_armour`
- Effects: Armour: +60
- Owner: not unit-innate — item/weapon ability (equip-granted)
- Flags: none
- Proposed activation: when in melee and not fleeing - cast on self
- Your answer: _

### 268. Znarkharja's Ward
- Key(s): `wh3_dlc24_hero_abilities_znarkharjas_ward`
- Effects: Damage Resistance: +10%
- Owner: Hag Witch (Death)
- Flags: none
- Proposed activation: when in melee and not fleeing - cast on self
- Your answer: _

### 271. Battle of Wills
- Key(s): `wh3_dlc29_unit_abilities_battle_of_wills`
- Effects: Melee Attack: -24; Leadership: -8; Reload Skill: -40; Must Resist [to enemies in range] (other source)
- Owner: Lahmian Vampire Lord, Vampire Lord, Neferata, Coven Throne; unit set(s): mp_cap_unit_vmp_veh_coven_throne
- Flags: none
- Proposed activation: when in melee and not fleeing - cast on self
- Your answer: _

### 275. Ferocious Battle Howl
- Key(s): `wh3_dlc29_spell_bound_prayer_ferocious_battle_howl`
- Effects: Charge Speed: +50%; Speed: +25%; Charge Bonus: +40%; Mass: +50% [to self and allies] (other source)
- Owner: Emil Valgeir
- Flags: none
- Proposed activation: charge and in melee (and not fleeing) - cast on self
- Your answer: _

### 277. Ferocious Fury of Ulric
- Key(s): `wh3_dlc29_spell_bound_prayer_ferocious_fury_of_ulric`
- Effects: Can Cause Fear; Unbreakable [to self and allies] (other source)
- Owner: Emil Valgeir
- Flags: none
- Proposed activation: when in melee and not fleeing - cast on self
- Your answer: _

### 278. Ferocious Winter’s Chill
- Key(s): `wh3_dlc29_spell_bound_prayer_ferocious_winters_chill`
- Effects: Melee Attack: -24; Armour-Piercing Weapon Damage: -30%; Base Weapon Damage: -30%; Melee Defence: -24 [to enemies in range] (other source)
- Owner: Emil Valgeir
- Flags: none
- Proposed activation: when in melee and not fleeing - cast on self
- Your answer: _

### 279. Flame Incarnate
- Key(s): `wh3_main_character_abilities_flame_incarnate`
- Effects: Melee Damage Reflection: +14
- Owner: Firebelly
- Flags: none
- Proposed activation: when in melee and not fleeing - cast on self
- Your answer: _

### 280. Formless Horror
- Key(s): `wh3_dlc24_lord_abilities_formless_horror`, `wh3_dlc24_lord_abilities_formless_horror_quest_battle`
- Effects: <unknown> (other source)
- Owner: The Changeling
- Flags: none
- Proposed activation: when in melee and not fleeing - cast on self
- Your answer: _

### 281. Fury of Ulric
- Key(s): `wh3_dlc29_spell_bound_prayer_fury_of_ulric`
- Effects: Leadership: +8; Can Cause Fear [to self and allies] (other source)
- Owner: Priest of Ulric
- Flags: none
- Proposed activation: when in melee and not fleeing - cast on self
- Your answer: _

### 283. Immovable Bulwark
- Key(s): `wh3_dlc26_unit_abilities_immovable_bulwark`
- Effects: Melee Defence: +24; Melee Attack: -24
- Owner: Black Orcs, Krimson Killerz (Black Orcs); unit set(s): wh2_dlc11_grn_all_orc_infantry
- Flags: drawback
- Proposed activation: when in melee and not fleeing - cast on self
- Your answer: _

### 285. Primeval Roar
- Key(s): `wh2_dlc17_unit_abilities_primeval_roar`
- Effects: Melee Attack: +24
- Owner: The Pale Death (Feral Troglodon)
- Flags: none
- Proposed activation: when in melee and not fleeing - cast on self
- Your answer: _

### 286. Rune of Doom
- Key(s): `wh2_dlc17_lord_abilities_rune_of_doom`
- Effects: Type: Augment (area); Duration: 16 Seconds; Cooldown: 90 Seconds; Target: Self, affects allies in range; Effect Range: Map-wide; +24 Melee attack; Can cause Fear
- Owner: Thorek Ironbrow
- Flags: none
- Proposed activation: when in melee and not fleeing - cast on self
- Your answer: _

### 290. The Shadow's Coil
- Key(s): `wh_dlc05_unit_abilities_the_shadows_coil`
- Effects: Melee Defence: +24; Melee Attack: -24
- Owner: Bladesingers, Wardancers, Loec's Tricksters (Wardancers – Asrai Spears); unit set(s): wh2_twa02_wef_glade_captain_unmounted
- Flags: drawback
- Proposed activation: when in melee and not fleeing - cast on self
- Your answer: _

### 291. Transformation of the Dragon
- Key(s): `wh3_dlc24_lord_abilities_jade_dragon_dragon_form`, `wh3_main_lord_abilities_iron_dragon_dragon_form`, `wh3_main_lord_abilities_storm_dragon_dragon_form`
- Effects: Transform to Dragon form; Form offers powerful melee attacks and flight; Restricted spell availability and reduction in Harmony multiplier (other source)
- Owner: Yuan Bo, the Jade Dragon, Zhao Ming, the Iron Dragon, Miao Ying, the Storm Dragon
- Flags: none
- Proposed activation: when in melee and not fleeing - cast on self
- Your answer: _

### 292. Unstoppable Choppas
- Key(s): `wh3_dlc26_unit_abilities_unstoppable_choppas`
- Effects: Base Weapon Damage: +50%; Armour-Piercing Weapon Damage: +50%; Melee Defence: -24
- Owner: Krimson Killerz (Black Orcs), Black Orcs (Great Weapons); unit set(s): wh2_dlc11_grn_all_orc_infantry
- Flags: drawback
- Proposed activation: when in melee and not fleeing - cast on self
- Your answer: _

### 293. Winter’s Chill
- Key(s): `wh3_dlc29_ability_bound_prayer_winters_chill`, `wh3_dlc29_spell_bound_prayer_winters_chill`
- Effects: Melee Attack: -24; Armour-Piercing Weapon Damage: -30%; Base Weapon Damage: -30% [to enemies in range] (other source)
- Owner: Order of the Axe (Teutogen Guard), Priest of Ulric
- Flags: none
- Proposed activation: when in melee and not fleeing - cast on self
- Your answer: _

---

## Block 8 — questions (23 items)

_Tracker items §2 #294–#333._

### 295. Bangers & Smash
- Key(s): `wh2_dlc15_character_abilities_sausage_busta`
- Effects: Charge Bonus: +20%; Leadership: +12
- Owner: not unit-innate (granted by character skill)
- Flags: none
- Proposed activation: charge and in melee (and not fleeing) - cast on self
- Your answer: _

### 298. Death Frenzy
- Key(s): `wh2_dlc16_spell_bound_death_frenzy`
- Effects: Melee Attack: +24; Armour-Piercing Weapon Damage: +30%; Base Weapon Damage: +30%; Immune to Psychology [to self and allies] (other source)
- Owner: not unit-innate (granted by character skill)
- Flags: none
- Proposed activation: when in melee and not fleeing - cast on self
- Your answer: _

### 299. Dragonhorn
- Key(s): `wh2_dlc15_lord_abilities_dragonhorn`
- Effects: Melee Attack: +24; Can Cause Fear
- Owner: Imrik
- Flags: none
- Proposed activation: when in melee and not fleeing - cast on self
- Your answer: _

### 302. Greater Faith Bastion
- Key(s): `wh_dlc06_quest_abilities_grand_faiths_bastion`
- Effects: Damage Resistance: +90 [to self and allies] (other source)
- Owner: Arch Lector
- Flags: none
- Proposed activation: when in melee and not fleeing - cast on self
- Your answer: _

### 305. Cash Cascade
- Key(s): `wh3_dlc26_character_abilities_cash_cascade`
- Effects: Charge Bonus: +25%; Melee Attack: +24; Leadership: +8
- Owner: Ogre Paymaster, Greasus Goldtooth
- Flags: none
- Proposed activation: charge and in melee (and not fleeing) - cast on self
- Your answer: _

### 306. Empowering Shrooms
- Key(s): `wh3_dlc26_character_abilities_empowering_shrooms`
- Effects: Melee Attack: +24; Leadership: +16; Stops Rampage! [to allies in range] (other source)
- Owner: Night Goblin Big Boss
- Flags: rampage
- Proposed activation: when in melee and not fleeing - cast on self
- Your answer: _

### 307. Enchanted Metallurgy
- Key(s): `wh3_main_character_abilities_enchanted_metallurgy`
- Effects: Base Weapon Damage: +30%; Base Missile Damage: +25%
- Owner: Alchemist; unit set(s): wh3_main_cth_cha_alchemist_0
- Flags: none
- Proposed activation: when in melee and not fleeing - cast on self
- Your answer: _

### 308. Enchanted Metallurgy: Flaming
- Key(s): `wh3_main_character_abilities_enchanted_metallurgy_flaming`
- Effects: Base Weapon Damage: +60%; Base Missile Damage: +50%
- Owner: not unit-innate (granted by character skill)
- Flags: none
- Proposed activation: when in melee and not fleeing - cast on self
- Your answer: _

### 309. Enchanted Metallurgy: Piercing
- Key(s): `wh3_main_character_abilities_enchanted_metallurgy_piercing`
- Effects: Armour-Piercing Missile Damage: +25%; Base Missile Damage: +25%; Base Weapon Damage: +25%; Armour-Piercing Weapon Damage: +25%
- Owner: not unit-innate (granted by character skill)
- Flags: none
- Proposed activation: when in melee and not fleeing - cast on self
- Your answer: _

### 310. Enchanted Metallurgy: Poison
- Key(s): `wh3_main_character_abilities_enchanted_metallurgy_poison`
- Effects: Base Missile Damage: +30%; Base Weapon Damage: +25%
- Owner: not unit-innate (granted by character skill)
- Flags: none
- Proposed activation: when in melee and not fleeing - cast on self
- Your answer: _

### 312. Massacre
- Key(s): `wh3_main_prisoners_massacre`
- Effects: Base Weapon Damage: +25%; Armour-Piercing Weapon Damage: +25%; Melee Attack: +24
- Owner: army of: The Maneaters, Blood Guzzlers, Bloodmaw
- Flags: none
- Proposed activation: when in melee and not fleeing - cast on self
- Your answer: _

### 313. Master of Alchemy
- Key(s): `wh3_main_lord_abilities_master_of_alchemy`
- Effects: Base Weapon Damage: +30%; Base Missile Damage: +25%
- Owner: Zhao Ming, the Iron Dragon; unit set(s): wh3_main_cth_cha_iron_dragon_0
- Flags: none
- Proposed activation: when in melee and not fleeing - cast on self
- Your answer: _

### 314. Master of Alchemy: Flaming
- Key(s): `wh3_main_lord_abilities_master_of_alchemy_flaming`
- Effects: Base Weapon Damage: +60%; Base Missile Damage: +50%
- Owner: unit set(s): wh3_main_cth_cha_iron_dragon_0
- Flags: none
- Proposed activation: when in melee and not fleeing - cast on self
- Your answer: _

### 315. Master of Alchemy: Piercing
- Key(s): `wh3_main_lord_abilities_master_of_alchemy_piercing`
- Effects: Armour-Piercing Missile Damage: +25%; Base Missile Damage: +25%; Base Weapon Damage: +25%; Armour-Piercing Weapon Damage: +25%
- Owner: unit set(s): wh3_main_cth_cha_iron_dragon_0
- Flags: none
- Proposed activation: when in melee and not fleeing - cast on self
- Your answer: _

### 316. Master of Alchemy: Poison
- Key(s): `wh3_main_lord_abilities_master_of_alchemy_poison`
- Effects: Base Weapon Damage: +30%; Base Missile Damage: +25%
- Owner: unit set(s): wh3_main_cth_cha_iron_dragon_0
- Flags: none
- Proposed activation: when in melee and not fleeing - cast on self
- Your answer: _

### 317. Spite of Da Bad Moon
- Key(s): `wh_dlc06_lord_abilities_spite_of_da_bad_moon`
- Effects: Base Weapon Damage: +25%; Armour-Piercing Weapon Damage: +25%; Bonus vs. Large: 16
- Owner: Night Goblin Warboss, Skarsnik
- Flags: none
- Proposed activation: when in melee and not fleeing - cast on self
- Your answer: _

### 319. "Stay Here, I'll Get Help!"
- Key(s): `wh2_dlc09_character_abilities_stay_here_ill_get_help`
- Effects: Self; Unspottable; Stalk; Ally; Leadership: +16
- Owner: Tretch Craventail
- Flags: none
- Proposed activation: when in melee and not fleeing - cast on self
- Your answer: _

### 321. Breath of Hatred
- Key(s): `wh3_dlc23_bound_abilities_breath_of_hatred`, `wh3_dlc23_character_abilities_breath_of_hatred`
- Effects: Melee Attack: +24
- Owner: not unit-innate — bound ability (item/skill-granted)
- Flags: none
- Proposed activation: when in melee and not fleeing - cast on self
- Your answer: _

### 322. Master Rune of Oath & Steel
- Key(s): `wh_dlc06_rune_abilities_master_rune_of_oath_and_steel`
- Effects: +60  Armour
- Owner: not unit-innate — rune ability (Dwarf runesmiths/lords)
- Flags: none
- Proposed activation: when in melee and not fleeing - cast on self
- Your answer: _

### 323. Master Rune of Speed
- Key(s): `wh2_dlc17_rune_abilities_master_rune_of_speed`
- Effects: Speed: +45%; Melee Attack: +24 [to self and allies]; Extended effect duration (other source)
- Owner: not unit-innate — rune ability (Dwarf runesmiths/lords)
- Flags: none
- Proposed activation: when in melee and not fleeing - cast on self
- Your answer: _

### 324. Rune of Oath & Steel
- Key(s): `wh_main_rune_abilities_rune_of_oath_and_steel`
- Effects: +30  Armour
- Owner: Runelord, Runesmith, Throni Ironbrow, Thorek Ironbrow; lore/group: Runic Magic
- Flags: none
- Proposed activation: when in melee and not fleeing - cast on self
- Your answer: _

### 325. Rune of Speed
- Key(s): `wh2_dlc17_rune_abilities_rune_of_speed`
- Effects: Type: Augment (area); Duration: 18 Seconds; Cooldown: 120 Seconds; Target: Self, ground, ally 100m; Effect Range: 40m; +45% Speed; +24 Melee attack
- Owner: Runelord, Runesmith, Throni Ironbrow, Thorek Ironbrow; lore/group: Runic Magic
- Flags: none
- Proposed activation: when in melee and not fleeing - cast on self
- Your answer: _

### 326. Birona's Timewarp
- Key(s): `wh_main_spell_bound_bironas_timewarp`
- Effects: Charge Speed: +25%; Speed: +25%; Melee Attack: +24 [to self and allies] (other source)
- Owner: Spirit of Tepok (Coatl)
- Flags: none
- Proposed activation: when in melee and not fleeing - cast on self
- Your answer: _

---

## Block 9 — questions (30 items)

_Tracker items §2 #334–#373._

### 335. From the Shadows
- Key(s): `wh2_dlc14_character_abilities_from_the_shadows`
- Effects: Unspottable; Stalk; Snipe
- Owner: not unit-innate (granted by character skill)
- Flags: none
- Proposed activation: when in melee and not fleeing - cast on self
- Your answer: _

### 336. Lord of Grand Cathay
- Key(s): `wh3_dlc24_lord_abilities_lord_of_grand_cathay`
- Effects: Melee Defence: +40; Physical Resistance: +20%
- Owner: Celestial General
- Flags: none
- Proposed activation: when in melee and not fleeing - cast on self
- Your answer: _

### 337. Shield of the Old Ones
- Key(s): `wh2_main_character_abilities_shield_of_the_old_ones`
- Effects: Damage Resistance: +20%; Leadership: +8
- Owner: Slann Mage-Priest (Beasts), Slann Mage-Priest (Death), Slann Mage-Priest (Fire), Slann Mage-Priest (Life), Slann Mage-Priest (Metal) (+6 more)
- Flags: none
- Proposed activation: when in melee and not fleeing - cast on self
- Your answer: _

### 338. Supreme Shield of the Old Ones
- Key(s): `wh2_dlc12_character_abilities_supreme_shield_of_the_old_ones`
- Effects: Damage Resistance: +40%
- Owner: Lord Kroak
- Flags: none
- Proposed activation: when in melee and not fleeing - cast on self
- Your answer: _

### 339. Gaze of Khaine
- Key(s): `wh2_dlc10_lord_abilities_gaze_of_khaine`
- Effects: Base Weapon Damage: +25%; Armour-Piercing Weapon Damage: +25%; Melee Attack: +24; Leadership: +8; Rampage!
- Owner: Crone Hellebron
- Flags: rampage
- Proposed activation: when in melee and not fleeing - cast on self
- Your answer: _

### 343. Star of Avelorn
- Key(s): `wh2_dlc10_item_abilities_star_of_avelorn`
- Effects: Heal Per Second: +0.80%
- Owner: not unit-innate — item/weapon ability (equip-granted)
- Flags: none
- Proposed activation: when in melee and not fleeing - cast on self
- Your answer: _

### 344. The Liber Mortis
- Key(s): `wh2_dlc09_lord_abilities_the_liber_mortis`
- Effects: Physical Resistance: +40%; Leadership: +8
- Owner: Arkhan the Black; unit set(s): cha_arkhan
- Flags: none
- Proposed activation: when in melee and not fleeing - cast on self
- Your answer: _

### 345. Gulyas
- Key(s): `wh3_dlc24_lord_abilities_gulyas`
- Effects: Heal Per Second: +0.08%; Leadership: +4; Vigour per second: -1%
- Owner: Mother Ostankya
- Flags: none
- Proposed activation: when in melee and not fleeing - cast on self
- Your answer: _

### 346. Mirror of Knowledge
- Key(s): `wh3_dlc24_item_abilities_mirror_of_knowledge`
- Effects: Speed: -25%; Reveals Unit [to enemies in range] (other source)
- Owner: not unit-innate — item/weapon ability (equip-granted)
- Flags: none
- Proposed activation: when in melee and not fleeing - cast on self
- Your answer: _

### 349. Fog of the Damned
- Key(s): `wh3_dlc29_bound_deep_fog_of_the_damned`
- Effects: Melee Attack: -24; Leadership: -8 [to enemies in range] (other source)
- Owner: unit set(s): nag_mourngul_haunter_banshee
- Flags: none
- Proposed activation: when in melee and not fleeing - cast on self
- Your answer: _

### 354. Bastion's Defenders
- Key(s): `wh3_dlc24_character_abilities_bastions_defenders`
- Effects: Melee Defence: +24; Immune to Flanking
- Owner: Gate Master; unit set(s): wh3_dlc24_cth_cha_gate_master
- Flags: none
- Proposed activation: when in melee and not fleeing - cast on self
- Your answer: _

### 355. Beastlord's Gaze
- Key(s): `wh2_twa03_lord_abilities_beastlords_gaze`
- Effects: Leadership: +16; Damage Resistnace: +10%; Stops Rampage!
- Owner: Rakarth
- Flags: rampage
- Proposed activation: when in melee and not fleeing - cast on self
- Your answer: _

### 356. Captain of the Phoenix Guard
- Key(s): `wh3_dlc27_character_abilities_captain_of_the_phoenix_guard`
- Effects: Heal Per Second: +0.50%; Physical Resistance: +30 [to allies in range]; Replenishes hit points of combatants (other source)
- Owner: Caradryan
- Flags: none
- Proposed activation: when in melee and not fleeing - cast on self
- Your answer: _

### 357. Da Boss 'as a Plan!
- Key(s): `wh3_dlc26_character_abilities_da_boss_as_a_plan`
- Effects: Melee Defence: +24; Leadership: +8; Expert Charge Defence
- Owner: Gorbad Ironclaw
- Flags: none
- Proposed activation: when in melee and not fleeing - cast on self
- Your answer: _

### 358. Favour of the Fay
- Key(s): `wh_dlc07_lord_abilities_favour_of_the_fay`
- Effects: Melee Attack: +40
- Owner: Fay Enchantress
- Flags: none
- Proposed activation: when in melee and not fleeing - cast on self
- Your answer: _

### 359. Fury of Khaine
- Key(s): `wh2_main_unit_abilities_fury_of_khaine`
- Effects: Base Weapon Damage: +30%; Charge Bonus: +20%; Melee Attack: +24; Rampage!
- Owner: Crone Hellebron, Death Hag
- Flags: rampage
- Proposed activation: when in melee and not fleeing - cast on self
- Your answer: _

### 360. Helm of Yvresse
- Key(s): `wh2_dlc15_item_abilities_helm_of_yvresse`
- Effects: Unbreakable; Cannot Die
- Owner: not unit-innate — item/weapon ability (equip-granted)
- Flags: none
- Proposed activation: when in melee and not fleeing - cast on self
- Your answer: _

### 361. Helping Hand
- Key(s): `wh2_pro08_character_abilities_helping_hand`
- Effects: Melee Attack: +40; Damage Resistance: +40%
- Owner: Felix
- Flags: none
- Proposed activation: when in melee and not fleeing - cast on self
- Your answer: _

### 362. Inspired Assault I
- Key(s): `wh3_main_lord_abilities_inspired_assault_i`
- Effects: Charge Bonus: +20%; Melee Attack: +24
- Owner: Lord Magistrate
- Flags: none
- Proposed activation: charge and in melee (and not fleeing) - cast on self
- Your answer: _

### 363. Inspired Assault II
- Key(s): `wh3_main_lord_abilities_inspired_assault_ii`
- Effects: Charge Bonus: +40%; Melee Attack: +24
- Owner: not unit-innate (granted by character skill)
- Flags: none
- Proposed activation: charge and in melee (and not fleeing) - cast on self
- Your answer: _

### 364. Inspired Assault III
- Key(s): `wh3_main_lord_abilities_inspired_assault_iii`
- Effects: Charge Bonus: +40%; Melee Attack: +40
- Owner: not unit-innate (granted by character skill)
- Flags: none
- Proposed activation: charge and in melee (and not fleeing) - cast on self
- Your answer: _

### 365. Inspired Defence I
- Key(s): `wh3_main_lord_abilities_inspired_defence_i`
- Effects: Melee Defence: +24; Leadership: +16
- Owner: Lord Magistrate
- Flags: none
- Proposed activation: when in melee and not fleeing - cast on self
- Your answer: _

### 366. Inspired Defence II
- Key(s): `wh3_main_lord_abilities_inspired_defence_ii`
- Effects: Melee Defence: +24; Leadership: +16; Expert Charge Defence
- Owner: not unit-innate (granted by character skill)
- Flags: none
- Proposed activation: when in melee and not fleeing - cast on self
- Your answer: _

### 367. Inspired Defence III
- Key(s): `wh3_main_lord_abilities_inspired_defence_iii`
- Effects: Melee Defence: +40; Leadership: +16; Expert Charge Defence
- Owner: not unit-innate (granted by character skill)
- Flags: none
- Proposed activation: when in melee and not fleeing - cast on self
- Your answer: _

### 368. Mantra of Invigoration
- Key(s): `wh3_cp1_character_abilities_protection_prayer`
- Effects: Heal Per Second: +0.65%; Vigour per second: -1%
- Owner: Clawspeaker (Life)
- Flags: none
- Proposed activation: when in melee and not fleeing - cast on self
- Your answer: _

### 369. Mantra of Righteousness
- Key(s): `wh3_cp1_character_abilities_offense_prayer`
- Effects: Imbuement: Sundered Armour; Base Weapon Damage: +25%; Armour-Piercing Weapon Damage: +25%; Melee Attack: +24
- Owner: Clawspeaker (Beasts)
- Flags: none
- Proposed activation: when in melee and not fleeing - cast on self
- Your answer: _

### 370. Meat Feast
- Key(s): `wh3_main_prisoners_butcher`
- Effects: Heal Per Second: +1.54%; Vigour per second: -3%
- Owner: army of: The Maneaters, Blood Guzzlers, Bloodmaw
- Flags: none
- Proposed activation: when in melee and not fleeing - cast on self
- Your answer: _

### 371. Offering to the Gods
- Key(s): `wh3_dlc27_lord_abilities_offering_to_the_gods`
- Effects: Damage: 400 every 1s [to allies in range]; Melee Attack: +40; Armour-Piercing Weapon Damage: +20%; Base Weapon Damage: +20%; Leadership: +16 [to allies in range]; Kills entities of targeted ally (other source)
- Owner: Great Shaman-Sorcerer (Death), Great Shaman-Sorcerer (Fire), Great Shaman-Sorcerer (Metal)
- Flags: friendly-fire
- Proposed activation: when in melee and not fleeing - cast on self
- Your answer: _

### 372. Orcs are da Best!
- Key(s): `wh3_dlc26_character_abilities_orcs_are_da_best`
- Effects: Base Weapon Damage: +50%; Armour-Piercing Weapon Damage: +50%; Melee Attack: +24
- Owner: Gorbad Ironclaw
- Flags: none
- Proposed activation: when in melee and not fleeing - cast on self
- Your answer: _

### 373. Overseer of the Unseen
- Key(s): `wh3_dlc29_hero_active_overseer_of_the_unseen`
- Effects: Melee Attack: +40; Cannot Die; Unbreakable [to allies in range] (other source)
- Owner: Morbidex Twiceborn
- Flags: none
- Proposed activation: when in melee and not fleeing - cast on self
- Your answer: _

---

## Appendix A — AUTO-ACCEPTED (trivial self-buffs, no answer needed)

These are implemented with the standard in-melee self activation (standing rule 9).
They are **not** questions.

**Block 7:**

- **Talisman of Loec** (#257) — `wh2_main_item_abilities_talisman_of_loec`
  - Effects: Base Weapon Damage: +30%; Melee Attack: +24
  - Owner: not unit-innate — item/weapon ability (equip-granted)
- **Warrior Familiar** (#263) — `wh3_dlc27_item_abilities_warrior_familiar`
  - Effects: Melee Attack: +24; Melee Defence: +24 (other source)
  - Owner: not unit-innate — item/weapon ability (equip-granted)

**Block 8:**

- **Curse of Years** (#297) — `wh3_dlc29_spell_bound_curse_of_years`
  - Effects: Imbuement: wh3_dlc29_unit_contact_curse_of_years (other source)
  - Owner: unit set(s): mp_cap_unit_vmp_inf_lahmian_handmaidens_death
- **Okkam's Mindrazor** (#303) — `wh3_dlc29_spell_bound_okkams_mindrazor`
  - Effects: Imbuement:  Magical Attacks; Base Weapon Damage: +50%; Armour-Piercing Weapon Damage: +50%
  - Owner: Lahmian Handmaidens (Shadows); unit set(s): mp_cap_unit_vmp_inf_lahmian_handmaidens_shadow

**Block 9:** none.

---

## Appendix B — EXCLUDED (with reason)

Army-bar abilities are skipped per standing rule 10 (“Skip all army bar abilities”).
Vortex / ranged / movement / charge-utility abilities are unsuitable for in-melee self automation.

**Block 7:**

| # | Ability | Reason |
|---|---|---|
| 254 | Shanty: Third Verse | army-bar ability |
| 259 | Thundermace | vortex |
| 260 | Venom Wave | vortex |
| 264 | Whirlwind of Death | vortex |
| 267 | Wrath of Ptra | vortex |
| 269 | Ark of Sotek | vortex |
| 270 | Battle Howl | movement |
| 272 | Call of Tor | bombardment/ranged |
| 273 | Celestial Sweep | vortex |
| 274 | Destruction | vortex |
| 276 | Ferocious Destruction | vortex |
| 282 | Grand Soulfire | bombardment/ranged |
| 284 | Kill for Khorne! | vortex |
| 287 | Sonic Boom | vortex |
| 288 | Soulfire | bombardment/ranged |
| 289 | The Hammer of Harry | vortex |

**Block 8:**

| # | Ability | Reason |
|---|---|---|
| 294 | Alakanash, the Staff of Power | vortex |
| 296 | Cellular Instability | vortex |
| 300 | Eruption | vortex |
| 301 | Glacial Blast | vortex |
| 304 | Splode da Big 'Un! | vortex |
| 311 | Horn of Khorne | army-bar ability |
| 318 | Twilight Horn II | movement |
| 320 | Armour of Contempt | army-bar ability |
| 327 | Gate of Khorne | spawned/ranged |
| 328 | Gate of Nurgle | spawned/ranged |
| 329 | Gate of Slaanesh | spawned/ranged |
| 330 | Greater Gate of Khorne | spawned/ranged |
| 331 | Greater Gate of Nurgle | spawned/ranged |
| 332 | Greater Gate of Slaanesh | spawned/ranged |
| 333 | Greater Gate of Tzeentch | spawned/ranged |

**Block 9:**

| # | Ability | Reason |
|---|---|---|
| 334 | The Tallyman's Blades | spawned/ranged |
| 340 | Mors Clanstone | army-bar ability |
| 341 | Pestilens Clanstone | army-bar ability |
| 342 | Rictus Clanstone | army-bar ability |
| 347 | Ancestral Rune of Grungni | army-bar ability |
| 348 | Basking in Our Flame | army-bar ability |
| 350 | The Airless Fires | army-bar ability |
| 351 | The Burning Waters | army-bar ability |
| 352 | The Unmasking | army-bar ability |
| 353 | Time Amok | movement |

