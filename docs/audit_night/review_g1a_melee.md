# Review g1a: melee_unwavering rows 1-150, melee_skip_commanders, melee, melee_health75, melee_self_or_ally

Reviewer notes: the evaluator code was read (FOURTH.evaluate_in_melee_self at line 8455 of the mod source, evaluate_melee_skip_commanders at 13758, evaluate_potion_health at 8908, evaluate_melee_self_or_ally at 18071). Durations and recharges come from tools/fact_sheet_open.py. Scores follow the brief. "-" in a cell means nothing to report.

## A. Families

### melee_unwavering
- Current sentence: "When armed, fires when this unit is in melee"
- What the code requires (FOURTH.evaluate_in_melee_self):
  - `unit:is_in_melee()` is true and the unit is not routing (a routing unit is never in melee, so this adds nothing).
  - `is_wavering()` is not exactly true. Wavering blocks the cast; an unreadable or missing morale read FIRES (fail-open).
  - Cast on the unit itself; no target, no range, no safety distance, no standing-still rule, no per-entry fields (no `target_class`, `aura_real` or `range_real` on any of the 299 entries; ground-form keys are cast at the caster's own position).
  - The family starts ARMED (DEFAULT_ON_TRIGGERS).
- Verdict: INCOMPLETE. The sentence leaves out the "not wavering" gate, which is a real condition: a wavering unit in melee does NOT fire. (Compare `melee_low_morale`, the opposite family, which says "in melee and wavering".)
- Proposed sentence: "When armed, fires when this unit is in melee and not wavering (an unreadable morale counts as steady)." (96 characters)

### melee_skip_commanders (Soulfire x2, Arachneruption, Call of Tor, Warp Lightning Rod)
- Current sentence: "When armed, fires when this unit is in melee, unless every enemy it is fighting is a Lord or Hero"
- What the code requires (evaluate_melee_skip_commanders):
  - `is_in_melee()` true, not routing. NO wavering check (a wavering unit in melee still fires).
  - "Fighting" is defined by the engagement set: living enemy units that are themselves in melee and whose edge-to-edge `unit_distance` to the caster is at most 12 m (`FOURTH.ENGAGE_CONTACT_M`). Each is classed commander by the 1,409-key commander set.
  - Fires if at least one member is a non-commander; holds if the set is non-empty and all members are commanders.
  - Empty set: falls back to the caster's `current_target()`; holds if that target is a commander, fires if not.
  - Set unreadable, or empty with no current target: fires on plain in-melee (fail-open).
  - Cast on the unit itself. Family starts ARMED.
- Verdict: INCOMPLETE (close). It omits the 12 m definition of "fighting" and the current-target fallback, but the headline rule is right. User decision 2026-10-18 on Arachneruption: "I find it satisfying right now" (leave as is).
- Proposed sentence: "When armed, fires when this unit is in melee, unless every enemy within 12 m of it is a Lord or Hero (no enemy in contact: its current target decides)." (about 150 characters)

### melee
- Current sentence: "When armed, fires when this unit is in melee"
- What the code requires (evaluate_melee): `is_in_melee()` true and not routing. No morale check at all (a wavering unit fires). Cast on the unit itself. Starts ARMED. Only entry: Hammer of Sigmar (2 keys, aura 35 m, so the buff also reaches allies near the caster).
- Verdict: EXACT. (The routing test is redundant with is_in_melee, so the sentence need not mention it.)
- Proposed sentence: unchanged, "When armed, fires when this unit is in melee."

### melee_health75
- Current sentence: "When armed, fires when this unit is in melee and at or below 75% health"
- What the code requires (evaluate_potion_health): `is_in_melee()` true, not routing, and `FOURTH.health_pct(unit)` is a number at or below 75. An unreadable health read does not fire. No morale check. Cast on itself. Starts ARMED.
- Verdict: EXACT. User rulings: Potion of Toughness is a user-designed trigger (tracker, block 4/5/6 round); Armour of Caledor "In melee + health <= 75%" (round 141).
- Proposed sentence: unchanged, "When armed, fires when this unit is in melee and at or below 75% health."

### melee_self_or_ally
- Current sentence: "When armed, fires when this unit or a friendly unit near it is in melee"
- What the code requires (evaluate_melee_self_or_ally):
  - Caster not routing; if the caster `is_in_melee()` it casts on itself (no morale check, no distance).
  - Otherwise the closest tracked ally that is alive, not the caster, not routing, `is_in_melee()`, and within the entry's 70 m bound (`ally_range_real = 100`, 70% rule) gets the cast, with the fresh controller handles re-fetched.
  - Own melee wins over an ally's; the ally arm needs no wavering check either.
- Verdict: INCOMPLETE (minor). "Near it" hides the 70 m bound and the fact that the caster's own melee takes priority, so the cast lands on the caster, not the ally.
- Proposed sentence: "When armed, fires on this unit when it is in melee, else on the closest friendly unit within 70 m that is in melee."


## B. Abilities

### melee_unwavering (rows 1-150 of the database table, in table order)

| Marker | Ability | Effect (short) | Score | Why (one line) | Better trigger (if score <= 3) | Restriction issue |
|---|---|---|---|---|---|---|
| acid_burps | Acid Burps | Leaves a trail of explosions behind (positive) | 4 | Trail of explosions is laid by a MOVING unit; a unit stuck in melee still blasts the enemies touching it (user ruling "Like Bloodstorm") | - | - |
| aether_sword | Aether Sword | AP dmg: +25%; base dmg: +25%; contact: wh2_dlc12_unit_contact_sundered_armour; Imbues magical a... | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| alchemists_elixir_of_iron_skin | Alchemist's Elixir of Iron Skin | Armour: +90 (self+allies) | 4 | Armour +90 also stops missiles, so some value is before melee; 25 s still covers a fight | - | - |
| alchemists_elixir_of_puissance | Alchemist's Elixir of Puissance | Melee Attack: +40 (self+allies) | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| alchemists_elixir_of_venom | Alchemist's Elixir of Venom | contact: wh2_dlc17_unit_contact_slow_death (self+allies) | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| all_hands_hoay | All Hands Hoay! | AP dmg: +25%; base dmg: +25%; Leadership: +16 (self+allies) | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| all_consuming_hatred | All-Consuming Hatred | Melee Damage Reflection: +40; Melee Defence: -12 (self) | 4 | Reflection +40 pays when hit; Melee Defence -12 is a cost, acceptable in a fight | - | - |
| amulet_of_itzl | Amulet of Itzl | Damage Resistance: +60 (self) | 4 | Damage resistance +60 for 18 s, text says it triggers when the wearer is struck; melee is when that happens | - | - |
| apocalyptic_vision | Apocalyptic Vision | Melee Attack: +24; Leadership: +16 (self+allies) | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| armour_of_gazrakh | Armour of Gazrakh | Damage Resistance: +30 (self); Effect intensity increases as the unit takes damage (positive) | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| armour_of_the_burrows | Armour of the Barrows | AP dmg: -25%; base dmg: -25%; Removes magical attacks (enemies) | 5 | Enemy debuff on enemies near the caster: pays while the fight lasts | - | - |
| arsebelcher | Arsebelcher | Stance: rebirth (self) | 4 | Self-centred blast, user ruling 2026-11-15 "Like Bloodstorm" (cannot hurt our units); in melee is where it hits | - | - |
| aura_of_inertia | Aura of Inertia | Speed: -25%; Leadership: -8; Fatigue: 0.01 (enemies) | 4 | Enemy slow + leadership: pays in the fight; the charge moment would also fit (rule 10 says melee or charge) | charge_or_melee (adds the charge arm) | - |
| aura_of_quetzl | Aura of Quetzl | Armour: +30; Melee Defence: +24 (self+allies) | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| avast_ye | Avast Ye! | AP dmg: +25%; base dmg: +25%; Leadership: +8 (self+allies) | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| axe_of_dargo | Axe of Dargo | Bonus vs. Large: +32; AP dmg: +50% (self) | 4 | AP +50% always useful, Bonus vs Large +32 only when a large enemy is engaged | - | - |
| axe_of_grom | Axe of Grom | AP dmg: +50%; base dmg: +50%; contact: wh_dlc06_unit_contact_sundered_armour (self) | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| axe_of_men | Axe of Men | Causes Terror (positive); Unbreakable (positive) (self) | 4 | Unbreakable 46 s + terror: good over a whole fight; the not-wavering gate means it never fires once morale already slipped | - | - |
| axes_of_kadrin | Axes of Kadrin | Bonus vs. Infantry: +16; AP dmg: +75%; base dmg: +75% (self) | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| azhags_ard_armour | Azhag's 'Ard Armour | Armour: +30; Melee Defence: +24 (self+allies) | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| ballet_of_blows | Ballet of Blows | Melee Attack: +12; AP dmg: +12%; base dmg: +12% (self); Melee Attack: +24; AP dmg: +24%; base d... | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| banner_of_hellfire | Banner of Hellfire | Damage: 5 per hit (max 2 entities) (enemies); Causes damage to combatants (positive) | 4 | 5 damage per hit to 2 entities of enemies in contact (user ruling "in melee", round 144) | - | - |
| barbed_knuckle_boxing | Barbed-Knuckle Boxing | Melee Attack: +24; AP dmg: +25%; base dmg: +25% (self) | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| bastions_defenders | Bastion's Defenders | Melee Defence: +24; Immune to Flanking (positive) (self+allies) | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| battle_of_wills | Battle of Wills | Melee Attack: -24; Leadership: -8; Reload Skill: -40; Must Resist (positive) (enemies) | 4 | 5 s wind-up while engaged; debuff pays in melee | - | - |
| bear_fang_talisman | Bear Fang Talisman | Damage Resistance: +40 (self) | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| beastslaver | Beastslaver | Bonus vs. Large: +16; AP dmg: +25%; base dmg: +25% (self) | 4 | AP +25% generic, Bonus vs Large +16 only against large | - | - |
| black_hammer_of_hashut | Black Hammer of Hashut | AP dmg: +50%; base dmg: +50%; contact: wh2_dlc12_unit_contact_flammable (self) | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| black_lotus | Black Lotus | contact: wh_dlc06_unit_contact_discouraged (self) | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| black_staff | Black Staff | Damage: 33 per hit (max 1 entities); Winds of Magic recharge: -20%; Winds of Magic reserves per... | 2 | Winds of Magic regen ability (damages the bearer 33); nothing to do with a melee fight | when_ready (the winds family, round 150) | Causes damage to self; not modelled as a cost |
| blade_of_bel_korhadris | Blade of Bel-Korhadris | Melee Attack: +24; AP dmg: +25% (self) | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| blades_of_shang_yang | Blades of Shang-Yang | Melee Attack: +24; AP dmg: +30%; base dmg: +30%; contact: wh_dlc06_unit_contact_flammable (self... | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| blight_of_terrors | Blight of Terrors | Leadership: -16 (enemies) | 5 | Enemy debuff on enemies near the caster: pays while the fight lasts | - | - |
| blood_lust | Blood Lust | AP dmg: +25% (self+allies) | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| blood_lust | Blood Lust | AP dmg: +25% (self+allies) | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| blood_omens | Blood Omens | Charge Speed: -25%; Speed: -25%; Revealed (positive) (enemies) | 3 | Charge speed -25% matters when the enemy is approaching; once engaged it is wasted (speed -25% and revealed still help) | charge_or_melee, or an enemy-approaching read (enemy_fast_near_ally style) | - |
| blood_forged_armour | Blood-Forged Armour | Armour: +30 (self); Explosion does not affect friendly troops (positive); Poor against large co... | 4 | Armour +30 for 12 s only, 30 s recharge: cheap, fires each time (the blast text is the same as Bloodstorm) | - | - |
| bloodstorm | Bloodstorm | Damage Resistance: +20 (self); Explosion does not affect friendly troops (positive); Poor again... | 4 | DR +20 for 9 s; short but cheap, 60 s recharge | - | - |
| bloodstorm_blades | Bloodstorm Blades | Bonus vs. Infantry: +16; AP dmg: +75%; base dmg: +75% (self) | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| brass_body | Brass Body | Melee Defence: +24; Damage Resistance: +40 (self) | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| breath_of_hatred | Breath of Hatred | Melee Attack: +24; contact: wh_dlc06_unit_contact_sundered_armour; Imbues ignition: 10 (self+al... | 5 | MA +24 aura at the fight start; ground-form cast at the caster | - | - |
| breath_of_hatred | Breath of Hatred | Melee Attack: +24; contact: wh_dlc06_unit_contact_sundered_armour; Imbues ignition: 10 (self+al... | 5 | Same as the bound twin | - | - |
| burp_of_grom | Burp of Grom | unknown (no stat or phase rows in the game's tables; the game's own delivery columns: vortex/ar... | 4 | Self-centred blast, user ruling 2026-11-15 "Like Bloodstorm" (cannot hurt our units); in melee is where it hits | - | - |
| burp_of_grom | Burp of Grom | unknown (no stat or phase rows in the game's tables; the game's own delivery columns: vortex/ar... | 4 | Self-centred blast, user ruling 2026-11-15 "Like Bloodstorm" (cannot hurt our units); in melee is where it hits | - | - |
| burp_of_grom | Burp of Grom | unknown (no stat or phase rows in the game's tables; the game's own delivery columns: vortex/ar... | 4 | Self-centred blast, user ruling 2026-11-15 "Like Bloodstorm" (cannot hurt our units); in melee is where it hits | - | - |
| call_for_power | Call for Power | Splash Attack Power: +50%; base dmg: +50%; Rampage (positive) (self) | 4 | Rampage + splash +50%: a melee-only boost, but rampage removes control (user accepted, positive tag) | - | - |
| cascading_fire_cloak | Cascading Fire Cloak | AP dmg: +25%; Melee Defence: +24 (self+allies) | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| change_or_die | Change or Die! | Leadership: +16; Damage Resistance: +20 (self+allies) | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| claws_of_mourkain | Claws of Mourkain | AP dmg: +50% (self) | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| cloak_of_mists_and_shadows | Cloak of Mists & Shadows | Physical Resistance: +75; Strider (positive); Imbues magical attacks (self) | 4 | Physical Res +75 for 29 s helps against missiles too, so melee is only part of the payoff; Strider is wasted | - | - |
| coat_in_blood | Coat in Blood | Melee Attack: +24; AP dmg: +50%; base dmg: +50%; Imbues ignition: 10 (self) | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| creature_killer | Creature-Killer | Bonus vs. Large: +16 (self+allies) | 3 | Bonus vs Large +16 and nothing else: wasted against infantry fights | melee_skip_commanders-style engagement test: in melee with a large enemy engaged (engagement set + generated large set) | - |
| crooked_dice | Crooked Dice | Armour: +60 (self); Physical Resistance: +40 (self); Damage Resistance: +40 (self); Grants one ... | 4 | One random of three defensive effects, fine at fight start | - | - |
| curse_of_years | Curse of Years | contact: wh3_dlc29_unit_contact_curse_of_years (self) | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| da_great_un_iz_ere | Da Great 'Un Iz 'Ere! | Melee Attack: +24; base dmg: +30%; Leadership: +8 (self+allies) | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| daemon_flask_of_ashak | Daemon Flask of Ashak | unknown (no stat or phase rows in the game's tables; the game's own delivery columns: vortex/ar... | 4 | Single use, 5 s blast (user ruling "Like Bloodstorm") | - | invalid usage flying_currently (and climbing, manning_equipment, on_a_platform) not gated: add is_currently_flying() ~= true |
| daemonblade | Daemonblade | AP dmg: +25%; base dmg: +25%; contact: wh_dlc06_unit_contact_discouraged (self) | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| daemonic_strength | Daemonic Strength | AP dmg: +50%; base dmg: +50% (self) | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| daemonshield | Daemonshield | Invulnerable (positive) (self); Unit is invulnerable to damage (does not apply to summoned unit... | 3 | Invulnerable 13 s is best spent when damage is actually flowing, not at the fight start of a healthy unit | melee_health75 (a unit that is already losing) | - |
| dagger_of_malice | Dagger of Malice | Melee Attack: +40; base dmg: +100%; contact: wh_main_unit_contact_poison (self) | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| dark_fortune | Dark Fortune | Damage Resistance: +20 (self) | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| dark_mace | Dark Mace | Armour: -30; Fatigue: 0.01 (enemies) | 5 | Enemy debuff on enemies near the caster: pays while the fight lasts | - | - |
| dark_protection | Dark Protection | Melee Defence: +24; Damage Resistance: +20 (self) | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| dark_venom | Dark Venom | base dmg: +90% (self) | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| darkwalker | Darkwalker | Physical Resistance: +40; Strider (positive) (self) | 4 | Physical Res +40 good, Strider wasted | - | - |
| death_frenzy | Death Frenzy | Melee Attack: +24; AP dmg: +30%; base dmg: +30%; Immune to Psychology (positive) (self+allies) | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| deathbringer | Deathbringer | AP dmg: +50%; base dmg: +50% (self) | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| deathbringer | Deathbringer | AP dmg: +100%; base dmg: +100% (self) | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| strike_of_nehekhara | Desertstrike | Melee Attack: +40; base dmg: +60%; Causes Terror (positive) (self) | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| dolorous_blade | Dolorous Blade | Melee Attack: +24; AP dmg: +50% (self) | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| doom_glaive | Doom Glaive | AP dmg: +75%; base dmg: +75%; Executioner (positive) (self) | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| dragon_spear | Dragon Spear | AP dmg: +100 (self+allies) | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| dragonhorn | Dragonhorn | Melee Attack: +24; Causes Fear (positive) (self+allies) | 4 | MA +24 + fear, 6 s wind-up, 3 uses: fine, but a use per fight is spent (3 uses) | - | - |
| dreaded_duelist | Dreaded Duelist | Melee Attack: +24; Melee Defence: +24 (self) | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| dwarf_gouger | Dwarf Gouger | Melee Attack: +24; AP dmg: +50%; base dmg: +50% (self) | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| earthing_rod | Earthing Rod | Miscast Chance: -100% (self) | 2 | Removes miscast chance: pays when the bearer casts a spell, unrelated to being in melee; single use | no feasible read of a spell cast; when_ready if the user wants it spent | - |
| elixir_of_damnation | Elixir of Damnation | contact: wh3_dlc27_unit_contact_elixir_of_damnation (self) | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| elixir_of_might | Elixir of Might | Melee Attack: +24; base dmg: +60% (self+allies) | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| empowering_shrooms | Empowering Shrooms | Melee Attack: +24; Leadership: +16; Rampage (negative) (to allies in range) | 3 | MA +24 and morale to SQUIG allies only (invalid target unit_is_not_squig); fires whether or not a squig is near | melee with a squig ally within 35 m (needs a generated squig set) | Target flag unit_is_not_squig: no squig in range means no effect |
| enhanced_skavenbrew | Enhanced Skavenbrew | Armour: -40; Mass: +25%; Melee Attack: +50; base dmg: +50%; Causes Terror (positive) (self+alli... | 4 | MA +50, base +50% for 60 s, Armour -40 is the cost; a long buff suits a fight | - | - |
| enrage | Enrage | Damage Resistance: +40 (self) | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| entice | Entice | Melee Defence: +24; contact: wh3_dlc20_contact_effect_euphoria (self) | 4 | Melee Defence +24 + euphoria | - | invalid usage health_below_50%: the game refuses below 50% health; add health >= 50 (else the cast is refused each poll) |
| eternal_vigour | Eternal Vigour | Melee Defence: +24; Physical Resistance: +20 (to allies in range) | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| everyone_has_their_price | Everyone Has Their Price | Melee Attack: -24; Leadership: -8; Rampage (positive) (enemies) | 3 | Debuffs the enemy (MA -24, ld -8) and tags Rampage as positive: unclear whether rampage on enemies helps us | - | - |
| evisceration | Evisceration | Stance: rebirth; Cannot move (self); Good against armour (positive); Huge, stationary area of e... | 4 | Self-centred blast, user ruling 2026-11-15 "Like Bloodstorm" (cannot hurt our units); in melee is where it hits; cannot move 4 s | - | - |
| eye_gouger | Eye Gouger | Melee Attack: +24; AP dmg: +50%; base dmg: +50%; contact: wh_dlc06_unit_contact_blinded (self) | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| eye_jabber | Eye Jabber | AP dmg: +25%; base dmg: +25%; contact: wh_dlc06_unit_contact_blinded (self) | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| eye_of_the_storm | Eye of the Storm | Melee Attack: +24; AP dmg: +50%; base dmg: +50% (self) | 5 | MA +24, AP/base x1.5 for 29 s | - | invalid usage ground_unit and unit_is_not_large (only a large non-ground unit may use it): not gated, casts by smaller or ground units are refused; add large set and is_currently_flying() == true |
| faiths_bastion | Faith's Bastion | Damage Resistance: +20 (self) | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| fangsword_of_eltharion | Fangsword of Eltharion | AP dmg: +25%; base dmg: +25%; Physical Resistance: +40; Imbues magical attacks (self) | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| favoured_by_the_matriarch | Favoured by the Matriarch | Melee Attack: +24; Leadership: +8 (self+allies) | 4 | MA +24, ld +8 | - | invalid usage health_below_25%: refused under 25% health; add health >= 25 |
| fearsome_roar | Fearsome Roar | Leadership: -8; Immune to Psychology (negative) (enemies) | 5 | Enemy debuff on enemies near the caster: pays while the fight lasts | - | - |
| feaster_of_souls | Feaster of Souls | Damage: 18 per hit (max 25 entities) (enemies); Converts damage dealt into health in targeting ... | 4 | Damage 18/hit to 25 enemies in 15 m with life steal (user ruling "Like Bloodstorm") | - | invalid usage flying_currently not gated: add is_currently_flying() ~= true |
| feint_and_reposte | Feint and Reposte | Melee Attack: +24; Melee Defence: +24; Physical Resistance: +20 (self) | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| ferocious_winters_chill | Ferocious Winter’s Chill | Melee Attack: -24; AP dmg: -30%; base dmg: -30%; Melee Defence: -24 (enemies) | 5 | Enemy debuff on enemies near the caster: pays while the fight lasts | - | - |
| fight_or_die | Fight or Die! | Melee Attack: +24; Leadership: +16 (self+allies) | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| filth_mace | Filth Mace | AP dmg: +25%; base dmg: +25%; Causes Terror (positive); contact: wh3_dlc20_unit_contact_corrosi... | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| fistful_of_laurels | Fistful of Laurels | Melee Attack: +40; Leadership: +16 (self+allies) | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| flame_incarnate | Flame Incarnate | Melee Damage Reflection: +14 (self) | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| flesh_to_stone | Flesh to Stone | Physical Resistance: +60 (self+allies) | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| fluid_injection | Fluid Injection | Melee Attack: +24; AP dmg: +25%; base dmg: +25%; Rampage (positive) (self) | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| focus_instincts | Focus Instincts | Rampage (negative) (self+allies) | 2 | Only removes Rampage from lizard allies in 35 m; no read for a rampaging unit, and melee is unrelated | none feasible (rampage unreadable, CLAUDE.md s5); when_ready if wanted | Target flag unit_is_not_a_lizard_unit: only lizards benefit |
| forbidden_rod | Forbidden Rod | Damage: 33 per hit (max 1 entities); Winds of Magic recharge: +60%; Winds of Magic reserves per... | 2 | Winds regen ability (damages the bearer 33): not a melee effect | when_ready (the winds family) | Causes damage to self |
| fury_of_ursun | Fury of Ursun | AP dmg: +25%; base dmg: +25%; Causes Terror (positive); Rampage (positive) (self) | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| fury_of_the_land | Fury of the Land | Causes Fear (positive); Strider (positive); Imbues magical attacks (to allies in range) | 3 | Fear + magical attacks help in a fight but Strider (the headline) is useless in melee | charge_or_melee | - |
| gaze_of_khaine | Gaze of Khaine | Melee Attack: +24; AP dmg: +25%; base dmg: +25%; Leadership: +8; Rampage (positive) (self+allie... | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| gaze_of_khorne | Gaze of Khorne | Cannot move (self); Causes moderate magical damage (positive); Causes severe disruption to enem... | 4 | Self-centred blast, user ruling 2026-11-15 "Like Bloodstorm" (cannot hurt our units); in melee is where it hits; cannot move 2 s | - | - |
| ghal_maraz | Ghal Maraz | Bonus vs. Large: +16; AP dmg: +50% (self) | 4 | AP +50% always useful, Bonus vs Large +16 only against large | - | - |
| giant_leap | Giant Leap | Stance: rebirth; Cannot move (self); Causes moderate magical damage (positive); Causes severe d... | 4 | Self-centred blast, user ruling 2026-11-15 "Like Bloodstorm" (cannot hurt our units); in melee is where it hits; cannot move 5 s | - | - |
| gitsnik | Gitsnik | Melee Attack: +24; AP dmg: +50%; base dmg: +50% (self) | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| gotrek_doom | Gotrek's Doom | Melee Defence: +40; Damage Resistance: +40 (self) | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| great_gutgouger | Great Gutgouger | Melee Attack: +24; AP dmg: +50%; base dmg: +50%; Causes Terror (positive); contact: wh2_dlc11_u... | 5 | MA +24, AP/base +50%, terror, monstrous impact | - | - |
| hagtree_fetish | Hagtree Fetish | Miscast Chance: -75% (self) | 2 | Same as Earthing Rod: miscast -75% pays only when casting | none feasible; when_ready if wanted | - |
| halo_of_maidenly_wrath | Halo of Maidenly Wrath | unknown (no stat or phase rows in the game's tables; the game's own delivery columns: vortex/ar... | 4 | Self-centred blast, user ruling 2026-11-15 "Like Bloodstorm" (cannot hurt our units); in melee is where it hits | - | - |
| hammer_axe_of_skoll | Hammer-Axe of Skoll | Melee Attack: +24; AP dmg: +75%; base dmg: +75% (self) | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| hellfire_sword | Hellfire Sword | AP dmg: +50%; base dmg: +50%; Imbues ignition: 10 (self) | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| hellish_vigour_upgraded | Hellish Vigour Upgraded | Melee Damage Reflection: +20; Fatigue: -0.02 (to allies in range) | 4 | Reflection +20 and fatigue recovery for allies in 35 m, 3 s wind-up | - | - |
| helm_of_discord | Helm of Discord | Melee Attack: -24; Melee Defence: -24 (enemies) | 5 | Enemy debuff on enemies near the caster: pays while the fight lasts | - | - |
| helm_of_many_eyes | Helm of Many Eyes | Melee Defence: +54 (self) | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| heroic_killing_blow_2 | Heroic Killing Blow | AP dmg: +100%; base dmg: +100% (self); Greater effect on melee damage (magic) | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| heroic_killing_blow_dlc07 | Heroic Killing Blow | AP dmg: +50%; base dmg: +50% (self) | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| heroic_killing_blow_main | Heroic Killing Blow | AP dmg: +50%; base dmg: +50% (self) | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| horn_of_the_wild_hunt | Horn of the Wild Hunt | Charge Bonus: +60% (self+allies) | 1 | Charge Bonus +60% pays on the charge; once locked in melee it is nearly spent (tracker 2026-10: charge-only) | charge_only (or charge) | - |
| howl_of_the_great_beast | Howl of the Great Beast | Speed: -25%; Leadership: -8 (enemies) | 4 | Slow + leadership debuff, 1 s wind-up; rule 10 allows melee or charge | charge_or_melee (adds the charge arm) | - |
| hurricane_of_death | Hurricane of Death | Stance: rebirth; Cannot move (self); Good against armour (positive); Huge, stationary area of e... | 4 | Self-centred blast, user ruling 2026-11-15 "Like Bloodstorm" (cannot hurt our units); in melee is where it hits; cannot move 6 s | - | - |
| hydra_blade | Hydra Blade | AP dmg: +50%; base dmg: +50% (self) | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| spell_slaanesh_hysterical_frenzy_bound | Hysterical Frenzy | Melee Attack: +40; AP dmg: +25%; base dmg: +25% (self+allies) | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| inevitable_horror | Inevitable Horror | Leadership: -8; Fatigue: 0.01 (enemies) | 5 | Enemy debuff on enemies near the caster: pays while the fight lasts | - | - |
| karaghul | Karaghul | Bonus vs. Infantry: +32; Melee Attack: +40; Imbues ignition: 10 (self) | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| killing_blow_1 | Killing Blow | AP dmg: +50%; base dmg: +50% (self) | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| killing_blow | Killing Blow | AP dmg: +25%; base dmg: +25% (self) | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| legbiter | Legbiter | Melee Attack: +24; AP dmg: +25%; base dmg: +25%; contact: wh3_dlc29_contact_phase_legbiter (sel... | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| liarsbane | Liarsbane | Melee Attack: +40; Melee Defence: +24 (self) | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| locus_of_abjuration | Locus of Abjuration | Spell Resistance: +65 (self+allies) | 3 | Spell Resistance +65 pays when enemy spells land, not specifically in melee | none feasible (incoming spell unreadable); melee is a loose proxy | - |
| locus_of_beguilement | Locus of Beguilement | Melee Defence: -24; Leadership: -8 (enemies) | 5 | Enemy debuff on enemies near the caster: pays while the fight lasts | - | - |
| locus_of_grace | Locus of Grace | Melee Defence: +24; Physical Resistance: +22 (self+allies) | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| locus_of_virulence | Locus of Virulence | Melee Attack: +24; AP dmg: +25%; base dmg: +25% (self+allies) | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| locus_of_wrath | Locus of Wrath | Melee Attack: +40 (self+allies) | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| lord_of_grand_cathay | Lord of Grand Cathay | Melee Defence: +40; Physical Resistance: +20 (self+allies) | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| lucky_banner | Lucky Banner | Melee Attack: +24; Damage Resistance: +40 (self) | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| mace_of_ulumak | Mace of Ulumak | Melee Attack: +40; AP dmg: +50%; base dmg: +50%; contact: wh2_dlc17_unit_contact_dazed (self) | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| mananns_luck | Manann's Luck | Melee Defence: +24; Damage Resistance: +20 (self) | 5 | Melee stat / damage buff lasting 20-45 s: pays from the first blows of the fight | - | - |
| offense_prayer | Mantra of Righteousness | Melee Attack: +24; AP dmg: +25%; base dmg: +25%; contact: wh2_dlc12_unit_contact_sundered_armou... | 5 | MA +24, AP +25%, sundering contact | - | target flag unit_is_not_tiger_warrior: allies that are tiger warriors get nothing (the caster still does) |
| manus_of_ursun | Manus of Ursun | base dmg: +12%; Causes Terror (positive); Rampage (positive) (self+allies) | 4 | Base dmg +12% weak; terror + rampage | - | - |
| master_rune_of_breaking | Master Rune of Breaking | AP dmg: +25%; base dmg: +25%; contact: wh_dlc06_unit_contact_sundered_armour (self+allies); Ext... | 4 | AP +25% + sundered armour for 55 s, 3 s wind-up, 180 s recharge; rune of the spell bar family (CLAUDE.md rule 12: only the wheel copy is ours) | - | - |
| master_rune_of_negation | Master Rune of Negation | Damage Resistance: +40 (self+allies); Extended effect duration (magic) | 4 | DR +40 for 40 s; same rune note as Breaking | - | - |
| master_rune_of_oath_and_steel | Master Rune of Oath & Steel | Armour: +60 (self+allies); Greater effect on armour (magic) | 4 | Armour +60 for 44 s, ground-form cast; same rune note | - | - |
| master_of_the_black_arts | Master of the Black Arts | Spell Mastery: +60% (self) | 2 | Spell Mastery +60% pays only when the bearer casts; unrelated to melee | none feasible; when_ready if wanted | - |
| maw_shard | Maw Shard | Spell Mastery: +60% (self+allies); Causes damage to self (negative) | 2 | Spell Mastery +60% plus self damage; unrelated to melee | none feasible; when_ready if wanted | Causes damage to self; not modelled as a cost |
| miasma_of_despair | Miasma of Despair | Speed: -25%; Leadership: -8; Fatigue: 0.01 (enemies) | 5 | Enemy debuff on enemies near the caster: pays while the fight lasts | - | - |

### melee_skip_commanders
| Marker | Ability | Effect (short) | Score | Why (one line) | Better trigger (if score <= 3) | Restriction issue |
|---|---|---|---|---|---|---|
| soulfire | Soulfire (2 keys) | Self-centred fire burst, 7 s, 3 uses implied; effect not in tables | 4 | Burst on the engaged enemies; skipping Lord/Hero-only fights is the user's rule (2026-10-18 "satisfying right now") | - | invalid usage `climbing` (siege flag, not modelled) |
| arachneruption | Arachneruption | Bombardment around the caster, 2 s, 3 uses | 4 | Same rule, user decision 2026-10-18: leave as is | - | - |
| call_of_tor | Call of Tor | Divine lightning barrage on self-centred area, 7 s | 4 | User ruling 2026-10-18 "same trigger as a Soulfire" | - | - |
| warp_lightning_rod | Warp Lightning Rod | Bombardment on the caster's spot (campaign-granted mutation key) | 4 | User ruling 2026-10-18 "treat it the same as Soulfire" | - | invalid usage `climbing` |

### melee
| Marker | Ability | Effect (short) | Score | Why (one line) | Better trigger (if score <= 3) | Restriction issue |
|---|---|---|---|---|---|---|
| hammer_of_sigmar | Hammer of Sigmar (2 keys) | Melee Attack +24 to self and allies within 35 m, 25 s, 60 s recharge | 5 | A melee-only stat on a pure in-melee trigger, 25 s covers the fight | - | - |

### melee_health75
| Marker | Ability | Effect (short) | Score | Why (one line) | Better trigger (if score <= 3) | Restriction issue |
|---|---|---|---|---|---|---|
| potion_of_toughness | Potion of Toughness | Armour +30, Melee Defence +24, heal 0.8%/s, 21 s, 1 use | 5 | User-designed: a one-shot heal-and-armour used once the unit is hurt in melee | - | usage `morale_is_broken_or_lower` is honoured in effect (routing units never fire); a unit that is broken but not yet routing is not checked |
| armour_of_caledor | Armour of Caledor | Heals 1.6%/s for 20 s, fatigue recovery, CANNOT MOVE, 3 uses, 180 s | 4 | User ruling "In melee + health <= 75%"; the 20 s immobility is the cost, accepted in a fight | - | - |

### melee_self_or_ally
| Marker | Ability | Effect (short) | Score | Why (one line) | Better trigger (if score <= 3) | Restriction issue |
|---|---|---|---|---|---|---|
| terrorgheist_skull | Terrorgheist Skull | Removes rest between uses (own ability recharge -60 s) plus blinding contact, to the target and friends, 44 s | 3 | User ruling 2026-11-13 "Self or ally in melee". But the main effect (recharge reduction) pays when abilities are recharging, not because of melee | self_recharging family (caster has >= 1 ability locked), as Spell-Wrought Sceptre uses recharging_in_reach; keep melee as a second arm | - |

## C. Game-mechanics questions
- Does "Everyone Has Their Price" (Rampage tagged positive on enemies, MA -24, ld -8) really make enemy rampage good for us, or is the tag only a UI colour?
- Do the "blast cannot hurt our units" claims (user ruling "Like Bloodstorm") hold for Burp of Grom x3, Banner of Hellfire, Feaster of Souls, Daemon Flask, Hurricane of Death, Evisceration, Giant Leap, Gaze of Khorne, Acid Burps and Halo of Maidenly Wrath? The game data lists no friendly-fire flag for them, only Bloodstorm and Blood-Forged Armour say "Explosion does not affect friendly troops".
- Do the bombardment keys on melee_skip_commanders (Call of Tor lightning, Arachneruption, Warp Lightning Rod) damage our own troops locked in the same melee? No friendly-fire check exists in that family; the later melee_clear family (round 159) was created exactly for such blasts.
- Eye of the Storm invalid usage flags `ground_unit` and `unit_is_not_large`: assumed to mean "refused while the unit is on the ground form or is not large" (Storm Dragon form). A field cast on a normal ground Lord would confirm it is refused.
- Does the Wavering gate (blocks a wavering unit) cost anything for Unbreakable / morale buffs (Axe of Men, Fight or Die, Focus Instincts)? A wavering unit is the one that most needs them; assumed the user wants the not-wavering gate for all 299.
- Horn of the Wild Hunt: does Charge Bonus +60% still help while the unit is locked in its first seconds of melee? Assumed the bonus only counts for a short window after impact.
- Daemonshield (Invulnerable 13 s) and Amulet of Itzl (DR +60, "if the wearer is struck"): assumed these are worth most when the unit is already taking damage, not at the first contact.
- Earthing Rod, Hagtree Fetish, Master of the Black Arts, Maw Shard: assumed the benefit is realised only when the bearer casts a spell during the window; no battle read exists for a spell cast, so melee is a weak stand-in.
- Black Staff and Forbidden Rod: assumed the winds regeneration gain is independent of combat and the 33 damage to the bearer is a real cost.
- Terrorgheist Skull: "Own ability recharge -60 s" assumed to cut the recharge of the target's abilities by 60 s while the 44 s window runs.

## Summary
1. The melee_unwavering tooltip omits its "not wavering" gate (wavering blocks the cast, unreadable morale fires); proposed sentence given. melee_skip_commanders and melee_self_or_ally also hide a 12 m contact definition and the 70 m ally bound.
2. Worst fits in rows 1-150: Horn of the Wild Hunt (charge bonus, score 1, better charge_only), the Winds/spell-power items (Black Staff, Forbidden Rod, Earthing Rod, Hagtree Fetish, Master of the Black Arts, Maw Shard, Focus Instincts, score 2: melee is unrelated to their payoff).
3. Score 3 cases: Creature-Killer (large-only bonus), Daemonshield (spend when hurt), Blood Omens (charge speed), Locus of Abjuration (spell resistance), Fury of the Land (Strider), Empowering Shrooms (squig-only), Everyone Has Their Price (unclear), Terrorgheist Skull (user ruling; recharge-based trigger would pay better).
4. Unhonoured game restrictions that cause refused casts: Eye of the Storm (ground_unit, unit_is_not_large), Daemon Flask and Feaster of Souls (flying_currently), Entice (health_below_50%), Favoured by the Matriarch (health_below_25%); Mantra of Righteousness, Focus Instincts and Empowering Shrooms have target-class flags only.
5. The other ~120 rows are melee-stat, AP/damage, defence and enemy-debuff abilities that pay off from the first blows of a fight and score 4-5; the stale tracker text for the Winds items still says "ready" while the code rides melee_unwavering.
