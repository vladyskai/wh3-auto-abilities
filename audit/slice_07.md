# WH3 ability-logic audit — slice 07 of 10 (ABILITIES entries 349–406, source order)

All 58 entries of this slice ride the same trigger (`melee_unwavering`: the unit is alive, in melee, not routing and not wavering — fail-open morale) and, except where a bespoke target is noted, cast via `perform_special_ability(key, owner)`, i.e. on the owner itself. Judged against the game's own ability data (`unit_spec_abil` / `phases` / `phase_junc` / UI-effect tables dumps) and the established engine reads (friendly units only; no enemy card/id/health read; no per-unit firing or cooldown read).

**Counts: 58 audited · 36 flagged · 22 clean.**

## FLAGGED

### Hellish Vigour — `hellish_vigour` (#349)
- **Key(s):** `wh3_dlc29_lord_abilities_hellish_vigour`
- **Current logic:** Rides `melee_unwavering` - fires when the unit is in melee, not routing and not wavering; the cast passes the owner itself as the target (`perform_special_ability(key, owner)`).
- **Game declares:** A single FRIENDLY-unit augment (`target_friends=true`, `num_effected_friendly_units=1`, cast range 75 m): +20 damage reflection and reduced fatigue for 25 s. The caster is NOT among the affected: `affect_self=false`, `target_self=false`, and the phase targets friends only.
- **Why it makes no sense:** Casting it on the owner applies the augment to nobody - the caster is excluded from its own effect. It is a targeted hand-out to another friendly unit ('drives his host onward'), and a self-cast cannot deliver it.
- **Feasibility:** Fixable without enemy reads: friendly units are readable and the mod already ships ally-targeted casts (Glorious Death / Blood Sacrifice pattern); the tracker itself notes 'nearest-ally picker later'. Needs an ally picker, not enemy reads.

### Hellish Vigour Upgraded — `hellish_vigour_upgraded` (#350)
- **Key(s):** `wh3_dlc29_lord_abilities_hellish_vigour_upgraded`
- **Current logic:** Rides `melee_unwavering` - fires when the unit is in melee, not routing and not wavering; the cast passes the owner itself as the target (`perform_special_ability(key, owner)`).
- **Game declares:** The area version of the same augment: 35 m radius, all friendly units in range (`num_effected_friendly_units=-1`), caster still excluded (`affect_self=false`); valid target forms are a friendly UNIT or the GROUND (`target_friends=true`, `target_ground=true`, range 75 m).
- **Why it makes no sense:** Same mismatch as the base key: the self-cast matches neither declared target form and still cannot include the caster; the unit-target call passes the owner where the game expects a friendly unit or a ground point.
- **Feasibility:** Fixable without enemy reads: an ally pick, or the mod's existing own-position ground form (friends within 35 m of the caster would be covered; the caster correctly is not).

### Hidden Huntress — `hidden_huntress` (#351)
- **Key(s):** `wh3_cp1_lord_abilities_hidden_huntress`
- **Current logic:** Rides `melee_unwavering` - fires when the unit is in melee, not routing and not wavering; the cast passes the owner itself as the target (`perform_special_ability(key, owner)`).
- **Game declares:** A single-ENEMY armour hex (`target_enemies=true`, `num_effected_enemy_units=1`, range 75 m): -25% speed, -24 Melee Defence for 20 s.
- **Why it makes no sense:** The effect applies only to the chosen ENEMY (and the game requires that choice - single/limited targets, some restricted to commander or missile units). The mod's cast passes the owner as the target, so nothing lands on any enemy; with no enemy-unit read (no card, id or health) the cast can neither be aimed nor gated.
- **Feasibility:** Not implementable as-is: the engine exposes no enemy unit read and enemy-targeted casts cannot be aimed by the mod - firing it blindly on self cannot deliver an enemy-targeted effect.

### Hidden Huntress Upgraded — `hidden_huntress_upgraded` (#352)
- **Key(s):** `wh3_cp1_lord_abilities_hidden_huntress_upgraded`
- **Current logic:** Rides `melee_unwavering` - fires when the unit is in melee, not routing and not wavering; the cast passes the owner itself as the target (`perform_special_ability(key, owner)`).
- **Game declares:** A single-ENEMY hex, upgraded: -25% speed, -30 armour, -40 Melee Defence for 20 s, range 75 m.
- **Why it makes no sense:** The effect applies only to the chosen ENEMY (and the game requires that choice - single/limited targets, some restricted to commander or missile units). The mod's cast passes the owner as the target, so nothing lands on any enemy; with no enemy-unit read (no card, id or health) the cast can neither be aimed nor gated.
- **Feasibility:** Not implementable as-is: the engine exposes no enemy unit read and enemy-targeted casts cannot be aimed by the mod - firing it blindly on self cannot deliver an enemy-targeted effect.

### Horn of the Wild Hunt — `horn_of_the_wild_hunt` (#353)
- **Key(s):** `wh_dlc05_item_abilities_horn_of_the_wild_hunt`
- **Current logic:** Rides `melee_unwavering` - fires when the unit is in melee, not routing and not wavering; the cast passes the owner itself as the target (`perform_special_ability(key, owner)`).
- **Game declares:** An army-wide +60% charge bonus to all friendly units for 24 s (`stat_charge_bonus` x1.6, radius -1 = unrestricted) - 'all Elven forces are driven to the Hunt'. A charge-window effect.
- **Why it makes no sense:** The trigger fires only once the unit is ALREADY in melee, i.e. after its own charge is spent - the one moment the wearer's charge bonus is definitionally wasted (other units' later charges could still benefit, but the item is a charge tool fired at the wrong phase). The tracker first set this key aside as 'charge-only' and its own rule maps charge effects to the charge-and-in-melee trigger the mod already runs for Fangspike/Onslaught.
- **Feasibility:** Cast-on-self is fine; the fix is trigger-side and uses proven machinery (the `measure_charge` detector / `charge_or_melee` trigger). Not enemy-limited.

### Hornswaggle — `hornswaggle` (#355)
- **Key(s):** `wh2_dlc11_character_abilities_hornswaggle`
- **Current logic:** Rides `melee_unwavering` - fires when the unit is in melee, not routing and not wavering; the cast passes the owner itself as the target (`perform_special_ability(key, owner)`).
- **Game declares:** A single-ENEMY hex: -25% speed, -30 armour, -24 Melee Defence for 32 s, range 100 m.
- **Why it makes no sense:** The effect applies only to the chosen ENEMY (and the game requires that choice - single/limited targets, some restricted to commander or missile units). The mod's cast passes the owner as the target, so nothing lands on any enemy; with no enemy-unit read (no card, id or health) the cast can neither be aimed nor gated.
- **Feasibility:** Not implementable as-is: the engine exposes no enemy unit read and enemy-targeted casts cannot be aimed by the mod - firing it blindly on self cannot deliver an enemy-targeted effect.

### Hunter of Champions — `hunter_of_champions` (#357)
- **Key(s):** `wh_dlc08_character_abilities_hunter_of_champions`
- **Current logic:** Rides `melee_unwavering` - fires when the unit is in melee, not routing and not wavering; the cast passes the owner itself as the target (`perform_special_ability(key, owner)`).
- **Game declares:** A single-ENEMY hex that the game only allows on a commander-class target (invalid-target flag `unit_is_not_commander_class`): -45% speed, -60 armour, -40 Melee Defence for 24 s, range 100 m.
- **Why it makes no sense:** The effect applies only to the chosen ENEMY (and the game requires that choice - single/limited targets, some restricted to commander or missile units). The mod's cast passes the owner as the target, so nothing lands on any enemy; with no enemy-unit read (no card, id or health) the cast can neither be aimed nor gated.
- **Feasibility:** Not implementable as-is: the engine exposes no enemy unit read and enemy-targeted casts cannot be aimed by the mod - firing it blindly on self cannot deliver an enemy-targeted effect.

### Hunter's Snare — `hunters_snare` (#358)
- **Key(s):** `wh2_dlc13_lord_abilities_hunters_snare`
- **Current logic:** Rides `melee_unwavering` - fires when the unit is in melee, not routing and not wavering; the cast passes the owner itself as the target (`perform_special_ability(key, owner)`).
- **Game declares:** An ENEMY- or GROUND-targeted 35 m net (cant_move) for 11 s, placed up to 100 m away, 3 uses (`target_enemies=true`, `target_ground=true`).
- **Why it makes no sense:** The effect applies only to the chosen ENEMY (and the game requires that choice - single/limited targets, some restricted to commander or missile units). The mod's cast passes the owner as the target, so nothing lands on any enemy; with no enemy-unit read (no card, id or health) the cast can neither be aimed nor gated.
- **Feasibility:** Not implementable as-is: the engine exposes no enemy unit read and enemy-targeted casts cannot be aimed by the mod - firing it blindly on self cannot deliver an enemy-targeted effect.

### Hunter's Trap — `hunters_trap` (#359)
- **Key(s):** `wh2_dlc13_lord_abilities_hunters_trap`
- **Current logic:** Rides `melee_unwavering` - fires when the unit is in melee, not routing and not wavering; the cast passes the owner itself as the target (`perform_special_ability(key, owner)`).
- **Game declares:** An ENEMY- or GROUND-targeted 35 m net (cant_move) for 22 s, placed up to 100 m away, 3 uses.
- **Why it makes no sense:** The effect applies only to the chosen ENEMY (and the game requires that choice - single/limited targets, some restricted to commander or missile units). The mod's cast passes the owner as the target, so nothing lands on any enemy; with no enemy-unit read (no card, id or health) the cast can neither be aimed nor gated.
- **Feasibility:** Not implementable as-is: the engine exposes no enemy unit read and enemy-targeted casts cannot be aimed by the mod - firing it blindly on self cannot deliver an enemy-targeted effect.

### Inspired Marksmanship I — `inspired_marksmanship_i` (#361)
- **Key(s):** `wh3_main_lord_abilities_inspired_marksmanship_i`
- **Current logic:** Rides `melee_unwavering` - fires when the unit is in melee, not routing and not wavering; the cast passes the owner itself as the target (`perform_special_ability(key, owner)`).
- **Game declares:** A single-friendly augment that may only be placed on a unit that can perform missile attacks (invalid-target flag `cannot_perform_missile_attack`): +30 accuracy, +20 reloading for 29 s, range 100 m; the caster is not affected (`affect_self=false`).
- **Why it makes no sense:** The self-cast can receive nothing (ally-only, caster unaffected), and firing a shooting buff while the owner is stuck in melee is mistimed on both counts - the effect wants an ally that is actually shooting.
- **Feasibility:** Feasible in principle with the friendly reads the mod already has (plus a static missile-capability gate, which the mod's own API notes record as available); no enemy reads needed. The ally picker does not exist yet.

### Inspired Marksmanship II — `inspired_marksmanship_ii` (#362)
- **Key(s):** `wh3_main_lord_abilities_inspired_marksmanship_ii`
- **Current logic:** Rides `melee_unwavering` - fires when the unit is in melee, not routing and not wavering; the cast passes the owner itself as the target (`perform_special_ability(key, owner)`).
- **Game declares:** Same as I but +60 accuracy, +20 reloading for 44 s, range 100 m; same `cannot_perform_missile_attack` invalid-target flag.
- **Why it makes no sense:** Same mismatch: single-ally missile buff cast on the owner, who is not affected and is in melee when the trigger fires.
- **Feasibility:** Same as I: ally picker feasible (friendly reads exist); not enemy-limited.

### Inspired Marksmanship III — `inspired_marksmanship_iii` (#363)
- **Key(s):** `wh3_main_lord_abilities_inspired_marksmanship_iii`
- **Current logic:** Rides `melee_unwavering` - fires when the unit is in melee, not routing and not wavering; the cast passes the owner itself as the target (`perform_special_ability(key, owner)`).
- **Game declares:** Same as II with +40 reloading, 44 s, range 100 m; same `cannot_perform_missile_attack` invalid-target flag.
- **Why it makes no sense:** Same mismatch as I/II.
- **Feasibility:** Same as I/II: ally picker feasible; not enemy-limited.

### Iron-Handed Captain — `iron_hand_captain` (#364)
- **Key(s):** `wh3_dlc27_character_abilities_iron_hand_captain`
- **Current logic:** Rides `melee_unwavering` - fires when the unit is in melee, not routing and not wavering; the cast passes the owner itself as the target (`perform_special_ability(key, owner)`).
- **Game declares:** A rally for a broken ally: single friendly target (`only_affect_target=true`, range 200 m) that the game only allows on a unit whose morale is at or below 'broken' (invalid-target flag `morale_is_higher_than_broken`); grants +100 morale and the `force_rally` attribute for 42 s. Caster not affected (`affect_self=false`, phase friends-only).
- **Why it makes no sense:** Target and premise are both inverted: the mod fires it when the CASTER is in melee and specifically NOT wavering, and casts it on the caster - who is neither a valid target (`target_self=false`) nor broken. The ally it exists to rally is never involved.
- **Feasibility:** A fleeing-ally pick is conceivable in principle (friendly routing state is readable - `unit_is_routing` is already used on allies); the current self-cast cannot work. Not enemy-limited.

### Looming Dread — `looming_dread` (#369)
- **Key(s):** `wh2_dlc14_lord_abilities_looming_dread`
- **Current logic:** Rides `melee_unwavering` - fires when the unit is in melee, not routing and not wavering; the cast passes the owner itself as the target (`perform_special_ability(key, owner)`).
- **Game declares:** A single-ENEMY hex restricted to commander-class targets (invalid-target flag `unit_is_not_commander_class`): -45% speed, -24 Melee Defence, -20 missile resistance for 31 s, range 150 m.
- **Why it makes no sense:** The effect applies only to the chosen ENEMY (and the game requires that choice - single/limited targets, some restricted to commander or missile units). The mod's cast passes the owner as the target, so nothing lands on any enemy; with no enemy-unit read (no card, id or health) the cast can neither be aimed nor gated.
- **Feasibility:** Not implementable as-is: the engine exposes no enemy unit read and enemy-targeted casts cannot be aimed by the mod - firing it blindly on self cannot deliver an enemy-targeted effect.

### Lord of Dragons — `lord_of_dragons` (#370)
- **Key(s):** `wh2_dlc15_lord_abilities_lord_of_dragons`
- **Current logic:** Rides `melee_unwavering` - fires when the unit is in melee, not routing and not wavering; the cast passes the owner itself as the target (`perform_special_ability(key, owner)`).
- **Game declares:** A single-ENEMY hex: -40 Melee Attack, -24 Melee Defence for 22 s, range 75 m.
- **Why it makes no sense:** The effect applies only to the chosen ENEMY (and the game requires that choice - single/limited targets, some restricted to commander or missile units). The mod's cast passes the owner as the target, so nothing lands on any enemy; with no enemy-unit read (no card, id or health) the cast can neither be aimed nor gated.
- **Feasibility:** Not implementable as-is: the engine exposes no enemy unit read and enemy-targeted casts cannot be aimed by the mod - firing it blindly on self cannot deliver an enemy-targeted effect.

### Mark of the Plague Fleet — `mark_of_the_plague_fleet` (#372)
- **Key(s):** `wh3_dlc29_item_active_mark_of_the_plague_fleet`
- **Current logic:** Rides `melee_unwavering` - fires when the unit is in melee, not routing and not wavering; the cast passes the owner itself as the target (`perform_special_ability(key, owner)`).
- **Game declares:** An ENEMY hex affecting up to three units (spreads to enemies): -50% healing power, -20 all/magic/physical resistances for 30 s, range 75 m.
- **Why it makes no sense:** The effect applies only to the chosen ENEMY (and the game requires that choice - single/limited targets, some restricted to commander or missile units). The mod's cast passes the owner as the target, so nothing lands on any enemy; with no enemy-unit read (no card, id or health) the cast can neither be aimed nor gated.
- **Feasibility:** Not implementable as-is: the engine exposes no enemy unit read and enemy-targeted casts cannot be aimed by the mod - firing it blindly on self cannot deliver an enemy-targeted effect.

### Mark of Yin — `mark_of_yin` (#373)
- **Key(s):** `wh3_dlc24_unit_abilities_mark_of_yin`
- **Current logic:** Rides `melee_unwavering` - fires when the unit is in melee, not routing and not wavering; the cast passes the owner itself as the target (`perform_special_ability(key, owner)`).
- **Game declares:** A single-ENEMY hex: -30 armour, -25 missile block chance, -20 missile resistance for 28 s, range 180 m.
- **Why it makes no sense:** The effect applies only to the chosen ENEMY (and the game requires that choice - single/limited targets, some restricted to commander or missile units). The mod's cast passes the owner as the target, so nothing lands on any enemy; with no enemy-unit read (no card, id or health) the cast can neither be aimed nor gated.
- **Feasibility:** Not implementable as-is: the engine exposes no enemy unit read and enemy-targeted casts cannot be aimed by the mod - firing it blindly on self cannot deliver an enemy-targeted effect.

### Marked by Ulthar — `marked_by_ulthar` (#374)
- **Key(s):** `wh_dlc06_unit_abilities_marked_by_ulthar`
- **Current logic:** Rides `melee_unwavering` - fires when the unit is in melee, not routing and not wavering; the cast passes the owner itself as the target (`perform_special_ability(key, owner)`).
- **Game declares:** A single-ENEMY hex: -30 armour, -25 missile block chance, -20 missile resistance for 28 s, range 150 m.
- **Why it makes no sense:** The effect applies only to the chosen ENEMY (and the game requires that choice - single/limited targets, some restricted to commander or missile units). The mod's cast passes the owner as the target, so nothing lands on any enemy; with no enemy-unit read (no card, id or health) the cast can neither be aimed nor gated.
- **Feasibility:** Not implementable as-is: the engine exposes no enemy unit read and enemy-targeted casts cannot be aimed by the mod - firing it blindly on self cannot deliver an enemy-targeted effect.

### Marked for Eatin' — `marked_for_eatin` (#375)
- **Key(s):** `wh3_dlc26_unit_abilities_marked_for_eatin`
- **Current logic:** Rides `melee_unwavering` - fires when the unit is in melee, not routing and not wavering; the cast passes the owner itself as the target (`perform_special_ability(key, owner)`).
- **Game declares:** A single-ENEMY hex: -25% speed, -30 armour, -40 Melee Defence for 29 s, range 75 m.
- **Why it makes no sense:** The effect applies only to the chosen ENEMY (and the game requires that choice - single/limited targets, some restricted to commander or missile units). The mod's cast passes the owner as the target, so nothing lands on any enemy; with no enemy-unit read (no card, id or health) the cast can neither be aimed nor gated.
- **Feasibility:** Not implementable as-is: the engine exposes no enemy unit read and enemy-targeted casts cannot be aimed by the mod - firing it blindly on self cannot deliver an enemy-targeted effect.

### Master of Beguilement — `beguile` (#376)
- **Key(s):** `wh_dlc04_lord_abilities_beguile`
- **Current logic:** Rides `melee_unwavering` - fires when the unit is in melee, not routing and not wavering; the cast passes the owner itself as the target (`perform_special_ability(key, owner)`).
- **Game declares:** A single-ENEMY hex: -40 Melee Attack for 44 s, range 100 m.
- **Why it makes no sense:** The effect applies only to the chosen ENEMY (and the game requires that choice - single/limited targets, some restricted to commander or missile units). The mod's cast passes the owner as the target, so nothing lands on any enemy; with no enemy-unit read (no card, id or health) the cast can neither be aimed nor gated.
- **Feasibility:** Not implementable as-is: the engine exposes no enemy unit read and enemy-targeted casts cannot be aimed by the mod - firing it blindly on self cannot deliver an enemy-targeted effect.

### Master Predator — `master_predator` (#378)
- **Key(s):** `wh2_dlc17_lord_abilities_master_predator`
- **Current logic:** Rides `melee_unwavering` - fires when the unit is in melee, not routing and not wavering; the cast passes the owner itself as the target (`perform_special_ability(key, owner)`).
- **Game declares:** A TOGGLE-able self stance (1 s recharge, duration until toggled off): +20% missile range, Snipe and Unspottable, -25% speed and charge speed - a stealth/sniper mode Oxyotl switches on to stalk from range.
- **Why it makes no sense:** Firing it when the unit is in melee is backwards: stealth, sniping and extra range do nothing once the unit is spotted and engaged, and the -25% speed hurts exactly when disengaging; worse, it is a toggle - a condition that simply re-checks 'in melee' on every guard cycle can flip the stance on/off repeatedly instead of enabling it once.
- **Feasibility:** No enemy read involved, but the ability needs toggle-aware handling (fire once to enable; never re-fire per guard cycle as a condition) that the current per-condition batch machinery does not have - not operable as-is.

### Master Rune of Slowness — `master_rune_of_slowness` (#381)
- **Key(s):** `wh2_dlc17_rune_abilities_master_rune_of_slowness`
- **Current logic:** Rides `melee_unwavering` - fires when the unit is in melee, not routing and not wavering; the cast passes the owner itself as the target (`perform_special_ability(key, owner)`).
- **Game declares:** A single-ENEMY rune hex: -60% speed and charge speed, -40% charge bonus for 45 s, range 100 m.
- **Why it makes no sense:** The effect applies only to the chosen ENEMY (and the game requires that choice - single/limited targets, some restricted to commander or missile units). The mod's cast passes the owner as the target, so nothing lands on any enemy; with no enemy-unit read (no card, id or health) the cast can neither be aimed nor gated.
- **Feasibility:** Not implementable as-is: the engine exposes no enemy unit read and enemy-targeted casts cannot be aimed by the mod - firing it blindly on self cannot deliver an enemy-targeted effect.

### Merciw's Monstrous Regiment — `merciws_monstrous_regiment` (#383)
- **Key(s):** `wh3_dlc20_cataclysm_bound_merciws_monstrous_regiment` + `wh3_dlc27_cataclysm_bound_merciws_monstrous_regiment`
- **Current logic:** Rides `melee_unwavering` - fires when the unit is in melee, not routing and not wavering; the cast passes the owner itself as the target (`perform_special_ability(key, owner)`).
- **Game declares:** A single chosen ALLY receives +40 Melee Attack, +50% melee damage and +20 physical resistance for 120 s (`target_friends=true`, `num_effected_friendly_units=1`, `affect_self=false`; both bound keys - `wh3_dlc20_...` and `wh3_dlc27_...` - share the same phase). Caster not affected.
- **Why it makes no sense:** Ally-only single-target buff cast on the owner: the caster gains nothing from its own cast, and no ally is selected. ('Bestows it upon his chosen allies' - the chosen ally is the whole point.)
- **Feasibility:** Ally picker feasible with the friendly reads already in use (Glorious Death / Blood Sacrifice pattern); no enemy reads needed.

### Missile Mirror — `unit_bound_missile_mirror` (#390)
- **Key(s):** `wh3_dlc24_unit_bound_missile_mirror`
- **Current logic:** Rides `melee_unwavering` - fires when the unit is in melee, not routing and not wavering; the cast passes the owner itself as the target (`perform_special_ability(key, owner)`).
- **Game declares:** A single-ENEMY bound spell that must target an enemy missile unit (invalid-target flag `is_not_missile_unit`) to redirect its projectiles for 18 s, range 200 m.
- **Why it makes no sense:** The effect applies only to the chosen ENEMY (and the game requires that choice - single/limited targets, some restricted to commander or missile units). The mod's cast passes the owner as the target, so nothing lands on any enemy; with no enemy-unit read (no card, id or health) the cast can neither be aimed nor gated.
- **Feasibility:** Not implementable as-is: the engine exposes no enemy unit read and enemy-targeted casts cannot be aimed by the mod - firing it blindly on self cannot deliver an enemy-targeted effect.

### Mither — `mither` (#391)
- **Key(s):** `wh2_dlc15_hero_abilities_mither`
- **Current logic:** Rides `melee_unwavering` - fires when the unit is in melee, not routing and not wavering; the cast passes the owner itself as the target (`perform_special_ability(key, owner)`).
- **Game declares:** A single-ENEMY morale/speed hex: -60% speed and charge speed for 15 s, range 75 m.
- **Why it makes no sense:** The effect applies only to the chosen ENEMY (and the game requires that choice - single/limited targets, some restricted to commander or missile units). The mod's cast passes the owner as the target, so nothing lands on any enemy; with no enemy-unit read (no card, id or health) the cast can neither be aimed nor gated.
- **Feasibility:** Not implementable as-is: the engine exposes no enemy unit read and enemy-targeted casts cannot be aimed by the mod - firing it blindly on self cannot deliver an enemy-targeted effect.

### Moonshine — `moonshine` (#392)
- **Key(s):** `wh2_dlc11_item_abilities_moonshine`
- **Current logic:** Rides `melee_unwavering` - fires when the unit is in melee, not routing and not wavering; the cast passes the owner itself as the target (`perform_special_ability(key, owner)`).
- **Game declares:** A single-use courage draught granting Unbreakable (plus +25% melee damage and a small heal; -40% flame resistance as the cost), self-targeted, 15 s.
- **Why it makes no sense:** It is a last-stand item: the mod's standing rule maps the Unbreakable family to the wavering-self trigger and the mod's own items of this family (Helm of Yvresse, Vial of Troll Blood) fire on wavering - yet this rides `melee_unwavering`, which REQUIRES the unit not to be wavering, so the potion can never fire in the very state it is drunk for (about to break).
- **Feasibility:** Trigger-side fix only: the wavering read (`is_wavering`) and the wavering evaluators already exist; cast-on-self is correct. Not enemy-limited.

### Muster of Malevolents — `muster_of_malevolents` (#394)
- **Key(s):** `wh2_dlc16_character_abilities_muster_of_malevolents`
- **Current logic:** Rides `melee_unwavering` - fires when the unit is in melee, not routing and not wavering; the cast passes the owner itself as the target (`perform_special_ability(key, owner)`).
- **Game declares:** A single-ENEMY direct-damage effect: 144 damage over 15 s (max 1 entity damaged), range 75 m.
- **Why it makes no sense:** The effect applies only to the chosen ENEMY (and the game requires that choice - single/limited targets, some restricted to commander or missile units). The mod's cast passes the owner as the target, so nothing lands on any enemy; with no enemy-unit read (no card, id or health) the cast can neither be aimed nor gated.
- **Feasibility:** Not implementable as-is: the engine exposes no enemy unit read and enemy-targeted casts cannot be aimed by the mod - firing it blindly on self cannot deliver an enemy-targeted effect.

### Net Dem Up! — `net_dem_up` (#396)
- **Key(s):** `wh3_dlc26_unit_abilities_net_dem_up`
- **Current logic:** Rides `melee_unwavering` - fires when the unit is in melee, not routing and not wavering; the cast passes the owner itself as the target (`perform_special_ability(key, owner)`).
- **Game declares:** A single-ENEMY net (cant_move, -50 missile block chance) for 18 s, range 75 m.
- **Why it makes no sense:** The effect applies only to the chosen ENEMY (and the game requires that choice - single/limited targets, some restricted to commander or missile units). The mod's cast passes the owner as the target, so nothing lands on any enemy; with no enemy-unit read (no card, id or health) the cast can neither be aimed nor gated.
- **Feasibility:** Not implementable as-is: the engine exposes no enemy unit read and enemy-targeted casts cannot be aimed by the mod - firing it blindly on self cannot deliver an enemy-targeted effect.

### Net of Amyntok — `net_of_amyntok` (#397)
- **Key(s):** `wh_dlc04_spell_bound_net_of_amyntok`
- **Current logic:** Rides `melee_unwavering` - fires when the unit is in melee, not routing and not wavering; the cast passes the owner itself as the target (`perform_special_ability(key, owner)`).
- **Game declares:** A single-ENEMY bound net (cant_move) for 20 s, range 100 m, 3 uses.
- **Why it makes no sense:** The effect applies only to the chosen ENEMY (and the game requires that choice - single/limited targets, some restricted to commander or missile units). The mod's cast passes the owner as the target, so nothing lands on any enemy; with no enemy-unit read (no card, id or health) the cast can neither be aimed nor gated.
- **Feasibility:** Not implementable as-is: the engine exposes no enemy unit read and enemy-targeted casts cannot be aimed by the mod - firing it blindly on self cannot deliver an enemy-targeted effect.

### Null Stone — `null_stone` (#398)
- **Key(s):** `wh3_dlc27_item_abilities_null_stone`
- **Current logic:** Rides `melee_unwavering` - fires when the unit is in melee, not routing and not wavering; the cast passes the owner itself as the target (`perform_special_ability(key, owner)`).
- **Game declares:** A self-activation field with NO target flags (not an aimed hex): 35 s of `silenced` + remove-magical over an unrestricted radius, applied to FRIENDS AND ENEMIES alike (num_effected_friendly_units = -1, num_effected_enemy_units = -1) - a global magic shutdown that also hits the bearer's own wizards.
- **Why it makes no sense:** The field has no connection to melee contact - it neither needs nor uses an engaged enemy - so the in-melee trigger is an arbitrary moment that silences the caster's own side for 35 s as a side effect; the tracker's own class for this key is the enemy-in-sight trigger, which is exactly what the mod cannot read.
- **Feasibility:** The enemy-in-sight condition is impossible (no enemy unit read exists); of the honest options, a readiness/no-condition activation would at least match the effect's untargeted, global nature. Not implementable as the tracker intended.

### Oath of Vengeance — `oath_of_vengeance` (#399)
- **Key(s):** `wh2_dlc10_lord_abilities_oath_of_vengeance`
- **Current logic:** Rides `melee_unwavering` - fires when the unit is in melee, not routing and not wavering; the cast passes the owner itself as the target (`perform_special_ability(key, owner)`).
- **Game declares:** A single-ENEMY hex: -24 Melee Defence for 44 s, range 200 m.
- **Why it makes no sense:** The effect applies only to the chosen ENEMY (and the game requires that choice - single/limited targets, some restricted to commander or missile units). The mod's cast passes the owner as the target, so nothing lands on any enemy; with no enemy-unit read (no card, id or health) the cast can neither be aimed nor gated.
- **Feasibility:** Not implementable as-is: the engine exposes no enemy unit read and enemy-targeted casts cannot be aimed by the mod - firing it blindly on self cannot deliver an enemy-targeted effect.

### Oil Flask — `oil_flask` (#400)
- **Key(s):** `wh2_dlc13_lord_abilities_oil_flask`
- **Current logic:** Rides `melee_unwavering` - fires when the unit is in melee, not routing and not wavering; the cast passes the owner itself as the target (`perform_special_ability(key, owner)`).
- **Game declares:** A thrown PROJECTILE fired at an enemy unit (`activated_projectile`): -48% speed and +50% flame weakness on contact, requires line of sight, range 70 m, 3 uses.
- **Why it makes no sense:** The effect applies only to the chosen ENEMY (and the game requires that choice - single/limited targets, some restricted to commander or missile units). The mod's cast passes the owner as the target, so nothing lands on any enemy; with no enemy-unit read (no card, id or health) the cast can neither be aimed nor gated.
- **Feasibility:** Not implementable as-is: the engine exposes no enemy unit read and enemy-targeted casts cannot be aimed by the mod - firing it blindly on self cannot deliver an enemy-targeted effect.

### Otto's Scythe — `ottos_scythe` (#401)
- **Key(s):** `wh3_dlc29_item_active_ottos_scythe`
- **Current logic:** Rides `melee_unwavering` - fires when the unit is in melee, not routing and not wavering; the cast passes the owner itself as the target (`perform_special_ability(key, owner)`).
- **Game declares:** A single-ENEMY hex: -40 Melee Attack, -24 morale, and negative charge-defence/reflection attributes for 28 s, range 100 m.
- **Why it makes no sense:** The effect applies only to the chosen ENEMY (and the game requires that choice - single/limited targets, some restricted to commander or missile units). The mod's cast passes the owner as the target, so nothing lands on any enemy; with no enemy-unit read (no card, id or health) the cast can neither be aimed nor gated.
- **Feasibility:** Not implementable as-is: the engine exposes no enemy unit read and enemy-targeted casts cannot be aimed by the mod - firing it blindly on self cannot deliver an enemy-targeted effect.

### Pack Trap — `pack_trap` (#402)
- **Key(s):** `wh3_dlc24_unit_abilities_pack_trap`
- **Current logic:** Rides `melee_unwavering` - fires when the unit is in melee, not routing and not wavering; the cast passes the owner itself as the target (`perform_special_ability(key, owner)`).
- **Game declares:** A single-ENEMY net (cant_move, +fatigue) for 10 s, range 100 m, 3 uses.
- **Why it makes no sense:** The effect applies only to the chosen ENEMY (and the game requires that choice - single/limited targets, some restricted to commander or missile units). The mod's cast passes the owner as the target, so nothing lands on any enemy; with no enemy-unit read (no card, id or health) the cast can neither be aimed nor gated.
- **Feasibility:** Not implementable as-is: the engine exposes no enemy unit read and enemy-targeted casts cannot be aimed by the mod - firing it blindly on self cannot deliver an enemy-targeted effect.

### Pageant of Shrikes — `pageant_of_shrikes` (#403)
- **Key(s):** `wh2_dlc16_character_abilities_pageant_of_shrikes`
- **Current logic:** Rides `melee_unwavering` - fires when the unit is in melee, not routing and not wavering; the cast passes the owner itself as the target (`perform_special_ability(key, owner)`).
- **Game declares:** A single-ENEMY hex: -60% ammunition replenishment, -20 reloading, -20% missile range for 20 s, range 75 m.
- **Why it makes no sense:** The effect applies only to the chosen ENEMY (and the game requires that choice - single/limited targets, some restricted to commander or missile units). The mod's cast passes the owner as the target, so nothing lands on any enemy; with no enemy-unit read (no card, id or health) the cast can neither be aimed nor gated.
- **Feasibility:** Not implementable as-is: the engine exposes no enemy unit read and enemy-targeted casts cannot be aimed by the mod - firing it blindly on self cannot deliver an enemy-targeted effect.

### Pestilent Potions — `pestilent_potions` (#405)
- **Key(s):** `wh3_dlc20_item_abilities_pestilent_potions`
- **Current logic:** Rides `melee_unwavering` - fires when the unit is in melee, not routing and not wavering; the cast passes the owner itself as the target (`perform_special_ability(key, owner)`).
- **Game declares:** An ENEMY hex affecting up to five units (spreads between enemies): -24 Melee Attack, -25% melee damage for 25 s, range 100 m.
- **Why it makes no sense:** The effect applies only to the chosen ENEMY (and the game requires that choice - single/limited targets, some restricted to commander or missile units). The mod's cast passes the owner as the target, so nothing lands on any enemy; with no enemy-unit read (no card, id or health) the cast can neither be aimed nor gated.
- **Feasibility:** Not implementable as-is: the engine exposes no enemy unit read and enemy-targeted casts cannot be aimed by the mod - firing it blindly on self cannot deliver an enemy-targeted effect.

## CLEAN

Judged a confident yes (all 22):

- horn_of_vaul (#354)
- howl_of_the_great_beast (#356)
- spell_slaanesh_hysterical_frenzy_bound (#360)
- jagged_dagger (#365)
- locus_of_abjuration (#366)
- locus_of_change (#367)
- locus_of_conjuration (#368)
- magical_animus (#371)
- master_of_the_black_arts (#377)
- master_rune_of_breaking (#379)
- master_rune_of_negation (#380)
- maw_shard (#382)
- miasma_of_despair (#384)
- mighty_oath_stone (#385)
- mighty_roar (#386)
- mimic_cold_blooded (#387)
- mimic_feint_and_riposte (#388)
- mimic_grand_hammer_of_faith (#389)
- morgrims_eye (#393)
- neferras_scrolls_of_mighty_incantations (#395)
- pearl_of_infinite_bleakness (#404)
- phas_protection (#406)
