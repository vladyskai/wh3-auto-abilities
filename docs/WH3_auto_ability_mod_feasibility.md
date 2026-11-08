# Could someone build a "toggle abilities so they auto-fire on a condition" mod for WARHAMMER III?

**Verdict: Yes. It is possible, it is well within the game's supported modding surface, and the pieces are all documented. But the version you'd actually want is a small programming project with one genuine unknown — not a weekend data edit.**

Investigation date: 26 September 2026 (game on Update 9.0). Everything below is read from the game's own shipped files, Creative Assembly's scripting interface, and a mod that is doing this today — not from memory.

---

## The one-paragraph answer

The game's battle engine exposes three levers to a modder: **data tables** (the numbers and flags the engine reads), **Lua scripts** (running code that can read battle state and issue orders, including "use this ability"), and the **battle AI** (which already auto-uses abilities, and which a mod can hand units to). Route 1 is how the existing Workshop mods are built — proven, cheap, but blunt. Route 2 is the one that would give you real per-ability conditional triggering, and every single function it needs exists and is documented. Route 3 is the cheapest of all but means giving up control of the unit.

What is **not** possible: adding new conditions to the engine's own data-driven system, or giving the player a menu where they map "ability X → condition Y" themselves. The condition vocabulary in the data layer is a fixed, shipped list. In Lua you can compute any condition you like — but only ones you, the mod author, coded. There is no user-facing trigger editor unless somebody writes one.

---

## Route 1 — Data tables: make the ability "passive" and bolt a condition onto it

This is what **Auto Abilities**, **Auto Abilities Foe Seeker** and **Too Many Activatable Skills** actually do. Here is the machinery, from the game's data.

**The ability list.** Two tables matter. `unit_abilities` is the master list of every ability plus its `source_type` (army / unit / spell),[12] and `unit_special_abilities` holds the battle parameters of each — **71 columns**, including one literally called `passive`.[6] The counts in that table: **1,884 abilities are `passive=false`** (you click them) and **1,289 are `passive=true`** (the engine applies them for you). So the "passive" pattern you'd be copying is already used 1,289 times in the shipped game — there is no shortage of working examples to clone.

Example row, verbatim from the game data (`wh_main_character_abilities_foe_seeker`): recharge 60 s, 25 s active, `passive = false`. The Foe Seeker submod's whole job was to flip that to passive and add a health condition.

**The condition vocabulary — a closed list of 235 flags.** The table `special_ability_invalid_usage_flags` is just a list of names,[7] and it is exactly the set the mods advertise:

| Category | Flags that exist (selection) |
|---|---|
| Health | `health_above_10%/20%/25%/50%/75%`, `health_below_25%/50%/75%`, `health_above_50%_base`, `hp_replenish_cap_reached` |
| Melee | `engaged_in_melee`, `out_of_melee`, `engaged_in_melee_anything`, `winning_melee_combat`, `losing_melee_combat`, `unit_is_attacking_rear_or_flank`, `unit_is_in_melee_breakoff` |
| Morale | `morale_is_wavering_or_lower`, `morale_is_broken_or_lower`, `morale_is_lower_than_half_of_base_morale`, `friendly_battle_leader_killed_or_routed` |
| Fatigue | `fatigue_is_below_active / winded / tired / very_tired / exhausted` |
| Magic | `mana_above_50%`, `mana_below_50%`, `mana_below_value_15`, `has_casting_ability`, `no_spells_active`, `no_enemy_spells_active` |
| Movement | `moving`, `not_moving`, `unit_is_not_charging`, `flying_currently`, `grounded`, `climbing`, `on_a_platform` |
| Ammo / missiles | `have_ammo_below_threshold`, `is_under_missile_fire`, `is_not_under_gun_fire` |
| Kills & proximity | `unit_tier1_kills`, `unit_tier2_kills`, `unit_tier3_kills`, `enemy_unit_died_within_range`, `enemies_in_intercept_range`, `troll_enemies_in_intercept_range` |
| Unit identity | `unit_is_large`, `unit_is_daemonic`, `unit_is_slayer`, `unit_is_skaven`, `undead_unit`, `living_unit`, `unit_is_not_single_entity` |

**How the condition is attached.** Two junction tables, both small and readable:

- `special_ability_to_auto_deactivate_flags` — **571 rows**, two columns: `deactivate_flag`, `special_ability`.[8] This is the switch. Real example rows: `health_above_50%` → `wh2_dlc09_character_passive_befalling_curse`; `hasnt_realm_of_souls_tier_3` → `wh2_dlc09_army_passive_realm_of_souls_ushabti_trigger`. The flag names the state in which the ability **turns itself off** — so the ability is live the rest of the time.
- `special_ability_to_invalid_usage_flags` — **705 rows**, same shape: the ability is simply unavailable while that flag is true.[9] A third sibling, `special_ability_to_invalid_target_flags` (755 rows), governs what it may be aimed at.

That is the whole trick, and it explains the quote from the Auto Abilities author: *"we cannot create new trigger conditions, we have to use those already in the game."* The 235 flags are shipped data. You can combine them in rows, but you cannot invent a new one.

**Route 1 assessment**

| | |
|---|---|
| Possible? | Yes — three mods on the Workshop are built this way |
| Skills needed | No programming. A database editor (RPFM[16]) and tables. |
| Effort | Hours for a handful of abilities; days to do all ~1,900 and tune them |
| Gives you | Real conditional firing (health/melee/charge/fatigue/morale…), zero clicking |
| Doesn't give you | An in-game toggle. The behaviour is baked into the mod, decided before the battle. |
| Cost | The ability usually must weaken: Too Many Activatable Skills cuts effect strength to a third because an always-on ability is far stronger than a 25-second one. |

---

## Route 2 — A Lua script that watches the battle and fires abilities itself

This is the version you asked about, and **it is possible. Every function required exists and is documented.**

**Step 1 — getting code into every battle.** The game ships an official mod loader. Its own source file says: *"The following allows modders to load their own script files without editing any existing game scripts. This allows multiple scripted mods to work together without one preventing the execution of another."*[5] In battle it loads everything in **`script/battle/mod/`** — in *campaign* battles, not just custom ones. The Community Bug Fix Mod ships a battle script on exactly that path, so this is live in a 100k-subscriber mod, not theory.[10] So: drop a `.lua` file in the mod's pack under that path and it runs in every battle.

**Step 2 — a heartbeat to run the checks on.** `bm:repeat_callback(function, milliseconds, "name")` re-runs your function on a timer, and the battle library also offers `callback` (one-shot), `remove_process` (cancel), watches (poll until a condition is true), and phase-change callbacks for deployment and combat start.[13][3] The bug-fix mod polls at **50 ms**.[10] That is the pattern you'd copy.

**Step 3 — firing the ability.** The documented functions:[2][19]

| Function | What it does |
|---|---|
| `battle_unitcontroller:perform_special_ability(ability_key, target_unit)` | Orders the unit(s) to use the named ability, optionally on a target |
| `battle_unitcontroller:perform_special_ability_q(ability_key, target_unit)` | Same but **queued** — starts when the unit's current order finishes, so it doesn't interrupt what it's doing |
| `battle_unitcontroller:perform_special_ability_ground(ability_key, position, orientation, width)` | For ground-targeted abilities |
| `battle_unitcontroller:reset_ability_cooldown(key)` / `reset_ability_number_of_uses(key)` | Override cooldown and use limits |
| `battle_army:use_special_ability(key, position, bearing, width)` | Army-level abilities (the "army abilities" bar) |

**Step 4 — checking whether it's legal to fire.** `battle_unit:can_perform_special_ability(key)` answers yes/no; `owned_special_abilities()`, `owned_passive_special_abilities()` and `owned_non_passive_special_abilities()` list what a unit actually has; `disable_special_ability(key, on/off)` turns one off.[1] This matters because the order is validated: issuing an ability that is not legal for any controlled unit raises a script error — so the correct pattern is *ask first, then fire*.

**Step 5 — reading the conditions.** All of these are exposed on each unit:[1] `unary_hitpoints()` (health as a 0–1 fraction), `unary_of_men_alive()`, `is_in_melee()`, `is_wavering()`, `is_routing()`, `is_crumbling()`, `fatigue_state()` (fresh/active/winded/tired/very_tired/exhausted), `is_moving()`, `is_moving_fast()` (running or charging), `current_target()`, `has_attribute(key)`, `is_currently_flying()`, `ammo_left()`, `is_under_missile_attack()`, `is_left_flank_threatened()` / `right` / `rear`, `strategic_value()`, `number_of_enemies_killed()`, `position()`, `unit_distance(other)`.

So every condition the existing mods advertise — and many they can't express — is readable in code. In Lua you can write arbitrary logic: *"fire Sword of Anti-Heroes when this character has been in melee for 4 seconds, is below 60% health, is not routing, and the ability isn't on cooldown."* None of that is expressible in the data layer.

**Step 6 — the toggle button.** `core:get_ui_root()` gets the interface root; `find_uicomponent(...)` finds an element; `UIC:CreateComponent(name, template_path)` creates a new component from an existing one as a template; `UIC:SetState(state_name)` switches its look; `AddScriptEventReporter()` delivers mouse-enter/mouse-leave events; `SetContextObject` attaches data to it.[11] Battle screens are layout files under `ui/battle ui/` (`hud_battle.twui.xml` and friends). Three current mods ship exactly such a button in the battle orders bar, which settles whether it's achievable in practice.

**The catch — control handover.** This is the honest risk, and I could not test it without the game running. The documentation on unitcontrollers states: *"A unitcontroller implicitly takes control of units to which it is assigned if an order is issued"*, and *"Should a unitcontroller take control of a player unit then the player will not be able to issue commands to it (the card belonging to the unit will appear greyed-out)."*[2] The API provides `take_control()` and `release_control()` precisely for this handover,[2] so the intended pattern is *take → fire → release*, and using the queued `perform_special_ability_q` avoids replacing the unit's existing order. Whether a momentary take/release is visually clean, whether it can cancel a player's order in edge cases, and how it behaves under high unit counts — that is an in-game test question, and any honest feasibility answer has to name it as the unknown rather than pretend it away.

**Route 2 assessment**

| | |
|---|---|
| Possible? | Yes — all required functions documented; each step is proven separately in shipping code |
| Skills needed | Real Lua programming: state polling, target selection, UI wiring |
| Effort | Weeks for something competent. The hard part is not the trigger — it's deciding *who* to target. Healing, buffs and hexes need a target unit chosen sensibly; that logic is the bulk of the work. |
| Gives you | Exactly what you asked for: per-ability conditions, an in-battle on/off toggle, full-strength abilities |
| Risks | Control handover side effects; performance of polling every unit several times a second in large battles; each new game patch may break it (script mods break more often than data mods) |
---

## Route 3 — Hand the unit to the game's own battle AI

The game's AI already uses abilities, so the cheapest mod is one that simply lends it your unit. `ai_planner:add_units(...)` and `ai_planner:remove_units(...)` add units to the AI planner for your side, with `attack_unit`, `rush_unit`, `move_to_position`, `defend_position`, `clear_objective` for direction.[4] That is the mechanism behind **AI Army Control** (whose page says it "makes extensive use of Total War: WARHAMMER III's native battle AI planner")[18] and the AI General family.

How eagerly the AI spends abilities is itself data-driven: `_kv_battle_ai_ability_usage_variables_tables` holds knobs like `min_score_for_activation = 0.5` and `mana_saving_threshold = 0.1`, and every ability carries an `ai_usage` tag in `unit_special_abilities` (e.g. `augment_melee_self`, `aoe_bombardment`, `threatened`, `healing`).[6]

**Assessment:** possible, hours not weeks, and the most actively maintained mods on the Workshop do it. But it is not the thing you asked for — you get "the AI plays this unit now", not "this ability fires when this condition is met", and you lose manual control of that unit.

---

## What cannot be done

1. **No new conditions in the data layer.** The flag list is shipped, fixed, 235 entries.[7] You cannot add a flag; you can only attach the existing ones to abilities.
2. **No in-game trigger editor.** Nothing in the scripting interface exposes a settings UI for defining conditions. You could ship a settings panel built on the **Mod Configuration Tool** (an in-game settings API for Lua mods — 771,420 subscribers, last updated 19 July 2026)[14] so the player can tick "auto-cast for these categories" — but the logic behind each tick is still code you wrote. There is no general "map any ability to any condition" editor, and building one is a much larger project than the mod itself.
3. **No preserving an ability's full power for free.** An always-on version of a 25-second ability is strictly stronger; the existing mods compensate by cutting effect strength, which is a design decision you inherit.
4. **No guarantee it survives patches.** Data-only mods survive most patches; script mods break when the interface changes. Update 9.0 shipped two days ago; the freshest ability mod predates it.

---

## If you (or someone) actually wanted to build it

**The cheapest useful version — Route 1, one evening, no programming.** Install RPFM (free, MIT, actively developed — last commit 25 September 2026),[16] open the game's data, and for a short list of abilities flip `passive` to true and add one row per ability to `special_ability_to_auto_deactivate_flags`. Test in custom battles. This is literally how Auto Abilities was made — its author said he learned enough to build it "in about 1 to 2 hours having no prior modding experience."

**The version you'd want — Route 2.** Order of work:
1. RPFM + Visual Studio Code setup, with RPFM's exported Lua definitions for autocomplete.[17]
2. A `script/battle/mod/<name>.lua` file that gets auto-loaded, registering a repeating callback.
3. Per-unit loop: read conditions → decide → `can_perform_special_ability` → `perform_special_ability(_q)`.
4. A curated per-ability table of trigger rules and target-selection rules (this is where the weeks go).
5. A toggle button on the battle HUD, plus persistent settings via MCT.[14]
6. In-game testing loop with the **Lua Console** mod, which runs Lua inside the running game (Shift+F3).[15]

**Skills it needs:** Lua, some UI layout, and patience with a proprietary engine you can't step-debug. Your industrial controls background is honestly the right mental model — it is loop checking: read the process variable, compare against a setpoint, drive the output, and handle the interlock (here, the interlock is *don't steal the player's control of the unit*).

**My blunt read on the market gap:** a conditional auto-cast mod doesn't exist because the *easy* version (Route 1) is a two-hour data edit that one person did and 5,465 people subscribed to, and the *good* version (Route 2) is a multi-week engineering job with per-ability tuning that nobody has been paid to do. The gap is not technical impossibility. It's effort versus reward.

## Sources

[1] https://chadvandy.github.io/tw_modding_resources/WH3/battle/battle_unit.html — WH3 battle scripting doc: Unit (ability + condition functions)
[2] https://raw.githubusercontent.com/LyciaPintella/Total-War-Warhammer-III-Lua-Library-Documentation/main/battle/battle_unitcontroller.lua — WH3 Lua library dump: battle_unitcontroller (perform_special_ability)
[3] https://chadvandy.github.io/tw_modding_resources/WH3/battle/battle_index.html — WH3 Battle Index (script loading, phases, timers, watches)
[4] https://raw.githubusercontent.com/LyciaPintella/Total-War-Warhammer-III-Lua-Library-Documentation/main/battle/ai_planner.lua — WH3 Lua library dump: ai_planner (add_units)
[5] https://raw.githubusercontent.com/Shazbot/WH3-Dump/main/script/_lib/lib_mod_loader.lua — Game file: script/_lib/lib_mod_loader.lua (the mod loader)
[6] https://raw.githubusercontent.com/Shazbot/WH3-Dump/main/db/unit_special_abilities_tables/data__.tsv — Game data: unit_special_abilities table (71 columns, incl. passive)
[7] https://raw.githubusercontent.com/Shazbot/WH3-Dump/main/db/special_ability_invalid_usage_flags_tables/data__.tsv — Game data: the 235 condition flags
[8] https://raw.githubusercontent.com/Shazbot/WH3-Dump/main/db/special_ability_to_auto_deactivate_flags_tables/data__.tsv — Game data: special_ability_to_auto_deactivate_flags (571 rows)
[9] https://raw.githubusercontent.com/Shazbot/WH3-Dump/main/db/special_ability_to_invalid_usage_flags_tables/data__.tsv — Game data: special_ability_to_invalid_usage_flags (705 rows)
[10] https://raw.githubusercontent.com/chadvandy/cbfm_wh3/main/script/battle/mod/zzz_cbfm_cacophonous_assault.lua — Working example: battle mod using repeat_callback + use_special_ability
[11] https://raw.githubusercontent.com/LyciaPintella/Total-War-Warhammer-III-Lua-Library-Documentation/main/battle/uicomponent.lua — WH3 Lua library dump: uicomponent (CreateComponent, SetState, mouse callbacks)
[12] https://raw.githubusercontent.com/Shazbot/WH3-Dump/main/db/unit_abilities_tables/data__.tsv — Game data: unit_abilities table (source_type army/unit/spell)
[13] https://chadvandy.github.io/tw_modding_resources/WH3/battle/battle_manager.html — WH3 Battle Manager doc (callbacks, phases)
[14] https://steamcommunity.com/sharedfiles/filedetails/?id=2927955021 — Mod Configuration Tool (MCT) for WH3 - in-game settings API
[15] https://steamcommunity.com/sharedfiles/filedetails/?id=2791799449 — Modding Development Tools: Lua Console (test code in-game)
[16] https://github.com/Frodo45127/rpfm — RPFM - Rusted PackFile Manager (DB editing + .pack creation)
[17] https://tw-modding.com/wiki/Lua/Setup — Total War Modding wiki: Lua setup (RPFM + VS Code workflow)
[18] https://steamcommunity.com/sharedfiles/filedetails/?id=3787823404 — Steam Workshop: AI Army Control (uses native battle AI planner)
[19] https://raw.githubusercontent.com/LyciaPintella/Total-War-Warhammer-III-Lua-Library-Documentation/main/battle/battle_army.lua — WH3 Lua library dump: battle_army (use_special_ability)
