-- Mock engine prelude for the ROUND-4 zz_probe_ui_text smoke test
-- (TARGETED STAT DUMP). Loaded into a lupa Lua runtime BEFORE the probe.
--
-- It is the round-3 prelude (round-3 capture still ships and must keep
-- working) PLUS the extra reads the round-4 stat dump performs:
--   * Visible()/VisibleFromRoot() now answer a MUTABLE per-component flag, so
--     the driver can open/close the "stat panel" and watch the auto trigger,
--   * Bounds(), GetImagePath(i), NumImages(), NumStates(), GetStateByIndex(i),
--   * M.set_visible(comp, v), M.chain_named(parent, n, prefix).
--
-- The round-3 plumbing (listeners, Address, AddScriptEventReporter, local
-- units) is unchanged. UI-state SETTERS (SetText / SetState / ... ) still trip
-- (`trips[]`) so the test fails if the probe ever mutates the UI.

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
	c.visible = (opts.visible ~= false)           -- round 4
	c.visibleroot = opts.visibleroot               -- round 4
	if c.visibleroot == nil then c.visibleroot = c.visible end
	c.img0 = opts.img0
	c.img1 = opts.img1
	c.nimages = opts.nimages
	c.nstates = opts.nstates
	c.states = opts.states
	c.bwidth = opts.bwidth
	c.bheight = opts.bheight

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
	function c:Visible() return self.visible end
	function c:VisibleFromRoot() return self.visibleroot end
	function c:Position() return 11, 22 end
	function c:Bounds() return (self.bwidth or 100), (self.bheight or 50) end
	function c:GetImagePath(i)
		if i == 1 then return self.img1 end
		return self.img0
	end
	function c:NumImages()
		if self.nimages ~= nil then return self.nimages end
		if self.img1 ~= nil then return 2 end
		return 1
	end
	function c:NumStates() return self.nstates or 1 end
	function c:GetStateByIndex(i)
		if self.states == nil then return nil end
		return self.states[i + 1]
	end
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
function M.set_visible(comp, v) comp.visible = v; comp.visibleroot = v end

-- Deliver a synthetic component event to the probe's registered listener.
function M.fire(event, ctx)
	local cb = M.listeners[event]
	if cb == nil then return false end
	cb(ctx)
	return true
end

-- A chain of `n` nested children under `parent`; element k has id "deep_k" and
-- text "deep node k". Element 10 sits at depth 10 (> round-3 MAX_DEPTH 9).
function M.chain(parent, n)
	local node = parent
	for k = 1, n do
		local child = make_component("deep_" .. k, { stext = "deep node " .. k })
		node.children = { child }
		node = child
	end
end

-- A chain with a custom id prefix - so the round-4 deep walk (depth 20) can be
-- told apart from the round-3 walk (depth 9) by a distinctive id.
function M.chain_named(parent, n, prefix)
	local node = parent
	for k = 1, n do
		local child = make_component((prefix or "chain_") .. k,
			{ stext = (prefix or "chain_") .. " depth " .. k })
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
