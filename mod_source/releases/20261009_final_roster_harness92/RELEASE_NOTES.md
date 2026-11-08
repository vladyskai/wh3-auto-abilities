# HARNESS 92 / the FINAL ROSTER BUILD - release notes

## What shipped
THE FINAL ROSTER BUILD. The 12 INDIVIDUAL abilities from
`WH3_remaining_triage.md` (section 3) are all resolved; **no row anywhere in the
tracker reads `proposed` / `proposed (FF)`**.

**6 BUILT** (the two new triggers + four in-melee-self entries):

| Ability | Key | Trigger as built |
|---|---|---|
| Blood Sacrifice | `wh3_dlc26_lord_abilities_blood_sacrifice` | `blood_sacrifice` (NEW) - cast on the lowest-health ally in range at or below 75% |
| Eat da Runts! | `wh3_dlc26_unit_abilities_eat_da_runts` | `eat_da_runts` (NEW) - cast on self at or below 75%, else the lowest-health ally in range |
| Locus of Virulence | `wh3_main_character_abilities_locus_of_virulence` | `melee_unwavering` (in-melee self) |
| The Dance of Dreaming | `wh3_dlc27_lord_abilities_the_dance_of_dreaming` | `melee_unwavering` (in-melee self) |
| The Waltz of Lethargy | `wh3_dlc27_lord_abilities_the_waltz_of_lethargy` | `melee_unwavering` (in-melee self) |
| Ultimate Verdict | `wh3_cp1_character_abilities_terrifying_presence` | `melee_unwavering` (in-melee self) |

**6 EXCLUDED** (with reasons):

| Ability | Key | Reason |
|---|---|---|
| More Powder! | `wh2_dlc11_hero_abilities_more_powder` | no ammo-low read (ammo replenish) |
| Restock! | `wh2_dlc17_hero_abilities_more_powder_generic` | no ammo-low read (ammo replenish) |
| Restock! | `wh3_dlc25_abilities_restock_gunnery_school` | no ammo-low read (ammo replenish) |
| Ominous Powder | `wh3_dlc25_item_abilities_ominous_powder` | no effect text available (unsourceable) |
| The Soulstealer | `wh3_dlc29_spell_bound_undeath_khizaar_the_soulstealer` | enemy-ground placement (no placement path) |
| Touched by the Moon | `wh2_dlc17_army_abilities_touched_by_the_moon` | army-bar ability (standing rule 10) |

NOTE on **Touched by the Moon**: the triage's draft proposal was a real
activation ("cast on self / nearest ally while in melee"), but its game key
carries `army_abilities`, which the repo's STANDING RULE 10 ("Skip all army bar
abilities") and its FOUR hard army-bar checks (harness 0m/0n/0o) plus the build
script's own `assert "army_abilities" not in script_txt` forbid shipping. It is
therefore resolved with the SAME settled status the other 98 army-bar rows
carry: `excluded (auto: army-bar ability (standing rule 10))`.

## The two NEW ally-heal triggers
Both are ally-targeting heals that CAST ON THE CHOSEN ALLY (not self):
* a **conservative named 25 m range constant** (`FOURTH.BLOOD_SACRIFICE_RANGE_M`,
  `FOURTH.EAT_DA_RUNTS_RANGE_M`); the game data (`unit_spec_abil.tsv`) gives
  these single-ally heals NO aura radius (effect_range 0.0000,
  num_effected_friendly_units 1) with a target_intercept_range of 100.0000 m;
* the **pre-cast re-check / drift skip** (the Glorious-Death / Verminking safety
  pattern): the chosen ally's gap AND health are re-read immediately before the
  cast and the cast is SKIPPED on drift or when the ally healed above the line;
* each carries its OWN distinct reason string; all helpers/state ride the
  existing `FOURTH` bag (NO new chunk-level locals - the chunk sits at Lua's
  200-local ceiling); no `string.find`.

## Counts
* abilities table: **573 -> 579 entries** (**599 -> 605 keys**)
* melee_unwavering 477 -> 481; two new triggers (blood_sacrifice 1, eat_da_runts 1)
* NO army_abilities key shipped.

## Files
    script/battle/mod/zz_test_deadly_onslaught.lua   (live)  sha256 cdba77592993fc92aa3f588928a719fdb54e5efe0e7366758f99bb75ec979de6
    WH3_auto_ability_annotated.lua                   (reading copy, log-free) sha256 4badf14a4ca59b9bd7549ecc0427ee2c0e933bd3ee0b9fd8281d60fafc6695fc

## Build + install (RPFM WebSocket ws://127.0.0.1:45127, server started then stopped)
    All 5 ship files MATCHES SOURCE: True (per-file sha256 gate).
    Main mod byte-identical (untouched by the packer): True.
    installed md5 74c42447d9cbdd5ee7145849e57e74d6   (dist == installed, IDENTICAL True)

## Harness 92
    GREEN : 2662 checks, 0 failures
    RED   : 2629 checks, 84 failures  (baseline snapshot = pre-edit live+ann:
                                        pre92_live.lua / pre92_ann.lua = 573 entries / 599 keys)
    Every red failure is a DESIGNED grown-table pin (A4 579, B4 579, H68 579/605,
    C6c 579, M6 579/605, N13 579/605, S1 579/605, 0h/0m/0n 481, 0o 579/481), an
    aggregate that tallies a pin-dependent world result (A1-A4 6/8, B1-B6 10/12 -
    also failed in the harness-90/91 red runs), or the new HARNESS-92 section
    (0p tokens + the P worlds absent on the snapshot). The harness-91 red-branch
    aggregate was re-based to the N/A form (the harness-92 snapshot already
    carries the auto-327 sweep). No unexpected red-branch self-failures.

## Closing roster tally (in the tracker, section-10 closing note)
    total inventory rows            1797
    implemented                      605
    approved                           0
    excluded (impossible)             97
    excluded (by reason family)     1004
    skipped                           72
    rejected                          19
    reconcile 605 + 0 + (1004+97) + 72 + 19 = 1797
