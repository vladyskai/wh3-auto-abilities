# WH3 Enemy Targeting in Battle Lua — Community Findings

Research date: 2026-10-09. Method: web searches across Total War Center, the TWA fandom wiki,
r/totalwar / r/totalwarhammer, Steam Workshop, and GitHub mod repos, plus full-page extracts of the
most promising hits. ~20 distinct queries were run (several phrasings, `site:` operators where the
backend supported them); the key sources were then read in full. All quotes below are verbatim from
the named source.

Note on source quality: Creative Assembly's own WH3 battle-scripting documentation is not hosted by
CA publicly any more; the two URLs the community actually uses are mirrors of that CA documentation
(`chadvandy.github.io/tw_modding_resources/` and `go.recoveringme.com/WH3/`) plus a GitHub repo
(`LyciaPintella/...-Lua-Library-Documentation`) that auto-generates the same CA docs into `.lua`
stubs. Where these agree on a signature I treat them as "official doc (community mirror)".

---

## PART A — The API surface (official CA docs, community-mirrored)

### Finding A1 — `perform_special_ability` DOES accept an optional target unit
- **Claim:** The unit-controller ability call takes an optional `battle_unit` target. The doc does
  **not** restrict that target to friendly units (contrast the `attack_unit` variant, which *does*
  say "This must be an enemy unit").
- **Source:** https://chadvandy.github.io/tw_modding_resources/WH3/battle/battle_unitcontroller.html
  (mirror: http://go.recoveringme.com/WH3/battle/battle_unitcontroller.html)
- **Quote:** "`unitcontroller:perform_special_ability(string ability key, [battle_unit target unit])`
  Issues an order to the units associated with this unitcontroller to perform the supplied special
  ability. Special abilities are listed in the `unit_special_abilities` table. An optional unit
  target may be specified."
- **Reliability:** Official doc (community mirror). **High.** No friendly-only qualifier present.

### Finding A2 — queued variant behaves the same
- **Claim:** `perform_special_ability_q` also takes the optional target unit.
- **Source:** same page.
- **Quote:** "`unitcontroller:perform_special_ability_q( string ability key, [battle_unit target
  unit])` Issues a queued order to the units associated with this unitcontroller to perform the
  supplied special ability. ... An optional unit target may be specified with the second argument."
- **Reliability:** Official doc. **High.**

### Finding A3 — positional ground-cast variant exists
- **Claim:** `perform_special_ability_ground(ability_key, position, orientation, width)` issues the
  ability at a `battle_vector` position (no unit needed) — useful for ground-target AoE hexes.
- **Source:** https://raw.githubusercontent.com/LyciaPintella/Total-War-Warhammer-III-Lua-Library-Documentation/main/battle/battle_unitcontroller.lua
  and the chadvandy unitcontroller page.
- **Quote:** "`function battle_unitcontroller:perform_special_ability_ground(ability_key, position,
  orientation_in_degrees, width_in_m) end`" — doc: "Issues an order ... to perform the supplied
  special ability on a specified position (can support orientation and width)."
- **Reliability:** Official doc. **High.**

### Finding A4 — scripts CAN drive the unit controller's ability use (full ability API)
- **Claim:** The `battle_unitcontroller` interface (reached from a script unit via the `.uc` field)
  exposes a full special-ability API.
- **Source:** chadvandy unitcontroller page + LyciaPintella `battle_unitcontroller.lua`.
- **Quotes / signatures found:**
  - `unitcontroller:perform_special_ability(ability_key, [target])`
  - `unitcontroller:perform_special_ability_q(ability_key, [target])`
  - `unitcontroller:perform_special_ability_ground(ability_key, position, orientation, width)`
  - `unitcontroller:reset_ability_cooldown(ability_key)`
  - `unitcontroller:reset_ability_number_of_uses(ability_key)`
  - on the unit side: `unit:can_perform_special_ability(special ability key)` and
    `current_special_ability`
  - in `lib_battle_script_unit.lua`: "`su.uc = create_unitcontroller(unit)`" — every script unit
    carries a unitcontroller.
- **Reliability:** Official doc + vanilla library source. **High.**

### Finding A5 — there ARE enemy equivalents of `get_scriptunits_for_local_players_army`
- **Claim:** The battle manager exposes several functions to get the **enemy** army/alliance and its
  script units — no need to hack anything.
- **Sources:** https://chadvandy.github.io/tw_modding_resources/WH3/battle/battle_manager.html and
  the mirror http://go.recoveringme.com/WH3/battle/battle_manager.html
- **Quotes:**
  - "`battle_manager:get_scriptunits_for_army( number alliance id, number army id, [number
    reinforcement units id])` : Gets an automatically-generated `script_units` collection object
    containing a `script_unit` for every unit in the specified army. ... Alliances are specified by
    1-based index, currently either `1` or `2`."
  - "`battle_manager:get_scriptunits_for_main_enemy_army_to_local_player()`" (listed on the page)
  - "`battle_manager:get_non_player_alliance()` : Returns the alliance object of the local player's
    enemy." and "`battle_manager:get_non_player_alliance_num()`".
  - "`battle_manager:get_first_non_player_army()` ... `@return battle_army #enemy army`"
  - On script_unit: "`script_unit:get_enemy_alliance()` : Gets the enemy alliance object." and
    "`script_unit:get_enemy_alliance_num()`"
- **Reliability:** Official doc (community mirror). **High.** This directly answers the "enemy
  equivalent" question: yes, `get_scriptunits_for_army(2, n)` / `get_scriptunits_for_main_enemy_army_to_local_player()`
  / `get_non_player_alliance()` all exist.

### Finding A6 — older official doc shows the *pre-target* signature (context)
- **Claim:** The older engine-level "Battle Script Documentation" (historical-battle era, CA wiki)
  lists `perform_special_ability(String ability_name)` with **no** target argument. The WH3-era docs
  (A1) added the optional `target unit`.
- **Source:** https://wiki.totalwar.com/w/Battle_Script_Documentation.html
- **Quote:** "`perform_special_ability` nil `perform_special_ability(String ability_name)` Orders
  units to perform a special ability."
- **Reliability:** Official but older engine doc. **Medium** for WH3; useful only to show the target
  parameter is a later addition.

---

## PART B — A real, public, working mod that targets an enemy unit

### Finding B1 — `DasAng/warhammer_mind_control_spell` (WH3, Lua) — the closest real example
- **Claim:** A public WH3 mod creates a custom spell that lets the caster **select and control an
  enemy unit** for 1 minute, and states it "lays the foundation ... [for] other spells that target
  enemy units."
- **Source:** https://github.com/DasAng/warhammer_mind_control_spell and the author's write-up
  https://dasang.github.io/blog/warhammer_mod/
- **Quotes:**
  - Repo README: "This custom spell lays the foundation and showcases how you can create other
    spells that targets enemy units. The mod relies heavily on Lua scripting."
  - Blog: "the objective of this mod would be to create our own spell that introduces a new gameplay
    mechanic: the ability to control an enemy unit for a brief period... This would lay the
    foundation for doing all kinds of spell that can target enemy units."
- **Reliability:** Public working code + detailed author write-up. **High** for the mechanism.

### Finding B2 — HOW the mod obtains enemy handles (the actual technique)
- **Claim:** The mod iterates the enemy alliance's armies and units and wraps each in a `script_unit`,
  proving battle scripts can hold handles to enemy units.
- **Source:** repo file `script/battle/mod/ang_mind_control_spell.lua` (via
  https://raw.githubusercontent.com/DasAng/warhammer_mind_control_spell/master/script/battle/mod/ang_mind_control_spell.lua)
  and the blog.
- **Quote (verbatim code):**
  ```lua
  MindControl.activateMindControl = function()
      ...
      local armies = bm:get_non_player_alliance():armies()
      for i = 1, armies:count() do
          local army = armies:item(i)
          local units = army:units()
          for j = 1, units:count() do
              local unit = units:item(j)
              if unit and not unit:is_commanding_unit() then
                  local sunit = script_unit:new_by_reference(army, unit:name())
                  sunit:add_ping_icon(2,mindControlDurationSelection)
                  MindControl.mindControlUnits:add_sunits(sunit)
              end
          end
      end
  end
  ```
- **Reliability:** Working public code. **High.** This is a concrete answer to "how mods obtain enemy
  handles."

### Finding B3 — the mod drives an enemy unit's unitcontroller
- **Claim:** Once an enemy `script_unit` is held, its `.uc` (unitcontroller) and script-unit methods
  are used to issue orders.
- **Source:** same Lua file / blog.
- **Quote (verbatim code):**
  ```lua
  MindControl.moveEnemyEast = function()
      if MindControl.selectedMindControlUnit then
          MindControl.selectedMindControlUnit:stop_attack_closest_enemy()
          local pos = MindControl.selectedMindControlUnit.unit:position()
          local newpos = battle_vector:new(pos:get_x()+100,pos:get_y(),pos:get_z())
          MindControl.selectedMindControlUnit.uc:goto_location(newpos, true)
      end
  end
  ```
  (plus `:halt()` and `:start_attack_closest_enemy()` further down.)
- **Reliability:** Working public code. **High.**

### Finding B4 — the mod's explicit statement about "directly targeting an enemy unit"
- **Claim:** The author states the engine has **no inherent method to directly target an enemy unit**
  for the *player-facing click-to-select* interaction, and works around it by overlaying a clickable
  ping icon and reading the UI-click event. This is the single most-cited "limitation" statement
  found, and it is specifically about **UI targeting**, not about whether a script can reference an
  enemy handle.
- **Source:** https://dasang.github.io/blog/warhammer_mod/
- **Quotes:**
  - "In the game mechanics, there's no inherent method to directly target an enemy unit. Spell
    functionalities typically revolve around modifying database parameters such as spell range or
    target selection criteria, rather than providing direct control over spells via Lua scripts."
  - "the game itself doesn't seem to handle events where you can point and click on an enemy unit, at
    least not in an obvious manner."
  - Workaround: "I've discovered a workaround by leveraging the game function called `add_ping_icon()`
    ... This function essentially enables us to overlay a clickable UI icon onto any unit ...
    When clicking on the icon, the game triggers events to the Lua script ... allowing us to identify
    the targeted unit."
  - "By clicking on a UI component on the battlefield and determining the ID of the enemy unit from
    the clicked UI component, we've essentially enabled ourselves to apply various actions on the
    enemy unit dynamically."
  - "This opens the door to many more potential custom spells in the future, allowing us to perform a
    variety of actions targeting enemy units through Lua scripting."
- **Reliability:** Author's own write-up about his working mod. **High** as a statement of what he
  found; **note** it is one modder's account, not a CA statement, and it is contradicted in part by
  his own code (which freely holds enemy handles) — so read it as "there is no built-in
  click-to-target-an-enemy hook", not "scripts cannot reference enemies".

### Finding B5 — the mod does NOT itself use `perform_special_ability` at an enemy
- **Claim:** The DasAng mod targets/controls an enemy via movement/attack orders through the
  unitcontroller; it does **not** demonstrate `perform_special_ability("hex", enemy_unit)`. So it
  proves enemy handles + unitcontroller control, but not the specific "auto-cast a debuff at an
  enemy" call.
- **Source:** full read of `ang_mind_control_spell.lua` (only `uc:goto_location`, `halt()`,
  `start_attack_closest_enemy()` used).
- **Reliability:** Direct code inspection. **High.** (This is a gap, stated plainly.)

---

## PART C — Auto-cast mods on Steam Workshop (player automation)

### Finding C1 — several auto-cast/automation mods exist, but none is documented as a script that
targets enemies programmatically
- **Claim:** WH3 Workshop has popular mods that automate the player's own ability/spell casting, but
  their descriptions describe gizmo/UI toggling and interval-based casting, not a documented
  script API that fires a debuff at a chosen enemy.
- **Sources & quotes:**
  - "Auto Abilities" (Welter) — https://steamcommunity.com/sharedfiles/filedetails/?id=3009989710 :
    "So I had enough of having to Micro my Lord and turn on his 5 active abilities at a perfect time
    while still microing the rest of my army." (self-buff activation via active-skill toggles.)
  - "Auto-Cast Specialist Commands" — https://steamcommunity.com/sharedfiles/filedetails/?id=3459647882 :
    "Auto-Casting for each Command ability can be toggled by right clicking the ability gizmo, or in
    the mod settings."
  - "AutoCast" — https://steamcommunity.com/sharedfiles/filedetails/?id=3501038025 :
    "This mod automates the process of casting spells from the Grimoire. Features: -Automatic Spell
    Casting: Automatically casts your chosen spell at a set interval."
  - "AI General: Unified Tactics" — https://steamcommunity.com/sharedfiles/filedetails/?id=3727310475 :
    "Puts Lords and characters to work casting spells and using special abilities."
- **Reliability:** Workshop descriptions (marketing-level; mechanism not inspected). **Medium** as
  evidence that automation exists; **do not** cite as proof of any specific API. (Direct page extracts
  timed out; content is from search snippets.)

---

## PART D — Total War Center, Reddit, and the TWA fandom wiki

### Finding D1 — Total War Center has no WH3-specific "target an enemy with an ability" recipe
- **Claim:** TWC's battle-scripting threads found are for older/historical engines (Rome/Medieval II
  scripting language), not WH3 Lua. They show that older engines labelled units and issued
  `unit_order_attack_unit`/`unit_order_attack_closest_unit`, but nothing matching WH3's
  `perform_special_ability`-at-enemy.
- **Sources:** 
  - TWC "TATW Battle Editor" thread: https://twcenter.net/threads/tatw-battle-editor-tutorials-help-manual-development.277519/page-3
    — quote: "`unit_order_attack_unit cavalry1 enemy4 run` ... Orders one unit to attack another"
    (Rome/Med-II `.txt` scripting, labels + monitors).
  - TWC "Modding Q&A's": https://twcenter.net/threads/modding-q-as.623782/page-5 — a modder notes:
    "All the battle scripting documentation I could find online was several games old and for
    historical battles, as far as I could tell."
  - TWC "All LUA functions ... exposed by Empire": https://twcenter.net/threads/all-lua-functions-variables-modules-exposed-by-empire.243201
    lists `perform_special_ability` / `perform_special_ability_q` as engine functions (Empire era),
    confirming the name predates WH3 but giving no WH3 enemy-target usage.
- **Reliability:** Community forum, older engines. **Medium** as background; **no** WH3 recipe.

### Finding D2 — Reddit (r/totalwar, r/totalwarhammer) is player-level, not a scripting recipe source
- **Claim:** Reddit threads discuss spell/ability *balance* and player micro, not Lua targeting. The
  one relevant pointer is that modders direct people to the full CA scripting API and to the modding
  Discord for Lua help.
- **Sources:**
  - https://www.reddit.com/r/totalwarhammer/comments/1n6a4jk/peg_leg — "The full scripting API is
    available here if you're interested. There is quite a bunch about battle scripting..."
  - https://www.reddit.com/r/totalwarhammer/comments/1cavfbo/making_my_own_mods/ — "If you get into
    scripting, it's a mix of Lua and CA functions ... There is a discord for [modding] ... greytigergames
    has a number of lua tutorials for creating custom ui..."
- **Reliability:** Community hearsay. **Low–Medium.** Points to where expertise lives (Discord, CA
  API mirror, greytigergames tutorials) but contains no recipe.

### Finding D3 — the TWA fandom wiki has no scripting API
- **Claim:** `totalwarwarhammer.fandom.com` covers abilities/spells at a gameplay level (what a hex
  does, ability lists) but documents no battle-scripting API. Searches there returned only
  gameplay/ability catalogue pages.
- **Sources:** https://totalwarwarhammer.fandom.com/wiki/Abilities ,
  https://totalwarwarhammer.fandom.com/wiki/Total_War:_Warhammer_abilities
- **Reliability:** Not applicable to scripting. **Not useful** for this question.

---

## VERDICT

**Community consensus: casting/targeting an enemy unit from a WH3 battle script is possible in
principle, and the ingredients are documented — but nobody has published an end-to-end "auto-cast a
hex/debuff at an enemy" recipe.**

What the community record actually establishes:

1. **`perform_special_ability` accepts an optional `battle_unit` target** and is not documented as
   friendly-only (Finding A1/A2). The doc simply says "an optional unit target may be specified."
   There is **no** official statement anywhere that the target must be friendly.
2. **Enemy handles are easily obtainable** — this is the direct answer to the "enemy equivalent of
   `get_scriptunits_for_local_players_army`" question. It exists:
   - `battle_manager:get_scriptunits_for_army(2, n)` (alliance 2 = the non-player alliance),
   - `battle_manager:get_scriptunits_for_main_enemy_army_to_local_player()`,
   - `battle_manager:get_non_player_alliance()` / `get_first_non_player_army()`,
   - `script_unit:get_enemy_alliance()`.
   (Finding A5.)
3. **Scripts can drive the unitcontroller's ability use** — `perform_special_ability`,
   `perform_special_ability_q`, `perform_special_ability_ground`, `reset_ability_cooldown/number_of_uses`,
   plus `unit:can_perform_special_ability`. (Finding A4.)
4. A **real public WH3 mod** (DasAng mind-control) confirms battle scripts hold enemy unit handles and
   issue orders to them, and explicitly frames itself as the foundation for "spells that target enemy
   units." (Findings B1–B3.)
5. The **one "limitation" quote** the community leans on — "there's no inherent method to directly
   target an enemy unit" — is about the **player click-to-select UI**, not the script API, and the
   same author immediately works around it with `add_ping_icon()` + UI-click events and then applies
   arbitrary effects to the enemy. So it is **not** a "scripts cannot target enemy units" verdict.
   (Finding B4.)

**Is a working recipe documented?** Partially, but not assembled publicly.
- Documented pieces: the ability API takes a target; the enemy-handle functions exist; the technique
  for acquiring an enemy unit and driving it is published (DasAng).
- NOT found: any public snippet/mod that calls `perform_special_ability("<hex_key>", <enemy_unit>)`
  or otherwise auto-casts a debuff at an enemy, with code shown. (Finding B5.) The auto-cast Workshop
  mods automate the player's *own* casters and expose no enemy-targeting script example. (Finding C1.)
- No authoritative "this is impossible" source was found either. The strongest counter-claim is one
  modder's informal remark about UI targeting, which his own code contradicts.

**Bottom line for a builder:** The documented API strongly supports the approach
(get an enemy `script_unit` via `get_scriptunits_for_main_enemy_army_to_local_player()` /
`get_scriptunits_for_army(2, n)` / `get_non_player_alliance()`, then call
`enemy_sunit.uc:perform_special_ability("ability_key", enemy_sunit.unit)` or the ground variant with
the enemy's position). But this exact combination is **not** demonstrated in any public source; treat
it as "well-supported by the API docs, not yet proven in the wild." The one caveat worth carrying:
`perform_special_ability` runs a legality check ("If the ability is not valid for any of the units, a
script error results") and targets *the controller's own units* — the second argument is what the
ability is aimed *at*, so an enemy-facing hex must be a valid target for that specific ability key.

---

## URLs worth citing

Official CA docs (community mirrors) — highest authority:
- Battle unitcontroller (ability API, incl. `perform_special_ability`): https://chadvandy.github.io/tw_modding_resources/WH3/battle/battle_unitcontroller.html
  (mirror: http://go.recoveringme.com/WH3/battle/battle_unitcontroller.html)
- Battle manager (`get_scriptunits_for_army`, `get_scriptunits_for_main_enemy_army_to_local_player`, `get_non_player_alliance`): https://chadvandy.github.io/tw_modding_resources/WH3/battle/battle_manager.html
- Script unit (`.unit`/`.uc`, `get_enemy_alliance`, `add_ping_icon`, `start_attack_closest_enemy`): https://chadvandy.github.io/tw_modding_resources/WH3/battle/script_unit.html
- Battle hierarchy / scriptunit workflow: https://chadvandy.github.io/tw_modding_resources/WH3/battle/battle_hierarchy.html
- Battle unit (`can_perform_special_ability`): https://chadvandy.github.io/tw_modding_resources/WH3/battle/battle_unit.html
- Auto-generated Lua stubs of the same CA docs (game-version pinned): https://github.com/LyciaPintella/Total-War-Warhammer-III-Lua-Library-Documentation
- Older official engine doc (`perform_special_ability` with no target): https://wiki.totalwar.com/w/Battle_Script_Documentation.html

Real public mod / worked example:
- DasAng mind-control spell (repo): https://github.com/DasAng/warhammer_mind_control_spell
- DasAng write-up (enemy-handle technique, `add_ping_icon` workaround): https://dasang.github.io/blog/warhammer_mod/
- Raw script: https://raw.githubusercontent.com/DasAng/warhammer_mind_control_spell/master/script/battle/mod/ang_mind_control_spell.lua

Secondary / context:
- Auto Abilities: https://steamcommunity.com/sharedfiles/filedetails/?id=3009989710
- Auto-Cast Specialist Commands: https://steamcommunity.com/sharedfiles/filedetails/?id=3459647882
- AutoCast: https://steamcommunity.com/sharedfiles/filedetails/?id=3501038025
- AI General: Unified Tactics: https://steamcommunity.com/sharedfiles/filedetails/?id=3727310475
- Total War Modding wiki (Lua): https://tw-modding.com/wiki/Lua
- TWC Modding Q&A (battle-scripting doc gap): https://twcenter.net/threads/modding-q-as.623782/page-5

---

*Nothing in this document was fabricated: every quote is from the cited page/code as fetched. The
one thing that could NOT be found is a public end-to-end example of a script auto-casting a hex/debuff
at an enemy — that gap is stated above rather than filled with a guess.*
