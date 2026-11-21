# Stand-still audit of every trigger (2026-11-21, round 190)

User: "Fix the 8 and also audit all the triggers." The 8 shot abilities are fixed in round 190. This document is the
audit; nothing in it is built. Each group needs your ruling.

## The rule being checked

Your 2026-11-17 ruling ("Option A, animation decides all"): a cast whose ability plays a cast animation (the game's
`wind_up_stance`, the generated `FOURTH.ANIM` table) stops a moving caster, so such a cast must wait until the caster
stands still. A cast without an animation may fire on the move. The Amber Bow battle (2026-11-21) showed what happens
without the check: Markus was walking, the cast went out, he stopped where he was.

## Method

`tools\audit_stand_still.py` (read-only). For each of the 141 triggers it follows the trigger's code and every helper it
calls, and asks whether that code ever reaches `FOURTH.blob_still` (the one stand-still test). It then counts the
animated abilities on that trigger. Table: `docs\WH3_stand_still_audit_2026-11-21.tsv`. I checked one result by hand
(the melee-enemy picker `enc_pick_enemy`, 103 lines, never reads the caster's movement).

## Result

- 49 triggers carry at least one animated ability.
- 16 of them already wait (the blast shots, waves, wanderers, cones, drains, the 8 fixed shots ...).
- **33 triggers, 103 animated abilities, never check.** Grouped by when they fire:

| Group | Abilities | Triggers | Can the caster be walking when it fires? |
|---|---:|---|---|
| 1. At an enemy somewhere else | 40 | enemy_ground_melee_infantry 12 (Celestial Comet, Meteor Strike, Lightning Strike ...), enemy_ground_melee 7, enemy_engaged_or_shot 6 (Oil Flask, Eternal Gaze ...), enemy_melee 6, enemy_fast_near_ally 4 (Rune of Slowness, Net of Amyntok ...), enemy_melee_or_fast 3 (Crippling Throw ...), enemy_melee_noncommander 1, enemy_missile_shooting 1 (Missile Mirror) | **Yes.** Exactly the Amber Bow case: an enemy elsewhere enters melee while you are moving the caster. |
| 2. On an ally | 14 | health_aura_ally 3 (Earth Blood, Trollguts ...), health_aura_ally_rule 2, health_aura_ground 2 (Gulyas, Slime Smoothie), self_or_ally_fire_melee 2, ally_heal 1, ally_in_melee 1, ally_offering 1, wavering_ally_range 1 (Doom Lord), melee_or_shooting_self_or_ally 1 | **Yes.** The ally's state triggers it, wherever the caster is going. |
| 3. The caster itself in melee | 32 | melee_unwavering 27 (Curse of Years, Okkam's Mindrazor, Primeval Roar ...), enemy_sweep 2, melee_skip_commanders 2, melee_clear 1 | Rarely: a unit in melee is fighting, not walking to an order. |
| 4. The caster's own state | 6 | wavering_self 1, wavering_self_or_ally 1 (Fury of Ulric), health_below_15 1 (Tz'arkan), ushoran_health 1 (Invocation of Nehek), under_fire 1 (Morikhane), melee_or_under_fire 1 (Rune of Oath & Steel) | **Yes.** A hurt, wavering or shot-at unit is often the one you are pulling back. |
| 5. On the caster's charge | 8 | charge_or_melee 4 (Rune of Speed, Master Rune of Speed, Full Power!, More Power!), aura_charge_only 2 (Battle Howl x2), charge_only 1 (Ferocious Battle Howl), charge_or_wavering 1 (Bangers & Smash) | **Always**, for the charge arm: the trigger is the caster charging. |
| 6. Built to fire on the move | 3 | air_drop_on_infantry 2 (Sky-Junk Bomb, Nan-Gau Grenades), fly_dive 1 (Emberstorm) | Always: flying over the enemy is the trigger. |

## Options and my recommendation per group

- **Group 1 (40) and group 2 (14): apply the same fix as the 8** (the animation decides: wait until the caster stands
  still). Recommended: it is the Amber Bow defect again, and your ruling "better if it doesn't fire" covers the cost (a
  cast may wait while you move the caster).
- **Group 4 (6):** A, the same fix (recommended: stopping a unit you are pulling back is the worse outcome); B, leave it.
- **Group 3 (32): leave it** (recommended). The caster is fighting. One unknown: whether `is_moving()` reads true while a
  unit fights. If it does, a stand-still check here would silence these abilities in melee. Alternative: the check with
  "in melee counts as standing".
- **Group 5 (8): check the logs first** (recommended). A stand-still check would kill the charge arm (it only fires
  while the caster moves); leaving it means the cast may halt the charge. Neither is known: I can search the archived
  battles for these casts and see whether the caster stopped. Then A (check: melee arm only), B (leave), or C (move the
  charge arm to "in melee").
- **Group 6 (3): leave it** (recommended): a check would silence them for good.

ASSUMPTION throughout: that every animated cast stops its caster. Round 168 matched it on 4 field cases, and the Amber Bow
battle is a fifth; it is not proven for every animation.

## Round 191 update (2026-11-21)

User: "For now, please only implement number 1." Group 1 (40 abilities, 8 triggers) is BUILT
(`docs\WH3_round191_still1.md`): those triggers now wait for an animated caster to stand still. The tool now counts the
load-time wrap; its round-191 table is `docs\WH3_stand_still_audit_2026-11-21_r191.tsv` (24 of 49 triggers wait, 63
animated abilities left). Groups 2 (14), 3 (32), 4 (6), 5 (8) and 6 (3) still wait for rulings.
