# WH3 — RECOUNT UNDER THE WHEEL-ONLY POLICY

**Measurement round only.** No tracker status was changed, no mod file was touched, nothing was built.
Every number below is produced by joining the 1,797-row inventory in
`docs/WH3_ability_database_master.md` to the game's own tables under
`%LOCALAPPDATA%\Temp\wh3\` (the extraction of `db/` from the WH3-Dump dataset).

Date: 2026-10-17.

---

## 1. The policy being measured

One rule, verbatim, replacing every previous exclusion rule:

> **"Do not implement any ability that is not in the ability wheel (this should cover spells and army
> abilities implicitly). All the rest, I think we can tackle."**

So the numerator question is no longer "can this be automated?" — it is **"is this ability on the unit's
ability bar at all?"**. Everything on the bar is in scope; everything off the bar is out, regardless of how
buildable its trigger is.

---

## 2. Definition of "in the ability wheel"

An ability is **in the wheel** if all three hold:

1. **Carrier** — the engine classifies it as a *unit-carried* ability: `unit_abilities.source_type` ∈
   `{active, bound, lord, character, unit, item, rune, weapon}`. This is the game's own enum for *how an
   ability reaches a unit*, and it is the primary discriminator.
2. **Drawable** — the UI has everything it needs for a button: `unit_abilities.icon_name` non-empty (the
   button art), `unit_abilities.is_hidden_in_ui = false`, and a row in `unit_special_abilities` (so it is a
   real battle ability with phases, not a campaign command).
3. **Not an off-wheel family** — it is none of: a **spell** (`source_type = spell`), a **cataclysm spell**
   (`source_type = cataclysm`), an **army-bar ability** (`source_type = army`), or the quest-battle army
   ability (`source_type = quest`, which also sits in the army registry).

**Off-wheel ⇒ excluded. Everything else ⇒ included.**

### 2.1 Why `source_type` is the carrier test rather than the unit list alone

The obvious test — "referenced by a unit's ability list" — is **incomplete**, and the data proves it:
`land_units_to_unit_abilites_junctions_tables` + `unit_set_unit_ability_junctions_tables` cover only
**597 of the 1,158** included abilities. The other **561** are carried by *items, weapons and equipment*,
which the roster junction does not record: they attach to whichever character wears the item, and the engine
draws them on that unit's bar. The project's own mod is the empirical proof — **300 of the 605 keys the mod
already casts** (`perform_special_ability` from the owning unit) have no roster reference at all
(120 item, 77 weapon, 27 character, 18 lord, 25 bound-spell, 10 rune, 4 unit, 2 hero, 17 other). An ability
a unit can cast is on that unit's bar; the roster junction is simply not the table that records equipment.

So: `source_type` decides the **family**; the roster junction is used as **corroboration**, not as the gate.

### 2.2 Tables and columns actually used

| # | File (`%LOCALAPPDATA%\Temp\wh3\`) | Table | Columns used | What it decides |
|---|---|---|---|---|
| 1 | `unit_abilities.tsv` | `unit_abilities_tables` | `key`, `source_type`, `icon_name`, `is_hidden_in_ui`, `type` | **the carrier family** (the rule) + button art |
| 2 | `unit_spec_abil.tsv` | `unit_special_abilities_tables` | `key`, `passive`, `num_uses`, `special_ability_display`, `target_*` | is it a battle special ability; active vs passive; targeting |
| 3 | `land_abil.tsv` | `land_units_to_unit_abilites_junctions_tables` | `ability`, `land_unit` | roster corroboration (is a unit type issued this ability) |
| 4 | `uset_ability.tsv` | `unit_set_unit_ability_junctions_tables` | `unit_ability`, `unit_set` | roster corroboration via unit sets |
| 5 | `sag_to_abilities.tsv` | `special_ability_groups_to_unit_abilities_junctions_tables` | `special_ability_groups`, `unit_special_abilities` | **spell-side** proof: the ability is a member of a lore group |
| 6 | `army_spec.tsv` | `army_special_abilities_tables` | `army_special_ability`, `unit_special_ability` | **army-side** proof: the ability is an army-bar entry |
| 7 | `army_ab_faction.tsv` | `army_special_abilities_for_faction_junctions_tables` | `army_special_ability`, `faction` | army-side second registry |
| 8 | `phases.tsv` + `phase_junc.tsv` | `special_ability_phases` / junction | `phase_display`, `special_ability` | phase/status icon availability (UI corroboration) |
| 9 | `unit_abilities.loc.tsv` | `unit_abilities__.loc` | `key`, `text` | display names |

`army_spec.tsv` (286 army-bar keys game-wide) and `army_ab_faction.tsv` (374 faction rows) were downloaded
this round from the same dump the rest of the extraction came from; everything else was already on disk.

### 2.3 Ruling per family, with the data that backs it

| `source_type` | In inventory | Verdict | Evidence from the data | Confidence |
|---|---:|---|---|---|
| `active` | 941 | **in** | unit-carried by definition; 512 sit in a roster list, the other 429 are item/weapon/character-granted; 531 already cast by the mod | **high** |
| `bound` | 176 | **in** | bound spells are buttons with a charge count (`num_uses`); 73 are in a roster list; 50 already cast by the mod | **high** |
| `lord` | 10 | **in** | all 10 are battle effect types (hex / vortex / bombardment / dmg), none is a campaign command; 7 in a roster list | **high** |
| `item` | 12 | **in** | item-granted abilities drawn on the bar; 4 already cast by the mod | **high** |
| `rune` | 12 | **in** | Dwarf rune abilities; all 12 are battle effects; 10 already cast by the mod | **high** |
| `character` | 3 | **in** | character battle abilities; 2 in a roster list, 2 cast by the mod | **high** |
| `unit` | 3 | **in** | unit battle abilities; 3 in a roster list | **high** |
| `weapon` | 1 | **in** | weapon-granted (Tyrant's Talon) | **high** |
| `spell` | 418 | **out** | lore-group members (`sag_to_abilities`); cast from the spellbook, not a unit button; all 418 carry status `excluded (spell)` | **high** |
| `cataclysm` | 16 | **out** | cataclysm spells; all 16 sit in `army_special_abilities_tables`; all carry status `excluded (spell)` | **high** |
| `army` | 204 | **out** | army-bar family; 191 in the army registry (the other 13 are endgame-crisis / vortic variants attached elsewhere) | **high** |
| `quest` | 1 | **out** | `wh2_dlc11_quest_battle_supply` is in the army registry — a quest-battle army ability | **high** |

### 2.4 "No campaign-only or lord-only commands in the inventory" — verified

Confirmed. All 1,797 rows are **active battle abilities**: every one has `passive = false` in
`unit_special_abilities`, every one has a non-empty `icon_name`, and **0** have `is_hidden_in_ui = true`.
The 10 `lord` and 3 `character` rows are battle abilities of the `perform_special_ability` kind (hex, vortex,
bombardment, direct damage), not campaign commands. The single `quest` row is a quest-*battle* army ability.
There is no campaign-only contamination in this inventory. (Passive abilities — 1,289 rows in the game's
special-ability table — are out of scope by the tracker's own construction, not by this rule.)

### 2.5 The one judgement call: bound spells

`bound` (176) is kept **in** because a bound spell is drawn as a button on the unit's bar with a limited use
count — that is exactly what the wheel is. The tracker agrees: all 176 carry battle-effect statuses
(vortex, bombardment, no-enemy-read), never `excluded (spell)`, and 50 are already implemented. If the policy
is meant as *"any spell, bound or not, is out"*, add 176 to the exclusions → included 982.

### 2.6 The 19 borderline keys (army registry vs carrier type disagree)

38 inventory keys with a non-army carrier sit somewhere in the army registry. 19 of them have an in-wheel
carrier type, and those are the only ones where the two authorities disagree:

- **16 × `cataclysm_bound_*`** — bound copies of the eight cataclysm spells (`wh3_dlc20_*` and `wh3_dlc27_*`:
  gehennas_golden_globe, thorsens_thunderstorm, magma_storm, ashes_and_dust, dance_of_despair,
  storm_of_renewal, time_amok, merciws_monstrous_regiment). Carrier says `bound` (unit button); key prefix and
  the army registry say cataclysm.
- **3 × `active`** — `wh2_dlc15_character_abilities_wardens_cage`,
  `wh3_dlc29_army_abilities_pestilential_bombardment`, `wh3_main_cataclysm_khorne_greater_gate_of_khorne`.

3 of the 19 are implemented (`wardens_cage`, and `merciws_monstrous_regiment` ×2). They are counted **in**
under the carrier rule and flagged here. If they are pulled out:

| | headline | if the 19 are also excluded |
|---|---:|---:|
| excluded | 639 (35.56%) | 658 (36.62%) |
| included | 1,158 (64.44%) | 1,139 (63.38%) |
| implemented, in wheel | 603 (52.07% of included) | 600 (52.68%) |
| not implemented, in wheel | 555 (47.93% of included) | 539 (47.32%) |

That is a ±19 band on the included figure (1.6%). The headline below uses the carrier rule.

---

## 3. Method

1. **Inventory** parsed from `docs/WH3_ability_database_master.md` §2: every markdown table row whose second
   column is a backticked key → **1,797 rows, 1,797 distinct keys** (matches the master's own §1 total and
   its 1145 + 218 + 434 = 1,797 split).
2. **Implemented set** taken from the mod itself, not the tracker:
   `mod_source/script/battle/mod/zz_test_deadly_onslaught.lua`, `local ABILITIES = { … }` → **579 entries /
   605 distinct keys**, all 605 present in the inventory.
3. **Join** on the exact key string against tables 1–8 in §2.2. All 1,797 keys resolve in `unit_abilities`
   and `unit_special_abilities` (0 misses).
4. **Verdict** applied from `source_type` (§2.3), then counts and percentages computed in code — no figure in
   this document was summed by hand.
5. **Validation** — the independent checks in §8 all pass.

---

## 4. The numbers

Percentages carry their denominator in the row. "of total" = of 1,797; "of included" = of 1,158.

| # | Measure | Absolute | % of total (1,797) | % of included (1,158) |
|---|---|---:|---:|---:|
| 1 | **Total active abilities (the inventory)** | **1,797** | 100.00% | — |
| 2 | **Excluded — not in the ability wheel** | **639** | **35.56%** | — |
| 3 | **Included — in the ability wheel** | **1,158** | **64.44%** | 100.00% |
| 4 | **Implemented among included** | **603** | 33.56% | **52.07%** |
| 5 | **Not implemented among included** | **555** | 30.88% | **47.93%** |
| 6 | Implemented but **outside** the rule (reported separately, §6) | 2 | 0.11% | 0.17% |
| 7 | All implemented in the mod (4 + 6) | 605 | 33.67% | 52.25% |

**The headline the user asked for:** of **1,158** abilities that are actually on the ability wheel, **603 are
implemented (52.07%)** and **555 are not (47.93%)**. Two more implemented abilities sit outside the rule and
are neither counted as progress under it nor hidden.

### 4.1 Included, by carrier family

| `source_type` | Included | % of total | % of included | Implemented | % of that family |
|---|---:|---:|---:|---:|---:|
| `active` | 941 | 52.37% | 81.26% | 531 | 56.43% |
| `bound` | 176 | 9.79% | 15.20% | 50 | 28.41% |
| `rune` | 12 | 0.67% | 1.04% | 10 | 83.33% |
| `item` | 12 | 0.67% | 1.04% | 4 | 33.33% |
| `lord` | 10 | 0.56% | 0.86% | 5 | 50.00% |
| `character` | 3 | 0.17% | 0.26% | 2 | 66.67% |
| `unit` | 3 | 0.17% | 0.26% | 1 | 33.33% |
| `weapon` | 1 | 0.06% | 0.09% | 0 | 0.00% |
| **Total** | **1,158** | **64.44%** | **100.00%** | **603** | **52.07%** |

---

## 5. Family breakdown of the 639 exclusions

| Family | Keys | % of total (1,797) | % of excluded (639) | How identified |
|---|---:|---:|---:|---|
| **Spells** (`source_type = spell`) | **418** | 23.26% | 65.41% | lore-group members in `special_ability_groups_to_unit_abilities_junctions` |
| **Army-bar abilities** (`source_type = army`) | **204** | 11.35% | 31.92% | `army_special_abilities_tables` / `army_special_abilities_for_faction_junctions` (191 in-registry) |
| **Cataclysm spells** (`source_type = cataclysm`) | **16** | 0.89% | 2.50% | all 16 are army-bar entries; 8 spells × base + `_com` |
| **Quest-battle army ability** (`source_type = quest`) | **1** | 0.06% | 0.16% | `wh2_dlc11_quest_battle_supply`, in the army registry |
| **Total excluded** | **639** | **35.56%** | 100.00% | |

4 families → 2 real ones: **spells & cataclysms = 434 (67.92% of exclusions)** and
**army-bar (incl. the quest ability) = 205 (32.08% of exclusions)**.

Status of the 639 today: 619 were excluded, 18 skipped, **2 implemented** (§6).

---

## 6. Implemented but OUTSIDE the new rule — by name

Only two, and both are the same family. They are in the mod, they work, and the new policy says they should
not have been built. Listing them honestly rather than folding them into either count:

| Ability | Key | Family | Mod entry | Tracker status |
|---|---|---|---|---|
| **Meat Feast** | `wh3_main_prisoners_butcher` | army-bar | `marker = "butcher"` | `skipped (army-bar ability)` — **stale**: it is in the mod |
| **Massacre** | `wh3_main_prisoners_massacre` | army-bar | `marker = "massacre"` | `implemented (in-melee self)` |

Notes:
- These are the only 2 of the mod's 605 keys that sit outside the wheel. **No spell is implemented** — the
  new policy orphans no spell work at all.
- They also resolve the 605-vs-604 discrepancy in the master DB: 604 rows carry an `implemented` status, but
  the mod holds 605 keys. The extra one is Meat Feast, whose status still says `skipped`.
- A third key in the same Ogre family, `wh3_main_prisoners_dismember` (Dismember), is **not** in the mod and
  stays excluded.
- Recommendation for the next round (not done here): either delete these two entries from the mod or record a
  written exception. Leaving them in while the policy says "wheel only" is an unrecorded contradiction.

---

## 7. What the new policy re-opens

**555 abilities** that the old rules excluded are inside the wheel and are now in scope — that is
**47.93% of the included set**. (Every not-implemented included row is, by definition, one the old rules had
shut.)

Cross-referenced against `docs/WH3_exclusion_rules_review.md`, which split the 1,192 non-implemented rows into
**281 re-openable now / 583 policy / 328 still sound**:

| Review bucket | Total in bucket | Now **inside** the wheel (re-opened) | Now **outside** the wheel (stay shut) |
|---|---:|---:|---:|
| **281 — "re-openable now"** | 281 | **235** | 46 |
| **583 — "policy call"** | 583 | **32** | 551 |
| **328 — "still sound"** | 328 | **288** | 40 |
| **Total** | **1,192** | **555** | **637** |

The mapping reproduces all three review subtotals **exactly** (235+46 = 281, 32+551 = 583, 288+40 = 328),
which is the strongest check that the join and the bucket logic agree with the review's own arithmetic.

What this means in practice:

- **The 281 "re-openable now" list shrinks to 235 rows that are actually on the wheel.** 46 of them were
  spells or army abilities whose exclusion had been attributed to an effect rule (bombardment, explosive,
  no-enemy-read) before the carrier rule ever ran — they are now out by policy and their refuted
  justifications no longer matter.
- **Of the 583 "policy call" bucket, 551 (spells 434 + army-bar 117) are now out by rule**, so that
  judgement is settled — no re-asking needed. The remaining **32 re-open immediately**: revisit 15,
  spawned/ranged 10, flanking/ambush 7.
- **The whole 328 "still sound" bucket is dissolved**: 288 of them are on the wheel, and the old reasons
  (vortex, summons, breath/cone, own-troop-damage, stealth, transform, movement, mutual exclusivity,
  drawback, rampage, explicit FF, magic scope) were all "cannot automate safely" arguments, which this
  policy explicitly replaces with "can we reach it on the bar?".
- **One counting correction worth carrying forward:** the review's "army-bar 117" was a *rule-attribution*
  count, not the family size. The army family in the inventory is **204**, because 85 army rows had been
  attributed to an effect rule (vortex 31, bombardment 28, placed 11, no-enemy-unit-read 6,
  own-troop-damage 5, breath/cone 2, stealth/escape 2) before the army rule was reached, and 1 was
  implemented. Spells (434) did match exactly. This is why the wheel rule excludes
  639, not 551.

---

## 8. Validation checks (all passed)

| Check | Result |
|---|---|
| Inventory rows = distinct keys | 1,797 = 1,797 |
| Inventory = master DB §1 total | 1,797 = 1,797 |
| Every key resolves in `unit_abilities` and `unit_special_abilities` | 1,797 / 1,797, 0 misses |
| Mod `ABILITIES` keys all present in the inventory | 605 / 605 |
| Mod entries vs keys | 579 entries → 605 keys (matches the master DB) |
| Sum of the four exclusion families | 418 + 204 + 16 + 1 = 639 |
| Included + excluded | 1,158 + 639 = 1,797 |
| Implemented in + implemented out | 603 + 2 = 605 = the whole mod |
| Not implemented in + implemented in | 555 + 603 = 1,158 |
| Every inventory row drawable | `icon_name` non-empty 1,797/1,797; `is_hidden_in_ui = true` 0/1,797 |
| Every inventory row an *active* ability | `passive = false` 1,797/1,797; phase/status icon present on 1,001 |
| Review buckets reproduced | 281 / 583 / 328 exact |

---

## 9. Caveats, stated plainly

1. **Bound spells are counted in** (§2.5). If "spells" means all spells including bound, the included figure
   drops to 982 and the excluded rises to 815.
2. **The 19-key edge band** (§2.6) would move included to 1,139 if those keys are treated as cataclysm/army.
   The carrier rule puts them in.
3. **`source_type` is the engine's classification, not a guarantee of a visible button.** For a handful of
   abilities the button only appears once a unit is issued the granting item; the inventory is keyed by
   ability, not by carrier, so "on the wheel" means "has a wheel slot on at least one unit in at least one
   configuration". That is the only definition that can be applied to a 1,797-key list without enumerating
   every unit × item combination.
4. **Passive abilities are not in the inventory** (1,289 in the game's table), so the wheel-only policy says
   nothing about them. If the user later wants passives, that is a separate measure.
5. The two implemented army abilities (§6) are a real policy contradiction in the current mod, not a
   measurement artefact.
