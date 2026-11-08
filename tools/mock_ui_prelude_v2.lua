-- Mock engine prelude for the ROUND-2 zz_probe_ui_text smoke test
-- (continuous capture). Loaded into a lupa Lua runtime BEFORE the probe.
--
-- It provides the globals the probe touches (core, UIComponent, bm, out) and a
-- MUTABLE UI tree the Python driver can reshape between polls:
--   * M.hud starts EMPTY (proves empty-tree polls are suppressed),
--   * M.new / M.attach / M.set_text / M.set_state / M.clear / M.fill let the
--     driver add a component with text, change its text, or fan the tree out,
--   * every SETTER trips (`trips[]`) so the test fails if the probe calls one,
--   * a component with a hostile CurrentState (tostring raises) proves the
--     pcall wall, and a component whose GetStateText raises proves a raising
--     read is recorded as <ERR>, not fatal.

trips = {}
poll_fn = nil
poll_ms = nil
poll_name = nil
conflict = true

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

	for _, n in ipairs({ "SetText", "SetStateText", "SetProperty", "SetTooltipText",
	                     "SetState", "Layout", "CreateComponent", "Destroy" }) do
		c[n] = trip(n)
	end
	return c
end

-- ------------------------------------------------------------------ controls
M = {}

function M.new(id, opts) return make_component(id, opts) end
function M.attach(parent, child) parent.children[#parent.children + 1] = child end
function M.clear(parent) parent.children = {} end
function M.set_text(comp, stext, tip) comp.stext = stext; comp.tip = tip end
function M.set_state(comp, st) comp.state = st end

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

bm = {}
function bm:repeat_callback(fn, ms, name) poll_fn = fn; poll_ms = ms; poll_name = name; return true end
function bm:is_conflict_phase() return conflict end

out = function(...) end
