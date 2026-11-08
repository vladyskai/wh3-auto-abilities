# Engine and API traps found in the field

Check these before writing any trigger, counter or distance test. Each one has already
caused a silent field failure in this project.

## Vector axes: the ground plane is X/Z, not X/Y

`battle_vector`: `get_x()` = east-west, `get_y()` = **HEIGHT above the water plane**,
`get_z()` = north-south. `distance()` is 3D; `distance_xz()` is "disregarding any height
difference".

For every horizontal test use `position()` ("centre position of the main squad") plus
`distance_xz()`, with `sqrt(dx*dx + dz*dz)` as the fallback. An x/y "horizontal" read
made a 40 m-altitude flier look 40 m away from the unit directly beneath it.

## HealthPercent is a 0..1 fraction

`common.get_context_value("CcoBattleUnit", id, "HealthPercent")` returns **0..1**, not
0-100. So `hp < 75` is true for a full-health unit and `hp < 20` is true for everything.
The log signature of the bug is pick lines reading only `0 %` or `1 %`, never 2-19 %.

Route ALL health reads through one helper that prefers `unary_hitpoints()` and scales any
0..1 value by 100. Two documented failures came from this: the ≤75 % heal family firing
at any health, and the Eye of Khorne finisher offering healthy targets.

## unit_distance is edge-to-edge, and there is no radius read

`battle_unit:unit_distance()` measures the gap between bounding-box OUTLINES. No
radius/footprint read exists: `battle_unit` has 106 functions and none is
`radius`, `unit_radius`, `bounding_box`, `bbox`, `size`, `footprint`. The near-misses are
not usable:

- `ordered_width()` - one axis, and it is the ORDERED formation, not the live one.
- `script_unit:get_cached_width()` - same, behind `cache_location()`, zero vanilla calls.
- `script_units:radius()` - a COLLECTION's spread around its mean centre.
- `battle_entities.radius` - one MODEL's collision radius, not the unit.

Two large formations can have outlines 0.5 m apart while their centres are 15 m apart, so
an edge bound of 1 m fires while a flier is still beside the target, not over it.

For any "is X under Y" test: centre x/z distance against a documented constant, logging
both positions, the threshold and (when available) the radii sum.

### Deriving a frontage when a bare centre test is too blunt

A raw centre bound under-triggers on wide blocks and over-triggers on narrow ones. Derive a
half-frontage instead:

    ordered_width()/2    when it is a sane positive number inside the clamp range
    else ceil(men / RANKS) * MODEL_RADIUS        (RANKS 2, MODEL_RADIUS 0.6 m)
    clamp 1..12 m; 0 for a single model; 0 when unreadable

`battle_entities.radius` is the modal per-model collision radius over the infantry rows
(0.6 m, median 0.7), so 20 models over two ranks is about 6 m - which matches what a
zombie block measures on screen. Only trust `ordered_width()` when it is live: for a unit
with no move order it reports the ORDERED formation, and a small valid number then clamps
to the floor and gives almost no credit, which reads in play as "the credit never applies".

## Counting soldiers: current count vs initial count

Two different questions, two different reads - picking the wrong one silently breaks a
threshold:

- **How much mass is there NOW** -> `number_of_men_alive()`. A block ground down to 8
  survivors is no longer a mass worth bombing, so a `> N` validity rule uses this one.
- **Is this a single entity** -> `initial_number_of_men() == 1`, exact equality. Zero models
  cannot exist, so `<= 1` hides intent. Use the INITIAL count so a 20-model unit reduced to
  one survivor is still a 20-model unit, not a lord.

An unreadable `initial_number_of_men()` must skip the candidate (fail closed) - and know
that this is a TOTAL-SILENCE failure mode: if the read is unreliable for some class, every
candidate is skipped and the trigger never fires while the log fills with skip lines.

A one-model test usually subsumes the lord/hero case, so do not stack a commander key set on
top of it. Over the mounted lord rows, 432 of 504 read 1 model; the 50 that read 2 are all
CHARIOTS, and every character row with 2+ models is `land_units.class = com` - a class an
infantry filter drops anyway. Keep the 1,409-key commander set for evaluators that have no
infantry filter and no model-count rule.

## No engine helper for area containment

Nothing exposes point-in-area, unit-over-unit, `is_in_area`, `point_in_circle` or
`is_over`. The engine evaluates `flying_over_platform`, `flying_over_invalid_location` and
`enemies_in_intercept_range` internally, but only as ability-usage FLAGS script can SET,
never read.

## perform_special_ability issues an ORDER and a second call REPLACES it

The docs are explicit that queued orders start when the current order completes - i.e.
the plain call replaces the current one. Field evidence: Moondial and Wraith Storm on one
caster, 0.25 s apart, **both controller calls accepted**, the first effect never landed
while its use was spent, and the next Moondial attempt came 119 s later on its 120 s
recharge.

Two gates are needed, and they do different jobs:

1. **Per-ability, after a successful cast:** hold for `wind_up_time + 2 s` (never less than
the plain guard). Nurgling Tide re-issued every 2 s into a 3 s wind-up and cancelled
itself 55 times; the same rule fixed a 3 s wind-up ability from 3 casts in 19 polls to 1.
2. **Per-caster:** while any ability on that unit is resolving, issue no DIFFERENT ability
on it (window = wind-up + 2 s, min 2.5 s). A same-ability repeat must NOT extend this
window or one trigger starves the other.

## Multi-use abilities do not refuse when empty

`can_perform_special_ability` returns `true` for a multi-use ability whose charge pool is
empty (single-use rows DO refuse). Without a charge gate the mod spends every charge the
moment its trigger is satisfied, then again each time the pool refills. Hold the pair for
the ability's own `recharge_time` after a successful cast.

## Reads that do work for lead and prediction

- `ordered_position()` - the point the unit was ordered to. NOT `position_ordered()`.
- `bearing()` - facing in degrees. NOT `orientation()`.
- `is_moving()`, `is_moving_fast()`.
- `slow_speed()`, `fast_speed()` - m/s.

There is no velocity VECTOR anywhere, so rebuild it: `speed * normalise(ordered_position -
position)`, using `fast_speed()` when `is_moving_fast()`, else `slow_speed()`.

Verify every method name against the dump before coding, not from memory: two names written
from memory (`position_ordered`, `orientation`) simply did not exist and cost a round. The
dump's own doc text is the contract - it states scale and axes in words ("Returns the
centre position of the main squad", "disregarding any height difference"), and that sentence
settles more arguments than any field test.

Fail closed rather than inventing motion. `ordered_position()` returns the CURRENT point for
a unit that is ATTACKING, so an engaged enemy has no heading; a destination under 0.5 m away
is degenerate. Return ZERO velocity with a named source (`stationary`, `no-heading`,
`no-speed`, `moving-unreadable`) and log which, so a silent trigger is diagnosable. Keep
`bearing()` as a caster-only fallback while moving - its degree-to-axis convention is
undocumented and is the one link in the chain not verified against a real value.

When a decision hangs on a read whose SEMANTICS you are assuming, log the RAW returns, not
only the derived number: the moving flags, both speeds, both position pairs and the
computed heading length. Identical `pos` and `ordered` pairs with `|h|=0.0` prove the read
returns the current point; a plausible offset proves otherwise. One line per contact
episode settles an argument the user would otherwise have to field-test twice.

## Start simple: the plain rule beat the machinery

Before reaching for the projection and delay machinery below, know how it ended for the
air-drop family. Five successive designs were built, field-tested and discarded: velocity
projection with four lead dials, a path-segment test with derived frontage, a fixed dwell, a
velocity-scaled dwell, and then nothing at all. What the user kept was the simplest thing that
worked:

    candidate = alive and number_of_men_alive() > 10
    fire when centre-to-centre x/z distance < 6 m   (no delay, no projection, no fallback)

Each discarded layer added a failure mode that the next field test found: extra dials to tune,
state to purge, a fallback that fired late, and a crossing target whose projection was largest
exactly when it was underneath. The mass threshold did the work the frontage maths was trying
to do.

So: build the plain single-comparison rule first, field-test it, and add a dial only when a
report names a term the plain rule cannot express. When a design is replaced, DELETE the
machinery and mark it RETIRED in the sheet with a one-line reason - leftover unused helpers
are what a later round mistakes for the current design.

The sections below are still the reference for what each layer does and why it failed, not a
recommended build order.

## Delayed effects: project BOTH bodies, and give each side its own dial

For anything with a delivery delay (air-drop ordnance, ~1-2 s, engine-side with no data
row), comparing a projected target against the caster's CURRENT position is wrong: the
caster travels during the delay too. Project both and compare the projected points.

Keep the two sides on SEPARATE knobs. One passing field test proves only the term it
exercised:

- stationary caster + stationary target passing -> says nothing about either lead term.
- caster moving, target still, dropping EARLY -> the caster term over-leads. Lower the
  caster lead (1.0 -> 0.5 -> 0.3 -> 0.0); do not touch the target term.
- caster parked, column walking THROUGH beneath it, never firing -> the target term
  over-leads. A crossing target's projection carries it several metres PAST the bomber, so
  the projected gap is LARGEST exactly when the target is underneath, and a tight bound is
  never satisfied.
- early even with both parked -> the shared delay itself is too long.

A crosser is the diagnostic case: it separates "under me now" from "under me at impact"
better than any stationary pair. Widen the bound per ability to make a crosser fire and you
re-open the early-drop case that the bound was tuned to fix - fix the projection instead.

### "It fires too soon, add a delay" means WAIT, not LEAD

That sentence is genuinely two-way: fire a second BEFORE contact (a lead) or hold a second
AFTER contact (a dwell). State your reading in the reply, or ask - building the wrong one
costs a whole rebuild round. "Fires too soon" on its own means the cast is consumed before
the target is properly under, i.e. the trigger needs to hold longer.

A dwell is per pair, not per ability:

- stamp the contact when the pair first enters the threshold, fire only once the stamped
  delay has elapsed, cancel on separation and re-stamp on re-contact;
- run the dwell clock on the POLL tick, never on the fast-pass counter: fast ticks add
  evaluations but no time, so a missed poll can only make the cast later, never early - say
  this when it matters, because it is the guarantee that stops "it fired early" reports;
- a strict dwell can NEVER fire on a target that crosses in less than the dwell. Add a
  minimum-contact fallback that fires on the separation evaluation once the contact lasted
  at least a stated floor, and log every cancelled contact with its duration so the dwell
  can be tuned down from real numbers instead of guessed;
- quantise expectations to the poll grid: on the 250 ms clock a computed 0.29 s lands at
  0.50 s and 1.71 s at 1.75 s. State that before the user reports it as a rounding bug.

### When the wait itself depends on the target's motion

A fixed delay cannot serve a target that closes and a target that flees. Scale it by the
cosine between the enemy's velocity and the axis from enemy to caster:

    delay = MID - SWING * cos      (MID 1.0 s, SWING 1.0 s -> 0 / 1 / 2 s)

cos +1 closing fires at once, 0 perpendicular or stationary at MID, -1 receding at
MID + SWING, with smooth interpolation in between. It needs a direction, not an absolute
speed. Measure it ONCE at first contact and keep it for that whole contact - a target that
turns mid-approach keeps the delay it was stamped with - and re-measure only on
re-contact. Unknown heading (attacking unit, no `ordered_position`) falls back to MID with
the reason logged.

Vanilla does not validate air-drop targeting in Lua at all: the ordnance spawns
engine-side at the caster and script only decides when. A drop threshold is therefore the
mod's own dial, not a copy of engine logic.

## Before rebuilding on a guessed value

When a trigger depends on a number the game does not expose (axes, scale, delivery delay,
footprint, threshold), do not quietly bake in a guess. State the current algorithm step by
step, name the assumption, lay out the alternatives with their failure modes, and let the
user rule before you build. They field-test every round and want the choice; a guessed
scale, plane or lead costs a whole rebuild-retest cycle and looks like a new bug.

## Enemy enumeration: the default call sees only the main army

`get_scriptunits_for_main_enemy_army_to_local_player()` is literally
`get_scriptunits_for_army(non_player_alliance, 1)` - army index ONE. Reinforcements are
invisible to it, so any enemy-targeting trigger built on it silently ignores reinforcing
waves arriving mid-battle.

Walk the alliances when reinforcements matter:

    bm:alliances():item(a):armies():item(n):units()
    army:get_reinforcement_units(t), army:num_reinforcement_units()
    -- flat form: bm:num_alliances() -> bm:num_armies_in_alliance(i) -> bm:get_scriptunits_for_army(i, j, k)

## Classify abilities from the data, not from hand-kept key lists

`unit_special_abilities.ai_usage` carries CA's own label for all 3,173 abilities
(`aoe_bombardment`, `vortex_breath`, `healing_area`, `hex_melee`, ...), next to
`target_ground`, `vortex`, `bombardment` and `target_intercept_range`. Derive trigger
families and cast forms from those columns rather than maintaining `ground_keys`-style hand
lists: a hand list drifts from the data and needs re-auditing every round.

Negative evidence worth keeping: the engine's AI scoring vocabulary includes
`bool_shooting` and `bool_charging_at_me`, confirming that "is this unit firing" exists only
AI-side and is never a battle Lua read. The scoring tables are ordinary DB rows and can be
dumped; they show what the ENGINE values - friendly units inside a blast area are weighted
~6.0 against 2-3.0 for enemies - which is a fair sanity check on a cast point even when the
mod does not imitate the solver.

## Counting: abilities vs keys

Every implemented entry can carry several keys (a base row plus `_mp`, `_snikch`,
`_upgraded`, `_thanquol`, and so on), so "30 abilities done" can be 31-34 keys.
Reconcile both numbers against the tracker before reporting progress, and say which unit
the count is in - an off-by-four "remaining" list reads as a bug in the work rather than in
the arithmetic.

