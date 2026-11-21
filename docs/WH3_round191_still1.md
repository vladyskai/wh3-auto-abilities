# Round 191: the animation decides in group 1 (2026-11-21)

## 1. The ruling

Round 190 fixed the 8 shot abilities and audited every trigger (`docs\WH3_stand_still_audit_2026-11-21.md`: 33 more
triggers, 103 animated abilities that never wait for the caster to stand still, in six groups). The user:

> "For now, please only implement number 1."

Group 1 = the triggers that fire at an enemy somewhere else. The caster can be walking to your order when an enemy
elsewhere enters melee; an animated cast then stops him (the Amber Bow case). Groups 2-6 are NOT touched and still wait
for rulings.

## 2. The change (`tools\round191_still.py`, both copies)

One block before the load loop, and four lines in it:

1. `FOURTH.STILL_GATE_TRIGGERS`: the 8 group-1 triggers: `enemy_ground_melee_infantry`, `enemy_ground_melee`,
   `enemy_engaged_or_shot`, `enemy_melee`, `enemy_fast_near_ally`, `enemy_melee_or_fast`, `enemy_melee_noncommander`,
   `enemy_missile_shooting`.
2. `FOURTH.still_wrap(f)`: returns an evaluator that first asks `FOURTH.blob_still(unit)` and answers "no" while the
   caster moves, otherwise runs the trigger as before.
3. At load, every entry on one of those triggers gets its evaluator wrapped (`ability.still_gate = true`).

In plain words: before the mod even looks for a target for one of these abilities, it asks "does this cast play an
animation, and if so, is the caster standing?" `FOURTH.blob_still` answers "yes" for a cast without an animation, so
only the animated abilities change.

Why per entry and not inside the shared pickers: the pickers (`eg_pick_enemy`, `evaluate_enemy_melee`) are also used by
triggers outside group 1 (for example `enemy_ground_area`, and other families call `evaluate_enemy_melee`). Wrapping
the entry changes exactly the 8 triggers ruled on.

## 3. What changes in battle

These 40 abilities now wait until their caster stands still (50 workbook rows):

| Trigger | Abilities |
|---|---|
| enemy_ground_melee_infantry (12) | Celestial Comet, Celestial Lightning, Comet of Casandora, Klad Brakak, Lightning Strike, Lord of the Storm, Master of Lightning, Meteor Strike, Nemesis Crown, Searing Doom, Slicing Shards, Urannon's Thunderbolt |
| enemy_ground_melee (7) | Captain Roth's Moondial, The Awakening, The Heralds' Arrival, Transformation of Kadon, Undeath to All, Undeath to All Upgraded, Savage Dominion |
| enemy_engaged_or_shot (6) | Doom & Darkness, Eternal Gaze, Fecund Rebirth, Oil Flask, Plague of Rust, The Withering |
| enemy_melee (6) | Acquiescence, Otto's Scythe, Ravaging Swarm, Ravaging Swarm Upgraded, Tendrils of the Sea, The Enfeebling Foe |
| enemy_fast_near_ally (4) | Master Rune of Slowness, Net of Amyntok, Rune of Slowness, Whispering Mist |
| enemy_melee_or_fast (3) | Crippling Throw, The Golden Blowpipe of P'Toohee, Storm of the Night |
| enemy_melee_noncommander (1) | The Dreaded Thirteenth |
| enemy_missile_shooting (1) | Missile Mirror |

Every other ability on these triggers (no cast animation) still fires on the move, e.g. Accusation.

Doom & Darkness: one of its three keys plays an animation (`wh3_dlc27_spell_bound_runecaller_death_doom_and_darkness`).
The mod treats an entry as one (round 168: any animated key), so its other two keys wait too.

Cost (the user's "better if it doesn't fire"): while you move one of these casters, the ability waits. A slow (Rune of
Slowness, Net of Amyntok) fires on a fast enemy coming at an ally; if the caster is walking at that moment, it waits.

## 4. Proof

Harness 190 (`mod_source\releases\20261121_still1_harness190\harness190.lua`, section `run_h190`):

| Test | World | Expected | RED (pre-191) |
|---|---|---|---|
| 0zz39 | the set (8 triggers), the wrapper, the load-loop wrap, in both files | present | absent |
| OF1 | **Oil Flask, caster walking**, an enemy in melee at 20 m | **0 casts** | **1 cast** |
| OF2 | Oil Flask, caster standing | 1 | 1 |
| AC1 | Accusation (same trigger, no animation), caster walking | 1 | 1 |
| CC1 | **Celestial Comet, caster walking**, infantry in melee at 60 m (ground cast) | **0** | **1** |
| CC2 | Celestial Comet, caster standing | 1 | 1 |

- GREEN: full suite **7,967 checks / 0 failures**, twice, byte-identical (`h190_run1.txt`, `h190_run2.txt`). No pin
  needed a rebase.
- RED (`H190_LIVE` / `H190_ANN` on `docs\backups\round191\pre191_*.lua`, `h190_red.txt`): the old code casts Oil Flask
  and Celestial Comet while the caster walks.
- Build `build_and_install191.py` (ROUND 191 GATE: exactly the 8 triggers, each wired; the wrapper asks blob_still; the
  load loop wraps; Oil Flask and Celestial Comet still animated in the game data). Installed pack md5
  **`ffd2f85006fd334d245a2710d3449656`**, 1,600,810 bytes, `IDENTICAL True`, 4 x `MATCHES SOURCE: True`. Archived as
  `archive\packs\zz_test_deadly_onslaught_20261121_round191.pack`.
- Workbook v73: the 50 trigger texts gain the STANDING sentence; `verify_xlsx_v73.py` VERIFY OK.
- Audit re-run (`tools\audit_stand_still.py`, now counting the load-time wrap;
  `docs\WH3_stand_still_audit_2026-11-21_r191.tsv`): 24 of 49 triggers with animated abilities wait; 63 animated
  abilities left (groups 2-6). The round-190 table is kept as it was.

Not seen in game yet. Next battle from log byte 881,292,588.
