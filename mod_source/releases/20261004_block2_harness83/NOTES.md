# Round: BLOCK 2 - the second in-melee-self batch (27) + the five new trigger types - 2026-10-04

## What shipped

### A. The 27 simple in-melee-self entries (block 2)
- The 27 approved entries, each on the SAME shared rule as the block-1 batch
  and blood_lust: trigger `melee_unwavering`, one shared evaluator
  `FOURTH.evaluate_in_melee_self(unit, routing)` (alive + in melee + not
  routing + not wavering, fail-open morale, self-cast). Every one carries its
  own marker, display name, badge id (`zz_auto_badge_<marker>`) and key list.
- **KEY CORRECTION (user):** the tracker listed
  `wh2_dlc11_lord_abilities_dreaded_duellist` with a DOUBLE l - that is a typo.
  The real database key is `wh2_dlc11_lord_abilities_dreaded_duelist` (single
  l). The single-l key is used; the build script asserts the double-l typo is
  absent from the shipped script.

### B. The five new trigger types (each its OWN evaluator + a DISTINCT reason)
1. **Eagle-Feather Torc** `wh3_dlc27_item_abilities_eagle_feather_torc`
   - trigger `barrier_broken`, evaluator `FOURTH.evaluate_barrier_broken`.
   - Fires when barrier HP is 0 with a NONZERO BarrierMaxHp, both read live via
     `common.get_context_value("CcoBattleUnit", <ui id>, <field>)` (the
     vanilla-proven read). Reason: `barrier broken (BarrierHp 0/120)`.
2. **Fangspike** `wh3_dlc26_weapon_abilities_fangspike`
   - trigger `charge_or_melee`, evaluator `FOURTH.evaluate_charge_or_melee`
     (reuses the onslaught charge detector; the arms cannot co-fire - the
     charge arm is tested first). Reasons: `charging (gap=..m dist=..m eta=..s)`
     and the DISTINCT `in melee (charge or melee)`.
3. **Summoned Foe-Seeker** `wh_main_character_abilities_foe_seeker_summoned`
   - NOT a new entry: the key was added to the EXISTING foe_seeker entry
     (third key), so the summoned caster shares that ability's marker
     (`foe_seeker`), badge (`zz_auto_badge_fs`), arming state and back-off.
     Reason: `tired or worse (fatigue: tired)` (the shared tired rule).
4. **Ghoul King of Ushoran** `wh2_dlc11_lord_abilities_ghoul_king_of_ushoran`
   - trigger `ushoran_health`, evaluator `FOURTH.evaluate_ushoran_health`.
   - Fires when the unit's OWN live HealthPercent <= 75%, WITH HYSTERESIS: once
     it fires it is re-armed only after climbing above 80% (`FOURTH.ushoran_high`),
     so a unit parked low does not re-cast every window. Reason:
     `health 72% (<= 75%)`.
5. **Glorious Death** `wh3_dlc25_lord_abilities_glorious_death`
   - trigger `glorious_death`, evaluator `FOURTH.evaluate_glorious_death`.
   - THE MOD'S FIRST ALLY-TARGETING ability: when in melee, prefer ANOTHER
     friendly unit in melee (not self) with the LOWEST HealthPercent; fall back
     to self only when there is no other in-melee ally. The chosen unit is left
     in `FOURTH.cast_target` (cleared before every evaluate) and the dispatch
     passes it to `perform_special_ability(key, target or unit)`. We cannot
     identify Slayer units from script, so ANY in-melee ally is offered and the
     engine refusal for non-Slayers is an ordinary rejection the existing
     back-off absorbs. Reasons: `ally in melee (priority)` / `self fallback
     (no other melee ally)`.

### C. Mechanics unchanged
- Still ONE `ability.evaluate(unit, routing)` dispatch (critique-2 item 8), the
  claim walk, the deferred badge creation/placement (any wheel slot 1..6), the
  M/A badge click (default M), the readiness gate, the 2 s guard, and the
  rejection-informed cooldown back-off. No new timers. **ZERO new chunk-level
  locals** (the file sits at Lua's 200-local ceiling): every new function and
  its two pieces of state (`context_value`, `ushoran_high`, `cast_target`) are
  FIELDS of the existing `FOURTH` helper bag.
- The annotated reading copy was updated in step (entries, the new evaluators,
  the dispatch, the cast, `context_value`) - it still reads correctly and stays
  log-/find-free.

## Harness (releases/20261004_block2_harness83/harness83.lua)
- GREEN: **1962 checks, 0 failures.** The WHOLE harness-82 suite (1861 checks,
  boundary-asserted: "checks so far = 1860") re-ran, plus the block-2 section
  (0y tokens + 14 worlds + aggregates).
- New worlds:
  * **S1**: all 27 block-2 simple keys fire on the in-melee condition ALONE
    (28 units; each badge claimed + armed; 27 fires; a 28th duplicate-marker
    unit that is NOT in melee stays silent; exactly 27 components).
  * **E1**: the torc fires ONLY for the broken barrier (BarrierHp 0, max 120);
    the intact-barrier and no-barrier owners stay silent.
  * **F1**: charging -> `charging`, in-melee -> `in melee (charge or melee)`,
    fast-and-in-melee takes the MELEE arm (no co-fire), idle silent.
  * **S2**: a unit owning ONLY the summoned key claims the foe_seeker marker,
    builds the SAME badge (`zz_auto_badge_fs`), and fires on the tired rule; the
    loaded table proves the key sits on the one foe_seeker entry.
  * **U1**: fires at 70% (`health 70% (<= 75%)`), does NOT re-fire while parked
    at 70% past the 2 s guard (hysteresis), re-arms after climbing to 90%, fires
    again on the next low read; an 80%-health owner never fires.
  * **G1**: THE ALLY-TARGET ASSERTION - the cast target is the LOWEST-health
    in-melee ally (NOT the caster, NOT the higher-health ally).
  * **G2**: no other in-melee ally -> the cast falls back to SELF.
- ADAPTED existing checks (forced by the grown table; everything else re-ran):
  0c `and not routing` 6 -> 7; A4a/A4b 33 -> 64 (66 -> 128 iters); B4a 33 -> 64;
  H68 table 33 -> 64, key map / array 38 -> 70; C6c wired 33 -> 64; and the
  harness-82 red branch re-labelled N/A (the pre-block-2 snapshot already
  carries block 1). The harness-82 suite boundary is asserted at 1860.
- RED CONTROL (harness83 with H83_LIVE / H83_ANN -> releases/20261004_pre_block2/):
  **1941 checks, 82 failures - ALL designed:**
  * 0y tokens 24 (no block-2 entries/evaluators/keys/reader/slot/reasons)
  * adapted count pins 15 (0c x2, A4 x4, B4 x2, H68 x5, C6c x2)
  * block-2 worlds 41 (S1/E1/F1/S2/U1/G1/G2 - no claim, no badge, no fire)
  * knock-on aggregates 2 (active-set 6/8, owned-list 10/12)
  * the two harness-83 red-branch checks (RED CONTROL 82 N/A + RED CONTROL 83
    new-claims/badges/fires = 0 and 0/14 worlds) PASS; every earlier suite
    behaves identically.

## Build + install
- Server: `WH3_mod/tools/rpfm/rpfm_server.exe` (127.0.0.1:45127).
- Build: `uv run --quiet --with websockets python build_and_install.py`
  (gained the ROUND v83 gates: the 27 markers/keys/badges, the 4 new-trigger
  entries, the summoned key, the 4 evaluators + map entries, the context
  reader, the ally-target dispatch, the hysteresis field, the four reason
  strings, the 56 `melee_unwavering` entries, and the typo guard).
- Pack md5: **bb6555259035f92591181c5a02436aee** (dist/ == installed).
- Independently verified (`verify_cleaned_independent.py`, raw PFH5 parse):
  exactly the 5 ship files, every file byte-identical to source, main mod
  sha256 **9125f191ee8f2e1a3d30af87ee790b7fa77615abb8c73c893eefd320dfdf145d**,
  installed pack sha256 67a76e66c8268c11680016625e9d784eb0c82e9bb2365cc88b82f546bd87006b,
  zero zz_probe_* fragments, RESULT: PASS.

## HOW TO FIELD-TEST
See `C:\Users\vlady\Desktop\WH3_mod\docs\WH3_test_plan_new_triggers.md` (the plain-language
plan: the five original abilities, the five new triggers, the 27 simple batch,
the negative checks, and how to arm badges).

## Files in this archive
- `harness83.lua`                 - the extended harness (green + red verified)
- `h83_green.txt`                 - the green run output (1962 checks / 0)
- `h83_red.txt`                   - the red-control run output (1941 / 82 designed)
- `zz_test_deadly_onslaught.lua`  - the main mod AS SHIPPED this round
- `WH3_auto_ability_annotated.lua`- the annotated reading copy, same round
- `zz_test_deadly_onslaught.pack` - the built+installed pack (md5 bb655525...)
- Pre-edit snapshot lives in `../20261004_pre_block2/`.
