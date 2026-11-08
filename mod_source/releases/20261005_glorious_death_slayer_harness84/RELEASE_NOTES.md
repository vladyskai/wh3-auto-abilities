# Release 2026-10-05 — Glorious Death (Slayer-only) + Ushoran hysteresis removal — harness84

Two corrections from the user's block-2 field test, plus the harness extension,
the build/install and the tracker status pass.

## Shipped source
`script/battle/mod/zz_test_deadly_onslaught.lua`  sha256 c775ca4e6d996ff1917c05ac6cc398db…
`WH3_auto_ability_annotated.lua` (Desktop reading copy)  sha256 ae7a471f453fe54aeb4aba9746bdfdae…
Pack installed to `.../Total War WARHAMMER III/data/zz_test_deadly_onslaught.pack`
installed md5 `7d2d40ab37fc88400155032fa5976d63` (dist == installed, IDENTICAL True);
per-file sha256 gate: all 5 shipped files MATCHES SOURCE True.

## Correction 1 — GLORIOUS DEATH is SLAYER-ONLY
* The candidate set is SLAYER UNITS ONLY (the earlier "any friendly unit in reach"
  wording was wrong).
* (a) an in-melee **Slayer ally** (other than self, lowest health) is preferred;
  (b) else the **owner itself** self-casts ONLY when the owner is a Slayer AND in melee;
  (c) else **silent**.
* A **non-Slayer ally is never targeted** — the old any-in-melee-ally fallback is REMOVED.
* Who is a Slayer = `FOURTH.slayer_keys`, a list of **land_units type keys DERIVED FROM
  THE GAME'S OWN DATA**: `%LOCALAPPDATA%\Temp\wh3\land_units.loc.tsv`, every
  `land_units_onscreen_name_<key>` row whose own key contains `slayer`/`doomseeker`,
  copied verbatim (10 keys: `wh_main_dwf_inf_slayers`, `wh2_dlc10_dwf_inf_giant_slayers`,
  `wh3_dlc25_dwf_cha_daemon_slayer`, `wh3_dlc25_dwf_cha_dragon_slayer`,
  `wh3_dlc25_dwf_inf_slayer_pirates`, `wh3_dlc25_dwf_inf_slayer_pirates_ror`,
  `wh3_dlc25_dwf_inf_slayers_grudge_unit`, `wh_dlc06_dwf_inf_dragonback_slayers_0`,
  `wh3_dlc25_dwf_inf_doomseekers`, `wh3_dlc25_dwf_inf_doomseekers_ror`).
* Membership is `FOURTH.slayer_keys[t] == true` — **EXACT WHOLE-KEY equality, one table
  read; `string.find` stays banned** (the near-miss Bretonnian ROR "Beastslayers of
  Bastonne" key carries no `slayer` and is correctly NOT a Slayer; a Slayer whose key does
  not spell it, e.g. Gotrek, is a documented under-approximation).
* Fallback choice: the old **non-Slayer fallback is removed** (the user's correction), so
  the only self case is a Slayer owner in melee. Reason strings: `slayer ally in melee
  (priority)` / `self slayer fallback (in melee)`.
* Not using `string.find` means `wh3_dlc25_dwf_inf_doomseekers` etc. are matched only when
  the engine's `type()` key equals the whole listed key.

## Correction 2 — GHOUL KING OF USHORAN hysteresis removed
* Plain rule: fire when own health <= 75%. The 80%-re-arm hysteresis (which could disarm
  the trigger for good under sustained damage) is REMOVED; `FOURTH.ushoran_high` is gone.
* Repeat attempts are limited by the EXISTING readiness gate
  (`can_perform_special_ability`), the ability's own engine cooldown, and the
  rejection-informed back-off — never a second health threshold.

## Harness 84
Built from harness83 (env pair now `H84_LIVE` / `H84_ANN`). New section: `W0` (direct
`FOURTH.is_slayer` membership), `W1` (owner not in melee + in-melee Slayer ally -> ally),
`W2` (Slayer owner in melee + no Slayer ally -> self; non-Slayer never targeted), `W3`
(silent), `W4` (membership beats health: Slayer ally at 90% beats non-Slayer at 20%), `W5`
(non-Slayer owner + non-Slayer ally -> silent), plus section-0z static gates.
Rewritten in the harness-83 suite for the corrections: `U1` (no hysteresis: re-fire at a
parked 60% + the readiness gate limits), `G1` (Slayer-only targeting), `G2` (Slayer self
fallback). Adapted pins: section 0c `and not routing` 7 -> 6 (the trigger change),
section 0y reasons reworded, section 0y `ushoran_high` -> "hysteresis field GONE".

GREEN:  **checks: 2039, failures: 0**  (the whole harness-83 suite re-ran unchanged, count
pin `checks == 1961` at its boundary; +77 new checks).
RED (pre-edit snapshot, this dir's `pre84_snapshot/`): **failures: 66**, every one a
designed delta of this round — section-0z (21), W0-W5 (30), the adapted pins (0c x2,
0y reasons x1, 0y hysteresis-gone x2), the rewritten U1/G1/G2 (11), and their live-only
reason checks; the harness-83/harness-82 red aggregates and W3 (shared-silent) pass by
design. No unrelated check fails.

## Tracker
`C:\Users\vlady\Desktop\WH3_mod\docs\WH3_ability_tracker.md` — two header notes + two legend entries;
the 27 block-2 simple entries -> `pending test (not yet field-tested)`; **Eagle-Feather
Torc** and **Fangspike** -> `pending test (DLC unavailable)` (item-gated); summoned
**Foe-Seeker** and **Ghoul King of Ushoran** -> `pending test (not yet field-tested)`;
**Glorious Death** -> field-tested (DLC25), rule corrected. Nothing was marked
unimplemented.
