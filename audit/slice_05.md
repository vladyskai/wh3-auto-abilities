# WH3 ability audit — slice 05 (entries 233–290)

Source of truth: `C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua` (ABILITIES table, entries 233–290 in source order, read from the live file 2026-10-09).
Judged against the game's own data: `unit_spec_abil.tsv` (targeting / range / intercept / use flags), `phase_junc.tsv` + `phases.tsv` (who each phase affects, effect type, stat/damage/heal rows, attributes), the uieff bullets, and the invalid-target/invalid-usage flags.
Counts: entries audited 58 · flagged 15 · clean 43.
Note on classification: enemy-effect area hexes with no `target_*` flags and `target_intercept_range = 0` (nothing to aim; same shape as the field-verified self-centred auras) are treated as caster-centred activations, where a self-cast is the native form; the flagged enemy abilities are the ones the data actually marks as aimed at enemies (`target_enemies = true`).

## FLAGGED

### 1. Orcs are da Best! — entry 238, marker `orcs_are_da_best`, key `wh3_dlc26_character_abilities_orcs_are_da_best`
- Current logic: trigger `melee_unwavering` (in melee, not routing, not wavering) → plain self-cast (`perform_special_ability(key, unit)`; no cast_target is set).
- What the game declares: a single-FRIENDLY-unit augment — `target_friends = true`, `num_effected_friendly_units = 1`, `target_self = false`, `affect_self = false` (intercept 150 m; +24 melee attack, ×1.5 damage for 27 s); its phase is friends-only (`self = false`).
- Why it makes no sense: the cast lands on the owner, which the data excludes both as a target and as an affected unit — the buff never reaches the friendly unit, and the questionnaire's own note ("cast on self for now, nearest-ally picker later") confirms the ally is the intended recipient.
- Feasibility: not implementable as written (self-cast cannot deliver it), but implementable overall — friendly units are fully readable and the ally-target cast pattern already exists (FOURTH.cast_target + drift re-check, the blood-sacrifice shape); it needs an ally picker.

### 2. Overseer of the Unseen — entry 239, marker `overseer_of_the_unseen`, key `wh3_dlc29_hero_active_overseer_of_the_unseen`
- Current logic: trigger `melee_unwavering` → self-cast.
- What the game declares: one friendly unit (`target_friends = true`, `num_effected_friendly_units = 1`, `target_self = false`), `only_affect_target = true`; invalid targets `unit_is_commander_class` and `unit_is_large` (+40 melee attack, cannot die, unbreakable for 44 s). In other words: cast on a non-commander, non-large friendly unit.
- Why it makes no sense: the owner is a hero (commander class) — as the cast target it is an INVALID target under the db's own invalid-target flags, so the intended foot-unit recipient never gets the effect and the self-cast has no declared target.
- Feasibility: implementable via an ally picker over readable friendly units, filtering by `unit:type()` (the land-units key the mod already reads) for the commander/large exclusions; not as currently written.

### 3. Star of Avelorn — entry 249, marker `star_of_avelorn`, key `wh2_dlc10_item_abilities_star_of_avelorn`
- Current logic: trigger `ushoran_health` (own health ≤ 75%) → self-cast through the ordinary unit form.
- What the game declares: a GROUND-targeted group heal — `target_ground = true`, `target_ground_under_allies = true`, `target_self = false` (heals up to 3 friendly units in a 15 m area, 27 s, ×2 uses); the project's own record for it says "cast at own feet (existing ground-cast path)".
- Why it makes no sense: the db gives this ability no self target — the cast shape the game declares is the position form, not a unit target; the mod's `ground_keys` list omits this key, so what actually fires is the unit-target self-cast, which is not this ability's declared cast mode.
- Feasibility: the ground path already exists (`perform_special_ability_ground` at the caster's own position — tacticians_stand_your_ground rides it); adding this key is the concrete fix. The health-gated heal trigger itself is fine.

### 4. "Stay Here, I'll Get Help!" — entry 250, marker `stay_here_ill_get_help`, key `wh2_dlc09_character_abilities_stay_here_ill_get_help`
- Current logic: trigger `wavering_ally_range` — picks the closest wavering, non-routing ally within the conservative 25 m and re-checks the gap before firing — but the cast itself stays ON SELF (its own log line reads "self-cast"); the picked ally is never passed as the cast target.
- What the game declares: friend/ground/self targeting (intercept 60 m); its morale phase affects FRIENDS only (`self = false`, +16 morale, 35 m) while a second phase grants the caster stalk/unspottable; and `invalid_usage: engaged_in_melee` (it cannot be used while the caster is engaged in melee).
- Why it makes no sense: the user-approved criterion and the tracker row say "cast on that ally" — the ally is selected, yet the cast does not use it; the self-anchor only reaches the ally through the friends-phase area, which is not the declared ally-targeted cast, and the evaluator never gates on the engaged-in-melee usage restriction.
- Feasibility: the ally is already picked and range-checked (FOURTH.wa_ally); passing it as the cast target is the existing blood-sacrifice pattern — implementable. Attempts while the caster is in melee will be engine-refused and simply feed the cooldown hold.

### 5. Accusation — entry 263, marker `accusation`, key `wh_main_hero_abilities_accusation`
- Current logic: trigger `melee_unwavering` → self-cast.
- What the game declares: a hex aimed at ONE ENEMY UNIT — `target_enemies = true`, `num_effected_enemy_units = 1`, intercept 75 m (negative phase: −30 armour, −24 melee defence, −20 missile/physical resist, 35 s).
- Why it makes no sense: the debuff's target is an enemy unit; a self-cast cannot deliver it — the mod casts at the only unit it can reach (its own), which is not a target of this ability.
- Feasibility: NOT implementable as-is — there is no enemy unit read (no card, no id, no health) and enemy-targeted casts cannot be aimed by the mod; the "cast at the enemy it is fighting" idea recorded for it cannot be built with the available reads.

### 6. Acquiescence — entry 264, marker `acquiescence`, key `wh3_dlc27_spell_bound_acquiescence`
- Current logic: trigger `melee_unwavering` → self-cast.
- What the game declares: a hex aimed at one enemy unit — `target_enemies = true`, `num_effected_enemy_units = 1`, intercept 200 m (×0.75 speed, −24 melee defence, 25 s, ×2 uses, wind-up 1 s, spell-bound).
- Why it makes no sense: enemy-targeted hex cast on self — wrong target class on every axis.
- Feasibility: NOT implementable as-is (no enemy reads; enemy casts cannot be aimed by the mod).

### 7. Amulet of Pha-Stah — entry 271, marker `amulet_of_phastah`, key `wh2_dlc09_item_abilities_amulet_of_phastah`
- Current logic: trigger `melee_unwavering` → self-cast.
- What the game declares: an area hex aimed at ENEMY GROUND — `target_enemies = true` AND `target_ground = true`, `num_effected_enemy_units = -1`, intercept 100 m, 55 m area (−30 armour, −48% missile block, 22 s).
- Why it makes no sense: the cast is at the owner, not at enemy ground; nothing in the mod places it where the db says it must go.
- Feasibility: NOT implementable as-is — no enemy reads and no enemy-position ground target; even the mod's ground path (own position only) is not what this ability declares.

### 8. Apocalyptic Charge — entry 272, marker `apocalyptic_charge`, key `wh_pro04_unit_abilities_apocalyptic_charge`
- Current logic: trigger `melee_unwavering` → self-cast.
- What the game declares: a charge effect — self-centred 35 m area with ×1.1 charge speed and ×1.2 charge bonus for 30 s (`ai_usage = aoe_centred_on_self`, `affect_self = true`). The cast target (self) is correct; the TRIGGER is the problem.
- Why it makes no sense: a charge effect should involve charging — the trigger only fires once the unit is already in melee, after the charge bonus has been spent; the charge window is deliberately excluded even though the mod carries charge detectors.
- Feasibility: implementable — ride `charge_or_melee` (or `charge_only`), which uses the existing `measure_charge` detector; no new reads needed.

### 9. Armour of Caledor — entry 274, marker `armour_of_caledor`, key `wh2_dlc15_item_abilities_armour_of_caledor`
- Current logic: trigger `melee_unwavering` → self-cast.
- What the game declares: a self regeneration — heals 1.6%/s for 20 s (≈32% max) with `cant_move = true`, ×3 uses (augment_spellcasting).
- Why it makes no sense: a heal should not need melee — the regeneration is gated behind being in melee, so it only ever fires after the unit is already engaged; a heal of this kind is usable before/during trouble regardless of engagement.
- Feasibility: implementable — self-cast target is fine; the `HealthPercent` read (already used by the ushoran_health family) would fit a regeneration item if a health gate is wanted.

### 10. Assassin's Trophy — entry 276, marker `assassins_trophy`, key `wh2_main_character_abilities_assassins_trophy`
- Current logic: trigger `melee_unwavering` → self-cast.
- What the game declares: a hex aimed at one enemy unit — `target_enemies = true`, intercept 150 m, `invalid_target: unit_is_not_commander_class` (i.e. the target must be an enemy commander/character-class unit; −24 melee attack and defence, 29 s).
- Why it makes no sense: enemy-targeted hex (and specifically an enemy-character hex) cast on self.
- Feasibility: NOT implementable as-is — no enemy unit reads; an ability that must be aimed at a specific enemy is not buildable with the available reads.

### 11. Bastet — entry 281, marker `bastet`, key `wh3_dlc29_lord_abilities_bastet`
- Current logic: trigger `melee_unwavering` → self-cast.
- What the game declares: a hex aimed at one enemy unit — `target_enemies = true`, intercept 100 m (−60 armour, −40 melee defence, 19 s).
- Why it makes no sense: enemy-targeted hex cast on self; the intended "cast at the enemy it is fighting" is neither implemented nor implementable.
- Feasibility: NOT implementable as-is (no enemy reads; enemy casts cannot be aimed by the mod).

### 12. Bitter Sting — entry 282, marker `bitter_sting`, key `wh3_dlc27_qb_unit_abilities_bitter_sting`
- Current logic: trigger `melee_unwavering` → self-cast.
- What the game declares: a hex aimed at one enemy unit — `target_enemies = true`, intercept 30 m (−24 melee attack and defence; `cant_run` and `flying` negative attributes; 30 s).
- Why it makes no sense: enemy-targeted hex cast on self.
- Feasibility: NOT implementable as-is (no enemy reads; enemy casts cannot be aimed by the mod).

### 13. Blade of Setep — entry 285, marker `blade_of_setep`, key `wh2_dlc09_weapon_abilities_blade_of_setep`
- Current logic: trigger `melee_unwavering` → self-cast.
- What the game declares: a hex aimed at one enemy unit — `target_enemies = true`, intercept 100 m (−30 armour, −20 physical resist, 44 s).
- Why it makes no sense: enemy-targeted hex cast on self.
- Feasibility: NOT implementable as-is (no enemy reads; enemy casts cannot be aimed by the mod).

### 14. Blight Swarm — entry 288, marker `blight_swarm`, key `wh3_main_lord_abilities_blight_swarm`
- Current logic: trigger `melee_unwavering` → self-cast.
- What the game declares: a chain hex — `target_enemies = true`, `num_effected_enemy_units = 5`, intercept 200 m, spreads to enemies within the spread range of affected units, −20 melee defence, 20 s, ×4 uses.
- Why it makes no sense: it must be aimed at enemy units (up to five, chained); a self-cast cannot start the chain.
- Feasibility: NOT implementable as-is (no enemy reads; enemy casts cannot be aimed by the mod).

### 15. Bloody Onslaught — entry 290, marker `bloody_onslaught`, key `wh3_dlc26_character_abilities_bloody_onslaught`
- Current logic: trigger `melee_unwavering` → self-cast.
- What the game declares: a hex aimed at one enemy unit — `target_enemies = true`, intercept 75 m (−30 armour, −24 melee defence, 38 s; its text: "towards the heart of every army: its leader").
- Why it makes no sense: enemy-targeted hex cast on self.
- Feasibility: NOT implementable as-is (no enemy reads; enemy casts cannot be aimed by the mod).

## CLEAN

Confident yes (43): marker — entry number.

1. `master_of_alchemy_poison` — 233
2. `master_rune_of_oath_and_steel` — 234
3. `master_rune_of_speed` — 235
4. `offense_prayer` — 236
5. `okkams_mindrazor` — 237
6. `primeval_roar` — 240
7. `protection_prayer` — 241
8. `rune_of_doom` — 242
9. `rune_of_oath_and_steel` — 243
10. `rune_of_speed` — 244
11. `sausage_busta` — 245
12. `shield_of_the_old_ones` — 246
13. `slayer_for_chaos` — 247
14. `spite_of_da_bad_moon` — 248
15. `supreme_shield_of_the_old_ones` — 251
16. `talisman_of_loec` — 252
17. `the_liber_mortis` — 253
18. `the_shadows_coil` — 254
19. `unstoppable_choppas` — 255
20. `vial_of_troll_blood` — 256
21. `warpstone_addiction` — 257
22. `warrior_familiar` — 258
23. `winters_chill` — 259
24. `witchbrew` — 260
25. `worlds_edge_armour` — 261
26. `znarkharjas_ward` — 262
27. `aken_seth_the_staff_of_pain` — 265
28. `alchemists_elixir_of_iron_skin` — 266
29. `alchemists_elixir_of_puissance` — 267
30. `alchemists_elixir_of_venom` — 268
31. `all_hands_hoay` — 269
32. `amulet_of_itzl` — 270
33. `magic_prayer` — 273
34. `armour_of_the_burrows` — 275
35. `aura_of_inertia` — 277
36. `avast_ye` — 278
37. `axe_of_men` — 279
38. `barbed_knuckle_boxing` — 280
39. `black_periapt` — 283
40. `black_staff` — 284
41. `blessed_helm_of_the_oblast` — 286
42. `blight_of_terrors` — 287
43. `blood_omens` — 289
