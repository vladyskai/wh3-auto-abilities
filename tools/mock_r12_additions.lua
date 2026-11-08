-- Mock engine additions for the ROUND-12 zz_probe_ui_text smoke test.
-- Executed AFTER mock_ui_prelude_v7.lua and BEFORE the probe.
--
-- Round 12 BANS the engine's name-lookup helper entirely, so (as in round 11)
-- a LOUD global of that name is installed: if the probe ever calls it the call
-- is COUNTED (and raises), so the smoke proves the banned call is never made.
--
-- It builds four scenes:
--   build_r12_scene() - the real case: under unit_id_holder sit NUMERIC unit-id
--                       nodes (1001/1002/1003); the SELECTED unit 1001 carries
--                       modular_parent > health_and_stats_parent > dynamic_stats >
--                       template_stat rows, with ONE row's stat_name/dy_value at
--                       DEPTH 8 (the round-11 cap of 4 missed all of it).
--   build_r12_deep()  - a stat_name one level BEYOND the depth-8 cap (depth 10)
--                       must NOT be located.
--   build_r12_wide()  - a 930-node fan-out under one unit-id node must be cut off
--                       at the 800-visit budget.
--   build_r12_noseed()- unit_id_holder with NO numeric children: step 3 aborts
--                       cleanly (no seeds).

M.fu_calls = 0        -- calls to the BANNED name-lookup global - must stay 0
M.uic_bool_calls = 0  -- UIComponent(<boolean>) - the round-9 crash - must stay 0

-- the BANNED global: counted, and loud so a real call is impossible to miss.
find_uicomponent = function(...)
  M.fu_calls = M.fu_calls + 1
  error("mock: find_uicomponent was CALLED - it is BANNED in this probe")
end

UIComponent = function(x)
  if type(x) == "boolean" then
    M.uic_bool_calls = M.uic_bool_calls + 1
    error("mock: UIComponent(boolean) - THE ROUND-9 CRASH")
  end
  return x
end

-- walk every component under a node (path ignored; used to stamp a default
-- GetContextObjectId that answers nil unless a component overrides it).
local function walk(node, fn)
  if node == nil then return end
  fn(node)
  for _, ch in ipairs(node.children or {}) do walk(ch, fn) end
end

local function nil_ctxid(self, tid)
  M.getctxid_calls = M.getctxid_calls + 1
  return nil
end

-- The station: ten top-level roots, the unit-id holder with three NUMERIC
-- children, the selected unit's panel (with a depth-8 row), and the two
-- non-selected units' shallow modular_parents.
function M.build_r12_scene()
  local ROOT = M.root
  M.clear(ROOT)
  M.attach(ROOT, M.new("hud_battle"))

  local uid = M.new("unit_id_holder")
  M.attach(ROOT, uid)
  local u1 = M.new("1001"); M.attach(uid, u1)   -- the SELECTED unit
  local u2 = M.new("1002"); M.attach(uid, u2)   -- NON-selected
  local u3 = M.new("1003"); M.attach(uid, u3)   -- NON-selected

  -- the SELECTED unit's panel: unit_id_holder/1001/modular_parent (10 children)
  local mp = M.new("modular_parent"); M.attach(u1, mp)
  for i = 1, 7 do M.attach(mp, M.new("filler_" .. i)) end
  local hsp = M.new("health_and_stats_parent"); M.attach(mp, hsp)   -- depth 3
  local ds = M.new("dynamic_stats"); M.attach(hsp, ds)              -- depth 4
  local row1 = M.new("template_stat"); M.attach(ds, row1)           -- depth 5
  M.attach(row1, M.new("stat_name", { stext = "Armour" }))          -- depth 6
  local vh1 = M.new("value_holder"); M.attach(row1, vh1)            -- depth 6
  M.attach(vh1, M.new("dy_value", { stext = "85" }))                -- depth 7
  local row2 = M.new("template_stat"); M.attach(ds, row2)
  M.attach(row2, M.new("stat_name", { stext = "Leadership" }))
  local vh2 = M.new("value_holder"); M.attach(row2, vh2)
  M.attach(vh2, M.new("dy_value", { stext = "60" }))

  -- one DEEP row: template_stat at depth 7, its stat_name/dy_value at depth 8 -
  -- proof the descent reaches depth 8 (the round-11 cap of 4 missed all this)
  local d3 = M.new("deep3"); M.attach(mp, d3)
  local d4 = M.new("deep4"); M.attach(d3, d4)
  local d5 = M.new("deep5"); M.attach(d4, d5)
  local d6 = M.new("deep6"); M.attach(d5, d6)
  local deeprow = M.new("template_stat"); M.attach(d6, deeprow)     -- depth 7
  M.attach(deeprow, M.new("stat_name", { stext = "Deep Name" }))    -- depth 8
  M.attach(deeprow, M.new("dy_value", { stext = "777" }))           -- depth 8

  -- the non-selected units: a modular_parent with children but NO stat rows
  local mp2 = M.new("modular_parent"); M.attach(u2, mp2)
  for i = 1, 10 do M.attach(mp2, M.new("bf_" .. i)) end
  local mp3 = M.new("modular_parent"); M.attach(u3, mp3)
  for i = 1, 10 do M.attach(mp3, M.new("bf_" .. i)) end

  -- pad the roots out (unit_id_holder is one of ten, as in the field)
  M.attach(ROOT, M.new("tactical_map"))
  M.attach(ROOT, M.new("left"))
  M.attach(ROOT, M.new("right"))
  M.attach(ROOT, M.new("tactical_hud"))
  M.attach(ROOT, M.new("menu_bar"))
  M.attach(ROOT, M.new("panel_manager"))
  M.attach(ROOT, M.new("battle_orders"))
  M.attach(ROOT, M.new("watermark_square"))

  -- context ids: by default NO component answers (nil), so step 5's reads prove
  -- what the PANEL reports. dynamic_stats answers CcoUnitDetails/CcoUnitStat;
  -- the unit-id node answers CcoBattleUnit with its own ui id.
  walk(ROOT, function(c) c.GetContextObjectId = nil_ctxid end)
  ds.GetContextObjectId = function(self, tid)
    M.getctxid_calls = M.getctxid_calls + 1
    if tid == "CcoUnitDetails" then return "5001" end
    if tid == "CcoUnitStat" then return "5101" end
    return nil
  end
  row1.GetContextObjectId = function(self, tid)
    M.getctxid_calls = M.getctxid_calls + 1
    if tid == "CcoUnitDetails" then return "5002" end
    return nil
  end
  u1.GetContextObjectId = function(self, tid)
    M.getctxid_calls = M.getctxid_calls + 1
    if tid == "CcoBattleUnit" then return "1001" end
    return nil
  end

  M.local_units = { 1001, 1002 }
  M.gcv_values = {
    ["StatList.Size"] = 3,
    ["5001|StatList.Size"] = 3,
    ["1002|StatList.Size"] = 3,
  }
  return { u1 = u1, u2 = u2, u3 = u3, ds = ds, row1 = row1 }
end

-- a stat_name BEYOND the depth-8 cap: unit_id_holder(d0) > 1001(d1) > lvl2..
-- lvl9 (d2..d9) > stat_name (d10). The descent must reach lvl8 but NOT lvl9.
function M.build_r12_deep()
  local ROOT = M.root
  M.clear(ROOT)
  local uid = M.new("unit_id_holder"); M.attach(ROOT, uid)
  local u1 = M.new("1001"); M.attach(uid, u1)
  local node = u1
  for i = 2, 9 do
    local c = M.new("lvl" .. i); M.attach(node, c); node = c
  end
  M.attach(node, M.new("stat_name", { stext = "TOO DEEP" }))   -- depth 10
  M.local_units = { 1001, 1002 }
end

-- a huge fan-out under one unit-id node: 1 + 30 + 900 = 931 nodes; the 800-visit
-- budget must cut step 3 off.
function M.build_r12_wide()
  local ROOT = M.root
  M.clear(ROOT)
  local uid = M.new("unit_id_holder"); M.attach(ROOT, uid)
  local u1 = M.new("1001"); M.attach(uid, u1)
  for i = 1, 30 do
    local c = M.new("c" .. i); M.attach(u1, c)
    for j = 1, 30 do M.attach(c, M.new("g" .. i .. "_" .. j)) end
  end
  M.local_units = { 1001, 1002 }
end

-- unit_id_holder with NO numeric children: step 2 seeds nothing, step 3 aborts.
function M.build_r12_noseed()
  local ROOT = M.root
  M.clear(ROOT)
  local uid = M.new("unit_id_holder"); M.attach(ROOT, uid)
  M.attach(uid, M.new("not_a_number"))    -- the holder exists, but no ui-id seed
  M.local_units = { 1001, 1002 }
end
