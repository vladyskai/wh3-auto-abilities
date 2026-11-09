# Round 137: audit batch 6, morale (sign-off round)

Date: 2026-11-09. Harness: `harness136.lua`. Release folder: `mod_source\releases\20261109_morale_harness136\`.
Audit group R6 of `docs\WH3_trigger_audit_2026-11-09.md`.

## 1. The rulings (user, 2026-11-09)

- **Morale-only auras centred on the caster, "Self or ally wavering" (9):** Call of Violence, Get Back 'Ere!,
  Magical Animus, Rally!, Reanimate, Reanimate Upgraded, Pearl of Infinite Bleakness, Unholy Clamour (whole army),
  Mirror (Cold-Blooded) (self only).
- **Single-target Unbreakable / Leadership spells, "On the wavering ally":** Crown of Command, Doom Lord, Cold-Blooded.
  - The user also asked: *"if an ability removes rampage, it should also cast on any rampaging ally unit"*.
  - No battle read for a rampaging unit exists (not in the API, the mod or the API notes), so the user chose "Drop the
    rampage arm".
- **Tacticians, Rally! (missed in the first question) and Pilgrimage of Skulls, "On the wavering ally":** the game data
  forbids targeting the caster (`target_self = false`), so the area is centred on the wavering ally.
- **Morale plus a combat stat (6), "Keep in melee":** Change or Die!, Rot or Die!, Scrying Stone, Shield of the Old
  Ones, The Liber Mortis, Axe of Men.
- **Dedicated triggers (5), "Keep all 5 for now":** Ghoul King of Ushoran, Gulyas, Purge the Weak!, Daemonic Whispers,
  Verminous Fury.
- **Vigour:** the user added *"if an ability restores vigor, it should trigger when vigor of target is low"*, then
  *"the vigor buff is many times secondary to the other buffs. We should go one by one and decide what is more
  important."* "Tired or worse" is the line.
- **Earlier decisions:** questionnaire approvals only.

## 2. The change

| Family | Entries | Fires when | Cast |
|---|---|---|---|
| `wavering_aura` (NEW) | 9 | the caster's `is_wavering()` is exactly true, or a friendly unit (alive, not routing) inside the aura's 70% bound is wavering | the caster |
| `wavering_ally_range` (1 -> 6) | +5 | the closest wavering friendly unit inside the ability's 70% ally bound (Crown of Command, Pilgrimage of Skulls, Tacticians, Rally! 70 m; Doom Lord, Cold-Blooded 140 m) | that ally |

**The aura bounds for `wavering_aura`:**
- 35 m aura: a 24 m bound;
- Unholy Clamour: `effect_range -1`, the whole army;
- Mirror (Cold-Blooded): self only, so no ally counts.

An unreadable morale never fires, and a routing ally does not count.

**What this means in battle.**
- The morale buffs no longer fire every time the caster gets into melee. They fire when morale is actually breaking:
  the caster's own, or that of a unit inside the aura.
- The Unbreakable spells go onto the unit that is about to break.

## 3. The proof

| Run | Checks | Failures | File |
|---|---:|---:|---|
| harness135 on the new source (before the rebase) | 5,901 | 40: count pins and the tooltip mirror | (not kept) |
| FULL, run 1 | 5,948 | 0 | `h136_run1.txt` |
| FULL, run 2 | 5,948 | 0, byte-identical | `h136_run2.txt` |
| LIGHT | 2,767 | 0 | `h136_light.txt` |
| RED, pre-137 snapshot (light) | 2,733 | 0; RED 6/6 | `h136_red.txt` |

Section 136 (22 worlds):
- **Rally!:**
  - R1: the caster is wavering: one cast on the caster.
  - R2: an ally 20 m away is wavering: one cast on the caster.
  - R3: the wavering ally is 30 m away: no cast.
  - R4: in melee with nobody wavering: no cast.
  - R5: the morale read is unreadable: no cast.
  - R6: the only wavering ally is routing: no cast.
- **Unholy Clamour:** U1: an ally wavering 150 m away: one cast.
- **Mirror (Cold-Blooded):**
  - M1: an ally is wavering: no cast.
  - M2: the caster is wavering: one cast.
- **Crown of Command:** C1: an ally wavering 60 m away: one cast on that ally.
- **Tacticians, Rally!:** C2: in melee with nobody wavering: no cast.

**RED** (the round-136 build):
- R2 and C1 cast nothing.
- R4 casts (the old melee trigger).

## 4. Pins rebased

| Pin | Old | New |
|---|---:|---:|
| `melee_unwavering` (harness 21 lines; builder 4 gates) | 328 | 314 |
| `wavering_ally_range` | 1 | 6 |
| `ally_range_real` fields | 46 | 51 |
| tooltip mirror | - | + `wavering_aura` |

## 5. Build and install

- **`build_and_install137.py`** (from `tools\make_builder137.py`, order-fixed):
  - ROUND 123 to 137 gates OK;
  - `MATCHES SOURCE: True` for all five files.
- **Installed pack:** md5 **`c719e140ddff4f0525889c1388bb3fd8`**, 1,316,389 bytes, `IDENTICAL True`.

Archived:
- `archive\packs\zz_test_deadly_onslaught_20261109_round137.pack`;
- `archive\mod_source\round137\` (source md5 `6165875e1604677d9b6edbaf003d2a03`, annotated md5
  `42ce3b399b59f6e4756791faa1006fdf`).

## 6. Roster documents

- **Tracker:** 14 rows updated, plus section 10.18.
- **Database:** the new family text; `DATABASE VERIFY OK`.
- **Workbook:** `docs\WH3_abilities_master_v29_2026-11-09.xlsx` plus `.ods`.
  - Checked by `XLSX v29 VERIFY OK`.
  - 58 families; the bombardment block is now at row 104.
  - v1 to v28 are byte-unchanged (52 files).
- **Wheel audit:** OK.
- **Progress page:** rebuilt.
- **Trigger audit:**
  - R6 is empty; its 11 kept abilities are listed as ruled.
  - The new R8 lists the 27 vigour restorers for the one-by-one review.
  - R1 to R7 are all empty.

## 7. Not done

- **Not tested in the game.** The first battle will show whether `is_wavering()` turns true early enough for the
  morale buffs to matter.
- **R8, the vigour review (27 abilities):** waits for the user's one-by-one ruling.
- **Five rarer target filters remain:**
  - undead only (Eternal Gaze);
  - not flying (Entangle);
  - missile units (Missile Mirror);
  - spellcasters (Void Pendulum, Word of Change).
