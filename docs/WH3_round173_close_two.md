# Round 173: Null Stone and Rock Eye closed (sign-off round)

Date: 2026-11-18. Harness: `harness172.lua`. Release folder: `mod_source\releases\20261118_close_two_harness172\`.

## 1. The ruling

User, 2026-11-18: "Close Null stone, Rock Eye." (rows 18 and 16 of `docs\WH3_low_score_review_2026-11-17.md`).

## 2. What changed (what you will see in battle)

- Null Stone and Rock Eye no longer get an M/A badge and never fire by themselves. You cast them by hand.
- Both rode `melee_unwavering` (in melee, not wavering). Null Stone's charge-gate hold row (3 uses) is removed too, and
  the generated recharge table was regenerated (the other generated tables did not change).
- **Counts:** 939 -> 937 entries; 994 -> 992 keys; 102 families; melee_unwavering 282 -> 280.

## 3. The proof

| Run | Checks | Failures | File |
|---|---:|---:|---|
| FULL, run 1 | 7,251 | 0 | `h172_run1.txt` |
| FULL, run 2 | 7,251 | 0, byte-identical | `h172_run2.txt` |
| RED, pre-173 snapshot | 7,249 | 0; RED 4/4 | `h172_red.txt` |

- **0zz21:** 937 entries; no `null_stone` or `rock_eye` left in either file.
- **NS1 / RE1:** a unit owning the ability, in melee, its badge clicked: no cast. On the pre-173 build: one cast each.

## 4. Pins rebased (harness 172 vs 171)

| Pin | Old | New | Why |
|---|---|---|---|
| every entry count | 939 | 937 | 2 closed |
| key-count comparisons (11) | 994 | 992 | 2 closed keys |
| melee_unwavering (15 + 2 EXP) | 282 | 280 | both rode it |
| h105 A4a iterations | 1,878 | 1,874 | 2 x 937 |
| h103 charge-gate rows | 327 | 326 | Null Stone's hold row removed |
| h127 H1-H4 subject | Null Stone | Doom Glaive | the same shape: 3 uses, 120 s recharge, no wind-up, melee_unwavering, a hold row |

**Builder:** the same counts; the auto-accepted list loses both markers (291 -> 289 entries, 306 -> 304 keys); the ROUND
173 gate refuses either name back in the source.

## 5. Build, install, documents

- **Installed pack:** md5 **`b64667d0b84ef3257f3943c7ccc4a7ca`**, 1,447,398 bytes; `IDENTICAL True`; `MATCHES SOURCE:
  True` four times; ROUND 123 to 173 gates OK.
- **Archived:** `archive\packs\zz_test_deadly_onslaught_20261118_round173.pack`; `archive\mod_source\round173\` (source
  md5 `fe3a63bca72e2651b2d0df5ed4b3fb86`).
- **Workbook:** `docs\WH3_abilities_master_v56_2026-11-18.xlsx` plus `.ods`; `XLSX v56 VERIFY OK` (992 implemented, 47
  skipped; v1 to v55 byte-unchanged, 106 files).
- **Tracker:** 2 rows, section 10.51. **Database:** `DATABASE VERIFY OK`. **Audits:** wheel OK, trigger audit all 0.
  **Progress page:** 992 automated, 76 decided, 55 open.

## 6. Also recorded

- **Read F, the spellcaster class (rows 32-36, 39):** ruled in a side session, "Okay, then let's use the caster list."
  The review doc's read F row now carries it. The list tool (`tools\list_casters.py`) and its two outputs belong to
  that session and are not part of this commit.

## 7. Next

Rows 24 to 50 (user: "You may implement items 24 to 50").
