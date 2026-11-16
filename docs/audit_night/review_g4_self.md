# Review g4: self-cast and timing families (night audit 2026-11-16/17)

Scope: 28 families, about 120 entries. Evaluators read in the live source (lines 8413-8545 charge/tired/barrier/ushoran, 8700 health_aura_self, 9040-9345 charge_only/wavering/blood sacrifice/eat da runts, 8776 glorious death, 13518 summon, 14321-14450 farsight/self_shooting/under_fire, 18050-18260 recharging/last stand/ammo/undead aura, 18959 when_ready, `measure_charge` at 6524).

Common gate, true for EVERY family below (so it is not repeated in each verdict): all evaluators return nothing while the unit is routing (`if routing then return nil`), and the dispatch adds the shared gates (armed, can_perform, 2 s guard, charge hold, back-off). None of the family sentences says "not routing". I propose leaving that out of the sentences (a routing unit is a different state from the player's point of view) but listing it here so the omission is a choice, not an oversight.

Charge detection (`measure_charge`, used by charge, charge_or_melee, charge_only, charge_or_wavering): `charging` is true when the unit `is_moving_fast()`, is NOT in melee, has a `current_target()`, the edge-to-edge distance to that target is 12 to 60 m, and the time to contact (distance / `fast_speed()`) is at most 4 s. If the distance or the speed cannot be read, that sub-test passes (fail open). So the "charge" is: running at an enemy it was ordered to attack, 12 to 60 m away, and no more than 4 s from impact.

---

## A. Families

### charge (1 entry: Deadly Onslaught)
- Current: "When armed, fires when this unit charges or is in melee"
- Code: not routing; either the charge window above (first) or `is_in_melee()` (no wavering check). Cast on self.
- Verdict: INCOMPLETE. "Charges" hides the 12-60 m / 4 s window; says nothing of routing.
- Proposed: "When armed, fires when this unit runs at an enemy it is attacking from 12 to 60 m away and reaches it within 4 s, or when it is in melee"

### charge_or_melee (37 entries)
- Current: "When armed, fires when this unit charges or is in melee"
- Code: identical to `charge` (it calls `evaluate_charge` and only renames the melee reason). No per-entry fields (no target_class, no aura_real). Cast on self (aura/enemy-debuff abilities are self-centred).
- Verdict: INCOMPLETE (same as charge). Note the family is two different things: 31 self buffs and 4 self-centred enemy debuffs (Seduction, Song of Enthrallment, Smoke Bomb, Maneater Smoke Bomb) that the user ruled onto this trigger (rule 10).
- Proposed: same as charge.

### charge_only (4 entries)
- Current: "When armed, fires when this unit charges"
- Code: charge window only, no melee arm. Not routing.
- Verdict: INCOMPLETE (window not described).
- Proposed: "When armed, fires when this unit runs at an enemy it is attacking from 12 to 60 m away and reaches it within 4 s"

### charge_or_wavering (1 entry: Bangers & Smash)
- Current: "When armed, fires when this unit charges or is wavering"
- Code: charge window (tested first) or `is_wavering()` exactly true (fail closed). Not routing.
- Verdict: INCOMPLETE (charge window).
- Proposed: "When armed, fires when this unit runs at an enemy from 12 to 60 m away and reaches it within 4 s, or when it is wavering"

### when_ready (21 entries, the Winds of Magic abilities)
- Current: "When armed, fires as soon as it is ready"
- Code: no condition except not routing (round 160). The shared gates decide readiness.
- Verdict: EXACT apart from the routing gate (a routing unit never fires).
- Proposed: "When armed, fires as soon as it is ready, unless the unit is routing" (honest, 56 characters of substance; drop the clause if routing is treated as common).

### ushoran_health (19 entries)
- Current: "When armed, fires when this unit is at or below 75% health"
- Code: `health_pct(unit) <= 75` on the caster only (no melee, no ally, no range, no morale or enemy test). Cast on self. No hysteresis by design.
- Verdict: EXACT for the conditions the code checks. The sentence is correct but the family is a bad fit for several of its abilities (see B): it ignores four game restriction flags and 3 abilities that are friend-targeted heals.
- Proposed: keep, or "When armed, fires when this unit's own health is at or below 75%".

### tired (2 entries / 5 keys: Dazh's Song x2, Foe-Seeker x3)
- Current: "When armed, fires when this unit is tired or worse"
- Code: `unit:fatigue_state()` in {tired, very_tired, exhausted}; fail closed if unreadable. Not routing.
- Verdict: EXACT.
- Proposed: keep.

### under_fire (4 entries)
- Current: "When armed, fires when this unit (or, for an aura, a friendly unit near it) is under missile fire"
- Code: caster `is_under_missile_attack() == true`; else, only for entries with `aura_real` (Shield of Chaqua), the closest other friendly unit (alive, not routing) inside the 70% aura bound that is under fire. No melee arm. Cast on self.
- Verdict: EXACT. ("near it" is vague but the bound is per entry; "within 70% of its aura" is more exact.)
- Proposed: "When armed, fires when this unit is under missile fire (for an aura, also when a friendly unit within 70% of its radius is)"

### melee_or_under_fire (4 entries)
- Current: "When armed, fires when this unit (or, for an aura, a friendly unit near it) is in melee or under missile fire"
- Code: melee arm uses `evaluate_in_melee_self`, which REFUSES when the unit is wavering (reads `wavering == true` as blocked); then caster under fire (no wavering test); then, for aura entries, a friendly unit in melee or under fire inside the bound (no wavering test for the ally).
- Verdict: INCOMPLETE. The "not wavering" clause on the caster's own melee arm is missing from the sentence and is inconsistent with the other two arms (a wavering unit in melee that is also under fire fires; one only in melee does not). Probably an inherited quirk, not a user decision.
- Proposed: "When armed, fires when this unit is in melee (and not wavering) or under missile fire; for an aura, also when a friendly unit within 70% of its radius is in melee or under fire"

### wavering_self (4 entries)
- Current: "When armed, fires when this unit is wavering"
- Code: `is_wavering() == true` exactly (fail closed), not routing.
- Verdict: EXACT.
- Proposed: keep.

### self_recharging (5) and self_recharging_2 (1)
- Current: "...when another ability of this unit is recharging" / "...when two other abilities of this unit are recharging"
- Code: count of THE MOD'S OWN accepted casts on this unit whose (effect + recharge) lock has not run out, excluding the entry's own keys. Needs 1 (or 2). The player's clicked casts and campaign recharge bonuses are invisible.
- Verdict: INCOMPLETE. The sentence reads like an engine fact; it is the mod's own bookkeeping, and the window includes the effect time, not only the recharge.
- Proposed: "When armed, fires when at least one (two, for Scroll of Power) other ability this mod cast on this unit is still active or recharging"

### recharging_in_reach (1: Spell-Wrought Sceptre)
- Current: "When armed, fires when this unit or a friendly unit near it has an ability recharging"
- Code: own recharge count >= 1, else `ab_pick_ally(unit, routing, "recharging")` (an ally within 70 m whose mod-cast lock is running); cast on self. Same bookkeeping limit.
- Verdict: INCOMPLETE (same as above; "near" = 70 m).
- Proposed: "When armed, fires when this unit, or a friendly unit within 70 m, has an ability this mod cast that is still active or recharging"

### self_shooting (1: Boom!)
- Current: "When armed, fires when this unit is shooting"
- Code: `shooting_past_cast_point` (ammo drop = firing on, plus 0.5 x reload past the first shot; moving units only if they fire on the move). Not routing.
- Verdict: INCOMPLETE ("shooting" means the engine's firing flag after the cast point, a few seconds into a volley).
- Proposed: "When armed, fires once this unit is shooting and has fired past half of one reload"

### self_shooting_clear (1: Of Warp and Ruin)
- Current: "When armed, fires when this unit is shooting at a target that is not in melee"
- Code: shooting_past_cast_point AND `target_in_melee(unit) == false` (unreadable fails closed).
- Verdict: EXACT in substance (same "shooting" caveat).
- Proposed: keep.

### self_shooting_healthy (1: Ominous Powder)
- Current: "When armed, fires when this unit is shooting and above half health"
- Code: shooting_past_cast_point AND health_pct > 50 (unreadable fails closed).
- Verdict: EXACT.
- Proposed: keep.

### self_out_of_ammo (1: Rock Bottom)
- Current: "When armed, fires when this unit has no ammunition left"
- Code: `ammo_left() <= 0` (a failed read does not fire). No health test although the ability deals 350 damage to the caster.
- Verdict: EXACT for what is checked; the missing health guard is a design gap (section B).
- Proposed: keep.

### self_moving (1: Blooood!)
- Current: "When armed, fires when this unit is moving"
- Code: `is_moving() == true` (any movement, not only a move order toward the enemy, any speed).
- Verdict: EXACT.
- Proposed: keep.

### self_last_stand (1: Hag's Denial)
- Current: "When armed, fires when this unit is at 10% health or less while in melee or under fire"
- Code: health_pct <= 10 and (is_in_melee or under_fire).
- Verdict: EXACT.
- Proposed: keep (or "at or below 10% health while in melee or under missile fire").

### self_summon_melee (1: Nurgling Tide)
- Current: "When armed, fires when this unit itself is fighting in melee and the summon is cast on it"
- Code: caster in melee (`is_in_melee() == true`), not routing; cast on self; fresh handle. No wavering test.
- Verdict: INCOMPLETE only in wording: "and the summon is cast on it" is filler (how it is cast, not when).
- Proposed: "When armed, fires when this unit is in melee"

### health_below_15 (1 entry / 5 keys: Tz'arkan)
- Current: "When armed, fires when this unit is below 15% health"
- Code: health_pct strictly < 15 (readable), not routing; self cast, one-way transform.
- Verdict: EXACT.
- Proposed: keep.

### health_aura_self (2: Locus of Fecundity, Salyak's Lullaby)
- Current: "When armed, fires when this unit or a friendly unit in its aura is at or below 75% health, cast on itself"
- Code: `ah_pick`: the lowest-health unit among the caster and other friendly units (alive, not routing) that is at or below 75% and inside 70% of the aura (Fecundity 38 m, Salyak 24 m); the cast is always on the caster. An unreadable gap counts as in range.
- Verdict: INCOMPLETE. "In its aura" means "within 70% of the aura's radius"; the player may expect the full radius. The tail "cast on itself" is how, not when.
- Proposed: "When armed, fires when this unit, or a friendly unit within 70% of its aura radius, is at or below 75% health"

### health_aura_self_undead (1: Icon of the King)
- Current: "When armed, fires when this unit or a non-living friendly unit in its aura is hurt"
- Code: same pick, restricted to units whose type is in the generated undead set, health <= 75%, within 24 m (70% of 35). The caster only counts if it is itself undead.
- Verdict: INCOMPLETE: "hurt" is the 75% line.
- Proposed: "When armed, fires when this unit, or a friendly unit within 70% of its aura radius, is non-living and at or below 75% health"

### barrier_broken (1: Eagle-Feather Torc)
- Current: "When armed, fires when this unit's barrier breaks"
- Code: BarrierHp <= 0 with BarrierMaxHp > 0, both readable.
- Verdict: EXACT. Proposed: keep.

### blood_sacrifice (1)
- Current: "When armed, fires on the lowest-health ally in range when it is at or below 75% health"
- Code: other friendly units (alive, not routing) at or below 75% inside 70 m (70% of the 100 m reach); the lowest health wins; cast ON that ally. No test of the caster's own health.
- Verdict: INCOMPLETE ("in range" = 70 m; "ally" = another unit than the caster).
- Proposed: "When armed, fires on the lowest-health other friendly unit within 70 m that is at or below 75% health"

### eat_da_runts (1)
- Current: "When armed, fires when this unit is at or below 75% health, otherwise on the lowest-health ally in range"
- Code: own health <= 75 first (cast on self), else the blood_sacrifice pick within 70 m (70% of the 100 m reach), cast on that ally.
- Verdict: EXACT in substance; "in range" = 70 m.
- Proposed: "When armed, fires on this unit if it is at or below 75% health, else on the lowest-health other friendly unit within 70 m that is"

### glorious_death (1)
- Current: "When armed, fires when a Slayer ally in range is in melee"
- Code: (a) the closest in-melee, non-routing Slayer ally (type key in the 10-key list) within 38 m (70% of 55 m) arms it; (b) otherwise the caster itself arms it only if IT is a Slayer in melee; (c) else silent. Cast always on the caster.
- Verdict: INCOMPLETE. The sentence omits arm (b) (a Slayer caster in melee fires without any ally), the 38 m bound and that routing allies do not count.
- Proposed: "When armed, fires when this unit is a Slayer in melee, or a Slayer friendly unit in melee is within 38 m"

### no_enemy_in_range_within_boost (1: Potion of Farsight)
- Current: "When armed, fires when no enemy is in this unit's missile range but one is just beyond it"
- Code: not in melee, `ammo_left() > 0`, `missile_range() > 0`, no enemy within the range, nearest enemy within range x FARSIGHT_BAND (1.21, the potion's +30% boost reduced for margin). Not routing.
- Verdict: INCOMPLETE. Missing "has ammunition", "not in melee", and the 1.21 bound ("just beyond").
- Proposed: "When armed, fires when this unit has ammunition, is not in melee, has no enemy in missile range, and the nearest enemy is within 1.21 times that range"

---

## B. Abilities

Scores follow the brief. "UR" = user ruling in the tracker. Restriction column says "OK" when honoured or irrelevant to a self-cast.

### charge / charge_or_melee / charge_only / charge_or_wavering

| Marker | Ability | Effect (short) | Score | Why | Better trigger (<=3) | Restriction issue |
|---|---|---|---|---|---|---|
| deadly_onslaught | Deadly Onslaught (charge) | +60% charge bonus, +25% weapon dmg | 5 | Reference: pays on the impact. | | OK |
| (charge_or_melee) deadly_onslaught / daemonic_onslaught | Daemonic Onslaught | +60% charge bonus, +25% dmg | 5 | Same effect, same moment. | | OK |
| bloodthirst | Bloodthirst | charge speed, speed, +40% charge bonus | 5 | Pure charge buff. | | OK |
| crimson_juggernaut | Crimson Juggernaut | +50% charge speed, +40% charge bonus | 5 | Pure charge buff. | | OK |
| fangspike | Fangspike | +40% charge bonus, +50% dmg | 5 | Charge bonus plus damage in the first clash. | | OK |
| heart_piercing | Heart Piercing | +40% charge bonus, +50% AP | 5 | Charge buff. | | OK |
| star_lance | Star Lance | +60% charge bonus, +25% AP | 5 | Charge buff. | | OK |
| stormlance | Stormlance | +40% charge bonus, +75% dmg | 5 | Charge buff. | | OK |
| storm_hammer | Storm Hammer | +40% charge bonus, +40 melee attack | 5 | Charge plus melee. | | OK |
| morglor | Morglor the Mangler | +20% charge, +75% dmg | 5 | Charge plus melee damage. | | OK |
| storm_rage | Storm Rage | +20% charge, +24 MA, +25% dmg | 5 | Pays off in the clash and after. | | OK |
| tempest_rage | Tempest Rage | +20% charge, +24 MA, +25% dmg, a stance | 4 | Good; the "Stance" phase attribute is a stance (CLAUDE.md: stances not automated); check it is not a stance toggle. | | See C |
| locus_of_fury | Locus of Fury | +40% charge, +25% dmg (self+allies) | 4 | Self-centred aura: only helps allies standing near at the cast. | | OK |
| locus_of_swiftness | Locus of Swiftness | +25% charge speed/speed, +40% charge (aura) | 4 | As above. | | OK |
| cash_cascade | Cash Cascade | +25% charge, +24 MA, +8 Ld (aura) | 4 | As above. | | OK |
| horn_of_the_first_beast | Horn of the First Beast | +20% charge, +24 MA, +8 Ld (aura) | 4 | As above. | | OK |
| the_horn_of_kygor | The Horn of Kygor | +20% charge, +24 MA, +8 Ld (aura) | 4 | As above. | | OK |
| bironas_timewarp | Birona's Timewarp | +25% charge speed/speed, +24 MA (aura) | 4 | Good; aura radius 35 m, target need not be within. | | OK |
| book_of_arkhan | Book of Arkhan | +25% speed, +24 MA (aura) | 4 | Speed pays in the charge, MA after. | | OK |
| masterful_strike / mastered_strike | Masterful Strike | +16 vs large, +26 MA, +25% dmg | 4 | Fine; best when the target is large. | Charge or melee vs a LARGE current target (target_class set exists) would be a 5. | OK |
| colossal_strike (x2 keys) | Colossal Strike | +16 vs large, +25% dmg, immune to psychology | 4 | Same. | Same large-target gate. | OK |
| guiding_strike | Guiding Strike | +24 MA, contact weakened | 4 | Melee effect, fires a few seconds early. | | OK |
| pendant_of_slaanesh | Pendant of Slaanesh | +25% speed, +40 MA | 4 | UR 2026-11-09 "Charge, else in melee". | | OK |
| lightning_reflexes | Lightning Reflexes | +25% speed, +20 dmg resistance | 4 | UR 2026-11-09. | | OK |
| master_of_the_skies | Master of the Skies | +25% speed, +40 MD | 4 | UR 2026-11-09. | | OK |
| slippery | Slippery | +25% speed, +24 MD | 4 | Melee in-melee arm; UR block 4. | | OK |
| transfix | Transfix | +25% speed, +20 resist, contact discouraged | 4 | UR melee batch. | | OK |
| purge_the_weak | Purge the Weak! | +30% speed, +6 Ld, -0.02 fatigue | 4 | Charge-and-melee all fine. | | OK |
| full_power | Full Power! | +100% accel, -70% turn, +50% speed | 4 | Charge arm is the payoff; the melee arm wastes it (-70% turn rate is a cost in melee). | Charge window only (charge_only) would be a 5. | OK |
| more_power | More Power! | +25% charge speed, +150% accel, +25% speed, +50% mass | 4 | Mass and acceleration pay on the charge; speed is wasted in melee. | Charge only. | OK |
| rune_of_speed / master_rune_of_speed | Runes of Speed | +45% speed, +24 MA (aura) | 4 | Fine. | | Rune lock: see C |
| shield_of_thorns (x2 keys) | Shield of Thorns | +20 melee damage reflection (aura) | 3 | Reflection only matters when STRUCK; the charge arm fires up to 4 s before contact and burns the window. | Melee (unwavering) only, or fire when an enemy is in melee with it. | OK |
| seduction | Seduction | enemy -25% speed, -24 MA | 4 | UR/rule 10 (enemy slows on charge or melee). | | OK |
| song_of_enthrallment | Song of Enthrallment | enemy -45% speed, -24 MA | 4 | Same (round 123). | | `climbing` usage flag: siege, not modelled (fine) |
| smoke_bomb | Smoke Bomb | enemy -60% speed | 4 | Same (round 123). | | auto-deactivate `manning_equipment`: siege only |
| maneater_smoke_bomb | Maneater Smoke Bomb | +25% speed, +24 MD, enemy speed down | 4 | Round 159 look-alike ruling. | | OK |
| apocalyptic_charge | Apocalyptic Charge | +10% charge speed, +20% charge bonus | 5 | charge_only, pure charge. | | OK |
| ferocious_battle_howl | Ferocious Battle Howl | +50% charge speed, +40% charge, +50% mass | 5 | Pure charge. | | OK |
| potion_of_speed | Potion of Speed | +25% charge speed/speed, accel | 5 | Pure charge. | | OK |
| twilight_horn_i | Twilight Horn I | +25% charge speed/speed, +20% charge | 5 | Pure charge. | | OK |
| bangers_and_smash | Bangers & Smash | +20% charge, +12 Ld (aura) | 4 | Two arms: charge bonus on the run-in, leadership when wavering. UR block 8. | | OK |

### when_ready (21)

All 21 are Winds of Magic regen/miscast/mastery buffs. Score 4 for every one: UR 2026-11-14 "All when ready". The ruling is respected. Two refinements are feasible: the map log has a WINDS row (current / reserve / recharge) every 2 s, so "caster's pool below X and not routing" is a real read (the pool is NOT full at start, user screenshot 12/100); and several abilities only matter if the caster has spells to cast (Jagged Dagger's owner is a Bray-Shaman who fled). Neither would change the score below 4.

| Marker | Ability | Effect (short) | Score | Why | Better trigger (<=3) | Restriction issue |
|---|---|---|---|---|---|---|
| arcane_hymn, black_periapt, book_of_hoeth, extra_ingredients, jagged_dagger, locus_of_conjuration, neferras_scrolls, prismatic_amplifier, unlimited_power, winds_of_change | recharge +60% (some +0.2 reserve/s) | winds recharge | 4 | Fires on the first ready tick; the buff is useful while the pool refills. UR. | | OK |
| scroll_of_destiny, skull_of_rarkos, starwood_staff | +0.4 reserve/s | winds reserve | 4 | Same; the earlier the better. UR. | | OK |
| staff_of_volans, staff_of_wu_xing, whispering_skull | recharge +140%, miscast -50% | winds | 4 | Same. UR. | | OK |
| snowflake_pendant, stave_of_avelorn | miscast -50/-100%, recharge +60% | miscast safety | 3 | Miscast reduction only pays WHILE the wizard casts; cast at tick 1 the 26-30 s window may expire before the first spell. | Fire when the caster (a wizard) has enough Winds to cast; or when its own spells are off cooldown. No spell-ready read exists, so 4 with UR stands. | OK |
| power_stone, the_chromatic_tome | recharge -20%, +0.1 reserve/s | winds | 3 | The recharge LOSS (-20%) is applied for the duration; with the UR "all when ready" it is net negative on recharge for a small reserve gain, and it uses a charge (Power Stone has 1 use). | Fire only when the pool is low (WINDS row current < 50%); or ask the user whether he wants these two (Power Stone, Chromatic Tome) and Warpstone Tokens on the same rule. | OK |
| warpstone_tokens | miscast -50%, recharge -20%, +0.5 reserve/s | winds | 4 | +0.5/s outweighs the -20%. UR. | | OK |

### ushoran_health (19)

| Marker | Ability | Effect (short) | Score | Why | Better trigger (<=3) | Restriction issue |
|---|---|---|---|---|---|---|
| ghoul_king_of_ushoran | Ghoul King of Ushoran | +8 Ld, heal 0.8%/s | 4 | Heal that works at any time; 75% line is arbitrary but UR. | | OK |
| blood_chalice | Blood Chalice | heal 1.6%/s | 5 | Strong self heal at 75%. | | OK |
| blood_chalice_of_bathori | Blood Chalice of Bathori | heal 1.6%/s, fatigue (self+allies), friend-target | 3 | Friend-targeted (reach 60 m); self-only trigger wastes the ally side. | ally_heal / health_aura_ally with a commander filter (a commander list exists). | `unit_is_not_commander_class`: target must be a Lord/Hero, not modelled; fine for a self cast by a character, but the ally side would need it |
| undeath_morkharn_breath_of_darkness (+ upgraded) | Breath of Darkness | heal, resurrect, -fatigue (friend-target 200 m) | 3 | A 200 m friend-target heal cast only on the caster. | health_aura_ally with the generated undead set (exists since round 144) | `living_unit` (caster must be undead: not checked for self, unlikely); `hp_replenish_cap_reached` NOT honoured (engine refuses, back-off absorbs it) |
| bugmans_xxxxxx | Bugman's XXXXXX | heal 1.7%/s, -fatigue | 3 | A drink; the game forbids it with an enemy in the intercept range, so at 75% in a fight it is refused and retried. | Fire at <=75% only when no enemy is within the ability's intercept range (nearest_enemy_gap exists). | `enemies_in_intercept_range` NOT honoured (usage flag) |
| hieratic_jar | Hieratic Jar | heal, resurrect | 4 | Health includes dead men, so it fires on casualties. | | OK |
| immortal_will | Immortal Will | heal 0.8%/s | 4 | Fine. | | `morale_is_broken_or_lower`: effectively honoured by the routing gate; confirm "broken" = routing (C) |
| invocation_of_nehek | Invocation of Nehek | heal, resurrect | 4 | Fine. | | `hp_replenish_cap_reached` NOT honoured (no read); back-off handles it |
| mantra_of_invigoration | Mantra of Invigoration | heal 0.65%/s, -fatigue, friend (100 m) | 3 | UR "below 75% no melee gate" for the OWNER, but it is a friend-target heal that reaches allies. | Ally-aware pick, filtered to Tiger Warriors (type key list needed) | `unit_is_not_tiger_warrior` NOT modelled (no key list) |
| neuroparasites | Necroparasites | heal 1.6%/0.5 s, resurrect | 4 | Strong, fine. | | `hp_replenish_cap_reached`, `on_a_platform`: first not honoured, second is siege |
| necrotic_phylactry | Necrotic Phylactery | +15 spell resist, contact immunity, spreading area | 2 | A defensive/anti-magic ward; health <=75% has no relation to the effect. | Fire when an enemy spellcaster/missile threat is near, or when under fire (under_fire family); user to decide. | OK |
| pestilent_regeneration | Pestilent Regeneration | heal 0.4%/s + spreading area | 4 | Fine. | | OK |
| potion_of_charoi | Potion of Charoi | +40 damage resistance, heal | 3 | The resistance pays in melee; a health trigger without a melee gate can burn it while marching hurt. | Health <= 75% AND in melee or under fire. | OK |
| potion_of_healing | Potion of Healing | heal 0.8%/s | 4 | Fine. | | `hp_replenish_cap_reached`, `morale_is_broken_or_lower` (second effectively honoured by the routing gate) |
| regenerating_flesh | Regenerating Flesh | heal 0.8%/s | 4 | Fine. | | `morale_is_broken_or_lower` (as above) |
| saint_annushkas_finger_bone | Saint Annushka's Finger Bone | heal 0.2%/s, self+allies | 3 | Tiny heal; effect_range 0 in the data so the ally side cannot be tested. | Fine as is; low value either way. | OK |
| skalm | Skalm | heal 0.8%/s | 4 | Fine. | | `morale_is_broken_or_lower` (as above) |
| skars_kraken_killer | Skar's Kraken-Killer | invulnerable, heal 1.6%/s, -fatigue | 3 | Invulnerability pays when about to die, not at 75%. | Health <=50% (or a last-stand line) while in melee. | OK |

### tired (2 entries)

| Marker | Ability | Effect (short) | Score | Why | Better trigger (<=3) | Restriction issue |
|---|---|---|---|---|---|---|
| dazhs_song_of_winter_sunlight (x2 keys) | Dazh's Song of Winter Sunlight | fatigue -1 (self+allies in range) | 4 | Fatigue effect meets the fatigue trigger; self read only, allies tired would be better. | Tired self OR >=1 tired friendly in aura (fatigue_state is readable per unit). | OK |
| foe_seeker (x3 keys) | Foe-Seeker | +25% speed/charge speed, -0.01 fatigue | 3 | UR block 2 / 2026-11-15 "Foe-Seeker + tired", but the main stats are speed buffs that pay on a charge or a chase, not when resting. | charge_or_melee (the user may keep tired: user ruling). | OK |

### under_fire (4) and melee_or_under_fire (4)

| Marker | Ability | Effect (short) | Score | Why | Better trigger (<=3) | Restriction issue |
|---|---|---|---|---|---|---|
| shield_of_chaqua | Shield of Chaqua | +40 missile resist (aura 55) | 5 | Exactly the moment. | | OK |
| golden_eye_of_tzeentch | The Golden Eye of Tzeentch | +40 missile resist, barrier restore | 5 | Same. | | OK |
| lions_shield | The Lion's Shield | +40 spell and missile resist | 5 | Fires under missile fire; spell side missed (no read for spells). | | OK |
| morikhane | Morikhane, the Black Armour | missile mirror (behaviour) | 4 | Reflects shots; fine. | | `unit_is_artillery_or_war_machine`: carrier is a character, harmless |
| blessed_helm_of_the_oblast | Blessed Helm of the Oblast | +60 armour, +20 missile resist (aura) | 5 | Both threats covered. | | OK |
| charmed_shield | Charmed Shield | +25 block, +20 dmg resist | 5 | Same. | | OK |
| glacial_defence | Glacial Defence | -25% speed, +60 armour, +20 missile resist | 4 | The speed loss is a cost; trigger fine. | | OK |
| the_bane_shield | The Bane Shield | +30 armour, +24 missile block (aura) | 5 | Same. | | OK |

### wavering_self (4)

| Marker | Ability | Effect (short) | Score | Why | Better trigger (<=3) | Restriction issue |
|---|---|---|---|---|---|---|
| ferocious_fury_of_ulric | Ferocious Fury of Ulric | fear, unbreakable (aura) | 5 | Saves the wavering unit. | | OK |
| vial_of_troll_blood | Vial of Troll Blood | unbreakable (aura) | 5 | Exactly the moment. | | OK |
| helm_of_yvresse | Helm of Yvresse | cannot die, unbreakable | 4 | Unbreakable fits; "cannot die" would be better at low health. | | OK |
| verminous_valour | Verminous Valour | +25% speed, +8 Ld, escape melee | 4 | Round 159 look-alike ruling. | | OK |

### recharge families, shooting families, singles

| Marker | Ability | Effect (short) | Score | Why | Better trigger (<=3) | Restriction issue |
|---|---|---|---|---|---|---|
| aken_seth, channelling_staff, staff_of_nagash, staff_of_tomorrow, the_liber_noctus | recharge -15/-30/-120 s | self_recharging | 4 | UR round 141 "1 ability recharging". The mod's lock includes the effect time, so the first seconds can be wasted. | Count only the recharge part, not the effect (needs one more constant). | Liber Noctus deals 33 damage to the caster: no health guard |
| scroll_of_power | Scroll of Power | -60 s recharge, 1 use | 4 | UR "2+ abilities recharging". | | OK |
| spell_wrought_sceptre | Spell-Wrought Sceptre | -30 s recharge (aura) | 4 | UR "recharging unit in reach". | | OK |
| boom | Boom! | +25% explosive damage | 4 | Fires once shooting; firing flag unproven in the field. | | `cannot_perform_missile_attack` (usage): honoured because shooting implies it |
| of_warp_and_ruin | Of Warp and Ruin | +40% explosive, +20% radius | 5 | UR round 142 "Shooting, not into melee". | | OK |
| ominous_powder | Ominous Powder | +40% missile damage, 26 dmg to self | 4 | UR round 142 "health above 50%". | | OK |
| rock_bottom | Rock Bottom | refill 30% ammo, 350 dmg to caster | 3 | UR "wait until no ammo left", but the 350 self-damage is not guarded. | Out of ammo AND health above a safe line (for example the unit's remaining HP clearly above 350). | No health guard (a design gap) |
| blooood | Blooood! | +25% speed, +18% accel, -fatigue | 3 | Fires on any movement (a short reposition burns the cast). | Moving fast (is_moving_fast; the Hellcannon never runs, so use a distance-to-ordered-position test) toward an enemy beyond a threshold. | `cannot_perform_missile_attack` usage NOT checked (ammo test unknown) |
| hags_denial | Hag's Denial | cannot die, +40 resist | 5 | UR "10%, melee or fire". | | OK |
| nurgling_tide | Nurgling Tide | summons in melee | 4 | UR; charge gate for the empty-pool case. | | `on_a_platform`: siege |
| tzarkan | Tz'arkan | one-way transform | 5 | UR "below 15% health". | | `climbing_manning_eq_on_platform`: siege |
| locus_of_fecundity, salyaks_lullaby | Heals 0.8%/s (aura 55 / 35) | health_aura_self | 5 | Ally-aware, bound at 70%. | | OK |
| icon_of_the_king | Icon of the King | heal, resurrect, -fatigue (aura 35) | 5 | Undead-only pick. | | `living_unit` honoured by the undead set |
| eagle_feather_torc | Eagle-Feather Torc | barrier restore 0.1 | 5 | Exactly when the barrier breaks. | | OK |
| blood_sacrifice | Blood Sacrifice | heal 1%/s allies, 144 dmg to the caster entity | 4 | Ally pick fine; the caster's cost is unguarded but small. | | friends=yes, self=no honoured (ally only) |
| eat_da_runts | Eat da Runts! | 144 dmg to one entity, heal 1.5%/s, -fatigue | 3 | Self arm casts on the caster though the target flags say self=no; both arms follow the same 75% line. | Confirm in battle that the self arm lands (C). | Target flag self=no vs a self cast |
| glorious_death | Glorious Death | cannot die (aura) | 4 | Slayer-only gate; the UR corrected this trigger in the field. | | `unit_is_not_slayer` honoured by the 10-key list (Gotrek-type keys missing: under-approximation) |
| potion_of_farsight | Potion of Farsight | +30% range | 5 | Exactly the moment (enemy just outside the range). | | OK |

---

## C. Game-mechanics questions

1. Is `morale_is_broken_or_lower` (Immortal Will, Potion of Healing, Regenerating Flesh, Skalm) exactly "routing"? If "broken" is a state before routing, the routing gate does not cover it.
2. `enemies_in_intercept_range` on Bugman's XXXXXX: is the intercept range the ability's `target_intercept_range` (a tabled value)? If it is a fixed 20-30 m, `nearest_enemy_gap` can honour it.
3. `hp_replenish_cap_reached` (Potion of Healing, Invocation of Nehek, Necroparasites, Breath of Darkness x2): what the cap is (a share of lost men that cannot be healed?) and whether `unit:health_percent` approximations can read it. The mod now retries into a refusal and backs off.
4. Does `perform_special_ability` with a friend-targeted key (self=no, friends=yes: Eat da Runts, Blood Sacrifice) work when aimed at the caster itself? Eat da Runts' self arm depends on it.
5. Are Mantra of Invigoration (100 m), Blood Chalice of Bathori (60 m) and Breath of Darkness (200 m) really useful on allies in the field? Their game targeting is friend-only; ally picking (health_aura_ally style) needs a Tiger Warrior key list, the commander list and the undead set (the latter two exist).
6. Is Tempest Rage's "Stance" attribute a stance the player toggles? CLAUDE.md says stances are not automated.
7. Does Foe-Seeker matter when tired, or did the user mean "chase while tired"? The tracker keeps "Foe-Seeker + tired" as a user ruling; score 3 reflects the effect, not a request to change it.
8. Shield of Thorns: does the reflection apply to damage taken during the 4 s before contact (no)? A melee-only trigger would not lose anything.
9. Winds of Magic: do the 21 abilities consume the Winds pool or only buff regen? If a cast is wasted when the pool is already full, a "pool < X" gate (the WINDS log row) is the refinement.
10. `fast_speed()` for ttc: is it the unit's run speed? With a missing speed the ttc test passes, so the charge window widens to 12-60 m.
11. Are the runes (Rune of Speed, Master Rune of Speed) on the wheel? Rule 12 says a wheel copy is ours; "activating one locks the others" was why the spell bar was dropped.

---

## Summary (5 lines)

1. Charge families are the strongest (most 5s): the trigger fires 4 s before contact; sentence "charges" hides the 12-60 m / 4 s window and every sentence omits "not routing".
2. ushoran_health (19) carries four unhonoured restriction flags: `enemies_in_intercept_range` (Bugman's), `hp_replenish_cap_reached` (5 keys), `morale_is_broken_or_lower` (4, mostly covered by the routing gate), `unit_is_not_tiger_warrior`; and 3 friend-target heals (Mantra, Bathori, Breath of Darkness) are cast only on the caster.
3. Weak fits: Necrotic Phylactery (2, ward on a heal line), Skar's Kraken-Killer, Potion of Charoi (3, resist/invulnerable without a melee gate), Shield of Thorns on the charge arm, Foe-Seeker on tired, Blooood! on any movement, Rock Bottom with no health guard.
4. Wrong or incomplete sentences: melee_or_under_fire (silent "not wavering" on one arm), glorious_death (omits the Slayer-caster arm and 38 m), no_enemy_in_range_within_boost (omits ammo, melee, 1.21), self_recharging (mod bookkeeping, not engine fact), health_aura_self (full aura vs 70%).
5. when_ready is right per the user ruling; Power Stone and Chromatic Tome (recharge -20%) and the miscast-only pair (Snowflake Pendant, Stave of Avelorn) are the ones where "all when ready" is least obviously good.
