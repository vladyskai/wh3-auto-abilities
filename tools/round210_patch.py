#!/usr/bin/env python3
"""Round 210 (2026-11-22, the user's second replies to the afternoon code review).

1. THE LOONS, A NEW TRIGGER (user: "I would like to change them completely ... they could only fire while the caster is
   standing. And there is ... infantry enemy unit that is approaching. And it's, let's say, between 25 and 15 meters
   from the caster unit. And then you just cast in that direction ... there shouldn't be any friendly units that are
   infantry. So single entities is okay, but any friendly units that are not single entity should [not] be in the
   path."). Spinning Loons and The Loons of Eight Peaks move to enemy_wave_charge (empty since round 204), table kind
   8: the caster standing, an enemy INFANTRY unit of more than one man moving and coming closer, its edge 15 to 25 m
   from the caster, and none of our units of more than one man in the fanatics' path (from the caster towards that
   enemy, 84 m, 4 m wide at the start widening by the simulated 95% sideways drift). The order is a ground order on
   the line towards the enemy with that bearing. Round 209's ring_clear leaves the two entries (its code stays).
2. THE FIVE CASTER-FRONT BREATHS ARE CONES FROM THE CASTER (user test: "I tested Skarbscrath and it always starts at
   the caster"): 0.1 m wide at the caster, growing per metre, path long (not offset + path), the exact-wave rule (the
   value of standing enemy soldiers under it, at most 5 of ours, single entities not counted) on a finer grid.
3. SLOW UNITS CAN CHARGE (user: "okay, do it" on option B): the run-up a charge needs is the smaller of 12 m and
   2 seconds of the unit's own run speed.
4. A TRANSFORMED UNIT'S NEW ABILITIES (user test with Malus Darkblade: the unit id AND the unit type stay): every
   4 s a unit that owns abilities of ours has its owned list read again, and its tables are rebuilt when it changed.
5. TEST BUILD ONLY: the per-second dial dump wrote one line per ability (982) while a Deadly Onslaught owner was
   selected. It now writes only the badges that exist.
Backups: docs/backups/round210/pre210_{live,ann}.lua."""
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_ww_tables as G  # noqa: E402
import gen_wave_cone as GC  # noqa: E402

LIVE = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"
BK = r"C:\Users\vlady\Desktop\WH3_mod\docs\backups\round210"

RING_LINE = "\t\tring_clear = true,   -- ROUND 209: none of our other units inside the fanatics' reach\n"
ENTRIES = [
    ('\t{ marker = "spinning_loons", name = "Spinning Loons", trigger = "enemy_ground_melee",\n',
     '\t{ marker = "spinning_loons", name = "Spinning Loons", trigger = "enemy_wave_charge",\n'),
    ('\t{ marker = "loons_of_eight_peaks", name = "The Loons of Eight Peaks", trigger = "enemy_ground_melee",\n',
     '\t{ marker = "loons_of_eight_peaks", name = "The Loons of Eight Peaks", trigger = "enemy_wave_charge",\n'),
]

A_CONE = "\tlocal L = row.off + row.path\n"
N_CONE = """	-- ROUND 210 (user test 2026-11-22: "I tested Skarbscrath and it always starts at the caster"): the breath starts at
	-- the caster, 0.1 m wide, and grows per metre along its path (not offset + path). The exact-wave rule on a finer
	-- grid: the value of the standing enemy soldiers under it, at most WAVE_OWN_MAX of ours
	if FOURTH.ww_exact(row) and row.r0 ~= nil then
		FOURTH.ww_fine = true
		local val = FOURTH.ww_line_value(unit, m, row, cx, cz, cx + dx / len * row.path, cz + dz / len * row.path)
		FOURTH.ww_fine = nil
		return val
	end
""" + A_CONE
A_GRID = ("\tlocal na = math.max(1, math.min(10, math.floor(s.w / 3 + 0.5)))\n"
          "\tlocal nc = math.max(1, math.min(6, math.floor(s.d / 3 + 0.5)))\n")
N_GRID = ("\tlocal fine = (FOURTH.ww_fine == true)   -- ROUND 210: a thin cone from the caster is counted on a 1.5 m grid\n"
          "\tlocal na = math.max(1, math.min(fine and 20 or 10, math.floor(s.w / (fine and 1.5 or 3) + 0.5)))\n"
          "\tlocal nc = math.max(1, math.min(fine and 12 or 6, math.floor(s.d / (fine and 1.5 or 3) + 0.5)))\n")

A_LOONS = "function FOURTH.evaluate_enemy_wave_charge(unit, routing)\n"
N_LOONS = """-- ============================================================================
-- ROUND 210 - THE LOONS' OWN TRIGGER (user ruling 2026-11-22: "they could only
-- fire while the caster is standing. And there is ... infantry enemy unit that
-- is approaching. And it's, let's say, between 25 and 15 meters from the caster
-- unit. And then you just cast in that direction ... single entities is okay,
-- but any friendly units that are not single entity should [not] be in the
-- path."). Table kind 8 on enemy_wave_charge: the fanatics are released at the
-- caster's front and wander. Their path: from the caster towards the enemy,
-- row.path long, row.r wide at the start, widening by the simulated 95%%
-- sideways drift (row.buf) at the end. The two distances are metre values the
-- user set himself (named constants, outside the range rule).
-- ============================================================================
FOURTH.LOONS_MIN_M = 15         -- the user's value: the enemy's edge at least this far from the caster
FOURTH.LOONS_MAX_M = 25         -- the user's value: ...and at most this far (the ability's real range)
FOURTH.LOONS_WATCH_M = 60       -- enemies inside this distance are watched for coming closer
FOURTH.LOONS_CLOSING_MPS = 1    -- "approaching": the gap to the caster shrinks at least this fast, over 1 s
FOURTH.LOONS_AIM_M = 20         -- the ordered ground point lies at most this far from the caster's centre
FOURTH.loons_hist = {}          -- caster id -> enemy id -> the last gap samples

-- is this enemy coming closer to this caster? One gap sample per poll, the answer needs a sample at least 1 s old
function FOURTH.loons_closing(unit, enemy, gap)
	local cid, eid = nil, nil
	pcall(function()
		cid = tostring(unit:unique_ui_id())
		eid = tostring(enemy:unique_ui_id())
	end)
	if cid == nil or eid == nil or gap == nil then return false end
	local per = FOURTH.loons_hist[cid]
	if per == nil then
		per = {}
		FOURTH.loons_hist[cid] = per
	end
	local h = per[eid]
	if h == nil then
		h = {}
		per[eid] = h
	end
	local now = tick_count * POLL_MS / 1000
	if #h == 0 or h[#h].t ~= now then h[#h + 1] = { t = now, g = gap } end
	while #h > 0 and now - h[1].t > 2.5 do table.remove(h, 1) end
	local old = nil
	for i = #h, 1, -1 do
		if now - h[i].t >= 1 then
			old = h[i]
			break
		end
	end
	if old == nil then return false end
	return (old.g - gap) / (now - old.t) >= FOURTH.LOONS_CLOSING_MPS
end

-- one candidate: its gap, the heading towards it and the centre distance, or nil
function FOURTH.ww_loons_ok(unit, e, m, row, closing)
	if not closing then return nil end
	local ok_c, c_mv = pcall(function() return unit:is_moving() end)
	if not (ok_c and c_mv == false) then return nil end   -- the caster stands
	if e.men <= 1 or not FOURTH.eg_class_ok(e.unit) or not FOURTH.enemy_is_infantry(e.unit) then return nil end
	local ok_mv, mv = pcall(function() return e.unit:is_moving() end)
	if not (ok_mv and mv == true) then return nil end
	local gap = FOURTH.eg_enemy_gap(unit, e.unit)
	if gap == nil or gap < FOURTH.LOONS_MIN_M or gap > FOURTH.LOONS_MAX_M then return nil end
	local cx, cz = FOURTH.self_xz(unit)
	if cx == nil then return nil end
	local dx, dz = e.x - cx, e.z - cz
	local len = math.sqrt(dx * dx + dz * dz)
	if len < 0.5 then return nil end
	local hx, hz = dx / len, dz / len
	local ex, ez = cx + hx * row.path, cz + hz * row.path
	-- none of our units of more than one man in the path (the caster never counts, our single entities do not)
	local self_id = nil
	pcall(function() self_id = tostring(unit:unique_ui_id()) end)
	local l2 = row.path * row.path
	for i = 1, #m.ours do
		local o = m.ours[i]
		if o.men > 1 then
			local oid = nil
			pcall(function() oid = tostring(o.unit:unique_ui_id()) end)
			if oid == nil or oid ~= self_id then
				local tmax = 0
				if l2 > 0 then
					for k = 1, #o.pts do
						local t = ((o.pts[k][1] - cx) * (ex - cx) + (o.pts[k][2] - cz) * (ez - cz)) / l2
						if t > tmax then tmax = t end
					end
				end
				local need = row.r + row.buf * math.min(1, tmax)
				if FOURTH.ww_pt_seg(o.x, o.z, cx, cz, ex, ez) - o.half <= need
					and FOURTH.ww_seg_rect_gap(cx, cz, ex, ez, o) <= need then
					return nil
				end
			end
		end
	end
	return gap, hx, hz, len
end

function FOURTH.evaluate_loons(unit, routing, row)
	if routing then return %(miss)s end
	local m = FOURTH.blob_map(false)
	local best, bg, bhx, bhz, blen = nil, nil, nil, nil, nil
	for i = 1, #m.all do
		local e = m.all[i]
		local gap = FOURTH.eg_enemy_gap(unit, e.unit)
		if gap ~= nil and gap <= FOURTH.LOONS_WATCH_M then
			local closing = FOURTH.loons_closing(unit, e.unit, gap)   -- sampled every poll, also outside the band
			local g, hx, hz, len = FOURTH.ww_loons_ok(unit, e, m, row, closing)
			if g ~= nil and (bg == nil or g < bg) then best, bg, bhx, bhz, blen = e, g, hx, hz, len end
		end
	end
	if best == nil then return %(miss)s end
	local cx, cz = FOURTH.self_xz(unit)
	local d = math.min(blen, FOURTH.LOONS_AIM_M)
	FOURTH.eg_range_m = FOURTH.LOONS_MAX_M   -- the pre-cast re-check's bound: the user's own distance
	FOURTH.ww_take(unit, best, row, { x = cx + bhx * d, z = cz + bhz * d, hx = bhx, hz = bhz,
		deg = FOURTH.ww_bearing(bhx, bhz), loons = true })
	local etype = "enemy"
	pcall(function() etype = tostring(best.unit:type()) end)
	return string.format("enemy infantry approaching (%%s, %%.1fm away, the band is %%s to %%sm), the caster standing; none "
		.. "of our units of more than one man in the %%sm path towards it (%%sm wide at the start, + %%sm drift at the "
		.. "end)", etype, bg, tostring(FOURTH.LOONS_MIN_M), tostring(FOURTH.LOONS_MAX_M), tostring(row.path),
		tostring(row.r), tostring(row.buf)) .. FOURTH.ww_aim_text()
end

-- ROUND 210: has a unit's list of our keys changed? (a transformation keeps the unit id and the unit type)
function FOURTH.keys_changed(old, new)
	if old == nil then return true end
	if #old ~= #new then return true end
	local seen = {}
	for i = 1, #old do seen[old[i]] = true end
	for i = 1, #new do
		if seen[new[i]] ~= true then return true end
	end
	return false
end

-- ROUND 210: the owned list of a unit is read again 2 s and 10 s after an ability was cast on it, and every re-detect
-- period once it has changed (a transformation that runs out changes it back). Answers changed, the unit's key.
FOURTH.rescan_due = {}
FOURTH.rescan_watch = {}
function FOURTH.rescan_soon(id_text)
	if id_text == nil then return end
	FOURTH.rescan_due[id_text] = { at = tick_count + 8, again = true }
end
function FOURTH.reread_unit(unit, ui_id, periodic)
	local idt = tostring(ui_id)
	local due = FOURTH.rescan_due[idt]
	local now = (due ~= nil and tick_count >= due.at)
	if now then
		if due.again then
			FOURTH.rescan_due[idt] = { at = tick_count + 32 }
		else
			FOURTH.rescan_due[idt] = nil
		end
	end
	if not now and not (periodic and FOURTH.rescan_watch[idt] == true) then return false, nil end
	local found, all_keys = scan_unit_abilities(unit)
	local now_keys = %(ours)s
	if #now_keys == 0 or not FOURTH.keys_changed(owned_keys_by_unit[idt], now_keys) then return false, nil end
	owned_keys_by_unit[idt] = now_keys
	owned_abilities_by_unit[idt] = owned_abilities_of(now_keys)
	FOURTH.rescan_watch[idt] = true
	if found ~= nil then target_key_by_unit[ui_id] = found end
%(log)s	return true, found
end

""" + A_LOONS
A_BRANCH = "\tFOURTH.ww_charge = true\n\tlocal row = FOURTH.ww_row()\n"
N_BRANCH = A_BRANCH + "\tif row ~= nil and row.kind == 8 then return FOURTH.evaluate_loons(unit, routing, row) end   -- ROUND 210\n"
A_STILL = "\t\t\tif row.kind == 4 then return FOURTH.ww_strike_value(unit, e, m, row) ~= nil end   -- ROUND 163\n"
N_STILL = ("\t\t\tif row.kind == 8 then   -- ROUND 210: the Loons, the same rule on the fresh map\n"
           "\t\t\t\tlocal gap8 = FOURTH.eg_enemy_gap(unit, e.unit)\n"
           "\t\t\t\treturn FOURTH.ww_loons_ok(unit, e, m, row, FOURTH.loons_closing(unit, e.unit, gap8)) ~= nil\n"
           "\t\t\tend\n") + A_STILL

TIP_OLD = '\tenemy_wave_charge = "When armed and standing still, fires its wave at a charging enemy whose path holds none of our units",\n'
TIP_NEW = ('\tenemy_wave_charge = "When armed and standing still, releases at enemy infantry approaching the unit, with none of '
           'our units in the path",\n')
CARD_OLD = '\tenemy_wave_charge = "Fires[ when standing still{ANIM},] at a fast enemy closing on allies[, its path clear of allies{FF}]",\n'
CARD_NEW = '\tenemy_wave_charge = "Fires when standing still at enemy infantry approaching the unit, the path clear of allies",\n'

A_SPEED = "m.ttc = m.target_dist / speed\n"
N_SPEED = A_SPEED + "\t\t\t\tm.speed = speed   -- ROUND 210: the run speed, for the run-up below\n"
A_RUNUP = "\t\t\tenough_run_up = (m.target_dist >= CHARGE_MIN_DISTANCE_M)\n"
N_RUNUP = ("\t\t\t-- ROUND 210 (user ruling 2026-11-22, \"okay, do it\"): the run-up is the smaller of CHARGE_MIN_DISTANCE_M\n"
           "\t\t\t-- and 2 seconds of the unit's own run speed, so a unit slower than 3 m/s can be seen charging too\n"
           "\t\t\tlocal run_up = CHARGE_MIN_DISTANCE_M\n"
           "\t\t\tif m.speed ~= nil and m.speed * 2 < run_up then run_up = m.speed * 2 end\n"
           "\t\t\tenough_run_up = (m.target_dist >= run_up)\n")

A_RESCAN = "\t\t\tlocal unit_abilities = owned_abilities_by_unit[tostring(ui_id)]\n"
N_RESCAN = """			-- ROUND 210: a unit that already owns abilities of ours can gain others mid-battle. A transformation keeps
			-- the unit id AND the unit type (Malus Darkblade, field 2026-11-22), so the identity watch above never
			-- sees it. FOURTH.reread_unit reads the owned list again a moment after an ability was cast on the unit
			-- (and, once a unit has changed, every re-detect period) and rebuilds its tables when the set changed.
			if target_key_by_unit[ui_id] ~= nil then
				local changed210, found210 = FOURTH.reread_unit(unit, ui_id, do_redetect)
				active_refresh_pending = active_refresh_pending or changed210
%(akey)s			end
""" + A_RESCAN
AKEY_LIVE = "\t\t\t\tif found210 ~= nil then ability_key = found210 end\n"
RESCAN_LOG = ('\tlog("owned abilities changed: unit " .. idt .. " - keys: " .. table.concat(now_keys, ", "))\n')
A_SOON1 = "\t\tr.n = r.n - 1\n\t\treturn 0\n\tend\n\tlocal hold_s = FOURTH.PLAYER_CAST_HOLD_S\n"
N_SOON1 = ("\t\tr.n = r.n - 1\n\t\treturn 0\n\tend\n"
           "\t-- ROUND 210: the player's cast may be a transformation: the selected units' owned lists are read again soon\n"
           "\tfor i = 1, #selected_ui_ids do FOURTH.rescan_soon(selected_ui_ids[i]) end\n"
           "\tlocal hold_s = FOURTH.PLAYER_CAST_HOLD_S\n")
A_SOON2 = "\t\t\t\t\tFOURTH.note_own_order(ready_key)   -- ROUND 209: the game will report this order back\n"
N_SOON2 = A_SOON2 + "\t\t\t\t\tFOURTH.rescan_soon(tostring(ui_id))   -- ROUND 210: the cast may be a transformation\n"

A_DUMP = """		local prefix = "OUR BADGE"
		if ability.marker ~= "onslaught" then
			prefix = prefix .. " [" .. ability.marker .. "]"
		end
		log(prefix .. ": visible=" .. (bvis and "true" or "false") .. " pos=" .. bpos
			.. " offset=(" .. tostring(BADGE_X + ability.ox) .. "," .. tostring(BADGE_Y + ability.oy)
			.. ") letter='" .. bletter .. "'")
"""
N_DUMP = """		local prefix = "OUR BADGE"
		if ability.marker ~= "onslaught" then
			prefix = prefix .. " [" .. ability.marker .. "]"
		end
		-- ROUND 210: only the badges that exist are written (one line per ability, 982 a second, lagged the game
		-- while a Deadly Onslaught owner was selected). The three original abilities keep their line.
		if state.badge ~= nil or ability.marker == "onslaught" or ability.marker == "foe_seeker"
			or ability.marker == "hammer_of_sigmar" then
		log(prefix .. ": visible=" .. (bvis and "true" or "false") .. " pos=" .. bpos
			.. " offset=(" .. tostring(BADGE_X + ability.ox) .. "," .. tostring(BADGE_Y + ability.oy)
			.. ") letter='" .. bletter .. "'")
		end
"""


def one(s, a, b, what):
    assert s.count(a) == 1, (what, s.count(a))
    return s.replace(a, b)


def regen(s):
    kf = G.keys_in(s)
    for pat, new in (
            (r'FOURTH\.WW_TEXT = "[^"]*"', re.search(r'FOURTH\.WW_TEXT = "[^"]*"', G.lua_block(G.derive(kf))).group(0)),
            (r'FOURTH\.WW_NOMELEE_TEXT = "[^"]*"', re.search(r'FOURTH\.WW_NOMELEE_TEXT = "[^"]*"', G.nomelee_block(kf)).group(0)),
            (r'FOURTH\.RING_TEXT = "[^"]*"', re.search(r'FOURTH\.RING_TEXT = "[^"]*"', G.ring_block(G.ring_rows(G.ring_keys(s)))).group(0))):
        old = re.search(pat, s).group(0)
        s = one(s, old, new, pat)
    old_cone = re.search(r'FOURTH\.WW_CONE_TEXT = "[^"]*"', s).group(0)
    cone = GC.derive(s)
    assert len(cone) == 25, len(cone)
    return one(s, old_cone, 'FOURTH.WW_CONE_TEXT = "%s"' % GC.text(cone), "cone")


def patch(path, live):
    s = open(path, encoding="utf-8", newline="").read()
    assert "ROUND 210" not in s, "already patched: " + path
    assert s.count(RING_LINE) == 2
    s = s.replace(RING_LINE, "")
    for old, new in ENTRIES:
        s = one(s, old, new, "entry")
    s = regen(s)
    assert "wh_main_unit_abilities_spinning_loons=8,4,84,0," in s and 'FOURTH.RING_TEXT = ""' in s
    miss = "nil" if live else "false"
    s = one(s, A_CONE, N_CONE, "cone value")
    s = one(s, A_GRID, N_GRID, "grid")
    s = one(s, A_LOONS, N_LOONS % {"miss": miss, "ours": "our_keys_of(all_keys)" if live else "all_keys",
                                   "log": RESCAN_LOG if live else ""}, "loons")
    s = one(s, A_BRANCH, N_BRANCH, "branch")
    s = one(s, A_STILL, N_STILL, "still")
    s = one(s, CARD_OLD, CARD_NEW, "card")
    s = one(s, A_SPEED, N_SPEED, "speed")
    s = one(s, A_RUNUP, N_RUNUP, "run-up")
    s = one(s, A_RESCAN, N_RESCAN % {"akey": AKEY_LIVE if live else ""}, "rescan")
    s = one(s, A_SOON1, N_SOON1, "rescan after the player's cast")
    s = one(s, A_SOON2, N_SOON2, "rescan after the mod's cast")
    if live:
        s = one(s, A_DUMP, N_DUMP, "dump")
    open(path, "w", encoding="utf-8", newline="").write(s)
    print("patched", path)


def main():
    os.makedirs(BK, exist_ok=True)
    for src, name in ((LIVE, "pre210_live.lua"), (ANN, "pre210_ann.lua")):
        dst = os.path.join(BK, name)
        if not os.path.exists(dst):
            shutil.copy2(src, dst)
        elif "--again" in sys.argv:
            shutil.copy2(dst, src)   # start again from the pre-round snapshot
    patch(LIVE, True)
    patch(ANN, False)


if __name__ == "__main__":
    main()
