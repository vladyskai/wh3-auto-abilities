# Round 193: Scry-Orb on when_ready, the read-only pre-shot probe (2026-11-21)

## 1. The rulings (user, 2026-11-21)

| Item | Ruling |
|---|---|
| Fast enemy direction (round 192) | "tested in battle. seems to work" (log: Hunter's Snare fired on charging Cold Ones at 38.6 m, so is_moving_fast() answers on enemies) |
| Scry-Orb | "implement" (fire when ready, like the 21 pure winds abilities) |
| Casting before the first shot | "implement recommendation and propose a test battle" (the read-only probe first) |
| Learning the recharge from the button | "too complicated, drop it for now" (a later memory read may do it) |
| The older harness logs (1.8 GB) | "Sure, if they are no useful anymore" (deleted: mock battles, 100+ fake sessions in their first 30 MB) |
| Patch check | monthly, plus an extra check on the day of an announced patch (done: the scheduled task) |

## 2. The changes (`tools\round193_patch.py`, both copies)

1. **Scry-Orb** on when_ready (3 uses, a 120 s hold row = the game's recharge_time). It starts armed with its family.
2. **The pre-shot probe** (read-only). For every ranged unit of ours that is not firing, every poll, `FOURTH.preshot_now`
   asks:
   - a current target (it exists only after an attack order or a fire-at-will pick) within the unit's own live
     `missile_range()`,
   - the target visible,
   - the unit standing, unless it can fire on the move,
   - ammunition left,
   - the unit not in melee.

   The live log gets three kinds of line:
   - `WOULD CAST unit ... at t=...` when all of them start to hold (with the fire-at-will behaviour, never read before),
   - `WOULD CAST ENDED ... after X s with no shot (reason)` when they stop without a shot,
   - `PRESHOT unit ...: the condition held X s before the first shot` or `...came with no would-cast before it` at the
     first shot.

   Nothing is cast. The reading copy keeps the same logic with its log lines turned into comments.
3. **`tools\analyze_preshot.py <log> --from <offset>`** reads a battle: how many would-cast moments were followed by a
   shot, after how long, how many ended without one (and why), and the shots that came with no warning.

## 3. Proof

- Harness 192: **8,047 checks / 0 failures**, twice, byte-identical. New section: 0zz41 (tokens), SO1 (Scry-Orb casts
  once), PS1-PS5 (standing in range: WOULD CAST then PRESHOT held; walking: no WOULD CAST and 'no would-cast before it';
  out of range: none; target hidden: none; standing then walking: WOULD CAST ENDED (moving); every world casts nothing).
- RED (`h192_red.txt`, the pre-193 snapshot): no Scry-Orb cast, no probe line.
- Rebased pins (`tools\make_harness192.py`): entries 984 -> 985, keys 1,037 -> 1,038, the badge walk 1,968 -> 1,970,
  when_ready 20 -> 21, the charge gate's multi-use rows 346 -> 347 (all: Scry-Orb).
- Build `build_and_install193.py` (ROUND 193 GATE: Scry-Orb on when_ready with its recharge as hold, the three probe
  functions issue no order, the two call sites). Installed pack md5 **`9f3107dd086756560d98caf1516de831`**, 1,607,113
  bytes, 4 x `MATCHES SOURCE: True`, archived as `archive\packs\zz_test_deadly_onslaught_20261121_round193.pack`.
- Workbook **v75** (`make_xlsx_v75.py`, `verify_xlsx_v75.py` OK): Scry-Orb IMPLEMENTED, 1,038 implemented, **0 open**.

## 4. The proposed test battle (for the probe)

Custom battle, our side Empire, against an AI army that walks into our fire (Greenskins or Lizardmen):
- Lord: Markus Wulfhart (a shooting character).
- Ranged: Handgunners, Crossbowmen, Huntsmen, Pistoliers (they fire on the move), a Great Cannon.
- What to do during the battle:
  1. Leave fire at will ON for half of the ranged units. Turn it OFF for the other half and give them attack orders.
  2. Walk one unit into range and stop it there.
  3. Put one unit where a hill or a wood blocks its view.
  4. Let one unit's target reach our melee line (shooting into melee).
  5. Keep the Pistoliers moving while they shoot.

Afterwards: `python tools\analyze_preshot.py <game log> --from <offset>` gives the evidence for the ruling.

Next battle from log byte 905,235,993.
