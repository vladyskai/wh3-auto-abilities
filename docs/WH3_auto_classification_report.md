# WARHAMMER III — auto-classification report (widened standing rules R1–R4)

Scope: **every undecided tracker candidate** — the rows reading `proposed` or `proposed (FF)` in
`WH3_ability_tracker.md` §3a/§3b — swept **in one pass** into auto-accept / auto-exclude / flag.
Classification is derived from the game's own data: `grouped2.json` (effect family),
`unit_spec_abil.tsv` (targeting / engine flags) and the real effect phases
(`phase_junc.tsv` + `phases.tsv`). **Nothing here is built or installed** — this is the triage list.

## Count table

| Bucket | Rows | Share |
|---|---:|---:|
| Total scanned (`proposed` + `proposed (FF)`) | 999 | 100% |
| **AUTO-ACCEPT** (R1 positive buffs / R2 enemy debuffs) | 327 | 32% |
| **AUTO-EXCLUDE** (R3 unsuitable families) | 325 | 32% |
| **FLAG** (R4 — the only items still to ask about) | 347 | 34% |

**Auto-accepted by trigger:** `in-melee self` 274 · `health<=75 (no melee gate)` 37 · `charge and in-melee` 16

**Top auto-exclude reasons:** army-bar ability (standing rule 10) 98 · summon 74 · explosive projectile 52 · vortex 29 · explosive / breath attack 29

**Flag reasons:** friendly fire (FF-parked block) 218 · ambiguous / mixed net effect (needs the user) 70 · friendly fire (own-troop damage) 26 · stealth/escape/stalk effect 11 · mixed positive-and-negative effect 11 · transform/shapechange 11

### How the widened rules were applied

- **R1 positive-only self/ally buffs** → auto-accept, trigger chosen by effect family (melee/weapon/armour/leadership/resistance/ranged/spellcasting buffs → `in-melee self`; charge families → `charge and in-melee`; heals → `health<=75 (no melee gate)`; heal+melee → `in melee and health<=75`).
- **R2 enemy debuffs** (hexes: melee / leadership / armour / speed / ranged / spellcaster) → auto-accept `in-melee self`.
- **R3 unsuitable families** → auto-exclude: vortex · bombardment · explosive/placed AoE · breath · summon (incl. `threatened`) · ground-target-only · no sourceable effect text. **Army-bar abilities** are also auto-excluded under the existing **standing rule 10** (user: “Skip all army bar abilities”) rather than re-queued.
- **R4** → flag only: the **friendly-fire block** (the 218 FF-parked rows), own-troop-damage AoE, rampage, mutual exclusivity, stealth/escape, transform/shapechange, and anything ambiguous or mixed positive/negative.

> **Note on the FF block.** The task's R4 says the friendly-fire rows are *flagged* (“including the FF rows”); their effect families (vortex / bombardment / explosive) are otherwise the ones R3 sweeps. This report follows the
> explicit R4 instruction and **flags all 218**. If you would rather sweep them away as R3 excludes, the single
> change is: flag 347 → 129 and auto-exclude 325 → 543.

> **Note on army-bar.** R4 lists army-bar as a flag category, but the user already gave the standing decision
> “Skip all army bar abilities” (rule 10), so those rows are auto-excluded (reason `army-bar ability`) and never re-asked.
> If you would rather follow R4 literally and flag them, the change is: flag 347 → 445 and auto-exclude 325 → 227.

## Appendix A — AUTO-ACCEPT (all rows)

All 327 rows, sorted by trigger then ability name. Trigger code is what the implementation job will build.

| Ability | Key | Trigger (rule) | One-line effect |
|---|---|---|---|
| Bloodthirst | `wh3_main_lord_abilities_bloodthirst` | charge and in-melee | charge bonus (self) |
| Colossal Strike | `wh3_dlc24_character_abilities_colossal_strike` | charge and in-melee | charge bonus (self) |
| Colossal Strike | `wh3_dlc24_character_abilities_colossal_strike_summoned` | charge and in-melee | charge bonus (self) |
| Crimson Juggernaut | `wh3_dlc26_character_abilities_crimson_juggernaut` | charge and in-melee | charge bonus (self) |
| Daemonic Onslaught | `wh3_main_daemon_legs_abilities_daemonic_onslaught` | charge and in-melee | charge bonus (self) |
| Deadly Onslaught | `wh_dlc03_character_abilities_deadly_onslaught` | charge and in-melee | charge bonus (self) |
| Full Power! | `wh3_dlc25_unit_abilities_full_power` | charge and in-melee | charge bonus (self) |
| Guiding Strike | `wh3_cp1_lord_abilities_guiding_strike` | charge and in-melee | charge bonus (self) |
| Locus of Fury | `wh3_main_character_abilities_locus_of_fury` | charge and in-melee | charge bonus (self) |
| Locus of Swiftness | `wh3_main_character_abilities_locus_of_swiftness` | charge and in-melee | charge bonus (self) |
| Masterful Strike | `wh3_cp1_lord_abilities_mastered_strike` | charge and in-melee | charge bonus (self) |
| More Power! | `wh3_dlc23_unit_abilities_more_power` | charge and in-melee | charge bonus (self) |
| Purge the Weak! | `wh3_main_daemon_wings_abilities_purge_the_weak` | charge and in-melee | charge bonus (self) |
| Shield of Thorns | `wh2_dlc17_spell_bound_shield_of_thorns` | charge and in-melee | charge bonus (applied when charged at) |
| Shield of Thorns | `wh_dlc05_spell_bound_shield_of_thorns` | charge and in-melee | charge bonus (applied when charged at) |
| Storm Hammer | `wh3_dlc29_spell_bound_storm_hammer` | charge and in-melee | charge bonus (self) |
| Berry Wine | `wh2_dlc16_item_abilities_berry_wine` | health<=75 (no melee gate) | heal / hit-point replenish |
| Blood Chalice | `wh3_dlc29_hero_abilities_blood_chalice` | health<=75 (no melee gate) | heal / hit-point replenish |
| Blood Chalice of Bathori | `wh_pro02_item_abilities_blood_chalice_of_bathori` | health<=75 (no melee gate) | heal / hit-point replenish |
| Breath of Darkness | `wh3_dlc29_spell_bound_undeath_morkharn_breath_of_darkness` | health<=75 (no melee gate) | heal / hit-point replenish |
| Breath of Darkness Upgraded | `wh3_dlc29_spell_bound_undeath_morkharn_breath_of_darkness_upgraded` | health<=75 (no melee gate) | heal / hit-point replenish (area) |
| Bugman's XXXXXX | `wh3_dlc26_item_abilities_bugmans_xxxxxx` | health<=75 (no melee gate) | one-use heal / replenish |
| Dreaming Ring I | `wh2_dlc16_item_abilities_dreaming_ring_i` | health<=75 (no melee gate) | heal / hit-point replenish |
| Dreaming Ring II | `wh2_dlc16_item_abilities_dreaming_ring_ii` | health<=75 (no melee gate) | heal / hit-point replenish |
| Dreaming Ring III | `wh2_dlc16_item_abilities_dreaming_ring_iii` | health<=75 (no melee gate) | heal / hit-point replenish |
| Earth Blood | `wh2_dlc16_spell_bound_earth_blood` | health<=75 (no melee gate) | heal / hit-point replenish (area) |
| Earth Blood | `wh3_main_spell_bound_earth_blood` | health<=75 (no melee gate) | heal / hit-point replenish (area) |
| Elvish Healing Herbs | `wh3_dlc27_unit_abilities_elfish_healing_herbs` | health<=75 (no melee gate) | heal / hit-point replenish |
| Fleshy Abundance | `wh3_dlc20_spell_bound_fleshy_abundance` | health<=75 (no melee gate) | heal / hit-point replenish |
| Hieratic Jar | `wh2_dlc09_item_abilities_hieratic_jar` | health<=75 (no melee gate) | one-use heal / replenish |
| Immortal Will | `wh_main_hero_abilities_immortal_will` | health<=75 (no melee gate) | heal / hit-point replenish |
| Invocation of Nehek | `wh3_dlc29_spell_bound_invocation_of_nehek` | health<=75 (no melee gate) | heal / hit-point replenish |
| Locus of Fecundity | `wh3_main_character_abilities_locus_of_fecundity` | health<=75 (no melee gate) | heal / hit-point replenish |
| Makaisson's Persuader | `wh3_dlc25_weapon_abilities_makaissons_persuader` | health<=75 (no melee gate) | heal / hit-point replenish |
| Necroparasites | `wh2_dlc16_unit_abilities_neuroparasites` | health<=75 (no melee gate) | heal / hit-point replenish |
| Necrotic Phylactery | `wh3_dlc25_item_abilities_necrotic_phylactry` | health<=75 (no melee gate) | one-use heal / replenish |
| Patch Up | `wh2_dlc13_character_abilities_patch_up` | health<=75 (no melee gate) | heal / hit-point replenish |
| Pestilent Regeneration | `wh3_main_daemon_head_abilities_pestilent_regeneration` | health<=75 (no melee gate) | heal / hit-point replenish |
| Potion of Charoi | `wh2_main_lord_abilities_potion_of_charoi` | health<=75 (no melee gate) | heal / hit-point replenish |
| Potion of Healing | `wh_main_item_abilities_potion_of_healing` | health<=75 (no melee gate) | one-use heal / replenish |
| Radiant Gem of Hoeth | `wh2_main_spell_bound_radiant_gem_of_hoeth` | health<=75 (no melee gate) | heal / hit-point replenish |
| Reforge | `wh3_dlc23_character_abilities_reforge` | health<=75 (no melee gate) | heal / hit-point replenish |
| Regenerating Flesh | `wh_main_item_abilities_regenerating_flesh` | health<=75 (no melee gate) | heal / hit-point replenish |
| Regrowth | `wh2_dlc16_spell_bound_regrowth` | health<=75 (no melee gate) | heal / hit-point replenish |
| Remouldered | `wh2_dlc16_lord_abilities_remouldered` | health<=75 (no melee gate) | heal / hit-point replenish |
| Restore | `wh2_dlc09_character_abilities_restore` | health<=75 (no melee gate) | heal / hit-point replenish |
| Revivification Crystal | `wh2_main_unit_abilities_revivification_crystal` | health<=75 (no melee gate) | heal / hit-point replenish |
| Saint Annushka's Finger Bone | `wh3_main_item_abilities_saint_annushkas_finger_bone` | health<=75 (no melee gate) | heal / hit-point replenish |
| Salyak's Lullaby | `wh3_main_character_abilities_salyaks_lullaby` | health<=75 (no melee gate) | heal / hit-point replenish (area) |
| Scroll of Power | `wh_main_item_abilities_scroll_of_power` | health<=75 (no melee gate) | heal / hit-point replenish |
| Skalm | `wh2_main_item_abilities_skalm` | health<=75 (no melee gate) | heal / hit-point replenish |
| Skar's Kraken-Killer | `wh3_main_weapon_abilities_skars_kraken_killer` | health<=75 (no melee gate) | heal / hit-point replenish |
| Trollguts | `wh3_dlc26_spell_bound_trollguts` | health<=75 (no melee gate) | heal / hit-point replenish |
| Accusation | `wh_main_hero_abilities_accusation` | in-melee self | enemy melee debuff (hex) |
| Acquiescence | `wh3_dlc27_spell_bound_acquiescence` | in-melee self | enemy melee debuff (hex) |
| Aken-seth, the Staff of Pain | `wh3_dlc29_weapon_abilities_aken_seth_the_staff_of_pain` | in-melee self | enemy armour debuff (hex) |
| Alchemist's Elixir of Iron Skin | `wh3_main_item_abilities_alchemists_elixir_of_iron_skin` | in-melee self | melee combat buff (attack / weapon strength) |
| Alchemist's Elixir of Puissance | `wh3_main_item_abilities_alchemists_elixir_of_puissance` | in-melee self | melee combat buff (attack / weapon strength) |
| Alchemist's Elixir of Venom | `wh3_main_item_abilities_alchemists_elixir_of_venom` | in-melee self | melee combat buff (attack / weapon strength) |
| All Hands Hoay! | `wh2_dlc11_character_abilities_all_hands_hoay` | in-melee self | leadership (morale) buff (area) |
| Amulet of Itzl | `wh2_main_item_abilities_amulet_of_itzl` | in-melee self | melee defence buff |
| Amulet of Pha-Stah | `wh2_dlc09_item_abilities_amulet_of_phastah` | in-melee self | enemy armour debuff (hex, area) |
| Apocalyptic Charge | `wh_pro04_unit_abilities_apocalyptic_charge` | in-melee self | self-centred beneficial aura |
| Arcane Hymn | `wh3_cp1_character_abilities_magic_prayer` | in-melee self | melee defence buff (area) |
| Armour of Caledor | `wh2_dlc15_item_abilities_armour_of_caledor` | in-melee self | spellcasting buff |
| Armour of the Barrows | `wh3_dlc29_item_abilities_armour_of_the_burrows` | in-melee self | enemy melee debuff (hex, area) |
| Assassin's Trophy | `wh2_main_character_abilities_assassins_trophy` | in-melee self | enemy melee debuff (hex) |
| Aura of Inertia | `wh2_dlc13_lord_abilities_aura_of_inertia` | in-melee self | enemy leadership debuff (hex, area) |
| Avast Ye! | `wh2_dlc11_character_abilities_avast_ye` | in-melee self | leadership (morale) buff (area) |
| Axe of Men | `wh_dlc03_weapon_abilities_axe_of_men` | in-melee self | leadership (morale) buff |
| Barbed-Knuckle Boxing | `wh2_dlc17_lord_abilities_barbed_knuckle_boxing` | in-melee self | melee combat buff (attack / weapon strength) |
| Bastet | `wh3_dlc29_lord_abilities_bastet` | in-melee self | enemy melee debuff (hex) |
| Bitter Sting | `wh3_dlc27_qb_unit_abilities_bitter_sting` | in-melee self | enemy melee debuff (hex) |
| Black Periapt | `wh_main_item_abilities_black_periapt` | in-melee self | spellcasting buff |
| Black Staff | `wh2_main_spell_bound_black_staff` | in-melee self | spellcasting buff |
| Blade of Setep | `wh2_dlc09_weapon_abilities_blade_of_setep` | in-melee self | enemy melee debuff (hex, area) |
| Blessed Helm of the Oblast | `wh3_dlc24_item_abilities_blessed_helm_of_the_oblast` | in-melee self | missile (ranged) attack buff (area) |
| Blight of Terrors | `wh2_dlc16_character_abilities_blight_of_terrors` | in-melee self | enemy leadership debuff (hex, area) |
| Blight Swarm | `wh3_main_lord_abilities_blight_swarm` | in-melee self | enemy melee debuff (hex) |
| Blood Omens | `wh3_dlc29_unit_abilities_blood_omens` | in-melee self | enemy ranged debuff (hex, area) |
| Bloody Onslaught | `wh3_dlc26_character_abilities_bloody_onslaught` | in-melee self | enemy armour debuff (hex) |
| Blooood! | `wh_main_unit_abilities_blooood` | in-melee self | melee defence buff |
| Book of Arkhan | `wh_main_spell_bound_book_of_arkhan` | in-melee self | melee combat buff (attack / weapon strength) |
| Book of Hoeth | `wh2_main_item_abilities_book_of_hoeth` | in-melee self | spellcasting buff |
| Book of Secrets | `wh3_dlc24_item_abilities_book_of_secrets` | in-melee self | enemy melee debuff (hex) |
| Boom! | `wh_main_unit_abilities_boom` | in-melee self | missile (ranged) attack buff |
| Call of Violence | `wh_dlc03_character_abilities_call_of_violence` | in-melee self | leadership (morale) buff (area) |
| Cascading Fire Cloak | `wh3_main_spell_bound_cascading_fire_cloak` | in-melee self | melee combat buff (attack / weapon strength) |
| Chalice of Dark Rain | `wh_dlc03_item_abilities_chalice_of_dark_rain` | in-melee self | enemy ranged debuff (hex, area) |
| Channelling Staff | `wh_main_item_abilities_channelling_staff` | in-melee self | spellcasting buff |
| Charmed Shield | `wh_main_weapon_abilities_charmed_shield` | in-melee self | missile resistance / defence buff |
| Cold-Blooded | `wh2_main_character_abilities_cold_blooded` | in-melee self | leadership (morale) buff |
| Crown of Command | `wh_main_item_abilities_crown_of_command` | in-melee self | leadership (morale) buff |
| Cube of Darkness | `wh2_main_item_abilities_cube_of_darkness` | in-melee self | enemy spellcaster debuff (hex) |
| Curse of Khsar | `wh2_dlc09_character_abilities_curse_of_khsar` | in-melee self | enemy armour debuff (hex, area) |
| Daemonic Whispers | `wh3_dlc27_character_abilities_slezuzus_voice` | in-melee self | leadership (morale) buff |
| Dark Fortune | `wh_main_item_abilities_dark_fortune` | in-melee self | melee combat buff (attack / weapon strength) |
| Deranged Munitions | `wh3_dlc25_lord_abilities_deranged_munitions` | in-melee self | missile (ranged) attack buff |
| Deranged Munitions Upgraded | `wh3_dlc25_lord_abilities_deranged_munitions_upgraded` | in-melee self | missile (ranged) attack buff (area) |
| Don't Even Try It | `wh2_dlc15_lord_abilities_dont_even_try_it` | in-melee self | enemy melee debuff (hex) |
| Doom & Darkness | `wh3_dlc25_spell_Bound_doom_and_darkness_gunnery_school` | in-melee self | enemy leadership debuff (hex) |
| Doom & Darkness | `wh3_dlc27_spell_bound_runecaller_death_doom_and_darkness` | in-melee self | enemy leadership debuff (hex) |
| Doom & Darkness | `wh_dlc08_spell_bound_death_doom_and_darkness` | in-melee self | enemy leadership debuff (hex) |
| Doom Lord | `wh3_dlc29_lord_abilities_doom_lord` | in-melee self | melee combat buff (attack / weapon strength) |
| Earthing Rod | `wh_main_item_abilities_earthing_rod` | in-melee self | spellcasting buff |
| El Syf | `wh_dlc05_weapon_abilities_el_syf` | in-melee self | enemy melee debuff (hex) |
| Elixir of Might | `wh2_dlc09_item_abilities_elixir_of_might` | in-melee self | melee combat buff (attack / weapon strength) |
| Embers of the Phoenix | `wh2_main_spell_bound_embers_of_the_phoenix` | in-melee self | missile (ranged) attack buff (area) |
| Enchanted Ballistics | `wh2_dlc11_character_abilities_ballistic_enchantment` | in-melee self | missile (ranged) attack buff (area) |
| Enhanced Skavenbrew | `wh3_dlc29_item_abilities_enhanced_skavenbrew` | in-melee self | melee combat buff (attack / weapon strength) |
| Entangle | `wh2_dlc10_character_abilities_entangle` | in-melee self | enemy speed debuff (hex, under fire) |
| Entrenchment | `wh_main_unit_abilities_entrenchment` | in-melee self | missile (ranged) attack buff |
| Eternal Gaze | `wh3_dlc29_lord_abilities_gaze_of_usirian` | in-melee self | enemy leadership debuff (hex) |
| Eternal Vigour | `wh3_dlc29_character_abilities_eternal_vigour` | in-melee self | melee defence buff (area) |
| Extra Ingredients | `wh3_main_character_abilities_extra_ingredients` | in-melee self | spellcasting buff |
| Favoured by the Matriarch | `wh3_dlc27_hero_abilities_favoured_by_the_matriarch` | in-melee self | missile resistance / defence buff |
| Fear of Aramar | `wh2_dlc10_item_abilities_fear_of_aramar` | in-melee self | enemy leadership debuff (hex) |
| Fearsome Roar | `wh3_dlc24_unit_abilities_fearsome_roar` | in-melee self | enemy leadership debuff (hex, area) |
| Fecund Rebirth | `wh3_dlc29_character_active_mark_of_the_monster` | in-melee self | enemy melee debuff (hex) |
| Fermented Fungi | `wh2_dlc15_lord_abilities_fermented_fungi` | in-melee self | enemy melee debuff (hex) |
| Fight or Die! | `wh_dlc08_lord_abilities_fight_or_die` | in-melee self | leadership (morale) buff (area) |
| Fistful of Laurels | `wh3_main_item_abilities_fistful_of_laurels` | in-melee self | melee combat buff (area, allies in range) |
| Flesh to Stone | `wh2_dlc16_spell_bound_flesh_to_stone` | in-melee self | melee combat buff (attack / weapon strength) |
| Focus Instincts | `wh2_dlc12_lord_abilities_focus_instincts` | in-melee self | leadership (morale) buff |
| Forbidden Rod | `wh_main_item_abilities_forbidden_rod` | in-melee self | spellcasting buff |
| Frenzied Challenge | `wh3_dlc27_qb_unit_abilities_frenzied_challenge` | in-melee self | enemy melee debuff (hex) |
| Frost Shard Glaive | `wh3_main_weapon_abilities_frost_shard_glaive` | in-melee self | self-centred melee hex aura |
| Funnel of Flame | `wh2_dlc13_lord_abilities_funnel_of_flame` | in-melee self | missile (ranged) attack buff |
| Gaze of Fate | `wh3_main_lord_abilities_gaze_of_fate` | in-melee self | enemy melee debuff (hex) |
| Get 'Em! | `wh3_dlc25_character_abilities_get_em` | in-melee self | enemy speed debuff (hex, under fire) |
| Get Back 'Ere! | `wh_main_character_abilities_get_back_ere` | in-melee self | leadership (morale) buff (area) |
| Gilellion's Soulnetter | `wh3_main_weapon_abilities_soulnetter` | in-melee self | enemy melee debuff (hex) |
| Glacial Defence | `wh3_twa08_unit_abilities_glacial_defence` | in-melee self | missile resistance / defence buff |
| Glory Seeker | `wh3_dlc29_hero_active_glory_seeker` | in-melee self | enemy melee debuff (hex) |
| Glory Seeker Upgraded | `wh3_dlc29_hero_active_glory_seeker_upgraded` | in-melee self | enemy melee debuff (hex) |
| Grut's Sickle | `wh3_main_item_abilities_gruts_sickle` | in-melee self | spellcasting buff |
| Guttural Roar | `wh3_dlc27_qb_unit_abilities_guttural_roar` | in-melee self | enemy leadership debuff (hex, area) |
| Hagtree Fetish | `wh_dlc03_item_abilities_hagtree_fetish` | in-melee self | spellcasting buff |
| Hail of Fire | `wh2_dlc13_lord_abilities_hail_of_fire` | in-melee self | missile (ranged) attack buff |
| Harmonic Convergence | `wh3_main_spell_bound_harmonic_convergence` | in-melee self | melee combat buff (attack / weapon strength) |
| Headhunt | `wh3_dlc26_character_abilities_headhunt` | in-melee self | enemy melee debuff (hex) |
| Hellish Vigour | `wh3_dlc29_lord_abilities_hellish_vigour` | in-melee self | melee combat buff (attack / weapon strength) |
| Hellish Vigour Upgraded | `wh3_dlc29_lord_abilities_hellish_vigour_upgraded` | in-melee self | melee combat buff (area, allies in range) |
| Hidden Huntress | `wh3_cp1_lord_abilities_hidden_huntress` | in-melee self | enemy armour debuff (hex) |
| Hidden Huntress Upgraded | `wh3_cp1_lord_abilities_hidden_huntress_upgraded` | in-melee self | enemy armour debuff (hex) |
| Horn of the Wild Hunt | `wh_dlc05_item_abilities_horn_of_the_wild_hunt` | in-melee self | melee combat buff (area, allies in range) |
| Horn of Vaul | `wh2_main_item_abilities_dragonhorn` | in-melee self | missile (ranged) attack buff (area) |
| Hornswaggle | `wh2_dlc11_character_abilities_hornswaggle` | in-melee self | enemy melee debuff (hex) |
| Howl of the Great Beast | `wh3_dlc24_unit_abilities_howl_of_the_great_beast` | in-melee self | enemy leadership debuff (hex, area) |
| Hunter of Champions | `wh_dlc08_character_abilities_hunter_of_champions` | in-melee self | enemy melee debuff (hex) |
| Hunter's Snare | `wh2_dlc13_lord_abilities_hunters_snare` | in-melee self | enemy speed debuff (hex, area) |
| Hunter's Trap | `wh2_dlc13_lord_abilities_hunters_trap` | in-melee self | enemy speed debuff (hex, area) |
| Hysterical Frenzy | `wh3_main_spell_slaanesh_hysterical_frenzy_bound` | in-melee self | melee combat buff (attack / weapon strength) |
| Inspired Marksmanship I | `wh3_main_lord_abilities_inspired_marksmanship_i` | in-melee self | missile (ranged) attack buff |
| Inspired Marksmanship II | `wh3_main_lord_abilities_inspired_marksmanship_ii` | in-melee self | missile (ranged) attack buff |
| Inspired Marksmanship III | `wh3_main_lord_abilities_inspired_marksmanship_iii` | in-melee self | missile (ranged) attack buff |
| Iron-Handed Captain | `wh3_dlc27_character_abilities_iron_hand_captain` | in-melee self | leadership (morale) buff |
| Jagged Dagger | `wh_dlc03_item_abilities_jagged_dagger` | in-melee self | spellcasting buff |
| Locus of Abjuration | `wh3_main_character_abilities_locus_of_abjuration` | in-melee self | missile resistance / defence buff (area) |
| Locus of Change | `wh3_main_character_abilities_locus_of_change` | in-melee self | missile (ranged) attack buff (area) |
| Locus of Conjuration | `wh3_main_character_abilities_locus_of_conjuration` | in-melee self | spellcasting buff |
| Looming Dread | `wh2_dlc14_lord_abilities_looming_dread` | in-melee self | enemy melee debuff (hex) |
| Lord of Dragons | `wh2_dlc15_lord_abilities_lord_of_dragons` | in-melee self | enemy melee debuff (hex) |
| Magical Animus | `wh_main_character_abilities_magical_animus` | in-melee self | leadership (morale) buff |
| Mark of the Plague Fleet | `wh3_dlc29_item_active_mark_of_the_plague_fleet` | in-melee self | enemy melee debuff (hex) |
| Mark of Yin | `wh3_dlc24_unit_abilities_mark_of_yin` | in-melee self | enemy ranged debuff (hex) |
| Marked by Ulthar | `wh_dlc06_unit_abilities_marked_by_ulthar` | in-melee self | enemy ranged debuff (hex) |
| Marked for Eatin' | `wh3_dlc26_unit_abilities_marked_for_eatin` | in-melee self | enemy melee debuff (hex) |
| Master of Beguilement | `wh_dlc04_lord_abilities_beguile` | in-melee self | enemy melee debuff (hex) |
| Master of the Black Arts | `wh_main_lord_abilities_master_of_the_black_arts` | in-melee self | spellcasting buff |
| Master Predator | `wh2_dlc17_lord_abilities_master_predator` | in-melee self | missile (ranged) attack buff |
| Master Rune of Breaking | `wh2_dlc17_rune_abilities_master_rune_of_breaking` | in-melee self | melee combat buff (attack / weapon strength) |
| Master Rune of Negation | `wh_dlc06_rune_abilities_master_rune_of_negation` | in-melee self | melee defence buff (area) |
| Master Rune of Slowness | `wh2_dlc17_rune_abilities_master_rune_of_slowness` | in-melee self | enemy speed debuff (hex, under fire) |
| Maw Shard | `wh3_main_item_abilities_maw_shard` | in-melee self | spellcasting buff |
| Merciw's Monstrous Regiment | `wh3_dlc20_cataclysm_bound_merciws_monstrous_regiment` | in-melee self | melee combat buff (attack / weapon strength) |
| Merciw's Monstrous Regiment | `wh3_dlc27_cataclysm_bound_merciws_monstrous_regiment` | in-melee self | melee combat buff (attack / weapon strength) |
| Miasma of Despair | `wh2_dlc13_lord_abilities_miasma_of_despair` | in-melee self | enemy leadership debuff (hex, area) |
| Mighty Oath Stone | `wh_dlc06_lord_abilities_mighty_oath_stone` | in-melee self | leadership (morale) buff (area) |
| Mighty Roar | `wh2_dlc15_unit_abilities_mighty_roar` | in-melee self | enemy leadership debuff (hex, area) |
| Mirror (Cold-Blooded) | `wh2_dlc15_unit_abilities_mimic_cold_blooded` | in-melee self | leadership (morale) buff |
| Mirror (Feint & Riposte) | `wh2_dlc15_unit_abilities_mimic_feint_and_riposte` | in-melee self | melee combat buff (attack / weapon strength) |
| Mirror (Grand Hammer of Faith) | `wh2_dlc15_unit_abilities_mimic_grand_hammer_of_faith` | in-melee self | melee combat buff (attack / weapon strength) |
| Missile Mirror | `wh3_dlc24_unit_bound_missile_mirror` | in-melee self | enemy ranged debuff (hex) |
| Mither | `wh2_dlc15_hero_abilities_mither` | in-melee self | enemy leadership debuff (hex) |
| Moonshine | `wh2_dlc11_item_abilities_moonshine` | in-melee self | leadership (morale) buff |
| Morgrim's Eye | `wh3_dlc23_item_abilities_morgrims_eye` | in-melee self | missile (ranged) attack buff (area) |
| Muster of Malevolents | `wh2_dlc16_character_abilities_muster_of_malevolents` | in-melee self | enemy melee debuff (hex) |
| Neferra's Scrolls of Mighty Incantations | `wh2_dlc09_item_abilities_neferras_scrolls_of_mighty_incantations` | in-melee self | spellcasting buff |
| Net Dem Up! | `wh3_dlc26_unit_abilities_net_dem_up` | in-melee self | enemy melee debuff (hex) |
| Net of Amyntok | `wh_dlc04_spell_bound_net_of_amyntok` | in-melee self | enemy speed debuff (hex, under fire) |
| Null Stone | `wh3_dlc27_item_abilities_null_stone` | in-melee self | enemy spellcasting debuff (hex) |
| Oath of Vengeance | `wh2_dlc10_lord_abilities_oath_of_vengeance` | in-melee self | enemy melee debuff (hex) |
| Oil Flask | `wh2_dlc13_lord_abilities_oil_flask` | in-melee self | enemy speed debuff (hex, under fire) |
| Otto's Scythe | `wh3_dlc29_item_active_ottos_scythe` | in-melee self | enemy melee debuff (hex) |
| Pack Trap | `wh3_dlc24_unit_abilities_pack_trap` | in-melee self | enemy melee debuff (hex) |
| Pageant of Shrikes | `wh2_dlc16_character_abilities_pageant_of_shrikes` | in-melee self | enemy ranged debuff (hex) |
| Pearl of Infinite Bleakness | `wh2_main_item_abilities_pearl_of_infinite_bleakness` | in-melee self | leadership (morale) buff (area) |
| Pestilent Potions | `wh3_dlc20_item_abilities_pestilent_potions` | in-melee self | enemy melee debuff (hex) |
| Pha's Protection | `wh3_main_spell_bound_phas_protection` | in-melee self | melee combat buff (attack / weapon strength) |
| Pilgrimage of Skulls | `wh3_dlc26_lord_abilities_pilgrimage_of_skulls` | in-melee self | melee combat buff (area, allies in range) |
| Plague of Rust | `wh3_main_spell_bound_plague_of_rust` | in-melee self | enemy armour debuff (hex) |
| Plaque of Dominion | `wh2_main_item_abilities_plaque_of_dominion` | in-melee self | enemy leadership debuff (hex, area) |
| Potion of Farsight | `wh3_main_item_abilities_potion_of_farsight` | in-melee self | missile (ranged) attack buff |
| Potion of Foolhardiness | `wh_main_item_abilities_potion_of_foolhardiness` | in-melee self | leadership (morale) buff |
| Potion of Speed | `wh_main_item_abilities_potion_of_speed` | in-melee self | missile resistance / defence buff |
| Power Familiar | `wh3_dlc27_item_abilities_power_familiar` | in-melee self | spellcasting buff |
| Power Siphon | `wh2_dlc11_lord_abilities_power_siphon` | in-melee self | enemy spellcaster debuff (hex) |
| Power Stone | `wh_main_item_abilities_power_stone` | in-melee self | spellcasting buff |
| Predatory Instincts | `wh3_cp1_lord_abilities_predatory_instincts` | in-melee self | melee defence buff |
| Prey of Anath Raema | `wh_dlc05_character_abilities_prey_of_anath_raema` | in-melee self | enemy melee debuff (hex) |
| Prey of the Blood God | `wh3_pro12_hero_abilities_prey_of_the_blood_god` | in-melee self | enemy melee debuff (hex) |
| Prismatic Amplifier | `wh3_main_item_abilities_prismatic_amplifier` | in-melee self | spellcasting buff |
| Rally! | `wh_main_character_abilities_rally` | in-melee self | leadership (morale) buff (area) |
| Ravaging Swarm | `wh3_dlc29_hero_active_dispatch_the_swarm_attack` | in-melee self | enemy melee debuff (hex) |
| Ravaging Swarm Upgraded | `wh3_dlc29_hero_active_dispatch_the_swarm_attack_upgraded` | in-melee self | enemy melee debuff (hex) |
| Reanimate | `wh2_dlc09_character_abilities_tomb_king_rally` | in-melee self | leadership (morale) buff (area) |
| Reanimate Upgraded | `wh2_dlc09_character_abilities_tomb_king_rally_upgraded` | in-melee self | leadership (morale) buff (area) |
| Red Fury | `wh_main_character_abilities_red_fury` | in-melee self | melee combat buff (attack / weapon strength) |
| Rock Eye | `wh3_main_item_passive_rock_eye` | in-melee self | enemy ranged debuff (hex, area) |
| Rune of Breaking | `wh2_dlc17_rune_abilities_rune_of_breaking` | in-melee self | melee combat buff (attack / weapon strength) |
| Rune of Negation | `wh_main_rune_abilities_rune_of_negation` | in-melee self | melee defence buff (area) |
| Rune of Slowness | `wh2_dlc17_rune_abilities_rune_of_slowness` | in-melee self | enemy speed debuff (hex, under fire) |
| Rune of Thungni | `wh3_dlc23_item_abilities_rune_of_thungni` | in-melee self | melee combat buff (attack / weapon strength) |
| Sadistic Snare | `wh3_dlc23_lord_abilities_sadistic_snare` | in-melee self | enemy melee debuff (hex) |
| Sceptre of Stability | `wh_main_item_abilities_sceptre_of_stability` | in-melee self | missile resistance / defence buff |
| Scroll of Destiny | `wh3_main_item_abilities_scroll_of_destiny` | in-melee self | spellcasting buff |
| Scroll of Leeching | `wh_main_item_abilities_scroll_of_leeching` | in-melee self | enemy spellcaster debuff (hex) |
| Scroll of Shielding | `wh_main_item_abilities_scroll_of_shielding` | in-melee self | melee defence buff |
| Shield of Chaqua | `wh2_dlc12_unit_abilities_shield_of_chaqua` | in-melee self | missile resistance / defence buff |
| Shielding Swarm | `wh3_dlc29_hero_active_dispatch_the_swarm_protect` | in-melee self | melee combat buff (area, allies in range) |
| Shielding Swarm Upgraded | `wh3_dlc29_hero_active_dispatch_the_swarm_protect_upgraded` | in-melee self | melee combat buff (area, allies in range) |
| Shock Collar | `wh2_dlc16_hero_abilities_shock_collar` | in-melee self | leadership (morale) buff |
| Silence the Prey | `wh3_main_character_abilities_silence_the_prey` | in-melee self | enemy spellcaster debuff (hex) |
| Skavenbrew | `wh2_main_item_abilities_skavenbrew` | in-melee self | melee combat buff (attack / weapon strength) |
| Skjalandir's Fall | `wh3_dlc23_character_abilities_skjalandirs_fall` | in-melee self | missile (ranged) attack buff |
| Skull of Rarkos | `wh_dlc03_item_abilities_skull_of_rarkos` | in-melee self | spellcasting buff |
| Snowflake Pendant | `wh3_main_item_abilities_snowflake_pendant` | in-melee self | spellcasting buff |
| Spearfisher's Net | `wh2_dlc11_lord_abilities_spearfishers_net` | in-melee self | enemy melee debuff (hex) |
| Spell-Wrought Sceptre | `wh3_dlc23_weapon_abilities_spell_wrought_sceptre` | in-melee self | spellcasting buff |
| Spiderweb Attack | `wh3_dlc26_character_abilities_spider_web_attack` | in-melee self | enemy melee debuff (hex) |
| Staff of Damnation | `wh_main_spell_bound_staff_of_damnation` | in-melee self | self / ally buff (area) |
| Staff of Nagash | `wh2_dlc09_item_abilities_staff_of_nagash` | in-melee self | spellcasting buff |
| Staff of Tomorrow | `wh3_main_weapon_abilities_staff_of_tomorrow` | in-melee self | spellcasting buff |
| Staff of Volans | `wh_main_item_abilities_staff_of_volans` | in-melee self | spellcasting buff |
| Staff of Wu Xing | `wh3_main_item_abilities_staff_of_wu_xing` | in-melee self | spellcasting buff |
| Starwood Staff | `wh2_main_item_abilities_starwood_staff` | in-melee self | spellcasting buff |
| Stave of Avelorn | `wh2_dlc10_item_abilities_stave_of_avelorn` | in-melee self | spellcasting buff |
| Sword of Filth | `wh3_dlc25_weapon_abilities_sword_of_filth` | in-melee self | enemy armour debuff (hex) |
| Tacticians, Rally! | `wh3_dlc24_character_abilities_tacticians_rally` | in-melee self | leadership (morale) buff (area) |
| Taunt | `wh2_dlc11_character_abilities_taunt` | in-melee self | enemy melee debuff (hex) |
| Tendrils of the Sea | `wh3_dlc29_hero_active_tendrils_of_the_sea` | in-melee self | enemy melee debuff (hex) |
| Terrorgheist Skull | `wh_dlc08_item_abilities_terrorgheist_skull` | in-melee self | spellcasting buff |
| The Averland Runefang | `wh2_dlc13_weapon_abilities_averland_runefang` | in-melee self | enemy melee debuff (hex) |
| The Bane Shield | `wh2_main_item_abilities_the_bane_shield` | in-melee self | missile resistance / defence buff (area) |
| The Black Tongue | `wh3_dlc27_character_abilities_the_black_tongue` | in-melee self | enemy melee debuff (hex) |
| The Chromatic Tome | `wh3_main_item_abilities_the_chromatic_tome` | in-melee self | spellcasting buff |
| The Dark Master | `wh3_main_lord_abilities_the_dark_master` | in-melee self | enemy melee debuff (hex) |
| The Enfeebling Foe | `wh3_dlc23_spell_bound_enfeebling_foe` | in-melee self | enemy melee debuff (hex) |
| The Enfeebling Foe | `wh3_dlc27_spell_bound_enfeebling_foe` | in-melee self | enemy melee debuff (hex) |
| The Enfeebling Foe | `wh3_main_spell_bound_enfeebling_foe` | in-melee self | enemy melee debuff (hex) |
| The Enfeebling Foe | `wh3_twa08_spell_bound_enfeebling_foe_keeper_of_secrets_ror` | in-melee self | enemy melee debuff (hex) |
| The Golden Eye of Tzeentch | `wh3_dlc24_item_abilities_the_golden_eye_of_tzeentch` | in-melee self | missile resistance / defence buff |
| The Guiding Eye | `wh2_main_item_abilities_the_guiding_eye` | in-melee self | missile (ranged) attack buff (area) |
| The Hammer of Karak Drazh | `wh_main_weapon_abilities_the_hammer_of_karak_drazh` | in-melee self | enemy melee debuff (hex) |
| The Hand of Dust | `wh3_dlc29_spell_bound_undeath_sulekhim_hand_of_dust` | in-melee self | melee combat buff (attack / weapon strength) |
| The Liber Noctus | `wh_dlc04_item_abilities_the_liber_noctus` | in-melee self | spellcasting buff |
| The Lion's Shield | `wh_dlc07_lord_abilities_lions_shield` | in-melee self | missile resistance / defence buff |
| The Praise of Slaanesh | `wh3_dlc27_lord_abilities_the_praise_of_slaanesh` | in-melee self | melee defence buff |
| The Seerstaff of Saphery | `wh2_main_spell_bound_the_seerstaff_of_saphery` | in-melee self | missile (ranged) attack buff |
| The Trickster's Pendant | `wh2_main_item_abilities_the_tricksters_pendant` | in-melee self | enemy spellcaster debuff (hex) |
| The Vial of Hashut | `wh3_dlc23_item_abilities_the_vial_of_hashut` | in-melee self | enemy armour debuff (hex) |
| The Vortex Shard | `wh2_main_item_abilities_the_vortex_shard` | in-melee self | enemy spellcaster debuff (hex) |
| The Wintertooth Crown | `wh_dlc08_item_abilities_the_wintertooth_crown` | in-melee self | leadership (morale) buff (area) |
| The Wissenland Runefang | `wh2_dlc13_weapon_abilities_wissenland_runefang` | in-melee self | self-centred melee hex aura |
| The Withering | `wh3_dlc23_spell_bound_the_withering` | in-melee self | enemy leadership debuff (hex) |
| The Withering | `wh3_twa08_spell_bound_the_withering` | in-melee self | enemy leadership debuff (hex) |
| They Needs Stabbin’ | `wh2_dlc15_character_abilities_they_needs_stabbin` | in-melee self | enemy melee debuff (hex) |
| Thorn's Aura | `wh3_dlc24_hero_abilities_thorns_aura` | in-melee self | enemy leadership debuff (hex, area) |
| Thunderburner | `wh3_dlc25_unit_abilities_thunderburner` | in-melee self | enemy speed debuff (hex, under fire) |
| Thunderburner Upgraded | `wh3_dlc25_unit_abilities_thunderburner_upgraded` | in-melee self | enemy speed debuff (hex, under fire) |
| Titan Headsman | `wh3_dlc25_hero_abilities_titan_headsman` | in-melee self | enemy melee debuff (hex) |
| Torment Blade | `wh3_main_weapon_abilities_torment_blade` | in-melee self | enemy melee debuff (hex) |
| Trickster's Shard | `wh_main_item_abilities_tricksters_shard` | in-melee self | enemy spellcaster debuff (hex) |
| Trophy Heads | `wh2_main_lord_abilities_trophy_heads` | in-melee self | enemy melee debuff (hex) |
| Trophy Heads | `wh3_main_daemon_wings_abilities_trophy_heads` | in-melee self | enemy melee debuff (hex) |
| Twilight Horn I | `wh2_dlc16_item_abilities_twilight_horn_i` | in-melee self | melee combat buff (attack / weapon strength) |
| Undeath Resurgent | `wh_main_character_abilities_undeath_resurgent` | in-melee self | melee combat buff (area, allies in range) |
| Unholy Clamour | `wh2_main_mount_abilities_unholy_clamour` | in-melee self | leadership (morale) buff |
| Unlimited Power! | `wh2_dlc12_lord_abilities_unlimited_power` | in-melee self | spellcasting buff |
| Ursun's Mighty Roar | `wh3_main_pro_character_abilities_ursuns_roar_2` | in-melee self | leadership (morale) buff (area) |
| Ursun's Roar | `wh3_main_character_abilities_ursuns_roar` | in-melee self | leadership (morale) buff (area) |
| Ursun's Roar | `wh3_main_pro_character_abilities_ursuns_roar` | in-melee self | leadership (morale) buff (area) |
| Ursun's Roar | `wh3_main_pro_character_abilities_ursuns_roar_1` | in-melee self | leadership (morale) buff (area) |
| Ursun's Roar | `wh3_main_pro_character_abilities_ursuns_roar_3` | in-melee self | leadership (morale) buff (area) |
| Van Horstmann's Speculum | `wh_main_item_abilities_van_horstmanns_speculum` | in-melee self | enemy melee debuff (hex, area) |
| Verminous Fury | `wh3_dlc29_lord_abilities_verminous_fury` | in-melee self | melee combat buff (attack / weapon strength) |
| Virulent Contagion | `wh3_main_lord_abilities_virulent_contagion` | in-melee self | enemy melee debuff (hex) |
| Virulent Contagion Upgraded | `wh3_main_lord_abilities_virulent_contagion_upgraded` | in-melee self | enemy melee debuff (hex) |
| Visions of Madness | `wh3_dlc27_qb_unit_abilities_visions_of_madness` | in-melee self | enemy melee debuff (hex) |
| Void Pendulum | `wh3_main_item_abilities_void_pendulum` | in-melee self | enemy spellcasting debuff (hex) |
| Vorozheja's Foresight | `wh3_dlc24_hero_abilities_vorozhejas_foresight` | in-melee self | enemy ranged debuff (hex) |
| Waaagh! | `wh3_dlc26_unit_abilities_waaagh_in_combat` | in-melee self | melee combat buff (attack / weapon strength) |
| Waaagh! | `wh_main_character_abilities_waaagh` | in-melee self | melee combat buff (area, allies in range) |
| Wand of Jet | `wh_main_item_abilities_wand_of_jet` | in-melee self | spellcasting buff |
| Warden's Cage | `wh2_dlc15_character_abilities_wardens_cage` | in-melee self | enemy melee debuff (hex) |
| Warp Gaze | `wh_pro04_unit_abilities_warp_gaze` | in-melee self | enemy speed debuff (hex, under fire) |
| Warpstiletto | `wh3_dlc29_item_abilities_warpstiletto` | in-melee self | enemy speed debuff (hex, under fire) |
| Warpstone Tokens | `wh3_dlc29_item_abilities_warpstone_tokens` | in-melee self | spellcasting buff |
| Watched by the Watcher | `wh3_dlc24_character_abilities_watched_by_the_watcher` | in-melee self | enemy ranged debuff (hex, area) |
| Where You Goin!? | `wh3_dlc26_character_abilities_were_you_goin` | in-melee self | melee defence buff |
| Whip of Agony | `wh2_twa03_weapon_abilities_whip_of_agony` | in-melee self | enemy melee debuff (hex) |
| Whip of Misery | `wh2_main_spell_bound_whip_of_agony` | in-melee self | enemy melee debuff (hex) |
| Whiplash! | `wh2_dlc14_lord_abilities_whiplash` | in-melee self | melee combat buff (attack / weapon strength) |
| Whispering Mist | `wh3_dlc29_hero_abilities_whispering_mist` | in-melee self | enemy melee debuff (hex, area) |
| Whispering Skull | `wh3_dlc29_item_abilities_whispering_skull` | in-melee self | spellcasting buff |
| Wild Abandon | `wh3_dlc26_lord_abilities_wild_abandon` | in-melee self | melee combat buff (attack / weapon strength) |
| Willing Prey | `wh3_main_lord_abilities_willing_prey` | in-melee self | enemy melee debuff (hex) |
| Winds of Change | `wh3_main_daemon_body_abilities_winds_of_change` | in-melee self | spellcasting buff |
| Word of Change | `wh3_main_daemon_head_abilities_word_of_change` | in-melee self | enemy melee debuff (hex) |
| Word of Pain | `wh2_dlc10_spell_bound_word_of_pain` | in-melee self | enemy melee debuff (hex) |
| Word of Pain | `wh3_dlc27_spell_dark_magic_word_of_pain_bound_1use` | in-melee self | enemy melee debuff (hex) |
| Woven Mist | `wh_dlc05_unit_abilities_woven_mist` | in-melee self | missile resistance / defence buff |
| Wrath of the Storm | `wh3_main_lord_abilities_wrath_of_the_storm` | in-melee self | melee combat buff (area, allies in range) |
| Wrathful Reaper | `wh3_main_lord_abilities_wrathful_reaper` | in-melee self | melee combat buff (attack / weapon strength) |
| Wristbands of Black Gold | `wh3_dlc29_item_abilities_wristbands_of_black_gold` | in-melee self | melee combat buff (attack / weapon strength) |
| You're Next! | `wh2_dlc15_lord_abilities_youre_next` | in-melee self | enemy melee debuff (hex) |

## Appendix B — AUTO-EXCLUDE (all rows, with reason)

All 325 rows, sorted by reason then ability name.

| Ability | Key | Reason | Notes |
|---|---|---|---|
| A Joyous Deliquescence | `wh3_dlc27_army_abilities_eternal_dance_tempo_3_denial_of_death` | army-bar ability (standing rule 10) | cd 90s · 24s · friend · ×2 uses · wind-up 1s · army |
| Ancestral Rune of Valaya | `wh2_dlc17_army_abilities_ancestral_rune_of_valaya` | army-bar ability (standing rule 10) | cd 120s · 24s · ground · ×1 uses · wind-up 5s · army |
| Ancestral Warriors | `wh3_main_army_abilities_ancestral_warriors` | army-bar ability (standing rule 10) | cd 120s · 10s · friend/self · ×1 uses · wind-up 5s · army |
| Apotheosis | `wh3_dlc27_army_high_magic_apotheosis` | army-bar ability (standing rule 10) | cd 29s · 10s · friend · ×3 uses · wind-up 1s · army |
| Arcane Surge | `wh3_main_army_abilities_arcane_surge` | army-bar ability (standing rule 10) | cd 60s · 14s · friend · army |
| Beasts of Itzl | `wh2_dlc13_army_abilities_beasts_of_itzl` | army-bar ability (standing rule 10) | cd 120s · 10s · enemy ground · ×3 uses · wind-up 5s · army |
| Beasts of Itzl | `wh2_dlc13_army_abilities_beasts_of_itzl_upgraded` | army-bar ability (standing rule 10) | cd 90s · 10s · enemy ground · ×5 uses · wind-up 5s · army |
| Blood & Fireborn | `wh3_dlc23_lord_abilities_blood_and_fireborn` | army-bar ability (standing rule 10) | cd 120s · 7s · friend/self · ×1 uses · army |
| Blood God's Shackles | `wh3_dlc26_army_abilities_blood_gods_shackles` | army-bar ability (standing rule 10) | cd 120s · 34s · enemy unit · ×1 uses · army · questionnaire §2 #449 |
| Blood God's Shackles Upgraded | `wh3_dlc26_army_abilities_blood_gods_shackles_upgraded` | army-bar ability (standing rule 10) | cd 120s · 34s · enemy unit · ×2 uses · army · questionnaire §2 #449 |
| Call of the Wild | `wh3_dlc25_army_abilities_call_of_the_wild` | army-bar ability (standing rule 10) | cd 120s · 1s · friend/self · ×1 uses · wind-up 5s · army |
| Call the Miners | `wh3_dlc25_army_abilities_summon_miners` | army-bar ability (standing rule 10) | cd 45s · 1s · enemy ground · ×2 uses · wind-up 5s · army |
| Call to Ceithin-Har | `wh2_dlc16_army_abilities_call_to_ceithin_har` | army-bar ability (standing rule 10) | cd 120s · -1s · friend/self · ×1 uses · army |
| Channelling Spire | `wh2_main_army_abilities_channeling_spire` | army-bar ability (standing rule 10) | cd 60s · -1s · ground · ×3 uses · wind-up 1s · army |
| Clanrats Below | `wh3_dlc29_endgame_crisis_the_vermintide_the_menace_below_hidden` | army-bar ability (standing rule 10) | cd 30s · 1s · enemy ground · ×1 uses · army |
| Curse of the Slug | `wh3_main_army_abilities_curse_of_the_slug` | army-bar ability (standing rule 10) | cd 60s · 20s · enemy unit · army |
| Cut da Chainz | `wh3_dlc26_army_abilities_cut_da_chains` | army-bar ability (standing rule 10) | cd 120s · 1s · friend/self · ×3 uses · army |
| Dark Conduit | `wh2_main_army_abilities_dark_conduit` | army-bar ability (standing rule 10) | cd 120s · 27s · friend · ×3 uses · wind-up 5s · army · questionnaire §2 #404 |
| Dismember | `wh3_main_prisoners_dismember` | army-bar ability (standing rule 10) | cd 60s · 14s · enemy unit · army |
| Eagle Sanctuary | `wh2_main_army_abilities_eagle_sanctuary` | army-bar ability (standing rule 10) | cd 120s · 1s · friend/self · ×3 uses · wind-up 5s · army |
| Engineer's Gyrocopter Bomb | `wh3_dlc25_army_abilities_gyrocopter_bomb` | army-bar ability (standing rule 10) | cd 0.1s · 0.1s · self · army |
| Fascination | `wh3_main_army_abilities_fascination` | army-bar ability (standing rule 10) | cd 120s · 14s · enemy unit · wind-up 5s · army · questionnaire §2 #470 |
| Fecundity | `wh3_main_army_abilities_fecundity` | army-bar ability (standing rule 10) | cd 90s · 12s · friend · army |
| Feral Cold Ones | `wh2_main_army_abilities_feral_cold_ones` | army-bar ability (standing rule 10) | cd 120s · 1s · enemy ground · ×3 uses · wind-up 5s · army |
| Feral Cold Ones | `wh2_main_army_abilities_feral_cold_ones_qb_scripted` | army-bar ability (standing rule 10) | cd 80s · 1s · enemy ground · ×3 uses · wind-up 5s · army |
| Frozen on the Pyre | `wh3_dlc27_army_abilities_eternal_dance_tempo_3_submission_to_the_prince` | army-bar ability (standing rule 10) | cd 90s · 36s · enemy unit · ×3 uses · wind-up 1s · army · questionnaire §2 #477 |
| Geomantic Nexus | `wh2_main_army_abilities_geomantic_nexus` | army-bar ability (standing rule 10) | cd 90s · 1s · friend/self · ×2 uses · wind-up 3s · army |
| Gluttony | `wh3_main_army_abilities_gluttony` | army-bar ability (standing rule 10) | cd 90s · 20s · friend · ×1 uses · army |
| Hand of Glory | `wh3_dlc27_army_high_magic_hand_of_glory` | army-bar ability (standing rule 10) | cd 28s · 29s · friend · ×3 uses · wind-up 1s · army |
| Holy Stela | `wh2_main_army_abilities_holy_stela` | army-bar ability (standing rule 10) | cd 60s · 57s · ground · ×3 uses · army |
| Iron Reinforcements | `wh3_cp1_army_abilities_tiger_warrior_reinforcements` | army-bar ability (standing rule 10) | cd 120s · 10s · friend/self · ×1 uses · wind-up 5s · army |
| Launch Gyrocopters | `wh3_dlc25_army_abilities_launch_gyrocopters` | army-bar ability (standing rule 10) | cd 120s · 10s · ground · ×1 uses · wind-up 5s · army |
| Lure of the Pale Queen | `wh2_main_army_abilities_lure_of_the_pale_queen` | army-bar ability (standing rule 10) | cd 90s · 11s · ground · ×3 uses · army |
| Mislead | `wh2_dlc14_final_battle_ability_summon_snikch` | army-bar ability (standing rule 10) | cd 0s · 1s · enemy ground · ×3 uses · wind-up 1s · army |
| Moulder Clanstone | `wh2_main_army_abilities_moulder_clanstone` | army-bar ability (standing rule 10) | cd 120s · 22s · ground · ×3 uses · army |
| Murderous Libations | `wh3_dlc27_army_abilities_eternal_dance_tempo_3_nectar_of_the_daemonette` | army-bar ability (standing rule 10) | cd 120s · 36s · friend · ×2 uses · wind-up 1s · army · questionnaire §2 #408 |
| Narcissism | `wh3_main_army_abilities_narcissism` | army-bar ability (standing rule 10) | cd 90s · 16s · enemy unit · wind-up 3s · army |
| Oblast Outriders | `wh3_main_abilities_call_horse_archers` | army-bar ability (standing rule 10) | cd 120s · 5s · ground · ×2 uses · wind-up 2s · army |
| ph | `wh2_main_army_abilities_carnosaur_qb_scripted` | army-bar ability (standing rule 10) | cd 80s · 1s · enemy ground · ×3 uses · wind-up 5s · army |
| ph | `wh2_main_army_abilities_stegadon_qb_scripted` | army-bar ability (standing rule 10) | cd 80s · 1s · enemy ground · ×3 uses · wind-up 5s · army |
| Plague Monks Below | `wh3_dlc29_endgame_crisis_the_vermintide_pestilent_birth_hidden` | army-bar ability (standing rule 10) | cd 60s · 1s · enemy ground · ×1 uses · army |
| Protection of Quetzl | `wh2_dlc13_army_abilities_protection_of_quetzl` | army-bar ability (standing rule 10) | cd 120s · 35s · friend · ×3 uses · wind-up 5s · army · questionnaire §2 #410 |
| Protection of Quetzl | `wh2_dlc13_army_abilities_protection_of_quetzl_upgraded` | army-bar ability (standing rule 10) | cd 90s · 55s · friend · ×3 uses · wind-up 5s · army · questionnaire §2 #410 |
| Rat Ogres Below | `wh3_dlc29_endgame_crisis_the_vermintide_beast_pack_hidden` | army-bar ability (standing rule 10) | cd 45s · 1s · enemy ground · ×1 uses · army |
| Realm of Souls Ushabti | `wh2_dlc09_army_abilities_realm_of_souls_ushabti` | army-bar ability (standing rule 10) | cd 0s · 1s · enemy ground · wind-up 10s · army |
| Relentless Rage | `wh3_main_army_abilities_relentless_rage` | army-bar ability (standing rule 10) | cd 90s · 20s · friend · army · questionnaire §2 #377 |
| Rot, Glorious Rot | `wh3_main_army_abilities_rot_glorious_rot` | army-bar ability (standing rule 10) | cd 120s · 25s · enemy unit · army |
| Roused to Wrath | `wh2_dlc16_lord_abilities_roused_to_wrath_3` | army-bar ability (standing rule 10) | cd 90s · 1s · friend/self · ×3 uses · wind-up 1s · army |
| Ryze: Crypt Horrors | `wh3_dlc29_army_abilities_ryze_the_grave_call_crypt_horrors` | army-bar ability (standing rule 10) | cd 0s · 1s · enemy ground · ×2 uses · wind-up 10s · army |
| Ryze: Grave Guard | `wh3_dlc29_army_abilities_ryze_the_grave_call_grave_guard` | army-bar ability (standing rule 10) | cd 0s · 1s · enemy ground · ×2 uses · wind-up 10s · army |
| Ryze: Grave Guard Upgraded | `wh3_dlc29_army_abilities_ryze_the_grave_call_grave_guard_endless` | army-bar ability (standing rule 10) | cd 0s · 1s · enemy ground · ×2 uses · wind-up 10s · army |
| Ryze: Khemrian Warsphinx | `wh3_dlc29_army_abilities_ryze_the_grave_call_khemrian_warsphinx` | army-bar ability (standing rule 10) | cd 0s · 1s · enemy ground · ×1 uses · wind-up 10s · army |
| Ryze: Khemric Titan | `wh3_dlc29_army_abilities_ryze_the_grave_call_khemric_titan` | army-bar ability (standing rule 10) | cd 0s · 1s · enemy ground · ×1 uses · wind-up 10s · army |
| Ryze: Khemric Titan Upgraded | `wh3_dlc29_army_abilities_ryze_the_grave_call_khemric_titan_endless` | army-bar ability (standing rule 10) | cd 0s · 1s · enemy ground · ×1 uses · wind-up 10s · army |
| Ryze: Mournguls | `wh3_dlc29_army_abilities_ryze_the_grave_call_mournguls` | army-bar ability (standing rule 10) | cd 0s · 1s · enemy ground · ×2 uses · wind-up 10s · army |
| Ryze: Necrofex Colossus | `wh3_dlc29_army_abilities_ryze_the_grave_call_necrofex_colossus` | army-bar ability (standing rule 10) | cd 0s · 1s · enemy ground · ×1 uses · wind-up 10s · army |
| Ryze: Nehekharan Warriors | `wh3_dlc29_army_abilities_ryze_the_grave_call_nehekharan_warriors` | army-bar ability (standing rule 10) | cd 0s · 1s · enemy ground · ×3 uses · wind-up 10s · army |
| Ryze: Rotting Prometheans (Gunnery Mob) | `wh3_dlc29_army_abilities_ryze_the_grave_call_rotting_prometheans_gunnery_mob` | army-bar ability (standing rule 10) | cd 0s · 1s · enemy ground · ×2 uses · wind-up 10s · army |
| Ryze: Rotting Prometheans (Gunnery Mob) Upgraded | `wh3_dlc29_army_abilities_ryze_the_grave_call_rotting_prometheans_gunnery_mob_endless` | army-bar ability (standing rule 10) | cd 0s · 1s · enemy ground · ×2 uses · wind-up 10s · army |
| Ryze: Spirit Host | `wh3_dlc29_army_abilities_ryze_the_grave_call_spirit_host` | army-bar ability (standing rule 10) | cd 0s · 1s · enemy ground · ×3 uses · wind-up 10s · army |
| Ryze: Terrorgheist | `wh3_dlc29_army_abilities_ryze_the_grave_call_terrorgheist` | army-bar ability (standing rule 10) | cd 0s · 1s · enemy ground · ×1 uses · wind-up 10s · army |
| Ryze: Ushabti | `wh3_dlc29_army_abilities_ryze_the_grave_call_ushabti` | army-bar ability (standing rule 10) | cd 0s · 1s · enemy ground · ×2 uses · wind-up 10s · army |
| Ryze: Zombie Pirate Gunnery Mob (Bombers) | `wh3_dlc29_army_abilities_ryze_the_grave_call_zombie_pirate_gunnery_mob_bombers` | army-bar ability (standing rule 10) | cd 0s · 1s · enemy ground · ×3 uses · wind-up 10s · army |
| Scruten Clanstone | `wh3_dlc29_army_abilities_scruten_clanstone` | army-bar ability (standing rule 10) | cd 120s · 48s · ground · ×3 uses · army |
| Shamanistic Ritual (Death) | `wh3_dlc27_army_abilities_sayl_manipulations_spawn_shaman_death` | army-bar ability (standing rule 10) | cd 90s · 1s · friend/self · ×1 uses · wind-up 3s · army |
| Shamanistic Ritual (Fire) | `wh3_dlc27_army_abilities_sayl_manipulations_spawn_shaman_fire` | army-bar ability (standing rule 10) | cd 90s · 1s · friend/self · ×1 uses · wind-up 3s · army |
| Shamanistic Ritual (Metal) | `wh3_dlc27_army_abilities_sayl_manipulations_spawn_shaman_metal` | army-bar ability (standing rule 10) | cd 90s · 1s · friend/self · ×1 uses · wind-up 3s · army |
| Shield of the Old Ones | `wh2_dlc13_final_battle_abilities_shield_of_the_old_ones` | army-bar ability (standing rule 10) | cd 90s · 180s · ground · army |
| Ships of the Line | `wh3_dlc27_army_abilities_ships_of_the_line` | army-bar ability (standing rule 10) | cd 60s · 10s · friend/self · ×3 uses · wind-up 1s · army |
| Skryre Clanstone | `wh2_main_army_abilities_skryre_clanstone` | army-bar ability (standing rule 10) | cd 120s · 52s · ground · ×3 uses · army |
| Spirit of Grungni | `wh3_dlc25_army_abilities_spirit_of_grungni` | army-bar ability (standing rule 10) | cd 120s · 1s · ground · ×1 uses · wind-up 5s · army |
| Stormvermin Below | `wh3_dlc29_endgame_crisis_the_vermintide_stormvermin_menace_below_hidden` | army-bar ability (standing rule 10) | cd 75s · 1s · enemy ground · ×1 uses · army |
| Summon Plague Drones | `wh3_dlc29_army_abilities_rotborne_summon_plague_drones` | army-bar ability (standing rule 10) | cd 120s · 10s · ground · ×1 uses · wind-up 5s · army |
| Summon Plague Drones (Death's heads) | `wh3_dlc29_army_abilities_rotborne_summon_plague_drones_1` | army-bar ability (standing rule 10) | cd 120s · 10s · ground · ×1 uses · wind-up 5s · army |
| Summon the Sentinels | `wh2_dlc15_army_abilities_summon_the_sentinels` | army-bar ability (standing rule 10) | cd 120s · 5s · ground · ×2 uses · wind-up 2s · army |
| Summon the Sentinels Upgraded | `wh2_dlc15_army_abilities_summon_the_sentinels_upgraded` | army-bar ability (standing rule 10) | cd 120s · 5s · ground · ×4 uses · wind-up 2s · army |
| Summoned from Beyond | `wh3_main_army_abilities_summoned_from_beyond_daemon_prince` | army-bar ability (standing rule 10) | cd 90s · 10s · enemy ground · ×10 uses · wind-up 5s · army |
| Summoned from Beyond | `wh3_main_army_abilities_summoned_from_beyond_khorne` | army-bar ability (standing rule 10) | cd 120s · 10s · enemy ground · ×2 uses · wind-up 5s · army |
| Summoned from Beyond | `wh3_main_army_abilities_summoned_from_beyond_nurgle` | army-bar ability (standing rule 10) | cd 120s · 10s · enemy ground · ×2 uses · wind-up 5s · army |
| Summoned from Beyond | `wh3_main_army_abilities_summoned_from_beyond_slaanesh` | army-bar ability (standing rule 10) | cd 120s · 10s · enemy ground · ×2 uses · wind-up 5s · army |
| Summoned from Beyond | `wh3_main_army_abilities_summoned_from_beyond_tzeentch` | army-bar ability (standing rule 10) | cd 120s · 10s · enemy ground · ×2 uses · wind-up 5s · army |
| Sweet Sorrow | `wh3_main_army_abilities_sweet_sorrow` | army-bar ability (standing rule 10) | cd 60s · 15s · friend · wind-up 1s · army · questionnaire §2 #402 |
| Temple of Mists | `wh2_main_army_abilities_temple_of_mists` | army-bar ability (standing rule 10) | cd 120s · 38s · ground · ×3 uses · army |
| The Bitter End | `wh3_dlc27_army_abilities_eternal_dance_tempo_3_poisonous_aroma` | army-bar ability (standing rule 10) | cd 120s · 10s · enemy unit · ×2 uses · wind-up 1s · army |
| The Bitterness of Winter | `wh3_main_army_abilities_the_bitterness_of_winter` | army-bar ability (standing rule 10) | cd 90s · 16s · enemy ground · ×3 uses · army |
| The Effulgent Incense | `wh3_dlc27_army_abilities_eternal_dance_tempo_3_path_of_indulgence` | army-bar ability (standing rule 10) | cd 120s · 24s · ground · ×1 uses · wind-up 3s · army |
| The Land Awakened | `wh3_main_army_abilities_the_land_awakened` | army-bar ability (standing rule 10) | cd 120s · 1s · enemy ground · ×1 uses · wind-up 5s · army · questionnaire §2 #486 |
| The Menace Below | `wh2_dlc29_army_abilities_the_menace_below_qb` | army-bar ability (standing rule 10) | cd 45s · 1s · enemy ground · ×5 uses · wind-up 5s · army |
| The Menace Below | `wh2_main_army_abilities_the_menace_below` | army-bar ability (standing rule 10) | cd 45s · 1s · enemy ground · ×1 uses · wind-up 5s · army |
| The Menace Below (Stormvermin) | `wh3_dlc29_army_abilities_stormvermin_menace_below` | army-bar ability (standing rule 10) | cd 60s · 1s · enemy ground · ×2 uses · wind-up 5s · army |
| Titanic Exultation | `wh3_dlc27_army_abilities_decadence_in_praise_of_sla_i` | army-bar ability (standing rule 10) | cd 180s · 10s · enemy unit · ×1 uses · wind-up 3s · army |
| Tzcatli's Sanctum | `wh2_dlc17_army_abilities_tzcatlis_sanctum` | army-bar ability (standing rule 10) | cd 60s · 5s · enemy ground · ×3 uses · wind-up 3s · army |
| Unleash | `wh3_dlc29_army_abilities_unleash` | army-bar ability (standing rule 10) | cd 60s · 1s · enemy ground · ×1 uses · wind-up 5s · army |
| Unleash the Winds | `wh2_dlc15_army_abilities_unleash_the_winds` | army-bar ability (standing rule 10) | cd 60s · 15s · self · army |
| Vortical Enrichment | `wh2_main_army_abilities_vortic_enrichment` | army-bar ability (standing rule 10) | cd 30s · 5s · ground · army |
| War Supplies | `wh3_dlc27_army_abilities_war_supplies` | army-bar ability (standing rule 10) | cd 60s · 10s · friend/self · ×3 uses · wind-up 1s · army |
| Warpbomb | `wh2_main_army_abilities_warpbomb` | army-bar ability (standing rule 10) | cd 60s · 16s · friend · ×1 uses · wind-up 1s · army · questionnaire §2 #413 |
| Wrath of the Bear | `wh3_main_army_abilities_wrath_of_the_bear` | army-bar ability (standing rule 10) | cd 90s · 17s · friend · ×3 uses · army · questionnaire §2 #393 |
| Ancient Chaos Frost Dragon Scale | `wh_dlc08_item_abilities_ancient_frost_wyrm_scale` | explosive / breath attack | cd 120s · 24s · enemy ground · wind-up 1s |
| Breath of the Hydra | `wh2_dlc10_quest_abilities_fiery_head` | explosive / breath attack | cd 25s · 45s · self · wind-up 2s |
| Death from Above | `wh2_dlc09_unit_abilities_death_from_above` | explosive / breath attack | cd 0.1s · 1s · self · ×1 uses |
| Drop Rocks | `wh2_dlc12_unit_abilities_drop_rocks_character` | explosive / breath attack | cd 5s · -1s · self · ×1 uses |
| Drop Rocks | `wh2_main_unit_abilities_drop_rocks` | explosive / breath attack | cd 5s · -1s · self · ×1 uses |
| Drop Rocks of Chotec | `wh2_dlc12_unit_abilities_drop_rocks_of_chotec` | explosive / breath attack | cd 5s · -1s · self · ×1 uses |
| Drop Rocks of Sundering | `wh2_dlc12_unit_abilities_drop_rocks_of_sundering` | explosive / breath attack | cd 5s · -1s · self · ×1 uses |
| Drop Sphere of Tepok | `wh2_dlc12_lord_abilities_drop_sphere_of_tepok` | explosive / breath attack | cd 5s · -1s · self · ×1 uses |
| Drop Sphere of Tepok Upgraded | `wh2_dlc12_lord_abilities_drop_sphere_of_tepok_upgraded` | explosive / breath attack | cd 5s · -1s · self · ×2 uses |
| Emberstorm | `wh2_dlc15_unit_abilities_emberstorm` | explosive / breath attack | cd 90s · 11.5s · self · ×3 uses · wind-up 1.5s |
| Eye of Rejuvenation | `wh2_dlc10_quest_abilities_regenerating_head` | explosive / breath attack | cd 15s · 25s · self · wind-up 2s |
| Fire Bombs | `wh3_dlc25_unit_abilities_gyrobomber_fire_bomb` | explosive / breath attack | cd 3s · 1s · self · ×3 uses |
| Fire Bombs | `wh3_dlc25_unit_abilities_thunderbarge_fire_bomb` | explosive / breath attack | cd 3s · 1s · self · ×3 uses |
| Gyrobomber Bomb | `wh_main_unit_abilities_gyrobomber_bomb` | explosive / breath attack | cd 0.1s · 0.1s · self · ×11 uses |
| Gyrocopter Bomb | `wh_main_unit_abilities_gyrocopter_bomb` | explosive / breath attack | cd 0.1s · 0.1s · self · ×2 uses |
| Gyrocopter Bomb (Trollhammer) | `wh3_dlc25_unit_abilities_gyrocopter_bomb_anti_large` | explosive / breath attack | cd 0.1s · 0.1s · self · ×2 uses |
| Howling Winter | `wh_dlc08_quest_abilities_howling_winter` | explosive / breath attack | cd 3s · 27s · enemy ground · wind-up 1s |
| Land Mine | `wh3_dlc25_unit_abilities_marienburg_land_mines` | explosive / breath attack | cd 10s · -1s · self · ×3 uses |
| Moon Flare | `wh3_dlc24_unit_abilities_moon_flare` | explosive / breath attack | cd 90s · 11.5s · self · ×3 uses · wind-up 1.5s |
| Nan-Gau Grenades | `wh3_dlc24_unit_abilities_nan_gau_grenades` | explosive / breath attack | cd 60s · 10s · self · ×2 uses |
| Searing Torrent | `wh3_twa07_unit_abilities_searing_torrent` | explosive / breath attack | cd 60s · -1s · self · ×5 uses |
| Sky-Junk Bomb | `wh3_main_unit_abilities_sky_junk_bomb` | explosive / breath attack | cd 30s · 1s · self · ×3 uses · wind-up 1s |
| Skyhammer Bomb | `wh_dlc06_unit_abilities_skyhammer_bomb` | explosive / breath attack | cd 0.1s · 1s · self · ×5 uses |
| Skyhammer Fire Bomb | `wh_dlc06_unit_abilities_skyhammer_fire_bomb` | explosive / breath attack | cd 0.1s · 1s · self · ×5 uses |
| Slann Gold | `wh2_dlc11_item_abilities_slann_gold` | explosive / breath attack | cd 120s · 55s · enemy unit |
| Song of Enthrallment | `wh2_dlc11_lord_abilities_song_of_enthrallment` | explosive / breath attack | cd 90s · 22s · self |
| Undeath from Above | `wh3_dlc29_unit_abilities_undeath_from_above` | explosive / breath attack | cd 0.1s · 1s · self · ×1 uses |
| Unidentified Hydra Head | `wh2_dlc10_quest_abilities_unidentified_hydra_head` | explosive / breath attack | cd 135s · 35s · self · ×3 uses · wind-up 2s |
| Wake of Fire | `wh2_main_unit_abilities_wake_of_fire` | explosive / breath attack | cd 0.1s · 0.1s · self · ×10 uses |
| Arrow of Kurnous | `wh_dlc05_hero_abilities_arrow_of_kurnous` | explosive projectile | cd 90s · -1s · enemy unit · ×3 uses |
| Bellow of Endless Fury | `wh3_main_lord_abilities_bellow_of_endless_fury` | explosive projectile | cd 60s · -1s · enemy unit · ×3 uses · wind-up 1.2s |
| Bellow of Fury | `wh3_main_lord_abilities_bellow_of_fury` | explosive projectile | cd 60s · -1s · enemy unit · ×3 uses · wind-up 1s |
| Big Boom | `wh2_dlc13_character_abilities_big_boom` | explosive projectile | cd 120s · -1s · enemy unit · ×3 uses · wind-up 2.2s |
| Bilespurt | `wh3_dlc29_hero_active_bilespurter` | explosive projectile | cd 60s · -1s · enemy unit · ×3 uses · wind-up 1.3s |
| Blast | `wh2_dlc10_item_bound_blast` | explosive projectile | cd 60s · -1s · enemy unit · ×1 uses · bound |
| Bolt Storm | `wh3_main_weapon_abilities_nuku_chos_crossbow` | explosive projectile | cd 90s · -1s · enemy unit · wind-up 1s |
| Bomb-Throw | `wh2_dlc11_hero_abilities_bomb_throw` | explosive projectile | cd 60s · -1s · enemy unit · ×4 uses · wind-up 0.4s |
| Bow of the Seafarer | `wh2_main_weapon_abilities_bow_of_the_seafarer` | explosive projectile | cd 90s · -1s · enemy unit · ×3 uses · wind-up 1s |
| Cackle Fruit | `wh2_dlc11_character_abilities_cackle_fruit` | explosive projectile | cd 90s · -1s · enemy unit · ×3 uses · wind-up 0.4s |
| Cinderblast Cluster Bomb | `wh3_dlc25_lord_abilities_cinderblast_cluster_bomb` | explosive projectile | cd 120s · -1s · enemy unit · ×3 uses · wind-up 3s |
| Cinderblast Shell | `wh2_dlc17_hero_abilities_cinderblast_shell` | explosive projectile | cd 90s · -1s · enemy unit · ×3 uses · wind-up 1s |
| Copious Vomit | `wh_dlc08_lord_abilities_copious_vomit` | explosive projectile | cd 60s · -1s · enemy unit · ×3 uses |
| Coruscating Blast | `wh3_dlc25_unit_abilities_coruscating_blast` | explosive projectile | cd 120s · -1s · enemy unit · ×3 uses · wind-up 1.3s |
| Cracklebomb | `wh2_dlc14_character_abilities_cracklebomb` | explosive projectile | cd 90s · -1s · enemy unit · ×3 uses · wind-up 0.8s |
| Crippling Throw | `wh3_main_character_abilities_crippling_throw` | explosive projectile | cd 90s · -1s · enemy unit · ×3 uses · wind-up 3s |
| Dark Fire of Chaos | `wh2_main_unit_abilities_dark_fire_of_chaos` | explosive projectile | cd 60s · -1s · enemy unit · ×3 uses · wind-up 1.1s |
| Death Shriek | `wh2_main_unit_abilities_death_shriek` | explosive projectile | cd 60s · -1s · enemy unit · ×3 uses · wind-up 0.6s |
| Doomrocket | `wh2_main_hero_abilities_doomrocket` | explosive projectile | cd 90s · -1s · enemy unit · ×1 uses · wind-up 1s |
| Elemental Breath | `wh3_main_unit_abilities_elemental_breath` | explosive projectile | cd 60s · -1s · enemy unit · ×3 uses · wind-up 2.7s |
| Experimental Explosive | `wh3_dlc25_weapon_abilities_experimental_explosive` | explosive projectile | cd 120s · -1s · enemy unit · ×2 uses · wind-up 0.8s |
| Fiery Breath | `wh2_main_unit_abilities_fiery_breath` | explosive projectile | cd 60s · -1s · enemy unit · ×3 uses · wind-up 1s |
| Fire Breath | `wh3_main_character_abilities_fire_breath` | explosive projectile | cd 60s · -1s · enemy unit · ×3 uses · wind-up 1.9s |
| Flaming Breath | `wh3_dlc23_unit_abilities_flaming_breath` | explosive projectile | cd 90s · -1s · enemy unit · ×3 uses · wind-up 1s |
| Flaming Breath | `wh3_dlc27_unit_abilities_flaming_breath` | explosive projectile | cd 90s · -1s · enemy unit · ×3 uses · wind-up 1s |
| Frost Breath | `wh2_dlc10_unit_abilities_frost_breath` | explosive projectile | cd 60s · -1s · enemy unit · ×3 uses · wind-up 1s |
| Frost Breath | `wh2_dlc10_unit_abilities_frost_wyrm_breath` | explosive projectile | cd 60s · -1s · enemy unit · ×3 uses · wind-up 1.1s |
| Gordinar's Dragon Breath | `wh2_dlc15_unit_abilities_sun_dragon_breath_imrik` | explosive projectile | cd 60s · -1s · enemy unit · ×3 uses · wind-up 1.3s |
| Hunting Spear | `wh_dlc03_weapon_abilities_hunting_spear` | explosive projectile | cd 120s · -1s · enemy unit |
| Ice Breath | `wh3_dlc24_unit_abilities_ice_breath` | explosive projectile | cd 60s · -1s · enemy unit · ×3 uses · wind-up 1.3s |
| Ice Shard | `wh3_main_character_abilities_ice_shard` | explosive projectile | cd 90s · -1s · enemy unit · ×3 uses · wind-up 3s |
| Lamentation of Despairs | `wh_dlc05_lord_abilities_lamentation_of_despair` | explosive projectile | cd 90s · -1s · enemy unit · wind-up 1s |
| Lamentation of Despairs (Empowered) | `wh3_dlc29_lord_abilities_lamentation_of_despair_upgraded` | explosive projectile | cd 90s · -1s · enemy unit · wind-up 1s |
| Master Rune of Flight | `wh2_dlc17_rune_abilities_master_rune_of_flight` | explosive projectile | cd 120s · -1s · enemy unit |
| Moon Dragon's Breath | `wh2_main_unit_abilities_moon_dragons_breath` | explosive projectile | cd 60s · -1s · enemy unit · ×3 uses · wind-up 1.3s |
| Noxious Breath | `wh2_main_unit_abilities_noxious_breath` | explosive projectile | cd 60s · -1s · enemy unit · ×3 uses · wind-up 1.3s |
| Pestilent Torrent | `wh3_dlc29_lord_active_pestilent_torrent` | explosive projectile | cd 90s · -1s · enemy unit · ×3 uses · wind-up 1.3s |
| Pestilential Breath | `wh2_main_unit_abilities_pestilential_breath` | explosive projectile | cd 60s · -1s · enemy unit · ×3 uses · wind-up 1.3s |
| Pyromaniac | `wh2_dlc11_character_abilities_pyromaniac` | explosive projectile | cd 90s · -1s · enemy unit · ×3 uses · wind-up 0.4s |
| Reaver Bow | `wh2_main_weapon_bound_reaver_bow` | explosive projectile | cd 90s · -1s · enemy unit · ×3 uses · wind-up 1s · bound |
| Shackolot's Noxious Breath | `wh2_dlc15_unit_abilities_noxious_breath_imrik` | explosive projectile | cd 60s · -1s · enemy unit · ×3 uses · wind-up 1.3s |
| Skarsnik's Prodder | `wh_dlc06_weapon_abilities_skarsniks_prodder` | explosive projectile | cd 120s · -1s · enemy unit · ×2 uses · wind-up 3s |
| Soporific Breath | `wh2_main_unit_abilities_soporific_breath` | explosive projectile | cd 60s · -1s · enemy unit · ×3 uses · wind-up 1.3s |
| Star Dragon's Breath | `wh2_main_unit_abilities_star_dragons_breath` | explosive projectile | cd 60s · -1s · enemy unit · ×3 uses · wind-up 1.3s |
| Storm Daemon | `wh2_dlc12_weapon_abilities_storm_daemon` | explosive projectile | cd 120s · -1s · enemy unit · ×2 uses · wind-up 5s |
| Sun Dragon's Breath | `wh2_main_unit_abilities_sun_dragons_breath` | explosive projectile | cd 60s · -1s · enemy unit · ×3 uses · wind-up 1.3s |
| The Amber Spear | `wh_dlc03_spell_bound_the_amber_spear` | explosive projectile | cd 90s · -1s · enemy unit · ×3 uses · bound |
| The Moonbow | `wh2_dlc10_weapon_abilities_the_moonbow` | explosive projectile | cd 120s · -1s · enemy unit · ×2 uses · wind-up 3s |
| The Venom Staff | `wh2_dlc09_weapon_abilities_venom_staff` | explosive projectile | cd 30s · -1s · enemy unit · ×4 uses · wind-up 1s |
| Unspeakable Foulness | `wh3_dlc25_unit_abilities_unspeakable_foulness` | explosive projectile | cd 60s · -1s · enemy unit · ×3 uses · wind-up 1.3s |
| Volley of Dark Arrows | `wh2_main_character_abilities_volley_of_dark_arrows` | explosive projectile | cd 90s · -1s · enemy unit · ×3 uses · wind-up 1s |
| Volley of High Arrows | `wh2_main_character_abilities_volley_of_high_arrows` | explosive projectile | cd 90s · -1s · enemy unit · ×3 uses · wind-up 1s |
| Ballistics Calibration | `wh_main_hero_abilities_ballistics_calibration` | ground-target-only | cd 90s · 22s · ground |
| Curse of Djaf | `wh2_dlc09_character_abilities_curse_of_djaf` | ground-target-only | cd 0s · 13s · enemy ground · ×1 uses · questionnaire §2 #480 |
| Dance of Despair | `wh3_dlc20_cataclysm_bound_dance_of_despair` | ground-target-only | cd 120s · 45s · enemy ground · ×1 uses · wind-up 5s · bound · questionnaire §2 #484 |
| Dance of Despair | `wh3_dlc27_cataclysm_bound_dance_of_despair` | ground-target-only | cd 120s · 45s · enemy ground · ×3 uses · wind-up 5s · bound · questionnaire §2 #484 |
| Master of Mists | `wh3_dlc27_character_abilities_master_of_mists` | ground-target-only | cd 120s · 58s · ground · ×2 uses |
| Master of Mists | `wh3_dlc27_character_abilities_master_of_mists_custom` | ground-target-only | cd 120s · 36s · ground · ×2 uses |
| Soulblight | `wh3_dlc29_spell_bound_soulblight` | ground-target-only | cd 45s · 20s · self · ×2 uses · wind-up 1s · questionnaire §2 #485 |
| Soulblight | `wh2_dlc10_spell_bound_soulblight` | ground-target-only | cd 90s · 20s · enemy ground · ×2 uses · wind-up 3s · bound · questionnaire §2 #485 |
| Storm of Renewal | `wh3_dlc20_cataclysm_bound_storm_of_renewal` | ground-target-only | cd 120s · 20s · ground · ×1 uses · wind-up 5s · bound |
| Storm of Renewal | `wh3_dlc27_cataclysm_bound_storm_of_renewal` | ground-target-only | cd 120s · 20s · ground · ×3 uses · wind-up 5s · bound |
| The Curse of Anraheir | `wh2_dlc16_spell_bound_the_curse_of_anraheir` | ground-target-only | cd 120s · 21s · enemy ground · ×1 uses · bound · questionnaire §2 #482 |
| The Curse of Anraheir | `wh3_main_spell_bound_the_curse_of_anraheir` | ground-target-only | cd 120s · 21s · enemy ground · ×1 uses · bound · questionnaire §2 #482 |
| The Curse of Anraheir | `wh_dlc05_spell_bound_the_curse_of_anraheir` | ground-target-only | cd 120s · 21s · enemy ground · ×1 uses · bound · questionnaire §2 #482 |
| Transmutation of Lead | `wh3_main_spell_bound_transmutation_of_lead` | ground-target-only | cd 120s · 50s · enemy ground · ×1 uses · wind-up 5s · bound · questionnaire §2 #487 |
| Banner of Hellfire | `wh3_main_banner_abilities_banner_of_hellfire` | no effect text available (unsourceable) | cd 120s · 17s · self |
| Battlefield Resupply | `wh2_dlc11_quest_battle_supply` | no effect text available (unsourceable) | cd 120s · 30s · self · ×3 uses · quest |
| Black Hammer of Hashut | `wh3_dlc23_weapon_abilities_black_hammer_of_hashut` | no effect text available (unsourceable) | cd 120s · 32s · self |
| Cloak of the Dunes | `wh2_dlc09_item_abilities_cloak_of_the_dunes` | no effect text available (unsourceable) | cd 90s · 73s · self |
| Crooked Dice | `wh3_dlc23_hero_abilities_crooked_dice` | no effect text available (unsourceable) | cd 90s · 30s · self |
| Dark Mace | `wh3_dlc23_weapon_abilities_dark_mace` | no effect text available (unsourceable) | cd 90s · 30s · self |
| Ghostly Howl | `wh3_dlc29_hero_active_ghostly_howl` | no effect text available (unsourceable) | cd 90s · 8s · enemy unit · wind-up 3s |
| Hag's Denial | `wh3_dlc24_unit_abilities_hags_denial` | no effect text available (unsourceable) | cd 120s · 44s · self · ×1 uses |
| Hunter of Champions | `wh2_dlc17_character_abilities_hunter_of_champions_upgraded` | no effect text available (unsourceable) | cd 90s · 24s · enemy unit |
| Hunter's Call | `wh2_dlc13_character_ability_hunters_call` | no effect text available (unsourceable) | cd 120s · 32s · self · ×3 uses |
| Icon of the King | `wh3_dlc29_item_abilities_icon_of_the_king` | no effect text available (unsourceable) | cd 120s · 16s · self · ×2 uses · item |
| Morikhane, the Black Armour | `wh3_dlc29_item_abilities_morikhane_the_black_armour` | no effect text available (unsourceable) | cd 120s · 14s · self · wind-up 1s · item |
| Of Warp and Ruin | `wh3_dlc29_unit_abilities_of_warp_and_ruin` | no effect text available (unsourceable) | cd 120s · 32s · self |
| Petrifying Gaze | `wh3_dlc24_unit_passive_petrifying_gaze` | no effect text available (unsourceable) | cd 120s · 32s · enemy unit · ×2 uses |
| Rock Bottom | `wh2_dlc15_unit_abilities_rock_bottom` | no effect text available (unsourceable) | cd 45s · 1s · self · wind-up 1s |
| Ruinshelter | `wh2_dlc15_unit_abilities_mimic_ruinshelter` | no effect text available (unsourceable) | cd 90s · 60s · self |
| Seduction | `wh2_dlc11_lord_abilities_seduction` | no effect text available (unsourceable) | cd 120s · 41s · self |
| Storm of Blades | `wh_dlc05_unit_abilities_storm_of_blades` | no effect text available (unsourceable) | cd 1s · -1s · self · wind-up 1s |
| Temptator | `wh3_dlc20_lord_abilities_temptator` | no effect text available (unsourceable) | cd 120s · 19s · self |
| The Crimson Blade | `wh3_dlc29_item_abilities_crimson_blade` | no effect text available (unsourceable) | cd 120s · 30s · self · item |
| The Gold Standard | `wh3_dlc25_item_abilities_the_gold_standard` | no effect text available (unsourceable) | cd 90s · 13s · friend |
| The Graven Sceptre | `wh3_dlc23_weapon_abilities_the_graven_sceptre` | no effect text available (unsourceable) | cd 120s · 24s · self |
| Transfix | `wh3_dlc29_lord_abilities_transfix` | no effect text available (unsourceable) | cd 120s · 25s · enemy unit · ×3 uses |
| Vine Dragon Scale | `wh2_dlc15_item_abilities_vine_dragon_scale` | no effect text available (unsourceable) | cd 120s · 14s · self |
| Whirling Death | `wh2_dlc16_unit_abilities_whirling_death` | no effect text available (unsourceable) | cd 1s · -1s · self · wind-up 1s |
| Ancestral Vengeance | `wh3_dlc23_item_abilities_ancestral_vengeance` | summon | cd 120s · 10s · ground · ×2 uses · wind-up 5s |
| Ancestral Warriors | `wh3_main_spell_bound_ancestral_warriors` | summon | cd 120s · 10s · friend/self · ×2 uses · wind-up 5s · bound |
| Arachnarok Eggs | `wh_dlc08_item_abilities_arachnarok_eggs` | summon | cd 60s · 1s · enemy ground · ×5 uses · questionnaire §2 #479 |
| Beast Pack | `wh2_dlc16_lord_abilities_beast_pack` | summon | cd 120s · 1s · friend/self · ×1 uses |
| Beyond the Realm | `wh2_dlc11_character_abilities_beyond_the_realm` | summon | cd 120s · 3s · friend/self · ×2 uses · wind-up 3s |
| Blacktoof's Conjuration | `wh2_dlc15_item_abilities_blacktoofs_conjuration` | summon | cd 300s · 1s · friend/self · ×1 uses |
| Burrow | `wh3_dlc27_unit_abilities_dread_maw_underground` | summon | cd 20s · 3s · self · wind-up 4s |
| Call of the Shadow Dancer | `wh2_dlc10_lord_abilities_deadly_mislead` | summon | cd 90s · 62s · ground · ×3 uses |
| Call to Ceithin-Har | `wh2_dlc16_lord_abilities_call_to_ceithin_har` | summon | cd 120s · -1s · friend/self · ×1 uses |
| Call to Gwindalor | `wh2_dlc16_lord_abilities_call_to_gwindalor` | summon | cd 120s · -1s · friend/self · ×1 uses |
| Captain Roth's Moondial | `wh2_dlc11_item_abilities_captain_roths_moondial` | summon | cd 120s · 3s · friend/self · ×2 uses · wind-up 3s |
| Children of the Forest | `wh3_dlc25_character_abilities_children_of_the_forest` | summon | cd 90s · 1s · friend/self · ×5 uses |
| Deceiving Shadows | `wh3_dlc24_lord_item_deceiving_shadows` | summon | cd 120s · 20s · ground · ×3 uses |
| Doppelgang | `wh2_dlc14_unit_abilities_doppelgang` | summon | cd 90s · 60s · friend/self · ×2 uses |
| Dreaming Cloak I | `wh2_dlc16_item_abilities_dreaming_cloak_i` | summon | cd 120s · 1s · friend/self · ×1 uses · wind-up 1s |
| Dreaming Cloak II | `wh2_dlc16_item_abilities_dreaming_cloak_ii` | summon | cd 120s · 1s · friend/self · ×1 uses · wind-up 1s |
| Dreaming Cloak III | `wh2_dlc16_item_abilities_dreaming_cloak_iii` | summon | cd 120s · 1s · friend/self · ×1 uses · wind-up 1s |
| Eye of Khorne | `wh3_dlc26_lord_abilities_eye_of_khorne` | summon | cd 120s · 10s · enemy unit · ×1 uses · questionnaire §2 #452 |
| Gate of Chaos | `wh3_main_daemon_arms_abilities_gate_of_chaos` | summon | cd 120s · 10s · ground · ×2 uses · wind-up 5s |
| Gate of Chaos Upgraded | `wh3_main_daemon_arms_abilities_gate_of_chaos_upgraded` | summon | cd 120s · 10s · ground · ×2 uses · wind-up 5s |
| Gate of Tzeentch | `wh3_main_character_abilities_gate_of_tzeentch` | summon | cd 120s · 10s · friend/self · ×1 uses · wind-up 5s |
| Ghosts of the Past | `wh2_dlc11_character_abilities_ghosts_of_the_past_0` | summon | cd 120s · 1s · friend/self · ×1 uses · wind-up 3s |
| Ghosts of the Past | `wh2_dlc11_character_abilities_ghosts_of_the_past_1` | summon | cd 120s · 1s · friend/self · ×2 uses · wind-up 3s |
| Ghosts of the Past | `wh2_dlc11_character_abilities_ghosts_of_the_past_2` | summon | cd 120s · 1s · friend/self · ×2 uses · wind-up 3s |
| Gorger Onslaught | `wh3_main_lord_abilities_gorger_onslaught` | summon | cd 60s · 1s · enemy ground · ×1 uses · wind-up 1s |
| Gorger Onslaught Upgraded | `wh3_dlc26_lord_abilities_gorger_onslaught_upgraded` | summon | cd 90s · 1s · enemy ground · ×3 uses · wind-up 1s |
| Guardian Call | `wh3_main_character_abilities_guardian_call` | summon | cd 0s · 1s · enemy ground · ×1 uses · wind-up 3s |
| Guardian Call II | `wh3_main_character_abilities_guardian_call_ii` | summon | cd 0s · 1s · enemy ground · ×1 uses · wind-up 3s |
| Guardian Call III | `wh3_main_character_abilities_guardian_call_iii` | summon | cd 0s · 1s · enemy ground · ×1 uses · wind-up 3s |
| Guardian of the Forest | `wh3_dlc25_character_abilities_guardian_of_the_forest` | summon | cd 120s · 1s · friend/self · ×1 uses |
| Horn of the Ancestors | `wh2_dlc10_item_abilities_horn_of_the_ancestors` | summon | cd 120s · 1s · friend/self · ×1 uses |
| Inventory of Hatchlings | `wh3_dlc26_character_abilities_inventory_of_hatchlings` | summon | cd 120s · 1s · enemy ground · ×3 uses |
| Inventory of Hatchlings Upgraded | `wh3_dlc26_character_abilities_inventory_of_hatchlings_upgraded` | summon | cd 60s · 1s · enemy ground · ×5 uses |
| Invocation of the Lichemaster | `wh3_dlc29_character_abilities_invocation_of_the_lichemaster` | summon | cd 90s · 3s · ground · ×1 uses |
| Invocation of the Lichemaster | `wh3_dlc29_character_abilities_invocation_of_the_lichemaster_0` | summon | cd 90s · 3s · ground · ×1 uses |
| Invocation of the Lichemaster | `wh3_dlc29_character_abilities_invocation_of_the_lichemaster_1` | summon | cd 90s · 3s · ground · ×1 uses |
| Kettle's Call | `wh3_dlc25_character_abilities_kettles_call` | summon | cd 120s · 1s · friend/self · ×2 uses · wind-up 5s |
| Koldunja's Spirit | `wh3_dlc24_hero_abilities_koldunjas_spirit` | summon | cd 120s · 1s · ground · ×1 uses · wind-up 1s |
| Lesser Raise Dead | `wh2_dlc16_spell_bound_vampires_lesser_raise_dead` | summon | cd 0s · 1s · friend/self · ×1 uses · wind-up 3s · bound |
| Locus of Transmogrification | `wh3_main_character_abilities_locus_of_transmogrification` | summon | cd 90s · 10s · friend/self · ×2 uses · wind-up 5s |
| Lord of Undeath | `wh_pro03_lord_abilities_lord_of_undeath` | summon | cd 120s · 1s · friend/self · ×1 uses |
| Lord of Undeath | `wh_pro03_lord_abilities_lord_of_undeath_0` | summon | cd 120s · 1s · friend/self · ×1 uses |
| Lord of Undeath | `wh_pro03_lord_abilities_lord_of_undeath_1` | summon | cd 120s · 1s · friend/self · ×1 uses |
| Lord of Undeath | `wh_pro03_lord_abilities_lord_of_undeath_2` | summon | cd 120s · 1s · friend/self · ×1 uses |
| Lord of Undeath | `wh_pro03_lord_abilities_lord_of_undeath_3` | summon | cd 120s · 1s · friend/self · ×1 uses |
| Lord of Undeath | `wh_pro03_lord_abilities_lord_of_undeath_4` | summon | cd 120s · 1s · friend/self · ×1 uses |
| Mask of the Merlord | `wh3_dlc27_item_abilities_mask_of_the_merlord` | summon | cd 120s · 3s · ground · ×1 uses · wind-up 5s |
| Master of Souls | `wh_dlc08_quest_abilities_master_of_souls` | summon | cd 5s · 2s · friend · ×40 uses · wind-up 1s |
| Maternal Instinct | `wh_dlc06_unit_abilities_maternal_instinct` | summon | cd 60s · 1s · enemy ground · ×5 uses · wind-up 5s |
| Mislead | `wh2_dlc10_lord_abilities_mislead` | summon | cd 90s · 62s · ground · ×3 uses |
| Nurgling Birth | `wh3_dlc29_hero_active_nurgling_birth` | summon | cd 90s · 2s · ground · ×3 uses · wind-up 1s |
| Nurgling Birth Upgraded | `wh3_dlc29_hero_active_nurgling_birth_upgraded` | summon | cd 90s · 2s · ground · ×5 uses · wind-up 1s |
| Nurgling Tide | `wh3_main_lord_abilities_nurgling_tide` | summon | cd 90s · 10s · self · ×3 uses · wind-up 3s |
| Ritual of the Beast | `wh3_dlc24_item_abilities_ritual_of_the_beast` | summon | cd 300s · 1s · friend/self · ×1 uses · item |
| Roused to Wrath | `wh2_dlc16_lord_abilities_roused_to_wrath` | summon | cd 90s · 1s · friend/self · ×1 uses · wind-up 1s |
| Roused to Wrath | `wh2_dlc16_lord_abilities_roused_to_wrath_2` | summon | cd 90s · 1s · friend/self · ×2 uses · wind-up 1s |
| Sacrilege | `wh2_dlc11_character_abilities_sacrilege` | summon | cd 120s · 3s · friend/self · ×2 uses · wind-up 3s |
| Savage Dominion | `wh2_dlc17_spell_bound_savage_dominion` | summon | cd 120s · 1s · friend/self · ×2 uses · wind-up 5s · bound |
| Savage Predators | `wh3_dlc26_hero_abilities_savage_predators` | summon | cd 120s · 1s · friend/self · ×1 uses · wind-up 5s |
| Servants of Nagash | `wh_dlc04_quest_abilities_servant_of_nagash` | summon | cd 8s · 5s · friend · ×15 uses |
| Spinning Loons | `wh_main_unit_abilities_spinning_loons` | summon | cd 30s · 12s · enemy ground · ×3 uses · questionnaire §2 #481 |
| Squig Thinkin' | `wh3_dlc26_character_abilities_squig_thinkin` | summon | cd 90s · 1s · ground · ×1 uses |
| Stave of Ruinous Corruption | `wh_dlc05_weapon_abilities_stave_of_ruinous_corruption` | summon | cd 120s · 1s · enemy ground · ×1 uses · wind-up 5s |
| Surface | `wh3_dlc27_unit_abilities_dread_maw_surface` | summon | cd 25s · 2s · self |
| Surprise Squig! | `wh3_dlc25_character_abilities_surprise_squig` | summon | cd 60s · 1s · friend/self · ×5 uses |
| Sword of Change | `wh_dlc01_weapon_abilities_sword_of_change` | summon | cd 90s · 11s · friend/self · ×1 uses · wind-up 5s |
| The Awakening | `wh3_dlc29_lord_abilities_the_awakening` | summon | cd 120s · 1s · ground · ×1 uses · wind-up 3s |
| The Loons of Eight Peaks | `wh_dlc06_unit_abilities_the_loons_of_eight_peaks` | summon | cd 30s · 12s · enemy ground · ×3 uses · questionnaire §2 #483 |
| The Tomb Blade of Arkhan | `wh2_dlc09_weapon_abilities_tomb_blade_of_arkhan` | summon | cd 120s · 1s · friend/self · ×5 uses |
| Tide of Death | `wh2_dlc16_hero_abilities_tide_of_death` | summon | cd 120s · 1s · friend/self · ×1 uses |
| Tide of Pox | `wh2_dlc16_hero_abilities_tide_of_pox` | summon | cd 120s · 1s · friend/self · ×1 uses |
| Undeath to All | `wh3_dlc29_lord_abilities_raise_legion` | summon | cd 120s · 1s · ground · ×1 uses · wind-up 3s |
| Undeath to All Upgraded | `wh3_dlc29_lord_abilities_raise_legion_upgraded` | summon | cd 120s · 1s · ground · ×1 uses · wind-up 3s |
| Wake Da Idol | `wh3_main_item_abilities_zak_aloooog` | summon | cd 300s · 1s · friend/self · ×1 uses |
| Bloodstone | `wh3_main_item_abilities_bloodstone` | summon/transform | cd 120s · 10s · ground · ×1 uses · wind-up 5s |
| Get Tha Gitz! | `wh3_dlc23_hero_abilities_get_tha_gitz!` | summon/transform | cd 120s · 5s · enemy ground · ×3 uses · wind-up 3s |
| Karanak's Howl | `wh3_pro12_hero_abilities_karanaks_howl` | summon/transform | cd 120s · 10s · friend/self · ×1 uses · wind-up 5s |
| The Portalglyph | `wh3_main_item_abilities_the_portalglyph` | summon/transform | cd 120s · 10s · enemy ground · ×1 uses · wind-up 5s |
| Acid Burps | `wh3_dlc26_unit_abilities_acid_vomit` | vortex | cd 120s · 14s · self · questionnaire §2 #1 |
| Arsebelcher | `wh3_main_character_abilities_arsebelcher` | vortex | cd 120s · 4s · self · character · questionnaire §2 #10 |
| Blood-Forged Armour | `wh2_dlc15_item_abilities_blood_forged_armour` | vortex | cd 30s · 12s · self · questionnaire §2 #23 |
| Bloodbeast | `wh2_dlc17_lord_abilities_bloodbeast` | vortex | cd 90s · 6s · self · questionnaire §2 #24 |
| Bloodstorm | `wh2_dlc14_lord_abilities_bloodstorm` | vortex | cd 60s · 9s · self · questionnaire §2 #25 |
| Burning Rage | `wh3_main_lord_abilities_burning_rage` | vortex | cd 90s · 7s · self · ×3 uses · questionnaire §2 #233 |
| Burp of Grom | `wh2_dlc15_character_abilities_burp_of_grom_0` | vortex | cd 60s · 17s · self · questionnaire §2 #29 |
| Burp of Grom | `wh2_dlc15_character_abilities_burp_of_grom_1` | vortex | cd 60s · 17s · self · questionnaire §2 #29 |
| Burp of Grom | `wh2_dlc15_character_abilities_burp_of_grom_2` | vortex | cd 60s · 17s · self · questionnaire §2 #29 |
| Daemon Flask of Ashak | `wh3_dlc23_item_abilities_daemon_flask_of_ashak` | vortex | cd 120s · 5s · self · ×1 uses · questionnaire §2 #234 |
| Deathmaster's Sigil | `wh2_dlc14_lord_abilities_deathmasters_sigil` | vortex | cd 90s · 7s · enemy unit · questionnaire §2 #419 |
| Deep Tunneling | `wh3_dlc27_unit_abilities_burrow` | vortex | cd 60s · -1s · ground · wind-up 2s |
| Emergency Vent | `wh2_dlc13_unit_abilities_emergency_vent` | vortex | cd 60s · 12s · self |
| Feaster of Souls | `wh3_dlc29_mount_abilities_feaster_of_souls` | vortex | cd 120s · 5s · self · ×3 uses · wind-up 1s |
| Flash Bomb | `wh_pro01_lord_abilities_flash_bomb` | vortex | cd 90s · 16s · enemy unit |
| Groundbreaker | `wh3_main_character_abilities_groundbreaker` | vortex | cd 90s · 3s · self · ×3 uses · questionnaire §2 #243 |
| Heaven's Flash | `wh3_main_unit_abilities_stun_bomb` | vortex | cd 90s · 31s · ground · ×1 uses |
| Hurricane of Death | `wh3_dlc25_character_abilities_hurricane_of_death` | vortex | cd 120s · 6s · self · questionnaire §2 #98 |
| Maneater Smoke Bomb | `wh3_dlc26_unit_abilities_maneater_smoke_bomb` | vortex | cd 90s · 24s · self · questionnaire §2 #115 |
| Mist Form | `wh3_dlc29_lord_abilities_mist_form` | vortex | cd 120s · 1s · ground · wind-up 2s |
| Necrotic Explosion | `wh3_main_unit_abilities_necrotic_explosion` | vortex | cd 0.1s · 10.1s · self · ×1 uses |
| Shadowstrider | `wh3_dlc29_lord_abilities_warp_step` | vortex | cd 120s · -1s · ground · wind-up 3s |
| Slime Smoothie | `wh2_dlc15_character_abilities_slimy_smoothie` | vortex | cd 30s · 14s · friend/self · ×3 uses · wind-up 1s |
| Smoke Bomb | `wh_dlc06_unit_abilities_smoke_bomb` | vortex | cd 90s · 21s · self |
| Spurting Bile-Blood | `wh3_dlc27_item_abilities_spurting_bile_blood` | vortex | cd 0s · 9s · self · ×2 uses · bound |
| Verminous Valour | `wh2_main_character_abilities_verminous_valour` | vortex | cd 60s · 17s · self · questionnaire §2 #219 |
| Violent Wind | `wh3_dlc20_unit_abilities_violent_wind` | vortex | cd 120s · 4s · self · unit · questionnaire §2 #220 |
| Whirl of Weeping Blades | `wh2_dlc14_weapon_abilities_whirl_of_weeping_blades` | vortex | cd 120s · 5s · self · questionnaire §2 #224 |
| Whirlwind of Pleasure | `wh3_dlc27_lord_abilities_whirlwind_of_pleasure` | vortex | cd 120s · 5s · self · lord · questionnaire §2 #225 |

## Appendix C — FLAG for the user (all rows, with reason)

All 347 rows. These stay `proposed` in the tracker — the only items to be asked about later.

| Ability | Key | Flag reason | Notes |
|---|---|---|---|
| 'Effagee' of da Git | `wh_dlc06_character_abilities_effagee_of_da_git` | ambiguous / mixed net effect (needs the user) | cd 120s · 13s · enemy unit · ×2 uses |
| Amber Bow | `wh2_dlc13_weapon_abilities_amber_bow` | ambiguous / mixed net effect (needs the user) | cd 120s · -1s · enemy unit · ×2 uses · wind-up 4.5s |
| Armour of the Stars | `wh2_main_item_abilities_armour_of_the_stars` | ambiguous / mixed net effect (needs the user) | cd 90s · 73s · self |
| Arrow of Aqshy | `wh2_dlc13_lord_abilities_fire_arrow` | ambiguous / mixed net effect (needs the user) | cd 90s · -1s · enemy unit · ×3 uses · wind-up 4.5s |
| Blood Statuette of Spite | `wh2_main_item_abilities_blood_statuette_of_spite` | ambiguous / mixed net effect (needs the user) | cd 60s · 14s · enemy unit · ×2 uses |
| Burning Wrath | `wh3_dlc23_spell_bound_burning_wrath` | ambiguous / mixed net effect (needs the user) | cd 30s · -1s · enemy unit · ×3 uses · wind-up 1s · bound |
| Chain Lightning | `wh3_dlc27_spell_heavens_chain_lightning_bound` | ambiguous / mixed net effect (needs the user) | cd 50s · 5s · enemy unit · ×2 uses · wind-up 5s · bound |
| Chain Lightning | `wh3_dlc27_spell_heavens_chain_lightning_bound_unit` | ambiguous / mixed net effect (needs the user) | cd 60s · 5s · enemy unit · ×1 uses · wind-up 5s · bound |
| Concealment Bombs | `wh2_main_character_abilities_concealment_bombs` | ambiguous / mixed net effect (needs the user) | cd 90s · 73s · self · ×3 uses |
| Concealment Bombs | `wh2_main_unit_abilities_concealment_bombs` | ambiguous / mixed net effect (needs the user) | cd 90s · 73s · self · ×3 uses |
| Daemonic Possession | `wh3_main_lord_abilities_daemonic_possession` | ambiguous / mixed net effect (needs the user) | cd 90s · 26s · enemy unit · ×2 uses · lord |
| Damned Pistol | `wh3_main_weapon_abilities_godkiller_pistol` | ambiguous / mixed net effect (needs the user) | cd 120s · -1s · enemy unit · ×2 uses · wind-up 2.3s |
| Darkened Mist | `wh3_dlc23_item_abilities_darkened_mist` | ambiguous / mixed net effect (needs the user) | cd 120s · 20s · enemy unit · ×3 uses · wind-up 3s |
| Dart of Doom | `wh2_dlc16_item_abilities_dart_of_doom` | ambiguous / mixed net effect (needs the user) | cd 120s · -1s · enemy unit · ×3 uses · wind-up 1s |
| Dead Eye | `wh3_dlc26_character_abilities_dead_eye` | ambiguous / mixed net effect (needs the user) | cd 120s · -1s · enemy unit · wind-up 5s |
| Dire Spirit Bear | `wh3_dlc24_lord_abilities_spirit_bear_upgrade` | ambiguous / mixed net effect (needs the user) | cd 120s · -1s · enemy unit · ×3 uses · wind-up 4s |
| Dissolving Bone | `wh3_dlc27_qb_unit_abilities_dissolving_bone` | ambiguous / mixed net effect (needs the user) | cd 60s · 2s · enemy unit |
| Eagle Quiver | `wh2_dlc16_item_abilities_eagle_quiver` | ambiguous / mixed net effect (needs the user) | cd 120s · -1s · enemy unit · ×2 uses |
| Ethrac's Brazier | `wh3_dlc29_item_active_ethracs_brazier` | ambiguous / mixed net effect (needs the user) | cd 120s · 14s · enemy unit · ×1 uses · wind-up 3s |
| Executioner | `wh2_dlc13_lord_abilities_executioner` | ambiguous / mixed net effect (needs the user) | cd 90s · -1s · enemy unit · ×3 uses · wind-up 5s |
| Fireball | `wh_main_spell_bound_fireball` | ambiguous / mixed net effect (needs the user) | cd 60s · -1s · enemy unit · ×4 uses · bound |
| Fireball Upgraded | `wh3_dlc27_spell_bound_fireball_upgraded` | ambiguous / mixed net effect (needs the user) | cd 60s · -1s · enemy unit · ×6 uses · bound |
| Focused Shot | `wh2_dlc13_lord_abilities_kill_shot` | ambiguous / mixed net effect (needs the user) | cd 120s · -1s · enemy unit · ×2 uses · wind-up 5s |
| From the Shadows | `wh3_main_character_abilities_from_the_shadows` | ambiguous / mixed net effect (needs the user) | cd 120s · 38s · self |
| Gaze of Nagash | `wh2_dlc15_spell_bound_gaze_of_nagash` | ambiguous / mixed net effect (needs the user) | cd 90s · -1s · enemy unit · ×3 uses · wind-up 3s · bound |
| Goggly Glare | `wh2_dlc15_character_abilities_goggly_glare` | ambiguous / mixed net effect (needs the user) | cd 60s · -1s · enemy unit · ×3 uses · wind-up 1s |
| Hail of Doom Arrow | `wh_dlc05_item_abilities_hail_of_doom_arrow` | ambiguous / mixed net effect (needs the user) | cd 90s · -1s · enemy unit · ×3 uses |
| Hand of Gods | `wh2_main_spell_bound_hand_of_gods` | ambiguous / mixed net effect (needs the user) | cd 120s · -1s · enemy unit · ×2 uses · bound |
| Hidden in Time | `wh3_main_lord_abilities_hidden_in_time` | ambiguous / mixed net effect (needs the user) | cd 90s · 73s · self · ×2 uses |
| Locus of Virulence | `wh3_main_character_abilities_locus_of_virulence` | ambiguous / mixed net effect (needs the user) | cd 90s · 25s · self |
| Loec's Shroud | `wh_pro04_unit_abilities_loecs_shroud` | ambiguous / mixed net effect (needs the user) | cd 120s · 44s · self |
| Maelstrom of Change | `wh3_dlc24_unit_abilities_maelstrom_of_change` | ambiguous / mixed net effect (needs the user) | cd 60s · 7s · enemy unit · ×3 uses |
| Mercurial Shot | `wh3_dlc25_character_abilities_mercurial_shot` | ambiguous / mixed net effect (needs the user) | cd 90s · -1s · enemy unit · ×3 uses |
| Mirror (Loec's Shroud) | `wh2_dlc15_unit_abilities_mimic_loecs_shroud` | ambiguous / mixed net effect (needs the user) | cd 120s · 44s · self |
| More Powder! | `wh2_dlc11_hero_abilities_more_powder` | ambiguous / mixed net effect (needs the user) | cd 60s · 10s · friend · ×4 uses |
| Otherworldly Pestilence | `wh3_dlc29_lord_abilities_otherworldly_pestilence` | ambiguous / mixed net effect (needs the user) | cd 120s · 20s · enemy unit · ×1 uses |
| Punch-Dagger | `wh3_dlc29_item_abilities_punch_dagger` | ambiguous / mixed net effect (needs the user) | cd 120s · 4s · enemy unit · ×3 uses |
| Quiver of Aqshy | `wh2_dlc13_lord_abilities_arrows_of_aqshy` | ambiguous / mixed net effect (needs the user) | cd 90s · -1s · enemy unit · ×3 uses · wind-up 4.5s |
| Rancid Visitations | `wh3_main_spell_bound_rancid_visitations` | ambiguous / mixed net effect (needs the user) | cd 90s · 10s · enemy unit · ×2 uses · wind-up 3s · bound |
| Restock! | `wh2_dlc17_hero_abilities_more_powder_generic` | ambiguous / mixed net effect (needs the user) | cd 60s · 10s · friend · ×4 uses |
| Restock! | `wh3_dlc25_abilities_restock_gunnery_school` | ambiguous / mixed net effect (needs the user) | cd 60s · 10s · friend · ×2 uses |
| Schalkain's Teeth | `wh3_dlc27_item_abilities_schalkains_teeth` | ambiguous / mixed net effect (needs the user) | cd 90s · -1s · enemy unit · ×2 uses |
| Shadowblood | `wh3_dlc29_lord_abilities_shadowblood` | ambiguous / mixed net effect (needs the user) | cd 120s · -1s · enemy unit · ×3 uses · wind-up 3s |
| Shem's Burning Gaze | `wh_main_spell_light_shems_burning_gaze_bound` | ambiguous / mixed net effect (needs the user) | cd 60s · -1s · enemy unit · ×3 uses · wind-up 3s · bound |
| Spear of Grungni | `wh3_dlc25_unit_abilities_spear_of_grungni` | ambiguous / mixed net effect (needs the user) | cd 120s · -1s · enemy unit · ×1 uses · wind-up 1s |
| Spear of Kurnous | `wh_dlc05_weapon_abilities_spear_of_kurnous` | ambiguous / mixed net effect (needs the user) | cd 120s · -1s · enemy unit |
| Spirit Bear | `wh3_dlc24_lord_abilities_spirit_bear` | ambiguous / mixed net effect (needs the user) | cd 120s · -1s · enemy unit · ×3 uses · wind-up 4s |
| Spirit Leech | `wh2_dlc09_spell_death_spirit_leech_bound` | ambiguous / mixed net effect (needs the user) | cd 45s · 13s · enemy unit · ×2 uses · wind-up 3s · bound |
| Spirit Leech | `wh3_dlc25_spell_bound_spirit_leech` | ambiguous / mixed net effect (needs the user) | cd 32s · 13s · enemy unit · ×2 uses · wind-up 1s · bound |
| Spirit Leech | `wh3_dlc25_spell_bound_spirit_leech_gunnery_school` | ambiguous / mixed net effect (needs the user) | cd 32s · 13s · enemy unit · ×1 uses · wind-up 1s · bound |
| Spirit Leech | `wh3_main_spell_bound_spirit_leech` | ambiguous / mixed net effect (needs the user) | cd 60s · 13s · enemy unit · ×2 uses · wind-up 1s · bound |
| Spirit Leech | `wh3_twa08_spell_bound_spirit_leech_great_unclean_one_ror` | ambiguous / mixed net effect (needs the user) | cd 60s · 13s · enemy unit · ×1 uses · wind-up 1s · bound |
| Sting of Snagla | `wh3_dlc26_character_abilities_sting_of_snagla` | ambiguous / mixed net effect (needs the user) | cd 120s · -1s · enemy unit · ×3 uses · wind-up 2s |
| Swamp Breath | `wh2_dlc15_hero_abilities_swamp_breath` | ambiguous / mixed net effect (needs the user) | cd 60s · -1s · enemy unit · ×3 uses · wind-up 1.2s |
| Taal's Judgement | `wh3_dlc24_lord_abilities_taals_judgement` | ambiguous / mixed net effect (needs the user) | cd 90s · -1s · enemy unit · ×3 uses · wind-up 4.5s |
| Terrible Malice | `wh3_dlc27_qb_unit_abilities_terrible_malice` | ambiguous / mixed net effect (needs the user) | cd 90s · 2s · enemy unit |
| The Dance of Dreaming | `wh3_dlc27_lord_abilities_the_dance_of_dreaming` | ambiguous / mixed net effect (needs the user) | cd 20s · -1s · self · lord |
| The Emperor's Executioner | `wh3_dlc24_lord_abilities_the_emperors_executioner` | ambiguous / mixed net effect (needs the user) | cd 120s · 2s · enemy unit · ×1 uses · wind-up 2s |
| The Emperor's Executioner | `wh3_dlc24_lord_abilities_the_emperors_executioner_upgrade` | ambiguous / mixed net effect (needs the user) | cd 120s · 2s · enemy unit · ×1 uses · wind-up 2s |
| The Fate of Bjuna | `wh3_dlc25_spell_bound_the_fate_of_bjuna` | ambiguous / mixed net effect (needs the user) | cd 52s · 18s · enemy unit · ×1 uses · wind-up 5s · bound |
| The Fate of Bjuna | `wh3_main_spell_bound_the_fate_of_bjuna` | ambiguous / mixed net effect (needs the user) | cd 120s · 18s · enemy unit · ×1 uses · wind-up 5s · bound |
| The Gaze of Dust | `wh3_dlc29_unit_abilities_the_gaze_of_dust` | ambiguous / mixed net effect (needs the user) | cd 120s · -1s · enemy unit · ×3 uses · wind-up 2.5s |
| The Golden Blowpipe of P'Toohee | `wh2_dlc17_weapon_abilities_the_golden_blowpipe_of_ptoohee` | ambiguous / mixed net effect (needs the user) | cd 120s · -1s · enemy unit · wind-up 2.5s |
| The Liber Bubonicus | `wh2_main_item_abilities_the_liber_bubonicus` | ambiguous / mixed net effect (needs the user) | cd 120s · 15s · enemy unit · ×2 uses |
| The Soulstealer | `wh3_dlc29_spell_bound_undeath_khizaar_the_soulstealer` | ambiguous / mixed net effect (needs the user) | cd 37s · 11s · enemy ground · ×1 uses · wind-up 3s · bound |
| The Windblade | `wh3_dlc24_hero_abilities_windblade` | ambiguous / mixed net effect (needs the user) | cd 120s · -1s · enemy unit · wind-up 1s |
| Vindictive Glare | `wh_dlc06_spell_bound_vindictive_glare` | ambiguous / mixed net effect (needs the user) | cd 60s · -1s · enemy unit · ×4 uses · wind-up 1s · bound |
| Volley of Kurnous | `wh2_dlc16_unit_abilities_volley_of_kurnous` | ambiguous / mixed net effect (needs the user) | cd 90s · -1s · enemy unit · ×1 uses |
| Warp-Fireball | `wh2_dlc14_spell_bound_warpfireball` | ambiguous / mixed net effect (needs the user) | cd 60s · -1s · enemy unit · ×4 uses · bound |
| Wind Bow | `wh3_dlc24_item_abilities_wind_bow` | ambiguous / mixed net effect (needs the user) | cd 120s · -1s · enemy unit · ×3 uses · wind-up 5s · item |
| Acorns of the Oak of Ages | `wh2_dlc16_item_abilities_acorns_of_the_oak_of_ages` | friendly fire (FF-parked block) | cd 120s · 12s · enemy ground · ×2 uses · wind-up 3s |
| Ancestral Rune of Grimnir | `wh2_dlc17_army_abilities_ancestral_rune_of_grimnir` | friendly fire (FF-parked block) | cd 120s · 15s · ground · ×1 uses · wind-up 5s · army |
| Arachneruption | `wh2_dlc15_unit_abilities_arachneruption` | friendly fire (FF-parked block) | cd 90s · 2s · self · ×3 uses |
| Arcane Vassal | `wh2_main_character_abilities_arcane_vassal` | friendly fire (FF-parked block) | cd 120s · 1s · friend |
| Arnzipal's Black Horror | `wh2_dlc10_item_bound_arnizipals_black_horror` | friendly fire (FF-parked block) | cd 120s · 16s · enemy ground · ×1 uses · wind-up 5s · bound |
| Assault of Stone | `wh2_dlc10_item_bound_assault_of_stone` | friendly fire (FF-parked block) | cd 90s · 9s · enemy ground · ×1 uses · wind-up 3s · bound |
| Asur Fire I | `wh3_dlc27_army_abilities_asuryans_rage` | friendly fire (FF-parked block) | cd 60s · 15s · enemy ground · ×3 uses · wind-up 3s · army |
| Asur Fire II | `wh3_dlc27_army_abilities_asuryans_fury` | friendly fire (FF-parked block) | cd 90s · 20s · enemy ground · ×3 uses · wind-up 3s · army |
| Asur Fire III | `wh3_dlc27_army_abilities_asuryans_wrath` | friendly fire (FF-parked block) | cd 120s · 25s · enemy ground · ×3 uses · wind-up 3s · army |
| Axe of Tor | `wh3_main_weapon_abilities_axe_of_tor` | friendly fire (FF-parked block) | cd 90s · 4s · enemy ground · ×3 uses · wind-up 3s |
| Bangstick | `wh3_main_item_abilities_bangstick` | friendly fire (FF-parked block) | cd 90s · 6s · enemy ground · ×3 uses · wind-up 3s |
| Banishment | `wh3_main_spell_bound_banishment` | friendly fire (FF-parked block) | cd 120s · 17s · enemy ground · ×1 uses · wind-up 5s · bound |
| Banishment | `wh_dlc04_spell_bound_banishment` | friendly fire (FF-parked block) | cd 120s · 17s · enemy ground · ×2 uses · wind-up 5s · bound |
| Banishment | `wh_dlc04_spell_bound_banishment_innate` | friendly fire (FF-parked block) | cd 120s · 17s · enemy ground · ×2 uses · wind-up 5s · bound |
| Befuddlement of Mischiefs | `wh2_dlc16_character_abilities_befuddlement_of_mischiefs` | friendly fire (FF-parked block) | cd 90s · 11s · enemy ground · ×3 uses |
| Bjuna Bombard | `wh3_dlc25_army_abilities_bjuna_bombard` | friendly fire (FF-parked block) | cd 120s · 8s · ground · ×1 uses · wind-up 5s · army |
| Black Dragon Egg | `wh2_main_item_abilities_black_dragon_egg` | friendly fire (FF-parked block) | cd 90s · 16s · enemy ground · ×3 uses · wind-up 3s |
| Blade of Khorne | `wh3_main_army_abilities_blade_of_khorne` | friendly fire (FF-parked block) | cd 120s · 8s · enemy ground · wind-up 5s · army |
| Blight Boil | `wh3_dlc29_endgame_crisis_the_vermintide_enemy_clan_morbidus_pestilent_pustule_hidden` | friendly fire (FF-parked block) | cd 60s · 1s · enemy ground · ×3 uses · wind-up 15s · army |
| Blight Boil | `wh3_main_item_abilities_deaths_head` | friendly fire (FF-parked block) | cd 120s · 1s · enemy ground · ×2 uses · wind-up 5s · bound |
| Bloodwrack Cauldron | `wh2_main_army_abilities_bloodwrack_cauldron` | friendly fire (FF-parked block) | cd 60s · 7s · enemy ground · ×3 uses · wind-up 5s · army |
| Blue Fire of Chaos | `wh3_main_daemon_arms_abilities_blue_fire` | friendly fire (FF-parked block) | cd 30s · 6s · ground · ×2 uses |
| Blue Fire of Chaos Upgraded | `wh3_main_daemon_arms_abilities_blue_fire_upgraded` | friendly fire (FF-parked block) | cd 30s · 6s · ground · ×4 uses |
| Boiling Cauldron | `wh3_dlc26_army_abilities_boiling_cauldron` | friendly fire (FF-parked block) | cd 120s · 6s · enemy ground · ×1 uses · wind-up 1.5s · army |
| Boiling Cauldron | `wh3_dlc26_lord_abilities_boiling_cauldron` | friendly fire (FF-parked block) | cd 120s · 6s · enemy ground · ×1 uses · wind-up 1.5s |
| Bolt of Change | `wh3_main_army_abilities_bolt_of_change` | friendly fire (FF-parked block) | cd 90s · 10s · enemy unit · wind-up 3s · army |
| Bolt of Spite | `wh2_main_army_abilities_bolt_of_spite` | friendly fire (FF-parked block) | cd 120s · 7s · enemy unit · ×3 uses · wind-up 5s · army |
| Bonecrusher | `wh3_dlc26_spell_bound_bonecrusher` | friendly fire (FF-parked block) | cd 90s · 6s · enemy ground · ×1 uses · wind-up 3s · bound |
| Bound Fiery Convocation | `wh2_main_spell_bound_khaines_ring_of_fury` | friendly fire (FF-parked block) | cd 120s · 10s · enemy ground · ×2 uses · wind-up 5s · bound |
| Brass Orb | `wh2_dlc12_character_abilities_brass_orb` | friendly fire (FF-parked block) | cd 90s · 13s · enemy ground · ×3 uses · wind-up 3s |
| Brass Orb | `wh2_dlc12_character_abilities_brass_orb_tech_lab_doom_flayer` | friendly fire (FF-parked block) | cd 90s · 13s · enemy ground · ×3 uses · wind-up 3s |
| Brass Orb Upgraded | `wh2_dlc12_character_abilities_brass_orb_upgrade` | friendly fire (FF-parked block) | cd 90s · 13s · enemy ground · ×3 uses · wind-up 3s |
| Brazen Cauldron | `wh2_main_army_abilities_brazen_cauldron` | friendly fire (FF-parked block) | cd 60s · 7s · enemy ground · ×3 uses · wind-up 3s · army |
| Bubonic Broadside | `wh3_dlc29_army_abilities_pestilential_bombardment` | friendly fire (FF-parked block) | cd 90s · 5s · ground · ×2 uses · wind-up 5s |
| Burning Alignment | `wh2_dlc12_unit_abilities_burning_alignment` | friendly fire (FF-parked block) | cd 120s · 12s · enemy ground · ×2 uses · wind-up 5s |
| Celestial Comet | `wh3_main_mount_bound_celestial_comet` | friendly fire (FF-parked block) | cd 49s · 7s · enemy ground · ×2 uses · wind-up 5s · bound |
| Celestial Intervention | `wh3_main_army_abilities_celestial_intervention` | friendly fire (FF-parked block) | cd 120s · 7s · enemy ground · ×1 uses · wind-up 5s · army |
| Celestial Lightning | `wh3_main_mount_bound_celestial_lightning` | friendly fire (FF-parked block) | cd 42s · 4s · enemy ground · ×2 uses · wind-up 3s · bound |
| Chain Lightning | `wh_main_spell_bound_chain_lightning_ror` | friendly fire (FF-parked block) | cd 60s · 20s · enemy ground · ×1 uses · wind-up 5s · bound |
| Chalice of Potions | `wh_dlc07_item_abilities_chalice_of_potions` | friendly fire (FF-parked block) | cd 120s · 7s · enemy ground · ×2 uses · wind-up 5s |
| Comet of Casandora | `wh3_main_spell_bound_comet_of_casandora` | friendly fire (FF-parked block) | cd 120s · 7s · enemy ground · ×1 uses · wind-up 5s · bound |
| Copious Phlegm | `wh3_dlc27_qb_unit_abilities_copious_phlegm` | friendly fire (FF-parked block) | cd 45s · 1s · enemy ground |
| Crackleblaze | `wh3_main_item_abilities_crackleblaze` | friendly fire (FF-parked block) | cd 90s · 1s · enemy ground · ×3 uses |
| Da Boss' Loons | `wh2_dlc15_lord_abilities_da_boss_loons` | friendly fire (FF-parked block) | cd 30s · 12s · enemy ground · ×2 uses |
| Diabolical Puppetry | `wh3_pro10_army_abilities_diabolical_puppetry` | friendly fire (FF-parked block) | cd 90s · 25s · enemy ground · wind-up 3s · army |
| Diabolical Puppetry | `wh3_pro10_army_abilities_diabolical_puppetry_upgrade_1` | friendly fire (FF-parked block) | cd 75s · 30s · enemy ground · wind-up 3s · army |
| Diabolical Puppetry | `wh3_pro10_army_abilities_diabolical_puppetry_upgrade_2` | friendly fire (FF-parked block) | cd 60s · 35s · enemy ground · wind-up 3s · army |
| Diabolical Puppetry | `wh3_pro10_army_abilities_diabolical_puppetry_upgrade_3` | friendly fire (FF-parked block) | cd 45s · 40s · enemy ground · wind-up 3s · army |
| Disembowelling Sweep | `wh3_dlc29_unit_active_ripping_blades` | friendly fire (FF-parked block) | cd 90s · 9s · enemy ground · wind-up 1s |
| Doom Diver Strike | `wh2_dlc15_army_abilities_doom_diver_strike` | friendly fire (FF-parked block) | cd 90s · 6s · ground · ×5 uses · army |
| Doom of Hashut | `wh3_dlc23_army_abilities_doom_of_hashut` | friendly fire (FF-parked block) | cd 120s · 7s · enemy ground · ×1 uses · wind-up 5s · army |
| Doomrocket | `wh3_dlc29_endgame_crisis_the_vermintide_enemy_clan_skryre_doomrocket_hidden` | friendly fire (FF-parked block) | cd 120s · 5s · enemy ground · ×3 uses · wind-up 15s · army |
| Dragon Ogre's Great Horn | `wh_dlc08_item_abilities_great_horn_of_dragon_ogre` | friendly fire (FF-parked block) | cd 120s · 20s · enemy ground · ×2 uses |
| Dragonship Assault | `wh3_dlc27_army_abilities_dragonship_assault` | friendly fire (FF-parked block) | cd 60s · 6s · enemy ground · ×3 uses · wind-up 3s · army |
| Dragonship Blitz | `wh3_dlc27_army_abilities_dragonship_blitz` | friendly fire (FF-parked block) | cd 60s · 6s · enemy ground · ×3 uses · wind-up 3s · army |
| Dragonship Volley | `wh3_dlc27_army_abilities_dragonship_volley` | friendly fire (FF-parked block) | cd 60s · 6s · enemy ground · ×3 uses · wind-up 3s · army |
| Dreadquake Battery | `wh3_dlc23_army_abilities_tower_ballistics` | friendly fire (FF-parked block) | cd 90s · 4s · ground · ×1 uses · wind-up 5s · army |
| Dreadquake Battery Upgraded | `wh3_dlc23_army_abilities_tower_ballistics_upgraded_toz` | friendly fire (FF-parked block) | cd 90s · 4s · ground · ×1 uses · wind-up 5s · army |
| Fiery Convocation | `wh2_dlc10_quest_abilities_magic_fiery_convocation` | friendly fire (FF-parked block) | cd 25s · 10s · enemy ground · wind-up 5s |
| Fiery Convocation | `wh2_dlc10_spell_bound_magic_fiery_convocation` | friendly fire (FF-parked block) | cd 120s · 10s · enemy ground · ×2 uses · wind-up 5s · bound |
| Fiery Ring of Thori | `wh_main_item_abilities_fiery_ring_of_thori` | friendly fire (FF-parked block) | cd 90s · 7s · enemy ground · ×3 uses · wind-up 1s |
| Fishy Breath | `wh2_dlc15_character_abilities_fishy_breathe` | friendly fire (FF-parked block) | cd 32s · 6s · enemy ground · ×3 uses · wind-up 0.5s |
| Flame & Shadow | `wh3_dlc23_lord_abilities_flame_and_shadow` | friendly fire (FF-parked block) | cd 90s · 5s · enemy ground · ×2 uses · wind-up 3s · lord |
| Flame Storm | `wh2_dlc10_quest_abilities_flame_storm` | friendly fire (FF-parked block) | cd 25s · 27s · enemy ground · wind-up 5s |
| Flame Storm | `wh3_dlc20_spell_bound_flame_storm` | friendly fire (FF-parked block) | cd 50s · 27s · enemy ground · ×1 uses · wind-up 5s · bound |
| Flame Storm | `wh3_main_spell_bound_flame_storm` | friendly fire (FF-parked block) | cd 120s · 27s · enemy ground · ×1 uses · wind-up 5s · bound |
| Flesh-eating Scarabs | `wh3_dlc29_unit_abilities_flesh_eating_scarabs` | friendly fire (FF-parked block) | cd 90s · 1s · ground · ×3 uses · wind-up 1s |
| Fly at da Smoke! | `wh3_dlc26_army_abilities_fly_at_da_smoke` | friendly fire (FF-parked block) | cd 120s · 5s · enemy ground · ×3 uses · wind-up 1s · army |
| Foot of Gork | `wh3_dlc26_army_abilities_da_plan_foot_of_gork` | friendly fire (FF-parked block) | cd 180s · 8s · enemy ground · ×3 uses · wind-up 5s · army |
| Frost Fang | `wh3_main_weapon_abilities_frost_fang` | friendly fire (FF-parked block) | cd 120s · 5s · enemy ground · ×2 uses · wind-up 5s |
| Gaze of Malice | `wh2_main_lord_abilities_gaze_of_malice` | friendly fire (FF-parked block) | cd 90s · 8s · enemy ground · ×3 uses · wind-up 3s |
| Gehenna's Golden Globe | `wh3_dlc20_cataclysm_bound_gehennas_golden_globe` | friendly fire (FF-parked block) | cd 120s · 12s · ground · ×1 uses · wind-up 5s · bound |
| Gehenna's Golden Globe | `wh3_dlc27_cataclysm_bound_gehennas_golden_globe` | friendly fire (FF-parked block) | cd 120s · 12s · ground · ×3 uses · wind-up 5s · bound |
| Gehenna's Golden Globe | `wh3_pro10_cataclysm_metal_gehennas_golden_globe_bound` | friendly fire (FF-parked block) | cd 120s · 12s · ground · ×2 uses · wind-up 5s · bound |
| Gehenna's Golden Hounds | `wh3_dlc20_spell_bound_gehennas_golden_hounds` | friendly fire (FF-parked block) | cd 45s · 13s · enemy ground · ×1 uses · wind-up 3s · bound |
| Gilded Horn of Galon Konook | `wh2_main_item_bound_gilded_horn_of_galon_konook` | friendly fire (FF-parked block) | cd 90s · 13s · enemy ground · ×2 uses · wind-up 3s · bound |
| Great Invocation of Sotek | `wh2_dlc12_army_abilities_great_invocation_of_sotek` | friendly fire (FF-parked block) | cd 120s · 6s · enemy ground · ×1 uses · wind-up 5s · army |
| Guns of Zharr | `wh3_dlc23_army_abilities_guns_of_zharr` | friendly fire (FF-parked block) | cd 60s · 4s · enemy ground · wind-up 2s · army |
| Hawk's Talon | `wh_dlc05_weapon_abilities_hawks_talon` | friendly fire (FF-parked block) | cd 90s · -1s · enemy ground · ×3 uses · wind-up 3s |
| Heaven's Gate | `wh3_cp1_item_abilities_heavens_gate` | friendly fire (FF-parked block) | cd 120s · -1s · ground · wind-up 2s |
| Hell Hammer | `wh3_dlc23_spell_bound_hell_hammer` | friendly fire (FF-parked block) | cd 50s · 4s · enemy ground · ×1 uses · wind-up 5s · bound |
| Hounds of Orion | `wh_dlc05_lord_ablities_grey_wolves` | friendly fire (FF-parked block) | cd 90s · 13s · enemy ground · ×3 uses · wind-up 3s |
| Inevitable Fate | `wh3_pro10_army_abilities_inevitable_fate` | friendly fire (FF-parked block) | cd 150s · 15s · friend · wind-up 3s · army |
| Inevitable Fate | `wh3_pro10_army_abilities_inevitable_fate_upgrade_1` | friendly fire (FF-parked block) | cd 120s · 20s · friend · wind-up 3s · army |
| Inevitable Fate | `wh3_pro10_army_abilities_inevitable_fate_upgrade_2` | friendly fire (FF-parked block) | cd 105s · 25s · friend · wind-up 3s · army |
| Inevitable Fate | `wh3_pro10_army_abilities_inevitable_fate_upgrade_3` | friendly fire (FF-parked block) | cd 90s · 30s · friend · wind-up 3s · army |
| Infernal Gateway | `wh3_dlc20_spell_bound_infernal_gateway` | friendly fire (FF-parked block) | cd 54s · 17s · enemy ground · ×1 uses · wind-up 6s · bound |
| Invocation of Ending | `wh2_dlc15_army_abilities_invocation_of_ending` | friendly fire (FF-parked block) | cd 120s · 12s · ground · army |
| Irresistible Plague! | `wh3_dlc29_spell_bound_plague` | friendly fire (FF-parked block) | cd 50s · 20s · enemy ground · ×1 uses · wind-up 5s · bound |
| Isha's Rain | `wh2_dlc13_character_ability_ishas_rain` | friendly fire (FF-parked block) | cd 120s · 9s · enemy ground · ×3 uses · wind-up 3s |
| Jade Lion's Breath | `wh3_dlc24_unit_abilities_jade_dragons_breath` | friendly fire (FF-parked block) | cd 30s · 3s · enemy ground · ×2 uses · wind-up 1s · bound |
| Jungle Swarm | `wh2_dlc12_army_abilities_jungle_swarm` | friendly fire (FF-parked block) | cd 90s · 26s · enemy ground · ×3 uses · wind-up 3s · army |
| Khaine's Flail | `wh2_main_army_abilities_khaines_flail` | friendly fire (FF-parked block) | cd 60s · 4s · enemy ground · ×3 uses · wind-up 3s · army |
| Khaine's Lash | `wh2_main_army_abilities_khaines_lash` | friendly fire (FF-parked block) | cd 60s · 4s · enemy ground · ×3 uses · wind-up 1s · army |
| Khaine's Scourge | `wh2_main_army_abilities_khaines_scourge` | friendly fire (FF-parked block) | cd 60s · 4s · enemy ground · ×3 uses · wind-up 5s · army |
| Khorne's Wrath | `wh3_dlc26_army_abilities_khornes_wrath` | friendly fire (FF-parked block) | cd 120s · 7s · enemy unit · army |
| Klad Brakak | `wh2_dlc17_spell_bound_urannons_thunderbolt_upgraded` | friendly fire (FF-parked block) | cd 30s · 4s · enemy ground · wind-up 3s |
| Kovsh Breath | `wh3_main_item_abilities_kovsh_breath` | friendly fire (FF-parked block) | cd 60s · 2s · enemy ground · ×3 uses · wind-up 1s |
| Lamprey's Bite | `wh3_dlc24_unit_abilities_lampreys_bite` | friendly fire (FF-parked block) | cd 90s · 1s · ground · ×5 uses |
| Lash of Slaanesh | `wh3_dlc27_spell_bound_lash_of_slaanesh` | friendly fire (FF-parked block) | cd 60s · 6s · enemy ground · ×2 uses · wind-up 1s · bound |
| Lash of Slaanesh | `wh3_main_spell_bound_lash_of_slaanesh` | friendly fire (FF-parked block) | cd 30s · 6s · enemy ground · ×2 uses · wind-up 1s · bound |
| Lash of Slaanesh | `wh3_main_spell_bound_lash_of_slaanesh_keeper_of_secrets` | friendly fire (FF-parked block) | cd 30s · 6s · enemy ground · ×2 uses · wind-up 1s · bound |
| Legionary Barrage | `wh2_dlc09_army_abilities_barrage_of_the_legion` | friendly fire (FF-parked block) | cd 90s · 4s · enemy ground · ×3 uses · wind-up 3s · army |
| Lesser Banishment | `wh2_dlc17_spell_bound_lesser_banishment` | friendly fire (FF-parked block) | cd 120s · 8s · enemy ground · ×1 uses · wind-up 5s · bound |
| Lesser Chain Lightning | `wh2_dlc17_spell_bound_lesser_chain_lightning` | friendly fire (FF-parked block) | cd 120s · 10s · enemy ground · ×1 uses · wind-up 5s · bound |
| Lesser Doombolt | `wh2_dlc10_spell_bound_lesser_doombolt` | friendly fire (FF-parked block) | cd 90s · 7s · enemy unit · ×2 uses · wind-up 3s · bound |
| Lightning Strike | `wh3_dlc29_unit_abilities_lightning_strike` | friendly fire (FF-parked block) | cd 42s · 4s · enemy ground · ×2 uses · wind-up 3s · bound |
| Lord of the Storm | `wh_main_lord_abilities_lord_of_the_storm` | friendly fire (FF-parked block) | cd 90s · 11s · enemy ground · ×3 uses · wind-up 1s |
| Magma Storm | `wh3_dlc20_cataclysm_bound_magma_storm` | friendly fire (FF-parked block) | cd 120s · 12s · ground · ×1 uses · wind-up 5s · bound |
| Magma Storm | `wh3_dlc27_cataclysm_bound_magma_storm` | friendly fire (FF-parked block) | cd 120s · 12s · ground · ×3 uses · wind-up 5s · bound |
| Magma Storm | `wh3_pro10_cataclysm_fire_magma_storm_bound` | friendly fire (FF-parked block) | cd 120s · 12s · ground · ×2 uses · wind-up 5s · bound |
| Man the Cannons! | `wh2_dlc13_army_abilities_amber_bow_cannons` | friendly fire (FF-parked block) | cd 60s · 4s · enemy ground · wind-up 3s · army |
| Master of Lightning | `wh3_dlc29_spell_bound_warp_lightning` | friendly fire (FF-parked block) | cd 30s · 5s · enemy ground · ×3 uses · wind-up 1s · bound |
| Master Rune of Immolation | `wh2_dlc17_rune_abilities_master_rune_of_immolation` | friendly fire (FF-parked block) | cd 30s · -1s · self |
| Master Rune of Wrath & Ruin | `wh_dlc06_rune_abilities_master_rune_of_wrath_and_ruin` | friendly fire (FF-parked block) | cd 180s · 10s · enemy ground · wind-up 3s · rune |
| Meteor Strike | `wh3_dlc29_unit_abilities_meteor_strike` | friendly fire (FF-parked block) | cd 49s · 7s · enemy ground · ×3 uses · wind-up 5s · bound |
| Nemesis Crown | `wh3_dlc25_lord_abilities_nemesis_crown` | friendly fire (FF-parked block) | cd 120s · 10s · enemy ground · wind-up 6s |
| Nightmaw | `wh3_dlc27_character_abilities_nightmaw` | friendly fire (FF-parked block) | cd 45s · 5s · enemy ground · ×3 uses · wind-up 3s |
| Norse Roar | `wh2_dlc11_army_abilities_norse_roar` | friendly fire (FF-parked block) | cd 90s · 4s · enemy ground · ×2 uses · wind-up 3s · army |
| Pandemicium | `wh3_dlc25_army_abilities_pandemicium` | friendly fire (FF-parked block) | cd 120s · 4s · ground · ×1 uses · wind-up 3s · army |
| Pestilent Breath | `wh2_main_mount_bound_pestilent_breath` | friendly fire (FF-parked block) | cd 60s · 8s · enemy ground · wind-up 1s |
| Pestilent Breath | `wh3_main_spell_bound_pestilent_breath` | friendly fire (FF-parked block) | cd 60s · 8s · enemy ground · ×4 uses · wind-up 1s · bound |
| Piercing Bolts of Burning | `wh_main_spell_bound_piercing_bolts_of_burning` | friendly fire (FF-parked block) | cd 120s · 8s · enemy ground · ×4 uses · bound |
| Pigeon Bomb | `wh3_dlc25_character_abilities_pigeon_bomb` | friendly fire (FF-parked block) | cd 120s · 12s · enemy ground · ×3 uses |
| Pink Fire of Tzeentch | `wh3_dlc20_spell_bound_pink_fire_of_tzeentch` | friendly fire (FF-parked block) | cd 30s · 2s · enemy ground · ×2 uses · wind-up 1s · bound |
| Pink Fire of Tzeentch | `wh3_main_spell_tzeentch_pink_fire_of_tzeentch_bound` | friendly fire (FF-parked block) | cd 30s · 2s · enemy ground · ×2 uses · wind-up 1s · bound |
| Pit of Shades | `wh3_dlc27_spell_bound_pit_of_shades` | friendly fire (FF-parked block) | cd 120s · 13s · enemy ground · ×1 uses · wind-up 6s · bound |
| Pit of Shades | `wh3_main_spell_bound_pit_of_shades` | friendly fire (FF-parked block) | cd 120s · 13s · enemy ground · ×1 uses · wind-up 6s · bound |
| Pit of Shades | `wh_dlc05_spell_shadow_pit_of_shades_bound` | friendly fire (FF-parked block) | cd 49s · 13s · enemy ground · ×1 uses · wind-up 6s · bound |
| Plaguemaster | `wh3_dlc29_spell_bound_plaguemaster` | friendly fire (FF-parked block) | cd 50s · 20s · enemy ground · ×2 uses · wind-up 5s · bound |
| Rod of the Storm | `wh2_dlc11_army_abilities_rod_of_the_storm` | friendly fire (FF-parked block) | cd 90s · 4s · enemy ground · ×3 uses · wind-up 3s · army |
| Rod of the Storm | `wh2_main_spell_bound_rod_of_the_storm` | friendly fire (FF-parked block) | cd 90s · 4s · enemy ground · ×3 uses · wind-up 3s · bound |
| Rod of Torment | `wh3_dlc20_item_abilities_rod_of_torment` | friendly fire (FF-parked block) | cd 90s · 7s · enemy unit · ×3 uses · wind-up 3s · bound |
| Rubric of Dark Dimensions | `wh2_main_spell_bound_rubric_of_dark_dimensions` | friendly fire (FF-parked block) | cd 90s · 13s · enemy ground · ×2 uses · wind-up 6s · bound |
| Rune of Wrath & Ruin | `wh_main_rune_abilities_rune_of_wrath_and_ruin` | friendly fire (FF-parked block) | cd 120s · 10s · enemy ground · wind-up 3s · rune |
| Sandstorm | `wh2_dlc09_lord_abilities_sand_storm` | friendly fire (FF-parked block) | cd 90s · 14s · enemy ground · ×3 uses · wind-up 3s |
| Sartosa Grapeshot | `wh2_dlc11_army_abilities_sartosa_grapeshot` | friendly fire (FF-parked block) | cd 90s · 6s · enemy ground · ×2 uses · wind-up 1s · army |
| Sceptre of Stone | `wh2_dlc10_item_abilities_sceptre_of_stone` | friendly fire (FF-parked block) | cd 90s · 9s · enemy ground · ×2 uses · wind-up 5s |
| Scorch | `wh2_main_mount_bound_scorch` | friendly fire (FF-parked block) | cd 90s · 12s · enemy ground · wind-up 3s |
| Seafang | `wh_dlc08_lord_abilities_seafang` | friendly fire (FF-parked block) | cd 90s · 8s · enemy ground · ×3 uses · wind-up 4s |
| Searing Doom | `wh3_twa08_spell_bound_searing_doom` | friendly fire (FF-parked block) | cd 60s · 8s · enemy ground · ×2 uses · wind-up 1s · bound |
| Shadows of Anlec | `wh2_main_army_abilities_shadows_of_anlec` | friendly fire (FF-parked block) | cd 60s · 8s · enemy ground · ×3 uses · wind-up 1s · army |
| Shatter | `wh2_dlc13_character_ability_shatter` | friendly fire (FF-parked block) | cd 120s · 5s · enemy ground · ×3 uses · wind-up 1s |
| Shatterstone | `wh2_dlc17_army_abilities_shatterstone` | friendly fire (FF-parked block) | cd 45s · 1s · enemy ground · ×2 uses · wind-up 5s · army |
| Siegebreaker | `wh3_main_weapon_abilities_siegebreaker` | friendly fire (FF-parked block) | cd 120s · 1s · enemy ground · ×3 uses · wind-up 5s |
| Simmering Pot | `wh3_dlc26_lord_abilities_simmering_pot` | friendly fire (FF-parked block) | cd 90s · 6s · enemy ground · ×1 uses · wind-up 1.5s |
| Skabscrath | `wh_main_weapon_abilities_skabscrath` | friendly fire (FF-parked block) | cd 90s · 17s · enemy ground · ×3 uses |
| Skurvy Guns | `wh3_dlc29_endgame_crisis_the_vermintide_enemy_clan_skurvy_guns_hidden` | friendly fire (FF-parked block) | cd 75s · 4s · enemy ground · ×3 uses · wind-up 15s · army |
| Sky Cauldron | `wh2_main_army_abilities_sky_cauldron` | friendly fire (FF-parked block) | cd 60s · 7s · enemy ground · ×3 uses · wind-up 1s · army |
| Slicing Shards | `wh3_dlc20_spell_bound_slicing_shards` | friendly fire (FF-parked block) | cd 48s · 9s · enemy ground · ×1 uses · wind-up 5s · bound |
| Sotek's Sanctum | `wh2_dlc17_army_abilities_soteks_sanctum` | friendly fire (FF-parked block) | cd 90s · 26s · enemy ground · ×3 uses · wind-up 3s · army |
| Soul Rain | `wh2_main_army_abilities_soul_rain` | friendly fire (FF-parked block) | cd 60s · 9s · enemy ground · ×3 uses · wind-up 1s · army |
| Soul Storm | `wh2_main_army_abilities_soul_storm` | friendly fire (FF-parked block) | cd 60s · 9s · enemy ground · ×3 uses · wind-up 5s · army |
| Soul Torrent | `wh2_main_army_abilities_soul_torrent` | friendly fire (FF-parked block) | cd 60s · 9s · enemy ground · ×3 uses · wind-up 3s · army |
| Soul-slaying Hunger | `wh3_dlc29_unit_abilities_soul_slaying_hunger` | friendly fire (FF-parked block) | cd 120s · 20s · enemy ground · ×1 uses · wind-up 5s |
| Spirit Barrage | `wh3_dlc25_army_abilities_spirit_barrage` | friendly fire (FF-parked block) | cd 120s · 10s · enemy unit · ×1 uses · wind-up 5s · army |
| Stoneshaker | `wh3_main_army_abilities_stoneshaker` | friendly fire (FF-parked block) | cd 120s · 1s · enemy ground · ×3 uses · wind-up 1s · army |
| Storm of Fire | `wh3_main_army_abilities_storm_of_fire` | friendly fire (FF-parked block) | cd 120s · 27s · enemy ground · wind-up 5s · army |
| Storm of the Night | `wh2_dlc11_lord_abilities_storm_of_the_night` | friendly fire (FF-parked block) | cd 90s · 22s · enemy unit · ×3 uses |
| Storm of Xholankha | `wh2_dlc13_army_abilities_storm_of_xholankha_upgraded` | friendly fire (FF-parked block) | cd 90s · 30s · enemy ground · ×2 uses · wind-up 5s · army |
| Stream of Corruption | `wh3_dlc20_spell_bound_stream_of_corruption` | friendly fire (FF-parked block) | cd 29s · 3s · enemy ground · ×2 uses · wind-up 1s · bound |
| Stream of Corruption | `wh3_main_spell_nurgle_stream_of_corruption_bound` | friendly fire (FF-parked block) | cd 29s · 3s · enemy ground · ×2 uses · wind-up 1s · bound |
| Sunfang | `wh2_main_weapon_abilities_sunfang` | friendly fire (FF-parked block) | cd 120s · 17s · enemy ground · wind-up 5s |
| Sword of Khaine | `wh2_dlc10_weapon_abilities_sword_of_khaine` | friendly fire (FF-parked block) | cd 120s · 11s · enemy ground |
| Tempest | `wh3_dlc27_army_high_magic_tempest` | friendly fire (FF-parked block) | cd 44s · 17s · enemy unit · ×2 uses · wind-up 3s · army |
| Tempest of Blue Flame | `wh3_pro10_army_abilities_tempest_of_blue_flame` | friendly fire (FF-parked block) | cd 90s · 15s · ground · wind-up 3s · army |
| Tempest of Blue Flame | `wh3_pro10_army_abilities_tempest_of_blue_flame_upgrade_1` | friendly fire (FF-parked block) | cd 75s · 20s · ground · wind-up 3s · army |
| Tempest of Blue Flame | `wh3_pro10_army_abilities_tempest_of_blue_flame_upgrade_2` | friendly fire (FF-parked block) | cd 60s · 25s · ground · wind-up 3s · army |
| Tempest of Blue Flame | `wh3_pro10_army_abilities_tempest_of_blue_flame_upgrade_3` | friendly fire (FF-parked block) | cd 45s · 30s · ground · wind-up 3s · army |
| The Abyssal Swarm | `wh3_dlc29_spell_bound_undeath_the_abyssal_swarm` | friendly fire (FF-parked block) | cd 42s · 30s · enemy ground · ×2 uses · wind-up 3s · bound |
| The Bow of Loren | `wh_dlc05_weapon_abilities_the_bow_of_loren` | friendly fire (FF-parked block) | cd 60s · -1s · enemy ground · wind-up 3s |
| The Burning Head | `wh3_dlc25_spell_bound_fire_the_burning_head` | friendly fire (FF-parked block) | cd 90s · 20s · enemy ground · ×1 uses · wind-up 3s · bound |
| The Burning Head | `wh3_dlc29_spell_bound_fire_skull_of_flaming_death` | friendly fire (FF-parked block) | cd 90s · 20s · enemy ground · ×3 uses · wind-up 3s · bound |
| The Dreaded Thirteenth Spell | `wh3_dlc29_spell_bound_the_dreaded_thirteenth` | friendly fire (FF-parked block) | cd 52s · 13s · enemy ground · ×1 uses · wind-up 5s · bound |
| The Dreaded Thirteenth Spell | `wh3_dlc29_spell_bound_the_dreaded_thirteenth_1` | friendly fire (FF-parked block) | cd 52s · 13s · enemy ground · ×1 uses · wind-up 5s · bound |
| The Dreaded Thirteenth Spell | `wh3_dlc29_spell_bound_the_dreaded_thirteenth_thanquol` | friendly fire (FF-parked block) | cd 52s · 13s · enemy ground · ×1 uses · wind-up 5s · bound |
| The Dreaded Thirteenth Spell | `wh3_dlc29_spell_bound_the_dreaded_thirteenth_thanquol_1` | friendly fire (FF-parked block) | cd 52s · 13s · enemy ground · ×1 uses · wind-up 5s · bound |
| The Dwellers Below | `wh3_main_spell_bound_the_dwellers_below` | friendly fire (FF-parked block) | cd 120s · 15s · enemy ground · ×1 uses · wind-up 5s · bound |
| The Dwellers Below | `wh_dlc08_spell_bound_the_dwellers_below` | friendly fire (FF-parked block) | cd 120s · 15s · enemy ground · ×2 uses · wind-up 5s · bound |
| The Gem of Sunfire | `wh2_main_spell_bound_the_gem_of_sunfire` | friendly fire (FF-parked block) | cd 90s · 26s · enemy ground · ×1 uses · wind-up 5s · bound |
| The Hammer of Smednir | `wh3_dlc23_item_abilities_hammer_of_smednir` | friendly fire (FF-parked block) | cd 120s · 10s · enemy ground · ×3 uses · wind-up 3s |
| The Matterless Earth | `wh3_dlc27_army_abilities_eternal_dance_tempo_3_carver_of_ways` | friendly fire (FF-parked block) | cd 120s · 10s · ground · ×1 uses · wind-up 5s · army |
| The Penumbral Pendulum | `wh3_dlc20_spell_bound_the_penumbral_pendulum` | friendly fire (FF-parked block) | cd 40s · 2s · enemy ground · ×1 uses · wind-up 3s · bound |
| The Purple Eclipse | `wh3_dlc25_army_abilities_purple_eclipse` | friendly fire (FF-parked block) | cd 120s · 10s · ground · ×1 uses · wind-up 5s · army |
| The Purple Sun of Xereus | `wh2_dlc11_spell_bound_the_purple_sun_of_xereus` | friendly fire (FF-parked block) | cd 120s · 11s · enemy ground · ×2 uses · wind-up 5s · bound |
| The Ruination of Cities | `wh2_main_lord_abilities_the_ruination_of_cities` | friendly fire (FF-parked block) | cd 120s · 7s · enemy ground · ×2 uses · wind-up 5s |
| The Solid Airs | `wh3_dlc27_army_abilities_eternal_dance_tempo_3_tempest_of_depravity` | friendly fire (FF-parked block) | cd 120s · 12s · ground · ×1 uses · wind-up 5s · army |
| The Spear Slaupnir | `wh3_dlc20_weapon_abilities_the_spear_slaupnir` | friendly fire (FF-parked block) | cd 120s · 2s · enemy ground · ×2 uses · wind-up 3s |
| Thorsen's Thunderstorm | `wh3_dlc20_cataclysm_bound_thorsens_thunderstorm` | friendly fire (FF-parked block) | cd 120s · 31s · ground · ×1 uses · wind-up 5s · bound |
| Thorsen's Thunderstorm | `wh3_dlc27_cataclysm_bound_thorsens_thunderstorm` | friendly fire (FF-parked block) | cd 120s · 31s · ground · ×3 uses · wind-up 5s · bound |
| Thunder Charge | `wh3_main_army_abilities_thunder_charge` | friendly fire (FF-parked block) | cd 120s · 6s · enemy ground · ×2 uses · wind-up 3s · army |
| Tidecall | `wh2_dlc11_spell_bound_tidecall` | friendly fire (FF-parked block) | cd 60s · 2s · enemy ground · ×4 uses · wind-up 1s |
| Tome of Furion | `wh2_main_spell_bound_tome_of_furion` | friendly fire (FF-parked block) | cd 60s · 7s · enemy unit · ×4 uses · wind-up 5s · bound |
| Tyrant's Talon | `wh3_cp1_weapon_abilities_tyrants_talon` | friendly fire (FF-parked block) | cd 120s · 27s · self · weapon |
| Urannon's Thunderbolt | `wh2_dlc17_spell_bound_urannons_thunderbolt` | friendly fire (FF-parked block) | cd 90s · 4s · enemy ground · ×2 uses · wind-up 3s · bound |
| Vaul's Hammer | `wh2_main_army_abilities_vauls_hammer` | friendly fire (FF-parked block) | cd 120s · 1s · enemy ground · ×2 uses · wind-up 5s · army |
| Vile Entropy | `wh2_dlc17_army_abilities_vile_entropy` | friendly fire (FF-parked block) | cd 90s · 20s · enemy ground · ×2 uses · wind-up 5s · army |
| Viletide | `wh_dlc03_spell_bound_viletide` | friendly fire (FF-parked block) | cd 60s · 3s · enemy ground · ×4 uses · wind-up 3s · bound |
| Viletide Upgraded | `wh2_dlc17_army_abilities_viletide` | friendly fire (FF-parked block) | cd 90s · 3s · enemy ground · ×2 uses · wind-up 3s · army |
| Vortical Blast | `wh2_main_army_abilities_vortic_blast` | friendly fire (FF-parked block) | cd 30s · 5s · enemy ground · army |
| Wall of Wind & Fire | `wh3_main_spell_bound_wall_of_wind_and_fire` | friendly fire (FF-parked block) | cd 90s · 25s · enemy ground · ×2 uses · wind-up 3s · bound |
| Wand of the Kharaidon | `wh2_main_spell_bound_wand_of_the_kharaidon` | friendly fire (FF-parked block) | cd 120s · 7s · enemy unit · ×2 uses · wind-up 5s · bound |
| Warp Junction | `wh3_dlc29_lord_abilities_warp_junction` | friendly fire (FF-parked block) | cd 120s · 14s · enemy ground · ×2 uses · wind-up 3s |
| Warp Lightning Rod | `wh2_dlc16_unit_abilities_warp_lightning_rod` | friendly fire (FF-parked block) | cd 60s · 5s · self · ×3 uses · wind-up 1s |
| Warpstorm Doomrocket | `wh2_dlc12_army_abilities_warpstorm_doomrocket` | friendly fire (FF-parked block) | cd 45s · 7s · enemy ground · ×1 uses · wind-up 5s · army |
| Warpstorm Doomrocket | `wh2_dlc12_army_abilities_warpstorm_doomrocket_upgraded` | friendly fire (FF-parked block) | cd 45s · 7s · enemy ground · ×1 uses · wind-up 5s · army |
| Warpstorm Doomrocket | `wh3_dlc24_tze_changeling_theatre_scheme_grand_cathay_doom_rocket` | friendly fire (FF-parked block) | cd 0s · 7s · enemy ground · ×3 uses · wind-up 5s · army |
| Wind Blast | `wh2_dlc11_spell_bound_wind_blast` | friendly fire (FF-parked block) | cd 60s · 2s · enemy ground · ×4 uses · wind-up 1s |
| Wind of Death | `wh2_dlc15_spell_bound_wind_of_death` | friendly fire (FF-parked block) | cd 120s · 5s · enemy ground · ×1 uses · wind-up 5s · bound |
| Winged Staff | `wh2_main_weapon_bound_winged_staff` | friendly fire (FF-parked block) | cd 60s · 7s · enemy ground · ×4 uses · bound |
| Wolf's Howl | `wh3_main_weapon_abilities_the_traitors_sword` | friendly fire (FF-parked block) | cd 90s · 10s · enemy unit · ×3 uses |
| Wraith Storm | `wh2_dlc11_army_abilities_wraith_storm` | friendly fire (FF-parked block) | cd 90s · 9s · enemy unit · ×3 uses · wind-up 3s · army |
| Wraith Storm | `wh2_dlc11_lord_abilities_wraith_storm` | friendly fire (FF-parked block) | cd 90s · 9s · enemy unit · ×3 uses · wind-up 3s |
| Wrath of Manann | `wh_dlc07_item_abilities_wrath_of_manann` | friendly fire (FF-parked block) | cd 120s · 5s · enemy ground · ×2 uses · wind-up 5s |
| Wrath of Zharr | `wh3_dlc23_army_abilities_wrath_of_zharr` | friendly fire (FF-parked block) | cd 90s · 4s · enemy ground · ×2 uses · wind-up 3s · army |
| Xapati's Sanctum | `wh2_dlc17_army_abilities_xapatis_sanctum` | friendly fire (FF-parked block) | cd 60s · 5s · enemy ground · ×3 uses · wind-up 3s · army |
| Zhufbar 42-Pounders | `wh2_dlc11_army_abilities_zhufbar_42_pounders` | friendly fire (FF-parked block) | cd 90s · 4s · enemy ground · ×2 uses · wind-up 3s · army |
| Zhufbar 42-Pounders | `wh2_dlc17_army_abilities_zhufbar_42_pounders_engineer` | friendly fire (FF-parked block) | cd 90s · 4s · enemy ground · ×1 uses · wind-up 3s · army |
| Ashes & Dust | `wh3_dlc20_cataclysm_bound_ashes_and_dust` | friendly fire (own-troop damage) | cd 120s · 11s · enemy ground · ×1 uses · wind-up 5s · bound |
| Ashes & Dust | `wh3_dlc27_cataclysm_bound_ashes_and_dust` | friendly fire (own-troop damage) | cd 120s · 11s · enemy ground · ×3 uses · wind-up 5s · bound |
| Defiling Deluge | `wh3_twa08_unit_abilities_defiling_deluge` | friendly fire (own-troop damage) | cd 120s · 6s · self · ×2 uses · questionnaire §2 #238 |
| Descent Into Dissolution | `wh3_dlc27_army_abilities_eternal_dance_tempo_3_jesters_laughter` | friendly fire (own-troop damage) | cd 120s · 48s · ground · ×2 uses · wind-up 3s · army |
| Eshin Clanstone | `wh2_main_army_abilities_eshin_clanstone` | friendly fire (own-troop damage) | cd 120s · 22s · ground · ×3 uses · army |
| Flock of Doom | `wh3_dlc27_spell_bound_runecaller_flock_of_doom` | friendly fire (own-troop damage) | cd 60s · 6s · enemy ground · ×3 uses · wind-up 1s · bound |
| Flock of Doom | `wh3_main_spell_bound_flock_of_doom` | friendly fire (own-troop damage) | cd 60s · 6s · enemy ground · ×2 uses · bound |
| Flock of Doom | `wh_dlc08_spell_bound_flock_of_doom` | friendly fire (own-troop damage) | cd 60s · 6s · enemy ground · ×4 uses · bound |
| Gust of the Grave | `wh3_dlc29_unit_abilities_lesser_tomb_swarm` | friendly fire (own-troop damage) | cd 90s · 18s · ground · ×1 uses · wind-up 5s · army |
| Murderous Exhortations | `wh3_dlc26_lord_abilities_murderous_exhortations` | friendly fire (own-troop damage) | cd 120s · 20s · self · ×3 uses · questionnaire §2 #246 |
| Plaguereaper | `wh3_dlc29_item_abilities_plaguereaper` | friendly fire (own-troop damage) | cd 120s · 25s · self · ×2 uses |
| Raging Tornado | `wh3_dlc29_unit_abilities_raging_tornado` | friendly fire (own-troop damage) | cd 120s · 32s · ground · ×3 uses · wind-up 5s · bound |
| Reaper of Souls | `wh2_dlc14_lord_abilities_reaper_of_souls` | friendly fire (own-troop damage) | cd 90s · 9s · self |
| Ring of Corin | `wh2_main_spell_bound_ring_of_corin` | friendly fire (own-troop damage) | cd 90s · 22s · enemy ground · ×2 uses · bound |
| Rod of Corruption | `wh2_main_item_abilities_rod_of_corruption` | friendly fire (own-troop damage) | cd 120s · 11s · self · ×3 uses · questionnaire §2 #251 |
| Shard Blade | `wh3_main_weapon_abilities_shard_blade` | friendly fire (own-troop damage) | cd 120s · 15s · self · ×2 uses |
| Soul Stealer | `wh2_dlc10_spell_bound_soul_stealer_ror` | friendly fire (own-troop damage) | cd 120s · 12s · enemy ground · ×1 uses · bound |
| Soul Stealer | `wh3_dlc27_spell_bound_soul_stealer` | friendly fire (own-troop damage) | cd 120s · 12s · enemy ground · ×1 uses · bound |
| Sword of Daith | `wh_dlc05_weapon_abilities_daiths_sword` | friendly fire (own-troop damage) | cd 120s · 17s · enemy ground · ×2 uses |
| The Divestment | `wh3_dlc27_army_abilities_eternal_dance_tempo_3_insidious_allure` | friendly fire (own-troop damage) | cd 120s · 24s · ground · ×1 uses · wind-up 3s · army |
| Tomb Swarm | `wh2_dlc09_army_abilities_tomb_swarm` | friendly fire (own-troop damage) | cd 120s · 18s · ground · ×2 uses · wind-up 5s · army |
| Wail of Malice | `wh2_dlc14_unit_abilities_wail_of_malice` | friendly fire (own-troop damage) | cd 90s · 7s · self · ×2 uses |
| Warp-Quake | `wh2_dlc14_unit_abilities_warp_quake` | friendly fire (own-troop damage) | cd 90s · 17s · self |
| Warpstorm Scroll | `wh2_main_item_abilities_warpstorm_scroll` | friendly fire (own-troop damage) | cd 60s · 29s · enemy ground · ×1 uses |
| Web of Shadows | `wh2_main_weapon_abilities_web_of_shadows` | friendly fire (own-troop damage) | cd 60s · 17s · self · ×1 uses |
| Zefet-nebtar, the Mortis Blade | `wh3_dlc29_item_abilities_zefet_nebtar_the_mortis_blade` | friendly fire (own-troop damage) | cd 120s · 1s · enemy ground · ×3 uses · wind-up 2s · item |
| Blood Sacrifice | `wh3_dlc26_lord_abilities_blood_sacrifice` | mixed positive-and-negative effect | cd 60s · 10s · friend · ×3 uses |
| Death's Timekeeper | `wh3_dlc25_item_abilities_deaths_timekeeper` | mixed positive-and-negative effect | cd 120s · 10s · enemy unit · ×2 uses |
| Dweomer Leach Orb | `wh3_dlc23_item_abilities_dweomer_leach_orb` | mixed positive-and-negative effect | cd 90s · 22s · enemy unit |
| Eat da Runts! | `wh3_dlc26_unit_abilities_eat_da_runts` | mixed positive-and-negative effect | cd 90s · 10s · friend · ×3 uses |
| Ominous Powder | `wh3_dlc25_item_abilities_ominous_powder` | mixed positive-and-negative effect | cd 120s · 30s · self |
| Preyton Horns | `wh3_dlc27_item_abilities_preyton_horns` | mixed positive-and-negative effect | cd 90s · 24s · enemy unit · bound |
| Staff of Masks | `wh3_dlc27_item_abilities_staff_of_the_masque` | mixed positive-and-negative effect | cd 120s · 23s · enemy unit · ×2 uses · item · questionnaire §2 #464 |
| The Amber Trance | `wh2_dlc10_item_abilities_the_amber_trance` | mixed positive-and-negative effect | cd 60s · 25s · enemy unit · ×1 uses |
| The Waltz of Lethargy | `wh3_dlc27_lord_abilities_the_waltz_of_lethargy` | mixed positive-and-negative effect | cd 20s · -1s · self · lord · questionnaire §2 #207 |
| Touched by the Moon | `wh2_dlc17_army_abilities_touched_by_the_moon` | mixed positive-and-negative effect | cd 90s · 45s · friend · ×2 uses · wind-up 5s · army · questionnaire §2 #412 |
| Ultimate Verdict | `wh3_cp1_character_abilities_terrifying_presence` | mixed positive-and-negative effect | cd 120s · 28s · self · questionnaire §2 #214 |
| Eagle Bow | `wh2_dlc16_weapon_abilities_eagle_bow` | stealth/escape/stalk effect | cd 60s · 25s · friend |
| Envelop in Mist | `wh2_dlc15_army_abilities_envelop_in_mist` | stealth/escape/stalk effect | cd 120s · 43s · ground · army |
| Envelop in Mist | `wh3_dlc27_character_abilities_envelop_in_mist_bound` | stealth/escape/stalk effect | cd 120s · 22s · ground · ×1 uses |
| Loec's Blessing | `wh2_dlc16_lord_abilities_loecs_blessing` | stealth/escape/stalk effect | cd 90s · 32s · friend/self |
| No Escape | `wh3_main_character_abilities_no_escape` | stealth/escape/stalk effect | cd 90s · 14s · enemy unit · ×3 uses · questionnaire §2 #456 |
| Perfect Predator | `wh3_dlc27_unit_abilities_perfect_predator` | stealth/escape/stalk effect | cd 120s · 48s · self |
| Rival Hide Talisman | `wh2_main_item_abilities_rival_hide_talisman` | stealth/escape/stalk effect | cd 60s · 31s · self · ×1 uses · questionnaire §2 #250 |
| Sand Veil | `wh2_dlc09_army_abilities_sand_veil` | stealth/escape/stalk effect | cd 90s · 89s · friend · ×3 uses · army |
| Skitterleap | `wh3_dlc29_spell_bound_skitterleap` | stealth/escape/stalk effect | cd 29s · 25s · friend/self · ×3 uses · wind-up 1s · bound |
| Speed of Lykos | `wh2_dlc10_item_abilities_speed_of_lykos` | stealth/escape/stalk effect | cd 60s · 36s · friend · ×1 uses |
| Tricksy Traps | `wh_dlc06_lord_abilities_tricksy_traps` | stealth/escape/stalk effect | cd 120s · 32s · self |
| Formless Horror | `wh3_dlc24_lord_abilities_formless_horror_changeling` | transform/shapechange | cd 60s · 5s · self · wind-up 5s |
| Formless Horror | `wh3_dlc24_lord_abilities_formless_horror_quest_battle_changeling_form` | transform/shapechange | cd 60s · 5s · self · wind-up 5s |
| Transformation of Kadon | `wh3_dlc27_spell_bound_transformation_of_kadon` | transform/shapechange | cd 45s · 1s · friend/self · ×1 uses · wind-up 5s · bound |
| Transformation of the Dragon | `wh3_dlc24_lord_abilities_jade_dragon_human_form` | transform/shapechange | cd 120s · 5s · self · wind-up 5s |
| Transformation of the Dragon | `wh3_main_lord_abilities_iron_dragon_human_form` | transform/shapechange | cd 120s · 5s · self · wind-up 5.3s |
| Transformation of the Dragon | `wh3_main_lord_abilities_storm_dragon_human_form` | transform/shapechange | cd 120s · 5s · self · wind-up 5.3s |
| Tz'arkan | `wh2_dlc14_lord_abilities_tzarkan` | transform/shapechange | cd 0s · 0s · self · wind-up 3s |
| Tz'arkan | `wh2_dlc14_lord_abilities_tzarkan_mp` | transform/shapechange | cd 0s · 0s · self · wind-up 3s |
| Tz'arkan | `wh2_dlc14_lord_abilities_tzarkan_snikch` | transform/shapechange | cd 0s · 0s · self · wind-up 1.5s |
| Tz'arkan | `wh2_dlc14_lord_abilities_tzarkan_spite` | transform/shapechange | cd 0s · 0s · self · wind-up 3s |
| Tz'arkan | `wh2_dlc14_lord_abilities_tzarkan_spite_mp` | transform/shapechange | cd 0s · 0s · self · wind-up 3s |

