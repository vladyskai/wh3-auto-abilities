# Round: BLOOD LUST (the FIFTH ability) - 2026-10-04

## What shipped
- The main mod (`zz_test_deadly_onslaught.lua`) now fires a FIFTH ability:
  Blood Lust, marker `blood_lust`.
- Ability keys (from the extracted game data):
  - `wh_main_character_abilities_blood_lust` - Vampire Counts Strigoi Ghoul
    King (`wh_dlc04_vmp_cha_strigoi_ghoul_king_0`, `_1`, `_boss`)
  - `wh_dlc03_character_abilities_blood_lust` - Beastmen Beastlords
    (`wh_dlc03_bst_cha_beastlord_0`, `_1`, `wh2_dlc17_bst_cha_beastlord_2`)
- Trigger `melee_unwavering`: alive + in melee + NOT routing + NOT wavering
  (morale read fail-open: only a readable `is_wavering() == true` suppresses).
- Cast: the proven self-targeted `uc:perform_special_ability(key, unit)`.
- Badge `zz_auto_badge_bl`: wheel slot 5 (the next free slot; measured
  135-degree position (28,877)); fallback offset -68,+32 from BADGE_X/BADGE_Y;
  M/A convention; default M/off exactly like foe_seeker.
- Refusals ride the EXISTING cooldown-hold back-off (HOLD_SECONDS=8 /
  MAX_HOLD_SECONDS=20) - no new constants.

## Harness (tests/harness80.lua)
- GREEN: 1592 checks, 0 failures (the whole harness-79 suite still re-runs,
  plus the new section 0v, the B1-B8 worlds x2 files, the boundary check).
- Ability-count pins updated in harness80 for the fifth entry: the
  not-routing guard count 5 -> 6, the full-table badge walks 4 -> 5 per pass,
  the unknown-cache fallback 4 -> 5 evaluations, the H68 table 4 -> 5
  entries / 7 -> 9 keys.
- RED CONTROL (run):
      H80_LIVE=C:/Users/vlady/AppData/Local/Temp/pre80/zz_test_deadly_onslaught.lua \
      H80_ANN=C:/Users/vlady/AppData/Local/Temp/pre80/WH3_auto_ability_annotated.lua \
      uv run --quiet --with lupa python run_mock.py harness80.lua
  Result: 74 failures, ALL designed deltas - the 0v tokens, the B-worlds
  (0/16 passed on the pre-edit snapshot; 0 claims / 0 badges / 0 fires in the
  LIVE worlds) and the updated pins; no unexpected failure.

## Build + install
- Build: `uv run --quiet --with websockets python build_and_install.py`
  (rpfm_server.exe started first from WH3_mod/tools/rpfm/).
- Pack md5: d3e1fcccd689652afbc412e5799ea33b (dist/ == installed).
- Installed pack verified independently (verify_cleaned_independent.py):
  exactly the 5 ship files, every file byte-identical to source (main mod
  sha256 8b7703d202b553af1eb4b58b2b9a6f4fc513843cc65f6353b7faf525d6bd0301),
  zero zz_probe_* fragments.

## Files in this archive
- `harness80.lua`            - the extended harness (green + red verified)
- `h80_green.txt`            - the green run output (1592/0)
- `h80_red.txt`              - the red-control run output (designed deltas only)
- `zz_test_deadly_onslaught.lua` - the main mod AS IMPLEMENTED this round
- `WH3_auto_ability_annotated.lua` - the annotated reading copy, same round
- Pre-edit snapshots live in `../20261004_pre_blood_lust/`.
