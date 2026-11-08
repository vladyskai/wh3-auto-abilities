# Round 112 — the enemy-side lead dial, and the two diagnostic fixes

2026-10-24 · air-drop family (`air_drop_on_infantry`, 12 entries / 19 keys)
Installed pack md5 **`237702987893b8837d2dbb5df05d566b`**
Evidence: `docs/WH3_skyjunk_diagnosis.md` (pack `651f12e61284cae472bb06bf3a66b87d`, session
lines 947215–952480) · Harness 112 · Spreadsheet v13

---

## 1. The formula (four dials, two per body)

```
caster_projected = caster + v_caster * AIR_DROP_CASTER_DELAY_S * AIR_DROP_CASTER_LEAD
enemy_projected  = enemy  + v_enemy  * AIR_DROP_DELAY_S       * AIR_DROP_ENEMY_LEAD

fire when  |caster_projected - enemy_projected|_xz  <=  AIR_DROP_CENTER_M
```

Everything is on the **ground plane X/Z** (`battle_vector:get_y()` is height — a 3-D read would
measure 30–60 m from a unit directly underneath). The cast is **self-centred**: the chosen enemy is
the justification for pressing the button, never the cast target.

## 2. The defaults that ship

| Dial | Ships as | What it scales | Notes |
| --- | --- | --- | --- |
| `FOURTH.AIR_DROP_DELAY_S` | **1.5 s** | the enemy's lead **time** (the fall time) | unchanged since round 110; a tunable constant, no row carries a fall time |
| `FOURTH.AIR_DROP_ENEMY_LEAD` | **0.3** | the enemy's **share** of it | **NEW in round 112** |
| `FOURTH.AIR_DROP_CASTER_DELAY_S` | **1.5 s** | the caster's own lead time | unchanged since round 111 |
| `FOURTH.AIR_DROP_CASTER_LEAD` | **0.5** | the caster's share of it | unchanged since round 111 |
| `FOURTH.AIR_DROP_CENTER_M` | **6 m** | the bound | unchanged since round 109 (the bound is **not** a lead) |
| `FOURTH.AIR_DROP_INHERIT` | **false** | momentum inheritance | unchanged; `true` adds the caster's lead term a second time |

### Why 0.3 for the enemy

* At the zombie's **2.3 m/s** the old full carry was `2.3 × 1.5 = 3.45 m`. That is what turned a
  genuine pass underneath into a **6 m+** projected gap: the projected point was carried *past* the
  hoverer, so the gap was **largest exactly when the enemy was underneath** (≈5 m at the pass,
  ≈10 m one second later).
* The release is **not instantaneous**, so zero lead is not right either — a walking target does
  move during the fall. **0.3** is **0.45 s** of travel: about **1.0 m** at 2.3 m/s, roughly a third
  of the old error.
* `0.0` = the enemy's **current** position (impact straight down on where it is) — the emergency
  setting if a target still slips through.

## 3. Tuning guide — one dial per test

| Symptom | Dial to change | Order to try |
| --- | --- | --- |
| The **enemy walks through underneath** while the caster **hovers** | `AIR_DROP_ENEMY_LEAD` | **0.3 → 0.0** (the round-112 report) |
| The **caster chases a standing target** and fires **early** | `AIR_DROP_CASTER_LEAD` | **0.5 → 0.3 → 0.0**; only then `AIR_DROP_CASTER_DELAY_S` **1.5 → 1.0** |
| Fires **late when both move** | the lead of the body that was moving | `AIR_DROP_CASTER_LEAD` **0.5 → 0.8 → 1.0** / `AIR_DROP_ENEMY_LEAD` **0.3 → 0.6 → 1.0** |
| Still **early while both are stationary** | `AIR_DROP_DELAY_S` | **1.5 → 1.2 → 1.0** (shrinks **both** bodies) |

**One dial per test.** The four defaults above are the starting point. The log prints all four on
every air-drop line, so the next report is arithmetic rather than inference.

## 4. The two diagnostic fixes

1. **Exact metres below 15 m.** The `watch:` line used to quantise to 5 m bands — *coarser than the
   6 m decision margin*, so `~5m` covered 5.00–9.99 m and the deciding number was destroyed exactly
   where it mattered. Both numbers are now printed as `%.2f` below 15 m; the 5 m band survives above
   15 m, where the number is context only.

   ```
   before: sky_junk_bomb watch: nearest INFANTRY 'wh_main_vmp_inf_zombie' is centre=~5m vs bound=6m
           -> NOT under the caster [projected sep=~5m after delay=1.50s; ...]
   after:  [1003] sky_junk_bomb watch: nearest INFANTRY 'wh_main_vmp_inf_zombie' is centre=5.83m
           vs bound=6m -> NOT under the caster [projected sep=7.16m after delay=1.50s;
           caster v=(0.0, 0.0) 0.0 m/s src=stationary (delay=1.50s enemy_lead=0.30
           delay_caster=1.50s caster_lead=0.50); enemy v=(1.6, -1.7) 2.3 m/s src=ordered]
   ```

2. **The unit's ui id on every air-drop line.** Four identical `wh3_main_cth_veh_sky_junk_0` units
   (1002–1005) made "which of the four said this?" unanswerable from the log. Every line — decision,
   `watch:`, skip, pre-cast re-check, airborne/melee hold — now starts `[<ui id>] <marker>`.
   `FOURTH.ad_tag` prints `[?]` if the id read fails rather than dropping the line.

3. **All four dials on every line**, exactly:

   ```
   delay=1.50s enemy_lead=0.30 delay_caster=1.50s caster_lead=0.50
   ```

   plus `moving caster: lead=0.50 of 1.50s` only when the caster's velocity is non-zero.

## 5. Harness 112 — worlds, numbers and pins

Pins asserted against **both** trees (live + annotated): bound **6 m**, `AIR_DROP_DELAY_S` **1.5 s**,
`AIR_DROP_ENEMY_LEAD` **0.3**, `AIR_DROP_CASTER_DELAY_S` **1.5 s**, `AIR_DROP_CASTER_LEAD` **0.5**,
`AIR_DROP_INHERIT` **false** — each defined exactly once.

| World | Geometry | Arithmetic | Expected |
| --- | --- | --- | --- |
| A1 | hovering caster (100, 200); enemy crossing at x=105 (5 m lateral), 2.3 m/s, abreast; **enemy lead 1.0** | `sqrt(25 + 3.45²)` = **6.07 m** | **SILENT** — the reported bug, reproduced |
| A2 | the same world at the shipped **0.3** | `sqrt(25 + 1.035²)` = **5.11 m** | **FIRES** |
| B1 | enemy lead **0.0**, 5.00 m, 6 m/s | projected = current = **5.00 m** | **FIRES** |
| B2 | enemy lead **0.0**, 6.50 m | **6.50 m** | **SILENT** |
| C1/C2 | receding caster (8 m/s, lead 0.5 → x=94) + parked enemy at 98 | **4.00 m** projected, **2.00 m** now | FIRES at 0.3 **and** 1.0, identical numbers |
| D1 | caster +8 (→106), enemy 120 closing (−4 → 118.2) | **12.20 m** | SILENT |
| D2 | caster +8 (→106), enemy 112 closing (−4 → 110.2) | **4.20 m** | FIRES |
| E1 | enemy (103, 207), 2.3 m/s | `sqrt(9 + 8.035²)` = **8.58 m** | printed **exactly**, no `~` |
| E2 | enemy (100, 220), 2.3 m/s | **21.03 m** | still **bands** to `~20m` |
| F1/F2 | two same-type units, 1003 and 1004 | — | every air-drop line carries its own `[id]`; neither prints the other's |

**Result:** `checks 4492, failures 0`, run twice with byte-identical output.
**Red control** (`H112_LIVE`/`H112_ANN` → `docs/backups/round112/pre112_*.lua`, the round-111
build): **31 failures**, all in the new section — the pre-112 build has no enemy dial, prints only
two dials, bands at 5 m and prints no ui id.

**Supersession, stated plainly:** 22 assertions in the older sections were re-spelled for the new
formats or REBASED for the new enemy arithmetic (each carries `(v112 …)` / `(REBASED v112)` in its
label and its new number in the text). No check was deleted; the check count is unchanged. The one
decision that flips is E2 in the harness-110 block (same-heading pair, 7 m → now 1.40 m, fires),
because the caster's lead (12 m) now exceeds the enemy's (3.6 m); it is pinned deliberately.

## 6. Retest plan

1. Arm all four Sky-junks in one click — expect four `AUTO sky_junk_bomb for unit 10NN: now ON`
   lines and `sky_junk_bomb=ON` in the tick line for each.
2. Park three beside a zombie lane and let the block walk past. Read, **per unit id**, the
   `watch:` line with the lowest exact `projected sep`:
   * it should now bottom **inside 6 m** on the pass and fire;
   * if it still bottoms just above 6 m, change **only** `AIR_DROP_ENEMY_LEAD` (0.3 → 0.0) and
     retest.
3. Send back the lowest `projected sep` per unit id plus the `target:`/`ATTEMPT` line if one fires.
4. **One dial per test**, chosen by symptom (table in §3): walk-through while hovering →
   `AIR_DROP_ENEMY_LEAD`; caster chasing and firing early → `AIR_DROP_CASTER_LEAD`; late when both
   move → raise the moving body's lead; early while both parked → `AIR_DROP_DELAY_S`.
