# Enemy targeting, casting and range: field-proven facts (WH3 battle scripts)

Established by live battles and probes; every item here cost at least one battle to learn.

## Enemy units ARE reachable (the old "no enemy read" limit was UI-only)
- `bm:get_scriptunits_for_main_enemy_army_to_local_player()` returns a collection with `:count()` / `:item(i)`; each item exposes `.unit` (battle_unit) and `.uc` (controller). Also `get_first_non_player_army():units()` and `get_scriptunits_for_army(alliance_id, army_id)` (lib_battle_manager.lua uses these itself).
- Enemy reads that work live: `type()`, `number_of_men_alive()`, hitpoints, `is_in_melee()`, `is_valid()`, `position()`, plus the `CcoBattleUnit` context fields by ui id. `is_under_missile_attack()` reports the unit RECEIVING fire - wrong for "is shooting", right for "is being shot at".
- There is NO per-unit "is firing" read. Near-misses and why they fail: is_under_missile_attack (receiving), current_target (set for melee units too), ammo_left (fired sometime this battle), battle-level get_num_units_under_fire, and flags.tsv is_missile_unit (a data-table construct, not a Lua read).

## Casting at an enemy: fresh handles, or it silently no-ops
- Working shape (mirrors vanilla: `siege_benchmark.lua` casts Ice Sheet at an enemy): re-fetch the CASTER and the TARGET from the script-unit enumerators on the SAME tick, then `caster_su.uc:perform_special_ability(key, enemy_su.unit)`.
- A controller handle held across polls returns `can=true accepted=true err=-` and does NOTHING: the target's effect count never moves, the caster's never moves, and `can_after` stays true so no cooldown was consumed. This is the most expensive lesson in this file.
- Passing a `script_unit` (instead of its `.unit`) or `nil` is a hard type error ("bad argument #1"); a battle_unit target is required.
- Ground-under-enemy area hexes: `perform_special_ability_ground(key, enemy_pos, 0, 0)`.
- PROVE A CAST BY EFFECT, NOT ACCEPTANCE: read the target's `common.get_context_value("CcoBattleUnit", <id>, "ActiveEffectList(true).Size")` before and after - and the caster's, to rule out self-application. delta 0 means the cast did nothing.
- The manual UI path (click ability, click enemy) is native C++ with no Lua equivalent; scripts only see `InterfaceFunction("AbilityKeyForScript")` on the button. It cannot be copied as code, but it registers a `Special Ability` command event you can log.

## Distance and range semantics (get these wrong and the unit walks)
- `unit:unit_distance(other)` is EDGE-TO-EDGE, bounding-box aware (battle_unit.lua:160 doc string); `position()` is the centre of the main squad. Real numbers: ~49% of charge-detector reads are exactly 0.0 m (touching boxes) and frontages (`ordered_width`) span ~1.1 m to ~29.4 m - the distinction is metres, not rounding.
- NEVER gate an offer/range test on `battle_unit:unit_in_range()`: it is the engine's own, much looser read (it returned true at 81.3 m where the ability's cast range gave a 52 m bound). Trusting it made the engine walk the caster into range - the user reported that as an unwanted move order. Compare `unit_distance` against your own named constant ONLY.
- `target_intercept_range` IS the cast range (community doc: "how close to the target you have to be to successfully cast the spell"); `effect_range` is the EFFECT'S AREA RADIUS (0 = single-unit/self cast). RPFM's schema gives empty descriptions for both columns, so do not assert engine semantics you cannot quote - an earlier "pursuit/intercept range" claim of ours came from a different table (projectile_homing_params.lookahead_time) and was simply wrong.
- No API read says "attacking/charging": absent are is_attacking, is_charging, speed, velocity, destination, has_order, current_order, order_queue. Available and useful: `is_moving`, `is_idle`, `ordered_position`, `script_unit:has_moved(pos, threshold)`.
- Command events: `bm:register_command_handler_callback` delivers 26 types (Move, Attack Unit, Special Ability, Entity Hit, ...) - the definitive way to see whether an engine order accompanied a cast. A scripted cast raised only `Special Ability`, even when the caster was walked.

## Target RESTRICTIONS in the game's data (who an ability may legally affect)
- `special_ability_to_invalid_target_flags_tables.tsv` (and the invalid-USAGE table) carry per-key flags naming the target classes an ability may NOT affect. The `unit_is_not_X` family is INVERTED from its name: `unit_is_not_squig` (Empowering Shrooms) means ONLY units carrying the `squig` attribute are valid recipients - 10 of them.
- Verify the polarity against same-table precedents instead of assuming: `unit_is_not_slayer` (Glorious Death), `unit_is_not_construct` (Tomb Kings Restore / Stone Shaper), `unit_is_not_artillery_or_war_machine` (Artillery Master), `unit_is_not_commander_class` (Guardian).
- Check these flags BEFORE designing a picker for any ability with an odd target set: they are why a self-cast can be entirely pointless (the caster is not a member of the legal class), and they turn "affects allies in range" into "affects only <attribute> units in range".
- Cross-check the phase junction (`phase_junc.tsv`) for who is affected at all: `target_self` / `target_friends` / `target_enemies` / `target_ground` decide whether the CASTER is among the legal recipients. The recurring defect is a self-cast on an ability whose `target_self` is false.
- When a flag names a unit ATTRIBUTE (squig, construct, hellforged), derive the affected-unit key list from the game's own tables exactly as for the Slayer list (see `unit-class-derivation.md`). Matching by ability name is not a substitute.
- The audit report is generated from these flags plus the phase tables, so an audit entry that says "no unit-type restriction found" is a positive finding, not an absence of investigation.

## Project rules the user has set (apply, do not re-ask)
- Every trigger range constant is 70% of the ability's real range, floored to whole metres, one named constant per ability: `FOURTH.RANGE_FRACTION = 0.70`, and the build asserts each constant equals `floor(real*0.70)`. No exceptions - the user overruled a field-tuned 25 m value to keep the rule absolute.
- Cast targets: enemy-targeted abilities cast at the ENEMY (never the owner); ally-targeted at the chosen ALLY; pure heals use health<=75 with no melee gate; heals that also grant armour/defence use melee+health; Unbreakable/Cannot-Die use the wavering trigger; army-bar keys are skipped (standing rule 10). The M/A badge is the opt-in that makes risky abilities acceptable.
- A probe pack left installed in `data/` interferes with the user's field tests (it runs its own casts every battle). Delete the probe pack BEFORE asking him to test, and rotate its log rather than deleting it.

## Probe pattern that works
- One throwaway Movie pack per question (`zz_probe_<topic>.pack` holding `script/battle/mod/zz_probe_<topic>.lua`), own log beside Warhammer3.exe with flush per line, conflict-phase gate logging BOTH `phase=<name>` and `conflict=<bool>` (`Deployed` IS the conflict phase - the main mod's own log proves it), shift+F3 console hook, hard caps on polls and any casts, pcall'd reads, a write-trip counter that must stay 0, and verification that the installed pack is byte-identical to source while the main mod's md5 is unchanged.
- Give each hypothesis its own labelled attempt in ONE run plus a machine-checkable verdict line (e.g. `VERDICT cast=1 moved_total=.. order_after_attack=.. already_moving_before=.. refused=..`): it collapses days of reasoning about a live game into one battle.
- A probe must not cast on the user's behalf unless casting IS the experiment. When the question is "what does the mod do", build an OBSERVER probe (read-only, zero writes) and correlate its tick-stamped lines with the main mod's own log instead of adding more casts.
- Log the real measured value, never a static label: a line reading "within 52m" while the gate actually passed at 81 m sent the investigation down the wrong path for a round. One decimal is enough, and state the primitive in a comment (`unit:unit_distance(other)`, edge-to-edge).
