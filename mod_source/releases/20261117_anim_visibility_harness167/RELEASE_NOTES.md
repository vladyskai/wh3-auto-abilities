# Round 168: the cast animation decides, the older pickers skip hidden enemies (2026-11-17)

- Only an ability with a cast animation (wind_up_stance) waits for its caster to stand still (GENERATED
  FOURTH.ANIM_TEXT, tools/gen_anim_keys.py, 228 keys); 63 entries may now fire while the caster moves.
- Every enemy picker skips an enemy the game reads as not visible to our alliance (FOURTH.enemy_not_hidden).
- Harness 167: 7,082 checks / 0 failures (run twice, identical); RED 16/16.
- Installed pack md5 89258fddf65a5ca819df984941cb7773 (1,414,743 bytes).
