# Round 116 — the air-drop wait is measured, not fixed: the enemy's own velocity

2026-10-18 · release `20261018_airdrop_velocity_harness116`
Installed pack md5 **`0c489c2438cf9acc98730bff1b0df52b`** (5 files, all byte-identical to source)
Round doc `docs/WH3_round116_airdrop_velocity.md` · spreadsheet `docs/WH3_abilities_master_v17_2026-10-18.xlsx`

---

## 1. The ruling

> "if the enemy unit is running away, then it is too soon. If the enemy moving is running
> towards, then it is too late. … But it must be calculated the moment the edge to edge
> distance is below our theshold. Then, if the unit is running towards the caster, then
> the delay would be 0. If running away, then the delay would be 2. If stationary or
> perpedicular, then should be 1. … the delay is dynamic in this way."

> "Okay, implement it. Also include logs to check the result of the function we use, like
> ordered_position(), just in case it isn't what we think it is."

Round 115's **fixed** 1-second dwell is replaced. The dwell *machinery* — the pair row,
the poll clock, the short-crossing fallback, the purge, the re-verifying pre-cast
re-check — is kept; only the **number** is now measured.

## 2. The rule

```
candidate = alive and number_of_men_alive() > AIR_DROP_MIN_MEN (10)
valid     = its unit_distance() is readable
chosen    = the NEAREST valid candidate
UNDER     = unit_distance(caster, chosen) < AIR_DROP_EDGE_M (0.10 m)

axis  = normalise(caster.position() - enemy.position())      x/z only
v     = speed * normalise(ordered_position() - position())
proj  = dot(v, axis) / (speed * |axis|)                      the COSINE, clamped to ±1
delay = AIR_DROP_DWELL_MID_S - AIR_DROP_DWELL_SWING_S * proj, floored at 0

FIRE  = elapsed >= THIS PAIR's delay (poll clock)
        OR a separation after AIR_DROP_MIN_CONTACT_S (0.3 s) — the short-crossing fallback
```

### Constants

| Constant | Ships as |
| --- | --- |
| `FOURTH.AIR_DROP_DWELL_MID_S` (**new**) | `1.0` s — the delay at proj 0 |
| `FOURTH.AIR_DROP_DWELL_SWING_S` (**new**) | `1.0` s — how far proj ±1 moves it |
| `FOURTH.AIR_DROP_MIN_CONTACT_S` | `0.3` s (unchanged) |
| `AIR_DROP_EDGE_M` / `AIR_DROP_MIN_MEN` / `AIR_DROP_NEAR_M` / `AIR_DROP_FAST_S` | `0.1` / `10` / `30` / `0.2` (unchanged) |
| ~~`FOURTH.AIR_DROP_DWELL_S`~~ | **removed** — no reference survives (pinned in the harness and the builder) |

**0 s closing · 1 s stationary/perpendicular · 2 s receding**, interpolated: `proj +0.71 →
0.29 s`, `proj -0.71 → 1.71 s`.

## 3. Measured once

`FOURTH.ad_pair[caster][enemy] = { first = <poll tick>, delay = <s>, proj = <cos>, src = <src> }`,
taken on the **first** evaluation of a contact — the one that stamps the pair and never
casts — and **never re-measured inside that contact**, even if the enemy turns (world G).
A **re-contact** measures again (world H).

The delay lands on the **250 ms poll grid** (`tick_count`): 0.29 s → fires at 0.50 s,
1.71 s → at 1.75 s, 0.00 s → on the next evaluation. Quantisation can only delay a cast.

## 4. The read-verification log

One line per contact episode:

```
[1003] death_from_above reads: moving=true is_moving_fast=false slow_speed=2.50 fast_speed=4.50 pos=(5.0,0.0) ordered=(-5.0,0.0) |h|=10.0 proj=+1.00 src=ordered delay=0.00s (measured once for this contact)
```

One per waiting tick (reads re-taken, stored measurement repeated):

```
[1003] death_from_above reads(hold): moving=true is_moving_fast=false slow_speed=2.50 fast_speed=4.50 pos=(5.0,0.0) ordered=(5.0,3.0) |h|=3.0 proj=+0.00 src=ordered delay=1.00s held=0.25s
```

`UNREADABLE` in any field whose `pcall` failed. If `ordered_position()` answers the
current position (the documented "attacking" case) the line shows `pos == ordered`,
`|h|=0.0`, `src=no-heading` — visible, not assumed. That is the **first thing to check** in
the returned log.

## 5. Sources — every read fails closed

| `src` | delay |
| --- | --- |
| `ordered` | `MID - SWING*proj` |
| `stationary` (`is_moving()` false) | 1.0 s |
| `moving-unreadable` / `speed-unreadable` / `speed-zero` | 1.0 s |
| `pos-unreadable` / `no-heading` (order point < 0.5 m or unreadable) | 1.0 s |
| `axis-degenerate` (centres < 0.5 m apart) / `axis-unreadable` | 1.0 s |

## 6. Harness 116 — 4,895 checks / 0 failures (twice, byte-identical)

| world | proves | numbers |
| --- | --- | --- |
| A | closing head-on (proj +1) | delay 0.00 s, fires next poll |
| B | perpendicular (proj 0) | delay 1.00 s |
| C | receding (proj -1) | delay 2.00 s, holds at 1.75 s |
| D | 45° (proj +0.71) | delay 0.29 s, fires at 0.50 s |
| E | 135° (proj -0.71) | delay 1.71 s, fires at 1.75 s |
| F | attacking (`ordered == position`) | `\|h\|=0.0 src=no-heading`, 1.00 s |
| G | measure-once across a turn | one measurement; stored proj/delay on every hold |
| H | re-contact | two measurements, 1.00 s then 2.00 s |
| I | unreadable speed / position / ordered | `UNREADABLE` verbatim, 1.00 s + reason |
| J | fallback + gates | 0.75 s contact fires on the way out; 5 fast ticks cast nothing |
| K | pre-cast re-check | gap drifted → SKIPPED, `dwell=<t>s of <t>s` |

Red control (`docs/backups/round116/pre116_*.lua`, the round-115 build): **72 failures**, all
section-0 pins and world assertions that depend on the measurement.

## 7. Build

```
tools\rpfm\rpfm_server.exe   → WebSocket 127.0.0.1:45127
build_and_install116.py      → round 114 + 115 + 116 content gates: OK
installed pack md5 0c489c2438cf9acc98730bff1b0df52b
```

Five files byte-identical to source, verified twice (build session + independent reopen of
the installed pack). `zz_probe_dist.pack` left installed (md5 `d4e67cfb8bc562c7d6f0ff742909c13d`).

## 8. Retest

Arm a flyer; let a block charge **in**, then let one **run away**, then one **cross**.
Send back the `reads:` line of a contact that felt **too early** (and the `reads(hold):`
line before any `dwell satisfied` / `short crossing`). One knob per test:
`AIR_DROP_DWELL_SWING_S` for the angle, `AIR_DROP_DWELL_MID_S` for every angle at once.
