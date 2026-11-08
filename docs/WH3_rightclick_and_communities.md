# ComponentRClickUp: has anyone used it? — and where WH3 modders actually are

Prepared 2026-09-27. Companion to the battle-script test case in
`C:\Users\vlady\Desktop\WH3_mod\mod_source\`.

## 1. The short answer

**No public trace of `ComponentRClickUp` being used in WH3 (or any Total War) modding, and the
engine's own UI layouts explain why: a component only receives the mouse events its layout file
declares, and no vanilla layout declares a right-click.**

Right-clicks in the vanilla UI are wired *per component* through two other mechanisms, neither of
which exists on the ability icons.

## 2. The evidence

### 2.1 No script anywhere uses it
| Where | `ComponentRClickUp` |
|---|---|
| The game's own 901 shipped `.lua` files | **1 file** — `script/events.lua`, where it appears only as a *name in the event table*. No script listens for it. |
| The 8 mods subscribed on this machine | **0** (while `ComponentLClickUp` appears 1/1/2 times in the three that do UI work — incl. a 227 MB overhaul with 527 listeners) |
| The community wiki `tw-modding.com` (all 37 pages) | **0 mentions**; its button tutorial teaches `ComponentLClickUp` |
| Web search for the exact string | returns nothing in any modding context |

Practical note: `grep.app` returns "no results" for `perform_special_ability` too, so **that engine
does not index Total War repos** and its silence proves nothing. Don't cite it.

### 2.2 The mechanism, from the UI layouts themselves
`ui3.pack` ships **907** `.twui.xml` layouts, stored uncompressed, so they can be read directly:

| Declaration | Occurrences in 907 layouts |
|---|---|
| `name="lclick"` | **83** |
| `name="rclick"` | **0** |
| `callback_id="ContextCommandLeftClick"` | **2 415** |
| `callback_id="ContextCommandRightClick"` | **115** |
| `mouse_event0="rclick"` (as a property) | 22 |

So a component handles a mouse button only if its layout says so. Three real examples:

```xml
<!-- the way CA wires right-click where it does exist: a property + a message -->
<property name="mouse_event0" value="rclick"/>
<property name="mouse_event1" value="lclick"/>
<property name="target_id"      value="^1"/>
…context_function_id="UiMsg(&quot;ingredient_selected&quot;)"
```
```xml
<!-- battle: a toggleable slot's two actions -->
<callback_with_context callback_id="ContextCommandLeftClick"
   context_object_id="CcoBattleToggleableSlotBuildable" context_function_id="PrimaryAction"/>
<callback_with_context callback_id="ContextCommandRightClick"
   context_object_id="CcoBattleToggleableSlotBuildable" context_function_id="SecondaryAction"/>
```

The **unit card** — the thing that draws the ability icons — declares
`name="lclick"` (×2) and `ContextCommandLeftClick` (×6) and **no right-click at all**
(`ui/common ui/land_unit_card.twui.xml`). Its ability buttons are instantiated by the engine from
the card's `template_ability` component.

**Therefore:** clicking the ability icon with the right button raises no component event, because
nothing on that component is registered to answer it. The click falls through to the game's normal
right-click handling (deselect / cancel / move order). This is not a scripting mistake and cannot
be fixed from a script.

### 2.3 To make right-click work, it would take a UI *layout* mod
Replace `land_unit_card.twui.xml` with a version that declares a right-click handler on the
ability button, and route what it raises into script (the `mouse_event0="rclick"` +
`UiMsg(...)` pattern above is CA's own recipe for that). Costs, honestly:

- it is a **vanilla UI file replacement**, so it conflicts with every other UI mod;
- the ability buttons are **engine-instanced**, so the pattern has to be attached to a template the
  engine controls, and the runtime component names are not knowable from the layout alone;
- it breaks on any patch that touches the unit card.

Versus: the script-only button already shipped (round 16) does the same job with no UI file at all.

## 3. Where the WH3 modding community actually is

| Community | What it is | Notes |
|---|---|---|
| **Da Modding Den** — `discord.com/invite/moddingden` | THE Total War modding Discord, Warhammer-focused | ~20 000 members; where the people who wrote the pages below answer questions. Channels for scripting ("Eldritch Knowledge" is cited by the CCO tutorial as the source for advanced UI knowledge) |
| **tw-modding.com** (Total War Modding wiki) | Community wiki, born out of Modding Den | 37 pages: `UI:Intro`, `UI:Build-a-Button Workshop`, `Tutorial:Component Context Objects (CCOs)`, `TWUI.XML Layout Files`, `Lua/First Script`, `Troubleshooting`. Search index is empty — browse the page list |
| **chadvandy.github.io/tw_modding_resources/WH3** | Generated API reference (battle/campaign/frontend) | The site used earlier for `battle_unitcontroller`; has `UI Scripting`, `Scripted Events`, `uicomponent` (incl. `AddScriptEventReporter`) |
| **Total War Center** — `twcenter.net/forums/db-editing-scripting.2198/` | The veteran modding forum | "DB Editing & Scripting" sub-forum is the right place for a Lua question |
| **CA official forums** — `community.creative-assembly.com` → Modding Corner | Developer-hosted, low traffic | Patch notes and mod-tool announcements |
| **r/totalwar** | Biggest audience, shallowest depth | Good for "does a mod exist", not for engine internals |
| **Consul Scriptum** — `consulscriptum.com` | A Lua scripting framework with in-game debug tools | `events.ComponentLClickUp` wrapper; `/debug_onclick` and `/debug_mouseover` print metadata for the component you click/hover, plus an HTML UI debugger. **Best tool available for identifying UI components** — and it names no right-click event |

### What to ask, and where
A single post in Da Modding Den's scripting channel gets a better answer than any reverse
engineering: quote the event table line (`ComponentRClickUp = {}` in `events.lua`), state that a
catch-all listener logged zero events across a battle while the player right-clicked ability icons,
and ask whether any layout declares `rclick` and whether any script has ever received the event.
The layout evidence above is what makes the question answerable — it points straight at the
`name="lclick"` / `name="rclick"` declaration.

## 4. One thing my test did not rule out

The catch-all listener logged **zero** events, which is consistent with the layout mechanism — but
it also can't distinguish "no component in that battle had an rclick handler" from "the listener
never registered". A one-battle control settles it: log the listener registration at load, listen
catch-all for `ComponentLClickUp` **and** `ComponentRClickUp` in the same build, then click the
ability icon (left, then right) and right-click a buildable slot (which *does* declare
`ContextCommandRightClick` — across the battlefield those slots are the control case).

- left-click logged, right-click on the icon silent → the event is real but the icon has no handler
  → route confirmed dead, exactly as the layouts say.
- both silent → the listener itself is the problem, and the event table entry means nothing.

Build time for that diagnostic: under an hour, one battle to read.
