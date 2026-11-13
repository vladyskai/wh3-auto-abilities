#!/usr/bin/env python3
"""Round 141 (harness 140): the nine recharge reducers, one by one (user rulings 2026-11-13).

  Scroll of Power -> self_recharging_2 (2+ of the caster's abilities recharging)
  Staff of Nagash, Staff of Tomorrow, The Liber Noctus, Channelling Staff, Aken-seth -> self_recharging (1+)
  Armour of Caledor -> melee_health75 (the existing family: in melee and health <= 75%)
  Terrorgheist Skull -> melee_self_or_ally: the caster in melee (cast on itself), else the closest ally within the 70%
      bound (100 m -> 70 m) in melee (cast on that ally)
  Spell-Wrought Sceptre -> recharging_in_reach: the caster has a recharging ability (cast on itself), else the closest
      ally within 70 m that has one (cast on that ally)
"Recharging" = an ability of that unit that the MOD cast (the game accepted it) and whose lock time - active_time +
recharge_time from the GENERATED FOURTH.RECHARGE_S (tools/gen_recharge_keys.py) - has not run out; the reducer's own
keys never count. The mod cannot see spells or abilities the player clicks, nor campaign recharge bonuses.
No string.find. Every helper is a FOURTH field.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_recharge_keys as G  # noqa: E402

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"

RETRIGGER = {"scroll_of_power": ("ushoran_health", "self_recharging_2", None),
             "staff_of_nagash": ("melee_unwavering", "self_recharging", None),
             "staff_of_tomorrow": ("melee_unwavering", "self_recharging", None),
             "the_liber_noctus": ("melee_unwavering", "self_recharging", None),
             "channelling_staff": ("melee_unwavering", "self_recharging", None),
             "aken_seth_the_staff_of_pain": ("melee_unwavering", "self_recharging", None),
             "armour_of_caledor": ("melee_unwavering", "melee_health75", None),
             "terrorgheist_skull": ("melee_unwavering", "melee_self_or_ally", "ally_range_real = 100"),
             "spell_wrought_sceptre": ("melee_unwavering", "recharging_in_reach", "ally_range_real = 100")}


def entry_span(s, marker):
    tag = '\t{ marker = "%s",' % marker
    assert s.count(tag) == 1, marker
    a = s.index(tag)
    b = s.index("ox = 0, oy = 0 },", a)
    b = s.index("\n", b) + 1
    block = s[a:b]
    assert block.count("\t{ marker = ") == 1, marker
    return a, b, block


def sub(s, a, b):
    assert s.count(a) == 1, (a[:80], s.count(a))
    return s.replace(a, b)


ELIG_OLD = '\t\t\t\t\telseif family == "fighting" then\n'
ELIG_NEW = ('\t\t\t\t\telseif family == "melee" then\n'
            '\t\t\t\t\t\t-- ROUND 141: Terrorgheist Skull - an ally in melee (the closest wins)\n'
            '\t\t\t\t\t\tlocal ok_m, m = pcall(function() return other:is_in_melee() end)\n'
            '\t\t\t\t\t\teligible = (ok_m and m == true)\n'
            '\t\t\t\t\telseif family == "recharging" then\n'
            '\t\t\t\t\t\t-- ROUND 141: Spell-Wrought Sceptre - an ally with an ability the mod cast still recharging\n'
            '\t\t\t\t\t\teligible = (FOURTH.recharging_count(other) >= 1)\n' + ELIG_OLD)
RECHECK_OLD = '\t\tif FOURTH.ab_family == "fighting" then\n'
RECHECK_NEW = ('\t\t-- ROUND 141: the melee / recharging families re-check their own condition\n'
               '\t\tif FOURTH.ab_family == "melee" then\n'
               '\t\t\tlocal ok_m, m = pcall(function() return ally:is_in_melee() end)\n'
               '\t\t\thp_ok_now = (ok_m and m == true)\n'
               '\t\tend\n'
               '\t\tif FOURTH.ab_family == "recharging" then\n'
               '\t\t\thp_ok_now = (FOURTH.recharging_count(ally) >= 1)\n'
               '\t\tend\n' + RECHECK_OLD)
POLL_OLD = "\t\t\t\t\tFOURTH.eg_class = ability.target_class\n"
POLL_NEW = POLL_OLD + ("\t\t\t\t\t-- ROUND 141: the reducer's own keys never count as 'recharging'\n"
                       "\t\t\t\t\tFOURTH.rc_self_keys = ability.keys\n")
NOTE_LIVE_OLD = '\t\toutcome = "fired"\n'
NOTE_LIVE_NEW = ('\t\t-- ROUND 141: remember the cast, so the recharge reducers know what is recharging\n'
                 '\t\tFOURTH.note_cast(unit, ability_key)\n' + NOTE_LIVE_OLD)
NOTE_ANN_OLD = '\tif ok_call then return "fired" end\n'
NOTE_ANN_NEW = ('\t-- ROUND 141: remember the cast, so the recharge reducers know what is recharging\n'
                '\tif ok_call then FOURTH.note_cast(unit, ability_key); return "fired" end\n')

COMMON = """-- ============================================================================
-- ROUND 141 - THE RECHARGE REDUCERS, ONE BY ONE (user rulings 2026-11-13).
--   The mod remembers every cast the game ACCEPTED (FOURTH.note_cast) and when
--   its lock ends: active_time + recharge_time from the GENERATED
--   FOURTH.RECHARGE_S. recharging_count = how many of a unit's abilities the
--   mod cast are still locked, the current entry's own keys excluded. Spells
--   and abilities the player clicks are invisible to it, and so are campaign
--   recharge bonuses (the table may say "recharging" a little too long).
--   self_recharging (1+), self_recharging_2 (2+): cast on the caster.
--   recharging_in_reach (Spell-Wrought Sceptre): the caster recharging -> on
--     itself, else the closest ally within the 70% bound that is -> on it.
--   melee_self_or_ally (Terrorgheist Skull): the caster in melee -> on itself,
--     else the closest ally within the bound in melee -> on it.
-- ============================================================================
FOURTH.recharge_until = {}     -- unit ui id -> { ability key -> poll tick when its lock ends }
FOURTH.rc_self_keys = nil      -- the current entry's keys (set by the poll before every evaluate)

function FOURTH.note_cast(unit, key)
	local total = FOURTH.RECHARGE_S[key]
	if total == nil then return end
	local id = nil
	pcall(function() id = tostring(unit:unique_ui_id()) end)
	if id == nil then return end
	local t = FOURTH.recharge_until[id]
	if t == nil then t = {}; FOURTH.recharge_until[id] = t end
	t[key] = tick_count + math.floor((total * 1000) / POLL_MS)
end

function FOURTH.recharging_count(unit)
	local id = nil
	pcall(function() id = tostring(unit:unique_ui_id()) end)
	if id == nil then return 0 end
	local t = FOURTH.recharge_until[id]
	if t == nil then return 0 end
	local skip = {}
	for _, k in ipairs(FOURTH.rc_self_keys or {}) do skip[k] = true end
	local n = 0
	for k, until_tick in pairs(t) do
		if until_tick > tick_count and not skip[k] then n = n + 1 end
	end
	return n
end

"""
EVAL_LIVE = """function FOURTH.evaluate_self_recharging(unit, routing)
	if routing then return nil end
	local n = FOURTH.recharging_count(unit)
	if n >= 1 then return string.format("%d of the caster's abilities recharging (need 1), cast on self", n) end
	return nil
end

function FOURTH.evaluate_self_recharging_2(unit, routing)
	if routing then return nil end
	local n = FOURTH.recharging_count(unit)
	if n >= 2 then return string.format("%d of the caster's abilities recharging (need 2), cast on self", n) end
	return nil
end

function FOURTH.evaluate_recharging_in_reach(unit, routing)
	if routing then return nil end
	local n = FOURTH.recharging_count(unit)
	if n >= 1 then return string.format("%d of the caster's abilities recharging, cast on self", n) end
	return FOURTH.ab_pick_ally(unit, routing, "recharging")
end

function FOURTH.evaluate_melee_self_or_ally(unit, routing)
	if routing then return nil end
	local ok, m = pcall(function() return unit:is_in_melee() end)
	if ok and m == true then return "the caster is in melee, cast on self" end
	return FOURTH.ab_pick_ally(unit, routing, "melee")
end

"""
EVAL_ANN = """function FOURTH.evaluate_self_recharging(unit, routing)
	if routing then return false end
	return FOURTH.recharging_count(unit) >= 1
end

function FOURTH.evaluate_self_recharging_2(unit, routing)
	if routing then return false end
	return FOURTH.recharging_count(unit) >= 2
end

function FOURTH.evaluate_recharging_in_reach(unit, routing)
	if routing then return false end
	if FOURTH.recharging_count(unit) >= 1 then return true end
	return FOURTH.ab_pick_ally(unit, routing, "recharging")
end

function FOURTH.evaluate_melee_self_or_ally(unit, routing)
	if routing then return false end
	local ok, m = pcall(function() return unit:is_in_melee() end)
	if ok and m == true then return true end
	return FOURTH.ab_pick_ally(unit, routing, "melee")
end

"""
MAP_OLD = "\tself_running = FOURTH.evaluate_self_running,\n"
MAP_NEW = MAP_OLD + ("\t-- ROUND 141\n"
                     "\tself_recharging = FOURTH.evaluate_self_recharging,\n"
                     "\tself_recharging_2 = FOURTH.evaluate_self_recharging_2,\n"
                     "\trecharging_in_reach = FOURTH.evaluate_recharging_in_reach,\n"
                     "\tmelee_self_or_ally = FOURTH.evaluate_melee_self_or_ally,\n")
TIP_OLD = '\tself_running = "When armed, fires when this unit is running",\n'
TIP_NEW = TIP_OLD + (
    '\tself_recharging = "When armed, fires when another ability of this unit is recharging",\n'
    '\tself_recharging_2 = "When armed, fires when two other abilities of this unit are recharging",\n'
    '\trecharging_in_reach = "When armed, fires when this unit or a friendly unit near it has an ability recharging",\n'
    '\tmelee_self_or_ally = "When armed, fires when this unit or a friendly unit near it is in melee",\n')
ANCHOR = "FOURTH.evaluators = {\n"

TABLE = G.lua_block(G.derive()) + "\n"
for path, ev, note in ((SRC, EVAL_LIVE, (NOTE_LIVE_OLD, NOTE_LIVE_NEW)), (ANN, EVAL_ANN, (NOTE_ANN_OLD, NOTE_ANN_NEW))):
    s = open(path, encoding="utf-8", newline="").read()
    assert "self_recharging" not in s and "FOURTH.RECHARGE_S" not in s
    for m, (old_t, new_t, extra) in RETRIGGER.items():
        a, b, block = entry_span(s, m)
        assert 'trigger = "%s",' % old_t in block, (m, old_t)
        nb = block.replace('trigger = "%s",' % old_t, 'trigger = "%s",' % new_t)
        if extra:
            assert "ally_range_real" not in nb
            nb = nb.replace("\t\tox = 0, oy = 0 },", "\t\t%s,\n\t\tox = 0, oy = 0 }," % extra, 1)
        s = s[:a] + nb + s[b:]
    s = sub(s, ELIG_OLD, ELIG_NEW)
    s = sub(s, RECHECK_OLD, RECHECK_NEW)
    s = sub(s, POLL_OLD, POLL_NEW)
    s = sub(s, note[0], note[1])
    s = sub(s, MAP_OLD, MAP_NEW)
    s = sub(s, TIP_OLD, TIP_NEW)
    s = sub(s, ANCHOR, TABLE + COMMON + ev + ANCHOR)
    counts = {f: s.count('trigger = "%s"' % f) for f in ("self_recharging", "self_recharging_2", "recharging_in_reach", "melee_self_or_ally")}
    assert counts == {"self_recharging": 5, "self_recharging_2": 1, "recharging_in_reach": 1, "melee_self_or_ally": 1}, counts
    open(path, "w", encoding="utf-8", newline="").write(s)
    print(path, counts)
