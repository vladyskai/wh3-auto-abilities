# Round 128: dropped multi-use casts (fix A) and the NOT FIRING snapshot (tuning round)

Date: 2026-11-03. Harness: `harness127.lua`. Release folder:
`mod_source\releases\20261103_ready_on_screen_harness127\`. Field data:
`docs\WH3_round127_field_analysis.md`.

## 1. The rulings (user, 2026-11-03)

1. "You can implement only A, and we can implement that in general."
2. On the 40 to 154 s pauses: "Could there be any other reason? Maybe they went to melee, maybe they
   lost the target ... waiting for a clear shot. Can we read any of that? ... maybe we should explore them."

## 2. Fix A: a cast the game accepted but never executed

- **The field case:** Isha's Rain's third cast was accepted and never executed.
  `can_perform_special_ability` stays true for a multi-use ability, so the charge hold kept its full
  120 s while the ability sat ready.
- **The fix, for every ability under a charge hold:** the hold is released, and the trigger may cast
  on that same poll, when all three hold:
  - the caster is the only unit the ENGINE reports selected;
  - at least the wind-up + 3 s (`FOURTH.CHARGE_RELEASE_SETTLE_S`) have passed since the cast;
  - the ability's own button reads `active` or `hover` (the game shows it ready).
- **The log line:** `charge gate <ability>: unit N is selected and its button reads 'active' (READY)
  Xs after the last cast - that cast did not take; the hold is released`.
- **Why the engine's live selection and not the mod's tracker:** the tracker deliberately keeps the
  last unit when nothing is selected. The harness caught this: a first version released the hold on
  a deselected unit, so the check now uses the engine's live selection set and requires exactly one
  selected unit.
- **Limit:** the button exists only for the selected unit, so a dropped cast on an unselected unit
  still waits for the full recharge.

## 3. The NOT FIRING snapshot (read-only; live file only)

For each ranged unit that is not firing, once a second, the readable reasons it may be holding fire.
Each is a live engine read. One line is logged per change, with the distance and missile range when
there is a target:

`NOT FIRING unit N 'type' at t=..s: target=<type|none> (in range|OUT of range|-) target_in_melee=..
target_hidden=.. | self: melee=.. moving=.. idle=.. fire_at_will=.. skirmish=.. wavering=..
routing=.. limbered=.. ammo=<ok|OUT> [distance ..m, range ..m]`

**Not readable:** line of sight (hills, friendly units in the way). The battle API has no such read.
A pause with every listed reason clear points there. `?` means that read was unavailable.

## 4. The proof

| Run | Checks | Failures | File |
|---|---:|---:|---|
| harness 126 on the round-128 source | 5,472 | 0 | (no pin moves) |
| FULL, run 1 | 5,507 | 0 | `h127_run1.txt` |
| FULL, run 2 | 5,507 | 0, byte-identical | `h127_run2.txt` |
| LIGHT | 2,326 | 0 | `h127_light.txt` |
| RED, pre-128 snapshot (light) | 2,306 | 5, all section-127 tokens | `h127_red.txt` |

Section 127 (35 checks, live and annotated):

- **Fix A, on Null Stone (3 uses, 120 s hold):**
  - **H1:** the unit is selected and its button stays ready, so the hold is released about 3 s after
    the cast. Two casts in 5 s; the release is logged once.
  - **H2:** the button reads `inactive` (the cast took): one cast.
  - **H3:** the button reads ready but another unit is selected: one cast.
  - **H4:** the button reads ready but nothing is selected: one cast.
- **The snapshot:**
  - **N1:** an idle crossbow unit logs exactly two lines, "OUT of range" (200 m vs 150 m) and then
    "in range".
  - **N2:** a firing unit logs no NOT FIRING line after its FIRING ON.

**RED** (round-127 build): H1 casts once and holds the full recharge, which is the field bug; N1
logs nothing.

**Harness corrections during the round** (harness-side): H3 first "deselected" without selecting
another unit. That exposed the tracker problem above, which led to the engine-selection check and
the new H4 world.

## 5. Build and install

`build_and_install128.py` adds the round-128 gate. Results:

- `ARMY-BAR GATE OK`, `RELOAD TABLE MATCHES the game data`, `ROUND 128 GATE OK`, and
  `MATCHES SOURCE: True` for all five files.
- Installed pack md5 **`e432f6ef7639278b742e141a9b4764fc`**, 1,159,494 bytes, `IDENTICAL True`.

Archived: `archive\packs\zz_test_deadly_onslaught_20261103_round128.pack` and
`archive\mod_source\round128\` (source md5 `f0792526ab089319bd2e548d800e1134`, annotated md5
`023139de8a2a1ecea594ac37c8b67b62`).

## 6. Not done

- Not field-tested.
- No ability uses the firing flag yet.
- No workbook version (no roster change).
