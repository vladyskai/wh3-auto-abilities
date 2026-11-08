# WARHAMMER III Auto-Ability Project — every ability in the game, and how to fire it well

Research date: **4 October 2026** · Game state: **Update 9.0** · For: choosing what to build next for the auto-ability mod.

**What this report is.** A complete inventory of the game's clickable battle abilities, the "perfect player" moment for each kind, what our mod can actually detect of that moment today, a collapse of all of it into **seven practical activation rules**, the new machinery each rule needs ranked by payoff, what the community "Autoactivate" mod does about the same problem, and a recommended build order. Everything here is read from the game's own files on this machine, its vanilla scripts, or cited web sources; counts and example ability names can be checked line-by-line.

**Where the raw material lives (used throughout, referred to by short name):**

- **The dump folder** `C:\Users\vlady\AppData\Local\Temp\wh3\`
  - `unit_spec_abil.tsv` — all 3,173 ability definitions with 71 columns (recharge, duration, targeting flags, AI usage tag, etc.) — a public mirror of the same table exists for checking [9]
  - `unit_abilities.tsv` — for each ability: its kind (`source_type`) and its display class (`type`, e.g. `wh_type_hex`)
  - `land_abil.tsv` — which land units innately carry which ability (9,686 rows)
  - `flags.tsv`, `special_ability_to_auto_deactivate_flags_tables.tsv`, `special_ability_to_invalid_usage_flags_tables.tsv`, `special_ability_to_invalid_target_flags_tables.tsv` — the engine's own condition vocabulary and the conditions under which it refuses a cast
  - `battle_unit.lua`, `battle_unitcontroller.lua`, `battle_army.lua` — the game's scripting interface dumps (what a Lua mod can call; public copies of these three: [10][11][12])
- **The vanilla scripts** `C:\Users\vlady\AppData\Local\Temp\WH3-scripts\script\` (901 battle scripts — how the game itself asks units to use abilities)
- **Our mod's own source** `C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua` (the readable copy; referred to as "the mod file")
- **Prior research from this project** `C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_mods.md` and `WH3_auto_ability_mod_feasibility.md`

---

## 1. INVENTORY SUMMARY — how many abilities exist, and what kind they are

**The filter.** A row counts as a *castable battle ability* if: it is not engine-run (`passive = false` in `unit_spec_abil.tsv`), it is not a passive leftover (`recharge_time` not −1), it is granted by something connected to battle (`source_type` in `unit_abilities.tsv` is not `passive`, `building` or `replenishments`), and it is not a hidden internal helper (`is_hidden_in_ui = false`). Same basis as the earlier feasibility study.

| Stage | Count |
|---|---|
| All definitions in the game's ability table | 3,173 |
| − engine-run passives (`passive = true`) | −1,289 |
| − leftover passive-style rows (`recharge_time = −1`) | −69 |
| − campaign-side leftovers (building / supply tables) | −4 |
| − hidden internal helpers (`is_hidden_in_ui = true`) | −14 |
| **= castable / active battle abilities** | **1,797** |

The four abilities the mod handles today all sit in this set: Deadly Onslaught `wh_main_character_abilities_deadly_onslaught` (90 s cooldown, 31 s duration), Foe-Seeker `wh_main_character_abilities_foe_seeker`, Hammer of Sigmar `wh_main_spell_bound_hammer_of_sigmar`, Stand Your Ground `wh_main_character_abilities_stand_your_ground` — all visible in the mod file and in `unit_spec_abil.tsv`.

### By where the ability comes from (`source_type`)

| Kind | Count | Plain meaning | Example |
|---|---|---|---|
| `active` | 941 | clickable abilities granted by skills, items, unit upgrades | Deadly Onslaught, Stand Your Ground |
| `spell` | 418 | the magic-lore spells of wizards | Fireball, Comet of Casandora |
| `army` | 204 | army-ability bar (above the unit cards, not the unit dial) | Barrage of the Legion |
| `bound` | 176 | "bound spell" charges from items/abilities | Hammer of Sigmar (bound), Curse of Anraheir |
| `cataclysm` | 16 | large scenario spells | Magma Storm |
| `rune`, `item`, `lord`, `unit`, `character`, `quest`, `weapon` | 42 | dwarf runes, item actions, lord-only moves, etc. | Master Rune of Speed |

### By what it must be pointed at (the target flags in `unit_spec_abil.tsv`)

| Pointing style | Count | Meaning for the mod |
|---|---|---|
| self / no target needed | **544** | castable today with the existing call |
| enemy unit (click a unit) | 326 | needs an enemy unit handle |
| enemy position (click ground near enemies) | 443 | needs a ground point *and* a decision where |
| friendly unit (click a unit) | 198 | needs an ally picker |
| friendly position (click ground near friends) | 161 | ground point near allies |
| bare ground point | 125 | ground point only |

**1,253 of the 1,797 (70%) need the mod to point at something other than itself** — and that pointing machinery is the single biggest gap. Examples: Fireball `wh_main_spell_fire_fireball` (enemy unit, 300 m), Tactician's Stand Your Ground `wh3_dlc24_character_abilities_tacticians_stand_your_ground` (friendly position — already wired in the mod file, cast at the caster's own feet).

### By effect family (collapsing the 30 `type` values in `unit_abilities.tsv`)

| Family | Count | Examples |
|---|---|---|
| Damage (vortex, bombardment, explosion, breath, wind, direct damage, missiles) | 663 | Comet of Casandora; Wind of Death; Fireball |
| Buff (augment, ward save, area-of-augment) | 623 | Foe-Seeker; Hammer of Sigmar; Light of Battle |
| Debuff (hex families) | 258 | Soulblight; Curse of Anraheir; Enfeebling Foe |
| Summon / transform | 163 | Realm-of-Souls Ushabti; Feral Cold Ones |
| Heal / regeneration | 70 | Regenerating Flesh; Invocation of Nehek; Dreaming Ring |
| Hide / formation utility | 20 | mislead-type abilities, testudo/wedge |
| Movement | ~0 as a family — there is no "movement" category in the table | movement-flavoured abilities (teleport, mislead, `full_hide`) are scattered, a few dozen |

### By timing

| Duration the effect lasts (`active_time`) | Count |
|---|---|
| ≈instant or ≤1 s (fire-and-forget) | 289 |
| 2–10 s | 362 |
| 11–30 s | 792 |
| more than 30 s | 354 |

| Cooldown (`recharge_time`) | Count |
|---|---|
| no cooldown (0 s) | 47 |
| 1–60 s | 790 |
| 61–120 s | 946 |
| more than 120 s | 14 |

Also: **783 abilities have a limited number of uses** (1–10 charges per battle; `num_uses`), 1,013 are unlimited. **994 have a wind-up** (`wind_up_time` > 0 — the "plant your feet for a moment" delay before they fire, up to several seconds). **417 cost magic pool points** (`mana_cost > 0` — all spells). **189 carry a miscast risk** (`miscast_chance` > 0). 207 are "upgraded" (overcast) twin versions of another row. And 607 of the 1,797 appear in `land_abil.tsv` — the direct unit→ability junction, i.e. abilities a unit inherently carries even in a plain custom battle; the rest arrive through character skills, items or the army bar.

### By reach (`target_intercept_range` = how far it can be sent) and area (`effect_range` = size of the patch it makes)

| Sent from standing still at… | Count | Patch size | Count |
|---|---|---|---|
| self only (0 m) | 745 | no patch (single target/self) | 1,421 |
| up to 50 m | 149 | up to ~35 m | 299 |
| 51–100 m | 333 | ~35–70 m | 72 |
| over 100 m (up to 300 m, the ranged spells) | 570 | over 70 m | 5 |

---

## 2. IDEAL STRATEGY — when a perfect player fires each kind

Derived from each row's effect columns plus the game's own AI label for it (`ai_usage`, which is how the battle AI itself decides to use it) and the engine's own switch-off flags where it ships them (`special_ability_to_auto_deactivate_flags_tables.tsv`).

| Family | The perfect moment | The game's own label (column evidence) | Aimed at |
|---|---|---|---|
| Self combat buffs | the instant the unit makes contact — the ability's duration should cover the fight you are already in. | `augment_melee_self` (147), `augment_melee` (112), `augment_melee_area` (95) | self |
| Charge buffs | the split second *before* impact. After contact the charge attack has already resolved — firing then wastes it. (This is also why the community data mods had to patch timing; see §6.) | `augment_charge_self` (15), `augment_charge` (2), `augment_charged_at` (7) | self |
| Melee debuffs | as the fight starts, on the enemy you are engaged with. | `hex_melee` (96), `hex_melee_area` (51+16); morale variants `hex_morale*` (33) | enemy unit / enemy spot |
| Ranged offense (hexes, missiles, direct damage) | at the most valuable enemy inside range, ideally one that cannot answer back; never while pinned in melee (the engine refuses 48 castables while in melee — mostly this kind; examples: `wh2_dlc10_unit_abilities_frost_breath`, `wh2_dlc11_hero_abilities_bomb_throw`). | `hex_ranged*` (61), `projectile_*` (110), `direct_damage_*` (96) | enemy unit |
| Placed attacks (bombardments, vortexes, winds, breaths) | on the biggest clump, aimed where the enemy *will be* after the wind-up (Comet: 5 s). | `aoe_bombardment` (101), `vortex_*` (193), `aoe`/`aoe_ap` (75) | ground point |
| Heals / regeneration | as the unit crosses a health line, before the models actually die — and only if it is not already at the healing cap. | `healing` (49), `healing_area` (17), `healing_single_use` (4) | self or ally |
| Morale support | when morale slides toward the wavering line, before it breaks and runs. | `augment_morale*` (35) | self or ally |
| Summons | when extra bodies change the fight — block a charge, plug a gap, add flank pressure. | `hex_ranged_summon` (42), `threatened` (88); 163 rows in the summon/transform display classes | ground near self/target |
| Spellcaster / staff items | mid casting sequence, benefitting from or feeding the winds pool. | `augment_spellcasting` (43) | self or ally |
| Chaff-clearing utility (hiding, ammo, opportunity attacks) | situation-specific; the game itself only fires these when it sees the opportunity. | `full_hide` (13), `assault_opportunity` (10), `flanking_opportunity` (7), `ammo_replenish` (5) | self |

The game already ships examples of *engine-side* conditions for exactly these moments — e.g. `out_of_melee` is the deactivate-flag for "The Trial of Blades"/"Woven Mist" style abilities, `engaged_in_melee` for Old Guard's Tankard, `health_above_50%` for defensive passives (`special_ability_to_auto_deactivate_flags_tables.tsv`). Those are the moments the designers considered canonical.

---

## 3. PRACTICAL STRATEGY — what our mod can actually see

**The mod's measured vocabulary** (everything it has ever successfully read in a real battle — the project's own record, plus the mod file):

`is_moving_fast()` · `is_in_melee()` · `is_routing()` · `is_shattered()` · `is_wavering()` (the only morale threshold; no percentage exists) · `number_of_men_alive()` · `type()` (unit identity) · `position()` · `current_target()` · `can_perform_special_ability(key)` (say yes/no to "may I cast now" — it does **not** report the cooldown) · the selection callback · per-unit ability ownership · the ability buttons on the dial and their keys.

**Deliberately not available** (measured): morale **percentages**, any **per-unit cooldown read**, and any **enemy information beyond the unit's own current target**. Anything below marked *(unverified)* exists in the game's scripting interface dump but has never been exercised by this mod — those need one test battle before they can be trusted.

| The perfect moment needs… | Can the mod see it? | Consequence |
|---|---|---|
| "in melee" | **Yes** — `is_in_melee()` | Groups 1–2 fire well today |
| "about to hit" (charge) | **Partly** — the mod's own charge test over `is_moving_fast()` + target | Group 4 exists and works; big-unit timing caveat (§6) |
| "the enemy I'm engaging" | **Yes, if the unit has a target** — `current_target()` | Group 2 can be aimed with a one-line plumbing change |
| "an enemy in range / the best enemy / enemies not routing" | **No** — no enemy surveying, no enemy morale | Group 3 can only act on a target the unit *already has*; no "best target" choice |
| "where the enemy stands" (for ground placement) | **Unverified** — current target's position plausible, not yet read | Group 3's ground half needs a placement policy |
| "health below X%" | **No** today; `unary_hitpoints()` exists in the interface dump *(unverified)* | Group 6 (heals/potions) cannot be triaged by health yet — see §5 |
| "men below X%" | **Partly** — `number_of_men_alive()` is measured; the "men at battle start" read exists *(unverified)* | Rough health proxy for multi-model units; useless for single-entity lords |
| "morale wobbling" | **Yes, one band only** — `is_wavering()` | Group 5 works; no "half morale" or "about to rally" fine-tuning |
| "mana low / winds available" | **No** today; `battle_army:winds_of_magic_current()` exists in the dump *(unverified)* | Spell pacing must stay manual or fire-when-ready |
| "cooldown finished" | **No direct read** — only `can_perform_special_ability` + the mod's learned refusals | The readiness gate + cooldown-hold learning stands in; occasional wasted asks |
| "being charged / under missile fire" | **No** — `is_under_missile_attack()` exists in the dump *(unverified)* | Pre-contact reactions stay approximate (use the charge test or in-melee) |
| "a friendly unit routs nearby" | **Yes in principle** — all own-army reads + `position()` math | Feasible small group (see §4 note) |

**The engine's own refusals** also bound what is worth attempting (from `special_ability_to_invalid_usage_flags_tables.tsv`): 346 abilities cannot be cast while climbing; 169 while manning siege equipment; **51 while in melee** (of which 48 in our set); 23 during deployment; 11 while broken. A script that fires blindly will mostly be refused there — the readiness gate absorbs the noise, but the mod should simply not *want* those casts (e.g. do not fire Frost Breath mid-melee).

**Summary of what the mod gives up:** it will never see enemy morale/routing percentages, enemy health, distances to enemies beyond the current target, or exact cooldowns. Everywhere the ideal moment depends on enemy state, the mod must approximate with "what my own unit is doing" (fighting, running, wavering) or "what it already has targeted".

---

## 4. GROUPING — seven activation rules cover all 1,797 abilities

**Method.** Each of the 1,797 abilities was assigned one primary group from its own `ai_usage` tag and targeting flags (the machine-readable way the game itself thinks about it). A handful of oddities fit two groups; counts are accurate to a few.

| # | Group (plain name) | The one-sentence rule the mod would implement | Targeting it needs | Abilities | Examples | New machinery |
|---|---|---|---|---|---|---|
| 1 | **Fight to the death** — self/area buffs & auras | *While the unit is fighting hand-to-hand and not fleeing, switch its combat abilities on.* | none (self), 318; friendly unit, 109; friendly ground, 57 | **488** | Foe-Seeker; Hammer of Sigmar; Rage Embodied; The Slayer of Kings | none for the self-casts; ally picker for the 109 |
| 2 | **Curse the enemy in front of you** — melee debuffs | *Same rule, but aimed at the enemy the unit is already fighting.* | enemy unit, 84; enemy spot, 32 | **147** | Curse of Anraheir; The Hammer of Karak Drazh | pass the current target into the cast call |
| 3 | **Strike what you've already targeted** — ranged offense | *While the unit already has an enemy in its sights, fire the ability at it.* | enemy unit, 238; enemy spot, 409; own spot, 79; other, 164 | **890** | Fireball; Comet of Casandora; Wind of Death; Soulblight | enemy targeting + ground placement policy (see §5) |
| 4 | **Hit them on the way in** — charge buffs | *While the unit is running at the enemy and has not made contact yet, fire.* | self | **27** | Deadly Onslaught; Full Power (`wh3_dlc25_unit_abilities_full_power`) | built — the mod's charge test |
| 5 | **When morale wobbles** — morale support | *While the unit's morale falls to the wavering line, fire.* | self, 23; ally, 11 | **35** | Light of Battle; Crown of Command; Magical Animus | built partly (the melee+wavering trigger); ally picker for 7 |
| 6 | **When the unit (or a friend) is hurt** — heals & panic buttons | *When health (or men) drops below a set line, fire the heal.* | self, 18; ally, 45; ground, 8 | **71** | Regenerating Flesh; Hieratic Jar; Invocation of Nehek; Dreaming Ring | **needs a health read** (§5) or a men-count proxy; ally picker |
| 7 | **Whenever it's ready** — everything with no readable condition | *Fire as soon as the engine allows, on itself (or its current target).* | self, 79; ally, 50; ground, 10 | **139** | Book of Hoeth; Unlimited Power; Stave of Avelorn | none beyond the existing readiness gate |

**Cross-check totals: 488 + 147 + 890 + 27 + 35 + 71 + 139 = 1,797.** ✔

**Where the current four abilities sit:** Deadly Onslaught → group 4; Foe-Seeker and Hammer of Sigmar → group 1; Stand Your Ground → groups 1/5. So the mod today implements three of the seven rules (melee, charge, morale) — but only for self-aimed casts. **The missing targeting machinery is what blocks most of the remaining 1,253 abilities.**

**Notes that belong to the table:**

- Groups 2 and 3 share one plumbing change (aim at `current_target()`); group 3 additionally splits into "click the unit" (238) and "click the ground where the enemy is" (409) forms.
- 204 **army abilities** (`source_type = army`) are cast from the army bar with a different call (`battle_army:use_special_ability`, dump `battle_army.lua` line 127). They are outside the unit-dial design; treat as a separate project (or skip).
- **React-to-a-rout** abilities (e.g. Crown of Command, Were You Goin!? — 6 named in the Autoactivate list [2]) fit inside group 5/7 with a "any friendly unit is `is_routing()`" gate; it is feasible with today's reads and cheap, but small.
- **Summon abilities distribute across groups 1–4** by their tag (`threatened` = fire when engaged; `hex_ranged_summon` = fire when the unit has a target), all needing a ground point near self or target.

---

## 5. NEW MACHINERY NEEDED — ranked by how many abilities each unlocks

*(Unverified = the call exists in the interface dumps on disk but this mod has never run it; needs one focused test battle before being trusted — consistent with how every other call in the mod was adopted.)*

| Rank | Machinery | Unlocks | Status |
|---|---|---|---|
| 1 | **Enemy targeting**: stop casting everything at self; pass the unit's `current_target()` into `perform_special_ability(key, target)` [11]; decide a "no target → skip" policy. (A true "best enemy" chooser would need to survey the enemy army — `battle_manager:get_scriptunits_for_main_enemy_army_to_local_player()` exists in the dump, `battle_manager.lua` line 40, but surveying enemies is exactly what this project measured as unavailable beyond the current target — treat the chooser as research, the current-target rule as buildable now.) | Groups 2+3 ≈ **1,037 abilities** (in practice those whose unit already has a target) | Call accepts a target today (mod passes self); the readiness gate is target-agnostic. **Small-to-medium job, largest payoff.** |
| 2 | **Ground placement policy + bearing**: when an ability is a "point at the ground" form, pick the point (best-effort: the current target's position if readable, else ahead of the unit along its facing, else own position as today) and pass a real orientation instead of 0°. Direction read `bearing()` exists in the dump (`battle_unit.lua` line 129) *(unverified)*; own positions are measured. | Ground-form half of group 3 plus ground summons/heals ≈ **730 abilities** | Ground cast path **already built** for one ability (cast at own feet, orientation 0 — mod file); needs the point-picking brain. **Medium job.** |
| 3 | **Health read**: `unary_hitpoints()` (dump line 258) and/or `unary_of_men_alive()` (line 236) to gate heals/potions/defensives; needs one test battle to confirm polling behaviour *(unverified)*. `number_of_men_alive()` + the "men at start" read (line 228) gives a men-count proxy for multi-model units at once. | Group 6 ≈ **71 abilities**, plus better quality across heals in every group | One new read; the plumbing is the same per-ability table. **Small job, high player-visible value.** |
| 4 | **Ally picker**: choose which friendly unit receives a friend-targeted cast (closest to the fight? lowest men? wavering?). All input reads exist (own units' positions, men, morale, melee state); distance math from positions works today, `unit_distance()` exists in the dump *(unverified)*. | ≈ **359** friend-plus-ground abilities across groups 1/5/6/7 (198 friend-unit + 161 friend-ground) | Not built. Interim trick: many friend-targeted casts accept the caster itself — one test battle to confirm. **Medium job.** |
| 5 | **Winds-of-magic read**: `battle_army:winds_of_magic_current()` (dump line 64) to reproduce the "pool below 50 → use staff" family and to pace spell casting *(unverified)*. | The ~9 staff/stone items (`augment_spellcasting`, 43 rows total) + spell pacing quality | Not built. **Small job if the call verifies.** |
| 6 | **Army-ability path**: `battle_army:use_special_ability(key, position, bearing, width)` (dump line 127 [12]) for the 204 `source_type = army` abilities — a different UI element (army bar), different targeting. | Up to **204 abilities** | Not built, and not on the unit dial — a design decision, not just code. **Larger job; do last.** |
| 7 | **Enemy detail reads** (their morale/routing, "no enemy is routing", "enemy caster near"): would enable the strict "enemies in range and none routing" family the data mods use [1][2]. | Strictness on group 3, not raw count | **Measured-unavailable.** Do not plan around it. |

**Already built, for the record:** the ground-cast path (one ability), the per-ability targeting-style flag (`ground_keys` set in the mod file), the charge test, the readiness gate and cooldown-hold learning, per-unit/per-ability switches with on-screen badges, and the selection-callback plumbing.

---

## 6. AUTOMOD INSPIRATION — what "Autoactivate" and friends do, and what to borrow

**Autoactivate** — Steam Workshop id `3014120667`, by Autumnchain [1]. A *data-layer* mod: it edits the game's own ability rows so each ability triggers on the engine's shipped condition flags. Last updated **22 August 2026**, 240 subscribers [8]. Its description states the policy plainly: abilities it does not touch are those with limited uses, a miscast downside, no per-frame target update, "some element of proper timing", or that change a unit's movement [1]. Its **pinned thread lists ~239 abilities in seven categories** [2] — counted from the post: in-melee & unbroken (155), charging (14), enemies in range & none routing (22), health low (24, including heal-a-friendly variants), winds of magic ≤ 50 (9), an allied unit routs (6), miscellaneous (9).

**Where it agrees with our grouping:** melee-and-unbroken is the dominant family (155 of ~239) — exactly our group 1; charging is carved out as its own timing (our group 4); health-gated healing is a named family (our group 6 — which it *can* do, because the data layer has `health_below_75%`-style flags we currently cannot read); "unbroken" gating matches our not-routing gate. Its *charging* category also documents a real timing cost: because the trigger starts the cooldown early, its author had to raise the cooldowns of 13 charge abilities after testing [2] — our script mod avoids this by casting the real ability through the real interface.

**Where it disagrees / where we differ:**
- It **omits aimed offensive casts entirely** — no bombardments, vortexes, missiles or ranged hexes appear in its list [2]. A condition flag cannot pick a target or a place; only a script can. Groups 2+3 (≈1,037 abilities) are territory only our approach can touch.
- It bakes the behaviour in and changes balance (cooldowns, and in "Too Many Activatable Skills" the effect strengths are cut to a third [6]). Our mod changes no data and can be switched off per unit in battle.
- Its "enemies in range, none routing" family rests on enemy-state flags (`enemies_in_intercept_range`, `no_enemy_unit_routing_or_broken_within_range` — `flags.tsv`) that our measured vocabulary cannot see. That family stays manual for us.

**Older conditional mods, same lineage:** *Auto Abilities* (Welter, id 3009989710 [3]) puts per-ability triggers on ~55 abilities — Charging / In melee / On cooldown / Health below 75%/50% / Losing melee / Morale wavering. Its author states the approach's ceiling — "we cannot create new conditions, so we must use those that are already in the game" — and its biggest practical wart: N'Kari's and Skarbrand's charging attacks resolve *before* melee contact (a huge-unit animation issue), so no shipped condition fits them [3]. Its companion *Auto Abilities Foe Seeker* [4] turns Foe-Seeker into a passive that switches off below 75% health because "there was no good activation condition for it" [4]. *Auto activation lite* [5] covers item abilities only, and its changelog adds a peer-reviewed fact: the author moved hex/augment item triggers to "when charging" because "when in melee is kinda buggy" and CA changed the "when in range" logic [5]. *Too Many Activatable Skills* (Zach, id 2985359051, updated 2 October 2026, 5,496 subscribers) sidesteps triggers entirely: every activatable becomes a permanently-on passive at one-third strength, a rebuilt version of a 2022 Korean-language original [6][7][8].

**Worth borrowing for our mod:**
1. Autoactivate's seven-category checklist [2] as the mod's default trigger table — it is a curated, community-tested list of which trigger suits which ability; port its assignments into the mod's per-ability table where the trigger is one we can read.
2. Its exclusion policy as default-off: limited-use, miscast-risk, timing-critical and movement abilities stay manual until individually proven [1]. Our table should carry the same "off by default" class.
3. Its heal-ally specifications ("heal nearby friendly units within range that have less than X% health but have not hit the healing cap" [2]) as the exact target spec for our group 6 once the health read verifies.
4. Its two known failure notes as test-case warnings: "when in range" conditions broke when CA changed the logic ([5] — the same risk class as any of our unverified reads), and huge-unit charge timing ([3] — expect it on N'Kari/Skarbrand-class units in our group 4 too).

---

## 7. RECOMMENDED LADDER — build order for "most abilities for the least machinery"

| Step | Build | One-line why | Reach |
|---|---|---|---|
| 1 | **Enemy targeting** — aim group 2 + the unit-form half of group 3 at `current_target()`; skip cleanly when there is none | Biggest single unlock; needs only plumbing, no new reads; the cast call already accepts a target | ≈1,000 abilities become *eligible* (those with a current target) |
| 2 | **Ground placement policy** — point-picking + orientation for the ground form, reusing the existing ground path | Second biggest unlock; the ground form is already proven to fire (Tactician's SYG) | ≈730 abilities |
| 3 | **Health read test-battle, then group 6** — verify `unary_hitpoints`/men-fraction, wire heals/potions to a threshold | The one genuinely new signal with broad, visible value; stops heals firing at full health | 71 + quality across all groups |
| 4 | **Ally picker** — choose the receiver for friend-targeted casts | Unlocks the friend-cast thirds of groups 1/5/6/7; interim self-cast trick cheap to try first | ≈360 receiver slots |
| 5 | **Winds-of-magic read** — pool ≤ 50 trigger for staff/stone items; spell pacing | Small count, cheap if the call verifies | ≈9 + pacing |
| 6 | **Army abilities** — different bar, different call (`battle_army:use_special_ability`) | Real count (204) but a different UI contract and targeting story; decide separately | 204 |
| ∞ | **Keep the default-off class** — limited-use, miscast, pure-timing abilities never auto-fire | Protects the player from wasted panic buttons; same line the community mods drew [1] | — |

**What stays manual forever (say it plainly):** abilities whose trigger lives in enemy state the script cannot see — "no enemy is routing", "an enemy caster is nearby", "the enemy is within range" (the Autoactivate "enemies in range" family [2]) — and things that need *placement judgement* the mod cannot match: a perfect vortex on a clump rather than on one target, panic buttons the player deliberately hoards, and the big-unit charge-timing cases the community already documented [3]. Those are not failures of effort; they are information the engine never hands a script.

**One more honest note on the biggest group.** Group 3's "fire at what you've already targeted" is only as good as the player's orders: a unit standing idle with no orders has no `current_target()`, so its spells will sit unused. Closing that gap means surveying the enemy army — the call exists in the dump but the project has measured enemy detail reads as unavailable beyond the current target, so it must be treated as a research item, not a promise.

---

*All counts in this report were computed from the dump folder's tables on 4 October 2026; ability examples are the database keys themselves, so any claim can be re-checked by searching that key in `unit_spec_abil.tsv`.*

## Sources

[1] https://steamcommunity.com/sharedfiles/filedetails/?id=3014120667 — Steam Workshop: Autoactivate (Autumnchain)
[2] https://steamcommunity.com/workshop/filedetails/discussion/3014120667/3806156528952655037 — Autoactivate pinned thread: List of Abilities
[3] https://steamcommunity.com/sharedfiles/filedetails/?id=3009989710 — Steam Workshop: Auto Abilities (Welter)
[4] https://steamcommunity.com/sharedfiles/filedetails/?id=3012442892 — Steam Workshop: Auto Abilities Foe Seeker
[5] https://steamcommunity.com/sharedfiles/filedetails/?id=2799569408 — Steam Workshop: Auto activation lite
[6] https://steamcommunity.com/sharedfiles/filedetails/?id=2985359051 — Steam Workshop: Too Many Activatable Skills 9.x VANILLA (Zach)
[7] https://steamcommunity.com/sharedfiles/filedetails/?id=2875046977 — Steam Workshop: too many active skills (2022 original)
[8] https://api.steampowered.com/ISteamRemoteStorage/GetPublishedFileDetails/v1 — Steam Web API: GetPublishedFileDetails (update dates, subscribers)
[9] https://raw.githubusercontent.com/Shazbot/WH3-Dump/main/db/unit_special_abilities_tables/data__.tsv — Public mirror: unit_special_abilities table dump
[10] https://chadvandy.github.io/tw_modding_resources/WH3/battle/battle_unit.html — WH3 scripting reference: battle_unit
[11] https://raw.githubusercontent.com/LyciaPintella/Total-War-Warhammer-III-Lua-Library-Documentation/main/battle/battle_unitcontroller.lua — WH3 Lua dump: battle_unitcontroller
[12] https://raw.githubusercontent.com/LyciaPintella/Total-War-Warhammer-III-Lua-Library-Documentation/main/battle/battle_army.lua — WH3 Lua dump: battle_army
