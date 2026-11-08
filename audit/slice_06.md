# Ability logic audit — slice 6 (entries 291–348, source order)

Counts: **58 audited · 26 flagged · 32 clean**.
Audited: `ABILITIES` entries 291–348 of `C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua`, in source order.
Game data: extracted game tables `%LOCALAPPDATA%\Temp\wh3\` (`unit_spec_abil.tsv`, `unit_abilities.tsv`, `phase_junc.tsv`, `phases.tsv`, `special_ability_to_invalid_usage_flags_tables.tsv`, `special_ability_to_invalid_target_flags_tables.tsv`, loc files) and `%LOCALAPPDATA%\Temp\wh3\uieff\`.
Engine context applied: all 58 entries ride the shared `melee_unwavering` evaluator (fires when the unit is in melee and neither routing nor wavering) and cast on **self** via the default `perform_special_ability(key, unit)` call — no `cast_target` writer and no ground key among these. For 32 of the 58 that self-cast matches the game's data (self augments, self-centred self+allies auras, self-centred hexes per `ai_usage`). The 26 flagged do not: 16 are aimed single-enemy hexes/debuffs (can't be aimed, self is not a legal target), 4 are enemy-ground area hexes, 2 may only target a friendly unit, and 4 are self buffs whose own engine gate refuses the cast exactly in the in-melee state. Trigger mix: 58× `melee_unwavering`.

## FLAGGED

### Blooood!
- **Marker / key:** `blooood` — `wh_main_unit_abilities_blooood` (entry 291, source line 1377)
- **Mod's current logic:** trigger `melee_unwavering` — fires when the Hellcannon is in melee (not routing/wavering), cast on itself.
- **What the game declares:** a self augment (`wh_type_augment`, `affect_self=true`) — Speed +25%, Acceleration +18%, Vigour −2%/s for 18 s, 60 s recharge — with a hard usage gate: `cannot_perform_missile_attack` (the game's own wording: "Can use if: Missile attack possible"). Its text: *"The Hellcannon breaks its chains and rushes forwards."*
- **Why it does not make sense:** it is a rush-forward movement buff meant to be pressed while the Hellcannon can still fire, and the game refuses it the moment the unit cannot perform a missile attack — exactly the "in melee" state the mod fires it in. The trigger selects the one state where the cast is invalid and the speed effect has nothing left to close.
- **Feasibility note:** not a read problem — the ability needs a moment *before* contact, so the in-melee trigger itself is wrong; as written every attempt is refused by the engine's own gate.

### Book of Secrets
- **Marker / key:** `book_of_secrets` — `wh3_dlc24_item_abilities_book_of_secrets` (entry 294, source line 1389)
- **Mod's current logic:** trigger `melee_unwavering` — fires when the owner is in melee, cast on self.
- **What the game declares:** a Hex (`wh_type_hex`) aimed at **one enemy unit** (`target_enemies=true`, `target_self=false`, `num_effected_enemy_units=1`, 100 m intercept) with three negative 20 s phases (Damage 10/s; −25% Speed + Fire Weakness; −24 Melee Attack/Defence), ×3 uses.
- **Why it does not make sense:** the cast must be aimed at an enemy and the mod cannot aim enemy-targeted casts (no enemy-unit read); a self-cast is not even a legal target for it, so the entry cannot deliver its declared debuff.
- **Feasibility note:** not implementable as-is — enemy-targeting needs an enemy read/selection the mod does not have; flag for the user (leave to the player or exclude).

### Boom!
- **Marker / key:** `boom` — `wh_main_unit_abilities_boom` (entry 295, source line 1393)
- **Mod's current logic:** trigger `melee_unwavering` — fires when the Hellcannon is in melee, cast on itself.
- **What the game declares:** a self augment for its own shots — +20% Armour-Piercing / +25% Base Explosive Damage for 15 s, 90 s recharge — gated by `cannot_perform_missile_attack` ("Enabled if: Missile attack possible").
- **Why it does not make sense:** the buff only means anything while the Hellcannon is shooting, and the game's own gate forbids it while the unit cannot perform a missile attack — which is precisely the in-melee state the trigger fires in. It cannot fire where it would matter, and would be pointless if it did.
- **Feasibility note:** trigger problem, not a read problem — should fire before contact (while the guns still work); as written the in-melee cast is refused.

### Chalice of Dark Rain
- **Marker / key:** `chalice_of_dark_rain` — `wh_dlc03_item_abilities_chalice_of_dark_rain` (entry 298, source line 1405)
- **Mod's current logic:** trigger `melee_unwavering` — fires when the owner is in melee, cast on self.
- **What the game declares:** an area Hex placed on **enemy ground** (`target_enemies=true`, `target_ground=true`, 35 m area, 200 m range) — Accuracy −30 for 89 s to affected combatants.
- **Why it does not make sense:** it is a ground-placed enemy-area hex that must be aimed at a spot under the enemy; the mod cannot aim it (no enemy read, and it never fires targeted casts with a guessed target) and self is not a legal target.
- **Feasibility note:** not implementable as-is — needs enemy/ground aiming the mod does not have; flag for the user.

### Cube of Darkness
- **Marker / key:** `cube_of_darkness` — `wh2_main_item_abilities_cube_of_darkness` (entry 303, source line 1425)
- **Mod's current logic:** trigger `melee_unwavering` — fires when the owner is in melee, cast on self.
- **What the game declares:** a Hex of the Winds aimed at **one enemy unit** (100 m intercept) — Power Recharge −40% for 18 s (it drains the targeted enemy spellcaster's winds).
- **Why it does not make sense:** an aimed single-enemy hex; casting it on the owner is not a legal target and the mod cannot aim at the enemy caster it is designed to drain.
- **Feasibility note:** not implementable as-is (no enemy targeting); flag for the user.

### Curse of Khsar
- **Marker / key:** `curse_of_khsar` — `wh2_dlc09_character_abilities_curse_of_khsar` (entry 304, source line 1429)
- **Mod's current logic:** trigger `melee_unwavering` — fires when the owner is in melee, cast on self.
- **What the game declares:** an area Hex on **enemy ground** (`target_ground=true`, 35 m area at up to 100 m) — Armour −60 for 25 s; one use; and its own usage condition `health_above_50%` marks it usable only at ≤50% caster health.
- **Why it does not make sense:** it must be aimed at ground under the enemy (not aimable, self not a legal target), and the mod's trigger ignores the ability's own ≤50%-health usage condition entirely.
- **Feasibility note:** not implementable as-is — enemy-ground aiming does not exist in the mod; flag for the user.

### Daemonic Whispers
- **Marker / key:** `slezuzus_voice` — `wh3_dlc27_character_abilities_slezuzus_voice` (entry 305, source line 1433)
- **Mod's current logic:** trigger `melee_unwavering` — fires when the owner is in melee, cast on self.
- **What the game declares:** an Augment that may target only **a friendly unit** (`target_friends=true`, `target_self=false`, `affect_self=false`, one unit, 200 m) — +16 Leadership to the chosen ally.
- **Why it does not make sense:** the game offers no self target for it (self is not in the target set), so the self-cast cannot deliver the declared buff to a friendly unit — the mod casts it on the one unit the ability does not accept.
- **Feasibility note:** friendly units are readable and the mod already ships ally-targeting evaluators, so an ally picker could carry it — but as written the self-cast is the wrong target; flag for the user.

### Deranged Munitions
- **Marker / key:** `deranged_munitions` — `wh3_dlc25_lord_abilities_deranged_munitions` (entry 307, source line 1441)
- **Mod's current logic:** trigger `melee_unwavering` — fires when the owner is in melee, cast on self.
- **What the game declares:** a missile augment: +50% Armour-Piercing and +50% Base Missile Damage (+ Magical Attacks) for 30 s, with the game's own target restriction `cannot_perform_missile_attack` (targets that cannot perform a missile attack are invalid).
- **Why it does not make sense:** the trigger fires exactly while the owner cannot perform a missile attack (locked in melee), the state the game's target gate rejects; and even where it were legal, a missile-damage buff does nothing for a unit that cannot fire.
- **Feasibility note:** needs a different condition/target (e.g. a friendly-unit picker outside the melee lock) — no new reads required for a friendly picker, but the in-melee self-cast is the one combination the game's data rejects.

### Deranged Munitions Upgraded
- **Marker / key:** `deranged_munitions_upgraded` — `wh3_dlc25_lord_abilities_deranged_munitions_upgraded` (entry 308, source line 1445)
- **Mod's current logic:** trigger `melee_unwavering` — fires when the owner is in melee, cast on self.
- **What the game declares:** the area version of the same missile augment (+50% missile damage, 35 m ally aura, 30 s) with the same `cannot_perform_missile_attack` target restriction.
- **Why it does not make sense:** same contradiction as the base key — the in-melee state is exactly when the owner (and any melee-locked ally) is an invalid target for a missile-damage buff.
- **Feasibility note:** same as the base key — a different trigger/target is needed; the in-melee self-cast cannot work as declared.

### Don't Even Try It
- **Marker / key:** `dont_even_try_it` — `wh2_dlc15_lord_abilities_dont_even_try_it` (entry 309, source line 1449)
- **Mod's current logic:** trigger `melee_unwavering` — fires when the owner is in melee, cast on self.
- **What the game declares:** a direct-damage Hex at **one enemy unit** (100 m intercept) — 144 Damage every 2 s for 18 s, +15 s ability recharge on the victim, ×2 uses ("Strong vs a single combatant").
- **Why it does not make sense:** its entire payload is aimed at a single enemy; the mod cannot aim it and self is not a legal target, so the cast cannot land the damage it exists for.
- **Feasibility note:** not implementable as-is (enemy targeting); flag for the user.

### Doom & Darkness
- **Marker / key:** `doom_and_darkness_gunnery_school` — `wh3_dlc25_spell_Bound_doom_and_darkness_gunnery_school` · `wh3_dlc27_spell_bound_runecaller_death_doom_and_darkness` · `wh_dlc08_spell_bound_death_doom_and_darkness` (entry 310, source line 1453)
- **Mod's current logic:** trigger `melee_unwavering` — fires when the owner is in melee, cast on self.
- **What the game declares:** a morale Hex aimed at **one enemy unit** (200 m intercept) — Leadership −16 for 36 s; ×2/×3 uses across the three keys.
- **Why it does not make sense:** an aimed single-enemy leadership debuff; the mod cannot aim enemy casts and self is not a legal target, so the entry cannot debuff the enemy it is designed for.
- **Key-claim defect (extra):** the first key contains an uppercase `B` (`spell_Bound…`, the game's own spelling), but the mod's button-claim match lower-cases the engine key before comparing — the lowered copy can never equal that listed key, so this variant can never claim its dial button/badge (the other two keys are lowercase and unaffected).
- **Feasibility note:** not implementable as-is (no enemy targeting); flag for the user.

### El Syf
- **Marker / key:** `el_syf` — `wh_dlc05_weapon_abilities_el_syf` (entry 313, source line 1467)
- **Mod's current logic:** trigger `melee_unwavering` — fires when the owner is in melee, cast on self.
- **What the game declares:** a Hex aimed at **one enemy unit within 200 m, restricted to commander-class targets** (`unit_is_not_commander_class` invalid-target flag) — Speed −45%, Melee Defence −40, Physical Resistance −20 for 24 s.
- **Why it does not make sense:** it must be aimed at an enemy character; the mod cannot aim it and self is not a legal target (and would not be commander-class either).
- **Feasibility note:** not implementable as-is — enemy targeting does not exist in the mod; flag for the user.

### Entangle
- **Marker / key:** `entangle` — `wh2_dlc10_character_abilities_entangle` (entry 318, source line 1487)
- **Mod's current logic:** trigger `melee_unwavering` — fires when the owner is in melee, cast on self.
- **What the game declares:** an area Hex placed on **enemy ground** (`target_ground=true`, 15 m area at up to 100 m; flying units invalid targets) — Cannot Move + Fire Weakness for 15 s, ×2 uses.
- **Why it does not make sense:** it must be aimed at a spot of ground under the enemy; the mod cannot place it and self is not a legal target — the snare can never catch the enemy it is aimed at.
- **Feasibility note:** not implementable as-is (enemy-ground aiming); flag for the user.

### Eternal Gaze
- **Marker / key:** `gaze_of_usirian` — `wh3_dlc29_lord_abilities_gaze_of_usirian` (entry 320, source line 1495)
- **Mod's current logic:** trigger `melee_unwavering` — fires when the owner is in melee, cast on self.
- **What the game declares:** a morale Hex aimed at **one enemy unit** (100 m intercept; undead invalid targets) — inflicts Terror and drains vigour for 15 s.
- **Why it does not make sense:** a targeted enemy terror hex; the mod cannot aim it and self is not a legal target, so the declared effect cannot be delivered.
- **Feasibility note:** not implementable as-is (enemy targeting); flag for the user.

### Fear of Aramar
- **Marker / key:** `fear_of_aramar` — `wh2_dlc10_item_abilities_fear_of_aramar` (entry 324, source line 1511)
- **Mod's current logic:** trigger `melee_unwavering` — fires when the owner is in melee, cast on self.
- **What the game declares:** a morale Hex aimed at **one enemy unit** (200 m intercept) — Leadership −24 for 47 s; one use.
- **Why it does not make sense:** an aimed enemy leadership debuff; self-casting it is not a legal target and the mod cannot aim at the enemy.
- **Feasibility note:** not implementable as-is (enemy targeting); flag for the user.

### Fecund Rebirth
- **Marker / key:** `mark_of_the_monster` — `wh3_dlc29_character_active_mark_of_the_monster` (entry 326, source line 1519)
- **Mod's current logic:** trigger `melee_unwavering` — fires when the owner is in melee, cast on self.
- **What the game declares:** a Hex aimed at **one large single-entity enemy** (`unit_is_not_large` / `unit_is_not_single_entity` invalid-target flags; 200 m intercept) — 38 Damage/s, −50% Speed/Charge Speed, blocks healing, 32 s.
- **Why it does not make sense:** it must be aimed at an enemy monster; the mod cannot aim it and self is not a legal target (nor a valid one — the owner need not be a large single entity).
- **Feasibility note:** not implementable as-is — enemy targeting does not exist in the mod; flag for the user.

### Fermented Fungi
- **Marker / key:** `fermented_fungi` — `wh2_dlc15_lord_abilities_fermented_fungi` (entry 327, source line 1523)
- **Mod's current logic:** trigger `melee_unwavering` — fires when the owner is in melee, cast on self.
- **What the game declares:** a Hex aimed at **one enemy unit** (75 m intercept) — Melee Defence −24 and Rampage! for 15 s, ×3 uses.
- **Why it does not make sense:** an aimed single-enemy debuff (the gas is "wafted towards the enemy"); the mod cannot aim it and self is not a legal target.
- **Feasibility note:** not implementable as-is (enemy targeting); flag for the user.

### Frenzied Challenge
- **Marker / key:** `frenzied_challenge` — `wh3_dlc27_qb_unit_abilities_frenzied_challenge` (entry 333, source line 1547)
- **Mod's current logic:** trigger `melee_unwavering` — fires when the owner is in melee, cast on self.
- **What the game declares:** a Hex aimed at **one enemy unit** (150 m intercept) — Speed +25%, Melee Defence −24 and Rampage! for 15 s.
- **Why it does not make sense:** a targeted enemy challenge-hex; self is not a legal target and the mod cannot aim it.
- **Feasibility note:** not implementable as-is (enemy targeting); flag for the user.

### Frost Shard Glaive
- **Marker / key:** `frost_shard_glaive` — `wh3_main_weapon_abilities_frost_shard_glaive` (entry 334, source line 1551)
- **Mod's current logic:** trigger `melee_unwavering` — fires when the owner is in melee, cast on self.
- **What the game declares:** a Hex aimed at **one enemy unit** (50 m intercept; `range=0` with a single-target count — the specs describe a picked enemy, not a self-centred area) — Speed −45%, Melee Defence −40 for 30 s.
- **Why it does not make sense:** it must be aimed at an enemy; the mod cannot aim it and self is not a legal target — the "cold, hard promise of sharp slaughter" never reaches a victim.
- **Feasibility note:** not implementable as-is (enemy targeting); flag for the user.

### Gaze of Fate
- **Marker / key:** `gaze_of_fate` — `wh3_main_lord_abilities_gaze_of_fate` (entry 336, source line 1559)
- **Mod's current logic:** trigger `melee_unwavering` — fires when the owner is in melee, cast on self.
- **What the game declares:** a Hex aimed at **one enemy unit** (100 m intercept) — Melee Attack −40 and Cannot Move ("freezes the foe where they stand") for 14 s, ×3 uses.
- **Why it does not make sense:** a targeted enemy freeze hex; the mod cannot aim it and self is not a legal target.
- **Feasibility note:** not implementable as-is (enemy targeting); flag for the user.

### Get 'Em!
- **Marker / key:** `get_em` — `wh3_dlc25_character_abilities_get_em` (entry 337, source line 1563)
- **Mod's current logic:** trigger `melee_unwavering` — fires when the owner is in melee, cast on self.
- **What the game declares:** an area Hex placed on **enemy ground** (`target_ground=true`, 35 m area at up to 100 m) — Cannot Move for 11 s.
- **Why it does not make sense:** a ground-placed enemy hex; the mod cannot aim or place it and self is not a legal target — the "Get 'Em!" order is issued against the wrong side.
- **Feasibility note:** not implementable as-is (enemy-ground aiming); flag for the user.

### Gilellion's Soulnetter
- **Marker / key:** `soulnetter` — `wh3_main_weapon_abilities_soulnetter` (entry 339, source line 1571)
- **Mod's current logic:** trigger `melee_unwavering` — fires when the owner is in melee, cast on self.
- **What the game declares:** a Hex aimed at **one enemy unit** (50 m intercept) — Cannot Move for 26 s ("traps its victims in immortal servitude").
- **Why it does not make sense:** a targeted single-enemy binding hex; the mod cannot aim it and self is not a legal target.
- **Feasibility note:** not implementable as-is (enemy targeting); flag for the user.

### Glory Seeker
- **Marker / key:** `glory_seeker` — `wh3_dlc29_hero_active_glory_seeker` (entry 341, source line 1579)
- **Mod's current logic:** trigger `melee_unwavering` — fires when the owner is in melee, cast on self.
- **What the game declares:** a Hex aimed at **one enemy unit within 100 m, restricted to commander-class targets** (`unit_is_not_commander_class` invalid-target flag) — Melee Defence −24, healing blocked, Cannot Move for 24 s.
- **Why it does not make sense:** it must be aimed at an enemy character; the mod cannot aim it and self is not a legal (or commander-class) target.
- **Feasibility note:** not implementable as-is — enemy targeting does not exist in the mod; flag for the user.

### Glory Seeker Upgraded
- **Marker / key:** `glory_seeker_upgraded` — `wh3_dlc29_hero_active_glory_seeker_upgraded` (entry 342, source line 1583)
- **Mod's current logic:** trigger `melee_unwavering` — fires when the owner is in melee, cast on self.
- **What the game declares:** the upgraded version of the same Hex at **one enemy commander-class unit** (100 m intercept) — Melee Defence −36, healing blocked, Cannot Move for 36 s.
- **Why it does not make sense:** same target mismatch as the base key — a targeted enemy-character hex under a self-cast trigger.
- **Feasibility note:** not implementable as-is (enemy targeting); flag for the user.

### Grut's Sickle
- **Marker / key:** `gruts_sickle` — `wh3_main_item_abilities_gruts_sickle` (entry 343, source line 1587)
- **Mod's current logic:** trigger `melee_unwavering` — fires when the owner is in melee, cast on self.
- **What the game declares:** an Augment of the Winds that may target only **a friendly unit** (`target_friends=true`, `target_self=false`, `affect_self=false`, one unit, 100 m) — Power Recharge +80% and Reserves +0.4/s to the chosen ally, at a health cost, ×3 uses.
- **Why it does not make sense:** the ability's target set is a friendly unit, and the caster is not among the legal targets (self-targeting is off) — so the self-cast cannot deliver the winds buff it declares.
- **Feasibility note:** friendly units are readable and an ally picker could carry it; as written the self-cast is the wrong target; flag for the user.

### Headhunt
- **Marker / key:** `headhunt` — `wh3_dlc26_character_abilities_headhunt` (entry 348, source line 1607)
- **Mod's current logic:** trigger `melee_unwavering` — fires when the owner is in melee, cast on self.
- **What the game declares:** a Hex aimed at **one enemy unit within 150 m, restricted to commander-class targets** (`unit_is_not_commander_class` invalid-target flag) — Melee Defence −40 and Missile Resistance −20 for 31 s.
- **Why it does not make sense:** it must be aimed at an enemy character; the mod cannot aim it and self is not a legal (or commander-class) target.
- **Feasibility note:** not implementable as-is — enemy targeting does not exist in the mod; flag for the user.

## CLEAN

- book_of_arkhan (292)
- book_of_hoeth (293)
- call_of_violence (296)
- cascading_fire_cloak (297)
- channelling_staff (299)
- charmed_shield (300)
- cold_blooded (301)
- crown_of_command (302)
- dark_fortune (306)
- doom_lord (311)
- earthing_rod (312)
- elixir_of_might (314)
- embers_of_the_phoenix (315)
- ballistic_enchantment (316)
- enhanced_skavenbrew (317)
- entrenchment (319)
- eternal_vigour (321)
- extra_ingredients (322)
- favoured_by_the_matriarch (323)
- fearsome_roar (325)
- fight_or_die (328)
- fistful_of_laurels (329)
- flesh_to_stone (330)
- focus_instincts (331)
- forbidden_rod (332)
- funnel_of_flame (335)
- get_back_ere (338)
- glacial_defence (340)
- guttural_roar (344)
- hagtree_fetish (345)
- hail_of_fire (346)
- harmonic_convergence (347)
