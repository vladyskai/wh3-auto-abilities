# WH3 battle knowledge (research notes for the ability automation)

Compiled 2026-11-16. Sources are web pages (URLs) or game data (`gamedata\wh3\<table>`). Anything with no
source is marked ASSUMPTION. Web coverage was thin: several wikis returned 402/403/429, and most community
claims are single-poster statements. Treat web claims as hints, game data as fact, the mod's own field logs
(CLAUDE.md section 5) as stronger than both.

## 1. Mechanics that decide WHEN an ability pays off

**Charge bonus.** It is added to melee attack (and weapon damage) at the first hit after the charger stops, then
decays steadily. Players report about 10 s total: 80% left at 2 s, 20% left at 8 s, gone by about 9-10 s;
best pull-out at 6-8 s
(https://steamcommunity.com/app/1142710/discussions/0/4357872738329493783). A second thread agrees on "about
10 seconds", and says the bonus applies after the charger stops moving (https://steamcommunity.com/app/1142710/discussions/0/4038104984934184302 via
search snippet; the exact number is unconfirmed by any official page). Charge defence on the target negates
the bonus; units holding still without it may get "Braced"
(same Steam results). Downhill charges are much stronger (thread above). Impact damage depends on speed and mass (same thread).
Consequence: a melee-attack or damage buff pays most in the first seconds after impact, and a buff cast
earlier than the moment of impact is partly wasted if its duration is short. ASSUMPTION: the buff stacks with the
decaying charge bonus additively.

**Hit chance.** Player-quoted formula: 35 + melee attack - melee defence percent, clamped to 8..90
(https://steamcommunity.com/app/1142710/discussions/0/4357872738329493783 search snippet; fan-sourced, unverified). So +N melee attack is +N
points of hit chance, which matters most between 8% and 90%. Melee defence is the mirror (chance not to be hit)
(https://totalwarwarhammer.fandom.com/wiki/Units). The mod cannot read either live (CLAUDE.md section 9, memory
reading closed).

**Missile resistance and ward saves.** Missile block chance is a front-facing chance to stop a missile; ward
save is a flat chance to ignore damage; physical resistance does the same for non-magical damage; armour
reduces non-AP damage (https://gameslantern.com/article/warhammer-iii-damage-types-explained and
https://www.totalwar.com/?p=19917, titles only, not opened: ASSUMPTION on exact stacking order). Armour-piercing
ignores a share of armour, so armour buffs matter against non-AP and missile-heavy enemies. The mod already
treats AP-heavy attacks as armour-sensitive.

**Leadership, wavering, broken.** Leadership shows as a white bar below the health bar. It drops when
surrounded, facing terror, or when the Lord dies/is wounded; an empty bar means rout; a broken unit may rally in
a few seconds if not chased; chased or repeatedly broken units flee for good. Flank allies and a nearby Lord raise it; Lord
abilities can refill it or make a unit unbreakable
(https://www.gamepressure.com/totalwarwarhammer/leadership-and-unit-fatigue/z38a4f). No numeric thresholds
were found on the web: UNKNOWN. The exact wavering/broken thresholds (the mod uses the engine's own states,
not numbers) are not documented in any page opened.

**Fatigue and vigour.** Fatigue levels: fresh, active, tired, exhausted. Tired has no direct penalty; exhausted
slows melee/reloading and cavalry cannot charge effectively (same gamepressure page, a WH1-era page). Vigour is WH3's
renamed fatigue bar (ASSUMPTION; not verified on a web page). Game data `phases`: columns `freeze_fatigue` and
`fatigue_change_ratio` exist, so vigour abilities are phases with those fields. Standing ruling: no vigour
trigger (CLAUDE.md section 5).

**Durations and recharges.** Game data `phases.tsv` has per-phase `duration`; `unit_abilities` / special
ability rows carry the recharge. Whether recharge starts at cast or at effect end: the mod's field note says it
starts when the effect ENDS (Restore: 24 s + 60 s). No web source found; the field note is the only evidence.

**Casting with a wind-up; can the target escape.** A cast stops its moving caster only when the ability plays a cast
animation (`unit_special_abilities.wind_up_stance` not empty). Field, 4 of 4: Volley of High Arrows and Soporific
Breath (`cast_forward_short`) stopped their casters (2026-11-14); Book of Hoeth (2026-11-14) and Gaze of Malice (the
user's manual cast, 2026-11-17) have no stance and did not. ASSUMPTION level: good evidence, no documented rule. Since
round 168 the mod's stand-still gate follows it (228 of our 1,003 keys are animated). A moving target can still leave
the area before a delayed effect lands. Web
sources: none found. For the target escaping, ASSUMPTION: area effects with a delay (breaths, vortexes) are placed at the target's
position at click time, not tracked (`battle_vortexs.follow_target` is false for Purple Sun, Flame Storm,
Banishment: game data).

**Winds of Magic.** Each battle draws a random pool (never added to the campaign reserve), no draw for armies
without mages; the usable mana rises by 1 every few seconds, draining the pool up to its max; lord/hero spells
cost mana, hero skills cost none and have longer cooldowns
(https://www.gamepressure.com/total-war-warhammer-3/winds-of-magic-and-spells/z7f97a). Exact recharge rate:
not on the page. The mod's own WINDS map row (every 2 s) is the only way to measure it.

## 2. Area attacks

**Do vortexes hurt friends?** Game data `battle_vortexs`: 242 of 313 vortex rows have `affects_allies=true`
(71 false). Purple Sun of Xereus (all four variants), Flame Storm and Banishment all have `affects_allies=true`
AND `affects_enemies=true`. So these vortexes hit friendly units by the data. Whether the caster itself is hit:
UNKNOWN (no table field; the caster is a battle unit like any other, so ASSUMPTION: yes if it stands inside). A wiki fragment says most damage
spells can hit friends and spells that do not say so in their description
(Total War: Warhammer wiki, found via search; page text not fetched).

**Heading of wind/breath spells.** Winds are straight rectangles, breaths are cones. Wind direction can be set
by dragging the cursor after the click (WH2 feature, per forum; not confirmed for WH3).
A forum snippet notes WH2 winds can drift off the aimed heading, especially near walls. In the data, vortexes
use `launch_source = target_centre` (all Purple Sun/Flame Storm/Banishment rows), i.e. they spawn on the target, not the caster.
Heading from caster to target for a script-issued cast: ASSUMPTION (a scripted cast has no drag, so the engine
most likely uses the caster-to-target line).

**Random-walk vortexes.** Game data, selected rows:

| vortex | change_max_angle | move_change_freq | movement_speed | duration |
|---|---|---|---|---|
| Purple Sun (wh_main, base) | 360 | 1 | 2 | 11 |
| Purple Sun upgraded | 360 | 1 | 2 | 22 |
| Flame Storm (bound) | 360 | 1 | 2 | 27 |
| Banishment (bound) | 360 | 1 | 2 | 18 |
| Purple Sun large (wh3_dlc25) | 0 | 0 | 0 | 7 |
| Purple Sun small | 360 | 2 / 1 | 4 | 5 |

`move_change_freq` 1 and `change_max_angle` 360 mean the heading can change by up to 360 degrees about each second
(ASSUMPTION on units: seconds and degrees). Forums agree vortexes wander: "usually missing a lot of units" in WH2
(https://steamcommunity.com/app/594570/discussions/0/1738841319805262411 via search snippet), and in WH3 Flame
Storm is "now mostly stationary" (https://steamcommunity.com/app/1142710/discussions/0/7318962605502287050). Most vortex/wind spells
were reworked to leave entities alive (same thread). The large Purple Sun (angle 0, speed 0) is stationary.

**Expendable.** Fandom Units page: expendable units are fodder whose rout or death does not reduce other units'
leadership, unless they are the same unit type
(https://totalwarwarhammer.fandom.com/wiki/Units, via search summary). Patch 3.1 removed Expendable from Bretonnian Peasants and gave Knights a separate attribute
(https://videogames.si.com/news/total-war-warhammer-3-patch-notes-update-3-1). Pusbags are expendable (Lords
of the End Times guide, https://powerupgaming.co.uk/2026/09/25/total-war-warhammer-3-best-new-units-lords-of-the-end-times/).
Game data: `db_unit_attributes.tsv` has the key `expendable`.

## 3. How experienced players use abilities

Sourcing here is weak: no single comprehensive WH3 ability guide opened. What the pages supported:

- Save mana: do not spend the whole pool at battle start; one well-placed Wind of Death, Burning Head or Pit of
  Shades can wipe half an army (https://earlyguides.pages.dev/total-war-warhammer-iii/tips via search summary).
- Cavalry: pull out 6-8 s after impact and recharge, because the charge bonus decays
  (https://steamcommunity.com/app/1142710/discussions/0/4357872738329493783).
- Lord abilities that refill leadership or make units unbreakable are the standard answer to terror and
  flanking (https://www.gamepressure.com/totalwarwarhammer/leadership-and-unit-fatigue/z38a4f).
- Health bars show 75/50/25% ticks to time health-triggered abilities
  (https://www.totalwar.com/?p=16273).
- AI hit by a couple of spells or missile fire is said to commit to attack (single Reddit anecdote, unverified).
- AI falls for ambushes frequently (guide-site claim, unverified).

General principles widely held (ASSUMPTION, matches design logic and the mod's own ruling 10, not a cited
source): buff just before impact and again after if short; hex the enemy unit your strongest unit is fighting;
debuff the target of your missiles; save escapes and unbreakable for the panic moment; chain stuns on the
dangerous monster; AoE on clumped AI. Specific tips for Deadly Onslaught, the Potion of Speed, arcane items and
lore-attribute spells: nothing citable was found.

AI behaviours relevant to automatic casting:

- AI clumps and gets stuck; players use AoE on the clusters (https://www.ludo.guide/guide/total-war-warhammer-3/exploiting-ai-weaknesses via search summary).
- Developers' known issues: the AI General misuses fire-at-will / skirmish for units it controls, so missile
  cavalry waste shots (Steam known-issues note, via search).
- Kiting: a commenter says restrictions exist because kiting forever "cheeses" battles (single Steam reply). A
  campaign-AI-runs-away complaint is about map play, not battle.
- "AI chases a single fast unit": no source found. UNKNOWN.

## 4. Assumption table

| Assumption | Verdict | Source |
|---|---|---|
| A caster is not hurt by its own breath or vortex | UNKNOWN, leaning refuted for vortexes: Purple Sun, Flame Storm, Banishment have `affects_allies=true`; the caster is a unit like others, so standing inside likely hurts it. No direct source for the caster | game data: battle_vortexs (affects_allies) |
| Wind spells travel from the caster's side through the target | UNKNOWN for scripted casts. Interactive winds take a drag heading (WH2, unconfirmed WH3); vortex rows spawn on `target_centre`, not at the caster | Total War: Warhammer wiki snippet; game data: battle_vortexs launch_source |
| `change_max_angle` is a random heading change of up to that angle | PLAUSIBLE, not confirmed. Data fits: 360 with `move_change_freq` 1 for the wandering vortexes, 0 / 0 for the stationary large Purple Sun. Forums confirm vortexes wander | game data: battle_vortexs; Steam WH3 thread 7318962605502287050 |
| Befuddlement of Mischiefs cannot freeze flying units | UNKNOWN. The phase is a negative 11 s phase with `cant_move=true`, affects enemies only. The invalid-target table (103 rows use `flying_currently`) has NO row for this ability, so by data flying units are valid targets. Whether `cant_move` holds a flier is not documented | game data: phases (befuddlement_of_mischiefs), special_ability_to_invalid_target_flags_tables |
| The `expendable` attribute means other units do not lose leadership when it dies | CONFIRMED in wording, with a limit: not for units of the same type. Attribute exists in WH3 data; Bretonnia peasants lost it in 3.1 | Fandom Units page; patch 3.1 notes; game data: db_unit_attributes |
| An ability's recharge starts after its effect ends | CONFIRMED by the mod's own field note only (Restore 24 s + 60 s). No web source | CLAUDE.md section 5 (field 2026-11-13) |
| Issuing a self-cast ability does not stop the unit's current move or attack order | UNKNOWN. Aimed casts STOP a moving caster (field 2026-11-14); self-centred casts were not tested in any source found. Mod design assumes they do not stop it | CLAUDE.md section 5; no web source |
| A unit that lands from flight to fight stops counting as flying | UNKNOWN. Consistent with the mod's field correction (round 159: a flier that lands is not flying) and with `flying_currently` as a live state in target flags. No web source | CLAUDE.md section 9 round 159; game data: invalid_target flags |

## Contradictions with the mod's assumptions

- Purple Sun, Flame Storm and Banishment really are two-sided (`affects_allies=true`), so friendly-fire safety
  margins are justified for them. 71 vortex rows have `affects_allies=false`; those could be cast without a
  friendly check (the mod would need the row to key the ability).
- Vortex heading data: wandering vortexes change heading every second by up to 360 degrees; a "safe" cast aimed at a
  blob may wander onto friends within seconds. The large Purple Sun does not wander.
- Charge bonus decays over about 10 s: a charge-timed buff is only valuable at impact, favouring `charge_or_melee`
  triggers fired at contact over firing on approach.
