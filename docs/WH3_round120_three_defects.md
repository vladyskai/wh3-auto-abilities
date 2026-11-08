# Round 120 — the three defects the user found (2026-10-20)

Data and documentation only. **No mod source change, no rebuild**: the installed pack is
still `2f215bc4c35845452103327fb62ba554` (1,109,330 bytes, mtime 2026-10-18 22:30), verified
by md5 in this round.

---

## 1. Army-bar rows labelled IN-WHEEL

**Symptom.** The Status column said `IN-WHEEL` while the neighbouring status-reason column said
`skipped (round 106: army-bar ability (army_spec junction) - out of wheel scope)` and the
Implementation column said `SKIPPED (round 106)`. Two columns contradicting each other in the
same row.

**Rows moved out of the wheel — exactly two, both Thorsen's Thunderstorm:**

| v18 item # | v19 item # | Ability | Key |
|---|---|---|---|
| 1334 | 1334 | Thorsen's Thunderstorm | `wh3_dlc20_cataclysm_bound_thorsens_thunderstorm` |
| 1335 | 1335 | Thorsen's Thunderstorm | `wh3_dlc27_cataclysm_bound_thorsens_thunderstorm` |

Both are now `EXCLUDED`; the reason keeps its round-106 text and ends
`- wheel status corrected in round 120: army-bar abilities are outside the wheel by the user's own rule`.
(The v19 item numbers are unchanged because the added row sits at 1296.)

**Corrected in-wheel total:**

```
v18:  1,141 IN-WHEEL +   658 EXCLUDED = 1,799 rows
      - 2 army-bar rows corrected out of the wheel
      + 1 added row (item 2 below, in-wheel)
v19:  1,140 IN-WHEEL +   660 EXCLUDED = 1,800 rows
```

**Root cause, traced through the pipeline.** The Status column was **never derived from the
army-bar test**:

1. `tools/build_abilities_master_xlsx.py:590` computes `"IN-WHEEL" if in_wheel else "EXCLUDED"`
   with `in_wheel = src in IN_WHEEL_SRC` (`:568`), where `src` is `unit_abilities.source_type`.
   The IN-WHEEL rule it documents names the army-bar family **only** as `source_type = army`.
   The `army_spec` junction — `army_special_abilities_tables`, the table that actually makes an
   ability an **army-bar button** — was never consulted by the classifier.
2. Both Thorsen keys are `source_type = bound` (a bound spell), so the classifier put them
   IN-WHEEL. That is the "default": **anything not literally `source_type = army` is in-wheel**.
3. Round 106 found the `army_spec` junction by hand and wrote the skip through
   `tools/make_xlsx_v7.py`'s `SKIP_KEYS` loop (`:168-185`), which writes columns **19, 20, 21,
   22** and never writes or asserts column **18** — while `set_impl()` in the same file
   (`:144-156`) **asserts `column 18 == "IN-WHEEL"`** before it writes. There was no mirror
   assertion for skips, so a skip could be recorded against a row whose status was never
   re-derived.

**So it cannot recur:**

* `tools/audit_wheel_status.py` (new) — **G1** fails if any row reads IN-WHEEL while its own
  reason / implementation / trigger text names an army-bar / army_spec / army-ability /
  campaign-side-junction exclusion; **G2** fails if an IN-WHEEL row's reason is not one of the
  two legitimate forms (`carrier family:…` / `skipped …`) or if an EXCLUDED row names a trigger
  family; **G3** fails if the set of `army_spec`-junction rows that still read IN-WHEEL differs
  from the documented baseline **in either direction** (a fresh mislabel fails, and so does a
  silent fix that forgets to update the baseline).
* Red/green control run in this round: **v18 → 3 failures** (the two rows via G1/G3, plus
  item 1349's malformed reason via G2), **v19 → 0 failures**.

**What the same default could have mislabelled — counted, listed, NOT silently fixed.**
**17 further rows / 17 keys** are `army_spec` junction entries that still read IN-WHEEL:

| Ability | Key(s) | State |
|---|---|---|
| Warden's Cage | `wh2_dlc15_character_abilities_wardens_cage` | **IMPLEMENTED** |
| Greater Gate of Khorne | `wh3_main_cataclysm_khorne_greater_gate_of_khorne` | **IMPLEMENTED** |
| Merciw's Monstrous Regiment (2 rows) | `wh3_dlc20_…_merciws_monstrous_regiment`, `wh3_dlc27_…_merciws_monstrous_regiment` | **IMPLEMENTED** |
| Bubonic Broadside | `wh3_dlc29_army_abilities_pestilential_bombardment` | not implemented — round 107's own arithmetic already calls it an army-bar junction and subtracts it from the 55 |
| Ashes & Dust ×2, Dance of Despair ×2, Gehenna's Golden Globe ×2, Magma Storm ×2, Storm of Renewal ×2, Time Amok ×2 | the `wh3_dlc20_cataclysm_bound_*` / `wh3_dlc27_cataclysm_bound_*` pairs | not implemented |

They are **not** moved here on purpose: under the strict reading they are army-bar and out of
scope, but **4 of the 17 rows are implemented in the mod today**, so moving them puts implemented
abilities outside the wheel and implies removing them from the mod — a **roster decision, not a
data correction**. The consequence is stated instead: **1,140 − 17 = 1,123 IN-WHEEL,
660 + 17 = 677 EXCLUDED** under the strict reading. *Ruling needed.*

---

## 2. The orphan key

`wh3_main_spell_slaanesh_slicing_shards_bound` is implemented in the mod (`entry marker
"slicing_shards"`, the **second** of its two keys, line 3270 of the source) and had **no row
anywhere** in the 1,799-row inventory.

**Its real data, from the game tables (not copied from the twin):**

| field | value |
|---|---|
| name | Slicing Shards (`unit_abilities_onscreen_name_wh3_main_spell_slaanesh_slicing_shards`) |
| `unit_abilities.source_type` | `bound` |
| `unit_spec_abil` | `num_uses 1`, `recharge_time -1` → **0 s / no cooldown**, `target_intercept_range 200`, `effect_range 0`, wind-up 5 s, duration 9 s, target flags friends+enemies+ground |
| grant path | `uset_ability.tsv`: unit_set `wh3_main_sla_mon_keeper_of_secrets_0` (Keeper of Secrets) |
| implementation | `IMPLEMENTED` (it ships today, as the twin key of the same mod entry) |
| trigger family / text | `enemy_ground_melee_infantry` — identical to its twin, because the mod carries **ONE** evaluator for the entry |

Added in **both** places: the **tracker** (`§3b`, immediately after its twin) and the **workbook**
(item **1296**, immediately after its twin, with every Column A item number renumbered 1…1,800 so
the sequence stays clean).

**Systematic audit of every implemented key.**

* Join used: parse the mod's `local ABILITIES = { … }` table → each entry's `keys = { … }` list →
  flat set of distinct key strings = **742 keys over 689 entries**; against workbook
  `Abilities!C` (`Ability key(s)`), split on `;`, `.strip()`, exact string equality.
* **v18 result: 741 / 742 matched, 1 unmatched** — `wh3_main_spell_slaanesh_slicing_shards_bound`.
* **v19 result: 742 / 742 matched, 0 unmatched.** Reverse direction also clean: 742 rows read
  `IMPLEMENTED`, they carry 742 distinct keys, and **none** is absent from the mod.
* The database's own §1.6 now prints *"Tracker status and the mod's table agree exactly."*

---

## 3. The master database, regenerated with an air-drop assertion

`docs/WH3_ability_database_master.md`, regenerated from the current tracker + mod by
`tools/build_ability_database.py` (nothing hand-typed).

* **Size 1,065,800 bytes, 2,727 lines** (was 1,063,484 bytes / 2,728 lines).
* **Diff summary: 51 lines removed, 50 added** (one 2-line block collapsed). The substantive
  changes: the generated timestamp; **§1.1 inventory 1,800 → 1,801 rows / 1,799 → 1,800 distinct
  keys**; §1.2 status families (implemented 742 → 743 rows — the added row; skipped 68 → 66 —
  the two Thorsen rows are now `excluded`); §1.3 and §2 **air-drop line rewritten to the shipped
  round-118 rule**; the added `wh3_main_spell_slaanesh_slicing_shards_bound` line in §2; §1.6 now
  reports exact agreement with the mod instead of naming a disagreement.
  **Why the database says 1,801 rows where the workbook says 1,800:** the tracker carries
  `wh3_twa07_spell_bound_call_of_tor` on **two** rows (§3a and §3b — a pre-existing duplicate,
  left alone), and §1.6 names it; the workbook has carried one row per key since v1, which is
  what makes its 1,800 rows and its 1,800 distinct keys the same number.
* **The old air-drop line** (the user's complaint) read *"…is within 0.1 m of this unit's edge…"*
  (the round-117 edge rule). It now reads the shipped sentence, verbatim from
  `FOURTH.TRIGGER_TIP.air_drop_on_infantry`: *"…comes within 6 m of this unit's centre, and casts
  immediately on that evaluation - no delay at all - airborne where the ability requires it"*.
* `build_ability_database.py` gained a `FAM_DESC` entry for `air_drop_on_infantry`, so §2 states
  the rule in force (`AIR_DROP_CENTER_M = 6.0`, > 10 models, no delay/dwell/projection/edge
  measurement) instead of *"unknown - see the mod's own evaluator"*.

**The assertion step: `tools/verify_ability_database.py`** — fails (exit 1) on any air-drop
disagreement:

| gate | what it fails on |
|---|---|
| A1 | the mod's, the tracker's and the database's air-drop **key sets** are not the same 19 keys / 12 entries |
| A2 | §1.3's plain-English sentence ≠ the mod's `FOURTH.TRIGGER_TIP.air_drop_on_infantry`, verbatim |
| A3 | §2's "Plain English" ≠ that same string |
| A4 | any of the 19 per-key `Fires:` clauses does not carry that sentence |
| A5 | any air-drop line still carries retired machinery (`0.1 m`, `AIR_DROP_EDGE_M`, `AIR_DROP_DWELL*`, `AIR_DROP_DELAY*`, `AIR_DROP_*_LEAD`, `AIR_DROP_INHERIT`, frontage, `ad_pair`, velocity, cosine) **or** lacks the live 6 m / centre tokens |
| A6 | any of the 19 tracker rows is not `implemented (…)`, is not filed under `air_drop_on_infantry`, or its RULE-IN-FORCE prefix lacks `AIR_DROP_CENTER_M = 6.0` or still carries a retired token |
| A7 | the entry/key counts in §1.3 or §2 differ from the mod's own parse (12 / 19) |
| A8 | §2's family description does not state `AIR_DROP_CENTER_M = 6.0` |
| G1 | any mod key has no §2 line, or its §2 status is not `implemented` |
| G2 | §1.6 does not report exact agreement, or the inventory counts are stale |

Red/green control: against the **stale** database it failed with **109 failures** (every
air-drop line carried `0.1 m`/edge, the orphan key's line read `unknown`, the inventory read
1,800/1,799). Against the regenerated file: **0 failures**.

---

## 4. The per-carrier-family Numbers block

v18's block was an older **key-level** count (1,143 keys, 638 implemented) sitting above a
**row-level** headline (1,141 rows, 742 implemented) — it could not tie by construction, and a
footnote saying so still left a reader with two numbers in the same unit-looking column.

**Resolved by making it tie, not by relabelling it.** The block is re-derived from the workbook's
own rows, joined by exact key to `unit_abilities.source_type`, and every cell is asserted:

| carrier family | included rows | implemented rows |
|---|---:|---:|
| active | 923 | 639 |
| bound | 176 | 79 |
| rune | 12 | 10 |
| item | 12 | 5 |
| lord | 10 | 6 |
| character | 3 | 2 |
| unit | 3 | 1 |
| weapon | 1 | 0 |
| **total** | **1,140** (= row 12) | **742** (= row 13) |

The header cell now reads *"…- ROW-LEVEL count … it TIES to the headline (sum = 1,140 included,
742 implemented)"* and states what the pre-v19 block was and why it could not tie. The exclusion
block was re-counted in rows too: spell 418 + army-bar 206 + cataclysm 16 + quest 1 + boss-only
15 + illusion 4 = **660** (= row 11).

While in there, one row-level defect was fixed: workbook item 1349 (Warp Lightning Rod) carried a
**status string** in the Status-reason column instead of a carrier family — the only such row. It
now reads `carrier family: active …` with the round-108 note kept.

---

## 5. Assertions added / run in this round

| script | what it proves | result |
|---|---|---|
| `tools/audit_wheel_status.py` | no army-bar row reads IN-WHEEL; reason forms sane; the `army_spec` remainder is exactly the documented 17 | **v18 red (3), v19 green (0)** |
| `tools/verify_xlsx_v19.py` | 1,800 rows = 1,140 + 660; item numbers 1…1,800; 1,868 key strings over 1,800 distinct keys; the 2 corrected rows; the added row's own game data; the **742/742 join**; the Numbers cells and both block sums; autofilter covers every row; v19 title + changelog | green |
| `tools/verify_ability_database.py` | the air-drop gates A1–A8 + G1/G2 above | **stale red (109), regenerated green (0)** |
| `make_xlsx_v19.py` | every count is asserted while building (rows, status split, implemented rows/keys, one key per row, family sums, exclusion sums, the 17-row remainder, the 2 moved rows) | green |

**Files written:** `docs/WH3_abilities_master_v19_2026-10-20.xlsx` (+ `.ods` twin),
`docs/WH3_ability_database_master.md` (regenerated), `docs/WH3_ability_tracker.md` (edited),
`tools/round120_tracker.py`, `tools/make_xlsx_v19.py`, `tools/verify_xlsx_v19.py`,
`tools/audit_wheel_status.py`, `tools/verify_ability_database.py`.
**Backups:** `docs/backups/WH3_ability_tracker.md.bak_pre_v19`,
`docs/backups/WH3_ability_database_master.md.bak_pre_v19`.
**v1–v18 are byte-unchanged.**
