# Overnight review of the mod (night of 2026-11-21 / 22)

Scope: the installed build of round 197 (pack md5 `febf51077902ccef857d0ac42cc872d7`), source
`mod_source\script\battle\mod\zz_test_deadly_onslaught.lua` (27,686 lines, 1,611,530 bytes), the MCT page and the badge layout.
Nothing was changed, built or committed. Line numbers refer to the source file.

How it was done: seven independent reviewers each read one slice of the file (six code slices, one for the ability data
against the game tables). I ran the standing gates and my own static checks, then re-read the code behind every finding
listed in sections 1 and 2 before keeping it. Findings I could not confirm in the code are marked UNPROVEN.

## 0. What is clean

- Full harness 196: 8,104 checks, 0 failures.
- The same full harness on a Lua 5.1 engine (LuaJIT): 8,104 checks, 0 failures. A recording shim found 0 calls that Lua 5.1
  would reject. The source compiles on plain Lua 5.1.
- Installed pack: all 5 files byte-identical to source, no probe path, no user path inside.
- Gates: army-bar gate 0 of 1,038 keys, range scan 0 mismatches, friendly-fire gate 0 violations, wheel audit OK on
  workbook v76, database verify OK.
- No misspelled global anywhere (read from the compiled bytecode: the script reads only the engine's globals and its own).
  No FOURTH name is used without being defined.
- Game build 26403568 equals the baseline: no patch since round 132's data.
- The last four battle sessions in the live log (from byte 946,588,829): no script error, no POLL ERROR line.
- Data: 0 duplicate keys, 0 duplicate markers, 0 triggers without an evaluator, 0 range fields off the game's tables,
  0 range constants off the range rule, 0 melee-only stats on a shooting trigger.

## 1. Defects that change what fires (ranked)

| # | What | Where | What you see in battle | Confidence |
|---|---|---|---|---|
| 1 | **The "one ability at a time" window is not re-armed when the same ability fires twice in a row.** The window is only set when the ability differs from the last one that set it, and that memory is never cleared when the window ends. | 23288-23290, 23362-23373 | A unit casts ability X (with a wind-up), later casts X again, and during that second wind-up another ability of the same unit is ordered and replaces it. X goes on cooldown with no effect. | High (code read) |
| 2 | **The air-drop fast pass reuses another ability's leftovers.** The normal poll wipes about 40 "chosen target" notes before each ability. The separate 0.2 s air-drop timer wipes only its own 6, so it inherits whatever the last ability of the last unit chose. Found independently by three reviewers. | 27386-27403, 24479-24559, 23313-23321 | A Gyrocopter or Sky-junk crosses an enemy and does not drop (the leftover check fails and locks the bomb for 2 s), or the drop is ordered with another unit's ally or enemy as its target. | High on the code path, medium on how often |
| 3 | **Get Tha Gitz! has 3 uses and no charge hold.** Every other multi-use ability has one. | entry 4537, no row in the hold table at 5228 | All three summons go out within about 15 s of the first melee in range. After that the mod keeps sending empty casts that the engine accepts, which also take the hero's cast slot from his other abilities. | High on the data |
| 4 | **Heaven's Flash is a ground-only ability cast in unit form.** Its key is missing from the ground-cast list (the round-184 rule). It is the only one of 86 keys on its trigger with this slip. | entry 2358, list at 7621-7760 | The single use is most likely accepted and lands nowhere. UNPROVEN in a battle. | High on the data |
| 5 | **Doom & Darkness (gunnery school) can never get a badge.** The game spells the key with a capital B. The badge code lowercases the button's key and compares it with the listed key, which keeps the capital. | key 1533, compare 25800-25816 | On the Amethyst Marienburg Land Ship the icon has no M/A letter, so it cannot be armed by its badge. | High (code read) |
| 6 | **Wrong key in the Lord/Hero list: the Necromancer (Undeath) on a Nightmare.** The list has `..._undeath_barded_nightmare`, the game's unit key is `..._undeath_nightmare` (the other generated lists have the right one). | 13591 | He is not seen as a Hero: Eye of Khorne and The Dreaded Thirteenth may target him, commander-only abilities never pick him. | High (game table read) |
| 7 | **Two slow / guard triggers still use the pre-round-192 "fast enemy" read.** `slow_aura` (The Rock of Inevitability, Wissenland Runefang, Seismic Snare x2) and `guard_aura` fire on any fast-type enemy that is merely moving inside the aura: walking, leaving or routing counts. Round 192 changed the shared read to running and closing, these two have their own copy. | 9167-9194, 21080-21098 | The slow is spent when cavalry walks past. Rule 10 says a slow never fires on an enemy passing by. Needs your ruling: apply the round-192 read here too (recommended). | High on the code |
| 8 | **Self arm on abilities the game does not let the caster target.** Favour of the Fay (target_self false, the caster is not affected) fires "on self" whenever the Enchantress is in melee and never reaches its ally arm while she fights. Shielding Swarm x2 the same. | entries 1070, 3643, 3650 | The buff is wasted or dropped. UNPROVEN: no battle log has one of these casts since round 179. | Medium |
| 9 | **Hellish Vigour Upgraded was left on a self trigger** when the base ability moved to "ally in melee" (round 179). Its only effect goes to allies. Nine more ally-targeted keys are still "cast on self for now" (Wild Abandon, Hand of Dust, Cash Cascade, Master of Alchemy x4, Master Rune of Oath and Steel, Spite of da Bad Moon): known debt in the tracker, never seen in a battle log. | 3269, 4008, 3793, 1031, 1171-1186, 1191, 1248 | Unknown until tested. | Medium |
| 10 | **The infantry test of the 30 bombardments trusts `is_infantry()` alone.** The map probe showed the engine calls Fell Bats, the Varghulf and the Zombie Dragon infantry. The blob family already adds "not large, not flying", this older test does not. | 14440-14456 | Comet of Casandora or Searing Doom placed on a single monster in melee. | Medium-high |
| 11 | **Bugman's XXXXXX clearance is 38 m, the game's rule is 55 m.** The 70% rule shortens a reach to stay inside a range. Here the number is a distance the enemy must stay OUT of, so 70% points the wrong way. You approved 38 in review row 106, so this is a correction to rule on. | 20782-20800 | With the nearest enemy 38 to 55 m away the mod tries every 2 s and the game refuses. | Medium |
| 12 | **One click changes every untouched unit of the same type in the same battle.** The remembered state per unit type is read live, so clicking one Swordsmen unit to M turns the other Swordsmen units (never clicked) to M at once. Consistent with "option A, per unit type", but it contradicts "state is per unit" within a battle. A question for you, not a slip. | 6447-6450, 25313-25325 | Described above. | High on the code |

Smaller, confirmed in the code, low impact: Eat da Runts and Grut's Sickle treat an ally whose value cannot be read as the
cheapest (10073, the read answered on every unit so far). Ally pickers count an unreadable distance as "in range" while enemy
pickers refuse it (10177, 19353). Enemy pickers never exclude a routing enemy (12597). Call of Tor has a stale hold row
(harmless). The comment above Bangers & Smash names the wrong trigger (1234).

## 2. Blocking a Steam Workshop release (ranked)

1. **No multiplayer or replay guard exists.** `is_multiplayer` appears nowhere in the file. Open point 18 records the
   decision, it is not built.
2. **Logging has no off switch, and several debug lines are very large.** Measured in the archived Dark Elves battle
   (62,084 lines, 21 MB): 18,900 lines are the per-second badge dump that writes one line for each of the 985 abilities
   while a unit with Deadly Onslaught is selected (26530), 5,889 are "readiness" lines written on every poll while a pair
   waits (23205). Also every 5 to 10 s a 20 KB line listing all 985 ON/OFF states (6469), the map probe every 2 s, 1,038
   lines at load, and evaluator "chosen ally / chosen enemy" lines 4 times a second. Each line is flushed to disk.
   You already ruled "logs removed before publishing": this is the list of what that covers.
3. **Work done 20 times a second in the UI timer.** A walk of up to 900 UI components on every 50 ms tick for the whole
   battle (27581), a 22-component search every second that only feeds the log (27562), and the icon scan runs three passes
   over all 985 abilities per ability button although a direct lookup table exists (25982). Not profiled in game.
4. **Lords, Heroes and large units from other mods are unknown to the mod.** The Lord/Hero test uses the baked list and
   reaches the engine's own class read only when the unit type is unreadable, which never happens (14173). With SFO or a
   lord pack loaded, a modded Lord counts as a normal unit.
5. **Only one army per side is read.** ASSUMPTION (CA's library is not in the project): the two calls the mod uses return
   your own army and the main enemy army. If so, in a battle with reinforcements the second enemy army is never targeted
   or counted, and allied armies are invisible to every friendly-fire check. One reinforcement battle would settle it.
6. **Debug and test switches are global names** any other mod can set or call: 10 console functions (`zz_badge_*`,
   `zz_all_*`) and 6 `ZZ_AUTO_TEST_*` switches read by live code.
7. Names still say `zz_test_deadly_onslaught` (log, timers, pack, badge files). The pack type is Movie.
8. Three hover cards contain a semicolon and clauses are joined with "; " (22863, 22865, 22961, 23127).

## 3. Robustness

- One raising ability check stops every later unit in that poll, every poll, with only a "POLL ERROR" line (24365-24568).
  The UI timer has no outer guard at all (27444), unlike the poll and the fast pass.
- The ALL click rewrites the settings file once per switch: 20 units with 5 abilities is 100 rewrites in one click (25547).
  The file is emptied before it is rewritten, and a failed write is not logged.
- A few engine reads have no guard where their neighbours have one (14966, 15164, 19345, 20881). No failure seen so far.
- The MCT page's click handler is not guarded although its header says everything is (the reset itself is).

## 4. Process and tooling

- The build's compile check and the harness run on Lua 5.5 (lupa's default). The game runs Lua 5.1. Tonight's run on a 5.1
  engine was clean, but the build would not catch a 5.1-only failure. Fix: one line in the builder (`lupa.lua51`).
- `tools\audit_wheel_status.py` reads workbook v20 (2026-10-20, 1,800 rows) unless given a path. On v76 it passes.
- `docs\WH3_restriction_audit_2026-11-17.md` (says 946 entries) and `docs\WH3_stand_still_audit_2026-11-21.tsv` are older
  than the source. A re-run changes both (I restored the committed copies).
- CLAUDE.md is stale in places: the source is 1.6 MB and 27,686 lines (it says 774 KB and 15,300), the live log is 0.96 GB
  (it says 5.4 GB), the build section says four shipped files.
- The main chunk has 190 file-level locals of Lua's 200.
- Dead code: `FOURTH.TRIGGER_TIP` (150 lines, no reader), 9 evaluators with no ability, `FOURTH.range_bound` (never called,
  the build checks the constants instead), two unused ally re-check helpers.
- Four files are untracked in git: `docs\WH3_spellcasters_all.md`, `docs\WH3_spellcasters_emp.md`, `tools\game_mouse.ps1`,
  `tools\list_casters.py`.

## 5. Recommended order

1. One fix round for section 1 rows 1 to 6: plain defects, no trigger design involved. Each gets a RED control first.
2. Your rulings on rows 7, 8, 9, 11 and 12.
3. A release round: the multiplayer guard, a log switch that is off by default, the debug dumps and probes out, the UI
   timer work cut down, the class fallback for modded units.
4. One reinforcement battle to settle section 2 item 5.

## 6. Status after the user's replies (2026-11-22)

- Section 1 rows 1, 2, 3, 6, 7, 8, 11: FIXED in round 198 (`docs\WH3_round198_review_fixes.md`).
- Row 4 (Heaven's Flash): WITHDRAWN. The user tested it and the log shows 4 casts in unit form that fired. A
  ground-only key ordered at an enemy unit is placed on that unit.
- Row 5 (Doom & Darkness, gunnery school): not touched. The user does not see the ability on the Amethyst Land Ship.
- Rows 9, 10, 12: waiting for rulings.
- Section 4, first point: the round-198 builder now also compiles the script on Lua 5.1.
- Rows 5, 9, 10, 12: FIXED in round 199 (`docs\WH3_round199_review_fixes2.md`).
