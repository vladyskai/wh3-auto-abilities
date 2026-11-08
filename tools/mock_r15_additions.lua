-- Mock engine additions for the ROUND-15 zz_probe_ui_text smoke test.
-- Executed AFTER mock_ui_prelude_v7.lua and mock_r14_additions.lua, BEFORE the probe.
--
-- Round 15 (the final experiment) needs three things the earlier scenes lack:
--   1. the DISCOVERED panel chain with stat rows that carry comparison children
--      (label_compare + comparison_arrow, plus one label_compare nested one level
--      deeper via a comp_holder child) - so step A's dump and the tracked fields
--      (label_compare text, compare-named text, row context id, vis) exist;
--   2. the cards panel (review_DY + two UnitCard components, 1001 selected,
--      1002 not) so a NON-selected hover target exists;
--   3. for the effect world, wrappers that make the TARGET card's
--      SimulateMouseOn/Off CHANGE the tracked values - the label_compare text
--      (+2 -> +7 -> +2) and the row's CcoUnitStat context id
--      (CTXID:... -> BattleUnit_1002 -> CTXID:...) - modelling the
--      user-observed engine behaviour. The wrappers count nothing themselves;
--      the prelude's own recorded SimulateMouseOn/Off run first (orig calls).
--
-- The plain scene (no wrappers) is the NEGATIVE world: nothing changes during
-- any pass, so the verdict must say 'no invisible exposure' and never raise WIN.

M.r15_ctx_override = nil    -- the ctx id the wrapped row answers while set
M.sim_effect = false        -- keep the prelude's own hover effect OFF here

local function r15_chain(ROOT)
  local names = { "info_panel_parent", "info_panel_background", "unit_information",
                  "info_parent", "info_panel", "list" }
  local hud = M.new("hud_battle", { visible = true })
  M.attach(ROOT, hud)
  local node = hud
  for i = 1, #names do
    local c = M.new(names[i], { visible = true })
    M.attach(node, c)
    node = c
  end
  return hud, node
end

-- One template_stat row: stat_name(0), value_holder>dy_value(1), bar_base(2),
-- bar_mod(3), label_compare(4), optional comparison_arrow(5).
local function r15_row(list, name, value, lc_text, lc_vis, with_arrow)
  local row = M.new("template_stat")
  M.attach(list, row)
  M.attach(row, M.new("stat_name", { stext = name }))
  local vh = M.new("value_holder")
  M.attach(row, vh)
  M.attach(vh, M.new("dy_value", { stext = value }))
  M.attach(row, M.new("bar_base"))
  M.attach(row, M.new("bar_mod"))
  local lc = M.new("label_compare", { stext = lc_text, visible = lc_vis })
  M.attach(row, lc)
  if with_arrow then
    M.attach(row, M.new("comparison_arrow", { stext = nil, visible = false }))
  end
  return row, lc
end

-- The shared scene: full chain + 3 rows (the third identified only by its
-- stat_name child and carrying a NESTED label_compare) + the cards panel.
function M.build_r15_scene_base()
  local ROOT = M.root
  M.clear(ROOT)
  M.r15_ctx_override = nil
  M.sim_effect = false
  local hud, list = r15_chain(ROOT)
  M.attach(list, M.new("row_header_stats"))
  local row1, lc1 = r15_row(list, "Range", "42", "+2", true, true)     -- row 1
  local row2, lc2 = r15_row(list, "Armour", "85", nil, false, false)   -- row 2
  -- row 3: the CcoUnitStat* id shape + a label_compare ONE LEVEL DEEPER
  local row3 = M.new("CcoUnitStat5974444112")
  M.attach(list, row3)
  M.attach(row3, M.new("stat_name", { stext = "Movement" }))
  local vh3 = M.new("value_holder")
  M.attach(row3, vh3)
  M.attach(vh3, M.new("dy_value", { stext = "5.2" }))
  local holder = M.new("comp_holder")
  M.attach(row3, holder)
  local lc3 = M.new("label_compare", { stext = "+1", visible = true })
  M.attach(holder, lc3)
  -- the cards panel: review_DY lives under hud_battle; 1001 is SELECTED.
  local review = M.new("review_DY")
  M.attach(hud, review)
  local c1 = M.new("1001", { callback_id = "UnitCard", state = "selected" })
  local c2 = M.new("1002", { callback_id = "UnitCard", state = "active" })
  M.attach(review, c1)
  M.attach(review, c2)
  M.local_units = { 1001, 1002 }
  M.gcv_values = {
    ["1001|Name"] = "Karl Franz",
    ["1002|Name"] = "Balthasar Gelt",
  }
  return { row1 = row1, lc1 = lc1, row2 = row2, lc2 = lc2, row3 = row3, lc3 = lc3,
           holder = holder, c1 = c1, c2 = c2, review = review, hud = hud, list = list }
end

-- The EFFECT world: hovering card 1002 (the non-selected target) changes row 1's
-- label_compare text and the row's CcoUnitStat context id; Off reverts both.
function M.build_r15_scene_effect()
  local s = M.build_r15_scene_base()
  local card = s.c2
  local on0, off0 = card.SimulateMouseOn, card.SimulateMouseOff
  card.SimulateMouseOn = function(self)
    on0(self)
    self.r15_on = true
    s.lc1.stext = "+7"
    M.r15_ctx_override = "BattleUnit_1002"
  end
  card.SimulateMouseOff = function(self)
    off0(self)
    self.r15_on = false
    s.lc1.stext = "+2"
    M.r15_ctx_override = nil
  end
  -- row1's GetContextObjectId consults the override for CcoUnitStat ONLY.
  local ctx0 = s.row1.GetContextObjectId
  s.row1.GetContextObjectId = function(self, type_id)
    local v = ctx0(self, type_id)
    if type_id == "CcoUnitStat" and M.r15_ctx_override ~= nil then
      return M.r15_ctx_override
    end
    return v
  end
  return s
end
