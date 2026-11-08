-- ============================================================================
-- 15. ROUND 11 - COMPLETE UI-ROOT ENUMERATION, THEN DESCEND TO THE STAT PANEL
--     AND ASK ONE DECISIVE get_context_value (the round-10 post-mortem build).
--
--     WHY. Round 10's step 1 enumerated the 25 top-level children of
--     core:get_ui_root() perfectly (ChildCount + Find(i)) - that route is proven
--     SAFE. Step 2 (the children of a few roots) also ran safely but stopped
--     before covering the other 22 roots. Step 3 then called the engine's
--     name-lookup helper (the vanilla "find by name" shape) and THE GAME DIED on
--     that call. THAT HELPER IS BANNED FROM THIS FILE - there is no call site for
--     it anywhere below, and build_and_install.py asserts the token is absent
--     from the shipped probe. The two other name finders (the script-tag and the
--     sequential finder) stay deleted too - neither has a call site in any
--     shipped script.
--
--     THE PLAN (all READ-ONLY; ZERO SetContextObject; simhover DISARMED; one
--     native call per armed console step, each logged BEFORE it is made):
--       STEP 1 - enumerate the top-level roots (ChildCount + Find(i)).
--       STEP 2 - list EVERY root's children (budget 40 each), tagging any id
--                containing unit/panel/info/stat/card/left/right/tactical as a
--                HINT - the unit-info panel lives SOMEWHERE in this tree.
--       STEP 3 - descend TWO more levels below every hint-tagged root or child
--                (budget 400 visits TOTAL for the step, depth 4 from the UI
--                root), logging the full path of every node visited. This is how
--                the panel and its stat rows are FOUND:
--                dynamic_stats > template_stat > stat_name / value_holder > dy_value.
--       STEP 4 - log every located panel component (path + children), read the
--                stat rows (stat_name -> value_holder/dy_value via GetStateText)
--                and the CcoUnitDetails / CcoUnitStat / CcoBattleUnit context ids
--                on the located components (GetContextObjectId only - a read).
--       STEP 5 - ONE decisive query, run twice with the SAME field: first with
--                the selected unit's context id (from step 4), then with a
--                NON-selected card's ui id: common.get_context_value(<type>,
--                <id>, "StatList.Size") - the vanilla call shape.
--
--     USE ONLY THE PROVEN-SAFE PRIMITIVES: ChildCount, Find, Id, Visible,
--     VisibleFromRoot, CurrentState, GetStateText. Every engine read is
--     pcall-walled, so a raising read can never take the walk down.
-- ============================================================================

local R11 = {
  run_no       = 0,
  step         = 0,          -- 0 = not started; +1 per armed step
  done         = false,
  lines        = 0,
  max_lines    = 6000,       -- HARD CAP on R11 log lines
  line_cap_spoken = false,
  -- hard enumeration budgets
  root_max       = 40,       -- top-level roots logged (step 1)
  child_max      = 40,       -- children per root (step 2) AND per child probe (step 4)
  descend_visits = 400,      -- step 3 TOTAL visits
  descend_depth  = 4,        -- step 3 max depth from the UI root
  -- hint substrings: an id containing ANY of these is tagged a HINT
  hints = { "unit", "panel", "info", "stat", "card", "left", "right", "tactical" },
  -- the panel components the descent is hunting (their ids)
  stat_ids = { ["dynamic_stats"] = true, ["template_stat"] = true,
               ["stat_name"] = true, ["value_holder"] = true, ["dy_value"] = true },
  -- step-1 output
  roots        = {},         -- { id, uic }
  -- step-2 output
  children     = {},         -- { id, uic, parent, root_id, hint }
  -- step-3 output
  located      = {},         -- id -> { uic, path }
  located_order = {},        -- ids in discovery order
  descend_count = 0,
  -- step-4 output
  rows         = {},         -- { n, name, value }
  ctx          = {},         -- type_id -> context id (non-nil, first kept)
  ctx_from     = {},         -- type_id -> path the id came from
  -- step-5
  fields       = { "StatList.Size" },          -- THE single decisive field
  ctx_types    = { "CcoUnitDetails", "CcoUnitStat", "CcoBattleUnit" },
}

-- ---------------------------------------------------------------- R11 logging
function R11.out(msg)
  if R11.lines >= R11.max_lines then
    if not R11.line_cap_spoken then
      R11.line_cap_spoken = true
      log("R11 line cap reached (" .. tostring(R11.max_lines) .. ") - further R11 lines are not logged")
    end
    return
  end
  R11.lines = R11.lines + 1
  log("R11 " .. tostring(msg))
end

-- ALWAYS call this IMMEDIATELY before a native call: it is the line that names
-- the fatal call if the engine dies on the next statement.
function R11.call(desc)
  R11.out("CALL " .. tostring(R11.step) .. " " .. tostring(desc))
end

function R11.read_text(fn)
  local ok, v = pcall(fn)
  if not ok then return "<ERR>" end
  if v == nil then return nil end
  local s = safe_text(v)
  if s ~= nil then return s end
  return "<opaque>"
end

-- ---------------------------------------------------- proven-shape primitives
function R11.ui_root()
  R11.call("core:get_ui_root()")
  local ok, r = pcall(function() return core:get_ui_root() end)
  if not ok or r == nil then return nil end
  return r
end

function R11.child_count(uic)
  if uic == nil then return 0 end
  local n = read1(function() return uic:ChildCount() end)
  if lua_type(n) == "number" then return n end
  return 0
end

-- uic:Find(i) -> a child, or nil. The result is TRUTHINESS-guarded (never wrap a
-- boolean: the round-9 crash).
function R11.child_at(uic, i)
  if uic == nil then return nil end
  local ok, raw = pcall(function() return uic:Find(i) end)
  if not ok or raw == nil or raw == false then return nil end
  return wrap(raw)
end

function R11.id_of(uic)
  if uic == nil then return nil end
  return R11.read_text(function() return uic:Id() end)
end

function R11.vis_of(uic)
  if uic == nil then return nil, nil end
  local vis = readb(function() return uic:Visible() end)
  local vfr = readb(function() return uic:VisibleFromRoot() end)
  return tostring(vis), tostring(vfr)
end

-- the HINT test: does an id contain any of the hint substrings?
function R11.hint_of(id)
  if id == nil or id == "" then return nil end
  local low = string.lower(id)
  for i = 1, #R11.hints do
    if contains_str(low, R11.hints[i]) then return R11.hints[i] end
  end
  return nil
end

function R11.count_located()
  local n = 0
  for _ in pairs(R11.located) do n = n + 1 end
  return n
end

function R11.count_ctx()
  local n = 0
  for _ in pairs(R11.ctx) do n = n + 1 end
  return n
end

-- ---------------------------------------------------------------- the steps
R11.steps = {}

-- STEP 1 - enumerate the top-level children of the global UI root.
R11.steps[1] = function()
  R11.out("STEP 1 - enumerate the UI root's top-level children (budget "
    .. tostring(R11.root_max) .. ")")
  local root = R11.ui_root()
  if root == nil then
    R11.out("STEP 1 aborted: core:get_ui_root() returned nil")
    return
  end
  local n = R11.child_count(root)
  R11.out("ROOTCOUNT " .. tostring(n))
  if n <= 0 then
    R11.out("STEP 1: the UI root has no children yet (battle not up?)")
    return
  end
  R11.roots = {}
  local lim = n
  if lim > R11.root_max then lim = R11.root_max end
  for i = 0, lim - 1 do
    R11.call("ui_root:Find(" .. tostring(i) .. ") + Id/ChildCount/Visible/VisibleFromRoot")
    local uic = R11.child_at(root, i)
    local id = R11.id_of(uic)
    local vis, vfr = R11.vis_of(uic)
    local cn = tostring(R11.child_count(uic))
    R11.out("ROOT " .. tostring(i) .. " id=" .. q(id) .. " vis=" .. tostring(vis)
      .. " vfr=" .. tostring(vfr) .. " children=" .. cn)
    R11.roots[#R11.roots + 1] = { uic = uic, id = id }
  end
  if n > lim then
    R11.out("ROOT ... (" .. tostring(n - lim) .. " more root(s) not listed; cap "
      .. tostring(R11.root_max) .. ")")
  end
end

-- STEP 2 - EVERY root's children (~one level deeper), with the hint tag.
R11.steps[2] = function()
  R11.out("STEP 2 - every root's children (budget " .. tostring(R11.child_max) .. " each)")
  if R11.roots == nil or #R11.roots == 0 then
    R11.out("STEP 2 aborted: no roots recorded by step 1")
    return
  end
  R11.children = {}
  for ri = 1, #R11.roots do
    local r = R11.roots[ri]
    R11.call("root " .. q(r.id) .. ":ChildCount()")
    local cn = R11.child_count(r.uic)
    local lim = cn
    if lim > R11.child_max then lim = R11.child_max end
    R11.out("ROOTCHILD root=" .. q(r.id) .. " children=" .. tostring(cn)
      .. " listed=" .. tostring(lim))
    for j = 0, lim - 1 do
      R11.call("root " .. q(r.id) .. ":Find(" .. tostring(j) .. ")")
      local ch = R11.child_at(r.uic, j)
      local cid = R11.id_of(ch)
      local ccn = tostring(R11.child_count(ch))
      local hint = R11.hint_of(cid)
      R11.out("ROOTCHILD " .. q(r.id) .. " " .. tostring(j) .. " id=" .. q(cid)
        .. " children=" .. ccn .. " hint=" .. tostring(hint))
      R11.children[#R11.children + 1] =
        { id = cid, uic = ch, parent = ri, root_id = r.id, hint = hint }
    end
  end
  R11.out("STEP 2 done: " .. tostring(#R11.children) .. " child component(s) listed across "
    .. tostring(#R11.roots) .. " root(s)")
end

-- STEP 3 - descend two levels below every hint-tagged root/child, hunting the
-- panel components (dynamic_stats / template_stat / stat_name / value_holder /
-- dy_value). ONE shared 400-visit budget, depth 4 from the UI root.
R11.steps[3] = function()
  R11.out("STEP 3 - descend two levels below hint-tagged nodes (budget "
    .. tostring(R11.descend_visits) .. " visits, depth " .. tostring(R11.descend_depth) .. ")")
  R11.located = {}
  R11.located_order = {}
  R11.descend_count = 0
  if R11.roots == nil or #R11.roots == 0 then
    R11.out("STEP 3 aborted: no roots recorded by step 1")
    return
  end
  -- seeds: hint-tagged roots (below 2), plus hint-tagged children whose own
  -- root is NOT a hint (so a hinted root's children are not descended twice).
  local seeds = {}
  for i = 1, #R11.roots do
    local r = R11.roots[i]
    if R11.hint_of(r.id) ~= nil then
      seeds[#seeds + 1] = { uic = r.uic, path = tostring(r.id), depth = 1, below = 2 }
    end
  end
  for i = 1, #R11.children do
    local c = R11.children[i]
    if c.hint ~= nil then
      local pr = R11.roots[c.parent]
      local parent_hinted = (pr ~= nil and R11.hint_of(pr.id) ~= nil)
      if not parent_hinted then
        seeds[#seeds + 1] = { uic = c.uic, path = tostring(c.root_id) .. "/" .. tostring(c.id),
                              depth = 2, below = 2 }
      end
    end
  end
  R11.out("STEP 3 seeds: " .. tostring(#seeds) .. " hinted node(s)")
  local function descend(uic, path, depth, below)
    if uic == nil then return end
    if R11.descend_count >= R11.descend_visits then return end
    if depth > R11.descend_depth then return end
    R11.descend_count = R11.descend_count + 1
    local id = R11.id_of(uic)
    R11.call("DESCEND " .. q(path) .. ":ChildCount()")
    local cn = R11.child_count(uic)
    R11.out("DESCEND path=" .. q(path) .. " id=" .. q(id) .. " children=" .. tostring(cn))
    if id ~= nil and R11.stat_ids[id] ~= nil and R11.located[id] == nil then
      R11.located[id] = { uic = uic, path = path }
      R11.located_order[#R11.located_order + 1] = id
    end
    if below <= 0 or depth >= R11.descend_depth then return end
    for i = 0, cn - 1 do
      if R11.descend_count >= R11.descend_visits then return end
      R11.call("DESCEND " .. q(path) .. ":Find(" .. tostring(i) .. ")")
      local ch = R11.child_at(uic, i)
      if ch ~= nil then
        local cid = R11.id_of(ch)
        if cid == nil or cid == "" then cid = "#" .. tostring(i) end
        descend(ch, path .. "/" .. cid, depth + 1, below - 1)
      end
    end
  end
  for i = 1, #seeds do
    local s = seeds[i]
    descend(s.uic, s.path, s.depth, s.below)
  end
  R11.out("STEP 3 done: visits=" .. tostring(R11.descend_count)
    .. " located=" .. tostring(R11.count_located()))
end

-- STEP 4 - read the located stat rows + the context ids (GetContextObjectId).
R11.steps[4] = function()
  R11.out("STEP 4 - read the located stat rows + the component context ids")
  R11.rows = {}
  R11.ctx = {}
  R11.ctx_from = {}
  if #R11.located_order == 0 then
    R11.out("STEP 4: the descent located NO panel component (dynamic_stats/template_stat/"
      .. "stat_name/value_holder/dy_value). Grep the DESCEND lines - the panel may sit deeper"
      .. " than depth " .. tostring(R11.descend_depth) .. " or under a non-hint root.")
  end
  -- find a child of `uic` whose Id() == want (bounded by child_max)
  local function child_named(uic, want)
    if uic == nil then return nil end
    local cn = R11.child_count(uic)
    local lim = cn
    if lim > R11.child_max then lim = R11.child_max end
    for i = 0, lim - 1 do
      R11.call("child " .. q(want) .. " under " .. q(R11.id_of(uic)) .. ":Find(" .. tostring(i) .. ")")
      local ch = R11.child_at(uic, i)
      if ch ~= nil and R11.id_of(ch) == want then return ch end
    end
    return nil
  end
  local function read_row(row, n)
    local sn = child_named(row, "stat_name")
    local vh = child_named(row, "value_holder")
    local dv = nil
    if vh ~= nil then dv = child_named(vh, "dy_value") end
    if dv == nil then dv = child_named(row, "dy_value") end
    local name_text, val_text = nil, nil
    if sn ~= nil then
      R11.call("stat_name:GetStateText()")
      name_text = R11.read_text(function() return sn:GetStateText() end)
    end
    if dv ~= nil then
      R11.call("dy_value:GetStateText()")
      val_text = R11.read_text(function() return dv:GetStateText() end)
    end
    R11.out("PANEL n=" .. tostring(n) .. " name=" .. q(name_text) .. " value=" .. q(val_text))
    R11.rows[#R11.rows + 1] = { n = n, name = name_text, value = val_text }
  end
  -- collect the stat rows: every template_stat child of a located dynamic_stats,
  -- else the located template_stat itself, else a lone located stat_name.
  local n = 0
  local ds = R11.located["dynamic_stats"]
  if ds ~= nil then
    local cn = R11.child_count(ds.uic)
    local lim = cn
    if lim > R11.child_max then lim = R11.child_max end
    for i = 0, lim - 1 do
      R11.call("dynamic_stats:Find(" .. tostring(i) .. ") looking for template_stat")
      local ch = R11.child_at(ds.uic, i)
      if ch ~= nil and R11.id_of(ch) == "template_stat" then
        n = n + 1
        read_row(ch, n)
      end
    end
  end
  if n == 0 and R11.located["template_stat"] ~= nil then
    n = n + 1
    read_row(R11.located["template_stat"].uic, n)
  end
  if n == 0 and R11.located["stat_name"] ~= nil then
    R11.call("stat_name:GetStateText()")
    local t = R11.read_text(function() return R11.located["stat_name"].uic:GetStateText() end)
    n = n + 1
    R11.out("PANEL n=" .. tostring(n) .. " name=" .. q(t) .. " value=" .. q(nil))
  end
  R11.out("STEP 4 rows=" .. tostring(#R11.rows))
  -- the context ids on every located component (a READ: GetContextObjectId)
  for k = 1, #R11.located_order do
    local id = R11.located_order[k]
    local rec = R11.located[id]
    if rec ~= nil then
      local cn = R11.child_count(rec.uic)
      R11.out("LOCATED " .. q(id) .. " path=" .. q(rec.path) .. " children=" .. tostring(cn))
      for t = 1, #R11.ctx_types do
        local tid = R11.ctx_types[t]
        R11.call(q(rec.path) .. " GetContextObjectId(" .. tid .. ")")
        local ok, raw = pcall(function() return rec.uic:GetContextObjectId(tid) end)
        local text = nil
        if ok then text = safe_text(raw) end
        R11.out("CTXID " .. q(rec.path) .. " " .. tid .. " -> " .. (ok and q(text) or "<ERR>"))
        if ok and text ~= nil and text ~= "" and R11.ctx[tid] == nil then
          R11.ctx[tid] = text
          R11.ctx_from[tid] = rec.path
        end
      end
    end
  end
  R11.out("STEP 4 done: items=" .. tostring(#R11.located_order)
    .. " ctx_ids=" .. tostring(R11.count_ctx()))
end

-- STEP 5 - ONE decisive query, run twice: the selected unit's context id, then a
-- NON-selected card's ui id. Vanilla shape, ZERO SetContextObject.
R11.steps[5] = function()
  local field = R11.fields[1]
  R11.out("STEP 5 - ONE decisive common.get_context_value (field=" .. field .. ")")
  local sel_tid, sel_id = nil, nil
  for i = 1, #R11.ctx_types do
    local tid = R11.ctx_types[i]
    if R11.ctx[tid] ~= nil then sel_tid = tid; sel_id = R11.ctx[tid]; break end
  end
  if sel_tid == nil then
    R11.out("STEP 5: no context id came out of step 4 - the decisive query is skipped")
    return
  end
  -- (a) the SELECTED unit's context id (read off the panel in step 4)
  R11.call("common.get_context_value(" .. sel_tid .. ", " .. q(sel_id) .. ", " .. q(field) .. ")")
  local ok1, v1 = pcall(function() return common.get_context_value(sel_tid, sel_id, field) end)
  local t1 = ok1 and text_of(v1, true) or "<ERR>"
  if t1 == nil then t1 = "<nil>" end
  R11.out("QUERY selected type=" .. sel_tid .. " id=" .. q(sel_id) .. " field=" .. field
    .. " -> " .. q(t1) .. " (from " .. tostring(R11.ctx_from[sel_tid]) .. ")")
  -- (b) a NON-selected card's ui id
  local cards, sel = nil, nil
  local cok, c1 = pcall(r5_read_cards)
  if cok then cards = c1 end
  local sok, s1 = pcall(r5_selected_set, cards)
  if sok then sel = s1 end
  if cards == nil or #cards == 0 then
    R11.out("QUERY nonsel: no unit cards found (review_DY) - keep the cards panel up with >=2 units")
    return
  end
  local nonsel_id, nonsel_ctx = nil, nil
  for i = 1, #cards do
    local c = cards[i]
    if c.uic ~= nil and c.vis == "true" and not (c.id ~= nil and sel ~= nil and sel[c.id] == true) then
      nonsel_id = c.id
      local ok_id, raw = pcall(function() return c.uic:GetContextObjectId("CcoBattleUnit") end)
      if ok_id then nonsel_ctx = safe_text(raw) end
      break
    end
  end
  if nonsel_id == nil then
    R11.out("QUERY nonsel: no visible NON-selected card (>=2 units needed)")
    return
  end
  R11.out("QUERY nonsel card ui id=" .. q(nonsel_id) .. " (its CcoBattleUnit ctx id="
    .. q(nonsel_ctx) .. ")")
  R11.call("common.get_context_value(\"CcoBattleUnit\", " .. q(nonsel_id) .. ", " .. q(field) .. ")")
  local ok2, v2 = pcall(function()
    return common.get_context_value("CcoBattleUnit", nonsel_id, field)
  end)
  local t2 = ok2 and text_of(v2, true) or "<ERR>"
  if t2 == nil then t2 = "<nil>" end
  R11.out("QUERY nonsel type=CcoBattleUnit id=" .. q(nonsel_id) .. " field=" .. field
    .. " -> " .. q(t2))
end

-- ---------------------------------------------------------------- the driver
function R11.advance()
  if R11.done then
    R11.out("step ignored: the run is done - zz_probe_r11() restarts it")
    return R11.step
  end
  R11.step = R11.step + 1
  local fn = R11.steps[R11.step]
  if fn == nil then
    R11.done = true
    R11.out("===== ROUND 11 RUN done (reads only; zero writes) =====")
    return R11.step
  end
  R11.out("")
  R11.out("===== R11 STEP " .. tostring(R11.step) .. " (t=" .. tostring(tick_count) .. ") =====")
  local ok, err = pcall(fn)
  if not ok then
    R11.out("STEP " .. tostring(R11.step) .. " raised (swallowed): " .. truncate(err, 160))
  end
  return R11.step
end

function zz_probe_r11()
  R11.step = 0
  R11.done = false
  R11.roots = {}
  R11.children = {}
  R11.located = {}
  R11.located_order = {}
  R11.descend_count = 0
  R11.rows = {}
  R11.ctx = {}
  R11.ctx_from = {}
  return PROBE_TAG .. "R11 READY (step 0). In battle, open AND PIN the unit-info panel (keep the"
    .. " cards panel up with >=2 units), then call zz_probe_r11_step() ONE step at a time -"
    .. " after each step, if the game is still alive, type the next. Steps 1-2 are PROVEN SAFE."
    .. " Or zz_probe_r11_auto() to run to the cap. Log: " .. LOG_FILE
end

function zz_probe_r11_step()
  if R11.step == 0 and (not R11.done) then
    R11.run_no = R11.run_no + 1
    R11.lines = 0
    R11.line_cap_spoken = false
    R11.out("")
    R11.out("===== ROUND 11 RUN #" .. tostring(R11.run_no)
      .. " (manual zz_probe_r11_step) t=" .. tostring(tick_count) .. " =====")
    R11.out("FULL UI-root enumeration first (steps 1-2); then TWO-level descent below the hint"
      .. " nodes (step 3); then the stat rows + context ids (step 4) and ONE decisive"
      .. " common.get_context_value (step 5). Every native call is logged BEFORE it is made;"
      .. " ZERO SetContextObject; simhover DISARMED.")
  end
  local before = R11.step
  R11.advance()
  local nxt = R11.step + 1
  local nxt_name = R11.steps[nxt] ~= nil and ("step " .. tostring(nxt)) or "done"
  return PROBE_TAG .. "R11 step " .. tostring(R11.step) .. " done (was " .. tostring(before)
    .. "); next: " .. nxt_name .. " - call zz_probe_r11_step() again. log=" .. LOG_FILE
end

function zz_probe_r11_auto()
  if R11.step == 0 and (not R11.done) then zz_probe_r11() end
  R11.run_no = R11.run_no + 1
  R11.lines = 0
  R11.line_cap_spoken = false
  R11.out("")
  R11.out("===== ROUND 11 AUTO RUN #" .. tostring(R11.run_no) .. " t=" .. tostring(tick_count)
    .. " - runs every step until the cap; a fatal call dies here and the last R11 CALL names it =====")
  local guard = 0
  while (not R11.done) and guard < 40 do
    guard = guard + 1
    R11.advance()
  end
  return PROBE_TAG .. "R11 auto finished (step=" .. tostring(R11.step)
    .. (R11.done and ", done" or ", cap") .. "). log=" .. LOG_FILE
end

function zz_probe_r11_status()
  return PROBE_TAG .. "R11 run=" .. tostring(R11.run_no) .. " step=" .. tostring(R11.step)
    .. "/5 done=" .. tostring(R11.done) .. " lines=" .. tostring(R11.lines)
    .. "/" .. tostring(R11.max_lines)
    .. " | roots=" .. tostring(#(R11.roots or {}))
    .. " children=" .. tostring(#(R11.children or {}))
    .. " descend_visits=" .. tostring(R11.descend_count) .. "/" .. tostring(R11.descend_visits)
    .. " located=" .. tostring(R11.count_located())
    .. " rows=" .. tostring(#(R11.rows or {}))
    .. " ctx_ids=" .. tostring(R11.count_ctx())
    .. " | zz_probe_r11() to start/restart; log=" .. LOG_FILE
end

function zz_probe_r11_help()
  return PROBE_TAG .. "R11 COMPLETE-ENUMERATION + DESCENT: start a battle, open AND PIN the"
    .. " unit-info panel, and keep the cards panel up with >=2 units. Call zz_probe_r11() once,"
    .. " then zz_probe_r11_step() repeatedly (after each step, if the game is alive, call it"
    .. " again). Steps 1-2 are PROVEN SAFE (they only use core:get_ui_root() + ChildCount +"
    .. " Find(i) + Id): step 1 lists the top-level roots, step 2 lists EVERY root's children"
    .. " (budget " .. tostring(R11.child_max) .. ") and tags unit/panel/info/stat/card/left/right/"
    .. "tactical ids as HINTS. Step 3 descends two levels below every hint node (budget "
    .. tostring(R11.descend_visits) .. " visits, depth " .. tostring(R11.descend_depth)
    .. ") to FIND the panel (dynamic_stats/template_stat/stat_name/value_holder/dy_value)."
    .. " Step 4 reads the stat rows (stat_name -> value_holder/dy_value, GetStateText) and the"
    .. " CcoUnitDetails/CcoUnitStat/CcoBattleUnit context ids (GetContextObjectId). Step 5 makes"
    .. " ONE common.get_context_value(\"<type>\", \"<id>\", \"StatList.Size\") with the SELECTED"
    .. " unit's context id, then the same with a NON-selected card's ui id. The engine's"
    .. " name-lookup helper is BANNED from this file. ZERO writes. Log: " .. LOG_FILE
end
