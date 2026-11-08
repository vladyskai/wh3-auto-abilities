# Diagnosis: two field failures — Nurgling Tide charge loop, Eye of Khorne above 20 %

Date: 2026-10-17 · Build: harness 103 · Installed pack md5 `dfec7ac14b296b68458a1f6e92c0d133`
Log analysed: `…\Total War WARHAMMER III\zz_test_deadly_onslaught_log.txt` (759,739 lines; heartbeat
`hb t=`, `tick N |`, `scan done:` / `INVENTORY` noise excluded from every count below).
The two battles: Nurgling Tide = session lines **686,841–748,076**; Eye of Khorne = session
**748,076–754,188**.

## 0. Verdict

| # | Symptom | Cause | Ours? | Fixed |
|---|---------|-------|-------|-------|
| 1 | Nurgling Tide's counter runs 3 → 2 → 1, then resets to 3, in a loop | **Ours.** The engine answers `can_perform = true` while a multi-USE pool is EMPTY and still ACCEPTS the call, so the 2 s guard re-spent the same 3 charges forever; the 3 uses refill 90 s after each was spent and were immediately re-spent. | yes | yes — charge gate |
| 2 | Eye of Khorne cast on a unit far above 20 % health | **Ours.** `HealthPercent` returns a **fraction 0..1**, not a percentage, so `hp < 20` was true for every unit and the picker always offered the lowest-health enemy regardless of health. | yes | yes — one health reader |

Nothing in either failure required a change to the trigger, the range rule, the cast form or the
badge layer.

---

# 1. Nurgling Tide — the charge loop

## 1.1 What the user reported

> "I tested Nurgling Tide and it started the ability, the counter went from 3 to 2 to 1, and then
> reset to 3 again. Like that in a loop."

## 1.2 What the log shows

The mod attempted the ability **55 times, at a dead-even 2.0 s cadence, from t=67 s to t=175 s**
(the moment the battle ended), and **every single attempt was accepted**:

```
702039: ATTEMPT nurgling_tide 'wh3_main_lord_abilities_nurgling_tide' on
        'wh3_main_nur_cha_ku_gath_plaguefather_0' ui id 1001 | reason: the caster itself is in
        melee (self summon - cast on SELF, no range bound) | armed=ON
702040:   can_perform before      : true
702041:   nurgling_tide pre-cast re-check: the caster is still in melee (alive=true melee=true,
        no range bound - self cast) - firing
702042:   perform_special_ability(key, unit) : ACCEPTED
702048: command: 'Special Ability' issued for 'wh3_main_lord_abilities_nurgling_tide'
```

Measured over the session:

* 55 `ATTEMPT nurgling_tide` lines; 55 blocks ending in `ACCEPTED`; **0** `REJECTED` / `on cooldown`
  lines for this ability in the whole file.
* Every inter-attempt gap is exactly **2.0 s** (`unique deltas: [2.0]`) — that is the mod's
  `GUARD_SECONDS = 2`, i.e. the ability fired as fast as the mod's own guard allows.
* Cast times: 67, 69, 71, 73, … 173, 175 s.

The ability's own button, meanwhile, said it was **not usable**:

```
705902 (t=82 s): INVENTORY button_ability3: visible=true pos=(194,947) …
        state='selected_inactive' key='wh3_main_lord_abilities_nurgling_tide'
```

`selected_inactive` = greyed. Right after the third cast (71 s) the slot reads greyed at **t=74 s**,
is greyed again at t=120 s and t=157 s, and only at **t=167 s** does it read `active` — for one
second, after which the mod fires again and it is greyed at 168 s. (Between t=99 and t=156 the slot
belongs to another ability, because the selected unit changed, so the greyed state is observable at
74/120/157 s rather than every second.) So: **42 of the 55 accepted casts (t=73…155 s) went into an
empty pool**, and the button said so whenever it was on screen.

## 1.3 What the ability's data says

`%LOCALAPPDATA%\Temp\wh3\unit_spec_abil.tsv`, key `wh3_main_lord_abilities_nurgling_tide`:

```
num_uses           = 3
recharge_time      = 90.0000
initial_recharge   = 0.0000
active_time        = 10.0000
wind_up_time       = 3.0000
shared_recharge_time = -1.0000
affect_self        = true        (no target flags at all, effect_range 0.0000)
spawned_unit       = wh3_main_nur_inf_nurglings_summoned_0
```

So: 3 uses, each recharging **90 s after it is spent** (independent per use — `shared_recharge_time`
is -1). That matches the button exactly: spent at 67/69/71 s → the three uses came back at
157/159/161 s, which is why "the counter reset to 3" and then ran down again.

## 1.4 Why it loops

1. The evaluator (`self_summon_melee`) is true on every poll — the caster is in melee.
2. `can_perform_special_ability` answers **true** even with an empty multi-use pool, and the engine
   **accepts** the call (`ACCEPTED`, no error). The mod has no other readiness read
   (there is no per-unit cooldown/uses API — established in earlier rounds).
3. The only brake left is the 2 s guard, so it fires every 2 s forever.
4. Every 90 s each spent use recharges, and the mod spends it within 2 s of it appearing.
   Net effect for the player: 3 → 2 → 1 in four seconds, 86 s of invisible no-op casts, then a
   "reset to 3" and the same thing again. Exactly the reported loop.

### Correction to the initial hypothesis

The suspicion was "our hold is time-based and it spends all three inside the hold window". The log
does not support a *hold window* at all: there is no hold. `HOLD_SECONDS = 8` only arms after an
engine **refusal** (`outcome == "cooling"`), and the engine never refused — so the only interval
between casts is `GUARD_SECONDS = 2`. The mechanism is the same family (time-based braking cannot
see charges), but the specific claim "spends all three within the hold" is wrong; it spends three in
four seconds and then keeps casting into an empty pool for 86 s.

### Contrast in the same log

Eye of Khorne (`num_uses = 1`) was **refused** on its second attempt:

```
751067: perform_special_ability(key, unit) : ACCEPTED            (t=35 s)
751182: perform_special_ability(key, unit) : REJECTED (on cooldown) - further holds suppressed for 8s  (t=36 s)
```

So the engine's own refusal *does* brake single-use abilities. The mod was correct to rely on it
there — and that is precisely why the break only shows on **multi-use** abilities.

## 1.5 The fix: a charge gate (one use per charge cycle)

Applied in the shared firing loop (not in the evaluator):

* A new table `charge_gate.hold_s` maps **every ability in the mod with `num_uses > 1`** (129 keys,
  generated from `unit_spec_abil.tsv`) to its own `recharge_time` in seconds.
  Nurgling Tide → `["wh3_main_lord_abilities_nurgling_tide"] = 90`.
* At load, each `ABILITIES` entry gets `ability.charge_s` from that table (single-use entries stay
  `nil`).
* After a successful cast the pair gets a deadline: `tick_count + floor(charge_s * 1000 / POLL_MS)`
  (90 s = 360 ticks). Until that tick the pair is not eligible; the wait is **silent** (one line is
  written when the use is spent, not one per suppressed poll).
* The deadline is purged with the unit in the one drop routine.

**The rule, stated plainly:** *an ability that carries more than one use is cast at most once per
its own recharge period.* One use per cycle means the pool is never drained, every cast is a real
cast, and no call is ever silently swallowed by an empty pool. It is deliberately conservative: the
2nd and 3rd charges stay banked rather than being sprayed two seconds apart.

Why not "burst `num_uses` then wait": that reproduces the visible 3-2-1-3 pattern the user reported,
and with the pool at zero any mistimed cast is a no-op. Why not "read the charges": there is no
script-reachable uses/cooldown read for a non-selected unit (established in earlier rounds; the
mod's only read, `can_perform`, is the very value that lies here).

## 1.6 General or ability-specific?

**Evaluator-general is the wrong layer; firing-layer-general is the right one.**

* It is **not** evaluator-specific: the loop has nothing to do with "self summon". Any multi-use
  ability on any trigger (enemy-ground summons such as Nurgling Birth ×3/×5, Inventory of
  Hatchlings ×3, The Tomb Blade of Arkhan ×5, Master of Souls ×40/5 s, …) will do the same the
  moment its trigger holds true for longer than 2 s.
* It is **not** applied to every ability either: single-use abilities keep the engine's own refusal
  as their brake (proved in this log), and gating them on a data-derived cooldown would
  change the whole roster for no evidence.
* So the gate lives in the **shared poll** and is keyed by **`num_uses > 1`** — data, not trigger,
  not marker. 129 of the mod's 682 keys qualify.

Residual risk, stated: an ability whose `recharge_time` is shorter than the gameplay window in which
it matters will now fire less often than the engine would allow (e.g. a 7-use / 60 s row fires once
per 60 s). That is the price of never wasting a charge; if the user prefers "spend the pool", the
one-line change is to allow `num_uses` casts before the hold.

---

# 2. Eye of Khorne — fired above 20 % health

## 2.1 What the user reported

> "I tested Eye of Khorne and it somehow cast on a unit that is above 20% health. The engine allowed
> it. So it may actually be a bug from the game."

## 2.2 What the mod measured

Caster: `wh3_dlc26_kho_cha_arbaal_flesh_hound` (Arbaal, ui id 1001). The chosen enemy was always
`wh_main_vmp_inf_skeleton_warriors_0`:

```
751062 (t=34 s): eye_of_khorne target: 'wh_main_vmp_inf_skeleton_warriors_0' is the chosen enemy
                 (health), health=1% distance=32.3m bound=35m
751064: ATTEMPT eye_of_khorne … reason: lowest-health non-commander enemy below 20% in bound
        (targeting wh_main_vmp_inf_skeleton_warriors_0, health=1%, distance=32.3m) | armed=ON
751066: eye_of_khorne pre-cast re-check: target still engaged (health, melee=false shot=false
        melee_only=false mode=health health=1%, distance=32.3m bound=35m) - firing
751067: perform_special_ability(key, unit) : ACCEPTED
```

Distance closed from 32.3 m to 0.0 m as the unit charged in; the bound was 35 m (70 % of the 50 m
row). The cast was **accepted** by the engine. A second attempt 2 s later was refused on cooldown —
the contrast with two-multi-use-ability behaviour in §1.4.

## 2.3 The scale problem: `HealthPercent` is a fraction

Across the whole battle there are **336** `eye_of_khorne target:` pick lines. Their `health=` values
are **only 0 or 1** — 138 × `health=0%`, 198 × `health=1%`, **not one value in 2…19 %**.

That distribution is impossible for a 0–100 percentage:

* a picked unit stayed at "1 %" from t=34 s to t=117 s (83 s) while it was alive, in melee, and the
  picker re-read it every poll;
* at t=118 s it read "0 %" — a live unit cannot be at 0 % health;
* if the scale were a percentage, the *lowest-health* enemy in a 35 m bubble over two minutes would
  have produced a spread (18, 12, 5, 3 …), not a constant 0/1.

`string.format("%.0f", x)` on a **0..1 fraction** produces exactly "0" (x < 0.5) or "1" (x ≥ 0.5),
which is the observed split. Independent support from the game's own UI: `unit_banner.twui.xml`
feeds this very field into a fill bar and compares it against 1:

```xml
<!-- line 1527-1529: the field drives a FILL BAR -->
<callback_with_context callback_id="ContextFillBar"
    context_object_id="CcoBattleUnit" context_function_id="HealthPercent">

<!-- line 1481: a visibility test written against 1, not 100 -->
context_function_id="HealthPercent &lt; 1"
```

A `ContextFillBar` input is 0..1. And the API dump's own description of the sibling read,
`battle_unit.lua` line 256-258, spells out the engine's convention for this quantity:

> "Returns the hitpoint strength of all soldiers in the unit, expressed as a **unary fraction** of
> the initial hitpoint strength of the unit. A returned value of **0.75** would indicate that the
> unit has lost 25% of the hitpoints it started the battle with."
> — `function battle_unit:unary_hitpoints()`

That is the read the fix now prefers; the context field carries the same 0..1 value.

**Consequence:** `hp < FOURTH.HEALTH_LINE_PCT` (`hp < 20`) was true for **every** unit in the game
(0.92 < 20), so the "finisher" gate never applied. The picker then took the lowest-health enemy in
range — which is a perfectly sensible unit to pick, just not necessarily below 20 %. That is exactly
what the user saw.

## 2.4 The ability's own data

`unit_spec_abil.tsv` (`wh3_dlc26_lord_abilities_eye_of_khorne`): `num_uses = 1`,
`recharge_time = 120`, `target_enemies = true`, `target_intercept_range = 50`,
`spawned_unit = wh3_dlc26_kho_mon_spawn_of_khorne_0_summoned`, `spawn_type = unit_position`.

The restriction is declared in the game's own flag table
`special_ability_to_invalid_target_flags_tables.tsv`:

```
invalid_target = climbing_manning_eq_on_platform   special_ability = wh3_dlc26_lord_abilities_eye_of_khorne
invalid_target = health_above_20%                  special_ability = wh3_dlc26_lord_abilities_eye_of_khorne
invalid_target = unit_is_commander_class           special_ability = wh3_dlc26_lord_abilities_eye_of_khorne
```

So the 20 % gate is real and is declared by the game. The mod's Lord/Hero half of the same rule
already worked (the commander was never chosen); the health half was dead because of the scale.

## 2.5 Did the engine "allow it"?

The call returned `ok_call = true` (`ACCEPTED`) at a target our (broken) read put at 1 % but which
was in reality far above 20 % — the user's report says the effect happened. Two readings remain
possible and the log cannot separate them:

1. the script cast path does not run the invalid-target validation (so the engine really does allow
   it) — then it is a CA-side observation on top of our bug;
2. the cast was accepted but inert (accepted ≠ applied — the mod's own standing rule), and what the
   user saw was the ability's VFX.

Either way **our read is the primary fault**, and fixing it removes the situation entirely: with the
correct scale the mod will not offer a >20 % unit, so whether the engine would have refused it
becomes moot. If the user still sees it land on a healthy unit **after** this build, that is a
genuine CA report — the evidence to attach is `invalid_target = health_above_20%` for the key plus a
log showing `health=NN%` above 20 at the pick line.

## 2.6 Online search for an existing report

Searched (18 queries, several per engine): `Eye of Khorne bug above 20% health`,
`"Eye of Khorne" below 20% health bug`, `warhammer 3 ability fires above health threshold bug`,
`"Eye of Khorne" "20%" health restriction`, `"eye of khorne" "above 20"`,
`"eye of khorne" "not working" OR "does nothing" bug`, `"eye of khorne" arbaal bug report`,
`total war warhammer 3 arbaal ability ignores health requirement`,
`total war warhammer 3 "less than 20%" ability bug not enforced`,
`"hit points less than 20%" total war ability broken`,
`"eye of khorne" chaos spawn bug reddit`, `"Eye of Khorne" Arbaal ability bug`, plus
`site:community.creative-assembly.com`, `site:community.creative-assembly.com inurl:bugs`,
`site:steamcommunity.com`, `site:steamcommunity.com/app/1142710`, `site:reddit.com/r/totalwar`.

**Nothing found.** No thread, bug ticket or wiki note reports Eye of Khorne firing on a unit above
20 % health. What exists is only background:

* `https://totalwarwarhammer.fandom.com/wiki/Eye_of_Khorne` — states the restriction verbatim:
  "Affects units if: **Hit Points less than 20%**; Unit is not Lord or Hero". Confirms the rule,
  not a bug.
* `https://community.creative-assembly.com/total-war/total-war-warhammer/forums/15-multiplayer-battles/threads/8230-khorne-new-content-fix-discussion`
  — a multiplayer balance thread, quoted: "In the case of Arbaal, he can get anywhere from 30 to 60
  kills with his Eye of Khorne ability when he targets a unit with many models still alive." This is
  a player describing normal use for kill counts, **not** a bug report, but it is consistent with
  the ability being used on units that are not visibly near death.
* `https://www.reddit.com/r/totalwar/comments/1hjj59m/could_somebody_explain_arbaals_eye_of_khorne/`
  — a "how does this ability work" question (page is behind a bot wall from here; only the search
  snippet is readable). Not a bug report.
* CA's bug tracker hits for "Arbaal" are unrelated (`Books of Khorne unable to progress`, `Praag`).

So: no prior art. If this turns out to be the engine skipping the invalid-target check on script
casts, it would be a **new** report.

---

# 3. What changed

## 3.1 Source (both files, LF preserved)

`mod_source\script\battle\mod\zz_test_deadly_onslaught.lua` and its log-free twin
`docs\WH3_auto_ability_annotated.lua`:

1. **`charge_gate`** (new, after the `ABILITIES` table): `hold_s` = 129 multi-use keys → their own
   `recharge_time` (28/30/31/43/44/46/47/60/90/120/180 s), plus the per-pair `until_tick` table.
2. **Load mapping**: each entry gets `ability.charge_s` (max over its keys; `nil` for single-use).
3. **Poll gate**: after the guard/hold decision, a pair whose charge deadline has not passed is not
   eligible (silent); on `outcome == "fired"` the deadline is set to
   `tick_count + floor(charge_s * 1000 / POLL_MS)` and one line is logged:
   `charge gate <marker>: one use spent - the next attempt waits Ns (the ability's own recharge_time)`.
4. **Drop purge**: `charge_gate.until_tick[id_slot] = nil` in the one drop routine.
5. **`FOURTH.health_pct(unit)`** (new): returns **0–100**, preferring
   `unit:unary_hitpoints()` (fraction → ×100) and falling back to `HealthPercent`
   (0..1 → ×100, >1 used as-is, unreadable → nil).
6. **All eleven `HealthPercent` call sites** routed through it (enemy finisher, ally-heal picks and their pre-cast
   re-checks, Ushoran/potion ≤75 %, the winds tiebreak's neighbour read). `enemy_health_pct` is now
   a one-line wrapper, so the caller code is unchanged.

Not touched: triggers, ranges, cast forms, badges, the readiness gate, the cooldown hold, the
spreadsheet/tracker.

Backups of the two pre-edit files: `docs\backups\round103\*.pre103.lua`.

## 3.2 Harness

New `%LOCALAPPDATA%\Temp\harness103.lua` (built from harness 102 + one section; older harnesses not
edited). 9 new worlds + 17 static gates.

**GREEN** (`uv run --with lupa python run_mock.py harness103.lua`):
`checks: 3569, failures: 0` → `HARNESS OK - all checks passed`.

Key worlds and what they prove:

| World | Proof |
|-------|-------|
| W1 | Nurgling Tide with `can_perform` always true and every call accepted: **1 fire in 120 polls**, **2 by poll 370**, second use ≥ 360 ticks (90 s) after the first, one `charge gate` line |
| W2 | a 1-use ability is **not** gated (3 fires in 20 polls = the plain 2 s guard) |
| W3 | fraction health 0.92 / 0.12 → picks the 0.12, logs `health=12%`, never names the 92 % unit |
| W4 | 0.90 / 0.75 fractions → **silent**, no pick line (the field failure) |
| W5 | fallback string `"0.85"` → 85 % → silent |
| W6 | fallback string `"0.08"` → fires, logs `health=8%` |
| W7 | legacy 0–100 fixtures unchanged (10 % beats 40 %) |
| W8/W9 | Ushoran ≤75 %: 0.90 silent, 0.40 fires |

**RED** (`H103_LIVE`/`H103_ANN` → `docs\backups\round103\*.pre103.lua`):
`checks: 3495, failures: 44`. The discriminators all flip as designed:

* `W1 (RED): … many fires in 120 polls (15)` and `… 370 polls still fire at the 2 s cadence (47)`
* `W4 (RED): the pre-103 build fired on a 75%-health unit (1 fires)`
* `W5 (RED): … fired on a 0.85 string read (1)`
* `W8 (RED): the pre-103 build fired at 90% health (1)`

Against harness 102 run on the same snapshot (32 failures, all older rounds' red controls), the
**only new failures are 10 new 0zz static gates plus the 2 health-text checks** (12 lines in all) —
nothing else changed.

## 3.3 Build + install

`mod_source\releases\20261017_bugfix_harness103\build_and_install103.py` (cloned from 102, round
note + 11 new content gates):

```
script/battle/mod/zz_test_deadly_onslaught.lua   672866 bytes  MATCHES SOURCE: True
ui/templates/zz_auto_badge.twui.xml                2864 bytes  MATCHES SOURCE: True
ui/zz_auto/blank.png                                 69 bytes  MATCHES SOURCE: True
ui/zz_auto/auto_badge.png                           252 bytes  MATCHES SOURCE: True
ui/common ui/special_ability_tooltip.twui.xml    331235 bytes  MATCHES SOURCE: True
built pack   md5 dfec7ac14b296b68458a1f6e92c0d133
installed    md5 dfec7ac14b296b68458a1f6e92c0d133
IDENTICAL    True
```

Installed artifact re-checked in the game folder:
`data\zz_test_deadly_onslaught.pack` md5 `dfec7ac14b296b68458a1f6e92c0d133`, 1,007,942 bytes, and
the new tokens are present inside it (`charge_gate.until_tick`, `function FOURTH.health_pct(unit)`,
`unit:unary_hitpoints()`, `charge gate `).

---

# 4. What to retest

**Nurgling Tide** (any Nurgle lord, in melee, ability armed):
1. Expect **one** cast, then the counter sits at **2** (not 0). It must not run 3→2→1.
2. In the log: exactly one
   `charge gate nurgling_tide: one use spent - the next attempt waits 90s (the ability's own recharge_time)`
   and **no** `ATTEMPT nurgling_tide` line for ~90 s.
3. After ~90 s in melee, a second cast; the counter goes 2→1.
4. Watch whether nurglings actually appear. In the tested battle the tracked army list never grew
   (the only `watching N unit(s)` line is `watching 2 unit(s)` at t=8 s), so that log cannot confirm
   any spawn landed even for the first three casts — the charge counter is the only proof that the
   casts were consumed. If no nurglings appear even with the fix, that is a separate finding.

**Eye of Khorne** (Arbaal, enemies in range):
1. It should no longer fire on healthy units. The pick line now prints a real percentage, e.g.
   `eye_of_khorne target: '…' is the chosen enemy (health), health=63% distance=…` — and a pick is
   only possible at all when something is genuinely **below 20 %**.
2. With everything healthy there should be **no** `eye_of_khorne target:` line and no cast.
3. If it *does* fire on a >20 % unit with a `health=NN%` above 20 in the same line, that is the CA
   case: keep the log, it is the bug report.

**Everything else** — because the health reader is shared, these now obey their real lines:
Ushoran / Potion of Toughness (≤75 %), Blood Sacrifice / Eat da Runts and the other ally heals
(≤75 %). They will fire **less** often than before and only when the unit really is below the line;
a heal that used to fire on a 90 % ally now waits.

**Any other multi-use ability** (Nurgling Birth ×3/×5, Inventory of Hatchlings, Tomb Blade of Arkhan,
Master of Souls, …): one cast per recharge period, one `charge gate <marker>` line per cast.

---

# 5. Follow-ups not done here

* The tracker (`docs\WH3_ability_tracker.md`) and the master spreadsheet were **not** updated; the
  per-ability logic text is unchanged, but a new row recording the charge gate and the health-scale
  fix belongs in the next spreadsheet version (`v5`) per the standing rule.
* `can_perform_special_ability` is proven unreliable for multi-use abilities. Any future ability
  whose engine refusal does not fire will need the same kind of data-derived brake.
* Whether the engine validates `invalid_target` on **script** casts is still unproven. A clean probe
  would be: cast Eye of Khorne at a 90 % unit with a guard that measures the target's active-effect
  count before/after (the `EFF before=… after=…` shape). Not attempted here because the mod must not
  offer such a target at all after this fix.
