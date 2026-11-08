-- Mock engine additions for the ROUND-14 zz_probe_ui_text smoke test.
-- Executed AFTER mock_ui_prelude_v7.lua and BEFORE the probe.
--
-- Round 14 SEEDS the descent on the DISCOVERED panel path
--   hud_battle > info_panel_parent > info_panel_background > unit_information >
--   info_parent > info_panel > list
-- (each link = the direct child whose Id matches), walks DOWN from `list`
-- (depth 6, budget 300), pairs the stat rows (stat_name -> value_holder/dy_value),
-- then runs a FIXED ladder of common.get_context_value calls: a control
-- (CcoBattleUnit + bare id + Name), CcoUnitDetails/"BattleUnit_1001" with
-- Name / StatList / StatList.Size, CcoUnitStat/"BattleUnit_1001" with
-- DisplayedValue / Name, then the SAME shape for the NON-selected unit
-- ("BattleUnit_1002" and bare "1002"). As in rounds 11-13 the engine's
-- name-lookup helper is BANNED: a LOUD global of that name is installed and
-- COUNTED, so the smoke proves it is never called.
--
-- Scenes:
--   build_r14_scene()  - the real case: the full discovered chain, a `list`
--                        holding row_header_stats + template_stat rows (each with
--                        stat_name + value_holder > dy_value) AND a row identified
--                        only by its stat_name child. The two CONTROLS succeed
--                        (CcoBattleUnit/1001/Name and /1002/Name) but NO new-format
--                        rung returns a value -> no false WIN.
--   build_r14_stopA()  - a SELECTED new-format rung (BattleUnit_1001 StatList.Size)
--                        returns a value -> LADDER A STOPS at rung 3.
--   build_r14_win()    - a NON-selected rung (BattleUnit_1002 StatList.Size) returns
--                        a value -> step 6 STOPS with the loud WIN; step 7 skipped.
--   build_r14_bare()   - the BU_1002 rungs all fail; the BARE id rung
--                        ("1002" StatList.Size) returns a value -> step 7 WIN.
--   build_r14_nolist() - the chain breaks at info_panel_background (missing).
--   build_r14_wide()   - a `list` with 500 children -> the 300-visit walk cuts.

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

-- Build the DISCOVERED chain under ROOT; return the `list` node.
local function build_chain(ROOT, stop_before)
  local names = { "info_panel_parent", "info_panel_background", "unit_information",
                  "info_parent", "info_panel", "list" }
  local hud = M.new("hud_battle", { visible = true })
  M.attach(ROOT, hud)
  local node = hud
  for i = 1, #names do
    if stop_before ~= nil and names[i] == stop_before then break end
    local c = M.new(names[i], { visible = true })
    M.attach(node, c)
    node = c
  end
  return hud, node
end

-- Attach one template_stat row: stat_name (name) + value_holder > dy_value (value).
local function add_row(list, name, value)
  local row = M.new("template_stat")
  M.attach(list, row)
  M.attach(row, M.new("stat_name", { stext = name }))
  local vh = M.new("value_holder")
  M.attach(row, vh)
  M.attach(vh, M.new("dy_value", { stext = value }))
  return row
end

-- The station: the full discovered chain; two controls answer, no new rung does.
function M.build_r14_scene()
  local ROOT = M.root
  M.clear(ROOT)
  local hud, list = build_chain(ROOT)
  M.attach(list, M.new("row_header_stats"))          -- the row block header
  add_row(list, "Melee Defence", "53")               -- row 1
  add_row(list, "Armour", "85")                      -- row 2
  -- row 3: identified ONLY by its stat_name child (the CcoUnitStat* shape)
  local row3 = M.new("CcoUnitStat5974444112")
  M.attach(list, row3)
  M.attach(row3, M.new("stat_name", { stext = "Movement" }))
  local vh3 = M.new("value_holder")
  M.attach(row3, vh3)
  M.attach(vh3, M.new("dy_value", { stext = "5.2" }))
  -- the empty-card holder (not needed for the descent; kept for realism)
  local uid = M.new("unit_id_holder")
  M.attach(ROOT, uid)
  M.attach(uid, M.new("1001"))
  M.attach(uid, M.new("1002"))

  M.local_units = { 1001, 1002 }
  M.gcv_values = {
    ["1001|Name"] = "Karl Franz",       -- LADDER A control (bare id) -> value
    ["1002|Name"] = "Balthasar Gelt",   -- LADDER B control (bare id) -> value
  }
  return { hud = hud, list = list, row3 = row3 }
end

-- A SELECTED new-format rung answers -> LADDER A stops at rung 3.
function M.build_r14_stopA()
  M.build_r14_scene()
  M.gcv_values["BattleUnit_1001|StatList.Size"] = 7
  return true
end

-- A NON-selected new-format rung answers -> step 6 STOPS with the WIN.
function M.build_r14_win()
  M.build_r14_scene()
  M.gcv_values["BattleUnit_1002|StatList.Size"] = 12
  return true
end

-- Only the BARE non-selected id answers -> step 7 WIN.
function M.build_r14_bare()
  M.build_r14_scene()
  M.gcv_values["1002|StatList.Size"] = 9
  return true
end

-- The chain breaks: info_panel_background is missing (step 1 cannot resolve).
function M.build_r14_nolist()
  local ROOT = M.root
  M.clear(ROOT)
  build_chain(ROOT, "info_panel_background")
  M.local_units = { 1001, 1002 }
  M.gcv_values = {}
  return true
end

-- A huge `list` (1 + 1 + 500 = 502 nodes) -> the 300-visit walk must cut.
function M.build_r14_wide()
  local ROOT = M.root
  M.clear(ROOT)
  local hud, list = build_chain(ROOT)
  M.attach(list, M.new("row_header_stats"))
  add_row(list, "Armour", "85")
  for i = 1, 500 do
    M.attach(list, M.new("filler_" .. i))
  end
  M.local_units = { 1001, 1002 }
  M.gcv_values = {
    ["1001|Name"] = "Karl Franz",
    ["1002|Name"] = "Balthasar Gelt",
  }
  return { hud = hud, list = list }
end
