# Trigger design: cadence, validity, simplification

Read before choosing a trigger rule, or before explaining one to the user. These are
design rules; the API facts live in `engine-api-traps.md`.

## Sampling must beat the detection window

The poll cadence and the cast guard are two different numbers. `POLL_MS = 250`; the ~2 s
figure that keeps appearing in logs is the per-pair CAST GUARD. Do not quote one as the
other - calling the poll "2 s" makes every window argument wrong, and it is easy to miss
because both numbers appear in the same log.

Before promising a threshold will be caught, compute the window:

- `window_seconds = threshold_m / closing_speed_mps`
- `step_m = speed_mps * interval_s`

A 0.1 m overlap threshold against a 2.3 m/s walker is a ~0.04 s window, while a 250 ms
poll moves ~0.58 m per check. The window can be stepped over entirely, so the trigger
reads as broken rather than late. If `step_m > threshold_m`, either poll every tick while
armed and a valid target is near, or widen the threshold, and state which was chosen.

Fast polling must be scoped, never global:

- a separate timer, not a change to `POLL_MS`;
- iterates only the affected ability entries, only armed units, only while a valid target
  is inside a proximity radius;
- calls the SAME extracted gate+cast function as the main poll - extract that block once,
  never keep two copies of the gates;
- stamps the guard BEFORE calling the cast;
- proved in the harness by two consecutive fast ticks producing one cast, and by an armed
  ability from another family with an enemy touching it firing nothing.

## Validity by model count

`number_of_men_alive()` is the current model count; `initial_number_of_men()` is the size
the unit started with.

- "Where the mass is" -> CURRENT count: a 20-model block ground down to 8 survivors stops
  being a target, which is what a mass-dependent effect wants.
- "What kind of unit is this" -> INITIAL count: the same block down to one survivor is
  still a 20-model unit and must not be mistaken for a lone character.
- Single entity is `initial_number_of_men() == 1` EXACTLY. Zero models cannot exist, so
  `<= 1` is dead logic and reads as careless.
- A one-model test covers lords and heroes on foot for free and is broader than a
  commander key set, because it also catches single-entity monsters. Mounted lords mostly
  report 1 model; the rows reporting 2 are chariots, which are `com` class and already
  excluded by an infantry filter. Do not stack the commander key set on top of a one-model
  test unless a mounted multi-model commander must be excluded.

## Collapse derived geometry to ONE engine-native measurement

The tempting path is to derive what the engine will not report: bounding boxes from model
count times per-model radius, overlap from point-to-segment distance, lead from projected
velocities. Every layer adds a constant, every constant needs its own field test, and the
dials interact - so the trigger becomes a tuning problem instead of a rule.

Prefer ONE measurement the user can reason about, even when it is coarse - but pick the
right one. `unit_distance` is engine-native yet answers "how far apart are the outlines",
which is the wrong question for "are enough models under the flier": a 20-model block's
fringe touches while its centre is many metres away, so an edge rule drops the bomb on the
fringe, which the user reports as "very few zombies are actually under". Centre distance on
x/z against one stated constant ("within 6 m of the centre") is the rule that survives
every rebuild. Offer the derived version only when the simple rule provably cannot express
what is wanted.

When a rule has been rebuilt three times, stop adding layers: collapse to the smallest
measurement the user can verify from a single log line, and delete the scaffolding. Three
successive air-drop designs (edge threshold, projected path with derived frontage, contact
dwell) each failed on a different axis; the one that held was centre distance plus a
motion-scaled delay.

When a field rule replaces a clever design, DELETE the scaffolding: constants, helpers,
log fields. First grep every helper for callers and state which survive for other
evaluators; then assert in the build that the removed tokens are gone. Dead constants left
in place get re-read by a later session as live tuning knobs. In the spreadsheet and
glossary mark the superseded section RETIRED with the reason rather than deleting the
history.

## Reporting a trigger that does not fire

Diagnose in this order, cheapest first:

1. Is the unit armed? Arming is per unit, not per type.
2. Is it evaluated? The poll iterates every friendly unit and never consults selection.
3. Do the gates hold (in-flight, charge, per-caster serialisation)?
4. Does the candidate filter reject everything? The log's own reason string says so.
5. Does the deciding number ever enter the threshold? Print it exactly.

Prefix every decision line with the unit's ui id: four units of one type turn an
ambiguous report into a whole log dive, and the same-type case is the one that gets
reported.

Print the deciding number EXACTLY inside the decision band. A 5 m band against a 6 m bound
hid the number that decided the cast for an entire round.

When a log is enormous, filter out the heartbeat rows (`hb t=`), the `tick N |` rows and
the `scan done:`/inventory rows before grepping: they contain every ability name and every
unit type in the army, so a naive grep returns thousands of matches and hides the
signal.

## Round cadence: light iterations, full sign-off

Tuning rounds and bookkeeping rounds are different, and the user has approved treating them
differently for iterative work (air-drop tuning is the standing example):

- run ONLY the affected harness section plus the boundary assertion, and SAY so - never
  claim a full-suite green you did not run;
- add only the essential new worlds for the changed behaviour;
- do NOT regenerate or touch the spreadsheet version;
- build + install + verify the 5 ship files, report the md5, and state plainly what remains
  unverified (an unrelated check elsewhere could regress unnoticed until sign-off).

Do the full suite and the workbook version once, at sign-off. The full pass is what makes a
round slow: ~4.9k checks, an 1800-row workbook rebuilt and re-verified per version, an
800 KB source re-read, and release docs. Batch the bookkeeping; do not drop it.

## Explaining a rule to this user

They do not read code fluently and they review before building. When they ask for the
code, print the deciding functions INLINE in the chat - never as a file they have to open -
and explain them line by line in plain words. Then name the exact places the rule can now
fail silently, and stop. Implement only after they approve a shape.

Take their challenges as technical claims and check them before defending: a comparison
that cannot occur below a valid minimum is `==` rather than `<=`; a filter that duplicates
another is removed, not kept "for safety". When they are right, say so in one line and
change the code.

When a number is not exposed by the game (axis, scale, delay, footprint, threshold), state
the current algorithm, name the assumption, lay out the alternatives with their failure
modes, and let them rule. Field-testing every round is their workflow; a quietly baked-in
guess costs a rebuild-retest cycle and looks like a fresh bug.
