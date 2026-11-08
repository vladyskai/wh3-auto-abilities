# Round 129: the unit cards veto a ghost selection (tuning round)

Date: 2026-11-03. Harness: `harness128.lua`. Release folder:
`mod_source\releases\20261103_card_veto_harness128\`. Field data:
`docs\WH3_round128_field_analysis.md`.

## 1. The ruling (user, 2026-11-03)

"Selection fix only." The too-long hold (real recharge about 83 s against the table's 120 s) is
not touched this round.

## 2. The bug

In field battle 3 the user box-selected seven characters, then clicked Kalara alone. The engine's
selection callback never sent the six "deselected" events. Two units (the Witch Hunter 1006 and
Ulrika 1007) stayed in the mod's selected set for the rest of the battle. Fix A requires exactly one
selected unit, so it never released Isha's Rain's hold. The unit cards were right the whole time:
1006 and 1007 read `active`.

## 3. The change

In the card reconciliation (it runs on every ui tick), a unit in the selected set is dropped when
its own card reads a known UNSELECTED state for at least 2 polls (0.5 s):

- the unselected states are `active`, `hover`, `inactive`, `taking_damage` and `wavering`: every
  unselected state seen in the three 2026-11-03 battles (`FOURTH.CARD_UNSELECTED_STATES`);
- any other state (`selected`, `selected_hover`, `taking_damage_selected`, `wavering_selected`, `?`
  or one never seen) and a card not found drop nothing;
- the 2-poll wait (`FOURTH.CARD_DESELECT_CONFIRM_POLLS = 2`) keeps a fresh selection whose card has
  not caught up yet.

The log line: `selection: card N reads 'active' - the game never sent its deselection; dropped from
the selected set (K selected now)`.

What it changes in battle:

- fix A works after a box selection;
- a badge click acts only on the units really selected.

Two rules shaped the code, both caught by the full suite on the first try:

- no `string.find`: the mod's standing ban; the first draft used it and 22 pins failed;
- no extra dial walk: the walk-path pin stays at 7, and the dial already shows the real selection.

## 4. The proof

| Run | Checks | Failures | File |
|---|---:|---:|---|
| FULL, run 1 | 5,528 | 0 | `h128_run1.txt` |
| FULL, run 2 | 5,528 | 0, byte-identical | `h128_run2.txt` |
| LIGHT | 2,347 | 0 | `h128_light.txt` |
| RED, pre-129 snapshot (light) | 2,332 | 0; the RED checks reproduce the bug | `h128_red.txt` |

Section 128 (21 checks, live and annotated, on Null Stone with a 120 s hold):

- **G1, the field case:** three units box-selected, then the lord clicked alone with no
  deselection events. Each ghost is dropped once, the lord never, and fix A releases: 2 casts in
  5 s.
- **G2:** a true group selection (all three cards keep reading `selected`). Nothing is dropped, ONE
  cast.
- **G3:** a fresh selection whose card lags one poll. The lord is kept.

**RED** (round-128 build): G1 casts once and the hold is never released, which is the field bug.

## 5. Build and install

`build_and_install129.py` adds the round-129 gate. Results:

- `ARMY-BAR GATE OK`, ROUND 123 to 129 gates OK, and `MATCHES SOURCE: True` for all five files.
- Installed pack md5 **`104f86410200b6d82923a2d67d2a8e23`**, 1,161,338 bytes, `IDENTICAL True`.
- The new log line is in the installed pack (grep count 1).

Archived: `archive\packs\zz_test_deadly_onslaught_20261103_round129.pack` and
`archive\mod_source\round129\` (source md5 `76f84dda9df52bbf76dc044603a6d977`, annotated md5
`8036c5f08ce4d7c5b6c52de7b4e5e59e`). Pre-round snapshots: `docs\backups\round129\`.

## 6. Not done

- Not field-tested.
- The hold still uses the table recharge (120 s for Isha's Rain; about 83 s in this campaign).
- No workbook version (no roster change).
