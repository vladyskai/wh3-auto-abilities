# Round 111 — the moving-caster dials (only the caster's lead moves)

Date: 2026-10-18 · Harness 111 · Installed pack md5 `651f12e61284cae472bb06bf3a66b87d`
(round 110 was `588e6c3c6781d02321ce7b31af04884f`)

The user's fourth field report, verbatim:

> "I tested it. It seems to work okay when the caster is stationary, but it definitely drops the
> rocks too soon when in movement. How do we tune it?"

A **stationary** caster is right, so the **enemy** projection and the 6 m bound are right and are
**not touched**. The error exists only while the caster moves and fires **too soon**, so the
caster's projected point runs ahead of the real impact point — the caster's lead term is
**over-stated**.

One behaviour change ships. No counts change: **689 entries / 742 keys**,
`air_drop_on_infantry` **12 entries / 19 keys**, 46 evaluators.

---

## 1. The rule

```
caster_projected = caster + v_caster * AIR_DROP_CASTER_DELAY_S * AIR_DROP_CASTER_LEAD
enemy_projected  = enemy  + v_enemy  * AIR_DROP_DELAY_S
fire when |caster_projected - enemy_projected|_xz <= AIR_DROP_CENTER_M (6 m)
```

## 2. Constants

| constant | value | meaning |
| --- | --- | --- |
| `FOURTH.AIR_DROP_CASTER_DELAY_S` | **1.5** (new) | the caster's **own** lead time, independent of the enemy's |
| `FOURTH.AIR_DROP_CASTER_LEAD` | **0.5** (new) | the **share** of that lead that is applied: `0.0` = caster treated as stationary, `1.0` = the round-110 behaviour that over-leads |
| `FOURTH.AIR_DROP_DELAY_S` | 1.5 (unchanged) | the **enemy's** projection and the shared fall time |
| `FOURTH.AIR_DROP_CENTER_M` | 6 (unchanged) | the centre bound |
| `FOURTH.AIR_DROP_INHERIT` | false (unchanged) | no-momentum flag; when true the caster's lead term is added a second time |

At the shipped pair the caster is projected **half** its 1.5 s travel (8 m/s → 6 m, not 12 m). A
parked caster is identical at every dial value, because the term multiplies zero velocity.

## 3. TUNING GUIDE — one dial per test, in this order

| symptom | change | order |
| --- | --- | --- |
| fires **early while MOVING** | `AIR_DROP_CASTER_LEAD` | **0.5 → 0.3 → 0.0**, then `AIR_DROP_CASTER_DELAY_S` 1.5 → 1.0 |
| still **early while STATIONARY** | `AIR_DROP_DELAY_S` | lower it (1.5 → 1.2 → 1.0) — touches both bodies |
| **never fires while MOVING** | `AIR_DROP_CASTER_LEAD` | **0.5 → 0.8 → 1.0** |

## 4. The log

The decision line prints the two dials after the caster's projected point, and a moving-only
fragment:

```
caster=(100.0, 200.0) v=(8.0, 0.0) 8.0 m/s src=ordered proj=(106.0, 200.0)
from delay_caster=1.50s lead=0.50 moving caster: lead=0.50 of 1.50s
enemy=(116.0, 200.0) v=(0.0, 0.0) 0.0 m/s src=stationary proj=(116.0, 200.0)
centre=10.0m ... now=16.0m ...
```

`moving caster: …` appears **only** when the caster's velocity is non-zero — a parked caster's lead
term did nothing, and a fragment there would invite tuning the wrong dial.

## 5. KEPT EXACTLY

The enemy term and its delay, the 6 m bound, `AIR_DROP_INHERIT`, `air_only` / `no_melee`, the
self-centred cast on the OWNER, every fail-closed read, the 70 % map exemption, and the pre-cast
re-check — which re-projects through the **same helper** and therefore reads the **same two dials**.

## 6. Harness 111

**4387 checks / 0 failures**, run twice, byte-identical (`h111_run1.txt` = `h111_run2.txt`,
md5 `65ba107b66f8861620bcd7c69b5ee1de`). Red control (round-110 snapshot,
`docs/backups/round111/pre111_*.lua`): **41 failures**, all in the new section.

Pins: `BOUND = 6`, `DELAY = 1.5`, `CASTER_DELAY = 1.5`, `CASTER_LEAD = 0.5`.

Worlds (caster at x=100 closing 8 m/s unless stated; lead L projects `100 + 12·L`):

| world | setup | lead | result |
| --- | --- | --- | --- |
| A1–A3 | parked caster, enemy 5.5 m | 0.5 / 1.0 / 0.0 | **fires at 5.5 m in all three** — the dial cannot move a parked caster |
| A4 | parked caster, enemy 6.5 m | 1.0 | silent (round-110 pin) |
| B1 | enemy 16 m ahead | **1.0** | **FIRES at 4.0 m projection** — the reported bug |
| B2 | enemy 16 m ahead | 0.5 | **silent**, projected band 10 m vs instant 15 m |
| D1/D2 | enemy 10 m | 1.0 / 0.5 | both fire: 2.0 m vs 4.0 m projection |
| D3/D4 | enemy 18 m | 1.0 / 0.5 | fires at 6.0 m / silent at 12.0 m |
| E1–E4 | enemy 4 m, moving vs parked | 0.0 / 0.5 / 1.0 / 0.5 | 0.0 ≡ parked: same point `(100.0, 200.0)`, same 4.0 m |
| F1/F2 | caster 60 m, enemy 80 m; caster delay 1.5 / 1.0 | 1.0 | caster 72.0 → 68.0; **enemy 74.0 in both** |
| G1/G2 | enemy drifts 110 → 105 / 110 → 140 | 0.5 | re-check 1.0 m **fires** / 34.0 m **SKIPPED**, dials in both lines |

Dial changes are applied the only faithful way — a copy of the source with **one constant line
substituted** (`variants/`, regenerated per run), because `FOURTH` is a file-local table.

The round-110 section inside `harness111.lua` was regenerated with one change: every world whose
caster **moves** pins lead 1.0, the rule it was written against. `harness110.lua` was rebuilt from it
and re-run alone: **4253 checks / 0 failures**.

## 7. Build

5 ship files byte-identical (script 782,275 bytes). built == installed
md5 **`651f12e61284cae472bb06bf3a66b87d`** (1,117,351 bytes). `zz_probe_dist.pack` left installed,
untouched (`d4e67cfb8bc562c7d6f0ff742909c13d`).

## 8. Retest plan

1. Moving pass at infantry. Compare `now=` at the decision with the previous build (16 m → ~10 m).
2. Still early → `AIR_DROP_CASTER_LEAD` 0.5 → 0.3; still early → 0.0.
3. 0.0 still early → `AIR_DROP_CASTER_DELAY_S` 1.5 → 1.0.
4. Never fires on a pass → lead 0.5 → 0.8.
5. Stationary wrong → **not** this dial; lower `AIR_DROP_DELAY_S` and say so.

Send back one good and one bad decision line.
