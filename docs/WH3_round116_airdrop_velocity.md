# Round 116 — the air-drop wait is now MEASURED, not fixed: the enemy's own velocity

2026-10-18 · release `20261018_airdrop_velocity_harness116`
Installed pack md5 **`0c489c2438cf9acc98730bff1b0df52b`** (5 files, all byte-identical to source)
Round doc `docs/WH3_round116_airdrop_velocity.md` · spreadsheet `docs/WH3_abilities_master_v17_2026-10-18.xlsx`
Harness 116: **4,895 checks / 0 failures** (run twice, byte-identical) · red control **72 failures**

---

## 1. The user's ruling

> "The issue is that if the enemy unit is running away, then it is too soon. If the
> enemy moving is running towards, then it is too late. So to actually make it work,
> I think we do need relative velocity. But it must be calculated the moment the edge
> to edge distance is below our theshold. Then, if the unit is running towards the
> caster, then the delay would be 0. If running away, then the delay would be 2. If
> stationary or perpedicular, then should be 1. If something in between, we can make
> it dependant on the projection of the enemy velocity vector on the line that unites
> both the caster and the enemy unit. So the delay is dynamic in this way."

and, on implementation:

> "Okay, implement it. Also include logs to check the result of the function we use,
> like ordered_position(), just in case it isn't what we think it is."

Round 115's **fixed** 1-second dwell is therefore **replaced**. The dwell *machinery*
(the pair row, the poll clock, the short-crossing fallback, the purge, the pre-cast
re-check) is kept intact — only the **number it waits for** is now measured.

## 2. The rule that ships

```
candidate = alive and number_of_men_alive() > AIR_DROP_MIN_MEN (10)
valid     = its unit_distance() is readable
chosen    = the NEAREST valid candidate
UNDER     = unit_distance(caster, chosen) < AIR_DROP_EDGE_M (0.10 m)

axis  = normalise(caster.position() - enemy.position())        x/z only
v     = speed * normalise(ordered_position() - position())     the heading
proj  = dot(v, axis) / (speed * |axis|)                        the COSINE, clamped to ±1
delay = AIR_DROP_DWELL_MID_S - AIR_DROP_DWELL_SWING_S * proj   floored at 0

FIRE  = elapsed >= THIS PAIR's delay  (poll clock)
        OR a separation after AIR_DROP_MIN_CONTACT_S (0.3 s) of contact (fallback)
```

`axis` runs **from the enemy to the caster**, so a positive cosine means *closing on
the caster* — exactly the sign the user described.

### The constants

| Constant | Ships as | Meaning |
| --- | --- | --- |
| `FOURTH.AIR_DROP_DWELL_MID_S` (**new**) | `1.0` s | the delay at proj 0 (stationary / perpendicular) |
| `FOURTH.AIR_DROP_DWELL_SWING_S` (**new**) | `1.0` s | how far proj ±1 moves it |
| `FOURTH.AIR_DROP_MIN_CONTACT_S` | `0.3` s | the short-crossing floor (unchanged) |
| `AIR_DROP_EDGE_M` / `AIR_DROP_MIN_MEN` / `AIR_DROP_NEAR_M` / `AIR_DROP_FAST_S` | `0.1` / `10` / `30` / `0.2` | unchanged |
| ~~`FOURTH.AIR_DROP_DWELL_S`~~ | **removed** | the fixed dwell is gone; no reference survives (pinned) |

At the shipped pair: **closing → 0.0 s, stationary / across → 1.0 s, receding → 2.0 s**,
and every angle between interpolates linearly (`proj +0.71 → 0.29 s`, `proj -0.71 → 1.71 s`).
Nothing about the shape is a lookup table; it is the one subtraction.

### The velocity, and how each source resolves

The script API has **no velocity vector**. The velocity is rebuilt from the documented
reads only (`battle_unit.lua`), and every read is `pcall`ed and **fails closed** to a
zero velocity with a `src` that names why. The delay then falls back to the 1.0 s
baseline:

| `src` | What happened | delay |
| --- | --- | --- |
| `ordered` | a real heading: `speed * normalise(ordered - position)` | `1 - proj` |
| `stationary` | `is_moving()` answered **false** | 1.0 s |
| `moving-unreadable` | `is_moving()` raised | 1.0 s |
| `speed-unreadable` | `slow_speed()` / `fast_speed()` for the unit's state raised | 1.0 s |
| `speed-zero` | the speed read answered ≤ 0 while moving | 1.0 s |
| `pos-unreadable` | `position()` (or its x/z) could not be read | 1.0 s |
| `no-heading` | `ordered_position()` unreadable **or** the order point is < 0.5 m away | 1.0 s |
| `axis-degenerate` | the two centres are < 0.5 m apart in x/z — no axis to project on | 1.0 s |
| `axis-unreadable` | the **caster's** position could not be read | 1.0 s |

`no-heading` is the case the documentation predicts: *"if the unit is attacking, as
opposed to moving, then this will return the current position of the unit"*. A unit
whose `ordered_position()` equals its `position()` has no readable heading, so it takes
the **1.0 s baseline** — and the log says so on the line. **This is the first thing to
check in the field log** (§3, §8): if the enemy charging you reads `|h|=0.0
src=no-heading`, the heading source needs to change (a `current_target()` axis is the
obvious alternative); if it reads a real `|h|` and a real cosine, the formula is doing
what the user asked.

### Measured ONCE per contact

The delay is taken on the **first** evaluation of a contact — the one that stamps the
pair — and stored with the tick, the cosine and the source:
`FOURTH.ad_pair[caster][enemy] = { first = <tick>, delay = <s>, proj = <cos>, src = <src> }`.
It is **never re-measured inside that contact**, even if the enemy turns; a
**re-contact** after a separation starts a **fresh** measurement. The hold lines
re-print the **stored** `proj`/`delay` beside freshly-read positions, so "measured once"
is visible in the log as well as provable in the harness (world G).

### The delay lands on the poll grid

`tick_count` advances once per poll (`POLL_MS = 250 ms`), so the cast happens on the
first poll at or after the measured delay: a measured **0.29 s** waits **0.50 s**, a
measured **1.71 s** waits **1.75 s**, a measured **0.00 s** fires on the **next
evaluation**. The log prints the measured value; the grid is what the clock can
deliver. Quantisation can only delay a cast, never advance it.

## 3. The read-verification log — verbatim

**One line per contact episode**, written on the stamping evaluation:

```
[1003] death_from_above reads: moving=true is_moving_fast=false slow_speed=2.50 fast_speed=4.50 pos=(5.0,0.0) ordered=(-5.0,0.0) |h|=10.0 proj=+1.00 src=ordered delay=0.00s (measured once for this contact)
```

**One line per waiting tick**, with the reads re-taken (so `ordered_position()` is
observable *during* the contact) and the **stored** measurement repeated:

```
[1003] death_from_above reads(hold): moving=true is_moving_fast=false slow_speed=2.50 fast_speed=4.50 pos=(5.0,0.0) ordered=(5.0,3.0) |h|=3.0 proj=+0.00 src=ordered delay=1.00s held=0.25s
```

Field by field:

| field | source | notes |
| --- | --- | --- |
| `moving=` | `unit:is_moving()` | `true`/`false`, or `UNREADABLE` if the call raised |
| `is_moving_fast=` | `unit:is_moving_fast()` | names the API function so the two `fast` values cannot be confused |
| `slow_speed=` | `unit:slow_speed()` | `%.2f` m/s |
| `fast_speed=` | `unit:fast_speed()` | `%.2f` m/s |
| `pos=(x,z)` | `unit:position()` → `get_x()`, `get_z()` | `%.1f`, the horizontal plane only |
| `ordered=(x,z)` | `unit:ordered_position()` | `%.1f`; **if this equals `pos`, the heading is zero** |
| `\|h\|=` | `sqrt(dx²+dz²)` of `ordered - pos` | `%.1f`, or `UNREADABLE` when either read failed |
| `proj=` | the cosine actually used | `+0.00` for a perpendicular approach (never `-0.00`) |
| `src=` | which read produced the velocity | the table in §2 |
| `delay=` | the delay stored for this pair | `measured once` on the stamp line, `held=<t>` on a hold |

Every one of those fields prints `UNREADABLE` when its read fails — `pos=UNREADABLE`,
`ordered=UNREADABLE`, `|h|=UNREADABLE`, `slow_speed=UNREADABLE` — and the delay falls
back to 1.0 s with the matching `src`. Harness world I proves all three failures.

The transition lines from round 115 are unchanged in shape:
`dwell started: under at gap <d>m, waiting <t>s (pair '<key>')`,
`dwell: under <t>s of <t>s (gap <d>m)`,
`dwell satisfied after <t>s -> FIRING (gap <d>m, pair '<key>')`,
`dwell cancelled: separated after <t>s (gap <d>m; the dwell is <t>s and the short-crossing floor is 0.30s)`,
`short crossing: under for <t>s (>= 0.30s) -> FIRING on separation (gap <d>m, the delay measured was <t>s)`.
The pre-cast re-check prints `(dwell <under>s of <delay>s)` — now the **pair's own**
measured delay — or `(short crossing: held <under>s of 0.30s)`.

## 4. What is kept exactly

The candidate filter (> 10 alive models), the nearest-by-`unit_distance` pick,
`air_only` / `no_melee` per row, the self-centred cast on the **owner**, every
fail-closed read, the **0.2 s fast pass** (same evaluator, same `FOURTH.try_pair`
gate+cast path, adds evaluations and never time), `POLL_MS = 250`, every guard /
charge / in-flight / serialisation gate, the short-crossing fallback, the pair purge
with the unit, the re-verifying pre-cast re-check (models, gap **and** the measured
delay — it re-reads and SKIPS rather than spending the cast).

## 5. Harness 116 — the worlds

| world | proves | numbers |
| --- | --- | --- |
| A | **closing head-on** (`proj +1`) | delay **0.00 s**, fires on the next poll (0.25 s) |
| B | **perpendicular** (`proj 0`) | delay **1.00 s**, holds at 0.75 s, fires at 1.00 s |
| C | **receding** (`proj -1`) | delay **2.00 s**, still holds at 1.75 s, fires at 2.00 s |
| D | **45°** approach (`proj +0.71`) | delay **0.29 s**, holds at 0.25 s, fires at 0.50 s (the grid) |
| E | **135°** approach (`proj -0.71`) | delay **1.71 s**, holds at 1.50 s, fires at 1.75 s |
| F | **attacking** unit (`ordered == position`) | `\|h\|=0.0 src=no-heading`, delay **1.00 s** |
| G | **measure-once**: the enemy turns mid-contact | ONE measurement line; the holds keep `proj=+0.00 delay=1.00s` while the fresh reads change (`\|h\|=3.0`); fires at 1.00 s |
| H | **re-contact** measures again | two measurement lines, 1.00 s then **2.00 s**, fires on the second one's tick |
| I | **unreadable reads** | `slow_speed=UNREADABLE`/`speed-unreadable`, `pos=UNREADABLE`/`pos-unreadable`, `ordered=UNREADABLE`/`no-heading`, all at 1.00 s |
| J | short-crossing fallback + **gates** | 0.75 s contact that separates fires on the way out; 5 fast ticks + 2 polls cast nothing more |
| K | pre-cast re-check | gap drifts to 0.30 m at the firing poll → **SKIPPED**, `dwell=<t>s of <t>s` |

**Pins** (section 0, both files): both constants defined exactly once; the retired
`AIR_DROP_DWELL_S` appears nowhere; the formula line, the `dot/(speed*|axis|)` cosine
with its ±1 clamp and the enemy→caster axis verbatim; the 0.5 m heading floor and the
`no-heading` return; ≥ 6 `pcall`s in the velocity helper and the whole `src` vocabulary;
**`FOURTH.ad_dynamic_delay(` appears exactly twice — one definition, one call site**;
the pair row carries `delay/proj/src`; the fire test reads `ad_pair_need`;
the complete read-field list and both log formats; the re-check's `fired.delay` floor;
the fallback + `MIN_CONTACT_S`; the candidate filter / air-only / no-melee / self cast;
both timers and `POLL_MS = 250`; 689 entries / 12 air-drop; the tooltip sentence.

**Red control** (`H116_LIVE`/`H116_ANN` → `docs/backups/round116/pre116_*.lua`, the
round-115 build): **72 failures**, every one a section-0 pin or a world assertion that
depends on the measurement (A2–A6, B1, C1/C2/C4, D1/D3, E1/E2, F1, G1/G2, H3/H4,
I1a–I3b, J2). Nothing else in the 4,895-check suite moves.

## 6. Build and install

```
tools\rpfm\rpfm_server.exe            (WebSocket 127.0.0.1:45127)
build_and_install116.py               round 114 + 115 + 116 content gates: OK
installed pack md5 0c489c2438cf9acc98730bff1b0df52b
```

The five shipped files are byte-identical to source, verified twice — once inside the
build session (`GetPackedFileRawData` vs sha256 of the source) and once
**independently** by re-opening the installed pack (`verify_installed116.py`):

| file | bytes | md5 |
| --- | --- | --- |
| `script/battle/mod/zz_test_deadly_onslaught.lua` | 791,851 | `8e33f82450e1aee078b86e37957ea7cd` |
| `ui/templates/zz_auto_badge.twui.xml` | 2,864 | `2debc9b4af50b418e2a3a891deb4a0cc` |
| `ui/zz_auto/blank.png` | 69 | `5287946d1ac6397d46239b125dfc91b5` |
| `ui/zz_auto/auto_badge.png` | 252 | `86baa3055b39a3417a84cf162a2f54aa` |
| `ui/common ui/special_ability_tooltip.twui.xml` | 331,235 | `96944455c59d081459615e5ba63876fd` |

`zz_probe_dist.pack` is **left installed** and untouched (md5
`d4e67cfb8bc562c7d6f0ff742909c13d`).

## 7. Spreadsheet v17

`docs/WH3_abilities_master_v17_2026-10-18.xlsx` — v17 supersedes v16; **v1–v16
byte-unchanged**. All **19** air-drop rows carry the dynamic-delay rule in column 19
(summary) and column 22 (full evaluator text); Definitions gains **section 14** (the
two constants, the formula, the source table, the measured-once rule, the poll grid,
the two log formats and the read-verification block); Numbers is reconciled (689
entries / 742 keys, 12 air-drop entries / 19 keys — behaviour only, no count moved);
a **v17** Changelog row records it.

## 8. Retest plan — and what to send back

Arm the flyer, let an enemy block approach from **in front**, then let one **run away**,
then one **cross** the flight path. Then send back, from
`zz_test_deadly_onslaught_log.txt`:

1. **The `reads:` line of one contact you thought was too early.** It contains the
   enemy's `pos`, `ordered`, `|h|`, `proj`, `src` and the delay it got. If `pos` and
   `ordered` are the same point (`|h|=0.0`), the heading was unavailable and the drop
   waited the 1.0 s baseline — say so and the heading source changes next round.
2. **The `reads(hold):` line just before a `dwell satisfied` / `short crossing` line**
   when the timing felt wrong — it shows where the enemy really was at that moment.
3. **One `dwell cancelled:` line**, if any, with its `the dwell is <t>s` value.

One number per field test: `AIR_DROP_DWELL_MID_S` (the across value) and
`AIR_DROP_DWELL_SWING_S` (how hard the angle moves it) — no per-entry edits.

## 9. Files in the release

```
mod_source\releases\20261018_airdrop_velocity_harness116\
  round116_edit.py            the source edit (live + annotated, asserted anchors)
  h116_section.lua            the harness-116 section
  assemble116.py              harness115.lua + rebased pins + the new section
  harness116.lua              the runnable harness (1,079,078 bytes)
  h116_run1.txt / h116_run2.txt   the two green runs (byte-identical, 4,895 / 0)
  h116_red.txt                the red control (72 failures, all accounted for)
  make_builder116.py          the builder generator
  build_and_install116.py     the RPFM session + every round's content gates
  verify_installed116.py      the independent post-install check
  rpfm_server_out.txt         the build session's server log
```

Backups of the pre-116 sources: `docs\backups\round116\pre116_live.lua`,
`pre116_ann.lua`.
