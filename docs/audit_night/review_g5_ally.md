# Review G5: ally-targeted and aura families (night audit 2026-11-16/17)

Scope: 30 families, 90 entries. Read: `FOURTH.ab_pick_ally` / `ab_filter_ok` / `class_keys`, `ah_pick` / `ah_pick_where`,
`evaluate_*` of every family, `TRIGGER_TIP`, `DEFAULT_ON_TRIGGERS`, the poll's per-entry slots (`ab_range_m`, `fa_bound_m`,
`ah_range_m`), `fact_sheet_open.py` for all 98 keys, the restriction audit, the tracker rulings.

Armed by default (`DEFAULT_ON_TRIGGERS`) in this scope: ally_melee_buff, wavering_aura, wavering_self_or_ally,
wavering_ally_range, ally_wavering, melee_or_wavering_aura, health_aura_ally, ally_heal, health_aura_ground, ally_ammo_low.
Every other family here starts on M.

Common facts used below (from the code):
- `ab_pick_ally` skips: the caster, dead units, `is_routing()` units; then the family rule; the bound is
  `ab_range_m` = floor(0.70 x cast range) by `unit_distance` (edge to edge); an unreadable distance passes (fail-open).
- Aura families (`fa_bound_m`) use floor(0.70 x effect_range): 35 m gives 24 m, 55 m gives 38 m, 15 m gives 10 m; `aura_real = -1`
  means the whole army; an entry with no `aura_real` has no aura (the caster only).
- `FOURTH.wavering()` counts only an exact `true`; routing units never count as wavering allies.

---------------------------------------------------------------------------------------------------------------------

## A. Families

### ally_melee_buff (14 entries, armed by default)
- Current: "When armed, fires when this unit is in melee, on an ally in range"
- Code: caster `is_in_melee()`, not routing, `wavering ~= true` (an unreadable morale still passes). Target: the CLOSEST ally
  (alive, not routing) inside floor(0.70 x cast range) (35 / 52 / 70 / 105 / 140 m). The ally does NOT need to be in melee,
  and there is no class filter. Cast form: unit form on the ally.
- Verdict: INCOMPLETE (omits "not wavering" and "closest"; the real gap is the picker, see B).
- Proposed: "When armed, fires when this unit is in melee and not wavering, on the closest non-routing ally in range"
- Append for Helping Hand (once fixed): "; Lords and Heroes only".

### melee_or_shooting_aura (10)
- Current: "When armed, fires when this unit or a friendly unit near it is in melee or shooting"
- Code: (1) caster in melee (wavering is allowed here), or (2) the closest other friendly (alive, not routing) in melee within
  `METALLURGY_RANGE_M` = 24 m, or (3) the caster or any friendly (alive, not routing) within the aura bound (24 m) that is
  shooting past its cast point (first shot + 0.5 x reload, and able to shoot now). Cast on the caster. One engaged unit is enough.
- Verdict: INCOMPLETE ("near" is 24 m; "shooting" is "past its cast point").
- Proposed: "When armed, fires on this unit when it, or a friendly unit within 70% of its aura radius, is in melee or shooting past its cast point"

### wavering_aura (9, armed by default)
- Current: "When armed, fires when this unit or a friendly unit near it is wavering"
- Code: not routing; caster wavering (exact true) OR the closest other friendly (alive, not routing) wavering within the aura
  bound (24 m). `aura_real = -1` (Unholy Clamour): any wavering friendly anywhere. No `aura_real` (Mirror Cold-Blooded):
  the caster only. Cast on the caster.
- Verdict: INCOMPLETE (hides the army-wide and self-only entries, and the routing exclusion).
- Proposed: "When armed, fires on this unit when it, or a non-routing friendly unit within 70% of its aura radius, is wavering"
- Append for Unholy Clamour: "; a wavering friendly unit anywhere on the field". Append for Mirror (Cold-Blooded): "; this unit only".

### health_aura_ally (9, armed by default)
- Current: "When armed, fires when this unit or a friendly unit in range is at or below 75% health, cast on it"
- Code: `ah_pick`: the caster or any alive non-routing friendly within 70% of the cast range (42 m for Berry Wine, 140 m for
  the 200 m entries) with `health_pct <= 75`; the LOWEST health wins (the caster wins ties as the first candidate); unit-form
  cast on the chosen unit (the caster included).
- Verdict: EXACT (add lowest first and not routing).
- Proposed: "When armed, fires on the lowest-health unit (this unit or a non-routing friendly unit in range) once it is at or below 75% health"

### allies_firing_aura (8)
- Current: "When armed, fires when this unit or a friendly unit near it is shooting"
- Code: at least `FIRING_AURA_MIN` = 1 unit (the caster counts) that is shooting past its cast point and able to shoot
  now, among the caster and the other alive non-routing friendlies within the aura bound (24 m for the 35 m entries, 38 m
  for the 55 m entries). Cast centred on the caster (Ballistics Calibration: ground at the caster's feet). User ruling round 131.
- Verdict: INCOMPLETE ("near" and "past its cast point").
- Proposed: "When armed, fires when this unit or a friendly unit within 70% of its aura radius is shooting past its cast point, centred on this unit"

### wavering_ally_range (6, armed by default)
- Current: "When armed, fires when an ally in range is wavering"
- Code: not routing (caster); the closest ally (alive, not routing, `wavering == true`) inside 70% of the cast range
  (42 / 70 / 140 m); cast on that ally. The caster's own morale and melee state are not read.
- Verdict: EXACT (name "closest" and "not routing").
- Proposed: "When armed, fires on the closest non-routing wavering friendly unit in range"

### health_aura_ground (3, armed by default)
- Current: "When armed, fires when this unit or a friendly unit in its area is at or below 75% health, placed on the ground under it"
- Code: `ah_pick` with reach = aura bound (10 m for Star of Avelorn, 24 m for the 35 m entries), not the cast range; lowest
  health wins; ground form under the chosen unit. "Under it" means under the CHOSEN (lowest) unit.
- Verdict: EXACT in effect, ambiguous "it".
- Proposed: "When armed, fires when this unit or a non-routing friendly unit within 70% of its area radius is at or below 75% health, on the ground under the lowest-health one"

### ally_missile (3)
- Current: "When armed, fires on a missile-capable ally in range"
- Code: the closest alive non-routing ally whose `type()` is in the generated missile set (primary_missile_weapon present),
  inside 70 m. No shooting, ammo or enemy condition at all: it fires the moment the ability is ready.
- Verdict: EXACT (the sentence is honest; the trigger is the weak part).
- Proposed: keep, or after a redesign: "When armed, fires on the closest missile-capable ally in range that is shooting past its cast point"

### ally_heal (3, armed by default)
- Current: "When armed, fires on the lowest-health ally in range when it is at or below 75% health"
- Code: `ab_pick_ally` family heal: the caster is never a candidate; alive, non-routing, `health_pct <= 75`, lowest wins, in range
  (35 m or 70 m); cast on the ally.
- Verdict: EXACT (add "other than this unit").
- Proposed: "When armed, fires on the lowest-health friendly unit in range other than this one, once it is at or below 75% health"

### ally_ammo_low (3, armed by default)
- Current: "When armed, fires on a shooting ally in range with 70% or less of its ammunition left (the lowest first)"
- Code: ally shooting now (firing flag, `can_shoot_now`), ammo fraction <= 0.70, not refilled in the last 12 s (claim table),
  inside 70 m; least ammo wins. The caster is never a candidate. User ruling round 130.
- Verdict: INCOMPLETE (the 12 s claim is silent).
- Proposed: "When armed, fires on the shooting friendly unit in range with the least ammunition, once it is at 70% or less and was not refilled in the last 12 s"

### wavering_self_or_ally (2, armed by default)
- Current: "When armed, fires when this unit or an ally in range is wavering"
- Code: caster wavering (exact true) OR the closest ally within 24 m that is BOTH in melee AND wavering and not routing. The
  melee requirement is hidden. User wording for Commanding Presence (2026-10): "Not related to melee, only to morale. The trigger
  should be when lord or nearby unit are wavering." The code adds a melee condition the quote does not contain.
- Verdict: WRONG for the sentence (it hides a condition) and divergent from the quoted ruling.
- Proposed: "When armed, fires on this unit when it is wavering, or when a friendly unit within 70% of its aura radius is both in melee and wavering"

### melee_or_wavering_aura (2, armed by default)
- Current: "When armed, fires when this unit or a friendly unit near it is in melee or wavering"
- Code: caster in melee or wavering (not routing); else the closest alive non-routing friendly within 24 m that is in melee
  or wavering. User ruling 2026-11-09: "The general or any friendly unit within 24m is in melee or wavering."
- Verdict: INCOMPLETE ("near" = 24 m).
- Proposed: "When armed, fires on this unit when it, or a non-routing friendly unit within 70% of its aura radius, is in melee or wavering"

### melee_or_shooting_self_or_ally (2)
- Current: "... otherwise on the closest friendly unit in range that is" (the sentence stops mid-clause)
- Code: caster in melee and not wavering (not routing) -> self; else caster shooting past cast point -> self (no morale check);
  else the closest ally within 140 m that is in melee or shooting past its cast point.
- Verdict: INCOMPLETE (grammar broken, "not wavering" missing).
- Proposed: "When armed, fires on this unit when it is in melee (not wavering) or shooting past its cast point, otherwise on the closest friendly unit in range that is"

### ally_wavering (2, armed by default)
- Current: "When armed, fires on a wavering ally in range"
- Code: identical to wavering_ally_range through the shared picker (closest wavering non-routing ally, 70 m).
- Verdict: EXACT.
- Proposed: "When armed, fires on the closest non-routing wavering friendly unit in range"

### verminking_wavering (1)
- Current: "When armed, fires when an ally in range is wavering"
- Code: the closest alive non-routing ally within 24 m (`VERMINKING_RANGE_M`) that is in melee AND wavering; cast on the caster.
  User-designed (2026-10-08): "fire when an ally in range is in melee and wavering; cast on self".
- Verdict: WRONG (omits "in melee" and "cast on this unit").
- Proposed: "When armed, fires on this unit when a non-routing friendly unit within 70% of its aura radius is in melee and wavering"

### self_or_ally_shooting (1)
- Current: "When armed, fires on this unit when it is shooting, otherwise on the closest friendly unit in range that is shooting"
- Code: caster shooting past cast point (not routing) -> self; else closest ally within 70 m shooting past cast point.
- Verdict: EXACT (add "past its cast point").
- Proposed: "When armed, fires on this unit when it is shooting past its cast point, otherwise on the closest friendly unit in range that is"

### melee_or_shooting_into_melee (1)
- Current: "When armed, fires when this unit is in melee, or is shooting at an enemy that is in melee"
- Code: in melee, not wavering, not routing; OR (not wavering, not routing) shooting past its cast point at a current target that is
  in melee. Cast on self.
- Verdict: INCOMPLETE ("not wavering").
- Proposed: "When armed and not wavering, fires when this unit is in melee, or is shooting past its cast point at an enemy that is in melee"

### melee_or_self_or_ally_shooting (1)
- Current: "When armed, fires on this unit in melee or when it is shooting, otherwise on the closest friendly unit in range that is shooting"
- Code: in melee, not wavering -> self; else the self_or_ally_shooting rule.
- Verdict: INCOMPLETE ("not wavering"; "past its cast point").
- Proposed: "When armed, fires on this unit when it is in melee (not wavering) or shooting past its cast point, otherwise on the closest friendly unit in range that is shooting"

### ground_ally_before_range (1)
- Current: "When armed, fires under a friendly missile unit when the enemy is just out of its range"
- Code: the caster or the closest friendly (alive, not routing, within 175 m) missile unit that is out of melee, has ammo, has NO
  enemy inside its own missile range and the nearest enemy inside range x 1.35; ground cast under it. User ruling round 142.
- Verdict: EXACT (add "with ammunition, out of melee, the caster included").
- Proposed: "When armed, fires on the ground under the closest friendly missile unit (this one included) that has ammunition, is out of melee, and has an enemy just beyond its range"

### ally_winds (1)
- Current: "When armed, fires on the ally with the most hit points remaining, cast on that ally"
- Code: any alive non-routing ally within 70 m with a readable HealthValue; the highest HealthValue wins. Nothing else.
- Verdict: EXACT (add "other than this unit").
- Proposed: keep, plus "other than this unit".

### ally_warmachine_heal / ally_hellforged_heal / ally_monster_heal / ally_construct_heal (1 each)
- Current: "When armed, fires on the lowest-health <class> ally in range that is at or below 75% health"
- Code: ally_heal plus a class filter from the generated sets (warmachine 68, hellforged 13, monster 235 by caste, construct 29).
- Verdict: EXACT.
- Proposed: keep ("other than this unit" optional). Monster entry: see B (moulder monsters are not excluded).

### ally_overseer (1)
- Current: "When armed, fires on a non-commander, non-large ally in range"
- Code: the closest non-routing ally of the generated 918-key set, EXCLUDING any ally with `is_currently_flying() == true`.
  No other condition.
- Verdict: INCOMPLETE (omits "not flying").
- Proposed: "When armed, fires on the closest non-flying ally in range that is neither a Lord/Hero nor a large unit"

### ally_beast (1)
- Current: "When armed, fires on a beast ally in range"
- Code: the closest non-routing ally whose type is in the war_beast caste set (55 keys). No other condition.
- Verdict: EXACT. Proposed: "When armed, fires on the closest beast (war beast) ally in range".

### ally_broken (1)
- Current: "When armed, fires on a broken-morale ally in range"
- Code: the closest ally with `MoraleState == "broken"` that is NOT `is_routing()`. If a broken unit reads `is_routing() == true`
  (see C1), the two conditions contradict and this never fires.
- Verdict: EXACT in wording, possibly dead in practice. Proposed: keep wording after C1 is answered.

### ally_heal_melee (1)
- Current: "When armed, fires when this unit is in melee, on the lowest-health ally in range at or below 75% health"
- Code: caster in melee (`is_in_melee`, routing guard only; wavering allowed) + the ally_heal pick. No class filter.
- Verdict: EXACT in wording. Restriction not honoured (see B).
- Proposed: "When armed, fires when this unit is in melee, on the lowest-health friendly unit in range at or below 75% health that is not a Lord, Hero or large unit"

### ally_hurt_melee (1)
- Current: "When armed, fires on the most hurt friendly unit in range that is in melee"
- Code: the caster or an alive non-routing friendly within 70 m with `health_pct <= 75` AND in melee; the lowest wins.
- Verdict: INCOMPLETE ("at or below 75%"). Proposed: "When armed, fires on the lowest-health friendly unit in range (this unit included) that is in melee and at or below 75% health"

### ally_blast (1)
- Current: "When armed, fires on the friendly unit (or itself) with the most enemy value around it"
- Code: caster or ally within 140 m whose blast circle (`blob_score`) reaches the minimum line `blob_need`; highest value wins.
- Verdict: INCOMPLETE (the minimum line is silent).
- Proposed: "When armed, fires on the friendly unit in range (this one included) with the most enemy value inside its blast circle, once that covers at least half a packed block"

---------------------------------------------------------------------------------------------------------------------

## B. Abilities

Legend for "Better trigger": ALLY-MELEE = the target ally must itself be in melee (feasible: `ab_pick_ally` family "melee" exists).

### ally_melee_buff (armed by default)
| Marker | Ability | Effect (short) | Score | Why | Better trigger (if <= 3) | Restriction issue |
|---|---|---|---|---|---|---|
| da_boss_as_a_plan | Da Boss 'as a Plan! | ally melee defence +24, leadership +8, 20 s, 150 m | 3 | caster in melee is a proxy; the closest ally may not be fighting | ALLY-MELEE: closest ally in melee, caster melee optional | none |
| favour_of_the_fay | Favour of the Fay | ally melee attack +40, 44 s | 3 | melee stat on a possibly idle ally | ALLY-MELEE | none |
| fury_of_khaine | Fury of Khaine | melee attack +24, damage x1.5, RAMPAGE (positive), 28 s | 2 | Rampage takes the unit out of the player's control; now armed by default; target may be an archer | ALLY-MELEE and a non-missile target, or keep it M | none; see C2 |
| helping_hand | Helping Hand | melee attack +40, all resist +40, 22 s, 50 m | 2 | the game allows only Lords/Heroes (class commander) as target; the picker takes any ally | ALLY-MELEE restricted to a Lord/Hero | NOT HONOURED: `unit_is_not_commander_class`. Fix: filter with the existing commander set (`FOURTH.enemy_is_commander(ally) == true`) |
| inspired_assault_i | Inspired Assault I | charge bonus x1.2, melee attack +24, 29 s | 3 | the charge bonus is wasted once the caster is already in melee | ALLY-MELEE, or an ally about to charge | none |
| inspired_assault_ii | Inspired Assault II | charge x1.4, melee attack +24, 42 s | 3 | same | same | none |
| inspired_assault_iii | Inspired Assault III | charge x1.4, melee attack +40, 43 s | 3 | same | same | none |
| inspired_defence_i | Inspired Defence I | melee defence +24, leadership +16, 24 s | 3 | closest ally may be idle | ALLY-MELEE | none |
| inspired_defence_ii | Inspired Defence II | defence +24, leadership +16, charge defence, 31 s | 3 | same | ALLY-MELEE | none |
| inspired_defence_iii | Inspired Defence III | defence +40, leadership +16, charge defence, 34 s | 3 | same | ALLY-MELEE | none |
| orcs_are_da_best | Orcs are da Best! | melee attack +24, damage x1.5, 27 s, 150 m | 3 | same | ALLY-MELEE | none |
| slezuzus_voice | Daemonic Whispers | leadership +16, Fear, Terror, 26 s, 200 m | 3 | a morale buff cast on the closest ally in any state | ALLY-MELEE or wavering ally | none |
| hellish_vigour | Hellish Vigour | melee damage reflection +20, 25 s, wind-up 3 s | 3 | reflection only pays on an ally being hit in melee; wind-up needs it to stay engaged | ALLY-MELEE | none |
| verminous_fury | Verminous Fury | RAMPAGE, Unbreakable, Unyielding Assault, 60 s, 3 uses | 2 | uncontrollable unit for 60 s, armed by default, may land on an archer | ALLY-MELEE, non-missile; or keep it M | none; see C2 |

### melee_or_shooting_aura (M by default)
| Marker | Ability | Effect (short) | Score | Why | Better trigger (if <= 3) | Restriction issue |
|---|---|---|---|---|---|---|
| enchanted_metallurgy | Enchanted Metallurgy | melee damage x1.3, missile x1.25, 12 s, aura 35 m | 4 | pays when anyone fights; one engaged unit is enough | at least 2 engaged units in the aura | none |
| enchanted_metallurgy_flaming | Enchanted Metallurgy: Flaming | x1.6 melee, x1.5 missile, 14 s | 4 | same | same | none |
| enchanted_metallurgy_piercing | Enchanted Metallurgy: Piercing | AP and base damage x1.25, 14 s | 4 | same | same | none |
| enchanted_metallurgy_poison | Enchanted Metallurgy: Poison | x1.3 melee, x1.25 missile, 12 s | 4 | same | same | none |
| master_of_alchemy | Master of Alchemy | as Metallurgy, 20 s | 4 | same | same | none |
| master_of_alchemy_flaming | Master of Alchemy: Flaming | x1.6 / x1.5, 16 s | 4 | same | same | none |
| master_of_alchemy_piercing | Master of Alchemy: Piercing | AP x1.25, 19 s | 4 | same | same | none |
| master_of_alchemy_poison | Master of Alchemy: Poison | x1.3 / x1.25, 18 s | 4 | same | same | none |
| embers_of_the_phoenix | Embers of the Phoenix | x1.3 melee, x1.25 missile, 28 s, 3 uses | 4 | 3 uses, 90 s recharge are forgiving | same | none |
| horn_of_vaul | Horn of Vaul | x1.3 / x1.25, 28 s, ONE use, no recharge | 3 | the single use is spent on the first engaged or shooting unit near the caster | a larger fight: at least 3 engaged units in the aura | none |

### wavering_aura (armed by default)
| Marker | Ability | Effect (short) | Score | Why | Better trigger (if <= 3) | Restriction issue |
|---|---|---|---|---|---|---|
| call_of_violence | Call of Violence | leadership +16, 14 s, aura 35 | 5 | fires exactly when a unit in the aura wavers | - | none |
| get_back_ere | Get Back 'Ere! | leadership +16, 14 s | 5 | same | - | none |
| magical_animus | Magical Animus | leadership +16, 14 s | 5 | same | - | none |
| rally | Rally! | leadership +16, 14 s | 5 | same | - | none |
| tomb_king_rally | Reanimate | leadership +16, 14 s | 5 | same | - | none |
| tomb_king_rally_upgraded | Reanimate Upgraded | leadership +16, heal 0.8%/s, 10 s | 5 | same, heal bonus is free | - | none |
| pearl_of_infinite_bleakness | Pearl of Infinite Bleakness | leadership +8, 44 s | 4 | +8 may not lift a wavering unit; long duration is fine | - | none |
| mimic_cold_blooded | Mirror (Cold-Blooded) | leadership +16, 40 s, 2 uses, self only | 4 | fires on any wavering friendly unit only if one is in the (absent) aura; effectively caster only; user ruling "Self only" | - | none |
| unholy_clamour | Unholy Clamour | leadership +16 to Skaven, whole army, 18 s | 4 | a wavering non-Skaven ally triggers a cast that does nothing for it | require the wavering unit to be Skaven (type prefix) | `unit_is_not_skaven`: no filter on the trigger unit |

### health_aura_ally (armed by default)
| Marker | Ability | Effect (short) | Score | Why | Better trigger (if <= 3) | Restriction issue |
|---|---|---|---|---|---|---|
| berry_wine | Berry Wine | heal 3.2%/s for 14 s (about 45%), ONE use, 60 m | 3 | a 45% heal started at 75% wastes about 20% of it, and there is one use | fire at or below 55% (or the lowest of several hurt units) | none |
| dreaming_ring_i | Dreaming Ring I | heal 1.6%/s, 13 s | 4 | good; the 75% line is cheap with 60 s recharge | - | none |
| dreaming_ring_ii | Dreaming Ring II | heal 3.2%/s, 13 s | 4 | same | - | none |
| dreaming_ring_iii | Dreaming Ring III | heal 3.2%/s, 17 s | 4 | same | - | none |
| earth_blood | Earth Blood (2 keys) | heal 0.8%/s for 7 s (about 6%), 2 uses | 4 | tiny heal; fine at 75% | - | `hp_replenish_cap_reached`: no read; the engine refuses a capped target |
| fleshy_abundance | Fleshy Abundance | heal 1.6%/s, 18 s, 1 use, wind-up 5 s | 4 | fine | - | climbing / manning (siege, not modelled) |
| radiant_gem_of_hoeth | Radiant Gem of Hoeth | heal 0.8%/s, 10 s, 4 uses | 4 | fine | - | none |
| regrowth | Regrowth | heal 0.8%/s, 26 s, 1 use | 4 | fine | - | `hp_replenish_cap_reached` (same) |
| trollguts | Trollguts | heal 0.8%/s, 35 s, 1 use, wind-up 5 s | 4 | fine | - | siege flags only |

### allies_firing_aura (M by default)
| Marker | Ability | Effect (short) | Score | Why | Better trigger (if <= 3) | Restriction issue |
|---|---|---|---|---|---|---|
| ballistics_calibration | Ballistics Calibration | reload +20, 22 s, aura 55 (ground at caster) | 4 | user ruling (1 shooter, caster counts); one shooter wastes a 55 m aura | at least 2 shooters (round 130 asked for 2) | none |
| funnel_of_flame | Funnel of Flame | reload +30, 33 s, aura 55 | 4 | same | same | none |
| hail_of_fire | Hail of Fire | reload +30, 22 s, aura 55 | 4 | same | same | none |
| ballistic_enchantment | Enchanted Ballistics | accuracy +60, reload +20, 32 s | 4 | same | same | none |
| locus_of_change | Locus of Change | missile damage x1.25, 40 s, aura 55 | 4 | same | same | none |
| morgrims_eye | Morgrim's Eye | accuracy +60, AP x1.25, 32 s, aura 35 | 4 | same | same | none |
| the_guiding_eye | The Guiding Eye | AP x1.2, 18 s, aura 55 | 4 | same | same | none |
| deranged_munitions_upgraded | Deranged Munitions Upgraded | missile damage x1.5, 30 s, aura 35 | 4 | same | same | `cannot_perform_missile_attack` target: honoured implicitly (only shooters count) |

### wavering_ally_range (armed by default)
| Marker | Ability | Effect (short) | Score | Why | Better trigger (if <= 3) | Restriction issue |
|---|---|---|---|---|---|---|
| stay_here_ill_get_help | "Stay Here, I'll Get Help!" | leadership +16 area 35 m, 35 s, 3 uses | 3 | fires with the caster in melee, where the game forbids the cast; wasted attempts | add: caster not in melee | `engaged_in_melee` usage: no caster check in the evaluator (relies on engine readiness, see C3) |
| cold_blooded | Cold-Blooded | leadership +16, Rampage (negative), 40 s | 3 | Rampage on a wavering unit, armed by default; user ruling "On the wavering ally" | keep (ruling) but unit must be Lizardmen | NOT HONOURED: `unit_is_not_a_lizard_unit` (non-Lizardmen allies are offered) |
| crown_of_command | Crown of Command | Unbreakable, 30 s | 5 | exactly the moment | - | none |
| doom_lord | Doom Lord | Cannot Die, Unbreakable, Rampage (negative), 40 s | 4 | user ruling "On the wavering ally"; Rampage is the cost | - | none |
| pilgrimage_of_skulls | Pilgrimage of Skulls | Unbreakable, fatigue -0.01, 21 s | 5 | exactly the moment | - | none |
| tacticians_rally | Tacticians, Rally! | leadership +16, area 35 m around the ally | 5 | exactly the moment, area helps neighbours | - | none |

### health_aura_ground (armed by default)
| Marker | Ability | Effect (short) | Score | Why | Better trigger (if <= 3) | Restriction issue |
|---|---|---|---|---|---|---|
| gulyas | Gulyas | heal 0.08%/s plus leadership +4, 23 s, area 35 | 4 | user-set 24 m reach (round 104); cast range 200 m would allow 140 m | - | none |
| star_of_avelorn | Star of Avelorn | heal 0.8%/s, 27 s, 2 uses, area 15, up to 3 units | 3 | reach limited to 10 m from the caster although the ability can be placed up to 140 m away | widen the reach to the cast range and choose the spot with most hurt units | `on_a_platform` / `climbing` / `manning_equipment`: siege, not modelled |
| slime_smoothie | Slime Smoothie | ground nourishment, 14 s, 3 uses, area 35 | 4 | fine; no phase row to prove the effect is a heal | - | none |

### ally_missile (M by default)
| Marker | Ability | Effect (short) | Score | Why | Better trigger (if <= 3) | Restriction issue |
|---|---|---|---|---|---|---|
| inspired_marksmanship_i | Inspired Marksmanship I | accuracy +30, reload +20, 29 s | 2 | fires at once on the closest missile unit, shooting or not, enemy near or not | closest missile ally that is shooting past its cast point (existing "shooting" picker) | `cannot_perform_missile_attack`: HONOURED (generated missile set) |
| inspired_marksmanship_ii | Inspired Marksmanship II | accuracy +60, reload +20, 44 s | 2 | same | same | honoured |
| inspired_marksmanship_iii | Inspired Marksmanship III | accuracy +60, reload +40, 44 s | 2 | same | same | honoured |

### ally_heal (armed by default) and ally_ammo_low (armed by default)
| Marker | Ability | Effect (short) | Score | Why | Better trigger (if <= 3) | Restriction issue |
|---|---|---|---|---|---|---|
| elfish_healing_herbs | Elvish Healing Herbs | heal 0.6%/s, 27 s, 3 uses, 50 m | 4 | fine | - | none |
| patch_up | Patch Up | heal 1.6%/s, 7 s, 3 uses | 4 | fine | - | none |
| revivification_crystal | Revivification Crystal | heal 0.5%/s, 20 s, 7 uses | 4 | fine | - | usage `morale_is_broken_or_lower` (caster): not read, relies on engine readiness |
| more_powder | More Powder! | refill 30% ammo, 4 uses | 5 | user ruling; 70% line wastes nothing | - | none |
| restock | Restock! | refill 30% ammo, 4 uses | 5 | same | - | none |
| restock_gunnery_school | Restock! (gunnery school) | refill 30%, 2 uses | 5 | same | - | none |

### wavering_self_or_ally, melee_or_wavering_aura (both armed by default)
| Marker | Ability | Effect (short) | Score | Why | Better trigger (if <= 3) | Restriction issue |
|---|---|---|---|---|---|---|
| commanding_presence | Commanding Presence | leadership +8, 20 s, aura 35 | 3 | ally arm needs the ally in melee AND wavering, while the user asked "lord or nearby unit wavering" | drop the in-melee requirement (use `wavering_ally_in_aura`), as the quote says | none |
| fury_of_ulric | Fury of Ulric | leadership +8, 25 s, aura 35 | 3 | same hidden melee requirement | same | none |
| stand_your_ground | Stand Your Ground (2 keys) | melee defence +24, leadership +16, 18 s | 4 | user ruling; fires on one engaged unit | at least 2 engaged | none |
| hunters_call | Hunter's Call | melee defence +24, 32 s, 3 uses, 120 s | 3 | 3 uses are spent on the first melee near the caster | at least 3 engaged units or the caster in melee | none |

### melee_or_shooting_self_or_ally and single-entry ally/aura families
| Marker | Ability | Effect (short) | Score | Why | Better trigger (if <= 3) | Restriction issue |
|---|---|---|---|---|---|---|
| harmonic_convergence | Harmonic Convergence | melee attack +24, defence +24, reload +20, 27 s, 2 uses | 4 | melee or shooting both pay; picks the closest fighting ally, not the best | - | none |
| the_seerstaff_of_saphery | The Seerstaff of Saphery | melee attack +24, reload +40, 22 s, 4 uses | 4 | same | - | none |
| ally_wavering: shock_collar | Shock Collar | melee attack +24, leadership +16, immune to psychology | 4 | wavering ally is the payoff | - | NOT HONOURED: `unit_is_moulder_monster` (see C4) |
| ally_wavering: were_you_goin | Where You Goin!? | Unbreakable, 25 s | 5 | exactly the moment | - | none |
| will_of_the_verminking | Will of the Verminking | enemy leadership -16, friend phase, 29 s | 4 | user-designed trigger; sentence hides it | - | none |
| deranged_munitions | Deranged Munitions | missile damage x1.5, 30 s | 4 | user ruling "self, else a shooting ally"; closest shooter not best | - | missile target: honoured implicitly (shooters only) |
| skjalandirs_fall | Skjalandir's Fall | accuracy +90, Blinded on hits, 39 s, self | 3 | accuracy does nothing in melee, so the "in melee" arm wastes the cast; the shooting-into-melee arm is the user ruling | drop the melee arm (keep only shooting at a target in melee) | none |
| entrenchment | Entrenchment | cannot move, missile AP x1.4, physical resist +20, 44 s | 4 | user accepted the root | - | `flying_currently` target: not filtered on the ally arm |
| master_of_mists (+ _custom key) | Master of Mists | missile range x1.5, damage x1.25, reload +20, 58 s | 5 | user ruling "before range" | - | none |
| gruts_sickle | Grut's Sickle | winds recharge, 33 damage per second to one soldier for 20 s | 3 | fires as soon as ready on the sturdiest ally whatever the winds pool; 3 uses spent early | fire when the winds pool is low (the WINDS map row exists) or no earlier than a set time | none |
| makaissons_persuader | Makaisson's Persuader | heal 1%/s, 17 s, war machines | 4 | fine | - | `unit_is_not_artillery_or_war_machine`: HONOURED (caste warmachine set) |
| reforge | Reforge | heal 0.8%/s, 19 s, Hell-Forged | 4 | fine | - | honoured (hellforged attribute set) |
| remouldered | Remouldered | heal 0.5%/s, melee attack +24, leadership +8, 24 s | 4 | fine | - | NOT HONOURED: `unit_is_moulder_monster` (the monster set includes rat ogres, wolf rats, stormfiends: 27 moulder keys) |
| restore | Restore | heal 0.8%/s, 24 s, constructs | 4 | fine | - | honoured (construct attribute set) |
| overseer_of_the_unseen | Overseer of the Unseen | melee attack +40, Cannot Die, Unbreakable, 35 s | 2 | no gate at all: fires on the closest eligible ally at battle start | ALLY-MELEE (and hurt or wavering for Cannot Die) | honoured: commander, large and flying all filtered |
| whiplash | Whiplash! | charge speed x1.25, charge x1.2, melee damage x1.5, 21 s | 2 | no gate: fires at once on the closest beast | beast ally about to charge or in melee | honoured (beast set is a subset of non-commander) |
| iron_hand_captain | Iron-Handed Captain | leadership +100, 42 s | 2 | probably never fires: the picker skips routing units and a broken unit is likely routing (C1) | broken ally, read from MoraleState only, without the routing skip | `morale_is_higher_than_broken`: honoured by the filter, but see C1 |
| captain_of_the_phoenix_guard | Captain of the Phoenix Guard | heal 0.5%/s, physical resist +30, 43 s | 3 | picks the lowest-health ally, and Lords and large units are the likely hurt ones; caster melee irrelevant to the target | ALLY-MELEE target at or below 75%, non-commander, non-large | NOT HONOURED: `unit_is_commander_class` and `unit_is_large` (no filter in ally_heal_melee). Fix: reuse the "overseer" set without its flying check |
| the_gold_standard | The Gold Standard | invulnerable 13 s | 5 | user ruling; lowest-health ally in melee | - | none |
| arcane_vassal | Arcane Vassal | ally casts a spell at the foe (blast) | 4 | user ruling "most enemies around"; threshold line is silent | - | none |

---------------------------------------------------------------------------------------------------------------------

## C. Game-mechanics questions

1. C1: Does a unit whose `MoraleState` is "broken" also read `is_routing() == true`? If yes, `ally_broken` (Iron-Handed Captain) can never find a target
   because `ab_pick_ally` drops routing units before the "broken" filter. A field line with MoraleState and routing on one fleeing unit settles it.
2. C2: What does Rampage do to a unit under player control (Fury of Khaine, Verminous Fury, Cold-Blooded, Doom Lord)? The database calls it "positive" for the
   first two and "negative" for the last two. Fury of Khaine and Verminous Fury now start armed (round 161), so a rampaging melee or missile ally may follow.
3. C3: Does `can_perform_special_ability` go false for the CASTER while an `engaged_in_melee` or `morale_is_broken_or_lower` usage flag is active? The mod relies
   on it for Stay Here, Revivification Crystal and all caster-state usage flags; nothing in these evaluators checks them.
4. C4: Shock Collar and Remouldered list `unit_is_moulder_monster` as an INVALID target. This reads as "cannot target Skaven moulder monsters", which sounds
   odd for a Master Moulder ability; confirm in game which way it works before filtering (27 keys carry the attribute: rat ogres, wolf rats, stormfiends,
   hell pit abomination, brood horror and some Skaven heroes).
5. C5: Invalid-target flag semantics assumed: `unit_is_X` means a unit of class X cannot be targeted; `unit_is_not_X` means ONLY class X can be. Helping Hand
   (`unit_is_not_commander_class`) then means Lords/Heroes only. A player test with a regular unit would confirm.
6. C6: `hp_replenish_cap_reached` (Earth Blood, Regrowth): assumed to mean the target has already received the spell's maximum heal; no battle read exists.
7. C7: When a cast is accepted on an invalid target, does the engine consume the cooldown or silently do nothing? This decides how bad the Helping Hand,
   Captain of the Phoenix Guard, Remouldered, Cold-Blooded and Entrenchment gaps are.
8. C8: Grut's Sickle: 33 damage each second to one entity for 20 s (about 660) paid by the target. Assumed the benefit is a winds refill; whether a refill
   applies with a full pool is unknown, so "when ready" may waste the use.
9. C9: Inspired Assault's charge bonus only counts during the charge; a caster already in melee fires after that window. Assumed true.
10. C10: Abilities marked `ground=yes` with `friends=yes` (Stay Here, Tacticians Rally, Star of Avelorn, Gulyas) are cast by the mod in the unit form
    (Stay Here, Tacticians) or ground form (Star, Gulyas). Assumed both forms apply the area effect around the target.
11. C11: Berry Wine heal rate: `heal_amount` 0.016 every 0.5 s read as 1.6% of maximum health per tick (about 45% in 14 s).

---------------------------------------------------------------------------------------------------------------------

## Summary (5 lines)
1. Real restriction bugs: Helping Hand (only Lords/Heroes may be targeted), Captain of the Phoenix Guard (Lords and large units are valid candidates), Remouldered and Shock Collar (moulder monsters), Cold-Blooded (non-Lizardmen), Entrenchment (flying ally).
2. `ally_broken` (Iron-Handed Captain) probably never fires: the shared picker discards routing units, and a broken unit is most likely routing.
3. Four families have no condition beyond "an ally exists" and fire at battle start: ally_overseer, ally_beast, ally_missile (3 keys), ally_winds; the missile one has a ready-made fix (the existing "shooting" picker).
4. ally_melee_buff (14, now armed) targets the closest ally even if idle; an ally-in-melee picker already exists. Fury of Khaine and Verminous Fury grant Rampage and now start armed.
5. Tooltip errors: verminking_wavering and wavering_self_or_ally hide an "in melee" requirement (the second also contradicts the user's quoted ruling for Commanding Presence); melee_or_shooting_self_or_ally ends mid-clause; most aura sentences hide the 70% radius and "past its cast point".
