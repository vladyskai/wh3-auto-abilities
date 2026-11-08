# Round 114 — the air-drop rule is one comparison, plus a 0.2 s fast pass

2026-10-18 · release `20261018_airdrop_edgesimple_harness114`
Installed pack md5 **`2cec3140e4d0838fa678187621ea55b0`** (5 files, all byte-identical to source)

---

## 1. What changed

### 1.1 The rule

```
candidate = number_of_men_alive() > 0 AND number_of_men_alive() > AIR_DROP_MIN_MEN (10)
valid     = that candidate's battle_unit:unit_distance(caster, enemy) is READABLE
chosen    = the NEAREST valid candidate by that distance
FIRE      = unit_distance(caster, chosen) < AIR_DROP_EDGE_M (0.10 m)
```

Then the row's own caster-side checks (`air_only` → `is_currently_flying()` exactly true, `no_melee` →
`is_in_melee()` not true), the self-centred cast on the OWNER, and the pre-cast re-check.

### 1.2 Deleted from the evaluator (and why nothing else broke)

The infantry filter, the `initial_number_of_men() == 1` exclusion, the four projection dials,
`AIR_DROP_INHERIT`, `AIR_DROP_CENTER_M`, the derived frontage (radius / ranks / min / max) and the path
segment test — with the helpers that served them: `ad_frontage`, `ad_frontage_text`, `ad_seg_dist`,
`ad_velocity`, `ad_lead`, `ad_project`, `ad_dial_text`, `ad_single_say`, `ad_single_clear`,
`ad_centre_gap`, `ad_pos`, `ad_sep`, `ad_vec_text`.

**Every caller of every one of those helpers was inside this evaluator or its pre-cast re-check**, so they
were deleted rather than left dead. `enemy_is_infantry` itself stays in service (3 call sites remain:
`enemy_ground_melee_infantry`, the `melee_skip_commanders` engagement set, and the `enemy_ground_*`
pre-cast re-check).

### 1.3 New constants

```lua
FOURTH.AIR_DROP_EDGE_M  = 0.1   -- fire below this edge-to-edge gap
FOURTH.AIR_DROP_MIN_MEN = 10    -- a candidate needs MORE alive models than this
FOURTH.AIR_DROP_NEAR_M  = 30    -- the fast pass runs while a valid enemy is this close
FOURTH.AIR_DROP_FAST_S  = 0.2   -- the fast pass interval (registered as 200 ms)
```

### 1.4 The fast pass, and the one-copy cast path

`FOURTH.try_pair(script_unit, unit, ability, ui_id, ability_key, reason, gone_ids)` is the poll's
readiness + cooldown-hold + guard + charge + in-flight + per-unit-serialisation + cast block,
**extracted verbatim** (it now answers `"gone"` instead of breaking). The poll calls it; the new
`FOURTH.ad_fast_pass` calls it too — so the gates exist in exactly one place.

The fast pass: a **second model timer** at `AIR_DROP_FAST_S`, its own `pcall`, iterating only
`FOURTH.ad_fast_abilities` (the 12 air-drop entries), only for alive + armed units, only while a valid
enemy is inside `AIR_DROP_NEAR_M`, running the **same** `FOURTH.ad_pick`.

Isolation proof (harness world J): with a NON-air-drop ability armed and an enemy at 0.00 m, five fast
ticks produce no fire and no air-drop line. Double-cast proof (world H): two consecutive fast ticks → one
cast; five more → still one; the next poll → still one (the guard is stamped in poll ticks **before** the
call).

### 1.5 Kept exactly

`POLL_MS = 250` and the global poll's registration, every other ability's cadence and evaluator, the
readiness gate, the charge / in-flight / serialisation holds, `air_only` / `no_melee`, the self-centred
cast, fail-closed reads, and the pre-cast re-check (now: still alive, still > 10 models, edge gap
re-measured on fresh handles). Counts: **689 entries / 742 keys**, `air_drop_on_infantry` **12 / 19**,
46 evaluators — unchanged.

## 2. The log

```
[1003] sky_junk_bomb nearest valid:'wh3_main_inf_zombie_0' entities=20 edge=0.04m (need < 0.10m) -> FIRING
[1003] sky_junk_bomb nearest valid:'wh3_main_inf_zombie_0' entities=20 edge=0.11m (need < 0.10m) -> NOT YET
[1003] sky_junk_bomb nearest valid:'<key>' entities=12 edge=0.20m (need < 0.10m) -> SKIPPED at re-check (...)
[1003] fast poll: ON (nearest valid 12.3m)   /   [1003] fast poll: OFF
```

Identical repeated decisions are de-duplicated (the fast pass runs 5×/s); the `fast poll:` transition is
written once per change.

## 3. Files

| File | Note |
| --- | --- |
| `round114_edit.py` | the whole source edit, applied to BOTH copies (exact-count anchors) |
| `block_live.lua` / `block_ann.lua` | the new evaluator block, live (with logs) and annotated (log-free) |
| `h114_section.lua` + `assemble114.py` + `post114.py` → `harness114.lua` | the suite: the harness-112 base (4,492 checks) + the round-114 section, carrying the documented supersessions |
| `make_builder114.py` → `build_and_install114.py` | the pack builder; 159 stale content asserts from the replaced design are gated behind `ROUND114 = True` and a new ROUND 114 gate block asserts the shipped state |
| `build_diag114.py` | the diagnostic that enumerated every stale assert (67) in one run |
| `verify_installed114.py` | independent post-install check: opens the **installed** pack and compares all five files |
| `run1.txt` / `run2.txt` | two green runs (4,614 checks), byte-identical |
| `red114.txt` | the red control (round-113 build): 56 failures, all in the new section |

## 4. Harness 114

* **4,614 checks / 0 failures**, twice, byte-identical.
* Worlds: A0 0.09 m fires · A1 0.11 m silent · B10 10 models excluded at 0.00 m · B11 11 models fires ·
  C 20-model cavalry fires (no infantry test) · D one-model lord excluded · E nearest-of-two ·
  F re-check skip at 0.20 m · G fast-poll ON at 20 m / OFF at 40 m, one line each · H two fast ticks →
  one cast · I unreadable distance fails closed · J the fast pass never runs a non-air-drop ability.
* Section-0 pins in both copies: the four new constants once each; the ten retired constants and
  thirteen retired helpers absent; `FOURTH.try_pair` defined once and called twice; `POLL_MS = 250` once;
  the 0.2 s registration; 12 entries / 689 markers; the new tooltip sentence.
* **Red control**: 56 failures, every one in the new section, none before it.
* **Supersessions** (nothing deleted, counts preserved): rounds 108-112's air-drop-only sections answer
  N/A in their existing slots (66 / 99 / 149 / 134 / 105); round 107's `0y` pins and A1-A10 worlds answer
  N/A through a renamed check call, while its S1/S2/S3 serialisation worlds still run for real with a
  20-model enemy at a 0.05 m gap. Three structural pins were rebased: the timer count (2 model timers),
  `unit_is_routing(unit)` (3 sites), and the `gone`-break pin (collect in `try_pair`, break in the caller).

## 5. Build and install

```
source script/... 766,246 bytes  md5 a503fff0e7c978724036481aacb643e7
five files        all MATCHES SOURCE: True
built pack        md5 2cec3140e4d0838fa678187621ea55b0
installed         md5 2cec3140e4d0838fa678187621ea55b0   IDENTICAL True
round-trip (re-opened the INSTALLED pack): all five files byte-identical
zz_probe_dist.pack left installed (md5 d4e67cfb8bc562c7d6f0ff742909c13d, untouched)
```

## 6. Retest plan

1. Hover an air-drop carrier over a **20-model** block and watch `edge=` fall under `0.10m` — the drop
   should leave at that moment.
2. Confirm the `fast poll:` ON/OFF pair appears once each, at 30 m.
3. Still early → `AIR_DROP_EDGE_M` 0.1 → 0.05. Never fires under a block → 0.1 → 0.2 → 0.3. One constant
   per test.
4. A Lord walked past must produce NO decision line (it fails the > 10 test).
5. The global poll is 250 ms, so 0.2 s is only marginally faster today; `AIR_DROP_FAST_S` 0.2 → 0.1 is
   the next step if the field wants more, and it still cannot cast twice.
