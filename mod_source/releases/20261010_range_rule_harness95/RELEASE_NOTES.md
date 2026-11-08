# HARNESS 95 / THE STANDING 70% RANGE RULE — release notes

## What shipped
The user's new **STANDING RULE**: **every trigger range = AT MOST 70% of the ability's REAL game-data
range, rounded DOWN to a whole metre** — ruled **ABSOLUTE, no exceptions**. The rule ships in code as
the named constant **`FOURTH.RANGE_FRACTION = 0.70`**; **every** range-bearing constant in the mod was
re-derived as `floor(real × 0.70)`, with the real value + its source in the comment beside it.

The symptom the rule removes (user-reported): after the Accusation field test the **Witch Hunter
WALKED** toward the target — a cast was offered at an enemy inside the ability's game-data *intercept*
reach but outside a comfortable *casting* range, so the engine walked the caster. User (verbatim):
**"for abilities that include a range, we should always specify 70% of the actual range to avoid such
things"**, later ruled absolute: **"...No exceptions."**

## The audit — every range constant (old → real → new)
| Constant | Old | Real range (source) | 70% target | **New** |
|---|---:|---|---:|---:|
| `GLORIOUS_DEATH_RANGE_M` (chunk local) | 25 | **55.0000** — `effect_range`, `wh3_dlc25_lord_abilities_glorious_death` | 38.5→**38** | **38** |
| `FOURTH.VERMINKING_RANGE_M` | 25 | **35.0000** — `effect_range`, `wh3_dlc29_lord_abilities_will_of_the_verminking` | 24.5→**24** | **24** |
| `FOURTH.METALLURGY_RANGE_M` | 25 | **35.0000** — `effect_range`, `wh3_main_character_abilities_enchanted_metallurgy`(+`_flaming`/`_piercing`/`_poison`) | 24.5→**24** | **24** |
| `FOURTH.WAVERING_RANGE_M` | 25 | **35.0000** — `effect_range`, `wh3_dlc29_lord_active_commanding_presence` / `wh3_dlc29_spell_bound_prayer_fury_of_ulric` / `wh2_dlc09_character_abilities_stay_here_ill_get_help` | 24.5→**24** | **24** |
| `FOURTH.BLOOD_SACRIFICE_RANGE_M` | 25 | **100.0000** — `target_intercept_range` (**no aura**: `effect_range` = 0.0000), `wh3_dlc26_lord_abilities_blood_sacrifice` | 70.0→**70** | **70** |
| `FOURTH.EAT_DA_RUNTS_RANGE_M` | 25 | **100.0000** — `target_intercept_range` (**no aura**: `effect_range` = 0.0000), `wh3_dlc26_unit_abilities_eat_da_runts` | 70.0→**70** | **70** |
| `FOURTH.ACCUSATION_RANGE_M` | 75 | **75.0000** — `target_intercept_range` (**no aura**: `effect_range` = 0.0000), `wh_main_hero_abilities_accusation` | 52.5→**52** | **52** |
| `CHARGE_MIN_DISTANCE_M` | 12 | **not an ability range** (charge-order run-up gate) | — | **12** (unchanged) |
| `CHARGE_MAX_DISTANCE_M` | 60 | **not an ability range** (charge-order run-up gate) | — | **60** (unchanged) |

**No inline numeric distance comparison** exists anywhere in the mod — every gate reads a named
constant. **The appended tooltip lines name no distance**, so no tooltip wording changed.

## The Glorious Death decision (the exception was VOIDED by the user)
The task's **first** draft said to keep Glorious Death at the field-tuned **25 m** as a deliberate
"never loosen a field-tested value" exception (70% of its 55 m aura is **38 m**, which would loosen it).
**The user overruled this mid-round: the rule is absolute — no exceptions.** So Glorious Death was set
to **38 m** at his direction and the "field-tested carve-out" was **removed from the rule**. The old
25 m value is recorded as history only. There is therefore **no surviving exception** in the code.

## Range basis
* **Aura abilities** (`effect_range` > 0): real range = `effect_range` — Glorious Death 55, Verminking
  35, Metallurgy 35, Wavering 35.
* **No-aura targeted abilities** (`effect_range` = 0): real range = `target_intercept_range` (the reach
  the engine uses to walk the caster) — Blood Sacrifice 100, Eat da Runts 100, Accusation 75. These are
  the two values the tracker's earlier rounds already treated as those heals' real reference.

## Files
    script/battle/mod/zz_test_deadly_onslaught.lua   (live)        sha256 ea48ca6dc6bf8e3657a179dfd869e7c876b4d2cf3dfb096f1821d957ba09b704
    WH3_auto_ability_annotated.lua                   (reading copy)
    WH3_ability_tracker.md                           (legend rule 15 + section-10 update)

## Harness 95
* **GREEN: 2856 checks / 0 failures** (both the live source AND the annotated reading copy).
  New **section 0s** asserts the rule constant + every derived value + the derivation comments + the
  unchanged charge-window pair + the unchanged 579-entry table.
* **BOUNDARY WORLDS: 28 world results (14 per file), 28/28 green, 7 fires.** For EVERY changed
  constant: a candidate **just inside the new bound FIRES**, and one **between 70% and 100% of the real
  range (the movement-prone zone) stays SILENT**:
  GD 38↔45 · VM 24↔25 · MT 24↔25 · WV 24↔25 · BS 70↔71 · EDR 70↔71 · ACC 52↔70.
* **RED: 2823 checks / 56 designed failures** against the pre95 snapshot (= the shipped harness-94
  build). The failures are: the **7 moved pins** (GD 25→38, VM/MT/WV 25→24, BS/EDR 25→70, ACC 75→52)
  plus the changed comment tokens — **20 checks**; the **section-0s tokens** — **22**; and the **14
  boundary-world legs** that sit INSIDE the new bound (G1/V2/M2/W2/B1/E1/A2 × 2 files). The re-based
  earlier worlds (GD R7 26→39 m, BS P4 26→71 m, BS/EDR drift 60→80 m) pass on BOTH builds by design;
  the h94 section's red branch was re-based to the N/A form (its old snapshot is now the h94 build).

## Build + install (RPFM WebSocket ws://127.0.0.1:45127, server reused then stopped)
    All 5 ship files MATCHES SOURCE: True (per-file sha256 gate).
    Main mod byte-identical (untouched by the packer): True.
    installed md5 f1b7363e411bfc340423d4ecdc1ea91c   (dist == installed, IDENTICAL True)

## Ranges that could not be derived
* **None could not be derived.** The two single-target heals (Blood Sacrifice, Eat da Runts) have **no
  aura** (`effect_range` = 0.0000), so their "real range" is the `target_intercept_range` = 100.0000 m
  — the same basis the tracker already recorded for them; their 70% value is therefore **70 m**.
