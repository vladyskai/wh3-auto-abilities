# Ability logic audit — slice 8 (entries 407–464, source order)

Counts: **58 audited · 21 flagged · 37 clean**.

Audited: `ABILITIES` entries 407–464 of `C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua`, in source order (`pilgrimage_of_skulls` … `the_dark_master`; one database key per entry, 58 keys).
Game data: the extracted game tables `%LOCALAPPDATA%\Temp\wh3\` and `%LOCALAPPDATA%\Temp\wh3\uieff\` — `unit_spec_abil.tsv` (targeting/engine flags), `unit_abilities.tsv` (type), `phase_junc.tsv` + `phases.tsv` + `special_ability_phase_stat_effects.tsv` / `phase_attribute_effects.tsv` (the real effect phases), and the loc tables for names and effect bullets; the tracker rows for all 58 keys were cross-checked.
Engine context (established, not re-litigated): only friendly units are readable; there is no enemy-unit read (no card / id / health), no per-unit firing read and no per-unit cooldown read; enemy-targeted casts cannot be aimed by the mod. Every entry in this slice rides the shared `melee_unwavering` evaluator — fires when the unit is in melee, not routing and (fail-open) not wavering — and casts **on self** through the default `perform_special_ability(key, unit)` call (no evaluator in this slice writes `cast_target`, and none of the 58 keys is a ground key). So the whole slice was judged against one logic shape: **in-melee self-cast**.

## FLAGGED

### Plague of Rust
- **Marker / key:** `plague_of_rust` — `wh3_main_spell_bound_plague_of_rust` (entry 408, source line 1848)
- **Mod's current logic:** trigger `melee_unwavering`; fires while in melee and casts on **self** (default self-target call).
- **What the game declares:** a Hex (`wh_type_hex`) aimed at **one enemy unit** (`target_enemies=true`, `num_effected_enemy_units=1`, cast range 200 m): −30 armour for 44 s; 2 uses, 60 s recharge. The tracker's own proposal for this row: "While the unit has an enemy in its sights: fire at it."
- **Why it makes no sense:** the cast must be aimed at an enemy unit and the mod aims it at the caster; the −30 armour hex can never land on an enemy (if the engine accepted the self-target, it would debuff the caster's own unit).
- **Feasibility note:** not implementable as-is — there is no enemy-unit read and enemy-targeted casts cannot be aimed (established engine limit); the tracker marks comparable rows `excluded (impossible: no enemy-unit read)`.

### Power Siphon
- **Marker / key:** `power_siphon` — `wh2_dlc11_lord_abilities_power_siphon` (entry 414, source line 1872)
- **Mod's current logic:** trigger `melee_unwavering`; in-melee self-cast.
- **What the game declares:** a Hex aimed at **one enemy unit** (`target_enemies=true`, cast range 100 m) — a caster-debuff that raises the target's ability recharge (+15 s) and fatigues it, for 30 s; ×4 uses, 60 s recharge.
- **Why it makes no sense:** it is a hex that must be aimed at an enemy caster, and the mod casts it on itself; the drain/slow effect can never be delivered to the intended target.
- **Feasibility note:** not implementable as-is — no enemy-unit read exists and enemy-targeted casts cannot be aimed; comparable rows are tracked as `excluded (impossible: no enemy-unit read)`.

### Prey of Anath Raema
- **Marker / key:** `prey_of_anath_raema` — `wh_dlc05_character_abilities_prey_of_anath_raema` (entry 417, source line 1884)
- **Mod's current logic:** trigger `melee_unwavering`; in-melee self-cast.
- **What the game declares:** a Hex aimed at **one enemy unit** (`target_enemies=true`, cast range 100 m): −20 missile resistance and held in place (`cant_move`) for 16 s; ×3 uses, 90 s recharge. The tracker's proposal: "When in melee with a current target: cast at the enemy it is fighting."
- **Why it makes no sense:** the debuff must be aimed at the enemy being fought, and the mod casts it on the caster; the −20 missile resistance never reaches an enemy.
- **Feasibility note:** not implementable as-is — the enemy-unit read needed to aim the cast does not exist (established engine limit).

### Prey of the Blood God
- **Marker / key:** `prey_of_the_blood_god` — `wh3_pro12_hero_abilities_prey_of_the_blood_god` (entry 418, source line 1888)
- **Mod's current logic:** trigger `melee_unwavering`; in-melee self-cast.
- **What the game declares:** a Hex aimed at **one enemy unit** (`target_enemies=true`, cast range 100 m): 33 damage/s to one entity plus `cant_move` for 22 s; ×3 uses, 120 s recharge. The tracker's proposal: "cast at the enemy it is fighting."
- **Why it makes no sense:** it is a targeted enemy damage/hold hex and the mod casts it on its own caster — the effect can never hit the intended victim.
- **Feasibility note:** not implementable as-is — no enemy-unit read; enemy casts cannot be aimed.

### Ravaging Swarm
- **Marker / key:** `dispatch_the_swarm_attack` — `wh3_dlc29_hero_active_dispatch_the_swarm_attack` (entry 421, source line 1900)
- **Mod's current logic:** trigger `melee_unwavering`; in-melee self-cast.
- **What the game declares:** a **chain Hex** on one enemy unit (`target_enemies=true`, up to five units affected, 30 m spread range, cast range 100 m): −24 melee defence for 24 s; 120 s recharge. The tracker's proposal: "cast at the enemy it is fighting."
- **Why it makes no sense:** the chain must start from an enemy unit; cast on the caster it cannot start, so neither the primary debuff nor the spread can occur.
- **Feasibility note:** not implementable as-is — no enemy-unit read; enemy casts cannot be aimed.

### Ravaging Swarm Upgraded
- **Marker / key:** `dispatch_the_swarm_attack_upgraded` — `wh3_dlc29_hero_active_dispatch_the_swarm_attack_upgraded` (entry 422, source line 1904)
- **Mod's current logic:** trigger `melee_unwavering`; in-melee self-cast.
- **What the game declares:** a **chain Hex** on one enemy unit (`target_enemies=true`, up to five, 30 m spread, cast range 100 m): −40 melee defence plus 4 damage/s to up to 10 entities for 24 s; 60 s recharge. Tracker proposal: "cast at the enemy it is fighting."
- **Why it makes no sense:** same as its base key — the chain hex needs an enemy starting unit and the mod casts it on itself.
- **Feasibility note:** not implementable as-is — no enemy-unit read; enemy casts cannot be aimed.

### Reanimate Upgraded
- **Marker / key:** `tomb_king_rally_upgraded` — `wh2_dlc09_character_abilities_tomb_king_rally_upgraded` (entry 424, source line 1912)
- **Mod's current logic:** trigger `melee_unwavering`; fires only while in melee and only while the unit is **not** wavering; self-cast (self-centred aura).
- **What the game declares:** a self-centred area Augment (`area_of_augments`, range 35 m, affects self and allies) that for 10 s grants +16 leadership **and replenishes hit points** ("Replenishes hit points of combatants", `heal_amount=0.008`, `hp_change_frequency=1`); 90 s recharge. The tracker's proposal: "When morale falls to wavering: cast."
- **Why it makes no sense:** the hit-point replenish is a heal component gated behind melee contact (and suppressed while the unit is wavering), so it cannot respond when the unit or its friends are hurt outside melee — "a heal should not need melee". The project's own heal/replenish batch (36 entries) rides the ≤75%-health trigger with no melee gate; this row kept the melee gate.
- **Feasibility note:** the health read and the `ushoran_health` evaluator already ship (`HealthPercent`, ≤75%, no melee gate), so no new reads are needed; the morale part could stay melee-gated if a split is preferred.

### Rune of Slowness
- **Marker / key:** `rune_of_slowness` — `wh2_dlc17_rune_abilities_rune_of_slowness` (entry 429, source line 1932)
- **Mod's current logic:** trigger `melee_unwavering`; in-melee self-cast.
- **What the game declares:** a Hex aimed at **one enemy unit** (`target_enemies=true`, cast range 100 m): −45% speed and charge speed, −40% charge bonus for 30 s; 120 s recharge. Tracker proposal: "fire at it (enemy in sights)."
- **Why it makes no sense:** the slow must be aimed at an enemy unit and the mod casts it on the caster; an enemy is never slowed.
- **Feasibility note:** not implementable as-is — no enemy-unit read; enemy casts cannot be aimed.

### Sadistic Snare
- **Marker / key:** `sadistic_snare` — `wh3_dlc23_lord_abilities_sadistic_snare` (entry 431, source line 1940)
- **Mod's current logic:** trigger `melee_unwavering`; in-melee self-cast.
- **What the game declares:** a Hex aimed at one enemy unit **within 20 m** (`target_enemies=true`, cast range 20 m): −24 melee defence and `cant_move` for 33 s; ×2 uses, 120 s recharge. Tracker proposal: "cast at the enemy it is fighting."
- **Why it makes no sense:** the snare must catch an enemy unit (the game itself limits the cast range to 20 m) and the mod aims it at the caster.
- **Feasibility note:** not implementable as-is — no enemy-unit read; enemy casts cannot be aimed.

### Scroll of Leeching
- **Marker / key:** `scroll_of_leeching` — `wh_main_item_abilities_scroll_of_leeching` (entry 434, source line 1952)
- **Mod's current logic:** trigger `melee_unwavering`; in-melee self-cast.
- **What the game declares:** a Hex of the Winds aimed at **one enemy unit** (`target_enemies=true`, cast range 100 m): −0.4 Winds of Magic regen on the target for 44 s; ×1 use, 60 s recharge. Tracker proposal: "fire at it."
- **Why it makes no sense:** it must be aimed at an enemy (a caster to drain); cast on the caster it can never sap the intended target.
- **Feasibility note:** not implementable as-is — no enemy-unit read; enemy casts cannot be aimed.

### Shock Collar
- **Marker / key:** `shock_collar` — `wh2_dlc16_hero_abilities_shock_collar` (entry 439, source line 1972)
- **Mod's current logic:** trigger `melee_unwavering`; in-melee self-cast.
- **What the game declares:** an Augment for **one friendly unit** (`target_friends=true`, `target_self=false`, `num_effected_friendly_units=1`, cast at a friendly unit within 100 m): +24 melee attack, +16 leadership, immune to psychology for 24 s; 60 s recharge. The tracker's own proposal: "When morale falls to wavering: cast on the wavering friendly unit."
- **Why it makes no sense:** the effect is single-unit and aimed at another friendly unit; self is not a declared target for the cast, so casting it on the caster buffs the wrong unit (or is refused) — the intended buff never lands where the tracker's plan puts it.
- **Feasibility note:** feasible with existing reads — the mod already ships this exact ally-picker pattern for other triggers (`blood_sacrifice`: lowest-health in-range ally, conservative range, pre-cast range re-check) and uses a 25 m trigger radius against the game's 100 m cast range; no enemy reads involved.

### Silence the Prey
- **Marker / key:** `silence_the_prey` — `wh3_main_character_abilities_silence_the_prey` (entry 440, source line 1976)
- **Mod's current logic:** trigger `melee_unwavering`; in-melee self-cast.
- **What the game declares:** a Hex aimed at **one enemy unit** (`target_enemies=true`, cast range 100 m): raises the target's ability recharge by +30 s (a caster silence) for 30 s; ×4 uses, 60 s recharge. Tracker proposal: "fire at it."
- **Why it makes no sense:** the silence must be aimed at an enemy; the mod casts it on itself, where it can never suppress an enemy caster.
- **Feasibility note:** not implementable as-is — no enemy-unit read; enemy casts cannot be aimed.

### Spearfisher's Net
- **Marker / key:** `spearfishers_net` — `wh2_dlc11_lord_abilities_spearfishers_net` (entry 445, source line 1996)
- **Mod's current logic:** trigger `melee_unwavering`; in-melee self-cast.
- **What the game declares:** a Hex aimed at **one enemy unit** (`target_enemies=true`, cast range 100 m): −24 melee defence and `cant_move` for 18 s; ×3 uses, 90 s recharge. Tracker proposal: "cast at the enemy it is fighting."
- **Why it makes no sense:** the net must catch an enemy unit; cast on the caster the hold/debuff never lands on an enemy.
- **Feasibility note:** not implementable as-is — no enemy-unit read; enemy casts cannot be aimed.

### Spiderweb Attack
- **Marker / key:** `spider_web_attack` — `wh3_dlc26_character_abilities_spider_web_attack` (entry 447, source line 2004)
- **Mod's current logic:** trigger `melee_unwavering`; in-melee self-cast.
- **What the game declares:** a Hex aimed at **one enemy unit** within 50 m (`target_enemies=true`, cast range 50 m): immobilises the target (`cant_move`) for 18 s; ×2 uses, 120 s recharge. Tracker proposal: "cast at the enemy it is fighting."
- **Why it makes no sense:** the web must be aimed at an enemy unit; cast on the caster it can never immobilise an enemy.
- **Feasibility note:** not implementable as-is — no enemy-unit read; enemy casts cannot be aimed.

### Sword of Filth
- **Marker / key:** `sword_of_filth` — `wh3_dlc25_weapon_abilities_sword_of_filth` (entry 455, source line 2036)
- **Mod's current logic:** trigger `melee_unwavering`; in-melee self-cast.
- **What the game declares:** a **chain Hex** on one enemy unit (`target_enemies=true`, up to five units, cast range 35 m): −30 armour and −24 melee defence for 20 s; 120 s recharge. Tracker proposal: "fire at it."
- **Why it makes no sense:** the chain must start from an enemy unit; cast on the caster neither the primary debuff nor the chain can occur.
- **Feasibility note:** not implementable as-is — no enemy-unit read; enemy casts cannot be aimed.

### Tacticians, Rally!
- **Marker / key:** `tacticians_rally` — `wh3_dlc24_character_abilities_tacticians_rally` (entry 456, source line 2040)
- **Mod's current logic:** trigger `melee_unwavering`; casts on **self** through the normal unit-target call — the key is **not** in `FOURTH.ground_keys`.
- **What the game declares:** a friend- **and ground-targeted** area Augment (`target_friends=true`, `target_ground=true`, 35 m aura affecting self+allies, cast range 100 m): +16 leadership for 14 s; 60 s recharge. Its targeting shape is identical to `wh3_dlc24_character_abilities_tacticians_stand_your_ground`, which the mod routes through the ground form (`perform_special_ability_ground`) via `FOURTH.ground_keys`. Tracker proposal: "cast on the wavering friendly unit."
- **Why it makes no sense:** the game declares ground targeting, and the mod's own convention (the `ground_keys` map, built for exactly this friend+ground shape) sends the identically-shaped SYG key through the ground form while this key fires the unit-target form on self — the two can't both be right; the declared friend/ground target is ignored either way.
- **Feasibility note:** aligning it is a one-line addition to `FOURTH.ground_keys` (the ground-cast helper already ships), but the project's own comment says the ground path is API-documentation-backed rather than battle-proven — confirm in a live battle before trusting it.

### Taunt
- **Marker / key:** `taunt` — `wh2_dlc11_character_abilities_taunt` (entry 457, source line 2044)
- **Mod's current logic:** trigger `melee_unwavering`; in-melee self-cast.
- **What the game declares:** a Hex aimed at **one enemy unit** (`target_enemies=true`, cast range 100 m): −30 armour, −24 melee defence, −25% speed for 17 s; 60 s recharge. Tracker proposal: "cast at the enemy it is fighting."
- **Why it makes no sense:** the hex must be aimed at an enemy unit; casting it on the caster never taunts/debuffs the enemy it is meant for.
- **Feasibility note:** not implementable as-is — no enemy-unit read; enemy casts cannot be aimed.

### Tendrils of the Sea
- **Marker / key:** `tendrils_of_the_sea` — `wh3_dlc29_hero_active_tendrils_of_the_sea` (entry 458, source line 2048)
- **Mod's current logic:** trigger `melee_unwavering`; in-melee self-cast.
- **What the game declares:** a Hex aimed at **one enemy unit** (`target_enemies=true`, cast range 200 m): −60% speed, −20% mass and −40 melee attack for 24 s; 120 s recharge. Tracker proposal: "cast at the enemy it is fighting."
- **Why it makes no sense:** the slowing hex must be aimed at an enemy unit; the mod casts it on the caster.
- **Feasibility note:** not implementable as-is — no enemy-unit read; enemy casts cannot be aimed.

### The Averland Runefang
- **Marker / key:** `averland_runefang` — `wh2_dlc13_weapon_abilities_averland_runefang` (entry 460, source line 2056)
- **Mod's current logic:** trigger `melee_unwavering`; in-melee self-cast.
- **What the game declares:** a Hex aimed at **one enemy unit** (`target_enemies=true`, cast range 100 m): −40 melee attack and ×0.4 base weapon damage for 33 s; 120 s recharge. Tracker proposal: "cast at the enemy it is fighting."
- **Why it makes no sense:** the weapon's hex must be aimed at an enemy unit; casting it on the caster leaves the intended enemy untouched (and may weaken the caster if the engine accepts the self-target).
- **Feasibility note:** not implementable as-is — no enemy-unit read; enemy casts cannot be aimed.

### The Black Tongue
- **Marker / key:** `the_black_tongue` — `wh3_dlc27_character_abilities_the_black_tongue` (entry 462, source line 2064)
- **Mod's current logic:** trigger `melee_unwavering`; in-melee self-cast.
- **What the game declares:** a Hex aimed at **one enemy unit** (`target_enemies=true`, cast range 200 m): silences the target for 21 s; ×2 uses, 120 s recharge. Tracker proposal: "cast at the enemy it is fighting."
- **Why it makes no sense:** the silence must be aimed at an enemy unit; cast on the caster it cannot silence the enemy it is meant for.
- **Feasibility note:** not implementable as-is — no enemy-unit read; enemy casts cannot be aimed.

### The Dark Master
- **Marker / key:** `the_dark_master` — `wh3_main_lord_abilities_the_dark_master` (entry 464, source line 2072)
- **Mod's current logic:** trigger `melee_unwavering`; in-melee self-cast.
- **What the game declares:** a Hex aimed at **one enemy unit** (`target_enemies=true`, cast range 100 m): −40 melee attack for 33 s; 90 s recharge. Tracker proposal: "cast at the enemy it is fighting."
- **Why it makes no sense:** the −40 melee attack hex must be aimed at an enemy unit; the mod casts it on the caster.
- **Feasibility note:** not implementable as-is — no enemy-unit read; enemy casts cannot be aimed.

## CLEAN

1. pilgrimage_of_skulls (407)
2. plaque_of_dominion (409)
3. potion_of_farsight (410)
4. potion_of_foolhardiness (411)
5. potion_of_speed (412)
6. power_familiar (413)
7. power_stone (415)
8. predatory_instincts (416)
9. prismatic_amplifier (419)
10. rally (420)
11. tomb_king_rally (423)
12. red_fury (425)
13. item_passive_rock_eye (426)
14. rune_of_breaking (427)
15. rune_of_negation (428)
16. rune_of_thungni (430)
17. sceptre_of_stability (432)
18. scroll_of_destiny (433)
19. scroll_of_shielding (435)
20. shield_of_chaqua (436)
21. dispatch_the_swarm_protect (437)
22. dispatch_the_swarm_protect_upgraded (438)
23. skavenbrew (441)
24. skjalandirs_fall (442)
25. skull_of_rarkos (443)
26. snowflake_pendant (444)
27. spell_wrought_sceptre (446)
28. staff_of_damnation (448)
29. staff_of_nagash (449)
30. staff_of_tomorrow (450)
31. staff_of_volans (451)
32. staff_of_wu_xing (452)
33. starwood_staff (453)
34. stave_of_avelorn (454)
35. terrorgheist_skull (459)
36. the_bane_shield (461)
37. the_chromatic_tome (463)
