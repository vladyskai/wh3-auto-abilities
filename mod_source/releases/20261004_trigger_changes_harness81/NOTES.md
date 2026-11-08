# Round: THREE APPROVED TRIGGER CHANGES - 2026-10-04

## What shipped (the user's own words)
1. "changing Deadly Onslaught to fire on charge and in melee, since it has a
   component that is useful in melee"
   - the proven charge window is UNTOUCHED (same `measure_charge` verdict,
     same reason text); the in-melee arm (`FIRE_ON_MELEE`) is switched ON and
     rides the same `unit:is_in_melee()` read the other melee triggers use
     (`m.melee`). The two arms exclude each other (a charging unit has not
     made contact), so one evaluation can never double-fire.
   - reason texts stay accurate: `reason: charging (gap=...m dist=...m
     eta=...s)` vs `reason: in melee`.
2. "Foe-Seeker should check the vigor state of the unit and fire when Tired
   or lower"
   - trigger `"running"` -> `"tired"`. The API dump HAS a plain getter:
     `battle_unit:fatigue_state()` ("Possible values are threshold_fresh,
     threshold_active, threshold_winded, threshold_tired,
     threshold_very_tired and threshold_exhausted."). No localised
     FatigueName is parsed - the read is language-independent.
   - EXACT matching only (the banned string.find never runs): the WHOLE
     value is compared by equality in `FOURTH.fatigue_states` (the
     documented "threshold_" forms AND the bare words are accepted). Fire
     set = tired / very_tired / exhausted ONLY (`FOURTH.fatigue_fire`); a
     merely winded unit holds the ability back.
   - FAIL CLOSED: an unreadable read (raises / no string / unknown state)
     NEVER fires and writes ONE one-time notice - either
     `foe_seeker fatigue: read UNAVAILABLE ...` or
     `foe_seeker fatigue: UNRECOGNISED value '<raw>' ...`. This deliberately
     differs from the morale guard (is_wavering), which fails OPEN - stated
     in the code comment.
   - THE LOCAL CEILING: the main chunk compiles EXACTLY at Lua's 200-local
     limit (pre-edit snapshot cannot take even ONE more local - verified by
     a compile probe), so the reader, its two maps and its once-flag are
     FIELDS on the existing FOURTH helper bag: ZERO new chunk locals.
     Restructured into `FOURTH.fatigue_*`; compile-verified.
3. "Foe-Seeker should no longer fire when running"
   - the `"running"` trigger branch is DELETED (branch, its reason text and
     its `is_moving_fast` gate). `is_moving_fast` remains ONLY inside
     `measure_charge` (the charge detector needs it - untouched).
   - guards kept as the branch had them: alive (poll), not routing, the 2 s
     guard, the cooldown-hold back-off. (The deleted branch had no wavering
     read - none was added.)

## Harness (tests/harness81.lua)
- GREEN: 1720 checks, 0 failures (the whole harness-80 suite re-runs - its
  boundary check pins checks-so-far = 1591 - plus section 0w, and the
  O1-O3 / F1-F6 worlds x2 files).
- The new worlds:
  * O1 onslaught fires in melee (new arm; reason text; window cadence)
  * O2 onslaught still fires in the charge window (regression; reason kept)
  * O3 neither condition -> silent; the melee arm is live on transition
  * F1 tired / very_tired / exhausted all fire (the bare 'exhausted' input
    proves the non-prefixed shape), one fatigue read per unit
  * F2 fresh / active / winded hold - EVEN WHILE RUNNING; only tired fires
  * F3 a running fresh unit never fires ('reason: running' gone); the SAME
    running unit fires the moment its state is tired
  * F4a missing/raising fatigue: fail closed + ONE notice over 3 polls
  * F4b unknown state string: fail closed + the notice NAMES the raw value
  * F5 the routing guard still holds under the new trigger
  * F6 all five abilities still claim + badge + place (M default; slots)
- FIXTURE UPDATES: every prior-suite world that fired Foe-Seeker via the
  RUNNING trigger now carries `fatigue = "threshold_tired"` on the same
  units (C1-C6, I3, A2, B3, B5, N1-N3, R1/R4/R5/R6, H1/H2, CO1-CO4) - the
  fire outcomes those worlds prove are unchanged, on the new mod AND the
  pre-edit snapshot. H1's final phase resets to fresh so its "no duplicate
  fires" boundary stays silent.
- RED CONTROL (pre81 snapshots -> H81_LIVE / H81_ANN): 49 failures, ALL
  designed:
  * 0w source tokens: 18 (the three changes' tokens absent)
  * O1: 7 (no melee fire; no 'reason: in melee')
  * O3: 4 (the melee control is silent)
  * F1: 5 (nothing fires for tired; zero fatigue reads)
  * F2: 4 (the RUNNING fresh/active/winded units DO fire - old trigger)
  * F3: 5 (a running fresh unit fires; 'reason: running' is written)
  * F4a: 3 / F4b: 3 (no one-time notice; no fatigue reads)
  No unexpected failure. The h81 red aggregate asserts the exact pattern
  (O1 0 fires, F1 0, F2 4, F3 first-fire 1 and 1 'reason: running', 0
  notices, 6/20 world results pass = both files' O2, F5, F6). One previous
  round's red-branch check (harness 80) was adapted to the new snapshot
  lineage the same way harness 80 adapted harness 79's ("N/A ... passes by
  design"), and the build script's old "is_moving_fast = the running
  trigger" gate was replaced with the new tokens (running gone / fatigue
  present / in-melee arm on / one-time notices / no string.find call).

## Build + install
- Build: `uv run --quiet --with websockets python build_and_install.py`
  (rpfm_server.exe started first from WH3_mod/tools/rpfm/).
- Pack md5: 0d7806abefec93a9fd8fe743580849e0 (dist/ == installed).
- Independently verified (verify_cleaned_independent.py, raw PFH5 parse):
  exactly the 5 ship files, every file byte-identical to source, main mod
  sha256 5d56093a24cbb3a18b7ed4f44aab1458b7818d2babc701370c366f2b7b4bfb2e,
  zero zz_probe_* fragments.

## HOW TO FIELD-TEST (one battle; search the log for "ATTEMPT" / "reason:")
1. Arm the badges (click to A) as usual.
2. Onslaught in melee: send the unit into hand-to-hand and let it fight.
   Expected:
   `ATTEMPT onslaught '<key>' on '<type>' ui id <id> | reason: in melee | armed=ON`
   (the charge case still logs `| reason: charging (gap=...m dist=...m eta=...s)`).
3. Foe-Seeker tired: run the unit until its card shows Tired or lower.
   Expected:
   `ATTEMPT foe_seeker '<key>' on '<type>' ui id <id> | reason: tired or worse (fatigue: tired) | armed=ON`
   ('very_tired' / 'exhausted' look the same; a merely winded unit must NOT fire).
4. Running alone: a fresh unit running around must produce NO foe_seeker
   ATTEMPT line, and no "reason: running" anywhere.
5. If the fatigue read ever fails, the log carries ONE line -
   `foe_seeker fatigue: read UNAVAILABLE ...` or
   `foe_seeker fatigue: UNRECOGNISED value '<raw>' ...` - and the ability
   does not fire (fail closed, by design).

## Files in this archive
- `harness81.lua`            - the extended harness (green + red verified)
- `h81_green.txt`            - the green run output (1720/0)
- `h81_red.txt`              - the red-control run output (49 designed)
- `zz_test_deadly_onslaught.lua` - the main mod AS SHIPPED this round
- `WH3_auto_ability_annotated.lua` - the annotated reading copy, same round
- Pre-edit snapshots live in `../20261004_pre_trigger_changes/`.
