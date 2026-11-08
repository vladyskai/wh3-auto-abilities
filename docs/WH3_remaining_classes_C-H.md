# WH3 remaining audit classes C-H — 29 abilities, one by one

Every entry below carries: the ability, its game key(s), what the game declares,
what the mod does now, why that makes no sense, and the feasibility note from the audit.
Write your decision on the `Your ruling:` line under each one.

One finding added after this report was written: **Empowering Shrooms (Class C) is
squig-only** (`invalid_target = unit_is_not_squig`) and cannot affect the caster.

---

## Class C — Ground-targeted casts sent via the unit form

#### 200. Cash Cascade  (slice 04)

- **Key(s):** `wh3_dlc26_character_abilities_cash_cascade`
- **Current logic:** trigger `charge_or_melee` - charge window OR in melee (not routing) - then casts on self.
- **Game declares:** Area augment: Charge Bonus +25%, Melee Attack +24, Leadership +8 "to self and allies". The game declares friends AND ground as the selectable targets: target_friends = true, target_ground = true, target_self = false, num_fr = -1, range 35 m, target_intercept_range 200 m.
- **Why it makes no sense:** Self is not a declared cast target - the game makes you aim this at a friendly unit or a ground point. The mod passes the caster as the unit target, which the engine may reject or re-interpret; the cast shape does not match the declared targeting.
- **Feasibility:** The class is exactly what the mod's own ground-cast doctrine describes ("the correct call for a key whose db row has target_ground = true"): the same tagging (friends + ground) is why Tactician's Stand Your Ground got the ground form. FOURTH.ground_cast exists and the own position is readable - one line in ground_keys (or an ally pick) applies.

**Your ruling:** ______________________________________________________________________________

**Your ruling:** ______________________________________________

#### 208. Empowering Shrooms  (slice 04)

- **Key(s):** `wh3_dlc26_character_abilities_empowering_shrooms`
- **Current logic:** trigger `melee_unwavering` then casts on self.
- **Game declares:** Ally area augment: Melee Attack +24, Leadership +16, Stops Rampage! "to allies in range" - target_friends = true, target_ground = true, target_self = false, num_fr = -1, range 35 m, intercept 100 m.
- **Why it makes no sense:** Self is not a declared target; the game asks for a friendly unit or a ground point (the area then covers the friends around it). The mod self-casts, so the cast shape contradicts the declared targeting.
- **Feasibility:** Ground form (cast at own feet via FOURTH.ground_cast) or an ally pick both match this class; the helper and the position read already exist.

**Your ruling:** ______________________________________________________________________________

**Your ruling:** ______________________________________________

#### 216. Gaze of Khaine  (slice 04)

- **Key(s):** `wh2_dlc10_lord_abilities_gaze_of_khaine`
- **Current logic:** trigger `melee_unwavering` then casts on self.
- **Game declares:** Area augment to self and allies: Melee Attack +24, AP +25%, Base +25%, Leadership +8 - but the ONLY declared target is the ground: target_ground = true, target_friends = false, target_self = false, num_fr = -1, range 35 m, intercept 100 m.
- **Why it makes no sense:** The game declares a ground-targeted cast (the area is placed at a point), and even the project's own approved activation for this key says "cast at own feet (existing ground-cast path)" - yet the shipped entry passes the unit target instead of the ground form.
- **Feasibility:** Own position is readable and FOURTH.ground_cast already exists for exactly this call shape; adding the key to ground_keys (cast at own feet) matches both the game data and the tracker's approved plan.

**Your ruling:** ______________________________________________________________________________

**Your ruling:** ______________________________________________

#### 218. Gulyas  (slice 04)

- **Key(s):** `wh3_dlc24_lord_abilities_gulyas`
- **Current logic:** trigger `ushoran_health` - owner at or below 75% health, no melee gate - then casts on self.
- **Game declares:** Area regeneration placed at a ground point: Heals +0.08%/tick, Leadership +4, Vigour -1%/s "to self and allies" (up to 5 friendly units) - target_ground = true, target_self = false, target_friends = false, num_fr = 5, range 35 m.
- **Why it makes no sense:** The only declared target is the ground; the mod passes the unit target. The project itself planned "cast at own feet (existing ground-cast path)" for this key, but the shipped entry is a plain self-cast.
- **Feasibility:** Ground form via FOURTH.ground_cast (own position readable) implements the approved plan; the trigger (own health <= 75%, health-only) fits the self+allies heal once the cast shape is right.

**Your ruling:** ______________________________________________________________________________

**Your ruling:** ______________________________________________

#### 229. Massacre  (slice 04)

- **Key(s):** `wh3_main_prisoners_massacre`
- **Current logic:** trigger `melee_unwavering` then casts on self.
- **Game declares:** Ally area augment: Melee Attack +24, AP +25%, Base +25% "to allies in range" - target_friends = true, target_ground = true, target_self = false, num_fr = -1, range 35 m.
- **Why it makes no sense:** Self is not a declared target; the game asks for a friendly unit or a ground point. The mod self-casts, so the cast shape contradicts the declared targeting.
- **Feasibility:** Ground form (FOURTH.ground_cast) or an ally pick matches the class; the helper and position read exist.

**Your ruling:** ______________________________________________________________________________

**Your ruling:** ______________________________________________

#### 230. Master of Alchemy  (slice 04)

- **Key(s):** `wh3_main_lord_abilities_master_of_alchemy`
- **Current logic:** trigger `metallurgy_melee` - owner in melee OR an in-melee ally within 25 m - casts on the OWNER (self).
- **Game declares:** Area augment: Base Missile Damage +25%, Base Weapon Damage +30%, Magical Attacks "to self and allies" - target_friends = true, target_ground = true, target_self = FALSE, num_fr = -1, range 35 m. (Its sibling keys Enchanted Metallurgy DO declare target_self = true; these Alchemy keys do not.)
- **Why it makes no sense:** The shared metallurgy evaluator always self-casts - legal for Enchanted Metallurgy (target_self = true) but not for this row, where self is not a declared target and the game asks for a friendly unit or a ground point.
- **Feasibility:** The evaluator already knows a qualifying in-melee ally (FOURTH.mtl_ally) and could pass it as the cast target, or the ground form could place the aura at the caster's feet; both reads exist.

**Your ruling:** ______________________________________________________________________________

**Your ruling:** ______________________________________________

#### 231. Master of Alchemy: Flaming  (slice 04)

- **Key(s):** `wh3_main_lord_abilities_master_of_alchemy_flaming`
- **Current logic:** trigger `metallurgy_melee` then casts on the owner (self).
- **Game declares:** Area augment: Base Missile Damage +50%, Base Weapon Damage +60%, Magical Attacks, Flaming Attacks "to self and allies" - target_friends = true, target_ground = true, target_self = false, num_fr = -1, range 35 m.
- **Why it makes no sense:** Same class as Master of Alchemy: self is not a declared target; the shared evaluator self-casts anyway.
- **Feasibility:** Ally pick (mtl_ally) or ground form at own feet; both supported by existing reads.

**Your ruling:** ______________________________________________________________________________

**Your ruling:** ______________________________________________

#### 232. Master of Alchemy: Piercing  (slice 04)

- **Key(s):** `wh3_main_lord_abilities_master_of_alchemy_piercing`
- **Current logic:** trigger `metallurgy_melee` then casts on the owner (self).
- **Game declares:** Area augment: AP Missile +25%, Base Missile +25%, AP Weapon +25%, Base Weapon +25%, Magical Attacks "to self and allies" - target_friends = true, target_ground = true, target_self = false, num_fr = -1, range 35 m.
- **Why it makes no sense:** Same class: self not a declared target; the evaluator self-casts.
- **Feasibility:** Ally pick or ground form; reads available.

**Your ruling:** ______________________________________________________________________________

**Your ruling:** ______________________________________________

#### 249. Star of Avelorn  (slice 05)

- **Key(s):** `wh2_dlc10_item_abilities_star_of_avelorn`
- **Current logic:** trigger `ushoran_health` (own health ≤ 75%) → self-cast through the ordinary unit form.
- **Game declares:** a GROUND-targeted group heal — `target_ground = true`, `target_ground_under_allies = true`, `target_self = false` (heals up to 3 friendly units in a 15 m area, 27 s, ×2 uses); the project's own record for it says "cast at own feet (existing ground-cast path)".
- **Why it makes no sense:** the db gives this ability no self target — the cast shape the game declares is the position form, not a unit target; the mod's `ground_keys` list omits this key, so what actually fires is the unit-target self-cast, which is not this ability's declared cast mode.
- **Feasibility:** the ground path already exists (`perform_special_ability_ground` at the caster's own position — tacticians_stand_your_ground rides it); adding this key is the concrete fix. The health-gated heal trigger itself is fine.

**Your ruling:** ______________________________________________________________________________

**Your ruling:** ______________________________________________

#### 350. Hellish Vigour Upgraded  (slice 07)

- **Key(s):** `wh3_dlc29_lord_abilities_hellish_vigour_upgraded`
- **Current logic:** Rides `melee_unwavering` - fires when the unit is in melee, not routing and not wavering; the cast passes the owner itself as the target (`perform_special_ability(key, owner)`).
- **Game declares:** The area version of the same augment: 35 m radius, all friendly units in range (`num_effected_friendly_units=-1`), caster still excluded (`affect_self=false`); valid target forms are a friendly UNIT or the GROUND (`target_friends=true`, `target_ground=true`, range 75 m).
- **Why it makes no sense:** Same mismatch as the base key: the self-cast matches neither declared target form and still cannot include the caster; the unit-target call passes the owner where the game expects a friendly unit or a ground point.
- **Feasibility:** Fixable without enemy reads: an ally pick, or the mod's existing own-position ground form (friends within 35 m of the caster would be covered; the caster correctly is not).

**Your ruling:** ______________________________________________________________________________

**Your ruling:** ______________________________________________

#### 456. Tacticians, Rally!  (slice 08)

- **Key(s):** `wh3_dlc24_character_abilities_tacticians_rally`
- **Current logic:** trigger `melee_unwavering`; casts on self through the normal unit-target call — the key is not in `FOURTH.ground_keys`.
- **Game declares:** a friend- and ground-targeted area Augment (`target_friends=true`, `target_ground=true`, 35 m aura affecting self+allies, cast range 100 m): +16 leadership for 14 s; 60 s recharge. Its targeting shape is identical to `wh3_dlc24_character_abilities_tacticians_stand_your_ground`, which the mod routes through the ground form (`perform_special_ability_ground`) via `FOURTH.ground_keys`. Tracker proposal: "cast on the wavering friendly unit."
- **Why it makes no sense:** the game declares ground targeting, and the mod's own convention (the `ground_keys` map, built for exactly this friend+ground shape) sends the identically-shaped SYG key through the ground form while this key fires the unit-target form on self — the two can't both be right; the declared friend/ground target is ignored either way.
- **Feasibility:** aligning it is a one-line addition to `FOURTH.ground_keys` (the ground-cast helper already ships), but the project's own comment says the ground path is API-documentation-backed rather than battle-proven — confirm in a live battle before trusting it.

**Your ruling:** ______________________________________________________________________________


---

**Your ruling:** ______________________________________________

---

## Class D — Heals or defensive effects gated behind melee

#### 118. Potion of Toughness  (slice 03)

- **Key(s):** `wh_main_item_abilities_potion_of_toughness`
- **Current logic:** trigger `melee_health75` — fires only when the unit is in melee AND its own health is at or below 75% (and not routing); cast on self via the default self-target call. The mod's own comment calls it "a ONE-TIME activation treated as a HEAL".
- **Game declares:** an active, self-targeted augment (`unit_abilities.type` = wh_type_augment; `unit_special_abilities` affect_self = true, all unit-target flags false, `ai_usage` = augment_melee_self) that for 21 s grants +30 armour, +24 melee defence and a small HP regeneration (heal_amount 0.0080); one use, 60 s recharge. Its game text: *"Those that consume a Potion of Toughness find their skin hardening as swords and arrows glance off their body…"* — i.e. protection that explicitly includes missile fire.
- **Why it makes no sense:** the mod treats the potion as a heal, yet gates it behind melee contact, so the defensive consumable can never fire before contact or while taking missile/artillery damage — exactly the "arrows" case its own text advertises ("a heal should not need melee"). The ≤75%-health arm alone already provides the "when hurt" condition; the extra melee requirement is not implied by the effect.
- **Feasibility:** both reads exist (is_in_melee and the proven HealthPercent read), and a health-only evaluator already ships (`ushoran_health` — the Ghoul King of Ushoran / Star of Avelorn "health ≤75%, no melee gate" pattern), so removing the melee arm needs no new reads or engine support. Note the tracker records the melee gate as a deliberate choice (armour/defence rationale), so this is flagged as a game-logic mismatch, not an engine limit.

**Your ruling:** ______________________________________________________________________________

**Your ruling:** ______________________________________________

#### 274. Armour of Caledor  (slice 05)

- **Key(s):** `wh2_dlc15_item_abilities_armour_of_caledor`
- **Current logic:** trigger `melee_unwavering` → self-cast.
- **Game declares:** a self regeneration — heals 1.6%/s for 20 s (≈32% max) with `cant_move = true`, ×3 uses (augment_spellcasting).
- **Why it makes no sense:** a heal should not need melee — the regeneration is gated behind being in melee, so it only ever fires after the unit is already engaged; a heal of this kind is usable before/during trouble regardless of engagement.
- **Feasibility:** implementable — self-cast target is fine; the `HealthPercent` read (already used by the ushoran_health family) would fit a regeneration item if a health gate is wanted.

**Your ruling:** ______________________________________________________________________________

**Your ruling:** ______________________________________________

#### 424. Reanimate Upgraded  (slice 08)

- **Key(s):** `wh2_dlc09_character_abilities_tomb_king_rally_upgraded`
- **Current logic:** trigger `melee_unwavering`; fires only while in melee and only while the unit is not wavering; self-cast (self-centred aura).
- **Game declares:** a self-centred area Augment (`area_of_augments`, range 35 m, affects self and allies) that for 10 s grants +16 leadership and replenishes hit points ("Replenishes hit points of combatants", `heal_amount=0.008`, `hp_change_frequency=1`); 90 s recharge. The tracker's proposal: "When morale falls to wavering: cast."
- **Why it makes no sense:** the hit-point replenish is a heal component gated behind melee contact (and suppressed while the unit is wavering), so it cannot respond when the unit or its friends are hurt outside melee — "a heal should not need melee". The project's own heal/replenish batch (36 entries) rides the ≤75%-health trigger with no melee gate; this row kept the melee gate.
- **Feasibility:** the health read and the `ushoran_health` evaluator already ship (`HealthPercent`, ≤75%, no melee gate), so no new reads are needed; the morale part could stay melee-gated if a split is preferred.

**Your ruling:** ______________________________________________________________________________


---

**Your ruling:** ______________________________________________

---

## Class E — Charge-component abilities on melee-only triggers

#### 272. Apocalyptic Charge  (slice 05)

- **Key(s):** `wh_pro04_unit_abilities_apocalyptic_charge`
- **Current logic:** trigger `melee_unwavering` → self-cast.
- **Game declares:** a charge effect — self-centred 35 m area with ×1.1 charge speed and ×1.2 charge bonus for 30 s (`ai_usage = aoe_centred_on_self`, `affect_self = true`). The cast target (self) is correct; the TRIGGER is the problem.
- **Why it makes no sense:** a charge effect should involve charging — the trigger only fires once the unit is already in melee, after the charge bonus has been spent; the charge window is deliberately excluded even though the mod carries charge detectors.
- **Feasibility:** implementable — ride `charge_or_melee` (or `charge_only`), which uses the existing `measure_charge` detector; no new reads needed.

**Your ruling:** ______________________________________________________________________________

**Your ruling:** ______________________________________________

#### 353. Horn of the Wild Hunt  (slice 07)

- **Key(s):** `wh_dlc05_item_abilities_horn_of_the_wild_hunt`
- **Current logic:** Rides `melee_unwavering` - fires when the unit is in melee, not routing and not wavering; the cast passes the owner itself as the target (`perform_special_ability(key, owner)`).
- **Game declares:** An army-wide +60% charge bonus to all friendly units for 24 s (`stat_charge_bonus` x1.6, radius -1 = unrestricted) - 'all Elven forces are driven to the Hunt'. A charge-window effect.
- **Why it makes no sense:** The trigger fires only once the unit is ALREADY in melee, i.e. after its own charge is spent - the one moment the wearer's charge bonus is definitionally wasted (other units' later charges could still benefit, but the item is a charge tool fired at the wrong phase). The tracker first set this key aside as 'charge-only' and its own rule maps charge effects to the charge-and-in-melee trigger the mod already runs for Fangspike/Onslaught.
- **Feasibility:** Cast-on-self is fine; the fix is trigger-side and uses proven machinery (the `measure_charge` detector / `charge_or_melee` trigger). Not enemy-limited.

**Your ruling:** ______________________________________________________________________________

**Your ruling:** ______________________________________________

#### 488. Twilight Horn I  (slice 09)

- **Key(s):** `wh2_dlc16_item_abilities_twilight_horn_i`
- **Current logic:** `melee_unwavering` — in melee (not wavering): cast on self (self is a legal target for this item).
- **Game declares:** an item augment on self or one friendly unit; 33 s: Charge Speed ×1.25, Speed ×1.25, Charge Bonus ×1.2 — a pure charge/movement effect.
- **Why it makes no sense:** trigger fit — the buff is spent on the next charge, but the trigger fires after contact, when the charge bonus can no longer apply; the project itself skipped the stronger twin (Twilight Horn II) as "unsuitable: movement" for exactly this reason.
- **Feasibility:** trigger-choice problem — the mod already ships a charge-window trigger for other charge-family abilities, so involving a charge needs no new reads.

**Your ruling:** ______________________________________________________________________________


---

**Your ruling:** ______________________________________________

---

## Class F — Engine-refused self casts

#### 291. Blooood!  (slice 06)

- **Key(s):** `wh_main_unit_abilities_blooood`
- **Current logic:** trigger `melee_unwavering` — fires when the Hellcannon is in melee (not routing/wavering), cast on itself.
- **Game declares:** a self augment (`wh_type_augment`, `affect_self=true`) — Speed +25%, Acceleration +18%, Vigour −2%/s for 18 s, 60 s recharge — with a hard usage gate: `cannot_perform_missile_attack` (the game's own wording: "Can use if: Missile attack possible"). Its text: *"The Hellcannon breaks its chains and rushes forwards."*
- **Why it makes no sense:** it is a rush-forward movement buff meant to be pressed while the Hellcannon can still fire, and the game refuses it the moment the unit cannot perform a missile attack — exactly the "in melee" state the mod fires it in. The trigger selects the one state where the cast is invalid and the speed effect has nothing left to close.
- **Feasibility:** not a read problem — the ability needs a moment *before* contact, so the in-melee trigger itself is wrong; as written every attempt is refused by the engine's own gate.

**Your ruling:** ______________________________________________________________________________

**Your ruling:** ______________________________________________

#### 295. Boom!  (slice 06)

- **Key(s):** `wh_main_unit_abilities_boom`
- **Current logic:** trigger `melee_unwavering` — fires when the Hellcannon is in melee, cast on itself.
- **Game declares:** a self augment for its own shots — +20% Armour-Piercing / +25% Base Explosive Damage for 15 s, 90 s recharge — gated by `cannot_perform_missile_attack` ("Enabled if: Missile attack possible").
- **Why it makes no sense:** the buff only means anything while the Hellcannon is shooting, and the game's own gate forbids it while the unit cannot perform a missile attack — which is precisely the in-melee state the trigger fires in. It cannot fire where it would matter, and would be pointless if it did.
- **Feasibility:** trigger problem, not a read problem — should fire before contact (while the guns still work); as written the in-melee cast is refused.

**Your ruling:** ______________________________________________________________________________

**Your ruling:** ______________________________________________

#### 307. Deranged Munitions  (slice 06)

- **Key(s):** `wh3_dlc25_lord_abilities_deranged_munitions`
- **Current logic:** trigger `melee_unwavering` — fires when the owner is in melee, cast on self.
- **Game declares:** a missile augment: +50% Armour-Piercing and +50% Base Missile Damage (+ Magical Attacks) for 30 s, with the game's own target restriction `cannot_perform_missile_attack` (targets that cannot perform a missile attack are invalid).
- **Why it makes no sense:** the trigger fires exactly while the owner cannot perform a missile attack (locked in melee), the state the game's target gate rejects; and even where it were legal, a missile-damage buff does nothing for a unit that cannot fire.
- **Feasibility:** needs a different condition/target (e.g. a friendly-unit picker outside the melee lock) — no new reads required for a friendly picker, but the in-melee self-cast is the one combination the game's data rejects.

**Your ruling:** ______________________________________________________________________________

**Your ruling:** ______________________________________________

#### 308. Deranged Munitions Upgraded  (slice 06)

- **Key(s):** `wh3_dlc25_lord_abilities_deranged_munitions_upgraded`
- **Current logic:** trigger `melee_unwavering` — fires when the owner is in melee, cast on self.
- **Game declares:** the area version of the same missile augment (+50% missile damage, 35 m ally aura, 30 s) with the same `cannot_perform_missile_attack` target restriction.
- **Why it makes no sense:** same contradiction as the base key — the in-melee state is exactly when the owner (and any melee-locked ally) is an invalid target for a missile-damage buff.
- **Feasibility:** same as the base key — a different trigger/target is needed; the in-melee self-cast cannot work as declared.

**Your ruling:** ______________________________________________________________________________


---

**Your ruling:** ______________________________________________

---

## Class G — Trigger fires in the wrong state

#### 378. Master Predator  (slice 07)

- **Key(s):** `wh2_dlc17_lord_abilities_master_predator`
- **Current logic:** Rides `melee_unwavering` - fires when the unit is in melee, not routing and not wavering; the cast passes the owner itself as the target (`perform_special_ability(key, owner)`).
- **Game declares:** A TOGGLE-able self stance (1 s recharge, duration until toggled off): +20% missile range, Snipe and Unspottable, -25% speed and charge speed - a stealth/sniper mode Oxyotl switches on to stalk from range.
- **Why it makes no sense:** Firing it when the unit is in melee is backwards: stealth, sniping and extra range do nothing once the unit is spotted and engaged, and the -25% speed hurts exactly when disengaging; worse, it is a toggle - a condition that simply re-checks 'in melee' on every guard cycle can flip the stance on/off repeatedly instead of enabling it once.
- **Feasibility:** No enemy read involved, but the ability needs toggle-aware handling (fire once to enable; never re-fire per guard cycle as a condition) that the current per-condition batch machinery does not have - not operable as-is.

**Your ruling:** ______________________________________________________________________________

**Your ruling:** ______________________________________________

#### 392. Moonshine  (slice 07)

- **Key(s):** `wh2_dlc11_item_abilities_moonshine`
- **Current logic:** Rides `melee_unwavering` - fires when the unit is in melee, not routing and not wavering; the cast passes the owner itself as the target (`perform_special_ability(key, owner)`).
- **Game declares:** A single-use courage draught granting Unbreakable (plus +25% melee damage and a small heal; -40% flame resistance as the cost), self-targeted, 15 s.
- **Why it makes no sense:** It is a last-stand item: the mod's standing rule maps the Unbreakable family to the wavering-self trigger and the mod's own items of this family (Helm of Yvresse, Vial of Troll Blood) fire on wavering - yet this rides `melee_unwavering`, which REQUIRES the unit not to be wavering, so the potion can never fire in the very state it is drunk for (about to break).
- **Feasibility:** Trigger-side fix only: the wavering read (`is_wavering`) and the wavering evaluators already exist; cast-on-self is correct. Not enemy-limited.

**Your ruling:** ______________________________________________________________________________

**Your ruling:** ______________________________________________

#### 398. Null Stone  (slice 07)

- **Key(s):** `wh3_dlc27_item_abilities_null_stone`
- **Current logic:** Rides `melee_unwavering` - fires when the unit is in melee, not routing and not wavering; the cast passes the owner itself as the target (`perform_special_ability(key, owner)`).
- **Game declares:** A self-activation field with NO target flags (not an aimed hex): 35 s of `silenced` + remove-magical over an unrestricted radius, applied to FRIENDS AND ENEMIES alike (num_effected_friendly_units = -1, num_effected_enemy_units = -1) - a global magic shutdown that also hits the bearer's own wizards.
- **Why it makes no sense:** The field has no connection to melee contact - it neither needs nor uses an engaged enemy - so the in-melee trigger is an arbitrary moment that silences the caster's own side for 35 s as a side effect; the tracker's own class for this key is the enemy-in-sight trigger, which is exactly what the mod cannot read.
- **Feasibility:** The enemy-in-sight condition is impossible (no enemy unit read exists); of the honest options, a readiness/no-condition activation would at least match the effect's untargeted, global nature. Not implementable as the tracker intended.

**Your ruling:** ______________________________________________________________________________

**Your ruling:** ______________________________________________

#### 482. Thunderburner  (slice 09)

- **Key(s):** `wh3_dlc25_unit_abilities_thunderburner`
- **Current logic:** `melee_unwavering` — in melee (not wavering): cast on self.
- **Game declares:** a self toggle for the flying Thunderbarge (cd 30 s): Speed ×2.5, Turn Speed ×0.3, with continuous self-damage (30 damage per hp tick) — a straight-line steam dash whose game text says it "soars forward at speed" and whose AI family is `hex_speed_under_fire` (a reaction to being under fire, not melee).
- **Why it makes no sense:** trigger fit — the ability's whole value is a long, pre-aimed dash across the field; firing it once the ship is already locked in melee spends the dash in the one state where its direction cannot be planned, while the self-damage cost still starts ticking.
- **Feasibility:** trigger-choice problem, not an engine limit — a different trigger moment (e.g. a movement/under-fire arm) uses reads the mod already has; no enemy targeting is involved.

**Your ruling:** ______________________________________________________________________________

**Your ruling:** ______________________________________________

#### 483. Thunderburner Upgraded  (slice 09)

- **Key(s):** `wh3_dlc25_unit_abilities_thunderburner_upgraded`
- **Current logic:** `melee_unwavering` — in melee (not wavering): cast on self.
- **Game declares:** same self toggle as 482, stronger: Speed ×3, Turn Speed ×0.3, continuous self-damage (10 per tick), `hex_speed_under_fire`.
- **Why it makes no sense:** trigger fit — same mismatch as Thunderburner: a planned dash fired from a melee scrum, where the movement cannot be directed and the damage cost applies anyway.
- **Feasibility:** trigger-choice problem, not an engine limit.

**Your ruling:** ______________________________________________________________________________

**Your ruling:** ______________________________________________

#### 519. Woven Mist  (slice 09)

- **Key(s):** `wh_dlc05_unit_abilities_woven_mist`
- **Current logic:** `melee_unwavering` — in melee (not wavering): cast on self.
- **Game declares:** a self toggle (permanent until disabled, 1 s recharge): −24 Melee Defence, +40 Missile Resistance — an anti-missile dance that pays for the protection with melee defence.
- **Why it makes no sense:** trigger fit — the toggle is fired exactly when the unit is in melee, i.e. when the melee-defence penalty bites and the missile protection is only partially relevant; the ability is built to be raised under missile fire, not in a melee.
- **Feasibility:** trigger-choice problem, not an engine limit — the mismatch is when it fires, not what it can read; the cast target (self) is correct.

**Your ruling:** ______________________________________________________________________________


---

**Your ruling:** ______________________________________________

---

## Class H — Effect does not fit the heal-family trigger

#### 556. Scroll of Power  (slice 10)

- **Key(s):** `wh_main_item_abilities_scroll_of_power`
- **Current logic:** trigger `ushoran_health` — fires when the unit's own health ≤75% and casts on itself (single use).
- **Game declares:** a one-use item effect ("runes to boost the power of a single spell"): 57 s positive phase with `ability_recharge_change = −60` and NO heal amount anywhere — it is an ability-recharge/spell-power boost, not a heal.
- **Why it makes no sense:** the entry rides the health-gated heal family, but the effect has nothing to do with the unit's health; the trigger cannot fit the effect, and firing it at ≤75% health wastes its one use at an arbitrary moment.
- **Feasibility:** no readable condition in the mod matches the ability's purpose (no magic-power or per-ability cooldown reads exist; only the engine's own readiness gate), so it should not ride this trigger at all.

**Your ruling:** ______________________________________________________________________________

**Your ruling:** ______________________________________________

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

**Your ruling:** ______________________________________________

---
