-- ============================================================================
-- WH3 AUTO-ABILITY MOD - ANNOTATED READING COPY  (every reporting line removed)
-- ============================================================================
--
-- WHAT THIS FILE IS
--   A readable copy of the working battle-mod script for Total War:
--   WARHAMMER III (the installed file is
--   script/battle/mod/zz_test_deadly_onslaught.lua). Every "write this down
--   in the battle log" statement has been stripped out; every decision, every
--   engine call, every timer and every stored value is the same as the
--   installed mod. The installed mod is this same logic with its reporting
--   lines left in.
--
-- WHAT THE MOD DOES, IN PLAIN WORDS
--   The game gives some units "special abilities" - extra moves a player
--   normally fires by clicking an icon on the unit's ability wheel. This mod
--   can fire its approved abilities automatically, with no click - the five
--   below, plus a batch of 28 approved entries (29 keys: item, weapon and
--   lord abilities) whose approved rule is exactly Blood Lust's - but ONLY
--   for the units and abilities the player has switched on:
--
--     1. Deadly Onslaught  - during a CHARGE (the unit is closing on a
--                            targeted enemy and impact is only seconds away)
--                            OR once the unit is already fighting in melee;
--     2. Foe-Seeker        - while the unit is TIRED OR WORSE (fatigue:
--                            tired, very tired or exhausted - a merely
--                            winded unit is held back);
--     3. Hammer of Sigmar  - while the unit is IN MELEE;
--     4. Stand Your Ground - while the unit is IN MELEE and its morale has
--                            dropped into the "wavering" band. This ability
--                            ships in two engine variants: the base form is
--                            centred on the unit itself, while the DLC24
--                            Tactician's form is a GROUND-TARGETED cast aimed
--                            at the ground under the unit.
--     5. Blood Lust        - while the unit is IN MELEE and its morale is
--                            neither routing nor wavering (unbroken). It
--                            ships in two engine variants, one per race that
--                            owns it, and always casts on the unit itself.
--     6. The approved batch - 28 further entries (29 keys: item, weapon and
--                            lord abilities such as Aether Sword, Axes of
--                            Kadrin or Deathbringer incl. its upgraded
--                            form). The approved rule is exactly Blood
--                            Lust's: in melee and not fleeing (alive,
--                            neither routing nor wavering, fail-open
--                            morale), cast on self. Each carries its own
--                            M/A badge; each is listed in full in the
--                            abilities table below (every entry whose
--                            trigger reads "melee_unwavering").
--
--   HOW AUTO-FIRING IS SWITCHED ON
--   The switch is PER UNIT and PER ABILITY. For each ability the mod draws a
--   small letter beside that ability's own slot on the wheel: "M" = manual
--   (the player fires it), "A" = automatic (the mod may fire it). Clicking
--   the letter flips that one switch for the unit. When several units are
--   selected, one click toggles the ability for every selected unit that owns
--   it - the same multi-select behaviour as the vanilla ability wheel. A unit
--   that was never switched on never fires anything, and two units carrying
--   the same ability are switched on and off completely independently.
--
--   HOW THE MOD SEES THE PLAYER'S SELECTION
--   The engine hands the mod its own select / deselect events (a per-unit
--   "selection callback"); while that is available it is the source of truth,
--   because the on-screen unit cards cannot see a group / box selection. A
--   sweep of the card states remains as the fallback for the times the
--   callback is missing or has never fired.
--
--   HOW OFTEN IT DOES ITS EXPENSIVE WORK  (it deliberately avoids per-tick
--   work, and re-scans the on-screen ability buttons only when there is a
--   reason to):
--     * a selection CHANGE (the wheel belongs to whoever is selected) or a
--       NEW unit on the watch list asks for exactly one scan;
--     * a selected unit that OWNS an ability we have not located on the wheel
--       yet asks for a scan about every 200 ms until the wheel yields it;
--     * otherwise a coarse safety net runs about every 5 seconds, so a bound
--       that was somehow missed still converges;
--     * and while nothing at all is known yet, a full fallback walk runs.
--     * Separately, the mod re-lists the player's army every 10 seconds, so
--       units that appear mid-battle (summons, splits, transformations) are
--       picked up and can be armed while the battle runs.
--     * For a unit that carries none of our abilities it watches the unit's
--       engine identity (its unit-type key) and re-scans only when that
--       identity CHANGES - which is how a transformation or a mount that
--       gains abilities mid-battle is caught - with a slow full rescan every
--       60 seconds as a safety net.
--
--   WHAT HAPPENS WHEN THE ENGINE REFUSES A FIRE
--     * A refusal is normally a cooldown hold. The mod has no way to READ
--       that a unit-and-ability pair is cooling down, so it learns from the
--       refusal itself: one refusal simply leaves the short 2-second brake in
--       place, but a SECOND one backs that pair off for 8 seconds, so a long
--       cooldown costs a handful of probes instead of an attempt every 2
--       seconds. Nothing is ever held for more than 20 seconds - the hard
--       bound forces a probe. Only an ACCEPTED fire clears the hold.
--     * A refusal that NAMES A UNIT WHICH NO LONGER EXISTS is treated as a
--       removal notice: the unit is dropped from the watch list at once and
--       kept dropped, so it is not re-adopted by the next 10-second re-list.
--       The ordinary cooldown message is a different string and is NEVER read
--       as a death.
--
-- HOW TO READ THIS FILE
--   - Lines starting with "--" are plain-English comments (human notes the
--     game ignores). Everything else is the actual script.
--   - A few words that will come back often, in plain terms:
--       * callback - a small function handed to the game to be called back
--                    later: on a timer, or when something happens.
--       * table    - Lua's container of labelled values (like a labelled
--                    parts tray). examples below: ABILITIES, armed.
--       * pcall    - "try this; if it fails, come back with an error value
--                    instead of crashing". Used around every engine call
--                    that has ever misbehaved.
--   - Section numbers and names are this copy's own; the installed build's
--     numbers referred to reporting sections that are not carried here.
-- ============================================================================


-- ============================================================================
-- SECTION 1 - SETTINGS
--   The reference board: the ability list, the on/off switches and the
--   tunable numbers the rest of the file reads. Nothing here does anything
--   by itself.
-- ============================================================================

-- THE ABILITIES - one entry per ability, and this table drives everything:
-- the dial scan (which buttons are ours), the firing loop (which trigger
-- fires it, which keys to try) and the badges (letter, id, backup offset).
--
--   marker  - short internal name; how the code looks this entry up.
--   name    - the display name, as the player sees it.
--   trigger - the situation that fires the ability:
--               "charge"  - the mod's charge test (SECTION 4), OR the
--                           plain in-melee condition (this round, user-
--                           approved: Deadly Onslaught has a component
--                           useful in melee, so it fires on the charge
--                           window or once already fighting - the same
--                           engine call the melee triggers below use)
--               "tired"   - the unit's FATIGUE state is Tired or worse:
--                           tired, very_tired or exhausted (a merely
--                           winded unit holds). Read through
--                           battle_unit:fatigue_state(); the WHOLE value
--                           is compared exactly - no find, no substring.
--                           An unreadable fatigue fails CLOSED (no fire)
--                           and is reported once.
--               "melee"   - the engine says the unit is in hand-to-hand
--               "melee_low_morale" - the engine says the unit is in
--                           hand-to-hand AND its morale is at or below the
--                           wavering threshold (battle_unit:is_wavering -
--                           the only morale threshold the API exposes;
--                           there is no percentage read). Fail-open: a
--                           morale read that cannot be taken falls back to
--                           the plain "melee" behaviour.
--               "melee_unwavering" - the engine says the unit is in
--                           hand-to-hand, the unit is not routing, and
--                           its morale is not wavering (fail-open: a
--                           morale read that cannot be taken rides the
--                           plain in-melee condition). This is
--                           blood_lust's rule; the 28 approved
--                           in-melee-self entries (this round) share it
--                           under the same trigger name.
--   evaluate - the per-entry dispatch (critique-2 item 8): the poll
--             calls ability.evaluate(unit, routing) directly; the field
--             is wired at load from the trigger name (SECTION 6d), so
--             no string comparison on the trigger runs any more.
--   keys    - the database names ("keys") the engine may use for this
--             ability. A dial button belongs to this ability only when its
--             key EQUALS one of these, letter for letter (all lowercase) -
--             exact equality, never a partial match. The unit scan uses
--             this list as its search set: which of these names a unit
--             actually carries. At fire time the readiness check
--             (SECTION 3) asks about the ONE name the scan found on the
--             unit; this list is walked only as the fallback when no
--             usable name is remembered for the unit yet. Two names are
--             listed for Foe-Seeker and for Hammer of Sigmar because the
--             game ships two variant definitions of each.
--   badge   - the on-screen component id of this ability's M/A letter.
--   ox, oy  - the backup badge offset (right +x, down +y), used only when
--             the mod cannot work out which wheel slot the ability occupies.
local ABILITIES = {
	{ marker = "onslaught", name = "Deadly Onslaught", trigger = "charge",
		badge = "zz_auto_badge",
		keys = { "wh_main_character_abilities_deadly_onslaught" },
		ox = 0, oy = 0 },                     -- backup offset: none added (top slot)
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
		ox = 70, oy = 30 },                   -- backup offset: +70 right, +30 down
	{ marker = "hammer_of_sigmar", name = "Hammer of Sigmar", trigger = "melee",
		badge = "zz_auto_badge_hos",
		keys = { "wh_main_spell_bound_hammer_of_sigmar",
			"wh_dlc04_spell_bound_hammer_of_sigmar_upgraded" },
		ox = 98, oy = 102 },                  -- backup offset: +98 right, +102 down
	{ marker = "stand_your_ground", name = "Stand Your Ground", trigger = "melee_low_morale",
		badge = "zz_auto_badge_syg",
		keys = { "wh_main_character_abilities_stand_your_ground",
			"wh3_dlc24_character_abilities_tacticians_stand_your_ground" },
		ox = 66, oy = 172 },                  -- backup offset: +66 right, +172 down (wheel slot 4)
	{ marker = "blood_lust", name = "Blood Lust", trigger = "melee_unwavering",
		badge = "zz_auto_badge_bl",
		keys = { "wh_main_character_abilities_blood_lust",
			"wh_dlc03_character_abilities_blood_lust" },
		ox = -68, oy = 32 },                  -- backup offset: -68 right, +32 down (wheel slot 5)
	-- THE APPROVED IN-MELEE-SELF BATCH (this round): 28 approved
	-- entries - 29 database keys; the two Deathbringer keys sit in ONE
	-- entry. Their approved rule is exactly blood_lust's - "when in
	-- melee (and not fleeing): cast on self" = alive, in melee, neither
	-- routing nor wavering (fail-open morale), self-cast - so they
	-- share its trigger name and its evaluator (SECTION 6d). Each
	-- carries its own marker, name, badge and key list; the badges are
	-- positioned by the claimed button's wheel slot (SECTION 8), with
	-- the top slot as the backup offset (ox 0, oy 0).
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
	-- dispatches to the ONE shared FOURTH.evaluate_in_melee_self (SECTION
	-- 6d), exactly like blood_lust and the block-1 batch. Each carries
	-- its own marker, display name, badge id and key list; the badges
	-- are positioned by the claimed button's wheel slot (SECTION 8), with
	-- the top slot as the fallback offset (ox 0, oy 0).
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
	-- OWN evaluator (SECTION 6d) with its OWN distinct reason text, so the
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
	{ marker = "lightning_reflexes", name = "Lightning Reflexes", trigger = "melee_unwavering",
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
	{ marker = "master_of_the_skies", name = "Master of the Skies", trigger = "melee_unwavering",
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
	{ marker = "pendant_of_slaanesh", name = "Pendant of Slaanesh", trigger = "melee_unwavering",
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
	{ marker = "slippery", name = "Slippery", trigger = "melee_unwavering",
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
	{ marker = "transfix", name = "Transfix", trigger = "melee_unwavering",
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
	{ marker = "enchanted_metallurgy", name = "Enchanted Metallurgy", trigger = "metallurgy_melee",
		badge = "zz_auto_badge_enchanted_metallurgy",
		keys = { "wh3_main_character_abilities_enchanted_metallurgy" },
		ox = 0, oy = 0 },
	{ marker = "enchanted_metallurgy_flaming", name = "Enchanted Metallurgy: Flaming", trigger = "metallurgy_melee",
		badge = "zz_auto_badge_enchanted_metallurgy_flaming",
		keys = { "wh3_main_character_abilities_enchanted_metallurgy_flaming" },
		ox = 0, oy = 0 },
	{ marker = "enchanted_metallurgy_piercing", name = "Enchanted Metallurgy: Piercing", trigger = "metallurgy_melee",
		badge = "zz_auto_badge_enchanted_metallurgy_piercing",
		keys = { "wh3_main_character_abilities_enchanted_metallurgy_piercing" },
		ox = 0, oy = 0 },
	{ marker = "enchanted_metallurgy_poison", name = "Enchanted Metallurgy: Poison", trigger = "metallurgy_melee",
		badge = "zz_auto_badge_enchanted_metallurgy_poison",
		keys = { "wh3_main_character_abilities_enchanted_metallurgy_poison" },
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
	{ marker = "butcher", name = "Meat Feast", trigger = "ushoran_health",
		badge = "zz_auto_badge_butcher",
		keys = { "wh3_main_prisoners_butcher" },
		ox = 0, oy = 0 },
	{ marker = "captain_of_the_phoenix_guard", name = "Captain of the Phoenix Guard", trigger = "melee_health75",
		badge = "zz_auto_badge_captain_of_the_phoenix_guard",
		keys = { "wh3_dlc27_character_abilities_captain_of_the_phoenix_guard" },
		ox = 0, oy = 0 },
	{ marker = "cash_cascade", name = "Cash Cascade", trigger = "charge_or_melee",
		badge = "zz_auto_badge_cash_cascade",
		keys = { "wh3_dlc26_character_abilities_cash_cascade" },
		ox = 0, oy = 0 },
	{ marker = "chanson_of_caging", name = "Chanson of Caging", trigger = "melee_unwavering",
		badge = "zz_auto_badge_chanson_of_caging",
		keys = { "wh3_dlc27_lord_abilities_chanson_of_caging" },
		ox = 0, oy = 0 },
	{ marker = "commanding_presence", name = "Commanding Presence", trigger = "wavering_self_or_ally",
		badge = "zz_auto_badge_commanding_presence",
		keys = { "wh3_dlc29_lord_active_commanding_presence" },
		ox = 0, oy = 0 },
	{ marker = "curse_of_years", name = "Curse of Years", trigger = "melee_unwavering",
		badge = "zz_auto_badge_curse_of_years",
		keys = { "wh3_dlc29_spell_bound_curse_of_years" },
		ox = 0, oy = 0 },
	{ marker = "da_boss_as_a_plan", name = "Da Boss 'as a Plan!", trigger = "melee_unwavering",
		badge = "zz_auto_badge_da_boss_as_a_plan",
		keys = { "wh3_dlc26_character_abilities_da_boss_as_a_plan" },
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
	{ marker = "favour_of_the_fay", name = "Favour of the Fay", trigger = "melee_unwavering",
		badge = "zz_auto_badge_favour_of_the_fay",
		keys = { "wh_dlc07_lord_abilities_favour_of_the_fay" },
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
	{ marker = "fury_of_khaine", name = "Fury of Khaine", trigger = "charge_or_melee",
		badge = "zz_auto_badge_fury_of_khaine",
		keys = { "wh2_main_unit_abilities_fury_of_khaine" },
		ox = 0, oy = 0 },
	{ marker = "fury_of_ulric", name = "Fury of Ulric", trigger = "wavering_self_or_ally",
		badge = "zz_auto_badge_fury_of_ulric",
		keys = { "wh3_dlc29_spell_bound_prayer_fury_of_ulric" },
		ox = 0, oy = 0 },
	{ marker = "gaze_of_khaine", name = "Gaze of Khaine", trigger = "melee_unwavering",
		badge = "zz_auto_badge_gaze_of_khaine",
		keys = { "wh2_dlc10_lord_abilities_gaze_of_khaine" },
		ox = 0, oy = 0 },
	{ marker = "grand_faiths_bastion", name = "Greater Faith Bastion", trigger = "melee_unwavering",
		badge = "zz_auto_badge_grand_faiths_bastion",
		keys = { "wh_dlc06_quest_abilities_grand_faiths_bastion" },
		ox = 0, oy = 0 },
	{ marker = "gulyas", name = "Gulyas", trigger = "ushoran_health",
		badge = "zz_auto_badge_gulyas",
		keys = { "wh3_dlc24_lord_abilities_gulyas" },
		ox = 0, oy = 0 },
	{ marker = "helm_of_yvresse", name = "Helm of Yvresse", trigger = "wavering_self",
		badge = "zz_auto_badge_helm_of_yvresse",
		keys = { "wh2_dlc15_item_abilities_helm_of_yvresse" },
		ox = 0, oy = 0 },
	{ marker = "helping_hand", name = "Helping Hand", trigger = "melee_unwavering",
		badge = "zz_auto_badge_helping_hand",
		keys = { "wh2_pro08_character_abilities_helping_hand" },
		ox = 0, oy = 0 },
	{ marker = "immovable_bulwark", name = "Immovable Bulwark", trigger = "melee_unwavering",
		badge = "zz_auto_badge_immovable_bulwark",
		keys = { "wh3_dlc26_unit_abilities_immovable_bulwark" },
		ox = 0, oy = 0 },
	{ marker = "inspired_assault_i", name = "Inspired Assault I", trigger = "charge_or_melee",
		badge = "zz_auto_badge_inspired_assault_i",
		keys = { "wh3_main_lord_abilities_inspired_assault_i" },
		ox = 0, oy = 0 },
	{ marker = "inspired_assault_ii", name = "Inspired Assault II", trigger = "charge_or_melee",
		badge = "zz_auto_badge_inspired_assault_ii",
		keys = { "wh3_main_lord_abilities_inspired_assault_ii" },
		ox = 0, oy = 0 },
	{ marker = "inspired_assault_iii", name = "Inspired Assault III", trigger = "charge_or_melee",
		badge = "zz_auto_badge_inspired_assault_iii",
		keys = { "wh3_main_lord_abilities_inspired_assault_iii" },
		ox = 0, oy = 0 },
	{ marker = "inspired_defence_i", name = "Inspired Defence I", trigger = "melee_unwavering",
		badge = "zz_auto_badge_inspired_defence_i",
		keys = { "wh3_main_lord_abilities_inspired_defence_i" },
		ox = 0, oy = 0 },
	{ marker = "inspired_defence_ii", name = "Inspired Defence II", trigger = "melee_unwavering",
		badge = "zz_auto_badge_inspired_defence_ii",
		keys = { "wh3_main_lord_abilities_inspired_defence_ii" },
		ox = 0, oy = 0 },
	{ marker = "inspired_defence_iii", name = "Inspired Defence III", trigger = "melee_unwavering",
		badge = "zz_auto_badge_inspired_defence_iii",
		keys = { "wh3_main_lord_abilities_inspired_defence_iii" },
		ox = 0, oy = 0 },
	{ marker = "lord_of_grand_cathay", name = "Lord of Grand Cathay", trigger = "melee_unwavering",
		badge = "zz_auto_badge_lord_of_grand_cathay",
		keys = { "wh3_dlc24_lord_abilities_lord_of_grand_cathay" },
		ox = 0, oy = 0 },
	{ marker = "massacre", name = "Massacre", trigger = "melee_unwavering",
		badge = "zz_auto_badge_massacre",
		keys = { "wh3_main_prisoners_massacre" },
		ox = 0, oy = 0 },
	{ marker = "master_of_alchemy", name = "Master of Alchemy", trigger = "metallurgy_melee",
		badge = "zz_auto_badge_master_of_alchemy",
		keys = { "wh3_main_lord_abilities_master_of_alchemy" },
		ox = 0, oy = 0 },
	{ marker = "master_of_alchemy_flaming", name = "Master of Alchemy: Flaming", trigger = "metallurgy_melee",
		badge = "zz_auto_badge_master_of_alchemy_flaming",
		keys = { "wh3_main_lord_abilities_master_of_alchemy_flaming" },
		ox = 0, oy = 0 },
	{ marker = "master_of_alchemy_piercing", name = "Master of Alchemy: Piercing", trigger = "metallurgy_melee",
		badge = "zz_auto_badge_master_of_alchemy_piercing",
		keys = { "wh3_main_lord_abilities_master_of_alchemy_piercing" },
		ox = 0, oy = 0 },
	{ marker = "master_of_alchemy_poison", name = "Master of Alchemy: Poison", trigger = "metallurgy_melee",
		badge = "zz_auto_badge_master_of_alchemy_poison",
		keys = { "wh3_main_lord_abilities_master_of_alchemy_poison" },
		ox = 0, oy = 0 },
	{ marker = "master_rune_of_oath_and_steel", name = "Master Rune of Oath & Steel", trigger = "melee_unwavering",
		badge = "zz_auto_badge_master_rune_of_oath_and_steel",
		keys = { "wh_dlc06_rune_abilities_master_rune_of_oath_and_steel" },
		ox = 0, oy = 0 },
	{ marker = "master_rune_of_speed", name = "Master Rune of Speed", trigger = "melee_unwavering",
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
	{ marker = "orcs_are_da_best", name = "Orcs are da Best!", trigger = "melee_unwavering",
		badge = "zz_auto_badge_orcs_are_da_best",
		keys = { "wh3_dlc26_character_abilities_orcs_are_da_best" },
		ox = 0, oy = 0 },
	{ marker = "overseer_of_the_unseen", name = "Overseer of the Unseen", trigger = "melee_unwavering",
		badge = "zz_auto_badge_overseer_of_the_unseen",
		keys = { "wh3_dlc29_hero_active_overseer_of_the_unseen" },
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
	{ marker = "rune_of_speed", name = "Rune of Speed", trigger = "melee_unwavering",
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
	{ marker = "star_of_avelorn", name = "Star of Avelorn", trigger = "ushoran_health",
		badge = "zz_auto_badge_star_of_avelorn",
		keys = { "wh2_dlc10_item_abilities_star_of_avelorn" },
		ox = 0, oy = 0 },
	{ marker = "stay_here_ill_get_help", name = "\"Stay Here, I'll Get Help!\"", trigger = "wavering_ally_range",
		badge = "zz_auto_badge_stay_here_ill_get_help",
		keys = { "wh2_dlc09_character_abilities_stay_here_ill_get_help" },
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
	{ marker = "the_shadows_coil", name = "The Shadow's Coil", trigger = "melee_unwavering",
		badge = "zz_auto_badge_the_shadows_coil",
		keys = { "wh_dlc05_unit_abilities_the_shadows_coil" },
		ox = 0, oy = 0 },
	{ marker = "unstoppable_choppas", name = "Unstoppable Choppas", trigger = "melee_unwavering",
		badge = "zz_auto_badge_unstoppable_choppas",
		keys = { "wh3_dlc26_unit_abilities_unstoppable_choppas" },
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
		ox = 0, oy = 0 },
	{ marker = "acquiescence", name = "Acquiescence", trigger = "melee_unwavering",
		badge = "zz_auto_badge_acquiescence",
		keys = { "wh3_dlc27_spell_bound_acquiescence" },
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
	{ marker = "amulet_of_phastah", name = "Amulet of Pha-Stah", trigger = "melee_unwavering",
		badge = "zz_auto_badge_amulet_of_phastah",
		keys = { "wh2_dlc09_item_abilities_amulet_of_phastah" },
		ox = 0, oy = 0 },
	{ marker = "apocalyptic_charge", name = "Apocalyptic Charge", trigger = "melee_unwavering",
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
	{ marker = "assassins_trophy", name = "Assassin's Trophy", trigger = "melee_unwavering",
		badge = "zz_auto_badge_assassins_trophy",
		keys = { "wh2_main_character_abilities_assassins_trophy" },
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
	{ marker = "bastet", name = "Bastet", trigger = "melee_unwavering",
		badge = "zz_auto_badge_bastet",
		keys = { "wh3_dlc29_lord_abilities_bastet" },
		ox = 0, oy = 0 },
	{ marker = "bitter_sting", name = "Bitter Sting", trigger = "melee_unwavering",
		badge = "zz_auto_badge_bitter_sting",
		keys = { "wh3_dlc27_qb_unit_abilities_bitter_sting" },
		ox = 0, oy = 0 },
	{ marker = "black_periapt", name = "Black Periapt", trigger = "melee_unwavering",
		badge = "zz_auto_badge_black_periapt",
		keys = { "wh_main_item_abilities_black_periapt" },
		ox = 0, oy = 0 },
	{ marker = "black_staff", name = "Black Staff", trigger = "melee_unwavering",
		badge = "zz_auto_badge_black_staff",
		keys = { "wh2_main_spell_bound_black_staff" },
		ox = 0, oy = 0 },
	{ marker = "blade_of_setep", name = "Blade of Setep", trigger = "melee_unwavering",
		badge = "zz_auto_badge_blade_of_setep",
		keys = { "wh2_dlc09_weapon_abilities_blade_of_setep" },
		ox = 0, oy = 0 },
	{ marker = "blessed_helm_of_the_oblast", name = "Blessed Helm of the Oblast", trigger = "melee_unwavering",
		badge = "zz_auto_badge_blessed_helm_of_the_oblast",
		keys = { "wh3_dlc24_item_abilities_blessed_helm_of_the_oblast" },
		ox = 0, oy = 0 },
	{ marker = "blight_of_terrors", name = "Blight of Terrors", trigger = "melee_unwavering",
		badge = "zz_auto_badge_blight_of_terrors",
		keys = { "wh2_dlc16_character_abilities_blight_of_terrors" },
		ox = 0, oy = 0 },
	{ marker = "blight_swarm", name = "Blight Swarm", trigger = "melee_unwavering",
		badge = "zz_auto_badge_blight_swarm",
		keys = { "wh3_main_lord_abilities_blight_swarm" },
		ox = 0, oy = 0 },
	{ marker = "blood_omens", name = "Blood Omens", trigger = "melee_unwavering",
		badge = "zz_auto_badge_blood_omens",
		keys = { "wh3_dlc29_unit_abilities_blood_omens" },
		ox = 0, oy = 0 },
	{ marker = "bloody_onslaught", name = "Bloody Onslaught", trigger = "melee_unwavering",
		badge = "zz_auto_badge_bloody_onslaught",
		keys = { "wh3_dlc26_character_abilities_bloody_onslaught" },
		ox = 0, oy = 0 },
	{ marker = "blooood", name = "Blooood!", trigger = "melee_unwavering",
		badge = "zz_auto_badge_blooood",
		keys = { "wh_main_unit_abilities_blooood" },
		ox = 0, oy = 0 },
	{ marker = "book_of_arkhan", name = "Book of Arkhan", trigger = "melee_unwavering",
		badge = "zz_auto_badge_book_of_arkhan",
		keys = { "wh_main_spell_bound_book_of_arkhan" },
		ox = 0, oy = 0 },
	{ marker = "book_of_hoeth", name = "Book of Hoeth", trigger = "melee_unwavering",
		badge = "zz_auto_badge_book_of_hoeth",
		keys = { "wh2_main_item_abilities_book_of_hoeth" },
		ox = 0, oy = 0 },
	{ marker = "book_of_secrets", name = "Book of Secrets", trigger = "melee_unwavering",
		badge = "zz_auto_badge_book_of_secrets",
		keys = { "wh3_dlc24_item_abilities_book_of_secrets" },
		ox = 0, oy = 0 },
	{ marker = "boom", name = "Boom!", trigger = "melee_unwavering",
		badge = "zz_auto_badge_boom",
		keys = { "wh_main_unit_abilities_boom" },
		ox = 0, oy = 0 },
	{ marker = "call_of_violence", name = "Call of Violence", trigger = "melee_unwavering",
		badge = "zz_auto_badge_call_of_violence",
		keys = { "wh_dlc03_character_abilities_call_of_violence" },
		ox = 0, oy = 0 },
	{ marker = "cascading_fire_cloak", name = "Cascading Fire Cloak", trigger = "melee_unwavering",
		badge = "zz_auto_badge_cascading_fire_cloak",
		keys = { "wh3_main_spell_bound_cascading_fire_cloak" },
		ox = 0, oy = 0 },
	{ marker = "chalice_of_dark_rain", name = "Chalice of Dark Rain", trigger = "melee_unwavering",
		badge = "zz_auto_badge_chalice_of_dark_rain",
		keys = { "wh_dlc03_item_abilities_chalice_of_dark_rain" },
		ox = 0, oy = 0 },
	{ marker = "channelling_staff", name = "Channelling Staff", trigger = "melee_unwavering",
		badge = "zz_auto_badge_channelling_staff",
		keys = { "wh_main_item_abilities_channelling_staff" },
		ox = 0, oy = 0 },
	{ marker = "charmed_shield", name = "Charmed Shield", trigger = "melee_unwavering",
		badge = "zz_auto_badge_charmed_shield",
		keys = { "wh_main_weapon_abilities_charmed_shield" },
		ox = 0, oy = 0 },
	{ marker = "cold_blooded", name = "Cold-Blooded", trigger = "melee_unwavering",
		badge = "zz_auto_badge_cold_blooded",
		keys = { "wh2_main_character_abilities_cold_blooded" },
		ox = 0, oy = 0 },
	{ marker = "crown_of_command", name = "Crown of Command", trigger = "melee_unwavering",
		badge = "zz_auto_badge_crown_of_command",
		keys = { "wh_main_item_abilities_crown_of_command" },
		ox = 0, oy = 0 },
	{ marker = "cube_of_darkness", name = "Cube of Darkness", trigger = "melee_unwavering",
		badge = "zz_auto_badge_cube_of_darkness",
		keys = { "wh2_main_item_abilities_cube_of_darkness" },
		ox = 0, oy = 0 },
	{ marker = "curse_of_khsar", name = "Curse of Khsar", trigger = "melee_unwavering",
		badge = "zz_auto_badge_curse_of_khsar",
		keys = { "wh2_dlc09_character_abilities_curse_of_khsar" },
		ox = 0, oy = 0 },
	{ marker = "slezuzus_voice", name = "Daemonic Whispers", trigger = "melee_unwavering",
		badge = "zz_auto_badge_slezuzus_voice",
		keys = { "wh3_dlc27_character_abilities_slezuzus_voice" },
		ox = 0, oy = 0 },
	{ marker = "dark_fortune", name = "Dark Fortune", trigger = "melee_unwavering",
		badge = "zz_auto_badge_dark_fortune",
		keys = { "wh_main_item_abilities_dark_fortune" },
		ox = 0, oy = 0 },
	{ marker = "deranged_munitions", name = "Deranged Munitions", trigger = "melee_unwavering",
		badge = "zz_auto_badge_deranged_munitions",
		keys = { "wh3_dlc25_lord_abilities_deranged_munitions" },
		ox = 0, oy = 0 },
	{ marker = "deranged_munitions_upgraded", name = "Deranged Munitions Upgraded", trigger = "melee_unwavering",
		badge = "zz_auto_badge_deranged_munitions_upgraded",
		keys = { "wh3_dlc25_lord_abilities_deranged_munitions_upgraded" },
		ox = 0, oy = 0 },
	{ marker = "dont_even_try_it", name = "Don't Even Try It", trigger = "melee_unwavering",
		badge = "zz_auto_badge_dont_even_try_it",
		keys = { "wh2_dlc15_lord_abilities_dont_even_try_it" },
		ox = 0, oy = 0 },
	{ marker = "doom_and_darkness_gunnery_school", name = "Doom & Darkness", trigger = "melee_unwavering",
		badge = "zz_auto_badge_doom_and_darkness_gunnery_school",
		keys = { "wh3_dlc25_spell_Bound_doom_and_darkness_gunnery_school",
			"wh3_dlc27_spell_bound_runecaller_death_doom_and_darkness",
			"wh_dlc08_spell_bound_death_doom_and_darkness" },
		ox = 0, oy = 0 },
	{ marker = "doom_lord", name = "Doom Lord", trigger = "melee_unwavering",
		badge = "zz_auto_badge_doom_lord",
		keys = { "wh3_dlc29_lord_abilities_doom_lord" },
		ox = 0, oy = 0 },
	{ marker = "earthing_rod", name = "Earthing Rod", trigger = "melee_unwavering",
		badge = "zz_auto_badge_earthing_rod",
		keys = { "wh_main_item_abilities_earthing_rod" },
		ox = 0, oy = 0 },
	{ marker = "el_syf", name = "El Syf", trigger = "melee_unwavering",
		badge = "zz_auto_badge_el_syf",
		keys = { "wh_dlc05_weapon_abilities_el_syf" },
		ox = 0, oy = 0 },
	{ marker = "elixir_of_might", name = "Elixir of Might", trigger = "melee_unwavering",
		badge = "zz_auto_badge_elixir_of_might",
		keys = { "wh2_dlc09_item_abilities_elixir_of_might" },
		ox = 0, oy = 0 },
	{ marker = "embers_of_the_phoenix", name = "Embers of the Phoenix", trigger = "melee_unwavering",
		badge = "zz_auto_badge_embers_of_the_phoenix",
		keys = { "wh2_main_spell_bound_embers_of_the_phoenix" },
		ox = 0, oy = 0 },
	{ marker = "ballistic_enchantment", name = "Enchanted Ballistics", trigger = "melee_unwavering",
		badge = "zz_auto_badge_ballistic_enchantment",
		keys = { "wh2_dlc11_character_abilities_ballistic_enchantment" },
		ox = 0, oy = 0 },
	{ marker = "enhanced_skavenbrew", name = "Enhanced Skavenbrew", trigger = "melee_unwavering",
		badge = "zz_auto_badge_enhanced_skavenbrew",
		keys = { "wh3_dlc29_item_abilities_enhanced_skavenbrew" },
		ox = 0, oy = 0 },
	{ marker = "entangle", name = "Entangle", trigger = "melee_unwavering",
		badge = "zz_auto_badge_entangle",
		keys = { "wh2_dlc10_character_abilities_entangle" },
		ox = 0, oy = 0 },
	{ marker = "entrenchment", name = "Entrenchment", trigger = "melee_unwavering",
		badge = "zz_auto_badge_entrenchment",
		keys = { "wh_main_unit_abilities_entrenchment" },
		ox = 0, oy = 0 },
	{ marker = "gaze_of_usirian", name = "Eternal Gaze", trigger = "melee_unwavering",
		badge = "zz_auto_badge_gaze_of_usirian",
		keys = { "wh3_dlc29_lord_abilities_gaze_of_usirian" },
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
	{ marker = "fear_of_aramar", name = "Fear of Aramar", trigger = "melee_unwavering",
		badge = "zz_auto_badge_fear_of_aramar",
		keys = { "wh2_dlc10_item_abilities_fear_of_aramar" },
		ox = 0, oy = 0 },
	{ marker = "fearsome_roar", name = "Fearsome Roar", trigger = "melee_unwavering",
		badge = "zz_auto_badge_fearsome_roar",
		keys = { "wh3_dlc24_unit_abilities_fearsome_roar" },
		ox = 0, oy = 0 },
	{ marker = "mark_of_the_monster", name = "Fecund Rebirth", trigger = "melee_unwavering",
		badge = "zz_auto_badge_mark_of_the_monster",
		keys = { "wh3_dlc29_character_active_mark_of_the_monster" },
		ox = 0, oy = 0 },
	{ marker = "fermented_fungi", name = "Fermented Fungi", trigger = "melee_unwavering",
		badge = "zz_auto_badge_fermented_fungi",
		keys = { "wh2_dlc15_lord_abilities_fermented_fungi" },
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
	{ marker = "frenzied_challenge", name = "Frenzied Challenge", trigger = "melee_unwavering",
		badge = "zz_auto_badge_frenzied_challenge",
		keys = { "wh3_dlc27_qb_unit_abilities_frenzied_challenge" },
		ox = 0, oy = 0 },
	{ marker = "frost_shard_glaive", name = "Frost Shard Glaive", trigger = "melee_unwavering",
		badge = "zz_auto_badge_frost_shard_glaive",
		keys = { "wh3_main_weapon_abilities_frost_shard_glaive" },
		ox = 0, oy = 0 },
	{ marker = "funnel_of_flame", name = "Funnel of Flame", trigger = "melee_unwavering",
		badge = "zz_auto_badge_funnel_of_flame",
		keys = { "wh2_dlc13_lord_abilities_funnel_of_flame" },
		ox = 0, oy = 0 },
	{ marker = "gaze_of_fate", name = "Gaze of Fate", trigger = "melee_unwavering",
		badge = "zz_auto_badge_gaze_of_fate",
		keys = { "wh3_main_lord_abilities_gaze_of_fate" },
		ox = 0, oy = 0 },
	{ marker = "get_em", name = "Get 'Em!", trigger = "melee_unwavering",
		badge = "zz_auto_badge_get_em",
		keys = { "wh3_dlc25_character_abilities_get_em" },
		ox = 0, oy = 0 },
	{ marker = "get_back_ere", name = "Get Back 'Ere!", trigger = "melee_unwavering",
		badge = "zz_auto_badge_get_back_ere",
		keys = { "wh_main_character_abilities_get_back_ere" },
		ox = 0, oy = 0 },
	{ marker = "soulnetter", name = "Gilellion's Soulnetter", trigger = "melee_unwavering",
		badge = "zz_auto_badge_soulnetter",
		keys = { "wh3_main_weapon_abilities_soulnetter" },
		ox = 0, oy = 0 },
	{ marker = "glacial_defence", name = "Glacial Defence", trigger = "melee_unwavering",
		badge = "zz_auto_badge_glacial_defence",
		keys = { "wh3_twa08_unit_abilities_glacial_defence" },
		ox = 0, oy = 0 },
	{ marker = "glory_seeker", name = "Glory Seeker", trigger = "melee_unwavering",
		badge = "zz_auto_badge_glory_seeker",
		keys = { "wh3_dlc29_hero_active_glory_seeker" },
		ox = 0, oy = 0 },
	{ marker = "glory_seeker_upgraded", name = "Glory Seeker Upgraded", trigger = "melee_unwavering",
		badge = "zz_auto_badge_glory_seeker_upgraded",
		keys = { "wh3_dlc29_hero_active_glory_seeker_upgraded" },
		ox = 0, oy = 0 },
	{ marker = "gruts_sickle", name = "Grut's Sickle", trigger = "melee_unwavering",
		badge = "zz_auto_badge_gruts_sickle",
		keys = { "wh3_main_item_abilities_gruts_sickle" },
		ox = 0, oy = 0 },
	{ marker = "guttural_roar", name = "Guttural Roar", trigger = "melee_unwavering",
		badge = "zz_auto_badge_guttural_roar",
		keys = { "wh3_dlc27_qb_unit_abilities_guttural_roar" },
		ox = 0, oy = 0 },
	{ marker = "hagtree_fetish", name = "Hagtree Fetish", trigger = "melee_unwavering",
		badge = "zz_auto_badge_hagtree_fetish",
		keys = { "wh_dlc03_item_abilities_hagtree_fetish" },
		ox = 0, oy = 0 },
	{ marker = "hail_of_fire", name = "Hail of Fire", trigger = "melee_unwavering",
		badge = "zz_auto_badge_hail_of_fire",
		keys = { "wh2_dlc13_lord_abilities_hail_of_fire" },
		ox = 0, oy = 0 },
	{ marker = "harmonic_convergence", name = "Harmonic Convergence", trigger = "melee_unwavering",
		badge = "zz_auto_badge_harmonic_convergence",
		keys = { "wh3_main_spell_bound_harmonic_convergence" },
		ox = 0, oy = 0 },
	{ marker = "headhunt", name = "Headhunt", trigger = "melee_unwavering",
		badge = "zz_auto_badge_headhunt",
		keys = { "wh3_dlc26_character_abilities_headhunt" },
		ox = 0, oy = 0 },
	{ marker = "hellish_vigour", name = "Hellish Vigour", trigger = "melee_unwavering",
		badge = "zz_auto_badge_hellish_vigour",
		keys = { "wh3_dlc29_lord_abilities_hellish_vigour" },
		ox = 0, oy = 0 },
	{ marker = "hellish_vigour_upgraded", name = "Hellish Vigour Upgraded", trigger = "melee_unwavering",
		badge = "zz_auto_badge_hellish_vigour_upgraded",
		keys = { "wh3_dlc29_lord_abilities_hellish_vigour_upgraded" },
		ox = 0, oy = 0 },
	{ marker = "hidden_huntress", name = "Hidden Huntress", trigger = "melee_unwavering",
		badge = "zz_auto_badge_hidden_huntress",
		keys = { "wh3_cp1_lord_abilities_hidden_huntress" },
		ox = 0, oy = 0 },
	{ marker = "hidden_huntress_upgraded", name = "Hidden Huntress Upgraded", trigger = "melee_unwavering",
		badge = "zz_auto_badge_hidden_huntress_upgraded",
		keys = { "wh3_cp1_lord_abilities_hidden_huntress_upgraded" },
		ox = 0, oy = 0 },
	{ marker = "horn_of_the_wild_hunt", name = "Horn of the Wild Hunt", trigger = "melee_unwavering",
		badge = "zz_auto_badge_horn_of_the_wild_hunt",
		keys = { "wh_dlc05_item_abilities_horn_of_the_wild_hunt" },
		ox = 0, oy = 0 },
	{ marker = "horn_of_vaul", name = "Horn of Vaul", trigger = "melee_unwavering",
		badge = "zz_auto_badge_horn_of_vaul",
		keys = { "wh2_main_item_abilities_dragonhorn" },
		ox = 0, oy = 0 },
	{ marker = "hornswaggle", name = "Hornswaggle", trigger = "melee_unwavering",
		badge = "zz_auto_badge_hornswaggle",
		keys = { "wh2_dlc11_character_abilities_hornswaggle" },
		ox = 0, oy = 0 },
	{ marker = "howl_of_the_great_beast", name = "Howl of the Great Beast", trigger = "melee_unwavering",
		badge = "zz_auto_badge_howl_of_the_great_beast",
		keys = { "wh3_dlc24_unit_abilities_howl_of_the_great_beast" },
		ox = 0, oy = 0 },
	{ marker = "hunter_of_champions", name = "Hunter of Champions", trigger = "melee_unwavering",
		badge = "zz_auto_badge_hunter_of_champions",
		keys = { "wh_dlc08_character_abilities_hunter_of_champions" },
		ox = 0, oy = 0 },
	{ marker = "hunters_snare", name = "Hunter's Snare", trigger = "melee_unwavering",
		badge = "zz_auto_badge_hunters_snare",
		keys = { "wh2_dlc13_lord_abilities_hunters_snare" },
		ox = 0, oy = 0 },
	{ marker = "hunters_trap", name = "Hunter's Trap", trigger = "melee_unwavering",
		badge = "zz_auto_badge_hunters_trap",
		keys = { "wh2_dlc13_lord_abilities_hunters_trap" },
		ox = 0, oy = 0 },
	{ marker = "spell_slaanesh_hysterical_frenzy_bound", name = "Hysterical Frenzy", trigger = "melee_unwavering",
		badge = "zz_auto_badge_spell_slaanesh_hysterical_frenzy_bound",
		keys = { "wh3_main_spell_slaanesh_hysterical_frenzy_bound" },
		ox = 0, oy = 0 },
	{ marker = "inspired_marksmanship_i", name = "Inspired Marksmanship I", trigger = "melee_unwavering",
		badge = "zz_auto_badge_inspired_marksmanship_i",
		keys = { "wh3_main_lord_abilities_inspired_marksmanship_i" },
		ox = 0, oy = 0 },
	{ marker = "inspired_marksmanship_ii", name = "Inspired Marksmanship II", trigger = "melee_unwavering",
		badge = "zz_auto_badge_inspired_marksmanship_ii",
		keys = { "wh3_main_lord_abilities_inspired_marksmanship_ii" },
		ox = 0, oy = 0 },
	{ marker = "inspired_marksmanship_iii", name = "Inspired Marksmanship III", trigger = "melee_unwavering",
		badge = "zz_auto_badge_inspired_marksmanship_iii",
		keys = { "wh3_main_lord_abilities_inspired_marksmanship_iii" },
		ox = 0, oy = 0 },
	{ marker = "iron_hand_captain", name = "Iron-Handed Captain", trigger = "melee_unwavering",
		badge = "zz_auto_badge_iron_hand_captain",
		keys = { "wh3_dlc27_character_abilities_iron_hand_captain" },
		ox = 0, oy = 0 },
	{ marker = "jagged_dagger", name = "Jagged Dagger", trigger = "melee_unwavering",
		badge = "zz_auto_badge_jagged_dagger",
		keys = { "wh_dlc03_item_abilities_jagged_dagger" },
		ox = 0, oy = 0 },
	{ marker = "locus_of_abjuration", name = "Locus of Abjuration", trigger = "melee_unwavering",
		badge = "zz_auto_badge_locus_of_abjuration",
		keys = { "wh3_main_character_abilities_locus_of_abjuration" },
		ox = 0, oy = 0 },
	{ marker = "locus_of_change", name = "Locus of Change", trigger = "melee_unwavering",
		badge = "zz_auto_badge_locus_of_change",
		keys = { "wh3_main_character_abilities_locus_of_change" },
		ox = 0, oy = 0 },
	{ marker = "locus_of_conjuration", name = "Locus of Conjuration", trigger = "melee_unwavering",
		badge = "zz_auto_badge_locus_of_conjuration",
		keys = { "wh3_main_character_abilities_locus_of_conjuration" },
		ox = 0, oy = 0 },
	{ marker = "looming_dread", name = "Looming Dread", trigger = "melee_unwavering",
		badge = "zz_auto_badge_looming_dread",
		keys = { "wh2_dlc14_lord_abilities_looming_dread" },
		ox = 0, oy = 0 },
	{ marker = "lord_of_dragons", name = "Lord of Dragons", trigger = "melee_unwavering",
		badge = "zz_auto_badge_lord_of_dragons",
		keys = { "wh2_dlc15_lord_abilities_lord_of_dragons" },
		ox = 0, oy = 0 },
	{ marker = "magical_animus", name = "Magical Animus", trigger = "melee_unwavering",
		badge = "zz_auto_badge_magical_animus",
		keys = { "wh_main_character_abilities_magical_animus" },
		ox = 0, oy = 0 },
	{ marker = "mark_of_the_plague_fleet", name = "Mark of the Plague Fleet", trigger = "melee_unwavering",
		badge = "zz_auto_badge_mark_of_the_plague_fleet",
		keys = { "wh3_dlc29_item_active_mark_of_the_plague_fleet" },
		ox = 0, oy = 0 },
	{ marker = "mark_of_yin", name = "Mark of Yin", trigger = "melee_unwavering",
		badge = "zz_auto_badge_mark_of_yin",
		keys = { "wh3_dlc24_unit_abilities_mark_of_yin" },
		ox = 0, oy = 0 },
	{ marker = "marked_by_ulthar", name = "Marked by Ulthar", trigger = "melee_unwavering",
		badge = "zz_auto_badge_marked_by_ulthar",
		keys = { "wh_dlc06_unit_abilities_marked_by_ulthar" },
		ox = 0, oy = 0 },
	{ marker = "marked_for_eatin", name = "Marked for Eatin'", trigger = "melee_unwavering",
		badge = "zz_auto_badge_marked_for_eatin",
		keys = { "wh3_dlc26_unit_abilities_marked_for_eatin" },
		ox = 0, oy = 0 },
	{ marker = "beguile", name = "Master of Beguilement", trigger = "melee_unwavering",
		badge = "zz_auto_badge_beguile",
		keys = { "wh_dlc04_lord_abilities_beguile" },
		ox = 0, oy = 0 },
	{ marker = "master_of_the_black_arts", name = "Master of the Black Arts", trigger = "melee_unwavering",
		badge = "zz_auto_badge_master_of_the_black_arts",
		keys = { "wh_main_lord_abilities_master_of_the_black_arts" },
		ox = 0, oy = 0 },
	{ marker = "master_predator", name = "Master Predator", trigger = "melee_unwavering",
		badge = "zz_auto_badge_master_predator",
		keys = { "wh2_dlc17_lord_abilities_master_predator" },
		ox = 0, oy = 0 },
	{ marker = "master_rune_of_breaking", name = "Master Rune of Breaking", trigger = "melee_unwavering",
		badge = "zz_auto_badge_master_rune_of_breaking",
		keys = { "wh2_dlc17_rune_abilities_master_rune_of_breaking" },
		ox = 0, oy = 0 },
	{ marker = "master_rune_of_negation", name = "Master Rune of Negation", trigger = "melee_unwavering",
		badge = "zz_auto_badge_master_rune_of_negation",
		keys = { "wh_dlc06_rune_abilities_master_rune_of_negation" },
		ox = 0, oy = 0 },
	{ marker = "master_rune_of_slowness", name = "Master Rune of Slowness", trigger = "melee_unwavering",
		badge = "zz_auto_badge_master_rune_of_slowness",
		keys = { "wh2_dlc17_rune_abilities_master_rune_of_slowness" },
		ox = 0, oy = 0 },
	{ marker = "maw_shard", name = "Maw Shard", trigger = "melee_unwavering",
		badge = "zz_auto_badge_maw_shard",
		keys = { "wh3_main_item_abilities_maw_shard" },
		ox = 0, oy = 0 },
	{ marker = "merciws_monstrous_regiment", name = "Merciw's Monstrous Regiment", trigger = "melee_unwavering",
		badge = "zz_auto_badge_merciws_monstrous_regiment",
		keys = { "wh3_dlc20_cataclysm_bound_merciws_monstrous_regiment",
			"wh3_dlc27_cataclysm_bound_merciws_monstrous_regiment" },
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
	{ marker = "mimic_cold_blooded", name = "Mirror (Cold-Blooded)", trigger = "melee_unwavering",
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
	{ marker = "unit_bound_missile_mirror", name = "Missile Mirror", trigger = "melee_unwavering",
		badge = "zz_auto_badge_unit_bound_missile_mirror",
		keys = { "wh3_dlc24_unit_bound_missile_mirror" },
		ox = 0, oy = 0 },
	{ marker = "mither", name = "Mither", trigger = "melee_unwavering",
		badge = "zz_auto_badge_mither",
		keys = { "wh2_dlc15_hero_abilities_mither" },
		ox = 0, oy = 0 },
	{ marker = "moonshine", name = "Moonshine", trigger = "melee_unwavering",
		badge = "zz_auto_badge_moonshine",
		keys = { "wh2_dlc11_item_abilities_moonshine" },
		ox = 0, oy = 0 },
	{ marker = "morgrims_eye", name = "Morgrim's Eye", trigger = "melee_unwavering",
		badge = "zz_auto_badge_morgrims_eye",
		keys = { "wh3_dlc23_item_abilities_morgrims_eye" },
		ox = 0, oy = 0 },
	{ marker = "muster_of_malevolents", name = "Muster of Malevolents", trigger = "melee_unwavering",
		badge = "zz_auto_badge_muster_of_malevolents",
		keys = { "wh2_dlc16_character_abilities_muster_of_malevolents" },
		ox = 0, oy = 0 },
	{ marker = "neferras_scrolls_of_mighty_incantations", name = "Neferra's Scrolls of Mighty Incantations", trigger = "melee_unwavering",
		badge = "zz_auto_badge_neferras_scrolls_of_mighty_incantations",
		keys = { "wh2_dlc09_item_abilities_neferras_scrolls_of_mighty_incantations" },
		ox = 0, oy = 0 },
	{ marker = "net_dem_up", name = "Net Dem Up!", trigger = "melee_unwavering",
		badge = "zz_auto_badge_net_dem_up",
		keys = { "wh3_dlc26_unit_abilities_net_dem_up" },
		ox = 0, oy = 0 },
	{ marker = "net_of_amyntok", name = "Net of Amyntok", trigger = "melee_unwavering",
		badge = "zz_auto_badge_net_of_amyntok",
		keys = { "wh_dlc04_spell_bound_net_of_amyntok" },
		ox = 0, oy = 0 },
	{ marker = "null_stone", name = "Null Stone", trigger = "melee_unwavering",
		badge = "zz_auto_badge_null_stone",
		keys = { "wh3_dlc27_item_abilities_null_stone" },
		ox = 0, oy = 0 },
	{ marker = "oath_of_vengeance", name = "Oath of Vengeance", trigger = "melee_unwavering",
		badge = "zz_auto_badge_oath_of_vengeance",
		keys = { "wh2_dlc10_lord_abilities_oath_of_vengeance" },
		ox = 0, oy = 0 },
	{ marker = "oil_flask", name = "Oil Flask", trigger = "melee_unwavering",
		badge = "zz_auto_badge_oil_flask",
		keys = { "wh2_dlc13_lord_abilities_oil_flask" },
		ox = 0, oy = 0 },
	{ marker = "ottos_scythe", name = "Otto's Scythe", trigger = "melee_unwavering",
		badge = "zz_auto_badge_ottos_scythe",
		keys = { "wh3_dlc29_item_active_ottos_scythe" },
		ox = 0, oy = 0 },
	{ marker = "pack_trap", name = "Pack Trap", trigger = "melee_unwavering",
		badge = "zz_auto_badge_pack_trap",
		keys = { "wh3_dlc24_unit_abilities_pack_trap" },
		ox = 0, oy = 0 },
	{ marker = "pageant_of_shrikes", name = "Pageant of Shrikes", trigger = "melee_unwavering",
		badge = "zz_auto_badge_pageant_of_shrikes",
		keys = { "wh2_dlc16_character_abilities_pageant_of_shrikes" },
		ox = 0, oy = 0 },
	{ marker = "pearl_of_infinite_bleakness", name = "Pearl of Infinite Bleakness", trigger = "melee_unwavering",
		badge = "zz_auto_badge_pearl_of_infinite_bleakness",
		keys = { "wh2_main_item_abilities_pearl_of_infinite_bleakness" },
		ox = 0, oy = 0 },
	{ marker = "pestilent_potions", name = "Pestilent Potions", trigger = "melee_unwavering",
		badge = "zz_auto_badge_pestilent_potions",
		keys = { "wh3_dlc20_item_abilities_pestilent_potions" },
		ox = 0, oy = 0 },
	{ marker = "phas_protection", name = "Pha's Protection", trigger = "melee_unwavering",
		badge = "zz_auto_badge_phas_protection",
		keys = { "wh3_main_spell_bound_phas_protection" },
		ox = 0, oy = 0 },
	{ marker = "pilgrimage_of_skulls", name = "Pilgrimage of Skulls", trigger = "melee_unwavering",
		badge = "zz_auto_badge_pilgrimage_of_skulls",
		keys = { "wh3_dlc26_lord_abilities_pilgrimage_of_skulls" },
		ox = 0, oy = 0 },
	{ marker = "plague_of_rust", name = "Plague of Rust", trigger = "melee_unwavering",
		badge = "zz_auto_badge_plague_of_rust",
		keys = { "wh3_main_spell_bound_plague_of_rust" },
		ox = 0, oy = 0 },
	{ marker = "plaque_of_dominion", name = "Plaque of Dominion", trigger = "melee_unwavering",
		badge = "zz_auto_badge_plaque_of_dominion",
		keys = { "wh2_main_item_abilities_plaque_of_dominion" },
		ox = 0, oy = 0 },
	{ marker = "potion_of_farsight", name = "Potion of Farsight", trigger = "melee_unwavering",
		badge = "zz_auto_badge_potion_of_farsight",
		keys = { "wh3_main_item_abilities_potion_of_farsight" },
		ox = 0, oy = 0 },
	{ marker = "potion_of_foolhardiness", name = "Potion of Foolhardiness", trigger = "melee_unwavering",
		badge = "zz_auto_badge_potion_of_foolhardiness",
		keys = { "wh_main_item_abilities_potion_of_foolhardiness" },
		ox = 0, oy = 0 },
	{ marker = "potion_of_speed", name = "Potion of Speed", trigger = "melee_unwavering",
		badge = "zz_auto_badge_potion_of_speed",
		keys = { "wh_main_item_abilities_potion_of_speed" },
		ox = 0, oy = 0 },
	{ marker = "power_familiar", name = "Power Familiar", trigger = "melee_unwavering",
		badge = "zz_auto_badge_power_familiar",
		keys = { "wh3_dlc27_item_abilities_power_familiar" },
		ox = 0, oy = 0 },
	{ marker = "power_siphon", name = "Power Siphon", trigger = "melee_unwavering",
		badge = "zz_auto_badge_power_siphon",
		keys = { "wh2_dlc11_lord_abilities_power_siphon" },
		ox = 0, oy = 0 },
	{ marker = "power_stone", name = "Power Stone", trigger = "melee_unwavering",
		badge = "zz_auto_badge_power_stone",
		keys = { "wh_main_item_abilities_power_stone" },
		ox = 0, oy = 0 },
	{ marker = "predatory_instincts", name = "Predatory Instincts", trigger = "melee_unwavering",
		badge = "zz_auto_badge_predatory_instincts",
		keys = { "wh3_cp1_lord_abilities_predatory_instincts" },
		ox = 0, oy = 0 },
	{ marker = "prey_of_anath_raema", name = "Prey of Anath Raema", trigger = "melee_unwavering",
		badge = "zz_auto_badge_prey_of_anath_raema",
		keys = { "wh_dlc05_character_abilities_prey_of_anath_raema" },
		ox = 0, oy = 0 },
	{ marker = "prey_of_the_blood_god", name = "Prey of the Blood God", trigger = "melee_unwavering",
		badge = "zz_auto_badge_prey_of_the_blood_god",
		keys = { "wh3_pro12_hero_abilities_prey_of_the_blood_god" },
		ox = 0, oy = 0 },
	{ marker = "prismatic_amplifier", name = "Prismatic Amplifier", trigger = "melee_unwavering",
		badge = "zz_auto_badge_prismatic_amplifier",
		keys = { "wh3_main_item_abilities_prismatic_amplifier" },
		ox = 0, oy = 0 },
	{ marker = "rally", name = "Rally!", trigger = "melee_unwavering",
		badge = "zz_auto_badge_rally",
		keys = { "wh_main_character_abilities_rally" },
		ox = 0, oy = 0 },
	{ marker = "dispatch_the_swarm_attack", name = "Ravaging Swarm", trigger = "melee_unwavering",
		badge = "zz_auto_badge_dispatch_the_swarm_attack",
		keys = { "wh3_dlc29_hero_active_dispatch_the_swarm_attack" },
		ox = 0, oy = 0 },
	{ marker = "dispatch_the_swarm_attack_upgraded", name = "Ravaging Swarm Upgraded", trigger = "melee_unwavering",
		badge = "zz_auto_badge_dispatch_the_swarm_attack_upgraded",
		keys = { "wh3_dlc29_hero_active_dispatch_the_swarm_attack_upgraded" },
		ox = 0, oy = 0 },
	{ marker = "tomb_king_rally", name = "Reanimate", trigger = "melee_unwavering",
		badge = "zz_auto_badge_tomb_king_rally",
		keys = { "wh2_dlc09_character_abilities_tomb_king_rally" },
		ox = 0, oy = 0 },
	{ marker = "tomb_king_rally_upgraded", name = "Reanimate Upgraded", trigger = "melee_unwavering",
		badge = "zz_auto_badge_tomb_king_rally_upgraded",
		keys = { "wh2_dlc09_character_abilities_tomb_king_rally_upgraded" },
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
	{ marker = "rune_of_slowness", name = "Rune of Slowness", trigger = "melee_unwavering",
		badge = "zz_auto_badge_rune_of_slowness",
		keys = { "wh2_dlc17_rune_abilities_rune_of_slowness" },
		ox = 0, oy = 0 },
	{ marker = "rune_of_thungni", name = "Rune of Thungni", trigger = "melee_unwavering",
		badge = "zz_auto_badge_rune_of_thungni",
		keys = { "wh3_dlc23_item_abilities_rune_of_thungni" },
		ox = 0, oy = 0 },
	{ marker = "sadistic_snare", name = "Sadistic Snare", trigger = "melee_unwavering",
		badge = "zz_auto_badge_sadistic_snare",
		keys = { "wh3_dlc23_lord_abilities_sadistic_snare" },
		ox = 0, oy = 0 },
	{ marker = "sceptre_of_stability", name = "Sceptre of Stability", trigger = "melee_unwavering",
		badge = "zz_auto_badge_sceptre_of_stability",
		keys = { "wh_main_item_abilities_sceptre_of_stability" },
		ox = 0, oy = 0 },
	{ marker = "scroll_of_destiny", name = "Scroll of Destiny", trigger = "melee_unwavering",
		badge = "zz_auto_badge_scroll_of_destiny",
		keys = { "wh3_main_item_abilities_scroll_of_destiny" },
		ox = 0, oy = 0 },
	{ marker = "scroll_of_leeching", name = "Scroll of Leeching", trigger = "melee_unwavering",
		badge = "zz_auto_badge_scroll_of_leeching",
		keys = { "wh_main_item_abilities_scroll_of_leeching" },
		ox = 0, oy = 0 },
	{ marker = "scroll_of_shielding", name = "Scroll of Shielding", trigger = "melee_unwavering",
		badge = "zz_auto_badge_scroll_of_shielding",
		keys = { "wh_main_item_abilities_scroll_of_shielding" },
		ox = 0, oy = 0 },
	{ marker = "shield_of_chaqua", name = "Shield of Chaqua", trigger = "melee_unwavering",
		badge = "zz_auto_badge_shield_of_chaqua",
		keys = { "wh2_dlc12_unit_abilities_shield_of_chaqua" },
		ox = 0, oy = 0 },
	{ marker = "dispatch_the_swarm_protect", name = "Shielding Swarm", trigger = "melee_unwavering",
		badge = "zz_auto_badge_dispatch_the_swarm_protect",
		keys = { "wh3_dlc29_hero_active_dispatch_the_swarm_protect" },
		ox = 0, oy = 0 },
	{ marker = "dispatch_the_swarm_protect_upgraded", name = "Shielding Swarm Upgraded", trigger = "melee_unwavering",
		badge = "zz_auto_badge_dispatch_the_swarm_protect_upgraded",
		keys = { "wh3_dlc29_hero_active_dispatch_the_swarm_protect_upgraded" },
		ox = 0, oy = 0 },
	{ marker = "shock_collar", name = "Shock Collar", trigger = "melee_unwavering",
		badge = "zz_auto_badge_shock_collar",
		keys = { "wh2_dlc16_hero_abilities_shock_collar" },
		ox = 0, oy = 0 },
	{ marker = "silence_the_prey", name = "Silence the Prey", trigger = "melee_unwavering",
		badge = "zz_auto_badge_silence_the_prey",
		keys = { "wh3_main_character_abilities_silence_the_prey" },
		ox = 0, oy = 0 },
	{ marker = "skavenbrew", name = "Skavenbrew", trigger = "melee_unwavering",
		badge = "zz_auto_badge_skavenbrew",
		keys = { "wh2_main_item_abilities_skavenbrew" },
		ox = 0, oy = 0 },
	{ marker = "skjalandirs_fall", name = "Skjalandir's Fall", trigger = "melee_unwavering",
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
	{ marker = "spearfishers_net", name = "Spearfisher's Net", trigger = "melee_unwavering",
		badge = "zz_auto_badge_spearfishers_net",
		keys = { "wh2_dlc11_lord_abilities_spearfishers_net" },
		ox = 0, oy = 0 },
	{ marker = "spell_wrought_sceptre", name = "Spell-Wrought Sceptre", trigger = "melee_unwavering",
		badge = "zz_auto_badge_spell_wrought_sceptre",
		keys = { "wh3_dlc23_weapon_abilities_spell_wrought_sceptre" },
		ox = 0, oy = 0 },
	{ marker = "spider_web_attack", name = "Spiderweb Attack", trigger = "melee_unwavering",
		badge = "zz_auto_badge_spider_web_attack",
		keys = { "wh3_dlc26_character_abilities_spider_web_attack" },
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
	{ marker = "sword_of_filth", name = "Sword of Filth", trigger = "melee_unwavering",
		badge = "zz_auto_badge_sword_of_filth",
		keys = { "wh3_dlc25_weapon_abilities_sword_of_filth" },
		ox = 0, oy = 0 },
	{ marker = "tacticians_rally", name = "Tacticians, Rally!", trigger = "melee_unwavering",
		badge = "zz_auto_badge_tacticians_rally",
		keys = { "wh3_dlc24_character_abilities_tacticians_rally" },
		ox = 0, oy = 0 },
	{ marker = "taunt", name = "Taunt", trigger = "melee_unwavering",
		badge = "zz_auto_badge_taunt",
		keys = { "wh2_dlc11_character_abilities_taunt" },
		ox = 0, oy = 0 },
	{ marker = "tendrils_of_the_sea", name = "Tendrils of the Sea", trigger = "melee_unwavering",
		badge = "zz_auto_badge_tendrils_of_the_sea",
		keys = { "wh3_dlc29_hero_active_tendrils_of_the_sea" },
		ox = 0, oy = 0 },
	{ marker = "terrorgheist_skull", name = "Terrorgheist Skull", trigger = "melee_unwavering",
		badge = "zz_auto_badge_terrorgheist_skull",
		keys = { "wh_dlc08_item_abilities_terrorgheist_skull" },
		ox = 0, oy = 0 },
	{ marker = "averland_runefang", name = "The Averland Runefang", trigger = "melee_unwavering",
		badge = "zz_auto_badge_averland_runefang",
		keys = { "wh2_dlc13_weapon_abilities_averland_runefang" },
		ox = 0, oy = 0 },
	{ marker = "the_bane_shield", name = "The Bane Shield", trigger = "melee_unwavering",
		badge = "zz_auto_badge_the_bane_shield",
		keys = { "wh2_main_item_abilities_the_bane_shield" },
		ox = 0, oy = 0 },
	{ marker = "the_black_tongue", name = "The Black Tongue", trigger = "melee_unwavering",
		badge = "zz_auto_badge_the_black_tongue",
		keys = { "wh3_dlc27_character_abilities_the_black_tongue" },
		ox = 0, oy = 0 },
	{ marker = "the_chromatic_tome", name = "The Chromatic Tome", trigger = "melee_unwavering",
		badge = "zz_auto_badge_the_chromatic_tome",
		keys = { "wh3_main_item_abilities_the_chromatic_tome" },
		ox = 0, oy = 0 },
	{ marker = "the_dark_master", name = "The Dark Master", trigger = "melee_unwavering",
		badge = "zz_auto_badge_the_dark_master",
		keys = { "wh3_main_lord_abilities_the_dark_master" },
		ox = 0, oy = 0 },
	{ marker = "enfeebling_foe", name = "The Enfeebling Foe", trigger = "melee_unwavering",
		badge = "zz_auto_badge_enfeebling_foe",
		keys = { "wh3_dlc23_spell_bound_enfeebling_foe",
			"wh3_dlc27_spell_bound_enfeebling_foe",
			"wh3_main_spell_bound_enfeebling_foe",
			"wh3_twa08_spell_bound_enfeebling_foe_keeper_of_secrets_ror" },
		ox = 0, oy = 0 },
	{ marker = "the_golden_eye_of_tzeentch", name = "The Golden Eye of Tzeentch", trigger = "melee_unwavering",
		badge = "zz_auto_badge_the_golden_eye_of_tzeentch",
		keys = { "wh3_dlc24_item_abilities_the_golden_eye_of_tzeentch" },
		ox = 0, oy = 0 },
	{ marker = "the_guiding_eye", name = "The Guiding Eye", trigger = "melee_unwavering",
		badge = "zz_auto_badge_the_guiding_eye",
		keys = { "wh2_main_item_abilities_the_guiding_eye" },
		ox = 0, oy = 0 },
	{ marker = "the_hammer_of_karak_drazh", name = "The Hammer of Karak Drazh", trigger = "melee_unwavering",
		badge = "zz_auto_badge_the_hammer_of_karak_drazh",
		keys = { "wh_main_weapon_abilities_the_hammer_of_karak_drazh" },
		ox = 0, oy = 0 },
	{ marker = "undeath_sulekhim_hand_of_dust", name = "The Hand of Dust", trigger = "melee_unwavering",
		badge = "zz_auto_badge_undeath_sulekhim_hand_of_dust",
		keys = { "wh3_dlc29_spell_bound_undeath_sulekhim_hand_of_dust" },
		ox = 0, oy = 0 },
	{ marker = "the_liber_noctus", name = "The Liber Noctus", trigger = "melee_unwavering",
		badge = "zz_auto_badge_the_liber_noctus",
		keys = { "wh_dlc04_item_abilities_the_liber_noctus" },
		ox = 0, oy = 0 },
	{ marker = "lions_shield", name = "The Lion's Shield", trigger = "melee_unwavering",
		badge = "zz_auto_badge_lions_shield",
		keys = { "wh_dlc07_lord_abilities_lions_shield" },
		ox = 0, oy = 0 },
	{ marker = "the_praise_of_slaanesh", name = "The Praise of Slaanesh", trigger = "melee_unwavering",
		badge = "zz_auto_badge_the_praise_of_slaanesh",
		keys = { "wh3_dlc27_lord_abilities_the_praise_of_slaanesh" },
		ox = 0, oy = 0 },
	{ marker = "the_seerstaff_of_saphery", name = "The Seerstaff of Saphery", trigger = "melee_unwavering",
		badge = "zz_auto_badge_the_seerstaff_of_saphery",
		keys = { "wh2_main_spell_bound_the_seerstaff_of_saphery" },
		ox = 0, oy = 0 },
	{ marker = "the_tricksters_pendant", name = "The Trickster's Pendant", trigger = "melee_unwavering",
		badge = "zz_auto_badge_the_tricksters_pendant",
		keys = { "wh2_main_item_abilities_the_tricksters_pendant" },
		ox = 0, oy = 0 },
	{ marker = "the_vial_of_hashut", name = "The Vial of Hashut", trigger = "melee_unwavering",
		badge = "zz_auto_badge_the_vial_of_hashut",
		keys = { "wh3_dlc23_item_abilities_the_vial_of_hashut" },
		ox = 0, oy = 0 },
	{ marker = "the_vortex_shard", name = "The Vortex Shard", trigger = "melee_unwavering",
		badge = "zz_auto_badge_the_vortex_shard",
		keys = { "wh2_main_item_abilities_the_vortex_shard" },
		ox = 0, oy = 0 },
	{ marker = "the_wintertooth_crown", name = "The Wintertooth Crown", trigger = "melee_unwavering",
		badge = "zz_auto_badge_the_wintertooth_crown",
		keys = { "wh_dlc08_item_abilities_the_wintertooth_crown" },
		ox = 0, oy = 0 },
	{ marker = "wissenland_runefang", name = "The Wissenland Runefang", trigger = "melee_unwavering",
		badge = "zz_auto_badge_wissenland_runefang",
		keys = { "wh2_dlc13_weapon_abilities_wissenland_runefang" },
		ox = 0, oy = 0 },
	{ marker = "the_withering", name = "The Withering", trigger = "melee_unwavering",
		badge = "zz_auto_badge_the_withering",
		keys = { "wh3_dlc23_spell_bound_the_withering",
			"wh3_twa08_spell_bound_the_withering" },
		ox = 0, oy = 0 },
	{ marker = "they_needs_stabbin", name = "They Needs Stabbin’", trigger = "melee_unwavering",
		badge = "zz_auto_badge_they_needs_stabbin",
		keys = { "wh2_dlc15_character_abilities_they_needs_stabbin" },
		ox = 0, oy = 0 },
	{ marker = "thorns_aura", name = "Thorn's Aura", trigger = "melee_unwavering",
		badge = "zz_auto_badge_thorns_aura",
		keys = { "wh3_dlc24_hero_abilities_thorns_aura" },
		ox = 0, oy = 0 },
	{ marker = "thunderburner", name = "Thunderburner", trigger = "melee_unwavering",
		badge = "zz_auto_badge_thunderburner",
		keys = { "wh3_dlc25_unit_abilities_thunderburner" },
		ox = 0, oy = 0 },
	{ marker = "thunderburner_upgraded", name = "Thunderburner Upgraded", trigger = "melee_unwavering",
		badge = "zz_auto_badge_thunderburner_upgraded",
		keys = { "wh3_dlc25_unit_abilities_thunderburner_upgraded" },
		ox = 0, oy = 0 },
	{ marker = "titan_headsman", name = "Titan Headsman", trigger = "melee_unwavering",
		badge = "zz_auto_badge_titan_headsman",
		keys = { "wh3_dlc25_hero_abilities_titan_headsman" },
		ox = 0, oy = 0 },
	{ marker = "torment_blade", name = "Torment Blade", trigger = "melee_unwavering",
		badge = "zz_auto_badge_torment_blade",
		keys = { "wh3_main_weapon_abilities_torment_blade" },
		ox = 0, oy = 0 },
	{ marker = "tricksters_shard", name = "Trickster's Shard", trigger = "melee_unwavering",
		badge = "zz_auto_badge_tricksters_shard",
		keys = { "wh_main_item_abilities_tricksters_shard" },
		ox = 0, oy = 0 },
	{ marker = "trophy_heads", name = "Trophy Heads", trigger = "melee_unwavering",
		badge = "zz_auto_badge_trophy_heads",
		keys = { "wh2_main_lord_abilities_trophy_heads",
			"wh3_main_daemon_wings_abilities_trophy_heads" },
		ox = 0, oy = 0 },
	{ marker = "twilight_horn_i", name = "Twilight Horn I", trigger = "melee_unwavering",
		badge = "zz_auto_badge_twilight_horn_i",
		keys = { "wh2_dlc16_item_abilities_twilight_horn_i" },
		ox = 0, oy = 0 },
	{ marker = "undeath_resurgent", name = "Undeath Resurgent", trigger = "melee_unwavering",
		badge = "zz_auto_badge_undeath_resurgent",
		keys = { "wh_main_character_abilities_undeath_resurgent" },
		ox = 0, oy = 0 },
	{ marker = "unholy_clamour", name = "Unholy Clamour", trigger = "melee_unwavering",
		badge = "zz_auto_badge_unholy_clamour",
		keys = { "wh2_main_mount_abilities_unholy_clamour" },
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
	{ marker = "verminous_fury", name = "Verminous Fury", trigger = "melee_unwavering",
		badge = "zz_auto_badge_verminous_fury",
		keys = { "wh3_dlc29_lord_abilities_verminous_fury" },
		ox = 0, oy = 0 },
	{ marker = "virulent_contagion", name = "Virulent Contagion", trigger = "melee_unwavering",
		badge = "zz_auto_badge_virulent_contagion",
		keys = { "wh3_main_lord_abilities_virulent_contagion" },
		ox = 0, oy = 0 },
	{ marker = "virulent_contagion_upgraded", name = "Virulent Contagion Upgraded", trigger = "melee_unwavering",
		badge = "zz_auto_badge_virulent_contagion_upgraded",
		keys = { "wh3_main_lord_abilities_virulent_contagion_upgraded" },
		ox = 0, oy = 0 },
	{ marker = "visions_of_madness", name = "Visions of Madness", trigger = "melee_unwavering",
		badge = "zz_auto_badge_visions_of_madness",
		keys = { "wh3_dlc27_qb_unit_abilities_visions_of_madness" },
		ox = 0, oy = 0 },
	{ marker = "void_pendulum", name = "Void Pendulum", trigger = "melee_unwavering",
		badge = "zz_auto_badge_void_pendulum",
		keys = { "wh3_main_item_abilities_void_pendulum" },
		ox = 0, oy = 0 },
	{ marker = "vorozhejas_foresight", name = "Vorozheja's Foresight", trigger = "melee_unwavering",
		badge = "zz_auto_badge_vorozhejas_foresight",
		keys = { "wh3_dlc24_hero_abilities_vorozhejas_foresight" },
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
	{ marker = "wardens_cage", name = "Warden's Cage", trigger = "melee_unwavering",
		badge = "zz_auto_badge_wardens_cage",
		keys = { "wh2_dlc15_character_abilities_wardens_cage" },
		ox = 0, oy = 0 },
	{ marker = "warp_gaze", name = "Warp Gaze", trigger = "melee_unwavering",
		badge = "zz_auto_badge_warp_gaze",
		keys = { "wh_pro04_unit_abilities_warp_gaze" },
		ox = 0, oy = 0 },
	{ marker = "warpstiletto", name = "Warpstiletto", trigger = "melee_unwavering",
		badge = "zz_auto_badge_warpstiletto",
		keys = { "wh3_dlc29_item_abilities_warpstiletto" },
		ox = 0, oy = 0 },
	{ marker = "warpstone_tokens", name = "Warpstone Tokens", trigger = "melee_unwavering",
		badge = "zz_auto_badge_warpstone_tokens",
		keys = { "wh3_dlc29_item_abilities_warpstone_tokens" },
		ox = 0, oy = 0 },
	{ marker = "watched_by_the_watcher", name = "Watched by the Watcher", trigger = "melee_unwavering",
		badge = "zz_auto_badge_watched_by_the_watcher",
		keys = { "wh3_dlc24_character_abilities_watched_by_the_watcher" },
		ox = 0, oy = 0 },
	{ marker = "were_you_goin", name = "Where You Goin!?", trigger = "melee_unwavering",
		badge = "zz_auto_badge_were_you_goin",
		keys = { "wh3_dlc26_character_abilities_were_you_goin" },
		ox = 0, oy = 0 },
	{ marker = "whip_of_agony", name = "Whip of Agony", trigger = "melee_unwavering",
		badge = "zz_auto_badge_whip_of_agony",
		keys = { "wh2_twa03_weapon_abilities_whip_of_agony" },
		ox = 0, oy = 0 },
	{ marker = "whip_of_misery", name = "Whip of Misery", trigger = "melee_unwavering",
		badge = "zz_auto_badge_whip_of_misery",
		keys = { "wh2_main_spell_bound_whip_of_agony" },
		ox = 0, oy = 0 },
	{ marker = "whiplash", name = "Whiplash!", trigger = "melee_unwavering",
		badge = "zz_auto_badge_whiplash",
		keys = { "wh2_dlc14_lord_abilities_whiplash" },
		ox = 0, oy = 0 },
	{ marker = "whispering_mist", name = "Whispering Mist", trigger = "melee_unwavering",
		badge = "zz_auto_badge_whispering_mist",
		keys = { "wh3_dlc29_hero_abilities_whispering_mist" },
		ox = 0, oy = 0 },
	{ marker = "whispering_skull", name = "Whispering Skull", trigger = "melee_unwavering",
		badge = "zz_auto_badge_whispering_skull",
		keys = { "wh3_dlc29_item_abilities_whispering_skull" },
		ox = 0, oy = 0 },
	{ marker = "wild_abandon", name = "Wild Abandon", trigger = "melee_unwavering",
		badge = "zz_auto_badge_wild_abandon",
		keys = { "wh3_dlc26_lord_abilities_wild_abandon" },
		ox = 0, oy = 0 },
	{ marker = "willing_prey", name = "Willing Prey", trigger = "melee_unwavering",
		badge = "zz_auto_badge_willing_prey",
		keys = { "wh3_main_lord_abilities_willing_prey" },
		ox = 0, oy = 0 },
	{ marker = "winds_of_change", name = "Winds of Change", trigger = "melee_unwavering",
		badge = "zz_auto_badge_winds_of_change",
		keys = { "wh3_main_daemon_body_abilities_winds_of_change" },
		ox = 0, oy = 0 },
	{ marker = "word_of_change", name = "Word of Change", trigger = "melee_unwavering",
		badge = "zz_auto_badge_word_of_change",
		keys = { "wh3_main_daemon_head_abilities_word_of_change" },
		ox = 0, oy = 0 },
	{ marker = "word_of_pain", name = "Word of Pain", trigger = "melee_unwavering",
		badge = "zz_auto_badge_word_of_pain",
		keys = { "wh2_dlc10_spell_bound_word_of_pain",
			"wh3_dlc27_spell_dark_magic_word_of_pain_bound_1use" },
		ox = 0, oy = 0 },
	{ marker = "woven_mist", name = "Woven Mist", trigger = "melee_unwavering",
		badge = "zz_auto_badge_woven_mist",
		keys = { "wh_dlc05_unit_abilities_woven_mist" },
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
	{ marker = "youre_next", name = "You're Next!", trigger = "melee_unwavering",
		badge = "zz_auto_badge_youre_next",
		keys = { "wh2_dlc15_lord_abilities_youre_next" },
		ox = 0, oy = 0 },
	-- health<=75, no melee gate (the R1 heal / replenish batch) (36 entries)
	{ marker = "berry_wine", name = "Berry Wine", trigger = "ushoran_health",
		badge = "zz_auto_badge_berry_wine",
		keys = { "wh2_dlc16_item_abilities_berry_wine" },
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
	{ marker = "dreaming_ring_i", name = "Dreaming Ring I", trigger = "ushoran_health",
		badge = "zz_auto_badge_dreaming_ring_i",
		keys = { "wh2_dlc16_item_abilities_dreaming_ring_i" },
		ox = 0, oy = 0 },
	{ marker = "dreaming_ring_ii", name = "Dreaming Ring II", trigger = "ushoran_health",
		badge = "zz_auto_badge_dreaming_ring_ii",
		keys = { "wh2_dlc16_item_abilities_dreaming_ring_ii" },
		ox = 0, oy = 0 },
	{ marker = "dreaming_ring_iii", name = "Dreaming Ring III", trigger = "ushoran_health",
		badge = "zz_auto_badge_dreaming_ring_iii",
		keys = { "wh2_dlc16_item_abilities_dreaming_ring_iii" },
		ox = 0, oy = 0 },
	{ marker = "earth_blood", name = "Earth Blood", trigger = "ushoran_health",
		badge = "zz_auto_badge_earth_blood",
		keys = { "wh2_dlc16_spell_bound_earth_blood",
			"wh3_main_spell_bound_earth_blood" },
		ox = 0, oy = 0 },
	{ marker = "elfish_healing_herbs", name = "Elvish Healing Herbs", trigger = "ushoran_health",
		badge = "zz_auto_badge_elfish_healing_herbs",
		keys = { "wh3_dlc27_unit_abilities_elfish_healing_herbs" },
		ox = 0, oy = 0 },
	{ marker = "fleshy_abundance", name = "Fleshy Abundance", trigger = "ushoran_health",
		badge = "zz_auto_badge_fleshy_abundance",
		keys = { "wh3_dlc20_spell_bound_fleshy_abundance" },
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
	{ marker = "locus_of_fecundity", name = "Locus of Fecundity", trigger = "ushoran_health",
		badge = "zz_auto_badge_locus_of_fecundity",
		keys = { "wh3_main_character_abilities_locus_of_fecundity" },
		ox = 0, oy = 0 },
	{ marker = "makaissons_persuader", name = "Makaisson's Persuader", trigger = "ushoran_health",
		badge = "zz_auto_badge_makaissons_persuader",
		keys = { "wh3_dlc25_weapon_abilities_makaissons_persuader" },
		ox = 0, oy = 0 },
	{ marker = "neuroparasites", name = "Necroparasites", trigger = "ushoran_health",
		badge = "zz_auto_badge_neuroparasites",
		keys = { "wh2_dlc16_unit_abilities_neuroparasites" },
		ox = 0, oy = 0 },
	{ marker = "necrotic_phylactry", name = "Necrotic Phylactery", trigger = "ushoran_health",
		badge = "zz_auto_badge_necrotic_phylactry",
		keys = { "wh3_dlc25_item_abilities_necrotic_phylactry" },
		ox = 0, oy = 0 },
	{ marker = "patch_up", name = "Patch Up", trigger = "ushoran_health",
		badge = "zz_auto_badge_patch_up",
		keys = { "wh2_dlc13_character_abilities_patch_up" },
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
	{ marker = "radiant_gem_of_hoeth", name = "Radiant Gem of Hoeth", trigger = "ushoran_health",
		badge = "zz_auto_badge_radiant_gem_of_hoeth",
		keys = { "wh2_main_spell_bound_radiant_gem_of_hoeth" },
		ox = 0, oy = 0 },
	{ marker = "reforge", name = "Reforge", trigger = "ushoran_health",
		badge = "zz_auto_badge_reforge",
		keys = { "wh3_dlc23_character_abilities_reforge" },
		ox = 0, oy = 0 },
	{ marker = "regenerating_flesh", name = "Regenerating Flesh", trigger = "ushoran_health",
		badge = "zz_auto_badge_regenerating_flesh",
		keys = { "wh_main_item_abilities_regenerating_flesh" },
		ox = 0, oy = 0 },
	{ marker = "regrowth", name = "Regrowth", trigger = "ushoran_health",
		badge = "zz_auto_badge_regrowth",
		keys = { "wh2_dlc16_spell_bound_regrowth" },
		ox = 0, oy = 0 },
	{ marker = "remouldered", name = "Remouldered", trigger = "ushoran_health",
		badge = "zz_auto_badge_remouldered",
		keys = { "wh2_dlc16_lord_abilities_remouldered" },
		ox = 0, oy = 0 },
	{ marker = "restore", name = "Restore", trigger = "ushoran_health",
		badge = "zz_auto_badge_restore",
		keys = { "wh2_dlc09_character_abilities_restore" },
		ox = 0, oy = 0 },
	{ marker = "revivification_crystal", name = "Revivification Crystal", trigger = "ushoran_health",
		badge = "zz_auto_badge_revivification_crystal",
		keys = { "wh2_main_unit_abilities_revivification_crystal" },
		ox = 0, oy = 0 },
	{ marker = "saint_annushkas_finger_bone", name = "Saint Annushka's Finger Bone", trigger = "ushoran_health",
		badge = "zz_auto_badge_saint_annushkas_finger_bone",
		keys = { "wh3_main_item_abilities_saint_annushkas_finger_bone" },
		ox = 0, oy = 0 },
	{ marker = "salyaks_lullaby", name = "Salyak's Lullaby", trigger = "ushoran_health",
		badge = "zz_auto_badge_salyaks_lullaby",
		keys = { "wh3_main_character_abilities_salyaks_lullaby" },
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
	{ marker = "trollguts", name = "Trollguts", trigger = "ushoran_health",
		badge = "zz_auto_badge_trollguts",
		keys = { "wh3_dlc26_spell_bound_trollguts" },
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
	{ marker = "the_dance_of_dreaming", name = "The Dance of Dreaming", trigger = "melee_unwavering",
		badge = "zz_auto_badge_the_dance_of_dreaming",
		keys = { "wh3_dlc27_lord_abilities_the_dance_of_dreaming" },
		ox = 0, oy = 0 },
	{ marker = "the_waltz_of_lethargy", name = "The Waltz of Lethargy", trigger = "melee_unwavering",
		badge = "zz_auto_badge_the_waltz_of_lethargy",
		keys = { "wh3_dlc27_lord_abilities_the_waltz_of_lethargy" },
		ox = 0, oy = 0 },
	{ marker = "ultimate_verdict", name = "Ultimate Verdict", trigger = "melee_unwavering",
		badge = "zz_auto_badge_ultimate_verdict",
		keys = { "wh3_cp1_character_abilities_terrifying_presence" },
		ox = 0, oy = 0 },
}

-- A flat list of every key above, built once when the file loads. When the
-- mod asks a unit "do you carry any of our abilities?", this is the list
-- the unit's answers are checked against - so adding an entry to the table
-- above is the only edit needed to watch one more ability.
local ALL_ABILITY_KEYS = {}
for _, ability in ipairs(ABILITIES) do
	for _, key in ipairs(ability.keys) do
		ALL_ABILITY_KEYS[#ALL_ABILITY_KEYS + 1] = key
	end
end

-- THE STATIC KEY -> MARKER MAP (item 1.3): every database key listed in the
-- table above, mapped to its ability's short marker, built once at load. It
-- turns a unit's cached owned keys (owned_keys_by_unit, SECTION 2) into the
-- short list of abilities that unit can actually carry; the poll's per-unit
-- ability loop (SECTION 7) walks that list instead of the whole table. Built
-- from the same keys the scan matches on, so it can never drift.
local marker_by_key = {}
for _, ability in ipairs(ABILITIES) do
	for _, key in ipairs(ability.keys) do
		marker_by_key[key] = ability.marker
	end
end

-- THE STATIC MARKER -> ENTRY MAP (item 3.1): the ability entry behind each
-- short marker name, built once when the file loads. It replaces the old
-- per-call walk of the whole abilities table with a single table read, so
-- each badge / letter / active-set lookup costs O(1) instead of O(entries).
-- INVARIANT: it is built AFTER the abilities table above is fully filled in
-- (it never changes afterwards), and every entry's own marker maps straight
-- back to that entry - the harness asserts it, because a mismatch would
-- silently drop a badge.
local ability_by_marker = {}
for _, ability in ipairs(ABILITIES) do
	ability_by_marker[ability.marker] = ability
end

-- THE STATIC BADGE-ID -> ENTRY MAP (item 3.1, audit): the same trick for the
-- click router's badge lookup - a badge id is unique per entry, so one read
-- answers it. Built after the abilities table, with the same invariant.
local ability_by_badge = {}
for _, ability in ipairs(ABILITIES) do
	ability_by_badge[ability.badge] = ability
end

-- THE STATIC KEY MEMBERSHIP SET (item 3.1): the same keys as the flat list
-- above, but as a set, so "is this engine key one of ours?" is a single table
-- read rather than a walk of the list. The flat LIST is kept for the ordered
-- iterations that need it. INVARIANT: built after the abilities table is
-- filled in, and every key of every entry is in the set - the harness asserts
-- it, because a missing key would silently miss an owned ability.
local ALL_ABILITY_KEYS_SET = {}
for _, ability in ipairs(ABILITIES) do
	for _, key in ipairs(ability.keys) do
		ALL_ABILITY_KEYS_SET[key] = true
	end
end

-- Look up an ability entry by its short marker name. nil = unknown name;
-- the callers treat nil as "nothing to do" rather than an error. This is
-- the O(1) map read (item 3.1), not a walk of the table.
local function ability_for(marker)
	return ability_by_marker[marker]
end

-- Look up an ability entry by its badge id - that is how a badge click is
-- routed to "its" ability. nil = unknown id (click ignored). Also an O(1)
-- map read (item 3.1, audit).
local function ability_for_badge(badge_id)
	return ability_by_badge[badge_id]
end

-- The charge trigger's on/off switches. FIRE_ON_CHARGE is the normal mode
-- (the proven charge window). FIRE_ON_MELEE adds the plain in-melee arm -
-- this round BOTH are ON (user-approved: Deadly Onslaught has a component
-- useful in melee), so the ability fires on the charge window or once the
-- unit is already fighting. The two arms cannot both hold on one
-- evaluation (a charging unit has not made contact - see SECTION 4).
local FIRE_ON_CHARGE = true
local FIRE_ON_MELEE  = true    -- the user-approved in-melee arm (this round)

-- THE CHARGE TEST'S NUMBERS (used by SECTION 4).
-- A charge here means an attack order on an enemy that is about to CONNECT
-- - not simply "moving fast", and not the instant the attack is ordered.
-- The engine offers no direct "is charging" flag, so the mod composes the
-- test from measurements: running, not yet in melee, an enemy is targeted,
-- the distance leaves room for a run-up but impact is imminent:
--   * at least CHARGE_MIN_DISTANCE_M metres away (a charge needs a run-up),
--   * at most CHARGE_MAX_DISTANCE_M metres away (not the whole map),
--   * estimated time until contact at most CHARGE_TIME_TO_CONTACT_S seconds.
-- (A documented "compare position with ordered position" signal was tried
-- and measured to track time-since-the-order instead of attack-versus-move;
-- it is not used. The real attack-versus-move signal is "has a target".)
local CHARGE_MIN_DISTANCE_M    = 12     -- metres - shortest run-up that still counts
local CHARGE_MAX_DISTANCE_M    = 60     -- metres - longest range that still counts
local CHARGE_TIME_TO_CONTACT_S = 4      -- seconds - fire when impact is this close

-- GLORIOUS DEATH'S TRIGGER RANGE (this round) - DELIBERATELY CONSERVATIVE.
-- The ability's wiki effects line reads "Effect range: 55m" (reference only);
-- the user's FIELD TESTING showed a 55 m trigger fired too early, so this is
-- a TIGHTER, deliberately conservative trigger range - GLORIOUS_DEATH_RANGE_M
-- is BELOW the ability's 55 m wiki aura on purpose. The gate below offers,
-- and re-checks just before the cast, an in-melee Slayer ally only when the
-- owner is within GLORIOUS_DEATH_RANGE_M metres of it.
local GLORIOUS_DEATH_RANGE_M = 25

-- How often the battlefield watcher looks at the units, in milliseconds
-- (250 ms = 4 times a second).
local POLL_MS = 250

-- THE SHORT GUARD - the short safety brake, in seconds, per (unit,
-- ability): one pair may not attempt twice inside this window. The
-- readiness gate (SECTION 3) is the real brake; this only stops doubles.
local GUARD_SECONDS = 2

-- THE COOLDOWN-HOLD BACK-OFF. There is NO per-unit engine read of a special
-- ability's cooldown / readiness / active state: the one read the API offers
-- (can_perform_special_ability) answers TRUE while the engine is refusing the
-- fire with "does not support this special ability", and the dial-button state
-- covers only the SELECTED unit. So the mod cannot KNOW a pair is on cooldown
-- before it tries - it LEARNS it from the engine's own refusal. The first
-- refusal of an episode speaks once (in the logging build); a REPEATED one
-- backs that pair off HOLD_SECONDS instead of the short guard, so a long
-- cooldown costs a handful of probes instead of one attempt every 2 s. An
-- ACCEPTED fire is the only thing that clears the episode.
local HOLD_SECONDS = 8

-- THE HARD BOUND. A hold is a SKIP, and nothing may sit out forever because of
-- a stuck flag or a stale read: however long a pair has been held, an attempt
-- is forced once the hold has lasted MAX_HOLD_SECONDS.
local MAX_HOLD_SECONDS = 20

-- How often, in polls, the cheap IDENTITY re-check runs for a unit we have
-- not yet found our ability on (16 x 250 ms = every 4 seconds). The check
-- reads ONE cheap engine value (the identity watch below); the FULL scan it
-- used to run here now happens only when that value changes, plus the slow
-- fallback beneath this constant.
local REDETECT_EVERY_N_POLLS = 16

-- THE IDENTITY WATCH (item 3.4). The re-check above no longer re-runs the
-- full scan: for a unit carrying nothing of ours the poll reads ONE cheap
-- engine value - the unit's identity, battle_unit:type(), the land_units key
-- the engine documents as "Returns the unit type of the unit, from the
-- land_units table" - and re-scans ONLY when that value CHANGES. That is what
-- catches a transformation or a mount: the type key moves, so a loadout that
-- gained abilities mid-battle is picked up and its new abilities arm and
-- fire. The read costs almost nothing, so the per-4-s engine work of scanning
-- every ability-less unit is gone.
local FALLBACK_RESCAN_EVERY_N_POLLS = 240   -- 240 x 250 ms = every 60 seconds

-- THE SLOW SAFETY FALLBACK, spelled out: every FALLBACK_RESCAN_EVERY_N_POLLS
-- polls a full scan still runs for a unit carrying nothing of ours, whatever
-- its identity says - so an unreadable or unchanging identity degrades to the
-- old behaviour, just far rarer (60 s instead of 4 s).

-- How often the poll re-lists the player's units, in polls (40 x 250 ms =
-- every 10 seconds). A battle can GROW its army after the first list was
-- built - a summon, a split, a transformation puts NEW units on the field
-- mid-battle - and the watch list must adopt them like any starting unit
-- (tracked, scanned, selection callback registered) without disturbing the
-- units already on it. Low-frequency enough that the handful of engine
-- reads never shows, frequent enough that a fresh arrival is picked up
-- within seconds of appearing.
local RELIST_EVERY_N_POLLS = 40

-- Explicitly take control of the unit before ordering it. OFF: issuing an
-- order takes control anyway, and an explicit takeover is a candidate
-- cause of the player's own order being cancelled.
local TAKE_CONTROL_FIRST = false

-- Hand the unit back to the player after the attempt - but ONLY a control
-- this mod actually took. A release is never sent on its own: the engine
-- answers ok to releasing control we never had, and it may read the
-- release as "drop whatever this unit was ordered to do", so with the
-- take OFF (the default) a release can never happen at all.
local RELEASE_CONTROL_AFTER = true


-- ============================================================================
-- SECTION 2 - BOOKKEEPING
--   The state the mod keeps while the battle runs: which units it watches,
--   which unit is currently selected, and the ON/OFF switch of every
--   (unit, ability) pair.
-- ============================================================================

local tracked_units = nil          -- the friendly units being watched; built on first contact
local units_by_ui_id = {}          -- unit id (as text) -> the unit object; the card-click lookup
local target_key_by_unit = {}      -- unit id -> the first of our keys that unit was found to own
local owned_keys_by_unit = {}      -- unit id (as text) -> EVERY one of our keys the scan found
                                   -- on it; the badge click's ownership test (SECTION 10)
local owned_abilities_by_unit = {} -- unit id (as text) -> the ABILITIES entries that unit OWNS,
                                   -- in ABILITIES order, variant-deduped (item 1.3). Computed
                                   -- once, when the scan fills the owned-key cache above; the
                                   -- poll's per-unit ability loop iterates this instead of the
                                   -- whole table. ABSENT (nil) = the owned keys are UNKNOWN ->
                                   -- the loop falls back to the full ABILITIES table, as today.
local identity_by_unit = {}        -- unit id (as text) -> the last-seen identity read of that unit
                                   -- (unit_identity -> battle_unit:type(), the land_units key).
                                   -- THE IDENTITY WATCH (item 3.4): the poll re-scans a unit
                                   -- carrying nothing of ours only when this value CHANGES -
                                   -- which is what catches a transformation or a mount mid-battle
local identity_checked = {}        -- unit id (as text) -> true once that unit has been identity
                                   -- checked at least once (item 5). Separate from the cache
                                   -- above: a unit whose very first identity read FAILED (nil)
                                   -- has no cached value but HAS been checked, so its first
                                   -- later GOOD read must re-scan rather than look like a
                                   -- first read. A nil read is never cached, so a transient
                                   -- failure can never erase the last good value.
local selected_unit_id = nil       -- the id (as text) of the one unit the single-choice tracker
                                   -- follows; with several units selected the badge click acts on
                                   -- selected_ui_ids below, this stays one of them
local selected_ui_ids = {}         -- EVERY id the engine reports as selected (the whole group,
                                   -- not just the tracker above). Maintained from the engine's
                                   -- own selection callback once it has delivered an event;
                                   -- until then - and whenever no callback event has ever
                                   -- arrived - the card read (SECTION 11) keeps it, as before.
                                   -- The badge click and the collective badge letter read this.

-- THE ENGINE SELECTION CALLBACK. The battle manager's own selection API
-- (battle_manager:register_unit_selection_callback - one registration per
-- unit) delivers every select/deselect event of a registered unit to its
-- callback as (unit, selected). The unit cards do NOT report a group/box
-- selection (they all read 'active'), so the callback is the only thing that
-- sees one; the card sweep stays as the fallback whenever the API is missing
-- or has never fired. The callback runs in the engine's event context and
-- only touches private state: it maintains the selected set and raises a
-- flag; the tracker and the badge letters follow at the next UI tick
-- (SECTION 11), so a ten-unit box selection costs one line of work, not ten.
local selection_callbacks_by_ui_id = {}    -- unit id -> true: a callback was accepted for it
local selection_callback_alive = false     -- true once the engine has DELIVERED an event
local selection_set_dirty = false          -- the set changed since the last convergence
local selection_set_sig = ""               -- the set at the last convergence ("1001,1002"; "" = empty)
local engine_selection_callback_errors = 0 -- swallowed callback errors: a raising callback would
                                           -- kill every callback of the battle, so the body is walled
local reconciled_card_ids = {}             -- id -> true while the id sits in the set only because
                                           -- the cards still report it (callback mode)
-- THE REASONED DIAL SCAN (item 1.1). The old rule re-walked the whole HUD
-- every second UI tick as long as ANY of our abilities was unclaimed - and
-- a selected unit that owns NONE of them (a Cathayan lord, a Tzeentch lord)
-- has no claim of ours to find, so the walk ran ~10x/s for the whole battle
-- and did nothing. These two flags carry the whole reason model: a selection
-- CHANGE (the dial belongs to whoever is selected) and a NEWLY TRACKED unit
-- (a re-list arrival) each ask for exactly ONE scan; they are booleans, so
-- however many events set them between two UI ticks, at most one scan runs.
local walk_on_selection_change = false    -- set by the selection paths; used by the UI tick
local walk_on_new_unit = false            -- set by the re-list; used by the UI tick
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
local armed = {}                   -- armed[unit id][marker] -> true when switched ON; ABSENT means OFF
local last_attempt_at = {}         -- armed attempt clock: last_attempt_at[unit id][marker] -> the tick of the last attempt (the guard)
-- THE COOLDOWN-HOLD TABLE: ui_id -> (marker -> record) for a pair the engine
-- has refused ON COOLDOWN. Each record carries the episode's start tick
-- (since - the hard bound is measured from it), the next tick the pair may be
-- probed (next_at), the count of consecutive refusals (streak) and whether the
-- episode has already spoken in the log (logged). Nested and miss-safe like
-- the tables above: a read never builds an inner table.
local cooldown_hold = {}
-- THE KNOWN-GONE SET (item 3.5): unit id (as text) -> true for a unit the
-- pre-fire validity read or an engine rejection proved is no longer there.
-- It makes the drop FINAL: the re-list consults it (SECTION 5), so a unit the
-- engine has not yet taken off its army list cannot be re-adopted and
-- re-attempted by the next 10 s refresh - the removal notice is honoured
-- once, not every re-list.
local gone_units = {}
local tick_count = 0               -- the mod's own battle clock: counts battlefield polls
local GUARD_TICKS = (GUARD_SECONDS * 1000) / POLL_MS   -- the guard expressed in poll ticks (2 s = 8 ticks)
local HOLD_TICKS = (HOLD_SECONDS * 1000) / POLL_MS     -- the repeat-refusal back-off (8 s = 32 ticks)
local MAX_HOLD_TICKS = (MAX_HOLD_SECONDS * 1000) / POLL_MS   -- the hard bound (20 s = 80 ticks)

-- The per-ability state, looked up by marker. One slot per ability holding:
-- the dial button we found (.button), the M/A badge component (.badge),
-- what the badge was last told to show (.last_letter - the cache), and
-- placement / visibility notes. Nothing per-unit lives in here.
local ability_state = {}
for _, ability in ipairs(ABILITIES) do
	ability_state[ability.marker] = {}
end

-- The deferred badge building. A claim during the dial scan only RECORDS
-- the button and raises pending_badge[marker]; the badge itself is built
-- later, on the UI tick, one guarded step at a time. badge_attempts counts
-- the tries since the last claim; badge_gave_up latches when the small
-- budget is spent - until the dial is rebuilt (a fresh claim resets both).
local pending_badge = {}    -- marker -> true while a claimed button waits for its badge
local badge_attempts = {}   -- marker -> badge-building attempts since its last claim
local badge_gave_up = {}    -- marker -> true after the attempt budget ran out, until the next claim

-- Which wheel slot each ability's button sits on. The claim walk measures
-- the button's 1-based position among the key-bearing children of its
-- parent bar and writes it here as the wheel-slot number (1..6); the badge
-- offset is derived from it (SECTION 9). Absent = not known yet, the bar
-- was unreadable, or more than six - the badge then uses its backup offset.
local slot_index = {}

-- ============================================================================
-- SECTION 2b - THE ACTIVE ABILITY SET (item 1.4)
-- ============================================================================
-- The UI tick's badge work was the only place the WHOLE ABILITIES table was
-- walked every 50 ms - free at three entries, per-tick waste at dozens. The
-- set below is the subset that can matter in THIS battle:
--
--   (a) every watched unit's OWNED markers - our keys filtered out of the
--       per-unit owned-key cache the scan already fills, so there is no new
--       engine read and no searching beyond the units we already watch;
--   (b) every marker CURRENTLY CLAIMED on the dial - its remembered button
--       still exists. This is the SUPERSET SAFETY: the dial belongs to
--       whoever is selected, so a claim can name an ability no watched unit
--       owns, and that badge must never be lost;
--   (c) nothing else.
--
-- It is recomputed ONLY when an input changes - the re-list, a scan, a
-- claim, a drop - never per tick, so the UI tick reads a ready list. Until
-- ANY information exists (the bootstrap: no watched unit has owned-keys data
-- yet) the set is nil and every reader falls back to the FULL ABILITIES
-- table, so the opening behaviour is unchanged. (The live copy writes one
-- line here when the membership changes; this reading copy is deliberately
-- silent.)
--
-- This is item 1.4's set; critique-2 item 1 then makes all_buttons_found()
-- test it instead of the whole table (falling back to the whole table while
-- it is unknown), so the UI walk stops completely when it is empty. The
-- poll's per-unit ability loop is deliberately untouched.
local active_abilities = nil          -- list of ABILITIES entries; nil = unknown -> use ABILITIES

-- The list the UI tick's badge paths iterate: the active set, or the whole
-- table while nothing is known yet.
local function active_abilities_list()
	return active_abilities or ABILITIES
end

-- Rebuild the set from the owned-key cache and the live claims. Cheap by
-- construction: it walks the watched units and their cached owned keys, and
-- never the engine.
local function refresh_active_abilities()
	local set = {}
	local known = false

	-- (a) every watched unit's owned markers, read out of the owned-key cache.
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
							-- instead of walking the abilities table and each
							-- entry's key list to find this key's marker.
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

	-- (c) bootstrap: no information at all -> the full table (unchanged
	-- opening behaviour).
	if not known then
		active_abilities = nil
		return
	end

	local list = {}
	for _, ability in ipairs(ABILITIES) do
		if set[ability.marker] then
			list[#list + 1] = ability
		end
	end
	active_abilities = list
end

-- ITEM 1.3 - THE PER-UNIT OWNED-ABILITY LIST. Turn a unit's cached owned DB
-- keys into the ABILITIES entries it can actually carry: each key maps through
-- the static marker_by_key table (built once, SECTION 1), the markers are
-- DEDUPED (a unit carrying BOTH engine variants of one marker - the main and
-- the DLC Foe-Seeker keys, say - yields that marker ONCE), and the list is
-- emitted in ABILITIES order, so the firing order - and with it every decision
-- - is exactly what the full-table walk produced. A unit carrying none of ours
-- yields an EMPTY list: the poll then evaluates nothing for it, rather than
-- the whole table.
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



-- The two arming tables above are nested: armed[unit id][marker]. The key is
-- the unit's own id AS A NUMBER - the engine reports it as a number, while the
-- click paths carry it as text (the card id IS that number). This little
-- mapping turns the text back into the number so both paths always land on the
-- SAME slot; a number (or a non-numeric id) passes through unchanged. It never
-- builds a string, so it costs no allocation.
local function unit_slot(ui_id)
	local n = tonumber(ui_id)
	if n ~= nil then return n end
	return ui_id
end

-- Is this unit's switch ON for this ability? ABSENT means OFF - a unit the
-- player has never switched on never fires anything. One entry per
-- (unit, ability) pair keeps two units carrying the same ability
-- completely independent. Reading an unarmed pair is just a lookup that
-- misses: it never creates the inner table, so nothing is allocated.
local function is_armed(unit, marker)
	if unit == nil then return false end
	local ok_id, raw_id = pcall(function() return unit:unique_ui_id() end)
	if not ok_id or raw_id == nil then return false end
	local ui_id = unit_slot(raw_id)
	local per = armed[ui_id]
	return per ~= nil and per[marker] == true
end

-- The unit behind the current selection, or nil while nothing is selected.
-- selected_unit_id follows the engine's own card state ('selected'); a
-- unit card's component id IS that unit's unique id, so this is a plain
-- table lookup - no searching of any kind.
local function selected_unit()
	if selected_unit_id == nil then return nil end
	return units_by_ui_id[tostring(selected_unit_id)]
end

-- Is this id in the selected set?
local function engine_selection_has(id)
	for i = 1, #selected_ui_ids do
		if selected_ui_ids[i] == id then return true end
	end
	return false
end

-- The callback body: add the id on a selection, remove it on a deselection,
-- raise the dirty flag when the set really moved. A unit we do not track is
-- ignored. No engine calls, no UI work - just the set; the tracker and the
-- badge letters follow at the next convergence (SECTION 11).
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

-- The registered callback: the body behind the error wall (a callback that
-- raises kills every callback registered for the battle, so it must not).
local function engine_selection_callback(unit, selected)
	local ok = pcall(engine_selection_body, unit, selected)
	if not ok then
		engine_selection_callback_errors = engine_selection_callback_errors + 1
	end
end


-- ============================================================================
-- SECTION 3 - FINDING THE ABILITY ON A UNIT
--   Two small readers: does this unit carry one of our abilities at all,
--   and will the engine let the unit use it right now (the readiness gate).
-- ============================================================================

-- Ask the engine which special abilities this unit carries and return the
-- first entry that matches our list (SECTION 1), together with EVERY one of
-- our keys found on it (the per-unit owned-key cache the badge click's
-- checkbox rule reads). nil as the first value = the unit carries none of
-- ours; the value is remembered per unit by the watch list.
local function scan_unit_abilities(unit)
	local owned = unit:owned_special_abilities()   -- the engine's list for this unit
	local matching_key = nil
	local owned_keys = {}                          -- every one of OUR keys this unit lists
	if owned == nil then
		return nil, owned_keys                     -- nothing listed (or unreadable)
	end
	for _, owned_key in pairs(owned) do   -- check each ability the unit lists ...
		-- ... against our key SET in a single read (item 3.1); the keys are
		-- unique, so an owned key was recorded exactly once before too.
		if ALL_ABILITY_KEYS_SET[owned_key] then
			matching_key = owned_key            -- an exact match against our list
			owned_keys[#owned_keys + 1] = owned_key
		end
	end
	return matching_key, owned_keys
end

-- THE CHEAP IDENTITY READ (item 3.4): ONE engine call - battle_unit:type(),
-- the unit's land_units key. It costs almost nothing and it is the value a
-- transformation or a mount moves, so it is what the poll watches instead of
-- re-running the full scan every 4 s. pcall-guarded and FAIL-OPEN: a missing
-- method, a raising read or a nil answer all come back as nil, and a nil
-- identity never reports a change (the 60 s fallback then carries the
-- re-scan). Used by the poll's re-check step only.
local function unit_identity(unit)
	local ok, value = pcall(function() return unit:type() end)
	if ok and value ~= nil then
		return tostring(value)
	end
	return nil
end

-- Does this remembered unit carry one of this ability's names? An exact
-- equality check against the per-unit owned-key cache above - no engine
-- read, no searching of any kind. Unknown units and units the scan has not
-- seen answer no.
local function unit_owns_marker(ui_id, marker)
	local ability = ability_for(marker)
	if ability == nil then return false end
	local owned = owned_keys_by_unit[tostring(ui_id)]
	if owned == nil then return false end
	for _, wanted_key in ipairs(ability.keys) do
		for _, owned_key in ipairs(owned) do
			if owned_key == wanted_key then return true end
		end
	end
	return false
end

-- WHY A SCAN WOULD EVER BE NEEDED (item 1.1). Two questions, both answered
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
	-- ITEM 11: read the selected unit's REMEMBERED owned markers (the list
	-- built from its owned names when it was scanned) instead of walking the
	-- whole ability table and asking about each entry. Every entry of that
	-- list is an ability the unit owns, so only the missing-claim question
	-- remains. A unit with no remembered owned-marker list owns nothing of
	-- ours we know of, so the gate stays closed.
	local list = owned_abilities_by_unit[tostring(selected_unit_id)]
	if list == nil then return false end
	for _, ability in ipairs(list) do
		if ability_state[ability.marker].button == nil then
			return true
		end
	end
	return false
end

-- THE COLLECTIVE SWITCH READ - what every badge letter should say. With ONE
-- selected unit this is exactly the old read: that unit's own switch. With
-- SEVERAL selected units it is the game's own "common ability" rule - on
-- only while EVERY selected unit that owns the ability has it switched on,
-- so the badge reads A while the whole group is armed and flips to M the
-- moment any member is off. A group where no selected unit owns the
-- ability reads off. Every badge write path calls this one function, so
-- they can never disagree about the letter.
local function collective_armed(marker)
	local n = #selected_ui_ids
	if n <= 1 then
		-- ONE selected unit: exactly the old read - that unit's own switch.
		return is_armed(selected_unit(), marker)
	end
	local owners = 0
	for i = 1, n do
		local id = selected_ui_ids[i]
		-- ITEM 10: membership is read from the remembered owned markers (the
		-- mapped, de-duplicated list the scan built) - a walk of a one-to-four
		-- element marker list, not a per-tick search of the ability's
		-- database-key names. A unit with no remembered owned-marker list owns
		-- nothing of ours we know of, so it is not one of this ability's owners.
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

-- THE READINESS GATE - ask the engine "can this unit use this ability right
-- now?" (can_perform_special_ability). The question is asked about the ONE
-- name the unit scan already found on this unit (SECTION 2): a database
-- variant the unit does not carry can only ever answer no, so asking
-- about every variant again at fire time told us nothing new. One query,
-- on the name the unit was found to own, is the whole question. The
-- remembered name is used only when it belongs to the ability being
-- fired (a unit can carry more than one of ours; asking the engine about
-- a DIFFERENT ability's name here could fire the wrong ability). When no
-- usable name is remembered - not scanned yet, or the remembered name is
-- another ability's - the original walk over this ability's names still
-- runs. There is deliberately no fall-through when the remembered name
-- answers no: that means the ability is running or on cooldown, and no
-- other variant changes that. Returns the name to fire, or nil when the
-- engine says no.
local function check_readiness(unit, ability, cached_key)
	local ready_key = nil

	-- Which remembered name may answer here: only one that belongs to
	-- this ability.
	local owned_key = nil
	if cached_key ~= nil then
		for _, wanted_key in ipairs(ability.keys) do
			if wanted_key == cached_key then owned_key = cached_key end
		end
	end

	if owned_key ~= nil then
		-- THE ONE QUERY: the name this unit was found to own.
		local ok_c, can = pcall(function()
			return unit:can_perform_special_ability(owned_key)   -- ask the engine
		end)
		if ok_c and can == true then
			ready_key = owned_key
		end
	else
		-- No usable name remembered yet: the original walk, so a unit
		-- the scan has not seen still fires exactly as before.
		for _, wanted_key in ipairs(ability.keys) do
			local ok_c, can = pcall(function()
				return unit:can_perform_special_ability(wanted_key)   -- ask the engine
			end)
			if ok_c and can == true and ready_key == nil then
				ready_key = wanted_key                                -- first "yes" wins
			end
		end
	end

	return ready_key
end


-- ============================================================================
-- SECTION 4 - IS THE UNIT CHARGING?
--   The mod's charge test (the numbers live in SECTION 1). It returns a
--   small tray of measurements; the entry named "charging" is the yes/no
--   verdict. If a measurement cannot be taken, the test that uses it stays
--   out of the way (treated as "not a reason to block"), so a missing
--   reading alone never blocks a genuine charge - only a MEASURED failure
--   does.
-- ============================================================================

local function measure_charge(unit)
	local m = {
		fast = unit:is_moving_fast(),   -- the engine says: the unit is running
		melee = unit:is_in_melee(),     -- the engine says: already fighting hand-to-hand
		has_target = false,             -- is an enemy currently targeted?
		target_dist = -1,               -- metres to that enemy; -1 = unknown
		ttc = -1,                       -- estimated seconds until contact; -1 = unknown
		charging = false,               -- the verdict
	}

	-- An enemy as the current target is the "this is an attack, not a
	-- move" signal: a plain move order sets no target.
	local ok_target, target = pcall(function() return unit:current_target() end)
	if ok_target and target ~= nil then
		m.has_target = true
	end

	-- Distance to the target, when there is one.
	if m.has_target then
		local ok_dist, dist = pcall(function() return unit:unit_distance(target) end)
		if ok_dist and dist ~= nil then
			m.target_dist = dist
		end

		-- Estimated seconds until impact = distance / the unit's fast
		-- speed, when both readings are available.
		if m.target_dist >= 0 then
			local ok_speed, speed = pcall(function() return unit:fast_speed() end)
			if ok_speed and speed ~= nil and speed > 0 then
				m.ttc = m.target_dist / speed
			end
		end
	end

	-- The verdict: running, NOT yet in melee, and an enemy targeted ...
	if m.fast and not m.melee and m.has_target then

		-- ... with a run-up long enough ...
		local enough_run_up = true
		if m.target_dist >= 0 then
			enough_run_up = (m.target_dist >= CHARGE_MIN_DISTANCE_M)
		end

		-- ... close enough that impact is imminent ...
		local close_enough = true
		if m.target_dist >= 0 then
			close_enough = (m.target_dist <= CHARGE_MAX_DISTANCE_M)
		end

		-- ... and impact within the allowed number of seconds.
		local soon_enough = true
		if m.ttc >= 0 then
			soon_enough = (m.ttc <= CHARGE_TIME_TO_CONTACT_S)
		end

		m.charging = enough_run_up and close_enough and soon_enough
	end

	return m
end


-- ============================================================================
-- SECTION 5 - BUILDING THE WATCH LIST
--   On the first battlefield poll, ask the game for the local player's
--   army as "script units". A script unit pairs the unit itself (.unit)
--   with a controller that can give it orders (.uc). The list is kept for
--   the whole battle: every unit's card lookup and every firing attempt
--   goes through it.
-- ============================================================================

-- THE ONE DROP ROUTINE (items 2 + 13). Defined here - ABOVE the watch-list
-- builder - because BOTH drop paths call it: the re-list below, and the poll's
-- dead-unit path in SECTION 7. The unit leaves tracked_units and EVERY
-- per-unit table is purged of its rows, so no stale row can be read for a unit
-- that is gone (the stuck-collective-letter class) and the per-unit caches
-- cannot grow without bound over a long battle. The id is put in gone_units,
-- which is deliberately KEPT (sticky), so the next 10 s re-list cannot re-adopt
-- a unit the engine has not yet taken off its army list - the removal notice is
-- honoured once, not every re-list. Called AFTER the poll's watching loop has
-- stopped walking the list, so the removal here can never disturb the iteration
-- it came from.
local function drop_unit_by_ui_id(ui_id)
	local id_text = tostring(ui_id)
	local id_slot = unit_slot(ui_id)
	gone_units[id_text] = true          -- STICKY (never purged): the re-list must not re-adopt
	if tracked_units ~= nil then
		for i = #tracked_units, 1, -1 do
			local script_unit = tracked_units[i]
			-- ITEMS 14 + 6 (one fix). Match on the id CACHED on the entry
			-- at registration (SECTION 5). The old test read the unit's own
			-- unique id (guarded) right here, so a dead unit whose read now
			-- FAILED matched nothing and its entry LINGERED on the watch
			-- list - with every per-unit row the purge below is meant to
			-- clear. The cached text needs no engine read, so the removal
			-- survives the dying engine's refusal. Fallback: an entry with
			-- no cached id yet still gets the old guarded engine read.
			local cached = script_unit and script_unit.zz_tracked_ui_id
			local same = false
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
				-- Purge the cached id WITH the entry, consistently with the
				-- per-unit purge below: the entry leaves the list and its
				-- cache leaves with it.
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

	-- THE SELECTED SET (item 2). A dead unit must not stay selected: a stale
	-- id in the set keeps collective_armed() computing the group's M/A letter
	-- from a unit that no longer exists, which pins the letter (the group
	-- reads M because the gone unit's is_armed() resolves false, even though
	-- every surviving selected owner is armed). Remove the id, hand the
	-- single-choice tracker to the first surviving selected id (or none), and
	-- let the EXISTING selection convergence plus the per-tick letter net
	-- re-derive the letter - no new timer.
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
	-- THE ADDITIVE RE-LIST. The old function wiped the watch list and made
	-- it anew; that is fine for its original single startup call, but the
	-- poll now re-runs it every RELIST_EVERY_N_POLLS polls (mid-battle
	-- arrivals: summons, Tzeentch splits, transformations), and a wipe
	-- would lose per-unit state. So the list is MERGED by identity (the
	-- unit's own id) instead: every unit already on it is left completely
	-- untouched; only units the list has never seen are appended, scanned
	-- and remembered - which also leaves the registration block at the
	-- bottom to register the engine selection callback for exactly the
	-- genuinely new units, once each; and a unit the engine no longer
	-- returns (died / left the field) is dropped, exactly what the old
	-- wholesale rebuild did with it.
	if tracked_units == nil then
		tracked_units = {}
	end

	local sunits = bm:get_scriptunits_for_local_players_army()   -- ask the game for the local player's army
	if sunits == nil then
		return              -- the army is not on the field yet; the next poll tries again
	end

	local total = sunits:count()   -- how many units does it contain?
	local fresh = {}               -- unit id (as text) -> true: the engine reported it this pass

	for i = 1, total do
		local script_unit = sunits:item(i)   -- one script unit: the unit + its order controller
		local unit = script_unit.unit
		local ui_id = unit:unique_ui_id()
		local id_text = tostring(ui_id)

		if fresh[id_text] == nil then
			fresh[id_text] = true

			-- Only a unit the list has never seen is added and scanned; an
			-- existing unit's remembered state is never touched here. A unit
			-- in gone_units (item 3.5) is NOT re-adopted: the pre-fire read or
			-- an engine rejection already proved it is gone, and the engine may
			-- still be listing it for a while.
			if units_by_ui_id[id_text] == nil and gone_units[id_text] == nil then
				tracked_units[#tracked_units + 1] = script_unit

				-- ITEMS 14 + 6 (one fix - the cached id). The unit's id is
				-- captured HERE, at registration, where it is already in
				-- hand, and stored ON the tracked entry. Every later use -
				-- the card sweep's wanted list and the drop routine's match
				-- - reads this cached text instead of asking the engine for
				-- the id again, so (a) the sweep's order no longer comes from
				-- pair order (no hash order; the sweep cap's subset is the
				-- same every call) and (b) a dead unit whose id read now
				-- FAILS can still be matched and removed. A unit is appended
				-- at most once (guarded above), so this cache is written
				-- exactly once per tracked entry.
				script_unit.zz_tracked_ui_id = id_text

				-- The card-click bridge: a unit card's component id is this
				-- unit's unique id, so a click on the card finds the unit
				-- right here.
				units_by_ui_id[id_text] = unit

				-- Record which of our keys (if any) this unit carries. A unit
				-- the ability cannot be seen on yet is quietly re-checked
				-- every few seconds by the poll (SECTION 7), in case it is
				-- attached a moment after deployment.
				local matching_key, owned_keys = scan_unit_abilities(unit)
				target_key_by_unit[ui_id] = matching_key
				owned_keys_by_unit[id_text] = owned_keys   -- the per-unit owned-key cache
				owned_abilities_by_unit[id_text] = owned_abilities_of(owned_keys)   -- item 1.3: the short list the poll walks
				walk_on_new_unit = true          -- a unit the list never saw: scan for its dial once
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
	local dropped_ids = {}
	for i = #tracked_units, 1, -1 do
		-- Items 14 + 6: the id comes from the tracked entry's cache, not a
		-- fresh engine read - a dead unit's id read can now fail, and this
		-- loop must still name it so the drop below can purge it. The
		-- guarded engine read is a fallback for an entry with no cached id
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
	end

	-- THE ENGINE SELECTION CALLBACKS: one registration per watched unit with
	-- the engine's own selection API, so a group / box selection reaches the
	-- mod per unit (the cards do not report one). All of it is guarded: the
	-- API may be missing or may not accept the unit - the card sweep then
	-- stays in charge, unchanged - and a registration that raises is caught
	-- (the callback itself is walled again, at every event). A unit already
	-- registered keeps its single registration across rebuilds, so a refresh
	-- registers for genuinely new units only, once each.
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
					end
				end
			end
		end
	end

	-- ITEM 1.4 - the re-list / drop just changed the inputs: refresh the
	-- active set (silent here; the live copy writes one line when it moves).
	refresh_active_abilities()
end


-- ============================================================================
-- SECTION 6 - FIRING THE ABILITY
--   The call sequence is copied from the game's own scripts: ability key
--   FIRST, target unit SECOND, and the target is required (for a
--   self-buffing ability the target is the unit itself). Every call here
--   is wrapped in pcall, so an engine refusal can never kill the battle's
--   timers.
-- ============================================================================

-- THE NON-EXISTENCE REFUSALS (item 3.5). The engine wraps a refused fire as
--   "calling 'perform_special_ability' on bad self (error: ...)". When the
--   unit it names is GONE the inner text says so in one of the forms below,
--   and those forms - exact substring only - are what mark such a refusal as
--   a REMOVAL NOTICE. The cooldown / active refusal this mod has always seen
--   is a DIFFERENT string ("does not support this special ability"): none of
--   the markers below occurs in it, so a live unit that is merely on cooldown
--   can never match and be dropped. (The battle log proves that string is a
--   hold, not a death: one unit produced it dozens of times and then ACCEPTED
--   a fire minutes later.)
local GONE_UNIT_ERRORS = {
	"does not exist",
	"no longer exists",
	"no such unit",
	"invalid unit",
	"unit is gone",
}

-- Does this text contain that substring? A plain slice scan over string.sub -
-- this reading copy carries no substring search call anywhere.
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

local function error_means_unit_gone(err_text)
	local text = tostring(err_text or "")
	for i = 1, #GONE_UNIT_ERRORS do
		if text_contains(text, GONE_UNIT_ERRORS[i]) then return true end
	end
	return false
end

-- THE PRE-FIRE VALIDITY READ (item 3.5). Two cheap, guarded engine reads
-- immediately before the fire call, closing the window between the poll's
-- alive check (which reads number_of_men_alive) and the call itself - a unit
-- that dies inside that window is why this exists.
--
-- THE RULE is deliberately two-signal and fail-open, because an identity read
-- alone is NOT a death test: an unreadable identity (battle_unit:type()
-- answering nothing) is a state this mod already supports - the identity
-- watch keeps such a unit, and the slow 60 s fallback still rescues it. So:
--   * if number_of_men_alive ANSWERS A NUMBER, that is the truth: > 0 alive,
--     <= 0 gone;
--   * only when it does NOT answer a number does the identity read decide,
--     and only a CLEAN nil (the unit answered nothing at all) counts as gone.
-- A READ THAT RAISES - either read - is a transient engine failure, exactly
-- what the guard catches, and is NEVER death. Two independent failures are
-- needed before a unit is called gone, so a single flaky read can never drop
-- a live unit. (unit_identity() is not reused on purpose: it folds a raising
-- read and a nil answer into the same nil, which would make a transient
-- failure look like death.)
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
-- SECTION 5b - MORALE, AND THE GROUND-TARGETED CAST (the fourth ability)
--   (a) THE MORALE THRESHOLD. There is no percentage / unary morale read
--   in the battle API. The only morale THRESHOLD the engine exposes to
--   script is battle_unit:is_wavering() - "Returns whether the morale of
--   the unit is currently wavering". Wavering is the first morale band
--   below steady, so it is the honest stand-in for "morale below a
--   threshold". (The API dump also carries morale_is_* @return names -
--   morale_is_lower_than_half_of_base_morale and friends - but they are
--   orphaned doc annotations with no callable function behind them.)
--   unit_is_wavering returns true (wavering - below the threshold), false
--   (a readable, healthy morale) or nil (the read could not be taken:
--   missing method, raising read or a nil answer). The trigger treats only
--   exact true as "below threshold" and falls back to plain in-melee on
--   nil, so an unreadable morale can never silently suppress the ability.
--
--   (b) THE GROUND-TARGETED CAST. The fourth ability carries two database
--   keys with DIFFERENT targeting. The base
--       wh_main_character_abilities_stand_your_ground
--   is self-centred (target_ground false) and fires through the proven
--   uc:perform_special_ability(key, unit). The DLC24
--       wh3_dlc24_character_abilities_tacticians_stand_your_ground
--   is friend- AND ground-targeted (target_friends true, target_ground
--   true), and for that one the engine offers a DIFFERENT call:
--   battle_unitcontroller:perform_special_ability_ground(ability_key,
--   position, orientation_in_degrees, width_in_m) - "on a specified
--   position". The position is a battle_vector, and battle_unit:position()
--   is one, so the ground point is the caster's own ground position (the
--   ability buffs itself and the friendly area around it). Vanilla passes
--   a unit to perform_special_ability at every one of its call sites and
--   never uses the _ground form, so the API documentation is the evidence
--   for the ground path.
--
--   FAIL-OPEN: if the position cannot be read, the cast is NOT made - the
--   mod never fires a targeted ability with a guessed target.
-- ============================================================================

-- ONE new top-level local only: the main chunk sits at Lua's 200-local
-- ceiling, so these three helpers are fields of the single table below (a
-- bare local function each would push the chunk over the limit). Call sites
-- read exactly as a function call would.
local FOURTH = {
	-- The keys whose engine call is the POSITION form.
	ground_keys = {
		["wh3_dlc24_character_abilities_tacticians_stand_your_ground"] = true,
	},
	-- ui id -> (marker -> true): one line per pair for a cast with no target.
	missing_logged = {},
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

-- The targeted-cast helper: read the caster's own ground position, then
-- issue the ground form of the call. Returns ok_call, err_call, no_target
-- - no_target true means nothing was fired because the position could not
-- be read (the caller must not fire).
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

local function attempt_activation(script_unit, unit, ability_key, target)
	-- PRE-FIRE VALIDITY (item 3.5): re-check the unit is still usable
	-- immediately before the call. A unit that is gone answers nothing, so it
	-- is dropped at once - the caller removes it from the watch list and the
	-- fire is never attempted.
	if unit_is_gone(unit) then
		return "gone"
	end

	-- THE PROVEN FRESH-HANDLE ROUTE (Accusation, this round): when the enemy
	-- trigger chose a target, use the CASTER script_unit re-fetched FRESH from
	-- the friendly enumerator THIS tick (never a controller held from an
	-- earlier poll). Falls back to the poll's own script_unit.
	local uc = script_unit.uc   -- the unit's order controller
	if FOURTH.eg_enemy ~= nil and FOURTH.eg_caster_su ~= nil and FOURTH.eg_caster_su.uc ~= nil then
		uc = FOURTH.eg_caster_su.uc
	end
	if uc == nil then
		return              -- no controller on this script unit; nothing can be ordered
	end

	-- Did WE actually take control on this attempt? Only a take that
	-- really succeeded may be handed back at the bottom; a failed take
	-- (or no take at all) must leave the control exactly where it was.
	local took_control = false

	if TAKE_CONTROL_FIRST then
		local ok_take = pcall(function() uc:take_control() end)
		took_control = ok_take
	end

	-- GLORIOUS DEATH RANGE RE-CHECK (this round): re-read the chosen ally's
	-- gap immediately before the cast; skip when it has drifted beyond the
	-- conservative 25 m trigger range. The
	-- owner-in-melee self arm leaves FOURTH.gd_ally nil - never gated.
	if FOURTH.gd_ally ~= nil and not FOURTH.gd_ally_in_range(unit, FOURTH.gd_ally) then
		FOURTH.gd_ally = nil
		return "held"
	end

	-- WILL OF THE VERMINKING RANGE RE-CHECK (this round): the same safety
	-- pattern as Glorious Death - re-read the chosen ally's gap immediately
	-- before the cast; skip when it has drifted beyond the conservative
	-- trigger range.
	if FOURTH.vm_ally ~= nil and not FOURTH.vm_ally_in_range(unit, FOURTH.vm_ally) then
		FOURTH.vm_ally = nil
		return "held"
	end


	-- ENCHANTED METALLURGY RANGE RE-CHECK (this round): the same safety pattern
	-- as Glorious Death / Will of the Verminking - re-read the chosen ally's gap
	-- immediately before the cast; skip when it has drifted beyond the
	-- conservative trigger range.
	if FOURTH.mtl_ally ~= nil and not FOURTH.mtl_ally_in_range(unit, FOURTH.mtl_ally) then
		FOURTH.mtl_ally = nil
		return "held"
	end

	-- WAVERING SELF-OR-ALLY RANGE RE-CHECK (blocks 7-9): re-read the chosen
	-- ally's gap immediately before the cast; skip when it has drifted beyond
	-- the conservative trigger range.
	if FOURTH.ws_ally ~= nil and not FOURTH.ws_ally_in_range(unit, FOURTH.ws_ally) then
		FOURTH.ws_ally = nil
		return "held"
	end

	-- WAVERING ALLY IN RANGE RE-CHECK (blocks 7-9): the same pattern for the
	-- Verminking-shape wavering-ally trigger.
	if FOURTH.wa_ally ~= nil and not FOURTH.wa_ally_in_range(unit, FOURTH.wa_ally) then
		FOURTH.wa_ally = nil
		return "held"
	end

	-- BLOOD SACRIFICE / EAT DA RUNTS ALLY RE-CHECK (this round): re-read the
	-- chosen ally's gap AND health immediately before the cast; skip when it has
	-- drifted out of range or healed above the 75% line. The Eat-da-Runts self
	-- arm leaves FOURTH.edr_ally nil - never gated.
	if FOURTH.bs_ally ~= nil and not FOURTH.bs_ally_valid(unit, FOURTH.bs_ally) then
		FOURTH.bs_ally = nil
		return "held"
	end
	if FOURTH.edr_ally ~= nil and not FOURTH.edr_ally_valid(unit, FOURTH.edr_ally) then
		FOURTH.edr_ally = nil
		return "held"
	end

	-- ACCUSATION ENEMY RE-CHECK (this round): re-read the chosen enemy's
	-- condition immediately before the cast - it must still be ALIVE and still
	-- IN MELEE or UNDER FIRE and still IN RANGE, or the cast is SKIPPED. The
	-- chosen enemy is the CAST TARGET - never the owner.
	if FOURTH.eg_enemy ~= nil then
		local enemy = FOURTH.eg_enemy
		local ok_alive, alive = pcall(function() return enemy:number_of_men_alive() end)
		local ok_melee, melee = pcall(function() return enemy:is_in_melee() end)
		local still_melee = (ok_melee and melee == true)
		local still_shot = false
		if not still_melee then
			still_shot = FOURTH.eg_under_missile_attack(enemy)
		end
		local alive_now = (ok_alive and type(alive) == "number" and alive > 0)
		local in_range_now = FOURTH.eg_enemy_in_range(unit, enemy)
		if not alive_now or not (still_melee or still_shot) or not in_range_now then
			FOURTH.eg_enemy = nil
			FOURTH.eg_arm = nil
			if RELEASE_CONTROL_AFTER and took_control then
				pcall(function() uc:release_control() end)
			end
			return "held"
		end
	end

	-- THE CALL. Ordinary keys (self- or unit-targeted) use the proven
	-- perform_special_ability(key, unit). A GROUND-TARGETED key uses the
	-- engine's own position form, perform_special_ability_ground(key,
	-- position, ...), with the caster's own ground position - the correct
	-- call for a database row whose target_ground flag is true. If the
	-- engine declines, the guarded call comes back with an error value and
	-- nothing else happens; the readiness gate decides the next attempt.
	local ok_call, err_call, no_target
	if FOURTH.is_ground_key(ability_key) then
		ok_call, err_call, no_target = FOURTH.ground_cast(uc, unit, ability_key)
	else
		ok_call, err_call = pcall(function()
			-- BLOCK 2: the ALLY-TARGETING call shape - an ability whose
			-- evaluator chose another friendly unit passes it here as the
			-- target; every self/unit-targeted ability passes nil and the
			-- unit is its own target, exactly as before (target or unit).
			uc:perform_special_ability(ability_key, target or unit)
		end)
	end

	-- FAIL-OPEN for a targeted cast: no readable position means NO fire -
	-- never a guessed target.
	if no_target then
		if RELEASE_CONTROL_AFTER and took_control then
			pcall(function() uc:release_control() end)
		end
		return "held"
	end

	-- AN ENGINE REJECTION THAT NAMES A NON-EXISTENT UNIT IS A REMOVAL NOTICE
	-- (item 3.5): the unit it names is gone, so report it and let the caller
	-- drop it. Only the non-existence text matches - the cooldown refusal is a
	-- different string, so a live unit on cooldown is never dropped.
	if not ok_call and error_means_unit_gone(tostring(err_call)) then
		return "gone"
	end

	-- Hand the unit back ONLY when the take above actually succeeded.
	-- Releasing control we never took does nothing useful, and the engine
	-- may read it as "drop the unit's current order". With the take OFF
	-- (the default), a release can therefore never happen at all.
	if RELEASE_CONTROL_AFTER and took_control then
		pcall(function() uc:release_control() end)
	end

	if ok_call then return "fired" end
	-- THE COOLDOWN REFUSAL is its own outcome: the caller arms/extends this
	-- pair's cooldown hold from it (a longer back-off, silent repeats) instead
	-- of the short guard.
	if text_contains(tostring(err_call), "does not support this special ability") then
		return "cooling"
	end
	return "held"
end


-- ============================================================================
-- SECTION 6b - IS THE UNIT ROUTING? One shared engine read, per unit, per poll
--   battle_unit:is_routing() is the read script can make: the vanilla scripts
--   use exactly this call (lib_battle_misc.lua's is_routing_or_dead runs it
--   on the unit; a script_unit reaches its unit through the .unit field -
--   the same handle this poll reads is_moving_fast() and is_in_melee() from).
--   A routing unit is fleeing the field, yet it can still look eligible to
--   several triggers (it keeps a target while it runs, it can sit in melee
--   geometry, and it still reports a fatigue state), so without this guard
--   an armed unit would spend active buffs while running away.
--
--   The rules, mirrored from the live file:
--     * one read per unit per poll - computed once below, reused by every
--       triggered ability;
--     * guarded (pcall), like every other engine read;
--     * FAIL-OPEN: only an exact true answer suppresses a trigger. A missing
--       method, a raising read or any other value counts as NOT routing, so
--       when the state cannot be read the mod behaves exactly as it did
--       before this condition existed.
-- ============================================================================

local function unit_is_routing(unit)
	local ok, routing = pcall(function() return unit:is_routing() end)
	if ok and routing == true then
		return true
	end
	return false
end


-- ============================================================================
-- SECTION 6c - THE FATIGUE READ (THIS ROUND): battle_unit:fatigue_state()
--   The API dump offers ONE direct fatigue read - fatigue_state() - which
--   answers the unit's state as a string: threshold_fresh, threshold_active,
--   threshold_winded, threshold_tired, threshold_very_tired or
--   threshold_exhausted. It is a plain engine value, NOT the wheel's
--   localised FatigueName - so no colour markup and no localised word is
--   parsed anywhere. The WHOLE value is compared, by equality, against the
--   known state strings (both the documented "threshold_" form and the bare
--   word are accepted) - no find, no substring, ever.
--
--   The reader returns the bare state word ("fresh".."exhausted") for the
--   caller's lookup, or nil when the read is UNREADABLE (the call raised,
--   answered no string, or named a state that is not one of the six).
--   An UNREADABLE fatigue FAILS CLOSED: the tired-or-worse trigger never
--   fires on it (the installed mod reports the first one once).
-- ============================================================================

-- THE LOCAL CEILING (why these live on FOURTH): the main chunk compiles
-- EXACTLY at Lua's 200-local limit, so this round adds NO new locals - the
-- reader and its two maps are FIELDS on the existing FOURTH helper bag
-- (the same table the shared morale read lives on).
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

function FOURTH.fatigue_state(unit)
	local ok, value = pcall(function() return unit:fatigue_state() end)
	if not ok or type(value) ~= "string" then
		return nil
	end
	return FOURTH.fatigue_states[value]
end


-- ============================================================================
-- SECTION 6d - THE TRIGGER EVALUATORS (critique-2 item 8: the dispatch)
--   The poll no longer compares trigger STRINGS in an if/elseif chain:
--   every ability entry is pointed at its own evaluator - one function
--   per trigger name, wired at load (the loop below) - and the poll
--   makes ONE call: ability.evaluate(unit, routing). Each evaluator
--   receives the unit and the already-read routing guard and answers
--   true (fire this ability) or false.
--   The five shipped abilities' evaluators are their old chain branches,
--   body for body - same engine reads, same guards - so their
--   behaviour is unchanged. evaluate_in_melee_self is the approved
--   batch rule ("when in melee (and not fleeing): cast on self") and
--   is exactly blood_lust's rule - blood_lust rides the same function,
--   so the rule cannot drift between the five and the batch.
--   THE LOCAL CEILING: the main chunk compiles at Lua's 200-local
--   limit, so the evaluators are FIELDS of the existing FOURTH helper
--   bag and the entry wiring is a load-time loop - no new locals.
-- ============================================================================

function FOURTH.evaluate_charge(unit, routing)
	local m = measure_charge(unit)
	if FIRE_ON_CHARGE and m.charging and not routing then
		return true
	elseif FIRE_ON_MELEE and m.melee and not routing then
		return true
	end
	return false
end

function FOURTH.evaluate_tired(unit, routing)
	local fatigue = FOURTH.fatigue_state(unit)
	if fatigue ~= nil and FOURTH.fatigue_fire[fatigue] and not routing then
		return true
	end
	return false
end

function FOURTH.evaluate_melee(unit, routing)
	if unit:is_in_melee() and not routing then
		return true
	end
	return false
end

function FOURTH.evaluate_melee_low_morale(unit, routing)
	if unit:is_in_melee() and not routing then
		local wavering = FOURTH.wavering(unit)
		if wavering ~= false then
			return true
		end
	end
	return false
end

function FOURTH.evaluate_in_melee_self(unit, routing)
	if unit:is_in_melee() and not routing then
		local wavering = FOURTH.wavering(unit)
		if wavering ~= true then
			return true
		end
	end
	return false
end

-- BLOCK 2 - THE FOUR NEW-TRIGGER EVALUATORS (this round). Each answers
-- FIRE / DON'T FIRE; in the LIVE build each carries its OWN distinct reason
-- text so the field log tells the triggers apart (the reading copy keeps no
-- text). The FIFTH new trigger - the summoned Foe-Seeker - needs no
-- evaluator: its key rides the existing foe_seeker entry and the shared
-- evaluate_tired above. THE LOCAL CEILING: these are FIELDS of the same
-- FOURTH helper bag (the chunk compiles at Lua's 200-local limit); their
-- per-unit state (cast_target, plus the Slayer key list below) rides the
-- same bag too.
FOURTH.cast_target = nil

-- GLORIOUS DEATH's chosen ally (this round): the CLOSEST in-melee Slayer
-- ally within GLORIOUS_DEATH_RANGE_M, kept only so the cast can RE-CHECK
-- the gap immediately before firing. The owner-in-melee self arm leaves it
-- nil, so that cast is never gated.
FOURTH.gd_ally = nil

-- GLORIOUS DEATH's distance helper (this round): the gap in metres from
-- the OWNER to a candidate Slayer ally (the charge detector's own
-- battle_unit:unit_distance primitive). nil when the read cannot be taken.
function FOURTH.gd_ally_gap(unit, ally)
	local ok, gap = pcall(function() return ally:unit_distance(unit) end)
	if ok and type(gap) == "number" then return gap end
	return nil
end

-- true when the gap is within the conservative 25 m trigger range; an
-- UNREADABLE gap (nil) is treated as IN range (fail-open).
function FOURTH.gd_ally_in_range(unit, ally)
	local gap = FOURTH.gd_ally_gap(unit, ally)
	return (gap == nil) or (gap <= GLORIOUS_DEATH_RANGE_M)
end

-- EAGLE-FEATHER TORC: fire when the barrier is BROKEN - barrier HP at 0 with
-- a NONZERO maximum, both read live. A unit with no barrier (max 0) or an
-- intact one stays silent; an unreadable value stays silent too.
function FOURTH.evaluate_barrier_broken(unit, routing)
	if not routing then
		local hp = FOURTH.context_value(unit, "BarrierHp")
		local max = FOURTH.context_value(unit, "BarrierMaxHp")
		if type(hp) == "number" and type(max) == "number" and max > 0 and hp <= 0 then
			return true
		end
	end
	return false
end

-- FANGSPIKE: the charge window OR in melee - the SAME charge detector the
-- onslaught trigger uses (its flags and reads). The arms cannot co-fire: the
-- charge arm is tested first and wins.
function FOURTH.evaluate_charge_or_melee(unit, routing)
	if FOURTH.evaluate_charge(unit, routing) then
		return true
	end
	return false
end

-- GHOUL KING OF USHORAN: fire when the unit's OWN health is at or below 75%,
-- read live. NO HYSTERESIS (removed this round - a second health threshold
-- could disarm the trigger for good under sustained damage). Repeat attempts
-- are held back by the readiness gate, the engine cooldown and the
-- rejection-informed back-off only.
function FOURTH.evaluate_ushoran_health(unit, routing)
	if not routing then
		local hp = FOURTH.context_value(unit, "HealthPercent")
		if type(hp) == "number" and hp <= 75 then
			return true
		end
	end
	return false
end

-- THE SLAYER TYPE-KEY LIST (this round). battle_unit:type() answers the
-- unit's land_units key; the list below was DERIVED FROM THE GAME'S OWN
-- DATA - the game dump's land_units localisation table
-- (%LOCALAPPDATA%\Temp\wh3\land_units.loc.tsv, its
-- land_units_onscreen_name_<key> rows): every land_units key whose own key
-- contains "slayer" or "doomseeker", copied verbatim. Membership is EXACT
-- WHOLE-KEY equality - one table read, no string search of any kind - so a
-- near-miss key (the Bretonnian ROR "Beastslayers of Bastonne", whose key
-- carries no "slayer") is correctly not a Slayer. A Slayer whose key does
-- not spell it (Gotrek) is a deliberate under-approximation - such a unit is
-- simply not offered to the engine by this trigger.
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

-- true only for a genuine Slayer unit (the engine's type() key is in the
-- list above; a missing/non-string read is not a Slayer).
function FOURTH.is_slayer(unit)
	local ok, t = pcall(function() return unit:type() end)
	if not ok or type(t) ~= "string" then return false end
	return FOURTH.slayer_keys[t] == true
end

-- GLORIOUS DEATH: the ability whose trigger does NOT require the OWNER to be
-- in melee. THE TRIGGER stays SLAYER-ONLY (a unit is a Slayer exactly when
-- its land_units type key is in FOURTH.slayer_keys):
-- (a) an in-melee SLAYER ally (other than self) arms it; else (b) the OWNER
-- itself arms it ONLY when it is a Slayer AND in melee; else silent. A
-- NON-Slayer ally is NEVER offered. THE CAST TARGET IS ALWAYS THE OWNER
-- ITSELF. THE RANGE GATE (this round): the ally arm only counts while the
-- owner is within the conservative trigger range GLORIOUS_DEATH_RANGE_M
-- (25 m, deliberately tighter than the ability's 55 m wiki aura) of
-- the ally; the CLOSEST in-range in-melee Slayer is chosen; the gap is
-- re-checked immediately before the cast and the cast is SKIPPED if the ally
-- has drifted out of range. The owner-in-melee self arm is NEVER gated.
function FOURTH.evaluate_glorious_death(unit, routing)
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
			FOURTH.cast_target = unit
			FOURTH.gd_ally = best_ally
			return true
		end
		if FOURTH.is_slayer(unit) and unit:is_in_melee() then
			FOURTH.cast_target = unit
			return true
		end
	end
	return false
end


-- ============================================================================
-- BLOCK 4/5/6 - THE TWO NEW-TRIGGER EVALUATORS (this round). Each carries its
-- OWN distinct situation. THE LOCAL CEILING: their per-unit state (vm_ally,
-- plus the named trigger-range constant below) rides the FOURTH helper bag -
-- the chunk compiles at Lua's 200-local limit, so NO new chunk-level locals.
-- ============================================================================

-- WILL OF THE VERMINKING'S TRIGGER RANGE (this round) - DELIBERATELY
-- CONSERVATIVE, stored on the FOURTH bag (no new chunk local). The ability's
-- GAME DATA gives a 35 m ally aura (unit_spec_abil.tsv: effect_range =
-- 35.0000, ai_usage = augment_melee); following the FIELD-PROVEN conservative
-- pattern used for Glorious Death (25 m vs its 55 m wiki aura) the trigger
-- radius here is a deliberately conservative 25 m - 10 m INSIDE the 35 m
-- aura. The ally arm fires only while the OWNER is within
-- FOURTH.VERMINKING_RANGE_M of the wavering ally. ONE place to tune.
FOURTH.VERMINKING_RANGE_M = 25

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
			FOURTH.vm_ally = best_ally
			return true
		end
	end
	return false
end

-- POTION OF TOUGHNESS: a ONE-TIME activation treated as a HEAL - fire when the
-- OWNER is in melee AND its own health is at or below 75%. Reuses the SAME
-- live health read (HealthPercent via FOURTH.context_value) and the SAME plain
-- hysteresis-free threshold style as Ghoul King of Ushoran; NO second
-- threshold. Repeat attempts are held back by the readiness gate, the engine
-- cooldown and the rejection-informed back-off only.
function FOURTH.evaluate_potion_health(unit, routing)
	if unit:is_in_melee() and not routing then
		local hp = FOURTH.context_value(unit, "HealthPercent")
		if type(hp) == "number" and hp <= 75 then
			return true
		end
	end
	return false
end


-- ============================================================================
-- ENCHANTED METALLURGY (this round) - ONE new trigger for the whole family.
-- The user's new trigger: "when self or ally in range is in melee; when ally
-- in range is shooting". The MELEE half ships; the SHOOTING half COULD NOT be
-- built, and NO proxy is used. THE API RESEARCH: battle_unit.lua (the game
-- dump) has NO per-unit "is firing / is shooting" read - is_under_missile_
-- attack is the unit RECEIVING fire (wrong direction), current_target /
-- ammo_left / missile_range prove nothing about firing NOW, and the engine's
-- flags.tsv vocabulary (is_missile_unit, is_under_missile_fire, ...) is a
-- DATA-TABLE construct, not a Lua read. No proven predicate -> no shooting arm.
-- THE LOCAL CEILING: the per-unit state (mtl_ally) and the named range
-- constant ride the FOURTH helper bag - NO new chunk-level locals.
-- ============================================================================

-- ENCHANTED METALLURGY'S TRIGGER RANGE (this round) - DELIBERATELY
-- CONSERVATIVE, stored on the FOURTH bag (no new chunk local). The ability's
-- GAME DATA gives a 35 m ally aura (unit_spec_abil.tsv: effect_range =
-- 35.0000 for all four keys, ai_usage = augment_melee); following the
-- FIELD-PROVEN conservative pattern used for Glorious Death and Will of the
-- Verminking (25 m against a larger aura) the trigger radius here is a
-- deliberately conservative 25 m - 10 m INSIDE the 35 m aura. ONE place to tune.
FOURTH.METALLURGY_RANGE_M = 25

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
-- trigger range of the owner; CAST ON SELF (the cast target is the OWNER, the
-- DEFAULT target or unit, so no cast_target write is needed). THE SAME SAFETY
-- PATTERN AS GLORIOUS DEATH / VERMINKING: for the ALLY arm the CLOSEST
-- qualifying in-melee ally is chosen, the gap is RE-CHECKED immediately before
-- the cast and the cast is SKIPPED on drift. The owner-in-melee self arm
-- leaves FOURTH.mtl_ally nil - never gated.
function FOURTH.evaluate_metallurgy_melee(unit, routing)
	if not routing then
		if unit:is_in_melee() then
			return true
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
			FOURTH.mtl_ally = best_ally
			return true
		end
	end
	return false
end


-- ============================================================================
-- BLOCKS 7-9 (this round) - FIVE new trigger types (and the redesigned pair).
-- Every evaluator is a field of the FOURTH helper bag and every new piece of
-- state / constant rides the bag too (NO new chunk-level locals - the chunk is
-- at Lua's 200-local ceiling). The reading copy answers true / false.
-- ============================================================================

-- CHARGE ONLY (Ferocious Battle Howl): the charge window WITHOUT the melee arm.
function FOURTH.evaluate_charge_only(unit, routing)
	local m = measure_charge(unit)
	if FIRE_ON_CHARGE and m.charging and not routing then
		return true
	end
	return false
end

-- WAVERING SELF (Ferocious Fury of Ulric / Helm of Yvresse / Vial of Troll
-- Blood): the OWNER itself is wavering (while not routing); only an EXACT true
-- morale answer fires (fail-closed).
function FOURTH.evaluate_wavering_self(unit, routing)
	if not routing and FOURTH.wavering(unit) == true then
		return true
	end
	return false
end

-- WAVERING SELF-OR-ALLY (Fury of Ulric / redesigned Commanding Presence): the
-- OWNER is wavering, OR a friendly in-melee wavering ally is within the
-- conservative trigger range; cast on self. THE TRIGGER RANGE is DELIBERATELY
-- CONSERVATIVE against the game-data 35 m aura (unit_spec_abil.tsv effect_range
-- 35.0000). Same safety pattern as Glorious Death / Verminking / Metallurgy:
-- closest ally, pre-cast gap re-check, skip on drift.
FOURTH.WAVERING_RANGE_M = 25

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
	if not routing then
		if FOURTH.wavering(unit) == true then
			return true
		end
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
			FOURTH.ws_ally = best_ally
			return true
		end
	end
	return false
end

-- CHARGE OR WAVERING (Bangers & Smash): the charge window OR wavering.
function FOURTH.evaluate_charge_or_wavering(unit, routing)
	if not routing then
		local m = measure_charge(unit)
		if FIRE_ON_CHARGE and m.charging then
			return true
		end
		if FOURTH.wavering(unit) == true then
			return true
		end
	end
	return false
end

-- WAVERING ALLY IN RANGE ("Stay Here, I'll Get Help!"): a friendly WAVERING
-- ally within the conservative range; cast on self. The owner need not be
-- wavering and the ally need not be in melee - the Verminking shape with the
-- ally-melee requirement removed (see the tracker note). Same safety pattern.
FOURTH.wa_ally = nil

function FOURTH.wa_ally_gap(unit, ally)
	local ok, gap = pcall(function() return ally:unit_distance(unit) end)
	if ok and type(gap) == "number" then return gap end
	return nil
end

function FOURTH.wa_ally_in_range(unit, ally)
	local gap = FOURTH.wa_ally_gap(unit, ally)
	return (gap == nil) or (gap <= FOURTH.WAVERING_RANGE_M)
end

function FOURTH.evaluate_wavering_ally_range(unit, routing)
	if not routing then
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
			FOURTH.wa_ally = best_ally
			return true
		end
	end
	return false
end

-- The trigger -> evaluator map and the load-time wiring of every entry
-- (keyed by the trigger name the abilities table in SECTION 1 carries).

-- ============================================================================
-- THE FINAL ROSTER ROUND (this round) - TWO new ALLY-HEAL evaluators for the
--   two built individuals that need a new trigger: BLOOD SACRIFICE (cast on
--   the LOWEST-health ally in range at or below 75%) and EAT DA RUNTS! (cast
--   on self at or below 75%, ELSE on the lowest-health ally in range at or
--   below 75%). Each answers FIRE / DON'T FIRE; the LIVE build carries its own
--   distinct reason text (the reading copy keeps no text). The chosen ally
--   rides FOURTH.cast_target + a per-trigger slot so the cast can re-check the
--   gap and the ally's health before firing (the Glorious-Death safety shape).
--   THE TRIGGER RANGE is a DELIBERATELY CONSERVATIVE 25 m named constant (the
--   game data gives these single-ally heals no aura radius, effect_range
--   0.0000, with target_intercept_range 100.0000 m). NO new chunk-level locals.
-- ============================================================================
FOURTH.BLOOD_SACRIFICE_RANGE_M = 25
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
function FOURTH.bs_ally_valid(unit, ally)
	if ally == nil then return false end
	if not FOURTH.bs_ally_in_range(unit, ally) then return false end
	local hp = FOURTH.context_value(ally, "HealthPercent")
	return (type(hp) ~= "number") or (hp <= 75)
end
function FOURTH.evaluate_blood_sacrifice(unit, routing)
	if not routing then
		local self_id = tostring(unit:unique_ui_id())
		local best_ally = nil
		local best_gap = nil
		local best_hp = nil
		for i = 1, #tracked_units do
			local other = tracked_units[i] and tracked_units[i].unit
			if other ~= nil and other ~= unit and other:number_of_men_alive() > 0 then
				if tostring(other:unique_ui_id()) ~= self_id and not unit_is_routing(other) then
					local hp = FOURTH.context_value(other, "HealthPercent")
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
			FOURTH.cast_target = best_ally
			FOURTH.bs_ally = best_ally
			return true
		end
	end
	return false
end
FOURTH.EAT_DA_RUNTS_RANGE_M = 25
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
function FOURTH.edr_ally_valid(unit, ally)
	if ally == nil then return true end
	if not FOURTH.edr_ally_in_range(unit, ally) then return false end
	local hp = FOURTH.context_value(ally, "HealthPercent")
	return (type(hp) ~= "number") or (hp <= 75)
end
function FOURTH.evaluate_eat_da_runts(unit, routing)
	if not routing then
		local hp = FOURTH.context_value(unit, "HealthPercent")
		if type(hp) == "number" and hp <= 75 then
			return true
		end
		local self_id = tostring(unit:unique_ui_id())
		local best_ally = nil
		local best_gap = nil
		local best_hp = nil
		for i = 1, #tracked_units do
			local other = tracked_units[i] and tracked_units[i].unit
			if other ~= nil and other ~= unit and other:number_of_men_alive() > 0 then
				if tostring(other:unique_ui_id()) ~= self_id and not unit_is_routing(other) then
					local ahp = FOURTH.context_value(other, "HealthPercent")
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
			FOURTH.cast_target = best_ally
			FOURTH.edr_ally = best_ally
			return true
		end
	end
	return false
end


-- ============================================================================
-- ACCUSATION (this round) - the FIRST ENEMY-TARGETED trigger, and the first
-- ability whose cast target is an ENEMY unit.
--   THE RULE: fire when an ENEMY unit in range is in melee OR under missile
--   fire - per poll, for a unit that owns an enemy-targeted key: enumerate the
--   enemy script units; keep those that are valid and alive AND inside the
--   ability's own reach; of those pick one that is IN MELEE or UNDER MISSILE
--   FIRE (prefer in-melee; among equals the closest). If none qualifies, do
--   nothing. The chosen enemy becomes the CAST TARGET - NEVER the owner.
--   THE PROVEN ROUTE (round-4 probe, log-confirmed): the target is re-fetched
--   FRESH from the enemy enumerator on the SAME tick and the caster's
--   controller is re-read fresh (SECTION 6a's FOURTH.eg_fresh_caster_su) - the
--   bench_fresh shape `caster_su.uc:perform_special_ability(key, enemy_su.unit)`
--   that LANDED in the probe. A controller held from an earlier poll no-ops.
--   THE RANGE SOURCE: Accusation's own target_intercept_range (unit_spec_abil
--   .tsv = 75.0000 m), stored as the named FOURTH.ACCUSATION_RANGE_M.
--   THE SAFETY PATTERN: the chosen enemy rides FOURTH.eg_enemy; the condition
--   (alive + still in melee/under fire + still in range) is RE-CHECKED
--   immediately before the cast and the cast is SKIPPED if it lapsed. The HOLD
--   is the existing per-pair guard + cooldown hold.
--   is_under_missile_attack() is not proven on an enemy - an unreadable read is
--   treated as FALSE (fail-safe). Every helper/constant/slot rides the FOURTH
--   bag - NO new chunk-level locals.
-- ============================================================================

-- ACCUSATION'S TRIGGER RANGE - the ability's own target_intercept_range (75 m).
FOURTH.ACCUSATION_RANGE_M = 75

-- the chosen ENEMY unit, its arm and the fresh CASTER script_unit - cleared
-- before every evaluate so no ability can inherit a stale enemy.
FOURTH.eg_enemy = nil
FOURTH.eg_arm = nil
FOURTH.eg_caster_su = nil

-- the gap in metres from the OWNER to a candidate enemy.
function FOURTH.eg_enemy_gap(unit, enemy)
	local ok, gap = pcall(function() return unit:unit_distance(enemy) end)
	if ok and type(gap) == "number" then return gap end
	return nil
end

-- true while the enemy is inside the ability's own reach: unit_in_range first,
-- a readable distance next, caster-in-melee last. A wholly unreadable reach is
-- treated as OUT of range (fail-safe).
function FOURTH.eg_enemy_in_range(unit, enemy)
	local okr, inr = pcall(function() return unit:unit_in_range(enemy) end)
	if okr and inr == true then return true end
	if okr and inr == false then return false end
	local gap = FOURTH.eg_enemy_gap(unit, enemy)
	if gap ~= nil then return gap <= FOURTH.ACCUSATION_RANGE_M end
	local okm, m = pcall(function() return unit:is_in_melee() end)
	return (okm and m == true)
end

-- true / false / nil - the enemy's validity (is_valid_target() is the probed
-- read; is_valid() is the documented one). An unreadable validity is nil.
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

-- true when the enemy is currently TAKING missile fire. An unreadable read is
-- treated as FALSE (fail-safe) - is_under_missile_attack() was never proven on
-- an enemy.
function FOURTH.eg_under_missile_attack(enemy)
	local ok, v = pcall(function() return enemy:is_under_missile_attack() end)
	if ok and v == true then return true end
	return false
end

-- re-fetch the CASTER's script_unit FRESH from the friendly enumerator THIS
-- tick (never a controller held from an earlier poll). nil when not found.
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

-- THE EVALUATOR: fire when an ENEMY unit in range is in melee OR under missile
-- fire; the chosen enemy is the CAST TARGET (never the owner). true = fire.
function FOURTH.evaluate_enemy_engaged_or_shot(unit, routing)
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
							elseif FOURTH.eg_under_missile_attack(enemy) then
								arm = "missile"
							end
							if arm ~= nil
								and ok_alive and type(alive) == "number" and alive > 0
								and (valid == nil or valid == true)
								and FOURTH.eg_enemy_in_range(unit, enemy) then
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
					FOURTH.eg_enemy = best_enemy
					FOURTH.eg_arm = best_arm
					FOURTH.eg_caster_su = FOURTH.eg_fresh_caster_su(unit)
					FOURTH.cast_target = best_enemy
					return true
				end
			end
		end
	end
	return false
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
}
for _, ability in ipairs(ABILITIES) do
	ability.evaluate = FOURTH.evaluators[ability.trigger]
	ability.tip = FOURTH.TRIGGER_TIP[ability.trigger]
end


-- ============================================================================
-- SECTION 7 - THE BATTLEFIELD POLL
--   Runs every POLL_MS milliseconds for the whole battle (registered at
--   the bottom of the file). One tick: advance the clock, then for every
--   watched unit and every ability check the conditions - this unit's pair
--   is armed, the unit is not routing (SECTION 6b), and the ability's own
--   trigger situation is met - then
--   the readiness gate, then the short guard, then fire. This loop is the
--   mod's automatic behaviour; everything else is controls and display.
-- ============================================================================

-- THE ONE DROP ROUTINE (drop_unit_by_ui_id) lives in SECTION 5, above the
-- watch-list builder, because BOTH drop paths call it - the re-list's own drop
-- there, and the poll's dead-unit path just below. It purges the unit's rows
-- from every per-unit table and settles the selected set (items 2 + 13); its
-- full note sits with its definition.

local function poll_body()
	tick_count = tick_count + 1     -- one step of the mod's own battle clock

	-- Nothing to do during deployment or after the battle is decided.
	if not bm:is_conflict_phase() then return end

	-- First poll after contact: build the list of friendly units.
	if tracked_units == nil then
		rebuild_unit_list()
		return
	end

	-- THE PERIODIC RE-LIST (SECTION 5): mid-battle arrivals - summons,
	-- splits, transformations - must be watched, scanned and armable like
	-- any starting unit, so the watch list is re-listed every
	-- RELIST_EVERY_N_POLLS polls (40 x 250 ms = 10 s). rebuild_unit_list is
	-- additive: existing units are untouched, only genuinely new ones are
	-- added (and units the engine no longer returns are dropped). No return
	-- here - the freshly listed units are processed on this very tick.
	if (tick_count % RELIST_EVERY_N_POLLS) == 0 then
		rebuild_unit_list()
	end

	local do_redetect = (tick_count % REDETECT_EVERY_N_POLLS) == 0   -- is this a 4-secondly re-check tick?
	local do_fallback_rescan = (tick_count % FALLBACK_RESCAN_EVERY_N_POLLS) == 0  -- or the slow 60 s one?

	-- EVERY unit a fire proves gone THIS TICK is collected here and dropped
	-- AFTER the loop (never mid-iteration): hitting a death must not cost the
	-- rest of the army its tick, and several deaths in one tick all drop.
	local gone_ids = {}

	-- ITEM 12 - THE DEFERRED ACTIVE-SET REFRESH. The per-unit re-scan block
	-- below (the identity-moved rescan and the 60 s fallback rescan both run
	-- through it) used to rebuild the active set DIRECTLY, so a tick that
	-- re-scanned N units rebuilt it N times - each a pass over units x owned
	-- markers. They now only RAISE this flag; ONE rebuild after the loop -
	-- and after the post-loop drop walk, so it observes the FINAL state -
	-- runs exactly ONCE per tick. Membership is unchanged: by the time the
	-- deferred rebuild reads, exactly the same inputs the old last in-loop
	-- rebuild saw are in place.
	local active_refresh_pending = false

	for i = 1, #tracked_units do
		local script_unit = tracked_units[i]
		local unit = script_unit and script_unit.unit

		-- Only look at units still alive on the field.
		if unit ~= nil and unit:number_of_men_alive() > 0 then
			-- The routing read: ONE engine call per unit per poll (SECTION
			-- 6b), shared by every ability below.
			local routing = unit_is_routing(unit)
			local ui_id = unit:unique_ui_id()

			-- Nothing of ours on this unit yet. THE IDENTITY WATCH (item
			-- 3.4): at the 4 s cadence the cheap identity read runs
			-- INSTEAD of a full scan - unit_identity (SECTION 3), one
			-- pcall'd battle_unit:type() - and the unit is re-scanned
			-- when that value CHANGES (a transformation or a mount
			-- moves the land_units key, so a loadout that gained
			-- abilities mid-battle is picked up and its new abilities
			-- arm and fire). ITEM 5: a nil read is NEVER cached, and the
			-- unit's very first check merely records - so a failed FIRST
			-- check (nothing cached) is re-scanned as soon as a later
			-- check reads a good value, which is exactly the poisoned-
			-- first-check case that used to go unseen for up to 60 s. A
			-- unit that has never been checked is not re-scanned on its
			-- first good read: the unit was already scanned when it
			-- entered the watch list. THE SLOW SAFETY FALLBACK: one
			-- full scan every 60 s whatever the identity says, so an
			-- unreadable or unchanging identity degrades to the old
			-- behaviour, just far rarer. (There is no log line here: the
			-- reading copy carries none - the live build writes ONE line
			-- for a re-scan that discovers something, and is silent
			-- otherwise.)
			if target_key_by_unit[ui_id] == nil and (do_redetect or do_fallback_rescan) then
				local id_text = tostring(ui_id)
				local old_identity = identity_by_unit[id_text]
				local new_identity = unit_identity(unit)
				-- ITEM 5: never cache a nil read. A transient failure must not
				-- erase the last good value, or the next good read would
				-- compare against nil and never look like a change. The
				-- per-unit checked flag says the unit has been identity
				-- checked at least once regardless of outcome, so a failed
				-- first check can still be turned into a re-scan by the next
				-- good read.
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
				-- re-scans.
				local identity_moved = (not first_identity_check
					and new_identity ~= nil
					and (old_identity == nil or new_identity ~= old_identity))
				local rescan = identity_moved or do_fallback_rescan

				if rescan then
					local found, owned_keys = scan_unit_abilities(unit)
					owned_keys_by_unit[id_text] = owned_keys   -- refresh the owned-key cache
					-- item 1.3: the learned keys change this unit's owned-ability
					-- list, so rebuild it too...
					owned_abilities_by_unit[id_text] = owned_abilities_of(owned_keys)
					-- ...and tell item 1.4: the owned keys were just learned, so
					-- the active set (the UI tick's badge paths) must see them at
					-- once. ITEM 12: only RAISE the flag - the ONE rebuild for
					-- this tick runs after the loop, so N re-scans cost ONE
					-- rebuild instead of N.
					active_refresh_pending = true
					if found ~= nil then
						target_key_by_unit[ui_id] = found      -- the newly-revealed ability is cached
					end
				end
			end

			-- One pass per ability: its own per-UNIT switch, its own
			-- trigger, then the readiness gate and the short guard.
			-- ITEM 1.3: iterate only the markers THIS unit OWNS - the list the
			-- scan cached (owned_abilities_by_unit, SECTION 2), mapped from the
			-- owned DB keys and variant-deduped, so a unit carrying one of
			-- three abilities costs ONE evaluation instead of three. A unit
			-- whose owned-key cache is UNKNOWN (nil - never scanned) falls back
			-- to the FULL table, exactly as before: no unit is ever skipped.
			local unit_abilities = owned_abilities_by_unit[tostring(ui_id)]
			if unit_abilities == nil then
				unit_abilities = ABILITIES
			end
			for _, ability in ipairs(unit_abilities) do

				-- THE PER-UNIT SWITCH: this (unit, ability) pair must be
				-- armed. Nothing fires for a unit the player has not
				-- switched on - two units carrying the same ability are
				-- completely independent.
				if is_armed(unit, ability.marker) then
					-- ITEM 8: per-entry dispatch - each entry's own evaluate
					-- function decides (SECTION 6d); the field is wired at load
					-- from its trigger name. No chain remains. BLOCK 2: the
					-- ally-target slot is CLEARED before every evaluate; an
					-- ally-targeting evaluator fills it, and the cast passes it.
					FOURTH.cast_target = nil
					FOURTH.gd_ally = nil
					FOURTH.vm_ally = nil
					FOURTH.mtl_ally = nil
					FOURTH.ws_ally = nil
					FOURTH.wa_ally = nil
					FOURTH.bs_ally = nil
					FOURTH.edr_ally = nil
					FOURTH.eg_enemy = nil
					FOURTH.eg_caster_su = nil
					local want_fire = ability.evaluate(unit, routing)

					if want_fire then
						-- THE READINESS GATE: the engine's own "can this
						-- unit use this ability now?" check. One query,
						-- on the name this unit was found to own; the
						-- name list is walked only when none is
						-- remembered (SECTION 3).
						local ready_key = check_readiness(unit, ability, target_key_by_unit[ui_id])

						if ready_key ~= nil then
							-- THE SHORT SAFETY BRAKE, alongside the
							-- readiness gate: at most one attempt per
							-- (unit, ability) inside GUARD_SECONDS.
							-- THE COOLDOWN-HOLD GATE: a pair the engine already
							-- refused ON COOLDOWN is governed by its own record
							-- - the next_at back-off plus the hard bound -
							-- instead of the raw guard.
							local bucket = cooldown_hold[ui_id]   -- this unit's own cooldown holds
							local hold = (bucket ~= nil and bucket[ability.marker]) or nil

							local eligible
							if hold ~= nil then
								-- THE HARD BOUND: a hold may never outlive
								-- MAX_HOLD_SECONDS. When it fires the bound
								-- re-bases, so a stuck or unreadable signal
								-- still gets probed.
								if (tick_count - hold.since) >= MAX_HOLD_TICKS then
									hold.since = tick_count
									hold.next_at = 0
								end
								eligible = (tick_count >= hold.next_at)
							else
								local guard = last_attempt_at[ui_id]   -- this unit's own attempt clock
								local last_attempt = (guard ~= nil and guard[ability.marker]) or -999999   -- -999999 means "never tried yet"
								eligible = (tick_count - last_attempt) >= GUARD_TICKS
							end

							if eligible then
								local guard = last_attempt_at[ui_id]
								if guard == nil then
									guard = {}                     -- built only when an attempt is actually stamped
									last_attempt_at[ui_id] = guard
								end
								guard[ability.marker] = tick_count   -- stamp the attempt
								-- "gone" means the pre-fire check or an engine
								-- rejection proved this unit is no longer there:
								-- collect its id and leave THIS unit's ability
								-- walk; every collected id is dropped after the
								-- unit loop. "cooling" is the engine's cooldown
								-- refusal.
								local outcome = attempt_activation(script_unit, unit, ready_key, FOURTH.cast_target)
								if outcome == "gone" then
									gone_ids[#gone_ids + 1] = ui_id
									break
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
										-- the first refusal keeps the short guard
										rec.next_at = tick_count + GUARD_TICKS
									else
										rec.next_at = tick_count + HOLD_TICKS
									end
									rec.logged = true
								elseif outcome == "fired" then
									-- a real fire ends the cooldown episode
									local b = cooldown_hold[ui_id]
									if b ~= nil then
										b[ability.marker] = nil
									end
								end
							end
						end
					end
				end
			end
		end
	end
	-- DROP EVERY COLLECTED id via the ONE drop routine (SECTION 5). Done here,
	-- AFTER the unit loop: the tracked list is never mutated mid-iteration (the
	-- routine's own scan + table.remove run freely now) and a death never costs
	-- the rest of the army its tick.
	for g = 1, #gone_ids do
		drop_unit_by_ui_id(gone_ids[g])
	end

	-- ITEM 12 - THE ONE (DEFERRED) ACTIVE-SET REBUILD of this tick. It runs
	-- here, AFTER the unit loop AND after the drop walk, so it observes the
	-- FINAL state - any owned-key learning done in the loop AND any unit the
	-- walk just dropped. A tick that re-scanned nothing raises nothing and
	-- rebuilds nothing (exactly as before); a tick that re-scanned N units
	-- rebuilds the set ONCE instead of N times.
	if active_refresh_pending then
		refresh_active_abilities()
	end
end

-- The poll body runs inside pcall. An error escaping a timer callback is
-- not merely a skipped tick: the battle model's timer driver stops
-- re-arming every repeating callback, so one bad tick would kill the
-- watching for the rest of the battle. The wrapper bleeds off the error.
local function poll()
	pcall(poll_body)
end

-- The name this poll registers under; used once, at registration
-- (SECTION 12).
local POLL_NAME = "zz_test_deadly_onslaught_poll"


-- ============================================================================
-- SECTION 8 - THE DIAL SCAN: finding and claiming the ability buttons
--   The game does not hand the mod a reference to the ability buttons, so
--   the mod walks the on-screen HUD tree and asks every component the one
--   question the game documents for identifying an ability button:
--   InterfaceFunction("AbilityKeyForScript") - "which ability key do you
--   show?". A button whose key EQUALS one of ours (SECTION 1) is CLAIMED:
--   the mod records the button reference and raises the flag that asks for
--   its badge.
--
--   THE SAFETY RULES this walk follows (each was paid for in testing):
--     * The engine sometimes hands back a value that looks like text but
--       kills the game when certain text operations touch it. So every
--       engine key is first COPIED into a fresh plain-text value
--       (as_plain_string below) and every check runs on the copy only.
--     * Matching is EXACT EQUALITY against the SECTION 1 table - never a
--       partial match. (The engine's four-argument search call that a
--       partial match would need is what crashed earlier sessions; no
--       search call of any kind runs anywhere in this file.)
--     * Every engine call here is wrapped, and the walk is bounded in
--       depth and in components visited, so no single hostile component
--       can kill the scan.
--     * A claim touches NOTHING on the engine side - it only records.
--       All the writing (badge building) happens later, on the UI tick,
--       in guarded steps (SECTION 9).
-- ============================================================================

-- How many components this scan has visited so far (reset per scan; the
-- walk gives up after a generous bound - see scan_component).
local walk_visits = 0

-- MAKE A FRESH PLAIN COPY OF AN ENGINE VALUE. The copy is made by joining
-- the value with an empty piece of text (Lua's ".." join - the one
-- operation such values provably survive), with tostring() as the
-- fallback; both attempts are guarded. Returns nil when neither works.
-- Everything downstream uses the copy, never the engine's original value.
local function as_plain_string(v)
	if v == nil then return nil end

	-- Fallback copy: the guarded standard text conversion.
	local text = nil
	local ok2, t2 = pcall(tostring, v)
	if ok2 and type(t2) == "string" then
		text = t2
	end

	-- Preferred copy: the fresh join. If it worked, use it.
	local ok_copy, copied = pcall(function() return v .. "" end)
	if ok_copy and type(copied) == "string" then
		return copied
	end
	return text
end

-- A SAFE LENGTH READ: how many characters does this value have? The read
-- runs on the fresh copy (above) and is guarded; the language's own "#"
-- is the fallback. Returns nil when the value cannot be measured at all -
-- the callers treat nil as "not a real key" and move on.
local function safe_len(s)
	local plain = as_plain_string(s)      -- measure the COPY, never the engine's original value
	if plain == nil then return nil end   -- could not make a copy: unreadable

	local n = nil
	local ok4, n4 = pcall(string.len, plain)   -- first try: the standard length read
	if ok4 and type(n4) == "number" then
		n = n4
	end
	if n ~= nil then return n end

	local ok5, n5 = pcall(function() return #plain end)   -- fallback: the language's "#" length
	if ok5 and type(n5) == "number" then
		n = n5
	end
	return n
end

-- IS THIS DIAL BUTTON SHOWING THIS ABILITY? The judgement is the button's
-- key ALONE (never the button's id or name - on a real ability button
-- those can be unhelpful or fail outright). The fresh copy of the key is
-- lowercased (guarded) and then compared, character for character,
-- against every key listed for this ability in SECTION 1. Only an EXACT
-- match claims; a key that merely CONTAINS the name does not - the list
-- in the table is the single source of truth. If the lowercasing failed,
-- the un-lowered copy is compared instead, so a misbehaving helper cannot
-- lose the button.
local function key_is_ours(ability, key)
	if ability == nil then return false end
	local plain = as_plain_string(key)   -- always work on a fresh copy
	if plain == nil then return false end

	local lowered = nil
	local ok6, l6 = pcall(string.lower, plain)   -- lowercase the copy (guarded)
	if ok6 then
		lowered = l6
	end

	local candidate = lowered or plain   -- if lowercasing failed, compare the un-lowered copy
	for _, listed_key in ipairs(ability.keys) do   -- compare against every key this ability lists
		if candidate == listed_key then
			return true
		end
	end
	return false
end

-- IS THIS ABILITY CLAIMED ON THE CURRENT DIAL RIGHT NOW? True when the
-- claimed button reference still exists AND its key still reads as ours -
-- the same test the scan claimed it with. One test in one place, so the
-- UI tick's show/hide judgement and the badge-click guard can never
-- disagree about whether a badge is live.
local function marker_claimed_now(ability)
	if ability == nil then return false end
	local state = ability_state[ability.marker]
	if state == nil or state.button == nil then return false end

	local ok_k, key = pcall(function() return state.button:InterfaceFunction("AbilityKeyForScript") end)   -- read its current key (guarded)
	if ok_k and (safe_len(key) or 0) > 3 and key_is_ours(ability, key) then
		return true
	end
	return false
end

-- THE ACTIVE-DIAL TEST (critique-2 item 1). True once every ability that can
-- matter in THIS battle has its dial button; the scan can then stop. The test
-- now runs over the ACTIVE set - item 1.4's active_abilities_list(): every
-- marker a watched unit OWNS or that is CURRENTLY CLAIMED - instead of the
-- whole ability table. In a battle where nothing of ours can be on the dial
-- (the selected unit a Cathayan or Tzeentch lord carrying none of our markers,
-- and nothing claimed) the active set is EMPTY, and an empty set counts as
-- VACUOUSLY complete: the UI tick's walk gate closes completely rather than
-- running the 5 s safety net for the whole fight. The opening (bootstrap) case
-- is unchanged: while nothing is known yet, active_abilities_list() falls back
-- to the full ability table, so the walk is exactly as it always was.
--
-- SELF-CORRECTING - stopping loses nothing: a scan, the re-list, the identity
-- watch or the 60 s fallback can reveal a NEWLY OWNED marker without any walk;
-- the active-set rebuild then adds it, this test returns false again (its
-- button is not claimed yet) and walking resumes. A selection change raises
-- walk_on_selection_change, so the next tick walks too.
local function all_buttons_found()
	for _, ability in ipairs(active_abilities_list()) do
		local state = ability_state[ability.marker]
		if state == nil or state.button == nil then return false end
	end
	return true
end

-- THE CLAIMED BUTTON'S WHEEL SLOT. The claimed button lives in a hidden
-- button bar, and its on-screen position is a bar coordinate, NOT a wheel
-- slot (reading that position is what placed badges off-screen in an
-- earlier build). What DOES map to the wheel is the button's 1-based
-- position among the KEY-BEARING children of its parent bar - two
-- measured battles showed the bar's key-bearing buttons sit in wheel
-- order. This function counts that position; "key-bearing" is the same
-- safe-length gate the scan uses. Every read is guarded, so no hostile
-- sibling can kill the walk; a component whose reads fail simply does not
-- count. "Ours" is found by IDENTITY first (the component's own address,
-- a stable per-component pointer) and by exact key equality second, so a
-- twin of our key earlier on the bar cannot steal our position. Returns
-- k >= 1, or nil when the parent or the children cannot be read.
local function bar_ordinal_for(uic, ability)
	if uic == nil or ability == nil then return nil end

	local ok_p, parent = pcall(function() return uic:Parent() end)   -- the button's parent is the hidden bar
	if not ok_p or parent == nil then return nil end
	local ok_w, container = pcall(function() return UIComponent(parent) end)
	if not ok_w or container == nil then return nil end

	local ok_n, n = pcall(function() return container:ChildCount() end)   -- how many children does the bar have?
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
					seen = seen + 1                       -- one more key-bearing sibling counted

					local is_ours = false
					if my_addr ~= nil then                    -- identity test first: same address?
						local ok_a, addr = pcall(function() return cc:Address() end)
						if ok_a and addr ~= nil and tostring(addr) == my_addr then
							is_ours = true
						end
					end
					if not is_ours and key_is_ours(ability, key) then
						is_ours = true                        -- otherwise: exact key equality
					end

					if is_ours then return seen end           -- our button: its position is "seen"
				end
			end
		end
	end
	return nil
end

-- ONE COMPONENT'S WORTH OF SCAN WORK. Runs inside its own guarded call
-- (scan_component below), so no single component - however hostile its
-- answers - can kill the walk. It asks for the component's ability key;
-- when the key is long enough to be real and EQUALS one of ours for an
-- ability not yet claimed, the claim is RECORDED: the button reference,
-- the pending-badge flag, and the measured wheel slot.
local function scan_component_body(uic)
	local ok_key, key = pcall(function() return uic:InterfaceFunction("AbilityKeyForScript") end)

	-- The gate is the COPY's length (safe_len works on the copy), never a
	-- type test on the engine's value: a value the engine dressed up as
	-- anything at all still gets its chance.
	if not (ok_key and (safe_len(key) or 0) > 3) then return end

	-- One claim per ability; the judgement is the key alone (no id check,
	-- no liveness gate).
	for _, ability in ipairs(ABILITIES) do
		local state = ability_state[ability.marker]
		if state.button == nil and key_is_ours(ability, key) then
			-- RECORD ONLY - nothing is created or written to the engine
			-- from inside this walk; the UI tick builds the badge from
			-- the flag, step by step (SECTION 9).
			state.button = uic
			pending_badge[ability.marker] = true
			badge_attempts[ability.marker] = 0
			badge_gave_up[ability.marker] = nil

			-- The wheel slot this button sits on, for its badge offset.
			local k = bar_ordinal_for(uic, ability)
			if k ~= nil and k >= 1 and k <= 6 then
				slot_index[ability.marker] = k   -- remember the slot number
			else
				slot_index[ability.marker] = nil -- no usable slot: use the backup offset
			end
		end
	end
end

-- WALK THE HUD TREE - bounded and hazard-proof. Bounds: depth 6, at most
-- 4000 components visited, and stop early once every ability is claimed.
-- Each component's own work runs inside a guarded call, and each child
-- read is guarded too, so nothing a component does can abort the scan.
local function scan_component(uic, depth)
	if uic == nil or depth > 6 or walk_visits > 4000 or all_buttons_found() then return end
	walk_visits = walk_visits + 1   -- count this visit against the walk's budget

	pcall(scan_component_body, uic)   -- examine this component (guarded)

	local ok_n, n = pcall(function() return uic:ChildCount() end)
	if ok_n and type(n) == "number" then
		-- Walk this component's children, one by one ...
		for i = 0, n - 1 do
			local ok_c, child = pcall(function() return uic:Find(i) end)
			if ok_c and child ~= nil then
				-- ... each recursion guarded, so a broken child cannot kill the walk.
				pcall(function()
					scan_component(UIComponent(child), depth + 1)
				end)
			end
		end
	end
end

-- ONE FULL SCAN: start at the top of the battle HUD ("hud_battle") and
-- walk for the ability buttons. Called from the phase callbacks, and
-- repeatedly from the UI tick until every ability is claimed. Everything
-- is wrapped; a failed scan simply means the next attempt tries again.
local function find_ability_buttons()
	if all_buttons_found() then return end

	walk_visits = 0

	pcall(function()
		local hud = UIComponent(core:get_ui_root():Find("hud_battle"))
		if hud == nil then
			return          -- the HUD is not on screen yet (early phases); keep trying
		end
		scan_component(hud, 0)
	end)

	-- ITEM 1.4 - the scan just ran: a claim (or a fresh owned-key read) may
	-- have changed the inputs, so refresh the active set (silent unless moved).
	refresh_active_abilities()
end


-- ============================================================================
-- SECTION 9 - THE BADGES AND THE M/A LETTER
--   WHAT A BADGE IS: the small letter the mod draws next to one ability's
--   place on the ability wheel - the mod's only control. "M" = this
--   ability is MANUAL for the selected unit (the player fires it); "A" =
--   AUTOMATIC (the mod may fire it). A click on the badge flips the
--   switch(es) of the selected group (SECTION 10); with ONE unit selected
--   the letter shows that unit's own state, with several it reads A only
--   while every selected unit that owns the ability is armed.
--
--   WHERE IT GOES: the visible ability wheel is a circle of six slots; the
--   six positions below were measured over two battles. Which slot an
--   ability occupies equals the ability's position in the hidden button
--   bar (measured by the claim, SECTION 8). The badge is docked to the
--   bottom-centre of the HUD with a hand-tuned base offset for the TOP
--   slot; every other slot adds that slot's measured delta from the top
--   slot. Only when the bar position is unknown does the ability's backup
--   offset (SECTION 1) get used instead.
--
--   WHEN IT IS BUILT: never inside the scan walk. A claim only records the
--   button; the badge is built on the UI tick, one guarded step at a time,
--   so a step that fails discards the half-built badge and the next tick
--   retries (a small number of tries per claim, then it waits until the
--   dial is rebuilt). The steps below are the settled call order.
-- ============================================================================

-- The HUD component the badges are drawn on. Found on the first creation:
-- the walk climbs from the claimed button until it reaches the
-- "hud_battle" screen, and the badge is created there (a plain container
-- that safely draws components we create; writing to the ability button
-- itself is what crashed earlier builds).
local badge_parent = nil

-- The hand-tuned base position for the TOP-slot badge (Deadly Onslaught's
-- measured slot). MINUS is left/up, PLUS is right/down, measured from the
-- bottom-centre dock point; the two numbers were tuned by hand in game.
local BADGE_X, BADGE_Y = -865, -209

-- The measured six wheel-slot positions, in slot order; slot 1 (the top)
-- is the slot the base pair above was tuned for, so its delta is zero and
-- the base pair is used as-is for it.
local WHEEL_TOP_X, WHEEL_TOP_Y = 96, 845
local WHEEL_SLOT = {
	{ 96, 845 },      -- 1 - top (the hand-tuned reference slot)
	{ 166, 875 },     -- 2 - 45 degrees
	{ 194, 947 },     -- 3 - right
	{ 162, 1017 },    -- 4 - -45 degrees
	{ 28, 877 },      -- 5 - 135 degrees
	{ 2, 949 },       -- 6 - left
}

-- How many UI ticks in a row to try building a badge before giving up on
-- that claim. A fresh claim resets the count.
local MAX_BADGE_ATTEMPTS = 3

-- Work out where this ability's badge goes: its wheel slot's delta from
-- the top slot, applied to the hand-tuned base pair; or the ability's own
-- backup offset (SECTION 1) when no slot number is known (never claimed,
-- unreadable bar, or more than six key-bearing children).
-- Returns: x offset, y offset.
local function badge_offsets_for(marker)
	local ability = ability_for(marker)
	if ability == nil then return nil end
	local k = slot_index[marker]
	if k ~= nil and k >= 1 and k <= 6 then
		local slot = WHEEL_SLOT[k]
		if slot ~= nil then
			-- Slot known: the hand-tuned base pair moved by this slot's delta.
			return BADGE_X + (slot[1] - WHEEL_TOP_X), BADGE_Y + (slot[2] - WHEEL_TOP_Y)
		end
	end
	-- No usable slot number: this ability's own backup offset.
	return BADGE_X + ability.ox, BADGE_Y + ability.oy
end

-- Run ONE group of engine calls for the badge safely: if anything in the
-- group raises an error, this comes back "false" (instead of killing the
-- battle) and the caller discards the half-made badge.
local function badge_step(fn)
	return pcall(fn)
end

-- THE LAYOUT NUDGE: after a real letter write, ask the engine to re-run
-- its layout/repaint pass for the badge AND for the HUD container it
-- lives on. Layout() is the only repaint-adjacent call the game offers
-- scripts, so it is the one lever against the delay between a letter
-- write and its pixels. Both calls are guarded: a repaint failure must
-- never abort a write.
local function nudge_badge_layout(state)
	pcall(function() state.badge:Layout() end)
	if badge_parent ~= nil then
		pcall(function() badge_parent:Layout() end)
	end
end

-- THE ONE LETTER WRITE: every path that changes a badge's letter goes
-- through here - the letter is written AND the repaint is asked for, as
-- one action, so no caller can write a letter without nudging it. The
-- letter that was last successfully written is remembered
-- (state.last_letter), so callers can stay quiet when the letter is
-- already correct; a write that FAILED does not move the memory, so the
-- next path writes again. Returns true when the write landed.
local function write_badge_letter(state, letter)
	local ok_text = pcall(function() state.badge:SetText(letter) end)
	if ok_text then state.last_letter = letter end
	nudge_badge_layout(state)
	return ok_text
end

-- DISCARD A CREATED BADGE. Letting go of the Lua reference does NOT remove
-- a component that was already created - it stays attached to the HUD
-- forever (a state where creation keeps failing would leak one per tick).
-- So every place that abandons a created-but-unfinished badge destroys the
-- engine-side component first: the Destroy call only happens when the
-- reference is live and the component supports it, it runs inside a pcall
-- so an engine-side refusal is swallowed, never raised into the retry path
-- (the live copy logs the refusal), and the reference is cleared either
-- way. A placed, working badge is never discarded - only the failed-creation
-- sites and the retry cleanup call this.
local function discard_badge(state)
	if state == nil or state.badge == nil then return end
	local ok_has, has_destroy = pcall(function() return state.badge.Destroy ~= nil end)
	if ok_has and has_destroy then
		pcall(function() state.badge:Destroy() end)
	end
	state.badge = nil
end

-- BUILD ONE BADGE, STEP BY STEP. Each step runs only when the previous
-- one completed; any failure clears the half-built badge (state.badge =
-- nil) and returns false - the retry policy lives in the UI tick.
local function create_badge(marker)
	local state = ability_state[marker]
	local ability = ability_for(marker)
	if state == nil or ability == nil or state.button == nil or state.badge ~= nil then return false end

	-- STEP 1 - create. Climb from the claimed button until the
	-- "hud_battle" screen is found (bounded to 8 levels), and create the
	-- badge there from this ability's layout template. The climb result
	-- is remembered as the parent for the later steps.
	if not badge_step(function()
		local node = state.button
		-- Climb one level at a time until the battle HUD is reached.
		for _ = 1, 8 do
			local ok_id, id = pcall(function() return node:Id() end)
			if ok_id and tostring(id) == "hud_battle" then break end    -- reached the battle HUD: stop here
			local ok_p, parent = pcall(function() return node:Parent() end)
			if not ok_p or parent == nil then break end
			local ok_w, wrapped = pcall(function() return UIComponent(parent) end)
			if not ok_w or wrapped == nil then break end
			node = wrapped
		end
		badge_parent = node
		-- Create the badge HERE (on the HUD), never on the ability button itself.
		state.badge = UIComponent(badge_parent:CreateComponent(ability.badge,
			"ui/templates/zz_auto_badge"))
		if state.badge == nil then error("CreateComponent returned nothing", 0) end
	end) then
		state.badge = nil
		return false
	end

	-- STEP 2 - dock the fresh component to the top-left of its parent
	-- (dock point 0; the final dock position is set in STEP 6).
	if not badge_step(function()
		state.badge:SetDockingPoint(0)
	end) then
		discard_badge(state)
		return false
	end

	-- STEP 3 - resize: room for the letter.
	if not badge_step(function()
		state.badge:Resize(24, 24)
	end) then
		discard_badge(state)
		return false
	end

	-- STEP 4 - blank the template's own title-bar art on every slot that
	-- has any (slots 0-4), so only the letter carries the look.
	if not badge_step(function()
		for i = 0, 4 do
			state.badge:SetImagePath("ui/zz_auto/blank.png", i)
		end
	end) then
		discard_badge(state)
		return false
	end

	-- STEP 5 - write the first letter: the collective switch read says what
	-- it should be (ONE selected unit: that unit's own switch, exactly as
	-- before; SEVERAL: A only while every selected owner is on). The write
	-- goes through THE ONE LETTER WRITE, exactly like every later write. A
	-- write that raises fails this whole step, so the badge is discarded
	-- and retried next tick.
	if not badge_step(function()
		local letter = collective_armed(marker) and "A" or "M"
		local ok_text = write_badge_letter(state, letter)
		if not ok_text then error("SetText raised - discarding the badge", 0) end
	end) then
		discard_badge(state)
		return false
	end

	-- STEP 6 - place it: HIDDEN AT BIRTH first (so a discarded badge can
	-- never linger on screen), then dock point 8 (bottom-centre of the
	-- parent) and this ability's own offset. The placement is remembered,
	-- so later re-positions can stay quiet when nothing moved.
	if not badge_step(function()
		local ox, oy = badge_offsets_for(marker)
		state.badge_shown = false                    -- born hidden ...
		state.badge:SetVisible(false)                -- ... so a discarded badge never shows
		state.badge:SetDockingPoint(8)               -- 8 = bottom-centre of the HUD
		state.badge:SetDockOffset(ox, oy)            -- the computed offset
		badge_parent:Layout()                        -- ask for a repaint
		state.placed = true                          -- remember this placement
		state.applied_ox, state.applied_oy = ox, oy
	end) then
		discard_badge(state)
		return false
	end

	return true
end


-- (Re)place an EXISTING badge: dock point 8 (bottom-centre of its parent)
-- plus this ability's own offset. Runs on the UI tick and does nothing
-- when the badge already sits at that offset (a fresh claim can bring a
-- new slot, which moves it). Every engine call is guarded.
local function place_badge(marker)
	local state = ability_state[marker]
	local ability = ability_for(marker)
	if state == nil or state.badge == nil or ability == nil then return end

	local ox, oy = badge_offsets_for(marker)

	-- Quiet when the badge is already placed at this exact offset.
	if state.placed and state.applied_ox == ox and state.applied_oy == oy then return end

	pcall(function() state.badge:SetDockingPoint(8) end)   -- 8 = bottom-centre
	pcall(function() state.badge:SetDockOffset(ox, oy) end)
	pcall(function() badge_parent:Layout() end)
	state.placed = true
	state.applied_ox, state.applied_oy = ox, oy
end

-- Set a badge's letter from a plain true/false switch value, through the
-- same write primitive and the same cache: when the letter already reads
-- correctly, nothing happens at all. This function does NOT touch the
-- badge's visibility - visibility belongs to the UI tick alone.
local function badge_visible(marker, on)
	local state = ability_state[marker]
	if state == nil or state.badge == nil then return end

	local letter = on and "A" or "M"
	if state.last_letter == letter then return end
	write_badge_letter(state, letter)
end

-- THE PER-TICK SAFETY NET for one badge's letter: re-derive what the
-- letter SHOULD be (the collective switch read - ONE selected unit: its
-- own switch, exactly as before; SEVERAL: A only while every selected
-- owner is on) and write it only when it differs from what the badge was
-- last told to show. So any change converges on screen within one UI tick,
-- and a steady letter stays completely silent (no repeated writes).
-- Returns true when a write happened.
local function refresh_badge_letter(marker)
	local state = ability_state[marker]
	if state == nil or state.badge == nil then return false end

	local on = collective_armed(marker)
	local letter = on and "A" or "M"
	if state.last_letter == letter then
		return false
	end
	write_badge_letter(state, letter)
	return true
end

-- THE SELECTION CHANGED: refresh every badge's letter from the new
-- selection in this same call, so the letters never lag the selection.
local function refresh_badge_letters_for_selection()
	for _, ability in ipairs(active_abilities_list()) do
		refresh_badge_letter(ability.marker)
	end
end

-- The look of a flipped switch: the badge's letter. (The ability itself
-- is never touched - it can always still be fired by hand.)
local function set_armed_look(marker, on)
	badge_visible(marker, on)
end

-- Re-sync one badge's letter with the collective switch read, skipping
-- entirely when nothing has changed since the last sync (the remembered
-- .feedback_on value).
local function apply_ability_feedback(marker)
	local state = ability_state[marker]
	if state == nil or state.button == nil then return end

	local on = collective_armed(marker)            -- the collective state (one unit: its own switch)
	if state.feedback_on == on then return end     -- nothing to change

	set_armed_look(marker, on)
	state.feedback_on = on
end

-- FLIP ONE SWITCH. The state belongs to ONE (unit, ability) pair only;
-- every other unit's state for the same ability is untouched. The badge
-- letter is updated right here as the click's feedback.
local function set_auto_for_unit(ui_id, marker, value)
	local id = unit_slot(ui_id)
	local per = armed[id]
	if per == nil then
		per = {}
		armed[id] = per
	end
	per[marker] = value == true
	apply_ability_feedback(marker)
end


-- ============================================================================
-- SECTION 10 - CLICKING: the badge toggle and the card selection
--   The left-click is the mod's only input, and a left-click that reaches
--   the script is routed two ways by what was clicked:
--     * a click on one of OUR badges ("zz_auto_badge", "..._fs", "..._hos")
--       flips the switch for that badge's ability across the SELECTED
--       GROUP: one selected unit - exactly the old single flip; several -
--       the checkbox rule over the selected units that own the ability
--       (all of them on -> switch them all off, otherwise switch them all
--       on; selected non-owners are never touched). Three checks guard the
--       click first: the id must map to a known ability, a unit must
--       actually be selected, and the ability must be claimed on the
--       current dial - a stale badge still on screen but no longer on the
--       wheel is INERT;
--     * a click on a unit's card selects that unit (the card's id IS the
--       unit's unique id - a plain lookup). This is the immediate
--       fast-path; the card sweep (SECTION 11) re-derives the selection
--       from the engine's own card states within one UI tick and wins.
--   When a click changes the selection, both badges' letters are refreshed
--   in this same handler call, so the letters never wait for a timer.
--   (Earlier builds also listened for right-clicks and key presses; those
--   routes are gone - this listener is the whole control surface.)
-- ============================================================================
core:add_listener(
	"zz_deadly_onslaught_lclick_control",
	"ComponentLClickUp",
	function(context) return true end,      -- every left-click, unfiltered; the body decides
	function(context)
		local clicked_id = tostring(context.string)

		-- (a) A CLICK ON ONE OF OUR BADGES: flip the switch(es) for that
		-- ability - the whole selected group, not just one unit.
		if string.sub(clicked_id, 1, 8) == "zz_auto_" then
			local ability = ability_for_badge(clicked_id)
			if ability == nil then
				return          -- some other zz_auto_* component; not ours to route
			end
			if selected_unit_id == nil and #selected_ui_ids == 0 then
				return          -- nothing selected: the click has nothing to act on
			end

			-- THE CLICK GUARD: a badge whose ability is not claimed on
			-- the current dial is inert (the very same test the UI tick
			-- uses, so the two can never disagree).
			if not marker_claimed_now(ability) then
				return
			end

			-- THE SELECTED SET: the click acts on every unit the engine
			-- reports as selected - the callback keeps this current once
			-- it has delivered (SECTION 2/11); until then the card read
			-- does. With NO selected set in the callback world the click
			-- acts on nobody; in the fallback world the single tracker
			-- stands in, exactly as before.
			local targets = {}
			for i = 1, #selected_ui_ids do
				if selected_ui_ids[i] ~= nil then
					targets[#targets + 1] = selected_ui_ids[i]
				end
			end
			if #targets == 0 then
				if selection_callback_alive then
					-- the engine's own answer: nothing is selected - the
					-- tracker may still name the last unit, but acting on
					-- it would flip a unit the player has deselected
					return
				end
				targets[1] = tostring(selected_unit_id)
			end

			if #targets <= 1 then
				-- ONE SELECTED UNIT - one unit's own pair flips. When the
				-- callback set is in charge the one id IS the engine's
				-- answer (it may already be newer than the tracker, which
				-- catches up at the next convergence); the fallback world
				-- keeps acting on the tracker, exactly as before. A scan
				-- that has not seen the ability on it yet does not block
				-- the flip (a late-arriving ability stays armable).
				local single_id = tostring(targets[1])
				if not selection_callback_alive then single_id = tostring(selected_unit_id) end
				local arm_slot = unit_slot(single_id)
				local per = armed[arm_slot]
				local was_armed = per ~= nil and per[ability.marker] == true
				set_auto_for_unit(single_id, ability.marker, not was_armed)
				return
			end

			-- SEVERAL SELECTED UNITS - the checkbox rule over the selected
			-- units that own one of this ability's names: all of them on
			-- -> switch them all off; otherwise -> switch them all on.
			-- Selected units that do not own the ability are never
			-- touched, so each unit's switch stays its own.
			local owners = {}
			for i = 1, #targets do
				if unit_owns_marker(targets[i], ability.marker) then
					owners[#owners + 1] = targets[i]
				end
			end
			if #owners == 0 then
				return          -- nobody selected owns the ability: nothing to flip
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
			return
		end

		-- (b) A CLICK ON A UNIT'S CARD: select that unit (the lookup is
		-- by the card's id; nil = not one of our units' cards).
		local clicked_unit = units_by_ui_id[clicked_id]
		if clicked_unit ~= nil then
			local selection_changed = (selected_unit_id ~= clicked_id)
			selected_unit_id = clicked_id

			-- On an ACTUAL change, refresh both badges' letters right
			-- here - this click is the refresh trigger.
			if selection_changed then
				walk_on_selection_change = true   -- the dial now belongs to this unit
				refresh_badge_letters_for_selection()
			end

			-- Re-sync the feedback bookkeeping so every other path agrees.
			for _, ability in ipairs(ABILITIES) do
				apply_ability_feedback(ability.marker)
			end
			return
		end

		-- Any other left-click is not this mod's business.
	end,
	true
)


-- ============================================================================
-- SECTION 11 - WHICH UNIT IS SELECTED (the engine's callback first, the
--   game's own cards as the fallback and reconciliation)
--   The battle manager delivers every select/deselect event of a watched
--   unit to the engine selection callback (SECTION 2), which maintains the
--   selected set; a per-UI-tick convergence (converge_engine_selection)
--   folds any change into one act: the tracker adoption and the badge
--   letters. The unit cards are the FALLBACK: whenever no callback event
--   has ever arrived, they drive the selection exactly as they always did.
--   The engine marks a SINGLE selected unit's card with the state text
--   'selected' (measured in battle: the selected card reads 'selected',
--   every other card reads 'active'); a group/box selection is NOT
--   reported by the cards - that is why the callback exists.
--   The card read derives from the cards:
--     * exactly one card reports 'selected' -> that unit is selected;
--     * several report it -> keep the current tracker when it is one of
--       them, otherwise take the first;
--     * none (or the reads fail)            -> keep the current selection.
--   TWO CADENCES share one reader and one derivation, so they can never
--   disagree:
--     * the FAST path runs on EVERY UI tick (~50 ms): a selection change
--       reaches the tracker and both badge letters within one tick;
--     * the once-per-second safety net runs the same derivation again.
--   Everything here only READS engine values; nothing is written. Every
--   read is guarded and type-checked - a failing read simply is not a
--   card, and nothing here can error out of the UI tick.
--   The card's component id must EQUAL the unit's unique id (the proven
--   bridge: the game's own code matches them the same way) - ids are
--   compared as exact strings, never searched for.
-- ============================================================================

local CARD_SWEEP_EVERY_N_POLL_TICKS = 4      -- 4 x 250 ms = ~1 s of battle time
local last_card_sweep_tick = -1000           -- so the first tick with units sweeps at once
-- A RUNAWAY GUARD, not a working limit: a single-player unit-card panel
-- tops out at 20 cards, so 40 can never bind for a real army - it is only
-- a belt against a pathological wanted-list (the walk itself is separately
-- visit-bounded). The old value (12) was a legacy work-cap that made units
-- past the 12th collected card invisible to selection tracking.
local CARD_SWEEP_MAX = 40                    -- at most this many wanted ids per read

-- Read a component's id as text; nil when it cannot be read. (The small
-- shared id-reader for the lookups below.)
local function read_component_id(uic)
	local ok, id = pcall(function() return uic:Id() end)
	if ok and type(id) == "string" and string.len(id) > 0 then return id end
	return nil
end

-- Resolve the cards-panel container by id: the engine's own recursive
-- search from the ui root, verified against the component's own id; nil
-- when nothing usable is found (the caller then falls back).
local function card_panel_find(root, wanted)
	local ok, got = pcall(function()
		local raw = root:Find(wanted, false)   -- the engine's own search (false = quiet when missing)
		if raw == nil then return nil end
		local ok_w, wrapped = pcall(UIComponent, raw)
		if ok_w and wrapped ~= nil then return wrapped end
		return raw
	end)
	if ok and got ~= nil and read_component_id(got) == wanted then return got end
	return nil
end

-- ONE bounded walk of the panel subtree, collecting the wanted cards;
-- every node's id read is guarded (a failing read is simply not a card),
-- the walk is visit- and depth-bounded, and each child read is guarded.
-- Nothing here can raise.
local function card_collect_from(start, wanted, found)
	local visits, max_visits = 0, 900   -- the walk is bounded in visits ...
	local stack = { { node = start, depth = 0 } }
	while #stack > 0 and visits < max_visits do
		local item = table.remove(stack)
		local node, depth = item.node, item.depth
		visits = visits + 1

		local id = read_component_id(node)   -- is this node one of the wanted cards?
		if id ~= nil and wanted[id] ~= nil and found[id] == nil then
			found[id] = node
		end

		if depth < 8 then   -- descend into children (depth-bounded)
			local ok_n, n = pcall(function() return node:ChildCount() end)
			if ok_n and type(n) == "number" and n > 0 then
				for i = n - 1, 0, -1 do
					local ok_c, child = pcall(function() return node:Find(i) end)
					if ok_c and child ~= nil then
						local ok_w, wrapped = pcall(UIComponent, child)
						if ok_w and wrapped ~= nil then
							-- Add the child to the work stack (visited later, deeper).
							stack[#stack + 1] = { node = wrapped, depth = depth + 1 }
						end
					end
				end
			end
		end
	end
end

-- THE SHARED CARD READ. Finds the watched units' cards and reads each
-- card's engine state ONCE; both cadences use this, so they can never
-- disagree about what the cards say. Returns the ids whose state reads
-- exactly 'selected', sorted (so "the first selected card" is a
-- reproducible choice). The wanted ids are collected in the WATCH LIST's
-- own order, each read through its cached id (SECTION 5) - never pair
-- order - so the subset swept under the cap is identical every call
-- (items 14 + 6).
local function read_tracked_card_states()
	-- THE WANTED IDS, IN A STABLE ORDER (items 14 + 6, one fix with the
	-- cached id in SECTION 5). The old shape collected the ids by walking
	-- the lookup table with pairs(), whose order is not defined (it is the
	-- process's hash order), so above the cap the subset swept - and with
	-- it which cards were state-read - changed from call to call. Now the
	-- ordered watch list is the source: walk tracked_units BY INDEX and
	-- read each entry's cached id (stored at registration), so the first
	-- cap-many ids are always the same list. No pair order, no engine read
	-- on the cached path. The cap stays a runaway guard (real panels top
	-- out at 20 cards, so it never binds); past it, units are now excluded
	-- consistently instead of flickering.
	local wanted, wanted_count = {}, 0   -- collect the card ids to look for ...
	local ordered = {}
	if tracked_units ~= nil then
		for i = 1, #tracked_units do
			if wanted_count >= CARD_SWEEP_MAX then break end   -- the runaway guard (never binds for real panels)
			local su = tracked_units[i]
			local cached = su and su.zz_tracked_ui_id
			if cached == nil then
				-- Every registered entry carries the cache, so this branch is
				-- unreachable; kept only as a defensive fallback for an entry
				-- with no cached id yet (the old guarded engine read).
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
	table.sort(ordered)   -- sorted, so "the first selected card" is reproducible

	local found = {}
	if wanted_count > 0 then
		local ok_r, root = pcall(function() return core:get_ui_root() end)   -- find the UI root (guarded)
		if ok_r and root ~= nil then
			-- The cards panel: "card_panel_docker", else "cards_panel",
			-- else the ui root itself (the walk then simply starts at the
			-- top). Not finding the panel is not fatal - the derivation
			-- then simply sees no cards this read.
			local start = card_panel_find(root, "card_panel_docker")
			if start == nil then start = card_panel_find(root, "cards_panel") end
			if start == nil then start = root end
			card_collect_from(start, wanted, found)
		end
	end

	-- Every found card's engine state, read ONCE (guarded; '?' on a
	-- failed read - which is never a claim). A card whose state reads
	-- exactly 'selected' is one of the units the game has selected.
	local selected = {}
	for i = 1, #ordered do
		local ui_id = ordered[i]
		local card = found[ui_id]
		if card ~= nil then
			-- Read this card's own state text ('?' when unreadable).
			local state = "?"
			local ok_s, s = pcall(function() return card:CurrentState() end)
			if ok_s and type(s) == "string" then state = s end
			if state == "selected" then
				selected[#selected + 1] = ui_id      -- the game says this unit is selected
			end
		end
	end

	-- THE SELECTED SET: expose the WHOLE group, not just the single-choice
	-- derivation built over it - the badge click and the collective badge
	-- letter read selected_ui_ids (SECTION 2). Two regimes:
	--   * no callback event has EVER been delivered (the API is missing, or
	--     the engine never called back): the cards are in charge and REPLACE
	--     the set, exactly as before - the unchanged fallback; a read that
	--     found no cards at all leaves the set alone, like the derivation
	--     keeping the current selection;
	--   * the callback HAS delivered (it is the engine's own word on group
	--     selections, which the cards do not report): the callback-fed set is
	--     in charge. The cards may still ADD an id the set has not seen (a
	--     single selection whose event did not arrive) - and such a
	--     card-added id is dropped again once the cards stop reporting it,
	--     so the reconciliation can never leave a phantom behind.
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
		end
	end

	return selected
end

-- THE SHARED DERIVATION: the engine's own signal decides the selection.
-- Given the sorted list of cards that read 'selected':
--   * exactly one  -> adopt its id;
--   * several      -> keep the current selection when it is one of them,
--                     otherwise take the first (the group-selection rule);
--   * none         -> nothing to adopt (the caller keeps the selection).
-- Returns the id to adopt, or nil.
local function derive_selection_from_cards(previous, selected)
	local derived = nil   -- nothing to adopt until a card says so
	if #selected == 1 then
		derived = selected[1]              -- exactly one selected card: adopt it
	elseif #selected > 1 then
		-- Several selected cards (group selection): keep the current one
		-- when it is among them, otherwise take the first (sorted) one.
		derived = previous
		local among = false
		for i = 1, #selected do
			if selected[i] == previous then among = true end
		end
		if not among then derived = selected[1] end
	end
	return derived
end

-- THE FAST PATH: derive the selection from the card states on EVERY UI
-- tick and adopt a change within that same tick. Completely quiet while
-- nothing changes; on a change it adopts and refreshes both badge
-- letters in this same call, so the letters never lag. The caller guards
-- the whole call.
local function fast_card_selection()
	local previous = "none"
	if selected_unit_id ~= nil then previous = tostring(selected_unit_id) end

	local selected = read_tracked_card_states()
	local derived = derive_selection_from_cards(previous, selected)
	if derived == nil or derived == previous then return end

	-- THE SELECTION CHANGED: adopt it and refresh the letters now.
	selected_unit_id = derived
	walk_on_selection_change = true   -- the dial now belongs to the adopted unit
	refresh_badge_letters_for_selection()
end

-- THE ENGINE SELECTION CONVERGENCE: the callback (SECTION 2) maintains the
-- selected set event by event; this runs on every UI tick and turns whatever
-- it collected into ONE coalesced act:
--   * the set change is folded ONCE per tick (the live copy writes a single
--     line naming the whole set; the signature below collapses any burst of
--     events between two ticks, and a steady set costs one string compare
--     and nothing else);
--   * the tracker adoption - the same rule the card derivation uses, so the
--     two mechanisms can never disagree (one selected id -> adopt it; several
--     -> keep the tracker when it is among them, else the first; none -> keep
--     it);
--   * the badge letters: refreshed in the same call - per letter, silently
--     unless a letter really changed when only the collective state moved.
local function converge_engine_selection()
	if not selection_set_dirty then return end
	selection_set_dirty = false

	local ids = {}
	for i = 1, #selected_ui_ids do ids[i] = tostring(selected_ui_ids[i]) end
	table.sort(ids)
	local sig = table.concat(ids, ",")
	if sig == selection_set_sig then return end
	selection_set_sig = sig

	local previous = "none"
	if selected_unit_id ~= nil then previous = tostring(selected_unit_id) end
	local derived = derive_selection_from_cards(previous, ids)
	if derived ~= nil and derived ~= previous then
		selected_unit_id = derived
		walk_on_selection_change = true   -- the dial now belongs to the adopted unit
		refresh_badge_letters_for_selection()
	else
		for _, ability in ipairs(active_abilities_list()) do
			refresh_badge_letter(ability.marker)
		end
	end
end

-- THE ONCE-A-SECOND SAFETY NET: the same read and the same derivation
-- again, one pass per ~1 s of battle time. In practice the fast path has
-- already adopted any change on earlier ticks; this stands ready in case
-- it ever runs first. The caller guards the whole call.
local function card_sweep()
	local previous = "none"
	if selected_unit_id ~= nil then previous = tostring(selected_unit_id) end

	local selected = read_tracked_card_states()
	local derived = derive_selection_from_cards(previous, selected)

	if derived ~= nil and derived ~= previous then
		-- Adopt and refresh the letters (normally the fast path did this
		-- first; this branch is the insurance).
		selected_unit_id = derived
		walk_on_selection_change = true   -- the census adoption re-homes the dial too
		refresh_badge_letters_for_selection()
	end
end


-- ============================================================================
-- SECTION 12 - STARTING IT ALL UP
--   What runs when this file loads in a battle, and the two repeating
--   timers that keep everything moving:
--     * the POLL (250 ms, battle/model timer): the battlefield watcher
--       (SECTION 7);
--     * the UI TICK (50 ms requested, real/UI timer): the badge builder,
--       the show/hide and letters, the card fast path and the scan retry.
--       The UI work of the mod lives here: the UI timer is the context
--       that has never died (UI work inside a model-timer callback is
--       what killed the poll in earlier rounds).
--   Phase callbacks: the game calls these when the battle enters a named
--   phase. "Deployment" and "Deployed" kick a scan and a feedback sync;
--   "Deployed" also builds the watch list.
-- ============================================================================

-- The phase hook: try to find the ability buttons, and bring every
-- badge's letter up to date with the current selection. Guarded.
local function phase_ui_refresh()
	find_ability_buttons()           -- the abilities' own buttons (SECTION 8)
	for _, ability in ipairs(ABILITIES) do
		apply_ability_feedback(ability.marker)   -- keep each letter in step
	end
end

bm:register_phase_change_callback("Deployment", function()
	pcall(phase_ui_refresh)          -- scan for the buttons; sync the letters
end)
bm:register_phase_change_callback("Deployed", function()
	pcall(phase_ui_refresh)          -- again once deployed (the HUD now exists)
end)
bm:register_phase_change_callback("Deployed", function()
	pcall(rebuild_unit_list)         -- and build the watch list for the battle
end)

-- The battlefield poll, registered ONCE and never touched again - the
-- timer registry is never modified from this script (removing and
-- re-adding a model timer is what broke the trigger in an earlier round).
bm:repeat_callback(poll, POLL_MS, POLL_NAME)

-- The UI tick's own counter (it also gates the scan retries below).
local ui_ticks = 0

local function ui_tick()
	ui_ticks = ui_ticks + 1

	-- (1) BUILD ANY BADGE THAT IS WAITING (the deferred creation). One
	-- attempt per badge per tick, up to MAX_BADGE_ATTEMPTS per claim; a
	-- failed attempt discards the half-built badge so the retry starts
	-- clean. After the budget is spent the marker waits until the dial is
	-- rebuilt (a fresh claim resets everything).
	for _, ability in ipairs(active_abilities_list()) do
		local marker = ability.marker
		local state = ability_state[marker]
		-- A claimed button whose badge is still missing and not given up on:
		if state.badge == nil and state.button ~= nil and pending_badge[marker] ~= nil
			and badge_gave_up[marker] == nil then
			if (badge_attempts[marker] or 0) >= MAX_BADGE_ATTEMPTS then
				badge_gave_up[marker] = true   -- wait for the dial to rebuild
			else
				badge_attempts[marker] = (badge_attempts[marker] or 0) + 1
				local ok = pcall(create_badge, marker)
				if not ok then
					discard_badge(state)       -- destroy it, then clear it for a clean retry
				end
			end
		end
		if state.badge ~= nil then pending_badge[marker] = nil end   -- the badge exists: done waiting
	end

	-- (2) SHOW/HIDE EACH BADGE FROM THE CLAIMED SET, and keep its letter
	-- true, EVERY tick. The desired visibility is recomputed from the
	-- claimed set - the marker is claimed on the dial right now (the same
	-- live test the click guard uses) AND its button reference exists.
	-- Whenever that differs from what was last applied, the badge is set
	-- to the desired state again. So no path can leave a badge visible
	-- while its ability is not on the dial - this holds after a dial
	-- rebuild, a slot change, or the ability disappearing.
	local active_dropped = false   -- item 1.4: a stale claim died this tick
	for _, ability in ipairs(active_abilities_list()) do
		local marker = ability.marker
		local state = ability_state[marker]

		-- A claim that is no longer live dies here: a rebuilt dial loses
		-- its stale claims (and any pending badge request with them).
		local claimed = marker_claimed_now(ability)   -- is it still on the dial right now?
		if not claimed and state.button ~= nil then
			state.button = nil
			pending_badge[marker] = nil
			active_dropped = true
		end

		if state.badge ~= nil then
			local desired = claimed and state.button ~= nil   -- should it be visible?

			if (state.badge_shown == true) ~= desired then
				state.badge_shown = desired
				pcall(function() state.badge:SetVisible(desired) end)
			end

			-- The per-tick safety net for the letter: converges within
			-- one tick of any change, and stays silent when steady.
			if state.badge_shown == true then
				refresh_badge_letter(marker)
			end
		end

		-- Keep the on-screen position in step with the computed offset.
		if state.badge ~= nil then pcall(place_badge, marker) end
	end

	-- ITEM 1.4 - a stale claim dropped this tick shrank the inputs: refresh
	-- the active set (silent unless the membership moved).
	if active_dropped then refresh_active_abilities() end

	-- (3) THE ENGINE SELECTION CONVERGENCE: fold whatever the callback
	-- collected since the last tick into ONE set change - adopt the tracker
	-- and refresh the letters first. Guarded like everything else.
	pcall(converge_engine_selection)

	-- (4) THE CARD SELECTION, FAST: adopt a selection change within one
	-- tick. Guarded like everything else.
	pcall(fast_card_selection)

	-- (5) THE ONCE-A-SECOND CARD SWEEP: the same derivation as a safety
	-- net, one pass per ~1 s of battle time. Guarded.
	if (tick_count - last_card_sweep_tick) >= CARD_SWEEP_EVERY_N_POLL_TICKS then
		last_card_sweep_tick = tick_count
		pcall(card_sweep)
	end

	-- (6) KEEP TRYING TO FIND THE ABILITY BUTTONS until every one of them
	-- is claimed: every second UI tick a scan runs (the buttons appear
	-- with the orders bar, which does not exist in the earliest phases).
	-- (6) THE REASONED DIAL SCAN (item 1.1). The scan runs only when there is
	-- a reason to expect OUR buttons on the dial:
	--   * a selection change this tick, or a newly tracked unit from the
	--     re-list (coalesced - one scan at most): scan immediately;
	--   * nothing known yet about the selected unit's keys (early battle, or
	--     nothing selected): scan as before, every other tick - the
	--     BOOTSTRAPPING phase;
	--   * the selected unit OWNS one of our keys whose claim is missing: retry
	--     every 4th tick (~200 ms) until the dial yields it;
	--   * otherwise: a coarse safety net, every 100th tick (~5 s), so a bound
	--     ability, a granted ability or a wrong owned-keys read can never
	--     leave us permanently blind.
	-- The scan itself and its cap and probe behaviour are unchanged;
	-- all_buttons_found() now ends a scan the moment the ACTIVE dial is
	-- complete - which an empty active set is, vacuously - so no scan runs at
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

-- The UI tick: real (UI) timer, 50 ms requested. It is the badge builder,
-- the visibility controller, the letter safety net and the card fast
-- path - all the UI work of the mod.
bm:repeat_real_callback(ui_tick, 50, "zz_deadly_onslaught_ui")
