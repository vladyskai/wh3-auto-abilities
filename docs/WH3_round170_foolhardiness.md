# Round 170: Potion of Foolhardiness fires on its charge (sign-off round)

Date: 2026-11-17. Harness: `harness169.lua`. Release folder: `mod_source\releases\20261117_foolhardiness_harness169\`.

## 1. The report and the cause

**User's report:** "I just tried a simple test with two empire captains. One potion of foolhardiness was armed, but did
not fire while charging. Why? We need to fix this."

**The log** (log bytes 781,091,240 to 783,197,257, archived as `archive\logs\battle_20261117_r169_captains.txt`):
- The armed captain (ui id 1001) DID cast the potion, at contact: `reason: in melee, morale not wavering`, ACCEPTED.
- The other captain's badge had been clicked to M.

**The cause:** the potion rode `melee_unwavering` (fires in melee). That family has no charge arm, so the run-in never
counted. This is the overnight review's row 2.

## 2. The ruling and the change

**Ruling (user, 2026-11-17):** "Charge or wavering".

**Effect (game data):** the caster only, charge bonus x1.4 plus Unbreakable, 31 s, ONE use.

**The trigger:** the potion now rides `charge_or_wavering` (existing; Bangers & Smash uses it). It fires:
- **on its own charge:** running at the enemy it attacks, 12 to 60 m away, at most 4 s from contact;
- **when wavering:** Unbreakable keeps it from breaking.

It no longer fires on a plain melee.

**It still starts armed, as before:**
- NEW entry field `start_armed = true`, read by the family default rule.
- `charge_or_wavering` itself does not start armed, so Bangers & Smash is unchanged.
- The round-167 risky rule and the test-only global still win.

**The card:** "Fires when charging or wavering".

## 3. The proof

| Run | Checks | Failures | File |
|---|---:|---:|---|
| FULL, run 1 | 7,126 | 0 | `h169_run1.txt` |
| FULL, run 2 | 7,126 | 0, byte-identical | `h169_run2.txt` |
| RED, pre-170 snapshot | 7,124 | 0; RED 10/10 | `h169_red.txt` |

**Section 169 (both files):**
- **PF1:** a captain charging at 20 m, not yet in melee: one cast. RED: none, which is your battle.
- **PF2:** wavering: one cast. RED: none.
- **PF3:** in melee, steady, not charging: no cast. RED: one cast, at contact as in your battle.
- **PF4:** no click, defaults on, charging: one cast, so it still starts armed. RED: none.
- **PF5:** the card.

## 4. Pins rebased (the entry moved family)

| Pins | Old | New |
|---|---|---|
| Harness: melee_unwavering entry count (17 checks, plus 2 EXP tables) | 299 | 298 |
| Harness: charge_or_wavering entry count (3 checks) | 1 | 2 |
| Builder: melee_unwavering count gates (4) | 299 | 298 |
| Builder: charge_or_wavering count gate | 1 | 2 |

## 5. Build, install, documents

- **`build_and_install170.py`:**
  - ROUND 123 to 170 gates OK, including the new ROUND 170 gate (the entry, start_armed, the default rule);
  - `MATCHES SOURCE: True` for all four files.
- **Installed pack:** md5 **`6a84ed8e067216679e7c4f50bb49c9f1`**, 1,415,242 bytes, `IDENTICAL True`.
- **Archived:**
  - `archive\packs\zz_test_deadly_onslaught_20261117_round170.pack`;
  - `archive\mod_source\round170\`.
- **Workbook:** `docs\WH3_abilities_master_v53_2026-11-17.xlsx` plus `.ods`; `XLSX v53 VERIFY OK`.
  - The potion row now reads charge_or_wavering, with the new text.
  - The trigger table: melee_unwavering 298 / 309, charge_or_wavering 2 / 2.
  - v1 to v52 are byte-unchanged (100 files).
- **Database:** `DATABASE VERIFY OK`.
- **Audits:** `WHEEL-STATUS AUDIT OK`; trigger audit all 0.
- **Not seen in game:** the next battle starts at log byte 783,197,257.
