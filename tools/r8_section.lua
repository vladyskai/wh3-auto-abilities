-- ============================================================================
-- 13. ROUND 8 - THE DECISIVE EXPERIMENT: the UNIT-CARD STAT NUMBERS of a
--     NON-SELECTED unit, procedurally, invisibly.
--
--     THE QUESTION. The stat panel's rows are readable text for the SELECTED
--     unit (rounds 4-7, PROVEN). The comparison fields (CcoUnitStat.
--     ComparisonValue / CcoUnitDetails.ComparisonContext / the label_compare
--     delta text) are rendered from the OTHER unit only while a card is
--     hovered. Round 8 asks: can the mod obtain a NON-selected unit's real stat
--     numbers procedurally - no player hover, no gameplay interruption - by
--     SIMULATING the hover itself and reading the comparison fields while they
--     live?
--
--     THE FOUR PARTS (each its own labelled block; grep 'R8 TRUTH',
--     'R8 SIMHOVER', 'R8 DESELECT-TEST'):
--       PART 1 GROUND TRUTH - the user clicks each unit once (PROVEN-SAFE
--         reading); each new selected unit's row table is logged as
--         'R8 TRUTH <id> <stat>=<value> ...' - the comparison baseline.
--       PART 2 SIMULATED-HOVER LADDER - for every NON-selected card, and for
--         the hold durations 50 / 150 / 300 / 1500 ms: SimulateMouseOn (logged
--         BEFORE the call), a poll every 50 ms of the panel's row values + the
--         label_compare rows + the compare context fields (READ ONLY), then
--         SimulateMouseOff at the end of the hold (EVERY On is paired with an
--         Off), then a 2 s persistence watch, then one verdict line
--         'R8 SIMHOVER card=<id> hold=<ms> comparison_seen=.. panel_changed=..
--          persisted_ms=<n> delta_text=..'. The whole ladder runs with the
--         player's hands OFF the mouse.
--       PART 3 INVISIBILITY (offline; the shipped layouts were read) -
--         ui/common ui/panel_sticky_tooltips.twui.xml: default_appear_val =
--           0.25 s (the DEFAULT tooltip APPEAR delay - nothing is drawn for
--           the first 250 ms of a hover), default_stick_val 0.9 s,
--           default_removal_val 0.15 s;
--         ui/battle ui/special_unit_tooltip.twui.xml: expand_delay_ms = 2500
--           (the unit-card tooltip does not EXPAND for 2.5 s);
--         ui/common ui/tooltip_default.twui.xml: expand_delay = 0.8 s.
--         So a simulated hover shorter than R8.visible_ms (250 ms) cannot draw
--         anything: the 50 ms and 150 ms passes are labelled invisible=yes; the
--         300 ms and 1500 ms passes cross the appear delay and may show a
--         minimised tooltip briefly (1500 ms is still short of the 2500 ms
--         expand).
--       PART 4 THE FAKE-SELECTION ROUTE (R8 DESELECT-TEST) - ONCE, and ONLY
--         when armed by hand (zz_probe_r8_toggle_select_test()): call
--         battle_unit:select_in_ui() on ONE non-selected unit, log the cards'
--         states and the panel's values before/after, and whether the selection
--         appears restored. DISARMED by default; the user reports what they SAW.
--
--     SAFETY. ZERO SetContextObject calls anywhere. The ONLY writes in round 8
--     are the SimulateMouseOn/Off pair in the SIMHOVER block, each logged BEFORE
--     the call and each On tracked so an Off ALWAYS follows (r8.owed; a stuck
--     hover is reported loudly). select_in_ui is a single hand-armed pass.
--     Every engine read is pcall-walled; every walk is depth/visit capped.
--
--     DRIVING. The ladder lives in its OWN 50 ms callback (zz_probe_r8_poll) so
--     the 50 ms hold is honoured; the truth capture is throttled inside it. The
--     truth phase runs while the panel is visible; once >= R8.min_truth units
--     are recorded and no new click has arrived for R8.truth_settle_ticks, the
--     ladder auto-starts. zz_probe_r8() starts it immediately.
--
--     HOOKS: zz_probe_r8() / zz_probe_r8_status() /
--            zz_probe_r8_toggle_select_test() / zz_probe_r8_help()
-- ============================================================================

local R8_POLL_NAME = "zz_probe_r8_poll"

local R8 = {
	poll_ms = 50,               -- the ladder's own poll cadence
	truth_every = 10,           -- truth capture every N r8 ticks (~500 ms)
	truth_settle_ticks = 120,   -- 6 s without a new click -> auto-start the ladder
	min_truth = 2,              -- at least this many units clicked before the ladder
	holds = { 50, 150, 300, 1500 },  -- the SIMULATED-HOVER LADDER (ms)
	persist_ms = 2000,          -- how long after MouseOff we keep watching (ms)
	visible_ms = 250,           -- default tooltip APPEAR delay (layouts); a hold
	                            -- shorter than this is labelled invisible=yes
	snap_visits = 220,          -- the ladder snapshot's visit cap
	snap_depth = 12,
	max_passes = 48,            -- HARD CAP hover passes per session
	max_sim = 48,               -- HARD CAP SimulateMouseOn (each paired with an Off)
	truth_cap = 30,             -- HARD CAP distinct truth entries
	max_lines = 1600,           -- HARD CAP R8 log lines
	gate_every = 20,            -- log the R8 GATE line every N r8 ticks (~1 s)
	gate_visits = 400,          -- the gate probe's own bounded walk (cheap)
	gate_depth = 16,            -- the gate probe's depth cap
	gate_max_lines = 4000,      -- HARD CAP on the ~1 Hz GATE lines (own budget)
	ctx_types = { "CcoUnitStat", "CcoUnitDetails", "CcoBattleUnit" },
	compare_fields = { "Value", "ValueBase", "DisplayedValue", "ComparisonValue" },
	details_fields = { "ComparisonContext", "ComparisonValue", "HitPoints" },
}

local r8 = {
	tick = 0,
	lines = 0, line_cap_spoken = false,
	phase = "idle",             -- idle | truth | ladder | done
	truth = {}, truth_count = 0,
	truth_order = {},
	truth_last_key = nil,
	truth_last_new = 0,
	ladder_started = false,
	queue = {}, queue_i = 0, hold_i = 0,
	pass = nil, passes_done = 0, pass_rows = {},
	sim_on = 0, sim_off = 0,
	owed = nil,                 -- a component that still owes a SimulateMouseOff
	select_armed = false, select_done = false,
	select_after_at = nil, select_after_unit = nil,
	select_base_sig = nil, select_sel_before = nil,
	panel_seen = false,
	done = false,
	-- ROUND 8 GATE OBSERVABILITY (this build): the ~1 Hz gate-line cache +
	-- the force-path bookkeeping. gate_open is set the first time either the
	-- stat panel shows rows OR a unit is selected with the cards panel up.
	gate_open = false, gate_fired = "none", selection_gate = false,
	gate_seen = false, gate_rows = 0, gate_names = "", gate_sel = "none",
	gate_tab = nil, gate_lines = 0, gate_cap_spoken = false,
	force_pending = false, force_calls = 0,
}

local function r8_out(msg)
	if r8.lines >= R8.max_lines then
		if not r8.line_cap_spoken then
			r8.line_cap_spoken = true
			log("R8 line cap reached (" .. tostring(R8.max_lines) .. ") - further R8 lines are not logged")
		end
		return
	end
	r8.lines = r8.lines + 1
	log("R8 " .. tostring(msg))
end

-- ONE get_context_value read, pcall'd (READ ONLY).
local function r8_gcv(type_id, obj_id, field)
	local ok, v = pcall(function() return common.get_context_value(type_id, obj_id, field) end)
	if not ok then return nil, false end
	return v, true
end

-- ---------------------------------------------------------------------------
-- 13a0. ROUND 8 GATE OBSERVABILITY (this build). The auto-gate used to be
--       SILENT when it was closed, so a battle that never triggered could not
--       say WHY. Now, about once a second (and on a forced run), ONE cheap line
--       is logged even when the gate is closed:
--         R8 GATE panel_seen=<yes/no> stat_rows=<n> stat_names=[..]
--                 selected_card=<id|none> ladder_state=<idle/armed/running/done>
--                 fired=<panel|selection|none> [tab={..} when no rows]
--       The gate OPENS when EITHER the stat panel shows rows OR a unit is
--       selected while the cards panel is up; the line names WHICH fired. When
--       no stat rows are found the panel's TAB STATE is logged too
--       (row_header_stats / row_header_abilities state + their dy_title texts +
--       abilities_listview visibility), so 'the Stats tab is not selected' is
--       tellable apart from 'the panel is not open'.
-- ---------------------------------------------------------------------------

-- The ~1 Hz gate lines have their OWN budget so they cannot exhaust the R8
-- value-line cap (max_lines), which bounds the truth/simhover output.
local function r8_gate_out(msg)
	if r8.gate_lines >= R8.gate_max_lines then
		if not r8.gate_cap_spoken then
			r8.gate_cap_spoken = true
			log("R8 GATE line cap reached (" .. tostring(R8.gate_max_lines) .. ")")
		end
		return
	end
	r8.gate_lines = r8.gate_lines + 1
	log("R8 " .. tostring(msg))
end

local function r8_ladder_state()
	if r8.done then return "done" end
	if r8.pass ~= nil or r8.ladder_started then return "running" end
	if r8.force_pending then return "armed" end
	return "idle"
end

-- Read one named component's CurrentState + (its first child's, then its own)
-- GetStateText - the tab-header shape (row_header_stats -> dy_title).
local function r8_named_state_text(uic)
	if uic == nil then return "NOT FOUND" end
	local st = r5_read_text(function() return uic:CurrentState() end)
	local title = nil
	local n = read1(function() return uic:ChildCount() end)
	if lua_type(n) == "number" and n > 0 then
		local ok_c, child = pcall(function() return uic:Find(0) end)
		if ok_c and child ~= nil then
			local ch = wrap(child)
			title = r5_read_text(function() return ch:GetStateText() end)
		end
	end
	if title == nil then
		title = r5_read_text(function() return uic:GetStateText() end)
	end
	return "state=" .. q(st) .. " title=" .. q(title)
end

-- The panel's TAB STATE (from the handles the gate walk collected): tells
-- 'Stats tab not selected' apart from 'the panel is not open'.
local function r8_tab_state_text(g)
	local parts = {}
	parts[#parts + 1] = "row_header_stats(" .. r8_named_state_text(g.rh_stats) .. ")"
	parts[#parts + 1] = "row_header_abilities(" .. r8_named_state_text(g.rh_abil) .. ")"
	if g.abil_lv ~= nil then
		parts[#parts + 1] = "abilities_listview.vis="
			.. tostring(readb(function() return g.abil_lv:Visible() end))
	else
		parts[#parts + 1] = "abilities_listview=NOT FOUND"
	end
	parts[#parts + 1] = "unit_information=" .. (g.unit_info ~= nil and "found" or "NOT FOUND")
	return table.concat(parts, " ")
end

-- ONE bounded probe: does dynamic_stats exist, how many stat rows, which stat
-- names, which card is selected, and (always) the panel's tab state. It walks
-- hud_battle ONCE (<= gate_visits visits) and reads the cards once.
local function r8_gate_probe()
	local out = { panel = nil, rows = 0, names = "", sel = "none", fired = "none" }

	-- the selected card (reuse the proven card reader). #cards > 0 means the
	-- cards panel is up.
	local cards = r5_read_cards()
	out.has_cards = (#cards > 0)
	if out.has_cards then
		local sel = r5_selected_set(cards)
		for i = 1, #cards do
			local c = cards[i]
			if c.vis == "true" and c.id ~= nil and sel[c.id] == true then
				out.sel = c.id
				break
			end
		end
	end

	-- one bounded walk of hud_battle: dynamic_stats, its stat_name texts, and
	-- the panel's tab-state components (Id() per visit + the few interesting
	-- reads only).
	local hud = find_by_name(DEFAULT_ROOT)
	if hud == nil then
		out.tab = "hud_battle not found"
		return out
	end
	local names = {}
	local rh_stats, rh_abil, abil_lv, unit_info = nil, nil, nil, nil
	local visits = { [1] = 0 }
	local function visit(uic, depth)
		if uic == nil or visits[1] >= R8.gate_visits then return end
		visits[1] = visits[1] + 1
		local id = r5_read_text(function() return uic:Id() end)
		if id == "dynamic_stats" then
			if out.panel == nil then out.panel = uic end
		elseif id == "stat_name" then
			if #names < 40 then
				local st = r5_read_text(function() return uic:GetStateText() end)
				if st ~= nil and st ~= "" then names[#names + 1] = st end
			end
		elseif id == "row_header_stats" then rh_stats = uic
		elseif id == "row_header_abilities" then rh_abil = uic
		elseif id == "abilities_listview" then abil_lv = uic
		elseif id == "unit_information" then unit_info = uic
		end
		if depth >= R8.gate_depth then return end
		local n = read1(function() return uic:ChildCount() end)
		if lua_type(n) == "number" and n > 0 then
			for i = 0, n - 1 do
				if visits[1] >= R8.gate_visits then return end
				local ok_c, child = pcall(function() return uic:Find(i) end)
				if ok_c and child ~= nil then
					pcall(visit, wrap(child), depth + 1)
				end
			end
		end
	end
	pcall(visit, hud, 0)
	out.rh_stats, out.rh_abil, out.abil_lv, out.unit_info = rh_stats, rh_abil, abil_lv, unit_info
	out.rows = #names
	out.names = table.concat(names, ",")
	if out.rows > 0 then
		out.fired = "panel"
	elseif out.has_cards and out.sel ~= "none" then
		out.fired = "selection"
	end
	if out.rows == 0 then
		out.tab = r8_tab_state_text(out)
	end
	return out
end

-- Log the gate line (~1 Hz and on a forced run). Opens the gate on the first
-- firing condition and names it. Returns the firing condition string.
local function r8_log_gate()
	local g = r8_gate_probe()
	r8.gate_seen = (g.panel ~= nil)
	r8.gate_rows = g.rows
	r8.gate_names = g.names
	r8.gate_sel = g.sel
	r8.gate_fired = g.fired
	r8.gate_tab = g.tab
	if g.rows > 0 then r8.panel_seen = true end

	-- OPEN the gate (once) on EITHER condition.
	if r8.phase == "idle" and g.fired ~= "none" then
		r8.phase = "truth"
		if g.fired == "selection" then r8.selection_gate = true end
		if not r8.gate_open then
			r8.gate_open = true
			r8_out("GATE OPENED by " .. tostring(g.fired) .. ": "
				.. (g.fired == "panel"
					and ("the stat panel shows rows (" .. tostring(g.rows) .. ")")
					or ("a unit (" .. tostring(g.sel)
						.. ") is selected and the cards panel is up")))
		end
	end

	local line = "GATE panel_seen=" .. (g.panel ~= nil and "yes" or "no")
		.. " stat_rows=" .. tostring(g.rows)
		.. " stat_names=[" .. tostring(g.names) .. "]"
		.. " selected_card=" .. tostring(g.sel)
		.. " ladder_state=" .. r8_ladder_state()
		.. " fired=" .. tostring(g.fired)
	if g.rows == 0 then
		line = line .. " tab={" .. tostring(g.tab) .. "}"
	end
	r8_gate_out(line)
	return g.fired
end

-- ---------------------------------------------------------------------------
-- 13a. THE PANEL SNAPSHOT (the ladder's light reader): the stat rows
--      (stat_name -> dy_value), the label_compare rows (the delta text) and the
--      panel's visibility. Every read pcall-walled; depth/visit capped.
-- ---------------------------------------------------------------------------
local function r8_snapshot()
	local ds = find_by_id_under_hud("dynamic_stats")
	if ds == nil then return nil end
	local vis = readb(function() return ds:Visible() end)
	local vfr = readb(function() return ds:VisibleFromRoot() end)
	local rows, compares = {}, {}
	local cur = nil
	local visits = { [1] = 0 }
	local function visit(uic, depth)
		if uic == nil or visits[1] >= R8.snap_visits then return end
		visits[1] = visits[1] + 1
		local id = r5_read_text(function() return uic:Id() end)
		if id == "template_stat" then
			if #rows < 60 then
				cur = { uic = uic, name = nil, value = nil }
				rows[#rows + 1] = cur
			else
				cur = nil
			end
		elseif id == "stat_name" and cur ~= nil and cur.name == nil then
			cur.name = r5_read_text(function() return uic:GetStateText() end)
		elseif id == "dy_value" then
			local st = r5_read_text(function() return uic:GetStateText() end)
			if cur ~= nil and cur.value == nil then cur.value = st end
		elseif id == "label_compare" then
			if #compares < 24 then
				compares[#compares + 1] = {
					uic = uic,
					stext = r5_read_text(function() return uic:GetStateText() end),
					state = r5_read_text(function() return uic:CurrentState() end),
					vis = readb(function() return uic:Visible() end),
				}
			end
		end
		if depth >= R8.snap_depth then return end
		local n = read1(function() return uic:ChildCount() end)
		if lua_type(n) == "number" and n > 0 then
			for i = 0, n - 1 do
				if visits[1] >= R8.snap_visits then return end
				local ok_c, child = pcall(function() return uic:Find(i) end)
				if ok_c and child ~= nil then
					pcall(visit, wrap(child), depth + 1)
				end
			end
		end
	end
	pcall(visit, ds, 0)
	local parts = {}
	for i = 1, #rows do
		local rn = rows[i].name or ""
		local rv = rows[i].value or ""
		if rn ~= "" or rv ~= "" then parts[#parts + 1] = rn .. "=" .. rv end
	end
	local sig = table.concat(parts, "|")
	local cparts = {}
	local compare_vis = false
	local delta_text = nil
	for i = 1, #compares do
		local c = compares[i]
		cparts[#cparts + 1] = tostring(c.stext) .. "/" .. tostring(c.vis)
		if c.vis == "true" and c.stext ~= nil and c.stext ~= "" then
			compare_vis = true
			if delta_text == nil then delta_text = c.stext end
		end
	end
	return { ds = ds, vis = vis, vfr = vfr, rows = rows, compares = compares,
		sig = sig, compare_sig = table.concat(cparts, "|"),
		compare_vis = compare_vis, delta_text = delta_text }
end

-- READ-ONLY probe of the compare rows' context objects. A CcoUnitStat /
-- CcoUnitDetails id surfaced here feeds get_context_value for the comparison
-- fields (ComparisonValue / ComparisonContext). Change-only per (row, type).
local function r8_compare_ctx_read(snap)
	if snap == nil or snap.compares == nil then return end
	for i = 1, #snap.compares do
		local c = snap.compares[i]
		for t = 1, #R8.ctx_types do
			local tid = R8.ctx_types[t]
			local ok_id, raw = pcall(function() return c.uic:GetContextObjectId(tid) end)
			local id_text = nil
			if ok_id then id_text = safe_text(raw) end
			if id_text ~= nil and id_text ~= "" then
				local key = "rc:" .. tostring(i) .. ":" .. tid
				if r8.pass_rows[key] ~= id_text then
					r8.pass_rows[key] = id_text
					r8_out("SIMHOVER compare#" .. tostring(i) .. " GetContextObjectId("
						.. q(tid) .. ") = " .. q(id_text))
					if tid == "CcoUnitStat" then
						for f = 1, #R8.compare_fields do
							local field = R8.compare_fields[f]
							local v, okf = r8_gcv("CcoUnitStat", id_text, field)
							if okf then
								local tx = text_of(v, true)
								if tx == nil then tx = "<nil>" end
								r8_out("SIMHOVER compare#" .. tostring(i) .. " CcoUnitStat."
									.. field .. " = " .. q(tx))
							end
						end
						if i == 1 then
							local ok_o, o = pcall(function() return c.uic:GetContextObject(tid) end)
							r8_out("SIMHOVER compare#1 GetContextObject(" .. q(tid) .. ") -> type="
								.. (ok_o and lua_type(o) or "<ERR>"))
						end
					elseif tid == "CcoUnitDetails" then
						for f = 1, #R8.details_fields do
							local field = R8.details_fields[f]
							local v, okf = r8_gcv("CcoUnitDetails", id_text, field)
							if okf then
								local tx = text_of(v, true)
								if tx == nil then tx = "<nil>" end
								r8_out("SIMHOVER compare#" .. tostring(i) .. " CcoUnitDetails."
									.. field .. " = " .. q(tx))
							end
						end
					end
				end
			end
		end
	end
end

-- ---------------------------------------------------------------------------
-- 13b. THE SIMULATED HOVER (the ONLY writes in round 8; every On paired with Off)
-- ---------------------------------------------------------------------------
local function r8_sim_on(uic, card_id, hold)
	r8_out("SIMHOVER SimulateMouseOn card=" .. q(card_id) .. " hold=" .. tostring(hold)
		.. "ms (write " .. tostring(r8.sim_on + 1) .. "/" .. tostring(R8.max_sim)
		.. "; logged BEFORE the call)")
	r8.sim_on = r8.sim_on + 1
	local ok, err = pcall(function() return uic:SimulateMouseOn() end)
	if not ok then
		r8_out("SIMHOVER SimulateMouseOn error (swallowed): " .. truncate(err, 140))
		return false
	end
	return true
end

local function r8_sim_off(uic, card_id, why)
	r8_out("SIMHOVER SimulateMouseOff card=" .. q(card_id) .. " (" .. tostring(why)
		.. "; logged BEFORE the call)")
	r8.sim_off = r8.sim_off + 1
	local ok, err = pcall(function() return uic:SimulateMouseOff() end)
	if not ok then
		r8_out("SIMHOVER SimulateMouseOff error (swallowed): " .. truncate(err, 140))
		return false
	end
	return true
end

-- ---------------------------------------------------------------------------
-- 13c. THE CARD QUEUE (the cards-panel components that answer a CcoBattleUnit
--      context id and are NOT in the selected set)
-- ---------------------------------------------------------------------------
local function r8_build_queue()
	local cards = r5_read_cards()
	local sel = r5_selected_set(cards)
	local q = {}
	for i = 1, #cards do
		local c = cards[i]
		if c.uic ~= nil and c.vis == "true" then
			local ok_id, raw = pcall(function() return c.uic:GetContextObjectId("CcoBattleUnit") end)
			local ctx = nil
			if ok_id then ctx = safe_text(raw) end
			local is_sel = (c.id ~= nil and sel[c.id] == true)
			if ctx ~= nil and ctx ~= "" and not is_sel then
				q[#q + 1] = { id = c.id, ctx = ctx, uic = c.uic, state = c.state }
			end
		end
	end
	return q
end

-- ---------------------------------------------------------------------------
-- 13d. PART 1 - GROUND TRUTH (the tone the probe reads as the user clicks)
-- ---------------------------------------------------------------------------
local function r8_capture_truth()
	local snap = r8_snapshot()
	local cards = r5_read_cards()
	local sel = r5_selected_set(cards)
	local selcard = nil
	for i = 1, #cards do
		local c = cards[i]
		if c.vis == "true" and c.id ~= nil and sel[c.id] == true then selcard = c; break end
	end
	local id = nil
	if selcard ~= nil then
		local ok_id, raw = pcall(function() return selcard.uic:GetContextObjectId("CcoBattleUnit") end)
		if ok_id then id = safe_text(raw) end
		if id == nil or id == "" then id = selcard.id end
	end

	-- NO STAT ROWS YET: log WHY once (the panel's tab state) instead of staying
	-- silent - this is what tells 'the Stats tab is not selected' apart from
	-- 'the panel is not open'.
	if snap == nil or snap.sig == "" then
		local key = "NOROWS|" .. tostring(id or "(no selected card)") .. "|"
			.. tostring(r8.gate_tab)
		if r8.truth_last_key ~= key then
			r8.truth_last_key = key
			local tab = r8.gate_tab
			if tab == nil then
				local g = r8_gate_probe()
				tab = g.tab
				r8.gate_tab = tab
			end
			r8_out("TRUTH " .. tostring(id or "(no selected card)")
				.. " (no stat rows visible) tab={" .. tostring(tab) .. "}")
		end
		return false
	end

	if selcard == nil then
		if not r8.panel_seen then
			r8.panel_seen = true
			r8_out("TRUTH: the stat panel is visible - click EACH unit in turn;"
				.. " the row table is logged per unit as 'R8 TRUTH <id> <stat>=<value> ...'")
		end
		return false
	end
	local key = tostring(id) .. "|" .. snap.sig
	if r8.truth_last_key == key then return false end
	r8.truth_last_key = key
	r8.truth_last_new = r8.tick
	if r8.truth[id] == nil and r8.truth_count < R8.truth_cap then
		r8.truth[id] = true
		r8.truth_order[#r8.truth_order + 1] = id
		r8.truth_count = r8.truth_count + 1
	end
	local parts = {}
	for i = 1, #snap.rows do
		local rn = snap.rows[i].name
		local rv = snap.rows[i].value
		if (rn ~= nil and rn ~= "") or (rv ~= nil and rv ~= "") then
			parts[#parts + 1] = tostring(rn or "?") .. "=" .. tostring(rv or "?")
		end
	end
	if #parts == 0 then
		r8_out("TRUTH " .. tostring(id) .. " (panel visible, no stat rows rendered yet)")
	else
		r8_out("TRUTH " .. tostring(id) .. " " .. table.concat(parts, " "))
	end
	return true
end

-- ---------------------------------------------------------------------------
-- 13e. PART 2 - THE SIMULATED-HOVER LADDER (pass lifecycle)
--      finish -> begin is a small cycle, so the pass functions are forward
--      declared and assigned.
-- ---------------------------------------------------------------------------
local r8_begin_next_pass, r8_finish_pass, r8_start_pass, r8_step_pass

local function r8_finish_ladder(why)
	if r8.owed ~= nil then
		r8_sim_off(r8.owed, "owed", "ladder cleanup")
		r8.owed = nil
	end
	r8.phase = "done"
	r8.done = true
	r8_out("LADDER done (" .. tostring(why) .. "): passes=" .. tostring(r8.passes_done)
		.. " sim_on=" .. tostring(r8.sim_on) .. " sim_off=" .. tostring(r8.sim_off)
		.. " truth_entries=" .. tostring(r8.truth_count))
	if r8.sim_on ~= r8.sim_off then
		r8_out("LADDER WARNING: SimulateMouseOn (" .. tostring(r8.sim_on)
			.. ") != SimulateMouseOff (" .. tostring(r8.sim_off) .. ") - a hover may be stuck")
	end
end

r8_start_pass = function(card, hold)
	local snap = r8_snapshot()          -- baseline BEFORE any write
	r8.pass_rows = {}
	local p = {
		card = card,
		hold = hold,
		hold_ticks = math.max(1, math.floor(hold / R8.poll_ms)),
		base_sig = (snap ~= nil) and snap.sig or nil,
		phase = "on",
		t_on = r8.tick, t_off = nil, last_compare_tick = nil,
		comparison_seen = false, panel_changed = false,
		delta_text = nil, on_ok = nil,
	}
	r8.pass = p
	r8_out("SIMHOVER start card=" .. q(card.id) .. " ctx=" .. q(card.ctx)
		.. " hold=" .. tostring(hold) .. "ms base_values=" .. r5_sig_text(p.base_sig))
	r8.phase = "ladder"
end

r8_begin_next_pass = function()
	if r8.passes_done >= R8.max_passes then
		r8_finish_ladder("pass cap " .. tostring(R8.max_passes))
		return
	end
	if r8.sim_on >= R8.max_sim then
		r8_finish_ladder("sim cap " .. tostring(R8.max_sim))
		return
	end
	local card = r8.queue[r8.queue_i]
	if card == nil then
		r8_finish_ladder("queue exhausted")
		return
	end
	local hold = R8.holds[r8.hold_i]
	if hold == nil then
		r8.queue_i = r8.queue_i + 1
		r8.hold_i = 1
		card = r8.queue[r8.queue_i]
		if card == nil then
			r8_finish_ladder("queue exhausted")
			return
		end
		hold = R8.holds[r8.hold_i]
	end
	r8_start_pass(card, hold)
end

r8_finish_pass = function()
	local p = r8.pass
	if p == nil then return end
	local persisted = 0
	if p.last_compare_tick ~= nil and p.t_off ~= nil and p.last_compare_tick > p.t_off then
		persisted = (p.last_compare_tick - p.t_off) * R8.poll_ms
	end
	local invisible = "no"
	if p.hold <= R8.visible_ms then invisible = "yes" end
	r8_out("SIMHOVER card=" .. q(p.card.id) .. " hold=" .. tostring(p.hold)
		.. " comparison_seen=" .. (p.comparison_seen and "yes" or "no")
		.. " panel_changed=" .. (p.panel_changed and "yes" or "no")
		.. " persisted_ms=" .. tostring(persisted)
		.. " delta_text=" .. q(p.delta_text or "")
		.. " invisible=" .. invisible
		.. " on_ok=" .. tostring(p.on_ok == true))
	r8.passes_done = r8.passes_done + 1
	r8.pass = nil
	r8.hold_i = r8.hold_i + 1
	r8_begin_next_pass()
end

r8_step_pass = function()
	local p = r8.pass
	if p == nil then return end
	if p.phase == "on" then
		p.on_ok = r8_sim_on(p.card.uic, p.card.id, p.hold)
		r8.owed = p.card.uic            -- this On now owes an Off
		p.t_on = r8.tick
		p.phase = "hold"
		return
	end
	local snap = r8_snapshot()
	if snap ~= nil then
		if p.base_sig ~= nil and snap.sig ~= p.base_sig then p.panel_changed = true end
		if snap.compare_vis then
			p.comparison_seen = true
			p.last_compare_tick = r8.tick
			if snap.delta_text ~= nil then p.delta_text = snap.delta_text end
		end
		if (r8.tick % 4) == 0 then pcall(r8_compare_ctx_read, snap) end
	end
	if p.phase == "hold" then
		if (r8.tick - p.t_on) >= p.hold_ticks then
			r8_sim_off(p.card.uic, p.card.id, "hold " .. tostring(p.hold) .. "ms ended")
			r8.owed = nil
			p.t_off = r8.tick
			p.phase = "persist"
		end
	elseif p.phase == "persist" then
		if (r8.tick - p.t_off) >= math.max(1, math.floor(R8.persist_ms / R8.poll_ms)) then
			r8_finish_pass()
		end
	end
end

local function r8_start_ladder(why, force)
	if r8.pass ~= nil then
		r8_out("LADDER start refused: a pass is already in flight")
		return false
	end
	local q = r8_build_queue()
	if #q == 0 and force then
		-- FORCE: accept ANY visible card (even the selected one), so the
		-- simulated-hover mechanism still gets exercised when the auto-gate
		-- never opened. The queue still prefers the non-selected cards.
		local cards = r5_read_cards()
		for i = 1, #cards do
			local c = cards[i]
			if c.uic ~= nil and c.vis == "true" then
				local ok_id, raw = pcall(function() return c.uic:GetContextObjectId("CcoBattleUnit") end)
				local ctx = nil
				if ok_id then ctx = safe_text(raw) end
				if ctx == nil or ctx == "" then ctx = c.id end
				q[#q + 1] = { id = c.id, ctx = ctx, uic = c.uic, state = c.state }
			end
		end
		if #q > 0 then
			r8_out("LADDER FORCE fallback: no NON-selected card was found; using "
				.. tostring(#q) .. " visible card(s) including the selected one")
		end
	end
	if #q == 0 then
		r8_out("LADDER start refused: no card found (cards_panel) - "
			.. (force
				and "even a FORCED run needs >=1 visible unit card; open the cards panel"
				or "select one unit and open the stat panel, then retry"))
		return false
	end
	r8.queue = q
	r8.queue_i = 1
	r8.hold_i = 1
	r8.ladder_started = true
	r8.phase = "ladder"
	r8_out("LADDER starting (" .. tostring(why) .. "): " .. tostring(#q)
		.. " non-selected card(s); holds " .. tostring(R8.holds[1]) .. "/"
		.. tostring(R8.holds[2]) .. "/" .. tostring(R8.holds[3]) .. "/"
		.. tostring(R8.holds[4]) .. " ms; tooltip appear delay "
		.. tostring(R8.visible_ms) .. " ms (holds below it are invisible=yes)")
	r8_begin_next_pass()
	return true
end

-- ---------------------------------------------------------------------------
-- 13f. PART 4 - THE FAKE-SELECTION ROUTE (manual, single pass, default OFF)
-- ---------------------------------------------------------------------------
local r8_select_after   -- forward

local function r8_run_select_test()
	r8.select_done = true
	r8_out("DESELECT-TEST begin (manual single pass; the ONE select_in_ui write)")
	local cards = r5_read_cards()
	local sel_before = r5_selected_set(cards)
	r8.select_sel_before = sel_before
	r8_out("DESELECT-TEST cards before: " .. r5_cards_text(cards))
	local snap_before = r8_snapshot()
	r8.select_base_sig = (snap_before ~= nil) and snap_before.sig or nil
	r8_out("DESELECT-TEST panel values before: " .. r5_sig_text(r8.select_base_sig))
	local units = r5_read_units()
	local sel_su, sel_why, nonsel, nonsel_why = r5_pick_units(units, sel_before)
	r8_out("DESELECT-TEST selected-unit guess: "
		.. (sel_su ~= nil and q(sel_su.uid_text) or "NONE"))
	if nonsel == nil or nonsel.unit == nil or nonsel.uid_text == nil then
		r8_out("DESELECT-TEST skipped: no non-selected unit handle could be read")
		r8_out("DESELECT-TEST end")
		return
	end
	r8.select_after_unit = nonsel.uid_text
	r8_out("DESELECT-TEST calling battle_unit:select_in_ui() on unit " .. q(nonsel.uid_text)
		.. " (" .. tostring(nonsel_why) .. "; logged BEFORE the call)")
	local ok, err = pcall(function() return nonsel.unit:select_in_ui() end)
	if not ok then
		r8_out("DESELECT-TEST select_in_ui error (swallowed): " .. truncate(err, 140))
	else
		r8_out("DESELECT-TEST select_in_ui accepted (no Lua error)")
	end
	r8.select_after_at = r8.tick + math.max(1, math.floor(1000 / R8.poll_ms))
end

r8_select_after = function()
	r8.select_after_at = nil
	local cards = r5_read_cards()
	local sel_after = r5_selected_set(cards)
	r8_out("DESELECT-TEST cards after: " .. r5_cards_text(cards))
	local changed = false
	for id in pairs(sel_after) do
		if not (r8.select_sel_before ~= nil and r8.select_sel_before[id] == true) then changed = true end
	end
	if r8.select_sel_before ~= nil then
		for id in pairs(r8.select_sel_before) do
			if not sel_after[id] then changed = true end
		end
	end
	r8_out("DESELECT-TEST selection " .. (changed and "DID change" or "unchanged"))
	local snap_after = r8_snapshot()
	local now_sig = (snap_after ~= nil) and snap_after.sig or nil
	local pchg = (now_sig ~= r8.select_base_sig)
	r8_out("DESELECT-TEST panel values after: " .. r5_sig_text(now_sig)
		.. " (changed=" .. tostring(pchg) .. ")")
	r8_out("DESELECT-TEST restored=" .. tostring((not changed) and (not pchg))
		.. " - the user reports what they SAW on screen")
	r8_out("DESELECT-TEST end")
end

-- ---------------------------------------------------------------------------
-- 13g. THE 50 ms POLL (truth phase -> auto ladder -> manual select test) and
--      the console hooks.
-- ---------------------------------------------------------------------------
local function r8_poll()
	local ok, err = pcall(function()
		r8.tick = r8.tick + 1

		-- the deferred after-read of the select test
		if r8.select_after_at ~= nil and r8.tick >= r8.select_after_at then
			r8_select_after()
		end

		-- THE ~1 Hz GATE LINE (runs even when the gate is closed, so a battle
		-- that never triggers can say WHY). It also OPENS the gate on the
		-- selection condition and names whichever condition fired.
		if (r8.tick % R8.gate_every) == 0 or r8.force_pending then
			pcall(r8_log_gate)
		end

		-- a hover pass in flight always steps first (it owns the simulated mouse)
		if r8.pass ~= nil then
			r8_step_pass()
			return
		end

		-- the manual select test (single pass) - runs at the next idle moment once armed
		if r8.select_armed and not r8.select_done
			and (r8.phase == "done" or (r8.tick - r8.truth_last_new) >= R8.truth_settle_ticks) then
			r8_run_select_test()
			return
		end

		-- PART 1 CONDITION A (the stat panel) -> truth phase. This per-tick
		-- check is the fast tell; CONDITION B (a unit selected while the cards
		-- panel is up) is handled by the ~1 Hz gate line above, which OPENS the
		-- gate and NAMES the firing condition.
		if r8.phase == "idle" then
			local ds = find_by_id_under_hud("dynamic_stats")
			if ds ~= nil then
				r8.panel_seen = true
				r8.phase = "truth"
				if not r8.gate_open then
					r8.gate_open = true
					r8_out("GATE OPENED by panel: dynamic_stats is present")
				end
			end
		end

		-- PART 1 truth phase -> PART 2 auto ladder
		if r8.phase == "truth" then
			if (r8.tick % R8.truth_every) == 0 then
				pcall(r8_capture_truth)
			end
			if r8.truth_count >= R8.min_truth
				and (r8.tick - r8.truth_last_new) >= R8.truth_settle_ticks then
				pcall(r8_start_ladder, "auto: truth stable for "
					.. tostring(math.floor(R8.truth_settle_ticks * R8.poll_ms / 1000)) .. " s")
			end
		end
	end)
	if not ok then
		log("R8 poll error (swallowed): " .. truncate(err, 160))
	end
end

function zz_probe_r8()
	r8.force_calls = r8.force_calls + 1
	r8.force_pending = true
	-- log the FORCE banner + the gate line FIRST (unambiguous, and it shows the
	-- gate state this forced run is bypassing)
	r8_out("FORCE zz_probe_r8() called (force #" .. tostring(r8.force_calls)
		.. ") - the auto-gate is bypassed; the gate line follows")
	local ok_g, fired = pcall(r8_log_gate)
	r8.force_pending = false
	if r8.phase == "idle" then r8.phase = "truth" end
	local fired_s = ok_g and tostring(fired) or "?"
	local ok, started = pcall(r8_start_ladder, "manual FORCE: zz_probe_r8()", true)
	if not ok then return PROBE_TAG .. "R8 error: " .. tostring(started) end
	if not started then
		return PROBE_TAG .. "R8 FORCE did not start (see the log: " .. LOG_FILE
			.. ") - the cards panel must be up with >=1 visible unit card"
	end
	return PROBE_TAG .. "R8 simulated-hover ladder started (FORCED; gate fired="
		.. fired_s .. ") - KEEP YOUR HANDS OFF THE MOUSE until it finishes; log: " .. LOG_FILE
end

function zz_probe_r8_status()
	local owed = (r8.owed ~= nil) and "YES" or "no"
	local p = r8.pass
	local pass_s = "none"
	if p ~= nil then
		pass_s = tostring(p.card.id) .. " hold=" .. tostring(p.hold) .. " phase=" .. tostring(p.phase)
	end
	return PROBE_TAG .. "R8 phase=" .. tostring(r8.phase)
		.. " truth_entries=" .. tostring(r8.truth_count)
		.. " passes=" .. tostring(r8.passes_done) .. "/" .. tostring(R8.max_passes)
		.. " sim_on=" .. tostring(r8.sim_on) .. " sim_off=" .. tostring(r8.sim_off)
		.. " owed_off=" .. owed .. " pass=" .. pass_s
		.. " select_armed=" .. tostring(r8.select_armed)
		.. " select_done=" .. tostring(r8.select_done)
		.. " gate[panel_seen=" .. tostring(r8.gate_seen)
		.. " stat_rows=" .. tostring(r8.gate_rows)
		.. " selected_card=" .. tostring(r8.gate_sel)
		.. " fired=" .. tostring(r8.gate_fired)
		.. " ladder_state=" .. r8_ladder_state() .. "]"
		.. " force=" .. tostring(r8.force_calls)
		.. " | holds " .. tostring(R8.holds[1]) .. "/" .. tostring(R8.holds[2]) .. "/"
		.. tostring(R8.holds[3]) .. "/" .. tostring(R8.holds[4]) .. " ms"
		.. " | manual: zz_probe_r8() / zz_probe_r8_toggle_select_test() | log=" .. LOG_FILE
end

function zz_probe_r8_toggle_select_test()
	r8.select_armed = not r8.select_armed
	local st = r8.select_armed and "ARMED" or "DISARMED"
	return PROBE_TAG .. "R8 select test " .. st
		.. (r8.select_armed
			and " - it runs ONCE at the next idle moment (after the ladder), then stops;"
			or " - the select test will NOT run;")
		.. " log=" .. LOG_FILE
end

function zz_probe_r8_help()
	return PROBE_TAG .. "R8 DECISIVE EXPERIMENT: (1) battle -> open AND PIN the unit-details"
		.. " panel -> click EACH of your units once in turn; each click logs"
		.. " 'R8 TRUTH <id> <stat>=<value> ...'. (2) After ~6 s of no new click the"
		.. " SIMULATED-HOVER LADDER auto-starts (or call zz_probe_r8() now): for every"
		.. " non-selected card it does SimulateMouseOn / SimulateMouseOff at holds "
		.. tostring(R8.holds[1]) .. "/" .. tostring(R8.holds[2]) .. "/" .. tostring(R8.holds[3]) .. "/"
		.. tostring(R8.holds[4]) .. " ms, polling every " .. tostring(R8.poll_ms)
		.. " ms, and writes one 'R8 SIMHOVER card=.. hold=.. comparison_seen=..' verdict"
		.. " per pass - KEEP YOUR HANDS OFF THE MOUSE while it runs. Holds below "
		.. tostring(R8.visible_ms) .. " ms are labelled invisible=yes (the layout's tooltip"
		.. " appear delay). (3) zz_probe_r8_toggle_select_test() arms the ONE"
		.. " select_in_ui test (R8 DESELECT-TEST; OFF by default). status:"
		.. " zz_probe_r8_status(). log: " .. LOG_FILE
end
