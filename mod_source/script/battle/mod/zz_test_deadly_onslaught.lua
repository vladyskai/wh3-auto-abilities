--------------------------------------------------------------------------------
-- Route 2 test case: automatically fire ONE ability, under a chosen condition.
--
-- Target ability : Deadly Onslaught
--                  database key = wh_main_character_abilities_deadly_onslaught
--                  (self-buff, 31 s duration, 90 s cooldown, unlimited uses,
--                   no magic cost, no usage restrictions of any kind,
--                   engine's own AI tag = augment_charge_self)
--
-- WHICH UNIT HAS IT
--   In skirmish/custom battles an ability comes from the unit's innate list
--   (db table: land_units_to_unit_abilites_junctions), not from a skill.
--   The Empire Captain does NOT have Deadly Onslaught there - which is why it
--   never showed up in skirmish. Boris Todbringer DOES, on all four of his
--   unit variants:
--       wh3_dlc29_emp_cha_boris_todbringer_toddy_0 ... _3
--   So this test works with Boris in skirmish, and needs no change of key.
--
-- WHAT THIS RUN IS FOR - it answers four questions in one battle:
--     1. Does a script in script/battle/mod/ run in this battle type?
--     2. Can we detect, per unit, whether it owns a given ability?
--     3. Can we make it fire that ability with no click from the player?
--     4. What happens to our control of that unit while it fires?
--
-- WHERE THIS FILE GOES
--   script/battle/mod/zz_test_deadly_onslaught.lua  inside the .pack file.
--   That folder is auto-loaded by the game's own mod loader
--   (script/_lib/lib_mod_loader.lua) in every battle. No vanilla file is edited.
--
-- WHERE THE OUTPUT GOES
--   zz_test_deadly_onslaught_log.txt, in the game's install folder (next to
--   Warhammer3.exe). Written directly by this script, so it does not depend on
--   any logging setting. Search it for "zz_test_deadly_onslaught".
--------------------------------------------------------------------------------


-- ============================================================================
-- 1. SETTINGS - the only things you normally touch
-- ============================================================================

-- ============================================================================
-- 1a. THE CLAIM-TEST BISECT - the crash hunt, one engine operation per battle
-- ============================================================================
-- The claim test runs a fixed sequence of operations on the engine's own
-- ability-key value. The sequence is a LADDER: every step can be enabled on
-- its own, and a step that runs announces itself - `bisect: step <n> <name>
-- entering` immediately before its operation, `bisect: step <n> <name> ok`
-- immediately after it. THE STEP THAT KILLS THE GAME IS THE ONE WHOSE
-- `entering` LINE IS THE LOG'S LAST LINE, WITH NO `ok` AFTER IT.
--
-- WHAT THE LADDER FOUND: steps 1-6 all passed in battle (type, tostring,
-- concat copy, string.len, #, string.lower), and the log's last line was
-- `bisect: step 7 string.find plain entering` with no `ok` after it - the
-- FOUR-ARGUMENT PLAIN-MODE find is what killed the engine.
--
-- SO THE FIND IS GONE. Both find forms (plain and pattern) have been removed
-- from every claim/match path, and the match is now EXACT KEY EQUALITY: the
-- lowered copy of the key is compared against the ability's listed keys
-- (ABILITIES, section 1 - already lowercase). Steps 7-8 stay in the ladder
-- as REMOVED slots: they log `SKIPPED (equality match - find removed)` and
-- run nothing, so the record stays honest. Step 9 is the equality compare
-- and remains the verdict gate.
--
-- The nine steps, in the order they run:
--   1 type(v)                    - the value's Lua type
--   2 tostring(v)                - pcall'd text read (the copy's fallback)
--   3 v .. "" (concat copy)      - the fresh plain copy the claim works on
--   4 string.len on the copy     - the length read, pcall'd
--   5 # on the copy              - the language-level length fallback
--   6 string.lower on the copy   - the lowercased copy, pcall'd
--   7 string.find plain          - REMOVED (the killer the bisect named)
--   8 string.find pattern-form   - REMOVED (no find remains at all)
--   9 the equality compare       - lowered copy == each listed key (the gate)
--
-- HOW TO RAISE IT - ONE STEP PER BATTLE:
--   * This build ships CLAIM_BISECT = 9: the whole ladder on - steps 1-6 and
--     9 run, steps 7-8 log their removal. Expect the claim lines and the
--     deferred badges in the next battle log.
--   * Lower levels still gate: with step 9 off the verdict falls back to
--     'not ours' (no claim), so the switch keeps working.
--   * A disabled step logs `bisect: step <n> <name> SKIPPED (disabled)` and
--     its result does not contribute; steps 7-8 always log their removal.
--   * 0 = the whole claim test off; 9 = everything that still exists on.
local CLAIM_BISECT = 9

-- THE ABILITIES - one entry per ability, and this table drives everything:
-- the HUD scan (which dial buttons are ours), the firing loop (which trigger
-- and which keys to try) and the badges (one per ability, id and offset).
--   marker  - the ability's short name, for the log lines and the internal
--             lookups (NO LONGER a substring search: the engine's key is
--             matched by EXACT EQUALITY against the keys listed below)
--   name    - the ability's display name, for the badge log lines
--   trigger - "charge" : the existing charge conditions (section 5), verbatim
--             PLUS (this round, user-approved) the plain in-melee condition -
--             Deadly Onslaught has a component that is useful in melee, so
--             it fires on the charge window OR once the unit is already
--             fighting. The two arms exclude each other (a charging unit
--             has not made contact yet); both switches below are ON.
--             "tired" : fire when the unit's FATIGUE state is Tired or
--             worse - tired / very_tired / exhausted; winded and above hold
--             it back. Read through battle_unit:fatigue_state() (section
--             7f); an unreadable read FAILS CLOSED and says so once.
--             "melee"  : fire whenever the engine says the unit is in melee
--             "melee_low_morale": fire when the engine says the unit is in
--                        melee AND its morale is at or below the wavering
--                        threshold (battle_unit:is_wavering - the only morale
--                        THRESHOLD the API exposes; there is NO percentage
--                        read). FAIL-OPEN: a morale read that cannot be taken
--                        falls back to the plain melee trigger, so an
--                        unreadable morale can never silently disable it.
--             "melee_unwavering": fire when the engine says the unit is in
--                        melee AND the unit is neither routing nor wavering
--                        (the same battle_unit:is_wavering threshold, now as
--                        a guard). FAIL-OPEN like the routing guard: only a
--                        READABLE wavering (exact true) holds it back, and an
--                        unreadable morale rides the plain in-melee condition.
--                        THE 28 APPROVED IN-MELEE-SELF ENTRIES (the
--                        questionnaire block-1 batch, this round) share
--                        this trigger name - their approved rule is
--                        EXACTLY blood_lust's - so they share its
--                        evaluator as well (section 7g). The trigger
--                        string is now ONLY the wiring key for that
--                        evaluator: the poll calls
--                        ability.evaluate(unit, routing) and never
--                        compares this string again (item 8).
--   evaluate- the per-entry dispatch (critique-2 item 8): the poll calls
--             ability.evaluate(unit, routing) directly. Section 7g wires
--             this field at load from the trigger name above, so the
--             dispatch is one call and no string comparison runs.
--   keys    - the database keys (lowercase) this ability answers to. A dial
--             button is CLAIMED when its key, lowercased, EQUALS one of
--             these, and the unit scan uses them as its search set (which
--             of them a unit actually carries - section 2). At fire time
--             the readiness check (can_perform_special_ability) asks about
--             the ONE key the scan found on the unit; this list is walked
--             only as the fallback when no usable key is cached yet. Add
--             new engine variants here: the scan probe prints every
--             key-bearing button we did not claim (ours=no), so an unknown
--             variant shows up in the log immediately.
--   badge   - the component id of the ability's own M/A badge (its click is
--             the only control)
--   ox, oy  - the badge's FALLBACK offset from the onslaught badge's own
--             BADGE_X / BADGE_Y (section 8b), used only when the claimed
--             button's bar position could not be determined at claim time:
--             onslaught BADGE_X+0/BADGE_Y+0, foe_seeker BADGE_X+70/BADGE_Y+30
--             (the measured +70,+30 from the top wheel slot to the 45-degree
--             slot), hammer_of_sigmar BADGE_X+98/BADGE_Y+102 (the measured
--             top-slot-to-right-slot step), stand_your_ground
--             BADGE_X+66/BADGE_Y+172 (the measured top-slot-to--45-degree
--             step = wheel slot 4), blood_lust BADGE_X-68/BADGE_Y+32 (the
--             measured top-slot-to-135-degree step = wheel slot 5). When the
--             bar position IS known,
--             the badge's offset is
--             that wheel slot's delta from the measured top slot (WHEEL_SLOT /
--             WHEEL_TOP_X/WHEEL_TOP_Y, section 8b) applied to BADGE_X/BADGE_Y,
--             so re-tuning the Deadly Onslaught badge (zz_badge_set) still
--             carries Foe-Seeker along.
local ABILITIES = {
	{ marker = "onslaught", name = "Deadly Onslaught", trigger = "charge",
		badge = "zz_auto_badge",
		keys = { "wh_main_character_abilities_deadly_onslaught" },
		ox = 0, oy = 0 },
	{ marker = "foe_seeker", name = "Foe-Seeker", trigger = "tired",
		badge = "zz_auto_badge_fs",
		keys = { "wh_main_character_abilities_foe_seeker",
			"wh_dlc03_character_abilities_foe_seeker",
			-- BLOCK 2 (this round): the SUMMONED Foe-Seeker - Krell's
			-- summoned form carries this third key. It is NOT a new
			-- entry: its key sits HERE, so the summoned caster shares
			-- this ability's marker, badge, arming state and back-off
			-- with every other Foe-Seeker owner.
			"wh_main_character_abilities_foe_seeker_summoned" },
		ox = 70, oy = 30 },
	{ marker = "hammer_of_sigmar", name = "Hammer of Sigmar", trigger = "melee",
		badge = "zz_auto_badge_hos",
		keys = { "wh_main_spell_bound_hammer_of_sigmar",
			"wh_dlc04_spell_bound_hammer_of_sigmar_upgraded" },
		ox = 98, oy = 102 },
	{ marker = "stand_your_ground", name = "Stand Your Ground", trigger = "melee_low_morale",
		badge = "zz_auto_badge_syg",
		keys = { "wh_main_character_abilities_stand_your_ground",
			"wh3_dlc24_character_abilities_tacticians_stand_your_ground" },
		ox = 66, oy = 172 },
	{ marker = "blood_lust", name = "Blood Lust", trigger = "melee_unwavering",
		badge = "zz_auto_badge_bl",
		keys = { "wh_main_character_abilities_blood_lust",
			"wh_dlc03_character_abilities_blood_lust" },
		ox = -68, oy = 32 },
	-- THE APPROVED IN-MELEE-SELF BATCH (the questionnaire's block 1,
	-- this round): 28 approved entries - 29 database keys; the two
	-- Deathbringer keys sit in ONE entry (base + upgraded). Their
	-- approved rule is EXACTLY blood_lust's - "when in melee (and not
	-- fleeing): cast on self" = the unit is alive, in melee, and
	-- neither routing nor wavering (fail-open morale), self-cast - so
	-- they share its trigger name and its evaluator (section 7g).
	-- Each entry carries its own marker, display name, badge id and
	-- key list. No separate fallback offset was measured for these
	-- badges: the wheel-slot path positions them (section 8b), and
	-- ox/oy stay at the top slot (0, 0) for the logged fallback case.
	{ marker = "aether_sword", name = "Aether Sword", trigger = "melee_unwavering",
		badge = "zz_auto_badge_aether_sword",
		keys = { "wh3_dlc20_weapon_abilities_aether_sword" },
		ox = 0, oy = 0 },
	{ marker = "apocalyptic_vision", name = "Apocalyptic Vision", trigger = "melee_unwavering",
		badge = "zz_auto_badge_apocalyptic_vision",
		keys = { "wh_dlc03_character_abilities_apocalyptic_vision" },
		ox = 0, oy = 0 },
	{ marker = "armour_of_gazrakh", name = "Armour of Gazrakh", trigger = "melee_unwavering",
		badge = "zz_auto_badge_armour_of_gazrakh",
		keys = { "wh3_dlc23_item_abilities_armour_of_gazrakh" },
		ox = 0, oy = 0 },
	{ marker = "aura_of_quetzl", name = "Aura of Quetzl", trigger = "melee_unwavering",
		badge = "zz_auto_badge_aura_of_quetzl",
		keys = { "wh2_main_item_abilities_aura_of_quetzl" },
		ox = 0, oy = 0 },
	{ marker = "axe_of_dargo", name = "Axe of Dargo", trigger = "melee_unwavering",
		badge = "zz_auto_badge_axe_of_dargo",
		keys = { "wh_main_weapon_abilities_axe_of_dargo" },
		ox = 0, oy = 0 },
	{ marker = "axe_of_grom", name = "Axe of Grom", trigger = "melee_unwavering",
		badge = "zz_auto_badge_axe_of_grom",
		keys = { "wh2_dlc15_weapon_abilities_axe_of_grom" },
		ox = 0, oy = 0 },
	{ marker = "axes_of_kadrin", name = "Axes of Kadrin", trigger = "melee_unwavering",
		badge = "zz_auto_badge_axes_of_kadrin",
		keys = { "wh3_dlc25_weapon_abilities_axes_of_kadrin" },
		ox = 0, oy = 0 },
	{ marker = "azhags_ard_armour", name = "Azhag's 'Ard Armour", trigger = "melee_unwavering",
		badge = "zz_auto_badge_azhags_ard_armour",
		keys = { "wh2_dlc15_item_abilities_azhags_ard_armour" },
		ox = 0, oy = 0 },
	{ marker = "ballet_of_blows", name = "Ballet of Blows", trigger = "melee_unwavering",
		badge = "zz_auto_badge_ballet_of_blows",
		keys = { "wh3_main_lord_abilities_ballet_of_blows" },
		ox = 0, oy = 0 },
	{ marker = "bear_fang_talisman", name = "Bear Fang Talisman", trigger = "melee_unwavering",
		badge = "zz_auto_badge_bear_fang_talisman",
		keys = { "wh3_dlc27_item_abilities_bear_fang_talisman" },
		ox = 0, oy = 0 },
	{ marker = "beastslaver", name = "Beastslaver", trigger = "melee_unwavering",
		badge = "zz_auto_badge_beastslaver",
		keys = { "wh2_dlc14_lord_abilities_beastslaver" },
		ox = 0, oy = 0 },
	{ marker = "blade_of_bel_korhadris", name = "Blade of Bel-Korhadris", trigger = "melee_unwavering",
		badge = "zz_auto_badge_blade_of_bel_korhadris",
		keys = { "wh2_main_item_abilities_blade_of_bel_korhadris" },
		ox = 0, oy = 0 },
	{ marker = "blades_of_shang_yang", name = "Blades of Shang-Yang", trigger = "melee_unwavering",
		badge = "zz_auto_badge_blades_of_shang_yang",
		keys = { "wh3_cp1_weapon_abilities_blades_of_shang_yang" },
		ox = 0, oy = 0 },
	{ marker = "bloodstorm_blades", name = "Bloodstorm Blades", trigger = "melee_unwavering",
		badge = "zz_auto_badge_bloodstorm_blades",
		keys = { "wh3_dlc26_weapon_abilities_bloodstorm_blades" },
		ox = 0, oy = 0 },
	{ marker = "brass_body", name = "Brass Body", trigger = "melee_unwavering",
		badge = "zz_auto_badge_brass_body",
		keys = { "wh2_dlc17_lord_abilities_brass_body" },
		ox = 0, oy = 0 },
	{ marker = "change_or_die", name = "Change or Die!", trigger = "melee_unwavering",
		badge = "zz_auto_badge_change_or_die",
		keys = { "wh3_dlc24_character_abilities_change_or_die" },
		ox = 0, oy = 0 },
	{ marker = "claws_of_mourkain", name = "Claws of Mourkain", trigger = "melee_unwavering",
		badge = "zz_auto_badge_claws_of_mourkain",
		keys = { "wh2_dlc11_lord_abilities_claws_of_mourkain" },
		ox = 0, oy = 0 },
	{ marker = "cloak_of_mists_and_shadows", name = "Cloak of Mists & Shadows", trigger = "melee_unwavering",
		badge = "zz_auto_badge_cloak_of_mists_and_shadows",
		keys = { "wh_main_item_abilities_cloak_of_mists_and_shadows" },
		ox = 0, oy = 0 },
	{ marker = "coat_in_blood", name = "Coat in Blood", trigger = "melee_unwavering",
		badge = "zz_auto_badge_coat_in_blood",
		keys = { "wh3_dlc29_hero_abilities_coat_in_blood" },
		ox = 0, oy = 0 },
	{ marker = "creature_killer", name = "Creature-Killer", trigger = "melee_unwavering",
		badge = "zz_auto_badge_creature_killer",
		keys = { "wh2_dlc16_weapon_abilities_creature_killer" },
		ox = 0, oy = 0 },
	{ marker = "da_great_un_iz_ere", name = "Da Great 'Un Iz 'Ere!", trigger = "melee_unwavering",
		badge = "zz_auto_badge_da_great_un_iz_ere",
		keys = { "wh2_dlc15_lord_abilities_da_great_un_iz_ere" },
		ox = 0, oy = 0 },
	{ marker = "daemonblade", name = "Daemonblade", trigger = "melee_unwavering",
		badge = "zz_auto_badge_daemonblade",
		keys = { "wh3_dlc20_weapon_abilities_daemonblade" },
		ox = 0, oy = 0 },
	{ marker = "daemonshield", name = "Daemonshield", trigger = "melee_unwavering",
		badge = "zz_auto_badge_daemonshield",
		keys = { "wh3_dlc20_item_abilities_daemonshield" },
		ox = 0, oy = 0 },
	{ marker = "dagger_of_malice", name = "Dagger of Malice", trigger = "melee_unwavering",
		badge = "zz_auto_badge_dagger_of_malice",
		keys = { "wh3_dlc23_weapon_abilities_dagger_of_malice" },
		ox = 0, oy = 0 },
	{ marker = "dark_protection", name = "Dark Protection", trigger = "melee_unwavering",
		badge = "zz_auto_badge_dark_protection",
		keys = { "wh2_dlc11_lord_abilities_dark_protection" },
		ox = 0, oy = 0 },
	{ marker = "darkwalker", name = "Darkwalker", trigger = "melee_unwavering",
		badge = "zz_auto_badge_darkwalker",
		keys = { "wh3_dlc25_lord_abilities_darkwalker" },
		ox = 0, oy = 0 },
	{ marker = "deathbringer", name = "Deathbringer", trigger = "melee_unwavering",
		badge = "zz_auto_badge_deathbringer",
		keys = { "wh3_main_lord_abilities_deathbringer",
			"wh3_main_lord_abilities_deathbringer_upgraded" },
		ox = 0, oy = 0 },
	{ marker = "strike_of_nehekhara", name = "Desertstrike", trigger = "melee_unwavering",
		badge = "zz_auto_badge_strike_of_nehekhara",
		keys = { "wh2_dlc09_character_abilities_strike_of_nehekhara" },
		ox = 0, oy = 0 },
	-- BLOCK 2 - THE SECOND IN-MELEE-SELF BATCH (this round): 27 more
	-- approved entries. Their approved rule is the SAME as the block-1
	-- batch's - "when in melee (and not fleeing): cast on self" = alive,
	-- in melee, neither routing nor wavering (fail-open morale),
	-- self-cast - so every one carries trigger "melee_unwavering" and
	-- dispatches to the ONE shared FOURTH.evaluate_in_melee_self (section
	-- 7g), exactly like blood_lust and the block-1 batch. Each carries
	-- its own marker, display name, badge id and key list; the badges
	-- are positioned by the claimed button's wheel slot (section 8b),
	-- with the top slot as the fallback offset (ox 0, oy 0).
	{ marker = "dolorous_blade", name = "Dolorous Blade", trigger = "melee_unwavering",
		badge = "zz_auto_badge_dolorous_blade",
		keys = { "wh_dlc07_hero_abilities_dolorous_blade" },
		ox = 0, oy = 0 },
	{ marker = "dragon_spear", name = "Dragon Spear", trigger = "melee_unwavering",
		badge = "zz_auto_badge_dragon_spear",
		keys = { "wh2_dlc16_weapon_abilities_dragon_spear" },
		ox = 0, oy = 0 },
	{ marker = "dreaded_duelist", name = "Dreaded Duelist", trigger = "melee_unwavering",
		badge = "zz_auto_badge_dreaded_duelist",
		keys = { "wh2_dlc11_lord_abilities_dreaded_duelist" },
		ox = 0, oy = 0 },
	{ marker = "dwarf_gouger", name = "Dwarf Gouger", trigger = "melee_unwavering",
		badge = "zz_auto_badge_dwarf_gouger",
		keys = { "wh2_main_weapon_abilities_dwarf_gouger" },
		ox = 0, oy = 0 },
	{ marker = "enrage", name = "Enrage", trigger = "melee_unwavering",
		badge = "zz_auto_badge_enrage",
		keys = { "wh_pro04_unit_abilities_enrage" },
		ox = 0, oy = 0 },
	{ marker = "entice", name = "Entice", trigger = "melee_unwavering",
		badge = "zz_auto_badge_entice",
		keys = { "wh3_dlc29_unit_abilities_entice" },
		ox = 0, oy = 0 },
	{ marker = "everyone_has_their_price", name = "Everyone Has Their Price", trigger = "melee_unwavering",
		badge = "zz_auto_badge_everyone_has_their_price",
		keys = { "wh3_main_lord_abilities_everyone_has_their_price" },
		ox = 0, oy = 0 },
	{ marker = "evisceration", name = "Evisceration", trigger = "melee_unwavering",
		badge = "zz_auto_badge_evisceration",
		keys = { "wh2_dlc16_hero_abilities_evisceration" },
		ox = 0, oy = 0 },
	{ marker = "eye_jabber", name = "Eye Jabber", trigger = "melee_unwavering",
		badge = "zz_auto_badge_eye_jabber",
		keys = { "wh3_dlc29_spell_bound_eye_jabber" },
		ox = 0, oy = 0 },
	{ marker = "eye_gouger", name = "Eye Gouger", trigger = "melee_unwavering",
		badge = "zz_auto_badge_eye_gouger",
		keys = { "wh3_dlc29_spell_bound_eye_gouger" },
		ox = 0, oy = 0 },
	{ marker = "eye_of_the_storm", name = "Eye of the Storm", trigger = "melee_unwavering",
		badge = "zz_auto_badge_eye_of_the_storm",
		keys = { "wh3_main_lord_abilities_eye_of_the_storm" },
		ox = 0, oy = 0 },
	{ marker = "faiths_bastion", name = "Faith's Bastion", trigger = "melee_unwavering",
		badge = "zz_auto_badge_faiths_bastion",
		keys = { "wh_main_hero_abilities_faiths_bastion" },
		ox = 0, oy = 0 },
	{ marker = "fangsword_of_eltharion", name = "Fangsword of Eltharion", trigger = "melee_unwavering",
		badge = "zz_auto_badge_fangsword_of_eltharion",
		keys = { "wh2_dlc15_weapon_abilities_fangsword_of_eltharion" },
		ox = 0, oy = 0 },
	{ marker = "feint_and_reposte", name = "Feint and Reposte", trigger = "melee_unwavering",
		badge = "zz_auto_badge_feint_and_reposte",
		keys = { "wh2_main_lord_abilities_feint_and_reposte" },
		ox = 0, oy = 0 },
	{ marker = "filth_mace", name = "Filth Mace", trigger = "melee_unwavering",
		badge = "zz_auto_badge_filth_mace",
		keys = { "wh_main_weapon_abilities_filth_mace" },
		ox = 0, oy = 0 },
	{ marker = "fluid_injection", name = "Fluid Injection", trigger = "melee_unwavering",
		badge = "zz_auto_badge_fluid_injection",
		keys = { "wh2_dlc16_unit_abilities_fluid_injection" },
		ox = 0, oy = 0 },
	{ marker = "gaze_of_khorne", name = "Gaze of Khorne", trigger = "melee_unwavering",
		badge = "zz_auto_badge_gaze_of_khorne",
		keys = { "wh3_dlc26_lord_abilities_gaze_of_khorne" },
		ox = 0, oy = 0 },
	{ marker = "fury_of_the_land", name = "Fury of the Land", trigger = "melee_unwavering",
		badge = "zz_auto_badge_fury_of_the_land",
		keys = { "wh3_dlc24_character_abilities_fury_of_the_land" },
		ox = 0, oy = 0 },
	{ marker = "fury_of_ursun", name = "Fury of Ursun", trigger = "melee_unwavering",
		badge = "zz_auto_badge_fury_of_ursun",
		keys = { "wh3_main_lord_abilities_fury_of_ursun" },
		ox = 0, oy = 0 },
	{ marker = "ghal_maraz", name = "Ghal Maraz", trigger = "melee_unwavering",
		badge = "zz_auto_badge_ghal_maraz",
		keys = { "wh_main_weapon_abilities_ghal_maraz" },
		ox = 0, oy = 0 },
	{ marker = "giant_leap", name = "Giant Leap", trigger = "melee_unwavering",
		badge = "zz_auto_badge_giant_leap",
		keys = { "wh3_dlc24_character_abilities_giant_leap" },
		ox = 0, oy = 0 },
	{ marker = "gitsnik", name = "Gitsnik", trigger = "melee_unwavering",
		badge = "zz_auto_badge_gitsnik",
		keys = { "wh_main_weapon_abilities_gitsnik" },
		ox = 0, oy = 0 },
	{ marker = "gotrek_doom", name = "Gotrek's Doom", trigger = "melee_unwavering",
		badge = "zz_auto_badge_gotrek_doom",
		keys = { "wh2_pro08_character_abilities_gotrek_doom" },
		ox = 0, oy = 0 },
	{ marker = "shield_of_faith_upgraded", name = "Shield of Faith (Upgraded)", trigger = "melee_unwavering",
		badge = "zz_auto_badge_shield_of_faith_upgraded",
		keys = { "wh_dlc04_spell_bound_shield_of_faith_upgraded" },
		ox = 0, oy = 0 },
	{ marker = "great_gutgouger", name = "Great Gutgouger", trigger = "melee_unwavering",
		badge = "zz_auto_badge_great_gutgouger",
		keys = { "wh3_dlc26_weapon_abilities_great_gutgouger" },
		ox = 0, oy = 0 },
	{ marker = "halo_of_maidenly_wrath", name = "Halo of Maidenly Wrath", trigger = "melee_unwavering",
		badge = "zz_auto_badge_halo_of_maidenly_wrath",
		keys = { "wh2_dlc14_lord_abilities_halo_of_maidenly_wrath" },
		ox = 0, oy = 0 },
	{ marker = "hammer_axe_of_skoll", name = "Hammer-Axe of Skoll", trigger = "melee_unwavering",
		badge = "zz_auto_badge_hammer_axe_of_skoll",
		keys = { "wh3_dlc29_weapon_active_hammer_axe_of_skoll" },
		ox = 0, oy = 0 },
	-- BLOCK 2 - THE FOUR NEW-TRIGGER ENTRIES (this round). Each rides its
	-- OWN evaluator (section 7g) with its OWN distinct reason text, so the
	-- field log tells them apart. (The fifth new trigger - the SUMMONED
	-- Foe-Seeker - is NOT an entry here: its key sits on the existing
	-- foe_seeker entry above, so it shares that ability's marker, badge,
	-- arming state and back-off.)
	{ marker = "eagle_feather_torc", name = "Eagle-Feather Torc", trigger = "barrier_broken",
		badge = "zz_auto_badge_eagle_feather_torc",
		keys = { "wh3_dlc27_item_abilities_eagle_feather_torc" },
		ox = 0, oy = 0 },
	{ marker = "fangspike", name = "Fangspike", trigger = "charge_or_melee",
		badge = "zz_auto_badge_fangspike",
		keys = { "wh3_dlc26_weapon_abilities_fangspike" },
		ox = 0, oy = 0 },
	{ marker = "ghoul_king_of_ushoran", name = "Ghoul King of Ushoran", trigger = "ushoran_health",
		badge = "zz_auto_badge_ghoul_king_of_ushoran",
		keys = { "wh2_dlc11_lord_abilities_ghoul_king_of_ushoran" },
		ox = 0, oy = 0 },
	{ marker = "glorious_death", name = "Glorious Death", trigger = "glorious_death",
		badge = "zz_auto_badge_glorious_death",
		keys = { "wh3_dlc25_lord_abilities_glorious_death" },
		ox = 0, oy = 0 },
	-- BLOCK 3 (this round) - THE 38 APPROVED ENTRIES. The 35 in-melee-self
	-- abilities ride the EXISTING shared melee_unwavering evaluator (no new
	-- evaluator); the 3 charge-or-melee abilities ride the EXISTING
	-- charge_or_melee evaluator (the one Fangspike uses). Each carries its
	-- own marker and badge id, so the field log tells them apart; the
	-- trigger emits the SAME distinct reason text the evaluator already
	-- writes. Nothing else in the table changes.
	{ marker = "legbiter", name = "Legbiter", trigger = "melee_unwavering",
		badge = "zz_auto_badge_legbiter",
		keys = { "wh3_dlc29_weapon_abilities_legbiter" },
		ox = 0, oy = 0 },
	{ marker = "hellfire_sword", name = "Hellfire Sword", trigger = "melee_unwavering",
		badge = "zz_auto_badge_hellfire_sword",
		keys = { "wh_main_weapon_abilities_hellfire_sword" },
		ox = 0, oy = 0 },
	{ marker = "helm_of_discord", name = "Helm of Discord", trigger = "melee_unwavering",
		badge = "zz_auto_badge_helm_of_discord",
		keys = { "wh_main_weapon_abilities_helm_of_discord" },
		ox = 0, oy = 0 },
	{ marker = "helm_of_many_eyes", name = "Helm of Many Eyes", trigger = "melee_unwavering",
		badge = "zz_auto_badge_helm_of_many_eyes",
		keys = { "wh_dlc01_item_passive_helm_of_many_eyes" },
		ox = 0, oy = 0 },
	{ marker = "heroic_killing_blow_2", name = "Heroic Killing Blow", trigger = "melee_unwavering",
		badge = "zz_auto_badge_heroic_killing_blow_2",
		keys = { "wh3_main_pro_character_abilities_heroic_killing_blow_2" },
		ox = 0, oy = 0 },
	{ marker = "heroic_killing_blow_dlc07", name = "Heroic Killing Blow", trigger = "melee_unwavering",
		badge = "zz_auto_badge_heroic_killing_blow_dlc07",
		keys = { "wh_dlc07_character_abilities_heroic_killing_blow" },
		ox = 0, oy = 0 },
	{ marker = "heroic_killing_blow_main", name = "Heroic Killing Blow", trigger = "melee_unwavering",
		badge = "zz_auto_badge_heroic_killing_blow_main",
		keys = { "wh_main_character_abilities_heroic_killing_blow" },
		ox = 0, oy = 0 },
	{ marker = "hydra_blade", name = "Hydra Blade", trigger = "melee_unwavering",
		badge = "zz_auto_badge_hydra_blade",
		keys = { "wh2_main_weapon_abilities_hydra_blade" },
		ox = 0, oy = 0 },
	{ marker = "inevitable_horror", name = "Inevitable Horror", trigger = "melee_unwavering",
		badge = "zz_auto_badge_inevitable_horror",
		keys = { "wh3_dlc26_character_abilities_inevitable_horror" },
		ox = 0, oy = 0 },
	{ marker = "karaghul", name = "Karaghul", trigger = "melee_unwavering",
		badge = "zz_auto_badge_karaghul",
		keys = { "wh2_pro08_weapon_abilities_karaghul" },
		ox = 0, oy = 0 },
	{ marker = "killing_blow_1", name = "Killing Blow", trigger = "melee_unwavering",
		badge = "zz_auto_badge_killing_blow_1",
		keys = { "wh3_main_pro_character_abilities_heroic_killing_blow_1" },
		ox = 0, oy = 0 },
	{ marker = "killing_blow", name = "Killing Blow", trigger = "melee_unwavering",
		badge = "zz_auto_badge_killing_blow",
		keys = { "wh_main_unit_abilities_killing_blow" },
		ox = 0, oy = 0 },
	{ marker = "liarsbane", name = "Liarsbane", trigger = "melee_unwavering",
		badge = "zz_auto_badge_liarsbane",
		keys = { "wh3_dlc25_weapon_abilities_liarsbane" },
		ox = 0, oy = 0 },
	{ marker = "lightning_reflexes", name = "Lightning Reflexes", trigger = "charge_or_melee",
		badge = "zz_auto_badge_lightning_reflexes",
		keys = { "wh2_dlc11_lord_abilities_lightning_reflexes" },
		ox = 0, oy = 0 },
	{ marker = "locus_of_beguilement", name = "Locus of Beguilement", trigger = "melee_unwavering",
		badge = "zz_auto_badge_locus_of_beguilement",
		keys = { "wh3_main_character_abilities_locus_of_beguilement" },
		ox = 0, oy = 0 },
	{ marker = "locus_of_grace", name = "Locus of Grace", trigger = "melee_unwavering",
		badge = "zz_auto_badge_locus_of_grace",
		keys = { "wh3_main_character_abilities_locus_of_grace" },
		ox = 0, oy = 0 },
	{ marker = "locus_of_wrath", name = "Locus of Wrath", trigger = "melee_unwavering",
		badge = "zz_auto_badge_locus_of_wrath",
		keys = { "wh3_main_character_abilities_locus_of_wrath" },
		ox = 0, oy = 0 },
	{ marker = "lucky_banner", name = "Lucky Banner", trigger = "melee_unwavering",
		badge = "zz_auto_badge_lucky_banner",
		keys = { "wh2_dlc15_item_abilities_lucky_banner" },
		ox = 0, oy = 0 },
	{ marker = "mace_of_ulumak", name = "Mace of Ulumak", trigger = "melee_unwavering",
		badge = "zz_auto_badge_mace_of_ulumak",
		keys = { "wh2_dlc13_weapon_abilities_mace_of_ulumak" },
		ox = 0, oy = 0 },
	{ marker = "mananns_luck", name = "Manann's Luck", trigger = "melee_unwavering",
		badge = "zz_auto_badge_mananns_luck",
		keys = { "wh2_dlc11_lord_abilities_mananns_luck" },
		ox = 0, oy = 0 },
	{ marker = "master_of_the_skies", name = "Master of the Skies", trigger = "charge_or_melee",
		badge = "zz_auto_badge_master_of_the_skies",
		keys = { "wh2_dlc12_lord_abilities_master_of_the_skies" },
		ox = 0, oy = 0 },
	{ marker = "mimic_waaagh", name = "Mirror (Waaagh!)", trigger = "melee_unwavering",
		badge = "zz_auto_badge_mimic_waaagh",
		keys = { "wh2_dlc15_unit_abilities_mimic_waaagh" },
		ox = 0, oy = 0 },
	{ marker = "mimic_grom_waaagh", name = "Mirror (Grom's Big Waaagh!)", trigger = "melee_unwavering",
		badge = "zz_auto_badge_mimic_grom_waaagh",
		keys = { "wh2_dlc15_unit_abilities_mimic_grom_waaagh" },
		ox = 0, oy = 0 },
	{ marker = "monstrous_strength", name = "Monstrous Strength", trigger = "melee_unwavering",
		badge = "zz_auto_badge_monstrous_strength",
		keys = { "wh2_dlc13_lord_abilities_monstrous_strength" },
		ox = 0, oy = 0 },
	{ marker = "mortal_blow", name = "Mortal Blow", trigger = "melee_unwavering",
		badge = "zz_auto_badge_mortal_blow",
		keys = { "wh3_main_daemon_arms_abilities_mortal_blow" },
		ox = 0, oy = 0 },
	{ marker = "mortal_blow_upgraded", name = "Mortal Blow (Upgraded)", trigger = "melee_unwavering",
		badge = "zz_auto_badge_mortal_blow_upgraded",
		keys = { "wh3_main_daemon_arms_abilities_mortal_blow_upgraded" },
		ox = 0, oy = 0 },
	{ marker = "mumbo_jumbo_chant", name = "Mumbo-Jumbo Chant", trigger = "melee_unwavering",
		badge = "zz_auto_badge_mumbo_jumbo_chant",
		keys = { "wh3_dlc26_character_abilities_mumbo_jumbo_chant" },
		ox = 0, oy = 0 },
	{ marker = "strike_of_nagash", name = "Necrostrike", trigger = "melee_unwavering",
		badge = "zz_auto_badge_strike_of_nagash",
		keys = { "wh2_dlc09_character_abilities_strike_of_nagash" },
		ox = 0, oy = 0 },
	{ marker = "nurgles_favoured_son", name = "Nurgle's Favoured Son", trigger = "melee_unwavering",
		badge = "zz_auto_badge_nurgles_favoured_son",
		keys = { "wh3_dlc25_lord_abilities_nurgles_favoured_son" },
		ox = 0, oy = 0 },
	{ marker = "opal_amulet", name = "Opal Amulet", trigger = "melee_unwavering",
		badge = "zz_auto_badge_opal_amulet",
		keys = { "wh_main_item_abilities_opal_amulet" },
		ox = 0, oy = 0 },
	{ marker = "oracle_of_eternity", name = "Oracle of Eternity", trigger = "melee_unwavering",
		badge = "zz_auto_badge_oracle_of_eternity",
		keys = { "wh3_main_lord_abilities_oracle_of_eternity" },
		ox = 0, oy = 0 },
	{ marker = "pendant_of_slaanesh", name = "Pendant of Slaanesh", trigger = "charge_or_melee",
		badge = "zz_auto_badge_pendant_of_slaanesh",
		keys = { "wh_main_item_abilities_pendant_of_slaanesh" },
		ox = 0, oy = 0 },
	{ marker = "plaguefathers_oration", name = "Plaguefather's Oration", trigger = "melee_unwavering",
		badge = "zz_auto_badge_plaguefathers_oration",
		keys = { "wh3_main_lord_abilities_plaguefathers_oration" },
		ox = 0, oy = 0 },
	{ marker = "primal_roar", name = "Primal Roar", trigger = "melee_unwavering",
		badge = "zz_auto_badge_primal_roar",
		keys = { "wh2_dlc13_lord_abilities_primal_roar" },
		ox = 0, oy = 0 },
	{ marker = "puncture", name = "Puncture", trigger = "melee_unwavering",
		badge = "zz_auto_badge_puncture",
		keys = { "wh3_dlc26_character_abilities_puncture" },
		ox = 0, oy = 0 },
	{ marker = "heart_piercing", name = "Heart Piercing", trigger = "charge_or_melee",
		badge = "zz_auto_badge_heart_piercing",
		keys = { "wh2_dlc11_lord_abilities_heart_piercing" },
		ox = 0, oy = 0 },
	{ marker = "horn_of_the_first_beast", name = "Horn of the First Beast", trigger = "charge_or_melee",
		badge = "zz_auto_badge_horn_of_the_first_beast",
		keys = { "wh_dlc03_item_abilities_horn_of_the_first_beast" },
		ox = 0, oy = 0 },
	{ marker = "morglor_the_mangler", name = "Morglor the Mangler", trigger = "charge_or_melee",
		badge = "zz_auto_badge_morglor_the_mangler",
		keys = { "wh3_dlc26_weapon_abilities_morglor_the_mangler" },
		ox = 0, oy = 0 },
	{ marker = "banespear", name = "The Bane Spear", trigger = "melee_unwavering",
		badge = "zz_auto_badge_banespear",
		keys = { "wh3_main_weapon_abilities_banespear" },
		ox = 0, oy = 0 },
	{ marker = "black_axe_of_krell", name = "The Black Axe of Krell", trigger = "melee_unwavering",
		badge = "zz_auto_badge_black_axe_of_krell",
		keys = { "wh3_dlc29_item_abilities_black_axe_of_krell" },
		ox = 0, oy = 0 },
	{ marker = "black_lotus", name = "Black Lotus", trigger = "melee_unwavering",
		badge = "zz_auto_badge_black_lotus",
		keys = { "wh2_main_character_abilities_black_lotus" },
		ox = 0, oy = 0 },
	{ marker = "blessed_blade_of_ptra", name = "The Blessed Blade of Ptra", trigger = "melee_unwavering",
		badge = "zz_auto_badge_blessed_blade_of_ptra",
		keys = { "wh2_dlc09_weapon_abilities_blessed_blade_of_ptra" },
		ox = 0, oy = 0 },
	{ marker = "daemonic_strength", name = "Daemonic Strength", trigger = "melee_unwavering",
		badge = "zz_auto_badge_daemonic_strength",
		keys = { "wh_main_item_abilities_daemonic_strength" },
		ox = 0, oy = 0 },
	{ marker = "dark_venom", name = "Dark Venom", trigger = "melee_unwavering",
		badge = "zz_auto_badge_dark_venom",
		keys = { "wh2_main_character_abilities_dark_venom" },
		ox = 0, oy = 0 },
	{ marker = "doom_glaive", name = "Doom Glaive", trigger = "melee_unwavering",
		badge = "zz_auto_badge_doom_glaive",
		keys = { "wh3_dlc29_item_abilities_doom_glaive" },
		ox = 0, oy = 0 },
	{ marker = "dragons_fang", name = "The Dragon's Fang", trigger = "melee_unwavering",
		badge = "zz_auto_badge_dragons_fang",
		keys = { "wh3_dlc24_weapon_abilities_dragons_fang" },
		ox = 0, oy = 0 },
	{ marker = "drakwald_runefang", name = "The Drakwald Runefang", trigger = "melee_unwavering",
		badge = "zz_auto_badge_drakwald_runefang",
		keys = { "wh2_dlc13_weapon_abilities_drakwald_runefang" },
		ox = 0, oy = 0 },
	{ marker = "elixir_of_damnation", name = "Elixir of Damnation", trigger = "melee_unwavering",
		badge = "zz_auto_badge_elixir_of_damnation",
		keys = { "wh3_dlc27_item_abilities_elixir_of_damnation" },
		ox = 0, oy = 0 },
	{ marker = "hochland_runefang", name = "The Hochland Runefang", trigger = "melee_unwavering",
		badge = "zz_auto_badge_hochland_runefang",
		keys = { "wh2_dlc13_weapon_abilities_hochland_runefang" },
		ox = 0, oy = 0 },
	{ marker = "nordland_runefang", name = "The Nordland Runefang", trigger = "melee_unwavering",
		badge = "zz_auto_badge_nordland_runefang",
		keys = { "wh2_dlc13_weapon_abilities_nordland_runefang" },
		ox = 0, oy = 0 },
	{ marker = "ostermark_runefang", name = "The Ostermark Runefang", trigger = "melee_unwavering",
		badge = "zz_auto_badge_ostermark_runefang",
		keys = { "wh2_dlc13_weapon_abilities_ostermark_runefang" },
		ox = 0, oy = 0 },
	{ marker = "ostland_runefang", name = "The Ostland Runefang", trigger = "melee_unwavering",
		badge = "zz_auto_badge_ostland_runefang",
		keys = { "wh2_dlc13_weapon_abilities_ostland_runefang" },
		ox = 0, oy = 0 },
	{ marker = "potion_of_strength", name = "Potion of Strength", trigger = "melee_unwavering",
		badge = "zz_auto_badge_potion_of_strength",
		keys = { "wh_main_item_abilities_potion_of_strength" },
		ox = 0, oy = 0 },
	{ marker = "potion_of_toughness", name = "Potion of Toughness", trigger = "melee_health75",
		badge = "zz_auto_badge_potion_of_toughness",
		keys = { "wh_main_item_abilities_potion_of_toughness" },
		ox = 0, oy = 0 },
	{ marker = "quickblood", name = "Quickblood", trigger = "melee_unwavering",
		badge = "zz_auto_badge_quickblood",
		keys = { "wh3_dlc29_lord_abilities_lightning_reflexes" },
		ox = 0, oy = 0 },
	{ marker = "quicksilver_strike", name = "Quicksilver Strike", trigger = "melee_unwavering",
		badge = "zz_auto_badge_quicksilver_strike",
		keys = { "wh3_dlc27_lord_abilities_quicksilver_strike" },
		ox = 0, oy = 0 },
	{ marker = "rage_embodied", name = "Rage Embodied", trigger = "melee_unwavering",
		badge = "zz_auto_badge_rage_embodied",
		keys = { "wh3_main_lord_abilities_rage_embodied" },
		ox = 0, oy = 0 },
	{ marker = "rage_incarnate", name = "Rage Incarnate", trigger = "melee_unwavering",
		badge = "zz_auto_badge_rage_incarnate",
		keys = { "wh3_main_lord_abilities_rage_incarnate" },
		ox = 0, oy = 0 },
	{ marker = "rapier_of_ecstasy", name = "Rapier of Ecstasy", trigger = "melee_unwavering",
		badge = "zz_auto_badge_rapier_of_ecstasy",
		keys = { "wh3_dlc20_weapon_abilities_rapier_of_ecstasy" },
		ox = 0, oy = 0 },
	{ marker = "red_ruin", name = "Red Ruin", trigger = "melee_unwavering",
		badge = "zz_auto_badge_red_ruin",
		keys = { "wh2_dlc10_lord_abilities_red_ruin" },
		ox = 0, oy = 0 },
	{ marker = "refuse_to_die", name = "Refuse to Die", trigger = "melee_unwavering",
		badge = "zz_auto_badge_refuse_to_die",
		keys = { "wh2_dlc12_unit_abilities_refuse_to_die" },
		ox = 0, oy = 0 },
	{ marker = "revenge_incarnate", name = "Revenge Incarnate", trigger = "melee_unwavering",
		badge = "zz_auto_badge_revenge_incarnate",
		keys = { "wh_dlc06_lord_abilities_revenge_incarnate" },
		ox = 0, oy = 0 },
	{ marker = "rock_of_itza", name = "Rok of Itza", trigger = "melee_unwavering",
		badge = "zz_auto_badge_rock_of_itza",
		keys = { "wh2_dlc13_lord_abilities_rock_of_itza" },
		ox = 0, oy = 0 },
	{ marker = "rot_or_die", name = "Rot or Die!", trigger = "melee_unwavering",
		badge = "zz_auto_badge_rot_or_die",
		keys = { "wh3_dlc25_lord_abilities_rot_or_die" },
		ox = 0, oy = 0 },
	{ marker = "rot_pocked_axe", name = "Rot-pocked Axe", trigger = "melee_unwavering",
		badge = "zz_auto_badge_rot_pocked_axe",
		keys = { "wh3_dlc29_item_active_rot_pocked_axe" },
		ox = 0, oy = 0 },
	{ marker = "rune_axe_of_gotrek", name = "Rune Axe of Gotrek", trigger = "melee_unwavering",
		badge = "zz_auto_badge_rune_axe_of_gotrek",
		keys = { "wh2_pro08_weapon_abilities_rune_axe_of_gotrek" },
		ox = 0, oy = 0 },
	{ marker = "rune_axe_of_grombrindal", name = "Rune Axe of Grombrindal", trigger = "melee_unwavering",
		badge = "zz_auto_badge_rune_axe_of_grombrindal",
		keys = { "wh_pro01_weapon_abilities_rune_axe_of_grombrindal" },
		ox = 0, oy = 0 },
	{ marker = "runefang", name = "Runefang", trigger = "melee_unwavering",
		badge = "zz_auto_badge_runefang",
		keys = { "wh_main_weapon_abilities_runefang" },
		ox = 0, oy = 0 },
	{ marker = "sacred_spawning_of_xhotl", name = "Sacred Spawning of Xhotl", trigger = "melee_unwavering",
		badge = "zz_auto_badge_sacred_spawning_of_xhotl",
		keys = { "wh2_main_lord_abilities_sacred_spawning_of_xhotl" },
		ox = 0, oy = 0 },
	{ marker = "sands_of_sickness", name = "Sands of Sickness", trigger = "melee_unwavering",
		badge = "zz_auto_badge_sands_of_sickness",
		keys = { "wh3_dlc25_character_abilities_sands_of_sickness" },
		ox = 0, oy = 0 },
	{ marker = "scales_of_the_celestial_court", name = "Scales of the Celestial Court", trigger = "melee_unwavering",
		badge = "zz_auto_badge_scales_of_the_celestial_court",
		keys = { "wh3_main_item_abilities_scales_of_the_celestial_court" },
		ox = 0, oy = 0 },
	{ marker = "sceptre_of_titans", name = "Sceptre of Titans", trigger = "melee_unwavering",
		badge = "zz_auto_badge_sceptre_of_titans",
		keys = { "wh3_main_weapon_abilities_sceptre_of_titans" },
		ox = 0, oy = 0 },
	{ marker = "scourge", name = "Scourge", trigger = "melee_unwavering",
		badge = "zz_auto_badge_scourge",
		keys = { "wh_dlc03_weapon_abilities_scourge" },
		ox = 0, oy = 0 },
	{ marker = "scrying_stone", name = "Scrying Stone", trigger = "melee_unwavering",
		badge = "zz_auto_badge_scrying_stone",
		keys = { "wh2_main_item_abilities_scrying_stone" },
		ox = 0, oy = 0 },
	{ marker = "seduction_of_the_serpent", name = "Seduction of the Serpent", trigger = "melee_unwavering",
		badge = "zz_auto_badge_seduction_of_the_serpent",
		keys = { "wh_dlc08_lord_abilities_seduction_of_the_serpent" },
		ox = 0, oy = 0 },
	{ marker = "shadow_shroud", name = "Shadow Shroud", trigger = "melee_unwavering",
		badge = "zz_auto_badge_shadow_shroud",
		keys = { "wh3_main_lord_abilities_shadow_shroud" },
		ox = 0, oy = 0 },
	{ marker = "shield_of_aeons", name = "Shield of Aeons", trigger = "melee_unwavering",
		badge = "zz_auto_badge_shield_of_aeons",
		keys = { "wh2_dlc13_item_abilities_shield_of_aeons" },
		ox = 0, oy = 0 },
	{ marker = "shield_of_faith", name = "Shield of Faith", trigger = "melee_unwavering",
		badge = "zz_auto_badge_shield_of_faith",
		keys = { "wh_main_spell_bound_shield_of_faith" },
		ox = 0, oy = 0 },
	{ marker = "silver_dagger", name = "Silver Dagger", trigger = "melee_unwavering",
		badge = "zz_auto_badge_silver_dagger",
		keys = { "wh3_dlc23_weapon_abilities_silver_dagger" },
		ox = 0, oy = 0 },
	{ marker = "skull_wand_of_kaloth", name = "Skull Wand of Kaloth", trigger = "melee_unwavering",
		badge = "zz_auto_badge_skull_wand_of_kaloth",
		keys = { "wh_main_item_abilities_skull_wand_of_kaloth" },
		ox = 0, oy = 0 },
	{ marker = "slippery", name = "Slippery", trigger = "charge_or_melee",
		badge = "zz_auto_badge_slippery",
		keys = { "wh_main_hero_abilities_slippery" },
		ox = 0, oy = 0 },
	{ marker = "sliverslash", name = "Sliverslash", trigger = "melee_unwavering",
		badge = "zz_auto_badge_sliverslash",
		keys = { "wh3_dlc20_weapon_abilities_sliverslash" },
		ox = 0, oy = 0 },
	{ marker = "smash_em_faster", name = "Smash 'Em Faster", trigger = "melee_unwavering",
		badge = "zz_auto_badge_smash_em_faster",
		keys = { "wh2_dlc15_lord_abilities_smash_em_faster" },
		ox = 0, oy = 0 },
	{ marker = "stand_or_die", name = "Stand or Die!", trigger = "melee_unwavering",
		badge = "zz_auto_badge_stand_or_die",
		keys = { "wh_main_character_abilities_stand_or_die" },
		ox = 0, oy = 0 },
	{ marker = "star_lance", name = "Star Lance", trigger = "charge_or_melee",
		badge = "zz_auto_badge_star_lance",
		keys = { "wh2_dlc15_weapon_abilities_star_lance" },
		ox = 0, oy = 0 },
	{ marker = "starcrusher", name = "Starcrusher", trigger = "melee_unwavering",
		badge = "zz_auto_badge_starcrusher",
		keys = { "wh_dlc01_weapon_abilities_starcrusher" },
		ox = 0, oy = 0 },
	{ marker = "steppe_hunters_horn", name = "Steppe Hunter's Horn", trigger = "melee_unwavering",
		badge = "zz_auto_badge_steppe_hunters_horn",
		keys = { "wh3_main_item_abilities_steppe_hunters_horn" },
		ox = 0, oy = 0 },
	{ marker = "stinky_giant_club", name = "Stinky Giant Club", trigger = "melee_unwavering",
		badge = "zz_auto_badge_stinky_giant_club",
		keys = { "wh_dlc08_weapon_abilities_stinky_giant_club" },
		ox = 0, oy = 0 },
	{ marker = "storm_rage", name = "Storm Rage", trigger = "charge_or_melee",
		badge = "zz_auto_badge_storm_rage",
		keys = { "wh3_dlc20_unit_abilities_storm_rage" },
		ox = 0, oy = 0 },
	{ marker = "stormlance", name = "Stormlance", trigger = "charge_or_melee",
		badge = "zz_auto_badge_stormlance",
		keys = { "wh3_dlc25_item_abilities_stormlance" },
		ox = 0, oy = 0 },
	{ marker = "strike_of_tombs", name = "Tombstrike", trigger = "melee_unwavering",
		badge = "zz_auto_badge_strike_of_tombs",
		keys = { "wh2_dlc09_character_abilities_strike_of_tombs" },
		ox = 0, oy = 0 },
	{ marker = "sword_dance", name = "The Dancing Blade", trigger = "melee_unwavering",
		badge = "zz_auto_badge_sword_dance",
		keys = { "wh3_dlc23_character_abilities_sword_dance" },
		ox = 0, oy = 0 },
	{ marker = "sword_of_anti_heroes", name = "Sword of Anti-Heroes", trigger = "melee_unwavering",
		badge = "zz_auto_badge_sword_of_anti_heroes",
		keys = { "wh_main_weapon_abilities_sword_of_anti_heroes" },
		ox = 0, oy = 0 },
	{ marker = "sword_of_lyonesse", name = "The Sword of Lyonesse", trigger = "melee_unwavering",
		badge = "zz_auto_badge_sword_of_lyonesse",
		keys = { "wh2_dlc14_weapon_abilities_sword_of_lyonesse" },
		ox = 0, oy = 0 },
	{ marker = "sword_of_torgald", name = "Sword of Torgald", trigger = "melee_unwavering",
		badge = "zz_auto_badge_sword_of_torgald",
		keys = { "wh_dlc08_weapon_abilities_sword_of_torgald" },
		ox = 0, oy = 0 },
	{ marker = "talabecland_runefang", name = "The Talabecland Runefang", trigger = "melee_unwavering",
		badge = "zz_auto_badge_talabecland_runefang",
		keys = { "wh2_dlc13_weapon_abilities_talabecland_runefang" },
		ox = 0, oy = 0 },
	{ marker = "tempest_rage", name = "Tempest Rage", trigger = "charge_or_melee",
		badge = "zz_auto_badge_tempest_rage",
		keys = { "wh3_dlc20_lord_abilities_tempest_rage" },
		ox = 0, oy = 0 },
	{ marker = "tenebrous_forge_hammer", name = "Tenebrous Forge-Hammer", trigger = "melee_unwavering",
		badge = "zz_auto_badge_tenebrous_forge_hammer",
		keys = { "wh3_dlc27_weapon_abilities_tenebrous_forge_hammer" },
		ox = 0, oy = 0 },
	{ marker = "the_armour_of_morkar", name = "The Armour of Morkar", trigger = "melee_unwavering",
		badge = "zz_auto_badge_the_armour_of_morkar",
		keys = { "wh3_dlc20_item_abilities_the_armour_of_morkar" },
		ox = 0, oy = 0 },
	{ marker = "the_black_cleaver", name = "The Black Cleaver", trigger = "melee_unwavering",
		badge = "zz_auto_badge_the_black_cleaver",
		keys = { "wh3_dlc25_weapon_abilities_the_black_cleaver" },
		ox = 0, oy = 0 },
	{ marker = "the_blood_price", name = "The Blood Price", trigger = "melee_unwavering",
		badge = "zz_auto_badge_the_blood_price",
		keys = { "wh2_dlc14_lord_abilities_the_blood_price" },
		ox = 0, oy = 0 },
	{ marker = "the_carstein_ring", name = "The Carstein Ring", trigger = "melee_unwavering",
		badge = "zz_auto_badge_the_carstein_ring",
		keys = { "wh_dlc04_item_abilities_the_carstein_ring" },
		ox = 0, oy = 0 },
	{ marker = "the_daemons_curse", name = "The Daemon's Curse", trigger = "melee_unwavering",
		badge = "zz_auto_badge_the_daemons_curse",
		keys = { "wh2_dlc14_lord_abilities_the_daemons_curse" },
		ox = 0, oy = 0 },
	{ marker = "the_eternal_blade", name = "The Eternal Blade", trigger = "melee_unwavering",
		badge = "zz_auto_badge_the_eternal_blade",
		keys = { "wh3_main_weapon_abilities_the_eternal_blade" },
		ox = 0, oy = 0 },
	{ marker = "the_father_of_blades", name = "The Father of Blades", trigger = "melee_unwavering",
		badge = "zz_auto_badge_the_father_of_blades",
		keys = { "wh3_dlc25_weapon_abilities_the_father_of_blades" },
		ox = 0, oy = 0 },
	{ marker = "the_horn_of_kygor", name = "The Horn of Kygor", trigger = "charge_or_melee",
		badge = "zz_auto_badge_the_horn_of_kygor",
		keys = { "wh2_main_item_abilities_the_horn_of_kygor" },
		ox = 0, oy = 0 },
	{ marker = "the_mace_of_helsturm", name = "The Mace of Helsturm", trigger = "melee_unwavering",
		badge = "zz_auto_badge_the_mace_of_helsturm",
		keys = { "wh_main_weapon_abilities_the_mace_of_helsturm" },
		ox = 0, oy = 0 },
	{ marker = "the_phoenix_blade", name = "The Phoenix Blade", trigger = "melee_unwavering",
		badge = "zz_auto_badge_the_phoenix_blade",
		keys = { "wh3_dlc27_weapon_abilities_the_phoenix_blade" },
		ox = 0, oy = 0 },
	{ marker = "the_reikland_runefang", name = "The Reikland Runefang", trigger = "melee_unwavering",
		badge = "zz_auto_badge_the_reikland_runefang",
		keys = { "wh_main_weapon_abilities_the_reikland_runefang" },
		ox = 0, oy = 0 },
	{ marker = "the_rock_of_inevitability", name = "The Rock of Inevitability", trigger = "melee_unwavering",
		badge = "zz_auto_badge_the_rock_of_inevitability",
		keys = { "wh3_main_item_abilities_the_rock_of_inevitability" },
		ox = 0, oy = 0 },
	{ marker = "the_rotaxes", name = "The Rotaxes", trigger = "melee_unwavering",
		badge = "zz_auto_badge_the_rotaxes",
		keys = { "wh3_dlc29_item_active_the_rotaxes" },
		ox = 0, oy = 0 },
	{ marker = "the_slayer_of_kings", name = "The Slayer of Kings", trigger = "melee_unwavering",
		badge = "zz_auto_badge_the_slayer_of_kings",
		keys = { "wh_dlc01_weapon_abilities_the_slayer_of_kings" },
		ox = 0, oy = 0 },
	{ marker = "the_slayer_sword", name = "The Slayer Sword", trigger = "melee_unwavering",
		badge = "zz_auto_badge_the_slayer_sword",
		keys = { "wh3_dlc26_weapon_abilities_the_slayer_sword" },
		ox = 0, oy = 0 },
	{ marker = "the_sword_of_couronne", name = "The Sword of Couronne", trigger = "melee_unwavering",
		badge = "zz_auto_badge_the_sword_of_couronne",
		keys = { "wh_main_weapon_abilities_the_sword_of_couronne" },
		ox = 0, oy = 0 },
	{ marker = "the_tenderiser", name = "The Tenderiser", trigger = "melee_unwavering",
		badge = "zz_auto_badge_the_tenderiser",
		keys = { "wh3_main_weapon_abilities_the_tenderiser" },
		ox = 0, oy = 0 },
	{ marker = "toad_rage", name = "Toad Rage", trigger = "melee_unwavering",
		badge = "zz_auto_badge_toad_rage",
		keys = { "wh2_dlc12_unit_abilities_toad_rage" },
		ox = 0, oy = 0 },
	{ marker = "tormentor_sword", name = "Tormentor Sword", trigger = "melee_unwavering",
		badge = "zz_auto_badge_tormentor_sword",
		keys = { "wh_main_weapon_abilities_tormentor_sword" },
		ox = 0, oy = 0 },
	{ marker = "tors_battle_hymn", name = "Tor's Battle Hymn", trigger = "melee_unwavering",
		badge = "zz_auto_badge_tors_battle_hymn",
		keys = { "wh3_main_character_abilities_tors_battle_hymn" },
		ox = 0, oy = 0 },
	{ marker = "transfix", name = "Transfix", trigger = "charge_or_melee",
		badge = "zz_auto_badge_transfix",
		keys = { "wh2_dlc11_lord_abilities_transfix" },
		ox = 0, oy = 0 },
	{ marker = "unyielding_defender", name = "Unyielding Defence", trigger = "melee_unwavering",
		badge = "zz_auto_badge_unyielding_defender",
		keys = { "wh3_main_character_abilities_unyielding_defender" },
		ox = 0, oy = 0 },
	{ marker = "ursuns_claw", name = "Ursun's Claw", trigger = "melee_unwavering",
		badge = "zz_auto_badge_ursuns_claw",
		keys = { "wh3_dlc24_weapon_abilities_ursuns_claw" },
		ox = 0, oy = 0 },
	{ marker = "warp_frenzy", name = "Warp Frenzy", trigger = "melee_unwavering",
		badge = "zz_auto_badge_warp_frenzy",
		keys = { "wh2_dlc16_hero_abilities_warp_frenzy" },
		ox = 0, oy = 0 },
	{ marker = "warriors_crest", name = "Warrior's Crest", trigger = "melee_unwavering",
		badge = "zz_auto_badge_warriors_crest",
		keys = { "wh2_dlc12_lord_abilities_warriors_crest" },
		ox = 0, oy = 0 },
	{ marker = "will_of_the_verminking", name = "Will of the Verminking", trigger = "verminking_wavering",
		badge = "zz_auto_badge_will_of_the_verminking",
		keys = { "wh3_dlc29_lord_abilities_will_of_the_verminking" },
		ox = 0, oy = 0 },
	{ marker = "witstealer_sword", name = "Witstealer Sword", trigger = "melee_unwavering",
		badge = "zz_auto_badge_witstealer_sword",
		keys = { "wh3_main_weapon_abilities_witstealer_sword" },
		ox = 0, oy = 0 },
	{ marker = "enchanted_metallurgy", name = "Enchanted Metallurgy", trigger = "melee_or_shooting_aura",
		badge = "zz_auto_badge_enchanted_metallurgy",
		keys = { "wh3_main_character_abilities_enchanted_metallurgy" },
		aura_real = 35,
		ox = 0, oy = 0 },
	{ marker = "enchanted_metallurgy_flaming", name = "Enchanted Metallurgy: Flaming", trigger = "melee_or_shooting_aura",
		badge = "zz_auto_badge_enchanted_metallurgy_flaming",
		keys = { "wh3_main_character_abilities_enchanted_metallurgy_flaming" },
		aura_real = 35,
		ox = 0, oy = 0 },
	{ marker = "enchanted_metallurgy_piercing", name = "Enchanted Metallurgy: Piercing", trigger = "melee_or_shooting_aura",
		badge = "zz_auto_badge_enchanted_metallurgy_piercing",
		keys = { "wh3_main_character_abilities_enchanted_metallurgy_piercing" },
		aura_real = 35,
		ox = 0, oy = 0 },
	{ marker = "enchanted_metallurgy_poison", name = "Enchanted Metallurgy: Poison", trigger = "melee_or_shooting_aura",
		badge = "zz_auto_badge_enchanted_metallurgy_poison",
		keys = { "wh3_main_character_abilities_enchanted_metallurgy_poison" },
		aura_real = 35,
		ox = 0, oy = 0 },
	{ marker = "bastions_defenders", name = "Bastion's Defenders", trigger = "melee_unwavering",
		badge = "zz_auto_badge_bastions_defenders",
		keys = { "wh3_dlc24_character_abilities_bastions_defenders" },
		ox = 0, oy = 0 },
	{ marker = "battle_of_wills", name = "Battle of Wills", trigger = "melee_unwavering",
		badge = "zz_auto_badge_battle_of_wills",
		keys = { "wh3_dlc29_unit_abilities_battle_of_wills" },
		ox = 0, oy = 0 },
	{ marker = "bironas_timewarp", name = "Birona's Timewarp", trigger = "charge_or_melee",
		badge = "zz_auto_badge_bironas_timewarp",
		keys = { "wh_main_spell_bound_bironas_timewarp" },
		ox = 0, oy = 0 },
	{ marker = "breath_of_hatred", name = "Breath of Hatred", trigger = "melee_unwavering",
		badge = "zz_auto_badge_breath_of_hatred",
		keys = { "wh3_dlc23_bound_abilities_breath_of_hatred", "wh3_dlc23_character_abilities_breath_of_hatred" },
		ox = 0, oy = 0 },
	{ marker = "captain_of_the_phoenix_guard", name = "Captain of the Phoenix Guard", trigger = "ally_heal_melee",
		badge = "zz_auto_badge_captain_of_the_phoenix_guard",
		keys = { "wh3_dlc27_character_abilities_captain_of_the_phoenix_guard" },
		ally_range_real = 50,
		ox = 0, oy = 0 },
	{ marker = "cash_cascade", name = "Cash Cascade", trigger = "charge_or_melee",
		badge = "zz_auto_badge_cash_cascade",
		keys = { "wh3_dlc26_character_abilities_cash_cascade" },
		ox = 0, oy = 0 },
	{ marker = "commanding_presence", name = "Commanding Presence", trigger = "wavering_self_or_ally",
		badge = "zz_auto_badge_commanding_presence",
		keys = { "wh3_dlc29_lord_active_commanding_presence" },
		ox = 0, oy = 0 },
	{ marker = "curse_of_years", name = "Curse of Years", trigger = "melee_unwavering",
		badge = "zz_auto_badge_curse_of_years",
		keys = { "wh3_dlc29_spell_bound_curse_of_years" },
		ox = 0, oy = 0 },
	{ marker = "da_boss_as_a_plan", name = "Da Boss 'as a Plan!", trigger = "ally_melee_buff",
		badge = "zz_auto_badge_da_boss_as_a_plan",
		keys = { "wh3_dlc26_character_abilities_da_boss_as_a_plan" },
		ally_range_real = 150,
		ox = 0, oy = 0 },
	{ marker = "dazs_song_of_winter_sunlight", name = "Dazh's Song of Winter Sunlight", trigger = "tired",
		badge = "zz_auto_badge_dazs_song_of_winter_sunlight",
		keys = { "wh3_main_character_abilities_dazs_song_of_winter_sunlight", "wh3_twa06_unit_abilities_dazs_song_of_winter_sunlight" },
		ox = 0, oy = 0 },
	{ marker = "death_frenzy", name = "Death Frenzy", trigger = "melee_unwavering",
		badge = "zz_auto_badge_death_frenzy",
		keys = { "wh2_dlc16_spell_bound_death_frenzy" },
		ox = 0, oy = 0 },
	{ marker = "dragonhorn", name = "Dragonhorn", trigger = "melee_unwavering",
		badge = "zz_auto_badge_dragonhorn",
		keys = { "wh2_dlc15_lord_abilities_dragonhorn" },
		ox = 0, oy = 0 },
	{ marker = "empowering_shrooms", name = "Empowering Shrooms", trigger = "melee_unwavering",
		badge = "zz_auto_badge_empowering_shrooms",
		keys = { "wh3_dlc26_character_abilities_empowering_shrooms" },
		ox = 0, oy = 0 },
	{ marker = "favour_of_the_fay", name = "Favour of the Fay", trigger = "ally_melee_buff",
		badge = "zz_auto_badge_favour_of_the_fay",
		keys = { "wh_dlc07_lord_abilities_favour_of_the_fay" },
		ally_range_real = 100,
		ox = 0, oy = 0 },
	{ marker = "ferocious_battle_howl", name = "Ferocious Battle Howl", trigger = "charge_only",
		badge = "zz_auto_badge_ferocious_battle_howl",
		keys = { "wh3_dlc29_spell_bound_prayer_ferocious_battle_howl" },
		ox = 0, oy = 0 },
	{ marker = "ferocious_fury_of_ulric", name = "Ferocious Fury of Ulric", trigger = "wavering_self",
		badge = "zz_auto_badge_ferocious_fury_of_ulric",
		keys = { "wh3_dlc29_spell_bound_prayer_ferocious_fury_of_ulric" },
		ox = 0, oy = 0 },
	{ marker = "ferocious_winters_chill", name = "Ferocious Winter’s Chill", trigger = "melee_unwavering",
		badge = "zz_auto_badge_ferocious_winters_chill",
		keys = { "wh3_dlc29_spell_bound_prayer_ferocious_winters_chill" },
		ox = 0, oy = 0 },
	{ marker = "flame_incarnate", name = "Flame Incarnate", trigger = "melee_unwavering",
		badge = "zz_auto_badge_flame_incarnate",
		keys = { "wh3_main_character_abilities_flame_incarnate" },
		ox = 0, oy = 0 },
	{ marker = "fury_of_khaine", name = "Fury of Khaine", trigger = "ally_melee_buff",
		badge = "zz_auto_badge_fury_of_khaine",
		keys = { "wh2_main_unit_abilities_fury_of_khaine" },
		ally_range_real = 100,
		ox = 0, oy = 0 },
	{ marker = "fury_of_ulric", name = "Fury of Ulric", trigger = "wavering_self_or_ally",
		badge = "zz_auto_badge_fury_of_ulric",
		keys = { "wh3_dlc29_spell_bound_prayer_fury_of_ulric" },
		ox = 0, oy = 0 },
	{ marker = "gate_of_khorne", name = "Gate of Khorne", trigger = "enemy_ground_melee",
		badge = "zz_auto_badge_gate_of_khorne",
		keys = { "wh3_main_character_abilities_gate_of_khorne" },
		range_real = 50,
		ox = 0, oy = 0 },
	{ marker = "gaze_of_khaine", name = "Gaze of Khaine", trigger = "melee_unwavering",
		badge = "zz_auto_badge_gaze_of_khaine",
		keys = { "wh2_dlc10_lord_abilities_gaze_of_khaine" },
		ox = 0, oy = 0 },
	{ marker = "gulyas", name = "Gulyas", trigger = "health_aura_ground",
		badge = "zz_auto_badge_gulyas",
		keys = { "wh3_dlc24_lord_abilities_gulyas" },
		aura_real = 35,
		ox = 0, oy = 0 },
	{ marker = "helm_of_yvresse", name = "Helm of Yvresse", trigger = "wavering_self",
		badge = "zz_auto_badge_helm_of_yvresse",
		keys = { "wh2_dlc15_item_abilities_helm_of_yvresse" },
		ox = 0, oy = 0 },
	{ marker = "helping_hand", name = "Helping Hand", trigger = "ally_melee_buff",
		badge = "zz_auto_badge_helping_hand",
		keys = { "wh2_pro08_character_abilities_helping_hand" },
		ally_range_real = 50,
		ox = 0, oy = 0 },
	{ marker = "inspired_assault_i", name = "Inspired Assault I", trigger = "ally_melee_buff",
		badge = "zz_auto_badge_inspired_assault_i",
		keys = { "wh3_main_lord_abilities_inspired_assault_i" },
		ally_range_real = 100,
		ox = 0, oy = 0 },
	{ marker = "inspired_assault_ii", name = "Inspired Assault II", trigger = "ally_melee_buff",
		badge = "zz_auto_badge_inspired_assault_ii",
		keys = { "wh3_main_lord_abilities_inspired_assault_ii" },
		ally_range_real = 100,
		ox = 0, oy = 0 },
	{ marker = "inspired_assault_iii", name = "Inspired Assault III", trigger = "ally_melee_buff",
		badge = "zz_auto_badge_inspired_assault_iii",
		keys = { "wh3_main_lord_abilities_inspired_assault_iii" },
		ally_range_real = 100,
		ox = 0, oy = 0 },
	{ marker = "inspired_defence_i", name = "Inspired Defence I", trigger = "ally_melee_buff",
		badge = "zz_auto_badge_inspired_defence_i",
		keys = { "wh3_main_lord_abilities_inspired_defence_i" },
		ally_range_real = 100,
		ox = 0, oy = 0 },
	{ marker = "inspired_defence_ii", name = "Inspired Defence II", trigger = "ally_melee_buff",
		badge = "zz_auto_badge_inspired_defence_ii",
		keys = { "wh3_main_lord_abilities_inspired_defence_ii" },
		ally_range_real = 100,
		ox = 0, oy = 0 },
	{ marker = "inspired_defence_iii", name = "Inspired Defence III", trigger = "ally_melee_buff",
		badge = "zz_auto_badge_inspired_defence_iii",
		keys = { "wh3_main_lord_abilities_inspired_defence_iii" },
		ally_range_real = 100,
		ox = 0, oy = 0 },
	{ marker = "lord_of_grand_cathay", name = "Lord of Grand Cathay", trigger = "melee_unwavering",
		badge = "zz_auto_badge_lord_of_grand_cathay",
		keys = { "wh3_dlc24_lord_abilities_lord_of_grand_cathay" },
		ox = 0, oy = 0 },
	{ marker = "master_of_alchemy", name = "Master of Alchemy", trigger = "melee_or_shooting_aura",
		badge = "zz_auto_badge_master_of_alchemy",
		keys = { "wh3_main_lord_abilities_master_of_alchemy" },
		aura_real = 35,
		ox = 0, oy = 0 },
	{ marker = "master_of_alchemy_flaming", name = "Master of Alchemy: Flaming", trigger = "melee_or_shooting_aura",
		badge = "zz_auto_badge_master_of_alchemy_flaming",
		keys = { "wh3_main_lord_abilities_master_of_alchemy_flaming" },
		aura_real = 35,
		ox = 0, oy = 0 },
	{ marker = "master_of_alchemy_piercing", name = "Master of Alchemy: Piercing", trigger = "melee_or_shooting_aura",
		badge = "zz_auto_badge_master_of_alchemy_piercing",
		keys = { "wh3_main_lord_abilities_master_of_alchemy_piercing" },
		aura_real = 35,
		ox = 0, oy = 0 },
	{ marker = "master_of_alchemy_poison", name = "Master of Alchemy: Poison", trigger = "melee_or_shooting_aura",
		badge = "zz_auto_badge_master_of_alchemy_poison",
		keys = { "wh3_main_lord_abilities_master_of_alchemy_poison" },
		aura_real = 35,
		ox = 0, oy = 0 },
	{ marker = "master_rune_of_oath_and_steel", name = "Master Rune of Oath & Steel", trigger = "melee_unwavering",
		badge = "zz_auto_badge_master_rune_of_oath_and_steel",
		keys = { "wh_dlc06_rune_abilities_master_rune_of_oath_and_steel" },
		ox = 0, oy = 0 },
	{ marker = "master_rune_of_speed", name = "Master Rune of Speed", trigger = "charge_or_melee",
		badge = "zz_auto_badge_master_rune_of_speed",
		keys = { "wh2_dlc17_rune_abilities_master_rune_of_speed" },
		ox = 0, oy = 0 },
	{ marker = "offense_prayer", name = "Mantra of Righteousness", trigger = "melee_unwavering",
		badge = "zz_auto_badge_offense_prayer",
		keys = { "wh3_cp1_character_abilities_offense_prayer" },
		ox = 0, oy = 0 },
	{ marker = "okkams_mindrazor", name = "Okkam's Mindrazor", trigger = "melee_unwavering",
		badge = "zz_auto_badge_okkams_mindrazor",
		keys = { "wh3_dlc29_spell_bound_okkams_mindrazor" },
		ox = 0, oy = 0 },
	{ marker = "orcs_are_da_best", name = "Orcs are da Best!", trigger = "ally_melee_buff",
		badge = "zz_auto_badge_orcs_are_da_best",
		keys = { "wh3_dlc26_character_abilities_orcs_are_da_best" },
		ally_range_real = 150,
		ox = 0, oy = 0 },
	{ marker = "overseer_of_the_unseen", name = "Overseer of the Unseen", trigger = "ally_overseer",
		badge = "zz_auto_badge_overseer_of_the_unseen",
		keys = { "wh3_dlc29_hero_active_overseer_of_the_unseen" },
		ally_range_real = 100,
		ox = 0, oy = 0 },
	{ marker = "primeval_roar", name = "Primeval Roar", trigger = "melee_unwavering",
		badge = "zz_auto_badge_primeval_roar",
		keys = { "wh2_dlc17_unit_abilities_primeval_roar" },
		ox = 0, oy = 0 },
	{ marker = "protection_prayer", name = "Mantra of Invigoration", trigger = "ushoran_health",
		badge = "zz_auto_badge_protection_prayer",
		keys = { "wh3_cp1_character_abilities_protection_prayer" },
		ox = 0, oy = 0 },
	{ marker = "rune_of_doom", name = "Rune of Doom", trigger = "melee_unwavering",
		badge = "zz_auto_badge_rune_of_doom",
		keys = { "wh2_dlc17_lord_abilities_rune_of_doom" },
		ox = 0, oy = 0 },
	{ marker = "rune_of_oath_and_steel", name = "Rune of Oath & Steel", trigger = "melee_unwavering",
		badge = "zz_auto_badge_rune_of_oath_and_steel",
		keys = { "wh_main_rune_abilities_rune_of_oath_and_steel" },
		ox = 0, oy = 0 },
	{ marker = "rune_of_speed", name = "Rune of Speed", trigger = "charge_or_melee",
		badge = "zz_auto_badge_rune_of_speed",
		keys = { "wh2_dlc17_rune_abilities_rune_of_speed" },
		ox = 0, oy = 0 },
	{ marker = "sausage_busta", name = "Bangers & Smash", trigger = "charge_or_wavering",
		badge = "zz_auto_badge_sausage_busta",
		keys = { "wh2_dlc15_character_abilities_sausage_busta" },
		ox = 0, oy = 0 },
	{ marker = "shield_of_the_old_ones", name = "Shield of the Old Ones", trigger = "melee_unwavering",
		badge = "zz_auto_badge_shield_of_the_old_ones",
		keys = { "wh2_main_character_abilities_shield_of_the_old_ones" },
		ox = 0, oy = 0 },
	{ marker = "slayer_for_chaos", name = "Slayer for Chaos", trigger = "melee_unwavering",
		badge = "zz_auto_badge_slayer_for_chaos",
		keys = { "wh3_dlc23_item_abilities_slayer_for_chaos" },
		ox = 0, oy = 0 },
	{ marker = "spite_of_da_bad_moon", name = "Spite of Da Bad Moon", trigger = "melee_unwavering",
		badge = "zz_auto_badge_spite_of_da_bad_moon",
		keys = { "wh_dlc06_lord_abilities_spite_of_da_bad_moon" },
		ox = 0, oy = 0 },
	{ marker = "star_of_avelorn", name = "Star of Avelorn", trigger = "health_aura_ground",
		badge = "zz_auto_badge_star_of_avelorn",
		keys = { "wh2_dlc10_item_abilities_star_of_avelorn" },
		aura_real = 15,
		ox = 0, oy = 0 },
	{ marker = "stay_here_ill_get_help", name = "\"Stay Here, I'll Get Help!\"", trigger = "wavering_ally_range",
		badge = "zz_auto_badge_stay_here_ill_get_help",
		keys = { "wh2_dlc09_character_abilities_stay_here_ill_get_help" },
		ally_range_real = 60,
		ox = 0, oy = 0 },
	{ marker = "supreme_shield_of_the_old_ones", name = "Supreme Shield of the Old Ones", trigger = "melee_unwavering",
		badge = "zz_auto_badge_supreme_shield_of_the_old_ones",
		keys = { "wh2_dlc12_character_abilities_supreme_shield_of_the_old_ones" },
		ox = 0, oy = 0 },
	{ marker = "talisman_of_loec", name = "Talisman of Loec", trigger = "melee_unwavering",
		badge = "zz_auto_badge_talisman_of_loec",
		keys = { "wh2_main_item_abilities_talisman_of_loec" },
		ox = 0, oy = 0 },
	{ marker = "the_liber_mortis", name = "The Liber Mortis", trigger = "melee_unwavering",
		badge = "zz_auto_badge_the_liber_mortis",
		keys = { "wh2_dlc09_lord_abilities_the_liber_mortis" },
		ox = 0, oy = 0 },
	{ marker = "vial_of_troll_blood", name = "Vial of Troll Blood", trigger = "wavering_self",
		badge = "zz_auto_badge_vial_of_troll_blood",
		keys = { "wh_dlc08_item_abilities_vial_of_troll_blood" },
		ox = 0, oy = 0 },
	{ marker = "warpstone_addiction", name = "Warpstone Addiction", trigger = "melee_unwavering",
		badge = "zz_auto_badge_warpstone_addiction",
		keys = { "wh3_dlc29_lord_abilities_warpstone_addiction" },
		ox = 0, oy = 0 },
	{ marker = "warrior_familiar", name = "Warrior Familiar", trigger = "melee_unwavering",
		badge = "zz_auto_badge_warrior_familiar",
		keys = { "wh3_dlc27_item_abilities_warrior_familiar" },
		ox = 0, oy = 0 },
	{ marker = "winters_chill", name = "Winter’s Chill", trigger = "melee_unwavering",
		badge = "zz_auto_badge_winters_chill",
		keys = { "wh3_dlc29_ability_bound_prayer_winters_chill", "wh3_dlc29_spell_bound_prayer_winters_chill" },
		ox = 0, oy = 0 },
	{ marker = "witchbrew", name = "Witchbrew", trigger = "melee_unwavering",
		badge = "zz_auto_badge_witchbrew",
		keys = { "wh2_main_character_abilities_witchbrew", "wh3_dlc24_unit_abilities_witchbrew" },
		ox = 0, oy = 0 },
	{ marker = "worlds_edge_armour", name = "World's Edge Armour", trigger = "melee_unwavering",
		badge = "zz_auto_badge_worlds_edge_armour",
		keys = { "wh2_main_item_abilities_worlds_edge_armour" },
		ox = 0, oy = 0 },
	{ marker = "znarkharjas_ward", name = "Znarkharja's Ward", trigger = "melee_unwavering",
		badge = "zz_auto_badge_znarkharjas_ward",
		keys = { "wh3_dlc24_hero_abilities_znarkharjas_ward" },
		ox = 0, oy = 0 },
	-- ============================================================================
	-- THE 327 AUTO-ACCEPTED ABILITIES (this round) - the 2026-10-09 standing
	-- auto-rules R1-R4 sweep (provenance: _classify_wh3.py). 311 entries /
	-- 327 database keys, riding THREE EXISTING evaluators - no new trigger types
	-- this round, so this is a DATA APPEND, not a logic change:
	--   melee_unwavering  261 entries / 274 keys  (in-melee self)
	--   ushoran_health     36 entries /  37 keys  (health <= 75%, no melee gate)
	--   charge_or_melee    14 entries /  16 keys  (charge window OR in melee)
	-- Base + DLC/summoned twin keys ride ONE entry (the Foe-Seeker convention);
	-- every entry self-casts and its ox/oy stay at the top slot (0, 0) for the
	-- wheel-slot fallback. Derived from WH3_ability_tracker.md section 3a.
	-- ============================================================================
	-- in-melee self (the approved R1/R2 combat-buff + hex batch) (261 entries)
	{ marker = "accusation", name = "Accusation", trigger = "enemy_engaged_or_shot",
		badge = "zz_auto_badge_accusation",
		keys = { "wh_main_hero_abilities_accusation" },
		range_real = 75,
		ox = 0, oy = 0 },
	{ marker = "acquiescence", name = "Acquiescence", trigger = "enemy_melee",
		badge = "zz_auto_badge_acquiescence",
		keys = { "wh3_dlc27_spell_bound_acquiescence" },
		range_real = 200,
		ox = 0, oy = 0 },
	{ marker = "aken_seth_the_staff_of_pain", name = "Aken-seth, the Staff of Pain", trigger = "melee_unwavering",
		badge = "zz_auto_badge_aken_seth_the_staff_of_pain",
		keys = { "wh3_dlc29_weapon_abilities_aken_seth_the_staff_of_pain" },
		ox = 0, oy = 0 },
	{ marker = "alchemists_elixir_of_iron_skin", name = "Alchemist's Elixir of Iron Skin", trigger = "melee_unwavering",
		badge = "zz_auto_badge_alchemists_elixir_of_iron_skin",
		keys = { "wh3_main_item_abilities_alchemists_elixir_of_iron_skin" },
		ox = 0, oy = 0 },
	{ marker = "alchemists_elixir_of_puissance", name = "Alchemist's Elixir of Puissance", trigger = "melee_unwavering",
		badge = "zz_auto_badge_alchemists_elixir_of_puissance",
		keys = { "wh3_main_item_abilities_alchemists_elixir_of_puissance" },
		ox = 0, oy = 0 },
	{ marker = "alchemists_elixir_of_venom", name = "Alchemist's Elixir of Venom", trigger = "melee_unwavering",
		badge = "zz_auto_badge_alchemists_elixir_of_venom",
		keys = { "wh3_main_item_abilities_alchemists_elixir_of_venom" },
		ox = 0, oy = 0 },
	{ marker = "all_hands_hoay", name = "All Hands Hoay!", trigger = "melee_unwavering",
		badge = "zz_auto_badge_all_hands_hoay",
		keys = { "wh2_dlc11_character_abilities_all_hands_hoay" },
		ox = 0, oy = 0 },
	{ marker = "amulet_of_itzl", name = "Amulet of Itzl", trigger = "melee_unwavering",
		badge = "zz_auto_badge_amulet_of_itzl",
		keys = { "wh2_main_item_abilities_amulet_of_itzl" },
		ox = 0, oy = 0 },
	{ marker = "amulet_of_phastah", name = "Amulet of Pha-Stah", trigger = "enemy_ground_area",
		badge = "zz_auto_badge_amulet_of_phastah",
		keys = { "wh2_dlc09_item_abilities_amulet_of_phastah" },
		range_real = 100,
		ox = 0, oy = 0 },
	{ marker = "apocalyptic_charge", name = "Apocalyptic Charge", trigger = "charge_only",
		badge = "zz_auto_badge_apocalyptic_charge",
		keys = { "wh_pro04_unit_abilities_apocalyptic_charge" },
		ox = 0, oy = 0 },
	{ marker = "magic_prayer", name = "Arcane Hymn", trigger = "melee_unwavering",
		badge = "zz_auto_badge_magic_prayer",
		keys = { "wh3_cp1_character_abilities_magic_prayer" },
		ox = 0, oy = 0 },
	{ marker = "armour_of_caledor", name = "Armour of Caledor", trigger = "melee_unwavering",
		badge = "zz_auto_badge_armour_of_caledor",
		keys = { "wh2_dlc15_item_abilities_armour_of_caledor" },
		ox = 0, oy = 0 },
	{ marker = "armour_of_the_burrows", name = "Armour of the Barrows", trigger = "melee_unwavering",
		badge = "zz_auto_badge_armour_of_the_burrows",
		keys = { "wh3_dlc29_item_abilities_armour_of_the_burrows" },
		ox = 0, oy = 0 },
	{ marker = "assassins_trophy", name = "Assassin's Trophy", trigger = "enemy_melee",
		badge = "zz_auto_badge_assassins_trophy",
		keys = { "wh2_main_character_abilities_assassins_trophy" },
		range_real = 150,
		target_class = "commander",
		ox = 0, oy = 0 },
	{ marker = "aura_of_inertia", name = "Aura of Inertia", trigger = "melee_unwavering",
		badge = "zz_auto_badge_aura_of_inertia",
		keys = { "wh2_dlc13_lord_abilities_aura_of_inertia" },
		ox = 0, oy = 0 },
	{ marker = "avast_ye", name = "Avast Ye!", trigger = "melee_unwavering",
		badge = "zz_auto_badge_avast_ye",
		keys = { "wh2_dlc11_character_abilities_avast_ye" },
		ox = 0, oy = 0 },
	{ marker = "axe_of_men", name = "Axe of Men", trigger = "melee_unwavering",
		badge = "zz_auto_badge_axe_of_men",
		keys = { "wh_dlc03_weapon_abilities_axe_of_men" },
		ox = 0, oy = 0 },
	{ marker = "barbed_knuckle_boxing", name = "Barbed-Knuckle Boxing", trigger = "melee_unwavering",
		badge = "zz_auto_badge_barbed_knuckle_boxing",
		keys = { "wh2_dlc17_lord_abilities_barbed_knuckle_boxing" },
		ox = 0, oy = 0 },
	{ marker = "bastet", name = "Bastet", trigger = "enemy_engaged_or_shot",
		badge = "zz_auto_badge_bastet",
		keys = { "wh3_dlc29_lord_abilities_bastet" },
		range_real = 100,
		ox = 0, oy = 0 },
	{ marker = "black_periapt", name = "Black Periapt", trigger = "melee_unwavering",
		badge = "zz_auto_badge_black_periapt",
		keys = { "wh_main_item_abilities_black_periapt" },
		ox = 0, oy = 0 },
	{ marker = "black_staff", name = "Black Staff", trigger = "melee_unwavering",
		badge = "zz_auto_badge_black_staff",
		keys = { "wh2_main_spell_bound_black_staff" },
		ox = 0, oy = 0 },
	{ marker = "blade_of_setep", name = "Blade of Setep", trigger = "enemy_engaged_or_shot",
		badge = "zz_auto_badge_blade_of_setep",
		keys = { "wh2_dlc09_weapon_abilities_blade_of_setep" },
		range_real = 100,
		ox = 0, oy = 0 },
	{ marker = "blessed_helm_of_the_oblast", name = "Blessed Helm of the Oblast", trigger = "melee_or_under_fire",
		badge = "zz_auto_badge_blessed_helm_of_the_oblast",
		keys = { "wh3_dlc24_item_abilities_blessed_helm_of_the_oblast" },
		aura_real = 35,
		ox = 0, oy = 0 },
	{ marker = "blight_of_terrors", name = "Blight of Terrors", trigger = "melee_unwavering",
		badge = "zz_auto_badge_blight_of_terrors",
		keys = { "wh2_dlc16_character_abilities_blight_of_terrors" },
		ox = 0, oy = 0 },
	{ marker = "blight_swarm", name = "Blight Swarm", trigger = "enemy_melee",
		badge = "zz_auto_badge_blight_swarm",
		keys = { "wh3_main_lord_abilities_blight_swarm" },
		range_real = 200,
		ox = 0, oy = 0 },
	{ marker = "blood_omens", name = "Blood Omens", trigger = "melee_unwavering",
		badge = "zz_auto_badge_blood_omens",
		keys = { "wh3_dlc29_unit_abilities_blood_omens" },
		ox = 0, oy = 0 },
	{ marker = "bloody_onslaught", name = "Bloody Onslaught", trigger = "enemy_engaged_or_shot",
		badge = "zz_auto_badge_bloody_onslaught",
		keys = { "wh3_dlc26_character_abilities_bloody_onslaught" },
		range_real = 75,
		ox = 0, oy = 0 },
	{ marker = "blooood", name = "Blooood!", trigger = "charge_only",
		badge = "zz_auto_badge_blooood",
		keys = { "wh_main_unit_abilities_blooood" },
		ox = 0, oy = 0 },
	{ marker = "book_of_arkhan", name = "Book of Arkhan", trigger = "charge_or_melee",
		badge = "zz_auto_badge_book_of_arkhan",
		keys = { "wh_main_spell_bound_book_of_arkhan" },
		ox = 0, oy = 0 },
	{ marker = "book_of_hoeth", name = "Book of Hoeth", trigger = "melee_unwavering",
		badge = "zz_auto_badge_book_of_hoeth",
		keys = { "wh2_main_item_abilities_book_of_hoeth" },
		ox = 0, oy = 0 },
	{ marker = "book_of_secrets", name = "Book of Secrets", trigger = "enemy_engaged_or_shot",
		badge = "zz_auto_badge_book_of_secrets",
		keys = { "wh3_dlc24_item_abilities_book_of_secrets" },
		range_real = 100,
		ox = 0, oy = 0 },
	{ marker = "boom", name = "Boom!", trigger = "self_shooting",
		badge = "zz_auto_badge_boom",
		keys = { "wh_main_unit_abilities_boom" },
		ox = 0, oy = 0 },
	{ marker = "call_of_violence", name = "Call of Violence", trigger = "wavering_aura",
		badge = "zz_auto_badge_call_of_violence",
		keys = { "wh_dlc03_character_abilities_call_of_violence" },
		aura_real = 35,
		ox = 0, oy = 0 },
	{ marker = "cascading_fire_cloak", name = "Cascading Fire Cloak", trigger = "melee_unwavering",
		badge = "zz_auto_badge_cascading_fire_cloak",
		keys = { "wh3_main_spell_bound_cascading_fire_cloak" },
		ox = 0, oy = 0 },
	{ marker = "chalice_of_dark_rain", name = "Chalice of Dark Rain", trigger = "enemy_ground_area",
		badge = "zz_auto_badge_chalice_of_dark_rain",
		keys = { "wh_dlc03_item_abilities_chalice_of_dark_rain" },
		range_real = 200,
		ox = 0, oy = 0 },
	{ marker = "channelling_staff", name = "Channelling Staff", trigger = "melee_unwavering",
		badge = "zz_auto_badge_channelling_staff",
		keys = { "wh_main_item_abilities_channelling_staff" },
		ox = 0, oy = 0 },
	{ marker = "charmed_shield", name = "Charmed Shield", trigger = "melee_or_under_fire",
		badge = "zz_auto_badge_charmed_shield",
		keys = { "wh_main_weapon_abilities_charmed_shield" },
		ox = 0, oy = 0 },
	{ marker = "cold_blooded", name = "Cold-Blooded", trigger = "wavering_ally_range",
		badge = "zz_auto_badge_cold_blooded",
		keys = { "wh2_main_character_abilities_cold_blooded" },
		ally_range_real = 200,
		ox = 0, oy = 0 },
	{ marker = "crown_of_command", name = "Crown of Command", trigger = "wavering_ally_range",
		badge = "zz_auto_badge_crown_of_command",
		keys = { "wh_main_item_abilities_crown_of_command" },
		ally_range_real = 100,
		ox = 0, oy = 0 },
	{ marker = "cube_of_darkness", name = "Cube of Darkness", trigger = "enemy_engaged_or_shot",
		badge = "zz_auto_badge_cube_of_darkness",
		keys = { "wh2_main_item_abilities_cube_of_darkness" },
		range_real = 100,
		ox = 0, oy = 0 },
	{ marker = "curse_of_khsar", name = "Curse of Khsar", trigger = "enemy_ground_area",
		badge = "zz_auto_badge_curse_of_khsar",
		keys = { "wh2_dlc09_character_abilities_curse_of_khsar" },
		range_real = 35,
		ox = 0, oy = 0 },
	{ marker = "slezuzus_voice", name = "Daemonic Whispers", trigger = "ally_melee_buff",
		badge = "zz_auto_badge_slezuzus_voice",
		keys = { "wh3_dlc27_character_abilities_slezuzus_voice" },
		ally_range_real = 200,
		ox = 0, oy = 0 },
	{ marker = "dark_fortune", name = "Dark Fortune", trigger = "melee_unwavering",
		badge = "zz_auto_badge_dark_fortune",
		keys = { "wh_main_item_abilities_dark_fortune" },
		ox = 0, oy = 0 },
	{ marker = "deranged_munitions", name = "Deranged Munitions", trigger = "self_or_ally_shooting",
		badge = "zz_auto_badge_deranged_munitions",
		keys = { "wh3_dlc25_lord_abilities_deranged_munitions" },
		ally_range_real = 100,
		ox = 0, oy = 0 },
	{ marker = "deranged_munitions_upgraded", name = "Deranged Munitions Upgraded", trigger = "allies_firing_aura",
		badge = "zz_auto_badge_deranged_munitions_upgraded",
		keys = { "wh3_dlc25_lord_abilities_deranged_munitions_upgraded" },
		aura_real = 35,
		ox = 0, oy = 0 },
	{ marker = "dont_even_try_it", name = "Don't Even Try It", trigger = "enemy_engaged_or_shot",
		badge = "zz_auto_badge_dont_even_try_it",
		keys = { "wh2_dlc15_lord_abilities_dont_even_try_it" },
		range_real = 100,
		ox = 0, oy = 0 },
	{ marker = "doom_and_darkness_gunnery_school", name = "Doom & Darkness", trigger = "enemy_engaged_or_shot",
		badge = "zz_auto_badge_doom_and_darkness_gunnery_school",
		keys = { "wh3_dlc25_spell_Bound_doom_and_darkness_gunnery_school",
			"wh3_dlc27_spell_bound_runecaller_death_doom_and_darkness",
			"wh_dlc08_spell_bound_death_doom_and_darkness" },
		range_real = 200,
		ox = 0, oy = 0 },
	{ marker = "doom_lord", name = "Doom Lord", trigger = "wavering_ally_range",
		badge = "zz_auto_badge_doom_lord",
		keys = { "wh3_dlc29_lord_abilities_doom_lord" },
		ally_range_real = 200,
		ox = 0, oy = 0 },
	{ marker = "earthing_rod", name = "Earthing Rod", trigger = "melee_unwavering",
		badge = "zz_auto_badge_earthing_rod",
		keys = { "wh_main_item_abilities_earthing_rod" },
		ox = 0, oy = 0 },
	{ marker = "el_syf", name = "El Syf", trigger = "enemy_melee",
		badge = "zz_auto_badge_el_syf",
		keys = { "wh_dlc05_weapon_abilities_el_syf" },
		range_real = 200,
		target_class = "commander",
		ox = 0, oy = 0 },
	{ marker = "elixir_of_might", name = "Elixir of Might", trigger = "melee_unwavering",
		badge = "zz_auto_badge_elixir_of_might",
		keys = { "wh2_dlc09_item_abilities_elixir_of_might" },
		ox = 0, oy = 0 },
	{ marker = "embers_of_the_phoenix", name = "Embers of the Phoenix", trigger = "melee_or_shooting_aura",
		badge = "zz_auto_badge_embers_of_the_phoenix",
		keys = { "wh2_main_spell_bound_embers_of_the_phoenix" },
		aura_real = 35,
		ox = 0, oy = 0 },
	{ marker = "ballistic_enchantment", name = "Enchanted Ballistics", trigger = "allies_firing_aura",
		badge = "zz_auto_badge_ballistic_enchantment",
		keys = { "wh2_dlc11_character_abilities_ballistic_enchantment" },
		aura_real = 55,
		ox = 0, oy = 0 },
	{ marker = "enhanced_skavenbrew", name = "Enhanced Skavenbrew", trigger = "melee_unwavering",
		badge = "zz_auto_badge_enhanced_skavenbrew",
		keys = { "wh3_dlc29_item_abilities_enhanced_skavenbrew" },
		ox = 0, oy = 0 },
	{ marker = "entangle", name = "Entangle", trigger = "enemy_ground_area",
		badge = "zz_auto_badge_entangle",
		keys = { "wh2_dlc10_character_abilities_entangle" },
		range_real = 15,
		ox = 0, oy = 0 },
	{ marker = "entrenchment", name = "Entrenchment", trigger = "melee_or_self_or_ally_shooting",
		badge = "zz_auto_badge_entrenchment",
		keys = { "wh_main_unit_abilities_entrenchment" },
		ally_range_real = 150,
		ox = 0, oy = 0 },
	-- ROUND 130: the first two abilities on the firing flag (user ruling 2026-11-01).
	{ marker = "restock", name = "Restock!", trigger = "ally_ammo_low",
		badge = "zz_auto_badge_restock",
		keys = { "wh2_dlc17_hero_abilities_more_powder_generic" },
		ally_range_real = 100,
		ox = 0, oy = 0 },
	{ marker = "ballistics_calibration", name = "Ballistics Calibration", trigger = "allies_firing_aura",
		badge = "zz_auto_badge_ballistics_calibration",
		keys = { "wh_main_hero_abilities_ballistics_calibration" },
		aura_real = 55,
		ox = 0, oy = 0 },
	{ marker = "gaze_of_usirian", name = "Eternal Gaze", trigger = "enemy_engaged_or_shot",
		badge = "zz_auto_badge_gaze_of_usirian",
		keys = { "wh3_dlc29_lord_abilities_gaze_of_usirian" },
		range_real = 50,   -- patch 9.0.5: 100 -> 50 m
		ox = 0, oy = 0 },
	{ marker = "eternal_vigour", name = "Eternal Vigour", trigger = "melee_unwavering",
		badge = "zz_auto_badge_eternal_vigour",
		keys = { "wh3_dlc29_character_abilities_eternal_vigour" },
		ox = 0, oy = 0 },
	{ marker = "extra_ingredients", name = "Extra Ingredients", trigger = "melee_unwavering",
		badge = "zz_auto_badge_extra_ingredients",
		keys = { "wh3_main_character_abilities_extra_ingredients" },
		ox = 0, oy = 0 },
	{ marker = "favoured_by_the_matriarch", name = "Favoured by the Matriarch", trigger = "melee_unwavering",
		badge = "zz_auto_badge_favoured_by_the_matriarch",
		keys = { "wh3_dlc27_hero_abilities_favoured_by_the_matriarch" },
		ox = 0, oy = 0 },
	{ marker = "fear_of_aramar", name = "Fear of Aramar", trigger = "enemy_engaged_or_shot",
		badge = "zz_auto_badge_fear_of_aramar",
		keys = { "wh2_dlc10_item_abilities_fear_of_aramar" },
		range_real = 200,
		ox = 0, oy = 0 },
	{ marker = "fearsome_roar", name = "Fearsome Roar", trigger = "melee_unwavering",
		badge = "zz_auto_badge_fearsome_roar",
		keys = { "wh3_dlc24_unit_abilities_fearsome_roar" },
		ox = 0, oy = 0 },
	{ marker = "mark_of_the_monster", name = "Fecund Rebirth", trigger = "enemy_engaged_or_shot",
		badge = "zz_auto_badge_mark_of_the_monster",
		keys = { "wh3_dlc29_character_active_mark_of_the_monster" },
		range_real = 200,
		target_class = "large_single",
		ox = 0, oy = 0 },
	{ marker = "fermented_fungi", name = "Fermented Fungi", trigger = "enemy_melee",
		badge = "zz_auto_badge_fermented_fungi",
		keys = { "wh2_dlc15_lord_abilities_fermented_fungi" },
		range_real = 75,
		ox = 0, oy = 0 },
	{ marker = "fight_or_die", name = "Fight or Die!", trigger = "melee_unwavering",
		badge = "zz_auto_badge_fight_or_die",
		keys = { "wh_dlc08_lord_abilities_fight_or_die" },
		ox = 0, oy = 0 },
	{ marker = "fistful_of_laurels", name = "Fistful of Laurels", trigger = "melee_unwavering",
		badge = "zz_auto_badge_fistful_of_laurels",
		keys = { "wh3_main_item_abilities_fistful_of_laurels" },
		ox = 0, oy = 0 },
	{ marker = "flesh_to_stone", name = "Flesh to Stone", trigger = "melee_unwavering",
		badge = "zz_auto_badge_flesh_to_stone",
		keys = { "wh2_dlc16_spell_bound_flesh_to_stone" },
		ox = 0, oy = 0 },
	{ marker = "focus_instincts", name = "Focus Instincts", trigger = "melee_unwavering",
		badge = "zz_auto_badge_focus_instincts",
		keys = { "wh2_dlc12_lord_abilities_focus_instincts" },
		ox = 0, oy = 0 },
	{ marker = "forbidden_rod", name = "Forbidden Rod", trigger = "melee_unwavering",
		badge = "zz_auto_badge_forbidden_rod",
		keys = { "wh_main_item_abilities_forbidden_rod" },
		ox = 0, oy = 0 },
	{ marker = "frost_shard_glaive", name = "Frost Shard Glaive", trigger = "enemy_melee",
		badge = "zz_auto_badge_frost_shard_glaive",
		keys = { "wh3_main_weapon_abilities_frost_shard_glaive" },
		range_real = 50,
		ox = 0, oy = 0 },
	{ marker = "funnel_of_flame", name = "Funnel of Flame", trigger = "allies_firing_aura",
		badge = "zz_auto_badge_funnel_of_flame",
		keys = { "wh2_dlc13_lord_abilities_funnel_of_flame" },
		aura_real = 55,
		ox = 0, oy = 0 },
	{ marker = "gaze_of_fate", name = "Gaze of Fate", trigger = "enemy_fast_near_ally",
		badge = "zz_auto_badge_gaze_of_fate",
		keys = { "wh3_main_lord_abilities_gaze_of_fate" },
		range_real = 100,
		ox = 0, oy = 0 },
	{ marker = "get_em", name = "Get 'Em!", trigger = "enemy_ground_area",
		badge = "zz_auto_badge_get_em",
		keys = { "wh3_dlc25_character_abilities_get_em" },
		range_real = 35,
		ox = 0, oy = 0 },
	{ marker = "get_back_ere", name = "Get Back 'Ere!", trigger = "wavering_aura",
		badge = "zz_auto_badge_get_back_ere",
		keys = { "wh_main_character_abilities_get_back_ere" },
		aura_real = 35,
		ox = 0, oy = 0 },
	{ marker = "soulnetter", name = "Gilellion's Soulnetter", trigger = "enemy_engaged_or_shot",
		badge = "zz_auto_badge_soulnetter",
		keys = { "wh3_main_weapon_abilities_soulnetter" },
		range_real = 50,
		ox = 0, oy = 0 },
	{ marker = "glacial_defence", name = "Glacial Defence", trigger = "melee_or_under_fire",
		badge = "zz_auto_badge_glacial_defence",
		keys = { "wh3_twa08_unit_abilities_glacial_defence" },
		ox = 0, oy = 0 },
	{ marker = "glory_seeker", name = "Glory Seeker", trigger = "enemy_engaged_or_shot",
		badge = "zz_auto_badge_glory_seeker",
		keys = { "wh3_dlc29_hero_active_glory_seeker" },
		range_real = 100,
		target_class = "commander",
		ox = 0, oy = 0 },
	{ marker = "glory_seeker_upgraded", name = "Glory Seeker Upgraded", trigger = "enemy_engaged_or_shot",
		badge = "zz_auto_badge_glory_seeker_upgraded",
		keys = { "wh3_dlc29_hero_active_glory_seeker_upgraded" },
		range_real = 100,
		target_class = "commander",
		ox = 0, oy = 0 },
	{ marker = "gruts_sickle", name = "Grut's Sickle", trigger = "ally_winds",
		badge = "zz_auto_badge_gruts_sickle",
		keys = { "wh3_main_item_abilities_gruts_sickle" },
		ally_range_real = 100,
		ox = 0, oy = 0 },
	{ marker = "hagtree_fetish", name = "Hagtree Fetish", trigger = "melee_unwavering",
		badge = "zz_auto_badge_hagtree_fetish",
		keys = { "wh_dlc03_item_abilities_hagtree_fetish" },
		ox = 0, oy = 0 },
	{ marker = "hail_of_fire", name = "Hail of Fire", trigger = "allies_firing_aura",
		badge = "zz_auto_badge_hail_of_fire",
		keys = { "wh2_dlc13_lord_abilities_hail_of_fire" },
		aura_real = 55,
		ox = 0, oy = 0 },
	{ marker = "harmonic_convergence", name = "Harmonic Convergence", trigger = "melee_or_shooting_self_or_ally",
		badge = "zz_auto_badge_harmonic_convergence",
		keys = { "wh3_main_spell_bound_harmonic_convergence" },
		ally_range_real = 200,
		ox = 0, oy = 0 },
	{ marker = "headhunt", name = "Headhunt", trigger = "enemy_engaged_or_shot",
		badge = "zz_auto_badge_headhunt",
		keys = { "wh3_dlc26_character_abilities_headhunt" },
		range_real = 150,
		target_class = "commander",
		ox = 0, oy = 0 },
	{ marker = "hellish_vigour", name = "Hellish Vigour", trigger = "ally_melee_buff",
		badge = "zz_auto_badge_hellish_vigour",
		keys = { "wh3_dlc29_lord_abilities_hellish_vigour" },
		ally_range_real = 75,
		ox = 0, oy = 0 },
	{ marker = "hellish_vigour_upgraded", name = "Hellish Vigour Upgraded", trigger = "melee_unwavering",
		badge = "zz_auto_badge_hellish_vigour_upgraded",
		keys = { "wh3_dlc29_lord_abilities_hellish_vigour_upgraded" },
		ox = 0, oy = 0 },
	{ marker = "hidden_huntress", name = "Hidden Huntress", trigger = "enemy_melee",
		badge = "zz_auto_badge_hidden_huntress",
		keys = { "wh3_cp1_lord_abilities_hidden_huntress" },
		range_real = 75,
		ox = 0, oy = 0 },
	{ marker = "hidden_huntress_upgraded", name = "Hidden Huntress Upgraded", trigger = "enemy_melee",
		badge = "zz_auto_badge_hidden_huntress_upgraded",
		keys = { "wh3_cp1_lord_abilities_hidden_huntress_upgraded" },
		range_real = 75,
		ox = 0, oy = 0 },
	{ marker = "horn_of_the_wild_hunt", name = "Horn of the Wild Hunt", trigger = "melee_unwavering",
		badge = "zz_auto_badge_horn_of_the_wild_hunt",
		keys = { "wh_dlc05_item_abilities_horn_of_the_wild_hunt" },
		ox = 0, oy = 0 },
	{ marker = "horn_of_vaul", name = "Horn of Vaul", trigger = "melee_or_shooting_aura",
		badge = "zz_auto_badge_horn_of_vaul",
		keys = { "wh2_main_item_abilities_dragonhorn" },
		aura_real = 35,
		ox = 0, oy = 0 },
	{ marker = "hornswaggle", name = "Hornswaggle", trigger = "enemy_melee",
		badge = "zz_auto_badge_hornswaggle",
		keys = { "wh2_dlc11_character_abilities_hornswaggle" },
		range_real = 100,
		ox = 0, oy = 0 },
	{ marker = "howl_of_the_great_beast", name = "Howl of the Great Beast", trigger = "melee_unwavering",
		badge = "zz_auto_badge_howl_of_the_great_beast",
		keys = { "wh3_dlc24_unit_abilities_howl_of_the_great_beast" },
		ox = 0, oy = 0 },
	{ marker = "hunter_of_champions", name = "Hunter of Champions", trigger = "enemy_engaged_or_shot",
		badge = "zz_auto_badge_hunter_of_champions",
		keys = { "wh_dlc08_character_abilities_hunter_of_champions",
			-- ROUND 123: the UPGRADED twin (same 100 m range, same armour /
			-- melee-defence hex) shares this marker, badge and trigger.
			"wh2_dlc17_character_abilities_hunter_of_champions_upgraded" },
		range_real = 100,
		target_class = "commander",
		ox = 0, oy = 0 },
	{ marker = "hunters_snare", name = "Hunter's Snare", trigger = "enemy_ground_area",
		badge = "zz_auto_badge_hunters_snare",
		keys = { "wh2_dlc13_lord_abilities_hunters_snare" },
		range_real = 35,
		ox = 0, oy = 0 },
	{ marker = "hunters_trap", name = "Hunter's Trap", trigger = "enemy_ground_area",
		badge = "zz_auto_badge_hunters_trap",
		keys = { "wh2_dlc13_lord_abilities_hunters_trap" },
		range_real = 35,
		ox = 0, oy = 0 },
	{ marker = "spell_slaanesh_hysterical_frenzy_bound", name = "Hysterical Frenzy", trigger = "melee_unwavering",
		badge = "zz_auto_badge_spell_slaanesh_hysterical_frenzy_bound",
		keys = { "wh3_main_spell_slaanesh_hysterical_frenzy_bound" },
		ox = 0, oy = 0 },
	{ marker = "inspired_marksmanship_i", name = "Inspired Marksmanship I", trigger = "ally_missile",
		badge = "zz_auto_badge_inspired_marksmanship_i",
		keys = { "wh3_main_lord_abilities_inspired_marksmanship_i" },
		ally_range_real = 100,
		ox = 0, oy = 0 },
	{ marker = "inspired_marksmanship_ii", name = "Inspired Marksmanship II", trigger = "ally_missile",
		badge = "zz_auto_badge_inspired_marksmanship_ii",
		keys = { "wh3_main_lord_abilities_inspired_marksmanship_ii" },
		ally_range_real = 100,
		ox = 0, oy = 0 },
	{ marker = "inspired_marksmanship_iii", name = "Inspired Marksmanship III", trigger = "ally_missile",
		badge = "zz_auto_badge_inspired_marksmanship_iii",
		keys = { "wh3_main_lord_abilities_inspired_marksmanship_iii" },
		ally_range_real = 100,
		ox = 0, oy = 0 },
	{ marker = "iron_hand_captain", name = "Iron-Handed Captain", trigger = "ally_broken",
		badge = "zz_auto_badge_iron_hand_captain",
		keys = { "wh3_dlc27_character_abilities_iron_hand_captain" },
		ally_range_real = 200,
		ox = 0, oy = 0 },
	{ marker = "jagged_dagger", name = "Jagged Dagger", trigger = "melee_unwavering",
		badge = "zz_auto_badge_jagged_dagger",
		keys = { "wh_dlc03_item_abilities_jagged_dagger" },
		ox = 0, oy = 0 },
	{ marker = "locus_of_abjuration", name = "Locus of Abjuration", trigger = "melee_unwavering",
		badge = "zz_auto_badge_locus_of_abjuration",
		keys = { "wh3_main_character_abilities_locus_of_abjuration" },
		ox = 0, oy = 0 },
	{ marker = "locus_of_change", name = "Locus of Change", trigger = "allies_firing_aura",
		badge = "zz_auto_badge_locus_of_change",
		keys = { "wh3_main_character_abilities_locus_of_change" },
		aura_real = 55,
		ox = 0, oy = 0 },
	{ marker = "locus_of_conjuration", name = "Locus of Conjuration", trigger = "melee_unwavering",
		badge = "zz_auto_badge_locus_of_conjuration",
		keys = { "wh3_main_character_abilities_locus_of_conjuration" },
		ox = 0, oy = 0 },
	{ marker = "looming_dread", name = "Looming Dread", trigger = "enemy_engaged_or_shot",
		badge = "zz_auto_badge_looming_dread",
		keys = { "wh2_dlc14_lord_abilities_looming_dread" },
		range_real = 150,
		target_class = "commander",
		ox = 0, oy = 0 },
	{ marker = "lord_of_dragons", name = "Lord of Dragons", trigger = "enemy_melee",
		badge = "zz_auto_badge_lord_of_dragons",
		keys = { "wh2_dlc15_lord_abilities_lord_of_dragons" },
		range_real = 75,
		ox = 0, oy = 0 },
	{ marker = "magical_animus", name = "Magical Animus", trigger = "wavering_aura",
		badge = "zz_auto_badge_magical_animus",
		keys = { "wh_main_character_abilities_magical_animus" },
		aura_real = 35,
		ox = 0, oy = 0 },
	{ marker = "mark_of_the_plague_fleet", name = "Mark of the Plague Fleet", trigger = "enemy_engaged_or_shot",
		badge = "zz_auto_badge_mark_of_the_plague_fleet",
		keys = { "wh3_dlc29_item_active_mark_of_the_plague_fleet" },
		range_real = 75,
		ox = 0, oy = 0 },
	{ marker = "mark_of_yin", name = "Mark of Yin", trigger = "enemy_engaged_or_shot",
		badge = "zz_auto_badge_mark_of_yin",
		keys = { "wh3_dlc24_unit_abilities_mark_of_yin" },
		range_real = 180,
		ox = 0, oy = 0 },
	{ marker = "marked_by_ulthar", name = "Marked by Ulthar", trigger = "enemy_engaged_or_shot",
		badge = "zz_auto_badge_marked_by_ulthar",
		keys = { "wh_dlc06_unit_abilities_marked_by_ulthar" },
		range_real = 150,
		ox = 0, oy = 0 },
	{ marker = "marked_for_eatin", name = "Marked for Eatin'", trigger = "enemy_melee",
		badge = "zz_auto_badge_marked_for_eatin",
		keys = { "wh3_dlc26_unit_abilities_marked_for_eatin" },
		range_real = 75,
		ox = 0, oy = 0 },
	{ marker = "beguile", name = "Master of Beguilement", trigger = "enemy_melee",
		badge = "zz_auto_badge_beguile",
		keys = { "wh_dlc04_lord_abilities_beguile" },
		range_real = 100,
		ox = 0, oy = 0 },
	{ marker = "master_of_the_black_arts", name = "Master of the Black Arts", trigger = "melee_unwavering",
		badge = "zz_auto_badge_master_of_the_black_arts",
		keys = { "wh_main_lord_abilities_master_of_the_black_arts" },
		ox = 0, oy = 0 },
	{ marker = "master_rune_of_breaking", name = "Master Rune of Breaking", trigger = "melee_unwavering",
		badge = "zz_auto_badge_master_rune_of_breaking",
		keys = { "wh2_dlc17_rune_abilities_master_rune_of_breaking" },
		ox = 0, oy = 0 },
	{ marker = "master_rune_of_negation", name = "Master Rune of Negation", trigger = "melee_unwavering",
		badge = "zz_auto_badge_master_rune_of_negation",
		keys = { "wh_dlc06_rune_abilities_master_rune_of_negation" },
		ox = 0, oy = 0 },
	{ marker = "master_rune_of_slowness", name = "Master Rune of Slowness", trigger = "enemy_fast_near_ally",
		badge = "zz_auto_badge_master_rune_of_slowness",
		keys = { "wh2_dlc17_rune_abilities_master_rune_of_slowness" },
		range_real = 100,
		ox = 0, oy = 0 },
	{ marker = "maw_shard", name = "Maw Shard", trigger = "melee_unwavering",
		badge = "zz_auto_badge_maw_shard",
		keys = { "wh3_main_item_abilities_maw_shard" },
		ox = 0, oy = 0 },
	{ marker = "miasma_of_despair", name = "Miasma of Despair", trigger = "melee_unwavering",
		badge = "zz_auto_badge_miasma_of_despair",
		keys = { "wh2_dlc13_lord_abilities_miasma_of_despair" },
		ox = 0, oy = 0 },
	{ marker = "mighty_oath_stone", name = "Mighty Oath Stone", trigger = "melee_unwavering",
		badge = "zz_auto_badge_mighty_oath_stone",
		keys = { "wh_dlc06_lord_abilities_mighty_oath_stone" },
		ox = 0, oy = 0 },
	{ marker = "mighty_roar", name = "Mighty Roar", trigger = "melee_unwavering",
		badge = "zz_auto_badge_mighty_roar",
		keys = { "wh2_dlc15_unit_abilities_mighty_roar" },
		ox = 0, oy = 0 },
	{ marker = "mimic_cold_blooded", name = "Mirror (Cold-Blooded)", trigger = "wavering_aura",
		badge = "zz_auto_badge_mimic_cold_blooded",
		keys = { "wh2_dlc15_unit_abilities_mimic_cold_blooded" },
		ox = 0, oy = 0 },
	{ marker = "mimic_feint_and_riposte", name = "Mirror (Feint & Riposte)", trigger = "melee_unwavering",
		badge = "zz_auto_badge_mimic_feint_and_riposte",
		keys = { "wh2_dlc15_unit_abilities_mimic_feint_and_riposte" },
		ox = 0, oy = 0 },
	{ marker = "mimic_grand_hammer_of_faith", name = "Mirror (Grand Hammer of Faith)", trigger = "melee_unwavering",
		badge = "zz_auto_badge_mimic_grand_hammer_of_faith",
		keys = { "wh2_dlc15_unit_abilities_mimic_grand_hammer_of_faith" },
		ox = 0, oy = 0 },
	{ marker = "unit_bound_missile_mirror", name = "Missile Mirror", trigger = "enemy_engaged_or_shot",
		badge = "zz_auto_badge_unit_bound_missile_mirror",
		keys = { "wh3_dlc24_unit_bound_missile_mirror" },
		range_real = 200,
		ox = 0, oy = 0 },
	{ marker = "mither", name = "Mither", trigger = "enemy_fast_near_ally",
		badge = "zz_auto_badge_mither",
		keys = { "wh2_dlc15_hero_abilities_mither" },
		range_real = 75,
		ox = 0, oy = 0 },
	{ marker = "moonshine", name = "Moonshine", trigger = "melee_unwavering",
		badge = "zz_auto_badge_moonshine",
		keys = { "wh2_dlc11_item_abilities_moonshine" },
		ox = 0, oy = 0 },
	{ marker = "morgrims_eye", name = "Morgrim's Eye", trigger = "allies_firing_aura",
		badge = "zz_auto_badge_morgrims_eye",
		keys = { "wh3_dlc23_item_abilities_morgrims_eye" },
		aura_real = 35,
		ox = 0, oy = 0 },
	{ marker = "muster_of_malevolents", name = "Muster of Malevolents", trigger = "enemy_engaged_or_shot",
		badge = "zz_auto_badge_muster_of_malevolents",
		keys = { "wh2_dlc16_character_abilities_muster_of_malevolents" },
		range_real = 75,
		ox = 0, oy = 0 },
	{ marker = "neferras_scrolls_of_mighty_incantations", name = "Neferra's Scrolls of Mighty Incantations", trigger = "melee_unwavering",
		badge = "zz_auto_badge_neferras_scrolls_of_mighty_incantations",
		keys = { "wh2_dlc09_item_abilities_neferras_scrolls_of_mighty_incantations" },
		ox = 0, oy = 0 },
	{ marker = "net_dem_up", name = "Net Dem Up!", trigger = "enemy_engaged_or_shot",
		badge = "zz_auto_badge_net_dem_up",
		keys = { "wh3_dlc26_unit_abilities_net_dem_up" },
		range_real = 75,
		ox = 0, oy = 0 },
	{ marker = "net_of_amyntok", name = "Net of Amyntok", trigger = "enemy_engaged_or_shot",
		badge = "zz_auto_badge_net_of_amyntok",
		keys = { "wh_dlc04_spell_bound_net_of_amyntok" },
		range_real = 100,
		ox = 0, oy = 0 },
	{ marker = "null_stone", name = "Null Stone", trigger = "melee_unwavering",
		badge = "zz_auto_badge_null_stone",
		keys = { "wh3_dlc27_item_abilities_null_stone" },
		ox = 0, oy = 0 },
	{ marker = "oath_of_vengeance", name = "Oath of Vengeance", trigger = "enemy_melee",
		badge = "zz_auto_badge_oath_of_vengeance",
		keys = { "wh2_dlc10_lord_abilities_oath_of_vengeance" },
		range_real = 200,
		ox = 0, oy = 0 },
	{ marker = "oil_flask", name = "Oil Flask", trigger = "enemy_engaged_or_shot",
		badge = "zz_auto_badge_oil_flask",
		keys = { "wh2_dlc13_lord_abilities_oil_flask" },
		range_real = 70,
		ox = 0, oy = 0 },
	{ marker = "ottos_scythe", name = "Otto's Scythe", trigger = "enemy_melee",
		badge = "zz_auto_badge_ottos_scythe",
		keys = { "wh3_dlc29_item_active_ottos_scythe" },
		range_real = 100,
		ox = 0, oy = 0 },
	{ marker = "pack_trap", name = "Pack Trap", trigger = "enemy_engaged_or_shot",
		badge = "zz_auto_badge_pack_trap",
		keys = { "wh3_dlc24_unit_abilities_pack_trap" },
		range_real = 100,
		ox = 0, oy = 0 },
	{ marker = "pageant_of_shrikes", name = "Pageant of Shrikes", trigger = "enemy_engaged_or_shot",
		badge = "zz_auto_badge_pageant_of_shrikes",
		keys = { "wh2_dlc16_character_abilities_pageant_of_shrikes" },
		range_real = 75,
		ox = 0, oy = 0 },
	{ marker = "pearl_of_infinite_bleakness", name = "Pearl of Infinite Bleakness", trigger = "wavering_aura",
		badge = "zz_auto_badge_pearl_of_infinite_bleakness",
		keys = { "wh2_main_item_abilities_pearl_of_infinite_bleakness" },
		aura_real = 35,
		ox = 0, oy = 0 },
	{ marker = "pestilent_potions", name = "Pestilent Potions", trigger = "enemy_melee",
		badge = "zz_auto_badge_pestilent_potions",
		keys = { "wh3_dlc20_item_abilities_pestilent_potions" },
		range_real = 100,
		ox = 0, oy = 0 },
	{ marker = "phas_protection", name = "Pha's Protection", trigger = "melee_unwavering",
		badge = "zz_auto_badge_phas_protection",
		keys = { "wh3_main_spell_bound_phas_protection" },
		ox = 0, oy = 0 },
	{ marker = "pilgrimage_of_skulls", name = "Pilgrimage of Skulls", trigger = "wavering_ally_range",
		badge = "zz_auto_badge_pilgrimage_of_skulls",
		keys = { "wh3_dlc26_lord_abilities_pilgrimage_of_skulls" },
		ally_range_real = 100,
		ox = 0, oy = 0 },
	{ marker = "plague_of_rust", name = "Plague of Rust", trigger = "enemy_engaged_or_shot",
		badge = "zz_auto_badge_plague_of_rust",
		keys = { "wh3_main_spell_bound_plague_of_rust" },
		range_real = 200,
		ox = 0, oy = 0 },
	{ marker = "plaque_of_dominion", name = "Plaque of Dominion", trigger = "melee_unwavering",
		badge = "zz_auto_badge_plaque_of_dominion",
		keys = { "wh2_main_item_abilities_plaque_of_dominion" },
		ox = 0, oy = 0 },
	{ marker = "potion_of_farsight", name = "Potion of Farsight", trigger = "no_enemy_in_range_within_boost",
		badge = "zz_auto_badge_potion_of_farsight",
		keys = { "wh3_main_item_abilities_potion_of_farsight" },
		ox = 0, oy = 0 },
	{ marker = "potion_of_foolhardiness", name = "Potion of Foolhardiness", trigger = "melee_unwavering",
		badge = "zz_auto_badge_potion_of_foolhardiness",
		keys = { "wh_main_item_abilities_potion_of_foolhardiness" },
		ox = 0, oy = 0 },
	{ marker = "potion_of_speed", name = "Potion of Speed", trigger = "charge_only",
		badge = "zz_auto_badge_potion_of_speed",
		keys = { "wh_main_item_abilities_potion_of_speed" },
		ox = 0, oy = 0 },
	{ marker = "power_familiar", name = "Power Familiar", trigger = "melee_unwavering",
		badge = "zz_auto_badge_power_familiar",
		keys = { "wh3_dlc27_item_abilities_power_familiar" },
		ox = 0, oy = 0 },
	{ marker = "power_siphon", name = "Power Siphon", trigger = "enemy_engaged_or_shot",
		badge = "zz_auto_badge_power_siphon",
		keys = { "wh2_dlc11_lord_abilities_power_siphon" },
		range_real = 100,
		ox = 0, oy = 0 },
	{ marker = "power_stone", name = "Power Stone", trigger = "melee_unwavering",
		badge = "zz_auto_badge_power_stone",
		keys = { "wh_main_item_abilities_power_stone" },
		ox = 0, oy = 0 },
	{ marker = "predatory_instincts", name = "Predatory Instincts", trigger = "melee_unwavering",
		badge = "zz_auto_badge_predatory_instincts",
		keys = { "wh3_cp1_lord_abilities_predatory_instincts" },
		ox = 0, oy = 0 },
	{ marker = "prey_of_anath_raema", name = "Prey of Anath Raema", trigger = "enemy_engaged_or_shot",
		badge = "zz_auto_badge_prey_of_anath_raema",
		keys = { "wh_dlc05_character_abilities_prey_of_anath_raema" },
		range_real = 100,
		ox = 0, oy = 0 },
	{ marker = "prey_of_the_blood_god", name = "Prey of the Blood God", trigger = "enemy_engaged_or_shot",
		badge = "zz_auto_badge_prey_of_the_blood_god",
		keys = { "wh3_pro12_hero_abilities_prey_of_the_blood_god" },
		range_real = 100,
		target_class = "commander",
		ox = 0, oy = 0 },
	{ marker = "prismatic_amplifier", name = "Prismatic Amplifier", trigger = "melee_unwavering",
		badge = "zz_auto_badge_prismatic_amplifier",
		keys = { "wh3_main_item_abilities_prismatic_amplifier" },
		ox = 0, oy = 0 },
	{ marker = "rally", name = "Rally!", trigger = "wavering_aura",
		badge = "zz_auto_badge_rally",
		keys = { "wh_main_character_abilities_rally" },
		aura_real = 35,
		ox = 0, oy = 0 },
	{ marker = "dispatch_the_swarm_attack", name = "Ravaging Swarm", trigger = "enemy_melee",
		badge = "zz_auto_badge_dispatch_the_swarm_attack",
		keys = { "wh3_dlc29_hero_active_dispatch_the_swarm_attack" },
		range_real = 30,
		ox = 0, oy = 0 },
	{ marker = "dispatch_the_swarm_attack_upgraded", name = "Ravaging Swarm Upgraded", trigger = "enemy_melee",
		badge = "zz_auto_badge_dispatch_the_swarm_attack_upgraded",
		keys = { "wh3_dlc29_hero_active_dispatch_the_swarm_attack_upgraded" },
		range_real = 30,
		ox = 0, oy = 0 },
	{ marker = "tomb_king_rally", name = "Reanimate", trigger = "wavering_aura",
		badge = "zz_auto_badge_tomb_king_rally",
		keys = { "wh2_dlc09_character_abilities_tomb_king_rally" },
		aura_real = 35,
		ox = 0, oy = 0 },
	{ marker = "tomb_king_rally_upgraded", name = "Reanimate Upgraded", trigger = "wavering_aura",
		badge = "zz_auto_badge_tomb_king_rally_upgraded",
		keys = { "wh2_dlc09_character_abilities_tomb_king_rally_upgraded" },
		aura_real = 35,
		ox = 0, oy = 0 },
	{ marker = "red_fury", name = "Red Fury", trigger = "melee_unwavering",
		badge = "zz_auto_badge_red_fury",
		keys = { "wh_main_character_abilities_red_fury" },
		ox = 0, oy = 0 },
	{ marker = "item_passive_rock_eye", name = "Rock Eye", trigger = "melee_unwavering",
		badge = "zz_auto_badge_item_passive_rock_eye",
		keys = { "wh3_main_item_passive_rock_eye" },
		ox = 0, oy = 0 },
	{ marker = "rune_of_breaking", name = "Rune of Breaking", trigger = "melee_unwavering",
		badge = "zz_auto_badge_rune_of_breaking",
		keys = { "wh2_dlc17_rune_abilities_rune_of_breaking" },
		ox = 0, oy = 0 },
	{ marker = "rune_of_negation", name = "Rune of Negation", trigger = "melee_unwavering",
		badge = "zz_auto_badge_rune_of_negation",
		keys = { "wh_main_rune_abilities_rune_of_negation" },
		ox = 0, oy = 0 },
	{ marker = "rune_of_slowness", name = "Rune of Slowness", trigger = "enemy_fast_near_ally",
		badge = "zz_auto_badge_rune_of_slowness",
		keys = { "wh2_dlc17_rune_abilities_rune_of_slowness" },
		range_real = 100,
		ox = 0, oy = 0 },
	{ marker = "rune_of_thungni", name = "Rune of Thungni", trigger = "melee_unwavering",
		badge = "zz_auto_badge_rune_of_thungni",
		keys = { "wh3_dlc23_item_abilities_rune_of_thungni" },
		ox = 0, oy = 0 },
	{ marker = "sadistic_snare", name = "Sadistic Snare", trigger = "enemy_fast_near_ally",
		badge = "zz_auto_badge_sadistic_snare",
		keys = { "wh3_dlc23_lord_abilities_sadistic_snare" },
		range_real = 20,
		ox = 0, oy = 0 },
	{ marker = "sceptre_of_stability", name = "Sceptre of Stability", trigger = "melee_unwavering",
		badge = "zz_auto_badge_sceptre_of_stability",
		keys = { "wh_main_item_abilities_sceptre_of_stability" },
		ox = 0, oy = 0 },
	{ marker = "scroll_of_destiny", name = "Scroll of Destiny", trigger = "melee_unwavering",
		badge = "zz_auto_badge_scroll_of_destiny",
		keys = { "wh3_main_item_abilities_scroll_of_destiny" },
		ox = 0, oy = 0 },
	{ marker = "scroll_of_leeching", name = "Scroll of Leeching", trigger = "enemy_engaged_or_shot",
		badge = "zz_auto_badge_scroll_of_leeching",
		keys = { "wh_main_item_abilities_scroll_of_leeching" },
		range_real = 100,
		ox = 0, oy = 0 },
	{ marker = "scroll_of_shielding", name = "Scroll of Shielding", trigger = "melee_unwavering",
		badge = "zz_auto_badge_scroll_of_shielding",
		keys = { "wh_main_item_abilities_scroll_of_shielding" },
		ox = 0, oy = 0 },
	{ marker = "shield_of_chaqua", name = "Shield of Chaqua", trigger = "under_fire",
		badge = "zz_auto_badge_shield_of_chaqua",
		keys = { "wh2_dlc12_unit_abilities_shield_of_chaqua" },
		aura_real = 55,
		ox = 0, oy = 0 },
	{ marker = "dispatch_the_swarm_protect", name = "Shielding Swarm", trigger = "melee_unwavering",
		badge = "zz_auto_badge_dispatch_the_swarm_protect",
		keys = { "wh3_dlc29_hero_active_dispatch_the_swarm_protect" },
		ox = 0, oy = 0 },
	{ marker = "dispatch_the_swarm_protect_upgraded", name = "Shielding Swarm Upgraded", trigger = "melee_unwavering",
		badge = "zz_auto_badge_dispatch_the_swarm_protect_upgraded",
		keys = { "wh3_dlc29_hero_active_dispatch_the_swarm_protect_upgraded" },
		ox = 0, oy = 0 },
	{ marker = "shock_collar", name = "Shock Collar", trigger = "ally_wavering",
		badge = "zz_auto_badge_shock_collar",
		keys = { "wh2_dlc16_hero_abilities_shock_collar" },
		ally_range_real = 100,
		ox = 0, oy = 0 },
	{ marker = "silence_the_prey", name = "Silence the Prey", trigger = "enemy_engaged_or_shot",
		badge = "zz_auto_badge_silence_the_prey",
		keys = { "wh3_main_character_abilities_silence_the_prey" },
		range_real = 100,
		ox = 0, oy = 0 },
	{ marker = "skavenbrew", name = "Skavenbrew", trigger = "melee_unwavering",
		badge = "zz_auto_badge_skavenbrew",
		keys = { "wh2_main_item_abilities_skavenbrew" },
		ox = 0, oy = 0 },
	{ marker = "skjalandirs_fall", name = "Skjalandir's Fall", trigger = "melee_or_shooting_into_melee",
		badge = "zz_auto_badge_skjalandirs_fall",
		keys = { "wh3_dlc23_character_abilities_skjalandirs_fall" },
		ox = 0, oy = 0 },
	{ marker = "skull_of_rarkos", name = "Skull of Rarkos", trigger = "melee_unwavering",
		badge = "zz_auto_badge_skull_of_rarkos",
		keys = { "wh_dlc03_item_abilities_skull_of_rarkos" },
		ox = 0, oy = 0 },
	{ marker = "snowflake_pendant", name = "Snowflake Pendant", trigger = "melee_unwavering",
		badge = "zz_auto_badge_snowflake_pendant",
		keys = { "wh3_main_item_abilities_snowflake_pendant" },
		ox = 0, oy = 0 },
	{ marker = "spearfishers_net", name = "Spearfisher's Net", trigger = "enemy_fast_near_ally",
		badge = "zz_auto_badge_spearfishers_net",
		keys = { "wh2_dlc11_lord_abilities_spearfishers_net" },
		range_real = 100,
		target_class = "not_flying",
		ox = 0, oy = 0 },
	{ marker = "spell_wrought_sceptre", name = "Spell-Wrought Sceptre", trigger = "melee_unwavering",
		badge = "zz_auto_badge_spell_wrought_sceptre",
		keys = { "wh3_dlc23_weapon_abilities_spell_wrought_sceptre" },
		ox = 0, oy = 0 },
	{ marker = "spider_web_attack", name = "Spiderweb Attack", trigger = "enemy_engaged_or_shot",
		badge = "zz_auto_badge_spider_web_attack",
		keys = { "wh3_dlc26_character_abilities_spider_web_attack" },
		range_real = 50,
		ox = 0, oy = 0 },
	{ marker = "staff_of_damnation", name = "Staff of Damnation", trigger = "melee_unwavering",
		badge = "zz_auto_badge_staff_of_damnation",
		keys = { "wh_main_spell_bound_staff_of_damnation" },
		ox = 0, oy = 0 },
	{ marker = "staff_of_nagash", name = "Staff of Nagash", trigger = "melee_unwavering",
		badge = "zz_auto_badge_staff_of_nagash",
		keys = { "wh2_dlc09_item_abilities_staff_of_nagash" },
		ox = 0, oy = 0 },
	{ marker = "staff_of_tomorrow", name = "Staff of Tomorrow", trigger = "melee_unwavering",
		badge = "zz_auto_badge_staff_of_tomorrow",
		keys = { "wh3_main_weapon_abilities_staff_of_tomorrow" },
		ox = 0, oy = 0 },
	{ marker = "staff_of_volans", name = "Staff of Volans", trigger = "melee_unwavering",
		badge = "zz_auto_badge_staff_of_volans",
		keys = { "wh_main_item_abilities_staff_of_volans" },
		ox = 0, oy = 0 },
	{ marker = "staff_of_wu_xing", name = "Staff of Wu Xing", trigger = "melee_unwavering",
		badge = "zz_auto_badge_staff_of_wu_xing",
		keys = { "wh3_main_item_abilities_staff_of_wu_xing" },
		ox = 0, oy = 0 },
	{ marker = "starwood_staff", name = "Starwood Staff", trigger = "melee_unwavering",
		badge = "zz_auto_badge_starwood_staff",
		keys = { "wh2_main_item_abilities_starwood_staff" },
		ox = 0, oy = 0 },
	{ marker = "stave_of_avelorn", name = "Stave of Avelorn", trigger = "melee_unwavering",
		badge = "zz_auto_badge_stave_of_avelorn",
		keys = { "wh2_dlc10_item_abilities_stave_of_avelorn" },
		ox = 0, oy = 0 },
	{ marker = "sword_of_filth", name = "Sword of Filth", trigger = "enemy_engaged_or_shot",
		badge = "zz_auto_badge_sword_of_filth",
		keys = { "wh3_dlc25_weapon_abilities_sword_of_filth" },
		range_real = 35,
		ox = 0, oy = 0 },
	{ marker = "tacticians_rally", name = "Tacticians, Rally!", trigger = "wavering_ally_range",
		badge = "zz_auto_badge_tacticians_rally",
		keys = { "wh3_dlc24_character_abilities_tacticians_rally" },
		ally_range_real = 100,
		ox = 0, oy = 0 },
	{ marker = "taunt", name = "Taunt", trigger = "enemy_melee",
		badge = "zz_auto_badge_taunt",
		keys = { "wh2_dlc11_character_abilities_taunt" },
		range_real = 100,
		ox = 0, oy = 0 },
	{ marker = "tendrils_of_the_sea", name = "Tendrils of the Sea", trigger = "enemy_melee",
		badge = "zz_auto_badge_tendrils_of_the_sea",
		keys = { "wh3_dlc29_hero_active_tendrils_of_the_sea" },
		range_real = 200,
		target_class = "large",
		ox = 0, oy = 0 },
	{ marker = "terrorgheist_skull", name = "Terrorgheist Skull", trigger = "melee_unwavering",
		badge = "zz_auto_badge_terrorgheist_skull",
		keys = { "wh_dlc08_item_abilities_terrorgheist_skull" },
		ox = 0, oy = 0 },
	{ marker = "averland_runefang", name = "The Averland Runefang", trigger = "enemy_melee",
		badge = "zz_auto_badge_averland_runefang",
		keys = { "wh2_dlc13_weapon_abilities_averland_runefang" },
		range_real = 100,
		ox = 0, oy = 0 },
	{ marker = "the_bane_shield", name = "The Bane Shield", trigger = "melee_or_under_fire",
		badge = "zz_auto_badge_the_bane_shield",
		keys = { "wh2_main_item_abilities_the_bane_shield" },
		aura_real = 35,
		ox = 0, oy = 0 },
	{ marker = "the_black_tongue", name = "The Black Tongue", trigger = "enemy_engaged_or_shot",
		badge = "zz_auto_badge_the_black_tongue",
		keys = { "wh3_dlc27_character_abilities_the_black_tongue" },
		range_real = 200,
		ox = 0, oy = 0 },
	{ marker = "the_chromatic_tome", name = "The Chromatic Tome", trigger = "melee_unwavering",
		badge = "zz_auto_badge_the_chromatic_tome",
		keys = { "wh3_main_item_abilities_the_chromatic_tome" },
		ox = 0, oy = 0 },
	{ marker = "the_dark_master", name = "The Dark Master", trigger = "enemy_melee",
		badge = "zz_auto_badge_the_dark_master",
		keys = { "wh3_main_lord_abilities_the_dark_master" },
		range_real = 100,
		ox = 0, oy = 0 },
	{ marker = "enfeebling_foe", name = "The Enfeebling Foe", trigger = "enemy_melee",
		badge = "zz_auto_badge_enfeebling_foe",
		keys = { "wh3_dlc23_spell_bound_enfeebling_foe",
			"wh3_dlc27_spell_bound_enfeebling_foe",
			"wh3_main_spell_bound_enfeebling_foe",
			"wh3_twa08_spell_bound_enfeebling_foe_keeper_of_secrets_ror" },
		range_real = 200,
		ox = 0, oy = 0 },
	{ marker = "the_golden_eye_of_tzeentch", name = "The Golden Eye of Tzeentch", trigger = "under_fire",
		badge = "zz_auto_badge_the_golden_eye_of_tzeentch",
		keys = { "wh3_dlc24_item_abilities_the_golden_eye_of_tzeentch" },
		ox = 0, oy = 0 },
	{ marker = "the_guiding_eye", name = "The Guiding Eye", trigger = "allies_firing_aura",
		badge = "zz_auto_badge_the_guiding_eye",
		keys = { "wh2_main_item_abilities_the_guiding_eye" },
		aura_real = 55,
		ox = 0, oy = 0 },
	{ marker = "the_hammer_of_karak_drazh", name = "The Hammer of Karak Drazh", trigger = "enemy_melee",
		badge = "zz_auto_badge_the_hammer_of_karak_drazh",
		keys = { "wh_main_weapon_abilities_the_hammer_of_karak_drazh" },
		range_real = 50,
		ox = 0, oy = 0 },
	{ marker = "undeath_sulekhim_hand_of_dust", name = "The Hand of Dust", trigger = "melee_unwavering",
		badge = "zz_auto_badge_undeath_sulekhim_hand_of_dust",
		keys = { "wh3_dlc29_spell_bound_undeath_sulekhim_hand_of_dust" },
		ox = 0, oy = 0 },
	{ marker = "the_liber_noctus", name = "The Liber Noctus", trigger = "melee_unwavering",
		badge = "zz_auto_badge_the_liber_noctus",
		keys = { "wh_dlc04_item_abilities_the_liber_noctus" },
		ox = 0, oy = 0 },
	{ marker = "lions_shield", name = "The Lion's Shield", trigger = "under_fire",
		badge = "zz_auto_badge_lions_shield",
		keys = { "wh_dlc07_lord_abilities_lions_shield" },
		ox = 0, oy = 0 },
	{ marker = "the_seerstaff_of_saphery", name = "The Seerstaff of Saphery", trigger = "melee_or_shooting_self_or_ally",
		badge = "zz_auto_badge_the_seerstaff_of_saphery",
		keys = { "wh2_main_spell_bound_the_seerstaff_of_saphery" },
		ally_range_real = 200,
		ox = 0, oy = 0 },
	{ marker = "the_tricksters_pendant", name = "The Trickster's Pendant", trigger = "enemy_ground_area",
		badge = "zz_auto_badge_the_tricksters_pendant",
		keys = { "wh2_main_item_abilities_the_tricksters_pendant" },
		range_real = 100,
		ox = 0, oy = 0 },
	{ marker = "the_vial_of_hashut", name = "The Vial of Hashut", trigger = "enemy_engaged_or_shot",
		badge = "zz_auto_badge_the_vial_of_hashut",
		keys = { "wh3_dlc23_item_abilities_the_vial_of_hashut" },
		range_real = 50,
		ox = 0, oy = 0 },
	{ marker = "the_vortex_shard", name = "The Vortex Shard", trigger = "enemy_engaged_or_shot",
		badge = "zz_auto_badge_the_vortex_shard",
		keys = { "wh2_main_item_abilities_the_vortex_shard" },
		range_real = 100,
		ox = 0, oy = 0 },
	{ marker = "the_wintertooth_crown", name = "The Wintertooth Crown", trigger = "melee_unwavering",
		badge = "zz_auto_badge_the_wintertooth_crown",
		keys = { "wh_dlc08_item_abilities_the_wintertooth_crown" },
		ox = 0, oy = 0 },
	{ marker = "wissenland_runefang", name = "The Wissenland Runefang", trigger = "melee_unwavering",
		badge = "zz_auto_badge_wissenland_runefang",
		keys = { "wh2_dlc13_weapon_abilities_wissenland_runefang" },
		ox = 0, oy = 0 },
	{ marker = "the_withering", name = "The Withering", trigger = "enemy_engaged_or_shot",
		badge = "zz_auto_badge_the_withering",
		keys = { "wh3_dlc23_spell_bound_the_withering",
			"wh3_twa08_spell_bound_the_withering" },
		range_real = 200,
		ox = 0, oy = 0 },
	{ marker = "they_needs_stabbin", name = "They Needs Stabbin’", trigger = "enemy_engaged_or_shot",
		badge = "zz_auto_badge_they_needs_stabbin",
		keys = { "wh2_dlc15_character_abilities_they_needs_stabbin" },
		range_real = 75,
		target_class = "commander",
		ox = 0, oy = 0 },
	{ marker = "thorns_aura", name = "Thorn's Aura", trigger = "melee_unwavering",
		badge = "zz_auto_badge_thorns_aura",
		keys = { "wh3_dlc24_hero_abilities_thorns_aura" },
		ox = 0, oy = 0 },
	{ marker = "titan_headsman", name = "Titan Headsman", trigger = "enemy_melee",
		badge = "zz_auto_badge_titan_headsman",
		keys = { "wh3_dlc25_hero_abilities_titan_headsman" },
		range_real = 75,
		ox = 0, oy = 0 },
	{ marker = "torment_blade", name = "Torment Blade", trigger = "enemy_melee",
		badge = "zz_auto_badge_torment_blade",
		keys = { "wh3_main_weapon_abilities_torment_blade" },
		range_real = 50,
		ox = 0, oy = 0 },
	{ marker = "tricksters_shard", name = "Trickster's Shard", trigger = "enemy_ground_area",
		badge = "zz_auto_badge_tricksters_shard",
		keys = { "wh_main_item_abilities_tricksters_shard" },
		range_real = 500,
		ox = 0, oy = 0 },
	{ marker = "trophy_heads", name = "Trophy Heads", trigger = "enemy_melee",
		badge = "zz_auto_badge_trophy_heads",
		keys = { "wh2_main_lord_abilities_trophy_heads",
			"wh3_main_daemon_wings_abilities_trophy_heads" },
		range_real = 150,
		target_class = "commander",
		ox = 0, oy = 0 },
	{ marker = "twilight_horn_i", name = "Twilight Horn I", trigger = "charge_only",
		badge = "zz_auto_badge_twilight_horn_i",
		keys = { "wh2_dlc16_item_abilities_twilight_horn_i" },
		ox = 0, oy = 0 },
	{ marker = "undeath_resurgent", name = "Undeath Resurgent", trigger = "melee_unwavering",
		badge = "zz_auto_badge_undeath_resurgent",
		keys = { "wh_main_character_abilities_undeath_resurgent" },
		ox = 0, oy = 0 },
	{ marker = "unholy_clamour", name = "Unholy Clamour", trigger = "wavering_aura",
		badge = "zz_auto_badge_unholy_clamour",
		keys = { "wh2_main_mount_abilities_unholy_clamour" },
		aura_real = -1,
		ox = 0, oy = 0 },
	{ marker = "unlimited_power", name = "Unlimited Power!", trigger = "melee_unwavering",
		badge = "zz_auto_badge_unlimited_power",
		keys = { "wh2_dlc12_lord_abilities_unlimited_power" },
		ox = 0, oy = 0 },
	{ marker = "ursuns_roar_2", name = "Ursun's Mighty Roar", trigger = "melee_unwavering",
		badge = "zz_auto_badge_ursuns_roar_2",
		keys = { "wh3_main_pro_character_abilities_ursuns_roar_2" },
		ox = 0, oy = 0 },
	{ marker = "ursuns_roar", name = "Ursun's Roar", trigger = "melee_unwavering",
		badge = "zz_auto_badge_ursuns_roar",
		keys = { "wh3_main_character_abilities_ursuns_roar",
			"wh3_main_pro_character_abilities_ursuns_roar",
			"wh3_main_pro_character_abilities_ursuns_roar_1",
			"wh3_main_pro_character_abilities_ursuns_roar_3" },
		ox = 0, oy = 0 },
	{ marker = "van_horstmanns_speculum", name = "Van Horstmann's Speculum", trigger = "melee_unwavering",
		badge = "zz_auto_badge_van_horstmanns_speculum",
		keys = { "wh_main_item_abilities_van_horstmanns_speculum" },
		ox = 0, oy = 0 },
	{ marker = "verminous_fury", name = "Verminous Fury", trigger = "ally_melee_buff",
		badge = "zz_auto_badge_verminous_fury",
		keys = { "wh3_dlc29_lord_abilities_verminous_fury" },
		ally_range_real = 200,
		ox = 0, oy = 0 },
	{ marker = "virulent_contagion", name = "Virulent Contagion", trigger = "enemy_melee",
		badge = "zz_auto_badge_virulent_contagion",
		keys = { "wh3_main_lord_abilities_virulent_contagion" },
		range_real = 200,
		ox = 0, oy = 0 },
	{ marker = "virulent_contagion_upgraded", name = "Virulent Contagion Upgraded", trigger = "enemy_melee",
		badge = "zz_auto_badge_virulent_contagion_upgraded",
		keys = { "wh3_main_lord_abilities_virulent_contagion_upgraded" },
		range_real = 200,
		ox = 0, oy = 0 },
	{ marker = "void_pendulum", name = "Void Pendulum", trigger = "enemy_engaged_or_shot",
		badge = "zz_auto_badge_void_pendulum",
		keys = { "wh3_main_item_abilities_void_pendulum" },
		range_real = 200,
		ox = 0, oy = 0 },
	{ marker = "vorozhejas_foresight", name = "Vorozheja's Foresight", trigger = "enemy_engaged_or_shot",
		badge = "zz_auto_badge_vorozhejas_foresight",
		keys = { "wh3_dlc24_hero_abilities_vorozhejas_foresight" },
		range_real = 150,
		ox = 0, oy = 0 },
	{ marker = "waaagh_in_combat", name = "Waaagh!", trigger = "melee_unwavering",
		badge = "zz_auto_badge_waaagh_in_combat",
		keys = { "wh3_dlc26_unit_abilities_waaagh_in_combat",
			"wh_main_character_abilities_waaagh" },
		ox = 0, oy = 0 },
	{ marker = "wand_of_jet", name = "Wand of Jet", trigger = "melee_unwavering",
		badge = "zz_auto_badge_wand_of_jet",
		keys = { "wh_main_item_abilities_wand_of_jet" },
		ox = 0, oy = 0 },
	{ marker = "warp_gaze", name = "Warp Gaze", trigger = "enemy_engaged_or_shot",
		badge = "zz_auto_badge_warp_gaze",
		keys = { "wh_pro04_unit_abilities_warp_gaze" },
		range_real = 100,
		ox = 0, oy = 0 },
	{ marker = "warpstiletto", name = "Warpstiletto", trigger = "enemy_engaged_or_shot",
		badge = "zz_auto_badge_warpstiletto",
		keys = { "wh3_dlc29_item_abilities_warpstiletto" },
		range_real = 100,
		ox = 0, oy = 0 },
	{ marker = "warpstone_tokens", name = "Warpstone Tokens", trigger = "melee_unwavering",
		badge = "zz_auto_badge_warpstone_tokens",
		keys = { "wh3_dlc29_item_abilities_warpstone_tokens" },
		ox = 0, oy = 0 },
	{ marker = "watched_by_the_watcher", name = "Watched by the Watcher", trigger = "melee_unwavering",
		badge = "zz_auto_badge_watched_by_the_watcher",
		keys = { "wh3_dlc24_character_abilities_watched_by_the_watcher" },
		ox = 0, oy = 0 },
	{ marker = "were_you_goin", name = "Where You Goin!?", trigger = "ally_wavering",
		badge = "zz_auto_badge_were_you_goin",
		keys = { "wh3_dlc26_character_abilities_were_you_goin" },
		ally_range_real = 100,
		ox = 0, oy = 0 },
	{ marker = "whip_of_agony", name = "Whip of Agony", trigger = "enemy_melee",
		badge = "zz_auto_badge_whip_of_agony",
		keys = { "wh2_twa03_weapon_abilities_whip_of_agony" },
		range_real = 75,
		ox = 0, oy = 0 },
	{ marker = "whip_of_misery", name = "Whip of Misery", trigger = "enemy_engaged_or_shot",
		badge = "zz_auto_badge_whip_of_misery",
		keys = { "wh2_main_spell_bound_whip_of_agony" },
		range_real = 200,
		target_class = "large",
		ox = 0, oy = 0 },
	{ marker = "whiplash", name = "Whiplash!", trigger = "ally_beast",
		badge = "zz_auto_badge_whiplash",
		keys = { "wh2_dlc14_lord_abilities_whiplash" },
		ally_range_real = 100,
		ox = 0, oy = 0 },
	{ marker = "whispering_mist", name = "Whispering Mist", trigger = "enemy_fast_near_ally",
		badge = "zz_auto_badge_whispering_mist",
		keys = { "wh3_dlc29_hero_abilities_whispering_mist" },
		range_real = 200,
		ox = 0, oy = 0 },
	{ marker = "whispering_skull", name = "Whispering Skull", trigger = "melee_unwavering",
		badge = "zz_auto_badge_whispering_skull",
		keys = { "wh3_dlc29_item_abilities_whispering_skull" },
		ox = 0, oy = 0 },
	{ marker = "wild_abandon", name = "Wild Abandon", trigger = "melee_unwavering",
		badge = "zz_auto_badge_wild_abandon",
		keys = { "wh3_dlc26_lord_abilities_wild_abandon" },
		ox = 0, oy = 0 },
	{ marker = "willing_prey", name = "Willing Prey", trigger = "enemy_melee",
		badge = "zz_auto_badge_willing_prey",
		keys = { "wh3_main_lord_abilities_willing_prey" },
		range_real = 200,
		ox = 0, oy = 0 },
	{ marker = "winds_of_change", name = "Winds of Change", trigger = "melee_unwavering",
		badge = "zz_auto_badge_winds_of_change",
		keys = { "wh3_main_daemon_body_abilities_winds_of_change" },
		ox = 0, oy = 0 },
	{ marker = "word_of_change", name = "Word of Change", trigger = "enemy_engaged_or_shot",
		badge = "zz_auto_badge_word_of_change",
		keys = { "wh3_main_daemon_head_abilities_word_of_change" },
		range_real = 200,
		ox = 0, oy = 0 },
	{ marker = "word_of_pain", name = "Word of Pain", trigger = "enemy_engaged_or_shot",
		badge = "zz_auto_badge_word_of_pain",
		keys = { "wh2_dlc10_spell_bound_word_of_pain",
			"wh3_dlc27_spell_dark_magic_word_of_pain_bound_1use" },
		range_real = 200,
		ox = 0, oy = 0 },
	{ marker = "wrath_of_the_storm", name = "Wrath of the Storm", trigger = "melee_unwavering",
		badge = "zz_auto_badge_wrath_of_the_storm",
		keys = { "wh3_main_lord_abilities_wrath_of_the_storm" },
		ox = 0, oy = 0 },
	{ marker = "wrathful_reaper", name = "Wrathful Reaper", trigger = "melee_unwavering",
		badge = "zz_auto_badge_wrathful_reaper",
		keys = { "wh3_main_lord_abilities_wrathful_reaper" },
		ox = 0, oy = 0 },
	{ marker = "wristbands_of_black_gold", name = "Wristbands of Black Gold", trigger = "melee_unwavering",
		badge = "zz_auto_badge_wristbands_of_black_gold",
		keys = { "wh3_dlc29_item_abilities_wristbands_of_black_gold" },
		ox = 0, oy = 0 },
	{ marker = "youre_next", name = "You're Next!", trigger = "enemy_melee",
		badge = "zz_auto_badge_youre_next",
		keys = { "wh2_dlc15_lord_abilities_youre_next" },
		range_real = 75,
		target_class = "commander",
		ox = 0, oy = 0 },
	-- health<=75, no melee gate (the R1 heal / replenish batch) (36 entries)
	{ marker = "berry_wine", name = "Berry Wine", trigger = "health_aura_ally",
		badge = "zz_auto_badge_berry_wine",
		keys = { "wh2_dlc16_item_abilities_berry_wine" },
		ally_range_real = 60,
		ox = 0, oy = 0 },
	{ marker = "blood_chalice", name = "Blood Chalice", trigger = "ushoran_health",
		badge = "zz_auto_badge_blood_chalice",
		keys = { "wh3_dlc29_hero_abilities_blood_chalice" },
		ox = 0, oy = 0 },
	{ marker = "blood_chalice_of_bathori", name = "Blood Chalice of Bathori", trigger = "ushoran_health",
		badge = "zz_auto_badge_blood_chalice_of_bathori",
		keys = { "wh_pro02_item_abilities_blood_chalice_of_bathori" },
		ox = 0, oy = 0 },
	{ marker = "undeath_morkharn_breath_of_darkness", name = "Breath of Darkness", trigger = "ushoran_health",
		badge = "zz_auto_badge_undeath_morkharn_breath_of_darkness",
		keys = { "wh3_dlc29_spell_bound_undeath_morkharn_breath_of_darkness" },
		ox = 0, oy = 0 },
	{ marker = "undeath_morkharn_breath_of_darkness_upgraded", name = "Breath of Darkness Upgraded", trigger = "ushoran_health",
		badge = "zz_auto_badge_undeath_morkharn_breath_of_darkness_upgraded",
		keys = { "wh3_dlc29_spell_bound_undeath_morkharn_breath_of_darkness_upgraded" },
		ox = 0, oy = 0 },
	{ marker = "bugmans_xxxxxx", name = "Bugman's XXXXXX", trigger = "ushoran_health",
		badge = "zz_auto_badge_bugmans_xxxxxx",
		keys = { "wh3_dlc26_item_abilities_bugmans_xxxxxx" },
		ox = 0, oy = 0 },
	{ marker = "dreaming_ring_i", name = "Dreaming Ring I", trigger = "health_aura_ally",
		badge = "zz_auto_badge_dreaming_ring_i",
		keys = { "wh2_dlc16_item_abilities_dreaming_ring_i" },
		ally_range_real = 200,
		ox = 0, oy = 0 },
	{ marker = "dreaming_ring_ii", name = "Dreaming Ring II", trigger = "health_aura_ally",
		badge = "zz_auto_badge_dreaming_ring_ii",
		keys = { "wh2_dlc16_item_abilities_dreaming_ring_ii" },
		ally_range_real = 200,
		ox = 0, oy = 0 },
	{ marker = "dreaming_ring_iii", name = "Dreaming Ring III", trigger = "health_aura_ally",
		badge = "zz_auto_badge_dreaming_ring_iii",
		keys = { "wh2_dlc16_item_abilities_dreaming_ring_iii" },
		ally_range_real = 200,
		ox = 0, oy = 0 },
	{ marker = "earth_blood", name = "Earth Blood", trigger = "health_aura_ally",
		badge = "zz_auto_badge_earth_blood",
		keys = { "wh2_dlc16_spell_bound_earth_blood",
			"wh3_main_spell_bound_earth_blood" },
		ally_range_real = 200,
		ox = 0, oy = 0 },
	{ marker = "elfish_healing_herbs", name = "Elvish Healing Herbs", trigger = "ally_heal",
		badge = "zz_auto_badge_elfish_healing_herbs",
		keys = { "wh3_dlc27_unit_abilities_elfish_healing_herbs" },
		ally_range_real = 50,
		ox = 0, oy = 0 },
	{ marker = "fleshy_abundance", name = "Fleshy Abundance", trigger = "health_aura_ally",
		badge = "zz_auto_badge_fleshy_abundance",
		keys = { "wh3_dlc20_spell_bound_fleshy_abundance" },
		ally_range_real = 200,
		ox = 0, oy = 0 },
	{ marker = "hieratic_jar", name = "Hieratic Jar", trigger = "ushoran_health",
		badge = "zz_auto_badge_hieratic_jar",
		keys = { "wh2_dlc09_item_abilities_hieratic_jar" },
		ox = 0, oy = 0 },
	{ marker = "immortal_will", name = "Immortal Will", trigger = "ushoran_health",
		badge = "zz_auto_badge_immortal_will",
		keys = { "wh_main_hero_abilities_immortal_will" },
		ox = 0, oy = 0 },
	{ marker = "invocation_of_nehek", name = "Invocation of Nehek", trigger = "ushoran_health",
		badge = "zz_auto_badge_invocation_of_nehek",
		keys = { "wh3_dlc29_spell_bound_invocation_of_nehek" },
		ox = 0, oy = 0 },
	{ marker = "locus_of_fecundity", name = "Locus of Fecundity", trigger = "health_aura_self",
		badge = "zz_auto_badge_locus_of_fecundity",
		keys = { "wh3_main_character_abilities_locus_of_fecundity" },
		aura_real = 55,
		ox = 0, oy = 0 },
	{ marker = "makaissons_persuader", name = "Makaisson's Persuader", trigger = "ally_warmachine_heal",
		badge = "zz_auto_badge_makaissons_persuader",
		keys = { "wh3_dlc25_weapon_abilities_makaissons_persuader" },
		ally_range_real = 100,
		ox = 0, oy = 0 },
	{ marker = "neuroparasites", name = "Necroparasites", trigger = "ushoran_health",
		badge = "zz_auto_badge_neuroparasites",
		keys = { "wh2_dlc16_unit_abilities_neuroparasites" },
		ox = 0, oy = 0 },
	{ marker = "necrotic_phylactry", name = "Necrotic Phylactery", trigger = "ushoran_health",
		badge = "zz_auto_badge_necrotic_phylactry",
		keys = { "wh3_dlc25_item_abilities_necrotic_phylactry" },
		ox = 0, oy = 0 },
	{ marker = "patch_up", name = "Patch Up", trigger = "ally_heal",
		badge = "zz_auto_badge_patch_up",
		keys = { "wh2_dlc13_character_abilities_patch_up" },
		ally_range_real = 100,
		ox = 0, oy = 0 },
	{ marker = "pestilent_regeneration", name = "Pestilent Regeneration", trigger = "ushoran_health",
		badge = "zz_auto_badge_pestilent_regeneration",
		keys = { "wh3_main_daemon_head_abilities_pestilent_regeneration" },
		ox = 0, oy = 0 },
	{ marker = "potion_of_charoi", name = "Potion of Charoi", trigger = "ushoran_health",
		badge = "zz_auto_badge_potion_of_charoi",
		keys = { "wh2_main_lord_abilities_potion_of_charoi" },
		ox = 0, oy = 0 },
	{ marker = "potion_of_healing", name = "Potion of Healing", trigger = "ushoran_health",
		badge = "zz_auto_badge_potion_of_healing",
		keys = { "wh_main_item_abilities_potion_of_healing" },
		ox = 0, oy = 0 },
	{ marker = "radiant_gem_of_hoeth", name = "Radiant Gem of Hoeth", trigger = "health_aura_ally",
		badge = "zz_auto_badge_radiant_gem_of_hoeth",
		keys = { "wh2_main_spell_bound_radiant_gem_of_hoeth" },
		ally_range_real = 200,
		ox = 0, oy = 0 },
	{ marker = "reforge", name = "Reforge", trigger = "ally_hellforged_heal",
		badge = "zz_auto_badge_reforge",
		keys = { "wh3_dlc23_character_abilities_reforge" },
		ally_range_real = 100,
		ox = 0, oy = 0 },
	{ marker = "regenerating_flesh", name = "Regenerating Flesh", trigger = "ushoran_health",
		badge = "zz_auto_badge_regenerating_flesh",
		keys = { "wh_main_item_abilities_regenerating_flesh" },
		ox = 0, oy = 0 },
	{ marker = "regrowth", name = "Regrowth", trigger = "health_aura_ally",
		badge = "zz_auto_badge_regrowth",
		keys = { "wh2_dlc16_spell_bound_regrowth" },
		ally_range_real = 200,
		ox = 0, oy = 0 },
	{ marker = "remouldered", name = "Remouldered", trigger = "ally_monster_heal",
		badge = "zz_auto_badge_remouldered",
		keys = { "wh2_dlc16_lord_abilities_remouldered" },
		ally_range_real = 100,
		ox = 0, oy = 0 },
	{ marker = "restore", name = "Restore", trigger = "ally_construct_heal",
		badge = "zz_auto_badge_restore",
		keys = { "wh2_dlc09_character_abilities_restore" },
		ally_range_real = 100,
		ox = 0, oy = 0 },
	{ marker = "revivification_crystal", name = "Revivification Crystal", trigger = "ally_heal",
		badge = "zz_auto_badge_revivification_crystal",
		keys = { "wh2_main_unit_abilities_revivification_crystal" },
		ally_range_real = 100,
		ox = 0, oy = 0 },
	{ marker = "saint_annushkas_finger_bone", name = "Saint Annushka's Finger Bone", trigger = "ushoran_health",
		badge = "zz_auto_badge_saint_annushkas_finger_bone",
		keys = { "wh3_main_item_abilities_saint_annushkas_finger_bone" },
		ox = 0, oy = 0 },
	{ marker = "salyaks_lullaby", name = "Salyak's Lullaby", trigger = "health_aura_self",
		badge = "zz_auto_badge_salyaks_lullaby",
		keys = { "wh3_main_character_abilities_salyaks_lullaby" },
		aura_real = 35,
		ox = 0, oy = 0 },
	{ marker = "scroll_of_power", name = "Scroll of Power", trigger = "ushoran_health",
		badge = "zz_auto_badge_scroll_of_power",
		keys = { "wh_main_item_abilities_scroll_of_power" },
		ox = 0, oy = 0 },
	{ marker = "skalm", name = "Skalm", trigger = "ushoran_health",
		badge = "zz_auto_badge_skalm",
		keys = { "wh2_main_item_abilities_skalm" },
		ox = 0, oy = 0 },
	{ marker = "skars_kraken_killer", name = "Skar's Kraken-Killer", trigger = "ushoran_health",
		badge = "zz_auto_badge_skars_kraken_killer",
		keys = { "wh3_main_weapon_abilities_skars_kraken_killer" },
		ox = 0, oy = 0 },
	{ marker = "trollguts", name = "Trollguts", trigger = "health_aura_ally",
		badge = "zz_auto_badge_trollguts",
		keys = { "wh3_dlc26_spell_bound_trollguts" },
		ally_range_real = 200,
		ox = 0, oy = 0 },
	-- charge and in-melee (the R1 charge-bonus batch) (14 entries)
	{ marker = "bloodthirst", name = "Bloodthirst", trigger = "charge_or_melee",
		badge = "zz_auto_badge_bloodthirst",
		keys = { "wh3_main_lord_abilities_bloodthirst" },
		ox = 0, oy = 0 },
	{ marker = "colossal_strike", name = "Colossal Strike", trigger = "charge_or_melee",
		badge = "zz_auto_badge_colossal_strike",
		keys = { "wh3_dlc24_character_abilities_colossal_strike",
			"wh3_dlc24_character_abilities_colossal_strike_summoned" },
		ox = 0, oy = 0 },
	{ marker = "crimson_juggernaut", name = "Crimson Juggernaut", trigger = "charge_or_melee",
		badge = "zz_auto_badge_crimson_juggernaut",
		keys = { "wh3_dlc26_character_abilities_crimson_juggernaut" },
		ox = 0, oy = 0 },
	{ marker = "daemonic_onslaught", name = "Daemonic Onslaught", trigger = "charge_or_melee",
		badge = "zz_auto_badge_daemonic_onslaught",
		keys = { "wh3_main_daemon_legs_abilities_daemonic_onslaught" },
		ox = 0, oy = 0 },
	{ marker = "deadly_onslaught", name = "Deadly Onslaught", trigger = "charge_or_melee",
		badge = "zz_auto_badge_deadly_onslaught",
		keys = { "wh_dlc03_character_abilities_deadly_onslaught" },
		ox = 0, oy = 0 },
	{ marker = "full_power", name = "Full Power!", trigger = "charge_or_melee",
		badge = "zz_auto_badge_full_power",
		keys = { "wh3_dlc25_unit_abilities_full_power" },
		ox = 0, oy = 0 },
	{ marker = "guiding_strike", name = "Guiding Strike", trigger = "charge_or_melee",
		badge = "zz_auto_badge_guiding_strike",
		keys = { "wh3_cp1_lord_abilities_guiding_strike" },
		ox = 0, oy = 0 },
	{ marker = "locus_of_fury", name = "Locus of Fury", trigger = "charge_or_melee",
		badge = "zz_auto_badge_locus_of_fury",
		keys = { "wh3_main_character_abilities_locus_of_fury" },
		ox = 0, oy = 0 },
	{ marker = "locus_of_swiftness", name = "Locus of Swiftness", trigger = "charge_or_melee",
		badge = "zz_auto_badge_locus_of_swiftness",
		keys = { "wh3_main_character_abilities_locus_of_swiftness" },
		ox = 0, oy = 0 },
	{ marker = "mastered_strike", name = "Masterful Strike", trigger = "charge_or_melee",
		badge = "zz_auto_badge_mastered_strike",
		keys = { "wh3_cp1_lord_abilities_mastered_strike" },
		ox = 0, oy = 0 },
	{ marker = "more_power", name = "More Power!", trigger = "charge_or_melee",
		badge = "zz_auto_badge_more_power",
		keys = { "wh3_dlc23_unit_abilities_more_power" },
		ox = 0, oy = 0 },
	{ marker = "purge_the_weak", name = "Purge the Weak!", trigger = "charge_or_melee",
		badge = "zz_auto_badge_purge_the_weak",
		keys = { "wh3_main_daemon_wings_abilities_purge_the_weak" },
		ox = 0, oy = 0 },
	{ marker = "shield_of_thorns", name = "Shield of Thorns", trigger = "charge_or_melee",
		badge = "zz_auto_badge_shield_of_thorns",
		keys = { "wh2_dlc17_spell_bound_shield_of_thorns",
			"wh_dlc05_spell_bound_shield_of_thorns" },
		ox = 0, oy = 0 },
	{ marker = "storm_hammer", name = "Storm Hammer", trigger = "charge_or_melee",
		badge = "zz_auto_badge_storm_hammer",
		keys = { "wh3_dlc29_spell_bound_storm_hammer" },
		ox = 0, oy = 0 },

	-- ============================================================================
	-- THE FINAL ROSTER ROUND (this round) - the SIX built individual
	-- abilities from the remaining-abilities triage (WH3_remaining_triage.md
	-- section 3 INDIVIDUAL table). Blood Sacrifice and Eat da Runts! ride
	-- the TWO NEW ally-heal triggers (blood_sacrifice / eat_da_runts, each
	-- its own evaluator, section 7g); the four melee ones ride the EXISTING
	-- shared melee_unwavering evaluator (in-melee self). Base + DLC twins
	-- ride one entry where a name repeats (none here - one key each).
	-- ============================================================================
	{ marker = "blood_sacrifice", name = "Blood Sacrifice", trigger = "blood_sacrifice",
		badge = "zz_auto_badge_blood_sacrifice",
		keys = { "wh3_dlc26_lord_abilities_blood_sacrifice" },
		ox = 0, oy = 0 },
	{ marker = "eat_da_runts", name = "Eat da Runts!", trigger = "eat_da_runts",
		badge = "zz_auto_badge_eat_da_runts",
		keys = { "wh3_dlc26_unit_abilities_eat_da_runts" },
		ox = 0, oy = 0 },
	{ marker = "locus_of_virulence", name = "Locus of Virulence", trigger = "melee_unwavering",
		badge = "zz_auto_badge_locus_of_virulence",
		keys = { "wh3_main_character_abilities_locus_of_virulence" },
		ox = 0, oy = 0 },
	{ marker = "ultimate_verdict", name = "Ultimate Verdict", trigger = "melee_unwavering",
		badge = "zz_auto_badge_ultimate_verdict",
		keys = { "wh3_cp1_character_abilities_terrifying_presence" },
		ox = 0, oy = 0 },

	-- ============================================================================
	-- ROUND 122 (harness 121): TEN SELF-CAST MELEE BUFFS on the EXISTING shared
	-- melee_unwavering evaluator (user ruling 2026-10-27: Group A and Group B
	-- both on melee_unwavering, tuning round). Fires when the unit is in melee
	-- and not wavering; cast on the unit itself. All ten are in the wheel, none
	-- is in the army_spec junction, all are self-only (no range column, so no
	-- 70% range constant), unlimited uses, timed duration (no toggle stances).
	--   GROUP A, melee damage: Call for Power, Manus of Ursun, Black Hammer of
	--     Hashut, The Graven Sceptre, Tyrant's Talon, The Crimson Blade.
	--   GROUP B, melee survival: Bloodstorm, Crooked Dice, Temptator,
	--     All-Consuming Hatred.
	-- Table: 687 entries / 738 keys -> 697 / 748; melee_unwavering 360 -> 370.
	-- ============================================================================
	{ marker = "call_for_power", name = "Call for Power", trigger = "melee_unwavering",
		badge = "zz_auto_badge_call_for_power",
		keys = { "wh3_main_daemon_head_abilities_call_for_power" },
		ox = 0, oy = 0 },
	{ marker = "manus_of_ursun", name = "Manus of Ursun", trigger = "melee_unwavering",
		badge = "zz_auto_badge_manus_of_ursun",
		keys = { "wh3_main_weapon_abilities_ursuns_claws" },
		ox = 0, oy = 0 },
	{ marker = "black_hammer_of_hashut", name = "Black Hammer of Hashut", trigger = "melee_unwavering",
		badge = "zz_auto_badge_black_hammer_of_hashut",
		keys = { "wh3_dlc23_weapon_abilities_black_hammer_of_hashut" },
		ox = 0, oy = 0 },
	{ marker = "the_graven_sceptre", name = "The Graven Sceptre", trigger = "melee_unwavering",
		badge = "zz_auto_badge_the_graven_sceptre",
		keys = { "wh3_dlc23_weapon_abilities_the_graven_sceptre" },
		ox = 0, oy = 0 },
	{ marker = "tyrants_talon", name = "Tyrant's Talon", trigger = "melee_unwavering",
		badge = "zz_auto_badge_tyrants_talon",
		keys = { "wh3_cp1_weapon_abilities_tyrants_talon" },
		ox = 0, oy = 0 },
	{ marker = "the_crimson_blade", name = "The Crimson Blade", trigger = "melee_unwavering",
		badge = "zz_auto_badge_the_crimson_blade",
		keys = { "wh3_dlc29_item_abilities_crimson_blade" },
		ox = 0, oy = 0 },
	{ marker = "bloodstorm", name = "Bloodstorm", trigger = "melee_unwavering",
		badge = "zz_auto_badge_bloodstorm",
		keys = { "wh2_dlc14_lord_abilities_bloodstorm" },
		ox = 0, oy = 0 },
	{ marker = "crooked_dice", name = "Crooked Dice", trigger = "melee_unwavering",
		badge = "zz_auto_badge_crooked_dice",
		keys = { "wh3_dlc23_hero_abilities_crooked_dice" },
		ox = 0, oy = 0 },
	{ marker = "temptator", name = "Temptator", trigger = "melee_unwavering",
		badge = "zz_auto_badge_temptator",
		keys = { "wh3_dlc20_lord_abilities_temptator" },
		ox = 0, oy = 0 },
	{ marker = "all_consuming_hatred", name = "All-Consuming Hatred", trigger = "melee_unwavering",
		badge = "zz_auto_badge_all_consuming_hatred",
		keys = { "wh3_dlc27_unit_abilities_consuming_hatred" },
		ox = 0, oy = 0 },

	-- ============================================================================
	-- ROUND 123 (harness 122): THE HEX BATCH, one trigger PER ABILITY from what
	-- its effect changes (user ruling 2026-10-27):
	--   * no speed effect -> melee_unwavering (in melee, not wavering, cast on
	--     self; the 35 m enemy aura is then centred on the fight): Rival Hide
	--     Talisman, Seductive Glory, Vine Dragon Scale, Dark Mace.
	--   * reduces ENEMY SPEED -> charge_or_melee (this unit charges or is in
	--     melee), so the slow lands as the fight starts, never on an enemy that
	--     is only passing by: Seduction, Song of Enthrallment, Smoke Bomb.
	--   * melee-only debuff on ONE enemy -> enemy_melee (NEW: an enemy in range
	--     that is IN MELEE; being shot does NOT count, because melee defence only
	--     matters in melee): No Escape, Transfix (the dlc29 HEX key, a different
	--     ability from the self-buff Transfix above), Flash Bomb.
	--   The 70% bounds: 100 m -> 70 m, 75 m -> 52 m (FOURTH.ENEMY_CAST).
	--   Daemonic Possession is deliberately NOT here (user: it only makes sense
	--   just before a friendly spell, so it is not automated).
	-- ============================================================================
	{ marker = "rival_hide_talisman", name = "Rival Hide Talisman", trigger = "melee_unwavering",
		badge = "zz_auto_badge_rival_hide_talisman",
		keys = { "wh2_main_item_abilities_rival_hide_talisman" },
		ox = 0, oy = 0 },
	{ marker = "seductive_glory", name = "Seductive Glory", trigger = "melee_unwavering",
		badge = "zz_auto_badge_seductive_glory",
		keys = { "wh3_main_lord_abilities_seductive_glory" },
		ox = 0, oy = 0 },
	{ marker = "vine_dragon_scale", name = "Vine Dragon Scale", trigger = "melee_unwavering",
		badge = "zz_auto_badge_vine_dragon_scale",
		keys = { "wh2_dlc15_item_abilities_vine_dragon_scale" },
		ox = 0, oy = 0 },
	{ marker = "dark_mace", name = "Dark Mace", trigger = "melee_unwavering",
		badge = "zz_auto_badge_dark_mace",
		keys = { "wh3_dlc23_weapon_abilities_dark_mace" },
		ox = 0, oy = 0 },
	{ marker = "seduction", name = "Seduction", trigger = "charge_or_melee",
		badge = "zz_auto_badge_seduction",
		keys = { "wh2_dlc11_lord_abilities_seduction" },
		ox = 0, oy = 0 },
	{ marker = "song_of_enthrallment", name = "Song of Enthrallment", trigger = "charge_or_melee",
		badge = "zz_auto_badge_song_of_enthrallment",
		keys = { "wh2_dlc11_lord_abilities_song_of_enthrallment" },
		ox = 0, oy = 0 },
	{ marker = "smoke_bomb", name = "Smoke Bomb", trigger = "charge_or_melee",
		badge = "zz_auto_badge_smoke_bomb",
		keys = { "wh_dlc06_unit_abilities_smoke_bomb" },
		ox = 0, oy = 0 },
	{ marker = "no_escape", name = "No Escape", trigger = "enemy_melee",
		badge = "zz_auto_badge_no_escape",
		keys = { "wh3_main_character_abilities_no_escape" },
		range_real = 100,
		ox = 0, oy = 0 },
	{ marker = "transfix_hex", name = "Transfix", trigger = "enemy_melee",
		badge = "zz_auto_badge_transfix_hex",
		keys = { "wh3_dlc29_lord_abilities_transfix" },
		range_real = 100,
		target_class = "commander",
		ox = 0, oy = 0 },
	{ marker = "flash_bomb", name = "Flash Bomb", trigger = "enemy_melee",
		badge = "zz_auto_badge_flash_bomb",
		keys = { "wh_pro01_lord_abilities_flash_bomb" },
		range_real = 75,
		ox = 0, oy = 0 },

	-- ============================================================================
	-- THE SUMMON ROUND (harness 102 / v102).
	-- (A) THE REST OF THE wh_type_summon_unit CLASS - every in-wheel, non-illusion,
	-- GROUND-CASTABLE summon derived from the game's own data (spawned_unit set +
	-- type wh_type_summon_unit + spawn_is_decoy false + target_ground true + in-wheel
	-- + not boss-only + not already implemented): 57 entries / 68 keys.
	-- They ride the PROVEN enemy_ground_melee trigger (Gate of Khorne's): the closest
	-- FIGHTING enemy inside each ability's own 70% bound, summon placed on THAT
	-- ENEMY's ground. (D) THE NINE unlabelled real spawners, same trigger, same cast
	-- form. (E) Eye of Khorne is a FINISHER (enemy_low_health_noncommander) and
	-- casts through the UNIT form (target_enemies = true, target_ground = false).
	-- (F) The Dreaded Thirteenth (4 keys, one entry) is an explosion+summon on
	-- enemy_melee_noncommander, placed on the enemy's ground. (B) Nurgling Tide is
	-- the ONE self-target summon (self_summon_melee, cast on SELF).
	-- The four ILLUSIONS are NOT here: they are engine-refused while engaged in
	-- melee, so a melee trigger can never fire them (excluded, see the tracker).
	-- ============================================================================
	{ marker = "ancestral_vengeance", name = "Ancestral Vengeance", trigger = "enemy_ground_melee",
		badge = "zz_auto_badge_ancestral_vengeance",
		keys = { "wh3_dlc23_item_abilities_ancestral_vengeance" },
		range_real = 30,
		ox = 0, oy = 0 },
	{ marker = "ancestral_warriors", name = "Ancestral Warriors", trigger = "enemy_ground_melee",
		badge = "zz_auto_badge_ancestral_warriors",
		keys = { "wh3_main_spell_bound_ancestral_warriors" },
		range_real = 50,
		ox = 0, oy = 0 },
	{ marker = "arachnarok_eggs", name = "Arachnarok Eggs", trigger = "enemy_ground_melee",
		badge = "zz_auto_badge_arachnarok_eggs",
		keys = { "wh_dlc08_item_abilities_arachnarok_eggs" },
		range_real = 50,
		ox = 0, oy = 0 },
	{ marker = "beyond_the_realm", name = "Beyond the Realm", trigger = "enemy_ground_melee",
		badge = "zz_auto_badge_beyond_the_realm",
		keys = { "wh2_dlc11_character_abilities_beyond_the_realm" },
		range_real = 50,
		ox = 0, oy = 0 },
	{ marker = "bloodstone", name = "Bloodstone", trigger = "enemy_ground_melee",
		badge = "zz_auto_badge_bloodstone",
		keys = { "wh3_main_item_abilities_bloodstone" },
		range_real = 50,
		ox = 0, oy = 0 },
	{ marker = "call_to_ceithin_har", name = "Call to Ceithin-Har", trigger = "enemy_ground_melee",
		badge = "zz_auto_badge_call_to_ceithin_har",
		keys = { "wh2_dlc16_lord_abilities_call_to_ceithin_har" },
		range_real = 50,
		ox = 0, oy = 0 },
	{ marker = "captain_roths_moondial", name = "Captain Roth's Moondial", trigger = "enemy_ground_melee",
		badge = "zz_auto_badge_captain_roths_moondial",
		keys = { "wh2_dlc11_item_abilities_captain_roths_moondial" },
		range_real = 150,
		ox = 0, oy = 0 },
	{ marker = "children_of_the_forest", name = "Children of the Forest", trigger = "enemy_ground_melee",
		badge = "zz_auto_badge_children_of_the_forest",
		keys = { "wh3_dlc25_character_abilities_children_of_the_forest" },
		range_real = 50,
		ox = 0, oy = 0 },
	{ marker = "dreaming_cloak_i", name = "Dreaming Cloak I", trigger = "enemy_ground_melee",
		badge = "zz_auto_badge_dreaming_cloak_i",
		keys = { "wh2_dlc16_item_abilities_dreaming_cloak_i" },
		range_real = 50,
		ox = 0, oy = 0 },
	{ marker = "dreaming_cloak_ii", name = "Dreaming Cloak II", trigger = "enemy_ground_melee",
		badge = "zz_auto_badge_dreaming_cloak_ii",
		keys = { "wh2_dlc16_item_abilities_dreaming_cloak_ii" },
		range_real = 50,
		ox = 0, oy = 0 },
	{ marker = "dreaming_cloak_iii", name = "Dreaming Cloak III", trigger = "enemy_ground_melee",
		badge = "zz_auto_badge_dreaming_cloak_iii",
		keys = { "wh2_dlc16_item_abilities_dreaming_cloak_iii" },
		range_real = 50,
		ox = 0, oy = 0 },
	{ marker = "gate_of_chaos", name = "Gate of Chaos", trigger = "enemy_ground_melee",
		badge = "zz_auto_badge_gate_of_chaos",
		keys = { "wh3_main_daemon_arms_abilities_gate_of_chaos" },
		range_real = 50,
		ox = 0, oy = 0 },
	{ marker = "gate_of_chaos_upgraded", name = "Gate of Chaos Upgraded", trigger = "enemy_ground_melee",
		badge = "zz_auto_badge_gate_of_chaos_upgraded",
		keys = { "wh3_main_daemon_arms_abilities_gate_of_chaos_upgraded" },
		range_real = 50,
		ox = 0, oy = 0 },
	{ marker = "gate_of_nurgle", name = "Gate of Nurgle", trigger = "enemy_ground_melee",
		badge = "zz_auto_badge_gate_of_nurgle",
		keys = { "wh3_main_character_abilities_gate_of_nurgle" },
		range_real = 50,
		ox = 0, oy = 0 },
	{ marker = "gate_of_slaanesh", name = "Gate of Slaanesh", trigger = "enemy_ground_melee",
		badge = "zz_auto_badge_gate_of_slaanesh",
		keys = { "wh3_main_character_abilities_gate_of_slaanesh" },
		range_real = 50,
		ox = 0, oy = 0 },
	{ marker = "gate_of_tzeentch", name = "Gate of Tzeentch", trigger = "enemy_ground_melee",
		badge = "zz_auto_badge_gate_of_tzeentch",
		keys = { "wh3_main_character_abilities_gate_of_tzeentch" },
		range_real = 50,
		ox = 0, oy = 0 },
	{ marker = "get_tha_gitz", name = "Get Tha Gitz!", trigger = "enemy_ground_melee",
		badge = "zz_auto_badge_get_tha_gitz",
		keys = { "wh3_dlc23_hero_abilities_get_tha_gitz!" },
		range_real = 90,
		ox = 0, oy = 0 },
	{ marker = "ghosts_of_the_past", name = "Ghosts of the Past", trigger = "enemy_ground_melee",
		badge = "zz_auto_badge_ghosts_of_the_past",
		keys = {
			"wh2_dlc11_character_abilities_ghosts_of_the_past_0",
			"wh2_dlc11_character_abilities_ghosts_of_the_past_1",
			"wh2_dlc11_character_abilities_ghosts_of_the_past_2" },
		range_real = 50,
		ox = 0, oy = 0 },
	{ marker = "gorger_onslaught", name = "Gorger Onslaught", trigger = "enemy_ground_melee",
		badge = "zz_auto_badge_gorger_onslaught",
		keys = { "wh3_main_lord_abilities_gorger_onslaught" },
		range_real = 50,
		ox = 0, oy = 0 },
	{ marker = "gorger_onslaught_upgraded", name = "Gorger Onslaught Upgraded", trigger = "enemy_ground_melee",
		badge = "zz_auto_badge_gorger_onslaught_upgraded",
		keys = { "wh3_dlc26_lord_abilities_gorger_onslaught_upgraded" },
		range_real = 100,
		ox = 0, oy = 0 },
	{ marker = "greater_gate_of_khorne", name = "Greater Gate of Khorne", trigger = "enemy_ground_melee",
		badge = "zz_auto_badge_greater_gate_of_khorne",
		-- ROUND 121: the ARMY-BAR cataclysm key was REMOVED from this entry (army_spec
		-- junction - it is not on the battle ability wheel, so it can never be cast).
		-- The in-wheel character key stays.
		keys = { "wh3_main_character_abilities_greater_gate_of_khorne" },
		range_real = 50,
		ox = 0, oy = 0 },
	{ marker = "greater_gate_of_nurgle", name = "Greater Gate of Nurgle", trigger = "enemy_ground_melee",
		badge = "zz_auto_badge_greater_gate_of_nurgle",
		keys = { "wh3_main_character_abilities_greater_gate_of_nurgle" },
		range_real = 50,
		ox = 0, oy = 0 },
	{ marker = "greater_gate_of_slaanesh", name = "Greater Gate of Slaanesh", trigger = "enemy_ground_melee",
		badge = "zz_auto_badge_greater_gate_of_slaanesh",
		keys = { "wh3_main_character_abilities_greater_gate_of_slaanesh" },
		range_real = 50,
		ox = 0, oy = 0 },
	{ marker = "greater_gate_of_tzeentch", name = "Greater Gate of Tzeentch", trigger = "enemy_ground_melee",
		badge = "zz_auto_badge_greater_gate_of_tzeentch",
		keys = { "wh3_main_character_abilities_greater_gate_of_tzeentch" },
		range_real = 50,
		ox = 0, oy = 0 },
	{ marker = "guardian_call", name = "Guardian Call", trigger = "enemy_ground_melee",
		badge = "zz_auto_badge_guardian_call",
		keys = { "wh3_main_character_abilities_guardian_call" },
		range_real = 50,
		ox = 0, oy = 0 },
	{ marker = "guardian_call_ii", name = "Guardian Call II", trigger = "enemy_ground_melee",
		badge = "zz_auto_badge_guardian_call_ii",
		keys = { "wh3_main_character_abilities_guardian_call_ii" },
		range_real = 50,
		ox = 0, oy = 0 },
	{ marker = "guardian_call_iii", name = "Guardian Call III", trigger = "enemy_ground_melee",
		badge = "zz_auto_badge_guardian_call_iii",
		keys = { "wh3_main_character_abilities_guardian_call_iii" },
		range_real = 50,
		ox = 0, oy = 0 },
	{ marker = "guardian_of_the_forest", name = "Guardian of the Forest", trigger = "enemy_ground_melee",
		badge = "zz_auto_badge_guardian_of_the_forest",
		keys = { "wh3_dlc25_character_abilities_guardian_of_the_forest" },
		range_real = 50,
		ox = 0, oy = 0 },
	{ marker = "horn_of_the_ancestors", name = "Horn of the Ancestors", trigger = "enemy_ground_melee",
		badge = "zz_auto_badge_horn_of_the_ancestors",
		keys = { "wh2_dlc10_item_abilities_horn_of_the_ancestors" },
		range_real = 50,
		ox = 0, oy = 0 },
	{ marker = "inventory_of_hatchlings", name = "Inventory of Hatchlings", trigger = "enemy_ground_melee",
		badge = "zz_auto_badge_inventory_of_hatchlings",
		keys = { "wh3_dlc26_character_abilities_inventory_of_hatchlings" },
		range_real = 50,
		ox = 0, oy = 0 },
	{ marker = "inventory_of_hatchlings_upgraded", name = "Inventory of Hatchlings Upgraded", trigger = "enemy_ground_melee",
		badge = "zz_auto_badge_inventory_of_hatchlings_upgraded",
		keys = { "wh3_dlc26_character_abilities_inventory_of_hatchlings_upgraded" },
		range_real = 100,
		ox = 0, oy = 0 },
	{ marker = "invocation_of_the_lichemaster", name = "Invocation of the Lichemaster", trigger = "enemy_ground_melee",
		badge = "zz_auto_badge_invocation_of_the_lichemaster",
		keys = {
			"wh3_dlc29_character_abilities_invocation_of_the_lichemaster",
			"wh3_dlc29_character_abilities_invocation_of_the_lichemaster_0",
			"wh3_dlc29_character_abilities_invocation_of_the_lichemaster_1" },
		range_real = 50,
		ox = 0, oy = 0 },
	{ marker = "karanaks_howl", name = "Karanak's Howl", trigger = "enemy_ground_melee",
		badge = "zz_auto_badge_karanaks_howl",
		keys = { "wh3_pro12_hero_abilities_karanaks_howl" },
		range_real = 50,
		ox = 0, oy = 0 },
	{ marker = "kettles_call", name = "Kettle's Call", trigger = "enemy_ground_melee",
		badge = "zz_auto_badge_kettles_call",
		keys = { "wh3_dlc25_character_abilities_kettles_call" },
		range_real = 45,
		ox = 0, oy = 0 },
	{ marker = "koldunjas_spirit", name = "Koldunja's Spirit", trigger = "enemy_ground_melee",
		badge = "zz_auto_badge_koldunjas_spirit",
		keys = { "wh3_dlc24_hero_abilities_koldunjas_spirit" },
		range_real = 50,
		ox = 0, oy = 0 },
	{ marker = "locus_of_transmogrification", name = "Locus of Transmogrification", trigger = "enemy_ground_melee",
		badge = "zz_auto_badge_locus_of_transmogrification",
		keys = { "wh3_main_character_abilities_locus_of_transmogrification" },
		range_real = 50,
		ox = 0, oy = 0 },
	{ marker = "lord_of_undeath", name = "Lord of Undeath", trigger = "enemy_ground_melee",
		badge = "zz_auto_badge_lord_of_undeath",
		keys = {
			"wh_pro03_lord_abilities_lord_of_undeath",
			"wh_pro03_lord_abilities_lord_of_undeath_0",
			"wh_pro03_lord_abilities_lord_of_undeath_1",
			"wh_pro03_lord_abilities_lord_of_undeath_2",
			"wh_pro03_lord_abilities_lord_of_undeath_3",
			"wh_pro03_lord_abilities_lord_of_undeath_4" },
		range_real = 200,
		ox = 0, oy = 0 },
	{ marker = "mask_of_the_merlord", name = "Mask of the Merlord", trigger = "enemy_ground_melee",
		badge = "zz_auto_badge_mask_of_the_merlord",
		keys = { "wh3_dlc27_item_abilities_mask_of_the_merlord" },
		range_real = 100,
		ox = 0, oy = 0 },
	{ marker = "maternal_instinct", name = "Maternal Instinct", trigger = "enemy_ground_melee",
		badge = "zz_auto_badge_maternal_instinct",
		keys = { "wh_dlc06_unit_abilities_maternal_instinct" },
		range_real = 50,
		ox = 0, oy = 0 },
	{ marker = "nurgling_birth", name = "Nurgling Birth", trigger = "enemy_ground_melee",
		badge = "zz_auto_badge_nurgling_birth",
		keys = { "wh3_dlc29_hero_active_nurgling_birth" },
		range_real = 75,
		ox = 0, oy = 0 },
	{ marker = "nurgling_birth_upgraded", name = "Nurgling Birth Upgraded", trigger = "enemy_ground_melee",
		badge = "zz_auto_badge_nurgling_birth_upgraded",
		keys = { "wh3_dlc29_hero_active_nurgling_birth_upgraded" },
		range_real = 75,
		ox = 0, oy = 0 },
	{ marker = "ritual_of_the_beast", name = "Ritual of the Beast", trigger = "enemy_ground_melee",
		badge = "zz_auto_badge_ritual_of_the_beast",
		keys = { "wh3_dlc24_item_abilities_ritual_of_the_beast" },
		range_real = 50,
		ox = 0, oy = 0 },
	{ marker = "roused_to_wrath", name = "Roused to Wrath", trigger = "enemy_ground_melee",
		badge = "zz_auto_badge_roused_to_wrath",
		keys = {
			"wh2_dlc16_lord_abilities_roused_to_wrath",
			"wh2_dlc16_lord_abilities_roused_to_wrath_2" },
		range_real = 50,
		ox = 0, oy = 0 },
	{ marker = "sacrilege", name = "Sacrilege", trigger = "enemy_ground_melee",
		badge = "zz_auto_badge_sacrilege",
		keys = { "wh2_dlc11_character_abilities_sacrilege" },
		range_real = 50,
		ox = 0, oy = 0 },
	{ marker = "stave_of_ruinous_corruption", name = "Stave of Ruinous Corruption", trigger = "enemy_ground_melee",
		badge = "zz_auto_badge_stave_of_ruinous_corruption",
		keys = { "wh_dlc05_weapon_abilities_stave_of_ruinous_corruption" },
		range_real = 50,
		ox = 0, oy = 0 },
	{ marker = "surprise_squig", name = "Surprise Squig!", trigger = "enemy_ground_melee",
		badge = "zz_auto_badge_surprise_squig",
		keys = { "wh3_dlc25_character_abilities_surprise_squig" },
		range_real = 50,
		ox = 0, oy = 0 },
	{ marker = "sword_of_change", name = "Sword of Change", trigger = "enemy_ground_melee",
		badge = "zz_auto_badge_sword_of_change",
		keys = { "wh_dlc01_weapon_abilities_sword_of_change" },
		range_real = 50,
		ox = 0, oy = 0 },
	{ marker = "the_awakening", name = "The Awakening", trigger = "enemy_ground_melee",
		badge = "zz_auto_badge_the_awakening",
		keys = { "wh3_dlc29_lord_abilities_the_awakening" },
		range_real = 75,
		ox = 0, oy = 0 },
	{ marker = "the_heralds_arrival", name = "The Heralds' Arrival", trigger = "enemy_ground_melee",
		badge = "zz_auto_badge_the_heralds_arrival",
		keys = { "wh3_dlc29_vmp_mon_morghast_archai_summon" },
		range_real = 50,
		ox = 0, oy = 0 },
	{ marker = "the_portalglyph", name = "The Portalglyph", trigger = "enemy_ground_melee",
		badge = "zz_auto_badge_the_portalglyph",
		keys = { "wh3_main_item_abilities_the_portalglyph" },
		range_real = 50,
		ox = 0, oy = 0 },
	{ marker = "the_tallymans_blades", name = "The Tallyman's Blades", trigger = "enemy_ground_melee",
		badge = "zz_auto_badge_the_tallymans_blades",
		keys = { "wh3_dlc25_character_abilities_tallymans_blades" },
		range_real = 50,
		ox = 0, oy = 0 },
	{ marker = "the_tallymans_blades_upgraded", name = "The Tallyman's Blades Upgraded", trigger = "enemy_ground_melee",
		badge = "zz_auto_badge_the_tallymans_blades_upgraded",
		keys = { "wh3_dlc25_character_abilities_tallymans_blades_2" },
		unbounded = true,
		ox = 0, oy = 0 },
	{ marker = "the_tomb_blade_of_arkhan", name = "The Tomb Blade of Arkhan", trigger = "enemy_ground_melee",
		badge = "zz_auto_badge_the_tomb_blade_of_arkhan",
		keys = { "wh2_dlc09_weapon_abilities_tomb_blade_of_arkhan" },
		range_real = 50,
		ox = 0, oy = 0 },
	{ marker = "transformation_of_kadon", name = "Transformation of Kadon", trigger = "enemy_ground_melee",
		badge = "zz_auto_badge_transformation_of_kadon",
		keys = { "wh3_dlc27_spell_bound_transformation_of_kadon" },
		range_real = 50,
		ox = 0, oy = 0 },
	{ marker = "undeath_to_all", name = "Undeath to All", trigger = "enemy_ground_melee",
		badge = "zz_auto_badge_undeath_to_all",
		keys = { "wh3_dlc29_lord_abilities_raise_legion" },
		range_real = 75,
		ox = 0, oy = 0 },
	{ marker = "undeath_to_all_upgraded", name = "Undeath to All Upgraded", trigger = "enemy_ground_melee",
		badge = "zz_auto_badge_undeath_to_all_upgraded",
		keys = { "wh3_dlc29_lord_abilities_raise_legion_upgraded" },
		range_real = 75,
		ox = 0, oy = 0 },
	{ marker = "viziers_kanopi", name = "Vizier's Kanopi", trigger = "enemy_ground_melee",
		badge = "zz_auto_badge_viziers_kanopi",
		keys = { "wh3_dlc26_item_tmb_liche_priest_viziers_kanopi" },
		range_real = 50,
		ox = 0, oy = 0 },
	{ marker = "beast_pack", name = "Beast Pack", trigger = "enemy_ground_melee",
		badge = "zz_auto_badge_beast_pack",
		keys = { "wh2_dlc16_lord_abilities_beast_pack" },
		range_real = 50,
		ox = 0, oy = 0 },
	{ marker = "blacktoofs_conjuration", name = "Blacktoof's Conjuration", trigger = "enemy_ground_melee",
		badge = "zz_auto_badge_blacktoofs_conjuration",
		keys = { "wh2_dlc15_item_abilities_blacktoofs_conjuration" },
		range_real = 50,
		ox = 0, oy = 0 },
	{ marker = "call_to_gwindalor", name = "Call to Gwindalor", trigger = "enemy_ground_melee",
		badge = "zz_auto_badge_call_to_gwindalor",
		keys = { "wh2_dlc16_lord_abilities_call_to_gwindalor" },
		range_real = 50,
		ox = 0, oy = 0 },
	{ marker = "lesser_raise_dead", name = "Lesser Raise Dead", trigger = "enemy_ground_melee",
		badge = "zz_auto_badge_lesser_raise_dead",
		keys = { "wh2_dlc16_spell_bound_vampires_lesser_raise_dead" },
		range_real = 50,
		ox = 0, oy = 0 },
	{ marker = "savage_dominion", name = "Savage Dominion", trigger = "enemy_ground_melee",
		badge = "zz_auto_badge_savage_dominion",
		keys = { "wh2_dlc17_spell_bound_savage_dominion" },
		range_real = 50,
		ox = 0, oy = 0 },
	{ marker = "savage_predators", name = "Savage Predators", trigger = "enemy_ground_melee",
		badge = "zz_auto_badge_savage_predators",
		keys = { "wh3_dlc26_hero_abilities_savage_predators" },
		range_real = 45,
		ox = 0, oy = 0 },
	{ marker = "tide_of_death", name = "Tide of Death", trigger = "enemy_ground_melee",
		badge = "zz_auto_badge_tide_of_death",
		keys = { "wh2_dlc16_hero_abilities_tide_of_death" },
		range_real = 50,
		ox = 0, oy = 0 },
	{ marker = "tide_of_pox", name = "Tide of Pox", trigger = "enemy_ground_melee",
		badge = "zz_auto_badge_tide_of_pox",
		keys = { "wh2_dlc16_hero_abilities_tide_of_pox" },
		range_real = 50,
		ox = 0, oy = 0 },
	{ marker = "wake_da_idol", name = "Wake Da Idol", trigger = "enemy_ground_melee",
		badge = "zz_auto_badge_wake_da_idol",
		keys = { "wh3_main_item_abilities_zak_aloooog" },
		range_real = 50,
		ox = 0, oy = 0 },
	{ marker = "eye_of_khorne", name = "Eye of Khorne", trigger = "enemy_low_health_noncommander",
		badge = "zz_auto_badge_eye_of_khorne",
		keys = { "wh3_dlc26_lord_abilities_eye_of_khorne" },
		range_real = 50,
		ox = 0, oy = 0 },
	{ marker = "the_dreaded_thirteenth", name = "The Dreaded Thirteenth", trigger = "enemy_melee_noncommander",
		badge = "zz_auto_badge_the_dreaded_thirteenth",
		keys = {
			"wh3_dlc29_spell_bound_the_dreaded_thirteenth",
			"wh3_dlc29_spell_bound_the_dreaded_thirteenth_1",
			"wh3_dlc29_spell_bound_the_dreaded_thirteenth_thanquol",
			"wh3_dlc29_spell_bound_the_dreaded_thirteenth_thanquol_1" },
		range_real = 100,
		ox = 0, oy = 0 },
	{ marker = "nurgling_tide", name = "Nurgling Tide", trigger = "self_summon_melee",
		badge = "zz_auto_badge_nurgling_tide",
		keys = { "wh3_main_lord_abilities_nurgling_tide" },
		ox = 0, oy = 0 },

	-- ============================================================================
	-- TZ'ARKAN (this round) - FIVE keys, ONE entry, ONE new low-health trigger.
	-- The user's rule: "I think it might make sense to activate Tz'arkan when
	-- caster health is below 15%, don't you think? Let's implement and test it."
	-- The five keys are the same transform in its five shipped forms (base, MP,
	-- Snikch's, and the spite form + its MP twin). They share ONE marker, badge,
	-- arming switch and back-off, exactly like the multi-key entries above.
	--
	-- KNOWN RISK, stated deliberately: a transform is very likely ONE-WAY, and
	-- these rows declare a 3 s wind-up (1.5 s for the Snikch key), so a caster at
	-- 14% can DIE inside that window before the transform resolves. The 15% line
	-- is the user's own rule and is ONE number (FOURTH.TZARKAN_PCT) - trivial to
	-- raise to 20% or 25% if field tests show deaths before the transform lands.
	-- ============================================================================
	{ marker = "tzarkan", name = "Tz'arkan", trigger = "health_below_15",
		badge = "zz_auto_badge_tzarkan",
		keys = {
			"wh2_dlc14_lord_abilities_tzarkan",
			"wh2_dlc14_lord_abilities_tzarkan_mp",
			"wh2_dlc14_lord_abilities_tzarkan_snikch",
			"wh2_dlc14_lord_abilities_tzarkan_spite",
			"wh2_dlc14_lord_abilities_tzarkan_spite_mp" },
		ox = 0, oy = 0 },

	-- ======================================================================
	-- ROUND 106 - THE BOMBARDMENT ROUND, family (1): Soulfire (both keys)
	-- and Arachneruption on the NEW trigger melee_skip_commanders.
	-- The user's rule: fire when the caster is IN MELEE, but SKIP when every
	-- enemy it is fighting is a Lord or a Hero. Both rows are SELF-CENTRED
	-- (target flags all false, target_intercept_range 0), so the cast is on
	-- the OWNER through the unit form - there is no target to pick.
	-- ======================================================================
	{ marker = "soulfire", name = "Soulfire", trigger = "melee_skip_commanders",
		badge = "zz_auto_badge_soulfire",
		keys = { "wh_main_spell_bound_soulfire",
			"wh_dlc04_spell_bound_soulfire_upgraded" },
		ox = 0, oy = 0 },
	{ marker = "arachneruption", name = "Arachneruption", trigger = "melee_skip_commanders",
		badge = "zz_auto_badge_arachneruption",
		keys = { "wh2_dlc15_unit_abilities_arachneruption" },
		ox = 0, oy = 0 },
	-- ROUND 107 (item 2): CALL OF TOR - the user's rule, verbatim: "Call of Tor
	-- looks very similar to Soulfire, so let's do the same trigger as a
	-- Soulfire." Its row is SELF-CENTRED exactly like Soulfire's (all four
	-- target flags false, target_intercept_range 0, ai_usage =
	-- aoe_centred_on_self), so it rides melee_skip_commanders unchanged: the
	-- caster must be in melee and at least one engaged enemy must NOT be a Lord
	-- or a Hero. The judged engagement set is logged with every member's type,
	-- commander flag and real distance - the same line Soulfire writes.
	{ marker = "call_of_tor", name = "Call of Tor", trigger = "melee_skip_commanders",
		badge = "zz_auto_badge_call_of_tor",
		keys = { "wh3_twa07_spell_bound_call_of_tor" },
		ox = 0, oy = 0 },
	-- ROUND 108 (item 2): WARP LIGHTNING ROD - the user's rule, verbatim:
	-- "Warp Lightning Rod seems to be an effect no unit has by default, but
	-- during the campaign some units can aquire it via mutation (Clan Moulder
	-- Lobotomy augmentation). Let's treat it the same as Soulfire."
	-- Its row is SELF-CENTRED exactly like Soulfire's (affect_self = true, all
	-- four target flags false, target_intercept_range 0, effect_range 0) and it
	-- calls a bombardment down around the caster, so it rides
	-- melee_skip_commanders unchanged: in melee, unless every enemy engaged with
	-- it is a Lord or a Hero. The judged engagement set is logged with every
	-- member's type, commander flag and real distance - the same line Soulfire
	-- writes - and the caster/enemy are re-read immediately before the cast.
	--
	-- ITS GRANT, WHICH EXPLAINS THE MISSING CARRIER: this key has NO carrier
	-- junction row anywhere in the extracted data - no land_units / uset_ability
	-- entry, only the ability row, its invalid-usage flag (`climbing`), its UI
	-- effects and its loc line. It is NOT a default unit ability. In campaign it
	-- is granted by the Clan Moulder LOBOTOMY augmentation (a mutation), which
	-- is why no battle roster shows a carrier and why the pre-108 data sweep
	-- found no junction. The entry still fires correctly because the mod arms
	-- per unit on whatever key that unit actually owns at battle time.
	{ marker = "warp_lightning_rod", name = "Warp Lightning Rod", trigger = "melee_skip_commanders",
		badge = "zz_auto_badge_warp_lightning_rod",
		keys = { "wh2_dlc16_unit_abilities_warp_lightning_rod" },
		ox = 0, oy = 0 },
	-- ======================================================================
	-- ROUND 106 - THE BOMBARDMENT ROUND, family (2): the 30 approved
	-- bombardment abilities on the NEW trigger enemy_ground_melee_infantry.
	-- Trigger: the CLOSEST enemy inside the ability's own 70% bound, IN
	-- MELEE, that IS INFANTRY (battle_unit:is_infantry, unit_class fallback,
	-- fail-closed). Cast form follows EACH row's own flags: the 24
	-- ground-targeted keys are placed on the chosen enemy's ground (they are
	-- listed in FOURTH.enemy_ground_keys above); the 6 unit-targeted keys
	-- (lesser_doombolt, rod_of_torment, tome_of_furion, wand_of_the_kharaidon,
	-- wolfs_howl, wraith_storm) cast on the enemy unit itself. Two of the 32
	-- are NOT here and are reported instead: Thorsen's Thunderstorm (both
	-- keys sit in army_spec - an ARMY-bar ability, out of wheel scope) and
	-- Warp Lightning Rod (target flags all false, range 0: it has no enemy
	-- target at all, so no enemy-triggered cast can be issued).
	-- ======================================================================
	{ marker = "assault_of_stone", name = "Assault of Stone", trigger = "enemy_ground_melee_infantry",
		badge = "zz_auto_badge_assault_of_stone",
		keys = { "wh2_dlc10_item_bound_assault_of_stone" },
		range_real = 200,
		ox = 0, oy = 0 },
	{ marker = "axe_of_tor", name = "Axe of Tor", trigger = "enemy_ground_melee_infantry",
		badge = "zz_auto_badge_axe_of_tor",
		keys = { "wh3_main_weapon_abilities_axe_of_tor" },
		range_real = 200,
		ox = 0, oy = 0 },
	{ marker = "celestial_comet", name = "Celestial Comet", trigger = "enemy_ground_melee_infantry",
		badge = "zz_auto_badge_celestial_comet",
		keys = { "wh3_main_mount_bound_celestial_comet" },
		range_real = 200,
		ox = 0, oy = 0 },
	{ marker = "celestial_lightning", name = "Celestial Lightning", trigger = "enemy_ground_melee_infantry",
		badge = "zz_auto_badge_celestial_lightning",
		keys = { "wh3_main_mount_bound_celestial_lightning" },
		range_real = 300,
		ox = 0, oy = 0 },
	{ marker = "chalice_of_potions", name = "Chalice of Potions", trigger = "enemy_ground_melee_infantry",
		badge = "zz_auto_badge_chalice_of_potions",
		keys = { "wh_dlc07_item_abilities_chalice_of_potions" },
		range_real = 200,
		ox = 0, oy = 0 },
	{ marker = "comet_of_casandora", name = "Comet of Casandora", trigger = "enemy_ground_melee_infantry",
		badge = "zz_auto_badge_comet_of_casandora",
		keys = { "wh3_main_spell_bound_comet_of_casandora" },
		range_real = 200,
		ox = 0, oy = 0 },
	{ marker = "dragon_ogres_great_horn", name = "Dragon Ogre's Great Horn", trigger = "enemy_ground_melee_infantry",
		badge = "zz_auto_badge_dragon_ogres_great_horn",
		keys = { "wh_dlc08_item_abilities_great_horn_of_dragon_ogre" },
		range_real = 200,
		ox = 0, oy = 0 },
	{ marker = "flame_and_shadow", name = "Flame & Shadow", trigger = "enemy_ground_melee_infantry",
		badge = "zz_auto_badge_flame_and_shadow",
		keys = { "wh3_dlc23_lord_abilities_flame_and_shadow" },
		range_real = 100,
		ox = 0, oy = 0 },
	{ marker = "hawks_talon", name = "Hawk's Talon", trigger = "enemy_ground_melee_infantry",
		badge = "zz_auto_badge_hawks_talon",
		keys = { "wh_dlc05_weapon_abilities_hawks_talon" },
		range_real = 200,
		ox = 0, oy = 0 },
	{ marker = "ishas_rain", name = "Isha's Rain", trigger = "enemy_ground_melee_infantry",
		badge = "zz_auto_badge_ishas_rain",
		keys = { "wh2_dlc13_character_ability_ishas_rain" },
		range_real = 200,
		ox = 0, oy = 0 },
	{ marker = "klad_brakak", name = "Klad Brakak", trigger = "enemy_ground_melee_infantry",
		badge = "zz_auto_badge_klad_brakak",
		keys = { "wh2_dlc17_spell_bound_urannons_thunderbolt_upgraded" },
		range_real = 30,
		ox = 0, oy = 0 },
	{ marker = "lesser_doombolt", name = "Lesser Doombolt", trigger = "enemy_ground_melee_infantry",
		badge = "zz_auto_badge_lesser_doombolt",
		keys = { "wh2_dlc10_spell_bound_lesser_doombolt" },
		range_real = 200,
		ox = 0, oy = 0 },
	{ marker = "lightning_strike", name = "Lightning Strike", trigger = "enemy_ground_melee_infantry",
		badge = "zz_auto_badge_lightning_strike",
		keys = { "wh3_dlc29_unit_abilities_lightning_strike" },
		range_real = 300,
		ox = 0, oy = 0 },
	{ marker = "lord_of_the_storm", name = "Lord of the Storm", trigger = "enemy_ground_melee_infantry",
		badge = "zz_auto_badge_lord_of_the_storm",
		keys = { "wh_main_lord_abilities_lord_of_the_storm" },
		range_real = 200,
		ox = 0, oy = 0 },
	{ marker = "master_of_lightning", name = "Master of Lightning", trigger = "enemy_ground_melee_infantry",
		badge = "zz_auto_badge_master_of_lightning",
		keys = { "wh3_dlc29_spell_bound_warp_lightning" },
		range_real = 200,
		ox = 0, oy = 0 },
	{ marker = "meteor_strike", name = "Meteor Strike", trigger = "enemy_ground_melee_infantry",
		badge = "zz_auto_badge_meteor_strike",
		keys = { "wh3_dlc29_unit_abilities_meteor_strike" },
		range_real = 200,
		ox = 0, oy = 0 },
	{ marker = "nemesis_crown", name = "Nemesis Crown", trigger = "enemy_ground_melee_infantry",
		badge = "zz_auto_badge_nemesis_crown",
		keys = { "wh3_dlc25_lord_abilities_nemesis_crown" },
		range_real = 100,
		ox = 0, oy = 0 },
	{ marker = "piercing_bolts_of_burning", name = "Piercing Bolts of Burning", trigger = "enemy_ground_melee_infantry",
		badge = "zz_auto_badge_piercing_bolts_of_burning",
		keys = { "wh_main_spell_bound_piercing_bolts_of_burning" },
		range_real = 200,
		ox = 0, oy = 0 },
	{ marker = "pigeon_bomb", name = "Pigeon Bomb", trigger = "enemy_ground_melee_infantry",
		badge = "zz_auto_badge_pigeon_bomb",
		keys = { "wh3_dlc25_character_abilities_pigeon_bomb" },
		range_real = 200,
		ox = 0, oy = 0 },
	{ marker = "rod_of_the_storm", name = "Rod of the Storm", trigger = "enemy_ground_melee_infantry",
		badge = "zz_auto_badge_rod_of_the_storm",
		keys = { "wh2_main_spell_bound_rod_of_the_storm" },
		range_real = 300,
		ox = 0, oy = 0 },
	{ marker = "rod_of_torment", name = "Rod of Torment", trigger = "enemy_ground_melee_infantry",
		badge = "zz_auto_badge_rod_of_torment",
		keys = { "wh3_dlc20_item_abilities_rod_of_torment" },
		range_real = 200,
		ox = 0, oy = 0 },
	{ marker = "sceptre_of_stone", name = "Sceptre of Stone", trigger = "enemy_ground_melee_infantry",
		badge = "zz_auto_badge_sceptre_of_stone",
		keys = { "wh2_dlc10_item_abilities_sceptre_of_stone" },
		range_real = 200,
		ox = 0, oy = 0 },
	{ marker = "searing_doom", name = "Searing Doom", trigger = "enemy_ground_melee_infantry",
		badge = "zz_auto_badge_searing_doom",
		keys = { "wh3_twa08_spell_bound_searing_doom" },
		range_real = 200,
		ox = 0, oy = 0 },
	{ marker = "slicing_shards", name = "Slicing Shards", trigger = "enemy_ground_melee_infantry",
		badge = "zz_auto_badge_slicing_shards",
		keys = { "wh3_dlc20_spell_bound_slicing_shards", "wh3_main_spell_slaanesh_slicing_shards_bound" },
		range_real = 200,
		ox = 0, oy = 0 },
	{ marker = "the_bow_of_loren", name = "The Bow of Loren", trigger = "enemy_ground_melee_infantry",
		badge = "zz_auto_badge_the_bow_of_loren",
		keys = { "wh_dlc05_weapon_abilities_the_bow_of_loren" },
		range_real = 200,
		ox = 0, oy = 0 },
	{ marker = "tome_of_furion", name = "Tome of Furion", trigger = "enemy_ground_melee_infantry",
		badge = "zz_auto_badge_tome_of_furion",
		keys = { "wh2_main_spell_bound_tome_of_furion" },
		range_real = 200,
		ox = 0, oy = 0 },
	{ marker = "urannons_thunderbolt", name = "Urannon's Thunderbolt", trigger = "enemy_ground_melee_infantry",
		badge = "zz_auto_badge_urannons_thunderbolt",
		keys = { "wh2_dlc17_spell_bound_urannons_thunderbolt" },
		range_real = 300,
		ox = 0, oy = 0 },
	{ marker = "wand_of_the_kharaidon", name = "Wand of the Kharaidon", trigger = "enemy_ground_melee_infantry",
		badge = "zz_auto_badge_wand_of_the_kharaidon",
		keys = { "wh2_main_spell_bound_wand_of_the_kharaidon" },
		range_real = 200,
		ox = 0, oy = 0 },
	{ marker = "wolfs_howl", name = "Wolf's Howl", trigger = "enemy_ground_melee_infantry",
		badge = "zz_auto_badge_wolfs_howl",
		keys = { "wh3_main_weapon_abilities_the_traitors_sword" },
		range_real = 200,
		ox = 0, oy = 0 },
	{ marker = "wraith_storm", name = "Wraith Storm", trigger = "enemy_ground_melee_infantry",
		badge = "zz_auto_badge_wraith_storm",
		keys = { "wh2_dlc11_lord_abilities_wraith_storm" },
		range_real = 200,
		ox = 0, oy = 0 },
	-- ======================================================================
	-- ======================================================================
	-- ROUND 107 (item 3), REWRITTEN IN ROUND 114: THE "ON TOP OF" FAMILY -
	-- 12 entries / 19 keys on the trigger air_drop_on_infantry.
	--
	-- Every one of these rows has NO target flags at all (friends / enemies /
	-- ground / self all false), effect_range 0, target_intercept_range 10 and
	-- ai_usage always_use_only_land: the engine drops the ordnance where the
	-- CASTER is, so the mod's only decision is WHEN.
	--
	-- THE RULE (round 114, the user's ruling; the MEASUREMENT moved to the
	-- CENTRE in round 117): fire the moment the NEAREST VALID enemy's GROUND
	-- CENTRE distance - position():distance_xz - is below
	-- FOURTH.AIR_DROP_CENTER_M = 6.0 m, where a valid enemy is one that is
	-- alive with MORE THAN FOURTH.AIR_DROP_MIN_MEN = 10 models, and while the
	-- caster satisfies the usage restrictions its own row declares:
	--   air_only = the row says the engine refuses it while `grounded`,
	--              OR every carrier of the key carries `flying`;
	--   no_melee = the row says the engine refuses it while `engaged_in_melee`.
	-- Two entries are deliberately NOT air-gated and say so on the entry:
	-- Drop Sphere of Tepok (one of its two lord keys is a GROUND variant and
	-- the row carries no `grounded` flag) and Searing Torrent (a ground
	-- carrier - the user's own field note is that it behaves the same and
	-- recharges in melee, so melee is NOT required, only excluded).
	-- The four constants and the fast pass are defined once, above the
	-- evaluator; nothing here is per-entry.
	-- ======================================================================

	{ marker = "death_from_above", name = "Death from Above", trigger = "air_drop_on_infantry",
		badge = "zz_auto_badge_death_from_above",
		keys = { "wh2_dlc09_unit_abilities_death_from_above" },
		range_real = 10,
		air_only = true,
		no_melee = true,
		ox = 0, oy = 0 },

	{ marker = "drop_rocks", name = "Drop Rocks", trigger = "air_drop_on_infantry",
		badge = "zz_auto_badge_drop_rocks",
		keys = { "wh2_main_unit_abilities_drop_rocks",
			"wh2_dlc12_unit_abilities_drop_rocks_character",
			"wh2_dlc12_unit_abilities_drop_rocks_of_chotec",
			"wh2_dlc12_unit_abilities_drop_rocks_of_sundering" },
		range_real = 10,
		air_only = true,
		no_melee = true,
		ox = 0, oy = 0 },

		-- NOT air-gated: wh2_dlc12_lzd_cha_tiktaqto_0 is a GROUND variant and
		-- the row declares no `grounded` flag, so the engine itself allows it on
		-- the ground. The enemy-under-the-caster test still decides WHEN.
	{ marker = "drop_sphere_of_tepok", name = "Drop Sphere of Tepok", trigger = "air_drop_on_infantry",
		badge = "zz_auto_badge_drop_sphere_of_tepok",
		keys = { "wh2_dlc12_lord_abilities_drop_sphere_of_tepok",
			"wh2_dlc12_lord_abilities_drop_sphere_of_tepok_upgraded" },
		range_real = 10,
		air_only = false,
		no_melee = true,
		ox = 0, oy = 0 },

	{ marker = "fire_bombs", name = "Fire Bombs", trigger = "air_drop_on_infantry",
		badge = "zz_auto_badge_fire_bombs",
		keys = { "wh3_dlc25_unit_abilities_gyrobomber_fire_bomb",
			"wh3_dlc25_unit_abilities_thunderbarge_fire_bomb" },
		range_real = 10,
		air_only = true,
		no_melee = false,
		ox = 0, oy = 0 },

	{ marker = "gyrobomber_bomb", name = "Gyrobomber Bomb", trigger = "air_drop_on_infantry",
		badge = "zz_auto_badge_gyrobomber_bomb",
		keys = { "wh_main_unit_abilities_gyrobomber_bomb",
			"wh_main_unit_abilities_gyrocopter_bomb" },
		range_real = 10,
		air_only = true,
		no_melee = false,
		ox = 0, oy = 0 },

	{ marker = "gyrocopter_bomb_anti_large", name = "Gyrocopter Bomb (anti-large)", trigger = "air_drop_on_infantry",
		badge = "zz_auto_badge_gyrocopter_bomb_anti_large",
		keys = { "wh3_dlc25_unit_abilities_gyrocopter_bomb_anti_large" },
		range_real = 10,
		air_only = true,
		no_melee = false,
		ox = 0, oy = 0 },

	{ marker = "sky_junk_bomb", name = "Sky-Junk Bomb", trigger = "air_drop_on_infantry",
		badge = "zz_auto_badge_sky_junk_bomb",
		keys = { "wh3_main_unit_abilities_sky_junk_bomb" },
		range_real = 10,
		air_only = true,
		no_melee = false,
		ox = 0, oy = 0 },

	{ marker = "skyhammer_bomb", name = "Skyhammer Bomb", trigger = "air_drop_on_infantry",
		badge = "zz_auto_badge_skyhammer_bomb",
		keys = { "wh_dlc06_unit_abilities_skyhammer_bomb",
			"wh_dlc06_unit_abilities_skyhammer_fire_bomb" },
		range_real = 10,
		air_only = true,
		no_melee = false,
		ox = 0, oy = 0 },

	{ marker = "wake_of_fire", name = "Wake of Fire", trigger = "air_drop_on_infantry",
		badge = "zz_auto_badge_wake_of_fire",
		keys = { "wh2_main_unit_abilities_wake_of_fire" },
		range_real = 10,
		air_only = true,
		no_melee = true,
		ox = 0, oy = 0 },

		-- NOT air-gated: Knights of Immolation (Doom Knights) are a GROUND
		-- carrier. no_melee is the row's own `engaged_in_melee` flag: the user's
		-- field note is that it RECHARGES in melee, so melee is never required -
		-- only excluded, because the engine refuses the cast while fighting.
	{ marker = "searing_torrent", name = "Searing Torrent", trigger = "air_drop_on_infantry",
		badge = "zz_auto_badge_searing_torrent",
		keys = { "wh3_twa07_unit_abilities_searing_torrent" },
		range_real = 10,
		air_only = false,
		no_melee = true,
		ox = 0, oy = 0 },

		-- Empress Crowmen (Onyx Crowmen), 2 uses / 60 s, air-only (`grounded`).
	{ marker = "nan_gau_grenades", name = "Nan-Gau Grenades", trigger = "air_drop_on_infantry",
		badge = "zz_auto_badge_nan_gau_grenades",
		keys = { "wh3_dlc24_unit_abilities_nan_gau_grenades" },
		range_real = 10,
		air_only = true,
		no_melee = false,
		ox = 0, oy = 0 },

		-- The Deck Droppers unit set wh2_dlc11_cst_deck_droppers (all four
		-- variants carry `flying`); the same set carries Drop Rocks.
	{ marker = "undeath_from_above", name = "Undeath from Above", trigger = "air_drop_on_infantry",
		badge = "zz_auto_badge_undeath_from_above",
		keys = { "wh3_dlc29_unit_abilities_undeath_from_above" },
		range_real = 10,
		air_only = true,
		no_melee = true,
		ox = 0, oy = 0 },
}


-- Every key from the table above, for the ownership scan and the log.
-- THE CHARGE GATE (this round): every ability in this mod that carries MORE THAN
-- ONE use (unit_spec_abil.tsv `num_uses` > 1), with its own `recharge_time` in
-- seconds. The engine answers `can_perform_special_ability` = TRUE while such a
-- pool is EMPTY and still ACCEPTS the call (field log 2026-10-17: Nurgling Tide,
-- 3 uses / 90 s, accepted 55 casts in 108 s and its button sat greyed
-- 'selected_inactive' the whole time), so the 2 s guard alone re-spends the same
-- pool forever and the charge counter loops 3-2-1-3. The poll reads this table
-- into `ability.charge_s` and, after a successful cast, holds that pair for the
-- ability's OWN recharge - ONE use per charge cycle, so the pool is never drained
-- and no cast is silently swallowed. Single-use abilities are NOT listed: the
-- engine refuses those by itself (Eye of Khorne, 1 use, was refused on the very
-- next attempt in the same log).
local charge_gate = {
	hold_s = {
		-- ROUND 132 (patch 9.0.5): Aken-seth went from unlimited to 3 uses, 120 s recharge.
		["wh3_dlc29_weapon_abilities_aken_seth_the_staff_of_pain"] = 120,
		-- ROUND 130: Restock! - 4 uses, 60 s recharge.
		["wh2_dlc17_hero_abilities_more_powder_generic"] = 60,
		-- ROUND 123: the two 3-use hexes on the new enemy_melee trigger
		-- (unit_spec_abil.tsv num_uses = 3, recharge_time in seconds).
		["wh3_main_character_abilities_no_escape"] = 90,
		["wh3_dlc29_lord_abilities_transfix"] = 120,
		-- ROUND 107: Call of Tor and the air-drop family's multi-use pools.
		-- Only keys whose recharge is SLOWER than the 2 s guard are listed:
		-- the 0.1 s-recharge bombers (Gyrobomber 11 uses, Skyhammer 5, Wake
		-- of Fire 10, Gyrocopter 2) refill faster than the guard, so their
		-- pool can never drain and a hold would be dead weight.
		["wh3_twa07_spell_bound_call_of_tor"] = 90,
		-- ROUND 108: Warp Lightning Rod - 3 uses, 60 s recharge.
		["wh2_dlc16_unit_abilities_warp_lightning_rod"] = 60,
		["wh2_dlc12_lord_abilities_drop_sphere_of_tepok_upgraded"] = 5,
		["wh3_dlc25_unit_abilities_gyrobomber_fire_bomb"] = 3,
		["wh3_dlc25_unit_abilities_thunderbarge_fire_bomb"] = 3,
		["wh3_dlc24_unit_abilities_nan_gau_grenades"] = 60,
		["wh3_twa07_unit_abilities_searing_torrent"] = 60,
		["wh3_main_unit_abilities_sky_junk_bomb"] = 30,
		-- ROUND 106: the bombardment family's multi-use pools (num_uses > 1)
		["wh3_main_weapon_abilities_axe_of_tor"] = 90,
		["wh3_main_mount_bound_celestial_comet"] = 49,
		["wh3_main_mount_bound_celestial_lightning"] = 42,
		["wh_dlc07_item_abilities_chalice_of_potions"] = 120,
		["wh_dlc08_item_abilities_great_horn_of_dragon_ogre"] = 120,
		["wh3_dlc23_lord_abilities_flame_and_shadow"] = 90,
		["wh_dlc05_weapon_abilities_hawks_talon"] = 90,
		["wh2_dlc13_character_ability_ishas_rain"] = 120,
		["wh2_dlc10_spell_bound_lesser_doombolt"] = 90,
		["wh3_dlc29_unit_abilities_lightning_strike"] = 42,
		["wh_main_lord_abilities_lord_of_the_storm"] = 90,
		["wh3_dlc29_spell_bound_warp_lightning"] = 30,
		["wh3_dlc29_unit_abilities_meteor_strike"] = 49,
		["wh_main_spell_bound_piercing_bolts_of_burning"] = 120,
		["wh3_dlc25_character_abilities_pigeon_bomb"] = 120,
		["wh2_main_spell_bound_rod_of_the_storm"] = 90,
		["wh3_dlc20_item_abilities_rod_of_torment"] = 90,
		["wh2_dlc10_item_abilities_sceptre_of_stone"] = 90,
		["wh3_twa08_spell_bound_searing_doom"] = 60,
		["wh2_main_spell_bound_tome_of_furion"] = 60,
		["wh2_dlc17_spell_bound_urannons_thunderbolt"] = 90,
		["wh2_main_spell_bound_wand_of_the_kharaidon"] = 120,
		["wh3_main_weapon_abilities_the_traitors_sword"] = 90,
		["wh2_dlc11_lord_abilities_wraith_storm"] = 90,
		["wh2_dlc15_unit_abilities_arachneruption"] = 90,
		-- recharge_time 28 s
		["wh3_dlc29_spell_bound_undeath_sulekhim_hand_of_dust"] = 28,
		-- recharge_time 30 s
		["wh3_dlc29_spell_bound_invocation_of_nehek"] = 30,
		-- recharge_time 31 s
		["wh3_dlc29_spell_bound_undeath_morkharn_breath_of_darkness"] = 31,
		["wh3_dlc29_spell_bound_undeath_morkharn_breath_of_darkness_upgraded"] = 31,
		-- recharge_time 43 s
		["wh3_main_spell_slaanesh_hysterical_frenzy_bound"] = 43,
		-- recharge_time 44 s
		["wh3_dlc24_unit_bound_missile_mirror"] = 44,
		-- recharge_time 46 s
		["wh3_dlc29_spell_bound_okkams_mindrazor"] = 46,
		-- recharge_time 47 s
		["wh3_dlc29_spell_bound_curse_of_years"] = 47,
		-- recharge_time 60 s
		["wh2_dlc09_character_abilities_restore"] = 60,
		["wh2_dlc11_lord_abilities_power_siphon"] = 60,
		["wh2_dlc15_hero_abilities_mither"] = 60,
		["wh2_dlc15_unit_abilities_mimic_cold_blooded"] = 60,
		["wh2_dlc16_spell_bound_earth_blood"] = 60,
		["wh2_main_lord_abilities_potion_of_charoi"] = 60,
		["wh2_main_spell_bound_radiant_gem_of_hoeth"] = 60,
		["wh2_main_spell_bound_the_seerstaff_of_saphery"] = 60,
		["wh2_main_unit_abilities_revivification_crystal"] = 60,
		["wh3_dlc23_character_abilities_reforge"] = 60,
		["wh3_dlc25_character_abilities_surprise_squig"] = 60,
		["wh3_dlc26_character_abilities_inventory_of_hatchlings_upgraded"] = 60,
		["wh3_dlc26_lord_abilities_blood_sacrifice"] = 60,
		["wh3_dlc27_spell_bound_acquiescence"] = 60,
		["wh3_dlc27_spell_bound_enfeebling_foe"] = 60,
		["wh3_main_character_abilities_silence_the_prey"] = 60,
		["wh3_main_item_abilities_gruts_sickle"] = 60,
		["wh3_main_lord_abilities_blight_swarm"] = 60,
		["wh3_main_spell_bound_cascading_fire_cloak"] = 60,
		["wh3_main_spell_bound_earth_blood"] = 60,
		["wh3_main_spell_bound_enfeebling_foe"] = 60,
		["wh3_main_spell_bound_harmonic_convergence"] = 60,
		["wh3_main_spell_bound_phas_protection"] = 60,
		["wh3_main_spell_bound_plague_of_rust"] = 60,
		["wh3_twa08_spell_bound_enfeebling_foe_keeper_of_secrets_ror"] = 60,
		["wh_dlc06_unit_abilities_maternal_instinct"] = 60,
		["wh_dlc08_item_abilities_arachnarok_eggs"] = 60,
		["wh_main_spell_bound_book_of_arkhan"] = 60,
		-- recharge_time 90 s
		["wh2_dlc09_character_abilities_stay_here_ill_get_help"] = 90,
		["wh2_dlc09_lord_abilities_the_liber_mortis"] = 90,
		["wh2_dlc10_lord_abilities_gaze_of_khaine"] = 90,
		["wh2_dlc10_spell_bound_word_of_pain"] = 90,
		["wh2_dlc11_lord_abilities_spearfishers_net"] = 90,
		["wh2_dlc12_unit_abilities_shield_of_chaqua"] = 90,
		["wh2_dlc13_character_abilities_patch_up"] = 90,
		["wh2_dlc13_lord_abilities_hunters_snare"] = 90,
		["wh2_dlc13_lord_abilities_hunters_trap"] = 90,
		["wh2_dlc13_lord_abilities_oil_flask"] = 90,
		["wh2_dlc15_lord_abilities_dont_even_try_it"] = 90,
		["wh2_dlc15_lord_abilities_fermented_fungi"] = 90,
		["wh2_dlc15_unit_abilities_mimic_feint_and_riposte"] = 90,
		["wh2_dlc15_unit_abilities_mimic_grand_hammer_of_faith"] = 90,
		["wh2_dlc16_character_abilities_blight_of_terrors"] = 90,
		["wh2_dlc16_character_abilities_muster_of_malevolents"] = 90,
		["wh2_dlc16_character_abilities_pageant_of_shrikes"] = 90,
		["wh2_dlc16_lord_abilities_roused_to_wrath_2"] = 90,
		["wh2_dlc16_spell_bound_flesh_to_stone"] = 90,
		["wh2_dlc17_spell_bound_shield_of_thorns"] = 90,
		["wh2_main_character_abilities_witchbrew"] = 90,
		["wh2_main_item_abilities_starwood_staff"] = 90,
		["wh2_main_spell_bound_black_staff"] = 90,
		["wh2_main_spell_bound_embers_of_the_phoenix"] = 90,
		["wh2_main_spell_bound_whip_of_agony"] = 90,
		["wh3_dlc23_bound_abilities_breath_of_hatred"] = 90,
		["wh3_dlc23_character_abilities_breath_of_hatred"] = 90,
		["wh3_dlc24_hero_abilities_znarkharjas_ward"] = 90,
		["wh3_dlc24_item_abilities_book_of_secrets"] = 90,
		["wh3_dlc24_unit_abilities_pack_trap"] = 90,
		["wh3_dlc25_character_abilities_children_of_the_forest"] = 90,
		["wh3_dlc26_lord_abilities_gorger_onslaught_upgraded"] = 90,
		["wh3_dlc26_unit_abilities_eat_da_runts"] = 90,
		["wh3_dlc27_spell_bound_runecaller_death_doom_and_darkness"] = 90,
		["wh3_dlc27_unit_abilities_elfish_healing_herbs"] = 90,
		["wh3_dlc29_hero_active_nurgling_birth"] = 90,
		["wh3_dlc29_hero_active_nurgling_birth_upgraded"] = 90,
		["wh3_dlc29_item_abilities_enhanced_skavenbrew"] = 90,
		["wh3_main_character_abilities_locus_of_fecundity"] = 90,
		["wh3_main_character_abilities_locus_of_transmogrification"] = 90,
		["wh3_main_character_abilities_salyaks_lullaby"] = 90,
		["wh3_main_item_abilities_alchemists_elixir_of_iron_skin"] = 90,
		["wh3_main_item_abilities_alchemists_elixir_of_puissance"] = 90,
		["wh3_main_item_abilities_void_pendulum"] = 90,
		["wh3_main_lord_abilities_gaze_of_fate"] = 90,
		["wh3_main_lord_abilities_nurgling_tide"] = 90,
		["wh_dlc04_spell_bound_net_of_amyntok"] = 90,
		["wh_dlc05_character_abilities_prey_of_anath_raema"] = 90,
		["wh_dlc05_spell_bound_shield_of_thorns"] = 90,
		["wh_dlc08_spell_bound_death_doom_and_darkness"] = 90,
		["wh_main_item_abilities_forbidden_rod"] = 90,
		["wh_main_spell_bound_staff_of_damnation"] = 90,
		["wh_pro04_unit_abilities_warp_gaze"] = 90,
		-- recharge_time 120 s
		["wh2_dlc09_weapon_abilities_tomb_blade_of_arkhan"] = 120,
		["wh2_dlc10_character_abilities_entangle"] = 120,
		["wh2_dlc10_item_abilities_star_of_avelorn"] = 120,
		["wh2_dlc11_character_abilities_beyond_the_realm"] = 120,
		["wh2_dlc11_character_abilities_ghosts_of_the_past_1"] = 120,
		["wh2_dlc11_character_abilities_ghosts_of_the_past_2"] = 120,
		["wh2_dlc11_character_abilities_sacrilege"] = 120,
		["wh2_dlc11_item_abilities_captain_roths_moondial"] = 120,
		["wh2_dlc15_character_abilities_sausage_busta"] = 120,
		["wh2_dlc15_lord_abilities_dragonhorn"] = 120,
		["wh2_dlc16_lord_abilities_remouldered"] = 120,
		["wh2_dlc17_spell_bound_savage_dominion"] = 120,
		["wh3_dlc20_item_abilities_pestilent_potions"] = 120,
		["wh3_dlc23_item_abilities_ancestral_vengeance"] = 120,
		["wh3_dlc23_lord_abilities_sadistic_snare"] = 120,
		["wh3_dlc24_character_abilities_watched_by_the_watcher"] = 120,
		["wh3_dlc25_character_abilities_kettles_call"] = 120,
		["wh3_dlc25_weapon_abilities_makaissons_persuader"] = 120,
		["wh3_dlc26_character_abilities_inventory_of_hatchlings"] = 120,
		["wh3_dlc26_character_abilities_spider_web_attack"] = 120,
		["wh3_dlc27_character_abilities_the_black_tongue"] = 120,
		["wh3_dlc27_item_abilities_elixir_of_damnation"] = 120,
		["wh3_dlc27_item_abilities_null_stone"] = 120,
		["wh3_dlc29_character_abilities_eternal_vigour"] = 120,
		["wh3_dlc29_item_abilities_doom_glaive"] = 120,
		["wh3_dlc29_item_abilities_warpstiletto"] = 120,
		["wh3_dlc29_item_abilities_warpstone_tokens"] = 120,
		["wh3_dlc29_lord_abilities_verminous_fury"] = 120,
		["wh3_dlc29_lord_abilities_warpstone_addiction"] = 120,
		["wh3_main_daemon_arms_abilities_gate_of_chaos"] = 120,
		["wh3_main_daemon_arms_abilities_gate_of_chaos_upgraded"] = 120,
		["wh3_main_item_abilities_fistful_of_laurels"] = 120,
		["wh3_main_lord_abilities_virulent_contagion"] = 120,
		["wh3_main_lord_abilities_virulent_contagion_upgraded"] = 120,
		["wh3_main_spell_bound_ancestral_warriors"] = 120,
		["wh3_pro12_hero_abilities_prey_of_the_blood_god"] = 120,
		["wh_dlc03_item_abilities_skull_of_rarkos"] = 120,
		["wh_dlc04_item_abilities_the_liber_noctus"] = 120,
		-- recharge_time 180 s
		["wh2_dlc15_item_abilities_armour_of_caledor"] = 180,
	},
	until_tick = {},   -- ui id -> (marker -> the tick before which the next use is not due)
}

-- THE IN-FLIGHT GATE (this round, the user's Nurgling Tide theory tested).
--
-- WHAT THE DATA SAYS: Nurgling Tide's own row (unit_spec_abil.tsv) declares
-- `wind_up_time` 3.0 s and NO other activation field - `activation_effect` is
-- empty, there is no `cast_time` column and phase_junc/phases carry no row for
-- this key - so the order-to-effect window the engine declares is 3 s. The
-- user's "around four seconds" is that 3 s wind-up plus the order delivery and
-- the visible cast, and BOTH numbers are longer than the 2 s guard, which is
-- the part that matters: the mod re-issued the call while the previous
-- activation was still resolving.
--
-- WHY THAT IS A CANCEL: `battle_unitcontroller:perform_special_ability` is
-- documented as issuing an ORDER ("Issues an order to the units associated
-- with this unitcontroller to perform the supplied special ability"), and the
-- API's queued twin `perform_special_ability_q` is documented as "Queued orders
-- start when the current order completes" - i.e. the NON-queued form replaces
-- the unit's current order. A second order arriving 2 s into a 3 s wind-up
-- therefore replaces the first before its effect lands. (The field log cannot
-- show the cancel directly - it only shows 55 ACCEPTED calls at a dead-even
-- 2.0 s cadence - but it is consistent: no summon was ever confirmed and the
-- three charges spent at 67/69/71 s prove only that three activations STARTED,
-- because a use is deducted when the cast begins, not when the effect lands.)
--
-- THE FIX: after a successful cast, a pair whose ability declares a wind-up is
-- held for that wind-up PLUS 2 s of slack (the order delivery plus the
-- activation landing), and never less than the ordinary guard. The hold is a
-- TIMEOUT, not an observation: there is no script read of a cast's progress
-- (no per-unit charge/cooldown/active read exists - established over earlier
-- rounds), so "the effect landed" cannot be observed, and the data-derived
-- wind-up plus slack is the honest window.
--
-- Generality: EVERY ability in this mod whose own row declares wind_up_time > 0
-- is listed (134 keys after round 121 removed 2 army-bar keys); entries with wind_up_time = 0 keep the plain 2 s guard
-- unchanged, because there is no activation to protect.
local cast_gate = {
	wind_up_s = {
		-- ROUND 106: the bombardment family's wind-up times (wind_up_time > 0)
		["wh2_dlc10_item_bound_assault_of_stone"] = 3,
		["wh3_main_weapon_abilities_axe_of_tor"] = 3,
		["wh3_main_mount_bound_celestial_comet"] = 5,
		["wh3_main_mount_bound_celestial_lightning"] = 3,
		["wh_dlc07_item_abilities_chalice_of_potions"] = 5,
		["wh3_main_spell_bound_comet_of_casandora"] = 5,
		["wh3_dlc23_lord_abilities_flame_and_shadow"] = 3,
		["wh_dlc05_weapon_abilities_hawks_talon"] = 3,
		["wh2_dlc13_character_ability_ishas_rain"] = 3,
		["wh2_dlc17_spell_bound_urannons_thunderbolt_upgraded"] = 3,
		["wh2_dlc10_spell_bound_lesser_doombolt"] = 3,
		["wh3_dlc29_unit_abilities_lightning_strike"] = 3,
		["wh_main_lord_abilities_lord_of_the_storm"] = 1,
		["wh3_dlc29_spell_bound_warp_lightning"] = 1,
		["wh3_dlc29_unit_abilities_meteor_strike"] = 5,
		["wh3_dlc25_lord_abilities_nemesis_crown"] = 6,
		["wh2_main_spell_bound_rod_of_the_storm"] = 3,
		["wh3_dlc20_item_abilities_rod_of_torment"] = 3,
		["wh2_dlc10_item_abilities_sceptre_of_stone"] = 5,
		["wh3_twa08_spell_bound_searing_doom"] = 1,
		["wh3_dlc20_spell_bound_slicing_shards"] = 5,
		["wh3_main_spell_slaanesh_slicing_shards_bound"] = 5,
		["wh_dlc05_weapon_abilities_the_bow_of_loren"] = 3,
		["wh2_main_spell_bound_tome_of_furion"] = 5,
		["wh2_dlc17_spell_bound_urannons_thunderbolt"] = 3,
		["wh2_main_spell_bound_wand_of_the_kharaidon"] = 5,
		["wh2_dlc11_lord_abilities_wraith_storm"] = 3,
		["wh_main_spell_bound_soulfire"] = 1,
		["wh_dlc04_spell_bound_soulfire_upgraded"] = 1,
		-- ROUND 107: Call of Tor (1 s) and Sky-Junk Bomb (1 s). Every other
		-- air-drop declares wind_up_time = 0 and keeps the plain guard.
		["wh3_twa07_spell_bound_call_of_tor"] = 1,
		["wh2_dlc16_unit_abilities_warp_lightning_rod"] = 1,
		["wh3_main_unit_abilities_sky_junk_bomb"] = 1,
		-- wind_up_time 0.5 s
		["wh3_dlc29_ability_bound_prayer_winters_chill"] = 0.5,
		["wh3_dlc29_spell_bound_prayer_ferocious_battle_howl"] = 0.5,
		["wh3_dlc29_spell_bound_prayer_ferocious_fury_of_ulric"] = 0.5,
		["wh3_dlc29_spell_bound_prayer_ferocious_winters_chill"] = 0.5,
		["wh3_dlc29_spell_bound_prayer_fury_of_ulric"] = 0.5,
		["wh3_dlc29_spell_bound_prayer_winters_chill"] = 0.5,
		-- wind_up_time 1 s
		["wh2_dlc15_character_abilities_sausage_busta"] = 1,
		["wh2_dlc16_item_abilities_dreaming_cloak_i"] = 1,
		["wh2_dlc16_item_abilities_dreaming_cloak_ii"] = 1,
		["wh2_dlc16_item_abilities_dreaming_cloak_iii"] = 1,
		["wh2_dlc16_lord_abilities_roused_to_wrath"] = 1,
		["wh2_dlc16_lord_abilities_roused_to_wrath_2"] = 1,
		["wh3_dlc23_spell_bound_enfeebling_foe"] = 1,
		["wh3_dlc23_unit_abilities_more_power"] = 1,
		["wh3_dlc24_hero_abilities_koldunjas_spirit"] = 1,
		["wh3_dlc24_unit_abilities_howl_of_the_great_beast"] = 1,
		["wh3_dlc25_unit_abilities_full_power"] = 1,
		["wh3_dlc25_weapon_abilities_sword_of_filth"] = 1,
		["wh3_dlc26_lord_abilities_gorger_onslaught_upgraded"] = 1,
		["wh3_dlc27_spell_bound_acquiescence"] = 1,
		["wh3_dlc27_spell_bound_enfeebling_foe"] = 1,
		["wh3_dlc27_spell_bound_runecaller_death_doom_and_darkness"] = 1,
		["wh3_dlc29_character_active_mark_of_the_monster"] = 1,
		["wh3_dlc29_hero_abilities_whispering_mist"] = 1,
		["wh3_dlc29_hero_active_dispatch_the_swarm_attack"] = 1,
		["wh3_dlc29_hero_active_dispatch_the_swarm_attack_upgraded"] = 1,
		["wh3_dlc29_hero_active_dispatch_the_swarm_protect"] = 1,
		["wh3_dlc29_hero_active_dispatch_the_swarm_protect_upgraded"] = 1,
		["wh3_dlc29_hero_active_nurgling_birth"] = 1,
		["wh3_dlc29_hero_active_nurgling_birth_upgraded"] = 1,
		["wh3_dlc29_item_active_ottos_scythe"] = 1,
		["wh3_dlc29_lord_abilities_doom_lord"] = 1,
		["wh3_dlc29_spell_bound_curse_of_years"] = 1,
		["wh3_dlc29_spell_bound_invocation_of_nehek"] = 1,
		["wh3_dlc29_spell_bound_undeath_morkharn_breath_of_darkness"] = 1,
		["wh3_dlc29_spell_bound_undeath_morkharn_breath_of_darkness_upgraded"] = 1,
		["wh3_dlc29_spell_bound_undeath_sulekhim_hand_of_dust"] = 1,
		["wh3_main_character_abilities_flame_incarnate"] = 1,
		["wh3_main_lord_abilities_gorger_onslaught"] = 1,
		["wh3_main_spell_bound_cascading_fire_cloak"] = 1,
		["wh3_main_spell_bound_earth_blood"] = 1,
		["wh3_main_spell_bound_enfeebling_foe"] = 1,
		["wh3_main_spell_bound_harmonic_convergence"] = 1,
		["wh3_main_spell_bound_phas_protection"] = 1,
		["wh3_main_spell_bound_plague_of_rust"] = 1,
		["wh3_twa08_spell_bound_enfeebling_foe_keeper_of_secrets_ror"] = 1,
		-- wind_up_time 1.5 s
		["wh2_dlc14_lord_abilities_tzarkan_snikch"] = 1.5,
		-- wind_up_time 1.9 s
		["wh2_dlc13_lord_abilities_oil_flask"] = 1.9,
		-- wind_up_time 3 s
		["wh2_dlc11_character_abilities_beyond_the_realm"] = 3,
		["wh2_dlc11_character_abilities_ghosts_of_the_past_0"] = 3,
		["wh2_dlc11_character_abilities_ghosts_of_the_past_1"] = 3,
		["wh2_dlc11_character_abilities_ghosts_of_the_past_2"] = 3,
		["wh2_dlc11_character_abilities_sacrilege"] = 3,
		["wh2_dlc11_item_abilities_captain_roths_moondial"] = 3,
		["wh2_dlc14_lord_abilities_tzarkan"] = 3,
		["wh2_dlc14_lord_abilities_tzarkan_mp"] = 3,
		["wh2_dlc14_lord_abilities_tzarkan_spite"] = 3,
		["wh2_dlc14_lord_abilities_tzarkan_spite_mp"] = 3,
		["wh2_dlc16_spell_bound_death_frenzy"] = 3,
		["wh2_dlc16_spell_bound_vampires_lesser_raise_dead"] = 3,
		["wh2_dlc17_rune_abilities_master_rune_of_breaking"] = 3,
		["wh2_dlc17_rune_abilities_master_rune_of_slowness"] = 3,
		["wh2_dlc17_rune_abilities_master_rune_of_speed"] = 3,
		["wh2_dlc17_rune_abilities_rune_of_breaking"] = 3,
		["wh2_dlc17_rune_abilities_rune_of_slowness"] = 3,
		["wh2_dlc17_rune_abilities_rune_of_speed"] = 3,
		["wh2_dlc17_spell_bound_shield_of_thorns"] = 3,
		["wh2_main_unit_abilities_revivification_crystal"] = 3,
		["wh3_dlc23_hero_abilities_get_tha_gitz!"] = 3,
		["wh3_dlc23_item_abilities_rune_of_thungni"] = 3,
		["wh3_dlc24_hero_abilities_vorozhejas_foresight"] = 3,
		["wh3_dlc24_lord_abilities_gulyas"] = 3,
		["wh3_dlc24_unit_abilities_mark_of_yin"] = 3,
		["wh3_dlc24_unit_bound_missile_mirror"] = 3,
		["wh3_dlc29_hero_active_tendrils_of_the_sea"] = 3,
		["wh3_dlc29_lord_abilities_gaze_of_usirian"] = 3,
		["wh3_dlc29_lord_abilities_hellish_vigour"] = 3,
		["wh3_dlc29_lord_abilities_hellish_vigour_upgraded"] = 3,
		["wh3_dlc29_lord_abilities_raise_legion"] = 3,
		["wh3_dlc29_lord_abilities_raise_legion_upgraded"] = 3,
		["wh3_dlc29_lord_abilities_the_awakening"] = 3,
		["wh3_dlc29_vmp_mon_morghast_archai_summon"] = 3,
		["wh3_main_character_abilities_guardian_call"] = 3,
		["wh3_main_character_abilities_guardian_call_ii"] = 3,
		["wh3_main_character_abilities_guardian_call_iii"] = 3,
		["wh3_main_lord_abilities_nurgling_tide"] = 3,
		["wh3_main_spell_slaanesh_hysterical_frenzy_bound"] = 3,
		["wh_dlc04_spell_bound_net_of_amyntok"] = 3,
		["wh_dlc06_rune_abilities_master_rune_of_negation"] = 3,
		["wh_dlc06_rune_abilities_master_rune_of_oath_and_steel"] = 3,
		["wh_dlc06_unit_abilities_marked_by_ulthar"] = 3,
		["wh_main_rune_abilities_rune_of_negation"] = 3,
		["wh_main_rune_abilities_rune_of_oath_and_steel"] = 3,
		-- wind_up_time 4.5 s
		["wh2_dlc17_unit_abilities_primeval_roar"] = 4.5,
		-- wind_up_time 5 s
		["wh2_dlc17_lord_abilities_rune_of_doom"] = 5,
		["wh2_dlc17_spell_bound_savage_dominion"] = 5,
		["wh3_dlc20_spell_bound_fleshy_abundance"] = 5,
		["wh3_dlc23_item_abilities_ancestral_vengeance"] = 5,
		["wh3_dlc25_character_abilities_kettles_call"] = 5,
		["wh3_dlc25_character_abilities_tallymans_blades"] = 5,
		["wh3_dlc25_character_abilities_tallymans_blades_2"] = 5,
		["wh3_dlc26_hero_abilities_savage_predators"] = 5,
		["wh3_dlc26_spell_bound_trollguts"] = 5,
		["wh3_dlc27_item_abilities_mask_of_the_merlord"] = 5,
		["wh3_dlc27_spell_bound_transformation_of_kadon"] = 5,
		["wh3_dlc29_spell_bound_the_dreaded_thirteenth"] = 5,
		["wh3_dlc29_spell_bound_the_dreaded_thirteenth_1"] = 5,
		["wh3_dlc29_spell_bound_the_dreaded_thirteenth_thanquol"] = 5,
		["wh3_dlc29_spell_bound_the_dreaded_thirteenth_thanquol_1"] = 5,
		["wh3_dlc29_unit_abilities_battle_of_wills"] = 5,
		["wh3_main_character_abilities_gate_of_khorne"] = 5,
		["wh3_main_character_abilities_gate_of_nurgle"] = 5,
		["wh3_main_character_abilities_gate_of_slaanesh"] = 5,
		["wh3_main_character_abilities_gate_of_tzeentch"] = 5,
		["wh3_main_character_abilities_greater_gate_of_khorne"] = 5,
		["wh3_main_character_abilities_greater_gate_of_nurgle"] = 5,
		["wh3_main_character_abilities_greater_gate_of_slaanesh"] = 5,
		["wh3_main_character_abilities_greater_gate_of_tzeentch"] = 5,
		["wh3_main_character_abilities_locus_of_transmogrification"] = 5,
		["wh3_main_daemon_arms_abilities_gate_of_chaos"] = 5,
		["wh3_main_daemon_arms_abilities_gate_of_chaos_upgraded"] = 5,
		["wh3_main_item_abilities_bloodstone"] = 5,
		["wh3_main_item_abilities_the_portalglyph"] = 5,
		["wh3_main_spell_bound_ancestral_warriors"] = 5,
		["wh3_pro12_hero_abilities_karanaks_howl"] = 5,
		["wh_dlc01_weapon_abilities_sword_of_change"] = 5,
		["wh_dlc05_weapon_abilities_stave_of_ruinous_corruption"] = 5,
		["wh_dlc06_unit_abilities_maternal_instinct"] = 5,
		["wh_main_spell_bound_bironas_timewarp"] = 5,
		-- wind_up_time 6 s
		["wh2_dlc15_lord_abilities_dragonhorn"] = 6,
	},
	until_tick = {},   -- ui id -> (marker -> the tick before which a resolving cast may not be re-issued)
	logged = {},       -- ui id -> (marker -> true once the gate has spoken for this pair)
	-- ROUND 107: THE PER-UNIT SERIALISATION WINDOW. One window per UNIT (not
	-- per pair): armed by every successful cast, it blocks a DIFFERENT
	-- ability on the same unit until it closes.
	unit_until = {},   -- ui id -> the tick before which no OTHER ability may be issued
	unit_marker = {},  -- ui id -> the marker of the cast that armed that window
	unit_logged = {},  -- ui id -> (marker -> true once the wait has been said this episode)
}
local ALL_ABILITY_KEYS = {}
for _, ability in ipairs(ABILITIES) do
	for _, key in ipairs(ability.keys) do
		ALL_ABILITY_KEYS[#ALL_ABILITY_KEYS + 1] = key
	end
end

-- THE STATIC KEY -> MARKER MAP (item 1.3): every database key listed in the
-- table above, mapped to its ability's short marker, built once at load. It is
-- what turns a unit's cached owned keys (owned_keys_by_unit, section 2) into
-- the short list of abilities that unit can actually carry - the poll's
-- per-unit ability loop (section 8) iterates that list instead of the whole
-- table. Built from the SAME keys the scan matches on, so it can never drift.
local marker_by_key = {}
for _, ability in ipairs(ABILITIES) do
	for _, key in ipairs(ability.keys) do
		marker_by_key[key] = ability.marker
	end
end

-- THE STATIC MARKER -> ENTRY MAP (item 3.1): the ABILITIES entry behind each
-- marker, built once at load. It replaces ability_for's per-call walk of the
-- WHOLE table with ONE table read, so every badge / letter / active-set
-- lookup is O(1) instead of O(entries). INVARIANT: it is built AFTER the
-- ABILITIES table is fully populated (it is - the table above never changes),
-- and ability_by_marker[entry.marker] == entry for EVERY entry; the harness
-- asserts exactly that, because a mismatch would silently drop a badge.
local ability_by_marker = {}
for _, ability in ipairs(ABILITIES) do
	ability_by_marker[ability.marker] = ability
end

-- THE STATIC BADGE-ID -> ENTRY MAP (item 3.1, audit): the same idea for the
-- click router's badge lookup - a badge id is unique per entry, built at load
-- (after ABILITIES, same invariant), so ability_for_badge is one read too.
local ability_by_badge = {}
for _, ability in ipairs(ABILITIES) do
	ability_by_badge[ability.badge] = ability
end

-- THE STATIC KEY MEMBERSHIP SET (item 3.1): the SAME keys as ALL_ABILITY_KEYS
-- (above), but as a set, so "is this engine key one of ours?" is ONE table
-- read instead of a walk of the array. The ARRAY is kept for the ordered
-- iterations that need it (the log and the ordered fallback). INVARIANT:
-- built AFTER ABILITIES is fully populated; EVERY key of EVERY entry is in
-- this set - the harness asserts it, because a missing key would silently
-- miss an owned ability.
local ALL_ABILITY_KEYS_SET = {}
for _, ability in ipairs(ABILITIES) do
	for _, key in ipairs(ability.keys) do
		ALL_ABILITY_KEYS_SET[key] = true
	end
end

-- The ABILITIES entry behind a marker, and behind a badge id (the click
-- router works in badge ids).
local function ability_for(marker)
	-- item 3.1: O(1) - the load-time map, never a walk of the table.
	return ability_by_marker[marker]
end

local function ability_for_badge(badge_id)
	-- item 3.1 (audit): O(1) - the load-time badge-id map.
	return ability_by_badge[badge_id]
end

-- Which situations count as "fire now".
-- Round 5 ran with BOTH on (deliberately, to get a positive result). You saw it
-- fire while merely running and while already fighting, which is exactly what
-- that configuration asked for. It was then tightened to charging only.
-- THIS ROUND (user-approved): BOTH are ON again - Deadly Onslaught has a
-- component that is useful in melee, so it fires on the proven charge window
-- OR once the unit is already fighting. The two arms can never both hold on
-- one evaluation (a charging unit is not yet in melee - see measure_charge),
-- so one situation never fires twice; the engine cooldown and the existing
-- cooldown-hold back-off govern the repeats.
local FIRE_ON_CHARGE = true
local FIRE_ON_MELEE  = true    -- the user-approved in-melee arm (this round)

-- A charge is an ATTACK order on an enemy that is about to CONNECT - not simply
-- "moving fast", and not the instant the attack order is given. The engine
-- exposes no "is charging", so it is inferred from five signals:
--
--   1. is_moving_fast()      - the unit is running (necessary, not sufficient)
--   2. not is_in_melee()     - it has not made contact yet
--   3. current_target()      - it has an enemy unit as its target
--   4. ordered_position()    - the documentation: "if the unit is attacking, as
--                              opposed to moving, then this will return the
--                              current position of the unit". So position() and
--                              ordered_position() are near-equal while charging
--                              a unit and far apart while walking to a spot.
--                              This is what separates a charge from a run.
--   5. distance to the target, and the estimated time until contact - so the
--      ability is spent on the charge that is about to land, not on a charge
--      ordered from the far side of the battlefield.
--
-- ROUND 7 CORRECTION - signal 4 DOES NOT WORK.
-- The documentation claims that while the unit is ATTACKING, ordered_position()
-- returns its current position. The round-7 log disproves it: during a charge
-- the gap grew steadily from 17 m to 322 m, tracking how far the unit had
-- travelled since the order was given. So it measures "how long ago you
-- clicked", not "is this an attack". It blocked every genuine charge and passed
-- only orders given at close range - which is exactly what you saw. It is now
-- logged for diagnostics only and takes NO part in the decision. The real
-- attack-versus-move signal is simply "does the unit have a target at all".
local CHARGE_MIN_DISTANCE_M    = 12     -- a charge needs a run-up
local CHARGE_MAX_DISTANCE_M    = 60     -- ...but not the length of the map
local CHARGE_TIME_TO_CONTACT_S = 4      -- fire when impact is this close

-- GLORIOUS DEATH'S TRIGGER RANGE (this round) - THE STANDING 70% RULE.
-- REAL range 55.0000 m = effect_range (unit_spec_abil.tsv,
-- wh3_dlc25_lord_abilities_glorious_death) - the ability's own aura.
-- 55 * 0.70 = 38.5 -> 38 m (FLOORED, FOURTH.RANGE_FRACTION). The gate below
-- offers, and re-checks just before the cast, an in-melee Slayer ally only
-- when the owner is within GLORIOUS_DEATH_RANGE_M metres of it. ONE place to
-- tune the gate. (HISTORY: harness 87 shipped a FIELD-TUNED 25 m here because
-- the 55 m aura fired too early; the user then ruled the 70% rule ABSOLUTE -
-- "...No exceptions." - so 25 m was REPLACED by 38 m at his direction.)
local GLORIOUS_DEATH_RANGE_M = 38

-- How often, in milliseconds, we look at the battlefield. 250 ms = 4x a second.
local POLL_MS = 250

-- THE SHORT GUARD - the short safety brake, in seconds, per (unit, ability):
-- no pair may attempt twice inside this window. The readiness gate (the
-- engine's own can_perform check, section 4) is the real brake now - there
-- are NO 60/90 s timers anywhere any more.
local GUARD_SECONDS = 2

-- THE IN-FLIGHT SLACK (this round, the Nurgling Tide theory): after a
-- successful cast, a pair whose ability declares a wind-up is held for that
-- wind-up PLUS this many seconds - the order has to reach the engine (up to one
-- poll) and the activation has to land (the wind-up itself) before a second
-- order may replace it. 2 s is one poll of delivery plus one poll of margin on
-- top of a whole wind-up, which puts Nurgling Tide's 3.0 s activation window
-- behind a 5 s hold and a 5.0 s wind-up behind a 7 s hold.
local IN_FLIGHT_SETTLE_SECONDS = 2

-- THE PER-UNIT SERIALISATION STAGGER (round 107). The engine allows ONE
-- special ability in flight per unit: a second order REPLACES the first
-- during its wind-up while the replaced cast's use is still spent (the
-- Moondial / Wraith Storm pair in the 2026-10-17 field log - Moondial's
-- 120 s recharge was consumed and its effect never landed). So a unit
-- that has just cast may not be ordered to cast a DIFFERENT ability until
-- its window closes: the wind-up it declared + IN_FLIGHT_SETTLE_SECONDS,
-- never less than this stagger. 2.5 s is ten polls - two ready abilities
-- fire in sequence, never together, and a buff is barely delayed.
-- It is a FIELD of the FOURTH bag, not a chunk local: the main chunk sits
-- exactly at Lua's 200-local ceiling.
-- (The VALUE itself is set beside FOURTH.RANGE_FRACTION, below: the
-- FOURTH bag does not exist yet at this point in the chunk.)

-- THE COOLDOWN-HOLD BACK-OFF (this round). RESEARCH, FIRST: there is NO
-- per-unit engine read of a special ability's cooldown / readiness / active
-- state. The API dump (battle_unit.lua) offers exactly ONE read -
-- can_perform_special_ability - and the live log proves it answers TRUE while
-- the engine is refusing the fire with "does not support this special
-- ability"; the only other cooldown entry in the whole API is
-- battle_unitcontroller:reset_ability_cooldown, a WRITE. The dial-button
-- state (INVENTORY dumps) reports 'active' for our buttons even during the
-- refusal, and it belongs to the SELECTED unit only, so it cannot cover an
-- attempt for a non-selected firing unit. So the mod cannot KNOW a pair is on
-- cooldown before it tries - it can only LEARN it from the engine's own
-- refusal.
--
-- WHAT THIS DOES: the first cooldown refusal of an episode still speaks (one
-- coalesced line, not the old four). A REPEATED refusal backs that pair off
-- HOLD_SECONDS instead of the 2 s guard, and every repeat after the first is
-- logged NOTHING (no ATTEMPT, no can_perform, no REJECTED): an ability on a
-- long cooldown costs a handful of silent probes instead of a REJECTED line
-- every 2 s. A refusal clears the episode only by an ACCEPTED fire - and a
-- probe that DOES fire is always reported in full (a fire is never
-- suppressed).
local HOLD_SECONDS = 8

-- THE HARD BOUND (this round). A hold is a SKIP: nothing may sit out forever
-- because of a stuck flag, a stale read or a mis-set timer. However long a
-- pair has been held, an attempt is forced once the hold has lasted
-- MAX_HOLD_SECONDS - so a permanently "cooling" pair still probes (and, if
-- the engine then allows it, still fires).
local MAX_HOLD_SECONDS = 20

-- How often, in polls, the cheap IDENTITY re-check runs for a unit we have
-- not yet found the ability on: 16 x 250 ms = every 4 seconds. The check
-- reads ONE cheap engine value (the identity watch below); the FULL scan it
-- used to run here now happens only when that value changes, plus the slow
-- fallback beneath this constant.
local REDETECT_EVERY_N_POLLS = 16    -- 16 x 250 ms = every 4 seconds

-- THE IDENTITY WATCH (this build, item 3.4). The 4 s re-check above no longer
-- re-runs the full scan: for a unit with nothing of ours, the poll reads ONE
-- cheap engine value - its identity, battle_unit:type() (battle_unit.lua:
-- "Returns the unit type of the unit, from the land_units table") - and
-- re-scans ONLY when that value CHANGES. That is what catches a
-- transformation or a mount: the unit's type key moves, so a loadout that
-- gained abilities mid-battle is picked up and its new abilities arm and
-- fire. The read costs almost nothing (a string the unit already carries),
-- so the per-4-s engine work of scanning every ability-less unit is gone.
--
-- THE SLOW SAFETY FALLBACK: every FALLBACK_RESCAN_EVERY_N_POLLS polls a full
-- scan still runs for a unit with nothing of ours, whatever its identity
-- says - so an unreadable or unchanging identity degrades to the old
-- behaviour, just far rarer (60 s instead of 4 s).
local FALLBACK_RESCAN_EVERY_N_POLLS = 240   -- 240 x 250 ms = every 60 seconds

-- How often to write one compact status line, in polls. 20 x 250 ms = every 5 s.
-- This is what makes a silent run diagnosable: it proves the poll is alive and
-- records the battle phase plus what every watched unit is doing.
local HEARTBEAT_EVERY_N_POLLS = 20

-- How often to re-list the player's units, in polls: a battle can GROW its
-- army after the first list was built - a summon, a Tzeentch split, a
-- transformation puts NEW units on the field mid-battle - and the watch list
-- must adopt them like any starting unit (tracked, scanned, selection
-- callback registered) without disturbing the units already on it. 40 x
-- 250 ms = every 10 seconds: low-frequency enough that the handful of engine
-- reads never shows, frequent enough that a fresh arrival is armed and
-- firing within seconds of appearing. The refresh speaks ONE line per
-- actual change, and is completely silent otherwise.
local RELIST_EVERY_N_POLLS = 40      -- 40 x 250 ms = every 10 seconds

-- Explicitly take control of the unit before ordering it.
-- OFF by default: the documentation says issuing an order takes control anyway,
-- and an explicit takeover is a candidate cause of the player's current order
-- being cancelled. Leave it off unless we find we need it.
local TAKE_CONTROL_FIRST = false

-- Hand the unit back to the player after the attempt - but ONLY a control we
-- actually took (took_control below). A release is never sent on its own:
-- the engine answers ok to releasing control we never had, and a needless
-- release may flush the unit's order queue. With TAKE_CONTROL_FIRST off
-- (today), this never runs at all.
local RELEASE_CONTROL_AFTER = true

-- How many of each unit's ability keys to write to the log.
local MAX_ABILITIES_TO_LOG = 14


-- ============================================================================
-- 2. BOOKKEEPING
-- ============================================================================

local tracked_units = nil                 -- units we watch
local units_by_ui_id = {}                 -- unique_ui_id (as string) -> unit (the unit-card click lookup)
local target_key_by_unit = {}             -- ui id -> the first of our keys found on the unit
local owned_keys_by_unit = {}             -- ui id (as text) -> EVERY one of our keys the scan
                                          -- found on that unit (ALL_ABILITY_KEYS filtered); the
                                          -- badge click's ownership test (section 10) and the
                                          -- per-unit primitive later items build on
local owned_abilities_by_unit = {}        -- ui id (as text) -> the ABILITIES entries that unit
                                          -- OWNS, in ABILITIES order, variants deduped (item 1.3).
                                          -- Computed once, when the scan fills the owned-key cache
                                          -- above; the poll's per-unit ability loop iterates THIS
                                          -- instead of the whole table. ABSENT (nil) = the unit's
                                          -- owned keys are UNKNOWN -> the loop falls back to the
                                          -- full ABILITIES table, exactly like today.
local identity_by_unit = {}               -- ui id (as text) -> the last-seen identity read of
                                          -- that unit (unit_identity -> battle_unit:type(), the
                                          -- land_units key). THE IDENTITY WATCH (item 3.4): the
                                          -- poll re-scans a unit with no key of ours only when
                                          -- this value CHANGES - which is what catches a
                                          -- transformation or a mount mid-battle
local identity_checked = {}               -- ui id (as text) -> true once that unit has been
                                          -- IDENTITY CHECKED at least once (item 5). This is
                                          -- distinct from identity_by_unit: a unit whose very
                                          -- first identity read FAILED (nil) has no cache entry
                                          -- but HAS been checked, so its first later GOOD read
                                          -- must re-scan instead of looking like a first read. A
                                          -- nil read is never cached, so a transient failure can
                                          -- never erase the last good value.
local selected_unit_id = nil              -- the single-choice tracker (string of unique_ui_id):
                                          -- a card click sets it, the card sweep (section 8e)
                                          -- keeps it on the engine's own 'selected' card; with
                                          -- several units selected it stays one of them while
                                          -- the badge click acts on selected_ui_ids below
local selected_ui_ids = {}                -- EVERY id the engine reports as SELECTED - the whole
                                          -- group, not just the tracker above. Maintained from
                                          -- the engine's own selection callback (section 3b)
                                          -- once it has delivered an event; until then (and
                                          -- whenever the callback has never fired) the shared
                                          -- card read (section 8e) keeps it, as it always did.
                                          -- Read by the badge click and the collective letter.

-- THE ENGINE SELECTION CALLBACK (this build). The battle manager's own
-- selection API - battle_manager:register_unit_selection_callback - takes one
-- registration per unit; the library registers the battle's single selection
-- handler once and dispatches every select/deselect event to each registered
-- unit's callback as (unit, selected:boolean). The card states do NOT carry a
-- group/box selection: measured in battle, box-selecting ten captains left
-- EVERY card reading 'active' - which is exactly why a badge click used to
-- toggle only one unit. The callback is the engine's own answer, so the
-- selected set is maintained from it; the card sweep stays as the fallback
-- and reconciliation whenever the API is unavailable or has never fired
-- (read_tracked_card_states, section 8e).
local selection_callbacks_by_ui_id = {}   -- ui id -> true: an accepted callback for that unit
local selection_callback_alive = false    -- true once the engine has DELIVERED an event
local selection_set_dirty = false         -- the set changed since the last convergence (section 8e)
local selection_set_sig = ""              -- the set at the last convergence ("1001,1002"; "" = empty)
local selection_callback_error_logged = false   -- one line for the first swallowed callback error
local reconciled_card_ids = {}            -- id -> true while the id sits in the set only because
                                          -- the cards still report it 'selected' (callback mode):
                                          -- the card read drops such an id again (section 8e)
-- THE REASONED WALK (this build). The old gate re-walked the whole HUD every
-- second UI tick for as long as ANY of our abilities was unclaimed - and a
-- selected unit that owns NONE of them (a Cathayan lord, a Tzeentch lord) has
-- no claim of ours to find, so the walk ran ~10x/s for the whole battle,
-- found nothing and filled the log. These two flags carry the whole reason
-- model: a selection CHANGE (the dial belongs to whoever is selected) and a
-- NEWLY TRACKED unit (a re-list arrival) each request exactly ONE walk - the
-- flag is a boolean, so however many events set it between two UI ticks, at
-- most one walk runs.
local walk_on_selection_change = false    -- set by the selection paths; consumed by the UI tick
local walk_on_new_unit = false            -- set by the re-list; consumed by the UI tick
-- THE BRISK WINDOW (round 7). The fast retries above are BOUNDED now: a
-- selection change / newly tracked unit opens a window of 48 ui ticks,
-- inside which the fast cadences still run (every 2nd tick while
-- the selected unit's info is unknown, every 4th while an owned marker's
-- claim is missing); outside any fresh window the walk falls back to the 5 s
-- safety net (every 100th tick) until the next event. The field log showed
-- the "missing owned ability claim" retry re-walking the whole HUD (630
-- components) for minutes when the dial never yielded the button. A battle
-- no event has ever touched keeps the old bootstrap cadence.
local brisk_walk_until = -1               -- ui tick until which the fast cadence is allowed; -1 = no event yet
local armed = {}                          -- ui_id -> (marker -> true/false); ABSENT means off
local last_attempt_at = {}                -- ui_id -> (marker -> tick of the last attempt)
-- THE COOLDOWN-HOLD TABLE (this round): ui_id -> (marker -> record) for a
-- pair the engine has refused ON COOLDOWN. The record carries the episode's
-- start tick (since - the hard bound is measured from it), the next tick the
-- pair may be probed (until), the running count of consecutive refusals
-- (streak) and whether the episode has already spoken (logged). Nested and
-- miss-safe, exactly like armed / last_attempt_at: a read never builds an
-- inner table, and the record is created only when a refusal actually arms
-- the hold.
local cooldown_hold = {}
-- THE KNOWN-GONE SET (this build): ui id (as text) -> true for a unit the
-- PRE-FIRE VALIDITY read or an engine rejection proved is no longer there.
-- It makes the drop FINAL: rebuild_unit_list consults it (section 6), so a
-- unit the engine has not yet taken off its army list cannot be re-adopted
-- and re-attempted by the next 10 s refresh - the removal notice is honoured
-- once, not every re-list.
local gone_units = {}
local pending_verify = nil                -- a deferred "did it take effect?" check
local tick_count = 0                      -- our battle clock
local GUARD_TICKS = (GUARD_SECONDS * 1000) / POLL_MS
local HOLD_TICKS = (HOLD_SECONDS * 1000) / POLL_MS
local MAX_HOLD_TICKS = (MAX_HOLD_SECONDS * 1000) / POLL_MS

-- The per-ability state, indexed by marker: the dial button the HUD scan found,
-- its event-reporting chain, the M/A badge component and its placement and
-- visibility bookkeeping. Nothing per-unit lives here.
local ability_state = {}
for _, ability in ipairs(ABILITIES) do
	ability_state[ability.marker] = { watch_chain = {} }
end

-- THE DEFERRED BADGE WORK (this build). A claim in the scan walk only records
-- the button and raises pending_badge[marker]; the ui tick builds the badge
-- from that flag, step by step and instrumented (section 8b). badge_attempts
-- counts the tick-creation attempts since the last claim, and badge_gave_up
-- latches once the budget is spent - until the dial rebuilds (a fresh claim
-- resets both).
local pending_badge = {}                  -- marker -> true while a claim waits for its badge
local badge_attempts = {}                 -- marker -> creation attempts since the last claim
local badge_gave_up = {}                  -- marker -> true once the attempt budget is spent

-- THE CLAIMED BUTTON'S BAR POSITION (this build): marker -> k, the 1-based
-- position of that ability's button among the KEY-BEARING children of its
-- parent bar ('button_parent' - the hidden bar the claimed buttons live in),
-- written by the claim walk (section 8b) and refreshed on every claim. Two
-- measured battles proved that position IS the wheel slot: k maps through
-- the static WHEEL_SLOT table (section 8b) to the measured wheel position,
-- and the badge's offset is BADGE_X/BADGE_Y (the hand-tuned top-slot pair)
-- shifted by that slot's delta from WHEEL_TOP_X/WHEEL_TOP_Y. nil / absent =
-- no usable position (never claimed, the bar unreadable, or more than six
-- key-bearing children): the badge then uses its fallback offset, logged at
-- placement. (The old live Position() read of the claimed button is GONE:
-- the claimed button lives in the hidden bar, so its Position() is a bar
-- coordinate like (1130,1052), NOT a wheel slot - that read is what put the
-- badges off-screen.)
local slot_index = {}

-- THE PER-UNIT SWITCH (this build): armed[ui_id][marker], ABSENT = off.
-- One entry per (unit, ability) pair, so two units carrying the same ability
-- arm and fire INDEPENDENTLY. A pair is flipped by: click the unit's card to
-- select it, then click the ability's M/A badge. This one helper is read by
-- BOTH the firing loop (does THIS unit fire THIS ability?) and the badge
-- display (which letter does the SELECTED unit's badge show?).
-- The arming tables are keyed by the unit's own ui id AS A NUMBER: the engine
-- reports it as a number (unit:unique_ui_id()), while the click paths carry
-- it as text (the card id IS that number). This maps the text form back to the
-- number so both paths always land on the SAME slot; a value that is already
-- the number (or a non-numeric id) passes through unchanged. tonumber never
-- allocates and no string is built, so the mapping is allocation-free.
local function unit_slot(ui_id)
	local n = tonumber(ui_id)
	if n ~= nil then return n end
	return ui_id
end

-- A READ NEVER CREATES: an unarmed (unit, marker) is a plain pass through
-- armed[ui_id] that MISSES (nil) - no inner table is ever built on a miss, so
-- reading a never-armed pair costs ONE table lookup and no allocation at all.
local function is_armed(unit, marker)
	if unit == nil then return false end
	local ok_id, raw_id = pcall(function() return unit:unique_ui_id() end)
	if not ok_id or raw_id == nil then return false end
	local ui_id = unit_slot(raw_id)
	local per = armed[ui_id]
	return per ~= nil and per[marker] == true
end

-- The unit behind the current selection, or nil while nothing is selected.
-- selected_unit_id follows the engine's own card state ('selected') through
-- the once-a-second card sweep (section 8e); a unit-card click is the
-- immediate fast-path when it lands first. A card's component id IS its
-- unit's unique_ui_id (the proven bridge - vanilla matches uic_card:Id() ==
-- unit:unique_ui_id() the same way), so selection is a plain table lookup:
-- no find of any kind.
local function selected_unit()
	if selected_unit_id == nil then return nil end
	return units_by_ui_id[tostring(selected_unit_id)]
end

-- One compact "how the per-unit switches stand" string, for the tick and
-- heartbeat logs: the selected unit and its own armed state per ability.
-- There is no global switch any more - each unit carries its own.
local function armed_states_string()
	local bits = { "selected=" .. tostring(selected_unit_id or "none") }
	local unit = selected_unit()
	for _, ability in ipairs(ABILITIES) do
		bits[#bits + 1] = ability.marker .. "=" .. (is_armed(unit, ability.marker) and "ON" or "OFF")
	end
	return table.concat(bits, ",")
end


-- ============================================================================
-- 3. LOGGING
--    a) our own file (primary - always works)
--    b) ModLog(), the mod loader's log, if it exists
--    c) out(), the game's own script log, if logging happens to be enabled
-- ============================================================================

local LOG_TAG  = "[zz_test_deadly_onslaught] "
local LOG_FILE = "zz_test_deadly_onslaught_log.txt"

local log_handle = nil
local file_logging_off = false

local function write_to_file(line)
	if file_logging_off then return end

	if log_handle == nil then
		local ok, handle = pcall(io.open, LOG_FILE, "a")
		if not ok or handle == nil then
			file_logging_off = true
			return
		end
		log_handle = handle
		log_handle:write("\n======== new battle session ========\n")
	end

	pcall(function()
		log_handle:write(line .. "\n")
		log_handle:flush()
	end)
end

local function log(message)
	local line = LOG_TAG .. tostring(message)

	write_to_file(line)

	if ModLog ~= nil then
		pcall(ModLog, line)
	end

	out(line)
end


-- ============================================================================
-- 2b. THE ACTIVE ABILITY SET (item 1.4)
-- ============================================================================
-- The ui tick's badge build/show/hide work was the only place the WHOLE
-- ABILITIES table was walked every 50 ms. At three entries that is free; at
-- dozens it is per-tick waste. The set below is the subset that can matter in
-- THIS battle:
--
--   (a) every tracked unit's OWNED markers - our keys filtered out of the
--       per-unit cache (owned_keys_by_unit, section 2) the scan already
--       fills, so no engine read and no searching beyond the units we
--       already watch;
--   (b) every marker CURRENTLY CLAIMED on the dial - ability_state
--       [marker].button ~= nil. This is the SUPERSET SAFETY: the dial
--       belongs to whoever is selected, and a claim can name an ability no
--       tracked unit owns, so a badge that is on the dial is never lost;
--   (c) nothing else.
--
-- It is recomputed ONLY when an input changes - the re-list, a scan, a
-- claim, a drop - never per tick, so the ui tick reads a ready list. Until
-- ANY information exists (the bootstrap: no tracked unit has owned-keys data
-- yet) the set is nil and every reader falls back to the FULL ABILITIES
-- table, which keeps the bootstrap behaviour identical to today. One line is
-- logged, and ONLY when the membership actually changes.
--
-- This is item 1.4's set; critique-2 item 1 then makes all_buttons_found()
-- test it instead of the full table (with the full-table fallback while it is
-- unknown), so the ui walk stops entirely when it is empty. The POLL's
-- per-unit ability loop (item 1.3) is deliberately untouched.

local active_abilities = nil          -- list of ABILITIES entries; nil = unknown -> use ABILITIES
local active_abilities_note = nil     -- the last logged membership line (silence unless it moves)

-- The list the ui tick's badge paths iterate: the active set, or the whole
-- table while nothing is known yet.
local function active_abilities_list()
	return active_abilities or ABILITIES
end

-- Rebuild the set from the owned-key cache and the live claims, and log ONE
-- line only when the membership changed. Cheap by construction: it walks the
-- tracked units and their cached owned keys, never the engine.
local function refresh_active_abilities()
	local set = {}
	local known = false

	-- (a) every tracked unit's owned markers, read out of the owned-key cache.
	if tracked_units ~= nil then
		for i = 1, #tracked_units do
			local su = tracked_units[i]
			local unit = su and su.unit
			if unit ~= nil then
				local ok_id, ui_id = pcall(function() return unit:unique_ui_id() end)
				if ok_id and ui_id ~= nil then
					local owned = owned_keys_by_unit[tostring(ui_id)]
					if owned ~= nil then
						known = true
						for oi = 1, #owned do
							-- item 3.1: one read of the static key->marker map
							-- instead of walking ABILITIES and each entry's keys.
							local marker = marker_by_key[owned[oi]]
							if marker ~= nil then
								set[marker] = true
							end
						end
					end
				end
			end
		end
	end

	-- (b) every currently claimed marker - the superset safety.
	for _, ability in ipairs(ABILITIES) do
		local state = ability_state[ability.marker]
		if state ~= nil and state.button ~= nil then
			set[ability.marker] = true
		end
	end

	-- (c) bootstrap: no information at all -> the full table (identical to
	-- today; nothing is logged).
	if not known then
		active_abilities = nil
		return
	end

	local list = {}
	local names = {}
	for _, ability in ipairs(ABILITIES) do
		if set[ability.marker] then
			list[#list + 1] = ability
			names[#names + 1] = ability.marker
		end
	end
	active_abilities = list

	local note = table.concat(names, ", ")
	if note ~= active_abilities_note then
		active_abilities_note = note
		log("active abilities this battle: " .. (note ~= "" and note or "(none)"))
	end
end

-- ITEM 1.3 - THE PER-UNIT OWNED-ABILITY LIST. Turn a unit's cached owned DB
-- keys into the ABILITIES entries it can actually carry: each key maps through
-- the static marker_by_key table (built once, section 1), the markers are
-- DEDUPED (a unit carrying BOTH engine variants of one marker - e.g. the main
-- and DLC Foe-Seeker keys - yields that marker ONCE), and the list is emitted
-- in ABILITIES order so the firing order - and therefore every log line and
-- every firing decision - is exactly what the full-table walk produced. A unit
-- carrying none of ours yields an EMPTY list, and the poll then evaluates
-- nothing for it instead of the whole table.
local function owned_abilities_of(owned_keys)
	local mark_owned = {}
	for oi = 1, #owned_keys do
		local marker = marker_by_key[owned_keys[oi]]
		if marker ~= nil then
			mark_owned[marker] = true
		end
	end
	local list = {}
	for _, ability in ipairs(ABILITIES) do
		if mark_owned[ability.marker] then
			list[#list + 1] = ability
		end
	end
	return list
end


-- ============================================================================
-- 3b. THE ENGINE SELECTION CALLBACK (this build)
--     The battle manager's own selection API: one registration per unit
--     (battle_manager:register_unit_selection_callback(unit, callback)), and
--     the engine then delivers every selection change of that unit to the
--     callback as (unit, selected:boolean) - truthy on a selection, the
--     boolean false on a deselection. This is the ONLY mechanism that sees a
--     group / box selection: the unit cards do not report one. The callback
--     runs in the engine's event context, so it does NOTHING but maintain the
--     selected set and raise a flag - no UI writes, no log lines (the set
--     change is logged ONCE per change by the tick convergence, section 8e,
--     so a ten-unit box selection cannot spam ten lines). Everything in the
--     body runs inside the pcall wall of the registered wrapper below: a
--     callback that raises kills every callback registered for the battle,
--     and this one is never allowed to be that.
-- ============================================================================

local function engine_selection_has(id)
	for i = 1, #selected_ui_ids do
		if selected_ui_ids[i] == id then return true end
	end
	return false
end

-- The callback body. Only private state: add the id on a selection, remove it
-- on a deselection, and raise selection_set_dirty when the set really moved
-- (the tracker and the badge letters follow at the next convergence, section
-- 8e). A unit we do not track is ignored (its events are not ours to act on).
local function engine_selection_body(unit, selected)
	if unit == nil then return end
	local ok_id, ui_id = pcall(function() return unit:unique_ui_id() end)
	if not ok_id or ui_id == nil then return end
	local id = tostring(ui_id)
	if units_by_ui_id[id] == nil then return end

	selection_callback_alive = true

	if selected then
		if not engine_selection_has(id) then
			selected_ui_ids[#selected_ui_ids + 1] = id
			selection_set_dirty = true
			walk_on_selection_change = true   -- the dial now belongs to the new selection
		end
	else
		for i = #selected_ui_ids, 1, -1 do
			if selected_ui_ids[i] == id then
				table.remove(selected_ui_ids, i)
				selection_set_dirty = true
				walk_on_selection_change = true   -- the dial re-homes when a selection drops
			end
		end
	end
end

-- THE REGISTERED CALLBACK: the body behind the error wall. The first swallowed
-- error is logged once (it is also the proof the wall is doing its job); every
-- later one is swallowed the same silent way.
local function engine_selection_callback(unit, selected)
	local ok, err = pcall(engine_selection_body, unit, selected)
	if not ok and not selection_callback_error_logged then
		selection_callback_error_logged = true
		log("selection callback error (swallowed - the engine's callbacks stay alive): "
			.. tostring(err))
	end
end


-- ============================================================================
-- 4. FIND THE ABILITY ON A UNIT
--    Returns:
--      matching_key : the ability key this unit owns, or nil
--      all_keys     : every ability key the unit owns (for the log)
-- ============================================================================

local function scan_unit_abilities(unit)
	local owned = unit:owned_special_abilities()
	local matching_key = nil
	local all_keys = {}

	if owned == nil then
		return nil, all_keys
	end

	for _, owned_key in pairs(owned) do
		all_keys[#all_keys + 1] = owned_key

		-- item 3.1: O(1) membership test against the static key set (the
		-- ALL_ABILITY_KEYS array stays for the ordered iterations).
		if ALL_ABILITY_KEYS_SET[owned_key] then
			matching_key = owned_key
		end
	end

	return matching_key, all_keys
end

-- THE CHEAP IDENTITY READ (this build, item 3.4): ONE engine call -
-- battle_unit:type(), the unit's land_units key (battle_unit.lua: "Returns
-- the unit type of the unit, from the land_units table"). It costs almost
-- nothing and it is the value a transformation or a mount moves, so it is
-- what the poll watches instead of re-running the full scan every 4 s. The
-- read is pcall-guarded and FAIL-OPEN: a missing method, a raising read or a
-- nil answer all come back as nil, and a nil identity never reports a change
-- (the 60 s fallback then carries the re-scan). Used by the poll's redetect
-- step only.
local function unit_identity(unit)
	local ok, value = pcall(function() return unit:type() end)
	if ok and value ~= nil then
		return tostring(value)
	end
	return nil
end

-- Which key of this ability (if any) did the unit list among its own? Used by
-- the watch-list log. owned_keys is the all_keys list scan_unit_abilities gave.
local function owned_key_in(ability, owned_keys)
	for _, wanted_key in ipairs(ability.keys) do
		for _, owned_key in ipairs(owned_keys) do
			if owned_key == wanted_key then return wanted_key end
		end
	end
	return nil
end

-- THE PER-UNIT OWNED-KEY CACHE (this build). The scan reports every ability a
-- unit carries (all_keys); this keeps only OUR keys from that list, per unit,
-- in owned_keys_by_unit (section 2). It answers one question without any
-- engine read or searching - "does this unit own this ability?" - for the
-- badge click's checkbox rule (section 10) and the collective badge letter.
local function our_keys_of(all_keys)
	local ours = {}
	for k = 1, #all_keys do
		-- item 3.1: O(1) membership test. The keys are unique, so an owned
		-- key was appended exactly once before too.
		if ALL_ABILITY_KEYS_SET[all_keys[k]] then
			ours[#ours + 1] = all_keys[k]
		end
	end
	return ours
end

-- Does this unit's cached owned-keys list carry one of this ability's keys?
-- (the same exact-equality match the scan and the ready gate use). Unknown
-- units and units the scan has not seen answer false.
local function unit_owns_marker(ui_id, marker)
	local ability = ability_for(marker)
	if ability == nil then return false end
	local owned = owned_keys_by_unit[tostring(ui_id)]
	if owned == nil then return false end
	return owned_key_in(ability, owned) ~= nil
end

-- WHY A WALK WOULD EVER BE NEEDED (this build). Two questions, both answered
-- from state the mod already holds - no engine read, no searching of any kind:
--   * is anything known yet about the SELECTED unit's own keys? (no selection,
--     or a selected id the scan has not cached: the BOOTSTRAP phase, which
--     keeps the old every-other-tick walk);
--   * does the selected unit OWN one of our keys whose dial claim is still
--     MISSING? (the dial-animation / lag case: retry briskly until claimed).
local function selection_walk_info_known()
	if selected_unit_id == nil then return false end
	if owned_keys_by_unit[tostring(selected_unit_id)] == nil then return false end
	return true
end

local function selected_unit_owns_unclaimed_key()
	if selected_unit_id == nil then return false end
	-- ITEM 11: read the selected unit's CACHED owned markers (item 1.3) -
	-- the abilities the scan mapped from its owned keys, in ABILITIES order
	-- - instead of walking the whole global table and asking the per-unit
	-- ownership test about each entry (which searched the ability's
	-- database-key list by string comparison on every gate evaluation). Every
	-- entry of this list is by construction an ability the unit OWNS, so the
	-- only question left here is whether its dial claim is still missing. A
	-- unit with no cached owned-marker list owns nothing of ours we know of -
	-- exactly the condition the old ownership test answered false on - so the
	-- gate stays closed.
	local list = owned_abilities_by_unit[tostring(selected_unit_id)]
	if list == nil then return false end
	for _, ability in ipairs(list) do
		if ability_state[ability.marker].button == nil then
			return true
		end
	end
	return false
end

-- THE COLLECTIVE SWITCH READ (this build) - the expected letter behind EVERY
-- badge write (the badge's first SetText, the cached writer, the per-tick
-- safety net and the click refresh all call it, so they can never disagree).
-- ONE selected unit: exactly the old read - that unit's own armed flag.
-- SEVERAL selected units: the vanilla "common ability" rule - on only when
-- EVERY selected unit that owns this ability has it armed, so the badge reads
-- A while the whole group is armed and flips to M the moment any member is
-- off. A group where no selected unit owns the ability reads off.
local function collective_armed(marker)
	local n = #selected_ui_ids
	if n <= 1 then
		-- ONE selected unit: exactly the old read - that unit's own flag.
		return is_armed(selected_unit(), marker)
	end
	local owners = 0
	for i = 1, n do
		local id = selected_ui_ids[i]
		-- ITEM 10: membership is read from the item-1.3 owned-marker cache
		-- (this unit's ABILITIES entries, mapped and variant-deduped at scan
		-- time) - a walk of a 1-4 element marker list, never the old per-key
		-- string comparison against the ability's database-key list. That
		-- search is gone from this per-tick path entirely. A unit with no
		-- cached owned-marker list owns nothing of ours we know of, exactly
		-- the condition the old ownership test answered false on, so it is not
		-- one of this ability's owners.
		local owns = false
		local list = owned_abilities_by_unit[tostring(id)]
		if list ~= nil then
			for _, entry in ipairs(list) do
				if entry.marker == marker then
					owns = true
					break
				end
			end
		end
		if owns then
			owners = owners + 1
			if not is_armed(units_by_ui_id[tostring(id)], marker) then
				return false
			end
		end
	end
	return owners > 0
end

-- THE READINESS GATE (the engine's own "can I use this?" check). The key it
-- asks about is the one the unit scan already found on this unit
-- (target_key_by_unit, section 2): a database variant the unit does NOT
-- carry can only ever answer false, so re-trying every variant at fire time
-- told us nothing new - one query, on the owned key, is the whole question.
-- The old walk over ability.keys stays ONLY as the fallback for a unit with
-- no usable cached key: not scanned yet, or the cached key belongs to a
-- DIFFERENT ability of ours (a unit can carry more than one - asking here
-- about that key could fire the wrong ability, so it is not used). No
-- fall-through when the owned key answers false: that means running/on
-- cooldown, and no other variant changes that. Returns the key or nil, plus
-- a text summary of every answer (logged on each evaluation, like the
-- earlier two-ability build).
local function check_readiness(unit, ability, cached_key)
	local ready_key = nil
	local parts = {}
	local suffix = " (fallback scan)"   -- no usable cached key: the old walk ran

	-- Which cached key may answer here: only one that belongs to THIS ability.
	local owned_key = nil
	if cached_key ~= nil then
		for _, wanted_key in ipairs(ability.keys) do
			if wanted_key == cached_key then owned_key = cached_key end
		end
	end

	if owned_key ~= nil then
		-- The one query: the key this unit was found to own.
		suffix = " (owned key)"
		local ok_c, can = pcall(function()
			return unit:can_perform_special_ability(owned_key)
		end)
		parts[#parts + 1] = owned_key .. "=" .. tostring(ok_c and tostring(can) or "ERROR")
		if ok_c and can == true then
			ready_key = owned_key
		end
	else
		-- No usable cached key yet: the original walk over the variants.
		for _, wanted_key in ipairs(ability.keys) do
			local ok_c, can = pcall(function()
				return unit:can_perform_special_ability(wanted_key)
			end)
			parts[#parts + 1] = wanted_key .. "=" .. tostring(ok_c and tostring(can) or "ERROR")
			if ok_c and can == true and ready_key == nil then
				ready_key = wanted_key
			end
		end
	end

	return ready_key, table.concat(parts, ", ") .. suffix
end


-- ============================================================================
-- 5. IS IT ACTUALLY CHARGING?
--    A charge is an ATTACK order on an enemy that is about to connect.
--    Returns a table of measurements, which the log prints, so every decision
--    can be audited from real numbers.
--
--    charging = fast AND not melee AND has a target AND the order is an attack
--               (not a move) AND the target is close enough that impact is
--               within CHARGE_TIME_TO_CONTACT_S seconds.
-- ============================================================================

local function measure_charge(unit)
	local m = {
		fast = unit:is_moving_fast(),
		melee = unit:is_in_melee(),
		has_target = false,
		order_gap = -1,      -- position() vs ordered_position(); -1 = unmeasurable
		target_dist = -1,    -- metres to the target unit; -1 = unknown
		ttc = -1,            -- estimated seconds until contact; -1 = unknown
		charging = false,
	}

	local ok_target, target = pcall(function() return unit:current_target() end)
	if ok_target and target ~= nil then
		m.has_target = true
	end

	local ok_gap, gap = pcall(function()
		return unit:position():distance(unit:ordered_position())
	end)
	if ok_gap and gap ~= nil then
		m.order_gap = gap
	end

	if m.has_target then
		local ok_dist, dist = pcall(function() return unit:unit_distance(target) end)
		if ok_dist and dist ~= nil then
			m.target_dist = dist
		end

		if m.target_dist >= 0 then
			local ok_speed, speed = pcall(function() return unit:fast_speed() end)
			if ok_speed and speed ~= nil and speed > 0 then

				m.ttc = m.target_dist / speed
			end
		end
	end

	if m.fast and not m.melee and m.has_target then
		-- Having a target at all is the attack-versus-move signal: a move
		-- order sets none. (ordered_position() is NOT used here - round 7
		-- proved it tracks time-since-order, not attack-versus-move.)

		-- A real charge has a run-up: far enough that the unit actually
		-- builds speed, close enough that the impact is imminent.
		local enough_run_up = true
		if m.target_dist >= 0 then
			enough_run_up = (m.target_dist >= CHARGE_MIN_DISTANCE_M)
		end

		local close_enough = true
		if m.target_dist >= 0 then
			close_enough = (m.target_dist <= CHARGE_MAX_DISTANCE_M)
		end

		local soon_enough = true
		if m.ttc >= 0 then
			soon_enough = (m.ttc <= CHARGE_TIME_TO_CONTACT_S)
		end

		m.charging = enough_run_up and close_enough and soon_enough
	end

	return m
end


-- ============================================================================
-- 6. BUILD THE WATCH LIST (and say out loud what we found)
--    bm:get_scriptunits_for_local_players_army() gives us "script units": each
--    wraps the unit itself (.unit) plus a controller that can give it orders
--    (.uc). The ability dump is what makes a failed run diagnosable: it shows
--    exactly which abilities each unit has, so we can retarget without guessing.
-- ============================================================================

-- THE ONE DROP ROUTINE (items 2 + 13). Defined here - ABOVE the watch-list
-- builder - because BOTH drop paths call it: the re-list below, and the poll's
-- dead-unit path in section 8. The unit leaves tracked_units and EVERY
-- per-unit table is purged of its rows, so no stale row can be read for a unit
-- that is gone (the stuck-collective-letter class) and the per-unit caches
-- cannot grow without bound over a long battle. The id is put in gone_units,
-- which is deliberately KEPT (sticky), so the next 10 s re-list cannot re-adopt
-- a unit the engine has not yet taken off its army list - the removal notice is
-- honoured once, not every re-list. Called AFTER the poll's tracking loop has
-- stopped walking the list, so the table.remove here can never disturb the
-- iteration it came from; it is silent - the caller has already written the one
-- drop line.
local function drop_unit_by_ui_id(ui_id)
	local id_text = tostring(ui_id)
	local id_slot = unit_slot(ui_id)
	gone_units[id_text] = true          -- STICKY (never purged): the re-list must not re-adopt
	if tracked_units ~= nil then
		for i = #tracked_units, 1, -1 do
			local script_unit = tracked_units[i]
			local same = false
			-- ITEMS 14 + 6 (ONE fix). Match on the id CACHED on the entry at
			-- registration (section 6). The old shape read unit:unique_ui_id()
			-- (pcall'd) right here, so a dead unit whose read now FAILED
			-- matched nothing and its entry LINGERED on the watch list - and
			-- every per-unit row the purge below is meant to clear lingered
			-- with it. The cached text needs no engine read, so the removal
			-- survives the dying engine's refusal. Fallback: an entry with no
			-- cached id yet (registered before this build) still gets the old
			-- pcall'd engine read.
			local cached = script_unit and script_unit.zz_tracked_ui_id
			if cached ~= nil then
				same = (cached == id_text)
			else
				local unit = script_unit and script_unit.unit
				if unit ~= nil then
					local ok_id, id = pcall(function() return unit:unique_ui_id() end)
					if ok_id and id ~= nil and tostring(id) == id_text then same = true end
				end
			end
			if same then
				-- PURGE the cached id WITH the entry (item 4 of the fix),
				-- consistently with the per-unit purge below: the entry leaves
				-- the list and its cache leaves with it.
				if script_unit ~= nil then
					script_unit.zz_tracked_ui_id = nil
				end
				table.remove(tracked_units, i)
			end
		end
	end

	-- PURGE EVERY PER-UNIT TABLE (items 2 + 13). The unit's id is stored in
	-- two shapes - as TEXT (units_by_ui_id and the scan caches, all keyed by
	-- tostring(id)) and as the normalised NUMBER (armed / last_attempt_at /
	-- cooldown_hold via unit_slot; target_key_by_unit as the raw engine
	-- number) - so BOTH forms are cleared; a nil write on a key that was never
	-- set costs nothing. gone_units above is the one deliberate exception.
	units_by_ui_id[id_text] = nil
	owned_keys_by_unit[id_text] = nil
	owned_abilities_by_unit[id_text] = nil
	identity_by_unit[id_text] = nil
	identity_checked[id_text] = nil
	reconciled_card_ids[id_text] = nil
	selection_callbacks_by_ui_id[id_text] = nil
	target_key_by_unit[id_slot] = nil
	target_key_by_unit[id_text] = nil
	armed[id_slot] = nil
	last_attempt_at[id_slot] = nil
	cooldown_hold[id_slot] = nil
	charge_gate.until_tick[id_slot] = nil
	cast_gate.until_tick[id_slot] = nil
	cast_gate.logged[id_slot] = nil
	cast_gate.unit_until[id_slot] = nil
	cast_gate.unit_marker[id_slot] = nil
	cast_gate.unit_logged[id_slot] = nil

	-- THE SELECTED SET (item 2). A dead unit must not stay selected: a stale
	-- id in the set keeps collective_armed() computing the group's M/A letter
	-- from a unit that no longer exists, which pins the letter (the group
	-- reads M because the gone unit's is_armed() resolves false, even though
	-- every surviving selected owner is armed). Remove the id, hand the
	-- single-choice tracker to the first surviving selected id (or none), and
	-- let the EXISTING selection convergence plus the ui tick's per-tick
	-- letter net re-derive the letter - no new timer.
	for i = #selected_ui_ids, 1, -1 do
		if selected_ui_ids[i] == id_text then
			table.remove(selected_ui_ids, i)
		end
	end
	if selected_unit_id ~= nil and tostring(selected_unit_id) == id_text then
		selected_unit_id = selected_ui_ids[1]
	end
	selection_set_dirty = true
end

local function rebuild_unit_list()
	-- THE ADDITIVE RE-LIST (this build). The old function wiped the watch
	-- list and rebuilt it from scratch - fine for its original single
	-- startup call, but the poll now re-runs it every RELIST_EVERY_N_POLLS
	-- polls (mid-battle arrivals: summons, Tzeentch splits, transformations),
	-- and a wipe would lose per-unit state. So this function now MERGES, by
	-- identity (ui id): every unit already on the list is left completely
	-- untouched; only units the list has never seen are appended, scanned
	-- and remembered; and a unit the engine no longer returns (died / left
	-- the field) is dropped, exactly what the old wholesale rebuild did
	-- with it.
	local first_build = (tracked_units == nil)
	if first_build then
		tracked_units = {}
	end

	local sunits = bm:get_scriptunits_for_local_players_army()
	if sunits == nil then
		log("no units returned yet (army not on the field?)")
		return
	end

	local total = sunits:count()
	if first_build then
		log("watching " .. tostring(total) .. " unit(s) in the local player's army")
	end

	local carriers = 0
	local fresh = {}            -- ui id (as text) -> true: the engine reported it this pass
	local new_count = 0
	local new_ids = {}

	for i = 1, total do
		local script_unit = sunits:item(i)
		local unit = script_unit.unit
		local ui_id = unit:unique_ui_id()
		local id_text = tostring(ui_id)

		if fresh[id_text] == nil then
			fresh[id_text] = true

			-- A UNIT THE LIST HAS NOT SEEN: track it, scan it, remember it. Only
			-- genuinely new arrivals run the scan below, so an existing unit's
			-- remembered key and owned keys can never be overwritten by a refresh.
			-- A unit in gone_units (this build) is NOT re-adopted: the pre-fire
			-- read or an engine rejection already proved it is gone, and the
			-- engine may still be listing it for a while.
			if units_by_ui_id[id_text] == nil and gone_units[id_text] == nil then
				tracked_units[#tracked_units + 1] = script_unit

				-- ITEMS 14 + 6 (ONE fix - the cached id). The unit's ui id is
				-- captured HERE, at registration, where it is already in hand,
				-- and stored ON the tracked entry. Every later use - the card
				-- sweep's wanted list and the drop routine's match - reads this
				-- cached text instead of calling unit:unique_ui_id() again, so
				-- (a) the sweep's order no longer comes from pairs() (no hash
				-- order; the CARD_SWEEP_MAX subset is the same every call) and
				-- (b) a dead unit whose engine id read now FAILS can still be
				-- matched and removed. A unit is appended at most once
				-- (guarded by units_by_ui_id / gone_units), so this cache is
				-- written exactly once per tracked entry.
				script_unit.zz_tracked_ui_id = id_text

				-- The card-click bridge: a unit card's component id IS this unit's
				-- unique_ui_id, so a click on the card finds the unit right here.
				units_by_ui_id[id_text] = unit

				local matching_key, all_keys = scan_unit_abilities(unit)

				target_key_by_unit[ui_id] = matching_key
				owned_keys_by_unit[id_text] = our_keys_of(all_keys)   -- the per-unit owned-key cache
				owned_abilities_by_unit[id_text] =                       -- item 1.3: the short list
					owned_abilities_of(owned_keys_by_unit[id_text])      -- this unit's poll walks
				if matching_key ~= nil then
					carriers = carriers + 1
				end

				new_count = new_count + 1
				new_ids[#new_ids + 1] = id_text
				walk_on_new_unit = true          -- a unit the list never saw: scan for its dial once

				-- THE OPENING CENSUS keeps its full per-unit log; a later refresh
				-- deliberately stays to its ONE change line below - a full census
				-- per refresh is exactly the log spam this build avoids.
				if first_build then
					local own_parts = {}
					for _, ability in ipairs(ABILITIES) do
						local owned_key = owned_key_in(ability, all_keys)
						own_parts[#own_parts + 1] = "owns " .. ability.name .. " = "
							.. tostring(owned_key ~= nil)
							.. (owned_key and (" as '" .. owned_key .. "'") or "")
					end

					log("  unit '" .. tostring(unit:type()) .. "'"
						.. " ui id " .. tostring(ui_id)
						.. " | " .. tostring(#all_keys) .. " abilities"
						.. " | " .. table.concat(own_parts, " | ")
						.. " | usable right now = "
						.. tostring(unit:can_perform_special_ability(ALL_ABILITY_KEYS[1])))

					for j = 1, #all_keys do
						if j <= MAX_ABILITIES_TO_LOG then
							log("      ability: " .. tostring(all_keys[j]))
						end
					end
				end
			end
		end
	end

	-- THE DROP: a unit the engine did not return this pass (it died or left
	-- the field) comes off the watch list, exactly as the old wholesale
	-- rebuild dropped it. BOTH DROP PATHS PURGE IDENTICALLY (items 2 + 13):
	-- instead of clearing only tracked_units / units_by_ui_id here, the ids
	-- are collected and each one is handed to the SAME routine the poll's
	-- dead-unit path uses (drop_unit_by_ui_id), so its rows leave every
	-- per-unit table too. Collecting first keeps that routine's own scan of
	-- tracked_units from disturbing this loop.
	local dropped_count = 0
	local dropped_ids = {}
	for i = #tracked_units, 1, -1 do
		-- Items 14 + 6: the id comes from the tracked entry's CACHE, not a
		-- fresh engine read - a dead unit's unique_ui_id() can now fail, and
		-- this loop must still name it so the drop below can purge it. The
		-- pcall'd engine read is a fallback for an entry with no cached id
		-- (registration always sets one, so it never runs).
		local su = tracked_units[i]
		local id_text = su and su.zz_tracked_ui_id
		if id_text == nil then
			local unit = su and su.unit
			if unit ~= nil then
				local ok_id, id = pcall(function() return unit:unique_ui_id() end)
				if ok_id and id ~= nil then id_text = tostring(id) end
			end
		end
		if id_text ~= nil and fresh[id_text] == nil then
			dropped_ids[#dropped_ids + 1] = id_text
		end
	end
	for d = 1, #dropped_ids do
		drop_unit_by_ui_id(dropped_ids[d])
		dropped_count = dropped_count + 1
	end

	-- Make the success case impossible to miss when reading the log (the
	-- opening census only).
	if first_build then
		log("ability carriers found: " .. tostring(carriers))
	end

	-- THE ONE REFRESH LINE: a re-list speaks exactly once, and ONLY when the
	-- watched set actually changed - silent while the army is steady, so the
	-- 10-second refreshes can never turn into per-poll log spam. (The
	-- opening census above is the initial build's voice; a refresh never
	-- repeats it.)
	if not first_build and (new_count > 0 or dropped_count > 0) then
		local parts = {}
		if new_count > 0 then
			parts[#parts + 1] = tostring(new_count) .. " new unit(s) now tracked ("
				.. table.concat(new_ids, ", ") .. ")"
		end
		if dropped_count > 0 then
			parts[#parts + 1] = tostring(dropped_count) .. " unit(s) dropped ("
				.. table.concat(dropped_ids, ", ") .. ")"
		end
		log("unit list refresh: " .. table.concat(parts, " | "))
	end

	-- THE ENGINE SELECTION CALLBACKS (this build): one registration per tracked
	-- unit with the engine's own selection API, so a GROUP / BOX selection
	-- reaches us per unit (the card states do not carry one - measured in
	-- battle). Everything is guarded twice: the API may not exist (or may not
	-- accept the unit) in some builds - the card sweep then stays in charge,
	-- unchanged - and a registration that raises is caught here (a callback
	-- that raises is caught again, inside, at every event). A unit already
	-- registered keeps its single registration across rebuilds, so a refresh
	-- registers for genuinely NEW units only - exactly once each.
	local registered_now = 0
	local ok_fn, is_fn = pcall(function()
		return type(bm.register_unit_selection_callback) == "function"
	end)
	if ok_fn and is_fn then
		for i = 1, #tracked_units do
			local su = tracked_units[i]
			local unit = su and su.unit
			if unit ~= nil then
				local ok_u, ui_id = pcall(function() return unit:unique_ui_id() end)
				if ok_u and ui_id ~= nil and selection_callbacks_by_ui_id[tostring(ui_id)] == nil then
					local ok_r, accepted = pcall(function()
						return bm:register_unit_selection_callback(unit, engine_selection_callback)
					end)
					if ok_r and accepted ~= false then
						selection_callbacks_by_ui_id[tostring(ui_id)] = true
						registered_now = registered_now + 1
					end
				end
			end
		end
		if first_build then
			log("engine selection API: " .. tostring(registered_now) .. " new callback(s) registered ("
				.. tostring(#selection_callbacks_by_ui_id) .. " unit(s) covered in total)")
		end
	else
		if first_build then
			log("engine selection API not available - the card-state sweep stays in charge (unchanged fallback)")
		end
	end

	-- ITEM 1.4 - the re-list / drop just changed the inputs: refresh the
	-- active set (silent unless the membership moved).
	refresh_active_abilities()
end


-- ============================================================================
-- 5b. THE ON/OFF SWITCH AND ITS BUTTON
--     One boolean, flipped by a small button docked in the battle order bar.
--
--     WHERE THIS CODE MAY RUN - learned the hard way over rounds 9-15:
--       * creating the component from a model timer or from a phase callback has
--         twice killed the battle's model timer (and with it the poll that
--         watches for charges) - rounds 9, 10 and 13;
--       * painting it from a timer silently does nothing, so the button keeps the
--         template's placeholder icon - rounds 11 and 14;
--       * painting from a phase callback, or from a click handler, works - the
--         icon was correct in rounds 9 and 13, and clicks repainted it correctly.
--     So: create and paint in the phase callbacks and the click handler. The poll is
--     registered once at load and never touched again (see the note at rearm's old
--     place in section 9): removing and re-adding a model timer is what broke the
--     trigger in round 17.
-- ============================================================================

-- (The switch is PER UNIT AND PER ABILITY: armed[ui_id][marker], section 2
--  - absent means off (the badges show M) until the player clicks them. The
--  player selects a unit by clicking its card (the card id IS the unit's
--  unique_ui_id), then each badge click flips ONLY that unit's own ability.
--  The badge click is the ONLY control - the keyboard, right-click and
--  double-click routes have all been removed (rounds 15-25 measured that
--  nothing else reaches script in battle).)

-- The switch itself. Everything that used to make a button for it - the template clone,
-- the docking, the two icon files, the bar-width fiddling and the click listener - has been
-- removed: the control is a left-click on the M/A badge (section 8b).

-- The poll's name, used once, where it is registered.
local POLL_NAME = "zz_test_deadly_onslaught_poll"


-- ============================================================================
-- 6. HEARTBEAT
--    One compact line every few seconds: the battle phase, and for each watched
--    unit whether it is alive, running/charging, in melee, and able to use the
--    ability. If a run fires nothing, this is what explains why.
-- ============================================================================

local function log_heartbeat()
	-- The phase name is the one call here I have not yet seen run inside the
	-- real game, so it is guarded: a failure must not break the poll loop.
	local phase_name = "?"
	local ok, value = pcall(function() return bm:get_current_phase_name() end)
	if ok then
		phase_name = value
	end

	local parts = {
		"hb t=" .. tostring(tick_count),
		"phase=" .. tostring(phase_name),
		"conflict=" .. tostring(bm:is_conflict_phase()),
		"auto=" .. armed_states_string(),
	}

	if tracked_units ~= nil then
		for i = 1, #tracked_units do
			local script_unit = tracked_units[i]
			local unit = script_unit and script_unit.unit

			if unit ~= nil then
				local ui_id = unit:unique_ui_id()
				local m = measure_charge(unit)

				parts[#parts + 1] = string.format(
					"%s#%s alive=%s fast=%s melee=%s tgt=%s gap=%.1fm dist=%.1fm eta=%.1fs",
					tostring(unit:type()),
					tostring(ui_id),
					tostring(unit:number_of_men_alive()),
					tostring(m.fast),
					tostring(m.melee),
					tostring(m.has_target),
					m.order_gap,
					m.target_dist,
					m.ttc)
			end
		end
	end

	log(table.concat(parts, " | "))
end


-- ============================================================================
-- 7. ACTIVATION
--    Resolved from the game's OWN script files, not from documentation:
--
--      script/battle/quest_battles/tamurkhan/kayzk/battle_script.lua
--        if sunit.unit:can_perform_special_ability("<key>") then
--            sunit.uc:perform_special_ability("<key>", sunit.unit)
--        end
--
--      script/benchmarks/battle_benchmark/battle_benchmark.lua
--        --- Khorne Lord Buffing Himself ---
--        sunit_kho_01.uc:perform_special_ability("<key>", sunit_kho_01.unit)
--
--    So: ability key FIRST, target unit SECOND, and the target is REQUIRED.
--    For a self-buff the target is the unit itself. Every one of the 26 vanilla
--    call sites passes a target; none omits it.
--
--    That explains the round 3 failure (we omitted the target) and the round 4
--    failures (we had the arguments the other way round, which the engine
--    reports as "bad self ... expecting special ability name (string)").
--
--    Round 3's ground-targeted variant is GONE - it is what left the unit
--    holding a targeting cursor with a crossed-out ability icon.
--
--    Success is still judged objectively: a real activation starts the cooldown,
--    so can_perform_special_ability must flip to false.
-- ============================================================================

-- (The old fixed brakes - 90 s per unit after an accepted activation, and the
--  20 s floor between attempts - are gone. The readiness gate (section 4) and
--  the short guard (GUARD_SECONDS, section 1) are the whole brake now.)


-- ============================================================================
-- 7c. ACTIVATION
--     Resolved from the game's OWN script files, not from documentation:
--
--       script/battle/quest_battles/tamurkhan/kayzk/battle_script.lua
--         if sunit.unit:can_perform_special_ability("<key>") then
--             sunit.uc:perform_special_ability("<key>", sunit.unit)
--         end
--
--       script/benchmarks/battle_benchmark/battle_benchmark.lua
--         --- Khorne Lord Buffing Himself ---
--         sunit_kho_01.uc:perform_special_ability("<key>", sunit_kho_01.unit)
--
--     Ability key FIRST, target unit SECOND, target REQUIRED. All 26 vanilla
--     call sites pass a target; none omits it. For a self-buff the target is the
--     unit itself. This is the call that worked in round 5.
--
--     A NOTE ON DETECTING SUCCESS
--     can_perform_special_ability() does NOT report the cooldown. Round 5 proved
--     that: the call was accepted and the ability fired, yet this check still
--     returned true. What the engine does say, once the ability is active, is:
--
--        error: unit '1' does not support this special ability
--
--     So that error is treated here as evidence that the ability is currently
--     active - i.e. that an earlier activation worked.
-- ============================================================================

-- A CONTAINS TEST WITH NO string.find IN IT. The bisect proved the engine
-- dies inside the four-argument plain-mode find, and this build has removed
-- every find call from the file. This small plain-Lua scan (string.sub
-- slices; it only ever sees our own tostring() error text, never an engine
-- value) is what checks for the engine's known "does not support this
-- special ability" message instead.
local function text_contains(haystack, needle)
	local h = tostring(haystack or "")
	local n = tostring(needle or "")
	local hlen = string.len(h)
	local nlen = string.len(n)
	if nlen == 0 or nlen > hlen then return false end
	for i = 1, hlen - nlen + 1 do
		if string.sub(h, i, i + nlen - 1) == n then return true end
	end
	return false
end

-- THE NON-EXISTENCE REFUSALS (this build). The engine wraps a refused fire as
-- "calling 'perform_special_ability' on bad self (error: ...)". When the unit
-- it names is GONE, the inner text says so in one of the forms below - and
-- those are what are matched here, exact substring only, through the same
-- find-free text_contains() the cooldown check uses. THE COOLDOWN/ACTIVE
-- REFUSAL THIS MOD HAS ALWAYS SEEN IS A DIFFERENT STRING ("does not support
-- this special ability"): none of the markers below is a substring of it, so
-- a LIVE unit that is merely on cooldown can never match and be dropped. The
-- live battle log proves that string is a hold, not a death: one unit (ui id
-- 1002) produced it dozens of times and ACCEPTED a fire minutes later.
local GONE_UNIT_ERRORS = {
	"does not exist",
	"no longer exists",
	"no such unit",
	"invalid unit",
	"unit is gone",
}

local function error_means_unit_gone(err_text)
	local text = tostring(err_text or "")
	for i = 1, #GONE_UNIT_ERRORS do
		if text_contains(text, GONE_UNIT_ERRORS[i]) then return true end
	end
	return false
end

-- THE PRE-FIRE VALIDITY READ (this build). Two cheap, pcall'd engine reads
-- immediately before the fire call, cutting the window between the poll's
-- alive check (which reads number_of_men_alive) and the call itself - a unit
-- that dies inside that window is exactly why this exists.
--
-- THE RULE is deliberately two-signal and fail-open, because an identity read
-- alone is NOT a death test: an unreadable identity (battle_unit:type()
-- answering nothing) is a state this mod already supports - the identity
-- watch keeps such a unit and the slow 60 s fallback still rescues it. So:
--   * if number_of_men_alive ANSWERS A NUMBER, that is the truth: > 0 alive,
--     <= 0 gone;
--   * only when it does NOT answer a number does the identity read decide,
--     and only a CLEAN nil (the unit answered nothing at all) counts as gone.
-- A READ THAT RAISES - either read - is a transient engine failure, exactly
-- the shape pcall catches, and is NEVER death. Two independent failures are
-- needed before a unit is called gone, so a single flaky read can never drop
-- a live unit. (unit_identity() is not reused here on purpose: it folds a
-- raising read and a nil answer into the same nil, which would make a
-- transient failure look like death.)
local function unit_is_gone(unit)
	if unit == nil then return true end
	local ok_alive, alive = pcall(function() return unit:number_of_men_alive() end)
	if ok_alive and type(alive) == "number" then
		return alive <= 0                  -- the engine answered: THAT is the truth
	end
	local ok_id, id = pcall(function() return unit:type() end)
	return ok_id and id == nil             -- no answer from either read: gone
end


-- ============================================================================
-- 7e. MORALE, AND THE GROUND-TARGETED CAST (the fourth ability)
--     TWO capabilities the earlier abilities never needed, both pcall'd and
--     FAIL-OPEN, and both in ONE place so the poll and the fire path can
--     never disagree about them.
--
--     (a) THE MORALE THRESHOLD. There is NO percentage / unary morale read in
--     the battle API. The only morale THRESHOLD the engine exposes to script
--     is battle_unit:is_wavering() - "Returns whether the morale of the unit
--     is currently wavering" (battle_unit.lua). Wavering is the first morale
--     band below steady, so it is the honest stand-in for "morale below a
--     threshold". (The API dump also carries morale_is_* @return names -
--     morale_is_lower_than_half_of_base_morale and friends - but they are
--     ORPHANED doc annotations with no callable function behind them, so
--     is_wavering is the only one that can actually be read.)
--     unit_is_wavering returns true (wavering - below the threshold), false
--     (a READABLE, healthy morale) or nil (the read could not be taken:
--     missing method, raising read or a nil answer). The trigger treats only
--     exact true as "below threshold" and falls back to plain in-melee on
--     nil, so an unreadable morale can never silently suppress the ability.
--
--     (b) THE GROUND-TARGETED CAST. The fourth ability carries TWO db keys
--     with DIFFERENT targeting. The base
--         wh_main_character_abilities_stand_your_ground
--     is self-centred (target_ground = false, affect_self = true) and fires
--     through the proven uc:perform_special_ability(key, unit). The DLC24
--         wh3_dlc24_character_abilities_tacticians_stand_your_ground
--     is friend- AND ground-targeted (target_friends = true,
--     target_ground = true), and for that one the API offers a DIFFERENT
--     call: battle_unitcontroller:perform_special_ability_ground(ability_key,
--     position, orientation_in_degrees, width_in_m) - "on a specified
--     position". The position is a battle_vector, and battle_unit:position()
--     IS one, so the ground point is the caster's own ground position (the
--     ability buffs itself and the friendly area around it). Vanilla passes a
--     UNIT to perform_special_ability at all 26 of its call sites and never
--     calls the _ground form, so the API documentation is the evidence for
--     the ground path. GROUND_TARGETED_KEYS below is the ONE place that maps
--     a key to it, so a later targeted ability is one line here.
--
--     FAIL-OPEN: if the position cannot be read, the cast is NOT made - the
--     mod never fires a targeted ability with a guessed target. The reason is
--     logged ONCE per (unit, marker) via FOURTH.missing_logged, not on every
--     retry; the pair then re-probes on its normal guard cadence.
--
--     ONE NEW TOP-LEVEL LOCAL ONLY: the main chunk already sits at Lua's
--     200-local ceiling, so the fourth ability's helpers are FIELDS of the
--     single table below (a bare local function each would push the chunk
--     over the limit and the whole file would fail to compile). Call sites
--     read exactly as a function call would: FOURTH.wavering(unit),
--     FOURTH.is_ground_key(key), FOURTH.ground_cast(uc, unit, key).
-- ============================================================================
local FOURTH = {
	-- The keys whose engine call is the POSITION form. Exact keys, lowercase -
	-- the same values the ABILITIES table (section 1) lists; a key that fires
	-- through the ground form must be listed here AND there.
	ground_keys = {
		["wh3_dlc24_character_abilities_tacticians_stand_your_ground"] = true,
		-- ROUND 130: Ballistics Calibration, placed at the caster's own feet.
		["wh_main_hero_abilities_ballistics_calibration"] = true,
	},
	-- THE ENEMY-GROUND AREA KEYS (Class A, harness 97): keys whose db row is
-- target_enemies + target_ground - the cast is PLACED ON ENEMY GROUND, so the
-- ground form perform_special_ability_ground(key, ENEMY_POSITION, 0, 0) is
-- used (never the caster's own position). Exact keys, lowercase.
enemy_ground_keys = {
		["wh2_dlc09_item_abilities_amulet_of_phastah"] = true,
		["wh_dlc03_item_abilities_chalice_of_dark_rain"] = true,
		["wh2_dlc09_character_abilities_curse_of_khsar"] = true,
		["wh2_dlc10_character_abilities_entangle"] = true,
		["wh3_dlc25_character_abilities_get_em"] = true,
		["wh2_dlc13_lord_abilities_hunters_snare"] = true,
		["wh2_dlc13_lord_abilities_hunters_trap"] = true,
		["wh2_main_item_abilities_the_tricksters_pendant"] = true,
		["wh_main_item_abilities_tricksters_shard"] = true,
		-- GATE OF KHORNE (harness 101): target_friends + target_ground, a SUMMON
		-- placed on the chosen FIGHTING enemy's ground - the ground form with the
		-- ENEMY's position, never the caster's.
		["wh3_main_character_abilities_gate_of_khorne"] = true,
		-- THE SUMMON ROUND (harness 102), part 1: the 68 keys of the A batch -
		-- every in-wheel, non-illusion, GROUND-CASTABLE wh_type_summon_unit row
		-- left. Each one is placed on the CHOSEN ENEMY's ground.
		["wh3_dlc23_item_abilities_ancestral_vengeance"] = true,
		["wh3_main_spell_bound_ancestral_warriors"] = true,
		["wh_dlc08_item_abilities_arachnarok_eggs"] = true,
		["wh2_dlc11_character_abilities_beyond_the_realm"] = true,
		["wh3_main_item_abilities_bloodstone"] = true,
		["wh2_dlc16_lord_abilities_call_to_ceithin_har"] = true,
		["wh2_dlc11_item_abilities_captain_roths_moondial"] = true,
		["wh3_dlc25_character_abilities_children_of_the_forest"] = true,
		["wh2_dlc16_item_abilities_dreaming_cloak_i"] = true,
		["wh2_dlc16_item_abilities_dreaming_cloak_ii"] = true,
		["wh2_dlc16_item_abilities_dreaming_cloak_iii"] = true,
		["wh3_main_daemon_arms_abilities_gate_of_chaos"] = true,
		["wh3_main_daemon_arms_abilities_gate_of_chaos_upgraded"] = true,
		["wh3_main_character_abilities_gate_of_nurgle"] = true,
		["wh3_main_character_abilities_gate_of_slaanesh"] = true,
		["wh3_main_character_abilities_gate_of_tzeentch"] = true,
		["wh3_dlc23_hero_abilities_get_tha_gitz!"] = true,
		["wh2_dlc11_character_abilities_ghosts_of_the_past_0"] = true,
		["wh2_dlc11_character_abilities_ghosts_of_the_past_1"] = true,
		["wh2_dlc11_character_abilities_ghosts_of_the_past_2"] = true,
		["wh3_main_lord_abilities_gorger_onslaught"] = true,
		["wh3_dlc26_lord_abilities_gorger_onslaught_upgraded"] = true,
		["wh3_main_character_abilities_greater_gate_of_khorne"] = true,
		["wh3_main_character_abilities_greater_gate_of_nurgle"] = true,
		["wh3_main_character_abilities_greater_gate_of_slaanesh"] = true,
		["wh3_main_character_abilities_greater_gate_of_tzeentch"] = true,
		["wh3_main_character_abilities_guardian_call"] = true,
		["wh3_main_character_abilities_guardian_call_ii"] = true,
		["wh3_main_character_abilities_guardian_call_iii"] = true,
		["wh3_dlc25_character_abilities_guardian_of_the_forest"] = true,
		["wh2_dlc10_item_abilities_horn_of_the_ancestors"] = true,
		["wh3_dlc26_character_abilities_inventory_of_hatchlings"] = true,
		["wh3_dlc26_character_abilities_inventory_of_hatchlings_upgraded"] = true,
		["wh3_dlc29_character_abilities_invocation_of_the_lichemaster"] = true,
		["wh3_dlc29_character_abilities_invocation_of_the_lichemaster_0"] = true,
		["wh3_dlc29_character_abilities_invocation_of_the_lichemaster_1"] = true,
		["wh3_pro12_hero_abilities_karanaks_howl"] = true,
		["wh3_dlc25_character_abilities_kettles_call"] = true,
		["wh3_dlc24_hero_abilities_koldunjas_spirit"] = true,
		["wh3_main_character_abilities_locus_of_transmogrification"] = true,
		["wh_pro03_lord_abilities_lord_of_undeath"] = true,
		["wh_pro03_lord_abilities_lord_of_undeath_0"] = true,
		["wh_pro03_lord_abilities_lord_of_undeath_1"] = true,
		["wh_pro03_lord_abilities_lord_of_undeath_2"] = true,
		["wh_pro03_lord_abilities_lord_of_undeath_3"] = true,
		["wh_pro03_lord_abilities_lord_of_undeath_4"] = true,
		["wh3_dlc27_item_abilities_mask_of_the_merlord"] = true,
		["wh_dlc06_unit_abilities_maternal_instinct"] = true,
		["wh3_dlc29_hero_active_nurgling_birth"] = true,
		["wh3_dlc29_hero_active_nurgling_birth_upgraded"] = true,
		["wh3_dlc24_item_abilities_ritual_of_the_beast"] = true,
		["wh2_dlc16_lord_abilities_roused_to_wrath"] = true,
		["wh2_dlc16_lord_abilities_roused_to_wrath_2"] = true,
		["wh2_dlc11_character_abilities_sacrilege"] = true,
		["wh_dlc05_weapon_abilities_stave_of_ruinous_corruption"] = true,
		["wh3_dlc25_character_abilities_surprise_squig"] = true,
		["wh_dlc01_weapon_abilities_sword_of_change"] = true,
		["wh3_dlc29_lord_abilities_the_awakening"] = true,
		["wh3_dlc29_vmp_mon_morghast_archai_summon"] = true,
		["wh3_main_item_abilities_the_portalglyph"] = true,
		["wh3_dlc25_character_abilities_tallymans_blades"] = true,
		["wh3_dlc25_character_abilities_tallymans_blades_2"] = true,
		["wh2_dlc09_weapon_abilities_tomb_blade_of_arkhan"] = true,
		["wh3_dlc27_spell_bound_transformation_of_kadon"] = true,
		["wh3_dlc29_lord_abilities_raise_legion"] = true,
		["wh3_dlc29_lord_abilities_raise_legion_upgraded"] = true,
		["wh3_dlc26_item_tmb_liche_priest_viziers_kanopi"] = true,
		-- THE SUMMON ROUND, part 2: the nine unlabelled real spawners (D).
		["wh2_dlc16_lord_abilities_beast_pack"] = true,
		["wh2_dlc15_item_abilities_blacktoofs_conjuration"] = true,
		["wh2_dlc16_lord_abilities_call_to_gwindalor"] = true,
		["wh2_dlc16_spell_bound_vampires_lesser_raise_dead"] = true,
		["wh2_dlc17_spell_bound_savage_dominion"] = true,
		["wh3_dlc26_hero_abilities_savage_predators"] = true,
		["wh2_dlc16_hero_abilities_tide_of_death"] = true,
		["wh2_dlc16_hero_abilities_tide_of_pox"] = true,
		["wh3_main_item_abilities_zak_aloooog"] = true,
		-- THE SUMMON ROUND, part 3: The Dreaded Thirteenth's four keys (F) -
		-- an explosion plus a summon, placed on the enemy's ground.
		["wh3_dlc29_spell_bound_the_dreaded_thirteenth"] = true,
		["wh3_dlc29_spell_bound_the_dreaded_thirteenth_1"] = true,
		["wh3_dlc29_spell_bound_the_dreaded_thirteenth_thanquol"] = true,
		["wh3_dlc29_spell_bound_the_dreaded_thirteenth_thanquol_1"] = true,
		-- ROUND 106: the 24 ground-targeted bombardment keys of the
		-- enemy_ground_melee_infantry family - each cast PLACES the strike on the
		-- chosen INFANTRY enemy's own ground through the ground form.
		["wh2_dlc10_item_bound_assault_of_stone"] = true,
		["wh3_main_weapon_abilities_axe_of_tor"] = true,
		["wh3_main_mount_bound_celestial_comet"] = true,
		["wh3_main_mount_bound_celestial_lightning"] = true,
		["wh_dlc07_item_abilities_chalice_of_potions"] = true,
		["wh3_main_spell_bound_comet_of_casandora"] = true,
		["wh_dlc08_item_abilities_great_horn_of_dragon_ogre"] = true,
		["wh3_dlc23_lord_abilities_flame_and_shadow"] = true,
		["wh_dlc05_weapon_abilities_hawks_talon"] = true,
		["wh2_dlc13_character_ability_ishas_rain"] = true,
		["wh2_dlc17_spell_bound_urannons_thunderbolt_upgraded"] = true,
		["wh3_dlc29_unit_abilities_lightning_strike"] = true,
		["wh_main_lord_abilities_lord_of_the_storm"] = true,
		["wh3_dlc29_spell_bound_warp_lightning"] = true,
		["wh3_dlc29_unit_abilities_meteor_strike"] = true,
		["wh3_dlc25_lord_abilities_nemesis_crown"] = true,
		["wh_main_spell_bound_piercing_bolts_of_burning"] = true,
		["wh3_dlc25_character_abilities_pigeon_bomb"] = true,
		["wh2_main_spell_bound_rod_of_the_storm"] = true,
		["wh2_dlc10_item_abilities_sceptre_of_stone"] = true,
		["wh3_twa08_spell_bound_searing_doom"] = true,
		["wh3_dlc20_spell_bound_slicing_shards"] = true,
		["wh3_main_spell_slaanesh_slicing_shards_bound"] = true,
		["wh_dlc05_weapon_abilities_the_bow_of_loren"] = true,
		["wh2_dlc17_spell_bound_urannons_thunderbolt"] = true,
	},
	-- One line per (unit, marker) for a targeted cast with no readable target:
	-- ui id -> (marker -> true), nested and miss-safe like armed /
	-- last_attempt_at (a read never builds an inner table).
	missing_logged = {},
}

-- ============================================================================
-- THE STANDING RANGE RULE (this round, set by the user). EVERY trigger-range
-- constant in this file MUST be AT MOST 70% of the ability's REAL game-data
-- range, rounded DOWN to a whole metre. The user's words: "for abilities that
-- include a range, we should always specify 70% of the actual range to avoid
-- such things" - and, ruling it absolute, "...No exceptions." The symptom is
-- the caster WALKING toward a target that sat inside the ability's own reach
-- but outside a comfortable cast range. FOURTH.RANGE_FRACTION is that 70%;
-- every range constant below names its real range, its source, and the
-- floor(real * FOURTH.RANGE_FRACTION) derivation in the comment beside it.
-- ============================================================================
FOURTH.RANGE_FRACTION = 0.70

-- THE PER-UNIT SERIALISATION STAGGER (round 107): the minimum window a
-- unit must wait after a cast before a DIFFERENT ability may be issued
-- (the comment beside IN_FLIGHT_SETTLE_SECONDS states the why).
FOURTH.SERIAL_MIN_HOLD_SECONDS = 2.5


-- ============================================================================
-- THE ENEMY-TARGETED CAST BOUNDS (Class A, harness 97). ONE named constant per
-- REAL target_intercept_range (unit_spec_abil.tsv) - several abilities that
-- share a real range SHARE the constant. The VALUE is the trigger bound =
-- floor(real * FOURTH.RANGE_FRACTION) (70%), rounded DOWN to a whole metre
-- (the +1e-9 epsilon mirrors the build assertion's floor). The R<N> suffix is
-- the ability's REAL range in metres; the bound is the number
-- unit:unit_distance(enemy) (EDGE-TO-EDGE metres, battle_unit.lua:160) is
-- compared against - NEVER the engine's own unit_in_range reach read.
--   real  10.0 m ->   7   (the air-drop family's own cast range)
--   real  15.0 m ->  10     real  75.0 m ->  52     real 180.0 m -> 126
--   real  20.0 m ->  14     real 100.0 m ->  70     real 200.0 m -> 140
--   real  30.0 m ->  21     real 150.0 m -> 105     real 500.0 m -> 350
--   real  35.0 m ->  24     real  70.0 m ->  49
--   real  50.0 m ->  35
-- ============================================================================
FOURTH.ENEMY_CAST_R10  = 7
FOURTH.ENEMY_CAST_R15  = 10
FOURTH.ENEMY_CAST_R20  = 14
FOURTH.ENEMY_CAST_R30  = 21
FOURTH.ENEMY_CAST_R35  = 24
FOURTH.ENEMY_CAST_R45  = 31
FOURTH.ENEMY_CAST_R50  = 35
FOURTH.ENEMY_CAST_R70  = 49
FOURTH.ENEMY_CAST_R75  = 52
FOURTH.ENEMY_CAST_R90  = 63
FOURTH.ENEMY_CAST_R100 = 70
FOURTH.ENEMY_CAST_R150 = 105
FOURTH.ENEMY_CAST_R180 = 126
FOURTH.ENEMY_CAST_R200 = 140
FOURTH.ENEMY_CAST_R300 = 210
FOURTH.ENEMY_CAST_R500 = 350

-- the ability's REAL target_intercept_range -> its named 70% bound, for the
-- load-time per-ability lookup (each Class-A entry carries range_real).
FOURTH.ENEMY_CAST = {
	[10]  = FOURTH.ENEMY_CAST_R10,
	[15]  = FOURTH.ENEMY_CAST_R15,
	[20]  = FOURTH.ENEMY_CAST_R20,
	[30]  = FOURTH.ENEMY_CAST_R30,
	[35]  = FOURTH.ENEMY_CAST_R35,
	[45]  = FOURTH.ENEMY_CAST_R45,
	[50]  = FOURTH.ENEMY_CAST_R50,
	[70]  = FOURTH.ENEMY_CAST_R70,
	[75]  = FOURTH.ENEMY_CAST_R75,
	[90]  = FOURTH.ENEMY_CAST_R90,
	[100] = FOURTH.ENEMY_CAST_R100,
	[150] = FOURTH.ENEMY_CAST_R150,
	[180] = FOURTH.ENEMY_CAST_R180,
	[200] = FOURTH.ENEMY_CAST_R200,
	[300] = FOURTH.ENEMY_CAST_R300,
	[500] = FOURTH.ENEMY_CAST_R500,
}





-- ============================================================================
-- THE ALLY-TARGETED CAST BOUNDS (Class B, harness 98). ONE named constant per
-- REAL target_intercept_range (unit_spec_abil.tsv) - several abilities that
-- share a real range SHARE the constant (stated per line below). The VALUE is
-- the trigger bound = floor(real * FOURTH.RANGE_FRACTION) (70%), rounded DOWN
-- to a whole metre (the +1e-9 epsilon mirrors the build assertion's floor).
-- The offer test is unit:unit_distance(ally) (EDGE-TO-EDGE metres,
-- battle_unit.lua:160) - NEVER the engine's own unit_in_range reach read.
--   real  50.0 m ->  35  (shared: captain_of_the_phoenix_guard, helping_hand,
--                          elfish_healing_herbs)
--   real  60.0 m ->  42  (stay_here_ill_get_help)
--   real  75.0 m ->  52  (hellish_vigour)
--   real 100.0 m ->  70  (shared: favour_of_the_fay, inspired_assault_i/_ii/
--                          _iii, inspired_defence_i/_ii/_iii, shock_collar,
--                          were_you_goin, patch_up, revivification_crystal)
--   real 150.0 m -> 105  (shared: da_boss_as_a_plan, orcs_are_da_best)
-- ============================================================================
FOURTH.ALLY_CAST_R50  = 35
FOURTH.ALLY_CAST_R60  = 42
FOURTH.ALLY_CAST_R75  = 52
FOURTH.ALLY_CAST_R100 = 70
FOURTH.ALLY_CAST_R150 = 105
FOURTH.ALLY_CAST_R200 = 140

-- the ability's REAL target_intercept_range -> its named 70% ALLY bound, for
-- the load-time per-ability lookup (each Class-B entry carries ally_range_real).
FOURTH.ALLY_CAST = {
	[50]  = FOURTH.ALLY_CAST_R50,
	[60]  = FOURTH.ALLY_CAST_R60,
	[75]  = FOURTH.ALLY_CAST_R75,
	[100] = FOURTH.ALLY_CAST_R100,
	[150] = FOURTH.ALLY_CAST_R150,
	[200] = FOURTH.ALLY_CAST_R200,
}
-- true / false / nil - only exact true means "morale below the threshold".
function FOURTH.wavering(unit)
	local ok, wavering = pcall(function() return unit:is_wavering() end)
	if ok then
		if wavering == true then return true end
		if wavering == false then return false end
	end
	return nil
end

function FOURTH.is_ground_key(ability_key)
	return FOURTH.ground_keys[ability_key] == true
end

-- THE TARGETED-CAST HELPER (reusable by any later targeted ability): read the
-- caster's own ground position, then issue the ground form of the call.
-- Returns ok_call, err_call, no_target - no_target true means NOTHING was
-- fired because the position could not be read (the caller must not fire).
function FOURTH.ground_cast(uc, unit, ability_key)
	local ok_pos, pos = pcall(function() return unit:position() end)
	if not ok_pos or pos == nil then
		return nil, nil, true
	end
	local ok_call, err_call = pcall(function()
		uc:perform_special_ability_ground(ability_key, pos, 0, 0)
	end)
	return ok_call, err_call, false
end

-- THE ENEMY-GROUND CAST HELPER (Class A, harness 97): the same shape as
-- ground_cast, but the position is the CHOSEN ENEMY's own ground position
-- (enemy:position()) - the placement an enemy-GROUND area hex requires. The
-- controller is the FRESH one (FOURTH.eg_caster_su.uc); a position that
-- cannot be read returns no_target = true (the caller must not fire).
function FOURTH.enemy_ground_cast(uc, enemy, ability_key)
	local ok_pos, pos = pcall(function() return enemy:position() end)
	if not ok_pos or pos == nil then
		return nil, nil, true
	end
	local ok_call, err_call = pcall(function()
		uc:perform_special_ability_ground(ability_key, pos, 0, 0)
	end)
	return ok_call, err_call, false
end

-- THE ALLY-GROUND CAST HELPER (this round, Star of Avelorn): the same shape as
-- enemy_ground_cast, but the position is the CHOSEN FRIENDLY UNIT's own ground
-- position - the placement a `target_ground_under_allies` area heal requires.
-- The controller passed in is the FRESH one (FOURTH.ah_caster_su.uc). A
-- position that cannot be read returns no_target = true (the caller must not
-- fire): the mod never places an area heal on a guessed point.
function FOURTH.ally_ground_cast(uc, ally, ability_key)
	local ok_pos, pos = pcall(function() return ally:position() end)
	if not ok_pos or pos == nil then
		return nil, nil, true
	end
	local ok_call, err_call = pcall(function()
		uc:perform_special_ability_ground(ability_key, pos, 0, 0)
	end)
	return ok_call, err_call, false
end

-- THE CONTEXT-VALUE READ (BLOCK 2, this round): the live per-unit values the
-- new triggers need - the barrier and the health percentage. The vanilla-
-- proven read is common.get_context_value("CcoBattleUnit", <ui id>, <field>)
-- (the same call the shipped UI binds its barrier/health fields through). The
-- unit's own unique_ui_id is the object id. BOTH calls are pcall-guarded and
-- a failure answers nil - every caller treats nil as "cannot read" and stays
-- SILENT (fail-closed for these triggers: never fire on a guessed value).
function FOURTH.context_value(unit, field)
	local ok_id, id = pcall(function() return unit:unique_ui_id() end)
	if not ok_id or id == nil then return nil end
	local ok, value = pcall(function()
		return common.get_context_value("CcoBattleUnit", id, field)
	end)
	if not ok then return nil end
	return value
end


local function attempt_activation(script_unit, unit, ability_key, reason, ui_id, marker, quiet, target)
	-- PRE-FIRE VALIDITY (this build): re-verify the unit is still usable
	-- immediately before the call. A unit that is gone answers nothing, so it
	-- is dropped at once - ONE line, and the fire is never attempted (this
	-- check sits BEFORE the ATTEMPT line, so no attempt is ever logged for it).
	if unit_is_gone(unit) then
		log("unit " .. tostring(ui_id) .. " is gone (pre-fire check)"
			.. " - dropped from tracking")
		return "gone"
	end

	-- The armed-check outcome rides on the attempt line itself (once per
	-- attempt): by the time an attempt runs, this unit's pair is armed. The
	-- line is BUILT here (its unit:type() read stays where it always was) but
	-- WRITTEN only for an ordinary attempt: a quiet re-probe inside a cooldown
	-- hold is silent unless it actually FIRES (see below), and a fire is never
	-- suppressed.
	local attempt_line = "ATTEMPT " .. tostring(marker) .. " '" .. ability_key .. "' on '" .. tostring(unit:type())
		.. "' ui id " .. tostring(ui_id) .. " | reason: " .. reason
		.. " | armed=" .. (is_armed(unit, marker) and "ON" or "OFF")
	if not quiet then
		log(attempt_line)
	end

	-- THE PROVEN FRESH-HANDLE ROUTE (Accusation, this round): when the enemy
	-- trigger chose a target, use the CASTER script_unit re-fetched FRESH from
	-- the friendly enumerator THIS tick (never a controller held from an
	-- earlier poll - the round-4 log-proven bench_fresh shape). Falls back to
	-- the poll's own script_unit if the fresh fetch failed.
	local uc = script_unit.uc
	if FOURTH.eg_enemy ~= nil and FOURTH.eg_caster_su ~= nil and FOURTH.eg_caster_su.uc ~= nil then
		uc = FOURTH.eg_caster_su.uc
	end
	-- CLASS B (harness 98): the ALLY-TARGETED cast uses the FRESH caster
	-- controller AND the FRESH ally unit, both re-enumerated from the local
	-- player's army list THIS tick - a controller held from an earlier poll
	-- silently no-ops. The chosen ally is the CAST TARGET - NEVER the owner.
	if FOURTH.ab_ally ~= nil then
		if FOURTH.ab_caster_su ~= nil and FOURTH.ab_caster_su.uc ~= nil then
			uc = FOURTH.ab_caster_su.uc
		end
		if FOURTH.ab_ally_su ~= nil and FOURTH.ab_ally_su.unit ~= nil then
			target = FOURTH.ab_ally_su.unit
		end
	end
	-- THE ALLY-AWARE HEALTH FAMILY (this round): the caster's controller is the
	-- FRESH one for every arm (aura, ally or self), and the UNIT form targets the
	-- FRESH chosen ALLY. The GROUND form (ah_ground) reads that ally's own
	-- position at the call itself, below.
	if FOURTH.ah_caster_su ~= nil and FOURTH.ah_caster_su.uc ~= nil then
		uc = FOURTH.ah_caster_su.uc
	end
	if FOURTH.ah_ally ~= nil and FOURTH.ah_ally_su ~= nil and FOURTH.ah_ally_su.unit ~= nil then
		if not FOURTH.ah_ground and not FOURTH.ah_selfaura then
			target = FOURTH.ah_ally_su.unit
		end
	end
	-- SELF-SUMMON (harness 102, Nurgling Tide): the cast is on the OWNER and
	-- the controller is the CASTER's script_unit re-fetched FRESH this tick
	-- (the same discipline as every other cast in this file).
	if FOURTH.ss_self then
		if FOURTH.ss_caster_su ~= nil and FOURTH.ss_caster_su.uc ~= nil then
			uc = FOURTH.ss_caster_su.uc
		end
		target = unit
	end
	-- TZ'ARKAN (this round): the cast is on the OWNER and the controller is the
	-- CASTER's script_unit re-fetched FRESH this tick (the same discipline as
	-- every other cast in this file). A self cast has no target choice to make.
	if FOURTH.tz_self then
		if FOURTH.tz_caster_su ~= nil and FOURTH.tz_caster_su.uc ~= nil then
			uc = FOURTH.tz_caster_su.uc
		end
		target = unit
	end
	-- THE AIR-DROP FAMILY (round 107): the cast is SELF-CENTRED (the row has
	-- no target flags at all), so the target stays the OWNER - and the
	-- controller is the CASTER's script_unit re-fetched FRESH this tick, like
	-- every other cast here. The chosen enemy is the justification for the
	-- press, never the cast target.
	if FOURTH.ad_caster_su ~= nil and FOURTH.ad_caster_su.uc ~= nil then
		uc = FOURTH.ad_caster_su.uc
	end

	if uc == nil then
		log("  STOP: script_unit.uc is nil - there is no controller to order")
		return
	end

	local took_control = false

	if TAKE_CONTROL_FIRST then
		local ok_take, err_take = pcall(function() uc:take_control() end)
		took_control = ok_take
		log("  take_control            : ok=" .. tostring(ok_take)
			.. (ok_take and "" or ("  ERROR: " .. tostring(err_take))))
	end

	local _, can_before = pcall(function()
		return unit:can_perform_special_ability(ability_key)
	end)
	if not quiet then
		log("  can_perform before      : " .. tostring(can_before))
	end

	-- GLORIOUS DEATH RANGE RE-CHECK (this round). The Slayer-ally arm chose
	-- the CLOSEST in-melee Slayer within GLORIOUS_DEATH_RANGE_M at evaluate
	-- time and left it in FOURTH.gd_ally; RE-READ the gap NOW, immediately
	-- before the cast - a unit can move a little between the poll and the
	-- cast. If the ally has drifted beyond the 38 m trigger range (70% of
	-- the ability's 55 m aura) the cast is wasted, so SKIP it rather than spend it.
	-- The owner-in-melee self arm leaves FOURTH.gd_ally nil - never gated.
	if FOURTH.gd_ally ~= nil and not FOURTH.gd_ally_in_range(unit, FOURTH.gd_ally) then
		log("  glorious_death SKIPPED: the chosen in-melee Slayer ally drifted out of range"
			.. " before the cast (the aura would not cover it) - cast not spent")
		FOURTH.gd_ally = nil
		if RELEASE_CONTROL_AFTER and took_control then
			local ok_release, err_release = pcall(function() uc:release_control() end)
			log("  release_control         : ok=" .. tostring(ok_release)
				.. (ok_release and "" or ("  ERROR: " .. tostring(err_release))))
		end
		return "held"
	end

	-- WILL OF THE VERMINKING RANGE RE-CHECK (this round): the same safety
	-- pattern as Glorious Death. The ally arm chose the CLOSEST in-range
	-- wavering in-melee ally at evaluate time and left it in FOURTH.vm_ally;
	-- RE-READ the gap NOW, immediately before the cast. If the ally has drifted
	-- out of range the cast is wasted, so SKIP it rather than spend it.
	if FOURTH.vm_ally ~= nil and not FOURTH.vm_ally_in_range(unit, FOURTH.vm_ally) then
		log("  will_of_the_verminking SKIPPED: the chosen wavering ally drifted out of range"
			.. " before the cast (the aura would not cover it) - cast not spent")
		FOURTH.vm_ally = nil
		if RELEASE_CONTROL_AFTER and took_control then
			local ok_release, err_release = pcall(function() uc:release_control() end)
			log("  release_control         : ok=" .. tostring(ok_release)
				.. (ok_release and "" or ("  ERROR: " .. tostring(err_release))))
		end
		return "held"
	end


	-- ENCHANTED METALLURGY RANGE RE-CHECK (this round): the same safety pattern
	-- as Glorious Death / Will of the Verminking. The ALLY arm chose the CLOSEST
	-- in-range in-melee ally at evaluate time and left it in FOURTH.mtl_ally;
	-- RE-READ the gap NOW, immediately before the cast. If the ally has drifted
	-- out of range the cast is wasted, so SKIP it rather than spend it. The
	-- owner-in-melee self arm leaves FOURTH.mtl_ally nil - never gated.
	if FOURTH.mtl_ally ~= nil and not FOURTH.mtl_ally_in_range(unit, FOURTH.mtl_ally) then
		log("  enchanted_metallurgy SKIPPED: the chosen in-melee ally drifted out of range"
			.. " before the cast (the aura would not cover it) - cast not spent")
		FOURTH.mtl_ally = nil
		if RELEASE_CONTROL_AFTER and took_control then
			local ok_release, err_release = pcall(function() uc:release_control() end)
			log("  release_control         : ok=" .. tostring(ok_release)
				.. (ok_release and "" or ("  ERROR: " .. tostring(err_release))))
		end
		return "held"
	end

	-- WAVERING SELF-OR-ALLY RANGE RE-CHECK (blocks 7-9): the same safety pattern
	-- as Glorious Death / Verminking / Metallurgy. The ALLY arm chose the
	-- CLOSEST in-range in-melee wavering ally and left it in FOURTH.ws_ally;
	-- RE-READ the gap NOW, immediately before the cast. If the ally has drifted
	-- out of range the cast is wasted, so SKIP it rather than spend it. The
	-- self-wavering arm leaves FOURTH.ws_ally nil - never gated.
	if FOURTH.ws_ally ~= nil and not FOURTH.ws_ally_in_range(unit, FOURTH.ws_ally) then
		log("  wavering_self_or_ally SKIPPED: the chosen wavering ally drifted out of range"
			.. " before the cast (the aura would not cover it) - cast not spent")
		FOURTH.ws_ally = nil
		if RELEASE_CONTROL_AFTER and took_control then
			local ok_release, err_release = pcall(function() uc:release_control() end)
			log("  release_control         : ok=" .. tostring(ok_release)
				.. (ok_release and "" or ("  ERROR: " .. tostring(err_release))))
		end
		return "held"
	end

	-- WAVERING ALLY IN RANGE RE-CHECK (blocks 7-9): the same safety pattern.
	-- The ally arm chose the CLOSEST in-range wavering ally and left it in
	-- FOURTH.wa_ally; RE-READ the gap NOW, immediately before the cast. If the
	-- ally has drifted out of range, SKIP rather than waste the cast.
	if FOURTH.wa_ally ~= nil and not FOURTH.wa_ally_in_range(unit, FOURTH.wa_ally) then
		log("  wavering_ally_range SKIPPED: the chosen wavering ally drifted out of range"
			.. " before the cast (the aura would not cover it) - cast not spent")
		FOURTH.wa_ally = nil
		if RELEASE_CONTROL_AFTER and took_control then
			local ok_release, err_release = pcall(function() uc:release_control() end)
			log("  release_control         : ok=" .. tostring(ok_release)
				.. (ok_release and "" or ("  ERROR: " .. tostring(err_release))))
		end
		return "held"
	end

	-- BLOOD SACRIFICE / EAT DA RUNTS ALLY RE-CHECK (this round): the same
	-- safety pattern as Glorious Death / Verminking / Metallurgy. The ally arm
	-- chose a LOW-HEALTH ally and left it in FOURTH.bs_ally / FOURTH.edr_ally;
	-- RE-READ the gap AND the ally's health NOW, immediately before the cast.
	-- If the ally has drifted out of range or healed above the 75% line the cast
	-- is wasted, so SKIP it rather than spend it. The Eat-da-Runts self arm
	-- leaves FOURTH.edr_ally nil - never gated (casting on self is always in
	-- range).
	if FOURTH.bs_ally ~= nil and not FOURTH.bs_ally_valid(unit, FOURTH.bs_ally) then
		log("  blood_sacrifice SKIPPED: the chosen ally drifted out of range or healed above 75%"
			.. " before the cast - cast not spent")
		FOURTH.bs_ally = nil
		if RELEASE_CONTROL_AFTER and took_control then
			local ok_release, err_release = pcall(function() uc:release_control() end)
			log("  release_control         : ok=" .. tostring(ok_release)
				.. (ok_release and "" or ("  ERROR: " .. tostring(err_release))))
		end
		return "held"
	end
	if FOURTH.edr_ally ~= nil and not FOURTH.edr_ally_valid(unit, FOURTH.edr_ally) then
		log("  eat_da_runts SKIPPED: the chosen ally drifted out of range or healed above 75%"
			.. " before the cast - cast not spent")
		FOURTH.edr_ally = nil
		if RELEASE_CONTROL_AFTER and took_control then
			local ok_release, err_release = pcall(function() uc:release_control() end)
			log("  release_control         : ok=" .. tostring(ok_release)
				.. (ok_release and "" or ("  ERROR: " .. tostring(err_release))))
		end
		return "held"
	end

	-- CLASS B ALLY-TARGETED RE-CHECK (harness 98): the ally trigger chose a
	-- friendly unit and left it in FOURTH.ab_ally (the cast target is the same
	-- unit, in FOURTH.cast_target); RE-READ the condition NOW, immediately
	-- before the cast - the ally must still be ALIVE and still WITHIN the
	-- ability's 70% bound, which is RE-READ here via the engine's
	-- `unit:unit_distance(ally)` (EDGE-TO-EDGE metres, battle_unit.lua:160) and
	-- whose REAL value is logged. If it lapsed the cast is wasted, so SKIP it
	-- rather than spend it. The chosen ally is the CAST TARGET - NEVER the owner.
	if FOURTH.ab_ally ~= nil then
		local ab_marker_now = FOURTH.ab_marker or "ally"
		local ab_bound_now = FOURTH.ab_range_m
		local ally = FOURTH.ab_ally
		local ok_alive, alive = pcall(function() return ally:number_of_men_alive() end)
		local alive_now = (ok_alive and type(alive) == "number" and alive > 0)
		local gap_now = FOURTH.ab_ally_gap(unit, ally)
		local in_bound_now = FOURTH.ab_gap_ok(gap_now)
		local hp_ok_now = true
		if FOURTH.ab_family == "heal" then
			local hp = FOURTH.health_pct(ally)
			hp_ok_now = (type(hp) ~= "number") or (hp <= 75)
		end
		-- ROUND 130: Restock! - the ally must still be shooting and still at or
		-- below the line (a refill on a unit that stopped is wasted).
		if FOURTH.ab_family == "ammo" then
			local fr = FOURTH.ammo_fraction_if_firing(ally)
			hp_ok_now = (fr ~= nil) and (fr <= FOURTH.RESTOCK_AT_FRACTION)
		end
		-- ROUND 131: the shooting family - the ally must still be shooting
		if FOURTH.ab_family == "shooting" then
			hp_ok_now = FOURTH.shooting_past_cast_point(ally)
		end
		if FOURTH.ab_family == "fighting" then
			hp_ok_now = FOURTH.fighting(ally)
		end
		if not alive_now or not in_bound_now or not hp_ok_now then
			log("  " .. ab_marker_now .. " SKIPPED: the chosen ally lapsed before the cast"
				.. " (alive=" .. tostring(alive_now) .. " healthy=" .. tostring(hp_ok_now)
				.. ((gap_now ~= nil) and (" distance=" .. string.format("%.1f", gap_now) .. "m") or " distance=?")
				.. " bound=" .. FOURTH.ab_bound_text() .. ") - cast not spent")
			FOURTH.ab_ally = nil
			if RELEASE_CONTROL_AFTER and took_control then
				local ok_release, err_release = pcall(function() uc:release_control() end)
				log("  release_control         : ok=" .. tostring(ok_release)
					.. (ok_release and "" or ("  ERROR: " .. tostring(err_release))))
			end
			return "held"
		end
		log("  " .. ab_marker_now .. " pre-cast re-check: the chosen ally is still valid ("
			.. tostring(FOURTH.ab_family) .. ", distance="
			.. ((gap_now ~= nil) and string.format("%.1f", gap_now) or "?")
			.. " bound=" .. FOURTH.ab_bound_text() .. ") - firing")
	end

	-- ENEMY-TARGETED RE-CHECK (Class A, harness 97): the enemy trigger chose an
	-- unit and left it in FOURTH.eg_enemy (the cast target is the same unit,
	-- in FOURTH.cast_target); RE-READ the condition NOW, immediately before the
	-- cast - the enemy must still be ALIVE and still satisfy ITS OWN trigger
	-- (in melee / under fire for the Class-A pickers, IN MELEE for Gate of
	-- Khorne, BELOW 20% HEALTH AND NOT A LORD OR HERO for the Eye of Khorne
	-- finisher, IN MELEE AND NOT A LORD OR HERO for The Dreaded Thirteenth) and
	-- still within the ability's own 70% bound, RE-READ here via the engine's
	-- `unit:unit_distance(enemy)` (EDGE-TO-EDGE metres, battle_unit.lua:160) and
	-- whose REAL value is logged. If it lapsed the cast is wasted, so SKIP it
	-- rather than spend it. The chosen enemy is the CAST TARGET - NEVER the
	-- owner.
	if FOURTH.eg_enemy ~= nil then
		local enemy = FOURTH.eg_enemy
		local eg_marker_now = FOURTH.eg_marker or "accusation"
		-- A "no bound" entry (the game row declares target_intercept_range =
		-- -1.0: no real range to take 70% of) skips the distance test entirely.
		local eg_unbounded_now = (FOURTH.eg_no_bound == true)
		local eg_bound_now = FOURTH.eg_range_m or FOURTH.ACCUSATION_RANGE_M
		local eg_bound_text = tostring(eg_bound_now) .. "m"
		if eg_unbounded_now then eg_bound_text = "none" end
		-- GATE OF KHORNE (harness 101): a melee-only choice must STILL be
		-- fighting; the missile arm is never a substitute for it.
		local eg_melee_only_now = (FOURTH.eg_melee_only == true)
		-- THE SUMMON-ROUND MODES (harness 102): the finisher (mode "health")
		-- and The Dreaded Thirteenth (mode "melee") own their conditions; every
		-- older enemy trigger leaves the mode nil.
		local eg_mode_now = FOURTH.eg_mode
		local ok_alive, alive = pcall(function() return enemy:number_of_men_alive() end)
		local ok_melee, melee = pcall(function() return enemy:is_in_melee() end)
		local still_melee = (ok_melee and melee == true)
		local still_shot = false
		if (not still_melee) and (not eg_melee_only_now) and eg_mode_now == nil then
			still_shot = FOURTH.eg_under_missile_attack(enemy)
		end
		local alive_now = (ok_alive and type(alive) == "number" and alive > 0)
		-- RE-READ the bound NOW via the engine's edge-to-edge distance and log
		-- its REAL value (the same primitive the offer test used).
		local gap_now = FOURTH.eg_enemy_gap(unit, enemy)
		local in_bound_now = eg_unbounded_now or (gap_now ~= nil and gap_now <= eg_bound_now)
		local cond_now = (still_melee or still_shot)
		local hp_now = nil
		if eg_mode_now == "health" then
			hp_now = FOURTH.enemy_health_pct(enemy)
			cond_now = (hp_now ~= nil and hp_now < FOURTH.HEALTH_LINE_PCT)
		elseif eg_mode_now == "melee" then
			cond_now = still_melee
		elseif eg_mode_now == "fast" then
			-- ROUND 135: still moving fast and close to one of our units
			cond_now = (FOURTH.fast_enemy_near(enemy, unit) ~= nil)
		end
		local cmdr_now = false
		if FOURTH.eg_noncommander then
			cmdr_now = FOURTH.enemy_is_commander(enemy)
		end
		-- ROUND 106: an INFANTRY choice is re-verified NOW, like the
		-- commander exclusion - a unit that died, left melee or is no
		-- longer readable as infantry makes the cast be skipped.
		local inf_now = true
		if FOURTH.eg_infantry then
			inf_now = FOURTH.enemy_is_infantry(enemy)
		end
		local hp_text_now = ""
		if hp_now ~= nil then
			hp_text_now = " health=" .. string.format("%.0f", hp_now) .. "%"
		end
		-- ROUND 135: the entry's target class (Lord/Hero, large) is re-checked too
		if not alive_now or not cond_now or cmdr_now or not inf_now or not in_bound_now
			or not FOURTH.eg_class_ok(enemy) then
			log("  " .. eg_marker_now .. " SKIPPED: the chosen enemy lapsed before the cast"
				.. " (alive=" .. tostring(alive_now) .. " melee=" .. tostring(still_melee)
				.. " shot=" .. tostring(still_shot)
				.. " melee_only=" .. tostring(eg_melee_only_now)
				.. " mode=" .. tostring(eg_mode_now) .. hp_text_now
				.. " infantry=" .. tostring(inf_now)
				.. " commander=" .. tostring(cmdr_now)
				.. ((gap_now ~= nil) and (" distance=" .. string.format("%.1f", gap_now) .. "m") or " distance=?")
				.. " bound=" .. eg_bound_text .. ") - cast not spent")
			FOURTH.eg_enemy = nil
			FOURTH.eg_arm = nil
			if RELEASE_CONTROL_AFTER and took_control then
				local ok_release, err_release = pcall(function() uc:release_control() end)
				log("  release_control         : ok=" .. tostring(ok_release)
					.. (ok_release and "" or ("  ERROR: " .. tostring(err_release))))
			end
			return "held"
		end
		log("  " .. eg_marker_now .. " pre-cast re-check: target still engaged (" .. tostring(FOURTH.eg_arm)
			.. ", melee=" .. tostring(still_melee) .. " shot=" .. tostring(still_shot)
			.. " melee_only=" .. tostring(eg_melee_only_now)
			.. " mode=" .. tostring(eg_mode_now) .. hp_text_now
			.. " infantry=" .. tostring(inf_now)
			.. ", distance=" .. ((gap_now ~= nil) and string.format("%.1f", gap_now) or "?")
			.. "m bound=" .. eg_bound_text .. ") - firing")
	end

	-- THE AIR-DROP RE-CHECK (round 114, re-measured on the CENTRE in round 117,
	-- delay evidence removed in round 118). Immediately before the call the
	-- CASTER must still be ALIVE, still AIRBORNE where its row is air-only and
	-- still OUT of melee where the engine forbids it; the CHOSEN ENEMY must
	-- still be alive with MORE THAN AIR_DROP_MIN_MEN models, and its CENTRE gap
	-- must still be under AIR_DROP_CENTER_M. The enemy reads and the distance
	-- are RE-TAKEN here from FRESH handles - the same number_of_men_alive() read
	-- and the SAME ad_centre_gap measurement the picker used, so the two
	-- readings cannot disagree - and a lapsed condition SKIPS the cast rather
	-- than spending it. There is NO WAIT to verify any more: the trigger fires on
	-- the evaluation that measured the centre inside the line, so the one
	-- question left is whether it is STILL inside it.
	-- Every number that decided it is written, with `-> SKIPPED at re-check`, and
	-- the gap it prints is the CENTRE gap re-measured on this line.
	if FOURTH.ad_enemy ~= nil then
		local enemy = FOURTH.ad_enemy
		local ad_marker_now = FOURTH.ad_marker or "air_drop"
		local ok_alive, alive = pcall(function() return unit:number_of_men_alive() end)
		local caster_alive = (ok_alive and type(alive) == "number" and alive > 0)
		local fly_now, fly_readable = true, true
		if FOURTH.ad_air_only then
			local ok_fly, v = pcall(function() return unit:is_currently_flying() end)
			fly_readable = ok_fly
			fly_now = (ok_fly and v == true)
		end
		local melee_now, melee_readable = false, true
		if FOURTH.ad_no_melee then
			local ok_m, m = pcall(function() return unit:is_in_melee() end)
			melee_readable = ok_m
			melee_now = (ok_m and m == true)
		end
		local ok_ea, ea = pcall(function() return enemy:number_of_men_alive() end)
		local enemy_alive = (ok_ea and type(ea) == "number" and ea > 0)
		local men_ok = (ok_ea and type(ea) == "number" and ea > FOURTH.AIR_DROP_MIN_MEN)
		local centre_now = FOURTH.ad_centre_gap(unit, enemy)
		local centre_ok = (centre_now ~= nil and centre_now < FOURTH.AIR_DROP_CENTER_M)
		local centre_text = ((centre_now ~= nil) and (string.format("%.2f", centre_now) .. "m") or "?")
		local men_text = ((ok_ea and type(ea) == "number") and tostring(ea) or "?")
		if not (caster_alive and fly_readable and fly_now and melee_readable
			and (not melee_now) and enemy_alive and men_ok and centre_ok) then
			log("  " .. FOURTH.ad_tag(unit) .. ad_marker_now .. " nearest valid:'"
				.. (FOURTH.type_plain(enemy) or "enemy") .. "' entities=" .. men_text
				.. " centre=" .. centre_text .. " (need < "
				.. string.format("%.2f", FOURTH.AIR_DROP_CENTER_M) .. "m) -> SKIPPED at re-check"
				.. " (caster_alive=" .. tostring(caster_alive) .. " flying=" .. tostring(fly_now)
				.. " melee=" .. tostring(melee_now) .. " enemy_alive=" .. tostring(enemy_alive)
				.. " over_min_men=" .. tostring(men_ok) .. " centre_ok=" .. tostring(centre_ok)
				.. " min_men=" .. tostring(FOURTH.AIR_DROP_MIN_MEN) .. ") - cast not spent")
			FOURTH.ad_enemy = nil
			if RELEASE_CONTROL_AFTER and took_control then
				local ok_release, err_release = pcall(function() uc:release_control() end)
				log("  release_control         : ok=" .. tostring(ok_release)
					.. (ok_release and "" or ("  ERROR: " .. tostring(err_release))))
			end
			return "held"
		end
		log("  " .. FOURTH.ad_tag(unit) .. ad_marker_now .. " nearest valid:'"
			.. (FOURTH.type_plain(enemy) or "enemy") .. "' entities=" .. men_text
			.. " centre=" .. centre_text .. " (need < "
			.. string.format("%.2f", FOURTH.AIR_DROP_CENTER_M) .. "m) -> FIRING (re-checked)")
	end

	-- SELF-SUMMON RE-CHECK (harness 102, Nurgling Tide). The user's rule:
	-- "that one should only trigger when the caster himself is in melee."
	-- Immediately before the call the OWNER must still be ALIVE and still IN
	-- MELEE. NO RANGE BOUND is read or needed here: the cast is on the OWNER
	-- itself, so there is no distance to measure and none is logged as a gap.
	if FOURTH.ss_self then
		local ok_alive, alive = pcall(function() return unit:number_of_men_alive() end)
		local ok_melee, melee = pcall(function() return unit:is_in_melee() end)
		local alive_now = (ok_alive and type(alive) == "number" and alive > 0)
		local melee_now = (ok_melee and melee == true)
		if not alive_now or not melee_now then
			log("  " .. tostring(FOURTH.eg_marker) .. " SKIPPED: the caster left melee before the self cast"
				.. " (alive=" .. tostring(alive_now) .. " melee=" .. tostring(melee_now)
				.. ", no range bound - self cast) - cast not spent")
			FOURTH.ss_self = nil
			if RELEASE_CONTROL_AFTER and took_control then
				local ok_release, err_release = pcall(function() uc:release_control() end)
				log("  release_control         : ok=" .. tostring(ok_release)
					.. (ok_release and "" or ("  ERROR: " .. tostring(err_release))))
			end
			return "held"
		end
		log("  " .. tostring(FOURTH.eg_marker) .. " pre-cast re-check: the caster is still in melee"
			.. " (alive=" .. tostring(alive_now) .. " melee=" .. tostring(melee_now)
			.. ", no range bound - self cast) - firing")
	end

	-- TZ'ARKAN'S PRE-CAST RE-CHECK (this round). The user's rule is health
	-- BELOW 15%, so immediately before the call the OWNER must still be ALIVE
	-- and its health - re-read through the ONE reader - must still be BELOW the
	-- line: a unit that died, or was healed above it, inside the wind-up would
	-- otherwise spend a one-way transform for nothing. The EXACT percentage is
	-- written at the decision (the ATTEMPT reason) and again here. An
	-- UNREADABLE health read does not block a cast the trigger already
	-- justified - the file's standing fail-open rule for an auxiliary read.
	if FOURTH.tz_self then
		local ok_alive, alive = pcall(function() return unit:number_of_men_alive() end)
		local alive_now = (ok_alive and type(alive) == "number" and alive > 0)
		local hp_now = FOURTH.health_pct(unit)
		local hp_text = ((type(hp_now) == "number") and (string.format("%.1f", hp_now) .. "%") or "?")
		local hp_ok = (type(hp_now) ~= "number") or (hp_now < FOURTH.TZARKAN_PCT)
		if not alive_now or not hp_ok then
			log("  tzarkan SKIPPED: the caster lapsed before the cast (alive="
				.. tostring(alive_now) .. ", health=" .. hp_text
				.. ", the line is BELOW " .. tostring(FOURTH.TZARKAN_PCT)
				.. "%, no range bound - self cast) - cast not spent")
			FOURTH.tz_self = nil
			if RELEASE_CONTROL_AFTER and took_control then
				local ok_release, err_release = pcall(function() uc:release_control() end)
				log("  release_control         : ok=" .. tostring(ok_release)
					.. (ok_release and "" or ("  ERROR: " .. tostring(err_release))))
			end
			return "held"
		end
		log("  tzarkan pre-cast re-check: the caster is still below the line (alive="
			.. tostring(alive_now) .. ", health=" .. hp_text .. " of BELOW "
			.. tostring(FOURTH.TZARKAN_PCT) .. "%, no range bound - self cast) - firing")
	end

	-- THE ALLY-AWARE HEALTH FAMILY RE-CHECK (this round). The chosen unit is
	-- re-read immediately before the call: it must still be ALIVE and still at
	-- or below 75%, and an ALLY must still be inside the ability's own reach.
	-- A lapsed condition means the cast is NOT made (a wasted cast is worse than
	-- a retry on the next poll). An UNREADABLE health read does not block a cast
	-- the trigger already justified - the file's standing rule for an auxiliary
	-- read is fail-open. Every number that decided it is written.
	if FOURTH.ah_ally ~= nil or FOURTH.ah_ground or FOURTH.ah_selfaura then
		local chosen = FOURTH.ah_chosen or FOURTH.ah_ally or unit
		local ok_alive, alive = pcall(function() return chosen:number_of_men_alive() end)
		local alive_now = (ok_alive and type(alive) == "number" and alive > 0)
		local hp_now = FOURTH.health_pct(chosen)
		local gap_now = nil
		local in_reach = true
		if FOURTH.ah_ally ~= nil then
			gap_now = FOURTH.ab_ally_gap(unit, chosen)
			in_reach = (FOURTH.ah_range_m == nil) or (gap_now == nil) or (gap_now <= FOURTH.ah_range_m)
		end
		local hp_ok = (type(hp_now) ~= "number") or (hp_now <= 75)
		local who = "the caster"
		if FOURTH.ah_ally ~= nil then
			who = "the chosen ALLY"
		elseif FOURTH.ah_selfaura then
			who = "the unit that armed this aura"
		end
		if not (alive_now and in_reach and hp_ok) then
			log("  " .. tostring(FOURTH.ah_marker) .. " SKIPPED: " .. who
				.. " lapsed before the cast (alive=" .. tostring(alive_now)
				.. ", health=" .. ((type(hp_now) == "number") and (string.format("%.0f", hp_now) .. "%") or "?")
				.. ", distance=" .. ((gap_now ~= nil) and (string.format("%.1f", gap_now) .. "m") or "?")
				.. " of " .. tostring(FOURTH.ah_range_m) .. "m " .. tostring(FOURTH.ah_range_word)
				.. ") - cast not spent")
			FOURTH.ah_ally = nil
			FOURTH.ah_ally_su = nil
			FOURTH.ah_chosen = nil
			FOURTH.ah_ground = false
			FOURTH.ah_selfaura = false
			FOURTH.cast_target = nil
			if RELEASE_CONTROL_AFTER and took_control then
				local ok_release, err_release = pcall(function() uc:release_control() end)
				log("  release_control         : ok=" .. tostring(ok_release)
					.. (ok_release and "" or ("  ERROR: " .. tostring(err_release))))
			end
			return "held"
		end
		log("  " .. tostring(FOURTH.ah_marker) .. " pre-cast re-check: " .. who
			.. " is still there (alive=" .. tostring(alive_now)
			.. ", health=" .. ((type(hp_now) == "number") and (string.format("%.0f", hp_now) .. "%") or "?")
			.. ", distance=" .. ((gap_now ~= nil) and (string.format("%.1f", gap_now) .. "m") or "?")
			.. " of " .. tostring(FOURTH.ah_range_m) .. "m " .. tostring(FOURTH.ah_range_word) .. ") - firing")
	end

	-- THE CALL. Ordinary keys (self- or unit-targeted) use the proven
	-- perform_special_ability(key, unit). A GROUND-TARGETED key (section 7e)
	-- uses the engine's own position form,
	-- perform_special_ability_ground(ability_key, position, ...), with the
	-- caster's own ground position - the correct call for a key whose db row
	-- has target_ground = true.
	local ok_call, err_call, no_target
	if FOURTH.ah_ground then
		-- ALLY-GROUND AREA HEAL (this round, Star of Avelorn): the cast is
		-- PLACED ON THE CHOSEN UNIT'S GROUND - the hurt ally's own position, or
		-- the caster's own feet when the caster is the chosen unit. The
		-- controller is the FRESH caster one (uc above). No readable position ->
		-- FAIL-CLOSED (no guessed placement).
		local gu = unit
		if FOURTH.ah_ally ~= nil and FOURTH.ah_ally_su ~= nil and FOURTH.ah_ally_su.unit ~= nil then
			gu = FOURTH.ah_ally_su.unit
		end
		ok_call, err_call, no_target = FOURTH.ally_ground_cast(uc, gu, ability_key)
		if not quiet then
			log("  ally-ground cast       : perform_special_ability_ground('"
				.. tostring(ability_key) .. "', <the chosen "
				.. ((FOURTH.ah_ally ~= nil) and "ALLY" or "CASTER") .. "'s own position vector>)"
				.. " - the ally-ground form")
		end
	elseif FOURTH.is_ground_key(ability_key) then
		ok_call, err_call, no_target = FOURTH.ground_cast(uc, unit, ability_key)
		if not quiet then
			log("  ground cast            : perform_special_ability_ground('"
				.. tostring(ability_key) .. "', <the unit's own position vector>) - the targeted form")
		end
	elseif FOURTH.enemy_ground_keys[ability_key] == true then
		-- ENEMY-GROUND AREA (Class A, harness 97): the cast is PLACED ON THE
		-- CHOSEN ENEMY'S GROUND. The controller is the FRESH one (uc above); the
		-- position is the enemy's own. NO enemy chosen -> FAIL-CLOSED (never a
		-- guessed or self target).
		if FOURTH.eg_enemy == nil then
			if not quiet then
				log("  enemy-ground cast SKIPPED: no enemy was chosen - not firing on a guessed target (fail-closed)")
			end
			if RELEASE_CONTROL_AFTER and took_control then
				pcall(function() uc:release_control() end)
			end
			return "held"
		end
		ok_call, err_call, no_target = FOURTH.enemy_ground_cast(uc, FOURTH.eg_enemy, ability_key)
		if not quiet then
			log("  enemy-ground cast      : perform_special_ability_ground('"
				.. tostring(ability_key) .. "', <the chosen ENEMY's position vector>) - the enemy-ground form")
		end
	else
		ok_call, err_call = pcall(function()
			-- BLOCK 2: the ALLY-TARGETING call shape - an ability whose
			-- evaluator chose another friendly unit passes it here as the
			-- target; every self/unit-targeted ability passes nil and the
			-- unit is its own target, exactly as before (target or unit).
			uc:perform_special_ability(ability_key, target or unit)
		end)
	end

	local outcome = "held"        -- held / cooling / fired / gone

	-- FAIL-OPEN FOR A TARGETED CAST (section 7e): no readable position means
	-- NO fire - never a guessed target. The reason is said ONCE per
	-- (unit, marker), then silent; the pair re-probes on its guard cadence.
	if no_target then
		local slot = unit_slot(ui_id)
		local per = FOURTH.missing_logged[slot]
		if per == nil then
			per = {}
			FOURTH.missing_logged[slot] = per
		end
		if per[marker] ~= true then
			per[marker] = true
			log("  targeted cast " .. tostring(marker)
				.. " SKIPPED: the unit's ground position could not be read"
				.. " - not firing with a wrong target (fail-open)")
		end
		if RELEASE_CONTROL_AFTER and took_control then
			local ok_release, err_release = pcall(function() uc:release_control() end)
			log("  release_control         : ok=" .. tostring(ok_release)
				.. (ok_release and "" or ("  ERROR: " .. tostring(err_release))))
		end
		return "held"
	end

	if ok_call then
		-- A quiet re-probe that FIRED is reported in full: the fire is the
		-- whole point, and a log that hides it would lie about the battle.
		if quiet then
			log(attempt_line)
			log("  can_perform before      : " .. tostring(can_before))
		end
		log("  perform_special_ability(key, unit) : ACCEPTED")
		log("  the readiness gate decides the next attempt (plus the "
			.. tostring(GUARD_SECONDS) .. " s guard)")
		outcome = "fired"
	else
		local err_text = tostring(err_call)

		-- AN ENGINE REJECTION THAT NAMES A NON-EXISTENT UNIT IS A REMOVAL
		-- NOTICE (this build): the unit it names is gone, so it is dropped at
		-- once. ONLY the non-existence text matches - the cooldown text below
		-- is a different string, so a live unit that is merely on cooldown
		-- never reaches this branch and keeps behaving exactly as before.
		if error_means_unit_gone(err_text) then
			if quiet then
				log(attempt_line)
				log("  can_perform before      : " .. tostring(can_before))
			end
			log("  perform_special_ability(key, unit) : REJECTED - " .. err_text)
			log("unit " .. tostring(ui_id) .. " is gone (engine rejected the call)"
				.. " - dropped from tracking")
			outcome = "gone"
		elseif text_contains(err_text, "does not support this special ability") then
			-- THE COOLDOWN HOLD (this round): the first refusal of an episode
			-- speaks ONCE, coalesced; every repeat is silent (nothing is
			-- written at all - the caller knows to stay quiet from the hold's
			-- record). The caller arms/extends the back-off from "cooling".
			if not quiet then
				log("  perform_special_ability(key, unit) : REJECTED (on cooldown)"
					.. " - further holds suppressed for " .. tostring(HOLD_SECONDS) .. "s")
				log("  -> engine says the unit cannot use it right now, which is what it")
				log("     says while the ability is active/on cooldown. The readiness gate")
				log("     will hold the next attempt back until the engine says yes again.")
			end
			outcome = "cooling"
		else
			-- ANY OTHER REFUSAL is never suppressed: it is not a cooldown hold.
			if quiet then
				log(attempt_line)
				log("  can_perform before      : " .. tostring(can_before))
			end
			log("  perform_special_ability(key, unit) : REJECTED - " .. err_text)
		end
	end

	if RELEASE_CONTROL_AFTER and took_control then
		local ok_release, err_release = pcall(function() uc:release_control() end)
		log("  release_control         : ok=" .. tostring(ok_release)
			.. (ok_release and "" or ("  ERROR: " .. tostring(err_release))))
	end

	return outcome
end


-- ============================================================================
-- 7d. IS THE UNIT ROUTING? One shared engine read, per unit, per poll
--     battle_unit:is_routing() is the script-reachable accessor. The vanilla
--     scripts read exactly this call: lib_battle_misc.lua's is_routing_or_dead
--     runs obj:is_routing() on the unit, and a script_unit reaches its unit
--     through the .unit field - the very handle this poll already reads
--     is_moving_fast() and is_in_melee() from.
--
--     WHY: a routing unit is fleeing the field, yet it can still look
--     eligible to several triggers (it keeps a target while it runs, it can
--     sit in melee geometry, and it still reports a fatigue state), so
--     without this guard an armed unit would burn active buffs while
--     running away.
--
--     THE RULES:
--       * ONE read per unit per poll - the poll computes it once below and
--         every trigger reuses that value, however many are armed;
--       * guarded like every other engine read (pcall);
--       * FAIL-OPEN: only an exact true answer suppresses a trigger. A
--         missing method, a raising read or any other value counts as NOT
--         routing, so when the state cannot be read the mod behaves exactly
--         as it did before this condition existed.
-- ============================================================================

local function unit_is_routing(unit)
	local ok, routing = pcall(function() return unit:is_routing() end)
	if ok and routing == true then
		return true
	end
	return false
end


-- ============================================================================
-- 7f. THE FATIGUE READ (THIS ROUND): battle_unit:fatigue_state()
--     The API dump offers ONE direct fatigue read - fatigue_state() - which
--     answers the unit's state as a string (NOT the localised FatigueName
--     the wheel shows, so no colour markup and no localised word is parsed:
--     this path is language-independent). Documented possible values:
--     threshold_fresh, threshold_active, threshold_winded, threshold_tired,
--     threshold_very_tired and threshold_exhausted.
--
--     THE RULES:
--       * EXACT matching only. The banned string.find NEVER runs here: the
--         WHOLE value is compared, by equality, against the known state
--         strings - both the documented "threshold_" form and the bare word
--         are accepted (either shape is one exact comparison, never a
--         substring search).
--       * the result is the bare state word ("fresh".."exhausted"), so the
--         caller tests "Tired or worse" with a simple lookup; nil means
--         UNREADABLE (the call raised, answered a non-string, or named a
--         state that is not one of the six).
--       * FAIL CLOSED - deliberately unlike the morale guard (is_wavering),
--         which fails OPEN: an unreadable fatigue NEVER fires the ability,
--         and the FIRST unreadable read writes ONE loud line for the whole
--         battle (never a per-tick stream). Assuming "fresh" would hide a
--         broken read; assuming "tired" would fire the ability with no
--         business to.
-- ============================================================================

-- THE LOCAL CEILING (why these live on FOURTH): the main chunk compiles
-- EXACTLY at Lua's 200-local limit (an earlier round had to free a slot for
-- it), so this round adds NO new locals - the reader, its two maps and its
-- once-flag are FIELDS on the existing FOURTH helper bag (the same table
-- the shared morale read lives on). No behaviour depends on the packing.
FOURTH.fatigue_states = {
	-- the documented "threshold_" forms...
	["threshold_fresh"] = "fresh", ["threshold_active"] = "active",
	["threshold_winded"] = "winded", ["threshold_tired"] = "tired",
	["threshold_very_tired"] = "very_tired", ["threshold_exhausted"] = "exhausted",
	-- ...and the bare words, in case this build answers those
	["fresh"] = "fresh", ["active"] = "active", ["winded"] = "winded",
	["tired"] = "tired", ["very_tired"] = "very_tired", ["exhausted"] = "exhausted",
}
FOURTH.fatigue_fire = {
	["tired"] = true, ["very_tired"] = true, ["exhausted"] = true,
}
FOURTH.fatigue_unreadable_logged = false

function FOURTH.fatigue_state(unit)
	local ok, value = pcall(function() return unit:fatigue_state() end)
	if not ok or type(value) ~= "string" then
		if not FOURTH.fatigue_unreadable_logged then
			FOURTH.fatigue_unreadable_logged = true
			log("foe_seeker fatigue: read UNAVAILABLE (raised or no string) - the tired-or-worse trigger FAILS CLOSED (no fire). One-time notice.")
		end
		return nil
	end
	local state = FOURTH.fatigue_states[value]
	if state == nil then
		if not FOURTH.fatigue_unreadable_logged then
			FOURTH.fatigue_unreadable_logged = true
			log("foe_seeker fatigue: UNRECOGNISED value '" .. tostring(value) .. "' - not one of the six known states - the tired-or-worse trigger FAILS CLOSED (no fire). One-time notice.")
		end
		return nil
	end
	return state
end


-- ============================================================================
-- 7g. THE TRIGGER EVALUATORS (critique-2 item 8: one dispatch per entry)
--     The poll no longer walks an if/elseif chain over trigger strings.
--     Every ability entry carries its own evaluate(unit, routing) - one
--     function per trigger name, wired at load (the loop below) - and
--     the poll makes ONE call: ability.evaluate(unit, routing). The
--     evaluator answers the attempt's REASON string, exactly what the
--     old chain left in the reason variable: nil = condition not met,
--     otherwise the textual reason that rides the ATTEMPT line.
--     The five shipped abilities' evaluators hold their old chain
--     branches body for body - same engine reads, same guards, same
--     reason strings - so behaviour and log text are unchanged.
--     evaluate_charge keeps the charge arm AND the user-approved
--     in-melee arm; evaluate_tired keeps the fail-closed fatigue gate;
--     evaluate_in_melee_self is the approved batch rule ("when in
--     melee (and not fleeing): cast on self") and is EXACTLY
--     blood_lust's rule - blood_lust itself rides this same function,
--     so the rule can never drift between the five and the batch.
--     THE LOCAL CEILING: the main chunk sits at Lua's 200-local limit,
--     so every evaluator is a FIELD of the existing FOURTH helper bag
--     (a named local function each would not compile) and the entry
--     wiring below is a load-time loop - no new chunk locals anywhere.
-- ============================================================================

function FOURTH.evaluate_charge(unit, routing)
	local reason = nil
	local m = measure_charge(unit)
	if FIRE_ON_CHARGE and m.charging and not routing then
		reason = string.format("charging (gap=%.1fm dist=%.1fm eta=%.1fs)",
			m.order_gap, m.target_dist, m.ttc)
	elseif FIRE_ON_MELEE and m.melee and not routing then
		reason = "in melee"
	end
	return reason
end

function FOURTH.evaluate_tired(unit, routing)
	local reason = nil
	local fatigue = FOURTH.fatigue_state(unit)
	if fatigue ~= nil and FOURTH.fatigue_fire[fatigue] and not routing then
		reason = "tired or worse (fatigue: " .. fatigue .. ")"
	end
	return reason
end

function FOURTH.evaluate_melee(unit, routing)
	local reason = nil
	if unit:is_in_melee() and not routing then
		reason = "in melee"
	end
	return reason
end

function FOURTH.evaluate_melee_low_morale(unit, routing)
	local reason = nil
	if unit:is_in_melee() and not routing then
		local wavering = FOURTH.wavering(unit)
		if wavering ~= false then
			reason = (wavering == true)
				and "in melee, morale below the wavering threshold"
				or "in melee (morale unreadable - plain in-melee fallback)"
		end
	end
	return reason
end

function FOURTH.evaluate_in_melee_self(unit, routing)
	local reason = nil
	if unit:is_in_melee() and not routing then
		local wavering = FOURTH.wavering(unit)
		if wavering ~= true then
			reason = (wavering == false)
				and "in melee, morale not wavering"
				or "in melee (morale unreadable - plain in-melee fallback)"
		end
	end
	return reason
end

-- ============================================================================
-- BLOCK 2 - THE FOUR NEW-TRIGGER EVALUATORS (this round). Each carries its
-- OWN distinct reason text so the field log tells the triggers apart. The
-- FIFTH new trigger - the summoned Foe-Seeker - needs no evaluator: its key
-- rides the existing foe_seeker entry and the shared evaluate_tired above.
-- THE LOCAL CEILING: these are FIELDS of the same FOURTH helper bag (the
-- chunk compiles at Lua's 200-local limit); their per-unit state
-- (cast_target, plus the Slayer key list below) rides the same bag -
-- NO new chunk locals.
-- ============================================================================

-- where an evaluator leaves the unit it chose for the cast. Glorious Death
-- now ALWAYS leaves the OWNER itself - the ability is self-centred, so the
-- caster is never ordered to walk to an ally. The dispatch clears it before
-- each evaluate and passes it to the cast, so a self-targeted ability can
-- never inherit a stale unit.
FOURTH.cast_target = nil

-- GLORIOUS DEATH's chosen ally (this round): the CLOSEST in-melee Slayer
-- ally within GLORIOUS_DEATH_RANGE_M, kept only so the cast can RE-CHECK
-- the gap immediately before firing. Cleared (with cast_target) before
-- every evaluate, so it can never leak into another ability's attempt. The
-- owner-in-melee self arm leaves it nil, so that cast is never gated.
FOURTH.gd_ally = nil

-- GLORIOUS DEATH's distance helper (this round): the gap in metres from
-- the OWNER to a candidate Slayer ally, read through the SAME primitive
-- the charge detector already uses (battle_unit:unit_distance, section 5).
-- nil when the read cannot be taken.
function FOURTH.gd_ally_gap(unit, ally)
	local ok, gap = pcall(function() return ally:unit_distance(unit) end)
	if ok and type(gap) == "number" then return gap end
	return nil
end

-- true when the gap is within the GD trigger range (38 m = 70% of the 55 m
-- aura). An UNREADABLE gap (nil) is treated as IN range (fail-open) - exactly how the
-- charge detector treats an unknown distance - so a flaky read can never
-- silently disable the ability.
function FOURTH.gd_ally_in_range(unit, ally)
	local gap = FOURTH.gd_ally_gap(unit, ally)
	return (gap == nil) or (gap <= GLORIOUS_DEATH_RANGE_M)
end

-- EAGLE-FEATHER TORC: fire when the barrier is BROKEN - barrier HP at 0 with
-- a NONZERO maximum, both read live. A unit with no barrier (max 0) or an
-- intact one (hp > 0) stays silent; an unreadable value stays silent too.
function FOURTH.evaluate_barrier_broken(unit, routing)
	local reason = nil
	if not routing then
		local hp = FOURTH.context_value(unit, "BarrierHp")
		local max = FOURTH.context_value(unit, "BarrierMaxHp")
		if type(hp) == "number" and type(max) == "number" and max > 0 and hp <= 0 then
			reason = string.format("barrier broken (BarrierHp %.0f/%.0f)", hp, max)
		end
	end
	return reason
end

-- FANGSPIKE: the charge window OR in melee - the SAME charge detector the
-- onslaught trigger uses (its flags and reads), but a DISTINCT in-melee
-- reason. The arms cannot co-fire: the charge arm is tested first and wins.
function FOURTH.evaluate_charge_or_melee(unit, routing)
	local reason = FOURTH.evaluate_charge(unit, routing)
	if reason == "in melee" then
		reason = "in melee (charge or melee)"
	end
	return reason
end

-- GHOUL KING OF USHORAN: fire when the unit's OWN health is at or below 75%,
-- read live. NO HYSTERESIS - removed this round after a field-test defect: a
-- unit under sustained damage may never climb back above a second threshold,
-- so a re-arm gate would disarm this trigger for good. Repeat attempts are
-- held back by the EXISTING machinery only - the readiness gate
-- (can_perform_special_ability), the ability's own engine cooldown and the
-- rejection-informed back-off - never by a second health threshold.
function FOURTH.evaluate_ushoran_health(unit, routing)
	local reason = nil
	if not routing then
		local hp = FOURTH.health_pct(unit)
		if type(hp) == "number" and hp <= 75 then
			reason = string.format("health %d%% (<= 75%%)", math.floor(hp))
		end
	end
	return reason
end

-- ============================================================================
-- THE ALLY-AWARE HEALTH FAMILY (this round) - the user's Star of Avelorn report.
--
-- WHAT WAS WRONG (the user's words): "I tested Star of Avelorn and it only
-- activated when the caster herself was below 75%. But it didn't when an ally
-- unit in range was below 75%."
--
-- Every entry in the health<=75% family rode ONE evaluator that read the
-- OWNER's health only. That is right for a SELF heal and wrong for an ability
-- whose effect reaches FRIENDS - the game's own effect text says so, e.g.
-- Star of Avelorn: "Heals: 0.008 per tick every 1 s (to self and allies in
-- range)", targeting `ground=yes`, `target_ground_under_allies=true`,
-- effect_range 15 m, up to 3 friendly units. So the mod only ever cast it when
-- the caster herself was hurt, at her own feet.
--
-- THE RULE (this round): the trigger is "THIS unit OR a FRIENDLY unit inside the
-- ability's own reach is at or below 75% health", and the LOWEST-health
-- qualifying unit is chosen. The reach is data-derived, never guessed:
--   * an AREA heal (effect_range > 0) uses the ability's own aura radius and the
--     STANDING 70% RULE - floor(effect_range * FOURTH.RANGE_FRACTION), stored as
--     the entry's `aura_m` at load. Star of Avelorn 15 -> 10 m, Gulyas 35 -> 24 m,
--     Salyak's Lullaby 35 -> 24 m, Locus of Fecundity 55 -> 38 m.
--   * a FRIEND-TARGETED heal (effect_range 0, target_friends = true) uses the
--     ability's own CAST range through the existing ally_range_real map:
--     floor(target_intercept_range * 0.70). 60 -> 42 m, 100 -> 70 m, 200 -> 140 m.
-- The OWNER keeps its old arm unchanged (health <= 75%, gap 0, no distance
-- test), so a hurt caster behaves exactly as it did before this round.
--
-- THE CAST TARGET follows the ability's own targeting data, never a guess:
--   * target_ground_under_allies -> the GROUND form at the chosen ALLY's own
--     position (the caster's own feet when the caster is the chosen unit);
--   * target_friends -> the UNIT form with the chosen ALLY as the target (the
--     caster itself when the caster is chosen);
--   * a SELF-CENTRED aura (no target flags at all) -> the caster ALWAYS; the
--     hurt ally only ARMS the trigger, it is never the cast target.
-- Every read is pcall'd and an unreadable distance fails OPEN, exactly as the
-- rest of this file treats an unknown distance.
--
-- WHY A SEPARATE TRIGGER NAME AND NOT A FLAG ON THE OLD ONE: the tooltip line is
-- composed from the entry's trigger, so a distinct trigger name is what keeps
-- each entry's sentence TRUE (see FOURTH.TRIGGER_TIP).
FOURTH.ah_ally = nil          -- the chosen ALLY (nil when the CASTER is chosen)
FOURTH.ah_ally_su = nil       -- its FRESH script_unit (re-fetched this tick)
FOURTH.ah_caster_su = nil     -- the caster's FRESH script_unit
FOURTH.ah_ground = false      -- the cast must use the GROUND form
FOURTH.ah_selfaura = false    -- the aura is centred on the caster: cast on SELF
FOURTH.ah_chosen = nil        -- the unit the picker CHOSE (owner or ally)
FOURTH.ah_range_m = nil       -- the reach the picker tested (metres)
FOURTH.ah_range_word = "aura"

-- THE SHARED PICKER: the lowest-health qualifying unit - the OWNER or a
-- friendly unit inside FOURTH.ah_range_m of the caster. Returns
-- unit, health_percent, distance (distance 0 for the owner, nil when the
-- distance read failed). nil when nothing qualifies.
function FOURTH.ah_pick(unit, routing)
	if routing then return nil, nil, nil end
	local reach = FOURTH.ah_range_m
	local best, best_hp, best_gap = nil, nil, nil
	local self_hp = FOURTH.health_pct(unit)
	if type(self_hp) == "number" and self_hp <= 75 then
		best, best_hp, best_gap = unit, self_hp, 0
	end
	local self_id = tostring(unit:unique_ui_id())
	for i = 1, #tracked_units do
		local other = tracked_units[i] and tracked_units[i].unit
		if other ~= nil and other ~= unit and other:number_of_men_alive() > 0 then
			if tostring(other:unique_ui_id()) ~= self_id and not unit_is_routing(other) then
				local hp = FOURTH.health_pct(other)
				if type(hp) == "number" and hp <= 75 then
					local gap = FOURTH.ab_ally_gap(unit, other)
					if reach == nil or gap == nil or gap <= reach then
						if best == nil or (type(best_hp) == "number" and hp < best_hp) then
							best, best_hp, best_gap = other, hp, gap
						end
					end
				end
			end
		end
	end
	return best, best_hp, best_gap
end

-- THE ALLY-ARM LINE: the chosen ally's TYPE, its REAL health percentage and the
-- REAL distance in metres are all written - the user asks for a number, not a
-- boolean, so none of them is a label.
function FOURTH.ah_log_ally(ally, hp, gap, cast_note)
	local atype = "ally"
	pcall(function() atype = tostring(ally:type()) end)
	log("  " .. tostring(FOURTH.ah_marker) .. " ally: '" .. atype .. "' is the chosen unit (health "
		.. string.format("%.0f", hp) .. "%, distance "
		.. ((gap ~= nil) and string.format("%.1f", gap) or "?") .. "m of "
		.. tostring(FOURTH.ah_range_m) .. "m " .. tostring(FOURTH.ah_range_word)
		.. ") - " .. cast_note)
end

-- health_aura_ground: an AREA heal PLACED ON THE GROUND (Star of Avelorn,
-- Gulyas). The owner arm casts at its own feet; a hurt ally arm casts at THAT
-- ally's ground. Both set FOURTH.ah_ground so the poll's cast path uses the
-- engine's position form.
function FOURTH.evaluate_health_aura_ground(unit, routing)
	local chosen, hp, gap = FOURTH.ah_pick(unit, routing)
	if chosen == nil then return nil end
	FOURTH.ah_chosen = chosen
	FOURTH.ah_ground = true
	FOURTH.ah_caster_su = FOURTH.ab_fresh_friend_su(unit)
	if chosen == unit then
		return string.format("health %d%% (<= 75%%)", math.floor(hp))
	end
	FOURTH.ah_ally = chosen
	FOURTH.ah_ally_su = FOURTH.ab_fresh_friend_su(chosen)
	FOURTH.ah_log_ally(chosen, hp, gap, "cast on the ground under that ally")
	return string.format("%s: lowest-health unit in the aura is an ALLY at %d%% (<= 75%%),"
		.. " distance %s of %sm %s - cast under the ally",
		tostring(FOURTH.ah_marker or "ally"), math.floor(hp),
		((gap ~= nil) and string.format("%.1f", gap) or "?"),
		tostring(FOURTH.ah_range_m), tostring(FOURTH.ah_range_word))
end

-- health_aura_ally: a FRIEND-TARGETED heal (target_friends, effect_range 0).
-- The cast target is the chosen ALLY through the proven unit form; the owner
-- arm keeps the old self cast.
function FOURTH.evaluate_health_aura_ally(unit, routing)
	local chosen, hp, gap = FOURTH.ah_pick(unit, routing)
	if chosen == nil then return nil end
	FOURTH.ah_chosen = chosen
	FOURTH.ah_caster_su = FOURTH.ab_fresh_friend_su(unit)
	if chosen == unit then
		return string.format("health %d%% (<= 75%%)", math.floor(hp))
	end
	FOURTH.ah_ally = chosen
	FOURTH.ah_ally_su = FOURTH.ab_fresh_friend_su(chosen)
	FOURTH.cast_target = chosen
	FOURTH.ah_log_ally(chosen, hp, gap, "cast on that ally")
	return string.format("%s: lowest-health unit in range is an ALLY at %d%% (<= 75%%),"
		.. " distance %s of %sm %s - cast on the ally",
		tostring(FOURTH.ah_marker or "ally"), math.floor(hp),
		((gap ~= nil) and string.format("%.1f", gap) or "?"),
		tostring(FOURTH.ah_range_m), tostring(FOURTH.ah_range_word))
end

-- health_aura_self: a SELF-CENTRED aura (no target flags; effect_range > 0, so
-- the heal reaches "self and allies in range" around the CASTER). A hurt ALLY
-- arms the trigger, but the cast is ALWAYS on the caster - the aura then covers
-- that ally, and the distance gate above guarantees the ally is inside it.
function FOURTH.evaluate_health_aura_self(unit, routing)
	local chosen, hp, gap = FOURTH.ah_pick(unit, routing)
	if chosen == nil then return nil end
	FOURTH.ah_chosen = chosen
	FOURTH.ah_selfaura = true
	FOURTH.ah_caster_su = FOURTH.ab_fresh_friend_su(unit)
	if chosen == unit then
		return string.format("health %d%% (<= 75%%)", math.floor(hp))
	end
	FOURTH.ah_log_ally(chosen, hp, gap, "cast on the caster (the aura is centred on it)")
	return string.format("%s: lowest-health unit in the aura is an ALLY at %d%% (<= 75%%),"
		.. " distance %s of %sm %s - cast on the caster",
		tostring(FOURTH.ah_marker or "ally"), math.floor(hp),
		((gap ~= nil) and string.format("%.1f", gap) or "?"),
		tostring(FOURTH.ah_range_m), tostring(FOURTH.ah_range_word))
end

-- THE SLAYER TYPE-KEY LIST (this round). The engine's battle_unit:type()
-- answers the unit's land_units key (the vanilla API dump: "the unit type of
-- the unit, from the land_units table"), and the mod already reads exactly
-- that key in the identity watch - so a genuine Slayer CAN be recognised from
-- script. The list below is DERIVED FROM THE GAME'S OWN DATA, not hand-
-- written: every land_units key whose own key contains "slayer" or
-- "doomseeker" was extracted from the game dump's localisation table
-- (%LOCALAPPDATA%\Temp\wh3\land_units.loc.tsv - its
-- land_units_onscreen_name_<key> rows) and copied here VERBATIM:
--   wh_main_dwf_inf_slayers, wh2_dlc10_dwf_inf_giant_slayers,
--   wh3_dlc25_dwf_cha_daemon_slayer, wh3_dlc25_dwf_cha_dragon_slayer,
--   wh3_dlc25_dwf_inf_slayer_pirates, wh3_dlc25_dwf_inf_slayer_pirates_ror,
--   wh3_dlc25_dwf_inf_slayers_grudge_unit, wh_dlc06_dwf_inf_dragonback_slayers_0,
--   wh3_dlc25_dwf_inf_doomseekers, wh3_dlc25_dwf_inf_doomseekers_ror.
-- Membership is EXACT WHOLE-KEY equality (ONE table read) - the banned
-- string.find never runs, so a near-miss key (the Bretonnian ROR
-- "Beastslayers of Bastonne", whose own key carries no "slayer") is
-- correctly NOT a Slayer. LIMIT: a Slayer whose key does not spell it (e.g.
-- Gotrek) is a deliberate under-approximation - such a unit is simply not
-- offered to the engine by this trigger.
FOURTH.slayer_keys = {
	["wh_main_dwf_inf_slayers"] = true,
	["wh2_dlc10_dwf_inf_giant_slayers"] = true,
	["wh3_dlc25_dwf_cha_daemon_slayer"] = true,
	["wh3_dlc25_dwf_cha_dragon_slayer"] = true,
	["wh3_dlc25_dwf_inf_slayer_pirates"] = true,
	["wh3_dlc25_dwf_inf_slayer_pirates_ror"] = true,
	["wh3_dlc25_dwf_inf_slayers_grudge_unit"] = true,
	["wh_dlc06_dwf_inf_dragonback_slayers_0"] = true,
	["wh3_dlc25_dwf_inf_doomseekers"] = true,
	["wh3_dlc25_dwf_inf_doomseekers_ror"] = true,
}

-- true only for a genuine Slayer unit: the engine's type() key is in the list
-- above. A missing, raising or non-string read is NOT a Slayer (fail-safe).
-- ONE pcall'd read, ONE table lookup - no string operation of any kind.
function FOURTH.is_slayer(unit)
	local ok, t = pcall(function() return unit:type() end)
	if not ok or type(t) ~= "string" then return false end
	return FOURTH.slayer_keys[t] == true
end

-- GLORIOUS DEATH: the mod's FIRST ability whose trigger does NOT require the
-- OWNER to be in melee. THE TRIGGER stays SLAYER-ONLY: a unit is a Slayer
-- exactly when its land_units type key is in FOURTH.slayer_keys.
--   (a) an in-melee SLAYER ally (other than self) arms the ability; else
--   (b) the OWNER itself arms it ONLY when it is a Slayer AND in melee; else
--   (c) SILENT. A NON-Slayer ally is NEVER offered to the engine.
-- THE CAST TARGET IS ALWAYS THE OWNER ITSELF (the ability is self-centred, so
-- the caster must never be ordered to walk to the Slayer ally).
-- THE RANGE GATE (this round, the reported bug fix): the ally arm only counts
-- while the owner is WITHIN GLORIOUS_DEATH_RANGE_M (38 m = 70% of the
-- ability's 55 m aura, FOURTH.RANGE_FRACTION) of the ally - otherwise the
-- cast is wasted. The CLOSEST
-- in-range in-melee
-- Slayer is the one chosen; the gap is RE-CHECKED immediately before the cast
-- (a unit can move a little between the poll and the cast) and the cast is
-- SKIPPED if the ally has drifted out of range. The owner-in-melee self arm
-- is NEVER gated (casting on self is always in range).
function FOURTH.evaluate_glorious_death(unit, routing)
	local reason = nil
	if not routing then
		local self_id = tostring(unit:unique_ui_id())
		local best_ally = nil
		local best_gap = nil
		for i = 1, #tracked_units do
			local other = tracked_units[i] and tracked_units[i].unit
			if other ~= nil and other ~= unit and other:number_of_men_alive() > 0 then
				if tostring(other:unique_ui_id()) ~= self_id
					and other:is_in_melee() and not unit_is_routing(other)
					and FOURTH.is_slayer(other) then
					local gap = FOURTH.gd_ally_gap(unit, other)
					if (gap == nil) or (gap <= GLORIOUS_DEATH_RANGE_M) then
						if best_ally == nil then
							best_ally, best_gap = other, gap
						elseif gap ~= nil and (best_gap == nil or gap < best_gap) then
							best_ally, best_gap = other, gap
						end
					end
				end
			end
		end
		if best_ally ~= nil then
			if best_gap ~= nil then
				log("  glorious_death ally: ui " .. tostring(best_ally:unique_ui_id())
					.. " at " .. string.format("%.1f", best_gap) .. "m is the CLOSEST"
					.. " in-melee Slayer within " .. tostring(GLORIOUS_DEATH_RANGE_M) .. "m")
			end
			FOURTH.cast_target = unit
			FOURTH.gd_ally = best_ally
			reason = "slayer in melee (self-cast)"
		elseif FOURTH.is_slayer(unit) and unit:is_in_melee() then
			FOURTH.cast_target = unit
			reason = "self in melee (self-cast)"
		end
	end
	return reason
end


-- ============================================================================
-- BLOCK 4/5/6 - THE TWO NEW-TRIGGER EVALUATORS (this round). Each carries its
-- OWN distinct reason text so the field log tells them apart.
-- THE LOCAL CEILING: their per-unit state (vm_ally, plus the named trigger-
-- range constant below) rides the FOURTH helper bag - the chunk compiles at
-- Lua's 200-local limit, so NO new chunk-level locals are introduced.
-- ============================================================================

-- WILL OF THE VERMINKING'S TRIGGER RANGE (this round) - THE STANDING 70% RULE.
-- REAL range 35.0000 m = effect_range (unit_spec_abil.tsv,
-- wh3_dlc29_lord_abilities_will_of_the_verminking, ai_usage = augment_melee).
-- 35 * 0.70 = 24.5 -> 24 m (FLOORED, FOURTH.RANGE_FRACTION). Stored on the
-- FOURTH bag (no new chunk local). The ally arm fires only while the OWNER is
-- within FOURTH.VERMINKING_RANGE_M of the wavering ally. ONE place to tune.
FOURTH.VERMINKING_RANGE_M = 24

-- WILL OF THE VERMINKING's chosen ally (this round): the CLOSEST in-melee
-- WAVERING ally within FOURTH.VERMINKING_RANGE_M, kept only so the cast can
-- RE-CHECK the gap immediately before firing. Cleared (with cast_target)
-- before every evaluate, so it can never leak into another ability's attempt.
FOURTH.vm_ally = nil

-- the gap in metres from the OWNER to a candidate ally - the SAME
-- battle_unit:unit_distance primitive the charge detector and Glorious Death
-- already use. nil when the read cannot be taken.
function FOURTH.vm_ally_gap(unit, ally)
	local ok, gap = pcall(function() return ally:unit_distance(unit) end)
	if ok and type(gap) == "number" then return gap end
	return nil
end

-- true when the gap is within the conservative trigger range. An UNREADABLE
-- gap (nil) is treated as IN range (fail-open) - exactly how Glorious Death's
-- gate treats an unknown distance - so a flaky read can never silently
-- disable the ability.
function FOURTH.vm_ally_in_range(unit, ally)
	local gap = FOURTH.vm_ally_gap(unit, ally)
	return (gap == nil) or (gap <= FOURTH.VERMINKING_RANGE_M)
end

-- WILL OF THE VERMINKING: fire when ANY friendly unit OTHER THAN THE CASTER is
-- IN MELEE and WAVERING and within the conservative trigger range of the
-- owner; CAST ON SELF (the effect is an ally aura centred on the caster - the
-- cast target is the OWNER, the DEFAULT target or unit, exactly how every
-- in-melee-self entry casts, so no cast_target write is needed).
-- THE SAME SAFETY PATTERN AS GLORIOUS DEATH: the CLOSEST qualifying ally is
-- chosen, the gap is RE-CHECKED immediately before the cast and the cast is
-- SKIPPED if the ally has drifted out of range. An unreadable morale
-- suppresses (only an EXACT wavering answer counts - fail-closed).
function FOURTH.evaluate_verminking_wavering(unit, routing)
	local reason = nil
	if not routing then
		local self_id = tostring(unit:unique_ui_id())
		local best_ally = nil
		local best_gap = nil
		for i = 1, #tracked_units do
			local other = tracked_units[i] and tracked_units[i].unit
			if other ~= nil and other ~= unit and other:number_of_men_alive() > 0 then
				if tostring(other:unique_ui_id()) ~= self_id
					and other:is_in_melee() and not unit_is_routing(other)
					and FOURTH.wavering(other) == true then
					local gap = FOURTH.vm_ally_gap(unit, other)
					if (gap == nil) or (gap <= FOURTH.VERMINKING_RANGE_M) then
						if best_ally == nil then
							best_ally, best_gap = other, gap
						elseif gap ~= nil and (best_gap == nil or gap < best_gap) then
							best_ally, best_gap = other, gap
						end
					end
				end
			end
		end
		if best_ally ~= nil then
			if best_gap ~= nil then
				log("  will_of_the_verminking ally: ui " .. tostring(best_ally:unique_ui_id())
					.. " at " .. string.format("%.1f", best_gap) .. "m is the CLOSEST"
					.. " wavering in-melee ally within " .. tostring(FOURTH.VERMINKING_RANGE_M) .. "m")
			end
			FOURTH.vm_ally = best_ally
			reason = "wavering ally in melee (self-cast)"
		end
	end
	return reason
end

-- POTION OF TOUGHNESS: a ONE-TIME activation treated as a HEAL - fire when the
-- OWNER is in melee AND its own health is at or below 75%. Reuses the SAME
-- live health read (FOURTH.health_pct - the ONE reader, 0-100 percent) and the
-- hysteresis-free threshold style as Ghoul King of Ushoran; NO second
-- threshold. Repeat attempts are held back by the readiness gate, the engine
-- cooldown and the rejection-informed back-off only.
function FOURTH.evaluate_potion_health(unit, routing)
	local reason = nil
	if unit:is_in_melee() and not routing then
		local hp = FOURTH.health_pct(unit)
		if type(hp) == "number" and hp <= 75 then
			reason = string.format("in melee, health %d%% (<= 75%%)", math.floor(hp))
		end
	end
	return reason
end


-- ============================================================================
-- ENCHANTED METALLURGY (this round) - ONE new trigger for the whole family.
-- The user's new trigger: "when self or ally in range is in melee; when ally
-- in range is shooting". The MELEE half ships; the SHOOTING half COULD NOT be
-- built, and NO proxy is used (see the note below).
-- API RESEARCH (the shooting predicate): the vanilla battle-script API
-- (battle_unit.lua in the game dump) exposes NO per-unit "is firing / is
-- shooting" read. The ONLY missile-related reads are is_under_missile_attack
-- ("Returns whether the unit is currently taking fire" - the unit RECEIVING
-- fire: the WRONG direction), current_target (the unit's target - a melee unit
-- has one too, so it proves nothing about firing), ammo_left / starting_ammo
-- (a "has fired sometime this battle" count, not "is firing now") and
-- missile_range (a static, ranged-capable property). battle_manager's
-- get_num_units_under_fire / get_proportion_under_fire are battle-level and
-- also count units UNDER fire. The engine's own flag vocabulary
-- (flags.tsv: is_missile_unit, is_under_missile_fire, cannot_perform_missile_
-- attack) is a DATA-TABLE construct for the ability auto-activate system, NOT
-- a Lua read. There is therefore NO proven predicate for "this unit is firing"
-- in the same trust class as is_in_melee / is_wavering / is_routing, so the
-- shooting half is deliberately NOT built.
-- THE MELEE HALF: fire when the OWNER is in melee, OR any friendly unit other
-- than the caster is in melee within the conservative trigger range; cast ON
-- SELF. THE LOCAL CEILING: the per-unit state (mtl_ally) and the named range
-- constant ride the FOURTH helper bag - NO new chunk-level locals.
-- ============================================================================

-- ENCHANTED METALLURGY'S TRIGGER RANGE (this round) - THE STANDING 70% RULE.
-- REAL range 35.0000 m = effect_range (unit_spec_abil.tsv, for all four keys
-- wh3_main_character_abilities_enchanted_metallurgy[_flaming|_piercing|
-- _poison], ai_usage = augment_melee). 35 * 0.70 = 24.5 -> 24 m (FLOORED,
-- FOURTH.RANGE_FRACTION). Stored on the FOURTH bag (no new chunk local). The
-- ally arm fires only while the OWNER is within FOURTH.METALLURGY_RANGE_M of
-- the in-melee ally. ONE place to tune.
FOURTH.METALLURGY_RANGE_M = 24

-- ENCHANTED METALLURGY's chosen ally (this round): the CLOSEST in-melee ally
-- within FOURTH.METALLURGY_RANGE_M, kept only so the cast can RE-CHECK the
-- gap immediately before firing. Cleared (with cast_target) before every
-- evaluate, so it can never leak into another ability's attempt.
FOURTH.mtl_ally = nil

-- the gap in metres from the OWNER to a candidate ally - the SAME
-- battle_unit:unit_distance primitive the charge detector, Glorious Death and
-- Will of the Verminking already use. nil when the read cannot be taken.
function FOURTH.mtl_ally_gap(unit, ally)
	local ok, gap = pcall(function() return ally:unit_distance(unit) end)
	if ok and type(gap) == "number" then return gap end
	return nil
end

-- true when the gap is within the conservative trigger range. An UNREADABLE
-- gap (nil) is treated as IN range (fail-open) - exactly how the Glorious
-- Death / Verminking gate treats an unknown distance - so a flaky read can
-- never silently disable the ability.
function FOURTH.mtl_ally_in_range(unit, ally)
	local gap = FOURTH.mtl_ally_gap(unit, ally)
	return (gap == nil) or (gap <= FOURTH.METALLURGY_RANGE_M)
end

-- ENCHANTED METALLURGY: fire when the OWNER ITSELF is in melee, OR any
-- friendly unit OTHER THAN THE CASTER is in melee within the conservative
-- trigger range of the owner; CAST ON SELF (these are self-centred dual-
-- purpose buffs - +weapon damage and +missile damage - that also reach nearby
-- allies: the cast target is the OWNER, the DEFAULT target or unit, exactly
-- how every in-melee-self entry casts, so no cast_target write is needed).
-- THE SAME SAFETY PATTERN AS GLORIOUS DEATH / VERMINKING: for the ALLY arm
-- the CLOSEST qualifying in-melee ally is chosen, the gap is RE-CHECKED
-- immediately before the cast and the cast is SKIPPED on drift. The
-- owner-in-melee self arm leaves FOURTH.mtl_ally nil - never gated.
function FOURTH.evaluate_metallurgy_melee(unit, routing)
	if not routing then
		if unit:is_in_melee() then
			return "in melee (metallurgy self-cast)"
		end
		local self_id = tostring(unit:unique_ui_id())
		local best_ally = nil
		local best_gap = nil
		for i = 1, #tracked_units do
			local other = tracked_units[i] and tracked_units[i].unit
			if other ~= nil and other ~= unit and other:number_of_men_alive() > 0 then
				if tostring(other:unique_ui_id()) ~= self_id
					and other:is_in_melee() and not unit_is_routing(other) then
					local gap = FOURTH.mtl_ally_gap(unit, other)
					if (gap == nil) or (gap <= FOURTH.METALLURGY_RANGE_M) then
						if best_ally == nil then
							best_ally, best_gap = other, gap
						elseif gap ~= nil and (best_gap == nil or gap < best_gap) then
							best_ally, best_gap = other, gap
						end
					end
				end
			end
		end
		if best_ally ~= nil then
			if best_gap ~= nil then
				log("  enchanted_metallurgy ally: ui " .. tostring(best_ally:unique_ui_id())
					.. " at " .. string.format("%.1f", best_gap) .. "m is the CLOSEST"
					.. " in-melee ally within " .. tostring(FOURTH.METALLURGY_RANGE_M) .. "m")
			end
			FOURTH.mtl_ally = best_ally
			return "in-melee ally (metallurgy self-cast)"
		end
	end
	return nil
end


-- ============================================================================
-- BLOCKS 7-9 (this round) - FIVE new trigger types (and the redesigned pair).
-- Every evaluator is a FIELD of the FOURTH helper bag and every new piece of
-- state / constant rides the bag too: the chunk already sits at Lua's 200-local
-- ceiling, so NO new chunk-level locals are introduced. Each LIVE evaluator
-- answers its OWN distinct reason string so the field log tells the triggers
-- apart; the reading copy answers true / false.
-- ============================================================================

-- CHARGE ONLY (Ferocious Battle Howl): fire in the charge window WITHOUT the
-- melee arm - the split second before impact, cast on self. This is the plain
-- charge detector (measure_charge, section 5) with the FIRE_ON_MELEE arm
-- deliberately OMITTED.
function FOURTH.evaluate_charge_only(unit, routing)
	local reason = nil
	local m = measure_charge(unit)
	if FIRE_ON_CHARGE and m.charging and not routing then
		reason = string.format("charging (charge only) (gap=%.1fm dist=%.1fm eta=%.1fs)",
			m.order_gap, m.target_dist, m.ttc)
	end
	return reason
end

-- WAVERING SELF (Ferocious Fury of Ulric / Helm of Yvresse / Vial of Troll
-- Blood): fire while the OWNER itself is wavering (while not routing); cast on
-- self. The morale read is the SAME battle_unit:is_wavering the Stand Your
-- Ground trigger uses (FOURTH.wavering); only an EXACT true answer fires
-- (fail-closed - an unreadable morale never fires a self-only wavering buff).
function FOURTH.evaluate_wavering_self(unit, routing)
	local reason = nil
	if not routing and FOURTH.wavering(unit) == true then
		reason = "wavering (self)"
	end
	return reason
end

-- WAVERING SELF-OR-ALLY (Fury of Ulric / the redesigned Commanding Presence):
-- fire when the OWNER is wavering, OR a friendly in-melee WAVERING ally lies
-- within the trigger range; cast ON SELF (the effect is a self-centred aura).
-- THE TRIGGER RANGE (this round) - THE STANDING 70% RULE. REAL range 35.0000 m
-- = effect_range (unit_spec_abil.tsv) for all three keys that ride it -
-- wh3_dlc29_lord_active_commanding_presence, wh3_dlc29_spell_bound_prayer_
-- fury_of_ulric and wh2_dlc09_character_abilities_stay_here_ill_get_help.
-- 35 * 0.70 = 24.5 -> 24 m (FLOORED, FOURTH.RANGE_FRACTION). THE SAME SAFETY
-- PATTERN as Glorious Death / Verminking / Metallurgy: the CLOSEST qualifying
-- in-melee wavering ally is chosen, the gap is RE-CHECKED immediately before
-- the cast and the cast is SKIPPED on drift. The self-wavering arm leaves
-- FOURTH.ws_ally nil - never gated.
FOURTH.WAVERING_RANGE_M = 24

-- the chosen ally (this round): cleared with cast_target before every evaluate.
FOURTH.ws_ally = nil

function FOURTH.ws_ally_gap(unit, ally)
	local ok, gap = pcall(function() return ally:unit_distance(unit) end)
	if ok and type(gap) == "number" then return gap end
	return nil
end

function FOURTH.ws_ally_in_range(unit, ally)
	local gap = FOURTH.ws_ally_gap(unit, ally)
	return (gap == nil) or (gap <= FOURTH.WAVERING_RANGE_M)
end

function FOURTH.evaluate_wavering_self_or_ally(unit, routing)
	local reason = nil
	if not routing then
		if FOURTH.wavering(unit) == true then
			reason = "wavering (self-or-ally)"
		else
			local self_id = tostring(unit:unique_ui_id())
			local best_ally = nil
			local best_gap = nil
			for i = 1, #tracked_units do
				local other = tracked_units[i] and tracked_units[i].unit
				if other ~= nil and other ~= unit and other:number_of_men_alive() > 0 then
					if tostring(other:unique_ui_id()) ~= self_id
						and other:is_in_melee() and not unit_is_routing(other)
						and FOURTH.wavering(other) == true then
						local gap = FOURTH.ws_ally_gap(unit, other)
						if (gap == nil) or (gap <= FOURTH.WAVERING_RANGE_M) then
							if best_ally == nil then
								best_ally, best_gap = other, gap
							elseif gap ~= nil and (best_gap == nil or gap < best_gap) then
								best_ally, best_gap = other, gap
							end
						end
					end
				end
			end
			if best_ally ~= nil then
				if best_gap ~= nil then
					log("  wavering_self_or_ally ally: ui " .. tostring(best_ally:unique_ui_id())
						.. " at " .. string.format("%.1f", best_gap) .. "m is the CLOSEST"
						.. " in-melee wavering ally within " .. tostring(FOURTH.WAVERING_RANGE_M) .. "m")
				end
				FOURTH.ws_ally = best_ally
				reason = "wavering in-melee ally (self-cast, self-or-ally)"
			end
		end
	end
	return reason
end

-- CHARGE OR WAVERING (Bangers & Smash): fire in the charge window OR while
-- wavering (while not routing); cast on self. The charge arm is the plain charge
-- detector (no melee arm); the wavering arm is FOURTH.wavering. The arms cannot
-- co-fire - the charge arm is tested first and wins.
function FOURTH.evaluate_charge_or_wavering(unit, routing)
	local reason = nil
	if not routing then
		local m = measure_charge(unit)
		if FIRE_ON_CHARGE and m.charging then
			reason = string.format("charging (charge or wavering) (gap=%.1fm dist=%.1fm eta=%.1fs)",
				m.order_gap, m.target_dist, m.ttc)
		elseif FOURTH.wavering(unit) == true then
			reason = "wavering (charge or wavering)"
		end
	end
	return reason
end

-- WAVERING ALLY IN RANGE ("Stay Here, I'll Get Help!"): fire when a friendly
-- WAVERING ally lies within the conservative trigger range; cast ON SELF. The
-- owner need NOT be wavering and the ally need NOT be in melee - this is the
-- Verminking evaluator shape with the ALLY-MELEE requirement REMOVED (the
-- tracker note records the difference). Same safety pattern: closest in-range
-- wavering ally, gap RE-CHECKED immediately before the cast, cast SKIPPED on
-- drift.
FOURTH.wa_ally = nil

function FOURTH.wa_ally_gap(unit, ally)
	local ok, gap = pcall(function() return ally:unit_distance(unit) end)
	if ok and type(gap) == "number" then return gap end
	return nil
end

function FOURTH.wa_ally_in_range(unit, ally)
	local gap = FOURTH.wa_ally_gap(unit, ally)
	if gap == nil then return true end
	-- CLASS B (harness 98): the per-ability 70% ALLY bound when the poll set one
	-- (Stay Here, I'll Get Help! carries ally_range_real = 60 -> 42 m); otherwise
	-- the shared conservative wavering constant.
	local bound = FOURTH.ab_range_m or FOURTH.WAVERING_RANGE_M
	return gap <= bound
end

function FOURTH.evaluate_wavering_ally_range(unit, routing)
	local reason = nil
	if not routing then
		-- CLASS B (harness 98): the per-ability 70% ALLY bound when the poll set
		-- one (ally_range_real = 60 -> 42 m); otherwise the shared constant.
		local bound = FOURTH.ab_range_m or FOURTH.WAVERING_RANGE_M
		local self_id = tostring(unit:unique_ui_id())
		local best_ally = nil
		local best_gap = nil
		for i = 1, #tracked_units do
			local other = tracked_units[i] and tracked_units[i].unit
			if other ~= nil and other ~= unit and other:number_of_men_alive() > 0 then
				if tostring(other:unique_ui_id()) ~= self_id
					and not unit_is_routing(other)
					and FOURTH.wavering(other) == true then
					local gap = FOURTH.wa_ally_gap(unit, other)
					if (gap == nil) or (gap <= bound) then
						if best_ally == nil then
							best_ally, best_gap = other, gap
						elseif gap ~= nil and (best_gap == nil or gap < best_gap) then
							best_ally, best_gap = other, gap
						end
					end
				end
			end
		end
		if best_ally ~= nil then
			if best_gap ~= nil then
				log("  wavering_ally_range ally: ui " .. tostring(best_ally:unique_ui_id())
					.. " at " .. string.format("%.1f", best_gap) .. "m is the CLOSEST"
					.. " wavering ally within " .. tostring(bound) .. "m")
			end
			FOURTH.wa_ally = best_ally
			-- CLASS B (harness 98): the cast is now issued ON THE CHOSEN ALLY, not
			-- on the owner - the ally rides FOURTH.cast_target and the FRESH
			-- caster/ally script_units (the fresh-handle discipline).
			FOURTH.cast_target = best_ally
			FOURTH.ab_ally = best_ally
			FOURTH.ab_caster_su = FOURTH.ab_fresh_friend_su(unit)
			FOURTH.ab_ally_su = FOURTH.ab_fresh_friend_su(best_ally)
			FOURTH.ab_family = "buff"
			reason = "wavering ally in range, cast on ally"
		end
	end
	return reason
end

-- THE TRIGGER -> EVALUATOR MAP, and the load-time wiring of EVERY entry.
-- The map is keyed by the trigger NAME the table in section 1 already
-- carries; the loop below points each entry at its evaluator. An entry
-- whose trigger name is missing from the map would leave evaluate nil -
-- the harness asserts every entry is wired. A new ability: add its
-- trigger name here and to the entry, nothing else.

-- ============================================================================
-- THE FINAL ROSTER ROUND (this round) - TWO new ALLY-HEAL evaluators for the
--   two built individuals that need a new trigger:
--     BLOOD SACRIFICE - cast on the LOWEST-health ally in range at or below 75%;
--     EAT DA RUNTS!   - cast on self at or below 75%, ELSE on the lowest-health
--                       ally in range at or below 75%.
--   Both are ally-targeting HEALS: the cast target is the CHOSEN ALLY (unlike
--   the self-centred auras, whose cast target is always the owner), so the
--   chosen ally rides FOURTH.cast_target AND a per-trigger slot (FOURTH.bs_ally
--   / FOURTH.edr_ally) so the cast can RE-CHECK the gap AND the ally's health
--   immediately before firing and SKIP on drift (the field-proven Glorious
--   Death / Verminking safety pattern). The self arm of Eat da Runts! writes NO
--   cast_target (the default target or unit = the owner), exactly the
--   Verminking convention - so the self-cast writes stay exactly two.
--   THE TRIGGER RANGE is a DELIBERATELY CONSERVATIVE named constant. The game
--   data (unit_spec_abil.tsv) gives these two SINGLE-ally heals NO aura radius
--   (effect_range = 0.0000; num_effected_friendly_units = 1) and a
--   target_intercept_range of 100.0000 m, so - following the file's field-proven
--   conservative pattern (25 m against larger auras) - the trigger radius is a
--   25 m constant. ONE place to tune.
--   THE LOCAL CEILING: every helper / constant / state is a FIELD of the FOURTH
--   bag - NO new chunk-level locals.
-- ============================================================================

-- BLOOD SACRIFICE'S TRIGGER RANGE (this round) - THE STANDING 70% RULE. The
-- ability has NO aura (effect_range = 0.0000, num_effected_friendly_units = 1),
-- so its REAL game-data range is its target_intercept_range = 100.0000 m
-- (unit_spec_abil.tsv, wh3_dlc26_lord_abilities_blood_sacrifice).
-- 100 * 0.70 = 70.0 -> 70 m (FLOORED, FOURTH.RANGE_FRACTION).
FOURTH.BLOOD_SACRIFICE_RANGE_M = 70
FOURTH.bs_ally = nil
function FOURTH.bs_ally_gap(unit, ally)
	local ok, gap = pcall(function() return ally:unit_distance(unit) end)
	if ok and type(gap) == "number" then return gap end
	return nil
end
function FOURTH.bs_ally_in_range(unit, ally)
	local gap = FOURTH.bs_ally_gap(unit, ally)
	return (gap == nil) or (gap <= FOURTH.BLOOD_SACRIFICE_RANGE_M)
end
-- the chosen ally is STILL a valid heal target: in range AND still at or below
-- 75% health (an unreadable health read is treated as still-valid, fail-open,
-- exactly how the range gate treats an unknown distance).
function FOURTH.bs_ally_valid(unit, ally)
	if ally == nil then return false end
	if not FOURTH.bs_ally_in_range(unit, ally) then return false end
	local hp = FOURTH.health_pct(ally)
	return (type(hp) ~= "number") or (hp <= 75)
end
-- BLOOD SACRIFICE: fire when a friendly unit other than the caster is at or
-- below 75% health within the conservative trigger range; CAST ON THE
-- LOWEST-HEALTH such ally. Silent when no in-range ally is hurt.
function FOURTH.evaluate_blood_sacrifice(unit, routing)
	local reason = nil
	if not routing then
		local self_id = tostring(unit:unique_ui_id())
		local best_ally = nil
		local best_gap = nil
		local best_hp = nil
		for i = 1, #tracked_units do
			local other = tracked_units[i] and tracked_units[i].unit
			if other ~= nil and other ~= unit and other:number_of_men_alive() > 0 then
				if tostring(other:unique_ui_id()) ~= self_id and not unit_is_routing(other) then
					local hp = FOURTH.health_pct(other)
					if type(hp) == "number" and hp <= 75 then
						local gap = FOURTH.bs_ally_gap(unit, other)
						if (gap == nil) or (gap <= FOURTH.BLOOD_SACRIFICE_RANGE_M) then
							if best_ally == nil or (type(best_hp) == "number" and hp < best_hp) then
								best_ally, best_gap, best_hp = other, gap, hp
							end
						end
					end
				end
			end
		end
		if best_ally ~= nil then
			if best_gap ~= nil then
				log("  blood_sacrifice ally: ui " .. tostring(best_ally:unique_ui_id())
					.. " at " .. string.format("%.1f", best_gap) .. "m is the LOWEST-health in-range ally"
					.. " within " .. tostring(FOURTH.BLOOD_SACRIFICE_RANGE_M) .. "m")
			end
			FOURTH.cast_target = best_ally
			FOURTH.bs_ally = best_ally
			reason = string.format("blood sacrifice: lowest-health ally %d%% (<= 75%%), cast on ally", math.floor(best_hp))
		end
	end
	return reason
end

-- EAT DA RUNTS!'S TRIGGER RANGE (this round) - THE STANDING 70% RULE. The
-- ability has NO aura (effect_range = 0.0000, num_effected_friendly_units = 1),
-- so its REAL game-data range is its target_intercept_range = 100.0000 m
-- (unit_spec_abil.tsv, wh3_dlc26_unit_abilities_eat_da_runts).
-- 100 * 0.70 = 70.0 -> 70 m (FLOORED, FOURTH.RANGE_FRACTION).
FOURTH.EAT_DA_RUNTS_RANGE_M = 70
FOURTH.edr_ally = nil
function FOURTH.edr_ally_gap(unit, ally)
	local ok, gap = pcall(function() return ally:unit_distance(unit) end)
	if ok and type(gap) == "number" then return gap end
	return nil
end
function FOURTH.edr_ally_in_range(unit, ally)
	local gap = FOURTH.edr_ally_gap(unit, ally)
	return (gap == nil) or (gap <= FOURTH.EAT_DA_RUNTS_RANGE_M)
end
-- a nil ally (the SELF arm) is always valid - never gated.
function FOURTH.edr_ally_valid(unit, ally)
	if ally == nil then return true end
	if not FOURTH.edr_ally_in_range(unit, ally) then return false end
	local hp = FOURTH.health_pct(ally)
	return (type(hp) ~= "number") or (hp <= 75)
end
-- EAT DA RUNTS!: fire when the OWNER itself is at or below 75% health (cast on
-- self), ELSE when a friendly unit other than the caster is at or below 75%
-- within the conservative trigger range (cast on the LOWEST-health such ally).
function FOURTH.evaluate_eat_da_runts(unit, routing)
	local reason = nil
	if not routing then
		local hp = FOURTH.health_pct(unit)
		if type(hp) == "number" and hp <= 75 then
			reason = string.format("eat da runts: self health %d%% (<= 75%%), cast on self", math.floor(hp))
		else
			local self_id = tostring(unit:unique_ui_id())
			local best_ally = nil
			local best_gap = nil
			local best_hp = nil
			for i = 1, #tracked_units do
				local other = tracked_units[i] and tracked_units[i].unit
				if other ~= nil and other ~= unit and other:number_of_men_alive() > 0 then
					if tostring(other:unique_ui_id()) ~= self_id and not unit_is_routing(other) then
						local ahp = FOURTH.health_pct(other)
						if type(ahp) == "number" and ahp <= 75 then
							local gap = FOURTH.edr_ally_gap(unit, other)
							if (gap == nil) or (gap <= FOURTH.EAT_DA_RUNTS_RANGE_M) then
								if best_ally == nil or (type(best_hp) == "number" and ahp < best_hp) then
									best_ally, best_gap, best_hp = other, gap, ahp
								end
							end
						end
					end
				end
			end
			if best_ally ~= nil then
				if best_gap ~= nil then
					log("  eat_da_runts ally: ui " .. tostring(best_ally:unique_ui_id())
						.. " at " .. string.format("%.1f", best_gap) .. "m is the LOWEST-health in-range ally"
						.. " within " .. tostring(FOURTH.EAT_DA_RUNTS_RANGE_M) .. "m")
				end
				FOURTH.cast_target = best_ally
				FOURTH.edr_ally = best_ally
				reason = string.format("eat da runts: lowest-health ally %d%% (<= 75%%), cast on ally", math.floor(best_hp))
			end
		end
	end
	return reason
end


-- ============================================================================
-- ============================================================================
-- CLASS B (harness 98) - ALLY-TARGETED EFFECTS CAST ON SELF.
--   The audit's Class B: abilities the game aims at ANOTHER friendly unit while
--   the mod self-casts, so the declared recipient never receives the effect.
--   THE MECHANISM is the mod's OWN ally-targeting shape - the blood_sacrifice /
--   eat_da_runts picker (a friendly unit other than the caster, chosen by a
--   per-family rule, range-tested against a conservative named bound, the gap
--   RE-READ immediately before the cast) - extended with the Class-A round's
--   FRESH-HANDLE discipline: the CASTER's controller AND the chosen ALLY are
--   re-enumerated from the local player's army list on the SAME tick
--   (FOURTH.ab_fresh_friend_su) and the cast is issued as
--   caster_su.uc:perform_special_ability(key, ally_su.unit). A controller held
--   from an earlier poll silently no-ops, so the fresh fetch is what makes the
--   ally-targeted cast LAND. The chosen ally still rides FOURTH.cast_target, so
--   the established dispatch passes it unchanged.
--   THE FOUR FAMILIES (each its own evaluator):
--     ally_heal        - a PURE HEAL: pick the LOWEST-health ally in range at or
--                        below 75% health (the health-only trigger family);
--     ally_heal_melee  - a heal that ALSO grants armour/defence: the same pick,
--                        but the OWNER must be in melee (the melee+health gate);
--     ally_wavering    - an Unbreakable / morale-recovery effect: pick the
--                        CLOSEST WAVERING ally in range (the wavering family);
--     ally_melee_buff  - the default in-melee/not-routing shape: pick the
--                        CLOSEST ally in range.
--   THE RANGE: every entry carries its own REAL target_intercept_range
--   (ally_range_real) mapped at load to ONE named 70% constant per real range
--   (FOURTH.ALLY_CAST). The offer test is the per-ability constant ONLY - the
--   gap is unit:unit_distance(ally), the engine's EDGE-TO-EDGE distance in
--   metres (bounding-box aware, battle_unit.lua:160) - and NEVER the engine's
--   looser unit_in_range reach read. The REAL distance is logged.
--   THE LOCAL CEILING: every helper / constant / state is a FIELD of the FOURTH
--   bag - NO new chunk-level locals.
-- ============================================================================

-- the chosen ally, the FRESH caster/ally script_units, and the current
-- ability's own 70% ally bound + marker + family - all cleared before every
-- evaluate, so no ability can inherit a stale ally.
FOURTH.ab_ally = nil
FOURTH.ab_caster_su = nil
FOURTH.ab_ally_su = nil
FOURTH.ab_range_m = nil
FOURTH.ab_marker = nil
FOURTH.ab_family = nil

-- re-fetch a FRIENDLY script_unit FRESH from the local player's army list THIS
-- tick (never a script_unit held from an earlier poll - the Class-A lesson: a
-- stale controller silently no-ops). nil when the army or the matching unit
-- cannot be found.
function FOURTH.ab_fresh_friend_su(unit)
	local ok_coll, coll = pcall(function()
		return bm:get_scriptunits_for_local_players_army()
	end)
	if not ok_coll or coll == nil then return nil end
	local ok_n, n = pcall(function() return coll:count() end)
	if not ok_n or type(n) ~= "number" then return nil end
	local want = nil
	pcall(function() want = tostring(unit:unique_ui_id()) end)
	if want == nil then return nil end
	for i = 1, n do
		local ok_su, su = pcall(function() return coll:item(i) end)
		if ok_su and su ~= nil then
			local u = nil
			pcall(function() u = su.unit end)
			if u ~= nil then
				local id = nil
				pcall(function() id = u:unique_ui_id() end)
				if id ~= nil and tostring(id) == want then return su end
			end
		end
	end
	return nil
end

-- the gap in metres from the OWNER to a candidate ally - the SAME
-- battle_unit:unit_distance primitive the charge detector and every ally-range
-- trigger already use. nil when the read cannot be taken.
function FOURTH.ab_ally_gap(unit, ally)
	local ok, gap = pcall(function() return ally:unit_distance(unit) end)
	if ok and type(gap) == "number" then return gap end
	return nil
end

-- true when a gap lies within the CURRENT ability's 70% ally bound. An
-- UNREADABLE gap (nil) is treated as IN range (fail-open); so is a missing
-- bound (a non-ally ability never reaches here).
function FOURTH.ab_gap_ok(gap)
	-- Merciw's Monstrous Regiment: NO distance bound at all (infinite range
	-- per the wiki).
	if FOURTH.ab_infinite then return true end
	if gap == nil then return true end
	local bound = FOURTH.ab_range_m
	if bound == nil then return true end
	return gap <= bound
end

-- true while the ally lies within the CURRENT ability's 70% ally bound.
function FOURTH.ab_ally_in_range(unit, ally)
	return FOURTH.ab_gap_ok(FOURTH.ab_ally_gap(unit, ally))
end

-- the chosen ally is STILL valid: in range AND (for a heal) still at or below
-- 75% health. An unreadable health read is treated as still-valid (fail-open).
function FOURTH.ab_ally_valid(unit, ally)
	if ally == nil then return false end
	if not FOURTH.ab_ally_in_range(unit, ally) then return false end
	if FOURTH.ab_family == "heal" then
		local hp = FOURTH.health_pct(ally)
		return (type(hp) ~= "number") or (hp <= 75)
	end
	if FOURTH.ab_family == "ammo" then
		local fr = FOURTH.ammo_fraction_if_firing(ally)
		return (fr ~= nil) and (fr <= FOURTH.RESTOCK_AT_FRACTION)
	end
	if FOURTH.ab_family == "shooting" then
		return FOURTH.shooting_past_cast_point(ally)
	end
	if FOURTH.ab_family == "fighting" then
		return FOURTH.fighting(ally)
	end
	return true
end

-- ============================================================================
-- THE TARGET-CLASS KEY LISTS (harness 99). Every list is DERIVED FROM THE
-- GAME'S OWN DATA - never hand-written - by exact whole-key matching, and
-- copied here VERBATIM (the same method the Slayer list above uses). NOTHING
-- here is a name guess: each entry states the source table + column and the
-- match rule. Membership is EXACT WHOLE-KEY equality (ONE table read; the
-- banned substring finder never runs), so a near-miss key is correctly NOT a
-- member. LIMITED: an unreadable type() read is treated as NOT-a-member
-- (fail-safe: such a unit is simply not offered to the engine).
--
--   beast      : main_units_tables.caste == "war_beast"  (the land_unit key
--                of each such main_units row).  [kind = beast]
--   monster    : main_units_tables.caste == "monster"    (land_unit key).
--   warmachine : main_units_tables.caste == "warmachine" (land_unit key).
--   construct  : the unit's unit_attributes group carries the "construct"
--                attribute (unit_attributes_to_groups_junctions_tables joined
--                to land_units_tables.attribute_group).
--   hellforged : the same join, attribute "hellforged" (the Hell-Forged units).
--   missile    : land_units_tables.primary_missile_weapon is NON-EMPTY (the
--                unit can perform missile attacks) - the flag the game's
--                cannot_perform_missile_attack invalid-target test mirrors.
--   overseer   : land_units_tables.class != "com" (NOT commander-class) AND the
--                battle entity size (battle_entities_tables.size, reached via
--                land_units_tables.man_entity) is NOT large / very_large (NOT
--                large) - exactly the two invalid-target flags the ability
--                carries (unit_is_commander_class, unit_is_large).
--
-- Sizes: beast=55, monster=235, warmachine=68, construct=29, hellforged=13, missile=493, overseer=918.
-- ============================================================================
FOURTH.class_keys = {
	beast = {
		["wh2_dlc09_tmb_mon_carrion_0"] = true,
		["wh2_dlc09_tmb_mon_carrion_ror"] = true,
		["wh2_dlc09_tmb_mon_dire_wolves"] = true,
		["wh2_dlc09_tmb_mon_fell_bats"] = true,
		["wh2_dlc11_cst_cav_deck_droppers_0"] = true,
		["wh2_dlc11_cst_cav_deck_droppers_1"] = true,
		["wh2_dlc11_cst_cav_deck_droppers_2"] = true,
		["wh2_dlc11_cst_cav_deck_droppers_ror_0"] = true,
		["wh2_dlc11_cst_mon_fell_bats"] = true,
		["wh2_dlc11_cst_mon_scurvy_dogs"] = true,
		["wh2_dlc15_hef_mon_war_lions_of_chrace_0"] = true,
		["wh2_dlc15_hef_mon_war_lions_of_chrace_ror_0"] = true,
		["wh2_dlc16_skv_mon_wolf_rats_0"] = true,
		["wh2_dlc16_skv_mon_wolf_rats_0_summoned"] = true,
		["wh2_dlc16_skv_mon_wolf_rats_1"] = true,
		["wh2_dlc16_skv_mon_wolf_rats_1_summoned"] = true,
		["wh2_dlc16_wef_mon_cave_bats"] = true,
		["wh2_dlc16_wef_mon_spider_hatchlings_0"] = true,
		["wh2_dlc16_wef_mon_wolves_0"] = true,
		["wh2_twa03_def_mon_wolves_0"] = true,
		["wh3_dlc24_cth_mon_jade_lion"] = true,
		["wh3_dlc24_cth_mon_jet_lion"] = true,
		["wh3_dlc26_grn_inf_squig_herd_0_summoned"] = true,
		["wh3_dlc26_ogr_mon_blood_vultures"] = true,
		["wh3_dlc26_ogr_mon_sabretusk_pack_0_summoned"] = true,
		["wh3_dlc27_tmb_mon_carrion_boss"] = true,
		["wh3_dlc29_emp_inf_hunting_hounds"] = true,
		["wh3_dlc29_emp_inf_hunting_hounds_ror"] = true,
		["wh3_main_kho_inf_chaos_warhounds_0"] = true,
		["wh3_main_kho_inf_flesh_hounds_of_khorne_0"] = true,
		["wh3_main_monster_feral_bears"] = true,
		["wh3_main_monster_feral_ice_bears"] = true,
		["wh3_main_nur_mon_plague_toads_0"] = true,
		["wh3_main_ogr_mon_sabretusk_pack_0"] = true,
		["wh3_main_pro_kho_inf_chaos_warhounds_0"] = true,
		["wh3_main_pro_kho_inf_flesh_hounds_of_khorne_0"] = true,
		["wh3_main_pro_kho_inf_flesh_hounds_of_khorne_simaergul_0"] = true,
		["wh3_pro12_kho_inf_flesh_hounds_of_khorne_summoned"] = true,
		["wh3_twa10_kho_inf_flesh_hounds_of_khorne_ror"] = true,
		["wh_dlc03_bst_inf_chaos_warhounds_0"] = true,
		["wh_dlc03_bst_inf_chaos_warhounds_1"] = true,
		["wh_dlc04_vmp_mon_direpack_0"] = true,
		["wh_dlc06_grn_inf_squig_explosive_0"] = true,
		["wh_dlc06_grn_inf_squig_herd_0"] = true,
		["wh_dlc06_grn_mon_spider_hatchlings_0"] = true,
		["wh_dlc06_grn_mon_spider_hatchlings_0_summoned"] = true,
		["wh_dlc08_nor_mon_marauder_warwolves_0"] = true,
		["wh_main_chs_mon_chaos_warhounds_0"] = true,
		["wh_main_chs_mon_chaos_warhounds_1"] = true,
		["wh_main_nor_mon_chaos_warhounds_0"] = true,
		["wh_main_nor_mon_chaos_warhounds_1"] = true,
		["wh_main_vmp_mon_dire_wolves"] = true,
		["wh_main_vmp_mon_fell_bats"] = true,
		["wh_pro04_nor_mon_marauder_warwolves_ror_0"] = true,
		["wh_twa03_def_inf_squig_explosive_0"] = true,
	},
	monster = {
		["wh2_dlc09_tmb_mon_heirotitan_0"] = true,
		["wh2_dlc09_tmb_mon_khemrian_warsphinx_0"] = true,
		["wh2_dlc09_tmb_mon_necrosphinx_0"] = true,
		["wh2_dlc09_tmb_mon_necrosphinx_ror"] = true,
		["wh2_dlc09_tmb_mon_tomb_scorpion_0"] = true,
		["wh2_dlc10_def_mon_chill_of_sontar_ror_0"] = true,
		["wh2_dlc10_def_mon_feral_manticore_0"] = true,
		["wh2_dlc10_def_mon_kharibdyss_0"] = true,
		["wh2_dlc10_def_mon_war_hydra_boss"] = true,
		["wh2_dlc10_hef_mon_treeman_0"] = true,
		["wh2_dlc10_lzd_mon_carnosaur_boss"] = true,
		["wh2_dlc10_nor_mon_phoenix_flamespyre_boss"] = true,
		["wh2_dlc10_skv_mon_hell_pit_abomination_boss"] = true,
		["wh2_dlc11_cst_mon_bloated_corpse_0"] = true,
		["wh2_dlc11_cst_mon_necrofex_colossus_0"] = true,
		["wh2_dlc11_cst_mon_necrofex_colossus_ror_0"] = true,
		["wh2_dlc11_cst_mon_rotting_leviathan_0"] = true,
		["wh2_dlc11_cst_mon_terrorgheist"] = true,
		["wh2_dlc11_vmp_mon_varghulf_summoned"] = true,
		["wh2_dlc12_lzd_cav_terradon_riders_0_tlaqua"] = true,
		["wh2_dlc12_lzd_cav_terradon_riders_1_tlaqua"] = true,
		["wh2_dlc12_lzd_cav_terradon_riders_ror_0"] = true,
		["wh2_dlc12_lzd_mon_ancient_salamander_0"] = true,
		["wh2_dlc12_lzd_mon_ancient_salamander_0_blessed"] = true,
		["wh2_dlc12_lzd_mon_ancient_stegadon_1"] = true,
		["wh2_dlc12_lzd_mon_ancient_stegadon_ror_0"] = true,
		["wh2_dlc12_lzd_mon_bastiladon_3"] = true,
		["wh2_dlc13_lzd_mon_dread_saurian_0"] = true,
		["wh2_dlc13_lzd_mon_dread_saurian_1"] = true,
		["wh2_dlc13_lzd_mon_dread_saurian_ror_0"] = true,
		["wh2_dlc14_def_mon_bloodwrack_medusa_0"] = true,
		["wh2_dlc14_def_mon_bloodwrack_medusa_ror_0"] = true,
		["wh2_dlc15_grn_mon_arachnarok_spider_waaagh_0"] = true,
		["wh2_dlc15_grn_mon_feral_hydra_waaagh_0"] = true,
		["wh2_dlc15_grn_mon_rogue_idol_0"] = true,
		["wh2_dlc15_grn_mon_rogue_idol_ror_0"] = true,
		["wh2_dlc15_grn_mon_rogue_idol_summoned_0"] = true,
		["wh2_dlc15_grn_mon_wyvern_waaagh_0"] = true,
		["wh2_dlc15_hef_mon_arcane_phoenix_0"] = true,
		["wh2_dlc15_hef_mon_arcane_phoenix_ror_0"] = true,
		["wh2_dlc15_hef_mon_black_dragon_imrik"] = true,
		["wh2_dlc15_hef_mon_black_dragon_imrik_boss"] = true,
		["wh2_dlc15_hef_mon_forest_dragon_0"] = true,
		["wh2_dlc15_hef_mon_forest_dragon_imrik"] = true,
		["wh2_dlc15_hef_mon_forest_dragon_imrik_boss"] = true,
		["wh2_dlc15_hef_mon_moon_dragon_imrik"] = true,
		["wh2_dlc15_hef_mon_moon_dragon_imrik_boss"] = true,
		["wh2_dlc15_hef_mon_star_dragon_imrik"] = true,
		["wh2_dlc15_hef_mon_star_dragon_imrik_boss"] = true,
		["wh2_dlc15_hef_mon_sun_dragon_imrik"] = true,
		["wh2_dlc15_hef_mon_sun_dragon_imrik_boss"] = true,
		["wh2_dlc16_skv_mon_brood_horror_0"] = true,
		["wh2_dlc16_skv_mon_hell_pit_abomination_ror_0"] = true,
		["wh2_dlc16_skv_mon_rat_ogre_mutant"] = true,
		["wh2_dlc16_skv_mon_rat_ogre_mutant_ror_0"] = true,
		["wh2_dlc16_wef_mon_ceithin_har_summoned"] = true,
		["wh2_dlc16_wef_mon_feral_manticore"] = true,
		["wh2_dlc16_wef_mon_gwindalor_summoned"] = true,
		["wh2_dlc16_wef_mon_hawks_0"] = true,
		["wh2_dlc16_wef_mon_malicious_treeman_0"] = true,
		["wh2_dlc17_bst_mon_ghorgon_0"] = true,
		["wh2_dlc17_bst_mon_ghorgon_boss_0"] = true,
		["wh2_dlc17_bst_mon_ghorgon_ror_0"] = true,
		["wh2_dlc17_bst_mon_jabberslythe_0"] = true,
		["wh2_dlc17_bst_mon_jabberslythe_ror_0"] = true,
		["wh2_dlc17_dwf_mon_carnosaur_thorek_0"] = true,
		["wh2_dlc17_lzd_mon_carnosaur_ror_0"] = true,
		["wh2_dlc17_lzd_mon_coatl_0"] = true,
		["wh2_dlc17_lzd_mon_coatl_ror_0"] = true,
		["wh2_dlc17_lzd_mon_dread_saurian_qb_boss"] = true,
		["wh2_dlc17_lzd_mon_troglodon_0"] = true,
		["wh2_dlc17_lzd_mon_troglodon_ror_0"] = true,
		["wh2_main_def_mon_black_dragon"] = true,
		["wh2_main_def_mon_war_hydra_0"] = true,
		["wh2_main_hef_mon_great_eagle"] = true,
		["wh2_main_hef_mon_great_eagle_summoned"] = true,
		["wh2_main_hef_mon_moon_dragon"] = true,
		["wh2_main_hef_mon_phoenix_flamespyre"] = true,
		["wh2_main_hef_mon_phoenix_frostheart"] = true,
		["wh2_main_hef_mon_star_dragon"] = true,
		["wh2_main_hef_mon_sun_dragon"] = true,
		["wh2_main_lzd_cav_terradon_riders_0"] = true,
		["wh2_main_lzd_cav_terradon_riders_0_blessed"] = true,
		["wh2_main_lzd_cav_terradon_riders_1"] = true,
		["wh2_main_lzd_cav_terradon_riders_blessed_1"] = true,
		["wh2_main_lzd_mon_ancient_stegadon"] = true,
		["wh2_main_lzd_mon_ancient_stegadon_blessed"] = true,
		["wh2_main_lzd_mon_bastiladon_0"] = true,
		["wh2_main_lzd_mon_bastiladon_1"] = true,
		["wh2_main_lzd_mon_bastiladon_2"] = true,
		["wh2_main_lzd_mon_bastiladon_blessed_2"] = true,
		["wh2_main_lzd_mon_carnosaur_0"] = true,
		["wh2_main_lzd_mon_carnosaur_blessed_0"] = true,
		["wh2_main_lzd_mon_stegadon_0"] = true,
		["wh2_main_lzd_mon_stegadon_1"] = true,
		["wh2_main_lzd_mon_stegadon_blessed_1"] = true,
		["wh2_main_skv_mon_hell_pit_abomination"] = true,
		["wh2_main_skv_mon_hell_pit_abomination_summoned"] = true,
		["wh2_pro06_tmb_mon_bone_giant_0"] = true,
		["wh2_twa03_def_mon_war_mammoth_0"] = true,
		["wh3_cp1_cth_mon_celestial_lion_summoned"] = true,
		["wh3_dlc20_chs_mon_giant_mnur_ror"] = true,
		["wh3_dlc20_chs_mon_warshrine"] = true,
		["wh3_dlc20_chs_mon_warshrine_mkho"] = true,
		["wh3_dlc20_chs_mon_warshrine_mnur"] = true,
		["wh3_dlc20_chs_mon_warshrine_msla"] = true,
		["wh3_dlc20_chs_mon_warshrine_mtze"] = true,
		["wh3_dlc23_chd_mon_bale_taurus"] = true,
		["wh3_dlc23_chd_mon_great_taurus"] = true,
		["wh3_dlc23_chd_mon_kdaai_destroyer"] = true,
		["wh3_dlc23_chd_mon_lammasu"] = true,
		["wh3_dlc24_cth_mon_celestial_lion"] = true,
		["wh3_dlc24_cth_mon_great_moon_bird"] = true,
		["wh3_dlc24_ksl_mon_frost_wyrm"] = true,
		["wh3_dlc24_ksl_mon_incarnate_elemental_of_beasts"] = true,
		["wh3_dlc24_ksl_mon_incarnate_elemental_of_beasts_summoned"] = true,
		["wh3_dlc24_tze_mon_cockatrice"] = true,
		["wh3_dlc24_tze_mon_mutalith_vortex_beast"] = true,
		["wh3_dlc24_tze_mon_mutalith_vortex_beast_ror"] = true,
		["wh3_dlc25_bst_mon_jabberslythe_qb_boss"] = true,
		["wh3_dlc25_emp_mon_hawks_summoned"] = true,
		["wh3_dlc25_emp_mon_incarnate_elemental_of_beasts_summoned"] = true,
		["wh3_dlc25_grn_mon_arachnarok_spider_boss"] = true,
		["wh3_dlc25_grn_mon_rogue_idol_qb_boss"] = true,
		["wh3_dlc25_hef_mon_sun_dragon_boss"] = true,
		["wh3_dlc25_nur_mon_toad_dragon"] = true,
		["wh3_dlc26_grn_cav_mangler_squig"] = true,
		["wh3_dlc26_grn_mon_arachnarok_spider_flinger"] = true,
		["wh3_dlc26_grn_mon_colossal_squig"] = true,
		["wh3_dlc26_grn_mon_colossal_squig_ror"] = true,
		["wh3_dlc26_grn_mon_wyvern_summoned"] = true,
		["wh3_dlc26_ogr_mon_thundertusk"] = true,
		["wh3_dlc27_bst_mon_ghorgon_boss"] = true,
		["wh3_dlc27_bst_mon_jabberslythe_boss"] = true,
		["wh3_dlc27_chd_mon_bale_taurus_boss"] = true,
		["wh3_dlc27_chd_mon_lammasu_boss"] = true,
		["wh3_dlc27_chs_feral_manticore_boss"] = true,
		["wh3_dlc27_cth_mon_celestial_lion_boss"] = true,
		["wh3_dlc27_def_mon_black_dragon_boss"] = true,
		["wh3_dlc27_hef_mon_merwyrm"] = true,
		["wh3_dlc27_hef_mon_merwyrm_ror"] = true,
		["wh3_dlc27_hef_mon_merwyrm_summoned"] = true,
		["wh3_dlc27_hef_mon_sea_elemental"] = true,
		["wh3_dlc27_lzd_mon_dread_saurian_boss"] = true,
		["wh3_dlc27_nor_mon_chimera"] = true,
		["wh3_dlc27_nor_mon_chimera_boss"] = true,
		["wh3_dlc27_nor_mon_chimera_ror"] = true,
		["wh3_dlc27_nor_mon_cursd_ettin"] = true,
		["wh3_dlc27_nor_mon_cursd_ettin_runecaller"] = true,
		["wh3_dlc27_nor_mon_dread_maw"] = true,
		["wh3_dlc27_nor_mon_dread_maw_underground"] = true,
		["wh3_dlc27_nur_mon_toad_dragon_boss"] = true,
		["wh3_dlc27_ogr_mon_thundertusk_boss"] = true,
		["wh3_dlc27_sla_mon_preyton"] = true,
		["wh3_dlc27_sla_mon_preyton_boss"] = true,
		["wh3_dlc27_sla_mon_preyton_ror"] = true,
		["wh3_dlc27_tze_mon_cockatrice_boss"] = true,
		["wh3_dlc29_chs_mon_basilisk"] = true,
		["wh3_dlc29_chs_mon_chaos_siege_giant"] = true,
		["wh3_dlc29_chs_mon_giant_spined_chaos_beast"] = true,
		["wh3_dlc29_chs_mon_giant_spined_chaos_beast_ror"] = true,
		["wh3_dlc29_cst_mon_necrofex_colossus_0_summoned"] = true,
		["wh3_dlc29_skv_mon_brood_horror_0_summoned"] = true,
		["wh3_dlc29_skv_veh_cauldron_of_a_thousand_poxes"] = true,
		["wh3_dlc29_tmb_mon_khemrian_warsphinx_0_summoned"] = true,
		["wh3_dlc29_tmb_mon_khemric_titan"] = true,
		["wh3_dlc29_tmb_mon_khemric_titan_ror"] = true,
		["wh3_dlc29_tmb_mon_khemric_titan_summoned"] = true,
		["wh3_dlc29_vmp_mon_terrorgheist_summoned"] = true,
		["wh3_dlc29_vmp_mon_zombie_dragon"] = true,
		["wh3_dlc29_vmp_mon_zombie_dragon_summoned"] = true,
		["wh3_main_cth_mon_terracotta_sentinel_0"] = true,
		["wh3_main_kho_mon_bloodthirster_0"] = true,
		["wh3_main_kho_mon_bloodthirster_summoned_0"] = true,
		["wh3_main_kho_mon_soul_grinder_0"] = true,
		["wh3_main_ksl_mon_elemental_bear_0"] = true,
		["wh3_main_ksl_mon_elemental_bear_summoned_0"] = true,
		["wh3_main_ksl_mon_snow_leopard_0"] = true,
		["wh3_main_ksl_mon_snow_leopard_summoned_0"] = true,
		["wh3_main_ksl_mon_snow_leopard_summoned_1"] = true,
		["wh3_main_ksl_mon_snow_leopard_summoned_2"] = true,
		["wh3_main_nur_mon_beast_of_nurgle_0"] = true,
		["wh3_main_nur_mon_great_unclean_one_0"] = true,
		["wh3_main_nur_mon_great_unclean_one_summoned_0"] = true,
		["wh3_main_ogr_feral_manticore_summoned"] = true,
		["wh3_main_ogr_mon_giant_0"] = true,
		["wh3_main_ogr_mon_stonehorn_0"] = true,
		["wh3_main_ogr_mon_stonehorn_1"] = true,
		["wh3_main_pro_ksl_mon_elemental_bear_ror_0"] = true,
		["wh3_main_sla_mon_keeper_of_secrets_0"] = true,
		["wh3_main_sla_mon_keeper_of_secrets_summoned_0"] = true,
		["wh3_main_sla_mon_soul_grinder_0"] = true,
		["wh3_main_tze_mon_exalted_flamer_0"] = true,
		["wh3_main_tze_mon_lord_of_change_0"] = true,
		["wh3_main_tze_mon_lord_of_change_summoned_0"] = true,
		["wh3_twa08_cth_mon_terracotta_sentinel_0_ror"] = true,
		["wh3_twa08_kho_mon_bloodthirster_0_ror"] = true,
		["wh3_twa08_ksl_mon_elemental_bear_0_ror"] = true,
		["wh3_twa08_nur_mon_great_unclean_one_0_ror"] = true,
		["wh3_twa08_ogr_mon_stonehorn_0_ror"] = true,
		["wh3_twa08_sla_mon_keeper_of_secrets_0_ror"] = true,
		["wh3_twa08_tze_mon_lord_of_change_0_ror"] = true,
		["wh_dlc01_chs_mon_dragon_ogre_shaggoth"] = true,
		["wh_dlc03_bst_feral_manticore"] = true,
		["wh_dlc03_bst_mon_giant_0"] = true,
		["wh_dlc05_wef_forest_dragon_0"] = true,
		["wh_dlc05_wef_mon_great_eagle_0"] = true,
		["wh_dlc05_wef_mon_treeman_0"] = true,
		["wh_dlc06_chs_feral_manticore"] = true,
		["wh_dlc06_grn_mon_venom_queen_0"] = true,
		["wh_dlc08_chs_mon_dragon_ogre_shaggoth_boss"] = true,
		["wh_dlc08_chs_mon_dragon_ogre_shaggoth_minor_boss"] = true,
		["wh_dlc08_grn_mon_arachnarok_spider_boss"] = true,
		["wh_dlc08_grn_mon_giant_boss"] = true,
		["wh_dlc08_nor_feral_manticore"] = true,
		["wh_dlc08_nor_mon_frost_wyrm_0"] = true,
		["wh_dlc08_nor_mon_frost_wyrm_boss"] = true,
		["wh_dlc08_nor_mon_frost_wyrm_ror_0"] = true,
		["wh_dlc08_nor_mon_norscan_giant_0"] = true,
		["wh_dlc08_nor_mon_war_mammoth_0"] = true,
		["wh_dlc08_nor_mon_war_mammoth_1"] = true,
		["wh_dlc08_nor_mon_war_mammoth_2"] = true,
		["wh_dlc08_nor_mon_war_mammoth_boss"] = true,
		["wh_dlc08_nor_mon_war_mammoth_ror_1"] = true,
		["wh_dlc08_vmp_mon_terrorgheist_boss"] = true,
		["wh_dlc08_wef_forest_dragon_boss"] = true,
		["wh_main_bst_feral_manticore_summoned"] = true,
		["wh_main_chs_mon_giant"] = true,
		["wh_main_grn_mon_arachnarok_spider_0"] = true,
		["wh_main_grn_mon_giant"] = true,
		["wh_main_grn_mon_giant_qb_tall_roff"] = true,
		["wh_main_vmp_mon_terrorgheist"] = true,
		["wh_main_vmp_mon_terrorgheist_qb"] = true,
		["wh_main_vmp_mon_varghulf"] = true,
		["wh_pro04_nor_mon_war_mammoth_ror_0"] = true,
	},
	warmachine = {
		["wh2_dlc09_tmb_art_screaming_skull_catapult_0"] = true,
		["wh2_dlc11_cst_art_carronade"] = true,
		["wh2_dlc11_cst_art_mortar"] = true,
		["wh2_dlc11_cst_art_queen_bess"] = true,
		["wh2_dlc12_skv_art_warp_lightning_cannon_ror_0"] = true,
		["wh2_dlc12_skv_veh_doomwheel_ror_0"] = true,
		["wh2_dlc12_skv_veh_doomwheel_ror_tech_lab_0"] = true,
		["wh2_dlc13_emp_art_mortar_ror_0"] = true,
		["wh2_dlc13_huntmarshall_veh_obsinite_gyrocopter_0"] = true,
		["wh2_dlc14_def_veh_bloodwrack_shrine_0"] = true,
		["wh2_main_def_art_reaper_bolt_thrower"] = true,
		["wh2_main_hef_art_eagle_claw_bolt_thrower"] = true,
		["wh2_main_skv_art_plagueclaw_catapult"] = true,
		["wh2_main_skv_art_warp_lightning_cannon"] = true,
		["wh2_main_skv_veh_doomwheel"] = true,
		["wh3_dlc23_chd_veh_deathshrieker_rocket_launcher"] = true,
		["wh3_dlc23_chd_veh_dreadquake_mortar"] = true,
		["wh3_dlc23_chd_veh_iron_daemon"] = true,
		["wh3_dlc23_chd_veh_iron_daemon_1dreadquake"] = true,
		["wh3_dlc23_chd_veh_iron_daemon_3payload_qb"] = true,
		["wh3_dlc23_chd_veh_iron_daemon_ror"] = true,
		["wh3_dlc23_chd_veh_iron_daemon_ror_1dreadquake"] = true,
		["wh3_dlc23_chd_veh_magma_cannon"] = true,
		["wh3_dlc23_chd_veh_skullcracker"] = true,
		["wh3_dlc23_chd_veh_skullcracker_1dreadquake"] = true,
		["wh3_dlc25_dwf_art_flame_cannon_grudge_unit"] = true,
		["wh3_dlc25_dwf_art_goblin_hewer"] = true,
		["wh3_dlc25_dwf_art_grudge_thrower_grudge_unit"] = true,
		["wh3_dlc25_dwf_veh_gyrocopter_1_grudge_unit"] = true,
		["wh3_dlc25_dwf_veh_gyrocopter_summoned_0"] = true,
		["wh3_dlc25_dwf_veh_thunderbarge"] = true,
		["wh3_dlc25_dwf_veh_thunderbarge_grungni"] = true,
		["wh3_dlc25_dwf_veh_thunderbarge_grungni_mp"] = true,
		["wh3_dlc25_emp_art_helstorm_rocket_battery_morr"] = true,
		["wh3_dlc26_grn_art_bolt_throwa"] = true,
		["wh3_dlc26_grn_art_bolt_throwa_ror"] = true,
		["wh3_dlc29_skv_art_plagueclaw_catapult_ror"] = true,
		["wh3_dlc29_skv_art_warp_doom_magma_cannon"] = true,
		["wh3_main_chd_art_hobgob_bolt_thrower"] = true,
		["wh3_main_chs_art_hellcannon_prologue"] = true,
		["wh3_main_cth_art_fire_rain_rocket_battery_0"] = true,
		["wh3_main_cth_art_grand_cannon_0"] = true,
		["wh3_main_cth_veh_sky_junk_0"] = true,
		["wh3_main_cth_veh_sky_lantern_0"] = true,
		["wh_dlc04_emp_art_hammer_of_the_witches_0"] = true,
		["wh_dlc04_emp_art_sunmaker_0"] = true,
		["wh_dlc06_dwf_art_bolt_thrower_0"] = true,
		["wh_dlc06_dwf_art_gob_lobber_0"] = true,
		["wh_dlc06_dwf_veh_skyhammer_0"] = true,
		["wh_dlc06_grn_art_hammer_of_gork_0"] = true,
		["wh_dlc07_brt_art_blessed_field_trebuchet_0"] = true,
		["wh_dlc08_nor_art_hellcannon_battery"] = true,
		["wh_main_brt_art_field_trebuchet"] = true,
		["wh_main_chs_art_hellcannon"] = true,
		["wh_main_dwf_art_cannon"] = true,
		["wh_main_dwf_art_flame_cannon"] = true,
		["wh_main_dwf_art_grudge_thrower"] = true,
		["wh_main_dwf_art_organ_gun"] = true,
		["wh_main_dwf_veh_gyrobomber"] = true,
		["wh_main_dwf_veh_gyrocopter_0"] = true,
		["wh_main_dwf_veh_gyrocopter_1"] = true,
		["wh_main_emp_art_great_cannon"] = true,
		["wh_main_emp_art_helblaster_volley_gun"] = true,
		["wh_main_emp_art_helstorm_rocket_battery"] = true,
		["wh_main_emp_art_mortar"] = true,
		["wh_main_grn_art_doom_diver_catapult"] = true,
		["wh_main_grn_art_goblin_rock_lobber"] = true,
		["wh_pro04_chs_art_hellcannon_ror_0"] = true,
	},
	construct = {
		["wh2_dlc09_tmb_cav_necropolis_knights_0"] = true,
		["wh2_dlc09_tmb_cav_necropolis_knights_1"] = true,
		["wh2_dlc09_tmb_cav_necropolis_knights_ror"] = true,
		["wh2_dlc09_tmb_mon_heirotitan_0"] = true,
		["wh2_dlc09_tmb_mon_khemrian_warsphinx_0"] = true,
		["wh2_dlc09_tmb_mon_necrosphinx_0"] = true,
		["wh2_dlc09_tmb_mon_necrosphinx_ror"] = true,
		["wh2_dlc09_tmb_mon_sepulchral_stalkers_0"] = true,
		["wh2_dlc09_tmb_mon_sepulchral_stalkers_ror"] = true,
		["wh2_dlc09_tmb_mon_tomb_scorpion_0"] = true,
		["wh2_dlc09_tmb_mon_ushabti_0"] = true,
		["wh2_dlc09_tmb_mon_ushabti_0_summoned"] = true,
		["wh2_dlc09_tmb_mon_ushabti_1"] = true,
		["wh2_dlc09_tmb_mon_ushabti_ror"] = true,
		["wh2_dlc15_grn_mon_rogue_idol_0"] = true,
		["wh2_dlc15_grn_mon_rogue_idol_ror_0"] = true,
		["wh2_dlc15_grn_mon_rogue_idol_summoned_0"] = true,
		["wh2_pro06_tmb_mon_bone_giant_0"] = true,
		["wh3_dlc24_cth_cha_saytang_the_watcher"] = true,
		["wh3_dlc24_cth_mon_jade_lion"] = true,
		["wh3_dlc24_cth_mon_jet_lion"] = true,
		["wh3_dlc25_grn_mon_rogue_idol_qb_boss"] = true,
		["wh3_dlc29_tmb_mon_khemrian_warsphinx_0_summoned"] = true,
		["wh3_dlc29_tmb_mon_khemric_titan"] = true,
		["wh3_dlc29_tmb_mon_khemric_titan_ror"] = true,
		["wh3_dlc29_tmb_mon_khemric_titan_summoned"] = true,
		["wh3_dlc29_tmb_mon_ushabti_ror_sepulchrex"] = true,
		["wh3_main_cth_mon_terracotta_sentinel_0"] = true,
		["wh3_twa08_cth_mon_terracotta_sentinel_0_ror"] = true,
	},
	hellforged = {
		["wh3_dlc23_chd_mon_kdaai_destroyer"] = true,
		["wh3_dlc23_chd_mon_kdaai_fireborn"] = true,
		["wh3_dlc23_chd_mon_kdaai_fireborn_summoned"] = true,
		["wh3_dlc23_chd_veh_deathshrieker_rocket_launcher"] = true,
		["wh3_dlc23_chd_veh_dreadquake_mortar"] = true,
		["wh3_dlc23_chd_veh_iron_daemon"] = true,
		["wh3_dlc23_chd_veh_iron_daemon_1dreadquake"] = true,
		["wh3_dlc23_chd_veh_iron_daemon_3payload_qb"] = true,
		["wh3_dlc23_chd_veh_iron_daemon_ror"] = true,
		["wh3_dlc23_chd_veh_iron_daemon_ror_1dreadquake"] = true,
		["wh3_dlc23_chd_veh_magma_cannon"] = true,
		["wh3_dlc23_chd_veh_skullcracker"] = true,
		["wh3_dlc23_chd_veh_skullcracker_1dreadquake"] = true,
	},
	missile = {
		["wh2_dlc09_tmb_art_casket_of_souls_0"] = true,
		["wh2_dlc09_tmb_cav_skeleton_horsemen_archers_0"] = true,
		["wh2_dlc09_tmb_cha_khatep_3"] = true,
		["wh2_dlc09_tmb_inf_skeleton_archers_0"] = true,
		["wh2_dlc09_tmb_inf_skeleton_archers_ror"] = true,
		["wh2_dlc09_tmb_mon_sepulchral_stalkers_0"] = true,
		["wh2_dlc09_tmb_mon_sepulchral_stalkers_ror"] = true,
		["wh2_dlc09_tmb_mon_ushabti_1"] = true,
		["wh2_dlc09_tmb_mon_ushabti_ror"] = true,
		["wh2_dlc09_tmb_veh_skeleton_archer_chariot_0"] = true,
		["wh2_dlc10_def_cav_raven_heralds_ror_0"] = true,
		["wh2_dlc10_def_inf_the_bolt_fiends_ror_0"] = true,
		["wh2_dlc10_hef_cav_the_heralds_of_the_wind_ror_0"] = true,
		["wh2_dlc10_hef_cha_alith_anar_0"] = true,
		["wh2_dlc10_hef_cha_alith_anar_summoned_0"] = true,
		["wh2_dlc10_hef_cha_alith_anar_summoned_1"] = true,
		["wh2_dlc10_hef_cha_handmaiden_0"] = true,
		["wh2_dlc10_hef_cha_handmaiden_1"] = true,
		["wh2_dlc10_hef_cha_handmaiden_2"] = true,
		["wh2_dlc10_hef_cha_shadow_walker"] = true,
		["wh2_dlc10_hef_inf_everqueens_court_guards_ror_0"] = true,
		["wh2_dlc10_hef_inf_shadow_walkers_0"] = true,
		["wh2_dlc10_hef_inf_shadow_warriors_0"] = true,
		["wh2_dlc10_hef_inf_sisters_of_avelorn_0"] = true,
		["wh2_dlc10_hef_inf_the_grey_ror_0"] = true,
		["wh2_dlc10_hef_inf_the_storm_riders_ror_0"] = true,
		["wh2_dlc11_cst_cav_deck_droppers_0"] = true,
		["wh2_dlc11_cst_cav_deck_droppers_1"] = true,
		["wh2_dlc11_cst_cav_deck_droppers_2"] = true,
		["wh2_dlc11_cst_cav_deck_droppers_ror_0"] = true,
		["wh2_dlc11_cst_cha_gunnery_wight_0"] = true,
		["wh2_dlc11_cst_cha_gunnery_wight_1"] = true,
		["wh2_dlc11_cst_cha_luthor_harkon_0"] = true,
		["wh2_dlc11_cst_cha_luthor_harkon_1"] = true,
		["wh2_dlc11_cst_cha_vampire_fleet_admiral_female_0"] = true,
		["wh2_dlc11_cst_cha_vampire_fleet_admiral_female_1"] = true,
		["wh2_dlc11_cst_cha_vampire_fleet_admiral_female_death_0"] = true,
		["wh2_dlc11_cst_cha_vampire_fleet_admiral_female_death_1"] = true,
		["wh2_dlc11_cst_cha_vampire_fleet_admiral_female_deeps_0"] = true,
		["wh2_dlc11_cst_cha_vampire_fleet_admiral_female_deeps_1"] = true,
		["wh2_dlc11_cst_inf_count_noctilus_1"] = true,
		["wh2_dlc11_cst_inf_deck_gunners_0"] = true,
		["wh2_dlc11_cst_inf_deck_gunners_0_summoned"] = true,
		["wh2_dlc11_cst_inf_deck_gunners_ror_0"] = true,
		["wh2_dlc11_cst_inf_sartosa_militia_0"] = true,
		["wh2_dlc11_cst_inf_zombie_gunnery_mob_0"] = true,
		["wh2_dlc11_cst_inf_zombie_gunnery_mob_1"] = true,
		["wh2_dlc11_cst_inf_zombie_gunnery_mob_2"] = true,
		["wh2_dlc11_cst_inf_zombie_gunnery_mob_3"] = true,
		["wh2_dlc11_cst_inf_zombie_gunnery_mob_ror_0"] = true,
		["wh2_dlc11_cst_inf_zombie_gunnery_mob_summoned_0"] = true,
		["wh2_dlc11_cst_mon_necrofex_colossus_0"] = true,
		["wh2_dlc11_cst_mon_necrofex_colossus_ror_0"] = true,
		["wh2_dlc11_vmp_inf_crossbowmen"] = true,
		["wh2_dlc11_vmp_inf_handgunners"] = true,
		["wh2_dlc12_lzd_cav_terradon_riders_0_tlaqua"] = true,
		["wh2_dlc12_lzd_cav_terradon_riders_1_tlaqua"] = true,
		["wh2_dlc12_lzd_cav_terradon_riders_ror_0"] = true,
		["wh2_dlc12_lzd_cha_skink_chief_red_crested_3"] = true,
		["wh2_dlc12_lzd_mon_ancient_salamander_0"] = true,
		["wh2_dlc12_lzd_mon_ancient_salamander_0_blessed"] = true,
		["wh2_dlc12_lzd_mon_ancient_stegadon_ror_0"] = true,
		["wh2_dlc12_lzd_mon_salamander_pack_0"] = true,
		["wh2_dlc12_lzd_mon_salamander_pack_0_blessed"] = true,
		["wh2_dlc12_lzd_mon_salamander_pack_ror_0"] = true,
		["wh2_dlc12_skv_art_warplock_jezzails_ror_tech_lab_0"] = true,
		["wh2_dlc12_skv_cha_ikit_claw_0"] = true,
		["wh2_dlc12_skv_inf_ratling_gun_0"] = true,
		["wh2_dlc12_skv_inf_ratling_gun_ror_0"] = true,
		["wh2_dlc12_skv_inf_ratling_gun_ror_tech_lab_0"] = true,
		["wh2_dlc12_skv_inf_warpfire_thrower_ror_tech_lab_0"] = true,
		["wh2_dlc12_skv_inf_warplock_jezzails_0"] = true,
		["wh2_dlc12_skv_inf_warplock_jezzails_ror_0"] = true,
		["wh2_dlc13_emp_cav_outriders_ror_0"] = true,
		["wh2_dlc13_emp_cav_pistoliers_ror_0"] = true,
		["wh2_dlc13_emp_cha_hunter_doctor_hertwig_van_hal_0"] = true,
		["wh2_dlc13_emp_cha_hunter_jorek_grimm_0"] = true,
		["wh2_dlc13_emp_cha_hunter_kalara_of_wydrioth_0"] = true,
		["wh2_dlc13_emp_cha_huntsmarshal_0"] = true,
		["wh2_dlc13_emp_cha_markus_wulfhart_0"] = true,
		["wh2_dlc13_emp_inf_archers_0"] = true,
		["wh2_dlc13_emp_inf_archers_ror_0"] = true,
		["wh2_dlc13_emp_inf_crossbowmen_ror_0"] = true,
		["wh2_dlc13_emp_inf_handgunners_ror_0"] = true,
		["wh2_dlc13_emp_inf_huntsmen_0"] = true,
		["wh2_dlc13_emp_inf_huntsmen_ror_0"] = true,
		["wh2_dlc13_emp_veh_steam_tank_driver_ror_0"] = true,
		["wh2_dlc13_emp_veh_war_wagon_0"] = true,
		["wh2_dlc13_emp_veh_war_wagon_1"] = true,
		["wh2_dlc13_emp_veh_war_wagon_ror_0"] = true,
		["wh2_dlc13_huntmarshall_veh_obsinite_gyrocopter_0"] = true,
		["wh2_dlc13_lzd_mon_razordon_pack_0"] = true,
		["wh2_dlc13_lzd_mon_razordon_pack_0_blessed"] = true,
		["wh2_dlc13_lzd_mon_razordon_pack_ror_0"] = true,
		["wh2_dlc13_lzd_mon_razordon_pack_summoned_0"] = true,
		["wh2_dlc14_def_cav_scourgerunner_chariot_0"] = true,
		["wh2_dlc14_def_cav_scourgerunner_chariot_ror_0"] = true,
		["wh2_dlc14_def_cha_high_beastmaster_1"] = true,
		["wh2_dlc14_def_mon_bloodwrack_medusa_0"] = true,
		["wh2_dlc14_def_mon_bloodwrack_medusa_ror_0"] = true,
		["wh2_dlc14_def_veh_bloodwrack_shrine_0"] = true,
		["wh2_dlc14_skv_cha_master_assassin_0"] = true,
		["wh2_dlc14_skv_inf_poison_wind_mortar_0"] = true,
		["wh2_dlc14_skv_inf_poison_wind_mortar_ror_0"] = true,
		["wh2_dlc15_grn_cav_forest_goblin_spider_riders_waaagh_0"] = true,
		["wh2_dlc15_grn_mon_rogue_idol_ror_0"] = true,
		["wh2_dlc15_hef_cha_princess_6"] = true,
		["wh2_dlc15_hef_inf_archers_ror_0"] = true,
		["wh2_dlc15_hef_inf_mistwalkers_sentinels_0"] = true,
		["wh2_dlc15_hef_inf_mistwalkers_skyhawks_0"] = true,
		["wh2_dlc15_hef_inf_mistwalkers_spireguard_0"] = true,
		["wh2_dlc16_wef_cha_female_glade_lord_4"] = true,
		["wh2_dlc16_wef_cha_glade_lord_4"] = true,
		["wh2_dlc16_wef_cha_sisters_of_twilight_0"] = true,
		["wh2_dlc16_wef_cha_sisters_of_twilight_1"] = true,
		["wh2_dlc17_bst_inf_centigors_ror_1"] = true,
		["wh2_dlc17_lzd_cha_oxyotl_0"] = true,
		["wh2_dlc17_lzd_cha_skink_oracle_troglodon_0"] = true,
		["wh2_dlc17_lzd_inf_chameleon_stalkers_0"] = true,
		["wh2_dlc17_lzd_inf_chameleon_stalkers_0_blessed"] = true,
		["wh2_dlc17_lzd_mon_troglodon_0"] = true,
		["wh2_dlc17_lzd_mon_troglodon_ror_0"] = true,
		["wh2_main_def_cav_cold_one_chariot"] = true,
		["wh2_main_def_cav_dark_riders_2"] = true,
		["wh2_main_def_cha_dreadlord_0"] = true,
		["wh2_main_def_cha_dreadlord_1"] = true,
		["wh2_main_def_cha_dreadlord_2"] = true,
		["wh2_main_def_cha_dreadlord_4"] = true,
		["wh2_main_def_cha_dreadlord_5"] = true,
		["wh2_main_def_cha_khainite_assassin_0"] = true,
		["wh2_main_def_inf_black_ark_corsairs_1"] = true,
		["wh2_main_def_inf_darkshards_0"] = true,
		["wh2_main_def_inf_darkshards_1"] = true,
		["wh2_main_def_inf_shades_0"] = true,
		["wh2_main_def_inf_shades_1"] = true,
		["wh2_main_def_inf_shades_2"] = true,
		["wh2_main_hef_cav_ellyrian_reavers_1"] = true,
		["wh2_main_hef_cav_tiranoc_chariot"] = true,
		["wh2_main_hef_cha_princess_0"] = true,
		["wh2_main_hef_cha_princess_1"] = true,
		["wh2_main_hef_cha_princess_3"] = true,
		["wh2_main_hef_cha_princess_4"] = true,
		["wh2_main_hef_cha_princess_5"] = true,
		["wh2_main_hef_inf_archers_0"] = true,
		["wh2_main_hef_inf_archers_1"] = true,
		["wh2_main_hef_inf_gate_guard"] = true,
		["wh2_main_hef_inf_lothern_sea_guard_0"] = true,
		["wh2_main_hef_inf_lothern_sea_guard_1"] = true,
		["wh2_main_lzd_cav_terradon_riders_0"] = true,
		["wh2_main_lzd_cav_terradon_riders_0_blessed"] = true,
		["wh2_main_lzd_cav_terradon_riders_1"] = true,
		["wh2_main_lzd_cav_terradon_riders_blessed_1"] = true,
		["wh2_main_lzd_cha_skink_chief_0"] = true,
		["wh2_main_lzd_cha_skink_chief_1"] = true,
		["wh2_main_lzd_cha_skink_chief_2"] = true,
		["wh2_main_lzd_cha_skink_chief_3"] = true,
		["wh2_main_lzd_cha_skink_priest_beasts_2"] = true,
		["wh2_main_lzd_cha_skink_priest_beasts_3"] = true,
		["wh2_main_lzd_cha_skink_priest_heavens_2"] = true,
		["wh2_main_lzd_cha_skink_priest_heavens_3"] = true,
		["wh2_main_lzd_inf_chameleon_skinks_0"] = true,
		["wh2_main_lzd_inf_chameleon_skinks_blessed_0"] = true,
		["wh2_main_lzd_inf_skink_cohort_1"] = true,
		["wh2_main_lzd_inf_skink_cohort_1_blessed"] = true,
		["wh2_main_lzd_inf_skink_skirmishers_0"] = true,
		["wh2_main_lzd_inf_skink_skirmishers_blessed_0"] = true,
		["wh2_main_lzd_mon_ancient_stegadon"] = true,
		["wh2_main_lzd_mon_ancient_stegadon_blessed"] = true,
		["wh2_main_lzd_mon_bastiladon_2"] = true,
		["wh2_main_lzd_mon_bastiladon_blessed_2"] = true,
		["wh2_main_lzd_mon_stegadon_1"] = true,
		["wh2_main_lzd_mon_stegadon_blessed_1"] = true,
		["wh2_main_skv_inf_death_globe_bombardiers"] = true,
		["wh2_main_skv_inf_gutter_runner_slingers_0"] = true,
		["wh2_main_skv_inf_gutter_runner_slingers_1"] = true,
		["wh2_main_skv_inf_gutter_runners_0"] = true,
		["wh2_main_skv_inf_gutter_runners_1"] = true,
		["wh2_main_skv_inf_night_runners_0"] = true,
		["wh2_main_skv_inf_night_runners_1"] = true,
		["wh2_main_skv_inf_poison_wind_globadiers"] = true,
		["wh2_main_skv_inf_skavenslave_slingers_0"] = true,
		["wh2_main_skv_inf_warpfire_thrower"] = true,
		["wh2_pro06_tmb_mon_bone_giant_0"] = true,
		["wh2_twa02_wef_cha_glade_captain_0"] = true,
		["wh2_twa02_wef_cha_glade_captain_1"] = true,
		["wh2_twa02_wef_cha_glade_captain_2"] = true,
		["wh2_twa02_wef_cha_glade_captain_3"] = true,
		["wh2_twa03_def_cha_rakarth_1"] = true,
		["wh3_cp1_cth_inf_stalkers_throwing_disc"] = true,
		["wh3_dlc20_chs_cav_marauder_horsemen_mkho_throwing_axes"] = true,
		["wh3_dlc20_chs_cav_marauder_horsemen_mnur_throwing_axes"] = true,
		["wh3_dlc20_chs_cav_marauder_horsemen_msla_javelins"] = true,
		["wh3_dlc20_chs_cav_marauder_horsemen_mtze_javelins"] = true,
		["wh3_dlc23_chd_cav_bull_centaurs_dual_axe_ror"] = true,
		["wh3_dlc23_chd_cav_hobgoblin_wolf_raiders_bows"] = true,
		["wh3_dlc23_chd_cav_hobgoblin_wolf_raiders_ror"] = true,
		["wh3_dlc23_chd_cha_daemonsmith_sorcerer_death"] = true,
		["wh3_dlc23_chd_cha_daemonsmith_sorcerer_death_bale_taurus"] = true,
		["wh3_dlc23_chd_cha_daemonsmith_sorcerer_death_great_taurus"] = true,
		["wh3_dlc23_chd_cha_daemonsmith_sorcerer_death_lammasu"] = true,
		["wh3_dlc23_chd_cha_daemonsmith_sorcerer_fire"] = true,
		["wh3_dlc23_chd_cha_daemonsmith_sorcerer_fire_bale_taurus"] = true,
		["wh3_dlc23_chd_cha_daemonsmith_sorcerer_fire_great_taurus"] = true,
		["wh3_dlc23_chd_cha_daemonsmith_sorcerer_fire_lammasu"] = true,
		["wh3_dlc23_chd_cha_daemonsmith_sorcerer_hashut"] = true,
		["wh3_dlc23_chd_cha_daemonsmith_sorcerer_hashut_bale_taurus"] = true,
		["wh3_dlc23_chd_cha_daemonsmith_sorcerer_hashut_great_taurus"] = true,
		["wh3_dlc23_chd_cha_daemonsmith_sorcerer_hashut_lammasu"] = true,
		["wh3_dlc23_chd_cha_daemonsmith_sorcerer_metal"] = true,
		["wh3_dlc23_chd_cha_daemonsmith_sorcerer_metal_bale_taurus"] = true,
		["wh3_dlc23_chd_cha_daemonsmith_sorcerer_metal_great_taurus"] = true,
		["wh3_dlc23_chd_cha_daemonsmith_sorcerer_metal_lammasu"] = true,
		["wh3_dlc23_chd_cha_infernal_castellan"] = true,
		["wh3_dlc23_chd_cha_sorcerer_prophet_death"] = true,
		["wh3_dlc23_chd_cha_sorcerer_prophet_death_bale_taurus"] = true,
		["wh3_dlc23_chd_cha_sorcerer_prophet_death_great_taurus"] = true,
		["wh3_dlc23_chd_cha_sorcerer_prophet_death_lammasu"] = true,
		["wh3_dlc23_chd_cha_sorcerer_prophet_fire"] = true,
		["wh3_dlc23_chd_cha_sorcerer_prophet_fire_bale_taurus"] = true,
		["wh3_dlc23_chd_cha_sorcerer_prophet_fire_great_taurus"] = true,
		["wh3_dlc23_chd_cha_sorcerer_prophet_fire_lammasu"] = true,
		["wh3_dlc23_chd_cha_sorcerer_prophet_hashut"] = true,
		["wh3_dlc23_chd_cha_sorcerer_prophet_hashut_bale_taurus"] = true,
		["wh3_dlc23_chd_cha_sorcerer_prophet_hashut_great_taurus"] = true,
		["wh3_dlc23_chd_cha_sorcerer_prophet_hashut_lammasu"] = true,
		["wh3_dlc23_chd_cha_sorcerer_prophet_metal"] = true,
		["wh3_dlc23_chd_cha_sorcerer_prophet_metal_bale_taurus"] = true,
		["wh3_dlc23_chd_cha_sorcerer_prophet_metal_great_taurus"] = true,
		["wh3_dlc23_chd_cha_sorcerer_prophet_metal_lammasu"] = true,
		["wh3_dlc23_chd_inf_chaos_dwarf_blunderbusses"] = true,
		["wh3_dlc23_chd_inf_chaos_dwarf_blunderbusses_ror"] = true,
		["wh3_dlc23_chd_inf_chaos_dwarf_warriors_ror"] = true,
		["wh3_dlc23_chd_inf_hobgoblin_archers"] = true,
		["wh3_dlc23_chd_inf_hobgoblin_sneaky_gits"] = true,
		["wh3_dlc23_chd_inf_infernal_guard_fireglaives"] = true,
		["wh3_dlc23_chd_inf_infernal_ironsworn"] = true,
		["wh3_dlc23_chd_veh_deathshrieker_rocket_launcher"] = true,
		["wh3_dlc23_chd_veh_dreadquake_mortar"] = true,
		["wh3_dlc23_chd_veh_iron_daemon"] = true,
		["wh3_dlc23_chd_veh_iron_daemon_1dreadquake"] = true,
		["wh3_dlc23_chd_veh_iron_daemon_ror"] = true,
		["wh3_dlc23_chd_veh_iron_daemon_ror_1dreadquake"] = true,
		["wh3_dlc23_chd_veh_magma_cannon"] = true,
		["wh3_dlc23_chd_veh_skullcracker_1dreadquake"] = true,
		["wh3_dlc23_neu_cha_ulrika"] = true,
		["wh3_dlc23_neu_cha_ulrika_warhorse"] = true,
		["wh3_dlc24_cth_cha_gate_master"] = true,
		["wh3_dlc24_cth_cha_gate_master_warhorse"] = true,
		["wh3_dlc24_cth_cha_saytang_the_watcher"] = true,
		["wh3_dlc24_cth_inf_dragon_guard_crossbowmen_ror"] = true,
		["wh3_dlc24_ksl_cha_druzhina"] = true,
		["wh3_dlc24_ksl_cha_druzhina_warhorse"] = true,
		["wh3_dlc24_ksl_cha_hag_witch_beast"] = true,
		["wh3_dlc24_ksl_cha_hag_witch_death"] = true,
		["wh3_dlc24_ksl_cha_hag_witch_hag"] = true,
		["wh3_dlc24_ksl_cha_hag_witch_shadow"] = true,
		["wh3_dlc24_ksl_cha_katarin_ice_court_sled"] = true,
		["wh3_dlc24_ksl_cha_mother_ostankya"] = true,
		["wh3_dlc24_ksl_inf_akshina_ambushers"] = true,
		["wh3_dlc24_ksl_inf_akshina_ambushers_ror"] = true,
		["wh3_dlc24_ksl_inf_streltsi_ror"] = true,
		["wh3_dlc24_tze_cha_blue_scribes"] = true,
		["wh3_dlc24_tze_inf_pink_horrors_ror"] = true,
		["wh3_dlc24_tze_mon_flamers_changebringers"] = true,
		["wh3_dlc25_dwf_cha_malakai_makaisson"] = true,
		["wh3_dlc25_dwf_inf_irondrakes_0_grudge_unit"] = true,
		["wh3_dlc25_dwf_inf_miners_1_summoned"] = true,
		["wh3_dlc25_dwf_inf_quarrellers_1_grudge_unit"] = true,
		["wh3_dlc25_dwf_inf_slayer_pirates"] = true,
		["wh3_dlc25_dwf_inf_slayer_pirates_ror"] = true,
		["wh3_dlc25_dwf_inf_thunderers_grudge_rakers"] = true,
		["wh3_dlc25_dwf_inf_thunderers_ror"] = true,
		["wh3_dlc25_dwf_veh_gyrocopter_1_grudge_unit"] = true,
		["wh3_dlc25_dwf_veh_gyrocopter_summoned_0"] = true,
		["wh3_dlc25_dwf_veh_thunderbarge"] = true,
		["wh3_dlc25_dwf_veh_thunderbarge_grungni"] = true,
		["wh3_dlc25_dwf_veh_thunderbarge_grungni_mp"] = true,
		["wh3_dlc25_emp_cav_outriders_morr"] = true,
		["wh3_dlc25_emp_cha_engineer"] = true,
		["wh3_dlc25_emp_cha_engineer_mechanical_steed"] = true,
		["wh3_dlc25_emp_cha_engineer_warhorse"] = true,
		["wh3_dlc25_emp_cha_master_engineer"] = true,
		["wh3_dlc25_emp_cha_master_engineer_mechanical_steed"] = true,
		["wh3_dlc25_emp_cha_master_engineer_steam_tank"] = true,
		["wh3_dlc25_emp_cha_master_engineer_warhorse"] = true,
		["wh3_dlc25_emp_inf_hochland_long_rifles"] = true,
		["wh3_dlc25_emp_inf_hochland_long_rifles_ror"] = true,
		["wh3_dlc25_emp_inf_nuln_ironsides"] = true,
		["wh3_dlc25_emp_inf_nuln_ironsides_morr"] = true,
		["wh3_dlc25_emp_veh_marienburg_land_ship"] = true,
		["wh3_dlc25_emp_veh_marienburg_land_ship_morr"] = true,
		["wh3_dlc25_emp_veh_marienburg_land_ship_ror"] = true,
		["wh3_dlc25_emp_veh_steam_tank_volley_gun"] = true,
		["wh3_dlc25_grn_mon_rogue_idol_qb_boss"] = true,
		["wh3_dlc25_nur_cav_plague_drones_1_ror"] = true,
		["wh3_dlc25_nur_cha_infernal_castellan_chieftain"] = true,
		["wh3_dlc25_nur_mon_soul_grinder_0_ror"] = true,
		["wh3_dlc26_grn_inf_rugluds_armoured_orcs"] = true,
		["wh3_dlc26_grn_mon_arachnarok_spider_flinger"] = true,
		["wh3_dlc26_kho_veh_skullcannon_ror"] = true,
		["wh3_dlc26_ogr_mon_thundertusk"] = true,
		["wh3_dlc27_hef_veh_skycutter_bolt_thrower"] = true,
		["wh3_dlc27_hef_veh_skycutter_bows"] = true,
		["wh3_dlc27_nor_cav_marauder_horsemen_ror"] = true,
		["wh3_dlc27_nor_mon_dread_maw"] = true,
		["wh3_dlc27_nor_mon_dread_maw_underground"] = true,
		["wh3_dlc27_ogr_mon_thundertusk_boss"] = true,
		["wh3_dlc27_sla_inf_devotees_of_slaanesh_crossbows"] = true,
		["wh3_dlc29_chs_cav_nur_plague_drones_1_summoned"] = true,
		["wh3_dlc29_cst_cha_gunnery_wight_0_summoned"] = true,
		["wh3_dlc29_cst_cha_vampire_fleet_admiral_female_undeath"] = true,
		["wh3_dlc29_cst_cha_vampire_fleet_admiral_female_undeath_rotting_promethean"] = true,
		["wh3_dlc29_cst_inf_zombie_pirate_gunnery_mob_bombers_summoned"] = true,
		["wh3_dlc29_cst_mon_necrofex_colossus_0_summoned"] = true,
		["wh3_dlc29_skv_cha_thanquol_boneripper_warpfire_projectors"] = true,
		["wh3_dlc29_skv_cha_verminlord_deceiver"] = true,
		["wh3_dlc29_skv_inf_poison_wind_mortar_0_summoned"] = true,
		["wh3_dlc29_skv_inf_skavenslave_slingers_vermintide"] = true,
		["wh3_dlc29_skv_mon_stormfiend_ratling_cannons"] = true,
		["wh3_dlc29_skv_mon_stormfiend_warpfire_projectors"] = true,
		["wh3_dlc29_skv_mon_stormfiend_windlaunchers"] = true,
		["wh3_dlc29_skv_mon_stormfiends_ratling_cannons_ror"] = true,
		["wh3_dlc29_tmb_veh_skeleton_archer_chariot_0_summoned"] = true,
		["wh3_main_cth_cha_alchemist_2"] = true,
		["wh3_main_cth_cha_lord_magistrate_2"] = true,
		["wh3_main_cth_inf_crane_gunners_0"] = true,
		["wh3_main_cth_inf_dragon_guard_crossbowmen_0"] = true,
		["wh3_main_cth_inf_grenadiers"] = true,
		["wh3_main_cth_inf_iron_hail_gunners_0"] = true,
		["wh3_main_cth_inf_jade_warrior_crossbowmen_0"] = true,
		["wh3_main_cth_inf_jade_warrior_crossbowmen_1"] = true,
		["wh3_main_cth_inf_peasant_archers_0"] = true,
		["wh3_main_cth_veh_sky_junk_0"] = true,
		["wh3_main_cth_veh_sky_lantern_0"] = true,
		["wh3_main_kho_mon_soul_grinder_0"] = true,
		["wh3_main_kho_veh_skullcannon_0"] = true,
		["wh3_main_ksl_cav_horse_archers_0"] = true,
		["wh3_main_ksl_cha_ataman"] = true,
		["wh3_main_ksl_inf_armoured_kossars_0"] = true,
		["wh3_main_ksl_inf_armoured_kossars_1"] = true,
		["wh3_main_ksl_inf_ice_guard_0"] = true,
		["wh3_main_ksl_inf_ice_guard_1"] = true,
		["wh3_main_ksl_inf_kossars_0"] = true,
		["wh3_main_ksl_inf_kossars_1"] = true,
		["wh3_main_ksl_inf_streltsi_0"] = true,
		["wh3_main_ksl_veh_heavy_war_sled_0"] = true,
		["wh3_main_ksl_veh_light_war_sled_0"] = true,
		["wh3_main_ksl_veh_little_grom_0"] = true,
		["wh3_main_nur_cav_plague_drones_1"] = true,
		["wh3_main_nur_cha_ku_gath_plaguefather_0"] = true,
		["wh3_main_nur_inf_plaguebearers_1"] = true,
		["wh3_main_nur_inf_plaguebearers_1_summoned"] = true,
		["wh3_main_nur_mon_soul_grinder_0"] = true,
		["wh3_main_ogr_cha_hunter_0"] = true,
		["wh3_main_ogr_cha_hunter_1"] = true,
		["wh3_main_ogr_inf_gnoblars_1"] = true,
		["wh3_main_ogr_inf_gnoblars_flingers"] = true,
		["wh3_main_ogr_inf_leadbelchers_0"] = true,
		["wh3_main_ogr_inf_maneaters_3"] = true,
		["wh3_main_ogr_mon_stonehorn_1"] = true,
		["wh3_main_ogr_veh_gnoblar_scraplauncher_0"] = true,
		["wh3_main_ogr_veh_ironblaster_0"] = true,
		["wh3_main_pro_ksl_inf_armoured_kossars_0"] = true,
		["wh3_main_pro_ksl_inf_armoured_kossars_1"] = true,
		["wh3_main_pro_ksl_inf_kossars_0"] = true,
		["wh3_main_pro_ksl_inf_kossars_1"] = true,
		["wh3_main_pro_ksl_inf_streltsi_0"] = true,
		["wh3_main_pro_ksl_veh_little_grom_0"] = true,
		["wh3_main_pro_tze_cha_herald_of_tzeentch_tzeentch_0"] = true,
		["wh3_main_pro_tze_cha_herald_of_tzeentch_tzeentch_1"] = true,
		["wh3_main_pro_tze_cha_herald_of_tzeentch_tzeentch_2"] = true,
		["wh3_main_pro_tze_inf_blue_horrors_0"] = true,
		["wh3_main_pro_tze_inf_pink_horrors_0"] = true,
		["wh3_main_pro_tze_mon_flamers_0"] = true,
		["wh3_main_tze_cha_herald_of_tzeentch_metal_0"] = true,
		["wh3_main_tze_cha_herald_of_tzeentch_metal_1"] = true,
		["wh3_main_tze_cha_herald_of_tzeentch_metal_2"] = true,
		["wh3_main_tze_cha_herald_of_tzeentch_tzeentch_0"] = true,
		["wh3_main_tze_cha_herald_of_tzeentch_tzeentch_1"] = true,
		["wh3_main_tze_cha_herald_of_tzeentch_tzeentch_2"] = true,
		["wh3_main_tze_cha_iridescent_horror_metal_0"] = true,
		["wh3_main_tze_cha_iridescent_horror_metal_1"] = true,
		["wh3_main_tze_cha_iridescent_horror_metal_2"] = true,
		["wh3_main_tze_cha_iridescent_horror_tzeentch_0"] = true,
		["wh3_main_tze_cha_iridescent_horror_tzeentch_1"] = true,
		["wh3_main_tze_cha_iridescent_horror_tzeentch_2"] = true,
		["wh3_main_tze_inf_blue_horrors_0"] = true,
		["wh3_main_tze_inf_blue_horrors_summoned_0"] = true,
		["wh3_main_tze_inf_pink_horrors_0"] = true,
		["wh3_main_tze_inf_pink_horrors_1"] = true,
		["wh3_main_tze_inf_pink_horrors_summoned_0"] = true,
		["wh3_main_tze_mon_exalted_flamer_0"] = true,
		["wh3_main_tze_mon_flamers_0"] = true,
		["wh3_main_tze_mon_soul_grinder_0"] = true,
		["wh3_main_tze_veh_burning_chariot_0"] = true,
		["wh3_survival_tze_cha_iridescent_horror_metal"] = true,
		["wh3_twa06_nur_inf_plaguebearers_ror_0"] = true,
		["wh3_twa06_ogr_inf_maneaters_ror_0"] = true,
		["wh3_twa06_tze_inf_pink_horrors_ror_0"] = true,
		["wh3_twa10_cth_inf_peasant_archers_ror"] = true,
		["wh3_twa10_ogr_inf_gnoblars_ror"] = true,
		["wh3_twa10_tze_inf_blue_horrors_ror"] = true,
		["wh_dlc03_bst_inf_centigors_1"] = true,
		["wh_dlc03_bst_inf_cygor_0"] = true,
		["wh_dlc03_bst_inf_cygor_0_summoned"] = true,
		["wh_dlc03_bst_inf_ungor_raiders_0"] = true,
		["wh_dlc04_emp_inf_free_company_militia_0"] = true,
		["wh_dlc04_emp_inf_silver_bullets_0"] = true,
		["wh_dlc04_emp_inf_stirlands_revenge_0"] = true,
		["wh_dlc04_emp_veh_templehof_luminark_0"] = true,
		["wh_dlc05_wef_cav_glade_riders_0"] = true,
		["wh_dlc05_wef_cav_glade_riders_1"] = true,
		["wh_dlc05_wef_cav_glade_riders_1_qb"] = true,
		["wh_dlc05_wef_cav_hawk_riders_0"] = true,
		["wh_dlc05_wef_cav_sisters_thorn_0"] = true,
		["wh_dlc05_wef_cha_female_glade_lord_0"] = true,
		["wh_dlc05_wef_cha_female_glade_lord_0_qb"] = true,
		["wh_dlc05_wef_cha_female_glade_lord_1"] = true,
		["wh_dlc05_wef_cha_female_glade_lord_2"] = true,
		["wh_dlc05_wef_cha_female_glade_lord_2_qb"] = true,
		["wh_dlc05_wef_cha_female_glade_lord_3"] = true,
		["wh_dlc05_wef_cha_glade_lord_0"] = true,
		["wh_dlc05_wef_cha_glade_lord_1"] = true,
		["wh_dlc05_wef_cha_glade_lord_2"] = true,
		["wh_dlc05_wef_cha_glade_lord_3"] = true,
		["wh_dlc05_wef_cha_orion_0"] = true,
		["wh_dlc05_wef_cha_waystalker_0"] = true,
		["wh_dlc05_wef_inf_deepwood_scouts_0"] = true,
		["wh_dlc05_wef_inf_deepwood_scouts_1"] = true,
		["wh_dlc05_wef_inf_deepwood_scouts_1_qb"] = true,
		["wh_dlc05_wef_inf_glade_guard_0"] = true,
		["wh_dlc05_wef_inf_glade_guard_1"] = true,
		["wh_dlc05_wef_inf_glade_guard_1_qb"] = true,
		["wh_dlc05_wef_inf_glade_guard_2"] = true,
		["wh_dlc05_wef_inf_waywatchers_0"] = true,
		["wh_dlc06_chs_cav_marauder_horsemasters_0"] = true,
		["wh_dlc06_dwf_cha_master_engineer_ghost_0"] = true,
		["wh_dlc06_dwf_inf_bugmans_rangers_0"] = true,
		["wh_dlc06_dwf_inf_ekrund_miners_0"] = true,
		["wh_dlc06_dwf_inf_norgrimlings_ironbreakers_0"] = true,
		["wh_dlc06_dwf_inf_norgrimlings_irondrakes_0"] = true,
		["wh_dlc06_dwf_inf_rangers_0"] = true,
		["wh_dlc06_dwf_inf_rangers_1"] = true,
		["wh_dlc06_dwf_inf_ulthars_raiders_0"] = true,
		["wh_dlc06_dwf_veh_skyhammer_0"] = true,
		["wh_dlc06_emp_cha_witch_hunter_boss"] = true,
		["wh_dlc06_grn_cav_deff_creepers_0"] = true,
		["wh_dlc06_grn_cav_mogrubbs_marauders_0"] = true,
		["wh_dlc06_grn_cav_teef_robbers_0"] = true,
		["wh_dlc06_grn_inf_da_rusty_arrers_0"] = true,
		["wh_dlc07_brt_inf_peasant_bowmen_1"] = true,
		["wh_dlc07_brt_inf_peasant_bowmen_2"] = true,
		["wh_dlc08_bst_mon_cygor_boss"] = true,
		["wh_dlc08_nor_cav_marauder_horsemasters_0"] = true,
		["wh_dlc08_nor_cav_marauder_warwolves_chariot_0"] = true,
		["wh_dlc08_nor_inf_marauder_hunters_0"] = true,
		["wh_dlc08_nor_inf_marauder_hunters_1"] = true,
		["wh_main_brt_cav_mounted_yeomen_1"] = true,
		["wh_main_brt_inf_peasant_bowmen"] = true,
		["wh_main_chs_cav_marauder_horsemen_0"] = true,
		["wh_main_chs_cav_marauder_horsemen_1"] = true,
		["wh_main_dwf_cha_master_engineer_0"] = true,
		["wh_main_dwf_inf_ironbreakers"] = true,
		["wh_main_dwf_inf_irondrakes_0"] = true,
		["wh_main_dwf_inf_irondrakes_2"] = true,
		["wh_main_dwf_inf_miners_1"] = true,
		["wh_main_dwf_inf_quarrellers_0"] = true,
		["wh_main_dwf_inf_quarrellers_1"] = true,
		["wh_main_dwf_inf_thunderers_0"] = true,
		["wh_main_dwf_veh_gyrobomber"] = true,
		["wh_main_dwf_veh_gyrocopter_0"] = true,
		["wh_main_dwf_veh_gyrocopter_1"] = true,
		["wh_main_emp_cav_outriders_0"] = true,
		["wh_main_emp_cav_outriders_1"] = true,
		["wh_main_emp_cav_pistoliers_1"] = true,
		["wh_main_emp_cha_witch_hunter"] = true,
		["wh_main_emp_inf_crossbowmen"] = true,
		["wh_main_emp_inf_handgunners"] = true,
		["wh_main_emp_veh_luminark_of_hysh_0"] = true,
		["wh_main_emp_veh_steam_tank_driver"] = true,
		["wh_main_grn_cav_forest_goblin_spider_riders_1"] = true,
		["wh_main_grn_cav_goblin_wolf_chariot"] = true,
		["wh_main_grn_cav_goblin_wolf_riders_1"] = true,
		["wh_main_grn_inf_goblin_archers"] = true,
		["wh_main_grn_inf_night_goblin_archers"] = true,
		["wh_main_grn_inf_night_goblin_fanatics_1"] = true,
		["wh_main_grn_inf_orc_arrer_boyz"] = true,
		["wh_main_grn_inf_savage_orc_arrer_boyz"] = true,
		["wh_main_nor_cav_marauder_horsemen_0"] = true,
		["wh_main_nor_cav_marauder_horsemen_1"] = true,
		["wh_pro04_brt_cav_mounted_yeomen_ror_0"] = true,
		["wh_pro04_bst_inf_cygor_ror_0"] = true,
		["wh_pro04_wef_inf_waywatchers_ror_0"] = true,
	},
	overseer = {
		["wh2_dlc09_tmb_art_casket_of_souls_0"] = true,
		["wh2_dlc09_tmb_art_screaming_skull_catapult_0"] = true,
		["wh2_dlc09_tmb_cav_hexwraiths"] = true,
		["wh2_dlc09_tmb_cav_necropolis_knights_0"] = true,
		["wh2_dlc09_tmb_cav_necropolis_knights_1"] = true,
		["wh2_dlc09_tmb_cav_necropolis_knights_ror"] = true,
		["wh2_dlc09_tmb_cav_nehekhara_horsemen_0"] = true,
		["wh2_dlc09_tmb_cav_nehekhara_horsemen_ror"] = true,
		["wh2_dlc09_tmb_cav_skeleton_horsemen_0"] = true,
		["wh2_dlc09_tmb_cav_skeleton_horsemen_0_summoned"] = true,
		["wh2_dlc09_tmb_cav_skeleton_horsemen_archers_0"] = true,
		["wh2_dlc09_tmb_inf_cairn_wraiths"] = true,
		["wh2_dlc09_tmb_inf_crypt_ghouls"] = true,
		["wh2_dlc09_tmb_inf_nehekhara_warriors_0"] = true,
		["wh2_dlc09_tmb_inf_nehekhara_warriors_ror"] = true,
		["wh2_dlc09_tmb_inf_skeleton_archers_0"] = true,
		["wh2_dlc09_tmb_inf_skeleton_archers_ror"] = true,
		["wh2_dlc09_tmb_inf_skeleton_spearmen_0"] = true,
		["wh2_dlc09_tmb_inf_skeleton_spearmen_ror"] = true,
		["wh2_dlc09_tmb_inf_skeleton_warriors_0"] = true,
		["wh2_dlc09_tmb_inf_skeleton_warriors_0_summoned"] = true,
		["wh2_dlc09_tmb_inf_spirit_host"] = true,
		["wh2_dlc09_tmb_inf_tomb_guard_0"] = true,
		["wh2_dlc09_tmb_inf_tomb_guard_1"] = true,
		["wh2_dlc09_tmb_inf_tomb_guard_ror"] = true,
		["wh2_dlc09_tmb_mon_carrion_0"] = true,
		["wh2_dlc09_tmb_mon_dire_wolves"] = true,
		["wh2_dlc09_tmb_mon_fell_bats"] = true,
		["wh2_dlc09_tmb_veh_skeleton_archer_chariot_0"] = true,
		["wh2_dlc09_tmb_veh_skeleton_chariot_0"] = true,
		["wh2_dlc09_tmb_veh_skeleton_chariot_0_summoned"] = true,
		["wh2_dlc10_def_cav_doomfire_warlocks_0"] = true,
		["wh2_dlc10_def_cav_knights_of_the_ebon_claw_ror_0"] = true,
		["wh2_dlc10_def_cav_raven_heralds_ror_0"] = true,
		["wh2_dlc10_def_cav_slaanesh_harvesters_ror_0"] = true,
		["wh2_dlc10_def_inf_blades_of_the_blood_queen_ror_0"] = true,
		["wh2_dlc10_def_inf_sisters_of_slaughter"] = true,
		["wh2_dlc10_def_inf_sisters_of_the_singing_doom_ror_0"] = true,
		["wh2_dlc10_def_inf_the_bolt_fiends_ror_0"] = true,
		["wh2_dlc10_def_inf_the_hellebronai_ror_0"] = true,
		["wh2_dlc10_dwf_inf_giant_slayers"] = true,
		["wh2_dlc10_hef_cav_the_fireborn_ror_0"] = true,
		["wh2_dlc10_hef_cav_the_heralds_of_the_wind_ror_0"] = true,
		["wh2_dlc10_hef_inf_dryads_0"] = true,
		["wh2_dlc10_hef_inf_everqueens_court_guards_ror_0"] = true,
		["wh2_dlc10_hef_inf_keepers_of_the_flame_ror_0"] = true,
		["wh2_dlc10_hef_inf_shadow_walkers_0"] = true,
		["wh2_dlc10_hef_inf_shadow_warriors_0"] = true,
		["wh2_dlc10_hef_inf_sisters_of_avelorn_0"] = true,
		["wh2_dlc10_hef_inf_the_grey_ror_0"] = true,
		["wh2_dlc10_hef_inf_the_scions_of_mathlann_ror_0"] = true,
		["wh2_dlc10_hef_inf_the_silverpelts_ror_0"] = true,
		["wh2_dlc10_hef_inf_the_storm_riders_ror_0"] = true,
		["wh2_dlc11_cst_art_carronade"] = true,
		["wh2_dlc11_cst_art_mortar"] = true,
		["wh2_dlc11_cst_art_queen_bess"] = true,
		["wh2_dlc11_cst_cav_deck_droppers_0"] = true,
		["wh2_dlc11_cst_cav_deck_droppers_1"] = true,
		["wh2_dlc11_cst_cav_deck_droppers_2"] = true,
		["wh2_dlc11_cst_cav_deck_droppers_ror_0"] = true,
		["wh2_dlc11_cst_cav_knights_errant_0"] = true,
		["wh2_dlc11_cst_cav_knights_errant_1"] = true,
		["wh2_dlc11_cst_cav_knights_errant_2"] = true,
		["wh2_dlc11_cst_cav_knights_of_the_realm"] = true,
		["wh2_dlc11_cst_cav_questing_knights_0"] = true,
		["wh2_dlc11_cst_inf_deck_gunners_0"] = true,
		["wh2_dlc11_cst_inf_deck_gunners_0_summoned"] = true,
		["wh2_dlc11_cst_inf_deck_gunners_ror_0"] = true,
		["wh2_dlc11_cst_inf_depth_guard_0"] = true,
		["wh2_dlc11_cst_inf_depth_guard_1"] = true,
		["wh2_dlc11_cst_inf_depth_guard_ror_0"] = true,
		["wh2_dlc11_cst_inf_sartosa_free_company_0"] = true,
		["wh2_dlc11_cst_inf_sartosa_militia_0"] = true,
		["wh2_dlc11_cst_inf_syreens"] = true,
		["wh2_dlc11_cst_inf_zombie_deckhands_mob_0"] = true,
		["wh2_dlc11_cst_inf_zombie_deckhands_mob_1"] = true,
		["wh2_dlc11_cst_inf_zombie_deckhands_mob_necrofex_summoned_0"] = true,
		["wh2_dlc11_cst_inf_zombie_deckhands_mob_ror_0"] = true,
		["wh2_dlc11_cst_inf_zombie_deckhands_mob_summoned_0"] = true,
		["wh2_dlc11_cst_inf_zombie_gunnery_mob_0"] = true,
		["wh2_dlc11_cst_inf_zombie_gunnery_mob_1"] = true,
		["wh2_dlc11_cst_inf_zombie_gunnery_mob_2"] = true,
		["wh2_dlc11_cst_inf_zombie_gunnery_mob_3"] = true,
		["wh2_dlc11_cst_inf_zombie_gunnery_mob_ror_0"] = true,
		["wh2_dlc11_cst_inf_zombie_gunnery_mob_summoned_0"] = true,
		["wh2_dlc11_cst_mon_fell_bats"] = true,
		["wh2_dlc11_cst_mon_scurvy_dogs"] = true,
		["wh2_dlc11_vmp_inf_crossbowmen"] = true,
		["wh2_dlc11_vmp_inf_handgunners"] = true,
		["wh2_dlc12_lzd_cav_cold_one_spearriders_ror_0"] = true,
		["wh2_dlc12_lzd_cav_ripperdactyl_riders_0"] = true,
		["wh2_dlc12_lzd_cav_ripperdactyl_riders_0_blessed"] = true,
		["wh2_dlc12_lzd_cav_ripperdactyl_riders_ror_0"] = true,
		["wh2_dlc12_lzd_cav_terradon_riders_0_tlaqua"] = true,
		["wh2_dlc12_lzd_cav_terradon_riders_1_tlaqua"] = true,
		["wh2_dlc12_lzd_cav_terradon_riders_ror_0"] = true,
		["wh2_dlc12_lzd_inf_saurus_warriors_ror_0"] = true,
		["wh2_dlc12_lzd_inf_skink_red_crested_0"] = true,
		["wh2_dlc12_lzd_inf_skink_red_crested_ror_0"] = true,
		["wh2_dlc12_lzd_inf_temple_guards_ror_0"] = true,
		["wh2_dlc12_lzd_mon_ancient_stegadon_1"] = true,
		["wh2_dlc12_lzd_mon_ancient_stegadon_ror_0"] = true,
		["wh2_dlc12_lzd_mon_salamander_pack_0"] = true,
		["wh2_dlc12_lzd_mon_salamander_pack_0_blessed"] = true,
		["wh2_dlc12_lzd_mon_salamander_pack_ror_0"] = true,
		["wh2_dlc12_skv_art_warp_lightning_cannon_ror_0"] = true,
		["wh2_dlc12_skv_art_warplock_jezzails_ror_tech_lab_0"] = true,
		["wh2_dlc12_skv_inf_clanrats_ror_0"] = true,
		["wh2_dlc12_skv_inf_plague_monk_censer_bearer_ror_0"] = true,
		["wh2_dlc12_skv_inf_ratling_gun_0"] = true,
		["wh2_dlc12_skv_inf_ratling_gun_ror_0"] = true,
		["wh2_dlc12_skv_inf_ratling_gun_ror_tech_lab_0"] = true,
		["wh2_dlc12_skv_inf_stormvermin_ror_0"] = true,
		["wh2_dlc12_skv_inf_warpfire_thrower_ror_tech_lab_0"] = true,
		["wh2_dlc12_skv_inf_warplock_jezzails_0"] = true,
		["wh2_dlc12_skv_inf_warplock_jezzails_ror_0"] = true,
		["wh2_dlc12_skv_veh_doom_flayer_0"] = true,
		["wh2_dlc12_skv_veh_doom_flayer_ror_0"] = true,
		["wh2_dlc12_skv_veh_doom_flayer_ror_tech_lab_0"] = true,
		["wh2_dlc12_skv_veh_doomwheel_ror_0"] = true,
		["wh2_dlc12_skv_veh_doomwheel_ror_tech_lab_0"] = true,
		["wh2_dlc13_emp_art_mortar_ror_0"] = true,
		["wh2_dlc13_emp_cav_empire_knights_ror_0"] = true,
		["wh2_dlc13_emp_cav_empire_knights_ror_1"] = true,
		["wh2_dlc13_emp_cav_empire_knights_ror_2"] = true,
		["wh2_dlc13_emp_cav_outriders_ror_0"] = true,
		["wh2_dlc13_emp_cav_pistoliers_ror_0"] = true,
		["wh2_dlc13_emp_inf_archers_0"] = true,
		["wh2_dlc13_emp_inf_archers_ror_0"] = true,
		["wh2_dlc13_emp_inf_crossbowmen_ror_0"] = true,
		["wh2_dlc13_emp_inf_greatswords_ror_0"] = true,
		["wh2_dlc13_emp_inf_halberdiers_ror_0"] = true,
		["wh2_dlc13_emp_inf_handgunners_ror_0"] = true,
		["wh2_dlc13_emp_inf_huntsmen_0"] = true,
		["wh2_dlc13_emp_inf_huntsmen_ror_0"] = true,
		["wh2_dlc13_emp_inf_spearmen_ror_0"] = true,
		["wh2_dlc13_emp_inf_swordsmen_ror_0"] = true,
		["wh2_dlc13_emp_veh_war_wagon_0"] = true,
		["wh2_dlc13_emp_veh_war_wagon_1"] = true,
		["wh2_dlc13_emp_veh_war_wagon_ror_0"] = true,
		["wh2_dlc13_lzd_mon_dread_saurian_1"] = true,
		["wh2_dlc13_lzd_mon_dread_saurian_ror_0"] = true,
		["wh2_dlc13_lzd_mon_razordon_pack_0"] = true,
		["wh2_dlc13_lzd_mon_razordon_pack_0_blessed"] = true,
		["wh2_dlc13_lzd_mon_razordon_pack_ror_0"] = true,
		["wh2_dlc13_lzd_mon_razordon_pack_summoned_0"] = true,
		["wh2_dlc14_def_cav_scourgerunner_chariot_0"] = true,
		["wh2_dlc14_def_cav_scourgerunner_chariot_ror_0"] = true,
		["wh2_dlc14_def_inf_harpies_ror_0"] = true,
		["wh2_dlc14_skv_inf_death_runners_ror_0"] = true,
		["wh2_dlc14_skv_inf_eshin_triads_0"] = true,
		["wh2_dlc14_skv_inf_eshin_triads_ror_0"] = true,
		["wh2_dlc14_skv_inf_eshin_triads_ror_summoned_0"] = true,
		["wh2_dlc14_skv_inf_poison_wind_mortar_0"] = true,
		["wh2_dlc14_skv_inf_poison_wind_mortar_ror_0"] = true,
		["wh2_dlc14_skv_inf_stormvermin_1_summoned"] = true,
		["wh2_dlc14_skv_inf_warp_grinder_0"] = true,
		["wh2_dlc15_grn_cav_forest_goblin_spider_riders_waaagh_0"] = true,
		["wh2_dlc15_grn_cav_squig_hoppers_waaagh_0"] = true,
		["wh2_dlc15_hef_inf_archers_ror_0"] = true,
		["wh2_dlc15_hef_inf_mistwalkers_faithbearers_0"] = true,
		["wh2_dlc15_hef_inf_mistwalkers_griffon_knights_0"] = true,
		["wh2_dlc15_hef_inf_mistwalkers_sentinels_0"] = true,
		["wh2_dlc15_hef_inf_mistwalkers_skyhawks_0"] = true,
		["wh2_dlc15_hef_inf_mistwalkers_spireguard_0"] = true,
		["wh2_dlc15_hef_inf_rangers_0"] = true,
		["wh2_dlc15_hef_inf_silverin_guard_0"] = true,
		["wh2_dlc15_hef_mon_war_lions_of_chrace_0"] = true,
		["wh2_dlc15_hef_mon_war_lions_of_chrace_ror_0"] = true,
		["wh2_dlc16_skv_mon_wolf_rats_0"] = true,
		["wh2_dlc16_skv_mon_wolf_rats_0_summoned"] = true,
		["wh2_dlc16_skv_mon_wolf_rats_1"] = true,
		["wh2_dlc16_skv_mon_wolf_rats_1_summoned"] = true,
		["wh2_dlc16_wef_cav_glade_riders_2"] = true,
		["wh2_dlc16_wef_cav_great_stag_knights_0"] = true,
		["wh2_dlc16_wef_cav_great_stag_knights_ror_0"] = true,
		["wh2_dlc16_wef_inf_bladesingers_0"] = true,
		["wh2_dlc16_wef_inf_dryads_0_summoned"] = true,
		["wh2_dlc16_wef_inf_dryads_ror_0"] = true,
		["wh2_dlc16_wef_inf_malicious_dryads_0"] = true,
		["wh2_dlc16_wef_mon_cave_bats"] = true,
		["wh2_dlc16_wef_mon_giant_spiders_0"] = true,
		["wh2_dlc16_wef_mon_harpies_0"] = true,
		["wh2_dlc16_wef_mon_hawks_0"] = true,
		["wh2_dlc16_wef_mon_spider_hatchlings_0"] = true,
		["wh2_dlc16_wef_mon_wolves_0"] = true,
		["wh2_dlc17_bst_cav_tuskgor_chariot_0"] = true,
		["wh2_dlc17_bst_inf_centigors_ror_1"] = true,
		["wh2_dlc17_emp_inf_prisoners_0"] = true,
		["wh2_dlc17_lzd_inf_chameleon_stalkers_0"] = true,
		["wh2_dlc17_lzd_inf_chameleon_stalkers_0_blessed"] = true,
		["wh2_main_def_art_reaper_bolt_thrower"] = true,
		["wh2_main_def_cav_cold_one_chariot"] = true,
		["wh2_main_def_cav_cold_one_knights_0"] = true,
		["wh2_main_def_cav_cold_one_knights_1"] = true,
		["wh2_main_def_cav_dark_riders_0"] = true,
		["wh2_main_def_cav_dark_riders_1"] = true,
		["wh2_main_def_cav_dark_riders_2"] = true,
		["wh2_main_def_inf_black_ark_corsairs_0"] = true,
		["wh2_main_def_inf_black_ark_corsairs_1"] = true,
		["wh2_main_def_inf_black_guard_0"] = true,
		["wh2_main_def_inf_bleakswords_0"] = true,
		["wh2_main_def_inf_darkshards_0"] = true,
		["wh2_main_def_inf_darkshards_1"] = true,
		["wh2_main_def_inf_dreadspears_0"] = true,
		["wh2_main_def_inf_har_ganeth_executioners_0"] = true,
		["wh2_main_def_inf_harpies"] = true,
		["wh2_main_def_inf_shades_0"] = true,
		["wh2_main_def_inf_shades_1"] = true,
		["wh2_main_def_inf_shades_2"] = true,
		["wh2_main_def_inf_witch_elves_0"] = true,
		["wh2_main_hef_art_eagle_claw_bolt_thrower"] = true,
		["wh2_main_hef_cav_dragon_princes"] = true,
		["wh2_main_hef_cav_ellyrian_reavers_0"] = true,
		["wh2_main_hef_cav_ellyrian_reavers_1"] = true,
		["wh2_main_hef_cav_ithilmar_chariot"] = true,
		["wh2_main_hef_cav_silver_helms_0"] = true,
		["wh2_main_hef_cav_silver_helms_1"] = true,
		["wh2_main_hef_cav_tiranoc_chariot"] = true,
		["wh2_main_hef_inf_archers_0"] = true,
		["wh2_main_hef_inf_archers_1"] = true,
		["wh2_main_hef_inf_gate_guard"] = true,
		["wh2_main_hef_inf_lothern_sea_guard_0"] = true,
		["wh2_main_hef_inf_lothern_sea_guard_1"] = true,
		["wh2_main_hef_inf_phoenix_guard"] = true,
		["wh2_main_hef_inf_spearmen_0"] = true,
		["wh2_main_hef_inf_swordmasters_of_hoeth_0"] = true,
		["wh2_main_hef_inf_white_lions_of_chrace_0"] = true,
		["wh2_main_lzd_cav_cold_one_spearriders_1"] = true,
		["wh2_main_lzd_cav_cold_one_spearriders_blessed_0"] = true,
		["wh2_main_lzd_cav_cold_ones_1"] = true,
		["wh2_main_lzd_cav_cold_ones_feral_0"] = true,
		["wh2_main_lzd_cav_cold_ones_feral_0_summoned"] = true,
		["wh2_main_lzd_cav_horned_ones_0"] = true,
		["wh2_main_lzd_cav_horned_ones_blessed_0"] = true,
		["wh2_main_lzd_cav_terradon_riders_0"] = true,
		["wh2_main_lzd_cav_terradon_riders_0_blessed"] = true,
		["wh2_main_lzd_cav_terradon_riders_1"] = true,
		["wh2_main_lzd_cav_terradon_riders_blessed_1"] = true,
		["wh2_main_lzd_inf_chameleon_skinks_0"] = true,
		["wh2_main_lzd_inf_chameleon_skinks_blessed_0"] = true,
		["wh2_main_lzd_inf_saurus_spearmen_0"] = true,
		["wh2_main_lzd_inf_saurus_spearmen_1"] = true,
		["wh2_main_lzd_inf_saurus_spearmen_blessed_1"] = true,
		["wh2_main_lzd_inf_saurus_warriors_0"] = true,
		["wh2_main_lzd_inf_saurus_warriors_1"] = true,
		["wh2_main_lzd_inf_saurus_warriors_blessed_1"] = true,
		["wh2_main_lzd_inf_skink_cohort_0"] = true,
		["wh2_main_lzd_inf_skink_cohort_1"] = true,
		["wh2_main_lzd_inf_skink_cohort_1_blessed"] = true,
		["wh2_main_lzd_inf_skink_skirmishers_0"] = true,
		["wh2_main_lzd_inf_skink_skirmishers_blessed_0"] = true,
		["wh2_main_lzd_inf_temple_guards"] = true,
		["wh2_main_lzd_inf_temple_guards_blessed"] = true,
		["wh2_main_lzd_mon_ancient_stegadon"] = true,
		["wh2_main_lzd_mon_ancient_stegadon_blessed"] = true,
		["wh2_main_lzd_mon_stegadon_1"] = true,
		["wh2_main_lzd_mon_stegadon_blessed_1"] = true,
		["wh2_main_skv_art_plagueclaw_catapult"] = true,
		["wh2_main_skv_art_warp_lightning_cannon"] = true,
		["wh2_main_skv_inf_clanrat_spearmen_0"] = true,
		["wh2_main_skv_inf_clanrat_spearmen_1"] = true,
		["wh2_main_skv_inf_clanrats_0"] = true,
		["wh2_main_skv_inf_clanrats_0_summoned"] = true,
		["wh2_main_skv_inf_clanrats_0_summoned_small"] = true,
		["wh2_main_skv_inf_clanrats_1"] = true,
		["wh2_main_skv_inf_death_globe_bombardiers"] = true,
		["wh2_main_skv_inf_death_runners_0"] = true,
		["wh2_main_skv_inf_death_runners_0_summoned"] = true,
		["wh2_main_skv_inf_gutter_runner_slingers_0"] = true,
		["wh2_main_skv_inf_gutter_runner_slingers_1"] = true,
		["wh2_main_skv_inf_gutter_runners_0"] = true,
		["wh2_main_skv_inf_gutter_runners_1"] = true,
		["wh2_main_skv_inf_night_runners_0"] = true,
		["wh2_main_skv_inf_night_runners_1"] = true,
		["wh2_main_skv_inf_plague_monk_censer_bearer"] = true,
		["wh2_main_skv_inf_plague_monks"] = true,
		["wh2_main_skv_inf_plague_monks_summoned"] = true,
		["wh2_main_skv_inf_poison_wind_globadiers"] = true,
		["wh2_main_skv_inf_skavenslave_slingers_0"] = true,
		["wh2_main_skv_inf_skavenslave_spearmen_0"] = true,
		["wh2_main_skv_inf_skavenslave_spearmen_0_summoned"] = true,
		["wh2_main_skv_inf_skavenslaves_0"] = true,
		["wh2_main_skv_inf_stormvermin_0"] = true,
		["wh2_main_skv_inf_stormvermin_0_quest"] = true,
		["wh2_main_skv_inf_stormvermin_0_summoned"] = true,
		["wh2_main_skv_inf_stormvermin_1"] = true,
		["wh2_main_skv_inf_warpfire_thrower"] = true,
		["wh2_main_skv_veh_doomwheel"] = true,
		["wh2_twa03_def_mon_wolves_0"] = true,
		["wh3_cp1_cth_inf_iron_claw_guandao"] = true,
		["wh3_cp1_cth_inf_iron_claw_guandao_summoned"] = true,
		["wh3_cp1_cth_inf_stalkers_throwing_disc"] = true,
		["wh3_cp1_cth_inf_tiger_warriors_dual_axe"] = true,
		["wh3_dlc20_chs_cav_chaos_chariot_mkho"] = true,
		["wh3_dlc20_chs_cav_chaos_chariot_mnur"] = true,
		["wh3_dlc20_chs_cav_chaos_chariot_msla"] = true,
		["wh3_dlc20_chs_cav_chaos_chariot_msla_ror"] = true,
		["wh3_dlc20_chs_cav_chaos_chariot_mtze"] = true,
		["wh3_dlc20_chs_cav_chaos_knights_mkho"] = true,
		["wh3_dlc20_chs_cav_chaos_knights_mkho_lances"] = true,
		["wh3_dlc20_chs_cav_chaos_knights_mnur"] = true,
		["wh3_dlc20_chs_cav_chaos_knights_mnur_lances"] = true,
		["wh3_dlc20_chs_cav_chaos_knights_msla"] = true,
		["wh3_dlc20_chs_cav_chaos_knights_msla_lances"] = true,
		["wh3_dlc20_chs_cav_chaos_knights_mtze_lances"] = true,
		["wh3_dlc20_chs_cav_marauder_horsemen_mkho_throwing_axes"] = true,
		["wh3_dlc20_chs_cav_marauder_horsemen_mnur_throwing_axes"] = true,
		["wh3_dlc20_chs_cav_marauder_horsemen_msla_javelins"] = true,
		["wh3_dlc20_chs_cav_marauder_horsemen_mtze_javelins"] = true,
		["wh3_dlc20_chs_inf_aspiring_champions_mtze_ror"] = true,
		["wh3_dlc20_chs_inf_chaos_marauders_mkho"] = true,
		["wh3_dlc20_chs_inf_chaos_marauders_mkho_dualweapons"] = true,
		["wh3_dlc20_chs_inf_chaos_marauders_mnur"] = true,
		["wh3_dlc20_chs_inf_chaos_marauders_mnur_greatweapons"] = true,
		["wh3_dlc20_chs_inf_chaos_marauders_msla"] = true,
		["wh3_dlc20_chs_inf_chaos_marauders_msla_hellscourges"] = true,
		["wh3_dlc20_chs_inf_chaos_marauders_mtze"] = true,
		["wh3_dlc20_chs_inf_chaos_marauders_mtze_spears"] = true,
		["wh3_dlc20_chs_inf_chaos_warriors_mnur"] = true,
		["wh3_dlc20_chs_inf_chaos_warriors_mnur_greatweapons"] = true,
		["wh3_dlc20_chs_inf_chaos_warriors_msla"] = true,
		["wh3_dlc20_chs_inf_chaos_warriors_msla_hellscourges"] = true,
		["wh3_dlc20_chs_inf_chaos_warriors_mtze"] = true,
		["wh3_dlc20_chs_inf_chaos_warriors_mtze_halberds"] = true,
		["wh3_dlc20_chs_inf_chosen_mkho"] = true,
		["wh3_dlc20_chs_inf_chosen_mkho_dualweapons"] = true,
		["wh3_dlc20_chs_inf_chosen_mnur"] = true,
		["wh3_dlc20_chs_inf_chosen_mnur_greatweapons"] = true,
		["wh3_dlc20_chs_inf_chosen_msla"] = true,
		["wh3_dlc20_chs_inf_chosen_msla_hellscourges"] = true,
		["wh3_dlc20_chs_inf_chosen_mtze"] = true,
		["wh3_dlc20_chs_inf_chosen_mtze_halberds"] = true,
		["wh3_dlc20_chs_inf_forsaken_mkho"] = true,
		["wh3_dlc20_chs_inf_forsaken_msla"] = true,
		["wh3_dlc20_chs_mon_warshrine"] = true,
		["wh3_dlc20_chs_mon_warshrine_mkho"] = true,
		["wh3_dlc20_chs_mon_warshrine_mnur"] = true,
		["wh3_dlc20_chs_mon_warshrine_msla"] = true,
		["wh3_dlc20_chs_mon_warshrine_mtze"] = true,
		["wh3_dlc20_kho_cav_skullcrushers_mkho_ror"] = true,
		["wh3_dlc23_chd_cav_hobgoblin_wolf_raiders_bows"] = true,
		["wh3_dlc23_chd_cav_hobgoblin_wolf_raiders_ror"] = true,
		["wh3_dlc23_chd_cav_hobgoblin_wolf_raiders_spears"] = true,
		["wh3_dlc23_chd_inf_chaos_dwarf_blunderbusses"] = true,
		["wh3_dlc23_chd_inf_chaos_dwarf_blunderbusses_ror"] = true,
		["wh3_dlc23_chd_inf_chaos_dwarf_warriors"] = true,
		["wh3_dlc23_chd_inf_chaos_dwarf_warriors_great_weapons"] = true,
		["wh3_dlc23_chd_inf_chaos_dwarf_warriors_ror"] = true,
		["wh3_dlc23_chd_inf_goblin_labourers"] = true,
		["wh3_dlc23_chd_inf_hobgoblin_archers"] = true,
		["wh3_dlc23_chd_inf_hobgoblin_cutthroats"] = true,
		["wh3_dlc23_chd_inf_hobgoblin_cutthroats_summoned"] = true,
		["wh3_dlc23_chd_inf_hobgoblin_sneaky_gits"] = true,
		["wh3_dlc23_chd_inf_infernal_guard"] = true,
		["wh3_dlc23_chd_inf_infernal_guard_fireglaives"] = true,
		["wh3_dlc23_chd_inf_infernal_guard_great_weapons"] = true,
		["wh3_dlc23_chd_inf_infernal_ironsworn"] = true,
		["wh3_dlc23_chd_inf_infernal_ironsworn_ror"] = true,
		["wh3_dlc23_chd_inf_orc_labourers"] = true,
		["wh3_dlc23_chd_veh_deathshrieker_rocket_launcher"] = true,
		["wh3_dlc23_chd_veh_dreadquake_mortar"] = true,
		["wh3_dlc23_chd_veh_iron_daemon"] = true,
		["wh3_dlc23_chd_veh_iron_daemon_1dreadquake"] = true,
		["wh3_dlc23_chd_veh_iron_daemon_3payload_qb"] = true,
		["wh3_dlc23_chd_veh_iron_daemon_ror"] = true,
		["wh3_dlc23_chd_veh_iron_daemon_ror_1dreadquake"] = true,
		["wh3_dlc23_chd_veh_magma_cannon"] = true,
		["wh3_dlc23_chd_veh_skullcracker"] = true,
		["wh3_dlc23_chd_veh_skullcracker_1dreadquake"] = true,
		["wh3_dlc24_cth_inf_dragon_guard_crossbowmen_ror"] = true,
		["wh3_dlc24_cth_inf_onyx_crowmen"] = true,
		["wh3_dlc24_cth_inf_onyx_crowmen_ror"] = true,
		["wh3_dlc24_cth_veh_zhangu_war_drum"] = true,
		["wh3_dlc24_cth_veh_zhangu_war_drum_ror"] = true,
		["wh3_dlc24_ksl_inf_akshina_ambushers"] = true,
		["wh3_dlc24_ksl_inf_akshina_ambushers_ror"] = true,
		["wh3_dlc24_ksl_inf_kislevite_warriors"] = true,
		["wh3_dlc24_ksl_inf_streltsi_ror"] = true,
		["wh3_dlc24_ksl_mon_the_things_in_the_woods"] = true,
		["wh3_dlc24_ksl_mon_the_things_in_the_woods_ror"] = true,
		["wh3_dlc24_ksl_mon_the_things_in_the_woods_summoned"] = true,
		["wh3_dlc24_qb_cst_cav_knights_errant_0"] = true,
		["wh3_dlc24_qb_cst_cav_knights_of_the_realm"] = true,
		["wh3_dlc24_qb_cst_cav_questing_knights_0"] = true,
		["wh3_dlc24_tze_inf_centigors_great_weapons"] = true,
		["wh3_dlc24_tze_inf_pink_horrors_ror"] = true,
		["wh3_dlc24_tze_inf_tzaangors"] = true,
		["wh3_dlc24_tze_mon_screamers_ror"] = true,
		["wh3_dlc25_dwf_art_flame_cannon_grudge_unit"] = true,
		["wh3_dlc25_dwf_art_goblin_hewer"] = true,
		["wh3_dlc25_dwf_art_grudge_thrower_grudge_unit"] = true,
		["wh3_dlc25_dwf_inf_doomseekers"] = true,
		["wh3_dlc25_dwf_inf_doomseekers_ror"] = true,
		["wh3_dlc25_dwf_inf_hammerers_grudge_unit"] = true,
		["wh3_dlc25_dwf_inf_irondrakes_0_grudge_unit"] = true,
		["wh3_dlc25_dwf_inf_longbeards_1_grudge_unit"] = true,
		["wh3_dlc25_dwf_inf_miners_1_summoned"] = true,
		["wh3_dlc25_dwf_inf_quarrellers_1_grudge_unit"] = true,
		["wh3_dlc25_dwf_inf_slayer_pirates"] = true,
		["wh3_dlc25_dwf_inf_slayer_pirates_ror"] = true,
		["wh3_dlc25_dwf_inf_slayers_grudge_unit"] = true,
		["wh3_dlc25_dwf_inf_thunderers_grudge_rakers"] = true,
		["wh3_dlc25_dwf_inf_thunderers_ror"] = true,
		["wh3_dlc25_emp_art_helstorm_rocket_battery_morr"] = true,
		["wh3_dlc25_emp_cav_knights_of_the_black_rose"] = true,
		["wh3_dlc25_emp_cav_outriders_morr"] = true,
		["wh3_dlc25_emp_inf_hochland_long_rifles"] = true,
		["wh3_dlc25_emp_inf_hochland_long_rifles_ror"] = true,
		["wh3_dlc25_emp_inf_nuln_ironsides"] = true,
		["wh3_dlc25_emp_inf_nuln_ironsides_morr"] = true,
		["wh3_dlc25_emp_inf_spearmen_shields_ror"] = true,
		["wh3_dlc25_emp_mon_hawks_summoned"] = true,
		["wh3_dlc25_emp_veh_marienburg_land_ship"] = true,
		["wh3_dlc25_emp_veh_marienburg_land_ship_morr"] = true,
		["wh3_dlc25_emp_veh_marienburg_land_ship_ror"] = true,
		["wh3_dlc25_nur_cav_plague_drones_1_ror"] = true,
		["wh3_dlc25_nur_cav_rot_knights"] = true,
		["wh3_dlc25_nur_cav_rot_knights_ror"] = true,
		["wh3_dlc25_nur_inf_nurglings_summoned"] = true,
		["wh3_dlc25_nur_inf_pestigors"] = true,
		["wh3_dlc26_chs_inf_chosen_mkho_ror"] = true,
		["wh3_dlc26_grn_art_bolt_throwa"] = true,
		["wh3_dlc26_grn_art_bolt_throwa_ror"] = true,
		["wh3_dlc26_grn_inf_black_orcs_shield"] = true,
		["wh3_dlc26_grn_inf_rugluds_armoured_orcs"] = true,
		["wh3_dlc26_grn_inf_squig_herd_0_summoned"] = true,
		["wh3_dlc26_kho_inf_khorngors"] = true,
		["wh3_dlc26_kho_inf_skullreapers"] = true,
		["wh3_dlc26_kho_inf_wrathmongers"] = true,
		["wh3_dlc26_kho_inf_wrathmongers_ror"] = true,
		["wh3_dlc26_kho_veh_skullcannon_ror"] = true,
		["wh3_dlc26_ogr_inf_pigback_riders"] = true,
		["wh3_dlc26_ogr_inf_pigback_riders_ror"] = true,
		["wh3_dlc26_ogr_mon_blood_vultures"] = true,
		["wh3_dlc26_ogr_mon_sabretusk_pack_0_summoned"] = true,
		["wh3_dlc27_hef_inf_militia_qb"] = true,
		["wh3_dlc27_hef_inf_ships_company"] = true,
		["wh3_dlc27_hef_inf_ships_company_ror"] = true,
		["wh3_dlc27_hef_inf_swordmasters_of_hoeth_ror"] = true,
		["wh3_dlc27_hef_veh_skycutter_bolt_thrower"] = true,
		["wh3_dlc27_hef_veh_skycutter_bows"] = true,
		["wh3_dlc27_hef_veh_skycutter_ror"] = true,
		["wh3_dlc27_nor_cav_chaos_chariot_ror"] = true,
		["wh3_dlc27_nor_cav_kurgan_horsemen_dualweapons"] = true,
		["wh3_dlc27_nor_cav_kurgan_horsemen_greatweapons"] = true,
		["wh3_dlc27_nor_cav_marauder_horsemen_ror"] = true,
		["wh3_dlc27_nor_inf_chaos_marauders_great_weapons_ror"] = true,
		["wh3_dlc27_nor_inf_marauder_bearmen"] = true,
		["wh3_dlc27_nor_inf_marauder_bearmen_greatweapons"] = true,
		["wh3_dlc27_sla_cav_pleasureseekers"] = true,
		["wh3_dlc27_sla_inf_chaos_furies_summoned"] = true,
		["wh3_dlc27_sla_inf_devotees_of_slaanesh"] = true,
		["wh3_dlc27_sla_inf_devotees_of_slaanesh_crossbows"] = true,
		["wh3_dlc27_sla_inf_slaangors"] = true,
		["wh3_dlc27_sla_inf_vengeful_furies_summoned"] = true,
		["wh3_dlc27_sla_veh_seeker_chariot_ror"] = true,
		["wh3_dlc29_chs_cav_nur_plague_drones_1_summoned"] = true,
		["wh3_dlc29_chs_cav_nur_plague_drones_summoned"] = true,
		["wh3_dlc29_chs_inf_chaos_warriors_mnur_summoned_small"] = true,
		["wh3_dlc29_chs_inf_chosen_mnur_ror"] = true,
		["wh3_dlc29_chs_inf_flayerkin"] = true,
		["wh3_dlc29_chs_inf_putrid_blightkings_axe_shield"] = true,
		["wh3_dlc29_chs_inf_putrid_blightkings_dual_axe"] = true,
		["wh3_dlc29_chs_inf_putrid_blightkings_dual_axe_ror"] = true,
		["wh3_dlc29_chs_inf_putrid_blightkings_great_weapons"] = true,
		["wh3_dlc29_cst_inf_zombie_pirate_gunnery_mob_bombers_summoned"] = true,
		["wh3_dlc29_emp_cav_knights_of_the_white_wolf"] = true,
		["wh3_dlc29_emp_cav_knights_of_the_white_wolf_ror"] = true,
		["wh3_dlc29_emp_cav_knights_panther"] = true,
		["wh3_dlc29_emp_inf_hunting_hounds"] = true,
		["wh3_dlc29_emp_inf_hunting_hounds_ror"] = true,
		["wh3_dlc29_emp_inf_teutogen_guard"] = true,
		["wh3_dlc29_emp_inf_teutogen_guard_ror"] = true,
		["wh3_dlc29_emp_inf_warriors_of_ulric"] = true,
		["wh3_dlc29_emp_inf_wolf_kin"] = true,
		["wh3_dlc29_emp_veh_celestial_hurricanum_0"] = true,
		["wh3_dlc29_skv_art_plagueclaw_catapult_ror"] = true,
		["wh3_dlc29_skv_art_warp_doom_magma_cannon"] = true,
		["wh3_dlc29_skv_inf_clanrat_spearmen_vermintide"] = true,
		["wh3_dlc29_skv_inf_clanrats_vermintide"] = true,
		["wh3_dlc29_skv_inf_deathvermin_ror"] = true,
		["wh3_dlc29_skv_inf_poison_wind_mortar_0_summoned"] = true,
		["wh3_dlc29_skv_inf_pusbags"] = true,
		["wh3_dlc29_skv_inf_skavenslave_slingers_vermintide"] = true,
		["wh3_dlc29_skv_inf_skavenslave_spearmen_vermintide"] = true,
		["wh3_dlc29_skv_inf_skavenslaves_vermintide"] = true,
		["wh3_dlc29_skv_veh_cauldron_of_a_thousand_poxes"] = true,
		["wh3_dlc29_skv_veh_doom_flayer_0_summoned"] = true,
		["wh3_dlc29_tmb_inf_nehekhara_warriors_0_summoned"] = true,
		["wh3_dlc29_tmb_veh_skeleton_archer_chariot_0_summoned"] = true,
		["wh3_dlc29_vmp_cav_drakenhof_templars"] = true,
		["wh3_dlc29_vmp_inf_grave_guard_0_the_awakening"] = true,
		["wh3_dlc29_vmp_inf_grave_guard_1_the_awakening"] = true,
		["wh3_dlc29_vmp_inf_grave_guard_2_the_awakening"] = true,
		["wh3_dlc29_vmp_inf_lahmian_handmaidens_death"] = true,
		["wh3_dlc29_vmp_inf_lahmian_handmaidens_shadow"] = true,
		["wh3_dlc29_vmp_inf_skeleton_warriors_0_raise_legion"] = true,
		["wh3_dlc29_vmp_inf_skeleton_warriors_0_raise_legion_upgraded"] = true,
		["wh3_dlc29_vmp_inf_skeleton_warriors_0_the_awakening"] = true,
		["wh3_dlc29_vmp_inf_spirit_host"] = true,
		["wh3_dlc29_vmp_inf_spirit_host_summoned"] = true,
		["wh3_dlc29_vmp_inf_zombies_raise_legion"] = true,
		["wh3_dlc29_vmp_veh_coven_throne"] = true,
		["wh3_main_chd_art_hobgob_bolt_thrower"] = true,
		["wh3_main_chs_art_hellcannon_prologue"] = true,
		["wh3_main_cth_art_fire_rain_rocket_battery_0"] = true,
		["wh3_main_cth_art_grand_cannon_0"] = true,
		["wh3_main_cth_cav_jade_lancers_0"] = true,
		["wh3_main_cth_cav_jade_longma_riders_0"] = true,
		["wh3_main_cth_cav_peasant_horsemen_0"] = true,
		["wh3_main_cth_inf_ancestral_warriors_summoned_0"] = true,
		["wh3_main_cth_inf_crane_gunners_0"] = true,
		["wh3_main_cth_inf_dragon_guard_0"] = true,
		["wh3_main_cth_inf_dragon_guard_crossbowmen_0"] = true,
		["wh3_main_cth_inf_grenadiers"] = true,
		["wh3_main_cth_inf_iron_hail_gunners_0"] = true,
		["wh3_main_cth_inf_jade_warrior_crossbowmen_0"] = true,
		["wh3_main_cth_inf_jade_warrior_crossbowmen_1"] = true,
		["wh3_main_cth_inf_jade_warriors_0"] = true,
		["wh3_main_cth_inf_jade_warriors_1"] = true,
		["wh3_main_cth_inf_peasant_archers_0"] = true,
		["wh3_main_cth_inf_peasant_spearmen_1"] = true,
		["wh3_main_cth_veh_sky_junk_0"] = true,
		["wh3_main_cth_veh_sky_lantern_0"] = true,
		["wh3_main_cth_veh_war_compass_0"] = true,
		["wh3_main_dae_inf_chaos_furies_0"] = true,
		["wh3_main_dae_inf_chaos_furies_summoned_0"] = true,
		["wh3_main_grn_inf_goblins_sword_shield"] = true,
		["wh3_main_grn_inf_orc_boyz_spear_shield"] = true,
		["wh3_main_kho_cav_bloodcrushers_0"] = true,
		["wh3_main_kho_cav_gorebeast_chariot"] = true,
		["wh3_main_kho_cav_skullcrushers_0"] = true,
		["wh3_main_kho_inf_bloodletters_0"] = true,
		["wh3_main_kho_inf_bloodletters_1"] = true,
		["wh3_main_kho_inf_bloodletters_summoned_0"] = true,
		["wh3_main_kho_inf_chaos_furies_0"] = true,
		["wh3_main_kho_inf_chaos_warhounds_0"] = true,
		["wh3_main_kho_inf_chaos_warriors_0"] = true,
		["wh3_main_kho_inf_chaos_warriors_1"] = true,
		["wh3_main_kho_inf_chaos_warriors_2"] = true,
		["wh3_main_kho_inf_flesh_hounds_of_khorne_0"] = true,
		["wh3_main_kho_veh_blood_shrine_0"] = true,
		["wh3_main_kho_veh_skullcannon_0"] = true,
		["wh3_main_ksl_cav_gryphon_legion_0"] = true,
		["wh3_main_ksl_cav_horse_archers_0"] = true,
		["wh3_main_ksl_cav_kossovite_dervishes_0"] = true,
		["wh3_main_ksl_cav_war_bear_riders_1"] = true,
		["wh3_main_ksl_cav_winged_lancers_0"] = true,
		["wh3_main_ksl_inf_armoured_kossars_0"] = true,
		["wh3_main_ksl_inf_armoured_kossars_1"] = true,
		["wh3_main_ksl_inf_ice_guard_0"] = true,
		["wh3_main_ksl_inf_ice_guard_1"] = true,
		["wh3_main_ksl_inf_kossars_0"] = true,
		["wh3_main_ksl_inf_kossars_1"] = true,
		["wh3_main_ksl_inf_kossars_tutorial_0"] = true,
		["wh3_main_ksl_inf_kossars_tutorial_1"] = true,
		["wh3_main_ksl_inf_streltsi_0"] = true,
		["wh3_main_ksl_inf_tzar_guard_0"] = true,
		["wh3_main_ksl_inf_tzar_guard_1"] = true,
		["wh3_main_ksl_mon_snow_leopard_0"] = true,
		["wh3_main_ksl_mon_snow_leopard_summoned_0"] = true,
		["wh3_main_ksl_mon_snow_leopard_summoned_1"] = true,
		["wh3_main_ksl_mon_snow_leopard_summoned_2"] = true,
		["wh3_main_ksl_veh_heavy_war_sled_0"] = true,
		["wh3_main_ksl_veh_light_war_sled_0"] = true,
		["wh3_main_ksl_veh_little_grom_0"] = true,
		["wh3_main_monster_feral_bears"] = true,
		["wh3_main_monster_feral_ice_bears"] = true,
		["wh3_main_nur_cav_plague_drones_0"] = true,
		["wh3_main_nur_cav_plague_drones_1"] = true,
		["wh3_main_nur_cav_pox_riders_of_nurgle_0"] = true,
		["wh3_main_nur_inf_chaos_furies_0"] = true,
		["wh3_main_nur_inf_forsaken_0"] = true,
		["wh3_main_nur_inf_nurglings_0"] = true,
		["wh3_main_nur_inf_nurglings_summoned_0"] = true,
		["wh3_main_nur_inf_plaguebearers_0"] = true,
		["wh3_main_nur_inf_plaguebearers_1"] = true,
		["wh3_main_nur_inf_plaguebearers_1_summoned"] = true,
		["wh3_main_nur_inf_plaguebearers_summoned_0"] = true,
		["wh3_main_nur_mon_plague_toads_0"] = true,
		["wh3_main_nur_mon_rot_flies_0"] = true,
		["wh3_main_ogr_inf_gnoblars_0"] = true,
		["wh3_main_ogr_inf_gnoblars_1"] = true,
		["wh3_main_ogr_inf_gnoblars_flingers"] = true,
		["wh3_main_ogr_mon_sabretusk_pack_0"] = true,
		["wh3_main_ogr_veh_gnoblar_scraplauncher_0"] = true,
		["wh3_main_ogr_veh_ironblaster_0"] = true,
		["wh3_main_pro_kho_inf_bloodletters_0"] = true,
		["wh3_main_pro_kho_inf_chaos_furies_0"] = true,
		["wh3_main_pro_kho_inf_chaos_warhounds_0"] = true,
		["wh3_main_pro_kho_inf_chaos_warriors_0"] = true,
		["wh3_main_pro_kho_inf_flesh_hounds_of_khorne_0"] = true,
		["wh3_main_pro_ksl_cav_kossovite_dervishes_0"] = true,
		["wh3_main_pro_ksl_cav_war_bear_riders_1"] = true,
		["wh3_main_pro_ksl_cav_winged_lancers_0"] = true,
		["wh3_main_pro_ksl_inf_armoured_kossars_0"] = true,
		["wh3_main_pro_ksl_inf_armoured_kossars_1"] = true,
		["wh3_main_pro_ksl_inf_kossars_0"] = true,
		["wh3_main_pro_ksl_inf_kossars_1"] = true,
		["wh3_main_pro_ksl_inf_streltsi_0"] = true,
		["wh3_main_pro_ksl_inf_tzar_guard_0"] = true,
		["wh3_main_pro_ksl_veh_little_grom_0"] = true,
		["wh3_main_pro_tze_cav_chaos_knights_0"] = true,
		["wh3_main_pro_tze_inf_blue_horrors_0"] = true,
		["wh3_main_pro_tze_inf_pink_horrors_0"] = true,
		["wh3_main_pro_tze_mon_screamers_0"] = true,
		["wh3_main_sla_cav_heartseekers_of_slaanesh_0"] = true,
		["wh3_main_sla_cav_hellstriders_0"] = true,
		["wh3_main_sla_cav_hellstriders_1"] = true,
		["wh3_main_sla_cav_seekers_of_slaanesh_0"] = true,
		["wh3_main_sla_inf_chaos_furies_0"] = true,
		["wh3_main_sla_inf_daemonette_0"] = true,
		["wh3_main_sla_inf_daemonette_1"] = true,
		["wh3_main_sla_inf_daemonette_summoned_0"] = true,
		["wh3_main_sla_inf_marauders_0"] = true,
		["wh3_main_sla_inf_marauders_1"] = true,
		["wh3_main_sla_inf_marauders_2"] = true,
		["wh3_main_sla_veh_exalted_seeker_chariot_0"] = true,
		["wh3_main_sla_veh_hellflayer_0"] = true,
		["wh3_main_sla_veh_seeker_chariot_0"] = true,
		["wh3_main_tze_cav_chaos_knights_0"] = true,
		["wh3_main_tze_cav_doom_knights_0"] = true,
		["wh3_main_tze_inf_blue_horrors_0"] = true,
		["wh3_main_tze_inf_blue_horrors_summoned_0"] = true,
		["wh3_main_tze_inf_chaos_furies_0"] = true,
		["wh3_main_tze_inf_forsaken_0"] = true,
		["wh3_main_tze_inf_pink_horrors_0"] = true,
		["wh3_main_tze_inf_pink_horrors_1"] = true,
		["wh3_main_tze_inf_pink_horrors_summoned_0"] = true,
		["wh3_main_tze_mon_screamers_0"] = true,
		["wh3_main_vmp_blood_knights_sword_shield"] = true,
		["wh3_main_vmp_inf_grave_guard_2"] = true,
		["wh3_pro12_kho_inf_flesh_hounds_of_khorne_summoned"] = true,
		["wh3_twa06_cth_inf_dragon_guard_ror_0"] = true,
		["wh3_twa06_kho_inf_bloodletters_ror_0"] = true,
		["wh3_twa06_ksl_inf_tzar_guard_ror_0"] = true,
		["wh3_twa06_nur_inf_plaguebearers_ror_0"] = true,
		["wh3_twa06_sla_inf_daemonette_ror_0"] = true,
		["wh3_twa06_tze_inf_pink_horrors_ror_0"] = true,
		["wh3_twa07_cth_cav_jade_longma_riders_ror_0"] = true,
		["wh3_twa07_kho_cav_bloodcrushers_ror_0"] = true,
		["wh3_twa07_ksl_cav_war_bear_riders_ror_0"] = true,
		["wh3_twa07_nur_cav_pox_riders_of_nurgle_ror_0"] = true,
		["wh3_twa07_sla_cav_heartseekers_of_slaanesh_ror_0"] = true,
		["wh3_twa07_tze_cav_doom_knights_ror_0"] = true,
		["wh3_twa10_cth_inf_peasant_archers_ror"] = true,
		["wh3_twa10_kho_inf_flesh_hounds_of_khorne_ror"] = true,
		["wh3_twa10_ksl_inf_armoured_kossars_ror"] = true,
		["wh3_twa10_nur_inf_nurglings_ror"] = true,
		["wh3_twa10_ogr_inf_gnoblars_ror"] = true,
		["wh3_twa10_sla_inf_marauders_spears_ror"] = true,
		["wh3_twa10_tze_inf_blue_horrors_ror"] = true,
		["wh_dlc01_chs_cav_gorebeast_chariot"] = true,
		["wh_dlc01_chs_inf_chaos_warriors_2"] = true,
		["wh_dlc01_chs_inf_chosen_2"] = true,
		["wh_dlc01_chs_inf_forsaken_0"] = true,
		["wh_dlc02_vmp_cav_blood_knights_0"] = true,
		["wh_dlc03_bst_cav_razorgor_chariot_0"] = true,
		["wh_dlc03_bst_inf_bestigor_herd_0"] = true,
		["wh_dlc03_bst_inf_centigors_0"] = true,
		["wh_dlc03_bst_inf_centigors_1"] = true,
		["wh_dlc03_bst_inf_centigors_2"] = true,
		["wh_dlc03_bst_inf_chaos_warhounds_0"] = true,
		["wh_dlc03_bst_inf_chaos_warhounds_1"] = true,
		["wh_dlc03_bst_inf_gor_herd_0"] = true,
		["wh_dlc03_bst_inf_gor_herd_1"] = true,
		["wh_dlc03_bst_inf_razorgor_herd_0"] = true,
		["wh_dlc03_bst_inf_ungor_herd_1"] = true,
		["wh_dlc03_bst_inf_ungor_raiders_0"] = true,
		["wh_dlc03_bst_inf_ungor_spearmen_0"] = true,
		["wh_dlc03_bst_inf_ungor_spearmen_1"] = true,
		["wh_dlc04_emp_art_hammer_of_the_witches_0"] = true,
		["wh_dlc04_emp_art_sunmaker_0"] = true,
		["wh_dlc04_emp_cav_knights_blazing_sun_0"] = true,
		["wh_dlc04_emp_cav_royal_altdorf_gryphites_0"] = true,
		["wh_dlc04_emp_cav_zintlers_reiksguard_0"] = true,
		["wh_dlc04_emp_inf_flagellants_0"] = true,
		["wh_dlc04_emp_inf_free_company_militia_0"] = true,
		["wh_dlc04_emp_inf_sigmars_sons_0"] = true,
		["wh_dlc04_emp_inf_silver_bullets_0"] = true,
		["wh_dlc04_emp_inf_stirlands_revenge_0"] = true,
		["wh_dlc04_emp_inf_tattersouls_0"] = true,
		["wh_dlc04_emp_veh_templehof_luminark_0"] = true,
		["wh_dlc04_vmp_cav_chillgheists_0"] = true,
		["wh_dlc04_vmp_cav_vereks_reavers_0"] = true,
		["wh_dlc04_vmp_inf_feasters_in_the_dusk_0"] = true,
		["wh_dlc04_vmp_inf_konigstein_stalkers_0"] = true,
		["wh_dlc04_vmp_inf_sternsmen_0"] = true,
		["wh_dlc04_vmp_inf_tithe_0"] = true,
		["wh_dlc04_vmp_mon_direpack_0"] = true,
		["wh_dlc04_vmp_veh_claw_of_nagash_0"] = true,
		["wh_dlc04_vmp_veh_corpse_cart_0"] = true,
		["wh_dlc04_vmp_veh_corpse_cart_1"] = true,
		["wh_dlc04_vmp_veh_corpse_cart_2"] = true,
		["wh_dlc04_vmp_veh_mortis_engine_0"] = true,
		["wh_dlc05_bst_mon_harpies_0"] = true,
		["wh_dlc05_wef_cav_glade_riders_0"] = true,
		["wh_dlc05_wef_cav_glade_riders_1"] = true,
		["wh_dlc05_wef_cav_glade_riders_1_qb"] = true,
		["wh_dlc05_wef_cav_sisters_thorn_0"] = true,
		["wh_dlc05_wef_cav_wild_riders_0"] = true,
		["wh_dlc05_wef_cav_wild_riders_1"] = true,
		["wh_dlc05_wef_inf_deepwood_scouts_0"] = true,
		["wh_dlc05_wef_inf_deepwood_scouts_1"] = true,
		["wh_dlc05_wef_inf_deepwood_scouts_1_qb"] = true,
		["wh_dlc05_wef_inf_dryads_0"] = true,
		["wh_dlc05_wef_inf_eternal_guard_0"] = true,
		["wh_dlc05_wef_inf_eternal_guard_1"] = true,
		["wh_dlc05_wef_inf_eternal_guard_1_qb"] = true,
		["wh_dlc05_wef_inf_glade_guard_0"] = true,
		["wh_dlc05_wef_inf_glade_guard_1"] = true,
		["wh_dlc05_wef_inf_glade_guard_1_qb"] = true,
		["wh_dlc05_wef_inf_glade_guard_2"] = true,
		["wh_dlc05_wef_inf_wardancers_0"] = true,
		["wh_dlc05_wef_inf_wardancers_1"] = true,
		["wh_dlc05_wef_inf_waywatchers_0"] = true,
		["wh_dlc05_wef_inf_wildwood_rangers_0"] = true,
		["wh_dlc06_chs_cav_marauder_horsemasters_0"] = true,
		["wh_dlc06_chs_inf_aspiring_champions_0"] = true,
		["wh_dlc06_dwf_art_bolt_thrower_0"] = true,
		["wh_dlc06_dwf_art_gob_lobber_0"] = true,
		["wh_dlc06_dwf_inf_bugmans_rangers_0"] = true,
		["wh_dlc06_dwf_inf_dragonback_slayers_0"] = true,
		["wh_dlc06_dwf_inf_ekrund_miners_0"] = true,
		["wh_dlc06_dwf_inf_norgrimlings_ironbreakers_0"] = true,
		["wh_dlc06_dwf_inf_norgrimlings_irondrakes_0"] = true,
		["wh_dlc06_dwf_inf_old_grumblers_0"] = true,
		["wh_dlc06_dwf_inf_peak_gate_guard_0"] = true,
		["wh_dlc06_dwf_inf_rangers_0"] = true,
		["wh_dlc06_dwf_inf_rangers_1"] = true,
		["wh_dlc06_dwf_inf_ulthars_raiders_0"] = true,
		["wh_dlc06_dwf_inf_warriors_dragonfire_pass_0"] = true,
		["wh_dlc06_grn_art_hammer_of_gork_0"] = true,
		["wh_dlc06_grn_cav_broken_tusks_mob_0"] = true,
		["wh_dlc06_grn_cav_deff_creepers_0"] = true,
		["wh_dlc06_grn_cav_durkits_squigs_0"] = true,
		["wh_dlc06_grn_cav_mogrubbs_marauders_0"] = true,
		["wh_dlc06_grn_cav_moon_howlers_0"] = true,
		["wh_dlc06_grn_cav_squig_hoppers_0"] = true,
		["wh_dlc06_grn_cav_teef_robbers_0"] = true,
		["wh_dlc06_grn_inf_da_eight_peaks_loonies_0"] = true,
		["wh_dlc06_grn_inf_da_rusty_arrers_0"] = true,
		["wh_dlc06_grn_inf_da_warlords_boyz_0"] = true,
		["wh_dlc06_grn_inf_krimson_killerz_0"] = true,
		["wh_dlc06_grn_inf_nasty_skulkers_0"] = true,
		["wh_dlc06_grn_inf_squig_explosive_0"] = true,
		["wh_dlc06_grn_inf_squig_herd_0"] = true,
		["wh_dlc06_grn_mon_spider_hatchlings_0"] = true,
		["wh_dlc06_grn_mon_spider_hatchlings_0_summoned"] = true,
		["wh_dlc07_brt_art_blessed_field_trebuchet_0"] = true,
		["wh_dlc07_brt_cav_grail_guardians_0"] = true,
		["wh_dlc07_brt_cav_knights_errant_0"] = true,
		["wh_dlc07_brt_cav_questing_knights_0"] = true,
		["wh_dlc07_brt_cav_royal_hippogryph_knights_0"] = true,
		["wh_dlc07_brt_cav_royal_pegasus_knights_0"] = true,
		["wh_dlc07_brt_inf_battle_pilgrims_0"] = true,
		["wh_dlc07_brt_inf_foot_squires_0"] = true,
		["wh_dlc07_brt_inf_men_at_arms_1"] = true,
		["wh_dlc07_brt_inf_men_at_arms_2"] = true,
		["wh_dlc07_brt_inf_peasant_bowmen_1"] = true,
		["wh_dlc07_brt_inf_peasant_bowmen_2"] = true,
		["wh_dlc07_brt_inf_peasant_mob_0"] = true,
		["wh_dlc07_brt_inf_spearmen_at_arms_1"] = true,
		["wh_dlc08_nor_art_hellcannon_battery"] = true,
		["wh_dlc08_nor_cav_marauder_horsemasters_0"] = true,
		["wh_dlc08_nor_cav_marauder_warwolves_chariot_0"] = true,
		["wh_dlc08_nor_inf_marauder_berserkers_0"] = true,
		["wh_dlc08_nor_inf_marauder_champions_0"] = true,
		["wh_dlc08_nor_inf_marauder_champions_1"] = true,
		["wh_dlc08_nor_inf_marauder_hunters_0"] = true,
		["wh_dlc08_nor_inf_marauder_hunters_1"] = true,
		["wh_dlc08_nor_inf_marauder_spearman_0"] = true,
		["wh_dlc08_nor_mon_marauder_warwolves_0"] = true,
		["wh_dlc08_nor_mon_war_mammoth_1"] = true,
		["wh_dlc08_nor_mon_war_mammoth_2"] = true,
		["wh_dlc29_vmp_inf_cairn_wraiths_summoned"] = true,
		["wh_dlc29_vmp_inf_cairn_wraiths_summoned_upgraded_0"] = true,
		["wh_dlc29_vmp_inf_cairn_wraiths_summoned_upgraded_1"] = true,
		["wh_main_brt_art_field_trebuchet"] = true,
		["wh_main_brt_cav_grail_knights"] = true,
		["wh_main_brt_cav_knights_of_the_realm"] = true,
		["wh_main_brt_cav_mounted_yeomen_0"] = true,
		["wh_main_brt_cav_mounted_yeomen_1"] = true,
		["wh_main_brt_cav_pegasus_knights"] = true,
		["wh_main_brt_inf_men_at_arms"] = true,
		["wh_main_brt_inf_peasant_bowmen"] = true,
		["wh_main_brt_inf_spearmen_at_arms"] = true,
		["wh_main_chs_art_hellcannon"] = true,
		["wh_main_chs_cav_chaos_chariot"] = true,
		["wh_main_chs_cav_chaos_knights_0"] = true,
		["wh_main_chs_cav_chaos_knights_1"] = true,
		["wh_main_chs_cav_marauder_horsemen_0"] = true,
		["wh_main_chs_cav_marauder_horsemen_1"] = true,
		["wh_main_chs_inf_chaos_marauders_0"] = true,
		["wh_main_chs_inf_chaos_marauders_1"] = true,
		["wh_main_chs_inf_chaos_warriors_0"] = true,
		["wh_main_chs_inf_chaos_warriors_1"] = true,
		["wh_main_chs_inf_chosen_0"] = true,
		["wh_main_chs_inf_chosen_1"] = true,
		["wh_main_chs_mon_chaos_warhounds_0"] = true,
		["wh_main_chs_mon_chaos_warhounds_1"] = true,
		["wh_main_dwf_art_cannon"] = true,
		["wh_main_dwf_art_flame_cannon"] = true,
		["wh_main_dwf_art_grudge_thrower"] = true,
		["wh_main_dwf_art_organ_gun"] = true,
		["wh_main_dwf_inf_dwarf_warrior_0"] = true,
		["wh_main_dwf_inf_dwarf_warrior_1"] = true,
		["wh_main_dwf_inf_hammerers"] = true,
		["wh_main_dwf_inf_ironbreakers"] = true,
		["wh_main_dwf_inf_irondrakes_0"] = true,
		["wh_main_dwf_inf_irondrakes_2"] = true,
		["wh_main_dwf_inf_longbeards"] = true,
		["wh_main_dwf_inf_longbeards_1"] = true,
		["wh_main_dwf_inf_miners_0"] = true,
		["wh_main_dwf_inf_miners_1"] = true,
		["wh_main_dwf_inf_quarrellers_0"] = true,
		["wh_main_dwf_inf_quarrellers_1"] = true,
		["wh_main_dwf_inf_slayers"] = true,
		["wh_main_dwf_inf_thunderers_0"] = true,
		["wh_main_emp_art_great_cannon"] = true,
		["wh_main_emp_art_helblaster_volley_gun"] = true,
		["wh_main_emp_art_helstorm_rocket_battery"] = true,
		["wh_main_emp_art_mortar"] = true,
		["wh_main_emp_cav_demigryph_knights_0"] = true,
		["wh_main_emp_cav_demigryph_knights_1"] = true,
		["wh_main_emp_cav_empire_knights"] = true,
		["wh_main_emp_cav_outriders_0"] = true,
		["wh_main_emp_cav_outriders_1"] = true,
		["wh_main_emp_cav_pistoliers_1"] = true,
		["wh_main_emp_cav_reiksguard"] = true,
		["wh_main_emp_inf_crossbowmen"] = true,
		["wh_main_emp_inf_greatswords"] = true,
		["wh_main_emp_inf_halberdiers"] = true,
		["wh_main_emp_inf_handgunners"] = true,
		["wh_main_emp_inf_spearmen_0"] = true,
		["wh_main_emp_inf_spearmen_1"] = true,
		["wh_main_emp_inf_swordsmen"] = true,
		["wh_main_emp_veh_luminark_of_hysh_0"] = true,
		["wh_main_grn_art_doom_diver_catapult"] = true,
		["wh_main_grn_art_goblin_rock_lobber"] = true,
		["wh_main_grn_cav_forest_goblin_spider_riders_0"] = true,
		["wh_main_grn_cav_forest_goblin_spider_riders_1"] = true,
		["wh_main_grn_cav_goblin_wolf_chariot"] = true,
		["wh_main_grn_cav_goblin_wolf_riders_0"] = true,
		["wh_main_grn_cav_goblin_wolf_riders_1"] = true,
		["wh_main_grn_cav_orc_boar_boy_big_uns"] = true,
		["wh_main_grn_cav_orc_boar_boyz"] = true,
		["wh_main_grn_cav_orc_boar_chariot"] = true,
		["wh_main_grn_cav_savage_orc_boar_boy_big_uns"] = true,
		["wh_main_grn_cav_savage_orc_boar_boyz"] = true,
		["wh_main_grn_inf_black_orcs"] = true,
		["wh_main_grn_inf_goblin_archers"] = true,
		["wh_main_grn_inf_goblin_spearmen"] = true,
		["wh_main_grn_inf_night_goblin_archers"] = true,
		["wh_main_grn_inf_night_goblin_fanatics"] = true,
		["wh_main_grn_inf_night_goblin_fanatics_1"] = true,
		["wh_main_grn_inf_night_goblins"] = true,
		["wh_main_grn_inf_orc_arrer_boyz"] = true,
		["wh_main_grn_inf_orc_big_uns"] = true,
		["wh_main_grn_inf_orc_boyz"] = true,
		["wh_main_grn_inf_savage_orc_arrer_boyz"] = true,
		["wh_main_grn_inf_savage_orc_big_uns"] = true,
		["wh_main_grn_inf_savage_orcs"] = true,
		["wh_main_nor_cav_chaos_chariot"] = true,
		["wh_main_nor_cav_marauder_horsemen_0"] = true,
		["wh_main_nor_cav_marauder_horsemen_1"] = true,
		["wh_main_nor_inf_chaos_marauders_0"] = true,
		["wh_main_nor_inf_chaos_marauders_1"] = true,
		["wh_main_nor_mon_chaos_warhounds_0"] = true,
		["wh_main_nor_mon_chaos_warhounds_1"] = true,
		["wh_main_vmp_cav_black_knights_0"] = true,
		["wh_main_vmp_cav_black_knights_3"] = true,
		["wh_main_vmp_cav_hexwraiths"] = true,
		["wh_main_vmp_inf_cairn_wraiths"] = true,
		["wh_main_vmp_inf_crypt_ghouls"] = true,
		["wh_main_vmp_inf_crypt_ghouls_summoned"] = true,
		["wh_main_vmp_inf_grave_guard_0"] = true,
		["wh_main_vmp_inf_grave_guard_0_summoned"] = true,
		["wh_main_vmp_inf_grave_guard_1"] = true,
		["wh_main_vmp_inf_skeleton_warriors_0"] = true,
		["wh_main_vmp_inf_skeleton_warriors_0_summoned"] = true,
		["wh_main_vmp_inf_skeleton_warriors_1"] = true,
		["wh_main_vmp_inf_zombie"] = true,
		["wh_main_vmp_inf_zombie_summoned"] = true,
		["wh_main_vmp_mon_dire_wolves"] = true,
		["wh_main_vmp_mon_fell_bats"] = true,
		["wh_main_vmp_veh_black_coach"] = true,
		["wh_pro03_vmp_cha_krell_0"] = true,
		["wh_pro03_vmp_cha_krell_campaign_0"] = true,
		["wh_pro03_vmp_cha_krell_campaign_1"] = true,
		["wh_pro03_vmp_cha_krell_campaign_2"] = true,
		["wh_pro03_vmp_cha_krell_campaign_3"] = true,
		["wh_pro03_vmp_cha_krell_campaign_4"] = true,
		["wh_pro04_brt_cav_knights_errant_ror_0"] = true,
		["wh_pro04_brt_cav_knights_of_the_realm_ror_0"] = true,
		["wh_pro04_brt_cav_mounted_yeomen_ror_0"] = true,
		["wh_pro04_brt_cav_questing_knights_ror_0"] = true,
		["wh_pro04_brt_inf_battle_pilgrims_ror_0"] = true,
		["wh_pro04_brt_inf_foot_squires_ror_0"] = true,
		["wh_pro04_bst_inf_bestigor_herd_ror_0"] = true,
		["wh_pro04_bst_inf_centigors_ror_0"] = true,
		["wh_pro04_bst_inf_gor_herd_ror_0"] = true,
		["wh_pro04_bst_inf_ungor_spearmen_ror_0"] = true,
		["wh_pro04_chs_art_hellcannon_ror_0"] = true,
		["wh_pro04_chs_cav_chaos_knights_ror_0"] = true,
		["wh_pro04_chs_inf_chaos_warriors_ror_0"] = true,
		["wh_pro04_chs_inf_forsaken_ror_0"] = true,
		["wh_pro04_nor_inf_chaos_marauders_ror_0"] = true,
		["wh_pro04_nor_inf_marauder_berserkers_ror_0"] = true,
		["wh_pro04_nor_mon_marauder_warwolves_ror_0"] = true,
		["wh_pro04_nor_mon_war_mammoth_ror_0"] = true,
		["wh_pro04_wef_cav_wild_riders_ror_0"] = true,
		["wh_pro04_wef_inf_eternal_guard_ror_0"] = true,
		["wh_pro04_wef_inf_wardancers_ror_0"] = true,
		["wh_pro04_wef_inf_waywatchers_ror_0"] = true,
		["wh_pro04_wef_inf_wildwood_rangers_ror_0"] = true,
		["wh_twa03_def_inf_squig_explosive_0"] = true,
	},
}

-- true when the engine's type() key of `unit` is a member of the named class
-- list above. A missing / raising / non-string type() read is NOT a member.
function FOURTH.class_member(unit, name)
	local tbl = FOURTH.class_keys[name]
	if tbl == nil then return false end
	local ok, t = pcall(function() return unit:type() end)
	if not ok or type(t) ~= "string" then return false end
	return tbl[t] == true
end


-- THE TARGET-CLASS GATE (harness 99): the CURRENT entry's required class, or
-- "broken" for the morale gate, or nil for a plain ally pick. Set by the
-- entry's own evaluator and cleared by the poll before every evaluate.
FOURTH.ab_filter = nil
-- true when THIS entry's cast carries NO distance bound (Merciw's Monstrous
-- Regiment - infinite range per the wiki).
FOURTH.ab_infinite = nil

-- the printed bound text: "none (infinite range per wiki)" for an unbounded
-- entry, otherwise the ability's own named 70% constant in metres.
function FOURTH.ab_bound_text()
	if FOURTH.ab_infinite then return "none (infinite range per wiki)" end
	return tostring(FOURTH.ab_range_m) .. "m"
end

-- MORALE-BROKEN read for the Iron-Handed Captain gate: the engine's per-unit
-- MoraleState context string; only the exact state name "broken" counts
-- (fail-closed: an unreadable read is NOT broken).
function FOURTH.morale_broken(unit)
	local ok, st = pcall(function() return FOURTH.context_value(unit, "MoraleState") end)
	if not ok then return false end
	return st == "broken"
end

-- true when `unit` passes THIS entry's TARGET-CLASS gate (FOURTH.ab_filter).
-- nil filter -> every unit passes; a class name -> the unit's type() key must
-- be a member of that derived list; "broken" -> its morale must be broken.
-- A missing / unreadable read FAILS CLOSED (the unit is not offered).
function FOURTH.ab_filter_ok(unit)
	local f = FOURTH.ab_filter
	if f == nil then return true end
	if f == "broken" then return FOURTH.morale_broken(unit) end
	-- ROUND 132 (patch 9.0.5): Overseer of the Unseen can no longer target a flying
	-- unit (invalid target flying_currently): a flying ally is skipped. An
	-- unreadable flight read is not flying.
	if f == "overseer" then
		local ok_fly, fly = pcall(function() return unit:is_currently_flying() end)
		if ok_fly and fly == true then return false end
	end
	return FOURTH.class_member(unit, f)
end
-- THE SHARED ALLY PICKER (Class B): walk the tracked friendly units and keep
-- the ones that are ALIVE, NOT the caster and NOT routing; a TARGET-CLASS gate
-- (FOURTH.ab_filter, harness 99) is applied to every candidate FIRST; the
-- family rule then chooses - "heal" = the LOWEST-health ally at or below 75%,
-- "wavering" = the CLOSEST wavering ally, "winds" = the ally with the MOST
-- ABSOLUTE HIT POINTS REMAINING (max HealthValue - the recipient of Grut's
-- Sickle pays a health cost, so the sturdiest unit can best afford it),
-- "buff" = the CLOSEST ally. The chosen ally rides FOURTH.cast_target (the
-- CAST TARGET), FOURTH.ab_ally (the pre-cast re-check slot) and the FRESH
-- caster/ally script_units. Returns the reason string, or nil when nothing
-- qualifies. The OWNER is NEVER the target.
function FOURTH.ab_pick_ally(unit, routing, family)
	FOURTH.ab_family = family
	local best_ally, best_gap, best_hp, best_val = nil, nil, nil, nil
	if not routing then
		local self_id = tostring(unit:unique_ui_id())
		for i = 1, #tracked_units do
			local other = tracked_units[i] and tracked_units[i].unit
			if other ~= nil and other ~= unit and other:number_of_men_alive() > 0 then
				if tostring(other:unique_ui_id()) ~= self_id and not unit_is_routing(other)
					and FOURTH.ab_filter_ok(other) then
					local eligible = false
					local hp = nil
					local val = nil
					if family == "heal" then
						hp = FOURTH.health_pct(other)
						eligible = (type(hp) == "number" and hp <= 75)
					elseif family == "wavering" then
						eligible = (FOURTH.wavering(other) == true)
					elseif family == "winds" then
						val = FOURTH.context_value(other, "HealthValue")
						eligible = (type(val) == "number")
					elseif family == "fighting" then
						-- ROUND 132: Seerstaff / Harmonic Convergence - an ally in melee
						-- or shooting past its cast point (the closest wins)
						eligible = FOURTH.fighting(other)
					elseif family == "shooting" then
						-- ROUND 131: Deranged Munitions / Entrenchment - an ally shooting
						-- past its cast point (the closest wins, the default rule below)
						eligible = FOURTH.shooting_past_cast_point(other)
					elseif family == "ammo" then
						-- ROUND 130: Restock! - shooting now, at or below the line
						val = FOURTH.ammo_fraction_if_firing(other)
						eligible = (val ~= nil and val <= FOURTH.RESTOCK_AT_FRACTION)
					else
						eligible = true
					end
					if eligible then
						local gap = FOURTH.ab_ally_gap(unit, other)
						if FOURTH.ab_gap_ok(gap) then
							local better = false
							if best_ally == nil then
								better = true
							elseif family == "heal" then
								better = (type(hp) == "number" and type(best_hp) == "number" and hp < best_hp)
							elseif family == "winds" then
								better = (type(val) == "number" and (type(best_val) ~= "number" or val > best_val))
							elseif family == "ammo" then
								better = (type(best_val) ~= "number" or val < best_val)
							else
								better = (gap ~= nil and (best_gap == nil or gap < best_gap))
							end
							if better then
								best_ally, best_gap, best_hp, best_val = other, gap, hp, val
							end
						end
					end
				end
			end
		end
	end
	if best_ally == nil then return nil end
	local atype = "ally"
	pcall(function() atype = tostring(best_ally:type()) end)
	log("  " .. (FOURTH.ab_marker or "ally") .. " ally: '" .. atype .. "' is the chosen ally ("
		.. tostring(family)
		.. ((FOURTH.ab_filter ~= nil) and (", gate=" .. tostring(FOURTH.ab_filter)) or "")
		.. ") distance="
		.. ((best_gap ~= nil) and string.format("%.1f", best_gap) or "?")
		.. "m bound=" .. FOURTH.ab_bound_text())
	FOURTH.ab_ally = best_ally
	FOURTH.ab_caster_su = FOURTH.ab_fresh_friend_su(unit)
	FOURTH.ab_ally_su = FOURTH.ab_fresh_friend_su(best_ally)
	FOURTH.cast_target = best_ally
	if family == "heal" then
		return string.format("%s: lowest-health ally %d%% (<= 75%%), cast on ally",
			tostring(FOURTH.ab_marker or "ally"), math.floor(best_hp or 0))
	elseif family == "wavering" then
		return tostring(FOURTH.ab_marker or "ally") .. ": wavering ally in range, cast on ally"
	elseif family == "fighting" then
		return tostring(FOURTH.ab_marker or "ally") .. ": the caster is neither in melee nor shooting; the closest ally in melee or shooting, cast on ally"
	elseif family == "shooting" then
		return tostring(FOURTH.ab_marker or "ally") .. ": the caster is not shooting; the closest ally shooting past its cast point, cast on ally"
	elseif family == "ammo" then
		pcall(function() FOURTH.ammo_claim_id = tostring(best_ally:unique_ui_id()) end)
		return string.format("%s: shooting ally with the least ammunition left, %d%% (<= %d%%), cast on ally",
			tostring(FOURTH.ab_marker or "ally"), math.floor((best_val or 0) * 100),
			math.floor(FOURTH.RESTOCK_AT_FRACTION * 100 + 0.5))
	elseif family == "winds" then
		return string.format("%s: highest-hit-point ally %d hp (HealthValue), cast on ally",
			tostring(FOURTH.ab_marker or "ally"), math.floor(best_val or 0))
	elseif FOURTH.ab_infinite then
		return tostring(FOURTH.ab_marker or "ally")
			.. ": closest ally in range, no distance bound (infinite range per wiki), cast on ally"
	elseif FOURTH.ab_filter ~= nil then
		return tostring(FOURTH.ab_marker or "ally") .. ": closest "
			.. tostring(FOURTH.ab_filter) .. "-class ally in range, cast on ally"
	end
	return tostring(FOURTH.ab_marker or "ally") .. ": closest ally in range, cast on ally"
end

-- ally_heal: a PURE HEAL - the health-only trigger family. Fires when a
-- friendly unit other than the caster is at or below 75% health within the
-- ability's own 70% bound; the LOWEST-health such ally is the CAST TARGET.
function FOURTH.evaluate_ally_heal(unit, routing)
	return FOURTH.ab_pick_ally(unit, routing, "heal")
end

-- ally_heal_melee: a heal that ALSO grants armour/defence - the melee+health
-- gate (the Potion-of-Toughness pattern). The OWNER must be in melee; the
-- LOWEST-health ally at or below 75% within the bound is the CAST TARGET.
function FOURTH.evaluate_ally_heal_melee(unit, routing)
	if routing or not unit:is_in_melee() then return nil end
	local reason = FOURTH.ab_pick_ally(unit, routing, "heal")
	if reason ~= nil then
		reason = "in melee, " .. reason
	end
	return reason
end

-- ally_wavering: an Unbreakable / morale-recovery effect - the wavering family.
-- The CLOSEST WAVERING ally within the bound is the CAST TARGET. The owner need
-- not be in melee and need not be wavering.
function FOURTH.evaluate_ally_wavering(unit, routing)
	return FOURTH.ab_pick_ally(unit, routing, "wavering")
end

-- ally_melee_buff: the DEFAULT in-melee/not-routing shape. The OWNER must be in
-- melee and neither routing nor wavering (fail-open morale); the CLOSEST ally
-- within the bound is the CAST TARGET.
function FOURTH.evaluate_ally_melee_buff(unit, routing)
	if routing or not unit:is_in_melee() then return nil end
	if FOURTH.wavering(unit) == true then return nil end
	return FOURTH.ab_pick_ally(unit, routing, "buff")
end

-- TARGET-CLASS GATED ALLY FAMILIES (harness 99). Each sets FOURTH.ab_filter
-- to its required class (or "broken" for the morale gate) and rides the
-- SHARED ally picker. The ONLY offer gates are: the ally is ALIVE, NOT the
-- caster, NOT routing, PASSES the class gate, and lies within the ability's
-- OWN 70% bound (SKIPPED entirely for Merciw's - infinite range per the wiki).
-- The CAST TARGET is ALWAYS the qualifying ally - NEVER the caster.
function FOURTH.evaluate_ally_overseer(unit, routing)
	FOURTH.ab_filter = "overseer"
	return FOURTH.ab_pick_ally(unit, routing, "buff")
end

-- whiplash: the target must be a BEAST (FOURTH.class_keys.beast).
function FOURTH.evaluate_ally_beast(unit, routing)
	FOURTH.ab_filter = "beast"
	return FOURTH.ab_pick_ally(unit, routing, "buff")
end

-- iron_hand_captain: the target's morale must be BROKEN.
function FOURTH.evaluate_ally_broken(unit, routing)
	FOURTH.ab_filter = "broken"
	return FOURTH.ab_pick_ally(unit, routing, "buff")
end

-- inspired_marksmanship i/ii/iii: the target must be MISSILE-CAPABLE.
function FOURTH.evaluate_ally_missile(unit, routing)
	FOURTH.ab_filter = "missile"
	return FOURTH.ab_pick_ally(unit, routing, "buff")
end

-- makaissons_persuader: the target must be a WAR MACHINE (a repair).
function FOURTH.evaluate_ally_warmachine_heal(unit, routing)
	FOURTH.ab_filter = "warmachine"
	return FOURTH.ab_pick_ally(unit, routing, "heal")
end

-- reforge: the target must carry the HELL-FORGED attribute (a repair).
function FOURTH.evaluate_ally_hellforged_heal(unit, routing)
	FOURTH.ab_filter = "hellforged"
	return FOURTH.ab_pick_ally(unit, routing, "heal")
end

-- remouldered: the target must be a MONSTER (a heal + combat buff).
function FOURTH.evaluate_ally_monster_heal(unit, routing)
	FOURTH.ab_filter = "monster"
	return FOURTH.ab_pick_ally(unit, routing, "heal")
end

-- restore: the target must be a CONSTRUCT (a heal).
function FOURTH.evaluate_ally_construct_heal(unit, routing)
	FOURTH.ab_filter = "construct"
	return FOURTH.ab_pick_ally(unit, routing, "heal")
end

-- merciws_monstrous_regiment: an ally-targeted buff with NO distance bound.
-- INFINITE RANGE per the wiki (target_intercept_range = -1.0 = no real range),
-- so the offer test is skipped ENTIRELY - the chosen ally is the closest
-- qualifying one, however far. The REAL distance is still logged for
-- diagnosis (the picker and the pre-cast re-check both print it).
function FOURTH.evaluate_ally_infinite_buff(unit, routing)
	FOURTH.ab_infinite = true
	return FOURTH.ab_pick_ally(unit, routing, "buff")
end

-- gruts_sickle: ally-targeted, but the PICK RULE is the ally with the
-- HIGHEST ABSOLUTE HIT POINTS REMAINING (max HealthValue), not the lowest -
-- the recipient pays a health COST for the winds recharge, so the sturdiest
-- unit can best afford it. No health-percentage gate.
function FOURTH.evaluate_ally_winds(unit, routing)
	return FOURTH.ab_pick_ally(unit, routing, "winds")
end

-- ACCUSATION (this round) - the FIRST ENEMY-TARGETED trigger, and the first
-- ability whose cast target is an ENEMY unit.
--   THE USER'S RULE (verbatim): "implement accusation automatic activation when
--   enemy unit in range is in melee or being shot at."
--   THE TRIGGER (per poll, for a unit that owns an enemy-targeted key):
--   enumerate the enemy script units; keep those that are (a) valid and alive
--   and (b) inside the ability's own reach; of those pick one that is IN MELEE
--   or UNDER MISSILE FIRE (prefer in-melee; among equals the closest). If none
--   qualifies, do nothing. The chosen enemy becomes the CAST TARGET - NEVER
--   the owner.
--   THE PROVEN ROUTE (round-4 probe, log-confirmed): the target is re-fetched
--   FRESH from the enemy enumerator on the SAME tick and the caster's
--   controller is re-read fresh (FOURTH.eg_fresh_caster_su) - the bench_fresh
--   shape `caster_su.uc:perform_special_ability(key, enemy_su.unit)`, which
--   LANDED in the probe (target effect count 0->1, `CMD event=SpecialAbility`,
--   RESULT route=bench_fresh landed=yes). A controller handle held from an
--   earlier poll silently no-ops (accepted=true, nothing applies).
--   THE RANGE SOURCE (harness 96 - THE MOVE-ORDER ROOT CAUSE FIXED):
--   Accusation's own target_intercept_range in unit_spec_abil.tsv = 75.0000 m;
--   the standing 70% rule stores floor(75 * 0.70) = 52 m as the named
--   FOURTH.ACCUSATION_RANGE_M. The enemy is offered ONLY while
--   FOURTH.eg_enemy_within_bound is true - i.e. while the engine's distance
--   `unit:unit_distance(enemy)` (EDGE-TO-EDGE metres, battle_unit.lua:160) is
--   <= FOURTH.ACCUSATION_RANGE_M. THE ENGINE'S OWN LOOSER unit_in_range reach
--   read IS NOT USED: the observer probe proved the offer fired at 81.3 m with
--   the engine flag true while our 52 m test was false, and the engine then
--   WALKED the caster in - the reported move order. The bound is a named
--   constant - ONE place to tune.
--   THE SAFETY PATTERN: the chosen enemy rides FOURTH.eg_enemy; the condition
--   (alive + still in melee/under fire + still in range) is RE-CHECKED
--   immediately before the cast and the cast is SKIPPED if it lapsed. The HOLD
--   is the existing per-pair guard + cooldown hold - it never fires every tick.
--   FIELD READS (round 4, proven live on enemies): type(), number_of_men_alive(),
--   is_in_melee(), is_valid_target(). is_under_missile_attack() is NOT proven
--   on an enemy - an unreadable read is treated as FALSE (fail-safe), logged
--   once for the whole battle.
--   THE LOCAL CEILING: every helper, constant and slot rides the FOURTH bag -
--   NO new chunk-level locals.
-- ============================================================================

-- ACCUSATION'S TRIGGER RANGE (this round) - THE STANDING 70% RULE. REAL range
-- 75.0000 m = the ability's own target_intercept_range (unit_spec_abil.tsv,
-- wh_main_hero_abilities_accusation; effect_range = 0.0000, so the intercept
-- reach is the real range). 75 * 0.70 = 52.5 -> 52 m (FLOORED,
-- FOURTH.RANGE_FRACTION). SET TO 52 AFTER THE CASTER WAS SEEN TO WALK toward
-- an enemy that sat inside the 75 m reach but outside a comfortable cast range
-- - the very symptom this rule exists to remove.
FOURTH.ACCUSATION_RANGE_M = 52

-- the chosen ENEMY unit (re-fetched fresh each tick), its arm ("melee" /
-- "missile") and the fresh CASTER script_unit - all cleared before every
-- evaluate so no ability can inherit a stale enemy.
FOURTH.eg_enemy = nil
FOURTH.eg_arm = nil
FOURTH.eg_caster_su = nil
-- the CURRENT ability's 70% bound and its marker (set by the poll before every
-- evaluate), and whether the current enemy trigger is the GROUND form.
FOURTH.eg_range_m = nil
FOURTH.eg_marker = nil
FOURTH.eg_ground = nil
-- THE MELEE-ONLY FLAG (harness 101, Gate of Khorne): set by its OWN
-- evaluator before the shared picker runs, so the picker keeps ONLY
-- enemies that are FIGHTING (in melee) and the pre-cast re-check
-- demands the same. Every other enemy trigger leaves it nil.
FOURTH.eg_melee_only = nil
-- THE SUMMON-ROUND SLOTS (harness 102): the SELF-SUMMON arm's own flag and
-- its freshly re-fetched caster script_unit; the non-commander flag; the
-- picker's MODE ("health" / "melee"); and the "no bound" flag for an
-- entry whose own game row declares target_intercept_range = -1.0 (no real
-- range, so there is no 70% value to take). Cleared before every evaluate.
FOURTH.ss_self = nil
FOURTH.ss_caster_su = nil
-- TZ'ARKAN (this round): the low-health self-transform arm's own flag and
-- the freshly re-fetched caster script_unit. Cleared before every evaluate.
FOURTH.tz_self = nil
FOURTH.tz_caster_su = nil
FOURTH.eg_noncommander = nil
FOURTH.eg_mode = nil
FOURTH.eg_no_bound = nil
FOURTH.eg_infantry = nil

-- one-time notice for an unreadable is_under_missile_attack.
FOURTH.eg_unreadable_logged = false

-- THE DISTANCE PRIMITIVE (harness 96): the gap in metres from the OWNER to a
-- candidate enemy is `unit:unit_distance(enemy)` - an ENGINE-PROVIDED read
-- returning the STRAIGHT-LINE distance in METRES. It is EDGE-TO-EDGE
-- (bounding-box aware), per battle_unit.lua:160 - so the number the log prints
-- IS exactly the number the offer test compared. The charge detector and every
-- ally-range trigger already use this same primitive. nil when the read cannot
-- be taken.
function FOURTH.eg_enemy_gap(unit, enemy)
	local ok, gap = pcall(function() return unit:unit_distance(enemy) end)
	if ok and type(gap) == "number" then return gap end
	return nil
end

-- true while the enemy lies within Accusation's 70% bound (harness 96 - THE
-- FIX FOR THE MOVE ORDER). THE OFFER TEST IS THE CONSTANT ONLY:
--   FOURTH.eg_enemy_gap(unit, enemy) <= FOURTH.ACCUSATION_RANGE_M
-- where the gap is `unit:unit_distance(enemy)` - the engine's EDGE-TO-EDGE
-- distance in metres (bounding-box aware, battle_unit.lua:160). The engine's
-- own looser unit_in_range reach read is NOT consulted: the probe saw it TRUE
-- at 81.3 m where our 52 m test was FALSE, and trusting it made the mod offer a
-- target the engine then WALKED the caster toward. A wholly unreadable
-- distance is treated as OUT of range (fail-safe: never offer an enemy the
-- ability may not cover).
function FOURTH.eg_enemy_within_bound(unit, enemy)
	-- AN UNBOUNDED ENTRY (harness 102): its game row declares
	-- target_intercept_range = -1.0 - NO real range - so there is no 70%
	-- bound to apply and every living enemy is inside it.
	if FOURTH.eg_no_bound == true then return true end
	local gap = FOURTH.eg_enemy_gap(unit, enemy)
	if gap == nil then return false end
	-- THE PER-ABILITY BOUND: FOURTH.eg_range_m is the current ability's own
	-- 70% constant, set by the poll before every evaluate. Accusation (and any
	-- caller that leaves it unset) falls back to FOURTH.ACCUSATION_RANGE_M.
	local bound = FOURTH.eg_range_m
	if bound == nil then
		return gap <= FOURTH.ACCUSATION_RANGE_M
	end
	return gap <= bound
end

-- true / false / nil - the enemy's validity. is_valid_target() is the read the
-- round-4 probe took; is_valid() is the documented name. A raising read on both
-- answers nil (the caller fail-opens: an unreadable validity never blocks).
function FOURTH.eg_enemy_valid(enemy)
	local ok, v = pcall(function() return enemy:is_valid_target() end)
	if ok then
		if v == true then return true end
		if v == false then return false end
	end
	local ok2, v2 = pcall(function() return enemy:is_valid() end)
	if ok2 then
		if v2 == true then return true end
		if v2 == false then return false end
	end
	return nil
end

-- true when the enemy is currently TAKING missile fire. battle_unit:
-- is_under_missile_attack() exists but was NEVER probed on an enemy, so an
-- unreadable read is treated as FALSE (fail-safe) and a raising read writes ONE
-- loud line for the whole battle (never a per-tick stream).
function FOURTH.eg_under_missile_attack(enemy)
	local ok, v = pcall(function() return enemy:is_under_missile_attack() end)
	if ok and v == true then return true end
	if not ok and not FOURTH.eg_unreadable_logged then
		FOURTH.eg_unreadable_logged = true
		log("accusation: enemy is_under_missile_attack read UNAVAILABLE (raised) - treated as FALSE (fail-safe). One-time notice.")
	end
	return false
end

-- re-fetch the CASTER's script_unit FRESH from the friendly enumerator THIS
-- tick (never a controller held from an earlier poll - the round-4 lesson).
-- nil when the army or the matching unit cannot be found.
function FOURTH.eg_fresh_caster_su(unit)
	local ok_coll, coll = pcall(function()
		return bm:get_scriptunits_for_local_players_army()
	end)
	if not ok_coll or coll == nil then return nil end
	local ok_n, n = pcall(function() return coll:count() end)
	if not ok_n or type(n) ~= "number" then return nil end
	local want = nil
	pcall(function() want = tostring(unit:unique_ui_id()) end)
	if want == nil then return nil end
	for i = 1, n do
		local ok_su, su = pcall(function() return coll:item(i) end)
		if ok_su and su ~= nil then
			local u = nil
			pcall(function() u = su.unit end)
			if u ~= nil then
				local id = nil
				pcall(function() id = u:unique_ui_id() end)
				if id ~= nil and tostring(id) == want then return su end
			end
		end
	end
	return nil
end

-- THE SHARED ENEMY PICKER (Class A, harness 97): fire when an ENEMY unit in
-- range is in melee OR under missile fire. Used by BOTH enemy triggers - the
-- unit form (ground = false) and the enemy-GROUND area form (ground = true).
-- The chosen enemy rides FOURTH.cast_target (the CAST TARGET) and
-- FOURTH.eg_enemy (the pre-cast re-check slot) - the owner is NEVER the target.
-- Returns the ATTEMPT reason string, or nil when nothing qualifies.
function FOURTH.eg_pick_enemy(unit, routing, ground)
	local reason = nil
	local marker = FOURTH.eg_marker or "accusation"
	local bound = FOURTH.eg_range_m or FOURTH.ACCUSATION_RANGE_M
	FOURTH.eg_ground = ground
	-- THE MELEE-ONLY ARM (harness 101): Gate of Khorne's trigger says the enemy
	-- must be FIGHTING - in melee - so this form never accepts the
	-- under-missile-fire arm. Every other enemy trigger leaves it unset.
	local melee_only = (FOURTH.eg_melee_only == true)
	if not routing then
		local ok_coll, coll = pcall(function()
			return bm:get_scriptunits_for_main_enemy_army_to_local_player()
		end)
		if ok_coll and coll ~= nil then
			local ok_n, n = pcall(function() return coll:count() end)
			if ok_n and type(n) == "number" then
				local best_enemy, best_gap, best_arm = nil, nil, nil
				for i = 1, n do
					local ok_su, su = pcall(function() return coll:item(i) end)
					if ok_su and su ~= nil then
						local enemy = nil
						pcall(function() enemy = su.unit end)
						if enemy ~= nil then
							local ok_alive, alive = pcall(function() return enemy:number_of_men_alive() end)
							local valid = FOURTH.eg_enemy_valid(enemy)
							local ok_melee, melee = pcall(function() return enemy:is_in_melee() end)
							local arm = nil
							if ok_melee and melee == true then
								arm = "melee"
							elseif (not melee_only) and FOURTH.eg_under_missile_attack(enemy) then
								arm = "missile"
							end
							if arm ~= nil
								and ok_alive and type(alive) == "number" and alive > 0
								and (valid == nil or valid == true)
								and FOURTH.eg_class_ok(enemy)
								and FOURTH.eg_enemy_within_bound(unit, enemy) then
								local gap = FOURTH.eg_enemy_gap(unit, enemy)
								if best_enemy == nil
									or (arm == "melee" and best_arm ~= "melee")
									or (arm == best_arm and gap ~= nil and (best_gap == nil or gap < best_gap)) then
									best_enemy, best_gap, best_arm = enemy, gap, arm
								end
							end
						end
					end
				end
				if best_enemy ~= nil then
					local etype = "enemy"
					pcall(function() etype = tostring(best_enemy:type()) end)
					log("  " .. marker .. " target: '" .. etype .. "' is the chosen enemy (" .. tostring(best_arm)
						.. ") distance=" .. ((best_gap ~= nil) and string.format("%.1f", best_gap) or "?")
						.. "m bound=" .. tostring(bound) .. "m")
					FOURTH.eg_enemy = best_enemy
					FOURTH.eg_arm = best_arm
					FOURTH.eg_caster_su = FOURTH.eg_fresh_caster_su(unit)
					FOURTH.cast_target = best_enemy
					if melee_only then
						-- GATE OF KHORNE'S OWN REASON: names the chosen enemy's type and
						-- the REAL edge-to-edge distance the offer test measured.
						reason = "closest fighting (in-melee) enemy within bound (targeting "
							.. etype .. ", distance="
							.. ((best_gap ~= nil) and string.format("%.1f", best_gap) or "?")
							.. "m)"
					elseif ground then
						if best_arm == "melee" then
							reason = "enemy-ground area in melee (targeting " .. etype .. ")"
						else
							reason = "enemy-ground area under missile fire (targeting " .. etype .. ")"
						end
					else
						if best_arm == "melee" then
							reason = "enemy in melee (targeting " .. etype .. ")"
						else
							reason = "enemy under missile fire (targeting " .. etype .. ")"
						end
					end
				end
			end
		end
	end
	return reason
end

-- THE MELEE-ONLY ENEMY-GROUND EVALUATOR (harness 101, Gate of Khorne).
-- THE USER'S TRIGGER, verbatim: "The trigger will place it on the closest
-- enemy that is in range of the ability and fighting." So: among ENEMY units
-- within the ability's OWN 70% bound (50 m real -> floor(50 * 0.70) = 35 m,
-- FOURTH.ENEMY_CAST_R50), keep those FIGHTING (in melee), pick the CLOSEST,
-- and place the summon on THAT ENEMY'S GROUND via the ground form. The
-- under-missile-fire arm is deliberately NOT accepted - "fighting" is read as
-- in-melee, the strictest reading of the user's word. The chosen enemy is the
-- CAST TARGET - NEVER the owner.
function FOURTH.evaluate_enemy_ground_melee(unit, routing)
	FOURTH.eg_melee_only = true
	return FOURTH.eg_pick_enemy(unit, routing, true)
end

-- THE UNIT-FORM EVALUATOR: the FIRST ENEMY-TARGETED trigger - an enemy UNIT
-- is the cast target.
function FOURTH.evaluate_enemy_engaged_or_shot(unit, routing)
	return FOURTH.eg_pick_enemy(unit, routing, false)
end

-- THE ENEMY-GROUND AREA EVALUATOR (Class A): the same pick, but the cast is
-- PLACED ON THE CHOSEN ENEMY'S GROUND (perform_special_ability_ground with the
-- enemy's own position) instead of aimed at the enemy unit.
function FOURTH.evaluate_enemy_ground_area(unit, routing)
	return FOURTH.eg_pick_enemy(unit, routing, true)
end

-- THE MELEE-ONLY ENEMY-UNIT EVALUATOR (round 123). THE USER'S RULE: a hex
-- whose effect is a melee-only stat (melee defence -40 on No Escape and
-- Transfix) "makes sense only when the enemy is in melee. It does not make
-- sense to activate it when the enemy is shot." So: the SAME shared picker as
-- enemy_engaged_or_shot (enemy alive, a valid target, within this entry's own
-- 70% bound, the closest wins), with the under-missile-fire arm switched OFF
-- by the existing melee-only flag (the one Gate of Khorne uses). The cast is
-- aimed at the chosen ENEMY UNIT (ground = false), and the shared pre-cast
-- re-check requires that enemy to be STILL in melee and still within the
-- bound, or the cast is skipped and not spent.
function FOURTH.evaluate_enemy_melee(unit, routing)
	FOURTH.eg_melee_only = true
	return FOURTH.eg_pick_enemy(unit, routing, false)
end

-- ============================================================================
-- THE SUMMON ROUND (harness 102 / v102) - THE FOUR SUMMON TRIGGERS' HELPERS.
--
--   enemy_ground_melee            (already shipped with Gate of Khorne)
--       (A) the REST of the wh_type_summon_unit class - every in-wheel,
--       non-illusion, GROUND-CASTABLE summon derived from the game's own data
--       (spawned_unit set + type wh_type_summon_unit + spawn_is_decoy false +
--       target_ground true + in-wheel + not boss-only + not implemented) - and
--       (D) the nine unlabelled real spawners. Closest FIGHTING enemy inside
--       the ability's own 70% bound; the summon is placed on THAT ENEMY's
--       ground through the ground form. Never the caster's own ground.
--   self_summon_melee             (NEW - Nurgling Tide)
--       the user's rule, verbatim: "that one should only trigger when the
--       caster himself is in melee." Owner alive + NOT routing + is_in_melee()
--       true; the cast goes on the OWNER through the unit form. NO RANGE
--       BOUND is read or needed - a self cast has no distance to measure (the
--       ability's own row carries target_intercept_range = 0, no target flags
--       at all and affect_self = true: a self-centred spawn).
--   enemy_low_health_noncommander (NEW - Eye of Khorne, a FINISHER)
--       ANY enemy inside the ability's own 70% bound that is BELOW 20% HEALTH
--       and is NOT a Lord or Hero; the LOWEST-health one wins (closest as the
--       tiebreak). Cast through the UNIT form: the row has target_enemies =
--       true and target_ground = false, so perform_special_ability(key, enemy).
--   enemy_melee_noncommander      (NEW - The Dreaded Thirteenth, 4 keys)
--       ANY enemy inside the 70% bound IN MELEE that is NOT a Lord or Hero;
--       closest wins. Cast through the enemy-GROUND form (target_ground = true,
--       spawn_type = unit_position_offset: an explosion plus a summon).
--
-- THE LORD/HERO EXCLUSION COMES FROM A REAL READ. FOURTH.commander_keys is
-- DERIVED from the game's own class/caste columns: every land_units key whose
-- `class` is "com" - the engine's COMMANDER class, the very class its own
-- invalid-target flags name unit_is_commander_class / unit_is_not_commander_class
-- - UNION every land_units key reached from a main_units row whose `caste` is
-- "lord" or "hero" (that second arm catches the six Krell variants whose
-- land_units row still says inf_mel - a known data quirk). It is matched by
-- EXACT WHOLE-KEY equality against battle_unit:type(), the PROVEN land_units key
-- read (the same shape as the Slayer list). battle_unit:unit_class() == "com"
-- is the FALLBACK read when type() cannot be taken; if NEITHER answers, the
-- unit is treated as a COMMANDER and the finisher never fires at it (FAIL
-- CLOSED), one line for the whole battle.
--
-- NO NEW CHUNK-LEVEL LOCALS: every helper, table and slot below is a FIELD of
-- the FOURTH bag - the main chunk sits at Lua's 200-local ceiling.
-- ============================================================================
FOURTH.commander_keys = {
	-- THE DERIVED COMMANDER (LORD/HERO) KEY SET ... 1409 keys
		["wh2_dlc09_skv_cha_tretch_craventail"] = true,
		["wh2_dlc09_tmb_cha_arkhan_0"] = true,
		["wh2_dlc09_tmb_cha_arkhan_1"] = true,
		["wh2_dlc09_tmb_cha_arkhan_2"] = true,
		["wh2_dlc09_tmb_cha_khalida_0"] = true,
		["wh2_dlc09_tmb_cha_khalida_1"] = true,
		["wh2_dlc09_tmb_cha_khalida_2"] = true,
		["wh2_dlc09_tmb_cha_khatep_0"] = true,
		["wh2_dlc09_tmb_cha_khatep_1"] = true,
		["wh2_dlc09_tmb_cha_khatep_2"] = true,
		["wh2_dlc09_tmb_cha_khatep_3"] = true,
		["wh2_dlc09_tmb_cha_liche_priest_death_0"] = true,
		["wh2_dlc09_tmb_cha_liche_priest_death_1"] = true,
		["wh2_dlc09_tmb_cha_liche_priest_light_0"] = true,
		["wh2_dlc09_tmb_cha_liche_priest_light_1"] = true,
		["wh2_dlc09_tmb_cha_liche_priest_nehekhara_0"] = true,
		["wh2_dlc09_tmb_cha_liche_priest_nehekhara_1"] = true,
		["wh2_dlc09_tmb_cha_liche_priest_shadow_0"] = true,
		["wh2_dlc09_tmb_cha_liche_priest_shadow_1"] = true,
		["wh2_dlc09_tmb_cha_necrotect_0"] = true,
		["wh2_dlc09_tmb_cha_necrotect_1"] = true,
		["wh2_dlc09_tmb_cha_settra_0"] = true,
		["wh2_dlc09_tmb_cha_settra_1"] = true,
		["wh2_dlc09_tmb_cha_settra_2"] = true,
		["wh2_dlc09_tmb_cha_settra_3"] = true,
		["wh2_dlc09_tmb_cha_tomb_king_0"] = true,
		["wh2_dlc09_tmb_cha_tomb_king_1"] = true,
		["wh2_dlc09_tmb_cha_tomb_king_2"] = true,
		["wh2_dlc09_tmb_cha_tomb_king_3"] = true,
		["wh2_dlc09_tmb_cha_tomb_prince_0"] = true,
		["wh2_dlc09_tmb_cha_tomb_prince_1"] = true,
		["wh2_dlc09_tmb_cha_tomb_prince_2"] = true,
		["wh2_dlc10_def_cha_crone_0"] = true,
		["wh2_dlc10_def_cha_crone_1"] = true,
		["wh2_dlc10_def_cha_crone_4"] = true,
		["wh2_dlc10_def_cha_crone_5"] = true,
		["wh2_dlc10_def_cha_sorceress_beasts_0"] = true,
		["wh2_dlc10_def_cha_sorceress_beasts_1"] = true,
		["wh2_dlc10_def_cha_sorceress_beasts_2"] = true,
		["wh2_dlc10_def_cha_sorceress_beasts_3"] = true,
		["wh2_dlc10_def_cha_sorceress_death_0"] = true,
		["wh2_dlc10_def_cha_sorceress_death_1"] = true,
		["wh2_dlc10_def_cha_sorceress_death_2"] = true,
		["wh2_dlc10_def_cha_sorceress_death_3"] = true,
		["wh2_dlc10_def_cha_supreme_sorceress_beasts_0"] = true,
		["wh2_dlc10_def_cha_supreme_sorceress_beasts_1"] = true,
		["wh2_dlc10_def_cha_supreme_sorceress_beasts_2"] = true,
		["wh2_dlc10_def_cha_supreme_sorceress_beasts_3"] = true,
		["wh2_dlc10_def_cha_supreme_sorceress_beasts_4"] = true,
		["wh2_dlc10_def_cha_supreme_sorceress_beasts_5"] = true,
		["wh2_dlc10_def_cha_supreme_sorceress_dark_0"] = true,
		["wh2_dlc10_def_cha_supreme_sorceress_dark_1"] = true,
		["wh2_dlc10_def_cha_supreme_sorceress_dark_2"] = true,
		["wh2_dlc10_def_cha_supreme_sorceress_dark_3"] = true,
		["wh2_dlc10_def_cha_supreme_sorceress_dark_4"] = true,
		["wh2_dlc10_def_cha_supreme_sorceress_dark_5"] = true,
		["wh2_dlc10_def_cha_supreme_sorceress_death_0"] = true,
		["wh2_dlc10_def_cha_supreme_sorceress_death_1"] = true,
		["wh2_dlc10_def_cha_supreme_sorceress_death_2"] = true,
		["wh2_dlc10_def_cha_supreme_sorceress_death_3"] = true,
		["wh2_dlc10_def_cha_supreme_sorceress_death_4"] = true,
		["wh2_dlc10_def_cha_supreme_sorceress_death_5"] = true,
		["wh2_dlc10_def_cha_supreme_sorceress_fire_0"] = true,
		["wh2_dlc10_def_cha_supreme_sorceress_fire_1"] = true,
		["wh2_dlc10_def_cha_supreme_sorceress_fire_2"] = true,
		["wh2_dlc10_def_cha_supreme_sorceress_fire_3"] = true,
		["wh2_dlc10_def_cha_supreme_sorceress_fire_4"] = true,
		["wh2_dlc10_def_cha_supreme_sorceress_fire_5"] = true,
		["wh2_dlc10_def_cha_supreme_sorceress_shadow_0"] = true,
		["wh2_dlc10_def_cha_supreme_sorceress_shadow_1"] = true,
		["wh2_dlc10_def_cha_supreme_sorceress_shadow_2"] = true,
		["wh2_dlc10_def_cha_supreme_sorceress_shadow_3"] = true,
		["wh2_dlc10_def_cha_supreme_sorceress_shadow_4"] = true,
		["wh2_dlc10_def_cha_supreme_sorceress_shadow_5"] = true,
		["wh2_dlc10_dwf_cha_thane_ghost_summoned_0"] = true,
		["wh2_dlc10_hef_cha_alarielle_the_radiant_0"] = true,
		["wh2_dlc10_hef_cha_alarielle_the_radiant_1"] = true,
		["wh2_dlc10_hef_cha_alarielle_the_radiant_2"] = true,
		["wh2_dlc10_hef_cha_alarielle_the_radiant_3"] = true,
		["wh2_dlc10_hef_cha_alith_anar_0"] = true,
		["wh2_dlc10_hef_cha_alith_anar_summoned_0"] = true,
		["wh2_dlc10_hef_cha_alith_anar_summoned_1"] = true,
		["wh2_dlc10_hef_cha_handmaiden_0"] = true,
		["wh2_dlc10_hef_cha_handmaiden_1"] = true,
		["wh2_dlc10_hef_cha_handmaiden_2"] = true,
		["wh2_dlc10_hef_cha_mage_heavens_0"] = true,
		["wh2_dlc10_hef_cha_mage_heavens_1"] = true,
		["wh2_dlc10_hef_cha_mage_heavens_2"] = true,
		["wh2_dlc10_hef_cha_mage_shadows_0"] = true,
		["wh2_dlc10_hef_cha_mage_shadows_1"] = true,
		["wh2_dlc10_hef_cha_mage_shadows_2"] = true,
		["wh2_dlc10_hef_cha_shadow_walker"] = true,
		["wh2_dlc10_nor_mon_phoenix_flamespyre_boss"] = true,
		["wh2_dlc11_cst_cha_aranessa_0"] = true,
		["wh2_dlc11_cst_cha_aranessa_1"] = true,
		["wh2_dlc11_cst_cha_cylostra_direfin_0"] = true,
		["wh2_dlc11_cst_cha_cylostra_direfin_1"] = true,
		["wh2_dlc11_cst_cha_damned_paladin_0"] = true,
		["wh2_dlc11_cst_cha_damned_paladin_1"] = true,
		["wh2_dlc11_cst_cha_gunnery_wight_0"] = true,
		["wh2_dlc11_cst_cha_gunnery_wight_1"] = true,
		["wh2_dlc11_cst_cha_luthor_harkon_0"] = true,
		["wh2_dlc11_cst_cha_luthor_harkon_1"] = true,
		["wh2_dlc11_cst_cha_mourngul_haunter"] = true,
		["wh2_dlc11_cst_cha_vampire_fleet_admiral_0"] = true,
		["wh2_dlc11_cst_cha_vampire_fleet_admiral_1"] = true,
		["wh2_dlc11_cst_cha_vampire_fleet_admiral_death_0"] = true,
		["wh2_dlc11_cst_cha_vampire_fleet_admiral_death_1"] = true,
		["wh2_dlc11_cst_cha_vampire_fleet_admiral_deeps_0"] = true,
		["wh2_dlc11_cst_cha_vampire_fleet_admiral_deeps_1"] = true,
		["wh2_dlc11_cst_cha_vampire_fleet_admiral_female_0"] = true,
		["wh2_dlc11_cst_cha_vampire_fleet_admiral_female_1"] = true,
		["wh2_dlc11_cst_cha_vampire_fleet_admiral_female_death_0"] = true,
		["wh2_dlc11_cst_cha_vampire_fleet_admiral_female_death_1"] = true,
		["wh2_dlc11_cst_cha_vampire_fleet_admiral_female_deeps_0"] = true,
		["wh2_dlc11_cst_cha_vampire_fleet_admiral_female_deeps_1"] = true,
		["wh2_dlc11_cst_cha_vampire_fleet_captain_0"] = true,
		["wh2_dlc11_cst_cha_vampire_fleet_captain_1"] = true,
		["wh2_dlc11_cst_cha_vampire_fleet_captain_death_0"] = true,
		["wh2_dlc11_cst_cha_vampire_fleet_captain_death_1"] = true,
		["wh2_dlc11_cst_cha_vampire_fleet_captain_deeps_0"] = true,
		["wh2_dlc11_cst_cha_vampire_fleet_captain_deeps_1"] = true,
		["wh2_dlc11_cst_inf_count_noctilus_0"] = true,
		["wh2_dlc11_cst_inf_count_noctilus_1"] = true,
		["wh2_dlc11_def_cha_lokhir_fellheart_0"] = true,
		["wh2_dlc11_def_cha_lokhir_fellheart_1"] = true,
		["wh2_dlc11_vmp_cha_bloodline_blood_dragon_lord_0"] = true,
		["wh2_dlc11_vmp_cha_bloodline_blood_dragon_lord_1"] = true,
		["wh2_dlc11_vmp_cha_bloodline_blood_dragon_lord_2"] = true,
		["wh2_dlc11_vmp_cha_bloodline_blood_dragon_lord_3"] = true,
		["wh2_dlc11_vmp_cha_bloodline_lahmian_lord_0"] = true,
		["wh2_dlc11_vmp_cha_bloodline_lahmian_lord_1"] = true,
		["wh2_dlc11_vmp_cha_bloodline_lahmian_lord_2"] = true,
		["wh2_dlc11_vmp_cha_bloodline_lahmian_lord_3"] = true,
		["wh2_dlc11_vmp_cha_bloodline_necrarch_lord_0"] = true,
		["wh2_dlc11_vmp_cha_bloodline_necrarch_lord_1"] = true,
		["wh2_dlc11_vmp_cha_bloodline_necrarch_lord_2"] = true,
		["wh2_dlc11_vmp_cha_bloodline_necrarch_lord_3"] = true,
		["wh2_dlc11_vmp_cha_bloodline_strigoi_lord_0"] = true,
		["wh2_dlc11_vmp_cha_bloodline_strigoi_lord_1"] = true,
		["wh2_dlc11_vmp_cha_bloodline_von_carstein_lord_0"] = true,
		["wh2_dlc11_vmp_cha_bloodline_von_carstein_lord_1"] = true,
		["wh2_dlc11_vmp_cha_bloodline_von_carstein_lord_2"] = true,
		["wh2_dlc11_vmp_cha_bloodline_von_carstein_lord_3"] = true,
		["wh2_dlc11_vmp_cha_heinrich_kemmler_1"] = true,
		["wh2_dlc12_lzd_cha_skink_chief_red_crested_0"] = true,
		["wh2_dlc12_lzd_cha_skink_chief_red_crested_1"] = true,
		["wh2_dlc12_lzd_cha_skink_chief_red_crested_2"] = true,
		["wh2_dlc12_lzd_cha_skink_chief_red_crested_3"] = true,
		["wh2_dlc12_lzd_cha_skink_priest_beasts_4"] = true,
		["wh2_dlc12_lzd_cha_skink_priest_heavens_4"] = true,
		["wh2_dlc12_lzd_cha_tehenhauin_0"] = true,
		["wh2_dlc12_lzd_cha_tehenhauin_1"] = true,
		["wh2_dlc12_lzd_cha_tehenhauin_2"] = true,
		["wh2_dlc12_lzd_cha_tehenhauin_3"] = true,
		["wh2_dlc12_lzd_cha_tiktaqto_0"] = true,
		["wh2_dlc12_lzd_cha_tiktaqto_1"] = true,
		["wh2_dlc12_lzd_lzd_cha_kroak_0"] = true,
		["wh2_dlc12_lzd_lzd_cha_kroak_0_boss"] = true,
		["wh2_dlc12_skv_cha_ikit_claw_0"] = true,
		["wh2_dlc12_skv_cha_ikit_claw_1"] = true,
		["wh2_dlc12_skv_cha_ikit_claw_2"] = true,
		["wh2_dlc12_skv_cha_warlock_master_0"] = true,
		["wh2_dlc12_skv_cha_warlock_master_1"] = true,
		["wh2_dlc12_skv_cha_warlock_master_2"] = true,
		["wh2_dlc13_emp_cha_hunter_doctor_hertwig_van_hal_0"] = true,
		["wh2_dlc13_emp_cha_hunter_jorek_grimm_0"] = true,
		["wh2_dlc13_emp_cha_hunter_kalara_of_wydrioth_0"] = true,
		["wh2_dlc13_emp_cha_hunter_rodrik_l_anguille_0"] = true,
		["wh2_dlc13_emp_cha_huntsmarshal_0"] = true,
		["wh2_dlc13_emp_cha_markus_wulfhart_0"] = true,
		["wh2_dlc13_lzd_cha_gor_rok_0"] = true,
		["wh2_dlc13_lzd_cha_kroxigor_ancient_0"] = true,
		["wh2_dlc13_lzd_cha_nakai_0"] = true,
		["wh2_dlc13_lzd_cha_slann_mage_priest_beasts_0"] = true,
		["wh2_dlc13_lzd_cha_slann_mage_priest_death_0"] = true,
		["wh2_dlc13_lzd_cha_slann_mage_priest_fire_0"] = true,
		["wh2_dlc13_lzd_cha_slann_mage_priest_life_0"] = true,
		["wh2_dlc13_lzd_cha_slann_mage_priest_metal_0"] = true,
		["wh2_dlc13_lzd_cha_slann_mage_priest_shadows_0"] = true,
		["wh2_dlc14_brt_cha_henri_le_massif_0"] = true,
		["wh2_dlc14_brt_cha_henri_le_massif_3"] = true,
		["wh2_dlc14_brt_cha_henri_le_massif_4"] = true,
		["wh2_dlc14_brt_cha_repanse_de_lyonesse_0"] = true,
		["wh2_dlc14_brt_cha_repanse_de_lyonesse_1"] = true,
		["wh2_dlc14_def_cha_high_beastmaster_0"] = true,
		["wh2_dlc14_def_cha_high_beastmaster_1"] = true,
		["wh2_dlc14_def_cha_high_beastmaster_2"] = true,
		["wh2_dlc14_def_cha_malus_darkblade_0"] = true,
		["wh2_dlc14_def_cha_malus_darkblade_0_mp"] = true,
		["wh2_dlc14_def_cha_malus_darkblade_1"] = true,
		["wh2_dlc14_def_cha_malus_darkblade_1_mp"] = true,
		["wh2_dlc14_def_cha_malus_darkblade_tzarkan_0"] = true,
		["wh2_dlc14_def_cha_malus_darkblade_tzarkan_0_final_battle"] = true,
		["wh2_dlc14_def_cha_malus_darkblade_tzarkan_1"] = true,
		["wh2_dlc14_def_cha_master_0"] = true,
		["wh2_dlc14_def_cha_master_1"] = true,
		["wh2_dlc14_def_cha_master_2"] = true,
		["wh2_dlc14_def_cha_master_3"] = true,
		["wh2_dlc14_def_cha_master_4"] = true,
		["wh2_dlc14_skv_cha_deathmaster_snikch_0"] = true,
		["wh2_dlc14_skv_cha_deathmaster_snikch_tzarkan_0"] = true,
		["wh2_dlc14_skv_cha_eshin_sorcerer_0"] = true,
		["wh2_dlc14_skv_cha_master_assassin_0"] = true,
		["wh2_dlc15_grn_cha_grom_the_paunch_0"] = true,
		["wh2_dlc15_grn_cha_night_goblin_warboss_0_big"] = true,
		["wh2_dlc15_grn_cha_river_troll_hag_0"] = true,
		["wh2_dlc15_hef_cha_alastar_1"] = true,
		["wh2_dlc15_hef_cha_archmage_beasts_0"] = true,
		["wh2_dlc15_hef_cha_archmage_beasts_1"] = true,
		["wh2_dlc15_hef_cha_archmage_beasts_2"] = true,
		["wh2_dlc15_hef_cha_archmage_beasts_3"] = true,
		["wh2_dlc15_hef_cha_archmage_beasts_4"] = true,
		["wh2_dlc15_hef_cha_archmage_death_0"] = true,
		["wh2_dlc15_hef_cha_archmage_death_1"] = true,
		["wh2_dlc15_hef_cha_archmage_death_2"] = true,
		["wh2_dlc15_hef_cha_archmage_death_3"] = true,
		["wh2_dlc15_hef_cha_archmage_death_4"] = true,
		["wh2_dlc15_hef_cha_archmage_fire_0"] = true,
		["wh2_dlc15_hef_cha_archmage_fire_1"] = true,
		["wh2_dlc15_hef_cha_archmage_fire_2"] = true,
		["wh2_dlc15_hef_cha_archmage_fire_3"] = true,
		["wh2_dlc15_hef_cha_archmage_fire_4"] = true,
		["wh2_dlc15_hef_cha_archmage_heavens_0"] = true,
		["wh2_dlc15_hef_cha_archmage_heavens_1"] = true,
		["wh2_dlc15_hef_cha_archmage_heavens_2"] = true,
		["wh2_dlc15_hef_cha_archmage_heavens_3"] = true,
		["wh2_dlc15_hef_cha_archmage_heavens_4"] = true,
		["wh2_dlc15_hef_cha_archmage_high_0"] = true,
		["wh2_dlc15_hef_cha_archmage_high_1"] = true,
		["wh2_dlc15_hef_cha_archmage_high_2"] = true,
		["wh2_dlc15_hef_cha_archmage_high_3"] = true,
		["wh2_dlc15_hef_cha_archmage_high_4"] = true,
		["wh2_dlc15_hef_cha_archmage_life_0"] = true,
		["wh2_dlc15_hef_cha_archmage_life_1"] = true,
		["wh2_dlc15_hef_cha_archmage_life_2"] = true,
		["wh2_dlc15_hef_cha_archmage_life_3"] = true,
		["wh2_dlc15_hef_cha_archmage_life_4"] = true,
		["wh2_dlc15_hef_cha_archmage_light_0"] = true,
		["wh2_dlc15_hef_cha_archmage_light_1"] = true,
		["wh2_dlc15_hef_cha_archmage_light_2"] = true,
		["wh2_dlc15_hef_cha_archmage_light_3"] = true,
		["wh2_dlc15_hef_cha_archmage_light_4"] = true,
		["wh2_dlc15_hef_cha_archmage_metal_0"] = true,
		["wh2_dlc15_hef_cha_archmage_metal_1"] = true,
		["wh2_dlc15_hef_cha_archmage_metal_2"] = true,
		["wh2_dlc15_hef_cha_archmage_metal_3"] = true,
		["wh2_dlc15_hef_cha_archmage_metal_4"] = true,
		["wh2_dlc15_hef_cha_archmage_shadows_0"] = true,
		["wh2_dlc15_hef_cha_archmage_shadows_1"] = true,
		["wh2_dlc15_hef_cha_archmage_shadows_2"] = true,
		["wh2_dlc15_hef_cha_archmage_shadows_3"] = true,
		["wh2_dlc15_hef_cha_archmage_shadows_4"] = true,
		["wh2_dlc15_hef_cha_eltharion_the_grim_0"] = true,
		["wh2_dlc15_hef_cha_eltharion_the_grim_1"] = true,
		["wh2_dlc15_hef_cha_eltharion_the_grim_2"] = true,
		["wh2_dlc15_hef_cha_imrik_0"] = true,
		["wh2_dlc15_hef_cha_imrik_1"] = true,
		["wh2_dlc15_hef_cha_imrik_2"] = true,
		["wh2_dlc15_hef_cha_mage_beasts_0"] = true,
		["wh2_dlc15_hef_cha_mage_beasts_1"] = true,
		["wh2_dlc15_hef_cha_mage_beasts_2"] = true,
		["wh2_dlc15_hef_cha_mage_death_0"] = true,
		["wh2_dlc15_hef_cha_mage_death_1"] = true,
		["wh2_dlc15_hef_cha_mage_death_2"] = true,
		["wh2_dlc15_hef_cha_mage_fire_0"] = true,
		["wh2_dlc15_hef_cha_mage_fire_1"] = true,
		["wh2_dlc15_hef_cha_mage_fire_2"] = true,
		["wh2_dlc15_hef_cha_mage_fire_3"] = true,
		["wh2_dlc15_hef_cha_mage_metal_0"] = true,
		["wh2_dlc15_hef_cha_mage_metal_1"] = true,
		["wh2_dlc15_hef_cha_mage_metal_2"] = true,
		["wh2_dlc15_hef_cha_prince_6"] = true,
		["wh2_dlc15_hef_cha_princess_6"] = true,
		["wh2_dlc15_hef_cha_teclis_2"] = true,
		["wh2_dlc16_skv_cha_chieftain_0"] = true,
		["wh2_dlc16_skv_cha_chieftain_1"] = true,
		["wh2_dlc16_skv_cha_ghoritch_0"] = true,
		["wh2_dlc16_skv_cha_ghoritch_0_boss"] = true,
		["wh2_dlc16_skv_cha_packmaster_0"] = true,
		["wh2_dlc16_skv_cha_packmaster_2"] = true,
		["wh2_dlc16_skv_cha_throt_the_unclean_0"] = true,
		["wh2_dlc16_skv_cha_throt_the_unclean_2"] = true,
		["wh2_dlc16_skv_cha_warlord_2"] = true,
		["wh2_dlc16_wef_cha_ancient_treeman_coeddil_0"] = true,
		["wh2_dlc16_wef_cha_ariel_0"] = true,
		["wh2_dlc16_wef_cha_drycha_0"] = true,
		["wh2_dlc16_wef_cha_female_glade_lord_4"] = true,
		["wh2_dlc16_wef_cha_glade_lord_4"] = true,
		["wh2_dlc16_wef_cha_malicious_ancient_treeman_beasts_0"] = true,
		["wh2_dlc16_wef_cha_malicious_ancient_treeman_life_0"] = true,
		["wh2_dlc16_wef_cha_malicious_ancient_treeman_shadows_0"] = true,
		["wh2_dlc16_wef_cha_malicious_branchwraith_beasts_0"] = true,
		["wh2_dlc16_wef_cha_malicious_branchwraith_life_0"] = true,
		["wh2_dlc16_wef_cha_malicious_branchwraith_shadows_0"] = true,
		["wh2_dlc16_wef_cha_sisters_of_twilight_0"] = true,
		["wh2_dlc16_wef_cha_sisters_of_twilight_1"] = true,
		["wh2_dlc16_wef_cha_spellweaver_beasts_0"] = true,
		["wh2_dlc16_wef_cha_spellweaver_beasts_1"] = true,
		["wh2_dlc16_wef_cha_spellweaver_beasts_2"] = true,
		["wh2_dlc16_wef_cha_spellweaver_beasts_3"] = true,
		["wh2_dlc16_wef_cha_spellweaver_dark_0"] = true,
		["wh2_dlc16_wef_cha_spellweaver_dark_1"] = true,
		["wh2_dlc16_wef_cha_spellweaver_dark_2"] = true,
		["wh2_dlc16_wef_cha_spellweaver_dark_3"] = true,
		["wh2_dlc16_wef_cha_spellweaver_high_0"] = true,
		["wh2_dlc16_wef_cha_spellweaver_high_1"] = true,
		["wh2_dlc16_wef_cha_spellweaver_high_2"] = true,
		["wh2_dlc16_wef_cha_spellweaver_high_3"] = true,
		["wh2_dlc16_wef_cha_spellweaver_life_0"] = true,
		["wh2_dlc16_wef_cha_spellweaver_life_1"] = true,
		["wh2_dlc16_wef_cha_spellweaver_life_2"] = true,
		["wh2_dlc16_wef_cha_spellweaver_life_3"] = true,
		["wh2_dlc16_wef_cha_spellweaver_shadows_0"] = true,
		["wh2_dlc16_wef_cha_spellweaver_shadows_1"] = true,
		["wh2_dlc16_wef_cha_spellweaver_shadows_2"] = true,
		["wh2_dlc16_wef_cha_spellweaver_shadows_3"] = true,
		["wh2_dlc17_bst_cha_beastlord_2"] = true,
		["wh2_dlc17_bst_cha_bray_shaman_beasts_2"] = true,
		["wh2_dlc17_bst_cha_bray_shaman_death_2"] = true,
		["wh2_dlc17_bst_cha_bray_shaman_shadows_2"] = true,
		["wh2_dlc17_bst_cha_bray_shaman_wild_2"] = true,
		["wh2_dlc17_bst_cha_doombull_0"] = true,
		["wh2_dlc17_bst_cha_khazrak_one_eye_2"] = true,
		["wh2_dlc17_bst_cha_taurox_the_brass_bull_0"] = true,
		["wh2_dlc17_bst_cha_wargor_0"] = true,
		["wh2_dlc17_bst_cha_wargor_1"] = true,
		["wh2_dlc17_bst_cha_wargor_2"] = true,
		["wh2_dlc17_dwf_cha_thane_ghost_2"] = true,
		["wh2_dlc17_dwf_cha_thorek_ironbrow_0"] = true,
		["wh2_dlc17_dwf_cha_thorek_ironbrow_1"] = true,
		["wh2_dlc17_lzd_cha_oxyotl_0"] = true,
		["wh2_dlc17_lzd_cha_skink_oracle_troglodon_0"] = true,
		["wh2_main_def_cha_death_hag_0"] = true,
		["wh2_main_def_cha_death_hag_1"] = true,
		["wh2_main_def_cha_dreadlord_0"] = true,
		["wh2_main_def_cha_dreadlord_1"] = true,
		["wh2_main_def_cha_dreadlord_2"] = true,
		["wh2_main_def_cha_dreadlord_4"] = true,
		["wh2_main_def_cha_dreadlord_5"] = true,
		["wh2_main_def_cha_dreadlord_female_0"] = true,
		["wh2_main_def_cha_dreadlord_female_1"] = true,
		["wh2_main_def_cha_dreadlord_female_2"] = true,
		["wh2_main_def_cha_dreadlord_female_4"] = true,
		["wh2_main_def_cha_dreadlord_female_5"] = true,
		["wh2_main_def_cha_khainite_assassin_0"] = true,
		["wh2_main_def_cha_malekith_0"] = true,
		["wh2_main_def_cha_malekith_1"] = true,
		["wh2_main_def_cha_malekith_2"] = true,
		["wh2_main_def_cha_malekith_3"] = true,
		["wh2_main_def_cha_morathi_0"] = true,
		["wh2_main_def_cha_morathi_1"] = true,
		["wh2_main_def_cha_sorceress_dark_0"] = true,
		["wh2_main_def_cha_sorceress_dark_1"] = true,
		["wh2_main_def_cha_sorceress_dark_2"] = true,
		["wh2_main_def_cha_sorceress_dark_3"] = true,
		["wh2_main_def_cha_sorceress_fire_0"] = true,
		["wh2_main_def_cha_sorceress_fire_1"] = true,
		["wh2_main_def_cha_sorceress_fire_2"] = true,
		["wh2_main_def_cha_sorceress_fire_3"] = true,
		["wh2_main_def_cha_sorceress_shadow_0"] = true,
		["wh2_main_def_cha_sorceress_shadow_1"] = true,
		["wh2_main_def_cha_sorceress_shadow_2"] = true,
		["wh2_main_def_cha_sorceress_shadow_3"] = true,
		["wh2_main_hef_cha_alastar_0"] = true,
		["wh2_main_hef_cha_alastar_3"] = true,
		["wh2_main_hef_cha_alastar_4"] = true,
		["wh2_main_hef_cha_alastar_5"] = true,
		["wh2_main_hef_cha_loremaster_of_hoeth_0"] = true,
		["wh2_main_hef_cha_mage_high_0"] = true,
		["wh2_main_hef_cha_mage_high_1"] = true,
		["wh2_main_hef_cha_mage_high_4"] = true,
		["wh2_main_hef_cha_mage_life_0"] = true,
		["wh2_main_hef_cha_mage_life_1"] = true,
		["wh2_main_hef_cha_mage_life_4"] = true,
		["wh2_main_hef_cha_mage_light_0"] = true,
		["wh2_main_hef_cha_mage_light_1"] = true,
		["wh2_main_hef_cha_mage_light_4"] = true,
		["wh2_main_hef_cha_noble_0"] = true,
		["wh2_main_hef_cha_noble_2"] = true,
		["wh2_main_hef_cha_noble_3"] = true,
		["wh2_main_hef_cha_noble_4"] = true,
		["wh2_main_hef_cha_prince_0"] = true,
		["wh2_main_hef_cha_prince_2"] = true,
		["wh2_main_hef_cha_prince_3"] = true,
		["wh2_main_hef_cha_prince_4"] = true,
		["wh2_main_hef_cha_prince_5"] = true,
		["wh2_main_hef_cha_princess_0"] = true,
		["wh2_main_hef_cha_princess_1"] = true,
		["wh2_main_hef_cha_princess_3"] = true,
		["wh2_main_hef_cha_princess_4"] = true,
		["wh2_main_hef_cha_princess_5"] = true,
		["wh2_main_hef_cha_teclis_0"] = true,
		["wh2_main_hef_cha_teclis_1"] = true,
		["wh2_main_hef_cha_tyrion_0"] = true,
		["wh2_main_hef_cha_tyrion_1"] = true,
		["wh2_main_lzd_cha_kroq_gar_0"] = true,
		["wh2_main_lzd_cha_kroq_gar_1"] = true,
		["wh2_main_lzd_cha_kroq_gar_2"] = true,
		["wh2_main_lzd_cha_kroq_gar_3"] = true,
		["wh2_main_lzd_cha_lord_mazdamundi_0"] = true,
		["wh2_main_lzd_cha_lord_mazdamundi_1"] = true,
		["wh2_main_lzd_cha_saurus_old_blood_0"] = true,
		["wh2_main_lzd_cha_saurus_old_blood_1"] = true,
		["wh2_main_lzd_cha_saurus_old_blood_2"] = true,
		["wh2_main_lzd_cha_saurus_scar_veteran_0"] = true,
		["wh2_main_lzd_cha_saurus_scar_veteran_1"] = true,
		["wh2_main_lzd_cha_saurus_scar_veteran_2"] = true,
		["wh2_main_lzd_cha_skink_chief_0"] = true,
		["wh2_main_lzd_cha_skink_chief_1"] = true,
		["wh2_main_lzd_cha_skink_chief_2"] = true,
		["wh2_main_lzd_cha_skink_chief_3"] = true,
		["wh2_main_lzd_cha_skink_priest_0_summoned"] = true,
		["wh2_main_lzd_cha_skink_priest_beasts_0"] = true,
		["wh2_main_lzd_cha_skink_priest_beasts_1"] = true,
		["wh2_main_lzd_cha_skink_priest_beasts_2"] = true,
		["wh2_main_lzd_cha_skink_priest_beasts_3"] = true,
		["wh2_main_lzd_cha_skink_priest_heavens_0"] = true,
		["wh2_main_lzd_cha_skink_priest_heavens_1"] = true,
		["wh2_main_lzd_cha_skink_priest_heavens_2"] = true,
		["wh2_main_lzd_cha_skink_priest_heavens_3"] = true,
		["wh2_main_lzd_cha_slann_mage_priest_campaign_0"] = true,
		["wh2_main_lzd_cha_slann_mage_priest_heavens_0"] = true,
		["wh2_main_lzd_cha_slann_mage_priest_high_0"] = true,
		["wh2_main_lzd_cha_slann_mage_priest_life_0_qb"] = true,
		["wh2_main_lzd_cha_slann_mage_priest_light_0"] = true,
		["wh2_main_skv_cha_assassin"] = true,
		["wh2_main_skv_cha_grey_seer_plague_0"] = true,
		["wh2_main_skv_cha_grey_seer_plague_1"] = true,
		["wh2_main_skv_cha_grey_seer_ruin_0"] = true,
		["wh2_main_skv_cha_grey_seer_ruin_1"] = true,
		["wh2_main_skv_cha_lord_skrolk"] = true,
		["wh2_main_skv_cha_plague_priest_0"] = true,
		["wh2_main_skv_cha_plague_priest_2"] = true,
		["wh2_main_skv_cha_queek_headtaker"] = true,
		["wh2_main_skv_cha_warlock_engineer"] = true,
		["wh2_main_skv_cha_warlord_0"] = true,
		["wh2_main_skv_cha_warlord_1"] = true,
		["wh2_pro07_emp_cha_wizard_death_0"] = true,
		["wh2_pro07_emp_cha_wizard_death_1"] = true,
		["wh2_pro07_emp_cha_wizard_death_2"] = true,
		["wh2_pro07_emp_cha_wizard_death_3"] = true,
		["wh2_pro08_neu_cha_felix"] = true,
		["wh2_pro08_neu_cha_gotrek"] = true,
		["wh2_pro09_grn_cha_black_orc_big_boss_0"] = true,
		["wh2_pro09_grn_cha_black_orc_big_boss_1"] = true,
		["wh2_twa01_grn_cha_goblin_great_shaman_3"] = true,
		["wh2_twa02_wef_cha_glade_captain_0"] = true,
		["wh2_twa02_wef_cha_glade_captain_1"] = true,
		["wh2_twa02_wef_cha_glade_captain_2"] = true,
		["wh2_twa02_wef_cha_glade_captain_3"] = true,
		["wh2_twa03_def_cha_rakarth_0"] = true,
		["wh2_twa03_def_cha_rakarth_1"] = true,
		["wh2_twa03_def_cha_rakarth_2"] = true,
		["wh2_twa03_def_cha_rakarth_3"] = true,
		["wh2_twa04_bst_cha_great_bray_shaman_beasts_0"] = true,
		["wh2_twa04_bst_cha_great_bray_shaman_beasts_1"] = true,
		["wh2_twa04_bst_cha_great_bray_shaman_beasts_2"] = true,
		["wh2_twa04_bst_cha_great_bray_shaman_death_0"] = true,
		["wh2_twa04_bst_cha_great_bray_shaman_death_1"] = true,
		["wh2_twa04_bst_cha_great_bray_shaman_death_2"] = true,
		["wh2_twa04_bst_cha_great_bray_shaman_shadows_0"] = true,
		["wh2_twa04_bst_cha_great_bray_shaman_shadows_1"] = true,
		["wh2_twa04_bst_cha_great_bray_shaman_shadows_2"] = true,
		["wh2_twa04_bst_cha_great_bray_shaman_wild_0"] = true,
		["wh2_twa04_bst_cha_great_bray_shaman_wild_1"] = true,
		["wh2_twa04_bst_cha_great_bray_shaman_wild_2"] = true,
		["wh3_cp1_cth_cha_bhashiva"] = true,
		["wh3_cp1_cth_cha_clawspeaker_beasts"] = true,
		["wh3_cp1_cth_cha_clawspeaker_life"] = true,
		["wh3_cp1_cth_cha_clawspeaker_shadows"] = true,
		["wh3_cp1_cth_cha_sawai"] = true,
		["wh3_cp1_cth_cha_taoyan"] = true,
		["wh3_cp1_tze_cha_qb_exalted_lord_of_change_boss"] = true,
		["wh3_dlc20_chs_cha_chaos_lord_mkho"] = true,
		["wh3_dlc20_chs_cha_chaos_lord_mkho_chaos_steed"] = true,
		["wh3_dlc20_chs_cha_chaos_lord_mkho_gorebeast_chariot"] = true,
		["wh3_dlc20_chs_cha_chaos_lord_mkho_juggernaut"] = true,
		["wh3_dlc20_chs_cha_chaos_lord_msla"] = true,
		["wh3_dlc20_chs_cha_chaos_lord_msla_chaos_chariot"] = true,
		["wh3_dlc20_chs_cha_chaos_lord_msla_chaos_steed"] = true,
		["wh3_dlc20_chs_cha_chaos_sorcerer_death_warshrine"] = true,
		["wh3_dlc20_chs_cha_chaos_sorcerer_fire_warshrine"] = true,
		["wh3_dlc20_chs_cha_chaos_sorcerer_lord_death_mnur"] = true,
		["wh3_dlc20_chs_cha_chaos_sorcerer_lord_death_mnur_chaos_steed"] = true,
		["wh3_dlc20_chs_cha_chaos_sorcerer_lord_death_mnur_warshrine"] = true,
		["wh3_dlc20_chs_cha_chaos_sorcerer_lord_death_warshrine"] = true,
		["wh3_dlc20_chs_cha_chaos_sorcerer_lord_fire_warshrine"] = true,
		["wh3_dlc20_chs_cha_chaos_sorcerer_lord_metal_mtze"] = true,
		["wh3_dlc20_chs_cha_chaos_sorcerer_lord_metal_mtze_chaos_steed"] = true,
		["wh3_dlc20_chs_cha_chaos_sorcerer_lord_metal_mtze_disc"] = true,
		["wh3_dlc20_chs_cha_chaos_sorcerer_lord_metal_mtze_warshrine"] = true,
		["wh3_dlc20_chs_cha_chaos_sorcerer_lord_metal_warshrine"] = true,
		["wh3_dlc20_chs_cha_chaos_sorcerer_lord_nurgle_mnur"] = true,
		["wh3_dlc20_chs_cha_chaos_sorcerer_lord_nurgle_mnur_chaos_steed"] = true,
		["wh3_dlc20_chs_cha_chaos_sorcerer_lord_nurgle_mnur_warshrine"] = true,
		["wh3_dlc20_chs_cha_chaos_sorcerer_lord_shadows_warshrine"] = true,
		["wh3_dlc20_chs_cha_chaos_sorcerer_lord_tzeentch_mtze"] = true,
		["wh3_dlc20_chs_cha_chaos_sorcerer_lord_tzeentch_mtze_chaos_steed"] = true,
		["wh3_dlc20_chs_cha_chaos_sorcerer_lord_tzeentch_mtze_disc"] = true,
		["wh3_dlc20_chs_cha_chaos_sorcerer_lord_tzeentch_mtze_warshrine"] = true,
		["wh3_dlc20_chs_cha_chaos_sorcerer_metal_mtze"] = true,
		["wh3_dlc20_chs_cha_chaos_sorcerer_metal_mtze_chaos_steed"] = true,
		["wh3_dlc20_chs_cha_chaos_sorcerer_metal_mtze_disc"] = true,
		["wh3_dlc20_chs_cha_chaos_sorcerer_metal_mtze_warshrine"] = true,
		["wh3_dlc20_chs_cha_chaos_sorcerer_metal_warshrine"] = true,
		["wh3_dlc20_chs_cha_chaos_sorcerer_shadows_msla"] = true,
		["wh3_dlc20_chs_cha_chaos_sorcerer_shadows_msla_chaos_steed"] = true,
		["wh3_dlc20_chs_cha_chaos_sorcerer_shadows_msla_warshrine"] = true,
		["wh3_dlc20_chs_cha_chaos_sorcerer_shadows_warshrine"] = true,
		["wh3_dlc20_chs_cha_chaos_sorcerer_slaanesh_msla"] = true,
		["wh3_dlc20_chs_cha_chaos_sorcerer_slaanesh_msla_chaos_steed"] = true,
		["wh3_dlc20_chs_cha_chaos_sorcerer_slaanesh_msla_warshrine"] = true,
		["wh3_dlc20_chs_cha_chaos_sorcerer_tzeentch_mtze"] = true,
		["wh3_dlc20_chs_cha_chaos_sorcerer_tzeentch_mtze_chaos_steed"] = true,
		["wh3_dlc20_chs_cha_chaos_sorcerer_tzeentch_mtze_disc"] = true,
		["wh3_dlc20_chs_cha_chaos_sorcerer_tzeentch_mtze_warshrine"] = true,
		["wh3_dlc20_chs_cha_cultist_msla_warshrine"] = true,
		["wh3_dlc20_chs_cha_daemon_prince"] = true,
		["wh3_dlc20_chs_cha_daemon_prince_mkho"] = true,
		["wh3_dlc20_chs_cha_daemon_prince_mnur"] = true,
		["wh3_dlc20_chs_cha_daemon_prince_msla"] = true,
		["wh3_dlc20_chs_cha_daemon_prince_mtze"] = true,
		["wh3_dlc20_chs_cha_exalted_hero_mkho"] = true,
		["wh3_dlc20_chs_cha_exalted_hero_mkho_chaos_steed"] = true,
		["wh3_dlc20_chs_cha_exalted_hero_mkho_gorebeast_chariot"] = true,
		["wh3_dlc20_chs_cha_exalted_hero_mkho_juggernaut"] = true,
		["wh3_dlc20_chs_cha_exalted_hero_mnur"] = true,
		["wh3_dlc20_chs_cha_exalted_hero_mnur_chaos_chariot"] = true,
		["wh3_dlc20_chs_cha_exalted_hero_mnur_chaos_steed"] = true,
		["wh3_dlc20_kho_cha_cultist_mkho_warshrine"] = true,
		["wh3_dlc20_kho_cha_valkia"] = true,
		["wh3_dlc20_nur_cha_cultist_mnur_warshrine"] = true,
		["wh3_dlc20_nur_cha_festus"] = true,
		["wh3_dlc20_sla_cha_azazel"] = true,
		["wh3_dlc20_tze_cha_cultist_mtze_warshrine"] = true,
		["wh3_dlc20_tze_cha_vilitch"] = true,
		["wh3_dlc23_chd_cha_astragoth_ironhand"] = true,
		["wh3_dlc23_chd_cha_bull_centaur_taurruk"] = true,
		["wh3_dlc23_chd_cha_daemonsmith_sorcerer_death"] = true,
		["wh3_dlc23_chd_cha_daemonsmith_sorcerer_death_bale_taurus"] = true,
		["wh3_dlc23_chd_cha_daemonsmith_sorcerer_death_great_taurus"] = true,
		["wh3_dlc23_chd_cha_daemonsmith_sorcerer_death_lammasu"] = true,
		["wh3_dlc23_chd_cha_daemonsmith_sorcerer_fire"] = true,
		["wh3_dlc23_chd_cha_daemonsmith_sorcerer_fire_bale_taurus"] = true,
		["wh3_dlc23_chd_cha_daemonsmith_sorcerer_fire_great_taurus"] = true,
		["wh3_dlc23_chd_cha_daemonsmith_sorcerer_fire_lammasu"] = true,
		["wh3_dlc23_chd_cha_daemonsmith_sorcerer_hashut"] = true,
		["wh3_dlc23_chd_cha_daemonsmith_sorcerer_hashut_bale_taurus"] = true,
		["wh3_dlc23_chd_cha_daemonsmith_sorcerer_hashut_great_taurus"] = true,
		["wh3_dlc23_chd_cha_daemonsmith_sorcerer_hashut_lammasu"] = true,
		["wh3_dlc23_chd_cha_daemonsmith_sorcerer_metal"] = true,
		["wh3_dlc23_chd_cha_daemonsmith_sorcerer_metal_bale_taurus"] = true,
		["wh3_dlc23_chd_cha_daemonsmith_sorcerer_metal_great_taurus"] = true,
		["wh3_dlc23_chd_cha_daemonsmith_sorcerer_metal_lammasu"] = true,
		["wh3_dlc23_chd_cha_drazhoath_the_ashen"] = true,
		["wh3_dlc23_chd_cha_drazhoath_the_ashen_bale_taurus_cinderbreath"] = true,
		["wh3_dlc23_chd_cha_gorduz_backstabber"] = true,
		["wh3_dlc23_chd_cha_gorduz_backstabber_giant_wolf"] = true,
		["wh3_dlc23_chd_cha_infernal_castellan"] = true,
		["wh3_dlc23_chd_cha_overseer"] = true,
		["wh3_dlc23_chd_cha_overseer_great_taurus"] = true,
		["wh3_dlc23_chd_cha_overseer_lammasu"] = true,
		["wh3_dlc23_chd_cha_sorcerer_prophet_death"] = true,
		["wh3_dlc23_chd_cha_sorcerer_prophet_death_bale_taurus"] = true,
		["wh3_dlc23_chd_cha_sorcerer_prophet_death_great_taurus"] = true,
		["wh3_dlc23_chd_cha_sorcerer_prophet_death_lammasu"] = true,
		["wh3_dlc23_chd_cha_sorcerer_prophet_fire"] = true,
		["wh3_dlc23_chd_cha_sorcerer_prophet_fire_bale_taurus"] = true,
		["wh3_dlc23_chd_cha_sorcerer_prophet_fire_great_taurus"] = true,
		["wh3_dlc23_chd_cha_sorcerer_prophet_fire_lammasu"] = true,
		["wh3_dlc23_chd_cha_sorcerer_prophet_hashut"] = true,
		["wh3_dlc23_chd_cha_sorcerer_prophet_hashut_bale_taurus"] = true,
		["wh3_dlc23_chd_cha_sorcerer_prophet_hashut_great_taurus"] = true,
		["wh3_dlc23_chd_cha_sorcerer_prophet_hashut_lammasu"] = true,
		["wh3_dlc23_chd_cha_sorcerer_prophet_metal"] = true,
		["wh3_dlc23_chd_cha_sorcerer_prophet_metal_bale_taurus"] = true,
		["wh3_dlc23_chd_cha_sorcerer_prophet_metal_great_taurus"] = true,
		["wh3_dlc23_chd_cha_sorcerer_prophet_metal_lammasu"] = true,
		["wh3_dlc23_chd_cha_zhatan_the_black"] = true,
		["wh3_dlc23_chd_cha_zhatan_the_black_great_taurus"] = true,
		["wh3_dlc23_chd_cha_zhatan_the_black_lammasu"] = true,
		["wh3_dlc23_neu_cha_ulrika"] = true,
		["wh3_dlc23_neu_cha_ulrika_warhorse"] = true,
		["wh3_dlc24_chs_cha_chaos_lord_mtze"] = true,
		["wh3_dlc24_chs_cha_chaos_lord_mtze_chaos_chariot"] = true,
		["wh3_dlc24_chs_cha_chaos_lord_mtze_chaos_steed"] = true,
		["wh3_dlc24_chs_cha_chaos_lord_mtze_disc"] = true,
		["wh3_dlc24_chs_cha_exalted_hero_mtze"] = true,
		["wh3_dlc24_chs_cha_exalted_hero_mtze_chaos_chariot"] = true,
		["wh3_dlc24_chs_cha_exalted_hero_mtze_chaos_steed"] = true,
		["wh3_dlc24_chs_cha_exalted_hero_mtze_disc"] = true,
		["wh3_dlc24_cth_cha_astromancer_great_moon_bird"] = true,
		["wh3_dlc24_cth_cha_celestial_general_yang"] = true,
		["wh3_dlc24_cth_cha_celestial_general_yang_cathayan_horse"] = true,
		["wh3_dlc24_cth_cha_celestial_general_yang_celestial_lion"] = true,
		["wh3_dlc24_cth_cha_celestial_general_yang_longma"] = true,
		["wh3_dlc24_cth_cha_gate_master"] = true,
		["wh3_dlc24_cth_cha_gate_master_warhorse"] = true,
		["wh3_dlc24_cth_cha_saytang_the_watcher"] = true,
		["wh3_dlc24_cth_cha_yuan_bo_dragon"] = true,
		["wh3_dlc24_cth_cha_yuan_bo_human"] = true,
		["wh3_dlc24_grn_cha_grimgor_ironhide_quest_battle"] = true,
		["wh3_dlc24_ksl_cha_druzhina"] = true,
		["wh3_dlc24_ksl_cha_druzhina_warhorse"] = true,
		["wh3_dlc24_ksl_cha_golden_knight"] = true,
		["wh3_dlc24_ksl_cha_golden_knight_warhorse"] = true,
		["wh3_dlc24_ksl_cha_hag_witch_beast"] = true,
		["wh3_dlc24_ksl_cha_hag_witch_death"] = true,
		["wh3_dlc24_ksl_cha_hag_witch_hag"] = true,
		["wh3_dlc24_ksl_cha_hag_witch_shadow"] = true,
		["wh3_dlc24_ksl_cha_ice_witch_ice_frost_wyrm"] = true,
		["wh3_dlc24_ksl_cha_ice_witch_tempest_frost_wyrm"] = true,
		["wh3_dlc24_ksl_cha_katarin_frost_wyrm"] = true,
		["wh3_dlc24_ksl_cha_katarin_ice_court_sled"] = true,
		["wh3_dlc24_ksl_cha_mother_ostankya"] = true,
		["wh3_dlc24_tze_cha_aekold_helbrass"] = true,
		["wh3_dlc24_tze_cha_blue_scribes"] = true,
		["wh3_dlc24_tze_cha_changeling"] = true,
		["wh3_dlc24_tze_cha_changeling_quest_battle"] = true,
		["wh3_dlc24_tze_cha_changeling_summoned_0"] = true,
		["wh3_dlc25_chs_cha_chaos_lord_mnur"] = true,
		["wh3_dlc25_chs_cha_chaos_lord_mnur_chaos_chariot"] = true,
		["wh3_dlc25_chs_cha_chaos_lord_mnur_chaos_steed"] = true,
		["wh3_dlc25_chs_cha_chaos_lord_mnur_rot_beast"] = true,
		["wh3_dlc25_chs_cha_chaos_sorcerer_death_mnur"] = true,
		["wh3_dlc25_chs_cha_chaos_sorcerer_death_mnur_chaos_steed"] = true,
		["wh3_dlc25_chs_cha_chaos_sorcerer_death_mnur_rot_beast"] = true,
		["wh3_dlc25_chs_cha_chaos_sorcerer_death_mnur_warshrine"] = true,
		["wh3_dlc25_chs_cha_chaos_sorcerer_lord_death_mnur_rot_beast"] = true,
		["wh3_dlc25_chs_cha_chaos_sorcerer_lord_nurgle_mnur_rot_beast"] = true,
		["wh3_dlc25_chs_cha_chaos_sorcerer_nurgle_mnur"] = true,
		["wh3_dlc25_chs_cha_chaos_sorcerer_nurgle_mnur_chaos_steed"] = true,
		["wh3_dlc25_chs_cha_chaos_sorcerer_nurgle_mnur_rot_beast"] = true,
		["wh3_dlc25_chs_cha_chaos_sorcerer_nurgle_mnur_warshrine"] = true,
		["wh3_dlc25_chs_cha_exalted_hero_mnur_rot_beast"] = true,
		["wh3_dlc25_dwf_cha_daemon_slayer"] = true,
		["wh3_dlc25_dwf_cha_dragon_slayer"] = true,
		["wh3_dlc25_dwf_cha_garagrim_ironfist"] = true,
		["wh3_dlc25_dwf_cha_malakai_makaisson"] = true,
		["wh3_dlc25_emp_cha_elspeth_von_draken"] = true,
		["wh3_dlc25_emp_cha_elspeth_von_draken_carmine_dragon"] = true,
		["wh3_dlc25_emp_cha_elspeth_von_draken_warhorse"] = true,
		["wh3_dlc25_emp_cha_engineer"] = true,
		["wh3_dlc25_emp_cha_engineer_mechanical_steed"] = true,
		["wh3_dlc25_emp_cha_engineer_warhorse"] = true,
		["wh3_dlc25_emp_cha_master_engineer"] = true,
		["wh3_dlc25_emp_cha_master_engineer_mechanical_steed"] = true,
		["wh3_dlc25_emp_cha_master_engineer_steam_tank"] = true,
		["wh3_dlc25_emp_cha_master_engineer_warhorse"] = true,
		["wh3_dlc25_emp_cha_theodore_bruckner"] = true,
		["wh3_dlc25_emp_cha_theodore_bruckner_demigryph_reaper"] = true,
		["wh3_dlc25_emp_cha_wizard_metal"] = true,
		["wh3_dlc25_emp_cha_wizard_metal_pegasus"] = true,
		["wh3_dlc25_emp_cha_wizard_metal_warhorse"] = true,
		["wh3_dlc25_nur_cha_bray_shaman_wild_chieftain"] = true,
		["wh3_dlc25_nur_cha_bray_shaman_wild_chieftain_razorgor_chariot"] = true,
		["wh3_dlc25_nur_cha_bray_shaman_wild_chieftain_tuskgor_chariot"] = true,
		["wh3_dlc25_nur_cha_epidemius"] = true,
		["wh3_dlc25_nur_cha_exalted_great_unclean_one_nurgle_qb_boss"] = true,
		["wh3_dlc25_nur_cha_exalted_hero_chieftain"] = true,
		["wh3_dlc25_nur_cha_exalted_hero_chieftain_chaos_chariot"] = true,
		["wh3_dlc25_nur_cha_exalted_hero_chieftain_chaos_dragon"] = true,
		["wh3_dlc25_nur_cha_exalted_hero_chieftain_chaos_steed"] = true,
		["wh3_dlc25_nur_cha_fimir_balefiend_shadow_chieftain"] = true,
		["wh3_dlc25_nur_cha_infernal_castellan_chieftain"] = true,
		["wh3_dlc25_nur_cha_kayzk_the_befouled"] = true,
		["wh3_dlc25_nur_cha_skin_wolf_werekin_chieftain"] = true,
		["wh3_dlc25_nur_cha_tamurkhan"] = true,
		["wh3_dlc25_nur_cha_tamurkhan_bubebolos"] = true,
		["wh3_dlc26_grn_cha_gorbad_ironclaw"] = true,
		["wh3_dlc26_grn_cha_gorbad_ironclaw_gnarla"] = true,
		["wh3_dlc26_grn_cha_night_goblin_big_boss"] = true,
		["wh3_dlc26_grn_cha_night_goblin_big_boss_squig"] = true,
		["wh3_dlc26_grn_cha_savage_orc_great_shaman"] = true,
		["wh3_dlc26_grn_cha_savage_orc_great_shaman_boar"] = true,
		["wh3_dlc26_grn_cha_savage_orc_great_shaman_wyvern"] = true,
		["wh3_dlc26_grn_cha_snagla_grobspit"] = true,
		["wh3_dlc26_kho_cha_arbaal"] = true,
		["wh3_dlc26_kho_cha_arbaal_flesh_hound"] = true,
		["wh3_dlc26_kho_cha_bloodspeaker"] = true,
		["wh3_dlc26_kho_cha_bloodspeaker_chaos_steed"] = true,
		["wh3_dlc26_kho_cha_bloodspeaker_warshrine"] = true,
		["wh3_dlc26_kho_cha_scyla_anfingrimm"] = true,
		["wh3_dlc26_kho_cha_skarr_bloodwrath"] = true,
		["wh3_dlc26_kho_cha_skulltaker"] = true,
		["wh3_dlc26_kho_cha_skulltaker_bloodthrone"] = true,
		["wh3_dlc26_kho_cha_skulltaker_juggernaut"] = true,
		["wh3_dlc26_ogr_cha_bragg_the_gutsman"] = true,
		["wh3_dlc26_ogr_cha_bruiser"] = true,
		["wh3_dlc26_ogr_cha_butcher_death"] = true,
		["wh3_dlc26_ogr_cha_butcher_heavens"] = true,
		["wh3_dlc26_ogr_cha_golgfag_maneater"] = true,
		["wh3_dlc26_ogr_cha_paymaster"] = true,
		["wh3_dlc26_ogr_cha_slaughtermaster_death"] = true,
		["wh3_dlc26_ogr_cha_slaughtermaster_heavens"] = true,
		["wh3_dlc27_chs_cha_chaos_lord_msla_daemonic_steed"] = true,
		["wh3_dlc27_chs_cha_chaos_sorcerer_shadows_msla_daemonic_steed"] = true,
		["wh3_dlc27_chs_cha_chaos_sorcerer_slaanesh_msla_daemonic_steed"] = true,
		["wh3_dlc27_chs_cha_daemon_prince_mkho_qb"] = true,
		["wh3_dlc27_chs_cha_exalted_hero_msla"] = true,
		["wh3_dlc27_chs_cha_exalted_hero_msla_chaos_chariot"] = true,
		["wh3_dlc27_chs_cha_exalted_hero_msla_chaos_steed"] = true,
		["wh3_dlc27_chs_cha_exalted_hero_msla_daemonic_steed"] = true,
		["wh3_dlc27_chs_cha_sorcerer_lord_shadows_msla"] = true,
		["wh3_dlc27_chs_cha_sorcerer_lord_shadows_msla_chaos_steed"] = true,
		["wh3_dlc27_chs_cha_sorcerer_lord_shadows_msla_daemonic_steed"] = true,
		["wh3_dlc27_chs_cha_sorcerer_lord_shadows_msla_warshrine"] = true,
		["wh3_dlc27_chs_cha_sorcerer_lord_slaanesh_msla"] = true,
		["wh3_dlc27_chs_cha_sorcerer_lord_slaanesh_msla_chaos_steed"] = true,
		["wh3_dlc27_chs_cha_sorcerer_lord_slaanesh_msla_daemonic_steed"] = true,
		["wh3_dlc27_chs_cha_sorcerer_lord_slaanesh_msla_warshrine"] = true,
		["wh3_dlc27_hef_cha_caradryan"] = true,
		["wh3_dlc27_hef_cha_caradryan_ashtari"] = true,
		["wh3_dlc27_hef_cha_caradryan_chariot"] = true,
		["wh3_dlc27_hef_cha_caradryan_steed"] = true,
		["wh3_dlc27_hef_cha_mist_mage"] = true,
		["wh3_dlc27_hef_cha_mist_mage_eagle"] = true,
		["wh3_dlc27_hef_cha_mist_mage_skycutter"] = true,
		["wh3_dlc27_hef_cha_sea_helm"] = true,
		["wh3_dlc27_hef_cha_sea_helm_eagle"] = true,
		["wh3_dlc27_hef_cha_sea_helm_skycutter"] = true,
		["wh3_dlc27_hef_cha_sea_lord_aislinn"] = true,
		["wh3_dlc27_hef_cha_sea_lord_aislinn_dragon"] = true,
		["wh3_dlc27_hef_cha_sea_lord_aislinn_skycutter"] = true,
		["wh3_dlc27_nor_cha_beorg_bearstruck"] = true,
		["wh3_dlc27_nor_cha_fimir_noble"] = true,
		["wh3_dlc27_nor_cha_great_shaman_sorcerer_death"] = true,
		["wh3_dlc27_nor_cha_great_shaman_sorcerer_death_chariot"] = true,
		["wh3_dlc27_nor_cha_great_shaman_sorcerer_death_mammoth"] = true,
		["wh3_dlc27_nor_cha_great_shaman_sorcerer_death_warhorse"] = true,
		["wh3_dlc27_nor_cha_great_shaman_sorcerer_fire"] = true,
		["wh3_dlc27_nor_cha_great_shaman_sorcerer_fire_chariot"] = true,
		["wh3_dlc27_nor_cha_great_shaman_sorcerer_fire_mammoth"] = true,
		["wh3_dlc27_nor_cha_great_shaman_sorcerer_fire_warhorse"] = true,
		["wh3_dlc27_nor_cha_great_shaman_sorcerer_metal"] = true,
		["wh3_dlc27_nor_cha_great_shaman_sorcerer_metal_chariot"] = true,
		["wh3_dlc27_nor_cha_great_shaman_sorcerer_metal_mammoth"] = true,
		["wh3_dlc27_nor_cha_great_shaman_sorcerer_metal_warhorse"] = true,
		["wh3_dlc27_nor_cha_sayl_the_faithless"] = true,
		["wh3_dlc27_nor_cha_sayl_the_faithless_chariot"] = true,
		["wh3_dlc27_nor_cha_sayl_the_faithless_mammoth"] = true,
		["wh3_dlc27_nor_cha_sayl_the_faithless_warhorse"] = true,
		["wh3_dlc27_nor_cha_shaman_sorcerer_death_2_summoned"] = true,
		["wh3_dlc27_nor_cha_shaman_sorcerer_fire_2_summoned"] = true,
		["wh3_dlc27_nor_cha_shaman_sorcerer_metal_2_summoned"] = true,
		["wh3_dlc27_sla_cha_alluress_shadow_daemonic_steed"] = true,
		["wh3_dlc27_sla_cha_alluress_slaanesh_daemonic_steed"] = true,
		["wh3_dlc27_sla_cha_dechala"] = true,
		["wh3_dlc27_sla_cha_druchii_anointed"] = true,
		["wh3_dlc27_sla_cha_druchii_anointed_cold_one"] = true,
		["wh3_dlc27_sla_cha_druchii_anointed_daemonic_steed"] = true,
		["wh3_dlc27_sla_cha_herald_of_slaanesh_shadow_daemonic_steed"] = true,
		["wh3_dlc27_sla_cha_herald_of_slaanesh_slaanesh_daemonic_steed"] = true,
		["wh3_dlc27_sla_cha_masque_of_slaanesh"] = true,
		["wh3_dlc27_sla_cha_styrkaar_the_sortsvinaer"] = true,
		["wh3_dlc27_sla_cha_styrkaar_the_sortsvinaer_daemonic_steed"] = true,
		["wh3_dlc27_sla_cha_styrkaar_the_sortsvinaer_steed_of_slaanesh"] = true,
		["wh3_dlc29_chs_cha_bloab"] = true,
		["wh3_dlc29_chs_cha_bloab_bilespurter"] = true,
		["wh3_dlc29_chs_cha_glottkin"] = true,
		["wh3_dlc29_chs_cha_gutrot_spume"] = true,
		["wh3_dlc29_chs_cha_gutrot_spume_warshrine"] = true,
		["wh3_dlc29_chs_cha_morbidex"] = true,
		["wh3_dlc29_chs_cha_morbidex_tripletongue"] = true,
		["wh3_dlc29_chs_cha_orghotts"] = true,
		["wh3_dlc29_chs_cha_orghotts_whippermaw"] = true,
		["wh3_dlc29_chs_cha_plagues_champion_mnur_summoned"] = true,
		["wh3_dlc29_cst_cha_gunnery_wight_0_summoned"] = true,
		["wh3_dlc29_cst_cha_vampire_fleet_admiral_female_undeath"] = true,
		["wh3_dlc29_cst_cha_vampire_fleet_admiral_female_undeath_rotting_promethean"] = true,
		["wh3_dlc29_cst_cha_vampire_fleet_admiral_undeath"] = true,
		["wh3_dlc29_cst_cha_vampire_fleet_admiral_undeath_rotting_promethean"] = true,
		["wh3_dlc29_cst_cha_vampire_fleet_captain_undeath"] = true,
		["wh3_dlc29_cst_cha_vampire_fleet_captain_undeath_rotting_promethean"] = true,
		["wh3_dlc29_emp_cha_boris_todbringer_toddy_0"] = true,
		["wh3_dlc29_emp_cha_boris_todbringer_toddy_1"] = true,
		["wh3_dlc29_emp_cha_boris_todbringer_toddy_2"] = true,
		["wh3_dlc29_emp_cha_boris_todbringer_toddy_3"] = true,
		["wh3_dlc29_emp_cha_emil_valgeir"] = true,
		["wh3_dlc29_emp_cha_emil_valgeir_warhorse"] = true,
		["wh3_dlc29_emp_cha_priest_of_ulric"] = true,
		["wh3_dlc29_emp_cha_priest_of_ulric_warhorse"] = true,
		["wh3_dlc29_emp_cha_seneschal_of_the_white_wolf"] = true,
		["wh3_dlc29_emp_cha_seneschal_of_the_white_wolf_warhorse"] = true,
		["wh3_dlc29_qb_brt_cha_lord_warhorse"] = true,
		["wh3_dlc29_skv_cha_lord_skrolk_cauldron"] = true,
		["wh3_dlc29_skv_cha_plague_priest_cauldron"] = true,
		["wh3_dlc29_skv_cha_skreech_verminking"] = true,
		["wh3_dlc29_skv_cha_thanquol"] = true,
		["wh3_dlc29_skv_cha_thanquol_boneripper_warpfire_braziers"] = true,
		["wh3_dlc29_skv_cha_thanquol_boneripper_warpfire_projectors"] = true,
		["wh3_dlc29_skv_cha_verminlord_corruptor"] = true,
		["wh3_dlc29_skv_cha_verminlord_deceiver"] = true,
		["wh3_dlc29_skv_cha_verminlord_warbringer"] = true,
		["wh3_dlc29_skv_cha_verminlord_warpseer"] = true,
		["wh3_dlc29_tmb_cha_arkhan_dread_abyssal"] = true,
		["wh3_dlc29_tmb_cha_arkhan_the_black_mp"] = true,
		["wh3_dlc29_tmb_cha_arkhan_the_black_skeletal_steed_mp"] = true,
		["wh3_dlc29_tmb_cha_arkhan_the_black_skeleton_chariot_mp"] = true,
		["wh3_dlc29_tmb_cha_liche_high_priest_death"] = true,
		["wh3_dlc29_tmb_cha_liche_high_priest_death_skeletal_steed"] = true,
		["wh3_dlc29_tmb_cha_liche_high_priest_death_skeleton_chariot"] = true,
		["wh3_dlc29_tmb_cha_liche_high_priest_light"] = true,
		["wh3_dlc29_tmb_cha_liche_high_priest_light_skeletal_steed"] = true,
		["wh3_dlc29_tmb_cha_liche_high_priest_light_skeleton_chariot"] = true,
		["wh3_dlc29_tmb_cha_liche_high_priest_nehekhara"] = true,
		["wh3_dlc29_tmb_cha_liche_high_priest_nehekhara_skeletal_steed"] = true,
		["wh3_dlc29_tmb_cha_liche_high_priest_nehekhara_skeleton_chariot"] = true,
		["wh3_dlc29_tmb_cha_liche_high_priest_shadow"] = true,
		["wh3_dlc29_tmb_cha_liche_high_priest_shadow_skeletal_steed"] = true,
		["wh3_dlc29_tmb_cha_liche_high_priest_shadow_skeleton_chariot"] = true,
		["wh3_dlc29_tmb_cha_liche_high_priest_undeath"] = true,
		["wh3_dlc29_tmb_cha_liche_high_priest_undeath_skeletal_steed"] = true,
		["wh3_dlc29_tmb_cha_liche_priest_undeath"] = true,
		["wh3_dlc29_tmb_cha_liche_priest_undeath_skeletal_steed"] = true,
		["wh3_dlc29_tmb_cha_tomb_herald"] = true,
		["wh3_dlc29_tmb_cha_tomb_herald_skeletal_steed"] = true,
		["wh3_dlc29_tmb_cha_tomb_herald_skeleton_chariot"] = true,
		["wh3_dlc29_tmb_cha_tomb_prince_0_summoned"] = true,
		["wh3_dlc29_vmp_cha_bloodline_lahmian_lord_coven_throne"] = true,
		["wh3_dlc29_vmp_cha_dieter_helsnicht"] = true,
		["wh3_dlc29_vmp_cha_dieter_helsnicht_undead_manticore"] = true,
		["wh3_dlc29_vmp_cha_krell"] = true,
		["wh3_dlc29_vmp_cha_lahmian_vampire"] = true,
		["wh3_dlc29_vmp_cha_lahmian_vampire_barded_nightmare"] = true,
		["wh3_dlc29_vmp_cha_lahmian_vampire_hellsteed"] = true,
		["wh3_dlc29_vmp_cha_mannfred_von_carstein_barded_nightmare_mp"] = true,
		["wh3_dlc29_vmp_cha_mannfred_von_carstein_dread_abyssal"] = true,
		["wh3_dlc29_vmp_cha_mannfred_von_carstein_hellsteed_mp"] = true,
		["wh3_dlc29_vmp_cha_mannfred_von_carstein_mp"] = true,
		["wh3_dlc29_vmp_cha_mannfred_von_carstein_zombie_dragon_mp"] = true,
		["wh3_dlc29_vmp_cha_master_necromancer_undeath"] = true,
		["wh3_dlc29_vmp_cha_master_necromancer_undeath_barded_nightmare"] = true,
		["wh3_dlc29_vmp_cha_master_necromancer_undeath_corpse_cart"] = true,
		["wh3_dlc29_vmp_cha_master_necromancer_undeath_corpse_cart_balefire"] = true,
		["wh3_dlc29_vmp_cha_master_necromancer_undeath_corpse_cart_lodestone"] = true,
		["wh3_dlc29_vmp_cha_master_necromancer_undeath_hellsteed"] = true,
		["wh3_dlc29_vmp_cha_nagash"] = true,
		["wh3_dlc29_vmp_cha_nagash_vampire_lord"] = true,
		["wh3_dlc29_vmp_cha_nagash_vampire_lord_barded_nightmare"] = true,
		["wh3_dlc29_vmp_cha_nagash_vampire_lord_coven_throne"] = true,
		["wh3_dlc29_vmp_cha_nagash_vampire_lord_hellsteed"] = true,
		["wh3_dlc29_vmp_cha_nagash_vampire_lord_zombie_dragon"] = true,
		["wh3_dlc29_vmp_cha_necromancer_undeath"] = true,
		["wh3_dlc29_vmp_cha_necromancer_undeath_barded_nightmare"] = true,
		["wh3_dlc29_vmp_cha_necromancer_undeath_corpse_cart"] = true,
		["wh3_dlc29_vmp_cha_necromancer_undeath_corpse_cart_balefire"] = true,
		["wh3_dlc29_vmp_cha_necromancer_undeath_corpse_cart_lodestone"] = true,
		["wh3_dlc29_vmp_cha_neferata"] = true,
		["wh3_dlc29_vmp_cha_neferata_barded_nightmare"] = true,
		["wh3_dlc29_vmp_cha_neferata_barded_nightmare_mp"] = true,
		["wh3_dlc29_vmp_cha_neferata_coven_throne"] = true,
		["wh3_dlc29_vmp_cha_neferata_coven_throne_mp"] = true,
		["wh3_dlc29_vmp_cha_neferata_dread_abyssal"] = true,
		["wh3_dlc29_vmp_cha_neferata_hellsteed"] = true,
		["wh3_dlc29_vmp_cha_neferata_hellsteed_mp"] = true,
		["wh3_dlc29_vmp_cha_neferata_mp"] = true,
		["wh3_dlc29_vmp_cha_neferata_zombie_dragon"] = true,
		["wh3_dlc29_vmp_cha_neferata_zombie_dragon_mp"] = true,
		["wh3_dlc29_vmp_cha_vampire_lord_coven_throne"] = true,
		["wh3_dlc29_vmp_cha_walach_harkon"] = true,
		["wh3_dlc29_vmp_cha_walach_harkon_barded_nightmare"] = true,
		["wh3_dlc29_vmp_cha_wight_king_barded_nightmare_summoned"] = true,
		["wh3_main_cth_cha_alchemist_0"] = true,
		["wh3_main_cth_cha_alchemist_1"] = true,
		["wh3_main_cth_cha_alchemist_2"] = true,
		["wh3_main_cth_cha_astromancer_0"] = true,
		["wh3_main_cth_cha_astromancer_1"] = true,
		["wh3_main_cth_cha_astromancer_2"] = true,
		["wh3_main_cth_cha_dragon_blooded_shugengan_lord_yang_0"] = true,
		["wh3_main_cth_cha_dragon_blooded_shugengan_lord_yang_1"] = true,
		["wh3_main_cth_cha_dragon_blooded_shugengan_lord_yang_2"] = true,
		["wh3_main_cth_cha_dragon_blooded_shugengan_lord_yin_0"] = true,
		["wh3_main_cth_cha_dragon_blooded_shugengan_lord_yin_1"] = true,
		["wh3_main_cth_cha_dragon_blooded_shugengan_lord_yin_2"] = true,
		["wh3_main_cth_cha_iron_dragon_0"] = true,
		["wh3_main_cth_cha_iron_dragon_1"] = true,
		["wh3_main_cth_cha_lord_magistrate_0"] = true,
		["wh3_main_cth_cha_lord_magistrate_1"] = true,
		["wh3_main_cth_cha_lord_magistrate_2"] = true,
		["wh3_main_cth_cha_storm_dragon_0"] = true,
		["wh3_main_cth_cha_storm_dragon_1"] = true,
		["wh3_main_dae_cha_be_lakor_0"] = true,
		["wh3_main_dae_cha_daemon_prince_0"] = true,
		["wh3_main_dae_cha_daemon_prince_MP"] = true,
		["wh3_main_dae_cha_daemon_prince_khorne_0"] = true,
		["wh3_main_dae_cha_daemon_prince_khorne_MP"] = true,
		["wh3_main_dae_cha_daemon_prince_nurgle_0"] = true,
		["wh3_main_dae_cha_daemon_prince_nurgle_MP"] = true,
		["wh3_main_dae_cha_daemon_prince_slaanesh_0"] = true,
		["wh3_main_dae_cha_daemon_prince_slaanesh_MP"] = true,
		["wh3_main_dae_cha_daemon_prince_tzeentch_0"] = true,
		["wh3_main_dae_cha_daemon_prince_tzeentch_MP"] = true,
		["wh3_main_ie_nor_cha_exalted_great_unclean_one_burplesmirk_spewpit"] = true,
		["wh3_main_ie_nor_cha_exalted_hero_mkho_killgore_slaymaim"] = true,
		["wh3_main_kho_cha_bloodreaper_0"] = true,
		["wh3_main_kho_cha_bloodreaper_1"] = true,
		["wh3_main_kho_cha_bloodreaper_2"] = true,
		["wh3_main_kho_cha_cultist_0"] = true,
		["wh3_main_kho_cha_cultist_1"] = true,
		["wh3_main_kho_cha_exalted_bloodthirster_0"] = true,
		["wh3_main_kho_cha_herald_of_khorne_0"] = true,
		["wh3_main_kho_cha_herald_of_khorne_1"] = true,
		["wh3_main_kho_cha_herald_of_khorne_2"] = true,
		["wh3_main_kho_cha_skarbrand_0"] = true,
		["wh3_main_ksl_cha_ataman"] = true,
		["wh3_main_ksl_cha_boris_0"] = true,
		["wh3_main_ksl_cha_boris_1"] = true,
		["wh3_main_ksl_cha_boris_2"] = true,
		["wh3_main_ksl_cha_boyar_0"] = true,
		["wh3_main_ksl_cha_boyar_1"] = true,
		["wh3_main_ksl_cha_boyar_2"] = true,
		["wh3_main_ksl_cha_frost_maiden_ice_0"] = true,
		["wh3_main_ksl_cha_frost_maiden_ice_1"] = true,
		["wh3_main_ksl_cha_frost_maiden_ice_2"] = true,
		["wh3_main_ksl_cha_frost_maiden_tempest_0"] = true,
		["wh3_main_ksl_cha_frost_maiden_tempest_1"] = true,
		["wh3_main_ksl_cha_frost_maiden_tempest_2"] = true,
		["wh3_main_ksl_cha_ice_witch_ice_0"] = true,
		["wh3_main_ksl_cha_ice_witch_ice_1"] = true,
		["wh3_main_ksl_cha_ice_witch_ice_2"] = true,
		["wh3_main_ksl_cha_ice_witch_tempest_0"] = true,
		["wh3_main_ksl_cha_ice_witch_tempest_1"] = true,
		["wh3_main_ksl_cha_ice_witch_tempest_2"] = true,
		["wh3_main_ksl_cha_katarin_0"] = true,
		["wh3_main_ksl_cha_katarin_1"] = true,
		["wh3_main_ksl_cha_katarin_2"] = true,
		["wh3_main_ksl_cha_kostaltyn_0"] = true,
		["wh3_main_ksl_cha_kostaltyn_1"] = true,
		["wh3_main_ksl_cha_kostaltyn_2"] = true,
		["wh3_main_ksl_cha_patriarch_0"] = true,
		["wh3_main_ksl_cha_patriarch_1"] = true,
		["wh3_main_ksl_cha_patriarch_2"] = true,
		["wh3_main_nur_cha_cultist_0"] = true,
		["wh3_main_nur_cha_cultist_1"] = true,
		["wh3_main_nur_cha_exalted_great_unclean_one_death_0"] = true,
		["wh3_main_nur_cha_exalted_great_unclean_one_nurgle_0"] = true,
		["wh3_main_nur_cha_herald_of_nurgle_death_0"] = true,
		["wh3_main_nur_cha_herald_of_nurgle_death_1"] = true,
		["wh3_main_nur_cha_herald_of_nurgle_death_2"] = true,
		["wh3_main_nur_cha_herald_of_nurgle_nurgle_0"] = true,
		["wh3_main_nur_cha_herald_of_nurgle_nurgle_1"] = true,
		["wh3_main_nur_cha_herald_of_nurgle_nurgle_2"] = true,
		["wh3_main_nur_cha_ku_gath_plaguefather_0"] = true,
		["wh3_main_nur_cha_plagueridden_death_0"] = true,
		["wh3_main_nur_cha_plagueridden_death_1"] = true,
		["wh3_main_nur_cha_plagueridden_death_2"] = true,
		["wh3_main_nur_cha_plagueridden_nurgle_0"] = true,
		["wh3_main_nur_cha_plagueridden_nurgle_1"] = true,
		["wh3_main_nur_cha_plagueridden_nurgle_2"] = true,
		["wh3_main_ogr_cha_butcher_beasts_0"] = true,
		["wh3_main_ogr_cha_butcher_great_maw_0"] = true,
		["wh3_main_ogr_cha_firebelly_0"] = true,
		["wh3_main_ogr_cha_greasus_goldtooth_0"] = true,
		["wh3_main_ogr_cha_hunter_0"] = true,
		["wh3_main_ogr_cha_hunter_1"] = true,
		["wh3_main_ogr_cha_skrag_the_slaughterer_0"] = true,
		["wh3_main_ogr_cha_slaughtermaster_beasts_0"] = true,
		["wh3_main_ogr_cha_slaughtermaster_great_maw_0"] = true,
		["wh3_main_ogr_cha_tyrant_0"] = true,
		["wh3_main_pro_kho_cha_bloodreaper_0"] = true,
		["wh3_main_pro_kho_cha_bloodreaper_1"] = true,
		["wh3_main_pro_kho_cha_bloodreaper_2"] = true,
		["wh3_main_pro_kho_cha_cultist_0"] = true,
		["wh3_main_pro_kho_cha_cultist_1"] = true,
		["wh3_main_pro_kho_cha_herald_of_khorne_0"] = true,
		["wh3_main_pro_kho_cha_herald_of_khorne_1"] = true,
		["wh3_main_pro_kho_cha_herald_of_khorne_2"] = true,
		["wh3_main_pro_ksl_cha_boyar_0"] = true,
		["wh3_main_pro_ksl_cha_boyar_1"] = true,
		["wh3_main_pro_ksl_cha_boyar_2"] = true,
		["wh3_main_pro_ksl_cha_frost_maiden_ice_0"] = true,
		["wh3_main_pro_ksl_cha_frost_maiden_ice_1"] = true,
		["wh3_main_pro_ksl_cha_frost_maiden_ice_2"] = true,
		["wh3_main_pro_ksl_cha_gerik_0"] = true,
		["wh3_main_pro_ksl_cha_patriarch_0"] = true,
		["wh3_main_pro_ksl_cha_patriarch_1"] = true,
		["wh3_main_pro_ksl_cha_patriarch_2"] = true,
		["wh3_main_pro_ksl_cha_sergi_0"] = true,
		["wh3_main_pro_ksl_cha_slavin_0"] = true,
		["wh3_main_pro_ksl_cha_yuri_0"] = true,
		["wh3_main_pro_ksl_cha_yuri_1"] = true,
		["wh3_main_pro_ksl_cha_yuri_2"] = true,
		["wh3_main_pro_ksl_cha_yuri_3"] = true,
		["wh3_main_pro_ksl_cha_yuri_4"] = true,
		["wh3_main_pro_ksl_cha_yuri_5"] = true,
		["wh3_main_pro_ksl_cha_yuri_5_brazen_altar"] = true,
		["wh3_main_pro_ksl_cha_yuri_5_howling_citadel"] = true,
		["wh3_main_pro_tze_cha_cultist_0"] = true,
		["wh3_main_pro_tze_cha_cultist_1"] = true,
		["wh3_main_pro_tze_cha_herald_of_tzeentch_tzeentch_0"] = true,
		["wh3_main_pro_tze_cha_herald_of_tzeentch_tzeentch_1"] = true,
		["wh3_main_pro_tze_cha_herald_of_tzeentch_tzeentch_2"] = true,
		["wh3_main_sla_cha_alluress_shadow_0"] = true,
		["wh3_main_sla_cha_alluress_shadow_1"] = true,
		["wh3_main_sla_cha_alluress_shadow_2"] = true,
		["wh3_main_sla_cha_alluress_shadow_3"] = true,
		["wh3_main_sla_cha_alluress_slaanesh_0"] = true,
		["wh3_main_sla_cha_alluress_slaanesh_1"] = true,
		["wh3_main_sla_cha_alluress_slaanesh_2"] = true,
		["wh3_main_sla_cha_alluress_slaanesh_3"] = true,
		["wh3_main_sla_cha_cultist_0"] = true,
		["wh3_main_sla_cha_cultist_1"] = true,
		["wh3_main_sla_cha_exalted_keeper_of_secrets_shadow_0"] = true,
		["wh3_main_sla_cha_exalted_keeper_of_secrets_slaanesh_0"] = true,
		["wh3_main_sla_cha_herald_of_slaanesh_shadow_0"] = true,
		["wh3_main_sla_cha_herald_of_slaanesh_shadow_1"] = true,
		["wh3_main_sla_cha_herald_of_slaanesh_shadow_2"] = true,
		["wh3_main_sla_cha_herald_of_slaanesh_shadow_3"] = true,
		["wh3_main_sla_cha_herald_of_slaanesh_slaanesh_0"] = true,
		["wh3_main_sla_cha_herald_of_slaanesh_slaanesh_1"] = true,
		["wh3_main_sla_cha_herald_of_slaanesh_slaanesh_2"] = true,
		["wh3_main_sla_cha_herald_of_slaanesh_slaanesh_3"] = true,
		["wh3_main_sla_cha_nkari_0"] = true,
		["wh3_main_tze_cha_cultist_0"] = true,
		["wh3_main_tze_cha_cultist_1"] = true,
		["wh3_main_tze_cha_exalted_lord_of_change_metal_0"] = true,
		["wh3_main_tze_cha_exalted_lord_of_change_tzeentch_0"] = true,
		["wh3_main_tze_cha_herald_of_tzeentch_metal_0"] = true,
		["wh3_main_tze_cha_herald_of_tzeentch_metal_1"] = true,
		["wh3_main_tze_cha_herald_of_tzeentch_metal_2"] = true,
		["wh3_main_tze_cha_herald_of_tzeentch_tzeentch_0"] = true,
		["wh3_main_tze_cha_herald_of_tzeentch_tzeentch_1"] = true,
		["wh3_main_tze_cha_herald_of_tzeentch_tzeentch_2"] = true,
		["wh3_main_tze_cha_iridescent_horror_metal_0"] = true,
		["wh3_main_tze_cha_iridescent_horror_metal_1"] = true,
		["wh3_main_tze_cha_iridescent_horror_metal_2"] = true,
		["wh3_main_tze_cha_iridescent_horror_tzeentch_0"] = true,
		["wh3_main_tze_cha_iridescent_horror_tzeentch_1"] = true,
		["wh3_main_tze_cha_iridescent_horror_tzeentch_2"] = true,
		["wh3_main_tze_cha_kairos_fateweaver_0"] = true,
		["wh3_pro10_tze_cha_cultist_0"] = true,
		["wh3_pro10_tze_cha_daemon_prince_of_tzeentch"] = true,
		["wh3_pro11_chs_cha_harald_hammerstorm"] = true,
		["wh3_pro12_kho_cha_karanak"] = true,
		["wh3_prologue_test_general_0"] = true,
		["wh3_survival_dae_cha_be_lakor_01"] = true,
		["wh3_survival_dae_cha_be_lakor_02"] = true,
		["wh3_survival_kho_cha_bloodreaper"] = true,
		["wh3_survival_kho_cha_daemon_prince_of_khorne"] = true,
		["wh3_survival_kho_cha_exalted_bloodthirster"] = true,
		["wh3_survival_kho_cha_exalted_bloodthirster_0"] = true,
		["wh3_survival_nur_cha_daemon_prince_of_nurgle"] = true,
		["wh3_survival_nur_cha_exalted_great_unclean_one_nurgle"] = true,
		["wh3_survival_nur_cha_exalted_great_unclean_one_nurgle_01"] = true,
		["wh3_survival_nur_cha_plagueridden_death"] = true,
		["wh3_survival_sla_cha_alluress_shadow"] = true,
		["wh3_survival_sla_cha_daemon_prince_of_slaanesh"] = true,
		["wh3_survival_sla_cha_exalted_keeper_of_secrets_slaanesh"] = true,
		["wh3_survival_tze_cha_daemon_prince_of_tzeentch"] = true,
		["wh3_survival_tze_cha_exalted_lord_of_change_tzeentch"] = true,
		["wh3_survival_tze_cha_iridescent_horror_metal"] = true,
		["wh_dlc01_chs_cha_chaos_lord_10"] = true,
		["wh_dlc01_chs_cha_chaos_lord_2"] = true,
		["wh_dlc01_chs_cha_chaos_lord_9"] = true,
		["wh_dlc01_chs_cha_chaos_sorcerer_death_8"] = true,
		["wh_dlc01_chs_cha_chaos_sorcerer_fire_8"] = true,
		["wh_dlc01_chs_cha_chaos_sorcerer_lord_death_0"] = true,
		["wh_dlc01_chs_cha_chaos_sorcerer_lord_death_10"] = true,
		["wh_dlc01_chs_cha_chaos_sorcerer_lord_death_12"] = true,
		["wh_dlc01_chs_cha_chaos_sorcerer_lord_death_13"] = true,
		["wh_dlc01_chs_cha_chaos_sorcerer_lord_death_7"] = true,
		["wh_dlc01_chs_cha_chaos_sorcerer_lord_death_8"] = true,
		["wh_dlc01_chs_cha_chaos_sorcerer_lord_death_9"] = true,
		["wh_dlc01_chs_cha_chaos_sorcerer_lord_fire_0"] = true,
		["wh_dlc01_chs_cha_chaos_sorcerer_lord_fire_10"] = true,
		["wh_dlc01_chs_cha_chaos_sorcerer_lord_fire_12"] = true,
		["wh_dlc01_chs_cha_chaos_sorcerer_lord_fire_13"] = true,
		["wh_dlc01_chs_cha_chaos_sorcerer_lord_fire_7"] = true,
		["wh_dlc01_chs_cha_chaos_sorcerer_lord_fire_8"] = true,
		["wh_dlc01_chs_cha_chaos_sorcerer_lord_fire_9"] = true,
		["wh_dlc01_chs_cha_chaos_sorcerer_lord_metal_0"] = true,
		["wh_dlc01_chs_cha_chaos_sorcerer_lord_metal_10"] = true,
		["wh_dlc01_chs_cha_chaos_sorcerer_lord_metal_12"] = true,
		["wh_dlc01_chs_cha_chaos_sorcerer_lord_metal_13"] = true,
		["wh_dlc01_chs_cha_chaos_sorcerer_lord_metal_7"] = true,
		["wh_dlc01_chs_cha_chaos_sorcerer_lord_metal_8"] = true,
		["wh_dlc01_chs_cha_chaos_sorcerer_lord_metal_9"] = true,
		["wh_dlc01_chs_cha_chaos_sorcerer_lord_shadows_0"] = true,
		["wh_dlc01_chs_cha_chaos_sorcerer_lord_shadows_1"] = true,
		["wh_dlc01_chs_cha_chaos_sorcerer_lord_shadows_2"] = true,
		["wh_dlc01_chs_cha_chaos_sorcerer_lord_shadows_3"] = true,
		["wh_dlc01_chs_cha_chaos_sorcerer_lord_shadows_4"] = true,
		["wh_dlc01_chs_cha_chaos_sorcerer_metal_8"] = true,
		["wh_dlc01_chs_cha_chaos_sorcerer_shadows_0"] = true,
		["wh_dlc01_chs_cha_chaos_sorcerer_shadows_1"] = true,
		["wh_dlc01_chs_cha_chaos_sorcerer_shadows_2"] = true,
		["wh_dlc01_chs_cha_chaos_sorcerer_shadows_3"] = true,
		["wh_dlc01_chs_cha_exalted_hero_10"] = true,
		["wh_dlc01_chs_cha_exalted_hero_8"] = true,
		["wh_dlc01_chs_cha_kholek"] = true,
		["wh_dlc01_chs_cha_prince_sigvald_the_magnificent"] = true,
		["wh_dlc01_chs_cha_qb_lord_of_change_0"] = true,
		["wh_dlc01_nor_cha_chaos_sorcerer_lord_0"] = true,
		["wh_dlc01_nor_cha_chaos_sorcerer_lord_1"] = true,
		["wh_dlc01_nor_cha_chaos_sorcerer_lord_2"] = true,
		["wh_dlc03_bst_cha_beastlord_0"] = true,
		["wh_dlc03_bst_cha_beastlord_0_qb"] = true,
		["wh_dlc03_bst_cha_beastlord_1"] = true,
		["wh_dlc03_bst_cha_bray_shaman_beasts_0"] = true,
		["wh_dlc03_bst_cha_bray_shaman_beasts_1"] = true,
		["wh_dlc03_bst_cha_bray_shaman_death_0"] = true,
		["wh_dlc03_bst_cha_bray_shaman_death_1"] = true,
		["wh_dlc03_bst_cha_bray_shaman_shadows_0"] = true,
		["wh_dlc03_bst_cha_bray_shaman_shadows_1"] = true,
		["wh_dlc03_bst_cha_bray_shaman_wild_0"] = true,
		["wh_dlc03_bst_cha_bray_shaman_wild_0_qb"] = true,
		["wh_dlc03_bst_cha_bray_shaman_wild_1"] = true,
		["wh_dlc03_bst_cha_gorebull_0"] = true,
		["wh_dlc03_bst_cha_graktar_0"] = true,
		["wh_dlc03_bst_cha_khazrak_one_eye_0"] = true,
		["wh_dlc03_bst_cha_khazrak_one_eye_1"] = true,
		["wh_dlc03_bst_cha_malagor_the_dark_omen_0"] = true,
		["wh_dlc03_emp_cha_boris_todbringer_0"] = true,
		["wh_dlc03_emp_cha_boris_todbringer_1"] = true,
		["wh_dlc03_emp_cha_boris_todbringer_2"] = true,
		["wh_dlc03_emp_cha_boris_todbringer_3"] = true,
		["wh_dlc03_emp_cha_wizard_beasts_0"] = true,
		["wh_dlc03_emp_cha_wizard_beasts_1"] = true,
		["wh_dlc03_emp_cha_wizard_beasts_2"] = true,
		["wh_dlc03_emp_cha_wizard_beasts_3"] = true,
		["wh_dlc03_emp_cha_wizard_beasts_4"] = true,
		["wh_dlc04_emp_cha_arch_lector_0"] = true,
		["wh_dlc04_emp_cha_arch_lector_1"] = true,
		["wh_dlc04_emp_cha_arch_lector_2"] = true,
		["wh_dlc04_emp_cha_volkmar_the_grim_0"] = true,
		["wh_dlc04_emp_cha_volkmar_the_grim_1"] = true,
		["wh_dlc04_emp_cha_volkmar_the_grim_2"] = true,
		["wh_dlc04_emp_cha_volkmar_the_grim_3"] = true,
		["wh_dlc04_vmp_cha_helman_ghorst_0"] = true,
		["wh_dlc04_vmp_cha_helman_ghorst_1"] = true,
		["wh_dlc04_vmp_cha_master_necromancer_1"] = true,
		["wh_dlc04_vmp_cha_master_necromancer_2"] = true,
		["wh_dlc04_vmp_cha_master_necromancer_3"] = true,
		["wh_dlc04_vmp_cha_necromancer_1"] = true,
		["wh_dlc04_vmp_cha_necromancer_2"] = true,
		["wh_dlc04_vmp_cha_necromancer_3"] = true,
		["wh_dlc04_vmp_cha_strigoi_ghoul_king_0"] = true,
		["wh_dlc04_vmp_cha_strigoi_ghoul_king_0_boss"] = true,
		["wh_dlc04_vmp_cha_strigoi_ghoul_king_1"] = true,
		["wh_dlc04_vmp_cha_vlad_von_carstein_0"] = true,
		["wh_dlc05_bst_cha_morghur_0"] = true,
		["wh_dlc05_bst_cha_morghur_0_boss"] = true,
		["wh_dlc05_emp_cha_wizard_life_0"] = true,
		["wh_dlc05_emp_cha_wizard_life_1"] = true,
		["wh_dlc05_emp_cha_wizard_life_2"] = true,
		["wh_dlc05_emp_cha_wizard_life_3"] = true,
		["wh_dlc05_emp_cha_wizard_shadows_0"] = true,
		["wh_dlc05_emp_cha_wizard_shadows_1"] = true,
		["wh_dlc05_emp_cha_wizard_shadows_2"] = true,
		["wh_dlc05_emp_cha_wizard_shadows_3"] = true,
		["wh_dlc05_vmp_cha_red_duke_0"] = true,
		["wh_dlc05_vmp_cha_red_duke_1"] = true,
		["wh_dlc05_vmp_cha_red_duke_2"] = true,
		["wh_dlc05_vmp_cha_red_duke_3"] = true,
		["wh_dlc05_vmp_cha_vampire_shadows_0"] = true,
		["wh_dlc05_vmp_cha_vampire_shadows_1"] = true,
		["wh_dlc05_vmp_cha_vampire_shadows_2"] = true,
		["wh_dlc05_wef_cha_ancient_treeman_0"] = true,
		["wh_dlc05_wef_cha_branchwraith_0"] = true,
		["wh_dlc05_wef_cha_durthu_0"] = true,
		["wh_dlc05_wef_cha_female_glade_lord_0"] = true,
		["wh_dlc05_wef_cha_female_glade_lord_0_qb"] = true,
		["wh_dlc05_wef_cha_female_glade_lord_1"] = true,
		["wh_dlc05_wef_cha_female_glade_lord_2"] = true,
		["wh_dlc05_wef_cha_female_glade_lord_2_qb"] = true,
		["wh_dlc05_wef_cha_female_glade_lord_3"] = true,
		["wh_dlc05_wef_cha_glade_lord_0"] = true,
		["wh_dlc05_wef_cha_glade_lord_1"] = true,
		["wh_dlc05_wef_cha_glade_lord_2"] = true,
		["wh_dlc05_wef_cha_glade_lord_3"] = true,
		["wh_dlc05_wef_cha_orion_0"] = true,
		["wh_dlc05_wef_cha_spellsinger_beasts_0"] = true,
		["wh_dlc05_wef_cha_spellsinger_beasts_1"] = true,
		["wh_dlc05_wef_cha_spellsinger_beasts_2"] = true,
		["wh_dlc05_wef_cha_spellsinger_beasts_3"] = true,
		["wh_dlc05_wef_cha_spellsinger_life_0"] = true,
		["wh_dlc05_wef_cha_spellsinger_life_1"] = true,
		["wh_dlc05_wef_cha_spellsinger_life_2"] = true,
		["wh_dlc05_wef_cha_spellsinger_life_3"] = true,
		["wh_dlc05_wef_cha_spellsinger_shadows_0"] = true,
		["wh_dlc05_wef_cha_spellsinger_shadows_1"] = true,
		["wh_dlc05_wef_cha_spellsinger_shadows_2"] = true,
		["wh_dlc05_wef_cha_spellsinger_shadows_3"] = true,
		["wh_dlc05_wef_cha_waystalker_0"] = true,
		["wh_dlc06_chs_cha_chaos_sorcerer_death_9"] = true,
		["wh_dlc06_chs_cha_chaos_sorcerer_fire_9"] = true,
		["wh_dlc06_chs_cha_chaos_sorcerer_metal_9"] = true,
		["wh_dlc06_dwf_cha_belegar_ironhammer_0"] = true,
		["wh_dlc06_dwf_cha_master_engineer_ghost_0"] = true,
		["wh_dlc06_dwf_cha_runelord_0"] = true,
		["wh_dlc06_dwf_cha_runelord_1"] = true,
		["wh_dlc06_dwf_cha_runesmith_ghost_0"] = true,
		["wh_dlc06_dwf_cha_thane_ghost_0"] = true,
		["wh_dlc06_dwf_cha_thane_ghost_1"] = true,
		["wh_dlc06_emp_cha_arch_lector_0_boss"] = true,
		["wh_dlc06_emp_cha_captain_0_boss"] = true,
		["wh_dlc06_emp_cha_witch_hunter_boss"] = true,
		["wh_dlc06_grn_cha_night_goblin_warboss_0"] = true,
		["wh_dlc06_grn_cha_night_goblin_warboss_1"] = true,
		["wh_dlc06_grn_cha_skarsnik_0"] = true,
		["wh_dlc06_grn_cha_wurrzag_0"] = true,
		["wh_dlc06_grn_cha_wurrzag_1"] = true,
		["wh_dlc07_brt_cha_alberic_bordeleaux_0"] = true,
		["wh_dlc07_brt_cha_alberic_bordeleaux_1"] = true,
		["wh_dlc07_brt_cha_alberic_bordeleaux_2"] = true,
		["wh_dlc07_brt_cha_alberic_bordeleaux_3"] = true,
		["wh_dlc07_brt_cha_damsel_beasts_0"] = true,
		["wh_dlc07_brt_cha_damsel_beasts_1"] = true,
		["wh_dlc07_brt_cha_damsel_beasts_2"] = true,
		["wh_dlc07_brt_cha_damsel_beasts_3"] = true,
		["wh_dlc07_brt_cha_damsel_life_0"] = true,
		["wh_dlc07_brt_cha_damsel_life_1"] = true,
		["wh_dlc07_brt_cha_damsel_life_2"] = true,
		["wh_dlc07_brt_cha_damsel_life_3"] = true,
		["wh_dlc07_brt_cha_fay_enchantress_0"] = true,
		["wh_dlc07_brt_cha_fay_enchantress_1"] = true,
		["wh_dlc07_brt_cha_green_knight_0"] = true,
		["wh_dlc07_brt_cha_prophetess_0"] = true,
		["wh_dlc07_brt_cha_prophetess_1"] = true,
		["wh_dlc07_brt_cha_prophetess_2"] = true,
		["wh_dlc07_brt_cha_prophetess_3"] = true,
		["wh_dlc07_brt_cha_prophetess_beasts_0"] = true,
		["wh_dlc07_brt_cha_prophetess_beasts_1"] = true,
		["wh_dlc07_brt_cha_prophetess_beasts_2"] = true,
		["wh_dlc07_brt_cha_prophetess_beasts_3"] = true,
		["wh_dlc07_brt_cha_prophetess_heavens_0"] = true,
		["wh_dlc07_brt_cha_prophetess_heavens_1"] = true,
		["wh_dlc07_brt_cha_prophetess_heavens_2"] = true,
		["wh_dlc07_brt_cha_prophetess_heavens_3"] = true,
		["wh_dlc08_bst_mon_cygor_boss"] = true,
		["wh_dlc08_chs_cha_chaos_lord_2_qb"] = true,
		["wh_dlc08_chs_mon_dragon_ogre_shaggoth_boss"] = true,
		["wh_dlc08_grn_mon_giant_boss"] = true,
		["wh_dlc08_nor_cha_arzik_0"] = true,
		["wh_dlc08_nor_cha_fimir_balefiend_fire_0"] = true,
		["wh_dlc08_nor_cha_fimir_balefiend_shadow_0"] = true,
		["wh_dlc08_nor_cha_kihar_0"] = true,
		["wh_dlc08_nor_cha_shaman_sorcerer_death_0"] = true,
		["wh_dlc08_nor_cha_shaman_sorcerer_death_1"] = true,
		["wh_dlc08_nor_cha_shaman_sorcerer_death_2"] = true,
		["wh_dlc08_nor_cha_shaman_sorcerer_fire_0"] = true,
		["wh_dlc08_nor_cha_shaman_sorcerer_fire_1"] = true,
		["wh_dlc08_nor_cha_shaman_sorcerer_fire_2"] = true,
		["wh_dlc08_nor_cha_shaman_sorcerer_metal_0"] = true,
		["wh_dlc08_nor_cha_shaman_sorcerer_metal_1"] = true,
		["wh_dlc08_nor_cha_shaman_sorcerer_metal_2"] = true,
		["wh_dlc08_nor_cha_skin_wolf_werekin_0"] = true,
		["wh_dlc08_nor_cha_throgg_0"] = true,
		["wh_dlc08_nor_cha_wulfrik_0"] = true,
		["wh_dlc08_nor_cha_wulfrik_1"] = true,
		["wh_dlc08_nor_cha_wulfrik_2"] = true,
		["wh_dlc08_nor_cha_wulfrik_3"] = true,
		["wh_dlc08_nor_mon_frost_wyrm_boss"] = true,
		["wh_dlc08_vmp_mon_terrorgheist_boss"] = true,
		["wh_dlc08_wef_forest_dragon_boss"] = true,
		["wh_dlc08_wef_mon_treeman_boss"] = true,
		["wh_main_brt_cha_damsel_0"] = true,
		["wh_main_brt_cha_damsel_1"] = true,
		["wh_main_brt_cha_damsel_2"] = true,
		["wh_main_brt_cha_damsel_3"] = true,
		["wh_main_brt_cha_king_louen_leoncoeur_0"] = true,
		["wh_main_brt_cha_king_louen_leoncoeur_1"] = true,
		["wh_main_brt_cha_king_louen_leoncoeur_2"] = true,
		["wh_main_brt_cha_king_louen_leoncoeur_3"] = true,
		["wh_main_brt_cha_king_louen_leoncoeur_4"] = true,
		["wh_main_brt_cha_lord_0"] = true,
		["wh_main_brt_cha_lord_2"] = true,
		["wh_main_brt_cha_lord_3"] = true,
		["wh_main_brt_cha_lord_4"] = true,
		["wh_main_brt_cha_paladin_0"] = true,
		["wh_main_brt_cha_paladin_3"] = true,
		["wh_main_brt_cha_paladin_4"] = true,
		["wh_main_chs_cha_archaon_the_everchosen_0"] = true,
		["wh_main_chs_cha_archaon_the_everchosen_1"] = true,
		["wh_main_chs_cha_chaos_lord_0"] = true,
		["wh_main_chs_cha_chaos_lord_11"] = true,
		["wh_main_chs_cha_chaos_lord_12"] = true,
		["wh_main_chs_cha_chaos_lord_8"] = true,
		["wh_main_chs_cha_chaos_sorcerer_death_0"] = true,
		["wh_main_chs_cha_chaos_sorcerer_death_10"] = true,
		["wh_main_chs_cha_chaos_sorcerer_death_11"] = true,
		["wh_main_chs_cha_chaos_sorcerer_death_7"] = true,
		["wh_main_chs_cha_chaos_sorcerer_fire_0"] = true,
		["wh_main_chs_cha_chaos_sorcerer_fire_10"] = true,
		["wh_main_chs_cha_chaos_sorcerer_fire_11"] = true,
		["wh_main_chs_cha_chaos_sorcerer_fire_7"] = true,
		["wh_main_chs_cha_chaos_sorcerer_metal_0"] = true,
		["wh_main_chs_cha_chaos_sorcerer_metal_10"] = true,
		["wh_main_chs_cha_chaos_sorcerer_metal_11"] = true,
		["wh_main_chs_cha_chaos_sorcerer_metal_7"] = true,
		["wh_main_chs_cha_exalted_hero_0"] = true,
		["wh_main_chs_cha_exalted_hero_12"] = true,
		["wh_main_chs_cha_exalted_hero_13"] = true,
		["wh_main_chs_cha_exalted_hero_7"] = true,
		["wh_main_chs_cha_lord_of_change_0"] = true,
		["wh_main_dwf_cha_high_king_thorgrim_grudgebearer_1"] = true,
		["wh_main_dwf_cha_lord_0"] = true,
		["wh_main_dwf_cha_master_engineer_0"] = true,
		["wh_main_dwf_cha_rune_smith_0"] = true,
		["wh_main_dwf_cha_thane"] = true,
		["wh_main_dwf_cha_ungrim_ironfist"] = true,
		["wh_main_emp_cha_balthasar_gelt_0"] = true,
		["wh_main_emp_cha_balthasar_gelt_1"] = true,
		["wh_main_emp_cha_balthasar_gelt_2"] = true,
		["wh_main_emp_cha_balthasar_gelt_3"] = true,
		["wh_main_emp_cha_captain_0"] = true,
		["wh_main_emp_cha_captain_1"] = true,
		["wh_main_emp_cha_captain_2"] = true,
		["wh_main_emp_cha_captain_3"] = true,
		["wh_main_emp_cha_general_0"] = true,
		["wh_main_emp_cha_general_1"] = true,
		["wh_main_emp_cha_general_2"] = true,
		["wh_main_emp_cha_general_3"] = true,
		["wh_main_emp_cha_general_4"] = true,
		["wh_main_emp_cha_karl_franz_0"] = true,
		["wh_main_emp_cha_karl_franz_1"] = true,
		["wh_main_emp_cha_karl_franz_2"] = true,
		["wh_main_emp_cha_karl_franz_3"] = true,
		["wh_main_emp_cha_karl_franz_4"] = true,
		["wh_main_emp_cha_warrior_priest_0"] = true,
		["wh_main_emp_cha_warrior_priest_1"] = true,
		["wh_main_emp_cha_warrior_priest_2"] = true,
		["wh_main_emp_cha_witch_hunter"] = true,
		["wh_main_emp_cha_wizard_fire_0"] = true,
		["wh_main_emp_cha_wizard_fire_1"] = true,
		["wh_main_emp_cha_wizard_fire_2"] = true,
		["wh_main_emp_cha_wizard_fire_3"] = true,
		["wh_main_emp_cha_wizard_heavens_0"] = true,
		["wh_main_emp_cha_wizard_heavens_1"] = true,
		["wh_main_emp_cha_wizard_heavens_2"] = true,
		["wh_main_emp_cha_wizard_heavens_4"] = true,
		["wh_main_emp_cha_wizard_light_0"] = true,
		["wh_main_emp_cha_wizard_light_1"] = true,
		["wh_main_emp_cha_wizard_light_2"] = true,
		["wh_main_emp_cha_wizard_light_4"] = true,
		["wh_main_grn_cha_azhag_the_slaughterer_0"] = true,
		["wh_main_grn_cha_azhag_the_slaughterer_1"] = true,
		["wh_main_grn_cha_goblin_big_boss_0"] = true,
		["wh_main_grn_cha_goblin_big_boss_1"] = true,
		["wh_main_grn_cha_goblin_big_boss_2"] = true,
		["wh_main_grn_cha_goblin_big_boss_4"] = true,
		["wh_main_grn_cha_goblin_great_shaman_0"] = true,
		["wh_main_grn_cha_goblin_great_shaman_1"] = true,
		["wh_main_grn_cha_goblin_great_shaman_2"] = true,
		["wh_main_grn_cha_grimgor_ironhide"] = true,
		["wh_main_grn_cha_night_goblin_shaman"] = true,
		["wh_main_grn_cha_orc_shaman_0"] = true,
		["wh_main_grn_cha_orc_shaman_1"] = true,
		["wh_main_grn_cha_orc_warboss_0"] = true,
		["wh_main_grn_cha_orc_warboss_1"] = true,
		["wh_main_grn_cha_orc_warboss_2"] = true,
		["wh_main_grn_cha_orc_warboss_3"] = true,
		["wh_main_ksl_cha_captain_0"] = true,
		["wh_main_ksl_cha_captain_1"] = true,
		["wh_main_ksl_cha_captain_2"] = true,
		["wh_main_ksl_cha_general_0"] = true,
		["wh_main_ksl_cha_general_1"] = true,
		["wh_main_ksl_cha_general_2"] = true,
		["wh_main_ksl_cha_wizard_0"] = true,
		["wh_main_ksl_cha_wizard_1"] = true,
		["wh_main_nor_cha_chaos_sorcerer_0"] = true,
		["wh_main_nor_cha_chaos_sorcerer_1"] = true,
		["wh_main_nor_cha_chaos_sorcerer_2"] = true,
		["wh_main_nor_cha_marauder_chieftan_0"] = true,
		["wh_main_nor_cha_marauder_chieftan_1"] = true,
		["wh_main_nor_cha_marauder_chieftan_2"] = true,
		["wh_main_nor_cha_marauder_chieftan_3"] = true,
		["wh_main_teb_cha_captain_0"] = true,
		["wh_main_teb_cha_captain_1"] = true,
		["wh_main_teb_cha_captain_2"] = true,
		["wh_main_teb_cha_general_0"] = true,
		["wh_main_teb_cha_general_1"] = true,
		["wh_main_teb_cha_general_2"] = true,
		["wh_main_teb_cha_wizard_0"] = true,
		["wh_main_teb_cha_wizard_1"] = true,
		["wh_main_vmp_cha_banshee"] = true,
		["wh_main_vmp_cha_heinrich_kemmler"] = true,
		["wh_main_vmp_cha_mannfred_von_carstein_0"] = true,
		["wh_main_vmp_cha_mannfred_von_carstein_2"] = true,
		["wh_main_vmp_cha_mannfred_von_carstein_3"] = true,
		["wh_main_vmp_cha_mannfred_von_carstein_4"] = true,
		["wh_main_vmp_cha_master_necromancer_0"] = true,
		["wh_main_vmp_cha_master_necromancer_4"] = true,
		["wh_main_vmp_cha_master_necromancer_5"] = true,
		["wh_main_vmp_cha_necromancer_0"] = true,
		["wh_main_vmp_cha_necromancer_5"] = true,
		["wh_main_vmp_cha_vampire_0"] = true,
		["wh_main_vmp_cha_vampire_1"] = true,
		["wh_main_vmp_cha_vampire_2"] = true,
		["wh_main_vmp_cha_vampire_lord_0"] = true,
		["wh_main_vmp_cha_vampire_lord_2"] = true,
		["wh_main_vmp_cha_vampire_lord_3"] = true,
		["wh_main_vmp_cha_vampire_lord_5"] = true,
		["wh_main_vmp_cha_wight_king_0"] = true,
		["wh_main_vmp_cha_wight_king_0_summoned"] = true,
		["wh_main_vmp_cha_wight_king_1"] = true,
		["wh_main_vmp_cha_wight_king_2"] = true,
		["wh_pro01_dwf_cha_grombrindal_0"] = true,
		["wh_pro02_vmp_cha_isabella_von_carstein_0"] = true,
		["wh_pro02_vmp_cha_isabella_von_carstein_2"] = true,
		["wh_pro02_vmp_cha_isabella_von_carstein_4"] = true,
		["wh_pro03_vmp_cha_krell_0"] = true,
		["wh_pro03_vmp_cha_krell_campaign_0"] = true,
		["wh_pro03_vmp_cha_krell_campaign_1"] = true,
		["wh_pro03_vmp_cha_krell_campaign_2"] = true,
		["wh_pro03_vmp_cha_krell_campaign_3"] = true,
		["wh_pro03_vmp_cha_krell_campaign_4"] = true,
}

-- THE FINISHER'S HEALTH LINE: strictly BELOW 20% (the user's word: "below 20% health").
FOURTH.HEALTH_LINE_PCT = 20

-- ONE line for the whole battle when a commander cannot be classified.
FOURTH.cmdr_unreadable_logged = false

-- THE PLAIN TYPE READ (pcall'd; nil when it cannot be taken).
function FOURTH.type_plain(unit)
	local ok, t = pcall(function() return unit:type() end)
	if ok and type(t) == "string" and t ~= "" then return t end
	return nil
end

-- true / false - IS THIS ENEMY A LORD OR A HERO? Exact whole-key equality
-- against the DERIVED commander set first (type() is the PROVEN land_units key
-- read), battle_unit:unit_class() == "com" second, FAIL CLOSED third.
function FOURTH.enemy_is_commander(enemy)
	local t = FOURTH.type_plain(enemy)
	if t ~= nil then
		return (FOURTH.commander_keys[t] == true)
	end
	local ok, cls = pcall(function() return enemy:unit_class() end)
	if ok and type(cls) == "string" and cls ~= "" then
		return (cls == "com")
	end
	if not FOURTH.cmdr_unreadable_logged then
		FOURTH.cmdr_unreadable_logged = true
		log("commander check: NEITHER type() NOR unit_class() could be read on an enemy -"
			.. " treating it as a COMMANDER (fail-closed: the finisher will not fire at it)."
			.. " One-time notice.")
	end
	return true
end

-- THE ONE HEALTH READ (this round): 0-100 PERCENT, whatever scale the engine
-- answers on.
--
-- WHY (field log 2026-10-17, Eye of Khorne): `HealthPercent` comes back as a
-- FRACTION (0..1), NOT a percentage. 336 picks in one battle printed ONLY
-- "health=0%" or "health=1%" while the picked unit was alive and fighting for
-- 84 s; a 0-100 percent read would have moved through 18/12/5%, and a 1%
-- unit does not survive 84 s of melee. The game's own unit_banner layout feeds
-- this same field straight into a ContextFillBar (a 0..1 input), and the
-- sibling unit read `battle_unit:unary_hitpoints()` is documented as a
-- fraction (0.88). Comparing a fraction against a PERCENT threshold made every
-- comparison true (hp < 20 <=> hp < 2000%), so the finisher offered, and cast
-- on, units far above 20% health.
--
-- The engine's own unit read is tried FIRST (unary_hitpoints, a documented
-- fraction); the context field is the fallback, scaled the same way. A value
-- in 0..1 is a fraction and is multiplied by 100; a value above 1 is already a
-- percent (defensive - never observed). nil when neither read answers.
function FOURTH.health_pct(unit)
	local ok, v = pcall(function() return unit:unary_hitpoints() end)
	if ok and type(v) == "number" then
		if v >= 0 and v <= 1 then return v * 100 end
		return v
	end
	local c = FOURTH.context_value(unit, "HealthPercent")
	if type(c) == "string" then c = tonumber(c) end
	if type(c) ~= "number" then return nil end
	if c >= 0 and c <= 1 then return c * 100 end
	return c
end

-- THE ENEMY HEALTH READ (percent, 0-100): the ONE reader above.
function FOURTH.enemy_health_pct(enemy)
	return FOURTH.health_pct(enemy)
end

-- TZ'ARKAN'S LOW-HEALTH TRIGGER (this round) - the user's rule: activate
-- Tz'arkan when the caster's health is BELOW 15%. ONE entry carries all five
-- Tz'arkan keys (base / MP / Snikch / spite / spite MP) on this one trigger.
--
-- The OWNER must be ALIVE (the poll already gated that), NOT routing, and its
-- health - read through the ONE reader, FOURTH.health_pct, a real 0-100
-- percent - must be BELOW the line. NEVER a raw HealthPercent read: that
-- field answers a 0..1 FRACTION, so `hp < 15` on it would be true for every
-- unit on the field (the round-103 field failure). The cast is on the OWNER
-- ITSELF through the unit form, with the caster's controller re-fetched FRESH
-- this tick; a self cast has NO range bound, so no distance is read.
--
-- THE THRESHOLD IS DELIBERATE (the user's own number, 2026-10-17). This
-- transform is very likely ONE-WAY and its wind-up is 3 s (1.5 s for the
-- Snikch key), so a caster at 14% may die before the transform resolves. It
-- is ONE constant - raise FOURTH.TZARKAN_PCT if field tests show deaths
-- inside the wind-up.
FOURTH.TZARKAN_PCT = 15

function FOURTH.evaluate_tzarkan_low_health(unit, routing)
	if routing then return nil end
	local hp = FOURTH.health_pct(unit)
	if type(hp) ~= "number" or hp >= FOURTH.TZARKAN_PCT then return nil end
	-- the cast is the OWNER: mark it and re-fetch the caster's controller FRESH
	-- this tick (a controller held from an earlier poll silently no-ops).
	FOURTH.tz_self = true
	FOURTH.tz_caster_su = FOURTH.eg_fresh_caster_su(unit)
	return string.format("health %.1f%% (BELOW the %d%% line) - one-way transform, cast on SELF",
		hp, FOURTH.TZARKAN_PCT)
end

-- THE SELF-SUMMON EVALUATOR (Nurgling Tide). The owner must be ALIVE (the poll
-- already gated that), NOT routing, and IN MELEE - nothing else, and NO RANGE
-- BOUND: the cast is on the OWNER itself, so there is no distance to test.
function FOURTH.evaluate_self_summon_melee(unit, routing)
	if routing then return nil end
	local ok_melee, melee = pcall(function() return unit:is_in_melee() end)
	if not (ok_melee and melee == true) then return nil end
	-- the cast is the OWNER: mark it and re-fetch the caster's controller FRESH
	-- this tick (a controller held from an earlier poll silently no-ops).
	FOURTH.ss_self = true
	FOURTH.ss_caster_su = FOURTH.eg_fresh_caster_su(unit)
	return "the caster itself is in melee (self summon - cast on SELF, no range bound)"
end

-- THE NON-COMMANDER ENEMY PICKER (Eye of Khorne + The Dreaded Thirteenth).
-- mode = "health": keep enemies BELOW FOURTH.HEALTH_LINE_PCT health, take the
--                   LOWEST health (closest as the tiebreak).
-- mode = "melee" : keep enemies IN MELEE, take the CLOSEST.
-- Both keep only ALIVE + VALID enemies inside the ability's own 70% bound that
-- are NOT a Lord or Hero. The chosen enemy rides FOURTH.eg_enemy / .eg_arm /
-- .eg_caster_su / .cast_target exactly like the existing enemy triggers, so the
-- shared pre-cast re-check and the shared cast path apply unchanged.
function FOURTH.enc_pick_enemy(unit, routing, ground, mode)
	local reason = nil
	local marker = FOURTH.eg_marker or "summon"
	local bound = FOURTH.eg_range_m
	FOURTH.eg_ground = ground
	FOURTH.eg_mode = mode
	FOURTH.eg_noncommander = true
	FOURTH.eg_infantry = (mode == "infantry")
	if not routing then
		local ok_coll, coll = pcall(function()
			return bm:get_scriptunits_for_main_enemy_army_to_local_player()
		end)
		if ok_coll and coll ~= nil then
			local ok_n, n = pcall(function() return coll:count() end)
			if ok_n and type(n) == "number" then
				local best_enemy, best_gap, best_hp = nil, nil, nil
				for i = 1, n do
					local ok_su, su = pcall(function() return coll:item(i) end)
					if ok_su and su ~= nil then
						local enemy = nil
						pcall(function() enemy = su.unit end)
						if enemy ~= nil then
							local ok_alive, alive = pcall(function() return enemy:number_of_men_alive() end)
							local valid = FOURTH.eg_enemy_valid(enemy)
							local ok_melee, melee = pcall(function() return enemy:is_in_melee() end)
							local hp = nil
							local qualifies = false
							if mode == "health" then
								hp = FOURTH.enemy_health_pct(enemy)
								qualifies = (hp ~= nil and hp < FOURTH.HEALTH_LINE_PCT)
							elseif mode == "infantry" then
								-- ROUND 106: IN MELEE **and** INFANTRY (real reads, fail-closed).
								qualifies = (ok_melee and melee == true) and FOURTH.enemy_is_infantry(enemy)
							else
								qualifies = (ok_melee and melee == true)
							end
							if qualifies
								and ok_alive and type(alive) == "number" and alive > 0
								and (valid == nil or valid == true)
								and FOURTH.eg_enemy_within_bound(unit, enemy)
								and not FOURTH.enemy_is_commander(enemy) then
								local gap = FOURTH.eg_enemy_gap(unit, enemy)
								local better = false
								if best_enemy == nil then
									better = true
								elseif mode == "health" then
									if hp < best_hp then
										better = true
									elseif hp == best_hp and gap ~= nil and (best_gap == nil or gap < best_gap) then
										better = true
									end
								elseif gap ~= nil and (best_gap == nil or gap < best_gap) then
									better = true
								end
								if better then best_enemy, best_gap, best_hp = enemy, gap, hp end
							end
						end
					end
				end
				if best_enemy ~= nil then
					local etype = "enemy"
					pcall(function() etype = tostring(best_enemy:type()) end)
					local bound_text = "none"
					if FOURTH.eg_no_bound ~= true then
						bound_text = tostring(bound) .. "m"
					end
					local hp_text = ""
					if mode == "health" then
						hp_text = ", health=" .. string.format("%.0f", best_hp) .. "%"
					end
					log("  " .. marker .. " target: '" .. etype .. "' is the chosen enemy (" .. tostring(mode) .. ")"
						.. hp_text .. " distance=" .. ((best_gap ~= nil) and string.format("%.1f", best_gap) or "?")
						.. "m bound=" .. bound_text)
					FOURTH.eg_enemy = best_enemy
					FOURTH.eg_arm = mode
					FOURTH.eg_caster_su = FOURTH.eg_fresh_caster_su(unit)
					FOURTH.cast_target = best_enemy
					if mode == "health" then
						reason = "lowest-health non-commander enemy below "
							.. tostring(FOURTH.HEALTH_LINE_PCT) .. "% in bound (targeting " .. etype
							.. ", health=" .. string.format("%.0f", best_hp) .. "%, distance="
							.. ((best_gap ~= nil) and string.format("%.1f", best_gap) or "?") .. "m)"
					elseif mode == "infantry" then
						reason = "closest in-melee INFANTRY enemy within bound (targeting "
							.. etype .. ", distance="
							.. ((best_gap ~= nil) and string.format("%.1f", best_gap) or "?") .. "m)"
					else
						reason = "closest non-commander enemy in melee within bound (targeting "
							.. etype .. ", distance="
							.. ((best_gap ~= nil) and string.format("%.1f", best_gap) or "?") .. "m)"
					end
				end
			end
		end
	end
	return reason
end

-- EYE OF KHORNE: the FINISHER trigger (lowest-health non-commander below the line).
function FOURTH.evaluate_enemy_low_health_noncommander(unit, routing)
	return FOURTH.enc_pick_enemy(unit, routing, false, "health")
end

-- THE DREADED THIRTEENTH: the non-commander in-melee trigger.
function FOURTH.evaluate_enemy_melee_noncommander(unit, routing)
	return FOURTH.enc_pick_enemy(unit, routing, true, "melee")
end


-- ============================================================================
-- ROUND 106 - THE BOMBARDMENT ROUND: the two approved families' helpers.
--
-- (1) melee_skip_commanders - Soulfire (2 keys) and Arachneruption.
--     The user's rule: fire when the caster is IN MELEE, but SKIP when the
--     caster is fighting ONLY a Lord or a Hero. The engagement set is read
--     from the game's own enemy enumerator: every ALIVE enemy that reports
--     is_in_melee() == true and whose edge-to-edge unit_distance() to the
--     caster is within FOURTH.ENGAGE_CONTACT_M (12 m - melee CONTACT for
--     bounding boxes, the same primitive the range rule uses everywhere).
--     Each member is classified by FOURTH.enemy_is_commander (the 1,409-key
--     derived set, unit_class() == "com" fallback, FAIL CLOSED).
--     The judged set is LOGGED once per (unit, marker) and again only when it
--     CHANGES - type, commander flag and the REAL distance - so the rule is
--     auditable in the field log without flooding it.
--     When NO enemy can be read as engaged, the caster's own current_target()
--     is the fallback; when that is absent too the ability fires on the plain
--     in-melee rule (the older behaviour) and says so.
--
-- (2) enemy_ground_melee_infantry - the 30 bombardment abilities of the
--     approved list. Trigger: the CLOSEST enemy inside the ability's own 70%
--     bound that is IN MELEE and IS INFANTRY.
--     INFANTRY IS A REAL READ: battle_unit:is_infantry() (API dump: "Returns
--     whether this is a unit of infantry"), with battle_unit:unit_class() as
--     the fallback - EXACT equality against the three land_units infantry
--     classes (inf_mel / inf_mis / inf_spr) - and FAIL CLOSED when neither
--     answers. This is the same READ-first discipline as the commander set;
--     a derived 942-key land_units list would also work but would miss every
--     DLC unit whose key is not in it, while the engine read cannot.
--     The cast follows EACH ability's own targeting data: a ground-targeted
--     key is placed with perform_special_ability_ground(key, enemy position);
--     a unit-targeted key goes through perform_special_ability(key, enemy).
--     The chosen enemy is re-checked immediately before the cast (alive, in
--     melee, still infantry, still inside the bound).
--
-- NO NEW CHUNK-LEVEL LOCALS: every table, counter and function below is a
-- field of the FOURTH bag (the main chunk sits at Lua's 200-local ceiling).
-- ============================================================================
FOURTH.ENGAGE_CONTACT_M = 12
FOURTH.engage_note = {}
FOURTH.infantry_unreadable_logged = false

-- true / false - IS THIS ENEMY INFANTRY? The engine's own read first, the
-- land_units class second (EXACT string equality - no substring search anywhere),
-- FAIL CLOSED (not infantry) when neither answers.
function FOURTH.enemy_is_infantry(enemy)
	local ok, v = pcall(function() return enemy:is_infantry() end)
	if ok then
		if v == true then return true end
		if v == false then return false end
	end
	local ok2, cls = pcall(function() return enemy:unit_class() end)
	if ok2 and type(cls) == "string" and cls ~= "" then
		return (cls == "inf_mel") or (cls == "inf_mis") or (cls == "inf_spr")
	end
		if not FOURTH.infantry_unreadable_logged then
		FOURTH.infantry_unreadable_logged = true
		log("infantry check: NEITHER is_infantry() NOR unit_class() could be read on an enemy -"
			.. " treating it as NOT infantry (fail-closed). One-time notice.")
	end
	return false
end

-- ONE read of the enemy enumerator (the collection every enemy trigger uses).
-- Returns members (each { unit, type, commander, gap }), the count of
-- NON-COMMANDER members; nil, nil when the enumerator itself cannot be read.
function FOURTH.engagement_set(unit)
	local ok_coll, coll = pcall(function()
		return bm:get_scriptunits_for_main_enemy_army_to_local_player()
	end)
	if not ok_coll or coll == nil then return nil, nil end
	local ok_n, n = pcall(function() return coll:count() end)
	if not ok_n or type(n) ~= "number" then return nil, nil end
	local members, noncmd = {}, 0
	for i = 1, n do
		local ok_su, su = pcall(function() return coll:item(i) end)
		if ok_su and su ~= nil then
			local enemy = nil
			pcall(function() enemy = su.unit end)
			if enemy ~= nil then
				local ok_alive, alive = pcall(function() return enemy:number_of_men_alive() end)
				local ok_melee, melee = pcall(function() return enemy:is_in_melee() end)
				local gap = nil
				local ok_gap, g = pcall(function() return unit:unit_distance(enemy) end)
				if ok_gap and type(g) == "number" then gap = g end
				if ok_alive and type(alive) == "number" and alive > 0
					and ok_melee and melee == true
					and (gap == nil or gap <= FOURTH.ENGAGE_CONTACT_M) then
					local etype = FOURTH.type_plain(enemy) or "enemy"
					local cmdr = FOURTH.enemy_is_commander(enemy)
					members[#members + 1] = { unit = enemy, type = etype, commander = cmdr, gap = gap }
					if not cmdr then noncmd = noncmd + 1 end
				end
			end
		end
	end
	return members, noncmd
end

-- RECORD THE JUDGED SET once, then only on a CHANGE (dedupe by note text).
function FOURTH.note_engagement(unit, marker, note)
	local ok_id, id = pcall(function() return unit:unique_ui_id() end)
	if not ok_id or id == nil then return end
	local slot = tostring(id)
	local per = FOURTH.engage_note[slot]
	if per == nil then per = {}; FOURTH.engage_note[slot] = per end
	if per[marker] == note then return end
	per[marker] = note
		log("  " .. tostring(marker) .. " " .. note)
end

-- THE SOULFIRE / ARACHNERUPTION TRIGGER.
function FOURTH.evaluate_melee_skip_commanders(unit, routing)
	if routing then return nil end
	local ok_melee, melee = pcall(function() return unit:is_in_melee() end)
	if not (ok_melee and melee == true) then return nil end
	local marker = FOURTH.eg_marker or "ability"
	local members, noncmd = FOURTH.engagement_set(unit)
	local note, reason
	if members == nil then
		note = "engagement set UNREADABLE (the enemy enumerator failed) - plain in-melee rule"
		reason = "in melee (engagement set unreadable - plain in-melee rule)"
	elseif #members == 0 then
		local ok_t, t = pcall(function() return unit:current_target() end)
		if ok_t and t ~= nil then
			local cmdr = FOURTH.enemy_is_commander(t)
			local tt = FOURTH.type_plain(t) or "enemy"
			if cmdr then
				note = "no enemy in contact - current_target '" .. tt
					.. "' is a COMMANDER (Lord/Hero) -> HOLDING"
				FOURTH.note_engagement(unit, marker, note)
				return nil
			end
			note = "no enemy in contact - current_target '" .. tt
				.. "' is not a commander -> firing"
			reason = "in melee - the current target ('" .. tt .. "') is not a Lord or Hero"
		else
			note = "no enemy readable in contact and no current target - plain in-melee rule (older behaviour)"
			reason = "in melee (engagement set unreadable - plain in-melee rule)"
		end
	else
		local parts = {}
		for i = 1, #members do
			local m = members[i]
			parts[#parts + 1] = "'" .. m.type .. "' "
				.. (m.commander and "COMMANDER" or "non-commander")
				.. ((m.gap ~= nil) and (" " .. string.format("%.1f", m.gap) .. "m") or " ?m")
		end
		if noncmd == 0 then
			note = "engagement set: " .. tostring(#members) .. " enemy unit(s) in contact (<= "
				.. tostring(FOURTH.ENGAGE_CONTACT_M) .. "m): " .. table.concat(parts, ", ")
				.. " -> HOLDING (every engaged enemy is a Lord or Hero)"
			FOURTH.note_engagement(unit, marker, note)
			return nil
		end
		note = "engagement set: " .. tostring(#members) .. " enemy unit(s) in contact (<= "
			.. tostring(FOURTH.ENGAGE_CONTACT_M) .. "m): " .. table.concat(parts, ", ")
			.. " -> FIRING (a non-commander is engaged)"
		reason = "in melee - " .. tostring(noncmd) .. " non-commander enemy unit(s) in contact"
	end
	FOURTH.note_engagement(unit, marker, note)
	return reason
end

-- THE BOMBARDMENT TRIGGER: closest in-melee INFANTRY enemy inside the bound,
-- cast at that enemy's own position in whichever form its row declares.
function FOURTH.evaluate_enemy_ground_melee_infantry(unit, routing)
	FOURTH.eg_melee_only = true
	return FOURTH.enc_pick_enemy(unit, routing, nil, "infantry")
end

-- ============================================================================
-- ROUND 114 - THE AIR-DROP RULE IS ONE COMPARISON: THE ENGINE'S EDGE GAP < 0.1 m
--
-- THE USER'S RULING, verbatim:
--   "1. I want the trigger to be checked much more frequently when armed and
--    less than 30 meters from a valid enemy unit.
--    2. Valid units are those who have more than 10 entities.
--    3. I trigger the moment distance between edges is below 0.1 meters.
--    That's it."
-- and, on this round's two follow-ups:
--   "1. Remove the 'and it is infantry'. No need for it now.
--    2. Current count 3. Let's try with 0.2 s for now."
--
-- ROUND 117 - THE MEASUREMENT MOVES, THE RULE DOES NOT
-- THE USER'S RULING, verbatim: "Let's keep our current calculation but just
-- replace the detection on edge with detection on the distance to center.
-- Let's say 6 meters for now. I'll test."
-- The candidate filter, the velocity-aware delay MEASURED ONCE PER CONTACT,
-- the short-crossing fallback, the 250 ms poll and the 0.2 s fast pass, the
-- gates and the read-verification lines are UNCHANGED. ONE number moved: the
-- gap that decides UNDER. It used to be the engine's bounding-box EDGE gap
-- (`unit:unit_distance(enemy)`, battle_unit.lua:160); it is now the
-- GROUND-PLANE CENTRE-to-CENTRE distance between the two units' own
-- position() reads - x/z only, the height is never read - computed by
-- FOURTH.ad_centre_gap(). The old 0.10 m edge constant is RETIRED (nothing
-- else in the file used it) and FOURTH.AIR_DROP_CENTER_M = 6.0 replaces it.
--
-- THE RULE, IN FULL - nothing else decides:
--   candidate = ALIVE (number_of_men_alive() > 0) and
--               number_of_men_alive() > AIR_DROP_MIN_MEN (10)
--   valid     = that candidate's CENTRE gap (ad_centre_gap) is READABLE
--   chosen    = the NEAREST valid candidate by that CENTRE gap
--   UNDER     = ad_centre_gap(caster, chosen) < AIR_DROP_CENTER_M (6.0 m)
--   FIRE      = UNDER, and the delay measured for that pair at the first
--               contact of the episode has elapsed (round 116 - see below)
-- plus the caster-side usage restrictions the ability's own row declares
-- (air_only / no_melee), the self-centred cast on the OWNER, and fail-closed
-- reads. Nothing else: no infantry test, no single-entity test, no projection.
--
-- WHY THE CENTRE, AND WHY x/z ONLY. battle_unit:unit_distance() is "the
-- shortest distance in metres between this unit and a supplied unit, taking
-- into account their bounding box rather than just working out the
-- centre-to-centre distance" (battle_unit.lua:160) - two wide formations can
-- have boxes 0.1 m apart while their CENTRES are 15 m apart, which reads as
-- "on top of each other" and drops too early. The user's ruling is to detect
-- on the distance to the CENTRE instead. battle_unit:position() is "the centre
-- position of the main squad of the unit"; battle_vector's ground plane is x/z
-- (get_y is HEIGHT), so the gap is read with position():distance_xz() and
-- never with the 3D distance - a flyer 60 m up over an enemy is 0 m away here,
-- which is exactly what an air drop on that enemy means.
--
-- WHAT ROUND 114 DELETED FROM THIS EVALUATOR (each was invented to make a
-- CENTRE POINT stand in for a box; the edge gap needs none of them):
--   * the infantry filter (the old class test) - the user's ruling 1. Every
--     OTHER evaluator keeps its own class filters untouched; only this
--     evaluator stopped asking.
--   * the single-entity exclusion via initial_number_of_men(): a one-model
--     unit fails the > 10 test by itself, which is exactly the case that
--     guard was protecting (the user's own point).
--   * the four projection dials AIR_DROP_DELAY_S / AIR_DROP_ENEMY_LEAD /
--     AIR_DROP_CASTER_DELAY_S / AIR_DROP_CASTER_LEAD and the AIR_DROP_INHERIT
--     momentum flag;
--   * the 6 m centre bound (round 117 brought it BACK, as AIR_DROP_CENTER_M)
--     and the derived frontage credit
--     (AIR_DROP_MODEL_RADIUS_M / AIR_DROP_RANKS / AIR_DROP_FRONTAGE_MIN_M /
--     AIR_DROP_FRONTAGE_MAX_M);
--   * the path SEGMENT test (ad_seg_dist), the velocity reads (ad_velocity) and
--     every projected point (ad_lead / ad_project);
--   * the helpers ad_frontage, ad_frontage_text, ad_seg_dist, ad_velocity,
--     ad_lead, ad_project, ad_dial_text, ad_single_say, ad_single_clear,
--     ad_centre_gap, ad_pos, ad_sep and ad_vec_text. (ad_centre_gap came back
--   in round 117 - it is now the ONE measurement the rule makes.)
--   NOTHING ELSE IN THE FILE USED ANY OF THEM (every caller of every one of
--   those helpers was inside this evaluator or its pre-cast re-check), so they
--   were REMOVED rather than left dead - see the round-114 block in
--   docs/WH3_round114_airdrop_edgesimple.md for the caller inventory.
--   The four helpers KEPT are ad_tag (the ui-id tag), ad_say (the change-gated
--   note), ad_nearest (ONE candidate scan, shared by the picker and the fast
--   pass) and ad_pick (the evaluator itself).
--
-- THE FAST PASS (FOURTH.ad_fast_pass, registered beside the poll): it re-runs
-- THE SAME ad_pick every AIR_DROP_FAST_S = 0.2 s, but only for units that are
-- ALIVE, ARMED for an air-drop marker, and only while a VALID enemy is inside
-- AIR_DROP_NEAR_M = 30 m. It is one copy of the rule: it calls the same
-- evaluator and the same cast path (FOURTH.try_pair) as the global poll, which
-- is untouched (POLL_MS and every other ability's cadence stay exactly as they
-- are).
--
-- THE FOUR CONSTANTS - one test value each, no per-entry edit needed:
--   AIR_DROP_CENTER_M = 6.0 m  FIRE below this CENTRE-to-CENTRE ground gap
--   AIR_DROP_MIN_MEN  = 10     a candidate needs MORE alive models than this
--   AIR_DROP_NEAR_M   = 30 m   the fast pass runs while a valid enemy is closer
--   AIR_DROP_FAST_S   = 0.2 s  the fast pass interval
FOURTH.AIR_DROP_CENTER_M = 6.0
FOURTH.AIR_DROP_MIN_MEN = 10
FOURTH.AIR_DROP_NEAR_M = 30
FOURTH.AIR_DROP_FAST_S = 0.2
-- ============================================================================
-- ============================================================================
-- ROUND 118 - THE DELAY IS GONE: THE FIRST EVALUATION THAT SEES THE CENTRE
-- INSIDE THE LINE CASTS
--
-- THE USER'S RULING, verbatim: "I tried it. Let's keep the distance to center
-- and remove the delay we had completely."
--
-- WHAT THE RULE IS NOW - one measurement, one comparison, no wait:
--   candidate = ALIVE, and number_of_men_alive() > AIR_DROP_MIN_MEN (10)
--   valid     = that candidate's CENTRE gap (ad_centre_gap) is READABLE
--   chosen    = the NEAREST valid candidate by that CENTRE gap
--   FIRE      = the chosen enemy's centre gap < AIR_DROP_CENTER_M (6.0 m)
-- The evaluation that first measures the chosen enemy's centre inside the line
-- returns the decision AND the cast goes out on it: nothing is stamped,
-- nothing is timed, nothing is re-measured inside a contact, and nothing fires
-- on the way out. Nothing waits for a second poll - the 0.2 s fast pass and the
-- 250 ms poll both fire on the evaluation that sees the line crossed, so the drop
-- leaves within one fast-pass interval (0.2 s) of the centre arriving.
--
-- WHAT ROUND 118 DELETED (every one of them existed to TIME a wait; the symbol
-- inventory and the caller audit are in docs/WH3_round118_airdrop_nodelay.md -
-- they are deliberately NOT named here, so a grep for any of them over this
-- file answers 0 and the harness pins exactly that):
--   * the two delay dials (a 1.0 s baseline and a 1.0 s swing) and the 0.3 s
--     minimum-contact floor;
--   * the per-pair contact row - one row per (caster, enemy) holding the tick
--     the contact started on, the delay measured for it, and the evidence that
--     delay came from - and every helper over it: the pair key, the stamp, the
--     per-pair delay read, the row drop, the elapsed read, the purge and the
--     no-valid-pair clear;
--   * the purge hook: its ONE call site was in drop_unit_by_ui_id, which
--     existed only to clear those rows. Both are gone, and nothing else in the
--     file ever named any of it;
--   * the enemy-velocity read, the raw-read body it built, the printed
--     projection and the formula that turned it into a delay;
--   * the un-deduped event line (contact started / held / satisfied /
--     cancelled / fired on separation): there are no delay events left to
--     write, and the change-gated decision line carries the whole decision;
--   * the fallback that fired on separation. With no wait there is no crossing
--     to rescue: a pair that arrives and leaves between two evaluations is
--     simply not seen, which is the fast pass's business, not a rule.
--
-- THE READ-VERIFICATION LOG WENT WITH IT, deliberately: it printed the engine's
-- movement flags, both speed reads, the position and the order point so the
-- projection could be checked against real answers. No rule consults a heading
-- any more, so the whole raw-read block was removed rather than left printing
-- values nothing reads. If a delay is ever designed back in, that block - in
-- the pre-118 source, kept under docs/backups/round118 - is where to start.
--
-- WHAT STAYED: the candidate filter (alive, more than AIR_DROP_MIN_MEN models,
-- no infantry test), the 6 m CENTRE bound and ad_centre_gap, the 0.2 s fast
-- pass with its 30 m near gate, the 250 ms poll, air_only / no_melee, the
-- self-centred cast on the OWNER, every fail-closed read, the gates in
-- FOURTH.try_pair, and the pre-cast re-check - which now only has to confirm
-- that the centre is STILL inside the line, on FRESH handles.
-- ============================================================================
FOURTH.ad_note = {}
FOURTH.ad_fast_on = {}
FOURTH.ad_fast_abilities = {}

-- THE UNIT TAG (round 112) - EVERY air-drop line names the unit that wrote it:
--     [1003] sky_junk_bomb nearest valid:'wh_main_inf_zombie_0' entities=20 ...
-- The round-112 diagnosis was taken against FOUR identical
-- wh3_main_cth_veh_sky_junk_0 units (ui ids 1002-1005) and the picker's own
-- lines carried no ui id at all, so "which of the four said this?" had to be
-- inferred from line counts in a 231 MB log. The id is the engine's
-- unique_ui_id(); an unreadable id (the unit died between the read and the log)
-- prints [?] rather than dropping the line - a line with an unknown owner is
-- still better than no line.
function FOURTH.ad_tag(unit)
	local ok_id, id = pcall(function() return unit:unique_ui_id() end)
	if not ok_id or id == nil then return "[?] " end
	return "[" .. tostring(id) .. "] "
end

-- One line per (unit, marker), and again only when the note CHANGES - the same
-- dedupe discipline as the engagement set. The air-drop rule is now checked 5x
-- a second by the fast pass, so an unchanged decision must not repeat: a parked
-- pair writes ONE line, and a decision that MOVES (another enemy, another
-- distance, another verdict) writes a new one. Every line carries the caster's
-- ui id through FOURTH.ad_tag.
function FOURTH.ad_say(unit, marker, note)
	local ok_id, id = pcall(function() return unit:unique_ui_id() end)
	if not ok_id or id == nil then return end
	local slot = tostring(id)
	local per = FOURTH.ad_note[slot]
	if per == nil then per = {}; FOURTH.ad_note[slot] = per end
	if per[marker] == note then return end
	per[marker] = note
		log("  " .. FOURTH.ad_tag(unit) .. tostring(marker) .. " " .. note)
end

-- THE CENTRE GAP (round 117) - the ONE measurement this evaluator makes:
-- the GROUND-PLANE distance between the caster's own centre and the enemy's
-- own centre, in metres, from the two documented position() reads.
--   * x/z ONLY. get_y is HEIGHT on battle_vector's ground plane; a caster 60 m
--     above the enemy is 0 m away, never 60 m.
--   * battle_vector:distance_xz(vector) is the engine's own "distance ...
--     disregarding any height difference" read; it is TRIED FIRST and the
--     plain sqrt(dx^2 + dz^2) is the fallback, so a state where the method is
--     unavailable still measures the same number.
--   * FAIL CLOSED: any read that raises, or that does not answer a NUMBER,
--     answers nil - the candidate is then not valid and nothing is cast.
-- Returns d, x1, z1, x2, z2 (the positions are returned so a caller may log
-- them; only d decides anything).
function FOURTH.ad_centre_gap(caster, enemy)
	local ok_a, a = pcall(function() return caster:position() end)
	local ok_b, b = pcall(function() return enemy:position() end)
	if not ok_a or not ok_b or a == nil or b == nil then return nil end
	local ok_x1, x1 = pcall(function() return a:get_x() end)
	local ok_z1, z1 = pcall(function() return a:get_z() end)
	local ok_x2, x2 = pcall(function() return b:get_x() end)
	local ok_z2, z2 = pcall(function() return b:get_z() end)
	if not (ok_x1 and ok_z1 and ok_x2 and ok_z2) then return nil end
	if type(x1) ~= "number" or type(z1) ~= "number"
		or type(x2) ~= "number" or type(z2) ~= "number" then return nil end
	local ok_d, d = pcall(function() return a:distance_xz(b) end)
	if not ok_d or type(d) ~= "number" then
		local dx, dz = x1 - x2, z1 - z2
		d = math.sqrt((dx * dx) + (dz * dz))
	end
	return d, x1, z1, x2, z2
end

-- ONE CANDIDATE SCAN, ONE MEASUREMENT - the whole filter, in one place, so the
-- picker and the fast pass can never disagree about who is valid.
-- Returns: nearest valid enemy, its CENTRE-to-CENTRE ground gap in metres, its
-- CURRENT model count, its type key. nil when no valid candidate exists, or
-- when the enemy army cannot be read at all (fail-closed: no candidate, no
-- cast).
-- A candidate is valid when number_of_men_alive() answers a NUMBER greater
-- than AIR_DROP_MIN_MEN AND ad_centre_gap() answers a number. Nothing else.
function FOURTH.ad_nearest(unit)
	local ok_coll, coll = pcall(function()
		return bm:get_scriptunits_for_main_enemy_army_to_local_player()
	end)
	if not ok_coll or coll == nil then return nil end
	local ok_n, n = pcall(function() return coll:count() end)
	if not ok_n or type(n) ~= "number" then return nil end
	local best, best_d, best_men, best_type = nil, nil, nil, nil
	for i = 1, n do
		local ok_su, su = pcall(function() return coll:item(i) end)
		if ok_su and su ~= nil then
			local enemy = nil
			pcall(function() enemy = su.unit end)
			if enemy ~= nil then
				local ok_alive, alive = pcall(function() return enemy:number_of_men_alive() end)
				if ok_alive and type(alive) == "number" and alive > FOURTH.AIR_DROP_MIN_MEN then
					local d = FOURTH.ad_centre_gap(unit, enemy)
					if d ~= nil and (best_d == nil or d < best_d) then
						best, best_d, best_men = enemy, d, alive
						best_type = FOURTH.type_plain(enemy)
					end
				end
			end
		end
	end
	if best == nil then return nil end
	return best, best_d, best_men, best_type
end


-- THE AIR-DROP EVALUATOR. ONE comparison decides - the NEAREST valid enemy's
-- CENTRE gap against AIR_DROP_CENTER_M - after the caster-side usage checks the
-- ability's own row declares. NO DELAY: the evaluation that measures the centre
-- inside the line FIRES on that evaluation. The enemy type, the entity count,
-- the exact CENTRE distance and this caster's ui id are written on EVERY
-- decision:
--     [1003] sky_junk_bomb nearest valid:'wh_main_inf_zombie_0' entities=20
--            centre=5.90m (need < 6.00m) -> FIRING
-- and the same line says NOT YET when the gap is at or over the line. An
-- unreadable caster side (air_only / no_melee) HOLDS with the reason.
function FOURTH.ad_pick(unit, routing)
	if routing then return nil end
	local marker = FOURTH.ad_marker or "air_drop"
	if FOURTH.ad_air_only then
		local ok_fly, flying = pcall(function() return unit:is_currently_flying() end)
		if not ok_fly or flying ~= true then
			FOURTH.ad_say(unit, marker, "airborne check: is_currently_flying() = "
				.. (ok_fly and tostring(flying) or "UNREADABLE")
				.. " -> HOLDING (this ability's row is air-only)")
			return nil
		end
	end
	if FOURTH.ad_no_melee then
		local ok_m, m = pcall(function() return unit:is_in_melee() end)
		if not ok_m then
			FOURTH.ad_say(unit, marker, "melee check: is_in_melee() UNREADABLE -> HOLDING (fail-closed)")
			return nil
		end
		if m == true then
			FOURTH.ad_say(unit, marker, "melee check: the caster is fighting in melee -> HOLDING"
				.. " (the row declares engaged_in_melee)")
			return nil
		end
	end
	local enemy, dist, men, etype = FOURTH.ad_nearest(unit)
	if enemy == nil then
		-- NOTHING VALID IS UNDER THE DROP: no candidate, so there is no decision to
		-- write and nothing to cast at. Fail closed, silently.
		return nil
	end
	etype = etype or "enemy"
	local centre_text = string.format("%.2f", dist)
	local need = string.format("%.2f", FOURTH.AIR_DROP_CENTER_M)
	if dist >= FOURTH.AIR_DROP_CENTER_M then
		-- NOT YET: the nearest valid enemy's CENTRE is at or outside the 6 m line.
		FOURTH.ad_say(unit, marker, "nearest valid:'" .. etype .. "' entities="
			.. tostring(men) .. " centre=" .. centre_text .. "m (need < " .. need .. "m) -> NOT YET")
		return nil
	end
	-- THE DECISION IS TAKEN NOW. No stamp, no wait and no second look inside the
	-- contact: the gap THIS evaluation measured is the gap the cast is made on,
	-- and the pre-cast re-check in FOURTH.try_pair confirms it before the call.
	FOURTH.ad_say(unit, marker, "nearest valid:'" .. etype .. "' entities="
		.. tostring(men) .. " centre=" .. centre_text .. "m (need < " .. need .. "m) -> FIRING"
		.. " (the nearest of the valid enemies; the gap is centre-to-centre, x/z)")
	FOURTH.ad_enemy = enemy
	FOURTH.ad_caster_su = FOURTH.eg_fresh_caster_su(unit)
	return "nearest valid '" .. etype .. "' has " .. tostring(men)
		.. " models, its CENTRE gap is " .. centre_text .. "m - under the " .. need
		.. "m line"
end

-- THE TRIGGER NAME STAYS `air_drop_on_infantry` (the entries, the tooltip map and
-- every harness pin key on it); only the RULE behind it changed.
function FOURTH.evaluate_air_drop_on_infantry(unit, routing)
	return FOURTH.ad_pick(unit, routing)
end

-- ============================================================================
-- ROUND 130 - THE FIRST TRIGGERS ON THE FIRING FLAG (user rulings 2026-11-01:
-- Restock! and Ballistics Calibration "both recommended options"; Skjalandir's
-- Fall "shooting into melee"). The firing flag (round 126, FOURTH.ammo_probe) is
-- read per unit through FOURTH.ammo_by_id, which the probe fills on the same poll,
-- before any trigger runs.
--   restock (Restock!): an ally within the 70 m bound that is SHOOTING (firing
--     flag on) with RESTOCK_AT_FRACTION (70%) or less of its ammunition left; the
--     one with the least left is the cast target. 70% = 100% - the 30% the
--     ability refills, so no refill is wasted. An ally refilled in the last
--     RESTOCK_CLAIM_S is skipped, so two casters never refill the same unit.
--   allies_firing_aura: at least FIRING_AURA_MIN units (ROUND 131: 1, the caster
--     counting) within the aura bound (70% of the effect_range) are shooting and
--     past their cast point. Ballistics Calibration is cast on the ground at the
--     caster's own feet; the self-centred auras (round 131) on the caster.
--   skjalandirs_fall: the melee trigger it had, OR the unit itself is shooting,
--     past its cast point, at a target that is in melee.
-- ============================================================================
FOURTH.RESTOCK_AT_FRACTION = 0.70   -- 1 - the 0.30 the ability refills ("Replenishes ammo: 0.3000")
FOURTH.RESTOCK_CLAIM_S = 12         -- the ability's active_time (10 s) + IN_FLIGHT_SETTLE_SECONDS (2 s)
FOURTH.FIRING_AURA_MIN = 1          -- units shooting inside the aura bound, the caster counting (user, round 131;
                                    -- round 130 asked for 2 allies)
FOURTH.ammo_by_id = {}              -- ui id (string) -> that unit's firing-flag state
FOURTH.ammo_claimed = {}            -- ui id (string) -> the poll a Restock! was cast on it
FOURTH.ammo_claim_id = nil          -- the ally the current Restock! pick chose
FOURTH.fa_bound_m = nil             -- the current entry's aura bound (set per entry by the poll)

-- the firing-flag state of a unit, and its ui id (nil when unknown)
function FOURTH.firing_state(unit)
	local id = nil
	pcall(function() id = tostring(unit:unique_ui_id()) end)
	if id == nil then return nil, nil end
	return FOURTH.ammo_by_id[id], id
end

-- the ammunition fraction left (0..1) of a unit that is SHOOTING now; nil when it
-- is not shooting, has no ammunition read, or was refilled in the last
-- RESTOCK_CLAIM_S.
function FOURTH.ammo_fraction_if_firing(unit)
	local st, id = FOURTH.firing_state(unit)
	if st == nil or st.firing ~= true or type(st.start) ~= "number" or st.start <= 0
		or type(st.last) ~= "number" then
		return nil
	end
	local at = FOURTH.ammo_claimed[id]
	if at ~= nil and (tick_count - at) < math.floor((FOURTH.RESTOCK_CLAIM_S * 1000) / POLL_MS) then
		return nil
	end
	return st.last / st.start
end

-- true while the unit is shooting AND past its cast point (first shot + 0.5 x reload)
function FOURTH.shooting_past_cast_point(unit)
	local st = FOURTH.firing_state(unit)
	return st ~= nil and st.firing == true and st.cast_point_passed == true
end

-- ally_ammo_low (Restock!): the shared ally picker, family "ammo".
function FOURTH.evaluate_ally_ammo_low(unit, routing)
	return FOURTH.ab_pick_ally(unit, routing, "ammo")
end

-- the number of OTHER friendly units (alive, not routing) within the current
-- entry's aura bound of `unit` that are shooting past their cast point. An
-- unreadable distance does not count (fail-closed).
function FOURTH.count_allies_firing_near(unit)
	local bound = FOURTH.fa_bound_m
	if bound == nil or tracked_units == nil then return 0, bound end
	local self_id = tostring(unit:unique_ui_id())
	local n = 0
	for i = 1, #tracked_units do
		local other = tracked_units[i] and tracked_units[i].unit
		if other ~= nil and other ~= unit then
			local ok_m, men = pcall(function() return other:number_of_men_alive() end)
			local ok_i, oid = pcall(function() return tostring(other:unique_ui_id()) end)
			if ok_m and type(men) == "number" and men > 0 and ok_i and oid ~= self_id
				and not unit_is_routing(other) and FOURTH.shooting_past_cast_point(other) then
				local gap = FOURTH.ab_ally_gap(unit, other)
				if gap ~= nil and gap <= bound then n = n + 1 end
			end
		end
	end
	return n, bound
end

-- allies_firing_aura (Ballistics Calibration and, from round 131, the self-centred
-- shooting auras): enough units shooting around the caster, the caster counting;
-- Ballistics Calibration is a ground key (cast at the caster's own position), the
-- others are cast on the caster.
function FOURTH.evaluate_allies_firing_aura(unit, routing)
	if routing then return nil end
	local n, bound = FOURTH.count_allies_firing_near(unit)
	-- ROUND 131: the caster counts too (user: "at least 1 ... caster counts")
	local own = FOURTH.shooting_past_cast_point(unit) and 1 or 0
	if n + own < FOURTH.FIRING_AURA_MIN then return nil end
	return string.format("%s: %d unit(s) within %sm are shooting past their cast point (%d allies + the caster %s; need %d), cast centred on the caster",
		tostring(FOURTH.ab_marker or "aura"), n + own, tostring(bound), n,
		(own == 1) and "shooting" or "not shooting", FOURTH.FIRING_AURA_MIN)
end

-- melee_or_shooting_into_melee (Skjalandir's Fall): the in-melee self trigger it
-- had, OR the unit is shooting (past its cast point) at a target that is in
-- melee. Not while routing or wavering.
function FOURTH.evaluate_melee_or_shooting_into_melee(unit, routing)
	local r = FOURTH.evaluate_in_melee_self(unit, routing)
	if r ~= nil then return r end
	if routing or FOURTH.wavering(unit) == true then return nil end
	if not FOURTH.shooting_past_cast_point(unit) then return nil end
	local ok_t, t = pcall(function() return unit:current_target() end)
	if not ok_t or t == nil then return nil end
	local ok_m, m = pcall(function() return t:is_in_melee() end)
	if not ok_m or m ~= true then return nil end
	return "shooting past its cast point at a target that is in melee, cast on self"
end

-- ============================================================================
-- ROUND 131 - THE SHOOTING BUFFS LEAVE THE MELEE TRIGGER (user rulings 2026-11-01).
--   self_or_ally_shooting (Deranged Munitions): the caster shooting past its cast
--     point -> cast on self; otherwise the closest ally within the 70% bound that
--     is shooting past its cast point -> cast on that ally ("Self, else a
--     shooting ally").
--   melee_or_self_or_ally_shooting (Entrenchment): in melee (as melee_unwavering:
--     the +20 physical resistance) -> self; otherwise as self_or_ally_shooting.
--     The target cannot move for 44 s (the user accepted rooting an ally).
--   no_enemy_in_range_within_boost (Potion of Farsight, 1 use): NO enemy inside
--     the unit's own live missile_range() AND at least one enemy inside
--     missile_range x FARSIGHT_BAND - the range the potion would give, with the
--     standing 70% rule applied to the +30% bonus (1 + 0.30 x 0.70 = 1.21). Not
--     in melee, ammunition left, every read fail-closed. unit_distance is edge to
--     edge, the same measure the firing flag's in-range read uses.
-- ============================================================================
FOURTH.FARSIGHT_BONUS = 0.30   -- Potion of Farsight: "Range: +30%" (the game's own phase stat)
FOURTH.FARSIGHT_BAND = 1 + FOURTH.FARSIGHT_BONUS * FOURTH.RANGE_FRACTION   -- 1.21

-- the nearest LIVE enemy's edge-to-edge gap from `unit`, and whether ANY live
-- enemy is within `inner` metres; nil when the enemy list cannot be read.
function FOURTH.nearest_enemy_gap(unit, inner)
	local ok_coll, coll = pcall(function()
		return bm:get_scriptunits_for_main_enemy_army_to_local_player()
	end)
	if not ok_coll or coll == nil then return nil, nil end
	local ok_n, n = pcall(function() return coll:count() end)
	if not ok_n or type(n) ~= "number" then return nil, nil end
	local best, any_inner = nil, false
	for i = 1, n do
		local ok_su, su = pcall(function() return coll:item(i) end)
		local enemy = nil
		if ok_su and su ~= nil then pcall(function() enemy = su.unit end) end
		if enemy ~= nil then
			local ok_a, alive = pcall(function() return enemy:number_of_men_alive() end)
			local ok_g, gap = pcall(function() return unit:unit_distance(enemy) end)
			if ok_a and type(alive) == "number" and alive > 0 and ok_g and type(gap) == "number" and gap >= 0 then
				if best == nil or gap < best then best = gap end
				if gap <= inner then any_inner = true end
			end
		end
	end
	return best, any_inner
end

function FOURTH.evaluate_self_or_ally_shooting(unit, routing)
	if routing then return nil end
	if FOURTH.shooting_past_cast_point(unit) then
		return "the caster is shooting past its cast point, cast on self"
	end
	return FOURTH.ab_pick_ally(unit, routing, "shooting")
end

function FOURTH.evaluate_melee_or_self_or_ally_shooting(unit, routing)
	local r = FOURTH.evaluate_in_melee_self(unit, routing)
	if r ~= nil then return r end
	return FOURTH.evaluate_self_or_ally_shooting(unit, routing)
end

function FOURTH.evaluate_no_enemy_in_range_within_boost(unit, routing)
	if routing then return nil end
	local ok_mel, mel = pcall(function() return unit:is_in_melee() end)
	if not ok_mel or mel ~= false then return nil end
	local ok_am, am = pcall(function() return unit:ammo_left() end)
	if not ok_am or type(am) ~= "number" or am <= 0 then return nil end
	local ok_r, r = pcall(function() return unit:missile_range() end)
	if not ok_r or type(r) ~= "number" or r <= 0 then return nil end
	local nearest, any_in_range = FOURTH.nearest_enemy_gap(unit, r)
	if nearest == nil or any_in_range then return nil end
	local outer = r * FOURTH.FARSIGHT_BAND
	if nearest > outer then return nil end
	return string.format("no enemy inside the missile range %.1fm; the nearest enemy is at %.1fm, inside range x %.2f = %.1fm, cast on self",
		r, nearest, FOURTH.FARSIGHT_BAND, outer)
end

-- ============================================================================
-- ROUND 132 - AUDIT BATCH 1 (user rulings 2026-11-08, all as recommended).
--   melee_or_shooting_aura (Enchanted Metallurgy x4, Master of Alchemy x4, Embers
--     of the Phoenix, Horn of Vaul): the Metallurgy melee rule unchanged (the
--     caster in melee, or the closest ally in melee within 24 m), OR the caster or
--     any unit within the aura bound (24 m = 70% of 35 m) shooting past its cast
--     point. Cast on the caster. The user's own 2026-10 rule for Metallurgy ("When
--     self or ally in range in melee. When ally in range is shooting."), whose
--     shooting half needed the firing flag.
--   melee_or_shooting_self_or_ally (The Seerstaff of Saphery, Harmonic
--     Convergence): the caster in melee (not wavering) or shooting -> self;
--     otherwise the closest ally within 140 m (70% of 200 m) in melee or shooting.
--   self_shooting (Boom!): the unit itself shooting past its cast point.
-- ============================================================================

-- true while the unit is in melee or shooting past its cast point (an
-- unreadable melee read counts as not in melee)
function FOURTH.fighting(unit)
	local ok_m, m = pcall(function() return unit:is_in_melee() end)
	if ok_m and m == true then return true end
	return FOURTH.shooting_past_cast_point(unit)
end

function FOURTH.evaluate_melee_or_shooting_aura(unit, routing)
	local r = FOURTH.evaluate_metallurgy_melee(unit, routing)
	if r ~= nil then return r end
	if routing then return nil end
	local n, bound = FOURTH.count_allies_firing_near(unit)
	local own = FOURTH.shooting_past_cast_point(unit) and 1 or 0
	if n + own < 1 then return nil end
	return string.format("%s: nobody in melee within reach; %d unit(s) within %sm are shooting past their cast point (%d allies + the caster %s), cast centred on the caster",
		tostring(FOURTH.ab_marker or "aura"), n + own, tostring(bound), n,
		(own == 1) and "shooting" or "not shooting")
end

function FOURTH.evaluate_melee_or_shooting_self_or_ally(unit, routing)
	if routing then return nil end
	local r = FOURTH.evaluate_in_melee_self(unit, routing)
	if r ~= nil then return r .. ", cast on self" end
	if FOURTH.shooting_past_cast_point(unit) then
		return "the caster is shooting past its cast point, cast on self"
	end
	return FOURTH.ab_pick_ally(unit, routing, "fighting")
end

function FOURTH.evaluate_self_shooting(unit, routing)
	if routing then return nil end
	if not FOURTH.shooting_past_cast_point(unit) then return nil end
	return "the unit is shooting past its cast point, cast on self"
end

-- ============================================================================
-- ROUND 133 - AUDIT BATCH 2: PROTECTION AGAINST SHOTS (user rulings 2026-11-08).
--   under_fire (Shield of Chaqua, The Golden Eye of Tzeentch, The Lion's Shield):
--     the caster under missile fire; for an aura (Shield of Chaqua) also any
--     friendly unit within the aura bound (70% of the effect_range). No melee arm.
--   melee_or_under_fire (The Blessed Helm of the Oblast, The Bane Shield, Charmed
--     Shield, Glacial Defence): the caster in melee (not wavering) or under fire;
--     for an aura also any friendly unit within the bound in melee or under fire.
--   The read is battle_unit:is_under_missile_attack() (the enemy picker's read);
--   only an exact true counts. Cast on the caster.
-- ============================================================================

-- true only when the engine answers exactly true
function FOURTH.under_fire(unit)
	local ok, v = pcall(function() return unit:is_under_missile_attack() end)
	return ok and v == true
end

-- the closest OTHER friendly unit (alive, not routing) within the current entry's
-- aura bound that passes test(u); nil when the entry has no aura or none passes.
-- An unreadable distance does not count.
function FOURTH.ally_in_aura(unit, test)
	local bound = FOURTH.fa_bound_m
	if bound == nil or tracked_units == nil then return nil, nil end
	local self_id = tostring(unit:unique_ui_id())
	local best, best_gap = nil, nil
	for i = 1, #tracked_units do
		local other = tracked_units[i] and tracked_units[i].unit
		if other ~= nil and other ~= unit then
			local ok_m, men = pcall(function() return other:number_of_men_alive() end)
			local ok_i, oid = pcall(function() return tostring(other:unique_ui_id()) end)
			if ok_m and type(men) == "number" and men > 0 and ok_i and oid ~= self_id
				and not unit_is_routing(other) and test(other) then
				local gap = FOURTH.ab_ally_gap(unit, other)
				if gap ~= nil and gap <= bound and (best_gap == nil or gap < best_gap) then
					best, best_gap = other, gap
				end
			end
		end
	end
	return best, best_gap
end

function FOURTH.melee_now(u)
	local ok, v = pcall(function() return u:is_in_melee() end)
	return ok and v == true
end

function FOURTH.melee_or_under_fire(u)
	return FOURTH.melee_now(u) or FOURTH.under_fire(u)
end

function FOURTH.evaluate_under_fire(unit, routing)
	if routing then return nil end
	if FOURTH.under_fire(unit) then return "the caster is under missile fire, cast on self" end
	local ally, gap = FOURTH.ally_in_aura(unit, FOURTH.under_fire)
	if ally == nil then return nil end
	return string.format("a friendly unit %.1fm away (bound %sm) is under missile fire, cast centred on the caster",
		gap, tostring(FOURTH.fa_bound_m))
end

function FOURTH.evaluate_melee_or_under_fire(unit, routing)
	local r = FOURTH.evaluate_in_melee_self(unit, routing)
	if r ~= nil then return r .. ", cast on self" end
	if routing then return nil end
	if FOURTH.under_fire(unit) then return "the caster is under missile fire, cast on self" end
	local ally, gap = FOURTH.ally_in_aura(unit, FOURTH.melee_or_under_fire)
	if ally == nil then return nil end
	return string.format("a friendly unit %.1fm away (bound %sm) is in melee or under missile fire, cast centred on the caster",
		gap, tostring(FOURTH.fa_bound_m))
end

-- ============================================================================
-- ROUND 135 - AUDIT BATCH 4: THE ENEMY SLOWS AND THE TARGET FILTERS
-- (user rulings 2026-11-09).
--   enemy_melee gains the 11 slows that also cut melee stats (no missile arm).
--   enemy_fast_near_ally (NEW; Mither, Rune of Slowness, Master Rune of
--     Slowness, Whispering Mist), the user's own design: the closest enemy
--     inside the ability's 70% cast bound that is MOVING, has a run speed of
--     FAST_ENEMY_MPS or more (fast_speed(), the unit's live run speed in m/s)
--     and is within FAST_ENEMY_NEAR_M of one of our units (edge to edge, the
--     caster counting). No charge detection. Cast at that enemy.
--   target_class (15 entries): the engine refuses an enemy outside the
--     ability's own invalid-target flags, so the picker skips it:
--     "commander" (Lord/Hero only), "large", "large_single" (large and a
--     single entity). The large and single sets are GENERATED from the game
--     data (tools/gen_unit_size_keys.py); an unreadable type never qualifies.
--   ROUND 136 (audit batch 5): 20 melee hexes join enemy_melee; Gaze of Fate,
--     Sadistic Snare and Spearfisher's Net join enemy_fast_near_ally; the class
--     "not_flying" (Spearfisher's Net) reads is_currently_flying() live.
-- ============================================================================
FOURTH.FAST_ENEMY_MPS = 5      -- user setting 2026-11-09 ("at least cavalry speed": 5 m/s run speed)
FOURTH.FAST_ENEMY_NEAR_M = 40  -- user setting 2026-11-09: closeness to one of our units, edge to edge
                               -- (a user-set test value, not an ability range: the cast bound stays 70%)
FOURTH.eg_class = nil

-- GENERATED by tools/gen_unit_size_keys.py from battle_entities, mounts, land_units and
-- main_units (round 135); the build refuses a pack whose tables differ from the game data.
-- large: man_entity or mount entity size large/very_large. single: num_men == 1.
FOURTH.class_keys.large = {
	["wh2_dlc09_tmb_cav_necropolis_knights_0"] = true,
	["wh2_dlc09_tmb_cav_necropolis_knights_1"] = true,
	["wh2_dlc09_tmb_cav_necropolis_knights_ror"] = true,
	["wh2_dlc09_tmb_cha_arkhan_2"] = true,
	["wh2_dlc09_tmb_cha_khalida_1"] = true,
	["wh2_dlc09_tmb_cha_khalida_2"] = true,
	["wh2_dlc09_tmb_cha_khatep_2"] = true,
	["wh2_dlc09_tmb_cha_necrotect_1"] = true,
	["wh2_dlc09_tmb_cha_settra_2"] = true,
	["wh2_dlc09_tmb_cha_settra_3"] = true,
	["wh2_dlc09_tmb_cha_tomb_king_2"] = true,
	["wh2_dlc09_tmb_cha_tomb_king_3"] = true,
	["wh2_dlc09_tmb_cha_tomb_prince_2"] = true,
	["wh2_dlc09_tmb_mon_carrion_ror"] = true,
	["wh2_dlc09_tmb_mon_crypt_horrors"] = true,
	["wh2_dlc09_tmb_mon_heirotitan_0"] = true,
	["wh2_dlc09_tmb_mon_khemrian_warsphinx_0"] = true,
	["wh2_dlc09_tmb_mon_morghast_archai"] = true,
	["wh2_dlc09_tmb_mon_morghast_harbingers"] = true,
	["wh2_dlc09_tmb_mon_necrosphinx_0"] = true,
	["wh2_dlc09_tmb_mon_necrosphinx_ror"] = true,
	["wh2_dlc09_tmb_mon_sepulchral_stalkers_0"] = true,
	["wh2_dlc09_tmb_mon_sepulchral_stalkers_ror"] = true,
	["wh2_dlc09_tmb_mon_tomb_scorpion_0"] = true,
	["wh2_dlc09_tmb_mon_ushabti_0"] = true,
	["wh2_dlc09_tmb_mon_ushabti_0_summoned"] = true,
	["wh2_dlc09_tmb_mon_ushabti_1"] = true,
	["wh2_dlc09_tmb_mon_ushabti_ror"] = true,
	["wh2_dlc09_tmb_veh_skeleton_archer_chariot_0"] = true,
	["wh2_dlc09_tmb_veh_skeleton_chariot_0"] = true,
	["wh2_dlc09_tmb_veh_skeleton_chariot_0_summoned"] = true,
	["wh2_dlc10_def_cha_crone_5"] = true,
	["wh2_dlc10_def_cha_supreme_sorceress_beasts_4"] = true,
	["wh2_dlc10_def_cha_supreme_sorceress_beasts_5"] = true,
	["wh2_dlc10_def_cha_supreme_sorceress_dark_4"] = true,
	["wh2_dlc10_def_cha_supreme_sorceress_dark_5"] = true,
	["wh2_dlc10_def_cha_supreme_sorceress_death_4"] = true,
	["wh2_dlc10_def_cha_supreme_sorceress_death_5"] = true,
	["wh2_dlc10_def_cha_supreme_sorceress_fire_4"] = true,
	["wh2_dlc10_def_cha_supreme_sorceress_fire_5"] = true,
	["wh2_dlc10_def_cha_supreme_sorceress_shadow_4"] = true,
	["wh2_dlc10_def_cha_supreme_sorceress_shadow_5"] = true,
	["wh2_dlc10_def_mon_chill_of_sontar_ror_0"] = true,
	["wh2_dlc10_def_mon_feral_manticore_0"] = true,
	["wh2_dlc10_def_mon_kharibdyss_0"] = true,
	["wh2_dlc10_def_mon_war_hydra_boss"] = true,
	["wh2_dlc10_hef_cha_alarielle_the_radiant_3"] = true,
	["wh2_dlc10_hef_cha_mage_heavens_2"] = true,
	["wh2_dlc10_hef_cha_mage_shadows_2"] = true,
	["wh2_dlc10_hef_mon_treekin_0"] = true,
	["wh2_dlc10_hef_mon_treeman_0"] = true,
	["wh2_dlc10_lzd_mon_carnosaur_boss"] = true,
	["wh2_dlc10_nor_mon_phoenix_flamespyre_boss"] = true,
	["wh2_dlc10_skv_mon_hell_pit_abomination_boss"] = true,
	["wh2_dlc11_cst_cav_deck_droppers_0"] = true,
	["wh2_dlc11_cst_cav_deck_droppers_1"] = true,
	["wh2_dlc11_cst_cav_deck_droppers_2"] = true,
	["wh2_dlc11_cst_cav_deck_droppers_ror_0"] = true,
	["wh2_dlc11_cst_cha_aranessa_1"] = true,
	["wh2_dlc11_cst_cha_cylostra_direfin_1"] = true,
	["wh2_dlc11_cst_cha_gunnery_wight_1"] = true,
	["wh2_dlc11_cst_cha_luthor_harkon_1"] = true,
	["wh2_dlc11_cst_cha_mourngul_haunter"] = true,
	["wh2_dlc11_cst_cha_vampire_fleet_admiral_1"] = true,
	["wh2_dlc11_cst_cha_vampire_fleet_admiral_death_1"] = true,
	["wh2_dlc11_cst_cha_vampire_fleet_admiral_deeps_1"] = true,
	["wh2_dlc11_cst_cha_vampire_fleet_admiral_female_1"] = true,
	["wh2_dlc11_cst_cha_vampire_fleet_admiral_female_death_1"] = true,
	["wh2_dlc11_cst_cha_vampire_fleet_admiral_female_deeps_1"] = true,
	["wh2_dlc11_cst_cha_vampire_fleet_captain_1"] = true,
	["wh2_dlc11_cst_cha_vampire_fleet_captain_death_1"] = true,
	["wh2_dlc11_cst_cha_vampire_fleet_captain_deeps_1"] = true,
	["wh2_dlc11_cst_inf_count_noctilus_1"] = true,
	["wh2_dlc11_cst_mon_animated_hulks_0"] = true,
	["wh2_dlc11_cst_mon_bloated_corpse_0"] = true,
	["wh2_dlc11_cst_mon_mournguls_0"] = true,
	["wh2_dlc11_cst_mon_mournguls_ror_0"] = true,
	["wh2_dlc11_cst_mon_necrofex_colossus_0"] = true,
	["wh2_dlc11_cst_mon_necrofex_colossus_ror_0"] = true,
	["wh2_dlc11_cst_mon_rotting_leviathan_0"] = true,
	["wh2_dlc11_cst_mon_rotting_prometheans_0"] = true,
	["wh2_dlc11_cst_mon_rotting_prometheans_gunnery_mob_0"] = true,
	["wh2_dlc11_cst_mon_rotting_prometheans_gunnery_mob_ror"] = true,
	["wh2_dlc11_cst_mon_rotting_prometheans_summoned_0"] = true,
	["wh2_dlc11_cst_mon_terrorgheist"] = true,
	["wh2_dlc11_def_cha_lokhir_fellheart_1"] = true,
	["wh2_dlc11_vmp_cha_bloodline_blood_dragon_lord_3"] = true,
	["wh2_dlc11_vmp_cha_bloodline_lahmian_lord_3"] = true,
	["wh2_dlc11_vmp_cha_bloodline_necrarch_lord_3"] = true,
	["wh2_dlc11_vmp_cha_bloodline_strigoi_lord_1"] = true,
	["wh2_dlc11_vmp_cha_bloodline_von_carstein_lord_3"] = true,
	["wh2_dlc11_vmp_mon_varghulf_summoned"] = true,
	["wh2_dlc12_lzd_cav_ripperdactyl_riders_0"] = true,
	["wh2_dlc12_lzd_cav_ripperdactyl_riders_0_blessed"] = true,
	["wh2_dlc12_lzd_cav_ripperdactyl_riders_ror_0"] = true,
	["wh2_dlc12_lzd_cav_terradon_riders_0_tlaqua"] = true,
	["wh2_dlc12_lzd_cav_terradon_riders_1_tlaqua"] = true,
	["wh2_dlc12_lzd_cav_terradon_riders_ror_0"] = true,
	["wh2_dlc12_lzd_cha_skink_chief_red_crested_1"] = true,
	["wh2_dlc12_lzd_cha_skink_chief_red_crested_2"] = true,
	["wh2_dlc12_lzd_cha_skink_chief_red_crested_3"] = true,
	["wh2_dlc12_lzd_cha_skink_priest_beasts_4"] = true,
	["wh2_dlc12_lzd_cha_skink_priest_heavens_4"] = true,
	["wh2_dlc12_lzd_cha_tehenhauin_2"] = true,
	["wh2_dlc12_lzd_cha_tehenhauin_3"] = true,
	["wh2_dlc12_lzd_cha_tiktaqto_1"] = true,
	["wh2_dlc12_lzd_lzd_cha_kroak_0"] = true,
	["wh2_dlc12_lzd_lzd_cha_kroak_0_boss"] = true,
	["wh2_dlc12_lzd_mon_ancient_salamander_0"] = true,
	["wh2_dlc12_lzd_mon_ancient_salamander_0_blessed"] = true,
	["wh2_dlc12_lzd_mon_ancient_stegadon_1"] = true,
	["wh2_dlc12_lzd_mon_ancient_stegadon_ror_0"] = true,
	["wh2_dlc12_lzd_mon_bastiladon_3"] = true,
	["wh2_dlc12_skv_cha_ikit_claw_2"] = true,
	["wh2_dlc13_emp_veh_steam_tank_driver_ror_0"] = true,
	["wh2_dlc13_emp_veh_war_wagon_0"] = true,
	["wh2_dlc13_emp_veh_war_wagon_1"] = true,
	["wh2_dlc13_emp_veh_war_wagon_ror_0"] = true,
	["wh2_dlc13_huntmarshall_veh_obsinite_gyrocopter_0"] = true,
	["wh2_dlc13_lzd_cha_kroxigor_ancient_0"] = true,
	["wh2_dlc13_lzd_cha_nakai_0"] = true,
	["wh2_dlc13_lzd_cha_slann_mage_priest_beasts_0"] = true,
	["wh2_dlc13_lzd_cha_slann_mage_priest_death_0"] = true,
	["wh2_dlc13_lzd_cha_slann_mage_priest_fire_0"] = true,
	["wh2_dlc13_lzd_cha_slann_mage_priest_life_0"] = true,
	["wh2_dlc13_lzd_cha_slann_mage_priest_metal_0"] = true,
	["wh2_dlc13_lzd_cha_slann_mage_priest_shadows_0"] = true,
	["wh2_dlc13_lzd_mon_dread_saurian_0"] = true,
	["wh2_dlc13_lzd_mon_dread_saurian_1"] = true,
	["wh2_dlc13_lzd_mon_dread_saurian_ror_0"] = true,
	["wh2_dlc13_lzd_mon_sacred_kroxigors_0"] = true,
	["wh2_dlc13_lzd_mon_sacred_kroxigors_0_blessed"] = true,
	["wh2_dlc13_lzd_mon_sacred_kroxigors_ror_0"] = true,
	["wh2_dlc14_brt_cha_henri_le_massif_3"] = true,
	["wh2_dlc14_def_cav_scourgerunner_chariot_0"] = true,
	["wh2_dlc14_def_cav_scourgerunner_chariot_ror_0"] = true,
	["wh2_dlc14_def_cha_high_beastmaster_1"] = true,
	["wh2_dlc14_def_cha_high_beastmaster_2"] = true,
	["wh2_dlc14_def_cha_master_4"] = true,
	["wh2_dlc14_def_mon_bloodwrack_medusa_0"] = true,
	["wh2_dlc14_def_mon_bloodwrack_medusa_ror_0"] = true,
	["wh2_dlc14_def_veh_bloodwrack_shrine_0"] = true,
	["wh2_dlc15_grn_cha_grom_the_paunch_0"] = true,
	["wh2_dlc15_grn_cha_night_goblin_warboss_0_big"] = true,
	["wh2_dlc15_grn_cha_river_troll_hag_0"] = true,
	["wh2_dlc15_grn_mon_arachnarok_spider_waaagh_0"] = true,
	["wh2_dlc15_grn_mon_feral_hydra_waaagh_0"] = true,
	["wh2_dlc15_grn_mon_river_trolls_0"] = true,
	["wh2_dlc15_grn_mon_river_trolls_ror_0"] = true,
	["wh2_dlc15_grn_mon_rogue_idol_0"] = true,
	["wh2_dlc15_grn_mon_rogue_idol_ror_0"] = true,
	["wh2_dlc15_grn_mon_rogue_idol_summoned_0"] = true,
	["wh2_dlc15_grn_mon_stone_trolls_0"] = true,
	["wh2_dlc15_grn_mon_wyvern_waaagh_0"] = true,
	["wh2_dlc15_grn_veh_snotling_pump_wagon_0"] = true,
	["wh2_dlc15_grn_veh_snotling_pump_wagon_flappas_0"] = true,
	["wh2_dlc15_grn_veh_snotling_pump_wagon_roller_0"] = true,
	["wh2_dlc15_grn_veh_snotling_pump_wagon_ror_0"] = true,
	["wh2_dlc15_hef_cha_alastar_1"] = true,
	["wh2_dlc15_hef_cha_archmage_beasts_2"] = true,
	["wh2_dlc15_hef_cha_archmage_beasts_3"] = true,
	["wh2_dlc15_hef_cha_archmage_beasts_4"] = true,
	["wh2_dlc15_hef_cha_archmage_death_2"] = true,
	["wh2_dlc15_hef_cha_archmage_death_3"] = true,
	["wh2_dlc15_hef_cha_archmage_death_4"] = true,
	["wh2_dlc15_hef_cha_archmage_fire_2"] = true,
	["wh2_dlc15_hef_cha_archmage_fire_3"] = true,
	["wh2_dlc15_hef_cha_archmage_fire_4"] = true,
	["wh2_dlc15_hef_cha_archmage_heavens_2"] = true,
	["wh2_dlc15_hef_cha_archmage_heavens_3"] = true,
	["wh2_dlc15_hef_cha_archmage_heavens_4"] = true,
	["wh2_dlc15_hef_cha_archmage_high_2"] = true,
	["wh2_dlc15_hef_cha_archmage_high_3"] = true,
	["wh2_dlc15_hef_cha_archmage_high_4"] = true,
	["wh2_dlc15_hef_cha_archmage_life_2"] = true,
	["wh2_dlc15_hef_cha_archmage_life_3"] = true,
	["wh2_dlc15_hef_cha_archmage_life_4"] = true,
	["wh2_dlc15_hef_cha_archmage_light_2"] = true,
	["wh2_dlc15_hef_cha_archmage_light_3"] = true,
	["wh2_dlc15_hef_cha_archmage_light_4"] = true,
	["wh2_dlc15_hef_cha_archmage_metal_2"] = true,
	["wh2_dlc15_hef_cha_archmage_metal_3"] = true,
	["wh2_dlc15_hef_cha_archmage_metal_4"] = true,
	["wh2_dlc15_hef_cha_archmage_shadows_2"] = true,
	["wh2_dlc15_hef_cha_archmage_shadows_3"] = true,
	["wh2_dlc15_hef_cha_archmage_shadows_4"] = true,
	["wh2_dlc15_hef_cha_eltharion_the_grim_2"] = true,
	["wh2_dlc15_hef_cha_imrik_2"] = true,
	["wh2_dlc15_hef_cha_mage_beasts_2"] = true,
	["wh2_dlc15_hef_cha_mage_death_2"] = true,
	["wh2_dlc15_hef_cha_mage_fire_2"] = true,
	["wh2_dlc15_hef_cha_mage_fire_3"] = true,
	["wh2_dlc15_hef_cha_mage_metal_2"] = true,
	["wh2_dlc15_hef_cha_prince_6"] = true,
	["wh2_dlc15_hef_cha_princess_6"] = true,
	["wh2_dlc15_hef_cha_teclis_2"] = true,
	["wh2_dlc15_hef_inf_mistwalkers_griffon_knights_0"] = true,
	["wh2_dlc15_hef_mon_arcane_phoenix_0"] = true,
	["wh2_dlc15_hef_mon_arcane_phoenix_ror_0"] = true,
	["wh2_dlc15_hef_mon_black_dragon_imrik"] = true,
	["wh2_dlc15_hef_mon_black_dragon_imrik_boss"] = true,
	["wh2_dlc15_hef_mon_forest_dragon_0"] = true,
	["wh2_dlc15_hef_mon_forest_dragon_imrik"] = true,
	["wh2_dlc15_hef_mon_forest_dragon_imrik_boss"] = true,
	["wh2_dlc15_hef_mon_moon_dragon_imrik"] = true,
	["wh2_dlc15_hef_mon_moon_dragon_imrik_boss"] = true,
	["wh2_dlc15_hef_mon_star_dragon_imrik"] = true,
	["wh2_dlc15_hef_mon_star_dragon_imrik_boss"] = true,
	["wh2_dlc15_hef_mon_sun_dragon_imrik"] = true,
	["wh2_dlc15_hef_mon_sun_dragon_imrik_boss"] = true,
	["wh2_dlc15_hef_veh_lion_chariot_of_chrace_0"] = true,
	["wh2_dlc16_skv_cha_chieftain_1"] = true,
	["wh2_dlc16_skv_cha_ghoritch_0"] = true,
	["wh2_dlc16_skv_cha_ghoritch_0_boss"] = true,
	["wh2_dlc16_skv_cha_packmaster_2"] = true,
	["wh2_dlc16_skv_cha_throt_the_unclean_2"] = true,
	["wh2_dlc16_skv_cha_warlord_2"] = true,
	["wh2_dlc16_skv_mon_brood_horror_0"] = true,
	["wh2_dlc16_skv_mon_hell_pit_abomination_ror_0"] = true,
	["wh2_dlc16_skv_mon_rat_ogre_mutant"] = true,
	["wh2_dlc16_skv_mon_rat_ogre_mutant_ror_0"] = true,
	["wh2_dlc16_skv_mon_rat_ogres_ror_0"] = true,
	["wh2_dlc16_skv_mon_rat_ogres_summoned"] = true,
	["wh2_dlc16_wef_cha_ancient_treeman_coeddil_0"] = true,
	["wh2_dlc16_wef_cha_ariel_0"] = true,
	["wh2_dlc16_wef_cha_malicious_ancient_treeman_beasts_0"] = true,
	["wh2_dlc16_wef_cha_malicious_ancient_treeman_life_0"] = true,
	["wh2_dlc16_wef_cha_malicious_ancient_treeman_shadows_0"] = true,
	["wh2_dlc16_wef_cha_sisters_of_twilight_0"] = true,
	["wh2_dlc16_wef_cha_sisters_of_twilight_1"] = true,
	["wh2_dlc16_wef_cha_spellweaver_beasts_3"] = true,
	["wh2_dlc16_wef_cha_spellweaver_dark_3"] = true,
	["wh2_dlc16_wef_cha_spellweaver_high_3"] = true,
	["wh2_dlc16_wef_cha_spellweaver_life_3"] = true,
	["wh2_dlc16_wef_cha_spellweaver_shadows_3"] = true,
	["wh2_dlc16_wef_mon_ceithin_har_summoned"] = true,
	["wh2_dlc16_wef_mon_feral_manticore"] = true,
	["wh2_dlc16_wef_mon_gwindalor_summoned"] = true,
	["wh2_dlc16_wef_mon_malicious_treekin_0"] = true,
	["wh2_dlc16_wef_mon_malicious_treeman_0"] = true,
	["wh2_dlc16_wef_mon_zoats"] = true,
	["wh2_dlc16_wef_mon_zoats_ror_0"] = true,
	["wh2_dlc17_bst_cav_tuskgor_chariot_0"] = true,
	["wh2_dlc17_bst_cha_beastlord_2"] = true,
	["wh2_dlc17_bst_cha_bray_shaman_beasts_2"] = true,
	["wh2_dlc17_bst_cha_bray_shaman_death_2"] = true,
	["wh2_dlc17_bst_cha_bray_shaman_shadows_2"] = true,
	["wh2_dlc17_bst_cha_bray_shaman_wild_2"] = true,
	["wh2_dlc17_bst_cha_doombull_0"] = true,
	["wh2_dlc17_bst_cha_khazrak_one_eye_2"] = true,
	["wh2_dlc17_bst_cha_taurox_the_brass_bull_0"] = true,
	["wh2_dlc17_bst_cha_wargor_1"] = true,
	["wh2_dlc17_bst_cha_wargor_2"] = true,
	["wh2_dlc17_bst_mon_ghorgon_0"] = true,
	["wh2_dlc17_bst_mon_ghorgon_boss_0"] = true,
	["wh2_dlc17_bst_mon_ghorgon_ror_0"] = true,
	["wh2_dlc17_bst_mon_jabberslythe_0"] = true,
	["wh2_dlc17_bst_mon_jabberslythe_ror_0"] = true,
	["wh2_dlc17_dwf_cha_thorek_ironbrow_1"] = true,
	["wh2_dlc17_dwf_mon_carnosaur_thorek_0"] = true,
	["wh2_dlc17_lzd_cha_skink_oracle_troglodon_0"] = true,
	["wh2_dlc17_lzd_mon_carnosaur_ror_0"] = true,
	["wh2_dlc17_lzd_mon_coatl_0"] = true,
	["wh2_dlc17_lzd_mon_coatl_ror_0"] = true,
	["wh2_dlc17_lzd_mon_dread_saurian_qb_boss"] = true,
	["wh2_dlc17_lzd_mon_troglodon_0"] = true,
	["wh2_dlc17_lzd_mon_troglodon_ror_0"] = true,
	["wh2_main_def_cav_cold_one_chariot"] = true,
	["wh2_main_def_cha_dreadlord_4"] = true,
	["wh2_main_def_cha_dreadlord_female_4"] = true,
	["wh2_main_def_cha_malekith_1"] = true,
	["wh2_main_def_cha_malekith_2"] = true,
	["wh2_main_def_cha_malekith_3"] = true,
	["wh2_main_def_mon_black_dragon"] = true,
	["wh2_main_def_mon_war_hydra_0"] = true,
	["wh2_main_hef_cav_ithilmar_chariot"] = true,
	["wh2_main_hef_cav_tiranoc_chariot"] = true,
	["wh2_main_hef_cha_alastar_3"] = true,
	["wh2_main_hef_cha_alastar_4"] = true,
	["wh2_main_hef_cha_alastar_5"] = true,
	["wh2_main_hef_cha_mage_high_4"] = true,
	["wh2_main_hef_cha_mage_life_4"] = true,
	["wh2_main_hef_cha_mage_light_4"] = true,
	["wh2_main_hef_cha_noble_3"] = true,
	["wh2_main_hef_cha_noble_4"] = true,
	["wh2_main_hef_cha_prince_3"] = true,
	["wh2_main_hef_cha_prince_4"] = true,
	["wh2_main_hef_cha_prince_5"] = true,
	["wh2_main_hef_cha_princess_3"] = true,
	["wh2_main_hef_cha_princess_4"] = true,
	["wh2_main_hef_cha_princess_5"] = true,
	["wh2_main_hef_mon_great_eagle"] = true,
	["wh2_main_hef_mon_great_eagle_summoned"] = true,
	["wh2_main_hef_mon_moon_dragon"] = true,
	["wh2_main_hef_mon_phoenix_flamespyre"] = true,
	["wh2_main_hef_mon_phoenix_frostheart"] = true,
	["wh2_main_hef_mon_star_dragon"] = true,
	["wh2_main_hef_mon_sun_dragon"] = true,
	["wh2_main_lzd_cav_terradon_riders_0"] = true,
	["wh2_main_lzd_cav_terradon_riders_0_blessed"] = true,
	["wh2_main_lzd_cav_terradon_riders_1"] = true,
	["wh2_main_lzd_cav_terradon_riders_blessed_1"] = true,
	["wh2_main_lzd_cha_kroq_gar_1"] = true,
	["wh2_main_lzd_cha_lord_mazdamundi_0"] = true,
	["wh2_main_lzd_cha_lord_mazdamundi_1"] = true,
	["wh2_main_lzd_cha_saurus_old_blood_2"] = true,
	["wh2_main_lzd_cha_saurus_scar_veteran_1"] = true,
	["wh2_main_lzd_cha_saurus_scar_veteran_2"] = true,
	["wh2_main_lzd_cha_skink_chief_1"] = true,
	["wh2_main_lzd_cha_skink_chief_2"] = true,
	["wh2_main_lzd_cha_skink_chief_3"] = true,
	["wh2_main_lzd_cha_skink_priest_beasts_1"] = true,
	["wh2_main_lzd_cha_skink_priest_beasts_2"] = true,
	["wh2_main_lzd_cha_skink_priest_beasts_3"] = true,
	["wh2_main_lzd_cha_skink_priest_heavens_1"] = true,
	["wh2_main_lzd_cha_skink_priest_heavens_2"] = true,
	["wh2_main_lzd_cha_skink_priest_heavens_3"] = true,
	["wh2_main_lzd_cha_slann_mage_priest_campaign_0"] = true,
	["wh2_main_lzd_cha_slann_mage_priest_heavens_0"] = true,
	["wh2_main_lzd_cha_slann_mage_priest_high_0"] = true,
	["wh2_main_lzd_cha_slann_mage_priest_life_0_qb"] = true,
	["wh2_main_lzd_cha_slann_mage_priest_light_0"] = true,
	["wh2_main_lzd_mon_ancient_stegadon"] = true,
	["wh2_main_lzd_mon_ancient_stegadon_blessed"] = true,
	["wh2_main_lzd_mon_bastiladon_0"] = true,
	["wh2_main_lzd_mon_bastiladon_1"] = true,
	["wh2_main_lzd_mon_bastiladon_2"] = true,
	["wh2_main_lzd_mon_bastiladon_blessed_2"] = true,
	["wh2_main_lzd_mon_carnosaur_0"] = true,
	["wh2_main_lzd_mon_carnosaur_blessed_0"] = true,
	["wh2_main_lzd_mon_kroxigors"] = true,
	["wh2_main_lzd_mon_kroxigors_blessed"] = true,
	["wh2_main_lzd_mon_stegadon_0"] = true,
	["wh2_main_lzd_mon_stegadon_1"] = true,
	["wh2_main_lzd_mon_stegadon_blessed_1"] = true,
	["wh2_main_skv_cha_warlord_1"] = true,
	["wh2_main_skv_mon_hell_pit_abomination"] = true,
	["wh2_main_skv_mon_hell_pit_abomination_summoned"] = true,
	["wh2_main_skv_mon_rat_ogres"] = true,
	["wh2_pro06_tmb_mon_bone_giant_0"] = true,
	["wh2_twa01_grn_cha_goblin_great_shaman_3"] = true,
	["wh2_twa02_wef_cha_glade_captain_2"] = true,
	["wh2_twa03_def_cha_rakarth_1"] = true,
	["wh2_twa03_def_cha_rakarth_2"] = true,
	["wh2_twa03_def_cha_rakarth_3"] = true,
	["wh2_twa03_def_mon_war_mammoth_0"] = true,
	["wh2_twa04_bst_cha_great_bray_shaman_beasts_1"] = true,
	["wh2_twa04_bst_cha_great_bray_shaman_beasts_2"] = true,
	["wh2_twa04_bst_cha_great_bray_shaman_death_1"] = true,
	["wh2_twa04_bst_cha_great_bray_shaman_death_2"] = true,
	["wh2_twa04_bst_cha_great_bray_shaman_shadows_1"] = true,
	["wh2_twa04_bst_cha_great_bray_shaman_shadows_2"] = true,
	["wh2_twa04_bst_cha_great_bray_shaman_wild_1"] = true,
	["wh2_twa04_bst_cha_great_bray_shaman_wild_2"] = true,
	["wh3_cp1_cth_mon_celestial_lion_summoned"] = true,
	["wh3_cp1_tze_cha_qb_exalted_lord_of_change_boss"] = true,
	["wh3_dlc20_chs_cav_chaos_chariot_mkho"] = true,
	["wh3_dlc20_chs_cav_chaos_chariot_mnur"] = true,
	["wh3_dlc20_chs_cav_chaos_chariot_msla"] = true,
	["wh3_dlc20_chs_cav_chaos_chariot_mtze"] = true,
	["wh3_dlc20_chs_cha_chaos_lord_mkho_gorebeast_chariot"] = true,
	["wh3_dlc20_chs_cha_chaos_lord_msla_chaos_chariot"] = true,
	["wh3_dlc20_chs_cha_chaos_sorcerer_death_warshrine"] = true,
	["wh3_dlc20_chs_cha_chaos_sorcerer_fire_warshrine"] = true,
	["wh3_dlc20_chs_cha_chaos_sorcerer_lord_death_mnur_warshrine"] = true,
	["wh3_dlc20_chs_cha_chaos_sorcerer_lord_death_warshrine"] = true,
	["wh3_dlc20_chs_cha_chaos_sorcerer_lord_fire_warshrine"] = true,
	["wh3_dlc20_chs_cha_chaos_sorcerer_lord_metal_mtze_warshrine"] = true,
	["wh3_dlc20_chs_cha_chaos_sorcerer_lord_metal_warshrine"] = true,
	["wh3_dlc20_chs_cha_chaos_sorcerer_lord_nurgle_mnur_warshrine"] = true,
	["wh3_dlc20_chs_cha_chaos_sorcerer_lord_shadows_warshrine"] = true,
	["wh3_dlc20_chs_cha_chaos_sorcerer_lord_tzeentch_mtze_warshrine"] = true,
	["wh3_dlc20_chs_cha_chaos_sorcerer_metal_mtze_warshrine"] = true,
	["wh3_dlc20_chs_cha_chaos_sorcerer_metal_warshrine"] = true,
	["wh3_dlc20_chs_cha_chaos_sorcerer_shadows_msla_warshrine"] = true,
	["wh3_dlc20_chs_cha_chaos_sorcerer_shadows_warshrine"] = true,
	["wh3_dlc20_chs_cha_chaos_sorcerer_slaanesh_msla_warshrine"] = true,
	["wh3_dlc20_chs_cha_chaos_sorcerer_tzeentch_mtze_warshrine"] = true,
	["wh3_dlc20_chs_cha_cultist_msla_warshrine"] = true,
	["wh3_dlc20_chs_cha_daemon_prince"] = true,
	["wh3_dlc20_chs_cha_daemon_prince_mkho"] = true,
	["wh3_dlc20_chs_cha_daemon_prince_mnur"] = true,
	["wh3_dlc20_chs_cha_daemon_prince_msla"] = true,
	["wh3_dlc20_chs_cha_daemon_prince_mtze"] = true,
	["wh3_dlc20_chs_cha_exalted_hero_mkho_gorebeast_chariot"] = true,
	["wh3_dlc20_chs_cha_exalted_hero_mnur_chaos_chariot"] = true,
	["wh3_dlc20_chs_mon_giant_mnur_ror"] = true,
	["wh3_dlc20_chs_mon_warshrine"] = true,
	["wh3_dlc20_chs_mon_warshrine_mkho"] = true,
	["wh3_dlc20_chs_mon_warshrine_mnur"] = true,
	["wh3_dlc20_chs_mon_warshrine_msla"] = true,
	["wh3_dlc20_chs_mon_warshrine_mtze"] = true,
	["wh3_dlc20_kho_cha_cultist_mkho_warshrine"] = true,
	["wh3_dlc20_nur_cha_cultist_mnur_warshrine"] = true,
	["wh3_dlc20_tze_cha_cultist_mtze_warshrine"] = true,
	["wh3_dlc23_chd_cav_bull_centaurs_axe"] = true,
	["wh3_dlc23_chd_cav_bull_centaurs_dual_axe"] = true,
	["wh3_dlc23_chd_cav_bull_centaurs_dual_axe_ror"] = true,
	["wh3_dlc23_chd_cav_bull_centaurs_greatweapons"] = true,
	["wh3_dlc23_chd_cha_bull_centaur_taurruk"] = true,
	["wh3_dlc23_chd_cha_daemonsmith_sorcerer_death_bale_taurus"] = true,
	["wh3_dlc23_chd_cha_daemonsmith_sorcerer_death_great_taurus"] = true,
	["wh3_dlc23_chd_cha_daemonsmith_sorcerer_death_lammasu"] = true,
	["wh3_dlc23_chd_cha_daemonsmith_sorcerer_fire_bale_taurus"] = true,
	["wh3_dlc23_chd_cha_daemonsmith_sorcerer_fire_great_taurus"] = true,
	["wh3_dlc23_chd_cha_daemonsmith_sorcerer_fire_lammasu"] = true,
	["wh3_dlc23_chd_cha_daemonsmith_sorcerer_hashut_bale_taurus"] = true,
	["wh3_dlc23_chd_cha_daemonsmith_sorcerer_hashut_great_taurus"] = true,
	["wh3_dlc23_chd_cha_daemonsmith_sorcerer_hashut_lammasu"] = true,
	["wh3_dlc23_chd_cha_daemonsmith_sorcerer_metal_bale_taurus"] = true,
	["wh3_dlc23_chd_cha_daemonsmith_sorcerer_metal_great_taurus"] = true,
	["wh3_dlc23_chd_cha_daemonsmith_sorcerer_metal_lammasu"] = true,
	["wh3_dlc23_chd_cha_drazhoath_the_ashen_bale_taurus_cinderbreath"] = true,
	["wh3_dlc23_chd_cha_overseer_great_taurus"] = true,
	["wh3_dlc23_chd_cha_overseer_lammasu"] = true,
	["wh3_dlc23_chd_cha_sorcerer_prophet_death_bale_taurus"] = true,
	["wh3_dlc23_chd_cha_sorcerer_prophet_death_great_taurus"] = true,
	["wh3_dlc23_chd_cha_sorcerer_prophet_death_lammasu"] = true,
	["wh3_dlc23_chd_cha_sorcerer_prophet_fire_bale_taurus"] = true,
	["wh3_dlc23_chd_cha_sorcerer_prophet_fire_great_taurus"] = true,
	["wh3_dlc23_chd_cha_sorcerer_prophet_fire_lammasu"] = true,
	["wh3_dlc23_chd_cha_sorcerer_prophet_hashut_bale_taurus"] = true,
	["wh3_dlc23_chd_cha_sorcerer_prophet_hashut_great_taurus"] = true,
	["wh3_dlc23_chd_cha_sorcerer_prophet_hashut_lammasu"] = true,
	["wh3_dlc23_chd_cha_sorcerer_prophet_metal_bale_taurus"] = true,
	["wh3_dlc23_chd_cha_sorcerer_prophet_metal_great_taurus"] = true,
	["wh3_dlc23_chd_cha_sorcerer_prophet_metal_lammasu"] = true,
	["wh3_dlc23_chd_cha_zhatan_the_black_great_taurus"] = true,
	["wh3_dlc23_chd_cha_zhatan_the_black_lammasu"] = true,
	["wh3_dlc23_chd_mon_bale_taurus"] = true,
	["wh3_dlc23_chd_mon_great_taurus"] = true,
	["wh3_dlc23_chd_mon_kdaai_destroyer"] = true,
	["wh3_dlc23_chd_mon_kdaai_fireborn"] = true,
	["wh3_dlc23_chd_mon_kdaai_fireborn_summoned"] = true,
	["wh3_dlc23_chd_mon_lammasu"] = true,
	["wh3_dlc23_chd_veh_dreadquake_mortar"] = true,
	["wh3_dlc23_chd_veh_iron_daemon"] = true,
	["wh3_dlc23_chd_veh_iron_daemon_1dreadquake"] = true,
	["wh3_dlc23_chd_veh_iron_daemon_3payload_qb"] = true,
	["wh3_dlc23_chd_veh_iron_daemon_ror"] = true,
	["wh3_dlc23_chd_veh_iron_daemon_ror_1dreadquake"] = true,
	["wh3_dlc23_chd_veh_skullcracker"] = true,
	["wh3_dlc23_chd_veh_skullcracker_1dreadquake"] = true,
	["wh3_dlc24_chs_cha_chaos_lord_mtze_chaos_chariot"] = true,
	["wh3_dlc24_chs_cha_exalted_hero_mtze_chaos_chariot"] = true,
	["wh3_dlc24_cth_cha_astromancer_great_moon_bird"] = true,
	["wh3_dlc24_cth_cha_celestial_general_yang_celestial_lion"] = true,
	["wh3_dlc24_cth_cha_gate_master_warhorse"] = true,
	["wh3_dlc24_cth_cha_saytang_the_watcher"] = true,
	["wh3_dlc24_cth_cha_yuan_bo_dragon"] = true,
	["wh3_dlc24_cth_mon_celestial_lion"] = true,
	["wh3_dlc24_cth_mon_great_moon_bird"] = true,
	["wh3_dlc24_cth_mon_jade_lion"] = true,
	["wh3_dlc24_cth_mon_jet_lion"] = true,
	["wh3_dlc24_cth_veh_zhangu_war_drum"] = true,
	["wh3_dlc24_cth_veh_zhangu_war_drum_ror"] = true,
	["wh3_dlc24_ksl_cha_hag_witch_beast"] = true,
	["wh3_dlc24_ksl_cha_hag_witch_death"] = true,
	["wh3_dlc24_ksl_cha_hag_witch_hag"] = true,
	["wh3_dlc24_ksl_cha_hag_witch_shadow"] = true,
	["wh3_dlc24_ksl_cha_ice_witch_ice_frost_wyrm"] = true,
	["wh3_dlc24_ksl_cha_ice_witch_tempest_frost_wyrm"] = true,
	["wh3_dlc24_ksl_cha_katarin_frost_wyrm"] = true,
	["wh3_dlc24_ksl_cha_katarin_ice_court_sled"] = true,
	["wh3_dlc24_ksl_mon_frost_wyrm"] = true,
	["wh3_dlc24_ksl_mon_incarnate_elemental_of_beasts"] = true,
	["wh3_dlc24_ksl_mon_incarnate_elemental_of_beasts_summoned"] = true,
	["wh3_dlc24_tze_mon_cockatrice"] = true,
	["wh3_dlc24_tze_mon_flamers_changebringers"] = true,
	["wh3_dlc24_tze_mon_mutalith_vortex_beast"] = true,
	["wh3_dlc24_tze_mon_mutalith_vortex_beast_ror"] = true,
	["wh3_dlc25_bst_mon_jabberslythe_qb_boss"] = true,
	["wh3_dlc25_chs_cha_chaos_lord_mnur_chaos_chariot"] = true,
	["wh3_dlc25_chs_cha_chaos_sorcerer_death_mnur_warshrine"] = true,
	["wh3_dlc25_chs_cha_chaos_sorcerer_nurgle_mnur_warshrine"] = true,
	["wh3_dlc25_dwf_veh_gyrocopter_1_grudge_unit"] = true,
	["wh3_dlc25_dwf_veh_gyrocopter_summoned_0"] = true,
	["wh3_dlc25_dwf_veh_thunderbarge"] = true,
	["wh3_dlc25_dwf_veh_thunderbarge_grungni"] = true,
	["wh3_dlc25_dwf_veh_thunderbarge_grungni_mp"] = true,
	["wh3_dlc25_emp_cha_elspeth_von_draken_carmine_dragon"] = true,
	["wh3_dlc25_emp_cha_master_engineer_steam_tank"] = true,
	["wh3_dlc25_emp_mon_incarnate_elemental_of_beasts_summoned"] = true,
	["wh3_dlc25_emp_veh_marienburg_land_ship"] = true,
	["wh3_dlc25_emp_veh_marienburg_land_ship_morr"] = true,
	["wh3_dlc25_emp_veh_marienburg_land_ship_ror"] = true,
	["wh3_dlc25_emp_veh_steam_tank_volley_gun"] = true,
	["wh3_dlc25_grn_mon_arachnarok_spider_boss"] = true,
	["wh3_dlc25_grn_mon_rogue_idol_qb_boss"] = true,
	["wh3_dlc25_hef_mon_sun_dragon_boss"] = true,
	["wh3_dlc25_nur_cha_bray_shaman_wild_chieftain_razorgor_chariot"] = true,
	["wh3_dlc25_nur_cha_bray_shaman_wild_chieftain_tuskgor_chariot"] = true,
	["wh3_dlc25_nur_cha_epidemius"] = true,
	["wh3_dlc25_nur_cha_exalted_great_unclean_one_nurgle_qb_boss"] = true,
	["wh3_dlc25_nur_cha_exalted_hero_chieftain_chaos_chariot"] = true,
	["wh3_dlc25_nur_cha_exalted_hero_chieftain_chaos_dragon"] = true,
	["wh3_dlc25_nur_cha_fimir_balefiend_shadow_chieftain"] = true,
	["wh3_dlc25_nur_cha_skin_wolf_werekin_chieftain"] = true,
	["wh3_dlc25_nur_cha_tamurkhan"] = true,
	["wh3_dlc25_nur_cha_tamurkhan_bubebolos"] = true,
	["wh3_dlc25_nur_inf_plague_ogres"] = true,
	["wh3_dlc25_nur_inf_plague_ogres_great_weapons"] = true,
	["wh3_dlc25_nur_mon_bile_trolls"] = true,
	["wh3_dlc25_nur_mon_soul_grinder_0_ror"] = true,
	["wh3_dlc25_nur_mon_toad_dragon"] = true,
	["wh3_dlc26_grn_cav_mangler_squig"] = true,
	["wh3_dlc26_grn_cha_savage_orc_great_shaman_wyvern"] = true,
	["wh3_dlc26_grn_mon_arachnarok_spider_flinger"] = true,
	["wh3_dlc26_grn_mon_colossal_squig"] = true,
	["wh3_dlc26_grn_mon_colossal_squig_ror"] = true,
	["wh3_dlc26_grn_mon_wyvern_summoned"] = true,
	["wh3_dlc26_kho_cha_bloodspeaker_warshrine"] = true,
	["wh3_dlc26_kho_cha_scyla_anfingrimm"] = true,
	["wh3_dlc26_kho_cha_skulltaker_bloodthrone"] = true,
	["wh3_dlc26_kho_mon_bloodbeast_of_khorne"] = true,
	["wh3_dlc26_kho_mon_slaughterbrute"] = true,
	["wh3_dlc26_kho_mon_spawn_of_khorne_0_summoned"] = true,
	["wh3_dlc26_kho_veh_skullcannon_ror"] = true,
	["wh3_dlc26_ogr_cha_bragg_the_gutsman"] = true,
	["wh3_dlc26_ogr_cha_bruiser"] = true,
	["wh3_dlc26_ogr_cha_butcher_death"] = true,
	["wh3_dlc26_ogr_cha_butcher_heavens"] = true,
	["wh3_dlc26_ogr_cha_golgfag_maneater"] = true,
	["wh3_dlc26_ogr_cha_paymaster"] = true,
	["wh3_dlc26_ogr_cha_slaughtermaster_death"] = true,
	["wh3_dlc26_ogr_cha_slaughtermaster_heavens"] = true,
	["wh3_dlc26_ogr_inf_eshin_maneater_ror"] = true,
	["wh3_dlc26_ogr_inf_golgfags_maneaters"] = true,
	["wh3_dlc26_ogr_mon_thundertusk"] = true,
	["wh3_dlc26_ogr_mon_yhetees"] = true,
	["wh3_dlc26_ogr_mon_yhetees_ror"] = true,
	["wh3_dlc27_bst_mon_ghorgon_boss"] = true,
	["wh3_dlc27_bst_mon_jabberslythe_boss"] = true,
	["wh3_dlc27_chd_mon_bale_taurus_boss"] = true,
	["wh3_dlc27_chd_mon_lammasu_boss"] = true,
	["wh3_dlc27_chs_cha_daemon_prince_mkho_qb"] = true,
	["wh3_dlc27_chs_cha_exalted_hero_msla_chaos_chariot"] = true,
	["wh3_dlc27_chs_cha_sorcerer_lord_shadows_msla_warshrine"] = true,
	["wh3_dlc27_chs_cha_sorcerer_lord_slaanesh_msla_warshrine"] = true,
	["wh3_dlc27_chs_feral_manticore_boss"] = true,
	["wh3_dlc27_cth_mon_celestial_lion_boss"] = true,
	["wh3_dlc27_def_mon_black_dragon_boss"] = true,
	["wh3_dlc27_hef_cha_caradryan_ashtari"] = true,
	["wh3_dlc27_hef_cha_caradryan_chariot"] = true,
	["wh3_dlc27_hef_cha_mist_mage_eagle"] = true,
	["wh3_dlc27_hef_cha_mist_mage_skycutter"] = true,
	["wh3_dlc27_hef_cha_sea_helm_eagle"] = true,
	["wh3_dlc27_hef_cha_sea_helm_skycutter"] = true,
	["wh3_dlc27_hef_cha_sea_lord_aislinn_dragon"] = true,
	["wh3_dlc27_hef_cha_sea_lord_aislinn_skycutter"] = true,
	["wh3_dlc27_hef_inf_oceanids"] = true,
	["wh3_dlc27_hef_inf_oceanids_split_up_summoned"] = true,
	["wh3_dlc27_hef_inf_oceanids_summoned"] = true,
	["wh3_dlc27_hef_mon_merwyrm"] = true,
	["wh3_dlc27_hef_mon_merwyrm_ror"] = true,
	["wh3_dlc27_hef_mon_merwyrm_summoned"] = true,
	["wh3_dlc27_hef_mon_sea_elemental"] = true,
	["wh3_dlc27_hef_veh_skycutter_bolt_thrower"] = true,
	["wh3_dlc27_hef_veh_skycutter_bows"] = true,
	["wh3_dlc27_hef_veh_skycutter_ror"] = true,
	["wh3_dlc27_lzd_mon_dread_saurian_boss"] = true,
	["wh3_dlc27_nor_cav_chaos_chariot_ror"] = true,
	["wh3_dlc27_nor_cha_beorg_bearstruck"] = true,
	["wh3_dlc27_nor_cha_fimir_noble"] = true,
	["wh3_dlc27_nor_cha_great_shaman_sorcerer_death_chariot"] = true,
	["wh3_dlc27_nor_cha_great_shaman_sorcerer_death_mammoth"] = true,
	["wh3_dlc27_nor_cha_great_shaman_sorcerer_fire_chariot"] = true,
	["wh3_dlc27_nor_cha_great_shaman_sorcerer_fire_mammoth"] = true,
	["wh3_dlc27_nor_cha_great_shaman_sorcerer_metal_chariot"] = true,
	["wh3_dlc27_nor_cha_great_shaman_sorcerer_metal_mammoth"] = true,
	["wh3_dlc27_nor_cha_sayl_the_faithless_chariot"] = true,
	["wh3_dlc27_nor_cha_sayl_the_faithless_mammoth"] = true,
	["wh3_dlc27_nor_cha_shaman_sorcerer_death_2_summoned"] = true,
	["wh3_dlc27_nor_cha_shaman_sorcerer_fire_2_summoned"] = true,
	["wh3_dlc27_nor_cha_shaman_sorcerer_metal_2_summoned"] = true,
	["wh3_dlc27_nor_mon_chimera"] = true,
	["wh3_dlc27_nor_mon_chimera_boss"] = true,
	["wh3_dlc27_nor_mon_chimera_ror"] = true,
	["wh3_dlc27_nor_mon_cursd_ettin"] = true,
	["wh3_dlc27_nor_mon_cursd_ettin_runecaller"] = true,
	["wh3_dlc27_nor_mon_dread_maw"] = true,
	["wh3_dlc27_nor_mon_dread_maw_underground"] = true,
	["wh3_dlc27_nur_mon_toad_dragon_boss"] = true,
	["wh3_dlc27_ogr_mon_thundertusk_boss"] = true,
	["wh3_dlc27_sla_cha_dechala"] = true,
	["wh3_dlc27_sla_mon_champions_of_slaanesh"] = true,
	["wh3_dlc27_sla_mon_champions_of_slaanesh_ror"] = true,
	["wh3_dlc27_sla_mon_giant_spawn_of_sla_summoned_i"] = true,
	["wh3_dlc27_sla_mon_preyton"] = true,
	["wh3_dlc27_sla_mon_preyton_boss"] = true,
	["wh3_dlc27_sla_mon_preyton_ror"] = true,
	["wh3_dlc27_sla_veh_seeker_chariot_ror"] = true,
	["wh3_dlc27_tmb_mon_carrion_boss"] = true,
	["wh3_dlc27_tze_mon_cockatrice_boss"] = true,
	["wh3_dlc29_chs_cha_bloab_bilespurter"] = true,
	["wh3_dlc29_chs_cha_glottkin"] = true,
	["wh3_dlc29_chs_cha_gutrot_spume_warshrine"] = true,
	["wh3_dlc29_chs_cha_morbidex_tripletongue"] = true,
	["wh3_dlc29_chs_cha_orghotts_whippermaw"] = true,
	["wh3_dlc29_chs_mon_basilisk"] = true,
	["wh3_dlc29_chs_mon_chaos_siege_giant"] = true,
	["wh3_dlc29_chs_mon_giant_spined_chaos_beast"] = true,
	["wh3_dlc29_chs_mon_giant_spined_chaos_beast_ror"] = true,
	["wh3_dlc29_cst_cha_vampire_fleet_admiral_female_undeath_rotting_promethean"] = true,
	["wh3_dlc29_cst_cha_vampire_fleet_admiral_undeath_rotting_promethean"] = true,
	["wh3_dlc29_cst_cha_vampire_fleet_captain_undeath_rotting_promethean"] = true,
	["wh3_dlc29_cst_mon_mournguls_0_summoned"] = true,
	["wh3_dlc29_cst_mon_necrofex_colossus_0_summoned"] = true,
	["wh3_dlc29_cst_mon_rotting_prometheans_gunnery_mob_summoned"] = true,
	["wh3_dlc29_emp_cha_boris_todbringer_toddy_3"] = true,
	["wh3_dlc29_emp_veh_celestial_hurricanum_0"] = true,
	["wh3_dlc29_skv_cha_lord_skrolk_cauldron"] = true,
	["wh3_dlc29_skv_cha_plague_priest_cauldron"] = true,
	["wh3_dlc29_skv_cha_skreech_verminking"] = true,
	["wh3_dlc29_skv_cha_thanquol_boneripper_warpfire_braziers"] = true,
	["wh3_dlc29_skv_cha_thanquol_boneripper_warpfire_projectors"] = true,
	["wh3_dlc29_skv_cha_verminlord_corruptor"] = true,
	["wh3_dlc29_skv_cha_verminlord_deceiver"] = true,
	["wh3_dlc29_skv_cha_verminlord_warbringer"] = true,
	["wh3_dlc29_skv_cha_verminlord_warpseer"] = true,
	["wh3_dlc29_skv_mon_brood_horror_0_summoned"] = true,
	["wh3_dlc29_skv_mon_stormfiend_doomflayer_gauntlets"] = true,
	["wh3_dlc29_skv_mon_stormfiend_grinderfists"] = true,
	["wh3_dlc29_skv_mon_stormfiend_ratling_cannons"] = true,
	["wh3_dlc29_skv_mon_stormfiend_shock_gauntlets"] = true,
	["wh3_dlc29_skv_mon_stormfiend_warpfire_projectors"] = true,
	["wh3_dlc29_skv_mon_stormfiend_windlaunchers"] = true,
	["wh3_dlc29_skv_mon_stormfiends_ratling_cannons_ror"] = true,
	["wh3_dlc29_skv_veh_cauldron_of_a_thousand_poxes"] = true,
	["wh3_dlc29_tmb_cha_arkhan_dread_abyssal"] = true,
	["wh3_dlc29_tmb_cha_arkhan_the_black_skeleton_chariot_mp"] = true,
	["wh3_dlc29_tmb_cha_liche_high_priest_death_skeleton_chariot"] = true,
	["wh3_dlc29_tmb_cha_liche_high_priest_light_skeleton_chariot"] = true,
	["wh3_dlc29_tmb_cha_liche_high_priest_nehekhara_skeleton_chariot"] = true,
	["wh3_dlc29_tmb_cha_liche_high_priest_shadow_skeleton_chariot"] = true,
	["wh3_dlc29_tmb_cha_tomb_herald_skeleton_chariot"] = true,
	["wh3_dlc29_tmb_mon_khemrian_warsphinx_0_summoned"] = true,
	["wh3_dlc29_tmb_mon_khemric_titan"] = true,
	["wh3_dlc29_tmb_mon_khemric_titan_ror"] = true,
	["wh3_dlc29_tmb_mon_khemric_titan_summoned"] = true,
	["wh3_dlc29_tmb_mon_ushabti_ror_sepulchrex"] = true,
	["wh3_dlc29_tmb_veh_skeleton_archer_chariot_0_summoned"] = true,
	["wh3_dlc29_vmp_cha_dieter_helsnicht_undead_manticore"] = true,
	["wh3_dlc29_vmp_cha_mannfred_von_carstein_dread_abyssal"] = true,
	["wh3_dlc29_vmp_cha_mannfred_von_carstein_zombie_dragon_mp"] = true,
	["wh3_dlc29_vmp_cha_nagash"] = true,
	["wh3_dlc29_vmp_cha_nagash_vampire_lord_zombie_dragon"] = true,
	["wh3_dlc29_vmp_cha_neferata_dread_abyssal"] = true,
	["wh3_dlc29_vmp_cha_neferata_zombie_dragon"] = true,
	["wh3_dlc29_vmp_cha_neferata_zombie_dragon_mp"] = true,
	["wh3_dlc29_vmp_mon_morghast_archai"] = true,
	["wh3_dlc29_vmp_mon_morghast_archai_ror"] = true,
	["wh3_dlc29_vmp_mon_morghast_archai_summon"] = true,
	["wh3_dlc29_vmp_mon_morghast_harbingers"] = true,
	["wh3_dlc29_vmp_mon_terrorgheist_summoned"] = true,
	["wh3_dlc29_vmp_mon_zombie_dragon"] = true,
	["wh3_dlc29_vmp_mon_zombie_dragon_summoned"] = true,
	["wh3_main_cth_art_fire_rain_rocket_battery_0"] = true,
	["wh3_main_cth_art_grand_cannon_0"] = true,
	["wh3_main_cth_cha_alchemist_2"] = true,
	["wh3_main_cth_cha_astromancer_2"] = true,
	["wh3_main_cth_cha_iron_dragon_1"] = true,
	["wh3_main_cth_cha_lord_magistrate_2"] = true,
	["wh3_main_cth_cha_storm_dragon_1"] = true,
	["wh3_main_cth_mon_terracotta_sentinel_0"] = true,
	["wh3_main_cth_veh_sky_junk_0"] = true,
	["wh3_main_cth_veh_sky_lantern_0"] = true,
	["wh3_main_cth_veh_war_compass_0"] = true,
	["wh3_main_dae_cha_be_lakor_0"] = true,
	["wh3_main_dae_cha_daemon_prince_0"] = true,
	["wh3_main_dae_cha_daemon_prince_MP"] = true,
	["wh3_main_dae_cha_daemon_prince_khorne_0"] = true,
	["wh3_main_dae_cha_daemon_prince_khorne_MP"] = true,
	["wh3_main_dae_cha_daemon_prince_nurgle_0"] = true,
	["wh3_main_dae_cha_daemon_prince_nurgle_MP"] = true,
	["wh3_main_dae_cha_daemon_prince_slaanesh_0"] = true,
	["wh3_main_dae_cha_daemon_prince_slaanesh_MP"] = true,
	["wh3_main_dae_cha_daemon_prince_tzeentch_0"] = true,
	["wh3_main_dae_cha_daemon_prince_tzeentch_MP"] = true,
	["wh3_main_ie_nor_cha_exalted_great_unclean_one_burplesmirk_spewpit"] = true,
	["wh3_main_kho_cav_gorebeast_chariot"] = true,
	["wh3_main_kho_cha_bloodreaper_2"] = true,
	["wh3_main_kho_cha_exalted_bloodthirster_0"] = true,
	["wh3_main_kho_cha_herald_of_khorne_2"] = true,
	["wh3_main_kho_cha_skarbrand_0"] = true,
	["wh3_main_kho_mon_bloodthirster_0"] = true,
	["wh3_main_kho_mon_bloodthirster_summoned_0"] = true,
	["wh3_main_kho_mon_khornataurs_0"] = true,
	["wh3_main_kho_mon_khornataurs_1"] = true,
	["wh3_main_kho_mon_soul_grinder_0"] = true,
	["wh3_main_kho_mon_spawn_of_khorne_0"] = true,
	["wh3_main_kho_veh_blood_shrine_0"] = true,
	["wh3_main_kho_veh_skullcannon_0"] = true,
	["wh3_main_ksl_mon_elemental_bear_0"] = true,
	["wh3_main_ksl_mon_elemental_bear_summoned_0"] = true,
	["wh3_main_ksl_veh_heavy_war_sled_0"] = true,
	["wh3_main_ksl_veh_light_war_sled_0"] = true,
	["wh3_main_nur_cha_exalted_great_unclean_one_death_0"] = true,
	["wh3_main_nur_cha_exalted_great_unclean_one_nurgle_0"] = true,
	["wh3_main_nur_cha_herald_of_nurgle_death_1"] = true,
	["wh3_main_nur_cha_herald_of_nurgle_nurgle_1"] = true,
	["wh3_main_nur_cha_ku_gath_plaguefather_0"] = true,
	["wh3_main_nur_cha_plagueridden_death_1"] = true,
	["wh3_main_nur_cha_plagueridden_nurgle_1"] = true,
	["wh3_main_nur_mon_beast_of_nurgle_0"] = true,
	["wh3_main_nur_mon_great_unclean_one_0"] = true,
	["wh3_main_nur_mon_great_unclean_one_summoned_0"] = true,
	["wh3_main_nur_mon_soul_grinder_0"] = true,
	["wh3_main_nur_mon_spawn_of_nurgle_0"] = true,
	["wh3_main_nur_mon_spawn_of_nurgle_0_summoned"] = true,
	["wh3_main_ogr_cav_crushers_0"] = true,
	["wh3_main_ogr_cav_crushers_1"] = true,
	["wh3_main_ogr_cav_mournfang_cavalry_0"] = true,
	["wh3_main_ogr_cav_mournfang_cavalry_1"] = true,
	["wh3_main_ogr_cav_mournfang_cavalry_2"] = true,
	["wh3_main_ogr_cha_butcher_beasts_0"] = true,
	["wh3_main_ogr_cha_butcher_great_maw_0"] = true,
	["wh3_main_ogr_cha_firebelly_0"] = true,
	["wh3_main_ogr_cha_greasus_goldtooth_0"] = true,
	["wh3_main_ogr_cha_hunter_0"] = true,
	["wh3_main_ogr_cha_hunter_1"] = true,
	["wh3_main_ogr_cha_skrag_the_slaughterer_0"] = true,
	["wh3_main_ogr_cha_slaughtermaster_beasts_0"] = true,
	["wh3_main_ogr_cha_slaughtermaster_great_maw_0"] = true,
	["wh3_main_ogr_cha_tyrant_0"] = true,
	["wh3_main_ogr_feral_manticore_summoned"] = true,
	["wh3_main_ogr_inf_ironguts_0"] = true,
	["wh3_main_ogr_inf_leadbelchers_0"] = true,
	["wh3_main_ogr_inf_maneaters_0"] = true,
	["wh3_main_ogr_inf_maneaters_1"] = true,
	["wh3_main_ogr_inf_maneaters_2"] = true,
	["wh3_main_ogr_inf_maneaters_3"] = true,
	["wh3_main_ogr_inf_maneaters_summoned_0"] = true,
	["wh3_main_ogr_inf_ogres_0"] = true,
	["wh3_main_ogr_inf_ogres_1"] = true,
	["wh3_main_ogr_inf_ogres_2"] = true,
	["wh3_main_ogr_mon_giant_0"] = true,
	["wh3_main_ogr_mon_gorgers_0"] = true,
	["wh3_main_ogr_mon_gorgers_summoned_0"] = true,
	["wh3_main_ogr_mon_stonehorn_0"] = true,
	["wh3_main_ogr_mon_stonehorn_1"] = true,
	["wh3_main_ogr_veh_gnoblar_scraplauncher_0"] = true,
	["wh3_main_ogr_veh_ironblaster_0"] = true,
	["wh3_main_pro_kho_cha_bloodreaper_2"] = true,
	["wh3_main_pro_kho_cha_herald_of_khorne_2"] = true,
	["wh3_main_pro_kho_inf_flesh_hounds_of_khorne_simaergul_0"] = true,
	["wh3_main_pro_ksl_cha_slavin_0"] = true,
	["wh3_main_pro_ksl_mon_elemental_bear_ror_0"] = true,
	["wh3_main_pro_tze_cha_herald_of_tzeentch_tzeentch_2"] = true,
	["wh3_main_pro_tze_mon_flamers_0"] = true,
	["wh3_main_sla_cha_alluress_shadow_2"] = true,
	["wh3_main_sla_cha_alluress_shadow_3"] = true,
	["wh3_main_sla_cha_alluress_slaanesh_2"] = true,
	["wh3_main_sla_cha_alluress_slaanesh_3"] = true,
	["wh3_main_sla_cha_exalted_keeper_of_secrets_shadow_0"] = true,
	["wh3_main_sla_cha_exalted_keeper_of_secrets_slaanesh_0"] = true,
	["wh3_main_sla_cha_herald_of_slaanesh_shadow_2"] = true,
	["wh3_main_sla_cha_herald_of_slaanesh_shadow_3"] = true,
	["wh3_main_sla_cha_herald_of_slaanesh_slaanesh_2"] = true,
	["wh3_main_sla_cha_herald_of_slaanesh_slaanesh_3"] = true,
	["wh3_main_sla_cha_nkari_0"] = true,
	["wh3_main_sla_mon_fiends_of_slaanesh_0"] = true,
	["wh3_main_sla_mon_keeper_of_secrets_0"] = true,
	["wh3_main_sla_mon_keeper_of_secrets_summoned_0"] = true,
	["wh3_main_sla_mon_soul_grinder_0"] = true,
	["wh3_main_sla_mon_spawn_of_slaanesh_0"] = true,
	["wh3_main_sla_veh_exalted_seeker_chariot_0"] = true,
	["wh3_main_sla_veh_hellflayer_0"] = true,
	["wh3_main_sla_veh_seeker_chariot_0"] = true,
	["wh3_main_tze_cha_exalted_lord_of_change_metal_0"] = true,
	["wh3_main_tze_cha_exalted_lord_of_change_tzeentch_0"] = true,
	["wh3_main_tze_cha_herald_of_tzeentch_metal_2"] = true,
	["wh3_main_tze_cha_herald_of_tzeentch_tzeentch_2"] = true,
	["wh3_main_tze_cha_iridescent_horror_metal_2"] = true,
	["wh3_main_tze_cha_iridescent_horror_tzeentch_2"] = true,
	["wh3_main_tze_cha_kairos_fateweaver_0"] = true,
	["wh3_main_tze_mon_exalted_flamer_0"] = true,
	["wh3_main_tze_mon_flamers_0"] = true,
	["wh3_main_tze_mon_lord_of_change_0"] = true,
	["wh3_main_tze_mon_lord_of_change_summoned_0"] = true,
	["wh3_main_tze_mon_soul_grinder_0"] = true,
	["wh3_main_tze_mon_spawn_of_tzeentch_0"] = true,
	["wh3_main_tze_veh_burning_chariot_0"] = true,
	["wh3_pro10_tze_cha_daemon_prince_of_tzeentch"] = true,
	["wh3_pro12_kho_cha_karanak"] = true,
	["wh3_survival_dae_cha_be_lakor_01"] = true,
	["wh3_survival_dae_cha_be_lakor_02"] = true,
	["wh3_survival_kho_cha_bloodreaper"] = true,
	["wh3_survival_kho_cha_daemon_prince_of_khorne"] = true,
	["wh3_survival_kho_cha_exalted_bloodthirster"] = true,
	["wh3_survival_kho_cha_exalted_bloodthirster_0"] = true,
	["wh3_survival_nur_cha_daemon_prince_of_nurgle"] = true,
	["wh3_survival_nur_cha_exalted_great_unclean_one_nurgle"] = true,
	["wh3_survival_nur_cha_exalted_great_unclean_one_nurgle_01"] = true,
	["wh3_survival_sla_cha_alluress_shadow"] = true,
	["wh3_survival_sla_cha_daemon_prince_of_slaanesh"] = true,
	["wh3_survival_sla_cha_exalted_keeper_of_secrets_slaanesh"] = true,
	["wh3_survival_tze_cha_daemon_prince_of_tzeentch"] = true,
	["wh3_survival_tze_cha_exalted_lord_of_change_tzeentch"] = true,
	["wh3_survival_tze_cha_iridescent_horror_metal"] = true,
	["wh3_twa06_ogr_inf_maneaters_ror_0"] = true,
	["wh3_twa07_ogr_cav_crushers_ror_0"] = true,
	["wh3_twa08_cth_mon_terracotta_sentinel_0_ror"] = true,
	["wh3_twa08_kho_mon_bloodthirster_0_ror"] = true,
	["wh3_twa08_ksl_mon_elemental_bear_0_ror"] = true,
	["wh3_twa08_nur_mon_great_unclean_one_0_ror"] = true,
	["wh3_twa08_ogr_mon_stonehorn_0_ror"] = true,
	["wh3_twa08_sla_mon_keeper_of_secrets_0_ror"] = true,
	["wh3_twa08_tze_mon_lord_of_change_0_ror"] = true,
	["wh_dlc01_chs_cav_gorebeast_chariot"] = true,
	["wh_dlc01_chs_cha_chaos_lord_10"] = true,
	["wh_dlc01_chs_cha_chaos_lord_2"] = true,
	["wh_dlc01_chs_cha_chaos_lord_9"] = true,
	["wh_dlc01_chs_cha_chaos_sorcerer_death_8"] = true,
	["wh_dlc01_chs_cha_chaos_sorcerer_fire_8"] = true,
	["wh_dlc01_chs_cha_chaos_sorcerer_lord_death_10"] = true,
	["wh_dlc01_chs_cha_chaos_sorcerer_lord_death_7"] = true,
	["wh_dlc01_chs_cha_chaos_sorcerer_lord_death_8"] = true,
	["wh_dlc01_chs_cha_chaos_sorcerer_lord_death_9"] = true,
	["wh_dlc01_chs_cha_chaos_sorcerer_lord_fire_10"] = true,
	["wh_dlc01_chs_cha_chaos_sorcerer_lord_fire_7"] = true,
	["wh_dlc01_chs_cha_chaos_sorcerer_lord_fire_8"] = true,
	["wh_dlc01_chs_cha_chaos_sorcerer_lord_fire_9"] = true,
	["wh_dlc01_chs_cha_chaos_sorcerer_lord_metal_10"] = true,
	["wh_dlc01_chs_cha_chaos_sorcerer_lord_metal_7"] = true,
	["wh_dlc01_chs_cha_chaos_sorcerer_lord_metal_8"] = true,
	["wh_dlc01_chs_cha_chaos_sorcerer_lord_metal_9"] = true,
	["wh_dlc01_chs_cha_chaos_sorcerer_lord_shadows_3"] = true,
	["wh_dlc01_chs_cha_chaos_sorcerer_lord_shadows_4"] = true,
	["wh_dlc01_chs_cha_chaos_sorcerer_metal_8"] = true,
	["wh_dlc01_chs_cha_chaos_sorcerer_shadows_3"] = true,
	["wh_dlc01_chs_cha_exalted_hero_10"] = true,
	["wh_dlc01_chs_cha_exalted_hero_8"] = true,
	["wh_dlc01_chs_cha_kholek"] = true,
	["wh_dlc01_chs_cha_qb_lord_of_change_0"] = true,
	["wh_dlc01_chs_mon_dragon_ogre"] = true,
	["wh_dlc01_chs_mon_dragon_ogre_shaggoth"] = true,
	["wh_dlc01_chs_mon_trolls_1"] = true,
	["wh_dlc01_nor_cha_chaos_sorcerer_lord_2"] = true,
	["wh_dlc03_bst_cav_razorgor_chariot_0"] = true,
	["wh_dlc03_bst_cha_beastlord_1"] = true,
	["wh_dlc03_bst_cha_bray_shaman_beasts_1"] = true,
	["wh_dlc03_bst_cha_bray_shaman_death_1"] = true,
	["wh_dlc03_bst_cha_bray_shaman_shadows_1"] = true,
	["wh_dlc03_bst_cha_bray_shaman_wild_1"] = true,
	["wh_dlc03_bst_cha_gorebull_0"] = true,
	["wh_dlc03_bst_cha_khazrak_one_eye_1"] = true,
	["wh_dlc03_bst_feral_manticore"] = true,
	["wh_dlc03_bst_inf_cygor_0"] = true,
	["wh_dlc03_bst_inf_cygor_0_summoned"] = true,
	["wh_dlc03_bst_inf_minotaurs_0"] = true,
	["wh_dlc03_bst_inf_minotaurs_1"] = true,
	["wh_dlc03_bst_inf_minotaurs_2"] = true,
	["wh_dlc03_bst_mon_chaos_spawn_0"] = true,
	["wh_dlc03_bst_mon_chaos_spawn_0_summoned"] = true,
	["wh_dlc03_bst_mon_giant_0"] = true,
	["wh_dlc03_emp_cha_boris_todbringer_3"] = true,
	["wh_dlc03_emp_cha_wizard_beasts_3"] = true,
	["wh_dlc04_emp_cha_volkmar_the_grim_1"] = true,
	["wh_dlc04_emp_veh_templehof_luminark_0"] = true,
	["wh_dlc04_vmp_cha_strigoi_ghoul_king_1"] = true,
	["wh_dlc04_vmp_mon_devils_swartzhafen_0"] = true,
	["wh_dlc05_bst_mon_chaos_spawn_0_boss"] = true,
	["wh_dlc05_vmp_cha_red_duke_3"] = true,
	["wh_dlc05_wef_cav_hawk_riders_0"] = true,
	["wh_dlc05_wef_cha_ancient_treeman_0"] = true,
	["wh_dlc05_wef_cha_durthu_0"] = true,
	["wh_dlc05_wef_cha_female_glade_lord_2"] = true,
	["wh_dlc05_wef_cha_female_glade_lord_2_qb"] = true,
	["wh_dlc05_wef_cha_female_glade_lord_3"] = true,
	["wh_dlc05_wef_cha_glade_lord_2"] = true,
	["wh_dlc05_wef_cha_glade_lord_3"] = true,
	["wh_dlc05_wef_cha_orion_0"] = true,
	["wh_dlc05_wef_cha_spellsinger_beasts_2"] = true,
	["wh_dlc05_wef_cha_spellsinger_life_2"] = true,
	["wh_dlc05_wef_cha_spellsinger_shadows_2"] = true,
	["wh_dlc05_wef_forest_dragon_0"] = true,
	["wh_dlc05_wef_mon_great_eagle_0"] = true,
	["wh_dlc05_wef_mon_treekin_0"] = true,
	["wh_dlc05_wef_mon_treeman_0"] = true,
	["wh_dlc06_chs_cha_chaos_sorcerer_death_9"] = true,
	["wh_dlc06_chs_cha_chaos_sorcerer_fire_9"] = true,
	["wh_dlc06_chs_cha_chaos_sorcerer_metal_9"] = true,
	["wh_dlc06_chs_feral_manticore"] = true,
	["wh_dlc06_dwf_cha_runelord_1"] = true,
	["wh_dlc06_dwf_veh_skyhammer_0"] = true,
	["wh_dlc06_grn_cav_teef_robbers_0"] = true,
	["wh_dlc06_grn_mon_venom_queen_0"] = true,
	["wh_dlc07_brt_cav_royal_hippogryph_knights_0"] = true,
	["wh_dlc07_brt_cha_alberic_bordeleaux_3"] = true,
	["wh_dlc07_brt_inf_grail_reliquae_0"] = true,
	["wh_dlc08_bst_mon_cygor_boss"] = true,
	["wh_dlc08_chs_cha_chaos_lord_2_qb"] = true,
	["wh_dlc08_chs_mon_dragon_ogre_shaggoth_boss"] = true,
	["wh_dlc08_chs_mon_dragon_ogre_shaggoth_minor_boss"] = true,
	["wh_dlc08_grn_mon_arachnarok_spider_boss"] = true,
	["wh_dlc08_grn_mon_giant_boss"] = true,
	["wh_dlc08_nor_cav_marauder_warwolves_chariot_0"] = true,
	["wh_dlc08_nor_cha_arzik_0"] = true,
	["wh_dlc08_nor_cha_fimir_balefiend_fire_0"] = true,
	["wh_dlc08_nor_cha_fimir_balefiend_shadow_0"] = true,
	["wh_dlc08_nor_cha_kihar_0"] = true,
	["wh_dlc08_nor_cha_shaman_sorcerer_death_2"] = true,
	["wh_dlc08_nor_cha_shaman_sorcerer_fire_2"] = true,
	["wh_dlc08_nor_cha_shaman_sorcerer_metal_2"] = true,
	["wh_dlc08_nor_cha_skin_wolf_werekin_0"] = true,
	["wh_dlc08_nor_cha_throgg_0"] = true,
	["wh_dlc08_nor_cha_wulfrik_2"] = true,
	["wh_dlc08_nor_cha_wulfrik_3"] = true,
	["wh_dlc08_nor_feral_manticore"] = true,
	["wh_dlc08_nor_mon_fimir_0"] = true,
	["wh_dlc08_nor_mon_fimir_1"] = true,
	["wh_dlc08_nor_mon_frost_wyrm_0"] = true,
	["wh_dlc08_nor_mon_frost_wyrm_boss"] = true,
	["wh_dlc08_nor_mon_frost_wyrm_ror_0"] = true,
	["wh_dlc08_nor_mon_norscan_giant_0"] = true,
	["wh_dlc08_nor_mon_norscan_ice_trolls_0"] = true,
	["wh_dlc08_nor_mon_skinwolves_0"] = true,
	["wh_dlc08_nor_mon_skinwolves_1"] = true,
	["wh_dlc08_nor_mon_war_mammoth_0"] = true,
	["wh_dlc08_nor_mon_war_mammoth_1"] = true,
	["wh_dlc08_nor_mon_war_mammoth_2"] = true,
	["wh_dlc08_nor_mon_war_mammoth_boss"] = true,
	["wh_dlc08_nor_mon_war_mammoth_ror_1"] = true,
	["wh_dlc08_vmp_mon_terrorgheist_boss"] = true,
	["wh_dlc08_wef_forest_dragon_boss"] = true,
	["wh_dlc08_wef_mon_treeman_boss"] = true,
	["wh_main_brt_cha_king_louen_leoncoeur_1"] = true,
	["wh_main_brt_cha_king_louen_leoncoeur_4"] = true,
	["wh_main_brt_cha_lord_2"] = true,
	["wh_main_bst_feral_manticore_summoned"] = true,
	["wh_main_chs_cav_chaos_chariot"] = true,
	["wh_main_chs_cha_chaos_lord_8"] = true,
	["wh_main_chs_cha_chaos_sorcerer_death_7"] = true,
	["wh_main_chs_cha_chaos_sorcerer_fire_7"] = true,
	["wh_main_chs_cha_chaos_sorcerer_metal_7"] = true,
	["wh_main_chs_cha_exalted_hero_7"] = true,
	["wh_main_chs_cha_lord_of_change_0"] = true,
	["wh_main_chs_mon_chaos_spawn"] = true,
	["wh_main_chs_mon_chaos_spawn_summoned"] = true,
	["wh_main_chs_mon_giant"] = true,
	["wh_main_chs_mon_trolls"] = true,
	["wh_main_dwf_cha_high_king_thorgrim_grudgebearer_1"] = true,
	["wh_main_dwf_veh_gyrobomber"] = true,
	["wh_main_dwf_veh_gyrocopter_0"] = true,
	["wh_main_dwf_veh_gyrocopter_1"] = true,
	["wh_main_emp_cha_general_3"] = true,
	["wh_main_emp_cha_karl_franz_1"] = true,
	["wh_main_emp_veh_luminark_of_hysh_0"] = true,
	["wh_main_emp_veh_steam_tank_driver"] = true,
	["wh_main_grn_cav_goblin_wolf_chariot"] = true,
	["wh_main_grn_cha_azhag_the_slaughterer_1"] = true,
	["wh_main_grn_cha_goblin_big_boss_4"] = true,
	["wh_main_grn_cha_goblin_great_shaman_2"] = true,
	["wh_main_grn_cha_orc_warboss_1"] = true,
	["wh_main_grn_mon_arachnarok_spider_0"] = true,
	["wh_main_grn_mon_giant"] = true,
	["wh_main_grn_mon_giant_qb_tall_roff"] = true,
	["wh_main_grn_mon_trolls"] = true,
	["wh_main_nor_cav_chaos_chariot"] = true,
	["wh_main_nor_cha_marauder_chieftan_2"] = true,
	["wh_main_nor_cha_marauder_chieftan_3"] = true,
	["wh_main_nor_mon_chaos_trolls"] = true,
	["wh_main_vmp_cha_mannfred_von_carstein_3"] = true,
	["wh_main_vmp_cha_vampire_lord_3"] = true,
	["wh_main_vmp_mon_crypt_horrors"] = true,
	["wh_main_vmp_mon_crypt_horrors_summoned"] = true,
	["wh_main_vmp_mon_terrorgheist"] = true,
	["wh_main_vmp_mon_terrorgheist_qb"] = true,
	["wh_main_vmp_mon_vargheists"] = true,
	["wh_main_vmp_mon_varghulf"] = true,
	["wh_main_vmp_veh_black_coach"] = true,
	["wh_pro04_bst_inf_cygor_ror_0"] = true,
	["wh_pro04_bst_inf_minotaurs_ror_0"] = true,
	["wh_pro04_chs_mon_chaos_spawn_ror_0"] = true,
	["wh_pro04_chs_mon_dragon_ogre_ror_0"] = true,
	["wh_pro04_nor_mon_fimir_ror_0"] = true,
	["wh_pro04_nor_mon_skinwolves_ror_0"] = true,
	["wh_pro04_nor_mon_war_mammoth_ror_0"] = true,
	["wh_pro04_wef_mon_treekin_ror_0"] = true,
}
FOURTH.class_keys.single = {
	["wh2_dlc09_skv_cha_tretch_craventail"] = true,
	["wh2_dlc09_tmb_art_casket_of_souls_0"] = true,
	["wh2_dlc09_tmb_cha_arkhan_0"] = true,
	["wh2_dlc09_tmb_cha_arkhan_1"] = true,
	["wh2_dlc09_tmb_cha_khalida_0"] = true,
	["wh2_dlc09_tmb_cha_khalida_1"] = true,
	["wh2_dlc09_tmb_cha_khatep_0"] = true,
	["wh2_dlc09_tmb_cha_khatep_1"] = true,
	["wh2_dlc09_tmb_cha_khatep_3"] = true,
	["wh2_dlc09_tmb_cha_liche_priest_death_0"] = true,
	["wh2_dlc09_tmb_cha_liche_priest_death_1"] = true,
	["wh2_dlc09_tmb_cha_liche_priest_light_0"] = true,
	["wh2_dlc09_tmb_cha_liche_priest_light_1"] = true,
	["wh2_dlc09_tmb_cha_liche_priest_nehekhara_0"] = true,
	["wh2_dlc09_tmb_cha_liche_priest_nehekhara_1"] = true,
	["wh2_dlc09_tmb_cha_liche_priest_shadow_0"] = true,
	["wh2_dlc09_tmb_cha_liche_priest_shadow_1"] = true,
	["wh2_dlc09_tmb_cha_necrotect_0"] = true,
	["wh2_dlc09_tmb_cha_settra_0"] = true,
	["wh2_dlc09_tmb_cha_settra_1"] = true,
	["wh2_dlc09_tmb_cha_settra_3"] = true,
	["wh2_dlc09_tmb_cha_tomb_king_0"] = true,
	["wh2_dlc09_tmb_cha_tomb_king_1"] = true,
	["wh2_dlc09_tmb_cha_tomb_king_3"] = true,
	["wh2_dlc09_tmb_cha_tomb_prince_0"] = true,
	["wh2_dlc09_tmb_cha_tomb_prince_1"] = true,
	["wh2_dlc09_tmb_mon_heirotitan_0"] = true,
	["wh2_dlc09_tmb_mon_necrosphinx_0"] = true,
	["wh2_dlc09_tmb_mon_necrosphinx_ror"] = true,
	["wh2_dlc09_tmb_mon_tomb_scorpion_0"] = true,
	["wh2_dlc10_def_cha_crone_0"] = true,
	["wh2_dlc10_def_cha_crone_1"] = true,
	["wh2_dlc10_def_cha_crone_5"] = true,
	["wh2_dlc10_def_cha_sorceress_beasts_0"] = true,
	["wh2_dlc10_def_cha_sorceress_beasts_1"] = true,
	["wh2_dlc10_def_cha_sorceress_beasts_2"] = true,
	["wh2_dlc10_def_cha_sorceress_beasts_3"] = true,
	["wh2_dlc10_def_cha_sorceress_death_0"] = true,
	["wh2_dlc10_def_cha_sorceress_death_1"] = true,
	["wh2_dlc10_def_cha_sorceress_death_2"] = true,
	["wh2_dlc10_def_cha_sorceress_death_3"] = true,
	["wh2_dlc10_def_cha_supreme_sorceress_beasts_0"] = true,
	["wh2_dlc10_def_cha_supreme_sorceress_beasts_1"] = true,
	["wh2_dlc10_def_cha_supreme_sorceress_beasts_2"] = true,
	["wh2_dlc10_def_cha_supreme_sorceress_beasts_3"] = true,
	["wh2_dlc10_def_cha_supreme_sorceress_beasts_4"] = true,
	["wh2_dlc10_def_cha_supreme_sorceress_beasts_5"] = true,
	["wh2_dlc10_def_cha_supreme_sorceress_dark_0"] = true,
	["wh2_dlc10_def_cha_supreme_sorceress_dark_1"] = true,
	["wh2_dlc10_def_cha_supreme_sorceress_dark_2"] = true,
	["wh2_dlc10_def_cha_supreme_sorceress_dark_3"] = true,
	["wh2_dlc10_def_cha_supreme_sorceress_dark_4"] = true,
	["wh2_dlc10_def_cha_supreme_sorceress_dark_5"] = true,
	["wh2_dlc10_def_cha_supreme_sorceress_death_0"] = true,
	["wh2_dlc10_def_cha_supreme_sorceress_death_1"] = true,
	["wh2_dlc10_def_cha_supreme_sorceress_death_2"] = true,
	["wh2_dlc10_def_cha_supreme_sorceress_death_3"] = true,
	["wh2_dlc10_def_cha_supreme_sorceress_death_4"] = true,
	["wh2_dlc10_def_cha_supreme_sorceress_death_5"] = true,
	["wh2_dlc10_def_cha_supreme_sorceress_fire_0"] = true,
	["wh2_dlc10_def_cha_supreme_sorceress_fire_1"] = true,
	["wh2_dlc10_def_cha_supreme_sorceress_fire_2"] = true,
	["wh2_dlc10_def_cha_supreme_sorceress_fire_3"] = true,
	["wh2_dlc10_def_cha_supreme_sorceress_fire_4"] = true,
	["wh2_dlc10_def_cha_supreme_sorceress_fire_5"] = true,
	["wh2_dlc10_def_cha_supreme_sorceress_shadow_0"] = true,
	["wh2_dlc10_def_cha_supreme_sorceress_shadow_1"] = true,
	["wh2_dlc10_def_cha_supreme_sorceress_shadow_2"] = true,
	["wh2_dlc10_def_cha_supreme_sorceress_shadow_3"] = true,
	["wh2_dlc10_def_cha_supreme_sorceress_shadow_4"] = true,
	["wh2_dlc10_def_cha_supreme_sorceress_shadow_5"] = true,
	["wh2_dlc10_def_mon_chill_of_sontar_ror_0"] = true,
	["wh2_dlc10_def_mon_feral_manticore_0"] = true,
	["wh2_dlc10_def_mon_kharibdyss_0"] = true,
	["wh2_dlc10_def_mon_war_hydra_boss"] = true,
	["wh2_dlc10_dwf_cha_thane_ghost_summoned_0"] = true,
	["wh2_dlc10_hef_cha_alarielle_the_radiant_0"] = true,
	["wh2_dlc10_hef_cha_alarielle_the_radiant_1"] = true,
	["wh2_dlc10_hef_cha_alarielle_the_radiant_2"] = true,
	["wh2_dlc10_hef_cha_alarielle_the_radiant_3"] = true,
	["wh2_dlc10_hef_cha_alith_anar_0"] = true,
	["wh2_dlc10_hef_cha_alith_anar_summoned_0"] = true,
	["wh2_dlc10_hef_cha_alith_anar_summoned_1"] = true,
	["wh2_dlc10_hef_cha_handmaiden_0"] = true,
	["wh2_dlc10_hef_cha_handmaiden_1"] = true,
	["wh2_dlc10_hef_cha_handmaiden_2"] = true,
	["wh2_dlc10_hef_cha_mage_heavens_0"] = true,
	["wh2_dlc10_hef_cha_mage_heavens_1"] = true,
	["wh2_dlc10_hef_cha_mage_shadows_0"] = true,
	["wh2_dlc10_hef_cha_mage_shadows_1"] = true,
	["wh2_dlc10_hef_cha_shadow_walker"] = true,
	["wh2_dlc10_hef_mon_treeman_0"] = true,
	["wh2_dlc10_lzd_mon_carnosaur_boss"] = true,
	["wh2_dlc10_nor_mon_phoenix_flamespyre_boss"] = true,
	["wh2_dlc10_skv_mon_hell_pit_abomination_boss"] = true,
	["wh2_dlc11_cst_cha_aranessa_0"] = true,
	["wh2_dlc11_cst_cha_aranessa_1"] = true,
	["wh2_dlc11_cst_cha_cylostra_direfin_0"] = true,
	["wh2_dlc11_cst_cha_cylostra_direfin_1"] = true,
	["wh2_dlc11_cst_cha_damned_paladin_0"] = true,
	["wh2_dlc11_cst_cha_damned_paladin_1"] = true,
	["wh2_dlc11_cst_cha_gunnery_wight_0"] = true,
	["wh2_dlc11_cst_cha_gunnery_wight_1"] = true,
	["wh2_dlc11_cst_cha_luthor_harkon_0"] = true,
	["wh2_dlc11_cst_cha_luthor_harkon_1"] = true,
	["wh2_dlc11_cst_cha_mourngul_haunter"] = true,
	["wh2_dlc11_cst_cha_vampire_fleet_admiral_0"] = true,
	["wh2_dlc11_cst_cha_vampire_fleet_admiral_1"] = true,
	["wh2_dlc11_cst_cha_vampire_fleet_admiral_death_0"] = true,
	["wh2_dlc11_cst_cha_vampire_fleet_admiral_death_1"] = true,
	["wh2_dlc11_cst_cha_vampire_fleet_admiral_deeps_0"] = true,
	["wh2_dlc11_cst_cha_vampire_fleet_admiral_deeps_1"] = true,
	["wh2_dlc11_cst_cha_vampire_fleet_admiral_female_0"] = true,
	["wh2_dlc11_cst_cha_vampire_fleet_admiral_female_1"] = true,
	["wh2_dlc11_cst_cha_vampire_fleet_admiral_female_death_0"] = true,
	["wh2_dlc11_cst_cha_vampire_fleet_admiral_female_death_1"] = true,
	["wh2_dlc11_cst_cha_vampire_fleet_admiral_female_deeps_0"] = true,
	["wh2_dlc11_cst_cha_vampire_fleet_admiral_female_deeps_1"] = true,
	["wh2_dlc11_cst_cha_vampire_fleet_captain_0"] = true,
	["wh2_dlc11_cst_cha_vampire_fleet_captain_1"] = true,
	["wh2_dlc11_cst_cha_vampire_fleet_captain_death_0"] = true,
	["wh2_dlc11_cst_cha_vampire_fleet_captain_death_1"] = true,
	["wh2_dlc11_cst_cha_vampire_fleet_captain_deeps_0"] = true,
	["wh2_dlc11_cst_cha_vampire_fleet_captain_deeps_1"] = true,
	["wh2_dlc11_cst_inf_count_noctilus_0"] = true,
	["wh2_dlc11_cst_inf_count_noctilus_1"] = true,
	["wh2_dlc11_cst_mon_bloated_corpse_0"] = true,
	["wh2_dlc11_cst_mon_terrorgheist"] = true,
	["wh2_dlc11_def_cha_lokhir_fellheart_0"] = true,
	["wh2_dlc11_def_cha_lokhir_fellheart_1"] = true,
	["wh2_dlc11_vmp_cha_bloodline_blood_dragon_lord_0"] = true,
	["wh2_dlc11_vmp_cha_bloodline_blood_dragon_lord_1"] = true,
	["wh2_dlc11_vmp_cha_bloodline_blood_dragon_lord_2"] = true,
	["wh2_dlc11_vmp_cha_bloodline_blood_dragon_lord_3"] = true,
	["wh2_dlc11_vmp_cha_bloodline_lahmian_lord_0"] = true,
	["wh2_dlc11_vmp_cha_bloodline_lahmian_lord_1"] = true,
	["wh2_dlc11_vmp_cha_bloodline_lahmian_lord_2"] = true,
	["wh2_dlc11_vmp_cha_bloodline_lahmian_lord_3"] = true,
	["wh2_dlc11_vmp_cha_bloodline_necrarch_lord_0"] = true,
	["wh2_dlc11_vmp_cha_bloodline_necrarch_lord_1"] = true,
	["wh2_dlc11_vmp_cha_bloodline_necrarch_lord_2"] = true,
	["wh2_dlc11_vmp_cha_bloodline_necrarch_lord_3"] = true,
	["wh2_dlc11_vmp_cha_bloodline_strigoi_lord_0"] = true,
	["wh2_dlc11_vmp_cha_bloodline_strigoi_lord_1"] = true,
	["wh2_dlc11_vmp_cha_bloodline_von_carstein_lord_0"] = true,
	["wh2_dlc11_vmp_cha_bloodline_von_carstein_lord_1"] = true,
	["wh2_dlc11_vmp_cha_bloodline_von_carstein_lord_2"] = true,
	["wh2_dlc11_vmp_cha_bloodline_von_carstein_lord_3"] = true,
	["wh2_dlc11_vmp_cha_heinrich_kemmler_1"] = true,
	["wh2_dlc11_vmp_mon_varghulf_summoned"] = true,
	["wh2_dlc12_lzd_cha_skink_chief_red_crested_0"] = true,
	["wh2_dlc12_lzd_cha_skink_chief_red_crested_1"] = true,
	["wh2_dlc12_lzd_cha_skink_chief_red_crested_2"] = true,
	["wh2_dlc12_lzd_cha_tehenhauin_0"] = true,
	["wh2_dlc12_lzd_cha_tehenhauin_1"] = true,
	["wh2_dlc12_lzd_cha_tehenhauin_2"] = true,
	["wh2_dlc12_lzd_cha_tiktaqto_0"] = true,
	["wh2_dlc12_lzd_cha_tiktaqto_1"] = true,
	["wh2_dlc12_lzd_lzd_cha_kroak_0"] = true,
	["wh2_dlc12_lzd_lzd_cha_kroak_0_boss"] = true,
	["wh2_dlc12_lzd_mon_ancient_salamander_0"] = true,
	["wh2_dlc12_lzd_mon_ancient_salamander_0_blessed"] = true,
	["wh2_dlc12_skv_cha_ikit_claw_0"] = true,
	["wh2_dlc12_skv_cha_ikit_claw_1"] = true,
	["wh2_dlc12_skv_cha_warlock_master_0"] = true,
	["wh2_dlc12_skv_cha_warlock_master_1"] = true,
	["wh2_dlc13_emp_cha_hunter_doctor_hertwig_van_hal_0"] = true,
	["wh2_dlc13_emp_cha_hunter_jorek_grimm_0"] = true,
	["wh2_dlc13_emp_cha_hunter_kalara_of_wydrioth_0"] = true,
	["wh2_dlc13_emp_cha_hunter_rodrik_l_anguille_0"] = true,
	["wh2_dlc13_emp_cha_huntsmarshal_0"] = true,
	["wh2_dlc13_emp_cha_markus_wulfhart_0"] = true,
	["wh2_dlc13_lzd_cha_gor_rok_0"] = true,
	["wh2_dlc13_lzd_cha_kroxigor_ancient_0"] = true,
	["wh2_dlc13_lzd_cha_nakai_0"] = true,
	["wh2_dlc13_lzd_cha_slann_mage_priest_beasts_0"] = true,
	["wh2_dlc13_lzd_cha_slann_mage_priest_death_0"] = true,
	["wh2_dlc13_lzd_cha_slann_mage_priest_fire_0"] = true,
	["wh2_dlc13_lzd_cha_slann_mage_priest_life_0"] = true,
	["wh2_dlc13_lzd_cha_slann_mage_priest_metal_0"] = true,
	["wh2_dlc13_lzd_cha_slann_mage_priest_shadows_0"] = true,
	["wh2_dlc13_lzd_mon_dread_saurian_0"] = true,
	["wh2_dlc14_brt_cha_henri_le_massif_0"] = true,
	["wh2_dlc14_brt_cha_henri_le_massif_3"] = true,
	["wh2_dlc14_brt_cha_henri_le_massif_4"] = true,
	["wh2_dlc14_brt_cha_repanse_de_lyonesse_0"] = true,
	["wh2_dlc14_brt_cha_repanse_de_lyonesse_1"] = true,
	["wh2_dlc14_def_cha_high_beastmaster_0"] = true,
	["wh2_dlc14_def_cha_high_beastmaster_2"] = true,
	["wh2_dlc14_def_cha_malus_darkblade_0"] = true,
	["wh2_dlc14_def_cha_malus_darkblade_0_mp"] = true,
	["wh2_dlc14_def_cha_malus_darkblade_1"] = true,
	["wh2_dlc14_def_cha_malus_darkblade_1_mp"] = true,
	["wh2_dlc14_def_cha_malus_darkblade_tzarkan_0"] = true,
	["wh2_dlc14_def_cha_malus_darkblade_tzarkan_0_final_battle"] = true,
	["wh2_dlc14_def_cha_malus_darkblade_tzarkan_1"] = true,
	["wh2_dlc14_def_cha_master_0"] = true,
	["wh2_dlc14_def_cha_master_1"] = true,
	["wh2_dlc14_def_cha_master_2"] = true,
	["wh2_dlc14_def_cha_master_3"] = true,
	["wh2_dlc14_def_mon_bloodwrack_medusa_0"] = true,
	["wh2_dlc14_def_mon_bloodwrack_medusa_ror_0"] = true,
	["wh2_dlc14_skv_cha_deathmaster_snikch_0"] = true,
	["wh2_dlc14_skv_cha_deathmaster_snikch_tzarkan_0"] = true,
	["wh2_dlc14_skv_cha_eshin_sorcerer_0"] = true,
	["wh2_dlc14_skv_cha_master_assassin_0"] = true,
	["wh2_dlc15_grn_cha_grom_the_paunch_0"] = true,
	["wh2_dlc15_grn_cha_night_goblin_warboss_0_big"] = true,
	["wh2_dlc15_grn_cha_river_troll_hag_0"] = true,
	["wh2_dlc15_grn_mon_feral_hydra_waaagh_0"] = true,
	["wh2_dlc15_grn_mon_rogue_idol_0"] = true,
	["wh2_dlc15_grn_mon_rogue_idol_ror_0"] = true,
	["wh2_dlc15_grn_mon_rogue_idol_summoned_0"] = true,
	["wh2_dlc15_grn_mon_wyvern_waaagh_0"] = true,
	["wh2_dlc15_hef_cha_archmage_beasts_0"] = true,
	["wh2_dlc15_hef_cha_archmage_beasts_1"] = true,
	["wh2_dlc15_hef_cha_archmage_beasts_3"] = true,
	["wh2_dlc15_hef_cha_archmage_beasts_4"] = true,
	["wh2_dlc15_hef_cha_archmage_death_0"] = true,
	["wh2_dlc15_hef_cha_archmage_death_1"] = true,
	["wh2_dlc15_hef_cha_archmage_death_3"] = true,
	["wh2_dlc15_hef_cha_archmage_death_4"] = true,
	["wh2_dlc15_hef_cha_archmage_fire_0"] = true,
	["wh2_dlc15_hef_cha_archmage_fire_1"] = true,
	["wh2_dlc15_hef_cha_archmage_fire_3"] = true,
	["wh2_dlc15_hef_cha_archmage_fire_4"] = true,
	["wh2_dlc15_hef_cha_archmage_heavens_0"] = true,
	["wh2_dlc15_hef_cha_archmage_heavens_1"] = true,
	["wh2_dlc15_hef_cha_archmage_heavens_3"] = true,
	["wh2_dlc15_hef_cha_archmage_heavens_4"] = true,
	["wh2_dlc15_hef_cha_archmage_high_0"] = true,
	["wh2_dlc15_hef_cha_archmage_high_1"] = true,
	["wh2_dlc15_hef_cha_archmage_high_3"] = true,
	["wh2_dlc15_hef_cha_archmage_high_4"] = true,
	["wh2_dlc15_hef_cha_archmage_life_0"] = true,
	["wh2_dlc15_hef_cha_archmage_life_1"] = true,
	["wh2_dlc15_hef_cha_archmage_life_3"] = true,
	["wh2_dlc15_hef_cha_archmage_life_4"] = true,
	["wh2_dlc15_hef_cha_archmage_light_0"] = true,
	["wh2_dlc15_hef_cha_archmage_light_1"] = true,
	["wh2_dlc15_hef_cha_archmage_light_3"] = true,
	["wh2_dlc15_hef_cha_archmage_light_4"] = true,
	["wh2_dlc15_hef_cha_archmage_metal_0"] = true,
	["wh2_dlc15_hef_cha_archmage_metal_1"] = true,
	["wh2_dlc15_hef_cha_archmage_metal_3"] = true,
	["wh2_dlc15_hef_cha_archmage_metal_4"] = true,
	["wh2_dlc15_hef_cha_archmage_shadows_0"] = true,
	["wh2_dlc15_hef_cha_archmage_shadows_1"] = true,
	["wh2_dlc15_hef_cha_archmage_shadows_3"] = true,
	["wh2_dlc15_hef_cha_archmage_shadows_4"] = true,
	["wh2_dlc15_hef_cha_eltharion_the_grim_0"] = true,
	["wh2_dlc15_hef_cha_eltharion_the_grim_1"] = true,
	["wh2_dlc15_hef_cha_eltharion_the_grim_2"] = true,
	["wh2_dlc15_hef_cha_imrik_0"] = true,
	["wh2_dlc15_hef_cha_imrik_1"] = true,
	["wh2_dlc15_hef_cha_imrik_2"] = true,
	["wh2_dlc15_hef_cha_mage_beasts_0"] = true,
	["wh2_dlc15_hef_cha_mage_beasts_1"] = true,
	["wh2_dlc15_hef_cha_mage_death_0"] = true,
	["wh2_dlc15_hef_cha_mage_death_1"] = true,
	["wh2_dlc15_hef_cha_mage_fire_0"] = true,
	["wh2_dlc15_hef_cha_mage_fire_1"] = true,
	["wh2_dlc15_hef_cha_mage_fire_3"] = true,
	["wh2_dlc15_hef_cha_mage_metal_0"] = true,
	["wh2_dlc15_hef_cha_mage_metal_1"] = true,
	["wh2_dlc15_hef_cha_prince_6"] = true,
	["wh2_dlc15_hef_cha_princess_6"] = true,
	["wh2_dlc15_hef_cha_teclis_2"] = true,
	["wh2_dlc15_hef_mon_arcane_phoenix_0"] = true,
	["wh2_dlc15_hef_mon_arcane_phoenix_ror_0"] = true,
	["wh2_dlc15_hef_mon_black_dragon_imrik"] = true,
	["wh2_dlc15_hef_mon_black_dragon_imrik_boss"] = true,
	["wh2_dlc15_hef_mon_forest_dragon_0"] = true,
	["wh2_dlc15_hef_mon_forest_dragon_imrik"] = true,
	["wh2_dlc15_hef_mon_forest_dragon_imrik_boss"] = true,
	["wh2_dlc15_hef_mon_moon_dragon_imrik"] = true,
	["wh2_dlc15_hef_mon_moon_dragon_imrik_boss"] = true,
	["wh2_dlc15_hef_mon_star_dragon_imrik"] = true,
	["wh2_dlc15_hef_mon_star_dragon_imrik_boss"] = true,
	["wh2_dlc15_hef_mon_sun_dragon_imrik"] = true,
	["wh2_dlc15_hef_mon_sun_dragon_imrik_boss"] = true,
	["wh2_dlc16_skv_cha_chieftain_0"] = true,
	["wh2_dlc16_skv_cha_chieftain_1"] = true,
	["wh2_dlc16_skv_cha_ghoritch_0"] = true,
	["wh2_dlc16_skv_cha_ghoritch_0_boss"] = true,
	["wh2_dlc16_skv_cha_packmaster_0"] = true,
	["wh2_dlc16_skv_cha_packmaster_2"] = true,
	["wh2_dlc16_skv_cha_throt_the_unclean_0"] = true,
	["wh2_dlc16_skv_cha_throt_the_unclean_2"] = true,
	["wh2_dlc16_skv_cha_warlord_2"] = true,
	["wh2_dlc16_skv_mon_brood_horror_0"] = true,
	["wh2_dlc16_skv_mon_hell_pit_abomination_ror_0"] = true,
	["wh2_dlc16_skv_mon_rat_ogre_mutant"] = true,
	["wh2_dlc16_skv_mon_rat_ogre_mutant_ror_0"] = true,
	["wh2_dlc16_wef_cha_ancient_treeman_coeddil_0"] = true,
	["wh2_dlc16_wef_cha_ariel_0"] = true,
	["wh2_dlc16_wef_cha_drycha_0"] = true,
	["wh2_dlc16_wef_cha_female_glade_lord_4"] = true,
	["wh2_dlc16_wef_cha_glade_lord_4"] = true,
	["wh2_dlc16_wef_cha_malicious_ancient_treeman_beasts_0"] = true,
	["wh2_dlc16_wef_cha_malicious_ancient_treeman_life_0"] = true,
	["wh2_dlc16_wef_cha_malicious_ancient_treeman_shadows_0"] = true,
	["wh2_dlc16_wef_cha_malicious_branchwraith_beasts_0"] = true,
	["wh2_dlc16_wef_cha_malicious_branchwraith_life_0"] = true,
	["wh2_dlc16_wef_cha_malicious_branchwraith_shadows_0"] = true,
	["wh2_dlc16_wef_cha_spellweaver_beasts_0"] = true,
	["wh2_dlc16_wef_cha_spellweaver_beasts_1"] = true,
	["wh2_dlc16_wef_cha_spellweaver_beasts_2"] = true,
	["wh2_dlc16_wef_cha_spellweaver_beasts_3"] = true,
	["wh2_dlc16_wef_cha_spellweaver_dark_0"] = true,
	["wh2_dlc16_wef_cha_spellweaver_dark_1"] = true,
	["wh2_dlc16_wef_cha_spellweaver_dark_2"] = true,
	["wh2_dlc16_wef_cha_spellweaver_dark_3"] = true,
	["wh2_dlc16_wef_cha_spellweaver_high_0"] = true,
	["wh2_dlc16_wef_cha_spellweaver_high_1"] = true,
	["wh2_dlc16_wef_cha_spellweaver_high_2"] = true,
	["wh2_dlc16_wef_cha_spellweaver_high_3"] = true,
	["wh2_dlc16_wef_cha_spellweaver_life_0"] = true,
	["wh2_dlc16_wef_cha_spellweaver_life_1"] = true,
	["wh2_dlc16_wef_cha_spellweaver_life_2"] = true,
	["wh2_dlc16_wef_cha_spellweaver_life_3"] = true,
	["wh2_dlc16_wef_cha_spellweaver_shadows_0"] = true,
	["wh2_dlc16_wef_cha_spellweaver_shadows_1"] = true,
	["wh2_dlc16_wef_cha_spellweaver_shadows_2"] = true,
	["wh2_dlc16_wef_cha_spellweaver_shadows_3"] = true,
	["wh2_dlc16_wef_mon_ceithin_har_summoned"] = true,
	["wh2_dlc16_wef_mon_feral_manticore"] = true,
	["wh2_dlc16_wef_mon_gwindalor_summoned"] = true,
	["wh2_dlc16_wef_mon_malicious_treeman_0"] = true,
	["wh2_dlc17_bst_cha_doombull_0"] = true,
	["wh2_dlc17_bst_cha_taurox_the_brass_bull_0"] = true,
	["wh2_dlc17_bst_cha_wargor_0"] = true,
	["wh2_dlc17_bst_mon_ghorgon_0"] = true,
	["wh2_dlc17_bst_mon_ghorgon_boss_0"] = true,
	["wh2_dlc17_bst_mon_ghorgon_ror_0"] = true,
	["wh2_dlc17_bst_mon_jabberslythe_0"] = true,
	["wh2_dlc17_bst_mon_jabberslythe_ror_0"] = true,
	["wh2_dlc17_dwf_cha_thane_ghost_2"] = true,
	["wh2_dlc17_dwf_cha_thorek_ironbrow_0"] = true,
	["wh2_dlc17_dwf_cha_thorek_ironbrow_1"] = true,
	["wh2_dlc17_dwf_mon_carnosaur_thorek_0"] = true,
	["wh2_dlc17_lzd_cha_oxyotl_0"] = true,
	["wh2_dlc17_lzd_cha_skink_oracle_troglodon_0"] = true,
	["wh2_dlc17_lzd_mon_carnosaur_ror_0"] = true,
	["wh2_dlc17_lzd_mon_coatl_0"] = true,
	["wh2_dlc17_lzd_mon_coatl_ror_0"] = true,
	["wh2_dlc17_lzd_mon_dread_saurian_qb_boss"] = true,
	["wh2_dlc17_lzd_mon_troglodon_0"] = true,
	["wh2_dlc17_lzd_mon_troglodon_ror_0"] = true,
	["wh2_main_def_cha_death_hag_0"] = true,
	["wh2_main_def_cha_dreadlord_0"] = true,
	["wh2_main_def_cha_dreadlord_1"] = true,
	["wh2_main_def_cha_dreadlord_2"] = true,
	["wh2_main_def_cha_dreadlord_4"] = true,
	["wh2_main_def_cha_dreadlord_5"] = true,
	["wh2_main_def_cha_dreadlord_female_0"] = true,
	["wh2_main_def_cha_dreadlord_female_1"] = true,
	["wh2_main_def_cha_dreadlord_female_2"] = true,
	["wh2_main_def_cha_dreadlord_female_4"] = true,
	["wh2_main_def_cha_dreadlord_female_5"] = true,
	["wh2_main_def_cha_khainite_assassin_0"] = true,
	["wh2_main_def_cha_malekith_0"] = true,
	["wh2_main_def_cha_malekith_1"] = true,
	["wh2_main_def_cha_malekith_2"] = true,
	["wh2_main_def_cha_malekith_3"] = true,
	["wh2_main_def_cha_morathi_0"] = true,
	["wh2_main_def_cha_morathi_1"] = true,
	["wh2_main_def_cha_sorceress_dark_0"] = true,
	["wh2_main_def_cha_sorceress_dark_1"] = true,
	["wh2_main_def_cha_sorceress_dark_2"] = true,
	["wh2_main_def_cha_sorceress_dark_3"] = true,
	["wh2_main_def_cha_sorceress_fire_0"] = true,
	["wh2_main_def_cha_sorceress_fire_1"] = true,
	["wh2_main_def_cha_sorceress_fire_2"] = true,
	["wh2_main_def_cha_sorceress_fire_3"] = true,
	["wh2_main_def_cha_sorceress_shadow_0"] = true,
	["wh2_main_def_cha_sorceress_shadow_1"] = true,
	["wh2_main_def_cha_sorceress_shadow_2"] = true,
	["wh2_main_def_cha_sorceress_shadow_3"] = true,
	["wh2_main_def_mon_black_dragon"] = true,
	["wh2_main_def_mon_war_hydra_0"] = true,
	["wh2_main_hef_cha_alastar_0"] = true,
	["wh2_main_hef_cha_alastar_3"] = true,
	["wh2_main_hef_cha_alastar_4"] = true,
	["wh2_main_hef_cha_alastar_5"] = true,
	["wh2_main_hef_cha_loremaster_of_hoeth_0"] = true,
	["wh2_main_hef_cha_mage_high_0"] = true,
	["wh2_main_hef_cha_mage_high_1"] = true,
	["wh2_main_hef_cha_mage_life_0"] = true,
	["wh2_main_hef_cha_mage_life_1"] = true,
	["wh2_main_hef_cha_mage_light_0"] = true,
	["wh2_main_hef_cha_mage_light_1"] = true,
	["wh2_main_hef_cha_noble_0"] = true,
	["wh2_main_hef_cha_noble_2"] = true,
	["wh2_main_hef_cha_noble_3"] = true,
	["wh2_main_hef_cha_prince_0"] = true,
	["wh2_main_hef_cha_prince_2"] = true,
	["wh2_main_hef_cha_prince_3"] = true,
	["wh2_main_hef_cha_prince_4"] = true,
	["wh2_main_hef_cha_prince_5"] = true,
	["wh2_main_hef_cha_princess_0"] = true,
	["wh2_main_hef_cha_princess_1"] = true,
	["wh2_main_hef_cha_princess_3"] = true,
	["wh2_main_hef_cha_princess_4"] = true,
	["wh2_main_hef_cha_princess_5"] = true,
	["wh2_main_hef_cha_teclis_0"] = true,
	["wh2_main_hef_cha_teclis_1"] = true,
	["wh2_main_hef_cha_tyrion_0"] = true,
	["wh2_main_hef_cha_tyrion_1"] = true,
	["wh2_main_hef_mon_great_eagle"] = true,
	["wh2_main_hef_mon_great_eagle_summoned"] = true,
	["wh2_main_hef_mon_moon_dragon"] = true,
	["wh2_main_hef_mon_phoenix_flamespyre"] = true,
	["wh2_main_hef_mon_phoenix_frostheart"] = true,
	["wh2_main_hef_mon_star_dragon"] = true,
	["wh2_main_hef_mon_sun_dragon"] = true,
	["wh2_main_lzd_cha_kroq_gar_0"] = true,
	["wh2_main_lzd_cha_kroq_gar_1"] = true,
	["wh2_main_lzd_cha_kroq_gar_2"] = true,
	["wh2_main_lzd_cha_kroq_gar_3"] = true,
	["wh2_main_lzd_cha_lord_mazdamundi_0"] = true,
	["wh2_main_lzd_cha_saurus_old_blood_0"] = true,
	["wh2_main_lzd_cha_saurus_old_blood_1"] = true,
	["wh2_main_lzd_cha_saurus_old_blood_2"] = true,
	["wh2_main_lzd_cha_saurus_scar_veteran_0"] = true,
	["wh2_main_lzd_cha_saurus_scar_veteran_1"] = true,
	["wh2_main_lzd_cha_saurus_scar_veteran_2"] = true,
	["wh2_main_lzd_cha_skink_chief_0"] = true,
	["wh2_main_lzd_cha_skink_chief_1"] = true,
	["wh2_main_lzd_cha_skink_priest_0_summoned"] = true,
	["wh2_main_lzd_cha_skink_priest_beasts_0"] = true,
	["wh2_main_lzd_cha_skink_priest_beasts_1"] = true,
	["wh2_main_lzd_cha_skink_priest_heavens_0"] = true,
	["wh2_main_lzd_cha_skink_priest_heavens_1"] = true,
	["wh2_main_lzd_cha_slann_mage_priest_campaign_0"] = true,
	["wh2_main_lzd_cha_slann_mage_priest_heavens_0"] = true,
	["wh2_main_lzd_cha_slann_mage_priest_high_0"] = true,
	["wh2_main_lzd_cha_slann_mage_priest_life_0_qb"] = true,
	["wh2_main_lzd_cha_slann_mage_priest_light_0"] = true,
	["wh2_main_lzd_mon_bastiladon_0"] = true,
	["wh2_main_lzd_mon_carnosaur_0"] = true,
	["wh2_main_lzd_mon_carnosaur_blessed_0"] = true,
	["wh2_main_lzd_mon_stegadon_0"] = true,
	["wh2_main_skv_cha_assassin"] = true,
	["wh2_main_skv_cha_grey_seer_plague_0"] = true,
	["wh2_main_skv_cha_grey_seer_plague_1"] = true,
	["wh2_main_skv_cha_grey_seer_ruin_0"] = true,
	["wh2_main_skv_cha_grey_seer_ruin_1"] = true,
	["wh2_main_skv_cha_lord_skrolk"] = true,
	["wh2_main_skv_cha_plague_priest_0"] = true,
	["wh2_main_skv_cha_plague_priest_2"] = true,
	["wh2_main_skv_cha_queek_headtaker"] = true,
	["wh2_main_skv_cha_warlock_engineer"] = true,
	["wh2_main_skv_cha_warlord_0"] = true,
	["wh2_main_skv_cha_warlord_1"] = true,
	["wh2_main_skv_mon_hell_pit_abomination"] = true,
	["wh2_main_skv_mon_hell_pit_abomination_summoned"] = true,
	["wh2_pro06_tmb_mon_bone_giant_0"] = true,
	["wh2_pro07_emp_cha_wizard_death_0"] = true,
	["wh2_pro07_emp_cha_wizard_death_1"] = true,
	["wh2_pro07_emp_cha_wizard_death_2"] = true,
	["wh2_pro07_emp_cha_wizard_death_3"] = true,
	["wh2_pro08_neu_cha_felix"] = true,
	["wh2_pro08_neu_cha_gotrek"] = true,
	["wh2_pro09_grn_cha_black_orc_big_boss_0"] = true,
	["wh2_pro09_grn_cha_black_orc_big_boss_1"] = true,
	["wh2_twa02_wef_cha_glade_captain_0"] = true,
	["wh2_twa02_wef_cha_glade_captain_1"] = true,
	["wh2_twa02_wef_cha_glade_captain_2"] = true,
	["wh2_twa02_wef_cha_glade_captain_3"] = true,
	["wh2_twa03_def_cha_rakarth_0"] = true,
	["wh2_twa03_def_cha_rakarth_2"] = true,
	["wh2_twa03_def_cha_rakarth_3"] = true,
	["wh2_twa03_def_mon_war_mammoth_0"] = true,
	["wh2_twa04_bst_cha_great_bray_shaman_beasts_0"] = true,
	["wh2_twa04_bst_cha_great_bray_shaman_death_0"] = true,
	["wh2_twa04_bst_cha_great_bray_shaman_shadows_0"] = true,
	["wh2_twa04_bst_cha_great_bray_shaman_wild_0"] = true,
	["wh3_cp1_cth_cha_bhashiva"] = true,
	["wh3_cp1_cth_cha_clawspeaker_beasts"] = true,
	["wh3_cp1_cth_cha_clawspeaker_life"] = true,
	["wh3_cp1_cth_cha_clawspeaker_shadows"] = true,
	["wh3_cp1_cth_cha_sawai"] = true,
	["wh3_cp1_cth_cha_taoyan"] = true,
	["wh3_cp1_cth_mon_celestial_lion_summoned"] = true,
	["wh3_cp1_tze_cha_qb_exalted_lord_of_change_boss"] = true,
	["wh3_dlc20_chs_cha_chaos_lord_mkho"] = true,
	["wh3_dlc20_chs_cha_chaos_lord_mkho_chaos_steed"] = true,
	["wh3_dlc20_chs_cha_chaos_lord_mkho_juggernaut"] = true,
	["wh3_dlc20_chs_cha_chaos_lord_msla"] = true,
	["wh3_dlc20_chs_cha_chaos_lord_msla_chaos_steed"] = true,
	["wh3_dlc20_chs_cha_chaos_sorcerer_death_warshrine"] = true,
	["wh3_dlc20_chs_cha_chaos_sorcerer_fire_warshrine"] = true,
	["wh3_dlc20_chs_cha_chaos_sorcerer_lord_death_mnur"] = true,
	["wh3_dlc20_chs_cha_chaos_sorcerer_lord_death_mnur_chaos_steed"] = true,
	["wh3_dlc20_chs_cha_chaos_sorcerer_lord_death_mnur_warshrine"] = true,
	["wh3_dlc20_chs_cha_chaos_sorcerer_lord_death_warshrine"] = true,
	["wh3_dlc20_chs_cha_chaos_sorcerer_lord_fire_warshrine"] = true,
	["wh3_dlc20_chs_cha_chaos_sorcerer_lord_metal_mtze"] = true,
	["wh3_dlc20_chs_cha_chaos_sorcerer_lord_metal_mtze_chaos_steed"] = true,
	["wh3_dlc20_chs_cha_chaos_sorcerer_lord_metal_mtze_disc"] = true,
	["wh3_dlc20_chs_cha_chaos_sorcerer_lord_metal_mtze_warshrine"] = true,
	["wh3_dlc20_chs_cha_chaos_sorcerer_lord_metal_warshrine"] = true,
	["wh3_dlc20_chs_cha_chaos_sorcerer_lord_nurgle_mnur"] = true,
	["wh3_dlc20_chs_cha_chaos_sorcerer_lord_nurgle_mnur_chaos_steed"] = true,
	["wh3_dlc20_chs_cha_chaos_sorcerer_lord_nurgle_mnur_warshrine"] = true,
	["wh3_dlc20_chs_cha_chaos_sorcerer_lord_shadows_warshrine"] = true,
	["wh3_dlc20_chs_cha_chaos_sorcerer_lord_tzeentch_mtze"] = true,
	["wh3_dlc20_chs_cha_chaos_sorcerer_lord_tzeentch_mtze_chaos_steed"] = true,
	["wh3_dlc20_chs_cha_chaos_sorcerer_lord_tzeentch_mtze_disc"] = true,
	["wh3_dlc20_chs_cha_chaos_sorcerer_lord_tzeentch_mtze_warshrine"] = true,
	["wh3_dlc20_chs_cha_chaos_sorcerer_metal_mtze"] = true,
	["wh3_dlc20_chs_cha_chaos_sorcerer_metal_mtze_chaos_steed"] = true,
	["wh3_dlc20_chs_cha_chaos_sorcerer_metal_mtze_disc"] = true,
	["wh3_dlc20_chs_cha_chaos_sorcerer_metal_mtze_warshrine"] = true,
	["wh3_dlc20_chs_cha_chaos_sorcerer_metal_warshrine"] = true,
	["wh3_dlc20_chs_cha_chaos_sorcerer_shadows_msla"] = true,
	["wh3_dlc20_chs_cha_chaos_sorcerer_shadows_msla_chaos_steed"] = true,
	["wh3_dlc20_chs_cha_chaos_sorcerer_shadows_msla_warshrine"] = true,
	["wh3_dlc20_chs_cha_chaos_sorcerer_shadows_warshrine"] = true,
	["wh3_dlc20_chs_cha_chaos_sorcerer_slaanesh_msla"] = true,
	["wh3_dlc20_chs_cha_chaos_sorcerer_slaanesh_msla_chaos_steed"] = true,
	["wh3_dlc20_chs_cha_chaos_sorcerer_slaanesh_msla_warshrine"] = true,
	["wh3_dlc20_chs_cha_chaos_sorcerer_tzeentch_mtze"] = true,
	["wh3_dlc20_chs_cha_chaos_sorcerer_tzeentch_mtze_chaos_steed"] = true,
	["wh3_dlc20_chs_cha_chaos_sorcerer_tzeentch_mtze_disc"] = true,
	["wh3_dlc20_chs_cha_chaos_sorcerer_tzeentch_mtze_warshrine"] = true,
	["wh3_dlc20_chs_cha_cultist_msla_warshrine"] = true,
	["wh3_dlc20_chs_cha_daemon_prince"] = true,
	["wh3_dlc20_chs_cha_daemon_prince_mkho"] = true,
	["wh3_dlc20_chs_cha_daemon_prince_mnur"] = true,
	["wh3_dlc20_chs_cha_daemon_prince_msla"] = true,
	["wh3_dlc20_chs_cha_daemon_prince_mtze"] = true,
	["wh3_dlc20_chs_cha_exalted_hero_mkho"] = true,
	["wh3_dlc20_chs_cha_exalted_hero_mkho_chaos_steed"] = true,
	["wh3_dlc20_chs_cha_exalted_hero_mkho_juggernaut"] = true,
	["wh3_dlc20_chs_cha_exalted_hero_mnur"] = true,
	["wh3_dlc20_chs_cha_exalted_hero_mnur_chaos_steed"] = true,
	["wh3_dlc20_chs_mon_giant_mnur_ror"] = true,
	["wh3_dlc20_chs_mon_warshrine"] = true,
	["wh3_dlc20_chs_mon_warshrine_mkho"] = true,
	["wh3_dlc20_chs_mon_warshrine_mnur"] = true,
	["wh3_dlc20_chs_mon_warshrine_msla"] = true,
	["wh3_dlc20_chs_mon_warshrine_mtze"] = true,
	["wh3_dlc20_kho_cha_cultist_mkho_warshrine"] = true,
	["wh3_dlc20_kho_cha_valkia"] = true,
	["wh3_dlc20_nur_cha_cultist_mnur_warshrine"] = true,
	["wh3_dlc20_nur_cha_festus"] = true,
	["wh3_dlc20_sla_cha_azazel"] = true,
	["wh3_dlc20_tze_cha_cultist_mtze_warshrine"] = true,
	["wh3_dlc20_tze_cha_vilitch"] = true,
	["wh3_dlc23_chd_cha_astragoth_ironhand"] = true,
	["wh3_dlc23_chd_cha_bull_centaur_taurruk"] = true,
	["wh3_dlc23_chd_cha_daemonsmith_sorcerer_death"] = true,
	["wh3_dlc23_chd_cha_daemonsmith_sorcerer_death_bale_taurus"] = true,
	["wh3_dlc23_chd_cha_daemonsmith_sorcerer_death_great_taurus"] = true,
	["wh3_dlc23_chd_cha_daemonsmith_sorcerer_death_lammasu"] = true,
	["wh3_dlc23_chd_cha_daemonsmith_sorcerer_fire"] = true,
	["wh3_dlc23_chd_cha_daemonsmith_sorcerer_fire_bale_taurus"] = true,
	["wh3_dlc23_chd_cha_daemonsmith_sorcerer_fire_great_taurus"] = true,
	["wh3_dlc23_chd_cha_daemonsmith_sorcerer_fire_lammasu"] = true,
	["wh3_dlc23_chd_cha_daemonsmith_sorcerer_hashut"] = true,
	["wh3_dlc23_chd_cha_daemonsmith_sorcerer_hashut_bale_taurus"] = true,
	["wh3_dlc23_chd_cha_daemonsmith_sorcerer_hashut_great_taurus"] = true,
	["wh3_dlc23_chd_cha_daemonsmith_sorcerer_hashut_lammasu"] = true,
	["wh3_dlc23_chd_cha_daemonsmith_sorcerer_metal"] = true,
	["wh3_dlc23_chd_cha_daemonsmith_sorcerer_metal_bale_taurus"] = true,
	["wh3_dlc23_chd_cha_daemonsmith_sorcerer_metal_great_taurus"] = true,
	["wh3_dlc23_chd_cha_daemonsmith_sorcerer_metal_lammasu"] = true,
	["wh3_dlc23_chd_cha_drazhoath_the_ashen"] = true,
	["wh3_dlc23_chd_cha_drazhoath_the_ashen_bale_taurus_cinderbreath"] = true,
	["wh3_dlc23_chd_cha_gorduz_backstabber"] = true,
	["wh3_dlc23_chd_cha_gorduz_backstabber_giant_wolf"] = true,
	["wh3_dlc23_chd_cha_infernal_castellan"] = true,
	["wh3_dlc23_chd_cha_overseer"] = true,
	["wh3_dlc23_chd_cha_overseer_great_taurus"] = true,
	["wh3_dlc23_chd_cha_overseer_lammasu"] = true,
	["wh3_dlc23_chd_cha_sorcerer_prophet_death"] = true,
	["wh3_dlc23_chd_cha_sorcerer_prophet_death_bale_taurus"] = true,
	["wh3_dlc23_chd_cha_sorcerer_prophet_death_great_taurus"] = true,
	["wh3_dlc23_chd_cha_sorcerer_prophet_death_lammasu"] = true,
	["wh3_dlc23_chd_cha_sorcerer_prophet_fire"] = true,
	["wh3_dlc23_chd_cha_sorcerer_prophet_fire_bale_taurus"] = true,
	["wh3_dlc23_chd_cha_sorcerer_prophet_fire_great_taurus"] = true,
	["wh3_dlc23_chd_cha_sorcerer_prophet_fire_lammasu"] = true,
	["wh3_dlc23_chd_cha_sorcerer_prophet_hashut"] = true,
	["wh3_dlc23_chd_cha_sorcerer_prophet_hashut_bale_taurus"] = true,
	["wh3_dlc23_chd_cha_sorcerer_prophet_hashut_great_taurus"] = true,
	["wh3_dlc23_chd_cha_sorcerer_prophet_hashut_lammasu"] = true,
	["wh3_dlc23_chd_cha_sorcerer_prophet_metal"] = true,
	["wh3_dlc23_chd_cha_sorcerer_prophet_metal_bale_taurus"] = true,
	["wh3_dlc23_chd_cha_sorcerer_prophet_metal_great_taurus"] = true,
	["wh3_dlc23_chd_cha_sorcerer_prophet_metal_lammasu"] = true,
	["wh3_dlc23_chd_cha_zhatan_the_black"] = true,
	["wh3_dlc23_chd_cha_zhatan_the_black_great_taurus"] = true,
	["wh3_dlc23_chd_cha_zhatan_the_black_lammasu"] = true,
	["wh3_dlc23_chd_mon_bale_taurus"] = true,
	["wh3_dlc23_chd_mon_great_taurus"] = true,
	["wh3_dlc23_chd_mon_kdaai_destroyer"] = true,
	["wh3_dlc23_chd_mon_lammasu"] = true,
	["wh3_dlc23_chd_veh_deathshrieker_rocket_launcher"] = true,
	["wh3_dlc23_chd_veh_magma_cannon"] = true,
	["wh3_dlc23_chd_veh_skullcracker"] = true,
	["wh3_dlc23_neu_cha_ulrika"] = true,
	["wh3_dlc23_neu_cha_ulrika_warhorse"] = true,
	["wh3_dlc24_chs_cha_chaos_lord_mtze"] = true,
	["wh3_dlc24_chs_cha_chaos_lord_mtze_chaos_steed"] = true,
	["wh3_dlc24_chs_cha_chaos_lord_mtze_disc"] = true,
	["wh3_dlc24_chs_cha_exalted_hero_mtze"] = true,
	["wh3_dlc24_chs_cha_exalted_hero_mtze_chaos_steed"] = true,
	["wh3_dlc24_chs_cha_exalted_hero_mtze_disc"] = true,
	["wh3_dlc24_cth_cha_astromancer_great_moon_bird"] = true,
	["wh3_dlc24_cth_cha_celestial_general_yang"] = true,
	["wh3_dlc24_cth_cha_celestial_general_yang_cathayan_horse"] = true,
	["wh3_dlc24_cth_cha_celestial_general_yang_celestial_lion"] = true,
	["wh3_dlc24_cth_cha_celestial_general_yang_longma"] = true,
	["wh3_dlc24_cth_cha_gate_master"] = true,
	["wh3_dlc24_cth_cha_gate_master_warhorse"] = true,
	["wh3_dlc24_cth_cha_saytang_the_watcher"] = true,
	["wh3_dlc24_cth_cha_yuan_bo_dragon"] = true,
	["wh3_dlc24_cth_cha_yuan_bo_human"] = true,
	["wh3_dlc24_cth_mon_celestial_lion"] = true,
	["wh3_dlc24_cth_mon_great_moon_bird"] = true,
	["wh3_dlc24_cth_mon_jade_lion"] = true,
	["wh3_dlc24_cth_mon_jet_lion"] = true,
	["wh3_dlc24_grn_cha_grimgor_ironhide_quest_battle"] = true,
	["wh3_dlc24_ksl_cha_druzhina"] = true,
	["wh3_dlc24_ksl_cha_druzhina_warhorse"] = true,
	["wh3_dlc24_ksl_cha_golden_knight"] = true,
	["wh3_dlc24_ksl_cha_golden_knight_warhorse"] = true,
	["wh3_dlc24_ksl_cha_hag_witch_beast"] = true,
	["wh3_dlc24_ksl_cha_hag_witch_death"] = true,
	["wh3_dlc24_ksl_cha_hag_witch_hag"] = true,
	["wh3_dlc24_ksl_cha_hag_witch_shadow"] = true,
	["wh3_dlc24_ksl_cha_ice_witch_ice_frost_wyrm"] = true,
	["wh3_dlc24_ksl_cha_ice_witch_tempest_frost_wyrm"] = true,
	["wh3_dlc24_ksl_cha_katarin_frost_wyrm"] = true,
	["wh3_dlc24_ksl_mon_frost_wyrm"] = true,
	["wh3_dlc24_ksl_mon_incarnate_elemental_of_beasts"] = true,
	["wh3_dlc24_ksl_mon_incarnate_elemental_of_beasts_summoned"] = true,
	["wh3_dlc24_tze_cha_aekold_helbrass"] = true,
	["wh3_dlc24_tze_cha_blue_scribes"] = true,
	["wh3_dlc24_tze_cha_changeling"] = true,
	["wh3_dlc24_tze_cha_changeling_quest_battle"] = true,
	["wh3_dlc24_tze_cha_changeling_summoned_0"] = true,
	["wh3_dlc24_tze_mon_cockatrice"] = true,
	["wh3_dlc24_tze_mon_mutalith_vortex_beast"] = true,
	["wh3_dlc24_tze_mon_mutalith_vortex_beast_ror"] = true,
	["wh3_dlc25_bst_mon_jabberslythe_qb_boss"] = true,
	["wh3_dlc25_chs_cha_chaos_lord_mnur"] = true,
	["wh3_dlc25_chs_cha_chaos_lord_mnur_chaos_steed"] = true,
	["wh3_dlc25_chs_cha_chaos_lord_mnur_rot_beast"] = true,
	["wh3_dlc25_chs_cha_chaos_sorcerer_death_mnur"] = true,
	["wh3_dlc25_chs_cha_chaos_sorcerer_death_mnur_chaos_steed"] = true,
	["wh3_dlc25_chs_cha_chaos_sorcerer_death_mnur_rot_beast"] = true,
	["wh3_dlc25_chs_cha_chaos_sorcerer_death_mnur_warshrine"] = true,
	["wh3_dlc25_chs_cha_chaos_sorcerer_lord_death_mnur_rot_beast"] = true,
	["wh3_dlc25_chs_cha_chaos_sorcerer_lord_nurgle_mnur_rot_beast"] = true,
	["wh3_dlc25_chs_cha_chaos_sorcerer_nurgle_mnur"] = true,
	["wh3_dlc25_chs_cha_chaos_sorcerer_nurgle_mnur_chaos_steed"] = true,
	["wh3_dlc25_chs_cha_chaos_sorcerer_nurgle_mnur_rot_beast"] = true,
	["wh3_dlc25_chs_cha_chaos_sorcerer_nurgle_mnur_warshrine"] = true,
	["wh3_dlc25_chs_cha_exalted_hero_mnur_rot_beast"] = true,
	["wh3_dlc25_dwf_cha_daemon_slayer"] = true,
	["wh3_dlc25_dwf_cha_dragon_slayer"] = true,
	["wh3_dlc25_dwf_cha_garagrim_ironfist"] = true,
	["wh3_dlc25_dwf_cha_malakai_makaisson"] = true,
	["wh3_dlc25_emp_cha_elspeth_von_draken"] = true,
	["wh3_dlc25_emp_cha_elspeth_von_draken_carmine_dragon"] = true,
	["wh3_dlc25_emp_cha_elspeth_von_draken_warhorse"] = true,
	["wh3_dlc25_emp_cha_engineer"] = true,
	["wh3_dlc25_emp_cha_engineer_mechanical_steed"] = true,
	["wh3_dlc25_emp_cha_engineer_warhorse"] = true,
	["wh3_dlc25_emp_cha_master_engineer"] = true,
	["wh3_dlc25_emp_cha_master_engineer_mechanical_steed"] = true,
	["wh3_dlc25_emp_cha_master_engineer_warhorse"] = true,
	["wh3_dlc25_emp_cha_theodore_bruckner"] = true,
	["wh3_dlc25_emp_cha_theodore_bruckner_demigryph_reaper"] = true,
	["wh3_dlc25_emp_cha_wizard_metal"] = true,
	["wh3_dlc25_emp_cha_wizard_metal_pegasus"] = true,
	["wh3_dlc25_emp_cha_wizard_metal_warhorse"] = true,
	["wh3_dlc25_emp_mon_incarnate_elemental_of_beasts_summoned"] = true,
	["wh3_dlc25_grn_mon_rogue_idol_qb_boss"] = true,
	["wh3_dlc25_hef_mon_sun_dragon_boss"] = true,
	["wh3_dlc25_nur_cha_bray_shaman_wild_chieftain"] = true,
	["wh3_dlc25_nur_cha_epidemius"] = true,
	["wh3_dlc25_nur_cha_exalted_great_unclean_one_nurgle_qb_boss"] = true,
	["wh3_dlc25_nur_cha_exalted_hero_chieftain"] = true,
	["wh3_dlc25_nur_cha_exalted_hero_chieftain_chaos_dragon"] = true,
	["wh3_dlc25_nur_cha_exalted_hero_chieftain_chaos_steed"] = true,
	["wh3_dlc25_nur_cha_fimir_balefiend_shadow_chieftain"] = true,
	["wh3_dlc25_nur_cha_infernal_castellan_chieftain"] = true,
	["wh3_dlc25_nur_cha_kayzk_the_befouled"] = true,
	["wh3_dlc25_nur_cha_skin_wolf_werekin_chieftain"] = true,
	["wh3_dlc25_nur_cha_tamurkhan"] = true,
	["wh3_dlc25_nur_cha_tamurkhan_bubebolos"] = true,
	["wh3_dlc25_nur_mon_soul_grinder_0_ror"] = true,
	["wh3_dlc25_nur_mon_toad_dragon"] = true,
	["wh3_dlc26_grn_cha_gorbad_ironclaw"] = true,
	["wh3_dlc26_grn_cha_gorbad_ironclaw_gnarla"] = true,
	["wh3_dlc26_grn_cha_night_goblin_big_boss"] = true,
	["wh3_dlc26_grn_cha_night_goblin_big_boss_squig"] = true,
	["wh3_dlc26_grn_cha_savage_orc_great_shaman"] = true,
	["wh3_dlc26_grn_cha_savage_orc_great_shaman_boar"] = true,
	["wh3_dlc26_grn_cha_savage_orc_great_shaman_wyvern"] = true,
	["wh3_dlc26_grn_cha_snagla_grobspit"] = true,
	["wh3_dlc26_grn_mon_colossal_squig"] = true,
	["wh3_dlc26_grn_mon_colossal_squig_ror"] = true,
	["wh3_dlc26_grn_mon_wyvern_summoned"] = true,
	["wh3_dlc26_kho_cha_arbaal"] = true,
	["wh3_dlc26_kho_cha_arbaal_flesh_hound"] = true,
	["wh3_dlc26_kho_cha_bloodspeaker"] = true,
	["wh3_dlc26_kho_cha_bloodspeaker_chaos_steed"] = true,
	["wh3_dlc26_kho_cha_bloodspeaker_warshrine"] = true,
	["wh3_dlc26_kho_cha_scyla_anfingrimm"] = true,
	["wh3_dlc26_kho_cha_skarr_bloodwrath"] = true,
	["wh3_dlc26_kho_cha_skulltaker"] = true,
	["wh3_dlc26_kho_cha_skulltaker_bloodthrone"] = true,
	["wh3_dlc26_kho_cha_skulltaker_juggernaut"] = true,
	["wh3_dlc26_kho_mon_slaughterbrute"] = true,
	["wh3_dlc26_kho_veh_skullcannon_ror"] = true,
	["wh3_dlc26_ogr_cha_bragg_the_gutsman"] = true,
	["wh3_dlc26_ogr_cha_bruiser"] = true,
	["wh3_dlc26_ogr_cha_butcher_death"] = true,
	["wh3_dlc26_ogr_cha_butcher_heavens"] = true,
	["wh3_dlc26_ogr_cha_golgfag_maneater"] = true,
	["wh3_dlc26_ogr_cha_paymaster"] = true,
	["wh3_dlc26_ogr_cha_slaughtermaster_death"] = true,
	["wh3_dlc26_ogr_cha_slaughtermaster_heavens"] = true,
	["wh3_dlc26_ogr_inf_eshin_maneater_ror"] = true,
	["wh3_dlc27_bst_mon_ghorgon_boss"] = true,
	["wh3_dlc27_bst_mon_jabberslythe_boss"] = true,
	["wh3_dlc27_chd_mon_bale_taurus_boss"] = true,
	["wh3_dlc27_chd_mon_lammasu_boss"] = true,
	["wh3_dlc27_chs_cha_chaos_lord_msla_daemonic_steed"] = true,
	["wh3_dlc27_chs_cha_chaos_sorcerer_shadows_msla_daemonic_steed"] = true,
	["wh3_dlc27_chs_cha_chaos_sorcerer_slaanesh_msla_daemonic_steed"] = true,
	["wh3_dlc27_chs_cha_daemon_prince_mkho_qb"] = true,
	["wh3_dlc27_chs_cha_exalted_hero_msla"] = true,
	["wh3_dlc27_chs_cha_exalted_hero_msla_chaos_steed"] = true,
	["wh3_dlc27_chs_cha_exalted_hero_msla_daemonic_steed"] = true,
	["wh3_dlc27_chs_cha_sorcerer_lord_shadows_msla"] = true,
	["wh3_dlc27_chs_cha_sorcerer_lord_shadows_msla_chaos_steed"] = true,
	["wh3_dlc27_chs_cha_sorcerer_lord_shadows_msla_daemonic_steed"] = true,
	["wh3_dlc27_chs_cha_sorcerer_lord_shadows_msla_warshrine"] = true,
	["wh3_dlc27_chs_cha_sorcerer_lord_slaanesh_msla"] = true,
	["wh3_dlc27_chs_cha_sorcerer_lord_slaanesh_msla_chaos_steed"] = true,
	["wh3_dlc27_chs_cha_sorcerer_lord_slaanesh_msla_daemonic_steed"] = true,
	["wh3_dlc27_chs_cha_sorcerer_lord_slaanesh_msla_warshrine"] = true,
	["wh3_dlc27_chs_feral_manticore_boss"] = true,
	["wh3_dlc27_cth_mon_celestial_lion_boss"] = true,
	["wh3_dlc27_def_mon_black_dragon_boss"] = true,
	["wh3_dlc27_hef_cha_caradryan"] = true,
	["wh3_dlc27_hef_cha_caradryan_ashtari"] = true,
	["wh3_dlc27_hef_cha_caradryan_steed"] = true,
	["wh3_dlc27_hef_cha_mist_mage"] = true,
	["wh3_dlc27_hef_cha_mist_mage_eagle"] = true,
	["wh3_dlc27_hef_cha_sea_helm"] = true,
	["wh3_dlc27_hef_cha_sea_helm_eagle"] = true,
	["wh3_dlc27_hef_cha_sea_lord_aislinn"] = true,
	["wh3_dlc27_hef_cha_sea_lord_aislinn_dragon"] = true,
	["wh3_dlc27_hef_mon_merwyrm"] = true,
	["wh3_dlc27_hef_mon_merwyrm_ror"] = true,
	["wh3_dlc27_hef_mon_merwyrm_summoned"] = true,
	["wh3_dlc27_hef_mon_sea_elemental"] = true,
	["wh3_dlc27_lzd_mon_dread_saurian_boss"] = true,
	["wh3_dlc27_nor_cha_beorg_bearstruck"] = true,
	["wh3_dlc27_nor_cha_fimir_noble"] = true,
	["wh3_dlc27_nor_cha_great_shaman_sorcerer_death"] = true,
	["wh3_dlc27_nor_cha_great_shaman_sorcerer_death_mammoth"] = true,
	["wh3_dlc27_nor_cha_great_shaman_sorcerer_death_warhorse"] = true,
	["wh3_dlc27_nor_cha_great_shaman_sorcerer_fire"] = true,
	["wh3_dlc27_nor_cha_great_shaman_sorcerer_fire_mammoth"] = true,
	["wh3_dlc27_nor_cha_great_shaman_sorcerer_fire_warhorse"] = true,
	["wh3_dlc27_nor_cha_great_shaman_sorcerer_metal"] = true,
	["wh3_dlc27_nor_cha_great_shaman_sorcerer_metal_mammoth"] = true,
	["wh3_dlc27_nor_cha_great_shaman_sorcerer_metal_warhorse"] = true,
	["wh3_dlc27_nor_cha_sayl_the_faithless"] = true,
	["wh3_dlc27_nor_cha_sayl_the_faithless_mammoth"] = true,
	["wh3_dlc27_nor_cha_sayl_the_faithless_warhorse"] = true,
	["wh3_dlc27_nor_mon_chimera"] = true,
	["wh3_dlc27_nor_mon_chimera_boss"] = true,
	["wh3_dlc27_nor_mon_chimera_ror"] = true,
	["wh3_dlc27_nor_mon_cursd_ettin"] = true,
	["wh3_dlc27_nor_mon_cursd_ettin_runecaller"] = true,
	["wh3_dlc27_nor_mon_dread_maw"] = true,
	["wh3_dlc27_nor_mon_dread_maw_underground"] = true,
	["wh3_dlc27_nur_mon_toad_dragon_boss"] = true,
	["wh3_dlc27_sla_cha_alluress_shadow_daemonic_steed"] = true,
	["wh3_dlc27_sla_cha_alluress_slaanesh_daemonic_steed"] = true,
	["wh3_dlc27_sla_cha_dechala"] = true,
	["wh3_dlc27_sla_cha_druchii_anointed"] = true,
	["wh3_dlc27_sla_cha_druchii_anointed_cold_one"] = true,
	["wh3_dlc27_sla_cha_druchii_anointed_daemonic_steed"] = true,
	["wh3_dlc27_sla_cha_herald_of_slaanesh_shadow_daemonic_steed"] = true,
	["wh3_dlc27_sla_cha_herald_of_slaanesh_slaanesh_daemonic_steed"] = true,
	["wh3_dlc27_sla_cha_masque_of_slaanesh"] = true,
	["wh3_dlc27_sla_cha_styrkaar_the_sortsvinaer"] = true,
	["wh3_dlc27_sla_cha_styrkaar_the_sortsvinaer_daemonic_steed"] = true,
	["wh3_dlc27_sla_cha_styrkaar_the_sortsvinaer_steed_of_slaanesh"] = true,
	["wh3_dlc27_sla_mon_giant_spawn_of_sla_summoned_i"] = true,
	["wh3_dlc27_sla_mon_preyton"] = true,
	["wh3_dlc27_sla_mon_preyton_boss"] = true,
	["wh3_dlc27_sla_mon_preyton_ror"] = true,
	["wh3_dlc27_tmb_mon_carrion_boss"] = true,
	["wh3_dlc27_tze_mon_cockatrice_boss"] = true,
	["wh3_dlc29_chs_cha_bloab"] = true,
	["wh3_dlc29_chs_cha_bloab_bilespurter"] = true,
	["wh3_dlc29_chs_cha_gutrot_spume"] = true,
	["wh3_dlc29_chs_cha_gutrot_spume_warshrine"] = true,
	["wh3_dlc29_chs_cha_morbidex"] = true,
	["wh3_dlc29_chs_cha_morbidex_tripletongue"] = true,
	["wh3_dlc29_chs_cha_orghotts"] = true,
	["wh3_dlc29_chs_cha_orghotts_whippermaw"] = true,
	["wh3_dlc29_chs_cha_plagues_champion_mnur_summoned"] = true,
	["wh3_dlc29_chs_mon_basilisk"] = true,
	["wh3_dlc29_chs_mon_chaos_siege_giant"] = true,
	["wh3_dlc29_chs_mon_giant_spined_chaos_beast"] = true,
	["wh3_dlc29_chs_mon_giant_spined_chaos_beast_ror"] = true,
	["wh3_dlc29_cst_cha_gunnery_wight_0_summoned"] = true,
	["wh3_dlc29_cst_cha_vampire_fleet_admiral_female_undeath"] = true,
	["wh3_dlc29_cst_cha_vampire_fleet_admiral_female_undeath_rotting_promethean"] = true,
	["wh3_dlc29_cst_cha_vampire_fleet_admiral_undeath"] = true,
	["wh3_dlc29_cst_cha_vampire_fleet_admiral_undeath_rotting_promethean"] = true,
	["wh3_dlc29_cst_cha_vampire_fleet_captain_undeath"] = true,
	["wh3_dlc29_cst_cha_vampire_fleet_captain_undeath_rotting_promethean"] = true,
	["wh3_dlc29_emp_cha_boris_todbringer_toddy_0"] = true,
	["wh3_dlc29_emp_cha_boris_todbringer_toddy_1"] = true,
	["wh3_dlc29_emp_cha_boris_todbringer_toddy_2"] = true,
	["wh3_dlc29_emp_cha_boris_todbringer_toddy_3"] = true,
	["wh3_dlc29_emp_cha_emil_valgeir"] = true,
	["wh3_dlc29_emp_cha_emil_valgeir_warhorse"] = true,
	["wh3_dlc29_emp_cha_priest_of_ulric"] = true,
	["wh3_dlc29_emp_cha_priest_of_ulric_warhorse"] = true,
	["wh3_dlc29_emp_cha_seneschal_of_the_white_wolf"] = true,
	["wh3_dlc29_emp_cha_seneschal_of_the_white_wolf_warhorse"] = true,
	["wh3_dlc29_qb_brt_cha_lord_warhorse"] = true,
	["wh3_dlc29_skv_cha_lord_skrolk_cauldron"] = true,
	["wh3_dlc29_skv_cha_plague_priest_cauldron"] = true,
	["wh3_dlc29_skv_cha_skreech_verminking"] = true,
	["wh3_dlc29_skv_cha_thanquol"] = true,
	["wh3_dlc29_skv_cha_thanquol_boneripper_warpfire_braziers"] = true,
	["wh3_dlc29_skv_cha_thanquol_boneripper_warpfire_projectors"] = true,
	["wh3_dlc29_skv_cha_verminlord_corruptor"] = true,
	["wh3_dlc29_skv_cha_verminlord_deceiver"] = true,
	["wh3_dlc29_skv_cha_verminlord_warbringer"] = true,
	["wh3_dlc29_skv_cha_verminlord_warpseer"] = true,
	["wh3_dlc29_skv_mon_brood_horror_0_summoned"] = true,
	["wh3_dlc29_skv_veh_cauldron_of_a_thousand_poxes"] = true,
	["wh3_dlc29_tmb_cha_arkhan_dread_abyssal"] = true,
	["wh3_dlc29_tmb_cha_arkhan_the_black_mp"] = true,
	["wh3_dlc29_tmb_cha_arkhan_the_black_skeletal_steed_mp"] = true,
	["wh3_dlc29_tmb_cha_liche_high_priest_death"] = true,
	["wh3_dlc29_tmb_cha_liche_high_priest_death_skeletal_steed"] = true,
	["wh3_dlc29_tmb_cha_liche_high_priest_light"] = true,
	["wh3_dlc29_tmb_cha_liche_high_priest_light_skeletal_steed"] = true,
	["wh3_dlc29_tmb_cha_liche_high_priest_nehekhara"] = true,
	["wh3_dlc29_tmb_cha_liche_high_priest_nehekhara_skeletal_steed"] = true,
	["wh3_dlc29_tmb_cha_liche_high_priest_shadow"] = true,
	["wh3_dlc29_tmb_cha_liche_high_priest_shadow_skeletal_steed"] = true,
	["wh3_dlc29_tmb_cha_liche_high_priest_undeath"] = true,
	["wh3_dlc29_tmb_cha_liche_high_priest_undeath_skeletal_steed"] = true,
	["wh3_dlc29_tmb_cha_liche_priest_undeath"] = true,
	["wh3_dlc29_tmb_cha_liche_priest_undeath_skeletal_steed"] = true,
	["wh3_dlc29_tmb_cha_tomb_herald"] = true,
	["wh3_dlc29_tmb_cha_tomb_herald_skeletal_steed"] = true,
	["wh3_dlc29_tmb_cha_tomb_prince_0_summoned"] = true,
	["wh3_dlc29_tmb_mon_khemric_titan"] = true,
	["wh3_dlc29_tmb_mon_khemric_titan_ror"] = true,
	["wh3_dlc29_tmb_mon_khemric_titan_summoned"] = true,
	["wh3_dlc29_vmp_cha_dieter_helsnicht"] = true,
	["wh3_dlc29_vmp_cha_dieter_helsnicht_undead_manticore"] = true,
	["wh3_dlc29_vmp_cha_krell"] = true,
	["wh3_dlc29_vmp_cha_lahmian_vampire"] = true,
	["wh3_dlc29_vmp_cha_lahmian_vampire_barded_nightmare"] = true,
	["wh3_dlc29_vmp_cha_lahmian_vampire_hellsteed"] = true,
	["wh3_dlc29_vmp_cha_mannfred_von_carstein_barded_nightmare_mp"] = true,
	["wh3_dlc29_vmp_cha_mannfred_von_carstein_dread_abyssal"] = true,
	["wh3_dlc29_vmp_cha_mannfred_von_carstein_hellsteed_mp"] = true,
	["wh3_dlc29_vmp_cha_mannfred_von_carstein_mp"] = true,
	["wh3_dlc29_vmp_cha_mannfred_von_carstein_zombie_dragon_mp"] = true,
	["wh3_dlc29_vmp_cha_master_necromancer_undeath"] = true,
	["wh3_dlc29_vmp_cha_master_necromancer_undeath_barded_nightmare"] = true,
	["wh3_dlc29_vmp_cha_master_necromancer_undeath_corpse_cart"] = true,
	["wh3_dlc29_vmp_cha_master_necromancer_undeath_corpse_cart_balefire"] = true,
	["wh3_dlc29_vmp_cha_master_necromancer_undeath_corpse_cart_lodestone"] = true,
	["wh3_dlc29_vmp_cha_master_necromancer_undeath_hellsteed"] = true,
	["wh3_dlc29_vmp_cha_nagash"] = true,
	["wh3_dlc29_vmp_cha_nagash_vampire_lord"] = true,
	["wh3_dlc29_vmp_cha_nagash_vampire_lord_barded_nightmare"] = true,
	["wh3_dlc29_vmp_cha_nagash_vampire_lord_hellsteed"] = true,
	["wh3_dlc29_vmp_cha_nagash_vampire_lord_zombie_dragon"] = true,
	["wh3_dlc29_vmp_cha_necromancer_undeath"] = true,
	["wh3_dlc29_vmp_cha_necromancer_undeath_corpse_cart"] = true,
	["wh3_dlc29_vmp_cha_necromancer_undeath_corpse_cart_balefire"] = true,
	["wh3_dlc29_vmp_cha_necromancer_undeath_corpse_cart_lodestone"] = true,
	["wh3_dlc29_vmp_cha_necromancer_undeath_nightmare"] = true,
	["wh3_dlc29_vmp_cha_neferata"] = true,
	["wh3_dlc29_vmp_cha_neferata_barded_nightmare"] = true,
	["wh3_dlc29_vmp_cha_neferata_barded_nightmare_mp"] = true,
	["wh3_dlc29_vmp_cha_neferata_dread_abyssal"] = true,
	["wh3_dlc29_vmp_cha_neferata_hellsteed"] = true,
	["wh3_dlc29_vmp_cha_neferata_hellsteed_mp"] = true,
	["wh3_dlc29_vmp_cha_neferata_mp"] = true,
	["wh3_dlc29_vmp_cha_neferata_zombie_dragon"] = true,
	["wh3_dlc29_vmp_cha_neferata_zombie_dragon_mp"] = true,
	["wh3_dlc29_vmp_cha_walach_harkon"] = true,
	["wh3_dlc29_vmp_cha_walach_harkon_barded_nightmare"] = true,
	["wh3_dlc29_vmp_cha_wight_king_barded_nightmare_summoned"] = true,
	["wh3_dlc29_vmp_mon_terrorgheist_summoned"] = true,
	["wh3_dlc29_vmp_mon_zombie_dragon"] = true,
	["wh3_dlc29_vmp_mon_zombie_dragon_summoned"] = true,
	["wh3_main_cth_cha_alchemist_0"] = true,
	["wh3_main_cth_cha_alchemist_1"] = true,
	["wh3_main_cth_cha_astromancer_0"] = true,
	["wh3_main_cth_cha_astromancer_1"] = true,
	["wh3_main_cth_cha_astromancer_2"] = true,
	["wh3_main_cth_cha_dragon_blooded_shugengan_lord_yang_0"] = true,
	["wh3_main_cth_cha_dragon_blooded_shugengan_lord_yang_1"] = true,
	["wh3_main_cth_cha_dragon_blooded_shugengan_lord_yang_2"] = true,
	["wh3_main_cth_cha_dragon_blooded_shugengan_lord_yin_0"] = true,
	["wh3_main_cth_cha_dragon_blooded_shugengan_lord_yin_1"] = true,
	["wh3_main_cth_cha_dragon_blooded_shugengan_lord_yin_2"] = true,
	["wh3_main_cth_cha_iron_dragon_0"] = true,
	["wh3_main_cth_cha_iron_dragon_1"] = true,
	["wh3_main_cth_cha_lord_magistrate_0"] = true,
	["wh3_main_cth_cha_lord_magistrate_1"] = true,
	["wh3_main_cth_cha_storm_dragon_0"] = true,
	["wh3_main_cth_cha_storm_dragon_1"] = true,
	["wh3_main_cth_mon_terracotta_sentinel_0"] = true,
	["wh3_main_cth_veh_war_compass_0"] = true,
	["wh3_main_dae_cha_be_lakor_0"] = true,
	["wh3_main_dae_cha_daemon_prince_0"] = true,
	["wh3_main_dae_cha_daemon_prince_MP"] = true,
	["wh3_main_dae_cha_daemon_prince_khorne_0"] = true,
	["wh3_main_dae_cha_daemon_prince_khorne_MP"] = true,
	["wh3_main_dae_cha_daemon_prince_nurgle_0"] = true,
	["wh3_main_dae_cha_daemon_prince_nurgle_MP"] = true,
	["wh3_main_dae_cha_daemon_prince_slaanesh_0"] = true,
	["wh3_main_dae_cha_daemon_prince_slaanesh_MP"] = true,
	["wh3_main_dae_cha_daemon_prince_tzeentch_0"] = true,
	["wh3_main_dae_cha_daemon_prince_tzeentch_MP"] = true,
	["wh3_main_ie_nor_cha_exalted_great_unclean_one_burplesmirk_spewpit"] = true,
	["wh3_main_ie_nor_cha_exalted_hero_mkho_killgore_slaymaim"] = true,
	["wh3_main_kho_cha_bloodreaper_0"] = true,
	["wh3_main_kho_cha_bloodreaper_1"] = true,
	["wh3_main_kho_cha_bloodreaper_2"] = true,
	["wh3_main_kho_cha_cultist_0"] = true,
	["wh3_main_kho_cha_cultist_1"] = true,
	["wh3_main_kho_cha_exalted_bloodthirster_0"] = true,
	["wh3_main_kho_cha_herald_of_khorne_0"] = true,
	["wh3_main_kho_cha_herald_of_khorne_1"] = true,
	["wh3_main_kho_cha_herald_of_khorne_2"] = true,
	["wh3_main_kho_cha_skarbrand_0"] = true,
	["wh3_main_kho_mon_bloodthirster_0"] = true,
	["wh3_main_kho_mon_bloodthirster_summoned_0"] = true,
	["wh3_main_kho_mon_soul_grinder_0"] = true,
	["wh3_main_kho_veh_blood_shrine_0"] = true,
	["wh3_main_kho_veh_skullcannon_0"] = true,
	["wh3_main_ksl_cha_ataman"] = true,
	["wh3_main_ksl_cha_boris_0"] = true,
	["wh3_main_ksl_cha_boris_1"] = true,
	["wh3_main_ksl_cha_boris_2"] = true,
	["wh3_main_ksl_cha_boyar_0"] = true,
	["wh3_main_ksl_cha_boyar_1"] = true,
	["wh3_main_ksl_cha_boyar_2"] = true,
	["wh3_main_ksl_cha_frost_maiden_ice_0"] = true,
	["wh3_main_ksl_cha_frost_maiden_ice_1"] = true,
	["wh3_main_ksl_cha_frost_maiden_ice_2"] = true,
	["wh3_main_ksl_cha_frost_maiden_tempest_0"] = true,
	["wh3_main_ksl_cha_frost_maiden_tempest_1"] = true,
	["wh3_main_ksl_cha_frost_maiden_tempest_2"] = true,
	["wh3_main_ksl_cha_ice_witch_ice_0"] = true,
	["wh3_main_ksl_cha_ice_witch_ice_1"] = true,
	["wh3_main_ksl_cha_ice_witch_ice_2"] = true,
	["wh3_main_ksl_cha_ice_witch_tempest_0"] = true,
	["wh3_main_ksl_cha_ice_witch_tempest_1"] = true,
	["wh3_main_ksl_cha_ice_witch_tempest_2"] = true,
	["wh3_main_ksl_cha_katarin_0"] = true,
	["wh3_main_ksl_cha_katarin_1"] = true,
	["wh3_main_ksl_cha_katarin_2"] = true,
	["wh3_main_ksl_cha_kostaltyn_0"] = true,
	["wh3_main_ksl_cha_kostaltyn_1"] = true,
	["wh3_main_ksl_cha_kostaltyn_2"] = true,
	["wh3_main_ksl_cha_patriarch_0"] = true,
	["wh3_main_ksl_cha_patriarch_1"] = true,
	["wh3_main_ksl_cha_patriarch_2"] = true,
	["wh3_main_ksl_mon_elemental_bear_0"] = true,
	["wh3_main_ksl_mon_elemental_bear_summoned_0"] = true,
	["wh3_main_ksl_mon_snow_leopard_0"] = true,
	["wh3_main_ksl_mon_snow_leopard_summoned_0"] = true,
	["wh3_main_ksl_mon_snow_leopard_summoned_1"] = true,
	["wh3_main_ksl_mon_snow_leopard_summoned_2"] = true,
	["wh3_main_nur_cha_cultist_0"] = true,
	["wh3_main_nur_cha_cultist_1"] = true,
	["wh3_main_nur_cha_exalted_great_unclean_one_death_0"] = true,
	["wh3_main_nur_cha_exalted_great_unclean_one_nurgle_0"] = true,
	["wh3_main_nur_cha_herald_of_nurgle_death_0"] = true,
	["wh3_main_nur_cha_herald_of_nurgle_death_1"] = true,
	["wh3_main_nur_cha_herald_of_nurgle_death_2"] = true,
	["wh3_main_nur_cha_herald_of_nurgle_nurgle_0"] = true,
	["wh3_main_nur_cha_herald_of_nurgle_nurgle_1"] = true,
	["wh3_main_nur_cha_herald_of_nurgle_nurgle_2"] = true,
	["wh3_main_nur_cha_ku_gath_plaguefather_0"] = true,
	["wh3_main_nur_cha_plagueridden_death_0"] = true,
	["wh3_main_nur_cha_plagueridden_death_1"] = true,
	["wh3_main_nur_cha_plagueridden_death_2"] = true,
	["wh3_main_nur_cha_plagueridden_nurgle_0"] = true,
	["wh3_main_nur_cha_plagueridden_nurgle_1"] = true,
	["wh3_main_nur_cha_plagueridden_nurgle_2"] = true,
	["wh3_main_nur_mon_beast_of_nurgle_0"] = true,
	["wh3_main_nur_mon_great_unclean_one_0"] = true,
	["wh3_main_nur_mon_great_unclean_one_summoned_0"] = true,
	["wh3_main_nur_mon_soul_grinder_0"] = true,
	["wh3_main_ogr_cha_butcher_beasts_0"] = true,
	["wh3_main_ogr_cha_butcher_great_maw_0"] = true,
	["wh3_main_ogr_cha_firebelly_0"] = true,
	["wh3_main_ogr_cha_greasus_goldtooth_0"] = true,
	["wh3_main_ogr_cha_hunter_0"] = true,
	["wh3_main_ogr_cha_hunter_1"] = true,
	["wh3_main_ogr_cha_skrag_the_slaughterer_0"] = true,
	["wh3_main_ogr_cha_slaughtermaster_beasts_0"] = true,
	["wh3_main_ogr_cha_slaughtermaster_great_maw_0"] = true,
	["wh3_main_ogr_cha_tyrant_0"] = true,
	["wh3_main_ogr_feral_manticore_summoned"] = true,
	["wh3_main_ogr_mon_giant_0"] = true,
	["wh3_main_ogr_mon_stonehorn_0"] = true,
	["wh3_main_ogr_mon_stonehorn_1"] = true,
	["wh3_main_ogr_veh_gnoblar_scraplauncher_0"] = true,
	["wh3_main_ogr_veh_ironblaster_0"] = true,
	["wh3_main_pro_kho_cha_bloodreaper_0"] = true,
	["wh3_main_pro_kho_cha_bloodreaper_1"] = true,
	["wh3_main_pro_kho_cha_bloodreaper_2"] = true,
	["wh3_main_pro_kho_cha_cultist_0"] = true,
	["wh3_main_pro_kho_cha_cultist_1"] = true,
	["wh3_main_pro_kho_cha_herald_of_khorne_0"] = true,
	["wh3_main_pro_kho_cha_herald_of_khorne_1"] = true,
	["wh3_main_pro_kho_cha_herald_of_khorne_2"] = true,
	["wh3_main_pro_kho_inf_flesh_hounds_of_khorne_simaergul_0"] = true,
	["wh3_main_pro_ksl_cha_boyar_0"] = true,
	["wh3_main_pro_ksl_cha_boyar_1"] = true,
	["wh3_main_pro_ksl_cha_boyar_2"] = true,
	["wh3_main_pro_ksl_cha_frost_maiden_ice_0"] = true,
	["wh3_main_pro_ksl_cha_frost_maiden_ice_1"] = true,
	["wh3_main_pro_ksl_cha_frost_maiden_ice_2"] = true,
	["wh3_main_pro_ksl_cha_gerik_0"] = true,
	["wh3_main_pro_ksl_cha_patriarch_0"] = true,
	["wh3_main_pro_ksl_cha_patriarch_1"] = true,
	["wh3_main_pro_ksl_cha_patriarch_2"] = true,
	["wh3_main_pro_ksl_cha_sergi_0"] = true,
	["wh3_main_pro_ksl_cha_slavin_0"] = true,
	["wh3_main_pro_ksl_cha_yuri_0"] = true,
	["wh3_main_pro_ksl_cha_yuri_1"] = true,
	["wh3_main_pro_ksl_cha_yuri_2"] = true,
	["wh3_main_pro_ksl_cha_yuri_3"] = true,
	["wh3_main_pro_ksl_cha_yuri_4"] = true,
	["wh3_main_pro_ksl_cha_yuri_5"] = true,
	["wh3_main_pro_ksl_cha_yuri_5_brazen_altar"] = true,
	["wh3_main_pro_ksl_cha_yuri_5_howling_citadel"] = true,
	["wh3_main_pro_ksl_mon_elemental_bear_ror_0"] = true,
	["wh3_main_pro_tze_cha_cultist_0"] = true,
	["wh3_main_pro_tze_cha_cultist_1"] = true,
	["wh3_main_pro_tze_cha_herald_of_tzeentch_tzeentch_0"] = true,
	["wh3_main_pro_tze_cha_herald_of_tzeentch_tzeentch_1"] = true,
	["wh3_main_sla_cha_alluress_shadow_0"] = true,
	["wh3_main_sla_cha_alluress_shadow_1"] = true,
	["wh3_main_sla_cha_alluress_slaanesh_0"] = true,
	["wh3_main_sla_cha_alluress_slaanesh_1"] = true,
	["wh3_main_sla_cha_cultist_0"] = true,
	["wh3_main_sla_cha_cultist_1"] = true,
	["wh3_main_sla_cha_exalted_keeper_of_secrets_shadow_0"] = true,
	["wh3_main_sla_cha_exalted_keeper_of_secrets_slaanesh_0"] = true,
	["wh3_main_sla_cha_herald_of_slaanesh_shadow_0"] = true,
	["wh3_main_sla_cha_herald_of_slaanesh_shadow_1"] = true,
	["wh3_main_sla_cha_herald_of_slaanesh_slaanesh_0"] = true,
	["wh3_main_sla_cha_herald_of_slaanesh_slaanesh_1"] = true,
	["wh3_main_sla_cha_nkari_0"] = true,
	["wh3_main_sla_mon_keeper_of_secrets_0"] = true,
	["wh3_main_sla_mon_keeper_of_secrets_summoned_0"] = true,
	["wh3_main_sla_mon_soul_grinder_0"] = true,
	["wh3_main_tze_cha_cultist_0"] = true,
	["wh3_main_tze_cha_cultist_1"] = true,
	["wh3_main_tze_cha_exalted_lord_of_change_metal_0"] = true,
	["wh3_main_tze_cha_exalted_lord_of_change_tzeentch_0"] = true,
	["wh3_main_tze_cha_herald_of_tzeentch_metal_0"] = true,
	["wh3_main_tze_cha_herald_of_tzeentch_metal_1"] = true,
	["wh3_main_tze_cha_herald_of_tzeentch_tzeentch_0"] = true,
	["wh3_main_tze_cha_herald_of_tzeentch_tzeentch_1"] = true,
	["wh3_main_tze_cha_iridescent_horror_metal_0"] = true,
	["wh3_main_tze_cha_iridescent_horror_metal_1"] = true,
	["wh3_main_tze_cha_iridescent_horror_tzeentch_0"] = true,
	["wh3_main_tze_cha_iridescent_horror_tzeentch_1"] = true,
	["wh3_main_tze_cha_kairos_fateweaver_0"] = true,
	["wh3_main_tze_mon_exalted_flamer_0"] = true,
	["wh3_main_tze_mon_lord_of_change_0"] = true,
	["wh3_main_tze_mon_lord_of_change_summoned_0"] = true,
	["wh3_main_tze_mon_soul_grinder_0"] = true,
	["wh3_main_tze_veh_burning_chariot_0"] = true,
	["wh3_pro10_tze_cha_cultist_0"] = true,
	["wh3_pro10_tze_cha_daemon_prince_of_tzeentch"] = true,
	["wh3_pro11_chs_cha_harald_hammerstorm"] = true,
	["wh3_pro12_kho_cha_karanak"] = true,
	["wh3_prologue_test_general_0"] = true,
	["wh3_survival_dae_cha_be_lakor_01"] = true,
	["wh3_survival_dae_cha_be_lakor_02"] = true,
	["wh3_survival_kho_cha_bloodreaper"] = true,
	["wh3_survival_kho_cha_daemon_prince_of_khorne"] = true,
	["wh3_survival_kho_cha_exalted_bloodthirster"] = true,
	["wh3_survival_kho_cha_exalted_bloodthirster_0"] = true,
	["wh3_survival_nur_cha_daemon_prince_of_nurgle"] = true,
	["wh3_survival_nur_cha_exalted_great_unclean_one_nurgle"] = true,
	["wh3_survival_nur_cha_exalted_great_unclean_one_nurgle_01"] = true,
	["wh3_survival_nur_cha_plagueridden_death"] = true,
	["wh3_survival_sla_cha_daemon_prince_of_slaanesh"] = true,
	["wh3_survival_sla_cha_exalted_keeper_of_secrets_slaanesh"] = true,
	["wh3_survival_tze_cha_daemon_prince_of_tzeentch"] = true,
	["wh3_survival_tze_cha_exalted_lord_of_change_tzeentch"] = true,
	["wh3_survival_tze_cha_iridescent_horror_metal"] = true,
	["wh3_twa08_cth_mon_terracotta_sentinel_0_ror"] = true,
	["wh3_twa08_kho_mon_bloodthirster_0_ror"] = true,
	["wh3_twa08_ksl_mon_elemental_bear_0_ror"] = true,
	["wh3_twa08_nur_mon_great_unclean_one_0_ror"] = true,
	["wh3_twa08_ogr_mon_stonehorn_0_ror"] = true,
	["wh3_twa08_sla_mon_keeper_of_secrets_0_ror"] = true,
	["wh3_twa08_tze_mon_lord_of_change_0_ror"] = true,
	["wh_dlc01_chs_cha_chaos_lord_10"] = true,
	["wh_dlc01_chs_cha_chaos_lord_2"] = true,
	["wh_dlc01_chs_cha_chaos_sorcerer_lord_death_0"] = true,
	["wh_dlc01_chs_cha_chaos_sorcerer_lord_death_10"] = true,
	["wh_dlc01_chs_cha_chaos_sorcerer_lord_death_12"] = true,
	["wh_dlc01_chs_cha_chaos_sorcerer_lord_death_13"] = true,
	["wh_dlc01_chs_cha_chaos_sorcerer_lord_death_9"] = true,
	["wh_dlc01_chs_cha_chaos_sorcerer_lord_fire_0"] = true,
	["wh_dlc01_chs_cha_chaos_sorcerer_lord_fire_10"] = true,
	["wh_dlc01_chs_cha_chaos_sorcerer_lord_fire_12"] = true,
	["wh_dlc01_chs_cha_chaos_sorcerer_lord_fire_13"] = true,
	["wh_dlc01_chs_cha_chaos_sorcerer_lord_fire_9"] = true,
	["wh_dlc01_chs_cha_chaos_sorcerer_lord_metal_0"] = true,
	["wh_dlc01_chs_cha_chaos_sorcerer_lord_metal_10"] = true,
	["wh_dlc01_chs_cha_chaos_sorcerer_lord_metal_12"] = true,
	["wh_dlc01_chs_cha_chaos_sorcerer_lord_metal_13"] = true,
	["wh_dlc01_chs_cha_chaos_sorcerer_lord_metal_9"] = true,
	["wh_dlc01_chs_cha_chaos_sorcerer_lord_shadows_0"] = true,
	["wh_dlc01_chs_cha_chaos_sorcerer_lord_shadows_1"] = true,
	["wh_dlc01_chs_cha_chaos_sorcerer_lord_shadows_2"] = true,
	["wh_dlc01_chs_cha_chaos_sorcerer_lord_shadows_3"] = true,
	["wh_dlc01_chs_cha_chaos_sorcerer_lord_shadows_4"] = true,
	["wh_dlc01_chs_cha_chaos_sorcerer_shadows_0"] = true,
	["wh_dlc01_chs_cha_chaos_sorcerer_shadows_1"] = true,
	["wh_dlc01_chs_cha_chaos_sorcerer_shadows_2"] = true,
	["wh_dlc01_chs_cha_chaos_sorcerer_shadows_3"] = true,
	["wh_dlc01_chs_cha_exalted_hero_10"] = true,
	["wh_dlc01_chs_cha_kholek"] = true,
	["wh_dlc01_chs_cha_prince_sigvald_the_magnificent"] = true,
	["wh_dlc01_chs_cha_qb_lord_of_change_0"] = true,
	["wh_dlc01_chs_mon_dragon_ogre_shaggoth"] = true,
	["wh_dlc01_nor_cha_chaos_sorcerer_lord_0"] = true,
	["wh_dlc01_nor_cha_chaos_sorcerer_lord_1"] = true,
	["wh_dlc03_bst_cha_beastlord_0"] = true,
	["wh_dlc03_bst_cha_beastlord_0_qb"] = true,
	["wh_dlc03_bst_cha_bray_shaman_beasts_0"] = true,
	["wh_dlc03_bst_cha_bray_shaman_death_0"] = true,
	["wh_dlc03_bst_cha_bray_shaman_shadows_0"] = true,
	["wh_dlc03_bst_cha_bray_shaman_wild_0"] = true,
	["wh_dlc03_bst_cha_bray_shaman_wild_0_qb"] = true,
	["wh_dlc03_bst_cha_gorebull_0"] = true,
	["wh_dlc03_bst_cha_graktar_0"] = true,
	["wh_dlc03_bst_cha_khazrak_one_eye_0"] = true,
	["wh_dlc03_bst_cha_malagor_the_dark_omen_0"] = true,
	["wh_dlc03_bst_feral_manticore"] = true,
	["wh_dlc03_bst_inf_cygor_0"] = true,
	["wh_dlc03_bst_inf_cygor_0_summoned"] = true,
	["wh_dlc03_bst_mon_giant_0"] = true,
	["wh_dlc03_emp_cha_boris_todbringer_0"] = true,
	["wh_dlc03_emp_cha_boris_todbringer_1"] = true,
	["wh_dlc03_emp_cha_boris_todbringer_2"] = true,
	["wh_dlc03_emp_cha_boris_todbringer_3"] = true,
	["wh_dlc03_emp_cha_wizard_beasts_0"] = true,
	["wh_dlc03_emp_cha_wizard_beasts_1"] = true,
	["wh_dlc03_emp_cha_wizard_beasts_2"] = true,
	["wh_dlc03_emp_cha_wizard_beasts_3"] = true,
	["wh_dlc03_emp_cha_wizard_beasts_4"] = true,
	["wh_dlc04_emp_cha_arch_lector_0"] = true,
	["wh_dlc04_emp_cha_arch_lector_1"] = true,
	["wh_dlc04_emp_cha_arch_lector_2"] = true,
	["wh_dlc04_emp_cha_volkmar_the_grim_0"] = true,
	["wh_dlc04_emp_cha_volkmar_the_grim_2"] = true,
	["wh_dlc04_emp_cha_volkmar_the_grim_3"] = true,
	["wh_dlc04_vmp_cha_helman_ghorst_0"] = true,
	["wh_dlc04_vmp_cha_helman_ghorst_1"] = true,
	["wh_dlc04_vmp_cha_master_necromancer_1"] = true,
	["wh_dlc04_vmp_cha_master_necromancer_2"] = true,
	["wh_dlc04_vmp_cha_master_necromancer_3"] = true,
	["wh_dlc04_vmp_cha_necromancer_1"] = true,
	["wh_dlc04_vmp_cha_necromancer_2"] = true,
	["wh_dlc04_vmp_cha_necromancer_3"] = true,
	["wh_dlc04_vmp_cha_strigoi_ghoul_king_0"] = true,
	["wh_dlc04_vmp_cha_strigoi_ghoul_king_0_boss"] = true,
	["wh_dlc04_vmp_cha_strigoi_ghoul_king_1"] = true,
	["wh_dlc04_vmp_cha_vlad_von_carstein_0"] = true,
	["wh_dlc04_vmp_veh_corpse_cart_0"] = true,
	["wh_dlc04_vmp_veh_corpse_cart_1"] = true,
	["wh_dlc04_vmp_veh_corpse_cart_2"] = true,
	["wh_dlc05_bst_cha_morghur_0"] = true,
	["wh_dlc05_bst_cha_morghur_0_boss"] = true,
	["wh_dlc05_emp_cha_wizard_life_0"] = true,
	["wh_dlc05_emp_cha_wizard_life_1"] = true,
	["wh_dlc05_emp_cha_wizard_life_2"] = true,
	["wh_dlc05_emp_cha_wizard_life_3"] = true,
	["wh_dlc05_emp_cha_wizard_shadows_0"] = true,
	["wh_dlc05_emp_cha_wizard_shadows_1"] = true,
	["wh_dlc05_emp_cha_wizard_shadows_2"] = true,
	["wh_dlc05_emp_cha_wizard_shadows_3"] = true,
	["wh_dlc05_vmp_cha_red_duke_0"] = true,
	["wh_dlc05_vmp_cha_red_duke_1"] = true,
	["wh_dlc05_vmp_cha_red_duke_2"] = true,
	["wh_dlc05_vmp_cha_red_duke_3"] = true,
	["wh_dlc05_vmp_cha_vampire_shadows_0"] = true,
	["wh_dlc05_vmp_cha_vampire_shadows_1"] = true,
	["wh_dlc05_vmp_cha_vampire_shadows_2"] = true,
	["wh_dlc05_wef_cha_ancient_treeman_0"] = true,
	["wh_dlc05_wef_cha_branchwraith_0"] = true,
	["wh_dlc05_wef_cha_durthu_0"] = true,
	["wh_dlc05_wef_cha_female_glade_lord_0"] = true,
	["wh_dlc05_wef_cha_female_glade_lord_0_qb"] = true,
	["wh_dlc05_wef_cha_female_glade_lord_1"] = true,
	["wh_dlc05_wef_cha_female_glade_lord_2"] = true,
	["wh_dlc05_wef_cha_female_glade_lord_2_qb"] = true,
	["wh_dlc05_wef_cha_female_glade_lord_3"] = true,
	["wh_dlc05_wef_cha_glade_lord_0"] = true,
	["wh_dlc05_wef_cha_glade_lord_1"] = true,
	["wh_dlc05_wef_cha_glade_lord_2"] = true,
	["wh_dlc05_wef_cha_glade_lord_3"] = true,
	["wh_dlc05_wef_cha_orion_0"] = true,
	["wh_dlc05_wef_cha_spellsinger_beasts_0"] = true,
	["wh_dlc05_wef_cha_spellsinger_beasts_1"] = true,
	["wh_dlc05_wef_cha_spellsinger_beasts_2"] = true,
	["wh_dlc05_wef_cha_spellsinger_beasts_3"] = true,
	["wh_dlc05_wef_cha_spellsinger_life_0"] = true,
	["wh_dlc05_wef_cha_spellsinger_life_1"] = true,
	["wh_dlc05_wef_cha_spellsinger_life_2"] = true,
	["wh_dlc05_wef_cha_spellsinger_life_3"] = true,
	["wh_dlc05_wef_cha_spellsinger_shadows_0"] = true,
	["wh_dlc05_wef_cha_spellsinger_shadows_1"] = true,
	["wh_dlc05_wef_cha_spellsinger_shadows_2"] = true,
	["wh_dlc05_wef_cha_spellsinger_shadows_3"] = true,
	["wh_dlc05_wef_cha_waystalker_0"] = true,
	["wh_dlc05_wef_forest_dragon_0"] = true,
	["wh_dlc05_wef_mon_great_eagle_0"] = true,
	["wh_dlc05_wef_mon_treeman_0"] = true,
	["wh_dlc06_chs_cha_chaos_sorcerer_death_9"] = true,
	["wh_dlc06_chs_cha_chaos_sorcerer_fire_9"] = true,
	["wh_dlc06_chs_cha_chaos_sorcerer_metal_9"] = true,
	["wh_dlc06_chs_feral_manticore"] = true,
	["wh_dlc06_dwf_cha_belegar_ironhammer_0"] = true,
	["wh_dlc06_dwf_cha_master_engineer_ghost_0"] = true,
	["wh_dlc06_dwf_cha_runelord_0"] = true,
	["wh_dlc06_dwf_cha_runelord_1"] = true,
	["wh_dlc06_dwf_cha_runesmith_ghost_0"] = true,
	["wh_dlc06_dwf_cha_thane_ghost_0"] = true,
	["wh_dlc06_dwf_cha_thane_ghost_1"] = true,
	["wh_dlc06_emp_cha_arch_lector_0_boss"] = true,
	["wh_dlc06_emp_cha_captain_0_boss"] = true,
	["wh_dlc06_emp_cha_witch_hunter_boss"] = true,
	["wh_dlc06_grn_cha_night_goblin_warboss_0"] = true,
	["wh_dlc06_grn_cha_night_goblin_warboss_1"] = true,
	["wh_dlc06_grn_cha_skarsnik_0"] = true,
	["wh_dlc06_grn_cha_wurrzag_0"] = true,
	["wh_dlc06_grn_cha_wurrzag_1"] = true,
	["wh_dlc06_grn_inf_squig_explosive_0"] = true,
	["wh_dlc07_brt_cha_alberic_bordeleaux_0"] = true,
	["wh_dlc07_brt_cha_alberic_bordeleaux_1"] = true,
	["wh_dlc07_brt_cha_alberic_bordeleaux_2"] = true,
	["wh_dlc07_brt_cha_alberic_bordeleaux_3"] = true,
	["wh_dlc07_brt_cha_damsel_beasts_0"] = true,
	["wh_dlc07_brt_cha_damsel_beasts_1"] = true,
	["wh_dlc07_brt_cha_damsel_beasts_2"] = true,
	["wh_dlc07_brt_cha_damsel_beasts_3"] = true,
	["wh_dlc07_brt_cha_damsel_life_0"] = true,
	["wh_dlc07_brt_cha_damsel_life_1"] = true,
	["wh_dlc07_brt_cha_damsel_life_2"] = true,
	["wh_dlc07_brt_cha_damsel_life_3"] = true,
	["wh_dlc07_brt_cha_fay_enchantress_0"] = true,
	["wh_dlc07_brt_cha_fay_enchantress_1"] = true,
	["wh_dlc07_brt_cha_green_knight_0"] = true,
	["wh_dlc07_brt_cha_prophetess_0"] = true,
	["wh_dlc07_brt_cha_prophetess_1"] = true,
	["wh_dlc07_brt_cha_prophetess_2"] = true,
	["wh_dlc07_brt_cha_prophetess_3"] = true,
	["wh_dlc07_brt_cha_prophetess_beasts_0"] = true,
	["wh_dlc07_brt_cha_prophetess_beasts_1"] = true,
	["wh_dlc07_brt_cha_prophetess_beasts_2"] = true,
	["wh_dlc07_brt_cha_prophetess_beasts_3"] = true,
	["wh_dlc07_brt_cha_prophetess_heavens_0"] = true,
	["wh_dlc07_brt_cha_prophetess_heavens_1"] = true,
	["wh_dlc07_brt_cha_prophetess_heavens_2"] = true,
	["wh_dlc07_brt_cha_prophetess_heavens_3"] = true,
	["wh_dlc07_brt_inf_grail_reliquae_0"] = true,
	["wh_dlc08_bst_mon_cygor_boss"] = true,
	["wh_dlc08_chs_cha_chaos_lord_2_qb"] = true,
	["wh_dlc08_chs_mon_dragon_ogre_shaggoth_boss"] = true,
	["wh_dlc08_chs_mon_dragon_ogre_shaggoth_minor_boss"] = true,
	["wh_dlc08_grn_mon_giant_boss"] = true,
	["wh_dlc08_nor_cha_arzik_0"] = true,
	["wh_dlc08_nor_cha_fimir_balefiend_fire_0"] = true,
	["wh_dlc08_nor_cha_fimir_balefiend_shadow_0"] = true,
	["wh_dlc08_nor_cha_kihar_0"] = true,
	["wh_dlc08_nor_cha_shaman_sorcerer_death_0"] = true,
	["wh_dlc08_nor_cha_shaman_sorcerer_death_1"] = true,
	["wh_dlc08_nor_cha_shaman_sorcerer_fire_0"] = true,
	["wh_dlc08_nor_cha_shaman_sorcerer_fire_1"] = true,
	["wh_dlc08_nor_cha_shaman_sorcerer_metal_0"] = true,
	["wh_dlc08_nor_cha_shaman_sorcerer_metal_1"] = true,
	["wh_dlc08_nor_cha_skin_wolf_werekin_0"] = true,
	["wh_dlc08_nor_cha_throgg_0"] = true,
	["wh_dlc08_nor_cha_wulfrik_0"] = true,
	["wh_dlc08_nor_cha_wulfrik_1"] = true,
	["wh_dlc08_nor_cha_wulfrik_3"] = true,
	["wh_dlc08_nor_feral_manticore"] = true,
	["wh_dlc08_nor_mon_frost_wyrm_0"] = true,
	["wh_dlc08_nor_mon_frost_wyrm_boss"] = true,
	["wh_dlc08_nor_mon_frost_wyrm_ror_0"] = true,
	["wh_dlc08_nor_mon_norscan_giant_0"] = true,
	["wh_dlc08_nor_mon_war_mammoth_0"] = true,
	["wh_dlc08_nor_mon_war_mammoth_2"] = true,
	["wh_dlc08_vmp_mon_terrorgheist_boss"] = true,
	["wh_dlc08_wef_forest_dragon_boss"] = true,
	["wh_dlc08_wef_mon_treeman_boss"] = true,
	["wh_main_brt_cha_damsel_0"] = true,
	["wh_main_brt_cha_damsel_1"] = true,
	["wh_main_brt_cha_damsel_2"] = true,
	["wh_main_brt_cha_damsel_3"] = true,
	["wh_main_brt_cha_king_louen_leoncoeur_0"] = true,
	["wh_main_brt_cha_king_louen_leoncoeur_1"] = true,
	["wh_main_brt_cha_king_louen_leoncoeur_2"] = true,
	["wh_main_brt_cha_king_louen_leoncoeur_3"] = true,
	["wh_main_brt_cha_king_louen_leoncoeur_4"] = true,
	["wh_main_brt_cha_lord_0"] = true,
	["wh_main_brt_cha_lord_2"] = true,
	["wh_main_brt_cha_lord_3"] = true,
	["wh_main_brt_cha_lord_4"] = true,
	["wh_main_brt_cha_paladin_0"] = true,
	["wh_main_brt_cha_paladin_3"] = true,
	["wh_main_brt_cha_paladin_4"] = true,
	["wh_main_bst_feral_manticore_summoned"] = true,
	["wh_main_chs_cha_archaon_the_everchosen_0"] = true,
	["wh_main_chs_cha_archaon_the_everchosen_1"] = true,
	["wh_main_chs_cha_chaos_lord_0"] = true,
	["wh_main_chs_cha_chaos_lord_11"] = true,
	["wh_main_chs_cha_chaos_lord_12"] = true,
	["wh_main_chs_cha_chaos_sorcerer_death_0"] = true,
	["wh_main_chs_cha_chaos_sorcerer_death_10"] = true,
	["wh_main_chs_cha_chaos_sorcerer_death_11"] = true,
	["wh_main_chs_cha_chaos_sorcerer_fire_0"] = true,
	["wh_main_chs_cha_chaos_sorcerer_fire_10"] = true,
	["wh_main_chs_cha_chaos_sorcerer_fire_11"] = true,
	["wh_main_chs_cha_chaos_sorcerer_metal_0"] = true,
	["wh_main_chs_cha_chaos_sorcerer_metal_10"] = true,
	["wh_main_chs_cha_chaos_sorcerer_metal_11"] = true,
	["wh_main_chs_cha_exalted_hero_0"] = true,
	["wh_main_chs_cha_exalted_hero_12"] = true,
	["wh_main_chs_cha_exalted_hero_13"] = true,
	["wh_main_chs_cha_lord_of_change_0"] = true,
	["wh_main_chs_mon_giant"] = true,
	["wh_main_dwf_cha_high_king_thorgrim_grudgebearer_1"] = true,
	["wh_main_dwf_cha_lord_0"] = true,
	["wh_main_dwf_cha_master_engineer_0"] = true,
	["wh_main_dwf_cha_rune_smith_0"] = true,
	["wh_main_dwf_cha_thane"] = true,
	["wh_main_dwf_cha_ungrim_ironfist"] = true,
	["wh_main_emp_cha_balthasar_gelt_0"] = true,
	["wh_main_emp_cha_balthasar_gelt_1"] = true,
	["wh_main_emp_cha_balthasar_gelt_2"] = true,
	["wh_main_emp_cha_balthasar_gelt_3"] = true,
	["wh_main_emp_cha_captain_0"] = true,
	["wh_main_emp_cha_captain_1"] = true,
	["wh_main_emp_cha_captain_2"] = true,
	["wh_main_emp_cha_captain_3"] = true,
	["wh_main_emp_cha_general_0"] = true,
	["wh_main_emp_cha_general_1"] = true,
	["wh_main_emp_cha_general_2"] = true,
	["wh_main_emp_cha_general_3"] = true,
	["wh_main_emp_cha_general_4"] = true,
	["wh_main_emp_cha_karl_franz_0"] = true,
	["wh_main_emp_cha_karl_franz_1"] = true,
	["wh_main_emp_cha_karl_franz_2"] = true,
	["wh_main_emp_cha_karl_franz_3"] = true,
	["wh_main_emp_cha_karl_franz_4"] = true,
	["wh_main_emp_cha_warrior_priest_0"] = true,
	["wh_main_emp_cha_warrior_priest_1"] = true,
	["wh_main_emp_cha_warrior_priest_2"] = true,
	["wh_main_emp_cha_witch_hunter"] = true,
	["wh_main_emp_cha_wizard_fire_0"] = true,
	["wh_main_emp_cha_wizard_fire_1"] = true,
	["wh_main_emp_cha_wizard_fire_2"] = true,
	["wh_main_emp_cha_wizard_fire_3"] = true,
	["wh_main_emp_cha_wizard_heavens_0"] = true,
	["wh_main_emp_cha_wizard_heavens_1"] = true,
	["wh_main_emp_cha_wizard_heavens_2"] = true,
	["wh_main_emp_cha_wizard_heavens_4"] = true,
	["wh_main_emp_cha_wizard_light_0"] = true,
	["wh_main_emp_cha_wizard_light_1"] = true,
	["wh_main_emp_cha_wizard_light_2"] = true,
	["wh_main_emp_cha_wizard_light_4"] = true,
	["wh_main_grn_cha_azhag_the_slaughterer_0"] = true,
	["wh_main_grn_cha_azhag_the_slaughterer_1"] = true,
	["wh_main_grn_cha_goblin_big_boss_0"] = true,
	["wh_main_grn_cha_goblin_big_boss_1"] = true,
	["wh_main_grn_cha_goblin_big_boss_2"] = true,
	["wh_main_grn_cha_goblin_great_shaman_0"] = true,
	["wh_main_grn_cha_goblin_great_shaman_1"] = true,
	["wh_main_grn_cha_grimgor_ironhide"] = true,
	["wh_main_grn_cha_night_goblin_shaman"] = true,
	["wh_main_grn_cha_orc_shaman_0"] = true,
	["wh_main_grn_cha_orc_shaman_1"] = true,
	["wh_main_grn_cha_orc_warboss_0"] = true,
	["wh_main_grn_cha_orc_warboss_1"] = true,
	["wh_main_grn_cha_orc_warboss_2"] = true,
	["wh_main_grn_mon_giant"] = true,
	["wh_main_grn_mon_giant_qb_tall_roff"] = true,
	["wh_main_ksl_cha_captain_0"] = true,
	["wh_main_ksl_cha_captain_1"] = true,
	["wh_main_ksl_cha_captain_2"] = true,
	["wh_main_ksl_cha_general_0"] = true,
	["wh_main_ksl_cha_general_1"] = true,
	["wh_main_ksl_cha_general_2"] = true,
	["wh_main_ksl_cha_wizard_0"] = true,
	["wh_main_ksl_cha_wizard_1"] = true,
	["wh_main_nor_cha_chaos_sorcerer_0"] = true,
	["wh_main_nor_cha_chaos_sorcerer_1"] = true,
	["wh_main_nor_cha_marauder_chieftan_0"] = true,
	["wh_main_nor_cha_marauder_chieftan_1"] = true,
	["wh_main_nor_cha_marauder_chieftan_3"] = true,
	["wh_main_teb_cha_captain_0"] = true,
	["wh_main_teb_cha_captain_1"] = true,
	["wh_main_teb_cha_captain_2"] = true,
	["wh_main_teb_cha_general_0"] = true,
	["wh_main_teb_cha_general_1"] = true,
	["wh_main_teb_cha_general_2"] = true,
	["wh_main_teb_cha_wizard_0"] = true,
	["wh_main_teb_cha_wizard_1"] = true,
	["wh_main_vmp_cha_banshee"] = true,
	["wh_main_vmp_cha_heinrich_kemmler"] = true,
	["wh_main_vmp_cha_mannfred_von_carstein_0"] = true,
	["wh_main_vmp_cha_mannfred_von_carstein_2"] = true,
	["wh_main_vmp_cha_mannfred_von_carstein_3"] = true,
	["wh_main_vmp_cha_mannfred_von_carstein_4"] = true,
	["wh_main_vmp_cha_master_necromancer_0"] = true,
	["wh_main_vmp_cha_master_necromancer_4"] = true,
	["wh_main_vmp_cha_master_necromancer_5"] = true,
	["wh_main_vmp_cha_necromancer_0"] = true,
	["wh_main_vmp_cha_necromancer_5"] = true,
	["wh_main_vmp_cha_vampire_0"] = true,
	["wh_main_vmp_cha_vampire_1"] = true,
	["wh_main_vmp_cha_vampire_2"] = true,
	["wh_main_vmp_cha_vampire_lord_0"] = true,
	["wh_main_vmp_cha_vampire_lord_2"] = true,
	["wh_main_vmp_cha_vampire_lord_3"] = true,
	["wh_main_vmp_cha_vampire_lord_5"] = true,
	["wh_main_vmp_cha_wight_king_0"] = true,
	["wh_main_vmp_cha_wight_king_0_summoned"] = true,
	["wh_main_vmp_cha_wight_king_1"] = true,
	["wh_main_vmp_cha_wight_king_2"] = true,
	["wh_main_vmp_mon_terrorgheist"] = true,
	["wh_main_vmp_mon_terrorgheist_qb"] = true,
	["wh_main_vmp_mon_varghulf"] = true,
	["wh_main_vmp_veh_black_coach"] = true,
	["wh_pro01_dwf_cha_grombrindal_0"] = true,
	["wh_pro02_vmp_cha_isabella_von_carstein_0"] = true,
	["wh_pro02_vmp_cha_isabella_von_carstein_2"] = true,
	["wh_pro02_vmp_cha_isabella_von_carstein_4"] = true,
	["wh_pro03_vmp_cha_krell_0"] = true,
	["wh_pro03_vmp_cha_krell_campaign_0"] = true,
	["wh_pro03_vmp_cha_krell_campaign_1"] = true,
	["wh_pro03_vmp_cha_krell_campaign_2"] = true,
	["wh_pro03_vmp_cha_krell_campaign_3"] = true,
	["wh_pro03_vmp_cha_krell_campaign_4"] = true,
	["wh_pro04_bst_inf_cygor_ror_0"] = true,
	["wh_twa03_def_inf_squig_explosive_0"] = true,
}

-- true when the enemy fits the current entry's target class (nil class = any enemy)
function FOURTH.eg_class_ok(enemy)
	local cls = FOURTH.eg_class
	if cls == nil then return true end
	local t = FOURTH.type_plain(enemy)
	if cls == "commander" then
		if t ~= nil then return FOURTH.commander_keys[t] == true end
		local ok, c = pcall(function() return enemy:unit_class() end)
		return ok and c == "com"
	end
	-- ROUND 136: Spearfisher's Net (the game's flying_currently flag) - read live;
	-- only an exact false passes, an unreadable flight never qualifies
	if cls == "not_flying" then
		local ok_f, fly = pcall(function() return enemy:is_currently_flying() end)
		return ok_f and fly == false
	end
	if t == nil then return false end
	if cls == "large" then return FOURTH.class_keys.large[t] == true end
	if cls == "large_single" then
		return FOURTH.class_keys.large[t] == true and FOURTH.class_keys.single[t] == true
	end
	return false
end

-- gap, speed when the enemy is MOVING with a run speed of FAST_ENEMY_MPS or
-- more and one of our units (the caster counting) is within FAST_ENEMY_NEAR_M
-- of it (edge to edge, the closest of ours); nil otherwise. Every read
-- fails closed.
function FOURTH.fast_enemy_near(enemy, caster)
	local ok_mv, mv = pcall(function() return enemy:is_moving() end)
	if not (ok_mv and mv == true) then return nil end
	local ok_sp, sp = pcall(function() return enemy:fast_speed() end)
	if not (ok_sp and type(sp) == "number" and sp >= FOURTH.FAST_ENEMY_MPS) then return nil end
	local best = nil
	local function try(u)
		if u == nil then return end
		local ok_m, men = pcall(function() return u:number_of_men_alive() end)
		if not (ok_m and type(men) == "number" and men > 0) then return end
		local ok_g, g = pcall(function() return u:unit_distance(enemy) end)
		if ok_g and type(g) == "number" and g >= 0 and (best == nil or g < best) then best = g end
	end
	try(caster)
	if tracked_units ~= nil then
		for i = 1, #tracked_units do
			try(tracked_units[i] and tracked_units[i].unit)
		end
	end
	if best ~= nil and best <= FOURTH.FAST_ENEMY_NEAR_M then return best, sp end
	return nil
end

-- the user's fast-enemy trigger: the qualifying enemy closest to our units wins
function FOURTH.evaluate_enemy_fast_near_ally(unit, routing)
	FOURTH.eg_mode = "fast"
	if routing then return nil end
	local marker = FOURTH.eg_marker or "fast_enemy"
	local ok_coll, coll = pcall(function() return bm:get_scriptunits_for_main_enemy_army_to_local_player() end)
	if not ok_coll or coll == nil then return nil end
	local ok_n, n = pcall(function() return coll:count() end)
	if not ok_n or type(n) ~= "number" then return nil end
	local best, best_near, best_sp = nil, nil, nil
	for i = 1, n do
		local ok_su, su = pcall(function() return coll:item(i) end)
		local enemy = nil
		if ok_su and su ~= nil then pcall(function() enemy = su.unit end) end
		if enemy ~= nil then
			local ok_alive, alive = pcall(function() return enemy:number_of_men_alive() end)
			local valid = FOURTH.eg_enemy_valid(enemy)
			if ok_alive and type(alive) == "number" and alive > 0 and (valid == nil or valid == true)
				and FOURTH.eg_class_ok(enemy) and FOURTH.eg_enemy_within_bound(unit, enemy) then
				local near, sp = FOURTH.fast_enemy_near(enemy, unit)
				if near ~= nil and (best_near == nil or near < best_near) then
					best, best_near, best_sp = enemy, near, sp
				end
			end
		end
	end
	if best == nil then return nil end
	local etype = "enemy"
	pcall(function() etype = tostring(best:type()) end)
	local gap = FOURTH.eg_enemy_gap(unit, best)
	FOURTH.eg_enemy = best
	FOURTH.eg_arm = "fast"
	FOURTH.eg_caster_su = FOURTH.eg_fresh_caster_su(unit)
	FOURTH.cast_target = best
	return string.format("fast enemy near our units (targeting %s, run speed %.1f m/s >= %d, %.1fm from our closest unit <= %dm, distance %sm bound %sm)",
		etype, best_sp, FOURTH.FAST_ENEMY_MPS, best_near, FOURTH.FAST_ENEMY_NEAR_M,
		(gap ~= nil) and string.format("%.1f", gap) or "?", tostring(FOURTH.eg_range_m))
end

-- ============================================================================
-- ROUND 137 - AUDIT BATCH 6: MORALE (user rulings 2026-11-09).
--   wavering_aura (NEW): the caster is wavering, or a friendly unit inside the
--     aura's 70% bound is wavering (aura_real -1 = the whole army; no aura_real
--     = the caster only); cast on the caster. The morale read is FOURTH.wavering
--     (is_wavering()); only an exact true counts, so an unreadable morale never
--     fires. A routing ally is not counted (its morale is already gone).
--   wavering_ally_range gains Crown of Command, Doom Lord, Cold-Blooded,
--     Pilgrimage of Skulls and Tacticians, Rally! (cast on the wavering ally).
-- ============================================================================

-- the closest OTHER friendly unit (alive, not routing) that is wavering and lies
-- inside the current entry's aura bound; a negative bound = the whole army; nil
-- bound = nobody (a self-only effect). An unreadable distance counts only for
-- the whole-army aura.
function FOURTH.wavering_ally_in_aura(unit)
	local bound = FOURTH.fa_bound_m
	if bound == nil or tracked_units == nil then return nil, nil end
	local self_id = tostring(unit:unique_ui_id())
	local best, best_gap = nil, nil
	for i = 1, #tracked_units do
		local other = tracked_units[i] and tracked_units[i].unit
		if other ~= nil and other ~= unit then
			local ok_m, men = pcall(function() return other:number_of_men_alive() end)
			local ok_i, oid = pcall(function() return tostring(other:unique_ui_id()) end)
			if ok_m and type(men) == "number" and men > 0 and ok_i and oid ~= self_id
				and not unit_is_routing(other) and FOURTH.wavering(other) == true then
				local gap = FOURTH.ab_ally_gap(unit, other)
				if bound < 0 and gap == nil then gap = 0 end
				if gap ~= nil and (bound < 0 or gap <= bound) and (best_gap == nil or gap < best_gap) then
					best, best_gap = other, gap
				end
			end
		end
	end
	return best, best_gap
end

function FOURTH.evaluate_wavering_aura(unit, routing)
	if routing then return nil end
	if FOURTH.wavering(unit) == true then
		return "wavering aura: the caster is wavering, cast centred on the caster"
	end
	local ally, gap = FOURTH.wavering_ally_in_aura(unit)
	if ally == nil then return nil end
	local atype = "ally"
	pcall(function() atype = tostring(ally:type()) end)
	if FOURTH.fa_bound_m < 0 then
		return "wavering aura: a friendly unit (" .. atype .. ") is wavering, the whole army is covered - cast centred on the caster"
	end
	return string.format("wavering aura: a friendly unit (%s) %.1fm away is wavering (bound %dm), cast centred on the caster",
		atype, gap, FOURTH.fa_bound_m)
end

FOURTH.evaluators = {
	charge = FOURTH.evaluate_charge,
	tired = FOURTH.evaluate_tired,
	melee = FOURTH.evaluate_melee,
	melee_low_morale = FOURTH.evaluate_melee_low_morale,
	melee_unwavering = FOURTH.evaluate_in_melee_self,
	-- BLOCK 2 (this round): the four new triggers, each its own evaluator.
	barrier_broken = FOURTH.evaluate_barrier_broken,
	charge_or_melee = FOURTH.evaluate_charge_or_melee,
	ushoran_health = FOURTH.evaluate_ushoran_health,
	-- THE ALLY-AWARE HEALTH FAMILY (this round): the same 75% line, but the
	-- trigger is "this unit OR a friendly unit in reach", and the cast target
	-- follows the ability's own targeting data (ground under the ally / the ally
	-- itself / the caster for a self-centred aura).
	health_aura_ground = FOURTH.evaluate_health_aura_ground,
	health_aura_ally = FOURTH.evaluate_health_aura_ally,
	health_aura_self = FOURTH.evaluate_health_aura_self,
	glorious_death = FOURTH.evaluate_glorious_death,
	-- BLOCK 4/5/6 (this round): the two new triggers, each its own evaluator.
	verminking_wavering = FOURTH.evaluate_verminking_wavering,
	melee_health75 = FOURTH.evaluate_potion_health,
	-- ROUND h89 (this round): the Enchanted Metallurgy family - one new trigger.
	metallurgy_melee = FOURTH.evaluate_metallurgy_melee,
	-- BLOCKS 7-9 (this round): five new triggers, each its own evaluator.
	charge_only = FOURTH.evaluate_charge_only,
	wavering_self = FOURTH.evaluate_wavering_self,
	wavering_self_or_ally = FOURTH.evaluate_wavering_self_or_ally,
	charge_or_wavering = FOURTH.evaluate_charge_or_wavering,
	wavering_ally_range = FOURTH.evaluate_wavering_ally_range,
	-- THE FINAL ROSTER ROUND (this round): the two ally-heal triggers.
	blood_sacrifice = FOURTH.evaluate_blood_sacrifice,
	eat_da_runts = FOURTH.evaluate_eat_da_runts,
	-- ACCUSATION (this round): the FIRST ENEMY-TARGETED trigger.
	enemy_engaged_or_shot = FOURTH.evaluate_enemy_engaged_or_shot,
	-- ROUND 123: an enemy in range that is IN MELEE (no missile arm).
	enemy_melee = FOURTH.evaluate_enemy_melee,
	-- CLASS A (harness 97): the rest of the enemy-aimed casts - the unit form
	-- (shared with Accusation) and the enemy-GROUND area form.
	enemy_ground_area = FOURTH.evaluate_enemy_ground_area,
	-- GATE OF KHORNE (harness 101): closest FIGHTING enemy, summon on its ground.
	enemy_ground_melee = FOURTH.evaluate_enemy_ground_melee,
	-- THE SUMMON ROUND (harness 102): the self-summon and the two
	-- non-commander enemy triggers, each its own evaluator.
	self_summon_melee = FOURTH.evaluate_self_summon_melee,
	-- TZ'ARKAN (this round): the low-health self transform.
	health_below_15 = FOURTH.evaluate_tzarkan_low_health,
	enemy_low_health_noncommander = FOURTH.evaluate_enemy_low_health_noncommander,
	enemy_melee_noncommander = FOURTH.evaluate_enemy_melee_noncommander,
	-- CLASS B (harness 98): the four ally-targeted families.
	ally_heal = FOURTH.evaluate_ally_heal,
	ally_heal_melee = FOURTH.evaluate_ally_heal_melee,
	ally_wavering = FOURTH.evaluate_ally_wavering,
	ally_melee_buff = FOURTH.evaluate_ally_melee_buff,
	-- THE TARGET-CLASS GATED FAMILIES (harness 99) + the unbounded / winds forms.
	ally_overseer = FOURTH.evaluate_ally_overseer,
	ally_beast = FOURTH.evaluate_ally_beast,
	ally_broken = FOURTH.evaluate_ally_broken,
	ally_missile = FOURTH.evaluate_ally_missile,
	-- ROUND 130: the firing-flag triggers.
	ally_ammo_low = FOURTH.evaluate_ally_ammo_low,
	allies_firing_aura = FOURTH.evaluate_allies_firing_aura,
	melee_or_shooting_into_melee = FOURTH.evaluate_melee_or_shooting_into_melee,
	-- ROUND 131
	self_or_ally_shooting = FOURTH.evaluate_self_or_ally_shooting,
	melee_or_self_or_ally_shooting = FOURTH.evaluate_melee_or_self_or_ally_shooting,
	no_enemy_in_range_within_boost = FOURTH.evaluate_no_enemy_in_range_within_boost,
	-- ROUND 132
	melee_or_shooting_aura = FOURTH.evaluate_melee_or_shooting_aura,
	melee_or_shooting_self_or_ally = FOURTH.evaluate_melee_or_shooting_self_or_ally,
	self_shooting = FOURTH.evaluate_self_shooting,
	-- ROUND 133
	under_fire = FOURTH.evaluate_under_fire,
	melee_or_under_fire = FOURTH.evaluate_melee_or_under_fire,
	-- ROUND 135
	enemy_fast_near_ally = FOURTH.evaluate_enemy_fast_near_ally,
	-- ROUND 137
	wavering_aura = FOURTH.evaluate_wavering_aura,
	ally_warmachine_heal = FOURTH.evaluate_ally_warmachine_heal,
	ally_hellforged_heal = FOURTH.evaluate_ally_hellforged_heal,
	ally_monster_heal = FOURTH.evaluate_ally_monster_heal,
	ally_construct_heal = FOURTH.evaluate_ally_construct_heal,
	ally_infinite_buff = FOURTH.evaluate_ally_infinite_buff,
	ally_winds = FOURTH.evaluate_ally_winds,
	-- ROUND 106: the two bombardment families.
	melee_skip_commanders = FOURTH.evaluate_melee_skip_commanders,
	-- ROUND 107: the "on top of" family - one evaluator, 12 entries.
	air_drop_on_infantry = FOURTH.evaluate_air_drop_on_infantry,
	enemy_ground_melee_infantry = FOURTH.evaluate_enemy_ground_melee_infantry,
}

-- THE TOOLTIP LINE (this round): the short sentence the mod appends to an
-- implemented ability's tooltip - ONE clause describing the TRIGGER that the
-- entry actually rides. It is composed at load from the entry's own trigger
-- field (never written per ability by hand), so every entry's line names the
-- evaluator that entry really calls. The old one-size generic line ("this
-- ability fires by itself while the unit charges ...") is REMOVED: it
-- described a charge behaviour most abilities do not have.
FOURTH.TRIGGER_TIP = {
	-- the legacy Deadly Onslaught family: the charge window OR already in melee
	charge = "When armed, fires when this unit charges or is in melee",
	tired = "When armed, fires when this unit is tired or worse",
	melee = "When armed, fires when this unit is in melee",
	melee_low_morale = "When armed, fires when this unit is in melee and wavering",
	melee_unwavering = "When armed, fires when this unit is in melee",
	barrier_broken = "When armed, fires when this unit's barrier breaks",
	charge_or_melee = "When armed, fires when this unit charges or is in melee",
	ushoran_health = "When armed, fires when this unit is at or below 75% health",
	-- THE ALLY-AWARE HEALTH FAMILY (this round) - three sentences, because the
	-- CAST TARGET differs per shape and each sentence must be true for its entry.
	health_aura_ground = "When armed, fires when this unit or a friendly unit in its area is at or below 75% health, placed on the ground under it",
	health_aura_ally = "When armed, fires when this unit or a friendly unit in range is at or below 75% health, cast on it",
	health_aura_self = "When armed, fires when this unit or a friendly unit in its aura is at or below 75% health, cast on itself",
	glorious_death = "When armed, fires when a Slayer ally in range is in melee",
	verminking_wavering = "When armed, fires when an ally in range is wavering",
	melee_health75 = "When armed, fires when this unit is in melee and at or below 75% health",
	metallurgy_melee = "When armed, fires when this unit or an ally in range is in melee",
	charge_only = "When armed, fires when this unit charges",
	wavering_self = "When armed, fires when this unit is wavering",
	wavering_self_or_ally = "When armed, fires when this unit or an ally in range is wavering",
	charge_or_wavering = "When armed, fires when this unit charges or is wavering",
	wavering_ally_range = "When armed, fires when an ally in range is wavering",
	blood_sacrifice = "When armed, fires on the lowest-health ally in range when it is at or below 75% health",
	eat_da_runts = "When armed, fires when this unit is at or below 75% health, otherwise on the lowest-health ally in range",
	enemy_engaged_or_shot = "When armed, fires when an enemy unit in range is in melee or under missile fire",
	enemy_melee = "When armed, fires on the closest enemy unit in range that is fighting in melee",
	enemy_ground_area = "When armed, fires when an enemy in range is in melee or under missile fire and the area hex is placed on its ground",
	enemy_ground_melee = "When armed, fires when an enemy in range is fighting in melee and the summon is placed on its ground",
	self_summon_melee = "When armed, fires when this unit itself is fighting in melee and the summon is cast on it",
	health_below_15 = "When armed, fires when this unit is below 15% health",
	enemy_low_health_noncommander = "When armed, fires on the lowest-health enemy in range that is below 20% health and is not a Lord or Hero",
	enemy_melee_noncommander = "When armed, fires on the closest enemy in range that is fighting in melee and is not a Lord or Hero",
	ally_heal = "When armed, fires on the lowest-health ally in range when it is at or below 75% health",
	ally_heal_melee = "When armed, fires when this unit is in melee, on the lowest-health ally in range at or below 75% health",
	ally_wavering = "When armed, fires on a wavering ally in range",
	ally_melee_buff = "When armed, fires when this unit is in melee, on an ally in range",
	ally_overseer = "When armed, fires on a non-commander, non-large ally in range",
	ally_beast = "When armed, fires on a beast ally in range",
	ally_broken = "When armed, fires on a broken-morale ally in range",
	ally_missile = "When armed, fires on a missile-capable ally in range",
	ally_ammo_low = "When armed, fires on a shooting ally in range with 70% or less of its ammunition left (the lowest first)",
	allies_firing_aura = "When armed, fires when this unit or a friendly unit near it is shooting",
	self_or_ally_shooting = "When armed, fires on this unit when it is shooting, otherwise on the closest friendly unit in range that is shooting",
	melee_or_self_or_ally_shooting = "When armed, fires on this unit in melee or when it is shooting, otherwise on the closest friendly unit in range that is shooting",
	no_enemy_in_range_within_boost = "When armed, fires when no enemy is in this unit's missile range but one is just beyond it",
	melee_or_shooting_aura = "When armed, fires when this unit or a friendly unit near it is in melee or shooting",
	melee_or_shooting_self_or_ally = "When armed, fires on this unit when it is in melee or shooting, otherwise on the closest friendly unit in range that is",
	self_shooting = "When armed, fires when this unit is shooting",
	under_fire = "When armed, fires when this unit (or, for an aura, a friendly unit near it) is under missile fire",
	melee_or_under_fire = "When armed, fires when this unit (or, for an aura, a friendly unit near it) is in melee or under missile fire",
	enemy_fast_near_ally = "When armed, fires on a fast enemy unit moving close to your units",
	wavering_aura = "When armed, fires when this unit or a friendly unit near it is wavering",
	melee_or_shooting_into_melee = "When armed, fires when this unit is in melee, or is shooting at an enemy that is in melee",
	ally_warmachine_heal = "When armed, fires on the lowest-health war machine ally in range that is at or below 75% health",
	ally_hellforged_heal = "When armed, fires on the lowest-health Hell-Forged ally in range that is at or below 75% health",
	ally_monster_heal = "When armed, fires on the lowest-health monster ally in range that is at or below 75% health",
	ally_construct_heal = "When armed, fires on the lowest-health construct ally in range that is at or below 75% health",
	ally_infinite_buff = "When armed, fires on an ally anywhere on the field (infinite range), cast on that ally",
	ally_winds = "When armed, fires on the ally with the most hit points remaining, cast on that ally",
	melee_skip_commanders = "When armed, fires when this unit is in melee, unless every enemy it is fighting is a Lord or Hero",
	enemy_ground_melee_infantry = "When armed, fires on the closest infantry unit in range that is fighting in melee",
	air_drop_on_infantry = "When armed, fires when the nearest enemy unit with more than 10 models comes within 6 m of this unit's centre, and casts immediately on that evaluation - no delay at all - airborne where the ability requires it",
}
for _, ability in ipairs(ABILITIES) do
	ability.evaluate = FOURTH.evaluators[ability.trigger]
	ability.tip = FOURTH.TRIGGER_TIP[ability.trigger]
	-- CLASS A (harness 97): an entry's REAL target_intercept_range (range_real)
	-- maps to its own named 70% bound (FOURTH.ENEMY_CAST). Entries without it
	-- (the self/ally triggers) leave range_m nil - never read for them.
	if ability.range_real ~= nil then
		ability.range_m = FOURTH.ENEMY_CAST[ability.range_real]
	end
	-- ROUND 114: the air-drop family is bounded by its OWN rule, not by the 70%
	-- table. The rule is ONE comparison - the nearest valid enemy's CENTRE gap
	-- against FOURTH.AIR_DROP_CENTER_M (round 117; it was the edge gap) - so the
	-- entry's range_m is carried for the inventory/diagnostics only and set to
	-- that same line; the evaluator never reads it. The 70% map would otherwise
	-- stamp the row's 10 m range onto it as 7 m, which is not the test any more.
	if ability.evaluate == FOURTH.evaluate_air_drop_on_infantry then
		ability.range_m = FOURTH.AIR_DROP_CENTER_M
		FOURTH.ad_fast_abilities[#FOURTH.ad_fast_abilities + 1] = ability
	end
	-- CLASS B (harness 98): an ally-targeted entry's REAL target_intercept_range
	-- (ally_range_real) maps to its own named 70% ALLY bound (FOURTH.ALLY_CAST).
	if ability.ally_range_real ~= nil then
		ability.range_m = FOURTH.ALLY_CAST[ability.ally_range_real]
	end
	-- THE CHARGE GATE (this round): a multi-USE ability carries its own
	-- recharge_time (seconds, from unit_spec_abil.tsv) here; the poll
	-- holds the pair for exactly that long after a successful cast.
	-- Single-use entries leave charge_s nil - the engine refuses those
	-- by itself on the next attempt.
	for _, key in ipairs(ability.keys) do
		local hold = charge_gate.hold_s[key]
		if hold ~= nil and (ability.charge_s == nil or hold > ability.charge_s) then
			ability.charge_s = hold
		end
	end
	-- THE IN-FLIGHT GATE (this round): the wind-up the game's own row declares
	-- for this entry's key(s), in seconds. nil for an entry with no wind-up in
	-- any of its rows - such an entry keeps the plain 2 s guard, because it has
	-- no activation window to protect.
	for _, key in ipairs(ability.keys) do
		local wu = cast_gate.wind_up_s[key]
		if wu ~= nil and (ability.wind_up_s == nil or wu > ability.wind_up_s) then
			ability.wind_up_s = wu
		end
	end
	-- THE AURA BOUND (this round): an entry whose trigger is an area heal
	-- carries the ability's REAL effect radius (aura_real, metres from
	-- unit_spec_abil.tsv `effect_range`) and gets the standing 70% bound
	-- computed here - floor(real * FOURTH.RANGE_FRACTION) - so no named
	-- constant is invented for 15/35/55 m.
	if ability.aura_real ~= nil then
		ability.aura_m = math.floor(ability.aura_real * FOURTH.RANGE_FRACTION + 1e-9)
	end
end


-- ============================================================================
-- 8. THE POLL - runs every POLL_MS milliseconds for the whole battle
-- ============================================================================

-- THE ONE DROP ROUTINE (drop_unit_by_ui_id) lives in section 6, above the
-- watch-list builder, because BOTH drop paths call it - the re-list's own drop
-- there, and the poll's dead-unit path just below. It purges the unit's rows
-- from every per-unit table and settles the selected set (items 2 + 13); its
-- full note sits with its definition.

-- ROUND 114: ONE COPY of the readiness read + every gate + the cast, shared by
-- the poll and the air-drop fast pass. It answers "gone" when the unit has
-- to be dropped after this tick's walk, nil otherwise. Nothing in it changed
-- in round 114 - it was MOVED here verbatim so the fast pass could not fork it.
-- ============================================================================
-- ROUND 128 - A DROPPED MULTI-USE CAST, SEEN ON SCREEN (user ruling 2026-11-03:
-- "implement only A ... in general"). The engine can ACCEPT a cast of a
-- multi-use ability and never execute it (Isha's Rain, field battle 2026-11-03:
-- the third cast left the button READY 32 s later). can_perform_special_ability
-- stays true for such an ability, so the charge hold below cannot tell. The one
-- honest signal is the ability's own button - and it exists only for the
-- SELECTED unit. So: while a charge hold runs, if this unit is the ONLY unit the
-- engine reports selected,
-- at least the wind-up + CHARGE_RELEASE_SETTLE_S after the cast, and the button
-- reads 'active' or 'hover' (ready), the cast did not take: release the hold.
-- Returns ready (bool), the state read, and the seconds since the cast.
-- ============================================================================
FOURTH.CHARGE_RELEASE_SETTLE_S = 3   -- seconds after the wind-up before a READY button is believed
function FOURTH.charge_hold_ready_on_screen(ui_id, ability, held_until)
	-- the ENGINE's live selection (not the tracker, which keeps the last unit when
	-- nothing is selected): exactly one unit selected, and it is this one
	if #selected_ui_ids ~= 1 or tostring(selected_ui_ids[1]) ~= tostring(ui_id) then return false end
	if ability.charge_s == nil or held_until == nil then return false end
	local cast_tick = held_until - math.floor((ability.charge_s * 1000) / POLL_MS)
	local since_s = (tick_count - cast_tick) * POLL_MS / 1000
	if since_s < (ability.wind_up_s or 0) + FOURTH.CHARGE_RELEASE_SETTLE_S then return false end
	local st = ability_state[ability.marker]
	if st == nil or st.button == nil then return false end
	local ok, s = pcall(function() return st.button:CurrentState() end)
	if not ok or type(s) ~= "string" then return false end
	return (s == "active" or s == "hover"), s, since_s
end

function FOURTH.try_pair(script_unit, unit, ability, ui_id, ability_key, reason, gone_ids)
		-- The readiness gate: the engine's own check.
		-- One query, on the key this unit was found to
		-- own (section 2); the variant list is walked
		-- only when no usable key is cached, and the
		-- answer is logged on this evaluation.
		local ready_key, readiness = check_readiness(unit, ability, ability_key)

		-- THE COOLDOWN-HOLD GATE (this round): a pair the
		-- engine already refused ON COOLDOWN is governed by
		-- its own record - the next_at back-off (a longer
		-- back-off after a repeat) plus the hard bound -
		-- instead of the raw guard, and a pair that has
		-- already spoken this episode is probed SILENTLY.
		local bucket = cooldown_hold[ui_id]
		local hold = (bucket ~= nil and bucket[ability.marker]) or nil

		-- The readiness query ALWAYS runs (the gate is
		-- untouched), but its per-tick whisper does not repeat
		-- while the pair sits in an already-spoken hold: the
		-- answer has not changed, so repeating it is noise.
		if hold == nil or hold.logged ~= true then
			log("  readiness " .. ability.marker .. " on ui id " .. tostring(ui_id)
				.. ": " .. readiness)
		end

		if ready_key ~= nil then
			local eligible, quiet
			if hold ~= nil then
				-- THE HARD BOUND: however the hold was set, it
				-- may never outlive MAX_HOLD_SECONDS. When it
				-- fires the bound re-bases, so an unreadable or
				-- stuck signal still gets probed - and, if the
				-- engine then allows it, still fires.
				if (tick_count - hold.since) >= MAX_HOLD_TICKS then
					hold.since = tick_count
					hold.next_at = 0
				end
				eligible = (tick_count >= hold.next_at)
				quiet = (hold.logged == true)
			else
				local guard = last_attempt_at[ui_id]
				local last_attempt = (guard ~= nil and guard[ability.marker]) or -999999
				eligible = (tick_count - last_attempt) >= GUARD_TICKS
				quiet = false
			end

			-- THE CHARGE GATE (this round): a multi-USE ability
			-- (num_uses > 1) answers can_perform = TRUE while its
			-- pool is EMPTY and still ACCEPTS the call - 55
			-- accepted casts of Nurgling Tide's 3 uses in 108 s
			-- in the field log, with its button greyed the whole
			-- time. So the 2 s guard would re-spend the same pool
			-- forever. After a successful cast the pair is held
			-- for the ability's OWN recharge_time: ONE use per
			-- charge cycle, the pool never drains, and no cast
			-- is silently swallowed.
			if eligible and ability.charge_s ~= nil then
				local cu = charge_gate.until_tick[ui_id]
				local held_until = (cu ~= nil and cu[ability.marker]) or nil
				if held_until ~= nil and tick_count < held_until then
					-- ROUND 128: the selected unit's button says READY -> the
					-- last cast did not take; release the hold (fix A).
					local ready, seen, since_s = FOURTH.charge_hold_ready_on_screen(ui_id, ability, held_until)
					if ready then
						cu[ability.marker] = nil
						log(string.format("  charge gate %s: unit %s is selected and its button reads '%s' (READY) %.2fs after the last cast - that cast did not take; the hold is released",
							ability.marker, tostring(ui_id), tostring(seen), since_s))
					else
						eligible = false
						quiet = true
					end
				end
			end

			-- THE IN-FLIGHT GATE (this round): a cast that is
			-- still RESOLVING may not be re-issued. The hold is
			-- the wind-up the game's own row declares plus 2 s of
			-- slack (IN_FLIGHT_SETTLE_SECONDS); an entry with no
			-- declared wind-up is never gated here and keeps the
			-- plain 2 s guard. Silent while it holds - the gate
			-- speaks ONCE, on the cast that armed it.
			if eligible and ability.wind_up_s ~= nil then
				local cgu = cast_gate.until_tick[ui_id]
				local resolving_until = (cgu ~= nil and cgu[ability.marker]) or nil
				if resolving_until ~= nil and tick_count < resolving_until then
					eligible = false
					quiet = true
				end
			end

			-- THE PER-UNIT SERIALISATION GATE (round 107): the
			-- engine allows ONE special ability in flight per unit.
			-- A second order REPLACES the first during its wind-up
			-- and the replaced cast's use is still spent - the
			-- 2026-10-17 field log shows Captain Roth's Moondial
			-- issued first (3 s wind-up), Wraith Storm issued 0.25 s
			-- later on the same caster, and the Moondial's 120 s
			-- recharge consumed with no effect. So a unit that has
			-- just cast may not be ordered to cast a DIFFERENT
			-- ability until its window closes: the wind-up it
			-- declared + IN_FLIGHT_SETTLE_SECONDS, never less than
			-- SERIAL_MIN_HOLD_SECONDS. The ability that fired is NOT
			-- throttled here - its own pair gates govern its repeat.
			if eligible and cast_gate.unit_until[ui_id] ~= nil
				and cast_gate.unit_marker[ui_id] ~= ability.marker
				and tick_count < cast_gate.unit_until[ui_id] then
				eligible = false
				quiet = true
				local lg = cast_gate.unit_logged[ui_id]
				if lg == nil then
					lg = {}
					cast_gate.unit_logged[ui_id] = lg
				end
				if lg[ability.marker] ~= true then
					lg[ability.marker] = true
										log("  per-unit cast gate " .. ability.marker .. ": unit " .. tostring(ui_id)
		.. " is still resolving '" .. tostring(cast_gate.unit_marker[ui_id])
		.. "' (" .. string.format("%.1f", ((cast_gate.unit_until[ui_id] - tick_count) * POLL_MS) / 1000)
		.. "s left) - waiting its turn (a second special ability would replace it)")
				end
			end

			if eligible then
				local guard = last_attempt_at[ui_id]
				if guard == nil then
					guard = {}
					last_attempt_at[ui_id] = guard
				end
				guard[ability.marker] = tick_count
				-- THE OUTCOME (this build): "gone" means the
				-- pre-fire check or an engine rejection proved
				-- this unit is no longer there. Leave the walk
				-- and drop it after the loop (never mid-iteration).
				-- "cooling" is the engine's cooldown refusal:
				-- arm or extend this pair's cooldown hold.
				local outcome = attempt_activation(script_unit, unit, ready_key, reason,
					ui_id, ability.marker, quiet, FOURTH.cast_target)
				if outcome == "gone" then
					gone_ids[#gone_ids + 1] = ui_id
				return "gone"
				elseif outcome == "cooling" then
					local b = cooldown_hold[ui_id]
					if b == nil then
						b = {}
						cooldown_hold[ui_id] = b
					end
					local rec = b[ability.marker]
					if rec == nil then
						rec = { since = tick_count, next_at = 0, streak = 0, logged = false }
						b[ability.marker] = rec
					end
					rec.streak = rec.streak + 1
					if rec.streak <= 1 then
						-- the first refusal of the episode is the
						-- one that speaks; it keeps the short guard
						rec.next_at = tick_count + GUARD_TICKS
					else
						rec.next_at = tick_count + HOLD_TICKS
					end
					rec.logged = true
				elseif outcome == "fired" then
					-- a real fire ends the cooldown episode
					-- ROUND 130: Restock! - the refilled ally is skipped by every caster
					-- for RESTOCK_CLAIM_S, so two casters never refill it twice.
					if FOURTH.ammo_claim_id ~= nil then
						FOURTH.ammo_claimed[FOURTH.ammo_claim_id] = tick_count
						FOURTH.ammo_claim_id = nil
					end
					local b = cooldown_hold[ui_id]
					if b ~= nil then
						b[ability.marker] = nil
					end
				-- THE PER-UNIT SERIALISATION WINDOW (round 107): arm it
				-- for THIS unit - no OTHER ability may be issued
				-- until it closes. A repeat of the SAME ability does
				-- NOT extend it: a fast-repeating ability must not
				-- starve every other ability on the unit forever.
				if cast_gate.unit_marker[ui_id] ~= ability.marker then
					local unit_hold_s = ((ability.wind_up_s or 0) + IN_FLIGHT_SETTLE_SECONDS)
					if unit_hold_s < FOURTH.SERIAL_MIN_HOLD_SECONDS then
						unit_hold_s = FOURTH.SERIAL_MIN_HOLD_SECONDS
					end
					cast_gate.unit_until[ui_id] = tick_count + math.floor((unit_hold_s * 1000) / POLL_MS)
					cast_gate.unit_marker[ui_id] = ability.marker
					cast_gate.unit_logged[ui_id] = nil
										if not quiet then
		log("  per-unit cast gate armed by " .. ability.marker .. ": no OTHER ability on unit "
			.. tostring(ui_id) .. " may be issued for " .. tostring(unit_hold_s)
			.. "s (wind-up + " .. tostring(IN_FLIGHT_SETTLE_SECONDS) .. "s, min "
			.. tostring(FOURTH.SERIAL_MIN_HOLD_SECONDS) .. "s)") 
	end
				end
					-- THE CHARGE GATE (this round): the cast SPENT
					-- one use, so hold the pair for the ability's own
					-- recharge_time (one use per charge cycle).
					if ability.charge_s ~= nil then
						local cu = charge_gate.until_tick[ui_id]
						if cu == nil then
							cu = {}
							charge_gate.until_tick[ui_id] = cu
						end
						cu[ability.marker] = tick_count + math.floor((ability.charge_s * 1000) / POLL_MS)
						log("  charge gate " .. ability.marker .. ": one use spent - the next attempt waits " .. tostring(ability.charge_s) .. "s (the ability's own recharge_time)")
					end
					-- THE IN-FLIGHT GATE (this round): this cast
					-- needs its own wind-up to land before any
					-- second order may replace it. The hold is
					-- wind_up + IN_FLIGHT_SETTLE_SECONDS, never less
					-- than the ordinary guard. It speaks ONCE per
					-- (unit, marker) - the first cast of the battle -
					-- so a 6 s hold on a buff does not flood the log.
					if ability.wind_up_s ~= nil then
						local cgu = cast_gate.until_tick[ui_id]
						if cgu == nil then
							cgu = {}
							cast_gate.until_tick[ui_id] = cgu
						end
						local hold_s = ability.wind_up_s + IN_FLIGHT_SETTLE_SECONDS
						if hold_s < GUARD_SECONDS then hold_s = GUARD_SECONDS end
						cgu[ability.marker] = tick_count + math.floor((hold_s * 1000) / POLL_MS)
						local lg = cast_gate.logged[ui_id]
						if lg == nil then
							lg = {}
							cast_gate.logged[ui_id] = lg
						end
						if lg[ability.marker] ~= true then
							lg[ability.marker] = true
							log("  in-flight gate " .. ability.marker .. ": the cast needs "
								.. tostring(ability.wind_up_s) .. "s wind-up - the next attempt on this"
								.. " unit waits " .. tostring(hold_s) .. "s (a second order would replace the first)")
						end
					end
				end
			end
		end
	return nil
end


-- ============================================================================
-- ROUND 126 - THE FIRING FLAG FROM THE GAME'S RELOAD TABLE (READ-ONLY: nothing
-- is cast from it yet). The battle API has no "this unit is shooting" read and
-- no reload read; ammo_left() drops when the unit fires (field-proven
-- 2026-11-03), and every ranged unit's reload comes from FOURTH.RELOAD_S below,
-- GENERATED from the game's own tables (user ruling 2026-11-03: a baked stat is
-- allowed when no live read exists). Per ranged unit, per poll (250 ms):
--   * FIRING ON   on the first poll whose ammo_left() is LOWER than the poll
--                 before - the first shot of an episode, which cannot be
--                 anticipated;
--   * CAST POINT  first shot + AMMO_CAST_FRACTION (0.5) x the unit's reload:
--                 where a firing-boosting ability would be cast - before the
--                 models that fired first can fire again (the user's design).
--                 Logged once per episode; NOTHING is cast in this round;
--   * FIRING OFF  once no drop has been seen for max(AMMO_OFF_FACTOR (2) x
--                 the unit's reload, AMMO_OFF_MIN_S (20 s)); a unit missing from
--                 the table uses the 20 s minimum. ROUND 127: the round-126
--                 window (1.25 x reload) split Land Ships, Steam Tanks and hunter
--                 characters into one episode per shot - they fire SLOWER than
--                 their table reload (field battle 2026-11-03). The round-125
--                 rule (1.25 x the most recent measured gap) is long gone;
--   * IN RANGE / OUT OF RANGE: the unit's current target within its own LIVE
--                 missile_range() (unit_distance, edge to edge), logged on each
--                 change; FIRING ON reports how long the unit had been in range
--                 before its first shot - the measurement that decides whether
--                 the first shot can be predicted;
--   * a rise in ammo_left() is a resupply, never a shot.
-- Units with no ammunition (starting_ammo() 0, or unreadable) are read ONCE.
-- ============================================================================
FOURTH.AMMO_OFF_FACTOR = 2            -- FIRING OFF after 2 x the unit's reload with no drop ...
FOURTH.AMMO_OFF_MIN_S = 20            -- ... but never sooner than 20 s (and 20 s for a unit missing from the table)
FOURTH.AMMO_CAST_FRACTION = 0.5       -- CAST POINT: first shot + 0.5 x the unit's reload (user, 2026-11-03)
FOURTH.ammo = setmetatable({}, { __mode = "k" })   -- per tracked entry: start, reload, last, firing, ...

-- BEGIN GENERATED RELOAD TABLE (tools/gen_reload_table.py; do not edit by hand)
-- 564 ranged units: seconds between shots (base_reload_time x (1 - reload skill / 100))
FOURTH.RELOAD_S = {
	["wh2_dlc09_tmb_art_casket_of_souls_0"] = 18,
	["wh2_dlc09_tmb_art_screaming_skull_catapult_0"] = 16,
	["wh2_dlc09_tmb_cav_skeleton_horsemen_archers_0"] = 11,
	["wh2_dlc09_tmb_cha_khatep_3"] = 18,
	["wh2_dlc09_tmb_inf_skeleton_archers_0"] = 8,
	["wh2_dlc09_tmb_inf_skeleton_archers_ror"] = 6.56,
	["wh2_dlc09_tmb_mon_sepulchral_stalkers_0"] = 10,
	["wh2_dlc09_tmb_mon_sepulchral_stalkers_ror"] = 8.2,
	["wh2_dlc09_tmb_mon_ushabti_1"] = 11,
	["wh2_dlc09_tmb_mon_ushabti_ror"] = 9.02,
	["wh2_dlc09_tmb_veh_skeleton_archer_chariot_0"] = 6,
	["wh2_dlc10_def_cav_raven_heralds_ror_0"] = 11.48,
	["wh2_dlc10_def_inf_the_bolt_fiends_ror_0"] = 11.48,
	["wh2_dlc10_hef_cav_the_heralds_of_the_wind_ror_0"] = 9.02,
	["wh2_dlc10_hef_cha_alith_anar_0"] = 11,
	["wh2_dlc10_hef_cha_alith_anar_summoned_0"] = 11,
	["wh2_dlc10_hef_cha_alith_anar_summoned_1"] = 11,
	["wh2_dlc10_hef_cha_handmaiden_0"] = 9,
	["wh2_dlc10_hef_cha_handmaiden_1"] = 9,
	["wh2_dlc10_hef_cha_handmaiden_2"] = 9,
	["wh2_dlc10_hef_cha_shadow_walker"] = 11,
	["wh2_dlc10_hef_inf_everqueens_court_guards_ror_0"] = 8.2,
	["wh2_dlc10_hef_inf_shadow_walkers_0"] = 11,
	["wh2_dlc10_hef_inf_shadow_warriors_0"] = 11,
	["wh2_dlc10_hef_inf_sisters_of_avelorn_0"] = 10,
	["wh2_dlc10_hef_inf_the_grey_ror_0"] = 9.02,
	["wh2_dlc10_hef_inf_the_storm_riders_ror_0"] = 9.02,
	["wh2_dlc11_cst_art_carronade"] = 22,
	["wh2_dlc11_cst_art_mortar"] = 20,
	["wh2_dlc11_cst_art_queen_bess"] = 18,
	["wh2_dlc11_cst_cav_deck_droppers_0"] = 9,
	["wh2_dlc11_cst_cav_deck_droppers_1"] = 14,
	["wh2_dlc11_cst_cav_deck_droppers_2"] = 13,
	["wh2_dlc11_cst_cav_deck_droppers_ror_0"] = 11.48,
	["wh2_dlc11_cst_cha_gunnery_wight_0"] = 8,
	["wh2_dlc11_cst_cha_gunnery_wight_1"] = 8,
	["wh2_dlc11_cst_cha_luthor_harkon_0"] = 4,
	["wh2_dlc11_cst_cha_luthor_harkon_1"] = 4,
	["wh2_dlc11_cst_cha_vampire_fleet_admiral_female_0"] = 4,
	["wh2_dlc11_cst_cha_vampire_fleet_admiral_female_1"] = 4,
	["wh2_dlc11_cst_cha_vampire_fleet_admiral_female_death_0"] = 4,
	["wh2_dlc11_cst_cha_vampire_fleet_admiral_female_death_1"] = 4,
	["wh2_dlc11_cst_cha_vampire_fleet_admiral_female_deeps_0"] = 4,
	["wh2_dlc11_cst_cha_vampire_fleet_admiral_female_deeps_1"] = 4,
	["wh2_dlc11_cst_inf_count_noctilus_1"] = 12,
	["wh2_dlc11_cst_inf_deck_gunners_0"] = 11,
	["wh2_dlc11_cst_inf_deck_gunners_0_summoned"] = 11,
	["wh2_dlc11_cst_inf_deck_gunners_ror_0"] = 9.02,
	["wh2_dlc11_cst_inf_sartosa_militia_0"] = 9,
	["wh2_dlc11_cst_inf_zombie_gunnery_mob_0"] = 11,
	["wh2_dlc11_cst_inf_zombie_gunnery_mob_1"] = 13,
	["wh2_dlc11_cst_inf_zombie_gunnery_mob_2"] = 14,
	["wh2_dlc11_cst_inf_zombie_gunnery_mob_3"] = 10,
	["wh2_dlc11_cst_inf_zombie_gunnery_mob_ror_0"] = 10.66,
	["wh2_dlc11_cst_inf_zombie_gunnery_mob_summoned_0"] = 11,
	["wh2_dlc11_cst_mon_necrofex_colossus_0"] = 12,
	["wh2_dlc11_cst_mon_necrofex_colossus_ror_0"] = 6.56,
	["wh2_dlc11_vmp_inf_crossbowmen"] = 13,
	["wh2_dlc11_vmp_inf_handgunners"] = 13,
	["wh2_dlc12_lzd_cav_terradon_riders_0_tlaqua"] = 6,
	["wh2_dlc12_lzd_cav_terradon_riders_1_tlaqua"] = 8,
	["wh2_dlc12_lzd_cav_terradon_riders_ror_0"] = 4.92,
	["wh2_dlc12_lzd_cha_skink_chief_red_crested_3"] = 8,
	["wh2_dlc12_lzd_mon_ancient_salamander_0"] = 12,
	["wh2_dlc12_lzd_mon_ancient_salamander_0_blessed"] = 12,
	["wh2_dlc12_lzd_mon_ancient_stegadon_ror_0"] = 6.56,
	["wh2_dlc12_lzd_mon_salamander_pack_0"] = 12,
	["wh2_dlc12_lzd_mon_salamander_pack_0_blessed"] = 12,
	["wh2_dlc12_lzd_mon_salamander_pack_ror_0"] = 9.84,
	["wh2_dlc12_skv_art_warp_lightning_cannon_ror_0"] = 17.22,
	["wh2_dlc12_skv_art_warplock_jezzails_ror_tech_lab_0"] = 9.84,
	["wh2_dlc12_skv_cha_ikit_claw_0"] = 12,
	["wh2_dlc12_skv_inf_ratling_gun_0"] = 5,
	["wh2_dlc12_skv_inf_ratling_gun_ror_0"] = 4.1,
	["wh2_dlc12_skv_inf_ratling_gun_ror_tech_lab_0"] = 4.1,
	["wh2_dlc12_skv_inf_warpfire_thrower_ror_tech_lab_0"] = 10.66,
	["wh2_dlc12_skv_inf_warplock_jezzails_0"] = 12,
	["wh2_dlc12_skv_inf_warplock_jezzails_ror_0"] = 9.84,
	["wh2_dlc13_emp_art_great_cannon_imperial_supply"] = 22,
	["wh2_dlc13_emp_art_helblaster_volley_gun_imperial_supply"] = 10,
	["wh2_dlc13_emp_art_helstorm_rocket_battery_imperial_supply"] = 17,
	["wh2_dlc13_emp_art_mortar_ror_0"] = 19,
	["wh2_dlc13_emp_cav_outriders_1_imperial_supply"] = 10,
	["wh2_dlc13_emp_cav_outriders_ror_0"] = 10,
	["wh2_dlc13_emp_cav_pistoliers_1_imperial_supply"] = 9,
	["wh2_dlc13_emp_cav_pistoliers_ror_0"] = 9,
	["wh2_dlc13_emp_cha_hunter_doctor_hertwig_van_hal_0"] = 4,
	["wh2_dlc13_emp_cha_hunter_jorek_grimm_0"] = 8,
	["wh2_dlc13_emp_cha_hunter_kalara_of_wydrioth_0"] = 8,
	["wh2_dlc13_emp_cha_huntsmarshal_0"] = 8,
	["wh2_dlc13_emp_cha_markus_wulfhart_0"] = 8,
	["wh2_dlc13_emp_inf_archers_0"] = 10,
	["wh2_dlc13_emp_inf_archers_ror_0"] = 8.2,
	["wh2_dlc13_emp_inf_crossbowmen_ror_0"] = 13,
	["wh2_dlc13_emp_inf_handgunners_imperial_supply"] = 13,
	["wh2_dlc13_emp_inf_handgunners_ror_0"] = 13,
	["wh2_dlc13_emp_inf_huntsmen_0"] = 11,
	["wh2_dlc13_emp_inf_huntsmen_0_imperial_supply"] = 11,
	["wh2_dlc13_emp_inf_huntsmen_ror_0"] = 9.02,
	["wh2_dlc13_emp_veh_luminark_of_hysh_0_imperial_supply"] = 11,
	["wh2_dlc13_emp_veh_steam_tank_imperial_supply"] = 10,
	["wh2_dlc13_emp_veh_steam_tank_ror_0"] = 11,
	["wh2_dlc13_emp_veh_war_wagon_0"] = 6,
	["wh2_dlc13_emp_veh_war_wagon_0_imperial_supply"] = 6,
	["wh2_dlc13_emp_veh_war_wagon_1"] = 19,
	["wh2_dlc13_emp_veh_war_wagon_1_imperial_supply"] = 19,
	["wh2_dlc13_emp_veh_war_wagon_ror_0"] = 8.2,
	["wh2_dlc13_huntmarshall_veh_obsinite_gyrocopter_0"] = 8,
	["wh2_dlc13_lzd_mon_razordon_pack_0"] = 10,
	["wh2_dlc13_lzd_mon_razordon_pack_0_blessed"] = 10,
	["wh2_dlc13_lzd_mon_razordon_pack_ror_0"] = 8.2,
	["wh2_dlc13_lzd_mon_razordon_pack_summoned_0"] = 10,
	["wh2_dlc14_def_cav_scourgerunner_chariot_0"] = 7,
	["wh2_dlc14_def_cav_scourgerunner_chariot_ror_0"] = 5.74,
	["wh2_dlc14_def_cha_high_beastmaster_1"] = 7,
	["wh2_dlc14_def_mon_bloodwrack_medusa_0"] = 10,
	["wh2_dlc14_def_mon_bloodwrack_medusa_ror_0"] = 8.2,
	["wh2_dlc14_def_veh_bloodwrack_shrine_0"] = 10,
	["wh2_dlc14_skv_cha_master_assassin_0"] = 6,
	["wh2_dlc14_skv_inf_poison_wind_mortar_0"] = 14,
	["wh2_dlc14_skv_inf_poison_wind_mortar_ror_0"] = 11.48,
	["wh2_dlc15_grn_cav_forest_goblin_spider_riders_waaagh_0"] = 8,
	["wh2_dlc15_grn_mon_rogue_idol_ror_0"] = 12.3,
	["wh2_dlc15_hef_cha_princess_6"] = 8,
	["wh2_dlc15_hef_inf_archers_ror_0"] = 9.02,
	["wh2_dlc15_hef_inf_mistwalkers_sentinels_0"] = 22,
	["wh2_dlc15_hef_inf_mistwalkers_skyhawks_0"] = 11,
	["wh2_dlc15_hef_inf_mistwalkers_spireguard_0"] = 11,
	["wh2_dlc16_wef_cha_female_glade_lord_4"] = 8,
	["wh2_dlc16_wef_cha_glade_lord_4"] = 8,
	["wh2_dlc16_wef_cha_sisters_of_twilight_0"] = 10,
	["wh2_dlc16_wef_cha_sisters_of_twilight_1"] = 10,
	["wh2_dlc17_bst_inf_centigors_ror_1"] = 8.2,
	["wh2_dlc17_lzd_cha_oxyotl_0"] = 6,
	["wh2_dlc17_lzd_cha_skink_oracle_troglodon_0"] = 8,
	["wh2_dlc17_lzd_inf_chameleon_stalkers_0"] = 6,
	["wh2_dlc17_lzd_inf_chameleon_stalkers_0_blessed"] = 6,
	["wh2_dlc17_lzd_mon_troglodon_0"] = 8,
	["wh2_dlc17_lzd_mon_troglodon_ror_0"] = 6.56,
	["wh2_main_def_art_reaper_bolt_thrower"] = 11,
	["wh2_main_def_cav_cold_one_chariot"] = 7,
	["wh2_main_def_cav_dark_riders_2"] = 14,
	["wh2_main_def_cha_dreadlord_0"] = 12,
	["wh2_main_def_cha_dreadlord_0_black_ark"] = 12,
	["wh2_main_def_cha_dreadlord_1"] = 12,
	["wh2_main_def_cha_dreadlord_2"] = 12,
	["wh2_main_def_cha_dreadlord_4"] = 12,
	["wh2_main_def_cha_dreadlord_5"] = 12,
	["wh2_main_def_cha_khainite_assassin_0"] = 5,
	["wh2_main_def_inf_black_ark_corsairs_1"] = 12,
	["wh2_main_def_inf_darkshards_0"] = 14,
	["wh2_main_def_inf_darkshards_1"] = 14,
	["wh2_main_def_inf_shades_0"] = 10,
	["wh2_main_def_inf_shades_1"] = 10,
	["wh2_main_def_inf_shades_2"] = 10,
	["wh2_main_hef_art_eagle_claw_bolt_thrower"] = 12,
	["wh2_main_hef_cav_ellyrian_reavers_1"] = 11,
	["wh2_main_hef_cav_tiranoc_chariot"] = 7,
	["wh2_main_hef_cha_princess_0"] = 8,
	["wh2_main_hef_cha_princess_1"] = 8,
	["wh2_main_hef_cha_princess_3"] = 8,
	["wh2_main_hef_cha_princess_4"] = 8,
	["wh2_main_hef_cha_princess_5"] = 8,
	["wh2_main_hef_inf_archers_0"] = 11,
	["wh2_main_hef_inf_archers_1"] = 11,
	["wh2_main_hef_inf_gate_guard"] = 11,
	["wh2_main_hef_inf_lothern_sea_guard_0"] = 11,
	["wh2_main_hef_inf_lothern_sea_guard_1"] = 11,
	["wh2_main_lzd_cav_terradon_riders_0"] = 6,
	["wh2_main_lzd_cav_terradon_riders_0_blessed"] = 6,
	["wh2_main_lzd_cav_terradon_riders_1"] = 8,
	["wh2_main_lzd_cav_terradon_riders_blessed_1"] = 8,
	["wh2_main_lzd_cha_skink_chief_0"] = 4,
	["wh2_main_lzd_cha_skink_chief_1"] = 4,
	["wh2_main_lzd_cha_skink_chief_2"] = 12,
	["wh2_main_lzd_cha_skink_chief_3"] = 8,
	["wh2_main_lzd_cha_skink_priest_beasts_2"] = 12,
	["wh2_main_lzd_cha_skink_priest_beasts_3"] = 8,
	["wh2_main_lzd_cha_skink_priest_heavens_2"] = 12,
	["wh2_main_lzd_cha_skink_priest_heavens_3"] = 8,
	["wh2_main_lzd_inf_chameleon_skinks_0"] = 6,
	["wh2_main_lzd_inf_chameleon_skinks_blessed_0"] = 6,
	["wh2_main_lzd_inf_skink_cohort_1"] = 10,
	["wh2_main_lzd_inf_skink_cohort_1_blessed"] = 10,
	["wh2_main_lzd_inf_skink_skirmishers_0"] = 6,
	["wh2_main_lzd_inf_skink_skirmishers_blessed_0"] = 6,
	["wh2_main_lzd_mon_ancient_stegadon"] = 8,
	["wh2_main_lzd_mon_ancient_stegadon_blessed"] = 8,
	["wh2_main_lzd_mon_bastiladon_2"] = 16,
	["wh2_main_lzd_mon_bastiladon_blessed_2"] = 16,
	["wh2_main_lzd_mon_stegadon_1"] = 12,
	["wh2_main_lzd_mon_stegadon_blessed_1"] = 12,
	["wh2_main_skv_art_plagueclaw_catapult"] = 18,
	["wh2_main_skv_art_warp_lightning_cannon"] = 21,
	["wh2_main_skv_inf_death_globe_bombardiers"] = 10,
	["wh2_main_skv_inf_gutter_runner_slingers_0"] = 8,
	["wh2_main_skv_inf_gutter_runner_slingers_1"] = 8,
	["wh2_main_skv_inf_gutter_runners_0"] = 7,
	["wh2_main_skv_inf_gutter_runners_1"] = 7,
	["wh2_main_skv_inf_night_runners_0"] = 7,
	["wh2_main_skv_inf_night_runners_1"] = 8,
	["wh2_main_skv_inf_poison_wind_globadiers"] = 12,
	["wh2_main_skv_inf_skavenslave_slingers_0"] = 9,
	["wh2_main_skv_inf_warpfire_thrower"] = 13,
	["wh2_pro06_tmb_mon_bone_giant_0"] = 11,
	["wh2_twa02_wef_cha_glade_captain_0"] = 9,
	["wh2_twa02_wef_cha_glade_captain_1"] = 9,
	["wh2_twa02_wef_cha_glade_captain_2"] = 9,
	["wh2_twa02_wef_cha_glade_captain_3"] = 9,
	["wh2_twa03_def_cha_rakarth_1"] = 7,
	["wh3_cp1_cth_inf_stalkers_throwing_disc"] = 8,
	["wh3_dlc20_chs_cav_marauder_horsemen_mkho_throwing_axes"] = 10,
	["wh3_dlc20_chs_cav_marauder_horsemen_mnur_throwing_axes"] = 10,
	["wh3_dlc20_chs_cav_marauder_horsemen_msla_javelins"] = 9,
	["wh3_dlc20_chs_cav_marauder_horsemen_mtze_javelins"] = 9,
	["wh3_dlc23_chd_cav_bull_centaurs_dual_axe_ror"] = 8.2,
	["wh3_dlc23_chd_cav_hobgoblin_wolf_raiders_bows"] = 10,
	["wh3_dlc23_chd_cav_hobgoblin_wolf_raiders_ror"] = 8.2,
	["wh3_dlc23_chd_cha_daemonsmith_sorcerer_death"] = 10,
	["wh3_dlc23_chd_cha_daemonsmith_sorcerer_death_bale_taurus"] = 10,
	["wh3_dlc23_chd_cha_daemonsmith_sorcerer_death_great_taurus"] = 10,
	["wh3_dlc23_chd_cha_daemonsmith_sorcerer_death_lammasu"] = 10,
	["wh3_dlc23_chd_cha_daemonsmith_sorcerer_fire"] = 10,
	["wh3_dlc23_chd_cha_daemonsmith_sorcerer_fire_bale_taurus"] = 10,
	["wh3_dlc23_chd_cha_daemonsmith_sorcerer_fire_great_taurus"] = 10,
	["wh3_dlc23_chd_cha_daemonsmith_sorcerer_fire_lammasu"] = 10,
	["wh3_dlc23_chd_cha_daemonsmith_sorcerer_hashut"] = 10,
	["wh3_dlc23_chd_cha_daemonsmith_sorcerer_hashut_bale_taurus"] = 10,
	["wh3_dlc23_chd_cha_daemonsmith_sorcerer_hashut_great_taurus"] = 10,
	["wh3_dlc23_chd_cha_daemonsmith_sorcerer_hashut_lammasu"] = 10,
	["wh3_dlc23_chd_cha_daemonsmith_sorcerer_metal"] = 10,
	["wh3_dlc23_chd_cha_daemonsmith_sorcerer_metal_bale_taurus"] = 10,
	["wh3_dlc23_chd_cha_daemonsmith_sorcerer_metal_great_taurus"] = 10,
	["wh3_dlc23_chd_cha_daemonsmith_sorcerer_metal_lammasu"] = 10,
	["wh3_dlc23_chd_cha_infernal_castellan"] = 8,
	["wh3_dlc23_chd_cha_sorcerer_prophet_death"] = 10,
	["wh3_dlc23_chd_cha_sorcerer_prophet_death_bale_taurus"] = 10,
	["wh3_dlc23_chd_cha_sorcerer_prophet_death_great_taurus"] = 10,
	["wh3_dlc23_chd_cha_sorcerer_prophet_death_lammasu"] = 10,
	["wh3_dlc23_chd_cha_sorcerer_prophet_fire"] = 10,
	["wh3_dlc23_chd_cha_sorcerer_prophet_fire_bale_taurus"] = 10,
	["wh3_dlc23_chd_cha_sorcerer_prophet_fire_great_taurus"] = 10,
	["wh3_dlc23_chd_cha_sorcerer_prophet_fire_lammasu"] = 10,
	["wh3_dlc23_chd_cha_sorcerer_prophet_hashut"] = 10,
	["wh3_dlc23_chd_cha_sorcerer_prophet_hashut_bale_taurus"] = 10,
	["wh3_dlc23_chd_cha_sorcerer_prophet_hashut_great_taurus"] = 10,
	["wh3_dlc23_chd_cha_sorcerer_prophet_hashut_lammasu"] = 10,
	["wh3_dlc23_chd_cha_sorcerer_prophet_metal"] = 10,
	["wh3_dlc23_chd_cha_sorcerer_prophet_metal_bale_taurus"] = 10,
	["wh3_dlc23_chd_cha_sorcerer_prophet_metal_great_taurus"] = 10,
	["wh3_dlc23_chd_cha_sorcerer_prophet_metal_lammasu"] = 10,
	["wh3_dlc23_chd_inf_chaos_dwarf_blunderbusses"] = 11,
	["wh3_dlc23_chd_inf_chaos_dwarf_blunderbusses_ror"] = 7.38,
	["wh3_dlc23_chd_inf_chaos_dwarf_warriors_ror"] = 7.38,
	["wh3_dlc23_chd_inf_hobgoblin_archers"] = 10,
	["wh3_dlc23_chd_inf_hobgoblin_sneaky_gits"] = 7,
	["wh3_dlc23_chd_inf_infernal_guard_fireglaives"] = 9,
	["wh3_dlc23_chd_inf_infernal_ironsworn"] = 9,
	["wh3_dlc23_chd_veh_deathshrieker_rocket_launcher"] = 12,
	["wh3_dlc23_chd_veh_dreadquake_mortar"] = 24,
	["wh3_dlc23_chd_veh_iron_daemon"] = 11,
	["wh3_dlc23_chd_veh_iron_daemon_1dreadquake"] = 24,
	["wh3_dlc23_chd_veh_iron_daemon_ror"] = 7.38,
	["wh3_dlc23_chd_veh_iron_daemon_ror_1dreadquake"] = 19.68,
	["wh3_dlc23_chd_veh_magma_cannon"] = 10,
	["wh3_dlc23_chd_veh_skullcracker_1dreadquake"] = 24,
	["wh3_dlc23_neu_cha_ulrika"] = 7,
	["wh3_dlc23_neu_cha_ulrika_warhorse"] = 7,
	["wh3_dlc24_cth_cha_gate_master"] = 12,
	["wh3_dlc24_cth_cha_gate_master_warhorse"] = 12,
	["wh3_dlc24_cth_cha_saytang_the_watcher"] = 11,
	["wh3_dlc24_cth_inf_dragon_guard_crossbowmen_ror"] = 10.66,
	["wh3_dlc24_ksl_cha_druzhina"] = 8,
	["wh3_dlc24_ksl_cha_druzhina_warhorse"] = 8,
	["wh3_dlc24_ksl_cha_hag_witch_beast"] = 8,
	["wh3_dlc24_ksl_cha_hag_witch_death"] = 8,
	["wh3_dlc24_ksl_cha_hag_witch_hag"] = 8,
	["wh3_dlc24_ksl_cha_hag_witch_shadow"] = 8,
	["wh3_dlc24_ksl_cha_katarin_ice_court_sled"] = 10,
	["wh3_dlc24_ksl_cha_mother_ostankya"] = 12,
	["wh3_dlc24_ksl_inf_akshina_ambushers"] = 12,
	["wh3_dlc24_ksl_inf_akshina_ambushers_ror"] = 10.8,
	["wh3_dlc24_ksl_inf_streltsi_ror"] = 11,
	["wh3_dlc24_tze_cha_blue_scribes"] = 7.2,
	["wh3_dlc24_tze_inf_pink_horrors_ror"] = 6.56,
	["wh3_dlc24_tze_mon_flamers_changebringers"] = 8,
	["wh3_dlc25_dwf_art_grudge_thrower_grudge_reward"] = 20,
	["wh3_dlc25_dwf_cha_malakai_makaisson"] = 7,
	["wh3_dlc25_dwf_inf_miners_1_summoned"] = 9,
	["wh3_dlc25_dwf_inf_slayer_pirates"] = 5,
	["wh3_dlc25_dwf_inf_slayer_pirates_ror"] = 4.1,
	["wh3_dlc25_dwf_inf_thunderers_grudge_rakers"] = 8,
	["wh3_dlc25_dwf_inf_thunderers_ror"] = 9.84,
	["wh3_dlc25_dwf_veh_gyrocopter_summoned_0"] = 8,
	["wh3_dlc25_dwf_veh_thunderbarge"] = 10,
	["wh3_dlc25_dwf_veh_thunderbarge_grungni"] = 10,
	["wh3_dlc25_dwf_veh_thunderbarge_grungni_mp"] = 10,
	["wh3_dlc25_dwf_veh_thunderbarge_malakai"] = 10,
	["wh3_dlc25_emp_art_helstorm_rocket_battery_morr"] = 17,
	["wh3_dlc25_emp_cav_outriders_morr"] = 10,
	["wh3_dlc25_emp_cha_engineer"] = 11,
	["wh3_dlc25_emp_cha_engineer_mechanical_steed"] = 11,
	["wh3_dlc25_emp_cha_engineer_warhorse"] = 11,
	["wh3_dlc25_emp_cha_master_engineer"] = 10,
	["wh3_dlc25_emp_cha_master_engineer_mechanical_steed"] = 10,
	["wh3_dlc25_emp_cha_master_engineer_steam_tank"] = 10,
	["wh3_dlc25_emp_cha_master_engineer_warhorse"] = 10,
	["wh3_dlc25_emp_inf_hochland_long_rifles"] = 13,
	["wh3_dlc25_emp_inf_hochland_long_rifles_ror"] = 10.66,
	["wh3_dlc25_emp_inf_nuln_ironsides"] = 7,
	["wh3_dlc25_emp_inf_nuln_ironsides_morr"] = 7,
	["wh3_dlc25_emp_veh_marienburg_land_ship"] = 10,
	["wh3_dlc25_emp_veh_marienburg_land_ship_morr"] = 10,
	["wh3_dlc25_emp_veh_marienburg_land_ship_ror"] = 8.2,
	["wh3_dlc25_emp_veh_steam_tank_volley_gun"] = 6,
	["wh3_dlc25_grn_mon_rogue_idol_qb_boss"] = 9.84,
	["wh3_dlc25_nur_cav_plague_drones_1_ror"] = 6,
	["wh3_dlc25_nur_cha_infernal_castellan_chieftain"] = 8,
	["wh3_dlc25_nur_chieftain_art_hellcannon"] = 12,
	["wh3_dlc25_nur_chieftain_inf_centigors_1"] = 10,
	["wh3_dlc25_nur_chieftain_inf_chaos_dwarf_blunderbusses"] = 11,
	["wh3_dlc25_nur_chieftain_inf_cygor_0"] = 15,
	["wh3_dlc25_nur_chieftain_inf_infernal_guard_fireglaives"] = 9,
	["wh3_dlc25_nur_chieftain_veh_dreadquake_mortar"] = 24,
	["wh3_dlc25_nur_mon_soul_grinder_0_ror"] = 16.4,
	["wh3_dlc26_grn_art_bolt_throwa"] = 12,
	["wh3_dlc26_grn_art_bolt_throwa_ror"] = 10,
	["wh3_dlc26_grn_inf_rugluds_armoured_orcs"] = 11,
	["wh3_dlc26_grn_mon_arachnarok_spider_flinger"] = 18,
	["wh3_dlc26_kho_veh_skullcannon_ror"] = 18,
	["wh3_dlc26_ogr_mon_thundertusk"] = 14,
	["wh3_dlc27_bst_inf_cygor_monst_arcanum_reward"] = 15,
	["wh3_dlc27_hef_veh_skycutter_bolt_thrower"] = 9,
	["wh3_dlc27_hef_veh_skycutter_bows"] = 8,
	["wh3_dlc27_nor_cav_marauder_horsemen_ror"] = 7.2,
	["wh3_dlc27_nor_mon_dread_maw"] = 10,
	["wh3_dlc27_nor_mon_dread_maw_underground"] = 10,
	["wh3_dlc27_ogr_mon_thundertusk_monst_arcanum"] = 9.8,
	["wh3_dlc27_sla_inf_devotees_of_slaanesh_crossbows"] = 8,
	["wh3_dlc29_chs_cav_nur_plague_drones_1_summoned"] = 8,
	["wh3_dlc29_cst_cha_gunnery_wight_0_summoned"] = 8,
	["wh3_dlc29_cst_cha_vampire_fleet_admiral_female_undeath"] = 4,
	["wh3_dlc29_cst_cha_vampire_fleet_admiral_female_undeath_rotting_promethean"] = 4,
	["wh3_dlc29_cst_inf_zombie_pirate_gunnery_mob_bombers_summoned"] = 10,
	["wh3_dlc29_cst_mon_necrofex_colossus_0_summoned"] = 12,
	["wh3_dlc29_skv_art_plagueclaw_catapult_ror"] = 15,
	["wh3_dlc29_skv_art_warp_doom_magma_cannon"] = 21,
	["wh3_dlc29_skv_cha_thanquol_boneripper_warpfire_projectors"] = 10,
	["wh3_dlc29_skv_cha_verminlord_deceiver"] = 6,
	["wh3_dlc29_skv_inf_poison_wind_mortar_0_summoned"] = 14,
	["wh3_dlc29_skv_inf_skavenslave_slingers_vermintide"] = 9,
	["wh3_dlc29_skv_mon_stormfiend_ratling_cannons"] = 5,
	["wh3_dlc29_skv_mon_stormfiend_warpfire_projectors"] = 13,
	["wh3_dlc29_skv_mon_stormfiend_windlaunchers"] = 14,
	["wh3_dlc29_skv_mon_stormfiends_ratling_cannons_ror"] = 4,
	["wh3_dlc29_tmb_veh_skeleton_archer_chariot_0_summoned"] = 6,
	["wh3_main_chd_art_hobgob_bolt_thrower"] = 12,
	["wh3_main_chs_art_hellcannon_prologue"] = 12,
	["wh3_main_cth_art_fire_rain_rocket_battery_0"] = 20,
	["wh3_main_cth_art_grand_cannon_0"] = 22,
	["wh3_main_cth_cha_alchemist_2"] = 12,
	["wh3_main_cth_cha_lord_magistrate_2"] = 12,
	["wh3_main_cth_inf_crane_gunners_0"] = 12,
	["wh3_main_cth_inf_dragon_guard_crossbowmen_0"] = 13,
	["wh3_main_cth_inf_grenadiers"] = 10,
	["wh3_main_cth_inf_iron_hail_gunners_0"] = 13,
	["wh3_main_cth_inf_jade_warrior_crossbowmen_0"] = 13,
	["wh3_main_cth_inf_jade_warrior_crossbowmen_1"] = 13,
	["wh3_main_cth_inf_peasant_archers_0"] = 11,
	["wh3_main_cth_veh_sky_junk_0"] = 20,
	["wh3_main_cth_veh_sky_lantern_0"] = 12,
	["wh3_main_kho_mon_soul_grinder_0"] = 5,
	["wh3_main_kho_veh_skullcannon_0"] = 11,
	["wh3_main_ksl_cav_horse_archers_0"] = 11,
	["wh3_main_ksl_cha_ataman"] = 4,
	["wh3_main_ksl_inf_armoured_kossars_0"] = 11,
	["wh3_main_ksl_inf_armoured_kossars_1"] = 11,
	["wh3_main_ksl_inf_ice_guard_0"] = 10,
	["wh3_main_ksl_inf_ice_guard_1"] = 10,
	["wh3_main_ksl_inf_kossars_0"] = 11,
	["wh3_main_ksl_inf_kossars_1"] = 11,
	["wh3_main_ksl_inf_streltsi_0"] = 13,
	["wh3_main_ksl_veh_heavy_war_sled_0"] = 13,
	["wh3_main_ksl_veh_light_war_sled_0"] = 13,
	["wh3_main_ksl_veh_little_grom_0"] = 14,
	["wh3_main_nur_cav_plague_drones_1"] = 8,
	["wh3_main_nur_cha_ku_gath_plaguefather_0"] = 10,
	["wh3_main_nur_inf_plaguebearers_1"] = 8,
	["wh3_main_nur_inf_plaguebearers_1_summoned"] = 8,
	["wh3_main_nur_mon_soul_grinder_0"] = 16,
	["wh3_main_ogr_cha_hunter_0"] = 8,
	["wh3_main_ogr_cha_hunter_1"] = 8,
	["wh3_main_ogr_inf_gnoblars_1"] = 8,
	["wh3_main_ogr_inf_gnoblars_flingers"] = 9,
	["wh3_main_ogr_inf_leadbelchers_0"] = 13,
	["wh3_main_ogr_inf_maneaters_3"] = 11,
	["wh3_main_ogr_mon_stonehorn_1"] = 12,
	["wh3_main_ogr_veh_gnoblar_scraplauncher_0"] = 17,
	["wh3_main_ogr_veh_ironblaster_0"] = 16,
	["wh3_main_pro_ksl_inf_armoured_kossars_0"] = 11,
	["wh3_main_pro_ksl_inf_armoured_kossars_1"] = 11,
	["wh3_main_pro_ksl_inf_ice_guard_ror_0"] = 10,
	["wh3_main_pro_ksl_inf_ice_guard_ror_1"] = 10,
	["wh3_main_pro_ksl_inf_kossars_0"] = 11,
	["wh3_main_pro_ksl_inf_kossars_1"] = 11,
	["wh3_main_pro_ksl_inf_streltsi_0"] = 13,
	["wh3_main_pro_ksl_veh_heavy_war_sled_ror_0"] = 13,
	["wh3_main_pro_ksl_veh_light_war_sled_ror_0"] = 13,
	["wh3_main_pro_ksl_veh_little_grom_0"] = 14,
	["wh3_main_pro_tze_cha_herald_of_tzeentch_tzeentch_0"] = 8,
	["wh3_main_pro_tze_cha_herald_of_tzeentch_tzeentch_1"] = 8,
	["wh3_main_pro_tze_cha_herald_of_tzeentch_tzeentch_2"] = 8,
	["wh3_main_pro_tze_inf_blue_horrors_0"] = 8,
	["wh3_main_pro_tze_inf_pink_horrors_0"] = 8,
	["wh3_main_pro_tze_mon_flamers_0"] = 8,
	["wh3_main_tze_cha_herald_of_tzeentch_metal_0"] = 8,
	["wh3_main_tze_cha_herald_of_tzeentch_metal_1"] = 8,
	["wh3_main_tze_cha_herald_of_tzeentch_metal_2"] = 8,
	["wh3_main_tze_cha_herald_of_tzeentch_tzeentch_0"] = 8,
	["wh3_main_tze_cha_herald_of_tzeentch_tzeentch_1"] = 8,
	["wh3_main_tze_cha_herald_of_tzeentch_tzeentch_2"] = 8,
	["wh3_main_tze_cha_iridescent_horror_metal_0"] = 8,
	["wh3_main_tze_cha_iridescent_horror_metal_1"] = 8,
	["wh3_main_tze_cha_iridescent_horror_metal_2"] = 8,
	["wh3_main_tze_cha_iridescent_horror_tzeentch_0"] = 8,
	["wh3_main_tze_cha_iridescent_horror_tzeentch_1"] = 8,
	["wh3_main_tze_cha_iridescent_horror_tzeentch_2"] = 8,
	["wh3_main_tze_inf_blue_horrors_0"] = 8,
	["wh3_main_tze_inf_blue_horrors_summoned_0"] = 8,
	["wh3_main_tze_inf_pink_horrors_0"] = 8,
	["wh3_main_tze_inf_pink_horrors_1"] = 8,
	["wh3_main_tze_inf_pink_horrors_summoned_0"] = 8,
	["wh3_main_tze_mon_exalted_flamers_0"] = 8,
	["wh3_main_tze_mon_flamers_0"] = 8,
	["wh3_main_tze_mon_soul_grinder_0"] = 12,
	["wh3_main_tze_veh_burning_chariot_0"] = 8,
	["wh3_survival_tze_cha_iridescent_horror_metal"] = 8,
	["wh3_twa06_nur_inf_plaguebearers_ror_0"] = 6.56,
	["wh3_twa06_ogr_inf_maneaters_ror_0"] = 9.02,
	["wh3_twa06_tze_inf_pink_horrors_ror_0"] = 6.56,
	["wh3_twa10_cth_inf_peasant_archers_ror"] = 9.02,
	["wh3_twa10_ogr_inf_gnoblars_ror"] = 6.56,
	["wh3_twa10_tze_inf_blue_horrors_ror"] = 6.56,
	["wh_dlc03_bst_inf_centigors_1"] = 10,
	["wh_dlc03_bst_inf_cygor_0"] = 15,
	["wh_dlc03_bst_inf_cygor_0_summoned"] = 15,
	["wh_dlc03_bst_inf_ungor_raiders_0"] = 9,
	["wh_dlc04_emp_art_hammer_of_the_witches_0"] = 18.04,
	["wh_dlc04_emp_art_sunmaker_0"] = 20.5,
	["wh_dlc04_emp_inf_free_company_militia_0"] = 9,
	["wh_dlc04_emp_inf_silver_bullets_0"] = 10.66,
	["wh_dlc04_emp_inf_stirlands_revenge_0"] = 7.38,
	["wh_dlc04_emp_veh_templehof_luminark_0"] = 9.02,
	["wh_dlc05_wef_cav_glade_riders_0"] = 11,
	["wh_dlc05_wef_cav_glade_riders_1"] = 11,
	["wh_dlc05_wef_cav_glade_riders_1_qb"] = 11,
	["wh_dlc05_wef_cav_hawk_riders_0"] = 7,
	["wh_dlc05_wef_cav_sisters_thorn_0"] = 8,
	["wh_dlc05_wef_cha_female_glade_lord_0"] = 8,
	["wh_dlc05_wef_cha_female_glade_lord_0_qb"] = 8,
	["wh_dlc05_wef_cha_female_glade_lord_1"] = 8,
	["wh_dlc05_wef_cha_female_glade_lord_2"] = 8,
	["wh_dlc05_wef_cha_female_glade_lord_2_qb"] = 8,
	["wh_dlc05_wef_cha_female_glade_lord_3"] = 8,
	["wh_dlc05_wef_cha_glade_lord_0"] = 8,
	["wh_dlc05_wef_cha_glade_lord_1"] = 8,
	["wh_dlc05_wef_cha_glade_lord_2"] = 8,
	["wh_dlc05_wef_cha_glade_lord_3"] = 8,
	["wh_dlc05_wef_cha_orion_0"] = 8,
	["wh_dlc05_wef_cha_waystalker_0"] = 8,
	["wh_dlc05_wef_inf_deepwood_scouts_0"] = 11,
	["wh_dlc05_wef_inf_deepwood_scouts_1"] = 11,
	["wh_dlc05_wef_inf_deepwood_scouts_1_qb"] = 11,
	["wh_dlc05_wef_inf_glade_guard_0"] = 11,
	["wh_dlc05_wef_inf_glade_guard_1"] = 11,
	["wh_dlc05_wef_inf_glade_guard_1_qb"] = 11,
	["wh_dlc05_wef_inf_glade_guard_2"] = 11,
	["wh_dlc05_wef_inf_waywatchers_0"] = 11,
	["wh_dlc06_chs_cav_marauder_horsemasters_0"] = 8,
	["wh_dlc06_dwf_art_bolt_thrower_0"] = 18,
	["wh_dlc06_dwf_art_gob_lobber_0"] = 16.4,
	["wh_dlc06_dwf_cha_master_engineer_ghost_0"] = 8,
	["wh_dlc06_dwf_inf_bugmans_rangers_0"] = 13,
	["wh_dlc06_dwf_inf_ekrund_miners_0"] = 7.38,
	["wh_dlc06_dwf_inf_norgrimlings_ironbreakers_0"] = 7.38,
	["wh_dlc06_dwf_inf_norgrimlings_irondrakes_0"] = 6.56,
	["wh_dlc06_dwf_inf_rangers_0"] = 13,
	["wh_dlc06_dwf_inf_rangers_1"] = 8,
	["wh_dlc06_dwf_inf_ulthars_raiders_0"] = 6.56,
	["wh_dlc06_dwf_veh_skyhammer_0"] = 4.92,
	["wh_dlc06_emp_cha_witch_hunter_boss"] = 4,
	["wh_dlc06_grn_art_hammer_of_gork_0"] = 14.76,
	["wh_dlc06_grn_cav_deff_creepers_0"] = 6.56,
	["wh_dlc06_grn_cav_mogrubbs_marauders_0"] = 6.56,
	["wh_dlc06_grn_cav_teef_robbers_0"] = 4.92,
	["wh_dlc06_grn_inf_da_rusty_arrers_0"] = 6.56,
	["wh_dlc07_brt_art_blessed_field_trebuchet_0"] = 20,
	["wh_dlc07_brt_inf_peasant_bowmen_1"] = 11,
	["wh_dlc07_brt_inf_peasant_bowmen_2"] = 11,
	["wh_dlc08_bst_mon_cygor_boss"] = 5,
	["wh_dlc08_nor_art_hellcannon_battery"] = 9.84,
	["wh_dlc08_nor_cav_marauder_horsemasters_0"] = 8,
	["wh_dlc08_nor_inf_marauder_hunters_0"] = 8,
	["wh_dlc08_nor_inf_marauder_hunters_1"] = 8,
	["wh_dlc08_nor_veh_marauder_warwolves_chariot_0"] = 10,
	["wh_main_brt_art_field_trebuchet"] = 20,
	["wh_main_brt_cav_mounted_yeomen_1"] = 11,
	["wh_main_brt_inf_peasant_bowmen"] = 11,
	["wh_main_chs_art_hellcannon"] = 12,
	["wh_main_chs_cav_marauder_horsemen_0"] = 9,
	["wh_main_chs_cav_marauder_horsemen_1"] = 10,
	["wh_main_dwf_art_cannon"] = 22,
	["wh_main_dwf_art_cannon_malakai"] = 22,
	["wh_main_dwf_art_flame_cannon"] = 10,
	["wh_main_dwf_art_flame_cannon_grudge_reward"] = 10,
	["wh_main_dwf_art_flame_cannon_malakai"] = 10,
	["wh_main_dwf_art_grudge_thrower"] = 20,
	["wh_main_dwf_art_organ_gun"] = 12,
	["wh_main_dwf_art_organ_gun_malakai"] = 12,
	["wh_main_dwf_cha_master_engineer_0"] = 8,
	["wh_main_dwf_inf_ironbreakers"] = 9,
	["wh_main_dwf_inf_irondrakes_0"] = 9,
	["wh_main_dwf_inf_irondrakes_0_grudge_reward"] = 9,
	["wh_main_dwf_inf_irondrakes_2"] = 20,
	["wh_main_dwf_inf_miners_1"] = 9,
	["wh_main_dwf_inf_quarrellers_0"] = 13,
	["wh_main_dwf_inf_quarrellers_1"] = 13,
	["wh_main_dwf_inf_quarrellers_1_grudge_reward"] = 13,
	["wh_main_dwf_inf_thunderers_0"] = 13,
	["wh_main_dwf_veh_gyrobomber"] = 6,
	["wh_main_dwf_veh_gyrobomber_malakai"] = 6,
	["wh_main_dwf_veh_gyrocopter_0"] = 8,
	["wh_main_dwf_veh_gyrocopter_0_malakai"] = 8,
	["wh_main_dwf_veh_gyrocopter_1"] = 9,
	["wh_main_dwf_veh_gyrocopter_1_grudge_reward"] = 20,
	["wh_main_dwf_veh_gyrocopter_1_malakai"] = 9,
	["wh_main_emp_art_great_cannon"] = 22,
	["wh_main_emp_art_helblaster_volley_gun"] = 10,
	["wh_main_emp_art_helstorm_rocket_battery"] = 17,
	["wh_main_emp_art_mortar"] = 19,
	["wh_main_emp_cav_outriders_0"] = 13,
	["wh_main_emp_cav_outriders_1"] = 10,
	["wh_main_emp_cav_pistoliers_1"] = 9,
	["wh_main_emp_cha_witch_hunter"] = 4,
	["wh_main_emp_inf_crossbowmen"] = 13,
	["wh_main_emp_inf_handgunners"] = 13,
	["wh_main_emp_veh_luminark_of_hysh_0"] = 11,
	["wh_main_emp_veh_steam_tank"] = 10,
	["wh_main_grn_art_doom_diver_catapult"] = 18,
	["wh_main_grn_art_goblin_rock_lobber"] = 18,
	["wh_main_grn_cav_forest_goblin_spider_riders_1"] = 8,
	["wh_main_grn_cav_goblin_wolf_chariot"] = 6,
	["wh_main_grn_cav_goblin_wolf_riders_1"] = 8,
	["wh_main_grn_inf_goblin_archers"] = 8,
	["wh_main_grn_inf_night_goblin_archers"] = 8,
	["wh_main_grn_inf_night_goblin_fanatics_1"] = 8,
	["wh_main_grn_inf_orc_arrer_boyz"] = 11,
	["wh_main_grn_inf_savage_orc_arrer_boyz"] = 11,
	["wh_main_nor_cav_marauder_horsemen_0"] = 9,
	["wh_main_nor_cav_marauder_horsemen_1"] = 10,
	["wh_pro04_brt_cav_mounted_yeomen_ror_0"] = 9.02,
	["wh_pro04_bst_inf_cygor_ror_0"] = 12.3,
	["wh_pro04_chs_art_hellcannon_ror_0"] = 9.84,
	["wh_pro04_wef_inf_waywatchers_ror_0"] = 9.02,
}
-- END GENERATED RELOAD TABLE

-- One unit's description for an AMMO / FIRING line: ui id, type, and its
-- current target with that target's melee state (every read pcall'd).
function FOURTH.ammo_describe(u)
	local id, ty = "?", "?"
	pcall(function() id = tostring(u:unique_ui_id()) end)
	pcall(function() ty = tostring(u:type()) end)
	local tgt, tmelee = "none", "?"
	local ok_t, t = pcall(function() return u:current_target() end)
	if ok_t and t ~= nil then
		tgt = "?"
		pcall(function() tgt = tostring(t:type()) end)
		local ok_m, m = pcall(function() return t:is_in_melee() end)
		if ok_m and type(m) == "boolean" then tmelee = m and "true" or "false" end
	end
	return "unit " .. id .. " '" .. ty .. "'", "target='" .. tgt .. "' target_in_melee=" .. tmelee
end

-- Is the unit's current target within the unit's own live missile range?
-- true / false, or nil when a read is unavailable (the state is then left as
-- it was). Returns the distance and the range too, for the log.
function FOURTH.ammo_in_range(u)
	local ok_t, t = pcall(function() return u:current_target() end)
	if not ok_t or t == nil then return false, nil, nil end
	local ok_r, r = pcall(function() return u:missile_range() end)
	local ok_d, d = pcall(function() return u:unit_distance(t) end)
	if not (ok_r and type(r) == "number" and r > 0 and ok_d and type(d) == "number" and d >= 0) then
		return nil, nil, nil
	end
	return d <= r, d, r
end

-- ============================================================================
-- ROUND 128 - THE NOT FIRING SNAPSHOT (READ-ONLY; user question 2026-11-03: why
-- do units pause?). For a ranged unit that is NOT firing, every
-- NOT_FIRING_EVERY_N_POLLS polls, the readable reasons it may be holding fire,
-- logged ONLY when they change (st.why is the last one logged): its target
-- (none, in or out of its own live missile range, in melee, hidden) and the unit
-- itself (in melee, moving, idle, fire-at-will, skirmish, wavering, routing,
-- limbered artillery, out of ammunition). Line of sight has NO read in the API:
-- a pause with every reason here clear points there. '?' = the read is
-- unavailable. Nothing is decided from it.
-- ============================================================================
FOURTH.NOT_FIRING_EVERY_N_POLLS = 4   -- 4 x 250 ms = once a second
function FOURTH.not_firing_snapshot(u, st, now_s, inr, d, r)
	local function b(fn)
		local ok, v = pcall(fn)
		if ok and type(v) == "boolean" then return v and "yes" or "no" end
		return "?"
	end
	local tgt = "none"
	local ok_t, t = pcall(function() return u:current_target() end)
	local t_melee, t_hidden = "-", "-"
	if ok_t and t ~= nil then
		tgt = "?"
		pcall(function() tgt = tostring(t:type()) end)
		t_melee = b(function() return t:is_in_melee() end)
		t_hidden = b(function() return t:is_hidden() end)
	end
	local range_txt = "-"
	if inr == true then range_txt = "in range" elseif inr == false and tgt ~= "none" then range_txt = "OUT of range" end
	local ammo_txt = "?"
	if st.last ~= nil then ammo_txt = (st.last <= 0) and "OUT" or "ok" end
	local key = "target=" .. tgt .. " (" .. range_txt .. ") target_in_melee=" .. t_melee .. " target_hidden=" .. t_hidden
		.. " | self: melee=" .. b(function() return u:is_in_melee() end)
		.. " moving=" .. b(function() return u:is_moving() end)
		.. " idle=" .. b(function() return u:is_idle() end)
		.. " fire_at_will=" .. b(function() return u:is_behaviour_active("fire_at_will") end)
		.. " skirmish=" .. b(function() return u:is_behaviour_active("skirmish") end)
		.. " wavering=" .. b(function() return u:is_wavering() end)
		.. " routing=" .. b(function() return u:is_routing() end)
		.. " limbered=" .. b(function() return u:is_limbered_artillery() end)
		.. " ammo=" .. ammo_txt
	if key == st.why then return end
	st.why = key
	local who = FOURTH.ammo_describe(u)
	local dist_txt = ""
	if d ~= nil and r ~= nil then dist_txt = string.format(" [distance %.1fm, range %.1fm]", d, r) end
	log(string.format("NOT FIRING %s at t=%.2fs: %s%s", who, now_s, key, dist_txt))
end

function FOURTH.ammo_probe(units)
	if units == nil then return end
	local now_s = tick_count * POLL_MS / 1000
	for i = 1, #units do
		local su = units[i]
		local u = su and su.unit
		if u ~= nil then
			local st = FOURTH.ammo[su]
			if st == nil then
				local ok_s, start = pcall(function() return u:starting_ammo() end)
				st = { start = (ok_s and type(start) == "number") and start or 0, firing = false }
				if st.start > 0 then
					local ok_ty, ty = pcall(function() return u:type() end)
					if ok_ty and type(ty) == "string" then st.reload = FOURTH.RELOAD_S[ty] end
				end
				FOURTH.ammo[su] = st
				-- ROUND 130: the same state by ui id, for the firing-flag triggers
				pcall(function() FOURTH.ammo_by_id[tostring(u:unique_ui_id())] = st end)
			end
			if st.start > 0 then
				local inr, d, r = FOURTH.ammo_in_range(u)
				if inr == true and not st.in_range then
					st.in_range = true
					st.in_range_since = now_s
					local who = FOURTH.ammo_describe(u)
					log(string.format("IN RANGE %s at t=%.2fs: target at %.1fm <= missile range %.1fm", who, now_s, d, r))
				elseif inr == false and st.in_range then
					st.in_range = false
					st.in_range_since = nil
					local who = FOURTH.ammo_describe(u)
					-- ROUND 127: a target that DISAPPEARED has no distance or range to
					-- print; formatting them raised, lost this line and skipped the rest
					-- of the army for the poll.
					if d ~= nil and r ~= nil then
						log(string.format("OUT OF RANGE %s at t=%.2fs: target at %.1fm > missile range %.1fm", who, now_s, d, r))
					else
						log(string.format("OUT OF RANGE %s at t=%.2fs: target lost (no current target)", who, now_s))
					end
				end
				-- ROUND 128: the read-only NOT FIRING snapshot (live file only)
				if not st.firing and (tick_count % FOURTH.NOT_FIRING_EVERY_N_POLLS) == 0 then
					FOURTH.not_firing_snapshot(u, st, now_s, inr, d, r)
				end
				local ok_a, now = pcall(function() return u:ammo_left() end)
				if ok_a and type(now) == "number" then
					if st.last ~= nil and now < st.last then
						local was_firing = st.firing
						st.firing = true
						st.last_drop_s = now_s
						local who, aim = FOURTH.ammo_describe(u)
						log(string.format("AMMO %s: %s -> %s of %s at t=%.2fs %s", who, tostring(st.last),
							tostring(now), tostring(st.start), now_s, aim))
						if not was_firing then
							st.first_shot_s = now_s
							st.cast_point_passed = false
							st.why = nil   -- ROUND 128: the next pause is logged fresh
							local lead = "never in range before it"
							if st.in_range_since ~= nil then
								lead = string.format("in range %.2fs before it", now_s - st.in_range_since)
							end
							log(string.format("FIRING ON %s at t=%.2fs (first shot; %s; reload %s) %s", who, now_s,
								lead, st.reload and string.format("%gs", st.reload) or "not in the table", aim))
						end
					elseif st.last ~= nil and now > st.last then
						local who = FOURTH.ammo_describe(u)
						log("AMMO " .. who .. ": " .. tostring(st.last) .. " -> " .. tostring(now)
							.. " of " .. tostring(st.start) .. " - RESUPPLIED (not a shot)")
					end
					st.last = now
				end
				if st.firing then
					if st.reload ~= nil and not st.cast_point_passed
						and (now_s - st.first_shot_s) >= FOURTH.AMMO_CAST_FRACTION * st.reload then
						st.cast_point_passed = true
						local who, aim = FOURTH.ammo_describe(u)
						log(string.format("CAST POINT %s at t=%.2fs: first shot %.2fs + %g x reload %gs (the firing-flag triggers may cast from here) %s",
							who, now_s, st.first_shot_s, FOURTH.AMMO_CAST_FRACTION, st.reload, aim))
					end
					local window = FOURTH.AMMO_OFF_MIN_S
					if st.reload ~= nil and FOURTH.AMMO_OFF_FACTOR * st.reload > window then
						window = FOURTH.AMMO_OFF_FACTOR * st.reload
					end
					if (now_s - st.last_drop_s) > window then
						st.firing = false
						local who = FOURTH.ammo_describe(u)
						log(string.format("FIRING OFF %s at t=%.2fs (no drop for %.2fs > window %.2fs%s)", who, now_s,
							now_s - st.last_drop_s, window,
							(st.reload == nil and ", no reload in the table: the 20 s minimum")
								or (FOURTH.AMMO_OFF_FACTOR * st.reload > FOURTH.AMMO_OFF_MIN_S
									and string.format(" = %g x reload %gs", FOURTH.AMMO_OFF_FACTOR, st.reload))
								or string.format(", the 20 s minimum (%g x reload %gs is shorter)", FOURTH.AMMO_OFF_FACTOR, st.reload)))
					end
				end
			end
		end
	end
end

local function poll_body()
	tick_count = tick_count + 1

	-- Proof of life: if this line is in the log, the repeating timer works.
	if tick_count == 1 then
		log("poll is running (first tick)")
	end

	-- The switch is flipped by right-clicking the ability icon in battle - see the
	-- listener at the bottom of the file. No UI component is created anywhere in
	-- this mod: doing so from a timer or a phase callback is what broke the model
	-- timer in rounds 9-14.

	-- Say something every 10 s whatever the phase, so a silent run is provable
	-- and so we can see whether the timer is still being called at all.
	if (tick_count % 40) == 0 then
		log("tick " .. tostring(tick_count)
			.. " | phase=" .. tostring(bm:get_current_phase_name())
			.. " | conflict=" .. tostring(bm:is_conflict_phase())
			.. " | auto=" .. armed_states_string()
			.. " | tracked=" .. (tracked_units ~= nil and tostring(#tracked_units) or "nil"))
	end

	if (tick_count % HEARTBEAT_EVERY_N_POLLS) == 0 then
		log_heartbeat()
	end

	-- Deferred "did it take effect?" check, for the case where a call was
	-- accepted but the ability did not go on cooldown immediately.
	if pending_verify ~= nil and tick_count >= pending_verify.at_tick then
		local pv = pending_verify
		pending_verify = nil

		if tracked_units ~= nil then
			for i = 1, #tracked_units do
				local u = tracked_units[i].unit
				if u ~= nil and u:unique_ui_id() == pv.ui_id then
					local _, still = pcall(function()
						return u:can_perform_special_ability(pv.key)
					end)
					log("  verify 1 s later        : can_perform = " .. tostring(still))
				end
			end
		end
	end

	-- Nothing to do during deployment or after the battle is decided.
	if not bm:is_conflict_phase() then return end

	-- First poll after contact: build the list.
	if tracked_units == nil then
		rebuild_unit_list()
		return
	end

	-- THE PERIODIC RE-LIST (this build): mid-battle arrivals - summons,
	-- Tzeentch splits, transformations - must become watched, scanned and
	-- selection-registered exactly like a starting unit, so the watch list is
	-- re-listed every RELIST_EVERY_N_POLLS polls (40 x 250 ms = 10 s).
	-- rebuild_unit_list is additive: existing units are untouched, only
	-- genuinely new ones are added (and units the engine no longer returns
	-- are dropped), and it speaks ONE line only when the set actually
	-- changed. No return here: the refreshed list is processed on this very
	-- tick.
	if (tick_count % RELIST_EVERY_N_POLLS) == 0 then
		rebuild_unit_list()
	end

	local do_redetect = (tick_count % REDETECT_EVERY_N_POLLS) == 0
	local do_fallback_rescan = (tick_count % FALLBACK_RESCAN_EVERY_N_POLLS) == 0

	-- EVERY unit a fire proves gone THIS TICK is collected here and dropped
	-- AFTER the loop (never mid-iteration, never breaking the walk): hitting a
	-- death must not cost the rest of the army its tick, and multiple deaths in
	-- one tick are all collected and all dropped.
	local gone_ids = {}

	-- ITEM 12 - THE DEFERRED ACTIVE-SET REFRESH. The per-unit re-scan block
	-- below (the identity-moved rescan and the 60 s fallback rescan both run
	-- through it) used to call the active-set recompute DIRECTLY, so a tick
	-- that re-scanned N units recomputed the set N times - each a pass
	-- over units x owned markers. They now only RAISE this flag; ONE call
	-- after the loop - and after the post-loop drop walk, so it observes the
	-- FINAL state - recomputes the set exactly ONCE per tick. Membership is
	-- unchanged: by the time the deferred call reads, exactly the same inputs
	-- the old last in-loop refresh saw are in place.
	local active_refresh_pending = false

	-- ROUND 125: the read-only ammo probe (above poll_body) - its own pcall, so
	-- nothing it meets can cost the army its tick.
	pcall(FOURTH.ammo_probe, tracked_units)

	for i = 1, #tracked_units do
		local script_unit = tracked_units[i]
		local unit = script_unit and script_unit.unit

		-- Only look at units still alive on the field.
		if unit ~= nil and unit:number_of_men_alive() > 0 then
			-- The routing guard's ONE read for this unit this poll (section
			-- 7d): every ability below reuses this same value.
			local routing = unit_is_routing(unit)
			local ui_id = unit:unique_ui_id()
			local ability_key = target_key_by_unit[ui_id]

			-- Nothing of ours on this unit yet. THE IDENTITY WATCH (item
			-- 3.4): at the old 4 s cadence the cheap identity read runs
			-- INSTEAD of a full scan - unit_identity (section 4), one
			-- pcall'd battle_unit:type() - and the unit is re-scanned
			-- when that value CHANGES (a transformation / a mount
			-- moves the land_units key, so a loadout that gained
			-- abilities mid-battle is picked up and its new abilities
			-- arm and fire). ITEM 5: a nil read is NEVER cached and the
			-- unit's very first check merely records - so a failed FIRST
			-- check (no cached value) is re-scanned as soon as a later
			-- check reads a good value, which is exactly the poisoned-
			-- first-check case that used to go unseen for up to 60 s. A
			-- unit that has never been checked is not re-scanned on its
			-- first good read: the unit was already scanned when it
			-- entered the watch list. THE SLOW SAFETY FALLBACK: one
			-- full scan every 60 s whatever the identity says, so an
			-- unreadable or unchanging identity degrades to the old
			-- behaviour, just far rarer.
			if ability_key == nil and (do_redetect or do_fallback_rescan) then
				local id_text = tostring(ui_id)
				local old_identity = identity_by_unit[id_text]
				local new_identity = unit_identity(unit)
				-- ITEM 5: NEVER cache a nil read. A transient failure must
				-- not erase the last good value, or the next good read would
				-- compare against nil and never look like a change. A unit's
				-- per-unit checked flag (identity_checked) says it has been
				-- identity checked at least once regardless of outcome, so a
				-- failed first check can still be turned into a re-scan by
				-- the next good read.
				local first_identity_check = (identity_checked[id_text] == nil)
				identity_checked[id_text] = true
				if new_identity ~= nil then
					identity_by_unit[id_text] = new_identity
				end

				-- ITEM 5 RESCAN RULE: re-scan when this unit HAS been checked
				-- before and the new read is good AND either the cache is
				-- still empty (its first read failed and this is the first
				-- good one) or the value actually moved. A unit's very first
				-- check merely records. A nil read changes nothing and never
				-- re-scans; the slow fallback below is the late-attachment
				-- insurance either way.
				local identity_moved = (not first_identity_check
					and new_identity ~= nil
					and (old_identity == nil or new_identity ~= old_identity))
				local rescan = identity_moved or do_fallback_rescan

				if rescan then
					local found, all_keys = scan_unit_abilities(unit)
					owned_keys_by_unit[id_text] = our_keys_of(all_keys)   -- refresh the owned-key cache
					-- item 1.3: the learned keys change this unit's
					-- owned-ability list, so rebuild it too...
					owned_abilities_by_unit[id_text] =
						owned_abilities_of(owned_keys_by_unit[id_text])
					-- ...and tell item 1.4: the owned keys were just
					-- learned, so the active set (the UI tick's
					-- badge paths) must see them at once. ITEM 12:
					-- only RAISE the flag - the ONE refresh for this
					-- tick runs after the loop, so N re-scans cost
					-- ONE refresh instead of N.
					active_refresh_pending = true
					-- ONE line, and ONLY when the re-scan discovered
					-- something of ours - completely silent otherwise
					-- (a re-scan that finds nothing writes nothing).
					if found ~= nil then
						target_key_by_unit[ui_id] = found
						ability_key = found
						local why = "fallback rescan"
						if identity_moved then
							why = "identity changed (" .. tostring(old_identity)
								.. " -> " .. tostring(new_identity) .. ")"
						end
						log("re-scan: unit " .. tostring(ui_id) .. " " .. why
							.. " - keys: " .. table.concat(all_keys, ", "))
					end
				end
			end

			-- One pass per ability (section 1): its own per-UNIT switch, its
			-- own trigger, then the readiness gate and the short guard.
			-- ITEM 1.3: iterate only the markers THIS unit OWNS - the list
			-- the scan cached (owned_abilities_by_unit, section 2), mapped
			-- from the owned DB keys and variant-deduped, so a unit carrying
			-- one of three abilities costs ONE evaluation instead of three.
			-- A unit whose owned-key cache is UNKNOWN (nil - never scanned)
			-- falls back to the FULL table, exactly like today, so no unit
			-- is ever silently skipped.
			local unit_abilities = owned_abilities_by_unit[tostring(ui_id)]
			if unit_abilities == nil then
				unit_abilities = ABILITIES
			end
			for _, ability in ipairs(unit_abilities) do

				-- THE PER-UNIT SWITCH: this (unit, ability) pair must be
				-- armed. Nothing fires for a unit the player has not armed -
				-- two units carrying the same ability are independent.
				if is_armed(unit, ability.marker) then
					-- ITEM 8 (critique-2): PER-ENTRY DISPATCH. The old if/elseif
					-- chain over ability.trigger is gone: the entry carries its own
					-- evaluate(unit, routing), wired at load to its trigger's
					-- evaluator (section 7g), and this ONE call is the whole
					-- dispatch. It yields the attempt's reason - exactly what the
					-- chain used to leave in this variable (nil = condition unmet).
					-- BLOCK 2: the ally-target slot is CLEARED before every
					-- evaluate; an ally-targeting evaluator (Glorious Death)
					-- fills it, and the cast below passes it - so a self-cast
					-- can never inherit a stale ally.
					FOURTH.cast_target = nil
					FOURTH.gd_ally = nil
					FOURTH.vm_ally = nil
					FOURTH.mtl_ally = nil
					FOURTH.ws_ally = nil
					FOURTH.wa_ally = nil
					FOURTH.bs_ally = nil
					FOURTH.edr_ally = nil
					FOURTH.eg_enemy = nil
					FOURTH.eg_arm = nil
					FOURTH.eg_caster_su = nil
					FOURTH.eg_ground = nil
					FOURTH.eg_melee_only = nil
					-- THE SUMMON ROUND (harness 102): the self-summon arm and the two
					-- non-commander enemy modes are cleared before EVERY evaluate, so no
					-- ability can inherit another's flag, target or cast mode.
					FOURTH.ss_self = nil
					FOURTH.ss_caster_su = nil
					-- TZ'ARKAN (this round): the self-transform slot is cleared
					-- before EVERY evaluate, like every other cast slot.
					FOURTH.tz_self = nil
					FOURTH.tz_caster_su = nil
					FOURTH.eg_noncommander = nil
					FOURTH.eg_infantry = nil
					FOURTH.eg_mode = nil
					FOURTH.ad_enemy = nil
					FOURTH.ad_caster_su = nil
					FOURTH.ad_air_only = nil
					FOURTH.ad_no_melee = nil
					FOURTH.ab_ally = nil
					FOURTH.ab_caster_su = nil
					FOURTH.ab_ally_su = nil
					FOURTH.ab_family = nil
					FOURTH.ab_filter = nil
					FOURTH.ab_infinite = nil
					-- ROUND 130: the Restock! pick and the aura bound, cleared/set per entry
					FOURTH.ammo_claim_id = nil
					FOURTH.fa_bound_m = ability.aura_m
					-- THE ALLY-AWARE HEALTH FAMILY (this round): the chosen
					-- unit, its fresh handles and the cast mode are cleared
					-- before EVERY evaluate, so no entry can inherit another's
					-- ally, ground flag or self-aura flag.
					FOURTH.ah_ally = nil
					FOURTH.ah_ally_su = nil
					FOURTH.ah_chosen = nil
					FOURTH.ah_caster_su = nil
					FOURTH.ah_ground = false
					FOURTH.ah_selfaura = false
					-- CLASS A (harness 97): the CURRENT ability's own 70% enemy-cast bound and
					-- its marker, so the shared enemy picker tests and logs against THIS entry's
					FOURTH.eg_range_m = ability.range_m
					-- ROUND 135: the entry's enemy target class (nil = any enemy)
					FOURTH.eg_class = ability.target_class
					-- AN UNBOUNDED ENTRY (harness 102): its game row declares
					-- target_intercept_range = -1.0 - no real range to take 70% of.
					FOURTH.eg_no_bound = (ability.unbounded == true)
					FOURTH.eg_marker = ability.marker
					-- ROUND 107: the AIR-DROP family's own slots - its 70% bound
					-- (7 m from the row's 10 m), its marker, and the two usage
					-- flags the row declares.
					FOURTH.ad_range_m = ability.range_m
					FOURTH.ad_marker = ability.marker
					FOURTH.ad_air_only = (ability.air_only == true)
					FOURTH.ad_no_melee = (ability.no_melee == true)
					-- CLASS B (harness 98): the CURRENT ability's own 70% ALLY bound and
					-- its marker, so the shared ally picker tests and logs against THIS
					FOURTH.ab_range_m = ability.range_m
					FOURTH.ab_marker = ability.marker
					-- THE ALLY-AWARE HEALTH FAMILY (this round): the reach THIS
					-- entry's picker tests - its own aura radius (aura_m) when the
					-- effect is an area, otherwise its own cast range - plus the
					-- word the log uses for it.
					FOURTH.ah_range_m = ability.aura_m or ability.range_m
					FOURTH.ah_range_word = (ability.aura_m ~= nil) and "aura" or "cast range"
					FOURTH.ah_marker = ability.marker
					local reason = ability.evaluate(unit, routing)

					if reason ~= nil then
						-- ROUND 114: the readiness read, every hold/gate and the cast
						-- itself now live in ONE function (FOURTH.try_pair), because
						-- the air-drop fast pass has to cast through the SAME gates
						-- rather than a copy of them. It answers "gone" when the unit
						-- must be dropped after this tick's walk.
						if FOURTH.try_pair(script_unit, unit, ability, ui_id, ability_key,
							reason, gone_ids) == "gone" then
							break
						end
					end
				end
			end
		end
	end
	-- DROP EVERY COLLECTED id via the ONE drop routine (items 2 + 13). Done
	-- here, AFTER the per-unit loop: the tracked list is never mutated
	-- mid-iteration (the routine's own scan + table.remove run freely now) and
	-- a death never costs the rest of the army its tick.
	for g = 1, #gone_ids do
		drop_unit_by_ui_id(gone_ids[g])
	end

	-- ITEM 12 - THE ONE (DEFERRED) ACTIVE-SET REFRESH of this tick. It runs
	-- here, AFTER the per-unit loop AND after the drop walk, so it observes the
	-- FINAL state - any owned-key learning done in the loop AND any unit the
	-- walk just dropped. A tick that re-scanned nothing raises nothing and
	-- recomputes nothing (exactly as before); a tick that re-scanned N units
	-- recomputes the set ONCE instead of N times. Silent unless the membership
	-- actually moved.
	if active_refresh_pending then
		refresh_active_abilities()
	end
end


-- An error escaping a timer callback does not merely skip that tick: the battle
-- model's timer driver aborts before re-arming itself, which kills EVERY
-- repeating callback in the battle for the rest of the fight
-- (lib_timer_manager.lua, "timer_manager_battle_callback"). So the body is
-- wrapped, and the first few errors are logged rather than swallowing the battle.
local poll_errors = 0

local function poll()
	local ok, err = pcall(poll_body)
	if not ok then
		poll_errors = poll_errors + 1
		if poll_errors <= 3 or (poll_errors % 40) == 0 then
			log("POLL ERROR #" .. tostring(poll_errors) .. " (poll continues): "
				.. tostring(err))
		end
	end
end


-- ============================================================================
-- ============================================================================
-- 8b. THE ABILITY ICON ITSELF: THE RIGHT-CLICK TOGGLE, AND THE FEEDBACK
--
-- The control the player uses is a RIGHT-CLICK ON THE ABILITY'S OWN ICON, and it
-- needs two halves, because the engine only routes a mouse button to a component
-- whose layout declares it (no vanilla layout declares rclick - 0 of the 907 in
-- ui3.pack, which is why right-clicking an ability icon has never done anything):
--
--   * the layout half - shipped in this pack as ui/battle ui/hud_battle.twui.xml
--     and ui/common ui/land_unit_card.twui.xml - adds CA's own
--     ContextEventBroadcaster callback, whose documented trigger list includes
--     rclick, to every component that draws a unit ability icon;
--   * this half listens for whatever comes back and flips the switch.
--
-- The engine's own script says where those icons are: lib_battle_ui.lua's
-- highlight_unit_abilities() walks battle_orders -> orders_parent ->
-- behaviour_parent, takes child 0 of each slot, and calls
-- InterfaceFunction("AbilityKeyForScript") to learn which ability a button shows.
-- ============================================================================

local logged_no_parent = false

-- (The single button reference, watch chain and feedback flag that used to sit
--  here are per ability now - ability_state[marker].button / .watch_chain /
--  .feedback_on, section 2.)

-- THE FEEDBACK: a plain image swap on the ability icon. Static - no pulse, no blink.
-- The icon slot is the one the vanilla layout marks with icon_index = 8 (round 21's layout read).
-- (ROUND 86: the vestigial ICON_INDEX / original_icon / read_icon / original_state
--  locals that used to sit here were DEAD - the read_icon helper and the two
--  original_* savers were never called or read anywhere, and the icon-swap
--  feedback never used them. They were removed to free local-ceiling slots for
--  GLORIOUS_DEATH_RANGE_M (section 1). The reading copy never carried them.)

-- THE BADGES - one per ability (option B, done right). Rounds 32-33 measured two things: an
-- engine-owned ability button does not draw children, and writing to it rebuilds it. So each
-- badge is created on the button's own ancestor (a plain container, the kind that demonstrably
-- draws components we create). Reading the button is safe; only writing to it is fatal.
--
-- Each ability has ONE badge component (the id from the table in section 1: zz_auto_badge for
-- Deadly Onslaught, zz_auto_badge_fs for Foe-Seeker), created HIDDEN and SHOWN only while ITS
-- ability is positively confirmed on the dial (the ui_tick test at the bottom of the file).
-- Its letter shows the collective switch for this ability (ONE selected unit: that unit's own
-- switch; SEVERAL: A only while every selected owner is armed) - "A" = armed/auto, "M" =
-- manual - and a click on it flips the selected owners' pairs (the checkbox rule, section 10):
-- the only control.
-- The components and flags live in ability_state[marker] (section 2).
local badge_parent = nil
local track = false          -- no computed tracking: the frames of reference do not match
                             -- (round 42). Position is the hand-tuned offset above.
local BADGE_X, BADGE_Y = -865, -209   -- the spot tuned by hand in-game (round 41), used as-is.
                                     -- MINUS is left/up, PLUS is right/down, from the bottom-centre
                                     -- dock of the badge's parent. Each ability's badge adds its
                                     -- own ox/oy from the table in section 1 (foe_seeker:
                                     -- +70,+30 - the measured top-slot-to-45-degree step), so a
                                     -- re-tune of these two numbers carries Foe-Seeker along.

-- THE MEASURED WHEEL (this build): the visible wheel is a circle centred
-- (95,944) radius 99 with six slots ~45 degrees apart; the six positions
-- below were measured over two battles. Deadly Onslaught sat on slot 1 (top)
-- in every observation - the slot the hand-tuned BADGE_X/BADGE_Y above were
-- tuned for - so slot 1 is the reference (WHEEL_TOP_X/WHEEL_TOP_Y).
--
-- WHICH SLOT AN ABILITY SITS ON IS ITS BAR POSITION: the claimed button's
-- ORDINAL among the key-bearing children of its parent bar (button_parent -
-- where the claimed buttons actually live) equals its wheel slot number,
-- 1-based. The claim walk counts it into slot_index (bar_ordinal_for,
-- section 8b), and every badge's offset is then
--     BADGE_X + (WHEEL_SLOT[k][1] - WHEEL_TOP_X),
--     BADGE_Y + (WHEEL_SLOT[k][2] - WHEEL_TOP_Y)
-- - that slot's delta from the top slot - so an ability on any of the six
-- slots gets the hand-tuned pair moved to its slot, and re-tuning the Deadly
-- Onslaught badge (zz_badge_set) still carries every other ability along.
-- Only when k is unknown (no claim yet, the bar unreadable, or more than six
-- key-bearing children - unexpected) does the badge fall back to section 1's
-- ox/oy pair, and that use is logged.
local WHEEL_TOP_X, WHEEL_TOP_Y = 96, 845

-- The six measured wheel slot positions, in slot order: 1 top (96,845),
-- 2 the 45-degree slot, 3 right, 4 the -45-degree slot, 5 the 135-degree
-- slot, 6 left. WHEEL_SLOT[k] is where the ability whose bar position is k
-- sits on the wheel.
local WHEEL_SLOT = {
	{ 96, 845 },      -- 1 - top (the hand-tuned reference slot)
	{ 166, 875 },     -- 2 - 45 degrees
	{ 194, 947 },     -- 3 - right
	{ 162, 1017 },    -- 4 - -45 degrees
	{ 28, 877 },      -- 5 - 135 degrees
	{ 2, 949 },       -- 6 - left
}

-- THE DEFERRED, STEPPED BADGE CREATION. The scan walk only records the button
-- and raises pending_badge[marker]; the badge is built HERE, on the ui tick,
-- one engine call group at a time, and every step is pcall'd and bracketed by
-- its own log lines ("step N <name>", then "step N ok" / "step N err: ..."),
-- so the last line of a crashed log names the step that died. A failed step
-- leaves the badge ABSENT (state.badge = nil) and the next tick tries again,
-- up to MAX_BADGE_ATTEMPTS per claim; after that the marker gives up until
-- the dial rebuilds (a fresh claim resets the budget).
--
-- The calls themselves are the stable single-badge path's, unchanged: the
-- same parent walk to hud_battle, the same template layout, the same
-- docking/resize/art-blank/SetText/place calls - only split into steps.
local MAX_BADGE_ATTEMPTS = 3

-- THE BADGE OFFSET, DERIVED FROM THE CLAIMED BUTTON'S BAR POSITION (this
-- build). slot_index[marker] is the claimed button's 1-based position among
-- the key-bearing children of its parent bar - which two measured battles
-- proved IS the wheel slot. When it is a slot number 1..6, the offset is
-- BADGE_X/BADGE_Y - the hand-tuned pair for the measured TOP slot (slot 1,
-- WHEEL_TOP_X/WHEEL_TOP_Y) - shifted by this slot's delta from that top slot,
-- through the static WHEEL_SLOT table above. Only when k is unknown (never
-- claimed, the bar unreadable, or more than six key-bearing children) does
-- it fall back to section 1's ox/oy pair (onslaught BADGE_X/BADGE_Y,
-- foe_seeker BADGE_X+70/BADGE_Y+30); the callers log which one was used.
-- Returns: ox, oy, wheel (slot number, nil on fallback), slot_x, slot_y.
local function badge_offsets_for(marker)
	local ability = ability_for(marker)
	if ability == nil then return nil end
	local k = slot_index[marker]
	if k ~= nil and k >= 1 and k <= 6 then
		local slot = WHEEL_SLOT[k]
		if slot ~= nil then
			return BADGE_X + (slot[1] - WHEEL_TOP_X), BADGE_Y + (slot[2] - WHEEL_TOP_Y),
				k, slot[1], slot[2]
		end
	end
	return BADGE_X + ability.ox, BADGE_Y + ability.oy, nil, nil, nil
end

-- One instrumented step: opening breadcrumb, the step's engine calls inside a
-- pcall, then ok/err. Returns true when the step completed.
local function badge_step(marker, step_no, step_name, fn)
	log("badge " .. marker .. ": step " .. tostring(step_no) .. " " .. step_name)
	local ok, err = pcall(fn)
	if ok then
		log("badge " .. marker .. ": step " .. tostring(step_no) .. " ok")
	else
		log("badge " .. marker .. ": step " .. tostring(step_no) .. " err: " .. tostring(err))
	end
	return ok
end

-- THE LAYOUT NUDGE (this build): THE ONE LETTER WRITE below is this
-- function's only caller, and it runs immediately after every REAL letter
-- write - creation step 5, the badge-click/feedback path and the selection
-- refresh all write through that one primitive - asking the engine to
-- re-run its layout/repaint pass for the badge AND for the parent it was
-- created on (the same badge_parent the placement code uses); when no
-- parent is known the badge alone is nudged. Layout() is the only
-- redraw-adjacent call the game exposes to script, so it is the one lever
-- against the delay between a letter write and its pixels. Both calls are
-- pcall'd: an error is swallowed and never aborts a letter write - the
-- outcome is reported on the letter's own log line
-- ('layout ok=<true|false>', the failing side named). Never called on a
-- cache hit: a write that did not happen gets no nudge and no line.
local function nudge_badge_layout(state)
	local ok_badge = pcall(function() state.badge:Layout() end)
	local ok_parent = true
	if badge_parent ~= nil then
		ok_parent = pcall(function() badge_parent:Layout() end)
	end
	if ok_badge and ok_parent then return true end
	if not ok_badge then return false, "badge" end
	return false, "parent"
end

-- THE ONE LETTER WRITE (this build): every path that moves a badge's letter
-- goes through this function and NOTHING else writes a badge's text - the
-- SetText call and the layout nudge are one primitive, so a caller cannot
-- write the letter without repainting it. (Before this build the nudge
-- lived at each call site; a path that forgot it produced exactly the bare,
-- outcome-less letter lines the battle log kept showing, so the last
-- un-nudged writer is now structurally impossible.) state.last_letter is
-- the one shared cache and moves only when SetText did not raise, so a
-- failed write does not poison it and the next path retries. Returns the
-- SetText outcome plus the nudge's outcome, so the caller's line can carry
-- both.
local function write_badge_letter(state, letter)
	local ok_text = pcall(function() state.badge:SetText(letter) end)
	if ok_text then state.last_letter = letter end
	local ok_layout, layout_err = nudge_badge_layout(state)
	return ok_text, ok_layout, layout_err
end

-- THE DISCARD (this build): the one way a created badge leaves the engine
-- tree. Dropping the Lua reference does NOT remove a created component - it
-- stays parented to hud_battle forever, and a systematic-failure state would
-- leak one doomed component per tick (every retry creates one more). Every
-- site that abandons a created-but-unfinished badge - a failed creation
-- step, or a creation attempt that raised mid-way - calls this instead of
-- clearing the reference directly: with the reference live and the component
-- supporting Destroy, the engine call is made inside a pcall (an engine-side
-- refusal is swallowed and logged, never raised into the retry path), and
-- the reference is cleared whatever happened - the badge is dead to this
-- code either way. NEVER called on a placed, working badge: only the
-- discard-on-failure sites and the create-attempt cleanup.
local function discard_badge(state)
	if state == nil or state.badge == nil then return end
	local ok_has, has_destroy = pcall(function() return state.badge.Destroy ~= nil end)
	if ok_has and has_destroy then
		local ok_destroy, destroy_err = pcall(function() state.badge:Destroy() end)
		if not ok_destroy then
			log("badge discard: Destroy raised: " .. tostring(destroy_err))
		end
	end
	state.badge = nil
end

local function create_badge(marker)
	local state = ability_state[marker]
	local ability = ability_for(marker)
	if state == nil or ability == nil or state.button == nil or state.badge ~= nil then return false end

	-- STEP 1 - create: walk up to hud_battle (the proven parent) and create
	-- the component there. Same walk, same template as the stable path.
	if not badge_step(marker, 1, "create", function()
		local node = state.button
		for _ = 1, 8 do
			local ok_id, id = pcall(function() return node:Id() end)
			if ok_id and tostring(id) == "hud_battle" then break end
			local ok_p, parent = pcall(function() return node:Parent() end)
			if not ok_p or parent == nil then break end
			local ok_w, wrapped = pcall(function() return UIComponent(parent) end)
			if not ok_w or wrapped == nil then break end
			node = wrapped
		end
		badge_parent = node
		state.badge = UIComponent(badge_parent:CreateComponent(ability.badge,
			"ui/templates/zz_auto_badge"))
		if state.badge == nil then error("CreateComponent returned nothing", 0) end
	end) then
		state.badge = nil
		return false
	end
	local ok_cid, pid = pcall(function() return badge_parent:Id() end)
	log("badge [" .. marker .. "]: created on '" .. tostring(ok_cid and pid or "?")
		.. "' (not on the ability button)")

	-- STEP 2 - dock the fresh component to the top-left of its parent.
	if not badge_step(marker, 2, "dock", function()
		state.badge:SetDockingPoint(0)
	end) then
		discard_badge(state)
		return false
	end

	-- STEP 3 - resize: room for the letter.
	if not badge_step(marker, 3, "resize", function()
		state.badge:Resize(24, 24)
	end) then
		discard_badge(state)
		return false
	end

	-- STEP 4 - blank art: the letter carries the look, so the template's own
	-- title-bar art is blanked on every slot (0-4). A failed art WRITE fails
	-- the step; a failed read is logged as '?' and does not (stable's rule).
	if not badge_step(marker, 4, "blank art", function()
		for i = 0, 4 do
			state.badge:SetImagePath("ui/zz_auto/blank.png", i)
			local ok_r, rep = pcall(function() return state.badge:GetImagePath(i) end)
			log("   badge [" .. marker .. "] art slot " .. i .. " -> '"
				.. tostring(ok_r and rep or "?") .. "'")
		end
	end) then
		discard_badge(state)
		return false
	end

	-- STEP 5 - SetText: the letter is supplied here (our copy of a vanilla
	-- text layout; SetText exists, SetTextColour does not). The letter shows
	-- the COLLECTIVE armed state for this ability (ONE selected unit: exactly
	-- the old read - the single unit's own flag; SEVERAL: A only while every
	-- selected unit that owns the ability is armed), and the write - the
	-- SetText call, its layout nudge and the state.last_letter cache update
	-- - goes through THE ONE LETTER WRITE like every later write, so this
	-- first write cannot repaint any differently from the others. A SetText
	-- that raises still fails this step (the badge is discarded and the
	-- next tick retries), so ok_text is always true by the time the line is
	-- logged.
	if not badge_step(marker, 5, "SetText", function()
		local letter = collective_armed(marker) and "A" or "M"
		local ok_text, ok_layout, layout_err = write_badge_letter(state, letter)
		if not ok_text then error("SetText raised - discarding the badge", 0) end
		local ok_g, got = pcall(function() return state.badge:GetText() end)
		log("   badge [" .. marker .. "] set text ok=true engine reports='"
			.. tostring(ok_g and got or "?") .. "' layout ok=" .. tostring(ok_layout)
			.. (layout_err and (" (" .. layout_err .. ")") or ""))
	end) then
		discard_badge(state)
		return false
	end

	-- STEP 6 - place: HIDDEN AT BIRTH first (so a discarded badge can never
	-- linger on screen), then the stable's proven placement - dock point 8
	-- (bottom-centre) and THIS ability's own offset: derived from the bar
	-- position its button was claimed at (badge_offsets_for -> WHEEL_SLOT),
	-- or section 1's fallback pair when no bar position could be determined -
	-- and which one was used is logged.
	if not badge_step(marker, 6, "place", function()
		local ox, oy, wheel, sx, sy = badge_offsets_for(marker)
		state.badge_shown = false
		state.badge:SetVisible(false)
		state.badge:SetDockingPoint(8)                 -- 8 = bottom-centre
		state.badge:SetDockOffset(ox, oy)
		badge_parent:Layout()
		state.placed = true
		state.applied_ox, state.applied_oy = ox, oy
		local ok_pid, pid2 = pcall(function() return badge_parent:Id() end)
		if wheel ~= nil then
			log("badge " .. marker .. ": placed bottom-centre of '" .. tostring(ok_pid and pid2 or "?")
				.. "' (offset " .. tostring(ox) .. "," .. tostring(oy) .. ") [wheel slot "
				.. tostring(wheel) .. " (" .. tostring(sx) .. "," .. tostring(sy) .. ")] ok=true")
		else
			log("badge " .. marker .. ": using fallback offset ("
				.. tostring(ox) .. "," .. tostring(oy) .. ")")
			log("badge " .. marker .. ": placed bottom-centre of '" .. tostring(ok_pid and pid2 or "?")
				.. "' (offset " .. tostring(ox) .. "," .. tostring(oy) .. ") [fallback] ok=true")
		end
	end) then
		discard_badge(state)
		return false
	end
	return true
end

local function button_xy(button)
	if button == nil then return nil, nil end
	local ok, a, b = pcall(function() return button:Position() end)
	if ok and type(a) == "number" and type(b) == "number" then return a, b end
	return nil, nil
end

local function place_badge(marker)
	local state = ability_state[marker]
	local ability = ability_for(marker)
	if state == nil or state.badge == nil or ability == nil then return end

	-- The badge's own offset (this build): DERIVED FROM THE CLAIMED BUTTON'S
	-- BAR POSITION - badge_offsets_for reads slot_index (the 1-based position
	-- among the key-bearing children of the claimed button's parent bar, which
	-- IS the wheel slot) and moves the hand-tuned pair by that slot's delta
	-- from the measured top slot; only when no bar position is known does it
	-- fall back to section 1's ox/oy pair.
	local ox, oy, wheel, sx, sy = badge_offsets_for(marker)

	-- TRACK MODE (round 40): the two numbers above stop being "where on the bar" and become the
	-- constant delta from the ability button's OWN position, recomputed every tick. Tune the delta
	-- once with the console while tracking, and the badge follows that icon - and, per ability, its
	-- own icon, since each badge is created for its own button.
	if track then
		local bx, by = button_xy(state.button)
		if bx ~= nil then
			pcall(function() state.badge:SetDockOffset(bx + ox, by + oy) end)
		end
		return
	end

	-- Re-place when the offset has MOVED (a fresh claim can bring a new slot),
	-- not only the first time: state.applied_ox/applied_oy remember what is on
	-- screen, so an unchanged offset stays quiet.
	if state.placed and state.applied_ox == ox and state.applied_oy == oy then return end
	-- AI General's proven configuration, and nothing cleverer than it: dock the created component to
	-- the BOTTOM-CENTRE of the bar and give it one offset. Round 38 proved the engine both reinterprets
	-- offsets and misreports the component's position, so there is nothing to steer by - one shot, and
	-- the numbers above are the only knobs left.
	pcall(function() state.badge:SetDockingPoint(8) end)                 -- 8 = bottom-centre
	local ok_o = pcall(function() state.badge:SetDockOffset(ox, oy) end)
	pcall(function() badge_parent:Layout() end)
	state.placed = true
	state.applied_ox, state.applied_oy = ox, oy
	if wheel ~= nil then
		log("badge " .. marker .. ": placed bottom-centre of '" .. tostring(badge_parent:Id())
			.. "' (offset " .. tostring(ox) .. "," .. tostring(oy) .. ") [wheel slot "
			.. tostring(wheel) .. " (" .. tostring(sx) .. "," .. tostring(sy) .. ")] ok=" .. tostring(ok_o))
	else
		log("badge " .. marker .. ": using fallback offset ("
			.. tostring(ox) .. "," .. tostring(oy) .. ")")
		log("badge " .. marker .. ": placed bottom-centre of '" .. tostring(badge_parent:Id())
			.. "' (offset " .. tostring(ox) .. "," .. tostring(oy) .. ") [fallback] ok="
			.. tostring(ok_o))
	end
end

-- Re-place every ability's badge from the current BADGE_X/BADGE_Y (the console
-- hooks call this, so a re-tune of the Deadly Onslaught badge carries Foe-Seeker).
local function replace_all_badges()
	for _, ability in ipairs(ABILITIES) do
		local state = ability_state[ability.marker]
		if state ~= nil then
			state.placed = false
			pcall(place_badge, ability.marker)
		end
	end
end
local function badge_visible(marker, on)
	local state = ability_state[marker]
	if state == nil or state.badge == nil then return end
	state.badge_visible_state = on    -- legacy bookkeeping; the letter cache is state.last_letter now
	-- THE LETTER IS THIS PATH'S WHOLE JOB - it must NOT touch visibility any
	-- more. The unconditional SetVisible(true) that used to sit here is one
	-- of the paths that left a stale badge visible while its marker was not
	-- on the dial (a card click or a toggle re-showed a badge the tick had
	-- hidden). Visibility now belongs to the ui tick's claimed-set logic
	-- alone, which re-applies the desired state on every single tick.
	-- THE CACHE (this build): the letter line happens ONLY when the desired
	-- letter differs from state.last_letter - the one shared cache every
	-- letter write updates - so a path that calls this with a letter the
	-- badge already shows is completely silent. A changed letter goes
	-- through THE ONE LETTER WRITE (SetText plus the layout nudge in one
	-- primitive) so the engine repaints it sooner and no caller can skip the
	-- nudge; a cache hit writes nothing and nudges nothing.
	local letter = on and "A" or "M"
	if state.last_letter == letter then return end
	local ok_t, ok_layout, layout_err = write_badge_letter(state, letter)
	log("   badge [" .. marker .. "] letter='" .. letter .. "' (auto "
		.. (on and "ON" or "OFF") .. ") layout ok=" .. tostring(ok_layout)
		.. (layout_err and (" (" .. layout_err .. ")") or "")
		.. " visible=" .. tostring(state.badge_shown == true)
		.. " text=" .. tostring(ok_t))
end

-- THE LETTER CACHE AND THE ONE LETTER WRITE (this build). The desired letter
-- is the COLLECTIVE armed state for this ability (collective_armed, section
-- 4): ONE selected unit - exactly the single unit's armed flag, as before;
-- SEVERAL selected units - "A" only while EVERY selected unit that owns the
-- ability is armed, "M" the moment any member is off or none owns it. The
-- write runs ONLY when the desired letter differs from state.last_letter -
-- the cache of what the badge was last told to show - so a steady letter is
-- never re-written and the per-tick safety net can run on every tick (any
-- change converges on screen within one tick; a write that failed does not
-- move the cache and is retried by the next path). Every actual write goes
-- through THE ONE LETTER WRITE (write_badge_letter: SetText + the layout
-- nudge in a single primitive) and its line carries the nudge's outcome
-- right after the letter; force_line additionally logs the line when the
-- letter was already correct (the selection-change refresh uses that, so its
-- header is followed by one line per badge whatever they show - a forced
-- line wrote nothing and is marked '(no write)', so no log reader can
-- mistake it for a write that skipped its nudge). Returns true when the
-- letter changed.
local function refresh_badge_letter(marker, force_line)
	local state = ability_state[marker]
	if state == nil or state.badge == nil then return false end
	local on = collective_armed(marker)
	local letter = on and "A" or "M"
	if state.last_letter == letter then
		if force_line then
			log("   badge [" .. marker .. "] letter='" .. letter .. "' (auto "
				.. (on and "ON" or "OFF") .. ") (no write)")
		end
		return false
	end
	local ok_text, ok_layout, layout_err = write_badge_letter(state, letter)
	log("   badge [" .. marker .. "] letter='" .. letter .. "' (auto "
		.. (on and "ON" or "OFF") .. ") layout ok=" .. tostring(ok_layout)
		.. (layout_err and (" (" .. layout_err .. ")") or ""))
	return true
end

-- THE SELECTION CHANGED - refresh BOTH badges' letters from the new
-- selection, immediately (this build). Called from every path that sets
-- selected_unit_id (the fast card path on every ui tick, the once-per-second
-- census when it adopts first, the card click fast-path), in the same call,
-- so the letters never lag the selection. Logged once per change: the header
-- line names the new selection, followed by each existing badge's own letter
-- line (the write inside still runs only when a letter actually changed -
-- the cache above; a forced line says '(no write)').
-- THE OPTIONAL TICK (this build) stamps the header with the battle clock:
--   selection changed to <ui_id> - refreshing badge letters (tick N)
-- The fast card path (section 8e) passes tick_count, so an adoption can be
-- measured against the tick it happened on; the click path and the census
-- call it without a tick and keep their headers exactly as they were.
local function refresh_badge_letters_for_selection(new_id, tick)
	local header = "selection changed to " .. tostring(new_id or "none")
		.. " - refreshing badge letters"
	if tick ~= nil then
		header = header .. " (tick " .. tostring(tick) .. ")"
	end
	log(header)
	for _, ability in ipairs(active_abilities_list()) do
		refresh_badge_letter(ability.marker, true)
	end
end

-- ============================================================================
-- 11. THE TUNING HOOK - for the Lua console (Modding Development Tools, shift+F3)
--     Global functions so they can be typed in-game. They close over the badge's
--     position, which matters: nothing in script can read where a created component
--     really is (round 38: Position() reported a place the badge was not), so the
--     human eye is the measuring instrument. That is how the community's own
--     positioning tutorial does it - "test coordinates until the new UIC looks like
--     it's in the right place".
-- ============================================================================
function zz_badge_set(x, y)
	BADGE_X = tonumber(x) or BADGE_X
	BADGE_Y = tonumber(y) or BADGE_Y
	-- re-place EVERY ability's badge: each one's offset is computed in
	-- place_badge (its wheel slot's delta when its bar position is known,
	-- its own ox/oy otherwise), so a re-tune of the Deadly Onslaught badge
	-- carries Foe-Seeker along.
	replace_all_badges()
	local msg = "BADGE offset = " .. tostring(BADGE_X) .. "," .. tostring(BADGE_Y)
		.. " track=" .. tostring(track)
	log(msg)
	return msg
end


function zz_badge_track(on)
	local want = (on == true) or (tostring(on) == "true") or (tonumber(on) == 1)
	if want == track then
		local m = "BADGE already tracking=" .. tostring(track) .. " delta=" .. tostring(BADGE_X)
			.. "," .. tostring(BADGE_Y)
		log(m)
		return m
	end
	-- switching modes CONVERTS the numbers, so the badge stays exactly where it is:
	-- absolute -> delta = subtract the button position; delta -> absolute = add it back.
	local master = ability_state[ABILITIES[1].marker]
	local bx, by = button_xy(master ~= nil and master.button or nil)
	if bx == nil then
		local m = "BADGE mode switch failed: no button position"
		log(m)
		return m
	end
	if want then
		BADGE_X, BADGE_Y = BADGE_X - bx, BADGE_Y - by
	else
		BADGE_X, BADGE_Y = BADGE_X + bx, BADGE_Y + by
	end
	track = want
	replace_all_badges()
	local m = "BADGE track=" .. tostring(track) .. " now " .. tostring(BADGE_X) .. "," .. tostring(BADGE_Y)
		.. " (button at " .. tostring(bx) .. "," .. tostring(by) .. ")"
	log(m)
	return m
end

function zz_badge_calibrate()
	return zz_badge_track(true)
end

function zz_badge_nudge(dx, dy)
	return zz_badge_set(BADGE_X + (tonumber(dx) or 0), BADGE_Y + (tonumber(dy) or 0))
end

function zz_badge_show(marker)
	marker = marker or "onslaught"
	local state = ability_state[marker]
	if state == nil or state.badge == nil then return "badge not created yet" end
	state.badge_shown = true    -- the next ui tick re-checks this against the claimed set
	pcall(function() state.badge:SetVisible(true) end)
	local ability = ability_for(marker)
	return "badge shown at " .. tostring(BADGE_X + ability.ox) .. "," .. tostring(BADGE_Y + ability.oy)
end

function zz_badge_hide(marker)
	marker = marker or "onslaught"
	local state = ability_state[marker]
	if state == nil or state.badge == nil then return "badge not created yet" end
	state.badge_shown = false   -- the next ui tick re-checks this against the claimed set
	pcall(function() state.badge:SetVisible(false) end)
	return "badge hidden"
end

function zz_badge_parent(marker)
	marker = marker or "onslaught"
	if badge_parent == nil then return "no parent yet" end
	local ability = ability_for(marker)
	if ability == nil then return "no ability with marker '" .. tostring(marker) .. "'" end
	local state = ability_state[marker]
	local ok, id = pcall(function() return badge_parent:Id() end)
	local ok2, w = pcall(function() return badge_parent:Width() end)
	local ok3, h = pcall(function() return badge_parent:Height() end)
	local bx, by = button_xy(state ~= nil and state.button or nil)
	local msg = "BADGE parent=" .. tostring(ok and id or "?") .. " size=" .. tostring(w)
		.. "x" .. tostring(h) .. " offset=" .. tostring(BADGE_X + ability.ox) .. ","
		.. tostring(BADGE_Y + ability.oy)
		.. " track=" .. tostring(track) .. " button=" .. tostring(bx) .. "," .. tostring(by)
		.. " marker=" .. tostring(marker)
	log(msg)
	return msg
end

local function set_armed_look(marker, on)
	-- Availability is NEVER touched: the ability can always be used by hand.
	-- The state is shown by the badge instead.
	badge_visible(marker, on)
end
local function apply_ability_feedback(marker)
	local state = ability_state[marker]
	if state == nil or state.button == nil then return end
	local on = collective_armed(marker)            -- the collective state (one unit: its own flag)
	if state.feedback_on == on then return end     -- nothing to change

	set_armed_look(marker, on)
	state.feedback_on = on
end

-- The one place a per-unit switch is flipped, whichever control did it
-- (currently: a click on the ability's M/A badge - the click handler calls
-- this once per unit its checkbox rule acts on). The state belongs to ONE
-- (unit, ability) pair; every other unit's state for the same ability is
-- untouched. The letter line comes from apply_ability_feedback right after,
-- so a toggle always reports both what changed and what the badge now shows.
local function set_auto_for_unit(ui_id, marker, value)
	local id = unit_slot(ui_id)
	local per = armed[id]
	if per == nil then
		per = {}
		armed[id] = per
	end
	per[marker] = value == true
	log("AUTO " .. tostring(marker) .. " for unit " .. tostring(ui_id) .. ": now "
		.. (value and "ON" or "OFF"))
	apply_ability_feedback(marker)   -- the letter on the badge - the only feedback now
end

-- Find the ability icon. Round 18 showed the engine's own highlight path
-- (battle_orders/orders_parent/behaviour_parent) is the fire-at-will/skirmish row: for Boris
-- all three slots report an EMPTY ability key, so Deadly Onslaught is not there. So scan the
-- HUD instead, bounded, and ask every component the one question the engine documents for
-- identifying an ability button - InterfaceFunction("AbilityKeyForScript") - logging each hit
-- with its Address(). A scan that finds nothing still reports how far it got.
local walk_visits = 0
local walk_skipped = 0        -- components this scan skipped after an error

-- ============================================================================
-- 1a's logging helpers (the switch itself, CLAIM_BISECT, sits in section 1a).
-- Every claim-test operation runs between a bisect_enter() and its bisect_ok()
-- (or bisect_fail(), when the operation itself errored). REMOVED steps (7-8,
-- the find that killed the engine) run nothing and always log their removal.
-- A DISABLED step logs SKIPPED and its result simply does not contribute -
-- the claim verdict falls back to 'not ours' and the walk keeps going.
-- ============================================================================

local last_key_type = nil     -- bisect step 1's answer, for the scan probe line

-- What each step may log per battle (an enter/ok pair = 1, a SKIPPED line = 1)
-- before it goes quiet. The crash this hunt is after happens on the FIRST
-- key-bearing component, so a small budget loses no evidence - it only keeps
-- a long battle's log readable.
local BISECT_LINE_CAP = 40

local bisect_slots_used = {}  -- step -> line-events written so far
local bisect_muted = {}       -- step -> true once its budget is spent

local function bisect_on(step)
	return step <= CLAIM_BISECT
end

-- One slot per logged event; the ok/fail line rides the entering line's slot,
-- so an `entering` with no `ok` (and no `FAILED`) after it can ONLY mean the
-- game itself died inside that operation - which is exactly the signal.
local function bisect_slot(step)
	local used = bisect_slots_used[step] or 0
	if used < BISECT_LINE_CAP then
		bisect_slots_used[step] = used + 1
		return true
	end
	if not bisect_muted[step] then
		bisect_muted[step] = true
		log("bisect: step " .. tostring(step) .. " - further lines suppressed for this battle (cap "
			.. tostring(BISECT_LINE_CAP) .. ")")
	end
	return false
end

-- Immediately BEFORE the step's operation. Returns enabled, shown.
local function bisect_enter(step, name)
	local enabled = bisect_on(step)
	local shown = bisect_slot(step)
	if shown then
		log("bisect: step " .. tostring(step) .. " " .. name
			.. (enabled and " entering" or " SKIPPED (disabled)"))
	end
	return enabled, shown
end

-- Immediately AFTER the step's operation completed cleanly.
local function bisect_ok(step, name, shown)
	if shown and bisect_on(step) then
		log("bisect: step " .. tostring(step) .. " " .. name .. " ok")
	end
end

-- The operation ran but failed (pcall caught it): the step is NAMED in the
-- log instead of an 'ok' line that would be a lie.
local function bisect_fail(step, name, shown, err)
	if shown and bisect_on(step) then
		log("bisect: step " .. tostring(step) .. " " .. name .. " FAILED: " .. tostring(err))
	end
end

-- A REMOVED SLOT (steps 7-8). The operation that used to sit here was
-- string.find - the four-argument plain form is what the bisect caught
-- killing the engine - and no find of any kind remains in the match paths.
-- The slot still logs so the ladder's record stays honest: it names the
-- removal, never `entering`/`ok`, at any level (there is no operation left
-- to enable or disable).
local function bisect_removed(step, name)
	if bisect_slot(step) then
		log("bisect: step " .. tostring(step) .. " " .. name
			.. " SKIPPED (equality match - find removed)")
	end
end

local function bisect_summary()
	local bits = {}
	for step = 1, 9 do
		bits[#bits + 1] = tostring(step) .. (bisect_on(step) and "=on" or "=off")
	end
	return table.concat(bits, " ")
end

-- A FRESH PLAIN-LUA COPY OF WHATEVER THE ENGINE RETURNED. The value a read
-- like InterfaceFunction("AbilityKeyForScript") answers with has passed
-- `type(key) == "string"` and still killed the game the moment it reached a C
-- string function (the crashed sessions' last line was the walk's own header
-- for our key - `.. key ..` printed fine just before the crash; the
-- `^ that one is ours` line and the claim line never followed, and between
-- them the only work was string.lower / find in key_is_ours below). The
-- bisect later named the killer: the four-argument plain-mode find, now
-- removed entirely - the match is exact key equality and runs on the copy
-- only. So nothing in the claim path ever hands the engine's value to a
-- string function: the copy is made by Lua's own concatenation - the one
-- operation the engine's value provably survives - with tostring as the
-- fallback, pcall'd like everything else here. nil when even that fails.
local function as_plain_string(v)
	if v == nil then return nil end

	-- BISECT STEP 1 - type(v): the value's Lua type (remembered for the probe).
	local on1, shown1 = bisect_enter(1, "type(v)")
	if on1 then
		local ok1, t1 = pcall(type, v)
		if ok1 then
			last_key_type = t1
			bisect_ok(1, "type(v)", shown1)
		else
			bisect_fail(1, "type(v)", shown1, t1)
		end
	end

	-- BISECT STEP 2 - tostring(v): pcall'd, the copy's fallback source.
	local text = nil
	local on2, shown2 = bisect_enter(2, "tostring(v)")
	if on2 then
		local ok2, t2 = pcall(tostring, v)
		if ok2 and type(t2) == "string" then
			text = t2
			bisect_ok(2, "tostring(v)", shown2)
		else
			bisect_fail(2, "tostring(v)", shown2,
				ok2 and "tostring answered a non-string" or t2)
		end
	end

	-- BISECT STEP 3 - v .. "": the fresh plain copy; tostring is the fallback.
	local on3, shown3 = bisect_enter(3, "v .. '' (concat copy)")
	if on3 then
		local ok_copy, copied = pcall(function() return v .. "" end)
		if ok_copy and type(copied) == "string" then
			bisect_ok(3, "v .. '' (concat copy)", shown3)
			return copied
		end
		bisect_fail(3, "v .. '' (concat copy)", shown3,
			ok_copy and "the concat did not make a plain string" or copied)
	end
	return text
end

-- A LENGTH READ MUST NEVER KILL THE SCAN. The engine can hand back a STRING
-- from a length read on these long ability keys (the in-battle failure this
-- guards: `string.len(key) > 3` raised "attempt to compare string with number"
-- and killed the whole walk before the button was ever claimed). The value is
-- copied FIRST (as_plain_string) - the length read and the # fallback below
-- only ever act on the copy, never on the engine value. The read is pcall'd,
-- the # operator is the language-level fallback, and nil means "unreadable".
local function safe_len(s)
	local plain = as_plain_string(s)
	if plain == nil then return nil end

	-- BISECT STEP 4 - string.len on the copy.
	local n = nil
	local on4, shown4 = bisect_enter(4, "string.len on the copy")
	if on4 then
		local ok4, n4 = pcall(string.len, plain)
		if ok4 and type(n4) == "number" then
			n = n4
			bisect_ok(4, "string.len on the copy", shown4)
		else
			bisect_fail(4, "string.len on the copy", shown4,
				ok4 and "the length read answered a non-number" or n4)
		end
	end
	if n ~= nil then return n end

	-- BISECT STEP 5 - # on the copy (the language-level fallback).
	local on5, shown5 = bisect_enter(5, "# on the copy")
	if on5 then
		local ok5, n5 = pcall(function() return #plain end)
		if ok5 and type(n5) == "number" then
			n = n5
			bisect_ok(5, "# on the copy", shown5)
		else
			bisect_fail(5, "# on the copy", shown5,
				ok5 and "the # read answered a non-number" or n5)
		end
	end
	return n
end

-- IS THIS BUTTON SHOWING THIS ABILITY? The claim test is the KEY ALONE - no
-- Id(): on a real ability button the engine answers Id() with a function (the
-- quirk the battle log printed as 'function: 0000000154EC9390') or fails
-- outright, so anything Id-gated rejects every ability button before its key
-- is ever considered. The match is EXACT KEY EQUALITY, hardened like safe_len
-- AND COPY-FIRST: string.lower only ever sees a fresh plain copy of the key
-- (as_plain_string), and the lowered copy is then compared, character for
-- character, against every key listed for the ability in ABILITIES (section
-- 1) - the table is the single source of truth. No find of any kind runs
-- here any more: the bisect proved the four-argument plain-mode string.find
-- kills the engine (the log's last line was `bisect: step 7 string.find
-- plain entering`, with no `ok`), so steps 7-8 are removed slots that only
-- log the removal and contribute nothing to the verdict.
--
-- THE NARROWING IS DELIBERATE: a key that merely CONTAINS an ability's name
-- (e.g. 'zz_wh_main_character_abilities_deadly_onslaught_xx') no longer
-- claims. Only the exact keys listed in ABILITIES are accepted - and the
-- scan probe prints every key-bearing component we did not claim (ours=no),
-- so an unknown engine variant shows up in the battle log immediately and
-- the fix is one line in the table.
--
-- THE BISECT (section 1a) splits this sequence into steps 6-9: at level 9 the
-- behaviour is the equality match; a disabled step logs SKIPPED and its
-- result simply does not contribute, so the verdict falls back to 'not ours'.
-- (The lower is pcall'd on its own, so an error in it is NAMED, not a silent
-- skip - and if it fails, the un-lowered copy is compared instead: a
-- misbehaving helper must not lose a button.)
local function key_is_ours(ability, key)
	if ability == nil then return false end
	local plain = as_plain_string(key)
	if plain == nil then return false end

	-- BISECT STEP 6 - string.lower on the copy.
	local lowered = nil
	local on6, shown6 = bisect_enter(6, "string.lower on the copy")
	if on6 then
		local ok6, l6 = pcall(string.lower, plain)
		if ok6 then
			lowered = l6
			bisect_ok(6, "string.lower on the copy", shown6)
		else
			bisect_fail(6, "string.lower on the copy", shown6, l6)
		end
	end

	-- BISECT STEPS 7-8 - REMOVED SLOTS. Step 7 was `string.find plain` and
	-- step 8 `string.find pattern-form`; the bisect named the plain form as
	-- the killer, so both are gone from every match path. The slots always
	-- log their removal and run nothing - they can never crash, and the
	-- ladder's record of what happened stays honest.
	bisect_removed(7, "string.find plain")
	bisect_removed(8, "string.find pattern-form")

	-- BISECT STEP 9 - THE EQUALITY COMPARE, the verdict gate. Equality, not
	-- containment: the lowered copy must EQUAL one of the ability's listed
	-- keys (they are lowercase already). If the lower failed or its step was
	-- disabled, the un-lowered copy is compared instead.
	local verdict = false
	local on9, shown9 = bisect_enter(9, "the equality compare")
	if on9 then
		local candidate = lowered or plain
		for _, listed_key in ipairs(ability.keys) do
			if candidate == listed_key then
				verdict = true
			end
		end
		bisect_ok(9, "the equality compare", shown9)
	end
	return verdict
end

-- THE LIVE CLAIM TEST, shared by the ui tick and the badge click guard: a
-- marker is ON THE CURRENTLY SELECTED UNIT'S DIAL right now when its claimed
-- button reference still exists AND its key read passes key_is_ours - the
-- same gate the scan claimed it with. One test in one place, so a click can
-- never act on a badge the tick considers unclaimed (or the other way round).
local function marker_claimed_now(ability)
	if ability == nil then return false end
	local state = ability_state[ability.marker]
	if state == nil or state.button == nil then return false end
	local ok_k, key = pcall(function() return state.button:InterfaceFunction("AbilityKeyForScript") end)
	if ok_k and (safe_len(key) or 0) > 3 and key_is_ours(ability, key) then
		return true
	end
	return false
end

-- THE SCAN PROBE: every component that reported a key but was NOT claimed is
-- recorded here (up to scan_probe_cap), and find_ability_buttons writes the
-- block - rate-limited - so a seen-but-unclaimed button can never be silent
-- again. ours= says whether our own matcher would have claimed it.
local scan_probe_queue = {}
local scan_probe_cap = 3
local scan_probe_diag_cap = 2         -- keytype/copyok/lenok line: at most this many per write
local scan_count = 0                  -- how many scans this battle
local last_probe_claim_count = -1     -- claim count of the last probe block written

-- THE ACTIVE-DIAL TEST (critique-2 item 1). True when every ability that can
-- matter THIS battle has its dial button: the scan stops there. The test now
-- runs over the ACTIVE set - item 1.4's active_abilities_list(), i.e. every
-- marker a tracked unit OWNS or that is CURRENTLY CLAIMED - rather than the
-- whole ABILITIES table. A battle where nothing of ours can be on the dial
-- (the selected unit a Cathayan or Tzeentch lord that owns none of our
-- markers, and nothing claimed) therefore yields an EMPTY active set, and an
-- empty set is VACUOUSLY complete: the ui tick's walk gate closes entirely
-- instead of running the 5 s safety net for the whole fight - the repetition
-- the user's log showed ("scan done: 632 component(s) visited - none of ours
-- found"). The BOOTSTRAP is untouched: while no information exists yet,
-- active_abilities_list() falls back to the full ABILITIES table, so this is
-- byte-for-byte the old full-table walk.
--
-- SELF-CORRECTING - nothing is lost by stopping: a scan, the re-list, the
-- identity watch or the 60 s fallback can reveal a NEWLY OWNED marker with no
-- walk at all; the active-set refresh then puts it in the active set, this
-- test returns false again (its button is not claimed yet) and walking
-- resumes. A selection change raises walk_on_selection_change, so the next
-- tick walks too.
local function all_buttons_found()
	for _, ability in ipairs(active_abilities_list()) do
		local state = ability_state[ability.marker]
		if state == nil or state.button == nil then return false end
	end
	return true
end

-- THE CLAIMED BUTTON'S 1-BASED POSITION AMONG THE KEY-BEARING CHILDREN OF
-- ITS PARENT BAR (this build). This is what maps to the wheel: two measured
-- battles showed the bar's key-bearing children sit in wheel order 1..6, so
-- the ordinal IS the slot number. ("Key-bearing" is the same gate the scan
-- walk uses: the child's key read passes safe_len > 3.) Every read here is
-- pcall'd exactly like the walk's, so no sibling - however hostile its key -
-- can kill the claim; a component whose reads fail simply does not count
-- (the badges then fall back, logged). "Ours" is found by IDENTITY first
-- (the component's own Address(), the stable per-component pointer the
-- battle log prints) and by EXACT key equality second (key_is_ours), so a
-- twin of our key earlier on the bar cannot steal our position. Returns
-- k >= 1, or nil when the parent or the children cannot be read.
local function bar_ordinal_for(uic, ability)
	if uic == nil or ability == nil then return nil end

	local ok_p, parent = pcall(function() return uic:Parent() end)
	if not ok_p or parent == nil then return nil end
	local ok_w, container = pcall(function() return UIComponent(parent) end)
	if not ok_w or container == nil then return nil end

	local ok_n, n = pcall(function() return container:ChildCount() end)
	if not ok_n or type(n) ~= "number" or n <= 0 then return nil end

	-- Our own address, for the identity test (nil when unreadable).
	local my_addr = nil
	local ok_my, my = pcall(function() return uic:Address() end)
	if ok_my and my ~= nil then my_addr = tostring(my) end

	local seen = 0
	for i = 0, n - 1 do
		local ok_c, child = pcall(function() return container:Find(i) end)
		if ok_c and child ~= nil then
			local ok_cw, cc = pcall(function() return UIComponent(child) end)
			if ok_cw and cc ~= nil then
				local ok_k, key = pcall(function() return cc:InterfaceFunction("AbilityKeyForScript") end)
				if ok_k and (safe_len(key) or 0) > 3 then
					seen = seen + 1

					local is_ours = false
					if my_addr ~= nil then
						local ok_a, addr = pcall(function() return cc:Address() end)
						if ok_a and addr ~= nil and tostring(addr) == my_addr then
							is_ours = true
						end
					end
					if not is_ours and key_is_ours(ability, key) then
						is_ours = true
					end

					if is_ours then return seen end
				end
			end
		end
	end
	return nil
end

-- ONE COMPONENT'S WORTH OF SCAN WORK. The walk below runs this inside its own
-- pcall, so no single component - however hostile its reads - can kill the
-- walk (the known in-game failure) or abort the scan silently.
-- ============================================================================
-- ROUND 125 - THE RIGHT-HAND SPELL BAR IS LEFT TO THE PLAYER (user ruling
-- 2026-11-03). The left-hand ability wheel is the mod's job; the right-hand
-- bar - spells, and the runes a Rune Smith carries, which the game also puts
-- there - gets no letter and no trigger. A button whose Id() reads
-- 'button_spell...' is therefore never claimed: no badge is built, the ability
-- can never be armed, so it never fires. The same key on a WHEEL button (a rune
-- granted by an item or an active ability) is claimed exactly as before. The
-- round-124 spell-bar badge placement (a field-tested success, but activating
-- one rune locks the others, so automating them makes little sense) is gone.
-- spell_bar_noted[marker] = true once the skip has been reported this battle.
-- ============================================================================
FOURTH.spell_bar_noted = {}

local function scan_component_body(uic)
	local ok_key, key = pcall(function() return uic:InterfaceFunction("AbilityKeyForScript") end)
	if not ok_key then
		walk_skipped = walk_skipped + 1
		if walk_skipped <= 5 then
			log("scan: " .. tostring(walk_skipped) .. " component(s) skipped after an error: "
				.. tostring(key))
		end
	end
	-- The gate is the COPY's length (as_plain_string inside safe_len), not a
	-- type() test on the engine value: a value the engine dressed as anything
	-- other than a plain string still gets its chance, and nothing raw is
	-- string-op'd anywhere in this body.
	if ok_key and (safe_len(key) or 0) > 3 then
		-- The id is LOGGED for diagnostics but never judged: on a real ability
		-- button the engine can answer Id() with a function, or fail outright,
		-- and an un-pcall'd read here killed the whole body BEFORE the key was
		-- considered. Nothing in this block may reject the component - the
		-- claim below is the key alone.
		local ok_addr, addr = pcall(function() return uic:Address() end)
		local ok_id, id = pcall(function() return uic:Id() end)
		log("   ability button: key='" .. key .. "' id='" .. tostring(ok_id and id or "?")
			.. "' address=" .. tostring(addr))

		-- One claim per ability: the judgement is the KEY ALONE - it passed
		-- safe_len() > 3 in the gate above and must EQUAL one of the
		-- ability's listed keys, lowercased (key_is_ours; exact equality,
		-- no find of any kind). Every database variant listed in the table
		-- attaches; an unlisted variant shows up in the probe below.
		-- No Id check, no Id-based liveness gate in this path.
		-- ROUND 125: a button on the right-hand SPELL bar is never claimed (see
		-- the banner above scan_component_body). Only a plain-string Id() can say
		-- so; anything else is judged by its key alone, exactly as before.
		local on_spell_bar = (ok_id and type(id) == "string" and string.sub(id, 1, 12) == "button_spell")
		if on_spell_bar then
			for _, ability in ipairs(ABILITIES) do
				if FOURTH.spell_bar_noted[ability.marker] == nil and key_is_ours(ability, key) then
					FOURTH.spell_bar_noted[ability.marker] = true
					log("scan: " .. ability.marker .. " is on the right-hand SPELL bar ('" .. id
						.. "') - not claimed: no badge, no trigger (user rule 2026-11-03)")
				end
			end
		end
		local claimed = nil
		for _, ability in ipairs(ABILITIES) do
			local state = ability_state[ability.marker]
			if state.button == nil and not on_spell_bar and key_is_ours(ability, key) then
				-- RECORD ONLY - nothing is created, painted or written to the
				-- engine from inside this walk. The reference and the flag are
				-- all a claim leaves behind; the ui tick builds the badge from
				-- the flag, step by step, instrumented (section 8b).
				state.button = uic
				pending_badge[ability.marker] = true
				badge_attempts[ability.marker] = 0
				badge_gave_up[ability.marker] = nil
				claimed = ability
				log("   ^ that one is ours (" .. ability.marker .. ")")
				log("claim: " .. ability.marker
					.. " button found - badge creation deferred to the tick")
				-- THE BAR POSITION (this build): the old live Position()
				-- read is GONE - it read the wrong widget (the claimed
				-- button lives in the HIDDEN BAR, so its Position() is a
				-- bar coordinate like (1130,1052), not a wheel slot, and
				-- the badges landed off-screen). What maps to the wheel is
				-- the button's 1-based position among the KEY-BEARING
				-- children of its parent bar - measured over two battles.
				-- bar_ordinal_for walks the siblings (every read pcall'd),
				-- and slot_index is refreshed on every claim; the badge's
				-- offset follows through WHEEL_SLOT (section 8b).
				local k = bar_ordinal_for(uic, ability)
				if k ~= nil and k >= 1 and k <= 6 then
					slot_index[ability.marker] = k
					local slot = WHEEL_SLOT[k]
					log("claim: " .. ability.marker .. " is bar position " .. tostring(k)
						.. " -> wheel slot (" .. tostring(slot[1]) .. "," .. tostring(slot[2]) .. ")")
				elseif k ~= nil then
					slot_index[ability.marker] = nil
					log("claim: " .. ability.marker .. " is bar position " .. tostring(k)
						.. " - MORE THAN SIX key-bearing bar children (unexpected) - badge will use its fallback offset")
				else
					slot_index[ability.marker] = nil
					log("claim: " .. ability.marker
						.. " bar position unreadable - badge will use its fallback offset")
				end
			end
		end

		-- The probe, collected here and written by find_ability_buttons: this
		-- component reported a key but did not become a button. ours=yes is
		-- the alarming case - our own matcher would have taken it.
		if claimed == nil and #scan_probe_queue < scan_probe_cap then
			local ours = false
			for _, ability in ipairs(ABILITIES) do
				if key_is_ours(ability, key) then
					ours = true
				end
			end
			local ok_id2, probe_id = pcall(function() return uic:Id() end)
			-- The key's own properties, so the next battle's log names exactly
			-- which of them is hostile: keytype is what the bisect's step 1
			-- (type(v)) answered for this value, copyok whether
			-- as_plain_string could make the fresh plain copy, lenok whether
			-- the copy measured (safe_len acts on the copy).
			scan_probe_queue[#scan_probe_queue + 1] = {
				id = tostring(ok_id2 and probe_id or "?"),
				key = key,
				keytype = last_key_type,
				copyok = (as_plain_string(key) ~= nil),
				lenok = (safe_len(key) ~= nil),
				ours = ours,
			}
		end

		if claimed ~= nil then
			-- NOTHING RUNS HERE ANY MORE. The claim used to continue with the
			-- event-reporter chain (7 x AddScriptEventReporter on the button and
			-- its ancestors), the container-chain walk, the icon/state reads and
			-- the feedback call - a dozen engine touches on a freshly claimed,
			-- engine-owned button, inside a walk, while the HUD may be mid-rebuild.
			-- The crashed session's log ends at the claim with no line after it,
			-- so a successful claim now leaves only the reference and the flag
			-- (above); every engine touch on the badge path happens on the ui
			-- tick, instrumented step by step (section 8b). The event reporters
			-- existed to hear right-clicks on the button - a control this mod no
			-- longer has (the M/A badge click is the only control).
			do end
		end
	end
end

local function scan_component(uic, depth)
	if uic == nil or depth > 6 or walk_visits > 4000 or all_buttons_found() then return end
	walk_visits = walk_visits + 1

	local ok_one, err_one = pcall(scan_component_body, uic)
	if not ok_one then
		walk_skipped = walk_skipped + 1
		if walk_skipped <= 5 then
			log("scan: " .. tostring(walk_skipped) .. " component(s) skipped after an error: "
				.. tostring(err_one))
		end
	end

	local ok_n, n = pcall(function() return uic:ChildCount() end)
	if ok_n and type(n) == "number" then
		for i = 0, n - 1 do
			local ok_c, child = pcall(function() return uic:Find(i) end)
			if ok_c and child ~= nil then
				local ok_r, err_r = pcall(function()
					scan_component(UIComponent(child), depth + 1)
				end)
				if not ok_r then
					walk_skipped = walk_skipped + 1
					if walk_skipped <= 5 then
						log("scan: " .. tostring(walk_skipped) .. " component(s) skipped after an error: "
							.. tostring(err_r))
					end
				end
			end
		end
	end
end

local function find_ability_buttons()
	if all_buttons_found() then return end
	walk_visits = 0
	walk_skipped = 0
	scan_probe_queue = {}
	scan_count = scan_count + 1

	local ok, err = pcall(function()
		local hud = UIComponent(core:get_ui_root():Find("hud_battle"))
		if hud == nil then
			if not logged_no_parent then
				logged_no_parent = true
				log("ability icons: hud_battle is not on screen yet (will keep trying)")
			end
			return
		end

		log("ability icons: scanning the HUD for ability buttons")
		scan_component(hud, 0)

		local found = {}
		local claim_bits = {}
		local claimed_count = 0
		for _, ability in ipairs(ABILITIES) do
			local is_claimed = ability_state[ability.marker].button ~= nil
			if is_claimed then
				found[#found + 1] = ability.marker
				claimed_count = claimed_count + 1
			end
			claim_bits[#claim_bits + 1] = ability.marker .. "=" .. tostring(is_claimed)
		end
		log("   scan done: " .. tostring(walk_visits) .. " component(s) visited - "
			.. (#found > 0 and ("found: " .. table.concat(found, ", ")) or "none of ours found")
			.. " | scan: claimed " .. table.concat(claim_bits, " "))

		-- HANDLE HEALTH: a scan that cannot walk the HUD is never silent again.
		-- A HUD that has children yet yields a one-component walk is the known
		-- dead-handle signature (the engine rebuilt hud_battle), so it is
		-- called out too and the next scan re-fetches.
		local children_str = "invalid"
		local ok_hc, hc = pcall(function() return hud:ChildCount() end)
		if ok_hc and type(hc) == "number" then children_str = tostring(hc) end
		log("   scan: hud_battle children=" .. children_str .. " visits=" .. tostring(walk_visits)
			.. " skipped=" .. tostring(walk_skipped))
		if children_str == "invalid"
			or (ok_hc and type(hc) == "number" and hc >= 1 and walk_visits <= 1) then
			log("   scan: hud_battle handle unusable this scan - refetching next time")
		end

		-- THE PROBE: write the collected unclaimed keys, rate-limited to a
		-- claim-count change or every 10th scan, so a mismatch is never
		-- silent and the log stays readable.
		if #scan_probe_queue > 0
			and (claimed_count ~= last_probe_claim_count or (scan_count % 10) == 0) then
			for i = 1, #scan_probe_queue do
				local entry = scan_probe_queue[i]
				-- Up to scan_probe_diag_cap entries also get the key's property
				-- line, immediately before the ours verdict.
				if i <= scan_probe_diag_cap then
					log("scan probe: keytype=" .. tostring(entry.keytype)
						.. " copyok=" .. tostring(entry.copyok)
						.. " lenok=" .. tostring(entry.lenok))
				end
				log("scan probe: id='" .. entry.id .. "' key='" .. entry.key .. "' ours="
					.. (entry.ours and "yes" or "no"))
			end
			last_probe_claim_count = claimed_count
		end
	end)

	if not ok then log("ability icon scan failed: " .. tostring(err)) end

	-- ITEM 1.4 - the scan just ran: a claim (or a fresh owned-key read) may
	-- have changed the inputs, so refresh the active set. Silent unless it moved.
	refresh_active_abilities()
end


-- (4) the engine's own report that an ability was *used* - the documented command channel
--     (battle.lua: "Special Ability - a command to use a special ability has been issued",
--     get_string1() = the ability name). Log only, but it is the control case for the whole
--     question: if a click on the icon reaches the game at all, this fires.
bm:register_command_handler_callback("Special Ability", function(context)
	local ability = "?"
	pcall(function() ability = context:get_string1() end)
	log("command: 'Special Ability' issued for '" .. tostring(ability) .. "'")
end, "zz_deadly_onslaught_ability_used")



-- Does this event belong to our chain? Returns the id of the matching component, or nil.
-- Compared by address first (what vanilla does) and by id second.
local function in_chain(context)
	for _, ability in ipairs(ABILITIES) do
		local state = ability_state[ability.marker]
		for i = 1, #state.watch_chain do
			local e = state.watch_chain[i]
			if e.addr ~= nil and context.component ~= nil and context.component == e.addr then
				return e.id or "?"
			end
		end
	end
	for _, ability in ipairs(ABILITIES) do
		local state = ability_state[ability.marker]
		for i = 1, #state.watch_chain do
			local e = state.watch_chain[i]
			if e.id ~= nil and context.string == e.id then return e.id end
		end
	end
	return nil
end

-- (1) THE EVENT THAT MATTERS: a right-click on the ability icon, now that the component
-- reports its events. script/events.lua declares ComponentRClickUp; this is the first time we are
-- actually asking for it. Matched by component id and by address, so whichever the context fills in
-- one of them will agree.
local rclick_other = 0
core:add_listener(
	"zz_deadly_onslaught_rclick",
	"ComponentRClickUp",
	function(context) return true end,          -- unfiltered ON PURPOSE: the log labels it
	function(context)
		local who = in_chain(context)
		if who ~= nil then
			log("RCLICK: right-click came in on '" .. tostring(context.string) .. "' - in our chain ("
				.. who .. ")")
			-- (the right-click toggle is gone: the badge click is the only control)
		else
			if rclick_other < 15 then
				rclick_other = rclick_other + 1
				log("RCLICK: right-click on '" .. tostring(context.string) .. "' - not ours")
			end
		end
	end,
	true
)

-- (2) THE KEYBOARD: gone. The shortcut listeners and their on_shortcut helper were deleted,
-- so pressing '8' (usegroup8) no longer reaches the mod at all. The badge click is the only control.

-- (3) THE CONTROL: a left-click on the same icon, which happens whenever the ability is used -
-- so this one is seen without the player doing anything special. If this reports and the
-- right-click does not, the reporter works and the engine simply never raises the right-click.
local lclick_other = 0
core:add_listener(
	"zz_deadly_onslaught_lclick_control",
	"ComponentLClickUp",
	function(context) return true end,          -- unfiltered ON PURPOSE: the log labels it
	function(context)
		local clicked_id = tostring(context.string)

		-- THE BADGE CLICK: a left-click on our OWN badge flips the per-unit
		-- switch(es) for that badge's ability. Round 43+ measured that these
		-- clicks DO reach script - six clicks each arrived as a "left-click
		-- on 'zz_auto_badge'" and were simply logged as "not ours". The badge
		-- is the component created on hud_battle with the id 'zz_auto_badge';
		-- any future 'zz_auto_*' component is routed the same way, so an
		-- added or renamed badge keeps working. Each badge id resolves to its
		-- own ability (section 1), so a click flips ONLY that ability - for
		-- every unit the engine reports as selected that owns it: one
		-- selected unit - exactly as before; several - the checkbox rule
		-- (all armed -> disarm all, else arm all; selected non-owners are
		-- never touched). With no unit selected the click does nothing but
		-- say so.
		if string.sub(clicked_id, 1, 8) == "zz_auto_" then
			local ability = ability_for_badge(clicked_id)
			if ability == nil then
				log("badge click on '" .. clicked_id
					.. "' - no ability has that badge id, ignored")
				return
			end
			if selected_unit_id == nil and #selected_ui_ids == 0 then
				log("click ignored: no unit selected yet - click the unit's card first")
				return
			end

			-- THE CLICK GUARD (this build): a badge whose marker is NOT
			-- currently claimed - i.e. NOT on the selected unit's dial - is
			-- INERT. The battle log showed a stale, still-visible badge
			-- being clicked while the dial had no Deadly Onslaught, and the
			-- click toggled the ability on for a unit that does not even
			-- own it. The test is marker_claimed_now, the same one the ui
			-- tick uses, so the tick and the click can never disagree.
			if not marker_claimed_now(ability) then
				log("click ignored: " .. ability.marker .. " is not on this unit's dial")
				return
			end

			-- THE SELECTED SET (this build): the badge click acts on EVERY
			-- unit the engine reports as selected, not just the single
			-- tracker below - the vanilla "common ability" behaviour. The
			-- shared card read keeps the set current (section 8e); when it
			-- is empty the tracker stands in alone, exactly as before.
			local targets, target_ids = {}, {}
			for i = 1, #selected_ui_ids do
				local id = selected_ui_ids[i]
				if id ~= nil then
					targets[#targets + 1] = id
					target_ids[#target_ids + 1] = tostring(id)
				end
			end
			if #targets == 0 then
				if selection_callback_alive then
					-- THE ENGINE'S OWN ANSWER: nothing is selected. The
					-- tracker may still name the last unit, but acting on
					-- it would toggle a unit the player has deselected -
					-- the callback set is authoritative, so the click acts
					-- on nobody.
					log("click ignored: no unit selected yet - click the unit's card first")
					return
				end
				targets[1] = tostring(selected_unit_id)
				target_ids[1] = tostring(selected_unit_id)
			end

			if #targets <= 1 then
				-- ONE SELECTED UNIT - one unit's own pair flips, whether or
				-- not the scan has seen the ability on it yet (a
				-- late-arriving ability stays armable). When the callback set
				-- is in charge, the one id IS the engine's answer (and may
				-- already be newer than the tracker, which catches up at the
				-- next convergence); the fallback world keeps acting on the
				-- tracker, exactly as before. The click-time context - the
				-- unit, its type and the state as it was - is written BEFORE
				-- the toggle takes effect: the diagnostic for the reported
				-- cross-unit toggle, so the log names the unit a click
				-- really acted on.
				local single_id = target_ids[1]
				if not selection_callback_alive then single_id = tostring(selected_unit_id) end
				local unit = units_by_ui_id[tostring(single_id)]
				local arm_slot = unit_slot(single_id)
				local per = armed[arm_slot]
				local was_armed = per ~= nil and per[ability.marker] == true
				local ok_t, unit_type = pcall(function() return unit:type() end)
				log("click: " .. ability.marker .. " badge -> selected unit "
					.. tostring(single_id) .. " ('" .. tostring(ok_t and unit_type or "?")
					.. "') armed was " .. (was_armed and "ON" or "OFF"))
				set_auto_for_unit(single_id, ability.marker, not was_armed)
				return
			end

			-- SEVERAL SELECTED UNITS - THE CHECKBOX RULE (this build): over
			-- every selected unit that OWNS one of this ability's keys (the
			-- per-unit owned-key cache, section 4), ALL armed -> disarm
			-- all, otherwise -> arm all. Selected units that do not own the
			-- ability are never touched, so per-unit independence holds.
			local owners, owner_ids = {}, {}
			for i = 1, #targets do
				if unit_owns_marker(targets[i], ability.marker) then
					owners[#owners + 1] = targets[i]
					owner_ids[#owner_ids + 1] = target_ids[i]
				end
			end
			if #owners == 0 then
				log("click: " .. ability.marker .. " badge -> " .. tostring(#targets)
					.. " selected unit(s), none owns the ability - nothing toggled")
				return
			end
			local all_armed = true
			for i = 1, #owners do
				local per = armed[unit_slot(owners[i])]
				if per == nil or per[ability.marker] ~= true then
					all_armed = false
				end
			end
			local value = not all_armed
			for i = 1, #owners do
				set_auto_for_unit(owners[i], ability.marker, value)
			end
			log("click: " .. ability.marker .. " badge -> " .. tostring(#owners)
				.. " selected unit(s) toggled " .. (value and "ON" or "OFF")
				.. " (" .. table.concat(owner_ids, ", ") .. ")")
			return
		end

		-- THE UNIT CARD: a click on a unit's card selects the unit the badge
		-- clicks act on. The card's component id IS its unit's own
		-- unique_ui_id (the proven bridge - vanilla matches
		-- uic_card:Id() == unit:unique_ui_id() the same way), so this is a
		-- plain table lookup, never a find. This is the FAST-PATH: the card
		-- sweep (section 8e) re-derives the selection from the engine's own
		-- card states within ~1 s and WINS over whatever this click set.
		local clicked_unit = units_by_ui_id[clicked_id]
		if clicked_unit ~= nil then
			-- IS THIS A SELECTION CHANGE? (this build) The letters are
			-- driven from a card click ONLY when the click actually moves
			-- the selection; a click that re-selects the same unit stays
			-- silent (the letter cache has nothing to change).
			local selection_changed = (selected_unit_id ~= clicked_id)
			selected_unit_id = clicked_id
			local ok_t, unit_type = pcall(function() return clicked_unit:type() end)
			log("SELECTED unit ui id " .. clicked_id .. " ('"
				.. tostring(ok_t and unit_type or "?")
				.. "') - badge clicks now act on it")
			if selection_changed then
				walk_on_selection_change = true   -- the dial now belongs to this unit
				-- THE SELECTION CHANGED: refresh BOTH badges' letters from
				-- the new selection in this same handler call (this build) -
				-- the letters never wait for a timer - then log the
				-- tick-stamped card-click line, so the click itself is the
				-- refresh trigger. The feedback caches are re-synced right
				-- after, so every other path agrees.
				refresh_badge_letters_for_selection(selected_unit_id)
				log("card click: selection -> " .. tostring(selected_unit_id)
					.. " - letters refreshed at tick " .. tostring(tick_count))
			end
			for _, ability in ipairs(ABILITIES) do
				apply_ability_feedback(ability.marker)
			end
			return
		end

		local who = in_chain(context)
		if who ~= nil then
			log("CONTROL: left-click came in on '" .. tostring(context.string) .. "' - in our chain ("
				.. who .. ") - component click events DO reach script in battle")
		else
			if lclick_other < 15 then
				lclick_other = lclick_other + 1
				log("CONTROL: left-click on '" .. tostring(context.string) .. "' - not ours")
			end
		end
	end,
	true
)

-- ============================================================================
-- 8c. THE DIAL DUMP - a once-per-second, READ-ONLY census of the ability dial
--     What the script sees vs what the screen shows: every child of our button's
--     parent container (the 'button_parent' next to our button), each with its
--     id, its AbilityKeyForScript and its Position(), plus the parent's and the
--     'SA_dial' ancestor's own positions and our badge's position/offset/letter.
--     The caller gates it to one block per ~1 s of battle time (4 x 250 ms), and
--     every engine read is pcall'd and type-checked, so it can never error out of
--     the tick. NOTHING here writes to any button.
-- ============================================================================

local DIAL_DUMP_EVERY_N_POLL_TICKS = 4      -- 4 x 250 ms = ~1 s of battle time
local last_dial_dump_tick = -1000           -- so the first confirmed tick dumps at once

local function fmt_xy(x, y)
	if type(x) == "number" and type(y) == "number" then
		return "(" .. tostring(x) .. "," .. tostring(y) .. ")"
	end
	return "(?,?)"
end

local function read_xy(uic)
	local ok, x, y = pcall(function() return uic:Position() end)
	if ok and type(x) == "number" and type(y) == "number" then return x, y end
	return nil, nil
end

local function log_dial_dump()
	local master = ability_state[ABILITIES[1].marker]
	if master == nil or master.button == nil then return end

	local ok_p, parent = pcall(function() return master.button:Parent() end)
	if not ok_p or parent == nil then return end
	local ok_w, container = pcall(function() return UIComponent(parent) end)
	if not ok_w or container == nil then return end

	-- The dial itself: the first 'SA_dial' on the way up from our button.
	local dial_str = "?"
	local node = master.button
	for _ = 1, 8 do
		local ok_up, up = pcall(function() return node:Parent() end)
		if not ok_up or up == nil then break end
		local ok_w2, wrapped = pcall(function() return UIComponent(up) end)
		if not ok_w2 or wrapped == nil then break end
		node = wrapped
		local ok_id, id = pcall(function() return node:Id() end)
		if ok_id and type(id) == "string" and id == "SA_dial" then
			local dx, dy = read_xy(node)
			dial_str = fmt_xy(dx, dy)
			break
		end
	end

	local slot_count = nil
	local ok_n, n = pcall(function() return container:ChildCount() end)
	if ok_n and type(n) == "number" then slot_count = n end

	local px, py = read_xy(container)
	log("DIAL t=" .. string.format("%.1f", tick_count * POLL_MS / 1000) .. "s slots="
		.. (slot_count ~= nil and tostring(slot_count) or "?")
		.. " parent=" .. fmt_xy(px, py) .. " dial=" .. dial_str)

	if slot_count ~= nil then
		for i = 0, slot_count - 1 do
			local ok_c, child = pcall(function() return container:Find(i) end)
			if ok_c and child ~= nil then
				local ok_c2, cc = pcall(function() return UIComponent(child) end)
				if ok_c2 and cc ~= nil then
					local cid = "?"
					local ok_i, id = pcall(function() return cc:Id() end)
					if ok_i and type(id) == "string" then cid = id end

					local ckey = "-"
					local ok_k, key = pcall(function() return cc:InterfaceFunction("AbilityKeyForScript") end)
					if ok_k and type(key) == "string" and (safe_len(key) or 0) > 3 then
						ckey = key
					end

					local cx, cy = read_xy(cc)
					log("  slot " .. tostring(i + 1) .. ": id='" .. cid
						.. "' key='" .. ckey .. "' pos=" .. fmt_xy(cx, cy))
				end
			end
		end
	end

	-- ONE FOOTER LINE PER ABILITY: the badge's visibility, position and letter,
	-- plus the offset it was placed at (BADGE_X/BADGE_Y + its own ox/oy). The
	-- onslaught footer keeps its original wording; added abilities get a tag.
	for _, ability in ipairs(ABILITIES) do
		local state = ability_state[ability.marker]
		local bvis, bpos, bletter = false, "(?,?)", "-"
		if state.badge ~= nil then
			bvis = state.badge_shown == true
			local bx, by = read_xy(state.badge)
			bpos = fmt_xy(bx, by)
			local ok_g, got = pcall(function() return state.badge:GetText() end)
			if ok_g and type(got) == "string" then
				bletter = got
			else
				bletter = is_armed(selected_unit(), ability.marker) and "A" or "M"
			end
		end
		local prefix = "OUR BADGE"
		if ability.marker ~= "onslaught" then
			prefix = prefix .. " [" .. ability.marker .. "]"
		end
		log(prefix .. ": visible=" .. (bvis and "true" or "false") .. " pos=" .. bpos
			.. " offset=(" .. tostring(BADGE_X + ability.ox) .. "," .. tostring(BADGE_Y + ability.oy)
			.. ") letter='" .. bletter .. "'")
	end
end

-- ============================================================================
-- 8d. THE INVENTORY SWEEP - a once-per-second, READ-ONLY census of every
--     candidate ability component, in TWO coordinate spaces at once.
--     The player sees a CIRCLE, but the DIAL dump above reports the button bar
--     as a straight line (same y, x stepping by 59 px). So either the circle is
--     a component outside button_parent, or Position() and the drawn position
--     live in different spaces - RelativePosition() and GetDockOffset() have
--     never been read. This sweep reads them, pcall'd, for every candidate id
--     and logs ONE line per candidate; a read that fails prints '?' and NEVER
--     skips its line. It runs whenever our ability button OR any candidate can
--     be found - NOT only while the dial is confirmed - once per ~1 s.
-- ============================================================================

local INVENTORY_EVERY_N_POLL_TICKS = 4      -- 4 x 250 ms = ~1 s of battle time
local last_inventory_tick = -1000           -- so the first tick with a find dumps at once

-- The fixed candidate ids, read and logged in this order. Every one is looked
-- up by id from the UI root: root:Find(id) is the engine's own recursive search.
local INVENTORY_FIXED = {
	"SA_dial", "dial_frame", "button_parent",
	"button_ability",
	"button_ability1", "button_ability2", "button_ability3",
	"button_ability4", "button_ability5", "button_ability6",
	"button_slot1", "button_slot2", "button_slot3",
	"button_slot4", "button_slot5", "button_slot6",
	"behaviour_parent", "orders_parent", "army_ability_parent", "ability_parent",
	"zz_auto_badge", "zz_auto_badge_fs",
}

local function inv_id_of(uic)
	local ok, id = pcall(function() return uic:Id() end)
	if ok and type(id) == "string" and string.len(id) > 0 then return id end
	return nil
end

-- Find one candidate: the engine's recursive Find from the ui root first, and
-- a bounded walk of the tree as a fallback. Returns the component, or nil.
local function inv_find(wanted)
	local ok, got = pcall(function()
		local root = core:get_ui_root()
		if root == nil then return nil end
		local raw = root:Find(wanted, false)      -- false = do not assert when missing
		if raw == nil then return nil end
		local ok_w, wrapped = pcall(UIComponent, raw)
		if ok_w and wrapped ~= nil then return wrapped end
		return raw
	end)
	if ok and got ~= nil then
		local id = inv_id_of(got)
		if id == nil or id == wanted then return got end
	end
	return nil
end

-- ONE bounded walk from the ui root, collecting every still-missing id at once.
-- Read-only; depth- and visit-bounded; every read pcall'd.
local function inv_walk(missing, found)
	local ok_r, root = pcall(function() return core:get_ui_root() end)
	if not ok_r or root == nil then return end

	local visits, max_visits = 0, 900
	local stack = { { node = root, depth = 0 } }
	while #stack > 0 and visits < max_visits do
		local item = table.remove(stack)
		local node, depth = item.node, item.depth
		visits = visits + 1

		local id = inv_id_of(node)
		if id ~= nil and missing[id] ~= nil and found[id] == nil then
			found[id] = node
		end

		if depth < 8 then
			local ok_n, n = pcall(function() return node:ChildCount() end)
			if ok_n and type(n) == "number" and n > 0 then
				for i = n - 1, 0, -1 do
					local ok_c, child = pcall(function() return node:Find(i) end)
					if ok_c and child ~= nil then
						local ok_w, wrapped = pcall(UIComponent, child)
						if ok_w and wrapped ~= nil then
							stack[#stack + 1] = { node = wrapped, depth = depth + 1 }
						end
					end
				end
			end
		end
	end
end

-- Resolve every wanted id, fresh each sweep: the engine's own Find per id,
-- then one shared walk for whatever is still missing.
local function inv_resolve(ids)
	local found = {}

	for i = 1, #ids do
		local got = inv_find(ids[i])
		if got ~= nil then found[ids[i]] = got end
	end

	local missing = {}
	local anything_missing = false
	for i = 1, #ids do
		if found[ids[i]] == nil then
			missing[ids[i]] = true
			anything_missing = true
		end
	end
	if anything_missing then inv_walk(missing, found) end

	-- Our own badges are special: if the engine's search cannot see a component
	-- WE created, the handle we already hold is the truth about it.
	for _, ability in ipairs(ABILITIES) do
		local state = ability_state[ability.marker]
		if found[ability.badge] == nil and state.badge ~= nil
			and inv_id_of(state.badge) == ability.badge then
			found[ability.badge] = state.badge
		end
	end

	return found
end

local function inv_rel_xy(uic)
	local ok, x, y = pcall(function() return uic:RelativePosition() end)
	if ok and type(x) == "number" and type(y) == "number" then return x, y end
	return nil, nil
end

local function inv_dock_xy(uic)
	local ok, x, y = pcall(function() return uic:GetDockOffset() end)
	if ok and type(x) == "number" and type(y) == "number" then return x, y end
	return nil, nil
end

-- One INVENTORY line. Every read is pcall'd and type-checked; a failed read
-- prints '?' and NEVER shortens the line. comp == nil means the candidate does
-- not exist right now - still a line, all fields '?', marked [not found].
local function inv_line(wanted, comp)
	if comp == nil then
		return "INVENTORY " .. wanted
			.. ": visible=? pos=(?,?) relpos=(?,?) dock=(?,?) state='?' key='?' [not found]"
	end

	local vis = "?"
	local ok_v, v = pcall(function() return comp:Visible(true) end)
	if ok_v and type(v) == "boolean" then
		vis = v and "true" or "false"
	end

	local px, py = read_xy(comp)
	local rx, ry = inv_rel_xy(comp)
	local dx, dy = inv_dock_xy(comp)

	local state = "?"
	local ok_s, s = pcall(function() return comp:CurrentState() end)
	if ok_s and type(s) == "string" then state = s end

	local key = "?"
	local ok_k, k = pcall(function() return comp:InterfaceFunction("AbilityKeyForScript") end)
	if ok_k then
		if type(k) == "string" and (safe_len(k) or 0) > 3 then
			key = k
		else
			key = "-"
		end
	end

	return "INVENTORY " .. wanted
		.. ": visible=" .. vis
		.. " pos=" .. fmt_xy(px, py)
		.. " relpos=" .. fmt_xy(rx, ry)
		.. " dock=" .. fmt_xy(dx, dy)
		.. " state='" .. state .. "'"
		.. " key='" .. key .. "'"
end

local function log_inventory_sweep()
	local found = inv_resolve(INVENTORY_FIXED)

	-- Children of button_parent whose id starts with 'button_order' (dynamic:
	-- the engine names them button_order1, button_order12, ... per unit).
	local order_children = {}
	local bp = found["button_parent"]
	if bp ~= nil then
		local ok_n, n = pcall(function() return bp:ChildCount() end)
		if ok_n and type(n) == "number" and n > 0 then
			for i = 0, n - 1 do
				local ok_c, child = pcall(function() return bp:Find(i) end)
				if ok_c and child ~= nil then
					local ok_w, cc = pcall(UIComponent, child)
					if ok_w and cc ~= nil then
						local cid = inv_id_of(cc)
						if cid ~= nil and string.sub(cid, 1, 12) == "button_order" then
							order_children[#order_children + 1] = { id = cid, comp = cc }
						elseif cid == nil then
							-- a child whose id cannot be read: still a line, never skipped
							order_children[#order_children + 1] =
								{ id = "button_order?[" .. tostring(i + 1) .. "]", comp = cc }
						end
					end
				end
			end
		end
	end

	local found_count = #order_children
	for i = 1, #INVENTORY_FIXED do
		if found[INVENTORY_FIXED[i]] ~= nil then found_count = found_count + 1 end
	end
	local total = #INVENTORY_FIXED + #order_children

	-- Run whenever one of our ability buttons OR any candidate exists; stay
	-- silent only when there is nothing at all to report on.
	local any_button = false
	for _, ability in ipairs(ABILITIES) do
		if ability_state[ability.marker].button ~= nil then any_button = true end
	end
	if not any_button and found_count == 0 then return end

	log("INVENTORY sweep t=" .. string.format("%.1f", tick_count * POLL_MS / 1000) .. "s"
		.. " found=" .. tostring(found_count) .. "/" .. tostring(total))

	log(inv_line("SA_dial", found["SA_dial"]))
	log(inv_line("dial_frame", found["dial_frame"]))
	log(inv_line("button_parent", found["button_parent"]))
	for i = 1, #order_children do
		log(inv_line(order_children[i].id, order_children[i].comp))
	end
	log(inv_line("button_ability", found["button_ability"]))
	for i = 1, 6 do
		log(inv_line("button_ability" .. tostring(i), found["button_ability" .. tostring(i)]))
	end
	for i = 1, 6 do
		log(inv_line("button_slot" .. tostring(i), found["button_slot" .. tostring(i)]))
	end
	log(inv_line("behaviour_parent", found["behaviour_parent"]))
	log(inv_line("orders_parent", found["orders_parent"]))
	log(inv_line("army_ability_parent", found["army_ability_parent"]))
	log(inv_line("ability_parent", found["ability_parent"]))
	log(inv_line("zz_auto_badge", found["zz_auto_badge"]))
	log(inv_line("zz_auto_badge_fs", found["zz_auto_badge_fs"]))
end

-- ============================================================================
-- 8e. THE SELECTION - the engine's selection callback FIRST, the card sweep
--     as the fallback and reconciliation, both converging on ONE set
--     (selected_ui_ids) and ONE tracker (selected_unit_id):
--
--     * THE ENGINE SELECTION CONVERGENCE (converge_engine_selection) runs on
--       every ui tick BEFORE the sweep: the callback (section 3b) maintains
--       the set event by event; the convergence folds any change into ONE
--       logged line naming the whole set
--           selection callback: <n> unit(s) selected now (<id1>, <id2>, ...)
--       adopts the tracker with the same rule the card derivation uses, and
--       refreshes the badge letters - all ONCE per change, never once per
--       unit event (a ten-unit box selection is one line, not ten).
--
--     * THE CARD SWEEP - the player's unit cards DRIVE THE SELECTION when no
--       callback event has EVER been delivered (API missing / behaviour
--       differs - the unchanged fallback), and RECONCILE the callback-fed
--       set otherwise (a card-reported id is added; a card-added id is
--       dropped once the cards stop reporting it). At TWO cadences:
--
--     * THE FAST PATH (fast_card_selection) runs on EVERY ui tick: it reads
--       the tracked units' card states and derives the selection the same
--       way the census always did (exactly one card reports 'selected' ->
--       adopt its id; several -> keep the tracker when it is one of them,
--       else the deterministic first; none/failed -> keep). On any change it
--       adopts the derived id and refreshes both badges' letters with the
--       tick number on the established header:
--           selection changed to <ui_id> - refreshing badge letters (tick N)
--       so the change reaches the tracker AND the letters within ONE ui tick
--       (~50 ms) instead of waiting up to a second for the next census. It
--       is QUIET while nothing changes - no notes, no summary, no repeated
--       lines - and on a change it includes the card lines ONCE, so the
--       change is documented with the states that caused it.
--
--     * THE VERBOSE CENSUS (log_card_sweep) stays at ONE BLOCK PER ~1 s of
--       battle time exactly as before (the 4 x 250 ms gate, same lines): the
--       once-per-change notes, its own adoption line should it ever get
--       there first, then the summary and one line per card:
--           card <ui_id> state='<CurrentState()>' visible=<true|false>
--           cards: selected-tracker=<ui_id or none>
--       with the [selected-tracker] tag on the card the tracker currently
--       names. The fast path runs first on every tick, so in practice the
--       census reports; its adoption branch stays as the safety net.
--
--     Both cadences share ONE read and ONE derivation (read_tracked_card_states
--     + derive_selection_from_cards) and one card-line writer (log_card_lines),
--     so they can never disagree about what the cards say.
--
--     The engine marks the selected unit's card with CurrentState() ==
--     'selected' (measured in battle: the selected card reads 'selected',
--     every other card reads 'active'); the card CLICK path stays as an
--     immediate fast-path (it sets the tracker on the spot), but the card
--     states win: whatever a click set, the next ui tick's read follows the
--     game. For each tracked unit (the read collects up to CARD_SWEEP_MAX
--     wanted ids first - a runaway guard, not a working limit: see the
--     constant below), the unit's CARD is the component in the cards panel
--     whose Id() EQUALS
--     the unit's unique_ui_id() - the proven bridge (vanilla matches
--     uic_card:Id() == unit:unique_ui_id() the same way; the card clicks
--     this build routes rely on exactly that identity). Every engine read is
--     pcall'd and type-checked: a failing or hostile read prints '?' and
--     NEVER shortens a line, and nothing here can error out of the tick.
--     Ids are matched by EXACT EQUALITY on a copied string - there is no
--     find of any kind (string.find is banned from this file). The walk is
--     depth- and visit-bounded; NOTHING here writes to any component.
-- ============================================================================

local CARD_SWEEP_EVERY_N_POLL_TICKS = 4      -- 4 x 250 ms = ~1 s of battle time
local last_card_sweep_tick = -1000           -- so the first tick with units sweeps at once
-- A RUNAWAY GUARD, not a working limit: a single-player unit-card panel
-- tops out at 20 cards, so 40 can never bind for a real army - it is only
-- a belt against a pathological wanted-list (the walk itself is separately
-- visit-bounded). The old value (12) was a legacy work-cap that made units
-- past the 12th collected card invisible to selection tracking.
local CARD_SWEEP_MAX = 40                    -- at most this many wanted ids per read

-- The last state-note this sweep logged (the multiple-selected and the
-- no-card-selected lines). A note is logged only when its TEXT changes -
-- once per change - so a steady state stays quiet however many sweeps pass.
local last_selection_note = nil

-- Resolve the cards-panel container by id: the engine's recursive Find from
-- the ui root first (the same call the inventory sweep proves works),
-- verified against the component's own id; nil when the search finds nothing
-- usable, so the caller can fall back to the ui root itself.
local function card_panel_find(root, wanted)
	local ok, got = pcall(function()
		local raw = root:Find(wanted, false)   -- false = do not assert when missing
		if raw == nil then return nil end
		local ok_w, wrapped = pcall(UIComponent, raw)
		if ok_w and wrapped ~= nil then return wrapped end
		return raw
	end)
	if ok and got ~= nil and inv_id_of(got) == wanted then return got end
	return nil
end

-- ONE bounded walk of the panel subtree, collecting the wanted cards: every
-- node's id is read through pcall (a failing read is simply not a card - the
-- walk carries on), the walk is visit- and depth-bounded like the inventory
-- walk, and each child read is pcall'd. Nothing here can raise.
local function card_collect_from(start, wanted, found)
	local visits, max_visits = 0, 900
	local stack = { { node = start, depth = 0 } }
	while #stack > 0 and visits < max_visits do
		local item = table.remove(stack)
		local node, depth = item.node, item.depth
		visits = visits + 1

		local id = inv_id_of(node)
		if id ~= nil and wanted[id] ~= nil and found[id] == nil then
			found[id] = node
		end

		if depth < 8 then
			local ok_n, n = pcall(function() return node:ChildCount() end)
			if ok_n and type(n) == "number" and n > 0 then
				for i = n - 1, 0, -1 do
					local ok_c, child = pcall(function() return node:Find(i) end)
					if ok_c and child ~= nil then
						local ok_w, wrapped = pcall(UIComponent, child)
						if ok_w and wrapped ~= nil then
							stack[#stack + 1] = { node = wrapped, depth = depth + 1 }
						end
					end
				end
			end
		end
	end
end

-- THE SHARED CARD READ (this build - the sweep is split into two cadences).
-- Resolves the tracked units' cards and reads each card's engine state ONCE.
-- Both cadences use it - the FAST path on every ui tick and the verbose
-- once-per-second census - so they can never disagree about what the cards
-- say. Every read is pcall'd and type-checked like the census always was: a
-- failing or hostile read prints '?' and NEVER shortens a line.
-- Returns:
--   ordered  - the wanted ids, sorted, so "the first selected card" is a
--              stable, reproducible choice. The COLLECTION order is the
--              tracked array's own order (items 14 + 6), each entry read
--              through its cached ui id - never pairs() order, so under
--              CARD_SWEEP_MAX the swept subset is the same every call
--   found    - id -> the card component found for it (absent = not found)
--   states   - id -> the card's CurrentState() string ('?' on a failed read)
--   selected - the ids whose state reads exactly 'selected', ordered order
-- ROUND 129: the cards veto a ghost selection (see the reconciliation below).
FOURTH.CARD_DESELECT_CONFIRM_POLLS = 2   -- 2 x 250 ms: a card must read unselected this long
FOURTH.card_unselected_since = {}        -- id -> the poll its card first read unselected
-- The card states that mean "NOT selected" (every one seen in the 2026-11-03
-- battles). Any other state (the selected ones, '?', or one never seen) drops nothing.
FOURTH.CARD_UNSELECTED_STATES = { active = true, hover = true, inactive = true, taking_damage = true, wavering = true }

local function read_tracked_card_states()
	-- THE WANTED IDS, IN A STABLE ORDER (items 14 + 6 - ONE fix with the
	-- cached id in section 6). Old shape: the lookup table walked with
	-- pairs() - which has NO defined order (in-process hash order) - so above
	-- CARD_SWEEP_MAX the collected SUBSET - and with it which cards got
	-- state-read - changed from call to call. The ordered watch list is now
	-- the source: iterate tracked_units BY INDEX and read each entry's CACHED
	-- ui id (attached at registration), so the first CARD_SWEEP_MAX ids are
	-- ALWAYS the same list. No pairs(), no engine read on the cached path.
	-- The cap is unchanged as a runaway guard: a real panel (<= 20 cards)
	-- never reaches it, and past it units are now EXCLUDED CONSISTENTLY (a
	-- stable truncation) instead of flickering in and out of the sweep.
	local wanted, wanted_count = {}, 0
	local ordered = {}
	if tracked_units ~= nil then
		for i = 1, #tracked_units do
			if wanted_count >= CARD_SWEEP_MAX then break end
			local su = tracked_units[i]
			local cached = su and su.zz_tracked_ui_id
			if cached == nil then
				-- Every registered entry carries the cache, so this branch is
				-- unreachable; kept only as a defensive fallback for an entry
				-- with no cached id yet (the old pcall'd engine read).
				local unit = su and su.unit
				if unit ~= nil then
					local ok_id, id = pcall(function() return unit:unique_ui_id() end)
					if ok_id and id ~= nil then cached = tostring(id) end
				end
			end
			if cached ~= nil and wanted[cached] == nil then
				wanted[cached] = true
				ordered[#ordered + 1] = cached
				wanted_count = wanted_count + 1
			end
		end
	end
	table.sort(ordered)

	local found = {}
	if wanted_count > 0 then
		local ok_r, root = pcall(function() return core:get_ui_root() end)
		if ok_r and root ~= nil then
			-- The cards panel: 'card_panel_docker', else 'cards_panel', else
			-- the ui root itself (the walk then simply looks from the top).
			-- NOT finding the panel is not fatal - the derivation simply
			-- sees no cards this read.
			local start = card_panel_find(root, "card_panel_docker")
			if start == nil then start = card_panel_find(root, "cards_panel") end
			if start == nil then start = root end
			card_collect_from(start, wanted, found)
		end
	end

	-- Every card's engine state, read ONCE (pcall'd and type-checked; '?' on
	-- failure and never a claim): a card whose state reads exactly 'selected'
	-- is one of the units the game currently has selected.
	local states = {}
	local selected = {}
	for i = 1, #ordered do
		local ui_id = ordered[i]
		local card = found[ui_id]
		if card ~= nil then
			local state = "?"
			local ok_s, s = pcall(function() return card:CurrentState() end)
			if ok_s and type(s) == "string" then state = s end
			states[ui_id] = state
			if state == "selected" then
				selected[#selected + 1] = ui_id
			end
		end
	end

	-- THE SELECTED SET (this build): expose the WHOLE group, not just the
	-- single-choice derivation built over it - the badge click and the
	-- collective letter read selected_ui_ids (section 2). Two regimes:
	--   * NO callback event has EVER been delivered (API missing, or the
	--     engine never called back): the cards are in charge and REPLACE the
	--     set, exactly as before - the unchanged fallback. A read that found
	--     no cards at all leaves the set alone, like the derivation keeping
	--     the tracker.
	--   * the callback HAS delivered (it is the engine's own word on group
	--     selections, which the cards do not report): the callback-fed set is
	--     in charge. The cards may still ADD an id the set has not seen (a
	--     single selection whose event did not arrive) - and such a
	--     card-added id is dropped again once the cards stop reporting it, so
	--     the reconciliation can never leave a phantom selected unit behind.
	if next(found) ~= nil then
		if not selection_callback_alive then
			selected_ui_ids = selected
		else
			for i = 1, #selected do
				local id = selected[i]
				if not engine_selection_has(id) then
					selected_ui_ids[#selected_ui_ids + 1] = id
					reconciled_card_ids[id] = true
					selection_set_dirty = true
				end
			end
			for id in pairs(reconciled_card_ids) do
				local still_reported = false
				for i = 1, #selected do
					if selected[i] == id then still_reported = true end
				end
				if not still_reported then
					reconciled_card_ids[id] = nil
					for i = #selected_ui_ids, 1, -1 do
						if selected_ui_ids[i] == id then
							table.remove(selected_ui_ids, i)
							selection_set_dirty = true
						end
					end
				end
			end
			-- ROUND 129: THE CARDS VETO A GHOST SELECTION. After a box
			-- selection the engine may never send the "deselected" events
			-- (field battle 2026-11-03: seven selected, then one clicked,
			-- two ghosts stayed for the rest of the battle and fix A never
			-- saw "exactly one selected"). A unit whose own card reads a
			-- known UNSELECTED state for CARD_DESELECT_CONFIRM_POLLS polls
			-- is not selected: drop it. A card not found, or any other
			-- state, is no evidence and drops nothing.
			for i = #selected_ui_ids, 1, -1 do
				local id = selected_ui_ids[i]
				local st = states[id]
				if st ~= nil and FOURTH.CARD_UNSELECTED_STATES[st] == true then
					local since = FOURTH.card_unselected_since[id]
					if since == nil then
						FOURTH.card_unselected_since[id] = tick_count
					elseif (tick_count - since) >= FOURTH.CARD_DESELECT_CONFIRM_POLLS then
						table.remove(selected_ui_ids, i)
						FOURTH.card_unselected_since[id] = nil
						reconciled_card_ids[id] = nil
						selection_set_dirty = true
						log(string.format("selection: card %s reads '%s' - the game never sent its deselection; dropped from the selected set (%d selected now)",
							tostring(id), st, #selected_ui_ids))
					end
				else
					FOURTH.card_unselected_since[id] = nil
				end
			end
		end
	end

	return ordered, found, states, selected
end

-- THE SHARED DERIVATION (this build): the engine's own signal decides the
-- selection, exactly as the census always did. Given the ordered selected
-- list:
--   * exactly one card reports 'selected' -> adopt its id;
--   * several (group selection)           -> keep the tracker when it is one
--     of them, else take the first (ordered) selected card;
--   * none (or the reads fail)            -> keep the tracker.
-- Returns the id to adopt (nil when nothing can be adopted) plus the note
-- text the verbose census logs once per change; the FAST path stays quiet
-- and ignores the note.
local function derive_selection_from_cards(previous, selected)
	local derived = nil
	local note = nil
	if #selected == 1 then
		derived = selected[1]
	elseif #selected > 1 then
		-- Group selection: keep the tracker when it is one of the selected
		-- cards, else take the first (ordered) one.
		derived = previous
		local among = false
		for i = 1, #selected do
			if selected[i] == previous then among = true end
		end
		if not among then derived = selected[1] end
		note = "multiple selected cards - tracker=" .. tostring(derived)
	else
		-- No card reports 'selected' (or the reads failed): keep the current
		-- value, and say so once per change (the note-text dedupe below).
		note = "no card reports selected - tracker stays " .. tostring(previous)
	end
	return derived, note
end

-- ONE CARD-LINE BLOCK (this build): the per-card census lines, in the same
-- ordered sequence: each card's state and visibility, the card the tracker
-- currently names tagged [selected-tracker]. Used by the verbose census once
-- per second AND by the fast path when the selection changes (the change is
-- then documented with the card states that caused it, once). Every read is
-- pcall'd and type-checked: a failing read prints '?' and NEVER shortens a
-- line. Nothing here writes to any component.
local function log_card_lines(ordered, found, states, tracker)
	for i = 1, #ordered do
		local ui_id = ordered[i]
		local card = found[ui_id]
		if card ~= nil then
			local state = states[ui_id] or "?"

			local vis = "?"
			local ok_v, v = pcall(function() return card:Visible(true) end)
			if ok_v and type(v) == "boolean" then vis = v and "true" or "false" end

			local line = "card " .. tostring(ui_id) .. " state='" .. state .. "' visible=" .. vis
			if tracker ~= "none" and tostring(ui_id) == tracker then
				line = line .. " [selected-tracker]"
			end
			log(line)
		end
	end
end

-- THE FAST PATH (this build): the selection is derived from the card states
-- on EVERY ui tick, so a change - a card click on the battlefield, a group
-- select, the engine's own reselection - is adopted, and both badges'
-- letters refreshed, within ONE ui tick instead of waiting for the next
-- census. It is QUIET unless the tracker actually changes: no notes, no
-- summary, no repeated lines. On a change it adopts the derived id, logs the
-- established header with the tick number on it
--     selection changed to <ui_id> - refreshing badge letters (tick N)
-- refreshes both badges' letters in the same call, and includes the card
-- lines ONCE - the change's own evidence block. Every read is pcall'd (the
-- shared reader above) and the caller pcalls this function, so nothing here
-- can error out of the ui tick.
-- In callback mode (section 3b) this path keeps only its single-select job:
-- the shared read hands the set to the callback regime, and the derivation
-- below adopts a change the callback has not reported yet (or adopts first in
-- the fallback world, exactly as it always did).
local function fast_card_selection()
	local previous = "none"
	if selected_unit_id ~= nil then previous = tostring(selected_unit_id) end

	local ordered, found, states, selected = read_tracked_card_states()
	local derived = derive_selection_from_cards(previous, selected)
	if derived == nil or derived == previous then return end

	-- THE SELECTION CHANGED: adopt it, refresh the letters (tick-stamped),
	-- and include the card lines once.
	walk_on_selection_change = true   -- the dial now belongs to the adopted unit
	selected_unit_id = derived
	refresh_badge_letters_for_selection(derived, tick_count)
	log_card_lines(ordered, found, states, tostring(derived))
end

-- THE ENGINE SELECTION CONVERGENCE (this build): the callback (section 3b)
-- maintains selected_ui_ids event by event; this runs on every ui tick and
-- turns whatever it collected into ONE coalesced act:
--   * ONE log line per set change, naming the whole set - a box selection of
--     ten units is ONE line, never ten (the signature below collapses any
--     burst of events between two ticks, and a steady set costs one string
--     compare and nothing else);
--   * the tracker adoption - the same rule the card derivation uses, so the
--     two mechanisms can never disagree (one selected id -> adopt it; several
--     -> keep the tracker when it is among them, else the first; none -> keep
--     it);
--   * the badge letters: refreshed in the same call (with the established
--     tick-stamped line when the tracker moves, per letter - silently unless
--     a letter really changed - when only the collective state changed).
local function converge_engine_selection(tick)
	if not selection_set_dirty then return end
	selection_set_dirty = false

	local ids = {}
	for i = 1, #selected_ui_ids do ids[i] = tostring(selected_ui_ids[i]) end
	table.sort(ids)
	local sig = table.concat(ids, ",")
	if sig == selection_set_sig then return end
	selection_set_sig = sig

	log("selection callback: " .. tostring(#ids) .. " unit(s) selected now ("
		.. (#ids > 0 and table.concat(ids, ", ") or "none") .. ")")

	local previous = "none"
	if selected_unit_id ~= nil then previous = tostring(selected_unit_id) end
	local derived = derive_selection_from_cards(previous, ids)
	if derived ~= nil and derived ~= previous then
		walk_on_selection_change = true   -- the dial now belongs to the adopted unit
		selected_unit_id = derived
		refresh_badge_letters_for_selection(derived, tick)
	else
		for _, ability in ipairs(active_abilities_list()) do
			refresh_badge_letter(ability.marker)
		end
	end
end

-- THE VERBOSE CENSUS (the once-per-second half of the split - the same gate,
-- the same lines, the same formats as it has had since it was built): the
-- notes once per change, its own adoption (the safety net - in practice the
-- fast path above ran first on every tick), the summary, then the per-card
-- lines. See the section header. Every engine read is pcall'd and
-- type-checked; nothing here can error out of the tick.
local function log_card_sweep()
	local previous = "none"
	if selected_unit_id ~= nil then previous = tostring(selected_unit_id) end

	local ordered, found, states, selected = read_tracked_card_states()
	local derived, note = derive_selection_from_cards(previous, selected)

	if note ~= nil then
		if note ~= last_selection_note then
			log(note)
			last_selection_note = note
		end
	else
		last_selection_note = nil
	end

	if derived ~= nil and derived ~= previous then
		log("selection updated from card states: " .. previous .. " -> " .. derived)
		selected_unit_id = derived
		walk_on_selection_change = true   -- the census adoption re-homes the dial too
		-- THE SELECTION CHANGED: refresh BOTH badges' letters from the new
		-- selection in this same call. The fast path and its per-tick
		-- safety net are the convergence mechanism now; this stays for the
		-- case where the census itself adopts first.
		refresh_badge_letters_for_selection(derived)
	end

	local tracker = "none"
	if selected_unit_id ~= nil then tracker = tostring(selected_unit_id) end
	log("cards: selected-tracker=" .. tracker)

	-- One line per card found, in the same ordered sequence: its state and
	-- visibility, the card the tracker currently names tagged.
	log_card_lines(ordered, found, states, tracker)
end

-- ============================================================================
-- 9. START IT UP
--    The poll, the on/off button, and the watchdog that keeps the poll alive.
-- ============================================================================

-- The watchdog's bookkeeping. Round 16 declared these where round 19's deletion removed them,
-- which silently left them as globals - harmless until the stall branch ran, where the arithmetic
-- on a nil would throw and take the UI timer with it. Caught by the mock, not by a battle.
local last_seen_tick = -1
local stalled_checks = 0

local function phase_ui_refresh()
	find_ability_buttons()          -- the abilities' own icons (section 8b)
	for _, ability in ipairs(ABILITIES) do
		apply_ability_feedback(ability.marker)  -- keep each badge's letter in step with the collective switch
	end
	last_seen_tick = tick_count     -- so the watchdog does not read this as a stall
end

bm:register_phase_change_callback("Deployment", function()
	local ok, err = pcall(phase_ui_refresh)
	if not ok then log("phase_ui_refresh (Deployment) FAILED: " .. tostring(err)) end
end)
bm:register_phase_change_callback("Deployed", function()
	local ok, err = pcall(phase_ui_refresh)
	if not ok then log("phase_ui_refresh (Deployed) FAILED: " .. tostring(err)) end
end)
bm:register_phase_change_callback("Deployed", function()
	local ok, err = pcall(function()
		log("combat phase started - building watch list")
		rebuild_unit_list()
	end)
	if not ok then log("deployed callback failed: " .. tostring(err)) end
end)

-- Diagnostic: the phase dispatcher triggers this event unconditionally, so its
-- presence (or absence) tells us whether phase changes reach scripts at all.
core:add_listener(
	"zz_deadly_onslaught_phase_watch",
	"ScriptEventBattlePhaseChanged",
	function(context) return true end,
	function(context)
		-- Log only. Painting here is what broke round 12: the phase dispatcher
		-- runs this via core:trigger_event, and UI work inside it stopped the
		-- whole phase system after Startup.
		log("phase change seen: " .. tostring(context.string))
	end,
	true
)

-- ============================================================================
-- THE AIR-DROP FAST PASS (round 114) - a SECOND timer, and the only thing it
-- schedules.
--
-- THE USER'S RULING (verbatim): "I want the trigger to be checked much more
-- frequently when armed and less than 30 meters from a valid enemy unit."
--
-- WHAT IT RUNS: FOURTH.ad_pick - THE SAME EVALUATOR the poll runs (one copy of
-- the rule, not a second implementation) - and it casts through
-- FOURTH.try_pair, THE SAME readiness + gate + cast sequence the poll uses. The
-- air-drop rule is therefore identical whichever timer reaches it.
--
-- WHEN IT RUNS: only in the conflict phase, only when the watch list exists,
-- only for ALIVE units the player has ARMED for one of the air-drop markers
-- (FOURTH.ad_fast_abilities, the 12 entries built at load), and only while a
-- VALID enemy (alive, more than AIR_DROP_MIN_MEN models, readable centre gap)
-- is inside AIR_DROP_NEAR_M = 30 m. Outside 30 m it does nothing but note the
-- transition.
--
-- ISOLATION: it never touches tick_count, the re-list, the heartbeat, the
-- identity watch, the active set or any NON-air-drop ability - the loop is over
-- FOURTH.ad_fast_abilities, never over ABILITIES. The global poll's interval and
-- every other ability's cadence are unchanged.
--
-- NO DOUBLE CAST: the guard, charge, in-flight and per-unit serialisation holds
-- are stamped in POLL ticks by the shared FOURTH.try_pair, and the guard is
-- written BEFORE the call. A second fast tick inside the same poll window finds
-- (tick_count - last_attempt) = 0, which is below GUARD_TICKS, so the pair is not
-- eligible - the fast pass can only ever advance a cast by less than one guard.
-- Harness 114 proves it with two consecutive fast ticks (one cast) and with a
-- fast tick immediately after a poll cast (still one).
function FOURTH.ad_fast_pass()
	if tracked_units == nil then return end
	if not bm:is_conflict_phase() then return end
	local list = FOURTH.ad_fast_abilities
	if list == nil or #list == 0 then return end
	local gone = {}
	for i = 1, #tracked_units do
		local script_unit = tracked_units[i]
		local unit = script_unit and script_unit.unit
		if unit ~= nil then
			local ok_alive, alive = pcall(function() return unit:number_of_men_alive() end)
			if ok_alive and type(alive) == "number" and alive > 0 then
				local ok_id, uid = pcall(function() return unit:unique_ui_id() end)
				if ok_id and uid ~= nil then
					for j = 1, #list do
						local ability = list[j]
						if is_armed(unit, ability.marker) then
							-- THE SAME CANDIDATE SCAN the evaluator uses, once, for
							-- the 30 m gate: the fast pass must not decide anything
							-- about WHO is valid on its own.
							local enemy, dist = FOURTH.ad_nearest(unit)
							local near = (enemy ~= nil and dist ~= nil
								and dist < FOURTH.AIR_DROP_NEAR_M)
							local was = (FOURTH.ad_fast_on[uid] == true)
							if near ~= was then
								FOURTH.ad_fast_on[uid] = near
								if near then
									log("  " .. FOURTH.ad_tag(unit) .. "fast poll: ON (nearest valid "
										.. string.format("%.1f", dist) .. "m)")
								else
									log("  " .. FOURTH.ad_tag(unit) .. "fast poll: OFF")
								end
							end
							if near then
								-- THE CURRENT ENTRY'S OWN SLOTS, exactly as the poll
								-- sets them before its evaluate call.
								FOURTH.ad_marker = ability.marker
								FOURTH.ad_air_only = (ability.air_only == true)
								FOURTH.ad_no_melee = (ability.no_melee == true)
								FOURTH.ad_range_m = ability.range_m
								FOURTH.ad_enemy = nil
								FOURTH.ad_caster_su = nil
								local routing = unit_is_routing(unit)
								local reason = ability.evaluate(unit, routing)
								if reason ~= nil then
									local ability_key = target_key_by_unit[uid]
									if FOURTH.try_pair(script_unit, unit, ability, uid,
										ability_key, reason, gone) == "gone" then
										break
									end
								end
							end
						end
					end
				end
			end
		end
	end
	for g = 1, #gone do
		drop_unit_by_ui_id(gone[g])
	end
end

bm:repeat_callback(poll, POLL_MS, POLL_NAME)

-- THE FAST PASS'S OWN REGISTRATION (round 114). A second model timer at
-- AIR_DROP_FAST_S (0.2 s = 200 ms), wrapped in its own pcall exactly like the
-- poll: an error escaping a timer callback aborts the battle model's timer
-- driver and would kill EVERY repeating callback, so it is caught and counted.
-- The global poll above keeps POLL_MS and its own name - nothing about it moves.
FOURTH.ad_fast_errors = 0
bm:repeat_callback(function()
	local ok, err = pcall(FOURTH.ad_fast_pass)
	if not ok then
		FOURTH.ad_fast_errors = FOURTH.ad_fast_errors + 1
		if FOURTH.ad_fast_errors <= 3 or (FOURTH.ad_fast_errors % 40) == 0 then
			log("AIR-DROP FAST ERROR #" .. tostring(FOURTH.ad_fast_errors)
				.. " (the fast pass stops, the poll is untouched): " .. tostring(err))
		end
	end
end, math.floor(FOURTH.AIR_DROP_FAST_S * 1000), "zz_test_deadly_onslaught_air_drop_fast")

-- POLL WATCHDOG (real / UI timer, 500 ms)
-- The poll is the only thing watching for charges, and UI work in a phase
-- callback can kill the model timer that drives it (rounds 9, 10, 13). This runs
-- in the UI timer - the one context that has never died - and only checks whether
-- the poll's tick counter is still moving; if it is not, the poll is put back.
-- Nothing is created or painted from here.
-- ---------------------------------------------------------------------------
local ui_ticks = 0

local function ui_tick()
	ui_ticks = ui_ticks + 1
	if ui_ticks == 1 then
		log("ui timer is running (real callback, 500 ms) - watching the poll")
	end

	-- Watch the poll's tick counter and REPORT only: touching the timer registry from a UI
	-- context is what broke the trigger in round 17. While the ability icons are still
	-- unknown, keep trying to find them - the orders bar does not exist in the early
	-- phases, so the first attempts are expected to fail.
	-- THE DEFERRED CREATION (this build): a claim in the walk only records the
	-- button and raises pending_badge[marker] (scan_component_body); the badge
	-- itself is built HERE, on the tick, one instrumented pcall'd step at a
	-- time - never from inside the walk. A step that fails is logged with its
	-- own err line, the badge stays absent and the next tick retries, up to
	-- MAX_BADGE_ATTEMPTS per claim; after that the marker waits for the dial to
	-- rebuild (a fresh claim resets the budget).
	for _, ability in ipairs(active_abilities_list()) do
		local marker = ability.marker
		local state = ability_state[marker]
		if state.badge == nil and state.button ~= nil and pending_badge[marker] ~= nil
			and badge_gave_up[marker] == nil then
			if (badge_attempts[marker] or 0) >= MAX_BADGE_ATTEMPTS then
				badge_gave_up[marker] = true
				log("badge " .. marker .. ": giving up until the dial rebuilds ("
					.. tostring(MAX_BADGE_ATTEMPTS) .. " failed attempts)")
			else
				badge_attempts[marker] = (badge_attempts[marker] or 0) + 1
				local ok, err = pcall(create_badge, marker)
				if not ok then
					discard_badge(state)
					log("badge " .. marker .. ": create attempt raised: " .. tostring(err))
				end
			end
		end
		if state.badge ~= nil then pending_badge[marker] = nil end
	end

	-- HIDDEN RELIABLY, NOT ON TRANSITIONS ALONE. Every tick, per ability: the
	-- DESIRED visibility is recomputed from the CLAIMED SET - the marker is
	-- claimed on the dial right now (marker_claimed_now: the claimed button
	-- reference still read as ours by the same key gate the scan used) AND
	-- there is a button reference - and whenever it differs from what the
	-- tick last applied (state.badge_shown), the badge is set to the desired
	-- state again, with exactly one log line for the change. No path can
	-- leave a badge visible while its marker is unclaimed: badge_visible
	-- (the letter path) no longer touches visibility at all, and the console
	-- hooks write the same bookkeeping so the next tick corrects them too.
	-- This holds after a dial rebuild, a slot change and an ability
	-- disappearing from the dial - whatever moved the dial.
	-- Per ability: judge ITS marker and show/hide/letter ITS own badge.
	local onslaught_confirmed = false
	local active_dropped = false    -- item 1.4: a stale claim died this tick - the set shrank

	for _, ability in ipairs(active_abilities_list()) do
		local state = ability_state[ability.marker]

		-- IS THE MARKER CLAIMED ON THIS DIAL RIGHT NOW? The same test the
		-- badge click guard runs, from the one shared place. A read that
		-- raises, an empty key or a foreign key means gone: the claim dies
		-- with the button (a rebuilt dial loses its stale claim).
		local claimed = marker_claimed_now(ability)
		if not claimed and state.button ~= nil then
			state.button = nil
			pending_badge[ability.marker] = nil   -- a stale claim dies with the button
			active_dropped = true
		end

		if ability.marker == "onslaught" then onslaught_confirmed = claimed end

		if state.badge ~= nil then
			local desired = claimed and state.button ~= nil

			if (state.badge_shown == true) ~= desired then
				state.badge_shown = desired
				pcall(function() state.badge:SetVisible(desired) end)
				if desired then
					log("badge " .. ability.marker .. ": shown (marker claimed)")
				else
					log("badge " .. ability.marker .. ": hidden (marker not claimed on this dial)")
				end
			end

			if state.badge_shown == true then
				-- THE PER-TICK SAFETY NET (this build): whichever event moved
				-- the selection or a unit's armed state, the letter is
				-- re-derived here every tick from the COLLECTIVE switch read
				-- (one unit: its own flag; several: all owners armed?) and
				-- re-written ONLY when it differs from the cached last
				-- letter (state.last_letter). So the display converges
				-- within one tick (250 ms) of ANY change, and a steady letter
				-- stays completely silent - no repeated SetText, no repeated
				-- line.
				refresh_badge_letter(ability.marker)
			end
		end
		if state.badge ~= nil then pcall(place_badge, ability.marker) end
	end

	-- ITEM 1.4 - a stale claim dropped this tick shrank the inputs: refresh
	-- the active set (silent unless the membership moved).
	if active_dropped then refresh_active_abilities() end

	-- THE DIAL DUMP (section 8c): while the dial positively shows our ability, one
	-- read-only census block per ~1 s of battle time. pcall'd so a surprise can
	-- never take the UI tick down with it.
	if onslaught_confirmed and (tick_count - last_dial_dump_tick) >= DIAL_DUMP_EVERY_N_POLL_TICKS then
		last_dial_dump_tick = tick_count
		pcall(log_dial_dump)
	end

	-- THE INVENTORY SWEEP (section 8d): one read-only block per ~1 s of battle
	-- time, whenever our ability button OR any candidate component can be found
	-- - not only while the dial is confirmed. pcall'd like the dump above so a
	-- surprise can never take the UI tick down with it.
	if (tick_count - last_inventory_tick) >= INVENTORY_EVERY_N_POLL_TICKS then
		last_inventory_tick = tick_count
		pcall(log_inventory_sweep)
	end

	-- THE ENGINE SELECTION CONVERGENCE (section 8e): the callback (section 3b)
	-- may have collected selection/deselection events since the last tick;
	-- fold them into ONE logged set change (exactly one line naming the whole
	-- set), adopt the tracker and refresh the badge letters before the card
	-- fast path reads anything. pcall'd like everything else so a surprise
	-- can never take the UI tick down.
	pcall(converge_engine_selection, tick_count)

	-- THE CARD SELECTION, FAST (section 8e): derived from the engine's own
	-- 'selected' card states on EVERY ui tick, so a selection change reaches
	-- the tracker and both badge letters within ONE tick (~50 ms). Quiet
	-- unless the tracker changes; on a change it logs the tick-stamped header
	-- and the card lines once. pcall'd like everything else so a surprise can
	-- never take the UI tick down.
	pcall(fast_card_selection)

	-- THE VERBOSE CARD SWEEP (section 8e): still one block per ~1 s of battle
	-- time - the same gate, the same lines. The fast path above ran first on
	-- this tick, so the sweep mostly reports; its own adoption branch stays
	-- as the safety net. pcall'd like the sweeps above so a surprise can
	-- never take the UI tick down.
	if (tick_count - last_card_sweep_tick) >= CARD_SWEEP_EVERY_N_POLL_TICKS then
		last_card_sweep_tick = tick_count
		pcall(log_card_sweep)
	end

	if tick_count == last_seen_tick then
		stalled_checks = stalled_checks + 1
		-- 12 strikes = 6 seconds of real time with no model time passing. Long enough that the
		-- pause menu (which freezes model time) does not read as a dead timer - round 20's log
		-- flagged a "stall" that was almost certainly the player being paused.
		if stalled_checks == 12 then
			log("WATCHDOG: model time has not advanced for 6 s (tick " .. tostring(tick_count)
				.. ") - paused, or the poll is dead. NOT repairing it (the timer registry must not be touched from a UI context)")
		end
	else
		stalled_checks = 0
	end
	last_seen_tick = tick_count

	-- THE REASONED HUD WALK (this build). The walk runs only when there is a
	-- reason to expect OUR buttons on the dial:
	--   * a selection change this tick, or a newly tracked unit from the
	--     re-list (coalesced - one walk at most): walk immediately;
	--   * nothing known yet about the selected unit's keys (early battle, or
	--     nothing selected): walk as before, every other tick - the
	--     BOOTSTRAPPING phase;
	--   * the selected unit OWNS one of our keys whose claim is missing: retry
	--     every 4th tick (~200 ms) until the dial yields it;
	--   * otherwise: a coarse safety net, every 100th tick (~5 s), so a bound
	--     ability, a granted ability or a wrong owned-keys read can never
	--     leave us permanently blind.
	-- The walk itself, its cap and its probe behaviour are unchanged;
	-- all_buttons_found() now ends every walk the moment the ACTIVE dial is
	-- complete - which an EMPTY active set is, vacuously - so no walk runs at
	-- all when nothing of ours can be on the dial.
	if not all_buttons_found() then
		local walk_now = false
		if walk_on_selection_change or walk_on_new_unit then
			walk_now = true
			walk_on_selection_change = false
			walk_on_new_unit = false
			brisk_walk_until = ui_ticks + 48   -- a FRESH brisk window per event (48 ui ticks)
		elseif not selection_walk_info_known() then
			-- ROUND 7 BOUND: once any event has opened a window, the old
			-- every-2nd-tick cadence runs only inside it; outside -> the 5 s net.
			if brisk_walk_until < 0 or ui_ticks <= brisk_walk_until then
				walk_now = (ui_ticks % 2) == 0
			else
				walk_now = (ui_ticks % 100) == 0
			end
		elseif selected_unit_owns_unclaimed_key() then
			-- ROUND 7 BOUND: the "missing owned ability claim" retry is a
			-- retry, not a permanent state - it stops with the window.
			if brisk_walk_until < 0 or ui_ticks <= brisk_walk_until then
				walk_now = (ui_ticks % 4) == 0
			else
				walk_now = (ui_ticks % 100) == 0
			end
		else
			walk_now = (ui_ticks % 100) == 0
		end
		if walk_now then
			find_ability_buttons()
		end
	end

end

bm:repeat_real_callback(ui_tick, 50, "zz_deadly_onslaught_ui")

-- ---------------------------------------------------------------------------
-- THE BUTTON ITSELF
-- A click handler is a UI context, and painting works from here (rounds 9-14:
-- both the state and the icon followed the clicks).
-- ---------------------------------------------------------------------------

log("loaded. polling every " .. tostring(POLL_MS) .. " ms"
	.. " | fire on charge = " .. tostring(FIRE_ON_CHARGE)
	.. " | fire on melee = " .. tostring(FIRE_ON_MELEE)
	.. " | automatic activation is PER UNIT: " .. armed_states_string()
	.. " | click a unit's card to select it, then the ability's M/A badge to flip it")
log("control: take=" .. (TAKE_CONTROL_FIRST and "explicit before every attempt" or "disabled")
	.. ", release=" .. (RELEASE_CONTROL_AFTER and "runs only after a successful take" or "off"))
log("claim-test bisect level " .. tostring(CLAIM_BISECT) .. "/9 - " .. bisect_summary()
	.. " (steps 1-6 + 9 run - the equality match; steps 7-8 log their removal; a step with 'entering' but no 'ok' names a crash)")
log("claim-test bisect steps: 1 type(v) | 2 tostring(v) | 3 concat copy | 4 string.len | 5 # | 6 string.lower | 7 find plain (removed) | 8 find pattern (removed) | 9 equality compare")
for _, ability in ipairs(ABILITIES) do
	for _, wanted_key in ipairs(ability.keys) do
		log("  accepting ability (" .. ability.marker .. "): " .. wanted_key)
	end
end

-- The tooltip override is a localisation file (text/db/zz_deadly_onslaught__.loc) that
-- re-writes the vanilla description of this ability with the right-click instruction
-- appended. This line proves whether it actually loaded: vanilla flavour text with no
-- "Right-click" line means the override lost, and only the tooltip is affected.
local TOOLTIP_KEY = "unit_abilities_tooltip_text_wh_main_character_abilities_deadly_onslaught"
local loc_ok, loc_text = pcall(function() return common.get_localised_string(TOOLTIP_KEY) end)
log("tooltip text in use (" .. (loc_ok and "ok" or "FAILED") .. "): " .. tostring(loc_text))
