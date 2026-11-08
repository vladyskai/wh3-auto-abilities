# WARHAMMER III — A-priori category-exclusion rules: review against the CURRENT capability set

**Date:** 2026-10-16 · **Scope:** policy review only. Nothing in the tracker's statuses, the mod, the
annotated copy or any pack was changed; nothing was built. This report is the only artifact written.

**What this is.** The project did not only decide abilities one at a time — it applied a series of
**category rules** that removed whole families of abilities *before* any individual consideration
(spells, army-bar, the friendly-fire families, summons, movement-only, stealth/escape, ammo-dependent,
ground-only, magic-scope, unsourceable effect text, mutual exclusivity, transform, and so on). This
report enumerates **every such rule**, each with the five fields the user asked for: the rule as
stated and when; how many abilities it removes and what they otherwise are; what justified it; whether
it is **still valid against the capability set we have today**; and what re-opening it would take, with
the risks.

**Data sources (read-only):**
- `docs/WH3_ability_tracker.md` — the legend (§ standing rules 1–15), §3a/§3b/§3c inventory, §10 decision logs.
- `docs/WH3_ability_database_master.md` §3 — the 1,192 excluded/skipped/rejected/impossible rows, grouped
  by decision family. **Counts in this report are taken directly from those group headings and verified
  row-by-row; they sum to exactly 1,192.**
- `docs/WH3_remaining_triage.md` — the 347 flagged items and the engine-limit statements that justified group A.
- `docs/WH3_auto_classification_report.md` — the 2026-10-09 sweep that established rules R1–R4.
- `docs/WH3_audit_report.md` — Classes A–H and the 418 clean entries.
- `docs/WH3_auto_ability_mod_feasibility.md`, `docs/WH3_enemy_targeting_research.md`,
  `docs/WH3_distance_and_range_research.md` — the mechanism record.
- The battle-script API dump `%LOCALAPPDATA%\Temp\wh3\battle_unit.lua`, `script_unit.lua` (re-read for the ammo question).

---

## The current capability set (what changed after these rules were written)

Everything in the "STILL VALID?" column is judged against **this**, not the set in force when each rule was written:

| # | Capability now proven | Evidence |
|---|---|---|
| C1 | **Enemy-unit targeting works from scripts.** Enumerate enemies via `battle_manager:get_scriptunits_for_main_enemy_army_to_local_player()` (coll `:count()`/`:item(i)` → `.unit`/`.uc`) and cast at them with **fresh handles**: `caster_uc:perform_special_ability(key, enemy_battle_unit)`. **89 entries / 97 keys ship** on `enemy_engaged_or_shot` (+ Accusation). | tracker harness 97; master §2 |
| C2 | **Enemy-GROUND cast works:** `caster_uc:perform_special_ability_ground(key, enemy_unit:position(), 0, 0)`. **9 entries ship** on `enemy_ground_area`. | master §2; skill `wh3-battle-mod-iteration` |
| C3 | **The own-feet ground form ships** (`FOURTH.ground_keys`). | tracker legend; audit Class C |
| C4 | **The real cast range is `target_intercept_range`** (the reach the engine walks the caster), and the offer test uses **that** constant only — **never** the engine's `unit_in_range`, which is looser and caused the Accusation walk-order bug. | tracker rule 15; `WH3_distance_and_range_research.md` |
| C5 | **The 70 % rule bounds every trigger:** `trigger range = floor(0.70 × real range)`, ruled absolute ("No exceptions"). | tracker rule 15 |
| C6 | **Invalid-target restriction flags are extractable** — 422 abilities carry one (`unit_is_not_squig`, `unit_is_not_slayer`, `unit_is_not_commander_class` ×24, `unit_is_not_hellforged`, …). Class/type gating is now possible. | master §1.4; `WH3_classC_targettype_check.md` |
| C7 | **Ally targeting works:** self-or-ally, lowest-health ally, highest-HP ally, and class-gated ally (beast / monster / war machine / construct / Hell-Forged / missile-capable / morale-broken). | master §2 (14 ally families) |
| C8 | **Triggers that did not exist when some rules were written now ship:** `charge_only`, `wavering_self`, `wavering_self_or_ally`, `charge_or_wavering`, `wavering_ally_range`, `tired`, `metallurgy_melee`. | tracker harness 90 |
| C9 | **Two ammo reads exist on `battle_unit`:** `ammo_left()` ("Returns the remaining ammunition count") and `starting_ammo()` ("the amount of ammunition the unit started the battle with"). A **unary ammo fraction is therefore computable** = `ammo_left()/starting_ammo()`. | API dump `battle_unit.lua` L338/L342 (re-verified for this review) |
| C10 | **Still absent:** no per-unit *is-firing / is-shooting* read; no per-unit *cooldown / readiness* read (only `can_perform_special_ability`, which answers `true` while the engine refuses); no *enemy-spell-cast* event; no *area-contents* read (what units stand inside a cone / blast / vortex patch). | tracker §10; triage §"Engine limits" |

**The mis-hit.** Two justifications in particular have been overtaken: **"no enemy-unit read"** (the
single largest engine-limit wall — C1 refutes it) and **"no ammo-low read"** (C9 refutes it). A third,
**"abilities that target the ground only"**, is refuted by C2/C3.

---

## Table 1 — every a-priori category rule at a glance

Legend for the **Split** columns: *self/ally* = the ability's own data declares self or friends as a
target (rides an existing own/ally evaluator today); *enemy-unit* = declares enemies; *ground* =
declares ground. *Other* = no targeting flags (self-centred / none). Counts verified to sum to 1,192.

| # | Rule (family) | Origin / when | Abilities | self/ally | enemy-unit | ground | other | Justification recorded | Still valid? |
|---|---|---|---:|---:|---:|---:|---:|---|:--:|
| 1 | **Spells & cataclysms** | "earlier standing decision" pre-block-1; log §3c; block 4 instance 2026-10-08 | **434** | 142 | 268 | 23 | 1 | out of scope (winds-of-magic resource abilities) | **policy — stands** |
| 2 | **Army-bar abilities** | rule 10, 2026-10-08 | **117** | 35 | 50 | 25 | 7 | user instruction; no unit junction | **policy — stands** |
| 3 | **No enemy-unit read** | triage 2026-10-09 | **76** | 0 | 76 | 0 | 0 | engine limit: an enemy unit has no card/id | **✗ REFUTED (C1)** |
| 4 | **Summons** | R3, 2026-10-09 (+ `summon/transform` 4) | **78** | 53 | 15 | 7 | 3 | spawns a unit; outcome not evaluable | **sound (outcome)** |
| 5 | **Vortex / wandering wind** | family decision 2026-10-09 (+ `vortex` 29 + `unsuitable: vortex` 17) | **116** | 6 | 55 | 15 | 40 | travels its own path; FF guaranteed, unaimable | **sound** |
| 6 | **Bombardment / ground artillery** | family decision 2026-10-09 (+ `unsuitable: bombardment/ranged` 3) | **66** | 0 | 51 | 9 | 6 | "placing it usefully needs an enemy read the engine does not have" | **✗ REFUTED (C1/C2)** |
| 7 | **Placed / static area damage** | family decision 2026-10-09 | **42** | 1 | 36 | 5 | 0 | "no enemy read to place it" + self-centred field hits friendlies | **partly REFUTED (C1/C2)** |
| 8 | **Breath / cone damage** | family decision 2026-10-09 (+ `explosive/breath attack` 29) | **59** | 1 | 29 | 3 | 26 | cone sweeps friendlies; no way to check the arc | **sound (no arc read, C10)** |
| 9 | **Explosive projectile** | R3, 2026-10-09 | **52** | 0 | 52 | 0 | 0 | explosive = area damage → FF | **partly re-openable** |
| 10 | **Own-troop-damage AoE** | family decision 2026-10-09 | **26** | 0 | 11 | 6 | 9 | damages your own troops by design | **sound** |
| 11 | **Flanking / ambush (stealth)** | family decision 2026-10-09 | **7** | 0 | 0 | 0 | 7 | stealth/escape family the user already rejected | **sound (policy)** |
| 12 | **Movement-only** | R3 / collection-time | **6** | 1 | 0 | 2 | 3 | pure movement with no combat effect | **sound** |
| 13 | **Stealth / escape** | rule 5; questionnaire | **13** | 6 | 0 | 2 | 5 | "tactically relevant and must be chosen by player" | **sound (policy)** |
| 14 | **Ammo-dependent (ammo replenish)** | triage §3 item 4/6/7, 2026-10-09 | **3** | 3 | 0 | 0 | 0 | "needs an ammo-low read the engine lacks" | **✗ REFUTED (C9)** |
| 15 | **Ground-target-only** | R3, 2026-10-09 (+ `enemy-ground placement` 1) | **15** | 0 | 9 | 5 | 1 | "abilities that target the ground only" | **✗ REFUTED (C2/C3)** |
| 16 | **Magic scope** | block 4, 2026-10-08 (+ `magic scope + self-damage`) | **2** | 0 | 0 | 0 | 2 | magic-resource cost (+ self-damage) | **sound** |
| 17 | **Unsourceable effect text** | R3, 2026-10-09 | **26** | 1 | 4 | 0 | 21 | "empty/unknown after one genuine sourcing attempt" | **✗ REFUTED (fresh extraction)** |
| 18 | **Mutual exclusivity** | rules 3 & 8; questionnaire | **5** | 0 | 0 | 0 | 5 | mutually exclusive → player decides | **sound** |
| 19 | **Transform / shapechange** | triage 2026-10-09 | **11** | 1 | 0 | 0 | 10 | engine cannot swap unit forms | **sound (engine)** |
| 20 | **Drawback** | rule 2; questionnaire | **5** | 0 | 0 | 0 | 5 | meaningful drawback → player decides | **sound (policy)** |
| 21 | **Rampage** | rules 4/7; questionnaire | **3** | 0 | 0 | 0 | 3 | loss-of-control (case-by-case since rule 7) | **sound (policy)** |
| 22 | **Friendly fire (explicit rejects)** | rule 1; questionnaire | **3** | 0 | 0 | 0 | 3 | "no automatic logic for now, potential for friendly fire" | **sound (policy)** |
| 23 | **Spawned / ranged** | collection-time | **10** | 10 | 0 | 0 | 0 | marked "spawned/ranged" at collection | **re-examine** |
| 24 | **Charge-only** | collection-time (block 4, 2026-10-08) | **1** | 0 | 0 | 0 | 1 | "charge-only; no automatic logic" | **✗ REFUTED (C8)** |
| 25 | **Revisit** | questionnaire | **15** | 2 | 0 | 2 | 11 | user chose to defer, not reject | **deferred, not a rule** |
| 26 | **Not achievable** | questionnaire | **1** | 0 | 0 | 0 | 1 | "reacting to an enemy spell cast needs a spell-cast event or an enemy unit read, neither of which exists" | **partly (no spell-cast event, C10)** |
| | **TOTAL** | | **1,192** | 262 | 656 | 104 | 170 | | |

---

## The rules, one section each

Each section gives **(1)** the rule and its verbatim origin, **(2)** how many abilities it removes,
split by whether they are otherwise implementable, **(3)** the justification, **(4)** whether it is
still valid against the CURRENT capability set, **(5)** what re-opening takes and the risks.

---

### Rule 1 — Spells & cataclysms (`excluded (spell)`) — 434 abilities

1. **The rule and origin.** The tracker's legend: *"`excluded (spell)` — spells / winds-of-magic /
   cataclysm abilities: out of scope by the user's earlier standing decision (§3c)."* The inventory's own
   heading (§3c) reads *"Spells & cataclysms — excluded by prior user decision … Listed for completeness
   only."* No single verbatim sentence for the original scope call is recorded in the tracker — the
   recorded form is the legend line plus the §3c heading. The rule was reaffirmed in the one case that
   came back on its own merits — **Sword of Teclis**, block 4 (2026-10-08): user *"Skip - it's a
   magic-resource ability (excluded scope)"*. Rule 10 explicitly *"extends the earlier exclusions
   (`spell` / winds-of-magic / cataclysm keys, §3c)"*.
2. **Count and split.** **434** (418 whose reason is `spell`, 16 `cataclysm`). By their own targeting:
   **142 self/ally**, **268 enemy-unit**, **23 ground**, **1 other**. Mechanically, the great majority
   (410 of 434) declare a target the mod can now reach; the exclusion is a scope choice, not an engine wall.
3. **Justification recorded.** Out of scope: these are winds-of-magic / magic-resource spells the player
   casts deliberately, and they carry a resource cost the rest of the mod's abilities do not.
4. **Still valid?** As a **policy rule it stands** — the capability set does not touch it; several are
   outright hostile to automation for **other** reasons already covered (vortex/breath/bombardment and
   the ~218 FF rows are inside this block). But it is **not** an engine limit: with C1 (enemy cast), C2/C3
   (ground) and C6 (target-class flags), the 410 target-reachable rows could now be cast. This is the
   user's scope decision to reopen or not — it is **not** refuted, and should not be silently reopened.
5. **If re-opened.** Needs: nothing new mechanically for the self/ally/enemy/ground subsets — they drop
   onto the existing evaluators exactly like the Class-A/B ability bodies. **Risks:** doubles the roster
   (~434 more entries to trigger, tune and field-test); the magic-resource timing is genuinely the
   player's tactical choice (winds are a scarce, regenerating pool); and most of the FF families live
   inside this set, so re-opening spells without keeping the FF families shut would import the whole
   friendly-fire problem. **Recommendation: leave it to the user's scope call; do not reopen unilaterally.**

---

### Rule 2 — Army-bar abilities (`skipped (army-bar ability)`) — 117 abilities

1. **The rule and origin.** Standing **rule 10**, set 2026-10-08. Verbatim user instruction:
   **"Skip all army bar abilities."** The rule text: *"any ability carried by the ARMY BAR rather than a
   unit's own dial is left out entirely … Such items are marked `skipped (army-bar ability)` and get NO
   automatic logic. The collection exclusion filter gains an `army-bar` keyword: any key whose database
   prefix carries `army_abilities` … is EXCLUDED from every future questionnaire block."* Recorded twice:
   the block-4/5/6 round (2026-10-08) and the Class-B round (2026-10-14, Meat Feast).
2. **Count and split.** **117** = 99 `excluded (auto: army-bar ability)` + 18 `skipped (army-bar ability)`.
   By targeting: **35 self/ally**, **50 enemy-unit**, **25 ground**, **7 other**. Every one of them is
   otherwise a conventional effect (buff / hex / heal / bombardment) — several would be trivially
   implementable if they sat on a unit dial.
3. **Justification recorded.** The army bar is a battle-wide UI element, not a unit's own dial; the mod
   is per-unit (a unit knows only its own abilities) and its badges/labels live on unit dials, so an
   army-bar ability has no unit junction to hang off.
4. **Still valid?** **Stands as a user instruction.** Note both halves: (a) the *user decision* is
   unambiguous and untouched by any capability change; (b) mechanically, a route **does** exist —
   `battle_army:use_special_ability(key, position, bearing, width)` (API dump, cited in the feasibility
   report) fires an army-level ability, so this is not an engine wall. The reason it stays shut is
   provenance and agency, not capability.
5. **If re-opened.** Needs: an army-level evaluator (the army bar is not polled by the current per-unit
   loop) plus a decision on where the badge lives when there is no unit dial. **Risks:** the whole UI
   story (badges, arming, the tooltip line) is per-unit by construction; army abilities fire for the
   whole force at once, so a mis-fire is army-wide; and the user has already ruled twice. **Recommendation:
   keep; surface it only as "user's standing call".**

---

### Rule 3 — "No enemy-unit read" (`excluded (impossible: no enemy-unit read)`) — 76 abilities

1. **The rule and origin.** Triage, 2026-10-09. Verbatim engine-limit statement: *"**No read of enemy
   units** — an enemy unit has no card and no id, so any ability that must **target, react to, or measure
   an enemy** cannot be automated → *no enemy-unit read*."* The audit (Class A, 98 entries) states the
   same: *"there is no enemy-unit read (no card, id or health) and enemy-targeted casts cannot be aimed,
   so none of these can deliver its declared effect as written."*
2. **Count and split.** **76**, every one enemy-unit-targeted (0 self/ally, 0 ground). They are the
   single-target hexes/debuffs, missile-bound spells (Fireball, Spirit Leech, Gaze of Nagash, Chain
   Lightning, The Fate of Bjuna …), and a few enemy-area effects. Effectively they are the residue of
   Class A after Accusation (harness 94) and the 97 Class-A entries that shipped in harness 97.
3. **Justification recorded.** An engine limit: enemy units were believed to be unenumerable and
   untargetable from script.
4. **Still valid? ✗ REFUTED.** C1 proves the opposite: enemies **do** enumerate
   (`get_scriptunits_for_main_enemy_army_to_local_player()`), the API **does** accept an enemy target
   argument, and **89 entries / 97 keys already ship** casting at enemies via the Accusation mechanism
   (`uc:perform_special_ability(key, enemy_battle_unit)`, fresh handles, offer test = enemy distance
   ≤ the per-ability 70 % constant). The triage's own worst case ("the *cast at the enemy it is
   fighting* idea cannot be built with the available reads") is now the shipped design.
5. **If re-opened.** Mechanism that now exists: the proven enemy-cast route (C1) + the 70 % bound (C5)
   + invalid-target flags (C6) for the class-restricted ones. What it takes: a per-entry `range_real`
   from `target_intercept_range`, the chosen enemy as the cast target, in-melee preference, pre-cast
   re-check, hold — all already written for the other 97. **Risks:** enemy selection (which of the
   enemies in reach), and that an enemy-targeted **projectile** (the 52 explosive-projectile rows are a
   sibling set) can still splash friendlies; also several of the 76 are `bound` spells with a **winds/
   uses** cost. **Verdict: RE-OPENABLE in full** — this is the biggest honest win, ~76 abilities.

---

### Rule 4 — Summons (`excluded (auto: summon)`) — 78 abilities

1. **The rule and origin.** Standing rule **R3**, 2026-10-09: *"**summon** (unless already handled)"* is
   an unsuitable family. (Grouped here with the 4 `summon/transform` rows.)
2. **Count and split.** **78** = 74 `summon` + 4 `summon/transform`. By targeting: **53 self/ally**,
   **15 enemy-unit**, **7 ground**, **3 other** (a summon spell's declared target is usually self+ground —
   where the unit appears — so the cast form itself is reachable).
3. **Justification recorded.** The ability spawns a new unit; its value is the spawned unit's placement
   and the moment, which the trigger cannot judge.
4. **Still valid?** **Sustained.** The *cast form* is reachable (C2/C3 ground placement at a point), but
   the rule was never about the cast form — it is about the **outcome**: a summon is a positional/timing
   decision (block a flank, plug a gap, add a caster) whose worth the script cannot measure. There is no
   read of whether the summoned unit helped. Keep, with the honest note that it is a *judgment* rule,
   not an engine wall.
5. **If re-opened.** Needs: a placement policy (the only defensible one is "at the owner's feet while in
   melee", i.e. accept a melee-screen summon) and a trigger. **Risks:** summons with a limited/one-shot
   use would be spent on a bad moment; the player's deliberate use (a tide-turner) would be burned
   automatically. **Verdict: keep shut.**

---

### Rule 5 — Vortex / wandering wind (`excluded (auto: vortex …)`) — 116 abilities

1. **The rule and origin.** The friendly-fire **family decision, 2026-10-09** (triage §2.1). Verbatim:
   *"A damage vortex/wind is released and **travels across the battlefield** on its own path, damaging
   every unit (friend and foe) it touches. · Recommendation: **EXCLUDE.** The path is uncontrollable and
   there is no read to aim or time it — friendly fire is guaranteed, not avoidable."* This is the family
   form of the original scope rule 1 (*"No friendly fire: any ability with friendly-fire potential gets
   NO automatic logic"*). Includes the 29 `vortex` and 17 `unsuitable: vortex` collection-time rows.
2. **Count and split.** **116** (70 wandering-wind + 29 vortex + 17 unsuitable-vortex). By targeting:
   **6 self/ally**, **55 enemy-unit**, **15 ground**, **40 other**.
3. **Justification recorded.** The vortex's path is the engine's, not the script's: once released it
   walks on its own heading and grinds whatever it crosses, friend or foe.
4. **Still valid?** **Yes — the strongest of the FF family.** C1/C2 let you *place* a vortex, but nothing
   lets you *steer* it or read its travel; the friendly-fire risk is not removable, only relocated.
   (The one nuance — some of the 40 "no targeting" rows may be self-centred vortex buffs mis-grouped —
   is worth a spot-check, not a rule change.)
5. **If re-opened.** Would need a placement policy and an acceptance of guaranteed own-line damage.
   **Risk:** the exact harm the original scope rule was written to prevent. **Verdict: keep shut.**

---

### Rule 6 — Bombardment / ground artillery (`excluded (auto: bombardment …)`) — 66 abilities

1. **The rule and origin.** Friendly-fire family decision, 2026-10-09 (triage §2.2). Verbatim:
   *"A strike is called down on a **chosen ground point** … Recommendation: **EXCLUDE.** Placing it
   usefully needs an enemy read the engine does not have; blind placement lands on your own line."*
2. **Count and split.** **66** = 63 bombardment/ground-artillery + 3 `unsuitable: bombardment/ranged`.
   By targeting: **0 self/ally**, **51 enemy-unit**, **9 ground**, **6 other**. Heavy single-strike
   artillery (Comet of Casandora, Hailstorm, The Dreaded Thirteenth, Searing Doom, Magma Storm …).
3. **Justification recorded.** *Explicitly*: "needs an enemy read the engine does not have" — i.e. the
   exclusion is predicated **on Rule 3's engine limit**.
4. **Still valid? ✗ REFUTED on its stated premise.** The enemy read now exists (C1), and the
   enemy-**ground** placement route is proven and shipping: `perform_special_ability_ground(key,
   enemy_pos, 0, 0)` — 9 entries already fire on `enemy_ground_area`, and the audit's Class C says the
   ground form is *"exactly what the mod's own ground-cast doctrine describes"*. The rule is no longer a
   wall; it is a **placement-policy decision** (the triage itself said so: ground-only abilities "are
   **not** impossible — their friendly-fire/placement risk is a decision, not an engine wall").
5. **If re-opened.** Mechanism that now exists: C1 + C2 + C5 (drop on the engaged enemy's ground, bounded
   by the 70 % offer test) and C6 (skip entries the target-class flags bar). What it takes: a placement
   policy — the honest conservative one is "place on the ground of the enemy this unit is already
   fighting, and only for abilities whose blast is small / that do not share a hex with friendlies",
   though the last clause is not fully checkable (C10: no area-contents read). **Risks:** the strike
   area is large and your own melee line is adjacent to the target **precisely when it is worth firing**;
   a bombardment dropped on a melee scrum is the textbook own-goal. So: **RE-OPENABLE, but the reopened
   form must be the conservative placement, and the user should accept the residual risk knowingly.**

---

### Rule 7 — Placed / static area damage (`excluded (auto: placed / static area damage …)`) — 42 abilities

1. **The rule and origin.** Friendly-fire family decision, 2026-10-09 (triage §2.3). Verbatim: *"A
   **static area-damage field** centred on a point (often self), damaging everything inside while it
   lasts. · Recommendation: **EXCLUDE.** Same wall: no enemy read to place it, and a self-centred field
   hits friendlies."*
2. **Count and split.** **42**: **1 self/ally**, **36 enemy-unit**, **5 ground**, **0 other** (Pit of
   Shades, Plaguemaster, Rubric of Dark Dimensions, Irresistible Plague!, Infernal Gateway …).
3. **Justification recorded.** Same as Rule 6 — "no enemy read to place it" — plus the self-centred
   variant hitting friendlies.
4. **Still valid? Partly refuted.** For the **36 enemy-targeted** rows the stated wall is gone (C1/C2).
   For a genuinely **self-centred** static field the second half of the justification stands: a field
   centred on your own unit damages whoever is next to it. So: refuted for the placed-on-the-enemy
   subset, sound for the self-centred subset.
5. **If re-opened.** Mechanism: place on the engaged enemy's ground (C2 + C5); the 36 enemy-targeted rows
   ride it. **Risks:** identical to Rule 6 (melee adjacency), and a static field persists — anything
   walking into it (including your own reinforcements) is caught. **Verdict: RE-OPENABLE for the
   36 enemy-placed rows; keep the 6 self-centred/other shut.**

---

### Rule 8 — Breath / cone damage (`excluded (auto: breath / cone damage …)`) — 59 abilities

1. **The rule and origin.** Friendly-fire family decision, 2026-10-09 (triage §2.4). Verbatim: *"A
   **forward cone** of damage from the caster (breath weapons, cones). · Recommendation: **EXCLUDE.** The
   cone sweeps friendly units in the arc; no way to check the arc is clear."* (Folded with the 29
   `explosive / breath attack` rows.)
2. **Count and split.** **59** = 30 breath/cone + 29 explosive/breath attack. By targeting: **1 self/ally**,
   **29 enemy-unit**, **3 ground**, **26 other**.
3. **Justification recorded.** The cone spans outward from the caster; anything in the arc takes it,
   friend or foe, and there is no read of what is in the arc.
4. **Still valid? Yes.** This is the one FF family whose justification is **not** touched by the enemy
   read: knowing *where an enemy is* does not tell you *what else is between you and it*. C10 confirms
   there is still no area-contents read. The enemy-ground route lets you place a *point*, not a *cone
   direction*.
5. **If re-opened.** Needs an arc-clearance read that does not exist (C10). **Risks:** firing a cone in
   melee always sweeps your own line. **Verdict: keep shut — genuinely sound.**

---

### Rule 9 — Explosive projectile (`excluded (auto: explosive projectile)`) — 52 abilities

1. **The rule and origin.** R3 auto-exclude, 2026-10-09: *"explosive/placed AoE"* family.
2. **Count and split.** **52**, all **enemy-unit-targeted** (0 self/ally, 0 ground). The Amber Spear,
   Warp-Fireball, Hand of Gods, bound damage spells, etc.
3. **Justification recorded.** An explosive projectile is an area-damage delivery — it catches friendlies
   near the impact.
4. **Still valid? Partly re-openable.** The projectile **can** now be aimed at an enemy unit (C1), so the
   "cannot be aimed" implication is gone; what remains is the blast radius. This is exactly the Rule 6/7
   risk with a smaller footprint.
5. **If re-opened.** Mechanism: fire at the enemy (C1) with the 70 % offer test (C5). **Risks:** the
   blast can still catch friendlies if the target is in a melee scrum; the honest gate ("only fire when
   the target is not adjacent to friendlies") is not fully checkable (C10). **Verdict: partially
   re-openable — a small/blast-radius filter would need to be added, or the user accepts the risk.**

---

### Rule 10 — Own-troop-damage AoE (`excluded (auto: own-troop-damage AoE …)`) — 26 abilities

1. **The rule and origin.** Friendly-fire family decision, 2026-10-09 (triage §2.5). Verbatim: *"The
   ability **deliberately damages your own units** as part of its effect (self-nova / sacrifice AoE). ·
   Recommendation: **EXCLUDE.** Harming your own troops by design is not something to auto-fire."*
2. **Count and split.** **26**: **0 self/ally**, **11 enemy-unit**, **6 ground**, **9 other** (Flock of
   Doom ×3, Ring of Corin, Soul Stealer, Defiling Deluge …
3. **Justification recorded.** Harmful-by-design.
4. **Still valid? Yes.** Nothing in the capability set changes the fact that the ability's own effect
   includes damaging your own side; a script cannot judge an acceptable sacrifice (that is exactly the
   player's exchange-rate call). Note this is the family the triage tied to the individual rows
   `Blood Sacrifice`/`Eat da Runts!`, which were later shipped **deliberately** as ally-targeted heals at
   a cost — so the line the project drew (heal-an-ally-at-a-cost = OK; damage-your-own-line = not) is
   consistent, and it is a user judgment.
5. **If re-opened.** Would need a "sacrifice is cheap enough" heuristic that does not exist.
   **Verdict: keep shut.**

---

### Rule 11 — Flanking / ambush (stealth) (`excluded (auto: flanking / ambush …)`) — 7 abilities

1. **The rule and origin.** Friendly-fire family decision, 2026-10-09 (triage §2.6). Verbatim: *"Hide /
   ambush / reposition effects (spotting and being spotted). · Recommendation: **EXCLUDE.** This is the
   stealth/escape family the user already rejected for other keys."*
2. **Count and split.** **7**: all "other" targeting (self-cast hide effects). Evidence in the tracker:
   *"Cast on self when the owner is flanked (needs an enemy-adjacent read; not currently possible)"*.
3. **Justification recorded.** Delegated to the stealth/escape rejection (Rule 13).
4. **Still valid? Sound as policy**, but note the **mechanism note inside the rule is now false**: a
   "flanked / threatened" condition **is** readable (`is_left_flank_threatened()` / `right` / `rear`, in
   the API dump) and the enemy read now exists (C1). So the *trigger* is buildable; what keeps the family
   shut is the user's **stealth/escape** preference, not the engine.
5. **If re-opened.** Needs a flanked trigger on the existing evaluator. **Risks:** the effect is a
   hide/disengage the user has said must be the player's call. **Verdict: the trigger is now possible;
   leave the decision to the user (stealth policy).**

---

### Rule 12 — Movement-only (`skipped (unsuitable: movement)`) — 6 abilities

1. **The rule and origin.** R3, 2026-10-09: *"pure movement / speed-only with no combat effect"*, plus
   collection-time "unsuitable (movement)" (Swiftness of Itzl etc.).
2. **Count and split.** **6** (5 `unsuitable: movement` + 1 `unsuitable: movement/vortex`): **1 self/ally**,
   **0 enemy-unit**, **2 ground**, **3 other**.
3. **Justification recorded.** A reposition/speed ability with no combat effect; the player owns movement.
4. **Still valid? Yes.** A trigger cannot judge where the player *wants* the unit; auto-moving a unit
   steals a movement decision. Sound.
5. **If re-opened.** No mechanism would help. **Verdict: keep shut.**

---

### Rule 13 — Stealth / escape (`rejected (tactical escape)` etc.) — 13 abilities

1. **The rule and origin.** Standing **rule 5**: *"Tactical escape effects: an ability whose value is a
   tactical escape (disengage / reposition) is left to the player — rejected for automation."* Verbatim
   user reasons in the tracker: **"the escape in melee is tactically relevant and must be chosen by
   player"** (×5), and the stealth variant **"No automatic logic (stealth/escape effect)"**. Includes the
   triage's 10 "already rejected by user (tactical escape/stealth)" rows + 2 trap escape + 1 stealth.
2. **Count and split.** **13**: **6 self/ally**, **0 enemy-unit**, **2 ground**, **5 other** (Skitterleap,
   Envelop in Mist, Sand Veil, Loec's Blessing, Eagle Bow, Tricksy Traps …).
3. **Justification recorded.** The escape is the player's tactical decision; auto-firing it wastes it or
   removes agency.
4. **Still valid? Yes — pure user policy**, untouched by the capability set.
5. **If re-opened.** Purely a user call. **Verdict: keep (policy).**

---

### Rule 14 — Ammo-dependent / ammo replenish (`excluded (auto: no ammo-low read …)`) — 3 abilities

1. **The rule and origin.** Triage, 2026-10-09 (individual rows 4/6/7). Verbatim: *"Restocks a friendly
   unit's ammunition. → When an ally in range is out of ammo — **needs an ammo-low read the engine
   lacks** → likely exclude."* Final status: `excluded (auto: no ammo-low read (ammo replenish))`.
2. **Count and split.** **3**: More Powder! (`wh2_dlc11_hero_abilities_more_powder`), Restock!
   (`wh2_dlc17_hero_abilities_more_powder_generic`), Restock! Gunnery School
   (`wh3_dlc25_abilities_restock_gunnery_school`) — all three **self/ally** (cast on an ally in range).
3. **Justification recorded.** The engine exposes no per-unit ammo-low read to trigger it.
4. **Still valid? ✗ REFUTED.** The API dump has **two** ammo reads on `battle_unit` (re-verified for this
   review): `ammo_left()` — *"Returns the remaining ammunition count of this unit"* — and `starting_ammo()`
   — *"the amount of ammunition the unit started the battle with"*. A unary fill fraction is therefore
   computable: `ammo_left() / starting_ammo()`. (There is no single "is-low" boolean; the fraction is
   derived, not given — but the read the rule said was missing plainly exists.) The data layer even names
   the concept: `have_ammo_below_threshold` is in the invalid-usage flag vocabulary.
5. **If re-opened.** Mechanism that now exists: C9 (compute the fraction) + C7 (the existing ally picker,
   which already selects the lowest-health ally; the analogous "ally with the lowest ammo fraction"
   picker is a small variant). What it takes: guard the divide (non-missile units / `starting_ammo() == 0`
   → fail closed), pick the ally with the lowest fill fraction, fire the replenish. **Risks:** ammo counts
   differ wildly by unit, so a fraction threshold is the only honest gate; a war machine's ammo is not the
   same resource as a bowman's — a class filter (C6) may be wanted. **Verdict: RE-OPENABLE (3 abilities).**

---

### Rule 15 — Ground-target-only (`excluded (auto: ground-target-only)`) — 15 abilities

1. **The rule and origin.** R3, 2026-10-09: *"**abilities that target the ground only**"* is an
   unsuitable family. (Grouped with the 1 `enemy-ground placement (no placement path)` row —
   The Soulstealer.)
2. **Count and split.** **15** = 14 ground-only + 1 enemy-ground-placement. By targeting: **0 self/ally**,
   **9 enemy-unit**, **5 ground**, **1 other** (Soulblight ×2, The Curse of Anraheir ×3, Transmutation of
   Lead, Dance of Despair ×2, Storm of Renewal ×2 …).
3. **Justification recorded.** The ability's declared target is the ground, not a unit, and the mod was
   thought to have no ground-placement path for them.
4. **Still valid? ✗ REFUTED.** C2/C3: the ground form **ships** — own-feet (`FOURTH.ground_keys`) and,
   crucially, **enemy-ground** (`perform_special_ability_ground(key, enemy_pos, 0, 0)`), which is proven
   live and carries 9 shipping entries. Most of this set is exactly that shape: a ground patch placed
   under the engaged enemy. (The triage already conceded the point for ground-only rows: they "are
   **not** impossible … their friendly-fire/placement risk is a *decision*".)
5. **If re-opened.** Mechanism: drop the patch on the engaged enemy's ground via C2, bounded by C5.
   **Risks:** the same melee-adjacency FF risk as Rules 6–7; the mod must place on the *enemy's* ground
   (not its own feet) so it is not caught in its own effect. **Verdict: RE-OPENABLE (15 abilities).**

---

### Rule 16 — Magic scope (`excluded (magic scope)` / `skipped (magic scope + self-damage)`) — 2 abilities

1. **The rule and origin.** Block 4, 2026-10-08, on **Sword of Teclis**: user *"Skip - it's a
   magic-resource ability (excluded scope)"*. And **Skull of Katam** (`wh_main_item_abilities_skull_of_katam`):
   user *"Skip - magic-resource + self-damage"*. Both carry `Spell Mastery` / winds-of-magic effects.
2. **Count and split.** **2**, both "other" targeting, both resource abilities.
3. **Justification recorded.** They manipulate the winds-of-magic resource (and, for the Skull, damage
   the wielder).
4. **Still valid? Yes.** The winds pool is the player's tactical resource, and the Skull has a genuine
   drawback (Rule 20). Sound.
5. **If re-opened.** No new mechanism pertains. **Verdict: keep shut.**

---

### Rule 17 — Unsourceable effect text (`no effect text available (unsourceable)`) — 26 abilities

1. **The rule and origin.** R3, 2026-10-09: *"anything whose **effect text is empty/unknown after one
   genuine sourcing attempt**"* auto-excludes. Recorded also in the triage (Ominous Powder: *"Exclude
   pending effect text (unsourceable)"*).
2. **Count and split.** **26**: **1 self/ally**, **4 enemy-unit**, **0 ground**, **21 other** (Banner of
   Hellfire, Black Hammer of Hashut, Crooked Dice, Hag's Denial, Icon of the King, Rock Bottom,
   The Gold Standard …).
3. **Justification recorded.** No sourceable effect text after one genuine attempt — i.e. the mod did
   not know what the ability does, so it could not build a trigger.
4. **Still valid? ✗ REFUTED by the fresh extraction.** The master database's own §3 rows now carry real
   mechanics for **25 of the 26**: e.g. Banner of Hellfire = "Damage: 5 per hit (max 2 entities) (to
   enemies in range)"; Icon of the King = heal + resurrects models; Hag's Denial = Damage Resistance +40 /
   Cannot Die. Only **1** (`Morikhane, the Black Armour`, `wh2_dlc14_item_abilities_morikhane_black_armour`)
   is still `unknown`. The premise ("empty/unknown after one genuine sourcing attempt") no longer holds
   for the set.
5. **If re-opened.** Needs: re-source the 25 whose effects the current extraction now carries (the master
   DB already has them), then route each onto its effect family's evaluator (heal → health≤75; buff →
   in-melee self; enemy debuff → enemy route via C1). **Risks:** the effects are now readable but a
   couple embed drawbacks (Rock Bottom damages self; Storm of Blades is +MA/−MD) — those fall under
   Rule 20, not this rule. **Verdict: RE-OPENABLE — this rule has simply gone stale against the project's
   own newer data.**

---

### Rule 18 — Mutual exclusivity (`rejected (auto: mutual exclusivity)`) — 5 abilities

1. **The rule and origin.** Standing **rule 3** and its automatic form **rule 8**: *"Mutual exclusivity
   is an automatic rejection: an ability the collection finds mutually exclusive with another is
   auto-rejected WITHOUT asking … marked `rejected (auto: mutual exclusivity)`."*
2. **Count and split.** **5**, all "other": Bastion of the Great Cities, Disdain of the Dragon Emperor,
   Fury of the Falling Blade, Harbinger of Pestilence, Healing Elixirs.
3. **Justification recorded.** The ability is mutually exclusive with another; firing it removes the
   player's choice of the other.
4. **Still valid? Yes.** A genuine design interaction, encoded by the collection. Sound.
5. **If re-opened.** Would need per-pair reasoning; no engine change helps. **Verdict: keep shut.**

---

### Rule 19 — Transform / shapechange (`excluded (impossible: no transform/shapechange support)`) — 11 abilities

1. **The rule and origin.** Triage, 2026-10-09: *"the engine **cannot swap unit forms**, so
   transform/shapechange effects have no implementation."*
2. **Count and split.** **11**: **1 self/ally**, **0 enemy-unit**, **0 ground**, **10 other**
   (Tz'arkan ×5, Formless Horror ×2, Transformation of Kadon, Transformation of the Dragon ×3).
3. **Justification recorded.** Engine limit — no form-swap API.
4. **Still valid? Yes.** No capability in C1–C9 provides a unit-form swap. Sound.
5. **If re-opened.** Needs an engine mechanism that does not exist. **Verdict: keep shut.**

---

### Rule 20 — Drawback (`rejected (drawback)`) — 5 abilities

1. **The rule and origin.** Standing **rule 2**: *"No meaningful drawback: any ability with a meaningful
   drawback / trade-off (a stat penalty, a self-risk) is left to the player."* Questionnaire reason, e.g.
   All-Consuming Hatred: *"serious drawback (Melee Defence -12); player should decide"*.
2. **Count and split.** **5**, all "other": All-Consuming Hatred, Daggerdance, Dance of Destruction,
   Dinner Bell, Harvestman's Scythe.
3. **Justification recorded.** A stat penalty / self-risk that only the player can weigh.
4. **Still valid? Yes — policy.** Nothing in the capability set evaluates a trade-off. Sound.
5. **If re-opened.** Would need a judgment the script cannot make. **Verdict: keep shut.**

---

### Rule 21 — Rampage (`rejected (rampage)`) — 3 abilities

1. **The rule and origin.** Originally **rule 4** (*"No loss of control: any ability with a loss-of-control
   effect (Rampage) is left to the player"*), **softened by rule 7 (2026-10-08)**: *"Rampage is no longer
   an automatic rejection … flagged and decided case by case (Fluid Injection! and Fury of Ursun were
   approved with it)."*
2. **Count and split.** **3**, all "other": Call for Power, In the Name of War, Manus of Ursun.
3. **Justification recorded.** Loss of control.
4. **Still valid? Sound, and already the softened form.** Note the rule *changed*: since 2026-10-08
   Rampage is case-by-case, and two Rampage abilities were **approved and shipped**. Also, the Class-B
   target-class round implemented the Rampage pair `fury_of_khaine`/`verminous_fury` on the plain in-melee
   ally family. So these 3 are simply the ones the user did not approve — a policy residue, not a rule.
5. **If re-opened.** Re-ask the 3 individually (rule 7's own procedure). **Verdict: keep as
   case-by-case.**

---

### Rule 22 — Friendly fire (explicit rejects) (`rejected (friendly fire)`) — 3 abilities

1. **The rule and origin.** Standing **rule 1**/*"original scope rule"*. Verbatim user reason (×3):
   **"no automatic logic for now, potential for friendly fire"**.
2. **Count and split.** **3**, all "other" (individual rows, not the family blocks: e.g. abilities the
   questionnaire reached one at a time).
3. **Justification recorded.** Friendly-fire potential.
4. **Still valid? Yes — the root policy** of which Rules 5–10 are the family forms.
5. **If re-opened.** Per-ability, with the same FF analysis as the families. **Verdict: keep shut.**

---

### Rule 23 — Spawned / ranged (`skipped (unsuitable: spawned/ranged)`) — 10 abilities

1. **The rule and origin.** Collection-time tagging, no verbatim user sentence. All 10 are the
   **Gate of Khorne / Nurgle / Slaanesh / Tzeentch** family (normal and "Greater") plus **The Tallyman's
   Blades** ×2.
2. **Count and split.** **10**, all **self/ally**.
3. **Justification recorded.** Marked "spawned/ranged" at collection — a spawned-capability / ranged
   effect.
4. **Still valid? Needs re-examination.** These read `unknown` in the effect column (their mechanics live
   in a spawned definition this extraction does not carry) — so they are really **Rule 17's**
   (unsourceable) problem wearing a different label, not a distinct engine limit. They should be routed
   to whatever Rule 17's re-decision produces.
5. **If re-opened.** Needs the spawned-definition's mechanics sourced. **Risks:** unknown until read.
   **Verdict: fold into Rule 17.**

---

### Rule 24 — Charge-only (`skipped (unsuitable: charge-only)`) — 1 ability

1. **The rule and origin.** Collection-time, block 4 (2026-10-08). Verbatim tracker: **Silver Horn of
   Vengeance** (`wh_main_item_abilities_silver_horn_of_vengeance`) — *"Decision: skipped (unsuitable:
   charge-only) — collection-time: charge-only; no automatic logic."*
2. **Count and split.** **1**: "Charge Bonus: +12 (to self and allies in range)" — a self/ally charge
   buff.
3. **Justification recorded.** "Charge-only" was deemed unsuitable.
4. **Still valid? ✗ REFUTED.** A **`charge_only` trigger now ships** (C8 — Ferocious Battle Howl,
   harness 90), and the whole `charge_or_melee` family (25 entries / 27 keys) exists. A charge-only
   ability is now one of the easiest shapes to build.
5. **If re-opened.** Mechanism: the shipped `charge_only` evaluator (or the charge arm of
   `charge_or_melee`). **Risks:** minimal (self-cast buff). **Verdict: RE-OPENABLE (1 ability) — it was
   excluded before the trigger existed.**

---

### Rule 25 — Revisit (`skipped (revisit)`) — 15 abilities

1. **The rule and origin.** Questionnaire: legend *"`skipped (revisit)` — user chose to skip the item
   for now (not a rejection); revisit in a later questionnaire block."* (Seductive Glory, Seismic Snare ….)
2. **Count and split.** **15**: **2 self/ally**, **0 enemy-unit**, **2 ground**, **11 other**.
3. **Justification recorded.** Deferred, not excluded.
4. **Still valid? Not really a rule** — it is an open queue. It is listed here only because the user's
   brief said "anything else excluded as unsuitable". These are re-openable simply by re-asking.
5. **If re-opened.** Re-ask. **Verdict: deferred queue, re-openable by asking.**

---

### Rule 26 — Not achievable (`skipped (not achievable)`) — 1 ability

1. **The rule and origin.** Questionnaire. Verbatim: *"user: not achievable — reacting to an enemy spell
   cast needs a spell-cast event or an enemy unit read, neither of which exists; no automatic logic."*
   The ability is **Enkhil's Kanopi** (`wh2_dlc09_item_abilities_enkhils_kanopi`, Spell Resistance +60 to
   self and allies).
2. **Count and split.** **1**, "other".
3. **Justification recorded.** Needed a spell-cast event **or** an enemy read; both said missing.
4. **Still valid? Half-refuted.** The **enemy read now exists** (C1). The **spell-cast event still does
   not** (C10 — there is no "enemy is casting" read). So the ability is still blocked *as written* (its
   trigger was "react to an enemy spell"), but a **related** form (a defensive buff cast when enemies are
   in range / a caster-class enemy is present) is now buildable.
5. **If re-opened.** A re-designed trigger (e.g. wavering or enemy-in-range) would work; a true
   spell-cast reaction still needs an event the engine does not expose. **Verdict: partially re-openable,
   with a redesigned trigger.**

---

## Summary

### A. Re-openable NOW — the recorded justification is refuted by the current capability set

These rules were written against engine limits that no longer hold. The mechanism to reopen each is
proven and shipping somewhere in the mod already.

| Rule | Abilities returned | Mechanism that now exists | What each needs |
|---|---:|---|---|
| **No enemy-unit read** | **76** | C1 — enemy enumeration + enemy-targeted cast (89 entries ship) | per-entry `target_intercept_range` → 70 % constant; enemy chosen as the cast target; in-melee preference; pre-cast re-check |
| **Bombardment / ground artillery** | **66** | C1 + C2 — enemy *ground* placement (`perform_special_ability_ground`), 9 entries ship | a conservative placement policy (drop on the engaged enemy's ground) |
| **Placed / static area damage** | **42** (36 enemy-placed) | C2 | same as bombardment; keep self-centred rows shut |
| **Explosive projectile** | **52** | C1 | fire at the enemy; the blast-radius risk is not fully checkable |
| **Unsourceable effect text** | **26** (25 now carry mechanics) | the master DB's own fresh extraction | re-source each, route onto its effect-family evaluator |
| **Ground-target-only** | **15** | C2/C3 — the ground form ships | place on the enemy's ground, not own feet |
| **Ammo replenish** | **3** | C9 — `ammo_left()` / `starting_ammo()` exist | compute the fill fraction (guard ÷0), pick the lowest-ammo ally |
| **Charge-only** | **1** | C8 — the `charge_only` trigger ships | ride the existing evaluator |
| **Subtotal** | **281** | | |

**The honest caveats inside the 281.** Not all 281 are clean:
- The **bombardment / placed / explosive / ground-only** clusters (~175 rows) share one real risk the
  capability set does **not** remove — a strike on an enemy who is locked in melee with your own line
  will catch your line, and there is **no area-contents read** (C10) to prove the hex is clear. They are
  re-openable as **decisions with a known residual FF risk**, not as free wins. A conservative form
  (place on the engaged enemy's ground, prefer abilities with a small footprint, keep the FF rows
  off-by-default) is buildable; a risk-free form is not.
- The **26 unsourceable** rows are re-openable because the project's own newer data now describes them —
  a couple of them embed a drawback (Rock Bottom damages self; Storm of Blades is +MA/−MD) and belong to
  Rule 20 instead.
- The **3 ammo** rows need a derived fraction and a class filter (a war machine's ammo ≠ a bowman's); the
  read exists, but the "is-low" test is computed, not given.

### B. Re-openable only by a policy decision — the mechanism is there, the rule is a scope/agency choice

| Rule | Abilities | Why it is a policy call, not an engine wall |
|---|---:|---|
| **Spells & cataclysms** | 434 | "out of scope" by the user's standing decision; 410 of 434 declare a target the mod can now reach (C1/C2/C3) |
| **Army-bar abilities** | 117 | user: "Skip all army bar abilities"; mechanically `battle_army:use_special_ability` exists, but the mod's badges/arming are per-unit by construction |
| **Revisit** | 15 | deferred, not rejected — re-openable by asking |
| **Spawned / ranged** | 10 | really the unsourceable problem (their mechanics are in an un-extracted spawned definition) |
| **Flanking / ambush** | 7 | the flanked trigger is now readable, but the effect is the stealth/escape family the user rejected |
| **Subtotal** | **583** | |

### C. Still sound — keep as-is

| Rule | Abilities | Why it survives the capability set |
|---|---:|---|
| **Vortex / wandering wind** | 116 | the path is the engine's; placement ≠ steering; FF not removable |
| **Summons** | 78 | the cast form is reachable, but the *outcome* (a spawned unit's placement/moment) is not judgeable |
| **Breath / cone damage** | 59 | needs an arc-contents read that still does not exist (C10) |
| **Own-troop-damage AoE** | 26 | harmful by design; the exchange-rate is the player's call |
| **Stealth / escape** | 13 | pure user policy ("must be chosen by player") |
| **Transform / shapechange** | 11 | no form-swap API exists |
| **Movement-only** | 6 | auto-moving steals a movement decision |
| **Mutual exclusivity** | 5 | a genuine design interaction; firing removes the choice of the other |
| **Drawback** | 5 | a trade-off only the player can weigh |
| **Rampage** | 3 | already softened to case-by-case by rule 7; these are just unapproved |
| **Friendly fire (explicit)** | 3 | the root "original scope rule" |
| **Magic scope** | 2 | the winds pool is the player's tactical resource |
| **Not achievable** | 1 | still no enemy-spell-cast event (C10) |
| **Subtotal** | **328** | |

### D. The bottom line

- **Total abilities under a-priori category rules: 1,192** (= the master DB §3 total; verified row-by-row).
- **Re-openable now (justification refuted): 281** — enemy-unit read 76, bombardment 66, explosive
  projectile 52, placed/static 42, unsourceable 26, ground-only 15, ammo 3, charge-only 1. All of these
  ride mechanisms that **already ship**; none needs a new engine capability.
- **Re-openable only by a policy call: 583** — spells 434, army-bar 117, revisit 15, spawned/ranged 10,
  flanking/ambush 7.
- **Still sound: 328** — vortex, summons, breath/cone, own-troop-damage, stealth/escape, transform,
  movement-only, mutual exclusivity, drawback, rampage, explicit FF, magic scope, not-achievable.
- **The two rules most worth reopening first** are **Rule 3 (no enemy-unit read, 76)** — the largest
  single mis-hit, already solved by the shipped Class-A mechanism — and **Rule 17 (unsourceable, 26)**,
  which is stale purely because the project's own newer extraction now describes 25 of the 26. **Rule 14
  (ammo, 3)** is a small but clean correction: the read the rule said was missing (`ammo_left()` /
  `starting_ammo()`) exists.
- **Where the rules remain correct and should not be touched:** no per-unit *is-firing* read; no per-unit
  *cooldown/readiness* read; no *area-contents* read; no *enemy-spell-cast* event. Those four absences are
  why breath/cone, vortex, summons, own-troop-damage and not-achievable genuinely cannot be automated —
  and a script genuinely cannot count a melee exchange the way a player can judge it, which is the real
  reason the drawback / sacrifice / own-troop-damage and mutual-exclusivity rules are sound.

*No tracker statuses were changed; the mod was not modified and nothing was built.*
