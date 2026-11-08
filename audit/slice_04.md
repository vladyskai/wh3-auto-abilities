# slice_04 — ABILITIES entries 175–232 (source order)

Counts: **audited 58 entries / 60 database keys · flagged 20 · clean 38.**
Judged against the game's own data (`unit_spec_abil.tsv` targeting flags, `phase_junc.tsv` target scope, `phases.tsv` effects, game text/loc) and the project's own recorded plans; engine limits noted where relevant. Every entry in this slice casts on **self** through the default `perform_special_ability(key, unit)` path — none of the 58 carries a bespoke cast target (the will_of_the_verminking / enchanted_metallurgy allies are pre-cast drift gates, not cast targets). No entry in the slice needs an enemy-unit read; the flagged entries are target mismatches only.

## FLAGGED


### 198. Meat Feast — `butcher`

- **Key:** `wh3_main_prisoners_butcher`
- **Mod's current logic:** trigger `ushoran_health` - fires when the OWNER's health is at or below 75% (no melee gate) - then casts on self (default `perform_special_ability(key, unit)`; no cast_target is set).
- **What the game declares:** An army-keyed single-target recover: Heals +2.8%/tick, Vigour -3%/s, "to allies in range" - target_friends = true, num_effected_friendly_units = 1, affect_self = false, target_self = false; the phase junction targets friends only. The game makes you pick ONE friendly unit; the caster is not among the legal targets and is not affected.
- **Why it does not make sense:** The effect lands on a friendly unit and never on the caster, yet the mod reads the caster's OWN health and points the cast at the caster - neither the trigger's health basis nor the cast target matches the declared target. A self-cast should be refused by the engine (self is not a legal target) or, if accepted, still applies the wrong way.
- **Feasibility:** Friendly units are readable - the mod already picks low-health allies (blood_sacrifice / eat_da_runts read `context_value(unit, "HealthPercent")` per friendly unit). An ally-heal picker (lowest-health in range) is the matching implementation; as-is the logic does not fit.

### 199. Captain of the Phoenix Guard — `captain_of_the_phoenix_guard`

- **Key:** `wh3_dlc27_character_abilities_captain_of_the_phoenix_guard`
- **Mod's current logic:** trigger `melee_health75` - in melee AND the owner at or below 75% health - then casts on self.
- **What the game declares:** A single friendly unit is the only target: Physical Resistance +30 and Heals +0.5%/tick, "to allies in range" - target_friends = true, target_self = false, num_effected_friendly_units = 1, only_affect_target = true, affect_self = false; the phase junction targets friends only.
- **Why it does not make sense:** The game declares one friendly unit as the target and applies the effect ONLY to that target, but the mod fires on the caster's own health and casts on the caster - a target the game does not list. The buff is intended for another unit (a hurt ally), not for the caster.
- **Feasibility:** Friendly health is readable (same reads as the ally-heal pattern already shipped for blood_sacrifice / eat_da_runts); an ally picker fixes the target, and the trigger could then key off the chosen ally's health instead of the caster's.

### 200. Cash Cascade — `cash_cascade`

- **Key:** `wh3_dlc26_character_abilities_cash_cascade`
- **Mod's current logic:** trigger `charge_or_melee` - charge window OR in melee (not routing) - then casts on self.
- **What the game declares:** Area augment: Charge Bonus +25%, Melee Attack +24, Leadership +8 "to self and allies". The game declares friends AND ground as the selectable targets: target_friends = true, target_ground = true, target_self = false, num_fr = -1, range 35 m, target_intercept_range 200 m.
- **Why it does not make sense:** Self is not a declared cast target - the game makes you aim this at a friendly unit or a ground point. The mod passes the caster as the unit target, which the engine may reject or re-interpret; the cast shape does not match the declared targeting.
- **Feasibility:** The class is exactly what the mod's own ground-cast doctrine describes ("the correct call for a key whose db row has target_ground = true"): the same tagging (friends + ground) is why Tactician's Stand Your Ground got the ground form. FOURTH.ground_cast exists and the own position is readable - one line in ground_keys (or an ally pick) applies.

### 204. Da Boss 'as a Plan! — `da_boss_as_a_plan`

- **Key:** `wh3_dlc26_character_abilities_da_boss_as_a_plan`
- **Mod's current logic:** trigger `melee_unwavering` - in melee, not routing or wavering (fail-open morale) - then casts on self.
- **What the game declares:** Single-friendly buff: Melee Defence +24, Leadership +8, Expert Charge Defence "to allies in range" - target_friends = true, target_self = false, num_effected_friendly_units = 1, affect_self = false; the phase junction targets friends only.
- **Why it does not make sense:** The declared target is one friendly unit and the buff never includes the caster, yet the mod casts on the caster - a unit the game does not offer as a target (the mod's own tracker row already carries the "cast on self for now (nearest-ally picker later)" caveat).
- **Feasibility:** Friendly units are readable and the ally-picker pattern is already proven in this mod (blood_sacrifice / eat_da_runts / glorious_death pass a chosen friendly unit as the cast target); the fix is a picker, not new reads.

### 208. Empowering Shrooms — `empowering_shrooms`

- **Key:** `wh3_dlc26_character_abilities_empowering_shrooms`
- **Mod's current logic:** trigger `melee_unwavering` then casts on self.
- **What the game declares:** Ally area augment: Melee Attack +24, Leadership +16, Stops Rampage! "to allies in range" - target_friends = true, target_ground = true, target_self = false, num_fr = -1, range 35 m, intercept 100 m.
- **Why it does not make sense:** Self is not a declared target; the game asks for a friendly unit or a ground point (the area then covers the friends around it). The mod self-casts, so the cast shape contradicts the declared targeting.
- **Feasibility:** Ground form (cast at own feet via FOURTH.ground_cast) or an ally pick both match this class; the helper and the position read already exist.

### 209. Favour of the Fay — `favour_of_the_fay`

- **Key:** `wh_dlc07_lord_abilities_favour_of_the_fay`
- **Mod's current logic:** trigger `melee_unwavering` then casts on self.
- **What the game declares:** Single-friendly buff: Melee Attack +40 - target_friends = true, target_self = false, num_effected_friendly_units = 1, affect_self = false; the game row gives friends as the target class.
- **Why it does not make sense:** The declared target is one friendly unit; the mod casts on the caster, which is not among the game's legal targets (the tracker row itself says "cast on self for now (nearest-ally picker later)").
- **Feasibility:** Friendly reads available; an ally picker matches the ability. As-is the self-cast does not match the declared target.

### 214. Fury of Khaine — `fury_of_khaine`

- **Key:** `wh2_main_unit_abilities_fury_of_khaine`
- **Mod's current logic:** trigger `charge_or_melee` - charge window OR in melee (not routing) - then casts on self.
- **What the game declares:** Single-friendly buff: Melee Attack +24, Armour-Piercing Weapon Damage +50%, Base Weapon Damage +50%, Rampage! "to allies in range" - target_friends = true, target_self = false, num_effected_friendly_units = 1, affect_self = false; the phase junction targets friends only.
- **Why it does not make sense:** The effect and its single target are an ally's (the wielder fires up another unit - e.g. the cauldron's Death Hags buff a chosen regiment), but the mod casts on the caster. The trigger itself (charge/melee) fits a melee buff, but the cast target does not.
- **Feasibility:** Ally picker (friendly units readable, pattern already shipped); as-is the self-cast targets the wrong unit.

### 216. Gaze of Khaine — `gaze_of_khaine`

- **Key:** `wh2_dlc10_lord_abilities_gaze_of_khaine`
- **Mod's current logic:** trigger `melee_unwavering` then casts on self.
- **What the game declares:** Area augment to self and allies: Melee Attack +24, AP +25%, Base +25%, Leadership +8 - but the ONLY declared target is the ground: target_ground = true, target_friends = false, target_self = false, num_fr = -1, range 35 m, intercept 100 m.
- **Why it does not make sense:** The game declares a ground-targeted cast (the area is placed at a point), and even the project's own approved activation for this key says "cast at own feet (existing ground-cast path)" - yet the shipped entry passes the unit target instead of the ground form.
- **Feasibility:** Own position is readable and FOURTH.ground_cast already exists for exactly this call shape; adding the key to ground_keys (cast at own feet) matches both the game data and the tracker's approved plan.

### 218. Gulyas — `gulyas`

- **Key:** `wh3_dlc24_lord_abilities_gulyas`
- **Mod's current logic:** trigger `ushoran_health` - owner at or below 75% health, no melee gate - then casts on self.
- **What the game declares:** Area regeneration placed at a ground point: Heals +0.08%/tick, Leadership +4, Vigour -1%/s "to self and allies" (up to 5 friendly units) - target_ground = true, target_self = false, target_friends = false, num_fr = 5, range 35 m.
- **Why it does not make sense:** The only declared target is the ground; the mod passes the unit target. The project itself planned "cast at own feet (existing ground-cast path)" for this key, but the shipped entry is a plain self-cast.
- **Feasibility:** Ground form via FOURTH.ground_cast (own position readable) implements the approved plan; the trigger (own health <= 75%, health-only) fits the self+allies heal once the cast shape is right.

### 220. Helping Hand — `helping_hand`

- **Key:** `wh2_pro08_character_abilities_helping_hand`
- **Mod's current logic:** trigger `melee_unwavering` then casts on self.
- **What the game declares:** Ally-anchored buff: Melee Attack +40, Damage Resistance +40 "to allies in range" - target_friends = true, target_self = false, affect_self = false, num_fr = -1; the phase junction targets friends only (the caster is never in the effect scope).
- **Why it does not make sense:** The ability is cast at a friendly unit and buffs the friends around it while excluding the caster - yet the mod self-casts. Self is not a legal target and the caster is not affected, so the cast cannot deliver what the trigger is waiting for (the tracker row: "cast on self for now (nearest-ally picker later)").
- **Feasibility:** Friendly reads available; a nearest-ally picker matches the ability.

### 222. Inspired Assault I — `inspired_assault_i`

- **Key:** `wh3_main_lord_abilities_inspired_assault_i`
- **Mod's current logic:** trigger `charge_or_melee` then casts on self.
- **What the game declares:** Single-friendly buff: Charge Bonus +20%, Melee Attack +24 "to allies in range" - target_friends = true, target_self = false, num_effected_friendly_units = 1, affect_self = false.
- **Why it does not make sense:** The charge bonus is meant for a unit on its way into combat - the game makes you target a friendly unit; the mod casts on the caster, which is not a declared target. (The trigger fits the effect; the cast target does not.)
- **Feasibility:** Ally picker (friendly units readable; the picker pattern already ships). As-is the self-cast does not match.

### 223. Inspired Assault II — `inspired_assault_ii`

- **Key:** `wh3_main_lord_abilities_inspired_assault_ii`
- **Mod's current logic:** trigger `charge_or_melee` then casts on self.
- **What the game declares:** Single-friendly buff: Charge Bonus +40%, Melee Attack +24 "to allies in range" - target_friends = true, target_self = false, num_fr = 1, affect_self = false.
- **Why it does not make sense:** Same mismatch as Inspired Assault I: the game's target is one friendly unit, the mod casts on the caster.
- **Feasibility:** Ally picker; friendly reads available.

### 224. Inspired Assault III — `inspired_assault_iii`

- **Key:** `wh3_main_lord_abilities_inspired_assault_iii`
- **Mod's current logic:** trigger `charge_or_melee` then casts on self.
- **What the game declares:** Single-friendly buff: Charge Bonus +40%, Melee Attack +40 "to allies in range" - target_friends = true, target_self = false, num_fr = 1, affect_self = false.
- **Why it does not make sense:** Same mismatch: declared target is one friendly unit; the mod self-casts.
- **Feasibility:** Ally picker; friendly reads available.

### 225. Inspired Defence I — `inspired_defence_i`

- **Key:** `wh3_main_lord_abilities_inspired_defence_i`
- **Mod's current logic:** trigger `melee_unwavering` then casts on self.
- **What the game declares:** Single-friendly buff: Melee Defence +24, Leadership +16 "to allies in range" - target_friends = true, target_self = false, num_fr = 1, affect_self = false.
- **Why it does not make sense:** Declared target is one friendly unit; the mod casts on the caster (the tracker row: "cast on self for now (nearest-ally picker later)").
- **Feasibility:** Ally picker; friendly reads available.

### 226. Inspired Defence II — `inspired_defence_ii`

- **Key:** `wh3_main_lord_abilities_inspired_defence_ii`
- **Mod's current logic:** trigger `melee_unwavering` then casts on self.
- **What the game declares:** Single-friendly buff: Melee Defence +24, Leadership +16, Expert Charge Defence "to allies in range" - target_friends = true, target_self = false, num_fr = 1, affect_self = false.
- **Why it does not make sense:** Declared target is one friendly unit; the mod self-casts.
- **Feasibility:** Ally picker; friendly reads available.

### 227. Inspired Defence III — `inspired_defence_iii`

- **Key:** `wh3_main_lord_abilities_inspired_defence_iii`
- **Mod's current logic:** trigger `melee_unwavering` then casts on self.
- **What the game declares:** Single-friendly buff: Melee Defence +40, Leadership +16, Expert Charge Defence "to allies in range" - target_friends = true, target_self = false, num_fr = 1, affect_self = false.
- **Why it does not make sense:** Declared target is one friendly unit; the mod self-casts.
- **Feasibility:** Ally picker; friendly reads available.

### 229. Massacre — `massacre`

- **Key:** `wh3_main_prisoners_massacre`
- **Mod's current logic:** trigger `melee_unwavering` then casts on self.
- **What the game declares:** Ally area augment: Melee Attack +24, AP +25%, Base +25% "to allies in range" - target_friends = true, target_ground = true, target_self = false, num_fr = -1, range 35 m.
- **Why it does not make sense:** Self is not a declared target; the game asks for a friendly unit or a ground point. The mod self-casts, so the cast shape contradicts the declared targeting.
- **Feasibility:** Ground form (FOURTH.ground_cast) or an ally pick matches the class; the helper and position read exist.

### 230. Master of Alchemy — `master_of_alchemy`

- **Key:** `wh3_main_lord_abilities_master_of_alchemy`
- **Mod's current logic:** trigger `metallurgy_melee` - owner in melee OR an in-melee ally within 25 m - casts on the OWNER (self).
- **What the game declares:** Area augment: Base Missile Damage +25%, Base Weapon Damage +30%, Magical Attacks "to self and allies" - target_friends = true, target_ground = true, target_self = FALSE, num_fr = -1, range 35 m. (Its sibling keys Enchanted Metallurgy DO declare target_self = true; these Alchemy keys do not.)
- **Why it does not make sense:** The shared metallurgy evaluator always self-casts - legal for Enchanted Metallurgy (target_self = true) but not for this row, where self is not a declared target and the game asks for a friendly unit or a ground point.
- **Feasibility:** The evaluator already knows a qualifying in-melee ally (FOURTH.mtl_ally) and could pass it as the cast target, or the ground form could place the aura at the caster's feet; both reads exist.

### 231. Master of Alchemy: Flaming — `master_of_alchemy_flaming`

- **Key:** `wh3_main_lord_abilities_master_of_alchemy_flaming`
- **Mod's current logic:** trigger `metallurgy_melee` then casts on the owner (self).
- **What the game declares:** Area augment: Base Missile Damage +50%, Base Weapon Damage +60%, Magical Attacks, Flaming Attacks "to self and allies" - target_friends = true, target_ground = true, target_self = false, num_fr = -1, range 35 m.
- **Why it does not make sense:** Same class as Master of Alchemy: self is not a declared target; the shared evaluator self-casts anyway.
- **Feasibility:** Ally pick (mtl_ally) or ground form at own feet; both supported by existing reads.

### 232. Master of Alchemy: Piercing — `master_of_alchemy_piercing`

- **Key:** `wh3_main_lord_abilities_master_of_alchemy_piercing`
- **Mod's current logic:** trigger `metallurgy_melee` then casts on the owner (self).
- **What the game declares:** Area augment: AP Missile +25%, Base Missile +25%, AP Weapon +25%, Base Weapon +25%, Magical Attacks "to self and allies" - target_friends = true, target_ground = true, target_self = false, num_fr = -1, range 35 m.
- **Why it does not make sense:** Same class: self not a declared target; the evaluator self-casts.
- **Feasibility:** Ally pick or ground form; reads available.

## CLEAN

- 175. `the_rotaxes`
- 176. `the_slayer_of_kings`
- 177. `the_slayer_sword`
- 178. `the_sword_of_couronne`
- 179. `the_tenderiser`
- 180. `toad_rage`
- 181. `tormentor_sword`
- 182. `tors_battle_hymn`
- 183. `transfix`
- 184. `unyielding_defender`
- 185. `ursuns_claw`
- 186. `warp_frenzy`
- 187. `warriors_crest`
- 188. `will_of_the_verminking`
- 189. `witstealer_sword`
- 190. `enchanted_metallurgy`
- 191. `enchanted_metallurgy_flaming`
- 192. `enchanted_metallurgy_piercing`
- 193. `enchanted_metallurgy_poison`
- 194. `bastions_defenders`
- 195. `battle_of_wills`
- 196. `bironas_timewarp`
- 197. `breath_of_hatred`
- 201. `chanson_of_caging`
- 202. `commanding_presence`
- 203. `curse_of_years`
- 205. `dazs_song_of_winter_sunlight`
- 206. `death_frenzy`
- 207. `dragonhorn`
- 210. `ferocious_battle_howl`
- 211. `ferocious_fury_of_ulric`
- 212. `ferocious_winters_chill`
- 213. `flame_incarnate`
- 215. `fury_of_ulric`
- 217. `grand_faiths_bastion`
- 219. `helm_of_yvresse`
- 221. `immovable_bulwark`
- 228. `lord_of_grand_cathay`
