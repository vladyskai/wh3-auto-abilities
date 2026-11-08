# Round 115 — the air-drop trigger now WAITS: a 1-second dwell on the pair

2026-10-18 · source `mod_source/script/battle/mod/zz_test_deadly_onslaught.lua`
installed pack **`56ef53853b74e2ee9e07ac5e343ce78a`** (5 files, all byte-identical to source)
release `mod_source/releases/20261018_airdrop_dwell_harness115/`
spreadsheet `docs/WH3_abilities_master_v16_2026-10-18.xlsx` (v15 superseded, v1–v15 byte-unchanged)

---

## 1. The user's ruling

> "I mean the trigger fires too soon. So we need a delay of 1 second for the trigger."

Round 114 shipped an **instant** comparison: the moment the edge gap dropped under 0.10 m the drop left.
That is what "fires too soon" means in the log — the trigger LED the contact instead of waiting for it.
Round 115 makes the trigger WAIT: **a dwell, not a lead.**

## 2. The rule that ships

```
candidate = number_of_men_alive() > 0  AND  number_of_men_alive() > AIR_DROP_MIN_MEN (10)
valid     = that candidate's unit_distance(caster, enemy) is READABLE
chosen    = the NEAREST valid candidate by that distance
UNDER     = unit_distance(caster, chosen) < AIR_DROP_EDGE_M (0.10 m)
FIRE      = that PAIR has been CONTINUOUSLY UNDER for AIR_DROP_DWELL_S (1.0 s)
            or it separated after at least AIR_DROP_MIN_CONTACT_S (0.3 s) of contact
```

then the caster-side usage checks the row declares (`air_only`, `no_melee`), the self-centred cast on the
**OWNER**, and the pre-cast re-check (which now re-verifies the **dwell** as well as the gap and the models).

### The constants

| Constant | Ships as | Meaning |
| --- | --- | --- |
| `FOURTH.AIR_DROP_EDGE_M` | `0.1` m | the line: the edge-to-edge gap must be **below** this |
| `FOURTH.AIR_DROP_MIN_MEN` | `10` | a candidate needs **more** alive models than this |
| `FOURTH.AIR_DROP_NEAR_M` | `30` m | the fast pass runs while a valid enemy is this close |
| `FOURTH.AIR_DROP_FAST_S` | `0.2` s | the fast pass interval (unchanged) |
| **`FOURTH.AIR_DROP_DWELL_S`** | **`1.0` s** | **how long the pair must stay under the line** |
| **`FOURTH.AIR_DROP_MIN_CONTACT_S`** | **`0.3` s** | **the short-crossing floor (fallback)** |

### The dwell, in full

* **The pair, not the unit.** State is keyed by `(caster ui id, enemy ui id)`, nested as
  `FOURTH.ad_pair[caster][enemy]` — no composite string key anywhere in the file (the file's own
  number/text id pitfall). A row holds **one** timestamp: the poll tick the contact started on.
  No gap history, no closing rate, no velocity.
* **The first evaluation of a contact never fires.** It stamps the row and returns `nil`.
* **The clock is the poll's own `tick_count`** (one poll = `POLL_MS = 250 ms`). 1.0 s of dwell is the
  stamp plus **four further polls**. The 0.2 s fast pass adds **evaluations, not time** — it can fire
  the instant the poll's clock completes the dwell, and a missed poll can only make a pair wait
  *longer*, never fire early. No engine clock is read (`os.clock`'s meaning in this Lua state is
  unproven). Real-world effect: the drop lands between **1.00 s and 1.25 s** after contact.
* **A re-contact starts a FRESH dwell** — the old stamp is dropped, never inherited.
* **The row dies with the unit**: `drop_unit_by_ui_id` purges every pair row naming it, as caster
  (whole slot) or as enemy (that one row). The purge is reached through ONE named global
  (`zz_ad_dwell_purge`) because that routine is declared **above** the `local FOURTH` bag and the
  chunk sits at Lua's 200-local ceiling (verified: one extra `local` fails to compile).

## 3. The log lines, and exactly what triggers each

All lines carry the caster's ui id and the marker (`[1003] sky_junk_bomb …`).

| Line | Written when |
| --- | --- |
| `dwell started: under at gap %.2fm, waiting %.2fs (pair '<key>')` | the **first** evaluation that finds the pair under the line. It never casts. |
| `dwell: under %.2fs of %.2fs (gap %.2fm)` | every evaluation while the pair is under but the dwell is not yet met (0.25, 0.50, 0.75 …) |
| `dwell satisfied after %.2fs -> FIRING (gap %.2fm, pair '<key>')` | the evaluation that completes the dwell — the cast follows, then `-> FIRING (re-checked) (dwell 1.00s of 1.00s)` |
| `dwell cancelled: separated after %.2fs (gap %.2fm; the dwell is %.2fs and the short-crossing floor is %.2fs)` | the pair separated **before** the dwell **and** before the floor. **This is the tuning datum**: the time under in this line says whether the dwell is too long for the crossings being flown. |
| `short crossing: under for %.2fs (>= %.2fs) -> FIRING on separation (gap %.2fm, the dwell is %.2fs)` | the pair separated **after** the floor but before the dwell — the fallback fires on that same separation evaluation |
| `… -> SKIPPED at re-check (… gap_ok=… dwell=… dwell_ok=… short_cross=…)` | the pre-cast re-check found the models, the aliveness, the gap or the dwell evidence lapsed; the cast is not spent |

The older `nearest valid:… -> NOT YET / FIRING` lines are unchanged (change-gated, as before).

## 4. The short-crossing fallback, precisely

On the evaluation that first sees the gap back at or over 0.10 m:

* `under >= AIR_DROP_MIN_CONTACT_S` → **fire now**. The pre-cast re-check accepts a fallback fire
  although the gap is over the line **by construction** (the fire happens on the separation
  evaluation), and logs the measured gap plus `(short crossing: held 0.75s of 0.30s)`.
* `under < AIR_DROP_MIN_CONTACT_S` → **cancel**, and log the time under and the separation gap.

Nothing else can fire a short crossing: the fallback exists only on that transition, and the contact
row is consumed by it.

## 5. Harness 115

`harness115.lua` = the harness-112 base suite (4,492 checks) + harness 114's section 0 static pins +
**88 N/A slots** replacing harness 114's instant-fire worlds + the new round-115 section.

* **4,739 checks / 0 failures**, run twice, **byte-identical**.
* Worlds (each runs against BOTH the live and the annotated copy):
  * **A** a 1.00 s contact fires on the poll that completes it, with `dwell started` / `dwell: under 0.75s
    of 1.00s` / `dwell satisfied after 1.00s` / `-> FIRING (re-checked) (dwell 1.00s of 1.00s)`;
  * **B** 0.75 s of contact then a separation to 0.40 m: **fires through the fallback only**
    (`short crossing: under for 0.75s (>= 0.30s)`), zero `dwell satisfied`;
  * **C** 0.25 s of contact then a separation: **no fire**, only `dwell cancelled: separated after 0.25s
    (gap 0.40m …)`;
  * **D** cancel, then re-contact: `dwell started` twice, still holding at 0.75 s after the **re**-contact
    (an inherited stamp would have fired), fires at 1.00 s after it;
  * **E** the first evaluation (a fast tick) never fires, five fast ticks move the dwell by **nothing**,
    then the polls complete the same dwell and it fires once;
  * **F** the gap drifts to 0.30 m at the re-check: 0 casts, the skip line carries the fresh edge,
    `dwell=1.00s of 1.00s`, `dwell_ok=true`, `edge_ok=false`;
  * **G** the pair table is purged with the unit — the enemy's drop removes its row, the caster's drop
    removes its whole slot, and a re-contact with a second enemy stamps a fresh row;
  * **H** 5 fast ticks and 2 polls after the dwell fire cast **nothing** more, exactly one
    `-> FIRING (re-checked)` in the window, and past the guard it can fire **once** more;
  * **I** a grounded caster never fires an air-only row however long it sits there.
* Section-0 pins (BOTH files): the two constants once each; the four round-114 constants unchanged;
  the nested pair state with `{ first = tick_count }` and **no** `.. "|" ..`; the clock is
  `tick_count` and `AIR_DROP_FAST_S` is **not** in `ad_under`; the never-fires-first `return nil`
  comment; the fallback branch; the purge hook (1 attach + 1 call); the re-check's `dwell_ok` /
  `gap_ok` and `and men_ok and gap_ok and dwell_ok`; air_only / no_melee / self-cast / fail-closed;
  both timers registered and `POLL_MS = 250`; 12 entries / 689 markers; the new tooltip sentence.
  Live-only: `FOURTH.ad_tag(unit)` = **7** sites (the dwell event helper is the new one) and the five
  dwell literals verbatim.
* **Red control** (`H115_LIVE`/`H115_ANN` → `docs/backups/round115/pre115_*.lua`, the round-114 build):
  **59 failures** — 56 in the new section (every `0 …` pin and every A–I world that asserts a dwell
  behaviour) plus **3 designed text pins this round rebased** (the tooltip sentence in both copies and
  the `ad_tag` site count). No crash, no failure outside those two classes.
* **Designed supersessions:** harness 114's 88 instant-fire world slots answer N/A (the same 88 slots,
  count preserved — the rule they proved is re-proved dwell and all by the new section); round 107's
  three air-drop serialisation assertions (S2a/S2b/S3a) answer N/A through a renamed check call for the
  same reason (a same-marker repeat now needs a fresh dwell); harness 93's TIP map carries the new
  air-drop sentence.

## 6. Build and install

```
source script/…         778,144 bytes
five files              all MATCHES SOURCE: True  (sha256, in-memory pack)
round 114 content gates : OK
round 115 content gates : OK
built pack              md5 56ef53853b74e2ee9e07ac5e343ce78a
installed               md5 56ef53853b74e2ee9e07ac5e343ce78a   IDENTICAL True
independent reopen      of the INSTALLED pack: all five files byte-identical
zz_probe_dist.pack      left installed, md5 d4e67cfb8bc562c7d6f0ff742909c13d (untouched)
```

Runtime tokens grepped straight out of the **installed** pack (stored uncompressed): `dwell started:
under at gap `, `dwell satisfied after `, `dwell: under `, `dwell cancelled: separated after `, `short
crossing: under for `, `AIR_DROP_DWELL_S`, `AIR_DROP_MIN_CONTACT_S`, `zz_ad_dwell_purge`.

## 7. Spreadsheet v16

`docs/WH3_abilities_master_v16_2026-10-18.xlsx` (md5 `d942ed769df072deb92839e1abb5b87c`), re-opened from
disk and verified by `tools/verify_xlsx_v16.py`:

* **19 air-drop rows** (Abilities rows 819, 836–841, 862, 863, 898–900, 957, 1017, 1031–1033, 1121, 1137):
  column **19** carries the round-115 rule summary and column **22** the full evaluator text — both
  name `AIR_DROP_DWELL_S = 1.0 s`, `AIR_DROP_MIN_CONTACT_S = 0.3 s`, the dwell, the **short-crossing
  fallback**, the poll clock, the never-fires-first rule and the re-check; no row still says
  "round 114 – THE SIMPLE EDGE-GAP RULE".
* **Definitions**: section 12 retitled to round 115; new **section 13** — the two constants with tuning
  guidance, the pair state, the clock, the five dwell lines, the purge, and a round-115 tuning guide
  (four symptoms → which constant, in which order).
* **Changelog**: a **v16** row.
* **Numbers**: the count table is unchanged **by design** (742 implemented / 689 entries /
  `air_drop_on_infantry` 12 entries / 19 keys) and carries an explicit round-115 reconciliation note.
* Abilities sheet still **1,800 rows**; **v15** re-read and confirmed to still hold the round-114 text
  (19 air-drop rows, no `AIR_DROP_DWELL_S`). v1–v15 were never opened for writing.
* Tracker `docs/WH3_ability_tracker.md`: a round-115 update entry, the dwell clause on all 19 ability
  rows, and the `air_drop_on_infantry` family row rewritten with the new rule (history kept).

## 8. Retest plan — and what to send back for tuning

Arm an air-drop carrier and fly it over a 20-model block. The log now tells you, per contact, exactly
how long the pair held:

1. **Look for the pair.** `dwell started: under at gap 0.05m, waiting 1.00s` → then `dwell: under
   0.25s of 1.00s` … → `dwell satisfied after 1.00s -> FIRING`. That is the trigger **waiting** and
   then firing, which is what was asked for.
2. **If it still leaves too soon**, send me the `dwell satisfied after X.XXs` line — the number is the
   actual hold at the cast. Raise `AIR_DROP_DWELL_S` 1.0 → 1.5 → 2.0.
3. **If it now feels late** (the block is already past), send the same lines plus any `dwell cancelled:
   separated after X.XXs` you see. If most contacts cancel around 0.5–0.7 s, the dwell is simply
   longer than the crossings you get: lower `AIR_DROP_DWELL_S` 1.0 → 0.7 → 0.5 (keep it above
   `AIR_DROP_MIN_CONTACT_S`).
4. **If quick crossings are being missed entirely** (nothing fires as blocks sweep past), send the
   `dwell cancelled: separated after X.XXs (gap …)` lines — each one names the time it *did* hold, so
   the log says what floor would have caught it. Lower `AIR_DROP_MIN_CONTACT_S` 0.3 → 0.2 → 0.1.
5. **If the fallback fires when it should not**, send the `short crossing: under for X.XXs (>= 0.30s)`
   lines and raise `AIR_DROP_MIN_CONTACT_S` 0.3 → 0.5 → 0.75.
6. One constant per test, and note that `AIR_DROP_EDGE_M` (0.10 m) is still the line itself — it has
   not changed and should not be touched in this round.

What to send back, in one message: **the `dwell …` lines for the ability that misbehaved**, the unit's
ui id if the log shows several carriers, and whether the problem is "too soon" or "too late". Every
dwell line already carries the time under and the gap, so no extra probing is needed.

## 9. Files in the release

| File | Note |
| --- | --- |
| `round115_edit.py` | the whole source edit, applied to BOTH copies with exact-count anchors |
| `h115_section.lua` + `assemble115.py` → `harness115.lua` | the suite: harness-112 base + 114 section 0 + 88 N/A slots + the round-115 section |
| `build_and_install115.py` + `gates115_block.txt` | the pack builder: round-114 gates plus a round-115 gate block |
| `verify_installed115.py` | independent post-install check: re-opens the INSTALLED pack, compares all five files |
| `h115_run1.txt` / `h115_run2.txt` | two green runs (4,739 checks), byte-identical |
| `h115_red.txt` | the red control (round-114 build): 59 failures, all accounted for |
| `docs/backups/round115/pre115_live.lua` / `pre115_ann.lua` | the pre-edit snapshots (md5 `a503fff0e7c978724036481aacb643e7` / `0d106b10e0be9fe8e471ab0fffba8a65`) |
