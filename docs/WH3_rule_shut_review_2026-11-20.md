# The 55 rule-shut abilities and the 9 "skipped (revisit)": one trigger per ability (proposals, 2026-11-20)

User, 2026-11-20: "Let's review those 55 abilities + the 'skipped (revisit)'".

## How this review was done

- **Scope:** 64 rows, one ability key each. 55 are shut by an old rule that you never ruled on one by one: the
  2026-10-09 family decisions (19 "own-troop damage", 7 "flanking / ambush", 2 "bombardment"), the 5 automatic
  "mutual exclusivity" rejects and 22 collection-time "unsuitable" skips. The other 9 are the ones you set to
  "skipped (revisit)" yourself; their tracker lines are quoted (rule 11).
- **Facts:** every effect, radius, duration, use count, range and target rule is from the game data
  (`tools\fact_sheet_open.py` plus the vortex, phase-target and phase-attribute tables). An unchecked claim is marked
  ASSUMPTION.
- **Ranges and radii** are given real, then at 70% (rule 3): 15 m -> 10, 25 -> 17, 30 -> 21, 35 -> 24, 55 -> 38,
  100 -> 70, 200 -> 140.
- **Look-alikes:** each proposal names the implemented abilities of the same shape and the ruling that put them there.
- **Proposals only (rule 9):** nothing changes until you rule. Write your ruling in the last column (or in chat).

### The headline finding: the "own-troop damage" rule was wrong for all 19 of its rows

The 2026-10-09 rule says these abilities *"deliberately damage your own units"*. The game data says otherwise: every
damage phase of all 19 targets **enemies only** (`phase_junc`: target_enemies = true, target_friends = false); the only
friendly phases are heals on the caster itself (Defiling Deluge, Plaguereaper, Reaper of Souls, Soul Stealer). One
ability has a friendly-fire side: Zefet-nebtar's 9 m knockback blast (`affects_allies = true`, no damage). So the reason
they were shut does not hold, and most of them have an implemented look-alike.

### Reads the proposals use

| Read | Status |
|---|---|
| In melee, wavering, routing, health %, under missile fire | exist |
| Charging / fresh contact (`charge_moment`) | exists (round 171) |
| A fast enemy closing on our units (`fast_enemy_near`) | exists |
| An enemy in melee within the aura (`enemy_melee_near`) | exists (round 177) |
| A large enemy in the fight (`fights_large`) | exists (round 177) |
| The blast clearance (none of ours within blast + 10 m) and the soldier count in a blast (`blast_cover`) | exist (rounds 159, 181) |
| The area-drain and single-drain pickers, the `flying` target class | exist (rounds 157-158) |
| The thickest group of enemies (`cluster_pick`, 24 m) | exists for spellcasters and shooters (round 174); NEW for enemies in melee |
| Hidden from the enemy (`unspottable`) | no read of our own visibility to the enemy: ASSUMPTION rows say so |

## 1. The "own-troop damage" rows (19): enemy damage only

**Self-centred damage auras** (the effect sits around the caster). Look-alikes: Banner of Hellfire, The Bane Spear,
The Nordland Runefang on `melee_unwavering`. A 35 m aura reaches well past the caster's own fight, so the existing
`enemy_melee_near` (round 177: the caster in melee, or an enemy within the 70% aura in melee) catches more of its value.

| # | Ability | Every effect (game data) | Options | Recommended | Ruling |
|---|---|---|---|---|---|
| 1 | Defiling Deluge (`wh3_twa08_unit_abilities_defiling_deluge`; Great Unclean One RoR) | enemies within 35 m: 5 damage a second to up to 25 models, 6 s; the caster heals 0.8% a second; 2 uses, recharge 120 s | **A** `melee_unwavering`. **B** `enemy_melee_near` (24 m). **C** `melee_health75` (in melee below 75%: the self-heal pays) | **B**: 6 s is short, so the enemies must stand still in reach; enemies in melee within 24 m do | |
| 2 | Murderous Exhortations (`wh3_dlc26_lord_abilities_murderous_exhortations`; Bloodspeaker) | enemies within 35 m: 5 damage a second to up to 10 models and morale -8, 20 s; 3 uses | **A** `melee_unwavering`. **B** `enemy_melee_near` (24 m) | **B**: the morale cut pays on enemies fighting (they waver sooner) | |
| 3 | Rod of Corruption (`wh2_main_item_abilities_rod_of_corruption`; item) | enemies within 35 m: 10 damage a second to up to 25 models, 11 s; 3 uses | **A** `melee_unwavering`. **B** `enemy_melee_near` (24 m) | **B** | |
| 4 | Wail of Malice (`wh2_dlc14_unit_abilities_wail_of_malice`; Bloodwrack Medusa RoR) | enemies within 35 m: 10 damage a second to up to 18 models, 7 s; 2 uses | **A** `melee_unwavering`. **B** `enemy_melee_near` (24 m) | **B** | |
| 5 | Plaguereaper (`wh3_dlc29_item_abilities_plaguereaper`; item) | enemies within 15 m: 12 damage a second to up to 4 models, 25 s; the caster heals 0.8% a second; 2 uses | **A** `melee_unwavering`. **B** `melee_health75` | **A**: a 15 m aura is the caster's own fight (as Bane Spear) | |
| 6 | Reaper of Souls (`wh2_dlc14_lord_abilities_reaper_of_souls`; Malus Darkblade, Tz'arkan) | enemies within 35 m: 96 damage a second to ONE model, 9 s; the caster heals 0.8% a second; recharge 90 s | **A** `melee_unwavering`. **B** `melee_vs_large` (the caster or an ally within 24 m fights a large enemy). **C** `melee_health75` | **B**: one model per tick; against a monster or hero all 864 damage lands on it, against infantry each tick kills at most one man (ASSUMPTION: which model the game picks) | |
| 7 | Shard Blade (`wh3_main_weapon_abilities_shard_blade`; item) | enemies within 15 m: 67 damage a second to ONE model and speed x0.55, 15 s; 2 uses | **A** `melee_unwavering`. **B** `melee_vs_large` | **B**, same reasoning as row 6; the slow is in melee, so rule 10 holds | |
| 8 | Web of Shadows (`wh2_main_weapon_abilities_web_of_shadows`; item) | enemies within 35 m: 67 damage a second to ONE model and speed x0.75, 17 s; 1 use | **A** `melee_unwavering`. **B** `melee_vs_large` | **B** (1 use: spend it on a big target) | |
| 9 | Warp-Quake (`wh2_dlc14_unit_abilities_warp_quake`; Warp Grinder) | enemies within 35 m (not flying): 5 damage every 0.5 s to up to 18 models and speed x0.75, 17 s; recharge 90 s | **A** `slow_aura` (in melee, or a fast enemy comes near; the family of Rock of Inevitability, round 171). **B** `enemy_melee_near` | **A**: rule 10 (enemy slows fire in melee or on the charge) | |

**Aimed area damage** (cast on an enemy or the ground). Look-alikes: the 7 area drains of round 158 on
`enemy_area_drain` (the most valuable infantry block with at least as many men as the effect's model cap, standing
still); the 10 single drains of round 157 on `enemy_single_drain` (your rulings: "Most valuable single" + "Standing
still").

| # | Ability | Every effect (game data) | Options | Recommended | Ruling |
|---|---|---|---|---|---|
| 10 | Flock of Doom (`wh3_dlc27_spell_bound_runecaller_flock_of_doom`; Cursed Ettin Runecaller) | 35 m area at range 100 m (70): 5 damage a second to up to 25 models, 6 s; 3 uses | **A** `enemy_area_drain`. **B** `enemy_ground_melee` (the nearest enemy in melee) | **A** (same shape as the round-158 drains) | |
| 11 | Flock of Doom (`wh3_main_spell_bound_flock_of_doom`) | same; 2 uses | same | **A** | |
| 12 | Flock of Doom (`wh_dlc08_spell_bound_flock_of_doom`) | same; 4 uses | same | **A** | |
| 13 | Sword of Daith (`wh_dlc05_weapon_abilities_daiths_sword`; Durthu) | 35 m area at 100 m (70): 5 damage a second to up to 25 models and armour -30, 17 s; 2 uses | **A** `enemy_area_drain`. **B** `enemy_large_shot` (armour first) | **A**: the armour cut pays most on a block our troops are about to hit; both pick standing blocks | |
| 14 | Zefet-nebtar, the Mortis Blade (`wh3_dlc29_item_abilities_zefet_nebtar_the_mortis_blade`; item) | on an enemy at 100 m (70): 50 damage once to up to 25 models within 15 m, damage turned into healing; a 9 m knockback blast that DOES hit our units (no damage); wind-up 1.5 s; 3 uses | **A** `enemy_area_drain` plus a clearance: none of ours within 19 m (9 + 10) of the target. **B** `enemy_blob_vortex` (the value pick, as Frost Dragon Scale, round 159) | **A**: the hit is per model, which the area-drain count measures; the clearance covers the knockback | |
| 15 | Ring of Corin (`wh2_main_spell_bound_ring_of_corin`; item) | on an enemy at 200 m (140): 67 damage a second to ONE model, 22 s; 2 uses | **A** `enemy_single_drain`. **B** `enemy_finisher` (the most hurt) | **A** (as the round-157 drains) | |
| 16 | Soul Stealer (`wh2_dlc10_spell_bound_soul_stealer_ror`; Slaanesh Harvesters RoR) | 35 m area at 100 m (70): 75 damage a second to ONE model, 12 s; the caster heals 0.8% a second; 1 use | **A** `enemy_single_drain`. **B** `enemy_area_drain` | **A**: one model per tick, so a single big target is worth most | |
| 17 | Soul Stealer (`wh3_dlc27_spell_bound_soul_stealer`; Druchii Anointed) | same; 1 use | same | **A** | |
| 18 | Warpstorm Scroll (`wh2_main_item_abilities_warpstorm_scroll`; item) | on a FLYING enemy only (the game refuses ground units) at 100 m (70): 67 damage a second to one model and speed x0.55, 29 s; 1 use | **A** `enemy_single_drain` with the `flying` class (Storm of the Night's class, round 158). **B** keep shut | **A** | |
| 19 | Raging Tornado (`wh3_dlc29_unit_abilities_raging_tornado`; Celestial Hurricanum) | ground under enemies at 100 m (70), 30 m area, 32 s in 4 steps: 2/4/6/8 damage a second to up to 25 models, speed x0.9 / 0.75 / 0.6 / 0.4; wind-up 5 s (cast animation); 3 uses | **A** NEW: under the thickest group of enemies in melee (`cluster_pick`, as the shooters' cluster of round 174). **B** `enemy_ground_melee` (the nearest enemy in melee). **C** `enemy_area_drain` | **A**: the damage grows over 32 s, so it needs enemies who stay; locked melees stay, and the slow in melee keeps rule 10 | |

## 2. The self-centred blasts (17; collection-time "unsuitable: vortex")

The same shape as round 159's group E: your rulings "Like Bloodstorm" (safe blasts on `melee_unwavering`, 13 entries),
`melee_clear` for blasts that hit our units (in melee, none of our other units within blast + 10 m), "Necrotic last"
(`last_stand_clear`), and round 181's Land Mine (60 soldiers in its 25 m blast). The game's own usage rules (for
example Sonic Boom: never while flying) are already honoured by the generated usage table.

| # | Ability | Every effect (game data) | Options | Recommended | Ruling |
|---|---|---|---|---|---|
| 20 | Alakanash, the Staff of Power (`wh3_dlc29_item_abilities_alakanash_the_staff_of_power`; item) | 7 pulses of a 14 m knockback blast, one every 3 s, following the caster; enemies within 10 m: 4 damage every 0.2 s to up to 10 models, 21 s; our units safe; 3 uses | **A** `melee_unwavering`. **B** `enemy_melee_near` | **A** (as Bloodstorm) | |
| 21 | Ark of Sotek (`wh2_dlc12_unit_abilities_ark_of_sotek`; Bastiladon) | a 15 m area at the caster's spot, 26 s: Sotek's poison on contact, 1 AP damage; our units safe | **A** `melee_unwavering`. **B** keep shut | **A** | |
| 22 | Celestial Sweep (`wh3_dlc24_lord_abilities_celestial_sweep`; Celestial General Yang) | a 6 m blast, 120 AP damage; the caster cannot move for 4 s; our units safe; never while flying | **A** `melee_unwavering`. **B** `melee_skip_commanders` | **A** | |
| 23 | Destruction (`wh3_dlc29_spell_bound_prayer_destruction`; Priest of Ulric) | a 15 m blast, 10 + 6 AP damage; our units safe; recharge 120 s | **A** `melee_unwavering` | **A** | |
| 24 | Eruption (`wh3_main_character_abilities_eruption`; Firebelly) | a 15 m blast, 25 fire damage; our units safe; 1 use | **A** `melee_unwavering`. **B** `melee_clear_block` without the clearance (60 soldiers in the blast: its only use) | **A** | |
| 25 | Ferocious Destruction (`wh3_dlc29_spell_bound_prayer_ferocious_destruction`; Emil Valgeir) | a 20 m blast, 12 + 8 AP damage, frostbite on contact; our units safe | **A** `melee_unwavering` | **A** | |
| 26 | Kill for Khorne! (`wh3_dlc26_character_abilities_kill_for_khorne`; Scyla Anfingrimm) | a 15 m blast, 8 + 16 AP damage; contact effect "rampage" on the enemies hit (ASSUMPTION: it makes them rampage); our units safe; wind-up 3 s | **A** `melee_unwavering` | **A** | |
| 27 | Sonic Boom (`wh3_main_daemon_head_abilities_sonic_boom`; Daemon Prince) | a 30 m blast, 4 AP damage, heavy knockback, "disorientated" on contact; our units safe; never while flying | **A** `melee_unwavering`. **B** `enemy_melee_near` (21 m) | **A** | |
| 28 | The Hammer of Harry (`wh3_pro11_weapon_abilities_the_hammer_of_harry`; item) | a 15 m blast, 12 + 24 AP damage, heavy knockback; the caster cannot move for 5 s; our units safe | **A** `melee_unwavering` | **A** | |
| 29 | Venom Wave (`wh2_dlc09_lord_abilities_venom_wave`; Khalida) | a 15 m blast, 16 damage, poison on contact; our units safe; 3 uses | **A** `melee_unwavering` | **A** | |
| 30 | Wrath of Ptra (`wh2_dlc09_lord_abilities_wrath_of_ptra`; Settra) | a 15 m blast, 16 fire damage; our units safe; 3 uses | **A** `melee_unwavering` | **A** | |
| 31 | Whirlwind of Death (`wh3_dlc25_unit_abilities_whirlwind_of_death`; Doomseekers) | a 4 m whirlwind around EVERY man, 4 AP damage, 4 s; they cannot move for 6 s; our units safe; 1 use | **A** `melee_unwavering`. **B** fresh contact only (entered melee at most 2 s ago: its one use at the moment of impact) | **A** | |
| 32 | Whirlwind of Death Upgraded (`wh3_dlc25_unit_abilities_whirlwind_of_death_upgraded`) | same, 6 AP damage | same | **A** | |
| 33 | Glacial Blast (`wh3_main_character_abilities_glacial_blast`; Ice Witch, Frost Maiden) | a 15 m blast, 10 + 5 AP damage, frostbite on contact; HITS OUR UNITS; wind-up 3 s; 3 uses | **A** `melee_clear` (none of ours within 25 m). **B** keep shut | **A** (as Burning Rage, Groundbreaker) | |
| 34 | Thundermace (`wh3_main_weapon_abilities_thundermace`; item) | a 10 m blast after 3 s, 48 + 24 AP damage, heavy knockback; HITS OUR UNITS; 3 uses | **A** `melee_clear` (none of ours within 20 m) | **A** | |
| 35 | Cellular Instability (`wh2_dlc16_unit_abilities_cellular_instability`) | a 25 m blast, 30 AP damage; HITS OUR UNITS; the caster takes 50 damage every 0.5 s for 6 s (600); 1 use | **A** `melee_clear_block` (as Land Mine: 60 soldiers in the blast, none of ours within 35 m). **B** `melee_clear`. **C** `last_stand_clear` | **A**: it costs the caster health, so it should buy a full blast; the 25 m blast is Land Mine's | |
| 36 | Splode da Big 'Un! (`wh3_dlc26_unit_abilities_splode_da_big_one`; a Da Plan unit) | the unit stands still 6.8 s, then a 30 m blast, 69 AP damage, HITS OUR UNITS, and the unit DIES; 1 use | **A** `last_stand_clear` ("Necrotic last"). **B** `melee_clear_block` with a higher floor. **C** keep shut | **A**: a unit that kills itself should only do it when it is dying anyway | |

## 3. Movement and charge (5; collection-time "unsuitable: movement" or "charge-only")

Look-alikes: **Ferocious Battle Howl** (the same priest, the same 55 m, 15 s, x1.25 speed, x1.25 charge speed, charge
bonus x1.2) and **Twilight Horn I** are on `charge_only`; Ursun's Roar is on `aura_charge`. These were skipped because
they raise speed, but each also raises the charge, which is a combat effect (rule 10: the trigger follows the effect).

| # | Ability | Every effect (game data) | Options | Recommended | Ruling |
|---|---|---|---|---|---|
| 37 | Battle Howl (`wh3_dlc29_ability_bound_prayer_battle_howl`; Hunting Hounds RoR) | the caster and allies within 55 m: speed x1.25, charge speed x1.25, charge bonus x1.2, 15 s | **A** `charge_only` (as Ferocious Battle Howl). **B** NEW aura charge: the caster or an ally within 38 m charges | **A**, the same as its twin | |
| 38 | Battle Howl (`wh3_dlc29_spell_bound_prayer_battle_howl`; Priest of Ulric) | same | same | **A** | |
| 39 | Twilight Horn II (`wh2_dlc16_item_abilities_twilight_horn_ii`; item) | allies within 35 m of a target (ally, ground or self, 200 m): speed x1.25, charge speed x1.25, charge bonus x1.2, 36 s | **A** `charge_only` on itself (as Twilight Horn I). **B** `self_or_ally_charge` (itself or the nearest charging ally, as Red Fury) | **B**: it reaches 140 m, so a charging ally is worth it even when the bearer is not charging | |
| 40 | Silver Horn of Vengeance (`wh_main_item_abilities_silver_horn_of_vengeance`; item; you deferred it 2026-11-01) | the caster and allies within 35 m: charge bonus +12, 22 s; recharge 60 s | **A** `charge_only`. **B** NEW aura charge: the caster or an ally within 24 m charges (`aura_charge` without its wavering arm: the horn gives no morale) | **B**: the bonus is for the whole group around the bearer | |
| 41 | Swiftness of Itzl (`wh2_main_character_abilities_swiftness_of_itzl`; Kroq-Gar) | the caster: speed x1.25, 32 s; a 25 m knockback ring around him (no damage) | **A** `charge_only`. **B** `melee_unwavering` (the knockback clears infantry around him). **C** keep shut (movement is the player's) | **A**: the knockback lands at the moment of impact and the speed carries the charge; I am least sure of this one | |

## 4. Flanking / stealth (7; the 2026-10-09 "flanking / ambush" rule)

Every row: the game's `stalk` and `unspottable` attributes (the unit can hide anywhere while it walks). The rule leaned
on your earlier ruling for escapes: *"the escape in melee is tactically relevant and must be chosen by player"*
(rejected (tactical escape), questionnaire). None of these rows moves the unit; they hide it. Five cannot be used in
melee at all (the game's `engaged_in_melee` usage rule) or are pure hides. ASSUMPTION for every option below: a hidden
unit stops being a target for enemy missiles. No battle read shows whether the enemy can see one of OUR units.

| # | Ability | Every effect (game data) | Options | Recommended | Ruling |
|---|---|---|---|---|---|
| 42 | Armour of the Stars (`wh2_main_item_abilities_armour_of_the_stars`; item) | hide (stalk, unspottable), 73 s; not in melee | **A** keep shut (stealth is the player's). **B** NEW: under missile fire, not in melee, not shooting. **C** when ready, not in melee | **A** | |
| 43 | Concealment Bombs (`wh2_main_character_abilities_concealment_bombs`; Assassin, Eshin Sorcerer, Snikch) | hide, 73 s; 3 uses; not in melee | same | **A** | |
| 44 | Concealment Bombs (`wh2_main_unit_abilities_concealment_bombs`; Death Runners, Eshin Triads, a Ratling Gun RoR) | same | same | **A** | |
| 45 | From the Shadows (`wh3_main_character_abilities_from_the_shadows`) | hide and speed x1.45, 38 s | same | **A** | |
| 46 | Hidden in Time (`wh3_main_lord_abilities_hidden_in_time`; Daemon Princes) | hide, 73 s; 2 uses; usable in melee | same, B also out of melee only (in melee it is the escape you ruled the player's) | **A** | |
| 47 | Loec's Shroud (`wh_pro04_unit_abilities_loecs_shroud`; Wardancers RoR, The Grey RoR) | hide and speed x1.25, 44 s | same | **A** | |
| 48 | Mirror (Loec's Shroud) (`wh2_dlc15_unit_abilities_mimic_loecs_shroud`) | same | same | **A** | |

My honest view: B is the only moment a hide clearly pays without taking a movement decision away from you, but it
rests on the ASSUMPTION above and these units usually hide to set up a flank you order. Keep shut unless you want B
tested in a battle first.

## 5. Mutual exclusivity (5; automatic reject)

All five last for ever once switched on (`active_time = -1`, recharge 30 s), and each unit carries a set of them: the
Zhangu War Drum plays one drum song at a time; Festus switches between harming and healing. They behave like
**stances**, which you parked (2026-11-01: never automated for now, a stance chooser is last priority).

| # | Ability | Every effect (game data) | Options | Recommended | Ruling |
|---|---|---|---|---|---|
| 49 | Bastion of the Great Cities (`wh3_dlc24_unit_abilities_bastion_of_the_great_cities`; Zhangu War Drum, RoR) | the drum and allies within 100 m: armour +24, until switched | **A** park with the stances. **B** chooser for the drum (below) | **A** | |
| 50 | Disdain of the Dragon Emperor (`wh3_dlc24_unit_abilities_disdain_of_the_dragon_emperor`; same) | allies within 100 m: melee attack +8, reload +10 | same | **A** | |
| 51 | Fury of the Falling Blade (`wh3_dlc24_unit_abilities_fury_of_the_falling_blade`; RoR only) | allies within 100 m: melee damage and AP damage x1.15 | same | **A** | |
| 52 | Harbinger of Pestilence (`wh3_dlc20_lord_abilities_harbinger_of_pestilence`; Festus) | enemies within 35 m: 4 damage a second to up to 6 models, until switched | **A** park. **B** chooser for Festus (below) | **A** | |
| 53 | Healing Elixirs (`wh3_dlc20_lord_abilities_healing_elixirs`; Festus) | the caster and allies within 35 m heal 0.1% a second, until switched | same | **A** | |

**Option B, if you want it now:** the drum plays Fury when 2+ allies within 70 m charge or fight (RoR), Bastion when
2+ allies within 70 m are under missile fire, Disdain otherwise in melee; Festus switches on Healing Elixirs when an
ally within 24 m is below 75% health and no enemy is within 24 m, Harbinger when an enemy within 24 m is in melee. Each
switch would wait for the 30 s recharge. This is the stance chooser in small, so it needs its own design round.

## 6. Bombardment (2; the 2026-10-09 rule)

| # | Ability | Every effect (game data) | Options | Recommended | Ruling |
|---|---|---|---|---|---|
| 54 | Bonecrusher (`wh3_dlc26_spell_bound_bonecrusher`; bound Great Maw spell) | an 8 m blast 3 s after landing, 32 + 32 AP damage; HITS OUR UNITS; range 200 m (140); never on flying targets; wind-up 3 s; 1 use | **A** `enemy_blob_vortex` (where the blast hurts the enemy most, none of ours within 18 m; as Frost Dragon Scale). **B** `enemy_strike` (the most valuable standing monster or character, as Siegebreaker) | **A**: the value pick already favours armoured and large targets for heavy AP | |
| 55 | Master Rune of Immolation (`wh2_dlc17_rune_abilities_master_rune_of_immolation`; a war machine rune) | 15 fire shells burst from under the war machine (6 m each), the rune made to destroy it before capture; switched on until it ends | **A** close it (destroying our own war machine is your call). **B** `last_stand_clear` (the crew in melee below 15%) | **A** | |

## 7. Your "skipped (revisit)" abilities (9)

| # | Ability | Every effect (game data) | Your earlier decision | Options | Recommended | Ruling |
|---|---|---|---|---|---|---|
| 56 | Beastlord's Gaze (`wh2_twa03_lord_abilities_beastlords_gaze`; Rakarth) | on an ally or itself at 200 m (140): morale +16, ward save +10%, rampage removed, 40 s; recharge 60 s | "Skip for now" (questionnaire #355) | **A** `ally_melee_risk` (an ally in melee that wavers or is badly hurt). **B** `wavering_ally_range`. **C** `melee_self_or_ally` | **A**: morale and ward pay on an ally under pressure; rampage has no read (round 137) | |
| 57 | Fog of the Damned (`wh3_dlc29_bound_deep_fog_of_the_damned`) | ground under enemies at 200 m (140), 35 m area: melee attack -24, morale -8, 35 s; not on flying; wind-up 3 s; 2 uses | "Skip for now" (#349) | **A** NEW: under the thickest group of enemies in melee (24 m cluster, as row 19). **B** `enemy_ground_melee` (the nearest enemy in melee). **C** at its own feet in melee (the old plan) | **A**: a melee-only cut (rule 10) over a 35 m area pays most on the biggest melee | |
| 58 | Locus of Contagion (`wh3_main_character_abilities_locus_of_contagion`) | enemies within 55 m: 5 damage a second to up to 25 models, 11 s; recharge 90 s | "Skip for now (revisit later)" (#108) | **A** `melee_unwavering`. **B** `enemy_melee_near` (38 m) | **B** (as rows 1-4) | |
| 59 | Mad Cap Mushrooms (`wh_main_hero_abilities_mad_cap_mushrooms`; Night Goblin Shaman) | the caster: ability recharge -30 (the game's `ability_recharge_change`; ASSUMPTION: seconds or percent), 50 s; 25% miscast chance | "Skip for now (effect is ability recharge, not combat)" (#113) | **A** `self_recharging` (while another of its abilities recharges). **B** keep shut | **A**: the recharge cut only pays while something recharges (Terrorgheist Skull's rule) | |
| 60 | Mirror of Knowledge (`wh3_dlc24_item_abilities_mirror_of_knowledge`; item) | ground, 55 m area: enemy speed x0.75, 40 s; wind-up 3 s; range -1 (ASSUMPTION: no limit; to check) | "Skip for now" (#346) | **A** `enemy_fast_near_ally` ground form (under a fast enemy closing on our units). **B** `slow_army` (an enemy charges the army, or in melee). **C** under the enemy melee cluster | **A**: rule 10, and 40 s of slow pays most against a charge | |
| 61 | Offering to the Gods (`wh3_dlc27_lord_abilities_offering_to_the_gods`; Shaman Sorcerers) | on one ally at 100 m (70; not a Lord, Hero or large unit): kills 3 of its models (400 damage each), then melee attack +40, melee damage x1.2, morale +16, 42 s | "Skip for now", sacrifice (#371) | **A** `ally_value_melee` with a floor: the most valuable infantry ally in melee with at least 30 men (3 lost = 10% or less). **B** the same on a charging ally. **C** keep shut | **A**, on the line you drew with Blood Sacrifice and Eat da Runts! (a cost paid by our own unit for its own buff) | |
| 62 | Seismic Snare (`wh2_dlc14_unit_abilities_seismic_snare`; Warp Grinder) | enemies within 35 m (not flying) cannot move, 13 s; recharge 60 s | "Skip for now" (#154) | **A** `slow_aura` (in melee, or a fast enemy comes near). **B** `guard_aura`. **C** keep shut | **A** (rule 10; as Rock of Inevitability) | |
| 63 | Seismic Snare (`wh3_dlc29_unit_abilities_stormfiend_seismic_snare`; Stormfiend) | same; 1 use | same | same | **A** | |
| 64 | The Black Gem of Gnar (`wh3_dlc23_item_abilities_black_gem_of_gnar`; item) | the caster is invulnerable and its melee attack is x0, 13 s; 3 uses | "Skip for now" (#258) | **A** `self_last_stand` (at or below 10% health, in melee or under fire, as Hag's Denial). **B** `self_hurt_attacked` (below 75% while attacked) | **A**: it stops the caster fighting, so only when survival is all that matters | |

## Summary

| Group | Rows | Recommended | Families |
|---|---:|---|---|
| "Own-troop damage" (the rule was wrong) | 19 | build all 19 | existing, plus NEW melee-cluster ground pick (row 19) and the area-drain clearance (row 14) |
| Self-centred blasts | 17 | build all 17 | existing (`melee_unwavering`, `melee_clear`, `melee_clear_block`, `last_stand_clear`) |
| Movement / charge | 5 | build all 5 | existing, plus NEW aura charge without wavering (row 40) |
| Stealth | 7 | keep shut | |
| Mutual exclusivity | 5 | park with the stances | |
| Bombardment | 2 | build 1, close 1 | existing |
| Your revisit list | 9 | build all 9 | existing, plus the melee-cluster pick (row 57) |

If you take every recommendation: **51 abilities built, 1 closed, 12 left shut or parked**, with 3 small new pieces
(the melee-cluster ground pick, the area-drain clearance, the aura charge without its wavering arm).
