# Roster-wide ability expansion (hundreds of abilities, one build)

For the stage of a battle-mod project where the trigger logic already works and the job becomes
covering a whole roster: every self-combat ability, then every candidate in the game's data
(~1,797 castable once passives and hidden rows are excluded). The design question is NOT "how do
I write another trigger" but "how does one approval cost a table row instead of code".

## Evaluator reuse is the whole game

Route every ability onto an EXISTING evaluator by its effect shape. A round that added 327
abilities rode three existing evaluators with no new logic at all; a new evaluator is justified
only by a genuinely new state read, never by a new ability arriving.

| Effect shape (read from the ability's own phase/stat-effect data) | Trigger family |
|---|---|
| melee attack / melee defence / weapon damage (base or AP) / armour / leadership / resistances / ward / Expert Charge Defence / Immune to Flanking or Psychology | in melee, cast on self |
| heal per second or replenishes hit points, with no melee-specific component | health <= 75%, NO melee gate |
| heal PLUS an armour or melee-defence component | in melee AND health <= 75% |
| Unbreakable / Cannot Die / Stubborn / Hold the Line | wavering (self; self-or-ally when the text reaches allies in range) |
| charge bonus / charge speed / mass / impact damage | charge and in-melee, or charge only when asked |
| negative stats applied TO ENEMIES in range | in melee, cast on self |
| +weapon damage AND +missile damage together | melee self-or-ally in range (the shooting half is unbuildable, see the API cheat sheet) |

Two habits that keep this honest:

- **Cast target is ALWAYS the caster.** An ally-targeted cast makes the engine order the unit to
  walk to the ally, which the user rejected outright. When an effect reaches allies in range the
  TRIGGER looks for a suitable ally, but the cast still targets self.
- **Proximity constants come from the game data, set deliberately inside it.** Read the ability's
  real aura (`unit_spec_abil.tsv`, `effect_range`) and set the trigger constant about 10 m inside
  it (real 35 -> 25), naming the source in a comment. When a field test reports it fired too early,
  TIGHTEN the constant; do not add range math. Range triggers share one safety shape: closest
  eligible ally within the constant, re-check the gap immediately before the cast, skip on drift.
- Give every evaluator its own distinct log reason string, so a battle log names which rule fired.

## Classifying an undecided backlog (the volume escalation)

Per-item questions stop being the instrument somewhere in the low hundreds of candidates. The move
that worked: widen the standing auto-rules, then classify the ENTIRE backlog programmatically in
one sweep and ask only what is genuinely ambiguous.

- **R1 positive-only buffs**, self or allies, with no negative and no friendly-fire component:
  auto-accept, trigger chosen by the table above.
- **R2 enemy debuffs** (negative stats applied to enemies in range): auto-accept as in-melee self.
- **R3 auto-exclude with a reason**: vortex, bombardment/explosive, summon, pure movement or
  speed-only, ground-target-only, and anything whose effect text cannot be sourced after one
  genuine attempt.
- **R4 flag for the user** (never auto-decide): applies Rampage, damages or kills friendly units,
  mutually exclusive, army-bar, stealth/escape/stalk/unspottable, transform/shapechange, needs a
  read that does not exist, or whose net effect is mixed positive-and-negative.

Classify from the game's own tables (effect phases plus engine flags), never from prose or a wiki
line alone: the mechanical numbers line is COMPOSED at display time from the phase/stat-effect
tables plus the attribute tables and is not stored as one string. Expect roughly a third accept, a
third exclude, a third flagged, with the flagged block dominated by area damage that can catch your
own troops. Report the FLAGGED block first, since it is the user's entire remaining queue, and emit
one print-friendly report with a count table plus an appendix per bucket so every auto-decision is
visible and vetoable in one pass.

**A mechanical classifier must not contradict a standing user rule.** A sweep re-queued a whole
family the user had already ordered skipped; the standing rule wins, and the conflict and its
resolution get reported rather than silently applied.

## Standing decisions for this class of work (apply without asking)

- Army-bar abilities: skipped entirely (they have no per-unit control to attach to).
- Mutually exclusive abilities: auto-rejected, never presented.
- Vortex / explosion / summon / pure movement / pure ranged: excluded.
- Risky-but-useful abilities stay automatable but default to manual; the per-ability toggle makes
  the risk opt-in rather than a reason to withhold coverage.
- No baked stat values anywhere, only live reads (stat numbers are unreadable for non-selected
  units and stale the moment an effect lands).
- One-shot and consumable items get a spend-window rule (a state threshold such as health below a
  level) rather than the roster's default action moment.

## The decision queue is the bottleneck, not the build

A build round costs minutes of machine time; a decision round costs the user a sitting. So: keep
one tracker file as the store of record (implemented / ordered candidates with decision lines /
inventory with a status column / header legend of the standing rules / decision log quoting the
user's reasoning), record each batch of answers in the SAME turn it was answered, and treat the
conversation as scratch space that a compaction can eat. Batch mechanics live in the
`batched-decision-workflows` skill; the trigger material above is the part that is specific to this
game.
