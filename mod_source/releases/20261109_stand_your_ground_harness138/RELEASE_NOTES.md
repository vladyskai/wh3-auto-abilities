# Round 139: QA battle 1 and Stand Your Ground (tuning round with a full suite)

Date: 2026-11-09. Harness: `harness138.lua`. Release folder: `mod_source\releases\20261109_stand_your_ground_harness138\`.

## 1. QA battle 1 (the user's battle, the log read 2026-11-09)

The battle's part of the log was cut out by byte offset (from 433,191,436 to the end: 6.05 MB, 15,266 lines); the log
was never opened whole.

- **Army:** General of the Empire (ui id 1001), Witch Hunter (1002), 7 Spearmen, 7 Archers; the enemy was Beastmen.
- **Charmed Shield** (round 133, melee or under fire):
  - 2 casts: `the caster is under missile fire, cast on self`;
  - 4 casts: `in melee, morale not wavering, cast on self`.
  - The user: *"The charmed shield worked really well."* This is the first field proof of `is_under_missile_attack()`
    on the player's own unit.
- **Slippery** (round 134, charge, else melee):
  - one cast on a charge, `charging (gap=0.0m dist=12.6m eta=3.7s)`;
  - two in melee, `in melee (charge or melee)`.
- **Accusation, Runefang, Opal Amulet, Foe-Seeker:** fired on their triggers.
- **Stand Your Ground** (melee_low_morale), reported by the user as not working:
  - It fired once. At 232.25 s the General was in melee and wavering; the engine ACCEPTED the cast and confirmed
    "Special Ability issued".
  - A second attempt at 234.5 s was refused "on cooldown" (it was active).
  - The General wavered again at 254 s, inside the 90 s recharge.
  - The cause is the rule, not a bug: it read only the General's own morale. The Spearmen around him had been
    wavering since 177 s:

    | Spearmen unit | First wavering |
    |---|---|
    | 1004 | 177 s |
    | 1008 | 178 s |
    | 1007 | 186 s |
    | 1005 | 194 s |
    | 1009 | 212 s |
- **Not testable in skirmish:**
  - Potion of Speed (not offered in the item list);
  - the Huntsman General's Crown of Command (one Lord per skirmish army; Crown of Command can go on a hero instead).

## 2. The ruling and the change

User ruling, verbatim: *"The general or any friendly unit within 24m is in melee or wavering."*

NEW `melee_or_wavering_aura` (Stand Your Ground, both keys). It fires when any of these holds:
- the caster is in melee;
- or the caster's `is_wavering()` is exactly true;
- or the closest friendly unit (alive, not routing) inside the 70% aura bound (35 m -> 24 m) is in melee or wavering.

It is cast on the caster; the DLC24 key keeps its ground form at the caster's position. `melee_low_morale` keeps its
evaluator with no entry.

## 3. The proof

| Run | Checks | Failures | File |
|---|---:|---:|---|
| harness137 on the new source (before the rebase) | 5,995 | 13: the old Stand Your Ground worlds and the tooltip mirror | (not kept) |
| FULL, run 1 | 6,018 | 0 | `h138_run1.txt` |
| FULL, run 2 | 6,018 | 0, byte-identical | `h138_run2.txt` |
| LIGHT | 2,837 | 0 | `h138_light.txt` |
| RED, pre-139 snapshot (light) | 2,823 | 0; RED 4/4 | `h138_red.txt` |

**Section 138 (10 worlds):**
- W1: an ally 20 m away wavering: one cast on the General, with the reason logged.
- W2: an ally 20 m away in melee: one cast.
- W3: the wavering ally is 30 m away: no cast.
- W4: nobody in melee or wavering: no cast.
- W5: the only wavering ally is routing: no cast.

**RED** (the round-138 build): W1 and W2 cast nothing.

**Old pins rebased** (each one is the new rule):
- the harness-68 token check names the new trigger;
- S5c and S8b expect the new in-melee reason;
- S7a/S7b: in melee with a healthy morale now fires;
- S9a: wavering while running now fires.

## 4. Build and install

- **`build_and_install139.py`:**
  - ROUND 123 to 139 gates OK;
  - `MATCHES SOURCE: True` for all five files.
- **Installed pack:** md5 **`55f3263e09fedd951d1bcd8ee9ce9351`**, 1,342,010 bytes, `IDENTICAL True`.

Archived:
- `archive\packs\zz_test_deadly_onslaught_20261109_round139.pack`;
- `archive\mod_source\round139\` (source md5 `e3748dc6a503b267aed27ff19895a269`, annotated md5
  `1f6f36b2a6bcf14f1e424c64d6ef73b7`).

**My own errors this round** (both caught before any file shipped):
1. The patch first matched the live source but not the annotated copy, whose line carries a trailing comment. The live
   file was restored from the backup (md5 checked against the round-138 archive) and the patch re-run on both.
2. A heredoc edit mangled escapes. The patch was then edited with the editor.

## 5. Roster documents

- **Tracker:** 2 rows updated, plus section 10.21.
- **Database:** the new family text; `DATABASE VERIFY OK`.
- **Workbook:** `docs\WH3_abilities_master_v31_2026-11-09.xlsx` plus `.ods`.
  - Checked by `XLSX v31 VERIFY OK`.
  - v1 to v30 are byte-unchanged (56 files).
- **Wheel audit:** OK.
- **Progress page and trigger audit:** rebuilt; every audit group is still empty.

## 6. Not done

- **The rest of the QA list:** battles 2 to 4 (Skaven, Warriors of Chaos, Cathay).
- **Charge only:** has no skirmish carrier on the Empire side; battle 3 (Hellcannon) covers it.
