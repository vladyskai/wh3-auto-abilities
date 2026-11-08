# Round 118 — air drop: THE DELAY GOES, the centre stays

**Date:** 2026-10-18
**Scope:** the air-drop family only (`trigger = "air_drop_on_infantry"`, 12 entries).
**Type:** ONE deletion. Light iteration cycle (air-drop harness sections only; no spreadsheet,
no full suite) — the cycle the user approved for tuning rounds.

---

## 1. The user's ruling (verbatim)

> I tried it. Let's keep the distance to center and remove the delay we had completely.

## 2. What the rule is now

| | |
|---|---|
| **candidate** | ALIVE, `number_of_men_alive() > AIR_DROP_MIN_MEN` (10), centre gap READABLE. No infantry test. |
| **chosen** | the NEAREST valid candidate by `FOURTH.ad_centre_gap` |
| **UNDER** | the chosen enemy's ground-plane **centre-to-centre** gap `< FOURTH.AIR_DROP_CENTER_M` (6.0 m) |
| **FIRE** | on the **evaluation that measured it** — subject only to the armed state, `air_only` / `no_melee`, the gates in `FOURTH.try_pair`, and the pre-cast re-check re-measuring the centre on fresh handles |

No stamp, no dwell, no elapsed check, no second look inside a contact, no fallback on the way
out. The 0.2 s fast pass and the 250 ms poll both cast on the evaluation that sees the line
crossed, so the drop leaves within one fast-pass interval (0.2 s) of the centre arriving —
normally on that very evaluation.

## 3. Deleted (and who used it)

The whole file was grepped for every symbol before anything was touched. The call-site audit
(line numbers in the pre-118 source, `docs/backups/round118/`):

| symbol | hits | outside the evaluator + its pre-cast re-check |
|---|---|---|
| `AIR_DROP_DWELL_MID_S` | 9 | none |
| `AIR_DROP_DWELL_SWING_S` | 4 | none |
| `AIR_DROP_MIN_CONTACT_S` | 9 | none |
| `FOURTH.ad_pair` (the contact table) | 21 | none |
| `ad_pair_key` / `ad_pair_stamp` / `ad_pair_need` / `ad_pair_drop` | 2 / 2 / 3 / 3 | none |
| `ad_under` | 3 | none |
| `ad_purge_unit` | 3 | **1** — line 4873, a comment in `drop_unit_by_ui_id` |
| `ad_contact_clear` | 2 | none |
| `zz_ad_dwell_purge` (the hook) | 2 | **1** — line 4875, its only call site, in `drop_unit_by_ui_id` |
| `ad_enemy_velocity` | 4 | none |
| `ad_proj_text` (the printed cosine) | 3 | none |
| `ad_dynamic_delay` | 2 | none |
| `ad_vread` / `ad_vread_px` / `ad_vread_pz` | 9 / 4 / 3 | none |
| `FOURTH.ad_event` | 9 | none |
| `ad_fired` | 4 | none |

**So exactly one dependency lived outside the evaluator:** the purge hook `zz_ad_dwell_purge`,
called from `drop_unit_by_ui_id` (the one drop routine). That routine existed only to clear the
per-pair contact rows, so the call **and** the hook were removed together — nothing else in the
file named it. Everything else was referenced only by the evaluator itself, its pre-cast
re-check, and its own documentation, so it was deleted outright rather than left dead.

**Removed:**

* `FOURTH.AIR_DROP_DWELL_MID_S = 1.0`, `FOURTH.AIR_DROP_DWELL_SWING_S = 1.0`,
  `FOURTH.AIR_DROP_MIN_CONTACT_S = 0.3`;
* `FOURTH.ad_pair` and every helper over it — `ad_pair_key`, `ad_pair_stamp`, `ad_pair_need`,
  `ad_pair_drop`, `ad_under`, `ad_purge_unit`, `ad_contact_clear`;
* the purge hook `zz_ad_dwell_purge` and its call site in `drop_unit_by_ui_id`;
* `ad_enemy_velocity` and the raw-read body it built (`ad_vread`, `ad_vread_px`, `ad_vread_pz`),
  `ad_proj_text`, `ad_dynamic_delay`;
* `ad_event` (the un-deduped event line: started / held / satisfied / cancelled / short crossing);
* the short-crossing fallback, and every dwell / hold / separation / cosine log line.

**The read-verification logging was removed with the delay it was serving.** It printed
`is_moving`, `is_moving_fast`, `slow_speed`, `fast_speed`, `position()`, `ordered_position()` and
`|h|` so the cosine could be checked against real engine answers. No rule consults a heading any
more, so the entire raw-read block went rather than being left printing values nothing reads. If a
delay is ever designed back in, that block is where to start (it survives in
`docs/backups/round118/pre118_zz_test_deadly_onslaught.lua`).

**Kept, untouched:** the centre detection and `ad_centre_gap` (x/z, `distance_xz` with the sqrt
fallback, fail-closed), the candidate filter, the 0.2 s fast pass with its 30 m near gate (which
now naturally reads the centre distance), the 250 ms poll (`POLL_MS`), `air_only` / `no_melee`, the
self-centred cast on the OWNER, every fail-closed read, the gates in `FOURTH.try_pair`, and the
pre-cast re-check. The tooltip now says "casts immediately on that evaluation - no delay at all".

Net effect on the shipped script: **16 111 → 15 682 lines** (795 425 → 774 254 bytes, −21 171).
The annotated copy: 13 528 → 13 187 lines (665 849 → 650 492 bytes).

## 4. Harness (light run)

New numbered harness: `mod_source/releases/20261018_airdrop_immediate_harness118/`
(`harness118.lua`, assembled from `harness117.lua` by `splice118.py`; the LIGHT switch is now
**`H118_LIGHT=1`**). It runs `run_h112`, `run_h114`, `run_h115`, `run_h116`, `run_h117`,
`run_h118`.

* **185 assertions retouched.** The three sections whose worlds pinned the removed machinery held
  **184** `check(...)` statements between them (`run_h115` 59, `run_h116` 70, `run_h117` 55); 183
  of them were rewritten or removed, 1 (`I2`) is unchanged, and one further pin
  (`h114`'s `ad_tag` site count, 6 → 5 call sites) moved with the deletion. **24 new assertions**
  were added in the six-world section.
  * `run_h115` — was the dwell section. Its worlds are gone; the section now pins the **absence**:
    one check per deleted symbol per file (21 × 2 files = 42 zero-occurrence pins), plus the four
    constants, the one comparison, the straight-to-cast UNDER branch, the candidate filter, the
    `air_only` / `no_melee` / self-cast / fail-closed survivors, the centre-only re-check, both
    timers, the family counts (12 of 689) and the new tooltip. Its `I` world (a grounded caster
    never fires an air-only row) is kept — it was never about the delay.
  * `run_h116` — was the velocity/cosine section. It now proves the negative: the evaluator reads
    no movement flag, no speed, no order point and no clock, no pair table exists, and a world whose
    enemy is **running straight away** at 5.9 m (the old `proj = −1`, 2.00 s case) still fires on the
    **first** evaluation.
  * `run_h117` — keeps its static pins for the CENTRE measurement (helper, `distance_xz`, one
    comparison, `centre=`, the re-check, the 6 m bound, `eg_enemy_gap` untouched), retouched where
    they described the delay. Its worlds moved to `run_h118`.
* **The six worlds** (both files each):
  * **(a)** 5.9 m → casts on the **first** poll, once; the decision line and the re-check line both
    print `centre=5.90m (need < 6.00m)`;
  * **(b)** 6.1 m → six polls + five fast ticks cast nothing, `-> NOT YET`, no wait line;
  * **(c)** static pin — no delay state survives: 21 deleted symbols × 2 files = 42 searches,
    **0 hits**; no per-pair table; no clock read inside the evaluator;
  * **(d)** a second evaluation right after a cast does not double-cast: 5 fast ticks + 2 polls
    inside the 2 s guard cast nothing more, one `FIRING (re-checked)` line, and past the guard the
    still-under pair casts again exactly once;
  * **(e)** unreadable positions fail closed — caster `position()` raises, enemy `position()`
    raises, and a position object with no `get_x`/`get_z`: 0 casts, no crash;
  * **(f)** the pre-cast re-check re-measures the centre: picker 5.9 m → re-check 6.1 m in the SAME
    evaluation → `centre=6.10m (need < 6.00m) -> SKIPPED at re-check`, `centre_ok=false`,
    `- cast not spent`; the control world without the drift casts on the first evaluation, and the
    drifted pair casts once the guard window the refused attempt consumed has passed.

### Results

| run | checks | failures |
|---|---|---|
| light run, new source (`H118_LIGHT=1`) | **1586** | **0** |
| light run, **red control** (pre-118 snapshots as `H118_LIVE` / `H118_ANN`) | 1586 | **80** — every zero-occurrence pin, the tooltip, the "no movement/clock read" pins, and worlds (a), (d), (f)-control and the running-away world fail: the old rule waits, so a 5.9 m contact does not cast on the first evaluation |

17 "the WHOLE harness-NN suite re-ran" cumulative-total checks are **not evaluated** in a light run
and are reported as skipped, exactly as in rounds 116 and 117.

The light run is smaller than round 117's 1828 because the dwell and velocity worlds it counted
(~1 650 of those checks) asserted a rule that no longer exists; they were replaced, not disabled.

## 5. Build + install

`build_and_install118.py` (generated from the round-117 builder by `make_builder118.py`) — RPFM
session on `ws://127.0.0.1:45127`.

* pack contents: the 5 ship files, all **MATCHES SOURCE: True** (sha256 per file), the main script
  **byte-identical** when read back out of the pack;
* content gates: round 114 / **118** both OK (the round-115 / 116 / 117 gate blocks were replaced —
  they asserted the delay machinery exists — by one round-118 block that asserts it is gone, with
  `AIR_DROP_DWELL_*` / `ad_pair*` / `ad_vread*` / `ad_dynamic_delay` / `ad_proj_text` /
  `zz_ad_dwell_purge` / `ad_fired` at **0 occurrences**, and pins the centre rule, the fast pass,
  `POLL_MS`, the 30 m gate, the 12 / 689 counts and the tooltip);
* built pack md5 **`2f215bc4c35845452103327fb62ba554`**, installed md5
  **`2f215bc4c35845452103327fb62ba554`**, IDENTICAL `True`;
* independent check of the INSTALLED pack: `casts immediately on that evaluation - no delay at all`
  = 1, `AIR_DROP_DWELL` = 0, `ad_pair` = 0, `ad_dynamic_delay` = 0, `dwell started` = 0,
  `ad_centre_gap` = 11, `-> FIRING (re-checked)` = 1.

| file | md5 |
|---|---|
| `mod_source/script/battle/mod/zz_test_deadly_onslaught.lua` | `99a3d107986ea06efc956c0e5ea5fb76` |
| `docs/WH3_auto_ability_annotated.lua` | `7a71e0d220fea0b4451ab5bf61ba752a` |
| installed `data/zz_test_deadly_onslaught.pack` | `2f215bc4c35845452103327fb62ba554` |

## 6. Deliberately NOT done this round

* **The full suite was not run.** Only the air-drop sections ran (the approved light cycle).
* **No spreadsheet / master workbook was regenerated or touched** (any version).
* The ability tracker was not updated.

## 7. What remains unverified

1. **No field test yet.** Whether 6 m is the right distance is the user's call in battle; what the
   harness proves is that the cast now lands on the first evaluation that sees the centre inside it.
2. **The full suite is unproven against this source.** The change is textually local to the air-drop
   evaluator, its helpers and one call site in `drop_unit_by_ui_id`, and every other trigger still
   uses `FOURTH.eg_enemy_gap` untouched — but no full-suite run has confirmed it.
3. **Real-engine `distance_xz`** is exercised only through a mock implementing the documented
   signature; the sqrt fallback is proven by the harness, the engine method's live return is not.
4. **A pass-through is now invisible by design.** A pair that arrives and leaves between two
   evaluations is not seen at all (there is no fallback any more). At 0.2 s that is a burst
   crossing more than 6 m of ground between fast ticks; if the user ever reports a missed drop,
   that is the mechanism, and the answer is the fast-pass interval, not a new delay.

## 8. Retest plan (in game)

1. Arm the air-drop family (M/A badge) on the same carrier units as round 117 and fly over a moving
   enemy line.
2. In `zz_test_deadly_onslaught_log.txt` watch for, per contact:
   `nearest valid:'<type>' entities=<n> centre=X.XXm (need < 6.00m) -> NOT YET` while approaching —
   the gap must read the **centre** distance (4–6 m just before the line, not 0.0–0.2 m);
   then the **same** line with `-> FIRING` on the first evaluation inside 6 m, immediately
   followed by `centre=X.XXm (need < 6.00m) -> FIRING (re-checked)`;
   and `-> SKIPPED at re-check ... centre_ok=false ... - cast not spent` if the pair drifted out
   between the two measurements of that evaluation.
3. **There is no wait line any more** — no `dwell`, no `reads:`, no `proj=`, no `waiting`. If any of
   those appear, the wrong pack is installed (check the installed md5 above).
4. If it drops too early, **LOWER** `AIR_DROP_CENTER_M` (6.0 -> 5.0 -> 4.0); if it never fires,
   **RAISE** it (6.0 -> 7.0). That is the ONLY number to tune in this design. (CORRECTED
   2026-10-20 at the sign-off pass - the original line had the direction inverted: FIRE is
   `centre < bound`, so a BIGGER bound fires EARLIER.)
5. Once the behaviour is signed off: run the **full suite** and regenerate the master workbook in
   the same step, and re-pin the suite-boundary checks to the exact total.

---

**RECONCILED 2026-10-20 (sign-off pass).** This round shipped in LIGHT mode, so the full suite was
unproven and the workbook was untouched at the time. Both are now done: the FULL suite runs
**4,777 checks / 0 failures** (harness 119, twice, byte-identical) and the master workbook is
`docs/WH3_abilities_master_v18_2026-10-18.xlsx` (+ `.ods`), which describes this round's rule and
retires what it replaced. Record: `docs/WH3_signoff_full_suite_v18.md`. No source change and no
rebuild - the installed pack is still `2f215bc4c35845452103327fb62ba554`.
