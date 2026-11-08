# Round 127: the firing flag's OFF window and the target-lost fix (tuning round)

Date: 2026-11-03. Harness: `harness126.lua`. Release folder:
`mod_source\releases\20261103_off_window_target_lost_harness126\`. Field data:
`docs\WH3_round126_field_firing_analysis.md`.

## 1. The ruling

The user approved both proposals, verbatim: "Yes, both".

1. **FIRING OFF after max(2 x reload, 20 s).** Land Ships, Steam Tanks and hunter characters fire
   slower than their table reload (Land Ship 10 s table, 13 s real; Steam Tank 10 s, 19.75 s; Witch
   Hunter 4 s, 16 s), so the round-126 window (1.25 x reload) split them into one episode per shot.
   Replayed on that battle: 64 episodes before, 43 with this window (38 is the ideal). A unit missing
   from the reload table now uses the 20 s minimum (it was a 10 s default; `AMMO_WINDOW_DEFAULT_S`
   is deleted).
2. **The bug.** When a unit's target disappeared, the OUT OF RANGE line formatted a nil distance and
   range. That raised inside the probe's pcall, lost the line, and skipped the rest of the army for
   that poll. It now logs `OUT OF RANGE ... target lost (no current target)`.

## 2. The change

- `FOURTH.AMMO_OFF_FACTOR = 2` and `FOURTH.AMMO_OFF_MIN_S = 20`:
  `window = max(2 x reload, 20 s)`, or 20 s for a unit missing from the table.
- The FIRING OFF line says which applied: `= 2 x reload Xs`, `the 20 s minimum (2 x reload Xs is
  shorter)`, or `no reload in the table: the 20 s minimum`.
- The live file's OUT OF RANGE branch prints numbers only when it has them.
- The annotated copy takes the same window logic and stays log-free.
- `tools\round127_off_window_and_target_lost.py` made the edits.

## 3. The proof

| Run | Checks | Failures | File |
|---|---:|---:|---|
| harness 125 on the round-127 source | 5,451 | 7, all pins of the old window | (discrimination run) |
| FULL, run 1 | 5,472 | 0 | `h126_run1.txt` |
| FULL, run 2 | 5,472 | 0, byte-identical | `h126_run2.txt` |
| LIGHT | 2,291 | 0 | `h126_light.txt` |
| RED, pre-127 snapshot (light) | 2,285 | 3, all section-126 tokens | `h126_red.txt` |

**Pins rebased** (in this file's copies of sections 124 and 125; old -> new, and why: the user
approved max(2 x reload, 20 s)):

| Pin | Old | New |
|---|---|---|
| constant token | `AMMO_OFF_FACTOR = 1.25` | `= 2` |
| constant token | `AMMO_WINDOW_DEFAULT_S = 10` | `AMMO_OFF_MIN_S = 20` |
| F1c | OFF after 16.25 s, world of 101 polls | OFF after 26 s (2 x 13), 140 polls |
| F3b | OFF on the 10 s default, 50 polls | the 20 s minimum, 95 polls |

Section 126 (21 checks, live and annotated):

- **0w:** the tokens; the deleted default gone; the live "target lost" branch; the annotated copy
  log-free.
- **G1:** the Land Ship's field rhythm (shots 13.25 s apart, table 10 s) is one episode.
- **G2:** the Witch Hunter (4 s) with shots 16 s apart is one episode, and its OFF line names the
  20 s minimum.
- **G3:** a target that disappears logs "target lost" once, and the unit listed after it is read on
  every poll. The expected read count is measured from a control world with the same units where the
  target never disappears: 20 of 20.

**RED** (round-126 build): the Land Ship splits into 4 episodes, and the lost target costs the next
unit one poll (19 reads against the control's 20). Both field problems are reproduced.

Harness corrections during the round (harness-side only):
- The token `AMMO_WINDOW_DEFAULT_S = 10` occurs in two older sections, not one.
- G3's expected read count was hard-coded as 19; it is now measured from the control world.

## 4. Build and install

`build_and_install127.py` adds the round-127 gate. Results:

- `ARMY-BAR GATE OK`, `RELOAD TABLE MATCHES the game data`, `ROUND 127 GATE OK`, and
  `MATCHES SOURCE: True` for all five files.
- Installed pack md5 **`4fe244e74b295771d2242f6d6784c7ae`**, 1,154,086 bytes, `IDENTICAL True`.

Archived: `archive\packs\zz_test_deadly_onslaught_20261103_round127.pack` and
`archive\mod_source\round127\` (source md5 `ad1a9a063a82169901842539892eb9a9`, annotated md5
`726ce3f7fa2589165cac84e1c85c5c68`).

## 5. Not done

- No ability uses the firing flag yet; wiring abilities to it needs a trigger ruling per ability.
- No workbook version (no roster change).
- Not field-tested.
