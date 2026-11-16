# review_g1b: melee_unwavering, rows 151-299 (149 abilities)

Reviewer scope: rows 151-299 of the `melee_unwavering` table in `docs/WH3_ability_database_master.md` (Miasma of Despair to Whirl of Weeping Blades). Evaluator read: `FOURTH.evaluate_in_melee_self(unit, routing)` (source line ~8455): fires when `unit:is_in_melee()` is true, the unit is not routing, and `FOURTH.wavering(unit)` is not true (an unreadable morale read fails open to plain in-melee). Cast on the unit itself. None of the 149 entries carries `target_class`, `aura_real`, `nosafe` or other extra gating fields (checked in the entry blocks); `ursuns_roar` carries `range_real = 150` only.

Marker note: four Ursun's Roar rows (284-287) share marker `ursuns_roar` (4 keys, one entry); two Waaagh! rows (291, 292) share marker `waaagh_in_combat`. Row 193 Ruinshelter is a `mimic_ruinshelter` key; row 225 Soulblight is marker `soulblight_handmaidens`.

## A. Families

### melee_unwavering
Covered by review_g1a. One observation for g1a to weigh: the shipped sentence "fires when this unit is in melee" omits the not-wavering gate, which the code does check (and the wavering read fails open when unreadable).

## B. Abilities

Scale reminder: 5 = matches payoff moment; 4 = good; 3 = clearly better feasible trigger exists; 2 = poor moment; 1 = wrong.
Short names used for better triggers: `charge_or_melee` (existing family), `melee_or_under_fire` (hypothetical: in melee OR `is_under_missile_attack()`, proven on own units in QA battle 1 on 2026-11-09), `melee_health75` (existing: in melee and health condition).
Restriction column: "none" means no unhandled flag found in the database row or the restriction audit.

| # | Marker | Ability | Effect (short) | Score | Why | Better trigger (if <= 3) | Restriction issue |
|---|---|---|---|---|---|---|---|
| 151 | miasma_of_despair | Miasma of Despair | enemy aura: speed -25%, Ldr -8, fatigue (35 m) | 4 | Enemy speed cut pays off when engaged; rule 10 allows melee or charge | optional `charge_or_melee` | none |
| 152 | mighty_oath_stone | Mighty Oath Stone | self+allies MD +24, expert charge defence (55 m) | 4 | Defence stat in melee; charge defence part pays off BEFORE contact | optional `charge_or_melee` is wrong direction (needs "enemy charging us", no read) | none |
| 153 | mighty_roar | Mighty Roar | enemy aura: speed -25%, Ldr -8 (35 m) | 4 | As Miasma | optional `charge_or_melee` | none |
| 154 | mimic_feint_and_riposte | Mirror (Feint & Riposte) | MA +24, MD +24, phys res +20 | 5 | Pure melee stats | | none |
| 155 | mimic_grand_hammer_of_faith | Mirror (Grand Hammer of Faith) | MA +24, damage res +20 | 5 | Melee attack plus resistance | | none |
| 156 | mimic_grom_waaagh | Mirror (Grom's Big Waaagh!) | MA +40, AP/base dmg +25%, immune psychology, heal | 5 | Melee-only offence, pays off in melee | | none |
| 157 | mimic_waaagh | Mirror (Waaagh!) | MA +24, dmg +25%, immune psychology | 5 | Melee-only offence | | none |
| 158 | monstrous_strength | Monstrous Strength | bonus vs infantry +16, dmg +25% | 5 | Melee-only damage | | none |
| 159 | moonshine | Moonshine | dmg +25%, flame res -40, unbreakable, heal | 4 | Melee offence plus unbreakable; flame res -40 is a drawback vs fire shooters, small | | none |
| 160 | mortal_blow | Mortal Blow | dmg +35% | 5 | Melee-only damage | | none |
| 161 | mortal_blow_upgraded | Mortal Blow (Upgraded) | dmg +50%, sundered armour contact | 5 | Melee-only | | none |
| 162 | mumbo_jumbo_chant | Mumbo-Jumbo Chant | allies MA +24, dmg +25%, Ldr +16; caster CANNOT MOVE (55 m) | 4 | Buffs allies in 55 m; caster is rooted, so firing only once already engaged is right | | none |
| 163 | strike_of_nagash | Necrostrike | base dmg +90%, terror | 5 | Melee damage | | none |
| 164 | null_stone | Null Stone | silence and removes magical attacks (allies in range), 3 uses, 35 s | 2 | Pays off when ENEMY casters or magic attackers are active, not when "in melee"; wastes 1 of 3 uses on a plain melee | No read of enemy casting; `melee_unwavering` plus (a) leave as is but note low value, or (b) skip; best feasible: fire when an enemy spellcaster-class (commander proxy) is visible in range, as `enemy_commander_value` does | none |
| 165 | nurgles_favoured_son | Nurgle's Favoured Son | MD +24, damage res +20 | 4 | Melee defence in melee; damage resistance also helps vs missiles | `melee_or_under_fire` (small gain) | none |
| 166 | okkams_mindrazor | Okkam's Mindrazor | dmg +50%, magical attacks | 5 | Melee damage | | none |
| 167 | opal_amulet | Opal Amulet | damage res +20 | 4 | Resistance applies to all damage; melee is the main case | `melee_or_under_fire` | none |
| 168 | oracle_of_eternity | Oracle of Eternity | damage res +44 | 4 | As Opal Amulet, stronger | `melee_or_under_fire` | none |
| 169 | phas_protection | Pha's Protection | self+allies armour +30, MD +24 (cast reach 200 m) | 4 | Armour also helps vs missiles; melee fine | `melee_or_under_fire` | none (self=yes, friends=yes) |
| 170 | plaguefathers_oration | Plaguefather's Oration | MD +24, Ldr +16 aura (35 m) | 5 | Melee defence plus morale in melee | | none |
| 171 | plaque_of_dominion | Plaque of Dominion | enemy Ldr -8 aura (35 m) | 4 | Morale shock pays off with enemies close; melee good | | none |
| 172 | potion_of_foolhardiness | Potion of Foolhardiness | CHARGE BONUS +40%, unbreakable | 2 | Charge bonus is spent in the first seconds of contact; "in melee" fires after the charge impact | `charge_or_melee` (fires on the charge, still catches melee for unbreakable) | none |
| 173 | potion_of_strength | Potion of Strength | dmg +50% | 5 | Melee damage | | none |
| 174 | power_familiar | Power Familiar | spell mastery +20% (22 s, 1 use) | 1 | Spell effect, no connection to melee; wasted when the lord is just fighting | No fitting read; best feasible: fire when a spell is likely (unit is a caster and winds pool is non-empty), else drop or `when_ready` | none |
| 175 | predatory_instincts | Predatory Instincts | self+allies MA +24, dmg +25%, fear (cast reach 100 m) | 4 | Melee offence | | Target flag `unit_is_not_tiger_warrior` unhandled (audit): the caster casts on itself; fails if the caster is a Tiger Warrior. Check `unit_is_not_tiger_warrior` key list on the caster |
| 176 | primal_roar | Primal Roar | self+allies MA +40, phys res +20, RAMPAGE (35 m) | 3 | Rampage removes control of the units; melee start is right, but arming it needs care | none better; note Rampage side effect (no read) | none |
| 177 | primeval_roar | Primeval Roar | self+allies MA +24 (35 m) | 5 | Melee attack | | none |
| 178 | puncture | Puncture | MA +24, sundered armour contact | 5 | Melee | | none |
| 179 | quickblood | Quickblood | MA +24, executioner | 5 | Melee | | none |
| 180 | quicksilver_strike | Quicksilver Strike | MA +40, dmg +50% | 5 | Melee | | none |
| 181 | rage_embodied | Rage Embodied | enemy RAMPAGE (35 m, 15 s) | 3 | Enemy rampage makes them attack uncontrollably (also each other); value depends on enemies being ours-vs-theirs mixed, not "in melee" | no better read; leave, but user flagged Rampage items earlier | invalid-target `climbing`, `on_a_platform` are siege flags (not modelled by design) |
| 182 | rage_incarnate | Rage Incarnate | enemy RAMPAGE (55 m) | 3 | As Rage Embodied | as above | none |
| 183 | rapier_of_ecstasy | Rapier of Ecstasy | MA +24, euphoria contact | 5 | Melee | | none |
| 184 | red_fury | Red Fury | self+allies CHARGE BONUS +20%, AP dmg +25%, fatigue (cast reach 100 m) | 3 | Charge bonus part is wasted once in melee | `charge_or_melee` | none |
| 185 | red_ruin | Red Ruin | dmg +75%, MD -24 | 4 | Huge damage; the MD drawback is the cost in melee, acceptable | | none |
| 186 | refuse_to_die | Refuse to Die | cannot die for 20 s (60 s recharge) | 3 | Cannot Die pays off only when the unit is about to die; firing on first melee contact burns 20 s early | `melee_health75`-style low-health arm (melee plus health below a threshold) | none |
| 187 | revenge_incarnate | Revenge Incarnate | MA +40, dmg +60% | 5 | Melee | | none |
| 188 | rival_hide_talisman | Rival Hide Talisman | enemy aura MA -40 (35 m) | 5 | Enemy melee attack cut matters in melee | | none |
| 189 | item_passive_rock_eye | Rock Eye | forest/scrub spotting +10% (60 s) | 1 | Spotting stat, irrelevant in melee | `when_ready` or drop (no read of forest/scrub stealth) | none |
| 190 | rock_of_itza | Rok of Itza | phys res +40, fatigue | 4 | Resistance in melee | `melee_or_under_fire` if phys res covers missiles | none |
| 191 | rot_or_die | Rot or Die! | melee damage reflection +20, Ldr +16, spreading | 5 | Reflection only hits attackers in melee | | none |
| 192 | rot_pocked_axe | Rot-pocked Axe | MA +24, dmg +25%, weakened contact (aura 55 m) | 5 | Melee | | none |
| 193 | (mimic) ruinshelter | Ruinshelter | speed -60%, armour +45, MA +8, MD +10 | 4 | Defensive posture in melee; the -60% speed means a unit that is NOT mid-march is right | | none |
| 194 | rune_axe_of_gotrek | Rune Axe of Gotrek | AP dmg +50%, dampen contact | 5 | Melee | | none |
| 195 | rune_axe_of_grombrindal | Rune Axe of Grombrindal | AP dmg +50%, discouraged contact | 5 | Melee | | none |
| 196 | rune_of_breaking | Rune of Breaking | self+allies dmg +25%, sundered armour (cast reach 100 m) | 5 | Melee | | none |
| 197 | rune_of_doom | Rune of Doom | self+allies MA +24, fear (55 m) | 5 | Melee | | none |
| 198 | rune_of_negation | Rune of Negation | self+allies damage res +40 (cast reach 100 m) | 4 | Resistance, helps vs missiles too | `melee_or_under_fire` | none |
| 199 | rune_of_oath_and_steel | Rune of Oath & Steel | armour +30 aura (35 m), ground-target, self=no friends=yes | 3 | Armour also helps vs missiles; also a ground-cast ability: cast "on itself" with self=no may be refused by the game | field-check cast form; trigger `melee_or_under_fire` | targets ground; self=no. Verify the cast-on-self route works (QA) |
| 200 | rune_of_thungni | Rune of Thungni | self+allies dmg +25%, sundered armour (cast reach 100 m) | 5 | Melee | | none |
| 201 | runefang | Runefang | splash +50%, dmg +50% | 5 | Melee | | none |
| 202 | sacred_spawning_of_xhotl | Sacred Spawning of Xhotl | phys res +20, fatigue | 4 | Resistance | `melee_or_under_fire` | none |
| 203 | sands_of_sickness | Sands of Sickness | enemy speed -25%, MD -24; own reflection +20, fatigue | 4 | Enemy debuff plus reflection; melee good | | none |
| 204 | scales_of_the_celestial_court | Scales of the Celestial Court | phys res +75, strider | 4 | Big resistance; protects from missiles too | `melee_or_under_fire` | none |
| 205 | sceptre_of_stability | Sceptre of Stability | self+allies SPELL resistance +40 (cast reach 100 m) | 2 | Spell resistance pays off vs enemy spells, not melee | Fire when enemy spellcasters present (`enemy_commander_value`-style proxy) or when caster/ally takes magic damage (no read) | none |
| 206 | sceptre_of_titans | Sceptre of Titans | bonus vs large +24, AP +75% | 4 | Melee-only; best only if the opponent is large (no large check) | add "enemy engaged is large" (generated large set exists) | none |
| 207 | scourge | Scourge | splash +50%, bonus vs infantry +32, dmg +25% | 5 | Melee | | none |
| 208 | scroll_of_shielding | Scroll of Shielding | self+allies damage res +20 | 4 | Resistance | `melee_or_under_fire` | none |
| 209 | scrying_stone | Scrying Stone | Ldr +8, damage res +20 | 4 | Fine in melee | | none |
| 210 | seduction_of_the_serpent | Seduction of the Serpent | MD +24, Ldr +16, discouraged contact | 5 | Melee defence | | none |
| 211 | seductive_glory | Seductive Glory | enemy MD -24, RAMPAGE (35 m) | 3 | Enemy rampage; user ruling 2026-10-28 keeps the ability (starts unarmed); trigger per ruling | user ruling, do not argue | none |
| 212 | shadow_shroud | Shadow Shroud | damage res +60 | 4 | Strong resistance | `melee_or_under_fire` | none |
| 213 | shield_of_aeons | Shield of Aeons | self+allies armour +60, expert charge defence, charge reflection (55 m) | 3 | Charge defence and charge reflection pay off BEFORE the enemy charge hits; "in melee" is after | No "enemy about to charge" read; `charge_or_melee` charges OUR charge, not theirs | none |
| 214 | shield_of_faith | Shield of Faith | self+allies damage res +20, good vs AP (55 m) | 4 | Resistance | `melee_or_under_fire` | none |
| 215 | shield_of_faith_upgraded | Shield of Faith (Upgraded) | as above, extended duration | 4 | As above | `melee_or_under_fire` | none |
| 216 | shield_of_the_old_ones | Shield of the Old Ones | self+allies Ldr +8, damage res +20 (cast reach 150 m, ground) | 4 | Fine in melee | `melee_or_under_fire` | ground-targeted (self=yes) |
| 217 | dispatch_the_swarm_protect | Shielding Swarm | self+allies MD +24, MISSILE BLOCK +36 | 3 | Missile block is wasted in melee; pays off under fire | `melee_or_under_fire` | self=no friends=yes: verify the cast-on-self route |
| 218 | dispatch_the_swarm_protect_upgraded | Shielding Swarm Upgraded | MD +36, missile block +48, 360 block | 3 | As above | `melee_or_under_fire` | as above |
| 219 | silver_dagger | Silver Dagger | dmg +25%, magical attacks | 5 | Melee | | none |
| 220 | skavenbrew | Skavenbrew | self+allies armour -30, MA +40, dmg +30%, immune psychology (cast reach 100 m) | 4 | Melee offence; armour -30 hurts vs missiles | | none |
| 221 | skull_wand_of_kaloth | Skull Wand of Kaloth | MA +24, dmg +60%, discouraged contact | 5 | Melee | | none |
| 222 | slayer_for_chaos | Slayer for Chaos | MA +12, CANNOT DIE, terror, unbreakable | 3 | Cannot Die burns on first contact | melee plus low-health arm (as `melee_health75`) | none |
| 223 | sliverslash | Sliverslash | AP/base dmg +50%, sundered armour, magical | 5 | Melee | | none |
| 224 | smash_em_faster | Smash 'Em Faster | self+allies MA +24, Ldr +16 (35 m) | 5 | Melee | | none |
| 225 | soulblight_handmaidens | Soulblight | contact effect soulblight | 5 | Contact effect applies on hits in melee | | none |
| 226 | spite_of_da_bad_moon | Spite of Da Bad Moon | self+allies bonus vs large +16, dmg +25% (cast reach 150 m, ground) | 4 | Melee-only; best vs large enemies | add large check | self=no friends=yes: verify the cast-on-self route |
| 227 | spurting_bile_blood | Spurting Bile-Blood | bile spurts on wound (details not in game tables) | 4 | Passive-like reaction to being hit in melee | | none |
| 228 | staff_of_damnation | Staff of Damnation | self+allies MA +40 (cast reach 200 m, 35 m) | 5 | Melee | | none |
| 229 | stand_or_die | Stand or Die! | MD +24, Ldr +16 (35 m) | 5 | Melee defence | | none |
| 230 | starcrusher | Starcrusher | splash +50%, dmg +50% | 5 | Melee | | none |
| 231 | steppe_hunters_horn | Steppe Hunter's Horn | bonus vs large +100%, charge defence vs large (35 m) | 3 | Large-only, and charge-defence half is before contact; fires vs any melee | add "engaged enemy is large"; `charge_or_melee` is wrong direction | none |
| 232 | stinky_giant_club | Stinky Giant Club | MA +24, dmg +60% | 5 | Melee | | none |
| 233 | supreme_shield_of_the_old_ones | Supreme Shield of the Old Ones | self+allies damage res +40 (cast reach 150 m, ground) | 4 | Resistance | `melee_or_under_fire` | ground-targeted (self=yes) |
| 234 | sword_of_anti_heroes | Sword of Anti-Heroes | dmg +50% | 4 | Melee; real payoff only vs heroes/lords (name implies bonus vs characters; table shows no flag) | add "engaged enemy is a Lord/Hero" if data confirms | none |
| 235 | sword_of_torgald | Sword of Torgald | dmg +50%, phase inevitable end contact, magical | 5 | Melee | | none |
| 236 | talisman_of_loec | Talisman of Loec | MA +24, dmg +30% | 5 | Melee | | none |
| 237 | temptator | Temptator | melee reflection +25, damage res +20 | 5 | Reflection only in melee | | none |
| 238 | tenebrous_forge_hammer | Tenebrous Forge-Hammer | self+allies dmg +20% (35 m) | 5 | Melee | | none |
| 239 | the_armour_of_morkar | The Armour of Morkar | self+allies MD +24, charge reflection (35 m) | 3 | Charge reflection pays off before enemy contact | no "enemy charging" read | none |
| 240 | banespear | The Bane Spear | damage 10/hit up to 25 entities to enemies in 35 m, strong vs 25+ entity units | 4 | Damaging aura; melee contact guarantees enemies close; does it harm our troops? not flagged (enemies only) | | none |
| 241 | black_axe_of_krell | The Black Axe of Krell | MA +24, dmg +30%, disembowel contact | 5 | Melee | | none |
| 242 | the_black_cleaver | The Black Cleaver | self+allies MA +24, dmg +25%, magical (55 m) | 5 | Melee | | none |
| 243 | blessed_blade_of_ptra | The Blessed Blade of Ptra | blinded contact, ignition 10, magical | 5 | Contact effects | | none |
| 244 | the_blood_price | The Blood Price | dmg +60%, damage res +20, 60 damage to self | 3 | Self-damage cost; on first contact is early if fight is short; fine for lord with HP | consider melee plus health above a safe threshold | none |
| 245 | the_carstein_ring | The Carstein Ring | damage res +60 | 4 | Strong resistance | `melee_or_under_fire` | none |
| 246 | the_crimson_blade | The Crimson Blade | disembowel contact, magical | 5 | Contact effects | | none |
| 247 | the_daemons_curse | The Daemon's Curse | enemy MD -24, Ldr -10 (35 m); small self-damage | 4 | Debuff aura; small self-cost | | none |
| 248 | sword_dance | The Dancing Blade | enemy MA -24 (15 m); self MD +24, phys res +40 | 5 | Close-range, melee only | | none |
| 249 | dragons_fang | The Dragon's Fang | MA +40, dmg +50%, executioner | 5 | Melee | | none |
| 250 | drakwald_runefang | The Drakwald Runefang | phys res +40, fatigue | 4 | Resistance | `melee_or_under_fire` | none |
| 251 | the_eternal_blade | The Eternal Blade | self+allies MA +40, dmg +50% | 5 | Melee | | none |
| 252 | the_father_of_blades | The Father of Blades | enemy MA -24 (20 m); self AP +25% | 5 | Melee | | none |
| 253 | the_graven_sceptre | The Graven Sceptre | MA +24, dmg +25%, magical | 5 | Melee | | none |
| 254 | undeath_sulekhim_hand_of_dust | The Hand of Dust | self+allies AP dmg +50%, magical (cast reach 200 m) | 5 | Melee | | none |
| 255 | hochland_runefang | The Hochland Runefang | enemy armour -60, MD -24 (35 m) | 5 | Melee debuff | | none |
| 256 | the_liber_mortis | The Liber Mortis | self+allies Ldr +8, phys res +40 (ground, 35 m) | 4 | Resistance | `melee_or_under_fire` | ground-targeted (self=yes) |
| 257 | the_mace_of_helsturm | The Mace of Helsturm | AP dmg +50%, ignition 10 | 5 | Melee | | none |
| 258 | nordland_runefang | The Nordland Runefang | 5 dmg/hit up to 25 entities, strong vs 25+ (35 m) | 4 | Damaging aura; check friendly fire not flagged | | none |
| 259 | ostermark_runefang | The Ostermark Runefang | bonus vs large +32, charge defence vs large (35 m) | 3 | Large only; fires vs any melee | add engaged-enemy-is-large check | none |
| 260 | ostland_runefang | The Ostland Runefang | dmg +50% | 5 | Melee | | none |
| 261 | the_phoenix_blade | The Phoenix Blade | bonus vs large +16, dmg +50%, flammable contact | 5 | Melee | | none |
| 262 | the_reikland_runefang | The Reikland Runefang | self+allies MA +24, Ldr +8 (35 m) | 5 | Melee | | none |
| 263 | the_rock_of_inevitability | The Rock of Inevitability | enemy charge speed -25%, speed -25%, MD -26 (35 m) | 3 | Charge-speed cut pays off before contact; rule 10 sends enemy speed reductions to melee or charge | `charge_or_melee` | none |
| 264 | the_rotaxes | The Rotaxes | MA +24, AP dmg +50%, executioner | 5 | Melee | | none |
| 265 | the_slayer_sword | The Slayer Sword | MA +24, dmg +50%, weakened contact | 5 | Melee | | none |
| 266 | the_slayer_of_kings | The Slayer of Kings | splash +50%, dmg +75% | 5 | Melee | | none |
| 267 | the_sword_of_couronne | The Sword of Couronne | enemy armour -30, MD -24 (35 m) | 5 | Melee debuff | | none |
| 268 | sword_of_lyonesse | The Sword of Lyonesse | MA +40, dmg +50% | 5 | Melee | | none |
| 269 | talabecland_runefang | The Talabecland Runefang | MA +40, sundered armour | 5 | Melee | | none |
| 270 | the_tenderiser | The Tenderiser | self+allies dmg +50% | 5 | Melee | | none |
| 271 | the_wintertooth_crown | The Wintertooth Crown | self+allies MD +24, unbreakable (55 m) | 5 | Melee | | none |
| 272 | wissenland_runefang | The Wissenland Runefang | enemy speed -45%, fatigue (35 m) | 3 | Rule 10: enemy speed reductions fire on the charge or in melee | `charge_or_melee` (optional gain: catches the charge) | none |
| 273 | thorns_aura | Thorn's Aura | self+allies melee reflection +14 (35 m) | 5 | Reflection only in melee | | none |
| 274 | toad_rage | Toad Rage | AP dmg +50%, dmg +50%, RAMPAGE | 3 | Rampage on self: player loses control; keep melee start | none better | none |
| 275 | strike_of_tombs | Tombstrike | MA +24, dmg +30%, terror | 5 | Melee | | none |
| 276 | tors_battle_hymn | Tor's Battle Hymn | self+allies MA +40 (35 m) | 5 | Melee | | none |
| 277 | tormentor_sword | Tormentor Sword | enemy MA -24, CANNOT MOVE (35 m) | 4 | Pins enemies; best when they are engaged; good | | none |
| 278 | tyrants_talon | Tyrant's Talon | MA +24, dmg +25%, brutal wounds contact | 5 | Melee | | none |
| 279 | ultimate_verdict | Ultimate Verdict | enemy MD -24 (35 m); self terror, executioner | 5 | Melee | | none |
| 280 | undeath_resurgent | Undeath Resurgent | self+allies MD +24, Ldr +16 (35 m) | 5 | Melee | | none |
| 281 | unyielding_defender | Unyielding Defence | MD +24, unbreakable | 5 | Melee | | none |
| 282 | ursuns_claw | Ursun's Claw | AP dmg +50%, frozen contact | 5 | Melee | | none |
| 283 | ursuns_roar_2 | Ursun's Mighty Roar | MA +40, Ldr +16 (greater melee effect) | 5 | Melee | | none |
| 284 | ursuns_roar | Ursun's Roar (`wh3_main_character_abilities_ursuns_roar`) | CHARGE BONUS +36%, Ldr +8 (35 m) | 2 | Pure charge buff; in melee is too late | `charge_or_melee` (marker shared with 3 other keys that are plain melee buffs: needs its own entry to move) | none |
| 285 | ursuns_roar | Ursun's Roar (`..pro_character_abilities_ursuns_roar`) | MA +40 | 5 | Melee | | none |
| 286 | ursuns_roar | Ursun's Roar (`..ursuns_roar_1`) | MA +20, Ldr +16 | 5 | Melee | | none |
| 287 | ursuns_roar | Ursun's Roar (`..ursuns_roar_3`) | MA +60, Ldr +16 | 5 | Melee | | none |
| 288 | van_horstmanns_speculum | Van Horstmann's Speculum | enemy MA -24, dmg -30%, MD -24 (35 m) | 5 | Melee debuff | | none |
| 289 | vine_dragon_scale | Vine Dragon Scale | enemy MD -24, CANNOT MOVE (35 m) | 4 | Pins enemies, fine in melee | | none |
| 290 | violent_wind | Violent Wind | self-centred blast, 4 s, "rebirth" stance flag; tracker says cannot hurt our units | 5 | Safe blast, in melee right (user-approved Bloodstorm look-alike) | | none |
| 291 | waaagh_in_combat | Waaagh! (`wh3_dlc26_unit_abilities_waaagh_in_combat`) | MA +24, dmg +25%, immune psychology | 5 | Melee ("in combat") | | none |
| 292 | waaagh_in_combat | Waaagh! (`wh_main_character_abilities_waaagh`) | SPEED +25%, CHARGE BONUS +20%, MA +20 (unlimited range) | 3 | Speed and charge half wasted once in melee | `charge_or_melee` (needs its own entry, shares marker with 291) | none |
| 293 | wand_of_jet | Wand of Jet | winds recharge -20%, own ability recharge 15 s (57 s) | 1 | Spell-economy item; no melee link | `when_ready` or fire when a winds-spending spell is likely (no read) | none |
| 294 | warp_frenzy | Warp Frenzy | MA +24, dmg +25% | 5 | Melee | | none |
| 295 | warpstone_addiction | Warpstone Addiction | damage res +33 | 4 | Resistance | `melee_or_under_fire` | none |
| 296 | warrior_familiar | Warrior Familiar | MA +24, MD +24 | 5 | Melee | | none |
| 297 | warriors_crest | Warrior's Crest | MA +40, MD +24 | 5 | Melee | | none |
| 298 | watched_by_the_watcher | Watched by the Watcher | enemies REVEALED (60 s, 3 uses) | 2 | Reveal pays off vs hidden/forest-stealth enemies, not in melee where the foe is visible | Fire when a living enemy reads not visible (`is_visible_to_alliance` = false) near the army; else `when_ready` | none |
| 299 | whirl_of_weeping_blades | Whirl of Weeping Blades | stationary huge-area attack, cannot move; safe blast flag | 5 | Same family as Violent Wind, user-approved melee start | | invalid-usage `climbing`, `manning_equipment`, `on_a_platform` are siege flags (not modelled by design) |

### Score distribution (149 rows)
5: 83, 4: 39, 3: 19, 2: 5, 1: 3 (counted from the table).

## C. Game-mechanics questions

1. Does Damage Resistance (and Physical Resistance) apply to missile damage in WH3? If yes, 20-plus abilities (Opal Amulet, Oracle, Shadow Shroud, Carstein Ring, Rune of Negation, Scales of the Celestial Court, etc.) are better on "melee OR under missile fire".
2. Charge Reflection and Expert Charge Defence (Shield of Aeons, Armour of Morkar, Mighty Oath Stone): are they only active while the enemy's charge impact is resolving? If so, a pre-contact trigger is needed and none feasible exists (no read for an incoming enemy charge).
3. Rampage on ENEMIES (Rage Embodied, Rage Incarnate, Seductive Glory): does it hurt the enemy army (they attack their own side) or just make them fight wildly? The database tags it "positive", which may be a flag convention, not a real benefit.
4. Cannot Die effects (Refuse to Die, Slayer for Chaos): how long is the real window against the 60 s recharge? Is a health-conditioned trigger acceptable to the user, given that Vigour/health triggers were previously ruled out for restorers only?
5. Ground-target abilities cast on self (Rune of Oath & Steel, Spite of Da Bad Moon, Shielding Swarm with self=no, friends=yes): does `perform_special_ability` on the unit itself succeed, or does the engine need self=yes? Field QA battle confirmation wanted.
6. Violent Wind and Whirl of Weeping Blades carry "Stance: rebirth": does the CLAUDE.md "stances are never automated" rule apply (these are blast attacks, not a mutually-exclusive stance chooser), and are they truly friendly-fire safe as the tracker says?
7. Predatory Instincts target flag `unit_is_not_tiger_warrior`: does it block the caster casting on itself when the caster is a Tiger Warrior?
8. Bonus-vs-large abilities (Sceptre of Titans, Ostermark Runefang, Steppe Hunter's Horn, Spite of Da Bad Moon): is a large-enemy check worth adding? The generated large set exists; no read of "who am I fighting" is documented beyond the melee table.
9. Enemy speed-reduction auras (Wissenland, Miasma, Mighty Roar, Rock of Inevitability): confirm the aura keeps working on enemies who are already engaged (speed -45% on engaged enemies may matter only on disengage).
10. Does Wand of Jet's "own ability recharge 15 s" shorten recharge of the bearer's other abilities only while active? If so the best moment is when another ability of the same unit is on cooldown.

## Summary

1. 149 rows reviewed; 83 pure melee stat, melee damage, contact-effect or melee-debuff abilities score 5, so "in melee" is the right moment for roughly half of this tail.
2. Charge-benefit abilities ride the wrong trigger: Potion of Foolhardiness, Red Fury, Ursun's Roar (charge_bonus key), Waaagh! (wh_main), The Rock of Inevitability and Wissenland Runefang belong on `charge_or_melee` (rule 10); two of them share a marker with plain-melee keys and need their own entry.
3. Score 1-2 misfits with no melee link: Power Familiar, Wand of Jet, Rock Eye (1); Null Stone, Sceptre of Stability (spell resistance), Watched by the Watcher (2): melee-first-contact wastes their uses; Cannot Die items (Refuse to Die, Slayer for Chaos) want a low-health arm.
4. Defence abilities with Damage/Physical Resistance or missile block (about 20 rows) would gain from a "melee or under missile fire" family; Shielding Swarm (missile block) and the pre-charge defences (Shield of Aeons, Armour of Morkar) are the weakest fits.
5. Restriction gaps: only Predatory Instincts (`unit_is_not_tiger_warrior` target flag, cast on self) is a real unhandled flag in this slice; ground-target/self=no abilities (Rune of Oath & Steel, Spite of Da Bad Moon, Shielding Swarm) need a field check of the cast-on-self route; siege flags are not modelled by design.
