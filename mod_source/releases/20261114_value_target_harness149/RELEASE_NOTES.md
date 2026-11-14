# Round 150: value targets, standstill, Winds of Magic when ready (sign-off round)

Date: 2026-11-14. Harness: `harness149.lua`. Release folder: `mod_source\releases\20261114_value_target_harness149\`.

## 1. The field battle (High Elves vs Vampire Counts)

Log from byte 576,158,537, archived as `archive\logs\battle_20261114_blob_he1.txt`.

- **15 blob casts** (13 accepted, 2 refused "on cooldown"): 9 on The Tithe, 6 on Grave Guard, always the densest safe
  target, as the round-146 rule said.
- **The enemy army:** 10 Grave Guard (armour 90, value 850 for 120 men, about 7 per soldier), 17 Tithe (armour 15,
  value 200 for 200 men, about 1 per soldier), one Master Necromancer.
- **Volley of High Arrows is 100% armour-piercing** (3 arrows of 120 AP, blast 150 AP). On the Tithe its AP advantage
  is wasted. The user's point 1 was right.
- **The breaths are mostly base damage** (30-40% AP), which armour blocks. By damage the Tithe was a fitting target; by
  value it was not. Killing a Tithe soldier is worth about 1, a Grave Guard soldier about 7.
- **Two casts stopped a moving caster:**
  - the Princess at 70 s (Volley of High Arrows, 9.7 -> 0.4 m/s);
  - the Forest Dragon at 198 s (Soporific Breath, 10.6 -> 0.4 m/s).
- **The other 13 came from casters already standing.** The four dragons at 124-126 s were hovering at 0 m/s while the
  enemy walked into their 56 m reach.
- **One counter-example:** Book of Hoeth (a self-buff with no cast stance) did not stop its moving caster
  (4.2 -> 8.6 m/s). The two stoppers are aimed at an enemy unit and play a cast stance (`cast_forward_short`); the
  evidence cannot yet tell which of the two causes the stop.

## 2. The rulings (user, 2026-11-14)

| Topic | Ruling |
|---|---|
| Blob target | "Most value destroyed" (AP-heavy attacks skip armour below 50) |
| Which casts wait for a standstill | "For now, only the Blob attacks" |
| The 8 aimed charge abilities | "Nothing" |
| The 21 Winds of Magic abilities | "All when ready" |
| Generalize | applies to the enemy-targeted damage abilities implemented from now on |
| Winds reads | "let's read those reserves" |

**A correction:** Claude claimed the winds pool is usually full at battle start, so a recharge bonus is often wasted.
The user's screenshot showed **Power 12/100, reserve 68, "Recharge blocked"**: false. The ruling stands on its own;
the probe now logs the real numbers.

## 3. The change (what you will see in battle)

- **Blob attacks (77):**
  - **They never fire while the caster moves:** `is_moving()` must read exactly false, on the pick and again just
    before the cast.
  - **Each safe candidate must still reach the density line on its own** (17 soldiers for a 5 m blast). Among those,
    **the one whose blast destroys the most enemy value wins**: every enemy block under the blast adds soldiers
    covered x the share of one soldier a hit kills x its live value per soldier.
  - **The share killed** is the blast damage after armour (base x (1 - 0.0075 x armour), the engine's average, plus
    AP), divided by the soldier's hit points. These come from generated tables.
  - **AP-heavy attacks (38)** never target a unit with armour below 50.
  - **The log line** now shows the value destroyed, the target's armour, the share of a soldier killed per hit and
    the value per soldier.
- **Winds of Magic (21):**
  - **The abilities:** Arcane Hymn, Black Periapt, Book of Hoeth, Extra Ingredients, Jagged Dagger, Locus of
    Conjuration, Neferra's Scrolls, Power Stone, Prismatic Amplifier, Scroll of Destiny, Skull of Rarkos, Snowflake
    Pendant, Staff of Volans, Staff of Wu Xing, Starwood Staff, Stave of Avelorn, The Chromatic Tome, Unlimited Power!,
    Warpstone Tokens, Whispering Skull and Winds of Change.
  - They move from "in melee" to the new `when_ready`: they fire as soon as they are ready, with no condition.
  - Forbidden Rod, Black Staff and Grut's Sickle (they hurt the caster) and Staff of Nagash / Liber Noctus (their own
    ruling) are unchanged.
- **The map log:** a `WINDS t=... current=... reserve=... recharge_rate=...` line every 2 s with our army's winds
  (`bm:get_player_army()`; the reads were never tried before; `?` if they fail).
- **Generated tables** (the build refuses a pack that differs from the game data):
  - `FOURTH.BLOB_DMG_TEXT`: the 77 blast damage splits and AP-heavy flags;
  - `FOURTH.UNIT_DEF_TEXT`: armour and hit points of 587 infantry types, from `unit_armour_types` (newly extracted,
    107 rows), `battle_entities` and `land_units`.

**Worked example (Sun Dragon's Breath, blast 31 base + 15 AP per soldier):**
- **Tithe soldier:** 55% of its health lost, x value 1 = 0.55.
- **Grave Guard soldier:** 31% lost, x value 7.1 = 2.2.
- At the battle's densities the breath now picks the Grave Guard.

## 4. The proof

| Run | Checks | Failures | File |
|---|---:|---:|---|
| harness148 on the new source (before the rebase) | - | 46: melee_unwavering pins, the Black Periapt worlds, the tooltip mirror, the round-149 identity check | (not kept) |
| FULL, run 1 | 6,374 | 0 | `h149_run1.txt` |
| FULL, run 2 | 6,374 | 0, byte-identical | `h149_run2.txt` |
| LIGHT | 3,193 | 0 | `h149_light.txt` |
| RED, pre-150 snapshot (light) | 3,183 | 0; RED 8/8 | `h149_red.txt` |

Section 149:

| World | Situation | Result |
|---|---|---|
| VD1 | Fireball: two stacked Tithe blocks and one Grave Guard block | the cast goes at the Grave Guard |
| VD2 | Volley of High Arrows, only Tithe in range | none |
| VD3 | Volley of High Arrows, Grave Guard in range | one cast at it |
| MV1 | Fireball while the caster moves | none |
| WR1 | Book of Hoeth out of melee | one cast |
| WL1 | the WINDS row (12 / 68 / 0 from a stub army) | logged |

**RED:**
- On the round-146 source, VD1 hits the Tithe, VD2 casts, MV1 casts and WR1 stays silent.
- The first VD1 used one Tithe block, and the old build picked the Grave Guard anyway: their spacings differ, so Grave
  Guard counted as denser. The world could not tell the two rules apart, so it was changed to two stacked Tithe blocks
  before the result was trusted.

**Not covered:** a target or caster changing in the instant between the pick and the cast (the re-check is in place
but no world exercises it).

## 5. Pins rebased

| Pin | Old | New | Why |
|---|---|---|---|
| `melee_unwavering` (harness; builder 4 gates) | 309 | 288 | the 21 Winds of Magic abilities moved |
| harness-91 O1/O2 example ability | Black Periapt | Runefang | Black Periapt is now when_ready; Runefang is still an in-melee self-cast |
| round-149 0zu "identical to round 146" | the current source | the pre-150 snapshot | the revert stays proven; the source moves on |
| tooltip mirror | - | enemy_blob wording changed, when_ready added | |

## 6. Build and install

- **`build_and_install150.py`:** ROUND 123 to 150 gates OK; `MATCHES SOURCE: True` for all five files.
- **Installed pack:** md5 **`49a0903d999768b3b1123379db5a4268`**, 1,521,612 bytes, `IDENTICAL True`.
- Archived: `archive\packs\zz_test_deadly_onslaught_20261114_round150.pack`; `archive\mod_source\round150\` (source md5
  `3a1eef9453bf499ce1446cbced0c3366`, annotated md5 `9d042e4361649f69b911bbd3e6deb224`).

## 7. Roster documents

- **Tracker:** 98 rows, plus section 10.28.
- **Database:** 2 family texts; `DATABASE VERIFY OK`.
- **Workbook:** `docs\WH3_abilities_master_v38_2026-11-14.xlsx` plus `.ods`; `XLSX v38 VERIFY OK`; 854 / 269
  unchanged, 75 families; v1 to v37 byte-unchanged (70 files).
  - The 98 changed rows were checked separately: 77 / 77 carry the value and standstill text, 21 / 21 the when_ready
    text.
- **Wheel audit:** OK. **Trigger audit:** R1 to R8 empty. **Progress page:** 68 open.

## 8. Not done

- **Not tested in the game.** The next battle starts at log byte **604,674,328**.
- **Not modelled in the value estimate:** physical and magic resistance, ward saves, shields against projectiles.
  There is no battle read for them.
- **Which casts stop a caster:** only the blob attacks wait, by the user's choice. The map rows keep collecting
  evidence for the other aimed and cast-stance abilities.
