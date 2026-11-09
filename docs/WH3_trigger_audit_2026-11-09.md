# Trigger audit, 2026-11-09

Every automated ability (698 entries) checked against the rules below by `tools/audit_triggers.py`. The effect is the game's own data; a flagged row is a candidate for review, not a decision.

| Rule | Candidates |
|---|---:|
| R1. Shooting-only buffs on a trigger with no shooting arm | 0 |
| R2. Melee AND shooting buffs on a melee-only trigger (the user asked to review these) | 0 |
| R3. Melee-only debuffs on a trigger with a missile arm (rule 10) | 0 |
| R4. Enemy slows on a trigger that is neither melee nor charge (rule 10) | 0 |
| R5. Protection against shots on a melee-only trigger | 0 |
| R6. Morale effects on a trigger with no morale read | 25 |
| R7. Speed buffs on the unit itself on a melee-only trigger | 0 |

## R1. Shooting-only buffs on a trigger with no shooting arm

None.

## R2. Melee AND shooting buffs on a melee-only trigger (the user asked to review these)

None.

## R3. Melee-only debuffs on a trigger with a missile arm (rule 10)

None.

## R4. Enemy slows on a trigger that is neither melee nor charge (rule 10)

None.

## R5. Protection against shots on a melee-only trigger

None.

## R6. Morale effects on a trigger with no morale read

| Ability | Marker | Trigger now | Effect (game data) |
|---|---|---|---|
| Axe of Men | `axe_of_men` | `melee_unwavering` | Causes Terror (positive); Unbreakable (positive) (to self) |
| Call of Violence | `call_of_violence` | `melee_unwavering` | Leadership: +16 (to self and allies in range) |
| Change or Die! | `change_or_die` | `melee_unwavering` | Leadership: +16; Damage Resistance: +20 (to self and allies in range) |
| Cold-Blooded | `cold_blooded` | `melee_unwavering` | Leadership: +16; Rampage (negative) (to self and allies in range) |
| Crown of Command | `crown_of_command` | `melee_unwavering` | Unbreakable (positive) (to self and allies in range) |
| Daemonic Whispers | `slezuzus_voice` | `ally_melee_buff` | Leadership: +16; Causes Fear (positive); Causes Terror (positive) (to allies in range) |
| Doom Lord | `doom_lord` | `melee_unwavering` | Cannot Die (positive); Rampage (negative); Unbreakable (positive) (to self and allies in range) |
| Get Back 'Ere! | `get_back_ere` | `melee_unwavering` | Leadership: +16 (to self and allies in range) |
| Ghoul King of Ushoran | `ghoul_king_of_ushoran` | `ushoran_health` | Leadership: +8; Heals: 0.008 per tick every 1 s (to self); Replenishes hit points of combatants (positive) |
| Gulyas | `gulyas` | `health_aura_ground` | Leadership: +4; Heals: 0.0008 per tick every 1 s; Fatigue: -0.01 (to self and allies in range) |
| Magical Animus | `magical_animus` | `melee_unwavering` | Leadership: +16 (to self and allies in range) |
| Mirror (Cold-Blooded) | `mimic_cold_blooded` | `melee_unwavering` | Leadership: +16; Rampage (negative); Fatigue: -0.1 (to self and allies in range) |
| Pearl of Infinite Bleakness | `pearl_of_infinite_bleakness` | `melee_unwavering` | Leadership: +8; Immune to Psychology (positive) (to self and allies in range) |
| Pilgrimage of Skulls | `pilgrimage_of_skulls` | `melee_unwavering` | Unbreakable (positive); Fatigue: -0.01 (to self and allies in range) |
| Purge the Weak! | `purge_the_weak` | `charge_or_melee` | Speed: +30%; Leadership: +6; Fatigue: -0.02 (to self) |
| Rally! | `rally` | `melee_unwavering` | Leadership: +16 (to self and allies in range) |
| Reanimate | `tomb_king_rally` | `melee_unwavering` | Leadership: +16 (to self and allies in range) |
| Reanimate Upgraded | `tomb_king_rally_upgraded` | `melee_unwavering` | Leadership: +16; Heals: 0.008 per tick every 1 s (to self and allies in range); Replenishes hit points of combatants (positive) |
| Rot or Die! | `rot_or_die` | `melee_unwavering` | Melee Damage Reflection: +20; Leadership: +16; Spreading area: wh3_dlc25_lord_abilities_rot_or_die (to self and allies in range); Will spread to friends within the Spread Range metres of affected unit (positive) |
| Scrying Stone | `scrying_stone` | `melee_unwavering` | Leadership: +8; Damage Resistance: +20 (to self) |
| Shield of the Old Ones | `shield_of_the_old_ones` | `melee_unwavering` | Leadership: +8; Damage Resistance: +20 (to self and allies in range) |
| Tacticians, Rally! | `tacticians_rally` | `melee_unwavering` | Leadership: +16 (to self and allies in range); Extended cast range (magic) |
| The Liber Mortis | `the_liber_mortis` | `melee_unwavering` | Leadership: +8; Physical Resistance: +40 (to self and allies in range) |
| Unholy Clamour | `unholy_clamour` | `melee_unwavering` | Leadership: +16; Fatigue: -0.01 (to self and allies in range) |
| Verminous Fury | `verminous_fury` | `ally_melee_buff` | Rampage (positive); Unbreakable (positive); Unyielding Assault (positive) (to allies in range) |

## R7. Speed buffs on the unit itself on a melee-only trigger

None.

## R4: kept by the user's ruling (not candidates)

| Ability | Marker | Trigger | Ruling |
|---|---|---|---|
| Book of Secrets | `book_of_secrets` | `enemy_engaged_or_shot` | round 135: 'Keep as is' (no target filter in the game data) |
| Fecund Rebirth | `mark_of_the_monster` | `enemy_engaged_or_shot` | round 135: 'Keep as is' (large single-entity filter) |
| Hunter of Champions | `hunter_of_champions` | `enemy_engaged_or_shot` | round 123: 'Hunter of champions is okay for enemy_engaged_or_shot' |
| Looming Dread | `looming_dread` | `enemy_engaged_or_shot` | round 135: 'Keep as is, but make sure the trigger filters for the enemy unit type' (Lord/Hero filter) |
