# Score 1-2 abilities: one trigger per ability (proposals, 2026-11-17)

User: "I feel like you tried to group the proposed trigger into groups and, in doing so, made the proposals lower
quality ... please review all the abilities in the scores 1-2 group again and propose a solution for each ability that
is the 5/5 for that ability."

## How this review was done

- **Scope:**
  - every row scored 1 or 2 in `docs\audit_night\review_*.md` (34 rows), with each grouped row split into single
    abilities;
  - the five abilities the overnight report's summary table listed with them (Red Fury, Waaagh!, The Rock of
    Inevitability, The Wissenland Runefang, Locus of Abjuration);
  - 52 abilities in 50 rows (row 47 covers the three ranks of Inspired Marksmanship).
- **Facts:** every stat comes from the game data (`tools\fact_sheet_open.py`, plus the phases, attribute and stat
  tables). Earlier decisions come from the tracker (rule 11).
- **Proposals only (rule 9):** nothing is changed until you rule.
- **Score after:** how sure I am that this is the best trigger the game's reads allow. A score below 5 says what is
  missing.

### Corrections to the overnight report

1. **Horn of the Wild Hunt (your example).** Its only effect is charge bonus x1.6, for the caster AND the whole army,
   for 24 s. "Or melee" was wrong as a general rule. The one thing that holds: charge bonus decays over about 10 s
   after impact (80% left at 2 s; `WH3_battle_knowledge.md`). So a cast in the first 2 s of a fresh melee still pays.
   A cast later in a fight is wasted.
2. **The Hammer of Smednir.** The report said its only effect is an enemy slow. Wrong: the x0.4 speed and charge phase
   is on the CASTER itself. Its effect on enemies is a 15 m knock-back blast (detonation force 225, 10 damage). Your
   round-163 ruling, "Keep the blast rule", is right.
3. **The summary table** put five score-3 abilities under "scores 1-2". They are included here anyway.

### Reads the proposals need

| Read | Status |
|---|---|
| A. Our unit in its charge window (12-60 m from its target, at most 4 s from contact) | exists (the charge families) |
| B. FRESH CONTACT: our unit entered melee less than 2 s ago | NEW: the mod polls `is_in_melee()` every 0.25 s, so it only needs to remember the moment each unit enters melee |
| C. ARMY CHARGE: how many of our units are in A or B right now | NEW, built from A and B |
| D. Winds of Magic pool and reserve (`WINDS` map row) | exists, field-proven (Dark Elves battle: pool 12 to 74, reserve 68 to 6) |
| E. Hidden enemy: a living enemy that `is_visible_to_alliance` reads false | exists (rounds 168-169) |
| F. SPELLCASTER class: the unit has a spell lore in the game's `special_ability_groups_to_units_junctions` (855 units, every wizard checked) | NEW, GENERATED; it misses a character who gets a lore only from campaign skills (a generic Vampire Lord) |
| G. PRIMAL INSTINCTS class: the 124 Lizardmen land units with the passive. The game switches it off above 50% health, so it rampages only below 50% | NEW, GENERATED |
| H. Fast enemy closing on our units (run speed 5 m/s or more, within 40 m) | exists (`fast_enemy_near`) |

## 1. Charge buffs and enemy slows

| # | Ability | Every effect (game data) | Now | Proposed trigger (5/5 for this ability) | Score after |
|---|---|---|---|---|---|
| 1 | Horn of the Wild Hunt (**BUILT round 171**) | charge bonus x1.6, caster AND whole army, 24 s; recharge 120 s; unlimited | in melee | **ARMY CHARGE** (**RULED 2026-11-17**): fires when at least N of our units are in their charge window or in fresh contact (reads A + B + C), N = 3, or every living unit of ours when the army has fewer than 3. Any range, since the buff is army-wide. User: "waiting for the perfect moment to use the ability is often less beneficial than just using the ability the moment it is useful". Tracker: "skipped ... charge-only" at collection time (an old rule, never your decision). | 5 |
| 2 | Potion of Foolhardiness (**RULED 2026-11-17: 'Charge or wavering'; built in round 170**) | caster only: charge bonus x1.4 + Unbreakable, 31 s; ONE use | in melee | **`charge_or_wavering`** (exists): on its own charge (charge bonus), or when it wavers (Unbreakable saves it from breaking). | 5 |
| 3 | Ursun's Roar (`wh3_main_character_abilities_ursuns_roar` only) (**BUILT round 171**) | charge bonus x1.36 + leadership +8, caster and allies within 35 m, **9 s**; recharge 60 s | in melee | **AURA CHARGE OR WAVERING** (**RULED 2026-11-17**: "Agreed, and include the wavering"): fires when at least 1 unit (the caster included, or any ally within 24 m = 70% of 35) is in its charge window or fresh contact (charge bonus), or is wavering (leadership +8). Needs its own entry: the other 3 keys of the entry are melee-attack buffs and stay in melee. | 5 |
| 4 | Red Fury (**BUILT round 171**) | charge bonus x1.2 + AP damage x1.25, ONE unit (the caster or an ally within 100 m), 31 s; recharge 90 s | in melee, on self | **ALLY CHARGE OR MELEE:** on the caster or the nearest ally within 70 m in its charge window. Else on the caster in fresh contact. Else on the caster in melee (the AP damage still pays for 31 s). | 5 |
| 5 | Waaagh! (`wh_main_character_abilities_waaagh` only) (**BUILT round 171**) | speed x1.25, charge bonus x1.2, melee attack +20, caster AND whole army, 30 s; recharge 90 s | in melee | **ARMY CHARGE OR ARMY MELEE** (**RULED 2026-11-17**): fires when at least N of our units are in their charge window or fresh contact (speed, charge bonus and melee attack all pay), or at least N are in melee (the +20 melee attack pays in any fight, charge or not). N = 3, or every living unit of ours when the army has fewer than 3. Replaces the 2026-10-08 questionnaire answer (in melee). The other key (`waaagh_in_combat`: melee attack and damage, self) stays in melee. | 5 |
| 6 | The Rock of Inevitability (**BUILT round 171**) | enemies within 35 m: speed x0.75, charge speed x0.75, melee defence -26, 22 s; recharge 90 s | in melee | **SLOW AURA:** fires when the caster is in melee, or a fast enemy (read H) is within 24 m and closing. The defence cut pays in melee; the charge-speed cut pays on an enemy charge. Rule 10 territory. | 5 |
| 7 | The Wissenland Runefang (**BUILT round 171**) | enemies within 35 m: speed x0.55, 29 s; recharge 120 s | in melee | **SLOW AURA**, as the Rock (rule 10: "Enemy speed reductions fire in melee or on the charge"). Tracker: "skipped ... movement" at collection time (an old rule). | 5 |

## 2. Winds of Magic, miscast and spell power items

| # | Ability | Every effect | Now | Proposed trigger | Score after |
|---|---|---|---|---|---|
| 8 | Black Staff (**BUILT round 171**) | winds recharge +80%, winds reserve rule x0.7; **33 damage per second to the target for 20 s (660)**; one unit (the caster or an ally within 200 m); 3 uses | in melee | **WINDS LOW:** fires when the winds pool is below 30 and the reserve is at least 20 (read D), on the caster while it is above 50% health. It starts on M since round 167 (self-damage). | 5 |
| 9 | Forbidden Rod (**BUILT round 171**) | winds recharge +160%, reserve rule x0.2; **33 damage per second to the caster for 23 s (759)**; 3 uses | in melee | **WINDS LOW**, as Black Staff. | 5 |
| 10 | Wand of Jet (**BUILT round 171**) | winds recharge +80% and own abilities recharge 15 s faster, 57 s; recharge 60 s; unlimited uses | in melee | **`when_ready`:** it is up 57 s of every 117. Waiting for a low pool would lose more than it saves. | 5 |
| 11 | Earthing Rod (**CLOSED round 171**) | miscast chance x0 for 36 s; ONE use | in melee | **Close it (no automation).** Your rule 10: "An effect that only helps before something else happens (... before a friendly spell) is not automated." Only you know when you will cast. | 5 (as a decision) |
| 12 | Hagtree Fetish (**CLOSED round 171**) | miscast chance x0.25 for 29 s; ONE use | in melee | **Close it**, as Earthing Rod. | 5 (as a decision) |
| 13 | Master of the Black Arts (**CLOSED round 171**) | spell mastery x1.6 for 15 s; recharge 90 s | in melee | **Close it**, as Earthing Rod: 15 s of spell power is wasted unless you cast in those 15 s. | 5 (as a decision) |
| 14 | Maw Shard (**CLOSED round 171**) | spell mastery x1.6 for the caster and allies, 22 s; ONE use | in melee | **Close it**, as Earthing Rod. | 5 (as a decision) |
| 15 | Power Familiar (**CLOSED round 171**) | spell mastery x1.2 for 22 s; ONE use | in melee | **Close it**, as Earthing Rod. | 5 (as a decision) |

## 3. Spotting and reveal

| # | Ability | Every effect | Now | Proposed trigger | Score after |
|---|---|---|---|---|---|
| 16 | Rock Eye (**OPEN: not a passive by the data (passive=false, source_type active, 1 use, 60 s); never cast in a battle**) | forest and scrub spotting x1.1, caster and army, 60 s; ONE use | in melee | **HIDDEN ENEMY:** fires when a living enemy reads not visible (read E). Note: the mod then acts on knowing a hidden unit exists, which you cannot see on screen. The alternative is `when_ready` at battle start. | 4 (+10% spotting is tiny whatever the moment) |
| 17 | Watched by the Watcher (**CLOSED round 171 ('close (no actuation)')**) | every enemy REVEALED for 60 s; 3 uses; recharge 120 s | in melee | **HIDDEN ENEMY** (read E), with the same note. | 5 |

## 4. Wards against magic

| # | Ability | Every effect | Now | Proposed trigger | Score after |
|---|---|---|---|---|---|
| 18 | Null Stone (**OPEN: NOT multiplayer-only (ancillaries: mp_exclusive=false, randomly_dropped=true, High Elves)**) | **every unit on BOTH sides** silenced and magical attacks removed, 35 s; 3 uses | in melee | **ENEMY MAGIC ONLY:** fires when a visible living enemy spellcaster exists (read F) and none of our units is a spellcaster. It silences our casters too. | 5 |
| 19 | Sceptre of Stability (**CLOSED round 171 ('no read against enemy magic')**) | magic resistance +40, one unit (the caster or an ally within 100 m), 22 s; recharge 60 s | in melee | **ON THE UNIT UNDER FIRE:** on the caster or the most valuable ally within 70 m that is under missile fire while a visible enemy spellcaster (read F) is within 150 m of it. ASSUMPTION: magic missiles count as missile fire for `is_under_missile_attack`. | 4 (no read of an incoming spell) |
| 20 | Locus of Abjuration (**CLOSED round 171 ('no read against enemy magic')**) | magic resistance +65, caster and allies within 55 m, 25 s; recharge 90 s | in melee | **AURA UNDER FIRE:** fires when the caster or an ally within 38 m is under missile fire while a visible enemy spellcaster is within 150 m. Same assumption. | 4 |
| 21 | Necrotic Phylactery (**BUILT round 171 (the contact list: 503 land units)**) | magic resistance +15, immunity to enemy contact effects (poison, burning, ...), spreads to nearby allies, 18 s; ONE use | at or below 75% health | **IN MELEE, NOT WAVERING:** contact effects arrive with melee blows. A 5 would also need the list of enemy units with a contact effect (not extracted yet; feasible later). | 4 |
| 22 | Focus Instincts (**CLOSED round 171 (no read of a rampaging unit)**) | removes Rampage (Primal Instincts) from the caster and Lizardmen allies within 35 m, 40 s; recharge 90 s | in melee | **RAMPAGE RISK:** fires when a Primal-Instincts ally within 24 m (read G) is in melee and at or below 50% health, the game's own condition for the instinct. | 5 |

## 5. Enemy-targeted

| # | Ability | Every effect | Now | Proposed trigger | Score after |
|---|---|---|---|---|---|
| 23 | Executioner | 1 shot: 200 damage, 420 AP, +240 vs large; **damage x1 at full health rising to x4 at 1% health** (`projectiles_scaling_damages`: kill_shot, the user caught it 2026-11-17); 3 uses; 5 s wind-up; range 250 m | blob (1 m blast) | **FINISHER** (**RULED 2026-11-17**: "No need for a max-hit-points table, let's just rely on percentages ... All of them should have priority, if possible, for the entity with the lowest health percentage"): the visible single-entity enemy within 175 m with the LOWEST live health percentage, clear of allies; a tie goes to the most valuable. It fires whenever such a target exists (no health line). ASSUMPTION: the multiplier reads the target entity's own health. | 5 |
| 24 | Amber Bow | 5 shots: 50 damage, 115 AP, +60 vs large, + a 30 / 65 AP burst; 2 uses | blob | **`enemy_large_shot`** (exists): the most valuable large enemy, else the most armoured infantry (the high AP suits armour). | 5 |
| 25 | Gaze of Nagash | 5 bolts: 30 damage, 75 AP, +50 vs large; 3 uses | blob | **`enemy_large_shot`** (AP 75: armour fallback). | 5 |
| 26 | Hand of Gods | 15 bolts: 20 damage, 50 AP, +33 vs large; 2 uses | blob | **LARGE, ELSE VALUE:** the most valuable large enemy, else the most valuable infantry per soldier. The armour fallback does not suit 50 AP. A small variant of `enemy_large_shot`. | 5 |
| 27 | Shem's Burning Gaze | 5 bolts: 20 damage, 50 AP, +33 vs large; 3 uses | blob | **LARGE, ELSE VALUE**, as Hand of Gods. | 5 |
| 28 | Goggly Glare | 10 bolts: 65 damage, 25 AP, +44 vs large; 3 uses | blob | **LARGE, ELSE VALUE** (low AP: never the armour fallback). | 5 |
| 29 | Vindictive Glare | 5 bolts: 65 damage, 25 AP, +44 vs large; 4 uses | blob | **LARGE, ELSE VALUE**. | 5 |
| 30 | Don't Even Try It | 144 damage every 2 s to ONE entity for 18 s (1,296), and its abilities recharge 15 s slower; 2 uses | enemy in melee or under fire | **`enemy_single_drain`** (exists): the most valuable single-entity enemy within 70 m. | 5 |
| 31 | Muster of Malevolents | 144 damage every 2 s to ONE entity for 15 s (1,080), and the target tires twice as fast; 3 uses | same | **`enemy_single_drain`**. | 5 |
| 32 | Cube of Darkness | the target's winds recharge -40% for 18 s; recharge 60 s | same | **ENEMY SPELLCASTER:** the most valuable visible enemy spellcaster (read F) within 70 m. | 5 |
| 33 | Scroll of Leeching | the target's winds recharge -40% for 44 s; ONE use | same | **ENEMY SPELLCASTER**. | 5 |
| 34 | The Vortex Shard | the target's winds recharge -80% for 31 s; ONE use | same | **ENEMY SPELLCASTER**. | 5 |
| 35 | The Trickster's Pendant | miscast chance x2 for enemies within 35 m of the spot, 16 s; range 100 m | ground under an enemy in melee or under fire | **UNDER THE SPELLCASTERS:** on the ground under the visible enemy spellcaster within 70 m with the most other enemy spellcasters within 24 m of it. | 4 (no read of when they cast) |
| 36 | Trickster's Shard | the same, range 500 m | same | **UNDER THE SPELLCASTERS** (bound 350 m). | 4 |
| 37 | Silence the Prey | the target's abilities recharge 30 s slower, 30 s; 4 uses | enemy in melee or under fire | **`enemy_commander_value`** (exists): the most valuable visible enemy Lord or Hero within 70 m (characters carry the most abilities). | 4 (no read of an enemy's ability state) |
| 38 | Power Siphon | the target's abilities recharge 15 s slower and it tires, 30 s; 4 uses | same | **`enemy_commander_value`**. | 4 |
| 39 | The Black Tongue | the target is SILENCED (no spells), 21 s; 2 uses; range 200 m | same | **ENEMY SPELLCASTER** (read F), within 140 m. | 5 |
| 40 | Pageant of Shrikes | the target's missile range x0.8 and reload skill -20, 20 s; 3 uses; range 75 m | same | **`enemy_missile_shooting`** (exists), with a variant: the most valuable shooting enemy missile unit within 52 m, not the closest. | 5 |
| 41 | Chalice of Dark Rain | accuracy -30 for enemies within 35 m of the spot, **89 s**; range 200 m | ground under an enemy in melee or under fire | **UNDER THE SHOOTERS:** on the ground under the shooting enemy missile unit with the most enemy missile value within 24 m of it (a variant of `enemy_ground_shooting`). | 5 |
| 42 | Transfix (`wh3_dlc29`) | the target cannot move, is silenced, melee defence -40, 25 s; the game accepts only a Lord or Hero at or below HALF its base morale; 3 uses | enemy Lord / Hero in melee | **WAVERING LORD OR HERO:** the most valuable visible enemy Lord or Hero within 70 m that is wavering or worse (the closest read to "half morale"; ASSUMPTION), in melee first. | 4 (wavering approximates the game's "half morale") |
| 43 | The Hammer of Smednir | a 15 m knock-back blast (force 225, 10 damage) on the target; the CASTER is slowed x0.4 for 10 s | blob on a standing enemy | **Keep the blast rule** (your round-163 ruling; correction 2 above). | 4 |

## 6. Ally-targeted

| # | Ability | Every effect | Now | Proposed trigger | Score after |
|---|---|---|---|---|---|
| 44 | Fury of Khaine | ONE ally within 100 m: melee attack +24, melee damage x1.5, **RAMPAGE**, 28 s | nearest ally while the caster is in melee (now M by default) | **ALLY CHARGE OR FRESH CONTACT, NEVER A MISSILE UNIT:** the nearest non-missile ally within 70 m in its charge window, else in fresh contact. Your questionnaire answer: "Charge and in melee". Rampage then hits a unit already committed. | 5 |
| 45 | Verminous Fury | ONE ally within 200 m: **RAMPAGE**, Unbreakable, Unyielding Assault, 60 s; 3 uses | same | **ALLY WAVERING IN MELEE, NEVER A MISSILE UNIT:** the most valuable non-missile ally within 140 m that is in melee and wavering. Unbreakable keeps it from breaking, and Rampage is harmless on a unit locked in melee. | 5 |
| 46 | Helping Hand | ONE Lord or Hero ally within 50 m: melee attack +40, all resistances +40, 22 s | the caster in melee, on the nearest Lord / Hero ally (round 165) | **LORD / HERO ALLY IN MELEE:** the nearest Lord or Hero ally within 35 m that is in melee, whether or not the caster fights. | 5 |
| 47 | Inspired Marksmanship I, II, III | ONE missile ally within 100 m: accuracy +30 / +60, reload +20 / +40, 29-44 s | the closest missile ally, at once | **SHOOTING ALLY:** the most valuable missile ally within 70 m that has been shooting for half a reload (the existing shooting read). | 5 |
| 48 | Overseer of the Unseen | ONE ally (never a Lord or Hero, never large, never flying): melee attack +40, **Cannot Die**, Unbreakable, 35 s | the closest eligible ally, at once | **ALLY IN MELEE, AT RISK:** the most valuable eligible ally within 70 m that is in melee and wavering or at or below 50% health (Cannot Die and Unbreakable pay then). Your questionnaire answer: "in melee". | 5 |
| 49 | Whiplash! | ONE beast ally (never a Lord or Hero): charge speed x1.25, charge bonus x1.2, melee damage x1.5, 21 s | the closest beast ally, at once | **BEAST CHARGE OR FRESH CONTACT:** the nearest beast ally within 70 m in its charge window, else in fresh contact. | 5 |
| 50 | Iron-Handed Captain | ONE ally whose morale is BROKEN (the game's rule): leadership +100, **Force Rally**, 42 s; range 200 m | broken ally, but the shared picker skips routing units, so it probably never fires | **ROUTING ALLY:** the most valuable routing ally within 140 m. Force Rally exists to bring a routing unit back. The picker must stop skipping routing units for this entry (a defect). | 5 |

## 7. FINISHERS (user ruling 2026-11-17)

A finisher is an ability whose damage grows as its target's health falls. Ruling: "All of them should have priority,
if possible, for the entity with the lowest health percentage", read from live percentages (no hit-point table).

| Ability | The game's rule | Now | Finisher target |
|---|---|---|---|
| Executioner (`wh2_dlc13_lord_abilities_executioner`) | damage x1 at full health, rising to x4 at 1% (`projectiles_scaling_damages`: kill_shot) | blob (row 23) | the lowest-health-percentage single entity within 175 m, clear of allies |
| Skjalandir's Fall (`wh3_dlc23_character_abilities_skjalandirs_fall`) | the same kill_shot scaling, x1 to x4 | `melee_or_shooting_into_melee` (round 130) | the lowest-health-percentage single entity within its 70% bound, clear of allies (it is a cast at an enemy, so its trigger becomes the finisher pick) |
| The Emperor's Executioner, base and upgrade | executes at or below 20% / 33% health (`execute_ratio`) | `enemy_execute`: the most valuable target at or below the line | the same line, but the LOWEST health percentage first (the most valuable breaks a tie) |

The Emperor's Executioner is a finisher by its effect (an execute), not by the scaling table. It is included because the
ruling says "all of them".

## What I ask

One ruling per row, or "approve all", or "approve all except #...".

- **Rows marked "Close it":** they leave automation (the badge disappears for those keys). They are kept in the
  workbook as "closed by the user" with the reason.
- **New reads:** B (fresh contact), C (army charge), F (spellcaster class) and G (Primal Instincts class). They are
  built and tested in the round that applies the rulings.
