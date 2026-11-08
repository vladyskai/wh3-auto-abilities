# Route 2 test case — auto-firing ONE ability (Deadly Onslaught, Boris Todbringer)

> ## STATUS: Round 26 — the firehose test, and the closing verdict.
>
> Subscribed to **all 399 event names** `script/events.lua` declares (0 refused by the engine), dumped
> every component the scan visits, and logged events from our chain uncapped. One battle produced
> **18 distinct events**:
> ```
> ComponentMouseOn (56)  ComponentMouseOff (49)  ComponentLClickUp (8)  RealTimeTrigger (5)
> BattleTimeTrigger (5)  ShortcutTriggered (5)  BattleUnitAttacksEnemyUnit (5)  …
> ComponentAnimationStarted/Finished  PanelOpenedBattle/ClosedBattle  BattleSessionEnded
> ```
> **`ComponentRClickUp`: zero. `ComponentLDBLClickUp`: zero — and 0 occurrences in the whole log
> across all 28 battle sessions.** With the complete event vocabulary subscribed and nothing refused,
> that is conclusive: the engine never raises a right-click (or left-double-click) component event in
> battle. Right-clicks are consumed as world orders before the UI sees them. **The click control is
> impossible — measured, not inferred.**
>
> "Hidden variable" question, answered: the component dump shows `button_order1` → `state='active'`,
> `img0='ui\skins\default\button_ability_selected_inactive.png'`, while the real ability icons are
> `button_ability`..`button_ability6` (proper `ui/battle ui/ability_icons/...` paths). There is no
> property-enumeration method on UIComponent (only `GetProperty(name)`), and nothing click-related is
> observable anyway.
>
> **One new door, if a switch is ever wanted: `ShortcutTriggered` works** — it fired with
> `string=step_r / step_l / step_bck / step_fwd`, i.e. keyboard shortcuts are reported to script *with
> their names*. A keyboard toggle would mean hijacking an existing shortcut, or adding one on a layout
> component (unverified). Not built.
>
> Shipped: md5 `1f0a33ac…` — the firehose stripped (1118 lines), auto on, fires on charge, tooltip
> says so. That is the finished article.
>
> ## STATUS (earlier): Round 25 — final verdict on the click control.
>
> Round 25's log (reporter on the ability button AND its whole ancestor chain, both click listeners
> unfiltered and labelled):
> ```
> event reporter on 'button_order1' ok=true … 'button_parent' … 'SA_dial' … 'battle_orders_pane' … 'root'
> CONTROL: left-click on '1001' - not ours
> CONTROL: left-click on 'button_battle_start' - not ours
> CONTROL: left-click on 'button_ability' - not ours        <- uses the ability
> command: 'Special Ability' issued for 'wh_main_character_abilities_deadly_onslaught'
> CONTROL: left-click on 'button_toggle_infopanel' - not ours
> RCLICK: (zero lines, for any component, all battle)
> ```
> **Left-click component events are delivered to script in battle. Right-clicks never are** — not for
> the ability button, not for any component, with the reporter enabled everywhere. That closes the
> question for good: no click-based control is possible in battle, and the reason is now measured
> rather than guessed. (The engine consumes right-clicks as world orders before they reach the UI.)
>
> Shipped instead (md5 `1a033f1c…`):
> - `AUTO_ENABLED = true` — the mod does its job out of the box; there is no in-battle click that can
>   arm it, so requiring one only made it look broken.
> - A 3-second flash on the ability icon at battle start = "automatic mode is live".
> - Tooltip: "Automatic: this ability fires by itself while the unit charges - no click needed".
> - Kept, harmless: the `ComponentLDBLClickUp` listener (the one remaining mouse gesture the engine
>   might report — logs what it sees, toggles if it belongs to our chain or to the unit card) and the
>   `Double Click Unit Card` command handler. Neither fired in testing; both cost nothing.
>
> ## STATUS (earlier): Round 24 — `AddScriptEventReporter()` and a self-diagnosing build.
>
> ### Why my first sweep missed it
> `list=allpages` returns only the main namespace: 37 pages. The wiki actually has **436** across
> `UI:`, `Lua:`, `Tutorial:`, `Battle Maps:` and `File:`. The answer was in **`UI:Main Page`**, which
> my earlier pass never reached.
>
> ### What it says (UI:Main Page, "AddScriptEventReporter (Warhammer 3)")
> > "UIComponents fire certain Lua events by default when they are interacted with. For example, most
> > UI elements will notify the script when they are clicked using the ComponentLClickUp event.
> > However, there are more detailed events which are **not fired by most UIComponents by default**…
> > You can use the **`AddScriptEventReporter()`** method on any UIComponent to cause it to begin
> > firing **all events**."
>
> Vanilla uses it exactly this way — `_lib/lib_movie_overlay.lua`:
> `uic_scripted_movie_panel:AddScriptEventReporter()` with the comment *"set the panel to report all
> script events"*, followed by a `Component*` listener. And `script/events.lua` lists
> `ComponentRClickUp` right beside `ComponentLClickUp`, so the event was always there — it was just
> never being *reported* for the ability button.
>
> **This is what rounds 15–21 got wrong:** they listened for `ComponentRClickUp` without ever calling
> `AddScriptEventReporter()`, so silence looked like "the engine can't do it". It can.
>
> ### Round 24's build
> - On discovery of `button_order1`: `uic:AddScriptEventReporter()` (logged).
> - Listener on `ComponentRClickUp` (matched by component id and by address) → toggles the switch.
> - Listener on `ComponentLClickUp` on the same button → **the control**: that click happens anyway
>   (it is how the ability is used), so if it reports and the right-click doesn't, the reporter works
>   and the engine simply never raises the right-click. Self-diagnosing in one battle.
> - `AUTO_ENABLED = false` again (the switch exists), the battle-start flash only when it starts ON,
>   the tooltip hint back to "Right-click this ability to toggle automatic use".
> - Also found on the wiki (community's own tooling): the **UI Context Viewer** overlay (settings
>   checkbox + `` ` `` key, shows the component tree) and the script helpers
>   `output_uicomponent_on_click()` / `print_all_uicomponent_children(uic)` for finding paths.
>
> ## STATUS (earlier): Round 23 — the control was a double-click on the unit card.
>
> ### The measurement that ended it (round 22's log)
> ```
> its container chain: root < hud_battle < battle_orders < battle_orders_pane < SA_dial < button_parent < button_order1
> property reads: zz_rclick='zz_rclick'  zz_lclick='zz_lclick'  icon_index='icon_index'  (ok=true)
> command: 'Special Ability' issued for 'wh_main_character_abilities_deadly_onslaught'
> ```
> Every property read echoes the property's **own name** — including `icon_index`, which vanilla
> itself declares with a value (8). So the component was right (the chain proves it) and the channel
> is dead: script cannot observe anything a layout callback sets. Since a right-click can *only*
> reach Lua through a layout callback, **right-click cannot be implemented.** No vanilla precedent,
> no mod precedent, and now a measured failure. Closed for good.
>
> What the same log proved: the **command channel** works — the engine reported the ability use to
> script. So the control moved there.
>
> ### Round 23: double-click the unit card
> `Double Click Unit Card` is in the engine's documented command list: *"A unit card has been
> double-clicked upon — get_unit() returns the subject unit."* One handler, no layout, nothing drawn:
> ```lua
> bm:register_command_handler_callback("Double Click Unit Card", function(context) ... end, name)
> ```
> It toggles only when the double-clicked unit's `unique_ui_id()` matches the carrier we found in
> `rebuild_unit_list` (recorded there as `our_unit_ui_id`); any other card is refused with a log line.
> The pulse on the ability icon is the feedback; the tooltip hint now says "Double-click this unit's
> card to toggle automatic use".
>
> ### The pack is now 2 files
> `script/battle/mod/zz_test_deadly_onslaught.lua` + `ui/common ui/special_ability_tooltip.twui.xml`.
> `hud_battle.twui.xml` and `land_unit_card.twui.xml` are **out** of the pack, so the vanilla HUD is
> back in force (no leftover callbacks). Auto still starts OFF.
>
> ## STATUS (earlier): Round 22 — a control that settles it in one battle.
>
> Round 21's log: the button was found (`button_order1`), feedback worked, and the property read
> returned **`'zz_rclick'`** — the property's own *name*, not the declared `"0"`. Two possibilities,
> and one build now separates them:
>
> | observable in the next log | what it means |
> |---|---|
> | `CONTROL: 'zz_lclick' reads '1'` after a left-click on the icon | a click on the ability icon **does** reach script through the layout → only the right-click is not delivered |
> | `icon_index='8'` on the line after discovery | the instance really is the component `hud_battle.twui.xml` defines (vanilla declares `icon_index` = 8 on it) |
> | neither appears; the reads keep echoing their own names | the property channel is not usable on this component → **the whole layout route is dead** |
>
> The control is a **left** click: using the ability by clicking it certainly reaches the engine (its
> own `BattleSpecialAbilityButton` consumes the click), so if the layout callback runs, script must
> see it. A `ContextCommandLeftClick` on the same component sets `zz_lclick` — same channel as the
> right-click, but driven by a click that we know happens.
>
> ### Correction to round 21's claim
> I wrote that layout-set properties read by script were "the game's own handshake". Checking who
> *sets* them: `faction_id`, `treasury_cost`, `campaign_key`, `lord_key` are **context/engine**
> properties (no layout declares them), and the one layout-set property in vanilla (`is_pinned` on
> the reinforcement button) is read **only by other layout expressions** — never by script. So the
> layout→script direction is *unproven*, not precedented. The engine→script direction is the one
> with precedent.
>
> Also found: `register_input_handler` is camera-only (move/rotate/edge scroll — no mouse), and the
> command list has `Special Ability` and `Double Click Unit Card` (both reach script) but nothing
> for right-click.
>
> ## STATUS (earlier): Round 21 — patched the component the ENGINE named.
>
> ### The research, and what it settles
> | question | evidence | verdict |
> |---|---|---|
> | can a right-click run an action on a UI component? | `ContextCommandRightClick`: **115 usages across 23 components** in vanilla, incl. ability icons (`dlc26_fragments_ability_slot`, `template_ability`) that open the spell browser | **yes** |
> | can script read what a layout sets on a component? | vanilla scripts read layout-set properties: `GetProperty("faction_id")` / `("treasury_cost")` in `wh3_dlc23_labour_move.lua`, `("campaign_key")` in `frontend_start.lua`, `("lord_key")`, `("id")` | **yes — this is the game's own UI→script handshake** |
> | does the engine report right-clicks to script any other way? | no `ComponentRClickUp` (0 hits in 907 layouts, 0 mods, silent in two battles), no right-click in the command list (`battle.lua` reports Move / Attack / **Special Ability** / **Double Click** / … but nothing for rclick) | **no** |
> | has any mod or guide done this? | nothing on the wiki, TWC, the web, or in the 8 mods on this machine; Consul Scriptum's debug tools report left-clicks only | **no precedent** |
> | does *battle* deliver a right-click to that component? | **not established anywhere** — the battle input layer may consume right-clicks as orders | **the one unknown** |
>
> ### The mistake that made the last three rounds fail
> The log had the answer all along: the component carrying Deadly Onslaught is
> **`id='button_order1'`** — under `sa_dial > button_parent`, defined once in `hud_battle.twui.xml`,
> with the engine's own `BattleSpecialAbilityButton` callback. I had patched `button_behaviour`,
> `template_ability`, `button_ability`, `button_spell` and the card's `template_ability` — none of
> them the ability button. That is why three different channels all did nothing.
>
> ### Round 21's change
> Two literal insertions into `button_order1` **only** (hud_battle 1390828 → 1391085 bytes, and the
> four wrong-component insertions from round 20 are gone — the file is rebuilt from vanilla):
> ```xml
> <userproperties><property name="zz_rclick" value="0"/>…</userproperties>
> <callback_with_context callback_id="ContextCommandRightClick" context_object_id="CcoStaticObject"
>     context_function_id="self.SetProperty(&quot;zz_rclick&quot;, &quot;1&quot;)"/>
> ```
> The property is *declared* (so the script's read returns "0" before any click, instead of the
> engine echoing the name of an undeclared property — which is what round 20's log showed).
> The script polls it from the UI timer, clears it, toggles on the change.
> Also added: a `Special Ability` command listener as the **control case** — the engine reports
> ability use through the command channel, so the log now proves whether a click on the icon
> reaches the game at all.
>
> ### And one honesty fix
> Round 20's `WATCHDOG` line was almost certainly the pause menu: model time freezes while paused and
> the strike threshold was 1.5 s of real time. Now 12 strikes (6 s) and the message says so.

> ## STATUS (earlier): Round 20 — right-click via a component property; auto starts OFF.
>
> ### What round 19's log proved
> ```
> scan done: 77 component(s) visited - OURS FOUND      <- the ability icon is found now
> (no RCLICK script event, no context event, no ability icon feedback line at all)
> ```
> So: **the layout's rclick *broadcast* never reaches script** — CA's docs say it notifies other
> *UI* callbacks — and `ComponentRClickUp` does not arrive for this component. Both candidate
> channels were dead, which is why right-clicking did nothing.
>
> ### The channel that works: a property on the component
> The layouts now declare **`ContextCommandRightClick`** — the callback CA uses 115 times,
> including in battle (`CcoBattleToggleableSlotBuildable` → `PrimaryAction`/`SecondaryAction`) —
> carrying the same expression the engine's own reinforcement button uses:
> ```xml
> <callback_with_context callback_id="ContextCommandRightClick" context_object_id="CcoStaticObject"
>     context_function_id="self.SetProperty(&quot;zz_rclick&quot;, &quot;1&quot;)"/>
> ```
> The script reads `GetProperty("zz_rclick")` off the ability button from the **UI timer** (a UI
> call, so the right clock for it), clears it, and flips the switch. A stuck property cannot cause
> flapping: the toggle fires on the *change* to "1", not on the value — mock-verified, including
> with `SetProperty` forced to fail.
>
> ### The other two complaints
> * **No visual feedback**: the pulse was only applied from phase callbacks and from toggles, and
>   round 19 found the ability icon *after* the last phase change — so nothing ever pulsed it. It
>   is now applied the moment the icon is found, and only when the state actually changes.
> * **Auto started ON**: now `AUTO_ENABLED = false`. The log's first line says
>   `automatic activation starts OFF`.
>
> ### Two of my own bugs, caught before they reached a battle
> * A regex replacing round 19's broadcaster blocks was anchored on `ContextEventBroadcaster`,
>   which **vanilla uses too** (the dev button's `DevLevelUp` broadcast) — it matched from vanilla's
>   block to ours and deleted **221 KB** of the unit card (434 214 → 212 601 bytes). Both layouts
>   are rebuilt from the pristine vanilla copies with literal insertions, and the build now asserts
>   the card's size so a truncated layout can never ship.
> * Round 19's deletion had removed the watchdog's `local` declarations, leaving them as globals:
>   harmless until the stall branch ran, where arithmetic on nil would take the UI timer with it.
>   The mock hit it; a battle would have.
>
> ### Mock-verified (harness23)
> Default OFF; icon found and pulse synced; property "1" toggles once and clears; a property that
> **sticks** toggles exactly once (no flapping); a second click toggles back; OFF = 0 fires over
> 400 polls, ON = fires; UI calls only in the UI-timer context; `remove_callback` raises in the mock
> and is never called.

> ## STATUS (earlier): Round 19 — the button is gone, the tooltip line is live.
>
> ### Two of my calls were wrong, from the round-18 log
> 1. **The old button was still being created.** I had kept it as a "fallback control" and did
>    not make that clear — your screenshot's double arrow was it, still showing the template's
>    placeholder. It is now deleted outright, with its two icon files: nothing in this mod
>    creates a UI component any more.
> 2. **`behaviour_parent` is not where a character's abilities live.** Round 18's log:
>    ```
>    ability icons: 3 slot(s) in the orders bar
>       slot 0 id='button_behaviour'  ability key=''
>       slot 1 id='button_behaviour2' ability key=''
>       slot 2 id='button_behaviour3' ability key=''
>    ```
>    Empty keys on all three: that row is the *fire-at-will / skirmish* behaviour row, unused for
>    Boris. The engine's own `highlight_unit_abilities()` walks it, which is why I assumed it held
>    unit abilities — it holds *behaviour* buttons. So the script no longer assumes a path: it scans
>    the HUD and asks each component `InterfaceFunction("AbilityKeyForScript")`, logging every hit
>    with its `Address()`. One battle now names the component (and confirms which layout file to
>    patch), rather than another guess.
>
> ### The tooltip line: the engine already has a slot for it
> `special_ability_tooltip.twui.xml` ships a **`label_right_click`** component, sibling of the
> `label_left_click` that prints *"Left-click to activate"* in your screenshot. Its placeholder
> text is literally:
> ```xml
> text="Right click text that comes from db"
> ```
> It was hidden for unit abilities (its visibility condition only holds in the spell-browser
> context) and filled from `Loc("right_click_spell_browser")`. Round 19 removes that condition and
> puts our own line in it:
> > **Right-click this ability to toggle automatic use (it then fires by itself on the charge)**
>
> No new component, no new hierarchy entry, no localisation file — and being a layout change it
> wins by pack name, which the loc-override route never did.
>
> ### Also from round 18's log
> * `NumStates()` on a script-created component returned a **function**, so `for i = 0, count - 1`
>   threw (`attempt to perform arithmetic on local 'count'`). Same pattern as `CurrentState()`
>   earlier. Moot now the button is gone, but it is why the per-state paint never ran.
> * `SetImagePath` reported success (`img=true`) while `GetImagePath(0)` came back `'0'` — the paint
>   never took effect. Not chased further: no button, no icon to paint.

> ## STATUS (earlier): Round 18 — the round-17 pack was fine; the trigger was killed by my own "repair".
>
> ### What the round-17 log actually shows
> ```
> tooltip text in use (ok): Such is the power and ferocity...     <- round-17 code ran; the loc override LOST
> button look: switch=ON -> ... icon auto_on.png (gold bolt)      <- we asked for the bolt
> ability icons: behaviour_parent is not on screen                <- discovery failed, and never retried
> poll re-armed (#1, ok=false error=lib_timer_manager.lua:299: attempt to perform arithmetic on a function value)
> the poll stopped (still at tick 2) - re-arming it               <- and never came back
> ```
> The installed pack md5 matched the round-17 build exactly, so nothing was mis-uploaded.
>
> ### The trigger died because of the re-arm, not the UI work
> `rearm_poll()` — added in round 16 as a repair — called `remove_callback()` **first**, so the
> healthy poll left the model timer list, and the re-add then threw inside
> `lib_timer_manager.lua:299` (`battle:time_elapsed_ms() + interval` with a function on one side).
> Record gone, add failed: the poll was dead for the rest of the battle. Every later re-arm the
> watchdog attempted reported `ok=true` and changed nothing — **once the model timer driver has
> lost its engine timer, adding records back is inert, they sit in a list nothing walks.** So the
> "repair" could never have worked; it only masked the symptom while spamming the log.
> Round 16's untested build had the same defect.
>
> **Round 18 removes the re-arm entirely.** The poll is registered once at load and never touched
> again; the watchdog now *reports* a stall and explicitly does not repair. Mock-verified: zero
> `remove_callback` calls in a whole battle.
>
> ### The icon: unmeasurable before, measurable now
> Every `SetImagePath` sat inside a `pcall` with no error reporting, so "the engine refused the
> image" and "the engine took it and drew something else" produced identical logs. Now:
> * each call's outcome is logged, with error text;
> * the paint walks **every state** of the button, not just the current one — the toggle template
>   gives each state its own image list, a likely reason the placeholder survived a repaint;
> * `GetImagePath(0)` is read back from the component afterwards.
>
> Mock output, success case:
> ```
> button paint: switch=ON | wanted state 'selected' icon ui/zz_deadly_onslaught/auto_on.png
>   (img=true state=true img2=true) | states walked: 3 [...] | component image 0 is now
>   'ui/zz_deadly_onslaught/auto_on.png' (read ok=true)
> ```
> and the failure case prints the engine's own error text instead of nothing.
>
> ### Also fixed
> * **Icon discovery retries** from the UI timer until `behaviour_parent` exists (it does not in the
>   early phases). Round 17 gave up on the first attempt, which also meant a right-click could never
>   have toggled anything.
> * **Tooltip**: the loc override lost, so the ability's tooltip text is now set from script via
>   `SetTooltipText` — the mechanism the engine's own code uses (`lib_core.lua:2857`) — with the
>   outcome logged. Why the loc route failed is now understood: a layout tooltip is localised through
>   CA's own string pipeline, and the `text_label` values in layouts (`StateText_…`) are editor tags
>   that resolve to nothing in the loc table.
> * Every `pcall` boundary in the UI path logs its failure instead of swallowing it.

> ## STATUS (earlier): Round 17 — the right-click now has a layout behind it.
>
> ### Why this is the right hook (all of it read off the engine's own files)
> * `ui3.pack` holds **907** layouts **and not one declares `rclick`** — right-clicking an ability icon has therefore never raised anything. That is why 0 of the mods on this machine use `ComponentRClickUp`, and why the catch-all listener in round 15 logged nothing at all.
> * CA's own UI callback documentation (chadvandy's `ui_callback_documentation.html`) defines **`ContextEventBroadcaster`**: *"On action specified by user property broadcasts the event specified (**lclick, rclick, mouseon, mouseoff**)"* — `rclick` is a documented trigger, and its user properties take the event name to broadcast.
> * Where the ability icons are came from the engine's own script, not from guessing: `lib_battle_ui.lua` → `highlight_unit_abilities()` walks `battle_orders/orders_parent/behaviour_parent`, takes **child 0** of each slot and reads `InterfaceFunction("AbilityKeyForScript")`.
> * `AddScriptEventReporter()` is **not** a route: CA's docs say outright *"Would be nice to have clicks in here, but there are over a hundred uses in Warhammer scripts that dont want to break"* — no clicks, ever.
>
> ### What the pack now contains (5 files + loc)
> | file | change |
> |---|---|
> | `ui/battle ui/hud_battle.twui.xml` | broadcaster added to `button_behaviour` (the orders-bar ability button), `template_ability`, `button_ability`, `button_spell` |
> | `ui/common ui/land_unit_card.twui.xml` | broadcaster added to the card's `template_ability` |
> | `text/db/zz_deadly_onslaught__.loc` | the ability's tooltip text, vanilla value + the right-click instruction |
>
> Each insertion broadcasts a **different** event name (`zz_auto_rclick_orders_bar`, `…_hud_ability`, `…_button_ability`, `…_button_spell`, `…_card_ability`) so the log says which button was actually pressed.
>
> ### The script half
> * listens on **both** candidate channels — `ComponentRClickUp` and `ContextTriggerEvent` — and toggles on whichever arrives, logging which one it was;
> * finds the ability icons at runtime and logs every slot's id and ability key, flagging ours;
> * reports **left**-clicks on our button too, which is the control case that separates "the engine ignores rclick" from "my listener never registered";
> * feedback is the engine's own **pulse highlight** on the ability icon itself (`StartPulseHighlight`), which the advice system uses — no custom image, nothing painted;
> * logs `tooltip text in use (…)` at load, which proves whether the loc override won.
>
> ### Mock-verified (harness21)
> Listeners register; discovery finds the button by ability key; a right-click on a *different* component does **not** toggle; a right-click on ours flips to OFF with **0 fires over 125 s** and stops the pulse; the layout broadcast flips it ON and restarts the pulse; an unrelated context event is logged only; the HUD button still toggles through the same `set_auto`. UI calls happen only in phase callbacks — the poll still makes **zero**.
>
> ### Risk to watch
> This is the first round that **replaces vanilla UI files**. If the battle HUD misbehaves (missing order bar, broken cards), delete `data\zz_test_deadly_onslaught.pack` to revert instantly.

> ## STATUS (earlier): Round 16 — button restored on the gold/grey bolt, plus a watchdog that repairs the poll if the UI work kills it.
>
> ### What the round-15 test proved (from your log, session 17)
> **Right-click is impossible in practice.** The listener was live and logged every
> distinct right-clicked component; the log contains **zero** such lines, while
> `auto=ON` throughout and the ability fired twice. `ComponentRClickUp` is listed
> in the engine's event table (`script/events.lua`) but nothing in battle ever
> delivers it. Not a coding bug — an engine gap.
>
> **And the round-14 subtitle failure now has a cause** (session 16):
> ```
> announce: automatic activation is ON
>   subtitle 'zz_deadly_onslaught_auto_on': ok=true result=false
> ```
> `result=false` = the engine found no text for that key: the hand-written `.loc`
> was never loaded. A localisation-loading problem, not a display one. Dropped.
>
> ### The pattern behind every button failure, across rounds 9-14
> | created in | timer survived | icon correct |
> |---|---|---|
> | model timer (round 10) | **no** | no |
> | phase callback (rounds 9, 13) | **no** | **yes** |
> | real timer (rounds 11, 14) | yes | no |
>
> Creating it in a phase callback is what kills the model timer; painting from a
> timer silently does nothing. So round 16 does both halves in the contexts that
> work, and repairs the timer damage afterwards:
>
> - **phase callbacks** (`Deployment`, `Deployed`): create the button, paint it,
>   then re-arm the poll timer (`remove_callback` first — the timer manager keys by
>   name and does *not* de-duplicate, so re-adding blindly would run the poll twice
>   per interval).
> - **real timer** (`ui_tick`, 500 ms): a watchdog that only *watches* — if the
>   poll's tick counter stops moving for two checks, it re-arms the poll. No UI call
>   is ever made from it.
> - **click handler**: paints (the gold/grey bolt is the feedback) and flips the
>   switch.
>
> ### Verified by mock (harness20)
> The poll makes **zero** UI calls. The phase callback creates, paints
> `auto_on.png` at index 0 and re-arms the poll. With the model timer made to die,
> the watchdog logs `the poll stopped (still at tick 60) - re-arming it` and
> heartbeats resume (3 → 13). A click flips it OFF with **0 fires over 125 s**, a
> second click flips it ON and it fires again. Every UI call is stamped with its
> context and only phase callbacks and clicks appear.

> ## STATUS (earlier): Round 15 — the toggle is a right-click on the ability's own icon. No custom UI at all.
>
> ### Why this route
> The engine's own event table (`script/events.lua`) lists a right-click event:
>
> ```lua
> ComponentLClickUp = {}
> ComponentLDBLClickUp = {}     -- left double-click
> ComponentRClickUp = {}        -- right-click  <-- used now
> ```
> Same mechanism as the old button's `ComponentLClickUp`, but it only *listens* to
> a component the game already draws. Nothing is created, styled or displayed by
> this mod any more — and every failure from rounds 9 to 14 came from creating and
> painting a component.
>
> ### What changed
> - Deleted: the button (create/dock/paint), the bar-resize machinery, the real
>   timer, the subtitle announcement, the `hud_ready` flag and both click
>   listeners. The script went from ~950 to 740 lines and the pack from 4 files
>   to **1**.
> - Added: one `ComponentRClickUp` listener.
> - The button icons and the subtitle `.loc` stay in the source tree but are no
>   longer shipped (the build script lists them as commented-out).
>
> ### The one thing not yet proven
> The ability icons come from the unit card layout
> (`ui/common ui/land_unit_card.twui.xml`, component id `template_ability`), but
> the engine instantiates them per card, so the runtime name is unknown. Rather
> than guess, the listener logs the name of **every** distinct right-clicked
> component once (no log spam) and toggles when the name contains "abilit":
>
> ```
> right-click on component 'template_ability'   <- treated as an ability button
> TOGGLE by right-click - automatic activation is now OFF
> ```
>
> If the real name differs, the log shows it and one line fixes the filter. Also
> still to confirm in play: whether right-clicking an ability does anything in
> vanilla (it may cancel or queue), which would be a side effect of this route.
>
> ### Verified by mock
> Listeners register; combat fires with the switch ON; a right-click on a
> non-ability component does **not** toggle (and is logged once only); a
> right-click on an ability button flips it OFF with **0 fires over 125 s**; a
> second right-click flips it ON and it fires again. The mock makes
> `find_uicomponent`, `UIComponent` and `core:get_ui_root` raise errors, so the
> test fails if the mod ever touches the UI layer.

> ## STATUS (earlier): Round 14 — the indicator is now engine-rendered (an on-screen subtitle), and the UI work is finally in a safe *and* late-enough context.
>
> ### Round 13's regression, from the log
> ```
> phase change seen: PrebattleCinematic
> button look: …            ← create + paint ran inside the Deployment dispatch
> toggle button: created
> phase change seen: Deployment
> (0 ticks, 0 heartbeats afterwards)
> ```
> So creating the component **inside the phase dispatch** killed the model timer
> (the poll like round 9); doing the same work in a **real timer** (round 11) left
> the timer alive but was far too early for the paint to stick. Neither round did
> both things at once.
>
> ### The indicator: a subtitle the engine draws
> `battle_manager:show_subtitle(key, full_key_supplied, force)` — called with
> `force = true` so it does not depend on the player having subtitles enabled.
> The strings ship in the pack's own localisation file:
>
> ```
> text/db/zz_deadly_onslaught__.loc
>     zz_deadly_onslaught_auto_on  = Deadly Onslaught: automatic activation ON
>     zz_deadly_onslaught_auto_off = Deadly Onslaught: automatic activation OFF
> ```
> It shows on every toggle, and once shortly after the battle starts. RPFM's
> encoder had to be driven to write that file: `NewPackedFile(pack, path,
> {"Loc": "Loc"})` then `SavePackedFileFromView(pack, path, {"Loc": {"table": …}})`
> — note the request variant is `Loc` while the decode response calls it
> `LocRFileInfo`, and it takes only the `{"table": …}` struct.
>
> ### The structure, round 14
> | Piece | Where it runs | Why |
> |---|---|---|
> | phase callbacks | raise a `hud_ready` flag, **no UI work** | rounds 9/13: UI work in the dispatch kills the model timer |
> | real timer (500 ms) | **all** UI work, starting only after `hud_ready` | round 11: real timers are safe; round 9: painting works once the HUD is up |
> | the poll | model timer, logic only | rounds 8/11: proven |
> | click handler | paint + subtitle | round 9: painting works here |
>
> New log lines to check with: `HUD is up - UI work can start`,
> `ui timer is running`, `announce: …`, `subtitle '<key>': ok=… result=…`
> (**nil** = the engine drew it; **false** = the localisation entry did not load).

> ## STATUS (earlier): Round 13 — round 12's regression removed; back to the only configuration with evidence behind it.
>
> ### What round 12 broke (my fault, and the log shows it)
> Round 12 added UI work in two new places: a **`Startup` phase callback** and
> **painting inside the phase-watch listener**. The log from that battle:
>
> ```
> button look: switch=ON -> ... | component reports 'function: 0000000153620FA0'
> toggle button: created in the battle order bar
> phase change seen: Startup          <- and then: no further phase events
> (0 heartbeats, no "poll is running (first tick)" at all)
> ```
>
> So painting during Startup killed the model timer *and* the phase dispatch
> before either had run properly. Two lessons: no UI work before the Deployment
> phase, and none inside the phase-event trigger (`core:trigger_event`).
>
> The self-report was useless too: `CurrentState()` returns a *function* rather
> than a state name on this component, so it was removed. The icon is the
> reliable indicator.
>
> ### Round 13 — only what has evidence
> | Piece | Where it runs | Evidence it works |
> |---|---|---|
> | create + paint the button | `Deployment` / `Deployed` phase callbacks | round 9: button appeared **with our bolt** |
> | repaint on toggle | the click handler | round 9: presses swapped gold ↔ grey correctly |
> | the poll | model timer, **logic only** | rounds 8 and 11: full battles, activations accepted |
>
> Removed: the `Startup` phase callback, painting in the phase-watch listener
> (now log-only), and the real timer entirely.

> ## STATUS (earlier): Round 12 — the automation is confirmed working in-game; the button now paints where painting works.
>
> ### Confirmed working from the log (this is real, not a mock)
> Round 11's battle log: **every phase event arrived** (`Startup`,
> `PrebattleWeather`, `PrebattleCinematic`, `Deployment`, `Deployed`, `Complete`),
> **148 heartbeats** across the whole battle, and **three activations**, each
> `ACCEPTED`, each during a genuine charge:
>
> ```
> ATTEMPT ... reason: charging (gap=274.5m dist=30.5m eta=3.9s)   ACCEPTED
> ATTEMPT ... reason: charging (gap=97.3m  dist=30.9m eta=4.0s)   ACCEPTED
> ATTEMPT ... reason: charging (gap=75.8m  dist=30.9m eta=4.0s)   ACCEPTED
> ```
> …and **zero attempts during every stretch with the switch OFF**. Trigger,
> switch, model timer, phase dispatch: all working in the real game.
>
> ### Why the icon was still the template's double-arrow
> Painting only sticks in UI-adjacent contexts — a click handler, or a phase
> callback. Round 9's button showed our bolt precisely because it was created in a
> *phase callback*; rounds 10 and 11 created it from a timer, so
> `SetImagePath`/`SetState` silently missed and the template's own placeholder
> showed through.
>
> That also explains the inverted feel: because the initial paint missed, the
> button sat in the template's default look — the very look used here for OFF —
> while the switch was actually ON. Hence "it activated while the button looked
> deactivated."
>
> ### Round 12 changes
> - The button is **painted from the phase callbacks** and on **every phase
>   event**, i.e. the context where painting demonstrably works.
> - New self-report in the log on every change:
>   `button look: switch=ON -> wanting state 'selected' icon auto_on.png | component reports 'selected'`
>   If the on-screen look ever disagrees with that line again, the log now says
>   whether the component accepted the state (then the state names mean the
>   opposite of what I assumed, and the fix is swapping two words) or refused it.
> - `Startup` added as a third phase callback, for one earlier paint.

> ## STATUS (earlier): Round 11 — the cause was UI work in the model timer. Moved to a real (UI) timer.
>
> ### The two symptoms were one cause
> - **The double-arrow icon** is the template's own placeholder —
>   `ui/skins/default/icon_movespeed.png`. Our `SetImagePath` never took effect.
> - **The ability never fired**, and the log showed the poll ticking once and
>   never again, with `phase change seen: Startup`, `PrebattleWeather` and then
>   **no further phase events at all** — so the phase callbacks could never run
>   either. Crucially there was **no `POLL ERROR` line**, so nothing threw in Lua.
>
> Both point the same way: the button was being created *from the model timer*
> (the poll), and engine UI calls made in that context do not take effect — which
> is exactly what paperpancake's own comment warns about ("some game functions
> might not be available in that part of the game loop... put calls into
> bm:callback"). Doing it there also left the battle's model timer dead afterwards.
>
> ### The fix
> A clean split, which is what the engine provides for this:
> - **Model timer (the poll) = logic only.** No UI calls whatsoever. This is the
>   round-8 structure that worked.
> - **Real timer (`bm:repeat_real_callback`) = all UI work.** Real timers are
>   synchronised to UI updates rather than the battle model, so engine UI calls
>   work there. `ui_tick()` creates the button, and re-applies the look every 2 s
>   so a state that fails to paint corrects itself.
> - The deferred repaint after a state transition is now a `real_callback` too.
>
> ### Verified before building
> 100 polls → **0 UI calls**; first UI tick → 1 `CreateComponent`, icon and state
> set; a late phase callback → still exactly 1 button; click → icon swaps to
> `auto_off.png` + state `active`; with the switch ON and a charging unit → fires.
>
> ### Diagnostics kept
> `tick n | phase= | conflict= | auto= | tracked=` every 10 s, `phase change seen:
> <name>` for every phase event, and `POLL ERROR #n` if the poll ever throws.

> ## STATUS (earlier): Round 10 — the round-9 breakage is diagnosed and fixed, and the button repaints properly.
>
> ### What the log said
> Round 9's run: the poll logged **exactly one tick** and then nothing — no
> heartbeats, and the "combat phase started / building watch list" line never
> appeared either. So the ability could not fire: the thing that watches for the
> charge had stopped running.
>
> ### Root cause, from the game's own library
> `script/_lib/lib_timer_manager.lua`, `timer_manager_battle_callback` — the one
> engine timer that drives **every** script timer in a battle:
>
> ```lua
> while #battle_model_timers > 0 do
>     local next_timer = battle_model_timers[1];
>     if next_timer.callback_time <= time_elapsed_ms then
>         local callback = next_timer.callback;
>         table.remove(battle_model_timers, 1);
>         callback();                       -- if THIS throws...
>     else break; end;
> end;
> battle:unregister_timer("timer_manager_battle_callback");
> if #battle_model_timers > 0 then
>     battle:register_singleshot_timer(...);  -- ...this re-arm never happens
> end;
> ```
> One error escaping any timer callback aborts the loop before the re-arm, and
> **every repeating callback in that battle goes silent for the rest of the
> fight.** The same shape exists in the phase dispatcher: an error out of one
> phase callback aborts the loop, starving every callback registered after it.
>
> Round 9 had opened both doors: a second repeating timer (the bar re-fit) that
> made UI calls (`Resize`/`Layout`) from a model-timer context, plus two extra
> phase callbacks ahead of the watch-list one.
>
> ### Fixes
> - The poll body is wrapped: an error logs `POLL ERROR #n (poll continues)` and
>   the loop survives. Same wrapping for every phase callback.
> - The separate 1 s layout timer is **gone**. The bottom bar is no longer
>   resized at all (`RESIZE_BAR = false`) — doing it by hand switches off the
>   game's own resizing, and the button fitted fine without it in your
>   screenshot.
> - Button creation is now retried **from the poll** every 250 ms, so a missed
>   phase event can no longer cost us the button.
> - New proof-of-life: a `tick n | phase= | conflict= | auto= | tracked=` line
>   every 10 s **whatever the phase**, so a silent run says why.
> - New diagnostic: `phase change seen: <name>` for every phase event, so we can
>   tell whether phase changes reach scripts at all.
>
> ### The visual bug
> The toggle template animates state changes over 200 ms, and a transition can
> leave the previous image in place — precisely what happened: perimeter changed,
> bolt did not. The image and state are now applied twice, the second time
> 260 ms later.

> ## STATUS (earlier): Round 9 — an ON/OFF button for the automation, in the battle order bar.
>
> ### Where the pattern came from
> Not invented: read out of **AI General 3** (paperpancake, `id=2799316652`), whose
> pack is on this machine after you subscribed to it. Its
> `script/pancake_lib/aigeneral_battlemod_button_ext.lua` shows the whole recipe:
>
> - the button is a **clone of a template the game already ships** —
>   `bottom_bar:CreateComponent(name, "ui/templates/square_medium_button_toggle")`
>   — so no custom `.twui.xml` layout file is needed. Confirmed present in this
>   game version at `ui3.pack` → `ui/templates/square_medium_button_toggle.twui.xml`;
> - the click arrives through
>   `core:add_listener(name, "ComponentLClickUp", filter, callback, true)` where the
>   filter tests `context.string == <the name passed to CreateComponent>`;
> - the button is docked with `SetDockingPoint(8)` (bottom-centre) +
>   `SetDockOffset(x, y)`, and the bottom bar must be resized by hand afterwards,
>   because doing so switches off the game's own resizing.
>
> ### The trap in that template
> Its states are `active`, `selected`, `inactive`, `hover`, `down`, … but
> **`inactive` is `disabled="true"`** — a button left in that state cannot be
> clicked again. So the switch here is `selected` = ON (lit) and `active` = OFF
> (normal), both interactive.
>
> ### Round 9 changes
> - `AUTO_ENABLED` boolean, flipped by the button; when OFF the poll fires nothing
>   at all (the charge logic is not even evaluated).
> - Button: gold bolt icon + "automatic activation ON - click to switch it off";
>   grey bolt + "…OFF - click to switch it on". Icons shipped in the pack at
>   `ui/zz_deadly_onslaught/` (generated 64×64 PNGs).
> - Heartbeats now carry `auto=ON` / `auto=OFF`.
> - A diagnostic listener logs any click on a component whose name contains
>   "toggle" but is not ours, so a wrong filter shows up in the log instead of
>   failing silently.
>
> ### Verified by mock before building
> Button created with the right name/template; docking calls correct; click flips
> the switch and swaps icon + tooltip; **0 fires during 125 s of charging with the
> switch OFF**; fires again after switching back ON.
>
> ### What to watch in the battle
> - Does the button appear in the battle order bar? It is docked bottom-centre and
>   offset **330 px right, 6 px up** (`BUTTON_X` / `BUTTON_Y` at the top of the
>   file — one-line change if it overlaps something).
> - Does clicking it swap the icon between gold and grey?
> - With it OFF, does the ability stop firing entirely?

> ## STATUS (earlier): Round 8 — the trigger bug is fixed AND the game's own mechanism was found.
>
> ### Round 7 result (your report) — and what the log actually showed
> You said: charging from far away did **not** activate; giving an attack order to a
> unit while in melee **did**. Both correct, and the log explains why:
>
> ```
> hb t=40  gap=17.1m  dist=296.6m     <- charging from far away
> hb t=100 gap=153.0m dist=161.3m
> hb t=160 gap=294.4m dist=14.5m      <- closing in, still no shot
> hb t=200 gap=321.2m dist=0.0m       <- contact, no shot
> ATTEMPT (gap=2.2m dist=24.5m)       <- only AFTER a fresh order at close range
> ATTEMPT (gap=0.8m dist=0.5m)        <- and again at point-blank
> ```
>
> **My "attack order, not a move order" test was wrong.** The documentation says
> that while a unit is *attacking*, `ordered_position()` returns its current
> position. The log disproves it: the gap climbed steadily from 17 m to 322 m and
> tracked **how far the unit had travelled since the order was given**. So my test
> really meant "you clicked less than 8 m ago" — it blocked every genuine charge
> and passed only clicks made right next to an enemy.
>
> ### Round 8 changes
> - `ordered_position()` is **removed from the decision** (logged for diagnostics
>   only). Having a target at all is the real attack-versus-move signal — proven
>   by the same log: running to a spot gives `tgt=false` every time.
> - **A minimum distance** (`CHARGE_MIN_DISTANCE_M = 12`) so a 0.5 m "charge"
>   against an adjacent unit no longer counts. A charge needs a run-up.
> - Kept: running, not in melee, has a target, within 60 m, impact within 4 s.
>
> ### Verified by replaying your own battle data
> The real round-7 heartbeat series was replayed through the new logic at the
> real 250 ms cadence:
>
> ```
> FIRE at ~t=160  dist=28.5 m  eta=3.7 s     <- the far charge that previously failed
> FIRE at ~t=800  dist=29.2 m  eta=3.7 s     <- the second charge
> total fires: 2
> ```
> Both genuine charges now fire on the way in, and the point-blank order
> (0.5–1.3 m) correctly does not.
>
> ### And a better route exists — see `WH3_charge_trigger_findings.md`
> No script in the game does this (all 26 `perform_special_ability` calls are
> benchmarks on fixed timers or quest scripts with no conditions), and the
> scripting API **cannot see** the engine's charge state. But the data layer
> already ships the feature: 10 vanilla abilities are gated to "only while
> charging" by `passive = true` plus a `unit_is_not_charging` auto-deactivate
> flag, which lets the engine's own charge state do the timing exactly.

> ## STATUS (earlier): Round 7 — fires on the charge that is about to land, not on the order.
>
> ### Round 6 result (your report)
> - Running to a location: **no activation** ✓ — the `ordered_position` test works
> - **Attack order at long range: activated immediately** ✗ — the enemy was too far
>   away for the buff to be worth spending
> - In melee: **no activation** ✓
>
> ### Why it fired too early
> Round 6 tested *whether the order was an attack*, which is a yes/no. It had no
> notion of *how far away the enemy was* — so the moment you right-clicked an
> enemy across the battlefield, the condition was satisfied.
>
> ### Round 7 changes
> Two more signals, both measured at every poll and logged:
> - **`unit_distance(target)`** — metres to the target unit, measured edge to
>   edge rather than centre to centre.
> - **Time to contact** = that distance ÷ the unit's own `fast_speed()`, so the
>   gate adapts to the unit: a fast cavalry lord gets a longer run-up than a slow
>   infantry hero.
>
> It now fires only when **all** of these hold: running, not in melee, an enemy is
> the target, the order is an attack rather than a move, the target is within
> **60 m**, and impact is within **4 seconds**.
>
> Both numbers are single constants at the top of the file and are meant to be
> tuned — the heartbeat prints the real `dist=` and `eta=` values so the right
> numbers can be read off a battle rather than guessed.
>
> ### What to do now
> 1. **Fully exit the game and launcher**, relaunch.
> 2. Battle with **Boris**. Order an attack on a **distant** enemy: it should stay
>    silent while he closes, then fire **just before he makes contact**.
> 3. Tell me roughly where he was when it fired. If it is too early I lower
>    `CHARGE_TIME_TO_CONTACT_S`; if too late I raise it. The log prints the exact
>    numbers, so this can be tuned without guesswork.

> ## STATUS (earlier): IT WORKS. Round 5 fired the ability. Round 6 tightened the trigger to charging only.
>
> ### Round 5 result — activation succeeded
> The fix was to copy the call the game uses on itself:
> `sunit.uc:perform_special_ability("<key>", sunit.unit)` — ability key first,
> **target unit second, and the target is required** (self, for a self-buff).
> Found by reading the 26 vanilla call sites in the game's own scripts, one of
> which is commented "Khorne Lord Buffing Himself".
>
> ### Two problems reported afterwards, both mine
> 1. **It also fired while merely running, and while in melee.** Correct
>    behaviour for that build — `FIRE_ON_MELEE` was on, and the "charge" test was
>    only `is_moving_fast()`, which the engine documents as *"running/charging"*.
>    Running to a spot counted as charging.
> 2. **My success test was wrong.** `can_perform_special_ability()` does **not**
>    report the cooldown — round 5 proved it: the call was accepted, the ability
>    fired, and that check still returned `true`. What the engine does say once
>    the ability is active is `error: unit '1' does not support this special
>    ability`.
>
> ### Round 6 changes
> - `FIRE_ON_MELEE` is now **off**. Charging only.
> - **A real charge test**, from four signals: `is_moving_fast()` (running),
>   `not is_in_melee()` (not yet in contact), `current_target()` (an enemy is the
>   target), and — the discriminator — `position()` vs `ordered_position()`, which
>   the documentation says are **equal while attacking a unit** but far apart
>   while walking to a spot. Tolerance: 8 m.
> - **The old cooldown brake**: after an accepted activation, no further attempts
>   for **90 s**, the ability's own `recharge_time`.
> - Heartbeats now print `tgt=` and `gap=` so the charge decision is visible.
>
> ### What to do now
> 1. **Fully exit the game and launcher**, relaunch.
> 2. Battle with **Boris Todbringer**. Try both: order him to **move to an empty
>    spot** (should NOT fire) and order him to **attack an enemy** (SHOULD fire).
> 3. Tell me what you see, and whether the log's `tgt=`/`gap=` values match what
>    he was actually doing.

> ## STATUS (earlier): ROUND 3 RAN — cause found. Round 4 installed and ready.
>
> ### Round 3 result: the order WAS reaching the engine, and being rejected
> The log caught the exact error:
> ```
> perform_special_ability : ok=false
>   ERROR: bad argument #1 to 'perform_special_ability'
>          (battle.unit expected, got no value)
> ```
> The published argument order — `perform_special_ability(ability_key,
> target_unit)` — **is wrong for this build.** The real call wants a
> `battle.unit` as the **first** argument.
>
> ### And that explains the two things you saw
> - **The crossed-out ability icon and the unit stopping**: my round-3 fallback
>   tried `perform_special_ability_ground(ability_key, position, ...)`. That call
>   *reported success* (`ok=true`) while leaving the unit holding a targeting
>   cursor — a self-buff with `target_ground = false` cannot be aimed at ground —
>   and because the order took control of the unit, its movement order was
>   cancelled. Both symptoms come from that one wrong call. It is now **gone**.
> - `take_control()` also succeeded and is another candidate for cancelling the
>   order, so it is now **off by default**.
>
> ### What round 4 changes
> - The ground variant is **deleted** from the code path.
> - `take_control()` is **off**; `release_control()` stays on so the card is not
>   left greyed out.
> - **A candidate list** is tried in order, logging each result, keeping the
>   first that works: `(unit, key)` → `(unit, key, unit)` →
>   `perform_special_ability_q(unit, key)` → `(unit)`.
> - **Objective success test**: a real activation starts the cooldown, so
>   `can_perform_special_ability` must flip to `false`. If the call is accepted
>   but the ability stays available, a **1-second-later re-check** is logged.
> - Once a candidate is confirmed working, the log says
>   `VERDICT: ACTIVATION CONFIRMED by cooldown` and locks to it.
>
> ### What you do now
> 1. **Fully exit the game and launcher**, relaunch.
> 2. Battle with **Boris Todbringer**, order him onto a distant enemy, let it
>    run **at least 60 seconds**.
> 3. Note whether the unit still stops, or the crossed icon still appears — if
>    those are gone but the ability fires, that confirms the ground call was the
>    whole cause.
> 4. Tell me when done.
>
> ### What your FIRST battle proved (from the log)
> - **The mod loaded.** Game loader log: `Loading mod file
>   [script\battle\mod\zz_test_deadly_onslaught.lua] ... loaded successfully`.
>   So the **Movie-pack trick works** — the engine does load it from `data/`
>   with no mod-manager step. That was the last unproven assumption.
> - **The battle manager and unit list work.** `watching 2 unit(s) in the local
>   player's army`.
> - **Ability detection works.** Boris Todbringer was found as
>   `wh_dlc03_emp_cha_boris_todbringer_0`, and reported
>   `owns Deadly Onslaught = true | usable right now = true`.
> - **Your observation was confirmed in data**: the Empire Captain reports
>   `owns Deadly Onslaught = false`. He only gets it in campaign, from the skill.
> - **Nothing fired.** No `FIRED` lines. Most likely the battle ended before
>   Boris ever ran fast or entered melee — the old build had no way to record
>   that, which is why round 2 adds a heartbeat.
>
> ### What changed for round 2
> - A **heartbeat line every 5 s**: battle phase + per-unit `alive / fast /
>   melee / can`, so a run that fires nothing is still fully explained.
> - A **"poll is running (first tick)"** line, to prove the repeating timer
>   works at all.
> - Accepts the **second, legacy ability key** as well.
> - **Late detection**: if a unit's abilities are not all attached when we first
>   look, we re-check every 4 s instead of failing silently.
>
> ### What you do now
> 1. **Fully exit the game and launcher** (the pack changed), then relaunch.
> 2. Fight a battle with **Boris Todbringer** — you already proved he has the
>    ability in skirmish. The Empire Captain is not needed any more, though
>    leaving him in does no harm.
> 3. **Actually engage**: order Boris to charge a distant enemy so he *runs* into
>    it, then let the fight run for **at least 30–60 seconds**.
> 4. Watch two things: does Deadly Onslaught fire **on its own**, and does
>    Boris's unit card **grey out / can you still command him** afterwards.
> 5. Tell me when done.
>
> The log file is appended, never overwritten, so round 1's evidence is kept
> above round 2's in the same file.

This folder holds the mod source. It needs only **one file** in the pack:

```
script/battle/mod/zz_test_deadly_onslaught.lua   <- the mod logic AND its own log writer
```

`script/enable_console_logging` is a leftover from the first draft and is **not
needed** — the script writes its own log file directly with `io.open`, so it
does not depend on the game's script-logging switch. (It is harmless if you
build it in; it just isn't required.)

---

## 1. What the test proves

Four things, in order:

1. That a Lua file dropped into `script/battle/mod/` **runs in a campaign battle** (not just a custom one).
2. That a script can **ask the game about a specific ability** on a specific unit.
3. That a script can **make that unit fire the ability**, with no click from you.
4. What happens to your **control of that unit** when a script does it — this is the unknown from the feasibility report, and the main reason to run the test.

---

## 2. The ability, from the game's own data

| Field | Value |
|---|---|
| Ability key | `wh_main_character_abilities_deadly_onslaught` |
| Type | `wh_type_augment`, `affect_self = true` (a buff on the Captain himself) |
| Active time | 31 seconds |
| Recharge | 90 seconds |
| Uses | unlimited (`num_uses = -1`) |
| Magic cost | 0 |
| Passive? | `false` — it is a player-activated ability, which is why it needs this mod |
| How the AI treats it | `ai_usage = augment_charge_self` — the game's own AI fires it on the charge, which is why "on charging" is a sensible trigger to copy |
| Granted by | the skill `wh_main_skill_all_all_self_deadly_onslaught` ("Deadly Onslaught"). In `unit_abilities` it is marked `requires_effect_enabling = true`, meaning the Captain only has it once the skill is unlocked. If the Captain does not have the skill, the script correctly does nothing — and the log will tell you so. |

---

## 3. Build it (RPFM)

> **Menu names depend on your RPFM version.** Current RPFM (5.x) calls the menu
> **Pack**; older versions and most community guides call it **PackFile**.
> If you cannot find an entry, press `Ctrl+P` (command palette) and type its name.

1. Install **RPFM** (Rusted PackFile Manager). Free, open source.
2. Point RPFM at your game: **Preferences -> Paths** -> Warhammer 3 instal folder
   (normally auto-detected from Steam). Without this, **Install** has nowhere to copy to.
3. Pick one of the two workflows below. **A is the one that matches this folder.**

### A. MyMod workflow (recommended here, because you already have a folder of files)

1. `MyMod -> New MyMod`. Name it `zz_test_deadly_onslaught` (**no spaces allowed**).
   RPFM creates a folder *and* an empty `.pack` inside it, type **Mod** by default.
2. `MyMod -> Open MyMod Folder`, then copy this project's `script/` folder into it
   so it sits next to the `.pack`, producing:
   - `script/battle/mod/zz_test_deadly_onslaught.lua`
   - `script/enable_console_logging`
3. Right-click the pack root in the tree -> **Import** (folder -> pack).
4. Right-click the pack root -> **Install** (copies the `.pack` into
   `<game>/data/`).

### B. Plain pack workflow (building by hand inside RPFM)

1. `Pack -> New Pack`. This creates an empty pack **in memory**; it is not on disk
   yet, and it already defaults to type **Mod** for Warhammer 3.
2. In the pack tree, create the folder path `script/battle/mod/` and add
   `zz_test_deadly_onslaught.lua`; then add `script/enable_console_logging`.
   (Right-click the pack root to add folders/files, or use **Import** to pull in
   a folder that already has the right layout.)
3. `Pack -> Save Pack As` and name the file `zz_test_deadly_onslaught.pack`.
   The type can be checked or changed by right-clicking the pack root ->
   **Change PackFile Type**.
4. Right-click the pack root -> **Install**.

**Both workflows end the same way:** the `.pack` sits in
`steamapps/common/Total War WARHAMMER III/data/`, and you tick it in the mod
manager before launching.

**Important:** the pack filename must stay unique. If another mod uses the same
filename, one overwrites the other. That is why it is prefixed `zz_test_`.


---

## 4. Run the test

1. Start any battle where you have **an Empire Captain with the Deadly Onslaught skill unlocked**.
   - Custom battle is the fastest place to try. If the log shows `can use Deadly Onslaught = false` for your Captain, he does not have the ability in that setup — switch to a campaign Captain who has taken the skill.
2. Order the Captain to **charge** an enemy unit (run him at them; don't let him arrive first).
3. Watch: he should fire Deadly Onslaught himself the moment he is running, before contact.
4. Watch the unit card: does it grey out for a moment? Can you still give him orders afterwards? **Write down what you see** — that answer decides how the full mod must be built.

### Reading the log

The game writes `script_log_DDMMYY_HHMM.txt` in your Total War WARHAMMER III install folder (usually `steamapps/common/Total War WARHAMMER III/`). A new one is created every time you enter a battle. Open the newest and search for **`zz_test_deadly_onslaught`**.

What you should see:

```
[zz_test_deadly_onslaught] loaded. Polling every 250 ms for wh_main_character_abilities_deadly_onslaught
[zz_test_deadly_onslaught] combat phase started - building watch list
[zz_test_deadly_onslaught] watching 20 unit(s) in the local player's army
[zz_test_deadly_onslaught]   unit type 'wh_main_emp_cha_captain_0', ui id 14, has 3 abilities, can use Deadly Onslaught = true
[zz_test_deadly_onslaught] FIRED Deadly Onslaught on ui id 14
```

There is also a second log, `lua_mod_log.txt`, written by the game's own mod loader (the same lines, tagged). If one is missing, check the other.

---

## 5. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| No `[zz_test_deadly_onslaught]` lines anywhere | The pack is not loading, or the file is at the wrong path | Check the path is exactly `script/battle/mod/<name>.lua`, pack type is **Mod**, mod ticked in the manager |
| Lines appear but the log file itself is missing | `out()` logging is off | `script/enable_console_logging` must be in the pack. Alternative: the Script Debug Activator mod, or MCT's logging setting |
| `watching 0 unit(s)` | The army list was built too early, or reinforcements | The list is built on the combat phase and on the first successful poll; the line says which |
| `can use Deadly Onslaught = false` for your Captain | He has not unlocked the skill, or the ability is on cooldown, or he is dead | Take the skill; or test again 90 s later |
| `can use ... = true` but never fires | He never satisfied the charge condition | He must be **running** (`is_moving_fast`) and **not yet in melee**. Walking does not count. If he is already fighting when the poll runs, it stays silent by design |
| Fires but the commander is odd | You are seeing the known limitation: the scripting interface has no true "is charging" switch | See section 7 |
| Unit card greys out after it fires | The script's controller took control of the unit | This is the control-handover issue. Try removing the `release_control()` line, or replacing `perform_special_ability` with `perform_special_ability_q` |

---

## 6. Poking at it manually with the Lua Console

Subscribe to **Modding Development Tools: Lua Console**, press **Shift+F3** in a battle, and paste lines to interrogate the game directly. This is the fastest way to learn the API.

```lua
-- what units do I have?
local s = bm:get_scriptunits_for_local_players_army()
out("units: " .. tostring(s:count()))

-- list every ability the first unit owns
local u = s:item(1).unit
for _, k in pairs(u:owned_special_abilities()) do out("ability: " .. k) end

-- does THIS unit have Deadly Onslaught right now?
out("can fire: " .. tostring(u:can_perform_special_ability("wh_main_character_abilities_deadly_onslaught")))

-- is it running/charging? is it in melee?
out("moving fast: " .. tostring(u:is_moving_fast()))
out("in melee: " .. tostring(u:is_in_melee()))

-- fire it manually, once, and see what happens to your control of it
s:item(1).uc:perform_special_ability("wh_main_character_abilities_deadly_onslaught")
```

The last line is the single most informative experiment in this whole test. It isolates the control-handover question from all the rest of the logic.

---

## 7. What is verified and what is not

**Verified here (run outside the game, against a mock of the same API calls):**
- The file is valid Lua and compiles.
- Given four units — one charging, one in melee, one walking, one dead — the script fires **only** on the charging one.
- Over 200 polls (50 seconds at 250 ms) it fires exactly **3 times** on that unit, respecting the 20-second brake.
- Once the unit is in melee it stops firing (0 fires over the next 200 polls).
- The diagnostic lines print the ability ownership check for every unit.

**Not verified (needs the game):**
- That `bm:get_scriptunits_for_local_players_army()` returns units with a usable `.uc` handle in every battle type. The code logs a warning line if `.uc` is nil.
- The exact behaviour of `perform_special_ability` on a **player-controlled** unit: whether the card greys out, whether the unit's current order is cancelled, and whether `release_control()` restores control cleanly. This is the real unknown and the reason for the test.
- Whether `can_perform_special_ability()` accounts for the 90-second cooldown. The 20-second brake exists in case it does not.

---

## 8. Where this goes next

Once the test runs, the generalisation is a **rule table** — one entry per ability:

```lua
local RULES = {
  ["wh_main_character_abilities_deadly_onslaught"] = { trigger = "charging" },
  ["wh_main_character_abilities_heroic_killing_blow"] = { trigger = "in_melee" },
  ["wh2_dlc11_..._potion_of_healing"]  = { trigger = "health_below", value = 0.75 },
  ...
}
```

…plus two condition helpers (`charging`, `in_melee`, `health_below`, `morale_below`, `off_cooldown`…) and, for abilities that need a target, a target-picking helper. That is the whole architecture. The remaining work is not engineering — it is deciding, for several hundred abilities, what the right trigger is, and that is the same job the existing Workshop mods did on paper.
