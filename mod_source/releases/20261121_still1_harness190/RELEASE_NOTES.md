# Round 191 release: the animation decides in group 1 (2026-11-21)

User: "For now, please only implement number 1." (group 1 of `docs\WH3_stand_still_audit_2026-11-21.md`)

- The 8 triggers that fire at an enemy somewhere else (enemy_ground_melee_infantry, enemy_ground_melee,
  enemy_engaged_or_shot, enemy_melee, enemy_fast_near_ally, enemy_melee_or_fast, enemy_melee_noncommander,
  enemy_missile_shooting) now wait for an animated caster to stand still: 40 abilities (Celestial Comet, Meteor Strike,
  Oil Flask, Rune of Slowness, Crippling Throw, Missile Mirror ...). Abilities without an animation still fire on the move.
- Harness 190: 7,967 checks / 0 failures (twice, identical); RED casts Oil Flask and Celestial Comet while the caster walks.
- Installed pack md5 `ffd2f85006fd334d245a2710d3449656`, 1,600,810 bytes. Workbook v73 (50 rows).
- Groups 2-6 (63 animated abilities) still wait for rulings.
- Round document: `docs\WH3_round191_still1.md`. Next battle from log byte 881,292,588.
