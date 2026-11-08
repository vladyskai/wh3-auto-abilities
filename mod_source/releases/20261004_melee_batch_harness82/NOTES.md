# Round: THE APPROVED IN-MELEE-SELF BATCH + ITEM 8 (one dispatch) - 2026-10-04

## What shipped

### A. The approved in-melee-self batch (the questionnaire's block 1)
- 28 approved entries / 29 database keys (the list enumerates 28 items;
  the two Deathbringer keys - base + upgraded - sit in ONE entry, as
  specified). Implemented verbatim from the user-approved list:
  Aether Sword, Apocalyptic Vision, Armour of Gazrakh, Aura of Quetzl,
  Axe of Dargo, Axe of Grom, Axes of Kadrin, Azhag's 'Ard Armour,
  Ballet of Blows, Bear Fang Talisman, Beastslaver, Blade of Bel-Korhadris,
  Blades of Shang-Yang, Bloodstorm Blades, Brass Body, Change or Die!,
  Claws of Mourkain, Cloak of Mists & Shadows, Coat in Blood,
  Creature-Killer, Da Great 'Un Iz 'Ere!, Daemonblade, Daemonshield,
  Dagger of Malice, Dark Protection, Darkwalker, Deathbringer (incl.
  upgraded), Desertstrike (`wh2_dlc09_character_abilities_strike_of_nehekhara`
  - the corrected key; the "states_strike..." variant does not exist).
- ONE rule, ONE evaluator: every batch entry carries
  `trigger = "melee_unwavering"` and dispatches to the NEW
  `FOURTH.evaluate_in_melee_self(unit, routing)` - exactly blood_lust's
  rule (alive + in melee + not routing + not wavering, fail-open morale,
  self-cast). blood_lust itself rides the SAME function, so the rule can
  never drift between the five and the batch.
- Each entry: its own marker, display name, badge id
  (`zz_auto_badge_<marker>`), key list, and the top-slot fallback pair
  (ox/oy 0,0 - the wheel-slot path positions every claimed badge; no
  measured fallback was taken for these).
- Everything else is the EXISTING machinery, reused as-is: the claim walk,
  the deferred badge creation/placement (any wheel slot 1..6), the M/A
  badge click (default OFF, exactly like foe_seeker), the readiness gate,
  the 2 s guard, and the rejected-informed cooldown back-off
  (HOLD 8 s / bound 20 s). No new timers. No new chunk-level locals (the
  file compiles at Lua's 200-local ceiling - everything new is a FIELD of
  the existing FOURTH helper bag or a table entry).

### B. Critique-2 item 8: the trigger chain -> per-entry evaluate(unit)
- The `if/elseif ability.trigger == ...` chain is GONE from the poll. Each
  ability entry carries `evaluate(unit, routing)`; the poll makes ONE call:
  `local reason = ability.evaluate(unit, routing)` (the annotated copy:
  `local want_fire = ability.evaluate(unit, routing)`).
- One evaluator function per trigger, defined in the new section 7g
  (annotated: 6d) as FOURTH fields: evaluate_charge, evaluate_tired,
  evaluate_melee, evaluate_melee_low_morale, evaluate_in_melee_self.
  The five shipped abilities' evaluators are their old chain branches,
  BODY FOR BODY - same engine reads, same guards, same reason strings - so
  behaviour and log text are byte-identical.
- The trigger -> evaluator map (`FOURTH.evaluators`) and a load-time loop
  wire EVERY entry (and every future addition) - the harness asserts all
  33 entries are wired and that the batch shares ONE function object with
  blood_lust.
- The annotated reading copy was updated in step (entries, SECTION 6d,
  dispatch, intro) - it still reads correctly and stays log-/find-free.

## Harness (tests/harness82.lua)

- GREEN: 1861 checks, 0 failures - the WHOLE harness-81 suite (1720
  checks, boundary-asserted: "checks so far = 1719") re-ran, plus 141 new
  checks (section 0x + the C1-C8 worlds x2 files + boundary/aggregates).
- The new worlds:
  * C1-C4: all 28 batch keys fire on the in-melee condition ALONE
    (four six-unit worlds; well past the "sample at least 6" bar), each
    with its blood_lust reason text, one claim + one badge each, badges on
    their computed wheel slots, and NO phantom badges (exact create count);
    C1 also proves the 2 s guard and the next window.
  * C5: the deathbringer entry from BOTH sides - one claim for its two
    buttons (one badge per marker), base-key owner AND upgraded-key owner
    both fire.
  * C6: SIX badges on ONE unit (the "several on a lord" case) - all M by
    default, two armed by click (A), ONLY those two fire, then fire again
    next window; runtime proof that every entry (33/33) is wired and that
    the batch + blood_lust share ONE evaluator object while a different
    rule keeps its own.
  * C7: a unit owning NONE keeps its dial clean (foreign bar button only:
    no component ever created, no claim, no fire, ZERO evaluations, entry
    scan really ran). Passes on the snapshot too - a non-regression.
  * C8: the guards hold (not-in-melee / routing / wavering / dead) with
    the steady control firing; the routing/wavering reads happen exactly
    where the rule reads them.
- ADAPTED existing checks (16, all forced by this round's approved
  changes; everything else is byte-unchanged and re-ran):
  * 11 ability-count pins for the grown table: A4a/A4b x2 (bootstrap walk
    10 iterations / 5 per pass -> 66 / 33), B4a x2 (unknown-cache
    fallback 5 -> 33 evaluations), H68 x5 (table 5 -> 33 entries, key map
    9 -> 38 keys, ordered array 9 -> 38 keys).
  * 4 chain-branch tokens re-pointed at the evaluators that replaced them:
    0v (melee_unwavering branch -> `function FOURTH.evaluate_in_melee_self(unit, routing)`)
    and 0w (tired branch -> `function FOURTH.evaluate_tired(unit, routing)`),
    each x2 files - with an in-file comment saying why.
  * 1 red-branch check (harness 81's) adapted to the new snapshot lineage:
    the pre82 snapshots already carry the trigger changes, so it now reads
    "N/A by design - 20/20 O/F worlds pass".
  * cosmetics only: the env pair renamed H81 -> H82, the header print, the
    red-mode banner text.
- RED CONTROL (harness82 with H82_LIVE / H82_ANN -> pre82 snapshots):
  1842 checks, 112 failures - ALL designed, zero unexpected:
  * A4 pins 4, B4 pin 2, H68 pins 5 (the pre-edit table is 5 entries/9 keys)
  * adapted tokens 4 (evaluators absent)
  * new 0x tokens 22 (no batch, chain still present)
  * C1-C6 world checks 68 + C8 5 (no batch: 0 claims, 0 badges, 0 fires)
  * knock-on world aggregates 2 (active-set 6/8, owned-list 10/12)
  * C7 (2 world results x2 files) PASSES by design; harness-80 "N/A 16/16"
    and harness-81 "N/A 20/20" red branches PASS; every earlier suite
    behaves identically.

## Build + install
- Build: `uv run --quiet --with websockets python build_and_install.py`
  (rpfm_server.exe started first from WH3_mod/tools/rpfm/). The script gained
  the ROUND v82 gates (the evaluators, the map, the wiring loop, the single
  dispatch, the batch markers/keys/badges, and "no ability.trigger ==").
- Pack md5: f2a633ed2f840a91ba3f0bf29d1341f0 (dist/ == installed).
- Independently verified:
  * verify_cleaned_independent.py (raw PFH5 parse): exactly the 5 ship
    files, every file byte-identical to source, main mod sha256
    638db5302ca904de5f58430e4e602942849f0e2506cce0447582f008f2581182,
    zero zz_probe_* fragments, RESULT: PASS.
  * verify_cleaned_rpfm.py (fresh RPFM reopen + extract): 5 files, all
    byte-identical, extracted copy on disk identical - OK.

## HOW TO FIELD-TEST (one battle; search the log for "ATTEMPT" / "reason:")
1. Pick a unit that owns several of the batch - a lord like
   **Taurox the Brass Bull** (Brass Body), **Grom the Paunch**
   (Da Great 'Un Iz 'Ere!), **Elspeth von Draken** (Darkwalker),
   a **Strigoi Vampire Lord** (Claws of Mourkain), a **Beastlord**
   (Apocalyptic Vision), an **Exalted Keeper of Secrets** (Ballet of
   Blows) - or any character carrying one of the item/weapon abilities
   (Axe of Grom, Aether Sword, Bear Fang Talisman, Daemonshield, ...).
2. Arm the badges: each batch ability now draws its own letter on the
   wheel. Click each one to **A** (default is M/off, exactly like the
   other five).
3. Send the unit into hand-to-hand and let it fight. Sample a few at
   random across your units - expected lines:
   `ATTEMPT <marker> '<key>' on '<unit type>' ui id <id> | reason: in melee, morale not wavering | armed=ON`
   e.g.
   `ATTEMPT brass_body 'wh2_dlc17_lord_abilities_brass_body' on 'Taurox the Brass Bull' ui id 1234 | reason: in melee, morale not wavering | armed=ON`
   (if the morale read cannot be taken the reason becomes
   `| reason: in melee (morale unreadable - plain in-melee fallback) |`).
   A landed cast logs `perform_special_ability(key, unit) : ACCEPTED`; a
   cooldown refusal logs `REJECTED (on cooldown)` ONCE per episode, then
   the existing back-off holds it (8 s, hard bound 20 s) and retries.
4. Controls to spot-check: a unit NOT in melee stays silent; a routing or
   wavering unit is held back; a unit that owns none of the batch shows
   NO new badge; the five original abilities behave exactly as before.

## Files in this archive
- `harness82.lua`            - the extended harness (green + red verified)
- `h82_green.txt`            - the green run output (1861 checks / 0)
- `h82_red.txt`              - the red-control run output (1842 checks / 112 designed)
- `zz_test_deadly_onslaught.lua` - the main mod AS SHIPPED this round
- `WH3_auto_ability_annotated.lua` - the annotated reading copy, same round
- Pre-edit snapshots live in `../20261004_pre_melee_batch/`.
