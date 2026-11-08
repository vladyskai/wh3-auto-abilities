---
name: steam-workshop-research
description: "Use when researching or building game mods: inventory, upkeep, feasibility, engine-side authoring."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Steam, Workshop, Mods, Gaming, Research, Maintenance]
    category: research
    related_skills: [grounded-citations, blocked-page-recovery]
---

# Steam Workshop research

Answers the request shape "list the mods for <game> that do <thing>, and tell me if they
are still maintained." The trap is that Workshop search relevance ranking, unresolvable
relative dates, and near-miss mods make a shallow pass look complete when it is not.
Two tool layers fix that: the **browser** for discovery (Workshop tiles are
JS-lazy-loaded), and the **keyless Steam API** for authoritative timestamps.

## When to Use

- Enumerating mods for a game (any appid) matching a functional description
- Judging whether mods are abandoned, patch-compatible, or superseded
- Comparing a mod against its own forks/submods/predecessors
- Any "check if X is still being updated" question about Workshop items
- A follow-up of the form "is it possible to create such a mod?" — see step 6, which
  answers from the engine's own data tables and scripting API rather than from whether
  somebody has already shipped it
- A further follow-up asking to build it: a one-ability test case, the engine-side
  script, verification, or help with the packaging step — see step 8 and `templates/`
- A further follow-up asking for something the player operates in battle (a toggle, a
  button, a key, a reaction to a click): see step 9 and
  `references/wh3-battle-ui-and-input.md`

## Procedure

### 1. Fix the two anchors before searching

- **appid** — from the game's store URL (`store.steampowered.com/app/<appid>/`).
  Total War: WARHAMMER III = `1142710`.
- **Current patch version and date** — from the developer's own release notes
  (Total War: `community.creative-assembly.com/total-war/.../blogs`). Every
  maintenance claim is relative to this date; capture it first or the verdict is
  guesswork.

### 2. Sweep search terms in the browser away from one query

```
https://steamcommunity.com/workshop/browse/?appid=<APPID>&searchtext=<q>
  &browsesort=textsearch&section=readytouseitems&actualsort=textsearch&p=1
```

- Text extractors return only the page header/chrome on Workshop browse pages —
  the result tiles are loaded by JS. Drive the browser, scroll 4-6 times with
  ~1.2s pauses so tiles mount, then harvest anchors rather than CSS classes
  (class names are obfuscated and rotate):

```js
JSON.stringify([...new Set([...document.querySelectorAll('a[href*="filedetails"]')]
  .map(a => (a.textContent||'').trim() + ' ||| ' + a.getAttribute('href'))
  .filter(s => s.length > 10))])
```

- **One query is not coverage.** Each search yields ~30 results sorted by
  relevance. Sweep 20-30 phrasings covering the *mechanism* from several angles
  (e.g. `auto cast`, `automatic abilities`, `make abilities passive`,
  `no micro`, `toggle abilities`), then dedupe the numeric ids in Python and
  report the count. Duplicated stops across queries are how you know you have
  saturated rather than sampled.
- **Sweep in the user's other languages too.** Mod titles in Russian/Chinese/etc.
  surface items English queries never return; translate the mechanism, not the
  title (e.g. `自动施法`, `авто способности`).
- Pace page loads (~2-3s) and prefer the API for bulk metadata — Steam answers
  repeated hits with "You've made too many requests recently".

### 3. Stamp every candidate with the keyless API

`ISteamRemoteStorage/GetPublishedFileDetails` needs **no API key** and returns
`title`, `time_created`, `time_updated`, `subscriptions`, `visibility`, `banned`:

```bash
curl -s -X POST "https://api.steampowered.com/ISteamRemoteStorage/GetPublishedFileDetails/v1/" \
  -d itemcount=2 -d 'publishedfileids[0]=3009989710' -d 'publishedfileids[1]=3290510918'
```

Use `scripts/stamp_mods.py <id> [<id> ...]` to do this and print a table sorted by
last-updated; it is stdlib-only (`urllib`), so it also runs where curl quoting gets
awkward. When hand-rolling the call, enumerate the `-d` arguments literally or build
a bash **array** (`args+=(-d "publishedfileids[$i]=$id")`) — string-concatenating them
into one variable and expanding it unquoted only survives while no value contains a
space.

Read the response codes carefully:

- `result == 1` — normal.
- `result == 9` (not found) — **not proof the mod is gone.** Items can be absent from
  this endpoint while still publicly viewable and subscribable on the Workshop. Open
  the page and check for the Subscribe button and subscriber count before declaring
  anything removed.

Workshop pages display **relative** dates ("20 Aug @ 7:28pm", or a bare "31 Jan, 2025").
Never report one without resolving it to an absolute date — that is what the API's
`time_updated` is for.

### 4. Classify by mechanism, not by title

For a functional request ("mods that do X"), near-miss mechanisms read the same in a
title and differ in ways the user cares about. Read each description and sort
candidates into explicit tiers, e.g.:

- **Exact** — implements X with the granularity asked for (per-ability conditional
  triggers).
- **Adjacent** — produces the same visible outcome by a different route (always-on
  passives; delegating the unit to the AI).
- **Dead predecessors / forks / submods** — same lineage, still useful as context for
  which item is canonical.

Present the tiers separately and say which one answers the question. Bundling an
adjacent mod into the headline list is the failure mode; the user asked for X and the
difference is the finding.

### 5. Judge maintenance on evidence, in this order

| Signal | Where | Weight |
|---|---|---|
| `time_updated` vs. the current patch date | API | Primary. Older than the latest patch = *unverified against it*, not *broken* |
| Author's own statement ("I no longer maintain…") | Description | Overrides a recent timestamp, which may be a description-only edit |
| Author replying to patch-compatibility reports | Comments | Strong liveness signal — active author beats a stale date |
| Community reports ("seems to be working with 9.0" vs. "my abilities came back") | Comments | Quote both sides when users disagree; do not average them into a verdict |
| Upstream now ships the feature natively | Developer patch notes | Kills the whole question — check before cataloguing mods |

For database-edit mods (most Total War mods), staleness is not automatically fatal:
they edit data rows rather than hooking code. Say that, and say that a patch which
reshuffles tables is exactly why an author may rebuild from scratch.

Comment and description extraction on a detail page: `.workshopItemDescription`,
`.detailsStatsContainerRight` (size | posted | updated), the sidebar div containing
`Unique Visitors / Current Subscribers / Current Favorites`, and
`.commentthread_comment` + `.commentthread_author_link` + `.commentthread_comment_text`
for the thread.

**Before reverse-engineering any engine behaviour, spend the first call on the community's own
documentation.** This game family has a maintained wiki, a 20k-member modding Discord and —
most usefully — a generated API reference that includes *CA's own* UI callback documentation.
Reading one page of that turned an inference into a fact (the documented trigger list of the
layout callback that handles mouse buttons) after several hours had already been spent inferring
it from data. The tell that you are about to repeat that mistake: you are about to conclude a
capability is impossible, or to enumerate engine internals by scanning binary files. Look first —
`references/tw-community-resources.md` lists where, and what each source is actually good for.
This does not replace reading the engine's own files; it decides *which* files to read.

### 6. Feasibility: could someone build the mod that does not exist?

A sweep that finds nothing is a market fact, not a capability fact. When the user
follows up with "investigate if it is possible to create such a mod", answer from the
engine's shipped surface — never from forum opinion or from the absence of a mod.

1. **Establish the engine's modding surface first.** Find (a) an API reference
   generated from the engine itself and (b) a public dump of the game's extracted data
   and scripts. Then cite **exact table and function names**. A verdict that names them
   is checkable; "it should be possible" is not.
2. **List files in a large dump repo with the git trees API** —
   `GET /repos/<owner>/<repo>/git/trees/<branch>?recursive=1`, then filter the paths in
   Python. The `/contents/` endpoint silently truncates a big directory at 1000
   entries, and the truncated tail reads exactly like "that table does not exist".
3. **Separate the two ceilings.** A *data-layer* mod can only use the condition values
   and enum lists the engine already ships — a fixed flag table cannot be extended, so
   "I want a condition that isn't in the list" is a genuine dead end. A *script-layer*
   mod can compute arbitrary conditions but must own control handover and breaks more
   often per patch. Say which one the user would be getting and what each costs.
   Before scripting an approximation of an engine state, search the flag and AI-scoring
   tables for that state — a condition the engine already tracks is often expressible as a
   `passive` ability plus one deactivate-flag row, evaluated against the engine's own state
   instead of estimated from queries. See `references/wh3-mod-authoring.md` § check the data
   layer before scripting an approximation.
4. **Prove every required step separately.** A shipped engine file or an existing mod
   that already calls that API is proof; a mod that only gets partway through the chain
   is not proof of the rest, and "each piece exists" is not the same claim as "nobody
   wired them together yet".
5. **Name what you could not test.** Anything requiring the game to be running
   (control handover between script and player, polling cost at scale, per-patch
   breakage) is a stated risk, not a favourable assumption.
6. **Frame the gap honestly, with effort.** Usually the missing mod is not technically
   impossible but effort-versus-reward: an easy data edit everyone has already done
   against a multi-week engineering job nobody was paid for. Give the estimate and say
   which one it is.
7. **Check the toolchain is alive before recommending it** — the standard editor/tool
   repo's last commit date — plus the in-game test tool for the title.
8. **Read a shipped mod's own files when one exists that does the thing.** A pack on disk
   beats any description of it, and a working mod is a worked example of the exact engine
   calls involved. Steam's anonymous command-line client cannot pull a Workshop item for a
   paid title — ask the user to subscribe, then read the pack from
   `steamapps/workshop/content/<appid>/<item id>/` (see `references/rpfm-server-protocol.md`
   § reading a pack you did not build). **Ask and stop rather than routing around it** — this user
offers to subscribe and wants the question, not a workaround that quietly narrows the check to what
was already on disk. Check the table filenames before concluding what a
   pack changes: a table file named anything other than `data__` is merged additively, while
   `data__` replaces the vendor's table outright.

Depth, doc sources and a worked example: `references/modding-feasibility.md`.

**Where to ask, and where the engine-level docs are.** Da Modding Den
(`discord.com/invite/moddingden`, ~20k members — the community the wiki and most script authors
came out of) is the fastest route to an engine question; `tw-modding.com` is its wiki (browse the
page list, its search index returns nothing for every query);
`chadvandy.github.io/tw_modding_resources/WH3` is the generated API reference;
`twcenter.net` → DB Editing & Scripting is the forum equivalent; and `consulscriptum.com` is a
scripting framework whose in-game `/debug_onclick` and `/debug_mouseover` name UI components for
you. Check all of them for a public precedent before concluding nobody has done a thing — but
report an absence as "no public trace found", naming which sources could have shown one.

### 7. Deliver

This user wants a **saveable file**, not a display-only answer: write the report as
markdown to the Desktop (`C:\Users\vlady\Desktop\<topic>.md`) and deliver it with
`MEDIA:<absolute path>`.

**When the user is choosing a look, show it, and build the mockup from the game's real assets.**
"Option A: dimmed icon. Option B: a small AUTO label. Option C: nothing." is decided on sight, not from
prose. Extract the actual artwork out of the vendor pack, embed it base64 in a self-contained HTML file,
draw the surrounding frame to scale, and render that file in the message with the app's preview
directive so it displays without the user opening anything; also leave the HTML on the Desktop and say
which parts are real art and which are the agent's drawing. The same applies to any before/after or
state comparison the user has to approve.

**The file is a second copy, never the only carrier.** The message must stand on its
own: the ranked table, the verdict, any code, and any numbered procedure all appear in
chat as well. Assume the attachment cannot be opened — when the deliverable is code or
a build procedure, paste the actual file contents and the steps inline and mention the
Desktop path as a convenience. A reply whose substance lives only in the file delivers
nothing.

**For a script the user has to read, ship a log-free annotated copy — and keep it in sync.** When the user asks to understand code rather than run it ("a version without logs, with a comment on every line so I can read it"), produce a separate copy on the Desktop: strip every logging call, destroy nothing else, and comment **every line or logical section** in plain English for someone who does not read code fluently — no unexplained programming jargon, and the same care in the section banners as in the lines. Two mechanical traps: a logging call can *be* a branch body (remove the logging, never the control flow), and comment prose that mentions a banned token still trips a later grep of the whole copy. Verify with syntax, a zero-count for the logging calls and for any banned function, a functional-token inventory proving every real call survived, and a smoke test driven by the existing mocks. Then re-mirror it on every subsequent change to the live file - an annotated copy that lags the code is worse than none - and diff the mirror to show only the intended hunks.

**Deliver visuals as static markup (HTML/CSS or inline SVG), not page scripts.** The user opens these
files in a viewer that renders text and static markup but never runs the page's JavaScript — two
canvas visualisations shipped this way came back as blank boxes ("Still don't see your visualization")
while captions rendered fine. Draw with plain markup, keep any scripted version as the optional extra,
and do not spend another round on it: the numbers belong in the message either way.

- Cite every mod by **numeric Steam id plus title** — titles collide across forks and
  localisations, ids are stable. Include subscriber counts and absolute last-updated
  dates, since those carry the maintenance argument.
- State the coverage method and its limits (how many sweeps, which languages) so the
  user can judge whether the list is complete.
- Lead with the mechanism explanation. This user reads critically and wants the real
  reason a thing behaves the way it does, plus plain-language definition of any
  domain jargon.
- **When the question is binary, answer it binary — first.** "Is that possible?" gets an explicit
  "Yes" or "No" as the opening word, then the reason in a sentence or two, then the evidence if it
  is short. Asking for a one-word answer is a signal that the surrounding analysis is what they
  cannot use yet; a paragraph of hedging before the verdict reads as evasion. Add the detail when
  they ask for it, or when the verdict is "no" and the reason changes what they do next.
- When generating a Sources block from a citation ledger, ids that appear **only
  inside markdown table rows are not counted as prose** and get dropped from the
  auto-rendered block. Render with an explicit id list (`render --only 1,2,3,...`)
  rather than `--cited-in`, or the delivered file loses most of its links.

### 8. Build it: the engine-file loop

When the request moves on to "do a test case with one ability" or "help me build it":

1. **One ability, one condition, one action.** A test case that cannot fail ambiguously
   is what makes the engine's behaviour legible. Before writing code, pull the target's
   real row out of the dump table — duration, cooldown, use limit, whether it is
   already `passive`, and the engine's own AI-usage tag for it. Quote those numbers:
   they say what a sensible trigger is, and whether the player has to unlock the
   ability first (a test that fails only because the unit never had the ability wastes
   a turn).
2. **Write to the loader's auto-load path under a unique name, and log from the first
   line.** Log the *diagnostic* fact the user would otherwise have to guess (does this
   unit own the ability at all?) next to the action line, so a run that does nothing
   still reports which half failed. Tag every line with the file name — the engine log
   is enormous.
3. **Ask, then act, then check the consequence.** Query legality before issuing the order
   (an illegal order raises a script error), log the attempt *before* the call so a failure
   cannot erase its own evidence, and afterwards re-read the dependent state to prove
   something actually changed — a call that returns successfully has not necessarily done
   anything. Keep a local rate guard as well: the legality check does **not** cover the
   cooldown, so take the guard's value from the ability's own `recharge_time` row rather than
   from a guess.
4. **Compile and mock-test before handing it over** — `scripts/lua_check.py` is the
   syntax gate, `templates/wh3_battle_auto_ability.lua` is the known-good file shape
   (whole-body-wrapped poll, the vendor-call-site activation shape, multi-key matching,
   charge measurement, guarded logging included), and
   `references/wh3-mod-authoring.md` has the harness and the packaging command set. Drive the real file against a
   mock of every call it makes, with the units it must ignore as well as the one it
   must act on. **Stub the whole chain the code walks and assert the path actually ran** — a
   stand-in that returns nothing for an intermediate lookup silently skips the very code under
   test while the harness still passes. Then split the deliverable explicitly: what the mock
   proved, and what only the running game can prove. Never present unrun code as working.
5. **Hand over the in-game procedure as numbered steps, the log lines to expect, and a
   symptom → cause table.** The log is the only debugger available, so a run that
   produces nothing must still be diagnosable from the answer alone.

   Give a **paired** test — one action that must fire and one that must not, differing only
   in the signal the condition depends on — so a single battle can falsify the condition
   rather than merely confirm it. Name the assumption the pair is testing, especially when the
   condition rests on an inference from documentation rather than on a query the engine
   provides.
6. **Offer the one-line experiment that isolates the risky call** — run the action
   directly, with no polling and no conditions — so the user can separate "the engine
   call misbehaves" from "my logic never fired".
7. **Build, verify and install the pack without the GUI.** The editor ships a headless
   backend (`rpfm_server`) that speaks its whole API over a local WebSocket, so the
   build-verify-install cycle can be run end to end instead of handed to the user as
   menu steps. `scripts/build_and_install_pack.py` does it: new pack, add files, set
 type, read every file back **out of the pack** and hash it against the source, save,
 then copy into `data/` and hash the installed copy. `scripts/rpfm_probe.py` is the read
 side (list / extract / search packed paths): use its `find` + `extract` modes to pull a whole
 vanilla file set out of a game pack and grep it locally rather than asking the server to search
 for you, and remember that the UI packs store layouts uncompressed, so a raw byte scan answers
 "does any layout declare X" with no tooling at all. Ship a test mod as type `Movie`
   — the engine loads it from `data/` unconditionally and hides it from the launcher,
   which removes the mod-manager step from the user's side entirely. The user's only
   job then is the part no tool can do: play the battle. Start the backend before the build
   and give it a beat: `rpfm_server` exits when its last WebSocket session disconnects, so it is
   not there for the next call — launch it as a **background process**, wait a few seconds, then
   build. Keep `&` out of terminal command text, including inside heredoc'd code: the guard reads
   a literal `&` (even a bitwise-and in Python) as backgrounding and refuses the whole command —
   write `% 4294967296` where you would have masked with `& 0xffffffff`.

### 9. Controls the player operates in battle

A toggle, a HUD button or a key is a different design question from the trigger logic, and
the engine's input surface is narrow: the input-handler hook carries camera movement only,
a settings framework gives a menu rather than an in-battle control, and a HUD control that
renders but never receives its click fails silently. Of player input, exactly two families reach a
script in battle — **left-click component events** and **keyboard shortcuts** (`ShortcutTriggered` /
`ShortcutPressed`); right-clicks and left-double-clicks are never delivered, measured against the
full event vocabulary, so any design that needs them is dead on arrival and should be reported as a
constraint rather than debugged. **Put every UI call in a UI-synchronised context — and check the context is not too early.**
Engine calls on uicomponents made from the battle-model timer (the poll) silently do nothing,
which reads as a styling bug, and can leave the battle's timers dead, which reads as the
trigger having broken. **The fix is never to manipulate the timer registry.** Register your repeat **once**, at load, and
leave it alone — do not "repair" a quiet timer by removing and re-adding it:

- `bm:remove_callback(name)` unregisters the record **first**, so if the re-add then raises you
  have deleted a healthy timer and put nothing back — the poll is dead for the rest of the battle;
- and it cannot be repaired afterwards. The battle's repeating callbacks ride on one engine timer
  whose driver re-arms it only *after* its callback loop completes, so once that driver has lost
  its engine timer, re-registering is **inert**: the records sit in a list nothing walks, and every
  re-add reports success while nothing ticks.

So: create and paint in the `Deployment`/`Deployed` callbacks, keep the phase-change listener
log-only, and let a `bm:repeat_real_callback` **watch** the poll's tick counter and simply *report*
a stall after two consecutive frozen checks (a pause legitimately freezes model time, so one silent
check means nothing). Reporting only — it makes no engine call and repairs nothing. Add nothing on
a third clock. If the appearance and the trigger turn out to be mutually exclusive, pick the one
the user asked for and say which you gave up: a repair that cannot work is worse than the failure
it hides, because it turns a legible cause into a plausible-looking success.

**Before drawing a control, enumerate what the engine already reports.** The engine ships its own
list of observable UI events (`script/events.lua` — `ComponentLClickUp`, `ComponentLDBLClickUp`,
`ComponentRClickUp`, `ComponentMouseOn`/`ComponentMouseOff` and the rest), and that table, not a
wiki page, is the authority for what player input a script can see. A listener on a component the
game already draws inverts every cost in this section: no `CreateComponent`, no icon to ship, no
clock to get wrong, nothing to repaint when the state flips. So when the requirement is "the
player operates X in battle", check whether the engine already draws something to operate before
designing a control — and if a custom control's cosmetics have already survived two rounds of
repair, that lookup is overdue.

**But the table proves only that an event NAME exists, never that the engine delivers it.** A UI
component receives only the mouse interactions its **layout file** declares, and right-click is
declared nowhere in the vanilla UI: `name="rclick"` appears **zero** times across the 907 layouts
in `data/ui3.pack`, against 83 `name="lclick"` and 2415 `ContextCommandLeftClick`, while CA's own
right-clicks are wired per component as `mouse_event0="rclick"` properties or
`ContextCommandRightClick` callbacks. The unit card that draws the ability icons declares
left-click only, so a catch-all `ComponentRClickUp` listener on it logged zero events in a battle
where the player right-clicked those icons repeatedly — the route failed silently, looking exactly
like a mis-painted icon while the feature under test kept running.

So before designing around a listed event:

1. **Check the layout declares that interaction** — the UI pack's layouts are stored uncompressed,
   so a raw byte scan answers it (`grep -a -o 'name="rclick"' data/ui3.pack | wc -l`). No
   declaration means no script change can make the event arrive — **and a replacement layout file
   does not save it either**: a layout callback can only broadcast to the UI or set a property that
   script reads back as its own name. So report the interaction as unavailable to script rather than
   iterating on the listener or shipping a layout override for it.
2. Enumerate the engine's delivered events with the firehose test (`references/wh3-battle-ui-and-input.md`)
   before designing around any listed name: it is the difference between "our filter is wrong" and
   "the engine never raises this".
3. If it is declared *and* delivered, take it permissively and let one real run name the component
   (next rule) before gating anything on it.

**Never gate a first build on a guessed component name.** Engine-drawn elements are often
instantiated per unit (ability buttons come from the unit card layout's `template_ability`), so the
name the event reports may not be the layout's string. Take the event with a filter that accepts
everything, log the name of every **distinct** component it fires on — once per name, keyed in a
table, or a click-heavy battle floods the log — and match loosely. The run then either works or
reports the real name for a one-line fix. Event inventory, the layout-declaration check and the recipe:
`references/wh3-battle-ui-and-input.md` § listening instead of drawing — read the layout before
designing around it.

For player-facing feedback, prefer what the engine renders over what you paint —
`bm:show_subtitle(key, true, true)` with your own `.loc` entry needs no layout work and
*reports* failure instead of failing silently. Recipe and the localisation-file step:
`references/wh3-battle-ui-and-input.md` § the engine-rendered indicator, which also carries
 the input inventory, the clock rule, the template-clone button recipe and the mock harness.
Keep the control's position
in a named constant (you cannot see the user's screen), and ask the user for the facts a log
cannot carry — did the control appear, where, and did its icon or label change. **When a test comes
back negative, investigate before proposing the next change.** This user asks for it in those words
("investigate first and find out why"): read the log, state the mechanism with the numbers that prove
it, and only then name a fix - and when the evidence shows the attempt could not have worked, say
which door that closes rather than shipping another variant of it.

## Pitfalls

- Reporting a Workshop page's relative date as "last updated" — always resolve it via
  the API first.
- Treating `result == 9` as deletion; confirm on the page.
- Declaring a mod list complete after one or two search phrasings — relevance ranking
  hides the long tail behind 20-30 differently-worded sweeps.
- Calling a stale mod broken without checking the comments; and calling it fine without
  checking whether the author abandoned it in the description.
- Skipping the current patch date — "last updated 2026" is meaningless without the
  yardstick it is being compared to.
- Answering "is this moddable?" from search results alone. The absence of a mod says
  nothing about what the engine allows; only the data tables and the scripting API do.
- **Reporting a negative from a code or search source you have not validated.** "No results" is
evidence only if that source indexes the corpus: one public code-search tool returned zero hits
for a Total War engine call that exists in thousands of shipped files, so its silence about any
other symbol proved nothing. Run a **control query** with a string you know is present before
quoting an empty result, and prefer sources that *can* show a positive — the engine's own shipped
files, the packs already on the user's disk, the community docs. Say "the packs on this machine
contain none" rather than "nobody has used it" when the sample is the user's subscriptions.
- **Trusting a `/contents/` directory listing on a large repo** — it truncates, and the
  missing tail is indistinguishable from a true negative.
- Presenting an untested step as working — including code you just wrote. Compile and
  mock-test what you can before handing it over, and if it needs the running game to
  confirm, the deliverable says so in the same sentence as the claim.
- Taking GUI menu paths from community guides. Tool menus get renamed between major
  versions and tutorials lag them; write instructions from the tool's own shipped
  documentation (a docs folder inside its repo), and say the menu name may differ in
  the user's version. A step the user cannot locate reads as a broken instruction, and
  the follow-up costs a whole turn.
- Blending two alternative tool workflows into one numbered list. When a tool offers a
  project/folder-based path and a manual path, write them as two labelled sequences; a
  merged list produces steps that contradict each other.
- Describing a creation step without saying what it does *not* do. Say that it builds
  the artifact in memory only, that the name arrives at a later save step, and that
  nothing is on disk yet — that gap is where the user loses the thread.
- Assuming a repo's default branch is `main` when fetching raw files. Read
  `default_branch` from the repo API first, or every raw URL 404s and the file reads as
  non-existent.
- **Picking a test unit from its campaign ability list.** A custom/skirmish battle grants
  only the unit's *innate* abilities (`land_units_to_unit_abilites_junctions` — note the
  engine's misspelling); campaign additionally grants skill-tree ones. Look the unit up
  in that junction table, and match on the ability **key** rather than its display name
  (the same ability can exist under two keys), before telling the user which character
  will demonstrate it. Otherwise the user runs the test, finds the ability missing, and
  debugs it for you.
- Treating "nothing in the log" as one symptom. A poll that early-returns on a phase
  gate makes "the timer never ran" and "no condition was ever met" produce byte-identical
  silence. Ship a proof-of-life line on the first tick plus a periodic heartbeat carrying
  the battle phase name and each watched unit's state — that is what converts a mystery
  into a diagnosis on the next run.
- **Letting one raising call kill every timer in the battle.** The battle's script timers all
  ride on a single engine timer whose driver loops the pending callbacks and re-arms itself
  only *after* that loop finishes — so one callback that raises aborts the re-arm and every
  repeating callback in the fight goes silent for good, which reads exactly like "the trigger
  never fired". The phase dispatcher has the same shape: an error out of one phase callback
  starves every callback registered after it. Wrap the **whole repeating body** in `pcall`
  (not only the individual engine calls inside it), wrap each phase callback separately,
  register the callback you cannot afford to lose before the cosmetic ones, and log the error
  text behind a counter so a recurring fault is visible without flooding the log.
- **Writing the success line after the call it reports.** A log statement placed after the
  engine call vanishes precisely when that call fails, so the run shows every precondition
  satisfied and no output at all. Log the attempt, then `pcall` the call, then log the
  error text — in that order.
- **Trusting a generated API annotation for a call's argument order or its described return
  behaviour.** Engine-side annotations lag the engine, describe signatures ambiguously, and
  can be flatly wrong about what a call returns — one documented as "the destination while
  moving, the unit's current position while attacking" actually tracked distance travelled
  since the order was given, so gating on it blocked every genuine trigger while looking
  correct in a mock. For an argument order the authority is the engine's own call sites: grep
  the shipped script tree for the method name, read two or three real call sites in full, and
  copy the shape verbatim — including which arguments are mandatory — before writing any code.
  For a *returned value* the authority is measurement: log it every cycle and read the real
  numbers from a real battle before gating anything on it. Probing `pcall`'d candidates is the
  fallback for a method with no call sites at all, not the first move: each guess costs the
  user a battle.
- **Shipping speculative extra triggers on the build the user tests.** A condition left on
  "so the run returns a positive result" fires when it should not, so a successful test comes
  back reported as a defect ("it activated while it was just running") and the diagnosis round
  is spent on a config flag instead of the mechanism. Put exactly the condition under test in
  the build, and keep any extra trigger behind a named constant that is off.
- **Reading a call's success as its outcome.** A return value says the order was accepted,
  not that it did anything. Re-read a dependent state afterwards and treat the change as the
  proof — but **validate the probe first**. A capability query describes what you may order
  now, not what is already running: one such probe stayed `true` right through a confirmed
  activation, which made a working build read as a total failure for a whole round. A probe
  that never moves is the wrong probe, not evidence that the action failed.
- **Adding a speculative fallback call whose preconditions the target does not meet.** A
  wrong-target order can be accepted, leave the unit in a targeting state, and cancel the
  player's movement order: the fallback becomes the bug the user reports, and the real
  cause stays hidden behind it for a round.
- **Blaming the game for a side effect your own order caused.** Issuing an order through a
  unit controller takes control of the unit — greyed card, cancelled current order. List
  the script's own side effects, next to the expected behaviour, in the deliverable.
- **Doing UI work from the battle-model timer.** Engine calls on uicomponents issued from a
  `bm:repeat_callback` / `bm:callback` (model clock) silently do nothing — a control keeps the
  template's vendor placeholder image while its state changes still apply, so it reads as a
  styling bug — and the model timer can stop running afterwards, which reads as the trigger
  having died. The same calls issued from a phase callback or the phase-change listener *do*
  land, and take the model timer down with them, so a feature that already worked comes back
  reported as broken. Do UI work only in a click listener or a `bm:repeat_real_callback` /
  `bm:real_callback` gated on a HUD-ready flag, and move work between the clocks by changing
  the call, never by retrying on the model one. When a control's appearance and its
  state disagree, make the two states unmistakable (separate icon files, lit vs plain) and ask
  the user which one looked lit — do **not** bank on a reported-state diagnostic:
  `CurrentState()` on a component built with `CreateComponent` returned a *function* rather
  than a state name, so that log line proved nothing — read back an **image** path instead
  (`uic:GetImagePath(0)`), which returned the real value. And once a purely cosmetic detail has
  survived a round or two of fixes, stop repairing it: move the player-facing feedback to
  something the engine renders with no asset and no localisation to resolve — the engine's own
  pulse highlight on a component it already draws (`uic:StartPulseHighlight(strength)` /
  `StopPulseHighlight()`, what the advice system uses) — rather than spending another battle on a
  picture. Text you supply is the weakest option: both localisation routes tried failed in
  practice (your own key via `show_subtitle` → `result=false`; overriding a vanilla key → the
  vanilla text still won).
- **Assuming your own `.loc` file loaded.** A hand-written localisation file shipped inside a
  `Movie` pack can sit unread, and the failure is legible if you log the call's result:
  `bm:show_subtitle(key, true, true)` comes back `ok=true result=false`, meaning the engine found
  no text for that key, and the screen stays empty. `result=false` is *the key did not resolve*,
  not a display failure — so never make text you supply the feature's only feedback until a run
  has proven the key resolves. Prefer an indicator the engine already draws.
- **"Repairing" an engine callback that has gone quiet by re-registering it.** Removing a
  repeating callback unregisters it *before* the re-add, so a re-add that raises deletes a healthy
  timer and leaves nothing behind; and once the engine-side driver has been lost, re-registering is
  inert — the add reports success and nothing ever runs again. Register once, then watch and report.
  A repair that cannot work is worse than the failure it hides, because it converts a legible cause
  into a plausible-looking success that costs rounds to unwind.
- **Answering "did you actually ship that build?" with assurance instead of evidence.** When the
  user reports that nothing changed, hash the installed artifact against the built one and point to
  a log line that **only the new build can print** (a new startup line, a new diagnostic). That
  settles delivery in one step and tells you which half to debug — and if the artifact does match,
  say so plainly before explaining the symptom, because "the build was current and my code was
  wrong" is a different conversation from "it did not upload". A plain `grep -a` for a symbol your edit introduced (occurrence count = definition + call sites) usually matches even inside the zlib-compressed pack, naming exactly what shipped without reopening it.
- **Trusting a mock that never reached the code under test.** A stand-in that returns nothing for an
  intermediate level of a lookup chain makes the harness skip the whole path in silence while still
  passing, so a broken paint path survives as "mock-verified" for several rounds. Stub every level the
  code walks, and assert the log line that proves the path ran — not merely that nothing raised. And cover the
  *absence* and *stale* cases, not only the healthy one: a fix whose point is "the indicator hides" is only
  demonstrated by a run where the handle is missing, and one about a dead handle only by a mock whose reads
  raise — a harness that supplies a healthy component proves the show path and nothing about the hide path.
- **Never remove and re-add a model timer.** A "repair the timer if it died" helper that calls
  `bm:remove_callback(name)` and then `bm:repeat_callback(...)` is worse than the disease: the
  removal takes the healthy repeating callback out of the model timer list, and if the re-add then
  raises (it was observed throwing inside `lib_timer_manager.lua`: `battle:time_elapsed_ms() +
  interval` with a function on one side), the callback is gone for the rest of the battle. And the
  repair can never work anyway: once the model-timer driver has lost its engine timer, records added
  back sit in a list nothing walks — re-registration returns success and does nothing, so a
  watchdog that "repairs" reports `ok=true` forever while the feature stays dead. Register once at
  load, leave the registry alone, and have any watchdog **report** a stall, not fix it.
- **A layout can already contain the affordance you are about to build.** Before designing a
  tooltip line, new component or extra panel, grep the layout the player is looking at for the
  words the feature would use — the ability tooltip ships `label_left_click` ("Left-click to
  activate") *and* a sibling `label_right_click` whose placeholder text is literally
  `Right click text that comes from db`, hidden only by a context visibility condition and filled
  from `Loc("right_click_spell_browser")`. Filling in the reserved component is one edit and wins
  by pack name; adding a component means hierarchy, definitions, fonts and loc.
- **Accessors on script-created components can be properties holding functions.** `NumStates()` and
  `CurrentState()` on a component built with `CreateComponent` returned functions on the real
  engine, so `for i = 0, count - 1` raised `attempt to perform arithmetic on local 'count'` and a
  per-state repaint silently did nothing. Guard with `type(x) == "number"` before using an accessor
  result, and validate what a control *reports* (`GetImagePath`) rather than trusting that a setter
  that did not raise had any effect: `SetImagePath` returned success while the component's image 0
  stayed unchanged. The same holds for `Id()` on engine-drawn ability buttons: it answered with a
  *function* (or a real id string, or raised - depending on the component and the moment) while the
  button's ability key read correctly, so a liveness gate keyed on `Id()` being a string rejects live
  buttons forever (`scan: claimed ...=false` every scan, no badge). **Judge ability buttons by their
  ability key, never by `Id()`** - and when the engine value itself misbehaves, copy it first:
  the ability-key value passed `type(key) == "string"` and concatenated fine (the walk header
  printed it), yet battles crashed right after the header with no claim line ever printed, the only
  work in between being `string.lower`/`string.find`/`#` on that value. Make a plain copy
  (`pcall(function() return v .. "" end)`, fallback `tostring`) and run every string operation on
  the copy only. **`string.find` is banned from the match path outright:** the bisect ladder named the four-argument plain-mode form as the operation that killed the engine (its last log line was `bisect: step 7 string.find plain entering`, no `ok`), so match ability keys by EXACT EQUALITY against a complete variant list; keep a find-free helper (`string.sub` slice scan) for the engine's own error text, and have the harness instrument `string.find` and assert zero invocations in every world.
- **The engine's "unit abilities" helper path is the behaviour row, not a character's abilities.**
  `lib_battle_ui.lua`'s `highlight_unit_abilities()` walks
  `battle_orders/orders_parent/behaviour_parent`, which misleads you into hard-coding it — on a
  character the three slots report an **empty** `InterfaceFunction("AbilityKeyForScript")`, because
  that row is fire-at-will/skirmish. Do not hard-code it: scan the HUD and ask each component that
  same question, logging each hit with `UIC:Address()`, so a failure names what was found instead
  of assuming a path.
- **Identify the component from the engine's own output before patching any layout.** Instrument the
  script to log the `Id()` of the component the engine reports for the thing you care about, then grep
  the layouts for that id. Guessing by role (`template_ability`, `button_behaviour`) is how three
  rounds got spent patching components the engine never delivers clicks to; the engine's own log named
  the real one in one line.
- **Enumerate EVERY namespace of a wiki, not just the main one.** MediaWiki's `list=allpages` returns
  namespace 0 by default: on tw-modding.com that was 37 pages while the `UI:`, `Lua:`, `Tutorial:` and
  `Battle Maps:` namespaces held ~400 more, and the answer to the question lived in `UI:Main Page`.
  Query `meta=siteinfo&siprop=namespaces` first, then `allpages&apnamespace=<id>` per namespace.
- **A UIComponent only fires some events by default (`ComponentLClickUp`). Call
  `uic:AddScriptEventReporter()` on it to make it fire ALL of them** - that is the documented
  (UI:Main Page) and vanilla-used (`_lib/lib_movie_overlay.lua`) route to mouse events such as
  `ComponentMouseOn`/`ComponentMouseOff`/`ComponentRClickUp`. Listening for those events without the
  reporter hears nothing, which looks exactly like "the engine cannot do it".
- **Measured in WH3 battle: left-click component events are delivered to script, right-clicks never
  are.** With `AddScriptEventReporter()` on the target component and its whole ancestor chain, an
  unfiltered `ComponentRClickUp` listener sees zero events; `ComponentLClickUp` fires for every HUD
  button (`button_ability`, `button_toggle_infopanel`, unit cards by id) in the same battle. Do not
  promise a right-click control in battle — it cannot be delivered.
- **A layout can act UI-internally but cannot hand anything to a script.** A broadcast callback
  (`ContextEventBroadcaster`) notifies UI callbacks only, and a property a layout sets with
  `self.SetProperty(...)` reads back from script as its **own name**, not its value — undeclared,
  declared in `<userproperties>`, and for a property vanilla itself sets (`icon_index`) alike, on a
  component whose `Id()` and parent chain proved it was the right one. So the layout-property bridge
  is closed: design around the channels the engine reports to script (command events, and the
  `Shortcut*` events below). Detail: `references/wh3-battle-ui-and-input.md` § what input the engine
  actually gives a script.
- **`register_input_handler` / `register_input_handler_callback` are camera-only** (move/rotate/edge
  scroll). Mouse clicks are not in that list; the only click channels are the Component* listeners,
  and only for an interaction the layout declares *and* the engine actually delivers.
- **Anchor a bulk edit on a marker unique to YOUR change, never on a name vanilla also uses.**
  A regex that found `ContextEventBroadcaster`-blocks by callback name and replaced them with the
  new callback ran from *vanilla's* identical block (the dev button's `DevLevelUp` broadcast) to the
  inserted value and deleted **221 KB** of a 434 KB layout — a file that still parsed, still
  had its `<components>` and `<hierarchy>` tags, and would have shipped as a silently gutted unit
  card. Edit by literal block, insert into a named component, and assert the result: after any bulk
  edit check the file size against the pristine copy and the count of the thing you added, and put
  both assertions in the build script so a truncated layout cannot ship.
- **Keyboard shortcuts are the one player input the engine delivers to a script in battle.**
  `ShortcutTriggered` and `ShortcutPressed` fire with the shortcut's name in `context.string`
  (`step_r`, `step_l`, `step_bck`, `step_fwd` were observed live), and **no vanilla script listens to
  either** — so binding a control to them hijacks nothing, unlike stealing the keyboard. A layout
  component declares the shortcuts it answers with `shortcut` / `shortcut0..N` user properties.
  **Whitelist one deliberate name; never blacklist the noisy family.** The camera actions are not one
  prefix — `cam_up`, `cam_down`, `rot_d`, `rot_u`, `step_l`, `step_fwd`, `intelli_zoom` all arrive, so
  excluding `step_*` alone left a switch that flipped dozens of times while the player merely looked
  around. Prefer a **number** key: pressing one whose control group is empty (`usegroup0` … `usegroup9`)
  does nothing else mid-battle, whereas every other observed name is a real game action
  (`toggle_pause`, `toggle_ui`, `battle_land_withdraw`, `battle_land_guard_mode`, `battle_land_about_face`,
  `battle_land_strafe_*`, `show_tactical_map`, `show_radial`, `cycle_next_spawn_zone`). **Debounce every
  press**: the same name arrives two or three times per key press, so a naive toggle flips and flips back
  in the same instant and reads as a dead control — drop a repeat of the same name inside one poll tick,
  and log the dupe so the pairing is visible instead of hidden. Recipe and the measured vocabulary:
  `references/wh3-battle-ui-and-input.md` § a key the engine reports.
- **Ask a component to report its events before giving up on one.** Components fire only a subset by
  default; `uic:AddScriptEventReporter()` (wiki `UI:Main Page`; vanilla's own use is
  `_lib/lib_movie_overlay.lua`, commented "set the panel to report all script events") makes one fire
  **all** of them — but it does not conjure events the engine never raises, and it applies per
  component, so put it on the component *and its ancestor chain* (a click can be credited to a
  container).
- **An engine-drawn component cannot be restyled from script — and writing to one breaks your handle
  on it.** On the ability button `SetImagePath(target, <icon index>)` returned success and `GetImagePath`
  read the new path straight back (`MATCHES` on ~190 swaps) while **nothing on screen ever changed**;
  `SetState(...)` behaved the same. The mechanism, measured over two further builds: a script write to
  such a component **invalidates the reference** — from the next toggle on, every read returned a
  *function pointer* or `'0'` instead of a value, and re-acquiring the component by its `Id()` failed,
  so all later writes went to a dead object. A read-back that matches proves the component **stored**
  your value, never that the frame **drew** it; and a *state name* read from the engine is not evidence
  about pixels — the same component read `active` in one run and `inactive` in another while looking
  unchanged both times. The user's eyes corrected the first explanation: believe them over the value.
  For a visible change on a component the game draws, either change the game state the engine draws
  *from* (for a battle ability: `unit:disable_special_ability(key, true)` produces the engine's own
  dimmed look, at the cost of blocking manual use while disarmed) or draw your own element — state
  which cost you are taking before spending a battle on it, and never re-try a restyle that already
  came back `MATCHES`-and-invisible.
- **The element you draw yourself should be a CHILD of the thing it labels.** A child component is
  positioned relative to its parent, so creating the indicator with
  `target_button:CreateComponent(name, "ui/templates/square_medium_button")` puts it on that icon and
  travels with it — no hardcoded coordinates, and the same code generalises to every instance the
  scan finds (one badge per ability, each answering to its own flag). AI General's battlemod extension
  is the shipped precedent for the rest of the recipe (docking + `SetDockOffset`, on the orders bar).
  Two consequences to state up front: creating a child is itself a write to the engine-owned parent —
  log whether the parent survives — and if the badge never appears, check that the *call site* landed,
  a patch that adds `create_badge()` while the invocation silently no-ops ships
  a defined-but-never-called feature whose log contains nothing at all. **And measure whether the child
  renders before building a feature on it:** on the engine-drawn ability button a child was created,
  painted (`GetImagePath(0)` read our own PNG back) and `SetVisible`-toggled, and was **never drawn** —
  a third closed door on that parent, after the image write and the state write, while the same pattern
  works on stable components. Strip every other write to the parent first (each one rebuilds the button
  and kills the child), then ask the user whether the thing appeared at all before any more work goes
  on top of it. The template's frame also decides the on-screen size: `Resize` on a created component did
  not beat it, and a hand-rasterised glyph is a dead end whatever the geometry — thick strokes fused into a blob at ~24 px, and a 4×-supersampled thin-stroked redraw the user still called horrible; hand-draw only simple shapes (a dot) and send letterforms to an engine-drawn **text component** (exact size, crisp edges) in a layout built by **copying** a
  vanilla one, never authoring it (next bullet).
- **A layout you ship is parsed at STARTUP — copy a vanilla template, never author one.** A
  malformed `.twui.xml` under `ui/templates/` does not fail in the battle that uses it: the engine
  reads the template set while the game loads, so a hand-authored layout (structure assembled from
  the wiki's page set, GUIDs invented to match the shape) came back as "the game crashes at
  startup" — before any battle, with the runtime log completely empty, and with no other new
  load-time artifact in that build. The safe route is a byte-identical copy: take a real vanilla
  template whose whole content is the one element you want, change *only* the attribute value you
  need, and assert the copy differs from vanilla in exactly that one string. Text colour, font and
  size are layout attributes (`font_m_font_name`, `font_m_size`, `font_m_colour="#RRGGBBAA"`,
  `fontcat_name` paired to the size) because the script API has `SetText`/`GetText` and **no**
  `SetTextColour`; and the file carries **two** colour attributes — the text's `font_m_colour` and a
  `colour` on the state/component — of which the rendered letter followed the `colour` one, so change
  one and confirm against the user's screenshot before touching the other. **A valid copy is not a
  clean one:** no template that contains a `component_text` is art-free — every one in `ui/templates/`
  also carries `<componentimages>`, so the copy draws the original's panel and ornament pictures too
  (grep for `imagepath=`, not `file=`, which matches nothing and returns a false all-clear);
  repointing those paths at a transparent PNG is measured **insufficient**, so strip the `<image>`
  declarations from the state instead — confirmed working on the user's report: the panel, the divider line and the seal all gone, the letter alone on screen. When the game dies at startup, bisect on what the engine parses at load — your
  shipped layouts first, then the script — and confirm the rebuilt pack's file list no longer
  carries the suspect file. Recipe: `references/wh3-battle-ui-and-input.md` § shipping a layout:
  copy, do not author.
- **Gate on the engine's readiness call, not on a hardcoded cooldown.** A `recharge_time`-derived timer is wrong in both directions once cooldown-modifying effects exist — the user's own objection, and a correct one. Vanilla gates on `unit:can_perform_special_ability(key)` in its battle scripts (quest battles, `wh_battle_advice.lua`), which reads as the intended "may I use this now" check: try each of the ability's keys and use whichever returns true, and log the value with every attempt so a run can confirm it tracks the cooldown. If it turns out not to, fire while the trigger holds and retry on a short interval until the engine accepts. Either way keep only a small (~1.5 s) per-(unit|ability) guard so one second cannot produce repeated calls, and **say which timing is whose**: the engine owns the cooldown and refuses a recharging call (modifiers included), while the guard only throttles how often the script re-asks — presented as cooldown logic it reads as exactly the mistake this user correctly suspects.
- **Bind a created indicator's VISIBILITY to what its target is showing, not to the target's existence.**
  Measured: the dot stayed on screen after the player selected another unit, because a dial is rebuilt per
  selection and is perfectly visible while showing *someone else's* ability. Each tick, ask the component
  you hold `InterfaceFunction("AbilityKeyForScript")` and compare against your key; when it no longer
  matches, hide the element and **drop the handle** so the discovery rescan can re-find the button (and
  re-show the element) when the ability comes back. Visibility is not identity. Gate the show path on positive confirmation *this tick*: no usable handle, or a handle whose engine read raises or returns a non-string, means **hidden** — a hide rule that only runs while a handle is held leaves the element on screen behind a stale reference, measured as the user's report "it doesn't disappear when it should".
- **Make the created indicator the control, and let it show its own state.** With per-unit behaviour, the only clickable surface the mod owns is a component it created itself: clicks on your own components DO arrive as `ComponentLClickUp` (measured on the badge), while right-click and double-click never do. The click carries the component's `Id()` (the badge logs as `zz_auto_badge`, and the click listener already logs every component click), so route an id-prefix check into the *existing* toggle function instead of duplicating the flip — and when the click becomes the control, delete every other binding in the same build (keyboard shortcut, dead right-click path): the user presses the old key, sees it still work, and reports the leftover binding as the bug ("the 8 button still does something"). So make the created component itself the control: visible whenever its ability is on the dial (it is the click target), with its state shown by **swapping the text with `SetText`** — a letter per state (the working build shows `A` = automatic, `M` = manual), one component, which the user confirmed renders *and* changes on the toggle. `SetText` is the only state-display call in this project that has never failed: reach for it first. Colour- and opacity-based state were both tried and came back wrong — **fractional opacity is not a dim look but an invisible one** (`SetOpacity(0.45)` reads back from the engine as `0`, so the idle state never drew and the user reported no badge at all), and a two-component cream/grey pair switched by `SetVisible` never demonstrably switched on screen across two builds. `SetTextColour` does not exist — colour is a layout attribute, so a real runtime recolour would need the unexplored `TextShaderVarsSet`. **Never two visible at once:** two components drawn at one offset render on top of each other, the player sees only the top one, and the top one takes the click — measured, clicking the Deadly Onslaught badge toggled Foe-Seeker — so the pair is switched by visibility, one at a time, never shown together. Affordance and state display at once, with no key binding and no layout work. Keep the armed state per unit AND per ability (`armed[unit:unique_ui_id() .. "|" .. marker]`); identify the selected unit from the unit cards, whose `Id()` equals the unit's `unique_ui_id()` — the pattern `lib_battle_script_unit.lua` itself uses to find a unit's card; and if no unit is selected when the badge is clicked, log that and do nothing rather than guessing which unit was meant — and tell the user in the hand-over that the card click is required, because the engine's own selection at battle start does not register as one. When a reported toggle appears to hit another unit, read the log's `SELECTED unit ui id …` lines first: the click acts on the last unit whose card click registered, so a missing or stale SELECTED line is the first thing to rule out.
- **Generalising a working one-target mod: a table of targets, each keeping its own behaviour.** One entry per ability carrying `marker` (matched against `InterfaceFunction("AbilityKeyForScript")`, so list every id variant explicitly - matching is exact equality against the full list — one ability can ship as a base key plus a DLC-prefixed twin), `trigger` (which condition fires it) and `keys` (every id the readiness call may answer true for). Do not fold the second target into the first one's condition: the existing logic is behaviour the user has already accepted and will name ("it must have its own logic"). Keep the per-ability state (handle, badge, last attempt) in a table indexed by marker, retire any global on/off switch in favour of the per-(unit|ability) armed set, and give the console hooks a target argument — two targets placed from one tuned constant overlap on a dial that shows both, so each needs its own baked numbers (`ox`/`oy` on the table entry, tuned per ability with the marker-taking hooks). Overlap is not merely cosmetic: at one shared offset the created elements stack, and the one on top takes the click, so the player toggles the wrong ability while aiming at the right icon.
- **Perceived latency in a player-operated control tracks the SCAN cadence, not the callback interval.**
  A 50 ms real callback is cheap; what the user feels is whatever you gated on `ui_ticks % N`, because the
  modulo multiplies the wait — a rescan every 4th tick turned a 150 ms tick into ~600 ms on a unit switch,
  reported as "still with delay". Shrink the tick and the modulo together, keep the per-tick body to a few
  calls, and name which part of the leftover delay is the engine's own redraw. The fastest shape that survived this project: derive the state on **every** ui tick from an engine state read (silent when unchanged, one tick-stamped line per real change — `... (tick N)`) with the verbose census on a slow gate, and once clicks are handled synchronously in the event handler, any residual delay is engine **event delivery**, not the mod — triage it from the battle log by counting click-path lines against fast-path adoptions with no click line before shipping another build. The engine's real timer argument is milliseconds in all modes, but dispatch is **UI-update driven with variable resolution** ("can be greater than a model tick (100-200 ms)" — vanilla `lib_timer_manager.lua`), so a registered 50 ms is never a 50 ms felt latency: never quote the registered interval to the user as the response time, and do not trust a file's own stale cadence prose over its registration arguments. Depth — timer semantics, the redraw-lever audit (why `Layout()` is the only lever), and why vanilla controls feel instant while script-drawn state does not: `references/wh3-ui-state-and-latency.md`.
- **Never compute a position across two coordinate spaces - measure it, and stop if nothing moves.**
  `Position()` returns absolute screen coordinates while `SetDockOffset`/docking is relative to the
  parent's anchor, so arithmetic between them lands the element anywhere (a badge meant for an ability
  icon sat in the middle of the info panel, verified by the log: `want(x,y) is(a,b)` with the offset
  growing while `is(a,b)` never changed). Correct by iteration instead: move it, read its own position
  back, apply the error, repeat — **and expect that to fail too**: measured, `Position()` can keep
  reporting a frozen value while the offset climbs past 4000, so the loop steers by a lying
  instrument and the element sits wherever the first placement put it. When it does, delete the loop
  and place the element **once** with the shipped configuration — `CreateComponent` on a plain parent,
  `SetDockingPoint(8)` (bottom-centre), one `SetDockOffset(x, y)`, one parent `Layout()` — leaving the
  two offset numbers as the only knobs, tuned from what the user reports seeing. **A parent that arranges its children itself ignores a per-child
  offset** - a `LayoutEngine` parent positions from the layout, so call the parent's `Layout()` after
  moving something (the shipped recipe does exactly that: `uic_bottom_bar:Layout()` /
  `refresh_layout()` after moving a created button). Treat "N corrections changed nothing" as the
  signature of an offset-owning parent rather than of a wrong number, and report which parent owns the
  position instead of growing the offset forever. **And accept that placement here is tuned, not
  derived.** The community's own positioning tutorial has the reader nudge `SetDockOffset` from a live
dev console "until it looks right", and the one shipped battle-HUD mod admits in its source that the
  constant its offset rests on is "just a guess" — so ship one placement with the offsets as named
  constants, offer the live-console route when the user can install a console mod — expose the numbers
  as **global** functions, **log** every result (a console entry box does not display return values),
  then bake the tuned values in as defaults, with the mode switch made idempotent *and* reversible so
  a repeated call cannot walk the element off screen — and when exactness
  matters put the position in a layout you ship instead of in a call. When the user asks for it, sweep
  the local mods, the wiki and the vanilla files and hand them the ranked ladder **before** building
  again: they choose the order, you implement one by one. Ranked ladder with costs:
  `references/wh3-battle-ui-and-input.md` § placing a created element. **A *derived* position fails too:**
  converting the hand-tuned spot into `tuned − target:Position()` put the badge nowhere near the icon on the
  next build, so ship a fixed offset against the parent's own anchor and let *visibility* do the following.
  Offsets are measured from the parent's dock point, read as **minus = left/up, plus = right/down** — this
  user's own convention; do not assume screen coordinates when reading a reported nudge back.
- **A dial's slot geometry is constant, but WHICH slot an ability occupies is not - read the slot at claim time.** Measured across two
  battles of different factions: the selected unit's ability icons are `button_ability`..`button_ability6`,
  six slots on a fixed circle (~45° apart, radius ~99 px), the same in both battles with only the
  abilities changing. So a badge calibrated by eye onto one icon reaches every other icon by adding that
  icon's measured delta (top slot → 45° slot = +70/+30 px), and per-ability offsets written as
  `base + delta` remain valid only as slot-to-slot geometry - the offset itself comes from the claimed button's Position() read at claim time. Do not hook a hidden look-alike: the `button_order*`
  strip mirrors the same ability keys while measured `visible=false`, and its coordinates are not the
  wheel's. Map, sweep recipe and the full delta table: `references/wh3-battle-ui-and-input.md` § the
  ability HUD map.
- **A single agent's negative on an asset search is usually a wrong pack.** Vanilla UI images and
  layouts ship in *different* packs (`ui/battle ui/ability_icons/<key>.png` is in `ui.pack`; the
  layouts are in `ui3.pack`), so `"<asset> is not in the pack I opened"` is not `"the asset does not
  exist"`. Offer the user a choice of looks only after extracting the real artwork, and check every
  candidate pack before reporting absence.
- **Settle "is this channel ever delivered?" by subscribing to every event name the engine declares,
  not by iterating on listeners.** Parse the table keys out of `script/events.lua` (~400 names),
  register one listener per name with a shared callback, cap lines per event, and give your own
  components an uncapped bypass so noise cannot bury them. One battle then answers it for the whole
  vocabulary, and a sibling event arriving while yours does not is a *constraint*, not a filter bug.
  Recipe and the measured result: `references/wh3-battle-ui-and-input.md` § the firehose test.
- **Put the control case in the instructions you hand the user, not only in the code.** A diagnostic
  that compares "the channel under test" against "a channel known to fire" is worthless if the test
  protocol asks only for the uncertain gesture: the control never happens, the run is inconclusive,
  and the answer costs a second battle. Name the control action in the numbered steps.
- **Deleting a chunk of a Lua file can delete a neighbour's declarations.** A section cut removed
  `local last_seen_tick`/`local stalled_checks` along with the code they were declared under, which
  silently turned them into globals — harmless until the branch that arithmetics them ran, at which
  point the timer died. After removing a block, re-read the surrounding function scope (and let the
  mock call every branch, not just the happy one).
- **Assert every scripted text edit landed.** A `str.replace()` / `re.subn()` that matches nothing
  returns the input unchanged and raises nothing, so a harness or layout "fix" silently does not
  happen while the build looks current — rounds get spent debugging code that was never written.
  Patch with `re.subn(...)` (or `count`) and assert the exact expected number of replacements, then
  print the file size and the count of the thing you added. The same applies to generated code: a
  generator that no-ops produces a plausible file that tests nothing. **Do not hand-compute the
  expected count** - print the occurrences first: an assert expecting 3 where the file legitimately
  holds 2 blocks a *correct* edit and costs a round, and an over-assert is the usual way a rushed
  patch fails. For slice-based edits verify both bounds too: `s.index("\nend\n", start)` matches the
  *next* block's terminator whenever the first candidate sits inside a nested `if`, so the replacement
  swallows a neighbour's `end` and the chunk dies at load (`<eof> expected near 'end'`) - compile
  immediately after any slice edit, before running the build. And when spot-checking an edit (your own or a subagent's), assert on **literal substrings** rather than hand-rolled regexes the file's own data can defeat: a character class excluding `}` (`[^}]*`) cannot span a table entry holding `keys = { ... }`, so a correctly applied edit gets reported as missing - print the block and match the literal text instead. The same trap catches log strings: a line
  assembled at runtime from variables (`.. ", showing the " .. (want and "cream" or "grey") .. " A"`)
  never matches the finished sentence you grep for, so check its parts or its call sites before
  concluding the feature is missing - a failed spot-check is as likely to be the pattern as the code.
- **Author patch/build scripts as files, not as shell heredocs, when the content carries escapes.**
  A heredoc payload passes through the tool-call layer first: a `\n` intended for the target file can
  arrive as a real newline inside the generated Python (unterminated string), and a single backslash
  inside a generated Lua string is an invalid escape that fails the whole chunk at load. Write the
  patch with `write_file`, run it, and keep escape-heavy literals (paths, patterns) out of the patch
  text — or build them with `chr(92)`.
- **Never keep a control the user rejected "as a fallback".** A HUD button the user had already said
  they did not want was left in the build while the replacement route was being proven; it turned up
  in their screenshot and read as the instruction being ignored ("the old button which I said we DO
  NOT WANT is still there"), costing a round of trust. Either remove it, or name it in the same
  message as the build and say why it is still there — silence about a rejected element is read as
  disregard, not as caution.
- **Designing a control for an interaction the engine already reports.** Read the engine's UI event
  table before drawing anything. A control the mod does not need to draw carries none of the
  context, clock and paint hazards above, and cosmetic repair on it can absorb several of the
  user's battles before anyone asks whether the control had to exist.
- **Archive a working build before refactoring it.** Copy the sources and the built pack into
  `releases/<date>_<state>/` and record the pack's md5 beside them — a version the user has just
  called perfect is the fallback that makes a risky refactor (one ability → a table of abilities)
  safe to attempt, and saying so is part of handing it over. **Restoring is a copy, not a rebuild:** put the archived `script/` and `ui/` back over the working tree, install the archived pack directly (it is already built), drop any build-script FILES entry the restored source no longer uses, and re-sync the build script's assertions to the restored design — then confirm the *installed* pack's md5 equals the archived record before telling the user it is back. **Hardening does not travel back with the archive:** a restored build carries the blind spots it had when archived, so hostile-read containment, key-based claims, probes and deferred creation added in the abandoned branch are NOT present. Walk this skill's pitfalls against the restored source before extending it, or the re-extension re-exposes every hazard the archive predates - each as a fresh in-game failure.
- **When a design change removes something the build script asserts, update that assertion in the same change.** A verify step that still demands the construct you deliberately deleted fails the *build* with a message that reads as missing code — the stale check is the bug, not the file it names. Keep assertions on the current design's invariants (the ids/markers that must reach the pack), and compile the build script after editing it: a replacement line pasted at the wrong indentation fails at module level.
- **Refactoring one large mod file: write the spec literally, delegate it, then verify before packing.** Hand a subagent the exact path, the literal table/constants to end up with, "minimal-diff, preserve existing behaviour, leave anything ambiguous and report it", and require the syntax gate plus the mock harness as its proof. Then check both directions yourself with targeted greps — the new constructs present *and* the replaced ones gone (`grep -c` returning 0 for a removed constant), with the tuned constants confirmed unchanged — because a self-report is a claim, and the build is the first thing that should ever trust it. Have the delegate do the **build and install** as part of its task and report the installed pack's md5, then hash the installed pack yourself — a fix whose report ends with "script ready, waiting on the build" has cost the user another round.
- **Reading a repeated `found nothing` scan line as a regression.** The HUD scan runs from load, so the first ~5 s of a battle - before any unit is selected and the dial exists - flood the log with `none of ours found`; pre-regression sessions carry the same lines. Correlate the not-found lines by LINE NUMBER against the session's state lines before diagnosing: in the log that "showed" the broken scan, every scan after the first unit selection found every button, and a byte-diff of the scan region against the known-good backup was identical. A delegated bug report can carry a wrong root cause - report the contradicting evidence instead of inventing a fix for a regression that is not in the file. A header is not a claim: `button: key=...` only means the walk SAW the key - the claim is the separate `^ that one is ours` / `scan: claimed <marker>=true` line, and concluding "the claim fix worked" from a header cost two rounds. Never certify the claim path from the seeing line; if the claim line never printed, the crash sits BEFORE it. Read the LAST session
  block's TAIL plus a per-keyword count table (`scan:`, `found:`, `watching`, `SELECTED`, `badge`,
  `showing the`, `AUTO `, `attempt to`, `deployed`, `skipped`) - a head-only filter prints the
  pre-selection phase and the first lines of a session, which is the least informative part of it.
- **A single throwing component can kill the whole HUD walk, permanently.** Measured: one component made the per-component visit raise (`attempt to compare string with number` — an engine accessor returning a number where the code compared strings), and from that moment **every** scan logged `1 component(s) visited - none of ours found`: the feature reads as absent rather than broken, and nothing built on the scan can ever run. Wrap the per-component visit body in `pcall`, count and log the skips, keep walking the siblings; and guard every comparison in a walk against engine-returned values (`type()`/`tostring()` before `<`, `>`, or a length-style test), because those accessors return numbers, booleans and functions where a string is documented. The signature in a log: one error line, then every later scan at the same tiny visited-count.
- **A walk that collapses to one component WITHOUT an error is an invalid handle, not an empty tree.**
  Log one health line per scan (`children=<n> visits=<n> skipped=<n>`) so the three states stay
  distinguishable: nothing found YET (normal before a unit is selected - the dial does not exist
  until then), handle invalid (a fault), and an error escaping a callback (fatal to what follows).
  Measured: after in-game menu/pause use, hundreds of consecutive scans reported
  `children=invalid` **with a fresh fetch every scan** - re-fetching from `core:get_ui_root()` is
  still mandatory (never cache a handle across scans, the engine rebuilds the HUD), but do not
  assume the cache was the bug: instrument the handle before changing logic, and treat
  "one visit, no error, no skips" as handle/`ChildCount` invalidity rather than an empty tree.
- **Guard the engine's list-shaped calls, and make the retry gate explicit.**
  `bm:get_scriptunits_for_local_players_army()` was measured returning a **boolean** at
  deployment time instead of the army list, so `sunits:count()` raised `attempt to index local
  'sunits' (a boolean value)` inside a callback and that battle tracked zero units (no firing, no
  unit-card mapping, badge clicks refused). pcall it and accept only a value that answers
  `count()`/`item()`; log "not ready yet" and retry. The trap: the failed rebuild left the tracked
  list as an EMPTY TABLE, not nil - so `if tracked == nil then retry` never fires. Gate the retry
  on an explicit flag/count, not on nil-ness. One battle log can carry several independent
  wrong-type failures; fix them one at a time and re-test, do not bundle the diagnoses.
- **Re-shipping a previously failed design: name what is different, in the same message.** The user remembers which approaches already failed and reads a silent repeat as carelessness. State what was measured since, and what now distinguishes the two failure modes on sight — typically a per-transition log line saying which look it was told to show, which is exactly the evidence the failed attempt never produced. Do not re-run a failed test with the same observability and a hopeful explanation.
- **A mock harness's extra ui() ticks can trip the mod's own UI watchdog.** The watchdog fires `NOT repairing it...` after 12 consecutive UI ticks with a frozen model-tick counter - its text contains "pair" and broke an unrelated harness check (`#find("pair") == 0`). When a new scenario adds ui() bursts, interleave `poll(1)` between them and keep each burst under 12 quiet ticks. To prove variant matching, flip the mock button's reported key to an unknown DLC-prefixed variant and count the scan's own claim lines - a claim can only come from the scan's matcher.
- **When a crash hides between two log lines, build a bisect ladder instead of guessing one hypothesis per battle.** Gate each engine-value operation behind a numbered switch constant (`CLAIM_BISECT` = one enabled-op count) and bracket every one: `bisect: step <n> <name> entering` before it, `ok` after, `SKIPPED (disabled)` when off, `FAILED: <err>` when the pcall caught a raise (never a lying `ok`). Cap lines per step per battle (e.g. 40 with a one-off suppression note) or a per-component scan floods the log, and make disabled steps fall the verdict back to "not ours" so the walk keeps running. **Once earlier battles have already proven the walk and its logging safe, ship at FULL level - the crash then names its own step in one battle; one-step-per-battle is only worth paying while the walk itself is still suspect.** Each test battle costs this user a game restart, so a build that touches an untested engine interaction must be self-naming before it ships: bracketed breadcrumbs around every new engine call, so the log's last line IS the diagnosis. The same discipline forces **deferred, stepped creation** for UI components: a claim records only (button reference + pending flag + one line), and the ui tick builds the component in pcall'd steps bracketed as `badge <m> step N <name>` -> `step N ok` / `step N err: ...` - a failed step clears the handle, retries next tick, caps at 3 attempts, then says it is giving up until the dial rebuilds (a re-claim resets the budget). Never create components inside the walk itself.
- **Script-UI visibility has exactly ONE decision point.** Every ui tick recompute
  `shown = (this marker is claimed on the dial)` per element, apply + log on change. A stray
  unconditional `SetVisible(true)` on another path (the letter-refresh path carried one) re-shows
  GHOST badges on dials of units that do not have the ability — they stay on screen and stay
  clickable, toggling state for a unit that cannot use it. Clicks on unclaimed markers get their
  own log line and no action (`click ignored: <marker> is not on this unit's dial`).
- **Selection: the engine has a callback; the cards only ever see a SINGLE selection.** Card
  `CurrentState() == 'selected'` is authoritative for one selected unit, and players can select in
  the world (which fires no component event, so a click-fed tracker goes stale and the next badge
  click toggles the previously card-clicked unit). But measured with a group of ten captains
  box-selected, **no card reported `'selected'`** (every one read `'active'`), and the card-shaped
  helpers (`num_units_selected`, `is_any_unit_selected`, `are_all_units_selected`) read that same
  state, so they are blind to groups too. Maintain the selected set from
  `battle_manager:register_unit_selection_callback(unit, callback)` — per-unit, registered once per
  tracked unit and re-registered for units a later re-list adds — keeping the card sweep as
  fallback/reconciliation, and coalesce the log to one line per resulting set change (never one per
  event: a ten-unit box-select must produce one line). The battle-level
  `battle:register_unit_selection_handler(name)` allows ONE handler and overwrites any previous
  one — vanilla's `lib_bm.lua` keeps a shared dispatcher for that reason. Click events stay a fast
  path only, with a per-click context line (`click: <marker> badge -> selected unit <ui id>`) so a
  mis-attributed toggle is provable from the log. When several selected units share the ability,
  the badge click is checkbox-style (all owners armed -> disarm all, else arm all), touches
  selected owners only, and the letter reads 'A' only while EVERY selected owner is armed — a
  collective 'A' over a mixed selection lies about what will fire. Rules and proof shapes:
  `references/wh3-ui-state-and-latency.md`.
- **Never ship a permanent "scanned and found nothing" flag for units with no matching ability.**
  A loadout can change mid-battle without a new unit appearing (a transformation or mount), and the
  engine's identity read for that is `battle_unit:type()` — the land_units key, where human and
  dragon form are different records; there is no script-level transformation accessor. Watch the
  identity with one cheap pcall'd read per re-check, rescan only when it changes, and keep a slow
  fallback rescan so an unreadable identity degrades to the old behaviour rather than to silence.
  Likewise a re-list of the army (for summons and splits) must be ADDITIVE and identity-based,
  never a wholesale wipe that discards per-unit state, and a created component that is abandoned
  mid-construction must be DESTROYED, not merely nil-ed. Recipe: `references/wh3-unit-lifecycle-and-objects.md`.

 **Where the API-surface facts live.** `references/battle-script-api.md` is the fast lookup index for
 battle scripting: selection (the engine callback vs the card states that cannot see groups), morale
 (the only threshold read is `is_wavering`, and the `morale_is_*` names in the dump are orphaned
 annotations that throw), cooldown/readiness (no per-unit cooldown read exists; the readiness call
 answers true through a refusal), casting (`perform_special_ability` takes a UNIT, the ground-targeted
 `perform_special_ability_ground` is a separate call), identity/existence, and component lifetime
 (`Destroy` is required; `Layout()` is the only redraw-adjacent method). Read it before diving the API
 Read it before diving the API dumps again; the topical files above carry the recipes that use those calls. For the ability-coverage strategy layer: the local dump folder `%LOCALAPPDATA%\Temp\wh3\` holds `unit_spec_abil.tsv` + `unit_abilities.tsv` (3,173 definitions; 1,797 castable once passives/hidden rows are excluded), and the Workshop mod **Autoactivate** (id 3014120667, by Autumnchain) maintains a ~240-entry per-ability trigger taxonomy in its pinned discussion — the community's curated map of which trigger suits which ability. Collated strategy report: `Desktop\WH3_ability_strategy_report.md` (7 activation rules; machinery ladder starts at enemy targeting via `current_target()`). **Roster-wide expansion** (covering hundreds of abilities at once) has its own file: `references/wh3-ability-roster-expansion.md` - the effect-shape-to-trigger decision table, the auto-rule set for classifying an undecided backlog in one sweep, the cast-on-self rule, and the convention for setting a proximity constant inside the ability's real range. Read it before adding more than a handful of abilities: the marginal cost of an approved ability should be a table row, not code.
