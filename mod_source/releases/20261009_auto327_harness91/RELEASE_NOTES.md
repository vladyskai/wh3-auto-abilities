# HARNESS 91 / the 327 auto-accepted abilities - release notes

## What shipped
THE AUTO-ACCEPT IMPLEMENTATION BUILD. All **327** abilities the standing
auto-rules R1-R4 sweep (2026-10-09, provenance `_classify_wh3.py`) marked
`approved (auto: <trigger>)` in `WH3_ability_tracker.md` §3a were implemented in
ONE round. The rows were derived PROGRAMMATICALLY (`h91_derive.py`), not
hand-typed.

  * 327 rows -> **311 entries / 327 database keys**. Rows sharing an ability
    name ride ONE entry (base + DLC/summoned twin keys) - the Foe-Seeker
    convention. Two entries whose naive key-derived marker collided needed a
    name-derived marker: **Horn of Vaul** (`dragonhorn` -> `horn_of_vaul`) and
    **Whip of Misery** (`whip_of_agony` -> `whip_of_misery`).
  * Zero rows were skipped as already present (the pre-edit idempotency check:
    none of the 327 keys was in the mod). Zero unmappable rows, zero unknown
    trigger codes.
  * THREE EXISTING evaluators (no new trigger types this round):
      `in-melee self`              274 rows / 261 entries -> `melee_unwavering`
      `health<=75 (no melee gate)`  37 rows /  36 entries -> `ushoran_health`
      `charge and in-melee`         16 rows /  14 entries -> `charge_or_melee`
  * The abilities table grows **262 -> 573 entries** (**272 -> 599 keys**):
    melee_unwavering 216 -> 477, ushoran_health 5 -> 41, charge_or_melee 15 -> 29.
  * A BULK DATA APPEND: no new trigger types, no new chunk-level locals (the
    chunk sits at Lua's 200-local ceiling) and no logic change.

## Files
  script/battle/mod/zz_test_deadly_onslaught.lua   (live)  sha256 7b9d2573e57e5e17cd8cffda5a04790c53588a5d62aa4140520c659d05c6a272
  WH3_auto_ability_annotated.lua                   (reading copy, log-free) sha256 bc9e0c81ae6e4a3bfbabaf6267c08972d68cc9cf51cedc8b1fb74b5779b59e67

## Build + install (RPFM WebSocket ws://127.0.0.1:45127)
  All 5 ship files MATCHES SOURCE: True (per-file sha256 gate).
  Independent PFH5 re-open of the installed pack: 5/5 IDENTICAL.
  installed md5 79571fd9a7ea6f4644c20bab9875b76b   (dist == installed, IDENTICAL True)

## Harness 91
  GREEN : 2571 checks, 0 failures   (baseline was harness90 2500/0; +71 new checks)
  RED   : 2539 checks, 73 failures   (baseline snapshot = pre-edit live+ann:
                                     pre91_live.lua / pre91_ann.lua = 262 entries / 272 keys)
  Every red failure is a DESIGNED grown-table pin, an aggregate that tallies a
  pin-dependent world result (A1-A4 6/8, B1-B6 10/12 - also failed in the
  harness-90 red run), or the new HARNESS-91 section (0o tokens + the O worlds)
  failing because the new abilities are simply absent on the snapshot. The
  harness-90 red-branch aggregate was re-based to the N/A form (the harness-91
  snapshot already carries blocks 7-9). No unexpected red-branch self-failures.
