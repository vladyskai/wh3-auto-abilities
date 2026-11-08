# Round 111 — the moving-caster dials (only the caster's lead moves)

2026-10-18 · harness 111 · installed pack md5 `651f12e61284cae472bb06bf3a66b87d`
(previous: 110 `588e6c3c6781d02321ce7b31af04884f`)

## 1. The field result, stated as arithmetic

The user's fourth air-drop report, verbatim:

> "I tested it. It seems to work okay when the caster is stationary, but it definitely drops the
> rocks too soon when in movement. How do we tune it?"

That splits the rule in two:

* **stationary caster → correct.** The enemy projection and the 6 m bound are therefore correct, and
  must not be touched.
* **moving caster → fires too soon.** "Too soon" means the release happens while the caster is
  still short of the target, i.e. the **caster's projected point runs AHEAD of the real impact
  point**. The caster's lead term is **over-stated**.

Round 110 projected the caster the full fall time ahead: `caster + v_caster * 1.5 s`. At 8 m/s that
is 12 m of lead. If the flier decelerates, turns into the pass, or the release happens part-way
through the wind-up, the real impact point is closer to the cast position than that. The fix is a
dial on the caster's term only.

## 2. The rule now

```
caster_projected = caster + v_caster * AIR_DROP_CASTER_DELAY_S * AIR_DROP_CASTER_LEAD
enemy_projected  = enemy  + v_enemy  * AIR_DROP_DELAY_S
fire when |caster_projected - enemy_projected|_xz <= AIR_DROP_CENTER_M (6 m)
```

| constant | ships as | meaning |
| --- | --- | --- |
| `FOURTH.AIR_DROP_CASTER_DELAY_S` | **1.5** s | the caster's OWN lead time (independent of the enemy's) |
| `FOURTH.AIR_DROP_CASTER_LEAD` | **0.5** | the share of that lead which is applied; `0.0` = caster treated as stationary, `1.0` = the round-110 behaviour that over-leads |
| `FOURTH.AIR_DROP_DELAY_S` | 1.5 s (unchanged) | the ENEMY's projection and the shared fall time |
| `FOURTH.AIR_DROP_CENTER_M` | 6 m (unchanged) | the bound |
| `FOURTH.AIR_DROP_INHERIT` | false (unchanged) | the no-momentum flag; when true the caster's lead term is added a second time |

At the shipped pair the caster is projected **half** its 1.5 s travel: 8 m/s → 6 m of lead instead
of 12 m. A parked caster is unchanged at any dial value (the term multiplies zero velocity), which
is exactly what the field says must stay right.

## 3. What is unchanged

The enemy projection (shared delay, full term), the 6 m centre bound, `AIR_DROP_INHERIT`,
`air_only` / `no_melee` per row, the self-centred cast on the OWNER, every fail-closed read, the
70 % map exemption, and the pre-cast re-check — which re-projects through the **same helper**, so it
reads the **same two dials** and cannot disagree with the picker.

Counts are untouched: **689 entries / 742 keys**, `air_drop_on_infantry` 12 entries / 19 keys,
46 evaluators.

## 4. The log

The decision line now names the term that produced the jump, immediately after the caster's
projected point:

```
... caster=(100.0, 200.0) v=(8.0, 0.0) 8.0 m/s src=ordered proj=(106.0, 200.0)
    from delay_caster=1.50s lead=0.50 moving caster: lead=0.50 of 1.50s
    enemy=(116.0, 200.0) v=(0.0, 0.0) 0.0 m/s src=stationary proj=(116.0, 200.0)
    centre=10.0m (the PROJECTED separation, which is what decides) now=16.0m ...
```

* `delay_caster=…s lead=…` — always present on the target line, the watch line and both pre-cast
  re-check lines.
* `moving caster: lead=0.50 of 1.50s` — **only** when the caster's velocity is non-zero. A parked
  caster's lead term is inert, and printing the fragment there would invite tuning the wrong dial.

## 5. TUNING GUIDE (change ONE dial per test, in this order)

| symptom | dial to change | order to try |
| --- | --- | --- |
| **fires early while MOVING** (rocks land ahead of the target on a pass) | `AIR_DROP_CASTER_LEAD` | **0.5 → 0.3 → 0.0**; if 0.0 is still early, then `AIR_DROP_CASTER_DELAY_S` **1.5 → 1.0** |
| **still early while STATIONARY** (the case the field says is right — so this means the fall time itself is wrong) | `AIR_DROP_DELAY_S` | lower it (1.5 → 1.2 → 1.0); this shrinks BOTH bodies and returns the round-109 shape for a parked pair |
| **never fires while MOVING** (the flier passes over and nothing happens) | `AIR_DROP_CASTER_LEAD` | **0.5 → 0.8 → 1.0** (1.0 = round-110 behaviour, the most aggressive lead) |

Levers, in one sentence each:

* `AIR_DROP_CASTER_LEAD` — *how much of the caster's own travel is real*. Down = the release is
  judged closer to the cast position = later in the pass.
* `AIR_DROP_CASTER_DELAY_S` — *how long the caster's own lead is*. Only for when the lead factor
  alone cannot fix it; it does not touch the enemy prediction at all.
* `AIR_DROP_DELAY_S` — *the fall time*. Touches BOTH bodies. Use only for a stationary symptom.

Do **not** change the lead and the delay in the same test: the log prints both, and one changed dial
at a time is what makes the next field result readable.

## 6. Harness 111

Green: **4387 checks / 0 failures**, run twice, byte-identical
(`h111_run1.txt` = `h111_run2.txt`, md5 `65ba107b66f8861620bcd7c69b5ee1de`).
Red control (the round-110 snapshot in `docs/backups/round111/pre111_*.lua`): **41 failures**, all in
the new section — every source check, every dial-log check and every moving world; the stationary
decisions and the round-109/110 suites above it all still pass, which is the signature of a
genuinely new mechanism rather than a renumbered one.

**Pins** (asserted against the source, so a silent retune fails the suite):
`PIN_BOUND = 6`, `PIN_DELAY = 1.5`, `PIN_CASTER_DELAY = 1.5`, `PIN_CASTER_LEAD = 0.5`.

Per-world distances (caster at x=100 closing at 8 m/s unless stated; lead L projects
`100 + 12·L`):

| world | setup | lead | result |
| --- | --- | --- | --- |
| A1 | parked caster, enemy 5.5 m | 0.5 | **fires**, projected 5.5 m = instant 5.5 m |
| A2 | parked caster, enemy 5.5 m | 1.0 | **fires**, same 5.5 m — a dial cannot move a parked caster |
| A3 | parked caster, enemy 5.5 m | 0.0 | **fires**, same 5.5 m |
| A4 | parked caster, enemy 6.5 m | 1.0 | **silent** (the round-110 pin) |
| B1 | enemy 16 m ahead | **1.0** | **FIRES at a 4.0 m projection** — the reported bug, x=112 |
| B2 | enemy 16 m ahead | 0.5 | **silent**, projected band 10 m vs instant band 15 m |
| D1/D2 | enemy 10 m ahead | 1.0 / 0.5 | both fire — projection **2.0 m** at 1.0, **4.0 m** at 0.5 (later in time) |
| D3/D4 | enemy 18 m ahead | 1.0 / 0.5 | **fires** at 6.0 m at lead 1.0; **silent** (12.0 m) at 0.5 |
| E1 | enemy 4 m ahead | 0.0 | **fires**, projected `(100.0, 200.0)` = the cast position, 4.0 m |
| E2 | enemy 4 m ahead | 0.5 | **fires** at 2.0 m (x=106) |
| E3 | enemy 4 m ahead | 1.0 | **silent** (x=112, 8.0 m) |
| E4 | PARKED caster, enemy 4 m | 0.5 | **fires** at 4.0 m — the same point and the same separation as E1 |
| F1/F2 | caster 60 m, enemy 80 m closing 4 m/s; caster delay 1.5 / 1.0 | 1.0 | caster projects **72.0 / 68.0** (a 4 m move); enemy projects **74.0 in both** — the enemy term never sees the dial |
| G1 | enemy 110 m at the pick, 105 m at the re-check | 0.5 | pick 4.0 m → re-check **1.0 m** → **fires**, both lines print `lead=0.50` |
| G2 | enemy 110 m at the pick, 140 m at the re-check | 0.5 | pick 4.0 m → re-check **34.0 m** → **SKIPPED**, dials in the skip line |

The harness changes a dial the only faithful way available: `FOURTH` is a **file-local** table, so
each non-default world loads a copy of the same source with **only the constant line substituted**
(`variants/`, regenerated per run), exactly the one-line edit the user would make. The red-control
snapshot has no dial lines, so the helper returns the file unchanged.

The round-110 section inside `harness111.lua` was regenerated from `h110_section.lua` with one
change: every world whose **caster moves** now pins lead 1.0 — the rule those worlds were written
against — so their documented distances and log fragments still hold. `harness110.lua` was rebuilt
from that section and re-run on its own: **4253 checks / 0 failures**.

## 7. Build

* 5 ship files byte-identical to source (script 782,275 bytes; tooltip 331,235; badge template 2,864;
  `blank.png` 69; `auto_badge.png` 252).
* built == installed md5 **`651f12e61284cae472bb06bf3a66b87d`** (1,117,351 bytes).
* installed-pack tokens: `FOURTH.AIR_DROP_CASTER_LEAD = 0.5` (1),
  `FOURTH.AIR_DROP_CASTER_DELAY_S = 1.5` (1), `function FOURTH.ad_dial_text(moving)` (1),
  `t_caster * lead_caster` (4), `delay_caster=` (2), `moving caster: lead=` (2).
* `zz_probe_dist.pack` left installed and untouched (md5 `d4e67cfb8bc562c7d6f0ff742909c13d`).

All five ship files were re-checked **verbatim inside the installed pack** after the copy
(script 782,275 B, tooltip 331,235 B, badge template 2,864 B, `blank.png` 69 B, `auto_badge.png`
252 B).

Spreadsheet `docs/WH3_abilities_master_v12_2026-10-18.xlsx` (+ `.ods`): the two dials and the tuning
guide in the Definitions, the round-111 rule on all 19 air-drop rows, the v12 Changelog row, Numbers
re-reconciled (every total identical to v11), and **v1-v11 byte-unchanged**.

## 8. What to retest

1. Arm Drop Rocks on a Terradon Riders unit and make a pass **while moving** at infantry. Watch the
   `centre=`/`now=` numbers: the release should now happen with a smaller `now=` than before
   (16 m → about 10 m on the same pass). If the rocks are still early, change
   `AIR_DROP_CASTER_LEAD` 0.5 → 0.3 (one line) and repeat.
2. If 0.3 is still early, go to 0.0 (caster treated as stationary). If 0.0 overshoots — rocks now
   landing *behind* the target — you have bracketed the answer between 0.0 and 0.3.
3. If 0.0 is STILL early, then the fall time itself is too long: lower `AIR_DROP_CASTER_DELAY_S`
   1.5 → 1.0.
4. If it stops firing on passes it used to fire on, the lead is too small: `AIR_DROP_CASTER_LEAD`
   0.5 → 0.8.
5. A stationary caster should behave exactly as before. If stationary tests now look wrong, the dial
   is not the cause — lower `AIR_DROP_DELAY_S` instead and report that, because that would mean the
   field result was about the fall time, not the lead.

Send back: the decision line (`caster=… proj=… from delay_caster=… lead=… enemy=… proj=… centre=…
now=…`) for one good pass and one bad pass.
