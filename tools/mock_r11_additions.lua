-- Mock engine additions for the ROUND-11 zz_probe_ui_text smoke test.
-- Executed AFTER mock_ui_prelude_v7.lua and BEFORE the probe.
--
-- Round 11 BANS the engine's name-lookup helper entirely, so there is no
-- find_uicomponent mock to build - instead a LOUD global of that name is
-- installed: if the probe ever calls it the call is COUNTED (and raises), so the
-- smoke proves the banned call is never made.
--
-- It builds three scenes:
--   build_r11_scene()  - the real case: the unit-INFO panel sits under a
--                        hint-tagged root (panel_manager > unit_information >
--                        health_and_stats_parent > dynamic_stats > template_stat),
--                        reachable by the two-level descent; the unit CARDS live
--                        under battle_orders/cards_panel/review_DY.
--   build_r11_deep()   - a stat row one level BEYOND the depth cap (depth 5) must
--                        NOT be located (the descent stops at depth 4).
--   build_r11_wide()   - a huge fan-out under one hinted root must be cut off at
--                        the 400-visit budget.

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

-- the unit-INFO panel: dynamic_stats reachable at depth 4 via panel_manager.
function M.build_r11_scene()
  local ROOT = M.root
  M.clear(ROOT)
  local hud = M.new("hud_battle")
  M.attach(ROOT, hud)
  M.attach(hud, M.new("hud_center_docker"))
  M.attach(hud, M.new("army_ability_parent"))

  local uid = M.new("unit_id_holder")
  M.attach(ROOT, uid)
  M.attach(uid, M.new("1001"))
  M.attach(uid, M.new("1002"))
  M.attach(uid, M.new("1003"))

  M.attach(ROOT, M.new("tactical_map"))
  M.attach(ROOT, M.new("left"))
  M.attach(ROOT, M.new("right"))
  M.attach(ROOT, M.new("tactical_hud"))
  M.attach(ROOT, M.new("menu_bar"))

  local pm = M.new("panel_manager")
  M.attach(ROOT, pm)
  local UI = M.new("unit_information")
  M.attach(pm, UI)
  local HSP = M.new("health_and_stats_parent")
  M.attach(UI, HSP)
  local DS = M.new("dynamic_stats")
  M.attach(HSP, DS)
  local row = M.new("template_stat")
  M.attach(DS, row)
  M.attach(row, M.new("stat_name", { stext = "Armour" }))
  local vh = M.new("value_holder")
  M.attach(row, vh)
  M.attach(vh, M.new("dy_value", { stext = "85" }))
  -- a second row, so step 4's dynamic_stats child scan is exercised
  local row2 = M.new("template_stat")
  M.attach(DS, row2)
  M.attach(row2, M.new("stat_name", { stext = "Leadership" }))
  local vh2 = M.new("value_holder")
  M.attach(row2, vh2)
  M.attach(vh2, M.new("dy_value", { stext = "60" }))

  local bo = M.new("battle_orders")
  M.attach(ROOT, bo)
  local cp = M.new("cards_panel")
  M.attach(bo, cp)
  local review = M.new("review_DY")
  M.attach(cp, review)
  M.attach(review, M.new("1001", { callback_id = "UnitCard", state = "selected" }))
  M.attach(review, M.new("1002", { callback_id = "UnitCard", state = "active" }))

  M.attach(ROOT, M.new("watermark_square"))
  M.local_units = { 1001, 1002 }
  M.gcv_values = { ["StatList.Size"] = 3, ["1002|StatList.Size"] = 3 }
  return { hud = hud, ui = UI, ds = DS, row = row, row2 = row2 }
end

-- a stat row BEYOND the depth cap: unit_id_holder(d1) > unit_z(d2) > aaa(d3) >
-- bbb(d4) > stat_name(d5, "DEEP"). The descent must reach bbb but NOT stat_name.
function M.build_r11_deep()
  local ROOT = M.root
  M.clear(ROOT)
  local uid = M.new("unit_id_holder")
  M.attach(ROOT, uid)
  local uz = M.new("unit_z")
  M.attach(uid, uz)
  local aaa = M.new("aaa")
  M.attach(uz, aaa)
  local bbb = M.new("bbb")
  M.attach(aaa, bbb)
  M.attach(bbb, M.new("stat_name", { stext = "DEEP" }))
  M.local_units = { 1001, 1002 }
end

-- a huge fan-out under one hinted root: 30 children x 30 grandchildren = 930 -
-- the 400-visit budget must cut the step off.
function M.build_r11_wide()
  local ROOT = M.root
  M.clear(ROOT)
  local tm = M.new("tactical_map")
  M.attach(ROOT, tm)
  for i = 1, 30 do
    local c = M.new("c" .. i)
    M.attach(tm, c)
    for j = 1, 30 do
      M.attach(c, M.new("g" .. i .. "_" .. j))
    end
  end
  M.local_units = { 1001, 1002 }
end
