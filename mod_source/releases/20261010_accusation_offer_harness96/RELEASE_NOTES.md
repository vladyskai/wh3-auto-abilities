# HARNESS 96 / THE ACCUSATION MOVE-ORDER ROOT CAUSE — release notes

## What was wrong (proven live)
The passive observer probe `zz_probe_dist` (its own pack, left installed) measures the
engine's reach read and both of the mod's candidate bounds side by side. At **tick 59** it
caught the bug:

```
CAND-FIRST tick=59 idx=1 type=orc_boyz dist=81.3m first_passing_test=engine mode=first engine_unit_in_range=t our_52_test=f our_75_test=f
```

The harness-95 build fixed the *magnitude* of Accusation's range (75 → 52 m) but its OFFER
test was still **`unit_in_range(enemy)` FIRST**, with `unit_distance <= 52` only as a
fallback. The engine's own reach read answered **TRUE at 81.3 m** while **BOTH** of the mod's
bounds said FALSE — `unit_in_range` reports the ability's *intercept/pursuit* reach, not a
cast range. The mod therefore offered (and cast at) a target 81.3 m away; the engine accepted
the cast and **WALKED the caster in** — the move order the user reported. The old log hid it:
a **static** `"within 52m"` label instead of the real distance.

## The fix
| | predicate |
|---|---|
| **BEFORE (shipped h95)** | `eg_enemy_in_range` = `(unit_in_range(enemy) == true) or (unit_distance(enemy) <= 52) or (caster in melee)` |
| **AFTER (h96)** | `eg_enemy_within_bound` = `unit_distance(enemy) <= FOURTH.ACCUSATION_RANGE_M` (52 m) — **the constant ONLY** |

* The engine's `unit:unit_in_range(enemy)` call is **REMOVED from the offer path entirely**.
* Untouched: in-melee preferred then closest; the in-melee OR under-missile-fire condition;
  the `bench_fresh` fresh-handle cast; the pre-cast re-check; the hold; cast target = the enemy.
* **Log fixed** so it cannot mislead again — the REAL computed distance to one decimal at BOTH
  the target choice and the pre-cast re-check (and the lapse-skip line), with the bound beside it:
  `accusation target: '<type>' is the chosen enemy (missile) distance=48.7m bound=52m`
* **Primitive stated in code:** `unit:unit_distance(other)` is **edge-to-edge (bounding-box
  aware)** per `battle_unit.lua:160` — so the number in the log IS exactly what the test used.

## The audit — every `unit_in_range` site
`grep unit_in_range` over the source found exactly **ONE** site:
`FOURTH.eg_enemy_in_range`'s `unit:unit_in_range(enemy)` read, used as the **Accusation
offer/range test** → **removed** (the function is replaced by `FOURTH.eg_enemy_within_bound`).
**No other range-bearing evaluator uses the engine helper** — charge, tired, melee,
melee_low_morale, in-melee-self, barrier, charge_or_melee, ushoran_health, glorious_death,
verminking, melee_health75, metallurgy, the blocks-7-9 triggers, blood_sacrifice and
eat_da_runts all already compare `unit_distance` against their own 70% constant.
`grep 'unit_in_range(' <source>` is now **EMPTY**.

## Base / revert
The shipped h95 source is the base: `pre96_live.lua` is byte-identical to it
(sha256 `ea48ca6dc6bf8e3657a179dfd869e7c876b4d2cf3dfb096f1821d957ba09b704`). The **unshipped
"contact range" attempt** (`releases/20261010_contact_range_harness96/`, applied to the source
but never harnessed, built or installed) was **reverted**; it is preserved here as
`pre96_POST96_attempt_{live,ann}.lua`.

## Harness 96
* **GREEN: 2902 checks / 0 failures** (live source AND annotated reading copy).
  * New **section 0t** (both files): the constant-only helper present, the gate wired,
    `unit_in_range(` and the old `eg_enemy_in_range` helper **GONE**, the real-distance log
    fragments present, the `unit:unit_distance` + `battle_unit.lua:160` citation present, the
    579-entry table and the 70% rule untouched; the annotated copy stays log-free / find-free.
  * **10 move-order worlds (5 × 2 files):** R1 the exact probe case (`in_range` TRUE, 81.3 m >
    52 m bound) → **SILENT**; R2 inside (48.7 m) → FIRES; R3 outside (70 m) → SILENT; R4 the
    log carries `distance=48.7m bound=52m` at both the choice and the re-check; R5 the engine
    flag FALSE but 40 m (inside) → the CONSTANT rules, FIRES.
* **RED: 2869 checks / 20 designed failures** against the pre96 snapshot (the shipped h95 build,
  whose offer test trusts `unit_in_range`): the 0t tokens (both files), **R1 firing** (both
  files — the regression), R4's LIVE log, and R5 (both files). R2/R3 + R4's annotated leg pass
  by design → 5/10 world results.
* **No regression:** the harness-95 suite re-runs **GREEN 2856 / 0** against the new source;
  its own boundary-count pin is re-based to the N/A form inside harness96.

## Build + install (RPFM WebSocket ws://127.0.0.1:45127, started then stopped)
```
All 5 ship files MATCHES SOURCE: True (per-file sha256 gate)
main mod byte-identical (untouched by the packer): True
built pack   md5 71ff20a3e71ca70fa4ac8d6d56672fb3
installed    md5 71ff20a3e71ca70fa4ac8d6d56672fb3   IDENTICAL True
```
Independently verified: the exact source bytes of all 5 ship files appear inside the installed
pack; the installed pack contains `distance=`, `m bound=`, `eg_enemy_within_bound` and
`battle_unit.lua:160` and contains **neither** `unit_in_range(` **nor** `") within "`.
Live source: sha256 `ffc6ed30a33d503ce07fa283c124e6b3791ed6e4b7c28dd285642a4e345564d9`, 418692 bytes.
Annotated copy: md5 `2543886ce50b0a84c2f02d973c0389de`.

## Roster
**579 entries / 605 keys — UNCHANGED before and after** (no ability entry added or removed;
only Accusation's offer predicate and log lines changed).

## Probe state
* `zz_probe_dist.pack` (the passive observer, `md5`-independent, 20063 bytes) is **LEFT INSTALLED**
  in the game's `data/` folder — it casts nothing and writes nothing, so it cannot interfere;
  the user will re-test with it.
* The step probe (`zz_probe_step.pack`) is **absent** from `data/`.
