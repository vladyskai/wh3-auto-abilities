# WH3 units and created objects: identity, mid-battle arrivals, disposal (measured)

## Unit identity: the read that moves when a unit changes shape
- `battle_unit:type()` returns the unit's land_units key and **changes on a transformation or
  mount** — human form and dragon form are different records, so the read moves. Vanilla uses
  `sunit.unit:type()` as its identity test (`lib_bsu.lua`). There is no script-level transformation
  accessor: `spawn_is_transformation` is only a DB column.
- Read it through the poll's unit handle (`script_unit.unit`, a battle_unit), pcall'd, and treat a
  nil/failed read as "no information" — never as a change.
- **Never ship a permanent "scanned, found nothing" flag.** The engine's own identity read is the
  cheap signal that a loadout may have changed, so: keep a per-unit last-seen identity, do one
  identity read per re-check cycle for units with no matching ability, and run the full ability
  scan ONLY when the identity changed. Add a slow fallback rescan (order of a minute) so an
  unreadable or unchanging identity degrades to the previous behaviour instead of to silence.
  Log one line only when a rescan actually happens AND finds something.
- Why not a timer: the old shape rescanned every keyless unit every few seconds forever. Measured
  saving with the identity watch: an ability-less unit costs ~6 identity reads over 100 polls and
  **zero** extra scans, versus a full scan per cycle before.

## Mid-battle arrivals (summons, splits, transformations)
- A unit list built once at battle start never sees a unit that appears later. Re-list the player's
  army on a coarse cadence **reused from the existing poll** (no new timer): one army read every
  ten seconds is cheap and needs no engine event.
- The rebuild must be **additive and identity-based** (key by the unit's `unique_ui_id`):
  - never wipe the registry — per-unit state (armed flags keyed by unit|marker, cached keys,
    badges, letters) must survive the refresh untouched;
  - only genuinely new ids are appended, scanned, and registered for the selection callback;
  - existing units are **not** re-scanned by a refresh;
  - units the engine no longer lists are dropped;
  - log ONE coalesced line only when the tracked set actually changed (`unit list refresh: <n> new
    unit(s) now tracked (<ids>)` / `... dropped`), silent otherwise — a refresh every ten seconds
    must not spam.
- The red control for this round exposed a second defect worth fixing in the same pass: the old
  wholesale rebuild kept reading dead units' stale handles every poll (and could act on them).
  Dropping dead units on the refresh tick is part of the fix, and the harness proves it by
  asserting zero further reads for the removed id.
- Harness shape: a dynamic mock army (`W.add_unit` / `W.remove_unit`) plus per-unit scan counters
  and a poll-tick counter, so one run proves (a) a unit added at poll N is tracked, scanned once,
  registered once, armable and firing on the same refresh tick; (b) a survivor's armed state still
  fires; (c) an unchanged refresh re-scans nothing, re-registers nothing and logs nothing; (d) a
  removed unit stops being read and its drop line appears exactly once.

## Disposing a created component: destroy, do not just forget
- `UIComponent:Destroy` exists (with `DestroyChildren`, `RemoveTopMost`). A component that was
  created and then abandoned mid-construction stays parented in the HUD if you only nil the Lua
  reference, and every retry leaks another — a systematic creation failure leaks at tick rate.
- Audit every nil-clearing site before swapping: one where the assignment provably cannot have
  completed holds nil already and must stay byte-identical (a blanket replacement over-reaches).
  Only the sites that can hold a live component (mid-creation failures, a raised create path) get
  the destroy.
- Helper shape: probe that the component's destroy method exists, `pcall` the call, swallow and
  log a refusal, then clear the reference and whatever the site cleared. Never let an engine error
  escape.
- Proof shape, all three parts needed: forced mid-creation failure -> **exactly one** destroy on
  the failed component and a fresh retry that completes; hostile destroy (raises) -> swallowed,
  logged, retry still works; normal operation across every other world -> destroy count **0**.
  The red control shows the leak ("components left orphaned: 1") on the forced-failure world.

## Script-side handles for unit state reads
- `script_unit` (the dumped API) has `is_in_melee` but NOT `is_moving_fast` / `is_routing`; the
  poll's `unit` is `script_unit.unit`, a **battle_unit**, and answers all three — so route
  auxiliary state reads through that same handle instead of hunting for a script_unit accessor.
- Do ONE guarded read per unit per poll and share it across every trigger, testing strictly
  `== true` so a dressed, raising or missing answer **fails open** (behaves like the old build)
  rather than blocking a legitimate fire. Classic example: suppress auto-fire while routing, but
  let a broken routing read fire as before.
- A unit that is "moving fast" inside a fight is not routing. Routing means morale broken and
  fleeing; guards keyed on routing will not stop a control from acting mid-melee, so if the intent
  is "only while closing", the condition is `not is_in_melee()`, not a routing guard — ask which
  one is meant before building it.
