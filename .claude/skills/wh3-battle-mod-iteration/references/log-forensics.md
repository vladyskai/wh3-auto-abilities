# Reading the battle runtime log without drowning in it

The log is append-only across every battle and grows past 700k lines, so a naive `grep`
for an ability name returns thousands of useless hits and looks like evidence. Work in this
order.

## 1. Bound the search to one battle

Find the last session boundary (the mod's battle-start line) and read forward from there.
A decision from last week's battle sitting next to this week's reads like a live bug.

## 2. Strip the lines that contain every ability name

These flood any name-based grep - drop them FIRST, by matching the text after the timestamp
prefix (`line.split("] ", 1)[-1]`):

- `hb t=` heartbeats - they carry the full `auto=` list, i.e. every ability in the mod.
- `tick N |` lines - same, one per poll.
- `scan done: ... component(s) visited` UI scans and the `unit '...' ui id ...` inventory
  dumps.

Then grep the remaining lines for the mod's own decision vocabulary: `ATTEMPT`, `reason:`,
`target:`, `watch:`, `pre-cast re-check`, `SKIPPED`, `charge gate`, `cast gate`, `armed=ON`.

## 3. Count presence and absence as evidence

An absence is stronger than a narrative. `ATTEMPT sky_junk_bomb = 1`, `gate lines = 0`,
`airborne check hits = 0`, `armed=ON` for all four units - each one deletes a hypothesis in
a line. Establish which hypotheses the log CAN refute before theorising about the ones it
cannot.

## 4. Write log lines that answer questions you have not asked yet

Every rule here came from a round where the log could not settle its own question:

- **Name the unit on every decision line** (ui id + type). Four units of one type with
  unlabelled lines are indistinguishable, and "which one fired" becomes a log dive.
- **Print exact distances anywhere near the threshold.** A `~5 m` band against a `6 m`
  bound hides the number that decides the cast. Band only far out (>30 m); print one
  decimal near the line.
- **Print the source of every derived value** - `src=ordered`, `src=stationary`,
  `radius=none`. A fail-closed zero and a genuine zero look identical otherwise, and the
  "why did it not fire" question lands with no answer in the log.
- **Pre-cast re-checks must call the SAME helper as the picker.** A re-implementation
  drifts and silently gates on a different number than the one logged at selection.
- **Log the constants in force** (`bound=6m delay=1.50s lead=0.50`), so a field report can
  be turned into a single-number correction instead of a re-diagnosis.

## 5. Ask for one firing line and one non-firing line

The pair localises the error to a term: the non-firing line shows the gap that failed, the
firing line shows the gap that passed, and the difference between them is the correction.
Asking for "the log" gets a 700k-line file.
