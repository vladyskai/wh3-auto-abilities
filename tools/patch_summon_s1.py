"""Stage 1 of the summon-round edit: data blocks (entries, commander set,
range constants, enemy_ground_keys) into BOTH files."""
import os, json, re

ROOT = r"C:\Users\vlady\Desktop\WH3_mod"
GEN = os.path.join(os.path.expandvars(r"%LOCALAPPDATA%\Temp"), "gen")
LIVE = os.path.join(ROOT, "mod_source", "script", "battle", "mod", "zz_test_deadly_onslaught.lua")
ANN = os.path.join(ROOT, "docs", "WH3_auto_ability_annotated.lua")

entries = open(os.path.join(GEN, "new_entries.lua"), encoding="utf-8").read()
entries = entries.replace("70%%", "70%")
cmdr = open(os.path.join(GEN, "commander_keys.lua"), encoding="utf-8").read()
plan = json.load(open(os.path.join(GEN, "plan.json"), encoding="utf-8"))

def rd(p):
    return open(p, "rb").read().decode("utf-8")

def wr(p, s):
    assert "\r" not in s, "CRLF in the new text"
    open(p, "wb").write(s.encode("utf-8"))

def sub(s, old, new, count=1, tag=""):
    n = s.count(old)
    assert n == count, "anchor %r hit %d times (want %d) %s" % (old[:60], n, count, tag)
    return s.replace(old, new)

NEW_GROUND = [k for k in plan["D_keys"]] + [k for k in plan["F_keys"]]

COMMANDER_BLOCK = """-- ============================================================================
-- THE SUMMON ROUND (harness 102 / v102) - THE FOUR NEW TRIGGERS' HELPERS.
--
--   enemy_ground_melee            (already shipped with Gate of Khorne)
--       (A) the REST of the wh_type_summon_unit class - every in-wheel,
--       non-illusion, GROUND-CASTABLE summon derived from the game's own data
--       (spawned_unit set + type wh_type_summon_unit + spawn_is_decoy false +
--       target_ground true + in-wheel + not boss-only + not implemented) - and
--       (D) the nine unlabelled real spawners. Closest FIGHTING enemy inside
--       the ability's own 70%% bound; the summon is placed on THAT ENEMY's
--       ground through the ground form. Never the caster's own ground.
--   self_summon_melee             (NEW - Nurgling Tide)
--       the user's rule, verbatim: "that one should only trigger when the
--       caster himself is in melee." Owner alive + NOT routing + is_in_melee()
--       true; the cast goes on the OWNER through the unit form. NO RANGE
--       BOUND is read or needed - a self cast has no distance to measure (the
--       ability's own row carries target_intercept_range = 0, no target flags
--       at all and affect_self = true: a self-centred spawn).
--   enemy_low_health_noncommander (NEW - Eye of Khorne, a FINISHER)
--       ANY enemy inside the ability's own 70%% bound that is BELOW 20%% HEALTH
--       and is NOT a Lord or Hero; the LOWEST-health one wins (closest as the
--       tiebreak). Cast through the UNIT form: the row has target_enemies =
--       true and target_ground = false, so perform_special_ability(key, enemy).
--   enemy_melee_noncommander      (NEW - The Dreaded Thirteenth, 4 keys)
--       ANY enemy inside the 70%% bound IN MELEE that is NOT a Lord or Hero;
--       closest wins. Cast through the enemy-GROUND form (target_ground = true,
--       spawn_type = unit_position_offset: an explosion plus a summon).
--
-- THE LORD/HERO EXCLUSION MUST COME FROM A REAL READ. It does:
--   FOURTH.commander_keys is DERIVED from the game's own class/caste columns -
--   every land_units key whose `class` is "com" (the engine's COMMANDER class;
--   the game's own invalid-target flags are literally named
--   unit_is_commander_class / unit_is_not_commander_class) UNION every
--   land_units key reached from a main_units row whose `caste` is "lord" or
--   "hero" (this second arm catches the six Krell variants whose land_units row
--   still says inf_mel - a known data quirk). It is matched by EXACT WHOLE-KEY
--   equality against battle_unit:type() (the proven land_units key read - the
--   same shape as the Slayer list). battle_unit:unit_class() == "com" is the
--   FALLBACK read when type() cannot be taken, and if NEITHER read answers the
--   unit is treated as a commander (FAIL CLOSED: the finisher never fires at a
--   unit it cannot classify), with ONE line for the whole battle.
--
-- NO NEW CHUNK-LEVEL LOCALS: every helper, table and slot below is a FIELD of
-- the FOURTH bag - the main chunk sits at Lua's 200-local ceiling.
-- ============================================================================
FOURTH.co"""+"""mmander_keys = {
""" + cmdr + """}

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

-- THE ENEMY HEALTH READ (percent, 0-100). Accepts a number or a numeric string
-- (the engine's context layer stringifies some fields); nil when unreadable.
function FOURTH.enemy_health_pct(enemy)
	local v = FOURTH.context_value(enemy, "HealthPercent")
	if type(v) == "number" then return v end
	if type(v) == "string" then
		local n = tonumber(v)
		if n ~= nil then return n end
	end
	return nil
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
						hp_text = " health=" .. string.format("%.0f", best_hp) .. "%"
					end
					log("  " .. marker .. " target: '" .. etype .. "' is the chosen enemy (" .. tostring(mode)
						.. hp_text .. ") distance=" .. ((best_gap ~= nil) and string.format("%.1f", best_gap) or "?")
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

-- EYE OF KHORNE: the FINISHER trigger.
function FOURTH.evaluate_enemy_low_health_noncommander(unit, routing)
	return FOURTH.enc_pick_enemy(unit, routing, false, "health")
end

-- THE DREADED THIRTEENTH: the non-commander in-melee trigger.
function FOURTH.evaluate_enemy_melee_noncommander(unit, routing)
	return FOURTH.enc_pick_enemy(unit, routing, true, "melee")
end

"""

for path, tag in ((LIVE, "live"), (ANN, "ann")):
    s = rd(path)
    # --- 1. the ABILITIES entries (before the table's closing brace) ---
    tail = '\t\tkeys = { "wh3_cp1_character_abilities_terrifying_presence" },\n\t\tox = 0, oy = 0 },\n}\n'
    s = sub(s, tail,
            '\t\tkeys = { "wh3_cp1_character_abilities_terrifying_presence" },\n\t\tox = 0, oy = 0 },\n\n'
            + entries + '}\n', 1, tag)

    # --- 2. the range constants + the map ---
    s = sub(s, "FOURTH.ENEMY_CAST_R35  = 24\n",
            "FOURTH.ENEMY_CAST_R35  = 24\nFOURTH.ENEMY_CAST_R45  = 31\n", 1, tag)
    s = sub(s, "FOURTH.ENEMY_CAST_R75  = 52\n",
            "FOURTH.ENEMY_CAST_R75  = 52\nFOURTH.ENEMY_CAST_R90  = 63\n", 1, tag)
    s = sub(s, "\t[35]  = FOURTH.ENEMY_CAST_R35,\n",
            "\t[35]  = FOURTH.ENEMY_CAST_R35,\n\t[45]  = FOURTH.ENEMY_CAST_R45,\n", 1, tag)
    s = sub(s, "\t[75]  = FOURTH.ENEMY_CAST_R75,\n",
            "\t[75]  = FOURTH.ENEMY_CAST_R75,\n\t[90]  = FOURTH.ENEMY_CAST_R90,\n", 1, tag)

    # --- 3. enemy_ground_keys: the nine + the four Dreaded Thirteenth keys ---
    gk_anchor = '\t\t["wh3_main_character_abilities_gate_of_khorne"] = true,\n\t},\n'
    add = '\t\t["wh3_main_character_abilities_gate_of_khorne"] = true,\n'
    for k in NEW_GROUND:
        add += '\t\t-- THE SUMMON ROUND (harness 102): %s\n' % k if False else ''
        add += '\t\t["%s"] = true,\n' % k
    add += '\t},\n'
    s = sub(s, gk_anchor, add, 1, tag)

    # --- 4. the new helpers/evaluators, before the evaluator map ---
    s = sub(s, "FOURTH.evaluators = {\n", COMMANDER_BLOCK + "FOURTH.evaluators = {\n", 1, tag)
    wr(path, s)
    print(tag, "stage 1 written:", len(s), "bytes")
