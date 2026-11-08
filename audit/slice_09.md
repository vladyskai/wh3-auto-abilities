# Slice 9 — ABILITIES entries 465–522 (source order)

Audit of `zz_test_deadly_onslaught.lua` (ABILITIES table, entries 465–522 of 579) against the game's own ability data.

**Counts: entries audited 58 · FLAGGED 32 · CLEAN 26.**

Method: game-side facts are read from the extracted db tables (`%LOCALAPPDATA%\Temp\wh3\` + `uieff\`): `unit_special_abilities` (target_friends/enemies/ground, affect_self, range, uses, wind-up, ai_usage), `special_ability_to_special_ability_phase_junctions` (target_self/friends/enemies), the `special_ability_phases` rows, stat/attribute effect tables and the loc files. Mod-side: every entry in this slice rides the shared `melee_unwavering` trigger ("when in melee and morale not wavering / fail-open: cast on self") and the cast is issued as `uc:perform_special_ability(key, unit)` — the unit itself. None of these 58 entries uses an ally picker or the ground-cast path.

## FLAGGED

### 465 — The Enfeebling Foe (`enfeebling_foe`)
- **Keys:** `wh3_dlc23_spell_bound_enfeebling_foe`, `wh3_dlc27_spell_bound_enfeebling_foe`, `wh3_main_spell_bound_enfeebling_foe`, `wh3_twa08_spell_bound_enfeebling_foe_keeper_of_secrets_ror`
- **Current logic:** `melee_unwavering` — in melee (not wavering): cast on self.
- **Game declares:** a bound Shadow hex aimed at ONE **enemy unit** (target_enemies = true, 200 m intercept, wind-up 1 s); 17 s: −24 Melee Attack, −24 Melee Defence.
- **Why it fails:** cast target — the mod passes the caster itself as the target, but the ability must be aimed at the enemy it is meant to enfeeble; a debuff cast on self is a wrong target.
- **Feasibility:** not implementable as-is — enemy-targeted casts cannot be aimed by the mod (no readable enemy unit, and no proven current-target plumbing). The trigger is achievable; the target is not.

### 468 — The Hammer of Karak Drazh (`the_hammer_of_karak_drazh`)
- **Key:** `wh_main_weapon_abilities_the_hammer_of_karak_drazh`
- **Current logic:** `melee_unwavering` — in melee (not wavering): cast on self.
- **Game declares:** a weapon hex aimed at ONE **enemy unit** (target_enemies = true); 50 s: −40 Melee Attack, ×0.7 Base Weapon Damage.
- **Why it fails:** cast target — self-cast leaves the enemy untouched; the debuff belongs on the enemy unit being fought.
- **Feasibility:** not implementable as-is — the mod cannot aim at an enemy (no enemy reads / no current-target plumbing).

### 474 — The Trickster's Pendant (`the_tricksters_pendant`)
- **Key:** `wh2_main_item_abilities_the_tricksters_pendant`
- **Current logic:** `melee_unwavering` — in melee (not wavering): cast on self.
- **Game declares:** an area-of-hexes cast on **enemy ground** under the target (target_enemies = true, target_ground = true, 100 m intercept, 35 m area); 16 s: enemy Miscast Chance ×2.
- **Why it fails:** cast target — the mod self-casts, so the hex lands at the caster, not under the enemy; a misplaced cast cannot hit the enemy spellcasters it punishes.
- **Feasibility:** not implementable as-is — the mod has no readable enemy to pick and no target-ground point under an enemy; only a key in the ground-key list with a readable position is cast ground-wise, and that path only uses the caster's own feet.

### 475 — The Vial of Hashut (`the_vial_of_hashut`)
- **Key:** `wh3_dlc23_item_abilities_the_vial_of_hashut`
- **Current logic:** `melee_unwavering` — in melee (not wavering): cast on self.
- **Game declares:** a hex aimed at ONE **enemy unit** (target_enemies = true, only_affect_target = true); 60 s: −60 Armour, −20 Weakness to Fire.
- **Why it fails:** cast target — the vial's debuff is designed to be applied to the enemy; self-cast addresses the caster.
- **Feasibility:** not implementable as-is — enemy-targeted casts cannot be aimed by the mod.

### 476 — The Vortex Shard (`the_vortex_shard`)
- **Key:** `wh2_main_item_abilities_the_vortex_shard`
- **Current logic:** `melee_unwavering` — in melee (not wavering): cast on self.
- **Game declares:** a hex of the winds aimed at ONE **enemy unit** (target_enemies = true); 31 s (becalms the enemy's magic).
- **Why it fails:** cast target — the mod self-casts an ability that exists to be thrown at the enemy.
- **Feasibility:** not implementable as-is — no enemy targeting available.

### 479 — The Withering (`the_withering`)
- **Keys:** `wh3_dlc23_spell_bound_the_withering`, `wh3_twa08_spell_bound_the_withering`
- **Current logic:** `melee_unwavering` — in melee (not wavering): cast on self.
- **Game declares:** a bound Shadow hex aimed at ONE **enemy unit** (target_enemies = true); 40 s: −30 Armour, −8 Leadership.
- **Why it fails:** cast target — a debuff cast on self; the enemy never receives it.
- **Feasibility:** not implementable as-is — enemy-targeted casts cannot be aimed by the mod.

### 480 — They Needs Stabbin' (`they_needs_stabbin`)
- **Key:** `wh2_dlc15_character_abilities_they_needs_stabbin`
- **Current logic:** `melee_unwavering` — in melee (not wavering): cast on self.
- **Game declares:** a hex aimed at ONE **enemy unit** (target_enemies = true; the game even restricts the victim to commander-class units); 29 s: −30 Armour, −24 Melee Defence.
- **Why it fails:** cast target — the gobbos are told to stab a chosen enemy; the mod aims the cast at its own caster.
- **Feasibility:** not implementable as-is — the mod cannot pick or aim at an enemy unit.

### 482 — Thunderburner (`thunderburner`)
- **Key:** `wh3_dlc25_unit_abilities_thunderburner`
- **Current logic:** `melee_unwavering` — in melee (not wavering): cast on self.
- **Game declares:** a self toggle for the flying Thunderbarge (cd 30 s): Speed ×2.5, Turn Speed ×0.3, with continuous self-damage (30 damage per hp tick) — a straight-line steam dash whose game text says it "soars forward at speed" and whose AI family is `hex_speed_under_fire` (a reaction to being under fire, not melee).
- **Why it fails:** trigger fit — the ability's whole value is a long, pre-aimed dash across the field; firing it once the ship is already locked in melee spends the dash in the one state where its direction cannot be planned, while the self-damage cost still starts ticking.
- **Feasibility:** trigger-choice problem, not an engine limit — a different trigger moment (e.g. a movement/under-fire arm) uses reads the mod already has; no enemy targeting is involved.

### 483 — Thunderburner Upgraded (`thunderburner_upgraded`)
- **Key:** `wh3_dlc25_unit_abilities_thunderburner_upgraded`
- **Current logic:** `melee_unwavering` — in melee (not wavering): cast on self.
- **Game declares:** same self toggle as 482, stronger: Speed ×3, Turn Speed ×0.3, continuous self-damage (10 per tick), `hex_speed_under_fire`.
- **Why it fails:** trigger fit — same mismatch as Thunderburner: a planned dash fired from a melee scrum, where the movement cannot be directed and the damage cost applies anyway.
- **Feasibility:** trigger-choice problem, not an engine limit.

### 484 — Titan Headsman (`titan_headsman`)
- **Key:** `wh3_dlc25_hero_abilities_titan_headsman`
- **Current logic:** `melee_unwavering` — in melee (not wavering): cast on self.
- **Game declares:** a hex aimed at ONE **enemy unit** (target_enemies = true); 29 s: Speed ×0.55, −24 Melee Defence.
- **Why it fails:** cast target — the crippling debuff must land on the enemy being finished off; the mod self-casts it.
- **Feasibility:** not implementable as-is — enemy-targeted casts cannot be aimed by the mod.

### 485 — Torment Blade (`torment_blade`)
- **Key:** `wh3_main_weapon_abilities_torment_blade`
- **Current logic:** `melee_unwavering` — in melee (not wavering): cast on self.
- **Game declares:** a weapon hex aimed at ONE **enemy unit** (target_enemies = true); 18 s: −24 Melee Attack, ×0.75 Base and AP Weapon Damage.
- **Why it fails:** cast target — the paralysing venom is for the victim, not the wielder; self-cast is a wrong target.
- **Feasibility:** not implementable as-is — no enemy aiming available.

### 486 — Trickster's Shard (`tricksters_shard`)
- **Key:** `wh_main_item_abilities_tricksters_shard`
- **Current logic:** `melee_unwavering` — in melee (not wavering): cast on self.
- **Game declares:** an area-of-hexes cast on **enemy ground** (target_enemies = true, target_ground = true, 500 m intercept, 35 m area); 16 s: enemy Miscast Chance ×2.
- **Why it fails:** cast target — the shard's curse must be placed among the enemy; the mod's self-cast puts (at best) the area on the caster.
- **Feasibility:** not implementable as-is — no readable enemy and no enemy-ground placement path in the mod.

### 487 — Trophy Heads (`trophy_heads`)
- **Keys:** `wh2_main_lord_abilities_trophy_heads`, `wh3_main_daemon_wings_abilities_trophy_heads`
- **Current logic:** `melee_unwavering` — in melee (not wavering): cast on self.
- **Game declares:** hexes aimed at ONE **enemy unit** (target_enemies = true; commander-class targets only); 36 s: −24 Melee Attack / −40 Melee Defence (base), −30 / −30 (daemon wings).
- **Why it fails:** cast target — the terror debuff belongs on the enemy; the mod aims it at the caster.
- **Feasibility:** not implementable as-is — enemy-targeted casts cannot be aimed.

### 488 — Twilight Horn I (`twilight_horn_i`)
- **Key:** `wh2_dlc16_item_abilities_twilight_horn_i`
- **Current logic:** `melee_unwavering` — in melee (not wavering): cast on self (self is a legal target for this item).
- **Game declares:** an item augment on self or one friendly unit; 33 s: Charge Speed ×1.25, Speed ×1.25, Charge Bonus ×1.2 — a pure charge/movement effect.
- **Why it fails:** trigger fit — the buff is spent on the next charge, but the trigger fires after contact, when the charge bonus can no longer apply; the project itself skipped the stronger twin (Twilight Horn II) as "unsuitable: movement" for exactly this reason.
- **Feasibility:** trigger-choice problem — the mod already ships a charge-window trigger for other charge-family abilities, so involving a charge needs no new reads.

### 495 — Verminous Fury (`verminous_fury`)
- **Key:** `wh3_dlc29_lord_abilities_verminous_fury`
- **Current logic:** `melee_unwavering` — in melee (not wavering): cast on self.
- **Game declares:** an augment cast on a **friendly unit — the caster itself is not a valid target** (target_friends = true, target_self = false, affect_self = false); 60 s: Rampage, Unbreakable, Unyielding Assault — a buff meant for a follower, not the Warbringer.
- **Why it fails:** cast target — an ally-targeted effect cast on self; the engine offers self as no target for this ability, so the buff cannot land on the caster as intended here.
- **Feasibility:** fixable in principle but not built — the mod already reads friendly units and passes an ally target for other abilities (the ally-picker pattern); this entry has no picker and self-casts.

### 496 — Virulent Contagion (`virulent_contagion`)
- **Key:** `wh3_main_lord_abilities_virulent_contagion`
- **Current logic:** `melee_unwavering` — in melee (not wavering): cast on self.
- **Game declares:** a chain hex aimed at ONE **enemy unit** (spreads to up to 5 enemies); 30 s: −40 Melee Defence.
- **Why it fails:** cast target — the plague is for the enemy formation; self-cast means the chain never starts.
- **Feasibility:** not implementable as-is — enemy-targeted casts cannot be aimed by the mod.

### 497 — Virulent Contagion Upgraded (`virulent_contagion_upgraded`)
- **Key:** `wh3_main_lord_abilities_virulent_contagion_upgraded`
- **Current logic:** `melee_unwavering` — in melee (not wavering): cast on self.
- **Game declares:** chain hex aimed at ONE **enemy unit** (up to 5 affected); 30 s: −50 Melee Defence.
- **Why it fails:** cast target — same mismatch as base Virulent Contagion: an enemy chain hex cast on the caster.
- **Feasibility:** not implementable as-is — no enemy aiming available.

### 498 — Visions of Madness (`visions_of_madness`)
- **Key:** `wh3_dlc27_qb_unit_abilities_visions_of_madness`
- **Current logic:** `melee_unwavering` — in melee (not wavering): cast on self.
- **Game declares:** a hex aimed at ONE **enemy unit** (up to 5 affected, 30 m intercept); 10 s: −16 Leadership, Rampage.
- **Why it fails:** cast target — the madness is inflicted on the enemy; the mod aims the cast at itself.
- **Feasibility:** not implementable as-is — enemy-targeted casts cannot be aimed.

### 499 — Void Pendulum (`void_pendulum`)
- **Key:** `wh3_main_item_abilities_void_pendulum`
- **Current logic:** `melee_unwavering` — in melee (not wavering): cast on self.
- **Game declares:** a hex of the winds aimed at ONE **enemy unit** (casting units only — invalid target flag `hasnt_casting_ability`); 25 s: shuts down the enemy spellcaster.
- **Why it fails:** cast target — a targeted spellcaster hex cast on the caster; the caster is not the intended victim (and may not even be a legal one).
- **Feasibility:** not implementable as-is — no enemy targeting/selection path exists in the mod.

### 500 — Vorozheja's Foresight (`vorozhejas_foresight`)
- **Key:** `wh3_dlc24_hero_abilities_vorozhejas_foresight`
- **Current logic:** `melee_unwavering` — in melee (not wavering): cast on self.
- **Game declares:** a hex aimed at ONE **enemy unit** (wind-up 3 s); 25 s: −12 Armour, −12 Missile Block Chance, −10 Missile Resistance.
- **Why it fails:** cast target — the curse binds the enemy; the mod self-casts it.
- **Feasibility:** not implementable as-is — enemy-targeted casts cannot be aimed by the mod.

### 503 — Warden's Cage (`wardens_cage`)
- **Key:** `wh2_dlc15_character_abilities_wardens_cage`
- **Current logic:** `melee_unwavering` — in melee (not wavering): cast on self.
- **Game declares:** direct damage aimed at ONE **enemy unit** (characters; strongly vs characters); 25 s: 20 damage per second, Can't Move, −60 Armour, −48 Melee Defence.
- **Why it fails:** cast target — the cage must trap an enemy character; the mod casts it on the Warden itself (self-cast cannot cage the target).
- **Feasibility:** not implementable as-is — enemy-targeted casts cannot be aimed by the mod.

### 504 — Warp Gaze (`warp_gaze`)
- **Key:** `wh_pro04_unit_abilities_warp_gaze`
- **Current logic:** `melee_unwavering` — in melee (not wavering): cast on self.
- **Game declares:** a hex aimed at ONE **enemy unit** (100 m intercept, ×3 uses); 12 s: the target Can't Move (the gaze pins the enemy).
- **Why it fails:** cast target — an enemy-pinning hex cast on the caster; the enemy never gets pinned.
- **Feasibility:** not implementable as-is — no enemy aiming available.

### 505 — Warpstiletto (`warpstiletto`)
- **Key:** `wh3_dlc29_item_abilities_warpstiletto`
- **Current logic:** `melee_unwavering` — in melee (not wavering): cast on self.
- **Game declares:** a hex aimed at ONE **enemy unit** (100 m intercept, ×2 uses); 20 s: the target Can't Move.
- **Why it fails:** cast target — the stiletto's effect must land on the enemy; the mod addresses the cast to the caster.
- **Feasibility:** not implementable as-is — enemy-targeted casts cannot be aimed by the mod.

### 508 — Where You Goin!? (`were_you_goin`)
- **Key:** `wh3_dlc26_character_abilities_were_you_goin`
- **Current logic:** `melee_unwavering` — in melee (not wavering): cast on self.
- **Game declares:** an augment cast on a **friendly unit — self is not a valid target** (target_friends = true, target_self = false, affect_self = false); 25 s: Unbreakable — the Bruiser flings a fleeing ally back into the fight.
- **Why it fails:** cast target — an ally-targeted effect cast on self; the recipient is meant to be another unit, and the game does not offer the caster as one.
- **Feasibility:** fixable in principle but not built — the mod can read friendly units and already passes an ally target elsewhere (ally-picker pattern); this entry has none.

### 509 — Whip of Agony (`whip_of_agony`)
- **Key:** `wh2_twa03_weapon_abilities_whip_of_agony`
- **Current logic:** `melee_unwavering` — in melee (not wavering): cast on self.
- **Game declares:** a hex aimed at ONE **enemy unit** (75 m intercept); 29 s: −24 Melee Defence, Causes Fear, Causes Terror.
- **Why it fails:** cast target — the pain is for the foe; self-cast is a wrong target.
- **Feasibility:** not implementable as-is — enemy-targeted casts cannot be aimed.

### 510 — Whip of Misery (`whip_of_misery`)
- **Key:** `wh2_main_spell_bound_whip_of_agony`
- **Current logic:** `melee_unwavering` — in melee (not wavering): cast on self.
- **Game declares:** a hex aimed at ONE **enemy unit** (large units only — invalid target flag `unit_is_not_large`, ×3 uses); 31 s: −30 Accuracy, −24 Melee Attack.
- **Why it fails:** cast target — the misery is inflicted on the enemy; the mod self-casts it.
- **Feasibility:** not implementable as-is — no enemy aiming available.

### 511 — Whiplash! (`whiplash`)
- **Key:** `wh2_dlc14_lord_abilities_whiplash`
- **Current logic:** `melee_unwavering` — in melee (not wavering): cast on self.
- **Game declares:** an augment cast on a **friendly unit — and commander-class units are invalid targets** (`unit_is_commander_class`; the Beastmaster whips the *beasts*); 21 s: Charge Speed ×1.25, Charge Bonus ×1.2, Weapon Damage ×1.5.
- **Why it fails:** cast target — an ally-targeted effect cast on self, and the caster (a commander-class character) is precisely the kind of unit the game forbids as a recipient; the buff can never apply to the caster.
- **Feasibility:** fixable in principle but not built — needs the ally-picker pattern (the mod already casts on friendly units elsewhere), plus the beast/non-commander recipient choice.

### 512 — Whispering Mist (`whispering_mist`)
- **Key:** `wh3_dlc29_hero_abilities_whispering_mist`
- **Current logic:** `melee_unwavering` — in melee (not wavering): cast on self.
- **Game declares:** a hex aimed at ONE **enemy unit** (wind-up 1 s); 32 s: Speed ×0.55, Charge Speed ×0.55.
- **Why it fails:** cast target — the slowing mist must be placed on the enemy; the mod self-casts it.
- **Feasibility:** not implementable as-is — enemy-targeted casts cannot be aimed by the mod.

### 515 — Willing Prey (`willing_prey`)
- **Key:** `wh3_main_lord_abilities_willing_prey`
- **Current logic:** `melee_unwavering` — in melee (not wavering): cast on self.
- **Game declares:** a hex aimed at ONE **enemy unit**; 15 s: −24 Melee Attack, −40 Melee Defence.
- **Why it fails:** cast target — the debuff is for the enemy; the mod aims the cast at the caster.
- **Feasibility:** not implementable as-is — no enemy aiming available.

### 517 — Word of Change (`word_of_change`)
- **Key:** `wh3_main_daemon_head_abilities_word_of_change`
- **Current logic:** `melee_unwavering` — in melee (not wavering): cast on self.
- **Game declares:** a hex of the winds aimed at ONE **enemy unit** (casting units only — `hasnt_casting_ability`); 42 s: enemy Miscast Chance ×2.
- **Why it fails:** cast target — the word is spoken at an enemy spellcaster; the mod self-casts it.
- **Feasibility:** not implementable as-is — enemy-targeted casts cannot be aimed by the mod.

### 518 — Word of Pain (`word_of_pain`)
- **Keys:** `wh2_dlc10_spell_bound_word_of_pain`, `wh3_dlc27_spell_dark_magic_word_of_pain_bound_1use`
- **Current logic:** `melee_unwavering` — in melee (not wavering): cast on self.
- **Game declares:** a bound Dark Magic hex aimed at ONE **enemy unit**; 40 s: −30 Accuracy, −40 Melee Attack.
- **Why it fails:** cast target — the agony is for the enemy; self-cast is a wrong target.
- **Feasibility:** not implementable as-is — enemy-targeted casts cannot be aimed by the mod.

### 519 — Woven Mist (`woven_mist`)
- **Key:** `wh_dlc05_unit_abilities_woven_mist`
- **Current logic:** `melee_unwavering` — in melee (not wavering): cast on self.
- **Game declares:** a self toggle (permanent until disabled, 1 s recharge): **−24 Melee Defence**, +40 Missile Resistance — an anti-missile dance that pays for the protection with melee defence.
- **Why it fails:** trigger fit — the toggle is fired exactly when the unit is in melee, i.e. when the melee-defence penalty bites and the missile protection is only partially relevant; the ability is built to be raised under missile fire, not in a melee.
- **Feasibility:** trigger-choice problem, not an engine limit — the mismatch is when it fires, not what it can read; the cast target (self) is correct.

## CLEAN

Every entry below was judged a confident yes: self is a valid cast target for it (self-only, or self+friends with affect_self), and its effect is one the unit can use in the melee state the trigger fires in.

- `the_golden_eye_of_tzeentch` — The Golden Eye of Tzeentch
- `the_guiding_eye` — The Guiding Eye
- `undeath_sulekhim_hand_of_dust` — The Hand of Dust
- `the_liber_noctus` — The Liber Noctus
- `lions_shield` — The Lion's Shield
- `the_praise_of_slaanesh` — The Praise of Slaanesh
- `the_seerstaff_of_saphery` — The Seerstaff of Saphery
- `the_wintertooth_crown` — The Wintertooth Crown
- `wissenland_runefang` — The Wissenland Runefang
- `thorns_aura` — Thorn's Aura
- `undeath_resurgent` — Undeath Resurgent
- `unholy_clamour` — Unholy Clamour
- `unlimited_power` — Unlimited Power!
- `ursuns_roar_2` — Ursun's Mighty Roar
- `ursuns_roar` — Ursun's Roar
- `van_horstmanns_speculum` — Van Horstmann's Speculum
- `waaagh_in_combat` — Waaagh!
- `wand_of_jet` — Wand of Jet
- `warpstone_tokens` — Warpstone Tokens
- `watched_by_the_watcher` — Watched by the Watcher
- `whispering_skull` — Whispering Skull
- `wild_abandon` — Wild Abandon
- `winds_of_change` — Winds of Change
- `wrath_of_the_storm` — Wrath of the Storm
- `wrathful_reaper` — Wrathful Reaper
- `wristbands_of_black_gold` — Wristbands of Black Gold

**Counts: entries audited 58 · flagged 32 · clean 26.**
