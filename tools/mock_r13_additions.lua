-- Mock engine additions for the ROUND-13 zz_probe_ui_text smoke test.
-- Executed AFTER mock_ui_prelude_v7.lua and BEFORE the probe.
--
-- Round 13 descends EVERY top-level UI root that has children (priority
-- hud_battle, panel_manager, under_advisor_docker, left, right, tactical_hud,
-- menu_bar, then the rest) and hunts the STABLE id PREFIX `CcoUnitStat`
-- (case-insensitive) as well as the structural names. As in rounds 11/12 the
-- engine's name-lookup helper is BANNED: a LOUD global of that name is installed
-- and COUNTED, so the smoke proves it is never called.
--
-- Scenes:
--   build_r13_scene() - the real case: hud_battle (vis=true) holds the panel
--                       (health_and_stats_parent > dynamic_stats > template_stat
--                       rows), including a CcoUnitStat*-PREFIXED row in BOTH cases
--                       (lowercase + mixed case). unit_id_holder holds the numeric
--                       cards (1001/1002). left/right/tactical_hud are HIDDEN but
--                       have children and must STILL be descended (the panel is
--                       visibly on screen while those roots read vis=false).
--   build_r13_deep()  - a CcoUnitStat* node one level BEYOND the depth-8 cap.
--   build_r13_wide()  - a 1641-node fan-out under hud_battle cut off at 1200 visits.
--   build_r13_nohit() - roots with children but NO prefix and NO structural ids.

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

local function walk(node, fn)
  if node == nil then return end
  fn(node)
  for _, ch in ipairs(node.children or {}) do walk(ch, fn) end
end

local function nil_ctxid(self, tid)
  M.getctxid_calls = M.getctxid_calls + 1
  return nil
end

-- The station: hud_battle (PRIORITY 1, vis=true) holds the panel with a
-- CcoUnitStat*-prefixed row; the other priority roots have children too; two of
-- them (left/right) and tactical_hud are HIDDEN yet descended; unit_id_holder
-- holds the numeric cards; watermark_square/paused_panel have NO children (skipped).
function M.build_r13_scene()
  local ROOT = M.root
  M.clear(ROOT)

  -- ---- PRIORITY ROOT 1: hud_battle (vis=true) - the panel lives here ----------
  local hud = M.new("hud_battle", { visible = true })
  M.attach(ROOT, hud)
  M.attach(hud, M.new("some_filler"))
  local u1 = M.new("1001")            -- a numeric unit-id INSIDE the panel path
  M.attach(hud, u1)
  local mp = M.new("modular_parent")
  M.attach(u1, mp)
  for i = 1, 4 do M.attach(mp, M.new("filler_" .. i)) end
  local hsp = M.new("health_and_stats_parent", { visible = true })   -- structural HIT
  M.attach(mp, hsp)
  local ds = M.new("dynamic_stats")                                   -- structural HIT
  M.attach(hsp, ds)
  -- row 1: template_stat -> stat_name "Armour" / value_holder > dy_value "85"
  local row1 = M.new("template_stat")
  M.attach(ds, row1)
  M.attach(row1, M.new("stat_name", { stext = "Armour" }))
  local vh1 = M.new("value_holder")
  M.attach(row1, vh1)
  M.attach(vh1, M.new("dy_value", { stext = "85" }))
  -- row 2: a LOWERCASE CcoUnitStat* id (case-insensitivity proof)
  local row2 = M.new("ccounitstat5974452864")
  M.attach(ds, row2)
  M.attach(row2, M.new("stat_name", { stext = "Movement" }))
  local vh2 = M.new("value_holder")
  M.attach(row2, vh2)
  M.attach(vh2, M.new("dy_value", { stext = "5.2" }))
  -- row 3: the real MIXED-CASE shape (the round-4 marker)
  local row3 = M.new("CcoUnitStat5974444112")
  M.attach(ds, row3)
  M.attach(row3, M.new("stat_name", { stext = "Armour" }))
  local vh3 = M.new("value_holder")
  M.attach(row3, vh3)
  M.attach(vh3, M.new("dy_value", { stext = "85" }))
  M.attach(hsp, M.new("row_header_stats"))     -- structural HIT
  M.attach(hsp, M.new("stats_toggle"))         -- structural HIT
  -- a filler chain under hud_battle (nested depth reach)
  local chain = M.new("chain_1")
  M.attach(hud, chain)
  for i = 2, 6 do
    local c = M.new("chain_" .. i)
    M.attach(chain, c)
    chain = c
  end

  -- ---- the other PRIORITY roots (children) ------------------------------------
  local pm = M.new("panel_manager"); M.attach(ROOT, pm)
  for i = 1, 2 do M.attach(pm, M.new("pm_" .. i)) end
  local uad = M.new("under_advisor_docker"); M.attach(ROOT, uad)
  for i = 1, 2 do M.attach(uad, M.new("uad_" .. i)) end
  local left = M.new("left", { visible = false }); M.attach(ROOT, left)
  for i = 1, 2 do M.attach(left, M.new("left_" .. i)) end
  local right = M.new("right", { visible = false }); M.attach(ROOT, right)
  for i = 1, 2 do M.attach(right, M.new("right_" .. i)) end
  local thud = M.new("tactical_hud", { visible = false }); M.attach(ROOT, thud)
  for i = 1, 2 do M.attach(thud, M.new("thud_" .. i)) end
  local mb = M.new("menu_bar", { visible = true }); M.attach(ROOT, mb)
  M.attach(mb, M.new("mb_1"))

  -- ---- the REST (children) ----------------------------------------------------
  local tmap = M.new("tactical_map", { visible = false }); M.attach(ROOT, tmap)
  M.attach(tmap, M.new("tmap_1"))
  local uid = M.new("unit_id_holder"); M.attach(ROOT, uid)
  M.attach(uid, M.new("1001"))   -- the selected card
  M.attach(uid, M.new("1002"))   -- a NON-selected card
  M.attach(uid, M.new("not_a_number"))

  -- ---- roots with NO children (must NOT be descended) -------------------------
  M.attach(ROOT, M.new("watermark_square"))
  M.attach(ROOT, M.new("paused_panel"))

  -- context ids: default NIL, so step 5's reads prove what the HITS report.
  walk(ROOT, function(c) c.GetContextObjectId = nil_ctxid end)
  ds.GetContextObjectId = function(self, tid)
    M.getctxid_calls = M.getctxid_calls + 1
    if tid == "CcoUnitDetails" then return "5001" end
    return nil
  end
  row3.GetContextObjectId = function(self, tid)
    M.getctxid_calls = M.getctxid_calls + 1
    if tid == "CcoUnitStat" then return "5101" end
    return nil
  end

  M.local_units = { 1001, 1002 }
  M.gcv_values = {
    ["5001|StatList.Size"] = 3,       -- query 1 (located id) returns -> query 2 uses DisplayedValue
    ["1002|DisplayedValue"] = "12.5", -- query 2 (non-selected ui id, as text)
  }
  return { hud = hud, ds = ds, row2 = row2, row3 = row3, u1 = u1 }
end

-- a CcoUnitStat* node one level BEYOND the depth-8 cap: hud_battle(d1) > lvl2..lvl8
-- (d2..d8) > CcoUnitStat* (d9). Depth 8 IS reached; depth 9 must NOT be visited.
function M.build_r13_deep()
  local ROOT = M.root
  M.clear(ROOT)
  local hud = M.new("hud_battle", { visible = true }); M.attach(ROOT, hud)
  local node = hud
  for i = 2, 8 do
    local c = M.new("lvl" .. i); M.attach(node, c); node = c
  end
  M.attach(node, M.new("CcoUnitStatDEADBEEF"))    -- depth 9 - beyond the cap
  M.local_units = { 1001, 1002 }
end

-- a huge fan-out under hud_battle (the priority-1 root): 1 + 40 + 1600 = 1641
-- nodes; the 1200-visit budget must cut step 2 off.
function M.build_r13_wide()
  local ROOT = M.root
  M.clear(ROOT)
  local hud = M.new("hud_battle", { visible = true }); M.attach(ROOT, hud)
  for i = 1, 40 do
    local c = M.new("c" .. i); M.attach(hud, c)
    for j = 1, 40 do M.attach(c, M.new("g" .. i .. "_" .. j)) end
  end
  M.local_units = { 1001, 1002 }
end

-- roots WITH children but no CcoUnitStat prefix and no structural id -> no HIT.
function M.build_r13_nohit()
  local ROOT = M.root
  M.clear(ROOT)
  local hud = M.new("hud_battle", { visible = true }); M.attach(ROOT, hud)
  for i = 1, 6 do M.attach(hud, M.new("plain_" .. i)) end
  local left = M.new("left", { visible = false }); M.attach(ROOT, left)
  for i = 1, 6 do M.attach(left, M.new("plain_l" .. i)) end
  M.local_units = { 1001, 1002 }
end
