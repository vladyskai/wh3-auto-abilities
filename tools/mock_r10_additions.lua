-- Mock engine additions for the ROUND-10 zz_probe_ui_text smoke test.
-- Executed AFTER mock_ui_prelude_v7.lua and BEFORE the probe. It supplies the
-- two things round 10 needs and round 7/8 did not:
--   * find_uicomponent(parent_uic, name, ...) - the VANILLA BATTLE shape - which
--     returns FALSE (not nil) on a miss. This is the round-9 trap.
--   * UIComponent(boolean) is made LOUD: it counts the call and raises, so the
--     smoke fails if the probe ever wraps find_uicomponent's FALSE.
-- It also builds the R10 scene: the unit CARDS live under battle_orders (a
-- SIBLING of hud_battle) and the unit-INFO panel lives under battle_orders too,
-- so a hud_battle walk MISSES the panel and only the UI-root enumeration finds it.

M.uic_bool_calls = 0        -- calls to UIComponent(false/true) - must stay 0
M.fu_calls = 0
M.fu_return_false = false   -- when true, find_uicomponent ALWAYS returns false

local function fu_find(node, id)
  if node == nil then return nil end
  if node.id == id then return node end
  for _, c in ipairs(node.children or {}) do
    local hit = fu_find(c, id)
    if hit ~= nil then return hit end
  end
  return nil
end

-- find_uicomponent(parent_uic, name1, name2, ...) - vanilla lib_common shape.
-- FALSE on a miss (NOT nil), exactly like the shipped _lib/lib_common.lua.
find_uicomponent = function(parent, ...)
  M.fu_calls = M.fu_calls + 1
  if M.fu_return_false then return false end
  local names = { ... }
  local cur = parent
  if type(parent) ~= "table" then          -- vanilla: a non-uic first arg is a NAME
    local all = { parent }                 -- (the search then starts at the UI root)
    for i = 1, #names do all[#all + 1] = names[i] end
    names = all
    cur = M.root
  end
  for i = 1, #names do
    cur = fu_find(cur, names[i])
    if cur == nil then return false end
  end
  if cur == nil then return false end
  return cur
end

-- The round-9 crash in one line: UIComponent(<boolean>).
UIComponent = function(x)
  if type(x) == "boolean" then
    M.uic_bool_calls = M.uic_bool_calls + 1
    error("mock: UIComponent(boolean) - THE ROUND-9 CRASH")
  end
  return x
end

-- The R10 scene. hud_battle holds the CARDS; the info panel is a sibling.
function M.build_r10_scene()
  local ROOT = M.root
  local BO = M.new("battle_orders")
  M.attach(ROOT, BO)
  M.attach(ROOT, M.new("army_ability_parent"))
  M.attach(ROOT, M.new("porthole_parent"))
  M.attach(ROOT, M.new("hud_center_docker"))
  local cards_panel = M.new("cards_panel")
  M.attach(BO, cards_panel)
  local review = M.new("review_DY")
  M.attach(cards_panel, review)
  M.attach(review, M.new("1001", { callback_id = "UnitCard", state = "selected" }))
  M.attach(review, M.new("1002", { callback_id = "UnitCard", state = "active" }))
  -- the unit-info panel: a SIBLING of hud_battle (under battle_orders)
  local UI = M.new("unit_information")
  M.attach(BO, UI)
  local DS = M.new("dynamic_stats")
  M.attach(UI, DS)
  local row = M.new("template_stat")
  M.attach(DS, row)
  M.attach(row, M.new("stat_name", { stext = "Armour" }))
  M.attach(row, M.new("dy_value", { stext = "85" }))
  M.local_units = { 1001, 1002 }
  return { ui = UI, ds = DS, row = row }
end

-- A minimal scene for the disarm checks: cards only, no info panel.
function M.build_r10_bare()
  local ROOT = M.root
  local BO = M.new("battle_orders")
  M.attach(ROOT, BO)
  local review = M.new("review_DY")
  M.attach(BO, review)
  M.attach(review, M.new("1001", { callback_id = "UnitCard", state = "selected" }))
  M.attach(review, M.new("1002", { callback_id = "UnitCard", state = "active" }))
  M.local_units = { 1001, 1002 }
end
