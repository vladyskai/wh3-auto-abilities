# Round 175: Master of Mists, before range else shooting (sign-off round)

Date: 2026-11-18. Harness: `harness174.lua`. Release folder: `mod_source\releases\20261118_master_of_mists_harness174\`.

## 1. Why

- **The battle** (Aislinn, one High Elf Archers unit, Empire Greatswords; log bytes 783,197,257-822,669,876, archived as
  `archive\logs\battle_20261118_r174_aislinn.txt`):
  - Master of Mists was armed at 157.75 s;
  - the Greatswords had entered the archers' range at 154.0 s;
  - its only trigger (round 142, "Before range (Farsight-like)") could no longer be met, so it never fired.
- **User:** "But it also has plain damage boost!"
- **The game data, both keys:**
  - missile damage base and armour-piercing x1.25, reload +20, missile range x1.5;
  - a 35 m area on the ground;
  - 58 s (36 s for the custom key), 2 uses, 120 s recharge.
- **Ruling:** "A: before range, else shooting".

## 2. What changed (what you will see in battle)

- **First, unchanged:** the ground under the closest friendly missile unit (the caster included) within 175 m that has no
  enemy inside its own range but one inside range x 1.35.
- **Else, NEW:** the ground under the friendly missile unit within 175 m that is shooting past its cast point.
  - Several shooting: the one with the most shooting units within 24 m of it (70% of the 35 m area); the closest wins a
    tie.
  - So one cast covers as many shooters as possible, and a late arming, or the second use, still pays the damage and
    reload.
- **Re-checked just before the cast:** the chosen unit must still be shooting.
- **Card:** "Fires under missile allies just before their enemy is in range, else while they shoot".
- **Default:** still starts on M (you did not ask to change it).

## 3. The proof

| Run | Checks | Failures | File |
|---|---:|---:|---|
| FULL, run 1 | 7,319 | 0 | `h174_run1.txt` |
| FULL, run 2 | 7,319 | 0, byte-identical | `h174_run2.txt` |
| RED, pre-175 snapshot | 7,317 | 0; RED 6/6 | `h174_red.txt` |

**Section 174 (both files):**
- MM1: one shooting Handgunner ally and no enemy just out of range. Ground casts under it.
- MM2: three shooting allies, one alone and closest, two 10 m apart. Ground casts under the pair (the closer of the
  two).
- MM3: a missile ally that never shoots. No cast.
- RED: the round-174 build casts nothing in MM1 and MM2, the same failure as in your battle.

**Pins rebased:** the h93 label mirror (the new label). No count moved.

## 4. Build, install, documents

- **Installed pack:** md5 **`0d6cb8ad1c3171b61c8e6adb4c43b53a`**, 1,501,952 bytes.
  - `IDENTICAL True`; `MATCHES SOURCE: True` four times.
  - The COMPILE gate and the ROUND 123 to 175 gates passed.
- **Archived:**
  - `archive\packs\zz_test_deadly_onslaught_20261118_round175.pack`;
  - `archive\mod_source\round175\` (source md5 `db446a982b44ffd6f9ad918b1a3bea96`).
- **Workbook:** `docs\WH3_abilities_master_v58_2026-11-18.xlsx` plus `.ods`; `XLSX v58 VERIFY OK`.
- **Tracker:** 2 rows, section 10.53.
- **Database, audits, progress page:** regenerated.

## 5. Not done

- **Not seen in game:** the next battle starts from byte 822,669,876.
- **Ruled but not built:** row 23 and section 7 (the finishers).
