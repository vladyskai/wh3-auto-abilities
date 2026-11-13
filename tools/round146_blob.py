#!/usr/bin/env python3
"""Round 146 (harness 145): THE BLOB TRIGGER (user rulings 2026-11-13).

  Scope: "79 open attacks" - the open group B attacks whose projectile explodes; 77 built (Dead Eye and Focused Shot
         are excluded: the game lets them target single-entity units only, so an infantry blob can never be theirs).
  Rule:  "A. Density line" - fire at the best SAFE enemy infantry unit when the blast around its centre would cover at
         least half of what it covers inside one tightly packed block: need = round(0.5 x pi x R^2 / PACKED_M2), R = the
         ability's blast radius (generated), PACKED_M2 = 2.368 (generated).
  Margin:"10 m" - no soldier of ours within R + 10 m of any part of the target unit's estimated rectangle.
  Map:   the round-145 probe's reads: centre, bearing, ordered_width, men, class, visibility (bm:get_player_alliance()),
         flying; depth = ranks x the type's close spacing (generated table; default 1.48 x 1.6). Infantry = an inf_* class,
         NOT in the generated large set, not flying (exact true excludes), at least 10 men, visible exactly true.
  Re-check: just before the cast the map is rebuilt and the chosen enemy must still pass every test (eg_mode "blob").
"""
import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_blob_tables as GB  # noqa: E402
import list_blob_candidates as LC  # noqa: E402

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"
EXCLUDED = {"wh3_dlc26_character_abilities_dead_eye", "wh2_dlc13_lord_abilities_kill_shot"}
NEW_R = [55, 60, 80, 130, 250, 350, 400, 600]


def sub(s, a, b):
    assert s.count(a) == 1, (a[:80], s.count(a))
    return s.replace(a, b)


def marker_of(key):
    return re.sub(r"^wh\d?_(main|dlc\d+|pro\d+|twa\d+|cp\d+)_", "", key)


def rows():
    out = [r for r in LC.candidates() if r["key"] not in EXCLUDED]
    assert len(out) == 77, len(out)
    return sorted(out, key=lambda r: r["key"])


def entries(rs, existing):
    txt = ""
    seen = set()
    for r in rs:
        m = marker_of(r["key"])
        if m in seen or ('marker = "%s"' % m) in existing:
            m = r["key"]                  # the full key is unique
        assert m not in seen and ('marker = "%s"' % m) not in existing, m
        seen.add(m)
        name = r["name"].replace('"', "'")
        rr = int(r["range"]) if r["range"] == int(r["range"]) else r["range"]
        lines = ['\t{ marker = "%s", name = "%s", trigger = "enemy_blob",' % (m, name),
                 '\t\tbadge = "zz_auto_badge_%s",' % m,
                 '\t\tkeys = { "%s" },' % r["key"],
                 "\t\trange_real = %s," % rr]
        if "flying_currently" in r["flags"]:
            lines.append('\t\ttarget_class = "not_flying",')
        lines.append("\t\tox = 0, oy = 0 },")
        txt += "\n".join(lines) + "\n"
    return txt


COMMON = r'''-- ============================================================================
-- ROUND 146 - THE BLOB TRIGGER (user rulings 2026-11-13: "A. Density line",
-- "10 m", "79 open attacks"). For an exploding attack aimed at an enemy UNIT:
--   1. the live map (the round-145 probe's reads) - our units, and the enemy
--      INFANTRY we can see (an inf_* class, not in the generated large set, not
--      flying, at least 10 men, is_visible_to_alliance exactly true);
--   2. every visible enemy infantry unit inside this ability's 70% bound is a
--      candidate; it is UNSAFE when any soldier of ours stands within the blast
--      radius + BLOB_MARGIN_M of any part of its estimated rectangle;
--   3. a safe candidate's score = the enemy infantry soldiers inside the blast
--      around its centre (overlapping units count);
--   4. fire at the best one when the score reaches the density line: half of
--      what the blast holds inside one tightly packed block.
-- The blast radius and the spacing are GENERATED tables (below). Depth is an
-- estimate: ranks x the type's front-to-back spacing (there is no depth read).
-- ============================================================================
FOURTH.BLOB_MARGIN_M = 10      -- user ruling 2026-11-13: "10 m"
FOURTH.BLOB_FRACTION = 0.5     -- user ruling 2026-11-13: "A. Density line" (half a packed block)
FOURTH.BLOB_MIN_MEN = 10       -- a unit with fewer soldiers is not counted as an infantry block
FOURTH.blob_cache = nil
FOURTH.blob_cache_tick = nil
FOURTH.blob_r = nil

'''
TABLES_TAIL = r'''
-- the density line for a blast of radius r (metres): at least one soldier
function FOURTH.blob_need(r)
	return math.max(1, math.floor(FOURTH.BLOB_FRACTION * math.pi * r * r / FOURTH.PACKED_M2 + 0.5))
end

-- one unit's estimated rectangle and its soldier points; nil when unreadable or dead
function FOURTH.blob_shape(u)
	local ok_p, p = pcall(function() return u:position() end)
	if not ok_p or p == nil then return nil end
	local ok_x, x, z = pcall(function() return p:get_x(), p:get_z() end)
	if not ok_x or type(x) ~= "number" or type(z) ~= "number" then return nil end
	local ok_m, men = pcall(function() return u:number_of_men_alive() end)
	if not ok_m or type(men) ~= "number" or men <= 0 then return nil end
	local ok_w, w = pcall(function() return u:ordered_width() end)
	if not ok_w or type(w) ~= "number" or w <= 0 then w = 2 end
	local ok_b, b = pcall(function() return u:bearing() end)
	if not ok_b or type(b) ~= "number" then b = 0 end
	local t = FOURTH.type_plain(u)
	local ok_c, cls = pcall(function() return u:unit_class() end)
	if not ok_c or type(cls) ~= "string" then cls = "?" end
	local inf = (cls:sub(1, 3) == "inf") and not (t ~= nil and FOURTH.class_keys.large[t] == true)
	local depth
	if men <= 1 or w < 3 then
		w = math.max(w, 2)
		depth = w
	elseif inf then
		local hv = (t ~= nil) and FOURTH.SPACING[t] or nil
		local h, v = 1.48, 1.6
		if hv ~= nil then h, v = hv[1], hv[2] end
		local files = math.max(1, math.floor(w / h + 0.5))
		depth = math.ceil(men / files) * v
	else
		depth = w
	end
	local r = math.rad(b)
	local s = { unit = u, x = x, z = z, fx = math.sin(r), fz = math.cos(r), w = w, d = depth, men = men, inf = inf }
	s.rx, s.rz = s.fz, -s.fx
	-- the 9 outline points (4 corners, 4 edge middles, the centre): the closest distance between two rectangles
	-- is always reached at one of them
	s.pts = {}
	for _, a in ipairs({ -0.5, 0, 0.5 }) do
		for _, c in ipairs({ -0.5, 0, 0.5 }) do
			s.pts[#s.pts + 1] = { x + s.rx * a * w + s.fx * c * depth, z + s.rz * a * w + s.fz * c * depth }
		end
	end
	s.density = men / (w * depth)          -- soldiers per square metre, spread evenly over the rectangle
	s.half = math.sqrt(w * w + depth * depth) / 2
	return s
end

-- the 19 points that sample a blast circle of radius 1 (the centre, 6 at 0.5, 12 at 0.87); each stands for 1/19 of
-- the circle's area
FOURTH.BLOB_RING = { { 0, 0 } }
for i = 0, 5 do FOURTH.BLOB_RING[#FOURTH.BLOB_RING + 1] = { 0.5 * math.cos(i * math.pi / 3), 0.5 * math.sin(i * math.pi / 3) } end
for i = 0, 11 do FOURTH.BLOB_RING[#FOURTH.BLOB_RING + 1] = { 0.87 * math.cos(i * math.pi / 6), 0.87 * math.sin(i * math.pi / 6) } end

-- distance from a point to a shape's rectangle (0 inside)
function FOURTH.blob_rect_gap(px, pz, s)
	local dx, dz = px - s.x, pz - s.z
	local a = math.abs(dx * s.rx + dz * s.rz) - s.w / 2
	local c = math.abs(dx * s.fx + dz * s.fz) - s.d / 2
	return math.sqrt(math.max(a, 0) ^ 2 + math.max(c, 0) ^ 2)
end

-- the map for this tick (built once; rebuilt when fresh == true)
function FOURTH.blob_map(fresh)
	if not fresh and FOURTH.blob_cache_tick == tick_count and FOURTH.blob_cache ~= nil then return FOURTH.blob_cache end
	if FOURTH.map_alliance == nil then
		pcall(function() FOURTH.map_alliance = bm:get_player_alliance() end)
	end
	local alliance = FOURTH.map_alliance
	local m = { ours = {}, enemies = {}, alliance = (alliance ~= nil) }
	for i = 1, #(tracked_units or {}) do
		local u = tracked_units[i] and tracked_units[i].unit
		if u ~= nil then
			local s = FOURTH.blob_shape(u)
			if s ~= nil then m.ours[#m.ours + 1] = s end
		end
	end
	if alliance ~= nil then
		local ok_c, coll = pcall(function() return bm:get_scriptunits_for_main_enemy_army_to_local_player() end)
		local ok_n, n = false, nil
		if ok_c and coll ~= nil then ok_n, n = pcall(function() return coll:count() end) end
		if ok_n and type(n) == "number" then
			for i = 1, n do
				local e = nil
				pcall(function() e = coll:item(i).unit end)
				if e ~= nil then
					local ok_v, vis = pcall(function() return e:is_visible_to_alliance(alliance) end)
					local ok_f, fly = pcall(function() return e:is_currently_flying() end)
					if ok_v and vis == true and not (ok_f and fly == true) then
						local s = FOURTH.blob_shape(e)
						if s ~= nil and s.inf and s.men >= FOURTH.BLOB_MIN_MEN then m.enemies[#m.enemies + 1] = s end
					end
				end
			end
		end
	end
	FOURTH.blob_cache, FOURTH.blob_cache_tick = m, tick_count
	return m
end

-- the closest gap between any of our units' rectangles and the target's rectangle (nil: none of ours near enough to
-- matter). Rectangle to rectangle: the corners and edge middles of each, measured against the other.
function FOURTH.blob_friend_gap(tgt, m, reach)
	local best = nil
	for i = 1, #m.ours do
		local o = m.ours[i]
		local cd = math.sqrt((o.x - tgt.x) ^ 2 + (o.z - tgt.z) ^ 2)
		if cd - o.half - tgt.half <= reach then
			for k = 1, #o.pts do
				local g = FOURTH.blob_rect_gap(o.pts[k][1], o.pts[k][2], tgt)
				if best == nil or g < best then best = g end
			end
			for k = 1, #tgt.pts do
				local g = FOURTH.blob_rect_gap(tgt.pts[k][1], tgt.pts[k][2], o)
				if best == nil or g < best then best = g end
			end
		end
	end
	return best
end

-- the enemy infantry soldiers a blast of radius r centred on the target would cover: 19 points inside the circle,
-- each adding the soldier density of every enemy block it falls in, times its share of the circle's area; and how
-- many units it touches
function FOURTH.blob_score(tgt, m, r)
	local share = math.pi * r * r / #FOURTH.BLOB_RING
	local got, touched = 0, {}
	for k = 1, #FOURTH.BLOB_RING do
		local px = tgt.x + FOURTH.BLOB_RING[k][1] * r
		local pz = tgt.z + FOURTH.BLOB_RING[k][2] * r
		for i = 1, #m.enemies do
			local e = m.enemies[i]
			if FOURTH.blob_rect_gap(px, pz, e) == 0 then
				got = got + e.density * share
				touched[i] = true
			end
		end
	end
	local units = 0
	for _ in pairs(touched) do units = units + 1 end
	return got, units
end

-- the best safe target for this caster: shape, score, units, friendly gap; nil when none passes
function FOURTH.blob_pick(unit, m, r)
	local reach = r + FOURTH.BLOB_MARGIN_M
	local best, bs, bu, bg = nil, nil, nil, nil
	for i = 1, #m.enemies do
		local e = m.enemies[i]
		if FOURTH.eg_class_ok(e.unit) and FOURTH.eg_enemy_within_bound(unit, e.unit) then
			local g = FOURTH.blob_friend_gap(e, m, reach)
			if g == nil or g > reach then
				local sc, un = FOURTH.blob_score(e, m, r)
				if best == nil or sc > bs then best, bs, bu, bg = e, sc, un, g end
			end
		end
	end
	return best, bs, bu, bg
end

-- the pre-cast re-check: the map is rebuilt and the chosen enemy must still be the same kind of target
function FOURTH.blob_still_ok(enemy, unit)
	local r = FOURTH.blob_r
	if r == nil then return false end
	local m = FOURTH.blob_map(true)
	local id = nil
	pcall(function() id = tostring(enemy:unique_ui_id()) end)
	for i = 1, #m.enemies do
		local e = m.enemies[i]
		local eid = nil
		pcall(function() eid = tostring(e.unit:unique_ui_id()) end)
		if eid ~= nil and eid == id then
			local reach = r + FOURTH.BLOB_MARGIN_M
			local g = FOURTH.blob_friend_gap(e, m, reach)
			if g ~= nil and g <= reach then return false end
			local sc = FOURTH.blob_score(e, m, r)
			return sc >= FOURTH.blob_need(r)
		end
	end
	return false
end

'''
EVAL_LIVE = r'''function FOURTH.evaluate_enemy_blob(unit, routing)
	FOURTH.eg_mode = "blob"
	if routing then return nil end
	local key = FOURTH.rc_self_keys and FOURTH.rc_self_keys[1]
	local r = key and FOURTH.BLAST_R[key]
	if r == nil then return nil end
	local m = FOURTH.blob_map(false)
	if #m.enemies == 0 then return nil end
	local tgt, sc, un, gap = FOURTH.blob_pick(unit, m, r)
	local need = FOURTH.blob_need(r)
	if tgt == nil or sc < need then return nil end
	local etype = "enemy"
	pcall(function() etype = tostring(tgt.unit:type()) end)
	FOURTH.blob_r = r
	FOURTH.eg_enemy = tgt.unit
	FOURTH.eg_arm = "blob"
	FOURTH.eg_caster_su = FOURTH.eg_fresh_caster_su(unit)
	FOURTH.cast_target = tgt.unit
	local d = FOURTH.eg_enemy_gap(unit, tgt.unit)
	return string.format("infantry blob (targeting %s): %d enemy soldiers in the %sm blast (line %d), %d unit(s);"
		.. " ours %s; distance %sm bound %sm", etype, math.floor(sc + 0.5), tostring(r), need, un,
		(gap ~= nil) and string.format("%.1fm away (needs > %sm)", gap, tostring(r + FOURTH.BLOB_MARGIN_M)) or "not near",
		(d ~= nil) and string.format("%.1f", d) or "?", tostring(FOURTH.eg_range_m))
end

'''
EVAL_ANN = r'''-- the blob trigger: the best SAFE visible enemy infantry unit whose blast reaches the density line
function FOURTH.evaluate_enemy_blob(unit, routing)
	FOURTH.eg_mode = "blob"
	if routing then return false end
	local key = FOURTH.rc_self_keys and FOURTH.rc_self_keys[1]
	local r = key and FOURTH.BLAST_R[key]
	if r == nil then return false end
	local m = FOURTH.blob_map(false)
	if #m.enemies == 0 then return false end
	local tgt, sc = FOURTH.blob_pick(unit, m, r)
	if tgt == nil or sc < FOURTH.blob_need(r) then return false end
	FOURTH.blob_r = r
	FOURTH.eg_enemy = tgt.unit
	FOURTH.eg_arm = "blob"
	FOURTH.eg_caster_su = FOURTH.eg_fresh_caster_su(unit)
	FOURTH.cast_target = tgt.unit
	return true
end

'''
EG_OLD = "\t\t\tcond_now = (FOURTH.wavering(enemy) == true)\n\t\tend\n"
EG_NEW = ("\t\t\tcond_now = (FOURTH.wavering(enemy) == true)\n"
          "\t\telseif eg_mode_now == \"blob\" then\n"
          "\t\t\t-- ROUND 146: the blob trigger - the map is rebuilt and the target must still be safe and dense\n"
          "\t\t\tcond_now = FOURTH.blob_still_ok(enemy, unit)\n"
          "\t\tend\n")
MAP_OLD = "\tenemy_wavering = FOURTH.evaluate_enemy_wavering,\n"
MAP_NEW = MAP_OLD + "\t-- ROUND 146\n\tenemy_blob = FOURTH.evaluate_enemy_blob,\n"
TIP_OLD = '\tenemy_wavering = "When armed, fires on the closest wavering enemy in range",\n'
TIP_NEW = TIP_OLD + ('\tenemy_blob = "When armed, fires at the densest enemy infantry in range when the blast hits enough '
                     'soldiers and none of ours are near",\n')
R_OLD = "FOURTH.ENEMY_CAST_R25  = 17   -- ROUND 143: the fanatic releases, 25 m -> floor(25 x 0.70)\n"
R_NEW = R_OLD + "".join("FOURTH.ENEMY_CAST_R%-3d = %d   -- ROUND 146: blob attacks, floor(%d x 0.70)\n"
                        % (r, math.floor(r * 0.70 + 1e-9), r) for r in NEW_R)
RM_OLD = "\t[150] = FOURTH.ENEMY_CAST_R150,\n"
RM_NEW = "".join("\t[%d]%s= FOURTH.ENEMY_CAST_R%d,\n" % (r, " " * (6 - len(str(r)) - 1) if len(str(r)) < 4 else " ", r)
                 for r in NEW_R) + RM_OLD
RESTOCK = '\t{ marker = "restock", name = "Restock!", trigger = "ally_ammo_low",'
WIND_OLD = "\twind_up_s = {\n"
HOLD_OLD = "\thold_s = {\n"
ANCHOR = "FOURTH.evaluators = {\n"


def numfmt(v):
    return ("%d" % v) if v == int(v) else ("%g" % v)


def main():
    rs = rows()
    for r in rs:
        assert r["range"] > 0, r
        assert int(r["range"]) in NEW_R or int(r["range"]) in (70, 75, 90, 150, 200, 300), r["range"]
    blast = GB.blast_table([r["key"] for r in rs])
    tables = GB.lua_block(blast, GB.spacing_table())
    wind = {r["key"]: r["wind"] for r in rs if r["wind"] > 0}
    hold = {r["key"]: r["recharge"] for r in rs if r["uses"] > 1}
    wind_new = WIND_OLD + "\t\t-- ROUND 146: the blob attacks' wind-ups (unit_spec_abil wind_up_time)\n" + "".join(
        '\t\t["%s"] = %s,\n' % (k, numfmt(v)) for k, v in sorted(wind.items()))
    hold_new = HOLD_OLD + "\t\t-- ROUND 146: the blob attacks with more than one use (recharge_time)\n" + "".join(
        '\t\t["%s"] = %s,\n' % (k, numfmt(v)) for k, v in sorted(hold.items()))
    for path, ev in ((SRC, EVAL_LIVE), (ANN, EVAL_ANN)):
        s = open(path, encoding="utf-8", newline="").read()
        assert "evaluate_enemy_blob" not in s
        before = s.count("\t{ marker = ")
        s = sub(s, RESTOCK, entries(rs, s) + RESTOCK)
        s = sub(s, WIND_OLD, wind_new)
        s = sub(s, HOLD_OLD, hold_new)
        s = sub(s, R_OLD, R_NEW)
        s = sub(s, RM_OLD, RM_NEW)
        s = sub(s, EG_OLD, EG_NEW)
        s = sub(s, MAP_OLD, MAP_NEW)
        s = sub(s, TIP_OLD, TIP_NEW)
        s = sub(s, ANCHOR, COMMON + tables + TABLES_TAIL + ev + ANCHOR)
        assert s.count("\t{ marker = ") == before + 77
        assert "string.find" not in COMMON + tables + TABLES_TAIL + ev
        open(path, "w", encoding="utf-8", newline="").write(s)
        print(path, "entries", before, "->", before + 77, "| wind-ups", len(wind), "| holds", len(hold))
    import gen_recharge_keys as G
    new_block = G.lua_block(G.derive())
    pat = re.compile(r"-- GENERATED by tools/gen_recharge_keys\.py.*?\nFOURTH\.load_recharge\(\)\n", re.S)
    for path in (SRC, ANN):
        s = open(path, encoding="utf-8", newline="").read()
        assert len(pat.findall(s)) == 1
        s = pat.sub(lambda m: new_block, s)
        open(path, "w", encoding="utf-8", newline="").write(s)
    print("lock table re-derived:", len(G.derive()), "keys")
    print("density lines:", sorted(set((v, max(1, math.floor(0.5 * math.pi * v * v / GB.packed_m2() + 0.5))) for v in blast.values())))


if __name__ == "__main__":
    main()
