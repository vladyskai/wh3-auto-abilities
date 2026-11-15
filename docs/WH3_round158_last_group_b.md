# Round 158: the last group B attacks (open batch 6, sign-off round)

Date: 2026-11-15. Harness: `harness157.lua`. Release folder: `mod_source\releases\20261115_last_group_b_harness157\`.
Group B (attacks cast at an enemy) is now closed.

## 1. The batch

The 12 remaining group-B attacks. Earlier tracker status: "excluded (impossible: no enemy-unit read)", from before the
round-145 map; no user decision. The facts come from the game tables (`tools\fact_sheet_open.py`).

**Area drains:** up to 25 models hit each second; 15 for Staff of Masks.

| Ability | Bound | Uses | Extra |
|---|---|---|---|
| Blood Statuette of Spite | 70 m | 2 | |
| Darkened Mist | 21 m | 3 | up to 3 units |
| The Fate of Bjuna (2 versions) | 70 m | 1 | 5 s wind-up |
| Maelstrom of Change | 140 m | 3 | chains to 5 units |
| Otherworldly Pestilence | 70 m | 1 | chains to 5 units |
| Staff of Masks | 35 m | 2 | also heals the caster |

**The rest:**

| Ability | What it does |
|---|---|
| Ethrac's Brazier | an area drain plus speed and charge speed x0.75 |
| Storm of the Night | flying targets only (the game's `ground_unit` rule); speed x0.4 |
| Preyton Horns | -8 morale to enemies near the target, +8 to our units there |
| The Amber Trance | -16 morale on one enemy, one use |
| Dweomer Leach Orb | enemy spellcasters only; the mod has no read for that |

**Unchecked readings in the proposal** (both from field names only): "25 models per tick", and whether direct damage
ignores armour.

## 2. The rulings (user, 2026-11-15, all recommended)

| Group | Ruling |
|---|---|
| Area drains | "Most valuable infantry" |
| The slows | "Rule 10: melee or charge" |
| Morale hexes | "Horns melee, Trance waver" |
| Dweomer Leach Orb | "Lord/Hero proxy" |

## 3. The change (what you will see in battle)

All 12 start on M, like every other ability aimed at an enemy.

- **NEW `enemy_area_drain` (7):**
  - **Target:** the enemy infantry you can see in range that still has at least the ability's own model count (25, or
    15 for the Staff) and is worth the most per soldier.
  - **When:** only while the caster stands still.
  - **No safety margin:** a direct effect cannot hit your units.
  - **The model count** comes from a GENERATED table (`FOURTH.AREA_TEXT`).
- **`enemy_melee_or_fast` gains Ethrac's Brazier and Storm of the Night.** The Storm also takes the NEW class `flying`:
  `is_currently_flying()` must read exactly true.
  - **What that means in practice:** a flier that lands to fight is no longer flying, so the Storm will mostly fire on
    the charge arm: a flier closing fast on your units.
- **The morale hexes:** Preyton Horns on `enemy_melee`; The Amber Trance on `enemy_wavering`.
- **NEW `enemy_commander_value` (1):**
  - **Target:** the most valuable enemy Lord or Hero in range you can see.
  - **If the target is not a caster:** the engine refuses the cast and the mod backs off.

## 4. The proof

| Run | Checks | Failures | File |
|---|---:|---:|---|
| FULL, run 1 | 6,677 | 0 | `h157_run1.txt` |
| FULL, run 2 | 6,677 | 0, byte-identical | `h157_run2.txt` |
| RED, pre-158 snapshot | 6,643 | 0; RED 12/12 | `h157_red.txt` |

Section 157 (14 worlds, both files = 28; cast worlds also check the TARGET):

| World | Situation | Result |
|---|---|---|
| AD1 | Fate of Bjuna: Zombies plus Grave Guard | cast at the Grave Guard |
| AD2 | Fate of Bjuna: Grave Guard down to 20 men | none |
| AD3 | Fate of Bjuna: the caster is moving | none |
| AD4 | Staff of Masks: 20 men at 30 m | cast |
| AD5 | Blood Statuette: our unit in melee with the target | cast (no margin) |
| SN1 | Storm of the Night: a flying fast enemy | cast |
| SN2 | Storm of the Night: the same enemy on the ground | none |
| EB1 | Ethrac's Brazier: an enemy in melee | cast |
| PH1 | Preyton Horns: an enemy in melee | cast |
| PH2 | Preyton Horns: an idle enemy | none |
| AT1 | The Amber Trance: a wavering enemy | cast |
| AT2 | The Amber Trance: a steady enemy | none |
| DL1 | Dweomer Leach Orb: a Vampire plus Grave Guard | cast at the Vampire |
| DL2 | Dweomer Leach Orb: Grave Guard only | none |

**RED:** on the round-157 build, the six control worlds (AD1, SN1, EB1, PH1, AT1, DL1) cast nothing.

**Two shell slips during the round, both fixed:**
- the first harness generator was mangled by the shell and rewritten as a file;
- two backspace characters in one rebase rule were stripped.

## 5. Pins rebased

| Pin | Old | New |
|---|---:|---:|
| entries (harness; builder 11 gates) | 822 | 834 |
| keys | 877 | 889 |
| full-table iterations | 1,644 | 1,668 |
| multi-use charge-gate keys | 258 | 263 |
| wind-up keys | 249 | 253 |
| `range_real` fields | 317 | 329 |
| target classes | 29 | 31 |
| `enemy_melee` (harness 3; builder 2) | 34 | 35 |
| `enemy_melee_or_fast` (harness; builder) | 2 | 4 |
| SHOT keys (builder 2 gates) | 23 | 33 |
| tooltip mirror | - | + 2 wordings |

## 6. Build and install

- **`build_and_install158.py`:** ROUND 123 to 158 gates OK. The new gate regenerates the AREA table from the game data.
  `MATCHES SOURCE: True` for all five files.
- **Installed pack:** md5 **`326b37332e8f0b94bffeacea5fb6a966`**, 1,623,137 bytes, `IDENTICAL True`.
- **Archived:**
  - `archive\packs\zz_test_deadly_onslaught_20261115_round158.pack`;
  - `archive\mod_source\round158\` (source md5 `4b9fcb9e1188e00bbef3ea3953bff2b5`, annotated md5
    `dc3cd09a8d89fac2975a1a82b212d6a4`).

## 7. Roster documents and audits

- **Workbook:** `docs\WH3_abilities_master_v44_2026-11-15.xlsx` plus `.ods`; `XLSX v44 VERIFY OK` (889 implemented,
  84 families, the 12 rows with their texts, earlier rows kept, v1 to v43 byte-unchanged: 82 files).
- **Tracker:** the 12 rows plus section 10.36. **Database:** two family texts; `DATABASE VERIFY OK`.
- **Trigger audit:** first raised R4 = 2 (the Brazier and the Storm) and R6 = 1 (Preyton Horns). Both were the audit not
  knowing this round's facts. `enemy_melee_or_fast` IS rule 10's melee-or-charge family, and Preyton Horns on melee is
  this round's ruling. Taught both to `tools\audit_triggers.py`; R1 to R8 now empty.
- **Progress page:** 889 automated, 33 open.

## 8. Not done

- **Not seen in the game.** Rounds 156, 157 and 158 wait for the next battle, from log byte 689,926,854.
- **Still open (33):** group E, the self-centred explosions and whirlwinds (marked "no change proposed" since the
  survey).
