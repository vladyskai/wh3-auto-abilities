# Round 101 - boss-only exclusion + Gate of Khorne (2026-10-17)

## Job

Two builds in one round:

**A.** Exclude every ACTIVE ability whose only grant path is a `_boss` unit, mark the reason in the
spreadsheet, and remove from the mod the ones that were implemented.

**B.** Implement **Gate of Khorne** on the user's trigger, verbatim: *"The trigger will place it on the
closest enemy that is in range of the ability and fighting."*

---

## A. Boss-only verification

Grant paths examined for every in-wheel key: `land_abil.tsv` (land_units_to_unit_abilites),
`uset_ability.tsv` (unit_set -> ability), `sag_to_abilities.tsv` + `sag_to_units.tsv`
(special-ability group -> ability -> unit) and `army_ab_faction.tsv`. `ui_coll_junc.tsv` is display-only.
**Skill-tree and rite junctions are NOT in this extraction** - the negative is closed only for the tables
above (same documented limit as `WH3_summon_analysis.md` §5.3).

**15 in-wheel keys qualify** (every grant terminates on a `_boss` unit; no other grant in any table):

| # | Ability | Key | Only granting unit | Was implemented |
|---|---|---|---|---|
| 1 | Greater Faith Bastion | `wh_dlc06_quest_abilities_grand_faiths_bastion` | `wh_dlc06_emp_cha_arch_lector_0_boss` | YES -> removed |
| 2 | Bitter Sting | `wh3_dlc27_qb_unit_abilities_bitter_sting` | `wh3_dlc27_chs_feral_manticore_boss` | YES -> removed |
| 3 | Frenzied Challenge | `wh3_dlc27_qb_unit_abilities_frenzied_challenge` | `wh3_dlc27_bst_mon_ghorgon_boss` | YES -> removed |
| 4 | Visions of Madness | `wh3_dlc27_qb_unit_abilities_visions_of_madness` | `wh3_dlc27_bst_mon_jabberslythe_boss` | YES -> removed |
| 5 | Guttural Roar | `wh3_dlc27_qb_unit_abilities_guttural_roar` | `wh3_dlc27_cth_mon_celestial_lion_boss` | YES -> removed |
| 6 | Breath of the Hydra | `wh2_dlc10_quest_abilities_fiery_head` | `wh2_dlc10_def_mon_war_hydra_boss` | no |
| 7 | Eye of Rejuvenation | `wh2_dlc10_quest_abilities_regenerating_head` | `wh2_dlc10_def_mon_war_hydra_boss` | no |
| 8 | Howling Winter | `wh_dlc08_quest_abilities_howling_winter` | `wh_dlc08_nor_mon_frost_wyrm_boss` | no |
| 9 | Master of Souls | `wh_dlc08_quest_abilities_master_of_souls` | `wh_dlc08_vmp_mon_terrorgheist_boss` | no |
| 10 | Servants of Nagash | `wh_dlc04_quest_abilities_servant_of_nagash` | `wh_dlc04_vmp_cha_strigoi_ghoul_king_0_boss` | no |
| 11 | Dissolving Bone | `wh3_dlc27_qb_unit_abilities_dissolving_bone` | `wh3_dlc27_tmb_mon_carrion_boss` | no |
| 12 | Terrible Malice | `wh3_dlc27_qb_unit_abilities_terrible_malice` | `wh3_dlc27_sla_mon_preyton_boss` | no |
| 13 | Copious Phlegm | `wh3_dlc27_qb_unit_abilities_copious_phlegm` | `wh3_dlc27_nur_mon_toad_dragon_boss` | no |
| 14 | Fiery Convocation | `wh2_dlc10_quest_abilities_magic_fiery_convocation` | `wh2_dlc10_nor_mon_phoenix_flamespyre_boss` | no |
| 15 | Flame Storm | `wh2_dlc10_quest_abilities_flame_storm` | `wh2_dlc10_nor_mon_phoenix_flamespyre_boss` | no |

**Three false positives rejected (they stay implemented):** a naive `_boss` name test also matches
`Empowering Shrooms`, `They Needs Stabbin'` and `Squig Thinkin'`, granted to `wh3_dlc26_grn_cha_night_goblin_big_boss*`
and `wh_main_grn_cha_goblin_big_boss_*`. Those are **ordinary recruitable Big Boss heroes** ("big boss" is the
unit's rank name, not a quest variant): generic on-screen names, `multiplayer_qb_cap = 2` in
`db_main_units.tsv`, recruitment cost > 0, and they reuse an existing warboss attribute group instead of a
bespoke one. All 15 real boss variants carry a bespoke attribute group (12 also `unbreakable`).

## A. Source change

Exactly five entries deleted from `ABILITIES` (same deletion in `docs/WH3_auto_ability_annotated.lua`):

| marker | name | trigger | badge | key |
|---|---|---|---|---|
| `grand_faiths_bastion` | Greater Faith Bastion | `melee_unwavering` | `zz_auto_badge_grand_faiths_bastion` | `wh_dlc06_quest_abilities_grand_faiths_bastion` |
| `bitter_sting` | Bitter Sting | `enemy_engaged_or_shot` | `zz_auto_badge_bitter_sting` | `wh3_dlc27_qb_unit_abilities_bitter_sting` |
| `frenzied_challenge` | Frenzied Challenge | `enemy_engaged_or_shot` | `zz_auto_badge_frenzied_challenge` | `wh3_dlc27_qb_unit_abilities_frenzied_challenge` |
| `visions_of_madness` | Visions of Madness | `enemy_engaged_or_shot` | `zz_auto_badge_visions_of_madness` | `wh3_dlc27_qb_unit_abilities_visions_of_madness` |
| `guttural_roar` | Guttural Roar | `melee_unwavering` | `zz_auto_badge_guttural_roar` | `wh3_dlc27_qb_unit_abilities_guttural_roar` |

No evaluator, trigger, helper, constant or state was removed. `melee_unwavering` keeps every other member;
`enemy_engaged_or_shot` keeps every other member.

---

## B. Gate of Khorne

Key **`wh3_main_character_abilities_gate_of_khorne`** (confirmed against `unit_spec_abil.tsv`: there is no
`dlc26` variant; the three Greater Gate keys are different abilities). Granted by three Cultist of Khorne units.

New trigger `enemy_ground_melee`, implemented as written:

1. enumerate the enemy army; keep enemies alive, validity not false, **FIGHTING (`is_in_melee() == true`)** and
   within the ability's **35 m** bound (`floor(50 * 0.70)`, `FOURTH.ENEMY_CAST_R50`; edge-to-edge
   `unit:unit_distance` ONLY - `unit_in_range` is never called);
2. pick the **CLOSEST** of them;
3. fresh caster controller + fresh enemy the same tick (`FOURTH.eg_fresh_caster_su`), hold via the existing
   per-pair guard, and a pre-cast re-check (alive + still in melee + still within 35 m) that SKIPS and logs
   the real distance;
4. cast `perform_special_ability_ground(key, enemy:position(), 0, 0)` - the **enemy's** position, never the
   caster's;
5. its own reason string: `closest fighting (in-melee) enemy within bound (targeting <type>, distance=<x>m)`.

**"Fighting" is read as in-melee** (the strictest reading of the user's word); the under-missile-fire arm of
the shared enemy picker is deliberately NOT accepted for this trigger (`FOURTH.eg_melee_only`).

Log lines (live build):
- `  gate_of_khorne target: 'orc_boyz' is the chosen enemy (melee) distance=30.0m bound=35m`
- `ATTEMPT gate_of_khorne 'wh3_main_character_abilities_gate_of_khorne' on '<caster type>' ui id <id> | reason: closest fighting (in-melee) enemy within bound (targeting orc_boyz, distance=30.0m) | armed=ON`
- `  gate_of_khorne pre-cast re-check: target still engaged (melee, melee=true shot=false melee_only=true, distance=30.0m bound=35m) - firing`
- `  gate_of_khorne SKIPPED: the chosen enemy lapsed before the cast (alive=true melee=false shot=false melee_only=true distance=30.0m bound=35m) - cast not spent`
- `  enemy-ground cast      : perform_special_ability_ground('wh3_main_character_abilities_gate_of_khorne', <the chosen ENEMY's position vector>) - the enemy-ground form`

---

## Counts

| | before | after | arithmetic |
|---|---:|---:|---|
| entries | 577 | **573** | -5 + 1 |
| keys | 603 | **599** | -5 + 1 |
| `melee_unwavering` | 362 | **360** | -2 |
| `enemy_engaged_or_shot` | 89 | **86** | -3 |
| `enemy_ground_melee` | 0 | **1** | new |
| `range_real` fields | 98 | **96** | -3 + 1 |
| `enemy_ground_area` | 9 | 9 | unchanged |
| `ushoran_health` | 33 | 33 | unchanged |

Live script: 548,092 bytes, sha256 `6ef0e28841b7ac9883dbba257665f0068febf4ba83bfa67316da5e80b0e3b0d7`.
Annotated: 439,461 bytes, sha256 `02a39b769f25c65b4cc2738850a010f12e8d32c841873594d069007370691e03`.

## Harness 101

`harness101.lua` = `harness100.lua` + re-based count pins + section 0aa and seven worlds.

- GREEN: **3442 checks / 0 failures** - `h101_green.txt` (`HARNESS OK - all checks passed`)
- RED (pre101 snapshot): **3396 checks / 78 designed failures** - `h101_red.txt`
  - 65 re-based count pins (573/599, 360, 86, 96, 1146, wording 573, `range_real` 96)
  - 3 tooltip-coverage pins (D1a/D1b/D2: snapshot 577 vs 573)
  - 8 inherited red-control branches from earlier rounds (82/88/89/90/93/96/97/98) whose snapshots are
    newer than this round's pre-edit snapshot
  - 2 aggregate world tallies that count the failed pins above
  - harness 101's own red branch and all seven Gate worlds pass on both sides by design (the snapshot has
    no Gate of Khorne, so every gate world fires nothing)

Worlds (live source): W1 a fighting enemy inside the bound -> fires at **that enemy's position**
(`pos:<enemy uid>`, orientation/width 0); W2 closest of three qualifying -> the 20 m one; W3 fighting but
60 m away with the engine helper set in-range -> SILENT, helper never consulted; W4 in range but only under
missile fire -> SILENT, no missile read taken; W5 the chosen enemy stops fighting between pick and cast ->
SKIPPED with the real distance logged; W6 no enemies -> SILENT; W7 self-cast guard (caster itself in melee)
-> the position is the enemy's, never the caster's.

## Build / install

- 5 ship files: all `MATCHES SOURCE: True` (script 548,092; tooltip 331,235; badge template 2,864; blank.png 69; auto_badge.png 252)
- `main mod untouched (byte-identical): True`
- installed pack md5 **`deaf707dcda5087d689116860f7b0f27`**, dist == installed
- `zz_probe_dist.pack` left installed and untouched (md5 `d4e67cfb8bc562c7d6f0ff742909c13d`)
- `tools/build_and_install.py` not touched; this round's builder is `build_and_install101.py`

## Docs

- tracker: legend gains `excluded (not in wheel: boss-only unit)`; header update paragraph; the five §2 blocks
  carry a Removed line; all **15** §3a rows carry the new status and the per-ability grant evidence; Gate of
  Khorne's §2 decision and §3a row rewritten to implemented; new **§10.3** records the verification, the
  removal, the trigger and the counts.
- spreadsheet: `docs/WH3_abilities_master_v3_2026-10-17.xlsx` (+ `.ods`) - **v3 supersedes v2; v1 and v2 are
  byte-unchanged**. 15 rows `EXCLUDED` / reason `boss-only unit (granted only to _boss units)`; the five
  removed implementations read `REMOVED (boss-only)`; Gate of Khorne `IMPLEMENTED` on `enemy_ground_melee`;
  Definitions gains two vocabulary rows, the 36th glossary row and the new totals; Numbers re-counted
  (1143 / 654 / 599 / 544); Changelog gains a v3 row.
