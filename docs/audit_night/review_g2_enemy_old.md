# Review g2: the older enemy-target families (night audit 2026-11-16/17)

Scope: enemy_blob (77), enemy_ground_melee (75), enemy_engaged_or_shot (46), enemy_ground_melee_infantry (30),
enemy_ground_area (9), enemy_ground_shooting (1), air_drop_on_infantry (12). Read from the source: the evaluators
(`eg_pick_enemy`, `enc_pick_enemy`, `evaluate_enemy_blob` with `blob_pick` / `blob_pick_large` / `blob_usage_ok` /
`blob_still` / `blob_friend_gap`, `ad_pick` / `ad_nearest`, `evaluate_enemy_missile_shooting`), the entries' extra fields
(`target_class`, `air_only`, `no_melee`, `unbounded`), the game facts (`fact_sheet_open.py`, the database sections), the
restriction audit and the tracker rulings. Markers are the snake_case of the ability name unless a marker is quoted.
Nothing was played; every "pays off" statement is judged from the effect text in the game data.

Common facts used below:
- `eg_pick_enemy` (shared by enemy_engaged_or_shot, enemy_ground_area, enemy_ground_melee): enemies alive, valid
  (`is_valid_target` when readable), passing the entry's `target_class`, with edge-to-edge `unit_distance` <= the
  ability's 70% bound (`unbounded = true` skips the bound). Arm "melee" = `is_in_melee()` true; arm "missile" =
  `is_under_missile_attack()` true (UNPROVEN on enemies, fail-closed). A melee-arm enemy always beats a missile-arm one,
  then the closest wins. The melee-only flag drops the missile arm. Routing caster: no cast. No friendly check, no
  caster-state check, no size or value check.
- `enc_pick_enemy` (enemy_ground_melee_infantry): in melee AND `is_infantry()` (fail-closed, `unit_class` fallback) AND
  NOT a Lord/Hero (`enemy_is_commander`), closest inside the bound.
- A cast is re-checked just before it is made (alive, still in melee / under fire, still in the bound).

---

## A. Families

### enemy_blob
- Current sentence: "When armed and standing still, fires at the enemy infantry where the blast destroys the most value, when it hits enough soldiers and none of ours are near"
- What the code requires:
  - Caster: `is_moving()` reads exactly false; the game's usage rules from the generated SHOT table (flying exactly true when
    the key is `grounded`-restricted, `is_in_melee()` exactly false when the key is `engaged_in_melee`-restricted).
  - Target set: only VISIBLE enemies (`is_visible_to_alliance`). Infantry candidates: `is_infantry`, at least 10 soldiers,
    NOT flying. Large candidates (only for the 53 prefer_central attacks): the generated large set, exactly not flying.
  - Large first: a central attack picks the best safe LARGE enemy in range (value = projectile + blast damage after armour
    against current hit points, times live strategic value); only if none, the infantry rule.
  - Infantry rule: the blast (generated radius) at the target must cover at least half a packed block (`blob_need`); the
    most value destroyed wins (breaths and central attacks take, within 20% of the best value, the side-on target);
    TRASH (live value under 2 per soldier) only when the blast covers 3 packed blocks; AP-heavy attacks never at armour
    below 50.
  - Safety: none of OUR (tracked, non-expendable) units within blast + 10 m of the target rectangle.
  - The entry's `target_class` (not_flying for Copious Vomit and Swamp Breath) and the 70% bound apply.
  - Pre-cast re-check on a fresh map.
- Verdict: INCOMPLETE. Missing from the sentence: "visible", "in range", the large-first rule for central attacks, the
  usage rules (flying / out of melee where the key needs it), the AP armour rule, the trash rule. "Enemy infantry" is
  wrong for the 53 central attacks, which take a large monster first. "enough soldiers" is vague (half a packed block;
  1 soldier for the 1 m shots).
- Proposed sentence: "When armed and standing still, fires at the visible enemy in range where the blast destroys the most value (a large non-flying one first for central attacks, else an infantry block), with none of yours within the blast + 10 m"
  (about 205 characters).
- Clauses to append per entry: "; the caster must be flying" (grounded breaths); "; the caster must be out of melee" (keys
  with the engaged_in_melee flag); "; armour-piercing: only armour 50 or more" (AP-heavy keys); "; not flying targets"
  (Copious Vomit, Swamp Breath).

### enemy_ground_melee
- Current sentence: "When armed, fires when an enemy in range is fighting in melee and the summon is placed on its ground"
- What the code requires: the melee-only picker (`eg_melee_only`): the CLOSEST enemy inside the bound that is in melee,
  passing `target_class` (not_flying for the two loons), cast through the ground form at that enemy's position
  (`unbounded` entry: any distance). No caster-state check, no friendly check.
- Verdict: WRONG for 15 of its 75 entries (the hexes and area damage: The Curse of Anraheir x3, Transmutation of Lead,
  Soulblight, The Soulstealer, Heaven's Flash, Spinning Loons, The Loons of Eight Peaks, and arguably Surprise Squig!). "the
  summon" is false for them. The rest is EXACT. "in range" means the 70% bound.
- Proposed sentence: "When armed, fires on the ground under the closest enemy within 70% of the ability's range that is fighting in melee"
  (about 120 characters; "summon" and "hex" both disappear because the cast form is the same).
- Append for the loons: "; not flying".
- User ruling (quoted): Gate of Khorne, "The trigger will place it on the closest enemy that is in range of the ability and fighting."
  Round 143 "Fighting enemy, all four / all three" for the curses and the loons.

### enemy_engaged_or_shot
- Current sentence: "When armed, fires when an enemy unit in range is in melee or under missile fire"
- What the code requires: the shared picker, unit form (`perform_special_ability` at the enemy): an enemy inside the 70% bound,
  alive and valid, passing `target_class` (commander / large / large_single / not_undead), that is in melee or under
  missile fire; it casts on the closest MELEE one if there is any, else the closest under-fire one.
- Verdict: INCOMPLETE. Fine as a description but it hides two things: the melee fight wins over a nearer shot-at unit, and
  the entry classes. It reads as a firing condition for the whole group, which is the family's real weakness (see B): it is
  a one-size trigger for 51 hexes with very different payoffs.
- Proposed sentence: "When armed, fires on the closest enemy within 70% of the ability's range that is in melee (a melee fight first) or, failing that, under missile fire"
  (about 150 characters).
- Append per entry: "; Lords and Heroes only" (glory_seeker, glory_seeker_upgraded, headhunt, hunter_of_champions, looming_dread,
  prey_of_the_blood_god, they_needs_stabbin, void_pendulum, word_of_change), "; large monsters only" (whip_of_misery,
  mark_of_the_monster is large and single), "; not undead" (gaze_of_usirian).

### enemy_ground_melee_infantry
- Current sentence: "When armed, fires on the closest infantry unit in range that is fighting in melee"
- What the code requires: closest enemy in the bound that is in melee, is infantry (`is_infantry()`; note the engine calls
  Fell Bats, Devils, the Varghulf and the Zombie Dragon infantry) and is NOT a Lord or Hero; cast in the form the key declares
  (ground form at the enemy, or at the unit for the 5 ground=no keys). No soldier-count or value check, no friendly check.
- Verdict: INCOMPLETE: "not a Lord or Hero" is missing (it is a hard exclusion in the code), and "infantry" hides that a unit
  with 2 survivors qualifies.
- Proposed sentence: "When armed, fires on the closest infantry unit (not a Lord or Hero) within 70% of the ability's range that is fighting in melee"
  (about 125 characters).
- User ruling (quoted, tracker 2026-10-18): "I find it satisfying right now"; the family is "not to be re-litigated". Scores
  below are given anyway and flagged.

### enemy_ground_area
- Current sentence: "When armed, fires when an enemy in range is in melee or under missile fire and the area hex is placed on its ground"
- Code: the shared picker, ground form. `entangle` has `target_class = not_flying`. Nothing else.
- Verdict: EXACT (one gap: Curse of Khsar's usage flag, see B).
- Proposed sentence: "When armed, fires on the ground under the closest enemy within 70% of the ability's range that is in melee (first) or under missile fire" (about 130 characters; same wording as the unit form with "on the ground under").
- Append: "; not flying" (Entangle).

### enemy_ground_shooting
- Current sentence: "When armed, fires on the ground under the closest enemy missile unit in range that is shooting"
- Code: closest enemy of the generated missile class, alive and valid, `FOURTH.enemy_shooting` true (the ammunition-drop
  firing flag with the cast-point and the can-shoot-while-moving rule), NOT in melee, inside the bound; cast on its ground.
- Verdict: INCOMPLETE: "not in melee" is missing.
- Proposed sentence: "When armed, fires on the ground under the closest enemy missile unit within 70% of the ability's range that is shooting and not in melee" (about 135 characters).
- User ruling (quoted, round 143): "Shooting enemy".

### air_drop_on_infantry
- Current sentence: "When armed, fires when the nearest enemy unit with more than 10 models comes within 6 m of this unit's centre, and casts immediately on that evaluation - no delay at all - airborne where the ability requires it"
- Code: not routing; `air_only` entries need `is_currently_flying()` exactly true (fail-closed); `no_melee` entries need
  `is_in_melee()` readable and false; the nearest enemy with more than 10 alive soldiers (ANY enemy: no visibility test, no
  flying test, no infantry test) by CENTRE-to-CENTRE x/z gap; fires when that gap is under 6.0 m (a user-set test constant,
  documented override of the 70% rule). No friendly check. The sentence also contains a hyphen filler ("no delay at all").
- Verdict: INCOMPLETE and wordy: it forgets "out of melee where the ability forbids melee", and the "no delay" clause is
  filler. "Models" should be soldiers/entities (unit sizes count men alive).
- Proposed sentence: "When armed, fires when the centre of the nearest enemy unit with more than 10 soldiers is under 6 m from this unit's centre (the caster must be flying, or out of melee, where the ability requires it)" (about 205 characters).
- User ruling (quoted, round 114): "I trigger the moment distance between edges is below 0.1 meters. That's it." (later changed to the centre-based 6 m test in rounds 114/117; "Valid units are those who have more than 10 entities.")

---

## B. Abilities

Scale as in the brief. For grouped rows, the score applies to every member unless a member is named separately.

### enemy_blob (77 entries; grouped by what the attack is)

Global restriction issue for the family: the game's `min_range` is not checked for Cinderblast Shell (10 m), Cinderblast
Cluster Bomb (5 m) and Coruscating Blast (10 m): an enemy block closer than that can be picked (the order is refused, or
the caster walks). Fix: skip an enemy whose `unit_distance` is under the key's min_range (the SHOT table already carries
min_range for the shot families; add it to BLOB_SHOT). Siege flags are not modelled. "Our units" are the player's tracked
units only (allied AI armies are not in the friendly check).

| Marker | Ability | Effect (short) | Score | Why (one line) | Better trigger (if score <= 3) | Restriction issue |
|---|---|---|---|---|---|---|
| dragon_breaths | Frost Breath x2, Dark Fire of Chaos, Moon / Star / Sun Dragon's Breath, Noxious Breath, Shackolot's Noxious Breath, Pestilential Breath, Soporific Breath, Gordinar's Dragon Breath, Flaming Breath (dlc23), Coruscating Blast | Dragon breath cones, 12-15 projectiles, central + breath | 4 | Value-destroyed, standing, large first, side-on within 20%, flying and out-of-melee rules honoured. The rulings of rounds 150-152. | | `grounded` (caster flying) and `engaged_in_melee` honoured via SHOT; Coruscating Blast min range 10 m not honoured |
| monster_breaths | Fiery Breath, Fire Breath, Elemental Breath, Death Shriek, Flaming Breath (dlc27), Ice Breath, Bellow of Fury, Bellow of Endless Fury, Unspeakable Foulness, Pestilent Torrent | Breath / roar / vomit attacks of monsters and lords | 4 | Same value logic. Bellow of (Endless) Fury also has a morale scare, which a blob is still a fair moment for. | | `engaged_in_melee` honoured |
| flying_target_breaths | Copious Vomit, Swamp Breath | Vomit / swamp breath, cannot hit flying | 4 | Same logic; the not_flying class is honoured for infantry and large. | | none |
| fireballs | Fireball, Fireball Upgraded, Warp-Fireball, Burning Wrath, The Windblade, Spirit Bear, Dire Spirit Bear, Doomrocket, Arrow of Aqshy, Cinderblast Shell, Quiver of Aqshy, Taal's Judgement | Single heavy exploding projectile, central | 5 | A fireball's payoff is exactly "most value in the blast"; large first is right for the strong ones. | | Cinderblast Shell min range 10 m not honoured |
| ap_snipers_central | The Moonbow, Storm Daemon, Dart of Doom, Eagle Quiver, Skarsnik's Prodder, Sting of Snagla, Ice Shard, Mercurial Shot, Spear of Grungni, The Venom Staff, The Amber Spear, The Gaze of Dust, Bilespurt, Shadowblood, Cinderblast Cluster Bomb, Wind Bow | Armour-piercing single shots / piercing beams, central | 4 | Large first then armour 50+ matches the round-156 rulings for the same kind of shot. Small radii (1-8 m) mean the "blob" is often 1-30 soldiers. | | Cinderblast Cluster Bomb min range 5 m not honoured; The Gaze of Dust "always affects self" is not modelled (harmless) |
| point_shots_r1 | Executioner, Amber Bow, Goggly Glare, Gaze of Nagash, Hand of Gods, Vindictive Glare, Shem's Burning Gaze | Single arrow / beam, blast radius 1 m, NOT central; most have a bonus vs large (Executioner 240, Amber Bow 60, Vindictive 44) | 2 | A 1 m "blob" degenerates to "one soldier of the most valuable infantry". They are snipers and large-killers; large and single targets are never considered. | `enemy_large_shot` ("AP shots: large first, then armour", round 156) for Executioner / Amber Bow; `enemy_single_shot` ("most valuable single", round 156) for the beams. Needs the user (rule 9). | none |
| arrow_volleys | Volley of Dark Arrows, Volley of High Arrows, Volley of Kurnous, Arrow of Kurnous, Bow of the Seafarer, Reaver Bow, Hail of Doom Arrow, Lamentation of Despairs, Lamentation of Despairs (Empowered) | Arrow rains over 3-6 m, AP-heavy | 5 | Arrow rain pays off on a packed block; armour 50+ rule keeps AP out of cloth. | | none |
| thrown_bombs | Cackle Fruit, Pyromaniac, Bomb-Throw, Cracklebomb, Big Boom, Experimental Explosive | Thrown bombs, caster must be out of melee | 5 | Area damage (Cackle Fruit also slows charge); the out-of-melee rule is honoured. | | `engaged_in_melee` honoured via SHOT |
| chain_lightning | Chain Lightning (bound), Chain Lightning (bound, unit) | Light damage, jumps up to 12 m | 3 | 5 damage per hit on a 12 m radius: the blob logic ignores that the chain spreads; low impact, wastes a charge easily. | Most valuable infantry by count (enemy_infantry_shot, "Most valuable infantry" like Bolt Storm) | none |

(Every one of the 77 entries is in one of these groups; the Frost Breath, Flaming Breath, Fire Breath and Chain Lightning pairs are listed once or twice by key.)

### enemy_ground_melee (75 entries)

All summons ride the user's "Fighting enemy" ruling: the summoned unit is placed on the closest in-melee enemy within 70% of the
cast reach. Nothing checks whether our own unit stands in the same melee, which is by the user's design. No restriction flag
other than the two below applies (platform / climbing / deployment flags are siege or battle-phase and not modelled).

| Marker | Ability | Effect (short) | Score | Why (one line) | Better trigger (if score <= 3) | Restriction issue |
|---|---|---|---|---|---|---|
| gates_greater | Gate of Khorne / Nurgle / Slaanesh / Tzeentch / Chaos, Gate of Chaos Upgraded, Greater Gate of Khorne / Nurgle / Slaanesh / Tzeentch, Bloodstone, The Portalglyph, Sword of Change, Locus of Transmogrification | Daemons summoned (degrade over time) | 5 | User ruling: reinforcement lands where the fight is. | | `greater_gate_of_khorne`: army-bar key removed (round 121) |
| monster_beast_summons | Beast Pack, Tide of Death, Tide of Pox, Call to Ceithin-Har, Call to Gwindalor, Children of the Forest, Guardian of the Forest, Guardian Call I / II / III, Gorger Onslaught x2, Stave of Ruinous Corruption, Savage Dominion, Savage Predators, Karanak's Howl, Kettle's Call, Koldunja's Spirit, Mask of the Merlord, The Heralds' Arrival, Ritual of the Beast, Squig Thinkin', Get Tha Gitz!, Lord of Undeath x6, Beyond the Realm, Ghosts of the Past x3, Sacrilege, Roused to Wrath x2, Dreaming Cloak I / II / III, Horn of the Ancestors | Combat units (monsters, cavalry, heroes, infantry) summoned | 4 | Same ruling; the best moment is a melee that is already joined. | | none |
| infantry_swarm_summons | Ancestral Warriors, Ancestral Vengeance, Arachnarok Eggs, Inventory of Hatchlings x2, Maternal Instinct, Lesser Raise Dead, Undeath to All x2, The Awakening, Vizier's Kanopi, The Tomb Blade of Arkhan, The Tallyman's Blades x2, Invocation of the Lichemaster x3, Nurgling Birth x2, Captain Roth's Moondial | Zombies / skeletons / spiders / nurglings summoned | 4 | Fodder joins the fight at the best moment; The Tallyman's Blades Upgraded is `unbounded` (any enemy). | | none |
| self_flagged_summons | Blacktoof's Conjuration, Wake Da Idol, Transformation of Kadon | Idol totem / transforms the caster (game flag: always affects self) | 3 | "Placed on the enemy's ground" is meaningless for an effect on the caster; the payoff is when the CASTER fights. | `melee_unwavering` (caster in melee) | "always affects self" is not modelled |
| surprise_squig | Surprise Squig! | Explosive squig summoned | 3 | The explosion at the enemy's feet is next to our own units in that melee. | enemy_melee_clear style (friendly-fire check, round 159) | friendly fire not checked |
| curse_of_anraheir | The Curse of Anraheir x3 | Speed -25%, Accuracy -30, Melee Attack -24, Melee Defence -24 to enemies in the area | 5 | A speed cut plus melee stats on a fighting enemy matches rule 10 (melee or charge) and the ruling. | | none |
| transmutation_of_lead | Transmutation of Lead | Melee Attack -24, base weapon damage -30% | 5 | Melee-only stats on an enemy in melee: exactly rule 10. | | none |
| soulblight | Soulblight (Doomfire Warlocks) | Armour -30, weapon damage -25% | 4 | Helps while fighting; armour also helps vs our missiles, slightly more value if the trigger also took shot-at enemies. | | none |
| heavens_flash | Heaven's Flash | Melee Attack -24, Melee Defence -24 | 4 | Melee stats on an enemy in melee. The speed reduction the old note mentioned is not in the data. | | none |
| the_soulstealer | The Soulstealer | 4 damage per hit, max 25 entities, fatigue | 3 | Damage-over-area on one fighting unit; low value per cast, better on a dense block. | blob logic (enemy_area_drain style, "max_damaged_entities" soldiers in the area) | none |
| fanatic_releases | Spinning Loons, The Loons of Eight Peaks | Fanatics (ball and chain) released onto the enemy, 3 uses | 4 | Spinning cyclone pays off where a unit is held in melee; not_flying is honoured. | | `health_below_25%` usage (caster may not cast under 25% health) NOT checked: add an own-health read, skip below 25% |

### enemy_engaged_or_shot (46 entries, 51 keys)

Family-wide: the trigger is a one-size grab-bag. Round 123 (user, verbatim, tracker 10.10) taught: "The one with effect only
-40 melee defense makes sense only when the enemy is in melee. It does not make sense to activate it when the enemy is shot
(please learn from this example)" and "The ones that reduce the enemies speed should trigger in melee or when charging.
This way we avoid the issue of fire on an enemy that is only passing by." The older members of this family have never been
re-sorted by that rule. Entries that mix a melee stat with armour / physical resistance score 4 (armour pays in both arms).

| Marker | Ability | Effect (short) | Score | Why (one line) | Better trigger (if score <= 3) | Restriction issue |
|---|---|---|---|---|---|---|
| accusation | Accusation | Armour -30, Melee Defence -24, Missile Resistance -20, Physical Resistance -20 | 4 | User ruling (verbatim: "implement accusation automatic activation when enemy unit in range is in melee or being shot at"). | | none |
| armour_pure | Plague of Rust, The Vial of Hashut, Blade of Setep, The Withering x2 | Armour -30 / -60 (+ fire weakness, phys res, leadership -8) | 4 | Armour helps against melee and missile damage: either arm is a payoff. | | none |
| armour_missile | Mark of Yin, Marked by Ulthar, Vorozheja's Foresight | Armour / Missile Block / Missile Resistance down | 4 | Mostly missile stats: best on the under-fire arm; the melee arm is still fine for armour.  | | none |
| armour_meleedef | Bastet, Bloody Onslaught, Sword of Filth, They Needs Stabbin' | Armour -30 / -60 plus Melee Defence -24 / -40 | 4 | Armour pays in both arms; the melee defence half is wasted on an enemy only being shot (rule 10, mixed). | | They Needs Stabbin' Lords/Heroes only: honoured (`commander`) |
| leadership | Doom & Darkness x3, Fear of Aramar, Eternal Gaze | Leadership -16 / -24, Terror, fatigue | 4 | Leadership loss breaks a unit that is fighting or being shot; Eternal Gaze not_undead honoured. | | Eternal Gaze: "does not affect units immune to Terror" not modelled (small) |
| mark_of_plague_fleet | Mark of the Plague Fleet | Healing -50%, resistances -20, fatigue | 4 | Resistance cuts pay in both arms. | | none |
| melee_only_stats | Whip of Misery, Word of Pain x2 | Accuracy -30 with Melee Attack -24 / -40 | 3 | Half of the effect is a melee stat (rule 10), half is accuracy (missile). On the under-fire arm only the accuracy matters, and it fires on large enemies only (Whip) at any distance in the bound. | `enemy_melee` for the melee half (a user choice, rule 9) | Whip: `unit_is_not_large` honoured via `large` |
| speed_cuts | Book of Secrets, Fecund Rebirth (`mark_of_the_monster`), Looming Dread, Hunter of Champions (speed -45%) | Speed -25% / -45% / -50%, plus damage or defences | 3 | Rule 10: a speed cut on an enemy merely being shot or passing is wasted. | `enemy_melee_or_fast` (melee or a fast enemy closing; the Round 123 pattern) | Lord/Hero or large + single classes honoured |
| roots | Gilellion's Soulnetter, Net of Amyntok, Spiderweb Attack, Warp Gaze, Warpstiletto, Pack Trap, Prey of Anath Raema, Net Dem Up!, Glory Seeker, Glory Seeker Upgraded, Hunter of Champions (second key) | Cannot move (some with melee defence, healing -100%, missile stats) | 3 | Rooting pays when a unit would otherwise move off a fight, or to stop a charge or advance; "in melee or shot at" often roots a unit that is already stuck. | `enemy_melee_or_fast` or a charging-enemy read (user choice) | Glory Seeker / Hunter of Champions Lords/Heroes only: honoured |
| headhunt | Headhunt | Melee Defence -40, Missile Resistance -20 | 4 | Mixed melee and missile stats; Lords/Heroes only is honoured. | | none |
| prey_of_the_blood_god | Prey of the Blood God | 33 damage to one entity, cannot move (Lord/Hero only) | 3 | A single 33-damage hit plus root; the 33 damage is weak vs a Lord: root-only value on the closest. | `enemy_commander_value` (most valuable Lord/Hero) | none |
| direct_damage | Don't Even Try It, Muster of Malevolents | 144 damage to ONE entity, strong vs characters, ability recharge penalty | 2 | A character killer fired at "the closest enemy that is in a fight", usually a rank-and-file unit. | `enemy_single_drain` / `enemy_commander_value` (most valuable single, round 157) | none |
| wind_drain | Cube of Darkness, Scroll of Leeching, The Vortex Shard | Winds of Magic recharge -140% / -180% for enemies in range | 2 | The effect matters only against an enemy wizard; the family has no caster read (fires on any fighting unit). | `enemy_commander_value` (Lord/Hero proxy for a caster, round 158) | none |
| wizard_hexes | Void Pendulum, Word of Change | Winds recharge down, miscast +100% (needs `hasnt_casting_ability` false) | 3 | Already limited to Lords and Heroes (the proxy), but still gated on melee / shot. | `enemy_commander_value` | `hasnt_casting_ability` approximated by "commander" |
| ability_clocks | Silence the Prey, Power Siphon, The Black Tongue | Enemy ability recharge +15-30 s, fatigue, silence | 2 | Pays against an enemy that owns abilities; the trigger ignores that (rule 10: effect first). | `enemy_commander_value` | none |
| pageant_of_shrikes | Pageant of Shrikes | Range -20%, reload skill -20, ammo drain | 2 | Pays only against a missile unit; a unit "in melee" is the wrong target. | `enemy_ground_shooting`-style pick (enemy missile unit shooting) | none |
| oil_flask | Oil Flask | Fire-weakness projectile | 3 | A projectile aimed at a unit in melee may strike our troops; nothing checks. | friendly-gap check as in enemy_blob | none |

### enemy_ground_melee_infantry (30 entries; user ruling 2026-10-18: "I find it satisfying right now")

All 30 are bombardments cast on the closest in-melee non-commander infantry unit. They share one weakness: no soldier-count
or value check (a 2-man remnant qualifies) and no friendly check (a bombardment on a unit fighting ours hits ours; the later
families, rounds 156 to 164, did add such checks). Not to be re-litigated unless the user reopens it. Scores given as asked.

| Marker | Ability | Effect (short) | Score | Why (one line) | Better trigger (if score <= 3) | Restriction issue |
|---|---|---|---|---|---|---|
| lightning_and_comets | Axe of Tor, Celestial Lightning, Klad Brakak, Lightning Strike, Rod of the Storm, Urannon's Thunderbolt, Comet of Casandora, Celestial Comet, Meteor Strike, Lord of the Storm, Master of Lightning | Bombardment of lightning / comets on a ground point | 3 | Strong area effect on whichever infantry unit is in melee first; a one-use comet is wasted on a nearly dead unit, and it falls in the melee. | blob scoring (value in the blast, `enemy_blob`) plus a friendly gap | `climbing` n/a |
| doombolts_and_beams | Lesser Doombolt, Rod of Torment, Tome of Furion, Wand of the Kharaidon, Wolf's Howl, Wraith Storm, Slicing Shards x2, Searing Doom, Piercing Bolts of Burning, Flame & Shadow | Single bolt or bombardment (unit form for the 5 ground=no keys) | 3 | Same: no size / value check. | same | none |
| rains_and_arrows | Isha's Rain, Hawk's Talon, The Bow of Loren, Pigeon Bomb, Nemesis Crown, Chalice of Potions, Assault of Stone, Sceptre of Stone, Dragon Ogre's Great Horn | Rains of arrows, rocks, birds | 3 | Same; Isha's Rain and Pigeon Bomb are the known "engine accepts and never executes" cases (CLAUDE section 5). | same | Dragon Ogre's Great Horn "always affects self" (not modelled) |

### enemy_ground_area (9 entries)

| Marker | Ability | Effect (short) | Score | Why (one line) | Better trigger (if score <= 3) | Restriction issue |
|---|---|---|---|---|---|---|
| amulet_of_phastah | Amulet of Pha-Stah | Armour -30, Missile Block -48 | 4 | Armour pays in both arms; missile block most when shot at. | | none |
| chalice_of_dark_rain | Chalice of Dark Rain | Accuracy -30 | 3 | Accuracy matters only for missile units; the area is also placed on a unit that is simply in melee. | `enemy_ground_shooting` (shooting enemy missile unit) | none |
| curse_of_khsar | Curse of Khsar | Armour -60 for 25 s, one use, 35 m radius | 4 | Armour in the blast of two arms; one use deserves a dense block (blob logic) but the melee-or-shot pick is acceptable. | | usage `health_above_50%`: the caster may cast it only below 50% health; the mod never reads the caster's health. Fix: require own `HealthPercent` <= 0.50 |
| entangle | Entangle | Fire weakness -20, cannot move; not flying | 3 | A root: see the roots row in enemy_engaged_or_shot. | `enemy_melee_or_fast` ground form | `flying_currently` honoured |
| roots_ground | Get 'Em!, Hunter's Snare, Hunter's Trap | Cannot move in the area | 3 | Same root issue. | same | none |
| miscast_traps | The Trickster's Pendant, Trickster's Shard | Miscast chance +100% | 2 | Matters only against enemy wizards; "any unit in a fight" is the wrong target. | `enemy_commander_value`, ground form | none |

### enemy_ground_shooting (1 entry)

| Marker | Ability | Effect (short) | Score | Why (one line) | Better trigger (if score <= 3) | Restriction issue |
|---|---|---|---|---|---|---|
| curse_of_djaf | Curse of Djaf | "Rampage" (positive) on enemies in the 35 m area, 13 s, one use | 3 | User ruling "Shooting enemy"; but a rampage on a shooting missile unit is a hunch (see C), and the unit form of the rule (no melee) is narrow. | keep unless the effect is proved | usage `health_above_50%`: caster must be below 50% health; not read. Fix: own `HealthPercent` <= 0.50 |

### air_drop_on_infantry (12 entries)

All fire when the nearest enemy unit with over 10 soldiers has its centre under 6 m from the caster's centre (user's test
constant). No friendly, visibility or flying-target test.

| Marker | Ability | Effect (short) | Score | Why (one line) | Better trigger (if score <= 3) | Restriction issue |
|---|---|---|---|---|---|---|
| bombs_air_only | Fire Bombs x2, Gyrobomber Bomb x2, Skyhammer Bomb x2, Nan-Gau Grenades, Sky-Junk Bomb | Bombs dropped while flying over | 4 | Dropping on top of a block of 10+ soldiers is the payoff; air-only honoured (`grounded`). Sky-Junk Bomb has no `grounded` flag in the game but the entry requires flight anyway (harmless). | | `climbing` / `phase_is_deployment` n/a |
| gyrocopter_bomb_anti_large | Gyrocopter Bomb (anti-large) | 100/100 damage, +50 vs large, 0 vs infantry | 3 | Built for monsters, but the pick demands over 10 soldiers, so it never goes at a large single-entity unit. | air-drop with the large class (`class_keys.large`) instead of a soldier count | none |
| drops_melee_forbidden | Death from Above, Undeath from Above, Drop Rocks x4 (incl. Chotec, Sundering), Wake of Fire, Drop Sphere of Tepok x2, Searing Torrent | Rocks, skulls, fire, spheres from a flying caster | 4 | Same drop logic; `no_melee` honoured. Drop Sphere of Tepok and Searing Torrent do not need flight (`air_only = false`). | | none |

---

## C. Game-mechanics questions

- Is `is_under_missile_attack()` readable and true on ENEMY units? (CLAUDE: proven only on our own units; the picker fails closed and the under-fire arm may never fire in practice.)
- Do Night Goblin Fanatics (Spinning Loons) damage friendly units? If yes, the fanatic releases need a friendly-fire check.
- Do bombardments (comets, lightning, rain of arrows) and the explosive squig damage our own units standing in the same fight? The bombardment family has no friendly check.
- Is the semantic of the usage flags "health_above_50%" and "health_below_25%" really "the ability cannot be cast while the caster's health is above 50% / below 25%"? (This is what the restriction audit and the brief assume; a player could confirm with Curse of Khsar.)
- What does Rampage on an ENEMY unit (Curse of Djaf) actually do? Is it useful on a shooting missile unit?
- Where does a summon appear when the ground target is an enemy position: on the enemy, or offset toward the caster (spawn type `unit_position_offset`)? Do "always affects self" summons (Blacktoof's Conjuration, Wake Da Idol, Transformation of Kadon, Call to Ceithin-Har / Gwindalor, Ritual of the Beast) use the ground position at all?
- Does a bomb dropped by an air-drop unit hit a flying enemy overhead, and do bombs hurt our own units under the caster?
- Is Cackle Fruit's slow on charge speed worth treating as a charge-only effect (rule 10), or is a damage blob moment acceptable?
- What does "Terror" (Eternal Gaze) do to a unit already in melee: does it route it, and which units are immune?
- Do "Winds of Magic recharge -140%" and "miscast chance +100%" matter on non-caster units (they should not), i.e. is the Lord/Hero class a safe proxy for "enemy wizard"?

---

## Summary

1. The tooltip sentences are mostly INCOMPLETE rather than wrong, but `enemy_ground_melee` is WRONG for about 15 of its 75 entries ("the summon is placed on its ground" is false for the curses, Heaven's Flash, Soulstealer and the loons); enemy_ground_melee_infantry hides its "not a Lord or Hero" exclusion; enemy_ground_shooting hides "not in melee".
2. enemy_engaged_or_shot is the weak family: a one-size trigger for 51 hexes that were never re-sorted by the round-123 rule 10 teaching; wind-of-magic / ability-clock / miscast hexes (about 9), speed cuts and roots (about 15), direct single-target damage (2) and Pageant of Shrikes score 2-3 and have named better families (enemy_commander_value, enemy_melee_or_fast, enemy_single_drain, enemy_ground_shooting).
3. enemy_blob is strong (4-5 for dragons, breaths, fireballs, arrow volleys, thrown bombs); the exceptions are the seven 1 m point shots (Executioner, Amber Bow, Goggly Glare, Gaze of Nagash, Hand of Gods, Vindictive Glare, Shem's Burning Gaze) which are snipers mis-filed as blobs (score 2), and Chain Lightning (3).
4. Restrictions not honoured: min_range for Cinderblast Shell, Cinderblast Cluster Bomb and Coruscating Blast (blob); the caster-health usage flags for Curse of Khsar and Curse of Djaf (health_above_50%) and Spinning Loons / Loons of Eight Peaks (health_below_25%); "always affects self" summons; the anti-large air-drop bomb cannot target a monster. All fixable with an own-health read or a min_range column.
5. The bombardment family (enemy_ground_melee_infantry, user ruling "I find it satisfying right now") and the air-drop family have no friendly check or soldier-count / value check unlike the later families; scored 3-4 and flagged only because the user asked for scores.
