# WARHAMMER III — Remaining-abilities triage (the 347 flagged items)

**Date:** 2026-10-09  ·  **Source:** `WH3_auto_classification_report.md` Appendix C (the 347 FLAG rows)  ·  **Tracker:** `WH3_ability_tracker.md` (§3a `proposed` 129 + §3b `proposed (FF)` 218).  **Nothing is built or installed here — this is the triage that shrinks the question list.**

Goal: turn the 347 flagged rows into the **smallest honest question list**. Rows that the engine can
never support are auto-excluded (group A); rows with the same effect family become **one decision each**
(group B); only genuinely case-by-case abilities are asked one by one (group C).

## Count table

| Group | Rows | What it means | Decisions still needed |
|---|---:|---|---:|
| **A — IMPOSSIBLE** (engine limit) | 97 | Auto-excluded; recorded with the specific reason. Never asked. | 0 |
| **B — CATEGORY-DECIDABLE** | 238 | Grouped into 6 effect families; **one decision per family** settles every row in it. | 6 |
| **C — INDIVIDUAL** | 12 | Genuinely case-by-case; asked one at a time. | 12 |
| **Total flagged** | 347 | | **18** |

**Net effect:** 347 flagged items → **6 family decisions + 12 individual questions = 18 decisions total** (down from 347). Counts check: 97 + 238 + 12 = 347.

### Engine limits that define group A (proven, not assumed)

- **No read of enemy units** — an enemy unit has no card and no id, so any ability that must **target, react to,
  or measure an enemy** cannot be automated → *no enemy-unit read*.
- **No per-unit firing/shooting read** — nothing exposes whether a unit is shooting.
- **No per-unit cooldown read** — the engine cannot inspect a unit's remaining cooldowns.
- Two further settled reasons: abilities the **user already rejected for tactical escape/stealth** stay rejected;
  and the engine **cannot swap unit forms**, so transform/shapechange effects have no implementation.

> **Reading of the limits:** "must target an *enemy*" is taken strictly as an **enemy *unit*** reference (needs the
> unit's id). Abilities that only need a **ground point** can still be cast on the mod's existing ground-cast path,
> so they are **not** impossible — their friendly-fire/placement risk is a *decision* (group B), not an engine wall.

---

## 1. IMPOSSIBLE — auto-excluded (97 rows)

These are marked `excluded (impossible: <reason>)` in the tracker. No question is asked about them.

### 1a. No enemy-unit read — must target an enemy unit (76 rows)

| Ability | Key | Flag reason it came from |
|---|---|---|
| 'Effagee' of da Git | `wh_dlc06_character_abilities_effagee_of_da_git` | ambiguous / mixed net effect (needs the user) |
| Amber Bow | `wh2_dlc13_weapon_abilities_amber_bow` | ambiguous / mixed net effect (needs the user) |
| Arrow of Aqshy | `wh2_dlc13_lord_abilities_fire_arrow` | ambiguous / mixed net effect (needs the user) |
| Blood Statuette of Spite | `wh2_main_item_abilities_blood_statuette_of_spite` | ambiguous / mixed net effect (needs the user) |
| Bolt of Change | `wh3_main_army_abilities_bolt_of_change` | friendly fire (FF-parked block) |
| Bolt of Spite | `wh2_main_army_abilities_bolt_of_spite` | friendly fire (FF-parked block) |
| Burning Wrath | `wh3_dlc23_spell_bound_burning_wrath` | ambiguous / mixed net effect (needs the user) |
| Chain Lightning | `wh3_dlc27_spell_heavens_chain_lightning_bound` | ambiguous / mixed net effect (needs the user) |
| Chain Lightning | `wh3_dlc27_spell_heavens_chain_lightning_bound_unit` | ambiguous / mixed net effect (needs the user) |
| Daemonic Possession | `wh3_main_lord_abilities_daemonic_possession` | ambiguous / mixed net effect (needs the user) |
| Damned Pistol | `wh3_main_weapon_abilities_godkiller_pistol` | ambiguous / mixed net effect (needs the user) |
| Darkened Mist | `wh3_dlc23_item_abilities_darkened_mist` | ambiguous / mixed net effect (needs the user) |
| Dart of Doom | `wh2_dlc16_item_abilities_dart_of_doom` | ambiguous / mixed net effect (needs the user) |
| Dead Eye | `wh3_dlc26_character_abilities_dead_eye` | ambiguous / mixed net effect (needs the user) |
| Death's Timekeeper | `wh3_dlc25_item_abilities_deaths_timekeeper` | mixed positive-and-negative effect |
| Dire Spirit Bear | `wh3_dlc24_lord_abilities_spirit_bear_upgrade` | ambiguous / mixed net effect (needs the user) |
| Dissolving Bone | `wh3_dlc27_qb_unit_abilities_dissolving_bone` | ambiguous / mixed net effect (needs the user) |
| Dweomer Leach Orb | `wh3_dlc23_item_abilities_dweomer_leach_orb` | mixed positive-and-negative effect |
| Eagle Quiver | `wh2_dlc16_item_abilities_eagle_quiver` | ambiguous / mixed net effect (needs the user) |
| Ethrac's Brazier | `wh3_dlc29_item_active_ethracs_brazier` | ambiguous / mixed net effect (needs the user) |
| Executioner | `wh2_dlc13_lord_abilities_executioner` | ambiguous / mixed net effect (needs the user) |
| Fireball | `wh_main_spell_bound_fireball` | ambiguous / mixed net effect (needs the user) |
| Fireball Upgraded | `wh3_dlc27_spell_bound_fireball_upgraded` | ambiguous / mixed net effect (needs the user) |
| Focused Shot | `wh2_dlc13_lord_abilities_kill_shot` | ambiguous / mixed net effect (needs the user) |
| Gaze of Nagash | `wh2_dlc15_spell_bound_gaze_of_nagash` | ambiguous / mixed net effect (needs the user) |
| Goggly Glare | `wh2_dlc15_character_abilities_goggly_glare` | ambiguous / mixed net effect (needs the user) |
| Hail of Doom Arrow | `wh_dlc05_item_abilities_hail_of_doom_arrow` | ambiguous / mixed net effect (needs the user) |
| Hand of Gods | `wh2_main_spell_bound_hand_of_gods` | ambiguous / mixed net effect (needs the user) |
| Khorne's Wrath | `wh3_dlc26_army_abilities_khornes_wrath` | friendly fire (FF-parked block) |
| Lesser Doombolt | `wh2_dlc10_spell_bound_lesser_doombolt` | friendly fire (FF-parked block) |
| Maelstrom of Change | `wh3_dlc24_unit_abilities_maelstrom_of_change` | ambiguous / mixed net effect (needs the user) |
| Mercurial Shot | `wh3_dlc25_character_abilities_mercurial_shot` | ambiguous / mixed net effect (needs the user) |
| No Escape | `wh3_main_character_abilities_no_escape` | stealth/escape/stalk effect |
| Otherworldly Pestilence | `wh3_dlc29_lord_abilities_otherworldly_pestilence` | ambiguous / mixed net effect (needs the user) |
| Preyton Horns | `wh3_dlc27_item_abilities_preyton_horns` | mixed positive-and-negative effect |
| Punch-Dagger | `wh3_dlc29_item_abilities_punch_dagger` | ambiguous / mixed net effect (needs the user) |
| Quiver of Aqshy | `wh2_dlc13_lord_abilities_arrows_of_aqshy` | ambiguous / mixed net effect (needs the user) |
| Rancid Visitations | `wh3_main_spell_bound_rancid_visitations` | ambiguous / mixed net effect (needs the user) |
| Rod of Torment | `wh3_dlc20_item_abilities_rod_of_torment` | friendly fire (FF-parked block) |
| Schalkain's Teeth | `wh3_dlc27_item_abilities_schalkains_teeth` | ambiguous / mixed net effect (needs the user) |
| Shadowblood | `wh3_dlc29_lord_abilities_shadowblood` | ambiguous / mixed net effect (needs the user) |
| Shem's Burning Gaze | `wh_main_spell_light_shems_burning_gaze_bound` | ambiguous / mixed net effect (needs the user) |
| Spear of Grungni | `wh3_dlc25_unit_abilities_spear_of_grungni` | ambiguous / mixed net effect (needs the user) |
| Spear of Kurnous | `wh_dlc05_weapon_abilities_spear_of_kurnous` | ambiguous / mixed net effect (needs the user) |
| Spirit Barrage | `wh3_dlc25_army_abilities_spirit_barrage` | friendly fire (FF-parked block) |
| Spirit Bear | `wh3_dlc24_lord_abilities_spirit_bear` | ambiguous / mixed net effect (needs the user) |
| Spirit Leech | `wh2_dlc09_spell_death_spirit_leech_bound` | ambiguous / mixed net effect (needs the user) |
| Spirit Leech | `wh3_dlc25_spell_bound_spirit_leech` | ambiguous / mixed net effect (needs the user) |
| Spirit Leech | `wh3_dlc25_spell_bound_spirit_leech_gunnery_school` | ambiguous / mixed net effect (needs the user) |
| Spirit Leech | `wh3_main_spell_bound_spirit_leech` | ambiguous / mixed net effect (needs the user) |
| Spirit Leech | `wh3_twa08_spell_bound_spirit_leech_great_unclean_one_ror` | ambiguous / mixed net effect (needs the user) |
| Staff of Masks | `wh3_dlc27_item_abilities_staff_of_the_masque` | mixed positive-and-negative effect |
| Sting of Snagla | `wh3_dlc26_character_abilities_sting_of_snagla` | ambiguous / mixed net effect (needs the user) |
| Storm of the Night | `wh2_dlc11_lord_abilities_storm_of_the_night` | friendly fire (FF-parked block) |
| Swamp Breath | `wh2_dlc15_hero_abilities_swamp_breath` | ambiguous / mixed net effect (needs the user) |
| Taal's Judgement | `wh3_dlc24_lord_abilities_taals_judgement` | ambiguous / mixed net effect (needs the user) |
| Tempest | `wh3_dlc27_army_high_magic_tempest` | friendly fire (FF-parked block) |
| Terrible Malice | `wh3_dlc27_qb_unit_abilities_terrible_malice` | ambiguous / mixed net effect (needs the user) |
| The Amber Trance | `wh2_dlc10_item_abilities_the_amber_trance` | mixed positive-and-negative effect |
| The Emperor's Executioner | `wh3_dlc24_lord_abilities_the_emperors_executioner` | ambiguous / mixed net effect (needs the user) |
| The Emperor's Executioner | `wh3_dlc24_lord_abilities_the_emperors_executioner_upgrade` | ambiguous / mixed net effect (needs the user) |
| The Fate of Bjuna | `wh3_dlc25_spell_bound_the_fate_of_bjuna` | ambiguous / mixed net effect (needs the user) |
| The Fate of Bjuna | `wh3_main_spell_bound_the_fate_of_bjuna` | ambiguous / mixed net effect (needs the user) |
| The Gaze of Dust | `wh3_dlc29_unit_abilities_the_gaze_of_dust` | ambiguous / mixed net effect (needs the user) |
| The Golden Blowpipe of P'Toohee | `wh2_dlc17_weapon_abilities_the_golden_blowpipe_of_ptoohee` | ambiguous / mixed net effect (needs the user) |
| The Liber Bubonicus | `wh2_main_item_abilities_the_liber_bubonicus` | ambiguous / mixed net effect (needs the user) |
| The Windblade | `wh3_dlc24_hero_abilities_windblade` | ambiguous / mixed net effect (needs the user) |
| Tome of Furion | `wh2_main_spell_bound_tome_of_furion` | friendly fire (FF-parked block) |
| Vindictive Glare | `wh_dlc06_spell_bound_vindictive_glare` | ambiguous / mixed net effect (needs the user) |
| Volley of Kurnous | `wh2_dlc16_unit_abilities_volley_of_kurnous` | ambiguous / mixed net effect (needs the user) |
| Wand of the Kharaidon | `wh2_main_spell_bound_wand_of_the_kharaidon` | friendly fire (FF-parked block) |
| Warp-Fireball | `wh2_dlc14_spell_bound_warpfireball` | ambiguous / mixed net effect (needs the user) |
| Wind Bow | `wh3_dlc24_item_abilities_wind_bow` | ambiguous / mixed net effect (needs the user) |
| Wolf's Howl | `wh3_main_weapon_abilities_the_traitors_sword` | friendly fire (FF-parked block) |
| Wraith Storm | `wh2_dlc11_army_abilities_wraith_storm` | friendly fire (FF-parked block) |
| Wraith Storm | `wh2_dlc11_lord_abilities_wraith_storm` | friendly fire (FF-parked block) |

### 1b. No transform/shapechange support (11 rows)

| Ability | Key | Flag reason it came from |
|---|---|---|
| Formless Horror | `wh3_dlc24_lord_abilities_formless_horror_changeling` | transform/shapechange |
| Formless Horror | `wh3_dlc24_lord_abilities_formless_horror_quest_battle_changeling_form` | transform/shapechange |
| Transformation of Kadon | `wh3_dlc27_spell_bound_transformation_of_kadon` | transform/shapechange |
| Transformation of the Dragon | `wh3_dlc24_lord_abilities_jade_dragon_human_form` | transform/shapechange |
| Transformation of the Dragon | `wh3_main_lord_abilities_iron_dragon_human_form` | transform/shapechange |
| Transformation of the Dragon | `wh3_main_lord_abilities_storm_dragon_human_form` | transform/shapechange |
| Tz'arkan | `wh2_dlc14_lord_abilities_tzarkan` | transform/shapechange |
| Tz'arkan | `wh2_dlc14_lord_abilities_tzarkan_mp` | transform/shapechange |
| Tz'arkan | `wh2_dlc14_lord_abilities_tzarkan_snikch` | transform/shapechange |
| Tz'arkan | `wh2_dlc14_lord_abilities_tzarkan_spite` | transform/shapechange |
| Tz'arkan | `wh2_dlc14_lord_abilities_tzarkan_spite_mp` | transform/shapechange |

### 1c. Already rejected by the user — tactical escape/stealth (10 rows)

*The stealth/escape flag held 11 rows; one of them (`No Escape`) targets an enemy unit and is counted in 1a.*

| Ability | Key | Flag reason it came from |
|---|---|---|
| Eagle Bow | `wh2_dlc16_weapon_abilities_eagle_bow` | stealth/escape/stalk effect |
| Envelop in Mist | `wh2_dlc15_army_abilities_envelop_in_mist` | stealth/escape/stalk effect |
| Envelop in Mist | `wh3_dlc27_character_abilities_envelop_in_mist_bound` | stealth/escape/stalk effect |
| Loec's Blessing | `wh2_dlc16_lord_abilities_loecs_blessing` | stealth/escape/stalk effect |
| Perfect Predator | `wh3_dlc27_unit_abilities_perfect_predator` | stealth/escape/stalk effect |
| Rival Hide Talisman | `wh2_main_item_abilities_rival_hide_talisman` | stealth/escape/stalk effect |
| Sand Veil | `wh2_dlc09_army_abilities_sand_veil` | stealth/escape/stalk effect |
| Skitterleap | `wh3_dlc29_spell_bound_skitterleap` | stealth/escape/stalk effect |
| Speed of Lykos | `wh2_dlc10_item_abilities_speed_of_lykos` | stealth/escape/stalk effect |
| Tricksy Traps | `wh_dlc06_lord_abilities_tricksy_traps` | stealth/escape/stalk effect |

---

## 2. CATEGORY-DECIDABLE — one decision per family (238 rows, 6 families)

All rows here come from the friendly-fire block (`proposed (FF)`, 205 rows) and the own-troop-damage flag
(26 rows), plus the 7 flanking/ambush rows. **Pick ACCEPT or EXCLUDE once per family** and the whole family is
settled. The recommendation below is the honest default; the "if you want them" line is the safe-ish form if you
decide the family is worth keeping.

### 2.0 Family summary

| # | Family | Rows | What the ability does | Recommendation |
|---|---|---:|---|---|
| 1 | **Vortex / wandering wind** | 70 | A damage vortex/wind is released and **travels across the battlefield** on its own path, damaging every unit (friend and foe) it touches. | **EXCLUDE.** The path is uncontrollable and there is no read to aim or time it — friendly fire is guaranteed, not avoidable. |
| 2 | **Bombardment / ground artillery** | 63 | A strike is called down on a **chosen ground point** (artillery / magical bombardment). | **EXCLUDE.** Placing it usefully needs an enemy read the engine does not have; blind placement lands on your own line. |
| 3 | **Placed / static area damage** | 42 | A **static area-damage field** centred on a point (often self), damaging everything inside while it lasts. | **EXCLUDE.** Same wall: no enemy read to place it, and a self-centred field hits friendlies. |
| 4 | **Breath / cone damage** | 30 | A **forward cone** of damage from the caster (breath weapons, cones). | **EXCLUDE.** The cone sweeps friendly units in the arc; no way to check the arc is clear. |
| 5 | **Own-troop-damage AoE** | 26 | The ability **deliberately damages your own units** as part of its effect (self-nova / sacrifice AoE). | **EXCLUDE.** Harming your own troops by design is not something to auto-fire. |
| 6 | **Flanking / ambush (flanking_opportunity)** | 7 | Hide / ambush / reposition effects (spotting and being spotted). | **EXCLUDE.** This is the stealth/escape family the user already rejected for other keys. |

| # | Family | If you want them (the safe-ish form) |
|---|---|---|
| 1 | Vortex / wandering wind | None that are safe — the only honest option is exclude. |
| 2 | Bombardment / ground artillery | Drop at the owner's own position while in melee (accepts friendly fire). |
| 3 | Placed / static area damage | Cast at own feet while in melee and not fleeing (accepts friendly fire). |
| 4 | Breath / cone damage | Cast on self while in melee and not fleeing (accepts friendly fire). |
| 5 | Own-troop-damage AoE | None — harmful to your own troops by design. |
| 6 | Flanking / ambush | Cast on self when the owner is flanked (needs an enemy-adjacent read; not currently possible). |

> Two rows inside these families target a **friend** and may actually be ally buffs mis-grouped by effect family
> (`Arcane Vassal`; `Inevitable Fate` ×4, all under §3b bombardment/vortex). If you want, promote those five to
> individual review — flag them in your answer and they move to group C.

### 2.1 Vortex / wandering wind — 70 rows

*What it does:* A damage vortex/wind is released and **travels across the battlefield** on its own path, damaging every unit (friend and foe) it touches.  ·  *Recommendation:* **EXCLUDE.** The path is uncontrollable and there is no read to aim or time it — friendly fire is guaranteed, not avoidable.

| Ability | Key | Target | Effect family (grouped2) | Notes |
|---|---|---|---|---|
| Arnzipal's Black Horror | `wh2_dlc10_item_bound_arnizipals_black_horror` | enemy ground | vortex_wind | cd 120s · 16s · enemy ground · ×1 uses · wind-up 5s · bound |
| Asur Fire I | `wh3_dlc27_army_abilities_asuryans_rage` | enemy ground | vortex_ap | cd 60s · 15s · enemy ground · ×3 uses · wind-up 3s · army |
| Asur Fire II | `wh3_dlc27_army_abilities_asuryans_fury` | enemy ground | vortex_ap | cd 90s · 20s · enemy ground · ×3 uses · wind-up 3s · army |
| Asur Fire III | `wh3_dlc27_army_abilities_asuryans_wrath` | enemy ground | vortex_ap | cd 120s · 25s · enemy ground · ×3 uses · wind-up 3s · army |
| Banishment | `wh3_main_spell_bound_banishment` | enemy ground | vortex_ap | cd 120s · 17s · enemy ground · ×1 uses · wind-up 5s · bound |
| Banishment | `wh_dlc04_spell_bound_banishment` | enemy ground | vortex_ap | cd 120s · 17s · enemy ground · ×2 uses · wind-up 5s · bound |
| Banishment | `wh_dlc04_spell_bound_banishment_innate` | enemy ground | vortex | cd 120s · 17s · enemy ground · ×2 uses · wind-up 5s · bound |
| Bound Fiery Convocation | `wh2_main_spell_bound_khaines_ring_of_fury` | enemy ground | vortex_wind_ap | cd 120s · 10s · enemy ground · ×2 uses · wind-up 5s · bound |
| Burning Alignment | `wh2_dlc12_unit_abilities_burning_alignment` | enemy ground | vortex_wind | cd 120s · 12s · enemy ground · ×2 uses · wind-up 5s |
| Diabolical Puppetry | `wh3_pro10_army_abilities_diabolical_puppetry` | enemy ground | vortex_ap | cd 90s · 25s · enemy ground · wind-up 3s · army |
| Diabolical Puppetry | `wh3_pro10_army_abilities_diabolical_puppetry_upgrade_1` | enemy ground | vortex_ap | cd 75s · 30s · enemy ground · wind-up 3s · army |
| Diabolical Puppetry | `wh3_pro10_army_abilities_diabolical_puppetry_upgrade_2` | enemy ground | vortex_ap | cd 60s · 35s · enemy ground · wind-up 3s · army |
| Diabolical Puppetry | `wh3_pro10_army_abilities_diabolical_puppetry_upgrade_3` | enemy ground | vortex_ap | cd 45s · 40s · enemy ground · wind-up 3s · army |
| Fiery Convocation | `wh2_dlc10_quest_abilities_magic_fiery_convocation` | enemy ground | vortex_wind_ap | cd 25s · 10s · enemy ground · wind-up 5s |
| Fiery Convocation | `wh2_dlc10_spell_bound_magic_fiery_convocation` | enemy ground | vortex_wind_ap | cd 120s · 10s · enemy ground · ×2 uses · wind-up 5s · bound |
| Flame Storm | `wh2_dlc10_quest_abilities_flame_storm` | enemy ground | vortex | cd 25s · 27s · enemy ground · wind-up 5s |
| Flame Storm | `wh3_dlc20_spell_bound_flame_storm` | enemy ground | vortex | cd 50s · 27s · enemy ground · ×1 uses · wind-up 5s · bound |
| Flame Storm | `wh3_main_spell_bound_flame_storm` | enemy ground | vortex | cd 120s · 27s · enemy ground · ×1 uses · wind-up 5s · bound |
| Gehenna's Golden Globe | `wh3_dlc20_cataclysm_bound_gehennas_golden_globe` | ground | vortex_wind | cd 120s · 12s · ground · ×1 uses · wind-up 5s · bound |
| Gehenna's Golden Globe | `wh3_dlc27_cataclysm_bound_gehennas_golden_globe` | ground | vortex_wind | cd 120s · 12s · ground · ×3 uses · wind-up 5s · bound |
| Gehenna's Golden Globe | `wh3_pro10_cataclysm_metal_gehennas_golden_globe_bound` | ground | vortex_wind | cd 120s · 12s · ground · ×2 uses · wind-up 5s · bound |
| Gehenna's Golden Hounds | `wh3_dlc20_spell_bound_gehennas_golden_hounds` | enemy ground | vortex | cd 45s · 13s · enemy ground · ×1 uses · wind-up 3s · bound |
| Gilded Horn of Galon Konook | `wh2_main_item_bound_gilded_horn_of_galon_konook` | enemy ground | vortex | cd 90s · 13s · enemy ground · ×2 uses · wind-up 3s · bound |
| Great Invocation of Sotek | `wh2_dlc12_army_abilities_great_invocation_of_sotek` | enemy ground | vortex_wind | cd 120s · 6s · enemy ground · ×1 uses · wind-up 5s · army |
| Guns of Zharr | `wh3_dlc23_army_abilities_guns_of_zharr` | enemy ground | vortex_wind | cd 60s · 4s · enemy ground · wind-up 2s · army |
| Heaven's Gate | `wh3_cp1_item_abilities_heavens_gate` | ground | vortex | cd 120s · -1s · ground · wind-up 2s |
| Hell Hammer | `wh3_dlc23_spell_bound_hell_hammer` | enemy ground | vortex_wind_ap | cd 50s · 4s · enemy ground · ×1 uses · wind-up 5s · bound |
| Hounds of Orion | `wh_dlc05_lord_ablities_grey_wolves` | enemy ground | vortex | cd 90s · 13s · enemy ground · ×3 uses · wind-up 3s |
| Inevitable Fate | `wh3_pro10_army_abilities_inevitable_fate` | friend | vortex_ap | cd 150s · 15s · friend · wind-up 3s · army |
| Inevitable Fate | `wh3_pro10_army_abilities_inevitable_fate_upgrade_1` | friend | vortex_ap | cd 120s · 20s · friend · wind-up 3s · army |
| Inevitable Fate | `wh3_pro10_army_abilities_inevitable_fate_upgrade_2` | friend | vortex_ap | cd 105s · 25s · friend · wind-up 3s · army |
| Inevitable Fate | `wh3_pro10_army_abilities_inevitable_fate_upgrade_3` | friend | vortex_ap | cd 90s · 30s · friend · wind-up 3s · army |
| Jungle Swarm | `wh2_dlc12_army_abilities_jungle_swarm` | enemy ground | vortex_ap | cd 90s · 26s · enemy ground · ×3 uses · wind-up 3s · army |
| Legionary Barrage | `wh2_dlc09_army_abilities_barrage_of_the_legion` | enemy ground | vortex_wind | cd 90s · 4s · enemy ground · ×3 uses · wind-up 3s · army |
| Lesser Banishment | `wh2_dlc17_spell_bound_lesser_banishment` | enemy ground | vortex | cd 120s · 8s · enemy ground · ×1 uses · wind-up 5s · bound |
| Lesser Chain Lightning | `wh2_dlc17_spell_bound_lesser_chain_lightning` | enemy ground | vortex | cd 120s · 10s · enemy ground · ×1 uses · wind-up 5s · bound |
| Man the Cannons! | `wh2_dlc13_army_abilities_amber_bow_cannons` | enemy ground | vortex_wind | cd 60s · 4s · enemy ground · wind-up 3s · army |
| Nightmaw | `wh3_dlc27_character_abilities_nightmaw` | enemy ground | vortex_wind | cd 45s · 5s · enemy ground · ×3 uses · wind-up 3s |
| Norse Roar | `wh2_dlc11_army_abilities_norse_roar` | enemy ground | vortex_wind | cd 90s · 4s · enemy ground · ×2 uses · wind-up 3s · army |
| Sandstorm | `wh2_dlc09_lord_abilities_sand_storm` | enemy ground | vortex_ap | cd 90s · 14s · enemy ground · ×3 uses · wind-up 3s |
| Seafang | `wh_dlc08_lord_abilities_seafang` | enemy ground | vortex_wind | cd 90s · 8s · enemy ground · ×3 uses · wind-up 4s |
| Skurvy Guns | `wh3_dlc29_endgame_crisis_the_vermintide_enemy_clan_skurvy_guns_hidden` | enemy ground | vortex_wind | cd 75s · 4s · enemy ground · ×3 uses · wind-up 15s · army |
| Sotek's Sanctum | `wh2_dlc17_army_abilities_soteks_sanctum` | enemy ground | vortex_ap | cd 90s · 26s · enemy ground · ×3 uses · wind-up 3s · army |
| Soul-slaying Hunger | `wh3_dlc29_unit_abilities_soul_slaying_hunger` | enemy ground | vortex | cd 120s · 20s · enemy ground · ×1 uses · wind-up 5s |
| Storm of Xholankha | `wh2_dlc13_army_abilities_storm_of_xholankha_upgraded` | enemy ground | vortex_ap | cd 90s · 30s · enemy ground · ×2 uses · wind-up 5s · army |
| Sword of Khaine | `wh2_dlc10_weapon_abilities_sword_of_khaine` | enemy ground | vortex_ap | cd 120s · 11s · enemy ground |
| Tempest of Blue Flame | `wh3_pro10_army_abilities_tempest_of_blue_flame` | ground | vortex_wind | cd 90s · 15s · ground · wind-up 3s · army |
| Tempest of Blue Flame | `wh3_pro10_army_abilities_tempest_of_blue_flame_upgrade_1` | ground | vortex_wind | cd 75s · 20s · ground · wind-up 3s · army |
| Tempest of Blue Flame | `wh3_pro10_army_abilities_tempest_of_blue_flame_upgrade_2` | ground | vortex_wind | cd 60s · 25s · ground · wind-up 3s · army |
| Tempest of Blue Flame | `wh3_pro10_army_abilities_tempest_of_blue_flame_upgrade_3` | ground | vortex_wind | cd 45s · 30s · ground · wind-up 3s · army |
| The Abyssal Swarm | `wh3_dlc29_spell_bound_undeath_the_abyssal_swarm` | enemy ground | vortex | cd 42s · 30s · enemy ground · ×2 uses · wind-up 3s · bound |
| The Burning Head | `wh3_dlc25_spell_bound_fire_the_burning_head` | enemy ground | vortex_wind | cd 90s · 20s · enemy ground · ×1 uses · wind-up 3s · bound |
| The Burning Head | `wh3_dlc29_spell_bound_fire_skull_of_flaming_death` | enemy ground | vortex_wind | cd 90s · 20s · enemy ground · ×3 uses · wind-up 3s · bound |
| The Dwellers Below | `wh3_main_spell_bound_the_dwellers_below` | enemy ground | vortex_ap | cd 120s · 15s · enemy ground · ×1 uses · wind-up 5s · bound |
| The Dwellers Below | `wh_dlc08_spell_bound_the_dwellers_below` | enemy ground | vortex_ap | cd 120s · 15s · enemy ground · ×2 uses · wind-up 5s · bound |
| The Gem of Sunfire | `wh2_main_spell_bound_the_gem_of_sunfire` | enemy ground | vortex | cd 90s · 26s · enemy ground · ×1 uses · wind-up 5s · bound |
| The Matterless Earth | `wh3_dlc27_army_abilities_eternal_dance_tempo_3_carver_of_ways` | ground | vortex_wind | cd 120s · 10s · ground · ×1 uses · wind-up 5s · army |
| The Penumbral Pendulum | `wh3_dlc20_spell_bound_the_penumbral_pendulum` | enemy ground | vortex_wind_ap | cd 40s · 2s · enemy ground · ×1 uses · wind-up 3s · bound |
| The Purple Eclipse | `wh3_dlc25_army_abilities_purple_eclipse` | ground | vortex_ap | cd 120s · 10s · ground · ×1 uses · wind-up 5s · army |
| The Purple Sun of Xereus | `wh2_dlc11_spell_bound_the_purple_sun_of_xereus` | enemy ground | vortex_ap | cd 120s · 11s · enemy ground · ×2 uses · wind-up 5s · bound |
| The Ruination of Cities | `wh2_main_lord_abilities_the_ruination_of_cities` | enemy ground | vortex | cd 120s · 7s · enemy ground · ×2 uses · wind-up 5s |
| The Solid Airs | `wh3_dlc27_army_abilities_eternal_dance_tempo_3_tempest_of_depravity` | ground | vortex_ap | cd 120s · 12s · ground · ×1 uses · wind-up 5s · army |
| Thunder Charge | `wh3_main_army_abilities_thunder_charge` | enemy ground | vortex_wind | cd 120s · 6s · enemy ground · ×2 uses · wind-up 3s · army |
| Tyrant's Talon | `wh3_cp1_weapon_abilities_tyrants_talon` | self | vortex | cd 120s · 27s · self · weapon |
| Wall of Wind & Fire | `wh3_main_spell_bound_wall_of_wind_and_fire` | enemy ground | vortex_wind_ap | cd 90s · 25s · enemy ground · ×2 uses · wind-up 3s · bound |
| Wind of Death | `wh2_dlc15_spell_bound_wind_of_death` | enemy ground | vortex_wind | cd 120s · 5s · enemy ground · ×1 uses · wind-up 5s · bound |
| Wrath of Manann | `wh_dlc07_item_abilities_wrath_of_manann` | enemy ground | vortex_wind | cd 120s · 5s · enemy ground · ×2 uses · wind-up 5s |
| Wrath of Zharr | `wh3_dlc23_army_abilities_wrath_of_zharr` | enemy ground | vortex_wind | cd 90s · 4s · enemy ground · ×2 uses · wind-up 3s · army |
| Zhufbar 42-Pounders | `wh2_dlc11_army_abilities_zhufbar_42_pounders` | enemy ground | vortex_wind | cd 90s · 4s · enemy ground · ×2 uses · wind-up 3s · army |
| Zhufbar 42-Pounders | `wh2_dlc17_army_abilities_zhufbar_42_pounders_engineer` | enemy ground | vortex_wind | cd 90s · 4s · enemy ground · ×1 uses · wind-up 3s · army |

### 2.2 Bombardment / ground artillery — 63 rows

*What it does:* A strike is called down on a **chosen ground point** (artillery / magical bombardment).  ·  *Recommendation:* **EXCLUDE.** Placing it usefully needs an enemy read the engine does not have; blind placement lands on your own line.

| Ability | Key | Target | Effect family (grouped2) | Notes |
|---|---|---|---|---|
| Ancestral Rune of Grimnir | `wh2_dlc17_army_abilities_ancestral_rune_of_grimnir` | ground | aoe_bombardment | cd 120s · 15s · ground · ×1 uses · wind-up 5s · army |
| Arachneruption | `wh2_dlc15_unit_abilities_arachneruption` | self | aoe_bombardment | cd 90s · 2s · self · ×3 uses |
| Assault of Stone | `wh2_dlc10_item_bound_assault_of_stone` | enemy ground | aoe_bombardment | cd 90s · 9s · enemy ground · ×1 uses · wind-up 3s · bound |
| Axe of Tor | `wh3_main_weapon_abilities_axe_of_tor` | enemy ground | aoe_bombardment | cd 90s · 4s · enemy ground · ×3 uses · wind-up 3s |
| Bjuna Bombard | `wh3_dlc25_army_abilities_bjuna_bombard` | ground | aoe_bombardment | cd 120s · 8s · ground · ×1 uses · wind-up 5s · army |
| Bloodwrack Cauldron | `wh2_main_army_abilities_bloodwrack_cauldron` | enemy ground | aoe_bombardment | cd 60s · 7s · enemy ground · ×3 uses · wind-up 5s · army |
| Bonecrusher | `wh3_dlc26_spell_bound_bonecrusher` | enemy ground | aoe_bombardment | cd 90s · 6s · enemy ground · ×1 uses · wind-up 3s · bound |
| Brazen Cauldron | `wh2_main_army_abilities_brazen_cauldron` | enemy ground | aoe_bombardment | cd 60s · 7s · enemy ground · ×3 uses · wind-up 3s · army |
| Bubonic Broadside | `wh3_dlc29_army_abilities_pestilential_bombardment` | ground | aoe_bombardment | cd 90s · 5s · ground · ×2 uses · wind-up 5s |
| Celestial Comet | `wh3_main_mount_bound_celestial_comet` | enemy ground | aoe_bombardment | cd 49s · 7s · enemy ground · ×2 uses · wind-up 5s · bound |
| Celestial Intervention | `wh3_main_army_abilities_celestial_intervention` | enemy ground | aoe_bombardment | cd 120s · 7s · enemy ground · ×1 uses · wind-up 5s · army |
| Celestial Lightning | `wh3_main_mount_bound_celestial_lightning` | enemy ground | aoe_bombardment | cd 42s · 4s · enemy ground · ×2 uses · wind-up 3s · bound |
| Chalice of Potions | `wh_dlc07_item_abilities_chalice_of_potions` | enemy ground | aoe_bombardment | cd 120s · 7s · enemy ground · ×2 uses · wind-up 5s |
| Comet of Casandora | `wh3_main_spell_bound_comet_of_casandora` | enemy ground | aoe_bombardment | cd 120s · 7s · enemy ground · ×1 uses · wind-up 5s · bound |
| Doom Diver Strike | `wh2_dlc15_army_abilities_doom_diver_strike` | ground | aoe_bombardment | cd 90s · 6s · ground · ×5 uses · army |
| Doom of Hashut | `wh3_dlc23_army_abilities_doom_of_hashut` | enemy ground | aoe_bombardment | cd 120s · 7s · enemy ground · ×1 uses · wind-up 5s · army |
| Doomrocket | `wh3_dlc29_endgame_crisis_the_vermintide_enemy_clan_skryre_doomrocket_hidden` | enemy ground | aoe_bombardment | cd 120s · 5s · enemy ground · ×3 uses · wind-up 15s · army |
| Dragon Ogre's Great Horn | `wh_dlc08_item_abilities_great_horn_of_dragon_ogre` | enemy ground | aoe_bombardment | cd 120s · 20s · enemy ground · ×2 uses |
| Dragonship Assault | `wh3_dlc27_army_abilities_dragonship_assault` | enemy ground | aoe_bombardment | cd 60s · 6s · enemy ground · ×3 uses · wind-up 3s · army |
| Dragonship Blitz | `wh3_dlc27_army_abilities_dragonship_blitz` | enemy ground | aoe_bombardment | cd 60s · 6s · enemy ground · ×3 uses · wind-up 3s · army |
| Dragonship Volley | `wh3_dlc27_army_abilities_dragonship_volley` | enemy ground | aoe_bombardment | cd 60s · 6s · enemy ground · ×3 uses · wind-up 3s · army |
| Dreadquake Battery | `wh3_dlc23_army_abilities_tower_ballistics` | ground | aoe_bombardment | cd 90s · 4s · ground · ×1 uses · wind-up 5s · army |
| Dreadquake Battery Upgraded | `wh3_dlc23_army_abilities_tower_ballistics_upgraded_toz` | ground | aoe_bombardment | cd 90s · 4s · ground · ×1 uses · wind-up 5s · army |
| Flame & Shadow | `wh3_dlc23_lord_abilities_flame_and_shadow` | enemy ground | aoe_bombardment | cd 90s · 5s · enemy ground · ×2 uses · wind-up 3s · lord |
| Fly at da Smoke! | `wh3_dlc26_army_abilities_fly_at_da_smoke` | enemy ground | aoe_bombardment | cd 120s · 5s · enemy ground · ×3 uses · wind-up 1s · army |
| Hawk's Talon | `wh_dlc05_weapon_abilities_hawks_talon` | enemy ground | aoe_bombardment | cd 90s · -1s · enemy ground · ×3 uses · wind-up 3s |
| Isha's Rain | `wh2_dlc13_character_ability_ishas_rain` | enemy ground | aoe_bombardment | cd 120s · 9s · enemy ground · ×3 uses · wind-up 3s |
| Khaine's Flail | `wh2_main_army_abilities_khaines_flail` | enemy ground | aoe_bombardment | cd 60s · 4s · enemy ground · ×3 uses · wind-up 3s · army |
| Khaine's Lash | `wh2_main_army_abilities_khaines_lash` | enemy ground | aoe_bombardment | cd 60s · 4s · enemy ground · ×3 uses · wind-up 1s · army |
| Khaine's Scourge | `wh2_main_army_abilities_khaines_scourge` | enemy ground | aoe_bombardment | cd 60s · 4s · enemy ground · ×3 uses · wind-up 5s · army |
| Klad Brakak | `wh2_dlc17_spell_bound_urannons_thunderbolt_upgraded` | enemy ground | aoe_bombardment | cd 30s · 4s · enemy ground · wind-up 3s |
| Lightning Strike | `wh3_dlc29_unit_abilities_lightning_strike` | enemy ground | aoe_bombardment | cd 42s · 4s · enemy ground · ×2 uses · wind-up 3s · bound |
| Lord of the Storm | `wh_main_lord_abilities_lord_of_the_storm` | enemy ground | aoe_bombardment | cd 90s · 11s · enemy ground · ×3 uses · wind-up 1s |
| Master of Lightning | `wh3_dlc29_spell_bound_warp_lightning` | enemy ground | aoe_bombardment | cd 30s · 5s · enemy ground · ×3 uses · wind-up 1s · bound |
| Master Rune of Immolation | `wh2_dlc17_rune_abilities_master_rune_of_immolation` | self | aoe_bombardment | cd 30s · -1s · self |
| Meteor Strike | `wh3_dlc29_unit_abilities_meteor_strike` | enemy ground | aoe_bombardment | cd 49s · 7s · enemy ground · ×3 uses · wind-up 5s · bound |
| Nemesis Crown | `wh3_dlc25_lord_abilities_nemesis_crown` | enemy ground | aoe_bombardment | cd 120s · 10s · enemy ground · wind-up 6s |
| Pandemicium | `wh3_dlc25_army_abilities_pandemicium` | ground | aoe_bombardment | cd 120s · 4s · ground · ×1 uses · wind-up 3s · army |
| Piercing Bolts of Burning | `wh_main_spell_bound_piercing_bolts_of_burning` | enemy ground | aoe_bombardment | cd 120s · 8s · enemy ground · ×4 uses · bound |
| Pigeon Bomb | `wh3_dlc25_character_abilities_pigeon_bomb` | enemy ground | aoe_bombardment | cd 120s · 12s · enemy ground · ×3 uses |
| Rod of the Storm | `wh2_dlc11_army_abilities_rod_of_the_storm` | enemy ground | aoe_bombardment | cd 90s · 4s · enemy ground · ×3 uses · wind-up 3s · army |
| Rod of the Storm | `wh2_main_spell_bound_rod_of_the_storm` | enemy ground | aoe_bombardment | cd 90s · 4s · enemy ground · ×3 uses · wind-up 3s · bound |
| Sceptre of Stone | `wh2_dlc10_item_abilities_sceptre_of_stone` | enemy ground | aoe_bombardment | cd 90s · 9s · enemy ground · ×2 uses · wind-up 5s |
| Searing Doom | `wh3_twa08_spell_bound_searing_doom` | enemy ground | aoe_bombardment | cd 60s · 8s · enemy ground · ×2 uses · wind-up 1s · bound |
| Sky Cauldron | `wh2_main_army_abilities_sky_cauldron` | enemy ground | aoe_bombardment | cd 60s · 7s · enemy ground · ×3 uses · wind-up 1s · army |
| Slicing Shards | `wh3_dlc20_spell_bound_slicing_shards` | enemy ground | aoe_bombardment | cd 48s · 9s · enemy ground · ×1 uses · wind-up 5s · bound |
| Soul Rain | `wh2_main_army_abilities_soul_rain` | enemy ground | aoe_bombardment | cd 60s · 9s · enemy ground · ×3 uses · wind-up 1s · army |
| Soul Storm | `wh2_main_army_abilities_soul_storm` | enemy ground | aoe_bombardment | cd 60s · 9s · enemy ground · ×3 uses · wind-up 5s · army |
| Soul Torrent | `wh2_main_army_abilities_soul_torrent` | enemy ground | aoe_bombardment | cd 60s · 9s · enemy ground · ×3 uses · wind-up 3s · army |
| Storm of Fire | `wh3_main_army_abilities_storm_of_fire` | enemy ground | aoe_bombardment | cd 120s · 27s · enemy ground · wind-up 5s · army |
| The Bow of Loren | `wh_dlc05_weapon_abilities_the_bow_of_loren` | enemy ground | aoe_bombardment | cd 60s · -1s · enemy ground · wind-up 3s |
| The Dreaded Thirteenth Spell | `wh3_dlc29_spell_bound_the_dreaded_thirteenth` | enemy ground | aoe_bombardment | cd 52s · 13s · enemy ground · ×1 uses · wind-up 5s · bound |
| The Dreaded Thirteenth Spell | `wh3_dlc29_spell_bound_the_dreaded_thirteenth_1` | enemy ground | aoe_bombardment | cd 52s · 13s · enemy ground · ×1 uses · wind-up 5s · bound |
| The Dreaded Thirteenth Spell | `wh3_dlc29_spell_bound_the_dreaded_thirteenth_thanquol` | enemy ground | aoe_bombardment | cd 52s · 13s · enemy ground · ×1 uses · wind-up 5s · bound |
| The Dreaded Thirteenth Spell | `wh3_dlc29_spell_bound_the_dreaded_thirteenth_thanquol_1` | enemy ground | aoe_bombardment | cd 52s · 13s · enemy ground · ×1 uses · wind-up 5s · bound |
| Thorsen's Thunderstorm | `wh3_dlc20_cataclysm_bound_thorsens_thunderstorm` | ground | aoe_bombardment | cd 120s · 31s · ground · ×1 uses · wind-up 5s · bound |
| Thorsen's Thunderstorm | `wh3_dlc27_cataclysm_bound_thorsens_thunderstorm` | ground | aoe_bombardment | cd 120s · 31s · ground · ×3 uses · wind-up 5s · bound |
| Urannon's Thunderbolt | `wh2_dlc17_spell_bound_urannons_thunderbolt` | enemy ground | aoe_bombardment | cd 90s · 4s · enemy ground · ×2 uses · wind-up 3s · bound |
| Warp Lightning Rod | `wh2_dlc16_unit_abilities_warp_lightning_rod` | self | aoe_bombardment | cd 60s · 5s · self · ×3 uses · wind-up 1s |
| Warpstorm Doomrocket | `wh2_dlc12_army_abilities_warpstorm_doomrocket` | enemy ground | aoe_bombardment | cd 45s · 7s · enemy ground · ×1 uses · wind-up 5s · army |
| Warpstorm Doomrocket | `wh2_dlc12_army_abilities_warpstorm_doomrocket_upgraded` | enemy ground | aoe_bombardment | cd 45s · 7s · enemy ground · ×1 uses · wind-up 5s · army |
| Warpstorm Doomrocket | `wh3_dlc24_tze_changeling_theatre_scheme_grand_cathay_doom_rocket` | enemy ground | aoe_bombardment | cd 0s · 7s · enemy ground · ×3 uses · wind-up 5s · army |
| Xapati's Sanctum | `wh2_dlc17_army_abilities_xapatis_sanctum` | enemy ground | aoe_bombardment | cd 60s · 5s · enemy ground · ×3 uses · wind-up 3s · army |

### 2.3 Placed / static area damage — 42 rows

*What it does:* A **static area-damage field** centred on a point (often self), damaging everything inside while it lasts.  ·  *Recommendation:* **EXCLUDE.** Same wall: no enemy read to place it, and a self-centred field hits friendlies.

| Ability | Key | Target | Effect family (grouped2) | Notes |
|---|---|---|---|---|
| Acorns of the Oak of Ages | `wh2_dlc16_item_abilities_acorns_of_the_oak_of_ages` | enemy ground | aoe | cd 120s · 12s · enemy ground · ×2 uses · wind-up 3s |
| Arcane Vassal | `wh2_main_character_abilities_arcane_vassal` | friend | aoe | cd 120s · 1s · friend |
| Befuddlement of Mischiefs | `wh2_dlc16_character_abilities_befuddlement_of_mischiefs` | enemy ground | aoe | cd 90s · 11s · enemy ground · ×3 uses |
| Blade of Khorne | `wh3_main_army_abilities_blade_of_khorne` | enemy ground | aoe_ap | cd 120s · 8s · enemy ground · wind-up 5s · army |
| Blight Boil | `wh3_dlc29_endgame_crisis_the_vermintide_enemy_clan_morbidus_pestilent_pustule_hidden` | enemy ground | aoe_ap | cd 60s · 1s · enemy ground · ×3 uses · wind-up 15s · army |
| Blight Boil | `wh3_main_item_abilities_deaths_head` | enemy ground | aoe_ap | cd 120s · 1s · enemy ground · ×2 uses · wind-up 5s · bound |
| Boiling Cauldron | `wh3_dlc26_army_abilities_boiling_cauldron` | enemy ground | aoe_ap | cd 120s · 6s · enemy ground · ×1 uses · wind-up 1.5s · army |
| Boiling Cauldron | `wh3_dlc26_lord_abilities_boiling_cauldron` | enemy ground | aoe_ap | cd 120s · 6s · enemy ground · ×1 uses · wind-up 1.5s |
| Brass Orb | `wh2_dlc12_character_abilities_brass_orb` | enemy ground | aoe_ap | cd 90s · 13s · enemy ground · ×3 uses · wind-up 3s |
| Brass Orb | `wh2_dlc12_character_abilities_brass_orb_tech_lab_doom_flayer` | enemy ground | aoe | cd 90s · 13s · enemy ground · ×3 uses · wind-up 3s |
| Brass Orb Upgraded | `wh2_dlc12_character_abilities_brass_orb_upgrade` | enemy ground | aoe_ap | cd 90s · 13s · enemy ground · ×3 uses · wind-up 3s |
| Chain Lightning | `wh_main_spell_bound_chain_lightning_ror` | enemy ground | aoe_ap | cd 60s · 20s · enemy ground · ×1 uses · wind-up 5s · bound |
| Copious Phlegm | `wh3_dlc27_qb_unit_abilities_copious_phlegm` | enemy ground | aoe_ap | cd 45s · 1s · enemy ground |
| Crackleblaze | `wh3_main_item_abilities_crackleblaze` | enemy ground | aoe | cd 90s · 1s · enemy ground · ×3 uses |
| Foot of Gork | `wh3_dlc26_army_abilities_da_plan_foot_of_gork` | enemy ground | aoe_ap | cd 180s · 8s · enemy ground · ×3 uses · wind-up 5s · army |
| Frost Fang | `wh3_main_weapon_abilities_frost_fang` | enemy ground | aoe_ap | cd 120s · 5s · enemy ground · ×2 uses · wind-up 5s |
| Infernal Gateway | `wh3_dlc20_spell_bound_infernal_gateway` | enemy ground | aoe_ap | cd 54s · 17s · enemy ground · ×1 uses · wind-up 6s · bound |
| Invocation of Ending | `wh2_dlc15_army_abilities_invocation_of_ending` | ground | aoe | cd 120s · 12s · ground · army |
| Irresistible Plague! | `wh3_dlc29_spell_bound_plague` | enemy ground | aoe_ap | cd 50s · 20s · enemy ground · ×1 uses · wind-up 5s · bound |
| Lamprey's Bite | `wh3_dlc24_unit_abilities_lampreys_bite` | ground | aoe | cd 90s · 1s · ground · ×5 uses |
| Magma Storm | `wh3_dlc20_cataclysm_bound_magma_storm` | ground | aoe_ap | cd 120s · 12s · ground · ×1 uses · wind-up 5s · bound |
| Magma Storm | `wh3_dlc27_cataclysm_bound_magma_storm` | ground | aoe_ap | cd 120s · 12s · ground · ×3 uses · wind-up 5s · bound |
| Magma Storm | `wh3_pro10_cataclysm_fire_magma_storm_bound` | ground | aoe_ap | cd 120s · 12s · ground · ×2 uses · wind-up 5s · bound |
| Master Rune of Wrath & Ruin | `wh_dlc06_rune_abilities_master_rune_of_wrath_and_ruin` | enemy ground | aoe_ap | cd 180s · 10s · enemy ground · wind-up 3s · rune |
| Pit of Shades | `wh3_dlc27_spell_bound_pit_of_shades` | enemy ground | aoe_ap | cd 120s · 13s · enemy ground · ×1 uses · wind-up 6s · bound |
| Pit of Shades | `wh3_main_spell_bound_pit_of_shades` | enemy ground | aoe_ap | cd 120s · 13s · enemy ground · ×1 uses · wind-up 6s · bound |
| Pit of Shades | `wh_dlc05_spell_shadow_pit_of_shades_bound` | enemy ground | aoe_ap | cd 49s · 13s · enemy ground · ×1 uses · wind-up 6s · bound |
| Plaguemaster | `wh3_dlc29_spell_bound_plaguemaster` | enemy ground | aoe_ap | cd 50s · 20s · enemy ground · ×2 uses · wind-up 5s · bound |
| Rubric of Dark Dimensions | `wh2_main_spell_bound_rubric_of_dark_dimensions` | enemy ground | aoe_ap | cd 90s · 13s · enemy ground · ×2 uses · wind-up 6s · bound |
| Rune of Wrath & Ruin | `wh_main_rune_abilities_rune_of_wrath_and_ruin` | enemy ground | aoe | cd 120s · 10s · enemy ground · wind-up 3s · rune |
| Shatterstone | `wh2_dlc17_army_abilities_shatterstone` | enemy ground | aoe | cd 45s · 1s · enemy ground · ×2 uses · wind-up 5s · army |
| Siegebreaker | `wh3_main_weapon_abilities_siegebreaker` | enemy ground | aoe | cd 120s · 1s · enemy ground · ×3 uses · wind-up 5s |
| Simmering Pot | `wh3_dlc26_lord_abilities_simmering_pot` | enemy ground | aoe_ap | cd 90s · 6s · enemy ground · ×1 uses · wind-up 1.5s |
| Stoneshaker | `wh3_main_army_abilities_stoneshaker` | enemy ground | aoe | cd 120s · 1s · enemy ground · ×3 uses · wind-up 1s · army |
| The Hammer of Smednir | `wh3_dlc23_item_abilities_hammer_of_smednir` | enemy ground | aoe_ap | cd 120s · 10s · enemy ground · ×3 uses · wind-up 3s |
| Vaul's Hammer | `wh2_main_army_abilities_vauls_hammer` | enemy ground | aoe | cd 120s · 1s · enemy ground · ×2 uses · wind-up 5s · army |
| Vile Entropy | `wh2_dlc17_army_abilities_vile_entropy` | enemy ground | aoe | cd 90s · 20s · enemy ground · ×2 uses · wind-up 5s · army |
| Viletide | `wh_dlc03_spell_bound_viletide` | enemy ground | aoe | cd 60s · 3s · enemy ground · ×4 uses · wind-up 3s · bound |
| Viletide Upgraded | `wh2_dlc17_army_abilities_viletide` | enemy ground | aoe | cd 90s · 3s · enemy ground · ×2 uses · wind-up 3s · army |
| Vortical Blast | `wh2_main_army_abilities_vortic_blast` | enemy ground | aoe | cd 30s · 5s · enemy ground · army |
| Warp Junction | `wh3_dlc29_lord_abilities_warp_junction` | enemy ground | aoe_ap | cd 120s · 14s · enemy ground · ×2 uses · wind-up 3s |
| Winged Staff | `wh2_main_weapon_bound_winged_staff` | enemy ground | aoe | cd 60s · 7s · enemy ground · ×4 uses · bound |

### 2.4 Breath / cone damage — 30 rows

*What it does:* A **forward cone** of damage from the caster (breath weapons, cones).  ·  *Recommendation:* **EXCLUDE.** The cone sweeps friendly units in the arc; no way to check the arc is clear.

| Ability | Key | Target | Effect family (grouped2) | Notes |
|---|---|---|---|---|
| Bangstick | `wh3_main_item_abilities_bangstick` | enemy ground | vortex_breath | cd 90s · 6s · enemy ground · ×3 uses · wind-up 3s |
| Black Dragon Egg | `wh2_main_item_abilities_black_dragon_egg` | enemy ground | vortex_breath_ap | cd 90s · 16s · enemy ground · ×3 uses · wind-up 3s |
| Blue Fire of Chaos | `wh3_main_daemon_arms_abilities_blue_fire` | ground | vortex_breath | cd 30s · 6s · ground · ×2 uses |
| Blue Fire of Chaos Upgraded | `wh3_main_daemon_arms_abilities_blue_fire_upgraded` | ground | vortex_breath | cd 30s · 6s · ground · ×4 uses |
| Da Boss' Loons | `wh2_dlc15_lord_abilities_da_boss_loons` | enemy ground | vortex_breath | cd 30s · 12s · enemy ground · ×2 uses |
| Disembowelling Sweep | `wh3_dlc29_unit_active_ripping_blades` | enemy ground | vortex_breath_ap | cd 90s · 9s · enemy ground · wind-up 1s |
| Fiery Ring of Thori | `wh_main_item_abilities_fiery_ring_of_thori` | enemy ground | vortex_breath | cd 90s · 7s · enemy ground · ×3 uses · wind-up 1s |
| Fishy Breath | `wh2_dlc15_character_abilities_fishy_breathe` | enemy ground | vortex_breath | cd 32s · 6s · enemy ground · ×3 uses · wind-up 0.5s |
| Flesh-eating Scarabs | `wh3_dlc29_unit_abilities_flesh_eating_scarabs` | ground | vortex_breath | cd 90s · 1s · ground · ×3 uses · wind-up 1s |
| Gaze of Malice | `wh2_main_lord_abilities_gaze_of_malice` | enemy ground | vortex_breath | cd 90s · 8s · enemy ground · ×3 uses · wind-up 3s |
| Jade Lion's Breath | `wh3_dlc24_unit_abilities_jade_dragons_breath` | enemy ground | vortex_breath | cd 30s · 3s · enemy ground · ×2 uses · wind-up 1s · bound |
| Kovsh Breath | `wh3_main_item_abilities_kovsh_breath` | enemy ground | vortex_breath | cd 60s · 2s · enemy ground · ×3 uses · wind-up 1s |
| Lash of Slaanesh | `wh3_dlc27_spell_bound_lash_of_slaanesh` | enemy ground | vortex_breath_ap | cd 60s · 6s · enemy ground · ×2 uses · wind-up 1s · bound |
| Lash of Slaanesh | `wh3_main_spell_bound_lash_of_slaanesh` | enemy ground | vortex_breath_ap | cd 30s · 6s · enemy ground · ×2 uses · wind-up 1s · bound |
| Lash of Slaanesh | `wh3_main_spell_bound_lash_of_slaanesh_keeper_of_secrets` | enemy ground | vortex_breath_ap | cd 30s · 6s · enemy ground · ×2 uses · wind-up 1s · bound |
| Pestilent Breath | `wh2_main_mount_bound_pestilent_breath` | enemy ground | vortex_breath | cd 60s · 8s · enemy ground · wind-up 1s |
| Pestilent Breath | `wh3_main_spell_bound_pestilent_breath` | enemy ground | vortex_breath | cd 60s · 8s · enemy ground · ×4 uses · wind-up 1s · bound |
| Pink Fire of Tzeentch | `wh3_dlc20_spell_bound_pink_fire_of_tzeentch` | enemy ground | vortex_breath | cd 30s · 2s · enemy ground · ×2 uses · wind-up 1s · bound |
| Pink Fire of Tzeentch | `wh3_main_spell_tzeentch_pink_fire_of_tzeentch_bound` | enemy ground | vortex_breath | cd 30s · 2s · enemy ground · ×2 uses · wind-up 1s · bound |
| Sartosa Grapeshot | `wh2_dlc11_army_abilities_sartosa_grapeshot` | enemy ground | vortex_breath | cd 90s · 6s · enemy ground · ×2 uses · wind-up 1s · army |
| Scorch | `wh2_main_mount_bound_scorch` | enemy ground | vortex_breath | cd 90s · 12s · enemy ground · wind-up 3s |
| Shadows of Anlec | `wh2_main_army_abilities_shadows_of_anlec` | enemy ground | vortex_breath | cd 60s · 8s · enemy ground · ×3 uses · wind-up 1s · army |
| Shatter | `wh2_dlc13_character_ability_shatter` | enemy ground | vortex_breath | cd 120s · 5s · enemy ground · ×3 uses · wind-up 1s |
| Skabscrath | `wh_main_weapon_abilities_skabscrath` | enemy ground | vortex_breath | cd 90s · 17s · enemy ground · ×3 uses |
| Stream of Corruption | `wh3_dlc20_spell_bound_stream_of_corruption` | enemy ground | vortex_breath_ap | cd 29s · 3s · enemy ground · ×2 uses · wind-up 1s · bound |
| Stream of Corruption | `wh3_main_spell_nurgle_stream_of_corruption_bound` | enemy ground | vortex_breath_ap | cd 29s · 3s · enemy ground · ×2 uses · wind-up 1s · bound |
| Sunfang | `wh2_main_weapon_abilities_sunfang` | enemy ground | vortex_breath | cd 120s · 17s · enemy ground · wind-up 5s |
| The Spear Slaupnir | `wh3_dlc20_weapon_abilities_the_spear_slaupnir` | enemy ground | vortex_breath | cd 120s · 2s · enemy ground · ×2 uses · wind-up 3s |
| Tidecall | `wh2_dlc11_spell_bound_tidecall` | enemy ground | vortex_breath | cd 60s · 2s · enemy ground · ×4 uses · wind-up 1s |
| Wind Blast | `wh2_dlc11_spell_bound_wind_blast` | enemy ground | vortex_breath | cd 60s · 2s · enemy ground · ×4 uses · wind-up 1s |

### 2.5 Own-troop-damage AoE — 26 rows

*What it does:* The ability **deliberately damages your own units** as part of its effect (self-nova / sacrifice AoE).  ·  *Recommendation:* **EXCLUDE.** Harming your own troops by design is not something to auto-fire.

| Ability | Key | Target | Effect family (grouped2) | Notes |
|---|---|---|---|---|
| Ashes & Dust | `wh3_dlc20_cataclysm_bound_ashes_and_dust` | enemy ground | direct_damage_multi_entity_area | cd 120s · 11s · enemy ground · ×1 uses · wind-up 5s · bound |
| Ashes & Dust | `wh3_dlc27_cataclysm_bound_ashes_and_dust` | enemy ground | direct_damage_multi_entity_area | cd 120s · 11s · enemy ground · ×3 uses · wind-up 5s · bound |
| Defiling Deluge | `wh3_twa08_unit_abilities_defiling_deluge` | self | aoe_centred_on_self | cd 120s · 6s · self · ×2 uses · questionnaire §2 #238 |
| Descent Into Dissolution | `wh3_dlc27_army_abilities_eternal_dance_tempo_3_jesters_laughter` | ground | direct_damage_multi_entity_area | cd 120s · 48s · ground · ×2 uses · wind-up 3s · army |
| Eshin Clanstone | `wh2_main_army_abilities_eshin_clanstone` | ground | hex_ranged | cd 120s · 22s · ground · ×3 uses · army |
| Flock of Doom | `wh3_dlc27_spell_bound_runecaller_flock_of_doom` | enemy ground | direct_damage_multi_entity_area | cd 60s · 6s · enemy ground · ×3 uses · wind-up 1s · bound |
| Flock of Doom | `wh3_main_spell_bound_flock_of_doom` | enemy ground | direct_damage_multi_entity_area | cd 60s · 6s · enemy ground · ×2 uses · bound |
| Flock of Doom | `wh_dlc08_spell_bound_flock_of_doom` | enemy ground | direct_damage_multi_entity_area | cd 60s · 6s · enemy ground · ×4 uses · bound |
| Gust of the Grave | `wh3_dlc29_unit_abilities_lesser_tomb_swarm` | ground | direct_damage_multi_entity_area | cd 90s · 18s · ground · ×1 uses · wind-up 5s · army |
| Murderous Exhortations | `wh3_dlc26_lord_abilities_murderous_exhortations` | self | aoe_centred_on_self | cd 120s · 20s · self · ×3 uses · questionnaire §2 #246 |
| Plaguereaper | `wh3_dlc29_item_abilities_plaguereaper` | self | direct_damage_multi_entity_area | cd 120s · 25s · self · ×2 uses |
| Raging Tornado | `wh3_dlc29_unit_abilities_raging_tornado` | ground | direct_damage_multi_entity_area | cd 120s · 32s · ground · ×3 uses · wind-up 5s · bound |
| Reaper of Souls | `wh2_dlc14_lord_abilities_reaper_of_souls` | self | direct_damage_single_entity_area | cd 90s · 9s · self |
| Ring of Corin | `wh2_main_spell_bound_ring_of_corin` | enemy ground | direct_damage_single_entity | cd 90s · 22s · enemy ground · ×2 uses · bound |
| Rod of Corruption | `wh2_main_item_abilities_rod_of_corruption` | self | aoe_centred_on_self | cd 120s · 11s · self · ×3 uses · questionnaire §2 #251 |
| Shard Blade | `wh3_main_weapon_abilities_shard_blade` | self | direct_damage_single_entity_area | cd 120s · 15s · self · ×2 uses |
| Soul Stealer | `wh2_dlc10_spell_bound_soul_stealer_ror` | enemy ground | direct_damage_single_entity_area | cd 120s · 12s · enemy ground · ×1 uses · bound |
| Soul Stealer | `wh3_dlc27_spell_bound_soul_stealer` | enemy ground | direct_damage_single_entity_area | cd 120s · 12s · enemy ground · ×1 uses · bound |
| Sword of Daith | `wh_dlc05_weapon_abilities_daiths_sword` | enemy ground | direct_damage_multi_entity_area | cd 120s · 17s · enemy ground · ×2 uses |
| The Divestment | `wh3_dlc27_army_abilities_eternal_dance_tempo_3_insidious_allure` | ground | direct_damage_multi_entity_area | cd 120s · 24s · ground · ×1 uses · wind-up 3s · army |
| Tomb Swarm | `wh2_dlc09_army_abilities_tomb_swarm` | ground | direct_damage_multi_entity_area | cd 120s · 18s · ground · ×2 uses · wind-up 5s · army |
| Wail of Malice | `wh2_dlc14_unit_abilities_wail_of_malice` | self | direct_damage_multi_entity_area | cd 90s · 7s · self · ×2 uses |
| Warp-Quake | `wh2_dlc14_unit_abilities_warp_quake` | self | direct_damage_multi_entity_area | cd 90s · 17s · self |
| Warpstorm Scroll | `wh2_main_item_abilities_warpstorm_scroll` | enemy ground | hex_flying_area | cd 60s · 29s · enemy ground · ×1 uses |
| Web of Shadows | `wh2_main_weapon_abilities_web_of_shadows` | self | direct_damage_single_entity_area | cd 60s · 17s · self · ×1 uses |
| Zefet-nebtar, the Mortis Blade | `wh3_dlc29_item_abilities_zefet_nebtar_the_mortis_blade` | enemy ground | direct_damage_multi_entity | cd 120s · 1s · enemy ground · ×3 uses · wind-up 2s · item |

### 2.6 Flanking / ambush (flanking_opportunity) — 7 rows

*What it does:* Hide / ambush / reposition effects (spotting and being spotted).  ·  *Recommendation:* **EXCLUDE.** This is the stealth/escape family the user already rejected for other keys.

| Ability | Key | Target | Effect family (grouped2) | Notes |
|---|---|---|---|---|
| Armour of the Stars | `wh2_main_item_abilities_armour_of_the_stars` | self | flanking_opportunity | cd 90s · 73s · self |
| Concealment Bombs | `wh2_main_character_abilities_concealment_bombs` | self | flanking_opportunity | cd 90s · 73s · self · ×3 uses |
| Concealment Bombs | `wh2_main_unit_abilities_concealment_bombs` | self | flanking_opportunity | cd 90s · 73s · self · ×3 uses |
| From the Shadows | `wh3_main_character_abilities_from_the_shadows` | self | flanking_opportunity | cd 120s · 38s · self |
| Hidden in Time | `wh3_main_lord_abilities_hidden_in_time` | self | flanking_opportunity | cd 90s · 73s · self · ×2 uses |
| Loec's Shroud | `wh_pro04_unit_abilities_loecs_shroud` | self | flanking_opportunity | cd 120s · 44s · self |
| Mirror (Loec's Shroud) | `wh2_dlc15_unit_abilities_mimic_loecs_shroud` | self | flanking_opportunity | cd 120s · 44s · self |

---

## 3. INDIVIDUAL — asked one by one (12 items)

These stay `proposed` in the tracker. Each is genuinely case-by-case and cannot be settled by a family rule.

| # | Ability | Key | Owner | Target / family | What it does | Proposed activation |
|---|---|---|---|---|---|---|
| 1 | Blood Sacrifice | `wh3_dlc26_lord_abilities_blood_sacrifice` | lord | friend / healing | Heals a friendly unit at a cost (mixed). | Cast on the lowest-health ally in range when health<=75. |
| 2 | Eat da Runts! | `wh3_dlc26_unit_abilities_eat_da_runts` | unit | friend / healing | Heals a friendly unit at a cost (mixed). | Cast on self / nearest ally when health<=75. |
| 3 | Locus of Virulence | `wh3_main_character_abilities_locus_of_virulence` | character | self / direct_damage_multi_entity_area | A self-centred virulence field with a mixed (buff/hex) net effect. | In melee, cast on self — effect text ambiguous; confirm intent first. |
| 4 | More Powder! | `wh2_dlc11_hero_abilities_more_powder` | hero | friend / ammo_replenish | Restocks a friendly unit's ammunition. | When an ally in range is out of ammo — needs an ammo-low read the engine lacks → likely exclude. |
| 5 | Ominous Powder | `wh3_dlc25_item_abilities_ominous_powder` | item | self / n/a | Effect unknown (no sourceable text). | Exclude pending effect text (unsourceable). |
| 6 | Restock! | `wh2_dlc17_hero_abilities_more_powder_generic` | hero | friend / ammo_replenish | Restocks a friendly unit's ammunition. | When an ally in range is out of ammo — no ammo read → likely exclude. |
| 7 | Restock! | `wh3_dlc25_abilities_restock_gunnery_school` | army (gunnery school) | friend / ammo_replenish | Restocks a friendly unit's ammunition. | When an ally in range is out of ammo — no ammo read → likely exclude. |
| 8 | The Dance of Dreaming | `wh3_dlc27_lord_abilities_the_dance_of_dreaming` | lord | self / direct_damage_multi_entity | Self-centred multi-entity damage/effect, lord, mixed. | In melee, cast on self. |
| 9 | The Soulstealer | `wh3_dlc29_spell_bound_undeath_khizaar_the_soulstealer` | spell-bound | enemy ground / direct_damage_single_entity_area | Bound single-entity area damage placed on enemy ground. | Needs an enemy-ground placement → propose exclude (no placement path). |
| 10 | The Waltz of Lethargy | `wh3_dlc27_lord_abilities_the_waltz_of_lethargy` | lord | self / aoe_centred_on_self | Self-centred lethargy field (questionnaire §2 #207); mixed. | In melee, cast on self. |
| 11 | Touched by the Moon | `wh2_dlc17_army_abilities_touched_by_the_moon` | army | friend / augment_melee | Friendly melee augment (questionnaire §2 #412); army-bar, mixed. | Cast on self / nearest ally while in melee. |
| 12 | Ultimate Verdict | `wh3_cp1_character_abilities_terrifying_presence` | character | self / augment_defense_melee_area | Self-centred melee-defence augment (questionnaire §2 #214); mixed. | In melee, cast on self. |

---

## Appendix — how this maps back to the tracker

- Group **A** (97): tracker status set to `excluded (impossible: <reason>)`.
- Group **B** (238): status left as-is (`proposed (FF)` / `proposed`), each row annotated with its family name.
- Group **C** (12): left `proposed`.

