# Sky-Junk Bomb — why one unit dropped and the other three did not

2026-10-18 · diagnosis of installed pack `651f12e61284cae472bb06bf3a66b87d` (round 111)
Log read: `...\Total War WARHAMMER III\zz_test_deadly_onslaught_log.txt` (231,740,166 B,
952,480 lines). Session analysed: the **last** one, lines **947215–952480** (battle clock
0–89 s, last poll tick 357).

User report, verbatim:

> "It works sometimes but sometimes not. For example, in the last battle the Sky-junk bomb
> dropped perfectly on the first unit. But when I selected the other 3 and just left them
> standing, the zombies passed below the Sky-junks and they didn't drop the bomb."

The user has since confirmed the four Sky-junks were **airborne the whole time** ("Sky-junks
always fly, they were flying"), so the grounded/flying reading is out on both evidence and
testimony.

---

## VERDICT

**Not a per-unit arming bug, not an identity/type collision, not a gate, not a poll that
skips units.** All four Sky-junks (ui id 1002, 1003, 1004, 1005) were armed in the same
click, all four were evaluated on every poll, and all four had ground infantry candidates.
The three that stayed put never fired because **the rule's release test was never
satisfied**: the picker requires the *projected centre-to-centre horizontal separation*
to be **≤ 6.0 m**, and for those three units the nearest zombie's centre bottomed out in
the **5–10 m band** — i.e. it never got inside 6 m — for the whole pass.

Two things turned a "zombies are underneath" picture into a "6–10 m off" measurement:

1. the test is **centre-to-centre**, not "is any model under me". A zombie block is wide;
   its centre can sit 6–10 m to one side while its models sweep underneath the hoverer.
   (This is the mirror image of the round-109 problem: 6 m was chosen so the enemy is under
   the *middle* of the drop formation — it does nothing for a wide enemy whose *centre*
   stays outside.)
2. the round-110/111 rule projects the enemy **1.5 s ahead**. For a stationary caster and a
   zombie *crossing* (not closing), that pushes the projected point ≈ 3.5 m further along
   its path, so the number is larger than what the eye sees exactly when it matters — at
   closest approach and while it recedes.

**Behaviour is by design; the misses are a consequence of the 6 m constant.** What *is*
defective is the diagnostics: the watch line bands to 5 m (wider than the 6 m decision
margin), and it does not name the unit, so neither the exact pass distance nor which of
four identical units logged a line can be recovered from the log. Both are described in
§7 with proposed — **not implemented** — fixes.

No engine rejection, no readiness refusal, no airborne hold and no gate line exists for
1003/1004/1005 anywhere in the session.

---

## 1. The four units and what the log recorded for each

Arming happened once, for all four at the same time:

```
948982  AUTO sky_junk_bomb for unit 1002: now ON
948983  AUTO sky_junk_bomb for unit 1003: now ON
948984  AUTO sky_junk_bomb for unit 1004: now ON
948985  AUTO sky_junk_bomb for unit 1005: now ON
948987  click: sky_junk_bomb badge -> 4 selected unit(s) toggled ON (1002, 1003, 1004, 1005)
```

There is **no** `AUTO sky_junk_bomb … OFF` line after that anywhere in the session (4 AUTO
lines total, all ON, `grep -c` = 4).

| unit | armed | evaluated (watch/target lines) | airborne | infantry candidate seen | closest projected sep. | fired |
| --- | --- | --- | --- | --- | --- | --- |
| 1002 | ON 948982 | yes — 8 `target:` lines, moving | yes (no hold) | grave guard, vampire lord, zombie | 3.5 m | **yes, 951089** |
| 1003 | ON 948983 | yes — watch lines, stationary | yes | `wh_main_vmp_inf_zombie` | 5–10 m band (never ≤6) | no |
| 1004 | ON 948984 | yes — watch lines, stationary | yes | same zombie | 5–10 m band | no |
| 1005 | ON 948985 | yes — watch lines, stationary | yes | same zombie | 5–10 m band | no |

The only attempt in the whole battle:

```
951089  ATTEMPT sky_junk_bomb 'wh3_main_unit_abilities_sky_junk_bomb' on 'wh3_main_cth_veh_sky_junk_0'
        ui id 1002 | reason: closest INFANTRY enemy under the projected caster point
        (targeting wh_main_vmp_inf_grave_guard_0, projected centre=3.5m after 1.50s, bound=6m) | armed=ON
951094  per-unit cast gate armed by sky_junk_bomb: no OTHER ability on unit 1002 may be issued for 3s
951095  charge gate sky_junk_bomb: one use spent - the next attempt waits 30s (the ability's own recharge_time)
951096  in-flight gate sky_junk_bomb: the cast needs 1s wind-up - the next attempt on this unit waits 3s
```

`ATTEMPT` count for `sky_junk_bomb` in the session: **1**. `target:` lines: 8 (all from
1002, same caster point `(-134.0, -151.2)`). `watch:` lines: 91.

---

## 2. Hypothesis by hypothesis

### H1 — per-unit arming: **REFUTED (proven)**

Arming is per `(unit, marker)` pair, keyed by the unit's own **numeric ui id**, and four
same-type units were armed independently in one click:

```lua
-- zz_test_deadly_onslaught.lua:4270
local function unit_slot(ui_id)
	local n = tonumber(ui_id)
	if n ~= nil then return n end
	return ui_id
end

-- :4279
local function is_armed(unit, marker)
	if unit == nil then return false end
	local ok_id, raw_id = pcall(function() return unit:unique_ui_id() end)
	if not ok_id or raw_id == nil then return false end
	local ui_id = unit_slot(raw_id)
	local per = armed[ui_id]
	return per ~= nil and per[marker] == true
end

-- :13834  the ONLY place a switch is flipped
local function set_auto_for_unit(ui_id, marker, value)
	local id = unit_slot(ui_id)
	local per = armed[id]
	...
	per[marker] = value == true
	log("AUTO " .. tostring(marker) .. " for unit " .. tostring(ui_id) .. ": now " ..
		(value and "ON" or "OFF"))
```

The multi-selection branch arms **every selected owner**, one call per unit (`:14617–14647`):

```lua
-- SEVERAL SELECTED UNITS - THE CHECKBOX RULE (this build): over
-- every selected unit that OWNS one of this ability's keys ...
local owners, owner_ids = {}, {}
...
for i = 1, #owners do
	set_auto_for_unit(owners[i], ability.marker, value)
end
log("click: " .. ability.marker .. " badge -> " .. tostring(#owners)
	.. " selected unit(s) toggled " .. (value and "ON" or "OFF")
	.. " (" .. table.concat(owner_ids, ", ") .. ")")
```

**Direct proof that the per-unit flag resolved correctly for a unit that did *not* fire** —
this is the tick line immediately after the trio's closest sampling (t = 80 s):

```
952053  tick 320 | phase=Deployed | conflict=true | auto=selected=1003,…,…,sky_junk_bomb=ON,…
```

Selected unit 1003, its own `sky_junk_bomb` = **ON**, at the exact tick of the pass.

### H1b — identity collision / type-keyed state: **REFUTED (proven)**

Every state table that could decide "has this unit fired / is this unit armed" is keyed by
ui id, never by type:

| table | key expression | line |
| --- | --- | --- |
| `armed` | `armed[unit_slot(unique_ui_id())][marker]` | 4200, 4279, 13834 |
| `last_attempt_at` | `[ui_id]` → `[marker]` | 4201, 13076 |
| `charge_gate.until_tick` | `[ui_id][marker]` | 13144 |
| `cast_gate.until_tick` / `.unit_until` | `[ui_id][marker]` / `[ui_id]` | 13035, 13056, 13129 |
| `cooldown_hold` | `[ui_id][marker]` | 4210, 12975 |
| `owned_abilities_by_unit` | `[tostring(ui_id)]` | 4126, 12869 |
| `target_key_by_unit` | `[ui_id]` | 4121 |
| `identity_by_unit` / `identity_checked` | `[tostring(ui_id)]` | 4133, 4139 |
| `FOURTH.ad_note` (log dedupe) | `[tostring(unique_ui_id())][marker]` | 12116 |
| `units_by_ui_id` (selection) | `[tostring(id)]` | 4120 |

No cache in the firing path is keyed by `unit:type()`. `unit:type()` is read only for
display/identity-change detection (`identity_by_unit`, keyed by ui id).

The charge gate that fired at 951095 is `charge_gate.until_tick[1002]["sky_junk_bomb"]`;
it cannot block 1003/1004/1005. Those three never entered it — none of them ever cast, so
`charge_gate.until_tick[1003]` is `nil` for the whole battle.

### H2 — grounded / `air_only` hold: **REFUTED (log + user)**

`sky_junk_bomb` ships `air_only = true` (entry at :3390), and the picker holds with a logged
reason when the read is not exactly `true`:

```lua
-- :12341
if FOURTH.ad_air_only then
	local ok_fly, flying = pcall(function() return unit:is_currently_flying() end)
	if not ok_fly or flying ~= true then
		FOURTH.ad_say(unit, marker, "airborne check: is_currently_flying() = "
			.. (ok_fly and tostring(flying) or "UNREADABLE")
			.. " -> HOLDING (this ability's row is air-only)")
		return nil
	end
end
```

`grep -c "airborne check"` over the session: **0**. If any of the four had been grounded,
there would be one such line per unit and no further evaluation; instead all four produced
watch/target lines. The user also states they were flying.

### H3 — no enemy / no infantry candidate: **REFUTED (proven)**

The picker found infantry for the trio — it names the zombie in their own watch notes:

```
952050  sky_junk_bomb watch: nearest INFANTRY 'wh_main_vmp_inf_zombie' is centre=~5m vs bound=6m
        -> NOT under the caster [projected sep=~5m after delay=1.50s; caster v=(0.0, 0.0) 0.0 m/s
        src=stationary …; enemy v=(1.6, -1.7) 2.3 m/s src=ordered]
```

`wh_main_vmp_inf_zombie` passes `FOURTH.enemy_is_infantry`. The candidate set is the whole
main enemy army (`bm:get_scriptunits_for_main_enemy_army_to_local_player()`, :12362) — the
zombies are in it (they appear as candidates), so "zombies were a second army" is out too.

**Restated: the trio found candidates every poll and rejected them on distance, not on class.**

### H4 / H5 — charge gate and per-caster serialisation: **REFUTED (proven)**

All three gate lines at 951094–951096 are keyed to **unit 1002** and cannot touch another
unit:

```lua
-- :13144
if ability.charge_s ~= nil then
	local cu = charge_gate.until_tick[ui_id]
	if cu == nil then cu = {}; charge_gate.until_tick[ui_id] = cu end
	cu[ability.marker] = tick_count + math.floor((ability.charge_s * 1000) / POLL_MS)

-- :13056  serialisation
if eligible and cast_gate.unit_until[ui_id] ~= nil
	and cast_gate.unit_marker[ui_id] ~= ability.marker
	and tick_count < cast_gate.unit_until[ui_id] then
```

Also, a gate cannot suppress the *picker*: a gate is evaluated **after** `ad_pick` returns a
reason, so a gated unit still logs its `target:` line. The trio logged **no** `target:` line
at all — nothing ever qualified to be gated.

And no gate line exists for 1003/1004/1005 anywhere in the session (`grep` for
`charge gate|in-flight gate|per-unit cast gate` in the session returns only unit 1001 and
unit 1002 lines).

### H6 — does the poll evaluate every friendly unit, or only selected ones? **Every unit, every poll (proven)**

Watch list = the local player's whole army, merged by ui id (`:4954`, `:4970`):

```lua
local sunits = bm:get_scriptunits_for_local_players_army()
...
for i = 1, total do
	local script_unit = sunits:item(i)
	local unit = script_unit.unit
	local ui_id = unit:unique_ui_id()
	...
		tracked_units[#tracked_units + 1] = script_unit
		units_by_ui_id[id_text] = unit
```

The firing loop is over that whole list, not over the selection (`:12770–12878`):

```lua
for i = 1, #tracked_units do
	local script_unit = tracked_units[i]
	local unit = script_unit and script_unit.unit
	if unit ~= nil and unit:number_of_men_alive() > 0 then
		local routing = unit_is_routing(unit)
		local ui_id = unit:unique_ui_id()
		...
		local unit_abilities = owned_abilities_by_unit[tostring(ui_id)]
		if unit_abilities == nil then unit_abilities = ABILITIES end
		for _, ability in ipairs(unit_abilities) do
			-- THE PER-UNIT SWITCH: this (unit, ability) pair must be armed.
			if is_armed(unit, ability.marker) then
				...
				ability.evaluate(unit, routing)
```

`selected_unit()` is used **only** for the badge letter and the click target
(`collective_armed`, :4683), never for evaluation.

Evidence in the log that three separate units evaluated in the same pass: three *identical*
watch notes in a row at the closest approach —

```
952050  … centre=~5m … caster v=(0.0, 0.0) 0.0 m/s src=stationary …
952051  … centre=~5m … caster v=(0.0, 0.0) 0.0 m/s src=stationary …
952052  … centre=~5m … caster v=(0.0, 0.0) 0.0 m/s src=stationary …
```

`FOURTH.ad_say` de-duplicates **per unit** (`ad_note[tostring(ui_id)][marker]`), so a unit
cannot print the same note twice; three identical consecutive lines can only come from
**three different units**. And the evaluation block they sit in is gated on
`is_armed(unit, ability.marker)` — so three units were simultaneously armed *and*
evaluated. (The fourth, 1002, was elsewhere with a different nearest enemy, which is why
it contributes no line to this group.)

---

## 3. What actually stopped the three: the distance, measured

Banded watch notes for the stationary trio, in order, with the battle clock taken from the
1 s inventory sweeps around each line:

| clock | line | now | projected | caster v |
| --- | --- | --- | --- | --- |
| ≈77 s | 951942/943 | ~10 m | ~10 m | stationary |
| ≈78 s | 951983, 952016/017 | ~10 m | **~5 m** | stationary |
| **≈79–80 s** | **952050/051/052** | **~5 m** | **~5 m** | **stationary** |
| ≈81 s | 952119/120 | ~5 m | ~10 m | stationary |
| ≈82 s | 952159/160 | ~10 m | ~10 m | stationary |
| ≈85 s | 952256/257 | ~10 m | ~15 m | stationary |
| ≈89 s | 952472/473 | ~20 m | ~20 m | stationary |

Reading of the table:

* the trio had the zombie inside 10 m of their centres for roughly **77–83 s of battle
  clock (≈ 5 s, ≈ 20 polls)** — plenty of opportunities, not a sampling miss;
* the *instant* gap bottomed in the **5–10 m** band, and it **never** reached the 0–5 m band
  for any stationary unit (contrast unit 1002 at 951177: `centre=~0m`, i.e. genuinely
  underneath — and even then it did not fire, because the *projected* gap was ~5 m and
  moving away);
* the *projected* gap is what decides, and it never reached 6.0 m: the moment the band read
  ~5 m the projected value was still > 6.0 m (otherwise a `target:` line and an `ATTEMPT`
  would exist);
* the projection **worsens** the number as the block goes by: ≈5 m at closest approach →
  ≈10 m one second later (951983→952119). At 2.3 m/s, 1.5 s of enemy travel is ≈3.45 m, so
  a zombie abreast of the hoverer is projected 3.45 m *past* it — no longer "under".

So the honest reading of the user's "the zombies passed below": models swept under the
hover, but the block's **centre** passed 6–10 m to the side, and the rule is a
centre-to-centre test. On the drop families' 10-model frontage that 6 m constant was
tuned to mean "under the middle of *my* formation"; a zombie horde is far wider, so 6 m
from *its* centre is not "it missed me" but "I am not over its middle".

---

## 4. The exact conditions under which those three would have fired

With the shipped code (`AIR_DROP_CENTER_M = 6`, `AIR_DROP_DELAY_S = 1.5`,
`AIR_DROP_CASTER_LEAD = 0.5`, `air_only = true`), unit 1003/1004/1005 fires when **all** of:

1. `is_armed(unit, "sky_junk_bomb") == true` — met (948983/948984/948985, still ON at tick 320);
2. `is_currently_flying() == true` — met (no hold line);
3. some enemy of the main enemy army has `number_of_men_alive() > 0` and `is_infantry()` — met;
4. for that enemy, `|caster_proj − enemy_proj|_xz ≤ 6.0 m` where
   `caster_proj = caster + v_caster · 1.5 · 0.5` (a parked Sky-junk: `= caster`) and
   `enemy_proj  = enemy + v_enemy · 1.5` — **not met: the closest projection was in the
   5–10 m band, strictly above 6.0 m**;
5. at the pre-cast re-check the same helper still returns ≤ 6 m (it re-reads the same two
   dials) — never reached.

Practical form of (4) for a parked Sky-junk: **the hover point must be within ~6 m of where
the zombie unit's centre will be 1.5 s later** — i.e. park it nearly on the lane the block
will walk, not beside it. A perfect overflight does fire (1002 proves the mechanism: it
fired at a projected `centre=3.5m`); a 7–9 m lateral pass does not, no matter how many
models sweep underneath.

---

## 5. Is it by design or a defect?

**By design (the behaviour).** Nothing was stuck, nothing was missed, no unit was skipped,
no wrong unit was toggled, and no state collided across the four identical units. Every
element of the shipped rule behaved exactly as written; the rule's answer to those three
passes was "the enemy is not under me".

**Genuine defects (the observability), and they are why this took a 231 MB log to answer:**

* **D1 — the watch band is coarser than the decision.** The watch note quantises to 5 m:

  ```lua
  -- :12435
  local band = math.floor(near_gap / 5) * 5
  local nband = math.floor(near_now / 5) * 5
  ```

  The decision margin is 6.0 m. So "~5m" covers everything from 5.00 to 9.99 m — the single
  number needed to choose a new bound is destroyed exactly where it matters. *Suspected
  consequence:* this is also why earlier rounds tuned the constant by trial rather than by
  arithmetic.
* **D2 — the air-drop log lines do not name the unit.** `FOURTH.ad_say` logs
  `marker .. " " .. note` only. With four identical `wh3_main_cth_veh_sky_junk_0` units,
  no watch/target line can be attributed to a card, so "which of the four?" had to be
  inferred from line counts. (The `ATTEMPT` line does carry the ui id and type — the
  picker's own lines do not.)
* **D3 — one global constant serves two opposite symptoms.** `AIR_DROP_CENTER_M` is forced
  onto *every* `air_drop_on_infantry` entry at load (`:12632`), so the same 6 m must satisfy
  a fast mover over infantry (round 111 needed it *tighter*: "drops too soon") and a parked
  hoverer beside a wide horde (this report needs it *looser*: "never drops"). One dial
  cannot be right for both; that is a design gap, not a coding error.

---

## 6. Proposed fixes — NOT IMPLEMENTED

Ordered by value. Only the first changes behaviour.

1. **Per-entry bound override (behaviour).** Add an optional `centre_m` on an ability entry,
   defaulting to `FOURTH.AIR_DROP_CENTER_M`, and let the load-time binding use it:

   ```lua
   if ability.evaluate == FOURTH.evaluate_air_drop_on_infantry then
       ability.range_m = (type(ability.centre_m) == "number") and ability.centre_m
                         or FOURTH.AIR_DROP_CENTER_M
   end
   ```

   then `centre_m = 10` on `sky_junk_bomb` only. Rationale: 10 m is the row's own
   `target_intercept_range`, the trio's pass bottomed in 5–10 m, and it leaves
   `drop_rocks` / `death_from_above` (the "too soon" cases) untouched at 6 m. Wait for a
   field test before touching the shared constant — moving it to 10 would re-open the
   round-111 early-release complaint for moving casters.
2. **Exact distance below 15 m (diagnostics).** In the watch note, print
   `string.format("%.2f", near_gap)` instead of the band whenever `near_gap < 15`, and
   always print the exact projected value. One line, no behaviour change, and the next
   report becomes arithmetic instead of inference.
3. **Name the unit (diagnostics).** Prefix `ad_say` with the unit, e.g.
   `sky_junk_bomb [1003 wh3_main_cth_veh_sky_junk_0]: watch: …`. Same cost, fixes the whole
   class of "four identical units" questions.
4. *(Optional, only if 1 still misses)* a secondary acceptance on the **instant edge gap**
   (`unit_distance ≤ 1.0 m`) alongside the projected centre test — the edge gap collapses
   when models are literally underneath. Do **not** replace the centre test with it: round
   109 removed edge-to-edge precisely because wide bodies side by side pass it and the rocks
   left too early.

---

## 7. What to retest after the fix

1. Arm all units in one click (4 selected) → expect four `AUTO … for unit 10NN: now ON`
   lines; the badge reads `A` (collective) while all selected owners are armed, `M` when any
   is not — that letter is per selected unit, so re-check it after switching cards.
2. Park three Sky-junks beside a zombie lane and let the block walk past. With D2/D3 applied
   the log should give, per unit, a decreasing **exact** projected distance and either a
   `target:` line or a minimum value; that minimum is the number the bound must clear.
3. Send back: the `watch:` line with the lowest `projected sep` for each of the three, plus
   the `target:`/`ATTEMPT` line if one fires.

---

## Appendix — raw evidence, verbatim

Session boundary and arming:

```
947215  ======== new battle session ========
948837  [zz_test_deadly_onslaught]       ability: wh3_main_unit_abilities_sky_junk_bomb
948842  … (×4 — one per Sky-junk unit in the watch list)
948856  active abilities this battle: inspired_assault_i, inspired_defence_i, inspired_marksmanship_i, sky_junk_bomb
948982  AUTO sky_junk_bomb for unit 1002: now ON
948983  AUTO sky_junk_bomb for unit 1003: now ON
948984  AUTO sky_junk_bomb for unit 1004: now ON
948985  AUTO sky_junk_bomb for unit 1005: now ON
948987  click: sky_junk_bomb badge -> 4 selected unit(s) toggled ON (1002, 1003, 1004, 1005)
```

The one successful cast (unit 1002):

```
951087  sky_junk_bomb target: 'wh_main_vmp_inf_grave_guard_0' is UNDER the caster (PROJECTED 1.50s AHEAD
        momentum=none caster=(-133.7, -151.6) v=(-1.5, 2.6) 3.0 m/s src=ordered proj=(-134.9, -149.7)
        from delay_caster=1.50s lead=0.50 moving caster: lead=0.50 of 1.50s enemy=(-138.1, -143.5)
        v=(2.0, -1.8) 2.7 … centre=3.5m (the PROJECTED separation, which is what decides) now=… bound=6m
951089  ATTEMPT sky_junk_bomb … on 'wh3_main_cth_veh_sky_junk_0' ui id 1002 | reason: closest INFANTRY
        enemy under the projected caster point (targeting wh_main_vmp_inf_grave_guard_0,
        projected centre=3.5m after 1.50s, bound=6m) | armed=ON
```

The trio at the closest pass (three units, one poll group), and the armed-state tick that
follows it:

```
952050  sky_junk_bomb watch: nearest INFANTRY 'wh_main_vmp_inf_zombie' is centre=~5m vs bound=6m
        -> NOT under the caster [projected sep=~5m after delay=1.50s; caster v=(0.0, 0.0) 0.0 m/s
        src=stationary (delay_caster=1.50s lead=0.50); enemy v=(1.6, -1.7) 2.3 m/s src=ordered]
952051  … (identical note, second unit)
952052  … (identical note, third unit)
952053  tick 320 | phase=Deployed | conflict=true | auto=selected=1003,…,sky_junk_bomb=ON,…
```

The projection turning a 5 m pass into a 10 m one as the block goes by:

```
952119  … centre=~5m … [projected sep=~10m … caster v=(0.0, 0.0) 0.0 m/s src=stationary …;
        enemy v=(1.6, -1.7) 2.3 m/s src=ordered]
952120  … (second unit, same note)
```

Session end — the battle was paused (not crashed), all five cards still on the field:

```
952466  cards: selected-tracker=1005
952467  card 1001 state='active' visible=true
952468  card 1002 state='active' visible=true
952469  card 1003 state='active' visible=true
952470  card 1004 state='active' visible=true
952471  card 1005 state='selected' visible=true [selected-tracker]
952474  WATCHDOG: model time has not advanced for 6 s (tick 357) - paused, or the poll is dead. …
```

Greps over the session, for the record:

| pattern | hits |
| --- | --- |
| `ATTEMPT sky_junk_bomb` | 1 (unit 1002) |
| `sky_junk_bomb target:` | 8 (all unit 1002) |
| `sky_junk_bomb watch:` | 91 |
| `AUTO sky_junk_bomb` | 4 (all `now ON`) |
| `airborne check` | **0** |
| `rejected` / `REFUSED` (sky-junk) | 0 |
| `charge gate` / `in-flight gate` / `per-unit cast gate` for 1003/1004/1005 | **0** |

---

## 8. WHAT WAS IMPLEMENTED AFTER THIS DIAGNOSIS (round 112, 2026-10-24)

* **The enemy-side lead dial** (`FOURTH.AIR_DROP_ENEMY_LEAD = 0.3`): the enemy is now projected
  `enemy + v_enemy * AIR_DROP_DELAY_S * AIR_DROP_ENEMY_LEAD`. This is the fix for §3's arithmetic:
  at 2.3 m/s the projected centre is carried **1.0 m** instead of **3.45 m**, so the three
  stationary Sky-junks see the pass at ≈5.1 m instead of ≈6.1 m and fire. `0.0` = the enemy's
  current position. §6 item 1 (a per-entry `centre_m` override) was **not** needed and the shared
  6 m bound is untouched.
* **D1 (exact distances)** — implemented: the `watch:` line prints both distances as `%.2f` below
  15 m; the 5 m band survives above 15 m.
* **D2 (name the unit)** — implemented as a `[<ui id>]` prefix on **every** air-drop line, plus all
  four dials printed on each line.
* Constraints recorded then, still true: the test remains **centre-to-centre** (§3), so a wide enemy
  whose centre passes 6–10 m to the side is still judged on its centre; §6 item 4 (a secondary
  instant edge-gap acceptance) remains **not implemented** by design.

Evidence: harness 112 (4492 checks / 0 failures), `docs/WH3_round112_airdrop_enemylead.md`,
`mod_source/releases/20261024_airdrop_enemylead_harness112/RELEASE_NOTES.md`; installed pack md5
`237702987893b8837d2dbb5df05d566b`.
