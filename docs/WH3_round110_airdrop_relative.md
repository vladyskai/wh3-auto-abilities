# Round 110 — two-body relative-motion prediction for the air-drop family

2026-10-18 · harness 110 · pack md5 `588e6c3c6781d02321ce7b31af04884f`

## 1. The problem, stated as arithmetic

Round 109 fired when the **instant** horizontal centre separation was ≤ 6 m. The ordnance,
however, is not at the target when the button is pressed: it appears at the caster's position and
takes a fall time `d` to arrive. In `d` seconds the caster moves `v_c·d` and the enemy moves `v_e·d`.
For the round-109 test to be right by luck, `v_c + v_e` would have to be zero.

The user's report says it is not: the rocks land **ahead** of the target on a closing pass.

## 2. The assumption that fixes the frame

The user's ruling: *"I think the rocks don't keep the momentum, so let's work with that
assumption."* — the ordnance does **not** inherit the caster's velocity. It is released and falls
**straight down** from the release point. Therefore

```
impact = caster(t_release)                (no v·t term for the ordnance itself)
```

and the button press must predict **where the caster will be** at `t_release + d`, plus where the
enemy will be:

```
caster(t+d) = caster(t) + v_c·d           <- the impact point
enemy (t+d) = enemy (t)  + v_e·d
fire when |caster(t+d) − enemy(t+d)|_xz ≤ 6 m
```

Equivalently, the test is on the **relative** position at impact:

```
|(p_e − p_c) + (v_e − v_c)·d|_xz ≤ 6
```

which makes the three regimes obvious: a shared velocity cancels (E worlds), a closing pair
subtracts 12 m in 1.5 s at 8 + 4 m/s (D worlds), and a receding pair adds it (B2).

## 3. What the API can and cannot tell us

`battle_unit.lua` (the dump) has **no** velocity vector, no last-position pair and no per-tick
history. It has:

| read | dump wording |
| --- | --- |
| `is_moving()` | "Returns whether the unit is currently moving." |
| `is_moving_fast()` | "Returns whether the unit is moving fast (running/charging)." |
| `slow_speed()` | "Returns the unit's slow/walking movement speed **in m/s**." |
| `fast_speed()` | "Returns the unit's fast/running movement speed **in m/s**." |
| `ordered_position()` | "Returns the position to which the unit has been **ordered to move to**. Note that if the unit is attacking, as opposed to moving, then this will return the current position of the unit." |
| `bearing()` | "Returns the current **orientation** of the main squad of the unit **in degrees**." |
| `ordered_bearing()` | "… orientation of the position to which the unit has been ordered …" |

So velocity is **reconstructed**: `v = speed · normalise(ordered_position − position)`.

Rejected alternatives, and why:

* **Position history inside the mod** — needs a moving estimate per unit per poll and a memory of
  the previous tick; the mod polls at 5 Hz and tracks dozens of units, and a cached extrapolation
  would drift through every teleport, spawn and charge. Not worth it for a 1.5 s look-ahead.
* **`unit_in_range` / `can_reach_position`** — they answer reachability, not motion (and the
  round-96 report already burned the mod once by trusting `unit_in_range`).
* **`bearing()` alone** — its degree-to-axis convention is not stated anywhere in the dump. It is
  kept as a **caster-only** fallback for the case where the ordered point is degenerate (the
  ATTACKING case the dump itself describes), and is never used for an enemy.

## 4. Thresholds and their status

| constant | value | status |
| --- | --- | --- |
| `AIR_DROP_CENTER_M` | 6 | documented constant standing in for the formation footprint (unchanged since 109) |
| `AIR_DROP_DELAY_S` | 1.5 | **tunable**, between the user's observed 1 s and 2 s. **No row carries a fall time** — searched: `unit_special_abilities` has wind_up_time / active_time / recharge_time / effect_range / target_intercept_range, none of which is a projectile flight time |
| `AIR_DROP_INHERIT` | false | the one flag; `true` → `impact = caster + 2·v·d` |

Tuning table (what the field log will tell the user):

| symptom | action |
| --- | --- |
| rocks land ahead of the target | raise `AIR_DROP_DELAY_S` |
| rocks land behind the target | lower `AIR_DROP_DELAY_S` |
| rocks land ahead **and** `caster v=` is large with `src=ordered` | flip `AIR_DROP_INHERIT = true` |
| fires too early but `proj=` looks right | the delay is too long for this family |
| never fires | read the `watch:` lines: projected separation + both velocities |

## 5. Fail-closed behaviour (unchanged philosophy)

* unreadable caster position → **HOLD** (there is nothing to project);
* unreadable enemy position → that candidate is **skipped**, never guessed;
* unreadable `is_moving()` → ZERO velocity, `moving-unreadable`;
* unreadable speed → ZERO, `no-speed`;
* no usable heading (degenerate ordered point, no permitted bearing) → ZERO, `no-heading`;
* all of the above **degrade to round-109 behaviour** rather than suppressing the ability.

## 6. Harness pins

`PIN_BOUND = 6`, `PIN_DELAY = 1.5`. The section asserts both against the source, so a silent retune
of either fails the suite instead of quietly changing behaviour.

Distance pins per world: A 5.5/6.5 (fires/silent) · B1 12 → 0 · B2 5 → 17 · C1 10 → 4 · C2 5 → 11 ·
D1 20 → 2 · D2 25 → 7 · E 4 and 7 (unchanged) · F1 7 → 7 · F2 crossing → 5 · G1 12 stays · G2 5 ·
G3 12 stays · G4 12 → 6 (bearing fallback) · H 5 → 30 (skipped at the re-check) · I 24 → 12 short
(flag off) / 24 → 0 (flag on).
