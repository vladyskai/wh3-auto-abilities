# HARNESS 97 / THE REST OF CLASS A (enemy-targeted abilities) — release notes

## What shipped
The PROVEN Accusation enemy-targeting mechanism is applied to the other **97** Class-A
entries from `WH3_audit_report.md` (Class A holds 98; **Accusation 263** was already done
and is the template).

* **88** ride the **existing** `enemy_engaged_or_shot` trigger — enemy-**UNIT** hexes
  (debuffs, chains, direct damage…). The cast target is the enemy unit.
* **9** ride a **new** `enemy_ground_area` trigger — enemy-**GROUND** area hexes. The
  cast goes through `perform_special_ability_ground(key, ENEMY_POSITION, 0, 0)` on the
  **chosen enemy's own ground** (not the caster's), with the same fresh-handle discipline
  and the same bound test.

Enemy-ground keys (9): `wh2_dlc09_item_abilities_amulet_of_phastah`,
`wh_dlc03_item_abilities_chalice_of_dark_rain`, `wh2_dlc09_character_abilities_curse_of_khsar`,
`wh2_dlc10_character_abilities_entangle`, `wh3_dlc25_character_abilities_get_em`,
`wh2_dlc13_lord_abilities_hunters_snare`, `wh2_dlc13_lord_abilities_hunters_trap`,
`wh2_main_item_abilities_the_tricksters_pendant`, `wh_main_item_abilities_tricksters_shard`.

## The list (derived programmatically, not hand-typed)
Parsed from the `## Class A` section of `WH3_audit_report.md` (98 `#### n.` blocks), joined
to the mod's ABILITIES table and to `unit_spec_abil.tsv`.

| | count |
|---|---:|
| Class-A entries (report) | **98** |
| already implemented (Accusation 263) | **1** |
| **new this round** | **97** (88 unit + 9 ground) |
| entries whose key could not be mapped | **0** |

## The per-ability 70% constants
Each entry carries its own REAL `target_intercept_range` (`range_real`) — the cast range per
this project's research (`effect_range` is the effect's area radius, 0 for single-unit casts).
At load it maps to ONE named constant per real range (12 constants, shared where the real
range is shared): `FOURTH.ENEMY_CAST_R<real>` = `floor(real * FOURTH.RANGE_FRACTION)` (70%),
floored with the `+1e-9` epsilon the build asserts.

| real (m, unit_spec_abil.tsv) | bound | abilities |
|---:|---:|---:|
| 15 | 10 | 1 |
| 20 | 14 | 1 |
| 30 | 21 | 4 |
| 35 | 24 | 5 |
| 50 | 35 | 6 |
| 70 | 49 | 1 |
| 75 | 52 | 15 (+Accusation = `FOURTH.ACCUSATION_RANGE_M`) |
| 100 | 70 | 33 |
| 150 | 105 | 7 |
| 180 | 126 | 1 |
| 200 | 140 | 22 |
| 500 | 350 | 1 |

## The mechanism (unchanged from Accusation, extended)
* **Offer test = the per-ability constant ONLY:** `unit:unit_distance(enemy) <= bound`
  (`unit_distance` is edge-to-edge, bounding-box aware, `battle_unit.lua:160`). The engine's
  looser `unit_in_range()` is **never** consulted — `grep 'unit_in_range('` is empty.
* **Fresh handles:** the caster controller is re-fetched the same tick
  (`FOURTH.eg_fresh_caster_su` → `uc = FOURTH.eg_caster_su.uc`); the enemy is re-enumerated
  the same tick.
* **Trigger shape:** an enemy within the bound that is `is_in_melee()` OR
  `is_under_missile_attack()`; in-melee preferred, closest among equals; pre-cast re-check
  (alive + still engaged + still in bound) with SKIP on lapse; the existing hold; the cast
  target is ALWAYS the enemy, never the owner.
* **Distinct log strings, real distance:** the target-choice, pre-cast re-check and lapse
  lines are marker-prefixed and print the REAL computed distance, e.g.
  `acquiescence target: 'orc_boyz' is the chosen enemy (melee) distance=131.0m bound=140m`.
  Enemy-ground casts log the enemy-ground form.
* One shared picker `FOURTH.eg_pick_enemy(unit, routing, ground)` backs both triggers; the
  enemy-ground cast branch fails **closed** if no enemy was chosen.

## Harness 97
* **GREEN: 3075 checks / 0 failures** (live source AND annotated reading copy).
  * New **section 0u** (both files): the 12 constants + values, the `FOURTH.ENEMY_CAST` map,
    the 98 `range_real` fields, the load-loop wiring, the shared picker + fresh-caster route,
    the enemy-ground evaluator/helper/key-set, the moved trigger counts, the poll slots, and
    that `unit_in_range(` is still GONE.
  * **54 worlds (27 × 2 files):** per real-range family (12) INSIDE → fires AT THE ENEMY
    (unit form) or casts on the ENEMY's GROUND (ground form) + self-cast guard; BEYOND →
    SILENT even though the engine's own helper says in-range (**THE REGRESSION GUARD**);
    plus MISSILE (under-fire fires), LAPSE (pick→cast lapse SKIPS), and FRESH (caster
    re-fetched the same tick — the stale-handle guard).
* **RED: 77 designed failures** against the pre-edit snapshot (`pre97_*.lua`, the shipped
  harness-96 build). The 0u tokens fail; every non-accusation INSIDE/missile/ground world
  fires nothing; the 24 BEYOND worlds pass by design; the ACCUSATION family passes (it is
  already enemy-targeted on the snapshot): **27/54 world results pass (want 27)**.
* **Re-based pins (documented):** the earlier rounds' `melee_unwavering == 480` pins → 383
  (7 sites), the h94/enemy-count pin → 89 (+ enemy_ground_area 9), the h94 live source-token
  pins (the log is now marker-prefixed), the two h96 0t log-token pins (the bound is now the
  per-ability local), the h93 tooltip wording map (gains `enemy_ground_area`). One harness-91
  world used a Class-A key (Whip of Agony) as its melee_unwavering representative and was
  re-pointed at **Black Periapt** (still melee_unwavering).

## Build + install (RPFM WebSocket ws://127.0.0.1:45127, started then stopped)
```
All 5 ship files MATCHES SOURCE: True (per-file sha256 gate)
main mod byte-identical (untouched by the packer): True
built pack   md5 f42ed662ce42fee8a570593346cca4e6
installed    md5 f42ed662ce42fee8a570593346cca4e6   IDENTICAL True
```
Independently verified: the installed pack's main script is byte-identical to the source and
contains every new token (`FOURTH.ENEMY_CAST_R100 = 70`, `enemy_ground_area = …`,
`function FOURTH.enemy_ground_cast`, `function FOURTH.eg_pick_enemy`, the load-loop map) and
contains **neither** `unit_in_range(`. Trigger counts inside the installed pack:
`melee_unwavering=383`, `enemy_engaged_or_shot=89`, `enemy_ground_area=9`, `range_real=98`,
`{ marker =` = 579.
Live source sha256 `bb26e915527f3b4faf4e5e8a1afa1b1d8ae0013f7052511efcd1eaf2089d0a0f`, 428103 bytes.
Annotated copy md5 `4028067c0b88f9b3c9334ca680629173`, 323449 bytes.

## Roster
**579 entries / 605 keys — UNCHANGED before and after** (97 entries moved between triggers; no
entry or key added or removed). `melee_unwavering` 480 → 383; `enemy_engaged_or_shot` 1 → 89;
`enemy_ground_area` 0 → 9.

## Tracker / annotated
* `WH3_ability_tracker.md`: all 105 Class-A rows (one per key) updated — status
  `implemented (enemy-targeted: …)`, group `enemy_unit`/`enemy_ground`, the proposal names the
  trigger + the 70% bound, and each note gains the enemy-targeting-mechanism tag; a round-97
  update note sits at the top.
* `WH3_auto_ability_annotated.lua`: carries the same change (log-free / find-free).

## Probe state
* `zz_probe_dist.pack` (the passive observer, 20063 bytes, md5 `d4e67cfb8bc562c7d6f0ff742909c13d`)
  is **LEFT INSTALLED** and untouched — it casts nothing and writes nothing.
* `zz_probe_step.pack` / `zz_probe_enemy_target.pack` are **absent** from `data/`.

## Left out (with reason)
* **Accusation (263)** — already implemented and field-verified; it is the template (only its
  entry gained the `range_real = 75` field).
* **`doom_and_darkness_gunnery_school` key case:** its first key
  `wh3_dlc25_spell_Bound_doom_and_darkness_gunnery_school` carries a capital `B`, which defeats
  the mod's dial-claim gate (`string.lower(read_key) == listed_key`, "they are lowercase
  already"). This is **PRE-EXISTING** and orthogonal to the enemy-targeting mechanism (the
  other two keys of the same entry are lowercase and claim normally); it is NOT fixed here
  because that would touch the shared key matcher used by all 605 keys. Flagged for a
  follow-up. (The harness's r200 family uses `acquiescence` — a clean lowercase key — for this
  reason.)
