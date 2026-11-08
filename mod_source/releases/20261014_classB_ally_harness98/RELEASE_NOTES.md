# HARNESS 98 / CLASS B (ally-targeted effects cast on self) — release notes

## What shipped
The audit's **Class B** (`WH3_audit_report.md`, **34 entries**) is implemented on the mod's
**own** ally picker (the `blood_sacrifice` / `eat_da_runts` shape) extended with the
**Class-A round's fresh-handle discipline**.

* **17** entries move to **four new ally families** and now cast **ON THE CHOSEN ALLY**
  (never the owner):
  * `ally_melee_buff` **11** — Da Boss 'as a Plan!, Favour of the Fay, Helping Hand,
    Inspired Assault I/II/III, Inspired Defence I/II/III, Orcs are da Best!, Hellish Vigour
    (the default in-melee/not-routing shape; pick the **closest ally in range**);
  * `ally_heal` **3** — Elvish Healing Herbs, Patch Up, Revivification Crystal
    (the health-only family; pick the **lowest-health ally in range at or below 75%**);
  * `ally_heal_melee` **1** — Captain of the Phoenix Guard (the melee+health gate);
  * `ally_wavering` **2** — Shock Collar, Where You Goin!? (the wavering family; pick the
    **closest wavering ally in range**).
* **1** — **Stay Here, I'll Get Help!** — already had an ally picker (`wavering_ally_range`);
  this round wires its **CAST TARGET** to the picked ally and gives it its **own** 70% bound
  (60 m real → **42 m**, superseding the shared `FOURTH.WAVERING_RANGE_M = 24` for this one
  entry, which was derived from that key's `effect_range`).
* **1** — **Meat Feast** — **SKIPPED: ARMY-BAR ability** (standing rule 10). Evidence: the
  audit's own wording ("An army-keyed single-target recover"), the project's grouped grade
  `army`, and the key's own audio field `wh3_main_army_ability_ogr_butcher`. Its
  pre-existing `ushoran_health` self-cast entry is left **unchanged**.
* **15** — **LEFT AS-IS, NEEDING A USER RULING** (see below).
* **0** — keys that could not be mapped.

## The list (derived programmatically, not hand-typed)
`parse_join_classB.py` parses the `## Class B` section of `WH3_audit_report.md` (34 `#### n.`
blocks), joins each entry to the mod's ABILITIES table and to `unit_spec_abil.tsv`
(`target_intercept_range`), and records the army-bar signals. Counts:

| | count |
|---|---:|
| Class-B entries (report) | **34** |
| skipped as army-bar (Meat Feast) | **1** |
| skipped as already implemented | **0** |
| implemented this round | **18** (17 new families + Stay Here's cast target) |
| needs a ruling | **15** |
| keys that could not be mapped | **0** |

## The per-ability 70% constants
Each implemented entry carries its own REAL `target_intercept_range` (`ally_range_real`) —
none of these single-ally casts has an aura (`effect_range` `0.0000`). At load it maps to ONE
named constant per real range (5 constants, shared where the real range is genuinely shared):
`FOURTH.ALLY_CAST_R<real>` = `floor(real * FOURTH.RANGE_FRACTION)` (70%), floored with the
`+1e-9` epsilon the build asserts.

| real (m, `unit_spec_abil.tsv`) | bound | abilities |
|---:|---:|---:|
| 50 | 35 | 3 (Captain of the Phoenix Guard, Helping Hand, Elvish Healing Herbs) |
| 60 | 42 | 1 (Stay Here, I'll Get Help!) |
| 75 | 52 | 1 (Hellish Vigour) |
| 100 | 70 | 11 (Favour of the Fay, Inspired Assault I/II/III, Inspired Defence I/II/III, Shock Collar, Where You Goin!?, Patch Up, Revivification Crystal) |
| 150 | 105 | 2 (Da Boss 'as a Plan!, Orcs are da Best!) |

## The mechanism
* **Offer test = the per-ability constant ONLY:** `unit:unit_distance(ally) <= bound`
  (`unit_distance` is edge-to-edge, bounding-box aware, `battle_unit.lua:160`). The engine's
  looser `unit_in_range()` is **never** consulted — `grep 'unit_in_range('` is empty.
* **Cast shape:** the established `perform_special_ability(key, target)` call with
  `target = FOURTH.cast_target` (exactly how `blood_sacrifice` / `eat_da_runts` already cast
  on a friendly unit), **plus** the fresh-handle discipline: the CASTER's controller and the
  chosen ALLY are re-enumerated from `get_scriptunits_for_local_players_army()` on the
  **same tick** (`FOURTH.ab_fresh_friend_su`) and the call is issued as
  `caster_su.uc:perform_special_ability(key, ally_su.unit)`. (The existing
  `blood_sacrifice` / `eat_da_runts` code used the poll's same-tick `script_unit.uc` with
  `FOURTH.cast_target`; this round keeps that call shape **and** adds the fresh re-fetch of
  both handles, so a controller held from an earlier poll cannot silently no-op.)
* **Distinct log strings, real distance:** the picker, the pre-cast re-check and the lapse
  line are marker-prefixed and print the REAL computed distance and the entry's own bound,
  e.g. `patch_up ally: 'empire_inf_state_troops' is the chosen ally (heal) distance=30.0m
  bound=70m` and `patch_up pre-cast re-check: the chosen ally is still valid (heal,
  distance=30.0m bound=70m) - firing`.
* **Hold + pre-cast lapse re-check:** an ally that dies or drifts out of the bound (or, for a
  heal, heals above 75%) between the pick and the cast is **SKIPPED** — the cast is not
  spent; the existing per-pair guard + cooldown hold keep it from re-firing every poll.
* **Fail-open on an unreadable read:** unknown distance/health = still valid (the file's
  standing convention).

## Harness 98
* **GREEN: 3186 checks / 0 failures** (live source AND annotated reading copy; up from the
  3075 on disk — +111).
  * New **section 0v** (both files): the 5 constants + values, the `FOURTH.ALLY_CAST` map, the
    18 `ally_range_real` fields, the load-loop wiring, the fresh-friend helper, the shared
    picker, the four family evaluators + map entries, the fresh-handle cast branch, the poll
    slots, the moved trigger counts, and that `unit_in_range(` is still GONE.
  * **32 ally worlds (16 × 2 files):** ally-in-range → cast ON THE ALLY + **self-cast guard**
    + **fresh-handle** proof (AB-U1); no ally → SILENT (AB-U2); ally BEYOND the bound → SILENT
    though the engine helper says in-range (**the regression guard**, AB-U3); the owner not in
    melee → SILENT (AB-U4); the heal fires on the health trigger and picks the **LOWEST-health
    ally of two** (AB-H1/H2), a steady ally is not a heal target (AB-H3), heal beyond the
    bound → SILENT (AB-H4); **two lapse worlds** — drift out of range, and the ally GONE at the
    re-check — both SKIP with the lapse line (AB-L1/L2); the wavering family (AB-W1/W2); the
    melee+health family fires / needs the owner in melee (AB-M1/M2); **Stay Here now casts on
    the picked ally** and its ally beyond its own 42 m bound stays SILENT (AB-S1/S2).
* **RED: 85 designed failures** against the pre-edit snapshot (`pre98_*.lua`, the shipped
  harness-97 build — **no ally triggers at all**). The 0v tokens fail; every FIRE world fails
  (the snapshot's **5 self-casts land on the OWNER**, never on an ally); the SILENT world
  whose snapshot trigger does fire (or whose lapse log is absent) fails too;
  **13/32 world results pass (want 13)**.
* **Re-based pins (documented):** the trigger counts — `melee_unwavering` 383→373 (×7),
  `charge_or_melee` 29→26 (×5), `ushoran_health` 41→38 (×2), `melee_health75` 2→1 — and the
  harness-90 worlds **N8b/N8c** (Stay Here's cast target is now the ally, and its reason reads
  `wavering ally in range, cast on ally`). The h93 tooltip-wording map gains the four new
  triggers.

## Build + install (RPFM WebSocket ws://127.0.0.1:45127, started then stopped)
```
All 5 ship files MATCHES SOURCE: True (per-file sha256 gate)
main mod byte-identical (untouched by the packer): True
built pack   md5 6927e4a6a36885274846616bdb53728e
installed    md5 6927e4a6a36885274846616bdb53728e   IDENTICAL True
```
Independently verified (`verify98.py`): the installed pack's main script is byte-identical to
the source (444560 bytes; sha256 `16919a72504f24f57fcb41d5227ec3007dfe69f1713ee162ea412e702a935697`)
and contains every new token, with `unit_in_range(` absent. Trigger counts inside the installed
pack: `melee_unwavering=373`, `charge_or_melee=26`, `ushoran_health=38`, `melee_health75=1`,
`ally_melee_buff=11`, `ally_heal=3`, `ally_heal_melee=1`, `ally_wavering=2`, `ally_range_real=18`;
`enemy_engaged_or_shot=89`, `enemy_ground_area=9`, `range_real=98` (Class A unchanged);
`{ marker =` = 579.
Annotated copy md5 `641f27c3ed09f2607995a5ac86b05cbb`, 337426 bytes (log-free / find-free).

## Roster
**579 entries / 605 keys — UNCHANGED before and after** (18 entries moved between triggers;
no entry or key added or removed). `melee_unwavering` 383 → 373; `charge_or_melee` 29 → 26;
`ushoran_health` 41 → 38; `melee_health75` 2 → 1; `ally_melee_buff` 0 → 11; `ally_heal` 0 → 3;
`ally_heal_melee` 0 → 1; `ally_wavering` 0 → 2.

## Left out (with reason) — the 15 entries needing a user ruling
Left EXACTLY as they are (still implemented as self-casts), each tagged
`round 98 (Class B): NEEDS A RULING` in the tracker:

| entry | reason |
|---|---|
| 214 Fury of Khaine | **rule 14** — the effect applies **Rampage!**; the note keeps `charge_or_melee`, which is not one of the ally families |
| 495 Verminous Fury | **rule 14** — applies **Rampage!** (it also grants Unbreakable; the Rampage flag wins) |
| 343 Grut's Sickle | **rule 14** — carries a **health cost** (drawback); the note itself says "flag for the user" |
| 305 Daemonic Whispers | the audit note itself says "**flag for the user**" |
| 383 Merciw's Monstrous Regiment | `target_intercept_range = -1.0` — **no real range**, so no defensible 70% bound |
| 239 Overseer of the Unseen | needs a **non-commander / non-large** TARGET-CLASS filter |
| 511 Whiplash! | needs a **non-commander / beast** TARGET-CLASS filter |
| 364 Iron-Handed Captain | needs a "**morale at or below broken**" target gate |
| 361/362/363 Inspired Marksmanship I/II/III | need a **missile-capability** target gate |
| 540 Makaisson's Persuader | needs a **war-machine / artillery** TARGET-CLASS filter |
| 548 Reforge | needs a **Hell-Forged** TARGET-CLASS filter |
| 551 Remouldered | needs a **monster** TARGET-CLASS filter |
| 552 Restore | needs a **construct** TARGET-CLASS filter |

No existing ally family provides those target-class gates, so implementing a plain
closest/lowest-health pick would deliver the effect to a unit the ability's own db gate
excludes — exactly the defect Class B exists to remove. Hence: flagged, not guessed.

## Probe state
* `zz_probe_dist.pack` (the passive observer, 20063 bytes, md5 `d4e67cfb8bc562c7d6f0ff742909c13d`)
  is **LEFT INSTALLED and untouched** — it casts nothing and writes nothing.
* `zz_probe_step.pack` / `zz_probe_enemy_target.pack` are **absent** from `data/`.

## Tracker / annotated
* `WH3_ability_tracker.md`: a round-98 update note at the top; all 18 implemented rows updated
  (status `implemented (ally-targeted: …)`, group `ally_unit`, the proposal naming the new
  trigger, the pick rule and the 70% bound); Meat Feast's row `skipped (army-bar ability)`;
  the 15 ruling rows tagged `NEEDS A RULING`; and a closing addendum with the ally
  range-constant table + the Stay Here supersession note.
* `WH3_auto_ability_annotated.lua`: carries the same change (log-free / find-free).
