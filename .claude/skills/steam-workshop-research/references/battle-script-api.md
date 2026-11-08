# Battle-script API cheat sheet (measured, not guessed)

All facts below were verified against the game's own Lua API dumps and vanilla script usage -
not inferred from documentation. Check here before re-diving dumps or the vanilla `script/` tree;
each entry cost hours to establish once.

## Selection

- `battle_manager:register_unit_selection_callback(subject_unit, callback)` is PER-UNIT and is the
  only way to observe a GROUP/box selection. The battle-level
  `battle:register_unit_selection_handler(name)` allows ONE handler (the dump says it overwrites),
  which is why vanilla keeps a single shared handler and dispatches per unit.
- Unit-card `CurrentState()` marks at most the FOCUSED card as `'selected'`; under a box/group
  selection every card reads `'active'`. A selection model derived from cards is therefore
  structurally blind to multi-select, and `num_units_selected` / `is_any_unit_selected` /
  `are_all_units_selected` are derived from the same card state, so they are not a second opinion.

## Morale

- No percentage read exists. `battle_unit:is_wavering()` is the only morale threshold read
  (first band below steady); siblings `is_routing`, `is_shattered`, `is_crumbling`, `is_unstable`.
- The morale `@return` names in the dump (`morale_is_lower_than_half_of_base_morale`, ...) are
  ORPHANED docgen annotations with no function behind them - calling one throws.

## Casting and targeting

- `perform_special_ability(ability_key, target_unit)` takes a UNIT.
- `perform_special_ability_ground(ability_key, position, orientation_degrees, width_m)` is the
  separate form for ground-targeted casts; the abilities TSV columns `target_ground` /
  `target_friends` identify which form an ability needs. Vanilla never calls the `_ground` form,
  so the dump is the only evidence that it exists.
- An aimed cast with an unreadable position must fail CLOSED (skip, log once) - never aim a guess.

## Cooldown / readiness

- `can_perform_special_ability(key)` is the only readiness read, and it answers TRUE while the
  engine still refuses the cast - it does not report cooldowns.
- No per-unit cooldown/active-state read exists; the only other entry is
  `reset_ability_cooldown`, a WRITE. A component's own state is mouse/theme state (reads
  `'active'` through a refusal) and describes the selected unit only.
- The refusal text for a recharging ability and for a non-existent unit are the SAME shape
  (`... on bad self (error: unit 'N' does not support this special ability)`), and the id in it is
  an internal index, not the army's ui id. Never key a unit-drop on it - match explicit
  non-existence markers only, and prove disjointness statically.

## Firing / missile state

- There is **no per-unit read for "is this unit firing/shooting right now"**. Established by
  enumerating the dumps; do not re-research it, and do not substitute a proxy for it.
- The near-misses and why each fails: `is_under_missile_attack()` describes the unit RECEIVING
  fire (the wrong direction); `current_target()` is set for melee units too, so it proves nothing
  about firing; `ammo_left()` / `starting_ammo()` prove a unit fired SOMETIME this battle, not
  that it is firing now; `missile_range()` is a static property; and the battle-level
  `get_num_units_under_fire()` / `get_proportion_under_fire()` are also under-fire, not outgoing.
- The `is_missile_unit` / `is_under_missile_fire` / `cannot_perform_missile_attack` flags live in
  `flags.tsv`, a DATA-TABLE construct for the game's own auto-activate system, not a Lua read.
- The booleans a script can trust (`is_routing`, `is_wavering`, `is_in_melee`, `is_moving_fast`)
  are same-class `battle_unit` reads and nothing in that class answers "firing". When a requested
  trigger needs this read, implement the half that is buildable, cast on self, and report the gap
  plainly rather than approximating it.

## Identity, existence, UI

- `battle_unit:type()` returns the land_units key and MOVES on a transformation/mount: use it as
  the change signal for a re-scan instead of a permanent "already scanned, nothing here" memo.
- Aliveness: `number_of_men_alive()`; a RAISING read is transient, a nil identity read is a
  supported live state - neither is death.
- `battle_unit:is_routing()` / `is_shattered()` live on the battle_unit layer; a script_unit
  wrapper reaches them via `.unit`. `script_unit` has `is_in_melee` but not
  `is_routing`/`is_moving_fast`.
- Component `Destroy()` exists and is required: dropping the Lua reference leaves the component in
  the HUD (a retry loop then leaks one per attempt).
- `Layout()` is the only redraw-adjacent method of the ~141 in the UI API, and calling it on a
  component AND its parent right after a text write is what makes a script-drawn label flip
  promptly; without it, flips lag visibly on a static screen.
- `Id()` on a real ability button can answer with a FUNCTION, and `GetProperty` echoes the
  property NAME rather than a value - never gate logic or liveness on either.
- A mod's main chunk shares Lua's 200-local limit: bundle new helpers as fields of ONE local table
  (`local X = { ... }` + `function X.helper(...)`) or the file stops compiling entirely.
