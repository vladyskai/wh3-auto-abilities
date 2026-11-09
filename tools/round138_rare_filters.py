#!/usr/bin/env python3
"""Round 138 (harness 137): the five rarer enemy target filters, and Missile Mirror's shooting trigger.

User request 2026-11-09 "Rarer target filters" and rulings:
  * Entangle (flying_currently): the existing not_flying class (live is_currently_flying());
  * Eternal Gaze (undead_unit): NEW class not_undead, from a GENERATED undead set (tools/gen_undead_keys.py,
    unit attribute "undead"; an unreadable type is not offered);
  * Void Pendulum, Word of Change (hasnt_casting_ability): "Lords/Heroes only" - the commander class (no battle
    read or data list can tell a spellcaster);
  * Missile Mirror (is_not_missile_unit): NEW class missile (the existing generated FOURTH.class_keys.missile),
    and its trigger "Missile enemy shooting" -> the NEW enemy_missile_shooting: an enemy missile unit inside
    the 70% bound, NOT in melee, whose ammo_left() dropped between two polls no more than
    ENEMY_AMMO_FRESH_S apart and whose last drop is within max(AMMO_OFF_FACTOR x reload, AMMO_OFF_MIN_S)
    (the round-126 firing-flag window). The enemy ammunition read has never been proven on an enemy: it
    fails closed (no read, no cast) and the live file logs one line the first time it cannot be read.
No string.find. Every helper is a FOURTH field.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_undead_keys as G  # noqa: E402

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"

CLASS = {"entangle": "not_flying", "gaze_of_usirian": "not_undead", "void_pendulum": "commander",
         "word_of_change": "commander", "unit_bound_missile_mirror": "missile"}


def entry_span(s, marker):
    tag = '\t{ marker = "%s",' % marker
    assert s.count(tag) == 1, marker
    a = s.index(tag)
    b = s.index("ox = 0, oy = 0 },\n", a) + len("ox = 0, oy = 0 },\n")
    block = s[a:b]
    assert block.count("\t{ marker = ") == 1 and "target_class" not in block, marker
    return a, b, block


def sub(s, a, b):
    assert s.count(a) == 1, (a[:80], s.count(a))
    return s.replace(a, b)


CLS_OLD = '\tif cls == "large" then return FOURTH.class_keys.large[t] == true end\n'
CLS_NEW = ('\t-- ROUND 138: Eternal Gaze (undead_unit) and Missile Mirror (is_not_missile_unit)\n'
           '\tif cls == "not_undead" then return FOURTH.class_keys.undead[t] ~= true end\n'
           '\tif cls == "missile" then return FOURTH.class_keys.missile[t] == true end\n' + CLS_OLD)
MODE_OLD = ('\t\telseif eg_mode_now == "fast" then\n'
            '\t\t\t-- ROUND 135: still moving fast and close to one of our units\n'
            '\t\t\tcond_now = (FOURTH.fast_enemy_near(enemy, unit) ~= nil)\n'
            '\t\tend\n')
MODE_NEW = ('\t\telseif eg_mode_now == "fast" then\n'
            '\t\t\t-- ROUND 135: still moving fast and close to one of our units\n'
            '\t\t\tcond_now = (FOURTH.fast_enemy_near(enemy, unit) ~= nil)\n'
            '\t\telseif eg_mode_now == "shoot" then\n'
            '\t\t\t-- ROUND 138: Missile Mirror - still shooting and not in melee\n'
            '\t\t\tcond_now = (not still_melee) and FOURTH.enemy_shooting(enemy)\n'
            '\t\tend\n')

BLOCK = """-- ============================================================================
-- ROUND 138 - THE RARER TARGET FILTERS AND MISSILE MIRROR'S SHOOTING TRIGGER.
--   Classes: not_undead (Eternal Gaze; the GENERATED undead set), missile
--   (Missile Mirror; the generated missile set), not_flying (Entangle),
--   commander (Void Pendulum, Word of Change: Lords/Heroes, the closest
--   approximation of "can cast spells" - user ruling 2026-11-09).
--   enemy_missile_shooting (NEW, Missile Mirror): an enemy missile unit inside
--   the 70% bound, not in melee, that is SHOOTING - its ammo_left() dropped
--   between two samples no more than ENEMY_AMMO_FRESH_S apart, and the last
--   drop lies within the firing-flag window max(AMMO_OFF_FACTOR x reload,
--   AMMO_OFF_MIN_S). An unreadable enemy ammunition never fires.
-- ============================================================================
FOURTH.ENEMY_AMMO_FRESH_S = 2      -- a drop counts only between two samples this close (no stale drop)
FOURTH.enemy_ammo = {}             -- enemy ui id -> { last, seen_s, reload, last_drop_s }
FOURTH.enemy_ammo_unreadable_logged = false

-- true while the enemy is shooting (see above); every call also takes the sample
function FOURTH.enemy_shooting(enemy)
	local id = nil
	pcall(function() id = tostring(enemy:unique_ui_id()) end)
	if id == nil then return false end
	local now_s = tick_count * POLL_MS / 1000
	local ok_a, now = pcall(function() return enemy:ammo_left() end)
	if not ok_a or type(now) ~= "number" then
@@UNREADABLE@@		return false
	end
	local st = FOURTH.enemy_ammo[id]
	if st == nil then
		local reload = nil
		local t = FOURTH.type_plain(enemy)
		if t ~= nil then reload = FOURTH.RELOAD_S[t] end
		FOURTH.enemy_ammo[id] = { last = now, seen_s = now_s, reload = reload }
		return false
	end
	if now < st.last and (now_s - st.seen_s) <= FOURTH.ENEMY_AMMO_FRESH_S then
		st.last_drop_s = now_s
	end
	st.last = now
	st.seen_s = now_s
	if st.last_drop_s == nil then return false end
	local window = FOURTH.AMMO_OFF_MIN_S
	if st.reload ~= nil and FOURTH.AMMO_OFF_FACTOR * st.reload > window then
		window = FOURTH.AMMO_OFF_FACTOR * st.reload
	end
	return (now_s - st.last_drop_s) <= window
end

-- Missile Mirror: the closest enemy missile unit in the bound that is shooting and not in melee
function FOURTH.evaluate_enemy_missile_shooting(unit, routing)
	FOURTH.eg_mode = "shoot"
	if routing then return @@NONE@@ end
	local ok_coll, coll = pcall(function() return bm:get_scriptunits_for_main_enemy_army_to_local_player() end)
	if not ok_coll or coll == nil then return @@NONE@@ end
	local ok_n, n = pcall(function() return coll:count() end)
	if not ok_n or type(n) ~= "number" then return @@NONE@@ end
	local best, best_gap = nil, nil
	for i = 1, n do
		local ok_su, su = pcall(function() return coll:item(i) end)
		local enemy = nil
		if ok_su and su ~= nil then pcall(function() enemy = su.unit end) end
		if enemy ~= nil then
			local ok_alive, alive = pcall(function() return enemy:number_of_men_alive() end)
			local valid = FOURTH.eg_enemy_valid(enemy)
			if ok_alive and type(alive) == "number" and alive > 0 and (valid == nil or valid == true)
				and FOURTH.eg_class_ok(enemy) then
				-- the sample is taken for every missile enemy, in the bound or not
				local shooting = FOURTH.enemy_shooting(enemy)
				local ok_m, melee = pcall(function() return enemy:is_in_melee() end)
				if shooting and not (ok_m and melee == true) and FOURTH.eg_enemy_within_bound(unit, enemy) then
					local gap = FOURTH.eg_enemy_gap(unit, enemy)
					if best == nil or (gap ~= nil and (best_gap == nil or gap < best_gap)) then
						best, best_gap = enemy, gap
					end
				end
			end
		end
	end
	if best == nil then return @@NONE@@ end
	FOURTH.eg_enemy = best
	FOURTH.eg_arm = "shoot"
	FOURTH.eg_caster_su = FOURTH.eg_fresh_caster_su(unit)
	FOURTH.cast_target = best
@@RETURN@@
end

"""
UNREAD_LIVE = ("\t\tif not FOURTH.enemy_ammo_unreadable_logged then\n"
               "\t\t\tFOURTH.enemy_ammo_unreadable_logged = true\n"
               "\t\t\tlog(\"missile mirror: an enemy's ammo_left() cannot be read - the shooting trigger FAILS CLOSED (no cast). One-time notice.\")\n"
               "\t\tend\n")
RET_LIVE = ("\tlocal etype = \"enemy\"\n"
            "\tpcall(function() etype = tostring(best:type()) end)\n"
            "\treturn string.format(\"enemy missile unit shooting (targeting %s, distance %sm, bound %sm)\", etype,\n"
            "\t\t(best_gap ~= nil) and string.format(\"%.1f\", best_gap) or \"?\", tostring(FOURTH.eg_range_m))")
MAP_OLD = "\twavering_aura = FOURTH.evaluate_wavering_aura,\n"
MAP_NEW = MAP_OLD + "\t-- ROUND 138\n\tenemy_missile_shooting = FOURTH.evaluate_enemy_missile_shooting,\n"
TIP_OLD = '\twavering_aura = "When armed, fires when this unit or a friendly unit near it is wavering",\n'
TIP_NEW = TIP_OLD + '\tenemy_missile_shooting = "When armed, fires on the closest enemy missile unit in range that is shooting",\n'
ANCHOR = "FOURTH.evaluators = {\n"

UND = G.lua_block(G.derive()) + "\n"
for path, live in ((SRC, True), (ANN, False)):
    s = open(path, encoding="utf-8", newline="").read()
    assert "enemy_missile_shooting" not in s and "FOURTH.class_keys.undead" not in s
    before = s.count("\t\ttarget_class = ")
    for m, cls in CLASS.items():
        a, b, block = entry_span(s, m)
        nb = block.replace("\t\tox = 0, oy = 0 },\n", '\t\ttarget_class = "%s",\n\t\tox = 0, oy = 0 },\n' % cls)
        if m == "unit_bound_missile_mirror":
            assert 'trigger = "enemy_engaged_or_shot",' in nb
            nb = nb.replace('trigger = "enemy_engaged_or_shot",', 'trigger = "enemy_missile_shooting",')
        s = s[:a] + nb + s[b:]
    blk = BLOCK.replace("@@UNREADABLE@@", UNREAD_LIVE if live else "")
    blk = blk.replace("@@NONE@@", "nil" if live else "false")
    blk = blk.replace("@@RETURN@@", RET_LIVE if live else "\treturn true")
    s = sub(s, CLS_OLD, CLS_NEW)
    s = sub(s, MODE_OLD, MODE_NEW)
    s = sub(s, MAP_OLD, MAP_NEW)
    s = sub(s, TIP_OLD, TIP_NEW)
    s = sub(s, ANCHOR, UND + blk + ANCHOR)
    assert s.count("\t\ttarget_class = ") == before + 5
    open(path, "w", encoding="utf-8", newline="").write(s)
    print(path, "target classes", before, "->", before + 5, "| enemy_missile_shooting", s.count('trigger = "enemy_missile_shooting"'))
