# Round 146: the blob trigger (sign-off round)

Date: 2026-11-13. Harness: `harness145.lua`. Release folder: `mod_source\releases\20261113_blob_trigger_harness145\`.

## 1. The rulings (user, 2026-11-13)

After the map probe's battle 1 (`docs\WH3_map_probe_battle1.md`):

- **Firing rule: "A. Density line".** Fire at the best safe enemy infantry unit when the blast around its centre would
  cover at least half of what it covers inside a tightly packed infantry block: `round(0.5 x pi x R^2 / 2.368)`.
  That is 17 soldiers for a 5 m blast, 66 for 10 m and 149 for 15 m (1 m: 1, 2 m: 3, 3 m: 6, 4 m: 11, 6 m: 24, 7 m: 33,
  8 m: 42, 9 m: 54, 12 m: 96).
- **Friendly margin: "10 m".** No soldier of ours within the blast radius + 10 m of any part of the target unit.
- **Scope: "79 open attacks".** The open group B attacks whose projectile explodes.

## 2. What the game data said first

- **All 112 open group B attacks are aimed at an enemy unit.** The trigger chooses which unit, not the exact spot.
- **79 explode, and all 79 can hurt our units** (`projectiles.can_damage_allies` and
  `projectiles_explosions.affects_allies`). The other 33 are direct effects (24) or non-exploding shots (9).
- **Blasts are small:** median 5 m, 72 of 79 under 10 m, the largest 15 m (Experimental Explosive). An infantry block is
  20-30 m wide, so most blasts cover part of one unit; overlapping units matter for the bigger blasts.
- **2 excluded:** Dead Eye and Focused Shot (1 m sniper shots the game lets target single-entity units only:
  `unit_is_not_single_entity`). A blob can never be their target, so they stay open.
- **No slows** among the 77 (rule 10 is not in play), checked against the effect text.
- Full list: `docs\WH3_blob_candidates_2026-11-13.md` (`tools\list_blob_candidates.py`).

## 3. The change (what you will see in battle)

- **77 new entries / 77 keys** on the new `enemy_blob` family, each with its own badge.
- When armed, the ability looks at the live map each poll:
  1. **Enemy infantry we can see:** an infantry class, NOT in the generated large set (the engine calls Fell Bats,
     Devils, the Varghulf and the Zombie Dragon infantry), not flying, at least 10 men, and visible to our side.
     An unreadable visibility means no cast.
  2. **Safety:** a target is skipped when any of our units' estimated rectangles comes within blast + 10 m of its
     rectangle (exact rectangle-to-rectangle distance, corners included).
  3. **Score:** the enemy infantry soldiers the blast would cover around the target's centre. 19 points spread over
     the blast circle each add the soldier density of every enemy block under them, so overlapping blocks count twice.
  4. **Cast:** at the best safe target, if its score reaches the line. Just before the cast the map is rebuilt and the
     target must still be safe and reach the line.
- **The log line** names the target, the soldiers in the blast, the line, the units touched and how far our nearest
  soldier is.
- **Generated tables** (the build refuses a pack that differs from the game data):
  - `FOURTH.BLAST_TEXT`: the 77 blast radii;
  - `FOURTH.SPACING_TEXT`: the close spacing of 535 infantry types (others use 1.48 x 1.6 m);
  - `FOURTH.PACKED_M2 = 2.368`.
- **Eight new 70% constants:** 55 m -> 38, 60 -> 42, 80 -> 56, 130 -> 91, 250 -> 175, 350 -> 245, 400 -> 280,
  600 -> 420.
- **Tables:** 66 wind-ups and 70 charge holds added; the lock table re-derived (637 -> 710 keys).
- **New tools:**
  - `tools\extract_db_table.py`: any game table, e.g. `projectiles_explosions`;
  - `tools\gen_blob_tables.py`;
  - `tools\list_blob_candidates.py`.

**A design fix made before shipping:** the first draft spread each unit's soldiers over a 3 x 3 grid. For a 5 m blast
that counted 18 soldiers where a packed 120-man block really puts about 31, which would have made small blasts
almost never fire. The circle-sampling score replaced it before any test was trusted.

## 4. The proof

| Run | Checks | Failures | File |
|---|---:|---:|---|
| harness144 on the new source (before the rebase) | - | 108: count pins, plus the round-145 read-only span | (not kept) |
| FULL, run 1 | 6,339 | 0 | `h145_run1.txt` |
| FULL, run 2 | 6,339 | 0, byte-identical | `h145_run2.txt` |
| LIGHT | 3,158 | 0 | `h145_light.txt` |
| RED, pre-146 snapshot (light) | 3,120 | 0; RED 4/4 | `h145_red.txt` |

Section 145: Fireball (5 m blast, line 17, bound 210 m) and Dire Spirit Bear (10 m, line 66, bound 105 m), the caster
100 m from the enemy.

| World | Situation | Result |
|---|---|---|
| FB1 | a full Swordsmen block | one cast at it |
| FB2 | 20 men in one thin rank | none |
| FB3 | our Swordsmen 10 m behind its rear edge | none |
| FB4 | our Swordsmen 40 m away | one cast |
| FB5 | the enemy not visible | none |
| FB6 | the Devils (large, the engine calls them infantry) | none |
| FB7 | no alliance read | none |
| FB8 | a thin block nearer, a full block further | the cast goes at the full one |
| SB1 | a full block | one cast |
| SB2 | an 80-man block | none |

**RED:** FB1 and SB1 cast nothing on the round-145 build.

**Not covered by a world:** the target lapsing between the pick and the cast. The re-check is in place and pinned, but
no world moves a unit in that instant.

## 5. Pins rebased

| Pin | Old | New |
|---|---:|---:|
| entries (harness; builder 11 gates) | 722 | 799 |
| keys | 777 | 854 |
| full-table iterations | 1,444 | 1,598 |
| multi-use charge-gate keys | 176 | 246 |
| wind-up keys | 169 | 235 |
| `range_real` fields (harness; builder 2) | 217 | 294 |
| target classes (harness; builder) | 24 | 26 |
| round-145 read-only span end (harness; builder) | the evaluator table | the round-146 block |
| tooltip mirror | - | + 1 wording |

## 6. Build and install

- **`build_and_install146.py`:** ROUND 123 to 146 gates OK; `MATCHES SOURCE: True` for all five files.
- **Installed pack:** md5 **`1d2b92d73019956836328a35dd2ade5c`**, 1,488,123 bytes, `IDENTICAL True`.
- Archived: `archive\packs\zz_test_deadly_onslaught_20261113_round146.pack`; `archive\mod_source\round146\` (source md5
  `e439dafc23b1708c273b9d350e0fade0`, annotated md5 `a42ebe00bca5db6d10944614dea24f34`).

## 7. Roster documents

- **Tracker:** 77 rows on `enemy_blob` and notes on the 2 excluded snipes, plus section 10.27.
- **Database:** 1 family text; `DATABASE VERIFY OK`.
- **Workbook:** `docs\WH3_abilities_master_v37_2026-11-13.xlsx` plus `.ods`; `XLSX v37 VERIFY OK`; 854 implemented,
  269 not implemented (27 skipped), 74 families; v1 to v36 byte-unchanged (68 files).
- **A verifier hole found and closed:** the first v37 verifier took the 77 keys from "open abilities in the newest
  workbook". v37 itself marks them implemented, so the check was empty. It now reads the keys from the mod source,
  and it passed again with all 77 checked.
- **Wheel audit:** OK. **Trigger audit:** R1 to R8 empty. **Progress page:** 68 still open.

## 8. Not done

- **Not tested in the game.** The next battle starts at log byte **513,464,904**. Arm a few of these attacks (Fireball,
  breaths, bombs) against an infantry army.
- **Performance is unmeasured in battle.** Each armed blob attack reads the map at most once per poll (it is cached for
  the tick and rebuilt only for the pre-cast re-check).
- **Still open:** the 33 non-exploding group B attacks, Dead Eye and Focused Shot, and group E.
- **A possible later step (the user chose not to now):** move the already-automated exploding attacks onto the same
  safety rule.
