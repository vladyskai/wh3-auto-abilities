# Round 187: the badges follow the wheel at any resolution or UI scale

Date: 2026-11-21. Harness: `harness186.lua`. Release folder: `mod_source\releases\20261121_uiscale_harness186\`.

## 1. The request

User, 2026-11-21: "we need to fix the UI scale ... when I change Resolution in the game, the A/M and the arm all buttons
are not aligned anymore" (a screenshot: the "A" at the far left edge, away from its ability icon).

## 2. The cause (the 2026-11-21 log, three battles)

| Battle | Wheel `ability_parent` | Bottom-centre `orders_parent` |
|---|---|---|
| 1 and 2 (UI scale 1.6: a 1600 x 900 UI space) | (42, 677) | (499, 839) |
| 3 (the tuned setting: 1984 x 1116, 2560 x 1440 at about 1.29) | (42, 893) | (691, 1055) |

The wheel hangs from the bottom-left corner: it moved (0, -216). The badges and the ALL button hang from the bottom
centre: it moved (-192, -216). So at 1.6 every badge landed 192 px too far left (slot 1 at x = -65, ALL at -123, off
screen). A resolution change does the same.

## 3. The fix (what you will see)

- Every 2 s the mod reads where the wheel and the bottom centre are (position reads only, the same reads the INVENTORY
  lines have used for many rounds) and moves every M/A badge and the ALL button by the difference from the tuned frame.
  On your tuned setting the correction is (0, 0): nothing moves. At 1.6 it is (+192, 0).
- A resolution or UI-scale change in the middle of a battle is followed within 2 s; the log says
  `UI SHIFT: the badges move by dx,dy (...)` when it happens.
- If a reference cannot be read, the last correction stays (0, 0 at the start: the old placement).
- The ALL button keeps your tuned spot (-923, 0); `zz_all_nudge` / `zz_all_set` still work on that tuned spot.

## 4. The proof

| Run | Checks | Failures | File |
|---|---:|---:|---|
| FULL, run 1 | 7,863 | 0 | `h186_run1.txt` |
| FULL, run 2 | 7,863 | 0, byte-identical | `h186_run2.txt` |
| RED, pre-187 snapshot | 7,861 | 0; RED 8/8 | `h186_red.txt` |

**Section 186 (both files):** with the log's 1.6 positions, the Focused Shot badge (slot 1) docks at (-673, -209) and the
ALL button at (-731, 0) (the pre-187 build: -865 / -923, off screen); the tuned frame and an unreadable frame keep
(-865, -209) / (-923, 0); a switch from the tuned frame to 1.6 in battle moves both within 41 ui ticks. **Builder:** the
round-152 gate's ALL line rebased to carry the correction; the ROUND 187 gate. No roster change, so no workbook version.

## 5. Also from the 2026-11-21 battle

- **Hunter's Snare:** one cast at t=76.75 s on Knights of the Realm charging at 8.4 m/s, 38.9 m from Markus, placed on the
  ground under them. Open point 2 (the charge test) is done.
- **Focused Shot (a ruling is pending, open point 13):** the first cast (t=67.25 s, the Bretonnian Lord 122 m away, inside
  175 m) was accepted but never fired: Markus walked 25 m straight toward the Lord, past our own Swordsmen, who stood
  across the line of fire, and stopped; the mod noticed the ability was still ready and the second cast (t=77 s, 58.8 m)
  fired. ASSUMPTION: the game walks a flat-shot caster to a clear line (Focused Shot: trajectory_sight low, can hurt our
  units).

## 6. Build, install

- **Installed pack:** md5 **`816abe086cd75efbb8297bd237a8470e`**, 1,582,433 bytes; `IDENTICAL True`; `MATCHES SOURCE:
  True` four times; the ROUND 123 to 187 gates passed.
- **Archived:** `archive\packs\zz_test_deadly_onslaught_20261121_round187.pack`; `archive\mod_source\round187\` (source
  md5 `b76df6d95c5e7cad8fce3f7c00cf0599`); the battle `archive\logs\battle_20261121_r186_wulfhart.txt`.
- **Not seen in game:** the placement at 1.6 needs one look in a battle.
