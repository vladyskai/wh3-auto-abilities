# Round 140: the QA battles of 2026-11-13; shooting and moving; Blooood! when running (sign-off round)

Date: 2026-11-13. Harness: `harness139.lua`. Release folder: `mod_source\releases\20261113_moving_running_harness139\`.

## 1. The battles (the log cut from byte 446,198,331: 45 MB, 4 sessions; never opened whole)

| Session | Battle | Army | Result |
|---|---|---|---|
| 1 | QA 2 | Skaven: Grey Seer, Warlord, 8 Clanrats | Rally! fired for a wavering Clanrat unit 11.3 m away (157 s) and when the Warlord wavered (226 s). Unholy Clamour not testable (no DLC). |
| 2, 3 | QA 3, twice | Chaos Lord, Hellcannon, giant, dragon ogre | Boom! cast on its cast point (69 s; 52.5 s). In session 2 it also cast at 159 s while running. Blooood! never fired. |
| 4 | QA 5 | Tomb Kings: Settra, Khalida, Arkhan, Necrotect, Liche High Priest, 8 Skeleton Warriors, Ushabti, Sepulchral Stalkers | Every armed ability fired; the user saw two problems, analysed below. |

Battle 4 (Cathay): no DLC.

**Boom! while running.**
- The Hellcannon's last shot was at 135.25 s, and it lost its target at 137.75 s.
- The firing flag stays ON for max(2 x reload, 20 s) = 24 s after the last shot, so that pauses between volleys don't
  switch it off.
- Boom! cast at 159.0 s, half a second before FIRING OFF (159.5 s); at 160 s the snapshot reads `moving=yes`.

**Blooood! never fired.** A Hellcannon cannot be given a non-missile attack order, so the charge window (round 134)
never opens.

**The Necrotect's Restore** (heal, 24 s, recharge 60 s, 2 uses, 100 m -> 70 m bound):
- It heals constructs only: the game's own rule is `unit_is_not_construct`. Skeleton Warriors and characters are
  never valid targets, at any distance.
- 208 s: cast on the Sepulchral Stalkers (74% health, 35.2 m): ACCEPTED.
- 268 s: the Stalkers at 12% health, 40.7 m away, inside the 70 m bound: REJECTED "on cooldown". The 60 s recharge
  starts when the 24 s effect ends, so it was ready only at about 292 s. The Stalkers were last seen at 274 s.
- Distance was not the cause. The mod measures `unit_distance`, which is edge to edge (the shortest possible
  measure), against 70% of the game's range.

**The cooldown reducer the user saw misused** is Arkhan's Staff of Nagash ("Own ability recharge: -30 s"), which fires
on `melee_unwavering` whether or not anything is recharging. Scroll of Power (-60 s in the game data; the user's
campaign shows -90 s, probably a bonus) fires on `ushoran_health`.

## 2. The rulings (user, 2026-11-13)

- **The firing flag:** *"Unless the unit can fire while moving, shooting and moving are incompatible."*
- **Blooood!:** "Running, any time".
- **The 9 recharge reducers:** *"We should go one by one, maybe the other effects of those active abilities are more
  important."* This is a separate review.

## 3. The change

- **`FOURTH.can_shoot_now(unit)`:**
  - a unit whose `is_moving()` is true is not shooting, unless its type is in the GENERATED fire_move set (233 types,
    unit attribute `mounted_fire_move`, `tools\gen_fire_move_keys.py`);
  - an unreadable `is_moving()` keeps today's behaviour;
  - it guards `FOURTH.shooting_past_cast_point`, `FOURTH.ammo_fraction_if_firing` and Missile Mirror's
    `FOURTH.enemy_shooting`, so every firing-flag trigger follows the rule.
- **NEW `self_running` (Blooood!):** `is_moving_fast()` exactly true, not routing; cast on self. `charge_only` 5 -> 4.

## 4. The proof

| Run | Checks | Failures | File |
|---|---:|---:|---|
| harness138 on the new source (before the rebase) | 6,018 | 12: the charge_only count pins and the tooltip mirror | (not kept) |
| FULL, run 1 | 6,049 | 0 | `h139_run1.txt` |
| FULL, run 2 | 6,049 | 0, byte-identical | `h139_run2.txt` |
| LIGHT | 2,868 | 0 | `h139_light.txt` |
| RED, pre-140 snapshot (light) | 2,854 | 0; RED 8/8 | `h139_red.txt` |

Section 139 (14 worlds):
- **Boom!:**
  - B1: the Hellcannon shooting while standing: one cast.
  - B2: shooting while moving: no cast. This reproduces the field bug on the RED build.
- **Hail of Fire:**
  - H1: Outriders (they fire on the move) moving and shooting: one cast.
  - H2: Handgunners moving and shooting: no cast.
- **Missile Mirror:** M1: enemy Handgunners shooting while moving: no cast.
- **Blooood!:**
  - R1: the Hellcannon running: one cast.
  - R2: standing: no cast.

**RED** (the round-139 build): B2, H2 and M1 cast; R1 casts nothing.

## 5. Build and install

- **`build_and_install140.py`:**
  - ROUND 123 to 140 gates OK;
  - the fire_move table matches the game data;
  - `MATCHES SOURCE: True` for all five files.
- **Installed pack:** md5 **`76cc9ff49ac96ac6ee89fa12372576b1`**, 1,355,810 bytes, `IDENTICAL True`.

Archived:
- `archive\packs\zz_test_deadly_onslaught_20261113_round140.pack`;
- `archive\mod_source\round140\` (source md5 `374d5eea907bc2a3c1d2d8f761aa4d6c`, annotated md5
  `a72f98b992da6c516fb8a868c81856f5`).

## 6. Roster documents

- **Tracker:** 1 row updated, plus section 10.22.
- **Database:** the new family text; `DATABASE VERIFY OK`.
- **Workbook:** `docs\WH3_abilities_master_v32_2026-11-13.xlsx` plus `.ods`.
  - Checked by `XLSX v32 VERIFY OK`.
  - 26 shooting rows carry the moving rule; 60 families.
  - v1 to v31 are byte-unchanged (58 files).
- **Wheel audit:** OK.
- **Progress page:** rebuilt.
- **Trigger audit:** re-run; still empty.

## 7. Not done

- **The one-by-one review of the 9 recharge reducers.**
- **Not tested in the game yet:** Boom! and Blooood! after this round.
- **Rally!'s earlier waverers:** Clanrats wavered from 115 s, before Rally!'s first cast at 157 s. The log records the
  distance only of the ally it picks, so whether those early waverers were beyond 24 m is not proven.
