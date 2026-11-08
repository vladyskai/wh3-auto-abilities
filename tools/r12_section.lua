-- ============================================================================
-- 16. ROUND 12 - FINISH THE PANEL HUNT: SEED THE DESCENT ON THE NUMERIC
--     UNIT-ID NODES UNDER unit_id_holder, DESCEND TO DEPTH 8 (800 VISITS),
--     PAIR THE STAT ROWS, READ THE CONTEXT IDS, THEN ASK EXACTLY TWO
--     common.get_context_value CALLS (the round-11 depth-cap post-mortem build).
--
--     WHY. Round 11's step 3 stopped at 88 of its 400 visits - the DEPTH cap
--     (4), not the budget, cut the hunt short. Its last node was
--         R11 DESCEND path="unit_id_holder/1001/modular_parent" id="modular_parent" children=10
--     i.e. the unit-info panel is PER-UNIT, under
--     unit_id_holder/<unit ui id>/modular_parent - and the stat rows sit at
--     DEPTH 5-8, one level past the round-11 cap. Round 12 re-seeds the
--     descent on the NUMERIC unit-id nodes (1001, 1002, ...) found under
--     unit_id_holder and descends to DEPTH 8 with an 800-visit budget.
--
--     R12 TOTAL STEPS 6 - you are done after step 6.
--
--     THE PLAN (all READ-ONLY; ZERO SetContextObject; simhover DISARMED; the
--     engine's name-lookup helper is BANNED from this file; ONE armed console
--     step at a time, every native call logged BEFORE it is made):
--       STEP 1 - enumerate the UI root's top-level children; keep unit_id_holder.
--       STEP 2 - list unit_id_holder's children; the NUMERIC ids (1001, 1002,
--                ...) are the per-unit seeds.
--       STEP 3 - descend EVERY unit-id subtree to DEPTH 8 (800 visits TOTAL),
--                logging R12 DOWN path/id/children/stext for every node inside.
--       STEP 4 - locate the stat-row nodes (health_and_stats / dynamic_stats /
--                template_stat / stat_name / value_holder / dy_value) and pair
--                every template_stat row's stat_name with its dy_value.
--       STEP 5 - read GetContextObjectId(CcoUnitDetails / CcoUnitStat /
--                CcoBattleUnit) on the located row components (reads only).
--       STEP 6 - run EXACTLY TWO common.get_context_value calls: ONE with the
--                SELECTED unit's context id, ONE with a NON-selected unit's ui id.
--     Only proven-safe primitives: ChildCount, Find, Id, Visible,
--     VisibleFromRoot, CurrentState, GetStateText, GetContextObjectId.
-- ============================================================================

-- A GLOBAL table (not a local): the probe chunk already carries ~168 top-level
-- locals and Lua's 200-local ceiling is real - R12 must not spend one.
R12 = {
  run_no          = 0,
  step            = 0,          -- 0 = not started; +1 per armed step
  done            = false,
  total_steps     = 6,          -- R12 TOTAL STEPS 6 - you are done after step 6
  lines           = 0,
  max_lines       = 9000,       -- HARD CAP on R12 log lines
  line_cap_spoken = false,
  -- hard enumeration budgets
  root_max        = 60,         -- top-level roots logged (step 1)
  child_max       = 60,         -- children scanned per node (steps 2/4)
  descend_visits  = 800,        -- step 3 TOTAL visits
  descend_depth   = 8,          -- step 3 max depth FROM a unit-id seed
  locate_max      = 60,         -- most located components kept for step 4/5
  ctx_max         = 60,         -- most located components probed in step 5
  -- the panel ids the descent is hunting (SUBSTRING match on a lowercased id)
  locate_names = { "health_and_stats", "dynamic_stats", "template_stat",
                   "stat_name", "value_holder", "dy_value" },
  -- step-1 output
  roots        = {},            -- { id, uic }
  -- step-2 output
  children     = {},            -- { id, uic, numeric, stext }
  seeds        = {},            -- { id, uic, path } - the NUMERIC unit-id nodes
  -- step-3 output
  located       = {},           -- id -> first { id, uic, path }
  located_order = {},           -- ids in discovery order
  located_list  = {},           -- EVERY located node { id, uic, path }
  descend_count = 0,
  desc_seen     = {},           -- path -> true (repeat/cycle guard)
  -- step-4 output
  rows         = {},            -- { n, name, value, uic, path }
  -- step-5 output
  ctx_types    = { "CcoUnitDetails", "CcoUnitStat", "CcoBattleUnit" },
  ctx          = {},            -- type_id -> context id (non-nil, first kept)
  ctx_from     = {},            -- type_id -> path the id came from
  selected_ui  = nil,           -- the SELECTED unit's numeric ui id (from a path)
  sel_tid      = nil,           -- the type the selected context id came from
  sel_id       = nil,           -- the selected context id
  -- step-6
  fields       = { "StatList.Size" },   -- THE single decisive field
  gcv_calls    = 0,
}

-- ---------------------------------------------------------------- R12 logging
function R12.out(msg)
  if R12.lines >= R12.max_lines then
    if not R12.line_cap_spoken then
      R12.line_cap_spoken = true
      log("R12 line cap reached (" .. tostring(R12.max_lines) .. ") - further R12 lines are not logged")
    end
    return
  end
  R12.lines = R12.lines + 1
  log("R12 " .. tostring(msg))
end

-- ALWAYS call this IMMEDIATELY before a native call: it is the line that names
-- the fatal call if the engine dies on the next statement.
function R12.call(desc)
  R12.out("CALL " .. tostring(R12.step) .. " " .. tostring(desc))
end

function R12.read_text(fn)
  local ok, v = pcall(fn)
  if not ok then return "<ERR>" end
  if v == nil then return nil end
  local s = safe_text(v)
  if s ~= nil then return s end
  return "<opaque>"
end

-- ---------------------------------------------------- proven-shape primitives
function R12.ui_root()
  R12.call("core:get_ui_root()")
  local ok, r = pcall(function() return core:get_ui_root() end)
  if not ok or r == nil then return nil end
  return r
end

function R12.child_count(uic)
  if uic == nil then return 0 end
  local n = read1(function() return uic:ChildCount() end)
  if lua_type(n) == "number" then return n end
  return 0
end

-- uic:Find(i) -> a child, or nil. The result is TRUTHINESS-guarded (never wrap a
-- boolean: the round-9 crash).
function R12.child_at(uic, i)
  if uic == nil then return nil end
  local ok, raw = pcall(function() return uic:Find(i) end)
  if not ok or raw == nil or raw == false then return nil end
  return wrap(raw)
end

function R12.id_of(uic)
  if uic == nil then return nil end
  return R12.read_text(function() return uic:Id() end)
end

function R12.vis_of(uic)
  if uic == nil then return nil, nil end
  local vis = readb(function() return uic:Visible() end)
  local vfr = readb(function() return uic:VisibleFromRoot() end)
  return tostring(vis), tostring(vfr)
end

-- an id is a unit ui id when EVERY character is a digit
function R12.is_numeric(s)
  local str = safe_text(s)
  if str == nil or str == "" then return false end
  local len = string.len(str)
  for i = 1, len do
    local c = string.byte(str, i)
    if c == nil or c < 48 or c > 57 then return false end
  end
  return true
end

-- does an id name one of the panel nodes the hunt is after?
function R12.is_located_id(id)
  local str = safe_text(id)
  if str == nil then return false end
  local low = string.lower(str)
  for i = 1, #R12.locate_names do
    if contains_str(low, R12.locate_names[i]) then return true end
  end
  return false
end

function R12.count_ctx()
  local n = 0
  for _ in pairs(R12.ctx) do n = n + 1 end
  return n
end

-- Split helpers WITHOUT string.find (the probe bans it): plain byte scans.
function R12.first_segment(s)
  local str = safe_text(s)
  if str == nil then return nil end
  local len = string.len(str)
  for i = 1, len do
    if string.sub(str, i, i) == "/" then return string.sub(str, 1, i - 1) end
  end
  return str
end

function R12.strip_prefix(s, p)
  local str = safe_text(s)
  local pp = tostring(p)
  if str == nil then return nil end
  if string.len(str) >= string.len(pp)
     and string.sub(str, 1, string.len(pp)) == pp then
    return string.sub(str, string.len(pp) + 1)
  end
  return str
end

-- ---------------------------------------------------------------- the steps
R12.steps = {}

-- STEP 1 - enumerate the UI root's top-level children (find unit_id_holder).
R12.steps[1] = function()
  R12.out("STEP 1 - enumerate the UI root's top-level children (budget "
    .. tostring(R12.root_max) .. ")")
  local root = R12.ui_root()
  if root == nil then
    R12.out("STEP 1 aborted: core:get_ui_root() returned nil")
    return
  end
  local n = R12.child_count(root)
  R12.out("ROOTCOUNT " .. tostring(n))
  if n <= 0 then
    R12.out("STEP 1: the UI root has no children yet (battle not up?)")
    return
  end
  R12.roots = {}
  local lim = n
  if lim > R12.root_max then lim = R12.root_max end
  for i = 0, lim - 1 do
    R12.call("ui_root:Find(" .. tostring(i) .. ") + Id/ChildCount/Visible/VisibleFromRoot")
    local uic = R12.child_at(root, i)
    local id = R12.id_of(uic)
    local vis, vfr = R12.vis_of(uic)
    local cn = tostring(R12.child_count(uic))
    R12.out("ROOT " .. tostring(i) .. " id=" .. q(id) .. " vis=" .. tostring(vis)
      .. " vfr=" .. tostring(vfr) .. " children=" .. cn)
    R12.roots[#R12.roots + 1] = { uic = uic, id = id }
  end
  if n > lim then
    R12.out("ROOT ... (" .. tostring(n - lim) .. " more root(s) not listed; cap "
      .. tostring(R12.root_max) .. ")")
  end
end

-- STEP 2 - list unit_id_holder's children; the NUMERIC ids are the seeds.
R12.steps[2] = function()
  R12.out("STEP 2 - list unit_id_holder's children; the NUMERIC ids (1001, 1002,"
    .. " ...) are the per-unit seeds")
  R12.children = {}
  R12.seeds = {}
  if R12.roots == nil or #R12.roots == 0 then
    R12.out("STEP 2 aborted: no roots recorded by step 1")
    return
  end
  local holder = nil
  for i = 1, #R12.roots do
    local rid = R12.roots[i].id
    if rid ~= nil and safe_text(rid) == "unit_id_holder" then holder = R12.roots[i]; break end
  end
  if holder == nil then
    for i = 1, #R12.roots do
      local rid = R12.roots[i].id
      if rid ~= nil and contains_str(string.lower(tostring(rid)), "unit_id_holder") then
        holder = R12.roots[i]; break
      end
    end
  end
  if holder == nil then
    R12.out("STEP 2: NO unit_id_holder root among the " .. tostring(#R12.roots)
      .. " root(s) - keep the unit cards up in battle")
    return
  end
  local cn = R12.child_count(holder.uic)
  local lim = cn
  if lim > R12.child_max then lim = R12.child_max end
  R12.out("UNITIDHOLDER children=" .. tostring(cn) .. " listed=" .. tostring(lim))
  for j = 0, lim - 1 do
    R12.call("unit_id_holder:Find(" .. tostring(j) .. ") + Id/ChildCount/GetStateText")
    local ch = R12.child_at(holder.uic, j)
    local cid = R12.id_of(ch)
    local ccn = tostring(R12.child_count(ch))
    local st = nil
    if ch ~= nil then
      R12.call("unit_id child GetStateText()")
      st = R12.read_text(function() return ch:GetStateText() end)
    end
    local numeric = R12.is_numeric(cid)
    R12.out("UNITIDCHILD " .. tostring(j) .. " id=" .. q(cid) .. " children=" .. ccn
      .. " numeric=" .. tostring(numeric) .. " stext=" .. q(st))
    R12.children[#R12.children + 1] = { id = cid, uic = ch, numeric = numeric, stext = st }
    if numeric and ch ~= nil then
      R12.seeds[#R12.seeds + 1] = { uic = ch, path = "unit_id_holder/" .. tostring(cid), id = cid }
    end
  end
  R12.out("STEP 2 done: " .. tostring(#R12.children) .. " child(ren), "
    .. tostring(#R12.seeds) .. " numeric unit-id seed(s)")
end

-- STEP 3 - descend EVERY unit-id subtree to DEPTH 8 (800 visits TOTAL). Only
-- proven-safe primitives. Paths are RELATIVE to the unit-id seed (seed = depth 1).
R12.steps[3] = function()
  R12.out("STEP 3 - descend EVERY unit-id subtree (seeds=" .. tostring(#R12.seeds)
    .. ", budget " .. tostring(R12.descend_visits) .. " visits, depth "
    .. tostring(R12.descend_depth) .. ")")
  R12.located = {}
  R12.located_order = {}
  R12.located_list = {}
  R12.descend_count = 0
  R12.desc_seen = {}
  if R12.seeds == nil or #R12.seeds == 0 then
    R12.out("STEP 3 aborted: no numeric unit-id seed came out of step 2 - open AND PIN"
      .. " the unit-info panel and keep the cards panel up with >=2 units")
    return
  end
  local function descend(uic, path, depth)
    if uic == nil then return end
    if R12.descend_count >= R12.descend_visits then return end
    if depth > R12.descend_depth then return end
    -- repeat / cycle guard keyed on the COMPONENT (paths collide when sibling ids
    -- repeat - e.g. every stat row is id "template_stat")
    if R12.desc_seen[uic] ~= nil then return end
    R12.desc_seen[uic] = true
    R12.descend_count = R12.descend_count + 1
    local id = R12.id_of(uic)
    R12.call("DOWN " .. q(path) .. ":ChildCount()")
    local cn = R12.child_count(uic)
    R12.call("DOWN " .. q(path) .. ":GetStateText() + CurrentState() + Visible/VisibleFromRoot")
    local st = R12.read_text(function() return uic:GetStateText() end)
    local cs = R12.read_text(function() return uic:CurrentState() end)
    local vis, vfr = R12.vis_of(uic)
    R12.out("DOWN path=" .. q(path) .. " id=" .. q(id) .. " children=" .. tostring(cn)
      .. " stext=" .. q(st) .. " state=" .. q(cs)
      .. " vis=" .. tostring(vis) .. " vfr=" .. tostring(vfr))
    if id ~= nil and R12.is_located_id(id) and #R12.located_list < R12.locate_max then
      local rec = { id = id, uic = uic, path = path }
      R12.located_list[#R12.located_list + 1] = rec
      if R12.located[id] == nil then
        R12.located[id] = rec
        R12.located_order[#R12.located_order + 1] = id
      end
    end
    if depth >= R12.descend_depth then return end
    for i = 0, cn - 1 do
      if R12.descend_count >= R12.descend_visits then return end
      R12.call("DOWN " .. q(path) .. ":Find(" .. tostring(i) .. ")")
      local ch = R12.child_at(uic, i)
      if ch ~= nil then
        local cid = R12.id_of(ch)
        if cid == nil or cid == "" then cid = "#" .. tostring(i) end
        descend(ch, path .. "/" .. cid, depth + 1)
      end
    end
  end
  for i = 1, #R12.seeds do
    local s = R12.seeds[i]
    descend(s.uic, s.path, 1)
  end
  R12.out("STEP 3 done: visits=" .. tostring(R12.descend_count)
    .. " located=" .. tostring(#R12.located_order))
end

-- STEP 4 - locate the stat-row nodes (path + id) and pair every template_stat
-- row's stat_name with its dy_value.
R12.steps[4] = function()
  R12.out("STEP 4 - locate the stat-row nodes and pair each row's name with its value")
  R12.rows = {}
  if R12.located_order == nil or #R12.located_order == 0 then
    R12.out("STEP 4: the descent located NO stat-row node (health_and_stats / dynamic_stats /"
      .. " template_stat / stat_name / value_holder / dy_value). Grep the DOWN lines - the panel"
      .. " may sit deeper than depth " .. tostring(R12.descend_depth) .. " or under a non-unit-id node")
  end
  for k = 1, #(R12.located_order or {}) do
    local id = R12.located_order[k]
    local rec = R12.located[id]
    if rec ~= nil then
      R12.out("LOCATED path=" .. q(rec.path) .. " id=" .. q(id)
        .. " children=" .. tostring(R12.child_count(rec.uic)))
    end
  end
  -- find a child of `uic` whose Id() == want (bounded by child_max)
  local function child_named(uic, want)
    if uic == nil then return nil end
    local cn = R12.child_count(uic)
    local lim = cn
    if lim > R12.child_max then lim = R12.child_max end
    for i = 0, lim - 1 do
      R12.call("child " .. q(want) .. " under " .. q(R12.id_of(uic)) .. ":Find(" .. tostring(i) .. ")")
      local ch = R12.child_at(uic, i)
      if ch ~= nil and R12.id_of(ch) == want then return ch end
    end
    return nil
  end
  local function read_row(row_uic, n, row_path)
    local sn = child_named(row_uic, "stat_name")
    local vh = child_named(row_uic, "value_holder")
    local dv = nil
    if vh ~= nil then dv = child_named(vh, "dy_value") end
    if dv == nil then dv = child_named(row_uic, "dy_value") end
    local name_text, val_text = nil, nil
    if sn ~= nil then
      R12.call("stat_name:GetStateText()")
      name_text = R12.read_text(function() return sn:GetStateText() end)
    end
    if dv ~= nil then
      R12.call("dy_value:GetStateText()")
      val_text = R12.read_text(function() return dv:GetStateText() end)
    end
    R12.out("PANEL row=" .. tostring(n) .. " name=" .. q(name_text) .. " value=" .. q(val_text)
      .. " path=" .. q(row_path))
    R12.rows[#R12.rows + 1] = { n = n, name = name_text, value = val_text, uic = row_uic, path = row_path }
  end
  -- every located template_stat is one stat row
  local n = 0
  for k = 1, #(R12.located_list or {}) do
    local rec = R12.located_list[k]
    if rec.id == "template_stat" then
      n = n + 1
      read_row(rec.uic, n, rec.path)
    end
  end
  -- fallback: a located dynamic_stats whose template_stat children were not
  -- themselves located (defensive; the descent normally visits them)
  if n == 0 then
    local ds = R12.located["dynamic_stats"]
    if ds ~= nil then
      local cn = R12.child_count(ds.uic)
      local lim = cn
      if lim > R12.child_max then lim = R12.child_max end
      for i = 0, lim - 1 do
        R12.call("dynamic_stats:Find(" .. tostring(i) .. ") looking for template_stat")
        local ch = R12.child_at(ds.uic, i)
        if ch ~= nil and R12.id_of(ch) == "template_stat" then
          n = n + 1
          read_row(ch, n, ds.path .. "/template_stat[" .. tostring(i) .. "]")
        end
      end
    end
  end
  -- fallback: a lone located stat_name (+ a located dy_value, if any)
  if n == 0 and R12.located["stat_name"] ~= nil then
    R12.call("stat_name:GetStateText()")
    local t = R12.read_text(function() return R12.located["stat_name"].uic:GetStateText() end)
    local v = nil
    local dv = R12.located["dy_value"]
    if dv ~= nil then
      R12.call("dy_value:GetStateText()")
      v = R12.read_text(function() return dv.uic:GetStateText() end)
    end
    n = n + 1
    R12.out("PANEL row=" .. tostring(n) .. " name=" .. q(t) .. " value=" .. q(v)
      .. " path=" .. q(R12.located["stat_name"].path))
    R12.rows[#R12.rows + 1] = { n = n, name = t, value = v }
  end
  R12.out("STEP 4 done: rows=" .. tostring(#R12.rows)
    .. " located=" .. tostring(#(R12.located_order or {})))
end

-- STEP 5 - read GetContextObjectId (CcoUnitDetails / CcoUnitStat / CcoBattleUnit)
-- on the located row components (READS only).
R12.steps[5] = function()
  R12.out("STEP 5 - read GetContextObjectId on the located row components (reads only)")
  R12.ctx = {}
  R12.ctx_from = {}
  R12.selected_ui = nil
  R12.sel_tid = nil
  R12.sel_id = nil
  if R12.located_list == nil or #R12.located_list == 0 then
    R12.out("STEP 5: nothing was located - no context id to read")
    return
  end
  local probed = 0
  for k = 1, #R12.located_list do
    if probed >= R12.ctx_max then break end
    local rec = R12.located_list[k]
    probed = probed + 1
    for t = 1, #R12.ctx_types do
      local tid = R12.ctx_types[t]
      R12.call(q(rec.path) .. " GetContextObjectId(" .. tid .. ")")
      local ok, raw = pcall(function() return rec.uic:GetContextObjectId(tid) end)
      local text = nil
      if ok then text = safe_text(raw) end
      R12.out("CTXID " .. q(rec.path) .. " " .. tid .. " -> " .. (ok and q(text) or "<ERR>"))
      if ok and text ~= nil and text ~= "" and R12.ctx[tid] == nil then
        R12.ctx[tid] = text
        R12.ctx_from[tid] = rec.path
      end
    end
  end
  -- the SELECTED unit's context id = the first non-nil one (a read off the panel)
  for i = 1, #R12.ctx_types do
    local tid = R12.ctx_types[i]
    if R12.ctx[tid] ~= nil then R12.sel_tid = tid; R12.sel_id = R12.ctx[tid]; break end
  end
  if R12.sel_tid == nil then
    R12.out("STEP 5: NO context id came back (all nil) - step 6 will have nothing to query")
    return
  end
  -- the SELECTED unit's ui id = the numeric segment right after unit_id_holder in
  -- the path the selected context id came from (recorded data only - no new read)
  local from = R12.ctx_from[R12.sel_tid]
  if from ~= nil then
    local rest = R12.strip_prefix(from, "unit_id_holder/")
    local seg = R12.first_segment(rest)
    if seg ~= nil and R12.is_numeric(seg) then R12.selected_ui = seg end
  end
  R12.out("STEP 5 done: ctx_ids=" .. tostring(R12.count_ctx())
    .. " selected_type=" .. tostring(R12.sel_tid) .. " selected_id=" .. q(R12.sel_id)
    .. " selected_ui=" .. q(R12.selected_ui))
end

-- STEP 6 - EXACTLY TWO common.get_context_value calls (vanilla shape, ZERO
-- SetContextObject): the SELECTED unit's context id, then a NON-selected ui id.
R12.steps[6] = function()
  local field = R12.fields[1]
  R12.out("STEP 6 - EXACTLY TWO common.get_context_value calls (vanilla shape, field="
    .. tostring(field) .. ")")
  R12.gcv_calls = 0
  if R12.sel_tid == nil or R12.sel_id == nil then
    R12.out("STEP 6: no context id came out of step 5 - both queries are skipped (0 calls made)")
    return
  end
  -- (a) the SELECTED unit's context id (read off the panel in step 5)
  R12.call("common.get_context_value(" .. R12.sel_tid .. ", " .. q(R12.sel_id) .. ", " .. q(field) .. ")")
  local ok1, v1 = pcall(function() return common.get_context_value(R12.sel_tid, R12.sel_id, field) end)
  R12.gcv_calls = R12.gcv_calls + 1
  local t1 = ok1 and text_of(v1, true) or "<ERR>"
  if t1 == nil then t1 = "<nil>" end
  R12.out("QUERY sel=" .. q(R12.sel_id) .. " type=" .. R12.sel_tid .. " field=" .. field
    .. " -> " .. q(t1) .. " (from " .. tostring(R12.ctx_from[R12.sel_tid]) .. ")")
  -- (b) a NON-selected unit's ui id (a numeric unit-id under unit_id_holder,
  --     other than the selected one) - the field-proven CcoBattleUnit ui-id shape
  local nonsel = nil
  for i = 1, #R12.children do
    local c = R12.children[i]
    if c.numeric and c.id ~= nil and tostring(c.id) ~= tostring(R12.selected_ui) then
      nonsel = tostring(c.id); break
    end
  end
  if nonsel == nil then
    R12.out("QUERY nonsel: no NON-selected numeric unit-id under unit_id_holder"
      .. " (keep the cards panel up with >=2 units)")
    return
  end
  R12.out("QUERY nonsel unit ui id=" .. q(nonsel) .. " (selected_ui=" .. q(R12.selected_ui) .. ")")
  R12.call("common.get_context_value(\"CcoBattleUnit\", " .. q(nonsel) .. ", " .. q(field) .. ")")
  local ok2, v2 = pcall(function() return common.get_context_value("CcoBattleUnit", nonsel, field) end)
  R12.gcv_calls = R12.gcv_calls + 1
  local t2 = ok2 and text_of(v2, true) or "<ERR>"
  if t2 == nil then t2 = "<nil>" end
  R12.out("QUERY nonsel=" .. q(nonsel) .. " type=CcoBattleUnit field=" .. field .. " -> " .. q(t2))
  R12.out("STEP 6 done: get_context_value calls=" .. tostring(R12.gcv_calls) .. " (want 2)")
end

-- ---------------------------------------------------------------- the driver
function R12.advance()
  if R12.done then
    R12.out("step ignored: the run is done (" .. tostring(R12.total_steps)
      .. " steps) - zz_probe_r12() restarts it")
    return R12.step
  end
  R12.step = R12.step + 1
  local fn = R12.steps[R12.step]
  if fn == nil then
    R12.done = true
    R12.out("===== ROUND 12 RUN done after " .. tostring(R12.total_steps)
      .. " steps (reads only; zero writes) - R12 TOTAL STEPS 6 - YOU ARE DONE =====")
    return R12.step
  end
  R12.out("")
  R12.out("===== R12 STEP " .. tostring(R12.step) .. "/" .. tostring(R12.total_steps)
    .. " (t=" .. tostring(tick_count) .. ") =====")
  local ok, err = pcall(fn)
  if not ok then
    R12.out("STEP " .. tostring(R12.step) .. " raised (swallowed): " .. truncate(err, 160))
  end
  return R12.step
end

function zz_probe_r12()
  R12.step = 0
  R12.done = false
  R12.roots = {}
  R12.children = {}
  R12.seeds = {}
  R12.located = {}
  R12.located_order = {}
  R12.located_list = {}
  R12.descend_count = 0
  R12.desc_seen = {}
  R12.rows = {}
  R12.ctx = {}
  R12.ctx_from = {}
  R12.selected_ui = nil
  R12.sel_tid = nil
  R12.sel_id = nil
  R12.gcv_calls = 0
  return PROBE_TAG .. "R12 READY (step 0 of 6). R12 TOTAL STEPS 6 - you are done after step 6."
    .. " In battle, open AND PIN the unit-info panel and keep the cards panel up with >=2 units,"
    .. " then call zz_probe_r12_step() ONE step at a time (after each step, if the game is alive,"
    .. " type the next). Step " .. tostring(R12.total_steps) .. " is the LAST step - stop there."
    .. " log=" .. LOG_FILE
end

function zz_probe_r12_step()
  if R12.step == 0 and (not R12.done) then
    R12.run_no = R12.run_no + 1
    R12.lines = 0
    R12.line_cap_spoken = false
    R12.out("")
    R12.out("===== ROUND 12 RUN #" .. tostring(R12.run_no)
      .. " (manual zz_probe_r12_step) t=" .. tostring(tick_count) .. " =====")
    R12.out("R12 TOTAL STEPS 6 - you are done after step 6. Seed the descent on the NUMERIC"
      .. " unit-id nodes under unit_id_holder; descend to DEPTH " .. tostring(R12.descend_depth)
      .. " with a " .. tostring(R12.descend_visits) .. "-visit budget; pair the stat rows;"
      .. " read the CcoUnitDetails / CcoUnitStat / CcoBattleUnit context ids; then run EXACTLY"
      .. " TWO common.get_context_value calls. Every native call is logged BEFORE it is made;"
      .. " ZERO SetContextObject; simhover DISARMED; the name-lookup helper is BANNED.")
  end
  local before = R12.step
  R12.advance()
  local nxt
  if R12.done or R12.step >= R12.total_steps or R12.steps[R12.step + 1] == nil then
    nxt = "DONE - STOP (zz_probe_r12 finished after " .. tostring(R12.total_steps) .. " steps)"
  else
    nxt = "step " .. tostring(R12.step + 1) .. " of " .. tostring(R12.total_steps)
  end
  return PROBE_TAG .. "R12 step " .. tostring(R12.step) .. "/" .. tostring(R12.total_steps)
    .. " done (was " .. tostring(before) .. "); next: " .. nxt
    .. " - call zz_probe_r12_step() again. log=" .. LOG_FILE
end

function zz_probe_r12_auto()
  if R12.step == 0 and (not R12.done) then zz_probe_r12() end
  R12.run_no = R12.run_no + 1
  R12.lines = 0
  R12.line_cap_spoken = false
  R12.out("")
  R12.out("===== ROUND 12 AUTO RUN #" .. tostring(R12.run_no) .. " t=" .. tostring(tick_count)
    .. " - runs every step to the cap; a fatal call dies here and the last R12 CALL names it =====")
  local guard = 0
  while (not R12.done) and guard < 40 do
    guard = guard + 1
    R12.advance()
  end
  return PROBE_TAG .. "R12 auto finished (step=" .. tostring(R12.step)
    .. (R12.done and ", done" or ", cap") .. "). log=" .. LOG_FILE
end

function zz_probe_r12_status()
  return PROBE_TAG .. "R12 TOTAL STEPS " .. tostring(R12.total_steps) .. " - run="
    .. tostring(R12.run_no) .. " step=" .. tostring(R12.step) .. "/" .. tostring(R12.total_steps)
    .. " done=" .. tostring(R12.done) .. " lines=" .. tostring(R12.lines)
    .. "/" .. tostring(R12.max_lines)
    .. " | roots=" .. tostring(#(R12.roots or {}))
    .. " seeds=" .. tostring(#(R12.seeds or {}))
    .. " descend_visits=" .. tostring(R12.descend_count) .. "/" .. tostring(R12.descend_visits)
    .. " located=" .. tostring(#(R12.located_order or {}))
    .. " rows=" .. tostring(#(R12.rows or {}))
    .. " ctx_ids=" .. tostring(R12.count_ctx())
    .. " gcv_calls=" .. tostring(R12.gcv_calls)
    .. " | zz_probe_r12() to start/restart; log=" .. LOG_FILE
end

function zz_probe_r12_help()
  return PROBE_TAG .. "R12 FINISH THE PANEL HUNT. R12 TOTAL STEPS 6 - you are done after step 6."
    .. " Start a battle, open AND PIN the unit-info panel, and keep the cards panel up with >=2"
    .. " units. Call zz_probe_r12() once, then zz_probe_r12_step() SIX times ("
    .. tostring(R12.total_steps) .. " total; STOP after step " .. tostring(R12.total_steps) .. ")."
    .. " Step 1 lists the top-level roots; step 2 lists unit_id_holder's children and keeps the"
    .. " NUMERIC unit-id nodes (1001, 1002, ...) as seeds; step 3 descends EVERY unit-id subtree to"
    .. " depth " .. tostring(R12.descend_depth) .. " (budget " .. tostring(R12.descend_visits)
    .. " visits), logging R12 DOWN path/id/children/stext for every node; step 4 locates the panel"
    .. " nodes (health_and_stats/dynamic_stats/template_stat/stat_name/value_holder/dy_value) and"
    .. " pairs every row (R12 PANEL row=.. name=.. value=..); step 5 reads GetContextObjectId for"
    .. " CcoUnitDetails/CcoUnitStat/CcoBattleUnit on the located rows (R12 CTXID); step 6 runs"
    .. " EXACTLY TWO common.get_context_value calls - ONE with the SELECTED unit's context id, ONE"
    .. " with a NON-selected unit's ui id (R12 QUERY sel=/nonsel=). zz_probe_r12_auto() runs every"
    .. " step to the cap. ZERO writes; simhover DISARMED; the name-lookup helper is BANNED. Log: "
    .. LOG_FILE
end
