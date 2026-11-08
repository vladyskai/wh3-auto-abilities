# WARHAMMER III — Auto-Ability Tracker (every active ability, status & proposed activation)

**MASTER REFERENCE (2026-10-16):** `docs/WH3_ability_database_master.md` is the definitive
database of every ability (1,797 rows: name, key(s), real game-data EFFECT, RESTRICTION flag
names, RANGE + the 70% trigger bound, STATUS, plain-English trigger). This tracker stays the
authoritative *inventory*; the database is generated from it plus a fresh extraction of the
game's own tables, and is regenerated with `tools/build_ability_database.py`.

**How this file is used (the workflow).** This is the master tracker for the auto-ability mod's expansion.
The plan: (1) a *questionnaire per ability* is produced from this file — each shows the ability's own game text,
its keys, its owners, and the one-line **proposed auto-activation**; (2) the user decides ability by ability
(approve / amend / reject, free-text alternatives welcome); (3) only after approval is the batch implemented in
`WH3_mod/mod_source` and field-tested. Nothing below is implemented unless it says `implemented`.

**Update 2026-10-04:** Block 1 shipped — the 28 approved abilities are now `implemented (in-melee self)` (harness82: 1861 checks).

**Update 2026-10-04 (block 2):** Block 2 shipped — the 27 approved simple abilities are now `implemented (in-melee self)` (they reuse the block-1 shared evaluator), plus the five new trigger types ship with their own evaluators and distinct reasons: **Eagle-Feather Torc** (barrier broken), **Fangspike** (charge window OR in melee), the **summoned Foe-Seeker** (a third key on the existing Foe-Seeker entry), **Ghoul King of Ushoran** (own health <= 75% with hysteresis), and **Glorious Death** (the first ally-targeting ability). Key correction: the real key is `wh2_dlc11_lord_abilities_dreaded_duelist` (single l), not the double-l tracker typo. Harness83: 1962 checks green.

**Update 2026-10-05 (field-test follow-up — two corrections + field-test status):** the block-2 field test produced two corrections, both implemented and shipped (harness84: 2039 checks green):
- **Glorious Death** — the candidate set is **SLAYER UNITS ONLY** (not "any friendly unit"). It fires when a Slayer unit is in melee: a Slayer **ally** is preferred (the lowest-health one); otherwise the **owner itself** casts on self only if the owner is a Slayer and in melee; otherwise silent. A **non-Slayer ally is never targeted** (the old any-in-melee-ally fallback is removed). "Slayer" is decided by a list of **land_units type keys derived from the game's own data** (`land_units.loc.tsv`: every unit key whose own key contains `slayer`/`doomseeker`, exact whole-key equality only — e.g. `wh_main_dwf_inf_slayers`, `wh2_dlc10_dwf_inf_giant_slayers`, `wh3_dlc25_dwf_cha_daemon_slayer`, `wh3_dlc25_dwf_inf_doomseekers`).
- **Ghoul King of Ushoran** — the 80%-re-arm **hysteresis is REMOVED** (a unit under sustained damage may never climb back above 80%, which would disarm the trigger for good); the rule is plain own health ≤ 75%, limited only by the readiness gate + the engine cooldown + the rejection-informed back-off.

**Field-test status of block 2 (read the entries below).** Only **Glorious Death** could be field-tested (the user owns that DLC and fielded it); it was tested and its trigger was corrected above. The entries marked `pending test (DLC unavailable)` are implemented but need a hero/item the user cannot field in skirmish-vs-AI (the user named **Fangspike** and **Eagle-Feather Torc** as item-gated). Entries marked `pending test (not yet field-tested)` are implemented but were not reached in the test battle (ownership of the needed DLC is not assumed). **All of these remain implemented and shipping** — they are awaiting a test opportunity, not unimplemented.

**Update 2026-10-05 (block 3 — melee questionnaire):** Block 3 decided — 31 items `approved (in-melee self)`, 3 approved with the combined charge-or-melee trigger `approved (charge and in-melee)` (`wh2_dlc11_lord_abilities_heart_piercing`, `wh_dlc03_item_abilities_horn_of_the_first_beast`, `wh3_dlc26_weapon_abilities_morglor_the_mangler` — mirroring Fangspike), 2 `skipped (revisit)` and 4 rejected. Decisions recorded inline (§2 entries and §3a rows) and in §6. A new status, `approved (charge and in-melee)`, is now in the legend — 3 items so far.

**Update 2026-10-08 (block 4 — melee questionnaire):** Block 4 decided — **36 approved in all: 33 `approved (in-melee self)` + 3 `approved (charge and in-melee)`** (Star Lance, Storm Rage, Stormlance). Also 2 `skipped (revisit)` (Seductive Glory, Seismic Snare), 1 `excluded (magic scope)` (Sword of Teclis), 2 skipped as unsuitable at collection time (charge-only Silver Horn of Vengeance; movement/vortex Swiftness of Itzl), and the earlier “duplicate” call on **Quickblood** corrected to `approved (in-melee self)` (its key differs from block 3's Lightning Reflexes — see §7). Decisions recorded inline (§2 entries and §3a rows) and in §7.
**Update 2026-10-08 (block 5 — melee questionnaire + trivial auto-accept correction):** Block 5 (tracker items §2 #174–#213; 40 items examined) is collected and partly decided. The trivial self-buff **auto-accept rule was corrected** (standing rule 9): **imbuements and attributes no longer block auto-acceptance**. The user's correction, about **The Eternal Blade**: “Yes, and should have been accepted from the beginning as I said. Please do not show me the trivial ones like this.” Re-filtering the block-5 candidates against the **real game-data phases** now auto-accepts **12 further items** — Sword of Torgald, The Black Axe of Krell, The Black Cleaver, The Blessed Blade of Ptra, The Dragon's Fang, The Eternal Blade, The Mace of Helsturm, The Rotaxes, The Slayer Sword, The Talabecland Runefang, The Tenderiser, Tombstrike — all marked `approved (in-melee self - auto, trivial)`, joining the 2 already auto-accepted at collection time (The Ostland Runefang, The Sword of Lyonesse). The other **23 candidates stay in the questionnaire** (§8).

**Update 2026-10-08 (block 4/5/6 IMPLEMENTATION ROUND — harness88):** the whole approved-but-unimplemented backlog is now **implemented and shipping**. **Blocks 4 and 5** contributed **74 approved entries** (54 `in-melee self` + 15 `in-melee self - auto, trivial` + 5 `charge and in-melee`); **block 6** contributed the **11 auto-accepted trivial self-buffs** (standing rule 9) plus the **two NEW trigger types the user just designed**: **Will of the Verminking** (`verminking_wavering` — an ally in range is in melee and wavering; cast on self; the Glorious-Death safety pattern) and **Potion of Toughness** (`melee_health75` — in melee at ≤ 75% health, a one-time heal). **87 new entries** in all; the abilities table grows **102 → 189 entries (108 → 195 keys)**. **Army-bar abilities** became a **standing exclusion** (rule 10) — Oath of Replenishment (base + upgraded) and Shanty: First/Second Verse (+ `_ai` twins) are marked `skipped (army-bar ability)`. Every ability implemented in this round is marked `implemented (...)` below and in §3a. Harness88: **2293 checks, 0 failures**; red control vs the pre-edit snapshot: 2264 checks, 77 failures — all documented count pins + the new section.

**Update 2026-10-09 (block 8 Enchanted Metallurgy IMPLEMENTATION ROUND — harness89):** the four **Enchanted Metallurgy** abilities (`wh3_main_character_abilities_enchanted_metallurgy` + `_flaming` + `_piercing` + `_poison`) are now **implemented and shipping** on the NEW trigger `metallurgy_melee` — fire when the **owner is in melee OR any friendly unit other than the caster is in melee within the conservative 25 m `FOURTH.METALLURGY_RANGE_M`** (game-data 35 m ally aura, `unit_spec_abil.tsv effect_range 35.0000`); **cast on self**; the Glorious-Death / Verminking safety pattern (closest ally, pre-cast gap re-check, skip on drift). **The user's SHOOTING half ("when ally in range is shooting") COULD NOT be built:** the API research is complete — the battle-script API (`battle_unit.lua`) exposes **NO per-unit is-firing / is-shooting read** (`is_under_missile_attack` is the unit *RECEIVING* fire; `current_target` / `ammo_left` / `missile_range` prove nothing about firing NOW; `battle_manager:get_num_units_under_fire` is battle-level and defensive; the `flags.tsv` vocabulary — `is_missile_unit`, `is_under_missile_fire`, `cannot_perform_missile_attack` — is a data-table construct, not a Lua read), so **no proxy was invented**. The four **Master of Alchemy** abilities (same trigger request) stay `approved` (not yet implemented). The abilities table grows **189 → 193 entries (195 → 199 keys)**; no new chunk locals. Harness89: **2369 checks, 0 failures**; red control vs the pre-edit (189-entry) snapshot: **2339 checks, 56 failures** — all documented table-size pins + the new section.

**Update 2026-10-09 (blocks 7-9 IMPLEMENTATION ROUND — harness90):** the whole approved-but-unimplemented backlog is now **implemented and shipping**. Derived programmatically from §3a: **69 further entry-groups / 73 keys** — the 73 rows carrying an `approved (…)` status (of which the 4 Enchanted Metallurgy rows were already shipped and are **skipped idempotently**), plus the two backlog `redesigned` abilities #36 Commanding Presence and #46 Dazh's Song of Winter Sunlight (2 keys) and the one `pending review` #32 Chanson of Caging. **FIVE NEW triggers** ship, each its own evaluator: **charge_only** (Ferocious Battle Howl — the charge window WITHOUT the melee arm), **wavering_self** (the owner wavering, fail-closed; Ferocious Fury of Ulric, Helm of Yvresse, Vial of Troll Blood), **wavering_self_or_ally** (owner wavering OR an in-melee wavering ally within the conservative 25 m `FOURTH.WAVERING_RANGE_M`, the game-data 35 m aura; Fury of Ulric + the redesigned Commanding Presence), **charge_or_wavering** (Bangers & Smash) and **wavering_ally_range** ("Stay Here, I'll Get Help!" — a wavering ally in range with **NO ally-melee requirement**: the Verminking shape minus its melee gate). The redesigned **Dazh's Song** (#46) rides the EXISTING `tired` trigger; the four **Master of Alchemy** abilities ship the **melee self-or-ally half** on the existing `metallurgy_melee` (the shooting half stays proven-unbuildable). Every new trigger **casts on self** with the pre-cast gap re-check / drift skip. The abilities table grows **193 → 262 entries (199 → 272 keys)**; no new chunk locals (all state/constants ride the `FOURTH` bag). Harness90: **2486 checks, 0 failures**; red control vs the pre-edit (193-entry) snapshot: **2455 checks, 94 failures** — all documented grown-table pins + the new HARNESS-90 section. Every ability implemented in this round is marked `implemented (...)` below and in §3a.

**Legend — Status column:**
- `implemented` — in the mod today, field-verified (the five abilities in §1).
- `proposed` — not yet implemented; carries a proposed activation. Melee candidates are detailed in §2.
- `proposed (FF)` — has friendly-fire potential (area damage that can catch your own troops): moved to the
  very end of the list (§3b) and off-by-default until its friendly-fire behaviour is proven in a test battle.
- `excluded (spell)` — spells / winds-of-magic / cataclysm abilities: out of scope by the user's earlier standing decision (§3c).
- `approved (in-melee self)` — user-approved in the questionnaire; implement with the stated activation (when in melee and not fleeing, cast on self).
- `approved (charge and in-melee)` — user-approved in the questionnaire with the combined trigger (the charge window OR in melee, and not fleeing): cast on self — mirrors Fangspike (§2 #68 / §5); 14 items so far (3 in block 3, 3 in block 4, 2 in block 5, 2 in block 8 — **Cash Cascade**, **Birona's Timewarp** — and 4 in block 9 — **Fury of Khaine**, **Inspired Assault I/II/III**).
- `approved (charge only)` — user-approved with a **charge-window-only** trigger (no melee arm): activate in the split second before impact, cast on self; 1 item so far (**Ferocious Battle Howl**, block 7).
- `approved (wavering self)` — user-approved with a **wavering** trigger: cast on self only while the owner is wavering; 3 items so far (**Vial of Troll Blood**, **Ferocious Fury of Ulric**, block 7; **Helm of Yvresse**, block 9).
- `approved (wavering self-or-ally in range)` — user-approved with a **wavering** trigger that also watches an ally: cast on self when the owner **or an ally in range** is wavering; 1 item so far (**Fury of Ulric**, block 7).
- `approved (charge or wavering)` — user-approved with a **combined** trigger: activate in the charge window **OR** when wavering, cast on self; 1 item so far (**Bangers & Smash**, block 8).
- `approved (melee self-or-ally / shooting ally in range)` — user-approved with a **two-part** trigger (the Alchemy buffs): in melee, cast on the owner **or an ally in range** (**self-or-ally**); OR, when an ally in range is **shooting**, cast on that ally (**shooting ally**). 8 items so far (the four **Enchanted Metallurgy** abilities and the four **Master of Alchemy** abilities, block 8; shorthand: `approved (melee self-or-ally / shooting ally)`). **The shooting half was RESEARCHED and is NOT buildable (harness89): the battle-script API exposes no per-unit is-firing / is-shooting read, so no proxy is used** — the four **Enchanted Metallurgy** abilities ship the **melee self-or-ally half** only (the four **Master of Alchemy** abilities remain unimplemented).
- `approved (wavering ally in range)` — user-approved with a **wavering** trigger that watches an ally: cast on an ally **in range** while that ally is wavering (the **owner need not be wavering, and the ally need not be in melee**); same evaluator shape as **Will of the Verminking** (closest ally in range, conservative range, drift re-check); 1 item so far (**"Stay Here, I'll Get Help!"**, block 8).
- `approved (health<=75, no melee gate)` — user-approved with a **health-only** trigger: cast on self when the owner's health is at or below **75%**, with **no melee requirement**. Same health-only evaluator family as the Ghoul King of Ushoran redesign (no melee gate); 5 items so far (**Ghoul King of Ushoran**, **Star of Avelorn**, **Gulyas**, **Mantra of Invigoration**, **Meat Feast**).
- `approved (in melee and health<=75)` — user-approved with a **combined melee+health** trigger (the Potion-of-Toughness pattern, `melee_health75`): cast on self when the owner is **in melee AND at or below 75% health**. Distinct from the health-only `approved (health<=75, no melee gate)` shape: used where the ability **also grants the owner/allies a resistance or other melee-relevant effect**, so the melee gate is meaningful (the pure heals Star of Avelorn/Gulyas take the health-only gate); 1 item so far (**Captain of the Phoenix Guard**, block 9).
- `approved (in-melee self - auto, trivial)` — **auto-accepted without the questionnaire** (standing rule 9): self-cast and the only positive effects are Melee Attack / Melee Defence / Weapon Strength / Splash Attack Power, after ignoring imbuements and attributes. Implement with the standard in-melee self activation; 15 items so far.
- `rejected (<reason>)` — user-rejected in the questionnaire; no automatic logic — left to the player (reasons so far: `friendly fire`, `drawback`, `mutual exclusivity`, `rampage`, `stealth/escape effect`; quoted where decided).
- `pending review` — user tentatively approved but flagged for review; not yet implemented — revisit before implementing.
- `redesigned` — user-approved with a different trigger than the melee default (see the item's decision note); implement with the stated redesigned activation.
- `pending test (DLC unavailable)` — implemented, but the ability needs a hero/item from a DLC the user does not own, so it cannot be fielded in skirmish-vs-AI; awaiting a test opportunity.
- `pending test (not yet field-tested)` — implemented, but not reached/verified in a field battle yet (ownership of the needed DLC is not assumed); awaiting a test opportunity.
- `skipped (not achievable)` — user-approved in principle but not achievable with current engine hooks; no automatic logic (see §5).
- `skipped (revisit)` — user chose to skip the item for now (not a rejection); revisit in a later questionnaire block.
- `implemented (verminking_wavering)` / `implemented (melee_health75)` — implemented with a **user-designed non-melee trigger** (see the entry's own decision note): **Will of the Verminking** (fire when an ally in range is in melee and wavering; cast on self) and **Potion of Toughness** (in melee at ≤ 75% health).
- `implemented (charge only)` / `implemented (wavering self)` / `implemented (wavering self-or-ally in range)` / `implemented (charge or wavering)` / `implemented (wavering ally in range)` / `implemented (metallurgy_melee)` / `implemented (tired)` — the block-7-9 implemented triggers (harness90): charge-only (no melee arm), wavering-self, wavering self-or-ally (owner or an in-melee wavering ally in range), charge-or-wavering, wavering-ally-in-range (no ally-melee requirement), the melee self-or-ally half of the Alchemy buffs, and Dazh's Song's existing tired trigger.
- `skipped (army-bar ability)` — the ability belongs to the ARMY BAR rather than a unit's own dial (its game key carries `army_abilities`); excluded by **standing rule 10** (see §10). Superseded for the two removed entries by the status below.
- `excluded (not in wheel: army ability - removed from mod per user decision 2026-10-17)` — the ability WAS implemented but sits outside the single in-wheel rule (army-bar); it has been **REMOVED from the mod's `ABILITIES` table** per the user's decision of 2026-10-17 (**Meat Feast**, **Massacre**; see §10.2).
- `excluded (not in wheel: boss-only unit)` — the ability's **ONLY grant path is a `_boss` unit** (a quest-battle boss variant: no player can recruit it, equip it, learn it from a skill tree or spend a rite on it), so it can never appear on a player unit's wheel. The five that were implemented were **REMOVED from the mod's `ABILITIES` table**; the other ten never shipped (see **§10.3**).

**Standing acceptance rules for future questionnaires (set with the user):**
1. **No friendly fire:** any ability with friendly-fire potential gets NO automatic logic (reconfirms the original scope rule).
2. **No meaningful drawback:** any ability with a meaningful drawback / trade-off (a stat penalty, a self-risk) is left to the player — rejected for automation.
3. **Mutual exclusivity:** any ability that is mutually exclusive with another is left to the player — rejected for automation.
4. **No loss of control:** any ability with a loss-of-control effect (Rampage) is left to the player — rejected for automation. (see rule 7 — Rampage is now decided case by case, not auto-rejected)
5. **Tactical escape effects:** an ability whose value is a tactical escape (disengage / reposition) is left to the player — rejected for automation.
6. **Per-ability M/A badges:** risky abilities can still be automated with the default M badge. The user reopens old rejects later, case by case; old rejects stay rejected for now and are marked `rejected pending reconsideration` when reopened.
7. **Rampage is no longer an automatic rejection:** a loss-of-control / Rampage effect is flagged and decided case by case (Fluid Injection! and Fury of Ursun were approved with it).
8. **Mutual exclusivity is an automatic rejection:** an ability the collection finds mutually exclusive with another is auto-rejected WITHOUT asking the user case by case, and is marked `rejected (auto: mutual exclusivity)` (this is the standing form of rule 3).
9. **Trivial self-buff auto-accept (corrected 2026-10-08; Splash Attack Power added 2026-10-08, block 5):** a self-cast ability is **auto-accepted WITHOUT being shown in the questionnaire** iff its only **POSITIVE** effects are **Melee Attack, Melee Defence, Weapon Strength (base and/or armour-piercing) and/or Splash Attack Power**. **Imbuements** (Flaming Attacks, Magical Attacks, Sundered Armour, Poison!, Blinded!, Disembowelled!, Weakened, Flammable!, Corroded Armour, Discouraged!, Legbiter, Inevitable End!, …) and **attributes** (Executioner, Strider, Can Cause Fear/Terror, Immune to Psychology, Charge Reflection, …) are **IGNORED** for this test — they neither qualify nor disqualify. It **still stays a question** if the ability has any of: a charge bonus, leadership/morale, a resistance, a vigour change, a heal, **rampage** (an attribute, but explicitly non-trivial), any negative value, any direct-damage/area component, any ally-or-area targeting beyond self-cast, or any other non-MA/MD/WS/Splash stat. Auto-accepted items are marked `approved (in-melee self - auto, trivial)` and implemented with the standard in-melee self activation, without asking. (Replaces the pre-correction form of the rule, which wrongly required a *pure* self cast and rejected any attribute/imbuement.)
10. **Army-bar abilities are excluded (standing, set 2026-10-08 with the user):** any ability carried by the **ARMY BAR** rather than a unit's own dial is left out entirely — user: **“Skip all army bar abilities.”** Such items are marked `skipped (army-bar ability)` and get **NO automatic logic**. The collection **exclusion filter gains an `army-bar` keyword**: any key whose database prefix carries `army_abilities` (or whose owners note reads “army-bar ability (no unit junction)”) is **EXCLUDED from every future questionnaire block**. This extends the earlier exclusions (`spell` / winds-of-magic / cataclysm keys, §3c).
11. **(R1) Positive-only buffs auto-accept, by effect family (widened 2026-10-09):** a self-only or ally-only buff with **no negative and no friendly-fire component** is **auto-accepted without the questionnaire**. Trigger by family: **melee attack / melee defence / weapon damage (base or AP) / armour / leadership / physical-or-damage resistance / ward / missile resistance / Expert Charge Defence / Immune to Flanking / Immune to Psychology** → `in-melee self`; **heal-over-time / hit-point replenish** with no melee part → `health<=75` (no melee gate); **heal + armour or melee-defence** → `in melee AND health<=75`; **Unbreakable / Cannot Die / Stubborn / Hold the Line** → `wavering self` (or `wavering self-or-ally` when the text reaches allies in range); **charge bonus / charge speed / mass / impact damage** → `charge and in-melee`. Auto-accepted items are marked `approved (auto: <trigger>)`.
12. **(R2) Enemy debuffs auto-accept (widened 2026-10-09):** effects applied **to enemies in range** — a negative melee attack / defence / leadership / armour / resistance / speed, i.e. the **Hex** families — are **auto-accepted as `in-melee self`**; the user has consistently approved these before.
13. **(R3) Unsuitable families auto-exclude (widened 2026-10-09):** **vortex**, **bombardment**, **explosive**, **summon** (unless already handled), **pure movement / speed-only with no combat effect**, **healing of enemies**, **abilities that target the ground only**, and anything whose **effect text is empty/unknown after one genuine sourcing attempt**. Auto-excluded items are marked `excluded (auto: <reason>)` and get **no automatic logic**.
14. **(R4) Flag for the user — do not auto-decide (widened 2026-10-09):** **applies Rampage**, **damages or kills friendly units** (friendly fire, **including the FF rows**), **mutually exclusive** abilities, **army-bar** abilities, **stealth / escape / stalk / unspottable** effects, **transform / shapechange**, abilities that need a **live enemy-unit read we do not have**, and anything whose net effect is **ambiguous or mixed positive-and-negative**. Flagged rows keep the status `proposed` / `proposed (FF)` so they still surface.
15. **(R5) THE STANDING 70% RANGE RULE (set 2026-10-10, ruled ABSOLUTE):** **every trigger-range constant MUST be AT MOST 70% of the ability's REAL game-data range, rounded DOWN to a whole metre** — i.e. `trigger range = floor(0.70 × real range)`. The real range is the ability's own `unit_spec_abil.tsv` `effect_range` when it has an aura, else its `target_intercept_range` (the reach the engine uses to walk the caster). The user's words: **"for abilities that include a range, we should always specify 70% of the actual range to avoid such things"** — and, ruling the rule absolute, **"...No exceptions."** The symptom it removes: the caster **WALKING** toward a target that sat inside the ability's own reach but outside a comfortable cast range (field-reported on **Accusation** — the Witch Hunter moved). The rule ships in code as **`FOURTH.RANGE_FRACTION = 0.70`**, and the build asserts every constant equals `floor(real × 0.70)`. **Applied values (harness 95):** GLORIOUS DEATH **55→38**, VERMINKING **35→24**, METALLURGY **35→24**, WAVERING **35→24**, BLOOD SACRIFICE **100→70**, EAT DA RUNTS **100→70**, ACCUSATION **75→52**. **No constant is exempt** — the old field-tuned 25 m Glorious Death gate was **replaced by 38 m** at the user's direction. The charge-window pair `CHARGE_MIN_DISTANCE_M` / `CHARGE_MAX_DISTANCE_M` are **not** ability ranges (they gate the charge order's run-up) and are left unchanged.

**Strategy groups** (from the research report `WH3_ability_strategy_report.md`, all 1,797 castables):
`melee_self` = self/ally combat buffs as the fight starts · `melee_enemy` = melee debuffs on the enemy you are fighting ·
`charge` = fire in the split second before impact · `morale` = when morale hits the wavering line ·
`degraded` = heals/panic when health or men drop · `ready` = no readable condition, fire when allowed ·
`target` = ranged offense at what the unit already targets.

**Counts (reconcile):** all castable/active abilities = 1,797 = 9 implemented keys (5 abilities, §1) + 1,136 normal
(includes the 530 melee-candidate keys / 491 items in §2) + 434 spells & cataclysms (§3c) + 218 friendly-fire-flagged (§3b).

**Data sources:** per-ability fields from the game dump `%LOCALAPPDATA%\Temp\wh3\` (`unit_spec_abil.tsv`, `unit_abilities.tsv`,
`land_abil.tsv`, `grouped2.json` = report grouping); names/descriptions are the game's own localisation, mirror
`Shazbot/WH3-Dump` @8a4f7e6 `text/db/unit_abilities__.loc.tsv` (plus land_units / character_skills / ancillaries / initiatives loc).
Descriptions quoted below are each ability's real in-game tooltip text (trimmed only if longer than 3 sentences).

---

**Update 2026-10-10 (harness 97 — the rest of Class A: enemy-targeted abilities):** the 97 remaining Class-A entries from `WH3_audit_report.md` (98 total; **Accusation** was already done and is the template) now fire at the ENEMY on the PROVEN Accusation mechanism. **88** ride the existing `enemy_engaged_or_shot` trigger (enemy-UNIT hexes); **9** ride a NEW `enemy_ground_area` trigger (enemy-GROUND area hexes) that casts through `perform_special_ability_ground(key, ENEMY_POSITION, 0, 0)` on the chosen enemy's ground. Every entry carries its own REAL `target_intercept_range` (`range_real`, from `unit_spec_abil.tsv`) mapped at load to ONE named 70% constant per real range (`FOURTH.ENEMY_CAST_R<real>`, 12 constants, `floor(real*0.70)`); the offer test is `unit:unit_distance(enemy) <= that constant` ONLY — never the engine's `unit_in_range`. The chosen enemy is the CAST TARGET (never the owner); fresh handles, the in-melee-preferred trigger, the pre-cast re-check and the hold are the Accusation ones; the log prints the REAL distance. `melee_unwavering` 480 -> 383; the table stays 579 entries / 605 keys. Harness 97: 3075 checks green (red control: 77 designed failures, 27/54 worlds). Installed pack md5 `f42ed662ce42fee8a570593346cca4e6`.

**Update 2026-10-14 (Class B IMPLEMENTATION ROUND - harness98):** the audit's **Class B** (ally-targeted effects cast on self; **34 entries**) was derived programmatically from `WH3_audit_report.md` and joined to the mod table and `unit_spec_abil.tsv`. Outcome: **17 implemented** on the mod's OWN ally picker (the `blood_sacrifice` / `eat_da_runts` shape) across **four new ally families** - `ally_melee_buff` 11 (Da Boss 'as a Plan!, Favour of the Fay, Helping Hand, Inspired Assault I/II/III, Inspired Defence I/II/III, Orcs are da Best!, Hellish Vigour), `ally_heal` 3 (Elvish Healing Herbs, Patch Up, Revivification Crystal), `ally_heal_melee` 1 (Captain of the Phoenix Guard), `ally_wavering` 2 (Shock Collar, Where You Goin!?) - plus **1** (`Stay Here, I'll Get Help!`) whose ally pick already shipped and which now gains the CAST TARGET and its own 70% bound; **1 SKIPPED as an ARMY-BAR ability** (Meat Feast, standing rule 10); and **15 left for a ruling** (rule-14 Rampage / drawback flags, unavailable target-class gates, or an undefined real range). Every implemented entry carries its OWN real `target_intercept_range` (`ally_range_real`) -> ONE named 70% constant per real range (5 constants: `FOURTH.ALLY_CAST_R50`=35, `R60`=42, `R75`=52, `R100`=70, `R150`=105, `floor(real*0.70)`); the offer test is `unit:unit_distance(ally)` <= that constant ONLY - **never** the engine's `unit_in_range` - and the cast goes through the **fresh-handle** route (the caster controller AND the chosen ally re-enumerated the SAME tick). `melee_unwavering` 383 -> 373, `charge_or_melee` 29 -> 26, `ushoran_health` 41 -> 38, `melee_health75` 2 -> 1; entries/keys unchanged (579 / 605). Harness98: **3186 checks, 0 failures**; red control vs the pre-edit snapshot: 3153 checks, 85 failures, 13/32 Class-B world results passing by design (all documented re-based pins).

**Update 2026-10-15 (TARGET-CLASS-GATED CLASS-B ROUND - harness99):** the **15** entries the Class-B round left tagged NEEDS A RULING were ruled and are now **ALL IMPLEMENTED as ally-targeted casts** on the mod's own ally picker. **10** are **TARGET-CLASS-GATED** - each must cast on an ALLY of a required class, whose key list is **DERIVED FROM THE GAME'S OWN DATA** (exact whole-key equality, the Glorious- Death method): `overseer_of_the_unseen` -> non-commander / non-large (**918** keys: `land_units.class` != "com" AND `battle_entities.size` not large/very_large), `whiplash` -> beast (**55**: `main_units.caste` == "war_beast"), `iron_hand_captain` -> morale BROKEN (`MoraleState` == "broken"), `inspired_marksmanship_i/ii/iii` -> missile-capable (**493**: `land_units.primary_missile_weapon` non-empty), `makaissons_persuader` -> war machine (**68**: `main_units.caste` == "warmachine"), `reforge` -> Hell-Forged (**13**: the `hellforged` unit attribute), `remouldered` -> monster (**235**: `main_units.caste` == "monster"), `restore` -> construct (**29**: the `construct` unit attribute). **2** are the **RAMPAGE** pair (`fury_of_khaine`, `verminous_fury`) - implemented on the plain in-melee ally buff family (the M/A badge is the opt-in). **1** - **Merciw's Monstrous Regiment** - is an ally-targeted cast with **NO distance bound** (INFINITE RANGE per the wiki; `target_intercept_range` = -1.0). **2** were ruled **mid-flight** this round and are included: **Daemonic Whispers** (plain ally buff, real 200 m) and **Grut's Sickle** (real 100 m, but its PICK RULE is the ally with the **HIGHEST ABSOLUTE HIT POINTS REMAINING**, max `HealthValue` - the recipient pays a health cost for the winds recharge). The offer test is the per-ability 70% constant ONLY - **never** the engine's `unit_in_range`; the cast goes through the **fresh-handle** route; the chosen ally is ALWAYS the cast target (never the owner). `melee_unwavering` 373 -> 363, `charge_or_melee` 26 -> 25, `ushoran_health` 38 -> 34; `ally_melee_buff` 11 -> 14; 10 new ally triggers; `ally_range_real` 18 -> 32; a new `FOURTH.ALLY_CAST_R200` = 140. Entries/keys unchanged (579 / 605). Harness99: **3365 checks, 0 failures**; red control vs the pre-edit snapshot: 3332 checks, the round's RED CONTROL passes 26/56 world results by design.

**Update 2026-10-17 (harness 100 — THE SINGLE IN-WHEEL RULE: the two implemented army abilities are REMOVED).** **Meat Feast** (`wh3_main_prisoners_butcher`) and **Massacre** (`wh3_main_prisoners_massacre`) were the only two implemented keys sitting **outside** the new single rule (*"Do not implement any ability that is not in the ability wheel …"*, `docs/WH3_recount_wheel_only.md` §1) — both are **army-bar** abilities. Per the user's instruction they are **REMOVED from the mod's `ABILITIES` table**; the table is now **577 entries / 603 keys** (was 579 / 605), `melee_unwavering` 362, `ushoran_health` 33. Nothing else was touched - in particular **Grut's Sickle stays** (a different, in-wheel item ability). Their §3a rows now read `excluded (not in wheel: army ability - removed from mod per user decision 2026-10-17)`. Full record: **§10.2**. Spreadsheet: `docs/WH3_abilities_master_v2_2026-10-17.xlsx` (v2 supersedes v1).

**Update 2026-10-17 (harness 101 — BOSS-ONLY EXCLUSION + GATE OF KHORNE).** **A. Boss-only exclusion.** Every ACTIVE ability whose only grant path is a `_boss` unit is excluded: **15** in-wheel keys were verified from the grant junctions (`land_abil.tsv`, `uset_ability.tsv`, the `sag_to_abilities`+`sag_to_units` pair and `army_ab_faction.tsv` - none of them has any other grant). **5 were implemented and are REMOVED from the mod**: Greater Faith Bastion, Bitter Sting, Frenzied Challenge, Visions of Madness, Guttural Roar; the other **10** never shipped and stay absent. The table is now **573 entries / 599 keys** (was 577 / 603); `melee_unwavering` **360**, `enemy_engaged_or_shot` **86**. **B. Gate of Khorne** (`wh3_main_character_abilities_gate_of_khorne`) is **IMPLEMENTED** on the user's trigger, verbatim: *"The trigger will place it on the closest enemy that is in range of the ability and fighting."* — a new `enemy_ground_melee` trigger: among enemies within the ability's own 70% bound (**35 m** of the 50 m cast range) keep those **FIGHTING (in melee)**, pick the **CLOSEST**, and place the summon on **THAT ENEMY'S ground** via `perform_special_ability_ground(key, enemy_pos, 0, 0)` with a fresh caster controller and a fresh enemy, a hold, a pre-cast re-check, and its own reason string naming the enemy type and the real distance — never the caster's position, and no `unit_in_range`. Full record: **§10.3**. Spreadsheet: `docs/WH3_abilities_master_v3_2026-10-17.xlsx` (v3 supersedes v2; v1 and v2 are unchanged).

**Update 2026-10-17 (harness 102 — THE SUMMON ROUND).** **A. The rest of the summon class.** Every in-wheel, non-illusion, **GROUND-CASTABLE** `wh_type_summon_unit` row (derived from the game's own data: `spawned_unit` set + type `wh_type_summon_unit` + `spawn_is_decoy` false + `target_ground` true + in-wheel + not boss-only + not already implemented) is now **implemented on the proven `enemy_ground_melee` trigger** — the closest FIGHTING enemy inside the ability's own 70% bound, the summon placed on THAT ENEMY's ground: **57 entries / 68 keys**. Exactly **one** row of the label set cannot take a ground point — **Nurgling Tide** (no target flags at all, `affect_self` = true, range 0) — and it is the one self-target summon (B). One A entry (The Tallyman's Blades Upgraded) declares `target_intercept_range` = -1.0, so it carries `unbounded = true` and has no 70% bound to take. **B. Nurgling Tide** rides a NEW `self_summon_melee` trigger — the user's rule, verbatim: *"that one should only trigger when the caster himself is in melee."* Owner alive + not routing + `is_in_melee()`, cast on SELF through the unit form with a freshly re-fetched caster controller, a hold and a pre-cast re-check of the same state; NO range bound (a self cast has no distance to measure). **C. The four illusions are EXCLUDED** — `excluded (not in wheel: illusion summon)`, reason *illusion (spawn_is_decoy; refused when engaged in melee)*: Call of the Shadow Dancer, Deceiving Shadows, Doppelgang, Mislead. None was ever in the mod, so nothing had to be removed. **D. The nine unlabelled real spawners** are implemented on the same trigger: Beast Pack, Blacktoof's Conjuration, Call to Gwindalor, Lesser Raise Dead, Savage Dominion, Savage Predators, Tide of Death, Tide of Pox, Wake Da Idol (9 entries / 9 keys). **E. Eye of Khorne** is a FINISHER on a NEW `enemy_low_health_noncommander` trigger: any enemy inside its 70% bound (35 m of 50 m) BELOW 20% health that is NOT a Lord or Hero; the lowest-health one wins (closest as the tiebreak), cast through the UNIT form. The Lord/Hero test is a REAL READ — a derived commander-class key set from the game's own `land_units.class` = "com" ∪ `main_units.caste` ∈ {lord, hero}, matched by exact whole-key equality against `battle_unit:type()`, with `battle_unit:unit_class()` == "com" as the fallback and a FAIL-CLOSED default. **F. The Dreaded Thirteenth** (four keys, one entry) rides a NEW `enemy_melee_noncommander` trigger: the closest non-commander enemy in melee inside its 70% bound (70 m of 100 m), placed on its ground. **Counts:** ABILITIES **573 -> 642 entries** (573 + 69), **599 -> 682 keys** (599 + 83); `melee_unwavering` stays **360**, `enemy_engaged_or_shot` stays **86**, `enemy_ground_area` stays **9**; `enemy_ground_melee` **1 -> 67**; the new `self_summon_melee` / `enemy_low_health_noncommander` / `enemy_melee_noncommander` each **1**. Full record: **§10.4**. Spreadsheet: `docs/WH3_abilities_master_v4_2026-10-17.xlsx` (v4 supersedes v3; v1-v3 unchanged).

**Update 2026-10-10 (annotated copy):** `WH3_auto_ability_annotated.lua` carries the same change (the per-ability bound, the shared picker, the enemy-ground evaluator/helper/key-set) — log-free / find-free, as always.

## 1. Implemented today (field-verified)

| # | Ability | Keys it covers today | Trigger (as built) |
|---|---|---|---|
| 1 | **Deadly Onslaught** (`marker: onslaught`) | `wh_main_character_abilities_deadly_onslaught` | charge window OR in melee (field-verified) |
| 2 | **Foe-Seeker** (`marker: foe_seeker`) | `wh_main_character_abilities_foe_seeker`; `wh_dlc03_character_abilities_foe_seeker` | fatigue Tired or worse, fail-closed; fires up to 3x when an ability carries no text (field-verified) |
| 3 | **Hammer of Sigmar** (`marker: hammer_of_sigmar`) | `wh_main_spell_bound_hammer_of_sigmar`; `wh_dlc04_spell_bound_hammer_of_sigmar_upgraded` | in melee, not routing (field-verified) |
| 4 | **Stand Your Ground** (`marker: stand_your_ground`) | `wh_main_character_abilities_stand_your_ground`; `wh3_dlc24_character_abilities_tacticians_stand_your_ground` | in melee + morale at/below wavering, fail-open (field-verified) |
| 5 | **Blood Lust** (`marker: blood_lust`) | `wh_main_character_abilities_blood_lust`; `wh_dlc03_character_abilities_blood_lust` | in melee, morale not wavering, fail-open; self-cast (field-verified) |

*All five: arm-first semantics (abilities fire only for units the player armed); engine readiness gate used
before every cast; badges shown on the unit dial; field-verified in battle.*

---

## 2. MELEE CANDIDATES — the ordered questionnaire list (excl. the five; 487 abilities)

Ordered **simplest / least-risky first**, then progressively more complex:
Tier 1 self-targeted (no targeting step) → Tier 2 self-or-ally → Tier 3 ground-at-own-feet →
Tier 4 ally-targeted (picker) → Tier 5 enemy-unit-targeted → Tier 6 enemy-ground.
Within a tier: no wind-up first, then no limited uses, then alphabetical. Each item carries: the game's own
tooltip text (source-marked), the exact key(s), the owning units/lores, and the one-line proposed activation
the questionnaire will offer. `key` order: base first, upgraded/summoned twins after.


### Tier 1 — self-targeted, no targeting step (304 items)

**1. Acid Burps** — *melee_self, self*
- Keys: `wh3_dlc26_unit_abilities_acid_vomit`
- Game text: “A copious natural by-product of this noisome Colossal Squig's healthy digestion. Just don't step in it.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc26_unit_abilities_acid_vomit`)*
- Owners: Da Acid Burpa (Colossal Squig)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 120s · 14s · self

**2. Acidic Musk Glands** — *melee_enemy, self*
- Keys: `wh2_dlc16_unit_abilities_acidic_musk_glands`
- Game text: “A sudden discharge of highly-concentrated acid douses everyone nearby, melting away armour and burning skin.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc16_unit_abilities_acidic_musk_glands`)*
- Owners: not unit-innate (granted by character skill)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **rejected (friendly fire)** — user reason: “no automatic logic for now, potential for friendly fire”
- Run stats: cd 60s · 19s · self

**3. Aether Sword** — *melee_self, self*
- Keys: `wh3_dlc20_weapon_abilities_aether_sword`
- Game text: “An enchanted blade instils a certain magical 'wallop' to its bearer's attacks.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc20_weapon_abilities_aether_sword`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — auto-activate when in melee and not fleeing, cast on self.
- Run stats: cd 90s · 27s · self

**4. All-Consuming Hatred** — *melee_enemy, self*
- Keys: `wh3_dlc27_unit_abilities_consuming_hatred`
- Game text: “The innate hatred carried within a Preyton makes it despise itself almost as much as its foes, whose attacks are repaid with added enmity.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc27_unit_abilities_consuming_hatred`)*
- Owners: Bloodthirsty Preyton, Scourge of Arden (Preyton), Preyton
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **rejected (drawback)** — user reason: “serious drawback (Melee Defence -12); player should decide”
- Run stats: cd 120s · 25s · self

**5. Apocalyptic Charge** — *melee_self, self*
- Keys: `wh_pro04_unit_abilities_apocalyptic_charge`
- Game text: “If you see him coming run as fast as you can… not that it will do you any good whatsoever!” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh_pro04_unit_abilities_apocalyptic_charge`)*
- Owners: Swords of Chaos (Chaos Knights)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 120s · 30s · self

**6. Apocalyptic Vision** — *melee_self, self*
- Keys: `wh_dlc03_character_abilities_apocalyptic_vision`
- Game text: “In fitful dreams, he sees the end... The world collapsing in on itself, leaving nothing but ashes and aberration.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh_dlc03_character_abilities_apocalyptic_vision`)*
- Owners: Beastlord, Khazrak the One-Eye
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — auto-activate when in melee and not fleeing, cast on self.
- Run stats: cd 90s · 18s · self

**7. Arcane Hymn** — *melee_self, self*
- Keys: `wh3_cp1_character_abilities_magic_prayer`
- Game text: “In hissed arcane melody, the Clawspeaker masterfully binds the Winds into a single, obedient stream.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_cp1_character_abilities_magic_prayer`)*
- Owners: Clawspeaker (Shadows)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 120s · 27s · self

**8. Armour of Gazrakh** — *melee_self, self*
- Keys: `wh3_dlc23_item_abilities_armour_of_gazrakh`
- Game text: “The sheer quality of this fine armour makes it able to withstand blows of any power, regardless of who is making them.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc23_item_abilities_armour_of_gazrakh`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — auto-activate when in melee and not fleeing, cast on self.
- Run stats: cd 120s · 48s · self

**9. Armour of the Barrows** — *melee_enemy, self*
- Keys: `wh3_dlc29_item_abilities_armour_of_the_burrows`
- Game text: “Strengthened by the passage of the ages, this Chaos plate's aura of entropy also has the power to decay the magic of enemy weapons.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc29_item_abilities_armour_of_the_burrows`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 120s · 27s · self · item

**10. Arsebelcher** — *melee_self, self*
- Keys: `wh3_main_character_abilities_arsebelcher`
- Game text: “Ogre diets are notoriously protein-heavy, ensuring their farts are less than fragrant! As you might expect, the enemy are not best pleased.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_character_abilities_arsebelcher`)*
- Owners: Tyrant
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 120s · 4s · self · character

**11. Aura of Quetzl** — *melee_self, self*
- Keys: `wh2_main_item_abilities_aura_of_quetzl`
- Game text: “This string of beaded shells, feathers and bones is a charm that surrounds the warrior in a miasma of colour.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_main_item_abilities_aura_of_quetzl`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — auto-activate when in melee and not fleeing, cast on self.
- Run stats: cd 90s · 25s · self

**12. Axe of Dargo** — *melee_self, self*
- Keys: `wh_main_weapon_abilities_axe_of_dargo`
- Game text: “The Axe of Dargo, a runic weapon of monstrous size, is tempered with dragon's blood and iron-oaths of vengeance.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh_main_weapon_abilities_axe_of_dargo`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — auto-activate when in melee and not fleeing, cast on self.
- Run stats: cd 120s · 29s · self

**13. Axe of Grom** — *melee_self, self*
- Keys: `wh2_dlc15_weapon_abilities_axe_of_grom`
- Game text: “Grom’s axe doubles as a can-opener of sorts, prying open a foe’s armour to make mince meat of 'em!” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc15_weapon_abilities_axe_of_grom`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — auto-activate when in melee and not fleeing, cast on self.
- Run stats: cd 120s · 29s · self

**14. Axes of Kadrin** — *melee_self, self*
- Keys: `wh3_dlc25_weapon_abilities_axes_of_kadrin`
- Game text: “Chained to Garagrim's wrists so he will never lose them, these twin axes are inscribed with powerful runes, augmenting their wielder's natural strength.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc25_weapon_abilities_axes_of_kadrin`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — auto-activate when in melee and not fleeing, cast on self.
- Run stats: cd 120s · 21s · self

**15. Azhag's 'Ard Armour** — *melee_self, self*
- Keys: `wh2_dlc15_item_abilities_azhags_ard_armour`
- Game text: “By the grace of Gork (or Mork), Azhag’s magical armour is so ‘ard, it can even protect those around him.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc15_item_abilities_azhags_ard_armour`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — auto-activate when in melee and not fleeing, cast on self.
- Run stats: cd 120s · 38s · self

**16. Ballet of Blows** — *melee_self, self*
- Keys: `wh3_main_lord_abilities_ballet_of_blows`
- Game text: “The finest combat is beautiful to behold, like the precision choreography of the most complex of dances – each delicious move bringing the Exalted Keeper of Secrets closer to the killing climax.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_lord_abilities_ballet_of_blows`)*
- Owners: Exalted Keeper of Secrets (Shadows), Exalted Keeper of Secrets (Slaanesh)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — auto-activate when in melee and not fleeing, cast on self.
- Run stats: cd 90s · 45s · self

**17. Barbed-Knuckle Boxing** — *melee_self, self*
- Keys: `wh2_dlc17_lord_abilities_barbed_knuckle_boxing`
- Game text: “A brutally simple weapon makes the Doombull’s incredible punching power more than enough to puncture armour and cause dreadful injury.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc17_lord_abilities_barbed_knuckle_boxing`)*
- Owners: Doombull
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 90s · 29s · self

**18. Bastion of the Great Cities** — *melee_self, self*
- Keys: `wh3_dlc24_unit_abilities_bastion_of_the_great_cities`
- Game text: “A steady beat symbolises the staunch defences of the Bastion, a bulwark through which no enemy shall break.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc24_unit_abilities_bastion_of_the_great_cities`)*
- Owners: The Jade War Drum (Zhangu War Drum), Zhangu War Drum
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **rejected (auto: mutual exclusivity)** — user reason: mutual exclusivity; no automatic logic — player decides.
- Run stats: cd 30s · -1s · self

**19. Bear Fang Talisman** — *melee_self, self*
- Keys: `wh3_dlc27_item_abilities_bear_fang_talisman`
- Game text: “This ancient, yellowed canine tooth is the sacred talisman of lordship among Beorg’s tribe, warding off blows that would otherwise harm its wearer.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc27_item_abilities_bear_fang_talisman`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — auto-activate when in melee and not fleeing, cast on self.
- Run stats: cd 90s · 25s · self

**20. Beastslaver** — *melee_self, self*
- Keys: `wh2_dlc14_lord_abilities_beastslaver`
- Game text: “Beastmasters share their minions’ belligerence, cutting down foemen with lash, spear, and harpoon before claiming their twitching bodies as fodder.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc14_lord_abilities_beastslaver`)*
- Owners: High Beastmaster, Rakarth
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — auto-activate when in melee and not fleeing, cast on self.
- Run stats: cd 60s · 34s · self

**21. Blade of Bel-Korhadris** — *melee_self, self*
- Keys: `wh2_main_item_abilities_blade_of_bel_korhadris`
- Game text: “The sword of the beloved Scholar-King is a renowned wyrm-slayer.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_main_item_abilities_blade_of_bel_korhadris`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — auto-activate when in melee and not fleeing, cast on self.
- Run stats: cd 90s · 38s · self

**22. Blades of Shang-Yang** — *melee_self, self*
- Keys: `wh3_cp1_weapon_abilities_blades_of_shang_yang`
- Game text: “Instilled with a measure of the Iron Dragon's own power, the White Tiger's katara burn eternally with strange alchemical fire.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_cp1_weapon_abilities_blades_of_shang_yang`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — auto-activate when in melee and not fleeing, cast on self.
- Run stats: cd 120s · 32s · self

**23. Blood-Forged Armour** — *melee_self, self*
- Keys: `wh2_dlc15_item_abilities_blood_forged_armour`
- Game text: “The cooling of this armour in the blood of Dwarf Runesmiths has imbued it with great powers – some explosive in nature!” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc15_item_abilities_blood_forged_armour`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 30s · 12s · self

**24. Bloodbeast** — *melee_self, self*
- Keys: `wh2_dlc17_lord_abilities_bloodbeast`
- Game text: “Seized by hyperviolent visions, the Bloodbeast spasms and shakes in a violent thrashing of fiery convulsions.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc17_lord_abilities_bloodbeast`)*
- Owners: Taurox the Brass Bull
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 90s · 6s · self

**25. Bloodstorm** — *melee_self, self*
- Keys: `wh2_dlc14_lord_abilities_bloodstorm`
- Game text: “Tz’arkan’s evil is a reflection of Malus’ hate; each gives them strength and always threatens to bubble over in devastating fashion.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc14_lord_abilities_bloodstorm`)*
- Owners: Malus Darkblade (Tz'arkan)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 60s · 9s · self

**26. Bloodstorm Blades** — *melee_self, self*
- Keys: `wh3_dlc26_weapon_abilities_bloodstorm_blades`
- Game text: “Only the strong have a chance of withstanding Skarr's Bloodstorm Blades. From his blood-dimmed point of view, none fall under that category.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc26_weapon_abilities_bloodstorm_blades`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — auto-activate when in melee and not fleeing, cast on self.
- Run stats: cd 120s · 35s · self

**27. Blooood!** — *melee_self, self*
- Keys: `wh_main_unit_abilities_blooood`
- Game text: “The Hellcannon breaks its chains and rushes forwards. Increased movement speed.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh_main_unit_abilities_blooood`)*
- Owners: Hellcannon, The Soul of Damnation (Hellcannon)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 60s · 18s · self

**28. Brass Body** — *melee_self, self*
- Keys: `wh2_dlc17_lord_abilities_brass_body`
- Game text: “Invoking the Dark Masters who endowed his gift, Taurox’s brazen skin temporarily hardens even further to an impossible rigidity.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc17_lord_abilities_brass_body`)*
- Owners: Taurox the Brass Bull
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — auto-activate when in melee and not fleeing, cast on self.
- Run stats: cd 120s · 41s · self

**29. Burp of Grom** — *melee_self, self*
- Keys: `wh2_dlc15_character_abilities_burp_of_grom_0` · `wh2_dlc15_character_abilities_burp_of_grom_1` · `wh2_dlc15_character_abilities_burp_of_grom_2`
- Game text: “Copious amounts of food constantly bubbles and brews in Grom’s astringent stomach bile, causing horrendous and explosive belching that he can barely control.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc15_character_abilities_burp_of_grom_0`)*
- Owners: not unit-innate (granted by character skill)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 60s · 17s · self

**30. Call for Power** — *melee_self, self*
- Keys: `wh3_main_daemon_head_abilities_call_for_power`
- Game text: “Having implored the Ruinous Powers to imbue him with the inexorable, raw power of Chaos, the Daemon Prince attacks with even greater vigour than before.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_daemon_head_abilities_call_for_power`)*
- Owners: Daemon Prince, Red Ulgor, Prince of Slaughter, Grand Vomitus, Prince of Buboes, Caress, the Darkling Prince, Zarrivyk, Feathered-Prince (+4 more)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **rejected (rampage)** — user reason: Rampage! (loss of control); no automatic logic — player decides.
- Run stats: cd 120s · 30s · self

**31. Change or Die!** — *melee_self, self*
- Keys: `wh3_dlc24_character_abilities_change_or_die`
- Game text: “Tzeentchian tyrants and Lords, whose word is law, ensure their troops will not run by issuing this dread order.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc24_character_abilities_change_or_die`)*
- Owners: Chaos Lord of Tzeentch
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — auto-activate when in melee and not fleeing, cast on self.
- Run stats: cd 90s · 22s · self

**32. Chanson of Caging** — *melee_self, self*
- Keys: `wh3_dlc27_lord_abilities_chanson_of_caging`
- Game text: “A tantalising snippet of a song no one else can hear... An enticing movement just out of the corner of one eye… What was I meant to be doing, again?...” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc27_lord_abilities_chanson_of_caging`)*
- Owners: The Masque of Slaanesh
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **pending review** — user: “Makes sense, but could be better. Let's say Yes for now but pending for review.”
- Run stats: cd 20s · -1s · self · lord

**33. Claws of Mourkain** — *melee_self, self*
- Keys: `wh2_dlc11_lord_abilities_claws_of_mourkain`
- Game text: “From deep within the Marshes of Madness, the Strigoi shall rise again!” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc11_lord_abilities_claws_of_mourkain`)*
- Owners: Strigoi Vampire Lord
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — auto-activate when in melee and not fleeing, cast on self.
- Run stats: cd 120s · 34s · self

**34. Cloak of Mists & Shadows** — *melee_self, self*
- Keys: `wh_main_item_abilities_cloak_of_mists_and_shadows`
- Game text: “Kemmler is surrounded by a dark cloak that swirls and twists with a life of its own.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh_main_item_abilities_cloak_of_mists_and_shadows`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — auto-activate when in melee and not fleeing, cast on self.
- Run stats: cd 120s · 29s · self

**35. Coat in Blood** — *melee_self, self*
- Keys: `wh3_dlc29_hero_abilities_coat_in_blood`
- Game text: “Behind the iron discipline of the Grand Master, rages a desire to coat the world in blood!” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc29_hero_abilities_coat_in_blood`)*
- Owners: not unit-innate (granted by character skill)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — auto-activate when in melee and not fleeing, cast on self.
- Run stats: cd 90s · 17s · self

**36. Commanding Presence** — *melee_self, self*
- Keys: `wh3_dlc29_lord_active_commanding_presence`
- Game text: “The presence itself is enough, the orders an afterthought – for this commander has seen it all and knows what needs to be done.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc29_lord_active_commanding_presence`)*
- Owners: Seneschal of the White Wolf
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **redesigned** — user: “Not related to melee, only to morale. The trigger should be when lord or nearby unit are wavering.”
- Run stats: cd 60s · 20s · self

**37. Creature-Killer** — *melee_self, self*
- Keys: `wh2_dlc16_weapon_abilities_creature_killer`
- Game text: “Throt’s modified things-catcher makes him an expert throttler, but allows him to excel at throttling things much larger than man-sized!” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc16_weapon_abilities_creature_killer`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — auto-activate when in melee and not fleeing, cast on self.
- Run stats: cd 120s · 38s · self

**38. Da Great 'Un Iz 'Ere!** — *melee_self, self*
- Keys: `wh2_dlc15_lord_abilities_da_great_un_iz_ere`
- Game text: “Grom is a veritable symbol of greatness, his prodigious size rivalling even the greatest Orcs, and his ambition to conquer outweighing them all.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc15_lord_abilities_da_great_un_iz_ere`)*
- Owners: Grom the Paunch
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — auto-activate when in melee and not fleeing, cast on self.
- Run stats: cd 90s · 21s · self

**39. Daemonblade** — *melee_self, self*
- Keys: `wh3_dlc20_weapon_abilities_daemonblade`
- Game text: “Fashioned by Slaanesh himself, Azazel's devilish sword strikes with a hellish force that even enchanted armour simply cannot deflect.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc20_weapon_abilities_daemonblade`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — auto-activate when in melee and not fleeing, cast on self.
- Run stats: cd 120s · 32s · self

**40. Daemonshield** — *melee_self, self*
- Keys: `wh3_dlc20_item_abilities_daemonshield`
- Game text: “Ever since the Daemon Prince Locephax angered the Gorequeen, his horned head and hypnotic eyes have adorned her shield.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc20_item_abilities_daemonshield`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — auto-activate when in melee and not fleeing, cast on self.
- Run stats: cd 120s · 13s · self

**41. Dagger of Malice** — *melee_self, self*
- Keys: `wh3_dlc23_weapon_abilities_dagger_of_malice`
- Game text: “This blade whispers thoughts of murder and violence to any that grasp its hilt, and remains gleaming, no matter how much bloody work it has done.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc23_weapon_abilities_dagger_of_malice`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — auto-activate when in melee and not fleeing, cast on self.
- Run stats: cd 120s · 17s · self

**42. Daggerdance** — *melee_self, self*
- Keys: `wh3_dlc27_lord_abilities_daggerdance`
- Game text: “A hypnotising gyre of flashing blades too fast to follow, denying any desperate attack and inspiring Dechala's followers to feats of battlefield grace to win their mistress' favour.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc27_lord_abilities_daggerdance`)*
- Owners: Dechala, the Denied One
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **rejected (drawback)** — user reason: drawbacks; no automatic logic — player decides.
- Run stats: cd 30s · -1s · self

**43. Dance of Destruction** — *melee_self, self*
- Keys: `wh3_dlc27_lord_abilities_dance_of_destruction`
- Game text: “Battle provides the stage to please one’s master, where sensuous movements and the eerie whistling of whirling blades entrances followers into heedless destruction.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc27_lord_abilities_dance_of_destruction`)*
- Owners: Dechala, the Denied One
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **rejected (drawback)** — user reason: drawback; no automatic logic — player decides.
- Run stats: cd 30s · -1s · self

**44. Dark Protection** — *melee_self, self*
- Keys: `wh2_dlc11_lord_abilities_dark_protection`
- Game text: “"If you need the strength, then turn to me…"” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc11_lord_abilities_dark_protection`)*
- Owners: Necrarch Vampire Lord
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — auto-activate when in melee and not fleeing, cast on self.
- Run stats: cd 90s · 30s · self

**45. Darkwalker** — *melee_self, self*
- Keys: `wh3_dlc25_lord_abilities_darkwalker`
- Game text: “It is hard to hit one that walks between worlds, straddling the line between life and death.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc25_lord_abilities_darkwalker`)*
- Owners: Elspeth von Draken
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — auto-activate when in melee and not fleeing, cast on self.
- Run stats: cd 120s · 30s · self

**46. Dazh's Song of Winter Sunlight** — *melee_self, self*
- Keys: `wh3_main_character_abilities_dazs_song_of_winter_sunlight` · `wh3_twa06_unit_abilities_dazs_song_of_winter_sunlight`
- Game text: “"Death is like a winter chill; No door can keep it from us; And summer yet may bloom again; Though ice be all upon us."” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_character_abilities_dazs_song_of_winter_sunlight`)*
- Owners: Kostaltyn, Patriarch, Dazh's Hearth-Blades (Tzar Guard – Great Weapons)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **redesigned** — user: “Ideally vigor based, not melee based. Activate when Tired.”
- Run stats: cd 90s · 10s · self

**47. Deathbringer** — *melee_self, self*
- Keys: `wh3_main_lord_abilities_deathbringer` · `wh3_main_lord_abilities_deathbringer_upgraded`
- Game text: “Cutting harder and deeper with each and every blow, this blade ensures that the blood of Kharneth's enemies flows like a river across the battlefield.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_lord_abilities_deathbringer`)*
- Owners: Daemon Prince of Khorne, Daemon Prince, Red Ulgor, Prince of Slaughter, Grand Vomitus, Prince of Buboes, Caress, the Darkling Prince (+6 more)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — auto-activate when in melee and not fleeing, cast on self.
- Run stats: cd 90s · 29s · self

**48. Desertstrike** — *melee_self, self*
- Keys: `wh2_dlc09_character_abilities_strike_of_nehekhara`
- Game text: “Beware the scorpion's sting, hidden 'neath the desert sands yet always poised to strike.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc09_character_abilities_strike_of_nehekhara`)*
- Owners: not unit-innate (granted by character skill)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — auto-activate when in melee and not fleeing, cast on self.
- Run stats: cd 120s · 23s · self

**49. Dinner Bell** — *melee_self, self*
- Keys: `wh3_dlc26_character_abilities_dinner_bell`
- Game text: “When the bell sounds, it's snack time for the assembled host. Then, the carnage can begin again, on a full stomach, with all of the associated drawbacks!” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc26_character_abilities_dinner_bell`)*
- Owners: not unit-innate (granted by character skill)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **rejected (drawback)** — user reason: drawback (30% miscast); no automatic logic — player decides.
- Run stats: cd 90s · 55s · self

**50. Disdain of the Dragon Emperor** — *melee_self, self*
- Keys: `wh3_dlc24_unit_abilities_disdain_of_the_dragon_emperor`
- Game text: “Urged on by the pounding of drums, the Cathayan warriors fight untouched by fear, unleashing the fury of the Dragon on their foes.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc24_unit_abilities_disdain_of_the_dragon_emperor`)*
- Owners: The Jade War Drum (Zhangu War Drum), Zhangu War Drum
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **rejected (auto: mutual exclusivity)** — user reason: mutual exclusivity; no automatic logic — player decides.
- Run stats: cd 30s · -1s · self

**51. Dolorous Blade** — *melee_self, self*
- Keys: `wh_dlc07_hero_abilities_dolorous_blade`
- Game text: “Glowing with an uncanny light, each stroke of this sword effortlessly carves the foe clean through.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh_dlc07_hero_abilities_dolorous_blade`)*
- Owners: The Green Knight
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **pending test (not yet field-tested)** — implemented (in-melee self); the block-2 field test could not reach it (no DLC ownership assumed) — awaiting a test opportunity.
- Run stats: cd 120s · 33s · self

**52. Dragon Spear** — *melee_self, self*
- Keys: `wh2_dlc16_weapon_abilities_dragon_spear`
- Game text: “A sharpened claw at this spear’s tip is impelled by the rage of the ancient Forest Dragon to whom it once belonged.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc16_weapon_abilities_dragon_spear`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **pending test (not yet field-tested)** — implemented (in-melee self); the block-2 field test could not reach it (no DLC ownership assumed) — awaiting a test opportunity.
- Run stats: cd 120s · 25s · self

**53. Dreaded Duellist** — *melee_self, self*
- Keys: `wh2_dlc11_lord_abilities_dreaded_duelist`
- Game text: “"There are but a few who've faced 'im and lived to tell the tale - you can count them on the fingers of Bernard's 'ands… and 'e's got no 'ands."” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc11_lord_abilities_dreaded_duelist`)*
- Owners: Lokhir Fellheart
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **pending test (not yet field-tested)** — implemented (in-melee self); the block-2 field test could not reach it (no DLC ownership assumed) — awaiting a test opportunity.
- Run stats: cd 60s · 22s · self

**54. Dwarf Gouger** — *melee_self, self*
- Keys: `wh2_main_weapon_abilities_dwarf_gouger`
- Game text: “A weapon created to kill the Dwarf-things, it perfectly suits Queek’s furious windmill style of attack.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_main_weapon_abilities_dwarf_gouger`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **pending test (not yet field-tested)** — implemented (in-melee self); the block-2 field test could not reach it (no DLC ownership assumed) — awaiting a test opportunity.
- Run stats: cd 120s · 36s · self

**55. Eagle-Feather Torc** — *melee_self, self*
- Keys: `wh3_dlc27_item_abilities_eagle_feather_torc`
- Game text: “It is said the feathers of eagles bear the magic of the Eagle God himself, providing special boons and protection to those deemed worthy.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc27_item_abilities_eagle_feather_torc`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **redesigned** — user: “Condition should be when barrier is broken” · **pending test (DLC unavailable)** — the torc is a DLC27 item the user cannot field.
- Run stats: cd 120s · 10s · self

**56. Endless Whirlwind of Death** — *melee_self, self*
- Keys: `wh3_dlc25_unit_abilities_whirlwind_of_death_ror` · `wh3_dlc25_unit_abilities_whirlwind_of_death_ror_upgraded`
- Game text: “Dual axe-edges carve through foes, lashing out in a spiral of slaughter, and leaving nought but a bloody mess in their wake.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc25_unit_abilities_whirlwind_of_death_ror`)*
- Owners: The Brotherhood of Grimnir (Doomseekers); unit set(s): wh3_dlc25_dwf_inf_doomseekers_rank7_ror
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **rejected (friendly fire)** — user reason: friendly fire; no automatic logic — player decides.
- Run stats: cd 60s · 6s · self

**57. Enkhil's Kanopi** — *melee_self, self*
- Keys: `wh2_dlc09_item_abilities_enkhils_kanopi`
- Game text: “The simple clay vessel may not look like much, but the High Priest's Undying essence within can thwart sorcery and strengthen incantations.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc09_item_abilities_enkhils_kanopi`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **skipped (not achievable)** — user: not achievable — reacting to an enemy spell cast needs a spell-cast event or an enemy unit read, neither of which exists; no automatic logic.
- Run stats: cd 120s · 24s · self

**58. Enrage** — *melee_self, self*
- Keys: `wh_pro04_unit_abilities_enrage`
- Game text: “You really don't want to make them angry. No, *really*.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh_pro04_unit_abilities_enrage`)*
- Owners: The Bloody Reaver Deck Guard (Depth Guard), The Great Mawherd of Bloodfjord (Feral Mammoths), Soulcrusher (War Mammoth); unit set(s): wh3_dlc23_chd_category_flying_beasts
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **pending test (not yet field-tested)** — implemented (in-melee self); the block-2 field test could not reach it (no DLC ownership assumed) — awaiting a test opportunity.
- Run stats: cd 90s · 22s · self

**59. Entice** — *melee_self, self*
- Keys: `wh3_dlc29_unit_abilities_entice`
- Game text: “A fleeting moment is all she needs – those who draw close find their will slipping away beneath her allure.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc29_unit_abilities_entice`)*
- Owners: Lahmian Vampire
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **pending test (not yet field-tested)** — implemented (in-melee self); the block-2 field test could not reach it (no DLC ownership assumed) — awaiting a test opportunity.
- Run stats: cd 120s · 24s · self

**60. Epidemic Outbreak** — *melee_self, self*
- Keys: `wh3_dlc25_character_abilties_epidemic_outbreak_improved`
- Game text: “A foetid explosion of putrescence tears through the enemy ranks, pulverising the unwary and dousing them in eternal decay.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc25_character_abilties_epidemic_outbreak_improved`)*
- Owners: not unit-innate (granted by character skill)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **rejected (tactical escape)** — user: “the escape in melee is tactically relevant and must be chosen by player”
- Run stats: cd 90s · 2s · self

**61. Epidemic Outburst** — *melee_self, self*
- Keys: `wh3_dlc25_character_abilties_epidemic_outbreak`
- Game text: “Layers of rotten skin explode in a toxic cloud of decay, forcing the foe to stagger back in agony and disgust.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc25_character_abilties_epidemic_outbreak`)*
- Owners: Epidemius
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **rejected (tactical escape)** — user: “the escape in melee is tactically relevant and must be chosen by player”
- Run stats: cd 90s · 2s · self

**62. Everyone Has Their Price** — *melee_self, self*
- Keys: `wh3_main_lord_abilities_everyone_has_their_price`
- Game text: “This hex makes the foe reconsider their options – perhaps leading a warband into almost certain death isn't quite such a good idea after all?” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_lord_abilities_everyone_has_their_price`)*
- Owners: Greasus Goldtooth
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **pending test (not yet field-tested)** — implemented (in-melee self); the block-2 field test could not reach it (no DLC ownership assumed) — awaiting a test opportunity.
- Run stats: cd 120s · 15s · self

**63. Evisceration** — *melee_self, self*
- Keys: `wh2_dlc16_hero_abilities_evisceration`
- Game text: “Consumed by all the rage of the Dark Gods themselves, Ghoritch turns himself into a whirling juggernaut of death.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc16_hero_abilities_evisceration`)*
- Owners: Ghoritch
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **pending test (not yet field-tested)** — implemented (in-melee self); the block-2 field test could not reach it (no DLC ownership assumed) — awaiting a test opportunity.
- Run stats: cd 90s · 4s · self

**64. Eye for an Eye** — *melee_self, self*
- Keys: `wh3_dlc29_spell_bound_eye_jabber`
- Game text: “Losing an eye never slowed down Boris Todbringer – but his foes are not as dogged as he is.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc29_spell_bound_eye_jabber`)*
- Owners: Boris Todbringer (Custom VO), Boris Todbringer
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **pending test (not yet field-tested)** — implemented (in-melee self); the block-2 field test could not reach it (no DLC ownership assumed) — awaiting a test opportunity.
- Run stats: cd 90s · 24s · self

**65. Eye Gouger** — *melee_self, self*
- Keys: `wh3_dlc29_spell_bound_eye_gouger`
- Game text: “Snow-blind, blood-blind, a wolf pushes on. An eye was the price Boris paid. His enemies will pay much more dearly.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc29_spell_bound_eye_gouger`)*
- Owners: not unit-innate (granted by character skill)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **pending test (not yet field-tested)** — implemented (in-melee self); the block-2 field test could not reach it (no DLC ownership assumed) — awaiting a test opportunity.
- Run stats: cd 90s · 24s · self

**66. Eye of the Storm** — *melee_self, self*
- Keys: `wh3_main_lord_abilities_eye_of_the_storm`
- Game text: “From the epicentre of the raging tempest of their righteousness, the Dragon strikes with effortless ease, sweeping the foe away like so many leaves on the wind.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_lord_abilities_eye_of_the_storm`)*
- Owners: Miao Ying, the Storm Dragon; unit set(s): wh3_main_cth_cha_storm_dragon_1
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **pending test (not yet field-tested)** — implemented (in-melee self); the block-2 field test could not reach it (no DLC ownership assumed) — awaiting a test opportunity.
- Run stats: cd 120s · 29s · self

**67. Faith's Bastion** — *melee_self, self*
- Keys: `wh_main_hero_abilities_faiths_bastion`
- Game text: “A quick invocation of protection to Sigmar or Ulric will bless the implorer with a shield of godly faith, should they prove worthy.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh_main_hero_abilities_faiths_bastion`)*
- Owners: not unit-innate (granted by character skill)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **pending test (not yet field-tested)** — implemented (in-melee self); the block-2 field test could not reach it (no DLC ownership assumed) — awaiting a test opportunity.
- Run stats: cd 60s · 22s · self

**68. Fangspike** — *melee_self, self*
- Keys: `wh3_dlc26_weapon_abilities_fangspike`
- Game text: “It is a fang that is a spike, made into a spear. As weaponcraft goes, it follows Goblin guidelines: quick and dirty; used likewise.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc26_weapon_abilities_fangspike`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **redesigned** — user: “Both charge and in melee” · **pending test (DLC unavailable)** — the fangspike is a DLC26 item the user cannot field.
- Run stats: cd 120s · 29s · self

**69. Fangsword of Eltharion** — *melee_self, self*
- Keys: `wh2_dlc15_weapon_abilities_fangsword_of_eltharion`
- Game text: “This rune-encrusted longsword has been passed down through Eltharion’s family for generations, bestowing unto him the zeal of his forefathers.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc15_weapon_abilities_fangsword_of_eltharion`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **pending test (not yet field-tested)** — implemented (in-melee self); the block-2 field test could not reach it (no DLC ownership assumed) — awaiting a test opportunity.
- Run stats: cd 120s · 31s · self

**70. Feint & Riposte** — *melee_self, self*
- Keys: `wh2_main_lord_abilities_feint_and_reposte`
- Game text: “Quite literally the cut-and-thrust of the Elven way of battle; every stroke is precisely made and finds its mark perfectly.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_main_lord_abilities_feint_and_reposte`)*
- Owners: Tyrion, Caradryan
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **pending test (not yet field-tested)** — implemented (in-melee self); the block-2 field test could not reach it (no DLC ownership assumed) — awaiting a test opportunity.
- Run stats: cd 90s · 28s · self

**71. Filth Mace** — *melee_self, self*
- Keys: `wh_main_weapon_abilities_filth_mace`
- Game text: “This rusted mace drips with Nurgle's choicest plagues and bears an enchantment that ensnares the souls of those crushed beneath its filth-encrusted mass.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh_main_weapon_abilities_filth_mace`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **pending test (not yet field-tested)** — implemented (in-melee self); the block-2 field test could not reach it (no DLC ownership assumed) — awaiting a test opportunity.
- Run stats: cd 90s · 30s · self

**72. Fluid Injection!** — *melee_self, self*
- Keys: `wh2_dlc16_unit_abilities_fluid_injection`
- Game text: “The mutated, stitched nightmare roars in pain as a surge of specially concocted Growth Juice courses through its foul body.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc16_unit_abilities_fluid_injection`)*
- Owners: The Thing-Thing (Hell Pit Abomination)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **pending test (not yet field-tested)** — implemented (in-melee self); the block-2 field test could not reach it (no DLC ownership assumed) — awaiting a test opportunity.
- Run stats: cd 60s · 22s · self

**73. Foe-Seeker** — *melee_self, self*
- Keys: `wh_main_character_abilities_foe_seeker_summoned`
- Game text: “There are those who wish nothing more than to be at the heart of battle, seeking foes to vanquish.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh_main_character_abilities_foe_seeker_summoned`)*
- Owners: Krell
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **redesigned** — user: “Same as Foe-Seeker (tired or worse)” · **pending test (not yet field-tested)** — Krell is a character the user did not field.
- Run stats: cd 60s · 25s · self

**74. Fury of the Blood God** — *melee_self, self*
- Keys: `wh3_dlc26_lord_abilities_gaze_of_khorne`
- Game text: “Khorne's gaze falls on all war, at all times, but only Arbaal's feats are capable of riveting His attention. Where it falls, infernos rise.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc26_lord_abilities_gaze_of_khorne`)*
- Owners: Arbaal the Undefeated
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **pending test (not yet field-tested)** — implemented (in-melee self); the block-2 field test could not reach it (no DLC ownership assumed) — awaiting a test opportunity.
- Run stats: cd 120s · 2s · self

**75. Fury of the Falling Blade** — *melee_self, self*
- Keys: `wh3_dlc24_unit_abilities_fury_of_the_falling_blade`
- Game text: “As the rising tempo reaches a crescendo, every man gives way to the rage of war, carrying their fury into every charge.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc24_unit_abilities_fury_of_the_falling_blade`)*
- Owners: The Jade War Drum (Zhangu War Drum)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **rejected (auto: mutual exclusivity)** — user reason: mutual exclusivity; no automatic logic — player decides.
- Run stats: cd 30s · -1s · self

**76. Fury of the Land** — *melee_self, self*
- Keys: `wh3_dlc24_character_abilities_fury_of_the_land`
- Game text: “"Through blood runs the power of the land. Kislev is the land. The Land is Kislev.…” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc24_character_abilities_fury_of_the_land`)*
- Owners: Hag Witch (Hag), Mother Ostankya
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **pending test (not yet field-tested)** — implemented (in-melee self); the block-2 field test could not reach it (no DLC ownership assumed) — awaiting a test opportunity.
- Run stats: cd 120s · 35s · self

**77. Fury of Ursun** — *melee_self, self*
- Keys: `wh3_main_lord_abilities_fury_of_ursun`
- Game text: “Taking on the mantle of the Bear himself, Urskin's furious rage terrifies his foes, walking the finest line between control and frenzy.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_lord_abilities_fury_of_ursun`)*
- Owners: Boris Ursus
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **pending test (not yet field-tested)** — implemented (in-melee self); the block-2 field test could not reach it (no DLC ownership assumed) — awaiting a test opportunity.
- Run stats: cd 90s · 18s · self

**78. Ghal Maraz** — *melee_self, self*
- Keys: `wh_main_weapon_abilities_ghal_maraz`
- Game text: “Ghal Maraz is the legendary hammer of Sigmar. This rune-encrusted weapon is not only the symbol of the Emperor's mantle, but one of the most potent artefacts in the world.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh_main_weapon_abilities_ghal_maraz`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **pending test (not yet field-tested)** — implemented (in-melee self); the block-2 field test could not reach it (no DLC ownership assumed) — awaiting a test opportunity.
- Run stats: cd 120s · 39s · self

**79. Ghoul King of Ushoran** — *melee_self, self*
- Keys: `wh2_dlc11_lord_abilities_ghoul_king_of_ushoran`
- Game text: “From his shattered kingdom, Prince Ushoran reaches forth and makes Lahmian dreams a twisted, hateful reality.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc11_lord_abilities_ghoul_king_of_ushoran`)*
- Owners: Strigoi Vampire Lord
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **redesigned** — user: “When health is 75% or lower”; the interim 80%-re-arm hysteresis was REMOVED (2026-10-05) — plain own health ≤ 75%. · **pending test (not yet field-tested)** — a WH2-DLC hero; not yet field-tested.
- Run stats: cd 120s · 32s · self

**80. Giant Leap** — *melee_self, self*
- Keys: `wh3_dlc24_character_abilities_giant_leap`
- Game text: “When Saytang leaps, the ground trembles …and his foes stumble and fall.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc24_character_abilities_giant_leap`)*
- Owners: Saytang the Watcher
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **pending test (not yet field-tested)** — implemented (in-melee self); the block-2 field test could not reach it (no DLC ownership assumed) — awaiting a test opportunity.
- Run stats: cd 120s · 5s · self

**81. Gitsnik** — *melee_self, self*
- Keys: `wh_main_weapon_abilities_gitsnik`
- Game text: “Shaped in the Daemon-forges of Zharr-Naggrund, Grimgor's mighty axe, Gitsnik, has never grown dull despite its constant use.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh_main_weapon_abilities_gitsnik`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **pending test (not yet field-tested)** — implemented (in-melee self); the block-2 field test could not reach it (no DLC ownership assumed) — awaiting a test opportunity.
- Run stats: cd 120s · 33s · self

**82. Glorious Death** — *melee_self, self*
- Keys: `wh3_dlc25_lord_abilities_glorious_death`
- Game text: “When a Daemon Slayer is at work, those around him get a taste of the glory as he courts renown, legend and, well, death on the battlefield.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc25_lord_abilities_glorious_death`)*
- Owners: Daemon Slayer, Ungrim Ironfist
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **redesigned** — user: “Cast on self when self is a character only makes sense when death is very close. Priority should be cast on another slayer unit (not character) when that unit is in melee.” CORRECTED after the field test (2026-10-05): SLAYER UNITS ONLY — a Slayer ally preferred, else self only when the owner itself is a Slayer and in melee, else silent; a non-Slayer ally is never targeted. Slayer-ness = the derived land_units type-key list. **Field-tested (DLC25).**
- Run stats: cd 120s · 40s · self

**83. Gotrek's Doom** — *melee_self, self*
- Keys: `wh2_pro08_character_abilities_gotrek_doom`
- Game text: “By which the Dwarf Slayer and his mannish chronicler are protected from magical harm, forcing the foe into single combat they have little chance of surviving.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_pro08_character_abilities_gotrek_doom`)*
- Owners: Gotrek
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **pending test (not yet field-tested)** — implemented (in-melee self); the block-2 field test could not reach it (no DLC ownership assumed) — awaiting a test opportunity.
- Run stats: cd 120s · 22s · self

**84. Grand Shield of Faith** — *melee_self, self*
- Keys: `wh_dlc04_spell_bound_shield_of_faith_upgraded`
- Game text: “The Warrior Priest’s faith manifests in the form of a shield as hard as castle-forged steel.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh_dlc04_spell_bound_shield_of_faith_upgraded`)*
- Owners: Arch Lector, Volkmar the Grim
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **pending test (not yet field-tested)** — implemented (in-melee self); the block-2 field test could not reach it (no DLC ownership assumed) — awaiting a test opportunity.
- Run stats: cd 120s · 50s · self · bound

**85. Great Gutgouger** — *melee_self, self*
- Keys: `wh3_dlc26_weapon_abilities_great_gutgouger`
- Game text: “Forged from a mighty Orc weapon brimming with sorcery, and tempered in the gut-stuff of Bragg's own kinfolk. Neither flesh nor minds can withstand it.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc26_weapon_abilities_great_gutgouger`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **pending test (not yet field-tested)** — implemented (in-melee self); the block-2 field test could not reach it (no DLC ownership assumed) — awaiting a test opportunity.
- Run stats: cd 120s · 22s · self

**86. Halo of Maidenly Wrath** — *melee_self, self*
- Keys: `wh2_dlc14_lord_abilities_halo_of_maidenly_wrath`
- Game text: “The power of the Lady shone from Repanse like a halo, her sword and armour glowing with the brilliant light of divine retribution.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc14_lord_abilities_halo_of_maidenly_wrath`)*
- Owners: Repanse de Lyonesse
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **pending test (not yet field-tested)** — implemented (in-melee self); the block-2 field test could not reach it (no DLC ownership assumed) — awaiting a test opportunity.
- Run stats: cd 120s · 3s · self

**87. Hammer-axe of Skoll** — *melee_self, self*
- Keys: `wh3_dlc29_weapon_active_hammer_axe_of_skoll`
- Game text: “The Hammer-axe of Skoll is not just a symbol of duty, but an effective means of carrying it out – particularly when smiting your adversaries.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc29_weapon_active_hammer_axe_of_skoll`)*
- Owners: not unit-innate (granted by character skill)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **pending test (not yet field-tested)** — implemented (in-melee self); the block-2 field test could not reach it (no DLC ownership assumed) — awaiting a test opportunity.
- Run stats: cd 120s · 25s · self

**88. Harbinger of Pestilence** — *melee_self, self*
- Keys: `wh3_dlc20_lord_abilities_harbinger_of_pestilence`
- Game text: “The Leechlord exudes waves of putrid infection, sickening his enemies as disease overcomes them.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc20_lord_abilities_harbinger_of_pestilence`)*
- Owners: Festus the Leechlord
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **rejected (auto: mutual exclusivity)** — user reason: mutual exclusivity; no automatic logic — player decides.
- Run stats: cd 30s · -1s · self · lord

**89. Harvestman's Scythe** — *melee_self, self*
- Keys: `wh3_dlc29_item_active_harvestmans_scythe`
- Game text: “When the blade wakes, it seeks only the greatest hosts for Bloab's virulent plagues.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc29_item_active_harvestmans_scythe`)*
- Owners: not unit-innate (granted by character skill)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **rejected (drawback)** — user reason: drawback (Bonus vs Infantry -100%); no automatic logic — player decides.
- Run stats: cd 120s · 28s · self

**90. Healing Elixirs** — *melee_self, self*
- Keys: `wh3_dlc20_lord_abilities_healing_elixirs`
- Game text: “Doktor Festus can heal as well as harm, he simply finds it far less enjoyable.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc20_lord_abilities_healing_elixirs`)*
- Owners: Festus the Leechlord
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **rejected (auto: mutual exclusivity)** — user reason: mutual exclusivity; no automatic logic — player decides.
- Run stats: cd 30s · -1s · self · lord

**91. Heart Piercing** — *melee_self, self*
- Keys: `wh2_dlc11_lord_abilities_heart_piercing`
- Game text: “When supernatural strength and speed work together, lesser opponents have little chance to counter.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc11_lord_abilities_heart_piercing`)*
- Owners: Blood Dragon Vampire Lord
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (charge and in-melee)** — user chose “Charge and in melee (like Fangspike)”: activate in the charge window OR in melee (and not fleeing), cast on self.
- Run stats: cd 120s · 28s · self

**92. Hellfire Sword** — *melee_self, self*
- Keys: `wh_main_weapon_abilities_hellfire_sword`
- Game text: “This blade was made from a single, searing flame that was hammered into material form and quenched in the body of a fire-djinn.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh_main_weapon_abilities_hellfire_sword`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — user-approved in the questionnaire: activate when in melee and not fleeing, cast on self.
- Run stats: cd 90s · 42s · self

**93. Helm of Discord** — *melee_enemy, self*
- Keys: `wh_main_weapon_abilities_helm_of_discord`
- Game text: “The battered Helm of Discord is a bronze helmet covered in withering symbols that both distract and unsettle any attacker.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh_main_weapon_abilities_helm_of_discord`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — user-approved in the questionnaire: activate when in melee and not fleeing, cast on self.
- Run stats: cd 90s · 25s · self

**94. Helm of Many Eyes** — *melee_self, self*
- Keys: `wh_dlc01_item_passive_helm_of_many_eyes`
- Game text: “This helm is covered with eyeballs that stare into the world as it was, as it is, and as it shall be. Those that can sift through the images are... changed.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh_dlc01_item_passive_helm_of_many_eyes`)*
- Owners: not unit-innate (granted by character skill)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — user-approved in the questionnaire: activate when in melee and not fleeing, cast on self.
- Run stats: cd 90s · 22s · self

**95. Heroic Killing Blow** — *melee_self, self*
- Keys: `wh3_main_pro_character_abilities_heroic_killing_blow_2` · `wh_dlc07_character_abilities_heroic_killing_blow` · `wh_main_character_abilities_heroic_killing_blow`
- Game text: “There are powerful beings who can decapitate a dragon or plunge a sword into the heart of a griffon in one mighty strike.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_pro_character_abilities_heroic_killing_blow_2`)*
- Owners: Alberic de Bordeleaux, Crone Hellebron, Alastar the White Lion, Black Orc Big Boss, Chaos Lord of Slaanesh (+10 more); unit set(s): wh2_twa02_wef_glade_lords_glade_captains
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — user-approved in the questionnaire: activate when in melee and not fleeing, cast on self.
- Run stats: cd 90s · 30s · self

**96. Horn of the First Beast** — *melee_self, self*
- Keys: `wh_dlc03_item_abilities_horn_of_the_first_beast`
- Game text: “When this ancient, fossilised horn is sounded a cloud of disarray falls upon the enemy but emboldens the Gors.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh_dlc03_item_abilities_horn_of_the_first_beast`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (charge and in-melee)** — user chose “Charge and in melee (like Fangspike)”: activate in the charge window OR in melee (and not fleeing), cast on self.
- Run stats: cd 120s · 35s · self

**97. Horn of the Wild Hunt** — *melee_self, self*
- Keys: `wh_dlc05_item_abilities_horn_of_the_wild_hunt`
- Game text: “When this ancient and revered relic is blown, all Elven forces are driven to the Hunt with a savage determination.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh_dlc05_item_abilities_horn_of_the_wild_hunt`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 120s · 24s · self

**98. Hurricane of Death** — *melee_self, self*
- Keys: `wh3_dlc25_character_abilities_hurricane_of_death`
- Game text: “Garagrim spins his weapon in a practiced arc, creating a whirlwind of blood, death and destruction.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc25_character_abilities_hurricane_of_death`)*
- Owners: Garagrim Ironfist
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 120s · 6s · self

**99. Hydra Blade** — *melee_self, self*
- Keys: `wh2_main_weapon_abilities_hydra_blade`
- Game text: “The Hydra Blade was carved from a single fang of Akholrak, first and greatest of the War Hydras broken by Malekith.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_main_weapon_abilities_hydra_blade`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — user-approved in the questionnaire: activate when in melee and not fleeing, cast on self.
- Run stats: cd 120s · 38s · self

**100. In the Name of War** — *melee_self, self*
- Keys: `wh3_dlc29_lord_abilities_in_the_name_of_war`
- Game text: “There is no better reason for conflict, than conflict itself.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc29_lord_abilities_in_the_name_of_war`)*
- Owners: Verminlord Warbringer
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **rejected (rampage)** — loss of control: Rampage (standing rule 4/7); no automatic logic — player decides.
- Run stats: cd 120s · 15s · self

**101. Inevitable Horror** — *melee_enemy, self*
- Keys: `wh3_dlc26_character_abilities_inevitable_horror`
- Game text: “Skarr's approach grants a horrible realisation. Doom is upon you. There is no escape.…” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc26_character_abilities_inevitable_horror`)*
- Owners: Skarr Bloodwrath
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — user-approved in the questionnaire: activate when in melee and not fleeing, cast on self.
- Run stats: cd 120s · 33s · self

**102. Karaghul** — *melee_self, self*
- Keys: `wh2_pro08_weapon_abilities_karaghul`
- Game text: “Felix Jaeger recovered the Rune Sword Karaghul, a blade with a dragon hilt, from a fallen Knight of the Fiery Heart deep within Karak Eight Peaks.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_pro08_weapon_abilities_karaghul`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — user-approved in the questionnaire: activate when in melee and not fleeing, cast on self.
- Run stats: cd 120s · 28s · self

**103. Killing Blow** — *melee_self, self*
- Keys: `wh3_main_pro_character_abilities_heroic_killing_blow_1` · `wh_main_unit_abilities_killing_blow`
- Game text: “There are powerful beings who can decapitate a dragon or plunge a sword into the heart of a griffon in one mighty strike.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_pro_character_abilities_heroic_killing_blow_1`)*
- Owners: not unit-innate (granted by character skill)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — user-approved in the questionnaire: activate when in melee and not fleeing, cast on self.
- Run stats: cd 90s · 30s · self

**104. Legbiter** — *melee_self, self*
- Keys: `wh3_dlc29_weapon_abilities_legbiter`
- Game text: “Boris wields the Runefang with artful, deadly efficiency, targeting weak points to open unexpectedly savage wounds with little effort.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc29_weapon_abilities_legbiter`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — user-approved in the questionnaire: activate when in melee and not fleeing, cast on self.
- Run stats: cd 120s · 28s · self

**105. Liarsbane** — *melee_self, self*
- Keys: `wh3_dlc25_weapon_abilities_liarsbane`
- Game text: “This mighty sword of Nuln is a heavy weight to bear, stained with the blood of the great city's foes and traitors.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc25_weapon_abilities_liarsbane`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — user-approved in the questionnaire: activate when in melee and not fleeing, cast on self.
- Run stats: cd 60s · 28s · self

**106. Lightning Reflexes** — *melee_self, self*
- Keys: `wh2_dlc11_lord_abilities_lightning_reflexes`
- Game text: “The body of a Vampire looks human, but is capable of reactions so fast that even the quickest swordsman would look clumsy in comparison.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc11_lord_abilities_lightning_reflexes`)*
- Owners: not unit-innate (granted by character skill)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — user-approved in the questionnaire: activate when in melee and not fleeing, cast on self.
- Run stats: cd 90s · 32s · self

**107. Locus of Beguilement** — *melee_enemy, self*
- Keys: `wh3_main_character_abilities_locus_of_beguilement`
- Game text: “"What? Why are we…? Er, where am I?…” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_character_abilities_locus_of_beguilement`)*
- Owners: Alluress (Shadows), Alluress (Slaanesh)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — user-approved in the questionnaire: activate when in melee and not fleeing, cast on self.
- Run stats: cd 90s · 22s · self

**108. Locus of Contagion** — *melee_self, self*
- Keys: `wh3_main_character_abilities_locus_of_contagion`
- Game text: “Resistance is futile, for it will only lead to greater suffering and a longer, more agonising demise.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_character_abilities_locus_of_contagion`)*
- Owners: not unit-innate (granted by character skill)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **skipped (revisit)** — user: “Skip for now.”
- Run stats: cd 90s · 11s · self

**109. Locus of Grace** — *melee_self, self*
- Keys: `wh3_main_character_abilities_locus_of_grace`
- Game text: “The warrior glides with a beauteous, smooth elegance that enables them to simply avoid blows as if in slow motion, for the Dark Prince has blessed their every move.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_character_abilities_locus_of_grace`)*
- Owners: Herald of Slaanesh (Shadows), Herald of Slaanesh (Slaanesh)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — user-approved in the questionnaire: activate when in melee and not fleeing, cast on self.
- Run stats: cd 90s · 22s · self

**110. Locus of Wrath** — *melee_self, self*
- Keys: `wh3_main_character_abilities_locus_of_wrath`
- Game text: “Khorne's Heralds find that the pure, unadulterated ire channelled directly from the Blood God Himself drives their own impetuous vehemence to even greater heights.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_character_abilities_locus_of_wrath`)*
- Owners: Herald of Khorne
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — user-approved in the questionnaire: activate when in melee and not fleeing, cast on self.
- Run stats: cd 90s · 25s · self

**111. Lucky Banner** — *melee_self, self*
- Keys: `wh2_dlc15_item_abilities_lucky_banner`
- Game text: “Along with his serendipitous standard-bearer, Niblet, who once somehow survived being sat on by him, the Goblin King’s banner brings inexplicable luck.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc15_item_abilities_lucky_banner`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — user-approved in the questionnaire: activate when in melee and not fleeing, cast on self.
- Run stats: cd 120s · 25s · self

**112. Mace of Ulumak** — *melee_self, self*
- Keys: `wh2_dlc13_weapon_abilities_mace_of_ulumak`
- Game text: “It is believed that the Old Ones themselves guide the hand of he who wields the Mace of Ulumak.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc13_weapon_abilities_mace_of_ulumak`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — user-approved in the questionnaire: activate when in melee and not fleeing, cast on self.
- Run stats: cd 120s · 24s · self

**113. Mad Cap Mushrooms** — *melee_self, self*
- Keys: `wh_main_hero_abilities_mad_cap_mushrooms`
- Game text: “Night Goblin Shamans brew a pungent fungus potion that, when drunk, will send the Fanatics into a spinning, whirling cyclone of death!” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh_main_hero_abilities_mad_cap_mushrooms`)*
- Owners: Night Goblin Shaman
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **skipped (revisit)** — user: “Skip for now” (effect is ability recharge, not combat).
- Run stats: cd 90s · 50s · self

**114. Manann's Luck** — *melee_self, self*
- Keys: `wh2_dlc11_lord_abilities_mananns_luck`
- Game text: “The Seafather looks after his own.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc11_lord_abilities_mananns_luck`)*
- Owners: Aranessa Saltspite
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — user-approved in the questionnaire: activate when in melee and not fleeing, cast on self.
- Run stats: cd 60s · 15s · self

**115. Maneater Smoke Bomb** — *melee_self, self*
- Keys: `wh3_dlc26_unit_abilities_maneater_smoke_bomb`
- Game text: “"Get 'em flailin' an' confused. Makes fightin' more fun. Get 'em smoked.…” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc26_unit_abilities_maneater_smoke_bomb`)*
- Owners: Eshin Maneater
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 90s · 24s · self

**116. Manus of Ursun** — *melee_self, self*
- Keys: `wh3_main_weapon_abilities_ursuns_claws`
- Game text: “These ancient fighting claws are believed to be the pattern upon which the Akshina modelled their weapons.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_weapon_abilities_ursuns_claws`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **rejected (rampage)** — rampage, affects self and allies (standing rule 4/7); no automatic logic — player decides.
- Run stats: cd 60s · 19s · self

**117. Master of the Skies** — *melee_self, self*
- Keys: `wh2_dlc12_lord_abilities_master_of_the_skies`
- Game text: “With the utmost speed and agility, Tiktaq'to leads his death-defying Terradon squadron from atop his prized-specimen mount, Zwup.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc12_lord_abilities_master_of_the_skies`)*
- Owners: Tiktaq'to
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — user-approved in the questionnaire: activate when in melee and not fleeing, cast on self.
- Run stats: cd 60s · 31s · self

**118. Mirror (Grom's Big Waaagh!)** — *melee_self, self*
- Keys: `wh2_dlc15_unit_abilities_mimic_grom_waaagh`
- Game text: “Grom keeps da ladz riled up by keeping them as well fed as he; his big Waaagh! doesn’t fight on an empty stomach!\\n\\n[[col:magic]]This ability is being mirrored using knowledge gained from a prisoner interrogation in Athel Tamarha.[[/col]]” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc15_unit_abilities_mimic_grom_waaagh`)*
- Owners: unit set(s): wh2_dlc15_mistwalkers
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — user-approved in the questionnaire: activate when in melee and not fleeing, cast on self.
- Run stats: cd 120s · 18s · self

**119. Mirror (Waaagh!)** — *melee_self, self*
- Keys: `wh2_dlc15_unit_abilities_mimic_waaagh`
- Game text: “Bellowing a war cry into the air, the mighty Waaagh! is unleashed – da ladz echo the terrifying roar in a crescendo of murderous hysteria!\\n\\n[[col:magic]]This ability is being mirrored using knowledge gained from a prisoner interrogation in Athel Tamarha.[[/col]]” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc15_unit_abilities_mimic_waaagh`)*
- Owners: unit set(s): wh2_dlc15_mistwalkers
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — user-approved in the questionnaire: activate when in melee and not fleeing, cast on self.
- Run stats: cd 90s · 18s · self

**120. Monstrous Strength** — *melee_self, self*
- Keys: `wh2_dlc13_lord_abilities_monstrous_strength`
- Game text: “Fools brace themselves for the impact – realists get well out of the way!” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc13_lord_abilities_monstrous_strength`)*
- Owners: Kroxigor Ancient
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — user-approved in the questionnaire: activate when in melee and not fleeing, cast on self.
- Run stats: cd 90s · 35s · self

**121. Morglor the Mangler** — *melee_self, self*
- Keys: `wh3_dlc26_weapon_abilities_morglor_the_mangler`
- Game text: “There's nothing that mangles matter more than Morglor the Mangler!” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc26_weapon_abilities_morglor_the_mangler`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (charge and in-melee)** — user chose “Charge and in melee (like Fangspike)”: activate in the charge window OR in melee (and not fleeing), cast on self.
- Run stats: cd 120s · 23s · self

**122. Mortal Blow** — *melee_self, self*
- Keys: `wh3_main_daemon_arms_abilities_mortal_blow` · `wh3_main_daemon_arms_abilities_mortal_blow_upgraded`
- Game text: “When all the Ruinous power inside you is charged and focused, a single, devastating blow is all that's needed.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_daemon_arms_abilities_mortal_blow`)*
- Owners: Daemon Prince of Slaanesh, Daemon Prince, Red Ulgor, Prince of Slaughter, Grand Vomitus, Prince of Buboes, Caress, the Darkling Prince (+6 more)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — user-approved in the questionnaire: activate when in melee and not fleeing, cast on self.
- Run stats: cd 60s · 16s · self

**123. Mumbo-Jumbo Chant** — *melee_self, self*
- Keys: `wh3_dlc26_character_abilities_mumbo_jumbo_chant`
- Game text: “The words of this magical chant are different each time, though identically meaningless. It's the conviction that matters, as well as the manic eye-rolling.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc26_character_abilities_mumbo_jumbo_chant`)*
- Owners: Savage Orc Great Shaman, Wurrzag
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — user-approved in the questionnaire: activate when in melee and not fleeing, cast on self.
- Run stats: cd 120s · 30s · self

**124. Necrostrike** — *melee_self, self*
- Keys: `wh2_dlc09_character_abilities_strike_of_nagash`
- Game text: “"This is just the beginning. When the Great Necromancer returns, all around will be laid waste!"” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc09_character_abilities_strike_of_nagash`)*
- Owners: not unit-innate (granted by character skill)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — user-approved in the questionnaire: activate when in melee and not fleeing, cast on self.
- Run stats: cd 120s · 27s · self

**125. Nurgle's Favoured Son** — *melee_self, self*
- Keys: `wh3_dlc25_lord_abilities_nurgles_favoured_son`
- Game text: “Nurgle loves all his children, but those however fated to be his favourites are afforded even more grotesque gifts with which to better carry out His will.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc25_lord_abilities_nurgles_favoured_son`)*
- Owners: Tamurkhan the Maggot Lord
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — user-approved in the questionnaire: activate when in melee and not fleeing, cast on self.
- Run stats: cd 120s · 40s · self

**126. Opal Amulet** — *melee_self, self*
- Keys: `wh_main_item_abilities_opal_amulet`
- Game text: “The Opal Amulet can grant its wearer a life-saving second chance, but suffers a hairline fracture in its previously perfect surface as a result.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh_main_item_abilities_opal_amulet`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — user-approved in the questionnaire: activate when in melee and not fleeing, cast on self.
- Run stats: cd 60s · 22s · self

**127. Oracle of Eternity** — *melee_self, self*
- Keys: `wh3_main_lord_abilities_oracle_of_eternity`
- Game text: “Whilst Kairos is consulting with the infinite he is temporarily protected from harm.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_lord_abilities_oracle_of_eternity`)*
- Owners: Kairos Fateweaver
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — user-approved in the questionnaire: activate when in melee and not fleeing, cast on self.
- Run stats: cd 90s · 22s · self

**128. Pendant of Slaanesh** — *melee_self, self*
- Keys: `wh_main_item_abilities_pendant_of_slaanesh`
- Game text: “This pendant was crafted from the crystallised soul of the very first man to have been seduced by Slaanesh.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh_main_item_abilities_pendant_of_slaanesh`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — user-approved in the questionnaire: activate when in melee and not fleeing, cast on self.
- Run stats: cd 60s · 25s · self

**129. Plaguefather's Oration** — *melee_self, self*
- Keys: `wh3_main_lord_abilities_plaguefathers_oration`
- Game text: “Words of purpose and encouragement from Ku'gath himself stir his warriors to continue spreading disease in Nurgle's blessed name.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_lord_abilities_plaguefathers_oration`)*
- Owners: Ku'gath Plaguefather
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — user-approved in the questionnaire: activate when in melee and not fleeing, cast on self.
- Run stats: cd 90s · 26s · self

**130. Primal Roar** — *melee_self, self*
- Keys: `wh2_dlc13_lord_abilities_primal_roar`
- Game text: “The rallying cry of the ancient, endless, deathless, and vicious.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc13_lord_abilities_primal_roar`)*
- Owners: Nakai the Wanderer
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — user-approved in the questionnaire: activate when in melee and not fleeing, cast on self.
- Run stats: cd 120s · 25s · self

**131. Puncture** — *melee_self, self*
- Keys: `wh3_dlc26_character_abilities_puncture`
- Game text: “For all that he is as ungainly a brute as they come, the Bruiser manoeuvres his wrist blades with the precision of a painter's brush.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc26_character_abilities_puncture`)*
- Owners: Bruiser
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — user-approved in the questionnaire: activate when in melee and not fleeing, cast on self.
- Run stats: cd 90s · 38s · self

**132. Quickblood** — *melee_self, self*
- Keys: `wh3_dlc29_lord_abilities_lightning_reflexes`
- Game text: “Lahmians are renowned for moving faster than the mortal eye can track.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc29_lord_abilities_lightning_reflexes`)*
- Owners: Lahmian Vampire Lord
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — CORRECTED 2026-10-08: NOT a duplicate; the key `wh3_dlc29_lord_abilities_lightning_reflexes` differs from block 3's `wh2_dlc11_lord_abilities_lightning_reflexes`. Auto-activate when in melee and not fleeing, cast on self.
- Run stats: cd 90s · 20s · self

**133. Quicksilver Strike** — *melee_self, self*
- Keys: `wh3_dlc27_lord_abilities_quicksilver_strike`
- Game text: “A technique performed with such speed and precision that it may appear to not have happened at all.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc27_lord_abilities_quicksilver_strike`)*
- Owners: Sea Helm
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — user-approved in the questionnaire: activate when in melee and not fleeing, cast on self.
- Run stats: cd 60s · 29s · self

**134. Rage Embodied** — *melee_self, self*
- Keys: `wh3_main_lord_abilities_rage_embodied`
- Game text: “Skarbrand is the very embodiment of all the Murder Lord's pent-up choler and bile. His presence drives Khorne's warriors to even greater fury.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_lord_abilities_rage_embodied`)*
- Owners: Skarbrand the Exiled
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — user-approved in the questionnaire: activate when in melee and not fleeing, cast on self.
- Run stats: cd 90s · 15s · self

**135. Rage Incarnate** — *melee_self, self*
- Keys: `wh3_main_lord_abilities_rage_incarnate`
- Game text: “Skarbrand's madness corrupts enemy combatants, causing them to rampage as the battlefield is consumed by anarchy.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_lord_abilities_rage_incarnate`)*
- Owners: not unit-innate (granted by character skill)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — user-approved in the questionnaire: activate when in melee and not fleeing, cast on self.
- Run stats: cd 90s · 15s · self

**136. Rapier of Ecstasy** — *melee_self, self*
- Keys: `wh3_dlc20_weapon_abilities_rapier_of_ecstasy`
- Game text: “This unholy blade screams with the power of the Daemon bound inside it – one eternally thirsty for the blood of mortals.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc20_weapon_abilities_rapier_of_ecstasy`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — user-approved in the questionnaire: activate when in melee and not fleeing, cast on self.
- Run stats: cd 90s · 17s · self

**137. Red Ruin** — *melee_self, self*
- Keys: `wh2_dlc10_lord_abilities_red_ruin`
- Game text: “Seeking a mighty death - despite his kingly obligations - Ungrim recklessly carves a path of red ruin through foolish enemies.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc10_lord_abilities_red_ruin`)*
- Owners: Ungrim Ironfist
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — user-approved in the questionnaire: activate when in melee and not fleeing, cast on self.
- Run stats: cd 90s · 35s · self

**138. Refuse to Die** — *melee_self, self*
- Keys: `wh2_dlc12_unit_abilities_refuse_to_die`
- Game text: “The surprising ability to hold back death despite some seriously heavy opposition…” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc12_unit_abilities_refuse_to_die`)*
- Owners: Cohort of Sotek (Red Crested Skinks); unit set(s): lzd_saurus
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — user-approved in the questionnaire: activate when in melee and not fleeing, cast on self.
- Run stats: cd 60s · 20s · self

**139. Revenge Incarnate** — *melee_self, self*
- Keys: `wh_dlc06_lord_abilities_revenge_incarnate`
- Game text: “Centuries of Dwarf grudges flow through Belegar's veins, who uses them to wreak vengeance upon his enemies.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh_dlc06_lord_abilities_revenge_incarnate`)*
- Owners: Belegar Ironhammer
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — user-approved in the questionnaire: activate when in melee and not fleeing, cast on self.
- Run stats: cd 120s · 33s · self

**140. Rok of Itza** — *melee_self, self*
- Keys: `wh2_dlc13_lord_abilities_rock_of_itza`
- Game text: “He is the stone upon which the Lizardmen's enemies are broken.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc13_lord_abilities_rock_of_itza`)*
- Owners: Gor-Rok
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — user-approved in the questionnaire: activate when in melee and not fleeing, cast on self.
- Run stats: cd 60s · 24s · self

**141. Rot or Die!** — *melee_self, self*
- Keys: `wh3_dlc25_lord_abilities_rot_or_die`
- Game text: “Some people are not sufficiently blessed to be given a choice in the matter.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc25_lord_abilities_rot_or_die`)*
- Owners: Chaos Lord of Nurgle
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — user-approved in the questionnaire: activate when in melee and not fleeing, cast on self.
- Run stats: cd 90s · 18s · self

**142. Rot-pocked Axe** — *melee_self, self*
- Keys: `wh3_dlc29_item_active_rot_pocked_axe`
- Game text: “This weapon has slain many a monstrous beast, its pitted edge retaining the vile blood of the creatures slain.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc29_item_active_rot_pocked_axe`)*
- Owners: not unit-innate (granted by character skill)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — user-approved in the questionnaire: activate when in melee and not fleeing, cast on self.
- Run stats: cd 120s · 24s · self

**143. Rune Axe of Gotrek** — *melee_self, self*
- Keys: `wh2_pro08_weapon_abilities_rune_axe_of_gotrek`
- Game text: “Gotrek's signature weapon is a battle-axe imbued with powerful rune magic, recovered from the corpse of King Thangrim Firebeard's son during the Dwarf Slayer's first excursion into the northern Chaos Wastes.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_pro08_weapon_abilities_rune_axe_of_gotrek`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — user-approved in the questionnaire: activate when in melee and not fleeing, cast on self.
- Run stats: cd 120s · 36s · self

**144. Rune Axe of Grombrindal** — *melee_self, self*
- Keys: `wh_pro01_weapon_abilities_rune_axe_of_grombrindal`
- Game text: “Mentioned in several sagas and legends, could the White Dwarf's mighty weapon be the fabled rune axe wielded by Grimnir at the dawn of history?” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh_pro01_weapon_abilities_rune_axe_of_grombrindal`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — user-approved in the questionnaire: activate when in melee and not fleeing, cast on self.
- Run stats: cd 120s · 32s · self

**145. Runefang** — *melee_self, self*
- Keys: `wh_main_weapon_abilities_runefang`
- Game text: “The Runefangs are held by the Elector Counts as symbols of their stately office. They are immensely powerful blades of unsurpassed power that only Ghal Maraz could rival.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh_main_weapon_abilities_runefang`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — user-approved in the questionnaire: activate when in melee and not fleeing, cast on self.
- Run stats: cd 120s · 33s · self

**146. Sacred Spawning of Xhotl** — *melee_self, self*
- Keys: `wh2_main_lord_abilities_sacred_spawning_of_xhotl`
- Game text: “Kroq-Gar arises once more, born anew to take revenge upon those who stand against him.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_main_lord_abilities_sacred_spawning_of_xhotl`)*
- Owners: Kroq-Gar
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — user-approved in the questionnaire: activate when in melee and not fleeing, cast on self.
- Run stats: cd 60s · 20s · self

**147. Sands of Sickness** — *melee_self, self*
- Keys: `wh3_dlc25_character_abilities_sands_of_sickness`
- Game text: “For Grandfather Nurgle's most devoted, sickness is as soothing as it is deliciously vile.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc25_character_abilities_sands_of_sickness`)*
- Owners: not unit-innate (granted by character skill)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — user-approved in the questionnaire: activate when in melee and not fleeing, cast on self.
- Run stats: cd 120s · 25s · self

**148. Scales of the Celestial Court** — *melee_self, self*
- Keys: `wh3_main_item_abilities_scales_of_the_celestial_court`
- Game text: “Fashioned from scales of the Celestial Dragon himself, this armour is worn only by the greatest Cathayan heroes, that they may resist blows and traverse terrain without impediment.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_item_abilities_scales_of_the_celestial_court`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — user-approved in the questionnaire: activate when in melee and not fleeing, cast on self.
- Run stats: cd 120s · 21s · self

**149. Sceptre of Titans** — *melee_self, self*
- Keys: `wh3_main_weapon_abilities_sceptre_of_titans`
- Game text: “This massive sceptre, ensorcelled with spells of might, helpfully imbues Greasus with the strength of a Sky-Titan.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_weapon_abilities_sceptre_of_titans`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — user-approved in the questionnaire: activate when in melee and not fleeing, cast on self.
- Run stats: cd 120s · 21s · self

**150. Scourge** — *melee_self, self*
- Keys: `wh_dlc03_weapon_abilities_scourge`
- Game text: “Scourge is a lethal whip, thirsty for blood and wrapped in the bitter curses of many generations of Bray-Shamans.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh_dlc03_weapon_abilities_scourge`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — user-approved in the questionnaire: activate when in melee and not fleeing, cast on self.
- Run stats: cd 120s · 35s · self

**151. Scrying Stone** — *melee_self, self*
- Keys: `wh2_main_item_abilities_scrying_stone`
- Game text: “An orb made of the polished gallstones from the dreaded Blindwyrm is said to be able to glimpse the future.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_main_item_abilities_scrying_stone`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — user-approved in the questionnaire: activate when in melee and not fleeing, cast on self.
- Run stats: cd 60s · 30s · self

**152. Seduction of the Serpent** — *melee_self, self*
- Keys: `wh_dlc08_lord_abilities_seduction_of_the_serpent`
- Game text: “Although the youngest of the Dark Gods, the Serpent is no less potent and can bind mortals to eternal service with alluring visions or tantalising temptations.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh_dlc08_lord_abilities_seduction_of_the_serpent`)*
- Owners: not unit-innate (granted by character skill)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — user-approved in the questionnaire: activate when in melee and not fleeing, cast on self.
- Run stats: cd 90s · 17s · self

**153. Seductive Glory** — *melee_self, self*
- Keys: `wh3_main_lord_abilities_seductive_glory`
- Game text: “When victory is thought to be close, caution is cast to the four winds and frenzy beckons enticingly.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_lord_abilities_seductive_glory`)*
- Owners: Daemon Prince, Red Ulgor, Prince of Slaughter, Grand Vomitus, Prince of Buboes, Caress, the Darkling Prince, Zarrivyk, Feathered-Prince (+6 more)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **skipped (revisit)** — drawback + Rampage; user: "Skip for now."
- Run stats: cd 90s · 15s · self

**154. Seismic Snare** — *melee_self, self*
- Keys: `wh2_dlc14_unit_abilities_seismic_snare` · `wh3_dlc29_unit_abilities_stormfiend_seismic_snare`
- Game text: “Like their huge, earth-boring equivalents, Warp-Grinders can turn solid rock into dust on a smaller scale, halting enemies’ movements by pulverising the ground beneath them.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc14_unit_abilities_seismic_snare`)*
- Owners: Warp-Grinders, Stormfiends (Grinderfists)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **skipped (revisit)** — user: "Skip for now."
- Run stats: cd 60s · 13s · self

**155. Shadow Shroud** — *melee_self, self*
- Keys: `wh3_main_lord_abilities_shadow_shroud`
- Game text: “The Father-in-Shadow wraps himself in a cloak of murk that protects him from lesser magicks.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_lord_abilities_shadow_shroud`)*
- Owners: Be'lakor, wh3_survival_dae_cha_be_lakor
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — user-approved in the questionnaire: activate when in melee and not fleeing, cast on self.
- Run stats: cd 120s · 22s · self

**156. Shield of Aeons** — *melee_self, self*
- Keys: `wh2_dlc13_item_abilities_shield_of_aeons`
- Game text: “A dozen Kroxigor were needed to haul this matchless shield to the mainland and generations of Skink artisans laboured to carve it.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc13_item_abilities_shield_of_aeons`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — user-approved in the questionnaire: activate when in melee and not fleeing, cast on self.
- Run stats: cd 120s · 23s · self

**157. Shield of Faith** — *melee_self, self*
- Keys: `wh_main_spell_bound_shield_of_faith`
- Game text: “The Warrior Priest’s faith manifests in the form of a shield as hard as castle-forged steel.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh_main_spell_bound_shield_of_faith`)*
- Owners: Warrior Priest
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — user-approved in the questionnaire: activate when in melee and not fleeing, cast on self.
- Run stats: cd 90s · 25s · self · bound

**158. Silver Dagger** — *melee_self, self*
- Keys: `wh3_dlc23_weapon_abilities_silver_dagger`
- Game text: “Neither armour nor wards can turn Ulrika's silver blade from its target, such are its innate magical properties.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc23_weapon_abilities_silver_dagger`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — user-approved in the questionnaire: activate when in melee and not fleeing, cast on self.
- Run stats: cd 120s · 32s · self

**159. Silver Horn of Vengeance** — *melee_self, self*
- Keys: `wh_main_item_abilities_silver_horn_of_vengeance`
- Game text: “When winded, the Silver Horn sounds a clear note that brings hope to Dwarfs and foreboding doom to the enemy.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh_main_item_abilities_silver_horn_of_vengeance`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **skipped (unsuitable: charge-only)** — collection-time: charge-only; no automatic logic.
- Run stats: cd 60s · 22s · self

**160. Skull Wand of Kaloth** — *melee_self, self*
- Keys: `wh_main_item_abilities_skull_wand_of_kaloth`
- Game text: “Originally captured from the Necromancer Kaloth by the gobbo Shaman Kazgi, the Skull Wand talks in a forgotten dread language and any who hear its words are doomed.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh_main_item_abilities_skull_wand_of_kaloth`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — user-approved in the questionnaire: activate when in melee and not fleeing, cast on self.
- Run stats: cd 120s · 27s · self

**161. Slippery** — *melee_self, self*
- Keys: `wh_main_hero_abilities_slippery`
- Game text: “Those who are "slippery" cannot be cornered or pinned - they simply "slip" away…” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh_main_hero_abilities_slippery`)*
- Owners: Alith Anar, Hand of the Shadow Crown, Hertwig van Hal, Deathmaster Snikch, Master Assassin (+11 more)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — user-approved in the questionnaire: activate when in melee and not fleeing, cast on self.
- Run stats: cd 60s · 25s · self

**162. Sliverslash** — *melee_self, self*
- Keys: `wh3_dlc20_weapon_abilities_sliverslash`
- Game text: “Enemies cannot hope to withstand such a grievous onslaught of graceful and deadly strikes.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc20_weapon_abilities_sliverslash`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — user-approved in the questionnaire: activate when in melee and not fleeing, cast on self.
- Run stats: cd 120s · 26s · self

**163. Smash 'Em Faster** — *melee_self, self*
- Keys: `wh2_dlc15_lord_abilities_smash_em_faster`
- Game text: “By the bellow of an angry Warboss, there’s always that little bit more murderousness to be squeezed from the boys.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc15_lord_abilities_smash_em_faster`)*
- Owners: Orc Warboss
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — user-approved in the questionnaire: activate when in melee and not fleeing, cast on self.
- Run stats: cd 90s · 30s · self

**164. Stand or Die!** — *melee_self, self*
- Keys: `wh_main_character_abilities_stand_or_die`
- Game text: “Those whose word is law ensure their troops will not run by issuing this dread order.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh_main_character_abilities_stand_or_die`)*
- Owners: Tretch Craventail, Overseer, Gutrot Spume, Chaos Lord, Chaos Lord – Deprecated (+2 more)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — user-approved in the questionnaire: activate when in melee and not fleeing, cast on self.
- Run stats: cd 90s · 18s · self

**165. Star Lance** — *melee_self, self*
- Keys: `wh2_dlc15_weapon_abilities_star_lance`
- Game text: “Legend has it that the Star Lance strikes with the wrath of a Star Dragon, and cannot be unmade while the drakes still live upon Ulthuan.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc15_weapon_abilities_star_lance`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (charge and in-melee)** — user chose "Charge and in melee (like Fangspike)": activate in the charge window OR in melee (and not fleeing), cast on self.
- Run stats: cd 120s · 29s · self

**166. Starcrusher** — *melee_self, self*
- Keys: `wh_dlc01_weapon_abilities_starcrusher`
- Game text: “The gigantic warhammer known as Starcrusher was forged in the raging heart of a volcano. Kholek wields this enormous weapon with staggering brutality and skill despite its size.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh_dlc01_weapon_abilities_starcrusher`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — user-approved in the questionnaire: activate when in melee and not fleeing, cast on self.
- Run stats: cd 120s · 43s · self

**167. Steppe Hunter's Horn** — *melee_self, self*
- Keys: `wh3_main_item_abilities_steppe_hunters_horn`
- Game text: “Taken from an unknown but clearly massive beast, this horn has been handed from father to eldest son through generations of Kislev's pre-eminent family of beast hunters.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_item_abilities_steppe_hunters_horn`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — user-approved in the questionnaire: activate when in melee and not fleeing, cast on self.
- Run stats: cd 60s · 20s · self

**168. Stinky Giant Club** — *melee_self, self*
- Keys: `wh_dlc08_weapon_abilities_stinky_giant_club`
- Game text: “Both the Giant and his club smell absolutely repulsive, their repellent odour discouraging foes just long enough for this blunt instrument to do its messy work.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh_dlc08_weapon_abilities_stinky_giant_club`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — user-approved in the questionnaire: activate when in melee and not fleeing, cast on self.
- Run stats: cd 120s · 57s · self

**169. Storm Rage** — *melee_self, self*
- Keys: `wh3_dlc20_unit_abilities_storm_rage`
- Game text: “Call upon the elemental rage of the storm, letting lightning strike and empower its summoner through an electrifying charge.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc20_unit_abilities_storm_rage`)*
- Owners: unit set(s): chs_dragon_ogre_shaggoths, chs_dragon_ogres
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (charge and in-melee)** — user chose "Charge and in melee (like Fangspike)": activate in the charge window OR in melee (and not fleeing), cast on self.
- Run stats: cd 90s · 24s · self

**170. Stormlance** — *melee_self, self*
- Keys: `wh3_dlc25_item_abilities_stormlance`
- Game text: “With a bladed tip crafted from meteoric iron and graven with the runes of the heavens, this lance strikes its target like a bolt of lightning, both burning and blasting them.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc25_item_abilities_stormlance`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (charge and in-melee)** — user chose "Charge and in melee (like Fangspike)": activate in the charge window OR in melee (and not fleeing), cast on self.
- Run stats: cd 120s · 32s · self

**171. Swiftness of Itzl** — *melee_self, self*
- Keys: `wh2_main_character_abilities_swiftness_of_itzl`
- Game text: “The speed and agility of the great three-horned ruler is sometimes bestowed upon his subjects.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_main_character_abilities_swiftness_of_itzl`)*
- Owners: Kroq-Gar
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **skipped (unsuitable: movement/vortex)** — collection-time: movement/vortex; no automatic logic.
- Run stats: cd 90s · 32s · self

**172. Sword of Anti-Heroes** — *melee_self, self*
- Keys: `wh_main_weapon_abilities_sword_of_anti_heroes`
- Game text: “This sword was said to be smelted in a cursed furnace and then quenched in the bloody body of a dying champion.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh_main_weapon_abilities_sword_of_anti_heroes`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self)** — user-approved in the questionnaire: activate when in melee and not fleeing, cast on self.
- Run stats: cd 90s · 40s · self

**173. Sword of Teclis** — *melee_self, self*
- Keys: `wh2_main_weapon_abilities_sword_of_teclis`
- Game text: “This sword, created by Teclis, is charged with crackling energy that rends apart those struck by its shining blade.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_main_weapon_abilities_sword_of_teclis`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **excluded (magic scope)** — user: "Skip - it's a magic-resource ability (excluded scope)".
- Run stats: cd 120s · 23s · self

**174. Sword of Torgald** — *melee_self, self*
- Keys: `wh_dlc08_weapon_abilities_sword_of_torgald`
- Game text: “Although King Torgald's blade is a prized trophy, it is also an eternal reminder of the consequences of grand proclamations afore the Gods.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh_dlc08_weapon_abilities_sword_of_torgald`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 120s · 44s · self
- Decision: **implemented (in-melee self - auto, trivial)** — trivial self-buff: Base/AP Weapon Damage +50% (imbuements Inevitable End!, Magical Attacks — ignored); auto-accepted WITHOUT the questionnaire per standing rule 9 (imbuements/attributes ignored). Implement: when in melee (and not fleeing), cast on self.

**175. Tempest Rage** — *melee_self, self*
- Keys: `wh3_dlc20_lord_abilities_tempest_rage`
- Game text: “Shining rays of light fall upon the worthy, riling the recipient into a violent frenzy.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc20_lord_abilities_tempest_rage`)*
- Owners: Kholek Suneater
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 120s · 36s · self
- Decision: **implemented (charge and in-melee)** — user chose “Charge and in melee (like Fangspike)”: activate in the charge window OR in melee (and not fleeing), cast on self.

**176. Tenebrous Forge-Hammer** — *melee_self, self*
- Keys: `wh3_dlc27_weapon_abilities_tenebrous_forge_hammer`
- Game text: “"...And so the hammer smote down the noble knight, his armour and flesh crumbling into black dust upon whence the blow struck. The cawing of crows echoed in the distance..." – Old Norscan legend” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc27_weapon_abilities_tenebrous_forge_hammer`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 90s · 24s · self
- Decision: **implemented (in-melee self)** — user-approved in the block-5 questionnaire: activate when in melee and not fleeing, cast on self.

**177. The Armour of Morkar** — *melee_self, self*
- Keys: `wh3_dlc20_item_abilities_the_armour_of_morkar`
- Game text: “The armour of the Everchosen is as ancient and powerful as his legend.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc20_item_abilities_the_armour_of_morkar`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 120s · 29s · self
- Decision: **implemented (in-melee self)** — user-approved in the block-5 questionnaire: activate when in melee and not fleeing, cast on self.

**178. The Bane Spear** — *melee_self, self*
- Keys: `wh3_main_weapon_abilities_banespear`
- Game text: “Bartered for his tribesmen's souls by a chieftain who then double-crossed the Dark Gods, this spear, which can banish their servants, is all that remains.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_weapon_abilities_banespear`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 120s · 21s · self
- Decision: **implemented (in-melee self)** — user-approved in the block-5 questionnaire: activate when in melee and not fleeing, cast on self.

**179. The Black Axe of Krell** — *melee_self, self*
- Keys: `wh3_dlc29_item_abilities_black_axe_of_krell`
- Game text: “When the Black Axe of Krell bites into flesh, it leaves behind jagged shards that swiftly eat their way into the victim's heart.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc29_item_abilities_black_axe_of_krell`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 120s · 31s · self · item
- Decision: **implemented (in-melee self - auto, trivial)** — trivial self-buff: Melee Attack +24, Base/AP Weapon Damage +30% (imbuement Disembowelled! — ignored); auto-accepted WITHOUT the questionnaire per standing rule 9 (imbuements/attributes ignored). Implement: when in melee (and not fleeing), cast on self.

**180. The Black Cleaver** — *melee_self, self*
- Keys: `wh3_dlc25_weapon_abilities_the_black_cleaver`
- Game text: “Gifted to him by the Chaos Dwarfs, the greyish fumes that emanate when this weapon is swung are foully poisonous – which pleases the Maggot Lord greatly!” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc25_weapon_abilities_the_black_cleaver`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 120s · 36s · self
- Decision: **implemented (in-melee self - auto, trivial)** — trivial self-buff: Melee Attack +24, Base/AP Weapon Damage +25% (imbuement Magical Attacks — ignored); auto-accepted WITHOUT the questionnaire per standing rule 9 (imbuements/attributes ignored). Implement: when in melee (and not fleeing), cast on self.

**181. The Blessed Blade of Ptra** — *melee_self, self*
- Keys: `wh2_dlc09_weapon_abilities_blessed_blade_of_ptra`
- Game text: “This blade, blessed by the Ptra the Sun God, channels the baking heat of the unforgiving Nehekharan desert into each deadly blow it makes.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc09_weapon_abilities_blessed_blade_of_ptra`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 120s · 43s · self
- Decision: **implemented (in-melee self - auto, trivial)** — trivial self-buff: self weapon-imbuements only (Flaming Attacks, Blinded!, Magical Attacks — all ignored); no non-imbuement effect; auto-accepted WITHOUT the questionnaire per standing rule 9 (imbuements/attributes ignored). Implement: when in melee (and not fleeing), cast on self.

**182. The Blood Price** — *melee_self, self*
- Keys: `wh2_dlc14_lord_abilities_the_blood_price`
- Game text: “Forever tormenting Malus’ soul, Tz’arkan’s Daemonic puissance always simmers just beneath Malus’ skin.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc14_lord_abilities_the_blood_price`)*
- Owners: Malus Darkblade
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 90s · 22s · self
- Decision: **implemented (in-melee self)** — user-approved in the block-5 questionnaire: activate when in melee and not fleeing, cast on self.

**183. The Carstein Ring** — *melee_self, self*
- Keys: `wh_dlc04_item_abilities_the_carstein_ring`
- Game text: “An ancestral ring, set with a gem of deep, sanguine claret, that has granted the von Carsteins everlasting Undeath.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh_dlc04_item_abilities_the_carstein_ring`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 120s · 22s · self
- Decision: **implemented (in-melee self)** — user-approved in the block-5 questionnaire: activate when in melee and not fleeing, cast on self.

**184. The Daemon's Curse** — *melee_self, self*
- Keys: `wh2_dlc14_lord_abilities_the_daemons_curse`
- Game text: “Those who go to war against Malus Darkblade feel his Daemonic aura. Those who come face to face with him are infected by it.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc14_lord_abilities_the_daemons_curse`)*
- Owners: Malus Darkblade
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 120s · 34s · self
- Decision: **implemented (in-melee self)** — user-approved in the block-5 questionnaire: activate when in melee and not fleeing, cast on self.

**185. The Dancing Blade** — *melee_self, self*
- Keys: `wh3_dlc23_character_abilities_sword_dance`
- Game text: “So graceful are her movements, and so precise her attacks, that to see Ulrika in the midst of battle is almost like witnessing a dance, rather than a slaughter.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc23_character_abilities_sword_dance`)*
- Owners: Ulrika Magdova
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 120s · 23s · self
- Decision: **implemented (in-melee self)** — user-approved in the block-5 questionnaire: activate when in melee and not fleeing, cast on self.

**186. The Dragon's Fang** — *melee_self, self*
- Keys: `wh3_dlc24_weapon_abilities_dragons_fang`
- Game text: “Exquisitely crafted from one of the Celestial Dragon’s own teeth is the weapon of his executioner, wielded by the Jade Dragon with strength and authority.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc24_weapon_abilities_dragons_fang`)*
- Owners: unit set(s): wh3_dlc24_cth_cha_yuan_bo_dragon, wh3_dlc24_cth_cha_yuan_bo_human
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 120s · 20s · self
- Decision: **implemented (in-melee self - auto, trivial)** — trivial self-buff: Melee Attack +40, Base/AP Weapon Damage +50% (attribute Executioner — ignored); auto-accepted WITHOUT the questionnaire per standing rule 9 (imbuements/attributes ignored). Implement: when in melee (and not fleeing), cast on self.

**187. The Drakwald Runefang** — *melee_self, self*
- Keys: `wh2_dlc13_weapon_abilities_drakwald_runefang`
- Game text: “One of twelve magical swords belonging to the Empire's Elector Counts, 'Beast Slayer' has taken down many of the hideous monsters infesting the dark, dense Drakwald Forest.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc13_weapon_abilities_drakwald_runefang`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 120s · 39s · self
- Decision: **implemented (in-melee self)** — user-approved in the block-5 questionnaire: activate when in melee and not fleeing, cast on self.

**188. The Eternal Blade** — *melee_self, self*
- Keys: `wh3_main_weapon_abilities_the_eternal_blade`
- Game text: “Present at every major battle since the dawn of time, this blade guarantees its owner great worldly renown as long as it consents to their will.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_weapon_abilities_the_eternal_blade`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 120s · 21s · self
- Decision: **implemented (in-melee self - auto, trivial)** — trivial self-buff: Melee Attack +40, Base/AP Weapon Damage +50%; auto-accepted WITHOUT the questionnaire per standing rule 9 (imbuements/attributes ignored). Implement: when in melee (and not fleeing), cast on self. **User correction (2026-10-08, block-5 questionnaire):** “Yes, and should have been accepted from the beggining as I said. Please do not show me the trivial ones like this.”

**189. The Father of Blades** — *melee_self, self*
- Keys: `wh3_dlc25_weapon_abilities_the_father_of_blades`
- Game text: “This ancient, storied sword is rumoured to be the first one ever forged. It certainly seems to have an uncanny power over other weapons...” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc25_weapon_abilities_the_father_of_blades`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 90s · 33s · self
- Decision: **implemented (in-melee self)** — user-approved in the block-5 questionnaire: activate when in melee and not fleeing, cast on self.

**190. The Hochland Runefang** — *melee_self, self*
- Keys: `wh2_dlc13_weapon_abilities_hochland_runefang`
- Game text: “One of twelve magical swords belonging to the Empire's Elector Counts, 'Goblin Bane', as its name suggests, has cleared the insidious Greenskins from Hochland's vast tracts of wilderness.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc13_weapon_abilities_hochland_runefang`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 120s · 24s · self
- Decision: **implemented (in-melee self)** — user-approved in the block-5 questionnaire: activate when in melee and not fleeing, cast on self.

**191. The Horn of Kygor** — *melee_self, self*
- Keys: `wh2_main_item_abilities_the_horn_of_kygor`
- Game text: “It is said that the legendary Kygor, the first owner of the horn, was a warrior who could stare down a Carnosaur!” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_main_item_abilities_the_horn_of_kygor`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 90s · 20s · self
- Decision: **implemented (charge and in-melee)** — user chose “Charge and in melee (like Fangspike)”: activate in the charge window OR in melee (and not fleeing), cast on self.

**192. The Mace of Helsturm** — *melee_self, self*
- Keys: `wh_main_weapon_abilities_the_mace_of_helsturm`
- Game text: “Used by Johann Helsturm, the first Grand Theogonist. When wielded by a warrior whose devotion is beyond reproach the head of the mace glows so brightly it bursts into flame.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh_main_weapon_abilities_the_mace_of_helsturm`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 90s · 40s · self
- Decision: **implemented (in-melee self - auto, trivial)** — trivial self-buff: Base Weapon Damage +60% (imbuement Flaming Attacks — ignored); auto-accepted WITHOUT the questionnaire per standing rule 9 (imbuements/attributes ignored). Implement: when in melee (and not fleeing), cast on self.

**193. The Nordland Runefang** — *melee_self, self*
- Keys: `wh2_dlc13_weapon_abilities_nordland_runefang`
- Game text: “One of twelve magical swords belonging to the Empire's Elector Counts, 'Crow Feeder' leaves its prey - often the marauding Norscans - as nothing but so much carrion.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc13_weapon_abilities_nordland_runefang`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 120s · 22s · self
- Decision: **implemented (in-melee self)** — user-approved in the block-5 questionnaire: activate when in melee and not fleeing, cast on self.

**194. The Ostermark Runefang** — *melee_self, self*
- Keys: `wh2_dlc13_weapon_abilities_ostermark_runefang`
- Game text: “One of twelve magical swords belonging to the Empire's Elector Counts, 'Troll Cleaver' is used to cull the myriad dangerous creatures rampaging around the extremely fertile 'East March'.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc13_weapon_abilities_ostermark_runefang`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 120s · 27s · self
- Decision: **implemented (in-melee self)** — user-approved in the block-5 questionnaire: activate when in melee and not fleeing, cast on self.

**195. The Ostland Runefang** — *melee_self, self*
- Keys: `wh2_dlc13_weapon_abilities_ostland_runefang`
- Game text: “One of twelve magical swords belonging to the Empire's Elector Counts, 'Brain Wounder' sees almost constant action against the savage Chaos Warbands invading from the desolate, frozen north.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc13_weapon_abilities_ostland_runefang`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 120s · 38s · self
- Decision: **implemented (in-melee self - auto, trivial)** — trivial self-buff: Base/AP Weapon Damage +50%; auto-accepted WITHOUT the questionnaire per standing rule 9 (imbuements/attributes ignored). Implement: when in melee (and not fleeing), cast on self.

**196. The Phoenix Blade** — *melee_self, self*
- Keys: `wh3_dlc27_weapon_abilities_the_phoenix_blade`
- Game text: “This ancient, flame-wreathed armament was enchanted for the first Captain of the Phoenix Guard as a fiery symbol of divine station.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc27_weapon_abilities_the_phoenix_blade`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 120s · 21s · self
- Decision: **implemented (in-melee self)** — user-approved in the block-5 questionnaire: activate when in melee and not fleeing, cast on self.

**197. The Praise of Slaanesh** — *melee_self, self*
- Keys: `wh3_dlc27_lord_abilities_the_praise_of_slaanesh`
- Game text: “The Dark Prince's servants are eternally bound to His whims. Those same whims, at times, dictate that He simply... set them loose.…” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc27_lord_abilities_the_praise_of_slaanesh`)*
- Owners: Dechala, the Denied One
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 30s · -1s · self

**198. The Reikland Runefang** — *melee_self, self*
- Keys: `wh_main_weapon_abilities_the_reikland_runefang`
- Game text: “The Reikland Runefang is the symbol of the Elector Count of this province. It is currently owned by the Prince of Altdorf, Karl Franz.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh_main_weapon_abilities_the_reikland_runefang`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 120s · 39s · self
- Decision: **implemented (in-melee self)** — user-approved in the block-5 questionnaire: activate when in melee and not fleeing, cast on self.

**199. The Rock of Inevitability** — *melee_self, self*
- Keys: `wh3_main_item_abilities_the_rock_of_inevitability`
- Game text: “So long as a single stone remains, the ageless Inevitable City shall always rebuild itself.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_item_abilities_the_rock_of_inevitability`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 90s · 22s · self
- Decision: **implemented (in-melee self)** — user-approved in the block-5 questionnaire: activate when in melee and not fleeing, cast on self.

**200. The Rotaxes** — *melee_self, self*
- Keys: `wh3_dlc29_item_active_the_rotaxes`
- Game text: “Rusted axes, fashioned from the fetor of Nurgle's Garden, whose foul essence infects their bite with unrelenting Daemonic strength.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc29_item_active_the_rotaxes`)*
- Owners: not unit-innate (granted by character skill)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 120s · 30s · self
- Decision: **implemented (in-melee self - auto, trivial)** — trivial self-buff: Melee Attack +24, Base/AP Weapon Damage +50% (attribute Executioner — ignored); auto-accepted WITHOUT the questionnaire per standing rule 9 (imbuements/attributes ignored). Implement: when in melee (and not fleeing), cast on self.

**201. The Slayer of Kings** — *melee_self, self*
- Keys: `wh_dlc01_weapon_abilities_the_slayer_of_kings`
- Game text: “The Second Everchosen, Vangel, trapped the Greater Daemon U'zuhl inside this regicidal blade.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh_dlc01_weapon_abilities_the_slayer_of_kings`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 120s · 25s · self
- Decision: **implemented (in-melee self - auto, trivial)** — user: “Yes, and also trivial.” Splash Attack Power now counts as trivial (standing rule 9, updated 2026-10-08 in the block-5 decision); auto-accepted WITHOUT the questionnaire. Implement: when in melee (and not fleeing), cast on self.

**202. The Slayer Sword** — *melee_self, self*
- Keys: `wh3_dlc26_weapon_abilities_the_slayer_sword`
- Game text: “A shard of Khorne's wrath made manifest. A foe's very soul speaks to it, begging for release, even as the flesh recoils, then gives way and parts without resistance.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc26_weapon_abilities_the_slayer_sword`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 120s · 22s · self
- Decision: **implemented (in-melee self - auto, trivial)** — trivial self-buff: Melee Attack +24, Base/AP Weapon Damage +50% (imbuement Weakened — ignored); auto-accepted WITHOUT the questionnaire per standing rule 9 (imbuements/attributes ignored). Implement: when in melee (and not fleeing), cast on self.

**203. The Sword of Couronne** — *melee_self, self*
- Keys: `wh_main_weapon_abilities_the_sword_of_couronne`
- Game text: “This powerful heirloom was forged from the finest Bretonnian silverline. It catches the suns rays and magnifies them, dazzling Louen's enemies as he makes the death stroke.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh_main_weapon_abilities_the_sword_of_couronne`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 120s · 38s · self
- Decision: **implemented (in-melee self)** — user-approved in the block-5 questionnaire: activate when in melee and not fleeing, cast on self.

**204. The Sword of Lyonesse** — *melee_self, self*
- Keys: `wh2_dlc14_weapon_abilities_sword_of_lyonesse`
- Game text: “When first she faced Chaos, Repanse broke open the reliquary of the village Grail Chapel and took up the ancient sword she found there.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc14_weapon_abilities_sword_of_lyonesse`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 120s · 24s · self
- Decision: **implemented (in-melee self - auto, trivial)** — trivial self-buff: Melee Attack +40, Base/AP Weapon Damage +50%; auto-accepted WITHOUT the questionnaire per standing rule 9 (imbuements/attributes ignored). Implement: when in melee (and not fleeing), cast on self.

**205. The Talabecland Runefang** — *melee_self, self*
- Keys: `wh2_dlc13_weapon_abilities_talabecland_runefang`
- Game text: “One of twelve magical swords belonging to the Empire's Elector Counts, Talabecland's 'Stone Breaker' has protected the founding province's thriving commerce from bandits of all kinds for centuries.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc13_weapon_abilities_talabecland_runefang`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 120s · 41s · self
- Decision: **implemented (in-melee self - auto, trivial)** — trivial self-buff: Melee Attack +40 (imbuement Sundered Armour — ignored); auto-accepted WITHOUT the questionnaire per standing rule 9 (imbuements/attributes ignored). Implement: when in melee (and not fleeing), cast on self.

**206. The Tenderiser** — *melee_self, self*
- Keys: `wh3_main_weapon_abilities_the_tenderiser`
- Game text: “This massive two-ended club is so heavy even a normal Ogre Bull would struggle. Bound into its heads is the power to shatter a boulder with one strike.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_weapon_abilities_the_tenderiser`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 90s · 25s · self
- Decision: **implemented (in-melee self - auto, trivial)** — trivial self-buff: Base/AP Weapon Damage +50%; auto-accepted WITHOUT the questionnaire per standing rule 9 (imbuements/attributes ignored). Implement: when in melee (and not fleeing), cast on self.

**207. The Waltz of Lethargy** — *melee_self, self*
- Keys: `wh3_dlc27_lord_abilities_the_waltz_of_lethargy`
- Game text: “A languorous, ceaseless waltz to haunt the enemy with spinning figures just outside the edge of their vision.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc27_lord_abilities_the_waltz_of_lethargy`)*
- Owners: The Masque of Slaanesh
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 20s · -1s · self · lord

**208. The Wissenland Runefang** — *melee_self, self*
- Keys: `wh2_dlc13_weapon_abilities_wissenland_runefang`
- Game text: “One of twelve magical swords belonging to the Empire's Elector Counts, 'Blood Bringer' is a mighty blade befitting Wissenland's important status as the centre of Imperial arms production.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc13_weapon_abilities_wissenland_runefang`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 120s · 29s · self

**209. Toad Rage** — *melee_self, self*
- Keys: `wh2_dlc12_unit_abilities_toad_rage`
- Game text: “The presence of the hated Lustrian Blot Toad sends the merciless Ripperdactyls into a barely-controlled frenzy of extreme violence!” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc12_unit_abilities_toad_rage`)*
- Owners: Colossadon Hunters (Ripperdactyl Riders)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 60s · 18s · self
- Decision: **implemented (in-melee self)** — user-approved in the block-5 questionnaire: activate when in melee and not fleeing, cast on self.

**210. Tombstrike** — *melee_self, self*
- Keys: `wh2_dlc09_character_abilities_strike_of_tombs`
- Game text: “He whose will transcends death can strike out from beyond the grave, to devastating effect.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc09_character_abilities_strike_of_tombs`)*
- Owners: High Queen Khalida, Tomb King, Tomb Prince
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 90s · 23s · self
- Decision: **implemented (in-melee self - auto, trivial)** — trivial self-buff: Melee Attack +24, Base Weapon Damage +30% (attribute Can Cause Terror — ignored); auto-accepted WITHOUT the questionnaire per standing rule 9 (imbuements/attributes ignored). Implement: when in melee (and not fleeing), cast on self.

**211. Tor's Battle Hymn** — *melee_self, self*
- Keys: `wh3_main_character_abilities_tors_battle_hymn`
- Game text: “"Thunder is strong and lightning is death, with Tor's wrath a flash-bolt takes their breath!"” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_character_abilities_tors_battle_hymn`)*
- Owners: Kostaltyn, Patriarch; unit set(s): ksl_boris_ursus, ksl_martial_lords
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 90s · 25s · self
- Decision: **implemented (in-melee self)** — user-approved in the block-5 questionnaire: activate when in melee and not fleeing, cast on self.

**212. Tormentor Sword** — *melee_enemy, self*
- Keys: `wh_main_weapon_abilities_tormentor_sword`
- Game text: “Those that take a wound from the jagged blade of the Tormentor Sword will not only feel pain - their thoughts will be wracked with terrible omens.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh_main_weapon_abilities_tormentor_sword`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 90s · 9s · self
- Decision: **implemented (in-melee self)** — user-approved in the block-5 questionnaire: activate when in melee and not fleeing, cast on self.

**213. Transfix** — *melee_self, self*
- Keys: `wh2_dlc11_lord_abilities_transfix`
- Game text: “"Look into my eyes and tremble, mortal…"” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc11_lord_abilities_transfix`)*
- Owners: not unit-innate (granted by character skill)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 120s · 26s · self
- Decision: **implemented (in-melee self)** — user-approved in the block-5 questionnaire: activate when in melee and not fleeing, cast on self.

**214. Ultimate Verdict** — *melee_self, self*
- Keys: `wh3_cp1_character_abilities_terrifying_presence`
- Game text: “"No mercy for Cathay's enemies, no redemption for corruption. The road to rebellion always ends with decapitation."” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_cp1_character_abilities_terrifying_presence`)*
- Owners: Taoyan the Merciless
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 120s · 28s · self

**215. Undeath Resurgent** — *melee_self, self*
- Keys: `wh_main_character_abilities_undeath_resurgent`
- Game text: “Arise! Do not falter! Do not crumble!…” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh_main_character_abilities_undeath_resurgent`)*
- Owners: Von Carstein Vampire Lord, Heinrich Kemmler, Vampire Lord
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 90s · 18s · self

**216. Unyielding Defence** — *melee_self, self*
- Keys: `wh3_main_character_abilities_unyielding_defender`
- Game text: “Never give up, never surrender, no matter what happens. Choose death over the way of the craven.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_character_abilities_unyielding_defender`)*
- Owners: not unit-innate (granted by character skill)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self - auto, trivial)** — auto-accepted per standing rule 9 (trivial positive self-buff); implemented in the block-4/5/6 round (harness88; the table now has 189 entries).
- Run stats: cd 90s · 28s · self

**217. Ursun's Claw** — *melee_self, self*
- Keys: `wh3_dlc24_weapon_abilities_ursuns_claw`
- Game text: “The magic of Kislev’s first Khan Queen allows the paragon of Kislev to wield this great glacier-cut sabre seemingly crafted for the hand of a giant!” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc24_weapon_abilities_ursuns_claw`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self - auto, trivial)** — auto-accepted per standing rule 9 (trivial positive self-buff); implemented in the block-4/5/6 round (harness88; the table now has 189 entries).
- Run stats: cd 120s · 17s · self

**218. Van Horstmann's Speculum** — *melee_enemy, self*
- Keys: `wh_main_item_abilities_van_horstmanns_speculum`
- Game text: “Van Horstmann's small magical mirror has the ability to destroy the enemy if only they will look upon its cracked surface...” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh_main_item_abilities_van_horstmanns_speculum`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 90s · 16s · self

**219. Verminous Valour** — *melee_self, self*
- Keys: `wh2_main_character_abilities_verminous_valour`
- Game text: “There is a sense in which the Skaven's natural cowardice can appear to be the very pinnacle of honourable conduct.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_main_character_abilities_verminous_valour`)*
- Owners: Tretch Craventail, Warlord, Queek Headtaker
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 60s · 17s · self

**220. Violent Wind** — *melee_self, self*
- Keys: `wh3_dlc20_unit_abilities_violent_wind`
- Game text: “'Better out than in' is a questionable maxim—particularly for the unfortunates caught in this deadly, reeking draught.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc20_unit_abilities_violent_wind`)*
- Owners: Bilious Thunderguff (Chaos Giant)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 120s · 4s · self · unit

**221. Waaagh!** — *melee_self, self*
- Keys: `wh3_dlc26_unit_abilities_waaagh_in_combat` · `wh_main_character_abilities_waaagh`
- Game text: “Bellowing a war cry into the air, the mighty Waaagh! is unleashed – da boyz echo the terrifying roar in a crescendo of murderous hysteria!” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc26_unit_abilities_waaagh_in_combat`)*
- Owners: not unit-innate (granted by character skill)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 90s · 18s · self

**222. Warp Frenzy** — *melee_self, self*
- Keys: `wh2_dlc16_hero_abilities_warp_frenzy`
- Game text: “When Ghoritch fires up his Warpstone-powered piston-driven claws, everyone within his extensive reach witnesses the true meaning of violence!” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc16_hero_abilities_warp_frenzy`)*
- Owners: Ghoritch
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self - auto, trivial)** — auto-accepted per standing rule 9 (trivial positive self-buff); implemented in the block-4/5/6 round (harness88; the table now has 189 entries).
- Run stats: cd 90s · 29s · self

**223. Warrior's Crest** — *melee_self, self*
- Keys: `wh2_dlc12_lord_abilities_warriors_crest`
- Game text: “It's not just for decoration, you know!” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc12_lord_abilities_warriors_crest`)*
- Owners: Red Crested Skink Chief
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self - auto, trivial)** — auto-accepted per standing rule 9 (trivial positive self-buff); implemented in the block-4/5/6 round (harness88; the table now has 189 entries).
- Run stats: cd 90s · 30s · self

**224. Whirl of Weeping Blades** — *melee_self, self*
- Keys: `wh2_dlc14_weapon_abilities_whirl_of_weeping_blades`
- Game text: “With a poisoned sword in both hands and his own tail, few warriors can survive long against the Deathmaster.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc14_weapon_abilities_whirl_of_weeping_blades`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 120s · 5s · self

**225. Whirlwind of Pleasure** — *melee_self, self*
- Keys: `wh3_dlc27_lord_abilities_whirlwind_of_pleasure`
- Game text: “Whether sinuously squeezing the life out of her thralls or rushing gleefully into the fray, Dechala revels in her feats of pain and misery.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc27_lord_abilities_whirlwind_of_pleasure`)*
- Owners: Dechala, the Denied One
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 120s · 5s · self · lord

**226. Will of the Verminking** — *melee_self, self*
- Keys: `wh3_dlc29_lord_abilities_will_of_the_verminking`
- Game text: “No creature can defy the will of the Verminking.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc29_lord_abilities_will_of_the_verminking`)*
- Owners: Skreech Verminking
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (verminking_wavering)** — user-designed trigger: fire when ANY friendly unit other than the caster is in melee AND wavering within a conservative 25 m (FOURTH.VERMINKING_RANGE_M, the game-data 35 m aura minus a margin); CAST ON SELF; the Glorious-Death safety pattern (closest ally, pre-cast range re-check, skip on drift). Implemented in the block-4/5/6 round (harness88).
- Run stats: cd 120s · 29s · self

**227. Witstealer Sword** — *melee_self, self*
- Keys: `wh3_main_weapon_abilities_witstealer_sword`
- Game text: “One touch from this enchanted blade and the poor fool won't know where they are or why they are here, let alone be able to defend themselves.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_weapon_abilities_witstealer_sword`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self - auto, trivial)** — auto-accepted per standing rule 9 (trivial positive self-buff); implemented in the block-4/5/6 round (harness88; the table now has 189 entries).
- Run stats: cd 120s · 17s · self

**228. Wrath of the Storm** — *melee_self, self*
- Keys: `wh3_main_lord_abilities_wrath_of_the_storm`
- Game text: “Elements thought uncontrollable can be harnessed to do the Dragon's bidding – both to crush their enemies and protect them when in human form.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_lord_abilities_wrath_of_the_storm`)*
- Owners: Miao Ying, the Storm Dragon; unit set(s): wh3_main_cth_cha_storm_dragon_0
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 120s · 32s · self

**229. Wrathful Reaper** — *melee_self, self*
- Keys: `wh3_main_lord_abilities_wrathful_reaper`
- Game text: “Skarbrand runs rampant, twin axes hacking and cleaving until there is no one left to kill.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_lord_abilities_wrathful_reaper`)*
- Owners: Skarbrand the Exiled
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 60s · 18s · self

**230. Wristbands of Black Gold** — *melee_self, self*
- Keys: `wh3_dlc29_item_abilities_wristbands_of_black_gold`
- Game text: “Though seemingly something one might flaunt at a noble soiree, these harden their wearer's form.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc29_item_abilities_wristbands_of_black_gold`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 60s · 22s · self · item

**231. Amulet of Itzl** — *melee_self, self*
- Keys: `wh2_main_item_abilities_amulet_of_itzl`
- Game text: “The amulet explodes into a million crystal shards if the wearer is struck, greatly improving their resistance to damage for a short time.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_main_item_abilities_amulet_of_itzl`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 60s · 18s · self · ×1 uses

**232. Black Lotus** — *melee_self, self*
- Keys: `wh2_main_character_abilities_black_lotus`
- Game text: “This poison contains a powerful narcotic and drives its victims to delusional insanity.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_main_character_abilities_black_lotus`)*
- Owners: Khainite Assassin
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self - auto, trivial)** — auto-accepted per standing rule 9 (trivial positive self-buff); implemented in the block-4/5/6 round (harness88; the table now has 189 entries).
- Run stats: cd 60s · 44s · self · ×1 uses

**233. Burning Rage** — *melee_self, self*
- Keys: `wh3_main_lord_abilities_burning_rage`
- Game text: “The physical manifestation of their endless, furious anger is an explosion of fiery death all around the Blood God's Daemonic servant.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_lord_abilities_burning_rage`)*
- Owners: Daemon Prince, Red Ulgor, Prince of Slaughter, Grand Vomitus, Prince of Buboes, Caress, the Darkling Prince, Zarrivyk, Feathered-Prince (+5 more)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 90s · 7s · self · ×3 uses

**234. Daemon Flask of Ashak** — *melee_self, self*
- Keys: `wh3_dlc23_item_abilities_daemon_flask_of_ashak`
- Game text: “Contained within this infamous iron vessel is a raging daemonic entity of phenomenal power, ready to be unleashed.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc23_item_abilities_daemon_flask_of_ashak`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 120s · 5s · self · ×1 uses

**235. Daemonic Strength** — *melee_self, self*
- Keys: `wh_main_item_abilities_daemonic_strength`
- Game text: “To have the strength of a raging Daemon is to slay in one swipe.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh_main_item_abilities_daemonic_strength`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self - auto, trivial)** — auto-accepted per standing rule 9 (trivial positive self-buff); implemented in the block-4/5/6 round (harness88; the table now has 189 entries).
- Run stats: cd 60s · 22s · self · ×1 uses

**236. Dark Fortune** — *melee_self, self*
- Keys: `wh_main_item_abilities_dark_fortune`
- Game text: “Asavar Kul, the Butcher of Praag, demanded his Champions sup boiled Daemon blood from the Chalice of Chaos, imbuing them with strength and vigour.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh_main_item_abilities_dark_fortune`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 60s · 57s · self · ×1 uses

**237. Dark Venom** — *melee_self, self*
- Keys: `wh2_main_character_abilities_dark_venom`
- Game text: “A victim of Dark Venom knows only a drawn-out and agonising death.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_main_character_abilities_dark_venom`)*
- Owners: Khainite Assassin
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self - auto, trivial)** — auto-accepted per standing rule 9 (trivial positive self-buff); implemented in the block-4/5/6 round (harness88; the table now has 189 entries).
- Run stats: cd 60s · 40s · self · ×1 uses

**238. Defiling Deluge** — *melee_self, self*
- Keys: `wh3_twa08_unit_abilities_defiling_deluge`
- Game text: “By which the Great Unclean One calls down a disgusting shower of putrid yuck to heal themselves and harm those foes unfortunate enough to be caught in it.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_twa08_unit_abilities_defiling_deluge`)*
- Owners: Uncle Furuncle (Great Unclean One)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 120s · 6s · self · ×2 uses

**239. Doom Glaive** — *melee_self, self*
- Keys: `wh3_dlc29_item_abilities_doom_glaive`
- Game text: “Neither size nor stature is an impediment to the butcher who bears this savage polearm on the fields of bloody carnage.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc29_item_abilities_doom_glaive`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self - auto, trivial)** — auto-accepted per standing rule 9 (trivial positive self-buff); implemented in the block-4/5/6 round (harness88; the table now has 189 entries).
- Run stats: cd 120s · 27s · self · ×3 uses

**240. Elixir of Damnation** — *melee_self, self*
- Keys: `wh3_dlc27_item_abilities_elixir_of_damnation`
- Game text: “A force-feeding of Dechala’s hideous poison thrusts her victims into the grip of pain and ecstasy, without the will or wherewithal to oppose her.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc27_item_abilities_elixir_of_damnation`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self - auto, trivial)** — auto-accepted per standing rule 9 (trivial positive self-buff); implemented in the block-4/5/6 round (harness88; the table now has 189 entries).
- Run stats: cd 120s · 19s · self · ×5 uses · item

**241. Eternal Vigour** — *melee_self, self*
- Keys: `wh3_dlc29_character_abilities_eternal_vigour`
- Game text: “It is hard to strike one whose cloak carries them through the veil between worlds.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc29_character_abilities_eternal_vigour`)*
- Owners: Heinrich Kemmler
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 120s · 26s · self · ×2 uses

**242. Fistful of Laurels** — *melee_self, self*
- Keys: `wh3_main_item_abilities_fistful_of_laurels`
- Game text: “Ogres don't believe in declaring their leadership qualities via trinkets, but that doesn't mean they're above robbing the dead if it inspires their forces to push even harder.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_item_abilities_fistful_of_laurels`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 120s · 50s · self · ×2 uses

**243. Groundbreaker** — *melee_self, self*
- Keys: `wh3_main_character_abilities_groundbreaker`
- Game text: “This Ogre is infamous for thudding his club on the ground, making it shake and shatter, and taking the enemy with it.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_character_abilities_groundbreaker`)*
- Owners: not unit-innate (granted by character skill)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 90s · 3s · self · ×3 uses

**244. Mirror (Feint & Riposte)** — *melee_self, self*
- Keys: `wh2_dlc15_unit_abilities_mimic_feint_and_riposte`
- Game text: “Quite literally the cut-and-thrust of the Elven way of battle; every stroke is precisely made and finds its mark perfectly.\\n\\n[[col:magic]]This ability is being mirrored using knowledge gained from a prisoner interrogation in Athel Tamarha.[[/col]]” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc15_unit_abilities_mimic_feint_and_riposte`)*
- Owners: unit set(s): wh2_dlc15_mistwalkers
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 90s · 28s · self · ×2 uses

**245. Mirror (Grand Hammer of Faith)** — *melee_self, self*
- Keys: `wh2_dlc15_unit_abilities_mimic_grand_hammer_of_faith`
- Game text: “Zealotry is another tool to be wielded by the disciplined; an application of ardour and devotion most precisely tuned towards victory!\\n\\n[[col:magic]]This ability is being mirrored using knowledge gained from a prisoner interrogation in Athel Tamarha.[[/col]]” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc15_unit_abilities_mimic_grand_hammer_of_faith`)*
- Owners: unit set(s): wh2_dlc15_mistwalkers
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 90s · 50s · self · ×2 uses

**246. Murderous Exhortations** — *melee_self, self*
- Keys: `wh3_dlc26_lord_abilities_murderous_exhortations`
- Game text: “Just a small taste of what awaits the aspirants in the Brazen Cage can undo the minds and bodies of anyone else.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc26_lord_abilities_murderous_exhortations`)*
- Owners: Bloodspeaker
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 120s · 20s · self · ×3 uses

**247. Oath of Replenishment** — *melee_self, self*
- Keys: `wh2_dlc15_army_abilities_oath_of_replenishment` · `wh2_dlc15_army_abilities_oath_of_replenishment_upgraded`
- Game text: “The Mages of Tor Yvresse work tirelessly to ensure those defending the city are suitably supplied and invigorated to ward off all assailants.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc15_army_abilities_oath_of_replenishment`)*
- Owners: army-bar ability (no unit junction)
- Proposed activation: **When in melee (and not fleeing): cast on self. [army-bar cast]**
- Decision: **skipped (army-bar ability)** — user: “Skip all army bar abilities.” (standing rule 10); army-bar abilities have NO automatic logic.
- Run stats: cd 120s · 21s · self · ×2 uses · army · army bar

**248. Potion of Strength** — *melee_self, self*
- Keys: `wh_main_item_abilities_potion_of_strength`
- Game text: “The sludgy black liquor in this stern glass flask is a Potion of Strength, allowing the drinker to cause devastating damage.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh_main_item_abilities_potion_of_strength`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (in-melee self - auto, trivial)** — auto-accepted per standing rule 9 (trivial positive self-buff); implemented in the block-4/5/6 round (harness88; the table now has 189 entries).
- Run stats: cd 60s · 33s · self · ×1 uses

**249. Potion of Toughness** — *melee_self, self*
- Keys: `wh_main_item_abilities_potion_of_toughness`
- Game text: “Those that consume a Potion of Toughness find their skin hardening as swords and arrows glance off their body, even on parts not covered by armour!” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh_main_item_abilities_potion_of_toughness`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Decision: **implemented (melee_health75)** — user-designed trigger: a one-time activation treated as a heal; fire when the owner is in melee AND its own health is at or below 75% (the shared health read, no second threshold). Implemented in the block-4/5/6 round (harness88).
- Run stats: cd 60s · 21s · self · ×1 uses

**250. Rival Hide Talisman** — *melee_self, self*
- Keys: `wh2_main_item_abilities_rival_hide_talisman`
- Game text: “Wearing the stitched hides of enemies slain through treachery is believed to attract the favour of the Horned Rat.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_main_item_abilities_rival_hide_talisman`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 60s · 31s · self · ×1 uses

**251. Rod of Corruption** — *melee_self, self*
- Keys: `wh2_main_item_abilities_rod_of_corruption`
- Game text: “The flail of Skrolk is a rusted, pitted ball of miasma that spreads poxes as it is swung.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_main_item_abilities_rod_of_corruption`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 120s · 11s · self · ×3 uses

**252. Shanty: First Verse** — *melee_self, self*
- Keys: `wh2_dlc11_army_abilities_shanty_verse_1` · `wh2_dlc11_army_abilities_shanty_verse_1_ai`
- Game text: “"Anchor the tides and slow the moons, becalm the waters for some hidden boons. Break the waves, tame the sea; how big can one beast be?"” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc11_army_abilities_shanty_verse_1`)*
- Owners: army-bar ability (no unit junction)
- Proposed activation: **When in melee (and not fleeing): cast on self. [army-bar cast]**
- Decision: **skipped (army-bar ability)** — user: “Skip all army bar abilities.” (standing rule 10); army-bar abilities have NO automatic logic.
- Run stats: cd 120s · 30s · self · ×1 uses · army · army bar

**253. Shanty: Second Verse** — *melee_self, self*
- Keys: `wh2_dlc11_army_abilities_shanty_verse_2` · `wh2_dlc11_army_abilities_shanty_verse_2_ai`
- Game text: “"Now that we have the ocean so slow, put the sails away and prepare to row; for the monster hunts and its prey should shiver, ever since the Vortex went a-quiver!"” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc11_army_abilities_shanty_verse_2`)*
- Owners: army-bar ability (no unit junction)
- Proposed activation: **When in melee (and not fleeing): cast on self. [army-bar cast]**
- Decision: **skipped (army-bar ability)** — user: “Skip all army bar abilities.” (standing rule 10); army-bar abilities have NO automatic logic.
- Run stats: cd 120s · 30s · self · ×1 uses · army · army bar

**254. Shanty: Third Verse** — *melee_self, self*
- Keys: `wh2_dlc11_army_abilities_shanty_verse_3` · `wh2_dlc11_army_abilities_shanty_verse_3_ai`
- Game text: “"Tattered sails, skull flags, and on the deck, zombies in rags; the beast cares not if you’re living or dead, in its belly is where you’ll head… Yet, all is not lost, the verse is complete, for the song is a rune to bless the Star-metal Harpoon."” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc11_army_abilities_shanty_verse_3`)*
- Owners: army-bar ability (no unit junction)
- Proposed activation: **When in melee (and not fleeing): cast on self. [army-bar cast]**
- Run stats: cd 120s · 30s · self · ×1 uses · army · army bar
- Decision: **skipped (army-bar ability)** — user: “Skip all army bar abilities.” (standing rule 10); no automatic logic.
- Keys: `wh2_dlc11_army_abilities_shanty_verse_3` · `wh2_dlc11_army_abilities_shanty_verse_3_ai`
- Game text: “"Tattered sails, skull flags, and on the deck, zombies in rags; the beast cares not if you’re living or dead, in its belly is where you’ll head… Yet, all is not lost, the verse is complete, for the song is a rune to bless the Star-metal Harpoon."” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc11_army_abilities_shanty_verse_3`)*
- Owners: army-bar ability (no unit junction)
- Proposed activation: **When in melee (and not fleeing): cast on self. [army-bar cast]**
- Run stats: cd 120s · 30s · self · ×1 uses · army · army bar

**255. Skull of Katam** — *melee_self, self*
- Keys: `wh_main_item_abilities_skull_of_katam`
- Game text: “The skull of the late Daemonologist, Katam, continues to jibber in secrets that could drive the listener insane. It knows how to suck the Winds from the enemy.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh_main_item_abilities_skull_of_katam`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 60s · 13s · self · ×1 uses
- Decision: **skipped (magic scope + self-damage)** — user: “Skip - magic-resource + self-damage.” No automatic logic — the magic-resource cost plus the self-damage drawback leave it to the player.

**256. Slayer for Chaos** — *melee_self, self*
- Keys: `wh3_dlc23_item_abilities_slayer_for_chaos`
- Game text: “"Ha! These 'trinkets' gave the Ancestor God Grimnir near immortality – I'm no lesser Dawi than him!"” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc23_item_abilities_slayer_for_chaos`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 120s · 24s · self · ×1 uses
- Decision: **approved (in-melee self)** — user-approved in the questionnaire: activate when in melee and not fleeing, cast on self.

**257. Talisman of Loec** — *melee_self, self*
- Keys: `wh2_main_item_abilities_talisman_of_loec`
- Game text: “Loec the Trickster‘s aid comes at a price. His talisman is strange - a bracelet of two interlocking halves.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_main_item_abilities_talisman_of_loec`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 0s · 67s · self · ×1 uses
- Decision: **approved (in-melee self - auto, trivial)** — auto-accepted WITHOUT the questionnaire per standing rule 9 (trivial self-buff: Base Weapon Damage: +30%; Melee Attack: +24). Implement with the standard in-melee self activation (when in melee and not fleeing, cast on self).
- Keys: `wh2_main_item_abilities_talisman_of_loec`
- Game text: “Loec the Trickster‘s aid comes at a price. His talisman is strange - a bracelet of two interlocking halves.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_main_item_abilities_talisman_of_loec`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 0s · 67s · self · ×1 uses

**258. The Black Gem of Gnar** — *melee_self, self*
- Keys: `wh3_dlc23_item_abilities_black_gem_of_gnar`
- Game text: “A double-edged sword, so to speak, for although this jewel protects its owner from attack, they cannot attack anyone while wearing it either.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc23_item_abilities_black_gem_of_gnar`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 90s · 13s · self · ×3 uses
- Decision: **skipped (revisit)** — user: “Skip for now.”

**259. Thundermace** — *melee_self, self*
- Keys: `wh3_main_weapon_abilities_thundermace`
- Game text: “Awesome crushing power, born of the most violent of elements – the clue is in the name...” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_weapon_abilities_thundermace`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 90s · 3s · self · ×3 uses
- Decision: **skipped (unsuitable: vortex)** — collection-time: unsuitable (vortex); no automatic logic.
- Keys: `wh3_main_weapon_abilities_thundermace`
- Game text: “Awesome crushing power, born of the most violent of elements – the clue is in the name...” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_weapon_abilities_thundermace`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 90s · 3s · self · ×3 uses

**260. Venom Wave** — *melee_self, self*
- Keys: `wh2_dlc09_lord_abilities_venom_wave`
- Game text: “Even if you survive the explosion, a surge of noxious fumes follows in its deadly wake.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc09_lord_abilities_venom_wave`)*
- Owners: High Queen Khalida
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 90s · 3s · self · ×3 uses
- Decision: **skipped (unsuitable: vortex)** — collection-time: unsuitable (vortex); no automatic logic.
- Keys: `wh2_dlc09_lord_abilities_venom_wave`
- Game text: “Even if you survive the explosion, a surge of noxious fumes follows in its deadly wake.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc09_lord_abilities_venom_wave`)*
- Owners: High Queen Khalida
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 90s · 3s · self · ×3 uses

**261. Vial of Troll Blood** — *melee_self, self*
- Keys: `wh_dlc08_item_abilities_vial_of_troll_blood`
- Game text: “Disgusting as it may be, a shot of Troll blood is just the thing to bolster the drinker's courage, causing an unstoppable bloodlust to rise within them.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh_dlc08_item_abilities_vial_of_troll_blood`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 90s · 73s · self · ×1 uses
- Decision: **approved (wavering self)** — user: “Only when wavering” → trigger variant: cast on self when the owner is wavering (no melee arm).

**262. Warpstone Addiction** — *melee_self, self*
- Keys: `wh3_dlc29_lord_abilities_warpstone_addiction`
- Game text: “While Warpstone has unhinged his sanity, it does also have its advantages.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc29_lord_abilities_warpstone_addiction`)*
- Owners: Thanquol
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 120s · 33s · self · ×2 uses
- Decision: **approved (in-melee self)** — user-approved in the questionnaire: activate when in melee and not fleeing, cast on self.

**263. Warrior Familiar** — *melee_self, self*
- Keys: `wh3_dlc27_item_abilities_warrior_familiar`
- Game text: “A warrior familiar accompanies its master and fights to protect them, taking the form of a diminutive Chaos Warrior or tiny monstrous creature.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc27_item_abilities_warrior_familiar`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 90s · 57s · self · ×1 uses
- Decision: **approved (in-melee self - auto, trivial)** — auto-accepted WITHOUT the questionnaire per standing rule 9 (trivial self-buff: Melee Attack: +24; Melee Defence: +24 other source). Implement with the standard in-melee self activation (when in melee and not fleeing, cast on self).
- Keys: `wh3_dlc27_item_abilities_warrior_familiar`
- Game text: “A warrior familiar accompanies its master and fights to protect them, taking the form of a diminutive Chaos Warrior or tiny monstrous creature.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc27_item_abilities_warrior_familiar`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 90s · 57s · self · ×1 uses

**264. Whirlwind of Death** — *melee_self, self*
- Keys: `wh3_dlc25_unit_abilities_whirlwind_of_death` · `wh3_dlc25_unit_abilities_whirlwind_of_death_upgraded`
- Game text: “Dual axe-edges carve through foes, lashing out in a spiral of slaughter, and leaving nought but a bloody mess in their wake.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc25_unit_abilities_whirlwind_of_death`)*
- Owners: Doomseekers; unit set(s): dwf_doomseekers_rank7
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 90s · 6s · self · ×1 uses
- Decision: **skipped (unsuitable: vortex)** — collection-time: unsuitable (vortex); no automatic logic.
- Keys: `wh3_dlc25_unit_abilities_whirlwind_of_death` · `wh3_dlc25_unit_abilities_whirlwind_of_death_upgraded`
- Game text: “Dual axe-edges carve through foes, lashing out in a spiral of slaughter, and leaving nought but a bloody mess in their wake.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc25_unit_abilities_whirlwind_of_death`)*
- Owners: Doomseekers; unit set(s): dwf_doomseekers_rank7
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 90s · 6s · self · ×1 uses

**265. Witchbrew** — *melee_self, self*
- Keys: `wh2_main_character_abilities_witchbrew` · `wh3_dlc24_unit_abilities_witchbrew`
- Game text: “Distilled from the blood of Hag Queens, this evil brew drives imbibers into an ecstasy of destruction.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_main_character_abilities_witchbrew`)*
- Owners: Crone Hellebron, Death Hag, Sisters of the Singing Doom (Witch Elves), Witch Elves
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 90s · 24s · self · ×3 uses
- Decision: **approved (in-melee self)** — user-approved in the questionnaire: activate when in melee and not fleeing, cast on self. (Covers both keys: `wh2_main_character_abilities_witchbrew` + `wh3_dlc24_unit_abilities_witchbrew`.)

**266. World's Edge Armour** — *melee_self, self*
- Keys: `wh2_main_item_abilities_worlds_edge_armour`
- Game text: “Many suits of Dwarfen Gromril have fallen into the clutches of the Skaven. Then they are remade to the ratmen’s liking.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_main_item_abilities_worlds_edge_armour`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 60s · 57s · self · ×1 uses
- Decision: **approved (in-melee self)** — user-approved in the questionnaire: activate when in melee and not fleeing, cast on self.

**267. Wrath of Ptra** — *melee_self, self*
- Keys: `wh2_dlc09_lord_abilities_wrath_of_ptra`
- Game text: “The heavenly fire of Ptra's rage, directed at those who dare stand against his servants.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc09_lord_abilities_wrath_of_ptra`)*
- Owners: Settra the Imperishable; unit set(s): wh3_dlc29_nagash
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 90s · 3s · self · ×3 uses
- Decision: **skipped (unsuitable: vortex)** — collection-time: unsuitable (vortex); no automatic logic.
- Keys: `wh2_dlc09_lord_abilities_wrath_of_ptra`
- Game text: “The heavenly fire of Ptra's rage, directed at those who dare stand against his servants.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc09_lord_abilities_wrath_of_ptra`)*
- Owners: Settra the Imperishable; unit set(s): wh3_dlc29_nagash
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 90s · 3s · self · ×3 uses

**268. Znarkharja's Ward** — *melee_self, self*
- Keys: `wh3_dlc24_hero_abilities_znarkharjas_ward`
- Game text: “A folk witch's ward is a powerful protection, meant to tend all manner of wound and ailment.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc24_hero_abilities_znarkharjas_ward`)*
- Owners: Hag Witch (Death)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 90s · 26s · self · ×2 uses
- Decision: **approved (in-melee self)** — user-approved in the questionnaire: activate when in melee and not fleeing, cast on self.

**269. Ark of Sotek** — *melee_self, self*
- Keys: `wh2_dlc12_unit_abilities_ark_of_sotek`
- Game text: “Sotek's crawling, swarming allies surround the bearer, affording them further might and protection in the struggle to come.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc12_unit_abilities_ark_of_sotek`)*
- Owners: Bastiladon (Ark of Sotek)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 90s · 26s · self · wind-up 1s
- Decision: **skipped (unsuitable: vortex)** — collection-time: unsuitable (vortex); no automatic logic.
- Keys: `wh2_dlc12_unit_abilities_ark_of_sotek`
- Game text: “Sotek's crawling, swarming allies surround the bearer, affording them further might and protection in the struggle to come.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc12_unit_abilities_ark_of_sotek`)*
- Owners: Bastiladon (Ark of Sotek)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 90s · 26s · self · wind-up 1s

**270. Battle Howl** — *melee_self, self*
- Keys: `wh3_dlc29_ability_bound_prayer_battle_howl` · `wh3_dlc29_spell_bound_prayer_battle_howl`
- Game text: “Is it a prayer to war, or a primal acclamation to the Wolf-God? It amounts to all and the same.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc29_ability_bound_prayer_battle_howl`)*
- Owners: Hounds of Ulricsberg (Hunting Hounds), Priest of Ulric
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 60s · 15s · self · wind-up 0.5s · unit
- Decision: **skipped (unsuitable: movement)** — collection-time: unsuitable (movement); no automatic logic.
- Keys: `wh3_dlc29_ability_bound_prayer_battle_howl` · `wh3_dlc29_spell_bound_prayer_battle_howl`
- Game text: “Is it a prayer to war, or a primal acclamation to the Wolf-God? It amounts to all and the same.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc29_ability_bound_prayer_battle_howl`)*
- Owners: Hounds of Ulricsberg (Hunting Hounds), Priest of Ulric
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 60s · 15s · self · wind-up 0.5s · unit

**271. Battle of Wills** — *melee_self, self*
- Keys: `wh3_dlc29_unit_abilities_battle_of_wills`
- Game text: “Those who ferry the Queen's exquisite throne once longed for her too...” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc29_unit_abilities_battle_of_wills`)*
- Owners: Lahmian Vampire Lord, Vampire Lord, Neferata, Coven Throne; unit set(s): mp_cap_unit_vmp_veh_coven_throne
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 120s · 20s · self · wind-up 5s
- Decision: **approved (in-melee self)** — user-approved in the questionnaire: activate when in melee and not fleeing, cast on self.

**272. Call of Tor** — *melee_self, self*
- Keys: `wh3_twa07_spell_bound_call_of_tor`
- Game text: “All fear the wrath of the storm-god Tor, striking foes down in a barrage of divine lightning!” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_twa07_spell_bound_call_of_tor`)*
- Owners: Oath-Brothers of Tor (War Bear Riders)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 90s · 7s · self · wind-up 1s · bound
- Decision: **skipped (unsuitable: bombardment/ranged)** — collection-time: unsuitable (bombardment/ranged); no automatic logic.
- Keys: `wh3_twa07_spell_bound_call_of_tor`
- Game text: “All fear the wrath of the storm-god Tor, striking foes down in a barrage of divine lightning!” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_twa07_spell_bound_call_of_tor`)*
- Owners: Oath-Brothers of Tor (War Bear Riders)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 90s · 7s · self · wind-up 1s · bound

**273. Celestial Sweep** — *melee_self, self*
- Keys: `wh3_dlc24_lord_abilities_celestial_sweep`
- Game text: “Such a sweeping maelstrom of energy can cut through a crowd of bodies, leaving blood and devastation in its wake.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc24_lord_abilities_celestial_sweep`)*
- Owners: Celestial General
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 120s · 4s · self · wind-up 0.1s
- Decision: **skipped (unsuitable: vortex)** — collection-time: unsuitable (vortex); no automatic logic.
- Keys: `wh3_dlc24_lord_abilities_celestial_sweep`
- Game text: “Such a sweeping maelstrom of energy can cut through a crowd of bodies, leaving blood and devastation in its wake.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc24_lord_abilities_celestial_sweep`)*
- Owners: Celestial General
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 120s · 4s · self · wind-up 0.1s

**274. Destruction** — *melee_self, self*
- Keys: `wh3_dlc29_spell_bound_prayer_destruction`
- Game text: “To hunt and stalk, one needs time. To kill, one need not waste it.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc29_spell_bound_prayer_destruction`)*
- Owners: Priest of Ulric
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 120s · 3s · self · wind-up 0.5s
- Decision: **skipped (unsuitable: vortex)** — collection-time: unsuitable (vortex); no automatic logic.
- Keys: `wh3_dlc29_spell_bound_prayer_destruction`
- Game text: “To hunt and stalk, one needs time. To kill, one need not waste it.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc29_spell_bound_prayer_destruction`)*
- Owners: Priest of Ulric
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 120s · 3s · self · wind-up 0.5s

**275. Ferocious Battle Howl** — *melee_self, self*
- Keys: `wh3_dlc29_spell_bound_prayer_ferocious_battle_howl`
- Game text: “What was once a full-throated clamour turns into the crush and press of bodies gone feral with bloodlust.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc29_spell_bound_prayer_ferocious_battle_howl`)*
- Owners: Emil Valgeir
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 60s · 15s · self · wind-up 0.5s · bound
- Decision: **approved (charge only)** — user: “Charge only” → NEW trigger variant: activate in the charge window only (no melee arm), cast on self.

**276. Ferocious Destruction** — *melee_self, self*
- Keys: `wh3_dlc29_spell_bound_prayer_ferocious_destruction`
- Game text: “As the the enemy's blood gushes hot, the blood still in their veins freezes in a terrible premonition of death.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc29_spell_bound_prayer_ferocious_destruction`)*
- Owners: Emil Valgeir
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 120s · 3s · self · wind-up 0.5s
- Decision: **skipped (unsuitable: vortex)** — collection-time: unsuitable (vortex); no automatic logic.
- Keys: `wh3_dlc29_spell_bound_prayer_ferocious_destruction`
- Game text: “As the the enemy's blood gushes hot, the blood still in their veins freezes in a terrible premonition of death.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc29_spell_bound_prayer_ferocious_destruction`)*
- Owners: Emil Valgeir
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 120s · 3s · self · wind-up 0.5s

**277. Ferocious Fury of Ulric** — *melee_self, self*
- Keys: `wh3_dlc29_spell_bound_prayer_ferocious_fury_of_ulric`
- Game text: “The scent of blood is palpable. As is the scent of fear.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc29_spell_bound_prayer_ferocious_fury_of_ulric`)*
- Owners: Emil Valgeir
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 120s · 25s · self · wind-up 0.5s · bound
- Decision: **approved (wavering self)** — user: “Only when wavering (like Vial of Troll Blood)” → trigger variant: cast on self when the owner is wavering (no melee arm).

**278. Ferocious Winter’s Chill** — *melee_enemy, self*
- Keys: `wh3_dlc29_spell_bound_prayer_ferocious_winters_chill`
- Game text: “When the foe's hand is stayed and their resolve stuttered, then their throat is bared – and so are the Wolf's fangs.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc29_spell_bound_prayer_ferocious_winters_chill`)*
- Owners: Emil Valgeir
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 90s · 20s · self · wind-up 0.5s · bound
- Decision: **approved (in-melee self)** — user-approved in the questionnaire: activate when in melee and not fleeing, cast on self.

**279. Flame Incarnate** — *melee_self, self*
- Keys: `wh3_main_character_abilities_flame_incarnate`
- Game text: “By which a vortex of fire surrounds the user; surprisingly, this improves their skills considerably.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_character_abilities_flame_incarnate`)*
- Owners: Firebelly
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 90s · 24s · self · wind-up 1s
- Decision: **approved (in-melee self)** — user-approved in the questionnaire: activate when in melee and not fleeing, cast on self.

**280. Formless Horror** — *melee_self, self*
- Keys: `wh3_dlc24_lord_abilities_formless_horror` · `wh3_dlc24_lord_abilities_formless_horror_quest_battle`
- Game text: “Features shift and morph, skin and cloth ripples, until the facsimile form is flawless.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc24_lord_abilities_formless_horror`)*
- Owners: The Changeling
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 60s · 5s · self · wind-up 5s
- Decision: **skipped (revisit)** — user: “Skip for now.” NOTE: its **Effects** line is `<unknown>` in the review doc (`WH3_blocks_7-8-9_review.md` §280, line 154 — “Effects: <unknown> (other source)”); the effect must be RECONSTRUCTED from the game data (`wh3_dlc24_lord_abilities_formless_horror` + `wh3_dlc24_lord_abilities_formless_horror_quest_battle`) before this item can ever be decided.

**281. Fury of Ulric** — *melee_self, self*
- Keys: `wh3_dlc29_spell_bound_prayer_fury_of_ulric`
- Game text: “When Ulric leads the pack, there is no contest – the quarry can do nothing but run.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc29_spell_bound_prayer_fury_of_ulric`)*
- Owners: Priest of Ulric
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 90s · 25s · self · wind-up 0.5s · bound
- Decision: **approved (wavering self-or-ally in range)** — user: “When wavering (self or ally in range)” → NEW trigger variant: cast on self when the owner or an ally in range is wavering.

**282. Grand Soulfire** — *melee_self, self*
- Keys: `wh_dlc04_spell_bound_soulfire_upgraded`
- Game text: “A battle prayer that bathes the Warrior Priest in white, holy fire, sears Sigmar’s foes but leaves the supplicant unharmed.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh_dlc04_spell_bound_soulfire_upgraded`)*
- Owners: Arch Lector, Volkmar the Grim
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 120s · 7s · self · wind-up 1s · bound
- Decision: **skipped (unsuitable: bombardment/ranged)** — collection-time: unsuitable (bombardment/ranged); no automatic logic.
- Keys: `wh_dlc04_spell_bound_soulfire_upgraded`
- Game text: “A battle prayer that bathes the Warrior Priest in white, holy fire, sears Sigmar’s foes but leaves the supplicant unharmed.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh_dlc04_spell_bound_soulfire_upgraded`)*
- Owners: Arch Lector, Volkmar the Grim
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 120s · 7s · self · wind-up 1s · bound

**283. Immovable Bulwark** — *melee_self, self*
- Keys: `wh3_dlc26_unit_abilities_immovable_bulwark`
- Game text: “"Nuffin' ain't gettin' past us."” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc26_unit_abilities_immovable_bulwark`)*
- Owners: Black Orcs, Krimson Killerz (Black Orcs); unit set(s): wh2_dlc11_grn_all_orc_infantry
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 1s · -1s · self · wind-up 1s
- Decision: **approved (in-melee self)** — user-approved in the questionnaire: activate when in melee and not fleeing, cast on self.

**284. Kill for Khorne!** — *melee_self, self*
- Keys: `wh3_dlc26_character_abilities_kill_for_khorne`
- Game text: “"For Khorne, my dear microcephalic abomination? Oh, well then, verily, you must kill!"\\n – The last words of a nameless, intestineless Arabyan Plenipotentiary” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc26_character_abilities_kill_for_khorne`)*
- Owners: Scyla Anfingrimm
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 120s · 1s · self · wind-up 3s
- Decision: **skipped (unsuitable: vortex)** — collection-time: unsuitable (vortex); no automatic logic.
- Keys: `wh3_dlc26_character_abilities_kill_for_khorne`
- Game text: “"For Khorne, my dear microcephalic abomination? Oh, well then, verily, you must kill!"\\n – The last words of a nameless, intestineless Arabyan Plenipotentiary” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc26_character_abilities_kill_for_khorne`)*
- Owners: Scyla Anfingrimm
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 120s · 1s · self · wind-up 3s

**285. Primeval Roar** — *melee_self, self*
- Keys: `wh2_dlc17_unit_abilities_primeval_roar`
- Game text: “All Lizardmen are roused at the wailing cry of the Troglodon, its eerie call stirring their savagery.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc17_unit_abilities_primeval_roar`)*
- Owners: The Pale Death (Feral Troglodon)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 60s · 31s · self · wind-up 4.5s
- Decision: **approved (in-melee self)** — user-approved in the questionnaire: activate when in melee and not fleeing, cast on self.

**286. Rune of Doom** — *melee_self, self*
- Keys: `wh2_dlc17_lord_abilities_rune_of_doom`
- Game text: “Etched upon the Anvil of Doom is a rune that can resonate with deep vibrations felt by both friend and foe.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc17_lord_abilities_rune_of_doom`)*
- Owners: Thorek Ironbrow
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 120s · 16s · self · wind-up 5s
- Decision: **approved (in-melee self)** — user-approved in the questionnaire: activate when in melee and not fleeing, cast on self.

**287. Sonic Boom** — *melee_self, self*
- Keys: `wh3_main_daemon_head_abilities_sonic_boom`
- Game text: “A colossal, ear-splitting burst of sound will hurl the foe across the battlefield, leaving them disorientated – assuming of course they survive the experience!” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_daemon_head_abilities_sonic_boom`)*
- Owners: Daemon Prince, Red Ulgor, Prince of Slaughter, Grand Vomitus, Prince of Buboes, Caress, the Darkling Prince, Zarrivyk, Feathered-Prince (+4 more); unit set(s): slaanesh_characters
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 90s · 6s · self · wind-up 3s
- Decision: **skipped (unsuitable: vortex)** — collection-time: unsuitable (vortex); no automatic logic.
- Keys: `wh3_main_daemon_head_abilities_sonic_boom`
- Game text: “A colossal, ear-splitting burst of sound will hurl the foe across the battlefield, leaving them disorientated – assuming of course they survive the experience!” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_daemon_head_abilities_sonic_boom`)*
- Owners: Daemon Prince, Red Ulgor, Prince of Slaughter, Grand Vomitus, Prince of Buboes, Caress, the Darkling Prince, Zarrivyk, Feathered-Prince (+4 more); unit set(s): slaanesh_characters
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 90s · 6s · self · wind-up 3s

**288. Soulfire** — *melee_self, self*
- Keys: `wh_main_spell_bound_soulfire`
- Game text: “A battle prayer that bathes the Warrior Priest in white, holy fire, sears Sigmar’s foes but leaves the supplicant unharmed.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh_main_spell_bound_soulfire`)*
- Owners: Warrior Priest
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 90s · 7s · self · wind-up 1s · bound
- Decision: **skipped (unsuitable: bombardment/ranged)** — collection-time: unsuitable (bombardment/ranged); no automatic logic.
- Keys: `wh_main_spell_bound_soulfire`
- Game text: “A battle prayer that bathes the Warrior Priest in white, holy fire, sears Sigmar’s foes but leaves the supplicant unharmed.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh_main_spell_bound_soulfire`)*
- Owners: Warrior Priest
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 90s · 7s · self · wind-up 1s · bound

**289. The Hammer of Harry** — *melee_self, self*
- Keys: `wh3_pro11_weapon_abilities_the_hammer_of_harry`
- Game text: “As if driven by an unstoppable force, Harry’s hammer is blessed by the gods to hurl back the bodies and souls of those he strikes.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_pro11_weapon_abilities_the_hammer_of_harry`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 120s · 5s · self · wind-up 3s
- Decision: **skipped (unsuitable: vortex)** — collection-time: unsuitable (vortex); no automatic logic.
- Keys: `wh3_pro11_weapon_abilities_the_hammer_of_harry`
- Game text: “As if driven by an unstoppable force, Harry’s hammer is blessed by the gods to hurl back the bodies and souls of those he strikes.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_pro11_weapon_abilities_the_hammer_of_harry`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 120s · 5s · self · wind-up 3s

**290. The Shadow's Coil** — *melee_self, self*
- Keys: `wh_dlc05_unit_abilities_the_shadows_coil`
- Game text: “The wending and twisting of the Wardancers hardens their spirits and their bodies against would-be attackers.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh_dlc05_unit_abilities_the_shadows_coil`)*
- Owners: Bladesingers, Wardancers, Loec's Tricksters (Wardancers – Asrai Spears); unit set(s): wh2_twa02_wef_glade_captain_unmounted
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 1s · -1s · self · wind-up 1s
- Decision: **approved (in-melee self)** — user-approved in the questionnaire: activate when in melee and not fleeing, cast on self.

**291. Transformation of the Dragon** — *melee_self, self*
- Keys: `wh3_dlc24_lord_abilities_jade_dragon_dragon_form` · `wh3_main_lord_abilities_iron_dragon_dragon_form` · `wh3_main_lord_abilities_storm_dragon_dragon_form`
- Game text: “Yuan Bo has the innate power to transmogrify from human form to Dragon and back again at will, and often at the most opportune moments.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc24_lord_abilities_jade_dragon_dragon_form`)*
- Owners: Yuan Bo, the Jade Dragon, Zhao Ming, the Iron Dragon, Miao Ying, the Storm Dragon
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 120s · 5s · self · wind-up 5s
- Decision: **skipped (revisit)** — user: “Skip for now.” (Applies to all three keys: `wh3_dlc24_lord_abilities_jade_dragon_dragon_form`, `wh3_main_lord_abilities_iron_dragon_dragon_form`, `wh3_main_lord_abilities_storm_dragon_dragon_form`.)

**292. Unstoppable Choppas** — *melee_self, self*
- Keys: `wh3_dlc26_unit_abilities_unstoppable_choppas`
- Game text: “When Orcs are determined to cleave something in half, very few things can stop them from doing so.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc26_unit_abilities_unstoppable_choppas`)*
- Owners: Krimson Killerz (Black Orcs), Black Orcs (Great Weapons); unit set(s): wh2_dlc11_grn_all_orc_infantry
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 1s · -1s · self · wind-up 1s
- Decision: **approved (in-melee self)** — user-approved in the questionnaire: activate when in melee and not fleeing, cast on self.

**293. Winter’s Chill** — *melee_enemy, self*
- Keys: `wh3_dlc29_ability_bound_prayer_winters_chill` · `wh3_dlc29_spell_bound_prayer_winters_chill`
- Game text: “Under such eyes, one's martial resolve withers – for behind them is the Wolf, daring you to lay a hand upon him.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc29_ability_bound_prayer_winters_chill`)*
- Owners: Order of the Axe (Teutogen Guard), Priest of Ulric
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 90s · 20s · self · wind-up 0.5s · unit
- Decision: **approved (in-melee self)** — user-approved in the questionnaire: activate when in melee and not fleeing, cast on self. (Covers both keys: `wh3_dlc29_ability_bound_prayer_winters_chill` + `wh3_dlc29_spell_bound_prayer_winters_chill`.)

**294. Alakanash, the Staff of Power** — *melee_self, self*
- Keys: `wh3_dlc29_item_abilities_alakanash_the_staff_of_power`
- Game text: “A magical artefact of immeasurable worth, it has changed many unworthy masters during the centuries before Nagash's return. Now it is finally in the hands of its creator.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc29_item_abilities_alakanash_the_staff_of_power`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 120s · 21s · self · ×3 uses · wind-up 1s · item
- Decision: **skipped (unsuitable: vortex)** — collection-time: unsuitable (vortex); no automatic logic.
- Keys: `wh3_dlc29_item_abilities_alakanash_the_staff_of_power`
- Game text: “A magical artefact of immeasurable worth, it has changed many unworthy masters during the centuries before Nagash's return. Now it is finally in the hands of its creator.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc29_item_abilities_alakanash_the_staff_of_power`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 120s · 21s · self · ×3 uses · wind-up 1s · item

**295. Bangers & Smash** — *melee_self, self*
- Keys: `wh2_dlc15_character_abilities_sausage_busta`
- Game text: “These sausages have quite the kick – thrown at an enemy, they violently rupture in a flesh-mangling implosion.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc15_character_abilities_sausage_busta`)*
- Owners: not unit-innate (granted by character skill)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 120s · 36s · self · ×3 uses · wind-up 1s
- Decision: **approved (charge or wavering)** — user: “When charging or wavering” → NEW trigger variant: activate in the charge window OR when wavering, cast on self.

**296. Cellular Instability** — *melee_self, self*
- Keys: `wh2_dlc16_unit_abilities_cellular_instability`
- Game text: “A constantly spiking fever is a symptom of a botched augmentation, but the explosive side effects make the subject a potentially effective weapon.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc16_unit_abilities_cellular_instability`)*
- Owners: not unit-innate (granted by character skill)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 90s · 6s · self · ×1 uses · wind-up 1s
- Decision: **skipped (unsuitable: vortex)** — collection-time: unsuitable (vortex); no automatic logic.
- Keys: `wh2_dlc16_unit_abilities_cellular_instability`
- Game text: “A constantly spiking fever is a symptom of a botched augmentation, but the explosive side effects make the subject a potentially effective weapon.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc16_unit_abilities_cellular_instability`)*
- Owners: not unit-innate (granted by character skill)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 90s · 6s · self · ×1 uses · wind-up 1s

**297. Curse of Years** — *melee_self, self*
- Keys: `wh3_dlc29_spell_bound_curse_of_years`
- Game text: “The Wizard spits out an ancient curse, causing his enemies to age at an incredible rate - their hair turning white and skin shrivelling up.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc29_spell_bound_curse_of_years`)*
- Owners: unit set(s): mp_cap_unit_vmp_inf_lahmian_handmaidens_death
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 47s · 35s · self · ×2 uses · wind-up 1s
- Decision: **approved (in-melee self - auto, trivial)** — auto-accepted WITHOUT the questionnaire per standing rule 9 (trivial self-buff: Imbuement: wh3_dlc29_unit_contact_curse_of_years other source). Implement with the standard in-melee self activation (when in melee and not fleeing, cast on self).
- Keys: `wh3_dlc29_spell_bound_curse_of_years`
- Game text: “The Wizard spits out an ancient curse, causing his enemies to age at an incredible rate - their hair turning white and skin shrivelling up.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc29_spell_bound_curse_of_years`)*
- Owners: unit set(s): mp_cap_unit_vmp_inf_lahmian_handmaidens_death
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 47s · 35s · self · ×2 uses · wind-up 1s

**298. Death Frenzy** — *melee_self, self*
- Keys: `wh2_dlc16_spell_bound_death_frenzy`
- Game text: “Gesticulating wildly, the caster gifts an allied unit with a rabid, frothing need to attack and consume the foe!” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc16_spell_bound_death_frenzy`)*
- Owners: not unit-innate (granted by character skill)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 90s · 28s · self · ×1 uses · wind-up 3s
- Decision: **approved (in-melee self)** — user-approved: activate when in melee and not fleeing, cast on self. (block 8)

**299. Dragonhorn** — *melee_self, self*
- Keys: `wh2_dlc15_lord_abilities_dragonhorn`
- Game text: “A single blast on the 'Dragonhorn', forged in the fire of Draugnir's flaming breath, causes the foe to shrink in terror, for they know what surely follows…” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc15_lord_abilities_dragonhorn`)*
- Owners: Imrik
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 120s · 16s · self · ×3 uses · wind-up 6s
- Decision: **approved (in-melee self)** — user-approved: activate when in melee and not fleeing, cast on self. (block 8)

**300. Eruption** — *melee_self, self*
- Keys: `wh3_main_character_abilities_eruption`
- Game text: “"That's torn it – now 'e's all angry like. I'd run if I were yoo… BOOM!"” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_character_abilities_eruption`)*
- Owners: Firebelly
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 120s · 4s · self · ×1 uses · wind-up 1s
- Decision: **skipped (unsuitable: vortex)** — collection-time: unsuitable (vortex); no automatic logic.
- Keys: `wh3_main_character_abilities_eruption`
- Game text: “"That's torn it – now 'e's all angry like. I'd run if I were yoo… BOOM!"” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_character_abilities_eruption`)*
- Owners: Firebelly
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 120s · 4s · self · ×1 uses · wind-up 1s

**301. Glacial Blast** — *melee_self, self*
- Keys: `wh3_main_character_abilities_glacial_blast`
- Game text: “This eldritch explosion propels lacerating shards of ice outwards, devastating anyone caught in its deadly squall.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_character_abilities_glacial_blast`)*
- Owners: Ice Witch (Tempest), Frost Maiden (Tempest)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 90s · 4s · self · ×3 uses · wind-up 3s
- Decision: **skipped (unsuitable: vortex)** — collection-time: unsuitable (vortex); no automatic logic.
- Keys: `wh3_main_character_abilities_glacial_blast`
- Game text: “This eldritch explosion propels lacerating shards of ice outwards, devastating anyone caught in its deadly squall.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_character_abilities_glacial_blast`)*
- Owners: Ice Witch (Tempest), Frost Maiden (Tempest)
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 90s · 4s · self · ×3 uses · wind-up 3s

**302. Greater Faith Bastion** — *melee_self, self*
- Keys: `wh_dlc06_quest_abilities_grand_faiths_bastion`
- Game text: “Swiftly invoking the protection of Sigmar or Ulric blesses the implorer with a shield of godly faith, should they prove worthy.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh_dlc06_quest_abilities_grand_faiths_bastion`)*
- Owners: Arch Lector
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 0s · 60s · self · ×1 uses · wind-up 3s
- Decision: **approved (in-melee self)** — user-approved: activate when in melee and not fleeing, cast on self. (block 8)
- Removed: **2026-10-17** — `excluded (not in wheel: boss-only unit)`; its only grant path is `wh_dlc06_emp_cha_arch_lector_0_boss` (land_abil.tsv), a quest-battle boss variant. It was implemented and is REMOVED from the mod's `ABILITIES` table. See §10.3.

**303. Okkam's Mindrazor** — *melee_self, self*
- Keys: `wh3_dlc29_spell_bound_okkams_mindrazor`
- Game text: “The supernatural solution is often the best; weapons materialise in hands, allowing them to slice through flesh, soul, and consciousness.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc29_spell_bound_okkams_mindrazor`)*
- Owners: Lahmian Handmaidens (Shadows); unit set(s): mp_cap_unit_vmp_inf_lahmian_handmaidens_shadow
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 46s · 32s · self · ×2 uses · wind-up 1s
- Decision: **approved (in-melee self - auto, trivial)** — auto-accepted WITHOUT the questionnaire per standing rule 9 (trivial self-buff: Imbuement:  Magical Attacks; Base Weapon Damage: +50%; Armour-Piercing Weapon Damage: +50%). Implement with the standard in-melee self activation (when in melee and not fleeing, cast on self).
- Keys: `wh3_dlc29_spell_bound_okkams_mindrazor`
- Game text: “The supernatural solution is often the best; weapons materialise in hands, allowing them to slice through flesh, soul, and consciousness.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc29_spell_bound_okkams_mindrazor`)*
- Owners: Lahmian Handmaidens (Shadows); unit set(s): mp_cap_unit_vmp_inf_lahmian_handmaidens_shadow
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 46s · 32s · self · ×2 uses · wind-up 1s

**304. Splode da Big 'Un!** — *melee_self, self*
- Keys: `wh3_dlc26_unit_abilities_splode_da_big_one`
- Game text: “[[i]]"When nothin' but a massive 'splosion’ll do, get da Shamans to blow up da biggest Squig yoov got."[[/i]]” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc26_unit_abilities_splode_da_big_one`)*
- Owners: unit set(s): grn_mon_colossal_squig
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 0s · 7s · self · ×1 uses · wind-up 0.4s
- Decision: **skipped (unsuitable: vortex)** — collection-time: unsuitable (vortex); no automatic logic.
- Keys: `wh3_dlc26_unit_abilities_splode_da_big_one`
- Game text: “[[i]]"When nothin' but a massive 'splosion’ll do, get da Shamans to blow up da biggest Squig yoov got."[[/i]]” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc26_unit_abilities_splode_da_big_one`)*
- Owners: unit set(s): grn_mon_colossal_squig
- Proposed activation: **When in melee (and not fleeing): cast on self.**
- Run stats: cd 0s · 7s · self · ×1 uses · wind-up 0.4s


### Tier 2 — self-or-ally form, castable on self today (30 items)

**305. Cash Cascade** — *melee_self, friend/self*
- Keys: `wh3_dlc26_character_abilities_cash_cascade`
- Game text: “"Right, there's a bonus in it for tha one that does the most creative killin'…"” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc26_character_abilities_cash_cascade`)*
- Owners: Ogre Paymaster, Greasus Goldtooth
- Proposed activation: **When in melee: cast on self (self-cast allowed; nearest-ally picker later).**
- Run stats: cd 120s · 30s · friend/self
- Decision: **approved (charge and in-melee)** — user chose the combined trigger (like Fangspike, §2 #68): activate in the charge window OR in melee (and not fleeing), cast on self.

**306. Empowering Shrooms** — *melee_self, friend/self*
- Keys: `wh3_dlc26_character_abilities_empowering_shrooms`
- Game text: “The fact that Squigs and gobbos love them should serve as a warning to the more inherently sensible races.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc26_character_abilities_empowering_shrooms`)*
- Owners: Night Goblin Big Boss
- Proposed activation: **When in melee: cast on self (self-cast allowed; nearest-ally picker later).**
- Run stats: cd 90s · 35s · friend/self
- Decision: **approved (in-melee self)** — user-approved: activate when in melee and not fleeing, cast on self. (block 8)

**307. Enchanted Metallurgy** — *melee_self, friend/self*
- Keys: `wh3_main_character_abilities_enchanted_metallurgy`
- Game text: “The science by which metals are extracted from their ores can be charged by magic and given purpose in war to devastating effect.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_character_abilities_enchanted_metallurgy`)*
- Owners: Alchemist; unit set(s): wh3_main_cth_cha_alchemist_0
- Proposed activation: **When in melee: cast on self (self-cast allowed; nearest-ally picker later).**
- Run stats: cd 60s · 12s · friend/self
- Decision: **approved (melee self-or-ally / shooting ally in range)** — NEW two-part trigger; user: “When self or ally in range in melee. When ally in range is shooting.” → in melee, cast on the owner or an ally in range; when an ally in range is shooting, cast on that ally. **RESEARCH COMPLETE (harness89): the shooting half is NOT built** — the battle API exposes no per-unit is-firing / is-shooting read (is_under_missile_attack is the unit RECEIVING fire; current_target / ammo_left / missile_range prove nothing about firing NOW; the flags.tsv vocabulary is a data-table construct, not a Lua read), so no proxy was invented. **The MELEE self-or-ally half is IMPLEMENTED (harness89):** fire when the owner is in melee OR any friendly unit other than the caster is in melee within the conservative 25 m `FOURTH.METALLURGY_RANGE_M` (game-data 35 m aura); cast on self; closest ally, pre-cast gap re-check, skip on drift.

**308. Enchanted Metallurgy: Flaming** — *melee_self, friend/self*
- Keys: `wh3_main_character_abilities_enchanted_metallurgy_flaming`
- Game text: “The science by which metals are extracted from their ores can be charged by magic and given purpose in war to devastating effect.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_character_abilities_enchanted_metallurgy_flaming`)*
- Owners: not unit-innate (granted by character skill)
- Proposed activation: **When in melee: cast on self (self-cast allowed; nearest-ally picker later).**
- Run stats: cd 90s · 14s · friend/self
- Decision: **approved (melee self-or-ally / shooting ally in range)** — same as #307 (Enchanted Metallurgy): melee self-or-ally half IMPLEMENTED (harness89); shooting half NOT built (no API is-firing predicate).

**309. Enchanted Metallurgy: Piercing** — *melee_self, friend/self*
- Keys: `wh3_main_character_abilities_enchanted_metallurgy_piercing`
- Game text: “The science by which metals are extracted from their ores can be charged by magic and given purpose in war to devastating effect.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_character_abilities_enchanted_metallurgy_piercing`)*
- Owners: not unit-innate (granted by character skill)
- Proposed activation: **When in melee: cast on self (self-cast allowed; nearest-ally picker later).**
- Run stats: cd 90s · 14s · friend/self
- Decision: **approved (melee self-or-ally / shooting ally in range)** — same as #307 (Enchanted Metallurgy): melee self-or-ally half IMPLEMENTED (harness89); shooting half NOT built (no API is-firing predicate).

**310. Enchanted Metallurgy: Poison** — *melee_self, friend/self*
- Keys: `wh3_main_character_abilities_enchanted_metallurgy_poison`
- Game text: “The science by which metals are extracted from their ores can be charged by magic and given purpose in war to devastating effect.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_character_abilities_enchanted_metallurgy_poison`)*
- Owners: not unit-innate (granted by character skill)
- Proposed activation: **When in melee: cast on self (self-cast allowed; nearest-ally picker later).**
- Run stats: cd 90s · 12s · friend/self
- Decision: **approved (melee self-or-ally / shooting ally in range)** — same as #307 (Enchanted Metallurgy): melee self-or-ally half IMPLEMENTED (harness89); shooting half NOT built (no API is-firing predicate).

**311. Horn of Khorne** — *melee_self, friend/self*
- Keys: `wh3_main_army_abilities_horn_of_khorne`
- Game text: “An extra horn bursts forth from the warriors' foreheads, increasing the possibility that attacks will be successful, and in turn the likelihood of the kill.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_army_abilities_horn_of_khorne`)*
- Owners: army of: Blood Keepers, Challengers of Khorne, Blooded Wanderers
- Proposed activation: **When in melee: cast on self (self-cast allowed; nearest-ally picker later). [army-bar cast]**
- Run stats: cd 90s · 31s · friend/self · army · army bar
- Decision: **skipped (army-bar ability)** — user: “Skip all army bar abilities.” (standing rule 10); no automatic logic.
- Keys: `wh3_main_army_abilities_horn_of_khorne`
- Game text: “An extra horn bursts forth from the warriors' foreheads, increasing the possibility that attacks will be successful, and in turn the likelihood of the kill.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_army_abilities_horn_of_khorne`)*
- Owners: army of: Blood Keepers, Challengers of Khorne, Blooded Wanderers
- Proposed activation: **When in melee: cast on self (self-cast allowed; nearest-ally picker later). [army-bar cast]**
- Run stats: cd 90s · 31s · friend/self · army · army bar

**312. Massacre** — *melee_self, friend/self*
- Keys: `wh3_main_prisoners_massacre`
- Game text: “When there’s fresh meat in the offing, Ogres are driven to even cruder levels of bludgeonous slaughter.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_prisoners_massacre`)*
- Owners: army of: The Maneaters, Blood Guzzlers, Bloodmaw
- Proposed activation: **When in melee: cast on self (self-cast allowed; nearest-ally picker later). [army-bar cast]**
- Run stats: cd 90s · 17s · friend/self · army · army bar
- Decision: **approved (in-melee self)** — user-approved: activate when in melee and not fleeing, cast on self. (block 8)
- Removed: **2026-10-17** — `excluded (not in wheel: army ability - removed from mod per user decision 2026-10-17)`; it was implemented but sits OUTSIDE the single in-wheel rule. See §10.2.

**313. Master of Alchemy** — *melee_self, friend/self*
- Keys: `wh3_main_lord_abilities_master_of_alchemy`
- Game text: “Base metals may be transmuted and transformed, so that they might strike harder and better at the Celestial Emperor's enemies.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_lord_abilities_master_of_alchemy`)*
- Owners: Zhao Ming, the Iron Dragon; unit set(s): wh3_main_cth_cha_iron_dragon_0
- Proposed activation: **When in melee: cast on self (self-cast allowed; nearest-ally picker later).**
- Run stats: cd 90s · 20s · friend/self
- Decision: **approved (melee self-or-ally / shooting ally in range)** — NEW two-part trigger; user: “Same as the Metallurgies (melee self-or-ally / shooting ally)”. Same rule as #307; the shooting half awaits an API predicate.

**314. Master of Alchemy: Flaming** — *melee_self, friend/self*
- Keys: `wh3_main_lord_abilities_master_of_alchemy_flaming`
- Game text: “Base metals may be transmuted and transformed, so that they might strike harder and better at the Celestial Emperor's enemies.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_lord_abilities_master_of_alchemy_flaming`)*
- Owners: unit set(s): wh3_main_cth_cha_iron_dragon_0
- Proposed activation: **When in melee: cast on self (self-cast allowed; nearest-ally picker later).**
- Run stats: cd 120s · 16s · friend/self
- Decision: **approved (melee self-or-ally / shooting ally in range)** — same as #313 (Master of Alchemy).

**315. Master of Alchemy: Piercing** — *melee_self, friend/self*
- Keys: `wh3_main_lord_abilities_master_of_alchemy_piercing`
- Game text: “Base metals may be transmuted and transformed, so that they might strike harder and better at the Celestial Emperor's enemies.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_lord_abilities_master_of_alchemy_piercing`)*
- Owners: unit set(s): wh3_main_cth_cha_iron_dragon_0
- Proposed activation: **When in melee: cast on self (self-cast allowed; nearest-ally picker later).**
- Run stats: cd 120s · 19s · friend/self
- Decision: **approved (melee self-or-ally / shooting ally in range)** — same as #313 (Master of Alchemy).

**316. Master of Alchemy: Poison** — *melee_self, friend/self*
- Keys: `wh3_main_lord_abilities_master_of_alchemy_poison`
- Game text: “Base metals may be transmuted and transformed, so that they might strike harder and better at the Celestial Emperor's enemies.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_lord_abilities_master_of_alchemy_poison`)*
- Owners: unit set(s): wh3_main_cth_cha_iron_dragon_0
- Proposed activation: **When in melee: cast on self (self-cast allowed; nearest-ally picker later).**
- Run stats: cd 120s · 18s · friend/self
- Decision: **approved (melee self-or-ally / shooting ally in range)** — same as #313 (Master of Alchemy).

**317. Spite of Da Bad Moon** — *melee_self, friend/self*
- Keys: `wh_dlc06_lord_abilities_spite_of_da_bad_moon`
- Game text: “Da Bad Moon offers heightened pugnacity to its weird and disgusting worshippers, spurring them to dish out even more pain.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh_dlc06_lord_abilities_spite_of_da_bad_moon`)*
- Owners: Night Goblin Warboss, Skarsnik
- Proposed activation: **When in melee: cast on self (self-cast allowed; nearest-ally picker later).**
- Run stats: cd 90s · 20s · friend/self
- Decision: **approved (in-melee self)** — user-approved: activate when in melee and not fleeing, cast on self. (block 8)

**318. Twilight Horn II** — *melee_self, friend/self*
- Keys: `wh2_dlc16_item_abilities_twilight_horn_ii`
- Game text: “No purer sound is there than a single note from this great horn, capable of emboldening the faint of heart and rousing the timid.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc16_item_abilities_twilight_horn_ii`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee: cast on self (self-cast allowed; nearest-ally picker later).**
- Run stats: cd 90s · 36s · friend/self
- Decision: **skipped (unsuitable: movement)** — collection-time: unsuitable (movement); no automatic logic.
- Keys: `wh2_dlc16_item_abilities_twilight_horn_ii`
- Game text: “No purer sound is there than a single note from this great horn, capable of emboldening the faint of heart and rousing the timid.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc16_item_abilities_twilight_horn_ii`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee: cast on self (self-cast allowed; nearest-ally picker later).**
- Run stats: cd 90s · 36s · friend/self

**319. "Stay Here, I'll Get Help!"** — *melee_self, friend/self*
- Keys: `wh2_dlc09_character_abilities_stay_here_ill_get_help`
- Game text: “It's not running away. It's knowing when and where to be to secure the best advantage.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc09_character_abilities_stay_here_ill_get_help`)*
- Owners: Tretch Craventail
- Proposed activation: **When in melee: cast on self (self-cast allowed; nearest-ally picker later).**
- Run stats: cd 90s · 35s · friend/self · ×3 uses
- Decision: **approved (wavering ally in range)** — NEW trigger; user: “If ally in range is wavering.” → cast on an ally in range that is wavering; **NO melee requirement (the ally need not be in melee)**. Same evaluator shape as Will of the Verminking (closest ally in range, conservative range, drift re-check).

**320. Armour of Contempt** — *melee_self, friend/self*
- Keys: `wh3_dlc23_army_abilities_armour_of_contempt`
- Game text: “A protective shell that makes those within it appear to be made of ash and stone, increasing their defensive capabilities, including immunity to counter-enchantment at the foe's hands.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc23_army_abilities_armour_of_contempt`)*
- Owners: army-bar ability (no unit junction)
- Proposed activation: **When in melee: cast on self (self-cast allowed; nearest-ally picker later). [army-bar cast]**
- Run stats: cd 120s · 26s · friend/self · ×3 uses · army · army bar
- Decision: **skipped (army-bar ability)** — user: “Skip all army bar abilities.” (standing rule 10); no automatic logic.
- Keys: `wh3_dlc23_army_abilities_armour_of_contempt`
- Game text: “A protective shell that makes those within it appear to be made of ash and stone, increasing their defensive capabilities, including immunity to counter-enchantment at the foe's hands.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc23_army_abilities_armour_of_contempt`)*
- Owners: army-bar ability (no unit junction)
- Proposed activation: **When in melee: cast on self (self-cast allowed; nearest-ally picker later). [army-bar cast]**
- Run stats: cd 120s · 26s · friend/self · ×3 uses · army · army bar

**321. Breath of Hatred** — *melee_self, friend/self*
- Keys: `wh3_dlc23_bound_abilities_breath_of_hatred` · `wh3_dlc23_character_abilities_breath_of_hatred`
- Game text: “Allies are infected with his malice and imbued with an even greater capacity for savage cruelty, for those choice moments when only even greater evil and destruction will do.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc23_bound_abilities_breath_of_hatred`)*
- Owners: not unit-innate — bound ability (item/skill-granted)
- Proposed activation: **When in melee: cast on self (self-cast allowed; nearest-ally picker later).**
- Decision: **approved (in-melee self)** — user-approved: activate when in melee and not fleeing, cast on self. (block 8)
- Run stats: cd 90s · 31s · friend/self · ×3 uses · bound

**322. Master Rune of Oath & Steel** — *melee_self, friend/self*
- Keys: `wh_dlc06_rune_abilities_master_rune_of_oath_and_steel`
- Game text: “Armour inscribed with the Rune of Oath & Steel will not bend or buckle.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh_dlc06_rune_abilities_master_rune_of_oath_and_steel`)*
- Owners: not unit-innate — rune ability (Dwarf runesmiths/lords)
- Proposed activation: **When in melee: cast on self (self-cast allowed; nearest-ally picker later).**
- Decision: **approved (in-melee self)** — user-approved: activate when in melee and not fleeing, cast on self. (block 8)
- Run stats: cd 180s · 44s · friend/self · wind-up 3s · rune

**323. Master Rune of Speed** — *melee_self, friend/self*
- Keys: `wh2_dlc17_rune_abilities_master_rune_of_speed`
- Game text: “This rune enhances its bearer’s awareness and quickness so that he moves more fluidly, taking faster opponents by surprise.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc17_rune_abilities_master_rune_of_speed`)*
- Owners: not unit-innate — rune ability (Dwarf runesmiths/lords)
- Proposed activation: **When in melee: cast on self (self-cast allowed; nearest-ally picker later).**
- Decision: **approved (in-melee self)** — user-approved: activate when in melee and not fleeing, cast on self. (block 8)
- Run stats: cd 180s · 40s · friend/self · wind-up 3s · rune

**324. Rune of Oath & Steel** — *melee_self, friend/self*
- Keys: `wh_main_rune_abilities_rune_of_oath_and_steel`
- Game text: “Armour inscribed with the Rune of Oath & Steel will not bend or buckle.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh_main_rune_abilities_rune_of_oath_and_steel`)*
- Owners: Runelord, Runesmith, Throni Ironbrow, Thorek Ironbrow; lore/group: Runic Magic
- Proposed activation: **When in melee: cast on self (self-cast allowed; nearest-ally picker later).**
- Decision: **approved (in-melee self)** — user-approved: activate when in melee and not fleeing, cast on self. (block 8)
- Run stats: cd 120s · 44s · friend/self · wind-up 3s · rune

**325. Rune of Speed** — *melee_self, friend/self*
- Keys: `wh2_dlc17_rune_abilities_rune_of_speed`
- Game text: “This rune enhances its bearer’s awareness and quickness so that he moves more fluidly, taking faster opponents by surprise.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc17_rune_abilities_rune_of_speed`)*
- Owners: Runelord, Runesmith, Throni Ironbrow, Thorek Ironbrow; lore/group: Runic Magic
- Proposed activation: **When in melee: cast on self (self-cast allowed; nearest-ally picker later).**
- Decision: **approved (in-melee self)** — user-approved: activate when in melee and not fleeing, cast on self. (block 8)
- Run stats: cd 120s · 30s · friend/self · wind-up 3s · rune

**326. Birona's Timewarp** — *melee_self, friend/self*
- Keys: `wh_main_spell_bound_bironas_timewarp`
- Game text: “The Wizard infuses his allies with Light Magic, freeing them from the passage of time and speeding up their actions.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh_main_spell_bound_bironas_timewarp`)*
- Owners: Spirit of Tepok (Coatl)
- Proposed activation: **When in melee: cast on self (self-cast allowed; nearest-ally picker later).**
- Decision: **approved (charge and in-melee)** — user chose charge and in melee; activate in the charge window OR in melee (and not fleeing), cast on self — mirrors Fangspike (§2 #68) / Heart Piercing (§2 #91).
- Run stats: cd 47s · 50s · friend/self · ×1 uses · wind-up 5s · bound

**327. Gate of Khorne** — *melee_enemy, friend/self*
- Keys: `wh3_main_character_abilities_gate_of_khorne`
- Game text: “Khorne's loyal Cultist forces open the gate to allow His vicious, chosen Bloodletters to surge through and consume the inauspicious enemy.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_character_abilities_gate_of_khorne`)*
- Owners: Cultist of Khorne
- Proposed activation: **When in melee: cast on self (self-cast allowed; nearest-ally picker later).**
- Run stats: cd 120s · 10s · friend/self · ×1 uses · wind-up 5s
- Decision: **implemented (enemy_ground_melee)** — **round 101 (2026-10-17):** the user chose the trigger, verbatim: *"The trigger will place it on the closest enemy that is in range of the ability and fighting."* Among enemies within the ability's own 70% bound (35 m of 50 m, `FOURTH.ENEMY_CAST_R50`) keep those FIGHTING (in melee), pick the CLOSEST, and place the summon on THAT ENEMY'S ground with the ground form, a fresh caster controller and a fresh enemy, a hold and a pre-cast re-check. Its own reason names the enemy type and the real distance; the cast target is never the caster.
- Keys: `wh3_main_character_abilities_gate_of_khorne`
- Game text: “Khorne's loyal Cultist forces open the gate to allow His vicious, chosen Bloodletters to surge through and consume the inauspicious enemy.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_character_abilities_gate_of_khorne`)*
- Owners: Cultist of Khorne
- Proposed activation: **When in melee: cast on self (self-cast allowed; nearest-ally picker later).**
- Run stats: cd 120s · 10s · friend/self · ×1 uses · wind-up 5s

**328. Gate of Nurgle** — *melee_enemy, friend/self*
- Keys: `wh3_main_character_abilities_gate_of_nurgle`
- Game text: “The Cultist hauls open the gate to allow yet more foul, droning Plaguebearers to shuffle into existence to surround and infect the enemy.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_character_abilities_gate_of_nurgle`)*
- Owners: Cultist of Nurgle
- Proposed activation: **When in melee: cast on self (self-cast allowed; nearest-ally picker later).**
- Run stats: cd 120s · 10s · friend/self · ×1 uses · wind-up 5s
- Decision: **skipped (unsuitable: spawned/ranged)** — collection-time: unsuitable (spawned/ranged); no automatic logic.
- Keys: `wh3_main_character_abilities_gate_of_nurgle`
- Game text: “The Cultist hauls open the gate to allow yet more foul, droning Plaguebearers to shuffle into existence to surround and infect the enemy.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_character_abilities_gate_of_nurgle`)*
- Owners: Cultist of Nurgle
- Proposed activation: **When in melee: cast on self (self-cast allowed; nearest-ally picker later).**
- Run stats: cd 120s · 10s · friend/self · ×1 uses · wind-up 5s

**329. Gate of Slaanesh** — *melee_enemy, friend/self*
- Keys: `wh3_main_character_abilities_gate_of_slaanesh`
- Game text: “The Cultist holds the gate open so alluring Daemonettes can surge through and have at the foe, as if starved of sustenance for an eternity prior.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_character_abilities_gate_of_slaanesh`)*
- Owners: Cultist of Slaanesh
- Proposed activation: **When in melee: cast on self (self-cast allowed; nearest-ally picker later).**
- Run stats: cd 120s · 10s · friend/self · ×1 uses · wind-up 5s
- Decision: **skipped (unsuitable: spawned/ranged)** — collection-time: unsuitable (spawned/ranged); no automatic logic.
- Keys: `wh3_main_character_abilities_gate_of_slaanesh`
- Game text: “The Cultist holds the gate open so alluring Daemonettes can surge through and have at the foe, as if starved of sustenance for an eternity prior.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_character_abilities_gate_of_slaanesh`)*
- Owners: Cultist of Slaanesh
- Proposed activation: **When in melee: cast on self (self-cast allowed; nearest-ally picker later).**
- Run stats: cd 120s · 10s · friend/self · ×1 uses · wind-up 5s

**330. Greater Gate of Khorne** — *melee_enemy, friend/self*
- Keys: `wh3_main_cataclysm_khorne_greater_gate_of_khorne` · `wh3_main_character_abilities_greater_gate_of_khorne`
- Game text: “The raging winds draw forth a Bloodthirster to savage the ill-omened opponents of the Murder Lord.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_cataclysm_khorne_greater_gate_of_khorne`)*
- Owners: not unit-innate (granted by character skill)
- Proposed activation: **When in melee: cast on self (self-cast allowed; nearest-ally picker later).**
- Run stats: cd 0s · 10s · friend/self · ×1 uses · wind-up 5s
- Decision: **skipped (unsuitable: spawned/ranged)** — collection-time: unsuitable (spawned/ranged); no automatic logic.
- Keys: `wh3_main_cataclysm_khorne_greater_gate_of_khorne` · `wh3_main_character_abilities_greater_gate_of_khorne`
- Game text: “The raging winds draw forth a Bloodthirster to savage the ill-omened opponents of the Murder Lord.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_cataclysm_khorne_greater_gate_of_khorne`)*
- Owners: not unit-innate (granted by character skill)
- Proposed activation: **When in melee: cast on self (self-cast allowed; nearest-ally picker later).**
- Run stats: cd 0s · 10s · friend/self · ×1 uses · wind-up 5s

**331. Greater Gate of Nurgle** — *melee_enemy, friend/self*
- Keys: `wh3_main_character_abilities_greater_gate_of_nurgle`
- Game text: “The Cultist holds open Nurgle's gate while a Great Unclean One emerges from the crevice to lay waste to his foes.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_character_abilities_greater_gate_of_nurgle`)*
- Owners: unit set(s): wh3_main_nur_cha_cultist_0
- Proposed activation: **When in melee: cast on self (self-cast allowed; nearest-ally picker later).**
- Run stats: cd 120s · 10s · friend/self · ×1 uses · wind-up 5s
- Decision: **skipped (unsuitable: spawned/ranged)** — collection-time: unsuitable (spawned/ranged); no automatic logic.
- Keys: `wh3_main_character_abilities_greater_gate_of_nurgle`
- Game text: “The Cultist holds open Nurgle's gate while a Great Unclean One emerges from the crevice to lay waste to his foes.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_character_abilities_greater_gate_of_nurgle`)*
- Owners: unit set(s): wh3_main_nur_cha_cultist_0
- Proposed activation: **When in melee: cast on self (self-cast allowed; nearest-ally picker later).**
- Run stats: cd 120s · 10s · friend/self · ×1 uses · wind-up 5s

**332. Greater Gate of Slaanesh** — *melee_enemy, friend/self*
- Keys: `wh3_main_character_abilities_greater_gate_of_slaanesh`
- Game text: “The Cultist forces open the gate, allowing a Keeper of Secrets to bound through and savage the uncomprehending enemy.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_character_abilities_greater_gate_of_slaanesh`)*
- Owners: not unit-innate (granted by character skill)
- Proposed activation: **When in melee: cast on self (self-cast allowed; nearest-ally picker later).**
- Run stats: cd 120s · 10s · friend/self · ×1 uses · wind-up 5s
- Decision: **skipped (unsuitable: spawned/ranged)** — collection-time: unsuitable (spawned/ranged); no automatic logic.
- Keys: `wh3_main_character_abilities_greater_gate_of_slaanesh`
- Game text: “The Cultist forces open the gate, allowing a Keeper of Secrets to bound through and savage the uncomprehending enemy.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_character_abilities_greater_gate_of_slaanesh`)*
- Owners: not unit-innate (granted by character skill)
- Proposed activation: **When in melee: cast on self (self-cast allowed; nearest-ally picker later).**
- Run stats: cd 120s · 10s · friend/self · ×1 uses · wind-up 5s

**333. Greater Gate of Tzeentch** — *melee_enemy, friend/self*
- Keys: `wh3_main_character_abilities_greater_gate_of_tzeentch`
- Game text: “The Cultist prises open the aperture, enabling a Lord of Change to enter reality and level great hope and towering ambition at the unsuspecting enemy.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_character_abilities_greater_gate_of_tzeentch`)*
- Owners: Cultist of Tzeentch
- Proposed activation: **When in melee: cast on self (self-cast allowed; nearest-ally picker later).**
- Run stats: cd 120s · 10s · friend/self · ×1 uses · wind-up 5s
- Decision: **skipped (unsuitable: spawned/ranged)** — collection-time: unsuitable (spawned/ranged); no automatic logic.
- Keys: `wh3_main_character_abilities_greater_gate_of_tzeentch`
- Game text: “The Cultist prises open the aperture, enabling a Lord of Change to enter reality and level great hope and towering ambition at the unsuspecting enemy.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_character_abilities_greater_gate_of_tzeentch`)*
- Owners: Cultist of Tzeentch
- Proposed activation: **When in melee: cast on self (self-cast allowed; nearest-ally picker later).**
- Run stats: cd 120s · 10s · friend/self · ×1 uses · wind-up 5s

**334. The Tallyman's Blades** — *melee_enemy, friend/self*
- Keys: `wh3_dlc25_character_abilities_tallymans_blades` · `wh3_dlc25_character_abilities_tallymans_blades_2`
- Game text: “The greatest of Plaguebearers are chosen by the Tallyman and summoned to the battlefield to assist his putrid cause.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc25_character_abilities_tallymans_blades`)*
- Owners: Epidemius
- Proposed activation: **When in melee: cast on self (self-cast allowed; nearest-ally picker later).**
- Run stats: cd 120s · 10s · friend/self · ×1 uses · wind-up 5s
- Decision: **skipped (unsuitable: spawned/ranged)** — collection-time: unsuitable (spawned/ranged); no automatic logic.
- Keys: `wh3_dlc25_character_abilities_tallymans_blades` · `wh3_dlc25_character_abilities_tallymans_blades_2`
- Game text: “The greatest of Plaguebearers are chosen by the Tallyman and summoned to the battlefield to assist his putrid cause.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc25_character_abilities_tallymans_blades`)*
- Owners: Epidemius
- Proposed activation: **When in melee: cast on self (self-cast allowed; nearest-ally picker later).**
- Run stats: cd 120s · 10s · friend/self · ×1 uses · wind-up 5s


### Tier 3 — ground form, cast at own feet (existing ground path) (19 items)

**335. From the Shadows** — *melee_self, ground*
- Keys: `wh2_dlc14_character_abilities_from_the_shadows`
- Game text: “With almost un-Skaven-like focus, Snikch moves unseen through the battlefield until the moment of murderous truth.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc14_character_abilities_from_the_shadows`)*
- Owners: not unit-innate (granted by character skill)
- Proposed activation: **When in melee: cast at own feet (existing ground-cast path).**
- Decision: **rejected (stealth/escape effect)** — user: “No automatic logic (stealth/escape effect)”.
- Run stats: cd 90s · 58s · ground

**336. Lord of Grand Cathay** — *melee_self, ground*
- Keys: `wh3_dlc24_lord_abilities_lord_of_grand_cathay`
- Game text: “When their noble Lord speaks, the men of Cathay listen, burning every inspiring word into their hearts to carry it with them into battle.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc24_lord_abilities_lord_of_grand_cathay`)*
- Owners: Celestial General
- Proposed activation: **When in melee: cast at own feet (existing ground-cast path).**
- Decision: **approved (in-melee self)** — user-approved in the questionnaire: when in melee and not fleeing, cast at own feet (existing ground-cast path).
- Run stats: cd 120s · 16s · ground

**337. Shield of the Old Ones** — *melee_self, ground*
- Keys: `wh2_main_character_abilities_shield_of_the_old_ones`
- Game text: “The resilience of the Old Ones is channelled into an energy barrier that protects its users from the full brunt of magical attacks against them.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_main_character_abilities_shield_of_the_old_ones`)*
- Owners: Slann Mage-Priest (Beasts), Slann Mage-Priest (Death), Slann Mage-Priest (Fire), Slann Mage-Priest (Life), Slann Mage-Priest (Metal) (+6 more)
- Proposed activation: **When in melee: cast at own feet (existing ground-cast path).**
- Decision: **approved (in-melee self)** — user-approved in the questionnaire: when in melee and not fleeing, cast at own feet (existing ground-cast path).
- Run stats: cd 90s · 17s · ground

**338. Supreme Shield of the Old Ones** — *melee_self, ground*
- Keys: `wh2_dlc12_character_abilities_supreme_shield_of_the_old_ones`
- Game text: “More than just a shield, this one channels the visceral power of the Old Ones to protect its bearer from magical attack.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc12_character_abilities_supreme_shield_of_the_old_ones`)*
- Owners: Lord Kroak
- Proposed activation: **When in melee: cast at own feet (existing ground-cast path).**
- Decision: **approved (in-melee self)** — user-approved in the questionnaire: when in melee and not fleeing, cast at own feet (existing ground-cast path).
- Run stats: cd 120s · 18s · ground

**339. Gaze of Khaine** — *melee_self, ground*
- Keys: `wh2_dlc10_lord_abilities_gaze_of_khaine`
- Game text: “Those who fall under the glare of Hellebron share her lust and rage.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc10_lord_abilities_gaze_of_khaine`)*
- Owners: Crone Hellebron
- Proposed activation: **When in melee: cast at own feet (existing ground-cast path).**
- Decision: **approved (in-melee self)** — user-approved in the questionnaire despite the Rampage! flag (standing rule 7: rampage decided case by case); when in melee and not fleeing, cast at own feet (existing ground-cast path).
- Run stats: cd 90s · 28s · ground · ×3 uses

**340. Mors Clanstone** — *melee_self, ground*
- Keys: `wh2_main_army_abilities_mors_clanstone`
- Game text: “On the battlefield, Clan Mors' sacred Warpstones instil their upstart warriors with even greater stamina and skill.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_main_army_abilities_mors_clanstone`)*
- Owners: army-bar ability (no unit junction)
- Proposed activation: **When in melee: cast at own feet (existing ground-cast path). [army-bar cast]**
- Run stats: cd 120s · 28s · ground · ×3 uses · army · army bar
- Decision: **skipped (army-bar ability)** — user: “Skip all army bar abilities.” (standing rule 10); no automatic logic.
- Keys: `wh2_main_army_abilities_mors_clanstone`
- Game text: “On the battlefield, Clan Mors' sacred Warpstones instil their upstart warriors with even greater stamina and skill.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_main_army_abilities_mors_clanstone`)*
- Owners: army-bar ability (no unit junction)
- Proposed activation: **When in melee: cast at own feet (existing ground-cast path). [army-bar cast]**
- Run stats: cd 120s · 28s · ground · ×3 uses · army · army bar

**341. Pestilens Clanstone** — *melee_self, ground*
- Keys: `wh2_main_army_abilities_pestilens_clanstone`
- Game text: “The Plague Monks use their sacred Warpstone to increase the potency of the vile plagues and virulent diseases that are their stock in trade.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_main_army_abilities_pestilens_clanstone`)*
- Owners: army-bar ability (no unit junction)
- Proposed activation: **When in melee: cast at own feet (existing ground-cast path). [army-bar cast]**
- Run stats: cd 120s · 75s · ground · ×3 uses · army · army bar
- Decision: **skipped (army-bar ability)** — user: “Skip all army bar abilities.” (standing rule 10); no automatic logic.
- Keys: `wh2_main_army_abilities_pestilens_clanstone`
- Game text: “The Plague Monks use their sacred Warpstone to increase the potency of the vile plagues and virulent diseases that are their stock in trade.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_main_army_abilities_pestilens_clanstone`)*
- Owners: army-bar ability (no unit junction)
- Proposed activation: **When in melee: cast at own feet (existing ground-cast path). [army-bar cast]**
- Run stats: cd 120s · 75s · ground · ×3 uses · army · army bar

**342. Rictus Clanstone** — *melee_self, ground*
- Keys: `wh2_dlc09_army_abilities_rictus_clanstone`
- Game text: “Clan Rictus' sacred Warpstones capitalise on the grim, vicious determination of its warriors to take on all comers and win.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc09_army_abilities_rictus_clanstone`)*
- Owners: army-bar ability (no unit junction)
- Proposed activation: **When in melee: cast at own feet (existing ground-cast path). [army-bar cast]**
- Run stats: cd 120s · 48s · ground · ×3 uses · army · army bar
- Decision: **skipped (army-bar ability)** — user: “Skip all army bar abilities.” (standing rule 10); no automatic logic.
- Keys: `wh2_dlc09_army_abilities_rictus_clanstone`
- Game text: “Clan Rictus' sacred Warpstones capitalise on the grim, vicious determination of its warriors to take on all comers and win.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc09_army_abilities_rictus_clanstone`)*
- Owners: army-bar ability (no unit junction)
- Proposed activation: **When in melee: cast at own feet (existing ground-cast path). [army-bar cast]**
- Run stats: cd 120s · 48s · ground · ×3 uses · army · army bar

**343. Star of Avelorn** — *melee_self, ground*
- Keys: `wh2_dlc10_item_abilities_star_of_avelorn`
- Game text: “A diadem of ithilmar with a radiant gem set within it, said to be a star plucked from the heavens.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc10_item_abilities_star_of_avelorn`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee: cast at own feet (existing ground-cast path).**
- Decision: **approved (health<=75, no melee gate)** — user: “When below 75% health. No need to use in melee as it has no melee effects as the Potion of Toughness”. Cast on self when own health ≤ 75%, no melee gate — same health-only evaluator as Ghoul King of Ushoran.
- Run stats: cd 120s · 27s · ground · ×2 uses

**344. The Liber Mortis** — *melee_self, ground*
- Keys: `wh2_dlc09_lord_abilities_the_liber_mortis`
- Game text: “One of the fabled nine Books of Nagash, this tome is one of the most potent sources of Necromantic magic in existence.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc09_lord_abilities_the_liber_mortis`)*
- Owners: Arkhan the Black; unit set(s): cha_arkhan
- Proposed activation: **When in melee: cast at own feet (existing ground-cast path).**
- Decision: **approved (in-melee self)** — user-approved in the questionnaire: when in melee and not fleeing, cast at own feet (existing ground-cast path).
- Run stats: cd 90s · 15s · ground · ×3 uses

**345. Gulyas** — *melee_self, ground*
- Keys: `wh3_dlc24_lord_abilities_gulyas`
- Game text: “Never doubt the healing power of a tasty mushroom goulash; the fungal spores alone work wonders for the soul.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc24_lord_abilities_gulyas`)*
- Owners: Mother Ostankya
- Proposed activation: **When in melee: cast at own feet (existing ground-cast path).**
- Decision: **approved (health<=75, no melee gate)** — user chose “Below 75% health (no melee gate)”. Cast on self when own health ≤ 75%, no melee gate — same health-only evaluator as Ghoul King of Ushoran and Star of Avelorn.
- Run stats: cd 120s · 23s · ground · wind-up 3s

**346. Mirror of Knowledge** — *melee_enemy, ground*
- Keys: `wh3_dlc24_item_abilities_mirror_of_knowledge`
- Game text: “"The mind is quicker than the eye. Your thoughts... are mine now."” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc24_item_abilities_mirror_of_knowledge`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee: cast at own feet (existing ground-cast path).**
- Decision: **skipped (revisit)** — user: “Skip for now” (revisit later).
- Run stats: cd 37s · 40s · ground · wind-up 3s

**347. Ancestral Rune of Grungni** — *melee_self, ground*
- Keys: `wh2_dlc17_army_abilities_ancestral_rune_of_grungni`
- Game text: “Grungni’s rune resonates with the fury of the Ancestor God himself, inspiring the smiting of foes and valour at arms.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc17_army_abilities_ancestral_rune_of_grungni`)*
- Owners: not unit-innate — rune ability (Dwarf runesmiths/lords)
- Proposed activation: **When in melee: cast at own feet (existing ground-cast path). [army-bar cast]**
- Run stats: cd 120s · 35s · ground · ×3 uses · wind-up 5s · army · army bar
- Decision: **skipped (army-bar ability)** — user: “Skip all army bar abilities.” (standing rule 10); no automatic logic.
- Keys: `wh2_dlc17_army_abilities_ancestral_rune_of_grungni`
- Game text: “Grungni’s rune resonates with the fury of the Ancestor God himself, inspiring the smiting of foes and valour at arms.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc17_army_abilities_ancestral_rune_of_grungni`)*
- Owners: not unit-innate — rune ability (Dwarf runesmiths/lords)
- Proposed activation: **When in melee: cast at own feet (existing ground-cast path). [army-bar cast]**
- Run stats: cd 120s · 35s · ground · ×3 uses · wind-up 5s · army · army bar

**348. Basking in Our Flame** — *melee_self, ground*
- Keys: `wh3_dlc27_army_abilities_eternal_dance_tempo_3_needful_caress`
- Game text: “Towards the end, we shall grow bold in our newfound sturdiness. Corrosive gusts and the crazed writhing of sharp, poisonous things will only serve to fan our flames.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc27_army_abilities_eternal_dance_tempo_3_needful_caress`)*
- Owners: army-bar ability (no unit junction)
- Proposed activation: **When in melee: cast at own feet (existing ground-cast path). [army-bar cast]**
- Run stats: cd 120s · 36s · ground · ×2 uses · wind-up 2s · army · army bar
- Decision: **skipped (army-bar ability)** — user: “Skip all army bar abilities.” (standing rule 10); no automatic logic.
- Keys: `wh3_dlc27_army_abilities_eternal_dance_tempo_3_needful_caress`
- Game text: “Towards the end, we shall grow bold in our newfound sturdiness. Corrosive gusts and the crazed writhing of sharp, poisonous things will only serve to fan our flames.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc27_army_abilities_eternal_dance_tempo_3_needful_caress`)*
- Owners: army-bar ability (no unit junction)
- Proposed activation: **When in melee: cast at own feet (existing ground-cast path). [army-bar cast]**
- Run stats: cd 120s · 36s · ground · ×2 uses · wind-up 2s · army · army bar

**349. Fog of the Damned** — *melee_enemy, ground*
- Keys: `wh3_dlc29_bound_deep_fog_of_the_damned`
- Game text: “"They'll never know how many we are in this fog… Attack!"” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc29_bound_deep_fog_of_the_damned`)*
- Owners: unit set(s): nag_mourngul_haunter_banshee
- Proposed activation: **When in melee: cast at own feet (existing ground-cast path).**
- Decision: **skipped (revisit)** — user: “Skip for now” (revisit later).
- Run stats: cd 44s · 35s · ground · ×2 uses · wind-up 3s · bound

**350. The Airless Fires** — *melee_self, ground*
- Keys: `wh3_dlc27_army_abilities_eternal_dance_tempo_3_revelry_and_madness`
- Game text: “When there is nothing left to feed any fire, one will keep burning still, made of what is left of us – the children of Chaos – and we will dance across the void to set it ablaze.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc27_army_abilities_eternal_dance_tempo_3_revelry_and_madness`)*
- Owners: army-bar ability (no unit junction)
- Proposed activation: **When in melee: cast at own feet (existing ground-cast path). [army-bar cast]**
- Run stats: cd 120s · 48s · ground · ×1 uses · wind-up 3s · army · army bar
- Decision: **skipped (army-bar ability)** — user: “Skip all army bar abilities.” (standing rule 10); no automatic logic.
- Keys: `wh3_dlc27_army_abilities_eternal_dance_tempo_3_revelry_and_madness`
- Game text: “When there is nothing left to feed any fire, one will keep burning still, made of what is left of us – the children of Chaos – and we will dance across the void to set it ablaze.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc27_army_abilities_eternal_dance_tempo_3_revelry_and_madness`)*
- Owners: army-bar ability (no unit junction)
- Proposed activation: **When in melee: cast at own feet (existing ground-cast path). [army-bar cast]**
- Run stats: cd 120s · 48s · ground · ×1 uses · wind-up 3s · army · army bar

**351. The Burning Waters** — *melee_self, ground*
- Keys: `wh3_dlc27_army_abilities_eternal_dance_tempo_3_streams_of_euphoria`
- Game text: “When the seas dry, essences will break all souls, their vessels, and spill in fiery tides that we alone can withstand.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc27_army_abilities_eternal_dance_tempo_3_streams_of_euphoria`)*
- Owners: army-bar ability (no unit junction)
- Proposed activation: **When in melee: cast at own feet (existing ground-cast path). [army-bar cast]**
- Run stats: cd 120s · 48s · ground · ×1 uses · wind-up 3s · army · army bar
- Decision: **skipped (army-bar ability)** — user: “Skip all army bar abilities.” (standing rule 10); no automatic logic.
- Keys: `wh3_dlc27_army_abilities_eternal_dance_tempo_3_streams_of_euphoria`
- Game text: “When the seas dry, essences will break all souls, their vessels, and spill in fiery tides that we alone can withstand.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc27_army_abilities_eternal_dance_tempo_3_streams_of_euphoria`)*
- Owners: army-bar ability (no unit junction)
- Proposed activation: **When in melee: cast at own feet (existing ground-cast path). [army-bar cast]**
- Run stats: cd 120s · 48s · ground · ×1 uses · wind-up 3s · army · army bar

**352. The Unmasking** — *melee_enemy, ground*
- Keys: `wh3_dlc27_army_abilities_eternal_dance_tempo_3_fate_of_desperation`
- Game text: “In the end, Loec's mask of shadow-dappled leaves will fall away – underneath it, there was never strength. His laughter will cease. Without it, there was never a voice.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc27_army_abilities_eternal_dance_tempo_3_fate_of_desperation`)*
- Owners: army-bar ability (no unit junction)
- Proposed activation: **When in melee: cast at own feet (existing ground-cast path). [army-bar cast]**
- Run stats: cd 120s · 48s · ground · ×1 uses · wind-up 3s · army · army bar
- Decision: **skipped (army-bar ability)** — user: “Skip all army bar abilities.” (standing rule 10); no automatic logic.
- Keys: `wh3_dlc27_army_abilities_eternal_dance_tempo_3_fate_of_desperation`
- Game text: “In the end, Loec's mask of shadow-dappled leaves will fall away – underneath it, there was never strength. His laughter will cease. Without it, there was never a voice.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc27_army_abilities_eternal_dance_tempo_3_fate_of_desperation`)*
- Owners: army-bar ability (no unit junction)
- Proposed activation: **When in melee: cast at own feet (existing ground-cast path). [army-bar cast]**
- Run stats: cd 120s · 48s · ground · ×1 uses · wind-up 3s · army · army bar

**353. Time Amok** — *melee_self, ground*
- Keys: `wh3_dlc20_cataclysm_bound_time_amok` · `wh3_dlc27_cataclysm_bound_time_amok`
- Game text: “The Wizard reaches into the tapestry of fate, altering the flow of time to suit his allies' needs, who then fight on harder and faster than ever before.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc20_cataclysm_bound_time_amok`)*
- Owners: not unit-innate — bound ability (item/skill-granted)
- Proposed activation: **When in melee: cast at own feet (existing ground-cast path).**
- Run stats: cd 120s · 45s · ground · ×1 uses · wind-up 5s · bound
- Decision: **skipped (unsuitable: movement)** — collection-time: unsuitable (movement); no automatic logic.
- Keys: `wh3_dlc20_cataclysm_bound_time_amok` · `wh3_dlc27_cataclysm_bound_time_amok`
- Game text: “The Wizard reaches into the tapestry of fate, altering the flow of time to suit his allies' needs, who then fight on harder and faster than ever before.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc20_cataclysm_bound_time_amok`)*
- Owners: not unit-innate — bound ability (item/skill-granted)
- Proposed activation: **When in melee: cast at own feet (existing ground-cast path).**
- Run stats: cd 120s · 45s · ground · ×1 uses · wind-up 5s · bound


### Tier 4 — ally-targeted (nearest-ally picker needed; self-cast interim) (60 items)

**354. Bastion's Defenders** — *melee_self, friend*
- Keys: `wh3_dlc24_character_abilities_bastions_defenders`
- Game text: “Sometimes, you must make a stand against a tide of Ruin. That time is now; the place is here.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc24_character_abilities_bastions_defenders`)*
- Owners: Gate Master; unit set(s): wh3_dlc24_cth_cha_gate_master
- Proposed activation: **When in melee: cast on self for now (nearest-ally picker later).**
- Decision: **approved (in-melee self)** — user-approved in the questionnaire: when in melee and not fleeing, cast on self for now (nearest-ally picker later).
- Run stats: cd 90s · 30s · friend

**355. Beastlord's Gaze** — *melee_self, friend*
- Keys: `wh2_twa03_lord_abilities_beastlords_gaze`
- Game text: “With a piercing stare, Rakarth makes known his innate cruelty and bloodlust to his beastly kindred spirits, thus subduing them.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_twa03_lord_abilities_beastlords_gaze`)*
- Owners: Rakarth
- Proposed activation: **When in melee: cast on self for now (nearest-ally picker later).**
- Decision: **skipped (revisit)** — user: “Skip for now” (revisit later). (block 9)
- Run stats: cd 60s · 40s · friend

**356. Captain of the Phoenix Guard** — *melee_self, friend*
- Keys: `wh3_dlc27_character_abilities_captain_of_the_phoenix_guard`
- Game text: “Being closest to the thoughts of the Creator God marks Caradryan with the divine strength to lead Asuryan's guardians.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc27_character_abilities_captain_of_the_phoenix_guard`)*
- Owners: Caradryan
- Proposed activation: **When in melee: cast on self for now (nearest-ally picker later).**
- Decision: **approved (in melee and health<=75)** — user chose “In melee and below 75% health”: the Potion-of-Toughness gate — in melee AND own health ≤ 75% — because the ability also grants Physical Resistance to allies, unlike the pure heals Star of Avelorn/Gulyas which take the health-only gate. Cast on self when in melee and at ≤ 75% health. (block 9)
- Run stats: cd 120s · 43s · friend

**357. Da Boss 'as a Plan!** — *melee_self, friend*
- Keys: `wh3_dlc26_character_abilities_da_boss_as_a_plan`
- Game text: “Although Gorbad's soldiers occasionally wonder what kind of weapon this "Plan" of his is and when he's going to use it, knowing he has it bolsters their spirits nonetheless.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc26_character_abilities_da_boss_as_a_plan`)*
- Owners: Gorbad Ironclaw
- Proposed activation: **When in melee: cast on self for now (nearest-ally picker later).**
- Decision: **approved (in-melee self)** — user-approved in the questionnaire: when in melee and not fleeing, cast on self for now (nearest-ally picker later). (block 9)
- Run stats: cd 90s · 20s · friend

**358. Favour of the Fay** — *melee_self, friend*
- Keys: `wh_dlc07_lord_abilities_favour_of_the_fay`
- Game text: “"I didn't know how empty was my soul... until it was filled."” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh_dlc07_lord_abilities_favour_of_the_fay`)*
- Owners: Fay Enchantress
- Proposed activation: **When in melee: cast on self for now (nearest-ally picker later).**
- Decision: **approved (in-melee self)** — user-approved in the questionnaire: when in melee and not fleeing, cast on self for now (nearest-ally picker later). (block 9)
- Run stats: cd 90s · 44s · friend

**359. Fury of Khaine** — *melee_self, friend*
- Keys: `wh2_main_unit_abilities_fury_of_khaine`
- Game text: “As the blood in the cauldron boils and bubbles, Khaine drives bloodlust to a fever pitch and stokes hearts with a violent fire.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_main_unit_abilities_fury_of_khaine`)*
- Owners: Crone Hellebron, Death Hag
- Proposed activation: **When in melee: cast on self for now (nearest-ally picker later).**
- Decision: **approved (charge and in-melee)** — user chose “Charge and in melee (like Fangspike)”: activate in the charge window OR in melee (and not fleeing), cast on self. (block 9)
- Run stats: cd 90s · 28s · friend

**360. Helm of Yvresse** — *melee_self, friend*
- Keys: `wh2_dlc15_item_abilities_helm_of_yvresse`
- Game text: “The ceremonial crown of he who protects Yvresse’s ancient metropolis is an inspirational symbol of dogged determination.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc15_item_abilities_helm_of_yvresse`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee: cast on self for now (nearest-ally picker later).**
- Decision: **approved (wavering self)** — user chose “Only when wavering (like Vial of Troll Blood)”: cast on self only while the owner is wavering (no melee arm). This is the **Unbreakable** pattern — now used by **Vial of Troll Blood**, **Ferocious Fury of Ulric** and this item (third member). (block 9)
- Run stats: cd 120s · 17s · friend

**361. Helping Hand** — *melee_self, friend*
- Keys: `wh2_pro08_character_abilities_helping_hand`
- Game text: “Two blades are infinitely better than one - twice the attack, double the number of fell lives unceremoniously ended.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_pro08_character_abilities_helping_hand`)*
- Owners: Felix
- Proposed activation: **When in melee: cast on self for now (nearest-ally picker later).**
- Decision: **approved (in-melee self)** — user-approved in the questionnaire: when in melee and not fleeing, cast on self for now (nearest-ally picker later). (block 9)
- Run stats: cd 120s · 22s · friend

**362. Inspired Assault I** — *melee_self, friend*
- Keys: `wh3_main_lord_abilities_inspired_assault_i`
- Game text: “The most noble, educated and experienced among us have the means to think laterally, the confidence to know that victory is close at hand, and most importantly, the power to inspire.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_lord_abilities_inspired_assault_i`)*
- Owners: Lord Magistrate
- Proposed activation: **When in melee: cast on self for now (nearest-ally picker later).**
- Decision: **approved (charge and in-melee)** — user chose “Charge and in melee (like Fangspike)”: activate in the charge window OR in melee (and not fleeing), cast on self. (block 9)
- Run stats: cd 60s · 29s · friend

**363. Inspired Assault II** — *melee_self, friend*
- Keys: `wh3_main_lord_abilities_inspired_assault_ii`
- Game text: “The most noble, educated and experienced among us have the means to think laterally, the confidence to know that victory is close at hand, and most importantly, the power to inspire.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_lord_abilities_inspired_assault_ii`)*
- Owners: not unit-innate (granted by character skill)
- Proposed activation: **When in melee: cast on self for now (nearest-ally picker later).**
- Decision: **approved (charge and in-melee)** — user chose “Charge and in melee (like Fangspike)”: activate in the charge window OR in melee (and not fleeing), cast on self. (block 9)
- Run stats: cd 90s · 42s · friend

**364. Inspired Assault III** — *melee_self, friend*
- Keys: `wh3_main_lord_abilities_inspired_assault_iii`
- Game text: “The most noble, educated and experienced among us have the means to think laterally, the confidence to know that victory is close at hand, and most importantly, the power to inspire.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_lord_abilities_inspired_assault_iii`)*
- Owners: not unit-innate (granted by character skill)
- Proposed activation: **When in melee: cast on self for now (nearest-ally picker later).**
- Decision: **approved (charge and in-melee)** — user chose “Charge and in melee (like Fangspike)”: activate in the charge window OR in melee (and not fleeing), cast on self. (block 9)
- Run stats: cd 120s · 43s · friend

**365. Inspired Defence I** — *melee_self, friend*
- Keys: `wh3_main_lord_abilities_inspired_defence_i`
- Game text: “The ability to think several moves ahead of their opponents gives the Cathayan nobles a distinct advantage in matters of defence.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_lord_abilities_inspired_defence_i`)*
- Owners: Lord Magistrate
- Proposed activation: **When in melee: cast on self for now (nearest-ally picker later).**
- Decision: **approved (in-melee self)** — user-approved in the questionnaire: when in melee and not fleeing, cast on self for now (nearest-ally picker later). (block 9)
- Run stats: cd 60s · 24s · friend

**366. Inspired Defence II** — *melee_self, friend*
- Keys: `wh3_main_lord_abilities_inspired_defence_ii`
- Game text: “The ability to think several moves ahead of their opponents gives the Cathayan nobles a distinct advantage in matters of defence.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_lord_abilities_inspired_defence_ii`)*
- Owners: not unit-innate (granted by character skill)
- Proposed activation: **When in melee: cast on self for now (nearest-ally picker later).**
- Decision: **approved (in-melee self)** — user-approved in the questionnaire: when in melee and not fleeing, cast on self for now (nearest-ally picker later). (block 9)
- Run stats: cd 90s · 31s · friend

**367. Inspired Defence III** — *melee_self, friend*
- Keys: `wh3_main_lord_abilities_inspired_defence_iii`
- Game text: “The ability to think several moves ahead of their opponents gives the Cathayan nobles a distinct advantage in matters of defence.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_lord_abilities_inspired_defence_iii`)*
- Owners: not unit-innate (granted by character skill)
- Proposed activation: **When in melee: cast on self for now (nearest-ally picker later).**
- Decision: **approved (in-melee self)** — user-approved in the questionnaire: when in melee and not fleeing, cast on self for now (nearest-ally picker later). (block 9)
- Run stats: cd 120s · 34s · friend

**368. Mantra of Invigoration** — *melee_self, friend*
- Keys: `wh3_cp1_character_abilities_protection_prayer`
- Game text: “Through fervent supplication, a Clawspeaker may be rejuvenated in body, for he knows mental fortitude cannot overcome the body's failings.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_cp1_character_abilities_protection_prayer`)*
- Owners: Clawspeaker (Life)
- Proposed activation: **When in melee: cast on self for now (nearest-ally picker later).**
- Decision: **approved (health<=75, no melee gate)** — user chose “Below 75% health (no melee gate)”: cast on self when own health ≤ 75%, no melee gate — the health-only evaluator; **fourth member of that family** (with Ghoul King of Ushoran, Star of Avelorn and Gulyas). (block 9)
- Run stats: cd 120s · 32s · friend

**369. Mantra of Righteousness** — *melee_self, friend*
- Keys: `wh3_cp1_character_abilities_offense_prayer`
- Game text: “The might of all Thousand Gods can be called down to the battlefield to anchor the souls of the noble Tigers.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_cp1_character_abilities_offense_prayer`)*
- Owners: Clawspeaker (Beasts)
- Proposed activation: **When in melee: cast on self for now (nearest-ally picker later).**
- Decision: **approved (in-melee self)** — user-approved in the questionnaire: when in melee and not fleeing, cast on self for now (nearest-ally picker later). (block 9)
- Run stats: cd 120s · 40s · friend

**370. Meat Feast** — *melee_self, friend*
- Keys: `wh3_main_prisoners_butcher`
- Game text: ““Gold… meat… What else is there? War, maybe? But dinner and pay come first...…” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_prisoners_butcher`)*
- Owners: army of: The Maneaters, Blood Guzzlers, Bloodmaw
- Proposed activation: **When in melee: cast on self for now (nearest-ally picker later).**
- Decision: **approved (health<=75, no melee gate)** — user chose “Below 75% health (no melee gate)”: cast on self when own health ≤ 75%, no melee gate — the health-only evaluator; **fifth member of that family** (with Ghoul King of Ushoran, Star of Avelorn, Gulyas and Mantra of Invigoration). (block 9)
- Removed: **2026-10-17** — `excluded (not in wheel: army ability - removed from mod per user decision 2026-10-17)`; it was implemented but sits OUTSIDE the single in-wheel rule. See §10.2.
- Run stats: cd 120s · 20s · friend · army · army bar

**371. Offering to the Gods** — *melee_self, friend*
- Keys: `wh3_dlc27_lord_abilities_offering_to_the_gods`
- Game text: “In true Norscan fashion, whatever cunning pacts and bargains the Shaman Sorcerers pursue, they must seal them with blood. Not theirs, of course…” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc27_lord_abilities_offering_to_the_gods`)*
- Owners: Great Shaman-Sorcerer (Death), Great Shaman-Sorcerer (Fire), Great Shaman-Sorcerer (Metal)
- Proposed activation: **When in melee: cast on self for now (nearest-ally picker later).**
- Decision: **skipped (revisit)** — user: “Skip for now” (revisit later). The effect **sacrifices a friendly unit** (it damages allies in range and kills entities of the targeted ally), so **no automatic logic is safe** for it. (block 9)
- Run stats: cd 120s · 43s · friend

**372. Orcs are da Best!** — *melee_self, friend*
- Keys: `wh3_dlc26_character_abilities_orcs_are_da_best`
- Game text: “"...and if sumbody sez else, smash 'em to prove dat!"” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc26_character_abilities_orcs_are_da_best`)*
- Owners: Gorbad Ironclaw
- Proposed activation: **When in melee: cast on self for now (nearest-ally picker later).**
- Decision: **approved (in-melee self)** — user-approved in the questionnaire: when in melee and not fleeing, cast on self for now (nearest-ally picker later). (block 9)
- Run stats: cd 90s · 27s · friend

**373. Overseer of the Unseen** — *melee_self, friend*
- Keys: `wh3_dlc29_hero_active_overseer_of_the_unseen`
- Game text: “"Lend them Grandfather's aid, my Nurglings, show them his strength given with love."” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc29_hero_active_overseer_of_the_unseen`)*
- Owners: Morbidex Twiceborn
- Proposed activation: **When in melee: cast on self for now (nearest-ally picker later).**
- Decision: **approved (in-melee self)** — user-approved in the questionnaire: when in melee and not fleeing, cast on self for now (nearest-ally picker later). The user was offered the wider **wavering self-or-ally** form and chose plain in-melee self. (block 9)
- Run stats: cd 90s · 44s · friend

**374. Pilgrimage of Skulls** — *melee_self, friend*
- Keys: `wh3_dlc26_lord_abilities_pilgrimage_of_skulls`
- Game text: “Never forget the path I have set you upon! If anything stands across it, bleed it, burn it, break it!"” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc26_lord_abilities_pilgrimage_of_skulls`)*
- Owners: Bloodspeaker
- Proposed activation: **When in melee: cast on self for now (nearest-ally picker later).**
- Run stats: cd 120s · 21s · friend

**375. Predatory Instincts** — *melee_self, friend*
- Keys: `wh3_cp1_lord_abilities_predatory_instincts`
- Game text: “A predator need not be savage in their approach. Skill and precision ends a hunt just as effectively as unbridled aggression.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_cp1_lord_abilities_predatory_instincts`)*
- Owners: Tiger Warrior Sawai
- Proposed activation: **When in melee: cast on self for now (nearest-ally picker later).**
- Run stats: cd 90s · 25s · friend

**376. Red Fury** — *melee_self, friend*
- Keys: `wh_main_character_abilities_red_fury`
- Game text: “Vampires have long had a savage and unstoppable bloodlust. They will continue to slaughter until their enemies lie dead at their feet, or have been turned to Undeath.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh_main_character_abilities_red_fury`)*
- Owners: Isabella von Carstein
- Proposed activation: **When in melee: cast on self for now (nearest-ally picker later).**
- Run stats: cd 90s · 31s · friend

**377. Relentless Rage** — *melee_self, friend*
- Keys: `wh3_main_army_abilities_relentless_rage`
- Game text: “The concentrated power of hatred gives the armies of Khorne energy beyond their normal means to hack and slay in His name.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_army_abilities_relentless_rage`)*
- Owners: army of: Blood Keepers, Challengers of Khorne, Blooded Wanderers
- Proposed activation: **When in melee: cast on self for now (nearest-ally picker later).**
- Run stats: cd 90s · 20s · friend · army · army bar

**378. Twilight Horn I** — *melee_self, friend*
- Keys: `wh2_dlc16_item_abilities_twilight_horn_i`
- Game text: “No purer sound is there than a single note from this great horn, capable of emboldening the faint of heart and rousing the timid.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc16_item_abilities_twilight_horn_i`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee: cast on self for now (nearest-ally picker later).**
- Run stats: cd 60s · 33s · friend

**379. Where You Goin!?** — *melee_self, friend*
- Keys: `wh3_dlc26_character_abilities_were_you_goin`
- Game text: “If anyone even thinks of fleeing a battle in the Bruiser's presence, they find themselves flung head over heels in the thick of it.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc26_character_abilities_were_you_goin`)*
- Owners: Bruiser
- Proposed activation: **When in melee: cast on self for now (nearest-ally picker later).**
- Run stats: cd 90s · 25s · friend

**380. Whiplash!** — *melee_self, friend*
- Keys: `wh2_dlc14_lord_abilities_whiplash`
- Game text: “The startling crack of the Beastmaster’s hefty and ever-so-slightly serrated whip of Dragon-sinew suitably infuriates the beasts for battle.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc14_lord_abilities_whiplash`)*
- Owners: High Beastmaster, Rakarth
- Proposed activation: **When in melee: cast on self for now (nearest-ally picker later).**
- Run stats: cd 90s · 21s · friend

**381. Wild Abandon** — *melee_self, friend*
- Keys: `wh3_dlc26_lord_abilities_wild_abandon`
- Game text: “The Bloodspeaker asks the impossible of his followers, and they do it. Many die afterwards. But before that, they kill.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc26_lord_abilities_wild_abandon`)*
- Owners: Bloodspeaker
- Proposed activation: **When in melee: cast on self for now (nearest-ally picker later).**
- Run stats: cd 90s · 25s · friend

**382. Alchemist's Elixir of Iron Skin** — *melee_self, friend*
- Keys: `wh3_main_item_abilities_alchemists_elixir_of_iron_skin`
- Game text: “To be a Cathayan alchemist afore the disapproving masses takes a thick skin, but the reddish liquid within this phial goes far beyond that.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_item_abilities_alchemists_elixir_of_iron_skin`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee: cast on self for now (nearest-ally picker later).**
- Run stats: cd 90s · 25s · friend · ×2 uses

**383. Alchemist's Elixir of Puissance** — *melee_self, friend*
- Keys: `wh3_main_item_abilities_alchemists_elixir_of_puissance`
- Game text: “The fighting prowess of Cathay's greatest can be taken in draught form when a further burst of aggression is needed to tip the balance in the Celestial Emperor's favour.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_item_abilities_alchemists_elixir_of_puissance`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee: cast on self for now (nearest-ally picker later).**
- Run stats: cd 90s · 29s · friend · ×2 uses

**384. Alchemist's Elixir of Venom** — *melee_self, friend*
- Keys: `wh3_main_item_abilities_alchemists_elixir_of_venom`
- Game text: “This concoction enables the taker to not just wound their opponent, but set deadly poison in the lacerated flesh as well.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_item_abilities_alchemists_elixir_of_venom`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee: cast on self for now (nearest-ally picker later).**
- Run stats: cd 90s · 36s · friend · ×1 uses

**385. Book of Arkhan** — *melee_self, friend*
- Keys: `wh_main_spell_bound_book_of_arkhan`
- Game text: “Friendly units targeted by the caster are filled with magical energy, making them even more aggressive!” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh_main_spell_bound_book_of_arkhan`)*
- Owners: not unit-innate — bound ability (item/skill-granted)
- Proposed activation: **When in melee: cast on self for now (nearest-ally picker later).**
- Run stats: cd 60s · 25s · friend · ×4 uses · bound

**386. Elixir of Might** — *melee_self, friend*
- Keys: `wh2_dlc09_item_abilities_elixir_of_might`
- Game text: “One sip of the elixir fills the body of its drinker with the strength of many powerful, elite warriors.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc09_item_abilities_elixir_of_might`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee: cast on self for now (nearest-ally picker later).**
- Run stats: cd 60s · 36s · friend · ×1 uses

**387. Enhanced Skavenbrew** — *melee_self, friend*
- Keys: `wh3_dlc29_item_abilities_enhanced_skavenbrew`
- Game text: “This concoction is made of Warpstone and the blood of many different creatures, making its effects even more devastating.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc29_item_abilities_enhanced_skavenbrew`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee: cast on self for now (nearest-ally picker later).**
- Run stats: cd 90s · 60s · friend · ×2 uses

**388. Flesh to Stone** — *melee_self, friend*
- Keys: `wh2_dlc16_spell_bound_flesh_to_stone`
- Game text: “This spell temporarily transforms allies' mortal flesh into unbreakable rock, increasing tenfold their resistance to attack.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc16_spell_bound_flesh_to_stone`)*
- Owners: Enigmas of Ghyran (Zoats), Zoats
- Proposed activation: **When in melee: cast on self for now (nearest-ally picker later).**
- Run stats: cd 90s · 19s · friend · ×3 uses · bound

**389. Scroll of Shielding** — *melee_self, friend*
- Keys: `wh_main_item_abilities_scroll_of_shielding`
- Game text: “Upon the Scroll of Shielding is a crude drawing of a warrior's shield displaying an unknown crest of a kingdom long lost.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh_main_item_abilities_scroll_of_shielding`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee: cast on self for now (nearest-ally picker later).**
- Run stats: cd 60s · 57s · friend · ×1 uses

**390. Skavenbrew** — *melee_self, friend*
- Keys: `wh2_main_item_abilities_skavenbrew`
- Game text: “This concoction is made of Warpstone and the blood of many creatures. Its effects are devastating.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_main_item_abilities_skavenbrew`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee: cast on self for now (nearest-ally picker later).**
- Run stats: cd 90s · 47s · friend · ×1 uses

**391. Staff of Damnation** — *melee_self, friend*
- Keys: `wh_main_spell_bound_staff_of_damnation`
- Game text: “This gnarled stave is carved from the blackened heartwood of a Hangman's Tree. It contains a powerful spell that fills nearby Undead with a frantic vitality.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh_main_spell_bound_staff_of_damnation`)*
- Owners: not unit-innate — bound ability (item/skill-granted)
- Proposed activation: **When in melee: cast on self for now (nearest-ally picker later).**
- Run stats: cd 90s · 25s · friend · ×3 uses · bound

**392. Verminous Fury** — *melee_self, friend*
- Keys: `wh3_dlc29_lord_abilities_verminous_fury`
- Game text: “Fervour and madness seep into the very ground the Warbringer walks on.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc29_lord_abilities_verminous_fury`)*
- Owners: Verminlord Warbringer
- Proposed activation: **When in melee: cast on self for now (nearest-ally picker later).**
- Run stats: cd 120s · 60s · friend · ×3 uses

**393. Wrath of the Bear** — *melee_self, friend*
- Keys: `wh3_main_army_abilities_wrath_of_the_bear`
- Game text: “Men imbued with the ire and fury of the Great Bear become as equally hard to break as they are fierce.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_army_abilities_wrath_of_the_bear`)*
- Owners: army-bar ability (no unit junction)
- Proposed activation: **When in melee: cast on self for now (nearest-ally picker later).**
- Run stats: cd 90s · 17s · friend · ×3 uses · army · army bar

**394. Doom Lord** — *melee_self, friend*
- Keys: `wh3_dlc29_lord_abilities_doom_lord`
- Game text: “"I do not fear death, for it answers to me!"” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc29_lord_abilities_doom_lord`)*
- Owners: Dieter Helsnicht; unit set(s): cha_dieter
- Proposed activation: **When in melee: cast on self for now (nearest-ally picker later).**
- Run stats: cd 120s · 40s · friend · wind-up 1s

**395. Hellish Vigour** — *melee_self, friend*
- Keys: `wh3_dlc29_lord_abilities_hellish_vigour` · `wh3_dlc29_lord_abilities_hellish_vigour_upgraded`
- Game text: “Saturating his forces with hellish energy, the Necrarch Lord drives his host onward with unnatural speed.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc29_lord_abilities_hellish_vigour`)*
- Owners: Necrarch Vampire Lord
- Proposed activation: **When in melee: cast on self for now (nearest-ally picker later).**
- Run stats: cd 90s · 25s · friend · wind-up 3s

**396. Master Rune of Breaking** — *melee_self, friend*
- Keys: `wh2_dlc17_rune_abilities_master_rune_of_breaking`
- Game text: “Runesmiths take particular delight in the sound of the inferior works of other races breaking like icicles beneath a hammer blow.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc17_rune_abilities_master_rune_of_breaking`)*
- Owners: not unit-innate — rune ability (Dwarf runesmiths/lords)
- Proposed activation: **When in melee: cast on self for now (nearest-ally picker later).**
- Run stats: cd 180s · 55s · friend · wind-up 3s · rune

**397. Master Rune of Negation** — *melee_self, friend*
- Keys: `wh_dlc06_rune_abilities_master_rune_of_negation`
- Game text: “The secret of this powerful rune was given to a Runelord by Valaya herself, insulating all under its auspices with protection from magic.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh_dlc06_rune_abilities_master_rune_of_negation`)*
- Owners: not unit-innate — rune ability (Dwarf runesmiths/lords)
- Proposed activation: **When in melee: cast on self for now (nearest-ally picker later).**
- Run stats: cd 180s · 40s · friend · wind-up 3s · rune

**398. Rune of Breaking** — *melee_self, friend*
- Keys: `wh2_dlc17_rune_abilities_rune_of_breaking`
- Game text: “Runesmiths take particular delight in the sound of the inferior works of other races breaking like icicles beneath a hammer blow.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc17_rune_abilities_rune_of_breaking`)*
- Owners: Runelord, Runesmith, Throni Ironbrow, Thorek Ironbrow; lore/group: Runic Magic
- Proposed activation: **When in melee: cast on self for now (nearest-ally picker later).**
- Run stats: cd 120s · 33s · friend · wind-up 3s · rune

**399. Rune of Negation** — *melee_self, friend*
- Keys: `wh_main_rune_abilities_rune_of_negation`
- Game text: “The secret of this powerful rune was given to a Runelord by Valaya herself, insulating all under its auspices with protection from magic.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh_main_rune_abilities_rune_of_negation`)*
- Owners: Runelord, Runesmith, Throni Ironbrow, Thorek Ironbrow; lore/group: Runic Magic
- Proposed activation: **When in melee: cast on self for now (nearest-ally picker later).**
- Run stats: cd 120s · 24s · friend · wind-up 3s · rune

**400. Rune of Thungni** — *melee_self, friend*
- Keys: `wh3_dlc23_item_abilities_rune_of_thungni`
- Game text: “This tablet provides the means to crack through any substance.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc23_item_abilities_rune_of_thungni`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee: cast on self for now (nearest-ally picker later).**
- Run stats: cd 120s · 40s · friend · wind-up 3s

**401. Shielding Swarm** — *melee_self, friend*
- Keys: `wh3_dlc29_hero_active_dispatch_the_swarm_protect` · `wh3_dlc29_hero_active_dispatch_the_swarm_protect_upgraded`
- Game text: “The swarm coalesces, dense in the air, obscuring the target from sight, and from harm.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc29_hero_active_dispatch_the_swarm_protect`)*
- Owners: Bloab Rotspawned
- Proposed activation: **When in melee: cast on self for now (nearest-ally picker later).**
- Run stats: cd 120s · 30s · friend · wind-up 1s

**402. Sweet Sorrow** — *melee_self, friend*
- Keys: `wh3_main_army_abilities_sweet_sorrow`
- Game text: “The Perfect Prince's warriors surge forth, bathing in the deepest, most beautiful melancholy and the most perverse notions of regret, then turning those feelings into the sweetest carnage.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_army_abilities_sweet_sorrow`)*
- Owners: army of: Keepers of Bliss, The Accursed Troupe, The Tormentors
- Proposed activation: **When in melee: cast on self for now (nearest-ally picker later).**
- Run stats: cd 60s · 15s · friend · wind-up 1s · army · army bar

**403. Cascading Fire Cloak** — *melee_self, friend*
- Keys: `wh3_main_spell_bound_cascading_fire_cloak`
- Game text: “A blazing aura surrounds the Pyromancer's chosen ally, shielding them with protective flame and augmenting their abilities.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_spell_bound_cascading_fire_cloak`)*
- Owners: not unit-innate — bound ability (item/skill-granted)
- Proposed activation: **When in melee: cast on self for now (nearest-ally picker later).**
- Run stats: cd 60s · 19s · friend · ×2 uses · wind-up 1s · bound

**404. Dark Conduit** — *melee_self, friend*
- Keys: `wh2_main_army_abilities_dark_conduit`
- Game text: “An intense inrush of Dark Magic causes an explosion that damages all around except the casting unit, who remain intact yet exhausted.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_main_army_abilities_dark_conduit`)*
- Owners: army-bar ability (no unit junction)
- Proposed activation: **When in melee: cast on self for now (nearest-ally picker later).**
- Run stats: cd 120s · 27s · friend · ×3 uses · wind-up 5s · army · army bar

**405. Harmonic Convergence** — *melee_self, friend*
- Keys: `wh3_main_spell_bound_harmonic_convergence`
- Game text: “Divining auspicious signs, the caster guides the minds of targets, augmenting them with the foresight needed for victory.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_spell_bound_harmonic_convergence`)*
- Owners: not unit-innate — bound ability (item/skill-granted)
- Proposed activation: **When in melee: cast on self for now (nearest-ally picker later).**
- Run stats: cd 60s · 27s · friend · ×2 uses · wind-up 1s · bound

**406. Hysterical Frenzy** — *melee_self, friend*
- Keys: `wh3_main_spell_slaanesh_hysterical_frenzy_bound`
- Game text: “The caster's victims are engulfed by a torrent of unreasoning emotion, excruciating pain and blissful rapture, causing them to embark on a riotous, clawing rampage.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_spell_slaanesh_hysterical_frenzy_bound`)*
- Owners: Druchii Anointed; unit set(s): wh3_main_sla_mon_keeper_of_secrets_0
- Proposed activation: **When in melee: cast on self for now (nearest-ally picker later).**
- Run stats: cd 43s · 28s · friend · ×2 uses · wind-up 3s · bound

**407. Merciw's Monstrous Regiment** — *melee_self, friend*
- Keys: `wh3_dlc20_cataclysm_bound_merciws_monstrous_regiment` · `wh3_dlc27_cataclysm_bound_merciws_monstrous_regiment`
- Game text: “The Wizard calls upon the strength of the wild world and bestows it upon his chosen allies, increasing the ferocity of their attack.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc20_cataclysm_bound_merciws_monstrous_regiment`)*
- Owners: not unit-innate — bound ability (item/skill-granted)
- Proposed activation: **When in melee: cast on self for now (nearest-ally picker later).**
- Run stats: cd 120s · 120s · friend · ×1 uses · wind-up 5s · bound

**408. Murderous Libations** — *melee_self, friend*
- Keys: `wh3_dlc27_army_abilities_eternal_dance_tempo_3_nectar_of_the_daemonette`
- Game text: “Blood fuels Khorne's base fires for a time. That which is imbibed fans flames beyond one's capacity to comprehend.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc27_army_abilities_eternal_dance_tempo_3_nectar_of_the_daemonette`)*
- Owners: army-bar ability (no unit junction)
- Proposed activation: **When in melee: cast on self for now (nearest-ally picker later).**
- Run stats: cd 120s · 36s · friend · ×2 uses · wind-up 1s · army · army bar

**409. Pha's Protection** — *melee_self, friend*
- Keys: `wh3_main_spell_bound_phas_protection`
- Game text: “The Wizard calls upon the beneficent Guardian of Light to protect his allies from harm.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_spell_bound_phas_protection`)*
- Owners: not unit-innate — bound ability (item/skill-granted)
- Proposed activation: **When in melee: cast on self for now (nearest-ally picker later).**
- Run stats: cd 60s · 22s · friend · ×2 uses · wind-up 1s · bound

**410. Protection of Quetzl** — *melee_self, friend*
- Keys: `wh2_dlc13_army_abilities_protection_of_quetzl` · `wh2_dlc13_army_abilities_protection_of_quetzl_upgraded`
- Game text: “The servants of the Warrior-God – his chosen ones – live for war's struggle and glory.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc13_army_abilities_protection_of_quetzl`)*
- Owners: army-bar ability (no unit junction)
- Proposed activation: **When in melee: cast on self for now (nearest-ally picker later).**
- Run stats: cd 120s · 35s · friend · ×3 uses · wind-up 5s · army · army bar

**411. The Hand of Dust** — *melee_self, friend*
- Keys: `wh3_dlc29_spell_bound_undeath_sulekhim_hand_of_dust`
- Game text: “Seconds and centuries are all the same to a master of Shyish. All that is transient is at his mercy. It fades and crumbles at his touch.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc29_spell_bound_undeath_sulekhim_hand_of_dust`)*
- Owners: not unit-innate — bound ability (item/skill-granted)
- Proposed activation: **When in melee: cast on self for now (nearest-ally picker later).**
- Run stats: cd 28s · 14s · friend · ×2 uses · wind-up 1s · bound

**412. Touched by the Moon** — *melee_self, friend*
- Keys: `wh2_dlc17_army_abilities_touched_by_the_moon`
- Game text: “Morrslieb's whispers can drive Beastmen into a terrifying frenzy, the power of which few can survive.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc17_army_abilities_touched_by_the_moon`)*
- Owners: army-bar ability (no unit junction)
- Proposed activation: **When in melee: cast on self for now (nearest-ally picker later).**
- Run stats: cd 90s · 45s · friend · ×2 uses · wind-up 5s · army · army bar

**413. Warpbomb** — *melee_self, friend*
- Keys: `wh2_main_army_abilities_warpbomb`
- Game text: “Warpstone's highly-unstable magical energies can be used to fashion devilishly deadly weapons.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_main_army_abilities_warpbomb`)*
- Owners: army-bar ability (no unit junction)
- Proposed activation: **When in melee: cast on self for now (nearest-ally picker later).**
- Run stats: cd 60s · 16s · friend · ×1 uses · wind-up 1s · army · army bar


### Tier 5 — enemy-unit-targeted (needs current-target plumbing) (65 items)

**414. Accusation** — *melee_enemy, enemy unit*  — **IMPLEMENTED (harness 94)**
- Keys: `wh_main_hero_abilities_accusation`
- Game text: “The Witch Hunter levels his finger across the battlefield and accuses one of the enemy of arch-heresy!” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh_main_hero_abilities_accusation`)*
- Owners: Hertwig van Hal, Witch Hunter
- Proposed activation: **When in melee with a current target: cast at the enemy it is fighting.**
- Run stats: cd 90s · 35s · enemy unit
- **Implemented activation (harness 94; range re-derived in harness 95; OFFER TEST FIXED in harness 96):** the FIRST enemy-targeted trigger, `enemy_engaged_or_shot` — fire when an
  **enemy unit within the ability's 52 m reach** (`FOURTH.ACCUSATION_RANGE_M` = 70% of the ability's own 75 m
  `target_intercept_range`, standing rule 15) is **in melee OR under missile fire**; the chosen enemy is the **cast target (never the
  owner)**, cast via the round-4-proven `bench_fresh` fresh-handle route (`caster_su.uc:perform_special_ability(key,
  enemy_su.unit)`). Same reusable shape will serve the other enemy-aimed abilities.
- **h96 MOVE-ORDER FIX:** the offer test is the **52 m constant ONLY** — `unit:unit_distance(enemy) <= FOURTH.ACCUSATION_RANGE_M`
  (`FOURTH.eg_enemy_within_bound`); the engine's looser `unit_in_range` reach read is **REMOVED from the offer path** (it was what
  offered a target 81.3 m away and made the engine WALK the caster in). The log now prints the **real edge-to-edge distance** at the
  target choice and the pre-cast re-check (`... distance=48.7m bound=52m`).

**415. Assassin's Trophy** — *melee_enemy, enemy unit*
- Keys: `wh2_main_character_abilities_assassins_trophy`
- Game text: “It should be no great surprise that those already adept in the art of silent death continue to improve with time and practice.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_main_character_abilities_assassins_trophy`)*
- Owners: Khainite Assassin, Assassin
- Proposed activation: **When in melee with a current target: cast at the enemy it is fighting.**
- Run stats: cd 60s · 29s · enemy unit

**416. Bastet** — *melee_enemy, enemy unit*
- Keys: `wh3_dlc29_lord_abilities_bastet`
- Game text: “A slender black silhouette is all that remains of Neferata's feline familiar, foreshadowing bad luck for her foes and protecting her from danger.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc29_lord_abilities_bastet`)*
- Owners: Neferata
- Proposed activation: **When in melee with a current target: cast at the enemy it is fighting.**
- Run stats: cd 90s · 19s · enemy unit

**417. Bitter Sting** — *melee_enemy, enemy unit*
- Keys: `wh3_dlc27_qb_unit_abilities_bitter_sting`
- Game text: “The surest mark of enduring malice is prolonging one's depredations on the weak and weary.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc27_qb_unit_abilities_bitter_sting`)*
- Owners: Rancorous Manticore
- Proposed activation: **When in melee with a current target: cast at the enemy it is fighting.**
- Run stats: cd 60s · 30s · enemy unit
- Removed: **2026-10-17** — `excluded (not in wheel: boss-only unit)`; its only grant path is `wh3_dlc27_chs_feral_manticore_boss` (land_abil.tsv), a quest-battle boss variant. It was implemented and is REMOVED from the mod's `ABILITIES` table. See §10.3.

**418. Blade of Setep** — *melee_enemy, enemy unit*
- Keys: `wh2_dlc09_weapon_abilities_blade_of_setep`
- Game text: “The very late King Setep's ornate, curved sword shimmers with a blue hue that shatters the foe's armour.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc09_weapon_abilities_blade_of_setep`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee with a current target: cast at the enemy it is fighting.**
- Run stats: cd 90s · 44s · enemy unit

**419. Deathmaster's Sigil** — *melee_enemy, enemy unit*
- Keys: `wh2_dlc14_lord_abilities_deathmasters_sigil`
- Game text: “Snikch leaves his distinctive symbol traced in blood beside his victims, so others will know the Deathmaster is abroad, and live in mortal dread.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc14_lord_abilities_deathmasters_sigil`)*
- Owners: Deathmaster Snikch
- Proposed activation: **When in melee with a current target: cast at the enemy it is fighting.**
- Run stats: cd 90s · 7s · enemy unit

**420. El Syf** — *melee_enemy, enemy unit*
- Keys: `wh_dlc05_weapon_abilities_el_syf`
- Game text: “The so-called 'Northern Sword' fears no duel; anyone who dares confront him will surely meet their death!” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh_dlc05_weapon_abilities_el_syf`)*
- Owners: The Red Duke
- Proposed activation: **When in melee with a current target: cast at the enemy it is fighting.**
- Run stats: cd 90s · 24s · enemy unit

**421. Frenzied Challenge** — *melee_enemy, enemy unit*
- Keys: `wh3_dlc27_qb_unit_abilities_frenzied_challenge`
- Game text: “Faced with this creature's challenge, one either fights or flees. Yet who would flee and doom themselves to nightmares of becoming its meal? Fight it is.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc27_qb_unit_abilities_frenzied_challenge`)*
- Owners: Vicious Ghorgon
- Proposed activation: **When in melee with a current target: cast at the enemy it is fighting.**
- Run stats: cd 90s · 15s · enemy unit
- Removed: **2026-10-17** — `excluded (not in wheel: boss-only unit)`; its only grant path is `wh3_dlc27_bst_mon_ghorgon_boss` (land_abil.tsv), a quest-battle boss variant. It was implemented and is REMOVED from the mod's `ABILITIES` table. See §10.3.

**422. Frost Shard Glaive** — *melee_self, enemy unit*
- Keys: `wh3_main_weapon_abilities_frost_shard_glaive`
- Game text: “The frost shard blade of this revered weapon sparkles with the cold, hard promise of sharp slaughter.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_weapon_abilities_frost_shard_glaive`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee with a current target: cast at the enemy it is fighting.**
- Run stats: cd 120s · 30s · enemy unit

**423. Gilellion's Soulnetter** — *melee_enemy, enemy unit*
- Keys: `wh3_main_weapon_abilities_soulnetter`
- Game text: “This blade of Gilellion the Lewd, champion of Slaanesh, traps its victims in immortal servitude to its bearer.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_weapon_abilities_soulnetter`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee with a current target: cast at the enemy it is fighting.**
- Run stats: cd 120s · 26s · enemy unit

**424. Glory Seeker** — *melee_enemy, enemy unit*
- Keys: `wh3_dlc29_hero_active_glory_seeker` · `wh3_dlc29_hero_active_glory_seeker_upgraded`
- Game text: “Meeting the gaze of Orghotts Daemonspew is enough to render a creature numb, such is the malice behind his eyes” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc29_hero_active_glory_seeker`)*
- Owners: Orghotts Daemonspew
- Proposed activation: **When in melee with a current target: cast at the enemy it is fighting.**
- Run stats: cd 120s · 24s · enemy unit

**425. Headhunt** — *melee_enemy, enemy unit*
- Keys: `wh3_dlc26_character_abilities_headhunt`
- Game text: “Promising a bonus for each and every skull detached, whether or not its owner objects, has proved to be something of a motivator among Ogre mercenaries.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc26_character_abilities_headhunt`)*
- Owners: Ogre Paymaster
- Proposed activation: **When in melee with a current target: cast at the enemy it is fighting.**
- Run stats: cd 90s · 31s · enemy unit

**426. Hornswaggle** — *melee_enemy, enemy unit*
- Keys: `wh2_dlc11_character_abilities_hornswaggle`
- Game text: “"Do pay attention or this one'll 'ave the shirt from yer back!"” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc11_character_abilities_hornswaggle`)*
- Owners: Luthor Harkon
- Proposed activation: **When in melee with a current target: cast at the enemy it is fighting.**
- Run stats: cd 90s · 32s · enemy unit

**427. Hunter of Champions** — *melee_enemy, enemy unit*
- Keys: `wh_dlc08_character_abilities_hunter_of_champions`
- Game text: “Cursed to wander the length and breadth of the world, his never-ending quest to challenge and best the most gifted warriors.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh_dlc08_character_abilities_hunter_of_champions`)*
- Owners: Wulfrik the Wanderer
- Proposed activation: **When in melee with a current target: cast at the enemy it is fighting.**
- Run stats: cd 90s · 24s · enemy unit

**428. Looming Dread** — *melee_enemy, enemy unit*
- Keys: `wh2_dlc14_lord_abilities_looming_dread`
- Game text: “Rather paradoxically, afflicting an enemy with profound paranoia can cause them to drop their guard.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc14_lord_abilities_looming_dread`)*
- Owners: Master Assassin
- Proposed activation: **When in melee with a current target: cast at the enemy it is fighting.**
- Run stats: cd 90s · 31s · enemy unit

**429. Lord of Dragons** — *melee_enemy, enemy unit*
- Keys: `wh2_dlc15_lord_abilities_lord_of_dragons`
- Game text: “Imrik’s affinity with Dragons gifts him their sharpness; with his concentration heightened, even the most skilful foes struggle to land blows.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc15_lord_abilities_lord_of_dragons`)*
- Owners: Imrik
- Proposed activation: **When in melee with a current target: cast at the enemy it is fighting.**
- Run stats: cd 90s · 22s · enemy unit

**430. Mark of the Plague Fleet** — *melee_enemy, enemy unit*
- Keys: `wh3_dlc29_item_active_mark_of_the_plague_fleet`
- Game text: “This rusted talisman typifies Gutrot's command, spreading Nurgle's strength and cursing the enemy with unsteadiness, their senses roiling like the Sea of Claws in a squall.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc29_item_active_mark_of_the_plague_fleet`)*
- Owners: not unit-innate (granted by character skill)
- Proposed activation: **When in melee with a current target: cast at the enemy it is fighting.**
- Run stats: cd 120s · 30s · enemy unit

**431. Marked for Eatin'** — *melee_enemy, enemy unit*
- Keys: `wh3_dlc26_unit_abilities_marked_for_eatin`
- Game text: “Picky eaters are frowned upon amongst the Ogres. Picky fighters, however, are some of the deadliest amongst them.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc26_unit_abilities_marked_for_eatin`)*
- Owners: Eshin Maneater
- Proposed activation: **When in melee with a current target: cast at the enemy it is fighting.**
- Run stats: cd 120s · 29s · enemy unit

**432. Master of Beguilement** — *melee_enemy, enemy unit*
- Keys: `wh_dlc04_lord_abilities_beguile`
- Game text: “This Vampire Lord feints and shades, confounding their enemy into missteps and errors.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh_dlc04_lord_abilities_beguile`)*
- Owners: Vlad von Carstein, Isabella von Carstein
- Proposed activation: **When in melee with a current target: cast at the enemy it is fighting.**
- Run stats: cd 90s · 44s · enemy unit

**433. Net Dem Up!** — *melee_enemy, enemy unit*
- Keys: `wh3_dlc26_unit_abilities_net_dem_up`
- Game text: “[[i]]"Give a gobbo a net an' he'll slow da enemy gitz down long enuff to stick 'em fulla arrers."[[/i]]” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc26_unit_abilities_net_dem_up`)*
- Owners: unit set(s): grn_infantry_goblin
- Proposed activation: **When in melee with a current target: cast at the enemy it is fighting.**
- Run stats: cd 90s · 18s · enemy unit

**434. Oath of Vengeance** — *melee_enemy, enemy unit*
- Keys: `wh2_dlc10_lord_abilities_oath_of_vengeance`
- Game text: “From the Dammaz Kron, the High King recounts an ancestral grudge towards the foe, driving the Dawi into a vengeful rage.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc10_lord_abilities_oath_of_vengeance`)*
- Owners: Thorgrim Grudgebearer
- Proposed activation: **When in melee with a current target: cast at the enemy it is fighting.**
- Run stats: cd 60s · 44s · enemy unit

**435. Taunt** — *melee_enemy, enemy unit*
- Keys: `wh2_dlc11_character_abilities_taunt`
- Game text: “"You're nowt but a bunch of lily-livered landlubbers! Know that your deaths will be short - soon you'll serve under the black flag!"” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc11_character_abilities_taunt`)*
- Owners: Vampire Fleet Captain (Vampires), Vampire Fleet Captain (Death), Vampire Fleet Captain (Deep), Vampire Fleet Captain (Undeath)
- Proposed activation: **When in melee with a current target: cast at the enemy it is fighting.**
- Run stats: cd 60s · 17s · enemy unit

**436. The Averland Runefang** — *melee_enemy, enemy unit*
- Keys: `wh2_dlc13_weapon_abilities_averland_runefang`
- Game text: “One of twelve magical swords belonging to the Empire's Elector Counts, this much-folded blade has caused many a mother's son to meet his maker somewhat earlier than planned.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc13_weapon_abilities_averland_runefang`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee with a current target: cast at the enemy it is fighting.**
- Run stats: cd 120s · 33s · enemy unit

**437. The Dark Master** — *melee_enemy, enemy unit*
- Keys: `wh3_main_lord_abilities_the_dark_master`
- Game text: “If you unwisely choose not to run, strike far harder than you dare, for Be'lakor wields Ruin's combined might to confuse and tempt and rot and slaughter his foes.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_lord_abilities_the_dark_master`)*
- Owners: Be'lakor, wh3_survival_dae_cha_be_lakor
- Proposed activation: **When in melee with a current target: cast at the enemy it is fighting.**
- Run stats: cd 90s · 33s · enemy unit

**438. The Hammer of Karak Drazh** — *melee_enemy, enemy unit*
- Keys: `wh_main_weapon_abilities_the_hammer_of_karak_drazh`
- Game text: “The Hammer of Karak Drazh was struck with such powerful runes it can be swung with preternatural ease.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh_main_weapon_abilities_the_hammer_of_karak_drazh`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee with a current target: cast at the enemy it is fighting.**
- Run stats: cd 90s · 50s · enemy unit

**439. They Needs Stabbin’** — *melee_enemy, enemy unit*
- Keys: `wh2_dlc15_character_abilities_they_needs_stabbin`
- Game text: “"Get yer stabbers out, boys. We ain’t leavin’ ‘til they's fulla gashes!"” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc15_character_abilities_they_needs_stabbin`)*
- Owners: Goblin Big Boss
- Proposed activation: **When in melee with a current target: cast at the enemy it is fighting.**
- Run stats: cd 60s · 29s · enemy unit

**440. Titan Headsman** — *melee_enemy, enemy unit*
- Keys: `wh3_dlc25_hero_abilities_titan_headsman`
- Game text: “When an enemy stands broken and bruised, finishing them off is but a matter of one solid strike.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc25_hero_abilities_titan_headsman`)*
- Owners: Theodore Bruckner
- Proposed activation: **When in melee with a current target: cast at the enemy it is fighting.**
- Run stats: cd 90s · 29s · enemy unit

**441. Torment Blade** — *melee_enemy, enemy unit*
- Keys: `wh3_main_weapon_abilities_torment_blade`
- Game text: “This sword is coated with a paralysing venom, a dose of which renders the victim utterly immobile.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_weapon_abilities_torment_blade`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee with a current target: cast at the enemy it is fighting.**
- Run stats: cd 60s · 18s · enemy unit

**442. Trophy Heads** — *melee_enemy, enemy unit*
- Keys: `wh2_main_lord_abilities_trophy_heads` · `wh3_main_daemon_wings_abilities_trophy_heads`
- Game text: “Oft-times, killers retain the heads of their victims as prizes or reminders of dark deeds done.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_main_lord_abilities_trophy_heads`)*
- Owners: Queek Headtaker, Daemon Prince, Red Ulgor, Prince of Slaughter, Grand Vomitus, Prince of Buboes, Caress, the Darkling Prince (+5 more); unit set(s): khorne_characters
- Proposed activation: **When in melee with a current target: cast at the enemy it is fighting.**
- Run stats: cd 90s · 36s · enemy unit

**443. Visions of Madness** — *melee_enemy, enemy unit*
- Keys: `wh3_dlc27_qb_unit_abilities_visions_of_madness`
- Game text: “Desperate bloodlust is a mark of borderline derangement – yet some creatures care not for the limits of mind.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc27_qb_unit_abilities_visions_of_madness`)*
- Owners: Maddened Jabberslythe
- Proposed activation: **When in melee with a current target: cast at the enemy it is fighting.**
- Run stats: cd 120s · 10s · enemy unit
- Removed: **2026-10-17** — `excluded (not in wheel: boss-only unit)`; its only grant path is `wh3_dlc27_bst_mon_jabberslythe_boss` (land_abil.tsv), a quest-battle boss variant. It was implemented and is REMOVED from the mod's `ABILITIES` table. See §10.3.

**444. Whip of Agony** — *melee_enemy, enemy unit*
- Keys: `wh2_twa03_weapon_abilities_whip_of_agony`
- Game text: “Pain nourishes courage in the hearts of the wild and fear in the hearts of the weak.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_twa03_weapon_abilities_whip_of_agony`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee with a current target: cast at the enemy it is fighting.**
- Run stats: cd 120s · 29s · enemy unit

**445. Willing Prey** — *melee_enemy, enemy unit*
- Keys: `wh3_main_lord_abilities_willing_prey`
- Game text: “Some beings, in their darkest heart, have a deep-seated desire for an agonising death.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_lord_abilities_willing_prey`)*
- Owners: N'Kari
- Proposed activation: **When in melee with a current target: cast at the enemy it is fighting.**
- Run stats: cd 90s · 15s · enemy unit

**446. Word of Change** — *melee_enemy, enemy unit*
- Keys: `wh3_main_daemon_head_abilities_word_of_change`
- Game text: “Through His ever-willing vessel, the Dark Sorcerer of the Chaos Gods can cause broiling waves of maddening Change to engulf spellcasting foes.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_daemon_head_abilities_word_of_change`)*
- Owners: Daemon Prince, Red Ulgor, Prince of Slaughter, Grand Vomitus, Prince of Buboes, Caress, the Darkling Prince, Zarrivyk, Feathered-Prince (+4 more)
- Proposed activation: **When in melee with a current target: cast at the enemy it is fighting.**
- Run stats: cd 120s · 42s · enemy unit

**447. You're Next!** — *melee_enemy, enemy unit*
- Keys: `wh2_dlc15_lord_abilities_youre_next`
- Game text: “Grimgor’s reputation is one that induces paralysing fear, especially in enemies who find out they have his unwanted attentions on the battlefield!” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc15_lord_abilities_youre_next`)*
- Owners: Grimgor Ironhide
- Proposed activation: **When in melee with a current target: cast at the enemy it is fighting.**
- Run stats: cd 90s · 24s · enemy unit

**448. Blight Swarm** — *melee_enemy, enemy unit*
- Keys: `wh3_main_lord_abilities_blight_swarm`
- Game text: “Flies, drenched in the pustulent gore of rotting intestines, swarm and surround the foe, hampering their blows and haltering their attacks.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_lord_abilities_blight_swarm`)*
- Owners: Fatsod, Burplesmirk Spewpit, Exalted Great Unclean One (Death), Exalted Great Unclean One (Nurgle)
- Proposed activation: **When in melee with a current target: cast at the enemy it is fighting.**
- Run stats: cd 60s · 20s · enemy unit · ×4 uses

**449. Blood God's Shackles** — *melee_enemy, enemy unit*
- Keys: `wh3_dlc26_army_abilities_blood_gods_shackles` · `wh3_dlc26_army_abilities_blood_gods_shackles_upgraded`
- Game text: “No one refuses Skulltaker's challenge, not because they will not but because they cannot. Mighty champions cannot escape it, and certainly neither can any rank-and-file fodder.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc26_army_abilities_blood_gods_shackles`)*
- Owners: army-bar ability (no unit junction)
- Proposed activation: **When in melee with a current target: cast at the enemy it is fighting.**
- Run stats: cd 120s · 34s · enemy unit · ×1 uses · army · army bar

**450. Book of Secrets** — *melee_enemy, enemy unit*
- Keys: `wh3_dlc24_item_abilities_book_of_secrets`
- Game text: “Fire, Death and Shadow; all parts of a balanced, nutritious breakfast. Mmmm…” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc24_item_abilities_book_of_secrets`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee with a current target: cast at the enemy it is fighting.**
- Run stats: cd 90s · 20s · enemy unit · ×3 uses

**451. Don't Even Try It** — *melee_enemy, enemy unit*
- Keys: `wh2_dlc15_lord_abilities_dont_even_try_it`
- Game text: “Goblins, in general, are a little twitchy to say the least. If you’ve flinched too soon, you’re probably already dead.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc15_lord_abilities_dont_even_try_it`)*
- Owners: Goblin Great Shaman
- Proposed activation: **When in melee with a current target: cast at the enemy it is fighting.**
- Run stats: cd 90s · 18s · enemy unit · ×2 uses

**452. Eye of Khorne** — *melee_enemy, enemy unit*
- Keys: `wh3_dlc26_lord_abilities_eye_of_khorne`
- Game text: “Should Arbaal's resolve shatter, an eternity as a Chaos Spawn awaits him. A similar fate also awaits anyone in his vicinity, for a short and painful while.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc26_lord_abilities_eye_of_khorne`)*
- Owners: Arbaal the Undefeated
- Proposed activation: **When in melee with a current target: cast at the enemy it is fighting.**
- Run stats: cd 120s · 10s · enemy unit · ×1 uses

**453. Fermented Fungi** — *melee_enemy, enemy unit*
- Keys: `wh2_dlc15_lord_abilities_fermented_fungi`
- Game text: “Rotten mushroom gas wafted towards the enemy can cause them to lose their mind at the worst possible moment in battle.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc15_lord_abilities_fermented_fungi`)*
- Owners: Night Goblin Warboss, Skarsnik
- Proposed activation: **When in melee with a current target: cast at the enemy it is fighting.**
- Run stats: cd 90s · 15s · enemy unit · ×3 uses

**454. Gaze of Fate** — *melee_enemy, enemy unit*
- Keys: `wh3_main_lord_abilities_gaze_of_fate`
- Game text: “Sometimes, the abyss stares right back at you, and true perspective is revealed. The shock freezes the foe where they stand.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_lord_abilities_gaze_of_fate`)*
- Owners: Daemon Prince, Red Ulgor, Prince of Slaughter, Grand Vomitus, Prince of Buboes, Caress, the Darkling Prince, Zarrivyk, Feathered-Prince (+6 more); unit set(s): tzeentch_characters
- Proposed activation: **When in melee with a current target: cast at the enemy it is fighting.**
- Run stats: cd 90s · 14s · enemy unit · ×3 uses

**455. Muster of Malevolents** — *melee_enemy, enemy unit*
- Keys: `wh2_dlc16_character_abilities_muster_of_malevolents`
- Game text: “Unleashed upon a foe, these aggressive manifestations of the forest are utilised for their needle-like arrows that inflict painful wounds from afar.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc16_character_abilities_muster_of_malevolents`)*
- Owners: Coeddil
- Proposed activation: **When in melee with a current target: cast at the enemy it is fighting.**
- Run stats: cd 90s · 15s · enemy unit · ×3 uses

**456. No Escape** — *melee_enemy, enemy unit*
- Keys: `wh3_main_character_abilities_no_escape`
- Game text: “"Enough of that flailing about, worm. Now you die!"” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_character_abilities_no_escape`)*
- Owners: not unit-innate (granted by character skill)
- Proposed activation: **When in melee with a current target: cast at the enemy it is fighting.**
- Run stats: cd 90s · 14s · enemy unit · ×3 uses

**457. Pack Trap** — *melee_enemy, enemy unit*
- Keys: `wh3_dlc24_unit_abilities_pack_trap`
- Game text: “Every woven strand of net bears a powerful hex, draining every ounce of pace from the prey caught in its binds.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc24_unit_abilities_pack_trap`)*
- Owners: The Wolfhearts (Akshina Ambushers)
- Proposed activation: **When in melee with a current target: cast at the enemy it is fighting.**
- Run stats: cd 90s · 10s · enemy unit · ×3 uses

**458. Pestilent Potions** — *melee_enemy, enemy unit*
- Keys: `wh3_dlc20_item_abilities_pestilent_potions`
- Game text: “To one blessed by Grandfather Nurgle, these elixirs are restorative brews, but to others they are debilitating poisons.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc20_item_abilities_pestilent_potions`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee with a current target: cast at the enemy it is fighting.**
- Run stats: cd 120s · 25s · enemy unit · ×3 uses

**459. Prey of Anath Raema** — *melee_enemy, enemy unit*
- Keys: `wh_dlc05_character_abilities_prey_of_anath_raema`
- Game text: “By all means summon the bloodthirsty Goddess of the Hunt to assist you, but always make sure you thank her afterwards…” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh_dlc05_character_abilities_prey_of_anath_raema`)*
- Owners: Glade Lord
- Proposed activation: **When in melee with a current target: cast at the enemy it is fighting.**
- Run stats: cd 90s · 16s · enemy unit · ×3 uses

**460. Prey of the Blood God** — *melee_enemy, enemy unit*
- Keys: `wh3_pro12_hero_abilities_prey_of_the_blood_god`
- Game text: “With the odour of his victim thick in his nostrils, Karanak's prey draws closer, the blood scent stronger, until there is no escape…” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_pro12_hero_abilities_prey_of_the_blood_god`)*
- Owners: Karanak
- Proposed activation: **When in melee with a current target: cast at the enemy it is fighting.**
- Run stats: cd 120s · 22s · enemy unit · ×3 uses

**461. Sadistic Snare** — *melee_enemy, enemy unit*
- Keys: `wh3_dlc23_lord_abilities_sadistic_snare`
- Game text: “The beauty in totally immobilising an enemy is that you can decide precisely how they will die.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc23_lord_abilities_sadistic_snare`)*
- Owners: Zhatan the Black
- Proposed activation: **When in melee with a current target: cast at the enemy it is fighting.**
- Run stats: cd 120s · 33s · enemy unit · ×2 uses

**462. Spearfisher's Net** — *melee_enemy, enemy unit*
- Keys: `wh2_dlc11_lord_abilities_spearfishers_net`
- Game text: “"Look at 'em all, trapped like stranded sea-turtles they are!"” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc11_lord_abilities_spearfishers_net`)*
- Owners: Aranessa Saltspite
- Proposed activation: **When in melee with a current target: cast at the enemy it is fighting.**
- Run stats: cd 90s · 18s · enemy unit · ×3 uses

**463. Spiderweb Attack** — *melee_enemy, enemy unit*
- Keys: `wh3_dlc26_character_abilities_spider_web_attack`
- Game text: “Nothing of a true Spider's slow and patient trapping technique, and all of Snagla's flair for... well, everything that the aforementioned is not!” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc26_character_abilities_spider_web_attack`)*
- Owners: Snagla Grobspit
- Proposed activation: **When in melee with a current target: cast at the enemy it is fighting.**
- Run stats: cd 120s · 18s · enemy unit · ×2 uses

**464. Staff of Masks** — *melee_self, enemy unit*
- Keys: `wh3_dlc27_item_abilities_staff_of_the_masque`
- Game text: “A mesmeric whirling of flickering golden masks and flowing, strained limbs draws foes into the Masque’s unholy pageant, pushing them to bone-weary agony.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc27_item_abilities_staff_of_the_masque`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee with a current target: cast at the enemy it is fighting.**
- Run stats: cd 120s · 23s · enemy unit · ×2 uses · item

**465. The Black Tongue** — *melee_enemy, enemy unit*
- Keys: `wh3_dlc27_character_abilities_the_black_tongue`
- Game text: “This Slaaneshi Lord’s noxious combination of herbs magically sublimates a pungent and debilitating aroma that quite literally strangles the tongue.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc27_character_abilities_the_black_tongue`)*
- Owners: Chaos Sorcerer Lord of Slaanesh (Shadows), Chaos Sorcerer Lord of Slaanesh (Slaanesh)
- Proposed activation: **When in melee with a current target: cast at the enemy it is fighting.**
- Run stats: cd 120s · 21s · enemy unit · ×2 uses

**466. Virulent Contagion** — *melee_enemy, enemy unit*
- Keys: `wh3_main_lord_abilities_virulent_contagion` · `wh3_main_lord_abilities_virulent_contagion_upgraded`
- Game text: “Sulphurous, acerbic disease is no respecter of rank, nobility or prowess in battle; all shall fall afore Nurgle's filthy infections.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_lord_abilities_virulent_contagion`)*
- Owners: Daemon Prince, Red Ulgor, Prince of Slaughter, Grand Vomitus, Prince of Buboes, Caress, the Darkling Prince, Zarrivyk, Feathered-Prince (+5 more); unit set(s): nurgle_characters
- Proposed activation: **When in melee with a current target: cast at the enemy it is fighting.**
- Run stats: cd 120s · 30s · enemy unit · ×2 uses

**467. Warden's Cage** — *melee_enemy, enemy unit*
- Keys: `wh2_dlc15_character_abilities_wardens_cage`
- Game text: “The Warden summons a magical cage that temporarily traps his target with no chance of escape.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc15_character_abilities_wardens_cage`)*
- Owners: not unit-innate (granted by character skill)
- Proposed activation: **When in melee with a current target: cast at the enemy it is fighting.**
- Run stats: cd 120s · 25s · enemy unit · ×1 uses

**468. Whip of Misery** — *melee_enemy, enemy unit*
- Keys: `wh2_main_spell_bound_whip_of_agony`
- Game text: “As the caster utters a forbidden name, her enemies are wracked with waves of misery.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_main_spell_bound_whip_of_agony`)*
- Owners: not unit-innate — bound ability (item/skill-granted)
- Proposed activation: **When in melee with a current target: cast at the enemy it is fighting.**
- Run stats: cd 90s · 31s · enemy unit · ×3 uses · bound

**469. Word of Pain** — *melee_enemy, enemy unit*
- Keys: `wh2_dlc10_spell_bound_word_of_pain` · `wh3_dlc27_spell_dark_magic_word_of_pain_bound_1use`
- Game text: “As the caster utters a forbidden name, their enemies are wracked with waves of agony.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc10_spell_bound_word_of_pain`)*
- Owners: Slaanesh's Harvesters (Doomfire Warlocks)
- Proposed activation: **When in melee with a current target: cast at the enemy it is fighting.**
- Run stats: cd 90s · 40s · enemy unit · ×2 uses · bound

**470. Fascination** — *melee_enemy, enemy unit*
- Keys: `wh3_main_army_abilities_fascination`
- Game text: “"Come closer, mortal being. Something almost… imperceptible draws you to me, stirring feelings hitherto buried… Come, it is your true master speaking..."” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_army_abilities_fascination`)*
- Owners: army of: Keepers of Bliss, The Accursed Troupe, The Tormentors
- Proposed activation: **When in melee with a current target: cast at the enemy it is fighting.**
- Run stats: cd 120s · 14s · enemy unit · wind-up 5s · army · army bar

**471. Fecund Rebirth** — *melee_enemy, enemy unit*
- Keys: `wh3_dlc29_character_active_mark_of_the_monster`
- Game text: “A host of Daemon Flies plunges down the ailing beast's throat, laying a thousand eggs. The wriggling larvae nestle among the lungs, guts, and heart – chewing the three-pocked mark through their innards, heralding the agonised birth of a creature darker still.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc29_character_active_mark_of_the_monster`)*
- Owners: not unit-innate (granted by character skill)
- Proposed activation: **When in melee with a current target: cast at the enemy it is fighting.**
- Run stats: cd 90s · 32s · enemy unit · wind-up 1s

**472. Otto's Scythe** — *melee_enemy, enemy unit*
- Keys: `wh3_dlc29_item_active_ottos_scythe`
- Game text: “Encrusted with bile and pus, Otto's plague-carrying scythe cuts down foes as easily as it reaps the harvest.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc29_item_active_ottos_scythe`)*
- Owners: not unit-innate (granted by character skill)
- Proposed activation: **When in melee with a current target: cast at the enemy it is fighting.**
- Run stats: cd 120s · 28s · enemy unit · wind-up 1s

**473. Ravaging Swarm** — *melee_enemy, enemy unit*
- Keys: `wh3_dlc29_hero_active_dispatch_the_swarm_attack` · `wh3_dlc29_hero_active_dispatch_the_swarm_attack_upgraded`
- Game text: “Bloab's swollen pall of of flies reaches out and engulfs his enemies, the creatures stinging, biting and infesting any flesh they can reach.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc29_hero_active_dispatch_the_swarm_attack`)*
- Owners: Bloab Rotspawned
- Proposed activation: **When in melee with a current target: cast at the enemy it is fighting.**
- Run stats: cd 120s · 24s · enemy unit · wind-up 1s

**474. Tendrils of the Sea** — *melee_enemy, enemy unit*
- Keys: `wh3_dlc29_hero_active_tendrils_of_the_sea`
- Game text: “A true gift for bringing low the terrifying creatures that lurk beneath the frigid waves of the Norscan coast.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc29_hero_active_tendrils_of_the_sea`)*
- Owners: Gutrot Spume
- Proposed activation: **When in melee with a current target: cast at the enemy it is fighting.**
- Run stats: cd 120s · 24s · enemy unit · wind-up 3s

**475. Whispering Mist** — *melee_enemy, enemy unit*
- Keys: `wh3_dlc29_hero_abilities_whispering_mist`
- Game text: “Cold mists curl about the enemy like a maiden's distracting caress.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc29_hero_abilities_whispering_mist`)*
- Owners: Lahmian Vampire
- Proposed activation: **When in melee with a current target: cast at the enemy it is fighting.**
- Run stats: cd 90s · 32s · enemy unit · wind-up 1s

**476. Acquiescence** — *melee_enemy, enemy unit*
- Keys: `wh3_dlc27_spell_bound_acquiescence`
- Game text: “The spellcaster's corrupting touch puts their victims into a blissful, euphoric state for a short time, rendering them little able to move, let alone defend themselves.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc27_spell_bound_acquiescence`)*
- Owners: not unit-innate — bound ability (item/skill-granted)
- Proposed activation: **When in melee with a current target: cast at the enemy it is fighting.**
- Run stats: cd 60s · 25s · enemy unit · ×2 uses · wind-up 1s · bound

**477. Frozen on the Pyre** — *melee_enemy, enemy unit*
- Keys: `wh3_dlc27_army_abilities_eternal_dance_tempo_3_submission_to_the_prince`
- Game text: “Virulent brutes and pestilential scum alike will stand slack-jawed amidst the maze of our fire-borne forms and shiver to ashes amidst their gardens.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc27_army_abilities_eternal_dance_tempo_3_submission_to_the_prince`)*
- Owners: army-bar ability (no unit junction)
- Proposed activation: **When in melee with a current target: cast at the enemy it is fighting.**
- Run stats: cd 90s · 36s · enemy unit · ×3 uses · wind-up 1s · army · army bar

**478. The Enfeebling Foe** — *melee_enemy, enemy unit*
- Keys: `wh3_dlc23_spell_bound_enfeebling_foe` · `wh3_dlc27_spell_bound_enfeebling_foe` · `wh3_main_spell_bound_enfeebling_foe` · `wh3_twa08_spell_bound_enfeebling_foe_keeper_of_secrets_ror`
- Game text: “By means of the Lore of Shadows, the Wizard causes the enemy to be worn down by their own burdens, until they are enervated to a sorry standstill.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc23_spell_bound_enfeebling_foe`)*
- Owners: Daemonsmith Sorcerer (Death), Daemonsmith Sorcerer (Fire), Daemonsmith Sorcerer (Hashut), Daemonsmith Sorcerer (Metal), Overseer (+8 more); unit set(s): mp_cap_unit_sla_mon_keeper_of_secrets_0_ror
- Proposed activation: **When in melee with a current target: cast at the enemy it is fighting.**
- Run stats: cd 60s · 17s · enemy unit · ×1 uses · wind-up 1s · bound


### Tier 6 — enemy-ground (needs target + placement policy) (9 items)

**479. Arachnarok Eggs** — *melee_enemy, enemy ground*
- Keys: `wh_dlc08_item_abilities_arachnarok_eggs`
- Game text: “Each egg contains deadly spiderlings, to swarm over and bite the foe's body, injecting deadly venom into the wounds.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh_dlc08_item_abilities_arachnarok_eggs`)*
- Owners: not unit-innate — item/weapon ability (equip-granted)
- Proposed activation: **When in melee: cast on the ground under its current target (placement policy needed).**
- Run stats: cd 60s · 1s · enemy ground · ×5 uses

**480. Curse of Djaf** — *melee_enemy, enemy ground*
- Keys: `wh2_dlc09_character_abilities_curse_of_djaf`
- Game text: “The essence of the Jackal-headed God imbues the bearer's weapons with an insatiable hunger for the souls of the living.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc09_character_abilities_curse_of_djaf`)*
- Owners: Tomb Prince
- Proposed activation: **When in melee: cast on the ground under its current target (placement policy needed).**
- Run stats: cd 0s · 13s · enemy ground · ×1 uses

**481. Spinning Loons** — *melee_self, enemy ground*
- Keys: `wh_main_unit_abilities_spinning_loons`
- Game text: “Sent mad by drinking fungus brew, Night Goblin Fanatics are released from their mobs as a twirling cyclone of destruction armed with a large ball and chain!” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh_main_unit_abilities_spinning_loons`)*
- Owners: Night Goblin Archers (Fanatics), Night Goblins (Fanatics); unit set(s): grn_fanatics
- Proposed activation: **When in melee: cast on the ground under its current target (placement policy needed).**
- Run stats: cd 30s · 12s · enemy ground · ×3 uses

**482. The Curse of Anraheir** — *melee_enemy, enemy ground*
- Keys: `wh2_dlc16_spell_bound_the_curse_of_anraheir` · `wh3_main_spell_bound_the_curse_of_anraheir` · `wh_dlc05_spell_bound_the_curse_of_anraheir`
- Game text: “At the spellcaster's command, nebulous nature spirits assail the foe, clawing with hands not nearly as insubstantial as they first appear.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc16_spell_bound_the_curse_of_anraheir`)*
- Owners: Sisters of the Thorn; unit set(s): wef_dlc05_wood_elf_sisters_thorn
- Proposed activation: **When in melee: cast on the ground under its current target (placement policy needed).**
- Run stats: cd 120s · 21s · enemy ground · ×1 uses · bound

**483. The Loons of Eight Peaks** — *melee_self, enemy ground*
- Keys: `wh_dlc06_unit_abilities_the_loons_of_eight_peaks`
- Game text: “The Goblin Fanatics of Karak Eight Peaks eschew the use of balls with their chains, favouring shaved Dwarfs instead!” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh_dlc06_unit_abilities_the_loons_of_eight_peaks`)*
- Owners: Da Eight Peak Loonies (Night Goblins – Fanatics)
- Proposed activation: **When in melee: cast on the ground under its current target (placement policy needed).**
- Run stats: cd 30s · 12s · enemy ground · ×3 uses

**484. Dance of Despair** — *melee_enemy, enemy ground*
- Keys: `wh3_dlc20_cataclysm_bound_dance_of_despair` · `wh3_dlc27_cataclysm_bound_dance_of_despair`
- Game text: “The Wizard produces a stringless fiddle and plays a haunting dirge that drives all sense of hope and urgency away, rendering the foe passive and prone.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_dlc20_cataclysm_bound_dance_of_despair`)*
- Owners: not unit-innate — bound ability (item/skill-granted)
- Proposed activation: **When in melee: cast on the ground under its current target (placement policy needed).**
- Run stats: cd 120s · 45s · enemy ground · ×1 uses · wind-up 5s · bound

**485. Soulblight** — *melee_enemy, enemy ground*
- Keys: `wh2_dlc10_spell_bound_soulblight` · `wh3_dlc29_spell_bound_soulblight`
- Game text: “Harnessing the sickly power of Shyish, the Wizard weakens the foe's will to survive the battle.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh2_dlc10_spell_bound_soulblight`)*
- Owners: Doomfire Warlocks, Lahmian Handmaidens (Death); unit set(s): mp_cap_unit_vmp_inf_lahmian_handmaidens_death
- Proposed activation: **When in melee: cast on the ground under its current target (placement policy needed).**
- Run stats: cd 90s · 20s · enemy ground · ×2 uses · wind-up 3s · bound

**486. The Land Awakened** — *melee_enemy, enemy ground*
- Keys: `wh3_main_army_abilities_the_land_awakened`
- Game text: “Believe enough and the very ground shall spew forth its wrath: the very embodiment of Ursun come to smite His enemies.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_army_abilities_the_land_awakened`)*
- Owners: army-bar ability (no unit junction)
- Proposed activation: **When in melee: cast on the ground under its current target (placement policy needed).**
- Run stats: cd 120s · 1s · enemy ground · ×1 uses · wind-up 5s · army · army bar

**487. Transmutation of Lead** — *melee_enemy, enemy ground*
- Keys: `wh3_main_spell_bound_transmutation_of_lead`
- Game text: “Transformed into lead, the foe’s weapons become heavy, cumbersome, and almost impossible to wield in battle, let alone use effectively.” *(source: WH3 loc `unit_abilities__.loc.tsv`, entry `unit_abilities_tooltip_text_wh3_main_spell_bound_transmutation_of_lead`)*
- Owners: not unit-innate — bound ability (item/skill-granted)
- Proposed activation: **When in melee: cast on the ground under its current target (placement policy needed).**
- Run stats: cd 120s · 50s · enemy ground · ×1 uses · wind-up 5s · bound

---

## 3. Full inventory tables (every castable ability, one row each)

### 3a. Main table — all non-spell abilities except the friendly-fire block

(Implemented rows first in their group; melee candidates cross-reference §2. `q#` = questionnaire item number.)

| Ability | Status | Group | Auto-activation proposal | Notes |
|---|---|---|---|---|
| Blood Lust `wh_dlc03_character_abilities_blood_lust` | `implemented` | melee_self | built: in melee, morale not wavering, fail-open; self-cast (field-verified) | cd 60s · 33s · friend |
| Blood Lust `wh_main_character_abilities_blood_lust` | `implemented` | melee_self | built: in melee, morale not wavering, fail-open; self-cast (field-verified) | cd 60s · 33s · friend |
| Foe-Seeker `wh_dlc03_character_abilities_foe_seeker` | `implemented` | melee_self | built: fatigue Tired or worse, fail-closed; fires up to 3x when an ability carries no text (field-verified) | cd 60s · 25s · self |
| Foe-Seeker `wh_main_character_abilities_foe_seeker` | `implemented` | melee_self | built: fatigue Tired or worse, fail-closed; fires up to 3x when an ability carries no text (field-verified) | cd 60s · 25s · self |
| Grand Hammer of Sigmar `wh_dlc04_spell_bound_hammer_of_sigmar_upgraded` | `implemented` | melee_self | built: in melee, not routing (field-verified) | cd 90s · 50s · self · bound |
| Hammer of Sigmar `wh_main_spell_bound_hammer_of_sigmar` | `implemented` | melee_self | built: in melee, not routing (field-verified) | cd 60s · 25s · self · bound |
| Stand Your Ground! `wh_main_character_abilities_stand_your_ground` | `implemented` | melee_self | built: in melee + morale at/below wavering, fail-open (field-verified) | cd 90s · 18s · self |
| Tacticians, Stand Your Ground! `wh3_dlc24_character_abilities_tacticians_stand_your_ground` | `implemented` | melee_self | built: in melee + morale at/below wavering, fail-open (field-verified) | cd 90s · 18s · friend/self |
| "Stay Here, I'll Get Help!" `wh2_dlc09_character_abilities_stay_here_ill_get_help` | `implemented (ally-targeted: waver_ally)` | ally_unit | When an ally in range is wavering: cast on that ally. NO melee requirement — the ally need not be in melee (same evaluator shape as Will of the Verminking: closest ally in range, conservative range, drift re-check). | cd 90s · 35s · friend/self · ×3 uses · questionnaire §2 #319 · user: “If ally in range is wavering.” · **round 98 (Class B):** casts ON THE CHOSEN ALLY - ally wavering - the picked WAVERING ally (the cast-target fix); own 70% bound = floor(60 * 0.70) = 42 m (FOURTH.ALLY_CAST_R60), offer test on unit:unit_distance only, fresh caster+ally handles. Was the #250 cast-target gap |
| Acid Burps `wh3_dlc26_unit_abilities_acid_vomit` | `excluded (auto: vortex)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 14s · self · questionnaire §2 #1 |
| Aether Sword `wh3_dlc20_weapon_abilities_aether_sword` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 27s · self · questionnaire §2 #3 |
| Alakanash, the Staff of Power `wh3_dlc29_item_abilities_alakanash_the_staff_of_power` | `skipped (unsuitable: vortex)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 21s · self · ×3 uses · wind-up 1s · item · questionnaire §2 #294 |
| Alchemist's Elixir of Iron Skin `wh3_main_item_abilities_alchemists_elixir_of_iron_skin` | `implemented (in-melee self)` | melee_self | When in melee: cast on self for now (nearest-ally picker later). | cd 90s · 25s · friend · ×2 uses · questionnaire §2 #382 |
| Alchemist's Elixir of Puissance `wh3_main_item_abilities_alchemists_elixir_of_puissance` | `implemented (in-melee self)` | melee_self | When in melee: cast on self for now (nearest-ally picker later). | cd 90s · 29s · friend · ×2 uses · questionnaire §2 #383 |
| Alchemist's Elixir of Venom `wh3_main_item_abilities_alchemists_elixir_of_venom` | `implemented (in-melee self)` | melee_self | When in melee: cast on self for now (nearest-ally picker later). | cd 90s · 36s · friend · ×1 uses · questionnaire §2 #384 |
| Amulet of Itzl `wh2_main_item_abilities_amulet_of_itzl` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 60s · 18s · self · ×1 uses · questionnaire §2 #231 |
| Ancestral Rune of Grungni `wh2_dlc17_army_abilities_ancestral_rune_of_grungni` | `skipped (army-bar ability)` | melee_self | When in melee: cast at own feet (existing ground-cast path). | cd 120s · 35s · ground · ×3 uses · wind-up 5s · army · questionnaire §2 #347 |
| Apocalyptic Charge `wh_pro04_unit_abilities_apocalyptic_charge` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 30s · self · questionnaire §2 #5 |
| Apocalyptic Vision `wh_dlc03_character_abilities_apocalyptic_vision` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 18s · self · questionnaire §2 #6 |
| Arcane Hymn `wh3_cp1_character_abilities_magic_prayer` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 27s · self · questionnaire §2 #7 |
| Ark of Sotek `wh2_dlc12_unit_abilities_ark_of_sotek` | `skipped (unsuitable: vortex)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 26s · self · wind-up 1s · questionnaire §2 #269 |
| Armour of Contempt `wh3_dlc23_army_abilities_armour_of_contempt` | `skipped (army-bar ability)` | melee_self | When in melee: cast on self (self-cast allowed; nearest-ally picker later). | cd 120s · 26s · friend/self · ×3 uses · army · questionnaire §2 #320 |
| Armour of Gazrakh `wh3_dlc23_item_abilities_armour_of_gazrakh` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 48s · self · questionnaire §2 #8 |
| Arsebelcher `wh3_main_character_abilities_arsebelcher` | `excluded (auto: vortex)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 4s · self · character · questionnaire §2 #10 |
| Aura of Quetzl `wh2_main_item_abilities_aura_of_quetzl` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 25s · self · questionnaire §2 #11 |
| Axe of Dargo `wh_main_weapon_abilities_axe_of_dargo` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 29s · self · questionnaire §2 #12 |
| Axe of Grom `wh2_dlc15_weapon_abilities_axe_of_grom` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 29s · self · questionnaire §2 #13 |
| Axes of Kadrin `wh3_dlc25_weapon_abilities_axes_of_kadrin` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 21s · self · questionnaire §2 #14 |
| Azhag's 'Ard Armour `wh2_dlc15_item_abilities_azhags_ard_armour` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 38s · self · questionnaire §2 #15 |
| Ballet of Blows `wh3_main_lord_abilities_ballet_of_blows` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 45s · self · questionnaire §2 #16 |
| Bangers & Smash `wh2_dlc15_character_abilities_sausage_busta` | `implemented (charge or wavering)` | melee_self | In the charge window OR when wavering: cast on self. (trigger variant — charge or wavering) | cd 120s · 36s · self · ×3 uses · wind-up 1s · questionnaire §2 #295 · user: “When charging or wavering” |
| Barbed-Knuckle Boxing `wh2_dlc17_lord_abilities_barbed_knuckle_boxing` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 29s · self · questionnaire §2 #17 |
| Basking in Our Flame `wh3_dlc27_army_abilities_eternal_dance_tempo_3_needful_caress` | `skipped (army-bar ability)` | melee_self | When in melee: cast at own feet (existing ground-cast path). | cd 120s · 36s · ground · ×2 uses · wind-up 2s · army · questionnaire §2 #348 |
| Bastion of the Great Cities `wh3_dlc24_unit_abilities_bastion_of_the_great_cities` | `rejected (auto: mutual exclusivity)` | melee_self | When in melee (and not fleeing): cast on self. | cd 30s · -1s · self · questionnaire §2 #18 · user reason: mutual exclusivity (player decides) |
| Bastion's Defenders `wh3_dlc24_character_abilities_bastions_defenders` | `implemented (in-melee self)` | melee_self | When in melee: cast on self for now (nearest-ally picker later). | cd 90s · 30s · friend · questionnaire §2 #354 |
| Battle Howl `wh3_dlc29_ability_bound_prayer_battle_howl` | `skipped (unsuitable: movement)` | melee_self | When in melee (and not fleeing): cast on self. | cd 60s · 15s · self · wind-up 0.5s · unit · questionnaire §2 #270 |
| Battle Howl `wh3_dlc29_spell_bound_prayer_battle_howl` | `skipped (unsuitable: movement)` | melee_self | When in melee (and not fleeing): cast on self. | cd 60s · 15s · self · wind-up 0.5s · bound · questionnaire §2 #270 |
| Battle of Wills `wh3_dlc29_unit_abilities_battle_of_wills` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 20s · self · wind-up 5s · questionnaire §2 #271 |
| Bear Fang Talisman `wh3_dlc27_item_abilities_bear_fang_talisman` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 25s · self · questionnaire §2 #19 |
| Beastlord's Gaze `wh2_twa03_lord_abilities_beastlords_gaze` | `skipped (revisit)` | melee_self | When in melee: cast on self for now (nearest-ally picker later). | cd 60s · 40s · friend · questionnaire §2 #355 · user: “Skip for now” |
| Beastslaver `wh2_dlc14_lord_abilities_beastslaver` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 60s · 34s · self · questionnaire §2 #20 |
| Birona's Timewarp `wh_main_spell_bound_bironas_timewarp` | `implemented (charge and in-melee)` | melee_self | When in melee: cast on self (self-cast allowed; nearest-ally picker later). | cd 47s · 50s · friend/self · ×1 uses · wind-up 5s · bound · questionnaire §2 #326 |
| Black Lotus `wh2_main_character_abilities_black_lotus` | `implemented (in-melee self - auto, trivial)` | melee_self | When in melee (and not fleeing): cast on self. | cd 60s · 44s · self · ×1 uses · questionnaire §2 #232 |
| Blade of Bel-Korhadris `wh2_main_item_abilities_blade_of_bel_korhadris` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 38s · self · questionnaire §2 #21 |
| Blades of Shang-Yang `wh3_cp1_weapon_abilities_blades_of_shang_yang` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 32s · self · questionnaire §2 #22 |
| Blood-Forged Armour `wh2_dlc15_item_abilities_blood_forged_armour` | `excluded (auto: vortex)` | melee_self | When in melee (and not fleeing): cast on self. | cd 30s · 12s · self · questionnaire §2 #23 |
| Bloodbeast `wh2_dlc17_lord_abilities_bloodbeast` | `excluded (auto: vortex)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 6s · self · questionnaire §2 #24 |
| Bloodstorm `wh2_dlc14_lord_abilities_bloodstorm` | `excluded (auto: vortex)` | melee_self | When in melee (and not fleeing): cast on self. | cd 60s · 9s · self · questionnaire §2 #25 |
| Bloodstorm Blades `wh3_dlc26_weapon_abilities_bloodstorm_blades` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 35s · self · questionnaire §2 #26 |
| Blooood! `wh_main_unit_abilities_blooood` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 60s · 18s · self · questionnaire §2 #27 |
| Book of Arkhan `wh_main_spell_bound_book_of_arkhan` | `implemented (in-melee self)` | melee_self | When in melee: cast on self for now (nearest-ally picker later). | cd 60s · 25s · friend · ×4 uses · bound · questionnaire §2 #385 |
| Brass Body `wh2_dlc17_lord_abilities_brass_body` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 41s · self · questionnaire §2 #28 |
| Breath of Hatred `wh3_dlc23_bound_abilities_breath_of_hatred` | `implemented (in-melee self)` | melee_self | When in melee: cast on self (self-cast allowed; nearest-ally picker later). | cd 90s · 31s · friend/self · ×3 uses · bound · questionnaire §2 #321 |
| Breath of Hatred `wh3_dlc23_character_abilities_breath_of_hatred` | `implemented (in-melee self)` | melee_self | When in melee: cast on self (self-cast allowed; nearest-ally picker later). | cd 90s · 31s · friend/self · ×3 uses · character · questionnaire §2 #321 |
| Burning Rage `wh3_main_lord_abilities_burning_rage` | `excluded (auto: vortex)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 7s · self · ×3 uses · questionnaire §2 #233 |
| Burp of Grom `wh2_dlc15_character_abilities_burp_of_grom_0` | `excluded (auto: vortex)` | melee_self | When in melee (and not fleeing): cast on self. | cd 60s · 17s · self · questionnaire §2 #29 |
| Burp of Grom `wh2_dlc15_character_abilities_burp_of_grom_1` | `excluded (auto: vortex)` | melee_self | When in melee (and not fleeing): cast on self. | cd 60s · 17s · self · questionnaire §2 #29 |
| Burp of Grom `wh2_dlc15_character_abilities_burp_of_grom_2` | `excluded (auto: vortex)` | melee_self | When in melee (and not fleeing): cast on self. | cd 60s · 17s · self · questionnaire §2 #29 |
| Call for Power `wh3_main_daemon_head_abilities_call_for_power` | `rejected (rampage)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 30s · self · questionnaire §2 #30 · user reason: Rampage! (loss of control — player decides) |
| Call of Tor `wh3_twa07_spell_bound_call_of_tor` | `skipped (unsuitable: bombardment/ranged)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 7s · self · wind-up 1s · bound · questionnaire §2 #272 |
| Captain of the Phoenix Guard `wh3_dlc27_character_abilities_captain_of_the_phoenix_guard` | `implemented (ally-targeted: ally_heal_melee)` | ally_unit | Activate in melee AND at ≤ 75% health: cast on self — the Potion-of-Toughness gate (the ability also grants Physical Resistance to allies). (trigger variant — in melee and health<=75) | cd 120s · 43s · friend · questionnaire §2 #356 · in melee and health<=75 · user: “In melee and below 75% health” · **round 98 (Class B):** casts ON THE CHOSEN ALLY - ally heal - owner in melee (the melee+health gate), the LOWEST-health ally at or below 75%; own 70% bound = floor(50 * 0.70) = 35 m (FOURTH.ALLY_CAST_R50), offer test on unit:unit_distance only, fresh caster+ally handles. Was a self-cast |
| Cascading Fire Cloak `wh3_main_spell_bound_cascading_fire_cloak` | `implemented (in-melee self)` | melee_self | When in melee: cast on self for now (nearest-ally picker later). | cd 60s · 19s · friend · ×2 uses · wind-up 1s · bound · questionnaire §2 #403 |
| Cash Cascade `wh3_dlc26_character_abilities_cash_cascade` | `implemented (charge and in-melee)` | melee_self | Activate in the charge window OR in melee (and not fleeing): cast on self — mirrors Fangspike. (trigger variant — charge and in melee) | cd 120s · 30s · friend/self · questionnaire §2 #305 · charge and in melee |
| Celestial Sweep `wh3_dlc24_lord_abilities_celestial_sweep` | `skipped (unsuitable: vortex)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 4s · self · wind-up 0.1s · questionnaire §2 #273 |
| Cellular Instability `wh2_dlc16_unit_abilities_cellular_instability` | `skipped (unsuitable: vortex)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 6s · self · ×1 uses · wind-up 1s · questionnaire §2 #296 |
| Change or Die! `wh3_dlc24_character_abilities_change_or_die` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 22s · self · questionnaire §2 #31 |
| Chanson of Caging `wh3_dlc27_lord_abilities_chanson_of_caging` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 20s · -1s · self · lord · questionnaire §2 #32 · user: “Makes sense, but could be better. Let's say Yes for now but pending for review.” |
| Claws of Mourkain `wh2_dlc11_lord_abilities_claws_of_mourkain` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 34s · self · questionnaire §2 #33 |
| Cloak of Mists & Shadows `wh_main_item_abilities_cloak_of_mists_and_shadows` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 29s · self · questionnaire §2 #34 |
| Coat in Blood `wh3_dlc29_hero_abilities_coat_in_blood` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 17s · self · questionnaire §2 #35 |
| Commanding Presence `wh3_dlc29_lord_active_commanding_presence` | `implemented (wavering self-or-ally in range)` | melee_self | When the lord or a nearby unit is wavering: cast on self. (redesigned — morale-based, not melee) | cd 60s · 20s · self · questionnaire §2 #36 · user: “Not related to melee, only to morale. The trigger should be when lord or nearby unit are wavering.” |
| Creature-Killer `wh2_dlc16_weapon_abilities_creature_killer` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 38s · self · questionnaire §2 #37 |
| Curse of Years `wh3_dlc29_spell_bound_curse_of_years` | `implemented (in-melee self - auto, trivial)` | melee_self | When in melee (and not fleeing): cast on self. | cd 47s · 35s · self · ×2 uses · wind-up 1s · questionnaire §2 #297 |
| Da Boss 'as a Plan! `wh3_dlc26_character_abilities_da_boss_as_a_plan` | `implemented (ally-targeted: ally_melee_buff)` | ally_unit | When in melee: cast on self for now (nearest-ally picker later). | cd 90s · 20s · friend · questionnaire §2 #357 · **round 98 (Class B):** casts ON THE CHOSEN ALLY - ally buff - the CLOSEST ally in range; owner in melee (not routing / not wavering); own 70% bound = floor(150 * 0.70) = 105 m (FOURTH.ALLY_CAST_R150), offer test on unit:unit_distance only, fresh caster+ally handles. Was a self-cast |
| Da Great 'Un Iz 'Ere! `wh2_dlc15_lord_abilities_da_great_un_iz_ere` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 21s · self · questionnaire §2 #38 |
| Daemon Flask of Ashak `wh3_dlc23_item_abilities_daemon_flask_of_ashak` | `excluded (auto: vortex)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 5s · self · ×1 uses · questionnaire §2 #234 |
| Daemonblade `wh3_dlc20_weapon_abilities_daemonblade` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 32s · self · questionnaire §2 #39 |
| Daemonic Strength `wh_main_item_abilities_daemonic_strength` | `implemented (in-melee self - auto, trivial)` | melee_self | When in melee (and not fleeing): cast on self. | cd 60s · 22s · self · ×1 uses · questionnaire §2 #235 |
| Daemonshield `wh3_dlc20_item_abilities_daemonshield` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 13s · self · questionnaire §2 #40 |
| Dagger of Malice `wh3_dlc23_weapon_abilities_dagger_of_malice` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 17s · self · questionnaire §2 #41 |
| Daggerdance `wh3_dlc27_lord_abilities_daggerdance` | `rejected (drawback)` | melee_self | When in melee (and not fleeing): cast on self. | cd 30s · -1s · self · questionnaire §2 #42 · user reason: drawbacks (player decides) |
| Dance of Destruction `wh3_dlc27_lord_abilities_dance_of_destruction` | `rejected (drawback)` | melee_self | When in melee (and not fleeing): cast on self. | cd 30s · -1s · self · questionnaire §2 #43 · user reason: drawback (player decides) |
| Dark Conduit `wh2_main_army_abilities_dark_conduit` | `excluded (auto: army-bar ability (standing rule 10))` | melee_self | When in melee: cast on self for now (nearest-ally picker later). | cd 120s · 27s · friend · ×3 uses · wind-up 5s · army · questionnaire §2 #404 |
| Dark Fortune `wh_main_item_abilities_dark_fortune` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 60s · 57s · self · ×1 uses · questionnaire §2 #236 |
| Dark Protection `wh2_dlc11_lord_abilities_dark_protection` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 30s · self · questionnaire §2 #44 |
| Dark Venom `wh2_main_character_abilities_dark_venom` | `implemented (in-melee self - auto, trivial)` | melee_self | When in melee (and not fleeing): cast on self. | cd 60s · 40s · self · ×1 uses · questionnaire §2 #237 |
| Darkwalker `wh3_dlc25_lord_abilities_darkwalker` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 30s · self · questionnaire §2 #45 |
| Dazh's Song of Winter Sunlight `wh3_main_character_abilities_dazs_song_of_winter_sunlight` | `implemented (tired)` | melee_self | When Tired: cast on self. (redesigned — vigor-based, not melee) | cd 90s · 10s · self · questionnaire §2 #46 · user: “Ideally vigor based, not melee based. Activate when Tired.” |
| Dazh's Song of Winter Sunlight `wh3_twa06_unit_abilities_dazs_song_of_winter_sunlight` | `implemented (tired)` | melee_self | When Tired: cast on self. (redesigned — vigor-based, not melee) | cd 90s · 10s · self · ×1 uses · questionnaire §2 #46 · user: “Ideally vigor based, not melee based. Activate when Tired.” |
| Death Frenzy `wh2_dlc16_spell_bound_death_frenzy` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 28s · self · ×1 uses · wind-up 3s · questionnaire §2 #298 |
| Deathbringer `wh3_main_lord_abilities_deathbringer` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 29s · self · questionnaire §2 #47 |
| Deathbringer Upgraded `wh3_main_lord_abilities_deathbringer_upgraded` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 29s · self · questionnaire §2 #47 |
| Defiling Deluge `wh3_twa08_unit_abilities_defiling_deluge` | `excluded (auto: own-troop-damage AoE (friendly fire by design, family decision 2026-10-09))` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 6s · self · ×2 uses · questionnaire §2 #238 · triage-family: Own-troop-damage AoE |
| Desertstrike `wh2_dlc09_character_abilities_strike_of_nehekhara` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 23s · self · questionnaire §2 #48 |
| Destruction `wh3_dlc29_spell_bound_prayer_destruction` | `skipped (unsuitable: vortex)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 3s · self · wind-up 0.5s · questionnaire §2 #274 |
| Dinner Bell `wh3_dlc26_character_abilities_dinner_bell` | rejected (drawback) | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 55s · self · questionnaire §2 #49 · user reason: drawback (30% miscast) (player decides) |
| Disdain of the Dragon Emperor `wh3_dlc24_unit_abilities_disdain_of_the_dragon_emperor` | rejected (auto: mutual exclusivity) | melee_self | When in melee (and not fleeing): cast on self. | cd 30s · -1s · self · questionnaire §2 #50 · user reason: mutual exclusivity (player decides) |
| Dolorous Blade `wh_dlc07_hero_abilities_dolorous_blade` | implemented (in-melee self) | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 33s · self · questionnaire §2 #51 |
| Doom Glaive `wh3_dlc29_item_abilities_doom_glaive` | `implemented (in-melee self - auto, trivial)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 27s · self · ×3 uses · questionnaire §2 #239 |
| Doom Lord `wh3_dlc29_lord_abilities_doom_lord` | `implemented (in-melee self)` | melee_self | When in melee: cast on self for now (nearest-ally picker later). | cd 120s · 40s · friend · wind-up 1s · questionnaire §2 #394 |
| Dragon Spear `wh2_dlc16_weapon_abilities_dragon_spear` | implemented (in-melee self) | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 25s · self · questionnaire §2 #52 |
| Dragonhorn `wh2_dlc15_lord_abilities_dragonhorn` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 16s · self · ×3 uses · wind-up 6s · questionnaire §2 #299 |
| Dreaded Duellist `wh2_dlc11_lord_abilities_dreaded_duelist` | implemented (in-melee self) | melee_self | When in melee (and not fleeing): cast on self. | cd 60s · 22s · self · questionnaire §2 #53 |
| Dwarf Gouger `wh2_main_weapon_abilities_dwarf_gouger` | implemented (in-melee self) | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 36s · self · questionnaire §2 #54 |
| Eagle-Feather Torc `wh3_dlc27_item_abilities_eagle_feather_torc` | `implemented (barrier_broken)` | melee_self | When the barrier is broken: cast on self. (redesigned — barrier-based, not melee) | cd 120s · 10s · self · questionnaire §2 #55 · user: “Condition should be when barrier is broken” |
| Elixir of Damnation `wh3_dlc27_item_abilities_elixir_of_damnation` | `implemented (in-melee self - auto, trivial)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 19s · self · ×5 uses · item · questionnaire §2 #240 |
| Elixir of Might `wh2_dlc09_item_abilities_elixir_of_might` | `implemented (in-melee self)` | melee_self | When in melee: cast on self for now (nearest-ally picker later). | cd 60s · 36s · friend · ×1 uses · questionnaire §2 #386 |
| Empowering Shrooms `wh3_dlc26_character_abilities_empowering_shrooms` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 35s · friend/self · questionnaire §2 #306 |
| Enchanted Metallurgy `wh3_main_character_abilities_enchanted_metallurgy` | `implemented (metallurgy_melee)` | melee_self | When self or an ally in range is in melee: cast on the owner or that ally. When an ally in range is shooting: cast on that ally. (MELEE self-or-ally half IMPLEMENTED, harness89; the SHOOTING half is NOT built — research complete: the battle API exposes NO per-unit is-firing/is-shooting read, so no proxy was invented. Cast on self.) | cd 60s · 12s · friend/self · questionnaire §2 #307 · user: “When self or ally in range in melee. When ally in range is shooting.” |
| Enchanted Metallurgy: Flaming `wh3_main_character_abilities_enchanted_metallurgy_flaming` | `implemented (metallurgy_melee)` | melee_self | Same as Enchanted Metallurgy (melee self-or-ally / shooting ally in range): melee self-or-ally half IMPLEMENTED (harness89); shooting half NOT built (no per-unit is-firing/is-shooting read in the battle API). | cd 90s · 14s · friend/self · questionnaire §2 #308 |
| Enchanted Metallurgy: Piercing `wh3_main_character_abilities_enchanted_metallurgy_piercing` | `implemented (metallurgy_melee)` | melee_self | Same as Enchanted Metallurgy (melee self-or-ally / shooting ally in range): melee self-or-ally half IMPLEMENTED (harness89); shooting half NOT built (no per-unit is-firing/is-shooting read in the battle API). | cd 90s · 14s · friend/self · questionnaire §2 #309 |
| Enchanted Metallurgy: Poison `wh3_main_character_abilities_enchanted_metallurgy_poison` | `implemented (metallurgy_melee)` | melee_self | Same as Enchanted Metallurgy (melee self-or-ally / shooting ally in range): melee self-or-ally half IMPLEMENTED (harness89); shooting half NOT built (no per-unit is-firing/is-shooting read in the battle API). | cd 90s · 12s · friend/self · questionnaire §2 #310 |
| Endless Whirlwind of Death `wh3_dlc25_unit_abilities_whirlwind_of_death_ror` | rejected (friendly fire) | melee_self | When in melee (and not fleeing): cast on self. | cd 60s · 6s · self · questionnaire §2 #56 · user reason: friendly fire (player decides) |
| Endless Whirlwind of Death Upgraded `wh3_dlc25_unit_abilities_whirlwind_of_death_ror_upgraded` | rejected (friendly fire) | melee_self | When in melee (and not fleeing): cast on self. | cd 60s · 6s · self · questionnaire §2 #56 · user reason: friendly fire (player decides) |
| Enhanced Skavenbrew `wh3_dlc29_item_abilities_enhanced_skavenbrew` | `implemented (in-melee self)` | melee_self | When in melee: cast on self for now (nearest-ally picker later). | cd 90s · 60s · friend · ×2 uses · questionnaire §2 #387 |
| Enkhil's Kanopi `wh2_dlc09_item_abilities_enkhils_kanopi` | skipped (not achievable) | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 24s · self · questionnaire §2 #57 · not achievable: needs a spell-cast event or an enemy unit read (neither exists) |
| Enrage `wh_pro04_unit_abilities_enrage` | implemented (in-melee self) | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 22s · self · questionnaire §2 #58 |
| Entice `wh3_dlc29_unit_abilities_entice` | implemented (in-melee self) | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 24s · self · questionnaire §2 #59 |
| Epidemic Outbreak `wh3_dlc25_character_abilties_epidemic_outbreak_improved` | rejected (tactical escape) | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 2s · self · questionnaire §2 #60 · user: “the escape in melee is tactically relevant and must be chosen by player” |
| Epidemic Outburst `wh3_dlc25_character_abilties_epidemic_outbreak` | rejected (tactical escape) | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 2s · self · questionnaire §2 #61 · user: “the escape in melee is tactically relevant and must be chosen by player” |
| Eruption `wh3_main_character_abilities_eruption` | `skipped (unsuitable: vortex)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 4s · self · ×1 uses · wind-up 1s · questionnaire §2 #300 |
| Eternal Vigour `wh3_dlc29_character_abilities_eternal_vigour` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 26s · self · ×2 uses · questionnaire §2 #241 |
| Everyone Has Their Price `wh3_main_lord_abilities_everyone_has_their_price` | implemented (in-melee self) | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 15s · self · questionnaire §2 #62 |
| Evisceration `wh2_dlc16_hero_abilities_evisceration` | implemented (in-melee self) | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 4s · self · questionnaire §2 #63 |
| Eye for an Eye `wh3_dlc29_spell_bound_eye_jabber` | implemented (in-melee self) | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 24s · self · questionnaire §2 #64 |
| Eye Gouger `wh3_dlc29_spell_bound_eye_gouger` | implemented (in-melee self) | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 24s · self · questionnaire §2 #65 |
| Eye of the Storm `wh3_main_lord_abilities_eye_of_the_storm` | implemented (in-melee self) | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 29s · self · questionnaire §2 #66 |
| Faith's Bastion `wh_main_hero_abilities_faiths_bastion` | implemented (in-melee self) | melee_self | When in melee (and not fleeing): cast on self. | cd 60s · 22s · self · questionnaire §2 #67 |
| Fangspike `wh3_dlc26_weapon_abilities_fangspike` | `implemented (charge and in-melee)` | melee_self | Charge window or in melee: cast on self. (redesigned — charge + melee) | cd 120s · 29s · self · questionnaire §2 #68 · user: “Both charge and in melee” |
| Fangsword of Eltharion `wh2_dlc15_weapon_abilities_fangsword_of_eltharion` | implemented (in-melee self) | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 31s · self · questionnaire §2 #69 |
| Favour of the Fay `wh_dlc07_lord_abilities_favour_of_the_fay` | `implemented (ally-targeted: ally_melee_buff)` | ally_unit | When in melee: cast on self for now (nearest-ally picker later). | cd 90s · 44s · friend · questionnaire §2 #358 · **round 98 (Class B):** casts ON THE CHOSEN ALLY - ally buff - the CLOSEST ally in range; owner in melee (not routing / not wavering); own 70% bound = floor(100 * 0.70) = 70 m (FOURTH.ALLY_CAST_R100), offer test on unit:unit_distance only, fresh caster+ally handles. Was a self-cast |
| Feint & Riposte `wh2_main_lord_abilities_feint_and_reposte` | implemented (in-melee self) | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 28s · self · questionnaire §2 #70 |
| Ferocious Battle Howl `wh3_dlc29_spell_bound_prayer_ferocious_battle_howl` | `implemented (charge only)` | melee_self | In the charge window: cast on self. (trigger variant — charge only) | cd 60s · 15s · self · wind-up 0.5s · bound · questionnaire §2 #275 · user: “Charge only” |
| Ferocious Destruction `wh3_dlc29_spell_bound_prayer_ferocious_destruction` | `skipped (unsuitable: vortex)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 3s · self · wind-up 0.5s · questionnaire §2 #276 |
| Ferocious Fury of Ulric `wh3_dlc29_spell_bound_prayer_ferocious_fury_of_ulric` | `implemented (wavering self)` | melee_self | When wavering: cast on self. (trigger variant — wavering self) | cd 120s · 25s · self · wind-up 0.5s · bound · questionnaire §2 #277 · user: “Only when wavering (like Vial of Troll Blood)” |
| Filth Mace `wh_main_weapon_abilities_filth_mace` | implemented (in-melee self) | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 30s · self · questionnaire §2 #71 |
| Fistful of Laurels `wh3_main_item_abilities_fistful_of_laurels` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 50s · self · ×2 uses · questionnaire §2 #242 |
| Flame Incarnate `wh3_main_character_abilities_flame_incarnate` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 24s · self · wind-up 1s · questionnaire §2 #279 |
| Flesh to Stone `wh2_dlc16_spell_bound_flesh_to_stone` | `implemented (in-melee self)` | melee_self | When in melee: cast on self for now (nearest-ally picker later). | cd 90s · 19s · friend · ×3 uses · bound · questionnaire §2 #388 |
| Fluid Injection! `wh2_dlc16_unit_abilities_fluid_injection` | implemented (in-melee self) | melee_self | When in melee (and not fleeing): cast on self. | cd 60s · 22s · self · questionnaire §2 #72 |
| Foe-Seeker `wh_main_character_abilities_foe_seeker_summoned` | `implemented (tired)` | melee_self | Fatigue Tired or worse, fail-closed: cast on self. (redesigned — matches Foe-Seeker) | cd 60s · 25s · self · questionnaire §2 #73 · user: “Same as Foe-Seeker (tired or worse)” |
| Formless Horror `wh3_dlc24_lord_abilities_formless_horror` | `skipped (revisit)` | melee_self | When in melee (and not fleeing): cast on self. | cd 60s · 5s · self · wind-up 5s · questionnaire §2 #280 · user: “Skip for now” — effects line missing (`<unknown>` in the review doc); must be reconstructed from game data before deciding |
| Formless Horror `wh3_dlc24_lord_abilities_formless_horror_quest_battle` | `skipped (revisit)` | melee_self | When in melee (and not fleeing): cast on self. | cd 60s · 5s · self · wind-up 5s · questionnaire §2 #280 · user: “Skip for now” — effects line missing (`<unknown>` in the review doc); must be reconstructed from game data before deciding |
| From the Shadows `wh2_dlc14_character_abilities_from_the_shadows` | `rejected (stealth/escape effect)` | melee_self | When in melee: cast at own feet (existing ground-cast path). | cd 90s · 58s · ground · questionnaire §2 #335 |
| Frost Shard Glaive `wh3_main_weapon_abilities_frost_shard_glaive` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (35 m of 50 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 120s · 30s · enemy unit · questionnaire §2 #422 · enemy-targeting mechanism (harness 97) |
| Fury of Khaine `wh2_main_unit_abilities_fury_of_khaine` | `implemented (ally-targeted: ally_melee_buff)` | ally_unit | Cast on the chosen ALLY (trigger `ally_melee_buff`; class gate: plain ally buff (owner in melee) - the RAMPAGE entry, implemented (the M/A badge is the opt-in)); trigger range = 70 m = 70% of the real 100 m. | cd 90s · 28s · friend · questionnaire §2 #359 · charge and in melee · **round 98 (Class B): NEEDS A RULING** - rule 14 - the effect applies Rampage!; the note keeps the charge_or_melee trigger, which is not one of the ally families. · **round 99 (target-class-gated):** casts ON THE CHOSEN ALLY of the required class (plain ally buff (owner in melee) - the RAMPAGE entry, implemented (the M/A badge is the opt-in)) - the offer test is `unit:unit_distance(ally)` <= its own 70% bound = floor(100 * 0.70) = 70 m (`FOURTH.ALLY_CAST_R100`) ONLY, never the engine's `unit_in_range`; fresh caster+ally handles. Was a self-cast. |
| Fury of the Blood God `wh3_dlc26_lord_abilities_gaze_of_khorne` | implemented (in-melee self) | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 2s · self · questionnaire §2 #74 |
| Fury of the Falling Blade `wh3_dlc24_unit_abilities_fury_of_the_falling_blade` | rejected (auto: mutual exclusivity) | melee_self | When in melee (and not fleeing): cast on self. | cd 30s · -1s · self · questionnaire §2 #75 · user reason: mutual exclusivity (player decides) |
| Fury of the Land `wh3_dlc24_character_abilities_fury_of_the_land` | implemented (in-melee self) | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 35s · self · questionnaire §2 #76 |
| Fury of Ulric `wh3_dlc29_spell_bound_prayer_fury_of_ulric` | `implemented (wavering self-or-ally in range)` | melee_self | When self or an ally in range is wavering: cast on self. (trigger variant — wavering self-or-ally in range) | cd 90s · 25s · self · wind-up 0.5s · bound · questionnaire §2 #281 · user: “When wavering (self or ally in range)” |
| Fury of Ursun `wh3_main_lord_abilities_fury_of_ursun` | implemented (in-melee self) | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 18s · self · questionnaire §2 #77 |
| Gaze of Khaine `wh2_dlc10_lord_abilities_gaze_of_khaine` | `implemented (in-melee self)` | melee_self | When in melee: cast at own feet (existing ground-cast path). | cd 90s · 28s · ground · ×3 uses · questionnaire §2 #339 |
| Ghal Maraz `wh_main_weapon_abilities_ghal_maraz` | implemented (in-melee self) | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 39s · self · questionnaire §2 #78 |
| Ghoul King of Ushoran `wh2_dlc11_lord_abilities_ghoul_king_of_ushoran` | `implemented (health<=75, no melee gate)` | melee_self | When health at/below 75%: cast on self. (redesigned — health-based, not melee) | cd 120s · 32s · self · questionnaire §2 #79 · user: “When health is 75% or lower” |
| Giant Leap `wh3_dlc24_character_abilities_giant_leap` | implemented (in-melee self) | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 5s · self · questionnaire §2 #80 |
| Gitsnik `wh_main_weapon_abilities_gitsnik` | implemented (in-melee self) | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 33s · self · questionnaire §2 #81 |
| Glacial Blast `wh3_main_character_abilities_glacial_blast` | `skipped (unsuitable: vortex)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 4s · self · ×3 uses · wind-up 3s · questionnaire §2 #301 |
| Glorious Death `wh3_dlc25_lord_abilities_glorious_death` | `implemented (glorious_death)` | melee_self | When a nearby Slayer unit (not a character) is in melee: cast on that unit. (redesigned — cast on another slayer unit) | cd 120s · 40s · self · questionnaire §2 #82 · user: “Cast on self when self is a character only makes sense when death is very close. Priority should be cast on another slayer unit (not character) when that unit is in melee.” |
| Gotrek's Doom `wh2_pro08_character_abilities_gotrek_doom` | implemented (in-melee self) | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 22s · self · questionnaire §2 #83 |
| Grand Shield of Faith `wh_dlc04_spell_bound_shield_of_faith_upgraded` | implemented (in-melee self) | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 50s · self · bound · questionnaire §2 #84 |
| Grand Soulfire `wh_dlc04_spell_bound_soulfire_upgraded` | `skipped (unsuitable: bombardment/ranged)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 7s · self · wind-up 1s · bound · questionnaire §2 #282 |
| Great Gutgouger `wh3_dlc26_weapon_abilities_great_gutgouger` | implemented (in-melee self) | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 22s · self · questionnaire §2 #85 |
| Greater Faith Bastion `wh_dlc06_quest_abilities_grand_faiths_bastion` | `excluded (not in wheel: boss-only unit)` | melee_self | — | When in melee (and not fleeing): cast on self. · **round 101 (2026-10-17):** EXCLUDED - its ONLY grant path is `wh_dlc06_emp_cha_arch_lector_0_boss` (land_abil.tsv), a quest-battle boss variant; REMOVED from the mod (it was implemented before this round) |
| Groundbreaker `wh3_main_character_abilities_groundbreaker` | `excluded (auto: vortex)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 3s · self · ×3 uses · questionnaire §2 #243 |
| Gulyas `wh3_dlc24_lord_abilities_gulyas` | `implemented (health<=75, no melee gate)` | melee_self | When in melee: cast at own feet (existing ground-cast path). | cd 120s · 23s · ground · wind-up 3s · questionnaire §2 #345 |
| Halo of Maidenly Wrath `wh2_dlc14_lord_abilities_halo_of_maidenly_wrath` | implemented (in-melee self) | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 3s · self · questionnaire §2 #86 |
| Hammer-axe of Skoll `wh3_dlc29_weapon_active_hammer_axe_of_skoll` | implemented (in-melee self) | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 25s · self · questionnaire §2 #87 |
| Harbinger of Pestilence `wh3_dlc20_lord_abilities_harbinger_of_pestilence` | rejected (auto: mutual exclusivity) | melee_self | When in melee (and not fleeing): cast on self. | cd 30s · -1s · self · lord · questionnaire §2 #88 · user reason: mutual exclusivity (player decides) |
| Harmonic Convergence `wh3_main_spell_bound_harmonic_convergence` | `implemented (in-melee self)` | melee_self | When in melee: cast on self for now (nearest-ally picker later). | cd 60s · 27s · friend · ×2 uses · wind-up 1s · bound · questionnaire §2 #405 |
| Harvestman's Scythe `wh3_dlc29_item_active_harvestmans_scythe` | `rejected (drawback)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 28s · self · questionnaire §2 #89 · user reason: drawback (Bonus vs Infantry -100%) |
| Healing Elixirs `wh3_dlc20_lord_abilities_healing_elixirs` | `rejected (auto: mutual exclusivity)` | melee_self | When in melee (and not fleeing): cast on self. | cd 30s · -1s · self · lord · questionnaire §2 #90 · user reason: mutual exclusivity (player decides) |
| Heart Piercing `wh2_dlc11_lord_abilities_heart_piercing` | `implemented (charge and in-melee)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 28s · self · questionnaire §2 #91 · user: charge window or in melee (like Fangspike) |
| Hellfire Sword `wh_main_weapon_abilities_hellfire_sword` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 42s · self · questionnaire §2 #92 |
| Hellish Vigour `wh3_dlc29_lord_abilities_hellish_vigour` | `implemented (ally-targeted: ally_melee_buff)` | ally_unit | When in melee: cast on self for now (nearest-ally picker later). | cd 90s · 25s · friend · wind-up 3s · questionnaire §2 #395 · **round 98 (Class B):** casts ON THE CHOSEN ALLY - ally buff - the CLOSEST ally in range; owner in melee (not routing / not wavering); own 70% bound = floor(75 * 0.70) = 52 m (FOURTH.ALLY_CAST_R75), offer test on unit:unit_distance only, fresh caster+ally handles. Was a self-cast |
| Hellish Vigour Upgraded `wh3_dlc29_lord_abilities_hellish_vigour_upgraded` | `implemented (in-melee self)` | melee_self | When in melee: cast on self for now (nearest-ally picker later). | cd 120s · 25s · friend/self · wind-up 3s · questionnaire §2 #395 |
| Helm of Many Eyes `wh_dlc01_item_passive_helm_of_many_eyes` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 22s · self · questionnaire §2 #94 |
| Helm of Yvresse `wh2_dlc15_item_abilities_helm_of_yvresse` | `implemented (wavering self)` | melee_self | When wavering: cast on self. (trigger variant — wavering self) | cd 120s · 17s · friend · questionnaire §2 #360 · user: “Only when wavering (like Vial of Troll Blood)” |
| Helping Hand `wh2_pro08_character_abilities_helping_hand` | `implemented (ally-targeted: ally_melee_buff)` | ally_unit | When in melee: cast on self for now (nearest-ally picker later). | cd 120s · 22s · friend · questionnaire §2 #361 · **round 98 (Class B):** casts ON THE CHOSEN ALLY - ally buff - the CLOSEST ally in range; owner in melee (not routing / not wavering); own 70% bound = floor(50 * 0.70) = 35 m (FOURTH.ALLY_CAST_R50), offer test on unit:unit_distance only, fresh caster+ally handles. Was a self-cast |
| Heroic Killing Blow `wh3_main_pro_character_abilities_heroic_killing_blow_2` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 30s · self · questionnaire §2 #95 |
| Heroic Killing Blow `wh_dlc07_character_abilities_heroic_killing_blow` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 25s · self · questionnaire §2 #95 |
| Heroic Killing Blow `wh_main_character_abilities_heroic_killing_blow` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 25s · self · questionnaire §2 #95 |
| Horn of Khorne `wh3_main_army_abilities_horn_of_khorne` | `skipped (army-bar ability)` | melee_self | When in melee: cast on self (self-cast allowed; nearest-ally picker later). | cd 90s · 31s · friend/self · army · questionnaire §2 #311 |
| Horn of the First Beast `wh_dlc03_item_abilities_horn_of_the_first_beast` | `implemented (charge and in-melee)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 35s · self · questionnaire §2 #96 · user: charge window or in melee (like Fangspike) |
| Horn of the Wild Hunt `wh_dlc05_item_abilities_horn_of_the_wild_hunt` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 24s · self · questionnaire §2 #97 |
| Hurricane of Death `wh3_dlc25_character_abilities_hurricane_of_death` | `excluded (auto: vortex)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 6s · self · questionnaire §2 #98 |
| Hydra Blade `wh2_main_weapon_abilities_hydra_blade` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 38s · self · questionnaire §2 #99 |
| Hysterical Frenzy `wh3_main_spell_slaanesh_hysterical_frenzy_bound` | `implemented (in-melee self)` | melee_self | When in melee: cast on self for now (nearest-ally picker later). | cd 43s · 28s · friend · ×2 uses · wind-up 3s · bound · questionnaire §2 #406 |
| Immovable Bulwark `wh3_dlc26_unit_abilities_immovable_bulwark` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 1s · -1s · self · wind-up 1s · questionnaire §2 #283 |
| In the Name of War `wh3_dlc29_lord_abilities_in_the_name_of_war` | `rejected (rampage)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 15s · self · questionnaire §2 #100 · user reason: rampage (loss of control; player decides) |
| Inspired Assault I `wh3_main_lord_abilities_inspired_assault_i` | `implemented (ally-targeted: ally_melee_buff)` | ally_unit | Activate in the charge window OR in melee (and not fleeing): cast on self — mirrors Fangspike. (trigger variant — charge and in melee) | cd 60s · 29s · friend · questionnaire §2 #362 · charge and in melee · **round 98 (Class B):** casts ON THE CHOSEN ALLY - ally buff - the CLOSEST ally in range; owner in melee (not routing / not wavering); own 70% bound = floor(100 * 0.70) = 70 m (FOURTH.ALLY_CAST_R100), offer test on unit:unit_distance only, fresh caster+ally handles. Was a self-cast |
| Inspired Assault II `wh3_main_lord_abilities_inspired_assault_ii` | `implemented (ally-targeted: ally_melee_buff)` | ally_unit | Activate in the charge window OR in melee (and not fleeing): cast on self — mirrors Fangspike. (trigger variant — charge and in melee) | cd 90s · 42s · friend · questionnaire §2 #363 · charge and in melee · **round 98 (Class B):** casts ON THE CHOSEN ALLY - ally buff - the CLOSEST ally in range; owner in melee (not routing / not wavering); own 70% bound = floor(100 * 0.70) = 70 m (FOURTH.ALLY_CAST_R100), offer test on unit:unit_distance only, fresh caster+ally handles. Was a self-cast |
| Inspired Assault III `wh3_main_lord_abilities_inspired_assault_iii` | `implemented (ally-targeted: ally_melee_buff)` | ally_unit | Activate in the charge window OR in melee (and not fleeing): cast on self — mirrors Fangspike. (trigger variant — charge and in melee) | cd 120s · 43s · friend · questionnaire §2 #364 · charge and in melee · **round 98 (Class B):** casts ON THE CHOSEN ALLY - ally buff - the CLOSEST ally in range; owner in melee (not routing / not wavering); own 70% bound = floor(100 * 0.70) = 70 m (FOURTH.ALLY_CAST_R100), offer test on unit:unit_distance only, fresh caster+ally handles. Was a self-cast |
| Inspired Defence I `wh3_main_lord_abilities_inspired_defence_i` | `implemented (ally-targeted: ally_melee_buff)` | ally_unit | When in melee: cast on self for now (nearest-ally picker later). | cd 60s · 24s · friend · questionnaire §2 #365 · **round 98 (Class B):** casts ON THE CHOSEN ALLY - ally buff - the CLOSEST ally in range; owner in melee (not routing / not wavering); own 70% bound = floor(100 * 0.70) = 70 m (FOURTH.ALLY_CAST_R100), offer test on unit:unit_distance only, fresh caster+ally handles. Was a self-cast |
| Inspired Defence II `wh3_main_lord_abilities_inspired_defence_ii` | `implemented (ally-targeted: ally_melee_buff)` | ally_unit | When in melee: cast on self for now (nearest-ally picker later). | cd 90s · 31s · friend · questionnaire §2 #366 · **round 98 (Class B):** casts ON THE CHOSEN ALLY - ally buff - the CLOSEST ally in range; owner in melee (not routing / not wavering); own 70% bound = floor(100 * 0.70) = 70 m (FOURTH.ALLY_CAST_R100), offer test on unit:unit_distance only, fresh caster+ally handles. Was a self-cast |
| Inspired Defence III `wh3_main_lord_abilities_inspired_defence_iii` | `implemented (ally-targeted: ally_melee_buff)` | ally_unit | When in melee: cast on self for now (nearest-ally picker later). | cd 120s · 34s · friend · questionnaire §2 #367 · **round 98 (Class B):** casts ON THE CHOSEN ALLY - ally buff - the CLOSEST ally in range; owner in melee (not routing / not wavering); own 70% bound = floor(100 * 0.70) = 70 m (FOURTH.ALLY_CAST_R100), offer test on unit:unit_distance only, fresh caster+ally handles. Was a self-cast |
| Karaghul `wh2_pro08_weapon_abilities_karaghul` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 28s · self · questionnaire §2 #102 |
| Kill for Khorne! `wh3_dlc26_character_abilities_kill_for_khorne` | `skipped (unsuitable: vortex)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 1s · self · wind-up 3s · questionnaire §2 #284 |
| Killing Blow `wh3_main_pro_character_abilities_heroic_killing_blow_1` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 30s · self · questionnaire §2 #103 |
| Killing Blow `wh_main_unit_abilities_killing_blow` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 60s · 13s · self · questionnaire §2 #103 |
| Legbiter `wh3_dlc29_weapon_abilities_legbiter` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 28s · self · questionnaire §2 #104 |
| Liarsbane `wh3_dlc25_weapon_abilities_liarsbane` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 60s · 28s · self · questionnaire §2 #105 |
| Lightning Reflexes `wh2_dlc11_lord_abilities_lightning_reflexes` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 32s · self · questionnaire §2 #106 |
| Locus of Contagion `wh3_main_character_abilities_locus_of_contagion` | `skipped (revisit)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 11s · self · questionnaire §2 #108 · user: Skip for now (revisit later) |
| Locus of Grace `wh3_main_character_abilities_locus_of_grace` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 22s · self · questionnaire §2 #109 |
| Locus of Wrath `wh3_main_character_abilities_locus_of_wrath` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 25s · self · questionnaire §2 #110 |
| Lord of Grand Cathay `wh3_dlc24_lord_abilities_lord_of_grand_cathay` | `implemented (in-melee self)` | melee_self | When in melee: cast at own feet (existing ground-cast path). | cd 120s · 16s · ground · questionnaire §2 #336 |
| Lucky Banner `wh2_dlc15_item_abilities_lucky_banner` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 25s · self · questionnaire §2 #111 |
| Mace of Ulumak `wh2_dlc13_weapon_abilities_mace_of_ulumak` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 24s · self · questionnaire §2 #112 |
| Mad Cap Mushrooms `wh_main_hero_abilities_mad_cap_mushrooms` | `skipped (revisit)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 50s · self · questionnaire §2 #113 · user: Skip for now (effect is ability recharge, not combat) |
| Manann's Luck `wh2_dlc11_lord_abilities_mananns_luck` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 60s · 15s · self · questionnaire §2 #114 |
| Maneater Smoke Bomb `wh3_dlc26_unit_abilities_maneater_smoke_bomb` | `excluded (auto: vortex)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 24s · self · questionnaire §2 #115 |
| Mantra of Invigoration `wh3_cp1_character_abilities_protection_prayer` | `implemented (health<=75, no melee gate)` | melee_self | Cast on self when own health ≤ 75% (no melee gate). | cd 120s · 32s · friend · questionnaire §2 #368 · user: “Below 75% health (no melee gate)” · health-only family (4th member) |
| Mantra of Righteousness `wh3_cp1_character_abilities_offense_prayer` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self for now (nearest-ally picker later). | cd 120s · 40s · friend · questionnaire §2 #369 |
| Manus of Ursun `wh3_main_weapon_abilities_ursuns_claws` | `rejected (rampage)` | melee_self | When in melee (and not fleeing): cast on self. | cd 60s · 19s · self · questionnaire §2 #116 · user reason: rampage (affects self and allies; player decides) |
| Massacre `wh3_main_prisoners_massacre` | `excluded (not in wheel: army ability - removed from mod per user decision 2026-10-17)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 17s · friend/self · army · questionnaire §2 #312 · **round 100 (2026-10-17):** REMOVED from the mod - implemented but OUTSIDE the single in-wheel rule (army-bar ability). |
| Master of Alchemy `wh3_main_lord_abilities_master_of_alchemy` | `implemented (metallurgy_melee)` | melee_self | When self or an ally in range is in melee: cast on the owner or that ally. When an ally in range is shooting: cast on that ally. (shooting half awaits an API predicate — if none is found the melee half ships alone) | cd 90s · 20s · friend/self · questionnaire §2 #313 · user: “Same as the Metallurgies (melee self-or-ally / shooting ally)” |
| Master of Alchemy: Flaming `wh3_main_lord_abilities_master_of_alchemy_flaming` | `implemented (metallurgy_melee)` | melee_self | Same as Master of Alchemy (melee self-or-ally / shooting ally in range); shooting half awaits an API predicate. | cd 120s · 16s · friend/self · questionnaire §2 #314 |
| Master of Alchemy: Piercing `wh3_main_lord_abilities_master_of_alchemy_piercing` | `implemented (metallurgy_melee)` | melee_self | Same as Master of Alchemy (melee self-or-ally / shooting ally in range); shooting half awaits an API predicate. | cd 120s · 19s · friend/self · questionnaire §2 #315 |
| Master of Alchemy: Poison `wh3_main_lord_abilities_master_of_alchemy_poison` | `implemented (metallurgy_melee)` | melee_self | Same as Master of Alchemy (melee self-or-ally / shooting ally in range); shooting half awaits an API predicate. | cd 120s · 18s · friend/self · questionnaire §2 #316 |
| Master of the Skies `wh2_dlc12_lord_abilities_master_of_the_skies` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 60s · 31s · self · questionnaire §2 #117 |
| Master Rune of Breaking `wh2_dlc17_rune_abilities_master_rune_of_breaking` | `implemented (in-melee self)` | melee_self | When in melee: cast on self for now (nearest-ally picker later). | cd 180s · 55s · friend · wind-up 3s · rune · questionnaire §2 #396 |
| Master Rune of Negation `wh_dlc06_rune_abilities_master_rune_of_negation` | `implemented (in-melee self)` | melee_self | When in melee: cast on self for now (nearest-ally picker later). | cd 180s · 40s · friend · wind-up 3s · rune · questionnaire §2 #397 |
| Master Rune of Oath & Steel `wh_dlc06_rune_abilities_master_rune_of_oath_and_steel` | `implemented (in-melee self)` | melee_self | When in melee: cast on self (self-cast allowed; nearest-ally picker later). | cd 180s · 44s · friend/self · wind-up 3s · rune · questionnaire §2 #322 |
| Master Rune of Speed `wh2_dlc17_rune_abilities_master_rune_of_speed` | `implemented (in-melee self)` | melee_self | When in melee: cast on self (self-cast allowed; nearest-ally picker later). | cd 180s · 40s · friend/self · wind-up 3s · rune · questionnaire §2 #323 |
| Meat Feast `wh3_main_prisoners_butcher` | `excluded (not in wheel: army ability - removed from mod per user decision 2026-10-17)` | army_bar | Cast on self when own health ≤ 75% (no melee gate). | cd 120s · 20s · friend · army · questionnaire §2 #370 · user: “Below 75% health (no melee gate)” · health-only family (5th member) · **round 98 (Class B):** ARMY-BAR ability (standing rule 10) - SKIPPED, no Class-B ally logic added. Evidence: the audit's own wording ("An army-keyed single-target recover"), the project's grouped grade `army` and the key's own audio field `wh3_main_army_ability_ogr_butcher`. (The pre-existing `ushoran_health` self-cast entry is retained UNCHANGED by this round.) · **round 100 (2026-10-17):** REMOVED from the mod - implemented but OUTSIDE the single in-wheel rule (army-bar ability) per user decision. |
| Merciw's Monstrous Regiment `wh3_dlc20_cataclysm_bound_merciws_monstrous_regiment` | `implemented (ally-targeted: ally_infinite_buff)` | ally_unit | Cast on the chosen ALLY (trigger `ally_infinite_buff`; class gate: NO distance bound - INFINITE RANGE per the wiki (target_intercept_range = -1.0); the real distance is still logged); trigger range = no bound (infinite range per the wiki). | cd 120s · 120s · friend · ×1 uses · wind-up 5s · bound · questionnaire §2 #407 · **round 98 (Class B): NEEDS A RULING** - target_intercept_range = -1.0 (no real range) - no defensible 70% bound. · **round 99 (target-class-gated):** casts ON THE CHOSEN ALLY with **NO distance bound** - INFINITE RANGE per the wiki (NO distance bound - INFINITE RANGE per the wiki (target_intercept_range = -1.0); the real distance is still logged); offer test skipped entirely, the real distance is still logged for diagnosis; fresh caster+ally handles; was a self-cast. |
| Merciw's Monstrous Regiment `wh3_dlc27_cataclysm_bound_merciws_monstrous_regiment` | `implemented (ally-targeted: ally_infinite_buff)` | ally_unit | Cast on the chosen ALLY (trigger `ally_infinite_buff`); no bound (infinite range per the wiki). | cd 120s · 120s · friend · ×3 uses · wind-up 5s · bound · questionnaire §2 #407 · **round 99 (target-class-gated):** shares the bound key's phase - casts ON THE CHOSEN ALLY with **NO distance bound** (infinite range per the wiki); was a self-cast. |
| Mirror (Feint & Riposte) `wh2_dlc15_unit_abilities_mimic_feint_and_riposte` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 28s · self · ×2 uses · questionnaire §2 #244 |
| Mirror (Grand Hammer of Faith) `wh2_dlc15_unit_abilities_mimic_grand_hammer_of_faith` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 50s · self · ×2 uses · questionnaire §2 #245 |
| Mirror (Grom's Big Waaagh!) `wh2_dlc15_unit_abilities_mimic_grom_waaagh` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 18s · self · questionnaire §2 #118 |
| Mirror (Waaagh!) `wh2_dlc15_unit_abilities_mimic_waaagh` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 18s · self · questionnaire §2 #119 |
| Monstrous Strength `wh2_dlc13_lord_abilities_monstrous_strength` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 35s · self · questionnaire §2 #120 |
| Morglor the Mangler `wh3_dlc26_weapon_abilities_morglor_the_mangler` | `implemented (charge and in-melee)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 23s · self · questionnaire §2 #121 · user: charge window or in melee (like Fangspike) |
| Mors Clanstone `wh2_main_army_abilities_mors_clanstone` | `skipped (army-bar ability)` | melee_self | When in melee: cast at own feet (existing ground-cast path). | cd 120s · 28s · ground · ×3 uses · army · questionnaire §2 #340 |
| Mortal Blow `wh3_main_daemon_arms_abilities_mortal_blow` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 60s · 16s · self · questionnaire §2 #122 |
| Mortal Blow Upgraded `wh3_main_daemon_arms_abilities_mortal_blow_upgraded` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 24s · self · questionnaire §2 #122 |
| Mumbo-Jumbo Chant `wh3_dlc26_character_abilities_mumbo_jumbo_chant` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 30s · self · questionnaire §2 #123 |
| Murderous Exhortations `wh3_dlc26_lord_abilities_murderous_exhortations` | `excluded (auto: own-troop-damage AoE (friendly fire by design, family decision 2026-10-09))` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 20s · self · ×3 uses · questionnaire §2 #246 · triage-family: Own-troop-damage AoE |
| Murderous Libations `wh3_dlc27_army_abilities_eternal_dance_tempo_3_nectar_of_the_daemonette` | `excluded (auto: army-bar ability (standing rule 10))` | melee_self | When in melee: cast on self for now (nearest-ally picker later). | cd 120s · 36s · friend · ×2 uses · wind-up 1s · army · questionnaire §2 #408 |
| Necrostrike `wh2_dlc09_character_abilities_strike_of_nagash` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 27s · self · questionnaire §2 #124 |
| Nurgle's Favoured Son `wh3_dlc25_lord_abilities_nurgles_favoured_son` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 40s · self · questionnaire §2 #125 |
| Oath of Replenishment `wh2_dlc15_army_abilities_oath_of_replenishment` | `skipped (army-bar ability)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 21s · self · ×2 uses · army · questionnaire §2 #247 |
| Oath of Replenishment Upgraded `wh2_dlc15_army_abilities_oath_of_replenishment_upgraded` | `skipped (army-bar ability)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 21s · self · ×4 uses · army · questionnaire §2 #247 |
| Offering to the Gods `wh3_dlc27_lord_abilities_offering_to_the_gods` | `skipped (revisit)` | melee_self | (no automatic logic) Sacrifices a friendly unit — no automatic logic is safe. | cd 120s · 43s · friend · questionnaire §2 #371 · user: “Skip for now” — sacrifice/friendly-fire ability |
| Okkam's Mindrazor `wh3_dlc29_spell_bound_okkams_mindrazor` | `implemented (in-melee self - auto, trivial)` | melee_self | When in melee (and not fleeing): cast on self. | cd 46s · 32s · self · ×2 uses · wind-up 1s · questionnaire §2 #303 |
| Opal Amulet `wh_main_item_abilities_opal_amulet` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 60s · 22s · self · questionnaire §2 #126 |
| Oracle of Eternity `wh3_main_lord_abilities_oracle_of_eternity` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 22s · self · questionnaire §2 #127 |
| Orcs are da Best! `wh3_dlc26_character_abilities_orcs_are_da_best` | `implemented (ally-targeted: ally_melee_buff)` | ally_unit | When in melee (and not fleeing): cast on self for now (nearest-ally picker later). | cd 90s · 27s · friend · questionnaire §2 #372 · **round 98 (Class B):** casts ON THE CHOSEN ALLY - ally buff - the CLOSEST ally in range; owner in melee (not routing / not wavering); own 70% bound = floor(150 * 0.70) = 105 m (FOURTH.ALLY_CAST_R150), offer test on unit:unit_distance only, fresh caster+ally handles. Was a self-cast |
| Overseer of the Unseen `wh3_dlc29_hero_active_overseer_of_the_unseen` | `implemented (ally-targeted: ally_overseer)` | ally_unit | Cast on the chosen ALLY (trigger `ally_overseer`; class gate: non-commander / non-large target - DERIVED (land_units.class != "com" AND the battle entity size is not large/very_large; 918 keys)); trigger range = 70 m = 70% of the real 100 m. | cd 90s · 44s · friend · questionnaire §2 #373 · **round 98 (Class B): NEEDS A RULING** - needs a non-commander / non-large TARGET-CLASS filter (no existing ally family). · **round 99 (target-class-gated):** casts ON THE CHOSEN ALLY of the required class (non-commander / non-large target - DERIVED (land_units.class != "com" AND the battle entity size is not large/very_large; 918 keys)) - the offer test is `unit:unit_distance(ally)` <= its own 70% bound = floor(100 * 0.70) = 70 m (`FOURTH.ALLY_CAST_R100`) ONLY, never the engine's `unit_in_range`; fresh caster+ally handles. Was a self-cast. |
| Pendant of Slaanesh `wh_main_item_abilities_pendant_of_slaanesh` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 60s · 25s · self · questionnaire §2 #128 |
| Pestilens Clanstone `wh2_main_army_abilities_pestilens_clanstone` | `skipped (army-bar ability)` | melee_self | When in melee: cast at own feet (existing ground-cast path). | cd 120s · 75s · ground · ×3 uses · army · questionnaire §2 #341 |
| Pha's Protection `wh3_main_spell_bound_phas_protection` | `implemented (in-melee self)` | melee_self | When in melee: cast on self for now (nearest-ally picker later). | cd 60s · 22s · friend · ×2 uses · wind-up 1s · bound · questionnaire §2 #409 |
| Pilgrimage of Skulls `wh3_dlc26_lord_abilities_pilgrimage_of_skulls` | `implemented (in-melee self)` | melee_self | When in melee: cast on self for now (nearest-ally picker later). | cd 120s · 21s · friend · questionnaire §2 #374 |
| Plaguefather's Oration `wh3_main_lord_abilities_plaguefathers_oration` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 26s · self · questionnaire §2 #129 |
| Potion of Strength `wh_main_item_abilities_potion_of_strength` | `implemented (in-melee self - auto, trivial)` | melee_self | When in melee (and not fleeing): cast on self. | cd 60s · 33s · self · ×1 uses · questionnaire §2 #248 |
| Potion of Toughness `wh_main_item_abilities_potion_of_toughness` | `implemented (melee_health75)` | melee_self | When in melee (and not fleeing): cast on self. | cd 60s · 21s · self · ×1 uses · questionnaire §2 #249 |
| Predatory Instincts `wh3_cp1_lord_abilities_predatory_instincts` | `implemented (in-melee self)` | melee_self | When in melee: cast on self for now (nearest-ally picker later). | cd 90s · 25s · friend · questionnaire §2 #375 |
| Primal Roar `wh2_dlc13_lord_abilities_primal_roar` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 25s · self · questionnaire §2 #130 |
| Primeval Roar `wh2_dlc17_unit_abilities_primeval_roar` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 60s · 31s · self · wind-up 4.5s · questionnaire §2 #285 |
| Protection of Quetzl `wh2_dlc13_army_abilities_protection_of_quetzl` | `excluded (auto: army-bar ability (standing rule 10))` | melee_self | When in melee: cast on self for now (nearest-ally picker later). | cd 120s · 35s · friend · ×3 uses · wind-up 5s · army · questionnaire §2 #410 |
| Protection of Quetzl `wh2_dlc13_army_abilities_protection_of_quetzl_upgraded` | `excluded (auto: army-bar ability (standing rule 10))` | melee_self | When in melee: cast on self for now (nearest-ally picker later). | cd 90s · 55s · friend · ×3 uses · wind-up 5s · army · questionnaire §2 #410 |
| Puncture `wh3_dlc26_character_abilities_puncture` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 38s · self · questionnaire §2 #131 |
| Quickblood `wh3_dlc29_lord_abilities_lightning_reflexes` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 20s · self · questionnaire §2 #132 · distinct key from block-3 Lightning Reflexes `wh2_dlc11_lord_abilities_lightning_reflexes` |
| Quicksilver Strike `wh3_dlc27_lord_abilities_quicksilver_strike` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 60s · 29s · self · questionnaire §2 #133 |
| Rage Embodied `wh3_main_lord_abilities_rage_embodied` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 15s · self · questionnaire §2 #134 |
| Rage Incarnate `wh3_main_lord_abilities_rage_incarnate` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 15s · self · questionnaire §2 #135 |
| Rapier of Ecstasy `wh3_dlc20_weapon_abilities_rapier_of_ecstasy` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 17s · self · questionnaire §2 #136 |
| Red Fury `wh_main_character_abilities_red_fury` | `implemented (in-melee self)` | melee_self | When in melee: cast on self for now (nearest-ally picker later). | cd 90s · 31s · friend · questionnaire §2 #376 |
| Red Ruin `wh2_dlc10_lord_abilities_red_ruin` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 35s · self · questionnaire §2 #137 |
| Refuse to Die `wh2_dlc12_unit_abilities_refuse_to_die` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 60s · 20s · self · questionnaire §2 #138 |
| Relentless Rage `wh3_main_army_abilities_relentless_rage` | `excluded (auto: army-bar ability (standing rule 10))` | melee_self | When in melee: cast on self for now (nearest-ally picker later). | cd 90s · 20s · friend · army · questionnaire §2 #377 |
| Revenge Incarnate `wh_dlc06_lord_abilities_revenge_incarnate` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 33s · self · questionnaire §2 #139 |
| Rictus Clanstone `wh2_dlc09_army_abilities_rictus_clanstone` | `skipped (army-bar ability)` | melee_self | When in melee: cast at own feet (existing ground-cast path). | cd 120s · 48s · ground · ×3 uses · army · questionnaire §2 #342 |
| Rival Hide Talisman `wh2_main_item_abilities_rival_hide_talisman` | `excluded (impossible: already rejected by user (tactical escape/stealth))` | melee_self | When in melee (and not fleeing): cast on self. | cd 60s · 31s · self · ×1 uses · questionnaire §2 #250 |
| Rod of Corruption `wh2_main_item_abilities_rod_of_corruption` | `excluded (auto: own-troop-damage AoE (friendly fire by design, family decision 2026-10-09))` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 11s · self · ×3 uses · questionnaire §2 #251 · triage-family: Own-troop-damage AoE |
| Rok of Itza `wh2_dlc13_lord_abilities_rock_of_itza` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 60s · 24s · self · questionnaire §2 #140 |
| Rot or Die! `wh3_dlc25_lord_abilities_rot_or_die` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 18s · self · questionnaire §2 #141 |
| Rot-pocked Axe `wh3_dlc29_item_active_rot_pocked_axe` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 24s · self · questionnaire §2 #142 |
| Rune Axe of Gotrek `wh2_pro08_weapon_abilities_rune_axe_of_gotrek` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 36s · self · questionnaire §2 #143 |
| Rune Axe of Grombrindal `wh_pro01_weapon_abilities_rune_axe_of_grombrindal` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 32s · self · questionnaire §2 #144 |
| Rune of Breaking `wh2_dlc17_rune_abilities_rune_of_breaking` | `implemented (in-melee self)` | melee_self | When in melee: cast on self for now (nearest-ally picker later). | cd 120s · 33s · friend · wind-up 3s · rune · questionnaire §2 #398 |
| Rune of Doom `wh2_dlc17_lord_abilities_rune_of_doom` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 16s · self · wind-up 5s · questionnaire §2 #286 |
| Rune of Negation `wh_main_rune_abilities_rune_of_negation` | `implemented (in-melee self)` | melee_self | When in melee: cast on self for now (nearest-ally picker later). | cd 120s · 24s · friend · wind-up 3s · rune · questionnaire §2 #399 |
| Rune of Oath & Steel `wh_main_rune_abilities_rune_of_oath_and_steel` | `implemented (in-melee self)` | melee_self | When in melee: cast on self (self-cast allowed; nearest-ally picker later). | cd 120s · 44s · friend/self · wind-up 3s · rune · questionnaire §2 #324 |
| Rune of Speed `wh2_dlc17_rune_abilities_rune_of_speed` | `implemented (in-melee self)` | melee_self | When in melee: cast on self (self-cast allowed; nearest-ally picker later). | cd 120s · 30s · friend/self · wind-up 3s · rune · questionnaire §2 #325 |
| Rune of Thungni `wh3_dlc23_item_abilities_rune_of_thungni` | `implemented (in-melee self)` | melee_self | When in melee: cast on self for now (nearest-ally picker later). | cd 120s · 40s · friend · wind-up 3s · questionnaire §2 #400 |
| Runefang `wh_main_weapon_abilities_runefang` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 33s · self · questionnaire §2 #145 |
| Sacred Spawning of Xhotl `wh2_main_lord_abilities_sacred_spawning_of_xhotl` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 60s · 20s · self · questionnaire §2 #146 |
| Sands of Sickness `wh3_dlc25_character_abilities_sands_of_sickness` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 25s · self · questionnaire §2 #147 |
| Scales of the Celestial Court `wh3_main_item_abilities_scales_of_the_celestial_court` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 21s · self · questionnaire §2 #148 |
| Sceptre of Titans `wh3_main_weapon_abilities_sceptre_of_titans` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 21s · self · questionnaire §2 #149 |
| Scourge `wh_dlc03_weapon_abilities_scourge` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 35s · self · questionnaire §2 #150 |
| Scroll of Shielding `wh_main_item_abilities_scroll_of_shielding` | `implemented (in-melee self)` | melee_self | When in melee: cast on self for now (nearest-ally picker later). | cd 60s · 57s · friend · ×1 uses · questionnaire §2 #389 |
| Scrying Stone `wh2_main_item_abilities_scrying_stone` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 60s · 30s · self · questionnaire §2 #151 |
| Seduction of the Serpent `wh_dlc08_lord_abilities_seduction_of_the_serpent` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 17s · self · questionnaire §2 #152 |
| Seductive Glory `wh3_main_lord_abilities_seductive_glory` | `skipped (revisit)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 15s · self · questionnaire §2 #153 |
| Seismic Snare `wh2_dlc14_unit_abilities_seismic_snare` | `skipped (revisit)` | melee_self | When in melee (and not fleeing): cast on self. | cd 60s · 13s · self · questionnaire §2 #154 |
| Seismic Snare `wh3_dlc29_unit_abilities_stormfiend_seismic_snare` | `skipped (revisit)` | melee_self | When in melee (and not fleeing): cast on self. | cd 60s · 13s · self · ×1 uses · questionnaire §2 #154 |
| Shadow Shroud `wh3_main_lord_abilities_shadow_shroud` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 22s · self · questionnaire §2 #155 |
| Shanty: First Verse `wh2_dlc11_army_abilities_shanty_verse_1` | `skipped (army-bar ability)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 30s · self · ×1 uses · army · questionnaire §2 #252 |
| Shanty: First Verse `wh2_dlc11_army_abilities_shanty_verse_1_ai` | `skipped (army-bar ability)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 30s · friend · ×1 uses · army · questionnaire §2 #252 |
| Shanty: Second Verse `wh2_dlc11_army_abilities_shanty_verse_2` | `skipped (army-bar ability)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 30s · self · ×1 uses · army · questionnaire §2 #253 |
| Shanty: Second Verse `wh2_dlc11_army_abilities_shanty_verse_2_ai` | `skipped (army-bar ability)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 30s · friend · ×1 uses · army · questionnaire §2 #253 |
| Shanty: Third Verse `wh2_dlc11_army_abilities_shanty_verse_3` | `skipped (army-bar ability)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 30s · self · ×1 uses · army · questionnaire §2 #254 |
| Shanty: Third Verse `wh2_dlc11_army_abilities_shanty_verse_3_ai` | `skipped (army-bar ability)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 30s · friend · ×1 uses · army · questionnaire §2 #254 |
| Shield of Aeons `wh2_dlc13_item_abilities_shield_of_aeons` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 23s · self · questionnaire §2 #156 |
| Shield of Faith `wh_main_spell_bound_shield_of_faith` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 25s · self · bound · questionnaire §2 #157 |
| Shield of the Old Ones `wh2_main_character_abilities_shield_of_the_old_ones` | `implemented (in-melee self)` | melee_self | When in melee: cast at own feet (existing ground-cast path). | cd 90s · 17s · ground · questionnaire §2 #337 |
| Shielding Swarm `wh3_dlc29_hero_active_dispatch_the_swarm_protect` | `implemented (in-melee self)` | melee_self | When in melee: cast on self for now (nearest-ally picker later). | cd 120s · 30s · friend · wind-up 1s · questionnaire §2 #401 |
| Shielding Swarm Upgraded `wh3_dlc29_hero_active_dispatch_the_swarm_protect_upgraded` | `implemented (in-melee self)` | melee_self | When in melee: cast on self for now (nearest-ally picker later). | cd 60s · 30s · friend · wind-up 1s · questionnaire §2 #401 |
| Silver Dagger `wh3_dlc23_weapon_abilities_silver_dagger` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 32s · self · questionnaire §2 #158 |
| Silver Horn of Vengeance `wh_main_item_abilities_silver_horn_of_vengeance` | `skipped (unsuitable: charge-only)` | melee_self | When in melee (and not fleeing): cast on self. | cd 60s · 22s · self · questionnaire §2 #159 |
| Skavenbrew `wh2_main_item_abilities_skavenbrew` | `implemented (in-melee self)` | melee_self | When in melee: cast on self for now (nearest-ally picker later). | cd 90s · 47s · friend · ×1 uses · questionnaire §2 #390 |
| Skull of Katam `wh_main_item_abilities_skull_of_katam` | `skipped (magic scope + self-damage)` | melee_self | When in melee (and not fleeing): cast on self. | cd 60s · 13s · self · ×1 uses · questionnaire §2 #255 · user: “Skip - magic-resource + self-damage” |
| Skull Wand of Kaloth `wh_main_item_abilities_skull_wand_of_kaloth` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 27s · self · questionnaire §2 #160 |
| Slayer for Chaos `wh3_dlc23_item_abilities_slayer_for_chaos` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 24s · self · ×1 uses · questionnaire §2 #256 |
| Slippery `wh_main_hero_abilities_slippery` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 60s · 25s · self · questionnaire §2 #161 |
| Sliverslash `wh3_dlc20_weapon_abilities_sliverslash` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 26s · self · questionnaire §2 #162 |
| Smash 'Em Faster `wh2_dlc15_lord_abilities_smash_em_faster` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 30s · self · questionnaire §2 #163 |
| Sonic Boom `wh3_main_daemon_head_abilities_sonic_boom` | `skipped (unsuitable: vortex)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 6s · self · wind-up 3s · questionnaire §2 #287 |
| Soulblight `wh3_dlc29_spell_bound_soulblight` | `excluded (auto: ground-target-only)` | melee_self | When in melee: cast on the ground under its current target (placement policy needed). | cd 45s · 20s · self · ×2 uses · wind-up 1s · questionnaire §2 #485 |
| Soulfire `wh_main_spell_bound_soulfire` | `skipped (unsuitable: bombardment/ranged)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 7s · self · wind-up 1s · bound · questionnaire §2 #288 |
| Spinning Loons `wh_main_unit_abilities_spinning_loons` | `excluded (auto: summon)` | melee_self | When in melee: cast on the ground under its current target (placement policy needed). | cd 30s · 12s · enemy ground · ×3 uses · questionnaire §2 #481 |
| Spite of Da Bad Moon `wh_dlc06_lord_abilities_spite_of_da_bad_moon` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 20s · friend/self · questionnaire §2 #317 |
| Splode da Big 'Un! `wh3_dlc26_unit_abilities_splode_da_big_one` | `skipped (unsuitable: vortex)` | melee_self | When in melee (and not fleeing): cast on self. | cd 0s · 7s · self · ×1 uses · wind-up 0.4s · questionnaire §2 #304 |
| Staff of Damnation `wh_main_spell_bound_staff_of_damnation` | `implemented (in-melee self)` | melee_self | When in melee: cast on self for now (nearest-ally picker later). | cd 90s · 25s · friend · ×3 uses · bound · questionnaire §2 #391 |
| Staff of Masks `wh3_dlc27_item_abilities_staff_of_the_masque` | `excluded (impossible: no enemy-unit read)` | melee_self | When in melee with a current target: cast at the enemy it is fighting. | cd 120s · 23s · enemy unit · ×2 uses · item · questionnaire §2 #464 |
| Stand or Die! `wh_main_character_abilities_stand_or_die` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 18s · self · questionnaire §2 #164 |
| Star Lance `wh2_dlc15_weapon_abilities_star_lance` | `implemented (charge and in-melee)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 29s · self · questionnaire §2 #165 |
| Star of Avelorn `wh2_dlc10_item_abilities_star_of_avelorn` | `implemented (health<=75, no melee gate)` | melee_self | When in melee: cast at own feet (existing ground-cast path). | cd 120s · 27s · ground · ×2 uses · questionnaire §2 #343 |
| Starcrusher `wh_dlc01_weapon_abilities_starcrusher` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 43s · self · questionnaire §2 #166 |
| Steppe Hunter's Horn `wh3_main_item_abilities_steppe_hunters_horn` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 60s · 20s · self · questionnaire §2 #167 |
| Stinky Giant Club `wh_dlc08_weapon_abilities_stinky_giant_club` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 57s · self · questionnaire §2 #168 |
| Storm Rage `wh3_dlc20_unit_abilities_storm_rage` | `implemented (charge and in-melee)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 24s · self · questionnaire §2 #169 |
| Stormlance `wh3_dlc25_item_abilities_stormlance` | `implemented (charge and in-melee)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 32s · self · questionnaire §2 #170 |
| Supreme Shield of the Old Ones `wh2_dlc12_character_abilities_supreme_shield_of_the_old_ones` | `implemented (in-melee self)` | melee_self | When in melee: cast at own feet (existing ground-cast path). | cd 120s · 18s · ground · questionnaire §2 #338 |
| Sweet Sorrow `wh3_main_army_abilities_sweet_sorrow` | `excluded (auto: army-bar ability (standing rule 10))` | melee_self | When in melee: cast on self for now (nearest-ally picker later). | cd 60s · 15s · friend · wind-up 1s · army · questionnaire §2 #402 |
| Swiftness of Itzl `wh2_main_character_abilities_swiftness_of_itzl` | `skipped (unsuitable: movement/vortex)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 32s · self · questionnaire §2 #171 |
| Sword of Anti-Heroes `wh_main_weapon_abilities_sword_of_anti_heroes` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 40s · self · questionnaire §2 #172 |
| Sword of Teclis `wh2_main_weapon_abilities_sword_of_teclis` | `excluded (magic scope)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 23s · self · questionnaire §2 #173 |
| Sword of Torgald `wh_dlc08_weapon_abilities_sword_of_torgald` | `implemented (in-melee self - auto, trivial)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 44s · self · questionnaire §2 #174 |
| Talisman of Loec `wh2_main_item_abilities_talisman_of_loec` | `implemented (in-melee self - auto, trivial)` | melee_self | When in melee (and not fleeing): cast on self. | cd 0s · 67s · self · ×1 uses · questionnaire §2 #257 |
| Tempest Rage `wh3_dlc20_lord_abilities_tempest_rage` | `implemented (charge and in-melee)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 36s · self · questionnaire §2 #175 |
| Tenebrous Forge-Hammer `wh3_dlc27_weapon_abilities_tenebrous_forge_hammer` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 24s · self · questionnaire §2 #176 |
| The Airless Fires `wh3_dlc27_army_abilities_eternal_dance_tempo_3_revelry_and_madness` | `skipped (army-bar ability)` | melee_self | When in melee: cast at own feet (existing ground-cast path). | cd 120s · 48s · ground · ×1 uses · wind-up 3s · army · questionnaire §2 #350 |
| The Armour of Morkar `wh3_dlc20_item_abilities_the_armour_of_morkar` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 29s · self · questionnaire §2 #177 |
| The Bane Spear `wh3_main_weapon_abilities_banespear` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 21s · self · questionnaire §2 #178 |
| The Black Axe of Krell `wh3_dlc29_item_abilities_black_axe_of_krell` | `implemented (in-melee self - auto, trivial)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 31s · self · item · questionnaire §2 #179 |
| The Black Cleaver `wh3_dlc25_weapon_abilities_the_black_cleaver` | `implemented (in-melee self - auto, trivial)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 36s · self · questionnaire §2 #180 |
| The Black Gem of Gnar `wh3_dlc23_item_abilities_black_gem_of_gnar` | `skipped (revisit)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 13s · self · ×3 uses · questionnaire §2 #258 · user: “Skip for now” |
| The Blessed Blade of Ptra `wh2_dlc09_weapon_abilities_blessed_blade_of_ptra` | `implemented (in-melee self - auto, trivial)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 43s · self · questionnaire §2 #181 |
| The Blood Price `wh2_dlc14_lord_abilities_the_blood_price` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 22s · self · questionnaire §2 #182 |
| The Burning Waters `wh3_dlc27_army_abilities_eternal_dance_tempo_3_streams_of_euphoria` | `skipped (army-bar ability)` | melee_self | When in melee: cast at own feet (existing ground-cast path). | cd 120s · 48s · ground · ×1 uses · wind-up 3s · army · questionnaire §2 #351 |
| The Carstein Ring `wh_dlc04_item_abilities_the_carstein_ring` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 22s · self · questionnaire §2 #183 |
| The Daemon's Curse `wh2_dlc14_lord_abilities_the_daemons_curse` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 34s · self · questionnaire §2 #184 |
| The Dancing Blade `wh3_dlc23_character_abilities_sword_dance` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 23s · self · questionnaire §2 #185 |
| The Dragon's Fang `wh3_dlc24_weapon_abilities_dragons_fang` | `implemented (in-melee self - auto, trivial)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 20s · self · questionnaire §2 #186 |
| The Drakwald Runefang `wh2_dlc13_weapon_abilities_drakwald_runefang` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 39s · self · questionnaire §2 #187 |
| The Eternal Blade `wh3_main_weapon_abilities_the_eternal_blade` | `implemented (in-melee self - auto, trivial)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 21s · self · questionnaire §2 #188 |
| The Father of Blades `wh3_dlc25_weapon_abilities_the_father_of_blades` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 33s · self · questionnaire §2 #189 |
| The Hammer of Harry `wh3_pro11_weapon_abilities_the_hammer_of_harry` | `skipped (unsuitable: vortex)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 5s · self · wind-up 3s · questionnaire §2 #289 |
| The Hand of Dust `wh3_dlc29_spell_bound_undeath_sulekhim_hand_of_dust` | `implemented (in-melee self)` | melee_self | When in melee: cast on self for now (nearest-ally picker later). | cd 28s · 14s · friend · ×2 uses · wind-up 1s · bound · questionnaire §2 #411 |
| The Hochland Runefang `wh2_dlc13_weapon_abilities_hochland_runefang` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 24s · self · questionnaire §2 #190 |
| The Horn of Kygor `wh2_main_item_abilities_the_horn_of_kygor` | `implemented (charge and in-melee)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 20s · self · questionnaire §2 #191 |
| The Liber Mortis `wh2_dlc09_lord_abilities_the_liber_mortis` | `implemented (in-melee self)` | melee_self | When in melee: cast at own feet (existing ground-cast path). | cd 90s · 15s · ground · ×3 uses · questionnaire §2 #344 |
| The Loons of Eight Peaks `wh_dlc06_unit_abilities_the_loons_of_eight_peaks` | `excluded (auto: summon)` | melee_self | When in melee: cast on the ground under its current target (placement policy needed). | cd 30s · 12s · enemy ground · ×3 uses · questionnaire §2 #483 |
| The Mace of Helsturm `wh_main_weapon_abilities_the_mace_of_helsturm` | `implemented (in-melee self - auto, trivial)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 40s · self · questionnaire §2 #192 |
| The Nordland Runefang `wh2_dlc13_weapon_abilities_nordland_runefang` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 22s · self · questionnaire §2 #193 |
| The Ostermark Runefang `wh2_dlc13_weapon_abilities_ostermark_runefang` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 27s · self · questionnaire §2 #194 |
| The Ostland Runefang `wh2_dlc13_weapon_abilities_ostland_runefang` | `implemented (in-melee self - auto, trivial)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 38s · self · questionnaire §2 #195 |
| The Phoenix Blade `wh3_dlc27_weapon_abilities_the_phoenix_blade` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 21s · self · questionnaire §2 #196 |
| The Praise of Slaanesh `wh3_dlc27_lord_abilities_the_praise_of_slaanesh` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 30s · -1s · self · questionnaire §2 #197 |
| The Reikland Runefang `wh_main_weapon_abilities_the_reikland_runefang` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 39s · self · questionnaire §2 #198 |
| The Rock of Inevitability `wh3_main_item_abilities_the_rock_of_inevitability` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 22s · self · questionnaire §2 #199 |
| The Rotaxes `wh3_dlc29_item_active_the_rotaxes` | `implemented (in-melee self - auto, trivial)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 30s · self · questionnaire §2 #200 |
| The Shadow's Coil `wh_dlc05_unit_abilities_the_shadows_coil` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 1s · -1s · self · wind-up 1s · questionnaire §2 #290 |
| The Slayer of Kings `wh_dlc01_weapon_abilities_the_slayer_of_kings` | `implemented (in-melee self - auto, trivial)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 25s · self · questionnaire §2 #201 |
| The Slayer Sword `wh3_dlc26_weapon_abilities_the_slayer_sword` | `implemented (in-melee self - auto, trivial)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 22s · self · questionnaire §2 #202 |
| The Sword of Couronne `wh_main_weapon_abilities_the_sword_of_couronne` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 38s · self · questionnaire §2 #203 |
| The Sword of Lyonesse `wh2_dlc14_weapon_abilities_sword_of_lyonesse` | `implemented (in-melee self - auto, trivial)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 24s · self · questionnaire §2 #204 |
| The Talabecland Runefang `wh2_dlc13_weapon_abilities_talabecland_runefang` | `implemented (in-melee self - auto, trivial)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 41s · self · questionnaire §2 #205 |
| The Tenderiser `wh3_main_weapon_abilities_the_tenderiser` | `implemented (in-melee self - auto, trivial)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 25s · self · questionnaire §2 #206 |
| The Waltz of Lethargy `wh3_dlc27_lord_abilities_the_waltz_of_lethargy` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 20s · -1s · self · lord · questionnaire §2 #207 |
| The Wissenland Runefang `wh2_dlc13_weapon_abilities_wissenland_runefang` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 29s · self · questionnaire §2 #208 |
| Thundermace `wh3_main_weapon_abilities_thundermace` | `skipped (unsuitable: vortex)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 3s · self · ×3 uses · questionnaire §2 #259 |
| Time Amok `wh3_dlc20_cataclysm_bound_time_amok` | `skipped (unsuitable: movement)` | melee_self | When in melee: cast at own feet (existing ground-cast path). | cd 120s · 45s · ground · ×1 uses · wind-up 5s · bound · questionnaire §2 #353 |
| Time Amok `wh3_dlc27_cataclysm_bound_time_amok` | `skipped (unsuitable: movement)` | melee_self | When in melee: cast at own feet (existing ground-cast path). | cd 120s · 45s · ground · ×3 uses · wind-up 5s · bound · questionnaire §2 #353 |
| Toad Rage `wh2_dlc12_unit_abilities_toad_rage` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 60s · 18s · self · questionnaire §2 #209 |
| Tombstrike `wh2_dlc09_character_abilities_strike_of_tombs` | `implemented (in-melee self - auto, trivial)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 23s · self · questionnaire §2 #210 |
| Tor's Battle Hymn `wh3_main_character_abilities_tors_battle_hymn` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 25s · self · questionnaire §2 #211 |
| Touched by the Moon `wh2_dlc17_army_abilities_touched_by_the_moon` | `excluded (auto: army-bar ability (standing rule 10))` | melee_self | When in melee: cast on self for now (nearest-ally picker later). | cd 90s · 45s · friend · ×2 uses · wind-up 5s · army · questionnaire §2 #412 |
| Transfix `wh2_dlc11_lord_abilities_transfix` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 26s · self · questionnaire §2 #213 |
| Transformation of the Dragon `wh3_dlc24_lord_abilities_jade_dragon_dragon_form` | `skipped (revisit)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 5s · self · wind-up 5s · questionnaire §2 #291 · user: “Skip for now” |
| Transformation of the Dragon `wh3_main_lord_abilities_iron_dragon_dragon_form` | `skipped (revisit)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 5s · self · wind-up 5s · questionnaire §2 #291 · user: “Skip for now” |
| Transformation of the Dragon `wh3_main_lord_abilities_storm_dragon_dragon_form` | `skipped (revisit)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 5s · self · wind-up 5s · questionnaire §2 #291 · user: “Skip for now” |
| Twilight Horn I `wh2_dlc16_item_abilities_twilight_horn_i` | `implemented (in-melee self)` | melee_self | When in melee: cast on self for now (nearest-ally picker later). | cd 60s · 33s · friend · questionnaire §2 #378 |
| Twilight Horn II `wh2_dlc16_item_abilities_twilight_horn_ii` | `skipped (unsuitable: movement)` | melee_self | When in melee: cast on self (self-cast allowed; nearest-ally picker later). | cd 90s · 36s · friend/self · questionnaire §2 #318 |
| Ultimate Verdict `wh3_cp1_character_abilities_terrifying_presence` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 28s · self · questionnaire §2 #214 |
| Undeath Resurgent `wh_main_character_abilities_undeath_resurgent` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 18s · self · questionnaire §2 #215 |
| Unstoppable Choppas `wh3_dlc26_unit_abilities_unstoppable_choppas` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 1s · -1s · self · wind-up 1s · questionnaire §2 #292 |
| Unyielding Defence `wh3_main_character_abilities_unyielding_defender` | `implemented (in-melee self - auto, trivial)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 28s · self · questionnaire §2 #216 |
| Ursun's Claw `wh3_dlc24_weapon_abilities_ursuns_claw` | `implemented (in-melee self - auto, trivial)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 17s · self · questionnaire §2 #217 |
| Venom Wave `wh2_dlc09_lord_abilities_venom_wave` | `skipped (unsuitable: vortex)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 3s · self · ×3 uses · questionnaire §2 #260 |
| Verminous Fury `wh3_dlc29_lord_abilities_verminous_fury` | `implemented (ally-targeted: ally_melee_buff)` | ally_unit | Cast on the chosen ALLY (trigger `ally_melee_buff`; class gate: plain ally buff (owner in melee) - the RAMPAGE entry, implemented (the M/A badge is the opt-in)); trigger range = 140 m = 70% of the real 200 m. | cd 120s · 60s · friend · ×3 uses · questionnaire §2 #392 · **round 98 (Class B): NEEDS A RULING** - rule 14 - the effect applies Rampage! (it also grants Unbreakable; the Rampage flag wins). · **round 99 (target-class-gated):** casts ON THE CHOSEN ALLY of the required class (plain ally buff (owner in melee) - the RAMPAGE entry, implemented (the M/A badge is the opt-in)) - the offer test is `unit:unit_distance(ally)` <= its own 70% bound = floor(200 * 0.70) = 140 m (`FOURTH.ALLY_CAST_R200`) ONLY, never the engine's `unit_in_range`; fresh caster+ally handles. Was a self-cast. |
| Verminous Valour `wh2_main_character_abilities_verminous_valour` | `excluded (auto: vortex)` | melee_self | When in melee (and not fleeing): cast on self. | cd 60s · 17s · self · questionnaire §2 #219 |
| Vial of Troll Blood `wh_dlc08_item_abilities_vial_of_troll_blood` | `implemented (wavering self)` | melee_self | When wavering: cast on self. (trigger variant — wavering self) | cd 90s · 73s · self · ×1 uses · questionnaire §2 #261 · user: “Only when wavering” |
| Violent Wind `wh3_dlc20_unit_abilities_violent_wind` | `excluded (auto: vortex)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 4s · self · unit · questionnaire §2 #220 |
| Waaagh! `wh3_dlc26_unit_abilities_waaagh_in_combat` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 18s · self · questionnaire §2 #221 |
| Waaagh! `wh_main_character_abilities_waaagh` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 30s · self · questionnaire §2 #221 |
| Warp Frenzy `wh2_dlc16_hero_abilities_warp_frenzy` | `implemented (in-melee self - auto, trivial)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 29s · self · questionnaire §2 #222 |
| Warpbomb `wh2_main_army_abilities_warpbomb` | `excluded (auto: army-bar ability (standing rule 10))` | melee_self | When in melee: cast on self for now (nearest-ally picker later). | cd 60s · 16s · friend · ×1 uses · wind-up 1s · army · questionnaire §2 #413 |
| Warpstone Addiction `wh3_dlc29_lord_abilities_warpstone_addiction` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 33s · self · ×2 uses · questionnaire §2 #262 |
| Warrior Familiar `wh3_dlc27_item_abilities_warrior_familiar` | `implemented (in-melee self - auto, trivial)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 57s · self · ×1 uses · questionnaire §2 #263 |
| Warrior's Crest `wh2_dlc12_lord_abilities_warriors_crest` | `implemented (in-melee self - auto, trivial)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 30s · self · questionnaire §2 #223 |
| Where You Goin!? `wh3_dlc26_character_abilities_were_you_goin` | `implemented (ally-targeted: ally_wavering)` | ally_unit | When in melee: cast on self for now (nearest-ally picker later). | cd 90s · 25s · friend · questionnaire §2 #379 · **round 98 (Class B):** casts ON THE CHOSEN ALLY - ally wavering - the CLOSEST WAVERING ally in range; own 70% bound = floor(100 * 0.70) = 70 m (FOURTH.ALLY_CAST_R100), offer test on unit:unit_distance only, fresh caster+ally handles. Was a self-cast |
| Whiplash! `wh2_dlc14_lord_abilities_whiplash` | `implemented (ally-targeted: ally_beast)` | ally_unit | Cast on the chosen ALLY (trigger `ally_beast`; class gate: beast target - DERIVED (main_units.caste == "war_beast"; 55 keys)); trigger range = 70 m = 70% of the real 100 m. | cd 90s · 21s · friend · questionnaire §2 #380 · **round 98 (Class B): NEEDS A RULING** - needs a non-commander / beast TARGET-CLASS filter (no existing ally family). · **round 99 (target-class-gated):** casts ON THE CHOSEN ALLY of the required class (beast target - DERIVED (main_units.caste == "war_beast"; 55 keys)) - the offer test is `unit:unit_distance(ally)` <= its own 70% bound = floor(100 * 0.70) = 70 m (`FOURTH.ALLY_CAST_R100`) ONLY, never the engine's `unit_in_range`; fresh caster+ally handles. Was a self-cast. |
| Whirl of Weeping Blades `wh2_dlc14_weapon_abilities_whirl_of_weeping_blades` | `excluded (auto: vortex)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 5s · self · questionnaire §2 #224 |
| Whirlwind of Death `wh3_dlc25_unit_abilities_whirlwind_of_death` | `skipped (unsuitable: vortex)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 6s · self · ×1 uses · questionnaire §2 #264 |
| Whirlwind of Death Upgraded `wh3_dlc25_unit_abilities_whirlwind_of_death_upgraded` | `skipped (unsuitable: vortex)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 6s · self · ×1 uses · questionnaire §2 #264 |
| Whirlwind of Pleasure `wh3_dlc27_lord_abilities_whirlwind_of_pleasure` | `excluded (auto: vortex)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 5s · self · lord · questionnaire §2 #225 |
| Wild Abandon `wh3_dlc26_lord_abilities_wild_abandon` | `implemented (in-melee self)` | melee_self | When in melee: cast on self for now (nearest-ally picker later). | cd 90s · 25s · friend · questionnaire §2 #381 |
| Will of the Verminking `wh3_dlc29_lord_abilities_will_of_the_verminking` | `implemented (verminking_wavering)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 29s · self · questionnaire §2 #226 |
| Witchbrew `wh2_main_character_abilities_witchbrew` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 24s · self · ×3 uses · questionnaire §2 #265 |
| Witchbrew `wh3_dlc24_unit_abilities_witchbrew` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 24s · self · ×1 uses · questionnaire §2 #265 |
| Witstealer Sword `wh3_main_weapon_abilities_witstealer_sword` | `implemented (in-melee self - auto, trivial)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 17s · self · questionnaire §2 #227 |
| World's Edge Armour `wh2_main_item_abilities_worlds_edge_armour` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 60s · 57s · self · ×1 uses · questionnaire §2 #266 |
| Wrath of Ptra `wh2_dlc09_lord_abilities_wrath_of_ptra` | `skipped (unsuitable: vortex)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 3s · self · ×3 uses · questionnaire §2 #267 |
| Wrath of the Bear `wh3_main_army_abilities_wrath_of_the_bear` | `excluded (auto: army-bar ability (standing rule 10))` | melee_self | When in melee: cast on self for now (nearest-ally picker later). | cd 90s · 17s · friend · ×3 uses · army · questionnaire §2 #393 |
| Wrath of the Storm `wh3_main_lord_abilities_wrath_of_the_storm` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 120s · 32s · self · questionnaire §2 #228 |
| Wrathful Reaper `wh3_main_lord_abilities_wrathful_reaper` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 60s · 18s · self · questionnaire §2 #229 |
| Wristbands of Black Gold `wh3_dlc29_item_abilities_wristbands_of_black_gold` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 60s · 22s · self · item · questionnaire §2 #230 |
| Znarkharja's Ward `wh3_dlc24_hero_abilities_znarkharjas_ward` | `implemented (in-melee self)` | melee_self | When in melee (and not fleeing): cast on self. | cd 90s · 26s · self · ×2 uses · questionnaire §2 #268 |
| Accusation `wh_main_hero_abilities_accusation` | `implemented (enemy engaged or shot)` | melee_enemy | Fire when an ENEMY unit within the ability's **52 m reach** (`FOURTH.ACCUSATION_RANGE_M` — 70% of the 75 m intercept range, standing rule 15) is in melee OR under missile fire (prefer in-melee, then closest); the chosen enemy is the CAST TARGET (never the owner), cast via the round-4-proven fresh-handle enemy-targeting route. **Offer test = the 52 m constant ONLY (`unit:unit_distance(enemy) <= FOURTH.ACCUSATION_RANGE_M`, harness 96) — the engine's `unit_in_range` is NOT used (it offered at 81.3 m and the caster walked).** | cd 90s · 35s · enemy unit · questionnaire §2 #414 · harness 94 · offer-test fix h96 |
| Acidic Musk Glands `wh2_dlc16_unit_abilities_acidic_musk_glands` | `rejected (friendly fire)` | melee_enemy | When in melee (and not fleeing): cast on self. | cd 60s · 19s · self · questionnaire §2 #2 · user: “no automatic logic for now, potential for friendly fire” |
| Acquiescence `wh3_dlc27_spell_bound_acquiescence` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (140 m of 200 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 60s · 25s · enemy unit · ×2 uses · wind-up 1s · bound · questionnaire §2 #476 · enemy-targeting mechanism (harness 97) |
| All-Consuming Hatred `wh3_dlc27_unit_abilities_consuming_hatred` | `rejected (drawback)` | melee_enemy | When in melee (and not fleeing): cast on self. | cd 120s · 25s · self · questionnaire §2 #4 · user: “serious drawback (Melee Defence -12); player should decide” |
| Arachnarok Eggs `wh_dlc08_item_abilities_arachnarok_eggs` | `implemented (enemy-ground: closest FIGHTING enemy)` | enemy_ground_melee | The CLOSEST enemy within the ability's 70% bound (35 m of its 50 m target_intercept_range) that is FIGHTING (in melee): the summon is placed on THAT ENEMY's ground (perform_special_ability_ground, fresh caster + fresh enemy, hold, pre-cast re-check). | cd 60s · 1s · enemy ground · ×5 uses · questionnaire §2 #479 · **round 102 (2026-10-17):** implemented on the Gate of Khorne trigger per the user's summon ruling (harness 102) |
| Armour of the Barrows `wh3_dlc29_item_abilities_armour_of_the_burrows` | `implemented (in-melee self)` | melee_enemy | When in melee (and not fleeing): cast on self. | cd 120s · 27s · self · item · questionnaire §2 #9 |
| Assassin's Trophy `wh2_main_character_abilities_assassins_trophy` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (105 m of 150 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 60s · 29s · enemy unit · questionnaire §2 #415 · enemy-targeting mechanism (harness 97) |
| Bastet `wh3_dlc29_lord_abilities_bastet` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (70 m of 100 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 90s · 19s · enemy unit · questionnaire §2 #416 · enemy-targeting mechanism (harness 97) |
| Bitter Sting `wh3_dlc27_qb_unit_abilities_bitter_sting` | `excluded (not in wheel: boss-only unit)` | enemy_unit | — | When an enemy unit within the 70% bound (21 m of 30 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). · **round 101 (2026-10-17):** EXCLUDED - its ONLY grant path is `wh3_dlc27_chs_feral_manticore_boss` (land_abil.tsv), a quest-battle boss variant; REMOVED from the mod (it was implemented before this round) |
| Blade of Setep `wh2_dlc09_weapon_abilities_blade_of_setep` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (70 m of 100 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 90s · 44s · enemy unit · questionnaire §2 #418 · enemy-targeting mechanism (harness 97) |
| Blight Swarm `wh3_main_lord_abilities_blight_swarm` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (140 m of 200 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 60s · 20s · enemy unit · ×4 uses · questionnaire §2 #448 · enemy-targeting mechanism (harness 97) |
| Blood God's Shackles `wh3_dlc26_army_abilities_blood_gods_shackles` | `excluded (auto: army-bar ability (standing rule 10))` | melee_enemy | When in melee with a current target: cast at the enemy it is fighting. | cd 120s · 34s · enemy unit · ×1 uses · army · questionnaire §2 #449 |
| Blood God's Shackles Upgraded `wh3_dlc26_army_abilities_blood_gods_shackles_upgraded` | `excluded (auto: army-bar ability (standing rule 10))` | melee_enemy | When in melee with a current target: cast at the enemy it is fighting. | cd 120s · 34s · enemy unit · ×2 uses · army · questionnaire §2 #449 |
| Book of Secrets `wh3_dlc24_item_abilities_book_of_secrets` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (70 m of 100 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 90s · 20s · enemy unit · ×3 uses · questionnaire §2 #450 · enemy-targeting mechanism (harness 97) |
| Curse of Djaf `wh2_dlc09_character_abilities_curse_of_djaf` | `excluded (auto: ground-target-only)` | melee_enemy | When in melee: cast on the ground under its current target (placement policy needed). | cd 0s · 13s · enemy ground · ×1 uses · questionnaire §2 #480 |
| Dance of Despair `wh3_dlc20_cataclysm_bound_dance_of_despair` | `excluded (auto: ground-target-only)` | melee_enemy | When in melee: cast on the ground under its current target (placement policy needed). | cd 120s · 45s · enemy ground · ×1 uses · wind-up 5s · bound · questionnaire §2 #484 |
| Dance of Despair `wh3_dlc27_cataclysm_bound_dance_of_despair` | `excluded (auto: ground-target-only)` | melee_enemy | When in melee: cast on the ground under its current target (placement policy needed). | cd 120s · 45s · enemy ground · ×3 uses · wind-up 5s · bound · questionnaire §2 #484 |
| Deathmaster's Sigil `wh2_dlc14_lord_abilities_deathmasters_sigil` | `excluded (auto: vortex)` | melee_enemy | When in melee with a current target: cast at the enemy it is fighting. | cd 90s · 7s · enemy unit · questionnaire §2 #419 |
| Don't Even Try It `wh2_dlc15_lord_abilities_dont_even_try_it` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (70 m of 100 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 90s · 18s · enemy unit · ×2 uses · questionnaire §2 #451 · enemy-targeting mechanism (harness 97) |
| El Syf `wh_dlc05_weapon_abilities_el_syf` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (140 m of 200 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 90s · 24s · enemy unit · questionnaire §2 #420 · enemy-targeting mechanism (harness 97) |
| Eye of Khorne `wh3_dlc26_lord_abilities_eye_of_khorne` | `implemented (enemy finisher: lowest-health non-commander below 20%)` | enemy_low_health_noncommander | ANY enemy within the ability's 70% bound (35 m of 50 m) that is BELOW 20% health and is NOT a Lord or Hero; the LOWEST-health one wins (closest as the tiebreak); cast on that enemy through the UNIT form (target_enemies). | cd 120s · 10s · enemy unit · ×1 uses · questionnaire §2 #452 · **round 102 (2026-10-17):** implemented per the user's finisher ruling (harness 102) |
| Fascination `wh3_main_army_abilities_fascination` | `excluded (auto: army-bar ability (standing rule 10))` | melee_enemy | When in melee with a current target: cast at the enemy it is fighting. | cd 120s · 14s · enemy unit · wind-up 5s · army · questionnaire §2 #470 |
| Fecund Rebirth `wh3_dlc29_character_active_mark_of_the_monster` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (140 m of 200 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 90s · 32s · enemy unit · wind-up 1s · questionnaire §2 #471 · enemy-targeting mechanism (harness 97) |
| Fermented Fungi `wh2_dlc15_lord_abilities_fermented_fungi` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (52 m of 75 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 90s · 15s · enemy unit · ×3 uses · questionnaire §2 #453 · enemy-targeting mechanism (harness 97) |
| Ferocious Winter’s Chill `wh3_dlc29_spell_bound_prayer_ferocious_winters_chill` | `implemented (in-melee self)` | melee_enemy | When in melee (and not fleeing): cast on self. | cd 90s · 20s · self · wind-up 0.5s · bound · questionnaire §2 #278 |
| Fog of the Damned `wh3_dlc29_bound_deep_fog_of_the_damned` | `skipped (revisit)` | melee_enemy | When in melee: cast at own feet (existing ground-cast path). | cd 44s · 35s · ground · ×2 uses · wind-up 3s · bound · questionnaire §2 #349 |
| Frenzied Challenge `wh3_dlc27_qb_unit_abilities_frenzied_challenge` | `excluded (not in wheel: boss-only unit)` | enemy_unit | — | When an enemy unit within the 70% bound (105 m of 150 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). · **round 101 (2026-10-17):** EXCLUDED - its ONLY grant path is `wh3_dlc27_bst_mon_ghorgon_boss` (land_abil.tsv), a quest-battle boss variant; REMOVED from the mod (it was implemented before this round) |
| Frozen on the Pyre `wh3_dlc27_army_abilities_eternal_dance_tempo_3_submission_to_the_prince` | `excluded (auto: army-bar ability (standing rule 10))` | melee_enemy | When in melee with a current target: cast at the enemy it is fighting. | cd 90s · 36s · enemy unit · ×3 uses · wind-up 1s · army · questionnaire §2 #477 |
| Gate of Khorne `wh3_main_character_abilities_gate_of_khorne` | `implemented (enemy-ground: closest FIGHTING enemy)` | enemy_ground_melee | The CLOSEST enemy within the ability's 70% bound (35 m of its 50 m target_intercept_range) that is FIGHTING (in melee): the summon is placed on THAT ENEMY'S ground (perform_special_ability_ground, fresh caster + fresh enemy, hold, pre-cast re-check). | cd 120s · 10s · ground/friend · ×1 uses · wind-up 5s · questionnaire §2 #327 · **round 101 (2026-10-17):** implemented per the user's trigger "place it on the closest enemy that is in range of the ability and fighting" (harness 101) |
| Gate of Nurgle `wh3_main_character_abilities_gate_of_nurgle` | `implemented (enemy-ground: closest FIGHTING enemy)` | enemy_ground_melee | The CLOSEST enemy within the ability's 70% bound (35 m of its 50 m target_intercept_range) that is FIGHTING (in melee): the summon is placed on THAT ENEMY's ground (perform_special_ability_ground, fresh caster + fresh enemy, hold, pre-cast re-check). | cd 120s · 10s · friend/self · ×1 uses · wind-up 5s · questionnaire §2 #328 · **round 102 (2026-10-17):** implemented on the Gate of Khorne trigger per the user's summon ruling (harness 102) |
| Gate of Slaanesh `wh3_main_character_abilities_gate_of_slaanesh` | `implemented (enemy-ground: closest FIGHTING enemy)` | enemy_ground_melee | The CLOSEST enemy within the ability's 70% bound (35 m of its 50 m target_intercept_range) that is FIGHTING (in melee): the summon is placed on THAT ENEMY's ground (perform_special_ability_ground, fresh caster + fresh enemy, hold, pre-cast re-check). | cd 120s · 10s · friend/self · ×1 uses · wind-up 5s · questionnaire §2 #329 · **round 102 (2026-10-17):** implemented on the Gate of Khorne trigger per the user's summon ruling (harness 102) |
| Gaze of Fate `wh3_main_lord_abilities_gaze_of_fate` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (70 m of 100 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 90s · 14s · enemy unit · ×3 uses · questionnaire §2 #454 · enemy-targeting mechanism (harness 97) |
| Gilellion's Soulnetter `wh3_main_weapon_abilities_soulnetter` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (35 m of 50 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 120s · 26s · enemy unit · questionnaire §2 #423 · enemy-targeting mechanism (harness 97) |
| Glory Seeker `wh3_dlc29_hero_active_glory_seeker` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (70 m of 100 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 120s · 24s · enemy unit · questionnaire §2 #424 · enemy-targeting mechanism (harness 97) |
| Glory Seeker Upgraded `wh3_dlc29_hero_active_glory_seeker_upgraded` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (70 m of 100 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 120s · 36s · enemy unit · questionnaire §2 #424 · enemy-targeting mechanism (harness 97) |
| Greater Gate of Khorne `wh3_main_cataclysm_khorne_greater_gate_of_khorne` | `implemented (enemy-ground: closest FIGHTING enemy)` | enemy_ground_melee | The CLOSEST enemy within the ability's 70% bound (no real range (target_intercept_range = -1.0) - no 70% bound) that is FIGHTING (in melee): the summon is placed on THAT ENEMY's ground (perform_special_ability_ground, fresh caster + fresh enemy, hold, pre-cast re-check). | cd 0s · 10s · friend/self · ×1 uses · wind-up 5s · questionnaire §2 #330 · **round 102 (2026-10-17):** implemented on the Gate of Khorne trigger per the user's summon ruling (harness 102) |
| Greater Gate of Khorne `wh3_main_character_abilities_greater_gate_of_khorne` | `implemented (enemy-ground: closest FIGHTING enemy)` | enemy_ground_melee | The CLOSEST enemy within the ability's 70% bound (35 m of its 50 m target_intercept_range) that is FIGHTING (in melee): the summon is placed on THAT ENEMY's ground (perform_special_ability_ground, fresh caster + fresh enemy, hold, pre-cast re-check). | cd 120s · 10s · friend/self · ×1 uses · wind-up 5s · questionnaire §2 #330 · **round 102 (2026-10-17):** implemented on the Gate of Khorne trigger per the user's summon ruling (harness 102) |
| Greater Gate of Nurgle `wh3_main_character_abilities_greater_gate_of_nurgle` | `implemented (enemy-ground: closest FIGHTING enemy)` | enemy_ground_melee | The CLOSEST enemy within the ability's 70% bound (35 m of its 50 m target_intercept_range) that is FIGHTING (in melee): the summon is placed on THAT ENEMY's ground (perform_special_ability_ground, fresh caster + fresh enemy, hold, pre-cast re-check). | cd 120s · 10s · friend/self · ×1 uses · wind-up 5s · questionnaire §2 #331 · **round 102 (2026-10-17):** implemented on the Gate of Khorne trigger per the user's summon ruling (harness 102) |
| Greater Gate of Slaanesh `wh3_main_character_abilities_greater_gate_of_slaanesh` | `implemented (enemy-ground: closest FIGHTING enemy)` | enemy_ground_melee | The CLOSEST enemy within the ability's 70% bound (35 m of its 50 m target_intercept_range) that is FIGHTING (in melee): the summon is placed on THAT ENEMY's ground (perform_special_ability_ground, fresh caster + fresh enemy, hold, pre-cast re-check). | cd 120s · 10s · friend/self · ×1 uses · wind-up 5s · questionnaire §2 #332 · **round 102 (2026-10-17):** implemented on the Gate of Khorne trigger per the user's summon ruling (harness 102) |
| Greater Gate of Tzeentch `wh3_main_character_abilities_greater_gate_of_tzeentch` | `implemented (enemy-ground: closest FIGHTING enemy)` | enemy_ground_melee | The CLOSEST enemy within the ability's 70% bound (35 m of its 50 m target_intercept_range) that is FIGHTING (in melee): the summon is placed on THAT ENEMY's ground (perform_special_ability_ground, fresh caster + fresh enemy, hold, pre-cast re-check). | cd 120s · 10s · friend/self · ×1 uses · wind-up 5s · questionnaire §2 #333 · **round 102 (2026-10-17):** implemented on the Gate of Khorne trigger per the user's summon ruling (harness 102) |
| Headhunt `wh3_dlc26_character_abilities_headhunt` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (105 m of 150 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 90s · 31s · enemy unit · questionnaire §2 #425 · enemy-targeting mechanism (harness 97) |
| Helm of Discord `wh_main_weapon_abilities_helm_of_discord` | `implemented (in-melee self)` | melee_enemy | When in melee (and not fleeing): cast on self. | cd 90s · 25s · self · questionnaire §2 #93 |
| Hornswaggle `wh2_dlc11_character_abilities_hornswaggle` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (70 m of 100 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 90s · 32s · enemy unit · questionnaire §2 #426 · enemy-targeting mechanism (harness 97) |
| Hunter of Champions `wh_dlc08_character_abilities_hunter_of_champions` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (70 m of 100 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 90s · 24s · enemy unit · questionnaire §2 #427 · enemy-targeting mechanism (harness 97) |
| Inevitable Horror `wh3_dlc26_character_abilities_inevitable_horror` | `implemented (in-melee self)` | melee_enemy | When in melee (and not fleeing): cast on self. | cd 120s · 33s · self · questionnaire §2 #101 |
| Locus of Beguilement `wh3_main_character_abilities_locus_of_beguilement` | `implemented (in-melee self)` | melee_enemy | When in melee (and not fleeing): cast on self. | cd 90s · 22s · self · questionnaire §2 #107 |
| Looming Dread `wh2_dlc14_lord_abilities_looming_dread` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (105 m of 150 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 90s · 31s · enemy unit · questionnaire §2 #428 · enemy-targeting mechanism (harness 97) |
| Lord of Dragons `wh2_dlc15_lord_abilities_lord_of_dragons` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (52 m of 75 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 90s · 22s · enemy unit · questionnaire §2 #429 · enemy-targeting mechanism (harness 97) |
| Mark of the Plague Fleet `wh3_dlc29_item_active_mark_of_the_plague_fleet` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (52 m of 75 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 120s · 30s · enemy unit · questionnaire §2 #430 · enemy-targeting mechanism (harness 97) |
| Marked for Eatin' `wh3_dlc26_unit_abilities_marked_for_eatin` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (52 m of 75 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 120s · 29s · enemy unit · questionnaire §2 #431 · enemy-targeting mechanism (harness 97) |
| Master of Beguilement `wh_dlc04_lord_abilities_beguile` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (70 m of 100 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 90s · 44s · enemy unit · questionnaire §2 #432 · enemy-targeting mechanism (harness 97) |
| Mirror of Knowledge `wh3_dlc24_item_abilities_mirror_of_knowledge` | `skipped (revisit)` | melee_enemy | When in melee: cast at own feet (existing ground-cast path). | cd 37s · 40s · ground · wind-up 3s · questionnaire §2 #346 |
| Muster of Malevolents `wh2_dlc16_character_abilities_muster_of_malevolents` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (52 m of 75 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 90s · 15s · enemy unit · ×3 uses · questionnaire §2 #455 · enemy-targeting mechanism (harness 97) |
| Net Dem Up! `wh3_dlc26_unit_abilities_net_dem_up` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (52 m of 75 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 90s · 18s · enemy unit · questionnaire §2 #433 · enemy-targeting mechanism (harness 97) |
| No Escape `wh3_main_character_abilities_no_escape` | `excluded (impossible: no enemy-unit read)` | melee_enemy | When in melee with a current target: cast at the enemy it is fighting. | cd 90s · 14s · enemy unit · ×3 uses · questionnaire §2 #456 |
| Oath of Vengeance `wh2_dlc10_lord_abilities_oath_of_vengeance` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (140 m of 200 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 60s · 44s · enemy unit · questionnaire §2 #434 · enemy-targeting mechanism (harness 97) |
| Otto's Scythe `wh3_dlc29_item_active_ottos_scythe` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (70 m of 100 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 120s · 28s · enemy unit · wind-up 1s · questionnaire §2 #472 · enemy-targeting mechanism (harness 97) |
| Pack Trap `wh3_dlc24_unit_abilities_pack_trap` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (70 m of 100 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 90s · 10s · enemy unit · ×3 uses · questionnaire §2 #457 · enemy-targeting mechanism (harness 97) |
| Pestilent Potions `wh3_dlc20_item_abilities_pestilent_potions` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (70 m of 100 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 120s · 25s · enemy unit · ×3 uses · questionnaire §2 #458 · enemy-targeting mechanism (harness 97) |
| Prey of Anath Raema `wh_dlc05_character_abilities_prey_of_anath_raema` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (70 m of 100 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 90s · 16s · enemy unit · ×3 uses · questionnaire §2 #459 · enemy-targeting mechanism (harness 97) |
| Prey of the Blood God `wh3_pro12_hero_abilities_prey_of_the_blood_god` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (70 m of 100 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 120s · 22s · enemy unit · ×3 uses · questionnaire §2 #460 · enemy-targeting mechanism (harness 97) |
| Ravaging Swarm `wh3_dlc29_hero_active_dispatch_the_swarm_attack` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (21 m of 30 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 120s · 24s · enemy unit · wind-up 1s · questionnaire §2 #473 · enemy-targeting mechanism (harness 97) |
| Ravaging Swarm Upgraded `wh3_dlc29_hero_active_dispatch_the_swarm_attack_upgraded` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (21 m of 30 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 60s · 24s · enemy unit · wind-up 1s · questionnaire §2 #473 · enemy-targeting mechanism (harness 97) |
| Sadistic Snare `wh3_dlc23_lord_abilities_sadistic_snare` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (14 m of 20 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 120s · 33s · enemy unit · ×2 uses · questionnaire §2 #461 · enemy-targeting mechanism (harness 97) |
| Soulblight `wh2_dlc10_spell_bound_soulblight` | `excluded (auto: ground-target-only)` | melee_enemy | When in melee: cast on the ground under its current target (placement policy needed). | cd 90s · 20s · enemy ground · ×2 uses · wind-up 3s · bound · questionnaire §2 #485 |
| Spearfisher's Net `wh2_dlc11_lord_abilities_spearfishers_net` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (70 m of 100 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 90s · 18s · enemy unit · ×3 uses · questionnaire §2 #462 · enemy-targeting mechanism (harness 97) |
| Spiderweb Attack `wh3_dlc26_character_abilities_spider_web_attack` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (35 m of 50 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 120s · 18s · enemy unit · ×2 uses · questionnaire §2 #463 · enemy-targeting mechanism (harness 97) |
| Taunt `wh2_dlc11_character_abilities_taunt` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (70 m of 100 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 60s · 17s · enemy unit · questionnaire §2 #435 · enemy-targeting mechanism (harness 97) |
| Tendrils of the Sea `wh3_dlc29_hero_active_tendrils_of_the_sea` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (140 m of 200 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 120s · 24s · enemy unit · wind-up 3s · questionnaire §2 #474 · enemy-targeting mechanism (harness 97) |
| The Averland Runefang `wh2_dlc13_weapon_abilities_averland_runefang` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (70 m of 100 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 120s · 33s · enemy unit · questionnaire §2 #436 · enemy-targeting mechanism (harness 97) |
| The Black Tongue `wh3_dlc27_character_abilities_the_black_tongue` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (140 m of 200 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 120s · 21s · enemy unit · ×2 uses · questionnaire §2 #465 · enemy-targeting mechanism (harness 97) |
| The Curse of Anraheir `wh2_dlc16_spell_bound_the_curse_of_anraheir` | `excluded (auto: ground-target-only)` | melee_enemy | When in melee: cast on the ground under its current target (placement policy needed). | cd 120s · 21s · enemy ground · ×1 uses · bound · questionnaire §2 #482 |
| The Curse of Anraheir `wh3_main_spell_bound_the_curse_of_anraheir` | `excluded (auto: ground-target-only)` | melee_enemy | When in melee: cast on the ground under its current target (placement policy needed). | cd 120s · 21s · enemy ground · ×1 uses · bound · questionnaire §2 #482 |
| The Curse of Anraheir `wh_dlc05_spell_bound_the_curse_of_anraheir` | `excluded (auto: ground-target-only)` | melee_enemy | When in melee: cast on the ground under its current target (placement policy needed). | cd 120s · 21s · enemy ground · ×1 uses · bound · questionnaire §2 #482 |
| The Dark Master `wh3_main_lord_abilities_the_dark_master` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (70 m of 100 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 90s · 33s · enemy unit · questionnaire §2 #437 · enemy-targeting mechanism (harness 97) |
| The Enfeebling Foe `wh3_dlc23_spell_bound_enfeebling_foe` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (140 m of 200 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 60s · 17s · enemy unit · ×1 uses · wind-up 1s · bound · questionnaire §2 #478 · enemy-targeting mechanism (harness 97) |
| The Enfeebling Foe `wh3_dlc27_spell_bound_enfeebling_foe` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (140 m of 200 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 60s · 17s · enemy unit · ×3 uses · wind-up 1s · bound · questionnaire §2 #478 · enemy-targeting mechanism (harness 97) |
| The Enfeebling Foe `wh3_main_spell_bound_enfeebling_foe` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (140 m of 200 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 60s · 17s · enemy unit · ×2 uses · wind-up 1s · bound · questionnaire §2 #478 · enemy-targeting mechanism (harness 97) |
| The Enfeebling Foe `wh3_twa08_spell_bound_enfeebling_foe_keeper_of_secrets_ror` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (140 m of 200 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 60s · 17s · enemy unit · ×2 uses · wind-up 1s · bound · questionnaire §2 #478 · enemy-targeting mechanism (harness 97) |
| The Hammer of Karak Drazh `wh_main_weapon_abilities_the_hammer_of_karak_drazh` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (35 m of 50 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 90s · 50s · enemy unit · questionnaire §2 #438 · enemy-targeting mechanism (harness 97) |
| The Land Awakened `wh3_main_army_abilities_the_land_awakened` | `excluded (auto: army-bar ability (standing rule 10))` | melee_enemy | When in melee: cast on the ground under its current target (placement policy needed). | cd 120s · 1s · enemy ground · ×1 uses · wind-up 5s · army · questionnaire §2 #486 |
| The Tallyman's Blades `wh3_dlc25_character_abilities_tallymans_blades` | `implemented (enemy-ground: closest FIGHTING enemy)` | enemy_ground_melee | The CLOSEST enemy within the ability's 70% bound (35 m of its 50 m target_intercept_range) that is FIGHTING (in melee): the summon is placed on THAT ENEMY's ground (perform_special_ability_ground, fresh caster + fresh enemy, hold, pre-cast re-check). | cd 120s · 10s · friend/self · ×1 uses · wind-up 5s · questionnaire §2 #334 · **round 102 (2026-10-17):** implemented on the Gate of Khorne trigger per the user's summon ruling (harness 102) |
| The Tallyman's Blades Upgraded `wh3_dlc25_character_abilities_tallymans_blades_2` | `implemented (enemy-ground: closest FIGHTING enemy)` | enemy_ground_melee | The CLOSEST enemy within the ability's 70% bound (no real range (target_intercept_range = -1.0) - no 70% bound) that is FIGHTING (in melee): the summon is placed on THAT ENEMY's ground (perform_special_ability_ground, fresh caster + fresh enemy, hold, pre-cast re-check). | cd 120s · 10s · friend/self · ×1 uses · wind-up 5s · questionnaire §2 #334 · **round 102 (2026-10-17):** implemented on the Gate of Khorne trigger per the user's summon ruling (harness 102) |
| The Unmasking `wh3_dlc27_army_abilities_eternal_dance_tempo_3_fate_of_desperation` | `skipped (army-bar ability)` | melee_enemy | When in melee: cast at own feet (existing ground-cast path). | cd 120s · 48s · ground · ×1 uses · wind-up 3s · army · questionnaire §2 #352 |
| They Needs Stabbin’ `wh2_dlc15_character_abilities_they_needs_stabbin` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (52 m of 75 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 60s · 29s · enemy unit · questionnaire §2 #439 · enemy-targeting mechanism (harness 97) |
| Titan Headsman `wh3_dlc25_hero_abilities_titan_headsman` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (52 m of 75 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 90s · 29s · enemy unit · questionnaire §2 #440 · enemy-targeting mechanism (harness 97) |
| Torment Blade `wh3_main_weapon_abilities_torment_blade` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (35 m of 50 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 60s · 18s · enemy unit · questionnaire §2 #441 · enemy-targeting mechanism (harness 97) |
| Tormentor Sword `wh_main_weapon_abilities_tormentor_sword` | `implemented (in-melee self)` | melee_enemy | When in melee (and not fleeing): cast on self. | cd 90s · 9s · self · questionnaire §2 #212 |
| Transmutation of Lead `wh3_main_spell_bound_transmutation_of_lead` | `excluded (auto: ground-target-only)` | melee_enemy | When in melee: cast on the ground under its current target (placement policy needed). | cd 120s · 50s · enemy ground · ×1 uses · wind-up 5s · bound · questionnaire §2 #487 |
| Trophy Heads `wh2_main_lord_abilities_trophy_heads` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (105 m of 150 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 90s · 36s · enemy unit · questionnaire §2 #442 · enemy-targeting mechanism (harness 97) |
| Trophy Heads `wh3_main_daemon_wings_abilities_trophy_heads` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (105 m of 150 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 120s · 36s · enemy unit · questionnaire §2 #442 · enemy-targeting mechanism (harness 97) |
| Van Horstmann's Speculum `wh_main_item_abilities_van_horstmanns_speculum` | `implemented (in-melee self)` | melee_enemy | When in melee (and not fleeing): cast on self. | cd 90s · 16s · self · questionnaire §2 #218 |
| Virulent Contagion `wh3_main_lord_abilities_virulent_contagion` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (140 m of 200 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 120s · 30s · enemy unit · ×2 uses · questionnaire §2 #466 · enemy-targeting mechanism (harness 97) |
| Virulent Contagion Upgraded `wh3_main_lord_abilities_virulent_contagion_upgraded` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (140 m of 200 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 120s · 30s · enemy unit · ×3 uses · questionnaire §2 #466 · enemy-targeting mechanism (harness 97) |
| Visions of Madness `wh3_dlc27_qb_unit_abilities_visions_of_madness` | `excluded (not in wheel: boss-only unit)` | enemy_unit | — | When an enemy unit within the 70% bound (21 m of 30 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). · **round 101 (2026-10-17):** EXCLUDED - its ONLY grant path is `wh3_dlc27_bst_mon_jabberslythe_boss` (land_abil.tsv), a quest-battle boss variant; REMOVED from the mod (it was implemented before this round) |
| Warden's Cage `wh2_dlc15_character_abilities_wardens_cage` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (70 m of 100 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 120s · 25s · enemy unit · ×1 uses · questionnaire §2 #467 · enemy-targeting mechanism (harness 97) |
| Whip of Agony `wh2_twa03_weapon_abilities_whip_of_agony` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (52 m of 75 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 120s · 29s · enemy unit · questionnaire §2 #444 · enemy-targeting mechanism (harness 97) |
| Whip of Misery `wh2_main_spell_bound_whip_of_agony` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (140 m of 200 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 90s · 31s · enemy unit · ×3 uses · bound · questionnaire §2 #468 · enemy-targeting mechanism (harness 97) |
| Whispering Mist `wh3_dlc29_hero_abilities_whispering_mist` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (140 m of 200 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 90s · 32s · enemy unit · wind-up 1s · questionnaire §2 #475 · enemy-targeting mechanism (harness 97) |
| Willing Prey `wh3_main_lord_abilities_willing_prey` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (140 m of 200 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 90s · 15s · enemy unit · questionnaire §2 #445 · enemy-targeting mechanism (harness 97) |
| Winter’s Chill `wh3_dlc29_ability_bound_prayer_winters_chill` | `implemented (in-melee self)` | melee_enemy | When in melee (and not fleeing): cast on self. | cd 90s · 20s · self · wind-up 0.5s · unit · questionnaire §2 #293 |
| Winter’s Chill `wh3_dlc29_spell_bound_prayer_winters_chill` | `implemented (in-melee self)` | melee_enemy | When in melee (and not fleeing): cast on self. | cd 90s · 20s · self · wind-up 0.5s · bound · questionnaire §2 #293 |
| Word of Change `wh3_main_daemon_head_abilities_word_of_change` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (140 m of 200 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 120s · 42s · enemy unit · questionnaire §2 #446 · enemy-targeting mechanism (harness 97) |
| Word of Pain `wh2_dlc10_spell_bound_word_of_pain` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (140 m of 200 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 90s · 40s · enemy unit · ×2 uses · bound · questionnaire §2 #469 · enemy-targeting mechanism (harness 97) |
| Word of Pain `wh3_dlc27_spell_dark_magic_word_of_pain_bound_1use` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (140 m of 200 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 90s · 40s · enemy unit · ×1 uses · bound · questionnaire §2 #469 · enemy-targeting mechanism (harness 97) |
| You're Next! `wh2_dlc15_lord_abilities_youre_next` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (52 m of 75 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 90s · 24s · enemy unit · questionnaire §2 #447 · enemy-targeting mechanism (harness 97) |
| Deadly Onslaught `wh_main_character_abilities_deadly_onslaught` | `implemented` | charge | built: charge window OR in melee (field-verified) | cd 90s · 31s · self |
| Bloodthirst `wh3_main_lord_abilities_bloodthirst` | `implemented (charge and in-melee)` | charge | While charging (moving fast at the enemy, pre-contact): cast. | cd 60s · 17s · self |
| Colossal Strike `wh3_dlc24_character_abilities_colossal_strike` | `implemented (charge and in-melee)` | charge | While charging (moving fast at the enemy, pre-contact): cast. | cd 90s · 32s · self |
| Colossal Strike `wh3_dlc24_character_abilities_colossal_strike_summoned` | `implemented (charge and in-melee)` | charge | While charging (moving fast at the enemy, pre-contact): cast. | cd 90s · 32s · self |
| Crimson Juggernaut `wh3_dlc26_character_abilities_crimson_juggernaut` | `implemented (charge and in-melee)` | charge | While charging (moving fast at the enemy, pre-contact): cast. | cd 120s · 25s · self |
| Daemonic Onslaught `wh3_main_daemon_legs_abilities_daemonic_onslaught` | `implemented (charge and in-melee)` | charge | While charging (moving fast at the enemy, pre-contact): cast. | cd 90s · 34s · self |
| Deadly Onslaught `wh_dlc03_character_abilities_deadly_onslaught` | `implemented (charge and in-melee)` | charge | While charging (moving fast at the enemy, pre-contact): cast. | cd 90s · 31s · self |
| Flash Bomb `wh_pro01_lord_abilities_flash_bomb` | `excluded (auto: vortex)` | charge | When the unit is charged (enemy closes on it): cast. | cd 90s · 16s · enemy unit |
| Full Power! `wh3_dlc25_unit_abilities_full_power` | `implemented (charge and in-melee)` | charge | While charging (moving fast at the enemy, pre-contact): cast. | cd 90s · 28s · self · wind-up 1s |
| Guiding Strike `wh3_cp1_lord_abilities_guiding_strike` | `implemented (charge and in-melee)` | charge | While charging (moving fast at the enemy, pre-contact): cast. | cd 90s · 29s · self |
| Heaven's Flash `wh3_main_unit_abilities_stun_bomb` | `excluded (auto: vortex)` | charge | When the unit is charged (enemy closes on it): cast. | cd 90s · 31s · ground · ×1 uses |
| Locus of Fury `wh3_main_character_abilities_locus_of_fury` | `implemented (charge and in-melee)` | charge | While charging (moving fast at the enemy, pre-contact): cast. | cd 90s · 17s · self |
| Locus of Swiftness `wh3_main_character_abilities_locus_of_swiftness` | `implemented (charge and in-melee)` | charge | While charging (moving fast at the enemy, pre-contact): cast. | cd 90s · 40s · self |
| Masterful Strike `wh3_cp1_lord_abilities_mastered_strike` | `implemented (charge and in-melee)` | charge | While charging (moving fast at the enemy, pre-contact): cast. | cd 120s · 34s · self |
| More Power! `wh3_dlc23_unit_abilities_more_power` | `implemented (charge and in-melee)` | charge | While charging (moving fast at the enemy, pre-contact): cast. | cd 90s · 28s · self · wind-up 1s |
| Purge the Weak! `wh3_main_daemon_wings_abilities_purge_the_weak` | `implemented (charge and in-melee)` | charge | While charging (moving fast at the enemy, pre-contact): cast. | cd 90s · 22s · self |
| Shield of Thorns `wh2_dlc17_spell_bound_shield_of_thorns` | `implemented (charge and in-melee)` | charge | When the unit is charged (enemy closes on it): cast. | cd 90s · 30s · friend · ×2 uses · wind-up 3s · bound |
| Shield of Thorns `wh_dlc05_spell_bound_shield_of_thorns` | `implemented (charge and in-melee)` | charge | When the unit is charged (enemy closes on it): cast. | cd 90s · 30s · friend · ×2 uses · bound |
| Smoke Bomb `wh_dlc06_unit_abilities_smoke_bomb` | `excluded (auto: vortex)` | charge | When the unit is charged (enemy closes on it): cast. | cd 90s · 21s · self |
| Storm Hammer `wh3_dlc29_spell_bound_storm_hammer` | `implemented (charge and in-melee)` | charge | While charging (moving fast at the enemy, pre-contact): cast. | cd 120s · 25s · self |
| All Hands Hoay! `wh2_dlc11_character_abilities_all_hands_hoay` | `implemented (in-melee self)` | morale | When morale falls to wavering: cast. | cd 90s · 20s · self |
| Avast Ye! `wh2_dlc11_character_abilities_avast_ye` | `implemented (in-melee self)` | morale | When morale falls to wavering: cast. | cd 60s · 14s · self |
| Axe of Men `wh_dlc03_weapon_abilities_axe_of_men` | `implemented (in-melee self)` | morale | When morale falls to wavering: cast. | cd 120s · 46s · self |
| Call of Violence `wh_dlc03_character_abilities_call_of_violence` | `implemented (in-melee self)` | morale | When morale falls to wavering: cast. | cd 60s · 14s · self |
| Cold-Blooded `wh2_main_character_abilities_cold_blooded` | `implemented (in-melee self)` | morale | When morale falls to wavering: cast on the wavering friendly unit. | cd 60s · 40s · friend |
| Crown of Command `wh_main_item_abilities_crown_of_command` | `implemented (in-melee self)` | morale | When morale falls to wavering: cast on the wavering friendly unit. | cd 90s · 30s · friend |
| Daemonic Whispers `wh3_dlc27_character_abilities_slezuzus_voice` | `implemented (ally-targeted: ally_melee_buff)` | ally_unit | Cast on the chosen ALLY (trigger `ally_melee_buff`; class gate: plain ally buff (owner in melee) - ruled + requested MID-FLIGHT this round); trigger range = 140 m = 70% of the real 200 m. | cd 120s · 26s · friend · character · **round 98 (Class B): NEEDS A RULING** - the audit note itself says 'flag for the user'. · **round 99 (target-class-gated):** casts ON THE CHOSEN ALLY of the required class (plain ally buff (owner in melee) - ruled + requested MID-FLIGHT this round) - the offer test is `unit:unit_distance(ally)` <= its own 70% bound = floor(200 * 0.70) = 140 m (`FOURTH.ALLY_CAST_R200`) ONLY, never the engine's `unit_in_range`; fresh caster+ally handles. Was a self-cast. |
| Fight or Die! `wh_dlc08_lord_abilities_fight_or_die` | `implemented (in-melee self)` | morale | When morale falls to wavering: cast. | cd 90s · 18s · self |
| Focus Instincts `wh2_dlc12_lord_abilities_focus_instincts` | `implemented (in-melee self)` | morale | When morale falls to wavering: cast. | cd 90s · 40s · self |
| Get Back 'Ere! `wh_main_character_abilities_get_back_ere` | `implemented (in-melee self)` | morale | When morale falls to wavering: cast. | cd 60s · 14s · self |
| Iron-Handed Captain `wh3_dlc27_character_abilities_iron_hand_captain` | `implemented (ally-targeted: ally_broken)` | ally_unit | Cast on the chosen ALLY (trigger `ally_broken`; class gate: morale-BROKEN target (MoraleState == "broken")); trigger range = 140 m = 70% of the real 200 m. | cd 120s · 42s · friend · **round 98 (Class B): NEEDS A RULING** - needs a 'morale at or below broken' target gate (no existing ally family). · **round 99 (target-class-gated):** casts ON THE CHOSEN ALLY of the required class (morale-BROKEN target (MoraleState == "broken")) - the offer test is `unit:unit_distance(ally)` <= its own 70% bound = floor(200 * 0.70) = 140 m (`FOURTH.ALLY_CAST_R200`) ONLY, never the engine's `unit_in_range`; fresh caster+ally handles. Was a self-cast. |
| Magical Animus `wh_main_character_abilities_magical_animus` | `implemented (in-melee self)` | morale | When morale falls to wavering: cast. | cd 60s · 14s · self |
| Mighty Oath Stone `wh_dlc06_lord_abilities_mighty_oath_stone` | `implemented (in-melee self)` | morale | When morale falls to wavering: cast. | cd 90s · 25s · self |
| Mirror (Cold-Blooded) `wh2_dlc15_unit_abilities_mimic_cold_blooded` | `implemented (in-melee self)` | morale | When morale falls to wavering: cast. | cd 60s · 40s · self · ×2 uses |
| Moonshine `wh2_dlc11_item_abilities_moonshine` | `implemented (in-melee self)` | morale | When morale falls to wavering: cast. | cd 60s · 15s · self · ×1 uses |
| Pearl of Infinite Bleakness `wh2_main_item_abilities_pearl_of_infinite_bleakness` | `implemented (in-melee self)` | morale | When morale falls to wavering: cast. | cd 60s · 44s · self |
| Potion of Foolhardiness `wh_main_item_abilities_potion_of_foolhardiness` | `implemented (in-melee self)` | morale | When morale falls to wavering: cast. | cd 60s · 31s · self · ×1 uses |
| Preyton Horns `wh3_dlc27_item_abilities_preyton_horns` | `excluded (impossible: no enemy-unit read)` | morale | When morale falls to wavering: cast. | cd 90s · 24s · enemy unit · bound |
| Rally! `wh_main_character_abilities_rally` | `implemented (in-melee self)` | morale | When morale falls to wavering: cast. | cd 60s · 14s · self |
| Reanimate `wh2_dlc09_character_abilities_tomb_king_rally` | `implemented (in-melee self)` | morale | When morale falls to wavering: cast. | cd 60s · 14s · self |
| Reanimate Upgraded `wh2_dlc09_character_abilities_tomb_king_rally_upgraded` | `implemented (in-melee self)` | morale | When morale falls to wavering: cast. | cd 90s · 10s · self |
| Shock Collar `wh2_dlc16_hero_abilities_shock_collar` | `implemented (ally-targeted: ally_wavering)` | ally_unit | When morale falls to wavering: cast on the wavering friendly unit. | cd 60s · 24s · friend · **round 98 (Class B):** casts ON THE CHOSEN ALLY - ally wavering - the CLOSEST WAVERING ally in range; own 70% bound = floor(100 * 0.70) = 70 m (FOURTH.ALLY_CAST_R100), offer test on unit:unit_distance only, fresh caster+ally handles. Was a self-cast |
| Tacticians, Rally! `wh3_dlc24_character_abilities_tacticians_rally` | `implemented (in-melee self)` | morale | When morale falls to wavering: cast on the wavering friendly unit. | cd 60s · 14s · friend/self |
| The Wintertooth Crown `wh_dlc08_item_abilities_the_wintertooth_crown` | `implemented (in-melee self)` | morale | When morale falls to wavering: cast. | cd 120s · 24s · self |
| Unholy Clamour `wh2_main_mount_abilities_unholy_clamour` | `implemented (in-melee self)` | morale | When morale falls to wavering: cast. | cd 120s · 18s · self |
| Ursun's Mighty Roar `wh3_main_pro_character_abilities_ursuns_roar_2` | `implemented (in-melee self)` | morale | When morale falls to wavering: cast. | cd 60s · 30s · self |
| Ursun's Roar `wh3_main_character_abilities_ursuns_roar` | `implemented (in-melee self)` | morale | When morale falls to wavering: cast. | cd 60s · 9s · self |
| Ursun's Roar `wh3_main_pro_character_abilities_ursuns_roar` | `implemented (in-melee self)` | morale | When morale falls to wavering: cast. | cd 60s · 20s · self |
| Ursun's Roar `wh3_main_pro_character_abilities_ursuns_roar_1` | `implemented (in-melee self)` | morale | When morale falls to wavering: cast. | cd 60s · 30s · self |
| Ursun's Roar `wh3_main_pro_character_abilities_ursuns_roar_3` | `implemented (in-melee self)` | morale | When morale falls to wavering: cast. | cd 60s · 30s · self |
| A Joyous Deliquescence `wh3_dlc27_army_abilities_eternal_dance_tempo_3_denial_of_death` | `excluded (auto: army-bar ability (standing rule 10))` | degraded | When health/men drop below the set line: cast on the hurt friendly unit. | cd 90s · 24s · friend · ×2 uses · wind-up 1s · army |
| Ancestral Rune of Valaya `wh2_dlc17_army_abilities_ancestral_rune_of_valaya` | `excluded (auto: army-bar ability (standing rule 10))` | degraded | When health/men drop below the set line: cast on the ground by the hurt unit. | cd 120s · 24s · ground · ×1 uses · wind-up 5s · army |
| Apotheosis `wh3_dlc27_army_high_magic_apotheosis` | `excluded (auto: army-bar ability (standing rule 10))` | degraded | When health/men drop below the set line: cast on the hurt friendly unit. | cd 29s · 10s · friend · ×3 uses · wind-up 1s · army |
| Berry Wine `wh2_dlc16_item_abilities_berry_wine` | `implemented (health<=75 (no melee gate))` | degraded | When health/men drop below the set line: cast on the hurt friendly unit. | cd 120s · 14s · friend · ×1 uses |
| Blood Chalice `wh3_dlc29_hero_abilities_blood_chalice` | `implemented (health<=75 (no melee gate))` | degraded | When health/men drop below the set line: cast. | cd 90s · 8s · self |
| Blood Chalice of Bathori `wh_pro02_item_abilities_blood_chalice_of_bathori` | `implemented (health<=75 (no melee gate))` | degraded | When health/men drop below the set line: cast on the hurt friendly unit. | cd 120s · 26s · friend |
| Blood Sacrifice `wh3_dlc26_lord_abilities_blood_sacrifice` | `implemented (blood_sacrifice)` | degraded | When health/men drop below the set line: cast on the hurt friendly unit. | cd 60s · 10s · friend · ×3 uses |
| Breath of Darkness `wh3_dlc29_spell_bound_undeath_morkharn_breath_of_darkness` | `implemented (health<=75 (no melee gate))` | degraded | When health/men drop below the set line: cast on the hurt friendly unit. | cd 31s · 14s · friend · ×2 uses · wind-up 1s · bound |
| Breath of Darkness Upgraded `wh3_dlc29_spell_bound_undeath_morkharn_breath_of_darkness_upgraded` | `implemented (health<=75 (no melee gate))` | degraded | When health/men drop below the set line: cast on the hurt friendly unit. | cd 31s · 14s · friend/self · ×2 uses · wind-up 1s · bound |
| Bugman's XXXXXX `wh3_dlc26_item_abilities_bugmans_xxxxxx` | `implemented (health<=75 (no melee gate))` | degraded | When health/men drop below the set line: cast. | cd 120s · 18s · self |
| Dreaming Ring I `wh2_dlc16_item_abilities_dreaming_ring_i` | `implemented (health<=75 (no melee gate))` | degraded | When health/men drop below the set line: cast on the hurt friendly unit. | cd 60s · 13s · friend |
| Dreaming Ring II `wh2_dlc16_item_abilities_dreaming_ring_ii` | `implemented (health<=75 (no melee gate))` | degraded | When health/men drop below the set line: cast on the hurt friendly unit. | cd 90s · 13s · friend |
| Dreaming Ring III `wh2_dlc16_item_abilities_dreaming_ring_iii` | `implemented (health<=75 (no melee gate))` | degraded | When health/men drop below the set line: cast on the hurt friendly unit. | cd 120s · 17s · friend |
| Earth Blood `wh2_dlc16_spell_bound_earth_blood` | `implemented (health<=75 (no melee gate))` | degraded | When health/men drop below the set line: cast on the hurt friendly unit. | cd 60s · 7s · friend/self · ×2 uses · bound |
| Earth Blood `wh3_main_spell_bound_earth_blood` | `implemented (health<=75 (no melee gate))` | degraded | When health/men drop below the set line: cast on the hurt friendly unit. | cd 60s · 7s · friend/self · ×2 uses · wind-up 1s · bound |
| Eat da Runts! `wh3_dlc26_unit_abilities_eat_da_runts` | `implemented (eat_da_runts)` | degraded | When health/men drop below the set line: cast on the hurt friendly unit. | cd 90s · 10s · friend · ×3 uses |
| Elvish Healing Herbs `wh3_dlc27_unit_abilities_elfish_healing_herbs` | `implemented (ally-targeted: ally_heal)` | ally_unit | When health/men drop below the set line: cast on the hurt friendly unit. | cd 90s · 27s · friend · ×3 uses · **round 98 (Class B):** casts ON THE CHOSEN ALLY - ally heal - the LOWEST-health ally in range at or below 75%; own 70% bound = floor(50 * 0.70) = 35 m (FOURTH.ALLY_CAST_R50), offer test on unit:unit_distance only, fresh caster+ally handles. Was a self-cast |
| Fecundity `wh3_main_army_abilities_fecundity` | `excluded (auto: army-bar ability (standing rule 10))` | degraded | When health/men drop below the set line: cast on the hurt friendly unit. | cd 90s · 12s · friend · army |
| Fleshy Abundance `wh3_dlc20_spell_bound_fleshy_abundance` | `implemented (health<=75 (no melee gate))` | degraded | When health/men drop below the set line: cast on the hurt friendly unit. | cd 54s · 18s · friend · ×1 uses · wind-up 5s · bound |
| Gluttony `wh3_main_army_abilities_gluttony` | `excluded (auto: army-bar ability (standing rule 10))` | degraded | When health/men drop below the set line: cast on the hurt friendly unit. | cd 90s · 20s · friend · ×1 uses · army |
| Hieratic Jar `wh2_dlc09_item_abilities_hieratic_jar` | `implemented (health<=75 (no melee gate))` | degraded | When health/men drop below the set line: cast. | cd 60s · 33s · self · ×1 uses |
| Icon of the King `wh3_dlc29_item_abilities_icon_of_the_king` | `excluded (auto: no effect text available (unsourceable))` | degraded | When health/men drop below the set line: cast. | cd 120s · 16s · self · ×2 uses · item |
| Immortal Will `wh_main_hero_abilities_immortal_will` | `implemented (health<=75 (no melee gate))` | degraded | When health/men drop below the set line: cast. | cd 60s · 13s · self |
| Invocation of Nehek `wh3_dlc29_spell_bound_invocation_of_nehek` | `implemented (health<=75 (no melee gate))` | degraded | When health/men drop below the set line: cast. | cd 30s · 18s · self · ×2 uses · wind-up 1s |
| Locus of Fecundity `wh3_main_character_abilities_locus_of_fecundity` | `implemented (health<=75 (no melee gate))` | degraded | When health/men drop below the set line: cast. | cd 90s · 11s · self · ×3 uses |
| Makaisson's Persuader `wh3_dlc25_weapon_abilities_makaissons_persuader` | `implemented (ally-targeted: ally_warmachine_heal)` | ally_unit | Cast on the chosen ALLY (trigger `ally_warmachine_heal`; class gate: WAR MACHINE target - DERIVED (main_units.caste == "warmachine"; 68 keys)); trigger range = 70 m = 70% of the real 100 m. | cd 120s · 17s · friend · ×3 uses · **round 98 (Class B): NEEDS A RULING** - needs a war-machine / artillery TARGET-CLASS filter (no existing ally family). · **round 99 (target-class-gated):** casts ON THE CHOSEN ALLY of the required class (WAR MACHINE target - DERIVED (main_units.caste == "warmachine"; 68 keys)) - the offer test is `unit:unit_distance(ally)` <= its own 70% bound = floor(100 * 0.70) = 70 m (`FOURTH.ALLY_CAST_R100`) ONLY, never the engine's `unit_in_range`; fresh caster+ally handles. Was a self-cast. |
| Moulder Clanstone `wh2_main_army_abilities_moulder_clanstone` | `excluded (auto: army-bar ability (standing rule 10))` | degraded | When health/men drop below the set line: cast on the ground by the hurt unit. | cd 120s · 22s · ground · ×3 uses · army |
| Necroparasites `wh2_dlc16_unit_abilities_neuroparasites` | `implemented (health<=75 (no melee gate))` | degraded | When health/men drop below the set line: cast. | cd 120s · 21s · self · ×1 uses |
| Necrotic Phylactery `wh3_dlc25_item_abilities_necrotic_phylactry` | `implemented (health<=75 (no melee gate))` | degraded | When health/men drop below the set line: cast. | cd 90s · 18s · self · ×1 uses |
| Patch Up `wh2_dlc13_character_abilities_patch_up` | `implemented (ally-targeted: ally_heal)` | ally_unit | When health/men drop below the set line: cast on the hurt friendly unit. | cd 90s · 7s · friend · ×3 uses · **round 98 (Class B):** casts ON THE CHOSEN ALLY - ally heal - the LOWEST-health ally in range at or below 75%; own 70% bound = floor(100 * 0.70) = 70 m (FOURTH.ALLY_CAST_R100), offer test on unit:unit_distance only, fresh caster+ally handles. Was a self-cast |
| Pestilent Regeneration `wh3_main_daemon_head_abilities_pestilent_regeneration` | `implemented (health<=75 (no melee gate))` | degraded | When health/men drop below the set line: cast. | cd 120s · 24s · self |
| Potion of Charoi `wh2_main_lord_abilities_potion_of_charoi` | `implemented (health<=75 (no melee gate))` | degraded | When health/men drop below the set line: cast. | cd 60s · 9s · self · ×4 uses |
| Potion of Healing `wh_main_item_abilities_potion_of_healing` | `implemented (health<=75 (no melee gate))` | degraded | When health/men drop below the set line: cast. | cd 60s · 33s · self · ×1 uses |
| Radiant Gem of Hoeth `wh2_main_spell_bound_radiant_gem_of_hoeth` | `implemented (health<=75 (no melee gate))` | degraded | When health/men drop below the set line: cast on the hurt friendly unit. | cd 60s · 10s · friend · ×4 uses · bound |
| Reforge `wh3_dlc23_character_abilities_reforge` | `implemented (ally-targeted: ally_hellforged_heal)` | ally_unit | Cast on the chosen ALLY (trigger `ally_hellforged_heal`; class gate: HELL-FORGED target - DERIVED (unit_attributes attribute "hellforged"; 13 keys)); trigger range = 70 m = 70% of the real 100 m. | cd 60s · 19s · friend · ×2 uses · **round 98 (Class B): NEEDS A RULING** - needs a Hell-Forged TARGET-CLASS filter (no existing ally family). · **round 99 (target-class-gated):** casts ON THE CHOSEN ALLY of the required class (HELL-FORGED target - DERIVED (unit_attributes attribute "hellforged"; 13 keys)) - the offer test is `unit:unit_distance(ally)` <= its own 70% bound = floor(100 * 0.70) = 70 m (`FOURTH.ALLY_CAST_R100`) ONLY, never the engine's `unit_in_range`; fresh caster+ally handles. Was a self-cast. |
| Regenerating Flesh `wh_main_item_abilities_regenerating_flesh` | `implemented (health<=75 (no melee gate))` | degraded | When health/men drop below the set line: cast. | cd 60s · 33s · self · ×1 uses |
| Regrowth `wh2_dlc16_spell_bound_regrowth` | `implemented (health<=75 (no melee gate))` | degraded | When health/men drop below the set line: cast on the hurt friendly unit. | cd 120s · 26s · friend · ×1 uses · bound |
| Remouldered `wh2_dlc16_lord_abilities_remouldered` | `implemented (ally-targeted: ally_monster_heal)` | ally_unit | Cast on the chosen ALLY (trigger `ally_monster_heal`; class gate: MONSTER target - DERIVED (main_units.caste == "monster"; 235 keys)); trigger range = 70 m = 70% of the real 100 m. | cd 120s · 24s · friend · ×3 uses · **round 98 (Class B): NEEDS A RULING** - needs a monster TARGET-CLASS filter (no existing ally family). · **round 99 (target-class-gated):** casts ON THE CHOSEN ALLY of the required class (MONSTER target - DERIVED (main_units.caste == "monster"; 235 keys)) - the offer test is `unit:unit_distance(ally)` <= its own 70% bound = floor(100 * 0.70) = 70 m (`FOURTH.ALLY_CAST_R100`) ONLY, never the engine's `unit_in_range`; fresh caster+ally handles. Was a self-cast. |
| Restore `wh2_dlc09_character_abilities_restore` | `implemented (ally-targeted: ally_construct_heal)` | ally_unit | Cast on the chosen ALLY (trigger `ally_construct_heal`; class gate: CONSTRUCT target - DERIVED (unit_attributes attribute "construct"; 29 keys)); trigger range = 70 m = 70% of the real 100 m. | cd 60s · 24s · friend · ×2 uses · **round 98 (Class B): NEEDS A RULING** - needs a construct TARGET-CLASS filter (no existing ally family). · **round 99 (target-class-gated):** casts ON THE CHOSEN ALLY of the required class (CONSTRUCT target - DERIVED (unit_attributes attribute "construct"; 29 keys)) - the offer test is `unit:unit_distance(ally)` <= its own 70% bound = floor(100 * 0.70) = 70 m (`FOURTH.ALLY_CAST_R100`) ONLY, never the engine's `unit_in_range`; fresh caster+ally handles. Was a self-cast. |
| Revivification Crystal `wh2_main_unit_abilities_revivification_crystal` | `implemented (ally-targeted: ally_heal)` | ally_unit | When health/men drop below the set line: cast on the hurt friendly unit. | cd 60s · 20s · friend · ×7 uses · wind-up 3s · **round 98 (Class B):** casts ON THE CHOSEN ALLY - ally heal - the LOWEST-health ally in range at or below 75%; own 70% bound = floor(100 * 0.70) = 70 m (FOURTH.ALLY_CAST_R100), offer test on unit:unit_distance only, fresh caster+ally handles. Was a self-cast |
| Saint Annushka's Finger Bone `wh3_main_item_abilities_saint_annushkas_finger_bone` | `implemented (health<=75 (no melee gate))` | degraded | When health/men drop below the set line: cast. | cd 60s · 13s · self |
| Salyak's Lullaby `wh3_main_character_abilities_salyaks_lullaby` | `implemented (health<=75 (no melee gate))` | degraded | When health/men drop below the set line: cast. | cd 90s · 15s · self · ×3 uses |
| Scroll of Power `wh_main_item_abilities_scroll_of_power` | `implemented (health<=75 (no melee gate))` | degraded | When health/men drop below the set line: cast. | cd 0s · 57s · self · ×1 uses |
| Skalm `wh2_main_item_abilities_skalm` | `implemented (health<=75 (no melee gate))` | degraded | When health/men drop below the set line: cast. | cd 60s · 33s · self · ×1 uses |
| Skar's Kraken-Killer `wh3_main_weapon_abilities_skars_kraken_killer` | `implemented (health<=75 (no melee gate))` | degraded | When health/men drop below the set line: cast. | cd 120s · 29s · self |
| Slime Smoothie `wh2_dlc15_character_abilities_slimy_smoothie` | `excluded (auto: vortex)` | degraded | When health/men drop below the set line: cast on the hurt friendly unit. | cd 30s · 14s · friend/self · ×3 uses · wind-up 1s |
| Storm of Renewal `wh3_dlc20_cataclysm_bound_storm_of_renewal` | `excluded (auto: ground-target-only)` | degraded | When health/men drop below the set line: cast on the ground by the hurt unit. | cd 120s · 20s · ground · ×1 uses · wind-up 5s · bound |
| Storm of Renewal `wh3_dlc27_cataclysm_bound_storm_of_renewal` | `excluded (auto: ground-target-only)` | degraded | When health/men drop below the set line: cast on the ground by the hurt unit. | cd 120s · 20s · ground · ×3 uses · wind-up 5s · bound |
| The Effulgent Incense `wh3_dlc27_army_abilities_eternal_dance_tempo_3_path_of_indulgence` | `excluded (auto: army-bar ability (standing rule 10))` | degraded | When health/men drop below the set line: cast on the ground by the hurt unit. | cd 120s · 24s · ground · ×1 uses · wind-up 3s · army |
| Trollguts `wh3_dlc26_spell_bound_trollguts` | `implemented (health<=75 (no melee gate))` | degraded | When health/men drop below the set line: cast on the hurt friendly unit. | cd 90s · 35s · friend · ×1 uses · wind-up 5s · bound |
| Vortical Enrichment `wh2_main_army_abilities_vortic_enrichment` | `excluded (auto: army-bar ability (standing rule 10))` | degraded | When health/men drop below the set line: cast on the ground by the hurt unit. | cd 30s · 5s · ground · army |
| Arcane Surge `wh3_main_army_abilities_arcane_surge` | `excluded (auto: army-bar ability (standing rule 10))` | ready | Whenever the engine allows (no readable condition): cast on an ally. | cd 60s · 14s · friend · army |
| Armour of Caledor `wh2_dlc15_item_abilities_armour_of_caledor` | `implemented (in-melee self)` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 180s · 20s · self · ×3 uses |
| Armour of the Stars `wh2_main_item_abilities_armour_of_the_stars` | `excluded (auto: flanking / ambush (stealth/escape, family decision 2026-10-09))` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 90s · 73s · self · triage-family: Flanking / ambush (flanking_opportunity) |
| Ballistics Calibration `wh_main_hero_abilities_ballistics_calibration` | `excluded (auto: ground-target-only)` | ready | Whenever the engine allows (no readable condition): cast on the ground. | cd 90s · 22s · ground |
| Battlefield Resupply `wh2_dlc11_quest_battle_supply` | `excluded (auto: no effect text available (unsourceable))` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 120s · 30s · self · ×3 uses · quest |
| Black Hammer of Hashut `wh3_dlc23_weapon_abilities_black_hammer_of_hashut` | `excluded (auto: no effect text available (unsourceable))` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 120s · 32s · self |
| Black Periapt `wh_main_item_abilities_black_periapt` | `implemented (in-melee self)` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 120s · 27s · self |
| Black Staff `wh2_main_spell_bound_black_staff` | `implemented (in-melee self)` | ready | Whenever the engine allows (no readable condition): cast on an ally. | cd 90s · 20s · friend · ×3 uses · bound |
| Blessed Helm of the Oblast `wh3_dlc24_item_abilities_blessed_helm_of_the_oblast` | `implemented (in-melee self)` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 90s · 30s · self |
| Book of Hoeth `wh2_main_item_abilities_book_of_hoeth` | `implemented (in-melee self)` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 90s · 36s · self |
| Boom! `wh_main_unit_abilities_boom` | `implemented (in-melee self)` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 90s · 15s · self |
| Channelling Spire `wh2_main_army_abilities_channeling_spire` | `excluded (auto: army-bar ability (standing rule 10))` | ready | Whenever the engine allows (no readable condition): cast on the ground. | cd 60s · -1s · ground · ×3 uses · wind-up 1s · army |
| Channelling Staff `wh_main_item_abilities_channelling_staff` | `implemented (in-melee self)` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 60s · 29s · self |
| Charmed Shield `wh_main_weapon_abilities_charmed_shield` | `implemented (in-melee self)` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 60s · 17s · self |
| Cloak of the Dunes `wh2_dlc09_item_abilities_cloak_of_the_dunes` | `excluded (auto: no effect text available (unsourceable))` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 90s · 73s · self |
| Concealment Bombs `wh2_main_character_abilities_concealment_bombs` | `excluded (auto: flanking / ambush (stealth/escape, family decision 2026-10-09))` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 90s · 73s · self · ×3 uses · triage-family: Flanking / ambush (flanking_opportunity) |
| Concealment Bombs `wh2_main_unit_abilities_concealment_bombs` | `excluded (auto: flanking / ambush (stealth/escape, family decision 2026-10-09))` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 90s · 73s · self · ×3 uses · triage-family: Flanking / ambush (flanking_opportunity) |
| Crooked Dice `wh3_dlc23_hero_abilities_crooked_dice` | `excluded (auto: no effect text available (unsourceable))` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 90s · 30s · self |
| Deranged Munitions `wh3_dlc25_lord_abilities_deranged_munitions` | `implemented (in-melee self)` | ready | Whenever the engine allows (no readable condition): cast on an ally. | cd 90s · 30s · friend |
| Deranged Munitions Upgraded `wh3_dlc25_lord_abilities_deranged_munitions_upgraded` | `implemented (in-melee self)` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 90s · 30s · self |
| Eagle Bow `wh2_dlc16_weapon_abilities_eagle_bow` | `excluded (impossible: already rejected by user (tactical escape/stealth))` | ready | Whenever the engine allows (no readable condition): cast on an ally. | cd 60s · 25s · friend |
| Earthing Rod `wh_main_item_abilities_earthing_rod` | `implemented (in-melee self)` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 60s · 36s · self · ×1 uses |
| Embers of the Phoenix `wh2_main_spell_bound_embers_of_the_phoenix` | `implemented (in-melee self)` | ready | Whenever the engine allows (no readable condition): cast on an ally. | cd 90s · 28s · friend/self · ×3 uses · bound |
| Enchanted Ballistics `wh2_dlc11_character_abilities_ballistic_enchantment` | `implemented (in-melee self)` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 90s · 32s · self |
| Entrenchment `wh_main_unit_abilities_entrenchment` | `implemented (in-melee self)` | ready | Whenever the engine allows (no readable condition): cast on an ally. | cd 90s · 44s · friend |
| Envelop in Mist `wh2_dlc15_army_abilities_envelop_in_mist` | `excluded (impossible: already rejected by user (tactical escape/stealth))` | ready | Whenever the engine allows (no readable condition): cast on the ground. | cd 120s · 43s · ground · army |
| Envelop in Mist `wh3_dlc27_character_abilities_envelop_in_mist_bound` | `excluded (impossible: already rejected by user (tactical escape/stealth))` | ready | Whenever the engine allows (no readable condition): cast on the ground. | cd 120s · 22s · ground · ×1 uses |
| Extra Ingredients `wh3_main_character_abilities_extra_ingredients` | `implemented (in-melee self)` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 90s · 31s · self |
| Favoured by the Matriarch `wh3_dlc27_hero_abilities_favoured_by_the_matriarch` | `implemented (in-melee self)` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 90s · 26s · self |
| Forbidden Rod `wh_main_item_abilities_forbidden_rod` | `implemented (in-melee self)` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 90s · 23s · self · ×3 uses |
| From the Shadows `wh3_main_character_abilities_from_the_shadows` | `excluded (auto: flanking / ambush (stealth/escape, family decision 2026-10-09))` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 120s · 38s · self · triage-family: Flanking / ambush (flanking_opportunity) |
| Funnel of Flame `wh2_dlc13_lord_abilities_funnel_of_flame` | `implemented (in-melee self)` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 90s · 33s · self |
| Glacial Defence `wh3_twa08_unit_abilities_glacial_defence` | `implemented (in-melee self)` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 60s · 21s · self |
| Grut's Sickle `wh3_main_item_abilities_gruts_sickle` | `implemented (ally-targeted: winds_maxhp)` | ally_unit | Cast on the chosen ALLY (trigger `ally_winds`; class gate: the ally with the HIGHEST ABSOLUTE HIT POINTS REMAINING (max HealthValue) - ruled + requested MID-FLIGHT this round); trigger range = 70 m = 70% of the real 100 m. | cd 60s · 20s · friend · ×3 uses · **round 98 (Class B): NEEDS A RULING** - rule 14 - carries a health COST (drawback); the note says 'flag for the user'. · **round 99 (target-class-gated):** casts ON THE CHOSEN ALLY of the required class (the ally with the HIGHEST ABSOLUTE HIT POINTS REMAINING (max HealthValue) - ruled + requested MID-FLIGHT this round) - the offer test is `unit:unit_distance(ally)` <= its own 70% bound = floor(100 * 0.70) = 70 m (`FOURTH.ALLY_CAST_R100`) ONLY, never the engine's `unit_in_range`; fresh caster+ally handles. Was a self-cast. |
| Hag's Denial `wh3_dlc24_unit_abilities_hags_denial` | `excluded (auto: no effect text available (unsourceable))` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 120s · 44s · self · ×1 uses |
| Hagtree Fetish `wh_dlc03_item_abilities_hagtree_fetish` | `implemented (in-melee self)` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 60s · 29s · self · ×1 uses |
| Hail of Fire `wh2_dlc13_lord_abilities_hail_of_fire` | `implemented (in-melee self)` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 90s · 22s · self |
| Hand of Glory `wh3_dlc27_army_high_magic_hand_of_glory` | `excluded (auto: army-bar ability (standing rule 10))` | ready | Whenever the engine allows (no readable condition): cast on an ally. | cd 28s · 29s · friend · ×3 uses · wind-up 1s · army |
| Hidden in Time `wh3_main_lord_abilities_hidden_in_time` | `excluded (auto: flanking / ambush (stealth/escape, family decision 2026-10-09))` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 90s · 73s · self · ×2 uses · triage-family: Flanking / ambush (flanking_opportunity) |
| Horn of Vaul `wh2_main_item_abilities_dragonhorn` | `implemented (in-melee self)` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 0s · 28s · self · ×1 uses |
| Hunter's Call `wh2_dlc13_character_ability_hunters_call` | `excluded (auto: no effect text available (unsourceable))` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 120s · 32s · self · ×3 uses |
| Inspired Marksmanship I `wh3_main_lord_abilities_inspired_marksmanship_i` | `implemented (ally-targeted: ally_missile)` | ally_unit | Cast on the chosen ALLY (trigger `ally_missile`; class gate: missile-capable target - DERIVED (land_units.primary_missile_weapon non-empty; 493 keys)); trigger range = 70 m = 70% of the real 100 m. | cd 60s · 29s · friend · **round 98 (Class B): NEEDS A RULING** - needs a missile-capability target gate (no existing ally family). · **round 99 (target-class-gated):** casts ON THE CHOSEN ALLY of the required class (missile-capable target - DERIVED (land_units.primary_missile_weapon non-empty; 493 keys)) - the offer test is `unit:unit_distance(ally)` <= its own 70% bound = floor(100 * 0.70) = 70 m (`FOURTH.ALLY_CAST_R100`) ONLY, never the engine's `unit_in_range`; fresh caster+ally handles. Was a self-cast. |
| Inspired Marksmanship II `wh3_main_lord_abilities_inspired_marksmanship_ii` | `implemented (ally-targeted: ally_missile)` | ally_unit | Cast on the chosen ALLY (trigger `ally_missile`; class gate: missile-capable target - DERIVED (land_units.primary_missile_weapon non-empty; 493 keys)); trigger range = 70 m = 70% of the real 100 m. | cd 90s · 44s · friend · **round 98 (Class B): NEEDS A RULING** - needs a missile-capability target gate (no existing ally family). · **round 99 (target-class-gated):** casts ON THE CHOSEN ALLY of the required class (missile-capable target - DERIVED (land_units.primary_missile_weapon non-empty; 493 keys)) - the offer test is `unit:unit_distance(ally)` <= its own 70% bound = floor(100 * 0.70) = 70 m (`FOURTH.ALLY_CAST_R100`) ONLY, never the engine's `unit_in_range`; fresh caster+ally handles. Was a self-cast. |
| Inspired Marksmanship III `wh3_main_lord_abilities_inspired_marksmanship_iii` | `implemented (ally-targeted: ally_missile)` | ally_unit | Cast on the chosen ALLY (trigger `ally_missile`; class gate: missile-capable target - DERIVED (land_units.primary_missile_weapon non-empty; 493 keys)); trigger range = 70 m = 70% of the real 100 m. | cd 120s · 44s · friend · **round 98 (Class B): NEEDS A RULING** - needs a missile-capability target gate (no existing ally family). · **round 99 (target-class-gated):** casts ON THE CHOSEN ALLY of the required class (missile-capable target - DERIVED (land_units.primary_missile_weapon non-empty; 493 keys)) - the offer test is `unit:unit_distance(ally)` <= its own 70% bound = floor(100 * 0.70) = 70 m (`FOURTH.ALLY_CAST_R100`) ONLY, never the engine's `unit_in_range`; fresh caster+ally handles. Was a self-cast. |
| Jagged Dagger `wh_dlc03_item_abilities_jagged_dagger` | `implemented (in-melee self)` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 60s · 31s · self |
| Locus of Abjuration `wh3_main_character_abilities_locus_of_abjuration` | `implemented (in-melee self)` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 90s · 25s · self |
| Locus of Change `wh3_main_character_abilities_locus_of_change` | `implemented (in-melee self)` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 90s · 40s · self |
| Locus of Conjuration `wh3_main_character_abilities_locus_of_conjuration` | `implemented (in-melee self)` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 90s · 20s · self |
| Loec's Blessing `wh2_dlc16_lord_abilities_loecs_blessing` | `excluded (impossible: already rejected by user (tactical escape/stealth))` | ready | Whenever the engine allows (no readable condition): cast on an ally. | cd 90s · 32s · friend/self |
| Loec's Shroud `wh_pro04_unit_abilities_loecs_shroud` | `excluded (auto: flanking / ambush (stealth/escape, family decision 2026-10-09))` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 120s · 44s · self · triage-family: Flanking / ambush (flanking_opportunity) |
| Master of Mists `wh3_dlc27_character_abilities_master_of_mists` | `excluded (auto: ground-target-only)` | ready | Whenever the engine allows (no readable condition): cast on the ground. | cd 120s · 58s · ground · ×2 uses |
| Master of Mists `wh3_dlc27_character_abilities_master_of_mists_custom` | `excluded (auto: ground-target-only)` | ready | Whenever the engine allows (no readable condition): cast on the ground. | cd 120s · 36s · ground · ×2 uses |
| Master of the Black Arts `wh_main_lord_abilities_master_of_the_black_arts` | `implemented (in-melee self)` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 90s · 15s · self |
| Master Predator `wh2_dlc17_lord_abilities_master_predator` | `implemented (in-melee self)` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 1s · -1s · self · wind-up 1s |
| Maw Shard `wh3_main_item_abilities_maw_shard` | `implemented (in-melee self)` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 60s · 22s · self · ×1 uses |
| Mirror (Loec's Shroud) `wh2_dlc15_unit_abilities_mimic_loecs_shroud` | `excluded (auto: flanking / ambush (stealth/escape, family decision 2026-10-09))` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 120s · 44s · self · triage-family: Flanking / ambush (flanking_opportunity) |
| More Powder! `wh2_dlc11_hero_abilities_more_powder` | `excluded (auto: no ammo-low read (ammo replenish))` | ready | Whenever the engine allows (no readable condition): cast on an ally. | cd 60s · 10s · friend · ×4 uses |
| Morgrim's Eye `wh3_dlc23_item_abilities_morgrims_eye` | `implemented (in-melee self)` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 120s · 32s · self |
| Neferra's Scrolls of Mighty Incantations `wh2_dlc09_item_abilities_neferras_scrolls_of_mighty_incantations` | `implemented (in-melee self)` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 90s · 31s · self · ×1 uses |
| Of Warp and Ruin `wh3_dlc29_unit_abilities_of_warp_and_ruin` | `excluded (auto: no effect text available (unsourceable))` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 120s · 32s · self |
| Ominous Powder `wh3_dlc25_item_abilities_ominous_powder` | `excluded (auto: no effect text available (unsourceable))` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 120s · 30s · self |
| Perfect Predator `wh3_dlc27_unit_abilities_perfect_predator` | `excluded (impossible: already rejected by user (tactical escape/stealth))` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 120s · 48s · self |
| Potion of Farsight `wh3_main_item_abilities_potion_of_farsight` | `implemented (in-melee self)` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 60s · 36s · self · ×1 uses |
| Potion of Speed `wh_main_item_abilities_potion_of_speed` | `implemented (in-melee self)` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 60s · 36s · self · ×1 uses |
| Power Familiar `wh3_dlc27_item_abilities_power_familiar` | `implemented (in-melee self)` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 90s · 22s · self · ×1 uses |
| Power Stone `wh_main_item_abilities_power_stone` | `implemented (in-melee self)` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 60s · 31s · self · ×1 uses |
| Prismatic Amplifier `wh3_main_item_abilities_prismatic_amplifier` | `implemented (in-melee self)` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 90s · 36s · self |
| Restock! `wh2_dlc17_hero_abilities_more_powder_generic` | `excluded (auto: no ammo-low read (ammo replenish))` | ready | Whenever the engine allows (no readable condition): cast on an ally. | cd 60s · 10s · friend · ×4 uses |
| Restock! `wh3_dlc25_abilities_restock_gunnery_school` | `excluded (auto: no ammo-low read (ammo replenish))` | ready | Whenever the engine allows (no readable condition): cast on an ally. | cd 60s · 10s · friend · ×2 uses |
| Rock Bottom `wh2_dlc15_unit_abilities_rock_bottom` | `excluded (auto: no effect text available (unsourceable))` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 45s · 1s · self · wind-up 1s |
| Ruinshelter `wh2_dlc15_unit_abilities_mimic_ruinshelter` | `excluded (auto: no effect text available (unsourceable))` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 90s · 60s · self |
| Sand Veil `wh2_dlc09_army_abilities_sand_veil` | `excluded (impossible: already rejected by user (tactical escape/stealth))` | ready | Whenever the engine allows (no readable condition): cast on an ally. | cd 90s · 89s · friend · ×3 uses · army |
| Sceptre of Stability `wh_main_item_abilities_sceptre_of_stability` | `implemented (in-melee self)` | ready | Whenever the engine allows (no readable condition): cast on an ally. | cd 60s · 22s · friend |
| Scroll of Destiny `wh3_main_item_abilities_scroll_of_destiny` | `implemented (in-melee self)` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 120s · 46s · self · ×1 uses |
| Scruten Clanstone `wh3_dlc29_army_abilities_scruten_clanstone` | `excluded (auto: army-bar ability (standing rule 10))` | ready | Whenever the engine allows (no readable condition): cast on the ground. | cd 120s · 48s · ground · ×3 uses · army |
| Shield of Chaqua `wh2_dlc12_unit_abilities_shield_of_chaqua` | `implemented (in-melee self)` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 90s · 25s · self · ×3 uses |
| Shield of the Old Ones `wh2_dlc13_final_battle_abilities_shield_of_the_old_ones` | `excluded (auto: army-bar ability (standing rule 10))` | ready | Whenever the engine allows (no readable condition): cast on the ground. | cd 90s · 180s · ground · army |
| Ships of the Line `wh3_dlc27_army_abilities_ships_of_the_line` | `excluded (auto: army-bar ability (standing rule 10))` | ready | Whenever the engine allows (no readable condition): cast on an ally. | cd 60s · 10s · friend/self · ×3 uses · wind-up 1s · army |
| Skitterleap `wh3_dlc29_spell_bound_skitterleap` | `excluded (impossible: already rejected by user (tactical escape/stealth))` | ready | Whenever the engine allows (no readable condition): cast on an ally. | cd 29s · 25s · friend/self · ×3 uses · wind-up 1s · bound |
| Skjalandir's Fall `wh3_dlc23_character_abilities_skjalandirs_fall` | `implemented (in-melee self)` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 120s · 39s · self |
| Skull of Rarkos `wh_dlc03_item_abilities_skull_of_rarkos` | `implemented (in-melee self)` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 120s · 34s · self · ×3 uses |
| Snowflake Pendant `wh3_main_item_abilities_snowflake_pendant` | `implemented (in-melee self)` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 90s · 25s · self |
| Speed of Lykos `wh2_dlc10_item_abilities_speed_of_lykos` | `excluded (impossible: already rejected by user (tactical escape/stealth))` | ready | Whenever the engine allows (no readable condition): cast on an ally. | cd 60s · 36s · friend · ×1 uses |
| Spell-Wrought Sceptre `wh3_dlc23_weapon_abilities_spell_wrought_sceptre` | `implemented (in-melee self)` | ready | Whenever the engine allows (no readable condition): cast on an ally. | cd 90s · 50s · friend |
| Staff of Nagash `wh2_dlc09_item_abilities_staff_of_nagash` | `implemented (in-melee self)` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 120s · 33s · self |
| Staff of Tomorrow `wh3_main_weapon_abilities_staff_of_tomorrow` | `implemented (in-melee self)` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 120s · 29s · self |
| Staff of Volans `wh_main_item_abilities_staff_of_volans` | `implemented (in-melee self)` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 120s · 30s · self |
| Staff of Wu Xing `wh3_main_item_abilities_staff_of_wu_xing` | `implemented (in-melee self)` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 120s · 30s · self · ×1 uses |
| Starwood Staff `wh2_main_item_abilities_starwood_staff` | `implemented (in-melee self)` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 90s · 23s · self · ×3 uses |
| Stave of Avelorn `wh2_dlc10_item_abilities_stave_of_avelorn` | `implemented (in-melee self)` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 60s · 40s · self · ×1 uses |
| Storm of Blades `wh_dlc05_unit_abilities_storm_of_blades` | `excluded (auto: no effect text available (unsourceable))` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 1s · -1s · self · wind-up 1s |
| Temptator `wh3_dlc20_lord_abilities_temptator` | `excluded (auto: no effect text available (unsourceable))` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 120s · 19s · self |
| Terrorgheist Skull `wh_dlc08_item_abilities_terrorgheist_skull` | `implemented (in-melee self)` | ready | Whenever the engine allows (no readable condition): cast on an ally. | cd 120s · 44s · friend |
| The Bane Shield `wh2_main_item_abilities_the_bane_shield` | `implemented (in-melee self)` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 0s · 44s · self · ×1 uses |
| The Chromatic Tome `wh3_main_item_abilities_the_chromatic_tome` | `implemented (in-melee self)` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 60s · 27s · self |
| The Crimson Blade `wh3_dlc29_item_abilities_crimson_blade` | `excluded (auto: no effect text available (unsourceable))` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 120s · 30s · self · item |
| The Gold Standard `wh3_dlc25_item_abilities_the_gold_standard` | `excluded (auto: no effect text available (unsourceable))` | ready | Whenever the engine allows (no readable condition): cast on an ally. | cd 90s · 13s · friend |
| The Golden Eye of Tzeentch `wh3_dlc24_item_abilities_the_golden_eye_of_tzeentch` | `implemented (in-melee self)` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 120s · 33s · self |
| The Graven Sceptre `wh3_dlc23_weapon_abilities_the_graven_sceptre` | `excluded (auto: no effect text available (unsourceable))` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 120s · 24s · self |
| The Guiding Eye `wh2_main_item_abilities_the_guiding_eye` | `implemented (in-melee self)` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 60s · 18s · self |
| The Liber Noctus `wh_dlc04_item_abilities_the_liber_noctus` | `implemented (in-melee self)` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 120s · 33s · self · ×2 uses |
| The Lion's Shield `wh_dlc07_lord_abilities_lions_shield` | `implemented (in-melee self)` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 90s · 22s · self |
| The Seerstaff of Saphery `wh2_main_spell_bound_the_seerstaff_of_saphery` | `implemented (in-melee self)` | ready | Whenever the engine allows (no readable condition): cast on an ally. | cd 60s · 22s · friend · ×4 uses · bound |
| Tricksy Traps `wh_dlc06_lord_abilities_tricksy_traps` | `excluded (impossible: already rejected by user (tactical escape/stealth))` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 120s · 32s · self |
| Unlimited Power! `wh2_dlc12_lord_abilities_unlimited_power` | `implemented (in-melee self)` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 90s · 26s · self |
| Wand of Jet `wh_main_item_abilities_wand_of_jet` | `implemented (in-melee self)` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 60s · 57s · self |
| War Supplies `wh3_dlc27_army_abilities_war_supplies` | `excluded (auto: army-bar ability (standing rule 10))` | ready | Whenever the engine allows (no readable condition): cast on an ally. | cd 60s · 10s · friend/self · ×3 uses · wind-up 1s · army |
| Warpstone Tokens `wh3_dlc29_item_abilities_warpstone_tokens` | `implemented (in-melee self)` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 120s · 26s · self · ×2 uses |
| Whirling Death `wh2_dlc16_unit_abilities_whirling_death` | `excluded (auto: no effect text available (unsourceable))` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 1s · -1s · self · wind-up 1s |
| Whispering Skull `wh3_dlc29_item_abilities_whispering_skull` | `implemented (in-melee self)` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 90s · 17s · self |
| Winds of Change `wh3_main_daemon_body_abilities_winds_of_change` | `implemented (in-melee self)` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 120s · 26s · self |
| Woven Mist `wh_dlc05_unit_abilities_woven_mist` | `implemented (in-melee self)` | ready | Whenever the engine allows (no readable condition): cast on self. | cd 1s · -1s · self · wind-up 1s |
| 'Effagee' of da Git `wh_dlc06_character_abilities_effagee_of_da_git` | `excluded (impossible: no enemy-unit read)` | target | While the unit has an enemy in its sights: fire at it. | cd 120s · 13s · enemy unit · ×2 uses |
| Aken-seth, the Staff of Pain `wh3_dlc29_weapon_abilities_aken_seth_the_staff_of_pain` | `implemented (in-melee self)` | target | While the unit has an enemy in its sights: fire at it. | cd 120s · 20s · self |
| Amber Bow `wh2_dlc13_weapon_abilities_amber_bow` | `excluded (impossible: no enemy-unit read)` | target | While the unit has an enemy in its sights: fire at it. | cd 120s · -1s · enemy unit · ×2 uses · wind-up 4.5s |
| Amulet of Pha-Stah `wh2_dlc09_item_abilities_amulet_of_phastah` | `implemented (enemy-targeted: enemy-ground area)` | enemy_ground | When an enemy unit within the 70% bound (70 m of 100 m) is in melee or under missile fire: `perform_special_ability_ground` places the area on the ENEMY's ground (fresh-handle route). | cd 120s · 22s · enemy ground · enemy-targeting mechanism (harness 97) |
| Ancestral Vengeance `wh3_dlc23_item_abilities_ancestral_vengeance` | `implemented (enemy-ground: closest FIGHTING enemy)` | enemy_ground_melee | The CLOSEST enemy within the ability's 70% bound (21 m of its 30 m target_intercept_range) that is FIGHTING (in melee): the summon is placed on THAT ENEMY's ground (perform_special_ability_ground, fresh caster + fresh enemy, hold, pre-cast re-check). | cd 120s · 10s · ground · ×2 uses · wind-up 5s · **round 102 (2026-10-17):** implemented on the Gate of Khorne trigger per the user's summon ruling (harness 102) |
| Ancestral Warriors `wh3_main_army_abilities_ancestral_warriors` | `excluded (auto: army-bar ability (standing rule 10))` | target | While the unit has an enemy in its sights: fire at it. | cd 120s · 10s · friend/self · ×1 uses · wind-up 5s · army |
| Ancestral Warriors `wh3_main_spell_bound_ancestral_warriors` | `implemented (enemy-ground: closest FIGHTING enemy)` | enemy_ground_melee | The CLOSEST enemy within the ability's 70% bound (35 m of its 50 m target_intercept_range) that is FIGHTING (in melee): the summon is placed on THAT ENEMY's ground (perform_special_ability_ground, fresh caster + fresh enemy, hold, pre-cast re-check). | cd 120s · 10s · friend/self · ×2 uses · wind-up 5s · bound · **round 102 (2026-10-17):** implemented on the Gate of Khorne trigger per the user's summon ruling (harness 102) |
| Ancient Chaos Frost Dragon Scale `wh_dlc08_item_abilities_ancient_frost_wyrm_scale` | `excluded (auto: explosive / breath attack)` | target | While the unit has an enemy in its sights: cast on the ground under the target. | cd 120s · 24s · enemy ground · wind-up 1s |
| Arrow of Aqshy `wh2_dlc13_lord_abilities_fire_arrow` | `excluded (impossible: no enemy-unit read)` | target | While the unit has an enemy in its sights: fire at it. | cd 90s · -1s · enemy unit · ×3 uses · wind-up 4.5s |
| Arrow of Kurnous `wh_dlc05_hero_abilities_arrow_of_kurnous` | `excluded (auto: explosive projectile)` | target | While the unit has an enemy in its sights: fire at it. | cd 90s · -1s · enemy unit · ×3 uses |
| Ashes & Dust `wh3_dlc20_cataclysm_bound_ashes_and_dust` | `excluded (auto: own-troop-damage AoE (friendly fire by design, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. | cd 120s · 11s · enemy ground · ×1 uses · wind-up 5s · bound · triage-family: Own-troop-damage AoE |
| Ashes & Dust `wh3_dlc27_cataclysm_bound_ashes_and_dust` | `excluded (auto: own-troop-damage AoE (friendly fire by design, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. | cd 120s · 11s · enemy ground · ×3 uses · wind-up 5s · bound · triage-family: Own-troop-damage AoE |
| Aura of Inertia `wh2_dlc13_lord_abilities_aura_of_inertia` | `implemented (in-melee self)` | target | While the unit has an enemy in its sights: fire at it. | cd 90s · 24s · self |
| Banner of Hellfire `wh3_main_banner_abilities_banner_of_hellfire` | `excluded (auto: no effect text available (unsourceable))` | target | While the unit has an enemy in its sights: fire at it. | cd 120s · 17s · self |
| Beast Pack `wh2_dlc16_lord_abilities_beast_pack` | `implemented (enemy-ground: closest FIGHTING enemy)` | enemy_ground_melee | The CLOSEST enemy within the ability's 70% bound (35 m of its 50 m target_intercept_range) that is FIGHTING (in melee): the summon is placed on THAT ENEMY's ground (perform_special_ability_ground, fresh caster + fresh enemy, hold, pre-cast re-check). | cd 120s · 1s · friend/self · ×1 uses · **round 102 (2026-10-17):** implemented on the Gate of Khorne trigger per the user's summon ruling (harness 102) |
| Beasts of Itzl `wh2_dlc13_army_abilities_beasts_of_itzl` | `excluded (auto: army-bar ability (standing rule 10))` | target | While the unit has an enemy in its sights: cast on the ground under the target. | cd 120s · 10s · enemy ground · ×3 uses · wind-up 5s · army |
| Beasts of Itzl `wh2_dlc13_army_abilities_beasts_of_itzl_upgraded` | `excluded (auto: army-bar ability (standing rule 10))` | target | While the unit has an enemy in its sights: cast on the ground under the target. | cd 90s · 10s · enemy ground · ×5 uses · wind-up 5s · army |
| Bellow of Endless Fury `wh3_main_lord_abilities_bellow_of_endless_fury` | `excluded (auto: explosive projectile)` | target | While the unit has an enemy in its sights: fire at it. | cd 60s · -1s · enemy unit · ×3 uses · wind-up 1.2s |
| Bellow of Fury `wh3_main_lord_abilities_bellow_of_fury` | `excluded (auto: explosive projectile)` | target | While the unit has an enemy in its sights: fire at it. | cd 60s · -1s · enemy unit · ×3 uses · wind-up 1s |
| Beyond the Realm `wh2_dlc11_character_abilities_beyond_the_realm` | `implemented (enemy-ground: closest FIGHTING enemy)` | enemy_ground_melee | The CLOSEST enemy within the ability's 70% bound (35 m of its 50 m target_intercept_range) that is FIGHTING (in melee): the summon is placed on THAT ENEMY's ground (perform_special_ability_ground, fresh caster + fresh enemy, hold, pre-cast re-check). | cd 120s · 3s · friend/self · ×2 uses · wind-up 3s · **round 102 (2026-10-17):** implemented on the Gate of Khorne trigger per the user's summon ruling (harness 102) |
| Big Boom `wh2_dlc13_character_abilities_big_boom` | `excluded (auto: explosive projectile)` | target | While the unit has an enemy in its sights: fire at it. | cd 120s · -1s · enemy unit · ×3 uses · wind-up 2.2s |
| Bilespurt `wh3_dlc29_hero_active_bilespurter` | `excluded (auto: explosive projectile)` | target | While the unit has an enemy in its sights: fire at it. | cd 60s · -1s · enemy unit · ×3 uses · wind-up 1.3s |
| Blacktoof's Conjuration `wh2_dlc15_item_abilities_blacktoofs_conjuration` | `implemented (enemy-ground: closest FIGHTING enemy)` | enemy_ground_melee | The CLOSEST enemy within the ability's 70% bound (35 m of its 50 m target_intercept_range) that is FIGHTING (in melee): the summon is placed on THAT ENEMY's ground (perform_special_ability_ground, fresh caster + fresh enemy, hold, pre-cast re-check). | cd 300s · 1s · friend/self · ×1 uses · **round 102 (2026-10-17):** implemented on the Gate of Khorne trigger per the user's summon ruling (harness 102) |
| Blast `wh2_dlc10_item_bound_blast` | `excluded (auto: explosive projectile)` | target | While the unit has an enemy in its sights: fire at it. | cd 60s · -1s · enemy unit · ×1 uses · bound |
| Blight of Terrors `wh2_dlc16_character_abilities_blight_of_terrors` | `implemented (in-melee self)` | target | While the unit has an enemy in its sights: fire at it. | cd 90s · 20s · self · ×3 uses |
| Blood & Fireborn `wh3_dlc23_lord_abilities_blood_and_fireborn` | `excluded (auto: army-bar ability (standing rule 10))` | target | While the unit has an enemy in its sights: fire at it. | cd 120s · 7s · friend/self · ×1 uses · army |
| Blood Omens `wh3_dlc29_unit_abilities_blood_omens` | `implemented (in-melee self)` | target | While the unit has an enemy in its sights: fire at it. | cd 90s · 26s · self · ×1 uses |
| Blood Statuette of Spite `wh2_main_item_abilities_blood_statuette_of_spite` | `excluded (impossible: no enemy-unit read)` | target | While the unit has an enemy in its sights: fire at it. | cd 60s · 14s · enemy unit · ×2 uses |
| Bloodstone `wh3_main_item_abilities_bloodstone` | `implemented (enemy-ground: closest FIGHTING enemy)` | enemy_ground_melee | The CLOSEST enemy within the ability's 70% bound (35 m of its 50 m target_intercept_range) that is FIGHTING (in melee): the summon is placed on THAT ENEMY's ground (perform_special_ability_ground, fresh caster + fresh enemy, hold, pre-cast re-check). | cd 120s · 10s · ground · ×1 uses · wind-up 5s · **round 102 (2026-10-17):** implemented on the Gate of Khorne trigger per the user's summon ruling (harness 102) |
| Bloody Onslaught `wh3_dlc26_character_abilities_bloody_onslaught` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (52 m of 75 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 90s · 38s · enemy unit · enemy-targeting mechanism (harness 97) |
| Bolt Storm `wh3_main_weapon_abilities_nuku_chos_crossbow` | `excluded (auto: explosive projectile)` | target | While the unit has an enemy in its sights: fire at it. | cd 90s · -1s · enemy unit · wind-up 1s |
| Bomb-Throw `wh2_dlc11_hero_abilities_bomb_throw` | `excluded (auto: explosive projectile)` | target | While the unit has an enemy in its sights: fire at it. | cd 60s · -1s · enemy unit · ×4 uses · wind-up 0.4s |
| Bow of the Seafarer `wh2_main_weapon_abilities_bow_of_the_seafarer` | `excluded (auto: explosive projectile)` | target | While the unit has an enemy in its sights: fire at it. | cd 90s · -1s · enemy unit · ×3 uses · wind-up 1s |
| Breath of the Hydra `wh2_dlc10_quest_abilities_fiery_head` | `excluded (not in wheel: boss-only unit)` | target | While the unit has an enemy in its sights: fire at it. |  cd 25s · 45s · self · wind-up 2s · **round 101 (2026-10-17):** boss-only - its ONLY grant path is `wh2_dlc10_def_mon_war_hydra_boss` (land_abil.tsv), a quest-battle boss variant; it never shipped in the mod. See §10.3. |
| Burning Wrath `wh3_dlc23_spell_bound_burning_wrath` | `excluded (impossible: no enemy-unit read)` | target | While the unit has an enemy in its sights: fire at it. | cd 30s · -1s · enemy unit · ×3 uses · wind-up 1s · bound |
| Burrow `wh3_dlc27_unit_abilities_dread_maw_underground` | `excluded (auto: summon)` | target | While the unit has an enemy in its sights: fire at it. | cd 20s · 3s · self · wind-up 4s |
| Cackle Fruit `wh2_dlc11_character_abilities_cackle_fruit` | `excluded (auto: explosive projectile)` | target | While the unit has an enemy in its sights: fire at it. | cd 90s · -1s · enemy unit · ×3 uses · wind-up 0.4s |
| Call of the Shadow Dancer `wh2_dlc10_lord_abilities_deadly_mislead` | `excluded (not in wheel: illusion summon)` | — | illusion (spawn_is_decoy; refused when engaged in melee) | cd 90s · 62s · ground · ×3 uses · **round 102 (2026-10-17):** excluded 2026-10-17 (round 102) - the engine refuses an illusion while its caster is engaged in melee, so a melee trigger can never fire it |
| Call of the Wild `wh3_dlc25_army_abilities_call_of_the_wild` | `excluded (auto: army-bar ability (standing rule 10))` | target | While the unit has an enemy in its sights: fire at it. | cd 120s · 1s · friend/self · ×1 uses · wind-up 5s · army |
| Call the Miners `wh3_dlc25_army_abilities_summon_miners` | `excluded (auto: army-bar ability (standing rule 10))` | target | While the unit has an enemy in its sights: cast on the ground under the target. | cd 45s · 1s · enemy ground · ×2 uses · wind-up 5s · army |
| Call to Ceithin-Har `wh2_dlc16_army_abilities_call_to_ceithin_har` | `excluded (auto: army-bar ability (standing rule 10))` | target | While the unit has an enemy in its sights: fire at it. | cd 120s · -1s · friend/self · ×1 uses · army |
| Call to Ceithin-Har `wh2_dlc16_lord_abilities_call_to_ceithin_har` | `implemented (enemy-ground: closest FIGHTING enemy)` | enemy_ground_melee | The CLOSEST enemy within the ability's 70% bound (35 m of its 50 m target_intercept_range) that is FIGHTING (in melee): the summon is placed on THAT ENEMY's ground (perform_special_ability_ground, fresh caster + fresh enemy, hold, pre-cast re-check). | cd 120s · -1s · friend/self · ×1 uses · **round 102 (2026-10-17):** implemented on the Gate of Khorne trigger per the user's summon ruling (harness 102) |
| Call to Gwindalor `wh2_dlc16_lord_abilities_call_to_gwindalor` | `implemented (enemy-ground: closest FIGHTING enemy)` | enemy_ground_melee | The CLOSEST enemy within the ability's 70% bound (35 m of its 50 m target_intercept_range) that is FIGHTING (in melee): the summon is placed on THAT ENEMY's ground (perform_special_ability_ground, fresh caster + fresh enemy, hold, pre-cast re-check). | cd 120s · -1s · friend/self · ×1 uses · **round 102 (2026-10-17):** implemented on the Gate of Khorne trigger per the user's summon ruling (harness 102) |
| Captain Roth's Moondial `wh2_dlc11_item_abilities_captain_roths_moondial` | `implemented (enemy-ground: closest FIGHTING enemy)` | enemy_ground_melee | The CLOSEST enemy within the ability's 70% bound (105 m of its 150 m target_intercept_range) that is FIGHTING (in melee): the summon is placed on THAT ENEMY's ground (perform_special_ability_ground, fresh caster + fresh enemy, hold, pre-cast re-check). | cd 120s · 3s · friend/self · ×2 uses · wind-up 3s · **round 102 (2026-10-17):** implemented on the Gate of Khorne trigger per the user's summon ruling (harness 102) |
| Chain Lightning `wh3_dlc27_spell_heavens_chain_lightning_bound` | `excluded (impossible: no enemy-unit read)` | target | While the unit has an enemy in its sights: fire at it. | cd 50s · 5s · enemy unit · ×2 uses · wind-up 5s · bound |
| Chain Lightning `wh3_dlc27_spell_heavens_chain_lightning_bound_unit` | `excluded (impossible: no enemy-unit read)` | target | While the unit has an enemy in its sights: fire at it. | cd 60s · 5s · enemy unit · ×1 uses · wind-up 5s · bound |
| Chalice of Dark Rain `wh_dlc03_item_abilities_chalice_of_dark_rain` | `implemented (enemy-targeted: enemy-ground area)` | enemy_ground | When an enemy unit within the 70% bound (140 m of 200 m) is in melee or under missile fire: `perform_special_ability_ground` places the area on the ENEMY's ground (fresh-handle route). | cd 90s · 89s · enemy ground · enemy-targeting mechanism (harness 97) |
| Children of the Forest `wh3_dlc25_character_abilities_children_of_the_forest` | `implemented (enemy-ground: closest FIGHTING enemy)` | enemy_ground_melee | The CLOSEST enemy within the ability's 70% bound (35 m of its 50 m target_intercept_range) that is FIGHTING (in melee): the summon is placed on THAT ENEMY's ground (perform_special_ability_ground, fresh caster + fresh enemy, hold, pre-cast re-check). | cd 90s · 1s · friend/self · ×5 uses · **round 102 (2026-10-17):** implemented on the Gate of Khorne trigger per the user's summon ruling (harness 102) |
| Cinderblast Cluster Bomb `wh3_dlc25_lord_abilities_cinderblast_cluster_bomb` | `excluded (auto: explosive projectile)` | target | While the unit has an enemy in its sights: fire at it. | cd 120s · -1s · enemy unit · ×3 uses · wind-up 3s |
| Cinderblast Shell `wh2_dlc17_hero_abilities_cinderblast_shell` | `excluded (auto: explosive projectile)` | target | While the unit has an enemy in its sights: fire at it. | cd 90s · -1s · enemy unit · ×3 uses · wind-up 1s |
| Clanrats Below `wh3_dlc29_endgame_crisis_the_vermintide_the_menace_below_hidden` | `excluded (auto: army-bar ability (standing rule 10))` | target | While the unit has an enemy in its sights: cast on the ground under the target. | cd 30s · 1s · enemy ground · ×1 uses · army |
| Copious Vomit `wh_dlc08_lord_abilities_copious_vomit` | `excluded (auto: explosive projectile)` | target | While the unit has an enemy in its sights: fire at it. | cd 60s · -1s · enemy unit · ×3 uses |
| Coruscating Blast `wh3_dlc25_unit_abilities_coruscating_blast` | `excluded (auto: explosive projectile)` | target | While the unit has an enemy in its sights: fire at it. | cd 120s · -1s · enemy unit · ×3 uses · wind-up 1.3s |
| Cracklebomb `wh2_dlc14_character_abilities_cracklebomb` | `excluded (auto: explosive projectile)` | target | While the unit has an enemy in its sights: fire at it. | cd 90s · -1s · enemy unit · ×3 uses · wind-up 0.8s |
| Crippling Throw `wh3_main_character_abilities_crippling_throw` | `excluded (auto: explosive projectile)` | target | While the unit has an enemy in its sights: fire at it. | cd 90s · -1s · enemy unit · ×3 uses · wind-up 3s |
| Cube of Darkness `wh2_main_item_abilities_cube_of_darkness` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (70 m of 100 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 60s · 18s · enemy unit · enemy-targeting mechanism (harness 97) |
| Curse of Khsar `wh2_dlc09_character_abilities_curse_of_khsar` | `implemented (enemy-targeted: enemy-ground area)` | enemy_ground | When an enemy unit within the 70% bound (24 m of 35 m) is in melee or under missile fire: `perform_special_ability_ground` places the area on the ENEMY's ground (fresh-handle route). | cd 0s · 25s · enemy ground · ×1 uses · enemy-targeting mechanism (harness 97) |
| Curse of the Slug `wh3_main_army_abilities_curse_of_the_slug` | `excluded (auto: army-bar ability (standing rule 10))` | target | While the unit has an enemy in its sights: fire at it. | cd 60s · 20s · enemy unit · army |
| Cut da Chainz `wh3_dlc26_army_abilities_cut_da_chains` | `excluded (auto: army-bar ability (standing rule 10))` | target | While the unit has an enemy in its sights: fire at it. | cd 120s · 1s · friend/self · ×3 uses · army |
| Daemonic Possession `wh3_main_lord_abilities_daemonic_possession` | `excluded (impossible: no enemy-unit read)` | target | While the unit has an enemy in its sights: fire at it. | cd 90s · 26s · enemy unit · ×2 uses · lord |
| Damned Pistol `wh3_main_weapon_abilities_godkiller_pistol` | `excluded (impossible: no enemy-unit read)` | target | While the unit has an enemy in its sights: fire at it. | cd 120s · -1s · enemy unit · ×2 uses · wind-up 2.3s |
| Dark Fire of Chaos `wh2_main_unit_abilities_dark_fire_of_chaos` | `excluded (auto: explosive projectile)` | target | While the unit has an enemy in its sights: fire at it. | cd 60s · -1s · enemy unit · ×3 uses · wind-up 1.1s |
| Dark Mace `wh3_dlc23_weapon_abilities_dark_mace` | `excluded (auto: no effect text available (unsourceable))` | target | While the unit has an enemy in its sights: fire at it. | cd 90s · 30s · self |
| Darkened Mist `wh3_dlc23_item_abilities_darkened_mist` | `excluded (impossible: no enemy-unit read)` | target | While the unit has an enemy in its sights: fire at it. | cd 120s · 20s · enemy unit · ×3 uses · wind-up 3s |
| Dart of Doom `wh2_dlc16_item_abilities_dart_of_doom` | `excluded (impossible: no enemy-unit read)` | target | While the unit has an enemy in its sights: fire at it. | cd 120s · -1s · enemy unit · ×3 uses · wind-up 1s |
| Dead Eye `wh3_dlc26_character_abilities_dead_eye` | `excluded (impossible: no enemy-unit read)` | target | While the unit has an enemy in its sights: fire at it. | cd 120s · -1s · enemy unit · wind-up 5s |
| Death from Above `wh2_dlc09_unit_abilities_death_from_above` | `excluded (auto: explosive / breath attack)` | target | While the unit has an enemy in its sights: fire at it. | cd 0.1s · 1s · self · ×1 uses |
| Death Shriek `wh2_main_unit_abilities_death_shriek` | `excluded (auto: explosive projectile)` | target | While the unit has an enemy in its sights: fire at it. | cd 60s · -1s · enemy unit · ×3 uses · wind-up 0.6s |
| Death's Timekeeper `wh3_dlc25_item_abilities_deaths_timekeeper` | `excluded (impossible: no enemy-unit read)` | target | While the unit has an enemy in its sights: fire at it. | cd 120s · 10s · enemy unit · ×2 uses |
| Deceiving Shadows `wh3_dlc24_lord_item_deceiving_shadows` | `excluded (not in wheel: illusion summon)` | — | illusion (spawn_is_decoy; refused when engaged in melee) | cd 120s · 20s · ground · ×3 uses · **round 102 (2026-10-17):** excluded 2026-10-17 (round 102) - the engine refuses an illusion while its caster is engaged in melee, so a melee trigger can never fire it |
| Deep Tunneling `wh3_dlc27_unit_abilities_burrow` | `excluded (auto: vortex)` | target | While the unit has an enemy in its sights: cast at the target's position (placement policy needed). | cd 60s · -1s · ground · wind-up 2s |
| Descent Into Dissolution `wh3_dlc27_army_abilities_eternal_dance_tempo_3_jesters_laughter` | `excluded (auto: own-troop-damage AoE (friendly fire by design, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast at the target's position (placement policy needed). | cd 120s · 48s · ground · ×2 uses · wind-up 3s · army · triage-family: Own-troop-damage AoE |
| Dire Spirit Bear `wh3_dlc24_lord_abilities_spirit_bear_upgrade` | `excluded (impossible: no enemy-unit read)` | target | While the unit has an enemy in its sights: fire at it. | cd 120s · -1s · enemy unit · ×3 uses · wind-up 4s |
| Dismember `wh3_main_prisoners_dismember` | `excluded (auto: army-bar ability (standing rule 10))` | target | While the unit has an enemy in its sights: fire at it. | cd 60s · 14s · enemy unit · army |
| Dissolving Bone `wh3_dlc27_qb_unit_abilities_dissolving_bone` | `excluded (not in wheel: boss-only unit)` | target | While the unit has an enemy in its sights: fire at it. |  cd 60s · 2s · enemy unit · **round 101 (2026-10-17):** boss-only - its ONLY grant path is `wh3_dlc27_tmb_mon_carrion_boss` (land_abil.tsv), a quest-battle boss variant; it never shipped in the mod. See §10.3. |
| Doom & Darkness `wh3_dlc25_spell_Bound_doom_and_darkness_gunnery_school` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (140 m of 200 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 90s · 36s · enemy unit · ×2 uses · bound · enemy-targeting mechanism (harness 97) |
| Doom & Darkness `wh3_dlc27_spell_bound_runecaller_death_doom_and_darkness` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (140 m of 200 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 90s · 36s · enemy unit · ×3 uses · wind-up 1s · bound · enemy-targeting mechanism (harness 97) |
| Doom & Darkness `wh_dlc08_spell_bound_death_doom_and_darkness` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (140 m of 200 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 90s · 36s · enemy unit · ×3 uses · bound · enemy-targeting mechanism (harness 97) |
| Doomrocket `wh2_main_hero_abilities_doomrocket` | `excluded (auto: explosive projectile)` | target | While the unit has an enemy in its sights: fire at it. | cd 90s · -1s · enemy unit · ×1 uses · wind-up 1s |
| Doppelgang `wh2_dlc14_unit_abilities_doppelgang` | `excluded (not in wheel: illusion summon)` | — | illusion (spawn_is_decoy; refused when engaged in melee) | cd 90s · 60s · friend/self · ×2 uses · **round 102 (2026-10-17):** excluded 2026-10-17 (round 102) - the engine refuses an illusion while its caster is engaged in melee, so a melee trigger can never fire it |
| Dreaming Cloak I `wh2_dlc16_item_abilities_dreaming_cloak_i` | `implemented (enemy-ground: closest FIGHTING enemy)` | enemy_ground_melee | The CLOSEST enemy within the ability's 70% bound (35 m of its 50 m target_intercept_range) that is FIGHTING (in melee): the summon is placed on THAT ENEMY's ground (perform_special_ability_ground, fresh caster + fresh enemy, hold, pre-cast re-check). | cd 120s · 1s · friend/self · ×1 uses · wind-up 1s · **round 102 (2026-10-17):** implemented on the Gate of Khorne trigger per the user's summon ruling (harness 102) |
| Dreaming Cloak II `wh2_dlc16_item_abilities_dreaming_cloak_ii` | `implemented (enemy-ground: closest FIGHTING enemy)` | enemy_ground_melee | The CLOSEST enemy within the ability's 70% bound (35 m of its 50 m target_intercept_range) that is FIGHTING (in melee): the summon is placed on THAT ENEMY's ground (perform_special_ability_ground, fresh caster + fresh enemy, hold, pre-cast re-check). | cd 120s · 1s · friend/self · ×1 uses · wind-up 1s · **round 102 (2026-10-17):** implemented on the Gate of Khorne trigger per the user's summon ruling (harness 102) |
| Dreaming Cloak III `wh2_dlc16_item_abilities_dreaming_cloak_iii` | `implemented (enemy-ground: closest FIGHTING enemy)` | enemy_ground_melee | The CLOSEST enemy within the ability's 70% bound (35 m of its 50 m target_intercept_range) that is FIGHTING (in melee): the summon is placed on THAT ENEMY's ground (perform_special_ability_ground, fresh caster + fresh enemy, hold, pre-cast re-check). | cd 120s · 1s · friend/self · ×1 uses · wind-up 1s · **round 102 (2026-10-17):** implemented on the Gate of Khorne trigger per the user's summon ruling (harness 102) |
| Drop Rocks `wh2_dlc12_unit_abilities_drop_rocks_character` | `excluded (auto: explosive / breath attack)` | target | While the unit has an enemy in its sights: fire at it. | cd 5s · -1s · self · ×1 uses |
| Drop Rocks `wh2_main_unit_abilities_drop_rocks` | `excluded (auto: explosive / breath attack)` | target | While the unit has an enemy in its sights: fire at it. | cd 5s · -1s · self · ×1 uses |
| Drop Rocks of Chotec `wh2_dlc12_unit_abilities_drop_rocks_of_chotec` | `excluded (auto: explosive / breath attack)` | target | While the unit has an enemy in its sights: fire at it. | cd 5s · -1s · self · ×1 uses |
| Drop Rocks of Sundering `wh2_dlc12_unit_abilities_drop_rocks_of_sundering` | `excluded (auto: explosive / breath attack)` | target | While the unit has an enemy in its sights: fire at it. | cd 5s · -1s · self · ×1 uses |
| Drop Sphere of Tepok `wh2_dlc12_lord_abilities_drop_sphere_of_tepok` | `excluded (auto: explosive / breath attack)` | target | While the unit has an enemy in its sights: fire at it. | cd 5s · -1s · self · ×1 uses |
| Drop Sphere of Tepok Upgraded `wh2_dlc12_lord_abilities_drop_sphere_of_tepok_upgraded` | `excluded (auto: explosive / breath attack)` | target | While the unit has an enemy in its sights: fire at it. | cd 5s · -1s · self · ×2 uses |
| Dweomer Leach Orb `wh3_dlc23_item_abilities_dweomer_leach_orb` | `excluded (impossible: no enemy-unit read)` | target | While the unit has an enemy in its sights: fire at it. | cd 90s · 22s · enemy unit |
| Eagle Quiver `wh2_dlc16_item_abilities_eagle_quiver` | `excluded (impossible: no enemy-unit read)` | target | While the unit has an enemy in its sights: fire at it. | cd 120s · -1s · enemy unit · ×2 uses |
| Eagle Sanctuary `wh2_main_army_abilities_eagle_sanctuary` | `excluded (auto: army-bar ability (standing rule 10))` | target | While the unit has an enemy in its sights: fire at it. | cd 120s · 1s · friend/self · ×3 uses · wind-up 5s · army |
| Elemental Breath `wh3_main_unit_abilities_elemental_breath` | `excluded (auto: explosive projectile)` | target | While the unit has an enemy in its sights: fire at it. | cd 60s · -1s · enemy unit · ×3 uses · wind-up 2.7s |
| Emberstorm `wh2_dlc15_unit_abilities_emberstorm` | `excluded (auto: explosive / breath attack)` | target | While the unit has an enemy in its sights: fire at it. | cd 90s · 11.5s · self · ×3 uses · wind-up 1.5s |
| Emergency Vent `wh2_dlc13_unit_abilities_emergency_vent` | `excluded (auto: vortex)` | target | While the unit has an enemy in its sights: fire at it. | cd 60s · 12s · self |
| Engineer's Gyrocopter Bomb `wh3_dlc25_army_abilities_gyrocopter_bomb` | `excluded (auto: army-bar ability (standing rule 10))` | target | While the unit has an enemy in its sights: fire at it. | cd 0.1s · 0.1s · self · army |
| Entangle `wh2_dlc10_character_abilities_entangle` | `implemented (enemy-targeted: enemy-ground area)` | enemy_ground | When an enemy unit within the 70% bound (10 m of 15 m) is in melee or under missile fire: `perform_special_ability_ground` places the area on the ENEMY's ground (fresh-handle route). | cd 120s · 15s · enemy ground · ×2 uses · enemy-targeting mechanism (harness 97) |
| Eshin Clanstone `wh2_main_army_abilities_eshin_clanstone` | `excluded (auto: own-troop-damage AoE (friendly fire by design, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast at the target's position (placement policy needed). | cd 120s · 22s · ground · ×3 uses · army · triage-family: Own-troop-damage AoE |
| Eternal Gaze `wh3_dlc29_lord_abilities_gaze_of_usirian` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (70 m of 100 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 90s · 15s · enemy unit · wind-up 3s · enemy-targeting mechanism (harness 97) |
| Ethrac's Brazier `wh3_dlc29_item_active_ethracs_brazier` | `excluded (impossible: no enemy-unit read)` | target | While the unit has an enemy in its sights: fire at it. | cd 120s · 14s · enemy unit · ×1 uses · wind-up 3s |
| Executioner `wh2_dlc13_lord_abilities_executioner` | `excluded (impossible: no enemy-unit read)` | target | While the unit has an enemy in its sights: fire at it. | cd 90s · -1s · enemy unit · ×3 uses · wind-up 5s |
| Experimental Explosive `wh3_dlc25_weapon_abilities_experimental_explosive` | `excluded (auto: explosive projectile)` | target | While the unit has an enemy in its sights: fire at it. | cd 120s · -1s · enemy unit · ×2 uses · wind-up 0.8s |
| Eye of Rejuvenation `wh2_dlc10_quest_abilities_regenerating_head` | `excluded (not in wheel: boss-only unit)` | target | While the unit has an enemy in its sights: fire at it. |  cd 15s · 25s · self · wind-up 2s · **round 101 (2026-10-17):** boss-only - its ONLY grant path is `wh2_dlc10_def_mon_war_hydra_boss` (land_abil.tsv), a quest-battle boss variant; it never shipped in the mod. See §10.3. |
| Fear of Aramar `wh2_dlc10_item_abilities_fear_of_aramar` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (140 m of 200 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 120s · 47s · enemy unit · ×1 uses · enemy-targeting mechanism (harness 97) |
| Fearsome Roar `wh3_dlc24_unit_abilities_fearsome_roar` | `implemented (in-melee self)` | target | While the unit has an enemy in its sights: fire at it. | cd 90s · 25s · self |
| Feaster of Souls `wh3_dlc29_mount_abilities_feaster_of_souls` | `excluded (auto: vortex)` | target | While the unit has an enemy in its sights: fire at it. | cd 120s · 5s · self · ×3 uses · wind-up 1s |
| Feral Cold Ones `wh2_main_army_abilities_feral_cold_ones` | `excluded (auto: army-bar ability (standing rule 10))` | target | While the unit has an enemy in its sights: cast on the ground under the target. | cd 120s · 1s · enemy ground · ×3 uses · wind-up 5s · army |
| Feral Cold Ones `wh2_main_army_abilities_feral_cold_ones_qb_scripted` | `excluded (auto: army-bar ability (standing rule 10))` | target | While the unit has an enemy in its sights: cast on the ground under the target. | cd 80s · 1s · enemy ground · ×3 uses · wind-up 5s · army |
| Fiery Breath `wh2_main_unit_abilities_fiery_breath` | `excluded (auto: explosive projectile)` | target | While the unit has an enemy in its sights: fire at it. | cd 60s · -1s · enemy unit · ×3 uses · wind-up 1s |
| Fire Bombs `wh3_dlc25_unit_abilities_gyrobomber_fire_bomb` | `excluded (auto: explosive / breath attack)` | target | While the unit has an enemy in its sights: fire at it. | cd 3s · 1s · self · ×3 uses |
| Fire Bombs `wh3_dlc25_unit_abilities_thunderbarge_fire_bomb` | `excluded (auto: explosive / breath attack)` | target | While the unit has an enemy in its sights: fire at it. | cd 3s · 1s · self · ×3 uses |
| Fire Breath `wh3_main_character_abilities_fire_breath` | `excluded (auto: explosive projectile)` | target | While the unit has an enemy in its sights: fire at it. | cd 60s · -1s · enemy unit · ×3 uses · wind-up 1.9s |
| Fireball `wh_main_spell_bound_fireball` | `excluded (impossible: no enemy-unit read)` | target | While the unit has an enemy in its sights: fire at it. | cd 60s · -1s · enemy unit · ×4 uses · bound |
| Fireball Upgraded `wh3_dlc27_spell_bound_fireball_upgraded` | `excluded (impossible: no enemy-unit read)` | target | While the unit has an enemy in its sights: fire at it. | cd 60s · -1s · enemy unit · ×6 uses · bound |
| Flaming Breath `wh3_dlc23_unit_abilities_flaming_breath` | `excluded (auto: explosive projectile)` | target | While the unit has an enemy in its sights: fire at it. | cd 90s · -1s · enemy unit · ×3 uses · wind-up 1s |
| Flaming Breath `wh3_dlc27_unit_abilities_flaming_breath` | `excluded (auto: explosive projectile)` | target | While the unit has an enemy in its sights: fire at it. | cd 90s · -1s · enemy unit · ×3 uses · wind-up 1s |
| Flock of Doom `wh3_dlc27_spell_bound_runecaller_flock_of_doom` | `excluded (auto: own-troop-damage AoE (friendly fire by design, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. | cd 60s · 6s · enemy ground · ×3 uses · wind-up 1s · bound · triage-family: Own-troop-damage AoE |
| Flock of Doom `wh3_main_spell_bound_flock_of_doom` | `excluded (auto: own-troop-damage AoE (friendly fire by design, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. | cd 60s · 6s · enemy ground · ×2 uses · bound · triage-family: Own-troop-damage AoE |
| Flock of Doom `wh_dlc08_spell_bound_flock_of_doom` | `excluded (auto: own-troop-damage AoE (friendly fire by design, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. | cd 60s · 6s · enemy ground · ×4 uses · bound · triage-family: Own-troop-damage AoE |
| Focused Shot `wh2_dlc13_lord_abilities_kill_shot` | `excluded (impossible: no enemy-unit read)` | target | While the unit has an enemy in its sights: fire at it. | cd 120s · -1s · enemy unit · ×2 uses · wind-up 5s |
| Formless Horror `wh3_dlc24_lord_abilities_formless_horror_changeling` | `excluded (impossible: no transform/shapechange support)` | target | While the unit has an enemy in its sights: fire at it. | cd 60s · 5s · self · wind-up 5s |
| Formless Horror `wh3_dlc24_lord_abilities_formless_horror_quest_battle_changeling_form` | `excluded (impossible: no transform/shapechange support)` | target | While the unit has an enemy in its sights: fire at it. | cd 60s · 5s · self · wind-up 5s |
| Frost Breath `wh2_dlc10_unit_abilities_frost_breath` | `excluded (auto: explosive projectile)` | target | While the unit has an enemy in its sights: fire at it. | cd 60s · -1s · enemy unit · ×3 uses · wind-up 1s |
| Frost Breath `wh2_dlc10_unit_abilities_frost_wyrm_breath` | `excluded (auto: explosive projectile)` | target | While the unit has an enemy in its sights: fire at it. | cd 60s · -1s · enemy unit · ×3 uses · wind-up 1.1s |
| Gate of Chaos `wh3_main_daemon_arms_abilities_gate_of_chaos` | `implemented (enemy-ground: closest FIGHTING enemy)` | enemy_ground_melee | The CLOSEST enemy within the ability's 70% bound (35 m of its 50 m target_intercept_range) that is FIGHTING (in melee): the summon is placed on THAT ENEMY's ground (perform_special_ability_ground, fresh caster + fresh enemy, hold, pre-cast re-check). | cd 120s · 10s · ground · ×2 uses · wind-up 5s · **round 102 (2026-10-17):** implemented on the Gate of Khorne trigger per the user's summon ruling (harness 102) |
| Gate of Chaos Upgraded `wh3_main_daemon_arms_abilities_gate_of_chaos_upgraded` | `implemented (enemy-ground: closest FIGHTING enemy)` | enemy_ground_melee | The CLOSEST enemy within the ability's 70% bound (35 m of its 50 m target_intercept_range) that is FIGHTING (in melee): the summon is placed on THAT ENEMY's ground (perform_special_ability_ground, fresh caster + fresh enemy, hold, pre-cast re-check). | cd 120s · 10s · ground · ×2 uses · wind-up 5s · **round 102 (2026-10-17):** implemented on the Gate of Khorne trigger per the user's summon ruling (harness 102) |
| Gate of Tzeentch `wh3_main_character_abilities_gate_of_tzeentch` | `implemented (enemy-ground: closest FIGHTING enemy)` | enemy_ground_melee | The CLOSEST enemy within the ability's 70% bound (35 m of its 50 m target_intercept_range) that is FIGHTING (in melee): the summon is placed on THAT ENEMY's ground (perform_special_ability_ground, fresh caster + fresh enemy, hold, pre-cast re-check). | cd 120s · 10s · friend/self · ×1 uses · wind-up 5s · **round 102 (2026-10-17):** implemented on the Gate of Khorne trigger per the user's summon ruling (harness 102) |
| Gaze of Nagash `wh2_dlc15_spell_bound_gaze_of_nagash` | `excluded (impossible: no enemy-unit read)` | target | While the unit has an enemy in its sights: fire at it. | cd 90s · -1s · enemy unit · ×3 uses · wind-up 3s · bound |
| Geomantic Nexus `wh2_main_army_abilities_geomantic_nexus` | `excluded (auto: army-bar ability (standing rule 10))` | target | While the unit has an enemy in its sights: fire at it. | cd 90s · 1s · friend/self · ×2 uses · wind-up 3s · army |
| Get 'Em! `wh3_dlc25_character_abilities_get_em` | `implemented (enemy-targeted: enemy-ground area)` | enemy_ground | When an enemy unit within the 70% bound (24 m of 35 m) is in melee or under missile fire: `perform_special_ability_ground` places the area on the ENEMY's ground (fresh-handle route). | cd 90s · 11s · enemy ground · enemy-targeting mechanism (harness 97) |
| Get Tha Gitz! `wh3_dlc23_hero_abilities_get_tha_gitz!` | `implemented (enemy-ground: closest FIGHTING enemy)` | enemy_ground_melee | The CLOSEST enemy within the ability's 70% bound (63 m of its 90 m target_intercept_range) that is FIGHTING (in melee): the summon is placed on THAT ENEMY's ground (perform_special_ability_ground, fresh caster + fresh enemy, hold, pre-cast re-check). | cd 120s · 5s · enemy ground · ×3 uses · wind-up 3s · **round 102 (2026-10-17):** implemented on the Gate of Khorne trigger per the user's summon ruling (harness 102) |
| Ghostly Howl `wh3_dlc29_hero_active_ghostly_howl` | `excluded (auto: no effect text available (unsourceable))` | target | While the unit has an enemy in its sights: fire at it. | cd 90s · 8s · enemy unit · wind-up 3s |
| Ghosts of the Past `wh2_dlc11_character_abilities_ghosts_of_the_past_0` | `implemented (enemy-ground: closest FIGHTING enemy)` | enemy_ground_melee | The CLOSEST enemy within the ability's 70% bound (35 m of its 50 m target_intercept_range) that is FIGHTING (in melee): the summon is placed on THAT ENEMY's ground (perform_special_ability_ground, fresh caster + fresh enemy, hold, pre-cast re-check). | cd 120s · 1s · friend/self · ×1 uses · wind-up 3s · **round 102 (2026-10-17):** implemented on the Gate of Khorne trigger per the user's summon ruling (harness 102) |
| Ghosts of the Past `wh2_dlc11_character_abilities_ghosts_of_the_past_1` | `implemented (enemy-ground: closest FIGHTING enemy)` | enemy_ground_melee | The CLOSEST enemy within the ability's 70% bound (35 m of its 50 m target_intercept_range) that is FIGHTING (in melee): the summon is placed on THAT ENEMY's ground (perform_special_ability_ground, fresh caster + fresh enemy, hold, pre-cast re-check). | cd 120s · 1s · friend/self · ×2 uses · wind-up 3s · **round 102 (2026-10-17):** implemented on the Gate of Khorne trigger per the user's summon ruling (harness 102) |
| Ghosts of the Past `wh2_dlc11_character_abilities_ghosts_of_the_past_2` | `implemented (enemy-ground: closest FIGHTING enemy)` | enemy_ground_melee | The CLOSEST enemy within the ability's 70% bound (35 m of its 50 m target_intercept_range) that is FIGHTING (in melee): the summon is placed on THAT ENEMY's ground (perform_special_ability_ground, fresh caster + fresh enemy, hold, pre-cast re-check). | cd 120s · 1s · friend/self · ×2 uses · wind-up 3s · **round 102 (2026-10-17):** implemented on the Gate of Khorne trigger per the user's summon ruling (harness 102) |
| Goggly Glare `wh2_dlc15_character_abilities_goggly_glare` | `excluded (impossible: no enemy-unit read)` | target | While the unit has an enemy in its sights: fire at it. | cd 60s · -1s · enemy unit · ×3 uses · wind-up 1s |
| Gordinar's Dragon Breath `wh2_dlc15_unit_abilities_sun_dragon_breath_imrik` | `excluded (auto: explosive projectile)` | target | While the unit has an enemy in its sights: fire at it. | cd 60s · -1s · enemy unit · ×3 uses · wind-up 1.3s |
| Gorger Onslaught `wh3_main_lord_abilities_gorger_onslaught` | `implemented (enemy-ground: closest FIGHTING enemy)` | enemy_ground_melee | The CLOSEST enemy within the ability's 70% bound (35 m of its 50 m target_intercept_range) that is FIGHTING (in melee): the summon is placed on THAT ENEMY's ground (perform_special_ability_ground, fresh caster + fresh enemy, hold, pre-cast re-check). | cd 60s · 1s · enemy ground · ×1 uses · wind-up 1s · **round 102 (2026-10-17):** implemented on the Gate of Khorne trigger per the user's summon ruling (harness 102) |
| Gorger Onslaught Upgraded `wh3_dlc26_lord_abilities_gorger_onslaught_upgraded` | `implemented (enemy-ground: closest FIGHTING enemy)` | enemy_ground_melee | The CLOSEST enemy within the ability's 70% bound (70 m of its 100 m target_intercept_range) that is FIGHTING (in melee): the summon is placed on THAT ENEMY's ground (perform_special_ability_ground, fresh caster + fresh enemy, hold, pre-cast re-check). | cd 90s · 1s · enemy ground · ×3 uses · wind-up 1s · **round 102 (2026-10-17):** implemented on the Gate of Khorne trigger per the user's summon ruling (harness 102) |
| Guardian Call `wh3_main_character_abilities_guardian_call` | `implemented (enemy-ground: closest FIGHTING enemy)` | enemy_ground_melee | The CLOSEST enemy within the ability's 70% bound (35 m of its 50 m target_intercept_range) that is FIGHTING (in melee): the summon is placed on THAT ENEMY's ground (perform_special_ability_ground, fresh caster + fresh enemy, hold, pre-cast re-check). | cd 0s · 1s · enemy ground · ×1 uses · wind-up 3s · **round 102 (2026-10-17):** implemented on the Gate of Khorne trigger per the user's summon ruling (harness 102) |
| Guardian Call II `wh3_main_character_abilities_guardian_call_ii` | `implemented (enemy-ground: closest FIGHTING enemy)` | enemy_ground_melee | The CLOSEST enemy within the ability's 70% bound (35 m of its 50 m target_intercept_range) that is FIGHTING (in melee): the summon is placed on THAT ENEMY's ground (perform_special_ability_ground, fresh caster + fresh enemy, hold, pre-cast re-check). | cd 0s · 1s · enemy ground · ×1 uses · wind-up 3s · **round 102 (2026-10-17):** implemented on the Gate of Khorne trigger per the user's summon ruling (harness 102) |
| Guardian Call III `wh3_main_character_abilities_guardian_call_iii` | `implemented (enemy-ground: closest FIGHTING enemy)` | enemy_ground_melee | The CLOSEST enemy within the ability's 70% bound (35 m of its 50 m target_intercept_range) that is FIGHTING (in melee): the summon is placed on THAT ENEMY's ground (perform_special_ability_ground, fresh caster + fresh enemy, hold, pre-cast re-check). | cd 0s · 1s · enemy ground · ×1 uses · wind-up 3s · **round 102 (2026-10-17):** implemented on the Gate of Khorne trigger per the user's summon ruling (harness 102) |
| Guardian of the Forest `wh3_dlc25_character_abilities_guardian_of_the_forest` | `implemented (enemy-ground: closest FIGHTING enemy)` | enemy_ground_melee | The CLOSEST enemy within the ability's 70% bound (35 m of its 50 m target_intercept_range) that is FIGHTING (in melee): the summon is placed on THAT ENEMY's ground (perform_special_ability_ground, fresh caster + fresh enemy, hold, pre-cast re-check). | cd 120s · 1s · friend/self · ×1 uses · **round 102 (2026-10-17):** implemented on the Gate of Khorne trigger per the user's summon ruling (harness 102) |
| Gust of the Grave `wh3_dlc29_unit_abilities_lesser_tomb_swarm` | `excluded (auto: own-troop-damage AoE (friendly fire by design, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast at the target's position (placement policy needed). | cd 90s · 18s · ground · ×1 uses · wind-up 5s · army · triage-family: Own-troop-damage AoE |
| Guttural Roar `wh3_dlc27_qb_unit_abilities_guttural_roar` | `excluded (not in wheel: boss-only unit)` | target | — | While the unit has an enemy in its sights: fire at it. · **round 101 (2026-10-17):** EXCLUDED - its ONLY grant path is `wh3_dlc27_cth_mon_celestial_lion_boss` (land_abil.tsv), a quest-battle boss variant; REMOVED from the mod (it was implemented before this round) |
| Gyrobomber Bomb `wh_main_unit_abilities_gyrobomber_bomb` | `excluded (auto: explosive / breath attack)` | target | While the unit has an enemy in its sights: fire at it. | cd 0.1s · 0.1s · self · ×11 uses |
| Gyrocopter Bomb `wh_main_unit_abilities_gyrocopter_bomb` | `excluded (auto: explosive / breath attack)` | target | While the unit has an enemy in its sights: fire at it. | cd 0.1s · 0.1s · self · ×2 uses |
| Gyrocopter Bomb (Trollhammer) `wh3_dlc25_unit_abilities_gyrocopter_bomb_anti_large` | `excluded (auto: explosive / breath attack)` | target | While the unit has an enemy in its sights: fire at it. | cd 0.1s · 0.1s · self · ×2 uses |
| Hail of Doom Arrow `wh_dlc05_item_abilities_hail_of_doom_arrow` | `excluded (impossible: no enemy-unit read)` | target | While the unit has an enemy in its sights: fire at it. | cd 90s · -1s · enemy unit · ×3 uses |
| Hand of Gods `wh2_main_spell_bound_hand_of_gods` | `excluded (impossible: no enemy-unit read)` | target | While the unit has an enemy in its sights: fire at it. | cd 120s · -1s · enemy unit · ×2 uses · bound |
| Hidden Huntress `wh3_cp1_lord_abilities_hidden_huntress` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (52 m of 75 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 60s · 20s · enemy unit · lord · enemy-targeting mechanism (harness 97) |
| Hidden Huntress Upgraded `wh3_cp1_lord_abilities_hidden_huntress_upgraded` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (52 m of 75 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 90s · 20s · enemy unit · lord · enemy-targeting mechanism (harness 97) |
| Holy Stela `wh2_main_army_abilities_holy_stela` | `excluded (auto: army-bar ability (standing rule 10))` | target | While the unit has an enemy in its sights: cast at the target's position (placement policy needed). | cd 60s · 57s · ground · ×3 uses · army |
| Horn of the Ancestors `wh2_dlc10_item_abilities_horn_of_the_ancestors` | `implemented (enemy-ground: closest FIGHTING enemy)` | enemy_ground_melee | The CLOSEST enemy within the ability's 70% bound (35 m of its 50 m target_intercept_range) that is FIGHTING (in melee): the summon is placed on THAT ENEMY's ground (perform_special_ability_ground, fresh caster + fresh enemy, hold, pre-cast re-check). | cd 120s · 1s · friend/self · ×1 uses · **round 102 (2026-10-17):** implemented on the Gate of Khorne trigger per the user's summon ruling (harness 102) |
| Howl of the Great Beast `wh3_dlc24_unit_abilities_howl_of_the_great_beast` | `implemented (in-melee self)` | target | While the unit has an enemy in its sights: fire at it. | cd 90s · 25s · self · wind-up 1s |
| Howling Winter `wh_dlc08_quest_abilities_howling_winter` | `excluded (not in wheel: boss-only unit)` | target | While the unit has an enemy in its sights: cast on the ground under the target. |  cd 3s · 27s · enemy ground · wind-up 1s · **round 101 (2026-10-17):** boss-only - its ONLY grant path is `wh_dlc08_nor_mon_frost_wyrm_boss` (land_abil.tsv), a quest-battle boss variant; it never shipped in the mod. See §10.3. |
| Hunter of Champions `wh2_dlc17_character_abilities_hunter_of_champions_upgraded` | `excluded (auto: no effect text available (unsourceable))` | target | While the unit has an enemy in its sights: fire at it. | cd 90s · 24s · enemy unit |
| Hunter's Snare `wh2_dlc13_lord_abilities_hunters_snare` | `implemented (enemy-targeted: enemy-ground area)` | enemy_ground | When an enemy unit within the 70% bound (24 m of 35 m) is in melee or under missile fire: `perform_special_ability_ground` places the area on the ENEMY's ground (fresh-handle route). | cd 90s · 11s · enemy ground · ×3 uses · enemy-targeting mechanism (harness 97) |
| Hunter's Trap `wh2_dlc13_lord_abilities_hunters_trap` | `implemented (enemy-targeted: enemy-ground area)` | enemy_ground | When an enemy unit within the 70% bound (24 m of 35 m) is in melee or under missile fire: `perform_special_ability_ground` places the area on the ENEMY's ground (fresh-handle route). | cd 90s · 22s · enemy ground · ×3 uses · enemy-targeting mechanism (harness 97) |
| Hunting Spear `wh_dlc03_weapon_abilities_hunting_spear` | `excluded (auto: explosive projectile)` | target | While the unit has an enemy in its sights: fire at it. | cd 120s · -1s · enemy unit |
| Ice Breath `wh3_dlc24_unit_abilities_ice_breath` | `excluded (auto: explosive projectile)` | target | While the unit has an enemy in its sights: fire at it. | cd 60s · -1s · enemy unit · ×3 uses · wind-up 1.3s |
| Ice Shard `wh3_main_character_abilities_ice_shard` | `excluded (auto: explosive projectile)` | target | While the unit has an enemy in its sights: fire at it. | cd 90s · -1s · enemy unit · ×3 uses · wind-up 3s |
| Inventory of Hatchlings `wh3_dlc26_character_abilities_inventory_of_hatchlings` | `implemented (enemy-ground: closest FIGHTING enemy)` | enemy_ground_melee | The CLOSEST enemy within the ability's 70% bound (35 m of its 50 m target_intercept_range) that is FIGHTING (in melee): the summon is placed on THAT ENEMY's ground (perform_special_ability_ground, fresh caster + fresh enemy, hold, pre-cast re-check). | cd 120s · 1s · enemy ground · ×3 uses · **round 102 (2026-10-17):** implemented on the Gate of Khorne trigger per the user's summon ruling (harness 102) |
| Inventory of Hatchlings Upgraded `wh3_dlc26_character_abilities_inventory_of_hatchlings_upgraded` | `implemented (enemy-ground: closest FIGHTING enemy)` | enemy_ground_melee | The CLOSEST enemy within the ability's 70% bound (70 m of its 100 m target_intercept_range) that is FIGHTING (in melee): the summon is placed on THAT ENEMY's ground (perform_special_ability_ground, fresh caster + fresh enemy, hold, pre-cast re-check). | cd 60s · 1s · enemy ground · ×5 uses · **round 102 (2026-10-17):** implemented on the Gate of Khorne trigger per the user's summon ruling (harness 102) |
| Invocation of the Lichemaster `wh3_dlc29_character_abilities_invocation_of_the_lichemaster` | `implemented (enemy-ground: closest FIGHTING enemy)` | enemy_ground_melee | The CLOSEST enemy within the ability's 70% bound (35 m of its 50 m target_intercept_range) that is FIGHTING (in melee): the summon is placed on THAT ENEMY's ground (perform_special_ability_ground, fresh caster + fresh enemy, hold, pre-cast re-check). | cd 90s · 3s · ground · ×1 uses · **round 102 (2026-10-17):** implemented on the Gate of Khorne trigger per the user's summon ruling (harness 102) |
| Invocation of the Lichemaster `wh3_dlc29_character_abilities_invocation_of_the_lichemaster_0` | `implemented (enemy-ground: closest FIGHTING enemy)` | enemy_ground_melee | The CLOSEST enemy within the ability's 70% bound (35 m of its 50 m target_intercept_range) that is FIGHTING (in melee): the summon is placed on THAT ENEMY's ground (perform_special_ability_ground, fresh caster + fresh enemy, hold, pre-cast re-check). | cd 90s · 3s · ground · ×1 uses · **round 102 (2026-10-17):** implemented on the Gate of Khorne trigger per the user's summon ruling (harness 102) |
| Invocation of the Lichemaster `wh3_dlc29_character_abilities_invocation_of_the_lichemaster_1` | `implemented (enemy-ground: closest FIGHTING enemy)` | enemy_ground_melee | The CLOSEST enemy within the ability's 70% bound (35 m of its 50 m target_intercept_range) that is FIGHTING (in melee): the summon is placed on THAT ENEMY's ground (perform_special_ability_ground, fresh caster + fresh enemy, hold, pre-cast re-check). | cd 90s · 3s · ground · ×1 uses · **round 102 (2026-10-17):** implemented on the Gate of Khorne trigger per the user's summon ruling (harness 102) |
| Iron Reinforcements `wh3_cp1_army_abilities_tiger_warrior_reinforcements` | `excluded (auto: army-bar ability (standing rule 10))` | target | While the unit has an enemy in its sights: fire at it. | cd 120s · 10s · friend/self · ×1 uses · wind-up 5s · army |
| Karanak's Howl `wh3_pro12_hero_abilities_karanaks_howl` | `implemented (enemy-ground: closest FIGHTING enemy)` | enemy_ground_melee | The CLOSEST enemy within the ability's 70% bound (35 m of its 50 m target_intercept_range) that is FIGHTING (in melee): the summon is placed on THAT ENEMY's ground (perform_special_ability_ground, fresh caster + fresh enemy, hold, pre-cast re-check). | cd 120s · 10s · friend/self · ×1 uses · wind-up 5s · **round 102 (2026-10-17):** implemented on the Gate of Khorne trigger per the user's summon ruling (harness 102) |
| Kettle's Call `wh3_dlc25_character_abilities_kettles_call` | `implemented (enemy-ground: closest FIGHTING enemy)` | enemy_ground_melee | The CLOSEST enemy within the ability's 70% bound (31 m of its 45 m target_intercept_range) that is FIGHTING (in melee): the summon is placed on THAT ENEMY's ground (perform_special_ability_ground, fresh caster + fresh enemy, hold, pre-cast re-check). | cd 120s · 1s · friend/self · ×2 uses · wind-up 5s · **round 102 (2026-10-17):** implemented on the Gate of Khorne trigger per the user's summon ruling (harness 102) |
| Koldunja's Spirit `wh3_dlc24_hero_abilities_koldunjas_spirit` | `implemented (enemy-ground: closest FIGHTING enemy)` | enemy_ground_melee | The CLOSEST enemy within the ability's 70% bound (35 m of its 50 m target_intercept_range) that is FIGHTING (in melee): the summon is placed on THAT ENEMY's ground (perform_special_ability_ground, fresh caster + fresh enemy, hold, pre-cast re-check). | cd 120s · 1s · ground · ×1 uses · wind-up 1s · **round 102 (2026-10-17):** implemented on the Gate of Khorne trigger per the user's summon ruling (harness 102) |
| Lamentation of Despairs `wh_dlc05_lord_abilities_lamentation_of_despair` | `excluded (auto: explosive projectile)` | target | While the unit has an enemy in its sights: fire at it. | cd 90s · -1s · enemy unit · wind-up 1s |
| Lamentation of Despairs (Empowered) `wh3_dlc29_lord_abilities_lamentation_of_despair_upgraded` | `excluded (auto: explosive projectile)` | target | While the unit has an enemy in its sights: fire at it. | cd 90s · -1s · enemy unit · wind-up 1s |
| Land Mine `wh3_dlc25_unit_abilities_marienburg_land_mines` | `excluded (auto: explosive / breath attack)` | target | While the unit has an enemy in its sights: fire at it. | cd 10s · -1s · self · ×3 uses |
| Launch Gyrocopters `wh3_dlc25_army_abilities_launch_gyrocopters` | `excluded (auto: army-bar ability (standing rule 10))` | target | While the unit has an enemy in its sights: cast at the target's position (placement policy needed). | cd 120s · 10s · ground · ×1 uses · wind-up 5s · army |
| Lesser Raise Dead `wh2_dlc16_spell_bound_vampires_lesser_raise_dead` | `implemented (enemy-ground: closest FIGHTING enemy)` | enemy_ground_melee | The CLOSEST enemy within the ability's 70% bound (35 m of its 50 m target_intercept_range) that is FIGHTING (in melee): the summon is placed on THAT ENEMY's ground (perform_special_ability_ground, fresh caster + fresh enemy, hold, pre-cast re-check). | cd 0s · 1s · friend/self · ×1 uses · wind-up 3s · bound · **round 102 (2026-10-17):** implemented on the Gate of Khorne trigger per the user's summon ruling (harness 102) |
| Locus of Transmogrification `wh3_main_character_abilities_locus_of_transmogrification` | `implemented (enemy-ground: closest FIGHTING enemy)` | enemy_ground_melee | The CLOSEST enemy within the ability's 70% bound (35 m of its 50 m target_intercept_range) that is FIGHTING (in melee): the summon is placed on THAT ENEMY's ground (perform_special_ability_ground, fresh caster + fresh enemy, hold, pre-cast re-check). | cd 90s · 10s · friend/self · ×2 uses · wind-up 5s · **round 102 (2026-10-17):** implemented on the Gate of Khorne trigger per the user's summon ruling (harness 102) |
| Locus of Virulence `wh3_main_character_abilities_locus_of_virulence` | `implemented (in-melee self)` | target | While the unit has an enemy in its sights: fire at it. | cd 90s · 25s · self |
| Lord of Undeath `wh_pro03_lord_abilities_lord_of_undeath` | `implemented (enemy-ground: closest FIGHTING enemy)` | enemy_ground_melee | The CLOSEST enemy within the ability's 70% bound (35 m of its 50 m target_intercept_range) that is FIGHTING (in melee): the summon is placed on THAT ENEMY's ground (perform_special_ability_ground, fresh caster + fresh enemy, hold, pre-cast re-check). | cd 120s · 1s · friend/self · ×1 uses · **round 102 (2026-10-17):** implemented on the Gate of Khorne trigger per the user's summon ruling (harness 102) |
| Lord of Undeath `wh_pro03_lord_abilities_lord_of_undeath_0` | `implemented (enemy-ground: closest FIGHTING enemy)` | enemy_ground_melee | The CLOSEST enemy within the ability's 70% bound (35 m of its 50 m target_intercept_range) that is FIGHTING (in melee): the summon is placed on THAT ENEMY's ground (perform_special_ability_ground, fresh caster + fresh enemy, hold, pre-cast re-check). | cd 120s · 1s · friend/self · ×1 uses · **round 102 (2026-10-17):** implemented on the Gate of Khorne trigger per the user's summon ruling (harness 102) |
| Lord of Undeath `wh_pro03_lord_abilities_lord_of_undeath_1` | `implemented (enemy-ground: closest FIGHTING enemy)` | enemy_ground_melee | The CLOSEST enemy within the ability's 70% bound (35 m of its 50 m target_intercept_range) that is FIGHTING (in melee): the summon is placed on THAT ENEMY's ground (perform_special_ability_ground, fresh caster + fresh enemy, hold, pre-cast re-check). | cd 120s · 1s · friend/self · ×1 uses · **round 102 (2026-10-17):** implemented on the Gate of Khorne trigger per the user's summon ruling (harness 102) |
| Lord of Undeath `wh_pro03_lord_abilities_lord_of_undeath_2` | `implemented (enemy-ground: closest FIGHTING enemy)` | enemy_ground_melee | The CLOSEST enemy within the ability's 70% bound (35 m of its 50 m target_intercept_range) that is FIGHTING (in melee): the summon is placed on THAT ENEMY's ground (perform_special_ability_ground, fresh caster + fresh enemy, hold, pre-cast re-check). | cd 120s · 1s · friend/self · ×1 uses · **round 102 (2026-10-17):** implemented on the Gate of Khorne trigger per the user's summon ruling (harness 102) |
| Lord of Undeath `wh_pro03_lord_abilities_lord_of_undeath_3` | `implemented (enemy-ground: closest FIGHTING enemy)` | enemy_ground_melee | The CLOSEST enemy within the ability's 70% bound (35 m of its 50 m target_intercept_range) that is FIGHTING (in melee): the summon is placed on THAT ENEMY's ground (perform_special_ability_ground, fresh caster + fresh enemy, hold, pre-cast re-check). | cd 120s · 1s · friend/self · ×1 uses · **round 102 (2026-10-17):** implemented on the Gate of Khorne trigger per the user's summon ruling (harness 102) |
| Lord of Undeath `wh_pro03_lord_abilities_lord_of_undeath_4` | `implemented (enemy-ground: closest FIGHTING enemy)` | enemy_ground_melee | The CLOSEST enemy within the ability's 70% bound (140 m of its 200 m target_intercept_range) that is FIGHTING (in melee): the summon is placed on THAT ENEMY's ground (perform_special_ability_ground, fresh caster + fresh enemy, hold, pre-cast re-check). | cd 120s · 1s · friend/self · ×1 uses · **round 102 (2026-10-17):** implemented on the Gate of Khorne trigger per the user's summon ruling (harness 102) |
| Lure of the Pale Queen `wh2_main_army_abilities_lure_of_the_pale_queen` | `excluded (auto: army-bar ability (standing rule 10))` | target | While the unit has an enemy in its sights: cast at the target's position (placement policy needed). | cd 90s · 11s · ground · ×3 uses · army |
| Maelstrom of Change `wh3_dlc24_unit_abilities_maelstrom_of_change` | `excluded (impossible: no enemy-unit read)` | target | While the unit has an enemy in its sights: fire at it. | cd 60s · 7s · enemy unit · ×3 uses |
| Mark of Yin `wh3_dlc24_unit_abilities_mark_of_yin` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (126 m of 180 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 120s · 28s · enemy unit · wind-up 3s · enemy-targeting mechanism (harness 97) |
| Marked by Ulthar `wh_dlc06_unit_abilities_marked_by_ulthar` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (105 m of 150 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 120s · 28s · enemy unit · wind-up 3s · enemy-targeting mechanism (harness 97) |
| Mask of the Merlord `wh3_dlc27_item_abilities_mask_of_the_merlord` | `implemented (enemy-ground: closest FIGHTING enemy)` | enemy_ground_melee | The CLOSEST enemy within the ability's 70% bound (70 m of its 100 m target_intercept_range) that is FIGHTING (in melee): the summon is placed on THAT ENEMY's ground (perform_special_ability_ground, fresh caster + fresh enemy, hold, pre-cast re-check). | cd 120s · 3s · ground · ×1 uses · wind-up 5s · **round 102 (2026-10-17):** implemented on the Gate of Khorne trigger per the user's summon ruling (harness 102) |
| Master of Souls `wh_dlc08_quest_abilities_master_of_souls` | `excluded (not in wheel: boss-only unit)` | target | While the unit has an enemy in its sights: fire at it. |  cd 5s · 2s · friend · ×40 uses · wind-up 1s · **round 101 (2026-10-17):** boss-only - its ONLY grant path is `wh_dlc08_vmp_mon_terrorgheist_boss` (land_abil.tsv), a quest-battle boss variant; it never shipped in the mod. See §10.3. |
| Master Rune of Flight `wh2_dlc17_rune_abilities_master_rune_of_flight` | `excluded (auto: explosive projectile)` | target | While the unit has an enemy in its sights: fire at it. | cd 120s · -1s · enemy unit |
| Master Rune of Slowness `wh2_dlc17_rune_abilities_master_rune_of_slowness` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (70 m of 100 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 180s · 45s · enemy unit · wind-up 3s · rune · enemy-targeting mechanism (harness 97) |
| Maternal Instinct `wh_dlc06_unit_abilities_maternal_instinct` | `implemented (enemy-ground: closest FIGHTING enemy)` | enemy_ground_melee | The CLOSEST enemy within the ability's 70% bound (35 m of its 50 m target_intercept_range) that is FIGHTING (in melee): the summon is placed on THAT ENEMY's ground (perform_special_ability_ground, fresh caster + fresh enemy, hold, pre-cast re-check). | cd 60s · 1s · enemy ground · ×5 uses · wind-up 5s · **round 102 (2026-10-17):** implemented on the Gate of Khorne trigger per the user's summon ruling (harness 102) |
| Mercurial Shot `wh3_dlc25_character_abilities_mercurial_shot` | `excluded (impossible: no enemy-unit read)` | target | While the unit has an enemy in its sights: fire at it. | cd 90s · -1s · enemy unit · ×3 uses |
| Miasma of Despair `wh2_dlc13_lord_abilities_miasma_of_despair` | `implemented (in-melee self)` | target | While the unit has an enemy in its sights: fire at it. | cd 90s · 16s · self |
| Mighty Roar `wh2_dlc15_unit_abilities_mighty_roar` | `implemented (in-melee self)` | target | While the unit has an enemy in its sights: fire at it. | cd 90s · 25s · self |
| Mislead `wh2_dlc10_lord_abilities_mislead` | `excluded (not in wheel: illusion summon)` | — | illusion (spawn_is_decoy; refused when engaged in melee) | cd 90s · 62s · ground · ×3 uses · **round 102 (2026-10-17):** excluded 2026-10-17 (round 102) - the engine refuses an illusion while its caster is engaged in melee, so a melee trigger can never fire it |
| Mislead `wh2_dlc14_final_battle_ability_summon_snikch` | `excluded (auto: army-bar ability (standing rule 10))` | target | While the unit has an enemy in its sights: cast on the ground under the target. | cd 0s · 1s · enemy ground · ×3 uses · wind-up 1s · army |
| Missile Mirror `wh3_dlc24_unit_bound_missile_mirror` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (140 m of 200 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 44s · 18s · enemy unit · ×2 uses · wind-up 3s · bound · enemy-targeting mechanism (harness 97) |
| Mist Form `wh3_dlc29_lord_abilities_mist_form` | `excluded (auto: vortex)` | target | While the unit has an enemy in its sights: cast at the target's position (placement policy needed). | cd 120s · 1s · ground · wind-up 2s |
| Mither `wh2_dlc15_hero_abilities_mither` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (52 m of 75 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 60s · 15s · enemy unit · ×3 uses · enemy-targeting mechanism (harness 97) |
| Moon Dragon's Breath `wh2_main_unit_abilities_moon_dragons_breath` | `excluded (auto: explosive projectile)` | target | While the unit has an enemy in its sights: fire at it. | cd 60s · -1s · enemy unit · ×3 uses · wind-up 1.3s |
| Moon Flare `wh3_dlc24_unit_abilities_moon_flare` | `excluded (auto: explosive / breath attack)` | target | While the unit has an enemy in its sights: fire at it. | cd 90s · 11.5s · self · ×3 uses · wind-up 1.5s |
| Morikhane, the Black Armour `wh3_dlc29_item_abilities_morikhane_the_black_armour` | `excluded (auto: no effect text available (unsourceable))` | target | While the unit has an enemy in its sights: fire at it. | cd 120s · 14s · self · wind-up 1s · item |
| Nan-Gau Grenades `wh3_dlc24_unit_abilities_nan_gau_grenades` | `excluded (auto: explosive / breath attack)` | target | While the unit has an enemy in its sights: fire at it. | cd 60s · 10s · self · ×2 uses |
| Narcissism `wh3_main_army_abilities_narcissism` | `excluded (auto: army-bar ability (standing rule 10))` | target | While the unit has an enemy in its sights: fire at it. | cd 90s · 16s · enemy unit · wind-up 3s · army |
| Necrotic Explosion `wh3_main_unit_abilities_necrotic_explosion` | `excluded (auto: vortex)` | target | While the unit has an enemy in its sights: fire at it. | cd 0.1s · 10.1s · self · ×1 uses |
| Net of Amyntok `wh_dlc04_spell_bound_net_of_amyntok` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (70 m of 100 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 90s · 20s · enemy unit · ×3 uses · wind-up 3s · bound · enemy-targeting mechanism (harness 97) |
| Noxious Breath `wh2_main_unit_abilities_noxious_breath` | `excluded (auto: explosive projectile)` | target | While the unit has an enemy in its sights: fire at it. | cd 60s · -1s · enemy unit · ×3 uses · wind-up 1.3s |
| Null Stone `wh3_dlc27_item_abilities_null_stone` | `implemented (in-melee self)` | target | While the unit has an enemy in its sights: fire at it. | cd 120s · 35s · self · ×3 uses |
| Nurgling Birth `wh3_dlc29_hero_active_nurgling_birth` | `implemented (enemy-ground: closest FIGHTING enemy)` | enemy_ground_melee | The CLOSEST enemy within the ability's 70% bound (52 m of its 75 m target_intercept_range) that is FIGHTING (in melee): the summon is placed on THAT ENEMY's ground (perform_special_ability_ground, fresh caster + fresh enemy, hold, pre-cast re-check). | cd 90s · 2s · ground · ×3 uses · wind-up 1s · **round 102 (2026-10-17):** implemented on the Gate of Khorne trigger per the user's summon ruling (harness 102) |
| Nurgling Birth Upgraded `wh3_dlc29_hero_active_nurgling_birth_upgraded` | `implemented (enemy-ground: closest FIGHTING enemy)` | enemy_ground_melee | The CLOSEST enemy within the ability's 70% bound (52 m of its 75 m target_intercept_range) that is FIGHTING (in melee): the summon is placed on THAT ENEMY's ground (perform_special_ability_ground, fresh caster + fresh enemy, hold, pre-cast re-check). | cd 90s · 2s · ground · ×5 uses · wind-up 1s · **round 102 (2026-10-17):** implemented on the Gate of Khorne trigger per the user's summon ruling (harness 102) |
| Nurgling Tide `wh3_main_lord_abilities_nurgling_tide` | `implemented (self-summon: the caster itself is in melee)` | self_summon_melee | Fires ONLY when the CASTER ITSELF is in melee (owner alive, not routing, is_in_melee()); cast on SELF, no range bound needed. | cd 90s · 10s · self · ×3 uses · wind-up 3s · **round 102 (2026-10-17):** the user's ruling, verbatim: "that one should only trigger when the caster himself is in melee" (harness 102) |
| Oblast Outriders `wh3_main_abilities_call_horse_archers` | `excluded (auto: army-bar ability (standing rule 10))` | target | While the unit has an enemy in its sights: cast at the target's position (placement policy needed). | cd 120s · 5s · ground · ×2 uses · wind-up 2s · army |
| Oil Flask `wh2_dlc13_lord_abilities_oil_flask` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (49 m of 70 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 90s · -1s · enemy unit · ×3 uses · wind-up 1.9s · enemy-targeting mechanism (harness 97) |
| Otherworldly Pestilence `wh3_dlc29_lord_abilities_otherworldly_pestilence` | `excluded (impossible: no enemy-unit read)` | target | While the unit has an enemy in its sights: fire at it. | cd 120s · 20s · enemy unit · ×1 uses |
| Pageant of Shrikes `wh2_dlc16_character_abilities_pageant_of_shrikes` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (52 m of 75 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 90s · 20s · enemy unit · ×3 uses · enemy-targeting mechanism (harness 97) |
| Pestilent Torrent `wh3_dlc29_lord_active_pestilent_torrent` | `excluded (auto: explosive projectile)` | target | While the unit has an enemy in its sights: fire at it. | cd 90s · -1s · enemy unit · ×3 uses · wind-up 1.3s |
| Pestilential Breath `wh2_main_unit_abilities_pestilential_breath` | `excluded (auto: explosive projectile)` | target | While the unit has an enemy in its sights: fire at it. | cd 60s · -1s · enemy unit · ×3 uses · wind-up 1.3s |
| Petrifying Gaze `wh3_dlc24_unit_passive_petrifying_gaze` | `excluded (auto: no effect text available (unsourceable))` | target | While the unit has an enemy in its sights: fire at it. | cd 120s · 32s · enemy unit · ×2 uses |
| ph `wh2_main_army_abilities_carnosaur_qb_scripted` | `excluded (auto: army-bar ability (standing rule 10))` | target | While the unit has an enemy in its sights: cast on the ground under the target. | cd 80s · 1s · enemy ground · ×3 uses · wind-up 5s · army |
| ph `wh2_main_army_abilities_stegadon_qb_scripted` | `excluded (auto: army-bar ability (standing rule 10))` | target | While the unit has an enemy in its sights: cast on the ground under the target. | cd 80s · 1s · enemy ground · ×3 uses · wind-up 5s · army |
| Plague Monks Below `wh3_dlc29_endgame_crisis_the_vermintide_pestilent_birth_hidden` | `excluded (auto: army-bar ability (standing rule 10))` | target | While the unit has an enemy in its sights: cast on the ground under the target. | cd 60s · 1s · enemy ground · ×1 uses · army |
| Plague of Rust `wh3_main_spell_bound_plague_of_rust` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (140 m of 200 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 60s · 44s · enemy unit · ×2 uses · wind-up 1s · bound · enemy-targeting mechanism (harness 97) |
| Plaguereaper `wh3_dlc29_item_abilities_plaguereaper` | `excluded (auto: own-troop-damage AoE (friendly fire by design, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: fire at it. | cd 120s · 25s · self · ×2 uses · triage-family: Own-troop-damage AoE |
| Plaque of Dominion `wh2_main_item_abilities_plaque_of_dominion` | `implemented (in-melee self)` | target | While the unit has an enemy in its sights: fire at it. | cd 60s · 20s · self |
| Power Siphon `wh2_dlc11_lord_abilities_power_siphon` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (70 m of 100 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 60s · 30s · enemy unit · ×4 uses · enemy-targeting mechanism (harness 97) |
| Punch-Dagger `wh3_dlc29_item_abilities_punch_dagger` | `excluded (impossible: no enemy-unit read)` | target | While the unit has an enemy in its sights: fire at it. | cd 120s · 4s · enemy unit · ×3 uses |
| Pyromaniac `wh2_dlc11_character_abilities_pyromaniac` | `excluded (auto: explosive projectile)` | target | While the unit has an enemy in its sights: fire at it. | cd 90s · -1s · enemy unit · ×3 uses · wind-up 0.4s |
| Quiver of Aqshy `wh2_dlc13_lord_abilities_arrows_of_aqshy` | `excluded (impossible: no enemy-unit read)` | target | While the unit has an enemy in its sights: fire at it. | cd 90s · -1s · enemy unit · ×3 uses · wind-up 4.5s |
| Raging Tornado `wh3_dlc29_unit_abilities_raging_tornado` | `excluded (auto: own-troop-damage AoE (friendly fire by design, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast at the target's position (placement policy needed). | cd 120s · 32s · ground · ×3 uses · wind-up 5s · bound · triage-family: Own-troop-damage AoE |
| Rancid Visitations `wh3_main_spell_bound_rancid_visitations` | `excluded (impossible: no enemy-unit read)` | target | While the unit has an enemy in its sights: fire at it. | cd 90s · 10s · enemy unit · ×2 uses · wind-up 3s · bound |
| Rat Ogres Below `wh3_dlc29_endgame_crisis_the_vermintide_beast_pack_hidden` | `excluded (auto: army-bar ability (standing rule 10))` | target | While the unit has an enemy in its sights: cast on the ground under the target. | cd 45s · 1s · enemy ground · ×1 uses · army |
| Realm of Souls Ushabti `wh2_dlc09_army_abilities_realm_of_souls_ushabti` | `excluded (auto: army-bar ability (standing rule 10))` | target | While the unit has an enemy in its sights: cast on the ground under the target. | cd 0s · 1s · enemy ground · wind-up 10s · army |
| Reaper of Souls `wh2_dlc14_lord_abilities_reaper_of_souls` | `excluded (auto: own-troop-damage AoE (friendly fire by design, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: fire at it. | cd 90s · 9s · self · triage-family: Own-troop-damage AoE |
| Reaver Bow `wh2_main_weapon_bound_reaver_bow` | `excluded (auto: explosive projectile)` | target | While the unit has an enemy in its sights: fire at it. | cd 90s · -1s · enemy unit · ×3 uses · wind-up 1s · bound |
| Ring of Corin `wh2_main_spell_bound_ring_of_corin` | `excluded (auto: own-troop-damage AoE (friendly fire by design, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. | cd 90s · 22s · enemy ground · ×2 uses · bound · triage-family: Own-troop-damage AoE |
| Ritual of the Beast `wh3_dlc24_item_abilities_ritual_of_the_beast` | `implemented (enemy-ground: closest FIGHTING enemy)` | enemy_ground_melee | The CLOSEST enemy within the ability's 70% bound (35 m of its 50 m target_intercept_range) that is FIGHTING (in melee): the summon is placed on THAT ENEMY's ground (perform_special_ability_ground, fresh caster + fresh enemy, hold, pre-cast re-check). | cd 300s · 1s · friend/self · ×1 uses · item · **round 102 (2026-10-17):** implemented on the Gate of Khorne trigger per the user's summon ruling (harness 102) |
| Rock Eye `wh3_main_item_passive_rock_eye` | `implemented (in-melee self)` | target | While the unit has an enemy in its sights: fire at it. | cd 0s · 60s · self · ×1 uses |
| Rot, Glorious Rot `wh3_main_army_abilities_rot_glorious_rot` | `excluded (auto: army-bar ability (standing rule 10))` | target | While the unit has an enemy in its sights: fire at it. | cd 120s · 25s · enemy unit · army |
| Roused to Wrath `wh2_dlc16_lord_abilities_roused_to_wrath` | `implemented (enemy-ground: closest FIGHTING enemy)` | enemy_ground_melee | The CLOSEST enemy within the ability's 70% bound (35 m of its 50 m target_intercept_range) that is FIGHTING (in melee): the summon is placed on THAT ENEMY's ground (perform_special_ability_ground, fresh caster + fresh enemy, hold, pre-cast re-check). | cd 90s · 1s · friend/self · ×1 uses · wind-up 1s · **round 102 (2026-10-17):** implemented on the Gate of Khorne trigger per the user's summon ruling (harness 102) |
| Roused to Wrath `wh2_dlc16_lord_abilities_roused_to_wrath_2` | `implemented (enemy-ground: closest FIGHTING enemy)` | enemy_ground_melee | The CLOSEST enemy within the ability's 70% bound (35 m of its 50 m target_intercept_range) that is FIGHTING (in melee): the summon is placed on THAT ENEMY's ground (perform_special_ability_ground, fresh caster + fresh enemy, hold, pre-cast re-check). | cd 90s · 1s · friend/self · ×2 uses · wind-up 1s · **round 102 (2026-10-17):** implemented on the Gate of Khorne trigger per the user's summon ruling (harness 102) |
| Roused to Wrath `wh2_dlc16_lord_abilities_roused_to_wrath_3` | `excluded (auto: army-bar ability (standing rule 10))` | target | While the unit has an enemy in its sights: fire at it. | cd 90s · 1s · friend/self · ×3 uses · wind-up 1s · army |
| Rune of Slowness `wh2_dlc17_rune_abilities_rune_of_slowness` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (70 m of 100 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 120s · 30s · enemy unit · wind-up 3s · rune · enemy-targeting mechanism (harness 97) |
| Ryze: Crypt Horrors `wh3_dlc29_army_abilities_ryze_the_grave_call_crypt_horrors` | `excluded (auto: army-bar ability (standing rule 10))` | target | While the unit has an enemy in its sights: cast on the ground under the target. | cd 0s · 1s · enemy ground · ×2 uses · wind-up 10s · army |
| Ryze: Grave Guard `wh3_dlc29_army_abilities_ryze_the_grave_call_grave_guard` | `excluded (auto: army-bar ability (standing rule 10))` | target | While the unit has an enemy in its sights: cast on the ground under the target. | cd 0s · 1s · enemy ground · ×2 uses · wind-up 10s · army |
| Ryze: Grave Guard Upgraded `wh3_dlc29_army_abilities_ryze_the_grave_call_grave_guard_endless` | `excluded (auto: army-bar ability (standing rule 10))` | target | While the unit has an enemy in its sights: cast on the ground under the target. | cd 0s · 1s · enemy ground · ×2 uses · wind-up 10s · army |
| Ryze: Khemrian Warsphinx `wh3_dlc29_army_abilities_ryze_the_grave_call_khemrian_warsphinx` | `excluded (auto: army-bar ability (standing rule 10))` | target | While the unit has an enemy in its sights: cast on the ground under the target. | cd 0s · 1s · enemy ground · ×1 uses · wind-up 10s · army |
| Ryze: Khemric Titan `wh3_dlc29_army_abilities_ryze_the_grave_call_khemric_titan` | `excluded (auto: army-bar ability (standing rule 10))` | target | While the unit has an enemy in its sights: cast on the ground under the target. | cd 0s · 1s · enemy ground · ×1 uses · wind-up 10s · army |
| Ryze: Khemric Titan Upgraded `wh3_dlc29_army_abilities_ryze_the_grave_call_khemric_titan_endless` | `excluded (auto: army-bar ability (standing rule 10))` | target | While the unit has an enemy in its sights: cast on the ground under the target. | cd 0s · 1s · enemy ground · ×1 uses · wind-up 10s · army |
| Ryze: Mournguls `wh3_dlc29_army_abilities_ryze_the_grave_call_mournguls` | `excluded (auto: army-bar ability (standing rule 10))` | target | While the unit has an enemy in its sights: cast on the ground under the target. | cd 0s · 1s · enemy ground · ×2 uses · wind-up 10s · army |
| Ryze: Necrofex Colossus `wh3_dlc29_army_abilities_ryze_the_grave_call_necrofex_colossus` | `excluded (auto: army-bar ability (standing rule 10))` | target | While the unit has an enemy in its sights: cast on the ground under the target. | cd 0s · 1s · enemy ground · ×1 uses · wind-up 10s · army |
| Ryze: Nehekharan Warriors `wh3_dlc29_army_abilities_ryze_the_grave_call_nehekharan_warriors` | `excluded (auto: army-bar ability (standing rule 10))` | target | While the unit has an enemy in its sights: cast on the ground under the target. | cd 0s · 1s · enemy ground · ×3 uses · wind-up 10s · army |
| Ryze: Rotting Prometheans (Gunnery Mob) `wh3_dlc29_army_abilities_ryze_the_grave_call_rotting_prometheans_gunnery_mob` | `excluded (auto: army-bar ability (standing rule 10))` | target | While the unit has an enemy in its sights: cast on the ground under the target. | cd 0s · 1s · enemy ground · ×2 uses · wind-up 10s · army |
| Ryze: Rotting Prometheans (Gunnery Mob) Upgraded `wh3_dlc29_army_abilities_ryze_the_grave_call_rotting_prometheans_gunnery_mob_endless` | `excluded (auto: army-bar ability (standing rule 10))` | target | While the unit has an enemy in its sights: cast on the ground under the target. | cd 0s · 1s · enemy ground · ×2 uses · wind-up 10s · army |
| Ryze: Spirit Host `wh3_dlc29_army_abilities_ryze_the_grave_call_spirit_host` | `excluded (auto: army-bar ability (standing rule 10))` | target | While the unit has an enemy in its sights: cast on the ground under the target. | cd 0s · 1s · enemy ground · ×3 uses · wind-up 10s · army |
| Ryze: Terrorgheist `wh3_dlc29_army_abilities_ryze_the_grave_call_terrorgheist` | `excluded (auto: army-bar ability (standing rule 10))` | target | While the unit has an enemy in its sights: cast on the ground under the target. | cd 0s · 1s · enemy ground · ×1 uses · wind-up 10s · army |
| Ryze: Ushabti `wh3_dlc29_army_abilities_ryze_the_grave_call_ushabti` | `excluded (auto: army-bar ability (standing rule 10))` | target | While the unit has an enemy in its sights: cast on the ground under the target. | cd 0s · 1s · enemy ground · ×2 uses · wind-up 10s · army |
| Ryze: Zombie Pirate Gunnery Mob (Bombers) `wh3_dlc29_army_abilities_ryze_the_grave_call_zombie_pirate_gunnery_mob_bombers` | `excluded (auto: army-bar ability (standing rule 10))` | target | While the unit has an enemy in its sights: cast on the ground under the target. | cd 0s · 1s · enemy ground · ×3 uses · wind-up 10s · army |
| Sacrilege `wh2_dlc11_character_abilities_sacrilege` | `implemented (enemy-ground: closest FIGHTING enemy)` | enemy_ground_melee | The CLOSEST enemy within the ability's 70% bound (35 m of its 50 m target_intercept_range) that is FIGHTING (in melee): the summon is placed on THAT ENEMY's ground (perform_special_ability_ground, fresh caster + fresh enemy, hold, pre-cast re-check). | cd 120s · 3s · friend/self · ×2 uses · wind-up 3s · **round 102 (2026-10-17):** implemented on the Gate of Khorne trigger per the user's summon ruling (harness 102) |
| Savage Dominion `wh2_dlc17_spell_bound_savage_dominion` | `implemented (enemy-ground: closest FIGHTING enemy)` | enemy_ground_melee | The CLOSEST enemy within the ability's 70% bound (35 m of its 50 m target_intercept_range) that is FIGHTING (in melee): the summon is placed on THAT ENEMY's ground (perform_special_ability_ground, fresh caster + fresh enemy, hold, pre-cast re-check). | cd 120s · 1s · friend/self · ×2 uses · wind-up 5s · bound · **round 102 (2026-10-17):** implemented on the Gate of Khorne trigger per the user's summon ruling (harness 102) |
| Savage Predators `wh3_dlc26_hero_abilities_savage_predators` | `implemented (enemy-ground: closest FIGHTING enemy)` | enemy_ground_melee | The CLOSEST enemy within the ability's 70% bound (31 m of its 45 m target_intercept_range) that is FIGHTING (in melee): the summon is placed on THAT ENEMY's ground (perform_special_ability_ground, fresh caster + fresh enemy, hold, pre-cast re-check). | cd 120s · 1s · friend/self · ×1 uses · wind-up 5s · **round 102 (2026-10-17):** implemented on the Gate of Khorne trigger per the user's summon ruling (harness 102) |
| Schalkain's Teeth `wh3_dlc27_item_abilities_schalkains_teeth` | `excluded (impossible: no enemy-unit read)` | target | While the unit has an enemy in its sights: fire at it. | cd 90s · -1s · enemy unit · ×2 uses |
| Scroll of Leeching `wh_main_item_abilities_scroll_of_leeching` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (70 m of 100 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 60s · 44s · enemy unit · ×1 uses · enemy-targeting mechanism (harness 97) |
| Searing Torrent `wh3_twa07_unit_abilities_searing_torrent` | `excluded (auto: explosive / breath attack)` | target | While the unit has an enemy in its sights: fire at it. | cd 60s · -1s · self · ×5 uses |
| Seduction `wh2_dlc11_lord_abilities_seduction` | `excluded (auto: no effect text available (unsourceable))` | target | While the unit has an enemy in its sights: fire at it. | cd 120s · 41s · self |
| Servants of Nagash `wh_dlc04_quest_abilities_servant_of_nagash` | `excluded (not in wheel: boss-only unit)` | target | While the unit has an enemy in its sights: fire at it. |  cd 8s · 5s · friend · ×15 uses · **round 101 (2026-10-17):** boss-only - its ONLY grant path is `wh_dlc04_vmp_cha_strigoi_ghoul_king_0_boss` (land_abil.tsv), a quest-battle boss variant; it never shipped in the mod. See §10.3. |
| Shackolot's Noxious Breath `wh2_dlc15_unit_abilities_noxious_breath_imrik` | `excluded (auto: explosive projectile)` | target | While the unit has an enemy in its sights: fire at it. | cd 60s · -1s · enemy unit · ×3 uses · wind-up 1.3s |
| Shadowblood `wh3_dlc29_lord_abilities_shadowblood` | `excluded (impossible: no enemy-unit read)` | target | While the unit has an enemy in its sights: fire at it. | cd 120s · -1s · enemy unit · ×3 uses · wind-up 3s |
| Shadowstrider `wh3_dlc29_lord_abilities_warp_step` | `excluded (auto: vortex)` | target | While the unit has an enemy in its sights: cast at the target's position (placement policy needed). | cd 120s · -1s · ground · wind-up 3s |
| Shamanistic Ritual (Death) `wh3_dlc27_army_abilities_sayl_manipulations_spawn_shaman_death` | `excluded (auto: army-bar ability (standing rule 10))` | target | While the unit has an enemy in its sights: fire at it. | cd 90s · 1s · friend/self · ×1 uses · wind-up 3s · army |
| Shamanistic Ritual (Fire) `wh3_dlc27_army_abilities_sayl_manipulations_spawn_shaman_fire` | `excluded (auto: army-bar ability (standing rule 10))` | target | While the unit has an enemy in its sights: fire at it. | cd 90s · 1s · friend/self · ×1 uses · wind-up 3s · army |
| Shamanistic Ritual (Metal) `wh3_dlc27_army_abilities_sayl_manipulations_spawn_shaman_metal` | `excluded (auto: army-bar ability (standing rule 10))` | target | While the unit has an enemy in its sights: fire at it. | cd 90s · 1s · friend/self · ×1 uses · wind-up 3s · army |
| Shard Blade `wh3_main_weapon_abilities_shard_blade` | `excluded (auto: own-troop-damage AoE (friendly fire by design, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: fire at it. | cd 120s · 15s · self · ×2 uses · triage-family: Own-troop-damage AoE |
| Shem's Burning Gaze `wh_main_spell_light_shems_burning_gaze_bound` | `excluded (impossible: no enemy-unit read)` | target | While the unit has an enemy in its sights: fire at it. | cd 60s · -1s · enemy unit · ×3 uses · wind-up 3s · bound |
| Silence the Prey `wh3_main_character_abilities_silence_the_prey` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (70 m of 100 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 60s · 30s · enemy unit · ×4 uses · enemy-targeting mechanism (harness 97) |
| Skarsnik's Prodder `wh_dlc06_weapon_abilities_skarsniks_prodder` | `excluded (auto: explosive projectile)` | target | While the unit has an enemy in its sights: fire at it. | cd 120s · -1s · enemy unit · ×2 uses · wind-up 3s |
| Skryre Clanstone `wh2_main_army_abilities_skryre_clanstone` | `excluded (auto: army-bar ability (standing rule 10))` | target | While the unit has an enemy in its sights: cast at the target's position (placement policy needed). | cd 120s · 52s · ground · ×3 uses · army |
| Sky-Junk Bomb `wh3_main_unit_abilities_sky_junk_bomb` | `excluded (auto: explosive / breath attack)` | target | While the unit has an enemy in its sights: fire at it. | cd 30s · 1s · self · ×3 uses · wind-up 1s |
| Skyhammer Bomb `wh_dlc06_unit_abilities_skyhammer_bomb` | `excluded (auto: explosive / breath attack)` | target | While the unit has an enemy in its sights: fire at it. | cd 0.1s · 1s · self · ×5 uses |
| Skyhammer Fire Bomb `wh_dlc06_unit_abilities_skyhammer_fire_bomb` | `excluded (auto: explosive / breath attack)` | target | While the unit has an enemy in its sights: fire at it. | cd 0.1s · 1s · self · ×5 uses |
| Slann Gold `wh2_dlc11_item_abilities_slann_gold` | `excluded (auto: explosive / breath attack)` | target | While the unit has an enemy in its sights: fire at it. | cd 120s · 55s · enemy unit |
| Song of Enthrallment `wh2_dlc11_lord_abilities_song_of_enthrallment` | `excluded (auto: explosive / breath attack)` | target | While the unit has an enemy in its sights: fire at it. | cd 90s · 22s · self |
| Soporific Breath `wh2_main_unit_abilities_soporific_breath` | `excluded (auto: explosive projectile)` | target | While the unit has an enemy in its sights: fire at it. | cd 60s · -1s · enemy unit · ×3 uses · wind-up 1.3s |
| Soul Stealer `wh2_dlc10_spell_bound_soul_stealer_ror` | `excluded (auto: own-troop-damage AoE (friendly fire by design, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. | cd 120s · 12s · enemy ground · ×1 uses · bound · triage-family: Own-troop-damage AoE |
| Soul Stealer `wh3_dlc27_spell_bound_soul_stealer` | `excluded (auto: own-troop-damage AoE (friendly fire by design, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. | cd 120s · 12s · enemy ground · ×1 uses · bound · triage-family: Own-troop-damage AoE |
| Spear of Grungni `wh3_dlc25_unit_abilities_spear_of_grungni` | `excluded (impossible: no enemy-unit read)` | target | While the unit has an enemy in its sights: fire at it. | cd 120s · -1s · enemy unit · ×1 uses · wind-up 1s |
| Spear of Kurnous `wh_dlc05_weapon_abilities_spear_of_kurnous` | `excluded (impossible: no enemy-unit read)` | target | While the unit has an enemy in its sights: fire at it. | cd 120s · -1s · enemy unit |
| Spirit Bear `wh3_dlc24_lord_abilities_spirit_bear` | `excluded (impossible: no enemy-unit read)` | target | While the unit has an enemy in its sights: fire at it. | cd 120s · -1s · enemy unit · ×3 uses · wind-up 4s |
| Spirit Leech `wh2_dlc09_spell_death_spirit_leech_bound` | `excluded (impossible: no enemy-unit read)` | target | While the unit has an enemy in its sights: fire at it. | cd 45s · 13s · enemy unit · ×2 uses · wind-up 3s · bound |
| Spirit Leech `wh3_dlc25_spell_bound_spirit_leech` | `excluded (impossible: no enemy-unit read)` | target | While the unit has an enemy in its sights: fire at it. | cd 32s · 13s · enemy unit · ×2 uses · wind-up 1s · bound |
| Spirit Leech `wh3_dlc25_spell_bound_spirit_leech_gunnery_school` | `excluded (impossible: no enemy-unit read)` | target | While the unit has an enemy in its sights: fire at it. | cd 32s · 13s · enemy unit · ×1 uses · wind-up 1s · bound |
| Spirit Leech `wh3_main_spell_bound_spirit_leech` | `excluded (impossible: no enemy-unit read)` | target | While the unit has an enemy in its sights: fire at it. | cd 60s · 13s · enemy unit · ×2 uses · wind-up 1s · bound |
| Spirit Leech `wh3_twa08_spell_bound_spirit_leech_great_unclean_one_ror` | `excluded (impossible: no enemy-unit read)` | target | While the unit has an enemy in its sights: fire at it. | cd 60s · 13s · enemy unit · ×1 uses · wind-up 1s · bound |
| Spirit of Grungni `wh3_dlc25_army_abilities_spirit_of_grungni` | `excluded (auto: army-bar ability (standing rule 10))` | target | While the unit has an enemy in its sights: cast at the target's position (placement policy needed). | cd 120s · 1s · ground · ×1 uses · wind-up 5s · army |
| Spurting Bile-Blood `wh3_dlc27_item_abilities_spurting_bile_blood` | `excluded (auto: vortex)` | target | While the unit has an enemy in its sights: fire at it. | cd 0s · 9s · self · ×2 uses · bound |
| Squig Thinkin' `wh3_dlc26_character_abilities_squig_thinkin` | `excluded (auto: summon)` | target | While the unit has an enemy in its sights: cast at the target's position (placement policy needed). | cd 90s · 1s · ground · ×1 uses |
| Star Dragon's Breath `wh2_main_unit_abilities_star_dragons_breath` | `excluded (auto: explosive projectile)` | target | While the unit has an enemy in its sights: fire at it. | cd 60s · -1s · enemy unit · ×3 uses · wind-up 1.3s |
| Stave of Ruinous Corruption `wh_dlc05_weapon_abilities_stave_of_ruinous_corruption` | `implemented (enemy-ground: closest FIGHTING enemy)` | enemy_ground_melee | The CLOSEST enemy within the ability's 70% bound (35 m of its 50 m target_intercept_range) that is FIGHTING (in melee): the summon is placed on THAT ENEMY's ground (perform_special_ability_ground, fresh caster + fresh enemy, hold, pre-cast re-check). | cd 120s · 1s · enemy ground · ×1 uses · wind-up 5s · **round 102 (2026-10-17):** implemented on the Gate of Khorne trigger per the user's summon ruling (harness 102) |
| Sting of Snagla `wh3_dlc26_character_abilities_sting_of_snagla` | `excluded (impossible: no enemy-unit read)` | target | While the unit has an enemy in its sights: fire at it. | cd 120s · -1s · enemy unit · ×3 uses · wind-up 2s |
| Storm Daemon `wh2_dlc12_weapon_abilities_storm_daemon` | `excluded (auto: explosive projectile)` | target | While the unit has an enemy in its sights: fire at it. | cd 120s · -1s · enemy unit · ×2 uses · wind-up 5s |
| Stormvermin Below `wh3_dlc29_endgame_crisis_the_vermintide_stormvermin_menace_below_hidden` | `excluded (auto: army-bar ability (standing rule 10))` | target | While the unit has an enemy in its sights: cast on the ground under the target. | cd 75s · 1s · enemy ground · ×1 uses · army |
| Summon Plague Drones `wh3_dlc29_army_abilities_rotborne_summon_plague_drones` | `excluded (auto: army-bar ability (standing rule 10))` | target | While the unit has an enemy in its sights: cast at the target's position (placement policy needed). | cd 120s · 10s · ground · ×1 uses · wind-up 5s · army |
| Summon Plague Drones (Death's heads) `wh3_dlc29_army_abilities_rotborne_summon_plague_drones_1` | `excluded (auto: army-bar ability (standing rule 10))` | target | While the unit has an enemy in its sights: cast at the target's position (placement policy needed). | cd 120s · 10s · ground · ×1 uses · wind-up 5s · army |
| Summon the Sentinels `wh2_dlc15_army_abilities_summon_the_sentinels` | `excluded (auto: army-bar ability (standing rule 10))` | target | While the unit has an enemy in its sights: cast at the target's position (placement policy needed). | cd 120s · 5s · ground · ×2 uses · wind-up 2s · army |
| Summon the Sentinels Upgraded `wh2_dlc15_army_abilities_summon_the_sentinels_upgraded` | `excluded (auto: army-bar ability (standing rule 10))` | target | While the unit has an enemy in its sights: cast at the target's position (placement policy needed). | cd 120s · 5s · ground · ×4 uses · wind-up 2s · army |
| Summoned from Beyond `wh3_main_army_abilities_summoned_from_beyond_daemon_prince` | `excluded (auto: army-bar ability (standing rule 10))` | target | While the unit has an enemy in its sights: cast on the ground under the target. | cd 90s · 10s · enemy ground · ×10 uses · wind-up 5s · army |
| Summoned from Beyond `wh3_main_army_abilities_summoned_from_beyond_khorne` | `excluded (auto: army-bar ability (standing rule 10))` | target | While the unit has an enemy in its sights: cast on the ground under the target. | cd 120s · 10s · enemy ground · ×2 uses · wind-up 5s · army |
| Summoned from Beyond `wh3_main_army_abilities_summoned_from_beyond_nurgle` | `excluded (auto: army-bar ability (standing rule 10))` | target | While the unit has an enemy in its sights: cast on the ground under the target. | cd 120s · 10s · enemy ground · ×2 uses · wind-up 5s · army |
| Summoned from Beyond `wh3_main_army_abilities_summoned_from_beyond_slaanesh` | `excluded (auto: army-bar ability (standing rule 10))` | target | While the unit has an enemy in its sights: cast on the ground under the target. | cd 120s · 10s · enemy ground · ×2 uses · wind-up 5s · army |
| Summoned from Beyond `wh3_main_army_abilities_summoned_from_beyond_tzeentch` | `excluded (auto: army-bar ability (standing rule 10))` | target | While the unit has an enemy in its sights: cast on the ground under the target. | cd 120s · 10s · enemy ground · ×2 uses · wind-up 5s · army |
| Sun Dragon's Breath `wh2_main_unit_abilities_sun_dragons_breath` | `excluded (auto: explosive projectile)` | target | While the unit has an enemy in its sights: fire at it. | cd 60s · -1s · enemy unit · ×3 uses · wind-up 1.3s |
| Surface `wh3_dlc27_unit_abilities_dread_maw_surface` | `excluded (auto: summon)` | target | While the unit has an enemy in its sights: fire at it. | cd 25s · 2s · self |
| Surprise Squig! `wh3_dlc25_character_abilities_surprise_squig` | `implemented (enemy-ground: closest FIGHTING enemy)` | enemy_ground_melee | The CLOSEST enemy within the ability's 70% bound (35 m of its 50 m target_intercept_range) that is FIGHTING (in melee): the summon is placed on THAT ENEMY's ground (perform_special_ability_ground, fresh caster + fresh enemy, hold, pre-cast re-check). | cd 60s · 1s · friend/self · ×5 uses · **round 102 (2026-10-17):** implemented on the Gate of Khorne trigger per the user's summon ruling (harness 102) |
| Swamp Breath `wh2_dlc15_hero_abilities_swamp_breath` | `excluded (impossible: no enemy-unit read)` | target | While the unit has an enemy in its sights: fire at it. | cd 60s · -1s · enemy unit · ×3 uses · wind-up 1.2s |
| Sword of Change `wh_dlc01_weapon_abilities_sword_of_change` | `implemented (enemy-ground: closest FIGHTING enemy)` | enemy_ground_melee | The CLOSEST enemy within the ability's 70% bound (35 m of its 50 m target_intercept_range) that is FIGHTING (in melee): the summon is placed on THAT ENEMY's ground (perform_special_ability_ground, fresh caster + fresh enemy, hold, pre-cast re-check). | cd 90s · 11s · friend/self · ×1 uses · wind-up 5s · **round 102 (2026-10-17):** implemented on the Gate of Khorne trigger per the user's summon ruling (harness 102) |
| Sword of Daith `wh_dlc05_weapon_abilities_daiths_sword` | `excluded (auto: own-troop-damage AoE (friendly fire by design, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. | cd 120s · 17s · enemy ground · ×2 uses · triage-family: Own-troop-damage AoE |
| Sword of Filth `wh3_dlc25_weapon_abilities_sword_of_filth` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (24 m of 35 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 120s · 20s · enemy unit · wind-up 1s · enemy-targeting mechanism (harness 97) |
| Taal's Judgement `wh3_dlc24_lord_abilities_taals_judgement` | `excluded (impossible: no enemy-unit read)` | target | While the unit has an enemy in its sights: fire at it. | cd 90s · -1s · enemy unit · ×3 uses · wind-up 4.5s |
| Temple of Mists `wh2_main_army_abilities_temple_of_mists` | `excluded (auto: army-bar ability (standing rule 10))` | target | While the unit has an enemy in its sights: cast at the target's position (placement policy needed). | cd 120s · 38s · ground · ×3 uses · army |
| Terrible Malice `wh3_dlc27_qb_unit_abilities_terrible_malice` | `excluded (not in wheel: boss-only unit)` | target | While the unit has an enemy in its sights: fire at it. |  cd 90s · 2s · enemy unit · **round 101 (2026-10-17):** boss-only - its ONLY grant path is `wh3_dlc27_sla_mon_preyton_boss` (land_abil.tsv), a quest-battle boss variant; it never shipped in the mod. See §10.3. |
| The Amber Spear `wh_dlc03_spell_bound_the_amber_spear` | `excluded (auto: explosive projectile)` | target | While the unit has an enemy in its sights: fire at it. | cd 90s · -1s · enemy unit · ×3 uses · bound |
| The Amber Trance `wh2_dlc10_item_abilities_the_amber_trance` | `excluded (impossible: no enemy-unit read)` | target | While the unit has an enemy in its sights: fire at it. | cd 60s · 25s · enemy unit · ×1 uses |
| The Awakening `wh3_dlc29_lord_abilities_the_awakening` | `implemented (enemy-ground: closest FIGHTING enemy)` | enemy_ground_melee | The CLOSEST enemy within the ability's 70% bound (52 m of its 75 m target_intercept_range) that is FIGHTING (in melee): the summon is placed on THAT ENEMY's ground (perform_special_ability_ground, fresh caster + fresh enemy, hold, pre-cast re-check). | cd 120s · 1s · ground · ×1 uses · wind-up 3s · **round 102 (2026-10-17):** implemented on the Gate of Khorne trigger per the user's summon ruling (harness 102) |
| The Bitter End `wh3_dlc27_army_abilities_eternal_dance_tempo_3_poisonous_aroma` | `excluded (auto: army-bar ability (standing rule 10))` | target | While the unit has an enemy in its sights: fire at it. | cd 120s · 10s · enemy unit · ×2 uses · wind-up 1s · army |
| The Bitterness of Winter `wh3_main_army_abilities_the_bitterness_of_winter` | `excluded (auto: army-bar ability (standing rule 10))` | target | While the unit has an enemy in its sights: cast on the ground under the target. | cd 90s · 16s · enemy ground · ×3 uses · army |
| The Dance of Dreaming `wh3_dlc27_lord_abilities_the_dance_of_dreaming` | `implemented (in-melee self)` | target | While the unit has an enemy in its sights: fire at it. | cd 20s · -1s · self · lord |
| The Divestment `wh3_dlc27_army_abilities_eternal_dance_tempo_3_insidious_allure` | `excluded (auto: own-troop-damage AoE (friendly fire by design, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast at the target's position (placement policy needed). | cd 120s · 24s · ground · ×1 uses · wind-up 3s · army · triage-family: Own-troop-damage AoE |
| The Emperor's Executioner `wh3_dlc24_lord_abilities_the_emperors_executioner` | `excluded (impossible: no enemy-unit read)` | target | While the unit has an enemy in its sights: fire at it. | cd 120s · 2s · enemy unit · ×1 uses · wind-up 2s |
| The Emperor's Executioner `wh3_dlc24_lord_abilities_the_emperors_executioner_upgrade` | `excluded (impossible: no enemy-unit read)` | target | While the unit has an enemy in its sights: fire at it. | cd 120s · 2s · enemy unit · ×1 uses · wind-up 2s |
| The Fate of Bjuna `wh3_dlc25_spell_bound_the_fate_of_bjuna` | `excluded (impossible: no enemy-unit read)` | target | While the unit has an enemy in its sights: fire at it. | cd 52s · 18s · enemy unit · ×1 uses · wind-up 5s · bound |
| The Fate of Bjuna `wh3_main_spell_bound_the_fate_of_bjuna` | `excluded (impossible: no enemy-unit read)` | target | While the unit has an enemy in its sights: fire at it. | cd 120s · 18s · enemy unit · ×1 uses · wind-up 5s · bound |
| The Gaze of Dust `wh3_dlc29_unit_abilities_the_gaze_of_dust` | `excluded (impossible: no enemy-unit read)` | target | While the unit has an enemy in its sights: fire at it. | cd 120s · -1s · enemy unit · ×3 uses · wind-up 2.5s |
| The Heralds' Arrival `wh3_dlc29_vmp_mon_morghast_archai_summon` | `implemented (enemy-ground: closest FIGHTING enemy)` | enemy_ground_melee | The CLOSEST enemy within the ability's 70% bound (35 m of its 50 m target_intercept_range) that is FIGHTING (in melee): the summon is placed on THAT ENEMY's ground (perform_special_ability_ground, fresh caster + fresh enemy, hold, pre-cast re-check). | cd 120s · 10s · ground · ×1 uses · **round 102 (2026-10-17):** implemented on the Gate of Khorne trigger per the user's summon ruling (harness 102) |
| The Golden Blowpipe of P'Toohee `wh2_dlc17_weapon_abilities_the_golden_blowpipe_of_ptoohee` | `excluded (impossible: no enemy-unit read)` | target | While the unit has an enemy in its sights: fire at it. | cd 120s · -1s · enemy unit · wind-up 2.5s |
| The Liber Bubonicus `wh2_main_item_abilities_the_liber_bubonicus` | `excluded (impossible: no enemy-unit read)` | target | While the unit has an enemy in its sights: fire at it. | cd 120s · 15s · enemy unit · ×2 uses |
| The Menace Below `wh2_dlc29_army_abilities_the_menace_below_qb` | `excluded (auto: army-bar ability (standing rule 10))` | target | While the unit has an enemy in its sights: cast on the ground under the target. | cd 45s · 1s · enemy ground · ×5 uses · wind-up 5s · army |
| The Menace Below `wh2_main_army_abilities_the_menace_below` | `excluded (auto: army-bar ability (standing rule 10))` | target | While the unit has an enemy in its sights: cast on the ground under the target. | cd 45s · 1s · enemy ground · ×1 uses · wind-up 5s · army |
| The Menace Below (Stormvermin) `wh3_dlc29_army_abilities_stormvermin_menace_below` | `excluded (auto: army-bar ability (standing rule 10))` | target | While the unit has an enemy in its sights: cast on the ground under the target. | cd 60s · 1s · enemy ground · ×2 uses · wind-up 5s · army |
| The Moonbow `wh2_dlc10_weapon_abilities_the_moonbow` | `excluded (auto: explosive projectile)` | target | While the unit has an enemy in its sights: fire at it. | cd 120s · -1s · enemy unit · ×2 uses · wind-up 3s |
| The Portalglyph `wh3_main_item_abilities_the_portalglyph` | `implemented (enemy-ground: closest FIGHTING enemy)` | enemy_ground_melee | The CLOSEST enemy within the ability's 70% bound (35 m of its 50 m target_intercept_range) that is FIGHTING (in melee): the summon is placed on THAT ENEMY's ground (perform_special_ability_ground, fresh caster + fresh enemy, hold, pre-cast re-check). | cd 120s · 10s · enemy ground · ×1 uses · wind-up 5s · **round 102 (2026-10-17):** implemented on the Gate of Khorne trigger per the user's summon ruling (harness 102) |
| The Soulstealer `wh3_dlc29_spell_bound_undeath_khizaar_the_soulstealer` | `excluded (auto: enemy-ground placement (no placement path))` | target | While the unit has an enemy in its sights: cast on the ground under the target. | cd 37s · 11s · enemy ground · ×1 uses · wind-up 3s · bound |
| The Tomb Blade of Arkhan `wh2_dlc09_weapon_abilities_tomb_blade_of_arkhan` | `implemented (enemy-ground: closest FIGHTING enemy)` | enemy_ground_melee | The CLOSEST enemy within the ability's 70% bound (35 m of its 50 m target_intercept_range) that is FIGHTING (in melee): the summon is placed on THAT ENEMY's ground (perform_special_ability_ground, fresh caster + fresh enemy, hold, pre-cast re-check). | cd 120s · 1s · friend/self · ×5 uses · **round 102 (2026-10-17):** implemented on the Gate of Khorne trigger per the user's summon ruling (harness 102) |
| The Trickster's Pendant `wh2_main_item_abilities_the_tricksters_pendant` | `implemented (enemy-targeted: enemy-ground area)` | enemy_ground | When an enemy unit within the 70% bound (70 m of 100 m) is in melee or under missile fire: `perform_special_ability_ground` places the area on the ENEMY's ground (fresh-handle route). | cd 60s · 16s · enemy ground · enemy-targeting mechanism (harness 97) |
| The Venom Staff `wh2_dlc09_weapon_abilities_venom_staff` | `excluded (auto: explosive projectile)` | target | While the unit has an enemy in its sights: fire at it. | cd 30s · -1s · enemy unit · ×4 uses · wind-up 1s |
| The Vial of Hashut `wh3_dlc23_item_abilities_the_vial_of_hashut` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (35 m of 50 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 120s · 60s · enemy unit · ×1 uses · enemy-targeting mechanism (harness 97) |
| The Vortex Shard `wh2_main_item_abilities_the_vortex_shard` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (70 m of 100 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 60s · 31s · enemy unit · ×1 uses · enemy-targeting mechanism (harness 97) |
| The Windblade `wh3_dlc24_hero_abilities_windblade` | `excluded (impossible: no enemy-unit read)` | target | While the unit has an enemy in its sights: fire at it. | cd 120s · -1s · enemy unit · wind-up 1s |
| The Withering `wh3_dlc23_spell_bound_the_withering` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (140 m of 200 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 90s · 40s · enemy unit · ×1 uses · bound · enemy-targeting mechanism (harness 97) |
| The Withering `wh3_twa08_spell_bound_the_withering` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (140 m of 200 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 90s · 40s · enemy unit · ×1 uses · bound · enemy-targeting mechanism (harness 97) |
| Thorn's Aura `wh3_dlc24_hero_abilities_thorns_aura` | `implemented (in-melee self)` | target | While the unit has an enemy in its sights: fire at it. | cd 120s · 30s · self |
| Thunderburner `wh3_dlc25_unit_abilities_thunderburner` | `implemented (in-melee self)` | target | While the unit has an enemy in its sights: fire at it. | cd 30s · -1s · self · wind-up 1s |
| Thunderburner Upgraded `wh3_dlc25_unit_abilities_thunderburner_upgraded` | `implemented (in-melee self)` | target | While the unit has an enemy in its sights: fire at it. | cd 30s · -1s · self · wind-up 1s |
| Tide of Death `wh2_dlc16_hero_abilities_tide_of_death` | `implemented (enemy-ground: closest FIGHTING enemy)` | enemy_ground_melee | The CLOSEST enemy within the ability's 70% bound (35 m of its 50 m target_intercept_range) that is FIGHTING (in melee): the summon is placed on THAT ENEMY's ground (perform_special_ability_ground, fresh caster + fresh enemy, hold, pre-cast re-check). | cd 120s · 1s · friend/self · ×1 uses · **round 102 (2026-10-17):** implemented on the Gate of Khorne trigger per the user's summon ruling (harness 102) |
| Tide of Pox `wh2_dlc16_hero_abilities_tide_of_pox` | `implemented (enemy-ground: closest FIGHTING enemy)` | enemy_ground_melee | The CLOSEST enemy within the ability's 70% bound (35 m of its 50 m target_intercept_range) that is FIGHTING (in melee): the summon is placed on THAT ENEMY's ground (perform_special_ability_ground, fresh caster + fresh enemy, hold, pre-cast re-check). | cd 120s · 1s · friend/self · ×1 uses · **round 102 (2026-10-17):** implemented on the Gate of Khorne trigger per the user's summon ruling (harness 102) |
| Titanic Exultation `wh3_dlc27_army_abilities_decadence_in_praise_of_sla_i` | `excluded (auto: army-bar ability (standing rule 10))` | target | While the unit has an enemy in its sights: fire at it. | cd 180s · 10s · enemy unit · ×1 uses · wind-up 3s · army |
| Tomb Swarm `wh2_dlc09_army_abilities_tomb_swarm` | `excluded (auto: own-troop-damage AoE (friendly fire by design, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast at the target's position (placement policy needed). | cd 120s · 18s · ground · ×2 uses · wind-up 5s · army · triage-family: Own-troop-damage AoE |
| Transfix `wh3_dlc29_lord_abilities_transfix` | `excluded (auto: no effect text available (unsourceable))` | target | While the unit has an enemy in its sights: fire at it. | cd 120s · 25s · enemy unit · ×3 uses |
| Transformation of Kadon `wh3_dlc27_spell_bound_transformation_of_kadon` | `implemented (enemy-ground: closest FIGHTING enemy)` | enemy_ground_melee | The CLOSEST enemy within the ability's 70% bound (35 m of its 50 m target_intercept_range) that is FIGHTING (in melee): the summon is placed on THAT ENEMY's ground (perform_special_ability_ground, fresh caster + fresh enemy, hold, pre-cast re-check). | cd 45s · 1s · friend/self · ×1 uses · wind-up 5s · bound · **round 102 (2026-10-17):** implemented on the Gate of Khorne trigger per the user's summon ruling (harness 102) |
| Transformation of the Dragon `wh3_dlc24_lord_abilities_jade_dragon_human_form` | `excluded (impossible: no transform/shapechange support)` | target | While the unit has an enemy in its sights: fire at it. | cd 120s · 5s · self · wind-up 5s |
| Transformation of the Dragon `wh3_main_lord_abilities_iron_dragon_human_form` | `excluded (impossible: no transform/shapechange support)` | target | While the unit has an enemy in its sights: fire at it. | cd 120s · 5s · self · wind-up 5.3s |
| Transformation of the Dragon `wh3_main_lord_abilities_storm_dragon_human_form` | `excluded (impossible: no transform/shapechange support)` | target | While the unit has an enemy in its sights: fire at it. | cd 120s · 5s · self · wind-up 5.3s |
| Trickster's Shard `wh_main_item_abilities_tricksters_shard` | `implemented (enemy-targeted: enemy-ground area)` | enemy_ground | When an enemy unit within the 70% bound (350 m of 500 m) is in melee or under missile fire: `perform_special_ability_ground` places the area on the ENEMY's ground (fresh-handle route). | cd 90s · 16s · enemy ground · enemy-targeting mechanism (harness 97) |
| Tz'arkan `wh2_dlc14_lord_abilities_tzarkan` | `excluded (impossible: no transform/shapechange support)` | target | While the unit has an enemy in its sights: fire at it. | cd 0s · 0s · self · wind-up 3s |
| Tz'arkan `wh2_dlc14_lord_abilities_tzarkan_mp` | `excluded (impossible: no transform/shapechange support)` | target | While the unit has an enemy in its sights: fire at it. | cd 0s · 0s · self · wind-up 3s |
| Tz'arkan `wh2_dlc14_lord_abilities_tzarkan_snikch` | `excluded (impossible: no transform/shapechange support)` | target | While the unit has an enemy in its sights: fire at it. | cd 0s · 0s · self · wind-up 1.5s |
| Tz'arkan `wh2_dlc14_lord_abilities_tzarkan_spite` | `excluded (impossible: no transform/shapechange support)` | target | While the unit has an enemy in its sights: fire at it. | cd 0s · 0s · self · wind-up 3s |
| Tz'arkan `wh2_dlc14_lord_abilities_tzarkan_spite_mp` | `excluded (impossible: no transform/shapechange support)` | target | While the unit has an enemy in its sights: fire at it. | cd 0s · 0s · self · wind-up 3s |
| Tzcatli's Sanctum `wh2_dlc17_army_abilities_tzcatlis_sanctum` | `excluded (auto: army-bar ability (standing rule 10))` | target | While the unit has an enemy in its sights: cast on the ground under the target. | cd 60s · 5s · enemy ground · ×3 uses · wind-up 3s · army |
| Undeath from Above `wh3_dlc29_unit_abilities_undeath_from_above` | `excluded (auto: explosive / breath attack)` | target | While the unit has an enemy in its sights: fire at it. | cd 0.1s · 1s · self · ×1 uses |
| Undeath to All `wh3_dlc29_lord_abilities_raise_legion` | `implemented (enemy-ground: closest FIGHTING enemy)` | enemy_ground_melee | The CLOSEST enemy within the ability's 70% bound (52 m of its 75 m target_intercept_range) that is FIGHTING (in melee): the summon is placed on THAT ENEMY's ground (perform_special_ability_ground, fresh caster + fresh enemy, hold, pre-cast re-check). | cd 120s · 1s · ground · ×1 uses · wind-up 3s · **round 102 (2026-10-17):** implemented on the Gate of Khorne trigger per the user's summon ruling (harness 102) |
| Undeath to All Upgraded `wh3_dlc29_lord_abilities_raise_legion_upgraded` | `implemented (enemy-ground: closest FIGHTING enemy)` | enemy_ground_melee | The CLOSEST enemy within the ability's 70% bound (52 m of its 75 m target_intercept_range) that is FIGHTING (in melee): the summon is placed on THAT ENEMY's ground (perform_special_ability_ground, fresh caster + fresh enemy, hold, pre-cast re-check). | cd 120s · 1s · ground · ×1 uses · wind-up 3s · **round 102 (2026-10-17):** implemented on the Gate of Khorne trigger per the user's summon ruling (harness 102) |
| Unidentified Hydra Head `wh2_dlc10_quest_abilities_unidentified_hydra_head` | `excluded (auto: explosive / breath attack)` | target | While the unit has an enemy in its sights: fire at it. | cd 135s · 35s · self · ×3 uses · wind-up 2s |
| Unleash `wh3_dlc29_army_abilities_unleash` | `excluded (auto: army-bar ability (standing rule 10))` | target | While the unit has an enemy in its sights: cast on the ground under the target. | cd 60s · 1s · enemy ground · ×1 uses · wind-up 5s · army |
| Unleash the Winds `wh2_dlc15_army_abilities_unleash_the_winds` | `excluded (auto: army-bar ability (standing rule 10))` | target | While the unit has an enemy in its sights: fire at it. | cd 60s · 15s · self · army |
| Unspeakable Foulness `wh3_dlc25_unit_abilities_unspeakable_foulness` | `excluded (auto: explosive projectile)` | target | While the unit has an enemy in its sights: fire at it. | cd 60s · -1s · enemy unit · ×3 uses · wind-up 1.3s |
| Vindictive Glare `wh_dlc06_spell_bound_vindictive_glare` | `excluded (impossible: no enemy-unit read)` | target | While the unit has an enemy in its sights: fire at it. | cd 60s · -1s · enemy unit · ×4 uses · wind-up 1s · bound |
| Vine Dragon Scale `wh2_dlc15_item_abilities_vine_dragon_scale` | `excluded (auto: no effect text available (unsourceable))` | target | While the unit has an enemy in its sights: fire at it. | cd 120s · 14s · self |
| Vizier's Kanopi `wh3_dlc26_item_tmb_liche_priest_viziers_kanopi` | `implemented (enemy-ground: closest FIGHTING enemy)` | enemy_ground_melee | The CLOSEST enemy within the ability's 70% bound (35 m of its 50 m target_intercept_range) that is FIGHTING (in melee): the summon is placed on THAT ENEMY's ground (perform_special_ability_ground, fresh caster + fresh enemy, hold, pre-cast re-check). | cd 120s · 10s · ground/friend · ×1 uses · **round 102 (2026-10-17):** implemented on the Gate of Khorne trigger per the user's summon ruling (harness 102) |
| Void Pendulum `wh3_main_item_abilities_void_pendulum` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (140 m of 200 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 90s · 25s · enemy unit · ×3 uses · enemy-targeting mechanism (harness 97) |
| Volley of Dark Arrows `wh2_main_character_abilities_volley_of_dark_arrows` | `excluded (auto: explosive projectile)` | target | While the unit has an enemy in its sights: fire at it. | cd 90s · -1s · enemy unit · ×3 uses · wind-up 1s |
| Volley of High Arrows `wh2_main_character_abilities_volley_of_high_arrows` | `excluded (auto: explosive projectile)` | target | While the unit has an enemy in its sights: fire at it. | cd 90s · -1s · enemy unit · ×3 uses · wind-up 1s |
| Volley of Kurnous `wh2_dlc16_unit_abilities_volley_of_kurnous` | `excluded (impossible: no enemy-unit read)` | target | While the unit has an enemy in its sights: fire at it. | cd 90s · -1s · enemy unit · ×1 uses |
| Vorozheja's Foresight `wh3_dlc24_hero_abilities_vorozhejas_foresight` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (105 m of 150 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 120s · 25s · enemy unit · wind-up 3s · enemy-targeting mechanism (harness 97) |
| Wail of Malice `wh2_dlc14_unit_abilities_wail_of_malice` | `excluded (auto: own-troop-damage AoE (friendly fire by design, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: fire at it. | cd 90s · 7s · self · ×2 uses · triage-family: Own-troop-damage AoE |
| Wake Da Idol `wh3_main_item_abilities_zak_aloooog` | `implemented (enemy-ground: closest FIGHTING enemy)` | enemy_ground_melee | The CLOSEST enemy within the ability's 70% bound (35 m of its 50 m target_intercept_range) that is FIGHTING (in melee): the summon is placed on THAT ENEMY's ground (perform_special_ability_ground, fresh caster + fresh enemy, hold, pre-cast re-check). | cd 300s · 1s · friend/self · ×1 uses · **round 102 (2026-10-17):** implemented on the Gate of Khorne trigger per the user's summon ruling (harness 102) |
| Wake of Fire `wh2_main_unit_abilities_wake_of_fire` | `excluded (auto: explosive / breath attack)` | target | While the unit has an enemy in its sights: fire at it. | cd 0.1s · 0.1s · self · ×10 uses |
| Warp Gaze `wh_pro04_unit_abilities_warp_gaze` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (70 m of 100 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 90s · 12s · enemy unit · ×3 uses · enemy-targeting mechanism (harness 97) |
| Warp-Fireball `wh2_dlc14_spell_bound_warpfireball` | `excluded (impossible: no enemy-unit read)` | target | While the unit has an enemy in its sights: fire at it. | cd 60s · -1s · enemy unit · ×4 uses · bound |
| Warp-Quake `wh2_dlc14_unit_abilities_warp_quake` | `excluded (auto: own-troop-damage AoE (friendly fire by design, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: fire at it. | cd 90s · 17s · self · triage-family: Own-troop-damage AoE |
| Warpstiletto `wh3_dlc29_item_abilities_warpstiletto` | `implemented (enemy-targeted: in-melee / under-fire)` | enemy_unit | When an enemy unit within the 70% bound (70 m of 100 m) is in melee or under missile fire: cast at the ENEMY (unit hex, fresh-handle route). | cd 120s · 20s · enemy unit · ×2 uses · enemy-targeting mechanism (harness 97) |
| Warpstorm Scroll `wh2_main_item_abilities_warpstorm_scroll` | `excluded (auto: own-troop-damage AoE (friendly fire by design, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. | cd 60s · 29s · enemy ground · ×1 uses · triage-family: Own-troop-damage AoE |
| Watched by the Watcher `wh3_dlc24_character_abilities_watched_by_the_watcher` | `implemented (in-melee self)` | target | While the unit has an enemy in its sights: fire at it. | cd 120s · 60s · self · ×3 uses |
| Web of Shadows `wh2_main_weapon_abilities_web_of_shadows` | `excluded (auto: own-troop-damage AoE (friendly fire by design, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: fire at it. | cd 60s · 17s · self · ×1 uses · triage-family: Own-troop-damage AoE |
| Wind Bow `wh3_dlc24_item_abilities_wind_bow` | `excluded (impossible: no enemy-unit read)` | target | While the unit has an enemy in its sights: fire at it. | cd 120s · -1s · enemy unit · ×3 uses · wind-up 5s · item |
| Zefet-nebtar, the Mortis Blade `wh3_dlc29_item_abilities_zefet_nebtar_the_mortis_blade` | `excluded (auto: own-troop-damage AoE (friendly fire by design, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. | cd 120s · 1s · enemy ground · ×3 uses · wind-up 2s · item · triage-family: Own-troop-damage AoE |

### 3b. Friendly-fire-flagged (moved to the END of the list by design)

Area-damage abilities that can be aimed at or around your own troops (engine label `aoe*` / `aoe_bombardment` / `vortex*`
and target ground or travel as winds/breaths). Not proposed for auto-fire until the friendly-fire behaviour is field-proven;
when the questionnaire reaches them, the proposal below is the starting offer with an explicit FF note.

| Ability | Status | Group | Auto-activation proposal (FF — off by default) | Notes |
|---|---|---|---|---|
| Acorns of the Oak of Ages `wh2_dlc16_item_abilities_acorns_of_the_oak_of_ages` | `excluded (auto: placed / static area damage (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 120s · 12s · enemy ground · ×2 uses · wind-up 3s · triage-family: Placed / static area damage |
| Ancestral Rune of Grimnir `wh2_dlc17_army_abilities_ancestral_rune_of_grimnir` | `excluded (auto: bombardment / ground artillery (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast at the target's position (placement policy needed). (FF — keep off until proven) | cd 120s · 15s · ground · ×1 uses · wind-up 5s · army · triage-family: Bombardment / ground artillery |
| Arachneruption `wh2_dlc15_unit_abilities_arachneruption` | `excluded (auto: bombardment / ground artillery (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: fire at it. (FF — keep off until proven) | cd 90s · 2s · self · ×3 uses · triage-family: Bombardment / ground artillery |
| Arcane Vassal `wh2_main_character_abilities_arcane_vassal` | `excluded (auto: placed / static area damage (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: fire at it. (FF — keep off until proven) | cd 120s · 1s · friend · triage-family: Placed / static area damage |
| Arnzipal's Black Horror `wh2_dlc10_item_bound_arnizipals_black_horror` | `excluded (auto: vortex / wandering wind (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 120s · 16s · enemy ground · ×1 uses · wind-up 5s · bound · triage-family: Vortex / wandering wind |
| Assault of Stone `wh2_dlc10_item_bound_assault_of_stone` | `excluded (auto: bombardment / ground artillery (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 90s · 9s · enemy ground · ×1 uses · wind-up 3s · bound · triage-family: Bombardment / ground artillery |
| Asur Fire I `wh3_dlc27_army_abilities_asuryans_rage` | `excluded (auto: vortex / wandering wind (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 60s · 15s · enemy ground · ×3 uses · wind-up 3s · army · triage-family: Vortex / wandering wind |
| Asur Fire II `wh3_dlc27_army_abilities_asuryans_fury` | `excluded (auto: vortex / wandering wind (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 90s · 20s · enemy ground · ×3 uses · wind-up 3s · army · triage-family: Vortex / wandering wind |
| Asur Fire III `wh3_dlc27_army_abilities_asuryans_wrath` | `excluded (auto: vortex / wandering wind (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 120s · 25s · enemy ground · ×3 uses · wind-up 3s · army · triage-family: Vortex / wandering wind |
| Axe of Tor `wh3_main_weapon_abilities_axe_of_tor` | `excluded (auto: bombardment / ground artillery (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 90s · 4s · enemy ground · ×3 uses · wind-up 3s · triage-family: Bombardment / ground artillery |
| Bangstick `wh3_main_item_abilities_bangstick` | `excluded (auto: breath / cone damage (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 90s · 6s · enemy ground · ×3 uses · wind-up 3s · triage-family: Breath / cone damage |
| Banishment `wh3_main_spell_bound_banishment` | `excluded (auto: vortex / wandering wind (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 120s · 17s · enemy ground · ×1 uses · wind-up 5s · bound · triage-family: Vortex / wandering wind |
| Banishment `wh_dlc04_spell_bound_banishment` | `excluded (auto: vortex / wandering wind (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 120s · 17s · enemy ground · ×2 uses · wind-up 5s · bound · triage-family: Vortex / wandering wind |
| Banishment `wh_dlc04_spell_bound_banishment_innate` | `excluded (auto: vortex / wandering wind (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 120s · 17s · enemy ground · ×2 uses · wind-up 5s · bound · triage-family: Vortex / wandering wind |
| Befuddlement of Mischiefs `wh2_dlc16_character_abilities_befuddlement_of_mischiefs` | `excluded (auto: placed / static area damage (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 90s · 11s · enemy ground · ×3 uses · triage-family: Placed / static area damage |
| Bjuna Bombard `wh3_dlc25_army_abilities_bjuna_bombard` | `excluded (auto: bombardment / ground artillery (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast at the target's position (placement policy needed). (FF — keep off until proven) | cd 120s · 8s · ground · ×1 uses · wind-up 5s · army · triage-family: Bombardment / ground artillery |
| Black Dragon Egg `wh2_main_item_abilities_black_dragon_egg` | `excluded (auto: breath / cone damage (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 90s · 16s · enemy ground · ×3 uses · wind-up 3s · triage-family: Breath / cone damage |
| Blade of Khorne `wh3_main_army_abilities_blade_of_khorne` | `excluded (auto: placed / static area damage (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 120s · 8s · enemy ground · wind-up 5s · army · triage-family: Placed / static area damage |
| Blight Boil `wh3_dlc29_endgame_crisis_the_vermintide_enemy_clan_morbidus_pestilent_pustule_hidden` | `excluded (auto: placed / static area damage (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 60s · 1s · enemy ground · ×3 uses · wind-up 15s · army · triage-family: Placed / static area damage |
| Blight Boil `wh3_main_item_abilities_deaths_head` | `excluded (auto: placed / static area damage (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 120s · 1s · enemy ground · ×2 uses · wind-up 5s · bound · triage-family: Placed / static area damage |
| Bloodwrack Cauldron `wh2_main_army_abilities_bloodwrack_cauldron` | `excluded (auto: bombardment / ground artillery (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 60s · 7s · enemy ground · ×3 uses · wind-up 5s · army · triage-family: Bombardment / ground artillery |
| Blue Fire of Chaos `wh3_main_daemon_arms_abilities_blue_fire` | `excluded (auto: breath / cone damage (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast at the target's position (placement policy needed). (FF — keep off until proven) | cd 30s · 6s · ground · ×2 uses · triage-family: Breath / cone damage |
| Blue Fire of Chaos Upgraded `wh3_main_daemon_arms_abilities_blue_fire_upgraded` | `excluded (auto: breath / cone damage (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast at the target's position (placement policy needed). (FF — keep off until proven) | cd 30s · 6s · ground · ×4 uses · triage-family: Breath / cone damage |
| Boiling Cauldron `wh3_dlc26_army_abilities_boiling_cauldron` | `excluded (auto: placed / static area damage (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 120s · 6s · enemy ground · ×1 uses · wind-up 1.5s · army · triage-family: Placed / static area damage |
| Boiling Cauldron `wh3_dlc26_lord_abilities_boiling_cauldron` | `excluded (auto: placed / static area damage (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 120s · 6s · enemy ground · ×1 uses · wind-up 1.5s · triage-family: Placed / static area damage |
| Bolt of Change `wh3_main_army_abilities_bolt_of_change` | `excluded (impossible: no enemy-unit read)` | target | While the unit has an enemy in its sights: fire at it. (FF — keep off until proven) | cd 90s · 10s · enemy unit · wind-up 3s · army |
| Bolt of Spite `wh2_main_army_abilities_bolt_of_spite` | `excluded (impossible: no enemy-unit read)` | target | While the unit has an enemy in its sights: fire at it. (FF — keep off until proven) | cd 120s · 7s · enemy unit · ×3 uses · wind-up 5s · army |
| Bonecrusher `wh3_dlc26_spell_bound_bonecrusher` | `excluded (auto: bombardment / ground artillery (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 90s · 6s · enemy ground · ×1 uses · wind-up 3s · bound · triage-family: Bombardment / ground artillery |
| Bound Fiery Convocation `wh2_main_spell_bound_khaines_ring_of_fury` | `excluded (auto: vortex / wandering wind (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 120s · 10s · enemy ground · ×2 uses · wind-up 5s · bound · triage-family: Vortex / wandering wind |
| Brass Orb `wh2_dlc12_character_abilities_brass_orb` | `excluded (auto: placed / static area damage (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 90s · 13s · enemy ground · ×3 uses · wind-up 3s · triage-family: Placed / static area damage |
| Brass Orb `wh2_dlc12_character_abilities_brass_orb_tech_lab_doom_flayer` | `excluded (auto: placed / static area damage (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 90s · 13s · enemy ground · ×3 uses · wind-up 3s · triage-family: Placed / static area damage |
| Brass Orb Upgraded `wh2_dlc12_character_abilities_brass_orb_upgrade` | `excluded (auto: placed / static area damage (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 90s · 13s · enemy ground · ×3 uses · wind-up 3s · triage-family: Placed / static area damage |
| Brazen Cauldron `wh2_main_army_abilities_brazen_cauldron` | `excluded (auto: bombardment / ground artillery (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 60s · 7s · enemy ground · ×3 uses · wind-up 3s · army · triage-family: Bombardment / ground artillery |
| Bubonic Broadside `wh3_dlc29_army_abilities_pestilential_bombardment` | `excluded (auto: bombardment / ground artillery (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast at the target's position (placement policy needed). (FF — keep off until proven) | cd 90s · 5s · ground · ×2 uses · wind-up 5s · triage-family: Bombardment / ground artillery |
| Burning Alignment `wh2_dlc12_unit_abilities_burning_alignment` | `excluded (auto: vortex / wandering wind (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 120s · 12s · enemy ground · ×2 uses · wind-up 5s · triage-family: Vortex / wandering wind |
| Celestial Comet `wh3_main_mount_bound_celestial_comet` | `excluded (auto: bombardment / ground artillery (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 49s · 7s · enemy ground · ×2 uses · wind-up 5s · bound · triage-family: Bombardment / ground artillery |
| Celestial Intervention `wh3_main_army_abilities_celestial_intervention` | `excluded (auto: bombardment / ground artillery (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 120s · 7s · enemy ground · ×1 uses · wind-up 5s · army · triage-family: Bombardment / ground artillery |
| Celestial Lightning `wh3_main_mount_bound_celestial_lightning` | `excluded (auto: bombardment / ground artillery (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 42s · 4s · enemy ground · ×2 uses · wind-up 3s · bound · triage-family: Bombardment / ground artillery |
| Chain Lightning `wh_main_spell_bound_chain_lightning_ror` | `excluded (auto: placed / static area damage (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 60s · 20s · enemy ground · ×1 uses · wind-up 5s · bound · triage-family: Placed / static area damage |
| Chalice of Potions `wh_dlc07_item_abilities_chalice_of_potions` | `excluded (auto: bombardment / ground artillery (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 120s · 7s · enemy ground · ×2 uses · wind-up 5s · triage-family: Bombardment / ground artillery |
| Comet of Casandora `wh3_main_spell_bound_comet_of_casandora` | `excluded (auto: bombardment / ground artillery (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 120s · 7s · enemy ground · ×1 uses · wind-up 5s · bound · triage-family: Bombardment / ground artillery |
| Copious Phlegm `wh3_dlc27_qb_unit_abilities_copious_phlegm` | `excluded (not in wheel: boss-only unit)` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) |  cd 45s · 1s · enemy ground · triage-family: Placed / static area damage · **round 101 (2026-10-17):** boss-only - its ONLY grant path is `wh3_dlc27_nur_mon_toad_dragon_boss` (land_abil.tsv), a quest-battle boss variant; it never shipped in the mod. See §10.3. |
| Crackleblaze `wh3_main_item_abilities_crackleblaze` | `excluded (auto: placed / static area damage (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 90s · 1s · enemy ground · ×3 uses · triage-family: Placed / static area damage |
| Da Boss' Loons `wh2_dlc15_lord_abilities_da_boss_loons` | `excluded (auto: breath / cone damage (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 30s · 12s · enemy ground · ×2 uses · triage-family: Breath / cone damage |
| Diabolical Puppetry `wh3_pro10_army_abilities_diabolical_puppetry` | `excluded (auto: vortex / wandering wind (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 90s · 25s · enemy ground · wind-up 3s · army · triage-family: Vortex / wandering wind |
| Diabolical Puppetry `wh3_pro10_army_abilities_diabolical_puppetry_upgrade_1` | `excluded (auto: vortex / wandering wind (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 75s · 30s · enemy ground · wind-up 3s · army · triage-family: Vortex / wandering wind |
| Diabolical Puppetry `wh3_pro10_army_abilities_diabolical_puppetry_upgrade_2` | `excluded (auto: vortex / wandering wind (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 60s · 35s · enemy ground · wind-up 3s · army · triage-family: Vortex / wandering wind |
| Diabolical Puppetry `wh3_pro10_army_abilities_diabolical_puppetry_upgrade_3` | `excluded (auto: vortex / wandering wind (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 45s · 40s · enemy ground · wind-up 3s · army · triage-family: Vortex / wandering wind |
| Disembowelling Sweep `wh3_dlc29_unit_active_ripping_blades` | `excluded (auto: breath / cone damage (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 90s · 9s · enemy ground · wind-up 1s · triage-family: Breath / cone damage |
| Doom Diver Strike `wh2_dlc15_army_abilities_doom_diver_strike` | `excluded (auto: bombardment / ground artillery (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast at the target's position (placement policy needed). (FF — keep off until proven) | cd 90s · 6s · ground · ×5 uses · army · triage-family: Bombardment / ground artillery |
| Doom of Hashut `wh3_dlc23_army_abilities_doom_of_hashut` | `excluded (auto: bombardment / ground artillery (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 120s · 7s · enemy ground · ×1 uses · wind-up 5s · army · triage-family: Bombardment / ground artillery |
| Doomrocket `wh3_dlc29_endgame_crisis_the_vermintide_enemy_clan_skryre_doomrocket_hidden` | `excluded (auto: bombardment / ground artillery (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 120s · 5s · enemy ground · ×3 uses · wind-up 15s · army · triage-family: Bombardment / ground artillery |
| Dragon Ogre's Great Horn `wh_dlc08_item_abilities_great_horn_of_dragon_ogre` | `excluded (auto: bombardment / ground artillery (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 120s · 20s · enemy ground · ×2 uses · triage-family: Bombardment / ground artillery |
| Dragonship Assault `wh3_dlc27_army_abilities_dragonship_assault` | `excluded (auto: bombardment / ground artillery (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 60s · 6s · enemy ground · ×3 uses · wind-up 3s · army · triage-family: Bombardment / ground artillery |
| Dragonship Blitz `wh3_dlc27_army_abilities_dragonship_blitz` | `excluded (auto: bombardment / ground artillery (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 60s · 6s · enemy ground · ×3 uses · wind-up 3s · army · triage-family: Bombardment / ground artillery |
| Dragonship Volley `wh3_dlc27_army_abilities_dragonship_volley` | `excluded (auto: bombardment / ground artillery (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 60s · 6s · enemy ground · ×3 uses · wind-up 3s · army · triage-family: Bombardment / ground artillery |
| Dreadquake Battery `wh3_dlc23_army_abilities_tower_ballistics` | `excluded (auto: bombardment / ground artillery (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast at the target's position (placement policy needed). (FF — keep off until proven) | cd 90s · 4s · ground · ×1 uses · wind-up 5s · army · triage-family: Bombardment / ground artillery |
| Dreadquake Battery Upgraded `wh3_dlc23_army_abilities_tower_ballistics_upgraded_toz` | `excluded (auto: bombardment / ground artillery (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast at the target's position (placement policy needed). (FF — keep off until proven) | cd 90s · 4s · ground · ×1 uses · wind-up 5s · army · triage-family: Bombardment / ground artillery |
| Fiery Convocation `wh2_dlc10_quest_abilities_magic_fiery_convocation` | `excluded (not in wheel: boss-only unit)` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) |  cd 25s · 10s · enemy ground · wind-up 5s · triage-family: Vortex / wandering wind · **round 101 (2026-10-17):** boss-only - its ONLY grant path is `wh2_dlc10_nor_mon_phoenix_flamespyre_boss` (land_abil.tsv), a quest-battle boss variant; it never shipped in the mod. See §10.3. |
| Fiery Convocation `wh2_dlc10_spell_bound_magic_fiery_convocation` | `excluded (auto: vortex / wandering wind (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 120s · 10s · enemy ground · ×2 uses · wind-up 5s · bound · triage-family: Vortex / wandering wind |
| Fiery Ring of Thori `wh_main_item_abilities_fiery_ring_of_thori` | `excluded (auto: breath / cone damage (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 90s · 7s · enemy ground · ×3 uses · wind-up 1s · triage-family: Breath / cone damage |
| Fishy Breath `wh2_dlc15_character_abilities_fishy_breathe` | `excluded (auto: breath / cone damage (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 32s · 6s · enemy ground · ×3 uses · wind-up 0.5s · triage-family: Breath / cone damage |
| Flame & Shadow `wh3_dlc23_lord_abilities_flame_and_shadow` | `excluded (auto: bombardment / ground artillery (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 90s · 5s · enemy ground · ×2 uses · wind-up 3s · lord · triage-family: Bombardment / ground artillery |
| Flame Storm `wh2_dlc10_quest_abilities_flame_storm` | `excluded (not in wheel: boss-only unit)` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) |  cd 25s · 27s · enemy ground · wind-up 5s · triage-family: Vortex / wandering wind · **round 101 (2026-10-17):** boss-only - its ONLY grant path is `wh2_dlc10_nor_mon_phoenix_flamespyre_boss` (land_abil.tsv), a quest-battle boss variant; it never shipped in the mod. See §10.3. |
| Flame Storm `wh3_dlc20_spell_bound_flame_storm` | `excluded (auto: vortex / wandering wind (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 50s · 27s · enemy ground · ×1 uses · wind-up 5s · bound · triage-family: Vortex / wandering wind |
| Flame Storm `wh3_main_spell_bound_flame_storm` | `excluded (auto: vortex / wandering wind (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 120s · 27s · enemy ground · ×1 uses · wind-up 5s · bound · triage-family: Vortex / wandering wind |
| Flesh-eating Scarabs `wh3_dlc29_unit_abilities_flesh_eating_scarabs` | `excluded (auto: breath / cone damage (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast at the target's position (placement policy needed). (FF — keep off until proven) | cd 90s · 1s · ground · ×3 uses · wind-up 1s · triage-family: Breath / cone damage |
| Fly at da Smoke! `wh3_dlc26_army_abilities_fly_at_da_smoke` | `excluded (auto: bombardment / ground artillery (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 120s · 5s · enemy ground · ×3 uses · wind-up 1s · army · triage-family: Bombardment / ground artillery |
| Foot of Gork `wh3_dlc26_army_abilities_da_plan_foot_of_gork` | `excluded (auto: placed / static area damage (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 180s · 8s · enemy ground · ×3 uses · wind-up 5s · army · triage-family: Placed / static area damage |
| Frost Fang `wh3_main_weapon_abilities_frost_fang` | `excluded (auto: placed / static area damage (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 120s · 5s · enemy ground · ×2 uses · wind-up 5s · triage-family: Placed / static area damage |
| Gaze of Malice `wh2_main_lord_abilities_gaze_of_malice` | `excluded (auto: breath / cone damage (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 90s · 8s · enemy ground · ×3 uses · wind-up 3s · triage-family: Breath / cone damage |
| Gehenna's Golden Globe `wh3_dlc20_cataclysm_bound_gehennas_golden_globe` | `excluded (auto: vortex / wandering wind (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast at the target's position (placement policy needed). (FF — keep off until proven) | cd 120s · 12s · ground · ×1 uses · wind-up 5s · bound · triage-family: Vortex / wandering wind |
| Gehenna's Golden Globe `wh3_dlc27_cataclysm_bound_gehennas_golden_globe` | `excluded (auto: vortex / wandering wind (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast at the target's position (placement policy needed). (FF — keep off until proven) | cd 120s · 12s · ground · ×3 uses · wind-up 5s · bound · triage-family: Vortex / wandering wind |
| Gehenna's Golden Globe `wh3_pro10_cataclysm_metal_gehennas_golden_globe_bound` | `excluded (auto: vortex / wandering wind (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast at the target's position (placement policy needed). (FF — keep off until proven) | cd 120s · 12s · ground · ×2 uses · wind-up 5s · bound · triage-family: Vortex / wandering wind |
| Gehenna's Golden Hounds `wh3_dlc20_spell_bound_gehennas_golden_hounds` | `excluded (auto: vortex / wandering wind (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 45s · 13s · enemy ground · ×1 uses · wind-up 3s · bound · triage-family: Vortex / wandering wind |
| Gilded Horn of Galon Konook `wh2_main_item_bound_gilded_horn_of_galon_konook` | `excluded (auto: vortex / wandering wind (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 90s · 13s · enemy ground · ×2 uses · wind-up 3s · bound · triage-family: Vortex / wandering wind |
| Great Invocation of Sotek `wh2_dlc12_army_abilities_great_invocation_of_sotek` | `excluded (auto: vortex / wandering wind (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 120s · 6s · enemy ground · ×1 uses · wind-up 5s · army · triage-family: Vortex / wandering wind |
| Guns of Zharr `wh3_dlc23_army_abilities_guns_of_zharr` | `excluded (auto: vortex / wandering wind (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 60s · 4s · enemy ground · wind-up 2s · army · triage-family: Vortex / wandering wind |
| Hawk's Talon `wh_dlc05_weapon_abilities_hawks_talon` | `excluded (auto: bombardment / ground artillery (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 90s · -1s · enemy ground · ×3 uses · wind-up 3s · triage-family: Bombardment / ground artillery |
| Heaven's Gate `wh3_cp1_item_abilities_heavens_gate` | `excluded (auto: vortex / wandering wind (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast at the target's position (placement policy needed). (FF — keep off until proven) | cd 120s · -1s · ground · wind-up 2s · triage-family: Vortex / wandering wind |
| Hell Hammer `wh3_dlc23_spell_bound_hell_hammer` | `excluded (auto: vortex / wandering wind (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 50s · 4s · enemy ground · ×1 uses · wind-up 5s · bound · triage-family: Vortex / wandering wind |
| Hounds of Orion `wh_dlc05_lord_ablities_grey_wolves` | `excluded (auto: vortex / wandering wind (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 90s · 13s · enemy ground · ×3 uses · wind-up 3s · triage-family: Vortex / wandering wind |
| Inevitable Fate `wh3_pro10_army_abilities_inevitable_fate` | `excluded (auto: vortex / wandering wind (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: fire at it. (FF — keep off until proven) | cd 150s · 15s · friend · wind-up 3s · army · triage-family: Vortex / wandering wind |
| Inevitable Fate `wh3_pro10_army_abilities_inevitable_fate_upgrade_1` | `excluded (auto: vortex / wandering wind (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: fire at it. (FF — keep off until proven) | cd 120s · 20s · friend · wind-up 3s · army · triage-family: Vortex / wandering wind |
| Inevitable Fate `wh3_pro10_army_abilities_inevitable_fate_upgrade_2` | `excluded (auto: vortex / wandering wind (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: fire at it. (FF — keep off until proven) | cd 105s · 25s · friend · wind-up 3s · army · triage-family: Vortex / wandering wind |
| Inevitable Fate `wh3_pro10_army_abilities_inevitable_fate_upgrade_3` | `excluded (auto: vortex / wandering wind (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: fire at it. (FF — keep off until proven) | cd 90s · 30s · friend · wind-up 3s · army · triage-family: Vortex / wandering wind |
| Infernal Gateway `wh3_dlc20_spell_bound_infernal_gateway` | `excluded (auto: placed / static area damage (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 54s · 17s · enemy ground · ×1 uses · wind-up 6s · bound · triage-family: Placed / static area damage |
| Invocation of Ending `wh2_dlc15_army_abilities_invocation_of_ending` | `excluded (auto: placed / static area damage (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast at the target's position (placement policy needed). (FF — keep off until proven) | cd 120s · 12s · ground · army · triage-family: Placed / static area damage |
| Irresistible Plague! `wh3_dlc29_spell_bound_plague` | `excluded (auto: placed / static area damage (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 50s · 20s · enemy ground · ×1 uses · wind-up 5s · bound · triage-family: Placed / static area damage |
| Isha's Rain `wh2_dlc13_character_ability_ishas_rain` | `excluded (auto: bombardment / ground artillery (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 120s · 9s · enemy ground · ×3 uses · wind-up 3s · triage-family: Bombardment / ground artillery |
| Jade Lion's Breath `wh3_dlc24_unit_abilities_jade_dragons_breath` | `excluded (auto: breath / cone damage (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 30s · 3s · enemy ground · ×2 uses · wind-up 1s · bound · triage-family: Breath / cone damage |
| Jungle Swarm `wh2_dlc12_army_abilities_jungle_swarm` | `excluded (auto: vortex / wandering wind (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 90s · 26s · enemy ground · ×3 uses · wind-up 3s · army · triage-family: Vortex / wandering wind |
| Khaine's Flail `wh2_main_army_abilities_khaines_flail` | `excluded (auto: bombardment / ground artillery (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 60s · 4s · enemy ground · ×3 uses · wind-up 3s · army · triage-family: Bombardment / ground artillery |
| Khaine's Lash `wh2_main_army_abilities_khaines_lash` | `excluded (auto: bombardment / ground artillery (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 60s · 4s · enemy ground · ×3 uses · wind-up 1s · army · triage-family: Bombardment / ground artillery |
| Khaine's Scourge `wh2_main_army_abilities_khaines_scourge` | `excluded (auto: bombardment / ground artillery (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 60s · 4s · enemy ground · ×3 uses · wind-up 5s · army · triage-family: Bombardment / ground artillery |
| Khorne's Wrath `wh3_dlc26_army_abilities_khornes_wrath` | `excluded (impossible: no enemy-unit read)` | target | While the unit has an enemy in its sights: fire at it. (FF — keep off until proven) | cd 120s · 7s · enemy unit · army |
| Klad Brakak `wh2_dlc17_spell_bound_urannons_thunderbolt_upgraded` | `excluded (auto: bombardment / ground artillery (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 30s · 4s · enemy ground · wind-up 3s · triage-family: Bombardment / ground artillery |
| Kovsh Breath `wh3_main_item_abilities_kovsh_breath` | `excluded (auto: breath / cone damage (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 60s · 2s · enemy ground · ×3 uses · wind-up 1s · triage-family: Breath / cone damage |
| Lamprey's Bite `wh3_dlc24_unit_abilities_lampreys_bite` | `excluded (auto: placed / static area damage (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast at the target's position (placement policy needed). (FF — keep off until proven) | cd 90s · 1s · ground · ×5 uses · triage-family: Placed / static area damage |
| Lash of Slaanesh `wh3_dlc27_spell_bound_lash_of_slaanesh` | `excluded (auto: breath / cone damage (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 60s · 6s · enemy ground · ×2 uses · wind-up 1s · bound · triage-family: Breath / cone damage |
| Lash of Slaanesh `wh3_main_spell_bound_lash_of_slaanesh` | `excluded (auto: breath / cone damage (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 30s · 6s · enemy ground · ×2 uses · wind-up 1s · bound · triage-family: Breath / cone damage |
| Lash of Slaanesh `wh3_main_spell_bound_lash_of_slaanesh_keeper_of_secrets` | `excluded (auto: breath / cone damage (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 30s · 6s · enemy ground · ×2 uses · wind-up 1s · bound · triage-family: Breath / cone damage |
| Legionary Barrage `wh2_dlc09_army_abilities_barrage_of_the_legion` | `excluded (auto: vortex / wandering wind (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 90s · 4s · enemy ground · ×3 uses · wind-up 3s · army · triage-family: Vortex / wandering wind |
| Lesser Banishment `wh2_dlc17_spell_bound_lesser_banishment` | `excluded (auto: vortex / wandering wind (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 120s · 8s · enemy ground · ×1 uses · wind-up 5s · bound · triage-family: Vortex / wandering wind |
| Lesser Chain Lightning `wh2_dlc17_spell_bound_lesser_chain_lightning` | `excluded (auto: vortex / wandering wind (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 120s · 10s · enemy ground · ×1 uses · wind-up 5s · bound · triage-family: Vortex / wandering wind |
| Lesser Doombolt `wh2_dlc10_spell_bound_lesser_doombolt` | `excluded (impossible: no enemy-unit read)` | target | While the unit has an enemy in its sights: fire at it. (FF — keep off until proven) | cd 90s · 7s · enemy unit · ×2 uses · wind-up 3s · bound |
| Lightning Strike `wh3_dlc29_unit_abilities_lightning_strike` | `excluded (auto: bombardment / ground artillery (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 42s · 4s · enemy ground · ×2 uses · wind-up 3s · bound · triage-family: Bombardment / ground artillery |
| Lord of the Storm `wh_main_lord_abilities_lord_of_the_storm` | `excluded (auto: bombardment / ground artillery (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 90s · 11s · enemy ground · ×3 uses · wind-up 1s · triage-family: Bombardment / ground artillery |
| Magma Storm `wh3_dlc20_cataclysm_bound_magma_storm` | `excluded (auto: placed / static area damage (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast at the target's position (placement policy needed). (FF — keep off until proven) | cd 120s · 12s · ground · ×1 uses · wind-up 5s · bound · triage-family: Placed / static area damage |
| Magma Storm `wh3_dlc27_cataclysm_bound_magma_storm` | `excluded (auto: placed / static area damage (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast at the target's position (placement policy needed). (FF — keep off until proven) | cd 120s · 12s · ground · ×3 uses · wind-up 5s · bound · triage-family: Placed / static area damage |
| Magma Storm `wh3_pro10_cataclysm_fire_magma_storm_bound` | `excluded (auto: placed / static area damage (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast at the target's position (placement policy needed). (FF — keep off until proven) | cd 120s · 12s · ground · ×2 uses · wind-up 5s · bound · triage-family: Placed / static area damage |
| Man the Cannons! `wh2_dlc13_army_abilities_amber_bow_cannons` | `excluded (auto: vortex / wandering wind (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 60s · 4s · enemy ground · wind-up 3s · army · triage-family: Vortex / wandering wind |
| Master of Lightning `wh3_dlc29_spell_bound_warp_lightning` | `excluded (auto: bombardment / ground artillery (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 30s · 5s · enemy ground · ×3 uses · wind-up 1s · bound · triage-family: Bombardment / ground artillery |
| Master Rune of Immolation `wh2_dlc17_rune_abilities_master_rune_of_immolation` | `excluded (auto: bombardment / ground artillery (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: fire at it. (FF — keep off until proven) | cd 30s · -1s · self · triage-family: Bombardment / ground artillery |
| Master Rune of Wrath & Ruin `wh_dlc06_rune_abilities_master_rune_of_wrath_and_ruin` | `excluded (auto: placed / static area damage (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 180s · 10s · enemy ground · wind-up 3s · rune · triage-family: Placed / static area damage |
| Meteor Strike `wh3_dlc29_unit_abilities_meteor_strike` | `excluded (auto: bombardment / ground artillery (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 49s · 7s · enemy ground · ×3 uses · wind-up 5s · bound · triage-family: Bombardment / ground artillery |
| Nemesis Crown `wh3_dlc25_lord_abilities_nemesis_crown` | `excluded (auto: bombardment / ground artillery (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 120s · 10s · enemy ground · wind-up 6s · triage-family: Bombardment / ground artillery |
| Nightmaw `wh3_dlc27_character_abilities_nightmaw` | `excluded (auto: vortex / wandering wind (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 45s · 5s · enemy ground · ×3 uses · wind-up 3s · triage-family: Vortex / wandering wind |
| Norse Roar `wh2_dlc11_army_abilities_norse_roar` | `excluded (auto: vortex / wandering wind (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 90s · 4s · enemy ground · ×2 uses · wind-up 3s · army · triage-family: Vortex / wandering wind |
| Pandemicium `wh3_dlc25_army_abilities_pandemicium` | `excluded (auto: bombardment / ground artillery (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast at the target's position (placement policy needed). (FF — keep off until proven) | cd 120s · 4s · ground · ×1 uses · wind-up 3s · army · triage-family: Bombardment / ground artillery |
| Pestilent Breath `wh2_main_mount_bound_pestilent_breath` | `excluded (auto: breath / cone damage (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 60s · 8s · enemy ground · wind-up 1s · triage-family: Breath / cone damage |
| Pestilent Breath `wh3_main_spell_bound_pestilent_breath` | `excluded (auto: breath / cone damage (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 60s · 8s · enemy ground · ×4 uses · wind-up 1s · bound · triage-family: Breath / cone damage |
| Piercing Bolts of Burning `wh_main_spell_bound_piercing_bolts_of_burning` | `excluded (auto: bombardment / ground artillery (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 120s · 8s · enemy ground · ×4 uses · bound · triage-family: Bombardment / ground artillery |
| Pigeon Bomb `wh3_dlc25_character_abilities_pigeon_bomb` | `excluded (auto: bombardment / ground artillery (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 120s · 12s · enemy ground · ×3 uses · triage-family: Bombardment / ground artillery |
| Pink Fire of Tzeentch `wh3_dlc20_spell_bound_pink_fire_of_tzeentch` | `excluded (auto: breath / cone damage (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 30s · 2s · enemy ground · ×2 uses · wind-up 1s · bound · triage-family: Breath / cone damage |
| Pink Fire of Tzeentch `wh3_main_spell_tzeentch_pink_fire_of_tzeentch_bound` | `excluded (auto: breath / cone damage (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 30s · 2s · enemy ground · ×2 uses · wind-up 1s · bound · triage-family: Breath / cone damage |
| Pit of Shades `wh3_dlc27_spell_bound_pit_of_shades` | `excluded (auto: placed / static area damage (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 120s · 13s · enemy ground · ×1 uses · wind-up 6s · bound · triage-family: Placed / static area damage |
| Pit of Shades `wh3_main_spell_bound_pit_of_shades` | `excluded (auto: placed / static area damage (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 120s · 13s · enemy ground · ×1 uses · wind-up 6s · bound · triage-family: Placed / static area damage |
| Pit of Shades `wh_dlc05_spell_shadow_pit_of_shades_bound` | `excluded (auto: placed / static area damage (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 49s · 13s · enemy ground · ×1 uses · wind-up 6s · bound · triage-family: Placed / static area damage |
| Plaguemaster `wh3_dlc29_spell_bound_plaguemaster` | `excluded (auto: placed / static area damage (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 50s · 20s · enemy ground · ×2 uses · wind-up 5s · bound · triage-family: Placed / static area damage |
| Rod of the Storm `wh2_dlc11_army_abilities_rod_of_the_storm` | `excluded (auto: bombardment / ground artillery (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 90s · 4s · enemy ground · ×3 uses · wind-up 3s · army · triage-family: Bombardment / ground artillery |
| Rod of the Storm `wh2_main_spell_bound_rod_of_the_storm` | `excluded (auto: bombardment / ground artillery (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 90s · 4s · enemy ground · ×3 uses · wind-up 3s · bound · triage-family: Bombardment / ground artillery |
| Rod of Torment `wh3_dlc20_item_abilities_rod_of_torment` | `excluded (impossible: no enemy-unit read)` | target | While the unit has an enemy in its sights: fire at it. (FF — keep off until proven) | cd 90s · 7s · enemy unit · ×3 uses · wind-up 3s · bound |
| Rubric of Dark Dimensions `wh2_main_spell_bound_rubric_of_dark_dimensions` | `excluded (auto: placed / static area damage (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 90s · 13s · enemy ground · ×2 uses · wind-up 6s · bound · triage-family: Placed / static area damage |
| Rune of Wrath & Ruin `wh_main_rune_abilities_rune_of_wrath_and_ruin` | `excluded (auto: placed / static area damage (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 120s · 10s · enemy ground · wind-up 3s · rune · triage-family: Placed / static area damage |
| Sandstorm `wh2_dlc09_lord_abilities_sand_storm` | `excluded (auto: vortex / wandering wind (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 90s · 14s · enemy ground · ×3 uses · wind-up 3s · triage-family: Vortex / wandering wind |
| Sartosa Grapeshot `wh2_dlc11_army_abilities_sartosa_grapeshot` | `excluded (auto: breath / cone damage (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 90s · 6s · enemy ground · ×2 uses · wind-up 1s · army · triage-family: Breath / cone damage |
| Sceptre of Stone `wh2_dlc10_item_abilities_sceptre_of_stone` | `excluded (auto: bombardment / ground artillery (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 90s · 9s · enemy ground · ×2 uses · wind-up 5s · triage-family: Bombardment / ground artillery |
| Scorch `wh2_main_mount_bound_scorch` | `excluded (auto: breath / cone damage (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 90s · 12s · enemy ground · wind-up 3s · triage-family: Breath / cone damage |
| Seafang `wh_dlc08_lord_abilities_seafang` | `excluded (auto: vortex / wandering wind (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 90s · 8s · enemy ground · ×3 uses · wind-up 4s · triage-family: Vortex / wandering wind |
| Searing Doom `wh3_twa08_spell_bound_searing_doom` | `excluded (auto: bombardment / ground artillery (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 60s · 8s · enemy ground · ×2 uses · wind-up 1s · bound · triage-family: Bombardment / ground artillery |
| Shadows of Anlec `wh2_main_army_abilities_shadows_of_anlec` | `excluded (auto: breath / cone damage (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 60s · 8s · enemy ground · ×3 uses · wind-up 1s · army · triage-family: Breath / cone damage |
| Shatter `wh2_dlc13_character_ability_shatter` | `excluded (auto: breath / cone damage (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 120s · 5s · enemy ground · ×3 uses · wind-up 1s · triage-family: Breath / cone damage |
| Shatterstone `wh2_dlc17_army_abilities_shatterstone` | `excluded (auto: placed / static area damage (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 45s · 1s · enemy ground · ×2 uses · wind-up 5s · army · triage-family: Placed / static area damage |
| Siegebreaker `wh3_main_weapon_abilities_siegebreaker` | `excluded (auto: placed / static area damage (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 120s · 1s · enemy ground · ×3 uses · wind-up 5s · triage-family: Placed / static area damage |
| Simmering Pot `wh3_dlc26_lord_abilities_simmering_pot` | `excluded (auto: placed / static area damage (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 90s · 6s · enemy ground · ×1 uses · wind-up 1.5s · triage-family: Placed / static area damage |
| Skabscrath `wh_main_weapon_abilities_skabscrath` | `excluded (auto: breath / cone damage (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 90s · 17s · enemy ground · ×3 uses · triage-family: Breath / cone damage |
| Skurvy Guns `wh3_dlc29_endgame_crisis_the_vermintide_enemy_clan_skurvy_guns_hidden` | `excluded (auto: vortex / wandering wind (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 75s · 4s · enemy ground · ×3 uses · wind-up 15s · army · triage-family: Vortex / wandering wind |
| Sky Cauldron `wh2_main_army_abilities_sky_cauldron` | `excluded (auto: bombardment / ground artillery (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 60s · 7s · enemy ground · ×3 uses · wind-up 1s · army · triage-family: Bombardment / ground artillery |
| Slicing Shards `wh3_dlc20_spell_bound_slicing_shards` | `excluded (auto: bombardment / ground artillery (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 48s · 9s · enemy ground · ×1 uses · wind-up 5s · bound · triage-family: Bombardment / ground artillery |
| Sotek's Sanctum `wh2_dlc17_army_abilities_soteks_sanctum` | `excluded (auto: vortex / wandering wind (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 90s · 26s · enemy ground · ×3 uses · wind-up 3s · army · triage-family: Vortex / wandering wind |
| Soul Rain `wh2_main_army_abilities_soul_rain` | `excluded (auto: bombardment / ground artillery (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 60s · 9s · enemy ground · ×3 uses · wind-up 1s · army · triage-family: Bombardment / ground artillery |
| Soul Storm `wh2_main_army_abilities_soul_storm` | `excluded (auto: bombardment / ground artillery (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 60s · 9s · enemy ground · ×3 uses · wind-up 5s · army · triage-family: Bombardment / ground artillery |
| Soul Torrent `wh2_main_army_abilities_soul_torrent` | `excluded (auto: bombardment / ground artillery (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 60s · 9s · enemy ground · ×3 uses · wind-up 3s · army · triage-family: Bombardment / ground artillery |
| Soul-slaying Hunger `wh3_dlc29_unit_abilities_soul_slaying_hunger` | `excluded (auto: vortex / wandering wind (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 120s · 20s · enemy ground · ×1 uses · wind-up 5s · triage-family: Vortex / wandering wind |
| Spirit Barrage `wh3_dlc25_army_abilities_spirit_barrage` | `excluded (impossible: no enemy-unit read)` | target | While the unit has an enemy in its sights: fire at it. (FF — keep off until proven) | cd 120s · 10s · enemy unit · ×1 uses · wind-up 5s · army |
| Stoneshaker `wh3_main_army_abilities_stoneshaker` | `excluded (auto: placed / static area damage (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 120s · 1s · enemy ground · ×3 uses · wind-up 1s · army · triage-family: Placed / static area damage |
| Storm of Fire `wh3_main_army_abilities_storm_of_fire` | `excluded (auto: bombardment / ground artillery (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 120s · 27s · enemy ground · wind-up 5s · army · triage-family: Bombardment / ground artillery |
| Storm of the Night `wh2_dlc11_lord_abilities_storm_of_the_night` | `excluded (impossible: no enemy-unit read)` | target | While the unit has an enemy in its sights: fire at it. (FF — keep off until proven) | cd 90s · 22s · enemy unit · ×3 uses |
| Storm of Xholankha `wh2_dlc13_army_abilities_storm_of_xholankha_upgraded` | `excluded (auto: vortex / wandering wind (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 90s · 30s · enemy ground · ×2 uses · wind-up 5s · army · triage-family: Vortex / wandering wind |
| Stream of Corruption `wh3_dlc20_spell_bound_stream_of_corruption` | `excluded (auto: breath / cone damage (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 29s · 3s · enemy ground · ×2 uses · wind-up 1s · bound · triage-family: Breath / cone damage |
| Stream of Corruption `wh3_main_spell_nurgle_stream_of_corruption_bound` | `excluded (auto: breath / cone damage (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 29s · 3s · enemy ground · ×2 uses · wind-up 1s · bound · triage-family: Breath / cone damage |
| Sunfang `wh2_main_weapon_abilities_sunfang` | `excluded (auto: breath / cone damage (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 120s · 17s · enemy ground · wind-up 5s · triage-family: Breath / cone damage |
| Sword of Khaine `wh2_dlc10_weapon_abilities_sword_of_khaine` | `excluded (auto: vortex / wandering wind (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 120s · 11s · enemy ground · triage-family: Vortex / wandering wind |
| Tempest `wh3_dlc27_army_high_magic_tempest` | `excluded (impossible: no enemy-unit read)` | target | While the unit has an enemy in its sights: fire at it. (FF — keep off until proven) | cd 44s · 17s · enemy unit · ×2 uses · wind-up 3s · army |
| Tempest of Blue Flame `wh3_pro10_army_abilities_tempest_of_blue_flame` | `excluded (auto: vortex / wandering wind (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast at the target's position (placement policy needed). (FF — keep off until proven) | cd 90s · 15s · ground · wind-up 3s · army · triage-family: Vortex / wandering wind |
| Tempest of Blue Flame `wh3_pro10_army_abilities_tempest_of_blue_flame_upgrade_1` | `excluded (auto: vortex / wandering wind (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast at the target's position (placement policy needed). (FF — keep off until proven) | cd 75s · 20s · ground · wind-up 3s · army · triage-family: Vortex / wandering wind |
| Tempest of Blue Flame `wh3_pro10_army_abilities_tempest_of_blue_flame_upgrade_2` | `excluded (auto: vortex / wandering wind (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast at the target's position (placement policy needed). (FF — keep off until proven) | cd 60s · 25s · ground · wind-up 3s · army · triage-family: Vortex / wandering wind |
| Tempest of Blue Flame `wh3_pro10_army_abilities_tempest_of_blue_flame_upgrade_3` | `excluded (auto: vortex / wandering wind (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast at the target's position (placement policy needed). (FF — keep off until proven) | cd 45s · 30s · ground · wind-up 3s · army · triage-family: Vortex / wandering wind |
| The Abyssal Swarm `wh3_dlc29_spell_bound_undeath_the_abyssal_swarm` | `excluded (auto: vortex / wandering wind (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 42s · 30s · enemy ground · ×2 uses · wind-up 3s · bound · triage-family: Vortex / wandering wind |
| The Bow of Loren `wh_dlc05_weapon_abilities_the_bow_of_loren` | `excluded (auto: bombardment / ground artillery (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 60s · -1s · enemy ground · wind-up 3s · triage-family: Bombardment / ground artillery |
| The Burning Head `wh3_dlc25_spell_bound_fire_the_burning_head` | `excluded (auto: vortex / wandering wind (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 90s · 20s · enemy ground · ×1 uses · wind-up 3s · bound · triage-family: Vortex / wandering wind |
| The Burning Head `wh3_dlc29_spell_bound_fire_skull_of_flaming_death` | `excluded (auto: vortex / wandering wind (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 90s · 20s · enemy ground · ×3 uses · wind-up 3s · bound · triage-family: Vortex / wandering wind |
| The Dreaded Thirteenth Spell `wh3_dlc29_spell_bound_the_dreaded_thirteenth` | `implemented (closest non-commander enemy in melee, enemy ground)` | enemy_melee_noncommander | ANY enemy within the ability's 70% bound (70 m of its 100 m target_intercept_range) that is IN MELEE and is NOT a Lord or Hero; the closest wins; the explosion + summon is placed on THAT ENEMY's ground. | cd 52s · 13s · enemy ground · ×1 uses · wind-up 5s · bound · triage-family: Bombardment / ground artillery · **round 102 (2026-10-17):** implemented per the user's ruling for this key (harness 102) |
| The Dreaded Thirteenth Spell `wh3_dlc29_spell_bound_the_dreaded_thirteenth_1` | `implemented (closest non-commander enemy in melee, enemy ground)` | enemy_melee_noncommander | ANY enemy within the ability's 70% bound (70 m of its 100 m target_intercept_range) that is IN MELEE and is NOT a Lord or Hero; the closest wins; the explosion + summon is placed on THAT ENEMY's ground. | cd 52s · 13s · enemy ground · ×1 uses · wind-up 5s · bound · triage-family: Bombardment / ground artillery · **round 102 (2026-10-17):** implemented per the user's ruling for this key (harness 102) |
| The Dreaded Thirteenth Spell `wh3_dlc29_spell_bound_the_dreaded_thirteenth_thanquol` | `implemented (closest non-commander enemy in melee, enemy ground)` | enemy_melee_noncommander | ANY enemy within the ability's 70% bound (70 m of its 100 m target_intercept_range) that is IN MELEE and is NOT a Lord or Hero; the closest wins; the explosion + summon is placed on THAT ENEMY's ground. | cd 52s · 13s · enemy ground · ×1 uses · wind-up 5s · bound · triage-family: Bombardment / ground artillery · **round 102 (2026-10-17):** implemented per the user's ruling for this key (harness 102) |
| The Dreaded Thirteenth Spell `wh3_dlc29_spell_bound_the_dreaded_thirteenth_thanquol_1` | `implemented (closest non-commander enemy in melee, enemy ground)` | enemy_melee_noncommander | ANY enemy within the ability's 70% bound (70 m of its 100 m target_intercept_range) that is IN MELEE and is NOT a Lord or Hero; the closest wins; the explosion + summon is placed on THAT ENEMY's ground. | cd 52s · 13s · enemy ground · ×1 uses · wind-up 5s · bound · triage-family: Bombardment / ground artillery · **round 102 (2026-10-17):** implemented per the user's ruling for this key (harness 102) |
| The Dwellers Below `wh3_main_spell_bound_the_dwellers_below` | `excluded (auto: vortex / wandering wind (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 120s · 15s · enemy ground · ×1 uses · wind-up 5s · bound · triage-family: Vortex / wandering wind |
| The Dwellers Below `wh_dlc08_spell_bound_the_dwellers_below` | `excluded (auto: vortex / wandering wind (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 120s · 15s · enemy ground · ×2 uses · wind-up 5s · bound · triage-family: Vortex / wandering wind |
| The Gem of Sunfire `wh2_main_spell_bound_the_gem_of_sunfire` | `excluded (auto: vortex / wandering wind (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 90s · 26s · enemy ground · ×1 uses · wind-up 5s · bound · triage-family: Vortex / wandering wind |
| The Hammer of Smednir `wh3_dlc23_item_abilities_hammer_of_smednir` | `excluded (auto: placed / static area damage (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 120s · 10s · enemy ground · ×3 uses · wind-up 3s · triage-family: Placed / static area damage |
| The Matterless Earth `wh3_dlc27_army_abilities_eternal_dance_tempo_3_carver_of_ways` | `excluded (auto: vortex / wandering wind (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast at the target's position (placement policy needed). (FF — keep off until proven) | cd 120s · 10s · ground · ×1 uses · wind-up 5s · army · triage-family: Vortex / wandering wind |
| The Penumbral Pendulum `wh3_dlc20_spell_bound_the_penumbral_pendulum` | `excluded (auto: vortex / wandering wind (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 40s · 2s · enemy ground · ×1 uses · wind-up 3s · bound · triage-family: Vortex / wandering wind |
| The Purple Eclipse `wh3_dlc25_army_abilities_purple_eclipse` | `excluded (auto: vortex / wandering wind (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast at the target's position (placement policy needed). (FF — keep off until proven) | cd 120s · 10s · ground · ×1 uses · wind-up 5s · army · triage-family: Vortex / wandering wind |
| The Purple Sun of Xereus `wh2_dlc11_spell_bound_the_purple_sun_of_xereus` | `excluded (auto: vortex / wandering wind (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 120s · 11s · enemy ground · ×2 uses · wind-up 5s · bound · triage-family: Vortex / wandering wind |
| The Ruination of Cities `wh2_main_lord_abilities_the_ruination_of_cities` | `excluded (auto: vortex / wandering wind (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 120s · 7s · enemy ground · ×2 uses · wind-up 5s · triage-family: Vortex / wandering wind |
| The Solid Airs `wh3_dlc27_army_abilities_eternal_dance_tempo_3_tempest_of_depravity` | `excluded (auto: vortex / wandering wind (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast at the target's position (placement policy needed). (FF — keep off until proven) | cd 120s · 12s · ground · ×1 uses · wind-up 5s · army · triage-family: Vortex / wandering wind |
| The Spear Slaupnir `wh3_dlc20_weapon_abilities_the_spear_slaupnir` | `excluded (auto: breath / cone damage (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 120s · 2s · enemy ground · ×2 uses · wind-up 3s · triage-family: Breath / cone damage |
| Thorsen's Thunderstorm `wh3_dlc20_cataclysm_bound_thorsens_thunderstorm` | `excluded (auto: bombardment / ground artillery (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast at the target's position (placement policy needed). (FF — keep off until proven) | cd 120s · 31s · ground · ×1 uses · wind-up 5s · bound · triage-family: Bombardment / ground artillery |
| Thorsen's Thunderstorm `wh3_dlc27_cataclysm_bound_thorsens_thunderstorm` | `excluded (auto: bombardment / ground artillery (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast at the target's position (placement policy needed). (FF — keep off until proven) | cd 120s · 31s · ground · ×3 uses · wind-up 5s · bound · triage-family: Bombardment / ground artillery |
| Thunder Charge `wh3_main_army_abilities_thunder_charge` | `excluded (auto: vortex / wandering wind (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 120s · 6s · enemy ground · ×2 uses · wind-up 3s · army · triage-family: Vortex / wandering wind |
| Tidecall `wh2_dlc11_spell_bound_tidecall` | `excluded (auto: breath / cone damage (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 60s · 2s · enemy ground · ×4 uses · wind-up 1s · triage-family: Breath / cone damage |
| Tome of Furion `wh2_main_spell_bound_tome_of_furion` | `excluded (impossible: no enemy-unit read)` | target | While the unit has an enemy in its sights: fire at it. (FF — keep off until proven) | cd 60s · 7s · enemy unit · ×4 uses · wind-up 5s · bound |
| Tyrant's Talon `wh3_cp1_weapon_abilities_tyrants_talon` | `excluded (auto: vortex / wandering wind (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: fire at it. (FF — keep off until proven) | cd 120s · 27s · self · weapon · triage-family: Vortex / wandering wind |
| Urannon's Thunderbolt `wh2_dlc17_spell_bound_urannons_thunderbolt` | `excluded (auto: bombardment / ground artillery (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 90s · 4s · enemy ground · ×2 uses · wind-up 3s · bound · triage-family: Bombardment / ground artillery |
| Vaul's Hammer `wh2_main_army_abilities_vauls_hammer` | `excluded (auto: placed / static area damage (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 120s · 1s · enemy ground · ×2 uses · wind-up 5s · army · triage-family: Placed / static area damage |
| Vile Entropy `wh2_dlc17_army_abilities_vile_entropy` | `excluded (auto: placed / static area damage (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 90s · 20s · enemy ground · ×2 uses · wind-up 5s · army · triage-family: Placed / static area damage |
| Viletide `wh_dlc03_spell_bound_viletide` | `excluded (auto: placed / static area damage (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 60s · 3s · enemy ground · ×4 uses · wind-up 3s · bound · triage-family: Placed / static area damage |
| Viletide Upgraded `wh2_dlc17_army_abilities_viletide` | `excluded (auto: placed / static area damage (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 90s · 3s · enemy ground · ×2 uses · wind-up 3s · army · triage-family: Placed / static area damage |
| Vortical Blast `wh2_main_army_abilities_vortic_blast` | `excluded (auto: placed / static area damage (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 30s · 5s · enemy ground · army · triage-family: Placed / static area damage |
| Wall of Wind & Fire `wh3_main_spell_bound_wall_of_wind_and_fire` | `excluded (auto: vortex / wandering wind (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 90s · 25s · enemy ground · ×2 uses · wind-up 3s · bound · triage-family: Vortex / wandering wind |
| Wand of the Kharaidon `wh2_main_spell_bound_wand_of_the_kharaidon` | `excluded (impossible: no enemy-unit read)` | target | While the unit has an enemy in its sights: fire at it. (FF — keep off until proven) | cd 120s · 7s · enemy unit · ×2 uses · wind-up 5s · bound |
| Warp Junction `wh3_dlc29_lord_abilities_warp_junction` | `excluded (auto: placed / static area damage (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 120s · 14s · enemy ground · ×2 uses · wind-up 3s · triage-family: Placed / static area damage |
| Warp Lightning Rod `wh2_dlc16_unit_abilities_warp_lightning_rod` | `excluded (auto: bombardment / ground artillery (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: fire at it. (FF — keep off until proven) | cd 60s · 5s · self · ×3 uses · wind-up 1s · triage-family: Bombardment / ground artillery |
| Warpstorm Doomrocket `wh2_dlc12_army_abilities_warpstorm_doomrocket` | `excluded (auto: bombardment / ground artillery (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 45s · 7s · enemy ground · ×1 uses · wind-up 5s · army · triage-family: Bombardment / ground artillery |
| Warpstorm Doomrocket `wh2_dlc12_army_abilities_warpstorm_doomrocket_upgraded` | `excluded (auto: bombardment / ground artillery (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 45s · 7s · enemy ground · ×1 uses · wind-up 5s · army · triage-family: Bombardment / ground artillery |
| Warpstorm Doomrocket `wh3_dlc24_tze_changeling_theatre_scheme_grand_cathay_doom_rocket` | `excluded (auto: bombardment / ground artillery (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 0s · 7s · enemy ground · ×3 uses · wind-up 5s · army · triage-family: Bombardment / ground artillery |
| Wind Blast `wh2_dlc11_spell_bound_wind_blast` | `excluded (auto: breath / cone damage (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 60s · 2s · enemy ground · ×4 uses · wind-up 1s · triage-family: Breath / cone damage |
| Wind of Death `wh2_dlc15_spell_bound_wind_of_death` | `excluded (auto: vortex / wandering wind (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 120s · 5s · enemy ground · ×1 uses · wind-up 5s · bound · triage-family: Vortex / wandering wind |
| Winged Staff `wh2_main_weapon_bound_winged_staff` | `excluded (auto: placed / static area damage (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 60s · 7s · enemy ground · ×4 uses · bound · triage-family: Placed / static area damage |
| Wolf's Howl `wh3_main_weapon_abilities_the_traitors_sword` | `excluded (impossible: no enemy-unit read)` | target | While the unit has an enemy in its sights: fire at it. (FF — keep off until proven) | cd 90s · 10s · enemy unit · ×3 uses |
| Wraith Storm `wh2_dlc11_army_abilities_wraith_storm` | `excluded (impossible: no enemy-unit read)` | target | While the unit has an enemy in its sights: fire at it. (FF — keep off until proven) | cd 90s · 9s · enemy unit · ×3 uses · wind-up 3s · army |
| Wraith Storm `wh2_dlc11_lord_abilities_wraith_storm` | `excluded (impossible: no enemy-unit read)` | target | While the unit has an enemy in its sights: fire at it. (FF — keep off until proven) | cd 90s · 9s · enemy unit · ×3 uses · wind-up 3s |
| Wrath of Manann `wh_dlc07_item_abilities_wrath_of_manann` | `excluded (auto: vortex / wandering wind (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 120s · 5s · enemy ground · ×2 uses · wind-up 5s · triage-family: Vortex / wandering wind |
| Wrath of Zharr `wh3_dlc23_army_abilities_wrath_of_zharr` | `excluded (auto: vortex / wandering wind (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 90s · 4s · enemy ground · ×2 uses · wind-up 3s · army · triage-family: Vortex / wandering wind |
| Xapati's Sanctum `wh2_dlc17_army_abilities_xapatis_sanctum` | `excluded (auto: bombardment / ground artillery (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 60s · 5s · enemy ground · ×3 uses · wind-up 3s · army · triage-family: Bombardment / ground artillery |
| Zhufbar 42-Pounders `wh2_dlc11_army_abilities_zhufbar_42_pounders` | `excluded (auto: vortex / wandering wind (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 90s · 4s · enemy ground · ×2 uses · wind-up 3s · army · triage-family: Vortex / wandering wind |
| Zhufbar 42-Pounders `wh2_dlc17_army_abilities_zhufbar_42_pounders_engineer` | `excluded (auto: vortex / wandering wind (friendly fire, family decision 2026-10-09))` | target | While the unit has an enemy in its sights: cast on the ground under the target. (FF — keep off until proven) | cd 90s · 4s · enemy ground · ×1 uses · wind-up 3s · army · triage-family: Vortex / wandering wind |

### 3c. Spells & cataclysms — excluded by prior user decision

Winds-of-magic spells and scenario 'cataclysm' spells (source type `spell` / `cataclysm`). Listed for completeness only.

| Ability | Status | Group | Notes |
|---|---|---|---|
| 'Eadbutt `wh_main_spell_big_waaagh_eadbutt` | `excluded (spell)` | target | spell |
| 'Eadbutt Upgraded `wh_main_spell_big_waaagh_eadbutt_upgraded` | `excluded (spell)` | target | spell |
| 'Ere We Go `wh_main_spell_big_waaagh_ere_we_go` | `excluded (spell)` | melee_self | spell |
| Acquiescence `wh3_main_spell_slaanesh_acquiescence` | `excluded (spell)` | melee_enemy | spell |
| Acquiescence Upgraded `wh3_main_spell_slaanesh_acquiescence_upgraded` | `excluded (spell)` | melee_enemy | spell |
| Ancestral Warriors `wh3_main_spell_yin_ancestral_warriors` | `excluded (spell)` | target | spell |
| Ancestral Warriors Upgraded `wh3_main_spell_yin_ancestral_warriors_upgraded` | `excluded (spell)` | target | spell |
| Apotheosis `wh2_main_spell_high_magic_apotheosis` | `excluded (spell)` | degraded | spell |
| Apotheosis Upgraded `wh2_main_spell_high_magic_apotheosis_upgraded` | `excluded (spell)` | degraded | spell |
| Arcane Unforging `wh2_main_spell_high_magic_arcane_unforging` | `excluded (spell)` | target | spell |
| Arcane Unforging Upgraded `wh2_main_spell_high_magic_arcane_unforging_upgraded` | `excluded (spell)` | target | spell |
| Armour of Darkness `wh2_dlc14_spell_stealth_armour_of_darkness` | `excluded (spell)` | ready | spell |
| Armour of Darkness Upgraded `wh2_dlc14_spell_stealth_armour_of_darkness_upgraded` | `excluded (spell)` | ready | spell |
| Ash Storm `wh3_dlc23_spell_hashut_ash_storm` | `excluded (spell)` | melee_enemy | spell |
| Ash Storm Upgraded `wh3_dlc23_spell_hashut_ash_storm_upgraded` | `excluded (spell)` | melee_enemy | spell |
| Ashes & Dust `wh3_dlc25_cataclysm_death_ashes_and_dust_com` | `excluded (spell)` | target | cataclysm |
| Ashes & Dust `wh3_main_cataclysm_death_ashes_and_dust` | `excluded (spell)` | target | cataclysm |
| Aspect of the Dread Knight `wh_dlc08_spell_death_aspect_of_the_dreadknight_arzik` | `excluded (spell)` | morale | spell |
| Aspect of the Dread Knight `wh_main_spell_death_aspect_of_the_dreadknight` | `excluded (spell)` | morale | spell |
| Aspect of the Dread Knight Upgraded `wh_main_spell_death_aspect_of_the_dreadknight_upgraded` | `excluded (spell)` | morale | spell |
| Awaken from the Grave `wh_dlc04_spell_vampires_raise_dead_helman` | `excluded (spell)` | target | spell |
| Awaken from the Grave Upgraded `wh_dlc04_spell_vampires_raise_dead_upgraded_helman` | `excluded (spell)` | target | spell |
| Awakening of the Wood `wh_dlc05_spell_life_awakening_of_the_wood` | `excluded (spell)` | target | spell |
| Awakening of the Wood `wh_dlc05_spell_life_awakening_the_wood_branchwraith` | `excluded (spell)` | target | spell |
| Banishment `wh_main_spell_light_banishment` | `excluded (spell)` | target | spell |
| Banishment Upgraded `wh_main_spell_light_banishment_upgraded` | `excluded (spell)` | target | spell |
| Birona's Timewarp `wh_main_spell_light_bironas_timewarp` | `excluded (spell)` | melee_self | spell |
| Birona's Timewarp Upgraded `wh_main_spell_light_bironas_timewarp_upgraded` | `excluded (spell)` | melee_self | spell |
| Biting Wind `wh3_main_spell_tempest_biting_wind` | `excluded (spell)` | target | spell |
| Biting Wind `wh3_main_spell_tempest_biting_wind_army` | `excluded (spell)` | target | spell |
| Biting Wind Upgraded `wh3_main_spell_tempest_biting_wind_upgraded` | `excluded (spell)` | target | spell |
| Black Whirlwind `wh2_dlc14_spell_stealth_black_whirlwind` | `excluded (spell)` | target | spell |
| Black Whirlwind Upgraded `wh2_dlc14_spell_stealth_black_whirlwind_upgraded` | `excluded (spell)` | target | spell |
| Bladewind `wh2_main_spell_dark_magic_bladewind` | `excluded (spell)` | target | spell |
| Bladewind Upgraded `wh2_main_spell_dark_magic_bladewind_upgraded` | `excluded (spell)` | target | spell |
| Bless with Filth `wh2_main_spell_plague_bless_with_filth` | `excluded (spell)` | melee_self | spell |
| Bless with Filth Upgraded `wh2_main_spell_plague_bless_with_filth_upgraded` | `excluded (spell)` | melee_self | spell |
| Blessed Cauldron `wh3_dlc24_spell_hags_cursed_cauldron_upgraded` | `excluded (spell)` | target | spell |
| Blessing of the Ancient Witch `wh3_dlc24_spell_hags_curse_of_the_ancient_witch_upgraded` | `excluded (spell)` | ready | spell |
| Blight Boil `wh3_main_spell_nurgle_pestilent_pustule` | `excluded (spell)` | target | spell |
| Blight Boil Upgraded `wh3_main_spell_nurgle_pestilent_pustule_upgraded` | `excluded (spell)` | target | spell |
| Blizzard `wh3_main_spell_tempest_blizzard` | `excluded (spell)` | target | spell |
| Blizzard Upgraded `wh3_main_spell_tempest_blizzard_upgraded` | `excluded (spell)` | target | spell |
| Blossom Wind `wh3_main_spell_yin_blossom_wind` | `excluded (spell)` | target | spell |
| Blossom Wind Upgraded `wh3_main_spell_yin_blossom_wind_upgraded` | `excluded (spell)` | target | spell |
| Blue Fire of Tzeentch `wh3_main_spell_tzeentch_blue_fire_of_tzeentch` | `excluded (spell)` | target | spell |
| Blue Fire of Tzeentch Upgraded `wh3_main_spell_tzeentch_blue_fire_of_tzeentch_upgraded` | `excluded (spell)` | target | spell |
| Bonecrusher `wh3_main_spell_great_maw_bonecrusher` | `excluded (spell)` | target | spell |
| Bonecrusher Upgraded `wh3_main_spell_great_maw_bonecrusher_upgraded` | `excluded (spell)` | target | spell |
| Brain Bursta `wh_main_spell_big_waaagh_brain_bursta` | `excluded (spell)` | target | spell |
| Brain Bursta Upgraded `wh_main_spell_big_waaagh_brain_bursta_upgraded` | `excluded (spell)` | target | spell |
| Braingobbler `wh3_main_spell_great_maw_braingobbler` | `excluded (spell)` | target | spell |
| Braingobbler Upgraded `wh3_main_spell_great_maw_braingobbler_upgraded` | `excluded (spell)` | target | spell |
| Bray-Scream `wh_dlc03_spell_wild_bray_scream` | `excluded (spell)` | target | spell |
| Bray-Scream Upgraded `wh_dlc03_spell_wild_bray_scream_upgraded` | `excluded (spell)` | target | spell |
| Breath of Darkness `wh3_dlc29_spell_undeath_morkharn_breath_of_darkness` | `excluded (spell)` | degraded | spell |
| Breath of Darkness Upgraded `wh3_dlc29_spell_undeath_morkharn_breath_of_darkness_upgraded` | `excluded (spell)` | degraded | spell |
| Brittle Bone `wh2_dlc14_spell_stealth_brittle_bone` | `excluded (spell)` | melee_enemy | spell |
| Brittle Bone Upgrade `wh2_dlc14_spell_stealth_brittle_bone_upgraded` | `excluded (spell)` | melee_enemy | spell |
| Bullgorger `wh3_main_spell_great_maw_bullgorger` | `excluded (spell)` | melee_self | spell |
| Bullgorger Upgraded `wh3_main_spell_great_maw_bullgorger_upgraded` | `excluded (spell)` | melee_self | spell |
| Burning Wrath `wh3_dlc23_spell_hashut_burning_wrath` | `excluded (spell)` | target | spell |
| Burning Wrath Upgraded `wh3_dlc23_spell_hashut_burning_wrath_upgraded` | `excluded (spell)` | target | spell |
| Cascading Fire Cloak `wh_main_spell_fire_cascading_fire_cloak` | `excluded (spell)` | melee_self | spell |
| Chain Lightning `wh2_dlc15_spell_bound_chain_lightning` | `excluded (spell)` | target | spell |
| Chain Lightning `wh3_dlc27_spell_heavens_chain_lightning` | `excluded (spell)` | target | spell |
| Chain Lightning `wh_main_spell_heavens_chain_lightning` | `excluded (spell)` | target | spell |
| Chillwind `wh2_main_spell_dark_magic_chillwind` | `excluded (spell)` | target | spell |
| Chillwind `wh3_dlc27_spell_dark_magic_chillwind_bound` | `excluded (spell)` | target | spell |
| Chillwind Upgraded `wh2_main_spell_dark_magic_chillwind_upgraded` | `excluded (spell)` | target | spell |
| Cloak of Jet `wh3_main_spell_yin_cloak_of_jet` | `excluded (spell)` | ready | spell |
| Cloak of Jet Upgraded `wh3_main_spell_yin_cloak_of_jet_upgraded` | `excluded (spell)` | ready | spell |
| Comet of Casandora `wh2_dlc17_spell_heavens_comet_of_casandora_bound_skink_oracle` | `excluded (spell)` | target | spell |
| Comet of Casandora `wh_main_spell_heavens_comet_of_casandora` | `excluded (spell)` | target | spell |
| Comet of Casandora `wh_main_spell_heavens_comet_of_casandora_summoned` | `excluded (spell)` | target | spell |
| Comet of Casandora Upgraded `wh_main_spell_heavens_comet_of_casandora_upgraded` | `excluded (spell)` | target | spell |
| Command of the Unliving `wh_dlc04_spell_vampires_raise_dead_strigoi` | `excluded (spell)` | target | spell |
| Command of the Unliving Upgraded `wh_dlc04_spell_vampires_raise_dead_upgraded_strigoi` | `excluded (spell)` | target | spell |
| Constellation of the Dragon `wh3_main_spell_yang_constellation_of_the_dragon` | `excluded (spell)` | target | spell |
| Constellation of the Dragon Upgraded `wh3_main_spell_yang_constellation_of_the_dragon_upgraded` | `excluded (spell)` | target | spell |
| Crack's Call `wh2_main_spell_ruin_cracks_call` | `excluded (spell)` | target | spell |
| Crack's Call Upgraded `wh2_main_spell_ruin_cracks_call_upgraded` | `excluded (spell)` | target | spell |
| Crystal Sanctuary `wh3_main_spell_ice_crystal_sanctuary` | `excluded (spell)` | melee_self | spell |
| Crystal Sanctuary Upgraded `wh3_main_spell_ice_crystal_sanctuary_upgraded` | `excluded (spell)` | melee_self | spell |
| Curse of Da Bad Moon `wh_main_spell_lil_waaagh_curse_of_da_bad_moon` | `excluded (spell)` | target | spell |
| Curse of Da Bad Moon Upgraded `wh_main_spell_lil_waaagh_curse_of_da_bad_moon_upgraded` | `excluded (spell)` | target | spell |
| Curse of Hashut `wh3_dlc23_spell_hashut_curse_of_hashut` | `excluded (spell)` | target | spell |
| Curse of Hashut Upgraded `wh3_dlc23_spell_hashut_curse_of_hashut_upgraded` | `excluded (spell)` | target | spell |
| Curse of the Ancient Witch `wh3_dlc24_spell_hags_curse_of_the_ancient_witch` | `excluded (spell)` | target | spell |
| Curse of the Leper `wh3_main_spell_nurgle_curse_of_the_leper` | `excluded (spell)` | melee_self | spell |
| Curse of the Leper Upgraded `wh3_main_spell_nurgle_curse_of_the_leper_upgraded` | `excluded (spell)` | melee_self | spell |
| Curse of the Midnight Wind `wh_main_spell_heavens_curse_of_the_midnight_wind` | `excluded (spell)` | melee_enemy | spell |
| Curse of the Midnight Wind Upgraded `wh_main_spell_heavens_curse_of_the_midnight_wind_upgraded` | `excluded (spell)` | melee_enemy | spell |
| Curse of Years `wh_dlc04_spell_vampires_curse_of_years_helman` | `excluded (spell)` | melee_enemy | spell |
| Curse of Years `wh_main_spell_vampires_curse_of_years` | `excluded (spell)` | melee_enemy | spell |
| Cursed Cauldron `wh3_dlc24_spell_hags_cursed_cauldron` | `excluded (spell)` | target | spell |
| Dance of Despair `wh3_dlc25_cataclysm_shadow_dance_of_despair_com` | `excluded (spell)` | melee_enemy | cataclysm |
| Dance of Despair `wh3_main_cataclysm_shadow_dance_of_despair` | `excluded (spell)` | melee_enemy | cataclysm |
| Dark Subjugation `wh3_dlc23_spell_hashut_dark_subjugation` | `excluded (spell)` | target | spell |
| Dark Subjugation Upgraded `wh3_dlc23_spell_hashut_dark_subjugation_upgraded` | `excluded (spell)` | target | spell |
| Death Frenzy `wh2_main_spell_ruin_death_frenzy` | `excluded (spell)` | melee_self | spell |
| Death Frenzy Upgraded `wh2_main_spell_ruin_death_frenzy_upgraded` | `excluded (spell)` | melee_self | spell |
| Death Frost `wh3_main_spell_ice_death_frost` | `excluded (spell)` | target | spell |
| Death Frost Upgraded `wh3_main_spell_ice_death_frost_upgraded` | `excluded (spell)` | target | spell |
| Deliverance of Itza I `wh2_dlc12_spell_kroak_deliverance_of_itza_1` | `excluded (spell)` | target | spell |
| Deliverance of Itza II `wh2_dlc12_spell_kroak_deliverance_of_itza_2` | `excluded (spell)` | target | spell |
| Deliverance of Itza III `wh2_dlc12_spell_kroak_deliverance_of_itza_3` | `excluded (spell)` | target | spell |
| Denizens of the Deep `wh2_dlc11_spell_deep_denizens_of_the_deep` | `excluded (spell)` | target | spell |
| Devolve `wh_dlc03_spell_wild_devolve` | `excluded (spell)` | melee_enemy | spell |
| Devolve Upgraded `wh_dlc03_spell_wild_devolve_upgraded` | `excluded (spell)` | melee_enemy | spell |
| Djaf's Incantation of Cursed Blades `wh2_dlc09_spell_nehekhara_djafs_incantation_of_cursed_blades` | `excluded (spell)` | melee_self | spell |
| Djaf's Incantation of Cursed Blades Upgraded `wh2_dlc09_spell_nehekhara_djafs_incantation_of_cursed_blades_upgraded` | `excluded (spell)` | melee_self | spell |
| Doom & Darkness `wh_dlc04_spell_death_doom_and_darkness_strigoi` | `excluded (spell)` | target | spell |
| Doom & Darkness `wh_main_spell_death_doom_and_darkness` | `excluded (spell)` | target | spell |
| Doom & Darkness Upgraded `wh3_dlc27_spell_death_doom_and_darkness_summoned` | `excluded (spell)` | target | spell |
| Doom & Darkness Upgraded `wh_main_spell_death_doom_and_darkness_upgraded` | `excluded (spell)` | target | spell |
| Doombolt `wh2_main_spell_dark_magic_doombolt` | `excluded (spell)` | target | spell |
| Doombolt Upgraded `wh2_main_spell_dark_magic_doombolt_upgraded` | `excluded (spell)` | target | spell |
| Dragon's Breath `wh3_main_spell_yang_dragons_breath` | `excluded (spell)` | target | spell |
| Dragon's Breath Upgraded `wh3_main_spell_yang_dragons_breath_upgraded` | `excluded (spell)` | target | spell |
| Drowned Dead `wh2_dlc11_spell_vampires_drowned_dead` | `excluded (spell)` | target | spell |
| Drowned Dead `wh3_dlc24_spell_the_changeling_drowned_dead` | `excluded (spell)` | target | spell |
| Drowned Dead Upgraded `wh2_dlc11_spell_vampires_drowned_dead_upgraded` | `excluded (spell)` | target | spell |
| Earth Blood `wh_dlc05_spell_life_earth_blood` | `excluded (spell)` | degraded | spell |
| Earth Blood `wh_dlc05_spell_life_earth_blood_branchwraith` | `excluded (spell)` | degraded | spell |
| Earth Blood Upgraded `wh_dlc05_spell_life_earth_blood_upgraded` | `excluded (spell)` | degraded | spell |
| Fiery Convocation `wh2_main_spell_high_magic_fiery_convocation` | `excluded (spell)` | target | spell |
| Fiery Convocation Upgraded `wh2_main_spell_high_magic_fiery_convocation_upgraded` | `excluded (spell)` | target | spell |
| Final Transmutation `wh_dlc08_spell_metal_final_transmutation_arzik` | `excluded (spell)` | target | spell |
| Final Transmutation `wh_main_spell_metal_final_transmutation` | `excluded (spell)` | target | spell |
| Final Transmutation Upgraded `wh3_dlc27_spell_metal_final_transmutation_summoned` | `excluded (spell)` | target | spell |
| Final Transmutation Upgraded `wh_main_spell_metal_final_transmutation_upgraded` | `excluded (spell)` | target | spell |
| Fireball `wh_dlc08_spell_fire_fireball_kihar` | `excluded (spell)` | target | spell |
| Fireball `wh_main_spell_fire_fireball` | `excluded (spell)` | target | spell |
| Fireball Upgraded `wh3_dlc27_spell_fire_fireball_summoned` | `excluded (spell)` | target | spell |
| Fireball Upgraded `wh_main_spell_fire_fireball_upgraded` | `excluded (spell)` | target | spell |
| Fists of Gork `wh_main_spell_big_waaagh_fists_of_gork` | `excluded (spell)` | melee_self | spell |
| Flame Storm `wh_main_spell_fire_flame_storm` | `excluded (spell)` | target | spell |
| Flame Storm Upgraded `wh3_dlc27_spell_fire_flame_storm_summoned` | `excluded (spell)` | target | spell |
| Flame Storm Upgraded `wh_main_spell_fire_flame_storm_upgraded` | `excluded (spell)` | target | spell |
| Flames of Azgorh `wh3_dlc23_spell_hashut_flames_of_azgorh` | `excluded (spell)` | target | spell |
| Flames of Azgorh Upgraded `wh3_dlc23_spell_hashut_flames_of_azgorh_upgraded` | `excluded (spell)` | target | spell |
| Flaming Sword of Rhuin `wh_dlc08_spell_fire_flaming_sword_of_rhuin_kihar` | `excluded (spell)` | melee_self | spell |
| Flaming Sword of Rhuin `wh_main_spell_fire_flaming_sword_of_rhuin` | `excluded (spell)` | melee_self | spell |
| Flaming Sword of Rhuin Upgraded `wh_main_spell_fire_flaming_sword_of_rhuin_upgraded` | `excluded (spell)` | melee_self | spell |
| Flensing Haar `wh3_dlc27_spell_mists_flensing_haar` | `excluded (spell)` | melee_enemy | spell |
| Flensing Haar Upgraded `wh3_dlc27_spell_mists_flensing_haar_upgraded` | `excluded (spell)` | melee_enemy | spell |
| Flensing Ruin `wh2_dlc14_spell_ruin_flensing_ruin` | `excluded (spell)` | target | spell |
| Flensing Ruin Upgraded `wh2_dlc14_spell_ruin_flensing_ruin_upgraded` | `excluded (spell)` | target | spell |
| Flesh to Stone `wh_dlc05_spell_life_flesh_to_stone` | `excluded (spell)` | melee_self | spell |
| Flesh to Stone Upgraded `wh_dlc05_spell_life_flesh_to_stone_upgraded` | `excluded (spell)` | melee_self | spell |
| Fleshy Abundance `wh3_main_spell_nurgle_fleshy_abundance` | `excluded (spell)` | degraded | spell |
| Fleshy Abundance Upgraded `wh3_main_spell_nurgle_fleshy_abundance_upgraded` | `excluded (spell)` | degraded | spell |
| Flock of Doom `wh_dlc03_spell_beasts_flock_of_doom` | `excluded (spell)` | target | spell |
| Flock of Doom Upgraded `wh_dlc03_spell_beasts_flock_of_doom_upgraded` | `excluded (spell)` | target | spell |
| Fog of the Damned `wh2_dlc11_spell_deep_fog_of_the_damned` | `excluded (spell)` | melee_enemy | spell |
| Fog of the Damned Upgraded `wh2_dlc11_spell_deep_fog_of_the_damned_upgraded` | `excluded (spell)` | melee_enemy | spell |
| Foot of Gork `wh_main_spell_big_waaagh_foot_of_gork` | `excluded (spell)` | target | spell |
| Foot of Gork Upgraded `wh_main_spell_big_waaagh_foot_of_gork_upgraded` | `excluded (spell)` | target | spell |
| Frost Blades `wh3_main_spell_ice_frost_blades` | `excluded (spell)` | melee_self | spell |
| Frost Blades Upgraded `wh3_main_spell_ice_frost_blades_upgraded` | `excluded (spell)` | melee_self | spell |
| Gaze of Mork `wh_main_spell_big_waaagh_gaze_of_mork` | `excluded (spell)` | target | spell |
| Gaze of Mork Upgraded `wh_main_spell_big_waaagh_gaze_of_mork_upgraded` | `excluded (spell)` | target | spell |
| Gaze of Nagash `wh_dlc04_spell_vampires_gaze_of_nagash_helman` | `excluded (spell)` | target | spell |
| Gaze of Nagash `wh_dlc04_spell_vampires_gaze_of_nagash_strigoi` | `excluded (spell)` | target | spell |
| Gaze of Nagash `wh_main_spell_vampires_gaze_of_nagash` | `excluded (spell)` | target | spell |
| Gaze of Nagash Upgraded `wh_main_spell_vampires_gaze_of_nagash_upgraded` | `excluded (spell)` | target | spell |
| Gehenna's Golden Globe `wh3_dlc25_cataclysm_metal_gehennas_golden_globe_com` | `excluded (spell)` | target | cataclysm |
| Gehenna's Golden Globe `wh3_main_cataclysm_metal_gehennas_golden_globe` | `excluded (spell)` | target | cataclysm |
| Gehenna's Golden Hounds `wh_dlc08_spell_metal_gehennas_golden_hounds_arzik` | `excluded (spell)` | target | spell |
| Gehenna's Golden Hounds `wh_main_spell_metal_gehennas_golden_hounds` | `excluded (spell)` | target | spell |
| Gehenna's Golden Hounds Upgraded `wh3_dlc27_spell_metal_gehennas_golden_hounds_summoned` | `excluded (spell)` | target | spell |
| Gehenna's Golden Hounds Upgraded `wh_main_spell_metal_gehennas_golden_hounds_upgraded` | `excluded (spell)` | target | spell |
| Glean Magic `wh3_main_spell_tzeentch_glean_magic` | `excluded (spell)` | target | spell |
| Glean Magic Upgraded `wh3_main_spell_tzeentch_glean_magic_upgraded` | `excluded (spell)` | target | spell |
| Glittering Robe `wh_main_spell_metal_glittering_robe` | `excluded (spell)` | melee_self | spell |
| Glittering Robe Upgraded `wh_main_spell_metal_glittering_robe_upgraded` | `excluded (spell)` | melee_self | spell |
| Gork'll Fix It `wh_main_spell_lil_waaagh_gorkll_fix_it` | `excluded (spell)` | target | spell |
| Gust of True Flight `wh3_main_spell_tempest_gust_of_true_flight` | `excluded (spell)` | ready | spell |
| Gust of True Flight Upgraded `wh3_main_spell_tempest_gust_of_true_flight_upgraded` | `excluded (spell)` | ready | spell |
| Hailstorm `wh3_main_spell_tempest_hailstorm` | `excluded (spell)` | target | spell |
| Hailstorm Upgraded `wh3_main_spell_tempest_hailstorm_upgraded` | `excluded (spell)` | target | spell |
| Hand of Glory `wh2_main_spell_high_magic_hand_of_glory` | `excluded (spell)` | ready | spell |
| Hand of Glory Upgraded `wh2_main_spell_high_magic_hand_of_glory_upgraded` | `excluded (spell)` | ready | spell |
| Harmonic Convergence `wh_main_spell_heavens_harmonic_convergence` | `excluded (spell)` | melee_self | spell |
| Harmonic Convergence Upgraded `wh_main_spell_heavens_harmonic_convergence_upgraded` | `excluded (spell)` | melee_self | spell |
| Hawks of Miska `wh3_main_spell_tempest_hawks_of_miska` | `excluded (spell)` | target | spell |
| Hawks of Miska Upgraded `wh3_main_spell_tempest_hawks_of_miska_upgraded` | `excluded (spell)` | target | spell |
| Heart of Winter `wh3_main_spell_ice_heart_of_winter` | `excluded (spell)` | target | spell |
| Heart of Winter `wh3_twa08_spell_bound_heart_of_winter_elemental_bear_ror` | `excluded (spell)` | target | spell |
| Heart of Winter Upgraded `wh3_main_spell_ice_heart_of_winter_upgraded` | `excluded (spell)` | target | spell |
| Hell Hammer `wh3_dlc23_spell_hashut_hell_hammer` | `excluded (spell)` | target | spell |
| Hell Hammer Upgraded `wh3_dlc23_spell_hashut_hell_hammer_upgraded` | `excluded (spell)` | target | spell |
| Howling Warpgale `wh2_main_spell_ruin_howling_warpgale` | `excluded (spell)` | target | spell |
| Howling Warpgale Upgraded `wh2_main_spell_ruin_howling_warpgale_upgraded` | `excluded (spell)` | target | spell |
| Hysterical Frenzy `wh3_main_spell_slaanesh_hysterical_frenzy` | `excluded (spell)` | melee_self | spell |
| Hysterical Frenzy Upgraded `wh3_main_spell_slaanesh_hysterical_frenzy_upgraded` | `excluded (spell)` | melee_self | spell |
| Ice Maiden's Kiss `wh3_main_spell_ice_ice_maidens_kiss` | `excluded (spell)` | target | spell |
| Ice Maiden's Kiss Upgraded `wh3_main_spell_ice_ice_maidens_kiss_upgraded` | `excluded (spell)` | target | spell |
| Ice Sheet `wh3_main_spell_ice_ice_sheet` | `excluded (spell)` | target | spell |
| Incantation of Mania `wh3_dlc24_spell_hags_malediction_of_madness_upgraded` | `excluded (spell)` | melee_self | spell |
| Infernal Gateway `wh3_main_spell_tzeentch_infernal_gateway` | `excluded (spell)` | target | spell |
| Infernal Gateway Upgraded `wh3_main_spell_tzeentch_infernal_gateway_upgraded` | `excluded (spell)` | target | spell |
| Invocation of Nehek `wh_dlc04_spell_vampires_invocation_of_nehek_helman` | `excluded (spell)` | degraded | spell |
| Invocation of Nehek `wh_dlc04_spell_vampires_invocation_of_nehek_strigoi` | `excluded (spell)` | degraded | spell |
| Invocation of Nehek `wh_main_spell_vampires_invocation_of_nehek` | `excluded (spell)` | degraded | spell |
| Invocation of Nehek Upgraded `wh_main_spell_vampires_invocation_of_nehek_upgraded` | `excluded (spell)` | degraded | spell |
| Itchy Nuisance `wh_main_spell_lil_waaagh_itchy_nuisance` | `excluded (spell)` | melee_enemy | spell |
| Jade Shield `wh3_main_spell_yang_jade_shield` | `excluded (spell)` | melee_self | spell |
| Jade Shield Upgraded `wh3_main_spell_yang_jade_shield_upgraded` | `excluded (spell)` | melee_self | spell |
| Kraken's Pull `wh2_dlc11_spell_deep_krakens_pull` | `excluded (spell)` | target | spell |
| Kraken's Pull Upgraded `wh2_dlc11_spell_deep_krakens_pull_upgraded` | `excluded (spell)` | target | spell |
| Ladrielle's Shroud `wh3_dlc27_spell_mists_ladrielles_shroud` | `excluded (spell)` | melee_self | spell |
| Ladrielle's Shroud Upgraded `wh3_dlc27_spell_mists_ladrielles_shroud_upgraded` | `excluded (spell)` | degraded | spell |
| Lash of Slaanesh `wh3_main_spell_slaanesh_lash_of_slaanesh` | `excluded (spell)` | target | spell |
| Lash of Slaanesh Upgraded `wh3_main_spell_slaanesh_lash_of_slaanesh_upgraded` | `excluded (spell)` | target | spell |
| Lesser Awakening from the Grave `wh3_dlc29_bound_spell_vampires_raise_dead_upgraded` | `excluded (spell)` | target | spell |
| Light of Battle `wh_main_spell_light_light_of_battle` | `excluded (spell)` | morale | spell |
| Light of Battle Upgraded `wh_main_spell_light_light_of_battle_upgraded` | `excluded (spell)` | morale | spell |
| Magma Storm `wh3_dlc25_cataclysm_fire_magma_storm_com` | `excluded (spell)` | target | cataclysm |
| Magma Storm `wh3_main_cataclysm_fire_magma_storm` | `excluded (spell)` | target | cataclysm |
| Malediction of Madness `wh3_dlc24_spell_hags_malediction_of_madness` | `excluded (spell)` | melee_enemy | spell |
| Mantle of Ghorok `wh_dlc03_spell_wild_mantle_of_ghorok` | `excluded (spell)` | melee_self | spell |
| Mantle of Ghorok Upgraded `wh2_dlc17_spell_wild_mantle_of_ghorok_upgraded` | `excluded (spell)` | melee_self | spell |
| Mathlann’s Spite `wh3_dlc27_spell_mists_mathlanns_spite` | `excluded (spell)` | target | spell |
| Mathlann’s Spite Upgraded `wh3_dlc27_spell_mists_mathlanns_spite_upgraded` | `excluded (spell)` | target | spell |
| Melkoth's Mystifying Miasma `wh3_dlc27_spell_shadow_melkoths_mystifying_miasma_bound` | `excluded (spell)` | target | spell |
| Melkoth's Mystifying Miasma `wh_dlc05_spell_shadow_melkoths_mystifying_miasma` | `excluded (spell)` | target | spell |
| Melkoth's Mystifying Miasma `wh_dlc05_spell_shadow_melkoths_mystifying_miasma_branchwraith` | `excluded (spell)` | target | spell |
| Melkoth's Mystifying Miasma Upgraded `wh_dlc05_spell_shadow_melkoths_mystifying_miasma_upgraded` | `excluded (spell)` | target | spell |
| Merciw's Monstrous Regiment `wh3_dlc25_cataclysm_beasts_merciws_monstrous_regiment_com` | `excluded (spell)` | melee_self | cataclysm |
| Merciw's Monstrous Regiment `wh3_main_cataclysm_beasts_merciws_monstrous_regiment` | `excluded (spell)` | melee_self | cataclysm |
| Miasma of Pestilence `wh3_main_spell_nurgle_miasma_of_pestilence` | `excluded (spell)` | melee_enemy | spell |
| Miasma of Pestilence Upgraded `wh3_main_spell_nurgle_miasma_of_pestilence_upgraded` | `excluded (spell)` | melee_enemy | spell |
| Might of Heaven & Earth `wh3_main_spell_yang_might_of_heaven_and_earth` | `excluded (spell)` | melee_self | spell |
| Might of Heaven & Earth Upgraded `wh3_main_spell_yang_might_of_heaven_and_earth_upgraded` | `excluded (spell)` | melee_self | spell |
| Missile Mirror `wh3_main_spell_yin_missile_mirror` | `excluded (spell)` | target | spell |
| Missile Mirror Upgraded `wh3_main_spell_yin_missile_mirror_upgraded` | `excluded (spell)` | target | spell |
| Mistress of the Deeps `wh3_dlc27_spell_mists_mistress_of_the_deeps` | `excluded (spell)` | target | spell |
| Neru's Incantation of Protection `wh2_dlc09_spell_nehekhara_nerus_incantation_of_protection` | `excluded (spell)` | melee_self | spell |
| Neru's Incantation of Protection Upgraded `wh2_dlc09_spell_nehekhara_nerus_incantation_of_protection_upgraded` | `excluded (spell)` | melee_self | spell |
| Net of Amyntok `wh_main_spell_light_net_of_amyntok` | `excluded (spell)` | target | spell |
| Net of Amyntok Upgraded `wh_main_spell_light_net_of_amyntok_upgraded` | `excluded (spell)` | target | spell |
| Night Shroud `wh_main_spell_lil_waaagh_night_shroud` | `excluded (spell)` | ready | spell |
| Night Shroud Upgraded `wh_main_spell_lil_waaagh_night_shroud_upgraded` | `excluded (spell)` | ready | spell |
| Okkam's Mindrazor `wh_dlc05_spell_shadow_okkams_mindrazor` | `excluded (spell)` | melee_self | spell |
| Okkam's Mindrazor Upgraded `wh_dlc05_spell_shadow_okkams_mindrazor_upgraded` | `excluded (spell)` | melee_self | spell |
| Omen of Spirits `wh3_dlc24_spell_hags_vengeance_of_spirits_upgraded` | `excluded (spell)` | ready | spell |
| Pann's Impenetrable Pelt `wh_dlc03_spell_beasts_panns_impenetrable_pelt` | `excluded (spell)` | ready | spell |
| Pann's Impenetrable Pelt `wh_dlc03_spell_beasts_panns_impenetrable_pelt_summoned` | `excluded (spell)` | ready | spell |
| Pann's Impenetrable Pelt Upgraded `wh_dlc03_spell_beasts_panns_impenetrable_pelt_upgraded` | `excluded (spell)` | ready | spell |
| Pavane of Slaanesh `wh3_main_spell_slaanesh_pavane_of_slaanesh` | `excluded (spell)` | target | spell |
| Pavane of Slaanesh Upgraded `wh3_main_spell_slaanesh_pavane_of_slaanesh_upgraded` | `excluded (spell)` | target | spell |
| Pestilent Birth `wh2_main_spell_plague_pestilent_birth` | `excluded (spell)` | target | spell |
| Pestilent Breath `wh2_main_spell_plague_pestilent_breath` | `excluded (spell)` | target | spell |
| Pestilent Breath Upgraded `wh2_main_spell_plague_pestilent_breath_upgraded` | `excluded (spell)` | target | spell |
| Pha's Protection `wh_main_spell_light_phas_protection` | `excluded (spell)` | melee_self | spell |
| Pha's Protection Upgraded `wh_main_spell_light_phas_protection_upgraded` | `excluded (spell)` | melee_self | spell |
| Phantasmagoria `wh3_main_spell_slaanesh_phantasmagoria` | `excluded (spell)` | target | spell |
| Phantasmagoria Upgraded `wh3_main_spell_slaanesh_phantasmagoria_upgraded` | `excluded (spell)` | target | spell |
| Piercing Bolts of Burning `wh_main_spell_fire_piercing_bolts_of_burning` | `excluded (spell)` | target | spell |
| Piercing Bolts of Burning Upgraded `wh_main_spell_fire_piercing_bolts_of_burning_upgraded` | `excluded (spell)` | target | spell |
| Pink Fire of Tzeentch `wh3_main_spell_tzeentch_pink_fire_of_tzeentch` | `excluded (spell)` | target | spell |
| Pink Fire of Tzeentch Upgraded `wh3_main_spell_tzeentch_pink_fire_of_tzeentch_upgraded` | `excluded (spell)` | target | spell |
| Pit of Shades `wh_dlc05_spell_shadow_pit_of_shades` | `excluded (spell)` | target | spell |
| Pit of Shades `wh_dlc08_spell_shadow_pit_of_shades_kihar` | `excluded (spell)` | target | spell |
| Pit of Shades Upgraded `wh_dlc05_spell_shadow_pit_of_shades_upgraded` | `excluded (spell)` | target | spell |
| Plague `wh2_main_spell_plague_plague` | `excluded (spell)` | target | spell |
| Plague of Rust `wh_dlc08_spell_metal_plague_of_rust_kihar` | `excluded (spell)` | target | spell |
| Plague of Rust `wh_main_spell_metal_plague_of_rust` | `excluded (spell)` | target | spell |
| Plague of Rust Upgraded `wh_main_spell_metal_plague_of_rust_upgraded` | `excluded (spell)` | target | spell |
| Plague Upgraded `wh2_main_spell_plague_plague_upgraded` | `excluded (spell)` | target | spell |
| Power of Darkness `wh2_main_spell_dark_magic_power_of_darkness` | `excluded (spell)` | ready | spell |
| Ptra's Incantation of Righteous Smiting `wh2_dlc09_spell_nehekhara_ptras_incantation_of_righteous_smiting` | `excluded (spell)` | ready | spell |
| Ptra's Incantation of Righteous Smiting Upgraded `wh2_dlc09_spell_nehekhara_ptras_incantation_of_righteous_smiting_upgraded` | `excluded (spell)` | ready | spell |
| Raise Dead `wh_main_spell_vampires_raise_dead` | `excluded (spell)` | target | spell |
| Raise Dead (Skeleton Warriors) `wh3_dlc29_bound_spell_vampires_raise_dead` | `excluded (spell)` | target | spell |
| Raise Dead Upgraded `wh_main_spell_vampires_raise_dead_upgraded` | `excluded (spell)` | target | spell |
| Rancid Visitations `wh3_main_spell_nurgle_rancid_visitations` | `excluded (spell)` | target | spell |
| Rancid Visitations Upgraded `wh3_main_spell_nurgle_rancid_visitations_upgraded` | `excluded (spell)` | target | spell |
| Regrowth `wh_dlc05_spell_life_regrowth` | `excluded (spell)` | degraded | spell |
| Regrowth Upgraded `wh_dlc05_spell_life_regrowth_upgraded` | `excluded (spell)` | degraded | spell |
| Sakhmet's Incantation of the Skullstorm `wh2_dlc09_spell_nehekhara_sakhmets_incantation_of_the_skullstorm` | `excluded (spell)` | target | spell |
| Sakhmet's Incantation of the Skullstorm Upgraded `wh2_dlc09_spell_nehekhara_sakhmets_incantation_of_the_skullstorm_upgraded` | `excluded (spell)` | target | spell |
| Savage Dominion `wh_dlc03_spell_wild_savage_dominion` | `excluded (spell)` | target | spell |
| Scorch `wh2_main_spell_ruin_scorch` | `excluded (spell)` | target | spell |
| Scorch Upgraded `wh2_main_spell_ruin_scorch_upgraded` | `excluded (spell)` | target | spell |
| Searing Doom `wh_dlc08_spell_metal_searing_doom_arzik` | `excluded (spell)` | target | spell |
| Searing Doom `wh_main_spell_metal_searing_doom` | `excluded (spell)` | target | spell |
| Searing Doom Upgraded `wh3_dlc27_spell_metal_searing_doom_summoned` | `excluded (spell)` | target | spell |
| Searing Doom Upgraded `wh_main_spell_metal_searing_doom_upgraded` | `excluded (spell)` | target | spell |
| Shem's Burning Gaze `wh_main_spell_light_shems_burning_gaze` | `excluded (spell)` | target | spell |
| Shem's Burning Gaze Upgraded `wh_main_spell_light_shems_burning_gaze_upgraded` | `excluded (spell)` | target | spell |
| Shield of Thorns `wh_dlc05_spell_life_shield_of_thorns` | `excluded (spell)` | charge | spell |
| Shield of Thorns `wh_dlc05_spell_life_shield_of_thorns_branchwraith` | `excluded (spell)` | charge | spell |
| Shield of Thorns Upgraded `wh_dlc05_spell_life_shield_of_thorns_upgraded` | `excluded (spell)` | charge | spell |
| Skitterleap `wh2_main_spell_ruin_skitterleap` | `excluded (spell)` | ready | spell |
| Skitterleap Upgraded `wh2_main_spell_ruin_skitterleap_upgraded` | `excluded (spell)` | ready | spell |
| Slicing Shards `wh3_main_spell_slaanesh_slicing_shards` | `excluded (spell)` | target | spell |
| Slicing Shards Upgraded `wh3_main_spell_slaanesh_slicing_shards_upgraded` | `excluded (spell)` | target | spell |
| Sneaky Stabbin' `wh_main_spell_lil_waaagh_sneaky_stabbin` | `excluded (spell)` | melee_self | spell |
| Soul Quench `wh2_main_spell_high_magic_soul_quench` | `excluded (spell)` | target | spell |
| Soul Quench Upgraded `wh2_main_spell_high_magic_soul_quench_upgraded` | `excluded (spell)` | target | spell |
| Soul Stealer `wh2_main_spell_dark_magic_soul_stealer` | `excluded (spell)` | target | spell |
| Soulblight `wh_dlc04_spell_death_soulblight_strigoi` | `excluded (spell)` | melee_enemy | spell |
| Soulblight `wh_dlc08_spell_death_soulblight_arzik` | `excluded (spell)` | melee_enemy | spell |
| Soulblight `wh_main_spell_death_soulblight` | `excluded (spell)` | melee_enemy | spell |
| Soulblight Upgraded `wh_main_spell_death_soulblight_upgraded` | `excluded (spell)` | melee_enemy | spell |
| Spirit Leech `wh_dlc04_spell_death_spirit_leech_strigoi` | `excluded (spell)` | target | spell |
| Spirit Leech `wh_main_spell_death_spirit_leech` | `excluded (spell)` | target | spell |
| Spirit Leech Upgraded `wh3_dlc27_spell_death_spirit_leech_summoned` | `excluded (spell)` | target | spell |
| Spirit Leech Upgraded `wh_main_spell_death_spirit_leech_upgraded` | `excluded (spell)` | target | spell |
| Spiteful Shot `wh2_dlc11_spell_deep_spiteful_shot` | `excluded (spell)` | ready | spell |
| Spiteful Shot Upgraded `wh2_dlc11_spell_deep_spiteful_shot_upgraded` | `excluded (spell)` | ready | spell |
| Stone Ground Stance `wh3_main_spell_yang_stone_ground_stance` | `excluded (spell)` | charge | spell |
| Stone Ground Stance Upgraded `wh3_main_spell_yang_stone_ground_stance_upgraded` | `excluded (spell)` | charge | spell |
| Storm of Renewal `wh3_dlc25_cataclysm_life_storm_of_renewal_com` | `excluded (spell)` | degraded | cataclysm |
| Storm of Renewal `wh3_main_cataclysm_life_storm_of_renewal` | `excluded (spell)` | degraded | cataclysm |
| Storm of Shadows `wh3_main_spell_yin_storm_of_shadows` | `excluded (spell)` | target | spell |
| Storm of Shadows Upgraded `wh3_main_spell_yin_storm_of_shadows_upgraded` | `excluded (spell)` | target | spell |
| Stream of Corruption `wh3_main_spell_nurgle_stream_of_corruption` | `excluded (spell)` | target | spell |
| Stream of Corruption Upgraded `wh3_main_spell_nurgle_stream_of_corruption_upgraded` | `excluded (spell)` | target | spell |
| Swiftwing `wh3_main_spell_tempest_swiftwing` | `excluded (spell)` | charge | spell |
| Swiftwing Upgraded `wh3_main_spell_tempest_swiftwing_upgraded` | `excluded (spell)` | charge | spell |
| Talons of Night `wh3_main_spell_yin_talons_of_night` | `excluded (spell)` | target | spell |
| Talons of Night Upgraded `wh3_main_spell_yin_talons_of_night_upgraded` | `excluded (spell)` | target | spell |
| Tempest `wh2_main_spell_high_magic_tempest` | `excluded (spell)` | target | spell |
| Tempest Upgraded `wh2_main_spell_high_magic_tempest_upgraded` | `excluded (spell)` | target | spell |
| The Abyssal Swarm `wh3_dlc29_spell_undeath_razkhar_the_abyssal_swarm` | `excluded (spell)` | target | spell |
| The Abyssal Swarm Upgraded `wh3_dlc29_spell_undeath_razkhar_the_abyssal_swarm_upgraded` | `excluded (spell)` | target | spell |
| The Amber Spear `wh_dlc03_spell_beasts_the_amber_spear` | `excluded (spell)` | target | spell |
| The Amber Spear Upgraded `wh_dlc03_spell_beasts_the_amber_spear_upgraded` | `excluded (spell)` | target | spell |
| The Burning Head `wh_main_spell_fire_the_burning_head` | `excluded (spell)` | target | spell |
| The Burning Head Upgraded `wh3_dlc27_spell_fire_the_burning_head_summoned` | `excluded (spell)` | target | spell |
| The Burning Head Upgraded `wh_main_spell_fire_the_burning_head_upgraded` | `excluded (spell)` | target | spell |
| The Curse of Anraheir `wh_dlc03_spell_beasts_the_curse_of_anraheir` | `excluded (spell)` | melee_enemy | spell |
| The Curse of Anraheir Upgraded `wh_dlc03_spell_beasts_the_curse_of_anraheir_upgraded` | `excluded (spell)` | melee_enemy | spell |
| The Dark Riders `wh3_dlc29_spell_undeath_akararan_the_dark_riders` | `excluded (spell)` | target | spell |
| The Dark Riders Upgraded `wh3_dlc29_spell_undeath_akararan_the_dark_riders_upgraded` | `excluded (spell)` | target | spell |
| The Dreaded Thirteenth Spell `wh2_dlc14_spell_grey_seer_the_dreaded_thirteenth_spell_upgraded` | `excluded (spell)` | melee_enemy | spell |
| The Dreaded Thirteenth Spell `wh2_main_spell_grey_seer_the_dreaded_thirteenth_spell` | `excluded (spell)` | target | spell |
| The Dwellers Below `wh_dlc05_spell_life_the_dwellers_below` | `excluded (spell)` | target | spell |
| The Dwellers Below Upgraded `wh_dlc05_spell_life_the_dwellers_below_upgraded` | `excluded (spell)` | target | spell |
| The Enfeebling Foe `wh_dlc05_spell_shadow_the_enfeebling_foe` | `excluded (spell)` | melee_enemy | spell |
| The Enfeebling Foe Upgraded `wh_dlc05_spell_shadow_the_enfeebling_foe_upgraded` | `excluded (spell)` | melee_enemy | spell |
| The Fate of Bjuna `wh_dlc08_spell_death_the_fate_of_bjuna_arzik` | `excluded (spell)` | target | spell |
| The Fate of Bjuna `wh_main_spell_death_the_fate_of_bjuna` | `excluded (spell)` | target | spell |
| The Forbidden Fens `wh3_dlc24_spell_hags_the_forbidden_fens` | `excluded (spell)` | target | spell |
| The Hand of Dust `wh3_dlc29_spell_undeath_sulekhim_hand_of_dust` | `excluded (spell)` | melee_self | spell |
| The Hand of Dust Upgraded `wh3_dlc29_spell_undeath_sulekhim_hand_of_dust_upgraded` | `excluded (spell)` | melee_self | spell |
| The Harbinger `wh3_dlc29_spell_undeath_kandorak_the_harbinger` | `excluded (spell)` | target | spell |
| The Maw `wh3_main_spell_great_maw_the_maw` | `excluded (spell)` | target | spell |
| The Maw Upgraded `wh3_main_spell_great_maw_the_maw_upgraded` | `excluded (spell)` | target | spell |
| The Penumbral Pendulum `wh_dlc05_spell_shadow_the_penumbral_pendulum` | `excluded (spell)` | target | spell |
| The Penumbral Pendulum `wh_dlc05_spell_shadow_the_penumbral_pendulum_branchwraith` | `excluded (spell)` | target | spell |
| The Penumbral Pendulum `wh_dlc08_spell_shadow_the_penumbral_pendulum_kihar` | `excluded (spell)` | target | spell |
| The Penumbral Pendulum Upgraded `wh_dlc05_spell_shadow_the_penumbral_pendulum_upgraded` | `excluded (spell)` | target | spell |
| The Purple Sun of Xereus `wh_main_spell_death_the_purple_sun_of_xereus` | `excluded (spell)` | target | spell |
| The Purple Sun of Xereus Upgraded `wh3_dlc27_spell_death_the_purple_sun_of_xereus_summoned` | `excluded (spell)` | target | spell |
| The Purple Sun of Xereus Upgraded `wh_main_spell_death_the_purple_sun_of_xereus_upgraded` | `excluded (spell)` | target | spell |
| The Soulstealer `wh3_dlc29_spell_undeath_khizaar_the_soulstealer` | `excluded (spell)` | target | spell |
| The Soulstealer Upgraded `wh3_dlc29_spell_undeath_khizaar_the_soulstealer_upgraded` | `excluded (spell)` | target | spell |
| The Withering `wh_dlc05_spell_shadow_the_withering` | `excluded (spell)` | target | spell |
| The Withering `wh_dlc05_spell_shadow_the_withering_branchwraith` | `excluded (spell)` | target | spell |
| The Withering Upgraded `wh_dlc05_spell_shadow_the_withering_upgraded` | `excluded (spell)` | target | spell |
| The Writhing Mist `wh3_dlc27_spell_mists_the_writhing_mist` | `excluded (spell)` | melee_enemy | spell |
| The Writhing Mist `wh3_dlc27_spell_mists_the_writhing_mist_bound` | `excluded (spell)` | melee_enemy | spell |
| The Writhing Mist Upgraded `wh3_dlc27_spell_mists_the_writhing_mist_upgraded` | `excluded (spell)` | melee_enemy | spell |
| Thorsen's Thunderstorm `wh3_dlc25_cataclysm_heavens_thorsens_thunderstorm_com` | `excluded (spell)` | target | cataclysm |
| Thorsen's Thunderstorm `wh3_main_cataclysm_heavens_thorsens_thunderstorm` | `excluded (spell)` | target | cataclysm |
| Tidecall `wh2_dlc11_spell_deep_tidecall` | `excluded (spell)` | target | spell |
| Tidecall Upgraded `wh2_dlc11_spell_deep_tidecall_upgraded` | `excluded (spell)` | target | spell |
| Time Amok `wh3_dlc25_cataclysm_light_time_amok_com` | `excluded (spell)` | melee_self | cataclysm |
| Time Amok `wh3_main_cataclysm_light_time_amok` | `excluded (spell)` | melee_self | cataclysm |
| Toothcracker `wh3_main_spell_great_maw_toothcracker` | `excluded (spell)` | ready | spell |
| Toothcracker Upgraded `wh3_main_spell_great_maw_toothcracker_upgraded` | `excluded (spell)` | ready | spell |
| Traitor-Kin `wh_dlc03_spell_wild_traitor_kin` | `excluded (spell)` | target | spell |
| Traitor-Kin Upgraded `wh_dlc03_spell_wild_traitor_kin_upgraded` | `excluded (spell)` | target | spell |
| Transformation of Kadon `wh2_dlc11_spell_beasts_transformation_of_kadon` | `excluded (spell)` | target | spell |
| Transformation of Kadon `wh2_dlc15_spell_beasts_transformation_of_kadon` | `excluded (spell)` | target | spell |
| Transformation of Kadon `wh2_dlc16_army_abilities_transformation_of_kadon` | `excluded (spell)` | target | spell |
| Transformation of Kadon `wh3_cp1_spell_beasts_transformation_of_kadon` | `excluded (spell)` | target | spell |
| Transformation of Kadon `wh_dlc03_spell_beasts_transformation_of_kadon` | `excluded (spell)` | target | spell |
| Transmutation of Lead `wh_dlc08_spell_metal_transmutation_of_lead_kihar` | `excluded (spell)` | melee_enemy | spell |
| Transmutation of Lead `wh_main_spell_metal_transmutation_of_lead` | `excluded (spell)` | melee_enemy | spell |
| Transmutation of Lead Upgraded `wh_main_spell_metal_transmutation_of_lead_upgraded` | `excluded (spell)` | melee_enemy | spell |
| Treason of Tzeentch `wh3_main_spell_tzeentch_treason_of_tzeentch` | `excluded (spell)` | target | spell |
| Treason of Tzeentch Upgraded `wh3_main_spell_tzeentch_treason_of_tzeentch_upgraded` | `excluded (spell)` | target | spell |
| Trollguts `wh3_main_spell_great_maw_trollguts` | `excluded (spell)` | degraded | spell |
| Trollguts Upgraded `wh3_main_spell_great_maw_trollguts_upgraded` | `excluded (spell)` | degraded | spell |
| Tzeentch's Firestorm `wh3_main_spell_tzeentch_tzeentchs_firestorm` | `excluded (spell)` | target | spell |
| Tzeentch's Firestorm Upgraded `wh3_main_spell_tzeentch_tzeentchs_firestorm_upgraded` | `excluded (spell)` | target | spell |
| Urannon's Thunderbolt `wh_main_spell_heavens_urannons_thunderbolt` | `excluded (spell)` | target | spell |
| Urannon's Thunderbolt Upgraded `wh_main_spell_heavens_urannons_thunderbolt_upgraded` | `excluded (spell)` | target | spell |
| Usekhp's Incantation of Desiccation `wh2_dlc09_spell_nehekhara_usekhps_incantation_of_desiccation` | `excluded (spell)` | melee_enemy | spell |
| Usekhp's Incantation of Desiccation Upgraded `wh2_dlc09_spell_nehekhara_usekhps_incantation_of_desiccation_upgraded` | `excluded (spell)` | melee_enemy | spell |
| Usirian's Incantation of Vengeance `wh2_dlc09_spell_nehekhara_usirians_incantation_of_vengeance` | `excluded (spell)` | target | spell |
| Usirian's Incantation of Vengeance Upgraded `wh2_dlc09_spell_nehekhara_usirians_incantation_of_vengeance_upgraded` | `excluded (spell)` | target | spell |
| Vangheist's Revenge `wh2_dlc11_spell_deep_ghost_ship` | `excluded (spell)` | target | spell |
| Vangheist's Revenge Upgraded `wh2_dlc11_spell_deep_ghost_ship_upgraded` | `excluded (spell)` | target | spell |
| Vanhel's Danse Macabre `wh_dlc04_spell_vampires_vanhels_danse_macabre_helman` | `excluded (spell)` | melee_self | spell |
| Vanhel's Danse Macabre `wh_main_spell_vampires_vanhels_danse_macabre` | `excluded (spell)` | melee_self | spell |
| Vanhel's Danse Macabre Upgraded `wh_main_spell_vampires_vanhels_danse_macabre_upgraded` | `excluded (spell)` | melee_self | spell |
| Veil of Shadows `wh2_dlc14_spell_stealth_veil_of_shadows` | `excluded (spell)` | target | spell |
| Veil of Shadows Upgraded `wh2_dlc14_spell_stealth_veil_of_shadows_upgraded` | `excluded (spell)` | target | spell |
| Vengeance of Spirits `wh3_dlc24_spell_hags_vengeance_of_spirits` | `excluded (spell)` | target | spell |
| Vermintide `wh2_main_spell_plague_vermintide` | `excluded (spell)` | target | spell |
| Viletide `wh_dlc03_spell_wild_viletide` | `excluded (spell)` | target | spell |
| Viletide Upgraded `wh_dlc03_spell_wild_viletide_upgraded` | `excluded (spell)` | target | spell |
| Vindictive Glare `wh_main_spell_lil_waaagh_vindictive_glare` | `excluded (spell)` | target | spell |
| Vindictive Glare Upgraded `wh_main_spell_lil_waaagh_vindictive_glare_upgraded` | `excluded (spell)` | target | spell |
| Walk Between Worlds `wh3_dlc27_spell_mists_walk_between_worlds` | `excluded (spell)` | ready | spell |
| Walk Between Worlds `wh3_dlc27_spell_mists_walk_between_worlds_upgraded` | `excluded (spell)` | ready | spell |
| Wall of Wind & Fire `wh3_main_spell_yang_wall_of_wind_and_fire` | `excluded (spell)` | target | spell |
| Wall of Wind & Fire Upgraded `wh3_main_spell_yang_wall_of_wind_and_fire_upgraded` | `excluded (spell)` | target | spell |
| Warp Lightning `wh2_main_spell_ruin_warp_lightning` | `excluded (spell)` | target | spell |
| Warp Lightning Upgraded `wh2_main_spell_ruin_warp_lightning_upgraded` | `excluded (spell)` | target | spell |
| Warp Stars `wh2_dlc14_spell_stealth_warp_stars` | `excluded (spell)` | target | spell |
| Warp Stars Upgraded `wh2_dlc14_spell_stealth_warp_stars_upgraded` | `excluded (spell)` | target | spell |
| Whispers in the Woods `wh3_dlc24_spell_hags_the_forbidden_fens_upgraded` | `excluded (spell)` | ready | spell |
| Wind Blast `wh_main_spell_heavens_wind_blast` | `excluded (spell)` | target | spell |
| Wind Blast `wh_main_spell_heavens_wind_blast_summoned` | `excluded (spell)` | target | spell |
| Wind Blast Upgraded `wh_main_spell_heavens_wind_blast_upgraded` | `excluded (spell)` | target | spell |
| Wind of Death `wh_dlc04_spell_vampires_wind_of_death_helman` | `excluded (spell)` | target | spell |
| Wind of Death `wh_main_spell_vampires_wind_of_death` | `excluded (spell)` | target | spell |
| Wind of Death Upgraded `wh_main_spell_vampires_wind_of_death_upgraded` | `excluded (spell)` | target | spell |
| Witchbrew `wh3_dlc24_spell_hags_witchbrew` | `excluded (spell)` | target | spell |
| Witchbroth `wh3_dlc24_spell_hags_witchbrew_upgraded` | `excluded (spell)` | target | spell |
| Wither `wh2_main_spell_plague_wither` | `excluded (spell)` | target | spell |
| Wither Upgraded `wh2_main_spell_plague_wither_upgraded` | `excluded (spell)` | target | spell |
| Word of Pain `wh2_main_spell_dark_magic_word_of_pain` | `excluded (spell)` | melee_enemy | spell |
| Word of Pain Upgraded `wh2_main_spell_dark_magic_word_of_pain_upgraded` | `excluded (spell)` | melee_enemy | spell |
| Wyssan's Wildform `wh_dlc03_spell_beasts_wyssans_wildform` | `excluded (spell)` | melee_self | spell |
| Wyssan's Wildform Upgraded `wh_dlc03_spell_beasts_wyssans_wildform_upgraded` | `excluded (spell)` | melee_self | spell |

*File generated from the game's own tables (see sources above). Total rows: 1145 + 218 + 434 = 1797.*

---

## 4. Decisions log — melee questionnaire, block 1

Block 1 of the melee questionnaire is complete. Decisions are recorded inline (§2 entries carry a `Decision:` note; §3a rows carry the status) and summarised here.

**Approved — in melee (and not fleeing): cast on self:** Aether Sword, Apocalyptic Vision, Armour of Gazrakh, Aura of Quetzl, Axe of Dargo, Axe of Grom, Axes of Kadrin, Azhag's 'Ard Armour, Ballet of Blows, Bear Fang Talisman, Beastslaver, Blade of Bel-Korhadris, Blades of Shang-Yang, Bloodstorm Blades, Brass Body, Change or Die!, Claws of Mourkain, Cloak of Mists & Shadows, Coat in Blood, Creature-Killer, Da Great 'Un Iz 'Ere!, Daemonblade, Daemonshield, Dagger of Malice, Dark Protection, Darkwalker, Deathbringer (incl. upgraded), Desertstrike.

**Rejected (6)** — no automatic logic; left to the player:
- **Acidic Musk Glands** (`wh2_dlc16_unit_abilities_acidic_musk_glands`) — friendly fire. User: “no automatic logic for now, potential for friendly fire”
- **All-Consuming Hatred** (`wh3_dlc27_unit_abilities_consuming_hatred`) — drawback (Melee Defence -12). User: “serious drawback (Melee Defence -12); player should decide”
- **Bastion of the Great Cities** (`wh3_dlc24_unit_abilities_bastion_of_the_great_cities`) — mutual exclusivity (standing rule 3).
- **Call for Power** (`wh3_main_daemon_head_abilities_call_for_power`) — loss of control: Rampage! (standing rule 4).
- **Daggerdance** (`wh3_dlc27_lord_abilities_daggerdance`) — drawbacks (standing rule 2).
- **Dance of Destruction** (`wh3_dlc27_lord_abilities_dance_of_destruction`) — drawback (standing rule 2).

**Redesigned (2)** — approved with a different trigger:
- **Commanding Presence** (`wh3_dlc29_lord_active_commanding_presence`) — user: “Not related to melee, only to morale. The trigger should be when lord or nearby unit are wavering.”
- **Dazh's Song of Winter Sunlight** (`wh3_main_character_abilities_dazs_song_of_winter_sunlight`) — user: “Ideally vigor based, not melee based. Activate when Tired.”

**Pending review (1)** — tentative yes; revisit before implementing:
- **Chanson of Caging** (`wh3_dlc27_lord_abilities_chanson_of_caging`) — user: “Makes sense, but could be better. Let's say Yes for now but pending for review.”

## 5. Decisions log — melee questionnaire, block 2

Block 2 of the melee questionnaire is complete. Decisions are recorded inline (§2 entries carry a `Decision:` note; §3a rows carry the status) and summarised here.

**Approved — in melee (and not fleeing): cast on self (27):** Dolorous Blade, Dragon Spear, Dreaded Duellist, Dwarf Gouger, Enrage, Entice, Everyone Has Their Price, Evisceration, Eye for an Eye, Eye Gouger, Eye of the Storm, Faith's Bastion, Fangsword of Eltharion, Feint & Riposte, Filth Mace, Fluid Injection!, Fury of the Blood God (Gaze of Khorne), Fury of the Land, Fury of Ursun, Ghal Maraz, Giant Leap, Gitsnik, Gotrek's Doom, Grand Shield of Faith, Great Gutgouger, Halo of Maidenly Wrath, Hammer-axe of Skoll.

**Approved with a different trigger (5)** — redesigned (see each item's decision note):
- **Eagle-Feather Torc** (`wh3_dlc27_item_abilities_eagle_feather_torc`) — user: “Condition should be when barrier is broken” → when the barrier is broken: cast on self.
- **Fangspike** (`wh3_dlc26_weapon_abilities_fangspike`) — user: “Both charge and in melee” → charge window or in melee: cast on self.
- **Foe-Seeker (summoned variant)** (`wh_main_character_abilities_foe_seeker_summoned`) — user: “Same as Foe-Seeker (tired or worse)” → fatigue Tired or worse, fail-closed.
- **Ghoul King of Ushoran** (`wh2_dlc11_lord_abilities_ghoul_king_of_ushoran`) — user: “When health is 75% or lower” → when health at/below 75%: cast on self.
- **Glorious Death** (`wh3_dlc25_lord_abilities_glorious_death`) — user: “Cast on self when self is a character only makes sense when death is very close. Priority should be cast on another slayer unit (not character) when that unit is in melee.” → cast on a nearby Slayer unit (not a character) that is in melee.

**Rejected (6)** — no automatic logic; left to the player:
- **Dinner Bell** (`wh3_dlc26_character_abilities_dinner_bell`) — drawback: 30% miscast (standing rule 2).
- **Disdain of the Dragon Emperor** (`wh3_dlc24_unit_abilities_disdain_of_the_dragon_emperor`) — mutual exclusivity (standing rule 3).
- **Endless Whirlwind of Death** (`wh3_dlc25_unit_abilities_whirlwind_of_death_ror` + `wh3_dlc25_unit_abilities_whirlwind_of_death_ror_upgraded`) — friendly fire (standing rule 1).
- **Epidemic Outbreak** (`wh3_dlc25_character_abilties_epidemic_outbreak_improved` + `wh3_dlc25_character_abilties_epidemic_outbreak`) — tactical escape. User: “the escape in melee is tactically relevant and must be chosen by player” (standing rule 5).
- **Fury of the Falling Blade** (`wh3_dlc24_unit_abilities_fury_of_the_falling_blade`) — mutual exclusivity (standing rule 3).
- **Harbinger of Pestilence** (`wh3_dlc20_lord_abilities_harbinger_of_pestilence`) — mutual exclusivity (standing rule 3).

**Skipped (1)** — approved in principle but not achievable:
- **Enkhil's Kanopi** (`wh2_dlc09_item_abilities_enkhils_kanopi`) — not achievable: reacting to an enemy spell cast needs a spell-cast event or an enemy unit read, neither of which exists.

**Key-spelling note:** the questionnaire supplied `wh2_dlc11_lord_abilities_dreaded_duellist`; the game dump and tracker use `wh2_dlc11_lord_abilities_dreaded_duelist` (single “l”). The decision was applied to the real key (`..._dreaded_duelist`, §2 #53 / §3a).

## 6. Decisions log — melee questionnaire, block 3

Block 3 of the melee questionnaire is complete (tracker items §2 #89–#131; 40 items decided). Decisions are recorded inline (§2 entries carry a `Decision:` note; §3a rows carry the status) and summarised here.

**Approved — in melee (and not fleeing): cast on self (31):** Hellfire Sword, Helm of Discord, Helm of Many Eyes, Heroic Killing Blow (3 keys), Hydra Blade, Inevitable Horror, Karaghul, Killing Blow (2 keys), Legbiter, Liarsbane, Lightning Reflexes, Locus of Beguilement, Locus of Grace, Locus of Wrath, Lucky Banner, Mace of Ulumak, Manann's Luck, Master of the Skies, Mirror (Grom's Big Waaagh!), Mirror (Waaagh!), Monstrous Strength, Mortal Blow (incl. upgraded), Mumbo-Jumbo Chant, Necrostrike, Nurgle's Favoured Son, Opal Amulet, Oracle of Eternity, Pendant of Slaanesh, Plaguefather's Oration, Primal Roar, Puncture.

**Approved — charge and in melee (3)** — user chose “Charge and in melee (like Fangspike)” for each; activate in the charge window OR in melee (and not fleeing), cast on self:
- **Heart Piercing** (`wh2_dlc11_lord_abilities_heart_piercing`)
- **Horn of the First Beast** (`wh_dlc03_item_abilities_horn_of_the_first_beast`)
- **Morglor the Mangler** (`wh3_dlc26_weapon_abilities_morglor_the_mangler`)

**Skipped for now — revisit (2):**
- **Locus of Contagion** (`wh3_main_character_abilities_locus_of_contagion`) — user: “Skip for now.”
- **Mad Cap Mushrooms** (`wh_main_hero_abilities_mad_cap_mushrooms`) — user: “Skip for now”; effect is ability recharge, not combat.

**Rejected (4)** — no automatic logic; left to the player:
- **Harvestman's Scythe** (`wh3_dlc29_item_active_harvestmans_scythe`) — drawback: Bonus vs Infantry -100% (standing rule 2).
- **Healing Elixirs** (`wh3_dlc20_lord_abilities_healing_elixirs`) — mutual exclusivity (standing rule 3).
- **In the Name of War** (`wh3_dlc29_lord_abilities_in_the_name_of_war`) — loss of control: Rampage (standing rule 4/7).
- **Manus of Ursun** (`wh3_main_weapon_abilities_ursuns_claws`) — Rampage; affects self and allies (standing rule 4/7).

**Also skipped as unsuitable at collection time (not part of the 40 decided):** Horn of the Wild Hunt (`wh_dlc05_item_abilities_horn_of_the_wild_hunt`) — charge-only; Hurricane of Death (`wh3_dlc25_character_abilities_hurricane_of_death`) — vortex; Maneater Smoke Bomb (`wh3_dlc26_unit_abilities_maneater_smoke_bomb`) — vortex.

## 7. Decisions log — melee questionnaire, block 4

Block 4 of the melee questionnaire is complete (tracker items §2 #132–#173; 42 items examined). **Block-4 approved total: 36 — 33 `approved (in-melee self)` + 3 `approved (charge and in-melee)`.** Decisions are recorded inline (§2 entries carry a `Decision:` note; §3a rows carry the status) and summarised here.

**Approved — in melee (and not fleeing): cast on self (33):** Quicksilver Strike, Rage Embodied, Rage Incarnate, Rapier of Ecstasy, Red Ruin, Refuse to Die, Revenge Incarnate, Rok of Itza, Rot or Die!, Rot-pocked Axe, Rune Axe of Gotrek, Rune Axe of Grombrindal, Runefang, Sacred Spawning of Xhotl, Sands of Sickness, Scales of the Celestial Court, Sceptre of Titans, Scourge, Scrying Stone, Seduction of the Serpent, Shadow Shroud, Shield of Aeons, Shield of Faith, Silver Dagger, Skull Wand of Kaloth, Slippery, Sliverslash, Smash 'Em Faster, Stand or Die!, Starcrusher, Steppe Hunter's Horn, Stinky Giant Club, Sword of Anti-Heroes.

**Approved — charge and in melee (3)** — user chose “Charge and in melee (like Fangspike)” for each; activate in the charge window OR in melee (and not fleeing), cast on self:
- **Star Lance** (`wh2_dlc15_weapon_abilities_star_lance`)
- **Storm Rage** (`wh3_dlc20_unit_abilities_storm_rage`)
- **Stormlance** (`wh3_dlc25_item_abilities_stormlance`)

**Skipped for now — revisit (2 items):**
- **Seductive Glory** (`wh3_main_lord_abilities_seductive_glory`) — drawback + Rampage; user: “Skip for now.”
- **Seismic Snare** (`wh2_dlc14_unit_abilities_seismic_snare` + `wh3_dlc29_unit_abilities_stormfiend_seismic_snare`) — user: “Skip for now.”

**Excluded of scope (1)** — `excluded (magic scope)`:
- **Sword of Teclis** (`wh2_main_weapon_abilities_sword_of_teclis`) — user: “Skip - it's a magic-resource ability (excluded scope)”.

**Correction — Quickblood is NOT a duplicate (1):** CORRECTED 2026-10-08 (the earlier “duplicate” call was wrong). Quickblood is **`approved (in-melee self)`** — activate when in melee and not fleeing, cast on self. It is a **distinct ability**, not the same as block 3's **Lightning Reflexes**: block 4's Quickblood uses `wh3_dlc29_lord_abilities_lightning_reflexes` (WH3 DLC29 prefix) while block 3's Lightning Reflexes uses `wh2_dlc11_lord_abilities_lightning_reflexes` (WH2 DLC11 prefix) — different keys, different db prefixes. Both statuses were updated (§2 #132 and the §3a row).

**Also skipped as unsuitable at collection time (2):**
- **Silver Horn of Vengeance** (`wh_main_item_abilities_silver_horn_of_vengeance`) — charge-only.
- **Swiftness of Itzl** (`wh2_main_character_abilities_swiftness_of_itzl`) — movement/vortex.

**Key-availability note (verified against the game dump, 2026-10-08):** the block-4 questionnaire listed `wh_dlc08_item_abilities_silver_horn_of_vengeance` for the charge-only Silver Horn of Vengeance, but **that key does not exist**. A grep for `silver_horn` across the extracted game data (`%LOCALAPPDATA%\Temp\wh3\`) returns **only** `wh_main_`-prefixed keys — `wh_main_item_abilities_silver_horn_of_vengeance` plus its matching ancillary id `wh_main_anc_enchanted_item_silver_horn_of_vengeance` — `unit_abilities.tsv:2978`, `unit_spec_abil.tsv:2972`, `phases.tsv:2373`, `phase_junc.tsv:2581`, `unit_abilities.loc.tsv:2978` (onscreen name) and `:6157` (tooltip). No `wh_dlc08_item_abilities_silver_horn_of_vengeance` occurs anywhere in the dump; the `wh_dlc08_item_abilities_*` namespace does exist (e.g. `seafang`, `arachnarok_eggs`, `vial_of_troll_blood`) but holds no silver_horn entry. So the tracker's **existing row already carries the correct key** — `wh_main_item_abilities_silver_horn_of_vengeance` (§2 #159 / §3a, `skipped (unsuitable: charge-only)`) — and no second row is needed.

## 8. Decisions log — melee questionnaire, block 5

Block 5 is collected (tracker items §2 #174–#213; 40 items examined → 14 auto-accepted, 23 questionnaire candidates, 1 skipped as unsuitable, 2 auto-rejected). The trivial self-buff **auto-accept rule was corrected** and the block re-filtered against the **real game-data phases** (`%LOCALAPPDATA%\Temp\wh3\uieff\block5.json`, `block5_run.txt`), not just the wiki effect lines.

**Rule correction (2026-10-08).** Imbuements and attributes no longer block auto-acceptance. The user, correcting the earlier run that left **The Eternal Blade** on the questionnaire: **“Yes, and should have been accepted from the beginning as I said. Please do not show me the trivial ones like this.”** The Eternal Blade is Base/AP Weapon Damage +50% and Melee Attack +40 — exactly the trivial self-buff shape the rule names. The earlier run rejected it because the wiki line hid the real targeting: its phase junction is `target_self=true, target_friends=true` (self **and allies**), whereas the two items accepted at collection time have a pure-self junction. Corrected: self-cast is decided by the game's own `ai_usage` field, which classifies The Eternal Blade as `augment_melee_self` (effect range 0, self buff) — so it counts as a trivial self-buff. The same field keeps genuine ally/area buffs out (e.g. Tenebrous Forge-Hammer is `augment_melee_area`).

**Auto-accepted — `approved (in-melee self - auto, trivial)` (12 new this pass):**
- **Sword of Torgald** (`wh_dlc08_weapon_abilities_sword_of_torgald`) — Base/AP Weapon Damage +50% (imbuements Inevitable End!, Magical Attacks ignored).
- **The Black Axe of Krell** (`wh3_dlc29_item_abilities_black_axe_of_krell`) — Melee Attack +24, Base/AP Weapon Damage +30% (Disembowelled! ignored).
- **The Black Cleaver** (`wh3_dlc25_weapon_abilities_the_black_cleaver`) — Melee Attack +24, Base/AP Weapon Damage +25% (Magical Attacks ignored).
- **The Blessed Blade of Ptra** (`wh2_dlc09_weapon_abilities_blessed_blade_of_ptra`) — self weapon-imbuements only (Flaming Attacks, Blinded!, Magical Attacks); no non-imbuement effect, still a pure self weapon buff.
- **The Dragon's Fang** (`wh3_dlc24_weapon_abilities_dragons_fang`) — Melee Attack +40, Base/AP Weapon Damage +50% (Executioner ignored).
- **The Eternal Blade** (`wh3_main_weapon_abilities_the_eternal_blade`) — Melee Attack +40, Base/AP Weapon Damage +50%. *(the user's example)*
- **The Mace of Helsturm** (`wh_main_weapon_abilities_the_mace_of_helsturm`) — Base Weapon Damage +60% (Flaming Attacks ignored).
- **The Rotaxes** (`wh3_dlc29_item_active_the_rotaxes`) — Melee Attack +24, Base/AP Weapon Damage +50% (Executioner ignored).
- **The Slayer Sword** (`wh3_dlc26_weapon_abilities_the_slayer_sword`) — Melee Attack +24, Base/AP Weapon Damage +50% (Weakened ignored).
- **The Talabecland Runefang** (`wh2_dlc13_weapon_abilities_talabecland_runefang`) — Melee Attack +40 (Sundered Armour ignored).
- **The Tenderiser** (`wh3_main_weapon_abilities_the_tenderiser`) — Base/AP Weapon Damage +50%.
- **Tombstrike** (`wh2_dlc09_character_abilities_strike_of_tombs`) — Melee Attack +24, Base Weapon Damage +30% (Can Cause Terror ignored).

**Already auto-accepted at collection (2):** The Ostland Runefang (`wh2_dlc13_weapon_abilities_ostland_runefang`), The Sword of Lyonesse (`wh2_dlc14_weapon_abilities_sword_of_lyonesse`) — both now also carry the `approved (in-melee self - auto, trivial)` status.

**Still on the questionnaire (23)** — each blocked by a non-MA/MD/WS effect or by non-self targeting (after ignoring imbuements/attributes):
- **Tempest Rage** (`wh3_dlc20_lord_abilities_tempest_rage`) — charge bonus.
- **Tenebrous Forge-Hammer** (`wh3_dlc27_weapon_abilities_tenebrous_forge_hammer`) — ally/area targeting (35 m, `augment_melee_area`).
- **The Armour of Morkar** (`wh3_dlc20_item_abilities_the_armour_of_morkar`) — ally/area targeting (35 m).
- **The Bane Spear** (`wh3_main_weapon_abilities_banespear`) — direct damage (area).
- **The Blood Price** (`wh2_dlc14_lord_abilities_the_blood_price`) — resistance (+self-damage).
- **The Carstein Ring** (`wh_dlc04_item_abilities_the_carstein_ring`) — resistance.
- **The Daemon's Curse** (`wh2_dlc14_lord_abilities_the_daemons_curse`) — hex on enemies, negative values.
- **The Dancing Blade** (`wh3_dlc23_character_abilities_sword_dance`) — enemy debuff + physical resistance.
- **The Drakwald Runefang** (`wh2_dlc13_weapon_abilities_drakwald_runefang`) — resistance + vigour change.
- **The Father of Blades** (`wh3_dlc25_weapon_abilities_the_father_of_blades`) — enemy debuff (MA −24), self phase only +25% AP WS.
- **The Hochland Runefang** (`wh2_dlc13_weapon_abilities_hochland_runefang`) — hex, negative values.
- **The Horn of Kygor** (`wh2_main_item_abilities_the_horn_of_kygor`) — charge bonus + leadership.
- **The Nordland Runefang** (`wh2_dlc13_weapon_abilities_nordland_runefang`) — direct damage.
- **The Ostermark Runefang** (`wh2_dlc13_weapon_abilities_ostermark_runefang`) — ally/area targeting + bonus vs large.
- **The Phoenix Blade** (`wh3_dlc27_weapon_abilities_the_phoenix_blade`) — bonus vs large.
- **The Reikland Runefang** (`wh_main_weapon_abilities_the_reikland_runefang`) — ally/area targeting + leadership.
- **The Rock of Inevitability** (`wh3_main_item_abilities_the_rock_of_inevitability`) — hex, negative values, speed.
- **The Slayer of Kings** (`wh_dlc01_weapon_abilities_the_slayer_of_kings`) — splash attack power.
- **The Sword of Couronne** (`wh_main_weapon_abilities_the_sword_of_couronne`) — hex, negative values.
- **Tor's Battle Hymn** (`wh3_main_character_abilities_tors_battle_hymn`) — ally/area targeting (35 m).
- **Tormentor Sword** (`wh_main_weapon_abilities_tormentor_sword`) — enemy debuff (MA −24).
- **Toad Rage** (`wh2_dlc12_unit_abilities_toad_rage`) — rampage.
- **Transfix** (`wh2_dlc11_lord_abilities_transfix`) — speed + resistance.

**Auto-rejected at collection (2):** The Praise of Slaanesh, The Waltz of Lethargy — mutual exclusivity (standing rule 8). **Skipped as unsuitable at collection (1):** The Wissenland Runefang — movement.

**Re-filter artifacts.** The corrected filter is encoded in `%LOCALAPPDATA%\Temp\wh3\uieff\build_block5.py` — `auto_accept()` now decides self-cast from the game's `ai_usage` field (`augment_melee_self`), ignores imbuements and attributes (except **rampage**, which still blocks), and otherwise requires only positive Melee Attack / Melee Defence / Weapon Strength. Refreshed outputs: `block5.json`, `block5_run.txt` (the pre-correction copy is kept as `block5_run.orig.txt`).

**Block-5 questionnaire decisions (this round, 2026-10-08).** The user reviewed the 23 remaining block-5 candidates and **approved them all** — 20 `approved (in-melee self)`, 2 `approved (charge and in-melee)`, and 1 `approved (in-melee self - auto, trivial)`. The two combined-trigger items are **Tempest Rage** (`wh3_dlc20_lord_abilities_tempest_rage` — Kholek Suneater; charge bonus) and **The Horn of Kygor** (`wh2_main_item_abilities_the_horn_of_kygor` — charge bonus + leadership). Two user quotes record the round:
- On **The Eternal Blade** (`wh3_main_weapon_abilities_the_eternal_blade`): **“Yes, and should have been accepted from the beggining as I said. Please do not show me the trivial ones like this.”** — the correction already reflected above.
- On **The Slayer of Kings** (`wh_dlc01_weapon_abilities_the_slayer_of_kings`): **“Yes, and also trivial.”** — so its only positive effect, **Splash Attack Power**, was added to the trivial set: standing rule 9 now reads Melee Attack / Melee Defence / Weapon Strength / **Splash Attack Power**, and The Slayer of Kings is `approved (in-melee self - auto, trivial)`.
Decisions are recorded inline (§2 entries carry a `Decision:` line; §3a rows carry the status). No block-5 questionnaire candidates remain; the block is fully decided.

## 9. Decisions log — implementation round (blocks 4, 5 and 6, 2026-10-08)

**The big implementation round.** Derived PROGRAMMATICALLY from this tracker: every §2/§3a row whose status was an `approved (...)` status AND whose key was not already in the mod — 74 keys from blocks 4 and 5 — plus block 6's **11 auto-accepted trivial self-buffs** (standing rule 9) and the **two new trigger types** the user designed. **87 new entries**; the mod's abilities table is now **189 entries / 195 keys**.

- **In-melee self (80 new on the shared `melee_unwavering` evaluator):** 54 block-4/5 `approved (in-melee self)` + 15 block-5 and 11 block-6 `approved (in-melee self - auto, trivial)` auto-accepts.
- **Charge and in melee (5 new on the existing `charge_or_melee` evaluator):** Star Lance, Storm Rage, Stormlance (block 4), Tempest Rage, The Horn of Kygor (block 5).
- **Will of the Verminking** (`wh3_dlc29_lord_abilities_will_of_the_verminking`) — trigger `verminking_wavering`; a named conservative trigger range `FOURTH.VERMINKING_RANGE_M = 25` (the game data gives a 35 m ally aura: `unit_spec_abil.tsv` `effect_range = 35.0000`); the CLOSEST in-range in-melee **wavering** ally is chosen, the gap is re-checked immediately before the cast (skip on drift), cast on SELF.
- **Potion of Toughness** (`wh_main_item_abilities_potion_of_toughness`) — trigger `melee_health75`; in melee AND own health ≤ 75%, reusing the shared live health read and the plain hysteresis-free threshold (no second threshold).
- **Army-bar exclusion (standing rule 10):** Oath of Replenishment (`wh2_dlc15_army_abilities_oath_of_replenishment` + `_upgraded`) and Shanty: First/Second Verse (`wh2_dlc11_army_abilities_shanty_verse_1`/`_2` + `_ai` twins) are `skipped (army-bar ability)`.

No approved-but-unimplemented item remains.



## 10. Decisions log — melee questionnaire, blocks 7, 8 and 9 (collected 2026-10-08)

Blocks 7–9 are collected (`%LOCALAPPDATA%\Temp\wh3\uieff\block7.json`, `block8.json`, `block9.json`, `blocks789_run.txt`, built by `build_blocks789.py`). They continue the ordered list at **§2 #254**, i.e. immediately after block 6 (§2 #214–#253). Range: **#254–#373** (120 items scanned: **75 questionnaire candidates, 4 auto-accepted trivial self-buffs, 41 excluded**; 0 auto-rejected). **Block 7 is now decided** — see the *Block-7 answers* note at the end of this section; **block 8 is now complete** (see the *Block-8 answers (in progress)* and *Block-8 complete / block-9 (in progress)* notes); **block 9 is now complete** (see the *Block-8 complete / block-9 (in progress)* and *Block-9 complete — final item #373* notes).

Review document: `C:\Users\vlady\Desktop\WH3_mod\docs\WH3_blocks_7-8-9_review.md`.

**Auto-accepted — `approved (in-melee self - auto, trivial)` (4):** Talisman of Loec (`wh2_main_item_abilities_talisman_of_loec`), Warrior Familiar (`wh3_dlc27_item_abilities_warrior_familiar`), Curse of Years (`wh3_dlc29_spell_bound_curse_of_years`), Okkam's Mindrazor (`wh3_dlc29_spell_bound_okkams_mindrazor`).

**Block 7 — excluded (16):** Shanty: Third Verse (army-bar ability), Thundermace (vortex), Venom Wave (vortex), Whirlwind of Death (vortex), Wrath of Ptra (vortex), Ark of Sotek (vortex), Battle Howl (movement), Call of Tor (bombardment/ranged), Celestial Sweep (vortex), Destruction (vortex), Ferocious Destruction (vortex), Grand Soulfire (bombardment/ranged), Kill for Khorne! (vortex), Sonic Boom (vortex), Soulfire (bombardment/ranged), The Hammer of Harry (vortex).
**Block 8 — excluded (15):** Alakanash, the Staff of Power (vortex), Cellular Instability (vortex), Eruption (vortex), Glacial Blast (vortex), Splode da Big 'Un! (vortex), Horn of Khorne (army-bar ability), Twilight Horn II (movement), Armour of Contempt (army-bar ability), Gate of Khorne (spawned/ranged), Gate of Nurgle (spawned/ranged), Gate of Slaanesh (spawned/ranged), Greater Gate of Khorne (spawned/ranged), Greater Gate of Nurgle (spawned/ranged), Greater Gate of Slaanesh (spawned/ranged), Greater Gate of Tzeentch (spawned/ranged).
**Block 9 — excluded (10):** The Tallyman's Blades (spawned/ranged), Mors Clanstone (army-bar ability), Pestilens Clanstone (army-bar ability), Rictus Clanstone (army-bar ability), Ancestral Rune of Grungni (army-bar ability), Basking in Our Flame (army-bar ability), The Airless Fires (army-bar ability), The Burning Waters (army-bar ability), The Unmasking (army-bar ability), Time Amok (movement).

**Block 7 — questionnaire candidates (22):** Skull of Katam, Slayer for Chaos, The Black Gem of Gnar, Vial of Troll Blood, Warpstone Addiction, Witchbrew, World's Edge Armour, Znarkharja's Ward, Battle of Wills, Ferocious Battle Howl, Ferocious Fury of Ulric, Ferocious Winter’s Chill, Flame Incarnate, Formless Horror, Fury of Ulric, Immovable Bulwark, Primeval Roar, Rune of Doom, The Shadow's Coil, Transformation of the Dragon, Unstoppable Choppas, Winter’s Chill.

**Block 8 — questionnaire candidates (23):** Bangers & Smash, Death Frenzy, Dragonhorn, Greater Faith Bastion, Cash Cascade, Empowering Shrooms, Enchanted Metallurgy, Enchanted Metallurgy: Flaming, Enchanted Metallurgy: Piercing, Enchanted Metallurgy: Poison, Massacre, Master of Alchemy, Master of Alchemy: Flaming, Master of Alchemy: Piercing, Master of Alchemy: Poison, Spite of Da Bad Moon, "Stay Here, I'll Get Help!", Breath of Hatred, Master Rune of Oath & Steel, Master Rune of Speed, Rune of Oath & Steel, Rune of Speed, Birona's Timewarp.

**Block 9 — questionnaire candidates (30):** From the Shadows, Lord of Grand Cathay, Shield of the Old Ones, Supreme Shield of the Old Ones, Gaze of Khaine, Star of Avelorn, The Liber Mortis, Gulyas, Mirror of Knowledge, Fog of the Damned, Bastion's Defenders, Beastlord's Gaze, Captain of the Phoenix Guard, Da Boss 'as a Plan!, Favour of the Fay, Fury of Khaine, Helm of Yvresse, Helping Hand, Inspired Assault I, Inspired Assault II, Inspired Assault III, Inspired Defence I, Inspired Defence II, Inspired Defence III, Mantra of Invigoration, Mantra of Righteousness, Meat Feast, Offering to the Gods, Orcs are da Best!, Overseer of the Unseen.


**Block-7 answers (recorded 2026-10-09).** The user reviewed the **22 block-7 questionnaire candidates** (§2 #254–#293) plus the **first block-8 item** (§2 #295, Bangers & Smash) — **23 items in all**. Outcome: **19 approved** — **14 `approved (in-melee self)`** and **5 approved with a different trigger** (four of them introducing **new trigger variants**) — and **4 skipped**. Decisions are recorded inline (§2 entries carry a `Decision:` line; §3a rows carry the status).

**Approved — in melee (and not fleeing): cast on self (14):** Slayer for Chaos, Warpstone Addiction, Witchbrew (`wh2_main_character_abilities_witchbrew` + `wh3_dlc24_unit_abilities_witchbrew`), World's Edge Armour, Znarkharja's Ward, Battle of Wills, Ferocious Winter’s Chill, Flame Incarnate, Immovable Bulwark, Primeval Roar, Rune of Doom, The Shadow's Coil, Unstoppable Choppas, Winter’s Chill (`wh3_dlc29_ability_bound_prayer_winters_chill` + `wh3_dlc29_spell_bound_prayer_winters_chill`).

**Approved with a different trigger (5)** — the user's quotes are verbatim; the trigger changes are quoted here:
- **Vial of Troll Blood** (`wh_dlc08_item_abilities_vial_of_troll_blood`) — `approved (wavering self)`. User: **“Only when wavering”** → cast on self when the owner is wavering (no melee arm). *(NEW variant)*
- **Ferocious Battle Howl** (`wh3_dlc29_spell_bound_prayer_ferocious_battle_howl`) — `approved (charge only)`. User: **“Charge only”** → activate in the charge window only, cast on self (no melee arm). *(NEW variant)*
- **Ferocious Fury of Ulric** (`wh3_dlc29_spell_bound_prayer_ferocious_fury_of_ulric`) — `approved (wavering self)`. User: **“Only when wavering (like Vial of Troll Blood)”**.
- **Fury of Ulric** (`wh3_dlc29_spell_bound_prayer_fury_of_ulric`) — `approved (wavering self-or-ally in range)`. User: **“When wavering (self or ally in range)”** → cast on self when the owner **or an ally in range** is wavering. *(NEW variant)*
- **Bangers & Smash** (`wh2_dlc15_character_abilities_sausage_busta`, block 8 #295) — `approved (charge or wavering)`. User: **“When charging or wavering”** → activate in the charge window **OR** when wavering, cast on self. *(NEW variant)*

**Skipped (4):**
- **Skull of Katam** (`wh_main_item_abilities_skull_of_katam`) — `skipped (magic scope + self-damage)`. User: **“Skip - magic-resource + self-damage”**.
- **The Black Gem of Gnar** (`wh3_dlc23_item_abilities_black_gem_of_gnar`) — `skipped (revisit)`. User: **“Skip for now”**.
- **Formless Horror** (`wh3_dlc24_lord_abilities_formless_horror` + `wh3_dlc24_lord_abilities_formless_horror_quest_battle`) — `skipped (revisit)`. User: **“Skip for now”**. **Its `Effects` line is `<unknown>` in the review doc** (`WH3_blocks_7-8-9_review.md` §280, line 154 — “Effects: <unknown> (other source)”); the effect must be **RECONSTRUCTED from the game data** before this item can ever be decided.
- **Transformation of the Dragon** (`wh3_dlc24_lord_abilities_jade_dragon_dragon_form` + `wh3_main_lord_abilities_iron_dragon_dragon_form` + `wh3_main_lord_abilities_storm_dragon_dragon_form`) — `skipped (revisit)`. User: **“Skip for now”**.

**New trigger variants now in use (4 new codes).** Beyond the existing `in-melee self` / `charge and in-melee` / `verminking_wavering` / `melee_health75`, block 7 adds four new trigger variants (all defined in the legend at the top of this file): **charge-only** (`approved (charge only)`), **wavering (self)** (`approved (wavering self)`), **wavering (self-or-ally in range)** (`approved (wavering self-or-ally in range)`), and **charge-or-wavering** (`approved (charge or wavering)`). Each must be built as a distinct evaluator. *(The charge-only and charge-or-wavering codes share the charge-window read; the two wavering codes share the morale/wavering read — the self-or-ally one additionally scans allies in range.)*

**Block-8 answers (in progress) (recorded 2026-10-09).** The user has begun reviewing the **23 block-8 questionnaire candidates** (§2 #294–#333). **16 are newly decided here**; adding **Bangers & Smash** (§2 #295, already recorded with the block-7 answers) makes **17 of 23** decided, leaving **6 open**. Decisions are recorded inline (§2 entries carry a `Decision:` line; §3a rows carry the status).

**Approved — in melee (and not fleeing): cast on self (6):** Death Frenzy (`wh2_dlc16_spell_bound_death_frenzy`), Dragonhorn (`wh2_dlc15_lord_abilities_dragonhorn`), Greater Faith Bastion (`wh_dlc06_quest_abilities_grand_faiths_bastion`), Empowering Shrooms (`wh3_dlc26_character_abilities_empowering_shrooms`), Massacre (`wh3_main_prisoners_massacre`), Spite of Da Bad Moon (`wh_dlc06_lord_abilities_spite_of_da_bad_moon`).

**Approved — charge and in melee (1):** Cash Cascade (`wh3_dlc26_character_abilities_cash_cascade`) — `approved (charge and in-melee)`, mirroring Fangspike (activate in the charge window OR in melee, and not fleeing; cast on self).

**Approved with the NEW trigger `approved (melee self-or-ally / shooting ally in range)` (8) — the four Enchanted Metallurgy abilities and the four Master of Alchemy abilities:**
- **Enchanted Metallurgy** (`wh3_main_character_abilities_enchanted_metallurgy`), **: Flaming** (`_flaming`), **: Piercing** (`_piercing`), **: Poison** (`_poison`). User: **“When self or ally in range in melee. When ally in range is shooting.”**
- **Master of Alchemy** (`wh3_main_lord_abilities_master_of_alchemy`), **: Flaming** (`_flaming`), **: Piercing** (`_piercing`), **: Poison** (`_poison`). User: **“Same as the Metallurgies (melee self-or-ally / shooting ally)”**
→ IMPLEMENTED (harness89) for the **FOUR Enchanted Metallurgy** abilities: fire when the owner is in melee, OR any friendly unit other than the caster is in melee within the conservative 25 m `FOURTH.METALLURGY_RANGE_M` (game-data 35 m aura); CAST ON SELF (closest ally, pre-cast gap re-check, skip on drift). **THE SHOOTING HALF IS NOT BUILT — research complete: the battle API exposes no per-unit is-firing / is-shooting read, so no proxy was invented.** The four **Master of Alchemy** abilities remain `approved` (not yet implemented). *(NEW variant)*

**Approved with the NEW trigger `approved (wavering ally in range)` (1):** **“Stay Here, I'll Get Help!”** (`wh2_dlc09_character_abilities_stay_here_ill_get_help`). User: **“If ally in range is wavering.”** → cast on an ally in range that is wavering; **no melee requirement — the ally need not be in melee** (the wording does not require the ally to be in melee; implement as ally wavering within range). Same evaluator shape as Will of the Verminking (closest ally in range, conservative range, drift re-check). *(NEW variant)*

**Still open (block 8 — 0):** none — the last five block-8 items (#321–#325) were recorded as `approved (in-melee self)` in the follow-up round (see the note below). Plus block 9 (30 candidates; 30 decided — complete; see the note below).

**Block-8 complete / block-9 (in progress) (recorded 2026-10-09).** The **last block-8 questionnaire item** — **Birona's Timewarp** (`wh_main_spell_bound_bironas_timewarp`, §2 #326) — was answered **charge and in melee** (`approved (charge and in-melee)`, mirroring Fangspike §2 #68 / Heart Piercing §2 #91): activate in the charge window OR in melee (and not fleeing), cast on self. *(Follow-up round, recorded 2026-10-09: the five remaining block-8 items — Breath of Hatred (#321), Master Rune of Oath & Steel (#322), Master Rune of Speed (#323), Rune of Oath & Steel (#324) and Rune of Speed (#325) — were recorded as `approved (in-melee self)` (activate when in melee and not fleeing, cast on self). Their answers were re-confirmed by the user in this round after a context compaction lost the originals. §3a now shows no `proposed` rows for block 8.)*

The user has also begun **block 9** (§2 #334–#373; 30 questionnaire candidates). **30 items are decided (block 9 complete)** — **15 `approved (in-melee self)`**, **4 `approved (health<=75, no melee gate)`**, **1 `approved (in melee and health<=75)`**, **4 `approved (charge and in-melee)`**, **1 `approved (wavering self)`**, **1 rejected** and **4 skipped** — with **4 approved on the health-only trigger** and **1 on the new melee+health trigger**.

**Approved — in melee (8, all `approved (in-melee self)`):** Lord of Grand Cathay (`wh3_dlc24_lord_abilities_lord_of_grand_cathay`, #336), Shield of the Old Ones (`wh2_main_character_abilities_shield_of_the_old_ones`, #337), Supreme Shield of the Old Ones (`wh2_dlc12_character_abilities_supreme_shield_of_the_old_ones`, #338), Gaze of Khaine (`wh2_dlc10_lord_abilities_gaze_of_khaine`, #339 — approved despite the **Rampage!** flag; standing rule 7), The Liber Mortis (`wh2_dlc09_lord_abilities_the_liber_mortis`, #344) and Bastion's Defenders (`wh3_dlc24_character_abilities_bastions_defenders`, #354). The first five cast **at own feet** (existing ground-cast path); Bastion's Defenders casts **on self for now** (nearest-ally picker later). Also **Da Boss 'as a Plan!** (`wh3_dlc26_character_abilities_da_boss_as_a_plan`, #357) and **Favour of the Fay** (`wh_dlc07_lord_abilities_favour_of_the_fay`, #358) — both cast on self for now (nearest-ally picker later).

**Rejected (1):** From the Shadows (`wh2_dlc14_character_abilities_from_the_shadows`, #335) — `rejected (stealth/escape effect)`. User: **“No automatic logic (stealth/escape effect)”**.

**Approved on the NEW health-only trigger `approved (health<=75, no melee gate)` (2):**
- **Star of Avelorn** (`wh2_dlc10_item_abilities_star_of_avelorn`, #343) — user: **“When below 75% health. No need to use in melee as it has no melee effects as the Potion of Toughness”**.
- **Gulyas** (`wh3_dlc24_lord_abilities_gulyas`, #345) — user chose **“Below 75% health (no melee gate)”**.
Both cast on self when own health ≤ 75%, **with no melee requirement** — the same health-only evaluator as **Ghoul King of Ushoran**.

**The health-only pattern (own health ≤ 75%, no melee gate) now has FIVE members:** **Ghoul King of Ushoran** (§2 #79), **Star of Avelorn** (§2 #343), **Gulyas** (§2 #345), **Mantra of Invigoration** (§2 #368) and **Meat Feast** (§2 #370). **Potion of Toughness differs deliberately** (block 6, `melee_health75`): it fires **in melee AND at ≤ 75% health** because it **also grants armour/defence**, so the melee gate is meaningful there; the health-only shape is used only where the effect carries **no melee component**. The **melee+health** shape (in melee AND at ≤ 75% health) now has a **SECOND member**: **Captain of the Phoenix Guard** (§2 #356, block 9) — approved on this gate because it **also grants Physical Resistance to allies**, so the melee gate is meaningful.

**Skipped for now (3):** Mirror of Knowledge (`wh3_dlc24_item_abilities_mirror_of_knowledge`, #346), Fog of the Damned (`wh3_dlc29_bound_deep_fog_of_the_damned`, #349) and Beastlord's Gaze (`wh2_twa03_lord_abilities_beastlords_gaze`, #355) — all `skipped (revisit)`.


**Block-9 (continued) (recorded 2026-10-09).** Five more block-9 items decided (§2 #355–#359), bringing block 9 to **16 of 30**. Outcomes: **2 `approved (in-melee self)`**, **1 `approved (in melee and health<=75)`** (NEW trigger variant), **1 `approved (charge and in-melee)`**, and **1 `skipped (revisit)`**. Decisions are recorded inline (§2 entries carry a `Decision:` line; §3a rows carry the status).

**Approved — in melee (2, `approved (in-melee self)`):** **Da Boss 'as a Plan!** (`wh3_dlc26_character_abilities_da_boss_as_a_plan`, #357) and **Favour of the Fay** (`wh_dlc07_lord_abilities_favour_of_the_fay`, #358) — when in melee and not fleeing, cast on self for now (nearest-ally picker later).

**Approved on the NEW melee+health trigger `approved (in melee and health<=75)` (1):** **Captain of the Phoenix Guard** (`wh3_dlc27_character_abilities_captain_of_the_phoenix_guard`, #356). User: **“In melee and below 75% health”** — the Potion-of-Toughness gate (`melee_health75`): cast on self when in melee AND at ≤ 75% health. Chosen rather than the health-only gate of Star of Avelorn/Gulyas because the ability **also grants Physical Resistance to allies**, so the melee gate is meaningful. *(NEW variant)*

**Approved — charge and in melee (1):** **Fury of Khaine** (`wh2_main_unit_abilities_fury_of_khaine`, #359) — `approved (charge and in-melee)`, user: **“Charge and in melee”**; joins the Fangspike family (activate in the charge window OR in melee, and not fleeing; cast on self).

**Skipped for now (1 more):** **Beastlord's Gaze** (`wh2_twa03_lord_abilities_beastlords_gaze`, #355) — `skipped (revisit)`. User: **“Skip for now”**.

**Block-9 (continued, #360–#367) (recorded 2026-10-09).** Eight more block-9 items decided (§2 #360–#367), bringing block 9 to **24 of 30**. Outcomes: **4 `approved (in-melee self)`** (Helping Hand #361; Inspired Defence I/II/III #365–#367), **3 `approved (charge and in-melee)`** (Inspired Assault I/II/III #362–#364) and **1 `approved (wavering self)`** (Helm of Yvresse #360). Decisions are recorded inline (§2 entries carry a `Decision:` line; §3a rows carry the status).

**Approved — in melee (4, `approved (in-melee self)`):** **Helping Hand** (`wh2_pro08_character_abilities_helping_hand`, #361) and **Inspired Defence I/II/III** (`wh3_main_lord_abilities_inspired_defence_i`/`_ii`/`_iii`, #365–#367) — when in melee and not fleeing, cast on self for now (nearest-ally picker later).

**Approved — charge and in melee (3, `approved (charge and in-melee)`):** **Inspired Assault I/II/III** (`wh3_main_lord_abilities_inspired_assault_i`/`_ii`/`_iii`, #362–#364) — the Fangspike family: activate in the charge window OR in melee (and not fleeing), cast on self.

**Approved on the wavering trigger `approved (wavering self)` (1):** **Helm of Yvresse** (`wh2_dlc15_item_abilities_helm_of_yvresse`, #360). User: **“Only when wavering (like Vial of Troll Blood)”** — cast on self only while the owner is wavering (no melee arm). **The Unbreakable / wavering pattern now has THREE members:** **Vial of Troll Blood** (§2 #261, block 7), **Ferocious Fury of Ulric** (§2 #277, block 7) and **Helm of Yvresse** (§2 #360, block 9).

**Block-9 (continued, #368–#372) (recorded 2026-10-09).** Five more block-9 items decided (§2 #368–#372), bringing block 9 to **29 of 30**. Outcomes: **2 `approved (in-melee self)`** (Mantra of Righteousness #369; Orcs are da Best! #372), **2 `approved (health<=75, no melee gate)`** (Mantra of Invigoration #368; Meat Feast #370) and **1 `skipped (revisit)`** (Offering to the Gods #371). Decisions are recorded inline (§2 entries carry a `Decision:` line; §3a rows carry the status).

**Approved — in melee (2, `approved (in-melee self)`):** **Mantra of Righteousness** (`wh3_cp1_character_abilities_offense_prayer`, #369) and **Orcs are da Best!** (`wh3_dlc26_character_abilities_orcs_are_da_best`, #372) — when in melee and not fleeing, cast on self for now (nearest-ally picker later).

**Approved on the health-only trigger `approved (health<=75, no melee gate)` (2):** **Mantra of Invigoration** (`wh3_cp1_character_abilities_protection_prayer`, #368) and **Meat Feast** (`wh3_main_prisoners_butcher`, #370) — user chose **“Below 75% health (no melee gate)”**: cast on self when own health ≤ 75%, no melee gate. **The health-only family now has FIVE members:** **Ghoul King of Ushoran** (§2 #79), **Star of Avelorn** (§2 #343), **Gulyas** (§2 #345), **Mantra of Invigoration** (§2 #368) and **Meat Feast** (§2 #370).

**Skipped for now (1 more):** **Offering to the Gods** (`wh3_dlc27_lord_abilities_offering_to_the_gods`, #371) — `skipped (revisit)`. User: **“Skip for now”**. The effect **sacrifices a friendly unit** (it deals damage to allies in range and kills entities of the targeted ally), so **no automatic logic is safe** for it.
**Block-9 complete — final item #373 (recorded 2026-10-09).** The last block-9 questionnaire candidate — **Overseer of the Unseen** (`wh3_dlc29_hero_active_overseer_of_the_unseen`, §2 #373) — was answered **in melee**: `approved (in-melee self)` — when in melee and not fleeing, cast on self for now (nearest-ally picker later). The user was offered the wider **wavering self-or-ally** form (the Fury-of-Ulric / Commanding-Presence pattern) and chose **plain in-melee self**. This brings **block 9 to 30 of 30 — COMPLETE**: **15 `approved (in-melee self)`**, **4 `approved (charge and in-melee)`**, **4 `approved (health<=75, no melee gate)`**, **1 `approved (in melee and health<=75)`**, **1 `approved (wavering self)`**, **1 rejected** and **4 skipped (revisit)**. Decisions are recorded inline (§2 entry carries a `Decision:` line; the §3a row carries the status). **No block-9 §3a row in the range §2 #334–#373 now reads `proposed`.**

---

**Auto-rule widening sweep (recorded 2026-10-09 — blocks 10, "no per-item review").** The user's direction for this round (relayed): **"tired of the five-questions-at-a-time pipeline"** and **"approved widening the auto-rules so most undecided candidates never reach him"**. Four new **standing rules (R1–R4, recorded as rules 11–14 in the header legend)** were added and applied **in one sweep** to every undecided candidate — the **781** rows still reading `proposed` plus the **218** rows reading `proposed (FF)` (**999** in all). Result: **327 auto-accepted** (`approved (auto: <trigger>)`), **325 auto-excluded** (`excluded (auto: <reason>)`), and **347 flagged** (kept `proposed` / `proposed (FF)` — the only rows the user will be asked about later). Auto-accepted by trigger: `in-melee self` 274 · `health<=75 (no melee gate)` 37 · `charge and in-melee` 16. Top auto-exclude reasons: army-bar ability (standing rule 10) 98 · summon 74 · explosive projectile 52 · vortex 29 · explosive / breath attack 29 · no effect text available (unsourceable) 25 · ground-target-only 14 · summon/transform 4. The full per-row lists are in the companion report `WH3_auto_classification_report.md` (Appendix A auto-accept, B auto-exclude, C flag), written so the user can **veto** any single auto-decision in one line. **No per-item review of the auto-decisions was performed** (faster option the user chose). **Nothing was built or installed in this round** — implementing the auto-accepted set is the next job. The friendly-fire block stays flagged (per the R4 wording "including the FF rows"); army-bar rows are auto-excluded under standing rule 10 ("Skip all army bar abilities").

---

**Auto-accepted implementation round (recorded 2026-10-09 — harness 91).** All **327** auto-accepted rows (`approved (auto: <trigger>)`) were implemented in ONE build and their §3a statuses flipped to `implemented (<trigger>)`, preserving each trigger description. They ride **three EXISTING evaluators** (no new trigger types): `in-melee self` **274** -> the shared `melee_unwavering` evaluator; `health<=75 (no melee gate)` **37** -> the `ushoran_health` evaluator; `charge and in-melee` **16** -> the `charge_or_melee` evaluator. Rows sharing an ability name ride ONE entry (base + DLC/summoned twin keys), so the 327 rows are **311 entries / 327 database keys**; the mod's abilities table grew **262 -> 573 entries** (**272 -> 599 keys**). Two name-collision entries took a name-derived marker (Horn of Vaul, Whip of Misery) so no marker repeats. Built and installed as a Movie .pack (`zz_test_deadly_onslaught.pack`); harness 91 is green (live+annotated) with a red control against the pre-edit snapshot. The friendly-fire block, the ambiguous/mixed rows and the army-bar rows remain flagged/excluded as recorded in the auto-rule sweep above.


**Pending review — field-test finding (recorded 2026-10-09).** **OPEN ITEM.** The user field-tested the abilities in battle and reports that the logic of **some abilities makes no sense** in play. He will review this later. No individual abilities are named or guessed here — this is logged as an open item to revisit once the remaining decisions are made.

---

**CLOSING ROSTER TALLY (the section-10 closing note) - the FINAL ROSTER BUILD, 2026-10-09.**

Every one of the **1,797** inventory rows (sections 3a + 3b + 3c) now carries a FINAL status; **no row anywhere reads `proposed` or `proposed (FF)`**.

| Final category | Rows |
|---|---:|
| **implemented** | 605 |
| **approved** (awaiting implementation) | 0 |
| **excluded - impossible** (engine wall / user-rejected class) | 97 |
| **excluded - by reason family** (auto/family decisions) | 1,004 |
| **skipped** (revisit / unsuitable / army-bar & magic-scope skips) | 72 |
| **rejected** (user) | 19 |
| **TOTAL** | **1,797** |

Reconcile: 605 (implemented) + 0 (approved) + 1,101 (excluded) + 72 (skipped) + 19 (rejected) = **1,797** = the inventory row count.

### The impossible rows (auto-excluded at triage time; reasons):

| Reason | Rows |
|---|---:|
| no enemy-unit read | 76 |
| no transform/shapechange support | 11 |
| already rejected by user (tactical escape/stealth) | 10 |
| **impossible total** | **97** |

### The 238 triage-family rows excluded this round (by family):

| Family | Rows |
|---|---:|
| Vortex / wandering wind | 70 |
| Bombardment / ground artillery | 63 |
| Placed / static area damage | 42 |
| Breath / cone damage | 30 |
| Own-troop-damage AoE | 26 |
| Flanking / ambush (flanking_opportunity) | 7 |
| **family total** | **238** |

### The 12 INDIVIDUAL rows resolved (6 built + 6 excluded):

| Final status | Rows |
|---|---:|
| `excluded (auto: army-bar ability (standing rule 10))` | 1 |
| `excluded (auto: enemy-ground placement (no placement path))` | 1 |
| `excluded (auto: no ammo-low read (ammo replenish))` | 3 |
| `excluded (auto: no effect text available (unsourceable))` | 1 |
| `implemented (blood_sacrifice)` | 1 |
| `implemented (eat_da_runts)` | 1 |
| `implemented (in-melee self)` | 4 |
| **individual total** | **12** |

**The flagged 347 = 97 excluded (impossible) + 238 excluded (family) + 12 individual - all resolved; totals reconcile.**

---

### 10.1 Tooltip-line fix — every implemented ability's appended line (ROUND v93, 2026-10-09)

The mod appends ONE line to each implemented special ability's tooltip. It used to be a single
generic sentence for every ability — *"Automatic: this ability fires by itself while the unit
charges - click the M/A badge ..."* — which described a **charge** behaviour most abilities do
not have (the bulk-added entries ride a handful of evaluators, none of them charge). **Fixed:** the
line is now ONE SHORT clause **composed per entry from the trigger the entry actually rides**
(`FOURTH.TRIGGER_TIP[trigger]` → `ability.tip`, wired in the evaluator-wiring loop), so every
implemented ability's line names its real evaluator. The old generic sentence is removed from the
shipped `ui/common ui/special_ability_tooltip.twui.xml`, which now carries only the short badge
hint.

| Trigger (evaluator the entry rides) | Appended line |
|---|---|
| `melee_unwavering` | When armed, fires when this unit is in melee |
| `charge_or_melee` | When armed, fires when this unit charges or is in melee |
| `charge_only` | When armed, fires when this unit charges |
| `ushoran_health` | When armed, fires when this unit is at or below 75% health |
| `melee_health75` | When armed, fires when this unit is in melee and at or below 75% health |
| `wavering_self` | When armed, fires when this unit is wavering |
| `wavering_self_or_ally` | When armed, fires when this unit or an ally in range is wavering |
| `wavering_ally_range`, `verminking_wavering` | When armed, fires when an ally in range is wavering |
| `tired` | When armed, fires when this unit is tired or worse |
| `barrier_broken` | When armed, fires when this unit's barrier breaks |
| `glorious_death` | When armed, fires when a Slayer ally in range is in melee |
| `metallurgy_melee` | When armed, fires when this unit or an ally in range is in melee |
| `blood_sacrifice` | When armed, fires on the lowest-health ally in range when it is at or below 75% health |
| `eat_da_runts` | When armed, fires when this unit is at or below 75% health, otherwise on the lowest-health ally in range |
| `charge` (Deadly Onslaught legacy charge+melee) | When armed, fires when this unit charges or is in melee |
| `melee` | When armed, fires when this unit is in melee |
| `melee_low_morale` | When armed, fires when this unit is in melee and wavering |
| `charge_or_wavering` | When armed, fires when this unit charges or is wavering |

**Harness 93:** every one of the **579** implemented entries was checked data-driven against its
trigger — **579/579** carry the allowed wording, **0 unmatched**. GREEN 2678 checks / 0 failures;
RED (pre-edit snapshot) 2645 checks / 11 designed failures. **Installed pack md5
`d83c5f93539d770fd6003cf91ce73e2d`** (all 5 ship files byte-identical to source).

**Update 2026-10-10 (ACCUSATION'S ENEMY-TARGETED TRIGGER — harness 94):** the round-4 probe's
log-confirmed enemy-targeting route is now wired into the MAIN mod as the first ENEMY-TARGETED
trigger. A NEW reusable evaluator **`enemy_engaged_or_shot`** (`FOURTH.evaluate_enemy_engaged_or_shot`)
fires when an **enemy unit within the ability's own reach is in melee OR under missile fire**:
per poll it enumerates the enemy script units (`bm:get_scriptunits_for_main_enemy_army_to_local_player()`),
keeps those that are alive + valid + in range, and of those picks one that is `is_in_melee()` **OR**
`is_under_missile_attack()` — **prefer in-melee, then the closest**. If none qualifies it stays silent.
The chosen enemy is the **CAST TARGET — never the owner** — and the cast uses the **proven
`bench_fresh` fresh-handle route**: the caster's script_unit is re-fetched fresh from the friendly
enumerator each tick (`FOURTH.eg_fresh_caster_su`) and the enemy is re-fetched fresh from the enemy
enumerator the same tick, then `caster_su.uc:perform_special_ability(key, enemy_su.unit)`. A pre-cast
re-check drops the cast if the enemy lapsed (no longer alive / in melee / under fire / in range);
the HOLD is the existing per-pair guard + cooldown hold. **The range source** is the ability's own
`target_intercept_range` (`unit_spec_abil.tsv` = 75.0000 m) stored as the named
`FOURTH.ACCUSATION_RANGE_M = 75`; the enemy is offered while `unit_in_range(enemy)` is true, else
`unit_distance(enemy) <= 75`, else the caster is in melee. **`is_under_missile_attack()` exists but
was never probed on an enemy — an unreadable read is treated as FALSE (fail-safe) with ONE log line
for the battle** (it was readable in the harness). **Accusation** (`wh_main_hero_abilities_accusation`)
moves from `melee_unwavering` to `enemy_engaged_or_shot`: melee_unwavering **481 → 480**, the new
trigger **0 → 1**. **The abilities table stays 579 entries / 605 keys** (Accusation already existed;
only its trigger changed) and **no new chunk locals** (every helper/constant/slot rides the `FOURTH`
bag). Tooltip line: *"When armed, fires when an enemy unit in range is in melee or under missile fire"*.
Harness 94: **GREEN 2772 checks / 0 failures; RED (pre94 snapshot = the shipped harness-93 build)
2739 checks / 62 designed failures** (the moved melee_unwavering pin ×12, the harness-93
wording-presence check ×2, the new section-0r tokens ×23, the firing N-world legs ×25). **Installed
pack md5 `65e66f6a87547268ae6d4c2c116558fa`** (all 5 ship files byte-identical to source, dist ==
installed). NOTE: the throwaway probe pack `zz_probe_enemy_target.pack`
(md5 `e21411bdd306db0e520f4e0b19a0244a`) is STILL installed in the game's `data/` folder from the
round-4 probe and is NOT part of this ship — delete it before field-testing (it runs its own
6-route enemy-cast sweep every battle).

---

**Update 2026-10-10 (THE STANDING 70% RANGE RULE — harness 95): the user's new STANDING RULE —
every trigger range = 70% of the ability's real range, NO exceptions.** After the Accusation field
test the user reported the **Witch Hunter WALKING** toward the target. His diagnosis and ruling
(verbatim): **"for abilities that include a range, we should always specify 70% of the actual range
to avoid such things"**, later ruled absolute: **"...No exceptions."** The rule now ships as the
named constant **`FOURTH.RANGE_FRACTION = 0.70`** and **EVERY** trigger-range constant in the mod was
re-derived as **`floor(real × 0.70)`**, where the real range is the ability's own game-data range
(`unit_spec_abil.tsv` `effect_range` when it has an aura, else its `target_intercept_range`). This is
**standing rule R5** in the header legend (§ top of this file, rule 15).

| Constant | Old | Real range (source) | 70% target | **New** |
|---|---:|---|---:|---:|
| `GLORIOUS_DEATH_RANGE_M` | 25 | **55.0000** — `effect_range`, `wh3_dlc25_lord_abilities_glorious_death` | 38.5→**38** | **38** |
| `FOURTH.VERMINKING_RANGE_M` | 25 | **35.0000** — `effect_range`, `wh3_dlc29_lord_abilities_will_of_the_verminking` | 24.5→**24** | **24** |
| `FOURTH.METALLURGY_RANGE_M` | 25 | **35.0000** — `effect_range`, `wh3_main_character_abilities_enchanted_metallurgy` (+`_flaming`/`_piercing`/`_poison`) | 24.5→**24** | **24** |
| `FOURTH.WAVERING_RANGE_M` | 25 | **35.0000** — `effect_range`, `wh3_dlc29_lord_active_commanding_presence` / `wh3_dlc29_spell_bound_prayer_fury_of_ulric` / `wh2_dlc09_character_abilities_stay_here_ill_get_help` | 24.5→**24** | **24** |
| `FOURTH.BLOOD_SACRIFICE_RANGE_M` | 25 | **100.0000** — `target_intercept_range` (no aura: `effect_range` 0.0000), `wh3_dlc26_lord_abilities_blood_sacrifice` | 70.0→**70** | **70** |
| `FOURTH.EAT_DA_RUNTS_RANGE_M` | 25 | **100.0000** — `target_intercept_range` (no aura: `effect_range` 0.0000), `wh3_dlc26_unit_abilities_eat_da_runts` | 70.0→**70** | **70** |
| `FOURTH.ACCUSATION_RANGE_M` | 75 | **75.0000** — `target_intercept_range` (no aura: `effect_range` 0.0000), `wh_main_hero_abilities_accusation` | 52.5→**52** | **52** |

**The Glorious Death exception the FIRST draft carried is VOID — the user overruled it.** The
harness-87 build kept a **field-tuned 25 m** gate for Glorious Death (the 55 m aura fired too early);
the 70% value is **38 m**, which would *loosen* it. The task first said to keep 25 m as a deliberate
"never loosen a field-tested value" exception — **the user then ruled the rule absolute ("...No
exceptions.")**, so Glorious Death was set to **38 m** at his direction and the "field-tested carve-out"
was removed from the rule. The old 25 m value is recorded here only as history.

**Not a range (audited, unchanged):** `CHARGE_MIN_DISTANCE_M = 12` and `CHARGE_MAX_DISTANCE_M = 60`
gate the **charge order's run-up window**, not an ability's range, so the 70% rule does not apply —
left exactly as they were. **No inline numeric distance comparison** remains anywhere (every gate uses
a named constant). **The appended tooltip lines name no distance**, so no tooltip wording changed.

**Harness 95:** GREEN **2856 checks / 0 failures** (live + annotated), including a new **section 0s**
that asserts the rule constant + every derived value + the derivation comments, and **28 boundary
worlds** (14 per file): for each changed constant an ally/enemy **just inside the new bound FIRES** and
one **between 70% and 100% of the real range (the movement-prone zone) stays SILENT**. RED (the pre95
snapshot = the shipped harness-94 build) **2823 checks / 56 designed failures** — the 7 moved pins
(×2 files = 14… plus the wording tokens, 20 in all), the 0s tokens (22) and the 14 boundary-world legs
that sit inside the NEW bound. The re-based earlier boundary worlds (GD R7 26→39 m, BS P4 26→71 m,
BS/EDR drift 60→80 m) pass on BOTH builds by design; the h94 red branch was re-based to the N/A form.
**Installed pack md5 `f1b7363e411bfc340423d4ecdc1ea91c`** (all 5 ship files byte-identical to source,
dist == installed; the live mod sha256 `ea48ca6dc6bf8e3657a179dfd869e7c876b4d2cf3dfb096f1821d957ba09b704`). RPFM server reused on
45127 and stopped afterwards.

---

**Update 2026-10-10 (THE ACCUSATION MOVE-ORDER ROOT CAUSE FIXED — harness 96): the offer test no longer trusts the engine's `unit_in_range`; it uses the 70% constant (52 m) ONLY.** The harness-95 build fixed the *magnitude* of the range (75 → 52 m) but its offer test was still **`unit_in_range(enemy)` FIRST**, with `unit_distance <= 52` only as a fallback. The passive observer probe (`zz_probe_dist`, its own pack) measured the crossing live and nailed the bug at **tick 59**:

```
CAND-FIRST tick=59 idx=1 type=orc_boyz dist=81.3m first_passing_test=engine mode=first engine_unit_in_range=t our_52_test=f our_75_test=f
```

The engine's own reach read answered **TRUE at 81.3 m** while **BOTH** of the mod's bounds said FALSE — because `unit_in_range` reports the ability's *intercept/pursuit* reach, not a cast range. The mod therefore offered (and cast at) a target 81.3 m away; the engine accepted the cast and **WALKED the caster in** — exactly the move order the user reported. The old log made this invisible: it printed a **static** `"within 52m"` label instead of the real distance.

**The fix (harness 96; the unshipped "contact range" attempt — `releases/20261010_contact_range_harness96/` — was reverted; the shipped h95 source is the base):**

- **THE OFFER TEST IS THE CONSTANT ONLY:** `FOURTH.eg_enemy_within_bound(unit, enemy)` = `unit:unit_distance(enemy) <= FOURTH.ACCUSATION_RANGE_M` (52 m). The engine's **`unit_in_range(enemy)` call is REMOVED from the offer path entirely** — it is the bug. Everything else is untouched: in-melee preferred then closest, the in-melee OR under-missile-fire condition, the `bench_fresh` fresh-handle cast, the pre-cast re-check, the hold, cast target always the enemy.
- **THE LOG NOW PRINTS THE REAL DISTANCE** (to one decimal) at both the **target choice** and the **pre-cast re-check** (and in the lapse-skip line), with the bound beside it: `accusation target: '<type>' is the chosen enemy (missile) distance=48.7m bound=52m`.
- **THE PRIMITIVE** is `unit:unit_distance(other)` — **edge-to-edge (bounding-box aware)** per `battle_unit.lua:160` — so the number in the log IS exactly the number the test used (stated in a code comment beside the reader).
- **AUDIT (every `unit_in_range` site):** grep found exactly **ONE** site — `FOURTH.eg_enemy_in_range`'s `unit:unit_in_range(enemy)` read, used as the Accusation offer/range test. **Removed** (the function is replaced by `FOURTH.eg_enemy_within_bound`). **No other evaluator** (charge, tired, melee, melee_low_morale, in-melee-self, barrier, charge_or_melee, ushoran_health, glorious_death, verminking, melee_health75, metallurgy, the blocks-7-9 triggers, blood_sacrifice, eat_da_runts) uses the engine helper — they all already compare `unit_distance` against their own 70% constant. `grep 'unit_in_range(' <source>` is now **empty**.

**Harness 96:** GREEN **2902 checks / 0 failures** (live + annotated), including a new **section 0t** (the fix tokens: the constant-only helper present, the gate wired, `unit_in_range(` and the old helper GONE, the real-distance log fragments, the `battle_unit.lua:160` citation) and **10 move-order worlds** (5 × 2 files): **R1** the exact probe case (`in_range` TRUE, 81.3 m > 52 m bound) → **stays SILENT**; **R2** inside (48.7 m) → FIRES; **R3** outside (70 m) → SILENT; **R4** the live log carries `distance=48.7m bound=52m` at both the choice and the re-check; **R5** the engine flag FALSE but 40 m (inside) → the CONSTANT rules, FIRES. RED (the pre96 snapshot = the shipped **harness-95** build, whose offer test trusts `unit_in_range`) **2869 checks / 20 designed failures**: the 0t tokens (both files), **R1 firing** (both files — the regression), R4's live log, and R5 (both files); R2/R3 + R4's annotated leg pass by design (5/10). The harness-95 suite re-runs **GREEN 2856 / 0** against the new source (no regression). **Installed pack md5 `71ff20a3e71ca70fa4ac8d6d56672fb3`** (all 5 ship files byte-identical to source, dist == installed; the live mod sha256 `ffc6ed30a33d503ce07fa283c124e6b3791ed6e4b7c28dd285642a4e345564d9`, 418692 bytes). RPFM server started on 45127 and stopped afterwards. **The observer probe pack `zz_probe_dist.pack` was LEFT INSTALLED** (it is a passive observer — zero casts, zero writes — so it cannot interfere; the user will re-test with it). The step probe is absent from `data/`.

---

**Update 2026-10-14 (CLASS B — the ALLY-TARGETED cast-target round, harness 98).**

**The ally range constants (each = `floor(real × 0.70)`, `FOURTH.RANGE_FRACTION`).** The real range is the ability's own `target_intercept_range` (`unit_spec_abil.tsv`) — none of these single-ally casts has an aura (`effect_range` is `0.0000` for all of them).

| Constant | Real range (`target_intercept_range`) | 70% bound | Abilities that ride it |
|---|---:|---:|---|
| `FOURTH.ALLY_CAST_R50` | 50.0000 m | **35** | Captain of the Phoenix Guard, Helping Hand, Elvish Healing Herbs |
| `FOURTH.ALLY_CAST_R60` | 60.0000 m | **42** | Stay Here, I'll Get Help! |
| `FOURTH.ALLY_CAST_R75` | 75.0000 m | **52** | Hellish Vigour |
| `FOURTH.ALLY_CAST_R100` | 100.0000 m | **70** | Favour of the Fay, Inspired Assault I/II/III, Inspired Defence I/II/III, Shock Collar, Where You Goin!?, Patch Up, Revivification Crystal |
| `FOURTH.ALLY_CAST_R150` | 150.0000 m | **105** | Da Boss 'as a Plan!, Orcs are da Best! |

**SUPERSEDES, for this one entry only:** **Stay Here, I'll Get Help!** previously shared `FOURTH.WAVERING_RANGE_M = 24` with Fury of Ulric / Commanding Presence (a bound derived from their **`effect_range` 35 m** aura — the round-95 table above). Because this ability's own real range is its **`target_intercept_range` 60 m**, the Class-B round gives it its **own** bound **42 m** (`FOURTH.ALLY_CAST_R60`), read through `FOURTH.ab_range_m`, and its cast target is now **the picked wavering ally** (not the owner). `FOURTH.WAVERING_RANGE_M = 24` is **unchanged** and still governs Fury of Ulric / Commanding Presence (the `wavering_self_or_ally` trigger).

**The mechanism.** The cast-target discipline is the mod's existing ally-picker shape (`blood_sacrifice` / `eat_da_runts`) extended with the Class-A round's **fresh-handle** rule: the caster's controller **and** the chosen ally's script_unit are re-enumerated from `get_scriptunits_for_local_players_army()` on the **same tick** (`FOURTH.ab_fresh_friend_su`), and the cast is `caster_su.uc:perform_special_ability(key, ally_su.unit)`. A controller held from an earlier poll silently no-ops. The offer test is `unit:unit_distance(ally)` **edge-to-edge, bounding-box aware** (`battle_unit.lua:160`) **≤ the entry's own 70% constant ONLY** — `unit_in_range(` remains absent from the whole file. A pre-cast re-check re-reads the ally's liveness, its real distance and (for a heal) its health, and SKIPs the cast on lapse; the existing per-pair guard + cooldown hold keep it from re-firing every poll.

**Harness 98:** GREEN **3186 checks / 0 failures** (live + annotated) — a new **section 0v** (the 5 constants + values, the `FOURTH.ALLY_CAST` map, the 18 `ally_range_real` fields, the load-loop wiring, the fresh-friend helper, the shared picker, the four family evaluators, the fresh-handle cast branch, the poll slots, the moved trigger counts, and `unit_in_range(` still GONE) plus **32 ally worlds** (16 × 2 files): ally-in-range → cast ON THE ALLY; no ally → SILENT; ally BEYOND the bound → SILENT though the engine helper says in-range; the heal fires on the health trigger AND picks the LOWEST-health ally; the melee+health family needs the owner in melee; the wavering family; two lapse worlds (drift; the ally gone) → SKIP; the fresh-handle proof; and Stay Here casting on the picked ally. RED (pre98 snapshot = the shipped harness-97 build, which has no ally triggers at all) **3153 checks / 85 designed failures, 13/32 world results** (only the SILENT worlds whose snapshot trigger stays quiet). Re-based pins (documented): the trigger counts (`melee_unwavering` 383→373 ×7, `charge_or_melee` 29→26 ×5, `ushoran_health` 41→38 ×2, `melee_health75` 2→1), and the harness-90 worlds **N8b/N8c** (Stay Here now targets the ally and says so). **Installed pack md5 `6927e4a6a36885274846616bdb53728e`** (all 5 ship files byte-identical to source, dist == installed; live mod sha256 `16919a72504f24f57fcb41d5227ec3007dfe69f1713ee162ea412e702a935697`, 444560 bytes). RPFM server started on 45127 and stopped afterwards. **The observer probe pack `zz_probe_dist.pack` was LEFT INSTALLED and untouched** (md5 `d4e67cfb8bc562c7d6f0ff742909c13d`, 20063 bytes).


---

### 10.2 The single in-wheel rule - the two implemented army abilities REMOVED (2026-10-17)

**The user's instruction (verbatim):** "remove from the mod the two abilities that are implemented but OUTSIDE the new single exclusion rule (both are army abilities, which the rule excludes)."

**The rule being enforced** (one rule, replacing every earlier exclusion rule): *"Do not implement any ability that is not in the ability wheel (this should cover spells and army abilities implicitly). All the rest, I think, we can tackle."* (`docs/WH3_recount_wheel_only.md` §1.)

**Decision.** Meat Feast (`wh3_main_prisoners_butcher`) and Massacre (`wh3_main_prisoners_massacre`) were the only two implemented keys outside the wheel (both `source_type = army`). Both are **REMOVED from the mod's `ABILITIES` table**. Their status is now `excluded (not in wheel: army ability - removed from mod per user decision 2026-10-17)`.

**What was removed - exactly two entries:**
- `marker = "butcher"` - **Meat Feast** (trigger `ushoran_health`, badge `zz_auto_badge_butcher`, key `wh3_main_prisoners_butcher`)
- `marker = "massacre"` - **Massacre** (trigger `melee_unwavering`, badge `zz_auto_badge_massacre`, key `wh3_main_prisoners_massacre`)

**What was NOT removed (and why):** no evaluator, trigger, helper, constant or state was deleted. `ushoran_health` keeps its other member (**Gulyas**) and stays at 33 entries; `melee_unwavering` remains the shared in-melee trigger at 362. In particular **Grut's Sickle is a DIFFERENT ability** (`wh3_main_item_abilities_gruts_sickle`, an in-wheel item ability) and is **untouched**, including its max-HP `winds` ally pick rule (`FOURTH.evaluate_ally_winds`, `family == "winds"`, `HealthValue`). The annotated copy carries the same removal.

**Counts (exact, before -> after):** ABILITIES **579 -> 577 entries**; **605 -> 603 keys**; `ushoran_health` **34 -> 33**; `melee_unwavering` **363 -> 362**. Every other trigger count and every other entry is unchanged.

**Spreadsheet:** `docs/WH3_abilities_master_v2_2026-10-17.xlsx` (and the `.ods` twin) - **v2 supersedes v1; v1 is left unchanged**. Both rows carry Implementation `REMOVED (outside rule)` (a new value added to the Definitions status vocabulary) and the Changelog has a v2 row.

**Harness 100:** GREEN **3388 checks / 0 failures** (live + annotated). New section 0x proves both keys, markers and badge ids are gone, the counts are exactly 577 / 603, the neighbours survive, `ushoran_health` keeps Gulyas and Grut's Sickle is untouched. RED (pre100 snapshot) **3355 checks / 74 designed failures**: 66 re-based count pins (579 -> 577, 605 -> 603, 363 -> 362, 34 -> 33) and 8 inherited red-control branches from earlier rounds whose snapshots are newer than this round's pre-edit snapshot; the harness-100 red control itself passes (the snapshot still carries both keys and 579 / 605).

**Build/install:** pack rebuilt and installed; all **5 ship files byte-identical** to source; installed pack md5 **`f7c5e525ded0d1a07242b22d9053d66d`** (live mod sha256 `c8573d52a54195aaa3b13a3dbdcc290aa2ed23d7c79bfb76fb957aa835b872ab`, 546,408 bytes). The passive observer probe `zz_probe_dist.pack` was **left installed and untouched** (md5 `d4e67cfb8bc562c7d6f0ff742909c13d`, 20,063 bytes).

### 10.3 The boss-only exclusion + Gate of Khorne (2026-10-17)

**The user's instruction (verbatim):** "exclude the active abilities that are granted to boss units. Mark in the
excel the reason for exclusion." and, for the second build: "The trigger will place it on the closest enemy that
is in range of the ability and fighting."

**A. What "boss-only" means, and how the list was verified.** A key is boss-only when **every** grant path found
in the extracted junction tables terminates on a `_boss` unit: `land_abil.tsv`
(land_units_to_unit_abilites), `uset_ability.tsv` (unit_set -> ability), `sag_to_abilities.tsv` +
`sag_to_units.tsv` (special-ability group -> ability -> unit) and `army_ab_faction.tsv`. `ui_coll_junc.tsv` is
display-only and grants nothing; skill-tree and rite junctions are **not part of this extraction**, so the
negative is closed only for the tables above (the same documented limit as `WH3_summon_analysis.md` §5.3).
**15 in-wheel keys qualify.** A naive `_boss` name test finds 18 - the extra three (`Empowering Shrooms`,
`They Needs Stabbin'`, `Squig Thinkin'`) are granted to `*_big_boss*` units, which are **ordinary recruitable Big
Boss heroes**, not quest variants (on-screen name is the generic rank name; `multiplayer_qb_cap = 2` in
`db_main_units.tsv`; they reuse an existing warboss attribute group instead of a bespoke one). Those three stay.

| Ability | Key | Only granting unit |
|---|---|---|
| Greater Faith Bastion | `wh_dlc06_quest_abilities_grand_faiths_bastion` | `wh_dlc06_emp_cha_arch_lector_0_boss` |
| Bitter Sting | `wh3_dlc27_qb_unit_abilities_bitter_sting` | `wh3_dlc27_chs_feral_manticore_boss` |
| Frenzied Challenge | `wh3_dlc27_qb_unit_abilities_frenzied_challenge` | `wh3_dlc27_bst_mon_ghorgon_boss` |
| Visions of Madness | `wh3_dlc27_qb_unit_abilities_visions_of_madness` | `wh3_dlc27_bst_mon_jabberslythe_boss` |
| Guttural Roar | `wh3_dlc27_qb_unit_abilities_guttural_roar` | `wh3_dlc27_cth_mon_celestial_lion_boss` |
| Breath of the Hydra | `wh2_dlc10_quest_abilities_fiery_head` | `wh2_dlc10_def_mon_war_hydra_boss` |
| Eye of Rejuvenation | `wh2_dlc10_quest_abilities_regenerating_head` | `wh2_dlc10_def_mon_war_hydra_boss` |
| Howling Winter | `wh_dlc08_quest_abilities_howling_winter` | `wh_dlc08_nor_mon_frost_wyrm_boss` |
| Master of Souls | `wh_dlc08_quest_abilities_master_of_souls` | `wh_dlc08_vmp_mon_terrorgheist_boss` |
| Servants of Nagash | `wh_dlc04_quest_abilities_servant_of_nagash` | `wh_dlc04_vmp_cha_strigoi_ghoul_king_0_boss` |
| Dissolving Bone | `wh3_dlc27_qb_unit_abilities_dissolving_bone` | `wh3_dlc27_tmb_mon_carrion_boss` |
| Terrible Malice | `wh3_dlc27_qb_unit_abilities_terrible_malice` | `wh3_dlc27_sla_mon_preyton_boss` |
| Copious Phlegm | `wh3_dlc27_qb_unit_abilities_copious_phlegm` | `wh3_dlc27_nur_mon_toad_dragon_boss` |
| Fiery Convocation | `wh2_dlc10_quest_abilities_magic_fiery_convocation` | `wh2_dlc10_nor_mon_phoenix_flamespyre_boss` |
| Flame Storm | `wh2_dlc10_quest_abilities_flame_storm` | `wh2_dlc10_nor_mon_phoenix_flamespyre_boss` |

**The five that were IMPLEMENTED and are now REMOVED** (entry, marker, badge and key all gone from the live
script and the annotated copy):

| marker | name | trigger before | badge | key |
|---|---|---|---|---|
| `grand_faiths_bastion` | Greater Faith Bastion | `melee_unwavering` | `zz_auto_badge_grand_faiths_bastion` | `wh_dlc06_quest_abilities_grand_faiths_bastion` |
| `bitter_sting` | Bitter Sting | `enemy_engaged_or_shot` | `zz_auto_badge_bitter_sting` | `wh3_dlc27_qb_unit_abilities_bitter_sting` |
| `frenzied_challenge` | Frenzied Challenge | `enemy_engaged_or_shot` | `zz_auto_badge_frenzied_challenge` | `wh3_dlc27_qb_unit_abilities_frenzied_challenge` |
| `visions_of_madness` | Visions of Madness | `enemy_engaged_or_shot` | `zz_auto_badge_visions_of_madness` | `wh3_dlc27_qb_unit_abilities_visions_of_madness` |
| `guttural_roar` | Guttural Roar | `melee_unwavering` | `zz_auto_badge_guttural_roar` | `wh3_dlc27_qb_unit_abilities_guttural_roar` |

**What was NOT touched:** no evaluator, trigger, helper, constant or state was removed. `melee_unwavering` loses
its two boss members only (362 -> 360) and stays the shared in-melee trigger; `enemy_engaged_or_shot` loses three
(89 -> 86); `enemy_ground_area` stays 9; `ushoran_health` stays 33; every other entry is unchanged.

**B. Gate of Khorne.** Key `wh3_main_character_abilities_gate_of_khorne` (there is NO `dlc26` variant - confirmed
against `unit_spec_abil.tsv` / `unit_abilities.tsv`). Data: 1 use, 120 s recharge / 60 s initial, 10 s active,
5 s wind-up, `target_intercept_range` 50 m, `target_ground` + `target_friends` (not `target_self`), restriction
`climbing_manning_eq_on_platform`, `ai_usage = hex_melee`, summons `wh3_main_kho_inf_bloodletters_summoned_0`
(100 Bloodletters). New trigger `enemy_ground_melee`, evaluated per poll:
1. enumerate the enemy army; keep enemies alive, valid, **in melee** and within **35 m** (70% of 50 m, the
   standing rule; `unit:unit_distance` ONLY - never `unit_in_range`);
2. pick the **CLOSEST** of them (the melee-only arm means the shared picker's melee preference collapses to a
   pure distance comparison);
3. re-fetch the caster controller and the chosen enemy the SAME tick; re-read the enemy (alive, still in melee,
   still within 35 m) immediately before the cast and SKIP if it lapsed, logging the real distance;
4. cast `perform_special_ability_ground(key, enemy:position(), 0, 0)` - the position is the ENEMY'S, never the
   caster's;
5. its own reason string: `closest fighting (in-melee) enemy within bound (targeting <type>, distance=<x>m)`.

**Counts (exact, before -> after):** ABILITIES **577 -> 573 entries** (-5 +1); **603 -> 599 keys** (-5 +1);
`melee_unwavering` **362 -> 360**; `enemy_engaged_or_shot` **89 -> 86**; `enemy_ground_melee` **1**;
`range_real` fields **98 -> 96**; `ushoran_health` 33 and `enemy_ground_area` 9 unchanged.

**Harness 101:** GREEN **3442 checks / 0 failures** (live + annotated). RED (pre101 snapshot) **3396 checks /
78 designed failures**: 65 re-based count pins (573/599, 360, 86, 96, 1146, wording 573) + 3 tooltip-coverage
pins + 8 inherited red-control branches from earlier rounds + 2 aggregate world tallies; harness 101's own 0aa
section and all seven Gate worlds pass on both sides by design (the snapshot has no Gate of Khorne, so every
gate world fires nothing).

**Build/install:** all **5 ship files byte-identical** to source (script 548,092 bytes); installed pack md5
**`deaf707dcda5087d689116860f7b0f27`**, dist == installed. `zz_probe_dist.pack` left installed and untouched
(md5 `d4e67cfb8bc562c7d6f0ff742909c13d`).

**Spreadsheet:** `docs/WH3_abilities_master_v3_2026-10-17.xlsx` (+ `.ods`) - **v3 supersedes v2; v1 and v2 are
unchanged**. The five rows carry Status `EXCLUDED` and reason `boss-only unit (granted only to _boss units)`;
the five removed implementations read `REMOVED (boss-only)`; Gate of Khorne reads `IMPLEMENTED` on
`enemy_ground_melee`; the Changelog has a v3 row.

### 10.4 The summon round - the ground-castable summons, the four new summon triggers, the illusions excluded (2026-10-17)

**A. THE REST OF THE SUMMON CLASS (derived, not hand-listed).** The list was derived programmatically from the
game's own tables (`unit_spec_abil.tsv` + `unit_abilities.tsv` in `%LOCALAPPDATA%\Temp\wh3\`, script
`tools/derive_summon_plan.py`): `spawned_unit` set AND `type = wh_type_summon_unit` AND `spawn_is_decoy` false/absent
AND `target_ground = true` AND in-wheel (`source_type` unit-side, `icon_name` set, `is_hidden_in_ui = false`, not the
army/quest family) AND not boss-only AND not already implemented. Result: **57 entries / 68 keys** (the two
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
finisher never fires at it (**FAIL CLOSED**, one log line for the whole battle). FIELD NOTE: the health read is the
same `common.get_context_value("CcoBattleUnit", <ui id>, "HealthPercent")` call the Class-B ally pick proved live, here keyed by the ENEMY's ui id (enemy ui ids are proven readable - the enemy-target probes used them); an enemy
health read that does not answer a number FAILS CLOSED (that enemy is never offered), so a field surprise costs a
silent finisher, never a wrong one. First battle confirms it from the `health=NN%` lines.

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
