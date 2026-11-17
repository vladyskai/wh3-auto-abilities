# Round 167: no final period, the safer defaults (sign-off round)

Date: 2026-11-17. Harness: `harness166.lua`. Release folder: `mod_source\releases\20261117_periods_risky_harness166\`.

## 1. The user's points (2026-11-17, after the Dark Elves battle)

1. "Gaze of Malice, I was able to manually cast while the caster was moving and he didn't stop. I now believe our check
   for which abilities stop the movement of a caster was wrong."
2. "Do you need to put a point at the end of a sentence when there is no sentence after it? Please remove the point.
   Check the other tooltips also."
3. "Please implement Safer defaults for Rampage and self-damage abilities. They stay on M even in families that start
   armed (Fury of Khaine, Verminous Fury, Rock Bottom)."
4. A question: what is "visibility for the older enemy pickers"? (answered in chat; no change).

## 2. What changed (what you will see in battle)

### No final period

- **The two tooltips:** the mod sets exactly two, the M/A badge card and the ALL button. Neither ends with a period now.
  Example: "Fires when charging or in melee".
- **Inside a card:** clauses are still joined with "; ".
- **The game's own text:** not ours to change.

### The safer defaults

- **The source:** NEW GENERATED `FOURTH.RISKY_TEXT` (`tools\gen_risky_keys.py`, from the game data). It lists 20 of our
  keys:
  - **R, rampage:** a phase of the ability gives the `rampage` attribute (positive) to the caster or its allies.
  - **D, self-damage:** a phase applied to the caster carries `damage_amount`.
- **The rule:** an entry with a risky key never starts armed, even in a family that does. A badge click still arms it,
  because your explicit choice wins.
- **Now start on M (15 entries, 16 keys):**

| Ability | Why | Family |
|---|---|---|
| Fury of Khaine | rampage | ally_melee_buff |
| Verminous Fury | rampage | ally_melee_buff |
| Witchbrew (2 keys) | rampage | melee_unwavering |
| Gaze of Khaine | rampage | melee_unwavering |
| Primal Roar | rampage | melee_unwavering |
| Toad Rage | rampage | melee_unwavering |
| Fluid Injection | rampage | melee_unwavering |
| Fury of Ursun | rampage | melee_unwavering |
| Wrathful Reaper | rampage | melee_unwavering |
| Call for Power | rampage | melee_unwavering |
| Manus of Ursun (Ursun's Claws) | rampage | melee_unwavering |
| The Blood Price | self-damage (60 per 2 s for 22 s) | melee_unwavering |
| Black Staff | self-damage (33 per s for 20 s) | melee_unwavering |
| Forbidden Rod | self-damage (33 per s for 23 s) | melee_unwavering |
| Rock Bottom | self-damage (350) | self_out_of_ammo |

- **Already unarmed by their family:** Ominous Powder, Necrotic Explosion, The Liber Noctus, Blood Sacrifice.
- **Field note:** in the Dark Elves battle the mod cast Witchbrew 6 times and Gaze of Khaine twice on their old
  defaults. From now on they wait for your click.

## 3. Gaze of Malice and the stand-still rule (NOT changed: waiting for your ruling)

**The finding.** The game data says which casts stop the caster: `unit_special_abilities.wind_up_stance`, the cast
animation.

| Ability | Cast animation | In battle |
|---|---|---|
| Volley of High Arrows | `cast_forward_short` | stopped its moving caster (2026-11-14) |
| Soporific Breath | `cast_forward_short` | stopped its moving caster (2026-11-14) |
| Book of Hoeth | none | did not stop (2026-11-14) |
| Gaze of Malice | none | did not stop (your manual cast, 2026-11-17) |

Four of four agree. This is an ASSUMPTION with good evidence, not a documented rule.

**What the mod does now.** Since round 150, 11 families wait for the caster to stand still, a rule applied per family.
In those families, 63 entries have no cast animation:
- 10 of 77 blob attacks;
- the Frost Dragon Scale;
- 15 of 30 waves;
- 22 of 43 wanderers;
- Siegebreaker;
- 3 of 5 cones;
- 5 of 10 single drains;
- 6 of 8 area drains.

These may be waiting for a stop that is not needed.

**The catch for waves and cones.** Their path runs along the line from the caster to the target. If the caster keeps
moving through a 3 s wind-up, the line may turn. It is unknown whether the game fixes the heading at the click or at the
release.

**Options (rule 9: your choice):**
- **A.** Stand still only when the ability has a cast animation, for every family. 63 entries could then fire while the
  caster moves.
- **B. (recommended)** As A, but waves and cones keep the stand-still rule until a battle shows the heading holds. About
  45 entries change.
- **C.** Keep the family rule as it is.

The target-still rules (waves, wanderers, drains) are not affected by any option.

## 4. The Dark Elves battle (log bytes 760,068,621 to 781,091,240)

Archived as `archive\logs\battle_20261117_r166_darkelves.txt` (21 MB).
- **Casts:** 87 accepted, on 35 abilities; no script errors.
- **Gaze of Malice (mod):** 1 accepted.
- **Breaths:** Fiery Breath 3, Noxious Breath 3, Frost Breath 2.
- **Soulblight:** 1 ground cast and 1 unit cast.

## 5. The proof

| Run | Checks | Failures | File |
|---|---:|---:|---|
| FULL, run 1 | 7,048 | 0 | `h166_run1.txt` |
| FULL, run 2 | 7,048 | 0, byte-identical | `h166_run2.txt` |
| RED, pre-167 snapshot | 7,046 | 0; RED 12/12 | `h166_red.txt` |

**Section 166 (both files):**
- **NP1:** no card ends with a period (RED: all 946 did).
- **SD1:** the risky entries start on M. 447 entries start armed (RED: 462).
- **RK1:** Fury of Khaine with no click: no cast (RED: one cast).
- **RK2:** with one click: one cast (RED: the click switched it off).
- **RK3:** Favour of the Fay, the same family but not risky, still casts on its own.
- **RK4:** Witchbrew with no click: no cast (RED: one cast).

## 6. Pins rebased (harness 166 vs 165)

| Pin | Old | New | Why |
|---|---|---|---|
| h152 AP2a, h153 BT1a | ALL text "... unit(s)." | "... unit(s)" | no final period |
| h164 CD1, h165 SC1 | a card ends with "." | a card does not end with "." | no final period |
| h164 CD2, h165 SC2, TT2 | 21 card literals ending "." | the same without the period | no final period |
| h165 0zz13, AL2 | the return `.. "."` and the ALL text with a period | without | no final period |

Builder: the round-166 gate's two period pins are rebased the same way.

## 7. Build and install

- **`build_and_install167.py`:** ROUND 123 to 167 gates OK; `MATCHES SOURCE: True` for all four files. The ROUND 167 gate
  regenerates RISKY from the game data, requires the default rule, and refuses a final period.
- **Installed pack:** md5 **`a2a5f5daf538e74aa5f5e230bada04d9`**, 1,402,929 bytes, `IDENTICAL True`.
- **Archived:**
  - `archive\packs\zz_test_deadly_onslaught_20261117_round167.pack`;
  - `archive\mod_source\round167\` (source md5 `808ab346b4b90744e5c95211da23ed75`, annotated md5
    `245e050f7478feebde4a2058e7b32a9b`).

## 8. Roster documents and audits

- **Workbook:** `docs\WH3_abilities_master_v51_2026-11-17.xlsx` plus `.ods`; `XLSX v51 VERIFY OK`.
  - The cards have no final period.
  - The 16 keys carry a round-167 note.
  - v1 to v50 are byte-unchanged (96 files).
- **Database:** `DATABASE VERIFY OK`.
- **Audits:** `WHEEL-STATUS AUDIT OK`; trigger audit R1 to R8 all 0.
- **Progress page:** 1,003 automated (432 seen in battle), 65 decided, 55 open.

## 9. Not done

- **Not seen in game:** the cards without the period, and the new defaults. The next battle starts at log byte
  781,091,240.
- **Waiting for your rulings:**
  - the stand-still rule (section 3);
  - visibility for the older enemy pickers;
  - the rest of the overnight audit.
