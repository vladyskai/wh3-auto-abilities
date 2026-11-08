# WH3 battle-script modding: HUD and input lessons (all measured in-game)

## Input channels in battle
- **A right-click cannot be detected.** `ComponentRClickUp` is declared in `script/events.lua` but the
  engine never raises it: zero events across every session, even with `AddScriptEventReporter()` on the
  component and its whole ancestor chain, with unfiltered listeners, and with all 399 event names
  subscribed. Left-clicks (`ComponentLClickUp`) *are* delivered for HUD components, but a left-click on
  an ability icon already means "use the ability".
- `AddScriptEventReporter()` (see UI:Main Page) makes a component fire *all* its events; it cannot
  conjure events the engine never sends. Components only fire `ComponentLClickUp` by default.
- **Keyboard works** via `ShortcutTriggered` / `ShortcutPressed`, carrying the shortcut name
  (`step_r`, `cam_up`, `toggle_pause`, `usegroup8`, ...). Number keys arrive as `usegroup0`-`usegroup9`,
  so an unused control-group slot is a clean deliberate toggle. Every press arrives **twice** - debounce
  repeats inside one poll tick.
- **Do not build a UI-to-script channel on component properties.** Reading a component's declared
  property from script returns the property *name*, not its value (measured, including for a property
  vanilla declares with a value). Layout callbacks can therefore not pass state to script that way.

## Engine-owned components (the ability dial button)
- `button_order1` (under `sa_dial` > `button_parent`) is engine-owned. `SetState`, `SetImagePath` and
  `CreateComponent` on it make the engine rebuild it; afterwards the script's reference is dead (reads
  return function pointers / `0`) and re-acquiring by id fails. Never write to such components - keep
  state in script.
- Its icon cannot be repainted: image-slot writes read back correctly but are never drawn, and children
  created on it are not rendered.
- The only way to change an ability icon's look is to let the *game* do it:
  `unit:disable_special_ability(key, true)` puts it into the engine's unavailable (dimmed) state - at the
  cost of blocking manual use as well.
- Badge/visibility tying: test *which ability a dial button is showing* (`InterfaceFunction("AbilityKeyForScript")`)
  each tick, not `VisibleFromRoot` - the dial is rebuilt for whichever unit is selected.

## Placing a HUD element of your own
- Create from a layout: `parent:CreateComponent(name, "ui/templates/x")` (no extension - the working
  form) or `core:get_or_create_component(name, path, parent)`; ship the layout in the pack.
- Parents with a **LayoutEngine** (e.g. `battle_orders`) arrange their children and ignore
  `SetDockOffset`; prefer a plain container such as `hud_battle`.
- `Position()` on a *created* component misreports (measured: reported a fixed point while the component
  sat elsewhere), so error-correcting loops cannot converge. **Hand-tune instead:** dock point 8 =
  bottom-centre (AI General's choice), offsets in the parent's space, minus = left/up, plus = right/down.
- Community practice is a live Lua console (Modding Development Tools, shift+F3) plus `SetDockOffset(x, y)`
  until it looks right - the wiki's own placement tutorial says exactly that. Ship `zz_*` global functions
  so the player can nudge values live, and **log every value**: the console entry box does not echo
  return values. Make calibrate steps idempotent (repeated conversion compounds the numbers).
- **Text and colour come from the layout, not script:** a `component_text` node with `font_m_font_name`,
  `font_m_size`, `font_m_colour="#RRGGBBAA"`, `fontcat_name`; set the string with `SetText`. There is no
  `SetTextColour`. Hand-rasterising glyphs into PNGs looks bad at HUD sizes - use the font.

## Test protocol that worked
One battle per hypothesis, the log naming every branch, plus a **control case** (a gesture that certainly
happens) so silence is interpretable instead of ambiguous.
