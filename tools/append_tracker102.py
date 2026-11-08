"""Append §10.4 (the summon round record) to the tracker."""
import os, json

ROOT = r"C:\Users\vlady\Desktop\WH3_mod"
GEN = os.path.join(os.path.expandvars(r"%LOCALAPPDATA%\Temp"), "gen")
TRK = os.path.join(ROOT, "docs", "WH3_ability_tracker.md")
plan = json.load(open(os.path.join(GEN, "plan.json"), encoding="utf-8"))

A_ENTRIES = len(plan["A_entries"])
A_KEYS = len(plan["A_keys"])

SEC = f"""
### 10.4 The summon round - the ground-castable summons, the four new summon triggers, the illusions excluded (2026-10-17)

**A. THE REST OF THE SUMMON CLASS (derived, not hand-listed).** The list was derived programmatically from the
game's own tables (`unit_spec_abil.tsv` + `unit_abilities.tsv` in `%LOCALAPPDATA%\\Temp\\wh3\\`, script
`tools/derive_summon_plan.py`): `spawned_unit` set AND `type = wh_type_summon_unit` AND `spawn_is_decoy` false/absent
AND `target_ground = true` AND in-wheel (`source_type` unit-side, `icon_name` set, `is_hidden_in_ui = false`, not the
army/quest family) AND not boss-only AND not already implemented. Result: **{A_ENTRIES} entries / {A_KEYS} keys** (the two
cataclysm/character twins and the six Lord-of-Undeath ranks collapse into ONE entry each; one broken `<loc>` name merged
into its base).

**The ONE row of that label set that cannot take a ground point:** **Nurgling Tide**
(`wh3_main_lord_abilities_nurgling_tide`) - `target_ground = false`, no target flag at all, `affect_self = true`,
`target_intercept_range` = 0, `effect_range` = 0: a self-centred spawn. It is implemented in (B) on a self trigger, so
nothing from the label set is left unimplemented.

**One entry has no real range:** **The Tallyman's Blades Upgraded** (`wh3_dlc25_character_abilities_tallymans_blades_2`)
declares `target_intercept_range` = -1.0. There is no 70% of a negative range, so the entry carries `unbounded = true`
and the picker skips the distance test (the closest in-melee enemy anywhere is offered), exactly as the Class-B
infinite-range entry does.

**B. NURGLING TIDE - self-target only.** The user's rule, verbatim: *"that one should only trigger when the caster
himself is in melee."* New trigger **`self_summon_melee`**: owner alive (the poll's own alive gate), NOT routing,
`is_in_melee()` true; then the cast goes on the OWNER through the unit form (`perform_special_ability(key, self)`) with
the caster's controller re-fetched FRESH the same tick, the ordinary hold and a pre-cast re-check of the same state
(alive + still in melee, logged). **No range bound** - stated in the code comment: a self cast has no distance to
measure (the row carries `target_intercept_range` = 0 and no target flags).

**C. THE FOUR ILLUSIONS - EXCLUDED.** They are the only four rows in the game with `spawn_is_decoy = true`, and the
engine REFUSES an illusion while its caster is engaged in melee, so no melee trigger can ever fire them. Tracker status
`excluded (not in wheel: illusion summon)`, reason *illusion (spawn_is_decoy; refused when engaged in melee)*:

| Ability | key | status |
|---|---|---|
| Call of the Shadow Dancer | `wh2_dlc10_lord_abilities_deadly_mislead` | `excluded (not in wheel: illusion summon)` |
| Deceiving Shadows | `wh3_dlc24_lord_item_deceiving_shadows` | `excluded (not in wheel: illusion summon)` |
| Doppelgang | `wh2_dlc14_unit_abilities_doppelgang` | `excluded (not in wheel: illusion summon)` |
| Mislead | `wh2_dlc10_lord_abilities_mislead` | `excluded (not in wheel: illusion summon)` |

**None of the four was ever implemented** (checked in both the live script and the annotated copy), so this round
removed nothing - unlike the boss-only round. The harness proves all four keys stay absent from both files.

**D. THE NINE UNLABELLED REAL SPAWNERS** - `wh_type_*` labels other than `wh_type_summon_unit`, all `spawned_unit` +
`target_ground` true. Implemented on **`enemy_ground_melee`** (the Gate of Khorne trigger), 9 entries / 9 keys:
Beast Pack `wh2_dlc16_lord_abilities_beast_pack`, Blacktoof's Conjuration
`wh2_dlc15_item_abilities_blacktoofs_conjuration`, Call to Gwindalor `wh2_dlc16_lord_abilities_call_to_gwindalor`,
Lesser Raise Dead `wh2_dlc16_spell_bound_vampires_lesser_raise_dead`, Savage Dominion
`wh2_dlc17_spell_bound_savage_dominion`, Savage Predators `wh3_dlc26_hero_abilities_savage_predators`, Tide of Death
`wh2_dlc16_hero_abilities_tide_of_death`, Tide of Pox `wh2_dlc16_hero_abilities_tide_of_pox`, Wake Da Idol
`wh3_main_item_abilities_zak_aloooog`. (Savage Predators is the one 45 m row -> **31 m** bound; the rest are 50 m ->
35 m.)

**E. EYE OF KHORNE - a FINISHER.** Key `wh3_dlc26_lord_abilities_eye_of_khorne`; its row is `target_enemies = true`,
`target_ground = false`, `spawn_type = unit_position`, 50 m -> **35 m** bound, so the cast is the UNIT form
(`perform_special_ability(key, enemy)`), NOT a ground cast. New trigger **`enemy_low_health_noncommander`**: any enemy
inside the bound BELOW 20% health (`HealthPercent`, number or numeric string) that is NOT a Lord or Hero; the
LOWEST-health one wins, closest as the tiebreak; own reason string; pre-cast re-check of alive + health + commander +
distance.

**The Lord/Hero predicate is a REAL READ.** `FOURTH.commander_keys` is DERIVED from the game's own class/caste
columns: every `land_units` key whose `class` = **"com"** - the engine's commander class, the same class its own
invalid-target flags `unit_is_commander_class` / `unit_is_not_commander_class` name - UNION every `land_units` key
reached from a `main_units` row whose `caste` is **"lord"** or **"hero"** (that second arm catches the six Krell
variants whose `land_units` row still says `inf_mel`). **1,409 keys**, matched by EXACT WHOLE-KEY equality against
`battle_unit:type()` (the proven `land_units` key read - the Slayer-list shape). `battle_unit:unit_class()` == "com"
is the FALLBACK read when `type()` cannot be taken; if neither answers, the unit is treated as a COMMANDER and the
finisher never fires at it (**FAIL CLOSED**, one log line for the whole battle).

**F. THE DREADED THIRTEENTH - four keys, one entry.** `wh3_dlc29_spell_bound_the_dreaded_thirteenth`, `_1`,
`_thanquol`, `_thanquol_1`: `target_ground` + `target_enemies`, `spawn_type = unit_position_offset`, 100 m -> **70 m**
bound, an explosion plus a summon. New trigger **`enemy_melee_noncommander`**: any enemy inside the bound IN MELEE that
is NOT a Lord or Hero (same predicate as E); closest wins; placed on that enemy's ground
(`perform_special_ability_ground(key, enemy:position(), 0, 0)`).

**THE FOUR TRIGGER NAMES (added to the glossary):**

| trigger | fires when | cast form |
|---|---|---|
| `enemy_ground_melee` | the closest enemy inside the ability's 70% bound that is FIGHTING (in melee) | ground form on THAT ENEMY's position |
| `self_summon_melee` | the OWNER itself is in melee (alive, not routing, `is_in_melee()`) | unit form on the OWNER - no range bound |
| `enemy_low_health_noncommander` | the lowest-health enemy inside the 70% bound below 20% health that is NOT a Lord or Hero (closest tiebreak) | unit form on that enemy |
| `enemy_melee_noncommander` | the closest enemy inside the 70% bound in melee that is NOT a Lord or Hero | ground form on that enemy's position |

**Counts (exact, before -> after).** ABILITIES **573 -> 642 entries** (573 + 69 = 57 A + 9 D + 1 E + 1 F + 1 B);
**599 -> 682 keys** (599 + 83 = 68 A + 9 D + 1 E + 4 F + 1 B). `melee_unwavering` stays **360** and
`enemy_engaged_or_shot` stays **86** (no entry changed trigger); `enemy_ground_area` stays **9**; `enemy_ground_melee`
**1 -> 67**; `self_summon_melee` **1**; `enemy_low_health_noncommander` **1**; `enemy_melee_noncommander` **1**;
`range_real` fields **96 -> 163** (+67: every new bounded entry); `enemy_ground_keys` **10 -> 91** (+81).

**Harness 102:** GREEN **3525 checks / 0 failures** (live + annotated). RED (the pre-102 snapshot, i.e. the shipped
harness-101 build) **3458 checks / 70 designed failures** - every summon world fires NOTHING (unit 0, ground 0) and
the failures are exactly the table-size / range_real / trigger-count pins (573/599/96/1 vs 642/682/163/67), the three
new tooltip wordings, the 0z static gates for code the snapshot does not carry, and the inherited red-control branches
of earlier rounds. The harness-101 suite itself still passes both sides (its own previous-round red aggregate is
re-based to the N/A form).

**Build/install:** all **5 ship files byte-identical** to source (script 661,255 bytes); installed pack md5
**`a49471940389cf429d5b21aaeac84959`**, dist == installed (independently re-opened and byte-compared).
`zz_probe_dist.pack` left installed and untouched (md5 `d4e67cfb8bc562c7d6f0ff742909c13d`).

**Spreadsheet:** `docs/WH3_abilities_master_v4_2026-10-17.xlsx` (+ `.ods`) - **v4 supersedes v3; v1, v2 and v3 are
unchanged**. Every touched row carries its new status; the four illusions read `EXCLUDED` with reason
*illusion (spawn_is_decoy; refused when engaged in melee)*; the Definitions sheet carries the three new trigger names;
the Changelog has a v4 row.
"""

s = open(TRK, "rb").read().decode("utf-8")
assert s.count("### 10.4") == 0
s = s.rstrip("\n") + "\n" + SEC
open(TRK, "wb").write(s.encode("utf-8"))
print("appended §10.4; bytes", os.path.getsize(TRK))
