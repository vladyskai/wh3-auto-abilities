# CLAUDE.md

Project memory for Claude Code. Read this before touching anything. These are standing user
rulings accumulated over many rounds, not suggestions. Apply them; do not re-ask.

## 1. PROJECT

A WARHAMMER III battle-script Lua mod that auto-fires special abilities on per-ability
triggers. It polls the battle state, walks the units the player has armed, calls a shared
trigger evaluator for each entry, and casts when the evaluator says fire.

- Mod source (the ONLY file edited per round):
  `C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua`
  (about 774 KB, about 15,300 lines)
- Packed as a Movie pack and installed as
  `zz_test_deadly_onslaught.pack` in
  `C:\Program Files (x86)\Steam\steamapps\common\Total War WARHAMMER III\data\`
- Installed build: md5 `c719e140ddff4f0525889c1388bb3fd8`, 1,316,389 bytes
  (round 137, 2026-11-09, audit batch 6: the morale abilities fire on wavering). RPFM packs are not byte-reproducible: compare contents, not the md5. Always re-measure instead of trusting this line.
- Game data: `gamedata\wh3\` inside the project (named once in `tools\gamedata_paths.py`;
  regenerate from the installed game with `tools\extract_gamedata.py`). NEVER read or write
  game data, harness inputs or check lists under Windows Temp: Temp cleanup emptied parts of it
  twice. Every new builder, harness and tool takes its paths from `gamedata_paths.py`.
- Project root: `C:\Users\vlady\Desktop\WH3_mod` (relocated 2026-10-16; absolute paths are
  baked into tools, harnesses and docs, so moving the tree breaks the toolchain)

Layout:

| Path | What it is |
|---|---|
| `mod_source\script\battle\mod\` | the live source script, plus retired probe scripts |
| `mod_source\releases\<date>_<name>_harness<N>\` | per-round harness + build script + run logs |
| `tools\` | builders, verifiers, harness runner, RPFM server |
| `docs\` | tracker, database, spreadsheets, round documents, annotated copy |
| `archive\` | sealed history: logs, packs, releases, vanilla extracts |
| `audit\` | independent audit output |

Pack contents are five files, and every build verifies all five are byte-identical to
source (paths below relative to `mod_source\`):

- `script\battle\mod\zz_test_deadly_onslaught.lua`
- `mod_source\ui\templates\zz_auto_badge.twui.xml`
- `mod_source\ui\zz_auto\auto_badge.png`
- `mod_source\ui\zz_auto\blank.png`
- `mod_source\ui\common ui\special_ability_tooltip.twui.xml` (the folder name really
  contains a space)

## 1b. VERSION CONTROL (since 2026-11-08)

- Public GitHub repository: https://github.com/vladyskai/wh3-auto-abilities (branch `main`), pushed
  over HTTPS through the GitHub CLI (`gh`, account `vladyskai`).
- Commit author is set in the repo: `vladyskaizen` / `116801803+vladyskai@users.noreply.github.com`
  (GitHub's private address; never the user's Gmail).
- Every round ends with ONE commit (the round's source, annotated copy, harness, builder, docs) and a
  push. The user wants the activity visible on his profile.
- `.gitattributes` stores every file byte for byte (`* -text`): the build's byte-identity gates and
  the LF mod source depend on it. Never remove it.
- `.gitignore` keeps out battle logs, packs, `gamedata/` and `archive/` (Creative Assembly data and
  other modders' files: not ours to publish), RPFM, the unchanged `hud_battle.twui.xml` copies and
  `claude_code_export/`. Before pushing, check that nothing over 50 MB and nothing from those
  groups is staged.

## 1c. THE LOOP (agreed 2026-11-08)

`docs\WH3_process_proposal_2026-11-08.md`, section 0. Every ability climbs: Open -> Proposed -> Approved ->
Built -> QA passed (the log of a battle THE USER fights; no self-playing build) -> Field approved. Rounds take
batches of about 10; every proposal walks the sensor checklist. The trigger audit
(`toolsudit_triggers.py`, `docs\WH3_trigger_audit_<date>.md`) feeds the batches; re-run it and
`tools\make_progress_page.py` (`docs\progress.html`) at the end of every round.

## 2. HARD RULES (settled; never re-litigate)

1. **Wheel-only.** `perform_special_ability` only fires abilities that are present in the
   unit's battle ability wheel. An ability that is not in the wheel can never be cast, so
   implementing it is dead weight. Army-bar abilities are the trap and are excluded
   absolutely: the army-bar set is the `army_spec` junction, and `unit_abilities.source_type`
   alone does NOT reveal it (several army-bar keys are `source_type = bound`). Enforced by
   three permanent gates, and a violation can never be "documented" into passing:
   - `tools\audit_wheel_status.py` G3 fails on any IN-WHEEL row carrying an army_spec key.
   - `tools\build_and_install*.py` has an assertion before any stale pack is deleted or any
     RPFM command is sent: `BUILD REFUSED (round 121 army-bar gate)`.
   - `tools\verify_ability_database.py` assertion A0 applies the same test to the database.
   Do not add exceptions lists. Do not argue that an army-bar entry "works".
2. **No em dashes** in anything written for this user: chat replies, docs, tracker text,
   comments, release notes. Use a comma, a colon, parentheses or a new sentence.
3. **The 70% range rule.** Every trigger range constant is `floor(real_range * 0.70)`, where
   the real range is `target_intercept_range` from the game's own tables (an aura's
   `effect_range` gives the radius; 0 means self-only). No exceptions. It overruled a 25 m
   value the user had field-tuned himself. Shipped as `FOURTH.RANGE_FRACTION = 0.70`; the
   build asserts `constant == floor(real * 0.70)`. The single documented override is a metre
   value the user personally sets for an overlap/underfoot test (air drop), which is a named
   constant, exempted explicitly from the range map, and commented as a test value.
4. **Prefer live reads; baked stats when no live read exists.** Read live from the engine
   whenever the API offers the value. When it does not (e.g. a unit's reload time), a table
   GENERATED from the game's own data by a tool (never hand-typed) is allowed (user ruling
   2026-11-03: "It is always better to read live from the engine, but when that is not
   possible, we can use baked stats"). Never trust
   `battle_unit:unit_in_range()` as an offer/range gate: it is the engine's own much looser
   reach read (it passed at 81.3 m where the ability's bound was 52 m) and trusting it makes
   the engine walk the caster toward the target, which the user sees as an unwanted move
   order. Compare `unit_distance` against your own constant only.
5. **Feedback is static on screen, never blinking.** No flashing, no animation, no timed
   fade. One stable badge per ability on the ability's own icon. The badge is the click
   control surface: `M` = manual/unarmed, `A` = automatic/armed. Clicking the badge on a
   selected unit's card flips that unit's state for that ability. State is per unit, not
   global.
6. **Do not disturb the game install.** Never rewrite game files, never touch
   `used_mods.txt` (`C:\Program Files (x86)\Steam\steamapps\common\Total War WARHAMMER III\used_mods.txt`),
   never add or remove other mods. Write exactly one pack into `data\`, and only through the
   round's build script.
7. **Archive everything.** Logs and mod versions are copied into `archive\` (logs under
   `archive\logs\`, packs under `archive\packs\`, source snapshots under `archive\mod_source\`)
   so that deleting the game does not lose history. The live battle log
   `zz_test_deadly_onslaught_log.txt` is currently about 5.4 GB: do not read it whole, never
   open it in an editor, grep or tail it only.
8. **The master spreadsheet is the single source of truth for the roster.** A NEW versioned
   filename per change (`docs\WH3_abilities_master_v<N>_<date>.xlsx` plus `.ods`), never
   overwrite an older version, older versions must stay byte-unchanged, newest version wins.
   Every new version is re-opened from disk and verified: same data-row count as the
   previous version, changed abilities show their new trigger text, and the Numbers sheet
   reconciles to the tracker.
9. **The user reserves trigger design.** Give the mechanism, two or three trigger options
   with the evidence for each, and a recommendation, then wait for approval. Never pick a
   trigger and ship it because it looks obviously right.
10. **The trigger follows the effect, per ability** (round 123, "please learn from this
   example"). Name the stat each ability changes and the moment it pays off, then pick the
   trigger per ability; never put a whole group on the family its look-alikes use. A melee-only
   stat (melee attack, melee defence, weapon damage) never goes on a trigger with a missile
   arm. Enemy speed reductions fire in melee or on the charge (`charge_or_melee`), never on an
   enemy merely passing by. An effect that only helps before something else happens (Daemonic
   Possession, before a friendly spell) is not automated.
11. **Read the tracker's decision before proposing an ability.** The workbook does not carry the
   questionnaire decisions (`rejected (...)`, `skipped (revisit)`); the tracker does. Rounds
   122-123 shipped four abilities the user had earlier rejected or skipped because only the
   workbook was read (kept by the user's 2026-10-28 ruling). Quote any earlier decision in the
   proposal.
12. **The left-hand wheel only** (user ruling 2026-11-03). Whatever the game puts on the
   right-hand bar (spells, and runes) gets no letter and no trigger: a `button_spell...` button
   is never claimed. The same key on a wheel button (e.g. an item- or ability-granted rune) is
   ours as usual. The round-124 spell-bar badge placement worked but is removed: activating one
   rune locks the others, so automating them makes little sense.

Current roster (round 137): 698 ABILITIES entries / 750 ability keys / 58 trigger evaluator families.
Wheel audit (workbook v29): 1,123 in-wheel, 677 excluded, of 1,800 inventory rows; 750 implemented,
373 not implemented among the included (24 of them skipped by user decision).

## 3. BUILD AND INSTALL

RPFM drives the packing over a WebSocket on port 45127.

```
cd C:/Users/vlady/Desktop/WH3_mod/tools/rpfm && ./rpfm_server.exe   # background, then wait
sleep 4
cd C:/Users/vlady/Desktop/WH3_mod/tools && uv run --quiet --with websockets python ../mod_source/releases/20261109_morale_harness136/build_and_install137.py 2>&1 | tail -12
```

- Expect `installed md5 <hash>` and `IDENTICAL True`. The server exits itself after
  `ClientDisconnecting`; stop it if it lingers.
- `tools\build_and_install.py` is a STALE generation (generation-92 content gates against a
  generation-99+ mod: it fails 13 CONTENT gates while every PATH step passes). Each round
  clones its own builder into `mod_source\releases\<round>\build_and_install<NN>.py`; run
  that one. Never "fix" the old builder's content gates by guessing: diff against the round's
  own builder and report the drift.
- Verify the INSTALLED artifact, not just the built one: `md5sum` the pack in the game `data\`
  folder and report that hash. Pack files are stored uncompressed, so
  `grep -cF "<new log string>" <installed.pack>` also proves the change shipped.
- The build asserts all five shipped files are byte-identical to source (`MATCHES SOURCE:
  True` five times) and refuses to ship any `zz_probe_` path.

## 4. TESTING DISCIPLINE

Harness suites are Lua, run under lupa through the project runner:

```
cd C:/Users/vlady/Desktop/WH3_mod
uv run --with lupa python tools/run_harness.py mod_source/releases/<round>/harness<NN>.lua
```

- Green means the output ends `HARNESS OK - all checks passed`.
- A RED control must reproduce the in-game failure before a GREEN pass is trusted. Run the
  harness against the pre-change source (or the annotated copy) with `--red <live.lua>
  <ann.lua>`, confirm the failure text matches what the user saw in battle, then run GREEN on
  the fixed source. A green suite that never went red proves nothing.
- **Sign-off rounds run the FULL suite** (harness136: 5,948 checks; it takes about 10 s) and produce a workbook
  version. **Tuning rounds run only the affected harness section** (the user approved this
  split), and you must state plainly that the full suite and workbook were skipped and what
  that leaves unverified. Never imply a full suite ran.
- Harnesses live in their release folder and are never edited after the fact; one numbered
  harness per round; every earlier section stays in the file with its boundary pin so a full
  run stays one command.
- Pins must be rebased deliberately and documented in the round doc (old value, new value,
  why). Never delete a pin to make a suite pass. When a full run fails, discriminate first: a
  failure whose content is byte-equal to a pre-change backup is a stale mirror pin, not a
  regression.
- Mock harness conventions: `bm`, `core`, `UIComponent`, `common.get_localised_string`,
  `is_string`, `find_uicomponent` are mocked; log lines go to an `out_lines` table through a
  global `out(s)`; assert with `l:find(t, 1, true)`.

## 5. ENGINE FACTS (hard-won; do not rediscover)

- `battle_unit:position()` is the unit CENTRE.
- The ground plane is X/Z. `get_y()` is HEIGHT, so an X/Y read measures altitude. Horizontal
  distance is `sqrt(dx*dx + dz*dz)` over `position()` getters.
- `unit_distance` is bounding box EDGE to EDGE, so it cannot answer "is A directly under B":
  two formations can have box edges 0.5 m apart with centres 15 m apart.
- There is NO radius or bounding box read in the API. A formation footprint must come from
  one documented constant.
- `ordered_position()` is the destination, usable as a heading source, unreliable for units
  that are attacking.
- `HealthPercent` returns a 0..1 fraction, not 0..100.
- `perform_special_ability` issues an ORDER. A second cast in the same tick REPLACES the
  first, so per-caster serialisation and per-ability wind-up gates are required.
- The engine tolerates `can_perform_special_ability` = true with an empty charge pool for
  multi-use abilities, so an explicit charge gate is required.
- Controller handles do not survive: re-fetch enemy and ally handles from the script unit
  enumerators on the same tick as the cast. A stale handle returns accepted = true, consumes
  no cooldown and applies nothing.
- `find_uicomponent` returns `false` on a miss, and wrapping it crashes the game. Never use it
  inside a probe.
- Enemy-targeted abilities cast at the ENEMY, ally-targeted at the chosen ALLY, never the
  owner. The self-centred auras cast on the owner by design.
- `battle_unit:is_infantry()`, `is_moving()`, `is_moving_fast()`, `number_of_men_alive()` and
  `is_engaged()` (via the melee table) are the per-unit reads the triggers use.
- The engine can ACCEPT a multi-use cast and never execute it (Isha's Rain, 2026-11-03), and
  `can_perform_special_ability` stays true for multi-use abilities, so it cannot tell. The only
  signal is the ability button's state ('active'/'hover' = ready), which exists only for the
  selected unit. Trust only the ENGINE's live selection (`selected_ui_ids`, exactly one): the
  mod's `selected_unit_id` tracker keeps the last unit when nothing is selected.
- After a box selection the engine may NEVER send the "deselected" callback events (2026-11-03:
  two ghosts stayed selected all battle). The unit cards are right: since round 129 a unit whose
  card reads a known unselected state for 2 polls leaves `selected_ui_ids`. The mod bans
  `string.find` (a standing pin); use lookup tables.
- Recharges can be shorter in battle than the table (campaign bonuses): Isha's Rain and Pigeon
  Bomb were ready about 83 s after a cast against a 120 s table value (2026-11-03). No API read.
- No battle API read exists for a unit's cooldown/charges, or for line of sight.
- STANCES are never automated for now (user, 2026-11-01): a stance chooser that weighs the unit's
  mutually exclusive stances is last priority. Round 131 removed the 9 that were automated.
- Field counts describe the user's orders in that battle (e.g. a character he sent into melee
  does not shoot). Never use them as an argument against a trigger (user, 2026-11-01).
- Game version 9.0.5 (patch 2026-11-03) is the data baseline since round 132: `gamedata\wh3\` was re-extracted,
  drift in `docs\DRIFT_2026-11-08_patch905.md`. After every game patch: re-extract, diff, fix the mod's
  derived data (ranges, uses, wind-ups, reload table) BEFORE any other work.
- Claude cannot click in Warhammer III (2026-11-08): screenshots, mouse movement and keys work, clicks
  are ignored (plain and SendInput modifier clicks). The user builds and fights the QA battle.
- Inline Python in a bash heredoc turns Windows paths like `ound132` into escape characters. Put any
  generator with Windows paths in a FILE with raw strings (it broke the round-133 builder once).
- No battle read exists for a RAMPAGING unit (round 137: the user dropped the rampage arm for that reason).
- Vigour (user, 2026-11-09): a vigour restorer is reviewed ONE BY ONE ("the vigor buff is many times secondary");
  "Tired or worse" (fatigue_state) is the line. The trigger audit lists them as R8.
- The mock's under-fire read is `def.missile` (a later definition overrides `def.in_range`).
- The mock engine accepts every repeat cast (no cooldown refusal): a world that counts casts must
  stop inside the 2 s guard after the first one.
- Enemy-targeted abilities carry the game's own target rule (special_ability_to_invalid_target_flags). Since round
  135 an entry's `target_class` (commander / large / large_single) filters the shared enemy picker; the large and
  single-entity sets are GENERATED by `tools\gen_unit_size_keys.py` (mount entity counts). Check the flags of every
  new enemy-targeted ability. Round 136 added `not_flying` (live is_currently_flying(), exact false only);
  5 rarer flags (undead, Entangle's flying, missile unit, caster) are not handled yet.
- Builder order (fixed 2026-11-09, `build_and_install135.py` onward): only the build output is cleared early; the
  installed pack is overwritten by the INSTALL step after every gate, so a refused build leaves it in place
  (proven by `tools\make_refusal_probe135.py`). Earlier builders deleted it first; never run one of those.
  Two RPFM builds of the same source differ in 2 header bytes (offsets 25-26): verify contents, not the md5.

## 6. DOCS

| File | Role |
|---|---|
| `docs\WH3_ability_tracker.md` | the authoritative inventory: every ability, status, proposed activation |
| `docs\WH3_abilities_master_v29_2026-11-09.xlsx` | the current master spreadsheet (versioned; newest wins); built by `tools\make_xlsx_v29.py`, verified by `tools\verify_xlsx_v29.py`; the `.ods` twin comes from headless LibreOffice (`soffice --headless --convert-to ods`) |
| `docs\WH3_ability_database_master.md` | the master database, 1,800 rows, one per key: effect, restrictions, real range, 70% bound, status, plain-English trigger |
| `docs\WH3_round*.md` | one document per round: the ruling, the change, the proof, the installed md5 |
| `docs\WH3_auto_ability_annotated.lua` | the annotated copy of the source, edited identically to it |
| `docs\backups\round<N>\` | pre-round source snapshots, used for RED controls |

Keep the tracker, the database and the spreadsheet consistent in the same round that changes
the roster, and regenerate the database with `tools\build_ability_database.py`.

## 7. COMMUNICATION

- The user cannot read Lua fluently. Explain logic line by line in plain words, and say what
  a change does to what he sees in battle.
- He wants blunt, honest assessment, including when a request is unbuildable or a plan is
  wrong. Do not soften it and do not agree with him to be agreeable.
- He sometimes writes "redact" when he means "draft". Read it as draft.
- He works in English, Spanish, Russian and French.
- Put the substance in the chat reply. An attachment alone is not a deliverable for him.

## 8. AVAILABLE SKILLS

`.claude\skills\` in this bundle holds the Hermes skills that carry the deep procedure for
this work. Read `wh3-battle-mod-iteration\SKILL.md` and its `references\` before editing the
mod; `steam-workshop-research\references\rpfm-server-protocol.md` for the pack tool;
`systematic-debugging` and `review-findings-verification` for diagnosis and critique handling;
`xlsx` for the spreadsheet; `codebase-inspection` for LOC and structure measurement;
`grounded-citations` for cited claims; `python-desktop-gui` for a viewer window.

## 9. OPEN ITEMS

- Game data moved out of Temp on 2026-11-01 (round 124): `gamedata\wh3\` regenerated from the
  installed game, drift recorded in `gamedata\DRIFT_2026-11-01.md` (no mod constant moved).
  Earlier rounds' builders and harnesses still name Temp; they are history, not re-run.
  `gamedata\wh3_layouts\` is empty (lost to Temp before the move): re-extract from `ui3.pack`
  before the next layout patch.
- The inventory's in-wheel rule omits `source_type = passive`. Two castable keys hide there:
  Grombrindal Has No Fear (a visible wheel button in the 2026-10-28 log) and Scry Orb. They need
  inventory rows at the next sign-off.
- THE FIRING FLAG (round 126, read-only, awaiting the field result): ammo_left() drop = FIRING
  ON; CAST POINT = first shot + 0.5 x reload; FIRING OFF = no drop for max(2 x reload, 20 s)
  (round 127: vehicles and hunter characters fire slower than their table reload). Reload
  comes from `FOURTH.RELOAD_S`, GENERATED by `tools\gen_reload_table.py` (564 ranged units,
  base x (1 - reload skill/100)); the build refuses a table that differs from the game data.
  "Target in range" precedes almost every first shot (37/38) but is NOT sufficient (41% of
  regular units' and 84% of characters' in-range periods had no shot), so casts wait for the
  cast point. Round 130 is the first to trigger on it: Restock! (`ally_ammo_low`), Ballistics
  Calibration (`allies_firing_aura`) and Skjalandir's Fall (`melee_or_shooting_into_melee`). Not
  field-tested yet. Round 131 added the shooting auras (`allies_firing_aura`: 1 shooter, the caster
  counting), `self_or_ally_shooting`, `melee_or_self_or_ally_shooting` and Potion of Farsight's
  `no_enemy_in_range_within_boost` (range x 1.21). Next on the user's plan: field test, then trigger
  options for Embers of the Phoenix, Horn of Vaul and the 8 Enchanted Metallurgy keys, then the next
  survey group (`docs/WH3_remaining_abilities_survey_2026-11-01.md`); casting BEFORE the first shot
  later (needs its own ruling).
- The five runes the 2026-11-01 log saw only on the spell bar (Breaking, Slowness, Speed,
  Negation, Oath and Steel) stay in ABILITIES (a wheel copy would be ours); decide their
  workbook status at the next sign-off.
- Deferred by the user (2026-11-01): the next-batch candidates Silver Horn of Vengeance and
  Grombrindal Has No Fear. The two other Restock-type keys (More Powder!, the gunnery-school Restock!)
  have the same effect but were not in the round-130 ruling.
- The charge hold uses the table recharge, about 37 s too long in the user's campaign (user
  chose "selection fix only" on 2026-11-03; learning the recharge from the button was option a).
- `archive\packs\` has no pack between 2026-10-04 and round 122; archive every installed pack from now on.
