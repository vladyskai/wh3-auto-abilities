# Round 188 release notes (2026-11-21)

The range rule: every cast-range bound is max(floor(real x 0.70), real - 20 m) (user ruling 2026-11-21, "C. Your rule,
the larger of 70% and real minus 20 m, everywhere."). Above a 66 m real range the mod now casts from further away
(100 m: 70 -> 80, 200 m: 140 -> 180, 250 m: 175 -> 230). Auras unchanged.

- Harness: `harness187.lua`, 7,876 checks / 0 failures twice (byte-identical); RED on `docs\backups\round188\`.
- Builder: `build_and_install188.py` (`tools\make_builder188.py`); log `build188_log.txt`.
- Installed pack md5 `c478299540ea6704a364d16083145f57`, 1,583,998 bytes.
- Workbook v70; round document `docs\WH3_round188_rangerule.md`.
