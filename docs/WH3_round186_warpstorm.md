# Round 186: Warpstorm Scroll as a damage dealer

Date: 2026-11-20. Harness: `harness185.lua`. Release folder: `mod_source\releases\20261120_warpstorm_harness185\`.

## 1. The ruling

User, 2026-11-20, on the round-184 rule-10 question: "No need to enforce single-entity. No need to enforce charge, treat
it just as a damage dealer. The slow is not so relevant in this case."

## 2. What changed (what you will see in battle)

- **Warpstorm Scroll** fires on the most valuable flying enemy within 70 m (70% of 100 m), whatever its size: a dragon,
  a flying Lord or Hero, or a flying unit such as Harpies. No charge condition; our units near the target do not stop it
  (the effect hits enemies only). It has no cast animation, so it may fire while its bearer moves.
- It rides NEW `enemy_most_valuable` (the shared shot picker's "value" kind with the entry's target class), because no
  family picked "the most valuable enemy" without a size or Lord/Hero limit. Card: "Fires on the most valuable enemy;
  flying targets only".
- The trigger audit records your ruling for rule 10 (R4, ruled).
- **Counts:** 988 entries / 1,041 keys / 141 families.

## 3. The proof

| Run | Checks | Failures | File |
|---|---:|---:|---|
| FULL, run 1 | 7,844 | 0 | `h185_run1.txt` |
| FULL, run 2 | 7,844 | 0, byte-identical | `h185_run2.txt` |
| RED, pre-186 snapshot | 7,842 | 0; RED 6/6 | `h185_red.txt` |

**Section 185 (both files):** a flying 20-man unit worth 500, a flying hero worth 300 and a ground hero worth 900: the
scroll takes the 20-man flier (the pre-186 build took the single-entity hero); with only a ground hero it holds. The
card is pinned.

**Pins rebased:** `enemy_single_drain` 14 -> 13 (2 places), harness 183's Warpstorm family and card, the TIP mirror (+1
label). **Builder:** the round-157 gate 14 -> 13, the round-184 gate's Warpstorm row, the ROUND 186 gate.

## 4. Build, install, documents

- **Installed pack:** md5 **`8bf23234706e1647946a84cc0e33a969`**, 1,579,341 bytes; `IDENTICAL True`; `MATCHES SOURCE:
  True` four times; the ROUND 123 to 186 gates passed. The first install attempt hit WinError 32 (the game was running);
  the installed pack stayed untouched until the user closed the game.
- **Archived:** `archive\packs\zz_test_deadly_onslaught_20261120_round186.pack`; `archive\mod_source\round186\` (source
  md5 `02faca9192027c0d65cebc73b02e0788`).
- **Workbook:** `docs\WH3_abilities_master_v69_2026-11-20.xlsx` plus `.ods`; `XLSX v69 VERIFY OK`.
- **Tracker:** section 10.64. **Database, audits, progress page:** regenerated.

## 5. Not done

- **Not seen in game.** Nothing since round 175 has been fought; the next battle starts from byte 822,999,135.
