# Cast orders, gates and aiming

Lessons from the bombardment / air-drop rounds. Read before writing any cast or
enemy-targeting trigger.

## One special ability in flight per unit

A `perform_special_ability` call issues an ORDER and replaces the unit's current one.
Re-issuing a cast 2 s into a 3 s wind-up therefore cancels the effect while still
deducting the use: the user sees a charge burnt and nothing land.

Guard it twice:

- per-ability in-flight hold of wind-up + 2 s (generate the wind-up per key from
  `unit_spec_abil`; entries with no declared wind-up keep the plain 2 s guard);
- per-unit serialisation window of the same length (min 2.5 s) after any successful
  cast, and a repeat of the SAME ability must NOT extend it, or one trigger starves
  the other forever.

The symptom to recognise: two abilities on one caster both fire, the second wins, the
first's effect never appears and its next attempt is a full recharge later.

## Charges

Multi-use abilities answer `can_perform=true` with an EMPTY charge pool; the engine only
refuses single-use rows. A per-pair charge gate holding `recharge_time` after a
successful cast is the only brake for multi-use rows, and it is not optional: without it
the mod spends all charges the moment the trigger is true and again on every recharge.

## Distance and overlap

`unit_distance` is bounding-box EDGE-to-edge, so it cannot answer "is A under B". Two
large formations read a 0.5 m edge gap while their centres are 15 m apart, which is how
a 1 m "overlap" test fires while the flier is still beside the enemy.

- Use centre distance on X/Z (`battle_vector:distance_xz`), never X/Y.
- Height must never enter the test: a 40 m flier would read 40 m from the unit beneath it.
- No radius, bounding box or footprint read exists on `battle_unit` (106 functions
  checked). `ordered_width()` is one axis of the ORDERED formation, not the live one.
  So any overlap threshold is a stated constant, not a game value, and the blast radius
  is not in the extracted tables either.

## Motion

Scalar reads exist: `is_moving`, `is_moving_fast`, `slow_speed`, `fast_speed` (m/s).
Heading comes from the difference between `position()` and `ordered_position()`; that
function returns the CURRENT point for an attacking unit, so treat it as stationary and
log which source was used. Never invent motion when `is_moving()` is false.

Exact API names, confirmed against the dump: `ordered_position()` and `bearing()`.
`position_ordered()` and `orientation()` do not exist. `bearing()`'s degree-to-axis
convention is undocumented - it is the one unverified step in the chain.

## Class reads

`battle_unit:is_infantry()` and `is_currently_flying()` are real reads. "Commander" has
no predicate: derive a key set (`land_units.class == "com"` union `main_units.caste`
lord/hero), match by exact whole key against `type()`, fall back to `unit_class()`,
and FAIL CLOSED when unreadable. The same derived-set method answers any other
target-class gate (infantry, monster, construct).

## Aiming at moving targets

Project both bodies forward by a fall delay and compare the PROJECTED separation to the
bound. Split the projection into separate dials so a field report can be attributed to
one term:

- caster lead and caster delay (scaling only the caster's velocity term);
- enemy lead (scaling only the enemy's velocity term);
- shared fall delay.

A full fall-time of lead is almost always too much in one of the two directions: a
moving flier chasing a standing target fires early, and a hovering bomber over a
crossing column never fires at all because the enemy's projected centre is carried past
it. Change ONE dial per field test and print all of them on the decision line.

Ordnance momentum: assume it does NOT inherit the caster's velocity (impact straight
down from the release position) and expose a single flag for the other case rather than
baking either in.

## Diagnostics that pay for themselves

- Prefix every decision line with the unit's ui id. Four units of one type otherwise
  produce indistinguishable lines and one ambiguous report costs a whole log dive.
- Print EXACT distances inside the decision band; coarse bands hide the number that
  decides the cast.
- Log the reason string when a velocity or a read falls back to zero, so a silent stall
  is attributable in one pass.
- Put a one-screen tuning table (symptom -> dial -> direction) in the release notes, the
  tracker and the spreadsheet glossary; the user tunes one dial per test.

## Before building a rule, and how to explain it

Read `references/trigger-design-and-review.md` before choosing a trigger rule: poll cadence
versus detection window, model-count validity, when to collapse derived geometry to one
engine-native comparison, and the review loop. In short - when the user asks for the code,
print the deciding functions inline in the chat, explain them line by line in plain words,
name the places the rule can now fail silently, and implement nothing until they approve.
