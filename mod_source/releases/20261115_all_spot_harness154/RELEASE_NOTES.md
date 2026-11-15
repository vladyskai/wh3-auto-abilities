# Round 155: the ALL button at the spot the user tuned by hand in battle

Date: 2026-11-15. Harness: `harness154.lua`. Release folder: `mod_source\releases\20261115_all_spot_harness154\`.
A tuning round (one constant): no ability, trigger or count changed, so no workbook version (v41 stays current). The
full suite ran anyway (it takes about 10 s).

## 1. The field battle (round 154 build)

- **Log:** from byte 675,107,621, 14.8 MB, archived as `archive\logs\battle_20261115_r154.txt`.
- **The user, on the new button:** "such a good job you did with the button design! It looks amazing."
- **The game's round button works in battle:** "ALL badge: created left of the wheel", then 11 ALL clicks (1, 2, 3 and 7
  units; ON and OFF).
- **The hand tuning:** 17 `ALL POS` lines, from -855,-26 through -930,-11 to -923,0. The last line, -923,0, was a
  `zz_all_where()` confirming the spot.
- **No breath or other blob attack was cast** in this 3-minute battle (89 WINDS rows), so the round-153 trash rule is still
  untested in the field. Book of Hoeth and Starwood Staff fired.

## 2. The change

`FOURTH.ALL_OX, FOURTH.ALL_OY = -923, 0` (was the round-154 estimate -855, -21), in the live source and the annotated
copy. The comment names the source of the pair and how to re-tune it.

## 3. The proof

| Run | Checks | Failures | File |
|---|---:|---:|---|
| FULL, run 1 | 6,512 | 0 | `h154_run1.txt` |
| FULL, run 2 | 6,512 | 0, byte-identical | `h154_run2.txt` |
| RED, pre-155 snapshot | 6,510 | 0; RED 2/2 | `h154_red.txt` |

- **GREEN, SP1:** the button is created at (-923, 0), docked bottom-centre, and `zz_all_where()` answers "ALL POS -923,0".
- **RED:** the pre-155 build sits at (-855, -21).

## 4. Pins rebased

| Pin | Old | New | Why |
|---|---|---|---|
| the ALL spot: 0zx, AP1a (section 151); 0zy, AP2a (152); 0zz, BT1a (153) | (-855, -21) | (-923, 0) | the user's hand-tuned spot |
| BT3a, `zz_all_nudge(5, -3)` from the base spot | -850,-24 | -918,-3 | the same base moved |
| builder round-152 gate | (-855, -21) | (-923, 0) | same |

## 5. Build and install

- **`build_and_install155.py`:** ROUND 123 to 155 gates OK; `MATCHES SOURCE: True` for all five files.
- **Installed pack:** md5 **`ed36892f37ca3838fd41f10c7431df50`**, 1,588,861 bytes, `IDENTICAL True`. The new spot line is
  in the installed pack.
- **Archived:**
  - `archive\packs\zz_test_deadly_onslaught_20261115_round155.pack`;
  - `archive\mod_source\round155\` (source md5 `b2e518850556934c7d08404cbd14076d`, annotated md5
    `5ce159d01c5d0a6ccfd86cb1458c934a`).
- **Trigger audit:** R1 to R8 empty. **Progress page:** 68 open.

## 6. Not done

- **Not seen in the game** at the baked spot. The hooks remain in the mod for any later re-tune.
- **The trash rule** (round 153) still waits for a battle with breaths against cheap infantry. The next battle starts at
  log byte **689,926,854**.
