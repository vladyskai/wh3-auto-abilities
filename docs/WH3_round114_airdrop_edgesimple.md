# Round 114 — the air-drop rule is one comparison, plus a 0.2 s fast pass

2026-10-18 · source `mod_source/script/battle/mod/zz_test_deadly_onslaught.lua`
installed pack **`2cec3140e4d0838fa678187621ea55b0`** (5 files, all byte-identical to source)
release `mod_source/releases/20261018_airdrop_edgesimple_harness114/`
spreadsheet `docs/WH3_abilities_master_v15_2026-10-18.xlsx` (v14 superseded, v1–v14 byte-unchanged)

---

## 1. The user's ruling

> 1. I want the trigger to be checked much more frequently when armed and less than 30 meters from a
>    valid enemy unit.
> 2. Valid units are those who have more than 10 entities.
> 3. I trigger the moment distance between edges is below 0.1 meters. That's it.

> 1. Remove the "and it is infantry". No need for it now.
> 2. Current count 3. Let's try with 0.2 s for now.

## 2. The rule that ships

```
candidate = number_of_men_alive() > 0  AND  number_of_men_alive() > AIR_DROP_MIN_MEN (10)
valid     = that candidate's battle_unit:unit_distance(caster, enemy) is READABLE
chosen    = the NEAREST valid candidate by that distance
FIRE      = unit_distance(caster, chosen) < AIR_DROP_EDGE_M (0.10 m)
```

then the caster-side usage checks the row itself declares (`air_only` → `is_currently_flying()` exactly
true; `no_melee` → `is_in_melee()` not true), the self-centred cast on the **OWNER**, and the pre-cast
re-check (fresh handles: still alive, still > 10 models, edge gap re-measured — skip if it moved out).

`battle_unit:unit_distance()` is *"the shortest distance in metres between this unit and a supplied unit,
taking into account their bounding box rather than just working out the centre-to-centre distance"*
(`battle_unit.lua:160`) — the edge-to-edge gap the user asked for, with no radius read anywhere in the
decision.

### The four constants

| Constant | Ships as | Meaning |
| --- | --- | --- |
| `FOURTH.AIR_DROP_EDGE_M` | `0.1` m | fire below this edge-to-edge gap |
| `FOURTH.AIR_DROP_MIN_MEN` | `10` | a candidate needs **more** alive models than this |
| `FOURTH.AIR_DROP_NEAR_M` | `30` m | the fast pass runs while a valid enemy is this close |
| `FOURTH.AIR_DROP_FAST_S` | `0.2` s | the fast pass interval (registered as 200 ms) |

## 3. What was removed, and who else used it

Deleted from the evaluator and from the file:

| Removed | Kind | Still used elsewhere? |
| --- | --- | --- |
| `enemy_is_infantry` call in this evaluator | filter | **No** — the function itself stays in service for `enemy_ground_melee_infantry`, `enemy_ground_area`, `enemy_engaged_or_shot` and the `melee_skip_commanders` engagement set (3 remaining references, all outside this evaluator) |
| `initial_number_of_men()` single-entity guard | filter | **No** — the method is no longer read anywhere in the mod |
| `AIR_DROP_DELAY_S`, `AIR_DROP_ENEMY_LEAD`, `AIR_DROP_CASTER_DELAY_S`, `AIR_DROP_CASTER_LEAD`, `AIR_DROP_INHERIT` | four dials + flag | **No** |
| `AIR_DROP_CENTER_M` (6 m) | bound | **No** |
| `AIR_DROP_MODEL_RADIUS_M`, `AIR_DROP_RANKS`, `AIR_DROP_FRONTAGE_MIN_M`, `AIR_DROP_FRONTAGE_MAX_M` | frontage credit | **No** |
| `ad_frontage`, `ad_frontage_text`, `ad_seg_dist`, `ad_velocity`, `ad_lead`, `ad_project`, `ad_dial_text`, `ad_single_say`, `ad_single_clear`, `ad_centre_gap`, `ad_pos`, `ad_sep`, `ad_vec_text` | helpers | **No** — every call site was inside this evaluator or its pre-cast re-check, so the helpers were **deleted**, not left dead |

Kept: `ad_tag` (the ui-id tag), `ad_say` (the change-gated note), the new `ad_nearest` and `ad_pick`.
Verified mechanically: each of those tokens has **0** occurrences in the shipped source (harness 114
section 0, both copies).

## 4. The log, per decision

```
[1003] sky_junk_bomb nearest valid:'wh3_main_inf_zombie_0' entities=20 edge=0.04m (need < 0.10m) -> FIRING
[1003] sky_junk_bomb nearest valid:'wh3_main_inf_zombie_0' entities=20 edge=0.11m (need < 0.10m) -> NOT YET
[1003] sky_junk_bomb nearest valid:'<key>' entities=12 edge=0.20m (need < 0.10m) -> SKIPPED at re-check (...)
[1003] fast poll: ON (nearest valid 12.3m)
[1003] fast poll: OFF
```

The exact distance, the entity count, the enemy type and the **caster's ui id** are on every decision; a
repeated identical decision is de-duplicated (the fast pass runs 5×/s, so an unchanged line must not
repeat), and the `fast poll:` transition is written **once per change**.

## 5. The fast pass, and why it cannot double-cast

`FOURTH.ad_fast_pass` is registered as a **second model timer** at `AIR_DROP_FAST_S` (200 ms), wrapped in
its own `pcall` exactly like the poll (an escaping timer error kills every repeating callback in the
battle).

* it iterates **`FOURTH.ad_fast_abilities`** — the 12 air-drop entries, built at load — never `ABILITIES`;
* only for units that are **alive** and **armed** for that marker, and only in the conflict phase;
* only while a **valid enemy** (alive, > 10 models, readable distance) is inside `AIR_DROP_NEAR_M`;
* the cast goes through **`FOURTH.try_pair`** — the readiness + cooldown-hold + guard + charge + in-flight
  + per-unit-serialisation + `attempt_activation` sequence **extracted verbatim** from the poll body, so
  there is exactly **one copy** of the gate logic (the poll calls the same function);
* it never touches `tick_count`, the re-list, the heartbeat, the identity watch or the active set, and the
  global poll keeps `POLL_MS = 250` and its own registration.

**No double cast:** the guard is stamped (`tick_count`) **before** the call. Two fast ticks inside the same
poll window see an elapsed `0 < GUARD_TICKS` and the pair is not eligible; the charge / in-flight / serial
holds sit on top. Harness 114 world H: first fast tick fires, the second does not, five more do not, the
next poll does not — `1` cast, and exactly one `-> FIRING` picker line plus one `-> FIRING (re-checked)`.

## 6. Harness 114

`harness114.lua` = the harness-112 suite (4,492 checks, unchanged) + the round-114 section.
**4,614 checks / 0 failures**, run twice, byte-identical (`run1.txt` / `run2.txt` in the release dir).

| World | Proves |
| --- | --- |
| A0 | 20 models at **0.09 m** → FIRES, with the full decision line |
| A1 | 20 models at **0.11 m** → silent, `-> NOT YET` |
| B10 / B11 | **10 models at 0.00 m** is never a candidate (not even measured) / **11 models at 0.05 m** fires |
| C | a **20-model cavalry** unit (is_infantry() → false) at 0.08 m **fires** — the infantry filter is gone |
| D | a **one-model lord** at 0.00 m is excluded by the > 10 test, no decision line |
| E | nearest-of-two: 0.04 m chosen over 0.9 m |
| F | re-check: picked at 0.05 m, 0.20 m at the call → `-> SKIPPED at re-check`, no cast |
| G | fast poll **ON** at 20 m, OFF at 40 m — exactly one line each, silent afterwards |
| H | two consecutive fast ticks → **one** cast; five more + the next poll → still one |
| I | `unit_distance` raises → no candidate, no cast, no invented line |
| J | a non-air-drop ability armed + enemy at 0.00 m → nothing, no air-drop line (isolation) |

Pins (section 0, asserted against **both** copies): the four constants exactly once with their values;
the ten retired constants and thirteen retired helpers **absent**; `ad_nearest` filters on
`alive > FOURTH.AIR_DROP_MIN_MEN` and reads `FOURTH.eg_enemy_gap`; the decision is
`if dist >= FOURTH.AIR_DROP_EDGE_M then`; `FOURTH.try_pair` defined once and called twice; the fast pass
iterates `FOURTH.ad_fast_abilities` and gates on `AIR_DROP_NEAR_M`; `local POLL_MS = 250` once; the
0.2 s registration present; 12 entries / 689 markers; the new tooltip sentence; and the live file's
**5** `FOURTH.ad_tag(unit)` sites.

**Red control** (`H114_LIVE`/`H114_ANN` → `docs/backups/round114/pre114_*.lua`, the round-113 build):
**56 failures, every one in the round-114 section, none before it** (`red114.txt` in the release dir).

**Supersessions (documented in `post114.py`, nothing deleted):** rounds 108, 109, 110, 111 and 112 were
air-drop-only rounds whose subject was deleted — their check slots (66 / 99 / 149 / 134 / 105) answer
explicit **N/A** so the running count and the boundary pins are unchanged; round 107's `0y` pins and
A1–A10 worlds answer N/A by a renamed check call, while its **S1/S2/S3 serialisation worlds still run for
real** (their enemy is now 20 models at a 0.05 m gap, which fires under the new rule). Three other
structural pins were rebased for the new shape: the timer count (2 `bm:repeat_callback`), the
`unit_is_routing(unit)` count (3: definition + poll + fast pass), and the `gone`-break pin (the collect
now lives in `try_pair`, the break in its caller).

## 7. Build and install

```
source script/...   766,246 bytes   md5 a503fff0e7c978724036481aacb643e7
five files          all MATCHES SOURCE: True
built pack          md5 2cec3140e4d0838fa678187621ea55b0
installed           md5 2cec3140e4d0838fa678187621ea55b0   IDENTICAL True
round-trip (re-opened the INSTALLED pack with a fresh rpfm_server): all five byte-identical
zz_probe_dist.pack left installed (md5 d4e67cfb8bc562c7d6f0ff742909c13d, untouched)
```

## 8. Spreadsheet v15 and tracker

* `docs/WH3_abilities_master_v15_2026-10-18.xlsx` — all **19** air-drop rows carry the new rule text
  (per-row `air_only` / `no_melee` values stated); the Definitions sections **8–11 are marked RETIRED IN
  ROUND 114** with the reason, and a new **section 12** documents the rule, the four constants, the two
  timers, the log and a tuning guide; **Numbers** carries the v15 version line (counts unchanged:
  1,797 / 1,141 / 742 / 689 / 46); **Changelog** has the v15 row. Re-opened from disk and verified.
* `docs/WH3_ability_tracker.md` — the 19 air-drop rows' rule text replaced, plus the round-114 update
  paragraph (backup: `docs/backups/round114/pre114_tracker.md`).

## 9. Retest plan

1. Arm a Sky-junk (or any air-drop carrier) and hover it over a **20-model** enemy block; watch the
   `edge=` number fall to under `0.10m` and the drop leave at that moment.
2. Watch the `fast poll: ON (nearest valid Nm)` / `fast poll: OFF` pair: ON at 30 m, OFF beyond.
3. If it still releases too early: `AIR_DROP_EDGE_M` **0.1 → 0.05**. If a block passes underneath and
   nothing fires: **0.1 → 0.2 → 0.3**. One constant per test.
4. Walk a Lord past: no drop, and no decision line at all (it fails the > 10 test).
5. If the trigger feels late for a fast approach: `AIR_DROP_NEAR_M` 30 → 40 (the fast pass starts
   earlier). `AIR_DROP_FAST_S` 0.2 → 0.1 only if 5 checks/s is still too slow — note the global poll is
   250 ms, so the fast pass is only marginally faster today.
