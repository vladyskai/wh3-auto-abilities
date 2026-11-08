-- Mock engine prelude for the zz_probe_ui_text smoke test.
-- Loaded into a lupa Lua runtime BEFORE the probe. It provides the globals the
-- probe touches (core, UIComponent, bm, out) and a fake UI tree that:
--   * renders a stat value the way the in-game tooltip does ("Base value: 53"),
--     so the probe's STAT-LIKE flag has something real to catch,
--   * includes a component whose tostring() raises, to prove the walk is
--     pcall-walled and continues,
--   * includes a component whose text/property reads raise, to prove each read
--     is pcall'd and recorded as <ERR>,
--   * includes a chain deeper than the depth cap and a fan-out wider than the
--     visit cap, to prove both caps bite,
--   * TRIPs on every setter, so if the probe ever called one the test fails.

trips = {}
periodic_fn = nil
periodic_ms = nil
periodic_name = nil

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
	c.prop = opts.prop
	c.stext_raises = opts.stext_raises
	c.tip_raises = opts.tip_raises
	c.prop_raises = opts.prop_raises

	function c:Id() return self.id end
	function c:CurrentState() return self.state end
	function c:GetStateText()
		if self.stext_raises then error("mock: GetStateText raises") end
		return self.stext
	end
	function c:GetTooltipText()
		if self.tip_raises then error("mock: GetTooltipText raises") end
		return self.tip
	end
	function c:GetProperty(name)
		if self.prop_raises then error("mock: GetProperty raises") end
		if self.prop == nil then return nil end
		return self.prop[name]
	end
	function c:Visible() return true end
	function c:VisibleFromRoot() return true end
	function c:Position() return 11, 22 end
	function c:ChildCount() return #self.children end
	function c:Find(i)
		if type(i) == "number" then return self.children[i + 1] end
		return find_recursive(self, i)          -- recursive search by id
	end
	function c:FindByScriptTag(tag) return find_recursive(self, tag) end
	function c:SequentialFind(a, b) return find_recursive(self, a) end

	for _, n in ipairs({ "SetText", "SetStateText", "SetProperty", "SetTooltipText",
	                     "SetState", "Layout", "CreateComponent", "Destroy" }) do
		c[n] = trip(n)
	end
	return c
end

-- a value whose tostring() raises: proves log_component is pcall-walled
local hostile_state = setmetatable({}, { __tostring = function() error("hostile tostring") end })

local card = make_component("101", { children = {
	make_component("stat_melee_defence", { stext = "Melee Defence", tip = "Base value: 53" }),
	make_component("stat_armour", { stext = "Armour", prop = { armour = 53 } }),
} })

local deep_chain = nil
do
	local node = make_component("deep_1")
	deep_chain = node
	for k = 2, 12 do
		local child = make_component("deep_" .. k)
		if k == 10 then child.id = "too_deep" end     -- depth 10 > MAX_DEPTH(9)
		node.children = { child }
		node = child
	end
end

local big_children = {}
for k = 1, 1600 do big_children[k] = make_component("leaf_" .. k) end

local hud = make_component("hud_battle", { children = {
	card,
	make_component("hostile", { state = hostile_state }),
	make_component("after_hostile"),
	make_component("raises_reads", { stext_raises = true, tip_raises = true, prop_raises = true }),
	deep_chain,
} })

local uinfo = make_component("unit_information", { children = {
	make_component("stat_name", { stext = "Melee Defence", tip = "Base value: 53 / Hold the Line!: 5" }),
} })

local tiproot = make_component("tooltip_ai_stats_modifier", { children = {
	make_component("value_holder", { stext = "53" }),
} })

local big_root = make_component("big_root", { children = big_children })

local ROOT = make_component("root", { children = { hud, uinfo, tiproot, big_root } })
ROOT.children[1].id = "hud_battle"

-- ------------------------------ engine globals -----------------------------
UIComponent = function(x) return x end

core = {}
function core:get_ui_root() return ROOT end

local su = { unit = { unique_ui_id = function() return 101 end } }
local coll = {}
function coll:count() return 1 end
function coll:item(i) return su end

bm = {}
function bm:repeat_callback(fn, ms, name) periodic_fn = fn; periodic_ms = ms; periodic_name = name; return true end
function bm:get_scriptunits_for_local_players_army() return coll end

out = function(...) end
