# Modding feasibility: is the capability buildable?

Depth for step 6 of the skill. Used when the mod sweep comes up empty (or partial) and
the user asks whether the missing mod *could* be built.

## The two ceilings

State early in any feasibility answer which of these the user is buying into:

| | Data layer | Script layer |
|---|---|---|
| What it is | Rows in the game's own tables | Code run by the engine at runtime |
| Conditions available | Only the condition values / enum lists the engine already ships. **A fixed list is a hard ceiling — you cannot add a value.** | Arbitrary logic the author writes |
| Gives the player | Behaviour baked in before the battle; usually no in-battle toggle | Per-instance toggles, live conditions |
| Cost | Effect values must often be weakened (see below) | Control handover, target selection, per-patch breakage |
| Skills | A database editor, no programming | Real programming |

**Always weaken, never free:** a timed ability converted to "always on" is strictly
stronger, which is why shipping conversions cut effect strength (a third is the number
this genre uses) to compensate. Say so — it is the design price the user inherits.

A third, cheaper route that bypasses both: hand the unit to the engine's battle AI,
which already uses abilities. It gives a working outcome with no conditional control,
and is usually the most actively maintained option in the ecosystem. Present it as
adjacent, not as an answer to the question asked.

## Where to look, in priority order

1. **API reference generated from the engine.** Look for a vendor or community-hosted
   scripting reference whose function list is machine-generated. Anything you cite
   from here is verifiable.
2. **A public dump of the game's extracted data and scripts.** Table names, column
   names, row counts and real example rows come from here — this is what turns "a mod
   could attach a condition" into "this table holds these 571 rows in these two
   columns".
3. **A shipped mod or engine file that already calls the API you plan to use.** The
   module that does the hard part in production is the proof; read its source in the
   dump or the mod's own repo.
4. **The community modding wiki** for the toolchain (pack/archive editor, script
   paths, IDE setup) — and check the tool's repo for a recent commit before
   recommending it.
5. **The in-game test tool** for that title, for the build-and-iterate loop.

## Reading a dump repo

```bash
curl -s "https://api.github.com/repos/<owner>/<repo>/git/trees/<branch>?recursive=1" -o tree.json
python - <<'PY'
import json
d=json.load(open("tree.json",encoding="utf-8"))
for t in d["tree"]:
    if t["path"].startswith("db/") and t["path"].endswith("_tables"):
        print(t["path"])
PY
```

- Check `truncated` in the response; if true, paginate. `/contents/<dir>` returns at
  most 1000 entries and gives no error when it stops — a table past the cut simply
  never appears.
- Confirm a junction/child table exists by requesting its exact path and checking for a
  non-404, **then** fetch its rows. Guessing three plausible names and stopping at the
  first 404 is how a real table gets reported as absent.
- Pull the header row first (`head -1 file.tsv | tr '\t' '\n' | nl`) to name columns
  before quoting any of them.
- Count a distribution rather than asserting one: `cut -f<n> file.tsv | sort | uniq -c`
  turns "abilities can be made passive" into "1,289 rows already are".

## Worked example — Total War: WARHAMMER III ability automation

The shape of a complete answer, for recognition when a future task looks like it:

- **Where code goes:** the engine ships a documented mod loader whose battle branch
  auto-loads `script/battle/mod/` in *every* battle including campaign battles. An
  existing bug-fix mod ships a file on exactly that path — so the hook is proven, and
  no vanilla file needs overwriting.
- **Heartbeat:** a repeating callback with a millisecond interval, plus one-shot
  callbacks, cancellable handles, and battle-phase callbacks. The shipped example polls
  at 50 ms.
- **The action:** `battle_unitcontroller:perform_special_ability(key, target)`, a
  queued variant that starts when the current order finishes (use it — it does not
  replace what the unit was doing), a ground-targeted variant, and an army-level
  `battle_army:use_special_ability(...)`. Cooldown and use-count reset calls exist too.
- **Legality first:** a `can_perform_special_ability(key)` check plus enumerators for
  owned abilities. Issuing an illegal order raises a script error, so the pattern is
  *ask, then fire*.
- **Conditions:** the unit interface exposes health as a fraction, men-alive fraction,
  in-melee, wavering/routing, fatigue state, moving-fast (charging), current target,
  attributes, ammo, flank threats, kills. Every condition the existing mods advertise
  is readable, and script can express combinations the data layer cannot.
- **The toggle UI:** a UI root accessor, component lookup, a create-from-template call,
  a state setter, and a mouse-event reporter — enough to build a button at runtime.
  Several shipping mods have such a button, which settles achievability.
- **The data-layer equivalent:** an ability's `passive` column (1,884 false / 1,289
  true in the shipped table), a junction table of auto-deactivate flags whose rows pair
  a condition with an ability, and a fixed list of condition flags — health above/below
  bands, in-melee, winning/losing melee, morale bands, fatigue bands, movement,
  ammo, kill tiers, proximity. **That the list is shipped rather than open is the whole
  reason the mod authors can only reach the conditions the game already defines.**
- **The one genuine unknown:** a unitcontroller implicitly takes control of a player
  unit when it issues an order, greying out the card. Take/release calls exist so the
  pattern is take → fire → release, but whether that is transparent to the player is an
  in-game test, and the deliverable must say so.

## Reporting shape

Verdict first, then per-route mechanism with named functions/tables, then an explicit
*what cannot be done* section, then effort and toolchain, then sources. The
*what cannot be done* section is the most load-bearing part: it is where the user finds
out that the ideal version (a menu mapping any ability to any condition) is a bigger
project than the mod itself.
