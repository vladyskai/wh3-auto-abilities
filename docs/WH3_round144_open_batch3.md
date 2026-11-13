# Round 144: open batch 3 (the rest of group C) (sign-off round)

Date: 2026-11-13. Harness: `harness143.lua`. Release folder: `mod_source\releases\20261113_open_batch3_harness143\`.

## 1. The rulings (user, 2026-11-13)

**Earlier status:** all 13 read "excluded (auto: no effect text available)", from before the game data could be read.
None had a user decision in the tracker.

| Ability (unit) | Effect (game data) | Ruling | Family | Bound |
|---|---|---|---|---|
| Hag's Denial | Damage resistance +40, Cannot Die, 44 s, 1 use | "10%, melee or fire" | `self_last_stand` (NEW) | self |
| Ruinshelter (Mistwalkers) | Armour +45, MA +8, MD +10, speed -60%, 60 s | In melee | `melee_unwavering` | self |
| Rock Bottom (Rogue Idol RoR) | Refills 30% of its ammo, 350 damage to itself | "wait until no ammo left" | `self_out_of_ammo` (NEW) | self |
| Morikhane, the Black Armour | Reflects missiles 14 s (not artillery) | Under fire | `under_fire` | self |
| Hunter's Call (Hertwig) | MD +24, Unbreakable, self + allies | Like Stand Your Ground | `melee_or_wavering_aura` | 24 m (of 35 m) |
| Icon of the King | Heal + resurrect, self + allies; the game excludes living units | Non-living allies only | `health_aura_self_undead` (NEW) | 24 m (of 35 m) |
| The Gold Standard | Invulnerable 13 s, cast on an ally | Lowest-health ally in melee | `ally_hurt_melee` (NEW) | 70 m (of 100 m) |
| Banner of Hellfire | 5 dmg/s to enemies around it, 17 s | In melee | `melee_unwavering` | self |
| Ghostly Howl (Banshee) | 16 dmg to 25 models, Ld -16; only an enemy below half morale | Closest wavering enemy | `enemy_wavering` (NEW) | 52 m (of 75 m) |
| Petrifying Gaze (Cockatrice) | Slows 25-75%, then cannot move; 2 uses | Fast enemy (round-136 immobiliser ruling) | `enemy_fast_near_ally` | 35 m (of 50 m) |
| Storm of Blades (Wardancers) | Stance, no end time | Skip | none (skipped) | - |
| Whirling Death (Bladesingers) | Stance, no end time | Skip | none (skipped) | - |
| Cloak of the Dunes | Stalk + unspottable | Skip | none (rejected, stealth) | - |

**A correction during the proposal:** for Hag's Denial I wrote that a one-use Cannot Die "pays off when the unit is
about to die" and then recommended 50%, which does not match that reasoning. The user caught it. The ruling is 10%.
Honest note: at 10% a single big hit between two polls (0.25 s) can still kill a single-model hero before the order
lands. That is the price of firing late; the user chose it.

## 2. The change (what you will see in battle)

- **10 new entries / 10 keys**, each with its own badge.
- **Hag's Denial:** fires only when her health reads 10% or less AND she is in melee or under missile fire. An
  unreadable health never fires.
- **Rock Bottom:** fires when the Rogue Idol's ammunition reads 0.
- **Icon of the King:** fires when the carrier or a non-living friendly unit within 24 m is at 75% health or less
  (the generated undead set: a living ally never arms it). Re-checked just before the cast.
- **The Gold Standard:** casts on the most hurt friendly unit within 70 m that is in melee (the carrier counts).
  Re-checked just before the cast: still in melee, still hurt, still in range.
- **Ghostly Howl:** casts on the closest wavering enemy within 52 m (wavering is the nearest live read to the game's
  "below half morale"). A small new enemy picker, because the shared one only offers fighting or shot enemies.
  Re-checked just before the cast: still wavering.
- **Ruinshelter, Banner of Hellfire, Morikhane, Hunter's Call, Petrifying Gaze:** existing families.
- **Tables:** wind-ups Rock Bottom 1 s, Morikhane 1 s, Ghostly Howl 3 s; charge holds Hunter's Call, Icon of the King,
  Petrifying Gaze 120 s each; the lock table re-derived 628 -> 637 keys.
- **The three skipped abilities** have no entry; the build refuses a pack that contains any of their keys.

## 3. The proof

| Run | Checks | Failures | File |
|---|---:|---:|---|
| harness142 on the new source (before the rebase) | - | 135: count pins | (not kept) |
| FULL, run 1 | 6,273 | 0 | `h143_run1.txt` |
| FULL, run 2 | 6,273 | 0, byte-identical | `h143_run2.txt` |
| LIGHT | 3,092 | 0 | `h143_light.txt` |
| RED, pre-144 snapshot (light) | 3,034 | 0; RED 10/10 | `h143_red.txt` |

Section 143 (19 worlds, both files = 38):
- **Hag's Denial:** HD1 8% in melee: one cast. HD2 8%, neither in melee nor shot: none. HD3 20% in melee: none.
  HD4 8% under fire: one cast.
- **RS1** Ruinshelter in melee, **BH1** Banner in melee: one cast each.
- **RB1** no ammunition: one cast. **RB2** 5 shots left: none.
- **MK1** under fire: one cast. **MK2** not: none.
- **HC1** an ally 20 m away in melee: one cast on self.
- **IK1** an undead ally at 50%: one cast. **IK2** a living ally at 50%: none.
- **GS1** an ally at 50% in melee: one cast ON that ally. **GS2** the same ally not in melee: none.
- **GH1** a wavering enemy: one cast on it. **GH2** not wavering: none.
- **PG1** an enemy moving at 8 m/s 20 m away: one cast on it. **PG2** standing still: none.

**RED:** on the round-143 build, HD1, RB1, IK1, GS1 and GH1 cast nothing.

**Not covered by a world:** a lapse between the pick and the cast (for example the Gold Standard's ally leaving melee
in that instant). The re-check code is pinned by token, not exercised.

## 4. Pins rebased

| Pin | Old | New |
|---|---:|---:|
| entries (harness; builder 11 gates) | 712 | 722 |
| keys | 767 | 777 |
| full-table iterations | 1,424 | 1,444 |
| multi-use charge-gate keys | 173 | 176 |
| wind-up keys | 166 | 169 |
| `melee_unwavering` (harness; builder 4 gates) | 307 | 309 |
| `range_real` fields (harness; builder 2) | 215 | 217 |
| `ally_range_real` fields (harness; builder) | 56 | 57 |
| `under_fire` (builder) | 3 | 4 |
| `enemy_fast_near_ally` (harness; builder) | 7 | 8 |
| tooltip mirror | - | + 5 wordings |

## 5. Build and install

- **`build_and_install144.py`:** ROUND 123 to 144 gates OK; `MATCHES SOURCE: True` for all five files.
- **Installed pack:** md5 **`826ef8834fbc437c35ecc86a298b931e`**, 1,413,633 bytes, `IDENTICAL True`; the new
  evaluator name is in the installed pack.

Archived (after the md5 changed and the marker was found):
- `archive\packs\zz_test_deadly_onslaught_20261113_round144.pack`;
- `archive\mod_source\round144\` (source md5 `898dc8cf67088aa9b0d0d8bbd01427b5`, annotated md5
  `19843f61572f904d45424f407bfb59b7`).

## 6. Roster documents

- **Tracker:** 13 rows (10 implemented, 2 skipped, 1 rejected), plus section 10.26.
- **Database:** 5 family texts; `DATABASE VERIFY OK`.
- **Workbook:** `docs\WH3_abilities_master_v36_2026-11-13.xlsx` plus `.ods`; `XLSX v36 VERIFY OK`; 777 implemented,
  346 not implemented (27 skipped), 73 families; v1 to v35 byte-unchanged (66 files).
- **Wheel audit:** OK. **Trigger audit:** R1 to R8 empty. **Progress page:** 145 still open.

## 7. Not done

- **Not tested in the game.**
- **Group C is finished.** What is open now is group B (attacks cast at an enemy: magic missiles, bombs, breaths) and
  group E (self-centred explosions and whirlwinds, where no change was proposed).
