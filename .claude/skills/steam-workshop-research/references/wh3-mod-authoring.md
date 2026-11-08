# Authoring a Total War battle script

Depth for step 8 of the skill: building, verifying and shipping the engine-side script
and the pack that carries it. Companion to `references/modding-feasibility.md`, which
holds the table and API inventory — this file is the build loop and does not repeat the
signatures.

## The artifact

- **Path inside the pack:** `script/battle/mod/<name>.lua`. The engine's own mod loader
  auto-loads that folder in every battle, campaign battles included; no vanilla file is
  overwritten, and several script mods coexist because each owns its own file.
- **Name it uniquely and prefix for sort order** (`zz_…` sorts late). Keep the pack
  filename unique too — two packs with the same filename in `data/` collide.
- **Entry point in battle is the file body.** The shipped example mod on that path is
  plain top-level code. The loader *also* looks for a global function named exactly like
  the file, but that convention is only invoked on the campaign side; do not rely on it
  in battle.

## Load order: what is already guaranteed to exist

Worth knowing because it removes a whole class of doubt before writing a line:

- The shared header (`script/_lib/lib_header.lua`) builds `core`, then `bm` /
  `cm` (`battle_manager` / `campaign_manager`) for the current mode, and only **then**
  requires `lib_mod_loader`. So by the time a battle mod's body runs, `bm` exists and
  `bm:repeat_callback(...)` at file scope is safe.
- The loader resolves each mod file with `loadfile`, sets its environment to the global
  environment, and executes it inside `pcall`. Two consequences: top-level code runs at
  load time, and **a crashing script is not an unloaded script** — the loader catches the
  error and writes `Failed to execute loaded mod file [...]` to its own log. Check that
  log before assuming the file was never found.

## Logging: own the file

- **Primary: write your own log with `io.open(name, "a")`, guarded by `pcall`, flushed
  every line.** No engine switch involved, and the file lands in the game install folder
  next to the executable, where it can be read directly afterwards. Append rather than
  truncate, and write a session divider, so successive runs stay distinguishable in one
  file.
- **Also call `ModLog()` if it exists** (`if ModLog ~= nil then`) — the loader's own log,
  `lua_mod_log.txt`, proves the file was loaded and executed at all.
- `out()` is the engine's script log and is **gated off by default**: it needs an empty
  file at `script/enable_console_logging` (no extension), or the in-game Script Debug
  Activator / Mod Configuration Tool. Treat it as a bonus channel, never the carrier.
- Tag every line with the mod's file name. The engine log is enormous, and the user may be
  reading a different log to you.

## The poll skeleton

```
on load:
  bm:repeat_callback(poll, 250, "<unique_name>")
  bm:register_phase_change_callback("Deployed", build_watch_list)

poll (every N ms):
  if first tick: log a proof-of-life line              -- is the timer alive at all?
  every Nth tick: log a heartbeat line                -- phase + per-unit state
  if not bm:is_conflict_phase() then return end        -- skip deployment and victory
  build the watch list from bm:get_scriptunits_for_local_players_army() if empty
  for each script unit:
    if the unit is alive and owns the ability key
      and unit:can_perform_special_ability(KEY)        -- ask first: an illegal order
                                                       -- raises a script error
      and <the condition>
      and the local rate guard allows it
    then
      log the ATTEMPT first                          -- before the call, never after
      script_unit.uc:perform_special_ability(KEY, unit)  -- key first, unit second, BOTH
                                                         -- required - see the signature
                                                         -- section below
      script_unit.uc:release_control()                 -- hand the unit back
      log the result; while the ability is active the engine refuses repeats
```

Rate guard: track the last accepted fire tick per unit id and refuse to re-fire inside a
window taken from the ability's own `recharge_time` row. The legality check does not cover
the cooldown (measured, not assumed), so this guard is the only thing standing between the
poll and an order every cycle.

**The heartbeat is not optional.** Without it, a run that logs only its watch list is
ambiguous between three different failures, and the user has already spent a battle. One
compact line is enough: poll count, current phase name, and for each watched unit
`alive / running / in-melee / can-use`. Guard `bm:get_current_phase_name()` and any other
call not yet observed running — a heartbeat that raises every cycle takes the loop with it.

Also log a proof-of-life line that does **not** sit behind the phase gate (every Nth tick,
whatever the phase). The heartbeat above is often inside the "is it the conflict phase yet"
branch, and then "the timer died" and "the phase gate never opened" produce byte-identical
silence for the whole battle.

### One raising callback kills every timer in the battle

The engine's script timers do not run independently. `script/_lib/lib_timer_manager.lua`
drives all of them from one engine timer, and its driver re-arms itself only *after* the
dispatch loop has finished:

```lua
while #battle_model_timers > 0 do
    local next_timer = battle_model_timers[1];
    if next_timer.callback_time <= time_elapsed_ms then
        table.remove(battle_model_timers, 1);
        callback();                       -- raises here and...
    else break; end;
end;
battle:unregister_timer("timer_manager_battle_callback");
if #battle_model_timers > 0 then
    battle:register_singleshot_timer(...);  -- ...this never runs
end;
```

One callback that raises therefore stops **every** repeating callback in that battle, for the
rest of the fight, permanently. What follows from it:

- Wrap the **whole repeating body**, not just the engine calls inside it:
  `local ok, err = pcall(poll_body)`, then count failures and log the first few plus every
  Nth. Per-call `pcall` does not protect against a fault in your own logic between the calls.
- Wrap **each phase callback separately**. The dispatcher shares the shape: an error thrown
  out of one phase callback aborts the loop and starves every callback registered after it,
  so an unrelated cosmetic callback registered early can silently cost you the watch-list
  build and look like a phase event that never arrived.
- When you add a **second** repeating callback for something cosmetic, keep engine and UI
  calls out of it entirely. Two distinct costs live here: on the **model** clock a UI call
  silently does nothing — a control keeps the template's placeholder image while its state
  changes still apply, so it reads as a styling bug — and the model timer can stop running
  afterwards; and a `Resize`/`Layout` issued from any timer context is the kind of call that
  raises, whose price is every timer in the battle. UI work belongs on the real timer:
  `references/wh3-battle-ui-and-input.md`.
- Diagnose the consequence, not the cause: *"the poll logged one tick and then nothing, and a
  phase callback never fired either"* is this failure. The wrapping above is the fix, and an
  error counter in the log is what names the call.
- Belt and braces for anything the player activates: do the UI work from the **real timer**
  (`bm:repeat_real_callback`, gated on a flag that a phase callback raised) — **never from
  the model-timer poll**, which cannot make a UI call take effect at all and can end up
  killing the timer it runs on, and **never from inside the phase dispatch**, which lands the
  appearance and takes the model timer down with it. Better still, avoid the drawing route:
  if the engine already draws the affordance, listen to it instead. See
  `references/wh3-battle-ui-and-input.md` § which clock your callback runs on, and § prefer
  listening to an engine-drawn component.

## Activating the ability: the signature, and how to prove it fired

**`<controller>:perform_special_ability("<ability_key>", target_unit)` — key first, target
second, and the target is MANDATORY.** For a self-buff the target is the unit itself.

The generated annotations describe this ambiguously, and each way of getting it wrong has
its own engine error worth recognising:

```
bad argument #1 to 'perform_special_ability' (battle.unit expected, got no value)
  → the target was omitted entirely
calling 'perform_special_ability' on bad self (expecting special ability name (string) argument)
  → the arguments were swapped: the engine is reading the unit where it wants the key
```

**Settle signatures from the engine's own call sites, before writing any code.** Extract the
vanilla script tree, grep it for the method name, read two or three call sites in full — the
shipped code is the specification, and its convention is what the engine was built against.
This activation appears dozens of times across the quest-battle and benchmark scripts, always
with a target. Only when a method has no call sites anywhere in the shipped tree should you
fall back to holding a short list of candidate shapes, trying one per attempt inside `pcall`,
logging what each returns, and locking to the first that passes a real test.

- **Do not treat a capability query as proof of effect.** `can_perform_special_ability(key)`
  stayed `true` immediately after a call that demonstrably fired the ability, and stayed
  `true` on later polls while the ability was active. It answers "may this unit be ordered to
  use this now", not "is this already running". A probe that never moves is the wrong probe.
- **The usable positive signal is the engine refusing the action while it is active:**

```
error: unit '1' does not support this special ability
```

  Once an activation has landed, repeat attempts during the same window come back with that
  text and recover by themselves after the recharge. Treat it as confirmation that an earlier
  activation worked, and let the user's observation of the effect decide the rest.
- **Log the attempt before the call.** A success line written *after* the engine calls
  disappears exactly when the call fails, leaving a run that shows the condition met, the
  ability available, and no output at all — the most expensive kind of silence. Attempt
  line first, then `pcall` each call, then log the error text.

### Never aim a self-buff at the ground

`perform_special_ability_ground(key, position, …)` **returns success** on an ability whose
data row has `target_ground = false`, while leaving the unit holding a targeting cursor.
In game that reads as a **crossed-out ability icon** and the unit **stopping**, as if its
movement order was cancelled — because the order took control of it. A speculative "try
the other variant as a fallback" becomes the visible bug the user reports, and it looks
for a whole round like the game misbehaving.

Before adding any fallback call, read the ability's own targeting columns (`affect_self`,
`target_self`, `target_friends`, `target_enemies`, `target_ground`) from its data row and
only call a variant whose preconditions the ability actually satisfies.

### Orders take control of the unit

A `battle_unitcontroller` takes control of its units when it issues an order, and a
player-owned unit under script control has its card greyed out. The script's own side
effects — a unit that stops mid-manoeuvre, a greyed card — are therefore *the script's*
doing, not the engine's. Prefer releasing control immediately after acting, treat an
explicit `take_control()` as a suspect rather than hygiene, and list these side effects in
 the deliverable so the user is not measuring your bug against the ability's behaviour.

## Condition mapping, and the one honest gap

| Wanted trigger | Read it with | Note |
|---|---|---|
| Health band | `unary_hitpoints()` (0–1 of starting HP), `unary_of_men_alive()` | fraction, not an absolute |
| In melee | `is_in_melee()` | paired with `out_of_melee` in the data layer |
| Losing / winning melee | **not readable directly** | the data-layer flag exists; in script, derive it from health or casualty deltas over successive polls |
| Morale state | `is_wavering()`, `is_routing()`, `is_crumbling()` | maps onto the morale band flags |
| Fatigue | `fatigue_state()` | returns a threshold string; compare, don't parse a number |
| Charging | **no direct query — compose it** | `is_moving_fast()` means running *or* charging, so on its own an order to **run to a spot** counts as a charge. Require the run **and** `not is_in_melee()` **and** `current_target() ~= nil` — a move order sets no target, and having one is the only reliable attack-versus-move signal. Then add a **run-up window** (`unit_distance(target)` between a floor and a ceiling) and fire when impact is near, estimated as `unit_distance(target) / unit:fast_speed()` seconds. **Do not gate on `position():distance(ordered_position())`.** The docs claim that while a unit is *attacking* `ordered_position()` returns its *current* position; measured across a real charge it does the opposite — the gap climbs steadily (17 m → 322 m) because it tracks the order's original point, i.e. **distance travelled since the order was given**. As a gate it passes only clicks made within a few metres of the enemy and blocks every genuine charge, while looking correct in a mock and even firing on the first post-order poll. Keep it as a logged diagnostic only |
| Target / position | `current_target()`, `position()`, `unit_distance(other)` | needed by any ability that must pick a unit |
| Alive | `number_of_men_alive()` | single-entity characters report 1 or 0 |

## Check the data layer before scripting an approximation

If the wanted trigger is a **state the engine already tracks**, the data layer may already
ship it — and a data-layer trigger is evaluated against the engine's own internal state,
whereas a script can only approximate that state from queries (the Charging row above took
three rounds to get right, and the approximation was still only ever close).

Worth a few minutes before writing any condition logic, all in the dump's database tables:

1. **`special_ability_to_auto_deactivate_flags`** (`deactivate_flag`, `special_ability`) —
   the table that makes an ability self-managing. A **`passive = true`** ability plus a row
   here turns the effect **off while the named condition holds**, which is how the engine
   says "on only while X". The charge answer is `unit_is_not_charging → <ability key>`:
   about ten shipped abilities use it and every one is a charge-only effect
   (`unit_passive_murderous_charge`, `unit_passive_ferocious_charge`,
   `character_passive_befouled_charge`, `unit_passive_impetuous`, …). Flip the target
   ability's `passive` column and add the row, and the engine does the timing itself.
2. **`special_ability_to_invalid_usage_flags` / `…_invalid_target_flags`** — the *blocking*
   vocabulary. It can stop a player using an ability; it can never fire one. The same flag
   may exist in one table and not another: the engine ships **no** charge entry in the
   invalid-usage list, so `unit_is_not_charging` is a deactivate-only flag — do not infer
   the reverse mechanism from a flag's presence.
3. **The ability's own `ai_usage` value**, when set, points at the AI's scoring rules:
   `battle_ai_abilities_usage_templates_to_params_tables` (parameter → template, with a
   weight), `…_template_names_tables` (`factor_bias`) and
   `_kv_battle_ai_ability_usage_variables_tables` (`min_score_for_activation = 0.5`). A
   self-buff tagged `augment_charge_self` is scored on exactly one parameter, `bool_charging`,
   at weight 1.0 — so the engine's own rule for it is "fire if and only if charging". That
   confirms both the intended condition and that the engine treats that state as reliable.
   `bool_charging` is engine-internal; no script function exposes it.
4. **Ruled out — do not spend time here:** `intensity_based_activation` is set only on
   abilities that are *already* passive and has no supporting tables or script functions;
   `battle_toggle_system` is siege map barriers and tower slots, not ability toggles;
   `ai_planner` will hand a unit to the AI (whose own logic then uses the ability correctly)
   but exposes no per-ability control and gives up the unit's movement with it.

**What the data route costs — say this before recommending it.** The ability stops being
clickable (a `passive` has no button on the card); the change applies to every faction and
AI unit, not just the one under test; the engine's own numbers keep applying, so a cooldown
raise is the usual payment for an ability that now fires itself — a shipped mod doing exactly
this paid roughly **1.3× the skill's `recharge_time`** (90 s → 117 s) for one ability, which is
a sane starting point to quote; and being a database edit it must be re-checked after patches,
unlike a script file.


The data layer, not the tooltip, decides this:

- The ability's battle row lives in `unit_special_abilities` (`passive`, `active_time`,
  `recharge_time`, `num_uses`, `mana_cost`, `ai_usage`). Quote those numbers in the
  deliverable — they say what a sensible trigger is.
- **`land_units_to_unit_abilites_junctions` is the unit's innate list** (the misspelling
  is the engine's). A custom/skirmish battle gives a unit only these; campaign also grants
  skill-tree abilities, which is why an ability a character demonstrably has in a campaign
  can be missing from the same character in skirmish. Look the unit key up there before
  promising it will demonstrate anything in a custom battle.
- **Match on keys, and accept a list of them.** The same ability can exist under more than
  one key (a main and a legacy/variant copy). Scan the unit's own
  `owned_special_abilities()` for any candidate key and remember which one matched, rather
  than hardcoding a single string and betting the test on it.
- **Re-check units that show nothing.** Ability instances may not all be attached at the
  moment the watch list is built; re-scan those units every few seconds and log a
  `late find` line instead of failing silently.

## Verifying without the game

```bash
uv run --quiet --with lupa python scripts/lua_check.py path/to/mod.lua   # syntax gate
```

Lua is rarely on PATH, and this host is not the one the code runs on. `lupa` compiles
and executes Lua from Python, which covers both the syntax gate and a real logic test.

**Mock harness shape.** In one Lua chunk, build stand-ins for every call the file makes:

- `bm` with `is_conflict_phase`, `get_scriptunits_for_local_players_army`,
  `repeat_callback` (capture the poll function), `register_phase_change_callback`;
- a collection object with `count()`/`item(i)`;
- unit objects whose methods return fixed values per scenario;
- a controller object that records the calls made on it.

Then `loadfile(mod)()`, call the captured poll function in a loop, and mutate the mocks
between phases. Assert at minimum:

1. it fires **only** on the eligible unit — include one decoy per condition (in melee,
   idling/walking, dead, ability not owned);
2. a unit owning only a *variant* key still fires;
3. the cadence respects the local rate guard;
4. it stops once the condition ends;
5. the diagnostic log line prints the ownership check, and the log guard survives an
   undefined `ModLog`;
6. **omit one method from the mock on purpose** (e.g. the phase-name query) and assert the
   heartbeat still writes — that is the only cheap way to prove a `pcall` guard actually
   guards;
7. **make one unit's activation call raise the engine's real error string** and assert the
   attempt line, the error text and the following step all reach the log — the mock is the
   only place a signature mismatch is cheap to rehearse.

**Replay the last real battle through the new logic.** The strongest proof available without
launching the game. The log already carries a per-heartbeat sample series (target, distance,
gap, in-melee, speed), so interpolate it back up to the poll cadence, drive the *real* file
against a mock unit whose state is set from those samples, and report which samples now trip
the condition. It upgrades "the mock passes" into "on your own battle data this would have
fired at 28 m out and stayed silent at 150 m". It is also the only cheap way to catch a gate
that is arithmetically right but unsatisfiable in practice: the wrong `ordered_position()`
gate passed a clean mock and died on a replay.

**Get the arithmetic right before calling anything a failure.** Expected fires =
`eligible_ticks / (brake_seconds * 1000 / poll_ms)`. A mis-set expectation is
indistinguishable from a code bug and burns a cycle chasing nothing; if the harness
reports fires and your "expected" is the only thing that disagrees, re-derive the
interval before touching the mod.

**What this proves:** syntax, control flow, condition logic, guard arithmetic. **What it
cannot prove:** anything about the engine — control handover on a player-owned unit,
whether a state query tracks what you assume it tracks, whether the collection handle
exposes a usable controller in every battle type, and frame cost at scale. State that split in the
deliverable with the claim, not in a footnote.

## Build, verify and install without the GUI

The editor ships a headless backend (`rpfm_server`) exposing the same API its UI uses,
over a local WebSocket — so this cycle does not need to be handed to the user as menu
steps. `scripts/build_and_install_pack.py` implements it; the shape is:

1. Extract the portable editor build somewhere that does **not** need admin rights (it
   writes update files relative to its own location) and run `rpfm_server.exe`. It binds
   `127.0.0.1:45127`: `/ws` for the JSON protocol, `/sessions` for REST, `/mcp` for MCP.
2. Messages are `{"id": N, "data": <command>}`; correlate replies by `id` and ignore the
   unsolicited `{"id": 0, …}` handshake message (`SessionConnected`).
3. Command sequence: `SetGameSelected` → `NewPack` → `AddPackedFiles` →
   `SetPackFileType` → `GetPackedFileRawData` (hash it) → `SavePackAs` → `ClosePack`.
4. **Expect the server to exit when its last session disconnects.** Do the whole build in
   one session, or restart it before the next step.

Details, exact JSON shapes and the traps: `references/rpfm-server-protocol.md`.

**Install = copy the `.pack` into `<game install>/data/`.** That is the whole step; on a
normal Steam install that folder is writable without elevation. Nothing needs the
launcher's Install button, and — for a `Movie` pack — nothing needs the mod manager
 either, because the engine loads it unconditionally. Use type `Mod` only when the user
should be able to toggle the mod themselves.

**Verify the artifact, not the write.** After saving, read each file back *out of the
pack* and hash it against the source; after copying, hash the installed copy. A pack that
"saved successfully" is not evidence it holds the right bytes, and the failure mode is a
silent in-game no-op that costs the user a battle.

## In-game test loop, and how a run fails

1. Fully exit the game and launcher so `data/` is re-scanned, then relaunch. With a
   `Movie` pack there is nothing to enable.
2. Start a battle with a unit that actually owns the ability in *that* battle type, and
   perform the trigger **and its negative twin**: for a charge condition, order the unit to
   **move to empty ground** (must not fire) and then to **attack a distant enemy** (must
   fire), watching the unit card. A condition that has only ever been seen to fire may be
   firing on something else — the paired run is what falsifies it.
3. Read the mod's own log file in the game install folder, and the loader's
   `lua_mod_log.txt` beside it, searching for the file tag.
4. Watch the unit card during and after activation — that is the handover question.

| Symptom | Cause |
|---|---|
| Loader log shows the file loaded, mod log shows only the watch list | the poll ran but no trigger was ever met — the heartbeat line is what tells you which |
| Loader log shows `Failed to execute loaded mod file` | the script raised while loading; the error text is on that line |
| No tagged lines anywhere, and no file in the loader log | pack not in `data/`, wrong internal path, or wrong pack type |
| `owns … = false` on the unit the user expected | it is not in that unit's innate list for this battle type, or the skill is not taken |
| `can use … = true` but it never fires | the condition was never met — walking is not running, and arriving in melee first skips a run-in trigger |
| `ok=true`, nothing happened, and the unit holds a crossed-out ability icon | a wrong-target order was accepted (see the ground-variant trap above): it took control and cancelled the unit's movement order, which the user experiences as the unit stopping |
| The unit stops mid-manoeuvre but no ability fired | an order from the script took control — the script's own side effect, not the engine's |
| Fires, but the card greys out | control handover: try the queued activation variant, or drop the explicit release |
| First attempt logged as accepted, later attempts log `does not support this special ability` | normal while the ability is active and recharging — that refusal is the engine confirming the earlier activation landed, not a new fault to chase |

**Direct API poking beats reading docs.** With an in-game Lua console, a handful of
one-liners sequence answers the whole design question: list the units, list one unit's
owned abilities, ask the legality check, ask the state queries, then perform the action
once by hand. The last one isolates the activation from the polling logic entirely —
that is the experiment to hand the user first.

**Lua 5.1 note:** `string.format` does not coerce booleans or floats — `%s` on a boolean
raises. `tostring()` every argument in log lines; a diagnostic that throws is worse than
no diagnostic.
