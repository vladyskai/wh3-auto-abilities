# Summon abilities - data model, counts and the trigger design

## How to identify a summon
- `unit_special_abilities.spawned_unit` is the only reliable spawn signal. `phases`/`phase_junc` carry
  NO spawn column; `resurrect` (32 abilities) is model replenishment (Invocation of Nehek style) and
  has zero overlap with spawns.
- `unit_abilities.type = wh_type_summon_unit` is a LABEL, not the definition: it misses real spawners
  whose label is augment / explosion / direct-damage, and it includes at least one illusion.

## Counts (inventory of 1,799)
- 170 real spawns in the inventory; **85 in-wheel** (85 keys / 71 names); 0 implemented when the class
  was opened.
- The 72 figure = the `wh_type_summon_unit` subset (one illusion in, 14 real spawners out).
- Unlabelled spawners (14 keys / 11 names): Beast Pack, Blacktoof's Conjuration, Call to Gwindalor,
  Eye of Khorne, Lesser Raise Dead, Savage Dominion, Savage Predators, The Dreaded Thirteenth Spell
  (4 keys), Tide of Death, Tide of Pox, Wake Da Idol.

## Illusions
- Exactly four rows in the game carry `spawn_is_decoy = true`: Call of the Shadow Dancer
  (`wh2_dlc10_lord_abilities_deadly_mislead`), Deceiving Shadows, Doppelgang, Mislead.
- Corroborate with the spawned unit's "- Decoy" on-screen name and a `*_mirror` man-entity.
- All four are refused by the engine while engaged in melee - a melee-only trigger can never fire them.

## Gate of Khorne (first implemented summon)
- Key `wh3_main_character_abilities_gate_of_khorne` (no dlc-prefixed variant).
- Summons 100 Bloodletters; 1 use; 120 s recharge (60 s initial); 10 s active; 5 s wind-up; 50 m.
- `target_ground=true`, `target_friends=true`, `target_self=false`; no phase rows; restriction
  `climbing_manning_eq_on_platform`; `ai_usage = hex_melee` - the AI places it on the enemy it fights.
- Implemented as `enemy_ground_melee`: enemy alive+valid+in melee+within the 70% bound (35 m from
  50 m), closest wins, cast via `perform_special_ability_ground(key, enemy:position(), 0, 0)` with
  fresh handles, logging the chosen enemy type and the real distance.

## Trigger design for the class
- "In melee" is data-supported (most summon AI tags are engagement-driven), but "ground below self" is
  only correct for the self/ally-ground subset: some summons take no ground point, some take only an
  enemy-ground point (own feet inverts them), and illusions are refused in melee.
- Preferred shape: charge-window-or-melee, with the cast point looked up from each ability's own flags.
  Minimum viable v1: the self/ally-ground keys only.

## Playability (unobtainable abilities)
- Boss-only detection needs more than a `_boss` substring: `*_big_boss*` keys are ordinary recruitable
  Big Boss heroes (`multiplayer_qb_cap = 2`, real recruitment cost, shared attribute group). Real boss
  variants have bespoke attribute groups and are usually `unbreakable`.
- Verified non-playable: Master of Souls (only owner a campaign Terrorgheist boss), Servants of Nagash
  (`_boss`-only, MP cap 0). 15 in-wheel abilities are `_boss`-only overall.
- Limit: roughly half the in-wheel abilities have no grant row in the extracted junctions because
  item/weapon grants live in tables that were not extracted - state that rather than claiming a full
  audit.

## In-wheel scope definition (the single exclusion rule)

- In scope iff `unit_abilities.source_type` is a unit-side type (active/bound/lord/character/unit/item/
  rune/weapon); the ability is drawable (`icon_name` set, `is_hidden_in_ui=false`, a
  `unit_special_abilities` row); and it is not spell/cataclysm/army/quest.
- Roster junctions alone are insufficient: hundreds of working keys are item/weapon-granted with no
  roster row.
- Counts move every round; read them from the workbook's Numbers sheet and the tracker, never from
  this file. Latest recount (v5): 1,799 rows; 1,141 in-wheel; 658 excluded; 682 implemented; 459 not.
  An older split (spells 418, army 204, cataclysm 16, quest 1 = 639) predates the family-size
  re-attribution, so do not add its parts hoping to reach the current total.
- Count by FAMILY SIZE: the earlier "army 117" was a rule-attribution figure; the family actually holds
  204.

## Transforms (the sibling class, not summons)

Identify from the data, never from key names or a tracker label:
`unit_special_abilities.spawn_is_transformation = true` OR `unit_abilities.type = wh_type_transform`,
then confirm the swap actually replaces the caster (a `spawned_unit` row plus
`spawn_shares_health_and_fatigue` as corroboration).

- **17 keys / 5 names in the inventory, all in-wheel, none implemented:**
  Tz'arkan (5: base, `_mp`, `_snikch`, `_spite`, `_spite_mp`); Formless Horror (4: base,
  `_changeling`, `_quest_battle`, `_quest_battle_changeling_form`); Transformation of the Dragon
  (6: jade / iron / storm, each with `_dragon_form` and `_human_form`); Burrow and Surface
  (`wh3_dlc27_unit_abilities_dread_maw_underground` / `_surface`).
- **A typed transform with no `spawned_unit` is model-state or movement**, not a unit swap (Mist Form,
  Shadowstrider). List those separately; a target-swap trigger would be meaningless for them.
- **Kadon is a genuine summon, not a transform.** Check all four signals before reclassifying:
  `spawn_is_transformation = false`, `spawn_shares_health_and_fatigue = false`,
  `type = wh_type_summon_unit`, and a spawned unit (a generic summoned manticore) unrelated to the
  caster. "It spawns something" decides nothing on its own.
- **A name-derived class list will be wrong in both directions.** One such list held ten real
  transforms plus Kadon and missed seven keys (three dragon forms, two Formless Horrors, both Dread
  Maw), while Burrow/Surface sat in the tracker as excluded summons. Regenerate class lists from the
  columns and diff them against the tracker before reporting a count.
- The 17 keys are mostly lord-granted swap forms; before proposing triggers, run the playability and
  grant-junction checks above, since an unobtainable transform is not worth designing for.
