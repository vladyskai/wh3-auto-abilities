# Round 190 release: the animation decides in every shot trigger (2026-11-21)

User: "Amber Bow canceled his movement, not good" -> "Fix the 8 and also audit all the triggers."

- Amber Bow, Gaze of Nagash, Damned Pistol, Schalkain's Teeth, Goggly Glare, Vindictive Glare, Shem's Burning Gaze and
  The Black Tongue play a cast animation, which stops a moving caster: they now wait until the caster stands still.
  Abilities without an animation on the same triggers still fire on the move.
- Harness 189: 7,944 checks / 0 failures (twice, identical); RED reproduces the Amber Bow field case.
- Installed pack md5 `1b749a4d7c6815722a94db93f420eff0`, 1,599,680 bytes. Workbook v72.
- Audit of every trigger: `docs\WH3_stand_still_audit_2026-11-21.md` (103 more abilities, rulings pending).
- Round document: `docs\WH3_round190_shotstill.md`. Next battle from log byte 881,292,588.
