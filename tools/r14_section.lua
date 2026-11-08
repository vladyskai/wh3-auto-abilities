-- ============================================================================
-- 17b. ROUND 14 - THE PANEL PATH AND THE CONTEXT-ID FORMAT ARE DISCOVERED.
--      SEED THE DESCENT DIRECTLY ON THE DISCOVERED PANEL PATH
--      (hud_battle/info_panel_parent/info_panel_background/unit_information/
--       info_parent/info_panel/list) WITH A SMALL BUDGET, PAIR THE STAT ROWS
--      (stat_name -> dy_value) INSIDE IT, THEN RUN A **FIXED LADDER** OF
--      common.get_context_value CALLS - ONE PER ARMED STEP, EVERY CALL LOGGED
--      BEFORE AND AFTER, STOPPING AT THE FIRST SUCCESS.
--
--      WHY. Round 13 found the panel's REAL path (unit_information lives UNDER
--      info_panel_parent inside hud_battle - not at the top level, not under
--      unit_id_holder) and the CONTEXT ID FORMAT: on the info_panel/list
--      component, GetContextObjectId("CcoUnitDetails") returned "BattleUnit_1001"
--      (the selected unit's ui id is 1001). But round 13's 1200-visit descent ran
--      out of budget before it reached the stat ROWS (PANEL rows: 0), so both of
--      its value queries returned <ERR>. So the FIELD NAME (and/or the type/id
--      pairing) is what is wrong - NOT the mechanism. Round 14 therefore stops
--      re-walking the whole HUD: it SEEDS the descent on the discovered path,
--      walks only the small `list` subtree, pairs the rows, and then throws a
--      SHORT, FIXED LADDER of common.get_context_value calls at the panel until
--      one lands. This is the finish line.
--
--      R14 TOTAL STEPS 8 - you are done after step 8.
--
--      THE PLAN (all READ-ONLY; ZERO SetContextObject; simhover DISARMED; the
--      engine's name-lookup helper is BANNED from this file; ONE armed console
--      step at a time, every native call logged BEFORE it is made):
--        STEP 1 - SEED the descent on the discovered path: resolve hud_battle ->
--                 info_panel_parent -> info_panel_background -> unit_information
--                 -> info_parent -> info_panel -> list (each link = the DIRECT
--                 child whose Id matches; fallback = that node's own recursive
--                 Find), then walk DOWN from `list` (depth 6, budget 300),
--                 logging R14 DOWN path/id/children/stext/tip/vis for every node.
--        STEP 2 - ROW PAIRING: for every walked node whose id contains
--                 template_stat OR that has a stat_name child, log
--                 R14 PANEL row=N name=.. value=.. rowid=.. path=.., the value
--                 read from value_holder > dy_value (or a direct dy_value/value).
--        STEP 3 - LADDER A CONTROL: common.get_context_value("CcoBattleUnit",
--                 "1001", "Name") - the round-7 known-good call. A CONTROL never
--                 stops the ladder; it only proves the harness works.
--        STEP 4 - LADDER A (the SELECTED unit): CcoUnitDetails / "BattleUnit_1001"
--                 with fields Name, StatList, StatList.Size, then CcoUnitStat /
--                 "BattleUnit_1001" with DisplayedValue, Name. Each call logged
--                 before AND after; the ladder STOPS at the first success.
--        STEP 5 - LADDER B CONTROL: common.get_context_value("CcoBattleUnit",
--                 "1002", "Name") - the bare-id NON-selected control. Never stops.
--        STEP 6 - LADDER B (the NON-selected unit, "BattleUnit_1002"): the same
--                 CcoUnitDetails / CcoUnitStat rungs; stop at the first success
--                 and log R14 *** WIN *** if a non-selected field reads back.
--        STEP 7 - LADDER B (bare "1002"): CcoUnitDetails / "1002" /
--                 StatList.Size + CcoUnitStat / "1002" / DisplayedValue; skipped
--                 if step 6 already won; otherwise stop at the first success.
--        STEP 8 - VERDICT: state whether a NON-selected NEW-format stat field was
--                 readable (the project's central question), and DONE.
--        Only proven-safe primitives: ChildCount, Find, Id, Visible,
--        VisibleFromRoot, CurrentState, GetStateText, GetTooltipText, and
--        common.get_context_value. ZERO UI writes.
-- ============================================================================

-- A GLOBAL table (not a local): the probe chunk already carries ~170 top-level
-- locals and Lua's 200-local ceiling is real - R14 must not spend one.
R14 = {
  run_no              = 0,
  step                = 0,          -- 0 = not started; +1 per armed step
  done                = false,
  total_steps         = 8,          -- R14 TOTAL STEPS 8 - you are done after step 8
  lines               = 0,
  max_lines           = 20000,      -- HARD CAP on R14 log lines
  line_cap_spoken     = false,
  -- hard budgets
  child_max           = 80,         -- children scanned per node
  walk_visits         = 300,        -- walk DOWN from `list`: TOTAL visits
  walk_depth          = 6,          -- walk DOWN from `list`: max depth
  row_max             = 60,         -- most stat rows paired
  -- the DISCOVERED panel path (root-first; each link is a direct child of the one before)
  chain               = { "hud_battle", "info_panel_parent", "info_panel_background",
                          "unit_information", "info_parent", "info_panel", "list" },
  -- resolved handles
  nodes               = {},         -- level -> { id, uic, how, children, path }
  list_uic            = nil,
  list_path           = nil,
  chain_ok            = false,
  -- walk output
  walked              = {},         -- { id, uic, path, stext, tip, depth }
  walk_count          = 0,
  walk_seen           = {},         -- component -> true (repeat/cycle guard)
  walk_cap_spoken     = false,
  -- rows
  rows                = {},
  -- the ladder
  ladder_n            = 0,          -- EVERY GCV call gets the next n
  selected_ui         = "1001",
  nonsel_ui           = "1002",
  rung_A              = {           -- LADDER A (selected): new-format rungs, in order
    { "CcoUnitDetails", "BattleUnit_1001", "Name" },
    { "CcoUnitDetails", "BattleUnit_1001", "StatList" },
    { "CcoUnitDetails", "BattleUnit_1001", "StatList.Size" },
    { "CcoUnitStat",    "BattleUnit_1001", "DisplayedValue" },
    { "CcoUnitStat",    "BattleUnit_1001", "Name" },
  },
  rung_B              = {           -- LADDER B (non-selected): new-format rungs, in order
    { "CcoUnitDetails", "BattleUnit_1002", "Name" },
    { "CcoUnitDetails", "BattleUnit_1002", "StatList" },
    { "CcoUnitDetails", "BattleUnit_1002", "StatList.Size" },
    { "CcoUnitStat",    "BattleUnit_1002", "DisplayedValue" },
    { "CcoUnitStat",    "BattleUnit_1002", "Name" },
    { "CcoUnitDetails", "1002", "StatList.Size" },
    { "CcoUnitStat",    "1002", "DisplayedValue" },
  },
  rung_B_split        = 5,          -- rungs 1..5 use "BattleUnit_1002"; rungs 6..7 use bare "1002"
  result_control_A    = nil,
  result_control_B    = nil,
  result_A            = nil,        -- first successful new-format A rung text
  result_A_rung       = nil,
  result_B            = nil,        -- first successful new-format B rung text
  result_B_rung       = nil,
  gcv_calls           = 0,
  win                 = false,      -- a NON-selected NEW-format field read back a value
  win_control         = false,      -- the NON-selected bare-id CONTROL read back a value
}

-- ---------------------------------------------------------------- R14 logging
function R14.out(msg)
  if R14.lines >= R14.max_lines then
    if not R14.line_cap_spoken then
      R14.line_cap_spoken = true
      log("R14 line cap reached (" .. tostring(R14.max_lines) .. ") - further R14 lines are not logged")
    end
    return
  end
  R14.lines = R14.lines + 1
  log("R14 " .. tostring(msg))
end

-- ALWAYS call this IMMEDIATELY before a native call: it names the fatal call if
-- the engine dies on the next statement.
function R14.call(desc)
  R14.out("CALL " .. tostring(R14.step) .. " " .. tostring(desc))
end

function R14.read_text(fn)
  local ok, v = pcall(fn)
  if not ok then return "<ERR>" end
  if v == nil then return nil end
  local s = safe_text(v)
  if s ~= nil then return s end
  return "<opaque>"
end

-- Quoted path for the log: the panel paths are ~100 chars, longer than q()'s
-- 90-char cap, so paths get their own (160-char) quoter.
function R14.qpath(s)
  if s == nil then return "nil" end
  local str = safe_text(s)
  if str == nil then return "\"<unreadable>\"" end
  if #str > 160 then str = string.sub(str, 1, 160) .. "..." end
  return "\"" .. str .. "\""
end

-- Log the walk visit-cap ONCE (both the top-of-walk and the in-loop cut paths
-- call this).
function R14.walk_cap()
  if not R14.walk_cap_spoken then
    R14.walk_cap_spoken = true
    R14.out("WALK visit budget reached (" .. tostring(R14.walk_visits) .. ") - subtree truncated here")
  end
end

-- ---------------------------------------------------- proven-shape primitives
function R14.ui_root()
  R14.call("core:get_ui_root()")
  local ok, r = pcall(function() return core:get_ui_root() end)
  if not ok or r == nil then return nil end
  return r
end

function R14.child_count(uic)
  if uic == nil then return 0 end
  local n = read1(function() return uic:ChildCount() end)
  if lua_type(n) == "number" then return n end
  return 0
end

-- uic:Find(i) -> a child, or nil. The result is TRUTHINESS-guarded (never wrap a
-- boolean: the round-9 crash).
function R14.child_at(uic, i)
  if uic == nil then return nil end
  local ok, raw = pcall(function() return uic:Find(i) end)
  if not ok or raw == nil or raw == false then return nil end
  return wrap(raw)
end

function R14.id_of(uic)
  if uic == nil then return nil end
  return R14.read_text(function() return uic:Id() end)
end

function R14.vis_of(uic)
  if uic == nil then return nil, nil end
  local vis = readb(function() return uic:Visible() end)
  local vfr = readb(function() return uic:VisibleFromRoot() end)
  return tostring(vis), tostring(vfr)
end

-- does this id CONTAIN the given lowercased fragment? (plain byte scan; the
-- probe never runs string.find on an engine value)
function R14.id_has(id, fragment)
  local str = safe_text(id)
  if str == nil or str == "" then return false end
  return contains_str(string.lower(str), fragment)
end

-- the DIRECT child of `uic` whose Id() == want (bounded by child_max; every Find
-- is logged BEFORE it is made). Returns the child, or nil.
function R14.find_child_named(uic, want)
  if uic == nil then return nil end
  local cn = R14.child_count(uic)
  local lim = cn
  if lim > R14.child_max then lim = R14.child_max end
  for i = 0, lim - 1 do
    R14.call(q(R14.id_of(uic) or "?") .. ":Find(" .. tostring(i) .. ") looking for " .. q(want))
    local ch = R14.child_at(uic, i)
    if ch ~= nil and R14.id_of(ch) == want then return ch end
  end
  return nil
end

-- is a common.get_context_value result a real, printable value?
function R14.usable(v, ok)
  if not ok or v == nil then return false end
  local s = safe_text(v)
  if s == nil then return false end
  if s == "" or s == "<ERR>" or s == "<nil>" or s == "<opaque>" then return false end
  return true
end

-- ---------------------------------------------------------------- the GCV call
-- ONE common.get_context_value call. Logged BEFORE (R14 CALL) and AFTER
-- (R14 GCV, carrying the value, even when it is an error). A CONTROL success
-- NEVER stops the ladder; ANY non-selected success raises the loud WIN line.
-- Returns (text, usable).
function R14.gcv(type_id, id_text, field, is_control, is_nonsel)
  R14.ladder_n = R14.ladder_n + 1
  local n = R14.ladder_n
  R14.gcv_calls = R14.gcv_calls + 1
  R14.out("CALL " .. tostring(R14.step) .. " n=" .. tostring(n)
    .. " common.get_context_value(" .. q(type_id) .. ", " .. q(id_text) .. ", " .. q(field) .. ")")
  local ok, v = pcall(function() return common.get_context_value(type_id, id_text, field) end)
  local text = "<ERR>"
  if ok then
    local t = text_of(v, true)
    if t == nil then text = "<nil>" else text = t end
  end
  local usable = R14.usable(v, ok)
  R14.out("GCV n=" .. tostring(n) .. " type=" .. tostring(type_id) .. " id=" .. q(id_text)
    .. " field=" .. q(field) .. " -> " .. q(text)
    .. (is_control and " [CONTROL]" or "") .. (is_nonsel and " [NON-SELECTED]" or "")
    .. (usable and "  **VALUE**" or "  (no value)"))
  if usable and is_nonsel then
    if is_control then
      R14.win_control = true
      R14.out("*** WIN(control): non-selected bare-id CcoBattleUnit field readable *** type="
        .. tostring(type_id) .. " id=" .. q(id_text) .. " field=" .. q(field)
        .. " value=" .. q(text))
    else
      R14.win = true
      R14.out("*** WIN: non-selected unit stat field readable *** type=" .. tostring(type_id)
        .. " id=" .. q(id_text) .. " field=" .. q(field) .. " value=" .. q(text))
    end
  end
  return text, usable
end

-- ---------------------------------------------------------------- the chain
-- Resolve the DISCOVERED panel path link by link. Link 1 (hud_battle) comes from
-- the ui root's own Find; every later link is the DIRECT child of the previous
-- link whose Id() == the link name (fallback: that node's own recursive Find).
function R14.resolve_chain()
  R14.nodes = {}
  R14.list_uic = nil
  R14.list_path = nil
  R14.chain_ok = false
  local root = R14.ui_root()
  if root == nil then
    R14.out("CHAIN aborted: core:get_ui_root() returned nil")
    return false
  end
  local cur = nil
  local cur_path = nil
  for k = 1, #R14.chain do
    local name = R14.chain[k]
    local got, how = nil, nil
    if k == 1 then
      R14.call("ui_root:Find(" .. q(name) .. ", false)")
      local ok_f, raw = pcall(function() return root:Find(name, false) end)
      if ok_f and raw ~= nil and raw ~= false then got = wrap(raw); how = "root:Find" end
      if got == nil then
        got = R14.find_child_named(root, name)
        if got ~= nil then how = "root direct child" end
      end
      cur_path = name
    else
      got = R14.find_child_named(cur, name)
      if got ~= nil then how = "direct child" end
      if got == nil then
        R14.call(q(cur_path) .. ":Find(" .. q(name) .. ", false)")
        local ok_f, raw = pcall(function() return cur:Find(name, false) end)
        if ok_f and raw ~= nil and raw ~= false then
          got = wrap(raw); how = "Find (recursive) from parent"
        end
      end
      cur_path = (cur_path or "?") .. "/" .. name
    end
    if got == nil then
      R14.out("CHAIN link " .. tostring(k) .. "/" .. tostring(#R14.chain)
        .. " id=" .. q(name) .. " NOT FOUND under " .. R14.qpath(cur_path or "?"))
      return false
    end
    local cn = R14.child_count(got)
    R14.nodes[k] = { id = name, uic = got, how = how, children = cn, path = cur_path }
    R14.out("SEED link " .. tostring(k) .. "/" .. tostring(#R14.chain) .. " path=" .. R14.qpath(cur_path)
      .. " id=" .. q(name) .. " how=" .. q(how) .. " children=" .. tostring(cn))
    cur = got
  end
  R14.list_uic = cur
  R14.list_path = cur_path
  R14.chain_ok = true
  R14.out("SEED resolved the FULL chain; list path=" .. R14.qpath(R14.list_path)
    .. " children=" .. tostring(R14.child_count(R14.list_uic)))
  return true
end

-- ---------------------------------------------------------------- the walk
-- Walk DOWN from the `list` node: depth-capped, visit-capped, every touch
-- pcall-walled, every node logged with id / children / stext / tip / vis.
function R14.walk(uic, path, depth)
  if uic == nil then return end
  if R14.walk_count >= R14.walk_visits then
    R14.walk_cap()
    return
  end
  if depth > R14.walk_depth then return end
  if R14.walk_seen[uic] ~= nil then return end
  R14.walk_seen[uic] = true
  R14.walk_count = R14.walk_count + 1
  local id = R14.id_of(uic)
  R14.call("WALK " .. q(path) .. " ChildCount/GetStateText/GetTooltipText/Visible/VisibleFromRoot")
  local cn = R14.child_count(uic)
  local st = R14.read_text(function() return uic:GetStateText() end)
  local tip = R14.read_text(function() return uic:GetTooltipText() end)
  local vis, vfr = R14.vis_of(uic)
  R14.out("DOWN path=" .. R14.qpath(path) .. " id=" .. q(id) .. " children=" .. tostring(cn)
    .. " stext=" .. q(st) .. " tip=" .. q(tip) .. " vis=" .. tostring(vis) .. " vfr=" .. tostring(vfr))
  R14.walked[#R14.walked + 1] = { id = id, uic = uic, path = path, stext = st, tip = tip, depth = depth }
  if depth >= R14.walk_depth then return end
  for i = 0, cn - 1 do
    if R14.walk_count >= R14.walk_visits then R14.walk_cap(); return end
    R14.call("WALK " .. q(path) .. ":Find(" .. tostring(i) .. ")")
    local ch = R14.child_at(uic, i)
    if ch ~= nil then
      local cid = R14.id_of(ch)
      if cid == nil or cid == "" then cid = "#" .. tostring(i) end
      R14.walk(ch, path .. "/" .. cid, depth + 1)
    end
  end
end

-- ---------------------------------------------------------------- the steps
R14.steps = {}

-- STEP 1 - seed the descent on the discovered path, then walk DOWN from `list`.
R14.steps[1] = function()
  R14.out("STEP 1 - seed the descent on the DISCOVERED panel path, then walk DOWN from `list`"
    .. " (depth " .. tostring(R14.walk_depth) .. ", budget " .. tostring(R14.walk_visits) .. ")")
  R14.nodes = {}
  R14.walked = {}
  R14.walk_count = 0
  R14.walk_seen = {}
  R14.walk_cap_spoken = false
  R14.rows = {}
  if not R14.resolve_chain() then
    R14.out("STEP 1 aborted: the discovered chain did not resolve - is the unit-info panel"
      .. " OPEN and PINNED? (the ladder steps below still run)")
    return
  end
  if R14.list_uic == nil then
    R14.out("STEP 1 aborted: the `list` node was not resolved")
    return
  end
  R14.walk(R14.list_uic, R14.list_path, 0)
  R14.out("STEP 1 done: chain links=" .. tostring(#R14.nodes) .. " walked="
    .. tostring(R14.walk_count) .. "/" .. tostring(R14.walk_visits))
end

-- STEP 2 - pair the stat rows under `list`.
R14.steps[2] = function()
  R14.out("STEP 2 - pair the stat rows (stat_name -> value_holder/dy_value) under `list`")
  R14.rows = {}
  if #R14.walked == 0 then
    R14.out("STEP 2: nothing was walked in step 1 - run step 1 with the panel OPEN and PINNED")
    return
  end
  local n = 0
  for k = 1, #R14.walked do
    if n >= R14.row_max then break end
    local rec = R14.walked[k]
    -- the row_header_stats node (the row block's header) is logged for context
    if R14.id_has(rec.id, "row_header_stats") then
      R14.out("ROWHEADER path=" .. q(rec.path) .. " id=" .. q(rec.id) .. " stext=" .. q(rec.stext))
    end
    local is_row = R14.id_has(rec.id, "template_stat")
    if not is_row and rec.uic ~= nil then
      -- a row may be identified by carrying a stat_name child
      local sn_probe = R14.find_child_named(rec.uic, "stat_name")
      if sn_probe ~= nil then is_row = true end
    end
    if is_row then
      n = n + 1
      local sn = R14.find_child_named(rec.uic, "stat_name")
      local name_text = nil
      if sn ~= nil then
        R14.call("stat_name:GetStateText()")
        name_text = R14.read_text(function() return sn:GetStateText() end)
      end
      local dv = nil
      local vh = R14.find_child_named(rec.uic, "value_holder")
      if vh ~= nil then dv = R14.find_child_named(vh, "dy_value") end
      if dv == nil then dv = R14.find_child_named(rec.uic, "dy_value") end
      if dv == nil then dv = R14.find_child_named(rec.uic, "value") end
      local val_text = nil
      if dv ~= nil then
        R14.call("dy_value:GetStateText()")
        val_text = R14.read_text(function() return dv:GetStateText() end)
      end
      R14.out("PANEL row=" .. tostring(n) .. " name=" .. q(name_text) .. " value=" .. q(val_text)
        .. " rowid=" .. q(rec.id) .. " path=" .. q(rec.path))
      R14.rows[#R14.rows + 1] = { n = n, name = name_text, value = val_text, rowid = rec.id }
    end
  end
  R14.out("STEP 2 done: rows=" .. tostring(#R14.rows))
end

-- STEP 3 - LADDER A CONTROL (the round-7 known-good call; never stops the ladder).
R14.steps[3] = function()
  R14.out("STEP 3 - LADDER A CONTROL: common.get_context_value(\"CcoBattleUnit\", "
    .. q(R14.selected_ui) .. ", \"Name\") - a CONTROL never stops the ladder")
  local t, ok = R14.gcv("CcoBattleUnit", R14.selected_ui, "Name", true, false)
  R14.result_control_A = t
  R14.out("STEP 3 done: control_A=" .. q(t) .. (ok and " (VALUE)" or " (no value)"))
end

-- STEP 4 - LADDER A (the SELECTED unit): the new-format rungs, stop at first success.
R14.steps[4] = function()
  R14.out("STEP 4 - LADDER A (SELECTED unit " .. q(R14.selected_ui)
    .. "): the new-format rungs, stop at the first success")
  if R14.result_A ~= nil then
    R14.out("STEP 4: LADDER A already succeeded - skipping")
    return
  end
  local rungs = R14.rung_A
  for i = 1, #rungs do
    local r = rungs[i]
    local t, ok = R14.gcv(r[1], r[2], r[3], false, false)
    if ok then
      R14.result_A = t
      R14.result_A_rung = tostring(r[1]) .. "/" .. tostring(r[2]) .. "/" .. tostring(r[3])
      R14.out("LADDER A STOPPED at first success: rung " .. tostring(i) .. "/" .. tostring(#rungs)
        .. " " .. R14.result_A_rung .. " = " .. q(t))
      return
    end
  end
  R14.out("STEP 4 done: LADDER A - no new-format rung returned a value (" .. tostring(#rungs)
    .. " tried)")
end

-- STEP 5 - LADDER B CONTROL (bare-id non-selected; never stops the ladder).
R14.steps[5] = function()
  R14.out("STEP 5 - LADDER B CONTROL: common.get_context_value(\"CcoBattleUnit\", "
    .. q(R14.nonsel_ui) .. ", \"Name\") - the bare-id NON-selected control")
  local t, ok = R14.gcv("CcoBattleUnit", R14.nonsel_ui, "Name", true, true)
  R14.result_control_B = t
  R14.out("STEP 5 done: control_B=" .. q(t) .. (ok and " (VALUE)" or " (no value)"))
end

-- STEP 6 - LADDER B (NON-selected, "BattleUnit_1002"), stop at first success.
R14.steps[6] = function()
  R14.out("STEP 6 - LADDER B (NON-selected unit \"BattleUnit_1002\"): the same new-format rungs,"
    .. " stop at the first success")
  if R14.result_B ~= nil then
    R14.out("STEP 6: LADDER B already succeeded - skipping")
    return
  end
  local rungs = R14.rung_B
  for i = 1, R14.rung_B_split do
    local r = rungs[i]
    local t, ok = R14.gcv(r[1], r[2], r[3], false, true)
    if ok then
      R14.result_B = t
      R14.result_B_rung = tostring(r[1]) .. "/" .. tostring(r[2]) .. "/" .. tostring(r[3])
      R14.out("LADDER B STOPPED at first success: rung " .. tostring(i) .. "/" .. tostring(#rungs)
        .. " " .. R14.result_B_rung .. " = " .. q(t))
      return
    end
  end
  R14.out("STEP 6 done: LADDER B (BattleUnit_1002) - no rung returned a value ("
    .. tostring(R14.rung_B_split) .. " tried)")
end

-- STEP 7 - LADDER B (bare "1002"): the bare-id rungs, stop at first success.
R14.steps[7] = function()
  R14.out("STEP 7 - LADDER B (bare \"1002\"): CcoUnitDetails/CcoUnitStat with the bare id,"
    .. " stop at the first success")
  if R14.result_B ~= nil then
    R14.out("STEP 7: the ladder already stopped (a NON-selected field read back in step 6) - skipping")
    return
  end
  local rungs = R14.rung_B
  for i = R14.rung_B_split + 1, #rungs do
    local r = rungs[i]
    local t, ok = R14.gcv(r[1], r[2], r[3], false, true)
    if ok then
      R14.result_B = t
      R14.result_B_rung = tostring(r[1]) .. "/" .. tostring(r[2]) .. "/" .. tostring(r[3])
      R14.out("LADDER B STOPPED at first success (bare id): rung " .. tostring(i) .. "/"
        .. tostring(#rungs) .. " " .. R14.result_B_rung .. " = " .. q(t))
      return
    end
  end
  R14.out("STEP 7 done: LADDER B (bare 1002) - no rung returned a value")
end

-- STEP 8 - VERDICT.
R14.steps[8] = function()
  R14.out("STEP 8 - VERDICT")
  R14.out("VERDICT control_A=" .. q(R14.result_control_A)
    .. " control_B=" .. q(R14.result_control_B)
    .. " new_A=" .. q(R14.result_A) .. " [" .. tostring(R14.result_A_rung) .. "]"
    .. " new_B=" .. q(R14.result_B) .. " [" .. tostring(R14.result_B_rung) .. "]")
  R14.out("VERDICT get_context_value calls=" .. tostring(R14.gcv_calls))
  if R14.win then
    R14.out("VERDICT: CENTRAL QUESTION ANSWERED - a NON-selected unit's new-format stat field IS"
      .. " readable: " .. tostring(R14.result_B_rung) .. " = " .. q(R14.result_B))
  else
    R14.out("VERDICT: NO non-selected NEW-format stat field was readable (control_B="
      .. q(R14.result_control_B) .. ") - the type/id/field pairing still needs work")
  end
  if R14.win_control then
    R14.out("VERDICT: the NON-selected bare-id control value WAS readable (round-7 mechanism confirmed)")
  end
  R14.out("STEP 8 done: R14 TOTAL STEPS 8 - you are done (STOP).")
end

-- ---------------------------------------------------------------- the driver
function R14.advance()
  if R14.done then
    R14.out("step ignored: the run is done (" .. tostring(R14.total_steps)
      .. " steps) - zz_probe_r14() restarts it")
    return R14.step
  end
  R14.step = R14.step + 1
  local fn = R14.steps[R14.step]
  if fn == nil then
    R14.done = true
    R14.out("===== ROUND 14 RUN done after " .. tostring(R14.total_steps)
      .. " steps (reads only; zero writes) - R14 TOTAL STEPS 8 - YOU ARE DONE =====")
    return R14.step
  end
  R14.out("")
  R14.out("===== R14 STEP " .. tostring(R14.step) .. "/" .. tostring(R14.total_steps)
    .. " (t=" .. tostring(tick_count) .. ") =====")
  local ok, err = pcall(fn)
  if not ok then
    R14.out("STEP " .. tostring(R14.step) .. " raised (swallowed): " .. truncate(err, 160))
  end
  return R14.step
end

-- ---------------------------------------------------------------- the hooks
function zz_probe_r14()
  R14.step = 0
  R14.done = false
  R14.nodes = {}
  R14.list_uic = nil
  R14.list_path = nil
  R14.chain_ok = false
  R14.walked = {}
  R14.walk_count = 0
  R14.walk_seen = {}
  R14.walk_cap_spoken = false
  R14.rows = {}
  R14.ladder_n = 0
  R14.result_control_A = nil
  R14.result_control_B = nil
  R14.result_A = nil
  R14.result_A_rung = nil
  R14.result_B = nil
  R14.result_B_rung = nil
  R14.gcv_calls = 0
  R14.win = false
  R14.win_control = false
  return PROBE_TAG .. "R14 READY (step 0 of 8). R14 TOTAL STEPS 8 - you are done after step 8."
    .. " In battle, open AND PIN the unit-info panel and keep the cards panel up with >=2 units,"
    .. " then call zz_probe_r14_step() ONE step at a time (after each step, if the game is alive,"
    .. " type the next). Step 8 is the LAST step - stop there. log=" .. LOG_FILE
end

function zz_probe_r14_step()
  if R14.step == 0 and (not R14.done) then
    R14.run_no = R14.run_no + 1
    R14.lines = 0
    R14.line_cap_spoken = false
    R14.out("")
    R14.out("===== ROUND 14 RUN #" .. tostring(R14.run_no)
      .. " (manual zz_probe_r14_step) t=" .. tostring(tick_count) .. " =====")
    R14.out("R14 TOTAL STEPS 8 - you are done after step 8. Seed the descent on the DISCOVERED"
      .. " panel path (hud_battle/info_panel_parent/info_panel_background/unit_information/"
      .. "info_parent/info_panel/list), walk DOWN from `list` (depth " .. tostring(R14.walk_depth)
      .. ", budget " .. tostring(R14.walk_visits) .. "), pair the stat rows, then run a FIXED"
      .. " LADDER of common.get_context_value calls (a control, then CcoUnitDetails/BattleUnit_1001"
      .. " fields Name/StatList/StatList.Size, then CcoUnitStat/BattleUnit_1001 DisplayedValue/Name;"
      .. " then the SAME ladder shape for the NON-selected unit \"BattleUnit_1002\" and bare \"1002\"),"
      .. " logged before AND after, stopping at the first success, with a loud R14 *** WIN *** if a"
      .. " NON-selected field reads back a value. Only proven-safe primitives; ZERO SetContextObject;"
      .. " simhover DISARMED; the name-lookup helper is BANNED.")
  end
  local before = R14.step
  R14.advance()
  local nxt
  if R14.done or R14.step >= R14.total_steps or R14.steps[R14.step + 1] == nil then
    nxt = "DONE - STOP (zz_probe_r14 finished after " .. tostring(R14.total_steps) .. " steps)"
  else
    nxt = "step " .. tostring(R14.step + 1) .. " of " .. tostring(R14.total_steps)
  end
  return PROBE_TAG .. "R14 step " .. tostring(R14.step) .. "/" .. tostring(R14.total_steps)
    .. " done (was " .. tostring(before) .. "); next: " .. nxt
    .. " - call zz_probe_r14_step() again. log=" .. LOG_FILE
end

function zz_probe_r14_auto()
  if R14.step == 0 and (not R14.done) then zz_probe_r14() end
  R14.run_no = R14.run_no + 1
  R14.lines = 0
  R14.line_cap_spoken = false
  R14.out("")
  R14.out("===== ROUND 14 AUTO RUN #" .. tostring(R14.run_no) .. " t=" .. tostring(tick_count)
    .. " - runs every step to the cap; a fatal call dies here and the last R14 CALL names it =====")
  local guard = 0
  while (not R14.done) and guard < 40 do
    guard = guard + 1
    R14.advance()
  end
  return PROBE_TAG .. "R14 auto finished (step=" .. tostring(R14.step)
    .. (R14.done and ", done" or ", cap") .. "). log=" .. LOG_FILE
end

function zz_probe_r14_status()
  return PROBE_TAG .. "R14 TOTAL STEPS " .. tostring(R14.total_steps) .. " - run="
    .. tostring(R14.run_no) .. " step=" .. tostring(R14.step) .. "/" .. tostring(R14.total_steps)
    .. " done=" .. tostring(R14.done) .. " lines=" .. tostring(R14.lines)
    .. "/" .. tostring(R14.max_lines)
    .. " | chain_ok=" .. tostring(R14.chain_ok)
    .. " list_path=" .. q(R14.list_path)
    .. " walked=" .. tostring(R14.walk_count) .. "/" .. tostring(R14.walk_visits)
    .. " rows=" .. tostring(#(R14.rows or {}))
    .. " gcv_calls=" .. tostring(R14.gcv_calls)
    .. " win=" .. tostring(R14.win) .. " win_control=" .. tostring(R14.win_control)
    .. " | zz_probe_r14() to start/restart; log=" .. LOG_FILE
end

function zz_probe_r14_help()
  return PROBE_TAG .. "R14 SEED ON THE DISCOVERED PANEL PATH + A FIXED GCV LADDER."
    .. " R14 TOTAL STEPS 8 - you are done after step 8."
    .. " Start a battle, open AND PIN the unit-info panel, and keep the cards panel up with"
    .. " >=2 units. Call zz_probe_r14() once, then zz_probe_r14_step() EIGHT times ("
    .. tostring(R14.total_steps) .. " total; STOP after step " .. tostring(R14.total_steps) .. ")."
    .. " Step 1 seeds the descent on hud_battle/info_panel_parent/info_panel_background/"
    .. "unit_information/info_parent/info_panel/list and walks DOWN from `list` (depth "
    .. tostring(R14.walk_depth) .. ", budget " .. tostring(R14.walk_visits) .. "); step 2 pairs the"
    .. " stat rows (R14 PANEL row=N name=.. value=..); step 3 is the LADDER A control"
    .. " (CcoBattleUnit/1001/Name); step 4 runs LADDER A (CcoUnitDetails/BattleUnit_1001 fields"
    .. " Name/StatList/StatList.Size then CcoUnitStat/BattleUnit_1001 DisplayedValue/Name), stopping"
    .. " at the first success; step 5 is the LADDER B control (CcoBattleUnit/1002/Name); step 6 runs"
    .. " LADDER B (CcoUnitDetails/BattleUnit_1002 ... then CcoUnitStat/BattleUnit_1002 ...); step 7 runs"
    .. " LADDER B with the bare id \"1002\"; step 8 states the verdict. EVERY common.get_context_value"
    .. " call is logged before AND after (R14 GCV n=.. type=.. id=.. field=.. -> value) and the ladder"
    .. " STOPS at the first success - a NON-selected success logs R14 *** WIN ***. ZERO writes; simhover"
    .. " DISARMED; the name-lookup helper is BANNED. Log: " .. LOG_FILE
end
