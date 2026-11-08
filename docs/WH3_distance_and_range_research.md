# WH3 — Distance and Range Research

**Scope.** Three factual questions, answered separately with quoted evidence:
1. How `battle_unit:unit_distance(other)` is computed (edge-to-edge vs centre-to-centre), and whether a unit-targeted cast reaches the target's edge or centre.
2. Whether the enemy in the disputed Accusation cast really satisfied the in-melee condition.
3. What `target_intercept_range` and `effect_range` actually mean, and whether the "pursuit range causing movement" claim holds.

**Status.** Investigation and documentation only. No file in the mod, the tracker, the annotated copy, or any pack was modified; nothing was built. This report is the only artifact written.

**Sources used** (all read-only):
- Battle-script API dump: `C:\Users\vlady\AppData\Local\Temp\wh3\` (`battle_unit.lua`, `script_unit.lua`, `lib_bsu.lua`, `battle.lua`, `battle_manager.lua`).
- Mod source (read-only): `C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua`.
- Builds that wrote the runtime log: `...\releases\20261010_accusation_harness94\insert_ev_live.lua`, `...\20261010_range_rule_harness95\pre95_live.lua`.
- Runtime log: `C:\Program Files (x86)\Steam\steamapps\common\Total War WARHAMMER III\zz_test_deadly_onslaught_log.txt` (~97 MB).
- Probe logs: `...\zz_probe_unit_reads_log.txt`, `...\zz_probe_enemy_target_log_round4.txt`.
- Extracted tables: `%LOCALAPPDATA%\Temp\wh3\unit_spec_abil.tsv`, `unit_abilities.tsv`.
- RPFM schema: `C:\Users\vlady\AppData\Roaming\FrodoWazEre\rpfm\config\schemas\schema_wh3.ron`.
- Community documentation: Cryswar's Steam guide "Creating and Editing Abilities" (`steamcommunity.com/sharedfiles/filedetails/?id=1698960734`), CA hotfix/balance threads, TWA fandom wiki ability pages. Fetched live over the browser/search.

---

## Question 1 — `battle_unit:unit_distance(other)`: edge-to-edge or centre-to-centre?

### The doc string (verbatim)

`battle_unit.lua`, lines 160–163:

```
--- Returns the shortest distance in metres between this unit and a supplied unit, taking into account their bounding box rather than just working out the centre-to-centre distance.
---@param target_unit battle_unit #target unit
---@return number #shortest distance
function battle_unit:unit_distance(target_unit) end
```

**This is explicit: `unit_distance` is a bounding-box (edge-to-edge) measurement, and the doc says so in exactly those terms — it is *not* centre-to-centre.** Confidence: **very high** (direct engine documentation).

For contrast, `battle_unit:position()` (lines 114–116) is documented as the **centre**:

```
--- Returns the centre position of the main squad of the unit.
---@return battle_vector #position
function battle_unit:position() end
```

So a centre-to-centre distance would be `a:position():distance(b:position())` — a *different* computation from `unit_distance`, which is exactly what the doc contrast implies.

### Is there a unit radius / bounding-box / extent accessor?

**No individual-unit radius or bounding-box accessor exists in the battle-script API.** The complete `battle_unit` function list (extracted from the dump) contains `position`, `ordered_position`, `ordered_bearing`, `ordered_width`, `position_of_officer`, `can_reach_position`, `missile_range`, `unit_distance`, `unit_in_range`, … — but **no** `radius`, `unit_radius`, `get_radius`, `bounding_box`, or `extent`. So a script **cannot read a unit's footprint** to convert an edge distance into a centre distance. Confidence: **very high**.

What *does* exist:
- `script_units:radius()` (`script_unit.lua` 485–487, implemented in `lib_bsu.lua` 2603–2617) — a **collection** radius, not a unit radius:
  > "Returns the distance from the furthest unit from the centre, to the centre, which is an indication of how spread out the units in this collection are."

  Its implementation is `current_sunit.unit:position():distance(centre_point)` — i.e. **centre-to-centre** unit positions around a collection centre. It measures how spread out a *group* is, not one unit's size.
- `battle_unit:ordered_width()` (lines 135–137):
  > "Returns the width of the position to which the unit has been ordered in metres."

  This is the **ordered formation frontage**, the closest extent proxy — but it is the *ordered* width, not the live footprint.
- The DB (`battle_entities_tables.radius` in `schema_wh3.ron`, ~line 51569) defines a per-soldier collision radius, but it is **not exposed to Lua** and its schema `description` is empty.

### Empirical anchors

**(a) The game's own scripts.** The only shipped battle script that compares a `unit_distance` result against a constant is the Tamurkhan werekin quest (`...\WH3-scripts\script\battle\quest_battles\tamurkhan\werekin\battle_script.lua:192`):

```lua
if is_routing_or_dead(sunit) == false and skraelsbane.unit:unit_distance(sunit.unit) < 50 then
```

A bare 50 m threshold — it does not derive the threshold from any radius, so it neither confirms nor refutes the semantics on its own; it only shows the engine author treating `unit_distance` as a usable "am I on top of it" test.

**(b) The runtime log (the strongest empirical anchor).** The mod's charge detector writes a **real `unit_distance` readout every charge attempt**. `zz_test_deadly_onslaught.lua` lines 3464–3483 and 4636–4637:

```lua
local ok_dist, dist = pcall(function() return unit:unit_distance(target) end)   -- target = unit:current_target()
...
reason = string.format("charging (gap=%.1fm dist=%.1fm eta=%.1fs)", m.order_gap, m.target_dist, m.ttc)
```

So in every `reason: charging (gap=… dist=… eta=…)` line, **`dist` *is* `unit_distance(current_target)`**. Cross-check: `eta = dist / fast_speed`. Example line ``charging (gap=270.0m dist=31.0m eta=4.0s)`` → 31.0 / 4.0 ≈ 7.75 m/s, a plausible fast speed; ``(gap=0.8m dist=0.5m eta=0.1s)`` → 0.5/7.75 ≈ 0.06 s → 0.1 s. The relationship holds.

Distribution of `dist=` across the whole log (n = 8 130):

| value | count |
|---|---:|
| exactly **0.0 m** | **3 962 (49 %)** |
| 0.1–0.9 m | 384 |
| 1.0–4.9 m | 596 |
| 5.0–9.9 m | 135 |
| ≥ 10 m | 3 053 |

Half of all `unit_distance` reads are **exactly 0.0 m**. Two distinct units cannot have their **centres** 0.0 m apart, so a centre-to-centre implementation could not produce this. `unit_distance = 0.0` is what you get when two units' **bounding boxes touch/overlap** — precisely the documented behaviour, and it is the normal state for a unit that has reached its target in melee. This corroborates the doc string empirically. Confidence: **high** (the doc is definitive; the log is consistent and would be hard to explain otherwise).

**(c) Probe data (partial extent data).** The unit-reads probe logged `ordered_width()` values of **1.12, 1.2, 1.4, 2.4, and 29.42 m** (`zz_probe_unit_reads_log.txt`). The recurring **29.42 m** is a large infantry block's frontage; the ~1.4 m values are single-entity/character units. So a big block's footprint is tens of metres across.

### Edge-vs-centre shift — how big could it be?

For two units in melee contact, the edge-to-edge distance is ≈ 0, whereas the centre-to-centre distance is ≈ (half the depth of each unit) + the gap. The probe's only numeric extent is the **frontage** (ordered_width, up to ≈ 29.4 m). The relevant half-extent for two blocks facing each other is their **half-depth**, not half-frontage, so the exact shift cannot be read off these data. **What can be said:** the distinction is *not* a rounding error — it is on the order of **the units' own half-footprints**, i.e. **roughly 1 m (character) up to ~10–30 m (large block)** per side. Treating a centre-to-centre number as an edge number (or vice-versa) can therefore be wrong by many metres. Confidence: **medium** (order-of-magnitude correct; exact figure undetermined).

### Does a unit-targeted cast reach the edge or the centre?

The cast is issued as `uc:perform_special_ability(key, unit)` (mod line 4417) — the engine receives a **unit handle**, not a position. Whether the engine resolves the effect at the target's edge, centre, or anywhere (the effect may simply attach to the unit's entity set) is **not observable** from any source I could find: the doc strings for `perform_special_ability` do not describe the hit-test geometry, no script performs such a cast and reports a hit position, and no probe logged caster+target positions at a known separation. **Undetermined.** (Note: the only probe that tried to compare positions, `zz_probe_unit_reads`, showed `position()` returns a `battle_vector` handle and that `unit_in_range(vector)` is rejected — *"battle.unit expected, got userdata"* — so positional geometry is not script-visible.)

### Question 1 — unknowns
- No script-level unit radius/footprint accessor exists, so the exact edge↔centre correction cannot be computed from Lua.
- Whether a unit-targeted cast applies at the target's edge, centre, or per-entity is unobservable from the sources available.
- The log's `dist=` values are for the *charge detector's* target, not for an Accusation cast; they demonstrate the semantics but not Accusation's specific geometry.

---

## Question 2 — Did the enemy really satisfy the in-melee condition at the Accusation cast?

### What the mod's condition actually reads

The user's rule, quoted in the mod (lines 5431–5432):

```
--   THE USER'S RULE (verbatim): "implement accusation automatic activation when
--   enemy unit in range is in melee or being shot at."
```

The evaluator is `FOURTH.evaluate_enemy_engaged_or_shot` (`zz_test_deadly_onslaught.lua` 5578–5637). The **predicate it calls on the ENEMY** is at lines 5596–5602:

```lua
local ok_melee, melee = pcall(function() return enemy:is_in_melee() end)
local arm = nil
if ok_melee and melee == true then
    arm = "melee"
elseif FOURTH.eg_under_missile_attack(enemy) then
    arm = "missile"
end
```

with `FOURTH.eg_under_missile_attack` (5536–5544) = `pcall(function() return enemy:is_under_missile_attack() end)`.

**The predicate is an OR: `enemy:is_in_melee() == true` OR `enemy:is_under_missile_attack() == true`.** "In melee" is only one of the two qualifying arms.

The pre-cast re-check reads the same predicates again (lines 4365–4367):

```lua
local ok_melee, melee = pcall(function() return enemy:is_in_melee() end)
local still_melee = (ok_melee and melee == true)
...
log("  accusation pre-cast re-check: target still engaged (" .. tostring(FOURTH.eg_arm)
    .. ", melee=" .. tostring(still_melee) .. " shot=" .. tostring(still_shot) .. ...
```

The build that actually wrote the runtime log (harness 94/95) used the identical logic — `pre95_live.lua` 4340–4364:

```lua
local ok_melee, melee = pcall(function() return enemy:is_in_melee() end)
local still_melee = (ok_melee and melee == true)
```

### Documented meaning of the predicates

`battle_unit.lua`:

| Predicate | Doc string (verbatim) |
|---|---|
| `battle_unit:is_in_melee()` (line 218) | "Returns whether the unit is currently in melee combat." |
| `battle_unit:is_under_missile_attack()` (line 214) | "Returns whether the unit is currently taking fire." |
| `script_unit:is_in_melee()` (line 151) | "Returns true if the unit is in melee. This is an unembellished wrapper for an underlying code function." |

**Semantics.** `is_in_melee()` means "**this unit is currently in melee combat**" — i.e. **in melee with *someone*, not necessarily with the caster**. It is *not* "is fighting the caster", and it is *not* "is attacking". It is a self-state of the enemy unit. The mod calls it on the enemy, so the "in melee" arm fires whenever **any** friendly unit has engaged that enemy, not only the caster. This is consistent with (and no narrower than) the user's wording "enemy unit … is in melee". Confidence: **high** (engine doc, plus the wrapper's own note that it is unembellished).

### Reconstruction of the timeline (tick numbers)

The log is an **append** log spanning **19 battle restarts** (`tick 40 | phase=Deployment` appears 19×; `phase=` values are only `Deployment`/`Deployed`/`VictoryCountdown`). It therefore contains several builds and battles. Within a battle, the tick number is the second (`hb t=320` and `tick 320` are the same instant; `INVENTORY sweep t=320.0s`).

There are **26** Accusation pre-cast re-checks (`- firing`), **0** `accusation SKIPPED`, and **505** `accusation target:` selection lines (224 "melee", 281 "missile"). The pre-cast re-checks split cleanly:

| Arm | re-checks | enemy `melee=` | enemy `shot=` |
|---|---:|---|---|
| (missile) | 19 | **false** | true |
| (melee) | 7 | **true** | false |

**Timeline — cast #1 (the earliest enemy-targeted Accusation cast in the log).** Nearest preceding heartbeat `t=320`. All line numbers are in the runtime log:

```
L572569  card 1002 state='active' visible=true
L572572    accusation target: 'wh_main_vmp_inf_skeleton_warriors_0' is the chosen enemy (missile) within 75m
L572573    readiness accusation on ui id 1002: wh_main_hero_abilities_accusation=true (fallback scan)
L572574  ATTEMPT accusation 'wh_main_hero_abilities_accusation' on 'wh_main_emp_cha_witch_hunter' ui id 1002 | reason: enemy under missile fire (targeting wh_main_vmp_inf_skeleton_warriors_0) | armed=ON
L572575    can_perform before      : true
L572576    accusation pre-cast re-check: target still engaged (missile, melee=false shot=true, in_range=true) - firing
L572577    perform_special_ability(key, unit) : ACCEPTED
L572581  command: 'Special Ability' issued for 'wh_main_hero_abilities_accusation'
```

*(The `tick 320 | phase=Deployed` heartbeat sits just above L572572; `hb t=340` follows at L572582.)*

**Timeline — a melee-arm cast (cast #13), for contrast.** Nearest heartbeat `t=420`:

```
    accusation target: 'wh_main_vmp_inf_skeleton_warriors_0' is the chosen enemy (melee) within 52m   (×4)
    accusation pre-cast re-check: target still engaged (melee, melee=true shot=false, in_range=true) - firing
```

**All 26 casts** (line, tick, arm, enemy `melee=`):

```
[ 1] L572576  t=320  (missile) within 75m  enemy melee=false   ACCEPTED   (command issued)
[ 2] L572664  t=340  (missile) within 75m  enemy melee=false   ACCEPTED   (command issued)
[ 3] L572781  t=340  (missile) within 75m  enemy melee=false   REJECTED on cooldown
[ 4] L572879  t=360  (missile) within 75m  enemy melee=false
[ 5] L573188  t=380  (missile) within 75m  enemy melee=false
[ 6] L577502  t=300  (missile) within 52m  enemy melee=false   ACCEPTED   (command issued)
[ 7] L577586  t=300  (missile) within 52m  enemy melee=false   ACCEPTED   (command issued)
[ 8] L577681  t=300  (missile) within 52m  enemy melee=false   REJECTED on cooldown
[ 9] L577758  t=320  (missile) within 52m  enemy melee=false
[10] L578062  t=340  (missile) within 52m  enemy melee=false
[11] L578373  t=380  (missile) within 52m  enemy melee=false
[12] L578444  t=380  (missile) within 52m  enemy melee=false
[13] L578750  t=420  (melee)   within 52m  enemy melee=true    ACCEPTED
[14] L579097  t=460  (melee)   within 52m  enemy melee=true
[15] L579249  t=460  (melee)   within 52m  enemy melee=true
[16] L579545  t=500  (melee)   within 52m  enemy melee=true
[17] L579842  t=540  (melee)   within 52m  enemy melee=true
[18] L579983  t=540  (melee)   within 52m  enemy melee=true
[19] L583804  t=240  (missile) within 52m  enemy melee=false   ACCEPTED   (command issued)
[20] L583890  t=260  (missile) within 52m  enemy melee=false   ACCEPTED   (command issued)
[21] L583985  t=260  (missile) within 52m  enemy melee=false   REJECTED on cooldown
[22] L584061  t=260  (missile) within 52m  enemy melee=false
[23] L584367  t=300  (missile) within 52m  enemy melee=false
[24] L584673  t=340  (missile) within 52m  enemy melee=false   ACCEPTED
[25] L584763  t=340  (missile) within 52m  enemy melee=false   REJECTED on cooldown
[26] L585092  t=380  (melee)   within 52m  enemy melee=true
```

(An earlier era of the log — before the enemy-targeted build — contains Accusation casts under the **old self-trigger**, e.g. L549754+ `reason: in melee, morale not wavering`, where "in melee" refers to the **caster**, not the enemy. Those are a different trigger and are not the enemy-targeted casts under dispute.)

### What the log proves — and what it does not

**Proves (confidence high):**
- At **every** enemy-targeted Accusation cast, the mod **did** log the chosen enemy's `is_in_melee()` result, as `melee=<bool>` in the pre-cast re-check. So the log **does** contain enough to answer the melee question.
- For the **missile-arm** casts (19 of 26, including all the earliest), **`melee=false`** and the ATTEMPT reason is `enemy under missile fire`. **The enemy was NOT in melee at those casts; it qualified via the other arm (`is_under_missile_attack() == true`).**
- For the **melee-arm** casts (7 of 26), `melee=true`.
- Every ATTEMPT that fired had `can_perform before : true`, and the re-checks never tripped the skip (`0` SKIPPED lines).

**Cannot prove / caveats (explicit):**
- **The log cannot distinguish "read returned false" from "read raised".** `still_melee = (ok_melee and melee == true)` prints `false` in both cases. So `melee=false` is *consistent with* the enemy not being in melee, but the log alone does not rule out an unreadable read. (The mod's own history says `is_in_melee()` was "proven live on enemies", so an error is unlikely — but it is not logged.)
- The re-check samples the enemy state at the **instant just before the cast**, not at the instant the effect resolves.
- `is_in_melee()` is the enemy's **self-state** ("in melee combat", with anyone). The log never records **whom** the enemy was fighting, so it cannot show the enemy was in melee *with the caster*.
- The selection line prints only the **arm** (`missile`/`melee`), not the raw boolean, at selection time; the boolean appears only in the re-check.
- **Build caveat:** this log was written by harness 94 (range constant 75 m) and harness 95 (52 m, the "70 % rule"). These builds gated the offer on `FOURTH.eg_enemy_in_range` = `unit:unit_in_range(enemy)` **or** `unit:unit_distance(enemy) <= 75/52` (`insert_ev_live.lua` 65–73). The **current** source (harness 96) gates instead on `FOURTH.eg_enemy_within_contact` = `unit:unit_distance(enemy) <= FOURTH.CONTACT_BOUND_M` (10 m) (lines 5509–5513, 5606). The log therefore describes **older behaviour** than the checked-out source.

### Question 2 — verdict
If the dispute is about an **enemy-targeted cast whose enemy was only being shot at**, the log supports the user: the enemy was **not** in melee (`melee=false`); it satisfied the condition via the **missile arm** of an OR. The claim that the enemy "was in melee" is **not supported for the missile-arm casts** (the earliest ones; 19 of 26) and **is supported only for the 7 melee-arm casts**. The mod does log enough to answer; what it cannot show is the enemy's melee partner or its state at effect resolution. Confidence: **high** for the melee/shot flags as logged; **medium** on the "no read error" assumption.

---

## Question 3 — `target_intercept_range` and `effect_range`: what they mean

### Where they live

Both columns are in the table **`unit_special_abilities_tables`** (RPFM schema `schema_wh3.ron` opens it at line 247130; extracted as `unit_spec_abil.tsv`). The `Accusation` row (`unit_spec_abil.tsv`, key `wh_main_hero_abilities_accusation`) maps to the header as:

| col | field | value |
|---|---|---|
| 3 | `recharge_time` | 90.0 |
| 5 | **`effect_range`** | **0.0000** |
| 8 | `num_effected_enemy_units` | 1 |
| 13 | `target_enemies` | true |
| 14 | `target_ground` | false |
| 15 | **`target_intercept_range`** | **75.0000** |
| 33 | `ai_usage` | **`hex_melee`** |
| 37/38 | `additional_melee_cp` / `additional_missile_cp` | 75.0 / 75.0 |

So the mod's data reading is correct: **`effect_range = 0.0`, `target_intercept_range = 75.0`, `ai_usage = hex_melee`, `target_enemies = true`, `target_ground = false`, `num_effected_enemy_units = 1`.** (Footnotes: the "75.0" is not unique — `additional_melee_cp` and `additional_missile_cp` are also 75.0; and the row's `35.0000` is `active_time`, not a range. `unit_abilities.tsv` confirms the key is `wh_type_hex`, `active`.)

### RPFM schema text (the closest thing to official)

`schema_wh3.ron`, `unit_special_abilities_tables`, version 74:

```
name: "effect_range",        field_type: F32, ... description: "",
name: "target_intercept_range", field_type: F32, ... description: "",
```

**Both `description` fields are empty.** RPFM ships semantic text for many columns, but **neither of these two has any** — so the schema is *silent*, not supporting either interpretation. Confidence: **very high** (verbatim).

⚠️ **A trap worth recording.** The string `"Time to look ahead to predict future position of target (intercept vs pursuit)."` does exist in `schema_wh3.ron` — but **not** in the abilities table. It is the `lookahead_time` field of **`projectile_homing_params_tables`** (line 196164 onwards, field at 196192). That is **projectile homing lead-prediction**, a different table entirely. Any "intercept = pursuit" reading that leans on this text is **misattributed**.

### Game code usage

**No Lua in the shipped game references either column.** `grep target_intercept_range|effect_range` over the extracted battle scripts and the archive `WH3-scripts` returns nothing. Both columns are consumed by the engine (C++) only; they appear in no script, so there is no script-level comment or call site to cite. This is why the RPFM schema and community docs matter.

### Community documentation

**Cryswar's "Creating and Editing Abilities"** (Steam guide, `id=1698960734`; also mirrored at steamsolo), read live — verbatim:

> "**Effect Range** is self explanatory for the most part - 40 range means 40 range - but similar to the last one, -1 means mapwide. **0 means self-only.**"

> "**Target Intercept Range** is how close to the target you have to be to successfully cast the spell."

> "**Min Range** is how far away from the caster you have to start the spell."

**CA hotfix 6.2.2** (patch notes, `community.creative-assembly.com`), verbatim:

> "Wrath of Khorne - **Target Intercept Range: 60 -> 100**"
> "Slime Trail - **Effect Range: 15 -> 35**"

**CA balance thread** (Preyton/Endless Malice), verbatim:

> "Increase the target intercept range of *Endless Malice* to 55m. … The activation condition of *Perfect Predator* remains too easy to trigger due to the fairly forgiving target intercept range."
> "…routing units naturally move away from combat and therefore the Preyton's position, reducing the uptime of this passive ability."

Here `target_intercept_range` is described as the **proximity range at which the ability triggers/activates** — **not** a movement instruction.

**TWA fandom wiki** ability pages use "Effect range" as the **area** of an ability, e.g. *Stand Your Ground!*: "Effect Range 35 metres … Affects allies in **range(all)**", and spells show a separate "Range" (e.g. 200 m) with a distinct "Effect range (Overcast) 35 metres". This comports with `effect_range` = area radius.

### So what do the two columns mean?

Cross-referencing the above, the best-supported reading is:

- **`target_intercept_range` = the maximum range at which the ability can be **cast at / activated on** a target** (i.e. **the cast/trigger range**). Community: *"how close to the target you have to be to successfully cast the spell"*; CA balance notes treat it as the passive's activation proximity. **For Accusation this is 75 m — so the user's statement "the cast range IS 75 m" is supported by the documentation.** Confidence: **high** from community sources; **the RPFM schema offers no contradicting text** (it has none).
- **`effect_range` = the radius of the area over which the effect is applied**; **0 = self-only / single-target, no aura** (Cryswar: *"0 means self-only"*; wiki: "Effect range 35 metres, affects allies in range(all)"). **For Accusation `effect_range = 0` — consistent with a single-target enemy hex (`num_effected_enemy_units = 1`).** Confidence: **high**.

### Is the "pursuit range causing movement" claim supported?

**Contradicted / not supported (as documented).** The only documentation that speaks to the column defines it as *a cast/activation range* — a *proximity requirement*, not a movement or pursuit order. The mod's own comment states the claim (lines 4111–4114, 5448–5453, 5470–5472):

> "…`target_intercept_range`, which is the reach at which the unit INTERRUPTS what it is doing to WALK AND INTERCEPT a target: a PURSUIT range, not a cast range."

Nothing I found supports "the engine walks the caster to intercept" as the *meaning* of the column. The apparent support in the RPFM schema (`"…intercept vs pursuit"`) belongs to **`projectile_homing_params_tables`**, a different table. **Verdict: the claim as stated is unsupported by, and in tension with, the available documentation.** Confidence: **medium-high** on "the column is a cast/trigger range"; **medium** on the negative "it is not a pursuit range", because the engine's runtime behaviour is not documented anywhere I could read.

**What is genuinely undetermined:** whether the **engine**, when handed a special-ability command for a target **outside** the ability's usable range, *also* issues a move-into-range order. No source documents the engine's cast-refusal/approach behaviour, and no probe isolated it. So "the column *means* a pursuit range" is contradicted; "the engine *ever* walks a caster as a side effect" remains **undetermined**.

### Alternative explanations for the unit stepping after a scripted cast

None of these is established by the evidence; listed as competing hypotheses, all consistent with the log (`0` skips, casts accepted, commands issued):

1. **An explicit order implied by the ability's class.** Accusation is `ai_usage = hex_melee`; the shipped engine's own "acquire a nearby enemy and attack it" loop calls `uc:attack_unit(enemy, true, true)` (`lib_battle_script_unit.lua:1928`). A melee-classed hex may legitimately drive an attack/approach.
2. **Cast refused → engine queues "move into range, then cast".** A common RTS pattern; would look like the unit walking toward the target. Not documented, not yet probed.
3. **Cast/wind-up animation repositions the caster.** `wind_up_time` exists for Accusation (row value 0.0), but animations can shift a unit without an explicit order.
4. **The unit already had a move order** (player or AI), independent of the cast. `battle_unit:ordered_position()` returns the current position "if the unit is attacking, as opposed to moving" — so move-vs-attack can be probed, but the log did not isolate it around these casts.
5. **Cooldown/guard re-approach.** Several casts show `REJECTED (on cooldown)`; a refused cast plus the 2 s guard could be followed by re-positioning, though this would not itself move the unit.

Only hypotheses 1–2 require the engine to move the unit "because of the cast"; 3–5 do not.

### Question 3 — unknowns
- The engine's runtime treatment of `target_intercept_range` is undocumented; the RPFM schema gives no text.
- Whether the engine walks a caster that is out of range is undetermined.
- The community guide is authored (not official) — it is the most explicit source found, but it is one person's modding guide plus CA patch-note wording, not a CA data dictionary.

---

## What this implies for the mod

Presented neutrally; no recommendation is required where the evidence is silent.

**On distance semantics (Q1)**
- `unit:unit_distance(enemy)` is an **edge-to-edge (bounding-box)** value, by engine doc. Any threshold the mod applies to it (e.g. `CONTACT_BOUND_M = 10`) is an **edge gap**, not a centre distance — worth stating wherever such a constant is documented, so the number is interpreted correctly.
- The API exposes **no unit radius/footprint**, so an edge figure cannot be converted to a centre figure at runtime; a gate expressed as "edges within N m" is the only cheaply available form.
- Whether a unit-targeted cast resolves at the target's edge, centre, or per-entity is **not observable** from the sources examined.

**On the in-melee condition (Q2)**
- The trigger is an **OR**: `enemy:is_in_melee()` **or** `enemy:is_under_missile_attack()` (plus, in the current source, `unit_distance ≤ CONTACT_BOUND_M`).
- In the logged battles the earliest casts fired on the **missile arm with the enemy not in melee** (`melee=false`); 7 later casts fired on the melee arm. If the intent is "the enemy must be *in melee*", the OR currently admits the missile state; if the intent is the user's verbatim rule ("in melee **or** being shot at"), the logged behaviour matches the rule.
- The log records the enemy's `melee=`/`shot=` booleans but **not** the melee partner; if the distinction "in melee *with the caster*" vs "in melee with anyone" matters, `is_in_melee()` alone cannot supply it and extra logging would be needed.
- The current source (harness 96) already adds a `unit_distance ≤ 10 m` contact gate that the logged build (harness 94/95, 75/52 m) did **not** have — so the log describes the older, looser gate.

**On the range column (Q3)**
- The documentation treats `target_intercept_range` as the **cast/trigger range** (75 m for Accusation) and `effect_range` as the **effect area radius** (0 = self-only). On that reading, "the cast range IS 75 m" is supported and "intercept range is a pursuit range that causes movement" is not.
- The mod's decision to **not** derive a constant from `target_intercept_range` for a no-aura ability can still be framed purely as a *policy* choice (fire only at melee contact), independent of whether the column is a cast range — but the code comments' factual justification ("a PURSUIT range") is **not supported** by the evidence gathered and could be corrected to say "a cast/trigger range per community docs; RPFM schema silent".
- The step-toward-target behaviour after a scripted cast remains **unexplained by the evidence**; the candidate causes (attack-order implied by `hex_melee`, engine move-into-range, animation, a pre-existing move order) are listed above and none is yet distinguished by a probe.

---

## Appendix — source excerpts used

- `battle_unit.lua` 160–163 (`unit_distance`), 114–116 (`position`), 135–137 (`ordered_width`), 155–158 (`unit_in_range`), 218–220 (`is_in_melee`), 214–216 (`is_under_missile_attack`), 122–125 (`can_reach_position`).
- `script_unit.lua` 485–487 (`script_units:radius`), 150–153 (`script_unit:is_in_melee`); `lib_bsu.lua` 2603–2617 (radius impl), 3825 (`get_closest ... < 70`).
- `zz_test_deadly_onslaught.lua` 3464–3483 / 4636–4637 (charge `dist`/`gap`), 4363–4396 (pre-cast re-check), 5509–5513 / 5578–5637 (enemy evaluator), 4105–4130 (RANGE_FRACTION / CONTACT_BOUND_M comments).
- `insert_ev_live.lua` 62–104 (harness-94 in-range + missile read), 134–196 (evaluator); `pre95_live.lua` 4340–4365 (re-check that wrote the log).
- Runtime log lines cited above (L572569–L572581, L572664, L572781, L578750, L585092, etc.); counts: 26 pre-cast re-checks, 0 skips, 505 target lines (224 melee / 281 missile), 9 "enemy under missile fire" ATTEMPTs, 19 battle restarts.
- `unit_spec_abil.tsv` header + `wh_main_hero_abilities_accusation` row; `unit_abilities.tsv` Accusation rows.
- `schema_wh3.ron` 247130 (`unit_special_abilities_tables` v74), 247195 / 247345 (`effect_range` / `target_intercept_range`, both `description: ""`), 196164–196192 (`projectile_homing_params_tables.lookahead_time`).
- Probe logs `zz_probe_unit_reads_log.txt` (`ordered_width` 1.12–29.42 m), `zz_probe_enemy_target_log_round4.txt` (`in_range=yes(unit_in_range)`).
- Community: Steam guide `id=1698960734` (verbatim Effect Range / Target Intercept Range / Min Range lines); CA hotfix 6.2.2 and balance-thread snippets; TWA fandom *Stand Your Ground!*.
