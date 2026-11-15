# Round 156: the magic missiles (open batch 4, sign-off round)

Date: 2026-11-15. Harness: `harness155.lua`. Release folder: `mod_source\releases\20261115_magic_missiles_harness155\`.

## 1. The batch

**What was open:**
- The 11 non-exploding magic missiles that were still open: the shots fired at one enemy unit.
- Earlier tracker status: "excluded (impossible: no enemy-unit read)" or "excluded (auto: explosive projectile)".
  Both were written before the round-145 map existed, and neither was a user decision.
- The facts come from the game's own tables (`tools\fact_sheet_open.py`).

**1. AP shots** (high damage per hit, very few hits; the game says they can hit our own units)

| Ability | Bound | Uses | Damage per hit (base + AP) |
|---|---|---|---|
| Blast | 70 m | 1 | 150 + 350 |
| Damned Pistol | 70 m | 2 | 495 + 855 |
| Hunting Spear | 140 m | unlimited | 0 + 540 |
| Master Rune of Flight | 70 m, min 5 m | unlimited | 150 + 350 |
| Schalkain's Teeth | 140 m | 2 | 2 shots of 250 + 250 |

**2. Snipers** (the game allows single-entity targets only; 5 s wind-up)

| Ability | Bound | Uses | Damage |
|---|---|---|---|
| Dead Eye | 105 m | unlimited | 420 + 630, +60 against infantry and large |
| Focused Shot | 175 m | 2 | 100 + 230, +120 against large |

**3. Debuff throws**

| Ability | Bound | Uses | Debuff |
|---|---|---|---|
| Crippling Throw | 84 m | 3 | speed x0.75 and melee defence -24 for 30 s; can't be cast in melee |
| The Golden Blowpipe of P'Toohee | 140 m, min 5 m | unlimited | poison: speed and damage x0.85 |
| Spear of Kurnous | 140 m | unlimited | blinded: accuracy -30, melee attack and defence -24 |

**4. Bolt Storm:** 175 m bound, 12 bolts at 9 + 24 AP each, +33 against infantry. The game forbids it in melee.

## 2. The rulings (user, 2026-11-15)

- **AP shots:** "Large first, then armour". Claude had recommended large only; the user chose the armour fallback.
- **Snipers:** "Most valuable single" (Rec.).
- **Debuff throws:** "Split by effect" (Rec.).
- **Bolt Storm:** "Most valuable infantry" (Rec.).
- **Also in the approved options:**
  - none of our units within 10 m of a map target;
  - the caster out of melee;
  - the snipers and Bolt Storm standing still.

## 3. The change (what you will see in battle)

All 11 start on M, like every enemy-targeted ability.

**Five new trigger families:**

| Family | Abilities | What it does |
|---|---|---|
| `enemy_large_shot` | the 5 AP shots | Shoots the most valuable visible large enemy in range (the game's live value). With no large target, shoots the most armoured visible enemy infantry instead. |
| `enemy_single_shot` | Dead Eye, Focused Shot | Shoots the most valuable single-entity enemy in range: a lord, a hero or a single monster. Focused Shot takes a large one first. The caster must stand still. |
| `enemy_infantry_shot` | Bolt Storm | Shoots the enemy infantry worth the most per soldier. The caster must stand still. |
| `enemy_melee_or_fast` | Crippling Throw, Blowpipe | Hits the closest enemy fighting in melee; otherwise a fast enemy closing on our units. |
| `enemy_melee_or_shooting` | Spear of Kurnous | Hits the closest enemy fighting in melee; otherwise the closest enemy missile unit that is shooting. |

**Rules shared by the map-based families:**
- Every map target is safe: no unit of ours within 10 m of it.
- The caster must be out of melee.
- The game's own melee ban and minimum range come from a generated table (`tools\gen_shot_tables.py`).

**New parts:**
- A new target class `single` honours the game's single-entity rule for the snipers.
- One new 70% constant: 120 m becomes 84 m.
- Every pick is re-checked just before the cast.

**Noted, not changed: what "large" covers.** The game's large set includes cavalry and chariots, not only monsters. A
valuable cavalry unit can therefore beat a single monster on "highest live value". The shot still hits one model.
User ruling 2026-11-15, asked after the build: "Keep as is".

## 4. The proof

| Run | Checks | Failures | File |
|---|---:|---:|---|
| FULL, run 1 | 6,579 | 0 | `h155_run1.txt` |
| FULL, run 2 | 6,579 | 0, byte-identical | `h155_run2.txt` |
| RED, pre-156 snapshot | 6,533 | 0; RED 10/10 | `h155_red.txt` |

**Before the rebase,** harness 154 on the new source failed 109 checks. All were count pins, the tooltip mirror and the
round-146 "Dead Eye and Focused Shot are absent" token.

**Section 155** (16 worlds, both files = 32; each cast world also checks the TARGET):

| World | Situation | Result |
|---|---|---|
| LS1 | Hunting Spear: Terrorgheist plus Grave Guard | cast at the Terrorgheist (large first) |
| LS2 | Hunting Spear: Zombies plus Grave Guard | cast at the Grave Guard (armour) |
| LS3 | Hunting Spear: our Swordsmen on the Terrorgheist | none |
| SS1 | Dead Eye: Vampire (900), Terrorgheist (600), Grave Guard (1500, not single) | cast at the Vampire |
| SS2 | Focused Shot: Vampire (1500), Terrorgheist (900) | cast at the Terrorgheist (large first) |
| SS3 | Dead Eye: the caster is moving | none |
| IS1 | Bolt Storm: Zombies plus Grave Guard | cast at the Grave Guard |
| IS2 | Bolt Storm: our unit on the target | none |
| IS3 | Bolt Storm: the caster in melee | none |
| MF1 | Crippling Throw: an enemy in melee | cast at it |
| MF2 | Crippling Throw: a fast enemy 20 m from us | cast at it |
| MF3 | Crippling Throw: the caster in melee | none |
| MF4 | Blowpipe: an enemy 3 m away (min 5 m) | none |
| MS1 | Spear of Kurnous: an enemy in melee | cast at it |
| MS2 | Spear of Kurnous: shooting handgunners | cast at them |
| MS3 | Spear of Kurnous: idle Swordsmen | none |

**RED:** on the round-155 build, LS1, SS1, IS1, MF1 and MS2 cast nothing.

**One world fixed during the round:** MF2 first failed because of the world, not the code. The fast-enemy check
measures from our unit to the enemy, so the caster's own distance had to be 20 m.

**Not covered by a world:** a lapse between the pick and the cast. The re-check code is pinned by token, not exercised.

## 5. Pins rebased

| Pin | Old | New |
|---|---:|---:|
| entries (harness; builder 11 gates) | 799 | 810 |
| keys | 854 | 865 |
| full-table iterations | 1,598 | 1,620 |
| multi-use charge-gate keys | 246 | 250 |
| wind-up keys | 235 | 241 |
| `range_real` fields (harness; builder 2) | 294 | 305 |
| target classes (harness; builder) | 26 | 28 |
| round-146 Dead Eye / Focused Shot pin (harness 0zr; builder gate 146) | the keys are absent | they are not on `enemy_blob` |
| tooltip mirror | - | + 5 wordings |

## 6. Build and install

- **`build_and_install156.py`:** ROUND 123 to 156 gates OK. The new gate regenerates the SHOT table from the game data and
  finds it in the script. `MATCHES SOURCE: True` for all five files.
- **Installed pack:** md5 **`4075645f56fcec8c08d10d53106fcf00`**, 1,605,250 bytes, `IDENTICAL True`. The new evaluator
  is in the installed pack.
- **Archived:**
  - `archive\packs\zz_test_deadly_onslaught_20261115_round156.pack`;
  - `archive\mod_source\round156\` (source md5 `cf3ac16ef46f8d89bc02ad3775b593cd`, annotated md5
    `d39f632c92d40b34d414e6936eac6a92`).

## 7. Roster documents

- **Workbook:** `docs\WH3_abilities_master_v42_2026-11-15.xlsx` plus `.ods`; `XLSX v42 VERIFY OK` (865 implemented,
  80 families, the 11 rows with their texts, v1 to v41 byte-unchanged: 78 files).
- **Tracker:** the 11 rows plus section 10.34. **Database:** five family texts; `DATABASE VERIFY OK`.
- **Audits:** `WHEEL-STATUS AUDIT OK`; R1 to R8 empty. **Progress page:** 865 automated, 57 open.

## 8. Not done

- **Not seen in the game.** The next battle starts at log byte 689,926,854.
- **Still open (57):**
  - 24 group B attacks: direct damage, chain effects, hexes and Storm of the Night;
  - the 33 group E self-centred explosions and whirlwinds.
