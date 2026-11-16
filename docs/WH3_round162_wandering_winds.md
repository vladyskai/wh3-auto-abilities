# Round 162: the wandering winds (sign-off round)

Date: 2026-11-16. Harness: `harness161.lua`. Release folder: `mod_source\releases\20261116_wandering_winds_harness161\`.

## 1. The batch

The 34 in-wheel abilities under the 2026-10-09 family rule "Vortex / wandering wind (friendly fire)". That was a RULE
written before the round-145 enemy map, never a ruling on these abilities one by one. Wrath of Manann was the first of
them seen uncovered (Bretonnia battle, 2026-11-16). The facts come from the game's vortex table
(`gamedata\wh3\battle_vortexs.tsv`) and `unit_spec_abil`.

## 2. The rulings (user, 2026-11-16)

| Group | Ruling |
|---|---|
| 12 straight waves | "Clear path, most value and not currently moving"; "some abilities are more random than others ... the ones that have low randomness might be okay with a lower safety buffer" |
| 16 wanderers | "Worst-case reach (Rec.)" |
| The other 6 | "Blob rule; close 2 (Rec.)" |
| The safety buffer | "Simulated 95%" |
| The Burning Head x2, Arnzipal's Black Horror | "Automate with the big buffer" |

**Why the target must stand still:** the waves take 3 to 5 s to cast. The path and the safety corridor are computed from
the target's position at the decision. A moving target walks out of the path, and the real path then starts somewhere
else, possibly through our units. The same reasoning holds for the wanderers and the static areas: they launch at the
target's position too. So the rule applies to all 32.

## 3. The change (what you will see in battle)

All 32 start on M (two NEW families).

**NEW `enemy_wave` (12):** Wrath of Manann, Wind of Death, Seafang, The Burning Head x2, Bound Fiery Convocation, Fiery
Convocation, Burning Alignment, Hell Hammer, Nightmaw, The Penumbral Pendulum, Arnzipal's Black Horror.
- **Conditions:** the caster stands still, and the target is a visible enemy in range that also stands still.
- **The path:** it starts the game's 24 m offset plus the target's half extent before the target, and runs
  speed x duration metres along the caster-to-target heading.
- **The safety corridor:** none of our units, the caster counting, within radius + 10 m of the path's start, widening to
  radius + the simulated 95% sideways drift + 10 m at its end. A wave cannot drift where it starts. Applying the full
  width along the whole path would put the caster itself inside Wrath of Manann's buffer at every legal range, so it
  would never fire.
- **The pick:** the most enemy value (live `strategic_value`) touched by the path.

**NEW `enemy_wander` (20):**
- **The abilities:**
  - the 15 wanderers: Banishment x3, Lesser Banishment, Lesser Chain Lightning, Flame Storm x2, The Gem of Sunfire,
    Gehenna's Golden Hounds, Gilded Horn of Galon Konook, Hounds of Orion, Sandstorm, Soul-slaying Hunger, Sword of
    Khaine, The Purple Sun of Xereus;
  - The Ruination of Cities (three straight 60 m spokes from the near edge, so its buffer is the whole spoke);
  - The Dwellers Below x2 (static 20 m);
  - Heaven's Gate and The Abyssal Swarm (the game marks them as not hitting allies: no friendly test).
- **Conditions:** the caster and the target stand still.
- **The target:** the visible enemy infantry blob that covers the blob density line and destroys the most value.
- **The safety ring:** none of our units within radius + the simulated 95% reach + 10 m of the target.

**Closed (tracker `rejected`):** Gehenna's Golden Globe and Wall of Wind & Fire. Their heading is not in the game data.

**The buffer table:** GENERATED `FOURTH.WW_TEXT` (`tools\gen_ww_tables.py`).
- **How:** 4,000 simulated paths for each of two readings of the turn field (+-angle and +-angle/2: the field's meaning
  is not documented), and the 95% line of the wider reading.
- **Reproducible:** fixed seeds per key, so the build re-derives it in about a second and refuses a mismatch.

| Ability | Radius | Path | 95% drift / reach | Clear distance |
|---|---:|---:|---:|---|
| Seafang, Fiery Convocation x2, Burning Alignment, Hell Hammer, Nightmaw, Penumbral Pendulum | 4-8 | 33-132 | 0 | radius + 10 along the whole path |
| Wrath of Manann | 6 | 70 | 17 | 16 m at the start, 33 m at the end |
| Wind of Death | 6 | 100 | 25 | 16 m to 41 m |
| Arnzipal's Black Horror | 10 | 140 | 64 | 20 m to 84 m |
| The Burning Head x2 | 7 | 180 | 109 | 17 m to 126 m |
| Banishment x3 | 12 | 36 | 16 | 38 m around the target |
| Purple Sun / Lesser Chain Lightning / Lesser Banishment | 10-12 | 18-22 | 11-12 | 33-34 m |
| Flame Storm x2, Gem of Sunfire | 10 | 54 | 19-20 | 39-40 m |
| Sandstorm | 12 | 56 | 46 | 68 m |
| The Ruination of Cities | 7 | 60 | 60 | 77 m + the target's half extent |
| The Dwellers Below x2 | 20 | static | 0 | 30 m |
| Heaven's Gate, The Abyssal Swarm | 5, 12 | | | no test (cannot hit allies) |

## 4. The proof

| Run | Checks | Failures | File |
|---|---:|---:|---|
| FULL, run 1 | 6,833 | 0 | `h161_run1.txt` |
| FULL, run 2 | 6,833 | 0, byte-identical | `h161_run2.txt` |
| RED, pre-162 snapshot | 6,811 | 0; RED 8/8 | `h161_red.txt` |

| World | Situation | Result |
|---|---|---|
| WV1 | Wrath of Manann: Grave Guard (800) standing 60 m ahead, Zombies (75) aside | cast at the Grave Guard |
| WV2 | Wrath of Manann: our Swordsmen 25 m beside the far half of the path | none |
| WV5 | Seafang (no drift): the same Swordsmen | cast (a low-drift wave needs less room) |
| WV3 | Wrath of Manann: the target moving | none |
| WV4 | Wrath of Manann: the caster moving | none |
| WN1 | Banishment: a 200-man block, ours 55 m away | cast at it |
| WN2 | Banishment: ours 25 m from the target | none |
| WN3 | Heaven's Gate: our Swordsmen fighting the block | one ground cast |
| WN4 | The Dwellers Below: ours 20 m from the target | none |

**RED:** on the round-161 build, the control worlds WV1, WV5, WN1 and WN3 cast nothing.

**Slips during the round, all fixed:**
- The first patch run stopped on a `%` in the generator's comment, after the entries were already written. Both files
  were restored from the round's backup and the whole patch re-ran.
- A guard tripped because `evaluate_enemy_wavering` contains `evaluate_enemy_wave`.
- A heredoc mangled a Windows path again (`\r`): the v46 verifier was then written with the Write tool. This is the
  CLAUDE.md lesson; I broke it twice this session.

## 5. Pins rebased

| Pin | Old | New | Why |
|---|---|---|---|
| entries (harness; builder 11 gates) | 860 | 892 | +32 |
| keys | 917 | 949 | +32 |
| full-table iterations | 1,720 | 1,784 | 2 x 892 |
| multi-use charge-gate keys | 271 | 287 | +16 |
| wind-up keys | 258 | 289 | +31 |
| `range_real` fields | 333 | 365 | +32 |
| target classes | 33 | 43 | +10 `not_flying` (the game's flying_currently rule) |
| builder round-160 gate: mod key count | 917 | 949 | the gate counts every key while re-deriving the wind-up set |
| harness 118 and builder round-118 dead-symbol token | `dwell` | ` dwell` (leading space) | the game's own key `the_dwellers_below` contains "dwell". Every form the round-118 deletion removed starts with a space; the narrowed token still finds 14 hits in `docs\backups\round118\pre118`. One token for one token, so the suite's boundary counts do not move. |
| tooltip mirror | - | + 2 wordings | |

## 6. Build and install

- **`build_and_install162.py`:** ROUND 123 to 162 gates OK. The new gate checks the two families, their wiring, the ww
  re-check, both starting unarmed, the two closed keys absent, and the WW table regenerated from the game data.
  `MATCHES SOURCE: True` for all five files.
- **Installed pack:** md5 **`5792ffbeaa36c6110448037d38314a06`**, 1,663,291 bytes, `IDENTICAL True`.
- **Archived:**
  - `archive\packs\zz_test_deadly_onslaught_20261116_round162.pack`;
  - `archive\mod_source\round162\` (source md5 `8158f2ad6a526aad89d16a36a3571e45`, annotated md5
    `92bf6f067983cf750353a1608979ab59`).

## 7. Roster documents and audits

- **Workbook:** `docs\WH3_abilities_master_v46_2026-11-16.xlsx` plus `.ods`; `XLSX v46 VERIFY OK`.
  - 949 implemented, 34 skipped by the user, 90 families.
  - The 32 rows carry their texts, the 2 closed rows their decision, and earlier rows are kept.
  - v1 to v45 are byte-unchanged (86 files).
- **Tracker:** the 34 rows plus section 10.40.
- **Database:** two family texts; `DATABASE VERIFY OK`.
- **Audits:** `WHEEL-STATUS AUDIT OK`; trigger audit R1 to R8 all 0.
- **Progress page:** 949 automated, 63 decided by the user, 111 open (all shut by an old rule).

## 8. Not done, and honest notes

- **Not seen in the game.** The next battle starts at log byte 735,692,926.
- **Unchecked assumptions:**
  - the wave heading is caster to target (the data says only "starts at the target's near edge");
  - the meaning of the turn field (the wider of two readings was used).
- **The Dwellers Below (20 m)** needs about 265 soldiers inside its circle to pass the blob density line, so it will
  fire only on dense, multi-unit blobs. The blob rule was the ruling.
- **The wanderers target infantry blobs only** (the blob rule), not lone monsters.
- **Still open, shut by an old rule (111):** 28 placed / static areas, 28 friendly-fire breaths, 19 own-troop auras, 22
  collection-time skips, 7 flanking, 5 mutually exclusive, 2 bombardment. Also your own 9 "skipped (revisit)".
