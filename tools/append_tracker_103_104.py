"""Append the round-103 / round-104 records (§10.5, §10.6) and the transform
inventory note (§10.7) to the tracker."""
import os

P = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_ability_tracker.md"
text = open(P, encoding="utf-8").read()
assert "### 10.5" not in text, "10.5 already present"

SEC = r"""
### 10.5 The firing-layer round — the charge gate and ONE health reader (round 103, 2026-10-17)

Two field failures, both ours, both fixed in the SHARED firing layer (no trigger, range, cast form or badge changed).

**A. NURGLING TIDE'S CHARGE LOOP — a multi-use pool the engine will not refuse.** The log (session lines
686,841-748,076) shows **55 `ATTEMPT nurgling_tide` lines, every one `ACCEPTED`, at a dead-even 2.0 s cadence**
(t=67 s to t=175 s) while the ability's own button read `selected_inactive` (greyed) at 74/120/157 s. The row says
`num_uses = 3`, `recharge_time = 90`, `shared_recharge_time = -1` — three independent 90 s charges. The engine answers
`can_perform = true` and ACCEPTS a cast on an EMPTY pool, so the 2 s guard re-spent the same three charges forever:
42 of the 55 accepted casts went into nothing, and the counter "reset to 3" when the charges came back at
157/159/161 s. Contrast in the same log: **Eye of Khorne** (`num_uses = 1`) was refused on its second attempt
("REJECTED (on cooldown) - further holds suppressed for 8s") — the engine's own refusal brakes single-use abilities
and only single-use abilities.

*Fix — `charge_gate.hold_s`.* A new table maps **every key in the mod with `num_uses > 1` (129 keys, generated from
`unit_spec_abil.tsv`) to its own `recharge_time`** (28/30/31/43/44/46/47/60/90/120/180 s). At load each `ABILITIES`
entry gets `ability.charge_s` = the max over its keys (single-use entries stay nil). After a successful cast the pair
gets `until_tick = tick_count + floor(charge_s * 1000 / POLL_MS)` (90 s = 360 ticks); until then it is not eligible,
and the wait is SILENT (one line when the use is spent: `charge gate <marker>: one use spent - the next attempt
waits Ns (the ability's own recharge_time)`). The deadline is purged in the one drop routine.

**The rule: an ability that carries more than one use is cast at most once per its own recharge period.** One use per
cycle means the pool is never drained and no cast is silently swallowed. Deliberately conservative — the 2nd and 3rd
charges stay banked. Residual risk, stated: a 7-use / 60 s row now fires once per 60 s. Not "burst `num_uses`" (that
reproduces the reported 3-2-1-3 loop) and not "read the charges" (there is no script-reachable uses/cooldown read;
`can_perform` is the value that lies here).

**B. EYE OF KHORNE ABOVE 20 % — `HealthPercent` is a 0..1 FRACTION.** Across 336 `eye_of_khorne target:` pick lines
the health values are **only 0 or 1** (138 x `health=0%`, 198 x `health=1%`, none in 2-19 %); one unit read "1 %" for
83 s while alive and in melee, then "0 %". `string.format("%.0f", 0..1)` produces exactly that. `unit_banner.twui.xml`
feeds the same context value into a `ContextFillBar` and tests it against **1**; `battle_unit:unary_hitpoints()` is
documented as a "unary fraction" where 0.75 = lost 25 %. So `hp < 20` was true for EVERY unit and the "below 20 %"
finisher never gated anything — the picker simply took the lowest-health enemy in range. The 20 % rule itself is the
game's own (`special_ability_to_invalid_target_flags_tables.tsv`: `invalid_target = health_above_20%` for this key).

*Fix — `FOURTH.health_pct(unit)`.* Returns **0-100**: prefers `unit:unary_hitpoints()` (fraction x100), falls back to
`HealthPercent` (0..1 -> x100; >1 used as-is; unreadable -> nil). **All eleven `HealthPercent` call sites** now route
through it (enemy finisher, ally-heal picks and their pre-cast re-checks, Ushoran/potion <=75 %, the winds tiebreak's
neighbour read); `enemy_health_pct` is a one-line wrapper, so caller code is unchanged. Consequence: the <=75 % heal
family now fires only when the unit really is at or below 75 % (it fires LESS often than before), and Eye of Khorne
cannot offer a >20 % unit at all.

**Proof — harness 103.** GREEN `checks: 3569, failures: 0`. Nine new worlds: W1 Nurgling Tide with `can_perform`
always true and every call accepted -> **1 fire in 120 polls, 2 by poll 370**, second use >= 360 ticks later, one
charge-gate line; W2 a 1-use ability is **not** gated (3 fires in 20 polls = the plain 2 s guard); W3 fraction
0.92/0.12 -> picks 0.12 and logs `health=12%`, never names the 92 % unit; W4 0.90/0.75 -> **silent** (the field
failure); W5/W6 fallback strings "0.85" -> 85 % silent, "0.08" -> 8 % fires; W7 legacy 0-100 fixtures unchanged;
W8/W9 Ushoran <=75 %: 0.90 silent, 0.40 fires. RED (pre-103 snapshot): `checks: 3495, failures: 44` — W1 fires 15
times in 120 polls and 47 in 370, W4/W5/W8 fire on 75-90 % units.

**Build/install 103:** script 672,866 bytes; all five ship files byte-identical to source; built == installed pack md5
**`dfec7ac14b296b68458a1f6e92c0d133`** (1,007,942 bytes). New tokens present in the installed pack: `charge_gate.until_tick`,
`function FOURTH.health_pct(unit)`, `unit:unary_hitpoints()`, `charge gate `.

**What this means for every implemented multi-use entry (the bookkeeping point):** all **129 multi-use keys** are now
one-cast-per-recharge-period. Nothing about their trigger, range or cast form changed. Single-use entries are
untouched. The <=75 % family (33 entries at the time) now obeys its real line; 13 of those entries were then made
ally-aware in round 104 (§10.6).

### 10.6 The in-flight gate and the ally-aware health arm (round 104, 2026-10-17)

**A. NURGLING TIDE, "it takes ~4 s to activate and the guard is only 2 s".** The row declares `wind_up_time = 3.0`
and has **no `phase_junc`/`phases` row at all** (0 of 2,731 phase-junction rows name it — it spawns, it has no
effect phases), so the order-to-effect window the engine declares is **3.0 s**. `perform_special_ability` **issues an
order** ("Issues an **order** to the units ... to perform the supplied special ability"), and the queued twin exists
because "Queued orders start when the current order completes" — the plain call does not queue, it REPLACES. A second
order arriving 2 s into a 3 s wind-up therefore replaces the first before its effect lands. The recharge arithmetic
(3 -> 2 -> 1 inside four seconds, returned at 157/159/161) proves three activations BEGAN; it cannot prove any effect
landed, and the previous round's reading that the recharge timing proves three completed casts is not supported.

*Fix — `cast_gate.wind_up_s`.* A new table carries **every key in the mod whose own row declares a wind-up (136 keys,
0.5-6.0 s)**, generated from `unit_spec_abil.tsv`. At load each entry gets `ability.wind_up_s` = max over its keys
(nil for the 518 keys with none). After a successful cast the pair is held for **`wind_up_s + 2 s`**
(`IN_FLIGHT_SETTLE_SECONDS`), never less than `GUARD_SECONDS`: Nurgling Tide **5 s**, a 5 s wind-up **7 s**, a 1 s
wind-up **3 s**. Silent while it holds; ONE log line per (unit, marker) per battle
(`in-flight gate <marker>: the cast needs Ns wind-up - the next attempt on this unit waits M s`). The 103 charge gate
stays and is the longer hold for Nurgling Tide (90 s). Deadline purged in the one drop routine.

**Why a timeout and not an observation:** there is still no script read of a cast's progress — no per-unit charges,
cooldown or active-effect read exists. The data-declared wind-up plus slack is the honest window.

*Proof — harness 104, world I1:* `death_frenzy` (`wind_up_time = 3.0`, `num_uses = 1`, so the charge gate cannot mask
it): pre-104 **3 fires in 19 polls** (ticks 1/9/17, 8-tick = 2 s gaps); this build **1 fire**, second at poll 21
(20-tick = 5 s gap).

**B. STAR OF AVELORN — it only ever checked the caster.** The row is a **ground-targeted group heal**
(`target_ground = true`, `target_ground_under_allies = true`, `effect_range 15 m`, `num_effected_friendly_units 3`,
`affect_self = true`, effect text "to self and allies in range"). It rode the health-only evaluator, which reads the
OWNER's health and casts on the owner — so it fired only when the caster herself was below 75 %, at her own feet.

*The rule now:* fire when **this unit OR a friendly unit inside the ability's own reach** is at or below 75 % health,
and choose the **LOWEST-health** qualifying unit. The reach is data-derived, never guessed: an **area** heal uses
`floor(effect_range x 0.70)` — Star of Avelorn **10 m** (of 15), Gulyas **24 m** (35), Salyak's Lullaby **24 m** (35),
Locus of Fecundity **38 m** (55); a **friend-targeted** heal uses `floor(target_intercept_range x 0.70)` through the
existing `ally_range_real` map — 60 -> **42 m**, 100 -> 70 m, 200 -> **140 m**. The cast follows the row's own
targeting: `target_ground_under_allies` -> **ground under the chosen ally**; `target_friends` -> **unit form on the
chosen ally**; a **self-centred aura** -> **the caster** (a hurt ally only arms the trigger). The owner's old arm is
unchanged (<= 75 %, no distance test). The chosen ally is re-checked immediately before the call (alive, still
<= 75 %, still in reach) and the cast is skipped with a logged reason if it lapsed; the log prints the chosen unit's
type, its health percentage and the real distance.

**Changed — 13 entries / 14 keys (ally-aware):**

| entry | trigger | reach used | cast |
|---|---|---|---|
| Star of Avelorn | `health_aura_ground` | 15 -> **10 m** aura | ground under the chosen ally |
| Gulyas | `health_aura_ground` | 35 -> **24 m** aura | ground under the chosen ally |
| Salyak's Lullaby | `health_aura_self` | 35 -> **24 m** aura | the caster |
| Locus of Fecundity | `health_aura_self` | 55 -> **38 m** aura | the caster |
| Berry Wine | `health_aura_ally` | 60 -> **42 m** | the chosen ally |
| Dreaming Ring I / II / III | `health_aura_ally` | 200 -> **140 m** | the chosen ally |
| Earth Blood (2 keys) | `health_aura_ally` | 200 -> **140 m** | the chosen ally |
| Fleshy Abundance | `health_aura_ally` | 200 -> **140 m** | the chosen ally |
| Regrowth | `health_aura_ally` | 200 -> **140 m** | the chosen ally |
| Radiant Gem of Hoeth | `health_aura_ally` | 200 -> **140 m** | the chosen ally |
| Trollguts | `health_aura_ally` | 200 -> **140 m** | the chosen ally |

**Deliberately left owner-only — 20 entries, with reasons:**

| entries | reason |
|---|---|
| Ghoul King of Ushoran, Blood Chalice, Bugman's XXXXXX, Hieratic Jar, Immortal Will, Invocation of Nehek, Necroparasites, Potion of Charoi, Potion of Healing, Regenerating Flesh, Skalm, Skar's Kraken-Killer (12) | the game's effect text says **(to self)** — a self-only heal |
| Mantra of Invigoration (`protection_prayer`) | reaches allies, but `invalid_target = unit_is_not_tiger_warrior`; no Tiger Warrior key list |
| Blood Chalice of Bathori | reaches allies, but `invalid_target = unit_is_not_commander_class`; a commander list is derivable (`FOURTH.commander_keys`) but not wired this round |
| Breath of Darkness + Upgraded (2) | reach allies, but `invalid_target = living_unit` — recipient must be undead; no undead key list |
| Necrotic Phylactery, Pestilent Regeneration, Saint Annushka's Finger Bone (3) | reach allies but `effect_range = 0` and no target flags — no measurable radius |
| Scroll of Power | a **recharge buff**, not a heal — an ally's health is the wrong trigger |

**Entry arithmetic (exact).** Entries stay **642**, keys **682** (`ushoran_health` **33 -> 20**; new
`health_aura_ground` **2**, `health_aura_self` **2**, `health_aura_ally` **9**: 20 + 13 = 33). `ally_range_real`
fields **32 -> 41**; new `aura_real` fields **4** (Star of Avelorn 15, Gulyas 35, Salyak's Lullaby 35, Locus of
Fecundity 55 — the raw radii the 70 % is taken from). Evaluators **39 -> 42**.

**Proof — harness 104.** GREEN `checks: 3650, failures: 0`. New worlds: I1 (above), I2 (Nurgling Tide is in both
tables — the 90 s charge dominates), S1 (Star fires for a 60 % ally at 7 m, ground cast at the ally's position),
S2 (nothing hurt -> silent), S3 (60 % ally at 12 m, outside the 10 m aura -> silent), S4 (caster at 60 %, allies
fine -> still fires at her own feet), S5 (owner 40 % beats ally 60 % -> cast at the caster), S6 (Gulyas fires at a
55 % ally at 20 m inside its 24 m aura), S7 (Gulyas silent at 30 m), S8 (Salyak's Lullaby arms on a 50 % ally at
10 m but casts on the CASTER), S9 (Berry Wine casts ON the ally), S10 (a routing ally is never offered), S11 (a
chosen ally that drifts from 7 m to 15 m is re-checked and the cast is skipped, with the real numbers logged).
RED (pre-104 = the round-103 build): `checks: 3563, failures: 74` = 60 baseline pins + 14 discriminators (I1's
three rows, S1a-d, S4a-b, S5, S6, S8a-c, S9a-b, S11b).

**Build/install 104:** script 701,943 bytes; all five ship files byte-identical to source; built == installed pack md5
**`1d7c199208d3892881fb6dea2adfbfac`** (1,037,019 bytes). New tokens present in the installed pack:
`local cast_gate = {`, `in-flight gate `, `function FOURTH.evaluate_health_aura_ground`, `ally-ground cast`,
`FOURTH.ah_chosen`.

**Spreadsheet:** `docs/WH3_abilities_master_v5_2026-10-17.xlsx` (+ `.ods`) — **v5 supersedes v4; v1-v4 unchanged**.
The 14 rows of the 13 changed entries carry their new trigger family and trigger text; the 20 owner-only rows carry
their reason; every implemented row that carries a charge or wind-up gate now says so in its Trigger (as implemented)
text; the Definitions glossary carries the three new health-aura evaluators and a new GATES section; the Numbers
sheet is re-counted; the Changelog has a v5 row.

### 10.7 Transform active abilities — the game-data inventory (2026-10-17)

The earlier classification carried **11** abilities as `excluded (impossible: no transform/shapechange support)`.
That list was built from ability NAMES + effect text, and it is **not the transform population**: it holds **10 real
transforms** plus **Transformation of Kadon**, which the game's own data marks as a **summon** (see below), and it
omits **7 further transform keys** that sit under other statuses. Re-derived from the game's own tables
(`unit_spec_abil.tsv` `spawn_is_transformation` + `spawn_shares_health_and_fatigue`, and `unit_abilities.type =
wh_type_transform`), the population is **17 active keys / 5 names**:

| # | Ability | Key | Tracker status |
|---|---|---|---|
| 1 | Tz'arkan | `wh2_dlc14_lord_abilities_tzarkan` | `excluded (impossible: no transform/shapechange support)` |
| 2 | Tz'arkan (MP) | `wh2_dlc14_lord_abilities_tzarkan_mp` | same |
| 3 | Tz'arkan (Snikch) | `wh2_dlc14_lord_abilities_tzarkan_snikch` | same |
| 4 | Tz'arkan (spite form) | `wh2_dlc14_lord_abilities_tzarkan_spite` | same |
| 5 | Tz'arkan (spite form, MP) | `wh2_dlc14_lord_abilities_tzarkan_spite_mp` | same |
| 6 | Formless Horror | `wh3_dlc24_lord_abilities_formless_horror` | `skipped (revisit)` |
| 7 | Formless Horror (Changeling) | `wh3_dlc24_lord_abilities_formless_horror_changeling` | `excluded (impossible: ...)` |
| 8 | Formless Horror (quest battle) | `wh3_dlc24_lord_abilities_formless_horror_quest_battle` | `skipped (revisit)` |
| 9 | Formless Horror (quest battle, Changeling form) | `wh3_dlc24_lord_abilities_formless_horror_quest_battle_changeling_form` | `excluded (impossible: ...)` |
| 10 | Transformation of the Dragon (Jade, dragon form) | `wh3_dlc24_lord_abilities_jade_dragon_dragon_form` | `skipped (revisit)` |
| 11 | Transformation of the Dragon (Jade, human form) | `wh3_dlc24_lord_abilities_jade_dragon_human_form` | `excluded (impossible: ...)` |
| 12 | Transformation of the Dragon (Iron, dragon form) | `wh3_main_lord_abilities_iron_dragon_dragon_form` | `skipped (revisit)` |
| 13 | Transformation of the Dragon (Iron, human form) | `wh3_main_lord_abilities_iron_dragon_human_form` | `excluded (impossible: ...)` |
| 14 | Transformation of the Dragon (Storm, dragon form) | `wh3_main_lord_abilities_storm_dragon_dragon_form` | `skipped (revisit)` |
| 15 | Transformation of the Dragon (Storm, human form) | `wh3_main_lord_abilities_storm_dragon_human_form` | `excluded (impossible: ...)` |
| 16 | Burrow | `wh3_dlc27_unit_abilities_dread_maw_underground` | `excluded (auto: summon)` -> corrected in this round to a TRANSFORM |
| 17 | Surface | `wh3_dlc27_unit_abilities_dread_maw_surface` | `excluded (auto: summon)` -> corrected in this round to a TRANSFORM |

* **All 17 are IN-WHEEL and NONE is implemented** (verified against the mod's 682 keys). There is therefore **no
  transform implemented as a summon**.
* **Transformation of Kadon** (`wh3_dlc27_spell_bound_transformation_of_kadon`, implemented in round 102 on
  `enemy_ground_melee`) was re-checked against the data: `spawn_is_transformation = false`,
  `spawn_shares_health_and_fatigue = false`, `unit_abilities.type = wh_type_summon_unit`, and it spawns a generic
  `wh3_main_ogr_feral_manticore_summoned` unrelated to the caster. **It is a real summon, not a transform** — the
  name is lore, not machinery. **No reclassification is needed**, and the earlier 11-list was wrong to include it.
* **Two engine-typed transforms do NOT replace the unit and are excluded from the 17:** **Mist Form**
  (`wh3_dlc29_lord_abilities_mist_form`) and **Shadowstrider** (`wh3_dlc29_lord_abilities_warp_step`) carry
  `unit_abilities.type = wh_type_transform` but have **no `spawned_unit` and no spawn flag** — they are model-state /
  movement effects, not unit swaps. The passive `wh2_dlc14_lord_passive_tzarkan` carries the flag too but is passive.
* The full list with signals, wheel status and implementation status is the **Transforms** sheet of
  `docs/WH3_abilities_master_v5_2026-10-17.xlsx`.
"""

open(P, "w", encoding="utf-8", newline="").write(text.rstrip("\n") + "\n" + SEC)
print("appended", len(SEC), "chars")
