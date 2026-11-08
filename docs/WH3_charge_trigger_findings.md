# Does anything already do this? — charge-triggered ability activation in WARHAMMER III

Investigation date: **27 September 2026**. Game: Update 9.0 (24 Sep 2026).
Everything below is from files on this machine: the game's own 901 Lua scripts
(`script/`), the generated scripting API dump, and the game's database tables.

---

## The short answer

**No script does it. The game engine does — in the data layer, not in Lua.**

Three separate mechanisms exist, and only one of them can actually do
"activate only when charging":

| Mechanism | Can it fire an ability on "charging"? | Evidence |
|---|---|---|
| Lua (`perform_special_ability`) | **No — not accurately.** The scripting API does not expose the engine's charge state at all. | grep of the entire generated API, below |
| Engine AI (data tables) | **Yes**, but only for AI-controlled units. | `ai_usage = augment_charge_self`, `bool_charging`, below |
| Data-layer flags | **Yes — the engine's own state decides, exactly.** 10 vanilla abilities already work this way. | `special_ability_to_auto_deactivate_flags`, below |

---

## 1. Every vanilla script that fires an ability — 26 call sites, none conditional

`perform_special_ability` appears in exactly two kinds of file:

**Benchmarks** — fired on a fixed timer, unconditionally:

```lua
-- script/benchmarks/battle_benchmark/battle_benchmark.lua:303
bm:callback(
    function()
        --- Khorne Lord Buffing Himself ---
        sunit_kho_01.uc:perform_special_ability("wh3_main_lord_abilities_rage_embodied", sunit_kho_01.unit);
    end,
    32000          -- <- 32 seconds into the battle. No condition of any kind.
);
```

**One quest battle** — fired whenever the script reaches that point, with a
single "is it allowed right now" guard and no battle-state reasoning at all:

```lua
-- script/battle/quest_battles/tamurkhan/kayzk/battle_script.lua:144
if sunit.unit:can_perform_special_ability("wh3_dlc20_quest_passive_daemonblade_mages") then
    sunit.uc:perform_special_ability("wh3_dlc20_quest_passive_daemonblade_mages", sunit.unit)
```

`can_perform_special_ability` is used in only three places in the whole game,
and two of them are not about casting at all:

- `wh_battle_advice.lua:3065` — decides whether to **show a tutorial pop-up**
  ("you can turn into a dragon now").
- `quest_battles/malakai/vampires_empowered` — used as a **battle objective
  check** (did the player use the bomb).

Nothing polls the battle and fires an ability when a condition becomes true.
Also: **no vanilla script mentions `ai_usage`, `ability_usage` or
`intensity_based_activation`** — the engine's own ability decisions are compiled
code fed by data tables, not script.

## 2. The scripting API cannot see "charging"

Searching the entire generated API for anything charge-related returns only:

- `battle_unit:is_moving_fast()` — documented as *"whether the unit is moving
  fast (running/charging)"*. Running **or** charging. This is the ambiguity that
  caused the "it fired while just running" bug.
- `battle_unit:trigger_sound_charge()` / `script_unit:play_sound_charge()` — audio only.
- `move_fast` — a parameter on attack orders. Also audio-free, also not a query.
- `unit_is_not_charging` — a *database flag*, not a function.

There is **no** `is_charging()`, no charge progress, no speed-toward-target.
The engine's own `bool_charging` exists (see below) but is not exposed to Lua.
So any Lua implementation can only ever *approximate* "charging" — which is
exactly the class of error we spent three rounds chasing.

## 3. The engine's own rule, for AI-controlled units

`unit_special_abilities` carries a column `ai_usage`. For both Deadly Onslaught
variants it is:

```
wh_main_character_abilities_deadly_onslaught   ai_usage = augment_charge_self
wh_dlc03_character_abilities_deadly_onslaught  ai_usage = augment_charge_self
```

And the AI's scoring rule for that usage type, from the data tables:

```
battle_ai_abilities_usage_templates_to_params_tables:
    bool_charging        -> template augment_charge_self, weight 1.0   <- the ONLY parameter

battle_ai_abilities_usage_template_names_tables:
    augment_charge_self, factor_bias 1.0

_kv_battle_ai_ability_usage_variables_tables:
    min_score_for_activation = 0.50
```

So the engine's rule is literally: **score = `bool_charging` × 1.0, activate when
score ≥ 0.5 — i.e. if and only if the unit is charging.** That is precisely the
behaviour wanted, and it confirms the target condition is "charging", not
"about to hit".

`bool_charging` is one of 74 parameters the engine can score abilities on
(alongside `bool_charged_at`, `bool_in_melee`, `bool_out_of_melee`,
`value_speed_current`, `value_speed_max`, `bool_standing_still`, …) — all
internal, none reachable from Lua.

## 4. The data layer already ships the feature — 10 vanilla abilities use it

This is the important find. There is a table:

```
special_ability_to_auto_deactivate_flags   (571 rows)
    columns: deactivate_flag, special_ability
```

83 distinct flags. The one that matters:

```
unit_is_not_charging   -> 10 abilities
```

and those 10 are all charge-only effects:

| ability | passive | active_time | recharge_time |
|---|---|---|---|
| `wh3_cp1_unit_passive_ferocious_charge` | **true** | 22 | 20 |
| `wh3_dlc20_unit_passive_murderous_charge` | **true** | 25 | 30 |
| `wh3_dlc25_character_passive_befouled_charge` | **true** | −1 | −1 |
| `wh_dlc07_unit_passive_impetuous` | **true** | 30 | −1 |
| `wh3_dlc24_unit_passive_bears_bulwark` | **true** | — | — |
| `wh3_dlc26_unit_passive_piggy_back_joust` | **true** | — | — |
| `wh3_dlc27_character_passive_war_cry` | **true** | — | — |
| *(3 more)* | | | |
| `wh_main_character_abilities_deadly_onslaught` | **false** ← today | 31 | 90 |

**The mechanism is: `passive = true` + a `unit_is_not_charging` row.** The engine
then switches the effect on while the unit charges and off when it stops, using
its own internal charge state — the same `bool_charging` the AI uses. No guess,
no polling, no timing error, and the numbers are untouched.

That is almost certainly what the existing Workshop mod does. **"Auto Abilities"**
(Welter, `id=3009989710`, last updated 30 Jul 2023, 518 subscribers, unmaintained
— the author now recommends a different mod) advertises triggers *Charging, In
melee, On cooldown, Health below 75%, Below 50% HP, Losing melee combat, Morale
wavering*, which map one-to-one onto this flag vocabulary:

| mod's trigger | database flag |
|---|---|
| Charging | `unit_is_not_charging` |
| In melee | `out_of_melee` |
| Health below 75% | `health_above_75%` |
| Losing melee combat | `winning_melee_combat` |
| Morale wavering | `morale_is_higher_than_wavering` |

…and its description says it changes only *when* abilities fire, never their
numbers — consistent with a flags-only edit.

**Not verified by reading its files.** SteamCMD's anonymous account cannot
download from a paid title's Workshop (`ERROR! Download item … failed
(Failure)`), and the mod is not in this machine's Workshop cache. To settle it
definitively: subscribe to it once, let Steam download it, and the pack can be
opened with RPFM and diffed against vanilla.

## 5. Dead ends checked and ruled out

- `battle_toggle_system.lua` — sounds like "toggle abilities", is actually
  **map barriers and buildable tower slots** in siege battles.
- `intensity_based_activation` (column on `unit_special_abilities`) — 25 vanilla
  abilities use it, but **all 25 are also `passive = true`**, so it does not give
  a click-ability automatic firing. There are no intensity-related tables and no
  intensity function in the API.
- `ai_planner` — can hand units to the AI (`add_units`, `attack_unit`,
  `rush_unit`, `move_to_position`, `defend_position`, `clear_objective`), and an
  AI-controlled unit *will* fire Deadly Onslaught on the charge automatically.
  But there is **no per-ability control**: you give up control of the unit
  entirely, its movement included. This is what the AI-delegation mods do.
- The 235-flag `special_ability_invalid_usage_flags` vocabulary — **contains no
  charge-related flag at all** (exact grep: 0 matches). `unit_is_not_charging`
  exists only as a *deactivate* flag, never as an invalid-usage flag. The
  invalid-usage mechanism can *block* an ability from being clicked; it cannot
  fire one.

---

## 6. What "Autoactivate" (Autumnchain) actually does — read from its own pack

Workshop item `id=3014120667`, downloaded by Steam to
`steamapps\workshop\content\1142710\3014120667\autoactivate.pack`, pack type
**Mod**, opened and decoded with RPFM (the schema had to be fetched first —
`UpdateSchemas` — or `DecodePackedFile` fails with *"Missing or invalid extra
data provided: schema"*).

**Contents — 8 files, 7 of them DB tables:**

```
db/battle_vortexs_tables/ztobeoverwritten_autoactivate                  0 rows
db/projectile_bombardments_tables/ztobeoverwritten_autoactivate         0 rows
db/projectiles_explosions_tables/ztobeoverwritten_autoactivate          0 rows
db/special_ability_to_auto_deactivate_flags_tables/autoactivate       433 rows
db/special_ability_to_invalid_target_flags_tables/autoactivate         27 rows
db/unit_abilities_tables/autoactivate                                 108 rows
db/unit_special_abilities_tables/!!autoactivate                       258 rows
text/db/autoactivate.loc
```

**It is the mechanism from section 4, applied by hand to 151 abilities.**

For Deadly Onslaught, before → after, from the mod's own table:

| column | vanilla | Autoactivate |
|---|---|---|
| `passive` | **false** | **true** ← it becomes a self-firing passive |
| `active_time` | 31 | 31 (unchanged) |
| `recharge_time` | 90 | **117** ← raised to offset that it now fires itself |
| `num_uses` | −1 | −1 (unchanged) |
| `ai_usage` | augment_charge_self | unchanged |

plus one row in the flag table:

```
special_ability_to_auto_deactivate_flags
    unit_is_not_charging  ->  wh_main_character_abilities_deadly_onslaught
```

**Across the whole mod:** 151 abilities flipped `passive: false → true`; 433
auto-deactivate rows covering 231 abilities, of which **14 use
`unit_is_not_charging`** (vanilla has 10); 9 `recharge_time` increases; 16
`target_intercept_range`, 5 `wind_up_time` and 4 `additional_melee_cp` tweaks;
107 ability keys that do not exist in vanilla (compatibility entries for other
mods — the `mixu_`, `elo_`, `str_`, `phy_` prefixes are Mixu's and others'
content).

**Additive, not destructive.** The files are named `autoactivate` and
`!!autoactivate`, not `data__`. Per the community modding convention, a table
file named anything other than `data__` is a **table fragment**: its rows are
merged into the vanilla table, and conflicts are settled by filename order
(`!` wins over letters). Naming a table `data__` is what replaces it wholesale.
So the vanilla 569 rows survive and the mod adds 433. Had they shipped it as
`data__`, 528 vanilla auto-deactivate rules would have vanished.

**Verdict: this mod does exactly what you asked for, engine-side.** No script,
no polling, no timing guess — the ability becomes a passive that the engine
switches on precisely while `bool_charging` is true, and the author pays for it
by lengthening the recharge from 90 s to 117 s.

**Compared with the Lua route:** same target behaviour, no approximation, no
maintenance of a polling loop — but it stops being a clickable ability, and
every ability it touches changes for *all* factions and AI units too, not just
your test unit.

## What this means for the mod

Two routes, and the second is strictly better:

**Route 2 (Lua, current build — Round 8)** — poll every 250 ms, approximate
"charging" from five signals, fire `perform_special_ability(key, unit)`. The
approximation can be made good (a replay of the real battle log now fires at
28 m out, 3.7 s before impact, on both genuine charges) but it is still an
approximation of a state the engine knows exactly.

**Route 1 (data — recommended)** — mark Deadly Onslaught `passive = true` and
add a `unit_is_not_charging` row to `special_ability_to_auto_deactivate_flags`.
The engine then applies it exactly while Boris charges, using the same internal
signal the AI uses for this very ability. Consequences to weigh:

- the ability stops being a clickable icon (it is a passive now);
- its duration/recharge fields still appear to apply to passives
  (`ferocious_charge` keeps 22 s / 20 s), so balance is probably preserved, but
  this should be confirmed in play;
- it is a database edit, so it needs re-checking after major patches — the same
  maintenance burden the popular "Too Many Activatable Skills" mod carries.
