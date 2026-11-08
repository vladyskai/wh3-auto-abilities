# WH3 auto-ability audit — consolidated report

**Scope:** all 579 entries of the `local ABILITIES = {` table in `C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua`, in source order (slice 01 = entries 1–58 … slice 10 = entries 523–579).

**Method:** every entry was judged on four questions against the game's own ability data (extracted db tables: `unit_spec_abil` targeting flags; `phase_junc` + `phases` effect phases and their stat/attribute rows; UI-effect bullets and loc text):

1. what the ability does and who it affects,
2. who the game declares as its legal targets,
3. whether the mod's trigger fits the effect,
4. whether the trigger is achievable with the mod's reads (friendly units readable; no enemy-unit read; ground cast at own position available; charge / health / morale reads exist).

Entries that fail (2), (3) or (4) — or that make the cast impossible as written — are flagged below. Every flagged entry ends with a blank **Your ruling:** line for your decision.

## Counts (all ten slices)

| Slice | Entries | Audited | Flagged | Clean |
|---|---:|---:|---:|---:|
| 01 | 1–58 | 58 | 0 | 58 |
| 02 | 59–116 | 58 | 0 | 58 |
| 03 | 117–174 | 58 | 1 | 57 |
| 04 | 175–232 | 58 | 20 | 38 |
| 05 | 233–290 | 58 | 15 | 43 |
| 06 | 291–348 | 58 | 26 | 32 |
| 07 | 349–406 | 58 | 36 | 22 |
| 08 | 407–464 | 58 | 21 | 37 |
| 09 | 465–522 | 58 | 32 | 26 |
| 10 | 523–579 | 57 | 10 | 47 |
| **Total** | **1–579** | **579** | **161** | **418** |

**Reconciliation: 161 flagged + 418 clean = 579 audited** (each slice's flagged + clean equals its audited count).

## Problem classes (the 161 flagged)

| Class | What it is | Flagged |
|---|---|---:|
| A | Enemy-aimed casts on self | 98 |
| B | Ally-targeted effects cast on self | 34 |
| C | Ground-targeted casts sent via the unit form | 11 |
| D | Heals or defensive effects gated behind melee | 3 |
| E | Charge-component abilities on melee-only triggers | 3 |
| F | Engine-refused self casts | 4 |
| G | Trigger fires in the wrong state | 6 |
| H | Effect does not fit the heal-family trigger | 2 |
| **Total** | | **161** |

---

## Your three examples

The audit independently reached these; they are listed first as you asked.

### Example 1 — Accusation — **FLAGGED** (Class A: enemy-aimed cast on self)

- **Key(s):** `wh_main_hero_abilities_accusation`  (slice 05, entry 263)
- **Current logic:** trigger `melee_unwavering` → self-cast.
- **Game declares:** a hex aimed at ONE ENEMY UNIT — `target_enemies = true`, `num_effected_enemy_units = 1`, intercept 75 m (negative phase: −30 armour, −24 melee defence, −20 missile/physical resist, 35 s).
- **Why it makes no sense:** the debuff's target is an enemy unit; a self-cast cannot deliver it — the mod casts at the only unit it can reach (its own), which is not a target of this ability.
- **Feasibility:** NOT implementable as-is — there is no enemy unit read (no card, no id, no health) and enemy-targeted casts cannot be aimed by the mod; the "cast at the enemy it is fighting" idea recorded for it cannot be built with the available reads.

**Your ruling:** ______________________________________________________________________________

### Example 2 — Amulet of Pha-Stah — **FLAGGED** (Class A: enemy-aimed cast on self; enemy ground)

- **Key(s):** `wh2_dlc09_item_abilities_amulet_of_phastah`  (slice 05, entry 271)
- **Current logic:** trigger `melee_unwavering` → self-cast.
- **Game declares:** an area hex aimed at ENEMY GROUND — `target_enemies = true` AND `target_ground = true`, `num_effected_enemy_units = -1`, intercept 100 m, 55 m area (−30 armour, −48% missile block, 22 s).
- **Why it makes no sense:** the cast is at the owner, not at enemy ground; nothing in the mod places it where the db says it must go.
- **Feasibility:** NOT implementable as-is — no enemy reads and no enemy-position ground target; even the mod's ground path (own position only) is not what this ability declares.

**Your ruling:** ______________________________________________________________________________

### Example 3 — Flesh to Stone — **NOT flagged (kept clean)**

- **Key(s):** `wh2_dlc16_spell_bound_flesh_to_stone`  (slice 06, entry 330)
- **Current logic:** trigger `melee_unwavering` → cast on self (the tracker note reads "cast on self for now (nearest-ally picker later)").
- **Game declares:** an augment whose declared targets include **self and friends** — `target_self = true`, `target_friends = true`, one friendly unit, 200 m intercept; its phase targets self + friends (`s=true,f=true`) and grants **+60 Physical Resistance for 19 s** ("transforms allies' mortal flesh into unbreakable rock, increasing tenfold their resistance to attack").
- **Why the audit passed it:** unlike the flagged ally-only rows (where `target_self = false` and the caster is excluded), self is a **legal target** for this ability and the phase includes the caster, so the self-cast delivers the declared defensive buff legally; the effect also fits the in-melee moment, and the trigger is achievable with existing reads. The "nearest-ally picker later" note is an optional enhancement, not a targeting error — so slice 06 did not flag it.

---

## Class A — Enemy-aimed casts on self (98 entries)

The game aims these at enemy units — single-target hexes and debuffs, chains, and enemy-ground area effects (some further restricted to commander-class, missile, large or single-entity victims). The mod fires them at the caster. There is no enemy-unit read (no card, id or health) and enemy-targeted casts cannot be aimed, so none of these can deliver its declared effect as written; the slices track comparable rows as `excluded (impossible: no enemy-unit read)`.

#### 263. Accusation  (slice 05)

- **Key(s):** `wh_main_hero_abilities_accusation`
- **Current logic:** trigger `melee_unwavering` → self-cast.
- **Game declares:** a hex aimed at ONE ENEMY UNIT — `target_enemies = true`, `num_effected_enemy_units = 1`, intercept 75 m (negative phase: −30 armour, −24 melee defence, −20 missile/physical resist, 35 s).
- **Why it makes no sense:** the debuff's target is an enemy unit; a self-cast cannot deliver it — the mod casts at the only unit it can reach (its own), which is not a target of this ability.
- **Feasibility:** NOT implementable as-is — there is no enemy unit read (no card, no id, no health) and enemy-targeted casts cannot be aimed by the mod; the "cast at the enemy it is fighting" idea recorded for it cannot be built with the available reads.

**Your ruling:** ______________________________________________________________________________


#### 264. Acquiescence  (slice 05)

- **Key(s):** `wh3_dlc27_spell_bound_acquiescence`
- **Current logic:** trigger `melee_unwavering` → self-cast.
- **Game declares:** a hex aimed at one enemy unit — `target_enemies = true`, `num_effected_enemy_units = 1`, intercept 200 m (×0.75 speed, −24 melee defence, 25 s, ×2 uses, wind-up 1 s, spell-bound).
- **Why it makes no sense:** enemy-targeted hex cast on self — wrong target class on every axis.
- **Feasibility:** NOT implementable as-is (no enemy reads; enemy casts cannot be aimed by the mod).

**Your ruling:** ______________________________________________________________________________


#### 271. Amulet of Pha-Stah  (slice 05)

- **Key(s):** `wh2_dlc09_item_abilities_amulet_of_phastah`
- **Current logic:** trigger `melee_unwavering` → self-cast.
- **Game declares:** an area hex aimed at ENEMY GROUND — `target_enemies = true` AND `target_ground = true`, `num_effected_enemy_units = -1`, intercept 100 m, 55 m area (−30 armour, −48% missile block, 22 s).
- **Why it makes no sense:** the cast is at the owner, not at enemy ground; nothing in the mod places it where the db says it must go.
- **Feasibility:** NOT implementable as-is — no enemy reads and no enemy-position ground target; even the mod's ground path (own position only) is not what this ability declares.

**Your ruling:** ______________________________________________________________________________


#### 276. Assassin's Trophy  (slice 05)

- **Key(s):** `wh2_main_character_abilities_assassins_trophy`
- **Current logic:** trigger `melee_unwavering` → self-cast.
- **Game declares:** a hex aimed at one enemy unit — `target_enemies = true`, intercept 150 m, `invalid_target: unit_is_not_commander_class` (i.e. the target must be an enemy commander/character-class unit; −24 melee attack and defence, 29 s).
- **Why it makes no sense:** enemy-targeted hex (and specifically an enemy-character hex) cast on self.
- **Feasibility:** NOT implementable as-is — no enemy unit reads; an ability that must be aimed at a specific enemy is not buildable with the available reads.

**Your ruling:** ______________________________________________________________________________


#### 281. Bastet  (slice 05)

- **Key(s):** `wh3_dlc29_lord_abilities_bastet`
- **Current logic:** trigger `melee_unwavering` → self-cast.
- **Game declares:** a hex aimed at one enemy unit — `target_enemies = true`, intercept 100 m (−60 armour, −40 melee defence, 19 s).
- **Why it makes no sense:** enemy-targeted hex cast on self; the intended "cast at the enemy it is fighting" is neither implemented nor implementable.
- **Feasibility:** NOT implementable as-is (no enemy reads; enemy casts cannot be aimed by the mod).

**Your ruling:** ______________________________________________________________________________


#### 282. Bitter Sting  (slice 05)

- **Key(s):** `wh3_dlc27_qb_unit_abilities_bitter_sting`
- **Current logic:** trigger `melee_unwavering` → self-cast.
- **Game declares:** a hex aimed at one enemy unit — `target_enemies = true`, intercept 30 m (−24 melee attack and defence; `cant_run` and `flying` negative attributes; 30 s).
- **Why it makes no sense:** enemy-targeted hex cast on self.
- **Feasibility:** NOT implementable as-is (no enemy reads; enemy casts cannot be aimed by the mod).

**Your ruling:** ______________________________________________________________________________


#### 285. Blade of Setep  (slice 05)

- **Key(s):** `wh2_dlc09_weapon_abilities_blade_of_setep`
- **Current logic:** trigger `melee_unwavering` → self-cast.
- **Game declares:** a hex aimed at one enemy unit — `target_enemies = true`, intercept 100 m (−30 armour, −20 physical resist, 44 s).
- **Why it makes no sense:** enemy-targeted hex cast on self.
- **Feasibility:** NOT implementable as-is (no enemy reads; enemy casts cannot be aimed by the mod).

**Your ruling:** ______________________________________________________________________________


#### 288. Blight Swarm  (slice 05)

- **Key(s):** `wh3_main_lord_abilities_blight_swarm`
- **Current logic:** trigger `melee_unwavering` → self-cast.
- **Game declares:** a chain hex — `target_enemies = true`, `num_effected_enemy_units = 5`, intercept 200 m, spreads to enemies within the spread range of affected units, −20 melee defence, 20 s, ×4 uses.
- **Why it makes no sense:** it must be aimed at enemy units (up to five, chained); a self-cast cannot start the chain.
- **Feasibility:** NOT implementable as-is (no enemy reads; enemy casts cannot be aimed by the mod).

**Your ruling:** ______________________________________________________________________________


#### 290. Bloody Onslaught  (slice 05)

- **Key(s):** `wh3_dlc26_character_abilities_bloody_onslaught`
- **Current logic:** trigger `melee_unwavering` → self-cast.
- **Game declares:** a hex aimed at one enemy unit — `target_enemies = true`, intercept 75 m (−30 armour, −24 melee defence, 38 s; its text: "towards the heart of every army: its leader").
- **Why it makes no sense:** enemy-targeted hex cast on self.
- **Feasibility:** NOT implementable as-is (no enemy reads; enemy casts cannot be aimed by the mod).

**Your ruling:** ______________________________________________________________________________


#### 294. Book of Secrets  (slice 06)

- **Key(s):** `wh3_dlc24_item_abilities_book_of_secrets`
- **Current logic:** trigger `melee_unwavering` — fires when the owner is in melee, cast on self.
- **Game declares:** a Hex (`wh_type_hex`) aimed at one enemy unit (`target_enemies=true`, `target_self=false`, `num_effected_enemy_units=1`, 100 m intercept) with three negative 20 s phases (Damage 10/s; −25% Speed + Fire Weakness; −24 Melee Attack/Defence), ×3 uses.
- **Why it makes no sense:** the cast must be aimed at an enemy and the mod cannot aim enemy-targeted casts (no enemy-unit read); a self-cast is not even a legal target for it, so the entry cannot deliver its declared debuff.
- **Feasibility:** not implementable as-is — enemy-targeting needs an enemy read/selection the mod does not have; flag for the user (leave to the player or exclude).

**Your ruling:** ______________________________________________________________________________


#### 298. Chalice of Dark Rain  (slice 06)

- **Key(s):** `wh_dlc03_item_abilities_chalice_of_dark_rain`
- **Current logic:** trigger `melee_unwavering` — fires when the owner is in melee, cast on self.
- **Game declares:** an area Hex placed on enemy ground (`target_enemies=true`, `target_ground=true`, 35 m area, 200 m range) — Accuracy −30 for 89 s to affected combatants.
- **Why it makes no sense:** it is a ground-placed enemy-area hex that must be aimed at a spot under the enemy; the mod cannot aim it (no enemy read, and it never fires targeted casts with a guessed target) and self is not a legal target.
- **Feasibility:** not implementable as-is — needs enemy/ground aiming the mod does not have; flag for the user.

**Your ruling:** ______________________________________________________________________________


#### 303. Cube of Darkness  (slice 06)

- **Key(s):** `wh2_main_item_abilities_cube_of_darkness`
- **Current logic:** trigger `melee_unwavering` — fires when the owner is in melee, cast on self.
- **Game declares:** a Hex of the Winds aimed at one enemy unit (100 m intercept) — Power Recharge −40% for 18 s (it drains the targeted enemy spellcaster's winds).
- **Why it makes no sense:** an aimed single-enemy hex; casting it on the owner is not a legal target and the mod cannot aim at the enemy caster it is designed to drain.
- **Feasibility:** not implementable as-is (no enemy targeting); flag for the user.

**Your ruling:** ______________________________________________________________________________


#### 304. Curse of Khsar  (slice 06)

- **Key(s):** `wh2_dlc09_character_abilities_curse_of_khsar`
- **Current logic:** trigger `melee_unwavering` — fires when the owner is in melee, cast on self.
- **Game declares:** an area Hex on enemy ground (`target_ground=true`, 35 m area at up to 100 m) — Armour −60 for 25 s; one use; and its own usage condition `health_above_50%` marks it usable only at ≤50% caster health.
- **Why it makes no sense:** it must be aimed at ground under the enemy (not aimable, self not a legal target), and the mod's trigger ignores the ability's own ≤50%-health usage condition entirely.
- **Feasibility:** not implementable as-is — enemy-ground aiming does not exist in the mod; flag for the user.

**Your ruling:** ______________________________________________________________________________


#### 309. Don't Even Try It  (slice 06)

- **Key(s):** `wh2_dlc15_lord_abilities_dont_even_try_it`
- **Current logic:** trigger `melee_unwavering` — fires when the owner is in melee, cast on self.
- **Game declares:** a direct-damage Hex at one enemy unit (100 m intercept) — 144 Damage every 2 s for 18 s, +15 s ability recharge on the victim, ×2 uses ("Strong vs a single combatant").
- **Why it makes no sense:** its entire payload is aimed at a single enemy; the mod cannot aim it and self is not a legal target, so the cast cannot land the damage it exists for.
- **Feasibility:** not implementable as-is (enemy targeting); flag for the user.

**Your ruling:** ______________________________________________________________________________


#### 310. Doom & Darkness  (slice 06)

- **Key(s):** `wh3_dlc25_spell_Bound_doom_and_darkness_gunnery_school`, `wh3_dlc27_spell_bound_runecaller_death_doom_and_darkness`, `wh_dlc08_spell_bound_death_doom_and_darkness`
- **Current logic:** trigger `melee_unwavering` — fires when the owner is in melee, cast on self.
- **Game declares:** a morale Hex aimed at one enemy unit (200 m intercept) — Leadership −16 for 36 s; ×2/×3 uses across the three keys.
- **Why it makes no sense:** an aimed single-enemy leadership debuff; the mod cannot aim enemy casts and self is not a legal target, so the entry cannot debuff the enemy it is designed for.
- **Feasibility:** not implementable as-is (no enemy targeting); flag for the user.
- **Also noted:** Key-claim defect (extra): the first key contains an uppercase `B` (`spell_Bound…`, the game's own spelling), but the mod's button-claim match lower-cases the engine key before comparing — the lowered copy can never equal that listed key, so this variant can never claim its dial button/badge (the other two keys are lowercase and unaffected).

**Your ruling:** ______________________________________________________________________________


#### 313. El Syf  (slice 06)

- **Key(s):** `wh_dlc05_weapon_abilities_el_syf`
- **Current logic:** trigger `melee_unwavering` — fires when the owner is in melee, cast on self.
- **Game declares:** a Hex aimed at one enemy unit within 200 m, restricted to commander-class targets (`unit_is_not_commander_class` invalid-target flag) — Speed −45%, Melee Defence −40, Physical Resistance −20 for 24 s.
- **Why it makes no sense:** it must be aimed at an enemy character; the mod cannot aim it and self is not a legal target (and would not be commander-class either).
- **Feasibility:** not implementable as-is — enemy targeting does not exist in the mod; flag for the user.

**Your ruling:** ______________________________________________________________________________


#### 318. Entangle  (slice 06)

- **Key(s):** `wh2_dlc10_character_abilities_entangle`
- **Current logic:** trigger `melee_unwavering` — fires when the owner is in melee, cast on self.
- **Game declares:** an area Hex placed on enemy ground (`target_ground=true`, 15 m area at up to 100 m; flying units invalid targets) — Cannot Move + Fire Weakness for 15 s, ×2 uses.
- **Why it makes no sense:** it must be aimed at a spot of ground under the enemy; the mod cannot place it and self is not a legal target — the snare can never catch the enemy it is aimed at.
- **Feasibility:** not implementable as-is (enemy-ground aiming); flag for the user.

**Your ruling:** ______________________________________________________________________________


#### 320. Eternal Gaze  (slice 06)

- **Key(s):** `wh3_dlc29_lord_abilities_gaze_of_usirian`
- **Current logic:** trigger `melee_unwavering` — fires when the owner is in melee, cast on self.
- **Game declares:** a morale Hex aimed at one enemy unit (100 m intercept; undead invalid targets) — inflicts Terror and drains vigour for 15 s.
- **Why it makes no sense:** a targeted enemy terror hex; the mod cannot aim it and self is not a legal target, so the declared effect cannot be delivered.
- **Feasibility:** not implementable as-is (enemy targeting); flag for the user.

**Your ruling:** ______________________________________________________________________________


#### 324. Fear of Aramar  (slice 06)

- **Key(s):** `wh2_dlc10_item_abilities_fear_of_aramar`
- **Current logic:** trigger `melee_unwavering` — fires when the owner is in melee, cast on self.
- **Game declares:** a morale Hex aimed at one enemy unit (200 m intercept) — Leadership −24 for 47 s; one use.
- **Why it makes no sense:** an aimed enemy leadership debuff; self-casting it is not a legal target and the mod cannot aim at the enemy.
- **Feasibility:** not implementable as-is (enemy targeting); flag for the user.

**Your ruling:** ______________________________________________________________________________


#### 326. Fecund Rebirth  (slice 06)

- **Key(s):** `wh3_dlc29_character_active_mark_of_the_monster`
- **Current logic:** trigger `melee_unwavering` — fires when the owner is in melee, cast on self.
- **Game declares:** a Hex aimed at one large single-entity enemy (`unit_is_not_large` / `unit_is_not_single_entity` invalid-target flags; 200 m intercept) — 38 Damage/s, −50% Speed/Charge Speed, blocks healing, 32 s.
- **Why it makes no sense:** it must be aimed at an enemy monster; the mod cannot aim it and self is not a legal target (nor a valid one — the owner need not be a large single entity).
- **Feasibility:** not implementable as-is — enemy targeting does not exist in the mod; flag for the user.

**Your ruling:** ______________________________________________________________________________


#### 327. Fermented Fungi  (slice 06)

- **Key(s):** `wh2_dlc15_lord_abilities_fermented_fungi`
- **Current logic:** trigger `melee_unwavering` — fires when the owner is in melee, cast on self.
- **Game declares:** a Hex aimed at one enemy unit (75 m intercept) — Melee Defence −24 and Rampage! for 15 s, ×3 uses.
- **Why it makes no sense:** an aimed single-enemy debuff (the gas is "wafted towards the enemy"); the mod cannot aim it and self is not a legal target.
- **Feasibility:** not implementable as-is (enemy targeting); flag for the user.

**Your ruling:** ______________________________________________________________________________


#### 333. Frenzied Challenge  (slice 06)

- **Key(s):** `wh3_dlc27_qb_unit_abilities_frenzied_challenge`
- **Current logic:** trigger `melee_unwavering` — fires when the owner is in melee, cast on self.
- **Game declares:** a Hex aimed at one enemy unit (150 m intercept) — Speed +25%, Melee Defence −24 and Rampage! for 15 s.
- **Why it makes no sense:** a targeted enemy challenge-hex; self is not a legal target and the mod cannot aim it.
- **Feasibility:** not implementable as-is (enemy targeting); flag for the user.

**Your ruling:** ______________________________________________________________________________


#### 334. Frost Shard Glaive  (slice 06)

- **Key(s):** `wh3_main_weapon_abilities_frost_shard_glaive`
- **Current logic:** trigger `melee_unwavering` — fires when the owner is in melee, cast on self.
- **Game declares:** a Hex aimed at one enemy unit (50 m intercept; `range=0` with a single-target count — the specs describe a picked enemy, not a self-centred area) — Speed −45%, Melee Defence −40 for 30 s.
- **Why it makes no sense:** it must be aimed at an enemy; the mod cannot aim it and self is not a legal target — the "cold, hard promise of sharp slaughter" never reaches a victim.
- **Feasibility:** not implementable as-is (enemy targeting); flag for the user.

**Your ruling:** ______________________________________________________________________________


#### 336. Gaze of Fate  (slice 06)

- **Key(s):** `wh3_main_lord_abilities_gaze_of_fate`
- **Current logic:** trigger `melee_unwavering` — fires when the owner is in melee, cast on self.
- **Game declares:** a Hex aimed at one enemy unit (100 m intercept) — Melee Attack −40 and Cannot Move ("freezes the foe where they stand") for 14 s, ×3 uses.
- **Why it makes no sense:** a targeted enemy freeze hex; the mod cannot aim it and self is not a legal target.
- **Feasibility:** not implementable as-is (enemy targeting); flag for the user.

**Your ruling:** ______________________________________________________________________________


#### 337. Get 'Em!  (slice 06)

- **Key(s):** `wh3_dlc25_character_abilities_get_em`
- **Current logic:** trigger `melee_unwavering` — fires when the owner is in melee, cast on self.
- **Game declares:** an area Hex placed on enemy ground (`target_ground=true`, 35 m area at up to 100 m) — Cannot Move for 11 s.
- **Why it makes no sense:** a ground-placed enemy hex; the mod cannot aim or place it and self is not a legal target — the "Get 'Em!" order is issued against the wrong side.
- **Feasibility:** not implementable as-is (enemy-ground aiming); flag for the user.

**Your ruling:** ______________________________________________________________________________


#### 339. Gilellion's Soulnetter  (slice 06)

- **Key(s):** `wh3_main_weapon_abilities_soulnetter`
- **Current logic:** trigger `melee_unwavering` — fires when the owner is in melee, cast on self.
- **Game declares:** a Hex aimed at one enemy unit (50 m intercept) — Cannot Move for 26 s ("traps its victims in immortal servitude").
- **Why it makes no sense:** a targeted single-enemy binding hex; the mod cannot aim it and self is not a legal target.
- **Feasibility:** not implementable as-is (enemy targeting); flag for the user.

**Your ruling:** ______________________________________________________________________________


#### 341. Glory Seeker  (slice 06)

- **Key(s):** `wh3_dlc29_hero_active_glory_seeker`
- **Current logic:** trigger `melee_unwavering` — fires when the owner is in melee, cast on self.
- **Game declares:** a Hex aimed at one enemy unit within 100 m, restricted to commander-class targets (`unit_is_not_commander_class` invalid-target flag) — Melee Defence −24, healing blocked, Cannot Move for 24 s.
- **Why it makes no sense:** it must be aimed at an enemy character; the mod cannot aim it and self is not a legal (or commander-class) target.
- **Feasibility:** not implementable as-is — enemy targeting does not exist in the mod; flag for the user.

**Your ruling:** ______________________________________________________________________________


#### 342. Glory Seeker Upgraded  (slice 06)

- **Key(s):** `wh3_dlc29_hero_active_glory_seeker_upgraded`
- **Current logic:** trigger `melee_unwavering` — fires when the owner is in melee, cast on self.
- **Game declares:** the upgraded version of the same Hex at one enemy commander-class unit (100 m intercept) — Melee Defence −36, healing blocked, Cannot Move for 36 s.
- **Why it makes no sense:** same target mismatch as the base key — a targeted enemy-character hex under a self-cast trigger.
- **Feasibility:** not implementable as-is (enemy targeting); flag for the user.

**Your ruling:** ______________________________________________________________________________


#### 348. Headhunt  (slice 06)

- **Key(s):** `wh3_dlc26_character_abilities_headhunt`
- **Current logic:** trigger `melee_unwavering` — fires when the owner is in melee, cast on self.
- **Game declares:** a Hex aimed at one enemy unit within 150 m, restricted to commander-class targets (`unit_is_not_commander_class` invalid-target flag) — Melee Defence −40 and Missile Resistance −20 for 31 s.
- **Why it makes no sense:** it must be aimed at an enemy character; the mod cannot aim it and self is not a legal (or commander-class) target.
- **Feasibility:** not implementable as-is — enemy targeting does not exist in the mod; flag for the user.

**Your ruling:** ______________________________________________________________________________


#### 351. Hidden Huntress  (slice 07)

- **Key(s):** `wh3_cp1_lord_abilities_hidden_huntress`
- **Current logic:** Rides `melee_unwavering` - fires when the unit is in melee, not routing and not wavering; the cast passes the owner itself as the target (`perform_special_ability(key, owner)`).
- **Game declares:** A single-ENEMY armour hex (`target_enemies=true`, `num_effected_enemy_units=1`, range 75 m): -25% speed, -24 Melee Defence for 20 s.
- **Why it makes no sense:** The effect applies only to the chosen ENEMY (and the game requires that choice - single/limited targets, some restricted to commander or missile units). The mod's cast passes the owner as the target, so nothing lands on any enemy; with no enemy-unit read (no card, id or health) the cast can neither be aimed nor gated.
- **Feasibility:** Not implementable as-is: the engine exposes no enemy unit read and enemy-targeted casts cannot be aimed by the mod - firing it blindly on self cannot deliver an enemy-targeted effect.

**Your ruling:** ______________________________________________________________________________


#### 352. Hidden Huntress Upgraded  (slice 07)

- **Key(s):** `wh3_cp1_lord_abilities_hidden_huntress_upgraded`
- **Current logic:** Rides `melee_unwavering` - fires when the unit is in melee, not routing and not wavering; the cast passes the owner itself as the target (`perform_special_ability(key, owner)`).
- **Game declares:** A single-ENEMY hex, upgraded: -25% speed, -30 armour, -40 Melee Defence for 20 s, range 75 m.
- **Why it makes no sense:** The effect applies only to the chosen ENEMY (and the game requires that choice - single/limited targets, some restricted to commander or missile units). The mod's cast passes the owner as the target, so nothing lands on any enemy; with no enemy-unit read (no card, id or health) the cast can neither be aimed nor gated.
- **Feasibility:** Not implementable as-is: the engine exposes no enemy unit read and enemy-targeted casts cannot be aimed by the mod - firing it blindly on self cannot deliver an enemy-targeted effect.

**Your ruling:** ______________________________________________________________________________


#### 355. Hornswaggle  (slice 07)

- **Key(s):** `wh2_dlc11_character_abilities_hornswaggle`
- **Current logic:** Rides `melee_unwavering` - fires when the unit is in melee, not routing and not wavering; the cast passes the owner itself as the target (`perform_special_ability(key, owner)`).
- **Game declares:** A single-ENEMY hex: -25% speed, -30 armour, -24 Melee Defence for 32 s, range 100 m.
- **Why it makes no sense:** The effect applies only to the chosen ENEMY (and the game requires that choice - single/limited targets, some restricted to commander or missile units). The mod's cast passes the owner as the target, so nothing lands on any enemy; with no enemy-unit read (no card, id or health) the cast can neither be aimed nor gated.
- **Feasibility:** Not implementable as-is: the engine exposes no enemy unit read and enemy-targeted casts cannot be aimed by the mod - firing it blindly on self cannot deliver an enemy-targeted effect.

**Your ruling:** ______________________________________________________________________________


#### 357. Hunter of Champions  (slice 07)

- **Key(s):** `wh_dlc08_character_abilities_hunter_of_champions`
- **Current logic:** Rides `melee_unwavering` - fires when the unit is in melee, not routing and not wavering; the cast passes the owner itself as the target (`perform_special_ability(key, owner)`).
- **Game declares:** A single-ENEMY hex that the game only allows on a commander-class target (invalid-target flag `unit_is_not_commander_class`): -45% speed, -60 armour, -40 Melee Defence for 24 s, range 100 m.
- **Why it makes no sense:** The effect applies only to the chosen ENEMY (and the game requires that choice - single/limited targets, some restricted to commander or missile units). The mod's cast passes the owner as the target, so nothing lands on any enemy; with no enemy-unit read (no card, id or health) the cast can neither be aimed nor gated.
- **Feasibility:** Not implementable as-is: the engine exposes no enemy unit read and enemy-targeted casts cannot be aimed by the mod - firing it blindly on self cannot deliver an enemy-targeted effect.

**Your ruling:** ______________________________________________________________________________


#### 358. Hunter's Snare  (slice 07)

- **Key(s):** `wh2_dlc13_lord_abilities_hunters_snare`
- **Current logic:** Rides `melee_unwavering` - fires when the unit is in melee, not routing and not wavering; the cast passes the owner itself as the target (`perform_special_ability(key, owner)`).
- **Game declares:** An ENEMY- or GROUND-targeted 35 m net (cant_move) for 11 s, placed up to 100 m away, 3 uses (`target_enemies=true`, `target_ground=true`).
- **Why it makes no sense:** The effect applies only to the chosen ENEMY (and the game requires that choice - single/limited targets, some restricted to commander or missile units). The mod's cast passes the owner as the target, so nothing lands on any enemy; with no enemy-unit read (no card, id or health) the cast can neither be aimed nor gated.
- **Feasibility:** Not implementable as-is: the engine exposes no enemy unit read and enemy-targeted casts cannot be aimed by the mod - firing it blindly on self cannot deliver an enemy-targeted effect.

**Your ruling:** ______________________________________________________________________________


#### 359. Hunter's Trap  (slice 07)

- **Key(s):** `wh2_dlc13_lord_abilities_hunters_trap`
- **Current logic:** Rides `melee_unwavering` - fires when the unit is in melee, not routing and not wavering; the cast passes the owner itself as the target (`perform_special_ability(key, owner)`).
- **Game declares:** An ENEMY- or GROUND-targeted 35 m net (cant_move) for 22 s, placed up to 100 m away, 3 uses.
- **Why it makes no sense:** The effect applies only to the chosen ENEMY (and the game requires that choice - single/limited targets, some restricted to commander or missile units). The mod's cast passes the owner as the target, so nothing lands on any enemy; with no enemy-unit read (no card, id or health) the cast can neither be aimed nor gated.
- **Feasibility:** Not implementable as-is: the engine exposes no enemy unit read and enemy-targeted casts cannot be aimed by the mod - firing it blindly on self cannot deliver an enemy-targeted effect.

**Your ruling:** ______________________________________________________________________________


#### 369. Looming Dread  (slice 07)

- **Key(s):** `wh2_dlc14_lord_abilities_looming_dread`
- **Current logic:** Rides `melee_unwavering` - fires when the unit is in melee, not routing and not wavering; the cast passes the owner itself as the target (`perform_special_ability(key, owner)`).
- **Game declares:** A single-ENEMY hex restricted to commander-class targets (invalid-target flag `unit_is_not_commander_class`): -45% speed, -24 Melee Defence, -20 missile resistance for 31 s, range 150 m.
- **Why it makes no sense:** The effect applies only to the chosen ENEMY (and the game requires that choice - single/limited targets, some restricted to commander or missile units). The mod's cast passes the owner as the target, so nothing lands on any enemy; with no enemy-unit read (no card, id or health) the cast can neither be aimed nor gated.
- **Feasibility:** Not implementable as-is: the engine exposes no enemy unit read and enemy-targeted casts cannot be aimed by the mod - firing it blindly on self cannot deliver an enemy-targeted effect.

**Your ruling:** ______________________________________________________________________________


#### 370. Lord of Dragons  (slice 07)

- **Key(s):** `wh2_dlc15_lord_abilities_lord_of_dragons`
- **Current logic:** Rides `melee_unwavering` - fires when the unit is in melee, not routing and not wavering; the cast passes the owner itself as the target (`perform_special_ability(key, owner)`).
- **Game declares:** A single-ENEMY hex: -40 Melee Attack, -24 Melee Defence for 22 s, range 75 m.
- **Why it makes no sense:** The effect applies only to the chosen ENEMY (and the game requires that choice - single/limited targets, some restricted to commander or missile units). The mod's cast passes the owner as the target, so nothing lands on any enemy; with no enemy-unit read (no card, id or health) the cast can neither be aimed nor gated.
- **Feasibility:** Not implementable as-is: the engine exposes no enemy unit read and enemy-targeted casts cannot be aimed by the mod - firing it blindly on self cannot deliver an enemy-targeted effect.

**Your ruling:** ______________________________________________________________________________


#### 372. Mark of the Plague Fleet  (slice 07)

- **Key(s):** `wh3_dlc29_item_active_mark_of_the_plague_fleet`
- **Current logic:** Rides `melee_unwavering` - fires when the unit is in melee, not routing and not wavering; the cast passes the owner itself as the target (`perform_special_ability(key, owner)`).
- **Game declares:** An ENEMY hex affecting up to three units (spreads to enemies): -50% healing power, -20 all/magic/physical resistances for 30 s, range 75 m.
- **Why it makes no sense:** The effect applies only to the chosen ENEMY (and the game requires that choice - single/limited targets, some restricted to commander or missile units). The mod's cast passes the owner as the target, so nothing lands on any enemy; with no enemy-unit read (no card, id or health) the cast can neither be aimed nor gated.
- **Feasibility:** Not implementable as-is: the engine exposes no enemy unit read and enemy-targeted casts cannot be aimed by the mod - firing it blindly on self cannot deliver an enemy-targeted effect.

**Your ruling:** ______________________________________________________________________________


#### 373. Mark of Yin  (slice 07)

- **Key(s):** `wh3_dlc24_unit_abilities_mark_of_yin`
- **Current logic:** Rides `melee_unwavering` - fires when the unit is in melee, not routing and not wavering; the cast passes the owner itself as the target (`perform_special_ability(key, owner)`).
- **Game declares:** A single-ENEMY hex: -30 armour, -25 missile block chance, -20 missile resistance for 28 s, range 180 m.
- **Why it makes no sense:** The effect applies only to the chosen ENEMY (and the game requires that choice - single/limited targets, some restricted to commander or missile units). The mod's cast passes the owner as the target, so nothing lands on any enemy; with no enemy-unit read (no card, id or health) the cast can neither be aimed nor gated.
- **Feasibility:** Not implementable as-is: the engine exposes no enemy unit read and enemy-targeted casts cannot be aimed by the mod - firing it blindly on self cannot deliver an enemy-targeted effect.

**Your ruling:** ______________________________________________________________________________


#### 374. Marked by Ulthar  (slice 07)

- **Key(s):** `wh_dlc06_unit_abilities_marked_by_ulthar`
- **Current logic:** Rides `melee_unwavering` - fires when the unit is in melee, not routing and not wavering; the cast passes the owner itself as the target (`perform_special_ability(key, owner)`).
- **Game declares:** A single-ENEMY hex: -30 armour, -25 missile block chance, -20 missile resistance for 28 s, range 150 m.
- **Why it makes no sense:** The effect applies only to the chosen ENEMY (and the game requires that choice - single/limited targets, some restricted to commander or missile units). The mod's cast passes the owner as the target, so nothing lands on any enemy; with no enemy-unit read (no card, id or health) the cast can neither be aimed nor gated.
- **Feasibility:** Not implementable as-is: the engine exposes no enemy unit read and enemy-targeted casts cannot be aimed by the mod - firing it blindly on self cannot deliver an enemy-targeted effect.

**Your ruling:** ______________________________________________________________________________


#### 375. Marked for Eatin'  (slice 07)

- **Key(s):** `wh3_dlc26_unit_abilities_marked_for_eatin`
- **Current logic:** Rides `melee_unwavering` - fires when the unit is in melee, not routing and not wavering; the cast passes the owner itself as the target (`perform_special_ability(key, owner)`).
- **Game declares:** A single-ENEMY hex: -25% speed, -30 armour, -40 Melee Defence for 29 s, range 75 m.
- **Why it makes no sense:** The effect applies only to the chosen ENEMY (and the game requires that choice - single/limited targets, some restricted to commander or missile units). The mod's cast passes the owner as the target, so nothing lands on any enemy; with no enemy-unit read (no card, id or health) the cast can neither be aimed nor gated.
- **Feasibility:** Not implementable as-is: the engine exposes no enemy unit read and enemy-targeted casts cannot be aimed by the mod - firing it blindly on self cannot deliver an enemy-targeted effect.

**Your ruling:** ______________________________________________________________________________


#### 376. Master of Beguilement  (slice 07)

- **Key(s):** `wh_dlc04_lord_abilities_beguile`
- **Current logic:** Rides `melee_unwavering` - fires when the unit is in melee, not routing and not wavering; the cast passes the owner itself as the target (`perform_special_ability(key, owner)`).
- **Game declares:** A single-ENEMY hex: -40 Melee Attack for 44 s, range 100 m.
- **Why it makes no sense:** The effect applies only to the chosen ENEMY (and the game requires that choice - single/limited targets, some restricted to commander or missile units). The mod's cast passes the owner as the target, so nothing lands on any enemy; with no enemy-unit read (no card, id or health) the cast can neither be aimed nor gated.
- **Feasibility:** Not implementable as-is: the engine exposes no enemy unit read and enemy-targeted casts cannot be aimed by the mod - firing it blindly on self cannot deliver an enemy-targeted effect.

**Your ruling:** ______________________________________________________________________________


#### 381. Master Rune of Slowness  (slice 07)

- **Key(s):** `wh2_dlc17_rune_abilities_master_rune_of_slowness`
- **Current logic:** Rides `melee_unwavering` - fires when the unit is in melee, not routing and not wavering; the cast passes the owner itself as the target (`perform_special_ability(key, owner)`).
- **Game declares:** A single-ENEMY rune hex: -60% speed and charge speed, -40% charge bonus for 45 s, range 100 m.
- **Why it makes no sense:** The effect applies only to the chosen ENEMY (and the game requires that choice - single/limited targets, some restricted to commander or missile units). The mod's cast passes the owner as the target, so nothing lands on any enemy; with no enemy-unit read (no card, id or health) the cast can neither be aimed nor gated.
- **Feasibility:** Not implementable as-is: the engine exposes no enemy unit read and enemy-targeted casts cannot be aimed by the mod - firing it blindly on self cannot deliver an enemy-targeted effect.

**Your ruling:** ______________________________________________________________________________


#### 390. Missile Mirror  (slice 07)

- **Key(s):** `wh3_dlc24_unit_bound_missile_mirror`
- **Current logic:** Rides `melee_unwavering` - fires when the unit is in melee, not routing and not wavering; the cast passes the owner itself as the target (`perform_special_ability(key, owner)`).
- **Game declares:** A single-ENEMY bound spell that must target an enemy missile unit (invalid-target flag `is_not_missile_unit`) to redirect its projectiles for 18 s, range 200 m.
- **Why it makes no sense:** The effect applies only to the chosen ENEMY (and the game requires that choice - single/limited targets, some restricted to commander or missile units). The mod's cast passes the owner as the target, so nothing lands on any enemy; with no enemy-unit read (no card, id or health) the cast can neither be aimed nor gated.
- **Feasibility:** Not implementable as-is: the engine exposes no enemy unit read and enemy-targeted casts cannot be aimed by the mod - firing it blindly on self cannot deliver an enemy-targeted effect.

**Your ruling:** ______________________________________________________________________________


#### 391. Mither  (slice 07)

- **Key(s):** `wh2_dlc15_hero_abilities_mither`
- **Current logic:** Rides `melee_unwavering` - fires when the unit is in melee, not routing and not wavering; the cast passes the owner itself as the target (`perform_special_ability(key, owner)`).
- **Game declares:** A single-ENEMY morale/speed hex: -60% speed and charge speed for 15 s, range 75 m.
- **Why it makes no sense:** The effect applies only to the chosen ENEMY (and the game requires that choice - single/limited targets, some restricted to commander or missile units). The mod's cast passes the owner as the target, so nothing lands on any enemy; with no enemy-unit read (no card, id or health) the cast can neither be aimed nor gated.
- **Feasibility:** Not implementable as-is: the engine exposes no enemy unit read and enemy-targeted casts cannot be aimed by the mod - firing it blindly on self cannot deliver an enemy-targeted effect.

**Your ruling:** ______________________________________________________________________________


#### 394. Muster of Malevolents  (slice 07)

- **Key(s):** `wh2_dlc16_character_abilities_muster_of_malevolents`
- **Current logic:** Rides `melee_unwavering` - fires when the unit is in melee, not routing and not wavering; the cast passes the owner itself as the target (`perform_special_ability(key, owner)`).
- **Game declares:** A single-ENEMY direct-damage effect: 144 damage over 15 s (max 1 entity damaged), range 75 m.
- **Why it makes no sense:** The effect applies only to the chosen ENEMY (and the game requires that choice - single/limited targets, some restricted to commander or missile units). The mod's cast passes the owner as the target, so nothing lands on any enemy; with no enemy-unit read (no card, id or health) the cast can neither be aimed nor gated.
- **Feasibility:** Not implementable as-is: the engine exposes no enemy unit read and enemy-targeted casts cannot be aimed by the mod - firing it blindly on self cannot deliver an enemy-targeted effect.

**Your ruling:** ______________________________________________________________________________


#### 396. Net Dem Up!  (slice 07)

- **Key(s):** `wh3_dlc26_unit_abilities_net_dem_up`
- **Current logic:** Rides `melee_unwavering` - fires when the unit is in melee, not routing and not wavering; the cast passes the owner itself as the target (`perform_special_ability(key, owner)`).
- **Game declares:** A single-ENEMY net (cant_move, -50 missile block chance) for 18 s, range 75 m.
- **Why it makes no sense:** The effect applies only to the chosen ENEMY (and the game requires that choice - single/limited targets, some restricted to commander or missile units). The mod's cast passes the owner as the target, so nothing lands on any enemy; with no enemy-unit read (no card, id or health) the cast can neither be aimed nor gated.
- **Feasibility:** Not implementable as-is: the engine exposes no enemy unit read and enemy-targeted casts cannot be aimed by the mod - firing it blindly on self cannot deliver an enemy-targeted effect.

**Your ruling:** ______________________________________________________________________________


#### 397. Net of Amyntok  (slice 07)

- **Key(s):** `wh_dlc04_spell_bound_net_of_amyntok`
- **Current logic:** Rides `melee_unwavering` - fires when the unit is in melee, not routing and not wavering; the cast passes the owner itself as the target (`perform_special_ability(key, owner)`).
- **Game declares:** A single-ENEMY bound net (cant_move) for 20 s, range 100 m, 3 uses.
- **Why it makes no sense:** The effect applies only to the chosen ENEMY (and the game requires that choice - single/limited targets, some restricted to commander or missile units). The mod's cast passes the owner as the target, so nothing lands on any enemy; with no enemy-unit read (no card, id or health) the cast can neither be aimed nor gated.
- **Feasibility:** Not implementable as-is: the engine exposes no enemy unit read and enemy-targeted casts cannot be aimed by the mod - firing it blindly on self cannot deliver an enemy-targeted effect.

**Your ruling:** ______________________________________________________________________________


#### 399. Oath of Vengeance  (slice 07)

- **Key(s):** `wh2_dlc10_lord_abilities_oath_of_vengeance`
- **Current logic:** Rides `melee_unwavering` - fires when the unit is in melee, not routing and not wavering; the cast passes the owner itself as the target (`perform_special_ability(key, owner)`).
- **Game declares:** A single-ENEMY hex: -24 Melee Defence for 44 s, range 200 m.
- **Why it makes no sense:** The effect applies only to the chosen ENEMY (and the game requires that choice - single/limited targets, some restricted to commander or missile units). The mod's cast passes the owner as the target, so nothing lands on any enemy; with no enemy-unit read (no card, id or health) the cast can neither be aimed nor gated.
- **Feasibility:** Not implementable as-is: the engine exposes no enemy unit read and enemy-targeted casts cannot be aimed by the mod - firing it blindly on self cannot deliver an enemy-targeted effect.

**Your ruling:** ______________________________________________________________________________


#### 400. Oil Flask  (slice 07)

- **Key(s):** `wh2_dlc13_lord_abilities_oil_flask`
- **Current logic:** Rides `melee_unwavering` - fires when the unit is in melee, not routing and not wavering; the cast passes the owner itself as the target (`perform_special_ability(key, owner)`).
- **Game declares:** A thrown PROJECTILE fired at an enemy unit (`activated_projectile`): -48% speed and +50% flame weakness on contact, requires line of sight, range 70 m, 3 uses.
- **Why it makes no sense:** The effect applies only to the chosen ENEMY (and the game requires that choice - single/limited targets, some restricted to commander or missile units). The mod's cast passes the owner as the target, so nothing lands on any enemy; with no enemy-unit read (no card, id or health) the cast can neither be aimed nor gated.
- **Feasibility:** Not implementable as-is: the engine exposes no enemy unit read and enemy-targeted casts cannot be aimed by the mod - firing it blindly on self cannot deliver an enemy-targeted effect.

**Your ruling:** ______________________________________________________________________________


#### 401. Otto's Scythe  (slice 07)

- **Key(s):** `wh3_dlc29_item_active_ottos_scythe`
- **Current logic:** Rides `melee_unwavering` - fires when the unit is in melee, not routing and not wavering; the cast passes the owner itself as the target (`perform_special_ability(key, owner)`).
- **Game declares:** A single-ENEMY hex: -40 Melee Attack, -24 morale, and negative charge-defence/reflection attributes for 28 s, range 100 m.
- **Why it makes no sense:** The effect applies only to the chosen ENEMY (and the game requires that choice - single/limited targets, some restricted to commander or missile units). The mod's cast passes the owner as the target, so nothing lands on any enemy; with no enemy-unit read (no card, id or health) the cast can neither be aimed nor gated.
- **Feasibility:** Not implementable as-is: the engine exposes no enemy unit read and enemy-targeted casts cannot be aimed by the mod - firing it blindly on self cannot deliver an enemy-targeted effect.

**Your ruling:** ______________________________________________________________________________


#### 402. Pack Trap  (slice 07)

- **Key(s):** `wh3_dlc24_unit_abilities_pack_trap`
- **Current logic:** Rides `melee_unwavering` - fires when the unit is in melee, not routing and not wavering; the cast passes the owner itself as the target (`perform_special_ability(key, owner)`).
- **Game declares:** A single-ENEMY net (cant_move, +fatigue) for 10 s, range 100 m, 3 uses.
- **Why it makes no sense:** The effect applies only to the chosen ENEMY (and the game requires that choice - single/limited targets, some restricted to commander or missile units). The mod's cast passes the owner as the target, so nothing lands on any enemy; with no enemy-unit read (no card, id or health) the cast can neither be aimed nor gated.
- **Feasibility:** Not implementable as-is: the engine exposes no enemy unit read and enemy-targeted casts cannot be aimed by the mod - firing it blindly on self cannot deliver an enemy-targeted effect.

**Your ruling:** ______________________________________________________________________________


#### 403. Pageant of Shrikes  (slice 07)

- **Key(s):** `wh2_dlc16_character_abilities_pageant_of_shrikes`
- **Current logic:** Rides `melee_unwavering` - fires when the unit is in melee, not routing and not wavering; the cast passes the owner itself as the target (`perform_special_ability(key, owner)`).
- **Game declares:** A single-ENEMY hex: -60% ammunition replenishment, -20 reloading, -20% missile range for 20 s, range 75 m.
- **Why it makes no sense:** The effect applies only to the chosen ENEMY (and the game requires that choice - single/limited targets, some restricted to commander or missile units). The mod's cast passes the owner as the target, so nothing lands on any enemy; with no enemy-unit read (no card, id or health) the cast can neither be aimed nor gated.
- **Feasibility:** Not implementable as-is: the engine exposes no enemy unit read and enemy-targeted casts cannot be aimed by the mod - firing it blindly on self cannot deliver an enemy-targeted effect.

**Your ruling:** ______________________________________________________________________________


#### 405. Pestilent Potions  (slice 07)

- **Key(s):** `wh3_dlc20_item_abilities_pestilent_potions`
- **Current logic:** Rides `melee_unwavering` - fires when the unit is in melee, not routing and not wavering; the cast passes the owner itself as the target (`perform_special_ability(key, owner)`).
- **Game declares:** An ENEMY hex affecting up to five units (spreads between enemies): -24 Melee Attack, -25% melee damage for 25 s, range 100 m.
- **Why it makes no sense:** The effect applies only to the chosen ENEMY (and the game requires that choice - single/limited targets, some restricted to commander or missile units). The mod's cast passes the owner as the target, so nothing lands on any enemy; with no enemy-unit read (no card, id or health) the cast can neither be aimed nor gated.
- **Feasibility:** Not implementable as-is: the engine exposes no enemy unit read and enemy-targeted casts cannot be aimed by the mod - firing it blindly on self cannot deliver an enemy-targeted effect.

**Your ruling:** ______________________________________________________________________________


#### 408. Plague of Rust  (slice 08)

- **Key(s):** `wh3_main_spell_bound_plague_of_rust`
- **Current logic:** trigger `melee_unwavering`; fires while in melee and casts on self (default self-target call).
- **Game declares:** a Hex (`wh_type_hex`) aimed at one enemy unit (`target_enemies=true`, `num_effected_enemy_units=1`, cast range 200 m): −30 armour for 44 s; 2 uses, 60 s recharge. The tracker's own proposal for this row: "While the unit has an enemy in its sights: fire at it."
- **Why it makes no sense:** the cast must be aimed at an enemy unit and the mod aims it at the caster; the −30 armour hex can never land on an enemy (if the engine accepted the self-target, it would debuff the caster's own unit).
- **Feasibility:** not implementable as-is — there is no enemy-unit read and enemy-targeted casts cannot be aimed (established engine limit); the tracker marks comparable rows `excluded (impossible: no enemy-unit read)`.

**Your ruling:** ______________________________________________________________________________


#### 414. Power Siphon  (slice 08)

- **Key(s):** `wh2_dlc11_lord_abilities_power_siphon`
- **Current logic:** trigger `melee_unwavering`; in-melee self-cast.
- **Game declares:** a Hex aimed at one enemy unit (`target_enemies=true`, cast range 100 m) — a caster-debuff that raises the target's ability recharge (+15 s) and fatigues it, for 30 s; ×4 uses, 60 s recharge.
- **Why it makes no sense:** it is a hex that must be aimed at an enemy caster, and the mod casts it on itself; the drain/slow effect can never be delivered to the intended target.
- **Feasibility:** not implementable as-is — no enemy-unit read exists and enemy-targeted casts cannot be aimed; comparable rows are tracked as `excluded (impossible: no enemy-unit read)`.

**Your ruling:** ______________________________________________________________________________


#### 417. Prey of Anath Raema  (slice 08)

- **Key(s):** `wh_dlc05_character_abilities_prey_of_anath_raema`
- **Current logic:** trigger `melee_unwavering`; in-melee self-cast.
- **Game declares:** a Hex aimed at one enemy unit (`target_enemies=true`, cast range 100 m): −20 missile resistance and held in place (`cant_move`) for 16 s; ×3 uses, 90 s recharge. The tracker's proposal: "When in melee with a current target: cast at the enemy it is fighting."
- **Why it makes no sense:** the debuff must be aimed at the enemy being fought, and the mod casts it on the caster; the −20 missile resistance never reaches an enemy.
- **Feasibility:** not implementable as-is — the enemy-unit read needed to aim the cast does not exist (established engine limit).

**Your ruling:** ______________________________________________________________________________


#### 418. Prey of the Blood God  (slice 08)

- **Key(s):** `wh3_pro12_hero_abilities_prey_of_the_blood_god`
- **Current logic:** trigger `melee_unwavering`; in-melee self-cast.
- **Game declares:** a Hex aimed at one enemy unit (`target_enemies=true`, cast range 100 m): 33 damage/s to one entity plus `cant_move` for 22 s; ×3 uses, 120 s recharge. The tracker's proposal: "cast at the enemy it is fighting."
- **Why it makes no sense:** it is a targeted enemy damage/hold hex and the mod casts it on its own caster — the effect can never hit the intended victim.
- **Feasibility:** not implementable as-is — no enemy-unit read; enemy casts cannot be aimed.

**Your ruling:** ______________________________________________________________________________


#### 421. Ravaging Swarm  (slice 08)

- **Key(s):** `wh3_dlc29_hero_active_dispatch_the_swarm_attack`
- **Current logic:** trigger `melee_unwavering`; in-melee self-cast.
- **Game declares:** a chain Hex on one enemy unit (`target_enemies=true`, up to five units affected, 30 m spread range, cast range 100 m): −24 melee defence for 24 s; 120 s recharge. The tracker's proposal: "cast at the enemy it is fighting."
- **Why it makes no sense:** the chain must start from an enemy unit; cast on the caster it cannot start, so neither the primary debuff nor the spread can occur.
- **Feasibility:** not implementable as-is — no enemy-unit read; enemy casts cannot be aimed.

**Your ruling:** ______________________________________________________________________________


#### 422. Ravaging Swarm Upgraded  (slice 08)

- **Key(s):** `wh3_dlc29_hero_active_dispatch_the_swarm_attack_upgraded`
- **Current logic:** trigger `melee_unwavering`; in-melee self-cast.
- **Game declares:** a chain Hex on one enemy unit (`target_enemies=true`, up to five, 30 m spread, cast range 100 m): −40 melee defence plus 4 damage/s to up to 10 entities for 24 s; 60 s recharge. Tracker proposal: "cast at the enemy it is fighting."
- **Why it makes no sense:** same as its base key — the chain hex needs an enemy starting unit and the mod casts it on itself.
- **Feasibility:** not implementable as-is — no enemy-unit read; enemy casts cannot be aimed.

**Your ruling:** ______________________________________________________________________________


#### 429. Rune of Slowness  (slice 08)

- **Key(s):** `wh2_dlc17_rune_abilities_rune_of_slowness`
- **Current logic:** trigger `melee_unwavering`; in-melee self-cast.
- **Game declares:** a Hex aimed at one enemy unit (`target_enemies=true`, cast range 100 m): −45% speed and charge speed, −40% charge bonus for 30 s; 120 s recharge. Tracker proposal: "fire at it (enemy in sights)."
- **Why it makes no sense:** the slow must be aimed at an enemy unit and the mod casts it on the caster; an enemy is never slowed.
- **Feasibility:** not implementable as-is — no enemy-unit read; enemy casts cannot be aimed.

**Your ruling:** ______________________________________________________________________________


#### 431. Sadistic Snare  (slice 08)

- **Key(s):** `wh3_dlc23_lord_abilities_sadistic_snare`
- **Current logic:** trigger `melee_unwavering`; in-melee self-cast.
- **Game declares:** a Hex aimed at one enemy unit within 20 m (`target_enemies=true`, cast range 20 m): −24 melee defence and `cant_move` for 33 s; ×2 uses, 120 s recharge. Tracker proposal: "cast at the enemy it is fighting."
- **Why it makes no sense:** the snare must catch an enemy unit (the game itself limits the cast range to 20 m) and the mod aims it at the caster.
- **Feasibility:** not implementable as-is — no enemy-unit read; enemy casts cannot be aimed.

**Your ruling:** ______________________________________________________________________________


#### 434. Scroll of Leeching  (slice 08)

- **Key(s):** `wh_main_item_abilities_scroll_of_leeching`
- **Current logic:** trigger `melee_unwavering`; in-melee self-cast.
- **Game declares:** a Hex of the Winds aimed at one enemy unit (`target_enemies=true`, cast range 100 m): −0.4 Winds of Magic regen on the target for 44 s; ×1 use, 60 s recharge. Tracker proposal: "fire at it."
- **Why it makes no sense:** it must be aimed at an enemy (a caster to drain); cast on the caster it can never sap the intended target.
- **Feasibility:** not implementable as-is — no enemy-unit read; enemy casts cannot be aimed.

**Your ruling:** ______________________________________________________________________________


#### 440. Silence the Prey  (slice 08)

- **Key(s):** `wh3_main_character_abilities_silence_the_prey`
- **Current logic:** trigger `melee_unwavering`; in-melee self-cast.
- **Game declares:** a Hex aimed at one enemy unit (`target_enemies=true`, cast range 100 m): raises the target's ability recharge by +30 s (a caster silence) for 30 s; ×4 uses, 60 s recharge. Tracker proposal: "fire at it."
- **Why it makes no sense:** the silence must be aimed at an enemy; the mod casts it on itself, where it can never suppress an enemy caster.
- **Feasibility:** not implementable as-is — no enemy-unit read; enemy casts cannot be aimed.

**Your ruling:** ______________________________________________________________________________


#### 445. Spearfisher's Net  (slice 08)

- **Key(s):** `wh2_dlc11_lord_abilities_spearfishers_net`
- **Current logic:** trigger `melee_unwavering`; in-melee self-cast.
- **Game declares:** a Hex aimed at one enemy unit (`target_enemies=true`, cast range 100 m): −24 melee defence and `cant_move` for 18 s; ×3 uses, 90 s recharge. Tracker proposal: "cast at the enemy it is fighting."
- **Why it makes no sense:** the net must catch an enemy unit; cast on the caster the hold/debuff never lands on an enemy.
- **Feasibility:** not implementable as-is — no enemy-unit read; enemy casts cannot be aimed.

**Your ruling:** ______________________________________________________________________________


#### 447. Spiderweb Attack  (slice 08)

- **Key(s):** `wh3_dlc26_character_abilities_spider_web_attack`
- **Current logic:** trigger `melee_unwavering`; in-melee self-cast.
- **Game declares:** a Hex aimed at one enemy unit within 50 m (`target_enemies=true`, cast range 50 m): immobilises the target (`cant_move`) for 18 s; ×2 uses, 120 s recharge. Tracker proposal: "cast at the enemy it is fighting."
- **Why it makes no sense:** the web must be aimed at an enemy unit; cast on the caster it can never immobilise an enemy.
- **Feasibility:** not implementable as-is — no enemy-unit read; enemy casts cannot be aimed.

**Your ruling:** ______________________________________________________________________________


#### 455. Sword of Filth  (slice 08)

- **Key(s):** `wh3_dlc25_weapon_abilities_sword_of_filth`
- **Current logic:** trigger `melee_unwavering`; in-melee self-cast.
- **Game declares:** a chain Hex on one enemy unit (`target_enemies=true`, up to five units, cast range 35 m): −30 armour and −24 melee defence for 20 s; 120 s recharge. Tracker proposal: "fire at it."
- **Why it makes no sense:** the chain must start from an enemy unit; cast on the caster neither the primary debuff nor the chain can occur.
- **Feasibility:** not implementable as-is — no enemy-unit read; enemy casts cannot be aimed.

**Your ruling:** ______________________________________________________________________________


#### 457. Taunt  (slice 08)

- **Key(s):** `wh2_dlc11_character_abilities_taunt`
- **Current logic:** trigger `melee_unwavering`; in-melee self-cast.
- **Game declares:** a Hex aimed at one enemy unit (`target_enemies=true`, cast range 100 m): −30 armour, −24 melee defence, −25% speed for 17 s; 60 s recharge. Tracker proposal: "cast at the enemy it is fighting."
- **Why it makes no sense:** the hex must be aimed at an enemy unit; casting it on the caster never taunts/debuffs the enemy it is meant for.
- **Feasibility:** not implementable as-is — no enemy-unit read; enemy casts cannot be aimed.

**Your ruling:** ______________________________________________________________________________


#### 458. Tendrils of the Sea  (slice 08)

- **Key(s):** `wh3_dlc29_hero_active_tendrils_of_the_sea`
- **Current logic:** trigger `melee_unwavering`; in-melee self-cast.
- **Game declares:** a Hex aimed at one enemy unit (`target_enemies=true`, cast range 200 m): −60% speed, −20% mass and −40 melee attack for 24 s; 120 s recharge. Tracker proposal: "cast at the enemy it is fighting."
- **Why it makes no sense:** the slowing hex must be aimed at an enemy unit; the mod casts it on the caster.
- **Feasibility:** not implementable as-is — no enemy-unit read; enemy casts cannot be aimed.

**Your ruling:** ______________________________________________________________________________


#### 460. The Averland Runefang  (slice 08)

- **Key(s):** `wh2_dlc13_weapon_abilities_averland_runefang`
- **Current logic:** trigger `melee_unwavering`; in-melee self-cast.
- **Game declares:** a Hex aimed at one enemy unit (`target_enemies=true`, cast range 100 m): −40 melee attack and ×0.4 base weapon damage for 33 s; 120 s recharge. Tracker proposal: "cast at the enemy it is fighting."
- **Why it makes no sense:** the weapon's hex must be aimed at an enemy unit; casting it on the caster leaves the intended enemy untouched (and may weaken the caster if the engine accepts the self-target).
- **Feasibility:** not implementable as-is — no enemy-unit read; enemy casts cannot be aimed.

**Your ruling:** ______________________________________________________________________________


#### 462. The Black Tongue  (slice 08)

- **Key(s):** `wh3_dlc27_character_abilities_the_black_tongue`
- **Current logic:** trigger `melee_unwavering`; in-melee self-cast.
- **Game declares:** a Hex aimed at one enemy unit (`target_enemies=true`, cast range 200 m): silences the target for 21 s; ×2 uses, 120 s recharge. Tracker proposal: "cast at the enemy it is fighting."
- **Why it makes no sense:** the silence must be aimed at an enemy unit; cast on the caster it cannot silence the enemy it is meant for.
- **Feasibility:** not implementable as-is — no enemy-unit read; enemy casts cannot be aimed.

**Your ruling:** ______________________________________________________________________________


#### 464. The Dark Master  (slice 08)

- **Key(s):** `wh3_main_lord_abilities_the_dark_master`
- **Current logic:** trigger `melee_unwavering`; in-melee self-cast.
- **Game declares:** a Hex aimed at one enemy unit (`target_enemies=true`, cast range 100 m): −40 melee attack for 33 s; 90 s recharge. Tracker proposal: "cast at the enemy it is fighting."
- **Why it makes no sense:** the −40 melee attack hex must be aimed at an enemy unit; the mod casts it on the caster.
- **Feasibility:** not implementable as-is — no enemy-unit read; enemy casts cannot be aimed.

**Your ruling:** ______________________________________________________________________________


#### 465. The Enfeebling Foe  (slice 09)

- **Key(s):** `wh3_dlc23_spell_bound_enfeebling_foe`, `wh3_dlc27_spell_bound_enfeebling_foe`, `wh3_main_spell_bound_enfeebling_foe`, `wh3_twa08_spell_bound_enfeebling_foe_keeper_of_secrets_ror`
- **Current logic:** `melee_unwavering` — in melee (not wavering): cast on self.
- **Game declares:** a bound Shadow hex aimed at ONE enemy unit (target_enemies = true, 200 m intercept, wind-up 1 s); 17 s: −24 Melee Attack, −24 Melee Defence.
- **Why it makes no sense:** cast target — the mod passes the caster itself as the target, but the ability must be aimed at the enemy it is meant to enfeeble; a debuff cast on self is a wrong target.
- **Feasibility:** not implementable as-is — enemy-targeted casts cannot be aimed by the mod (no readable enemy unit, and no proven current-target plumbing). The trigger is achievable; the target is not.

**Your ruling:** ______________________________________________________________________________


#### 468. The Hammer of Karak Drazh  (slice 09)

- **Key(s):** `wh_main_weapon_abilities_the_hammer_of_karak_drazh`
- **Current logic:** `melee_unwavering` — in melee (not wavering): cast on self.
- **Game declares:** a weapon hex aimed at ONE enemy unit (target_enemies = true); 50 s: −40 Melee Attack, ×0.7 Base Weapon Damage.
- **Why it makes no sense:** cast target — self-cast leaves the enemy untouched; the debuff belongs on the enemy unit being fought.
- **Feasibility:** not implementable as-is — the mod cannot aim at an enemy (no enemy reads / no current-target plumbing).

**Your ruling:** ______________________________________________________________________________


#### 474. The Trickster's Pendant  (slice 09)

- **Key(s):** `wh2_main_item_abilities_the_tricksters_pendant`
- **Current logic:** `melee_unwavering` — in melee (not wavering): cast on self.
- **Game declares:** an area-of-hexes cast on enemy ground under the target (target_enemies = true, target_ground = true, 100 m intercept, 35 m area); 16 s: enemy Miscast Chance ×2.
- **Why it makes no sense:** cast target — the mod self-casts, so the hex lands at the caster, not under the enemy; a misplaced cast cannot hit the enemy spellcasters it punishes.
- **Feasibility:** not implementable as-is — the mod has no readable enemy to pick and no target-ground point under an enemy; only a key in the ground-key list with a readable position is cast ground-wise, and that path only uses the caster's own feet.

**Your ruling:** ______________________________________________________________________________


#### 475. The Vial of Hashut  (slice 09)

- **Key(s):** `wh3_dlc23_item_abilities_the_vial_of_hashut`
- **Current logic:** `melee_unwavering` — in melee (not wavering): cast on self.
- **Game declares:** a hex aimed at ONE enemy unit (target_enemies = true, only_affect_target = true); 60 s: −60 Armour, −20 Weakness to Fire.
- **Why it makes no sense:** cast target — the vial's debuff is designed to be applied to the enemy; self-cast addresses the caster.
- **Feasibility:** not implementable as-is — enemy-targeted casts cannot be aimed by the mod.

**Your ruling:** ______________________________________________________________________________


#### 476. The Vortex Shard  (slice 09)

- **Key(s):** `wh2_main_item_abilities_the_vortex_shard`
- **Current logic:** `melee_unwavering` — in melee (not wavering): cast on self.
- **Game declares:** a hex of the winds aimed at ONE enemy unit (target_enemies = true); 31 s (becalms the enemy's magic).
- **Why it makes no sense:** cast target — the mod self-casts an ability that exists to be thrown at the enemy.
- **Feasibility:** not implementable as-is — no enemy targeting available.

**Your ruling:** ______________________________________________________________________________


#### 479. The Withering  (slice 09)

- **Key(s):** `wh3_dlc23_spell_bound_the_withering`, `wh3_twa08_spell_bound_the_withering`
- **Current logic:** `melee_unwavering` — in melee (not wavering): cast on self.
- **Game declares:** a bound Shadow hex aimed at ONE enemy unit (target_enemies = true); 40 s: −30 Armour, −8 Leadership.
- **Why it makes no sense:** cast target — a debuff cast on self; the enemy never receives it.
- **Feasibility:** not implementable as-is — enemy-targeted casts cannot be aimed by the mod.

**Your ruling:** ______________________________________________________________________________


#### 480. They Needs Stabbin'  (slice 09)

- **Key(s):** `wh2_dlc15_character_abilities_they_needs_stabbin`
- **Current logic:** `melee_unwavering` — in melee (not wavering): cast on self.
- **Game declares:** a hex aimed at ONE enemy unit (target_enemies = true; the game even restricts the victim to commander-class units); 29 s: −30 Armour, −24 Melee Defence.
- **Why it makes no sense:** cast target — the gobbos are told to stab a chosen enemy; the mod aims the cast at its own caster.
- **Feasibility:** not implementable as-is — the mod cannot pick or aim at an enemy unit.

**Your ruling:** ______________________________________________________________________________


#### 484. Titan Headsman  (slice 09)

- **Key(s):** `wh3_dlc25_hero_abilities_titan_headsman`
- **Current logic:** `melee_unwavering` — in melee (not wavering): cast on self.
- **Game declares:** a hex aimed at ONE enemy unit (target_enemies = true); 29 s: Speed ×0.55, −24 Melee Defence.
- **Why it makes no sense:** cast target — the crippling debuff must land on the enemy being finished off; the mod self-casts it.
- **Feasibility:** not implementable as-is — enemy-targeted casts cannot be aimed by the mod.

**Your ruling:** ______________________________________________________________________________


#### 485. Torment Blade  (slice 09)

- **Key(s):** `wh3_main_weapon_abilities_torment_blade`
- **Current logic:** `melee_unwavering` — in melee (not wavering): cast on self.
- **Game declares:** a weapon hex aimed at ONE enemy unit (target_enemies = true); 18 s: −24 Melee Attack, ×0.75 Base and AP Weapon Damage.
- **Why it makes no sense:** cast target — the paralysing venom is for the victim, not the wielder; self-cast is a wrong target.
- **Feasibility:** not implementable as-is — no enemy aiming available.

**Your ruling:** ______________________________________________________________________________


#### 486. Trickster's Shard  (slice 09)

- **Key(s):** `wh_main_item_abilities_tricksters_shard`
- **Current logic:** `melee_unwavering` — in melee (not wavering): cast on self.
- **Game declares:** an area-of-hexes cast on enemy ground (target_enemies = true, target_ground = true, 500 m intercept, 35 m area); 16 s: enemy Miscast Chance ×2.
- **Why it makes no sense:** cast target — the shard's curse must be placed among the enemy; the mod's self-cast puts (at best) the area on the caster.
- **Feasibility:** not implementable as-is — no readable enemy and no enemy-ground placement path in the mod.

**Your ruling:** ______________________________________________________________________________


#### 487. Trophy Heads  (slice 09)

- **Key(s):** `wh2_main_lord_abilities_trophy_heads`, `wh3_main_daemon_wings_abilities_trophy_heads`
- **Current logic:** `melee_unwavering` — in melee (not wavering): cast on self.
- **Game declares:** hexes aimed at ONE enemy unit (target_enemies = true; commander-class targets only); 36 s: −24 Melee Attack / −40 Melee Defence (base), −30 / −30 (daemon wings).
- **Why it makes no sense:** cast target — the terror debuff belongs on the enemy; the mod aims it at the caster.
- **Feasibility:** not implementable as-is — enemy-targeted casts cannot be aimed.

**Your ruling:** ______________________________________________________________________________


#### 496. Virulent Contagion  (slice 09)

- **Key(s):** `wh3_main_lord_abilities_virulent_contagion`
- **Current logic:** `melee_unwavering` — in melee (not wavering): cast on self.
- **Game declares:** a chain hex aimed at ONE enemy unit (spreads to up to 5 enemies); 30 s: −40 Melee Defence.
- **Why it makes no sense:** cast target — the plague is for the enemy formation; self-cast means the chain never starts.
- **Feasibility:** not implementable as-is — enemy-targeted casts cannot be aimed by the mod.

**Your ruling:** ______________________________________________________________________________


#### 497. Virulent Contagion Upgraded  (slice 09)

- **Key(s):** `wh3_main_lord_abilities_virulent_contagion_upgraded`
- **Current logic:** `melee_unwavering` — in melee (not wavering): cast on self.
- **Game declares:** chain hex aimed at ONE enemy unit (up to 5 affected); 30 s: −50 Melee Defence.
- **Why it makes no sense:** cast target — same mismatch as base Virulent Contagion: an enemy chain hex cast on the caster.
- **Feasibility:** not implementable as-is — no enemy aiming available.

**Your ruling:** ______________________________________________________________________________


#### 498. Visions of Madness  (slice 09)

- **Key(s):** `wh3_dlc27_qb_unit_abilities_visions_of_madness`
- **Current logic:** `melee_unwavering` — in melee (not wavering): cast on self.
- **Game declares:** a hex aimed at ONE enemy unit (up to 5 affected, 30 m intercept); 10 s: −16 Leadership, Rampage.
- **Why it makes no sense:** cast target — the madness is inflicted on the enemy; the mod aims the cast at itself.
- **Feasibility:** not implementable as-is — enemy-targeted casts cannot be aimed.

**Your ruling:** ______________________________________________________________________________


#### 499. Void Pendulum  (slice 09)

- **Key(s):** `wh3_main_item_abilities_void_pendulum`
- **Current logic:** `melee_unwavering` — in melee (not wavering): cast on self.
- **Game declares:** a hex of the winds aimed at ONE enemy unit (casting units only — invalid target flag `hasnt_casting_ability`); 25 s: shuts down the enemy spellcaster.
- **Why it makes no sense:** cast target — a targeted spellcaster hex cast on the caster; the caster is not the intended victim (and may not even be a legal one).
- **Feasibility:** not implementable as-is — no enemy targeting/selection path exists in the mod.

**Your ruling:** ______________________________________________________________________________


#### 500. Vorozheja's Foresight  (slice 09)

- **Key(s):** `wh3_dlc24_hero_abilities_vorozhejas_foresight`
- **Current logic:** `melee_unwavering` — in melee (not wavering): cast on self.
- **Game declares:** a hex aimed at ONE enemy unit (wind-up 3 s); 25 s: −12 Armour, −12 Missile Block Chance, −10 Missile Resistance.
- **Why it makes no sense:** cast target — the curse binds the enemy; the mod self-casts it.
- **Feasibility:** not implementable as-is — enemy-targeted casts cannot be aimed by the mod.

**Your ruling:** ______________________________________________________________________________


#### 503. Warden's Cage  (slice 09)

- **Key(s):** `wh2_dlc15_character_abilities_wardens_cage`
- **Current logic:** `melee_unwavering` — in melee (not wavering): cast on self.
- **Game declares:** direct damage aimed at ONE enemy unit (characters; strongly vs characters); 25 s: 20 damage per second, Can't Move, −60 Armour, −48 Melee Defence.
- **Why it makes no sense:** cast target — the cage must trap an enemy character; the mod casts it on the Warden itself (self-cast cannot cage the target).
- **Feasibility:** not implementable as-is — enemy-targeted casts cannot be aimed by the mod.

**Your ruling:** ______________________________________________________________________________


#### 504. Warp Gaze  (slice 09)

- **Key(s):** `wh_pro04_unit_abilities_warp_gaze`
- **Current logic:** `melee_unwavering` — in melee (not wavering): cast on self.
- **Game declares:** a hex aimed at ONE enemy unit (100 m intercept, ×3 uses); 12 s: the target Can't Move (the gaze pins the enemy).
- **Why it makes no sense:** cast target — an enemy-pinning hex cast on the caster; the enemy never gets pinned.
- **Feasibility:** not implementable as-is — no enemy aiming available.

**Your ruling:** ______________________________________________________________________________


#### 505. Warpstiletto  (slice 09)

- **Key(s):** `wh3_dlc29_item_abilities_warpstiletto`
- **Current logic:** `melee_unwavering` — in melee (not wavering): cast on self.
- **Game declares:** a hex aimed at ONE enemy unit (100 m intercept, ×2 uses); 20 s: the target Can't Move.
- **Why it makes no sense:** cast target — the stiletto's effect must land on the enemy; the mod addresses the cast to the caster.
- **Feasibility:** not implementable as-is — enemy-targeted casts cannot be aimed by the mod.

**Your ruling:** ______________________________________________________________________________


#### 509. Whip of Agony  (slice 09)

- **Key(s):** `wh2_twa03_weapon_abilities_whip_of_agony`
- **Current logic:** `melee_unwavering` — in melee (not wavering): cast on self.
- **Game declares:** a hex aimed at ONE enemy unit (75 m intercept); 29 s: −24 Melee Defence, Causes Fear, Causes Terror.
- **Why it makes no sense:** cast target — the pain is for the foe; self-cast is a wrong target.
- **Feasibility:** not implementable as-is — enemy-targeted casts cannot be aimed.

**Your ruling:** ______________________________________________________________________________


#### 510. Whip of Misery  (slice 09)

- **Key(s):** `wh2_main_spell_bound_whip_of_agony`
- **Current logic:** `melee_unwavering` — in melee (not wavering): cast on self.
- **Game declares:** a hex aimed at ONE enemy unit (large units only — invalid target flag `unit_is_not_large`, ×3 uses); 31 s: −30 Accuracy, −24 Melee Attack.
- **Why it makes no sense:** cast target — the misery is inflicted on the enemy; the mod self-casts it.
- **Feasibility:** not implementable as-is — no enemy aiming available.

**Your ruling:** ______________________________________________________________________________


#### 512. Whispering Mist  (slice 09)

- **Key(s):** `wh3_dlc29_hero_abilities_whispering_mist`
- **Current logic:** `melee_unwavering` — in melee (not wavering): cast on self.
- **Game declares:** a hex aimed at ONE enemy unit (wind-up 1 s); 32 s: Speed ×0.55, Charge Speed ×0.55.
- **Why it makes no sense:** cast target — the slowing mist must be placed on the enemy; the mod self-casts it.
- **Feasibility:** not implementable as-is — enemy-targeted casts cannot be aimed by the mod.

**Your ruling:** ______________________________________________________________________________


#### 515. Willing Prey  (slice 09)

- **Key(s):** `wh3_main_lord_abilities_willing_prey`
- **Current logic:** `melee_unwavering` — in melee (not wavering): cast on self.
- **Game declares:** a hex aimed at ONE enemy unit; 15 s: −24 Melee Attack, −40 Melee Defence.
- **Why it makes no sense:** cast target — the debuff is for the enemy; the mod aims the cast at the caster.
- **Feasibility:** not implementable as-is — no enemy aiming available.

**Your ruling:** ______________________________________________________________________________


#### 517. Word of Change  (slice 09)

- **Key(s):** `wh3_main_daemon_head_abilities_word_of_change`
- **Current logic:** `melee_unwavering` — in melee (not wavering): cast on self.
- **Game declares:** a hex of the winds aimed at ONE enemy unit (casting units only — `hasnt_casting_ability`); 42 s: enemy Miscast Chance ×2.
- **Why it makes no sense:** cast target — the word is spoken at an enemy spellcaster; the mod self-casts it.
- **Feasibility:** not implementable as-is — enemy-targeted casts cannot be aimed by the mod.

**Your ruling:** ______________________________________________________________________________


#### 518. Word of Pain  (slice 09)

- **Key(s):** `wh2_dlc10_spell_bound_word_of_pain`, `wh3_dlc27_spell_dark_magic_word_of_pain_bound_1use`
- **Current logic:** `melee_unwavering` — in melee (not wavering): cast on self.
- **Game declares:** a bound Dark Magic hex aimed at ONE enemy unit; 40 s: −30 Accuracy, −40 Melee Attack.
- **Why it makes no sense:** cast target — the agony is for the enemy; self-cast is a wrong target.
- **Feasibility:** not implementable as-is — enemy-targeted casts cannot be aimed by the mod.

**Your ruling:** ______________________________________________________________________________


#### 523. You're Next!  (slice 10)

- **Key(s):** `wh2_dlc15_lord_abilities_youre_next`
- **Current logic:** trigger `melee_unwavering` — fires when the unit is in melee and not wavering, then casts on itself (`perform_special_ability(key, unit)`; the badge tooltip reads "fires when this unit is in melee").
- **Game declares:** `wh_type_hex`, `target_enemies = true` only, `num_effected_enemy_units = 1` — a single-unit ENEMY hex: −24 melee attack, −40 melee defence, speed ×0.55 for 24 s; its invalid-target gate `unit_is_not_commander_class` further restricts the target to a commander-class enemy character.
- **Why it makes no sense:** the game's target is an enemy unit (a character), never the caster — a self-cast hands the engine a target the ability rejects and, even if accepted, would debuff the wrong side; the tracker's own intended rule was "cast at the enemy it is fighting".
- **Feasibility:** NOT implementable as-is — there is no enemy-unit read (no card, no id, no health) and enemy-targeted casts cannot be aimed by the mod; the engine form the mod uses cannot auto-pick the unit's current enemy either.

**Your ruling:** ______________________________________________________________________________


---

## Class B — Ally-targeted effects cast on self (34 entries)

The game's target is another friendly unit (usually one; the caster is excluded by the data). The mod self-casts, so the declared recipient never receives the effect. The slices mark all of these fixable in principle via the ally-picker pattern the mod already ships (`blood_sacrifice` shape: pick a friendly unit, conservative range, pre-cast re-check).

#### 198. Meat Feast  (slice 04)

- **Key(s):** `wh3_main_prisoners_butcher`
- **Current logic:** trigger `ushoran_health` - fires when the OWNER's health is at or below 75% (no melee gate) - then casts on self (default `perform_special_ability(key, unit)`; no cast_target is set).
- **Game declares:** An army-keyed single-target recover: Heals +2.8%/tick, Vigour -3%/s, "to allies in range" - target_friends = true, num_effected_friendly_units = 1, affect_self = false, target_self = false; the phase junction targets friends only. The game makes you pick ONE friendly unit; the caster is not among the legal targets and is not affected.
- **Why it makes no sense:** The effect lands on a friendly unit and never on the caster, yet the mod reads the caster's OWN health and points the cast at the caster - neither the trigger's health basis nor the cast target matches the declared target. A self-cast should be refused by the engine (self is not a legal target) or, if accepted, still applies the wrong way.
- **Feasibility:** Friendly units are readable - the mod already picks low-health allies (blood_sacrifice / eat_da_runts read `context_value(unit, "HealthPercent")` per friendly unit). An ally-heal picker (lowest-health in range) is the matching implementation; as-is the logic does not fit.

**Your ruling:** ______________________________________________________________________________


#### 199. Captain of the Phoenix Guard  (slice 04)

- **Key(s):** `wh3_dlc27_character_abilities_captain_of_the_phoenix_guard`
- **Current logic:** trigger `melee_health75` - in melee AND the owner at or below 75% health - then casts on self.
- **Game declares:** A single friendly unit is the only target: Physical Resistance +30 and Heals +0.5%/tick, "to allies in range" - target_friends = true, target_self = false, num_effected_friendly_units = 1, only_affect_target = true, affect_self = false; the phase junction targets friends only.
- **Why it makes no sense:** The game declares one friendly unit as the target and applies the effect ONLY to that target, but the mod fires on the caster's own health and casts on the caster - a target the game does not list. The buff is intended for another unit (a hurt ally), not for the caster.
- **Feasibility:** Friendly health is readable (same reads as the ally-heal pattern already shipped for blood_sacrifice / eat_da_runts); an ally picker fixes the target, and the trigger could then key off the chosen ally's health instead of the caster's.

**Your ruling:** ______________________________________________________________________________


#### 204. Da Boss 'as a Plan!  (slice 04)

- **Key(s):** `wh3_dlc26_character_abilities_da_boss_as_a_plan`
- **Current logic:** trigger `melee_unwavering` - in melee, not routing or wavering (fail-open morale) - then casts on self.
- **Game declares:** Single-friendly buff: Melee Defence +24, Leadership +8, Expert Charge Defence "to allies in range" - target_friends = true, target_self = false, num_effected_friendly_units = 1, affect_self = false; the phase junction targets friends only.
- **Why it makes no sense:** The declared target is one friendly unit and the buff never includes the caster, yet the mod casts on the caster - a unit the game does not offer as a target (the mod's own tracker row already carries the "cast on self for now (nearest-ally picker later)" caveat).
- **Feasibility:** Friendly units are readable and the ally-picker pattern is already proven in this mod (blood_sacrifice / eat_da_runts / glorious_death pass a chosen friendly unit as the cast target); the fix is a picker, not new reads.

**Your ruling:** ______________________________________________________________________________


#### 209. Favour of the Fay  (slice 04)

- **Key(s):** `wh_dlc07_lord_abilities_favour_of_the_fay`
- **Current logic:** trigger `melee_unwavering` then casts on self.
- **Game declares:** Single-friendly buff: Melee Attack +40 - target_friends = true, target_self = false, num_effected_friendly_units = 1, affect_self = false; the game row gives friends as the target class.
- **Why it makes no sense:** The declared target is one friendly unit; the mod casts on the caster, which is not among the game's legal targets (the tracker row itself says "cast on self for now (nearest-ally picker later)").
- **Feasibility:** Friendly reads available; an ally picker matches the ability. As-is the self-cast does not match the declared target.

**Your ruling:** ______________________________________________________________________________


#### 214. Fury of Khaine  (slice 04)

- **Key(s):** `wh2_main_unit_abilities_fury_of_khaine`
- **Current logic:** trigger `charge_or_melee` - charge window OR in melee (not routing) - then casts on self.
- **Game declares:** Single-friendly buff: Melee Attack +24, Armour-Piercing Weapon Damage +50%, Base Weapon Damage +50%, Rampage! "to allies in range" - target_friends = true, target_self = false, num_effected_friendly_units = 1, affect_self = false; the phase junction targets friends only.
- **Why it makes no sense:** The effect and its single target are an ally's (the wielder fires up another unit - e.g. the cauldron's Death Hags buff a chosen regiment), but the mod casts on the caster. The trigger itself (charge/melee) fits a melee buff, but the cast target does not.
- **Feasibility:** Ally picker (friendly units readable, pattern already shipped); as-is the self-cast targets the wrong unit.

**Your ruling:** ______________________________________________________________________________


#### 220. Helping Hand  (slice 04)

- **Key(s):** `wh2_pro08_character_abilities_helping_hand`
- **Current logic:** trigger `melee_unwavering` then casts on self.
- **Game declares:** Ally-anchored buff: Melee Attack +40, Damage Resistance +40 "to allies in range" - target_friends = true, target_self = false, affect_self = false, num_fr = -1; the phase junction targets friends only (the caster is never in the effect scope).
- **Why it makes no sense:** The ability is cast at a friendly unit and buffs the friends around it while excluding the caster - yet the mod self-casts. Self is not a legal target and the caster is not affected, so the cast cannot deliver what the trigger is waiting for (the tracker row: "cast on self for now (nearest-ally picker later)").
- **Feasibility:** Friendly reads available; a nearest-ally picker matches the ability.

**Your ruling:** ______________________________________________________________________________


#### 222. Inspired Assault I  (slice 04)

- **Key(s):** `wh3_main_lord_abilities_inspired_assault_i`
- **Current logic:** trigger `charge_or_melee` then casts on self.
- **Game declares:** Single-friendly buff: Charge Bonus +20%, Melee Attack +24 "to allies in range" - target_friends = true, target_self = false, num_effected_friendly_units = 1, affect_self = false.
- **Why it makes no sense:** The charge bonus is meant for a unit on its way into combat - the game makes you target a friendly unit; the mod casts on the caster, which is not a declared target. (The trigger fits the effect; the cast target does not.)
- **Feasibility:** Ally picker (friendly units readable; the picker pattern already ships). As-is the self-cast does not match.

**Your ruling:** ______________________________________________________________________________


#### 223. Inspired Assault II  (slice 04)

- **Key(s):** `wh3_main_lord_abilities_inspired_assault_ii`
- **Current logic:** trigger `charge_or_melee` then casts on self.
- **Game declares:** Single-friendly buff: Charge Bonus +40%, Melee Attack +24 "to allies in range" - target_friends = true, target_self = false, num_fr = 1, affect_self = false.
- **Why it makes no sense:** Same mismatch as Inspired Assault I: the game's target is one friendly unit, the mod casts on the caster.
- **Feasibility:** Ally picker; friendly reads available.

**Your ruling:** ______________________________________________________________________________


#### 224. Inspired Assault III  (slice 04)

- **Key(s):** `wh3_main_lord_abilities_inspired_assault_iii`
- **Current logic:** trigger `charge_or_melee` then casts on self.
- **Game declares:** Single-friendly buff: Charge Bonus +40%, Melee Attack +40 "to allies in range" - target_friends = true, target_self = false, num_fr = 1, affect_self = false.
- **Why it makes no sense:** Same mismatch: declared target is one friendly unit; the mod self-casts.
- **Feasibility:** Ally picker; friendly reads available.

**Your ruling:** ______________________________________________________________________________


#### 225. Inspired Defence I  (slice 04)

- **Key(s):** `wh3_main_lord_abilities_inspired_defence_i`
- **Current logic:** trigger `melee_unwavering` then casts on self.
- **Game declares:** Single-friendly buff: Melee Defence +24, Leadership +16 "to allies in range" - target_friends = true, target_self = false, num_fr = 1, affect_self = false.
- **Why it makes no sense:** Declared target is one friendly unit; the mod casts on the caster (the tracker row: "cast on self for now (nearest-ally picker later)").
- **Feasibility:** Ally picker; friendly reads available.

**Your ruling:** ______________________________________________________________________________


#### 226. Inspired Defence II  (slice 04)

- **Key(s):** `wh3_main_lord_abilities_inspired_defence_ii`
- **Current logic:** trigger `melee_unwavering` then casts on self.
- **Game declares:** Single-friendly buff: Melee Defence +24, Leadership +16, Expert Charge Defence "to allies in range" - target_friends = true, target_self = false, num_fr = 1, affect_self = false.
- **Why it makes no sense:** Declared target is one friendly unit; the mod self-casts.
- **Feasibility:** Ally picker; friendly reads available.

**Your ruling:** ______________________________________________________________________________


#### 227. Inspired Defence III  (slice 04)

- **Key(s):** `wh3_main_lord_abilities_inspired_defence_iii`
- **Current logic:** trigger `melee_unwavering` then casts on self.
- **Game declares:** Single-friendly buff: Melee Defence +40, Leadership +16, Expert Charge Defence "to allies in range" - target_friends = true, target_self = false, num_fr = 1, affect_self = false.
- **Why it makes no sense:** Declared target is one friendly unit; the mod self-casts.
- **Feasibility:** Ally picker; friendly reads available.

**Your ruling:** ______________________________________________________________________________


#### 238. Orcs are da Best!  (slice 05)

- **Key(s):** `wh3_dlc26_character_abilities_orcs_are_da_best`
- **Current logic:** trigger `melee_unwavering` (in melee, not routing, not wavering) → plain self-cast (`perform_special_ability(key, unit)`; no cast_target is set).
- **Game declares:** a single-FRIENDLY-unit augment — `target_friends = true`, `num_effected_friendly_units = 1`, `target_self = false`, `affect_self = false` (intercept 150 m; +24 melee attack, ×1.5 damage for 27 s); its phase is friends-only (`self = false`).
- **Why it makes no sense:** the cast lands on the owner, which the data excludes both as a target and as an affected unit — the buff never reaches the friendly unit, and the questionnaire's own note ("cast on self for now, nearest-ally picker later") confirms the ally is the intended recipient.
- **Feasibility:** not implementable as written (self-cast cannot deliver it), but implementable overall — friendly units are fully readable and the ally-target cast pattern already exists (FOURTH.cast_target + drift re-check, the blood-sacrifice shape); it needs an ally picker.

**Your ruling:** ______________________________________________________________________________


#### 239. Overseer of the Unseen  (slice 05)

- **Key(s):** `wh3_dlc29_hero_active_overseer_of_the_unseen`
- **Current logic:** trigger `melee_unwavering` → self-cast.
- **Game declares:** one friendly unit (`target_friends = true`, `num_effected_friendly_units = 1`, `target_self = false`), `only_affect_target = true`; invalid targets `unit_is_commander_class` and `unit_is_large` (+40 melee attack, cannot die, unbreakable for 44 s). In other words: cast on a non-commander, non-large friendly unit.
- **Why it makes no sense:** the owner is a hero (commander class) — as the cast target it is an INVALID target under the db's own invalid-target flags, so the intended foot-unit recipient never gets the effect and the self-cast has no declared target.
- **Feasibility:** implementable via an ally picker over readable friendly units, filtering by `unit:type()` (the land-units key the mod already reads) for the commander/large exclusions; not as currently written.

**Your ruling:** ______________________________________________________________________________


#### 250. "Stay Here, I'll Get Help!"  (slice 05)

- **Key(s):** `wh2_dlc09_character_abilities_stay_here_ill_get_help`
- **Current logic:** trigger `wavering_ally_range` — picks the closest wavering, non-routing ally within the conservative 25 m and re-checks the gap before firing — but the cast itself stays ON SELF (its own log line reads "self-cast"); the picked ally is never passed as the cast target.
- **Game declares:** friend/ground/self targeting (intercept 60 m); its morale phase affects FRIENDS only (`self = false`, +16 morale, 35 m) while a second phase grants the caster stalk/unspottable; and `invalid_usage: engaged_in_melee` (it cannot be used while the caster is engaged in melee).
- **Why it makes no sense:** the user-approved criterion and the tracker row say "cast on that ally" — the ally is selected, yet the cast does not use it; the self-anchor only reaches the ally through the friends-phase area, which is not the declared ally-targeted cast, and the evaluator never gates on the engaged-in-melee usage restriction.
- **Feasibility:** the ally is already picked and range-checked (FOURTH.wa_ally); passing it as the cast target is the existing blood-sacrifice pattern — implementable. Attempts while the caster is in melee will be engine-refused and simply feed the cooldown hold.

**Your ruling:** ______________________________________________________________________________


#### 305. Daemonic Whispers  (slice 06)

- **Key(s):** `wh3_dlc27_character_abilities_slezuzus_voice`
- **Current logic:** trigger `melee_unwavering` — fires when the owner is in melee, cast on self.
- **Game declares:** an Augment that may target only a friendly unit (`target_friends=true`, `target_self=false`, `affect_self=false`, one unit, 200 m) — +16 Leadership to the chosen ally.
- **Why it makes no sense:** the game offers no self target for it (self is not in the target set), so the self-cast cannot deliver the declared buff to a friendly unit — the mod casts it on the one unit the ability does not accept.
- **Feasibility:** friendly units are readable and the mod already ships ally-targeting evaluators, so an ally picker could carry it — but as written the self-cast is the wrong target; flag for the user.

**Your ruling:** ______________________________________________________________________________


#### 343. Grut's Sickle  (slice 06)

- **Key(s):** `wh3_main_item_abilities_gruts_sickle`
- **Current logic:** trigger `melee_unwavering` — fires when the owner is in melee, cast on self.
- **Game declares:** an Augment of the Winds that may target only a friendly unit (`target_friends=true`, `target_self=false`, `affect_self=false`, one unit, 100 m) — Power Recharge +80% and Reserves +0.4/s to the chosen ally, at a health cost, ×3 uses.
- **Why it makes no sense:** the ability's target set is a friendly unit, and the caster is not among the legal targets (self-targeting is off) — so the self-cast cannot deliver the winds buff it declares.
- **Feasibility:** friendly units are readable and an ally picker could carry it; as written the self-cast is the wrong target; flag for the user.

**Your ruling:** ______________________________________________________________________________


#### 349. Hellish Vigour  (slice 07)

- **Key(s):** `wh3_dlc29_lord_abilities_hellish_vigour`
- **Current logic:** Rides `melee_unwavering` - fires when the unit is in melee, not routing and not wavering; the cast passes the owner itself as the target (`perform_special_ability(key, owner)`).
- **Game declares:** A single FRIENDLY-unit augment (`target_friends=true`, `num_effected_friendly_units=1`, cast range 75 m): +20 damage reflection and reduced fatigue for 25 s. The caster is NOT among the affected: `affect_self=false`, `target_self=false`, and the phase targets friends only.
- **Why it makes no sense:** Casting it on the owner applies the augment to nobody - the caster is excluded from its own effect. It is a targeted hand-out to another friendly unit ('drives his host onward'), and a self-cast cannot deliver it.
- **Feasibility:** Fixable without enemy reads: friendly units are readable and the mod already ships ally-targeted casts (Glorious Death / Blood Sacrifice pattern); the tracker itself notes 'nearest-ally picker later'. Needs an ally picker, not enemy reads.

**Your ruling:** ______________________________________________________________________________


#### 361. Inspired Marksmanship I  (slice 07)

- **Key(s):** `wh3_main_lord_abilities_inspired_marksmanship_i`
- **Current logic:** Rides `melee_unwavering` - fires when the unit is in melee, not routing and not wavering; the cast passes the owner itself as the target (`perform_special_ability(key, owner)`).
- **Game declares:** A single-friendly augment that may only be placed on a unit that can perform missile attacks (invalid-target flag `cannot_perform_missile_attack`): +30 accuracy, +20 reloading for 29 s, range 100 m; the caster is not affected (`affect_self=false`).
- **Why it makes no sense:** The self-cast can receive nothing (ally-only, caster unaffected), and firing a shooting buff while the owner is stuck in melee is mistimed on both counts - the effect wants an ally that is actually shooting.
- **Feasibility:** Feasible in principle with the friendly reads the mod already has (plus a static missile-capability gate, which the mod's own API notes record as available); no enemy reads needed. The ally picker does not exist yet.

**Your ruling:** ______________________________________________________________________________


#### 362. Inspired Marksmanship II  (slice 07)

- **Key(s):** `wh3_main_lord_abilities_inspired_marksmanship_ii`
- **Current logic:** Rides `melee_unwavering` - fires when the unit is in melee, not routing and not wavering; the cast passes the owner itself as the target (`perform_special_ability(key, owner)`).
- **Game declares:** Same as I but +60 accuracy, +20 reloading for 44 s, range 100 m; same `cannot_perform_missile_attack` invalid-target flag.
- **Why it makes no sense:** Same mismatch: single-ally missile buff cast on the owner, who is not affected and is in melee when the trigger fires.
- **Feasibility:** Same as I: ally picker feasible (friendly reads exist); not enemy-limited.

**Your ruling:** ______________________________________________________________________________


#### 363. Inspired Marksmanship III  (slice 07)

- **Key(s):** `wh3_main_lord_abilities_inspired_marksmanship_iii`
- **Current logic:** Rides `melee_unwavering` - fires when the unit is in melee, not routing and not wavering; the cast passes the owner itself as the target (`perform_special_ability(key, owner)`).
- **Game declares:** Same as II with +40 reloading, 44 s, range 100 m; same `cannot_perform_missile_attack` invalid-target flag.
- **Why it makes no sense:** Same mismatch as I/II.
- **Feasibility:** Same as I/II: ally picker feasible; not enemy-limited.

**Your ruling:** ______________________________________________________________________________


#### 364. Iron-Handed Captain  (slice 07)

- **Key(s):** `wh3_dlc27_character_abilities_iron_hand_captain`
- **Current logic:** Rides `melee_unwavering` - fires when the unit is in melee, not routing and not wavering; the cast passes the owner itself as the target (`perform_special_ability(key, owner)`).
- **Game declares:** A rally for a broken ally: single friendly target (`only_affect_target=true`, range 200 m) that the game only allows on a unit whose morale is at or below 'broken' (invalid-target flag `morale_is_higher_than_broken`); grants +100 morale and the `force_rally` attribute for 42 s. Caster not affected (`affect_self=false`, phase friends-only).
- **Why it makes no sense:** Target and premise are both inverted: the mod fires it when the CASTER is in melee and specifically NOT wavering, and casts it on the caster - who is neither a valid target (`target_self=false`) nor broken. The ally it exists to rally is never involved.
- **Feasibility:** A fleeing-ally pick is conceivable in principle (friendly routing state is readable - `unit_is_routing` is already used on allies); the current self-cast cannot work. Not enemy-limited.

**Your ruling:** ______________________________________________________________________________


#### 383. Merciw's Monstrous Regiment  (slice 07)

- **Key(s):** `wh3_dlc20_cataclysm_bound_merciws_monstrous_regiment`, `wh3_dlc27_cataclysm_bound_merciws_monstrous_regiment`
- **Current logic:** Rides `melee_unwavering` - fires when the unit is in melee, not routing and not wavering; the cast passes the owner itself as the target (`perform_special_ability(key, owner)`).
- **Game declares:** A single chosen ALLY receives +40 Melee Attack, +50% melee damage and +20 physical resistance for 120 s (`target_friends=true`, `num_effected_friendly_units=1`, `affect_self=false`; both bound keys - `wh3_dlc20_...` and `wh3_dlc27_...` - share the same phase). Caster not affected.
- **Why it makes no sense:** Ally-only single-target buff cast on the owner: the caster gains nothing from its own cast, and no ally is selected. ('Bestows it upon his chosen allies' - the chosen ally is the whole point.)
- **Feasibility:** Ally picker feasible with the friendly reads already in use (Glorious Death / Blood Sacrifice pattern); no enemy reads needed.

**Your ruling:** ______________________________________________________________________________


#### 439. Shock Collar  (slice 08)

- **Key(s):** `wh2_dlc16_hero_abilities_shock_collar`
- **Current logic:** trigger `melee_unwavering`; in-melee self-cast.
- **Game declares:** an Augment for one friendly unit (`target_friends=true`, `target_self=false`, `num_effected_friendly_units=1`, cast at a friendly unit within 100 m): +24 melee attack, +16 leadership, immune to psychology for 24 s; 60 s recharge. The tracker's own proposal: "When morale falls to wavering: cast on the wavering friendly unit."
- **Why it makes no sense:** the effect is single-unit and aimed at another friendly unit; self is not a declared target for the cast, so casting it on the caster buffs the wrong unit (or is refused) — the intended buff never lands where the tracker's plan puts it.
- **Feasibility:** feasible with existing reads — the mod already ships this exact ally-picker pattern for other triggers (`blood_sacrifice`: lowest-health in-range ally, conservative range, pre-cast range re-check) and uses a 25 m trigger radius against the game's 100 m cast range; no enemy reads involved.

**Your ruling:** ______________________________________________________________________________


#### 495. Verminous Fury  (slice 09)

- **Key(s):** `wh3_dlc29_lord_abilities_verminous_fury`
- **Current logic:** `melee_unwavering` — in melee (not wavering): cast on self.
- **Game declares:** an augment cast on a friendly unit — the caster itself is not a valid target (target_friends = true, target_self = false, affect_self = false); 60 s: Rampage, Unbreakable, Unyielding Assault — a buff meant for a follower, not the Warbringer.
- **Why it makes no sense:** cast target — an ally-targeted effect cast on self; the engine offers self as no target for this ability, so the buff cannot land on the caster as intended here.
- **Feasibility:** fixable in principle but not built — the mod already reads friendly units and passes an ally target for other abilities (the ally-picker pattern); this entry has no picker and self-casts.

**Your ruling:** ______________________________________________________________________________


#### 508. Where You Goin!?  (slice 09)

- **Key(s):** `wh3_dlc26_character_abilities_were_you_goin`
- **Current logic:** `melee_unwavering` — in melee (not wavering): cast on self.
- **Game declares:** an augment cast on a friendly unit — self is not a valid target (target_friends = true, target_self = false, affect_self = false); 25 s: Unbreakable — the Bruiser flings a fleeing ally back into the fight.
- **Why it makes no sense:** cast target — an ally-targeted effect cast on self; the recipient is meant to be another unit, and the game does not offer the caster as one.
- **Feasibility:** fixable in principle but not built — the mod can read friendly units and already passes an ally target elsewhere (ally-picker pattern); this entry has none.

**Your ruling:** ______________________________________________________________________________


#### 511. Whiplash!  (slice 09)

- **Key(s):** `wh2_dlc14_lord_abilities_whiplash`
- **Current logic:** `melee_unwavering` — in melee (not wavering): cast on self.
- **Game declares:** an augment cast on a friendly unit — and commander-class units are invalid targets (`unit_is_commander_class`; the Beastmaster whips the *beasts*); 21 s: Charge Speed ×1.25, Charge Bonus ×1.2, Weapon Damage ×1.5.
- **Why it makes no sense:** cast target — an ally-targeted effect cast on self, and the caster (a commander-class character) is precisely the kind of unit the game forbids as a recipient; the buff can never apply to the caster.
- **Feasibility:** fixable in principle but not built — needs the ally-picker pattern (the mod already casts on friendly units elsewhere), plus the beast/non-commander recipient choice.

**Your ruling:** ______________________________________________________________________________


#### 534. Elvish Healing Herbs  (slice 10)

- **Key(s):** `wh3_dlc27_unit_abilities_elfish_healing_herbs`
- **Current logic:** trigger `ushoran_health` — fires when the unit's own health ≤75% and casts on itself.
- **Game declares:** single-target friendly heal (27 s regen at ~0.6%/s, −1% fatigue); `target_friends = true`, `only_affect_target = true`, and NO `target_self` / `affect_self` / `always_affect_self` — the target must be ANOTHER friendly unit.
- **Why it makes no sense:** self is not a legal target for this ability, so the mod's self-cast cannot heal anything (the tracker's intended rule was "cast on the hurt friendly unit").
- **Feasibility:** an ally-targeted version is buildable (friendly units/health/distance are readable — the `blood_sacrifice` pattern), but as wired on the self-health trigger the cast targets the caster.

**Your ruling:** ______________________________________________________________________________


#### 540. Makaisson's Persuader  (slice 10)

- **Key(s):** `wh3_dlc25_weapon_abilities_makaissons_persuader`
- **Current logic:** trigger `ushoran_health` — fires at the unit's own ≤75% health and casts on itself.
- **Game declares:** single-target repair — "a damaged War Machine can be returned to working order", effect HP regen + `replenish_ammo = 0.3` (ammo exists only on war machines), and its invalid-target gate `unit_is_not_artillery_or_war_machine` (the same gate carried by Malakai's/Chaos Dwarf war-machine passives) restricts the legal target to an artillery/war-machine friendly unit.
- **Why it makes no sense:** the carrier is a character (the ability is granted by the Makaisson's Persuader weapon), not a war machine — the self-cast points the repair at a unit the ability's own gate excludes and that has no ammo to replenish.
- **Feasibility:** a friendly-target version is buildable (friendly reads exist; the war-machine class could be derived from the game's data like the Slayer list), but the current self-cast cannot land.

**Your ruling:** ______________________________________________________________________________


#### 543. Patch Up  (slice 10)

- **Key(s):** `wh2_dlc13_character_abilities_patch_up`
- **Current logic:** trigger `ushoran_health` — fires at the unit's own ≤75% health and casts on itself.
- **Game declares:** single-target friendly heal (7 s regen at 1.6%/s) — "swiftly dress the wounds of targeted friendly units"; `target_friends = true` with no self target and no self effect (no `target_self`/`affect_self`/`always_affect_self`).
- **Why it makes no sense:** the ability can only be pointed at another friendly unit; a self-cast targets the caster, which the ability cannot affect, so the heal can never land.
- **Feasibility:** ally-targeting is buildable (readable friendlies), but not as wired on this self-cast trigger.

**Your ruling:** ______________________________________________________________________________


#### 548. Reforge  (slice 10)

- **Key(s):** `wh3_dlc23_character_abilities_reforge`
- **Current logic:** trigger `ushoran_health` — fires at the unit's own ≤75% health and casts on itself.
- **Game declares:** restores the hitpoints of "units with the Hell-Forged attribute" (UiEffect bullet verbatim: "Restores the hitpoints of units with the Hell-Forged attribute"); its invalid-target gate `unit_is_not_hellforged` encodes the same restriction, and the ability's owners are Daemonsmith Sorcerers — flesh-and-blood casters, not Hell-Forged units.
- **Why it makes no sense:** the Daemonsmith is not Hell-Forged, so a self-cast targets a unit the ability's own gate excludes (the row's `target_self = true` is contradicted by the effect bullet and the gate that CA ships for this key); no healing happens.
- **Feasibility:** could be re-scoped to target a friendly Hell-Forged unit (friendly reads exist; attribute keys derivable from game data), but the current self-cast cannot land.

**Your ruling:** ______________________________________________________________________________


#### 551. Remouldered  (slice 10)

- **Key(s):** `wh2_dlc16_lord_abilities_remouldered`
- **Current logic:** trigger `ushoran_health` — fires at the unit's own ≤75% health and casts on itself.
- **Game declares:** single-target friendly heal plus a 24 s combat buff (+24 melee attack, +8 morale) for a wounded MONSTER ("keep wounded monsters alive and keen"); `target_friends = true` with NO `target_self` — the exact target shape of Throt's Shock Collar, which is cast on his beasts, not himself.
- **Why it makes no sense:** the caster (Throt) is not the declared target of this ability; casting it at itself hands the engine a target the data does not declare (the tracker's intended rule was "cast on the hurt friendly unit"), so the heal/buff does not land where the ability is designed to go.
- **Feasibility:** an ally-targeted version is buildable (friendly reads exist; the monster-class gate could be derived from game data), but the current self-cast is wrong.

**Your ruling:** ______________________________________________________________________________


#### 552. Restore  (slice 10)

- **Key(s):** `wh2_dlc09_character_abilities_restore`
- **Current logic:** trigger `ushoran_health` — fires at the unit's own ≤75% health and casts on itself.
- **Game declares:** single-target friendly heal (24 s regen) whose invalid-target gate `unit_is_not_construct` restricts the target to a Tomb Kings CONSTRUCT; `target_friends = true` with no self target or self effect; the owner is a Necrotect.
- **Why it makes no sense:** the Necrotect is not a construct and self is not a declared target — the mod's self-cast can never apply the heal.
- **Feasibility:** a friendly-construct target is in principle selectable (readable friendlies; construct keys derivable), but not as wired.

**Your ruling:** ______________________________________________________________________________


#### 553. Revivification Crystal  (slice 10)

- **Key(s):** `wh2_main_unit_abilities_revivification_crystal`
- **Current logic:** trigger `ushoran_health` — fires at the unit's own ≤75% health and casts on itself.
- **Game declares:** single-target friendly heal plus resurrect (20 s, 0.5%/s); `target_friends = true` with no self target and no self effect; the owner is a Bastiladon whose crystal restores "supplicants" — other units — from the point of death.
- **Why it makes no sense:** the caster cannot be the target of its own crystal; the self-cast heals/resurrects nothing.
- **Feasibility:** ally-targeting is buildable (readable friendlies), but not as wired.

**Your ruling:** ______________________________________________________________________________


---

## Class C — Ground-targeted casts sent via the unit form (11 entries)

The ability's declared target is the ground (`target_ground = true`; self is not a declared target). The matching form is the ground-cast path (`perform_special_ability_ground` at the unit's own feet via `FOURTH.ground_keys`), which the mod already ships for Tactician's Stand Your Ground — these keys are not in it, so they fire the plain unit form at the caster instead.

#### 200. Cash Cascade  (slice 04)

- **Key(s):** `wh3_dlc26_character_abilities_cash_cascade`
- **Current logic:** trigger `charge_or_melee` - charge window OR in melee (not routing) - then casts on self.
- **Game declares:** Area augment: Charge Bonus +25%, Melee Attack +24, Leadership +8 "to self and allies". The game declares friends AND ground as the selectable targets: target_friends = true, target_ground = true, target_self = false, num_fr = -1, range 35 m, target_intercept_range 200 m.
- **Why it makes no sense:** Self is not a declared cast target - the game makes you aim this at a friendly unit or a ground point. The mod passes the caster as the unit target, which the engine may reject or re-interpret; the cast shape does not match the declared targeting.
- **Feasibility:** The class is exactly what the mod's own ground-cast doctrine describes ("the correct call for a key whose db row has target_ground = true"): the same tagging (friends + ground) is why Tactician's Stand Your Ground got the ground form. FOURTH.ground_cast exists and the own position is readable - one line in ground_keys (or an ally pick) applies.

**Your ruling:** ______________________________________________________________________________


#### 208. Empowering Shrooms  (slice 04)

- **Key(s):** `wh3_dlc26_character_abilities_empowering_shrooms`
- **Current logic:** trigger `melee_unwavering` then casts on self.
- **Game declares:** Ally area augment: Melee Attack +24, Leadership +16, Stops Rampage! "to allies in range" - target_friends = true, target_ground = true, target_self = false, num_fr = -1, range 35 m, intercept 100 m.
- **Why it makes no sense:** Self is not a declared target; the game asks for a friendly unit or a ground point (the area then covers the friends around it). The mod self-casts, so the cast shape contradicts the declared targeting.
- **Feasibility:** Ground form (cast at own feet via FOURTH.ground_cast) or an ally pick both match this class; the helper and the position read already exist.

**Your ruling:** ______________________________________________________________________________


#### 216. Gaze of Khaine  (slice 04)

- **Key(s):** `wh2_dlc10_lord_abilities_gaze_of_khaine`
- **Current logic:** trigger `melee_unwavering` then casts on self.
- **Game declares:** Area augment to self and allies: Melee Attack +24, AP +25%, Base +25%, Leadership +8 - but the ONLY declared target is the ground: target_ground = true, target_friends = false, target_self = false, num_fr = -1, range 35 m, intercept 100 m.
- **Why it makes no sense:** The game declares a ground-targeted cast (the area is placed at a point), and even the project's own approved activation for this key says "cast at own feet (existing ground-cast path)" - yet the shipped entry passes the unit target instead of the ground form.
- **Feasibility:** Own position is readable and FOURTH.ground_cast already exists for exactly this call shape; adding the key to ground_keys (cast at own feet) matches both the game data and the tracker's approved plan.

**Your ruling:** ______________________________________________________________________________


#### 218. Gulyas  (slice 04)

- **Key(s):** `wh3_dlc24_lord_abilities_gulyas`
- **Current logic:** trigger `ushoran_health` - owner at or below 75% health, no melee gate - then casts on self.
- **Game declares:** Area regeneration placed at a ground point: Heals +0.08%/tick, Leadership +4, Vigour -1%/s "to self and allies" (up to 5 friendly units) - target_ground = true, target_self = false, target_friends = false, num_fr = 5, range 35 m.
- **Why it makes no sense:** The only declared target is the ground; the mod passes the unit target. The project itself planned "cast at own feet (existing ground-cast path)" for this key, but the shipped entry is a plain self-cast.
- **Feasibility:** Ground form via FOURTH.ground_cast (own position readable) implements the approved plan; the trigger (own health <= 75%, health-only) fits the self+allies heal once the cast shape is right.

**Your ruling:** ______________________________________________________________________________


#### 229. Massacre  (slice 04)

- **Key(s):** `wh3_main_prisoners_massacre`
- **Current logic:** trigger `melee_unwavering` then casts on self.
- **Game declares:** Ally area augment: Melee Attack +24, AP +25%, Base +25% "to allies in range" - target_friends = true, target_ground = true, target_self = false, num_fr = -1, range 35 m.
- **Why it makes no sense:** Self is not a declared target; the game asks for a friendly unit or a ground point. The mod self-casts, so the cast shape contradicts the declared targeting.
- **Feasibility:** Ground form (FOURTH.ground_cast) or an ally pick matches the class; the helper and position read exist.

**Your ruling:** ______________________________________________________________________________


#### 230. Master of Alchemy  (slice 04)

- **Key(s):** `wh3_main_lord_abilities_master_of_alchemy`
- **Current logic:** trigger `metallurgy_melee` - owner in melee OR an in-melee ally within 25 m - casts on the OWNER (self).
- **Game declares:** Area augment: Base Missile Damage +25%, Base Weapon Damage +30%, Magical Attacks "to self and allies" - target_friends = true, target_ground = true, target_self = FALSE, num_fr = -1, range 35 m. (Its sibling keys Enchanted Metallurgy DO declare target_self = true; these Alchemy keys do not.)
- **Why it makes no sense:** The shared metallurgy evaluator always self-casts - legal for Enchanted Metallurgy (target_self = true) but not for this row, where self is not a declared target and the game asks for a friendly unit or a ground point.
- **Feasibility:** The evaluator already knows a qualifying in-melee ally (FOURTH.mtl_ally) and could pass it as the cast target, or the ground form could place the aura at the caster's feet; both reads exist.

**Your ruling:** ______________________________________________________________________________


#### 231. Master of Alchemy: Flaming  (slice 04)

- **Key(s):** `wh3_main_lord_abilities_master_of_alchemy_flaming`
- **Current logic:** trigger `metallurgy_melee` then casts on the owner (self).
- **Game declares:** Area augment: Base Missile Damage +50%, Base Weapon Damage +60%, Magical Attacks, Flaming Attacks "to self and allies" - target_friends = true, target_ground = true, target_self = false, num_fr = -1, range 35 m.
- **Why it makes no sense:** Same class as Master of Alchemy: self is not a declared target; the shared evaluator self-casts anyway.
- **Feasibility:** Ally pick (mtl_ally) or ground form at own feet; both supported by existing reads.

**Your ruling:** ______________________________________________________________________________


#### 232. Master of Alchemy: Piercing  (slice 04)

- **Key(s):** `wh3_main_lord_abilities_master_of_alchemy_piercing`
- **Current logic:** trigger `metallurgy_melee` then casts on the owner (self).
- **Game declares:** Area augment: AP Missile +25%, Base Missile +25%, AP Weapon +25%, Base Weapon +25%, Magical Attacks "to self and allies" - target_friends = true, target_ground = true, target_self = false, num_fr = -1, range 35 m.
- **Why it makes no sense:** Same class: self not a declared target; the evaluator self-casts.
- **Feasibility:** Ally pick or ground form; reads available.

**Your ruling:** ______________________________________________________________________________


#### 249. Star of Avelorn  (slice 05)

- **Key(s):** `wh2_dlc10_item_abilities_star_of_avelorn`
- **Current logic:** trigger `ushoran_health` (own health ≤ 75%) → self-cast through the ordinary unit form.
- **Game declares:** a GROUND-targeted group heal — `target_ground = true`, `target_ground_under_allies = true`, `target_self = false` (heals up to 3 friendly units in a 15 m area, 27 s, ×2 uses); the project's own record for it says "cast at own feet (existing ground-cast path)".
- **Why it makes no sense:** the db gives this ability no self target — the cast shape the game declares is the position form, not a unit target; the mod's `ground_keys` list omits this key, so what actually fires is the unit-target self-cast, which is not this ability's declared cast mode.
- **Feasibility:** the ground path already exists (`perform_special_ability_ground` at the caster's own position — tacticians_stand_your_ground rides it); adding this key is the concrete fix. The health-gated heal trigger itself is fine.

**Your ruling:** ______________________________________________________________________________


#### 350. Hellish Vigour Upgraded  (slice 07)

- **Key(s):** `wh3_dlc29_lord_abilities_hellish_vigour_upgraded`
- **Current logic:** Rides `melee_unwavering` - fires when the unit is in melee, not routing and not wavering; the cast passes the owner itself as the target (`perform_special_ability(key, owner)`).
- **Game declares:** The area version of the same augment: 35 m radius, all friendly units in range (`num_effected_friendly_units=-1`), caster still excluded (`affect_self=false`); valid target forms are a friendly UNIT or the GROUND (`target_friends=true`, `target_ground=true`, range 75 m).
- **Why it makes no sense:** Same mismatch as the base key: the self-cast matches neither declared target form and still cannot include the caster; the unit-target call passes the owner where the game expects a friendly unit or a ground point.
- **Feasibility:** Fixable without enemy reads: an ally pick, or the mod's existing own-position ground form (friends within 35 m of the caster would be covered; the caster correctly is not).

**Your ruling:** ______________________________________________________________________________


#### 456. Tacticians, Rally!  (slice 08)

- **Key(s):** `wh3_dlc24_character_abilities_tacticians_rally`
- **Current logic:** trigger `melee_unwavering`; casts on self through the normal unit-target call — the key is not in `FOURTH.ground_keys`.
- **Game declares:** a friend- and ground-targeted area Augment (`target_friends=true`, `target_ground=true`, 35 m aura affecting self+allies, cast range 100 m): +16 leadership for 14 s; 60 s recharge. Its targeting shape is identical to `wh3_dlc24_character_abilities_tacticians_stand_your_ground`, which the mod routes through the ground form (`perform_special_ability_ground`) via `FOURTH.ground_keys`. Tracker proposal: "cast on the wavering friendly unit."
- **Why it makes no sense:** the game declares ground targeting, and the mod's own convention (the `ground_keys` map, built for exactly this friend+ground shape) sends the identically-shaped SYG key through the ground form while this key fires the unit-target form on self — the two can't both be right; the declared friend/ground target is ignored either way.
- **Feasibility:** aligning it is a one-line addition to `FOURTH.ground_keys` (the ground-cast helper already ships), but the project's own comment says the ground path is API-documentation-backed rather than battle-proven — confirm in a live battle before trusting it.

**Your ruling:** ______________________________________________________________________________


---

## Class D — Heals or defensive effects gated behind melee (3 entries)

A heal, regeneration or defensive effect locked behind melee contact — it cannot fire before contact or while taking missile damage. The slice reasoning is 'a heal should not need melee'. The health-only evaluator already ships (`ushoran_health`, ≤75% health, no melee gate), so lifting the melee arm needs no new reads.

#### 118. Potion of Toughness  (slice 03)

- **Key(s):** `wh_main_item_abilities_potion_of_toughness`
- **Current logic:** trigger `melee_health75` — fires only when the unit is in melee AND its own health is at or below 75% (and not routing); cast on self via the default self-target call. The mod's own comment calls it "a ONE-TIME activation treated as a HEAL".
- **Game declares:** an active, self-targeted augment (`unit_abilities.type` = wh_type_augment; `unit_special_abilities` affect_self = true, all unit-target flags false, `ai_usage` = augment_melee_self) that for 21 s grants +30 armour, +24 melee defence and a small HP regeneration (heal_amount 0.0080); one use, 60 s recharge. Its game text: *"Those that consume a Potion of Toughness find their skin hardening as swords and arrows glance off their body…"* — i.e. protection that explicitly includes missile fire.
- **Why it makes no sense:** the mod treats the potion as a heal, yet gates it behind melee contact, so the defensive consumable can never fire before contact or while taking missile/artillery damage — exactly the "arrows" case its own text advertises ("a heal should not need melee"). The ≤75%-health arm alone already provides the "when hurt" condition; the extra melee requirement is not implied by the effect.
- **Feasibility:** both reads exist (is_in_melee and the proven HealthPercent read), and a health-only evaluator already ships (`ushoran_health` — the Ghoul King of Ushoran / Star of Avelorn "health ≤75%, no melee gate" pattern), so removing the melee arm needs no new reads or engine support. Note the tracker records the melee gate as a deliberate choice (armour/defence rationale), so this is flagged as a game-logic mismatch, not an engine limit.

**Your ruling:** ______________________________________________________________________________


#### 274. Armour of Caledor  (slice 05)

- **Key(s):** `wh2_dlc15_item_abilities_armour_of_caledor`
- **Current logic:** trigger `melee_unwavering` → self-cast.
- **Game declares:** a self regeneration — heals 1.6%/s for 20 s (≈32% max) with `cant_move = true`, ×3 uses (augment_spellcasting).
- **Why it makes no sense:** a heal should not need melee — the regeneration is gated behind being in melee, so it only ever fires after the unit is already engaged; a heal of this kind is usable before/during trouble regardless of engagement.
- **Feasibility:** implementable — self-cast target is fine; the `HealthPercent` read (already used by the ushoran_health family) would fit a regeneration item if a health gate is wanted.

**Your ruling:** ______________________________________________________________________________


#### 424. Reanimate Upgraded  (slice 08)

- **Key(s):** `wh2_dlc09_character_abilities_tomb_king_rally_upgraded`
- **Current logic:** trigger `melee_unwavering`; fires only while in melee and only while the unit is not wavering; self-cast (self-centred aura).
- **Game declares:** a self-centred area Augment (`area_of_augments`, range 35 m, affects self and allies) that for 10 s grants +16 leadership and replenishes hit points ("Replenishes hit points of combatants", `heal_amount=0.008`, `hp_change_frequency=1`); 90 s recharge. The tracker's proposal: "When morale falls to wavering: cast."
- **Why it makes no sense:** the hit-point replenish is a heal component gated behind melee contact (and suppressed while the unit is wavering), so it cannot respond when the unit or its friends are hurt outside melee — "a heal should not need melee". The project's own heal/replenish batch (36 entries) rides the ≤75%-health trigger with no melee gate; this row kept the melee gate.
- **Feasibility:** the health read and the `ushoran_health` evaluator already ship (`HealthPercent`, ≤75%, no melee gate), so no new reads are needed; the morale part could stay melee-gated if a split is preferred.

**Your ruling:** ______________________________________________________________________________


---

## Class E — Charge-component abilities on melee-only triggers (3 entries)

The effect pays out on the charge (charge bonus / charge speed components), but the trigger fires only once the unit is already in melee — after the charge is spent. Fixable with the mod's existing charge machinery (`measure_charge` / `charge_or_melee`); no new reads.

#### 272. Apocalyptic Charge  (slice 05)

- **Key(s):** `wh_pro04_unit_abilities_apocalyptic_charge`
- **Current logic:** trigger `melee_unwavering` → self-cast.
- **Game declares:** a charge effect — self-centred 35 m area with ×1.1 charge speed and ×1.2 charge bonus for 30 s (`ai_usage = aoe_centred_on_self`, `affect_self = true`). The cast target (self) is correct; the TRIGGER is the problem.
- **Why it makes no sense:** a charge effect should involve charging — the trigger only fires once the unit is already in melee, after the charge bonus has been spent; the charge window is deliberately excluded even though the mod carries charge detectors.
- **Feasibility:** implementable — ride `charge_or_melee` (or `charge_only`), which uses the existing `measure_charge` detector; no new reads needed.

**Your ruling:** ______________________________________________________________________________


#### 353. Horn of the Wild Hunt  (slice 07)

- **Key(s):** `wh_dlc05_item_abilities_horn_of_the_wild_hunt`
- **Current logic:** Rides `melee_unwavering` - fires when the unit is in melee, not routing and not wavering; the cast passes the owner itself as the target (`perform_special_ability(key, owner)`).
- **Game declares:** An army-wide +60% charge bonus to all friendly units for 24 s (`stat_charge_bonus` x1.6, radius -1 = unrestricted) - 'all Elven forces are driven to the Hunt'. A charge-window effect.
- **Why it makes no sense:** The trigger fires only once the unit is ALREADY in melee, i.e. after its own charge is spent - the one moment the wearer's charge bonus is definitionally wasted (other units' later charges could still benefit, but the item is a charge tool fired at the wrong phase). The tracker first set this key aside as 'charge-only' and its own rule maps charge effects to the charge-and-in-melee trigger the mod already runs for Fangspike/Onslaught.
- **Feasibility:** Cast-on-self is fine; the fix is trigger-side and uses proven machinery (the `measure_charge` detector / `charge_or_melee` trigger). Not enemy-limited.

**Your ruling:** ______________________________________________________________________________


#### 488. Twilight Horn I  (slice 09)

- **Key(s):** `wh2_dlc16_item_abilities_twilight_horn_i`
- **Current logic:** `melee_unwavering` — in melee (not wavering): cast on self (self is a legal target for this item).
- **Game declares:** an item augment on self or one friendly unit; 33 s: Charge Speed ×1.25, Speed ×1.25, Charge Bonus ×1.2 — a pure charge/movement effect.
- **Why it makes no sense:** trigger fit — the buff is spent on the next charge, but the trigger fires after contact, when the charge bonus can no longer apply; the project itself skipped the stronger twin (Twilight Horn II) as "unsuitable: movement" for exactly this reason.
- **Feasibility:** trigger-choice problem — the mod already ships a charge-window trigger for other charge-family abilities, so involving a charge needs no new reads.

**Your ruling:** ______________________________________________________________________________


---

## Class F — Engine-refused self casts (4 entries)

Self-targeted augments whose own engine gate (usage/target restriction such as `cannot_perform_missile_attack`) refuses the cast exactly in the in-melee state the trigger fires in. As written, every attempt fires where the game's own gate says no.

#### 291. Blooood!  (slice 06)

- **Key(s):** `wh_main_unit_abilities_blooood`
- **Current logic:** trigger `melee_unwavering` — fires when the Hellcannon is in melee (not routing/wavering), cast on itself.
- **Game declares:** a self augment (`wh_type_augment`, `affect_self=true`) — Speed +25%, Acceleration +18%, Vigour −2%/s for 18 s, 60 s recharge — with a hard usage gate: `cannot_perform_missile_attack` (the game's own wording: "Can use if: Missile attack possible"). Its text: *"The Hellcannon breaks its chains and rushes forwards."*
- **Why it makes no sense:** it is a rush-forward movement buff meant to be pressed while the Hellcannon can still fire, and the game refuses it the moment the unit cannot perform a missile attack — exactly the "in melee" state the mod fires it in. The trigger selects the one state where the cast is invalid and the speed effect has nothing left to close.
- **Feasibility:** not a read problem — the ability needs a moment *before* contact, so the in-melee trigger itself is wrong; as written every attempt is refused by the engine's own gate.

**Your ruling:** ______________________________________________________________________________


#### 295. Boom!  (slice 06)

- **Key(s):** `wh_main_unit_abilities_boom`
- **Current logic:** trigger `melee_unwavering` — fires when the Hellcannon is in melee, cast on itself.
- **Game declares:** a self augment for its own shots — +20% Armour-Piercing / +25% Base Explosive Damage for 15 s, 90 s recharge — gated by `cannot_perform_missile_attack` ("Enabled if: Missile attack possible").
- **Why it makes no sense:** the buff only means anything while the Hellcannon is shooting, and the game's own gate forbids it while the unit cannot perform a missile attack — which is precisely the in-melee state the trigger fires in. It cannot fire where it would matter, and would be pointless if it did.
- **Feasibility:** trigger problem, not a read problem — should fire before contact (while the guns still work); as written the in-melee cast is refused.

**Your ruling:** ______________________________________________________________________________


#### 307. Deranged Munitions  (slice 06)

- **Key(s):** `wh3_dlc25_lord_abilities_deranged_munitions`
- **Current logic:** trigger `melee_unwavering` — fires when the owner is in melee, cast on self.
- **Game declares:** a missile augment: +50% Armour-Piercing and +50% Base Missile Damage (+ Magical Attacks) for 30 s, with the game's own target restriction `cannot_perform_missile_attack` (targets that cannot perform a missile attack are invalid).
- **Why it makes no sense:** the trigger fires exactly while the owner cannot perform a missile attack (locked in melee), the state the game's target gate rejects; and even where it were legal, a missile-damage buff does nothing for a unit that cannot fire.
- **Feasibility:** needs a different condition/target (e.g. a friendly-unit picker outside the melee lock) — no new reads required for a friendly picker, but the in-melee self-cast is the one combination the game's data rejects.

**Your ruling:** ______________________________________________________________________________


#### 308. Deranged Munitions Upgraded  (slice 06)

- **Key(s):** `wh3_dlc25_lord_abilities_deranged_munitions_upgraded`
- **Current logic:** trigger `melee_unwavering` — fires when the owner is in melee, cast on self.
- **Game declares:** the area version of the same missile augment (+50% missile damage, 35 m ally aura, 30 s) with the same `cannot_perform_missile_attack` target restriction.
- **Why it makes no sense:** same contradiction as the base key — the in-melee state is exactly when the owner (and any melee-locked ally) is an invalid target for a missile-damage buff.
- **Feasibility:** same as the base key — a different trigger/target is needed; the in-melee self-cast cannot work as declared.

**Your ruling:** ______________________________________________________________________________


---

## Class G — Trigger fires in the wrong state (6 entries)

The cast target is right; the moment is wrong — a toggle, a dash, a last-stand drink or a global field fired on 'in melee, not wavering'. Some also need toggle-aware handling the per-condition batch machinery does not have (fire once to enable, not re-check every guard cycle).

#### 378. Master Predator  (slice 07)

- **Key(s):** `wh2_dlc17_lord_abilities_master_predator`
- **Current logic:** Rides `melee_unwavering` - fires when the unit is in melee, not routing and not wavering; the cast passes the owner itself as the target (`perform_special_ability(key, owner)`).
- **Game declares:** A TOGGLE-able self stance (1 s recharge, duration until toggled off): +20% missile range, Snipe and Unspottable, -25% speed and charge speed - a stealth/sniper mode Oxyotl switches on to stalk from range.
- **Why it makes no sense:** Firing it when the unit is in melee is backwards: stealth, sniping and extra range do nothing once the unit is spotted and engaged, and the -25% speed hurts exactly when disengaging; worse, it is a toggle - a condition that simply re-checks 'in melee' on every guard cycle can flip the stance on/off repeatedly instead of enabling it once.
- **Feasibility:** No enemy read involved, but the ability needs toggle-aware handling (fire once to enable; never re-fire per guard cycle as a condition) that the current per-condition batch machinery does not have - not operable as-is.

**Your ruling:** ______________________________________________________________________________


#### 392. Moonshine  (slice 07)

- **Key(s):** `wh2_dlc11_item_abilities_moonshine`
- **Current logic:** Rides `melee_unwavering` - fires when the unit is in melee, not routing and not wavering; the cast passes the owner itself as the target (`perform_special_ability(key, owner)`).
- **Game declares:** A single-use courage draught granting Unbreakable (plus +25% melee damage and a small heal; -40% flame resistance as the cost), self-targeted, 15 s.
- **Why it makes no sense:** It is a last-stand item: the mod's standing rule maps the Unbreakable family to the wavering-self trigger and the mod's own items of this family (Helm of Yvresse, Vial of Troll Blood) fire on wavering - yet this rides `melee_unwavering`, which REQUIRES the unit not to be wavering, so the potion can never fire in the very state it is drunk for (about to break).
- **Feasibility:** Trigger-side fix only: the wavering read (`is_wavering`) and the wavering evaluators already exist; cast-on-self is correct. Not enemy-limited.

**Your ruling:** ______________________________________________________________________________


#### 398. Null Stone  (slice 07)

- **Key(s):** `wh3_dlc27_item_abilities_null_stone`
- **Current logic:** Rides `melee_unwavering` - fires when the unit is in melee, not routing and not wavering; the cast passes the owner itself as the target (`perform_special_ability(key, owner)`).
- **Game declares:** A self-activation field with NO target flags (not an aimed hex): 35 s of `silenced` + remove-magical over an unrestricted radius, applied to FRIENDS AND ENEMIES alike (num_effected_friendly_units = -1, num_effected_enemy_units = -1) - a global magic shutdown that also hits the bearer's own wizards.
- **Why it makes no sense:** The field has no connection to melee contact - it neither needs nor uses an engaged enemy - so the in-melee trigger is an arbitrary moment that silences the caster's own side for 35 s as a side effect; the tracker's own class for this key is the enemy-in-sight trigger, which is exactly what the mod cannot read.
- **Feasibility:** The enemy-in-sight condition is impossible (no enemy unit read exists); of the honest options, a readiness/no-condition activation would at least match the effect's untargeted, global nature. Not implementable as the tracker intended.

**Your ruling:** ______________________________________________________________________________


#### 482. Thunderburner  (slice 09)

- **Key(s):** `wh3_dlc25_unit_abilities_thunderburner`
- **Current logic:** `melee_unwavering` — in melee (not wavering): cast on self.
- **Game declares:** a self toggle for the flying Thunderbarge (cd 30 s): Speed ×2.5, Turn Speed ×0.3, with continuous self-damage (30 damage per hp tick) — a straight-line steam dash whose game text says it "soars forward at speed" and whose AI family is `hex_speed_under_fire` (a reaction to being under fire, not melee).
- **Why it makes no sense:** trigger fit — the ability's whole value is a long, pre-aimed dash across the field; firing it once the ship is already locked in melee spends the dash in the one state where its direction cannot be planned, while the self-damage cost still starts ticking.
- **Feasibility:** trigger-choice problem, not an engine limit — a different trigger moment (e.g. a movement/under-fire arm) uses reads the mod already has; no enemy targeting is involved.

**Your ruling:** ______________________________________________________________________________


#### 483. Thunderburner Upgraded  (slice 09)

- **Key(s):** `wh3_dlc25_unit_abilities_thunderburner_upgraded`
- **Current logic:** `melee_unwavering` — in melee (not wavering): cast on self.
- **Game declares:** same self toggle as 482, stronger: Speed ×3, Turn Speed ×0.3, continuous self-damage (10 per tick), `hex_speed_under_fire`.
- **Why it makes no sense:** trigger fit — same mismatch as Thunderburner: a planned dash fired from a melee scrum, where the movement cannot be directed and the damage cost applies anyway.
- **Feasibility:** trigger-choice problem, not an engine limit.

**Your ruling:** ______________________________________________________________________________


#### 519. Woven Mist  (slice 09)

- **Key(s):** `wh_dlc05_unit_abilities_woven_mist`
- **Current logic:** `melee_unwavering` — in melee (not wavering): cast on self.
- **Game declares:** a self toggle (permanent until disabled, 1 s recharge): −24 Melee Defence, +40 Missile Resistance — an anti-missile dance that pays for the protection with melee defence.
- **Why it makes no sense:** trigger fit — the toggle is fired exactly when the unit is in melee, i.e. when the melee-defence penalty bites and the missile protection is only partially relevant; the ability is built to be raised under missile fire, not in a melee.
- **Feasibility:** trigger-choice problem, not an engine limit — the mismatch is when it fires, not what it can read; the cast target (self) is correct.

**Your ruling:** ______________________________________________________________________________


---

## Class H — Effect does not fit the heal-family trigger (2 entries)

These ride the health-gated heal batch but do not fit it: one has no heal at all (a one-use spell-power item), the other deliberately damages the friendly unit it is aimed at — the direction is inverted, and 'which ally is expendable' is not a decidable read.

#### 556. Scroll of Power  (slice 10)

- **Key(s):** `wh_main_item_abilities_scroll_of_power`
- **Current logic:** trigger `ushoran_health` — fires when the unit's own health ≤75% and casts on itself (single use).
- **Game declares:** a one-use item effect ("runes to boost the power of a single spell"): 57 s positive phase with `ability_recharge_change = −60` and NO heal amount anywhere — it is an ability-recharge/spell-power boost, not a heal.
- **Why it makes no sense:** the entry rides the health-gated heal family, but the effect has nothing to do with the unit's health; the trigger cannot fit the effect, and firing it at ≤75% health wastes its one use at an arbitrary moment.
- **Feasibility:** no readable condition in the mod matches the ability's purpose (no magic-power or per-ability cooldown reads exist; only the engine's own readiness gate), so it should not ride this trigger at all.

**Your ruling:** ______________________________________________________________________________


#### 575. Eat da Runts!  (slice 10)

- **Key(s):** `wh3_dlc26_unit_abilities_eat_da_runts`
- **Current logic:** bespoke `eat_da_runts` trigger — self ≤75% health → cast on SELF; otherwise the lowest-health in-range ally ≤75% → cast on that ALLY (both arms are described in-file as "ally-targeting HEALS").
- **Game declares:** the target is a friendly unit that gets EATEN — the ally phase deals `damage_amount = 144` ("Causes damage to allies" UiEffect bullet; the initiative text: feed gobbo-fodder to the hungry big'un), while the CASTER heals (1.5%/s self phase). `target_friends = true` with no self target — the ally is the meal, not the patient.
- **Why it makes no sense:** the mod inverts the effect — the "heal the ally" arm spends the cast to damage the ally it was trying to save (the lowest-health one, where 144 damage likely kills models), and the self arm targets a unit (the caster) the ability cannot take as a target.
- **Feasibility:** the ability deliberately damages a friendly unit; "which ally is expendable" is not a decidable read and the current direction is backwards — do not keep this as an ally-heal.

**Your ruling:** ______________________________________________________________________________


---

## The 418 clean entries

The other **418** of the 579 entries passed all checks — a confident yes on cast target, trigger fit and trigger achievability — and are not listed in this report. They remain listed per slice in the slice files (`WH3_audit\slice_01.md` … `slice_10.md`, each `## CLEAN` section): 58 + 58 + 57 + 38 + 43 + 32 + 22 + 37 + 26 + 47 = 418. Combined with the 161 flagged above, the audit covers all 579 entries.
