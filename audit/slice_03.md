# Ability logic audit — slice 3 (entries 117–174, source order)

Counts: **58 audited · 1 flagged · 57 clean**.
Audited: `ABILITIES` entries 117–174 of `C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua`, in source order.
Game data: extracted tables `%LOCALAPPDATA%\Temp\wh3\` (`unit_spec_abil.tsv`, `unit_abilities.tsv`, `phase_junc.tsv`, `phases.tsv`, loc files) and `%LOCALAPPDATA%\Temp\wh3\uieff\`.
Engine context applied: all 57 non-flagged entries cast on **self** via the default `perform_special_ability(key, unit)` call (no cast_target writer and no ground key among these) — which matches the game's data for them: every one is a self augment, a self-centred self+allies aura, or a self-centred hex (`ai_usage` = augment_melee_self / augment_melee_area / augment_defense_melee(_area) / augment_melee / augment_self_area / hex_melee_area_self). Trigger mix: 52× `melee_unwavering`, 5× `charge_or_melee`, 1× `melee_health75`.

## FLAGGED

### Potion of Toughness
- **Marker / key:** `potion_of_toughness` — `wh_main_item_abilities_potion_of_toughness` (entry 118, source line 672)
- **Mod's current logic:** trigger `melee_health75` — fires only when the unit is **in melee AND its own health is at or below 75%** (and not routing); cast on self via the default self-target call. The mod's own comment calls it "a ONE-TIME activation treated as a HEAL".
- **What the game declares:** an active, self-targeted augment (`unit_abilities.type` = wh_type_augment; `unit_special_abilities` affect_self = true, all unit-target flags false, `ai_usage` = augment_melee_self) that for 21 s grants +30 armour, +24 melee defence and a small HP regeneration (heal_amount 0.0080); one use, 60 s recharge. Its game text: *"Those that consume a Potion of Toughness find their skin hardening as swords and arrows glance off their body…"* — i.e. protection that explicitly includes **missile fire**.
- **Why it does not make sense:** the mod treats the potion as a heal, yet gates it behind melee contact, so the defensive consumable can never fire before contact or while taking missile/artillery damage — exactly the "arrows" case its own text advertises ("a heal should not need melee"). The ≤75%-health arm alone already provides the "when hurt" condition; the extra melee requirement is not implied by the effect.
- **Feasibility note:** both reads exist (is_in_melee and the proven HealthPercent read), and a health-only evaluator already ships (`ushoran_health` — the Ghoul King of Ushoran / Star of Avelorn "health ≤75%, no melee gate" pattern), so removing the melee arm needs no new reads or engine support. Note the tracker records the melee gate as a deliberate choice (armour/defence rationale), so this is flagged as a game-logic mismatch, not an engine limit.

## CLEAN

- potion_of_strength (117)
- quickblood (119)
- quicksilver_strike (120)
- rage_embodied (121)
- rage_incarnate (122)
- rapier_of_ecstasy (123)
- red_ruin (124)
- refuse_to_die (125)
- revenge_incarnate (126)
- rock_of_itza (127)
- rot_or_die (128)
- rot_pocked_axe (129)
- rune_axe_of_gotrek (130)
- rune_axe_of_grombrindal (131)
- runefang (132)
- sacred_spawning_of_xhotl (133)
- sands_of_sickness (134)
- scales_of_the_celestial_court (135)
- sceptre_of_titans (136)
- scourge (137)
- scrying_stone (138)
- seduction_of_the_serpent (139)
- shadow_shroud (140)
- shield_of_aeons (141)
- shield_of_faith (142)
- silver_dagger (143)
- skull_wand_of_kaloth (144)
- slippery (145)
- sliverslash (146)
- smash_em_faster (147)
- stand_or_die (148)
- star_lance (149)
- starcrusher (150)
- steppe_hunters_horn (151)
- stinky_giant_club (152)
- storm_rage (153)
- stormlance (154)
- strike_of_tombs (155)
- sword_dance (156)
- sword_of_anti_heroes (157)
- sword_of_lyonesse (158)
- sword_of_torgald (159)
- talabecland_runefang (160)
- tempest_rage (161)
- tenebrous_forge_hammer (162)
- the_armour_of_morkar (163)
- the_black_cleaver (164)
- the_blood_price (165)
- the_carstein_ring (166)
- the_daemons_curse (167)
- the_eternal_blade (168)
- the_father_of_blades (169)
- the_horn_of_kygor (170)
- the_mace_of_helsturm (171)
- the_phoenix_blade (172)
- the_reikland_runefang (173)
- the_rock_of_inevitability (174)
