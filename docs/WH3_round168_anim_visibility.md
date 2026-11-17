# Round 168: the cast animation decides, and the older pickers skip hidden enemies (sign-off round)

Date: 2026-11-17. Harness: `harness167.lua`. Release folder: `mod_source\releases\20261117_anim_visibility_harness167\`.

## 1. The rulings (user, 2026-11-17)

"Option A, animation decides all. And please implement the visibility."

## 2. What changed (what you will see in battle)

### The cast animation decides who waits

- **The rule:** a cast stops its moving caster only when the ability plays a cast animation
  (`unit_special_abilities.wind_up_stance` not empty).
  - Field evidence, 4 of 4: Volley of High Arrows and Soporific Breath stopped their casters; Book of Hoeth and Gaze of
    Malice did not.
- **The table:** NEW GENERATED `FOURTH.ANIM_TEXT` (`tools\gen_anim_keys.py`): 228 of our 1,003 keys play an animation.
- **The gate:** `FOURTH.blob_still` is the one stand-still gate for every family that waited, so the change sits in one
  place. For an entry with no animated key, it lets the cast through while the caster moves.
- **Families covered:** blob attacks, the Frost Dragon Scale, waves, the charge waves, wanderers, the strike, cones,
  single and area drains, and the single and infantry shots. No entry mixes animated and non-animated keys.
- **63 entries may now fire on the move:**
  - 10 blob attacks (Fireball and its upgrade, Warpfireball, Hand of Gods, Burning Wrath, The Amber Spear, Windblade,
    Eagle's Quiver, Volley of Kurnous, Arrow of Kurnous);
  - the Frost Dragon Scale;
  - 15 waves (Gaze of Malice, Wrath of Manann, Seafang, Khaine's Ring of Fury, Hell Hammer, Arnizipal's Black Horror,
    Blue Fire of Chaos x2, Bangstick, the Black Dragon Egg, the Fiery Ring of Thori, Lash of Slaanesh, ...);
  - 22 wanderers (the four Banishments, the Gem of Sunfire, the Gilded Horn, the Hounds of Orion, Sandstorm, the Sword
    of Khaine, the Purple Sun of Xereus, the Ruination of Cities, Blight Boil, ...);
  - Siegebreaker;
  - 3 cones (Pestilent Breath x2, Skabscrath);
  - 5 single drains;
  - 6 area drains.
- **Not changed:** an animated cast still waits for its caster to stand still. The rules that the TARGET stands still
  (waves, wanderers, the strike, cones) are untouched.
- **The cards:** the stand-still words now appear only on animated casts.
  - Fireball: "Fires where the blast hurts the enemy most, clear of allies".
  - Banishment: "Fires when the target stands still, ...".
  - Frost Fang (animated): "Fires when it and the target stand still, ...".

### The older pickers skip hidden enemies

- **The test:** NEW `FOURTH.enemy_not_hidden(enemy)`. It is false only when the game reads the enemy as NOT visible to
  our alliance (a living enemy hidden in fog or a forest reads false; field 2026-11-13). An unreadable read passes, as
  before.
- **Where it runs:**
  - first in `FOURTH.eg_class_ok`, which every enemy picker and the pre-cast re-check call;
  - in the separate non-commander picker (Eye of Khorne, The Dreaded Thirteenth, the infantry ground attacks).
- **What changes:** a hidden enemy is never a target. This covers the nearest enemy in melee, a fast enemy closing on
  your units, a wavering enemy, a shooting missile unit, the most hurt enemy, and the rest.
- **Not changed:** two triggers read enemies without picking one as the target: the air drop's underfoot test, and the
  Potion of Farsight / Mist "just beyond range" test. They can still sense a hidden enemy. Tell me if you want them to
  ignore hidden enemies too.

## 3. The proof

| Run | Checks | Failures | File |
|---|---:|---:|---|
| FULL, run 1 | 7,082 | 0 | `h167_run1.txt` |
| FULL, run 2 | 7,082 | 0, byte-identical | `h167_run2.txt` |
| RED, pre-168 snapshot | 7,080 | 0; RED 16/16 | `h167_red.txt` |

**Section 167 (both files):**
- **AN1:** Volley of High Arrows (animated) with its caster moving: no cast.
- **AN2:** Fireball with its caster moving: one cast (RED: none).
- **AN3:** Wrath of Manann with its caster moving: one cast (RED: none).
- **VS1:** Blight Swarm whose only enemy in melee is hidden: no cast (RED: it cast at the hidden enemy).
- **VS2:** the same enemy visible: one cast.
- **VS3 and VS4:** the same pair for The Dreaded Thirteenth.
- **CA1:** the cards.

## 4. Pins rebased (harness 167 vs 166)

| Pin | Old | New | Why |
|---|---|---|---|
| h149 MV1, Fireball with the caster moving | no cast | one cast | no cast animation |
| h161 WV4, Wrath of Manann with the caster moving | no cast | one cast | no cast animation |
| h165 SC2, Banishment's card | "Fires when it and the target stand still" | "Fires when the target stands still" | no cast animation |

## 5. Build and install

- **`build_and_install168.py`:** ROUND 123 to 168 gates OK; `MATCHES SOURCE: True` for all four files. The ROUND 168 gate
  regenerates ANIM and requires the gate and both visibility tests. The visibility test may block only an exact false.
- **Installed pack:** md5 **`89258fddf65a5ca819df984941cb7773`**, 1,414,743 bytes, `IDENTICAL True`.
- **Archived:**
  - `archive\packs\zz_test_deadly_onslaught_20261117_round168.pack`;
  - `archive\mod_source\round168\` (source md5 `5402521880c3e8ff073dbabeb8f1b140`, annotated md5
    `0b58076e2b3fc4149848267df7adc24b`).

## 6. Roster documents

- **Workbook:** `docs\WH3_abilities_master_v52_2026-11-17.xlsx` plus `.ods`; `XLSX v52 VERIFY OK`.
  - The 63 keys carry a round-168 note.
  - v1 to v51 are byte-unchanged (98 files).
- **Database:** `DATABASE VERIFY OK`.
- **Audits:** `WHEEL-STATUS AUDIT OK`; trigger audit R1 to R8 all 0.
- **Knowledge file:** `docs\WH3_battle_knowledge.md` now states the cast-animation rule and its evidence.

## 7. Not done

- **Not seen in game:** the next battle starts at log byte 781,091,240. Watch for:
  - a non-animated blast (Fireball, Gaze of Malice, Banishment) cast while its caster walks, and the caster keeping
    its pace;
  - the wave's direction when the caster moved during the wind-up.
- **Waiting for your rulings:** the rest of the overnight audit (`docs\WH3_overnight_audit_2026-11-17.md`).
