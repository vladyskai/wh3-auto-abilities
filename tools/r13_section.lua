-- ============================================================================
-- 17. ROUND 13 - THE PANEL IS NOT UNDER unit_id_holder (THAT SUBTREE IS THE
--     ON-FIELD CARD). DESCEND **EVERY** TOP-LEVEL UI ROOT THAT HAS CHILDREN
--     (PRIORITY: hud_battle, panel_manager, under_advisor_docker, left, right,
--     tactical_hud, menu_bar, THEN THE REST) TO DEPTH 8 WITH A 1200-VISIT
--     BUDGET, AND MATCH COMPONENTS BY THE STABLE id PREFIX **CcoUnitStat**
--     (CASE-INSENSITIVE) AS WELL AS BY THE STRUCTURAL NAMES. PAIR THE STAT
--     ROWS, READ THE CONTEXT IDS, THEN ASK EXACTLY TWO get_context_value CALLS.
--
--     WHY. Round 12's step 3 seeded the descent on the NUMERIC unit-id nodes
--     under unit_id_holder and walked 532 of its 800 visits straight into the
--     ON-FIELD UNIT CARD (character_portrait_parent, icon_rank_holder, cat_docker,
--     icon_leadership, icon_threat, script_ping_parent) - ZERO stat-row nodes
--     (LOCATED: 0), no panel, no context id, no query. The round-4 marker says
--     the stat components answer to ids that START WITH CcoUnitStat (e.g.
--     CcoUnitStat5974452864 'how fast a unit moves') - a STABLE PREFIX the round-11
--     hint-substring hunt never tested. So round 13 stops guessing the owning
--     subtree and descends EVERY top-level root that has children instead, hunting
--     the CcoUnitStat PREFIX and the structural names together.
--
--     R13 TOTAL STEPS 7 - you are done after step 7.
--
--     THE PLAN (all READ-ONLY; ZERO SetContextObject; simhover DISARMED; the
--     engine's name-lookup helper is BANNED from this file; ONE armed console
--     step at a time, every native call logged BEFORE it is made):
--       STEP 1 - enumerate the UI root's top-level children; keep EVERY root WITH
--                children and order them by the priority list above.
--       STEP 2 - descend the PRIORITY roots to DEPTH 8 (drop into the shared
--                1200-visit budget), logging R13 DOWN path/id/children/stext/vfr
--                for every node, and R13 HIT for every CcoUnitStat-prefixed or
--                structural node.
--       STEP 3 - descend the REMAINING roots with children, continuing the same
--                1200-visit budget.
--       STEP 4 - locate the stat-row nodes and pair each row's stat_name with its
--                value_holder/dy_value (R13 PANEL row=N name=.. value=..).
--       STEP 5 - read GetContextObjectId(CcoUnitDetails / CcoUnitStat /
--                CcoBattleUnit) on the located components (R13 CTXID; reads only).
--       STEP 6 - QUERY 1 of 2: common.get_context_value with the LOCATED context
--                id, field StatList.Size.
--       STEP 7 - QUERY 2 of 2: common.get_context_value with a NON-selected
--                unit's ui id AS TEXT (CcoBattleUnit), field DisplayedValue if
--                query 1 returned a value, else StatList.Size - so EXACTLY TWO
--                get_context_value calls run in total.
--       Only proven-safe primitives: ChildCount, Find, Id, Visible,
--       VisibleFromRoot, CurrentState, GetStateText, GetTooltipText,
--       GetContextObjectId.
-- ============================================================================

-- A GLOBAL table (not a local): the probe chunk already carries ~168 top-level
-- locals and Lua's 200-local ceiling is real - R13 must not spend one.
R13 = {
  run_no          = 0,
  step            = 0,          -- 0 = not started; +1 per armed step
  done            = false,
  total_steps     = 7,          -- R13 TOTAL STEPS 7 - you are done after step 7
  lines           = 0,
  max_lines       = 12000,      -- HARD CAP on R13 log lines (1200 visits + CALL lines)
  line_cap_spoken = false,
  -- hard enumeration budgets
  root_max        = 80,         -- top-level roots logged (step 1)
  child_max       = 80,         -- children scanned per node (steps 1/4)
  descend_visits  = 1200,       -- steps 2-3 TOTAL visits (shared)
  descend_depth   = 8,          -- steps 2-3 max depth FROM a top-level root
  locate_max      = 120,        -- most located (hit) components kept for step 4/5
  ctx_max         = 120,        -- most located components probed in step 5
  unit_id_max     = 40,         -- most numeric unit-id candidates kept
  -- the stable PREFIX every stat component id starts with (case-insensitive)
  stat_prefix     = "ccounitstat",
  -- the structural ids the hunt also matches (SUBSTRING match on a lowercased id)
  locate_names    = { "health_and_stats", "dynamic_stats", "template_stat",
                      "stat_name", "value_holder", "dy_value",
                      "row_header_stats", "stats_toggle" },
  -- the priority order the top-level roots are descended in
  priority        = { "hud_battle", "panel_manager", "under_advisor_docker",
                      "left", "right", "tactical_hud", "menu_bar" },
  -- step-1 output
  roots        = {},            -- { id, uic, children, rank, keep }
  prio_roots   = {},            -- priority-ordered roots WITH children
  rest_roots   = {},            -- the rest of the roots WITH children
  -- collected during the descent: numeric unit-id candidates (the on-field cards)
  unit_ids     = {},            -- { id, path }
  unit_ids_seen = {},           -- id -> true
  -- steps 2-3 output
  located       = {},           -- id -> first { id, uic, path, stext, tip }
  located_order = {},           -- ids in discovery order
  located_list  = {},           -- EVERY located (hit) node
  hit_count     = 0,
  descend_count = 0,
  desc_seen     = {},           -- component -> true (repeat/cycle guard)
  descent_begun = false,
  -- step-4 output
  rows         = {},            -- { n, name, value, rowid, path }
  -- step-5 output
  ctx_types    = { "CcoUnitDetails", "CcoUnitStat", "CcoBattleUnit" },
  ctx          = {},            -- type_id -> context id (non-nil, first kept)
  ctx_from     = {},            -- type_id -> path the id came from
  selected_ui  = nil,           -- the SELECTED unit's numeric ui id (from a path)
  sel_tid      = nil,           -- the type the located context id came from
  sel_id       = nil,           -- the located context id
  -- steps 6-7
  query_sel    = nil,           -- query 1's returned text (drives query 2's field)
  gcv_calls    = 0,
}

-- ---------------------------------------------------------------- R13 logging
function R13.out(msg)
  if R13.lines >= R13.max_lines then
    if not R13.line_cap_spoken then
      R13.line_cap_spoken = true
      log("R13 line cap reached (" .. tostring(R13.max_lines) .. ") - further R13 lines are not logged")
    end
    return
  end
  R13.lines = R13.lines + 1
  log("R13 " .. tostring(msg))
end

-- ALWAYS call this IMMEDIATELY before a native call: it is the line that names
-- the fatal call if the engine dies on the next statement.
function R13.call(desc)
  R13.out("CALL " .. tostring(R13.step) .. " " .. tostring(desc))
end

function R13.read_text(fn)
  local ok, v = pcall(fn)
  if not ok then return "<ERR>" end
  if v == nil then return nil end
  local s = safe_text(v)
  if s ~= nil then return s end
  return "<opaque>"
end

-- ---------------------------------------------------- proven-shape primitives
function R13.ui_root()
  R13.call("core:get_ui_root()")
  local ok, r = pcall(function() return core:get_ui_root() end)
  if not ok or r == nil then return nil end
  return r
end

function R13.child_count(uic)
  if uic == nil then return 0 end
  local n = read1(function() return uic:ChildCount() end)
  if lua_type(n) == "number" then return n end
  return 0
end

-- uic:Find(i) -> a child, or nil. The result is TRUTHINESS-guarded (never wrap a
-- boolean: the round-9 crash).
function R13.child_at(uic, i)
  if uic == nil then return nil end
  local ok, raw = pcall(function() return uic:Find(i) end)
  if not ok or raw == nil or raw == false then return nil end
  return wrap(raw)
end

function R13.id_of(uic)
  if uic == nil then return nil end
  return R13.read_text(function() return uic:Id() end)
end

function R13.vis_of(uic)
  if uic == nil then return nil, nil end
  local vis = readb(function() return uic:Visible() end)
  local vfr = readb(function() return uic:VisibleFromRoot() end)
  return tostring(vis), tostring(vfr)
end

-- an id is a unit ui id when EVERY character is a digit
function R13.is_numeric(s)
  local str = safe_text(s)
  if str == nil or str == "" then return false end
  local len = string.len(str)
  for i = 1, len do
    local c = string.byte(str, i)
    if c == nil or c < 48 or c > 57 then return false end
  end
  return true
end

-- does the lowercased id START WITH CcoUnitStat (the round-4 stable prefix)?
function R13.is_prefix_id(id)
  local str = safe_text(id)
  if str == nil or str == "" then return false end
  local low = string.lower(str)
  local p = R13.stat_prefix
  if string.len(low) < string.len(p) then return false end
  return string.sub(low, 1, string.len(p)) == p
end

-- does the lowercased id CONTAIN one of the structural names?
function R13.is_struct_id(id)
  local str = safe_text(id)
  if str == nil or str == "" then return false end
  local low = string.lower(str)
  for i = 1, #R13.locate_names do
    if contains_str(low, R13.locate_names[i]) then return true end
  end
  return false
end

-- a HIT is either a CcoUnitStat-prefixed id OR a structural name
function R13.is_hit_id(id)
  return R13.is_prefix_id(id) or R13.is_struct_id(id)
end

function R13.is_priority_id(id)
  local str = safe_text(id)
  if str == nil then return false end
  for i = 1, #R13.priority do
    if str == R13.priority[i] then return true end
  end
  return false
end

function R13.rank_of(id)
  local str = safe_text(id)
  if str == nil then return 100 end
  for i = 1, #R13.priority do
    if str == R13.priority[i] then return i end
  end
  return 100
end

function R13.count_ctx()
  local n = 0
  for _ in pairs(R13.ctx) do n = n + 1 end
  return n
end

-- the FIRST all-digit segment of a /-path (plain byte scans; no string.find)
function R13.first_numeric_segment(s)
  local str = safe_text(s)
  if str == nil then return nil end
  local len = string.len(str)
  local start = 1
  local i = 1
  while i <= len + 1 do
    local ch = (i <= len) and string.sub(str, i, i) or "/"
    if ch == "/" then
      if i > start then
        local seg = string.sub(str, start, i - 1)
        if R13.is_numeric(seg) then return seg end
      end
      start = i + 1
    end
    i = i + 1
  end
  return nil
end

function R13.ids_join(list)
  local parts = {}
  for i = 1, #list do
    parts[#parts + 1] = tostring(list[i].id)
  end
  return table.concat(parts, ",")
end

-- record a numeric unit-id candidate (the on-field cards), de-duped by id
function R13.note_unit_id(id, path)
  local str = safe_text(id)
  if str == nil or str == "" then return end
  if R13.unit_ids_seen[str] ~= nil then return end
  if #R13.unit_ids >= R13.unit_id_max then return end
  R13.unit_ids_seen[str] = true
  R13.unit_ids[#R13.unit_ids + 1] = { id = str, path = path }
end

-- ---------------------------------------------------------------- the descent
-- Descend one root subtree to R13.descend_depth, charging the SHARED budget.
-- Paths are RELATIVE to the top-level root (root = depth 1).
function R13.descend(uic, path, depth)
  if uic == nil then return end
  if R13.descend_count >= R13.descend_visits then return end
  if depth > R13.descend_depth then return end
  -- repeat / cycle guard keyed on the COMPONENT (paths collide when sibling ids
  -- repeat - e.g. every stat row is id "template_stat")
  if R13.desc_seen[uic] ~= nil then return end
  R13.desc_seen[uic] = true
  R13.descend_count = R13.descend_count + 1
  local id = R13.id_of(uic)
  R13.call("DOWN " .. q(path) .. ":ChildCount()")
  local cn = R13.child_count(uic)
  R13.call("DOWN " .. q(path) .. ":GetStateText/CurrentState/Visible/VisibleFromRoot")
  local st = R13.read_text(function() return uic:GetStateText() end)
  local cs = R13.read_text(function() return uic:CurrentState() end)
  local vis, vfr = R13.vis_of(uic)
  R13.out("DOWN path=" .. q(path) .. " id=" .. q(id) .. " children=" .. tostring(cn)
    .. " stext=" .. q(st) .. " vfr=" .. tostring(vfr) .. " vis=" .. tostring(vis)
    .. " state=" .. q(cs))
  -- a numeric id is a unit card's ui id (kept as a NON-selected query candidate)
  if id ~= nil and R13.is_numeric(id) then R13.note_unit_id(id, path) end
  -- a HIT: CcoUnitStat prefix OR a structural name
  if id ~= nil and R13.is_hit_id(id) then
    R13.call("HIT " .. q(path) .. ":GetTooltipText()")
    local tip = R13.read_text(function() return uic:GetTooltipText() end)
    R13.hit_count = R13.hit_count + 1
    R13.out("HIT path=" .. q(path) .. " id=" .. q(id) .. " stext=" .. q(st) .. " tip=" .. q(tip))
    if #R13.located_list < R13.locate_max then
      local rec = { id = id, uic = uic, path = path, stext = st, tip = tip }
      R13.located_list[#R13.located_list + 1] = rec
      if R13.located[id] == nil then
        R13.located[id] = rec
        R13.located_order[#R13.located_order + 1] = id
      end
    end
  end
  if depth >= R13.descend_depth then return end
  for i = 0, cn - 1 do
    if R13.descend_count >= R13.descend_visits then return end
    R13.call("DOWN " .. q(path) .. ":Find(" .. tostring(i) .. ")")
    local ch = R13.child_at(uic, i)
    if ch ~= nil then
      local cid = R13.id_of(ch)
      if cid == nil or cid == "" then cid = "#" .. tostring(i) end
      R13.descend(ch, path .. "/" .. cid, depth + 1)
    end
  end
end

-- ---------------------------------------------------------------- the steps
R13.steps = {}

-- STEP 1 - enumerate the UI root's top-level children; keep EVERY root WITH
-- children, ordered by the priority list.
R13.steps[1] = function()
  R13.out("STEP 1 - enumerate the UI root's top-level children; keep every root WITH"
    .. " children, priority-ordered (budget " .. tostring(R13.root_max) .. ")")
  local root = R13.ui_root()
  if root == nil then
    R13.out("STEP 1 aborted: core:get_ui_root() returned nil")
    return
  end
  local n = R13.child_count(root)
  R13.out("ROOTCOUNT " .. tostring(n))
  if n <= 0 then
    R13.out("STEP 1: the UI root has no children yet (battle not up?)")
    return
  end
  R13.roots = {}
  R13.unit_ids = {}
  R13.unit_ids_seen = {}
  local lim = n
  if lim > R13.root_max then lim = R13.root_max end
  for i = 0, lim - 1 do
    R13.call("ui_root:Find(" .. tostring(i) .. ") + Id/ChildCount/Visible/VisibleFromRoot")
    local uic = R13.child_at(root, i)
    local id = R13.id_of(uic)
    local vis, vfr = R13.vis_of(uic)
    local cn = R13.child_count(uic)
    local rank = R13.rank_of(id)
    local keep = (cn > 0 and uic ~= nil)
    R13.out("ROOT " .. tostring(i) .. " id=" .. q(id) .. " vis=" .. tostring(vis)
      .. " vfr=" .. tostring(vfr) .. " children=" .. tostring(cn)
      .. " rank=" .. tostring(rank) .. " keep=" .. tostring(keep))
    R13.roots[#R13.roots + 1] = { uic = uic, id = id, children = cn, rank = rank, keep = keep }
  end
  if n > lim then
    R13.out("ROOT ... (" .. tostring(n - lim) .. " more root(s) not listed; cap "
      .. tostring(R13.root_max) .. ")")
  end
  -- the DESCEND PLAN: priority roots first (in the listed order), then the rest
  R13.prio_roots = {}
  for k = 1, #R13.priority do
    for j = 1, #R13.roots do
      local r = R13.roots[j]
      if r.keep and safe_text(r.id) == R13.priority[k] then
        R13.prio_roots[#R13.prio_roots + 1] = r
        break
      end
    end
  end
  R13.rest_roots = {}
  for j = 1, #R13.roots do
    local r = R13.roots[j]
    if r.keep and not R13.is_priority_id(r.id) then
      R13.rest_roots[#R13.rest_roots + 1] = r
    end
  end
  -- keep a NON-selected unit-id candidate even if the budget never reaches
  -- unit_id_holder: scan that root's DIRECT children for numeric ids (reads only)
  for j = 1, #R13.roots do
    local r = R13.roots[j]
    if r.uic ~= nil and r.id ~= nil and contains_str(string.lower(tostring(r.id)), "unit_id_holder") then
      local cn = R13.child_count(r.uic)
      local clim = cn
      if clim > R13.child_max then clim = R13.child_max end
      for c = 0, clim - 1 do
        R13.call("unit_id_holder:Find(" .. tostring(c) .. ") + Id")
        local ch = R13.child_at(r.uic, c)
        local cid = R13.id_of(ch)
        if cid ~= nil and R13.is_numeric(cid) then R13.note_unit_id(cid, "unit_id_holder/" .. tostring(cid)) end
      end
      break
    end
  end
  R13.out("DESCEND PLAN prio=" .. tostring(#R13.prio_roots) .. " : " .. R13.ids_join(R13.prio_roots))
  R13.out("DESCEND PLAN rest=" .. tostring(#R13.rest_roots) .. " : " .. R13.ids_join(R13.rest_roots))
  R13.out("STEP 1 done: roots=" .. tostring(#R13.roots) .. " with_children="
    .. tostring(#R13.prio_roots + #R13.rest_roots) .. " unit_id_candidates="
    .. tostring(#R13.unit_ids))
end

-- STEP 2 - descend the PRIORITY roots (the shared budget begins here).
R13.steps[2] = function()
  R13.out("STEP 2 - descend the PRIORITY roots (" .. tostring(#R13.prio_roots)
    .. ") to depth " .. tostring(R13.descend_depth) .. ", budget "
    .. tostring(R13.descend_visits) .. " visits (shared with step 3)")
  R13.located = {}
  R13.located_order = {}
  R13.located_list = {}
  R13.hit_count = 0
  R13.descend_count = 0
  R13.desc_seen = {}
  if #R13.prio_roots == 0 then
    R13.out("STEP 2: no PRIORITY root has any children - step 3 covers the rest")
  end
  for k = 1, #R13.prio_roots do
    local r = R13.prio_roots[k]
    if R13.descend_count >= R13.descend_visits then
      R13.out("STEP 2: budget exhausted before root " .. q(r.id))
      break
    end
    R13.out("STEP 2 root " .. tostring(k) .. " id=" .. q(r.id)
      .. " children=" .. tostring(r.children) .. " (visits so far "
      .. tostring(R13.descend_count) .. ")")
    R13.descend(r.uic, tostring(r.id), 1)
  end
  R13.descent_begun = true
  R13.out("STEP 2 done: visits=" .. tostring(R13.descend_count) .. "/"
    .. tostring(R13.descend_visits) .. " hits=" .. tostring(R13.hit_count)
    .. " located=" .. tostring(#R13.located_order))
end

-- STEP 3 - descend the REMAINING roots with children (same shared budget).
R13.steps[3] = function()
  R13.out("STEP 3 - descend the REMAINING roots with children (" .. tostring(#R13.rest_roots)
    .. "), continuing the " .. tostring(R13.descend_visits)
    .. "-visit budget (used so far " .. tostring(R13.descend_count) .. ")")
  if not R13.descent_begun then
    R13.located = {}
    R13.located_order = {}
    R13.located_list = {}
    R13.hit_count = 0
    R13.descend_count = 0
    R13.desc_seen = {}
  end
  if #R13.rest_roots == 0 then
    R13.out("STEP 3: no further root with children was listed by step 1")
  end
  for k = 1, #R13.rest_roots do
    local r = R13.rest_roots[k]
    if R13.descend_count >= R13.descend_visits then
      R13.out("STEP 3: budget exhausted before root " .. q(r.id))
      break
    end
    R13.out("STEP 3 root " .. tostring(k) .. " id=" .. q(r.id)
      .. " children=" .. tostring(r.children) .. " (visits so far "
      .. tostring(R13.descend_count) .. ")")
    R13.descend(r.uic, tostring(r.id), 1)
  end
  R13.out("STEP 3 done: visits=" .. tostring(R13.descend_count) .. "/"
    .. tostring(R13.descend_visits) .. " hits=" .. tostring(R13.hit_count)
    .. " located=" .. tostring(#R13.located_order))
end

-- STEP 4 - log every located (hit) component and pair each stat ROW's stat_name
-- with its value_holder/dy_value. A row is a template_stat OR a CcoUnitStat* node.
R13.steps[4] = function()
  R13.out("STEP 4 - locate the stat rows and pair each row's name with its value")
  R13.rows = {}
  if R13.located_order == nil or #R13.located_order == 0 then
    R13.out("STEP 4: the descent located NO HIT (no CcoUnitStat prefix and no"
      .. " structural id). Grep the DOWN lines - the panel may sit deeper than depth "
      .. tostring(R13.descend_depth) .. " or under a root step 1 skipped")
  end
  for k = 1, #(R13.located_order or {}) do
    local id = R13.located_order[k]
    local rec = R13.located[id]
    if rec ~= nil then
      R13.out("LOCATED path=" .. q(rec.path) .. " id=" .. q(id)
        .. " children=" .. tostring(R13.child_count(rec.uic)))
    end
  end
  -- find a child of `uic` whose Id() == want (bounded by child_max)
  local function child_named(uic, want)
    if uic == nil then return nil end
    local cn = R13.child_count(uic)
    local lim = cn
    if lim > R13.child_max then lim = R13.child_max end
    for i = 0, lim - 1 do
      R13.call("child " .. q(want) .. " under " .. q(R13.id_of(uic)) .. ":Find(" .. tostring(i) .. ")")
      local ch = R13.child_at(uic, i)
      if ch ~= nil and R13.id_of(ch) == want then return ch end
    end
    return nil
  end
  local function read_row(row_uic, n, row_path, row_id)
    local sn = child_named(row_uic, "stat_name")
    local vh = child_named(row_uic, "value_holder")
    local dv = nil
    if vh ~= nil then dv = child_named(vh, "dy_value") end
    if dv == nil then dv = child_named(row_uic, "dy_value") end
    local name_text, val_text = nil, nil
    if sn ~= nil then
      R13.call("stat_name:GetStateText()")
      name_text = R13.read_text(function() return sn:GetStateText() end)
    end
    if dv ~= nil then
      R13.call("dy_value:GetStateText()")
      val_text = R13.read_text(function() return dv:GetStateText() end)
    end
    R13.out("PANEL row=" .. tostring(n) .. " name=" .. q(name_text) .. " value=" .. q(val_text)
      .. " path=" .. q(row_path) .. " rowid=" .. q(row_id))
    if R13.is_prefix_id(row_id) then
      R13.out("ROWCTX " .. q(row_path) .. " prefix=CcoUnitStat id=" .. q(row_id))
    end
    R13.rows[#R13.rows + 1] = { n = n, name = name_text, value = val_text,
                                rowid = row_id, uic = row_uic, path = row_path }
  end
  -- every located template_stat OR CcoUnitStat* node is one stat row
  local n = 0
  for k = 1, #(R13.located_list or {}) do
    local rec = R13.located_list[k]
    if rec.id == "template_stat" or R13.is_prefix_id(rec.id) then
      n = n + 1
      read_row(rec.uic, n, rec.path, rec.id)
    end
  end
  -- fallback: a located dynamic_stats whose template_stat children were not
  -- themselves located (defensive; the descent normally visits them)
  if n == 0 then
    local ds = R13.located["dynamic_stats"]
    if ds ~= nil then
      local cn = R13.child_count(ds.uic)
      local lim = cn
      if lim > R13.child_max then lim = R13.child_max end
      for i = 0, lim - 1 do
        R13.call("dynamic_stats:Find(" .. tostring(i) .. ") looking for template_stat")
        local ch = R13.child_at(ds.uic, i)
        if ch ~= nil and (R13.id_of(ch) == "template_stat" or R13.is_prefix_id(R13.id_of(ch))) then
          n = n + 1
          read_row(ch, n, ds.path .. "/" .. tostring(R13.id_of(ch)), R13.id_of(ch))
        end
      end
    end
  end
  -- fallback: a lone located stat_name (+ a located dy_value, if any)
  if n == 0 and R13.located["stat_name"] ~= nil then
    R13.call("stat_name:GetStateText()")
    local t = R13.read_text(function() return R13.located["stat_name"].uic:GetStateText() end)
    local v = nil
    local dv = R13.located["dy_value"]
    if dv ~= nil then
      R13.call("dy_value:GetStateText()")
      v = R13.read_text(function() return dv.uic:GetStateText() end)
    end
    n = n + 1
    R13.out("PANEL row=" .. tostring(n) .. " name=" .. q(t) .. " value=" .. q(v)
      .. " path=" .. q(R13.located["stat_name"].path) .. " rowid=" .. q("stat_name"))
    R13.rows[#R13.rows + 1] = { n = n, name = t, value = v, rowid = "stat_name" }
  end
  R13.out("STEP 4 done: hits=" .. tostring(R13.hit_count) .. " rows=" .. tostring(#R13.rows)
    .. " located=" .. tostring(#(R13.located_order or {})))
end

-- STEP 5 - read GetContextObjectId (CcoUnitDetails / CcoUnitStat / CcoBattleUnit)
-- on the located components (READS only).
R13.steps[5] = function()
  R13.out("STEP 5 - read GetContextObjectId on the located components (reads only)")
  R13.ctx = {}
  R13.ctx_from = {}
  R13.selected_ui = nil
  R13.sel_tid = nil
  R13.sel_id = nil
  if R13.located_list == nil or #R13.located_list == 0 then
    R13.out("STEP 5: nothing was located - no context id to read")
    return
  end
  local probed = 0
  for k = 1, #R13.located_list do
    if probed >= R13.ctx_max then break end
    local rec = R13.located_list[k]
    probed = probed + 1
    for t = 1, #R13.ctx_types do
      local tid = R13.ctx_types[t]
      R13.call(q(rec.path) .. " GetContextObjectId(" .. tid .. ")")
      local ok, raw = pcall(function() return rec.uic:GetContextObjectId(tid) end)
      local text = nil
      if ok then text = safe_text(raw) end
      R13.out("CTXID " .. q(rec.path) .. " " .. tid .. " -> " .. (ok and q(text) or "<ERR>"))
      if ok and text ~= nil and text ~= "" and R13.ctx[tid] == nil then
        R13.ctx[tid] = text
        R13.ctx_from[tid] = rec.path
      end
    end
  end
  -- the located context id = the first non-nil one (a read off a hit component)
  for i = 1, #R13.ctx_types do
    local tid = R13.ctx_types[i]
    if R13.ctx[tid] ~= nil then R13.sel_tid = tid; R13.sel_id = R13.ctx[tid]; break end
  end
  if R13.sel_tid == nil then
    R13.out("STEP 5: NO context id came back (all nil) - the query steps make no call")
    return
  end
  -- the SELECTED unit's ui id = the FIRST numeric segment of the path the located
  -- context id came from (recorded data only - no new read)
  local from = R13.ctx_from[R13.sel_tid]
  if from ~= nil then R13.selected_ui = R13.first_numeric_segment(from) end
  R13.out("STEP 5 done: ctx_ids=" .. tostring(R13.count_ctx()) .. " selected_type="
    .. tostring(R13.sel_tid) .. " selected_id=" .. q(R13.sel_id)
    .. " selected_ui=" .. q(R13.selected_ui))
end

-- STEP 6 - QUERY 1 of 2: the LOCATED context id, field StatList.Size.
R13.steps[6] = function()
  R13.out("STEP 6 - QUERY 1 of 2: the LOCATED context id (vanilla shape, field StatList.Size)")
  R13.gcv_calls = 0
  R13.query_sel = nil
  if R13.sel_tid == nil or R13.sel_id == nil then
    R13.out("STEP 6: no context id came out of step 5 - query 1 is skipped (0 calls so far)")
    return
  end
  local field = "StatList.Size"
  R13.call("common.get_context_value(" .. R13.sel_tid .. ", " .. q(R13.sel_id) .. ", " .. q(field) .. ")")
  local ok1, v1 = pcall(function() return common.get_context_value(R13.sel_tid, R13.sel_id, field) end)
  R13.gcv_calls = R13.gcv_calls + 1
  local t1 = ok1 and text_of(v1, true) or "<ERR>"
  if t1 == nil then t1 = "<nil>" end
  if ok1 and v1 ~= nil then R13.query_sel = t1 end
  R13.out("QUERY sel=" .. q(R13.sel_id) .. " type=" .. R13.sel_tid .. " field=" .. field
    .. " -> " .. q(t1) .. " (from " .. tostring(R13.ctx_from[R13.sel_tid]) .. ")")
  R13.out("STEP 6 done: get_context_value calls=" .. tostring(R13.gcv_calls) .. " (want 2 total)")
end

-- STEP 7 - QUERY 2 of 2: a NON-selected unit's ui id AS TEXT (CcoBattleUnit),
-- field DisplayedValue if query 1 returned a value, else StatList.Size.
R13.steps[7] = function()
  R13.out("STEP 7 - QUERY 2 of 2: a NON-selected unit's ui id as text (field"
    .. " DisplayedValue if query 1 returned, else StatList.Size)")
  if R13.sel_id == nil then
    R13.out("STEP 7: no context id came out of step 5 - query 2 is skipped,"
      .. " get_context_value calls=" .. tostring(R13.gcv_calls) .. " (want 2)")
    return
  end
  local nonsel = nil
  for i = 1, #(R13.unit_ids or {}) do
    local u = R13.unit_ids[i]
    if u.id ~= nil and tostring(u.id) ~= tostring(R13.selected_ui) then
      nonsel = tostring(u.id)
      break
    end
  end
  if nonsel == nil then
    R13.out("QUERY nonsel: no NON-selected unit ui id was collected (keep the"
      .. " cards panel up with >=2 units) - query 2 skipped, calls="
      .. tostring(R13.gcv_calls) .. " (want 2)")
    return
  end
  local returned = (R13.query_sel ~= nil and R13.query_sel ~= "<nil>" and R13.query_sel ~= "<ERR>")
  local field = returned and "DisplayedValue" or "StatList.Size"
  R13.out("QUERY nonsel unit ui id=" .. q(nonsel) .. " (selected_ui=" .. q(R13.selected_ui)
    .. ") field=" .. field)
  R13.call("common.get_context_value(\"CcoBattleUnit\", " .. q(nonsel) .. ", " .. q(field) .. ")")
  local ok2, v2 = pcall(function() return common.get_context_value("CcoBattleUnit", nonsel, field) end)
  R13.gcv_calls = R13.gcv_calls + 1
  local t2 = ok2 and text_of(v2, true) or "<ERR>"
  if t2 == nil then t2 = "<nil>" end
  R13.out("QUERY nonsel=" .. q(nonsel) .. " type=CcoBattleUnit field=" .. field .. " -> " .. q(t2))
  R13.out("STEP 7 done: get_context_value calls=" .. tostring(R13.gcv_calls) .. " (want 2)")
end

-- ---------------------------------------------------------------- the driver
function R13.advance()
  if R13.done then
    R13.out("step ignored: the run is done (" .. tostring(R13.total_steps)
      .. " steps) - zz_probe_r13() restarts it")
    return R13.step
  end
  R13.step = R13.step + 1
  local fn = R13.steps[R13.step]
  if fn == nil then
    R13.done = true
    R13.out("===== ROUND 13 RUN done after " .. tostring(R13.total_steps)
      .. " steps (reads only; zero writes) - R13 TOTAL STEPS 7 - YOU ARE DONE =====")
    return R13.step
  end
  R13.out("")
  R13.out("===== R13 STEP " .. tostring(R13.step) .. "/" .. tostring(R13.total_steps)
    .. " (t=" .. tostring(tick_count) .. ") =====")
  local ok, err = pcall(fn)
  if not ok then
    R13.out("STEP " .. tostring(R13.step) .. " raised (swallowed): " .. truncate(err, 160))
  end
  return R13.step
end

function zz_probe_r13()
  R13.step = 0
  R13.done = false
  R13.roots = {}
  R13.prio_roots = {}
  R13.rest_roots = {}
  R13.unit_ids = {}
  R13.unit_ids_seen = {}
  R13.located = {}
  R13.located_order = {}
  R13.located_list = {}
  R13.hit_count = 0
  R13.descend_count = 0
  R13.desc_seen = {}
  R13.descent_begun = false
  R13.rows = {}
  R13.ctx = {}
  R13.ctx_from = {}
  R13.selected_ui = nil
  R13.sel_tid = nil
  R13.sel_id = nil
  R13.query_sel = nil
  R13.gcv_calls = 0
  return PROBE_TAG .. "R13 READY (step 0 of 7). R13 TOTAL STEPS 7 - you are done after step 7."
    .. " In battle, open AND PIN the unit-info panel and keep the cards panel up with >=2 units,"
    .. " then call zz_probe_r13_step() ONE step at a time (after each step, if the game is alive,"
    .. " type the next). Step 7 is the LAST step - stop there. log=" .. LOG_FILE
end

function zz_probe_r13_step()
  if R13.step == 0 and (not R13.done) then
    R13.run_no = R13.run_no + 1
    R13.lines = 0
    R13.line_cap_spoken = false
    R13.out("")
    R13.out("===== ROUND 13 RUN #" .. tostring(R13.run_no)
      .. " (manual zz_probe_r13_step) t=" .. tostring(tick_count) .. " =====")
    R13.out("R13 TOTAL STEPS 7 - you are done after step 7. Descend EVERY top-level root"
      .. " that has children (priority: hud_battle, panel_manager, under_advisor_docker,"
      .. " left, right, tactical_hud, menu_bar, then the rest) to DEPTH "
      .. tostring(R13.descend_depth) .. " with a " .. tostring(R13.descend_visits)
      .. "-visit budget; match the CcoUnitStat* PREFIX (case-insensitive) AND the structural"
      .. " names; pair the stat rows; read the CcoUnitDetails / CcoUnitStat / CcoBattleUnit"
      .. " context ids; then run EXACTLY TWO common.get_context_value calls (the located id,"
      .. " then a NON-selected unit's ui id as text). Every native call is logged BEFORE it is"
      .. " made; ZERO SetContextObject; simhover DISARMED; the name-lookup helper is BANNED.")
  end
  local before = R13.step
  R13.advance()
  local nxt
  if R13.done or R13.step >= R13.total_steps or R13.steps[R13.step + 1] == nil then
    nxt = "DONE - STOP (zz_probe_r13 finished after " .. tostring(R13.total_steps) .. " steps)"
  else
    nxt = "step " .. tostring(R13.step + 1) .. " of " .. tostring(R13.total_steps)
  end
  return PROBE_TAG .. "R13 step " .. tostring(R13.step) .. "/" .. tostring(R13.total_steps)
    .. " done (was " .. tostring(before) .. "); next: " .. nxt
    .. " - call zz_probe_r13_step() again. log=" .. LOG_FILE
end

function zz_probe_r13_auto()
  if R13.step == 0 and (not R13.done) then zz_probe_r13() end
  R13.run_no = R13.run_no + 1
  R13.lines = 0
  R13.line_cap_spoken = false
  R13.out("")
  R13.out("===== ROUND 13 AUTO RUN #" .. tostring(R13.run_no) .. " t=" .. tostring(tick_count)
    .. " - runs every step to the cap; a fatal call dies here and the last R13 CALL names it =====")
  local guard = 0
  while (not R13.done) and guard < 40 do
    guard = guard + 1
    R13.advance()
  end
  return PROBE_TAG .. "R13 auto finished (step=" .. tostring(R13.step)
    .. (R13.done and ", done" or ", cap") .. "). log=" .. LOG_FILE
end

function zz_probe_r13_status()
  return PROBE_TAG .. "R13 TOTAL STEPS " .. tostring(R13.total_steps) .. " - run="
    .. tostring(R13.run_no) .. " step=" .. tostring(R13.step) .. "/" .. tostring(R13.total_steps)
    .. " done=" .. tostring(R13.done) .. " lines=" .. tostring(R13.lines)
    .. "/" .. tostring(R13.max_lines)
    .. " | roots=" .. tostring(#(R13.roots or {}))
    .. " prio=" .. tostring(#(R13.prio_roots or {}))
    .. " rest=" .. tostring(#(R13.rest_roots or {}))
    .. " unit_ids=" .. tostring(#(R13.unit_ids or {}))
    .. " descend_visits=" .. tostring(R13.descend_count) .. "/" .. tostring(R13.descend_visits)
    .. " hits=" .. tostring(R13.hit_count)
    .. " located=" .. tostring(#(R13.located_order or {}))
    .. " rows=" .. tostring(#(R13.rows or {}))
    .. " ctx_ids=" .. tostring(R13.count_ctx())
    .. " gcv_calls=" .. tostring(R13.gcv_calls)
    .. " | zz_probe_r13() to start/restart; log=" .. LOG_FILE
end

function zz_probe_r13_help()
  return PROBE_TAG .. "R13 DESCEND EVERY ROOT. R13 TOTAL STEPS 7 - you are done after step 7."
    .. " Start a battle, open AND PIN the unit-info panel, and keep the cards panel up with"
    .. " >=2 units. Call zz_probe_r13() once, then zz_probe_r13_step() SEVEN times ("
    .. tostring(R13.total_steps) .. " total; STOP after step " .. tostring(R13.total_steps) .. ")."
    .. " Step 1 enumerates every top-level root and keeps the ones WITH children, priority-ordered"
    .. " (hud_battle, panel_manager, under_advisor_docker, left, right, tactical_hud, menu_bar,"
    .. " then the rest); step 2 descends the priority roots to depth " .. tostring(R13.descend_depth)
    .. " (budget " .. tostring(R13.descend_visits) .. " visits), logging R13 DOWN"
    .. " path/id/children/stext/vfr for every node and R13 HIT for every CcoUnitStat*-prefixed or"
    .. " structural node; step 3 descends the remaining roots with children; step 4 pairs the rows"
    .. " (R13 PANEL row=N name=.. value=..); step 5 reads GetContextObjectId"
    .. " (CcoUnitDetails/CcoUnitStat/CcoBattleUnit) on the located components (R13 CTXID); steps"
    .. " 6-7 run EXACTLY TWO common.get_context_value calls - query 1 with the LOCATED context id"
    .. " (field StatList.Size), query 2 with a NON-selected unit's ui id as text (CcoBattleUnit,"
    .. " field DisplayedValue if query 1 returned, else StatList.Size) (R13 QUERY sel=/nonsel=)."
    .. " zz_probe_r13_auto() runs every step to the cap. ZERO writes; simhover DISARMED; the"
    .. " name-lookup helper is BANNED. Log: " .. LOG_FILE
end
