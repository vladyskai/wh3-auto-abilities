# Night review brief (2026-11-16/17): shared by every reviewer

Project: a Total War WARHAMMER III battle-script Lua mod that auto-casts special abilities. Each automated ability is an
entry in the ABILITIES table of `mod_source/script/battle/mod/zz_test_deadly_onslaught.lua` (about 24,000 lines; never
read it whole: grep for what you need). Each entry rides a TRIGGER FAMILY (`trigger = "..."`); the family's evaluator is
`FOURTH.evaluate_<family>` (or mapped in the `FOURTH.evaluators = {` table) and its one-line player-facing sentence is in
`FOURTH.TRIGGER_TIP = {`. Read `CLAUDE.md` first (the hard rules: rule 3 the 70% range rule, rule 9 the user designs
triggers, rule 10 "the trigger follows the effect", rule 11 earlier user decisions, section 5 engine facts = the only
battle reads that exist).

Data you can use:
- `docs/WH3_ability_database_master.md`: one section per family (`### \`<family>\``), every ability with its game effect,
  restrictions, range and the trigger text. Grep the section, do not read the whole file.
- `docs/WH3_ability_tracker.md`: the user's past decisions per ability (search the key; quote any "user ruling").
- `docs/WH3_restriction_audit_2026-11-17.md`: game restriction flags the mod may not honour (machine list; many may be
  honoured by a family filter the script did not model: check the evaluator).
- `uv run python tools/fact_sheet_open.py <key> [<key> ...]` from the project root prints an ability's game facts
  (range, uses, recharge, wind-up, phases and stats, invalid target / usage flags, tooltip).

The user's three questions, per ability:
1. Is the family's tooltip sentence a correct "necessary and sufficient" description of when the ability fires once
   armed (every condition the code checks, nothing it does not check, no filler words)? Read the evaluator code to know.
   Also note entry fields that add conditions the family sentence does not mention (`target_class`, `aura_real`,
   standing still, out of melee, target filters, safety distances, ground cast).
2. Is the trigger the best feasible one for this ability's effect? Score 1-5:
   5 = the trigger matches the moment the effect pays off and no better feasible read exists (e.g. Deadly Onslaught on
   the charge or in melee); 4 = good, a small improvement possible; 3 = acceptable but a clearly better feasible trigger
   exists; 2 = often fires at a poor moment or misses the payoff; 1 = wrong or contradicts the effect / a game rule.
   "Feasible" = buildable with the reads in CLAUDE.md section 5 and the existing families. Respect user rulings (quote
   them; a ruled trigger can still be scored, but say "user ruling" and do not argue it away).
3. Does the mod honour every game restriction (invalid target / usage flags, flying only, Lord/Hero only, not in melee,
   health conditions...)? List any that are not honoured and what check would fix it.

Write ONLY your output file (named in your task). Do not edit anything else. No em dashes anywhere (use commas, colons,
parentheses). Output format:

## A. Families
For each family: `### <family>` then: current sentence (quoted); what the code actually requires (short bullets: caster
gates, target choice, bounds, safety, cast form); verdict (EXACT / INCOMPLETE / WRONG + why); proposed sentence
(plain English, starts "When armed, ", one sentence, no filler, at most ~220 characters; if per-entry fields add
conditions, give the clause to append for those entries, e.g. "; Lords and Heroes only").

## B. Abilities
One table per family: | Marker | Ability | Effect (short) | Score | Why (one line) | Better trigger (if score <= 3) | Restriction issue |

## C. Game-mechanics questions
Assumptions you relied on that a player or the game data could confirm or refute (one line each).

Be concise; tables over prose. Finish with a 5-line summary of the most important findings.
