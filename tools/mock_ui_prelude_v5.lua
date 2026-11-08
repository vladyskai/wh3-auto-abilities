-- Mock engine prelude for the ROUND-5 zz_probe_ui_text smoke test
-- (THE CROSS-UNIT EXPERIMENT). Loaded into a lupa Lua runtime BEFORE the probe.
--
-- It is the round-4 prelude PLUS the extra engine surface round 5 touches:
--   * component reads: CallbackId()
--   * context objects: GetContextObject(type_id), GetContextObjectId(type_id),
--     SetContextObject(v) - all RECORDED (they are the experiment's own calls,
--     not UI-state setters, so they do NOT trip); a driver-armed effect can
--     make one SetContextObject call change a dy_value text, and setting the
--     component's OWN CcoUnitDetails object back restores it,
--   * the global cco(type, id) constructor (vanilla lib_bsu.lua shape),
--   * mouse simulation: SimulateMouseOn()/SimulateMouseOff() (recorded, never
--     trip; a per-component raise switch exists for the hostile world),
--   * battle_unit:select_in_ui() on the army's units, which ALSO models the
--     engine effect: the matching card becomes "selected", the others lose it.
--
-- UI-state SETTERS (SetText / SetState / ... ) still trip (`trips[]`) so the
-- test fails if the probe ever mutates the UI through them.

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

-- First dy_value node under a component (for the driver-armed context effect).
local function mock_dy_first(comp)
	local found = nil
	local function walk(c)
		if found ~= nil then return end
		if c.id == "dy_value" then found = c; return end
		for _, k in ipairs(c.children or {}) do walk(k) end
	end
	walk(comp)
	return found
end

local function mock_set_first_dy(comp, v)
	local dy = mock_dy_first(comp)
	if dy ~= nil then dy.stext = v end
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
	c.visible = (opts.visible ~= false)
	c.visibleroot = opts.visibleroot
	if c.visibleroot == nil then c.visibleroot = c.visible end
	c.img0 = opts.img0
	c.img1 = opts.img1
	c.nimages = opts.nimages
	c.nstates = opts.nstates
	c.states = opts.states
	c.bwidth = opts.bwidth
	c.bheight = opts.bheight
	-- round 5
	c.callback_id = opts.callback_id
	c.getctx_raises = opts.getctx_raises
	c.getctxid_raises = opts.getctxid_raises
	c.setctx_raises = opts.setctx_raises
	c.sim_raises = opts.sim_raises
	c.ctx_by_type = nil
	c.mouse_on = false

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

	-- ROUND 5: the context-object surface + CallbackId + mouse simulation.
	-- These are RECORDED, never trips: they are the experiment's own calls.
	function c:CallbackId()
		if self.callback_id == nil then return nil end
		return self.callback_id
	end
	function c:GetContextObject(type_id)
		M.getctx_calls = M.getctx_calls + 1
		M.calls[#M.calls + 1] = "GetContextObject:" .. tostring(self.id) .. ":" .. tostring(type_id)
		if self.getctx_raises then error("mock: GetContextObject raises") end
		self.ctx_by_type = self.ctx_by_type or {}
		if self.ctx_by_type[type_id] == nil then
			local o = { _type = type_id, _id = self.id }
			self.ctx_by_type[type_id] = setmetatable(o, {
				__tostring = function(x)
					return "CCO(" .. tostring(x._type) .. "):" .. tostring(x._id)
				end })
		end
		return self.ctx_by_type[type_id]
	end
	function c:GetContextObjectId(type_id)
		M.getctxid_calls = M.getctxid_calls + 1
		M.calls[#M.calls + 1] = "GetContextObjectId:" .. tostring(self.id) .. ":" .. tostring(type_id)
		if self.getctxid_raises then error("mock: GetContextObjectId raises") end
		return "CTXID:" .. tostring(self.id) .. ":" .. tostring(type_id)
	end
	function c:SetContextObject(v)
		M.setctx_calls = M.setctx_calls + 1
		M.calls[#M.calls + 1] = "SetContextObject:" .. tostring(self.id)
		M.setctx_log[#M.setctx_log + 1] = { id = self.id, value = v }
		if self.setctx_raises then error("mock: SetContextObject raises") end
		-- driver-armed effect: the Nth set call changes the panel's first value
		if M.setctx_effect_at ~= nil and M.setctx_calls == M.setctx_effect_at then
			mock_set_first_dy(self, "99")
		end
		-- setting the component's OWN CcoUnitDetails object back restores it
		local own = self.ctx_by_type and self.ctx_by_type["CcoUnitDetails"]
		if v ~= nil and own ~= nil and v == own then
			mock_set_first_dy(self, M.dy_original)
		end
	end
	function c:SimulateMouseOn()
		M.sim_on_calls = M.sim_on_calls + 1
		M.calls[#M.calls + 1] = "SimulateMouseOn:" .. tostring(self.id)
		if self.sim_raises then error("mock: SimulateMouseOn raises") end
		self.mouse_on = true
	end
	function c:SimulateMouseOff()
		M.sim_off_calls = M.sim_off_calls + 1
		M.calls[#M.calls + 1] = "SimulateMouseOff:" .. tostring(self.id)
		if self.sim_raises then error("mock: SimulateMouseOff raises") end
		self.mouse_on = false
	end

	for _, n in ipairs({ "SetText", "SetStateText", "SetProperty", "SetTooltipText",
	                     "SetState", "Layout", "CreateComponent", "Destroy",
	                     "MoveTo", "SetVisible", "SetAlpha", "Resize",
	                     "SetDockOffset", "SetDockingPoint" }) do
		c[n] = trip(n)
	end
	if c.callback_id == "UnitCard" then
		M.card_registry[#M.card_registry + 1] = c
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
-- round 5 recorders
M.calls = {}
M.card_registry = {}
M.getctx_calls = 0
M.getctxid_calls = 0
M.setctx_calls = 0
M.setctx_log = {}
M.select_calls = 0
M.select_log = {}
M.sim_on_calls = 0
M.sim_off_calls = 0
M.cco_calls = 0
M.setctx_effect_at = nil
M.dy_original = "42"

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

-- A chain of `n` nested children under `parent`.
function M.chain(parent, n)
	local node = parent
	for k = 1, n do
		local child = make_component("deep_" .. k, { stext = "deep node " .. k })
		node.children = { child }
		node = child
	end
end

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

-- The vanilla script-side CCO constructor: cco("CcoBattleUnit", ui_id) fed to
-- UIC:SetContextObject (lib_bsu.lua's ping icon does exactly this).
function cco(type_name, id)
	M.cco_calls = M.cco_calls + 1
	M.calls[#M.calls + 1] = "cco:" .. tostring(type_name) .. ":" .. tostring(id)
	local o = { _type = type_name, _id = id }
	return setmetatable(o, {
		__tostring = function(x)
			return "CCO(" .. tostring(x._type) .. "):" .. tostring(x._id)
		end })
end

bm = {}
function bm:repeat_callback(fn, ms, name) poll_fn = fn; poll_ms = ms; poll_name = name; return true end
function bm:is_conflict_phase() return conflict end

-- The local player's army: M.local_units is a list of ui ids (NUMBERS, so the
-- probe's "id as number" vs "id as text" candidates are visibly different).
function bm:get_scriptunits_for_local_players_army()
	local list = M.local_units or {}
	local obj = {}
	function obj:count() return #list end
	function obj:item(i)
		local id = list[i]
		if id == nil then return nil end
		local unit = {}
		unit.unique_ui_id = function() return id end
		unit.select_in_ui = function()
			M.select_calls = M.select_calls + 1
			M.calls[#M.calls + 1] = "select_in_ui:" .. tostring(id)
			if M.select_raises then error("mock: select_in_ui raises") end
			M.select_log[#M.select_log + 1] = id
			-- model the engine: this unit's card becomes selected, the others not
			for _, card in ipairs(M.card_registry or {}) do
				if card.id == tostring(id) then
					card.state = "selected"
				elseif card.state ~= nil and string.sub(card.state, 1, 8) == "selected" then
					card.state = "active"
				end
			end
		end
		return { unit = unit }
	end
	return obj
end

out = function(...) end
