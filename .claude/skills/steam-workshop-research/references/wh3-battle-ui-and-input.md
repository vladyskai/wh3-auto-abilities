# Total War battle UI and player input

Depth for a script that must be **controlled or observed by the player** during a battle:
a HUD control, a key, or a reaction to something the player did. The scripting loop itself
lives in `references/wh3-mod-authoring.md`; this file is the interaction layer.

## Which clock your callback runs on — decide this before calling any UI method

There are two timers and they are not interchangeable. UI calls made on the wrong one do
nothing at all, silently, and can take the battle's timers down with them.

| Registration | Clock | What is safe to do in it |
|---|---|---|
| `bm:repeat_callback(fn, ms, name)`, `bm:callback(fn, ms, name)` | battle **model** time (stops while the game is paused) | trigger logic, queries, orders — **no UI calls** |
| `bm:repeat_real_callback(fn, ms, name)`, `bm:real_callback(fn, ms, name)` | synchronised to **UI updates** | anything touching uicomponents |
| `bm:register_phase_change_callback(phase, fn)` | phase dispatch | **the only timer-driven context in which painting takes effect** — see the rule below |
| `core:add_listener(name, event, filter, cb, persist)` | UI event dispatch | UI work |

**Rule: create and paint in the phase callbacks; register your repeat once and never touch the
registry again.** Only two contexts actually paint a control: a **phase callback** and a **UI
click handler**. A control created from a timer keeps the template's placeholder image forever —
`SetImagePath` no-ops there while `SetState` still applies, so the perimeter lights up with a
stale glyph in it and it reads as a styling bug. A *real* timer is no better than the model one for
this; "UI-synchronised" is not the requirement, the phase/click dispatch is. UI work in the phase
dispatch can also leave the battle's model timer dead, so the feature's own poll goes quiet in the
same round the button finally looks right.

Do not try to fix that by moving timers around. Two mechanisms make the "repair" strictly worse
than the symptom:

- `bm:remove_callback(name)` unregisters **before** anything is added back, so a re-add that raises
  has deleted a healthy timer and put nothing in its place;
- and it cannot be undone afterwards. All the battle's repeating callbacks ride on one engine timer
  whose driver re-arms it only *after* its callback loop completes, so once that driver has lost its
  engine timer, re-registering is inert — every re-add reports success while the tick counter never
  moves again, which reads as a working repair in the log and a dead feature on screen.

So:

1. create and paint in the `Deployment`/`Deployed` callbacks;
2. register the repeating callback **once at load**, and never remove it;
3. let a `bm:repeat_real_callback` **watch** the repeat's tick counter and *report* a stall after
   two consecutive frozen checks (a pause legitimately freezes model time, so one silent check
   means nothing). Reporting only: it makes no engine call, and it repairs nothing.

Keep the phase-change listener log-only, and add nothing on a third clock — every retry in a
context that does not work is a fresh way to break the battle. If the look and the trigger turn out
to be mutually exclusive, pick the one the user asked for and say which you gave up.

Symptom → where to look:

| Symptom | Cause |
|---|---|
| Control shows the template's vendor placeholder (e.g. a movement-speed glyph) even though `SetImagePath` was called | The paint ran in a context that cannot paint — a model timer **or** a real timer. Create and paint in a phase callback, or in a click handler |
| The control's state changes apply but the icon never does | Same cause: `SetState` lands in contexts where `SetImagePath` does not. Move the whole paint into the phase callback |
| Engine→script callbacks dry up mid-battle (ticks, heartbeats or phase events stop) while UI listeners keep working | Something issued in the wrong context took the timer driver down. **Do not re-register to recover it** — re-registration is inert once the driver is gone. Read the log's last lines before the silence: they name what ran |
| The control's look disagrees with the state the script believes it is in | Log the state the component reports for itself, next to the one you asked for (below) |

## What input the engine actually gives a script

Check this inventory before designing anything, because two of these look like a general
hook and are not.

| Mechanism | What it really delivers |
|---|---|
| `battle:register_input_handler` / `bm:register_input_handler_callback(input, cb, name)` | **Camera movement only.** The valid input strings are `move forward`, `move forward fast`, `move backward`, `move left`, `move right`, `rotate right/left`, `move up/down`, `rotate up/down`, and the `edge …` variants. There is no general keyboard hook; do not design a hotkey around this |
| `bm:register_command_handler_callback(command, cb, name)` | Game commands, as an event object. Useful ones: **`Special Ability`** (with `event:get_string1()` = the ability key, so a player clicking an ability is detectable), `Change Skirmish`, `Change Melee`, `Fire At Will`, `Double Click Unit Card`, `Attack Unit`, `Move` (`get_bool1()` = moving fast), `Halt`, `Withdraw`, `Unit Left Battlefield`, `Battle Results`. Each event type only implements the methods relevant to it, so read `get_string1` only where the docs list it |
| `core:add_listener(name, "<Component event>", filter, cb, persist)` | Player UI input on a component — **for left-clicks only in practice.** The engine's own event table (`script/events.lua`) is the inventory of *names*: `ComponentLClickUp`, `ComponentLDBLClickUp`, `ComponentRClickUp`, `ComponentMouseOn`/`ComponentMouseOff`, `ComponentAnimationFinished`. Measured delivery in a battle: `ComponentLClickUp` fires for every HUD button the player presses, `ComponentMouseOn`/`Off` fire while hovering, and `ComponentRClickUp` / `ComponentLDBLClickUp` fire **never** — see the firehose test below. `context.string` is the component's name (for one you created, the string passed to `CreateComponent`; for one the engine drew, its **runtime name, which may be generated**) |
| `uic:AddScriptEventReporter()` | Not an input, a prerequisite: a component fires only a subset of its events by default, and this makes one report **all** of them (wiki `UI:Main Page`; vanilla: `_lib/lib_movie_overlay.lua`). Apply per component *and* per ancestor. It cannot conjure an event the engine does not raise |
| `core:add_listener(name, "ShortcutTriggered" \| "ShortcutPressed", …)` | **The keyboard, and the one player-input family that reliably reaches script in battle.** `context.string` is the shortcut's name (`step_r`, `step_l`, `step_bck`, `step_fwd` observed). No vanilla script listens to either, so nothing is hijacked; the names that exist to bind against are declared per component as `shortcut` / `shortcut0..N` properties. Detail below |
| `bm:steal_escape_key_with_callback(name, cb, is_persistent)` / `battle:steal_escape_key()` | A real key. Entries form a **LIFO stack**: only the most recently registered callback is notified, and a non-persistent entry is removed once called, releasing the key when the stack empties. While the stack is non-empty the UI never receives ESC, so the pause menu will not open from that key — say so when offering it |
| `bm:register_unit_selection_callback(unit, cb)` | Fires on selection/deselection, many times per battle. Too chatty to be a switch |
| A settings framework (Mod Configuration Tool and similar) | A **menu panel**, not a battle control. It gives the player a setting to read at battle start, not a switch to flip mid-battle, and it adds a dependency |

For the bare `battle:register_*` forms, the engine allows **one** handler and overwrites any
existing one — always take the `battle_manager:register_*_callback` wrapper, which the docs
recommend for exactly this reason.

## Listening instead of drawing — read the layout before designing around it

The engine's own event table (`script/events.lua`) is the inventory of event **names**
(`ComponentLClickUp`, `ComponentLDBLClickUp`, `ComponentRClickUp`, `ComponentMouseOn`/`Off`,
`ComponentAnimationFinished`), and grepping it is right (`RClick`, `Double`, `Mouse`, `Click`).
**But a name in that table is not a delivered event.** A UI component only receives the mouse
interactions its **layout file** declares, and no vanilla layout declares right-click:

```bash
# layouts live in data/ui3.pack, stored uncompressed, so a raw byte scan is valid
# 907 layouts in total
cd "<game>/data"
grep -a -o 'name="lclick"'                ui3.pack | wc -l   #   83
grep -a -o 'name="rclick"'                ui3.pack | wc -l   #    0
grep -a -o 'ContextCommandLeftClick'      ui3.pack | wc -l   # 2415
grep -a -o 'ContextCommandRightClick'     ui3.pack | wc -l   #  115
grep -a -o 'mouse_event0="rclick"'       ui3.pack | wc -l   #   22
```

The unit card — the thing that draws the ability icons — declares `name="lclick"` and
`ContextCommandLeftClick` and **no right-click at all**
(`ui/common ui/land_unit_card.twui.xml`). So a catch-all `ComponentRClickUp` listener logs zero
events there however the player clicks: measured in a real battle, not inferred from docs. Where
CA does support right-click it is wired per component, never globally — as a property
(`mouse_event0="rclick"` beside `UiMsg(...)`) or as a callback
(`ContextCommandRightClick` → `SecondaryAction` on a battle's toggleable slots, 115 uses, mostly
campaign UI).

Consequences:

- **Enumerate the layout declarations, not just the event table**, before designing around an
  interaction. An interaction the layout does not declare is not a scripting problem.
- **But it is a buildable one** — the layout can be told to react to a right-click, using CA's own
  documented callback (recipe below). State the cost before taking it: it means shipping a
  replacement for a vanilla UI file.
- A listener on a component the game already draws is still worth checking first, and is cheap
  when the interaction *is* declared: no `CreateComponent`, no icon in the pack, no clock
  question, nothing to repaint. The ability bar and unit card are the densest source of per-unit
  affordances (ability buttons come from the unit card layout's component id `template_ability`,
  which the engine instantiates once per card per ability).
- **Three tools name a component for you**, instead of guessing: `output_uicomponent_on_click()`
  (one line in a `.lua` under the loader's mod path — click anything, it prints the path from
  root), `print_all_uicomponent_children(uic)` (dump a subtree's paths), the in-game **UI Context
  Viewer** overlay (enabled by a checkbox in settings, opened with the `` ` `` key — shows the live
  component tree and each component's contexts), and Consul Scriptum's `/debug_onclick` +
  `/debug_mouseover` console commands with its HTML UI debugger. Reach for these before building a
  scanner; the mod-side scan is for cases the overlays cannot answer at runtime.

### Adding an interaction to a component the engine draws — measured, and closed

**This route does not exist, and finding that out cost several battles.** Two ways of telling a
vanilla component to react to a right-click were built, installed and battle-tested; both are dead:

| Route | What actually happens |
|---|---|
| `<callback_with_context callback_id="ContextEventBroadcaster">` + `<property name="rclick" value="my_event"/>` | The broadcast is **UI-internal** — CA's own docs say it "will notify other callbacks that listen to UI_UPDATE_MSG events". No script listener on `ContextTriggerEvent` ever fired, and no `ComponentRClickUp` was raised for the component either |
| `<callback_with_context callback_id="ContextCommandRightClick">` + `context_function_id="self.SetProperty(&quot;my_flag&quot;, &quot;1&quot;)"` | The callback runs, but script **cannot read the result**: `GetProperty("my_flag")` returns the string `my_flag` — for an undeclared property, for one declared in `<userproperties>`, and for a property vanilla itself sets (`icon_index`), on a component whose `Id()` and parent chain proved it was the one the engine reports |

So a layout edit can change what the **UI** does, and cannot hand a value to a script. Design
around the channels the engine reports (command events, shortcuts), or around a click the player
makes anyway — do not spend battles on layout callbacks.

### Ask a component to report its events — and know what that does not buy

Components fire only some of their events by default. `uic:AddScriptEventReporter()` (wiki
`UI:Main Page`; vanilla's own use is `_lib/lib_movie_overlay.lua`, commented *"set the panel to
report all script events"*) makes one fire **all** of them — that is how vanilla listens for
`ComponentAnimationFinished`. Apply it to the component you care about **and its ancestor chain**, a
click can be credited to a container, and log the outcome per level:

```lua
pcall(function() node:AddScriptEventReporter() end)   -- walk node = node:Parent() up the chain
```

**Measured limit:** it does not conjure events the engine never raises. With the reporter on the
ability button and every ancestor, in a battle where the player right-clicked that icon repeatedly
and double-clicked the unit card, still **zero** `ComponentRClickUp` and **zero**
`ComponentLDBLClickUp` arrived — while left-clicks and hover events poured in for the same
components.

### The firehose test — settle a whole channel family in one battle

When the question is "does the engine ever deliver X?", stop iterating on listeners. Parse the
engine's own event table and subscribe to **every** name it declares:

```python
import re
keys = re.findall(r"^\s*([A-Z][A-Za-z0-9_]*)\s*=\s*\{\}\s*,?\s*$",
                  open("script/events.lua", encoding="utf-8", errors="replace").read(), re.M)
# 399 names in WH3; register each with pcall and count the accepted number
```

In the shared callback: cap lines **per event name**, cap the total, and let anything touching your
own components (or the unit card whose id is the unit's `unique_ui_id`) **bypass every cap** — else
the first few hover events of a noisy name bury the interesting ones. Print the delivered-name
counts as the finding.

| Result | What it means |
|---|---|
| The name you need appears | The channel exists; gate on it |
| A sibling appears and yours never does (`ComponentMouseOn`/`Off` and `ComponentLClickUp` firing, `ComponentRClickUp`/`ComponentLDBLClickUp` absent) | The engine does not raise it in this context — a **constraint**, not a filter bug. Stop and report it with the counts |
| Only engine-internal events arrive | The context itself (battle vs campaign) is the limit |

Run this before promising any event-driven feature. It is what converts an unbounded "must be our
filter" loop into a defensible answer — and it is how the right-click question was finally closed.

The declared vocabulary **is** the ceiling: the engine exposes no event-enumeration or
property-enumeration call, so this net is complete by construction and there is nothing "hidden in
another variable" to find. When the user asks whether everything can be logged, the honest answer is
that everything *reachable* is logged by this method, and anything outside the declared surface is
unobservable from a script.

### A key the engine reports

Keyboard input is the one player-input channel that reaches script in battle:

| Piece | Detail |
|---|---|
| Events | `ShortcutTriggered` and `ShortcutPressed`, both carrying the shortcut's name in `context.string` |
| Declaration | A component declares the shortcuts it answers with `shortcut` / `shortcut0..N` user properties in its layout (`ui/battle ui/hud_battle.twui.xml` and others ship them) |
| Conflict | No vanilla script listens to either, so nothing is hijacked — unlike `steal_escape_key_with_callback`, which takes the keyboard and stops the pause menu opening |
| Filtering | **Whitelist one name; do not blacklist the noisy family.** Every camera action arrives (`cam_up`, `cam_down`, `rot_d`, `rot_u`, `step_l`, `step_bck`, `step_fwd`, `intelli_zoom`), so a prefix blacklist of `step_*` alone left the switch flipping dozens of times while the player simply looked around |
| Debounce | The **same name arrives two or three times per key press** (`ShortcutTriggered` plus `ShortcutPressed`, sometimes twice each). Without a debounce the toggle flips and flips back in the same instant: the state is correct-looking in the log and the user sees *nothing happen* |

Observed names in one battle, and which are usable as a switch:

| Name | What it is | Usable as a switch? |
|---|---|---|
| `usegroup0` … `usegroup9` | select control group N — **does nothing when that group is empty** | **yes — the best choice**; name the key in the build and tell the user which number, in case they use that group |
| `cam_up` / `cam_down` / `rot_u` / `rot_d` / `step_*` / `intelli_zoom` | camera movement and zoom | no: they fire continuously while the player looks around |
| `toggle_pause`, `toggle_ui`, `show_tactical_map`, `show_radial`, `toggle_group`, `cycle_next_spawn_zone`, `visibility_toggle_porthole` | real game actions | no: the switch would hijack them |
| `battle_land_withdraw`, `battle_land_guard_mode`, `battle_land_about_face`, `battle_land_strafe_left/right`, `battle_land_step_forward/backwards` | unit orders on the card | no: same reason |

So: pick a deliberate name (a number key), accept exactly that one, and log every other name as
ignored — the log then proves both halves in a single run.

```lua
local TOGGLE_KEY = "usegroup8"          -- one key, named up front
local last_name, last_tick = nil, -1

local function on_shortcut(name)
  if name ~= TOGGLE_KEY then log("key '" .. name .. "' ignored"); return end
  if name == last_name and tick_count <= last_tick + 1 then
    log("key '" .. name .. "' repeat - ignored")     -- one physical press, both events
    return
  end
  last_name, last_tick = name, tick_count
  set_auto(not AUTO_ENABLED)
end
```

`tick_count` is the mod's own poll counter (250 ms), so "same name inside one tick" is one press; a
wider window starts dropping genuine double-presses.

### Why you cannot repaint an engine-drawn component — measured, twice

**This does not work, and both halves look like they work.** On the ability button the engine draws,
two write attempts were battle-tested against a read-back:

| Attempt | What the engine said | What the screen did |
|---|---|---|
| `uic:SetImagePath("ui/battle ui/ability_icons/<other>.png", 8)` — index 8 read from the layout's own `icon_index` | `GetImagePath(8)` returned the **new** path on all ~190 swaps (`MATCHES` every time) | nothing — the icon never changed |
| `uic:SetState("inactive")` for the armed look | `CurrentState()` returned `inactive` (`MATCHES`) | nothing — the button was **already** `inactive` |

**The mechanism, measured over two further builds: a script write to an engine-drawn component
invalidates the reference you are holding.** After the first `SetState`/`SetImagePath` the component's
own reads returned `function: 0x…` and `'0'` instead of values, and a re-acquire walk looking for its
`Id()` could not find it any more — every later read and write hit a dead object. That is why no
swap, state, frame art or tooltip ever appeared on screen. It also retires the first explanation
("the game re-drives that state; the button was already `inactive`"): the same component read
`active` in one run and `inactive` in another, and looked unchanged on screen in both, so the state
value was never evidence about pixels. Its ten states are `active`, `hover`, `down`, `down_off`,
`inactive` (normal) × the `selected_*` variants (that unit selected), art
`ui/skins/default/button_ability_<state>.png` — useful material for a *diagnostic dump*, not for a
restyle. Re-acquire a handle before reusing it after any write, and treat a failed re-acquire as the
finding: the component is no longer addressable.

**The rule: a read-back that matches proves the component *stored* the value, never that the frame
*drew* it.** Before writing cosmetics onto a component the engine draws, ask whether the engine
re-derives that property; if it does, the only ways to a visible change are:

1. **Change the game state it draws from** — for a battle ability, `unit:disable_special_ability(key, true)`
   makes the *engine* choose the dimmed look — **expect this trade to be refused**: it blocks manual
   use while disarmed, and the requirement for an auto-assist feature is that manual use keeps
   working in *every* state. Name the cost and get a decision before building it, rather than
   shipping it and discovering the objection in a bug report;
2. **Draw your own element** and accept one extra thing on screen — works on a stable parent (AI General repaints unit cards), measured **not** to draw when parented on an engine-drawn ability button (see the child-element section);
3. **No visual**, with the state readable from the log and from behaviour.

Offer those three with their costs rather than iterating — this class of repair is what absorbs a
user's battles. What *is* portable from the attempts: a diagnostic dump should read `NumStates()`,
`GetStateByIndex(i)`, `CurrentState()`, `GetImagePath(i)` and `NumImages()` off the component, because
those numbers are what make the possibilities concrete for the user. And when you need an image path
that is guaranteed to resolve for a *created* control, read one off a live component rather than
guessing `ui/skins/default/icon_*.png`.

### Finding the component the engine already draws

Do not guess the hierarchy: the engine's own script names it. `lib_battle_ui.lua`'s
`highlight_unit_abilities()` walks the unit-ability buttons like this, and every button answers
which ability it shows:

```lua
local parent = find_uicomponent(core:get_ui_root(), "battle_orders", "orders_parent", "behaviour_parent")
for i = 0, parent:ChildCount() - 1 do
  local slot   = UIComponent(parent:Find(i))
  local button = UIComponent(slot:Find(0))                      -- child 0 is the button
  local key    = tostring(button:InterfaceFunction("AbilityKeyForScript"))
  -- key is the ability's script key: match loosely ("onslaught") and log every key seen
end
```

`InterfaceFunction` is how a component exposes its own semantic queries, so this is the general
trick for identifying an engine-drawn affordance: grep the shipped scripts for the component id you
found in the layout, and copy the query the game itself uses on it.

**Look it up on a retry, not once.** These parents do not exist in the early phases, so a single
lookup from the first phase callback logs "not on screen" and the switch then has nothing to
toggle — retry from the real timer every couple of seconds until the parent appears, and log the
failure **once**, not per attempt.

### A generated component name: discover it, do not guess it

Because those instances are created per card, the name the event reports need not be the layout's
`template_ability` string. Take the event permissively and let the run answer:

```lua
local seen = {}

core:add_listener("my_mod_click", "ComponentLClickUp",   -- an event the layout declares
  function(context) return true end,          -- accept everything; the callback sorts it out
  function(context)
    local name = tostring(context.string)
    if not seen[name] then                    -- once per distinct name: no log spam
      seen[name] = true
      log("click on component '" .. name .. "'")
    end
    if string.find(string.lower(name), "abilit") then <toggle> end
  end,
  true)
```

Either it works, or the log names the real component for a one-line fix. This is the same
shape as the diagnostic-first logging rule for the trigger logic.

### Make the mock enforce the architecture rule

When the point of a route is that the mod never touches the UI layer, do not rely on intent —
have the harness's UI globals **raise**:

```lua
function find_uicomponent(...) error("the mod called find_uicomponent - it must not") end
function UIComponent(...) error("the mod called UIComponent - it must not") end
function core:get_ui_root() error("the mod called core:get_ui_root - it must not") end
```

Any build that reaches for the UI layer then fails at load in the harness instead of passing the
test and breaking in the user's battle. A constraint the harness asserts survives; a constraint
held by intent does not. The same trick carries any "this code path must not exist" rule.

### What is proven, and what is not

That the engine *lists* an event is proven — it is in its own event table. That the engine
*delivers* it anywhere is a second question, answered by the layout declarations above; and that
a *specific* component emits it is a third, which the first battle settles. The permissive filter
above is what makes that battle informative either way. Two side effects to have the user watch for
when a click is repurposed as an input: the game may already act on that click (cancel or queue
something), and a single global switch flag means clicking any unit's copy of the affordance
toggles the same one.

## The ability HUD map — the icons, and where they really are (measured)

Two battles (different factions, same player) swept once per second. Use this map instead of guessing
containers; re-sweep with the recipe below if a patch ever moves the HUD.

- **The visible ability wheel is `button_ability` … `button_ability6`** — six slots on a **circle**,
  centre ≈ `(95,944)` and radius ≈ `99` px on a 2560×1440 screen, slots ≈45° apart. Identical in both
  battles: only the abilities in the slots change (Deadly Onslaught held the top slot in one battle,
  an item ability in the other). Each slot answers `InterfaceFunction("AbilityKeyForScript")` with its
  key, `-` when empty. These six are the per-icon target set for "one indicator per ability".
- **`button_order1` … inside `button_parent` (a 304×59 strip) is a look-alike, not the dial.** Measured
  `visible=false` in both battles while its keys mirrored the selected unit's abilities (in one battle
  they were item/army abilities). A badge hooked to it reads the right keys and hides at the right
  times — and its coordinates are still not the wheel's. Confirm which container your numbers came from
  before computing placement.
- **Coordinate spaces:** `Position()` = screen space (the one that matters); `RelativePosition()` = the
  component's layout-anchor offset (a constant `(6,6)` for every wheel icon — useless for placement).
  The method table also carries `Bounds`, `DockingPoint`, `GetDockOffset`. A component **you created**
  misreports `Position()` (see the placement sections above), so calibrate the base placement by eye and
  treat the wheel's own numbers as the geometry.
- **Slot deltas from the top slot** (fit to both battles, max residual ≈6 px):

| slot | angle | delta from the top slot |
|---|---|---|
| 2 | 45° | (+70, +30) |
| 3 | right | (+98, +102) |
| 4 | −45° | (+66, +172) |
| 5 | 135° | (−68, +32) |
| 6 | left | (−94, +104) |

  **Which ability occupies which slot varies per unit - never hard-wire an ability to a fixed offset; compute the offset as `BADGE + (WHEEL_SLOT[k] - WHEEL_SLOT[1])` from the static six-slot table above, where k is the ability button's 1-based position among the **key-bearing** children of `button_parent` (count them; the `button_order*` ids accumulate digits, so the ordinal cannot be parsed from the id). Do NOT read the claimed button's own `Position()` for this: measured, it returns a **hidden-bar** coordinate ((1130,1052), (1189,1052) - y=1052 is the bar strip, not the wheel), and every offset computed from it placed the element off the intended icon. The bar's ordinal equals the wheel slot, so the static table needs no live read. Log `claim: <marker> is bar position <k> -> wheel slot (x,y)` per claim and a `[fallback]` line when the ordinal cannot be counted.** The geometry is constant, so a badge calibrated by eye onto one icon reaches every other icon by
  adding that icon's delta — and per-ability offsets computed as `base + delta` (`ox = BADGE_X + 70`,
  `oy = BADGE_Y + 30`) carry any later re-tune of the base along (confirmed in a battle:
  `zz_badge_set(-900,-200)` re-placed the second ability's badge at `-830,-170`). This does **not**
  contradict "never derive a position": the base is still tuned and user-confirmed, and the deltas are
  a fixed measured table, not a runtime read of the engine's lying coordinate.

### The INVENTORY sweep — how to measure a HUD you cannot see

Do not guess containers: instrument once, run one battle, read the map. Once per second (gate a counter
off the real timer), log one line per candidate id, every read pcall'd:

```
INVENTORY sweep t=<battle seconds> found=<n>/<total>
INVENTORY <id>: visible=<true/false/'?'> pos=(x,y) relpos=(x,y) dock=(dx,dy) state='<name>' key='<AbilityKeyForScript or ->'
```

- Resolve each id from `core:get_ui_root()` (recursive `Find(id, false)` with a bounded DFS fallback);
  a candidate that is missing still logs a `[not found]` line so absence is visible rather than silent,
  and a failed single read writes `?` in that field only.
- Candidates swept: `SA_dial`, `dial_frame`, `button_parent`, `button_ability` + `button_ability1..6`,
  `button_slot1..6`, every `button_order*` child of `button_parent`, `behaviour_parent`, `orders_parent`,
  `army_ability_parent`, `ability_parent`, plus the mod's own created components.
- Fit circles in the analysis pass (3 points give centre and radius; check the residual on the rest)
  instead of eyeballing: that turned "the numbers look wrong" into "the dial is a circle of radius 99,
  and the container we had hooked is a hidden bar".
- **When a measurement looks impossibly regular — collinear points for an arrangement that is visibly a
  circle — question which container the numbers belong to before reporting them as the coordinates.**
  The user caught this directly ("the ability dial is a circle, so those cannot be the coordinates");
  the numbers belonged to a different, hidden container.
- The sweep is noisy (~30 log lines/s once it runs alongside the older DIAL block). Strip it back out
  once the map is learned; it is instrumentation, not a feature.

## Adding a control to the battle HUD

A button does not require a custom layout file. Clone a template the game already ships:

```lua
-- layouts live in the vendor pack data/ui3.pack as ui/<area>/<name>.twui.xml
-- (ui.pack / ui2.pack hold images only)
local pane = find_uicomponent(core:get_ui_root(), "hud_battle", "battle_orders", "battle_orders_pane")
local bar  = find_uicomponent(pane, "bottom_bar")
local button = UIComponent(bar:CreateComponent("<unique_name>",
                                               "ui/templates/square_medium_button_toggle"))
button:SetDockingPoint(8)              -- bottom-centre
button:SetDockOffset(BUTTON_X, BUTTON_Y)
button:SetState("selected")            -- latched on
button:SetImagePath("ui/<mod>/icon.png", 0)   -- index 0 is the icon slot
button:SetTooltipText("my tooltip text", true, true)  -- literal localised text, no loc file

core:add_listener("<unique_name>_clicked", "ComponentLClickUp",
  function(context) return context.string == "<unique_name>" end,
  function() <toggle> end, true)
```

**To attach an indicator to a specific engine-drawn element, create it as that element's CHILD.**
Children are positioned relative to their parent (`SetDockingPoint` / `SetDockOffset` place them inside
it), so the indicator sits on that icon, travels with it, and the same code repeated per discovered
instance gives one indicator per ability at that ability's own corner — no coordinates to maintain,
which is what makes the pattern generalise past the one ability under test. The shipped precedent for
the calls is AI General's own battle-button extension (in its workshop folder:
`script/pancake_lib/aigeneral_battlemod_button_ext.lua`):

```lua
local badge = UIComponent(ability_button:CreateComponent("my_badge", "ui/templates/square_medium_button"))
badge:SetDockingPoint(2)                 -- corner; confirm the numbering against a run, not the docs
badge:SetDockOffset(-2, -2)
badge:Resize(18, 18)
badge:SetImagePath("ui/<mod>/badge.png", 0)
badge:SetVisible(false)                  -- shown only in the state it marks
```

Two honest caveats: **creating a child is itself a write to an engine-owned parent** — the same class
of write that invalidated the ability button above — so log whether the parent still answers
(and whether the new component persists) after creation, and say that you are testing it rather than
asserting it works; and if the parent does not survive, parent the indicator on the parent's **stable
container** (`button_parent`, `battle_orders_pane`) instead, positioning it from the target's own
coordinates and re-aligning periodically. Ship the badge art inside the pack (`ui/<mod>/badge.png`,
index 0) exactly as the HUD-button recipe does.

**Measured, and this is where the child route stands on an engine-drawn button.** A badge built
exactly this way on the ability dial button was battle-tested: the component was created
(`CreateComponent` returned a usable object), `SetImagePath` was accepted — `GetImagePath(0)` read
our own `ui/<mod>/badge.png` straight back — and `SetVisible(true/false)` reported success on every
press, **and nothing ever appeared on screen**. So on an engine-drawn ability button a child is a
third closed door, next to the image write and the state write: the button does not draw what you
hang inside it. On a stable component the same pattern is fine — AI General repaints unit cards in
shipped builds — so the finding is about the *parent*, not the technique.

Two rules that experiment also produced, both general:

- **Find and remove every other write to the parent before concluding a child never renders.** The
  first two versions of that badge were created correctly and then died within milliseconds: the
  build was *also* writing `SetState` / `SetImagePath` to the parent on every toggle, and each such
  write makes the engine rebuild that button, taking the child — and your reference to both — down
  with it. Strip the other writes first, confirm the child still answers after a toggle, and only
  then judge whether it draws.
- **Prove a mechanism renders before building a feature on it.** One throwaway build whose only job
  is "does this appear on screen at all?" costs less than three feature builds that each end in a
  report of nothing, and the answer is one question to the user.

When the parent is an engine-drawn ability-dial button, treat a child indicator as unavailable and
go straight to the two remaining routes: change the game state the engine draws from
(`unit:disable_special_ability(key, …)`), or keep the toggle behaviour-only and let the log carry
the state.

`find_uicomponent(...)` returns **`false`** (not `nil`) when a component is missing, so test
for both. Creation fails while the battle HUD is not up yet, so retry — but retry from the
**real timer** and from the phase callbacks, never from the model-timer poll, and repaint on
every phase event so a control the timer created first still gets its intended look.

Traps, each of which costs a build-and-battle round:

- **Never leave the control in a `disabled` state.** In
  `square_medium_button_toggle` the states are `active`, `down`, `down_off`, `hover`,
  `inactive`, `selected`, `selected_down`, `selected_down_off`, `selected_hover`,
  `selected_inactive` — and `inactive` / `selected_inactive` carry `disabled="true"`, so a
  control parked there can never be clicked back. Use `selected` for the "on/latched" look
  and `active` for "off/normal"; both stay interactive.
- **Do not resize the bar unless the control is actually clipped.** A single docked button
  fitted at the end of the bar with no resizing at all, so ship the resize **behind a constant
  that defaults to off** and turn it on only when the user reports overlap or clipping.
  Resizing by hand costs twice: it **switches off the engine's own auto-resizing** (the bar
  stops tracking the unit-card panel until you redo the fit), and a `Resize`/`Layout` call
  issued from a timer context is the kind of call that raises — which in this engine takes
  every repeating callback in the battle down with it (see `wh3-mod-authoring.md` § one
  raising callback kills every timer). If it does have to be fitted:
  `bar:SetCanResizeWidth(true)`, `bar:Resize(w, h, false)`, `bar:SetCanResizeWidth(false)`,
  `bar:Layout()`, driven from a callback that compares the card panel's current width against
  the last one it fitted, and resizing only when the target differs or the bar grows every tick.
- **A state change animated over time leaves the old image behind.** The toggle template
  transitions between states over ~200 ms, so the background can change while the icon keeps
  the previous image — the user sees the perimeter light up with a stale glyph still in it
  (the reported symptom: "only the perimeter was highlighted, not the thunderbolt"). Apply the
  state **and** the image twice: immediately, and again once the transition has finished.
  Schedule the second pass with **`bm:real_callback(function() … end, 260, "<name>_repaint")`**
  (inside `pcall`) — `bm:callback` is a model-clock call and the repaint will not stick. Do not
  add a second repeating timer for this.
- **Position and size are the parts you cannot verify.** Put the offset in a named constant
  (`BUTTON_X` / `BUTTON_Y`) at the top of the file and tell the user it is a one-line change;
  then ask them whether the control appeared **and where on screen**, which is a fact no log
  can carry.
- **Ship the icon inside the pack** under `ui/<mod>/…png` — the templates' default image is a
  vendor placeholder (a movement-speed glyph, not a blank), so an unsupplied icon looks like a
  wrong-but-plausible control rather than an unfinished one. Ship two variants when the
  control is a switch and swap them with `SetImagePath` alongside `SetState`. The placeholder
  *still* being on screen after you called `SetImagePath` means the call did not take effect —
  check the clock before touching the path, the path name or the image itself.
- **Guard the cosmetic calls in `pcall`.** Their optional-argument semantics are not
  documented tightly enough to assume, and a failed tooltip must not take the button with it.
- **Register a diagnostic twin of the click filter** that logs any `ComponentLClickUp` whose
  `context.string` is not yours but resembles it. If the filter string is wrong the symptom is
  a control that renders and does nothing, and the diagnostic is what names the component to
  filter on instead of spending another battle guessing.
- **Log what the control reports about itself — an image path, not a state.** `CurrentState()` on a
  script-created component returned a **function** rather than a state name, so it proves nothing;
  `uic:GetImagePath(0)` returned the real value. Log, per paint: the outcome of **each**
  `SetImagePath` with the engine's error text (a bare `pcall` swallows it, and that text is the
  difference between "the engine refused the image" and "the engine accepted it and then drew
  something else"), how many states you walked, and `GetImagePath(0)` afterwards. One line per
  paint, not per tick.
- **Paint image 0 in every state, not just the current one.** Each state of a template component
  carries its **own** image list, so repainting whichever state happens to be current can leave the
  vendor placeholder showing the moment anything changes that state — walk `NumStates()` /
  `GetStateByIndex(i)`, set the image under each, then finish on the state you actually want.
- **Prefer feedback that needs no text at all.** For "tell the player which state this is in",
  the engine's own pulse highlight is the cheapest option and the only one with nothing to load —
  `uic:StartPulseHighlight(strength)` / `StopPulseHighlight()`, which is what the advice system uses
  to spotlight a HUD button. It is not proven on a component the engine redraws from game state, so
  log the call's outcome and be ready to fall back (see the engine-rendered indicator section).
  Text you supply is the weakest option,
  because it depends on a localisation key resolving: both routes tried here failed in practice
  (your own key → `result=false`; overriding a vanilla key → the vanilla text still won). See the
  engine-rendered indicator section for when that route is still worth a battle.

## The engine-rendered indicator

Three options, cheapest first. **Use the first one that works and stop there.**

1. **Pulse a component the engine already draws** — one call, no asset, no layout, no
   localisation, nothing to resolve: `uic:StartPulseHighlight(strength)` to arm,
   `uic:StopPulseHighlight()` to disarm, on the ability/behaviour button you found anyway. This is
   the advice system's own "look here" effect. **Cheapest, not proven**: it is untested on a
   component the engine redraws from game state (the ability button ignores both an image write and
   a state write — see above), so log the call's outcome, tell the user it is the one thing you
   could not verify, and fall back to option 2 rather than iterating on it for a second battle.
2. **Set the tooltip text from script** — `uic:SetTooltipText(text, text_source, all_states)`, the
   mechanism the engine's own code uses to override a component's tooltip (`lib_core.lua`:
   `uic:SetTooltipText(common.get_localised_string(new_tooltip), new_tooltip, false)`). A component
   whose tooltip comes from a bound layout may ignore it — log the outcome rather than assuming
   either way.
3. **Text the engine draws itself** (the subtitle call below) — the only option that carries a
   *sentence*, and also the only one that can fail for localisation reasons. Treat it as optional.

Two localisation facts decide whether option 3 is possible at all:

- A mod `.loc` file **overriding a vanilla key can lose.** `common.get_localised_string(key)`
  returned the vanilla text after the override was shipped and verified inside the pack; the
  per-topic fragments in `local_en.pack` (`text/db/<topic>__.loc`) are what serve the UI. Prefer
  **new** keys over overriding vendor ones, and settle which text is live by logging
  `common.get_localised_string(key)` in the battle rather than asking the user to read a tooltip.
- The `text_label` / `StateText_…` values inside layouts are **editor tags, not loc keys** — they
  resolve to nothing (queried with RPFM's `GetSourceDataFromLocKey`, which returned null for every
  one tried). You cannot localise a line you add to a layout by shipping a loc row named after its
  label; put the literal text in the layout's `text=` attribute.

When the deliverable is "show the player which state this is in", let the engine draw the
text. It has one blunt advantage over a custom control: a painter call that fails does so
silently, while a lookup that fails can be made to say so.

```lua
-- key, full_key_supplied = true, force = true
bm:show_subtitle("my_mod_auto_on", true, true)
```

- **`force = true` is required** if the indicator must always appear: without it
  `show_subtitle` returns early whenever the player has subtitles switched off.
- **`full_key_supplied = true` skips the vendor table.** With it false the function pads your
  key into `scripted_subtitles_localised_text_<key>` and expects a `scripted_subtitles` row;
  with it true the key goes straight to `common.get_localised_string`, so all the string needs
  is an entry in your own `.loc` file (recipe: `references/rpfm-server-protocol.md`
  § localisation files).
- **Log the return value.** `nil` means the engine accepted and drew it; `false` means it
  rejected the key, which is what a localisation entry that did not load looks like. That one
  line separates "the text is wrong" from "the text never arrived" without another battle.
- **Call it from a UI context.** It creates the subtitles component on first use, so it is
  itself UI work: a click listener or the gated real timer, never the phase dispatch.
- Show it on every state change **and once shortly after the battle starts**, so the player
  sees the initial state without pressing anything.

## Choosing the interaction, when the task is "add a toggle"

| Route | Cost | When it is right |
|---|---|---|
| HUD button (template clone) | Most work up front, no layout file, best discoverability | A player-facing switch that should look like part of the game |
| **A left-click component event on something the engine already draws** (`ComponentLClickUp` on a unit card, an orders-bar button, and similar) | No UI work, no icon in the pack, no clock hazard; the runtime component name must be discovered, and **only left-clicks are delivered** — right-clicks and left-double-clicks never reach script (measured) | When the affordance is already on the player's screen **and** a left-click on it means nothing else. If the click already does something (`is it an order?`), the toggle fights the game |
| **A keyboard shortcut** (`ShortcutTriggered` / `ShortcutPressed`, name in `context.string`) | Small: two listeners and one named key (`usegroup0` … `usegroup9` is the best choice — an empty control group does nothing else), plus a same-tick debounce. No conflict with the mod's own clicks | A switch the player flips while playing — the only player-input family that reliably reaches script in battle, and it works. **Not** a right-click design: that is unwinnable |
| Key press (ESC steal) | Smallest change; consumes a key that also opens the pause menu | A test harness, or when the user already accepts the key trade-off |
| An existing per-unit toggle read via `unit:is_behaviour_active("defend" \| "fire_at_will" \| "skirmish" \| …)` | No UI work and the button's own highlight doubles as the indicator | Only when the hijacked behaviour is irrelevant to the unit — these change real gameplay, and for a melee unit some of them do not exist at all |
| A dummy ability that exists only as a switch | Needs an ability row and an icon | When the click must be a normal ability-bar button |
| Reacting to the player's own use of the ability (`Special Ability` command event) | No UI at all; muddles "use it" with "toggle me" | A "manual override" design, where acting by hand is meant to disarm the automation |
| Data-layer route (see `wh3-mod-authoring.md`) | A database edit; if the unit's own ability can be switched off at runtime the toggle becomes a single call — **unverified, test it first** | When the ability itself is the switch, rather than the script's behaviour |

## Placing a created element: the ranked routes, and how this community does it

**There is no formula, and nobody computes these numbers.** The wiki's own positioning tutorial
(`Tutorial:Pooled Resource Unit Costs`, the canonical one) instructs the reader to test
`SetDockOffset(x, y)` *"until the new UIC looks like it's in the right place"* — from a live in-game
console (**Groove's Modding Dev Tools**, `shift + F3`). AI General, the one shipped mod that puts an
element on the battle HUD, carries the same admission in its source: the padding constant it derives
its offset from is annotated `-- this is just a guess for now`. Plan for tuning, not for arithmetic.

Ranked routes, best first:

| # | Route | Evidence / cost |
|---|---|---|
| 1 | **Live console tuning** — expose the knobs as one function in the mod (`zz_badge_set(x, y)`) and let the user dial them while watching (full recipe below) | Community-standard, and the fastest route to a perfect placement; needs a console mod the user must subscribe to (ask — this user offers). Also tunes values you cannot guess: size, corner, offset |
| 2 | **Author the position in a layout** — ship a layout with the element declared *inside* the target component's definition, docking/offsets written in XML, then `SetVisible` it from script | Best-evidenced *untried* route: the ability button's own definition already contains a layout-declared child (`auto_trigger_icon`), so declared children are drawn where a script-created one was never drawn; exactness by construction. Cost: shipping a replacement for a vanilla UI file — built by *copying* vanilla, never authored (§ shipping a layout: copy, do not author) |
| 3 | **One-shot shipped config + report-driven nudges** — one placement (parent, `SetDockingPoint(8)`, one offset, one parent `Layout()`), the offsets as named constants, tuned from what the user reports seeing | Works today; each nudge costs one build and one battle. The fallback when no console is available |
| 4 | `CopyComponent` of a neighbouring vanilla element | Useful for *look*, no placement advantage |
| 5 | No element — behaviour and the log only | Always acceptable; state that the toggle is confirmed and the badge is cosmetic |

Whatever route: place **once** — a correction loop steers by `Position()`, which was measured
reporting a frozen value while the offset climbed past 4000 — keep two named numbers as the only
knobs, and ask the user where the element **landed** rather than reading its coordinates back.

### The live-console workflow in full (route 1, and what it takes to make it stick)

What actually shipped: create the element on a **stable plain container** (the HUD root, or any
parent that does not run a LayoutEngine), keep the two numbers as the only knobs, and let the user
dial them live. Each moving part below cost a round when it was missing.

1. **Expose the knobs as GLOBAL functions** in the mod (`function zz_badge_set(x, y) … end`). A
   closure over the mod's locals is the point: the live console reaches globals only, and the
   locals hold the component handle, the offsets and the mode flag.
2. **Log every result as well as returning it.** The dev-tools console's entry box does **not**
   display a return value — the user sees an empty console and reports that the command shows
   nothing — so `log()` the same string you return. The log then carries the numbers to bake in
   later, and the return value serves any console that does echo.
3. **Tune in absolute mode first** (tracking off): the user nudges one small step per axis until the
   element sits where they want it, and tells you which axis moved the way they did not expect.
4. **Do not build the follow on a derived delta — measured, it does not place the element where you
tuned it.** Converting the tuned spot into `delta = tuned − target:Position()` produced a badge that sat
"nowhere near the ability icon" on the very next build (the user's screenshot showed it up in the middle
of the field), because the position you *read* and the offset you *write* are not one frame of reference.
Ship the **fixed offset against the parent's own anchor** — the number pair the user tuned — and let
**visibility**, not position, do the following (see "The indicator follows the state, not the element"
below). This is also the convention to read their nudges back in: **minus is left and up, plus is right
and down**, measured from the parent's dock point.
5. **Make the convert step idempotent and reversible.** A converter that re-applies itself on each
   call walks the number off the screen — measured: repeated calls produced `−1995 → −3125 →
   −4255` (each subtracting the target's position again) while the badge left the screen. Guard on
   the current mode (`already tracking → report and return`) and, switching the other way, apply
   the **inverse** conversion (delta → absolute = add the position back) so the user can alternate
   between eyeballing and tracking without losing the spot.
6. **Bake the tuned numbers in as the shipped default, as a fixed placement**, so the next battle
   needs no console — and read them out of the log rather than asking the user to transcribe them.

The same shape tunes anything the log can measure and the user can see: size, corner, icon choice.
Ask for the console mod (`Modding Development Tools`, `shift + F3`) when this route is chosen — this
user subscribes on request — and say that arbitrary code typed there runs inside the live battle, so
they should type only the mod's own `zz_*` functions.

### The indicator follows the state, not the element

An indicator that must sit "on the ability icon, for the right unit" has two separate jobs, and
conflating them is what produced a dot that stayed on screen after the player selected a different
unit:

- **Position** — fixed, in the parent's frame: the one number pair the user tuned. Never recompute it
  from another component's coordinates (the derived-delta failure above).
- **Visibility** — bound to what the target is *showing* right now, not to whether the component exists
  or is visible. A dial is rebuilt per selection, so the button can be perfectly `VisibleFromRoot()`
  while showing **another unit's** ability. Ask it, every tick:

```lua
local ok, key = pcall(function() return our_button:InterfaceFunction("AbilityKeyForScript") end)
local copy = ok and as_plain_string(key)   -- pcall'd copy; NEVER string.find (the 4-arg plain form kills the engine)
if copy == nil or not is_one_of_listed_keys(string.lower(copy)) then
  our_button = nil          -- drop the handle: the discovery rescan will re-find the button
  hide_badge()
end
```

Dropping the handle is the other half: the discovery scan early-returns while a handle is held, so
clearing it is what lets the button be re-found — and the indicator re-shown — when the ability
returns. Visibility is not identity.

**Selection goes stale when it listens only to unit-card clicks.** In battle the player usually selects units by clicking them in the world, which fires no component click at all, so the mod keeps acting on the last card-clicked unit while the dial on screen belongs to another - the reported shape is "clicking one unit's badge changed the other unit". Read the click-context line first (`click: <marker> badge -> selected unit <ui_id> ('<type>') armed was <ON/OFF>`, logged immediately before every toggle): it names the unit the mod believes it is acting on. **Resolved, measured: the selected card's `CurrentState()` reads `'selected'` while every other card reads `'active'`** (a card's `Id()` equals its unit's `unique_ui_id()`; cards resolve via `Find("card_panel_docker")` → `Find("cards_panel")`, sweep capped at ~12 cards, every read pcall'd). Drive selection from that, not from clicks: poll once a second and adopt the single `'selected'` card — the sweep's value **overrides** the card-click fast-path, logging `selection updated from card states: <old> -> <new>` — keep the current tracker when several cards report selected and it is among them (else take the first), and keep it with a note when no card can be read (`no card reports selected - tracker stays <id>`). After this fix the click-context line reads `click: onslaught badge -> selected unit 1002 ('captain')` with zero toggles for the stale unit.

**Visibility has exactly ONE owner: the per-tick recompute of "is this marker claimed on the current dial".** A helper that unconditionally calls `SetVisible(true)` as a side effect - the letter-update path, which runs on every card click and toggle - re-shows a STALE badge on the next unit's dial: a ghost for an ability that unit does not even have. And a ghost still takes clicks (measured: a click on a hidden badge toggled an ability for the wrong unit), so ghosts must also be inert: ignore any click whose marker is not currently claimed (`click ignored: <marker> is not on this unit's dial`). Give every other path - letters, toggles, console show/hide hooks - bookkeeping only; apply visibility in the tick; log one line per transition (`badge <marker>: hidden (marker not claimed on this dial)`).

### State displays, measured: text first, colour pair second — why opacity is not a look

**Order of preference:** one component whose **text** carries the state — `SetText("A")` armed /
`SetText("M")` manual — is the only state display in this project that never failed (user-confirmed
rendering and toggling); reach for it first. The colour pair below is the fallback when a genuine
colour difference is required.

```lua
-- one badge per ability, from the shipped text layout
-- one pair per ability: cream A = armed, grey A = not, exactly one visible
local on  = UIComponent(parent:CreateComponent("zz_auto_" .. marker .. "_on",  "ui/templates/zz_auto_badge"))
local off = UIComponent(parent:CreateComponent("zz_auto_" .. marker .. "_off", "ui/templates/zz_auto_badge_off"))
on:SetText("A"); off:SetText("A")      -- the colour lives in each layout copy, not in a call
on:SetVisible(armed); off:SetVisible(not armed)   -- SetVisible is the look switch; never both
```

- **Fractional opacity is not a dim look — it is an invisible one.** Measured in game: with
  `SetOpacity(0.45)` on the idle badge the engine reported `Opacity()` as `0`, so that state never
  drew and the player saw no badge at all (only the armed one, opacity 1, ever appeared). Do not
  build a "disabled = dimmed" look on opacity.
- **The colour surface, measured off the method table:** `SetOpacity`, `Opacity`,
  `PropagateOpacity`, `SetCurrentStateImageOpacity` / `GetCurrentStateImageOpacity` exist;
  `SetText` / `GetText` exist; there is **no** `SetTextColour`. So two looks = two layout copies
  differing in exactly one colour value, switched by `SetVisible`; a true runtime recolour would
  need `TextShaderTechniqueSet` / `TextShaderVarsSet` (present, unexplored).
- **Never two visible at once.** The trap is not the pair; it is drawing both. Measured: a
  battle-tested pair at one offset showed only the top member, and the click went to whichever sat
  on top — clicking the Deadly Onslaught badge toggled Foe-Seeker. Switch by `SetVisible` so exactly
  one exists on screen per state, and make the click accept **either** id
  (`zz_auto_<marker>_on` / `_off`, suffix stripped to the marker): the player clicks the unarmed
  look to arm it.
- **Both layouts must ship.** The grey twin only draws because the build's file list carries it; a
  file dropped from that list leaves the pack silently and the missing look fails as nothing at all.
- **Per-ability offsets:** each ability carries its own `ox`/`oy` in the abilities table, tuned with
  the marker-taking console hooks (see the generalising rule in SKILL.md). One shared constant puts
  every ability's element on the same spot.
- **Refresh the letter from the tracked selection — on change AND on a cached tick.** Bind the display
  to the same selection the firing logic uses, or the letter belongs to whichever unit last re-ran the
  update path: measured, the badge kept the previous unit's letter after a re-select and only corrected
  when an unrelated event (giving an order) nudged the refresh — reported as the letter "snapping" to
  the right value. Refresh both badges the moment `selected_unit_id` changes (log
  `selection changed to <ui_id> - refreshing badge letters`), plus a per-tick pass that writes only when
  the desired letter differs from the last one written (cache it). Count `SetText` in the harness as the
  proof it does not spin: measured 4 writes for a whole arm-and-reselect scenario, and 0 from ten
  seconds of ticking and sweeping.

### The latency budget

A control the player operates is judged by how fast it answers, and the callback interval is not the
brake. Measured: the badge logic ran on a 500 ms real callback and the *rescan* only every 4th tick, so
a unit switch waited up to ~600 ms and came back reported as lag. Dropping the callback to 50 ms and
the rescan to every 2nd tick (~100 ms) removed most of it. Rules: real callbacks at 50 ms are cheap
(keep the per-tick body to a few calls); whatever you gate on `ui_ticks % N` **multiplies** the
interval, so fix the cadence of the slow step before shrinking the tick further; and name which part
of what remains is the engine's own redraw — that part is the floor and cannot be scripted away.

### Artwork at HUD scale

A created element's picture is drawn into whatever rectangle its template gives it, so the **frame**
dominates what the player sees, not the pixel grid of the PNG. Two measured consequences:

- A hand-rasterised glyph is a dead end for letterforms: thick strokes fused into a solid triangle at
  ~24 px, and a 4×-supersampled, thin-stroked redraw the user still called "horrible". Hand-draw only
  simple shapes (a status dot; `scripts/make_png.py` writes an RGBA PNG from a drawing function with
  the stdlib alone) and take letters straight to an engine-drawn `text` component in a layout you ship.
- `Resize` on a created component did not beat the template — the user still called the element "too
  big". Exact size is a layout you ship, not a call.

### Shipping a layout: copy, do not author

When exact size or crisp text means shipping a `.twui.xml`, the file must be a **copy of a real
vanilla template with one value changed** — never a layout written from scratch.

Why, measured: a hand-authored layout (structure assembled from the wiki's page set, GUIDs invented
to match the shape) shipped under `ui/templates/` came back as **"the game crashes at startup"** —
before any battle loaded, with the runtime log completely empty, and with no other new load-time
artifact in that build. The engine reads the template set while the game starts, so a bad template
takes the whole game down rather than the one battle that would have used it. That is also the
diagnostic: **when the game dies at startup, bisect on what the engine parses at load** — your
shipped layouts first, then the mod script — and confirm the rebuilt pack's file list no longer
carries the suspect file; the pack container listing is the checklist, and a fix that "should" be
gone is not evidence.

The copy route:

1. **Pick the template that already IS what you want.** The extracted set is
   `data/ui3.pack` → `ui/templates/*.twui.xml`. Score candidates in Python: count the components in
   `<hierarchy>` (one component = no leftover furniture) and read the `component_text` element.
   `parchment_divider_title.twui.xml` won for a bare letter — 3.9 KB, exactly one component, no
   images, and this text element:
   `<component_text textvalign="Center" texthalign="Center" font_m_font_name="brand_header"
   font_m_size="16" font_m_colour="#FFF8D7FF" font_m_leading="3" fontcat_name="header_16"/>`
2. **Check what it draws before shipping it as "just text" — and expect it to draw something.**
   Scan for `<componentimages>` and `imagepath="…"` (the attribute images actually use — `file="…"`
   matches nothing and returns a false all-clear). Measured: **no template carrying a `component_text`
   is art-free** — every one in `ui/templates/` also carries `<componentimages>`, and this copy declares
   three pictures (`parchment_divider_title{,_top,_bottom}.png` — a panel, a divider line and a
   wax-seal ornament) which all render with it; the user reported exactly those as "a rectangular
   block", "an underscore" and "a drop of blood with a + inside icon". The copy route gets you a
   *valid* file, never a *bare* one: count the `<image>` declarations in the state you will show before
   promising the look.
   **To strip the art, edit declarations rather than paths.** Repointing every `imagepath` at a shipped
   transparent PNG was measured **insufficient** — the artifacts still drew (a blank texture stretched
   into a small slot reads as a pale bar). The lever that works, **battle-confirmed**: delete the
   `<image …/>` declarations from that state's `<imagemetrics>` so nothing is left to draw but the
   text, every other byte identical — the panel, the divider line and the wax-seal ornament all stopped
   drawing and the letter stood alone on screen.
3. **Change exactly one value** — typically the colour: `font_m_colour="#FFF8D7FF"` →
   `"#CD7F32FF"` for bronze. Assert the replacement count is 1, keep every GUID, id and attribute
   otherwise byte-identical, and write it under **your own** name
   (`ui/templates/zz_auto_badge.twui.xml`) so no vanilla file is replaced. Note the file holds **more
   than one colour attribute** — the text's `font_m_colour` and a `colour` on the component/state (and
   on the root's own image) — and measured, the *rendered* letter tracked the `colour` attribute while
   a `font_m_colour` edit changed nothing on screen: change one, then confirm against the user's
   screenshot before changing the other.
4. **Know the API's shape:** `uic:SetText(s)` / `GetText()` exist; there is **no** `SetTextColour` —
   colour, font and size live in the file. `fontcat_name` pairs with the size (`header_16` ↔
   `font_m_size="16"`, `body_12` ↔ 12), so a resize later changes both.
5. **Create it extensionless:** `CreateComponent("zz_auto_badge", "ui/templates/zz_auto_badge")`,
   the form the working recipes use (the engine resolves the area folder, then `ui/templates/`). A
   `Resize` is usually still needed: the vanilla component is sized for its own original use, not
   yours.
6. **Log the read-back**: `SetText("A")` then `GetText()` — the same store-vs-draw check as every
   other write, and what separates "the layout never loaded" from "the text is wrong".

State which half is proven when you hand it over: the file's **validity** is structural (a
byte-identical copy of something the engine already loads cannot trip the parser), while the created
component's **appearance and placement** still need one battle from the user.

## Verifying a UI feature without the game

Extend the mock harness with the UI surface: stand-ins for `core:get_ui_root()`,
`find_uicomponent(...)` (return `false` for the not-found case, matching the real helper's
return value), `UIComponent(x)` (pass through), a component object recording every
`CreateComponent` / `SetState` / `SetImagePath` / `SetDockingPoint` / `SetDockOffset` /
`Resize` / `Layout` call **and answering `CurrentState()`**, both timer registrations
(`repeat_callback` and `repeat_real_callback` are different entry points — capture them
separately so the test can prove which clock the UI work is on), and `core:add_listener`
**capturing the listeners** so the test can invoke a filter and its callback with a fake
`{string = "<component name>"}` context.

Then assert, in order: **the code path under test actually ran** — the log contains the creation
and paint lines, not merely "nothing raised" (a stand-in returning nothing for an intermediate
level of the lookup chain skips the whole path in silence while the harness still passes, which is
how a never-executed paint path survives several rounds of "mock-verified" builds); the creation
calls carry the intended name, template and icon; the click flips the state and swaps icon and
tooltip; **the model-timer poll makes zero UI calls** (the regression guard for the clock rule);
**no timer-registry call happens after load** — assert zero `remove_callback` and zero further
`repeat_callback` calls, which is the guard for the repair rule; the action is
**suppressed** for a window longer than the rate guard (otherwise the guard, not the switch,
explains the silence); and switching back resumes it. A switch that is only ever tested in
its "on" direction is not tested. The mock cannot prove rendering, placement or click
delivery — say so, and ask the user for those.

## Pitfalls

- Designing a hotkey on `register_input_handler_callback` — it carries camera inputs only.
- Parking a clickable control in a `disabled` template state; it can never be re-enabled.
- Doing UI work on the model clock (the poll, or `bm:callback`): the call silently no-ops,
  the control keeps the template's placeholder, and the model timer may stop running
  afterwards — which then reads as the trigger having broken rather than as a styling bug.
- Resizing the HUD bar once and assuming the engine keeps it fitted afterwards; the resize
  disables that very behaviour.
- Reporting a control as working because the creation calls returned without error. Rendering,
  placement and click delivery are only observable on the user's screen — ask, and give them
  the constant to tweak.
- Redesigning a control's look a second time from a screenshot alone. Ask for the log line that
  reports the state the component accepted first; without it, "wrong state names" and "calls
  not sticking" are indistinguishable and you will rebuild the wrong half.
- **"Repairing" a timer by re-registering it.** A remove-then-add around a raise deletes the
  timer and replaces it with nothing, and re-registration is inert once the engine-side driver is
  lost — so the log fills with successful re-arms while the feature stays dead. Register once,
  watch and report, and treat "the re-arm succeeded" as no evidence at all.
- **Doing UI work in a phase callback and leaving it there.** The appearance lands — and the
  battle's model timer can die with it, so the feature you already had working comes back reported
  as broken and the paint looks like the thing that fixed itself. Keep creating and painting in the
  phase callback (it is the context that paints), watch the poll from a real timer so the silence is
  *reported*, and do not touch the registry; see the clock rule above.
- **Building a control for an input the engine already reports.** Enumerate `events.lua` **and the
  layout declarations** before drawing anything; the listening route has none of the clock, paint
  or resize hazards above, and rounds spent repainting an icon the mod never needed to draw are the
  user's battles.
- **Hard-coding a component name for an engine-instantiated element.** Log every distinct name the
  event fires on, once each, and match loosely — a name guessed wrong is a silent no-op that looks
  exactly like a broken listener, and the log line that would name it is the thing you skipped.
- **Perfection on a cosmetic detail while the feature itself works.** Report both plainly:
  what is confirmed working, what is cosmetic and still wrong, and what you would rather do
  instead. A user who has run four battles for an icon is owed the option to drop it.
