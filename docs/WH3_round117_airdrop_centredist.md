# Round 117 — air drop: the detection moves from the EDGE to the CENTRE

**Date:** 2026-10-18
**Scope:** the air-drop family only (`trigger = "air_drop_on_infantry"`, 12 entries).
**Type:** ONE measurement change. Light iteration cycle (air-drop harness sections only; no
spreadsheet, no full suite) — explicitly approved by the user for tuning rounds.

---

## 1. The user's ruling (verbatim)

> 1. I agree with *"for tuning iterations like the air-drop work, run the affected harness section
>    only, skip the spreadsheet until you've signed off the behaviour, and do the full suite plus
>    workbook once at the end."* for now. Let's do it that way.
> 2. Let's keep our current calculation but just replace the detection on edge with detection on the
>    distance to center. Let's say 6 meters for now. I'll test.

## 2. What changed (and what did not)

| | |
|---|---|
| **Changed** | `UNDER` = the **ground-plane centre-to-centre** distance between the caster's `position()` and the enemy's `position()`, **x/z only** (`get_y` is HEIGHT), against `FOURTH.AIR_DROP_CENTER_M = 6.0`. |
| **Retired** | `FOURTH.AIR_DROP_EDGE_M = 0.1` and every `unit:unit_distance(enemy)` read in this evaluator. Nothing else in the file used the constant (checked: 0 occurrences survive). |
| **Kept exactly** | candidate filter (alive, `number_of_men_alive() > 10`), no infantry filter, the velocity-aware delay **measured once per contact** (0/1/2 s by cosine), the short-crossing fallback (0.3 s), the 0.2 s fast pass, the 250 ms poll (`tick_count` clock), `air_only` / `no_melee`, the self-centred cast on the OWNER, every fail-closed read, the read-verification log lines, the gates in `FOURTH.try_pair`. |

The new helper (restored from the round-109 implementation):

```lua
FOURTH.AIR_DROP_CENTER_M = 6.0

function FOURTH.ad_centre_gap(caster, enemy)
  -- position() on both, get_x/get_z on both, then position():distance_xz(other)
  -- with sqrt(dx^2 + dz^2) as the fallback; nil on ANY unreadable read (fail closed)
  return d, x1, z1, x2, z2
end
```

Every point that used the old number now uses the new one:

1. the candidate's measured gap used for **ranking** (`ad_nearest`),
2. the **UNDER test** (`if dist >= FOURTH.AIR_DROP_CENTER_M then` = separation),
3. the **contact stamping** and the dwell evidence (`ad_fired`),
4. the **waiting / hold / separation / fallback** log lines (all print the centre gap),
5. the **short-crossing fallback** reason string ("under the 6.00m centre line"),
6. the **pre-cast re-check** (`centre_now`, `centre_ok`, `gap_ok`),
7. the family's **inventory bound** (`ability.range_m = FOURTH.AIR_DROP_CENTER_M`),
8. the **tooltip** sentence and every decision line (`edge=` → `centre=`, 2 decimals).

## 3. Harness (light run)

New numbered harness: `mod_source/releases/20261018_airdrop_centredist_harness117/`
(`harness117.lua` assembled from `harness116.lua` by `splice117.py`, plus `h117_section.lua`).

* **`H117_LIGHT=1`** runs only the air-drop sections (`run_h112`, `h114`, `h115`, `h116`, `h117`);
  `run_h69` … `run_h108` are skipped. Without the variable the file is the full suite.
* **25 existing assertions retouched** (mechanically diffed: 25 `check(...)` statements changed),
  plus the 3 suite-boundary pins made LIGHT-aware:
  - h114 section 0 — 8 pins (constant, retired-token list, helper list, both call-site counts, the
    scan, the one comparison, the `edge=`→`centre=` field, the tooltip);
  - h115 section 0 — 2 pins (the four constants, `gap_ok = (centre_ok or …)`) + the A2/C2 log texts
    and the F drift world (edge `dist_seq` → **`pos_seq`**, since a sequence of edge metres no longer
    means anything);
  - h116 section 0 — 1 pin (the candidate filter/constants) + A3, F1, G2, I2a/I2b, J2, K1/K2 log and
    world texts, and the K drift world (edge `dseq` → `pos_seq`).
* **Worlds migrated, not deleted.** `mk` in h115/h116 keeps its `dm[euid] = <old edge gap>` table but
  turns it into a **place on the ground**: `< 0.1 → 5.9 m`, otherwise `6.5 m`, read on every
  `position()` call, with the bearing from the caster and the heading (`ordered − position`)
  preserved exactly — so every cosine the older worlds measured is unchanged and only the number the
  rule compares is new.
* **New worlds (h117)** — ~124 checks:
  - **A1** 5.9 m → stamps, waits the measured 1.00 s, fires on the poll that completes it;
  - **A2** 6.1 m → six polls, nothing stamped, nothing cast, `centre=6.10m (need < 6.00m)`;
  - **B1/B2/B3** the dynamic delay still applies at 5.9 m: closing `proj=+1.00 delay=0.00s` (fires on
    the next poll), receding `proj=-1.00 delay=2.00s` (holds at 1.75 s, fires at 2.00 s), across
    `proj=+0.00 delay=1.00s` (fires at 1.00 s);
  - **C1** a 0.25 s contact that separates to 6.5 m → **cancelled**, nothing fires;
  - **C2** a 0.75 s contact that separates to 6.5 m → the **short-crossing fallback fires** on the
    separation evaluation, and the re-check accepts it;
  - **D1/D2/D3** unreadable caster position / enemy position / co-ordinate read → no candidate, no
    cast, no crash (fail closed);
  - **E** the pre-cast re-check **re-measures the centre**: the pair drifts 5.9 → 6.1 m between the
    picker and the re-check of the same poll → `centre=6.10m (need < 6.00m) -> SKIPPED at re-check`.

### Results

| run | checks | failures |
|---|---|---|
| light run, new source (`H117_LIGHT=1`) | **1828** | **0** |
| light run, **red control** (pre-117 snapshots as `H117_LIVE`/`H117_ANN`) | 1828 | 85 (49 of them in the h117 section: every pin, A2, C1/C2, D and E fail — the old edge rule fires at 6.1 m and cannot detect an unreadable position) |

17 "the WHOLE harness-NN suite re-ran" cumulative-total checks are **not evaluated** in a light run
(they compare the running total against the full suite) and are reported as skipped.

## 4. Build + install

`build_and_install117.py` (generated by `make_builder117b.py` from the round-116 builder) — RPFM
session on `ws://127.0.0.1:45127`.

* pack contents: the 5 ship files, all **MATCHES SOURCE: True** (sha256 per file), the main script
  **byte-identical** when read back out of the pack;
* content gates: round 114 / 115 / 116 / **117** all OK;
* built pack md5 **`516b16aaa33d26abede8738c4447ffbe`**, installed md5 **`516b16aaa33d26abede8738c4447ffbe`**, IDENTICAL `True`;
* independent check of the INSTALLED pack: the whole source script is present verbatim,
  `AIR_DROP_EDGE_M` = 0 occurrences, `ad_centre_gap` = 1 definition, `" edge="` = 0.

| file | md5 |
|---|---|
| `mod_source/script/battle/mod/zz_test_deadly_onslaught.lua` | `c75d492d4e7599469d4b6e7b28aae3f0` |
| `docs/WH3_auto_ability_annotated.lua` | `b00fda45a7f92d1750f5653ef6a98970` |
| installed `data/zz_test_deadly_onslaught.pack` | `516b16aaa33d26abede8738c4447ffbe` |

## 5. Deliberately NOT done this round

* **The full suite was not run.** Only the air-drop sections ran (the approved light cycle). Other
  families' harnesses (h69–h108) and their cumulative totals were skipped.
* **No spreadsheet / master workbook was regenerated or touched** (any version).
* The ability tracker was not updated.

## 6. What remains unverified

1. **No field test yet.** The 6 m centre value is a test value the user will judge in battle; the
   harness proves the mechanism, not that 6 m is the right number.
2. **The full suite is unproven against this source.** The change is textually local to the air-drop
   evaluator and its helper, and the other triggers still use `FOURTH.eg_enemy_gap` unchanged, but no
   full-suite run has confirmed it. The h117 boundary pin is a **floor** (`>= 400` checks), not the
   exact full-suite total, until the next full run.
3. **Real-engine `distance_xz`** is exercised only through a mock that implements the documented
   signature; the sqrt fallback is proven by the harness, the engine method's live return is not.
4. **What 6 m means for a wide formation** — centre-to-centre ignores footprint, so a large enemy
   block is "under" the drop when its CENTRE is within 6 m, even if the caster is not literally over
   its models. That is the intended trade (the user asked for centre distance); it is unmeasured at
   the table.

## 7. Retest plan (in game)

1. Arm the air-drop family (M/A badge) on the same carrier units as round 116 and drop on a moving
   enemy line.
2. In `zz_test_deadly_onslaught_log.txt` watch for, per contact:
   `dwell started: under at gap X.XXm, waiting Y.YYs` — the gap must now read the **centre**
   distance (typically 4–6 m, not 0.0–0.2 m);
   `reads: … proj=… src=… delay=…` — the measured delay (0 s closing / 1 s across / 2 s receding);
   `dwell satisfied…` or `short crossing: … -> FIRING on separation`;
   the pre-cast line `centre=X.XXm (need < 6.00m) -> FIRING (re-checked)`.
3. If it still drops too early, **LOWER** `AIR_DROP_CENTER_M` (6.0 -> 5.0 -> 4.0: a smaller bound
   fires closer in, i.e. later); if it never fires, **RAISE** it (6.0 -> 7.0). That is the ONLY
   number to tune in this design. (CORRECTED 2026-10-20 at the sign-off pass - the original line
   had the direction inverted: FIRE is `centre < bound`, so a BIGGER bound fires EARLIER.)
4. Once the behaviour is signed off: run the **full suite** and regenerate the master workbook in the
   same step, and re-pin the h117 boundary to the exact total.

---

**RECONCILED 2026-10-20 (sign-off pass).** This round shipped in LIGHT mode, so the full suite was
unproven and the workbook was untouched at the time. Both are now done: the FULL suite runs
**4,777 checks / 0 failures** (harness 119, twice, byte-identical) and the master workbook is
`docs/WH3_abilities_master_v18_2026-10-18.xlsx` (+ `.ods`), which describes this round's rule and
retires what it replaced. Record: `docs/WH3_signoff_full_suite_v18.md`. No source change and no
rebuild - the installed pack is still `2f215bc4c35845452103327fb62ba554`.
