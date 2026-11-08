# Round 110 — the air drop is PREDICTED, not sampled (two-body relative motion)

Date: 2026-10-18 · Harness 110 · Installed pack md5 `588e6c3c6781d02321ce7b31af04884f`

The user's third field report: firing on **Drop Rocks** (Terradon Riders, `wh2_main_unit_abilities_drop_rocks`)
is still **early or misses**. The rocks take about 1-2 s to come down and the flier keeps moving,
so the enemy that was under the caster when the button was pressed is not under the rocks when they
land.

One behaviour change ships. No counts change: **689 entries / 742 keys**, `air_drop_on_infantry`
**12 entries / 19 keys**, 46 evaluators.

---

## 1. The assumption, and the rule it produces

The user's ruling, verbatim: *"I think the rocks don't keep the momentum, so let's work with that
assumption. Let's implement it and I'll test it."*

So the ordnance **does not inherit the caster's velocity**: it is released and falls **straight
down** from the point the caster occupies **at release**. The button therefore has to predict
**both** bodies:

```
caster(t+d) = caster(t) + v_caster * d        <- the IMPACT point
enemy (t+d) = enemy (t) + v_enemy  * d
```

and the drop fires when the **PROJECTED horizontal centre separation** is inside the **same**
`FOURTH.AIR_DROP_CENTER_M = 6 m`.

What this changes, and what it does not:

| situation | round 109 (instant) | round 110 (projected) |
| --- | --- | --- |
| both stationary | fires at ≤ 6 m | identical (projected = current) |
| caster closing on the target | fires at ≤ 6 m current | fires **earlier in time**, at a larger current distance (the gap closes during the fall) |
| caster receding | fires at ≤ 6 m current | fires later, or never |
| enemy closing / receding | judged where it was | judged where it will be (both directions proven in the harness) |
| both moving the same way at the same speed | n/a | projected separation **equals** the current one — the shared velocity cancels exactly |
| a target crossing the flight path | judged on its current point | judged on its **projected point** |

## 2. Constants

| constant | value | meaning |
| --- | --- | --- |
| `FOURTH.AIR_DROP_CENTER_M` | **6** | the bound, unchanged since round 109 (centre-to-centre, X/Z) |
| `FOURTH.AIR_DROP_DELAY_S` | **1.5** (new) | the fall time the prediction projects over — a **TUNABLE CONSTANT**, between the 1 s and 2 s the user observed. **No ability row carries a fall time**, so nothing in the game data can be quoted for it |
| `FOURTH.AIR_DROP_INHERIT` | **false** (new) | **THE ONE FLAG**: `true` adds `v*d` to the impact point a **second** time (`impact = caster + v*d*2`) if the field shows the rocks DO keep the momentum |

## 3. The velocity source, and its limits

The script API has **no velocity vector and no position history**. Velocity is **rebuilt** as
`speed * normalise(ordered_position() - position())` from the reads the dump actually documents:

* `battle_unit:is_moving()` — *"whether the unit is currently moving"*
* `battle_unit:is_moving_fast()` — *"whether the unit is moving fast (running/charging)"*
* `battle_unit:slow_speed()` / `fast_speed()` — *"the unit's slow/walking ... fast/running movement
  speed in m/s"*
* `battle_unit:ordered_position()` — *"the position to which the unit has been ordered to move to"*
* `battle_unit:bearing()` — *"the current orientation of the main squad of the unit in degrees"*

Limits, all stated in the code comment at the constants:

1. the speed is a **scalar** — a unit that is turning, braking into a charge or being pushed is
   mis-estimated;
2. `ordered_position()` answers the **current** position for a unit that is **attacking**, so an
   attacker has **no ordered heading**;
3. an ordered point under **0.5 m** away carries no direction and is treated as no heading;
4. `bearing()` is the **documented fallback for the CASTER ONLY**, and only while it is moving —
   the dump never says how its degrees map onto x/z, so the `sin/cos` mapping is the one unverified
   step, and it is never used to invent motion for an enemy;
5. `is_moving()` not exactly `true` → **ZERO** velocity, source `stationary`. An unreadable read →
   ZERO, `moving-unreadable`. No speed → ZERO, `no-speed`. No usable heading → ZERO, `no-heading`
   (the speed is still printed). **Motion is never invented**, and a unit whose velocity cannot be
   read is simply treated as stationary — i.e. round-109 behaviour.

## 4. The log, per decision

Target line (fired):

```
  drop_rocks target: 'wh2_main_lzd_inf_skink_skirmishers_0' is UNDER the caster (PROJECTED 1.50s AHEAD
  momentum=none caster=(100.0, 200.0) v=(8.0, 0.0) 8.0 m/s src=ordered proj=(112.0, 200.0)
  enemy=(112.0, 200.0) v=(0.0, 0.0) 0.0 m/s src=stationary proj=(112.0, 200.0)
  centre=0.0m (the PROJECTED separation, which is what decides) now=12.0m now_dxz=12.0m bound=6m
  edge=0.0m radius=none (constant stands in) air_only=true)
```

Watch line (did not fire; nearest infantry by **projected** separation, 5 m bands, only inside 30 m):

```
  drop_rocks watch: nearest INFANTRY 'wh2_main_lzd_inf_skink_skirmishers_0' is centre=~5m vs bound=6m
  -> NOT under the caster [projected sep=~15m after delay=1.50s; caster v=(-8.0, 0.0) 8.0 m/s
  src=ordered; enemy v=(0.0, 0.0) 0.0 m/s src=stationary]
```

Pre-cast re-check (re-projected from **fresh** reads just before the call) prints
`projected centre=… now=… delay=1.50s bound=6m` and either `- firing` or
`SKIPPED: the drop lapsed before the cast … - cast not spent`.

**What to look for in the field log:** `src=` on both bodies, `proj=` on both bodies, `centre=` (the
projected number that decided) vs `now=` (the instant one).

## 5. Harness 110

* **Green: 4253 checks, 0 failures**, run twice with byte-identical output (`h110_run1.txt` =
  `h110_run2.txt`), against the LIVE source AND the annotated copy.
* **Red control** (`H110_LIVE`/`H110_ANN` → `docs/backups/round110/pre110_*.lua`, the round-109
  build): **65 failures, ALL in the new section** — 31 static tokens (the delay, the flag, the six
  reads, the fail-closed sources, the 0.5 m gate, the caster-only bearing fallback, the projection,
  the picker's projected gate, the re-check, the assumption/flag documentation) and 34 world
  checks. Worlds that pass there **by design**: A1 (a stationary 5.5 m pair fires either way),
  E1 (4 m same-velocity), F1 (a crossing judged 7 m off), D2 (25 m closing), H1a (drift), G1a/G2a/
  G3a and I1a.
* Worlds (each run on the live build and the annotated copy; pins **bound = 6 m, delay = 1.5 s**):
  * **A1/A2** both stationary — 5.5 m FIRES (projected = now), 6.5 m silent.
  * **B1** caster closing at 8 m/s, enemy 12 m ahead → projected 0 m → **FIRES** (round 109 could
    not: 12 m > 6 m).
  * **B2** caster receding at 8 m/s, enemy 5 m away (round 109 fired here) → projected 17 m →
    **SILENT**.
  * **C1** enemy closing 10 → 4 m → **FIRES** though its current point is outside the bound.
  * **C2** enemy receding 5 → 11 m → **SILENT** though its current point is inside it.
  * **D1** both closing (8 + 4 m/s), 20 m apart → projected 2 m → **FIRES**.
  * **D2** the same pair 25 m apart → projected 7 m → **SILENT** (the pin).
  * **E1/E2** same direction, same speed → projected == current (4 m fires, 7 m silent).
  * **F1/F2** a target crossing the flight path 7 m / 5 m to the side → silent / fires.
  * **G1** `is_moving()` unreadable → ZERO, `moving-unreadable`, 12 m stays silent.
  * **G2** the same unreadable caster at 5 m → fires (treated as stationary), source printed.
  * **G3** moving with a degenerate ordered point and no bearing → `no-heading`, silent.
  * **G4** the caster-only bearing fallback (bearing 90, slow 4 m/s) → v = (4.0, 0.0), projected
    6 m from 12 m → **FIRES**, `src=bearing`.
  * **H** drift during the delay: chosen at 5 m, 30 m at the re-check → **SKIPPED**, cast not spent.
  * **I1/I2** THE ONE FLAG: the same source with `FOURTH.AIR_DROP_INHERIT = true` (the documented
    variant `harness110_inherit_on.lua`) moves the impact point from 112 m to **124 m**, so an enemy
    24 m ahead is silent with the shipped flag and **fires** with the flag flipped.

## 6. Files

* source `mod_source/script/battle/mod/zz_test_deadly_onslaught.lua` — 776,965 bytes, md5
  `997fb8bd56eba6801f04653164cc3b12`
* pack `mod_source/dist/zz_test_deadly_onslaught.pack` — md5 `588e6c3c6781d02321ce7b31af04884f`
  (**dist == installed**; all **5 ship files byte-identical to source**, verified inside the pack)
* annotated reading copy `docs/WH3_auto_ability_annotated.lua` (logic mirrored, log lines replaced
  by comments — the harness proves it has no `log(` call)
* spreadsheet `docs/WH3_abilities_master_v11_2026-10-18.xlsx` (+ `.ods`) — v11 supersedes v10,
  **v1-v10 byte-unchanged**
* tracker `docs/WH3_ability_tracker.md` — 19 rows + the glossary row + a dated update
* round doc `docs/WH3_round110_airdrop_relative.md`
* `zz_probe_dist.pack` LEFT INSTALLED (untouched, md5 `d4e67cfb8bc562c7d6f0ff742909c13d`)

## 7. How to re-test

Fly the Terradons over an infantry unit and watch the log as the button fires:

* **If the rocks still land AHEAD of the target** → raise `FOURTH.AIR_DROP_DELAY_S` (1.5 → 2.0).
* **If they land BEHIND** → lower it (1.5 → 1.0).
* **If the fire is late but the log's `proj=` for both bodies looks right** → the delay is too long.
* **If the rocks land ahead and the log's `caster v=` is large and `src=ordered`** → the momentum
  assumption is wrong: flip `FOURTH.AIR_DROP_INHERIT = true` and NOTHING else.
* **If `src=` never reads `ordered`** (always `no-heading` / `stationary` while the flier is clearly
  moving) → send the log; the fallback chain needs a different read.
* **If it never fires at all** → send the `watch:` lines: they carry the projected separation and
  both velocities, which is enough to see whether the bound or the delay is at fault.
