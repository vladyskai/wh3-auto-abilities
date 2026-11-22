# CLAUDE.md

Project memory for Claude Code. Read this before touching anything. These are standing user
rulings accumulated over many rounds, not suggestions. Apply them; do not re-ask.

## 1. PROJECT

A WARHAMMER III battle-script Lua mod that auto-fires special abilities on per-ability
triggers. It polls the battle state, walks the units the player has armed, calls a shared
trigger evaluator for each entry, and casts when the evaluator says fire.

- Mod source (the ONLY file edited per round):
  `C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua`
  (about 1.6 MB, about 27,700 lines)
- Packed as a Movie pack and installed as
  `zz_test_deadly_onslaught.pack` in
  `C:\Program Files (x86)\Steam\steamapps\common\Total War WARHAMMER III\data\`
- Installed build: md5 `d5535679368f82138f341b6138667818`, 1,625,301 bytes
  (round 201, 2026-11-22: the five Master Runes removed, Endless Whirlwind of Death added). RPFM packs are not byte-reproducible: compare contents, not the md5. Always re-measure instead of trusting this line.
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

Pack contents are FIVE files since round 194, and every build verifies all five are byte-identical to
source (paths below relative to `mod_source\`):

- `script\battle\mod\zz_test_deadly_onslaught.lua`
- `ui\templates\zz_auto_badge.twui.xml`
- `ui\zz_auto\auto_badge.png`
- `ui\zz_auto\blank.png`
- `script\mct\settings\smart_ability_autocast.lua` (round 194: the OPTIONAL MCT page, only MCT loads it)

RETIRED (round 166, user: remove the card's "Automatic: click the M/A badge ..." note):
`ui\common ui\special_ability_tooltip.twui.xml` existed only for that line (a pre-9.0.5 copy of the game's layout).
The builder REFUSES a pack that carries it; copy in `archive\mod_source\round166_retired\`.

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
(`tools\audit_triggers.py`, `docs\WH3_trigger_audit_<date>.md`) feeds the batches; re-run it and
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
3. **The range rule** (round 188, user ruling 2026-11-21: "C. Your rule, the larger of 70% and real minus 20 m,
   everywhere."). Every cast-range bound is `max(floor(real_range * 0.70), real_range - 20)`, where the real
   range is `target_intercept_range` from the game's own tables. AURAS keep `floor(effect_range * 0.70)` (0 means
   self-only); below 67 m the two rules agree. It overruled a 25 m value the user had field-tuned himself (the
   70% era). Shipped as `FOURTH.RANGE_FRACTION = 0.70` + `FOURTH.RANGE_MARGIN_M = 20` (`FOURTH.range_bound`); the
   build asserts every ENEMY_CAST / ALLY_CAST constant equals the rule. The single documented override is a metre
   value the user personally sets for an overlap/underfoot test (air drop), which is a named
   constant, exempted explicitly from the range map, and commented as a test value. SECOND exception (user ruling
   2026-11-20, round 182): the Executioner (a single-entity target) uses 90% of its real range
   (`FOURTH.SINGLE_RANGE_FRACTION`, entry field `range_frac = 0.90`); the build refuses it on any other entry.
   Since round 188 it takes the larger of its 90% and the rule (250 m: 230).
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
   `zz_test_deadly_onslaught_log.txt` is currently about 1 GB: do not read it whole, never
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

Current roster (round 201): 982 ABILITIES entries / 1,035 ability keys / 141 trigger evaluator families.
Wheel audit (workbook v79): 1,115 in-wheel, 687 excluded, of 1,802 inventory rows; 1,035 implemented,
80 not implemented among the included: 80 decided by the user, 0 OPEN (round 185 closed the rule-shut review;
the text below about rule-shut rows is history) = shut by an old RULE (the 2026-10-09
family decisions, 'auto:' exclusions, collection-time 'unsuitable' skips), never ruled on by the user one by one.
A rule is not a user decision: the progress page counts them open since round 161 (round 159's '0 open' was wrong).

## 3. BUILD AND INSTALL

RPFM drives the packing over a WebSocket on port 45127.

```
cd C:/Users/vlady/Desktop/WH3_mod/tools/rpfm && ./rpfm_server.exe   # background, then wait
sleep 4
cd C:/Users/vlady/Desktop/WH3_mod/tools && uv run --quiet --with websockets --with lupa python ../mod_source/releases/20261122_masterrunes_harness199/build_and_install201.py 2>&1 | tail -12
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
- Since round 174 the builder COMPILES the script (lupa; hence `--with lupa`) and refuses one that does not compile:
  every other gate compares text, and a broken table regeneration once passed them all.
- The build asserts all five shipped files are byte-identical to source (`MATCHES SOURCE:
  True` four times) and refuses to ship any `zz_probe_` path.

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
- **Sign-off rounds run the FULL suite** (harness199: 8,245 checks; it takes about 2 minutes) and produce a workbook
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
- A cast stops its moving caster ONLY when the ability plays a cast animation (unit_special_abilities.wind_up_stance
  not empty; field 4 of 4, round 168). GENERATED FOURTH.ANIM_TEXT (tools\gen_anim_keys.py); FOURTH.blob_still is the
  one stand-still gate and asks it first. User ruling 2026-11-17: 'Option A, animation decides all'.
- The ground plane is X/Z. `get_y()` is HEIGHT, so an X/Y read measures altitude. Horizontal
  distance is `sqrt(dx*dx + dz*dz)` over `position()` getters.
- `unit_distance` is bounding box EDGE to EDGE, so it cannot answer "is A directly under B":
  two formations can have box edges 0.5 m apart with centres 15 m apart.
- There is NO radius, depth or bounding box read in the API. ordered_width() (the ORDERED formation's frontage, metres)
  exists; depth is only an estimate (width, men, the game's unit_spacings table: gamedata\wh3\unit_spacings.tsv).
  The air drop still uses its one documented constant. Field (2026-11-13): ordered_width() answers on enemies too.
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
- Claude CAN click in Warhammer III (2026-11-20; the 2026-11-08 'cannot click' was wrong): the game moves its own
  cursor only from RELATIVE mouse input and ignores the computer-use tool's absolute cursor jumps, so those clicks
  land at the game's stale cursor. Use `tools\game_mouse.ps1 -x X -y Y [-click|-right]` (corner, then relative
  SendInput steps; x, y in the DPI-unaware 1600 x 900 space = screenshot frame x 1600/1456). Proven at the main
  menu (Battle submenu opened and closed). The game window must be in front; it starts MINIMIZED when launched
  from Claude (restore it with ShowWindow), and open_application on Warhammer3 starts a SECOND copy (Mutex error).
  The user still builds and fights the QA battle (no self-playing build). Positions in the mod's INVENTORY log lines
  use the same 1600 x 900 space (game at 2560 x 1440, ui_scale 1.6), so they can be aimed at directly.
- BADGE PLACEMENT DEPENDS ON UI SCALE (found 2026-11-20): the M/A badges and the ALL button dock to hud_battle's
  BOTTOM-CENTRE with fixed offsets (slot 1 -865,-209; ALL -923,0) while the wheel docks bottom-LEFT. At ui_scale 1.6
  (UI 1600 x 900) the wheel sits at (96,629), 216 px above the WHEEL_SLOT table, and the badges land at x = -65 /
  -123 (off screen); only the slot-2 badge peeks in at x = 5. FIXED in round 187: FOURTH.ui_shift_tick moves every
  badge and the ALL button by (wheel shift - bottom-centre shift) from the tuned 1984 x 1116 frame (refs
  ability_parent 42,893 / orders_parent 691,1055; Position() only; every 40 ui ticks = 2 s; the ui tick runs every
  50 ms). Not yet seen in game at 1.6.
- Inline Python in a bash heredoc turns Windows paths like `\round132` into escape characters. Put any
  generator with Windows paths in a FILE with raw strings (it broke the round-133 builder once). Round 158 again:
  a heredoc turned `\b` into a backspace byte and `\n` into a real newline. Write generators with the Write tool.
- QA battles (docs\WH3_QA_army_list_2026-11-09.md): read a battle by cutting the log from its byte offset before
  the battle (`tail -c +<old size+1>`), never the whole log. Skirmish mode: one Lord per army, and some items
  (Potion of Speed) are not offered. QA battle 1 (2026-11-09) proved is_under_missile_attack() on own units.
- The firing flag (round 140, user ruling 2026-11-13): "Unless the unit can fire while moving, shooting and moving are
  incompatible." FOURTH.can_shoot_now guards every firing-flag read; the fire_move set is GENERATED by
  `tools\gen_fire_move_keys.py` (unit attribute mounted_fire_move). The flag alone lags 2 x reload after the last shot.
- A Hellcannon (artillery) cannot receive a non-missile attack order, and it never RUNS (is_moving_fast always false,
  QA 2026-11-13): use is_moving() for it.
- After a build: archive the pack ONLY if the installed md5 changed and the new marker is in it (round 142: a refused
  build left the old pack installed and an unconditional copy archived it under the new name).
- An ability's recharge starts when its effect ENDS (Restore: 24 s effect + 60 s recharge); the charge hold counts the
  recharge from the cast, so one early attempt is refused "on cooldown" and the mod backs off (harmless, 2026-11-13).
- Recharging (round 141): the mod remembers each ACCEPTED cast (FOURTH.note_cast) and its lock = effect + recharge from
  the GENERATED FOURTH.RECHARGE_S (`tools\gen_recharge_keys.py`), stored as ONE text read at load so no key appears
  in quotes twice (harness pins count quoted keys). It cannot see player-clicked spells/abilities or campaign bonuses.
- Mock: helper abilities must be marked not ready after their first cast (`can_keys`), or the mock's accept-every-
  repeat lets them take the caster's cast slot every 2 s.
- No battle read exists for a RAMPAGING unit (round 137: the user dropped the rampage arm for that reason).
- Vigour (user, 2026-11-09): NO vigour trigger is added to a vigour restorer ("Skip the exercise, I reconsidered
  and there is no need to add this trigger"). Do not propose it again; R8 in the audit lists them as ruled.
- The mock's under-fire read is `def.missile` (a later definition overrides `def.in_range`).
- The mock engine accepts every repeat cast (no cooldown refusal): a world that counts casts must
  stop inside the 2 s guard after the first one.
- Enemy-targeted abilities carry the game's own target rule (special_ability_to_invalid_target_flags). Since round
  135 an entry's `target_class` (commander / large / large_single) filters the shared enemy picker; the large and
  single-entity sets are GENERATED by `tools\gen_unit_size_keys.py` (mount entity counts). Check the flags of every
  new enemy-targeted ability. Classes: commander, large, large_single, not_flying (live is_currently_flying()),
  not_undead (GENERATED by `tools\gen_undead_keys.py`), missile; a spellcaster rule maps to commander (no read).
  Every automated enemy-targeted ability honours its rule since round 138 (siege-platform flags not modelled).
- Enemy ammo_left() (round 138, Missile Mirror's enemy_missile_shooting) is UNPROVEN on enemies: fail-closed,
  one log line if unreadable.
- The build's INSTALL step fails with WinError 32 while the game runs (the pack is locked): ask the user to close the
  game; never kill it. The installed pack stays untouched (round 152).
- Builder order (fixed 2026-11-09, `build_and_install135.py` onward): only the build output is cleared early; the
  installed pack is overwritten by the INSTALL step after every gate, so a refused build leaves it in place
  (proven by `tools\make_refusal_probe135.py`). Earlier builders deleted it first; never run one of those.
  Two RPFM builds of the same source differ in 2 header bytes (offsets 25-26): verify contents, not the md5.

## 6. DOCS

| File | Role |
|---|---|
| `docs\WH3_ability_tracker.md` | the authoritative inventory: every ability, status, proposed activation |
| `docs\WH3_battle_knowledge.md` | battle mechanics research (sourced; ASSUMPTION marks the unsourced): read it before proposing a trigger |
| `docs\WH3_overnight_audit_2026-11-17.md` | the per-ability trigger scores (1-5), the restriction gaps, the open mechanics questions, feature ideas |
| `docs\WH3_abilities_master_v79_2026-11-22.xlsx` | the current master spreadsheet (versioned, newest wins). Built by `tools\make_xlsx_v79.py`, verified by `tools\verify_xlsx_v79.py <v78 md5> <pack md5>` (v79 = v78 + round 201: the 5 Master Runes EXCLUDED, Endless Whirlwind of Death x2 IMPLEMENTED, Numbers recomputed, Cards rebuilt. v78 = v77 + the round-199 sentences on 41 rows and 10 cards. v77 = v76 + the round-198 texts: 10 trigger texts and 3 cards. v76 = v75 + the FALLBACK sentence on the 70 blob-family rows. v75 implemented Scry-Orb. v74 added 2 rows and moved the 5 spell-bar runes to EXCLUDED. Numbers are recomputed from the rows by make_xlsx_v74's method, Cards come from the harness run); the `.ods` twin comes from headless LibreOffice (`soffice --headless --convert-to ods`) |
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

- WORKING DOCS (2026-11-20): `docs\WH3_open_points.md` is the living list of open points. The 55 rule-shut + 9 revisit
  abilities are reviewed in `docs\WH3_rule_shut_review_2026-11-20.md`; its LIVE copy is the Claude Docs doc 'Rule-shut
  abilities review' (https://claude.ai/artifact/HvLbtHifSNsbH8aeWcER5h, project 8904b7db-9839-4dad-bfcb-b6a2f5b4bd88):
  a Ruling dropdown per row and comment threads. READ THE RULINGS FROM THAT DOC (dropdowns AND threads) before building.
- WRITING (user 2026-11-21): no semicolons in any prose for the user ("stop using ';', nobody uses them"), same as em
  dashes. Workshop text: never "the ALL button" (say "a button in battle that ..."), no "battle only".
- ROUND 201 (2026-11-22, `docs\WH3_round201_master_runes.md`). FIELD (the user's Dwarf battle on the RELEASE build, no
  log): Master Rune of Slowness, a RIGHT-hand-bar button, FIRED BY ITSELF (its entry rode a default-armed family, and
  a cast needs no badge). Rulings: "do it" on removing the five Master Runes the game marks as runes (Breaking,
  Negation, Slowness, Speed, Oath & Steel) and "do it" on Endless Whirlwind of Death = the trigger of Whirlwind of
  Death (2 new entries on melee_unwavering; the tracker's old 'rejected (friendly fire)' was wrong by the data: the
  same vortexes, affects_allies false). PERMANENT BUILD GATE: no key with unit_abilities.source_type = rune (12 keys)
  may appear in the script. Master Rune of Flight / Immolation are source_type active and stay (asked the user where
  he sees them, no answer yet). Harness 199: old worlds moved to siblings (harness 123/124 Hunter's Trap, harness 133
  G3 Slippery). The release pack was rebuilt (`build_release.py --pack`, md5 007f09d5..., cast trace identical: 2,083
  worlds / 1,656 casts; release_cast_trace.py takes the harness as a 3rd argument and must run from the project
  root). The Workshop item (HIDDEN, title + text set by Claude in the Steam app through computer use: Chrome is not
  signed in to Steam) still carries the ROUND 199 pack: the user must press UPDATE in TW Launcher (Legacy). Both
  packs are in the data folder (the release stands down). FIELD-CONFIRMED by the user 2026-11-22 ("It seems those
  are fixed"; archive\logsattle_20261122_r201_dwarfs.txt, bytes 983,121,663-1,005,059,703). Same battle: the Fiery
  Ring of Thori (enemy_wave, armed on both Master Engineers) never fired: toolseplay_wave_log.py on the MAP rows
  shows one of our units within 16 m (radius 6 + 10) of every 72 m path in 177 of 177 in-range snapshots, 0 clear
  moments (an army of ~29 units, mostly Lords and Heroes in one mob). By design (round 162), explained to the user,
  no ruling asked. SECOND battle (archive\logsattle_20261122_r201_zombies.txt, bytes 1,005,059,703-1,012,254,884:
  one Master Engineer + Miners vs 4 Zombie units): the ring held again, the Miners stood within 16 m of every
  caster-to-target path (25 of 25 snapshots with a standing enemy in range). The user's screenshot shows the GAME lets
  the player place the wave and ROTATE it ('Hold left mouse button and drag to rotate'): he asked whether the mod
  uses that. It does NOT: every wave / cone is tested on the caster-to-target heading only and cast in the unit form
  (ground form passes orientation 0, width 0). PROPOSED (open point 25, waiting): FREE AIM = test several headings
  and start points, cast with perform_special_ability_ground(key, pos, ORIENTATION, 0). The orientation argument has
  NEVER been tried in a battle: a probe comes first. Next battle from byte 1,012,254,884. DONATIONS (researched
  2026-11-22): SEGA's EULA and CA's page forbid selling mods and say 'not permitted to charge or ask for money', no
  source allows or names tips, big mods carry Patreon / Ko-fi links: a tolerated grey area. PayPal is excluded by the
  user. Recommended Ko-fi with Stripe. GIFS: the user records the clips (Game Bar), Claude converts (ffmpeg is
  installed). A leftover scratch folder C:\t_red (two harness copies) could not be deleted by Claude.
- ROUND 200 (2026-11-22, "please prepare the pack for me to upload to steam workshop"; `docs\WH3_round200_workshop_release.md`).
  THE RELEASE IS GENERATED: `tools\build_release.py` (`--pack` needs the RPFM server; `--test <path>` writes the variant
  with the test switches for the harness) turns the development script into
  mod_source\release\script\battle\mod\smart_ability_autocast.lua: log() is an empty function (the whole logging section
  is cut), the five log-only periodic calls are gone (dial dump, inventory sweep, map probe, heartbeat, tick line), the
  ZZ_AUTO_TEST_* reads become nil, the zz_badge_* / zz_all_* console functions are nil'ed at the end, a multiplayer battle
  returns at once, and the release STANDS DOWN when the development build is loaded too (zz_badge_set ~= nil at load and
  at the top of poll / ui_tick / the fast pass). NEVER edit the release script by hand: change the development script,
  run the round, then `build_release.py --pack`. It builds smart_ability_autocast.pack (type Mod) and copies it and
  mod_source\workshop\smart_ability_autocast.png into the game's data folder (a SECOND file of ours there, asked for by
  the user; the test pack is not touched). Workshop text: mod_source\workshop\description.txt. PROOF METHOD: the cast
  trace (tools/release_cast_trace.py <out dir> <release-test script>: every perform_special_ability order of the full suite recorded on both builds, 2,067 worlds /
  1,652 casts identical). The harness loads many copies into ONE Lua state: reset zz_badge_set = nil per world or the
  release guard trips. ENGINE FACTS from the game's own scripts (data_script.pack, extracted with
  tools\extract_ui_layouts.py get data_script.pack script/_lib/<file>): bm:is_multiplayer() is real in battle (12 uses,
  battle_tours.lua); bm:is_benchmarking_mode() exists; get_scriptunits_for_main_enemy_army_to_local_player = army 1 of
  the non-player alliance and get_scriptunits_for_local_players_army = the local army only (reinforcing and allied
  armies are NOT read: confirmed, no longer an assumption); no replay read found; common.vfs_exists not found there.
  The old probe pack zz_probe_dist.pack (20 KB, 2026-10-10) was REMOVED from the game's data folder on 2026-11-22
  (user: "Yes, remove it"); copy in archive\packs\zz_probe_dist_20261010_removed_20261122.pack (md5 d4e67cfb...).
  NOT DONE: the upload itself (the user's account, TW Launcher (Legacy), tag Battle).
- ROUND 199 (2026-11-22, the review's second replies; `docs\WH3_round199_review_fixes2.md`). Row 5 "okay, then fix":
  FOURTH.KEY_LOWER (a listed key with a capital letter, lowered at load) joins the badge's equality compare. Row 9
  "please implement, but also include the caster as I tested and it could cast on the caster": THE ALLY ARM, entry
  field ally_value_arm (true on 8 entries, "only" on Wild Abandon and The Hand of Dust: target_self false AND no
  ground form, the Favour of the Fay case). FOURTH.ally_arm_wrap wraps the entry's evaluator at load: the caster's own
  trigger, plus ab_pick_ally 'value_melee' inside ally_range_real, the more valuable wins, the caster on a tie. Cards:
  FOURTH.CARD_ALLY_ARM / CARD_ALLY_ONLY. ENGINE FACT (user test): Cash Cascade (target_self false, friend + ground)
  FIRES when ordered at its own caster, so target_self false does not refuse an area ability with a ground form.
  Row 10 "agreed, please fix": FOURTH.enemy_is_infantry refuses the generated large set and a flying unit first.
  Row 12 "agreed, implement": ability.remembered = the battle's START (never changed by a click),
  ability.remember_next = what the file is written from (the last click wins). The user: Swordsmen have no active
  ability (use a unit that owns one in examples). NOT VERIFIED: an area ability ordered at an ALLY unit. All four
  rows of the review that waited are now built. Next battle from byte 978,682,624 (re-measure).
- ROUND 198 (2026-11-22, the overnight review `docs\WH3_overnight_review_2026-11-22.md`; the user replied row by row:
  "fix" on 1, 2, 3, 6, 7, 8, 11). BUILT: the per-unit serial window is re-armed when the SAME ability repeats (a closed
  window forgets its armer) and the armer yields one poll to an ability that waited (cast_gate.unit_waiting, else a
  repeater starves the unit). FOURTH.entry_reset(ability, unit) = the poll's per-entry slot reset, called by the air-drop
  fast pass too (it inherited the last poll's chosen targets). A NEW per-entry slot goes into entry_reset, nowhere else.
  Get Tha Gitz! hold row. The Necromancer (Undeath) on a Nightmare: land key added to commander_keys. slow_aura and
  guard_aura call FOURTH.fast_enemy_near (round 192). Entry field no_self (Favour of the Fay, Shielding Swarm x2: the
  game's target_self false; FOURTH.ab_no_self, FOURTH.CARD_TIP_NOSELF; the build compares no_self with the game table).
  BUGMAN_CLEAR_M 55 (a keep-out distance takes no 70% cut). The builder now also compiles the script on Lua 5.1
  (`lupa.lua51`; lupa's default is 5.5; the harness itself uses goto, so it runs on 5.5 or LuaJIT, not on plain 5.1).
  ENGINE FACT (user test 2026-11-22): a ground-only key ordered at an enemy UNIT fires on that unit (Heaven's Flash),
  so the round-184 'MUST join enemy_ground_keys' is not a must. WAITING FOR RULINGS: review rows 9 (ten ally-targeted
  keys still cast on the caster, target_self false: the game refuses them), 10 (the bombardments' infantry test trusts
  is_infantry() alone), 12 (a click flips every untouched unit of the same type in the same battle: proposed option A,
  the type memory applies at battle start only). Row 5 (Doom & Darkness gunnery school, capital B in the game's key: the
  badge compare lowercases, so it can never be claimed) is NOT fixed: the user does not see the ability on the Land Ship.
  The review's release list (no multiplayer guard, logging with no off switch, the UI timer's work, modded Lords unknown,
  one army per side) is open point 22. MOCK: hero defs with hp_frac shadow health_percent (set both). Lesson again: a
  heredoc turned \n inside a Python string into real newlines (tools written with the Write tool only). Harness dev
  loop: DEV=<path> tools\make_harness197.py writes a copy that runs only the new section. Next battle from byte
  978,682,624.
- ROUND 197 (2026-11-21, "A: whole army"): the blob family (enemy_blob, enemy_blob_vortex, 70 keys) drops its two
  save-it rules (armour for armour-piercing attacks, trash) when no living unit of the WHOLE enemy army, hidden ones
  included, passes them (FOURTH.blob_better_exists, FOURTH.blob_relax, wrappers FOURTH.blob_ap_rule / blob_trash_rule).
  Hidden enemies are only COUNTED, never targeted: a user-ruled exception to round 169. The wanderers keep the plain
  trash rule. TEST-ONLY ZZ_AUTO_TEST_NO_BLOB_FALLBACK / W.blob_fallback_on. FIELD-CONFIRMED by the user ("good
  enough. I just tested"). Workshop preview image APPROVED by the user (2026-11-21, "Looks good"):
  mod_source\workshop\smart_ability_autocast.png, 256 x 256, 71 KB, drawn by tools\make_game_a_3d.py (FINAL: the game's
  own A traced from brand_header_30.cuf, gold brushed 3D, centred + FINAL_NUDGE_X 3 px tuned by the user). The old
  512 px wheel preview (tools\make_preview_png.py) is RETIRED to designs\old_preview_512.png. The upload button is missing because the installed test pack is type Movie: the release pack must be type
  Mod and carry its FINAL name (a Workshop pack cannot be renamed after the first upload).
- ROUND 196 (2026-11-21): the MCT reset FIELD-CONFIRMED ("it worked, well done"). The user prefers the long label
  "Forget the remembered M/A choices": a wrapped label is fine as long as the page sets NO tooltip (no "?" marker).
  Arrow of Kurnous (enemy_blob) held a whole Wood Elves battle: Skeleton Warriors have armour 20 and the blob family's
  armour-piercing rule needs 50 (FOURTH.BLOB_AP_ARMOUR_MIN); the Wight King is a single model. Open point 21: fire
  anyway when no unit in the whole enemy army (visible or hidden) passes the save-it rules, PROPOSED. Next battle from
  byte 946,588,829.
- ROUND 195 (2026-11-21): the MCT page (user screenshot): MCT docks its icon row ("?" tooltip marker, global/floppy
  icons) to the BOTTOM-LEFT of the label box, so a label must fit ONE line (about 14 characters) and the page sets no
  tooltip. Section "Remembered M/A choices" (else MCT shows "Default Category"). After Reset: the button reads Done and
  greys out, the label reads Forgotten. MCT's source is cloned in the scratchpad only (re-clone github.com/chadvandy/mct_wh3).
  Casting before the first shot: PARKED by the user (the probe stays, read-only).
- ROUND 194 (2026-11-21): REMEMBERED M/A STATES (option A, per unit type and ability). A click records the switch in
  smart_ability_autocast_settings.txt next to the game ("<unit type> <marker> A|M", only switches that differ from the
  default). The states live on the ABILITY ENTRY (ability.remembered[type]): is_armed sits ABOVE the FOURTH table in the
  file and cannot reach FOURTH (the first attempt crashed every old world). A unit's type is read only for an ability
  with a remembered state. Reset: the OPTIONAL MCT page (5th pack file, script/mct/settings/smart_ability_autocast.lua:
  MCT's 'action' button when present, else a checkbox + MctOptionSettingFinalized), which empties the file and calls the
  global hook smart_ability_autocast_reset_remembered(). MCT is subscribed on this PC (Workshop 2927955021). TEST-ONLY:
  ZZ_AUTO_TEST_NO_REMEMBER (older worlds), ZZ_AUTO_TEST_REMEMBER_FILE / W.remember_on / W.remember_file. Pre-shot test
  battle (archive\logs\battle_20261121_r193_preshot.txt): 5 of 6 would-cast moments were followed by a shot within
  7.25 s, the ruling waits. Next battle from byte 933,407,000.
- ROUND 193 (2026-11-21): Scry-Orb on when_ready. The READ-ONLY pre-shot probe (FOURTH.preshot_now / preshot_probe /
  preshot_first_shot, called from FOURTH.ammo_probe): WOULD CAST / WOULD CAST ENDED / PRESHOT log lines, nothing cast.
  Read a battle with tools\analyze_preshot.py <log> --from <offset>. The test battle is in docs\WH3_round193_preshot.md.
  Round 192's closing rule FIELD-CONFIRMED (Hunter's Snare on charging Cold Ones, archive\logs\battle_20261121_r192_closing.txt).
  Learning the recharge from the button: DROPPED. Patch check: scheduled task 'wh3-game-patch-check' now MONTHLY (1st,
  10:00) plus a one-time check on an announced patch day. Workshop name chosen: "Smart Ability Autocast". Harness runs
  write a mock log into the working folder: delete zz_test_deadly_onslaught_log.txt after each run. Next battle from byte
  905,235,993.
- ROUND 192 (2026-11-21): a fast enemy counts only while RUNNING (is_moving_fast) and CLOSING (the gap to our nearest
  unit shrinks FOURTH.FAST_CLOSING_MPS 3 m/s over FOURTH.FAST_CLOSING_S 1 s; FOURTH.fast_closing; TEST-ONLY
  ZZ_AUTO_TEST_NO_CLOSING keeps older worlds on the old rule, W.closing_on tests it). is_moving_fast() has never been
  read on an ENEMY in a battle: watch the fast arms. Shock Collar / Remouldered: Clan Moulder monsters only (GENERATED
  FOURTH.MOULDER_TEXT, 28 units, code M; the flag NAME unit_is_moulder_monster reads backwards: its loc text says 'Unit
  is not a Clan Moulder Monster'). NEW Grombrindal Has No Fear (melee_or_wavering_aura, 55 m). REMOVED the 5 spell-bar
  runes (the 5 MASTER runes share source_type rune: question to the user). Workbook v74 has 1,802 rows; Scry-Orb open.
  When an entry leaves, its old harness worlds move to a sibling on the same trigger (tools\make_harness191.py).
  Harness runs now take about 2 minutes. Next battle from byte 881,292,588.
- 2026-11-21 (after round 191, no build): the progress page counts ONLY real battles now (game log + archive\logs; it
  had counted the harness logs: 189 of 1,041 keys seen, not 508). The harness writes the mod's log into its working
  folder (78 GB in the project root): never treat a project-root or tools\ log as a battle. Scheduled task
  'wh3-game-patch-check' (monthly since round 193) compares Steam's buildid with tools\game_build_baseline.txt; the patch-fix round
  updates the baseline. Steam Workshop release is REQUIRED (open point 18). Rulings recorded in docs\WH3_open_points.md.
- ROUND 191 (2026-11-21; 'For now, please only implement number 1.'): GROUP 1 of the stand-still audit BUILT. NEW
  FOURTH.STILL_GATE_TRIGGERS (the 8 'at an enemy elsewhere' triggers) + FOURTH.still_wrap: at load each entry on one of
  them gets its evaluator wrapped to ask FOURTH.blob_still first (per ENTRY, because the shared pickers serve other
  triggers too). 40 animated abilities wait (50 workbook rows: an entry with ANY animated key waits whole, e.g. Doom &
  Darkness). audit_stand_still.py counts the wrap (snapshot *_r191.tsv: 63 left in groups 2-6, RULINGS PENDING). Next
  battle from byte 881,292,588.
- ROUND 190 (2026-11-21): FIELD (bytes 860,397,883-881,292,588, archive\logs\battle_20261121_r189_lineoffire.txt): the
  line of fire WORKS (ground read answered; 22 blocks, each ability fired once clear). Amber Bow fired while Markus walked
  and STOPPED him ('canceled his movement, not good'): the shot triggers skipped the round-168 stand-still check
  (shot_caster_ok(unit, false) and five evaluators with no caster check). 'Fix the 8': shot_caster_ok and shot_still_ok
  always ask FOURTH.blob_still; the 8 animated shot abilities wait (Amber Bow, Gaze of Nagash, Damned Pistol,
  Schalkain's Teeth, Goggly / Vindictive Glare, Shem's Burning Gaze, The Black Tongue). AUDIT (open point 16,
  docs\WH3_stand_still_audit_2026-11-21.md, tools\audit_stand_still.py = call-graph closure to blob_still): 33 more
  triggers, 103 animated abilities never check, 6 groups, RULINGS PENDING. The reading copy answers 'false' where the
  live one answers 'nil' in some evaluators (patch both forms). Next battle from byte 881,292,588.
- ROUND 189 (2026-11-21): THE LINE OF FIRE (open point 13 BUILT). User: 'terrain on all 35 and units on all 35. Just
  let's be safe, and if it doesn't fire, that's okay ... It's better for the mod if it doesn't fire.' The 35 entries with a
  key the game marks 'Requires line of sight to the target' (GENERATED FOURTH.LOS_TEXT, tools\gen_los_keys.py, 56 keys)
  take an enemy only along a line clear of every OTHER unit, ours and the enemy's (blob_shape rectangles + 1 m, tops
  2.5 m / 6 m large, live heights: a hill shoots over, a flier passes over) and of the ground (bm:get_terrain_height every
  4 m, line 1.5 m above the caster to 1 m above the target, 0.5 m clearance; first checked within 3 m of a standing
  unit's height). FAIL-CLOSED everywhere. Hook: ONE line in FOURTH.eg_class_ok (FOURTH.eg_los_ok, caster from
  FOURTH.eg_caster set by the poll). The reading copy carries its two log lines as comments (it must stay log-free).
  MOCK: TEST-ONLY global ZZ_AUTO_TEST_NO_LOS (load_world sets it unless W.los_on; older worlds stack units at 0,0,0);
  the mock's bm has no get_terrain_height unless a world sets one. Rebased pin 0zz16 (counts inside ANIM_TEXT now).
  Cackle Fruit field test (user): an arcing throw lobs over our own unit. get_terrain_height NEVER read in a battle yet:
  a 'LINE OF FIRE:' log line means it failed and the 35 hold. Next battle from byte 860,397,883.
- ROUND 188 (2026-11-21): THE RANGE RULE is max(70%, real - 20 m) (rule 3; open point 15 DONE). 391 of 489 bounded
  entries reach further (Focused Shot 230 m, the Executioner 230 m, Accusation 55 m: its old 52 m came from a field
  walk, watch it). Workbook v70 restates 359 trigger texts. LINE OF SIGHT researched (open point 13, waiting for
  a ruling): no script read; the game's UI effect wh3_main_projectile_requires_line_of_sight tags 56 keys, 35 ours;
  bm:get_terrain_height(x, z) exists (unproven). build_ability_database.py now reads a constant with a trailing
  comment (round 188 dropped two). Next battle from byte 852,232,729.
- ROUND 187 (2026-11-21): the badges follow the wheel (see ENGINE FACTS, badge placement). The Wulfhart battle
  (archive\logs\battle_20261121_r186_wulfhart.txt, bytes 822,999,135-845,604,523): Hunter's Snare caught a real
  charge (open point 2 DONE); Focused Shot's first cast made Markus walk 25 m past our own Swordsmen standing across
  the line of fire (flat shot, trajectory_sight low; the cast never fired, the second did): a line-of-fire check is
  proposed (open point 13), NOT built. Next battle from byte 845,604,523.
- ROUND 186 (2026-11-20): Warpstorm Scroll on NEW enemy_most_valuable (shot kind 'value', any model count, its
  target_class flying; no charge arm). User: 'No need to enforce single-entity. No need to enforce charge, treat it
  just as a damage dealer. The slow is not so relevant in this case.' Rule 10 does not bind it (audit R4 ruled). The
  first install hit WinError 32 (the game was running); the user closed it.
- ROUND 185 (2026-11-20, review rows 20-64; 'Review ended, implement pls'): 33 built (13 safe blasts melee_unwavering;
  Glacial Blast, Thundermace melee_clear; Cellular Instability melee_clear_block; Splode da Big 'Un! and the Master Rune
  of Immolation last_stand_clear; Battle Howl x2 + Silver Horn on NEW aura_charge_only; Twilight Horn II; Itzl;
  Bonecrusher; Beastlord's Gaze; Fog of the Damned (enemy_ground_melee_cluster, ground); Locus of Contagion; Mad Cap
  Mushrooms; Mirror of Knowledge (unbounded, ground); Offering to the Gods on NEW ally_offering, OFFERING_MIN_MEN 30;
  Seismic Snare x2; Black Gem). 12 CLOSED (7 stealth, 5 mutual exclusivity = stances). gen_vortex_tables reads a
  self-centred BOMBARDMENT (explosion radius + radius_spread). The progress page shows 0 open. MOCK GOTCHA: an ally's
  dist field is both its gap to the caster AND to its own target (a charging ally must sit near 20 m). A blanket
  count swap (1008 -> 1041) hit a unit id in C6: exclude ids when rebasing.
- ROUND 184 (2026-11-20, review rows 10-19; 'Up to #19 ruled'): Flock of Doom x3, Sword of Daith, Zefet-nebtar on
  enemy_area_drain (it NEVER checked the enemy standing still: its gate is the caster's, for animated casts; a doc
  thread reply had said otherwise); Ring of Corin, Warpstorm Scroll (target_class flying) on enemy_single_drain; Soul
  Stealer x2 on NEW enemy_area_drain_hurt (DRAIN_HURT_PCT 75); Raging Tornado on NEW enemy_ground_melee_cluster
  (cluster_pick over enemies in melee, eg_mode 'melee'). A GROUND-ONLY key (target_ground, no target_enemies) MUST join
  enemy_ground_keys or the cast goes out in unit form (the harness caught it). New stand-still-family rows with no
  cast animation need the round-168 NOTE in the workbook (make_xlsx_v52.moving_keys). OPEN: Warpstorm's x0.55 slow
  rides no melee/charge arm (rule 10), recorded as ruled in audit R4 and put to the user.
- ROUND 183 (2026-11-20, review rows 1-9; 'You may start implementing #1-9 for now'): the 2026-10-09 'own-troop damage'
  rule was WRONG for all 19 rows (every damage phase targets enemies only). 9 NEW entries, existing families: Defiling
  Deluge, Murderous Exhortations, Rod of Corruption, Wail of Malice on enemy_melee_near (aura_real 35; start unarmed);
  Plaguereaper, Reaper of Souls on melee_health75; Shard Blade, Web of Shadows, Warp-Quake on melee_unwavering. The
  Numbers sheet's row 16 / carrier table had stayed at 1,003 (stale): v66 re-derives them. New entries need the
  regenerated key tables (round171_regen_tables.main) and hold_s rows for num_uses > 1. Next battle from byte
  822,999,135.
- ROUND 182 (2026-11-20, the finishers): the Executioner on NEW enemy_finisher (shot kind 'finisher': the single
  entity with the lowest health %, value on a tie, clear of ours, caster standing; 90% bound 225 m); the Emperor's
  Executioner: shot kind 'execute' ranks the HIGHEST health % below the line (user); Skjalandir's Fall on NEW
  melee_or_self_shooting (its phase imbue_contact = Blinded! on every hit; +90 accuracy). melee_or_shooting_into_melee
  is empty (code kept). gen_shot_tables.FAMILIES gained enemy_finisher (61 keys); the blob tables 68. No battle read
  since round 175. Next battle from byte 822,999,135.
- ROUND 181 (2026-11-20; 'Row 98, Land Mine: A / Fix the range mismatches / 28 Surprise Squig! implement blob with
  clearance'): NEW melee_clear_block (Land Mine: melee_clear + FOURTH.LAND_MINE_MIN_MEN 60 soldiers in its 25 m
  blast; FOURTH.blast_cover caps each unit at its strength), NEW enemy_summon_blob (Surprise Squig!: shot kind
  'summon', the standing block worth the most in the 21 m explosion, none of ours within 31 m; GENERATED
  FOURTH.SUMMON_BLAST_TEXT, tools\gen_summon_blast.py: spawned_unit -> its abilities -> bombardment; no density line).
  Range fixes: Curse of Khsar 100, Ravaging Swarm x2 100, Lord of Undeath split (lord_of_undeath_4 = the 200 m key).
  tools\scan_range_real.py checks EVERY key and is a build gate (0 mismatches). gen_vortex_tables.SELF_FAMILIES
  gained melee_clear_block. Curse of Khsar's game rule: refused above 50% caster health. Next battle from byte
  822,999,135. Still not built: the last review's row 23 + finishers.
- ROUND 180 (2026-11-18, score-3 review rows 87-114 and 128; 'Row 128 set A / Rows 57-86 do not touch / Rows 87-90
  implement without melee / Row 91-96 implement as in the doc / Row 98 improve / Rows 99-114 implement / 107 ... I like
  the option'). The 4 ground roots on enemy_fast_near_ally (the key forces the ground form) and on their REAL 100 m
  (they carried their AREA as range_real). NEW health_aura_ally_rule (ah_pick_where with FOURTH.ab_atarget_ok:
  Blood Chalice C, Breath of Darkness U, Mantra T), self_heal_clear (Bugman's, BUGMAN_CLEAR_M 38), self_hurt_attacked
  (Charoi, Skar's, HURT_ATTACKED_PCT 75), charge_or_tired (Foe-Seeker; legacy badge zz_auto_badge_fs). Rock Bottom
  > ROCK_BOTTOM_PCT 50. Eat da Runts!: hurt caster, cheapest healthy ally, no self arm. GENERATED lizard / tiger sets
  (tools\gen_rule_sets.py; ATARGET codes Z / T in gen_usage_keys.TARGET); CARD_ALLY_FAMILY gained wavering_ally_range
  and health_aura_ally_rule. gen_ww_tables.Q80: the 80% reach for 5 keys. CLOSED: Heaven's Gate, Snowflake Pendant,
  Stave of Avelorn. WAITING: row 98 Land Mine (its blast is 25 m: 'half a packed block' = 415 soldiers; options A 60
  soldiers in the blast (recommended), B two enemy units touched, C keep); row 28 Surprise Squig (a new proposal).
  NOT TOUCHED (range scan, tools\scan_range_real.py): Curse of Khsar 35 vs 100 m (row in 57-86), Dispatch the Swarm
  x2 30 vs 100 m, Lord of Undeath 200 vs 50 m. Every row of the score-3 review now has a decision: the user's
  enemy-charge test proposal was given (Markus Wulfhart's Hunter's Snare, skill wh2_dlc13_skill_emp_wulfhart_personal_5).
  GOTCHAS: the builder's content gates run AFTER the RPFM pack step (a scratch offline gate runner saved rounds);
  the mock grants ammo_left only with ammo_start AND ammo_seq; the blob coverage samples 19 points (it overcounts
  small units in a big blast). Next battle from byte 822,999,135.
- ROUND 179 (2026-11-18, score-3 review rows 115-134; 'Items 115-134 approved'): NEW ally_charge_or_melee
  (Inspired Assault x3), ally_melee_wavering_first (Inspired Defence x3, Da Boss), ally_value_melee (Orcs are da
  Best!), ally_in_melee (Hellish Vigour), health_aura_ally_deep (Berry Wine, FOURTH.HEAL_DEEP_PCT 55),
  heal_ground_best (Star of Avelorn: ally_range_real 200 + aura 15 -> 140 m reach, 10 m spot); ranked ally modes
  charge_contact_melee, melee_wavering_first, value_melee, expendable_hp, cheap_healthy. Favour of the Fay on
  melee_self_or_ally. wavering_self_or_ally lost its hidden ally-in-melee condition. Grut's Sickle (ally_winds):
  winds low only, expendable first, else cheapest above FOURTH.GRUT_HEALTHY_PCT 75. The 12 moved entries keep
  start_armed (33 plain lines). BUG FOUND: the shared heal re-check tests the ally against ah_range_m (the AREA);
  ah_mode 'spot' re-checks against ab_range_m, 'deep' against 55%. Mock: the ally-to-ally gap is the OTHER unit's
  dist_by_target[uid] (heal_ground_best's spot count). WAITING: row 128 Cold-Blooded's Lizardmen set (A: key prefix
  lzd, 133 units, recommended; B: Lizardmen voice culture, 107). Row 92 (Heaven's Gate) says CLOSE IT in the doc,
  not done (outside 115-134). Rows 57-114 wait. Next battle from byte 822,999,135.
- ROUND 178 (2026-11-18, score-3 review rows 23-55; 'Approve rows 23-55. Row 56 stays the same.'): NEW
  enemy_most_models (Chain Lightning x2, The Soulstealer: most models counted up to the AREA cap, FOURTH.MODELS_FLOOR
  16, standing still), enemy_fast_or_melee (Glory Seeker x2, commander class on both arms), enemy_fast_fire_melee
  (Prey of Anath Raema, Net Dem Up: FOURTH.eg_fire_first). The 6 plain roots on enemy_fast_near_ally (no melee arm).
  Spellcaster list for Void Pendulum, Word of Change, Dweomer Leach Orb, Slann Gold. Eye of Khorne value-first. Trophy
  Heads split (trophy_heads_daemon_wings). Bug fixed: a failed fast arm left eg_mode 'fast' (fallback cancelled).
  LESSON, AGAIN (round 171's): the first pass built the FIRST proposals of rows 23-24, 29, 36-45 although the RULED
  texts were committed in the doc; caught before the commit (first pass installed as bb0b9fe7..., never committed;
  a second RED control H177_RED2=1 on docs\backups\round178\first178_*.lua). Build from the CURRENT row text of the
  doc on disk, every row, not from memory of the proposal. Surprise Squig (row 28) NOT built: it SUMMONS Explosive
  Squigs, a new proposal is needed. Siegebreaker kept (100 + 100 AP to units). Rows 57-114 wait; rows 115-134 are
  APPROVED (round 179; read their RULED texts and the doc's later edits: #92 closed, #126/#132 keep, #129, #133).
  Next battle from byte 822,999,135.
- ROUND 177 (2026-11-18, score-3 review rows 1-22; row 3 kept by the user): NEW slow_army, melee_vs_large,
  ally_squig_melee (GENERATED FOURTH.SQUIG_TEXT, tools\gen_squig_keys.py), enemy_melee_near, aura_charge_or_melee,
  melee_health25, guard_aura, self_or_ally_fire_melee (ab_rank 'value_under_fire'), melee_healthy. The rest of
  docs\WH3_score3_review_2026-11-18.md: see round 178. REMIND THE USER when the whole list is finished: 'how well our trigger
  detects an enemy charge; propose a test with an ability available in skirmish vs AI'.
- ROUND 176 (2026-11-18): Master of Mists starts armed (start_armed; 9 plain start_armed lines). Next battle from
  byte 822,669,876.
- ROUND 175 (2026-11-18, the Aislinn battle, archive\logs\battle_20261118_r174_aislinn.txt, bytes 783,197,257-
  822,669,876): Master of Mists was armed 3.75 s after the enemy entered range, so it never fired. User: 'it also has
  plain damage boost' -> 'A: before range, else shooting': FOURTH.mist_shooting (ah_mode 'mist_shoot', MIST_AREA_M 24).
  A verifier cloned from the previous one must re-point BOTH its module alias reads (RUN and DST) at the new version
  (v58's first run read v57). Next battle from byte 822,669,876.
- ROUND 174 (2026-11-18, review rows 24-50; read F 'use the caster list'): GENERATED FOURTH.SPELLCASTER_TEXT
  (tools\gen_spellcaster_keys.py, 865 land units; class 'spellcaster' in eg_class_ok). NEW enemy_large_value_shot,
  enemy_spellcaster, enemy_ground_spellcasters / enemy_ground_shooters (FOURTH.cluster_pick, CLUSTER_M 24 = 70% of 35),
  enemy_missile_value, enemy_commander_wavering (shot kind 'waver'); ally scores FOURTH.AB_RANKED / FOURTH.ab_rank
  (charge_first, value_melee_wavering, value_shooting, value_melee_risk, routing; ab_filter 'not_missile'); the ally
  picker keeps routing allies only for 'routing'. ally_overseer/beast/broken/missile now empty (code kept). GOTCHAS:
  the reading copy has no FOURTH.shot_reason (answer true there); the mock's ally gap is the ALLY's dist field; a
  GENERATED block must be cut at '\nFOURTH.load_X()\n' (line start), never 'FOURTH.load_X()' (round174 blob bug).
  Row 23 + section 7 (finishers) RULED, not built: waiting for the user's go-ahead.
- ROUND 173 (2026-11-18): Null Stone and Rock Eye CLOSED ('Close Null stone, Rock Eye.'). h127's hold tests now use
  Doom Glaive. Read F (spellcaster class) RULED in a side session: 'Okay, then let's use the caster list'
  (tools\list_casters.py: junction OR a skill tree granting a lore/lore spell; never agent_subtypes.is_caster).
  NEXT: review rows 24-50 (user: 'You may implement items 24 to 50').
- ROUND 172 (2026-11-18): round 171 had built the FIRST proposals of review rows 1, 3, 5; the doc already held the
  user's RULED lines (user: 'I feel like you ignored the current version'). LESSON: before building from a proposal
  doc, re-read it FROM DISK (git diff vs its last commit) and quote every row's RULED text in the round doc.
  FOURTH.army_moments(): living / charging / fresh / melee counts; need = min(ARMY_CHARGE_MIN, living) (routing units
  are living but never count). Horn = army_charge; Waaagh! wh_main = NEW army_charge_or_melee; Ursun's Roar charge
  key = ONE unit (caster or within 24 m) charging, fresh contact or WAVERING (AURA_CHARGE_ALLIES removed). Still
  ruled in the doc but not built: row 23 + section 7 (finishers, lowest health % first). Rows 6-7 'and closing' is
  not checked (fast_enemy_near reads fast + moving only); flagged, no ruling.
- ROUND 171 (2026-11-17, the score 1-2 review rows 1-15 and 21): NEW families army_charge (Horn of the Wild Hunt,
  Waaagh! wh_main key = its own entry waaagh_army), aura_charge (Ursun's Roar charge key = own entry ursuns_roar_charge),
  self_or_ally_charge (Red Fury; ally picker family 'charging'), slow_aura (Rock of Inevitability, Wissenland Runefang),
  winds_low (Black Staff, Forbidden Rod: WINDS pool < 30, reserve >= 20, caster > 50%), contact_melee (Necrotic
  Phylactery; GENERATED FOURTH.CONTACT_TEXT, tools\gen_contact_keys.py, 503 land units; gamedata melee_weapons.tsv
  extracted). FRESH CONTACT = entered melee <= 2 s ago (FOURTH.track_melee, once per poll, every unit of ours). Wand of
  Jet -> when_ready. CLOSED by the user (workbook SKIPPED): Earthing Rod, Hagtree Fetish, Master of the Black Arts, Maw
  Shard, Power Familiar, Watched by the Watcher, Sceptre of Stability, Locus of Abjuration, Focus Instincts. Moved
  entries keep their default via start_armed (8). Answered: Rock Eye is ACTIVE by the data (passive=false); Null Stone
  is NOT mp-only (ancillaries.tsv extracted: mp_exclusive=false) -> rows 16, 18 wait. GOTCHA: the reading copy's ally
  picker returns false, the live one nil: test 'if r then'. GOTCHA: make_progress_page's 'seen in battle' reads the
  harness logs too (overstated). Rows 23-50 of docs\WH3_low_score_review_2026-11-17.md: next session.
- ROUND 170 (2026-11-17): Potion of Foolhardiness on charge_or_wavering (user test: it fired only at contact on
  melee_unwavering; ruling 'Charge or wavering'). NEW entry field start_armed = true (read by the default rule) keeps
  it armed by default; only this entry has it. WAITING FOR RULINGS: the other 49 rows of
  docs\WH3_low_score_review_2026-11-17.md (one 5/5 trigger per ability; new reads proposed: fresh contact, army charge,
  GENERATED spellcaster class from special_ability_groups_to_units_junctions, GENERATED Primal Instincts class; Iron-
  Handed Captain's picker skips routing units = a defect). Next battle from byte 783,197,257.
- ROUND 168 (2026-11-17; user: "Option A, animation decides all. And please implement the visibility."). STAND STILL:
  only an animated cast waits for its caster (63 entries may now fire on the move: Fireball, Gaze of Malice, Wrath of
  Manann, the Banishments ...); target-still rules unchanged. VISIBILITY: FOURTH.enemy_not_hidden (only an exact false
  from is_visible_to_alliance blocks; unreadable passes) first in eg_class_ok (every picker + the pre-cast re-check)
  and in the non-commander picker. ROUND 169 (user: 'Yes, those too'): the air drop, the Farsight / Mist read and the
  contact set skip hidden enemies too: EVERY decision ignores an enemy we cannot see (the map probe only logs). Next battle from byte 781,091,240: watch a
  non-animated blast cast on the move and a wave's heading after a moving wind-up.
- ROUND 167 (2026-11-17, after the Dark Elves battle, archive\logs\battle_20261117_r166_darkelves.txt, bytes
  760,068,621-781,091,240: 87 casts, 0 errors). User: NO FINAL PERIOD on a one-sentence tooltip (the card and the ALL
  text; the build refuses one). SAFER DEFAULTS: GENERATED FOURTH.RISKY_TEXT (tools\gen_risky_keys.py: the game's
  'rampage' phase attribute, positive, on the caster or its allies; phases with damage_amount on the caster; 20 keys):
  a risky entry never starts armed (15 entries, e.g. Fury of Khaine, Witchbrew, Rock Bottom); a click still arms it.
  WAITING FOR A RULING: Gaze of Malice did NOT stop its moving caster (user, manual cast). The game's
  unit_special_abilities.wind_up_stance (the cast animation) matches all 4 field cases (stoppers: cast_forward_short;
  non-stoppers: empty). 63 standstill-gated entries have no animation. Options A (stance decides everywhere), B
  (recommended: as A, waves and cones keep the rule: their path follows the caster-to-target heading), C (keep).
  Also waiting: visibility for the older enemy pickers (explained to the user 2026-11-17). Next battle from byte
  781,091,240.
- ROUND 166 (2026-11-17, the short cards; rulings after the Daemons battle). FIELD-CONFIRMED by the user: the M/A badge
  hover card WORKS (SetTooltipText on the badge). The user then ruled: cards short and thematic ('Deadly Onslaught might
  say fires when charging'): FOURTH.CARD_TIP is one 'Fires ...' sentence per family, NO distances, no name, no 'on A:'
  (longest 115 chars; the build refuses distance tokens back); FOURTH.CARD_TIP_NOAURA for the 4 aura families without
  an aura. The static card note is gone: the card xml is RETIRED (pack = 4 files). ALL tooltip = 'Arm or disarm every
  automatic ability of the selected unit(s).' Wanderers (kinds 2/3): the caster never blocks its own cast. User ruling
  'Vortex with affects_allies=false should have no friendly-fire check': already true (Heaven's Gate, Abyssal Swarm,
  Crackleblaze, Arcane Vassal); NEW gate tools\ff_gate.py (95 keys). Daemons battle archived as
  archive\logs\battle_20261117_r165_daemons.txt (bytes 735,692,926-760,068,621): 86 casts accepted, 0 errors, ground
  casts OK (Searing Doom, Portalglyph, Karanak's Howl). Next battle from byte 760,068,621: check the vanilla card (no
  last line), the short cards, Blue Fire / Siegebreaker ground casts. The rest of the overnight audit waits for rulings.
  Lesson (again): heredoc Python turned '\n' and '\t' into real characters twice this round: write with Write/Edit.
- ROUND 165 (2026-11-17, the night audit; user: "check during the night each ability one by one"). The round-93
  TRIGGER_TIP sentence was NEVER shown (ability.tip has no reader). NEW FOURTH.CARD_TIP (95 corrected sentences, tokens
  filled per entry by FOURTH.compose_card: 70% bounds, blast / wave clearances, charge window) + clauses = the hover
  tooltip of each M/A badge (pcall'd SetTooltipText, create_badge STEP 5b; NOT field-checked: ask the user to hover a
  badge). GENERATED FOURTH.USAGE_TEXT (tools\gen_usage_keys.py, the game's caster usage flags with a live read; 60 keys,
  10 newly honoured) gates try_pair; GENERATED FOURTH.ATARGET_TEXT gates the ally picker (ab_filter_ok; ally-picker
  families only). FIXED: the 7 ground-only WW keys now cast in the ground form (ww_take's eg_ground had no reader); the
  two sweeps got ENEMY_CAST_R6/R3 (they fell back to 52 m). Lesson: a harness that counts unit + ground casts together
  cannot prove a ground cast; count the forms apart. WAITING FOR RULINGS (docs\WH3_overnight_audit_2026-11-17.md):
  Commanding Presence / Fury of Ulric hide an 'ally in melee' condition that contradicts the user's ruling; the score-1-3
  trigger groups; visibility for the old enemy pickers; 'Caster doesn't count' for wanderers.
- ROUND 164 (2026-11-16): THE FRIENDLY-FIRE BREATHS (the 2026-10-09 'breath / cone damage' RULE reopened; VORTEX
  breaths, the 77 projectile breaths already ride enemy_blob). 18 target-launched on enemy_wave; NEW enemy_wave_charge
  (Tidecall, Wind Blast: their slows, rule 10: a fast enemy closing, the path clear); NEW enemy_cone (5 breaths from
  the caster's front: the zone caster -> target, offset + path long, clear of our OTHER units); NEW enemy_sweep
  (Disembowelling Sweep, Flesh-eating Scarabs: caster in melee, none of ours within the sweep's reach + 10 m, the
  closest enemy in melee); Da Boss' Loons on enemy_wander kind 6 (the ring around the caster). User: 'Caster doesn't
  count': a caster's own wave never blocks it (round 162's waves too). The game's engaged_in_melee rule joins the WW
  caster gate (GENERATED FOURTH.WW_NOMELEE_TEXT: Blue Fire x2). WW kinds now: 1 wave, 2/3 wanderer, 4 strike, 5 cone,
  6 wanderer from the caster, 7 sweep.
- ROUND 163 (2026-11-16): THE PLACED AREAS (the 2026-10-09 'placed / static area damage' RULE reopened) and the
  EXPENDABLE UNITS. 22 on enemy_wander (7 instant blasts 'Like Dwellers Below', 14 lingering areas 'Same as the
  blasts', Chain Lightning RoR); NEW ally_blast (Arcane Vassal: our unit with the most enemy value around it, cast on
  it); NEW enemy_strike (Siegebreaker: the most valuable STANDING single enemy, ground cast, none of ours within 11 m;
  as a unit target the game only accepts climbing / manning / platform units); Befuddlement on enemy_fast_near_ally
  (user: 'charge only', 'Any fast enemy'); Winged Staff on enemy_area_drain; the Wrath & Ruin runes closed (shared
  recharge 60/90 s locks the Runelord's other runes). gen_ww_tables now reads BOMBARDMENTS (projectile_bombardments
  extracted): Magma Storm safety 75 m with its 20 m vortex scoring; Hell Hammer's corridor radius 14.1 m. EXPENDABLE
  (user: 'Game's set + cheap undead'): blob_map leaves out of m.ours (the ONE list every friendly-fire check reads)
  our units with the game's 'expendable' attribute (GENERATED FOURTH.EXPENDABLE_TEXT, tools\gen_expendable_keys.py,
  48) and those below TRASH_VPS per soldier. Lesson: name EVERY stat an ability changes in the proposal (the audit
  caught Smednir's x0.4 speed; ruled 'Keep the blast rule'). Workbook prose slip: v46 says 172 not implemented, the
  right figure is 174 (its cell); recorded in v47.
- ROUND 162 (2026-11-16): THE WANDERING WINDS (the 2026-10-09 'vortex / wandering wind' family RULE reopened).
  NEW enemy_wave (12 straight waves) and enemy_wander (15 wanderers, Ruination of Cities, Dwellers Below x2, Heaven's
  Gate, Abyssal Swarm): the caster AND THE TARGET standing still (user: 3-5 s casts, a moving target leaves the
  computed path); waves pick the most enemy value on the path (offset 24 m + target half extent before it, speed x
  duration long, caster-to-target heading) with none of ours within radius + 10 m at its start widening to radius +
  95% drift + 10 m at its end; wanderers ride the blob rule with none of ours within radius + 95% reach + 10 m (none
  when the vortex cannot hit allies). GENERATED FOURTH.WW_TEXT (tools\gen_ww_tables.py: 4,000 simulated paths per
  reading of change_max_angle, the wider reading, fixed seeds; user: 'Simulated 95%', 'low randomness, lower
  buffer'). Closed: Gehenna's Golden Globe, Wall of Wind & Fire (heading unknown). The round-118 dead-symbol token
  'dwell' became ' dwell' (the key the_dwellers_below). Unchecked: the wave heading, the turn field's meaning.
- ROUND 161 (2026-11-16, tuning, from the Bretonnia battle at log bytes 704,611,726-735,692,926, archived as
  archive\logs\battle_20261116_r160_bretonnia.txt): ally_melee_buff (14) joins FOURTH.DEFAULT_ON_TRIGGERS ("Whole
  family"); the builder's round-151 gate pins the exact default-armed family set (now 29). Field: round 160's one-poll
  rule CONFIRMED (10 instant pairs, every first cast's retry refused 'on cooldown'). The wandering winds were done in
  round 162, the placed areas in 163, the breaths in 164; still rule-shut: 19 own-troop auras, 22 collection-time skips, 7
  flanking, 5 mutual exclusivity, 2 bombardment; plus the user's own 9 'skipped (revisit)'. Next battle from byte
  735,692,926.
- ROUND 160 (2026-11-16, tuning, from the Beastmen battle at log bytes 689,926,854-704,611,726, archived as
  archive\logs\battle_20261116_r159.txt): when_ready skips a ROUTING unit (Jagged Dagger was 'accepted' 6 times in
  11 s while its shaman fled); the per-unit serialisation window is ONE poll (FOURTH.SERIAL_INSTANT_HOLD_SECONDS) for
  an entry with no wind-up in cast_gate.wind_up_s (= exactly the game's 258 keys with wind_up_time > 0; the build
  regenerates and compares), and wind-up + 2 s (min 2.5 s) otherwise (user: instant abilities need no 2.5 s wait).
  Watch next battle: an instant cast's own retry 2 s later must still be refused 'on cooldown' (ACCEPTED = it was
  replaced). Bloodbeast (melee_clear) field-confirmed: fired at 25.1 m / 25.9 m clearance. Next battle from byte
  704,611,726. Mock gotcha: Blood Lust's badge is the legacy zz_auto_badge_bl.
- ROUND 159 (2026-11-15): GROUP E, the last open abilities (open is now 0). 13 safe self-centred blasts on
  melee_unwavering ("Like Bloodstorm"); 5 friendly-fire blasts on NEW melee_clear (in melee, none of our OTHER units
  within blast + 10 m of the caster); the Phoenix dives on NEW fly_dive (flying exactly true, an enemy within 70% of
  the blast, none of ours within blast + 10 m; corrected from 'in melee and flying' before the build: a flier that
  lands is not flying); Necrotic Explosion on NEW last_stand_clear; the Frost Dragon Scale on NEW enemy_blob_vortex
  (evaluate_enemy_blob with the vortex radius); look-alikes: Maneater Smoke Bomb charge_or_melee, Verminous Valour
  wavering_self, Heaven's Flash enemy_ground_melee, Slime Smoothie health_aura_ground, Slann Gold and Deathmaster's
  Sigil enemy_commander_value (the Sigil: NEW class commander_ground, target kept blast + 10 m clear). The 4 new
  families start unarmed (M). Blast radii: GENERATED FOURTH.VORTEX_TEXT (tools\gen_vortex_tables.py) from the NEW
  gamedata\wh3\battle_vortexs.tsv. Closed by the user ("Close 5, Necrotic last"): Mist Form, Shadowstrider, Deep
  Tunneling, Sword of Teclis, the Unidentified Hydra Head. Mock: a ground-form cast lands in W.ground_fires.
- ROUND 158 (2026-11-15): the last group B: 7 AREA DRAINS on NEW enemy_area_drain (max_damaged_entities from the
  GENERATED FOURTH.AREA_TEXT: the target needs at least that many soldiers left; most value per soldier; standing
  still; no margin), Ethrac's Brazier + Storm of the Night on enemy_melee_or_fast (Storm: NEW class "flying",
  is_currently_flying() exactly true), Preyton Horns on enemy_melee, The Amber Trance on enemy_wavering, Dweomer Leach
  Orb on NEW enemy_commander_value (the spellcaster proxy). The trigger audit now counts enemy_melee_or_fast as
  rule 10's melee-or-charge family and lists Preyton Horns as ruled (R6).
- ROUND 157 (2026-11-15): the 10 single-target DRAINS (max_damaged_entities = 1) on NEW enemy_single_drain ("Most
  valuable single" + "Standing still"; no 10 m margin: a direct effect cannot hit our units) and the Emperor's
  Executioner on NEW enemy_execute ("At the execute line": GENERATED FOURTH.EXEC_TEXT from execute_ratio, 20% base
  Lord/Hero only, 33% upgrade single entities). shot_pick / shot_cand_ok / shot_take take a trailing nosafe flag.
  The SHOT table now covers 23 keys (gen_shot_tables.FAMILIES).
- ROUND 156 (2026-11-15): THE MAGIC MISSILES, 11 entries on 5 NEW families (rulings: AP shots "Large first, then
  armour", snipers "Most valuable single", throws "Split by effect", Bolt Storm "Most valuable infantry"):
  enemy_large_shot / enemy_single_shot / enemy_infantry_shot use the map's NEW m.all list (every visible enemy, s.value =
  live strategic_value) and FOURTH.SHOT_SAFE_M = 10 (none of ours within 10 m of the target); enemy_melee_or_fast and
  enemy_melee_or_shooting chain the existing pickers. GENERATED FOURTH.SHOT_TEXT (tools\gen_shot_tables.py:
  engaged_in_melee usage, prefer-large, min_range). New target class "single". NOTE: the generated large set includes
  cavalry and chariots, so 'most valuable large' can pick cavalry over a monster (user ruling 2026-11-15: "Keep as is").
  tools\fact_sheet_open.py prints any ability's game facts; tools\list_open_abilities.py lists the open ones.
- ROUNDS 151-152 (2026-11-14/15): the 53 prefer_central_targets blob attacks hit a safe, NON-FLYING large enemy in
  range first; the whole-map hold is GONE (round 152: it silenced every breath all battle); the game's usage rules
  (12 grounded, 26 engaged_in_melee) are honoured; all 53 central attacks (breaths included) prefer a side-on target
  within 20% of the best value. ROUND 153: TRASH infantry (live value below 2 per soldier: Zombies, Skavenslaves, the
  Tithe, Skeletons, Clanrats) is skipped unless the blast covers 3 PACKED BLOCKS (3 x area / 2.368; the density line
  is HALF a packed block - do not mix the two again). 28 trigger families (434 entries, 'tired' added in round 152) START ARMED; harness worlds that arm by
  clicking need the TEST-ONLY global ZZ_AUTO_TEST_NO_DEFAULTS (load_world sets it unless W.defaults_on). The ALL
  badge (zz_auto_badge_all; round 151 put it off-screen at (-1007,-105); round 152 at (-880, 8) landed as predicted;
  round 153: (-855, -28), the middle of the cloth, shown for ANY selection owning our abilities, with a pcall'd
  SetTooltipText tooltip (confirmed in game, and the click on 7 units); ROUND 154: the GAME'S round_small_button_toggle
  (38 x 38, ui3.pack) with icon_abilities.png (ui2.pack) in image 0, no letters, PRESSED while every owned ability is
  armed (only a wrong state family is corrected: hover looks stay); the user loves the look (2026-11-15). ROUND 155:
  at (-923, 0), TUNED BY THE USER in battle (field-confirmed). He re-tunes it from the Lua Console (Modding Development Tools: Lua Console, workshop 2791799449, van_devtools.pack;
  Shift+F3): zz_all_nudge(dx, dy) / zz_all_set(x, y) / zz_all_where() log 'ALL POS x,y'; bake the last one) arms/disarms all of the selected units'
  abilities; the mock counts it apart (W.all_badge_created). Main chunk is near Lua's 200-local limit (about 190):
  add new state as FOURTH fields or ability-entry fields, never new file-level locals.
- WINDS OF MAGIC (round 150): the 21 pure winds abilities fire when ready (when_ready). The pool is NOT full at battle
  start (user screenshot: Power 12/100, reserve 68, 'Recharge blocked'). The map log now has a WINDS row every 2 s
  (army winds_of_magic_current / _reserve / _remaining_recharge_rate, first read in round 150: check the next battle).
- MEMORY READING: CLOSED by the user (2026-11-14, round 149, docs\WH3_round149_revert_probes.md); rounds 147-148
  reverted. Goal was live melee attack/defence: the game never STORES them (computed on demand), and nobody online
  reads them. Readable, kept as knowledge only (u = the address tostring prints for a battle.unit): current HP
  [[u+8]+0x280]+0x5CC, men [u+8]+0xA4, leadership [u+8]+0x3B78 (signed int), ammo left (all men) [u+8]+0x3D90, base
  stats [u+8]+0x37F0 MA / +0x3820 MD. Read-only tools stay in tools\memprobe\. Do not reopen unless the user asks.
  Claude can press keys in the game (P pauses, after a click on the window title bar) but its clicks are ignored.

- THE MAP PROBE (round 145, read-only; battle 1 read 2026-11-13, docs\WH3_map_probe_battle1.md): every 2 s the log
  gets MAP rows for both sides. Field facts: every read answers on BOTH sides (ordered_width included) except
  position_of_officer() (0%); is_visible_to_alliance(bm:get_player_alliance()) works (living enemies hidden in fog
  read 0; dead units read 0); strategic_value() is a live value near the unit's cost at full strength, falling with
  men and health, 0 when dead; bearing b faces (sin b, cos b) on X/Z (median 8.6 deg off the travel direction);
  is_infantry() AND unit_class() call Fell Bats, Devils, the Varghulf and the Zombie Dragon infantry: an infantry
  test needs the generated large set and not-flying too; dead units stay in both lists with men=0. The biggest
  blob was the enemy mobbing one of OUR units: any blob trigger needs the friendly check. Read a battle with
  tools\analyze_map_log.py <log> --from <offset>.
- THE BLOB TRIGGER (round 146; rounds 150-151 = field rulings; awaiting a battle from byte 689,926,854; the trash rule is still unseen): the
  target is the one whose blast destroys the most enemy VALUE (soldiers covered x share killed after armour vs hit
  points, generated tables BLOB_DMG / UNIT_DEF x live strategic_value per soldier); AP-heavy attacks (38) never target
  armour below 50; the caster must be standing (is_moving() false: an aimed cast STOPS a moving caster, field
  2026-11-14; the user limited the standstill rule to the blob attacks 'for now'). Before round 150:
  the best SAFE visible enemy infantry unit (inf class, not large, not flying, >= 10 men) whose blast covers at least
  half a packed block (round(0.5 pi R^2 / 2.368)); none of ours within blast + 10 m. Generated tables: blast radii
  (projectiles_explosions via tools\extract_db_table.py) and infantry spacing (tools\gen_blob_tables.py). A verifier
  or roster tool must NEVER take a round's keys from 'open in the newest workbook' after that workbook is written:
  read them from the mod source (round 146: the v37 verifier passed with an empty list once).
- Game data moved out of Temp on 2026-11-01 (round 124): `gamedata\wh3\` regenerated from the
  installed game, drift recorded in `gamedata\DRIFT_2026-11-01.md` (no mod constant moved).
  Earlier rounds' builders and harnesses still name Temp; they are history, not re-run.
  `gamedata\wh3_layouts\` holds vanilla UI files pulled on demand by `tools\extract_ui_layouts.py` (list <regex> /
  get <pack> <path>; one RPFM session per call, the server exits after each); round 154 pulled the round button
  templates, hud_battle and icons. Re-extract before the next layout patch.
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
