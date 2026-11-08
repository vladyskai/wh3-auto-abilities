# Round 105 — Tz'arkan on a low-health trigger, and the transform skips

Date: 2026-10-17 · Harness 105 · Installed pack md5 `a8fea1b2ee6292e5c07ada2c621fa900`

Two user rulings in one round. Nothing was removed from the mod.

---

## 1. Tz'arkan — implemented on a new low-health trigger

### 1.1 The user's rule

> "I think it might make sense to activate Tz'arkan when caster health is below 15%, don't you think? Let's
> implement and test it."

### 1.2 What the game's own data declares (all five keys)

`unit_spec_abil.tsv` / `unit_abilities.tsv`:

| key | wind_up_time | num_uses | recharge | target | type |
|---|---|---|---|---|---|
| `wh2_dlc14_lord_abilities_tzarkan` | 3.0 s | -1 (unlimited) | 0 | self (per the row's "affects self") | `wh_type_transform` |
| `…_tzarkan_mp` | 3.0 s | -1 | 0 | self | `wh_type_transform` |
| `…_tzarkan_snikch` | **1.5 s** | -1 | 0 | self | `wh_type_augment` (spawn flag says transform) |
| `…_tzarkan_spite` | 3.0 s | -1 | 0 | self | `wh_type_transform` |
| `…_tzarkan_spite_mp` | 3.0 s | -1 | 0 | self | `wh_type_transform` |

Each spawns the caster's transformed form (`wh2_dlc14_def_cha_malus_darkblade_tzarkan_0/1`,
`wh2_dlc14_skv_cha_deathmaster_snikch_tzarkan_0`). Unlimited uses, no cooldown → **no charge gate**; a declared
wind-up → **the in-flight gate applies**.

### 1.3 The trigger, exactly

**One entry** (`marker: tzarkan`) carries all **five** keys; **one new trigger family**, `health_below_15`
(`FOURTH.evaluate_tzarkan_low_health`):

> the OWNER is **alive** (the poll's own gate), **not routing**, and its health — read ONLY through
> **`FOURTH.health_pct`** (the ONE reader: `battle_unit:unary_hitpoints()` × 100, context fallback scaled the
> same way; **0-100**, never a raw `HealthPercent`, which answers a 0..1 fraction) — is **strictly BELOW 15**;
> the cast is on the **OWNER ITSELF** through the unit form with the caster's controller re-fetched **FRESH**
> that tick; there is **no range bound** (a self cast has no distance).

Attempt reason (logged on the ATTEMPT line):

```
health 14.0% (BELOW the 15% line) - one-way transform, cast on SELF
```

Pre-cast re-check (immediately before the call, same tick):

```
  tzarkan pre-cast re-check: the caster is still below the line (alive=true, health=14.0% of BELOW 15%, no range bound - self cast) - firing
```

Skip when the unit died or rose to/above the line inside the wind-up:

```
  tzarkan SKIPPED: the caster lapsed before the cast (alive=true, health=25.0%, the line is BELOW 15%, no range bound - self cast) - cast not spent
```

An **unreadable** health read does not block a cast the trigger already justified (the file's standing fail-open
rule for an auxiliary read); the log prints `health=?` in that case.

### 1.4 The gates

* **In-flight gate** (round 104) applies automatically: `cast_gate.wind_up_s` now lists the five keys
  (3 s on four, **1.5 s** on Snikch), so after a successful cast the pair waits **wind-up + 2 s**
  (5 s / 3.5 s). One log line per pair per battle.
* **No charge gate**: `num_uses = -1` (unlimited), so `charge_gate.hold_s` has no entry for these keys.
* **The 2 s guard** is the floor, as for every entry.

### 1.5 The wind-up risk, stated deliberately

A transform is very likely **one-way**, and the 3 s wind-up can let a caster at 14% die before the transform
resolves. **15% is the user's own number** and is **one constant** — `FOURTH.TZARKAN_PCT = 15`. Raising it to
20 / 25% is a one-line change if field tests show deaths inside the wind-up. This is written in the code
comment, the release note and the tracker row.

### 1.6 Entry arithmetic

642 → **643 entries** (one added), 682 → **687 keys** (five added), 42 → **43 evaluators** (one added).
The five keys were already IN-WHEEL, so the wheel count is unchanged; the spreadsheet moves 5 rows from
NOT IMPLEMENTED to IMPLEMENTED (682 → 687 implemented, 459 → 454 not implemented).

---

## 2. The other 12 transform keys — skipped by the user's decision

> "I see no point to automate Formless Horror, Transformation of the Dragon, Burrow and Surface. So we skip them
> and mark them as skipped in the spreadsheet."

Unified status, everywhere:
**`skipped (user decision 2026-10-17: no automation wanted)`**

| # | Ability | Key |
|---|---|---|
| 1 | Formless Horror | `wh3_dlc24_lord_abilities_formless_horror` |
| 2 | Formless Horror (Changeling) | `wh3_dlc24_lord_abilities_formless_horror_changeling` |
| 3 | Formless Horror (quest battle) | `wh3_dlc24_lord_abilities_formless_horror_quest_battle` |
| 4 | Formless Horror (quest battle, Changeling form) | `wh3_dlc24_lord_abilities_formless_horror_quest_battle_changeling_form` |
| 5 | Transformation of the Dragon (Jade, dragon form) | `wh3_dlc24_lord_abilities_jade_dragon_dragon_form` |
| 6 | Transformation of the Dragon (Jade, human form) | `wh3_dlc24_lord_abilities_jade_dragon_human_form` |
| 7 | Transformation of the Dragon (Iron, dragon form) | `wh3_main_lord_abilities_iron_dragon_dragon_form` |
| 8 | Transformation of the Dragon (Iron, human form) | `wh3_main_lord_abilities_iron_dragon_human_form` |
| 9 | Transformation of the Dragon (Storm, dragon form) | `wh3_main_lord_abilities_storm_dragon_dragon_form` |
| 10 | Transformation of the Dragon (Storm, human form) | `wh3_main_lord_abilities_storm_dragon_human_form` |
| 11 | Burrow | `wh3_dlc27_unit_abilities_dread_maw_underground` |
| 12 | Surface | `wh3_dlc27_unit_abilities_dread_maw_surface` |

* In the tracker this replaces the mixed set that was there (`skipped (revisit)` for the dragon-form and
  Formless-Horror base keys, `excluded (impossible: no transform/shapechange support)` for the human/Changeling
  keys, `excluded (auto: summon)` for Burrow and Surface) — the earlier notes stay as history, the status cell is
  the new one.
* In the spreadsheet: Implementation **`SKIPPED (user decision)`**, Status reason the same string, trigger
  columns `-`, and the new value is in the **Definitions vocabulary** (section 2).
* **Nothing was removed from the mod**: none of the 12 keys was ever in the `ABILITIES` table, and the round's
  build gate asserts none of the 12 key strings appears in the shipped script.

---

## 3. Harness 105

`harness105.lua` = harness 104 + one section (older harnesses never edited). The chunk sits at Lua's 200-local
ceiling, so the section adds **zero** chunk locals (a global function, `function run_h105()`).

**GREEN:** `checks: 3702, failures: 0` → `HARNESS OK - all checks passed`.

| world | fixture | result |
|---|---|---|
| T1 | 14.0% health | fires exactly once; the cast target **is the owner**; `health 14.0%` at the decision + `health=14.0%` at the re-check; `HealthPercent` fallback never read |
| T2 | 16.0% health | silent, no ATTEMPT line |
| T3 | 14.0% at the decision, 25.0% at the re-check | cast SKIPPED, the real number logged |
| T4 | dead owner (0 men), 10% | silent; nothing attempted |

Each world runs against BOTH the live source and the annotated copy. The static pins (section `0e`) assert the
entry shape (one entry, five keys), the evaluator + map + tooltip wiring, `FOURTH.TZARKAN_PCT = 15`, the ONE
reader (no raw `HealthPercent` inside the evaluator), the two `if FOURTH.tz_self then` blocks (cast handle +
re-check), the five wind-ups in the in-flight table, and the 12 skipped keys' absence.

**RED** (`H105_LIVE`/`H105_ANN` → `pre105_live.lua` / `pre105_ann.lua`, byte-identical to the shipped 104 build):

```
harness 104 on the same snapshot : checks 3563, failures  48   (baseline)
harness 105 on the same snapshot : checks 3601, failures 110
110 = 48 class-baseline + 53 designed count pins + 9 Tz'arkan discriminators
discriminators: T1a,T1b,T1c,T1d,T1e,T3b [live] + T1a,T1b,T1c [annotated]
```

The count pins are this round's copy pinning **643 / 687** and the **43**-entry wording table while the snapshot
is 642 / 682 / 42. Diffing the FAIL-label sets of the two red runs: **0 labels present in harness 104's red run
are absent from harness 105's** — no behavioural regression anywhere else.

---

## 4. Build + install

`mod_source\releases\20261017_tzarkan_harness105\build_and_install105.py` (cloned from 104: round note + a
30-assertion gate block - 18 statements, one looping over the 12 skipped keys - plus the five table-size gates
re-pinned 642 → 643):

```
script/battle/mod/zz_test_deadly_onslaught.lua   708037 bytes  MATCHES SOURCE: True
ui/templates/zz_auto_badge.twui.xml                2864 bytes  MATCHES SOURCE: True
ui/zz_auto/blank.png                                 69 bytes  MATCHES SOURCE: True
ui/zz_auto/auto_badge.png                           252 bytes  MATCHES SOURCE: True
ui/common ui/special_ability_tooltip.twui.xml    331235 bytes  MATCHES SOURCE: True
built pack   md5 a8fea1b2ee6292e5c07ada2c621fa900
installed    md5 a8fea1b2ee6292e5c07ada2c621fa900
IDENTICAL    True
```

Installed artifact re-checked in the game folder: `data\zz_test_deadly_onslaught.pack` md5
`a8fea1b2ee6292e5c07ada2c621fa900`, 1,043,113 bytes; the new tokens are present inside it. `zz_probe_dist.pack`
is still installed.

---

## 5. Bookkeeping

* **Tracker** (`docs\WH3_ability_tracker.md`): the five Tz'arkan rows are `implemented (health_below_15: below
  15% self)` with the full rule text; the 12 transform keys carry the unified status everywhere they appear
  (§3a rows, the §10.7 inventory table, and the decision paragraphs, which keep the earlier "skip for now" as
  history and add the FINAL ruling); the legend gains the two new status strings; new **§10.8** records the round.
* **Spreadsheet**: `docs\WH3_abilities_master_v6_2026-10-17.xlsx` (+ `.ods`) — **v6 supersedes v5; v1-v5
  byte-unchanged** (md5s asserted). 5 rows IMPLEMENTED on `health_below_15`; 12 rows `SKIPPED (user decision)`;
  Definitions vocabulary + glossary (43 evaluators, TOTAL 643 / 687); Numbers re-counted (implemented 687, not
  implemented 454, in-wheel 1,141 unchanged); Changelog v6 row; Transforms sheet 5 implemented / 12 skipped.
  Verified by RE-OPENING the file: the only changed Abilities rows are the 17 targets, and every count
  reconciles.

---

## 6. What to retest (Tz'arkan)

Field Malus Darkblade (or Snikch — either carries the key), arm the TZ badge, let him drop below 15% health.

1. **One cast** when the log reads `health 14.x% (BELOW the 15% line)` and the pre-cast line repeats the number;
   the unit should transform.
2. **No cast at 16% or above.**
3. If he **dies inside the wind-up**, the log shows `tzarkan SKIPPED: the caster lapsed before the cast` and no
   cast is spent — designed behaviour; raise `FOURTH.TZARKAN_PCT` if it happens often.
4. **A second cast cannot arrive before the first resolves** (in-flight gate: 5 s, 3.5 s on the Snikch key).

---

## 7. Follow-ups not done here

* The 12 skipped transforms need no follow-up unless the user reopens them.
* The readable database master (`docs\WH3_ability_database_master.md`) is regenerated from the tracker by
  `tools\build_ability_database.py`; run it after any tracker status change if the HTML/MD viewer is being read.
