# Round 105 — Tz'arkan on a low-health trigger; the other transforms skipped

Date: 2026-10-17 · Harness 105 · Installed pack md5 `a8fea1b2ee6292e5c07ada2c621fa900`

Two user rulings.

---

## 1. Tz'arkan — implemented

**User:** *"I think it might make sense to activate Tz'arkan when caster health is below 15%, don't you think?
Let's implement and test it."*

* **One entry (`marker: tzarkan`), five keys**: `wh2_dlc14_lord_abilities_tzarkan`, `_mp`, `_snikch`, `_spite`,
  `_spite_mp` — one badge, one arming switch, one back-off, exactly like the other multi-key entries.
* **New trigger family `health_below_15`** (`FOURTH.evaluate_tzarkan_low_health`). The exact rule:

  > the OWNER is **alive** (the poll's own gate), **not routing**, and its health — read only through
  > **`FOURTH.health_pct`**, the ONE 0-100 reader — is **strictly BELOW 15**; the cast is on the **OWNER ITSELF**
  > through the unit form (`perform_special_ability(key, owner)`) with the caster's controller re-fetched
  > **FRESH** that tick; **no range bound** is read or needed (a self cast has no distance).

  Never a raw `HealthPercent` read: that field answers a **0..1 fraction**, so `hp < 15` on it is true for every
  unit on the field (the round-103 failure). `FOURTH.health_pct` prefers `battle_unit:unary_hitpoints()`
  (fraction × 100) and only falls back to the context field, scaled the same way.
* **The in-flight gate applies automatically** (`ability.wind_up_s` from `cast_gate.wind_up_s`): the row declares
  **3.0 s** wind-up (**1.5 s** for the Snikch key), so after a cast the pair waits **wind-up + 2 s**. No charge
  gate (unlimited uses).
* **The exact percentage is logged at the decision AND at the pre-cast re-check**, and the re-check can skip:

  ```
  ATTEMPT tzarkan 'wh2_dlc14_lord_abilities_tzarkan' on '<type>' ui id <id> | reason: health 14.0% (BELOW the 15% line) - one-way transform, cast on SELF | armed=ON
    readiness tzarkan on ui id <id>: ...
    can_perform before      : true
    tzarkan pre-cast re-check: the caster is still below the line (alive=true, health=14.0% of BELOW 15%, no range bound - self cast) - firing
    perform_special_ability(key, unit) : ACCEPTED
  ```

  and when the unit died or was healed above the line inside the wind-up:

  ```
    tzarkan SKIPPED: the caster lapsed before the cast (alive=true, health=25.0%, the line is BELOW 15%, no range bound - self cast) - cast not spent
  ```

  (`alive=false` covers the death case; the health string is `?` when the read is unreadable, and an unreadable
  read does NOT block a cast the trigger already justified — the file's standing fail-open rule for an auxiliary
  read.)

**THE THRESHOLD IS DELIBERATE.** A transform is very likely **one-way**, and the 3 s wind-up can let a caster at
14% die before the transform resolves. 15% is the user's own number and is **one constant**
(`FOURTH.TZARKAN_PCT = 15`); raising it to 20 / 25% is a one-line change if field tests show deaths before the
transform completes.

**Counts:** 642 → **643 entries**, 682 → **687 keys**, 42 → **43 evaluators**.

---

## 2. The rest of the transforms — skipped by the user's decision

**User:** *"I see no point to automate Formless Horror, Transformation of the Dragon, Burrow and Surface. So we
skip them and mark them as skipped in the spreadsheet."*

All **12 keys** now carry exactly one status everywhere:
`skipped (user decision 2026-10-17: no automation wanted)`.

| # | Ability | Key(s) |
|---|---|---|
| 1–4 | Formless Horror (+ Changeling, + quest battle, + quest battle Changeling form) | `wh3_dlc24_lord_abilities_formless_horror`, `_changeling`, `_quest_battle`, `_quest_battle_changeling_form` |
| 5–10 | Transformation of the Dragon (Jade / Iron / Storm × dragon form / human form) | `wh3_dlc24_lord_abilities_jade_dragon_dragon_form`, `_human_form`; `wh3_main_lord_abilities_iron_dragon_dragon_form`, `_human_form`; `wh3_main_lord_abilities_storm_dragon_dragon_form`, `_human_form` |
| 11 | Burrow | `wh3_dlc27_unit_abilities_dread_maw_underground` |
| 12 | Surface | `wh3_dlc27_unit_abilities_dread_maw_surface` |

**Nothing was removed from the mod**: none of the 12 was ever in the `ABILITIES` table (the build asserts none of
the 12 key strings appears in the shipped script). The spreadsheet shows Implementation
**`SKIPPED (user decision)`** on those 12 rows and the new status value is in the Definitions vocabulary.

---

## 3. Harness 105

`harness105.lua` = harness 104 + one section (older harnesses never edited). The copy sits at Lua's 200-local
ceiling, so the section adds **zero** chunk locals (a global function only).

**GREEN:** `checks: 3702, failures: 0` → `HARNESS OK - all checks passed`.

| world | fixture | result |
|---|---|---|
| T1 | 14.0% health | fires exactly once; cast target **is the owner**; `health 14.0%` at the decision and `health=14.0%` at the re-check; the `HealthPercent` fallback never read |
| T2 | 16.0% health | silent (no ATTEMPT line) |
| T3 | 14.0% at the decision, 25.0% at the re-check | the cast is SKIPPED, with the real number logged |
| T4 | dead owner (0 men) at 10% | silent (the poll's alive gate; nothing attempted) |

Each world runs against the **live source AND the annotated copy**. Static pins: one `tzarkan` entry, five keys
inside it, the evaluator + map + tooltip wiring, `FOURTH.TZARKAN_PCT = 15`, no raw `HealthPercent` in the
evaluator, two `if FOURTH.tz_self then` blocks (cast handle + re-check), the five wind-ups in the in-flight
table, and the 12 skipped keys absent from the script.

**RED** (`H105_LIVE`/`H105_ANN` → `pre105_live.lua` / `pre105_ann.lua`): `checks: 3601, failures: 110`
= **48 baseline** (harness 104 itself shows 48 on this snapshot) increased by **53 designed count pins** (this
copy pins 643/687 and the 43-entry wording table; the snapshot has 642/682 and 42) + **9 Tz'arkan
discriminators** (T1a/b/c/d/e + T3b live; T1a/b/c annotated). Diffing the two red runs: **0 failures present in
harness 104's red run are absent here** — no regression elsewhere.

---

## 4. Build + install

`build_and_install105.py` (cloned from 104; round note + a 30-assertion gate block (18 statements, one looping over the 12 skipped keys); the five table-size gates re-pinned
642 → 643):

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
`a8fea1b2ee6292e5c07ada2c621fa900`, 1,043,113 bytes; tokens present inside it
(`trigger = "health_below_15"`, `FOURTH.TZARKAN_PCT = 15`, `function FOURTH.evaluate_tzarkan_low_health`,
`tzarkan pre-cast re-check`, `tzarkan SKIPPED: the caster lapsed`). `zz_probe_dist.pack` is still installed.

---

## 5. What to retest (Tz'arkan)

Field Malus Darkblade (or Snikch — either carries the key), arm the TZ badge, let him drop below 15% health.

1. **One cast** when the log reads `health 14.x% (BELOW the 15% line)` and the pre-cast line repeats the number;
   the unit should transform.
2. **No cast at 16% or above.**
3. If he **dies inside the wind-up** the log shows `tzarkan SKIPPED: the caster lapsed before the cast` and no
   cast is spent — designed behaviour. If it happens often, raise `FOURTH.TZARKAN_PCT` (one constant).
4. **A second cast cannot arrive before the first resolves**: the in-flight gate holds the pair for 5 s
   (3.5 s for the Snikch key).
