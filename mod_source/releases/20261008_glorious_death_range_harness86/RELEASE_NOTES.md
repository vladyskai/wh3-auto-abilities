# Release 2026-10-08 — Glorious Death RANGE GATE (the reported bug fix) — harness86

USER REPORT (verbatim): _"it casted before the slayer unit that was fighting was
in range of the ability."_

## Shipped source
`script/battle/mod/zz_test_deadly_onslaught.lua`  sha256 `6db1460bc524e9cc…` (266125 bytes)
`WH3_auto_ability_annotated.lua` (Desktop reading copy)  sha256 `1aeb0a4f2b906a95…` (177079 bytes)
Pack installed to `.../Total War WARHAMMER III/data/zz_test_deadly_onslaught.pack`
installed md5 `f589df5f61646d93ed621e5aaee92ea7` (dist == installed, IDENTICAL True);
per-file sha256 gate: all 5 shipped files MATCHES SOURCE True.
Independent PFH5 re-read (`verify_cleaned_independent.py`): **RESULT PASS** — 5/5 files
byte-identical, dist == installed, no probe paths.

## ROOT CAUSE
Since the fix that always casts on **SELF** (harness 85), the engine no longer
refuses the cast — the caster is trivially in range of *itself* — so the ability
fired even when the in-melee Slayer ally was far away and the 55 m aura would not
reach it. A wasted cast.

## THE FIX — a DISTANCE GATE on the Glorious Death trigger
* **The constant (single place to tune).** `local GLORIOUS_DEATH_RANGE_M = 55`
  in the SETTINGS section (LIVE line **729**; ANN line 732), clearly commented as
  **wiki-sourced**: the ability's wiki effects line reads **"Effect range: 55m"**.
* **The ally arm is gated.** An in-melee Slayer ally arms the ability only while the
  owner is WITHIN `GLORIOUS_DEATH_RANGE_M` of it. Reuses the mod's **EXISTING**
  distance machinery — the charge detector's `battle_unit:unit_distance` primitive
  (section 5), via the new helper `FOURTH.gd_ally_gap(unit, ally)`. No new API call.
* **The CLOSEST in-range ally is chosen** (not merely the first / the lowest-health),
  so the aura actually covers the chosen unit: the evaluator scans every candidate and
  keeps the minimum gap, recorded in the FOURTH field `FOURTH.gd_ally`.
* **Re-check immediately before the cast.** `attempt_activation` re-reads the gap via
  `FOURTH.gd_ally_in_range` right before the `perform_special_ability` call; if the ally
  has drifted out of range the cast is **SKIPPED** (`glorious_death SKIPPED: …`, outcome
  `held`) rather than wasted.
* **The owner-in-melee self-cast case is NEVER gated** — that arm leaves `FOURTH.gd_ally`
  nil, so the re-check is a no-op. Casting on self is always in range.
* The **cast TARGET stays the OWNER itself** (`FOURTH.cast_target = unit`, x2, unchanged);
  only the *choice of whether to fire* is gated. A chosen-ally line is logged for the field
  (`glorious_death ally: ui <id> at <gap>m is the CLOSEST…`).
* FAIL-OPEN on an unreadable gap (treated as in range), matching the charge detector.

## Local-ceiling housekeeping (documented, required)
The LIVE chunk sits AT Lua's **200-local** ceiling, so a new local would not compile
(proven: `too many local variables (limit is 200)`). The **dead** icon-read block —
`ICON_INDEX`, `original_icon`, `read_icon`, `original_state` — was removed to free the
slots for the constant. All four were never called or read anywhere, and the reading
copy never carried them. No live local was otherwise changed. (Precedent: a prior round
freed `CHARGE_ORDER_TOLERANCE_M` for the same reason.)

## Harness 86
Built from the SHIPPED harness85.lua (env pair now `H86_LIVE` / `H86_ANN`). Patches:
env rename, red banner, the mock `unit:unit_distance` gains a `dist_seq` (a per-call
SEQUENCE) so a world can model the ally drifting between decide and cast, the four older
rounds' red aggregates re-based for the advanced snapshot, and the new HARNESS 86 section.

New section (0i static tokens + five worlds, each run `[annotated]` + `[live]`):
* **R1** — in-melee Slayer ally WITHIN 55m → fires (owner not in melee).
* **R2** — in-melee Slayer ally BEYOND 55m → **SILENT** (the reported bug, fixed).
* **R3** — two in-melee Slayers, one nearer (the farther defined FIRST) → the **nearer** is chosen.
* **R4** — owner in melee, no Slayer ally → still self-casts, **ungated** (non-Slayer ally never offered).
* **R5** — **drift**: ally in range at decide (30m), out at cast (200m) → the cast is **SKIPPED**.

GREEN: **checks: 2170, failures: 0** (harness-85 suite boundary `checks == 2105` holds;
**+64 new checks**).
RED (pre-edit snapshot, this dir's `pre86_snapshot/` = the shipped harness-85 build):
**checks 2143, failures 24** — every one a designed delta: the section-0i tokens (16),
the R2 worlds (3: the bug fires on the snapshot), R3's live half (1: no chosen-ally line),
and R5 (4: the drift world fires on the snapshot). No unrelated check fails; the re-based
older red aggregates (h82/h83/h84/h85) all pass by design.

## Tracker
Not touched (no ability status changed).
