# Round 132: audit batch 1 and the patch-9.0.5 data fixes (sign-off round)

Date: 2026-11-08. Harness: `harness131.lua`. Release folder:
`mod_source\releases\20261108_audit1_patch905_harness131\`. The loop this round follows:
`docs\WH3_process_proposal_2026-11-08.md` (agreed 2026-11-08). The audit:
`docs\WH3_trigger_audit_2026-11-08.md`. The patch drift: `docs\DRIFT_2026-11-08_patch905.md`.

## 1. The rulings (user, 2026-11-08, all as recommended)

- **Enchanted Metallurgy and Master of Alchemy (8): "Add the shooting half".** This completes the
  user's own 2026-10 rule, "When self or ally in range in melee. When ally in range is shooting."
  Only its melee half had been built, because the mod could not see shooting then.
- **Embers of the Phoenix and Horn of Vaul: "Same as Metallurgy".**
- **The Seerstaff of Saphery and Harmonic Convergence: "Self, else an ally".**
- **Boom!: "When it is shooting".**
- **Also from the user, the same day:** no self-playing QA build. The user fights the QA battle, and
  Claude reads the log.

## 2. The change

| Ability | Was | Now | Fires when |
|---|---|---|---|
| Enchanted Metallurgy, Master of Alchemy (4 + 4), Embers of the Phoenix, Horn of Vaul | melee (Metallurgy: self or an ally within 24 m in melee) | `melee_or_shooting_aura` (NEW) | the same melee rule, OR the caster or any unit within 24 m (70% of 35 m) shooting past its cast point; cast on the caster |
| The Seerstaff of Saphery, Harmonic Convergence | the caster in melee | `melee_or_shooting_self_or_ally` (NEW, 140 m of 200 m) | the caster in melee or shooting: itself; otherwise the closest ally in melee or shooting |
| Boom! | in melee | `self_shooting` (NEW) | the unit itself shooting past its cast point |

**Patch 9.0.5** (packs dated 2026-11-03), from the re-extracted game data:

| Ability | Patch change | Mod change |
|---|---|---|
| Eternal Gaze | reach 100 -> 50 m | bound 70 -> 35 m (the old bound would have made the caster walk) |
| Aken-seth, the Staff of Pain | unlimited -> 3 uses, 120 s | a 120 s charge hold |
| Okkam's Mindrazor | wind-up 1 -> 0 s | its wind-up row removed |
| Overseer of the Unseen | can no longer target a flying unit | a flying ally is skipped |
| Stormfiend Windlaunchers | reload 13 -> 14 s | the reload table regenerated |

## 3. The proof

| Run | Checks | Failures | File |
|---|---:|---:|---|
| harness130 on the new source (before the rebase) | 5,638 | 46, every one a pin in section 4 | (not kept) |
| FULL, run 1 | 5,699 | 0 | `h131_run1.txt` |
| FULL, run 2 | 5,699 | 0, byte-identical | `h131_run2.txt` |
| LIGHT | 2,518 | 0 | `h131_light.txt` |
| RED, pre-132 snapshot (light) | 2,478 | 0; the RED checks reproduce every fixed fault | `h131_red.txt` |

Section 131 (61 checks, live and annotated, 26 worlds):

- **Enchanted Metallurgy:**
  - M1: an ally shooting 20 m away triggers it.
  - M2: an ally 30 m away does not.
  - M3: the caster in melee still triggers it.
- **The Seerstaff of Saphery:**
  - S1: an ally in melee 100 m away gets it.
  - S2: an ally 150 m away does not.
  - S3: the caster shooting gets it itself.
- **Boom!:**
  - B1: shooting triggers it.
  - B2: melee does not.
- **Eternal Gaze:**
  - G1: no cast at 40 m.
  - G2: cast at 30 m.
- **Aken-seth:** A1: cast and the 120 s hold armed.
- **Overseer of the Unseen:**
  - O1: a flying ally is skipped.
  - O2: a ground ally gets it.

**RED** (round-131 build), 10/10:

- M1 and S1 cast nothing.
- G1 casts at 40 m (the old 70 m bound: the move-order risk).
- A1 arms no hold.
- O1 casts on the flier.

**Harness corrections during the round:**

- My world total was 30; there are 26 worlds.
- One RED label said "pre-131"; it now says "pre-132".

## 4. Pins rebased (old -> new, why)

| Pin | Old | New | Why |
|---|---:|---:|---|
| `melee_unwavering` | 354 | 349 | Embers, Horn of Vaul, Seerstaff, Harmonic Convergence, Boom! moved |
| `metallurgy_melee` | 8 | 0 | the 8 keys moved to `melee_or_shooting_aura` (its evaluator stays as the melee arm) |
| harness-89 Metallurgy entry check | trigger `metallurgy_melee` | trigger `melee_or_shooting_aura` | the same move |
| `ally_range_real` fields | 44 | 46 | Seerstaff, Harmonic Convergence (200 m) |
| charge-gate keys | 164 | 165 | Aken-seth (patch) |
| wind-up keys | 165 | 164 | Okkam's Mindrazor (patch) |
| tooltip mirror | 52 | 55 | the three new wordings |

Builder gates rebased:

- `melee_unwavering` 354 -> 349 (4 gates);
- `metallurgy_melee` 8 -> 0 (2 gates);
- `ally_range_real` 44 -> 46 (1 gate).

## 5. Build and install

`build_and_install132.py` adds the round-132 gate. Results:

- ARMY-BAR GATE OK.
- `RELOAD TABLE MATCHES the game data` (patched).
- ROUND 123 to 132 gates OK.
- `MATCHES SOURCE: True` for all five files.
- Installed pack md5 **`47efd2465d26047dde59f0fed6d03e51`**, 1,178,331 bytes, `IDENTICAL True`.
- Both new log reasons are in the installed pack.

Archived: `archive\packs\zz_test_deadly_onslaught_20261108_round132.pack` and
`archive\mod_source\round132\` (source md5 `70db1cbf190548e9e2cda8a417b6ee68`, annotated md5
`42299d5c31719f3362d36e19a031a3a6`). Pre-round snapshots: `docs\backups\round132\`. The pre-patch game
data: `gamedata\snapshot_2026-11-08_pre905\` (local only; game data is not in the repository).

## 6. Roster documents

- **Tracker:** 17 rows updated, plus section 10.13.
- **Database:** regenerated, `DATABASE VERIFY OK`.
- **Workbook:** `docs\WH3_abilities_master_v24_2026-11-08.xlsx` plus `.ods`, checked by
  `XLSX v24 VERIFY OK`.
  - Every implemented row's family matches the mod.
  - Gate notes are kept.
  - The 4 patch rows are corrected.
  - 54 families.
  - v1 to v23 byte-unchanged (42 files).
- **Wheel audit:** `WHEEL-STATUS AUDIT OK`.
- **Progress page:** rebuilt: 255 of 752 automated abilities seen firing in a battle.
- **Trigger audit:** re-run: R1 and R2 are now empty; 88 candidates remain (R3 23, R4 19, R5 7, R6 25,
  R7 14).

## 7. Not done

- **Not tested in the game yet.** This round's QA step is the user's battle; Claude reads the log.
- **The QA army list** for a reusable custom battle is not written yet. It is the next step of the
  loop.
- **Next audit batches:** R5 (protection against shots, 7), then R3, R4, R6, R7.
