# Overnight audit, 2026-11-16 / 17

The overnight request was to check every ability one by one, against game knowledge and common sense, on three points:
the card note, the trigger's quality, and the restrictions. It also asked for feature ideas and a check of the ALL
button's tooltip.

**How it was done:**
- Six reviewers, each reading one group of trigger families. Their reports are in `docs\audit_night\review_g*.md`:
  723 table rows covering all 946 entries (some rows cover several entries).
- One research pass on battle mechanics: `docs\WH3_battle_knowledge.md`.
- A script that checks every game restriction flag against what the mod enforces: `tools\audit_restrictions.py` ->
  `docs\WH3_restriction_audit_2026-11-17.md`.
- I checked the claims that led to code changes in the source myself before acting on them.

**What shipped tonight:** round 165 (`docs\WH3_round165_night_audit.md`); pack md5 `df53a1b19192d4afecf132049cecb6e0`.
No trigger was redesigned: every trigger proposal below waits for your ruling.

## 1. The card note (point 1)

**The finding.** The note you see on the ability card is the static line "Automatic: click the M/A badge to switch
automatic use on or off". It does not say when the ability fires, for any ability. Round 93 wrote one sentence per
trigger family, but nothing in the mod ever displays it (`ability.tip` has no reader). So until tonight no card ever told
you when its ability fires.

**Several of those unseen sentences were also wrong or incomplete:**
- `melee_unwavering` (299 entries) hid "and not wavering".
- The charge families hid the real window: 12 to 60 m from the target, at most 4 s from contact.
- `wavering_self_or_ally` and `verminking_wavering` hid "the ally must be in melee".
- `melee_or_shooting_self_or_ally` stopped mid-sentence.
- The aura sentences said "near it" where the code uses 70% of the radius.
- The enemy sentences hid "visible", "standing still" and the 10 m safety margins.
- Two sentences carried filler: "and the summon is cast on it", "casts immediately on that evaluation - no delay at all".

**The fix (shipped):**
- **The sentences:** one corrected sentence per family, written from what the code actually tests.
- **The numbers:** each ability's own values are filled in: its range, aura radius, blast clearance, wave widths, charge
  window and execute line.
- **The clauses:** the game's restrictions are added as clauses (for example "not below 50% health", "never on a flying
  unit").
- **Where it shows:** the result is the hover tooltip of the ability's own M/A badge.
- **The full list:** all 946 cards are in the Cards sheet of workbook v49.

| Ability | Card |
|---|---|
| Deadly Onslaught | fires when this unit runs at the enemy it is attacking, 12 to 60 m away and at most 4 s from contact, or when it is in melee |
| Bloodstorm-type blasts | fires when this unit is in melee and not wavering |
| Bloodbeast | fires when this unit is in melee and not wavering, with none of your other units within 25 m of it |
| Wrath of Manann | fires its wave, while this unit and the target stand still, at the visible enemy within 70 m whose path holds the most enemy value, with none of your other units within 16 m of the path at its start, widening to 33 m at its end; never a flying target |
| Helping Hand | fires when this unit is in melee and not wavering, on the closest friendly unit within 35 m; the ally must be a Lord or Hero |
| Entice | fires when this unit is in melee and not wavering; not below 50% health |

**Needs your eyes next battle:** hover one M/A badge. The ALL button's tooltip works in game, but the M/A badge uses a
different template. If nothing shows, tell me and I will move the text (two options: a different badge template, or
appending to the ability's own tooltip).

**What a card leaves out:** the shared gates every ability has. These are:
- the ability ready;
- not routing;
- the 2 s retry guard;
- one cast at a time per unit.

They would repeat on all 946 cards, so I left them out (filler). If you want "never while routing" on every card, it is
one line to add.

## 2. Trigger quality (point 2)

Each row was scored 1 to 5. 5 means I am sure this is the best trigger the game's reads allow. Lower means a better
trigger probably exists, or the trigger misses the moment the effect pays.

| Score | Rows | Meaning |
|---:|---:|---|
| 5 | 249 | best feasible (Deadly Onslaught, pure charge buffs, Shield of Chaqua under fire, the heals at 75%) |
| 4 | 345 | right, with a small loss (an aura that only helps who stands near at the cast, a slightly early cast) |
| 3 | 95 | works, but a clearly better trigger exists |
| 2 | 30 | wrong moment for the effect |
| 1 | 4 | no link between trigger and effect |

The full tables are in the six review files. The main groups at 3 or below follow. **Every one needs your ruling
(rule 9); none was changed.**

### A. Wrong moment (scores 1-2)

| Abilities | Now | Why it is wrong | Proposal |
|---|---|---|---|
| Horn of the Wild Hunt, Potion of Foolhardiness, Ursun's Roar (1 key), Red Fury, Waaagh! (1 key), Rock of Inevitability, Wissenland Runefang | in melee | charge bonus or enemy charge-speed cut: spent once the clash has started | `charge_or_melee` (Ursun's Roar and Waaagh! share an entry with plain melee keys, so they need their own entries) |
| Black Staff, Forbidden Rod, Earthing Rod, Hagtree Fetish, Master of the Black Arts, Maw Shard, Power Familiar, Wand of Jet | in melee | winds, miscast or spell-mastery items: pay when the bearer casts, not when it fights | `when_ready` (like the other 21 winds items), or keep |
| Rock Eye, Watched by the Watcher | in melee | spotting / reveal: useless when the enemy is already in contact | `when_ready`, or fire when an enemy unit is hidden (the visibility read exists) |
| Null Stone, Sceptre of Stability, Locus of Abjuration, Necrotic Phylactery | melee / 75% health | anti-magic wards: pay when enemy spells land (no read) | Lord/Hero proxy as for the Leach Orb, or keep |
| 7 point-blast "blob" shots (Executioner, Amber Bow, Goggly Glare, Gaze of Nagash, Hand of Gods, Vindictive Glare, Shem's Burning Gaze) | `enemy_blob` | a 1 m blast is a sniper shot; the blob rule never looks at large or single targets | `enemy_large_shot` (your "AP shots: large first" ruling) |
| Cube of Darkness, Scroll of Leeching, Vortex Shard, Trickster's Pendant / Shard, Silence the Prey, Power Siphon, Black Tongue | enemy in melee or under fire | anti-caster hexes fired at any fighting unit | `enemy_commander_value` (the caster proxy) |
| Don't Even Try It, Muster of Malevolents | same | character killers fired at the closest fighting unit | `enemy_single_drain` |
| Pageant of Shrikes, Chalice of Dark Rain | same | accuracy debuffs: only matter on a shooting enemy | `enemy_ground_shooting`-style pick |
| Transfix | enemy Lord/Hero in melee | the game accepts it only when the target's morale is at or below half | add "the target is wavering" (an approximation) |
| Hammer of Smednir | blast rule | its only effect is a slow (rule 10) | the charge rule, like Wind Blast (you ruled "Keep the blast rule" in round 163; listed for completeness) |
| Inspired Marksmanship I-III | closest missile ally | fires at battle start on an idle unit | closest missile ally that is shooting (the picker exists) |
| Overseer of the Unseen, Whiplash! | closest eligible ally | fire at battle start, no condition | ally in melee (or about to charge) |
| Fury of Khaine, Verminous Fury | ally melee buff, armed by default | grant Rampage (the unit leaves your control), possibly on an archer | keep them on M by default, or a melee-only, non-missile target |

### B. Works, but better exists (score 3), the main groups

- **`ally_melee_buff` (14, armed by default)** casts on the closest ally even when that ally is idle (Inspired Defence /
  Assault, Favour of the Fay, Hellish Vigour, Orcs are da Best!...). Proposal: the closest ally that is in melee (the
  picker exists).
- **Commanding Presence and Fury of Ulric:**
  - **What the code does:** the ally arm requires an ally that is in melee AND wavering.
  - **Your ruling** (Commanding Presence, questionnaire 36): "Not related to melee, only to morale. The trigger should be
    when lord or nearby unit are wavering."
  - **Why it matters:** the code contradicts your ruling, and I cannot find a later ruling that added the melee condition.
  - **My recommendation:** drop the melee condition, to match your words. Not changed tonight because both are armed by
    default and the change makes them fire more often.
- **Cannot-die effects** (Refuse to Die, Slayer for Chaos, Daemonshield, Skar's Kraken-Killer) burn on first contact or
  at 75%. Proposal: in melee and low health (like Hag's Denial at 10%, or a 50% line).
- **Large-only bonuses** (Creature-Killer, Ostermark Runefang, Steppe Hunter's Horn, Masterful / Colossal Strike) fire
  against any enemy. Proposal: in melee with a large enemy engaged (the engagement set and the large set exist).
- **Missile-block or armour effects** on melee only (Dispatch the Swarm x2, Rune of Oath and Steel). Proposal:
  `melee_or_under_fire`.
- **Friend-targeted heals cast only on the caster:**
  - **Affected:** Blood Chalice of Bathori, Breath of Darkness x2, Mantra of Invigoration.
  - **The gap:** the ally side is wasted.
  - **Proposal:** an ally heal with the game's target class (Lords/Heroes; undead; Tiger Warriors needs a new set).
- **Roots and speed cuts on "enemy in melee or under fire"** (11 nets and roots, Book of Secrets, Looming Dread...).
  Proposal: `enemy_melee_or_fast` (rule 10).
- **Wanderers that almost never fire:**
  - **Affected:** Da Boss' Loons (98 m ring), Sandstorm, Lamprey's Bite, Ruination of Cities.
  - **Reviewer's claim:** their safety ring also counts the caster.
  - **My check:** that is round 162's design (the caster stands near a wanderer's path). Your "Caster doesn't count"
    ruling covered waves only.
  - **Question for you:** should it cover wanderers too?
- **No minimum value for waves, cones and strikes:** a limited-use wave can go on a few Skavenslaves. Proposal: the blob
  trash rule (3 packed blocks) for waves too.
- **Single-use items fired early:**
  - **Affected:** Berry Wine (a 45% heal fired at 75%), Horn of Vaul, Hunter's Call, Land Mine (3 charges in one fight),
    Grut's Sickle.
  - **Proposal:** a stricter line (55% for Berry Wine) or "at least 3 engaged units".
- **Winds items where "when ready" is weakest:**
  - **Power Stone and Chromatic Tome:** they cut recharge by 20% while adding reserve.
  - **Snowflake Pendant, Stave of Avelorn:** miscast protection that expires before the first spell.
  - **Proposal:** fire when the winds pool is low (the WINDS map row is read every 2 s).
- **Other single cases:**
  - Foe-Seeker on `tired`: your ruling; its speed buffs pay on a charge;
  - Shield of Thorns: the charge arm fires before it can reflect anything;
  - Blooood!: fires on any short move;
  - Rock Bottom: no guard for its 350 self-damage;
  - Eye of Khorne: may finish a 3-man remnant with its single use;
  - Star of Avelorn: reach limited to 10 m from the caster;
  - Terrorgheist Skull: a recharge reducer on melee.

## 3. Restrictions (point 3)

### Fixed tonight (shipped in round 165)

| Ability | The game's rule | What the mod now does |
|---|---|---|
| Entice | refused below 50% health | holds below 50% |
| Favoured by the Matriarch, both Loons | refused below 25% health | holds below 25% |
| Curse of Khsar, Curse of Djaf | refused above 50% health | fires only at or below 50% (until now they were refused at full health) |
| Daemon Flask of Ashak, Feaster of Souls | refused in flight | holds while flying |
| Eye of the Storm | large casters only | holds unless large (the Storm Dragon form) |
| Stay Here, I'll Get Help! | refused while the caster fights | holds while in melee (the rule table, not a new trigger) |
| Helping Hand | target must be a Lord or Hero | picks only a Lord or Hero |
| Captain of the Phoenix Guard | never a Lord, Hero or large unit | skips them |
| Entrenchment | never a flying target | skips a flying ally |
| Whiplash! | never a Lord or Hero | skips them |

All of these come from two tables GENERATED from the game data, and the build refuses a pack whose tables differ. In
total 60 keys carry a caster rule the mod checks live; 50 of them were already honoured by their families, 10 are
new.

### Bugs found and fixed

- **The 7 ground-only WW abilities were cast in the wrong form** (rounds 162-164: Blue Fire of Chaos x2, Siegebreaker,
  Heaven's Gate, Lamprey's Bite, Flesh-eating Scarabs, Magma Storm). The unit form was sent, so the engine may have
  refused them, or cast them wrongly. My round-164 test counted both forms together and missed it. Now fixed and tested
  separately.
- **The two sweeps had no range bound:** Disembowelling Sweep (6 m) and Flesh-eating Scarabs (3 m) fell back to a 52 m
  default. Now 4 m and 2 m, and the build refuses any range without its bound.

### Still not honoured (no live read, or needs a set the game data does not give cleanly)

| Rule | Abilities | Why not |
|---|---|---|
| target morale at or below half (`morale_is_higher_than_half_of_base_morale`) | Transfix, Ghostly Howl | no morale-value read; "wavering" is an approximation (proposal in 2A) |
| target must be a spellcaster (`hasnt_casting_ability`) | Dweomer Leach Orb, Slann Gold | the mod uses Lord/Hero as a proxy; a GENERATED set of units owning a spell is possible (a proposal) |
| Lizardmen / Tiger Warriors / Moulder monsters / Squigs only | Cold-Blooded, Focus Instincts, Predatory Instincts, the Prayers, Remouldered, Shock Collar, Empowering Shrooms | the game's grouping is not a clean table field; I would need to derive the sets and show them to you first |
| `hp_replenish_cap_reached` | 6 heals | no read; the engine refuses and the mod backs off (harmless) |
| `enemies_in_intercept_range` | Bugman's XXXXXX | the intercept distance is not in the table; proposal: no enemy within its range |
| `ground_unit` / `flying_unit` (caster) | Eye of the Storm, Wrath of the Storm | the flag may mean "a unit type that can fly" or "flying now"; opposite answers for a landed dragon, so I did not guess |
| `cannot_perform_missile_attack` | Boom!, Blooood!, Inspired Marksmanship, Deranged Munitions | covered in practice by the shooting reads (these fire only on shooters) |
| Trophy Heads' Daemon Wings key | Trophy Heads | the entry's "Lords and Heroes only" class comes from its other key; the Daemon Wings key does not have it. Needs the entry split |
| visibility | the older enemy pickers (melee, fast, wavering, missile) | they can pick an enemy hidden in fog; the newer blob and shot families check visibility. A one-line addition, for your ruling |

## 4. The ALL button's tooltip

- **The current text:** "ALL: arm or disarm every automatic ability of the selected unit(s). If any of them is on M, all
  go to A (automatic); if all are already on A, all go to M (manual). The button stays pressed while all of them are on
  A."
- **Verdict:** accurate. I checked it against `FOURTH.all_click`, which does exactly this, and the pressed state matches.
- **A tighter version, if you want it:** "ALL: if any automatic ability of the selected unit(s) is on M, set all to A;
  otherwise set all to M. Pressed while all are on A." Not changed: your call.

## 5. Feature ideas

1. **"Waiting for" line.** The selected unit's badge could show why its ability is not firing now: "waiting: no enemy
   in melee within 35 m" or "held: refused below 50% health". The mod already computes these reasons for the log. The
   cost is a tooltip refresh, about once a second, for the selected unit only.
2. **Army-wide ALL.** One click arms or disarms every unit's abilities. A second round button beside ALL is the
   simplest, since modifier clicks are hard to read.
3. **Per-ability army switch.** For example "never auto-cast Rampage abilities this battle". This is a right-click on a
   badge if the engine reports right-clicks (to check).
4. **Priority when two abilities compete for one unit.** One cast at a time per unit, so for example Potion of Speed
   could fire and then Onslaught waits 2.5 s. A small per-family priority would let the charge buff win the charge
   moment.
5. **Learn the real recharge from the button.** When the selected unit's button turns ready, the mod knows the true
   recharge, including campaign bonuses. This was option a in 2026-11-03; it would shorten the 37 s over-hold you have
   in your campaign.
6. **End-of-battle summary.** One block in the log per ability: casts accepted, refused, held by which rule. It would
   make QA battles much faster to read.
7. **Remember arming across battles,** per unit type. This needs a way to save from battle script, not checked yet.
8. **Safer defaults for Rampage and self-damage abilities.** They stay on M even in families that start armed (Fury of
   Khaine, Verminous Fury, Rock Bottom).

## 6. Battle knowledge and the assumptions behind the triggers

`docs\WH3_battle_knowledge.md` is the research file. Web sources were thin (several wikis blocked access, and most
claims come from single forum posts); the game data gave the solid answers. CLAUDE.md now points to it so every session
reads it.

| Assumption the mod relies on | Status | What would settle it |
|---|---|---|
| Vortexes hit our own units | CONFIRMED by data: 242 of 313 vortex rows affect allies (Purple Sun, Flame Storm, Banishment) | - |
| Wanderers turn up to 360 degrees about every second at 2 m/s | CONFIRMED by data (matches the 95% simulation) | - |
| A vortex spawns at the target, not the caster | CONFIRMED by data (`launch_source = target_centre`) | - |
| The charge bonus fades over about 9-10 s after impact | one forum source | a field test is not worth it: the charge triggers fire before impact anyway |
| A caster is not hurt by its own breath | UNKNOWN (no data field) | one battle: Blue Fire or Pink Fire next to its own caster, watch its health |
| A self-cast does not interrupt the unit's current order | UNKNOWN | watch a charging unit when Deadly Onslaught fires |
| A flier that lands to fight is "not flying" | UNKNOWN (the mod assumes yes) | the map log's flying column on a dragon in melee |
| "Broken" morale equals routing | ASSUMPTION | if true, Iron-Handed Captain (`ally_broken`) can never fire, because the picker skips routing allies first. One log line would tell |
| Can a friend-targeted ability be cast on its own caster? | UNKNOWN | Eat da Runts' self arm and Blood Sacrifice depend on it |
| Siegebreaker harms units in the field | UNKNOWN (the game only lists siege effects) | one cast in a field battle |
| Expendable units cost other unit types no morale | data and forum agree | - |

## 7. What I need from you

1. **Next battle:**
   - hover an M/A badge: is the card shown?
   - watch Blue Fire, Siegebreaker or Magma Storm cast (now in the ground form).
2. **Rulings:**
   - the Commanding Presence / Fury of Ulric melee condition (recommendation: drop it, matching your words);
   - the trigger groups in section 2, as many as you want to take, in batches as usual;
   - visibility for the older enemy pickers (recommendation: add it);
   - "Caster doesn't count" for wanderers too?
3. **Optional:** the ALL tooltip's tighter wording; which feature ideas to build (my pick: 1, then 6).
