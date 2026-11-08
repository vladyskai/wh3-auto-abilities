# Release 2026-10-08 — Glorious Death RANGE TIGHTENED 55 m → 25 m — harness87

USER INSTRUCTION (verbatim): _"I tested Glorious Death again and it casted too
soon. Make it 25 m to make sure it is in range."_

## Shipped source
`script/battle/mod/zz_test_deadly_onslaught.lua`  sha256 `f37f83e75f896310…` (266401 bytes)
`WH3_auto_ability_annotated.lua` (Desktop reading copy)  sha256 `add8676be6248481…` (177355 bytes)
Pack installed to `.../Total War WARHAMMER III/data/zz_test_deadly_onslaught.pack`
installed md5 `8eaf0819b592482e9a73eb5309bb4be3` (dist == installed, IDENTICAL True;
pack sha256 `b2385b05d997634f…`, size 601531);
per-file sha256 gate: all 5 shipped files MATCHES SOURCE True.
Independent PFH5 re-read (`verify_cleaned_independent.py`): **RESULT PASS** — 5/5 files
byte-identical, dist == installed, no probe paths.

## THE CHANGE — one constant, plus the comments that described the old gate
Harness 86 introduced `local GLORIOUS_DEATH_RANGE_M = 55` (the ability's wiki
"Effect range: 55m"). Field testing then showed 55 m still fired **too early**, so
the trigger range is tightened to a **DELIBERATELY CONSERVATIVE 25 m** — deliberately
**tighter** than the ability's 55 m wiki aura. The wiki's real effect range stays in
the constant's comment for reference.

* **LIVE line 732** (was 729): `local GLORIOUS_DEATH_RANGE_M = 25`
* ANN line 735 (was 732): `local GLORIOUS_DEATH_RANGE_M = 25`
* The constant's comment block was rewritten to read as a deliberately conservative
  trigger range chosen after field testing, and to name the wiki's actual
  "Effect range: 55m" for reference (`DELIBERATELY CONSERVATIVE`, `55 m wiki aura`).
* The four other comments that described the old 55 m gate were updated to the
  conservative 25 m trigger (LIVE 2258-2259, 2597, 2701-2704; ANN 1831, 2058, 2143-2144).

**No logic changed.** The gate, the CLOSEST in-range in-melee Slayer choice, the
pre-cast re-check (gap re-read, cast SKIPPED on drift) and the fail-open on an
unreadable gap are the harness-86 machinery, byte-for-byte. The cast TARGET stays
the OWNER (`FOURTH.cast_target = unit`, x2); the owner-in-melee self arm is NEVER
gated. No new chunk locals (the four dead icon-read locals stay removed; the LIVE
chunk remains under Lua's 200-local ceiling).

## Harness 87
Built from the SHIPPED harness86.lua (env pair now `H87_LIVE` / `H87_ANN`). Patches:
env rename, red banner, and the spliced range-gate section **replaced** by the
re-baselined HARNESS-87 section. The mock `dist_seq` (drift) added in round 86 is kept.

Worlds (section 0i static tokens + SEVEN worlds, each run `[annotated]` + `[live]`),
re-based for the 25 m threshold:
* **R1** — ally WITHIN range → fires (**20 m**; was 30 m).
* **R2** — ally BEYOND range → **SILENT** (**55 m**, the old wiki aura; was 200 m) — the field-test complaint.
* **R3** — two in-melee Slayers, one nearer (farther defined FIRST) → the **nearer** (8 m) is chosen; the farther (22 m) is ALSO in range.
* **R4** — owner in melee, no Slayer ally → self-casts, **ungated** (non-Slayer ally never offered).
* **R5** — **drift**: ally in range at decide (20 m), out at cast (55 m) → cast **SKIPPED**.
* **R6** — **BOUNDARY just UNDER**: **24 m** (one metre inside 25) → **FIRES** (NEW).
* **R7** — **BOUNDARY just OVER**: **26 m** (one metre outside 25) → **SILENT** (NEW).

GREEN: **checks: 2190, failures: 0** (harness-85 suite boundary `checks == 2105` holds;
**+85 new checks** over the boundary, vs round 86's +64 — R6/R7 and the extra 0i tokens).

RED (pre-edit snapshot, this dir's `pre87_snapshot/` = the shipped harness-86 build,
constant still 55): **checks 2163, failures 19** — every one a designed delta:
* 8 section-0i token checks (4 per file): the 25 m value, the "no longer 55" pin, the
  `DELIBERATELY CONSERVATIVE` comment, and the 55 m wiki-aura reference note.
* R2 (4): the 55 m ally still FIRES on the snapshot — the field-test complaint.
* R5 (3): its 55 m cast leg is still in range on the snapshot → no skip.
* R7 (4): the 26 m boundary ally fires on the snapshot.

No FAIL anywhere outside the HARNESS-87 section; the re-based older red aggregates
(h82/h83/h84/h85) all pass by design; world tally **8/14** (R1/R3/R4/R6 pass, the six
R2/R5/R7 live+annotated results fail), as designed.

## Tracker
Not touched (no ability status changed — only the tuned range).
