# Round 176: Master of Mists starts armed (sign-off round)

Date: 2026-11-18. Harness: `harness175.lua`. Release folder: `mod_source\releases\20261118_mists_armed_harness175\`.

## 1. The ruling and the change

- User, 2026-11-18: "Start it on A".
- The Master of Mists entry gets `start_armed = true` (round 170's per-entry field): its family,
  `ground_ally_before_range`, starts unarmed. It is not risky (no rampage, no self-damage), so the default rule arms it.
- **In battle:** its badge shows A from the start; a click still switches it to M.

## 2. The proof

| Run | Checks | Failures | File |
|---|---:|---:|---|
| FULL, run 1 | 7,326 | 0 | `h175_run1.txt` |
| FULL, run 2 | 7,326 | 0, byte-identical | `h175_run2.txt` |
| RED, pre-176 snapshot | 7,324 | 0; RED 2/2 | `h175_red.txt` |

- **DM1 (both files):** the defaults as in battle and nobody clicks. A shooting Handgunner ally: Master of Mists casts on
  the ground under it.
- **RED:** the round-175 build casts nothing (it started on M).
- **Pin rebased:** plain `start_armed` lines 8 -> 9 (harness and builder).

## 3. Build, install, documents

- **Installed pack:** md5 **`afd9d8321337e2a40eafc402c0c37b33`**, 1,502,038 bytes.
  - `IDENTICAL True`; `MATCHES SOURCE: True` four times.
  - The COMPILE gate and the ROUND 123 to 176 gates passed.
- **Archived:**
  - `archive\packs\zz_test_deadly_onslaught_20261118_round176.pack`;
  - `archive\mod_source\round176\` (source md5 `4ed82643bc61b74b770f8d4c1de1425d`).
- **Workbook:** `docs\WH3_abilities_master_v59_2026-11-18.xlsx` plus `.ods`; `XLSX v59 VERIFY OK`.
- **Tracker:** 2 rows, section 10.54.
- **Database, audits, progress page:** regenerated.
- **Not seen in game:** the next battle starts from byte 822,669,876.
