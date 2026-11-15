# Round 153: no trash targets unless a big blob; the ALL badge for any selection (sign-off round)

Date: 2026-11-15. Harness: `harness152.lua`. Release folder: `mod_source\releases\20261115_trash_all_harness152\`.

## 1. The field battle (round 152, High Elves vs Vampire Counts)

Log from byte 641,639,500, archived as `archive\logs\battle_20261115_r152.txt`.

| Target | Live value per soldier | Value destroyed per cast | Casts |
|---|---:|---:|---:|
| The Tithe | 0.8-1.0 | 15-19 | 7 (breaths) |
| Grave Guard | 6.0-7.1 | 72-178 | 7 (Star Dragon's Breath, Volley of High Arrows) |

The breaths took the Tithe whenever no Grave Guard block was safe and in range: the value rule always took the best
target available, however cheap.

The ALL badge showed under the portrait, but hid when two selected units shared no ability: it followed the ability
badges, and the wheel shows none for such a selection.

## 2. The rulings (user, 2026-11-15)

- **Trash:** "I think we should just ignore trash units ... definitely zombie does not require a breath. Unless there is
  a big blob". Trash = "Value below 2" per soldier, the bottom 4% of 520 infantry types by cost per soldier:
  - Zombies 0.62, Skavenslaves 0.69, The Tithe 1.0, Skeletons 1.88, Clanrats 1.88;
  - Goblin Spearmen (2.03) and Empire Spearmen (2.5) are not trash.
- **Big blob:** "3 packed blocks".
  - **Correction:** Claude's option text also said "3 x the density line (51+ soldiers)", which is wrong. The density
    line is half a packed block, so 51 soldiers is only 1.5 blocks.
  - The literal 3 packed blocks was built: 3 x the blast area / 2.368 m2, about 100 soldiers in a 5 m blast. The user
    was told.
- **The ALL badge:** shown for any selection with any of our abilities; "a bit more centered ... higher, so it's like
  in the middle of this visual cloth"; a hover tooltip "if it's possible".

## 3. The change (what you will see in battle)

- **The trash rule:** an infantry target worth less than 2 per soldier (live value) is skipped unless the blast covers
  3 packed blocks. An unreadable value is not treated as trash. The rule is checked on the pick and again just before
  the cast. Large targets and non-trash infantry are unchanged.
- **The ALL badge:**
  - It is shown whenever any selected unit owns any of our abilities.
  - It sits at offset (-855, -28): the middle of the cloth, measured from the user's second screenshot. The previous
    spot (-880, 8) landed exactly where predicted, which confirms the measurement.
  - It carries a hover tooltip: "ALL: arm or disarm every automatic ability of the selected unit(s). If any of them is
    on M, all go to A (automatic); if all are already on A, all go to M (manual)." The call is pcall'd: if the badge
    template has no tooltip support, no tooltip shows and nothing breaks.

## 4. The proof

| Run | Checks | Failures | File |
|---|---:|---:|---|
| FULL, run 1 | 6,473 | 0 | `h152_run1.txt` |
| FULL, run 2 | 6,473 | 0, byte-identical | `h152_run2.txt` |
| LIGHT | 3,292 | 0 | `h152_light.txt` |
| RED, pre-153 snapshot (light) | 3,278 | 0; RED 6/6 | `h152_red.txt` |

Section 152, Sun Dragon's Breath:

| World | Situation | Result |
|---|---|---|
| TR1 | one trash block | no cast |
| TR2 | two stacked (about 67 soldiers) | no cast |
| TR3 | four stacked (about 134) | one cast |
| TR4 | one ordinary block | one cast |
| AL1 | two selected units with no shared ability | ALL shown; one click arms both; both fire |
| AP2 | the ALL badge | at (-855, -28) with the tooltip |

**RED:** TR1 and TR2 cast on the round-152 source, and the badge sits at the old spot with no tooltip.

**Limit:** the mock's wheel is static, so it cannot reproduce "no ability badge for a mixed selection". AL1 proves the
new rule, not the old hiding.

## 5. Pins rebased

| Pin | Old | New | Why |
|---|---|---|---|
| active-list walks | 6 | 5 | the ALL badge no longer walks the ability list |
| section 151 ALL spot (0zx, AP1a) | (-880, 8) | (-855, -28) | moved by the user's request |
| builder round-152 gate | (-880, 8) | (-855, -28) | same |
| mock component | - | SetTooltipText recorded | the new tooltip |

## 6. Build and install

- **The first run was refused by the new round-153 gate,** because the gate miscounted. It expected 2 uses of
  `blob_trash_ok(e, sc, r)`, but the definition line also contains that text, so the true count is 3. The installed
  pack stayed untouched and was not archived. With the count fixed, the build ran clean.
- **`build_and_install153.py`:** ROUND 123 to 153 gates OK; `MATCHES SOURCE: True` for all five files.
- **Installed pack:** md5 **`04ed9fcfe08ef13b800d6810f61e4629`**, 1,586,283 bytes, `IDENTICAL True`.
- Archived: `archive\packs\zz_test_deadly_onslaught_20261115_round153.pack`; `archive\mod_source\round153\` (source md5
  `98f10208d658cfaef5dc6fa09320c72c`, annotated md5 `e28d2ad00f033dade52a912bdf476620`).

## 7. Roster documents

- **Workbook:** `docs\WH3_abilities_master_v41_2026-11-15.xlsx` plus `.ods`; `XLSX v41 VERIFY OK` (structural checks,
  trash 77 / 77, the round-152 texts intact); v1 to v40 byte-unchanged (76 files).
- **Tracker:** section 10.31. **Database:** the enemy_blob text; `DATABASE VERIFY OK`.
- **Audits:** the wheel audit is OK; R1 to R8 are empty. **Progress:** 68 open.

## 8. Not done

- **Not tested in the game.** The next battle starts at log byte **668,831,712**.
- **Check in the game:** the ALL badge's new spot, whether its tooltip appears on hover, and that two selected units
  with no shared ability still show it.
