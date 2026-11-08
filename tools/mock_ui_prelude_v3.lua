-- Mock engine prelude for the ROUND-3 zz_probe_ui_text smoke test
-- (mouse-armed capture). Loaded into a lupa Lua runtime BEFORE the probe.
--
-- It provides the globals the probe touches (core, UIComponent, bm, out) and a
-- MUTABLE UI tree the Python driver can reshape between polls, PLUS the two
-- things the mouse trigger needs:
--   * core:add_listener(name, event, cond, cb, persist)  -> records the
--     ComponentMouseOn / ComponentMouseOff callbacks so M.fire() can deliver a
--     synthetic hover,
--   * component Address() / AddScriptEventReporter()      -> so the reporter
--     subscription can be observed WITHOUT being a state setter,
--   * bm:get_scriptunits_for_local_players_army()         -> M.local_units.
--
-- UI-state SETTERS (SetText / SetState / ... ) still trip (`trips[]`) so the
-- test fails if the probe ever mutates the UI. AddScriptEventReporter is NOT a
-- state setter: it is recorded in M.reporter_calls / M.reporter_log instead.

trips = {}
poll_fn = nil
poll_ms = nil
poll_name = nil
conflict = false

local function trip(name)
	return function() trips[#trips + 1] = name; error("SETTER CALLED: " .. name) end
end

local function find_recursive(node, id)
	if node.id == id then return node end
	for _, c in ipairs(node.children or {}) do
		local hit = find_recursive(c, id)
		if hit ~= nil then return hit end
	end
	return nil
end

local function make_component(id, opts)
	opts = opts or {}
	local c = {}
	c.id = id
	c.children = opts.children or {}
	c.state = opts.state or "active"
	c.stext = opts.stext
	c.tip = opts.tip
	c.stext_raises = opts.stext_raises
	c.tip_raises = opts.tip_raises
	c.id_raises = opts.id_raises
	c.hostile_state = opts.hostile_state

	function c:Id()
		if self.id_raises then error("mock: Id raises") end
		return self.id
	end
	function c:CurrentState()
		if self.hostile_state ~= nil then return self.hostile_state end
		return self.state
	end
	function c:GetStateText()
		if self.stext_raises then error("mock: GetStateText raises") end
		return self.stext
	end
	function c:GetTooltipText()
		if self.tip_raises then error("mock: GetTooltipText raises") end
		return self.tip
	end
	function c:Visible() return true end
	function c:VisibleFromRoot() return true end
	function c:Position() return 11, 22 end
	function c:ChildCount() return #self.children end
	function c:Find(i)
		if type(i) == "number" then return self.children[i + 1] end
		return find_recursive(self, i)
	end
	function c:FindByScriptTag(tag) return find_recursive(self, tag) end
	function c:SequentialFind(a, b) return find_recursive(self, a) end

	-- The mouse-trigger plumbing (NOT state setters):
	function c:Address() return "Pointer<Component> (0x" .. tostring(self.id) .. ")" end
	function c:Parent() return nil end
	function c:AddScriptEventReporter()
		if self.reporter_raises then error("mock: AddScriptEventReporter raises") end
		M.reporter_calls = M.reporter_calls + 1
		M.reporter_log[#M.reporter_log + 1] = self.id
		return true
	end

	for _, n in ipairs({ "SetText", "SetStateText", "SetProperty", "SetTooltipText",
	                     "SetState", "Layout", "CreateComponent", "Destroy",
	                     "MoveTo", "SetVisible", "SetAlpha", "Resize",
	                     "SetDockOffset", "SetDockingPoint" }) do
		c[n] = trip(n)
	end
	return c
end

-- ------------------------------------------------------------------ controls
M = {}
M.listeners = {}
M.listener_names = {}
M.reporter_calls = 0
M.reporter_log = {}
M.local_units = {}

function M.new(id, opts) return make_component(id, opts) end
function M.attach(parent, child) parent.children[#parent.children + 1] = child end
function M.clear(parent) parent.children = {} end
function M.set_text(comp, stext, tip) comp.stext = stext; comp.tip = tip end
function M.set_state(comp, st) comp.state = st end
function M.set_conflict(v) conflict = v end

-- Deliver a synthetic component event to the probe's registered listener.
function M.fire(event, ctx)
	local cb = M.listeners[event]
	if cb == nil then return false end
	cb(ctx)
	return true
end

-- A chain of `n` nested children under `parent`; element k has id "deep_k" and
-- text "deep node k". Element 10 sits at depth 10 (> MAX_DEPTH 9) on purpose.
function M.chain(parent, n)
	local node = parent
	for k = 1, n do
		local child = make_component("deep_" .. k, { stext = "deep node " .. k })
		node.children = { child }
		node = child
	end
end

function M.fill(parent, n, prefix)
	for k = 1, n do
		parent.children[#parent.children + 1] = make_component((prefix or "leaf_") .. k)
	end
end

-- ---------------------------------------------------------------- engine tree
local ROOT = make_component("root")
local HUD = make_component("hud_battle")
M.root = ROOT
M.hud = HUD
ROOT.children[1] = HUD

-- the hostile-state value: its tostring raises (proves safe_text / pcall walls)
M.hostile_value = setmetatable({}, { __tostring = function() error("hostile tostring") end })

-- -------------------------------------------------------------- engine globals
UIComponent = function(x) return x end

core = {}
function core:get_ui_root() return M.root end
function core:add_listener(name, event, cond, cb, persist)
	M.listener_names[#M.listener_names + 1] = name
	M.listeners[event] = cb
	return true
end

bm = {}
function bm:repeat_callback(fn, ms, name) poll_fn = fn; poll_ms = ms; poll_name = name; return true end
function bm:is_conflict_phase() return conflict end

-- The local player's army: M.local_units is a list of ui-id strings.
function bm:get_scriptunits_for_local_players_army()
	local list = M.local_units or {}
	local obj = {}
	function obj:count() return #list end
	function obj:item(i)
		local id = list[i]
		if id == nil then return nil end
		return { unit = { unique_ui_id = function() return id end } }
	end
	return obj
end

out = function(...) end
