#!/usr/bin/env python3
"""Round 181 (user, 2026-11-20: "Row 98, Land Mine: A / Fix the range mismatches / 28 Surprise Squig! implement blob
with clearance").

  Land Mine (row 98, option A): NEW melee_clear_block - melee_clear AND at least LAND_MINE_MIN_MEN (60) enemy soldiers
    inside the blast centred on the caster (25 m; FOURTH.blast_cover counts each enemy unit at most once in full).
  Surprise Squig! (row 28): NEW enemy_summon_blob - the standing enemy infantry block with the most value inside the
    summoned squig's explosion (GENERATED FOURTH.SUMMON_BLAST_TEXT: 21 m), none of ours within the blast + 10 m; the
    summon is placed on that block's ground. No half-packed-block line (the doc's row 28 has none; at 21 m it would be
    292 soldiers).
  The range mismatches (rule 3: target_intercept_range): Curse of Khsar 35 -> 100; Ravaging Swarm x2 30 -> 100; Lord of
    Undeath split: its five 50 m keys keep the entry (200 -> 50), the 200 m key (_4) gets its own entry.
"""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"
import os  # noqa: E402
import sys  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_summon_blast as GSB  # noqa: E402

LOU_OLD = ('\t{ marker = "lord_of_undeath", name = "Lord of Undeath", trigger = "enemy_ground_melee",\n'
           '\t\tbadge = "zz_auto_badge_lord_of_undeath",\n'
           '\t\tkeys = {\n'
           '\t\t\t"wh_pro03_lord_abilities_lord_of_undeath",\n'
           '\t\t\t"wh_pro03_lord_abilities_lord_of_undeath_0",\n'
           '\t\t\t"wh_pro03_lord_abilities_lord_of_undeath_1",\n'
           '\t\t\t"wh_pro03_lord_abilities_lord_of_undeath_2",\n'
           '\t\t\t"wh_pro03_lord_abilities_lord_of_undeath_3",\n'
           '\t\t\t"wh_pro03_lord_abilities_lord_of_undeath_4" },\n'
           '\t\trange_real = 200,\n'
           '\t\tox = 0, oy = 0 },\n')
LOU_NEW = ('\t-- ROUND 181 (range fix): the five 50 m keys keep this entry; the 200 m key has its own (rule 3)\n'
           '\t{ marker = "lord_of_undeath", name = "Lord of Undeath", trigger = "enemy_ground_melee",\n'
           '\t\tbadge = "zz_auto_badge_lord_of_undeath",\n'
           '\t\tkeys = {\n'
           '\t\t\t"wh_pro03_lord_abilities_lord_of_undeath",\n'
           '\t\t\t"wh_pro03_lord_abilities_lord_of_undeath_0",\n'
           '\t\t\t"wh_pro03_lord_abilities_lord_of_undeath_1",\n'
           '\t\t\t"wh_pro03_lord_abilities_lord_of_undeath_2",\n'
           '\t\t\t"wh_pro03_lord_abilities_lord_of_undeath_3" },\n'
           '\t\trange_real = 50,\n'
           '\t\tox = 0, oy = 0 },\n'
           '\t-- ROUND 181 (range fix): the Lord of Undeath key whose cast range is 200 m\n'
           '\t{ marker = "lord_of_undeath_4", name = "Lord of Undeath", trigger = "enemy_ground_melee",\n'
           '\t\tbadge = "zz_auto_badge_lord_of_undeath_4",\n'
           '\t\tkeys = { "wh_pro03_lord_abilities_lord_of_undeath_4" },\n'
           '\t\trange_real = 200,\n'
           '\t\tox = 0, oy = 0 },\n')


def rng(marker, name, fam, key, old, new):
    a = ('\t{ marker = "%s", name = "%s", trigger = "%s",\n\t\tbadge = "zz_auto_badge_%s",\n\t\tkeys = { "%s" },\n'
         '\t\trange_real = %d,\n' % (marker, name, fam, marker, key, old))
    b = ('\t-- ROUND 181 (range fix): range_real %d -> %d (the game\'s target_intercept_range)\n'
         '\t{ marker = "%s", name = "%s", trigger = "%s",\n\t\tbadge = "zz_auto_badge_%s",\n\t\tkeys = { "%s" },\n'
         '\t\trange_real = %d,\n' % (old, new, marker, name, fam, marker, key, new))
    return (a, b)


R = [
    LOU_OLD and (LOU_OLD, LOU_NEW),
    rng("curse_of_khsar", "Curse of Khsar", "enemy_ground_area", "wh2_dlc09_character_abilities_curse_of_khsar", 35, 100),
    rng("dispatch_the_swarm_attack", "Ravaging Swarm", "enemy_melee", "wh3_dlc29_hero_active_dispatch_the_swarm_attack", 30, 100),
    rng("dispatch_the_swarm_attack_upgraded", "Ravaging Swarm Upgraded", "enemy_melee",
        "wh3_dlc29_hero_active_dispatch_the_swarm_attack_upgraded", 30, 100),
    ('\t{ marker = "land_mine", name = "Land Mine", trigger = "melee_clear",',
     '\t-- ROUND 181 (score-3 review): melee_clear_block\n\t{ marker = "land_mine", name = "Land Mine", trigger = "melee_clear_block",'),
    ('\t{ marker = "surprise_squig", name = "Surprise Squig!", trigger = "enemy_ground_melee",',
     '\t-- ROUND 181 (score-3 review): enemy_summon_blob\n\t{ marker = "surprise_squig", name = "Surprise Squig!", trigger = "enemy_summon_blob",'),
    # the shot picker's new kind
    ('\tif kind == "armour" or kind == "infantry" or kind == "area" then list = m.enemies end   -- ROUND 158: area\n',
     '\tif kind == "armour" or kind == "infantry" or kind == "area" or kind == "summon" then list = m.enemies end   -- ROUND 158: area; ROUND 181: summon\n'),
    ('\t\telseif kind == "models" then   -- ROUND 178',
     '\t\telseif kind == "summon" then   -- ROUND 181: Surprise Squig, a standing block, the most value in the explosion\n'
     '\t\t\tok_kind = FOURTH.ww_target_still(e)\n'
     '\t\t\tlocal _, v = FOURTH.blast_cover(e, m, FOURTH.entry_blast_r() or 0)\n'
     '\t\t\ts1 = v\n'
     '\t\telseif kind == "models" then   -- ROUND 178'),
    ('\telseif kind ~= "execute" and kind ~= "value" and kind ~= "waver" then',
     '\telseif kind ~= "execute" and kind ~= "value" and kind ~= "waver" and kind ~= "summon" then   -- ROUND 181: no caster gate for the squig;'),
    ('\t\t\tif kind == "models" and e.men < FOURTH.MODELS_FLOOR then return false end   -- ROUND 178\n',
     '\t\t\tif kind == "models" and e.men < FOURTH.MODELS_FLOOR then return false end   -- ROUND 178\n'
     '\t\t\tif kind == "summon" and not FOURTH.ww_target_still(e) then return false end   -- ROUND 181\n'),
    ('\treturn key and FOURTH.VORTEX_R[key]', '\treturn key and (FOURTH.VORTEX_R[key] or FOURTH.SUMMON_BLAST_R[key])   -- ROUND 181: a summon that explodes'),
    # wiring
    ('\thealth_aura_ally_rule = FOURTH.evaluate_health_aura_ally_rule,   -- ROUND 180\n',
     '\tmelee_clear_block = FOURTH.evaluate_melee_clear_block,   -- ROUND 181\n'
     '\tenemy_summon_blob = FOURTH.evaluate_enemy_summon_blob,\n'
     '\thealth_aura_ally_rule = FOURTH.evaluate_health_aura_ally_rule,   -- ROUND 180\n'),
    ('\thealth_aura_ally_rule = "When armed, fires when this unit or a friendly unit it may target is at or below 75% health, cast on it",\n',
     '\tmelee_clear_block = "When armed, fires in melee when none of our other units is inside its blast and at least 60 enemy soldiers are",   -- ROUND 181\n'
     '\tenemy_summon_blob = "When armed, places the summon under the standing enemy block worth the most inside its explosion, none of ours near",\n'
     '\thealth_aura_ally_rule = "When armed, fires when this unit or a friendly unit it may target is at or below 75% health, cast on it",\n'),
    ('\thealth_aura_ally_rule = "Fires on the most hurt unit nearby it may target, below 75% health",\n',
     '\tmelee_clear_block = "Fires in melee unless wavering[, clear of allies{FF}], with 60+ enemies in the blast",   -- ROUND 181\n'
     '\tenemy_summon_blob = "Fires under the standing enemy block worth the most[, clear of allies{FF}]",\n'
     '\thealth_aura_ally_rule = "Fires on the most hurt unit nearby it may target, below 75% health",\n'),
]
R = [x for x in R if x]
NEW_FNS = '''
-- ============================================================================
-- ROUND 181 - LAND MINE (row 98, user: "A"), SURPRISE SQUIG! (row 28, user: "implement blob with clearance").
--   blast_cover: the enemy soldiers (and their live value) a blast of radius r centred on tgt covers: the 19 sample
--     points, each unit counted at most at its own strength (the plain sampling over-counts a small unit in a big blast).
--   melee_clear_block (Land Mine): melee_clear AND at least LAND_MINE_MIN_MEN enemy soldiers inside the blast.
--   enemy_summon_blob (Surprise Squig!): the standing enemy infantry block with the most value inside the summon's
--     explosion (SUMMON_BLAST_R), none of ours within the blast + SHOT_SAFE_M; placed on that block's ground.
-- ============================================================================
FOURTH.LAND_MINE_MIN_MEN = 60   -- user ruling 2026-11-20 ("Row 98, Land Mine: A": 60 enemy soldiers in the 25 m blast)

function FOURTH.blast_cover(tgt, m, r)
	local share = math.pi * r * r / #FOURTH.BLOB_RING
	local pts = {}
	for k = 1, #FOURTH.BLOB_RING do
		local px = tgt.x + FOURTH.BLOB_RING[k][1] * r
		local pz = tgt.z + FOURTH.BLOB_RING[k][2] * r
		for i = 1, #m.all do
			if FOURTH.blob_rect_gap(px, pz, m.all[i]) == 0 then pts[i] = (pts[i] or 0) + 1 end
		end
	end
	local men, value = 0, 0
	for i, n in pairs(pts) do
		local e = m.all[i]
		local got = math.min(e.men, n * share * e.density)
		men = men + got
		value = value + got * (e.vps or 0)
	end
	return men, value
end

function FOURTH.evaluate_melee_clear_block(unit, routing)
	local why = FOURTH.evaluate_melee_clear(unit, routing)
	if not why then return nil end
	local r = FOURTH.entry_blast_r()
	local x, z = FOURTH.self_xz(unit)
	if r == nil or x == nil then return nil end
	local men = FOURTH.blast_cover({ x = x, z = z }, FOURTH.blob_map(false), r)
	if men < FOURTH.LAND_MINE_MIN_MEN then return nil end
	@@BLOCK_RETURN@@
end

function FOURTH.evaluate_enemy_summon_blob(unit, routing)
	FOURTH.eg_mode = "shot"
	FOURTH.shot_kind = nil
	if routing or FOURTH.entry_blast_r() == nil then return nil end
	local m = FOURTH.blob_map(false)
	local e, s = FOURTH.shot_pick(unit, m, "summon", false, false)
	if e == nil or s == nil or s <= 0 then return nil end
	FOURTH.shot_take(unit, e, "summon", false, false)
	@@SUMMON_RETURN@@
end
'''
BLOCK_LIVE = ('return why .. string.format("; %.0f enemy soldiers inside the %sm blast (needs %d)", men, tostring(r),\n'
              '\t\tFOURTH.LAND_MINE_MIN_MEN)')
SUMMON_LIVE = ('return FOURTH.shot_reason(unit, e, "the standing enemy block worth the most in the summon\'s explosion",\n'
               '\t\tstring.format("value %.0f in the %sm blast", s, tostring(FOURTH.entry_blast_r())))')
FN_ANCHOR = "\n-- ============================================================================\n-- ROUND 180 - THE SCORE-3 REVIEW, ROWS 87-114 AND 128"
TBL_ANCHOR = "FOURTH.load_vortex_table()\n"

for path in (SRC, ANN):
    live = (path == SRC)
    s = open(path, encoding="utf-8", newline="").read()
    for a, b in R:
        n = 2 if a.startswith("\tif kind == \"armour\" or kind == \"infantry\"") else 1
        assert s.count(a) == n, (path[-12:], a[:90], s.count(a))
        s = s.replace(a, b)
    fns = NEW_FNS.replace("@@BLOCK_RETURN@@", BLOCK_LIVE if live else "return true").replace(
        "@@SUMMON_RETURN@@", SUMMON_LIVE if live else "return true")
    if not live:
        fns = fns.replace("\tlocal why = FOURTH.evaluate_melee_clear(unit, routing)\n\tif not why then return nil end\n",
                          "\tif not FOURTH.evaluate_melee_clear(unit, routing) then return false end\n")
    assert s.count(FN_ANCHOR) == 1, path
    s = s.replace(FN_ANCHOR, "\n" + fns.strip("\n") + "\n" + FN_ANCHOR, 1)
    assert s.count(TBL_ANCHOR) == 1
    s = s.replace(TBL_ANCHOR, TBL_ANCHOR + GSB.lua_block(GSB.derive(GSB.keys_in(s))))
    assert "@@" not in s and "SUMMON_BLAST_TEXT = \"wh3_dlc25_character_abilities_surprise_squig=21\"" in s
    open(path, "w", encoding="utf-8", newline="").write(s)
    print(path[-36:], "patched")
