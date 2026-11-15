# Round 159: group E, the last open abilities (sign-off round)

Date: 2026-11-15. Harness: `harness158.lua`. Release folder: `mod_source\releases\20261115_group_e_harness158\`.
Group E is closed. **Every in-wheel ability is now automated or decided by the user: open = 0.**

## 1. The batch

The 33 group-E abilities.

**Earlier status:**
- 32 rows read "excluded (auto: vortex)", the 2026-10-09 R3 auto-exclusion. There is no user decision on them.
- Sword of Teclis carries the user's own skip (2026-10-08): "Skip - it's a magic-resource ability (excluded scope)".
- Groundbreaker uses the exact blast of Thundermace, which the tracker lists as "skipped (unsuitable: vortex)".

**Where the facts come from:**
- the blast radii, damage and the game's "affects allies" flag: the vortex table, extracted this round
  (`gamedata\wh3\battle_vortexs.tsv`, 313 rows);
- the rest: `tools\fact_sheet_open.py`.

**Precedent:** five blasts centred on the caster that cannot hurt our units already ship on `melee_unwavering`:
Bloodstorm, Halo of Maidenly Wrath, Evisceration, Giant Leap and Gaze of Khorne.

## 2. The rulings (user, 2026-11-15, all recommended)

| Group | Ruling |
|---|---|
| 13 blasts that cannot hurt our units | "Like Bloodstorm" |
| 5 blasts that do | "Melee, no friend near" |
| Emberstorm, Moon Flare | "Flying over enemies" |
| The buffs and hexes | "Look-alike set" |
| The 6 proposed for closing | "Close 5, Necrotic last" |

**A correction before the build:** the first proposal put the Phoenix dives on "in melee and flying". That would almost
never fire, because a flier that lands to fight is no longer flying (the Storm of the Night caveat from round 158). I
flagged it and asked again. The user chose "Flying over enemies".

## 3. The change (what you will see in battle)

**The 13 safe blasts on `melee_unwavering` (11 entries; Burp of Grom carries 3 keys).**
- **The abilities:** Burp of Grom, Blood-Forged Armour, Daemon Flask of Ashak, Feaster of Souls, Spurting
  Bile-Blood, Arsebelcher, Violent Wind, Whirlwind of Pleasure, Whirl of Weeping Blades, Hurricane of Death, Acid
  Burps.
- **When:** the caster is in melee and not wavering, exactly like Bloodstorm.
- **Armed state:** this family starts ARMED (A), by the round-151 ruling.

**NEW `melee_clear` (5): Groundbreaker, Burning Rage, Bloodbeast, Emergency Vent, Land Mine.**
- **When:** the caster is in melee and not wavering, AND none of our other units is within the blast radius + 10 m
  of the caster's centre.
- **The distances:** Groundbreaker 20 m, Burning Rage, Bloodbeast and Emergency Vent 25 m, Land Mine 35 m.

**NEW `fly_dive` (2): Emberstorm, Moon Flare.**
- **When:**
  - the Phoenix is flying (`is_currently_flying()` exactly true);
  - an enemy you can see is within 7 m of its centre (70% of the 10 m blast);
  - none of our other units is within 20 m.

**NEW `last_stand_clear` (1): Necrotic Explosion.**
- **When:** the Nurglings are at 10% health or less in melee, and none of our other units is within 25 m.
- **Note:** the blast destroys the unit itself.

**NEW `enemy_blob_vortex` (1): Ancient Chaos Frost Dragon Scale.**
- **What it is:** the blob attack rule (round 146), using the item's 7 m frost vortex in place of a projectile blast.
- **Target:** the enemy infantry within 21 m where the blast destroys the most value.
- **Conditions:** the caster standing still; none of ours within 17 m of the target.

**The look-alikes:**

| Ability | Family | Note |
|---|---|---|
| Maneater Smoke Bomb | `charge_or_melee` | +24 melee defence (rule 10), like Smoke Bomb |
| Verminous Valour | `wavering_self` | +8 morale |
| Heaven's Flash | `enemy_ground_melee` | -24 melee attack and defence in 35 m, one use |
| Slime Smoothie | `health_aura_ground` | like Gulyas |
| Slann Gold | `enemy_commander_value` | the spellcaster proxy, like the Leach Orb |
| Deathmaster's Sigil | `enemy_commander_value` | NEW class `commander_ground`: a Lord/Hero that is not flying; its 15 m blast hurts our units, so none of ours within 25 m of the target |

**Armed state:**
- The four NEW families start unarmed (M): their blasts can hurt our units, and Necrotic Explosion kills its own unit.
- Every other entry follows its family's existing default.

**Closed (tracker `rejected`, workbook `SKIPPED (user decision)`):**
- Mist Form, Shadowstrider, Deep Tunneling (teleports);
- Sword of Teclis (the user's 2026-10-08 skip kept);
- the Unidentified Hydra Head (a random effect; a 35 m blast that hurts our units).

**The generated table:** `FOURTH.VORTEX_TEXT` (`tools\gen_vortex_tables.py`), 10 keys. It holds the largest radius in
each ability's vortex chain, for the four new families and the Sigil. The build regenerates it from the game data and
refuses a mismatch.

## 4. The proof

| Run | Checks | Failures | File |
|---|---:|---:|---|
| FULL, run 1 | 6,760 | 0 | `h158_run1.txt` |
| FULL, run 2 | 6,760 | 0, byte-identical | `h158_run2.txt` |
| RED, pre-159 snapshot | 6,722 | 0; RED 22/22 | `h158_red.txt` |

**Section 158:** 20 worlds; both files make 40 runs.

| World | Situation | Result |
|---|---|---|
| BG1 | Burp of Grom in melee | cast |
| MC1 | Groundbreaker in melee, ours 100 m away | cast |
| MC2 | Groundbreaker, our Swordsmen 15 m away | none |
| MC3 | Groundbreaker not in melee | none |
| FD1 | Emberstorm flying over an enemy block | cast |
| FD2 | Emberstorm landed | none |
| FD3 | Emberstorm flying, enemy 40 m away | none |
| FD4 | Emberstorm over the enemy, our Swordsmen 15 m away | none |
| LS1 | Necrotic Explosion at 8% in melee | cast |
| LS2 | Necrotic Explosion at 50% | none |
| LS3 | Necrotic Explosion at 8%, ours 20 m away | none |
| SG1 | Deathmaster's Sigil, a grounded Vampire | cast at the Vampire |
| SG2 | the Vampire flying | none |
| SG3 | our Swordsmen 12 m from the Vampire | none |
| SL1 | Slann Gold, a Vampire plus Grave Guard | cast at the Vampire |
| FS1 | Frost Dragon Scale, Grave Guard 15 m away | cast at the Grave Guard |
| HF1 | Heaven's Flash, an enemy in melee | cast |
| SS1 | Slime Smoothie, the caster at 60% | cast (ground form) |
| SB1 | Maneater Smoke Bomb in melee | cast |
| VV1 | Verminous Valour wavering | cast |

**RED:** on the round-158 build, the 11 control worlds (BG1, MC1, FD1, LS1, SG1, SL1, FS1, HF1, SS1, SB1, VV1) cast
nothing in either file.

**Two fixes during the round:**
- **SS1 counted wrong at first:** the mock records ground-form casts in `W.ground_fires`, not `W.fires`. The section
  now counts both.
- **Three stale mirror pins:** harness 81's charge_or_melee count, harness 102's enemy_ground_melee sum, and harness
  157's enemy_commander_value count. All three were rebased (below).

## 5. Pins rebased

| Pin | Old | New |
|---|---:|---:|
| entries (harness; builder 11 gates) | 834 | 860 |
| keys | 889 | 917 |
| full-table iterations | 1,668 | 1,720 |
| multi-use charge-gate keys | 263 | 271 |
| wind-up keys | 253 | 258 |
| `range_real` fields | 329 | 333 |
| target classes | 31 | 33 |
| `melee_unwavering` (harness; builder 4) | 288 | 299 |
| `charge_or_melee` (harness incl. harness 81's `cm`; builder 2) | 36 | 37 |
| `wavering_self` | 3 | 4 |
| `enemy_ground_melee` (harness incl. harness 102's sum; builder) | 74 | 75 |
| `health_aura_ground` | 2 | 3 |
| `enemy_commander_value` (harness 157 section; builder round-158 gate) | 1 | 3 |
| SHOT keys (builder 3 gates) | 33 | 35 |
| tooltip mirror | - | + 4 wordings |

## 6. Build and install

- **`build_and_install159.py`:**
  - ROUND 123 to 159 gates OK.
  - The new gate checks the four families, their wiring, that they start unarmed, the Sigil's class, and the VORTEX
    table regenerated from the game data.
  - `MATCHES SOURCE: True` for all five files.
- **Installed pack:** md5 **`23b088aada7c4f68ab59601e6aabc1df`**, 1,638,511 bytes, `IDENTICAL True`. The new code is
  found in the installed pack.
- **Archived:**
  - `archive\packs\zz_test_deadly_onslaught_20261115_round159.pack`;
  - `archive\mod_source\round159\` (source md5 `bc7c4c9efa07b5570c7e723ff6c73148`, annotated md5
    `bb05f64f922053fdc680fafb01819f1b`).

## 7. Roster documents and audits

- **Workbook:** `docs\WH3_abilities_master_v45_2026-11-15.xlsx` plus `.ods`; `XLSX v45 VERIFY OK`.
  - 917 implemented, 32 skipped, 88 families.
  - The 28 rows carry their texts and the 5 closed rows their decision.
  - Earlier rows are kept; v1 to v44 are byte-unchanged (84 files).
- **Tracker:** the 33 rows plus section 10.37.
- **Database:** four family texts; `DATABASE VERIFY OK` (0 army-bar keys among the 917).
- **Audits:** `WHEEL-STATUS AUDIT OK`; trigger audit R1 to R8 all 0.
- **Progress page:** 917 automated, 206 decided, 0 open.
- **CLAUDE.md:** a BEL control byte in section 1c (`tools\audit_triggers.py`, from an old heredoc) was repaired.

## 8. Not done

**Not seen in the game.** Rounds 156 to 159 wait for the next battle, from log byte 689,926,854.

**Honest notes:**
- **Spurting Bile-Blood:** 2 uses with a table recharge of 0. The charge hold is 0, so once both uses are spent the
  mod may keep sending accepted-but-empty casts. They come at most every 9 s: the recharge lock is the 9 s effect.
- **The caster's own blast:** whether the caster is immune to it is not stated in the game data. `melee_clear` never
  counts the caster itself.
- **Feaster of Souls:** "one enemy unit" is read from a field name only.
