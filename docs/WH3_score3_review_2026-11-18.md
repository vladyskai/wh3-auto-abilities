# Score-3 abilities: one trigger per ability (proposals, 2026-11-18)

User, 2026-11-18: "Section 2B proposals" (section 2B of `docs\WH3_overnight_audit_2026-11-17.md`: "works, but a better
trigger exists").

## How this review was done

- **Scope:** every row scored 3 in `docs\audit_night\review_*.md` (95 rows), with each grouped row split into single
  abilities.
- **Already settled, not repeated here** (rounds 171-176):
  - built: Red Fury, The Rock of Inevitability, The Wissenland Runefang, Waaagh! (wh_main), Chalice of Dark Rain;
  - closed: Locus of Abjuration;
  - fixed in round 165: "Stay Here, I'll Get Help!" (it holds while the caster fights);
  - Waaagh! (dlc26 key): your round-171 ruling kept it in melee;
  - Chain Lightning (RoR): built on its own trigger in round 163.
- **Facts:** every effect, duration, use count, range and target rule comes from the game data
  (`tools\fact_sheet_open.py`). Earlier decisions come from the tracker (rule 11) and are quoted.
- **Proposals only (rule 9):** nothing is changed until you rule.
- **Score after:** how sure I am that this is the best trigger the game's reads allow. Below 5 says what is missing.
- **"RULED" rows:** you already decided these. I quote the ruling and give my proposal only as an option to reopen; the
  default is to keep your ruling.

### Reads the proposals use

| Read | Status |
|---|---|
| A. Charging / fresh contact (entered melee at most 2 s ago) | exists (rounds 171-174) |
| B. Fast enemy closing on our units (run speed 5 m/s or more, moving, within 40 m) | exists (`fast_enemy_near`) |
| C. The engagement set (enemies in melee within 12 m of the caster) and the GENERATED large set | both exist |
| D. Under missile fire (`is_under_missile_attack`) | exists |
| E. Live health % and live hit points (`HealthValue`) | exist |
| F. Winds pool and reserve (round 171 `winds_low`) | exists |
| G. The spellcaster list (round 174, 865 land units) | exists |
| H. The blob value pick with the friendly-fire clearance (round 146) | exists for projectile blasts; NEW for bombardments (their radius is in `projectile_bombardments`, already read by `tools\gen_ww_tables.py`) |
| I. GENERATED unit sets for Squigs, Tiger Warriors and Lizardmen (the game's own target rules) | NEW (from the game's unit groupings); I would show you the sets first |

## 1. Self and aura buffs that pay at a specific moment

| # | Ability | Every effect (game data) | Now | Proposed trigger | Score after |
|---|---|---|---|---|---|
| 1 | Blood Omens (**BUILT round 177**) | EVERY enemy: speed and charge speed x0.75, 26 s; ONE use | in melee | **SLOW, ARMY-WIDE:** fires when a visible fast enemy is closing on any of our units (read B), or the caster is in melee. Rule 10: an enemy speed cut pays on their charge. | 5 |
| 2 | Creature-Killer (**BUILT round 177**) | bonus vs large +16, caster and allies within 35 m, 38 s; recharge 120 s | in melee | **MELEE VS LARGE:** the caster, or a unit of ours within 24 m (70% of 35), is in melee with a LARGE enemy (read C). Against infantry the bonus does nothing. | 5 |
| 3 | Daemonshield (**KEPT round 177 (user: stays the same)**) | the caster is invulnerable, 13 s; recharge 120 s | in melee | **IN MELEE AND HURT:** in melee at or below 75% health (the existing `melee_health75`). 13 s of invulnerability pays when damage is flowing, not on a healthy unit's first contact. Option: 50%. | 4 (no read of incoming damage) |
| 4 | Empowering Shrooms (**BUILT round 177**) | SQUIG allies within 35 m (the game's rule: squigs only): melee attack +24, leadership +16, 35 s | in melee | **SQUIG IN MELEE:** a squig ally within 24 m is in melee (read I, a NEW squig set). Today it fires with no squig near. | 5 |
| 5 | Everyone Has Their Price (**BUILT round 177**) | enemies within 35 m: melee attack -24, leadership -8, 15 s | in melee | **ENEMIES FIGHTING NEAR:** the caster is in melee, or an enemy within 24 m is in melee with one of ours. | 5 |
| 6 | Fury of the Land (**BUILT round 177**) | allies within 55 m: Fear, magical attacks, Strider, 35 s | in melee | **AURA CHARGE OR MELEE:** the caster or a unit within 38 m is charging, just made contact, or in melee. Fear pays at contact; Strider before it. | 4 (Strider's terrain value has no read) |
| 7 | Terrorgheist Skull (**KEPT (ruled)**) | abilities recharge faster, caster or ally within 100 m, 44 s | caster or ally in melee | **RULED** (round 141: "Self or ally in melee"). **REOPENED (user, 2026-11-18: "Remove the melee fallback"):** the caster or an ally within 70 m with an ability the mod cast still recharging (the `recharging_in_reach` read), no melee arm. Limit: abilities you cast by hand are not seen. | 5 |
| 8 | Primal Roar (**KEPT**) | melee attack +40, physical resistance +20, caster and allies within 35 m, 25 s (Rampage) | in melee | **KEEP:** melee is the moment; the Rampage risk is handled by the round-167 default (it starts on M). | 4 |
| 9 | Rage Embodied (**KEPT**) | enemies within 35 m: Rampage, 15 s | in melee | **KEEP:** no read says when enemy Rampage helps us. | 3 |
| 10 | Rage Incarnate (**KEPT**) | enemies within 55 m: Rampage, 15 s | in melee | **KEEP**, as Rage Embodied. | 3 |
| 11 | Refuse to Die (**BUILT round 177**) | the caster cannot die, 20 s; recharge 60 s | in melee | **RULED (user, 2026-11-18: "change to 10% as my hag's denial"): LAST STAND, as Hag's Denial** (the existing `self_last_stand`: at or below 10% health, in melee or under fire). Cannot Die only matters near death; on first contact it burns 20 s early. | 5 |
| 12 | Rune of Oath & Steel (**BUILT round 177**) | armour +30, caster and allies within 35 m, 44 s; 3 s wind-up | in melee | **MELEE OR UNDER FIRE** (the existing `melee_or_under_fire`): armour also stops arrows. | 5 |
| 13 | Seductive Glory (**KEPT (ruled)**) | enemies within 35 m: melee defence -24 (Rampage) | in melee | **RULED** (2026-10-28: kept, starts unarmed). | - |
| 14 | Shield of Aeons (**BUILT round 177**) | armour +60, caster and allies within 55 m, 23 s | in melee | **GUARD AURA** (user, 2026-11-18: "the caster or any ally in range"): the caster, or ANY unit of ours within 38 m (70% of the 55 m aura), is in melee or under fire, or a fast enemy is closing on one of them (read B: an enemy charge). Cast on the caster, so the aura covers them. | 5 |
| 15 | Shielding Swarm (**BUILT round 177**) | ONE unit (the caster or an ally within 100 m): melee defence +24, missile block +36, 30 s | in melee, on self | **SELF OR ALLY UNDER FIRE OR IN MELEE:** the caster under fire or in melee; else the most valuable ally within 70 m under fire; else the nearest ally in melee. The missile block is the bigger part. | 5 |
| 16 | Shielding Swarm Upgraded (**BUILT round 177**) | as #15: melee defence +36, missile block +48 | in melee, on self | as #15 | 5 |
| 17 | Slayer for Chaos (**BUILT round 177**) | the caster cannot die, melee attack +12, 24 s; ONE use | in melee | **LAST STAND, as Hag's Denial** (the existing `self_last_stand`: at or below 10% health, in melee or under fire; your round-144 ruling for a one-use Cannot Die). | 5 |
| 18 | Steppe Hunter's Horn (**BUILT round 177**) | bonus vs large x2, caster and allies within 35 m, 20 s | in melee | **MELEE VS LARGE**, as #2. | 5 |
| 19 | The Armour of Morkar (**BUILT round 177**) | melee defence +24 and charge reflection, caster and allies within 35 m, 29 s | in melee | **GUARD AURA**, as #14, with the units within 24 m (70% of its 35 m aura) (the reflection pays when the enemy charges in). | 5 |
| 20 | The Blood Price (**BUILT round 177**) | melee damage x1.6, all resistances +20; the caster takes 60 damage every 2 s for 22 s (660) | in melee | **IN MELEE AND HEALTHY:** in melee above 50% health (the winds-items guard). It starts on M (self-damage, round 167). | 5 |
| 21 | The Ostermark Runefang (**BUILT round 177**) | bonus vs large +32, caster and allies within 35 m, 27 s | in melee | **MELEE VS LARGE**, as #2. | 5 |
| 22 | Toad Rage (**KEPT**) | melee damage x1.5 (Rampage), self, 18 s | in melee | **KEEP:** melee is the moment; it starts on M (Rampage). | 4 |

## 2. Enemy-targeted

| # | Ability | Every effect | Now | Proposed trigger | Score after |
|---|---|---|---|---|---|
| 23 | Chain Lightning (bound) (**BUILT round 178**) | 4 damage a second for 5 s, up to 75 models, chaining to 10 units; 2 uses; 5 s wind-up | blob | **MOST MODELS, NEVER BLOCKED** (user, 2026-11-18: "should not be unused if there are less models in the unit. Maybe preference for numerous entities units"): the visible enemy unit in range with the most models alive, counted up to 75 (every unit with 75 or more ranks as full; among those, the most value per soldier wins); with no unit of 75, the one with the most models still qualifies, down to a floor of 16 models (user, 2026-11-18: "a minimum of 16 units for both"). Standing still. NEW: a variant of `enemy_area_drain` with the 16-model floor in place of its minimum. The chain spreads, a 1-model blast does not describe it. | 5 |
| 24 | Chain Lightning (bound, unit) (**BUILT round 178**) | the same; ONE use | blob | **AREA DRAIN**, as #23. | 5 |
| 25 | Blacktoof's Conjuration (**KEPT round 178**) | a summon at a ground spot within 50 m; ONE use | ground under an enemy in melee | **KEEP:** a summon that joins a fight is right next to one. | 4 (the summon's own stats not reviewed) |
| 26 | Wake Da Idol (**KEPT round 178**) | a summon at a ground spot within 50 m; ONE use | same | **KEEP**, as #25. | 4 |
| 27 | Transformation of Kadon (**KEPT round 178**) | transforms at a ground spot within 50 m; 5 s wind-up; ONE use | same | **KEEP**, as #25 (ASSUMPTION: the transformation is a summoned monster at the spot; if it transforms the caster, "caster in melee" is better). | 3 |
| 28 | Surprise Squig! (**NOT BUILT round 178: the data shows it SUMMONS Explosive Squigs; a new proposal follows**) | an explosion at the enemy's feet; 5 uses | ground under an enemy in melee | **BLOB WITH CLEARANCE** (read H): the standing enemy block with the most value in the blast, none of ours within blast + 10 m. Today it lands in a melee next to our own troops. | 5 |
| 29 | The Soulstealer (**BUILT round 178**) | 4 damage a second for 11 s to up to 25 models, a 35 m area; ONE use | same | **MOST MODELS, NEVER BLOCKED**, as #23, counted up to 25 (its cap), with the same 16-model floor (user, 2026-11-18). | 5 |
| 30 | Whip of Misery (**BUILT round 178**) | ONE large enemy: accuracy -30, melee attack -24, 31 s; 3 uses | enemy in melee or under fire | **MELEE OR SHOOTING** (the existing `enemy_melee_or_shooting`, large class kept): the closest large enemy in melee, else the closest shooting one. Each half pays on its own target. | 5 |
| 31 | Word of Pain (2 keys) (**BUILT round 178**) | ONE enemy: accuracy -30, melee attack -40, 40 s; 2 uses / 1 use | same | **MELEE OR SHOOTING**, as #30 (any class). | 5 |
| 32 | Book of Secrets (**KEPT round 178**) | three phases: 10 damage a second to 25 models; speed x0.75 and flame weakness; melee attack and defence -24; 3 uses | same | **RULED** (round 135: "Keep as is"). Option: `enemy_melee_or_fast` (rule 10). | - |
| 33 | Fecund Rebirth (**KEPT round 178**) | ONE large single enemy: 38 damage a second, speed and charge speed x0.5, no healing, 32 s | same | **RULED** (round 135: "Keep as is", large single class). | - |
| 34 | Looming Dread (**KEPT round 178**) | ONE Lord or Hero: speed x0.55, melee defence -24, missile resistance -20, 31 s | same | **RULED** (round 135: "Keep as is, but make sure the trigger filters for the enemy unit type"). | - |
| 35 | Hunter of Champions (2 keys) (**KEPT round 178**) | ONE Lord or Hero: speed x0.55 (upgrade: rooted), armour -60, melee defence -40, 24 s | same | **RULED** (round 123: "Hunter of champions is okay for enemy_engaged_or_shot"). | - |
| 36 | Gilellion's Soulnetter (**BUILT round 178**) | ONE enemy rooted, 26 s; recharge 120 s | same | **ROOT, FAST ONLY** (user, 2026-11-18: "Yes pls", no melee arm, for #36-#41): a fast enemy closing on ours (read B); the root stops the charge before impact. No melee arm: a rooted unit already in melee still fights. The existing `enemy_fast_near_ally` pick. | 5 |
| 37 | Net of Amyntok (**BUILT round 178**) | ONE enemy rooted, 20 s; 3 uses; 3 s wind-up | same | **ROOT**, as #36. | 5 |
| 38 | Spiderweb Attack (**BUILT round 178**) | ONE enemy rooted, 18 s; 2 uses | same | **ROOT**, as #36. | 5 |
| 39 | Warp Gaze (**BUILT round 178**) | ONE enemy rooted, 12 s; 3 uses | same | **ROOT**, as #36. | 5 |
| 40 | Warpstiletto (**BUILT round 178**) | ONE enemy rooted, 20 s; 2 uses | same | **ROOT**, as #36. | 5 |
| 41 | Pack Trap (**BUILT round 178**) | ONE enemy rooted, 10 s; 3 uses | same | **ROOT**, as #36. | 5 |
| 42 | Prey of Anath Raema (**BUILT round 178**) | ONE enemy rooted, missile resistance -20, 16 s; 3 uses | same | **ROOT, ELSE UNDER OUR FIRE:** a fast enemy closing; else an enemy our shooters are hitting (read D on the enemy); else the closest in melee. | 5 |
| 43 | Net Dem Up! (**BUILT round 178**) | ONE enemy rooted, missile block -50, 18 s | same | **ROOT, ELSE UNDER OUR FIRE**, as #42. | 5 |
| 44 | Glory Seeker (**BUILT round 178**) | ONE Lord or Hero: rooted, melee defence -24, no healing, 24 s | same | **LORD OR HERO: FAST, ELSE MELEE** (user, 2026-11-18: "makes sense to also add root"): an enemy Lord or Hero closing fast on ours (the root stops its charge, read B), else an enemy Lord or Hero in melee (the defence cut and the no-healing pay in a duel). Commander class on both arms. | 5 |
| 45 | Glory Seeker Upgraded (**BUILT round 178**) | the same, melee defence -36, 36 s | same | as #44 | 5 |
| 46 | Prey of the Blood God (**BUILT round 178**) | ONE Lord or Hero: 33 damage a second for 22 s (726), rooted; 3 uses | same | **MOST VALUABLE LORD OR HERO** (the existing `enemy_commander_value`): the damage pays whatever it does. | 5 |
| 47 | Void Pendulum (**BUILT round 178**) | ONE enemy spellcaster (the game's rule), 25 s; 3 uses | same, Lord/Hero proxy | **ENEMY SPELLCASTER** (round 174, read G). | 5 |
| 48 | Word of Change (**BUILT round 178**) | ONE enemy spellcaster: miscast chance x2, 42 s | same | **ENEMY SPELLCASTER** (read G). | 4 (no read of when they cast) |
| 49 | Oil Flask (**KEPT round 178 (user: keep)**) | a thrown flask; it can hit OUR units (the game marks it); 3 uses | same | **KEEP** (user, 2026-11-18: "almost no damage value, so we keep it the same without need for clearance"): the enemy in melee or under fire, as now. Its projectile deals 1 damage. | - |
| 50 | Dweomer Leach Orb (**BUILT round 178**) | ONE enemy spellcaster (the game's rule): drains its winds to the caster, 22 s | most valuable Lord or Hero (round 158) | **ENEMY SPELLCASTER** (read G). Your round-158 ruling ("Lord/Hero proxy") was made because no spellcaster read existed; now one does. | 5 |
| 51 | Slann Gold (**BUILT round 178**) | ONE enemy spellcaster, 55 s | same | **ENEMY SPELLCASTER**, as #50. | 5 |
| 52 | Deathmaster's Sigil (**KEPT round 178**) | ONE grounded Lord or Hero rooted, 7 s, a 15 m blast | most valuable grounded Lord or Hero | **RULED** (round 159). Option: the Lord or Hero closing fast on ours, else in melee (a 7 s root pays then). | - |
| 53 | Eye of Khorne (**BUILT round 178**) | ONE non-Lord enemy at or below 20% health (the game's rule): 2,660 damage per 1 s tick, up to 100 models; ONE use | the lowest-health non-Lord | **RULED (user, 2026-11-18: "the below 20% highest value unit that is not a lord or hero"): MOST VALUABLE AT THE LINE:** the visible enemy at or below 20% health with the highest live value, never a Lord or Hero (the game's rule too). Today a 3-man remnant can take the one use. | 5 |
| 54 | Trophy Heads (2 keys) (**BUILT round 178**) | ONE enemy: melee attack -24 / -30, melee defence -40 / -30, 36 s | an enemy Lord/Hero in melee | **SPLIT THE ENTRY:** the base key keeps "Lord or Hero in melee" (its game rule); the Daemon Wings key has no such rule, so it becomes "the closest enemy in melee". | 5 |
| 55 | Siegebreaker (**KEPT round 178 (the data: 100 + 100 AP to units, so it harms units)**) | a strike (siege units only by the game's rule) | the most valuable standing single entity | **QUESTION:** does it harm units in a field battle? If not, close it outside sieges. | - |
| 56 | Gyrocopter Bomb (anti-large) (**KEPT round 178 (user: stays the same)**) | an air drop meant for monsters; 2 uses | air drop on infantry (10+ soldiers) | **AIR DROP ON LARGE:** the same flight rule, the target a LARGE enemy (the generated large set) instead of a soldier count. Today it can never pick a monster. | 5 |

### 2b. The bombardments and area spells (31 abilities on `enemy_ground_melee_infantry`)

Your round-106 ruling put these on "an enemy infantry unit in melee". The problem: the area lands in a melee, next to our
own units, and nothing checks value or friends. **Proposal for every row below: BOMBARD WITH CLEARANCE** (read H): the
standing enemy infantry block with the most value inside the area, none of ours within the area radius + 10 m, the
radius GENERATED from the game's bombardment and vortex tables. One-use comets get the trash rule (not on cheap
infantry unless 3 packed blocks). Score after: 5 for each (4 for Isha's Rain and Pigeon Bomb: the engine has accepted
them without executing, CLAUDE.md section 5).

| # | Ability | Uses / recharge / wind-up / range |
|---|---|---|
| 57 | Axe of Tor | 3 / 90 s / 3 s / 200 m |
| 58 | Celestial Lightning | 2 / 42 s / 3 s / 300 m |
| 59 | Klad Brakak | unlimited / 30 s / 3 s / 30 m |
| 60 | Lightning Strike | 2 / 42 s / 3 s / 300 m |
| 61 | Rod of the Storm | 3 / 90 s / 3 s / 300 m |
| 62 | Urannon's Thunderbolt | 2 / 90 s / 3 s / 300 m |
| 63 | Comet of Casandora | 1 / 120 s / 5 s / 200 m |
| 64 | Celestial Comet | 2 / 49 s / 5 s / 200 m |
| 65 | Meteor Strike | 3 / 49 s / 5 s / 200 m |
| 66 | Lord of the Storm | 3 / 90 s / 1 s / 200 m |
| 67 | Master of Lightning | 3 / 30 s / 1 s / 200 m |
| 68 | Lesser Doombolt | 2 / 90 s / 3 s / 200 m |
| 69 | Rod of Torment | 3 / 90 s / 3 s / 200 m |
| 70 | Tome of Furion | 4 / 60 s / 5 s / 200 m |
| 71 | Wand of the Kharaidon | 2 / 120 s / 5 s / 200 m |
| 72 | Wolf's Howl | 3 / 90 s / none / 200 m |
| 73 | Wraith Storm | 3 / 90 s / 3 s / 200 m |
| 74 | Slicing Shards (2 keys) | 1 each / 48 s / 5 s / 200 m |
| 75 | Searing Doom | 2 / 60 s / 1 s / 200 m |
| 76 | Piercing Bolts of Burning | 4 / 120 s / none / 200 m |
| 77 | Flame & Shadow | 2 / 90 s / 3 s / 100 m |
| 78 | Isha's Rain | 3 / 120 s / 3 s / 200 m |
| 79 | Hawk's Talon | 3 / 90 s / 3 s / 200 m |
| 80 | The Bow of Loren | unlimited / 60 s / 3 s / 200 m |
| 81 | Pigeon Bomb | 3 / 120 s / none / 200 m |
| 82 | Nemesis Crown | unlimited / 120 s / 6 s / 100 m |
| 83 | Chalice of Potions | 2 / 120 s / 5 s / 200 m |
| 84 | Assault of Stone | 1 / 90 s / 3 s / 200 m |
| 85 | Sceptre of Stone | 2 / 90 s / 5 s / 200 m |
| 86 | Dragon Ogre's Great Horn | 2 / 120 s / none / 200 m |

The wind-ups matter: a 5 s wind-up on a moving target misses, so these keep the standing-target rule of the blob pick.

### 2c. The ground roots

| # | Ability | Every effect | Now | Proposed trigger | Score after |
|---|---|---|---|---|---|
| 87 | Entangle | enemies in a 15 m area rooted, flame weakness, 15 s; 2 uses | ground under an enemy in melee or under fire | **GROUND ROOT:** under a fast enemy closing on ours, else under the closest enemy in melee. Open question: #36-#41 dropped their melee arm (user, 2026-11-18); should the ground roots too? | 5 |
| 88 | Get 'Em! | enemies in a 35 m area rooted, 11 s | same | **GROUND ROOT**, as #87. | 5 |
| 89 | Hunter's Snare | the same, 11 s; 3 uses | same | **GROUND ROOT**, as #87. | 5 |
| 90 | Hunter's Trap | the same, 22 s; 3 uses | same | **GROUND ROOT**, as #87. | 5 |

### 2d. The wandering winds and waves (your rulings, rounds 162-166)

| # | Ability | The issue | Proposal |
|---|---|---|---|
| 91 | Sandstorm | its safety ring (worst-case 95% reach) leaves a few metres of window inside the 70 m bound: it rarely fires | **RULED** ("worst-case reach"). Option: an 80% simulated reach for this key. |
| 92 | Heaven's Gate | the caster teleports INTO the blob; nothing checks the caster's own safety | **CLOSE IT** (user, 2026-11-18: "remove the ruling. This is a teleportation and requires player control"): out of automation, cast by hand. |
| 93 | Lamprey's Bite | 59 m clearance against a 70 m bound: rarely fires | **RULED.** Option as #91. |
| 94 | Da Boss' Loons | 98 m ring around the caster free of ours: almost never true in a battle line | **RULED** (round 164: "Loons as wanderer"). Option: a smaller ring if the fanatics do not hit our units (needs a battle test). |
| 95 | The Burning Head (2 keys) | the end-of-path buffer (84-126 m) exceeds the bound (70-105 m): rarely fires | **RULED.** Option as #91. |
| 96 | Arnzipal's Black Horror | the same | **RULED.** Option as #91. |

### 2e. Kept by your rulings

| # | Ability | Ruling |
|---|---|---|
| 97 | Curse of Djaf | "Shooting enemy" (round 143). |
| 98 | Land Mine | "Melee, no friend near" (round 159). Option: also require half a packed block of enemies inside the blast, so 3 charges do not go into one small fight. |

## 3. Self-cast items

| # | Ability | Every effect | Now | Proposed trigger | Score after |
|---|---|---|---|---|---|
| 99 | Shield of Thorns (2 keys) | ONE unit (the caster or an ally within 200 m): damage reflection +20, 30 s; 2 uses | charge or melee, on self | **SELF OR ALLY IN MELEE** (the existing `melee_self_or_ally`): the caster if it fights, else the nearest ally in melee within 140 m. Reflection only pays when struck; the charge arm spends it up to 4 s before contact. | 5 |
| 100 | Snowflake Pendant | miscast chance x0.5, 25 s | when ready (round 150) | **CLOSE IT** (rule 10, as Earthing Rod and Hagtree Fetish, closed in round 171): it only helps before a friendly spell. | 5 (as a decision) |
| 101 | Stave of Avelorn | miscast chance x0, 40 s; ONE use | when ready (round 150) | **CLOSE IT**, as #100. | 5 (as a decision) |
| 102 | Power Stone | winds (the game's phase carries winds effects only), 31 s; ONE use | when ready (round 150) | **WINDS LOW** (round 171, as Black Staff, without the health guard: no self-damage). | 5 |
| 103 | The Chromatic Tome | winds, caster and allies, 27 s | when ready (round 150) | **WINDS LOW**, as #102. | 5 |
| 104 | Blood Chalice of Bathori | a heal (1.6% a second, 26 s) on ONE Lord or Hero (the game's rule), the caster or an ally within 60 m | the caster at 75% | **LORD OR HERO HEAL:** the lowest-health Lord or Hero (the caster or an ally within 42 m) at or below 75%. Today the ally side is wasted. | 5 |
| 105 | Breath of Darkness (2 keys) | a heal (0.8% a second, 14 s) on undead units only (the game's rule), range 200 m; 2 uses | the caster at 75% | **UNDEAD HEAL** (the existing `health_aura_self_undead` pick): the lowest undead unit (the caster or an ally within 140 m) at or below 75%. | 5 |
| 106 | Bugman's XXXXXX | a self heal (1.7% a second, 18 s); the game refuses it with an enemy in its intercept range | the caster at 75% | **HEAL AWAY FROM THE ENEMY:** at or below 75% AND no visible enemy within 38 m (70% of its 55 m reach). Today it is refused in every fight. | 5 |
| 107 | Mantra of Invigoration | a heal on Tiger Warriors only (the game's rule), the caster or an ally within 100 m, 32 s | the caster at 75% | **RULED** (2026-10-08: "Below 75% health (no melee gate)"). Option: the lowest Tiger Warrior unit at or below 75% (read I). | - |
| 108 | Potion of Charoi | all resistances +40, a small heal, 9 s; 4 uses | the caster at 75% | **HURT AND HIT:** at or below 75% AND in melee or under fire. A 9 s resistance burst is wasted while marching hurt. | 5 |
| 109 | Saint Annushka's Finger Bone | a tiny heal (0.2% a second, 13 s) | the caster at 75% | **KEEP.** | 4 |
| 110 | Skar's Kraken-Killer | invulnerable, a heal (1.6% a second), 29 s | the caster at 75% | **LAST STAND:** in melee at or below 50%. | 5 |
| 111 | Foe-Seeker (3 keys) | speed and charge speed x1.25, 25 s | tired | **RULED** (2026-11-15: "Foe-Seeker + tired"). Option: charge or melee. | - |
| 112 | Rock Bottom | refills ammunition; the unit takes 350 damage | out of ammunition | **RULED** ("wait until no ammo left"). Option: add "and more than 700 hit points left" (read E), so the refill never kills it. | - |
| 113 | Blooood! | speed x1.25, acceleration x1.18, 18 s | moving | **RULED** (round 142: "When moving"). | - |
| 114 | Eat da Runts! | heals the caster by hurting an ally | its own family | **QUESTION** (a battle test): does the self arm land? | - |

## 4. Ally-targeted

| # | Ability | Every effect | Now | Proposed trigger | Score after |
|---|---|---|---|---|---|
| 115 | Inspired Assault I (**BUILT round 179**) | ONE ally within 100 m: charge bonus x1.2, melee attack +24, 29 s | the caster in melee, the closest ally | **ALLY CHARGE, ELSE MELEE:** the nearest ally within 70 m charging, else just in contact, else in melee; never a missile unit. | 5 |
| 116 | Inspired Assault II (**BUILT round 179**) | charge bonus x1.4, melee attack +24, 42 s | same | as #115 | 5 |
| 117 | Inspired Assault III (**BUILT round 179**) | charge bonus x1.4, melee attack +40, 43 s | same | as #115 | 5 |
| 118 | Inspired Defence I (**BUILT round 179**) | ONE ally: melee defence +24, leadership +16, 24 s | same | **ALLY IN MELEE, WAVERING FIRST:** the nearest wavering ally in melee within 70 m, else the nearest ally in melee. | 5 |
| 119 | Inspired Defence II (**BUILT round 179**) | the same, 31 s | same | as #118 | 5 |
| 120 | Inspired Defence III (**BUILT round 179**) | melee defence +40, leadership +16, 34 s | same | as #118 | 5 |
| 121 | Da Boss 'as a Plan! (**BUILT round 179**) | ONE ally within 150 m: melee defence +24, leadership +8, 20 s | same | as #118 (105 m) | 5 |
| 122 | Favour of the Fay (**BUILT round 179**) | the caster or ONE ally: melee attack +40, 44 s | same | **SELF OR ALLY IN MELEE** (the existing `melee_self_or_ally`). | 5 |
| 123 | Orcs are da Best! (**BUILT round 179**) | ONE ally within 150 m: melee attack +24, melee damage x1.5, 27 s | same | **MOST VALUABLE ALLY IN MELEE** within 105 m, never a missile unit. | 5 |
| 124 | Hellish Vigour (**BUILT round 179**) | ONE ally within 75 m: damage reflection +20, 25 s; 3 s wind-up | same | **ALLY IN MELEE:** the nearest ally in melee within 52 m (reflection pays when struck). | 5 |
| 125 | Daemonic Whispers (**KEPT round 179**) | ONE ally within 200 m: leadership +16, 26 s | same | **RULED** (round 137: "Keep all 5 for now"). Option: the nearest wavering ally (`ally_wavering`). | - |
| 126 | Horn of Vaul (**KEPT round 179**) | melee damage x1.3, missile damage x1.25, caster and allies within 35 m, 28 s; ONE use | 1 unit fighting or shooting within 24 m | **RULED, KEEP** (round 132: "Same as Metallurgy"; 2026-11-18: "no need of at least 3"). | - |
| 127 | Berry Wine (**BUILT round 179**) | a heal of about 45% over 14 s, the caster and allies within 60 m; ONE use | the lowest unit at 75% | **DEEPER LINE:** the lowest unit at or below 55%. At 75% about 20 points of the 45% heal are wasted. | 5 |
| 128 | Cold-Blooded (**KEPT round 179; the Lizardmen restriction waits for your look at the set**) | ONE Lizardmen unit (the game's rule): leadership +16, 40 s | the wavering ally | **RULED** ("On the wavering ally"). Restriction to add: Lizardmen allies only (read I). | - |
| 129 | Star of Avelorn (**BUILT round 179**) | a heal on a 15 m area anywhere within 200 m, 27 s; 2 uses | the area around the caster's 10 m | **BEST SPOT:** on the ground under the hurt unit of ours, the caster included (at or below 75%), within 140 m with the most hurt units within 10 m of it. Today it reaches only 10 m from the caster. | 5 |
| 130 | Commanding Presence (**BUILT round 179**) | leadership +8, caster and allies within 35 m, 20 s | wavering self, or an ally IN MELEE and wavering | **AS YOUR RULING:** "Not related to melee, only to morale. The trigger should be when lord or nearby unit are wavering." Drop the hidden melee condition. | 5 |
| 131 | Fury of Ulric (**BUILT round 179**) | leadership +8, caster and allies within 35 m, 25 s | same | as #130 | 5 |
| 132 | Hunter's Call (**KEPT round 179**) | melee defence +24, caster and allies within 35 m, 32 s; 3 uses | the caster or one unit within 24 m in melee or wavering | **KEEP** (the same reasoning as #126, 2026-11-18: no minimum count): the caster, or one unit within 24 m, in melee or wavering, as now. | - |
| 133 | Grut's Sickle (**BUILT round 179**) | ONE ally takes 33 damage a second for 20 s to restore winds; 3 uses | when ready, on the sturdiest ally | **WINDS LOW, CHEAPEST ALLY** (user, 2026-11-18: "on expendable ally first (highest hp), then on the ally with lowest value above 75%"): when the winds pool is below 30 with reserve 20+, the target is an EXPENDABLE ally within 70 m (the game's 'expendable' attribute, the GENERATED set from round 163), the one with the most hit points; with none, the ally with the LOWEST live value among those above 75% health. | 5 |
| 134 | Captain of the Phoenix Guard (**KEPT round 179**) | ONE ally (never a Lord, Hero or large): heal, physical resistance +30, 43 s | in melee and 75%, the lowest ally | **RULED** (2026-10-08: "In melee and below 75% health"). Keep. | - |

## 5. A finding for the finishers section

**Skjalandir's Fall** is listed in section 7 of the score 1-2 review as a finisher ("a cast at an enemy"). The game
data says otherwise: its only phase is **on the caster: accuracy +90 for 39 s**. If it carries the kill-shot scaling, it is
through its projectile, not a cast at an enemy. I will check this before the finishers are built; it may stay on your
round-130 ruling ("Shooting into melee").

## What I ask

One ruling per row, or "approve all", or "approve all except #...". RULED rows stay as they are unless you say "reopen
#...". Questions: #55 (Siegebreaker) and #114 (Eat da Runts). (#53 answered: most valuable; #92 answered: closed.)
