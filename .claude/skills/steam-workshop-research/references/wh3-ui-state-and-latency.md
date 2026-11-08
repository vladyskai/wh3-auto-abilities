# Script-drawn battle UI: state derivation, visibility, update latency (WH3, measured)

## Selection state: the engine has an event for it — the cards do not
- `CurrentState() == 'selected'` is authoritative for a **single** selection only. Measured with a
  group of ten units box-selected: **no card reported `'selected'`** — every card read `'active'`,
  and the census line said `no card reports selected - tracker stays <id>`. Any selected-set derived
  from card states is therefore blind to group/box/ctrl selections, and so are the card-shaped
  helpers `num_units_selected` / `is_any_unit_selected` / `are_all_units_selected`, which read the
  same state. Do not reach for them as the group signal, and do not treat the absence of a
  `'selected'` card as "nothing is selected".
- The script-reachable mechanism is the engine's own callback:
  `battle_manager:register_unit_selection_callback(unit, callback)`. It is **per unit**, so register
  each tracked unit once (guarded; treat a `false` answer as not registered) and re-register for
  units that join later via the periodic army re-list. The callback fires on select AND deselect
  with a selected boolean. Wrap its body in `pcall` — an error escaping a callback can take the
  battle's callbacks down with it.
- The battle-level `battle:register_unit_selection_handler(name)` allows **ONE** handler and
  overwrites any previous one (its own doc comment says so), which is why vanilla's `lib_bm.lua`
  keeps a single shared dispatcher keyed by unit. Either copy that dispatcher pattern or stay on the
  per-unit callback.
- Maintain `selected_ui_ids` from the callback; keep the card sweep as fallback/reconciliation, and
  make its precedence explicit: the cards REPLACE the set only while no callback event has ever
  fired, otherwise they may only add ids they observe (tracked so they can be dropped again) —
  never let a card-derived id linger as a phantom.
- COALESCE the log: one line per resulting SET change (e.g. `selection callback: <n> unit(s)
  selected now (<ids>)`). Never one line per event: a ten-unit box-select must produce exactly one
  line, and an add+remove inside one tick must produce none.
- Click events remain a fast path only; world selections fire no component event at all. Keep a
  per-click context line (`click: <marker> badge -> selected unit <ui id>`) so a mis-attributed
  toggle is provable from the log, and log each adoption once, tick-stamped
  (`selection changed to <id> - refreshing badge letters (tick N)`), refreshing dependent elements
  in the same call.
- Multi-select semantics for a per-unit control: arming stays keyed per (unit, marker); a badge
  click over several selected owners is checkbox-style (all armed -> disarm all, else arm all);
  selected units that do NOT own the ability are never touched; the letter reads 'A' only while
  EVERY selected owner is armed.
- Tie the control's state to the LIVE set, not to a per-unit cache: a cached key belongs to the
  unit, not to the ability being fired — a unit can carry two of the abilities at once, so "use the
  cached key when present" fires the wrong one. Match the cached key against the ability in hand.

## Visibility: one decision point per element
- Two separate rules, both needed:
  1. handle rule — if the held component no longer reports OUR ability key (or its reads raise),
     hide and DROP the handle so the rescan can re-find it;
  2. claim rule — every tick recompute `shown = marker claimed on this dial` and apply+log on
     change. One stray unconditional `SetVisible(true)` on another path (the letter-refresh call)
     re-showed ghost badges on dials that did not claim the marker; the ghosts stayed visible AND
     clickable, toggling state for units that cannot use the ability (`click ignored: <marker> is
     not on this unit's dial` is the guard + log).
- One cached writer per element: compute desired text/visibility, write only on change, log one
  line per change; the per-tick safety net re-derives but stays silent while steady. Counted
  `SetText` calls over idle ticks must be 0 — that is what "no spinning" means in the harness.

## Update latency: what is achievable (measured)
- **`Layout()` after a real write is the working redraw lever** — calling it (pcall'd) on the
  element AND its parent immediately after `SetText` removed the felt delay on badge-letter flips,
  confirmed by the user across battles. It is the only redraw-adjacent call in the 141-method
  UIComponent API (no Update/Refresh/Redraw/Invalidate exists).
- **Make the nudge structural.** Put it inside the one function that performs `SetText`, so no
  caller can skip it — an earlier assumption of "a single writer" was wrong (three real write sites
  existed), and per-site nudges leave the next added path un-nudged. Proof shape: record `SetText`
  and `Layout` calls in order and assert every `SetText` is immediately followed by a `Layout` on
  both element and parent, counting violations; then a MUTATION control (strip the nudge from the
  writer) must show those violations firing. A red control that reports ZERO violations only proves
  the pre-fix code was already correct — that round is enforcement/log-format, not a behaviour fix,
  and must be reported as such rather than claimed as a repair.
- Mark genuine no-write paths explicitly (` (no write)`): an unchanged-letter log line without that
  marker reads exactly like an un-nudged write and sends the next agent hunting a bug that does not
  exist (measured: exactly that misread, one wasted round).
- Timer semantics (vanilla `script/_lib/lib_timer_manager.lua`): model timers are ms in battle /
  s in campaign; real timers (`bm:repeat_real_callback`) take ms in ALL modes but dispatch is
  UI-update driven with VARIABLE resolution that "can be greater than a model tick (100-200 ms)".
  A registered 50 ms is therefore not a 50 ms felt latency — never quote the registered interval
  to the user as the response time, and do not trust a file's own stale cadence prose over its
  registration arguments.
- Why vanilla feels instant while script state does not: vanilla widgets (cooldowns, countdowns)
  are drawn by the engine's own widget code on the RENDER path, while `SetText`/visibility on a
  script-created component land on the slower UI-UPDATE pass. Present as the likely mechanism
  (no public source found stating it), not as documented fact.
- Triage residual delay from the battle log before building anything else: count selection
  changes delivered as click events (handled synchronously) versus adoptions found only by the
  state read. Measured here: 6 of 8 click-delivered, 2 only by the read — that remainder is
  engine event/state delivery and no script change moves it. When the lever set is empty, say so
  plainly ("no, and here is why") instead of shipping another variant.
