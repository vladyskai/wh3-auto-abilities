# Sign-off pass — the FULL harness suite and the master workbook v18

**Date:** 2026-10-18 (executed 2026-10-20)
**Type:** verification + documentation. **No source change, no rebuild, no pack reinstall.**

The user said *"Update the spreadsheet"*. Under the agreed rule that is the sign-off point: the light
cycle ends, the FULL suite runs, and the master workbook is regenerated. Rounds 117 and 118 had
shipped in light mode (air-drop harness sections only, no workbook), so v17 still documented round
116's measured delay — machinery that no longer exists in the shipped script.

---

## 1. The full suite

Harness 119 = harness 118 with five pin edits (see
`mod_source/releases/20261018_signoff_harness119/RELEASE_NOTES.md`). Both harnesses are run against
the shipped source and the annotated copy, both without `H118_LIGHT`.

| run | checks | failures |
|---|---|---|
| harness 118, FULL, shipped source | 4,777 | **5** |
| harness 119, FULL (run 1) | **4,777** | **0** |
| harness 119, FULL (run 2) | 4,777 | 0 — byte-identical |
| harness 119, LIGHT | 1,586 | 0 |

### The 5 failures, named and disposed of

| check | what it said |
|---|---|
| `0q live: all 46 required wording strings are present verbatim` | FAIL |
| `0q ann: all 46 required wording strings are present verbatim` | FAIL |
| `D2: EVERY implemented entry's line equals the allowed wording for its actual trigger (677/689)` | FAIL |
| `D3a: no entry left unmatched (12)` | FAIL — the 12 are exactly the `air_drop_on_infantry` entries |
| `HEADLINE (harness 93): the appended tooltip line is now ONE SHORT clause per ability …` | FAIL |

**One root cause, one stale pin.** `run_h93` carries a hand-kept mirror of `FOURTH.TRIGGER_TIP`. Its
`air_drop_on_infantry` value was still round 116's text *("… after a wait measured from that enemy's
velocity at the moment of contact: 0 s … 2 s …")*. That string is **byte-equal to the PRE-118
snapshot** (`docs/backups/round118/pre118_zz_test_deadly_onslaught.lua`), which proves the pin was
stale rather than the source being wrong; the shipped source says *"and casts immediately on that
evaluation - no delay at all"*. h93 is inside the section set that `H118_LIGHT` skips, so neither
round 117 nor 118 ever ran it.

**Disposition: stale pin, fixed in harness 119.** Nothing outside the air-drop family failed. There
is no regression from rounds 117/118.

### The floors the light cycle left behind

Four air-drop suite-boundary pins were `>=` floors, not values. Now exact (measured in the full run,
and proven stable across two runs):

| pin | was | now |
|---|---|---|
| h114 boundary (`pre115`) | `>= 200` | `== 4614` |
| h115 boundary (`pre116`) | `>= 200` | `== 4686` (light mode keeps its floor) |
| h116 boundary (`pre117`) | `>= 250` | `== 4702` (light mode keeps its floor) |
| h117 boundary (`pre118`) | `>= 250` | `== 4718` (light mode keeps its floor) |

The 17 `"the WHOLE harness-NN suite re-ran"` cumulative totals that a light run reports as skipped
were all evaluated in the full run and all passed.

---

## 2. Workbook v18

`docs/WH3_abilities_master_v18_2026-10-18.xlsx` (+ `.ods`), built by `tools/make_xlsx_v18.py` from
v17 and verified from disk by `tools/verify_xlsx_v18.py`. **v1-v17 byte-unchanged** (30 files; every
one predates v18 — md5s printed by the verifier).

### The 19 air-drop rows

Columns 19 (status reason) and 22 (trigger as implemented) rewritten to the SHIPPED rule:

```
candidate = ALIVE, number_of_men_alive() > AIR_DROP_MIN_MEN (10), centre gap READABLE
chosen    = the NEAREST valid candidate by the horizontal CENTRE distance
FIRE      = chosen's centre gap < AIR_DROP_CENTER_M (6.0 m)  -- on THAT evaluation
```

- **Kept:** the candidate rule (> 10 alive models, **no infantry filter**), `air_only` / `no_melee`,
  the self-centred cast on the OWNER, every fail-closed read, the 0.2 s fast pass with its 30 m near
  gate, `POLL_MS = 250`, the gates and the pre-cast re-check (which now re-measures the centre).
- **Gone from those rows:** every mention of the delay, the dwell, the velocity projection, the
  closing-rate/`reads:` logging, the short-crossing fallback and the edge measurement. The verifier
  scans **all 23 columns of all 19 rows** for 22 tokens (`delay`, `dwell`, `edge`, `frontage`,
  `velocity`, `proj`, `unit_distance`, every retired `AIR_DROP_*` name, `ad_pair`, …) and finds
  **0 hits**.

### Definitions

- The trigger-family glossary line for `air_drop_on_infantry` (row 69) is rewritten to the centre rule.
- **Sections 8-11** (prediction constants, moving-caster dials, the fourth dial, the path rule and
  derived frontage) get their round-114 retirement reason added to their titles.
- **Section 12** (edge rule + dwell), **section 13** (the dwell machinery) and **section 14** (the
  measured delay) are retitled **RETIRED**, each with one line of WHY. The history stays readable;
  nothing is deleted.
- **New section 15**: the rule in force in one line, the decision in order, why the centre and not a
  gap, the four constants (`AIR_DROP_CENTER_M = 6.0` is the only decision knob), the log lines, and a
  **retired list with one reason per block** — `AIR_DROP_EDGE_M`, `AIR_DROP_BOUND_M`,
  `AIR_DROP_DWELL_S` + `ad_pair` + the clock + the purge + `AIR_DROP_MIN_CONTACT_S`,
  `AIR_DROP_DWELL_MID_S` / `_SWING_S` + the cosine, the velocity rebuild + `reads:`, the four dials,
  the frontage + path test — plus a note that `AIR_DROP_CENTER_M` was retired in round 114 and came
  BACK in round 117, so nobody "retires" it again by reading the old sections.

### Numbers — the arithmetic, stated

| measure | count | how it was counted |
|---|---|---|
| inventory | **1,799** | Abilities sheet: 1,800 rows incl. header − 1 |
| IN-WHEEL | **1,141** | Status column, row count |
| EXCLUDED | **658** | Status column, row count; 418 spells + 204 army + 16 cataclysm + 1 quest + 15 boss-only + 4 illusion = 658 |
| 1,141 + 658 | **1,799** | ties to the inventory exactly |
| implemented keys | **742** | parsed from the shipped `ABILITIES` table |
| entries | **689** | `{ marker = … }` occurrences in that table |
| evaluators | **46** | `FOURTH.evaluators`; the family table's 46 families sum to 689 / 742 |
| IMPLEMENTED rows | **741** | each carries one distinct key; 741 + 1 = 742 |
| rows not implemented among the included | **400** | 1,141 − 741 (the older 399 subtracts keys from rows — both are stated on the sheet) |
| bombardment | **55** | 131 `wh_type_bombardment` rows → 58 unit-side → −3 army-bar = 55, all implemented |

**One genuine gap, named rather than smoothed:** `wh3_main_spell_slaanesh_slicing_shards_bound` (the
mod entry `slicing_shards`) is **implemented in the script and has no row anywhere in the 1,799-row
inventory** — not implemented, not excluded, absent. That is the 742nd key in the 741 + 1 arithmetic.
Also flagged, not fixed: the per-carrier-family block is a **key-level** count of an older vintage
(its columns sum to 1,143 and 638) and is not the same unit as 1,141 rows / 742 keys.

### Changelog

A v18 row records: rounds 117 and 118 shipped in **light mode** and are reconciled here; the rule
before and after; the 19 rows rewritten; the Definitions retirements; the full-suite totals
(4,777 / 0, and the pre-fix 5 with their single cause); the five pin fixes; the Numbers arithmetic;
and **both installed md5s** — round 117 `516b16aaa33d26abede8738c4447ffbe`, round 118
`2f215bc4c35845452103327fb62ba554`.

### One documentation bug found and fixed

`docs/WH3_round117_airdrop_centredist.md` and `docs/WH3_round118_airdrop_nodelay.md` both told the
reader to **raise** `AIR_DROP_CENTER_M` if the drop was early and **lower** it if late. That is
inverted: FIRE is `centre < bound`, so a **bigger** bound fires **earlier**. Both lines are corrected
in place (and marked as corrected at this pass), each doc now carries a "RECONCILED 2026-10-20"
footer, and the workbook's section 15 and Numbers line state the correct direction: lower
6.0 → 5.0 → 4.0 if still early, raise 6.0 → 7.0 if it never fires.

---

## 3. Decisions recorded (not re-litigable)

- **Bombardment: leave it as it is.** The user's words: *"I find it satisfying right now"*. Recorded
  in the tracker update block **and inline on all 36 implemented bombardment rows**
  (`enemy_ground_melee_infantry` 30 + `melee_skip_commanders` 6).
- **Hecleas review** (`docs/WH3_hecleas_mod_review.md`): the BATTLE AI claim resolves to a **weights
  table with no reusable ability scripting**; nothing was adopted. The user chose **not to pursue**
  the **friendly-fire veto** or the **reinforcement enumerator** at this time. Recorded in the
  tracker against the §3b friendly-fire block and in the sign-off decisions paragraph.

---

## 4. Artifacts

| file | md5 / note |
|---|---|
| `mod_source/script/battle/mod/zz_test_deadly_onslaught.lua` | `99a3d107986ea06efc956c0e5ea5fb76` — **unchanged** |
| `docs/WH3_auto_ability_annotated.lua` | `7a71e0d220fea0b4451ab5bf61ba752a` — unchanged |
| installed `data/zz_test_deadly_onslaught.pack` | `2f215bc4c35845452103327fb62ba554` — unchanged |
| `docs/WH3_abilities_master_v18_2026-10-18.xlsx` / `.ods` | new |
| `mod_source/releases/20261018_signoff_harness119/` | harness 119 + all four runs |
| `docs/WH3_ability_tracker.md` | three update paragraphs + the decisions + 19 + 36 row notes |
| `tools/make_xlsx_v18.py`, `tools/verify_xlsx_v18.py`, `tools/update_tracker_signoff.py` | the pass, re-runnable |

## 5. Still open

1. **`slicing_shards` has no inventory row** (see §2). The workbook's 1,799-row inventory is one row
   short of the mod's 742 keys. Adding it would move every headline count, so it is reported, not
   silently patched.
2. **The per-carrier-family Numbers block** is a key-level count of a pre-round-106 vintage and does
   not tie to the row-level headline. It needs one re-derivation as a single unit.
3. **Field test of round 118's rule** — the rule is harness-proven, not yet reported from a battle.
   If a drop is still early, lower `AIR_DROP_CENTER_M` (6.0 → 5.0 → 4.0); if it never fires, raise it.
4. **`docs/WH3_ability_database_master.md` still carries the round-108/113 air-drop line** ("within
   0.1 m of this unit's edge") in its §1.3 trigger-family table. It is generated by
   `tools/build_ability_database.py` from the tracker **plus a fresh game-data extraction**, so it was
   not hand-edited here; it needs one regeneration to pick the new rule up. Until then the workbook
   (Definitions section 15) and the tracker's air-drop rows are the authoritative statements.
