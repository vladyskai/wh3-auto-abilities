# WH3 bombardment abilities — research answers for round 106

Date: 2026-10-18 · round 106 (harness 106) · mod pack md5 `9108e7f685180cbb637ee8b9ef53cf24`
Author: automatic research pass for the user's four questions (R1–R4), all numbers re-derivable from the
game's own tables under `%LOCALAPPDATA%\Temp\wh3\` and from
`mod_source\script\battle\mod\zz_test_deadly_onslaught.lua`.

**Sources used (no wiki, no guesswork):**

| file | what it gives |
|---|---|
| `unit_abilities.tsv` | the game's own ability TYPE (`wh_type_*`), `source_type` (active / bound / lord / army / spell …), `icon_name`, `is_hidden_in_ui` |
| `unit_spec_abil.tsv` | `target_friends / target_enemies / target_ground / target_self`, `target_intercept_range` (the CAST range), `effect_range` (the area radius, 0 = self-only), `num_uses`, `recharge_time`, `wind_up_time`, `ai_usage`, `targetting_aoe`, `bombardment`, `spawn_type` |
| `land_abil.tsv`, `uset_ability.tsv`, `army_spec.tsv` | which unit / unit-set / army bar carries an ability |
| `land_units.loc.tsv`, `db_land_units.tsv` | the in-game unit names, `class`, `category` |
| `db_unit_attributes_to_groups_junctions.tsv` | the `flying` attribute per unit type |
| `special_ability_to_invalid_usage_flags_tables.tsv` | the engine's own "cannot use while …" flags (`grounded`, `engaged_in_melee`, …) |
| `battle_unit.lua` (API dump) | the script reads: `is_infantry()`, `is_currently_flying()`, `unit_distance()` |

---

## R1 — How many bombardment abilities are there? (your 57)

### The definition used here

An ability counts as a **bombardment ability** when ALL of these hold in the game's own data:

1. `unit_abilities.type = wh_type_bombardment` — the engine's own type label, not a name guess;
2. it is **unit-side**: `unit_abilities.source_type` ∈ {active, bound, lord, character, unit, item, rune,
   weapon} — i.e. it can sit on a unit's ability bar (a wheel button or a bound/item button);
3. it has a real `unit_special_abilities` row (a battle ability with phases, not a campaign command),
   `is_hidden_in_ui = false` and a non-empty `icon_name` (drawable);
4. it is **not** an army-bar junction (`army_spec.tsv`).

### The count

| step | keys |
|---|---|
| every `wh_type_bombardment` row in `unit_abilities.tsv` (spells, army abilities and passives included) | **131** |
| … of which unit-side with a real ability row (steps 2–3) | **58** |
| … of which are ALSO army-bar junction entries in `army_spec.tsv` | **3** |
| **unit-side, non-army = the implementable bombardment set** | **55** |

The 3 army-bar rows inside the 58 are:
`wh3_dlc20_cataclysm_bound_thorsens_thunderstorm`, `wh3_dlc27_cataclysm_bound_thorsens_thunderstorm`
(Thorsen's Thunderstorm ×2) and `wh3_dlc29_army_abilities_pestilential_bombardment` (**Bubonic Broadside**).

### Where your 57 comes from — and where it differs

**57 = the 58 unit-side rows minus Bubonic Broadside.** That is the only arithmetic in the data that lands
exactly on 57: Bubonic Broadside is the one of the three army-bar rows that also *looks* like a wheel
ability (`source_type = active`, a normal icon, `wh_type_bombardment`) and its key does not say
"cataclysm", so it is the natural one to drop when counting by hand.

**Your 57 is therefore correct under the reading "unit-side bombardment rows, excluding the army-bar
bombardment".** Two honest caveats:

* Under the stricter wheel rule (also drop the two `cataclysm_bound` Thorsen's keys, which are army-bar
  junctions too) the number is **55**.
* The tracker's own "Bombardment / ground artillery" family is a **different set** and has **63 rows** —
  it is not the game's type. Of those 63, **34** are not in the 58 at all (28 `source_type = army`,
  5 bound Dreaded-Thirteenth summon keys, 1 active, plus one key with no `unit_abilities` row), and it
  **misses 30** of the 58 — mostly the air-drop family (Drop Rocks, Gyrobomber Bomb, Skyhammer Bomb, …),
  which the tracker never filed under bombardment. So a tracker-derived count cannot reproduce 57; the
  data-derived count can.

**Bottom line: 58 unit-side / 55 after the strict army-bar rule / your 57 = 58 − Bubonic Broadside.**
The round implemented **30 of your 32 approved abilities** (see the appendix) — the two exceptions are
Thorsen's Thunderstorm (army-bar) and Warp Lightning Rod (no enemy target, see R3's sibling case).

---

## R2 — Who grants Call of Tor, Undeath from Above and Bubonic Broadside?

Join path: `unit_abilities` row → `land_abil.ability` (unit junction) or `uset_ability.unit_ability`
(unit-SET junction) → `land_units.loc.tsv` `land_units_onscreen_name_<key>`; army abilities via
`army_spec.tsv`; items/weapons via their `source_type` (the battle tables carry no item→unit junction,
which is normal for this project — most item abilities have no roster row either).

### Call of Tor — `wh3_twa07_spell_bound_call_of_tor`

* **Granted by: Oath-Brothers of Tor (War Bear Riders)** — `wh3_twa07_ksl_cav_war_bear_riders_ror_0`
  (a Kislev Regiment of Renown; `land_abil.tsv` names it directly).
* Bound spell, `source_type = bound`, **unlimited uses** (`num_uses = -1`), 90 s recharge, 1 s wind-up.
* **Self-centred**: `target_friends / target_enemies / target_ground / target_self` are ALL false,
  `target_intercept_range = 0`, and the engine's own `ai_usage = aoe_centred_on_self` with
  `targetting_aoe = wh_spell_generic_bombardment`. It is a bombardment AROUND THE CASTER, not a cast at
  an enemy.
* **Confidence: high** (direct `land_abil` junction + the unit's own display name matches the ability name).

### Undeath from Above — `wh3_dlc29_unit_abilities_undeath_from_above`

* **Granted by: the Deck Droppers unit set** `wh2_dlc11_cst_deck_droppers` (`uset_ability.tsv`), i.e. all
  four Vampire-Coast Deck Droppers variants:
  **Deck Droppers** (`wh2_dlc11_cst_cav_deck_droppers_0`), **Deck Droppers (Bombers)** (`_1`),
  **Deck Droppers (Handgunners)** (`_2`) and **Salt Lord Scuttlers (Deck Droppers – Bombers)** (`_ror_0`).
  All four carry the `flying` attribute.
* The same unit set also carries **Drop Rocks** (`deck_droppers_drop_cannonballs`) — a useful corroboration
  that the set is the "drop bombs from the sky" family.
* One use, 1 s active, no wind-up, range 10, no target flags (self-centred drop), `bombardment` self-reference,
  `targetting_aoe = wh_abilities_bomb_drop`, and an engine invalid-usage flag **`engaged_in_melee`**.
* **Confidence: high** (unit-set junction + the set's own key names the four units + the drop tooltip).

### Bubonic Broadside — `wh3_dlc29_army_abilities_pestilential_bombardment`

* **It is an ARMY-BAR ability.** `army_spec.tsv` lists it (`wh3_dlc29_army_abilities_pestilential_bombardment
  → wh3_dlc29_army_abilities_pestilential_bombardment`, unique id 722213027). It has **no** `land_abil`,
  **no** `uset_ability` and **no** `sag_to_abilities` junction — nothing in the battle tables grants it to a
  unit, a lord, a hero, an item or a mount.
* The game's own tooltip names its source: *"On **Gutrot's** signal, the **plague fleet** unleashes a
  plague-infused barrage at the target."* Gutrot Spume is `wh3_dlc29_chs_cha_gutrot_spume` (plus his Warshrine
  variant), and his land-unit ability list does NOT contain it — consistent with a campaign army ability
  unlocked through the DLC29 (Gutrot Spume) campaign rather than a wheel button.
* Row shape: `uniqueness = wh_main_anc_group_unique`, `is_unit_upgrade = true`, `target_ground = true`,
  `target_intercept_range = -1` (no range), 2 uses, 90 s, 5 s wind-up, `ai_usage = aoe_bombardment`.
* **Confidence: high that it is an army-bar ability with no unit/item/mount grant; medium on the exact
  campaign carrier (Gutrot Spume's plague fleet) — the campaign tables are not part of this extraction.**
* Consequence: out of wheel scope (standing rule), so it cannot be automated; it is reported, not implemented.

---

## R3 — "On top of an infantry unit": the nine

The nine you named: **Death from Above, Drop Rocks, Drop Sphere, Fire Bombs, Gyrobomber Bomb,
Searing Torrent, Sky-Junk Bomb, Skyhammer Bomb, Wake of Fire.**

### What the data says the mechanic actually is

All nine are `wh_type_bombardment` with **no target flags at all** (`target_friends`, `target_enemies`,
`target_ground`, `target_self` all false), `effect_range = 0`, `target_intercept_range = 10` (except
Searing Torrent's row, which is the same shape), `ai_usage = always_use_only_land`, and a
`bombardment` column that points at the ability itself plus a `targetting_aoe` of
`wh_abilities_bomb_drop` / `wh_abilities_bomb_small_drop`. In plain terms: **the ability is a bomb release
centred on the caster; there is no enemy to click.** The engine drops the ordnance where the flyer is.

The engine's own restriction flags confirm the air requirement — but only for some of them:

| ability | key | carrier (in game) | flying? | engine "cannot use while" flags |
|---|---|---|---|---|
| Death from Above | `wh2_dlc09_unit_abilities_death_from_above` | The Flock of Djaf (Carrion) | yes | `engaged_in_melee` |
| Drop Rocks | `wh2_main_unit_abilities_drop_rocks` (+ `_character`, `_of_chotec`, `_of_sundering`) | Terradon Riders + variants; Deck Droppers (via unit set) | yes | `engaged_in_melee` |
| Drop Sphere of Tepok | `wh2_dlc12_lord_abilities_drop_sphere_of_tepok` (+ `_upgraded`) | Tiktaq'to (both variants) | yes | `engaged_in_melee` |
| Fire Bombs | `wh3_dlc25_unit_abilities_gyrobomber_fire_bomb` (and `wh3_dlc25_unit_abilities_thunderbarge_fire_bomb`) | Gyrobombers (set `dwf_gyrobombers_no_ror`); the Thunderbarge variant has no junction in this extract | yes | `climbing`, **`grounded`**, `phase_is_deployment` |
| Gyrobomber Bomb | `wh_main_unit_abilities_gyrobomber_bomb` | Gyrobombers | yes | `climbing`, **`grounded`**, `phase_is_deployment` |
| Searing Torrent | `wh3_twa07_unit_abilities_searing_torrent` | Knights of Immolation (Doom Knights of Tzeentch) | **no** (disc-riding cavalry) | `engaged_in_melee` |
| Sky-Junk Bomb | `wh3_main_unit_abilities_sky_junk_bomb` | Sky-junk | vehicle (airframe) | none |
| Skyhammer Bomb | `wh_dlc06_unit_abilities_skyhammer_bomb` | Skyhammer Squadron (Gyrobombers) | yes | `climbing`, **`grounded`**, `phase_is_deployment` |
| Wake of Fire | `wh2_main_unit_abilities_wake_of_fire` | Flamespyre Phoenix | yes | `engaged_in_melee` |

**So the requirement is positional, not a target-type restriction.** The engine does not say "target must
be infantry"; it says "this is a self-centred drop, and for four of them you must be airborne". The
"on top of an infantry unit" framing is a PLAYER rule: the bomb only pays off if the flyer is physically
over a unit, and infantry is the dense target class.

### Can this be checked from the script layer? Honestly, in three parts

**(a) Is the enemy infantry? — YES, with a real read.**
`battle_unit:is_infantry()` is documented in the API dump ("Returns whether this is a unit of infantry").
The fallback is `battle_unit:unit_class()` (documented: "the class of the unit, from the land_units table"),
compared by EXACT equality against the three infantry class strings `inf_mel` / `inf_mis` / `inf_spr`
(the game's class column also has `com`, `cav_*`, `chariot`, `art_fld`, `spcl`). Both raising → **fail
closed** (treated as NOT infantry). This is exactly what round 106 implemented as
`FOURTH.enemy_is_infantry` — no 942-key derived list is needed, and a list would silently miss DLC keys.

**(b) Is the caster airborne? — YES.**
`battle_unit:is_currently_flying()` is documented ("Returns whether the unit can fly and is currently
flying"); `can_fly()` answers the type-level question. For the four abilities with the `grounded` invalid
flag the engine refuses the cast on the ground by itself, so this read is a belt-and-braces guard, not a
requirement. For the others it is the only way to know the drop will land "from above".

**(c) Does the ground point overlap the unit's footprint? — ONLY AS A PROXY.**
There is **no per-unit footprint or radius read** in the battle script API. `unit_distance(other)` is
documented as "the shortest distance in metres … taking into account their bounding box rather than just
working out the centre-to-centre distance", so two overlapping footprints answer **≈ 0 m** — that is the
best "on top of" test available, and it is a real engine read. But **the bomb's own area radius is NOT in
the extracted data**: `targetting_aoe` names an aoe key (`wh_abilities_bomb_drop` /
`wh_abilities_bomb_small_drop`) whose radius lives in an aoe table that is not part of this extraction, and
`effect_range` is 0. So the true hit radius is unknown and a **constant must be chosen**; the honest
constant is the row's own `target_intercept_range` (10 m) or a tighter contact value, and it should be
logged as a constant, not presented as the game's radius.

### Which of the nine this logic would serve, and which would still be unsafe

* **Servable (airborne, self-centred drop, "be over the enemy" is the whole mechanic):**
  Death from Above, Drop Rocks, Drop Sphere of Tepok, Fire Bombs, Gyrobomber Bomb, Sky-Junk Bomb,
  Skyhammer Bomb, Wake of Fire. A trigger of the shape *"while airborne (is_currently_flying) and an enemy
  INFANTRY unit is within the constant radius of the caster — fire the self-centred drop"* is honest and
  testable. Note it is still a **proximity** test, not a footprint-overlap proof: it cannot know the bomb's
  real blast radius, so it should use a conservative distance and say so.
* **Not safe: Searing Torrent.** Its carrier is a ground unit (disc-riding Doom Knights, no `flying`
  attribute), its invalid flag is `engaged_in_melee` (not `grounded`), and its row is a self-centred
  10 m nova. The "drop from above" model does not describe it at all. If it is ever automated it needs a
  different rule — *"not in melee and an enemy infantry unit within ~10 m"* — and that is a separate
  decision, not a variant of the drop family.
* **Also worth naming:** Call of Tor is the same self-centred shape (`ai_usage = aoe_centred_on_self`), and
  Warp Lightning Rod has no target flags and range 0 — neither can be cast "at an enemy" at all.

Round 106 did **not** implement the nine. They are a distinct trigger family (caster-position based, not
enemy-target based) and the user has not yet approved a rule for them; the research above is the input
for that decision.

---

## R4 — Nan-Gau Grenades

`wh3_dlc24_unit_abilities_nan_gau_grenades` (the `bombardment` column points at
`wh3_dlc24_unit_abilities_nan_gau_grenade`, singular — the same-family id).

| field | value |
|---|---|
| type | `wh_type_bombardment`, `source_type = active` |
| granted to | **Empress Crowmen (Onyx Crowmen)** — `wh3_dlc24_cth_inf_onyx_crowmen_ror`, a Cathay Regiment of Renown; `flying` attribute |
| target flags | friends / enemies / ground / self ALL **false** — self-centred, no target to click |
| range | `target_intercept_range = 10` m, `effect_range = 0` |
| uses / recharge | **2 uses**, 60 s recharge (`shared_recharge_time = -1`, per-use) |
| wind-up | 0 (instant) |
| aoe | `targetting_aoe = wh_abilities_bomb_small_drop`, `ai_usage = always_use_only_land`, `wind_up_stance = cast_up_short` |
| engine restriction | invalid while **`grounded`** — it is an AIR-ONLY ability |
| tooltip | *"Who would have thought such a small, unassuming object could cause such overwhelming damage?"* |

**The mechanic:** a small-radius bomb dropped from a flying unit onto whatever is beneath it. Two uses,
60 s apart. Because it is self-centred, the only decision the mod can make is WHEN to press it — the
placement is wherever the Crowmen happen to be.

### Trigger ideas, ranked

1. **BEST — "airborne, over an infantry unit":** fire when `is_currently_flying()` is true AND the closest
   enemy INFANTRY unit is within the drop constant (10 m — the row's own `target_intercept_range`;
   log the real distance), and cast through the unit form on SELF. **Why:** it is the only rule that makes
   the small blast pay — infantry is the dense class, the `grounded` flag proves the ability is meant to
   be used in the air, and the same `enemy_is_infantry` read already exists from this round. It also
   naturally throttles: the Crowmen must actually be over something.
2. **Any enemy unit within 10 m while airborne:** simplest and most casts, but it spends one of the two
   uses on single entities / monsters / heroes where a small bomb is wasted, and it fights the ability's
   own `always_use_only_land` targeting intent less well than #1 (a single model is a poor bomb target).
3. **Cluster rule — the densest enemy group within ~8 m of a candidate point:** best expected value
   (count enemies within the blast, pick the maximum), but the cast is still self-centred, so the mod can
   only pick the MOMENT, not the point; it needs a neighbour scan per candidate (O(n²) over the enemy
   list) and the blast radius is a constant anyway. Worth doing only after #1 proves the ability lands.

**Chosen: #1.** It is honest about what the data says (air-only, self-centred, small radius), it reuses the
infantry read the round already built, and it fails closed on every unreadable value. #3 is a later
refinement on top of it, not a replacement.

---

## Appendix — the 32 approved abilities: what shipped and what did not

**Implemented: 30 of 32** (31 keys; Slicing Shards carries two keys in one entry) on
`enemy_ground_melee_infantry`, bound = floor(0.70 × the row's real `target_intercept_range`).

| # | Ability | key | real range → bound | cast form |
|---|---|---|---|---|
| 1 | Assault of Stone | `wh2_dlc10_item_bound_assault_of_stone` | 200 → 140 | ground |
| 2 | Axe of Tor | `wh3_main_weapon_abilities_axe_of_tor` | 200 → 140 | ground |
| 3 | Celestial Comet | `wh3_main_mount_bound_celestial_comet` | 200 → 140 | ground |
| 4 | Celestial Lightning | `wh3_main_mount_bound_celestial_lightning` | 300 → 210 | ground |
| 5 | Chalice of Potions | `wh_dlc07_item_abilities_chalice_of_potions` | 200 → 140 | ground |
| 6 | Comet of Casandora | `wh3_main_spell_bound_comet_of_casandora` | 200 → 140 | ground |
| 7 | Dragon Ogre's Great Horn | `wh_dlc08_item_abilities_great_horn_of_dragon_ogre` | 200 → 140 | ground |
| 8 | Flame & Shadow | `wh3_dlc23_lord_abilities_flame_and_shadow` | 100 → 70 | ground |
| 9 | Hawk's Talon | `wh_dlc05_weapon_abilities_hawks_talon` | 200 → 140 | ground |
| 10 | Isha's Rain | `wh2_dlc13_character_ability_ishas_rain` | 200 → 140 | ground |
| 11 | Klad Brakak | `wh2_dlc17_spell_bound_urannons_thunderbolt_upgraded` | 30 → 21 | ground |
| 12 | Lesser Doombolt | `wh2_dlc10_spell_bound_lesser_doombolt` | 200 → 140 | **unit** |
| 13 | Lightning Strike | `wh3_dlc29_unit_abilities_lightning_strike` | 300 → 210 | ground |
| 14 | Lord of the Storm | `wh_main_lord_abilities_lord_of_the_storm` | 200 → 140 | ground |
| 15 | Master of Lightning | `wh3_dlc29_spell_bound_warp_lightning` | 200 → 140 | ground |
| 16 | Meteor Strike | `wh3_dlc29_unit_abilities_meteor_strike` | 200 → 140 | ground |
| 17 | Nemesis Crown | `wh3_dlc25_lord_abilities_nemesis_crown` | 100 → 70 | ground |
| 18 | Piercing Bolts of Burning | `wh_main_spell_bound_piercing_bolts_of_burning` | 200 → 140 | ground |
| 19 | Pigeon Bomb | `wh3_dlc25_character_abilities_pigeon_bomb` | 200 → 140 | ground |
| 20 | Rod of the Storm | `wh2_main_spell_bound_rod_of_the_storm` | 300 → 210 | ground |
| 21 | Rod of Torment | `wh3_dlc20_item_abilities_rod_of_torment` | 200 → 140 | **unit** |
| 22 | Sceptre of Stone | `wh2_dlc10_item_abilities_sceptre_of_stone` | 200 → 140 | ground |
| 23 | Searing Doom | `wh3_twa08_spell_bound_searing_doom` | 200 → 140 | ground |
| 24 | Slicing Shards | `wh3_dlc20_spell_bound_slicing_shards` + `wh3_main_spell_slaanesh_slicing_shards_bound` | 200 → 140 | ground |
| 25 | The Bow of Loren | `wh_dlc05_weapon_abilities_the_bow_of_loren` | 200 → 140 | ground |
| 26 | Tome of Furion | `wh2_main_spell_bound_tome_of_furion` | 200 → 140 | **unit** |
| 27 | Urannon's Thunderbolt | `wh2_dlc17_spell_bound_urannons_thunderbolt` | 300 → 210 | ground |
| 28 | Wand of the Kharaidon | `wh2_main_spell_bound_wand_of_the_kharaidon` | 200 → 140 | **unit** |
| 29 | Wolf's Howl | `wh3_main_weapon_abilities_the_traitors_sword` | 200 → 140 | **unit** |
| 30 | Wraith Storm | `wh2_dlc11_lord_abilities_wraith_storm` | 200 → 140 | **unit** |

**Not implemented — reported for your ruling:**

| # | Ability | key(s) | why |
|---|---|---|---|
| 31 | Thorsen's Thunderstorm | `wh3_dlc20_cataclysm_bound_thorsens_thunderstorm`, `wh3_dlc27_cataclysm_bound_thorsens_thunderstorm` | **ARMY-BAR**: both keys are `army_spec.tsv` junctions (`target_friends = true`, `target_ground = true`, range −1). Out of wheel scope under the standing rule. |
| 32 | Warp Lightning Rod | `wh2_dlc16_unit_abilities_warp_lightning_rod` | **No enemy target at all**: `target_friends / target_enemies / target_ground / target_self` all false, `target_intercept_range = 0`, `ai_usage` self-centred. There is nothing to cast "at an enemy"; it is the same self-centred shape as Soulfire, so if you want it automated it belongs on a caster-position rule, not this family. |

**Nothing else was skipped**: every other name on the 32-list resolved to exactly one implementable key set
(the alternate engine keys — the base spell rows, the army Rod of the Storm, the three Slicing Shards
variants — were deliberately left out: they are `source_type = spell` / `army`, i.e. out of wheel scope).
