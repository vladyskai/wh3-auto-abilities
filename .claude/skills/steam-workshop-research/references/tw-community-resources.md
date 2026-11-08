# Total War modding: where to look before you reverse-engineer anything

Ordered by value. None of this replaces reading the engine's own files — it tells you
*which* files to read, and often answers the question outright.

## 1. Generated API + CA's own callback documentation

`chadvandy.github.io/tw_modding_resources/WH3/` — script API by area (battle / campaign /
frontend). The prize is **`ui_callback_documentation.html` (~197k chars)**: CA's own
description of every UI/CCO callback, its area, and its user properties. It is what you
want for any question of the form "how do I make a UI component do X". Read it in a real
browser — the markdown extractor returns a stub. Entries are laid out as
`name <X> area <Y> doc <description> user_properties ...`, so search the rendered text for
the callback name and read forward ~1.5k chars.

Worked example — the answer that five rounds of inference missed:

> **ContextEventBroadcaster** — "On action specified by user property broadcasts the event
> specified (lclick, rclick, mouseon, mouseoff). Can use to notify other callbacks that
> listen to UI_UPDATE_MSG events such as ContextAnimationTrigger and ContextComponentInitialiser…"
> user properties: `rclick` — "mouseon, mouseoff, lclick, rclick, onkey - these are user
> properties you use to set when to broadcast. The value is the event name you want to broadcast."

**The `AddScriptEventReporter` entry on that page is the trap — the wiki's own UI tutorial
contradicts it, and the tutorial is right.** `UI:Main Page`: components fire only *some* events by
default (`ComponentLClickUp` for most), and `uic:AddScriptEventReporter()` makes one fire **all** of
them — vanilla uses it for exactly that in `_lib/lib_movie_overlay.lua` ("set the panel to report
all script events") before listening for `ComponentAnimationFinished`. Reading the callback-doc
snippet as "never clicks" costs several rounds of chasing the wrong thing. What the reporter does
*not* do is conjure events the engine never raises: right-click and left-double-click component
events are absent in battle even with it on the component and its whole ancestor chain (measured;
`wh3-battle-ui-and-input.md`).

Also on that site, per area: `scripted_events.html` (the event list, with examples) and the
`uicomponent` page (every method, incl. `StartPulseHighlight` / `StopPulseHighlight`, which is
how the advice system spotlights an existing HUD element — free engine-rendered feedback).

## 2. The engine's own files (after step 1)

- **UI layouts are stored UNCOMPRESSED inside `ui3.pack`** (~907 `.twui.xml`, 103 MB), so they
  can be read with a plain byte scan and extracted without decoding: a pattern search for
  `name="lclick"` / `name="rclick"` / `ContextEventBroadcaster` works directly on the pack.
  This is how you prove what a component can respond to rather than guessing.
- **Where a component lives**: search the engine's scripts for the component path the game
  itself uses (`grep -rn` the vanilla script tree for the id, e.g. `behaviour_parent`), then read
  the layout. The game's own highlight/advice code names the real hierarchy and, better, shows
  the query that identifies a component's meaning (`InterfaceFunction("AbilityKeyForScript")` on
  a unit-ability button).
- **A script-side stub dump of the API** (`battle.lua`, `battle_manager.lua`, `uicomponent.lua`) is
  worth more than forums for signatures: `battle:register_input_handler` lists its *complete* valid
  input list (camera movement only, in WH3) in its own doc comment.

## 3. Community wiki — `tw-modding.com`

Search index broken (returns 0 hits for everything — enumerate instead), and the site is larger than
it looks: **~436 pages**, of which only **37** are in the main namespace. `list=allpages` returns
namespace 0 by default, so the tutorials hide in the `UI:` (4 pages), `Lua:` (13), `Tutorial:` (33)
and `Battle Maps:` (4) namespaces — and the answer to a UI question lives in `UI:Main Page`, not in
the main-namespace pages. Dump the whole wiki once and grep it locally. The API sits at the site
root (`/api.php`; `/wiki/api.php` answers "No such action" and `/w/api.php` is a 404):

```bash
curl -s "https://tw-modding.com/api.php?action=query&meta=siteinfo&siprop=namespaces&format=json"
curl -s "https://tw-modding.com/api.php?action=query&list=allpages&apnamespace=<ns id>&aplimit=500&format=json"
# per page: ?action=parse&page=<title>&prop=wikitext&format=json — save each to a file, then grep
```

Good for: `UI:Main Page` (the UI scripting tutorial series — event reporters, `SetImagePath`,
`find_uicomponent`, `CreateComponent` / `CopyComponent`, the button pattern),
`UI:Build-a-Button Workshop` (the canonical `ComponentLClickUp` button recipe),
`Tutorial:Component Context Objects (CCOs)`, `Tutorial:Context Viewer (Warhammer 3)`,
`TWUI.XML Layout Files`, `Lua/Commands, Interfaces & Listeners`, `Lua/First Script`, `Troubleshooting`.

`Troubleshooting` is the authority on **load order**, and it is not what people assume:

| folder | ordered by |
|---|---|
| Db | table name |
| Scripts | **pack file name** |
| Text | table name |
| UI | **pack file name** |
| Variants | pack file name |
| Startpos | pack file name |

Load order is alphabetical (`!` < digits < `a-z`), so a pack named `zz_…` beats vanilla `ui3.pack`
for UI and script content. Practical consequence for a test mod: name it `zz_*` and it overrides
what you are testing without touching the mod manager.

**Placement is hand-tuned, and this wiki says so.** `Tutorial:Pooled Resource Unit Costs` is the
positioning reference: create the UIC, then test `SetDockOffset(x, y)` *"until the new UIC looks like
it's in the right place"* — from the live console in **Groove's Modding Dev Tools** (`shift + F3`).
That console is the tool to ask the user for when a created element has to be placed exactly; with it
the tuning loop takes seconds instead of a build-and-battle round each.

## 4. Da Modding Den (`discord.com/invite/moddingden`, ~20k members)

The place to ask. The wiki above was born out of it, and its advanced channels are cited as the
source of the CCO tutorial. Post with the evidence, not the question: quote the event-table line,
say what a catch-all listener logged, and include the layout fragment you found. Fastest for
"has anyone ever…" questions that no document answers.

## 5. Total War Center (`twcenter.net/forums/db-editing-scripting.2198/`)

Veteran forum, per-title subforums. Lower traffic than the Discord, but searchable and archived —
good for old Total War titles where the Discord has moved on. CA's own forums (Modding Corner) are
low-traffic by comparison.

## 6. Tooling notes that save time

- **Do not spend turns on RPFM's `GlobalSearch`.** Against a v5.0.6 server it rejects the
  documented payload with a chain of `missing field` errors (`anim`, then `matches`) even when
  every field of both `SearchOn` and `Matches` is supplied exactly as `master` defines them and
  the command really is `GlobalSearch(String, GlobalSearch)`. The struct definitions and the
  error message are simply inconsistent; treat it as unusable rather than diagnosing it.
- **What to do instead — and it is faster anyway:** `GetPackFileDataForTreeView` to list the
  packed paths, filter them in Python, then `ExtractPackedFiles` in batches of ~200. One call set
  pulled all **952** UI layouts out of `ui3.pack` (~103 MB) with no trouble, after which every
  question about layout contents is a local `grep`. `rpfm_probe.py` wraps all three commands
  (`find` / `extract` / `search`).
- **Rust-side ground truth** when a command's JSON shape is unclear: the IPC structs live in
  `rpfm_ipc/src/messages.rs` and `rpfm_extensions/src/search/mod.rs`, keyless to fetch from
  raw.githubusercontent.com. Cheaper than guessing field names.
- **Read a vanilla loc key before overriding it**: decode the game's own `.loc` fragment
  (`text/db/<topic>__.loc` in `local_en.pack`, one file per topic — decode candidates and search)
  and take the real string, then ship vanilla text + your addition. Never ship a guess at what you
  are replacing.
- **Verify an override from inside the game**: `common.get_localised_string(key)` returns whatever
  text is live, so one log line proves whether a loc override won — no need to ask the user to read
  a tooltip.
