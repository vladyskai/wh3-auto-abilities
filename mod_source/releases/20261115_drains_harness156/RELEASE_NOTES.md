# Round 157: the drains and the Emperor's Executioner (open batch 5, sign-off round)

Date: 2026-11-15. Harness: `harness156.lua`. Release folder: `mod_source\releases\20261115_drains_harness156\`.

## 1. The batch

The 12 open group-B attacks that hit ONE model at a time. Earlier tracker status: "excluded (impossible: no enemy-unit
read)", from before the round-145 map; no user decision. The facts come from the game's tables
(`tools\fact_sheet_open.py`).

**The drains:** the table's max_damaged_entities = 1.

| Ability | Bound | Uses | Damage |
|---|---|---|---|
| Spirit Leech (5 versions) | 70 m | 1 or 2 | 67/s for 13 s |
| The Liber Bubonicus | 70 m | 2 | 67/s for 15 s |
| Death's Timekeeper | 70 m | 2 | 67/s for 10 s, plus a small self-heal |
| Rancid Visitations | 70 m | 2 | 133/s for 10 s |
| 'Effagee' of da Git | 70 m | 2 | 67/s for 13 s; the target cannot move |
| Punch-Dagger | 10 m | 3 | 180/s for 4 s |

**The Emperor's Executioner:** 732 damage in one strike, 35 m bound.

| Version | Execute line | Allowed targets |
|---|---|---|
| Base | 20% health | Lord or Hero only (the game's rule) |
| Upgrade | 33% health | any target |

**Two readings were marked as unchecked in the proposal.** Both come from the field names only:
- `max_damaged_entities = 1` means one model per tick.
- `execute_ratio` means a target below the line is killed outright.

## 2. The rulings (user, 2026-11-15)

- **Drains:** "Most valuable single" (Rec.) and "Standing still" (Rec.).
- **The Executioner:** "At the execute line" (Rec.).

## 3. The change (what you will see in battle)

Both families start on M, like every other ability aimed at an enemy.

- **`enemy_single_drain` (10):**
  - **Target:** the most valuable single-entity enemy you can see in range: a lord, a hero or a single monster.
  - **When:** only while the caster stands still.
  - **No safety margin:** these are direct effects that cannot hit your units, so an enemy fighting your troops still
    qualifies.
- **`enemy_execute` (2):**
  - **Target:** the most valuable enemy in range whose health is at or below the execute line.
  - **Line:** the line comes from a GENERATED table (`FOURTH.EXEC_TEXT`, from `execute_ratio`).
  - **Who:** the base version keeps the game's Lord/Hero rule; the upgrade takes single entities.
- **Re-check:** every pick is re-checked just before the cast.
- **Shared code:** both families reuse the round-156 map pickers. Those gained a "no safety margin" switch and two new
  target kinds.

## 4. The proof

| Run | Checks | Failures | File |
|---|---:|---:|---|
| FULL, run 1 | 6,618 | 0 | `h156_run1.txt` |
| FULL, run 2 | 6,618 | 0, byte-identical | `h156_run2.txt` |
| RED, pre-157 snapshot | 6,596 | 0; RED 8/8 | `h156_red.txt` |

Section 156 (9 worlds, both files = 18; cast worlds also check the TARGET):

| World | Situation | Result |
|---|---|---|
| DR1 | Spirit Leech: Vampire (900) plus Grave Guard (1500, not single) | cast at the Vampire |
| DR2 | Spirit Leech: our Swordsmen fighting the Vampire | cast at the Vampire (no margin) |
| DR3 | Spirit Leech: the caster is moving | none |
| DR4 | Punch-Dagger: the Vampire 60 m away | none |
| DR5 | Punch-Dagger: the Vampire 8 m away | cast at it |
| EX1 | Executioner: Vampire at 15% | cast at it |
| EX2 | Executioner: Vampire at 30% | none |
| EX3 | Executioner upgrade: Terrorgheist at 30% | cast at it |
| EX4 | Executioner (Lord/Hero only): Terrorgheist at 15% | none |

**RED:** on the round-156 build, DR1, DR2, EX1 and EX3 cast nothing.

## 5. Pins rebased

| Pin | Old | New |
|---|---:|---:|
| entries (harness; builder 11 gates) | 810 | 822 |
| keys | 865 | 877 |
| full-table iterations | 1,620 | 1,644 |
| multi-use charge-gate keys | 250 | 258 |
| wind-up keys | 241 | 249 |
| `range_real` fields | 305 | 317 |
| target classes | 28 | 29 |
| builder gate 156: SHOT keys | 11 | 23 |
| tooltip mirror | - | + 2 wordings |

## 6. Build and install

- **`build_and_install157.py`:** ROUND 123 to 157 gates OK. The new gate regenerates the EXEC table from the game data.
  `MATCHES SOURCE: True` for all five files.
- **Installed pack:** md5 **`c387bc7df174378acbaaa443eabe9894`**, 1,614,693 bytes, `IDENTICAL True`.
- **Archived:**
  - `archive\packs\zz_test_deadly_onslaught_20261115_round157.pack`;
  - `archive\mod_source\round157\` (source md5 `9c5d74aafa2e7bf3facd5d1bc7a544a5`, annotated md5
    `98c2fa9221290504f04756fc52139c25`).

## 7. Roster documents

- **Workbook:** `docs\WH3_abilities_master_v43_2026-11-15.xlsx` plus `.ods`; `XLSX v43 VERIFY OK` (877 implemented,
  82 families, the 12 rows with their texts, the round-156 rows kept, v1 to v42 byte-unchanged: 80 files).
- **Tracker:** the 12 rows plus section 10.35. **Database:** two family texts; `DATABASE VERIFY OK`.
- **Audits:** `WHEEL-STATUS AUDIT OK`; R1 to R8 empty. **Progress page:** 877 automated, 45 open.

## 8. Not done

- **Not seen in the game.** Rounds 156 and 157 wait for the next battle, from log byte 689,926,854.
- **Still open (45):**
  - group B (12): the area drains (Blood Statuette of Spite, Darkened Mist, The Fate of Bjuna x2, Maelstrom of Change,
    Otherworldly Pestilence, Ethrac's Brazier, Staff of Masks), the hexes (Dweomer Leach Orb, Preyton Horns, The Amber
    Trance) and Storm of the Night;
  - group E (33): the self-centred explosions and whirlwinds.
