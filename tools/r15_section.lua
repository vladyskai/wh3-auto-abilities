-- ============================================================================
-- 17c. ROUND 15 - THE FINAL EXPERIMENT (user-designed): THE INVISIBLE-HOVER
--      COMPARISON PROBE.
--
--      THE QUESTION. The user has SEEN the panel render stat DIFFERENCES while
--      hovering ANOTHER unit's card with one unit selected. Round 14 proved the
--      panel's stat contexts are NOT addressable by unit id, so the remaining
--      route to a non-selected unit's numbers is the panel's OWN comparison data
--      DURING a hover. This round tests, mechanically, what the panel's
--      comparison fields hold while a hover is active - and whether a hover
--      SHORT ENOUGH TO STAY INVISIBLE (below the 0.25 s tooltip draw delay)
--      still moves any of them.
--
--      THE PLAN (all READ-ONLY from the script side; every SimulateMouseOn is
--      paired with its SimulateMouseOff; ZERO context writes; the engine's
--      name-lookup helper is BANNED from this file; ONE armed console step per
--      invocation, 7 steps total - A, pass1, pass2, pass3, control, verdict,
--      done):
--        STEP 1 (A)  - BASELINE (no hover): resolve the DISCOVERED panel path
--                      (hud_battle/info_panel_parent/info_panel_background/
--                       unit_information/info_parent/info_panel/list), walk DOWN
--                      from `list`, pair every stat row (stat_name -> value),
--                      then DUMP every row's children (and one level deeper):
--                      id/stext/tip/vis/state - hunting label_compare and every
--                      'comparison'/'compare' named component and its text. For
--                      the row AND its children: GetContextObjectId("CcoUnitStat")
--                      and ("CcoUnitDetails") - every NON-nil id is logged
--                      (read-only). Records the BASELINE VALUES the passes watch
--                      and picks ONE non-selected visible card as the hover target.
--        STEP 2      - PASS 1: SimulateMouseOn over the target card, hold 100 ms,
--                      SimulateMouseOff; poll every 25 ms.
--        STEP 3      - PASS 2: same, hold 150 ms.
--        STEP 4      - PASS 3: same, hold 250 ms.
--                      (100/150/250 ms are ALL below the 250 ms tooltip appear
--                      delay from the shipped layouts -> INVISIBLE by design.)
--        STEP 5      - CONTROL pass: hold 1500 ms. This one WILL draw the
--                      tooltip (expected). It proves the comparison data is
--                      reachable AT ALL and is the pass the user WATCHES.
--        STEP 6      - VERDICT: per-pass changed counts + whether any INVISIBLE
--                      pass exposed a non-selected unit's stat value
--                      (R15 *** WIN: hover exposes non-selected stats INVISIBLY ***
--                      / R15 no invisible exposure; control_changed=<n>). If a
--                      delta appeared, the R15 DELTA lines carry the selected
--                      value and the delta so the hover = selected - delta check
--                      can be made.
--        STEP 7      - DONE: pair totals + the STOP instruction.
--
--      DURING EVERY PASS the probe samples, every poll (requested 25 ms), the
--      three read classes: (i) every stat row's label_compare stext,
--      (ii) every comparison-named component's stext (+ its Visible, tracked as
--      a separate 'vis:' field - extra signal, never counted as a VALUE
--      exposure), (iii) the row's GetContextObjectId("CcoUnitStat") value. ANY
--      change vs the (per-pass refreshed) baseline logs ONE line:
--        R15 HOVER pass=<n> hold=<ms> t=<ms> row=<n> field=<..> was=".." now=".."
--      A change whose NEW value is a signed number on a label/compare field also
--      logs the delta arithmetic line (R15 DELTA ...).
--
--      Both SimulateMouseOn and SimulateMouseOff are logged IMMEDIATELY BEFORE
--      the call (a crash names its last simulated mouse op). The sampling reads
--      are NOT CALL-logged (they run 40x a second; every one is pcall-walled and
--      a raising read is counted as a warning and IGNORED, so a dead handle can
--      never fake a WIN). Only proven-safe primitives are used: ChildCount, Find,
--      Id, Visible, VisibleFromRoot, CurrentState, GetStateText, GetTooltipText,
--      GetContextObjectId, SimulateMouseOn, SimulateMouseOff.
-- ============================================================================

-- A GLOBAL table (not a local): the probe chunk is close to Lua's 200-local
-- ceiling - R15 must not spend one.
R15 = {
  run_no              = 0,
  step                = 0,          -- 0 = not started; +1 per armed step
  done                = false,
  total_steps         = 7,          -- R15 TOTAL STEPS 7 - you are done after step 7
  lines               = 0,
  max_lines           = 20000,      -- HARD CAP on R15 log lines
  line_cap_spoken     = false,
  -- cadence / timing
  poll_ms             = 25,         -- requested poll interval during a pass
  settle_ms           = 300,        -- sampling continues this long after Off
  visible_ms          = 250,        -- tooltip appear delay (shipped layouts) ->
                                    --   holds <= 250 ms are INVISIBLE by design
  poll_name           = "zz_probe_r15_poll",
  -- hard budgets
  child_max           = 40,         -- children scanned per node
  walk_visits         = 300,        -- walk DOWN from `list`: TOTAL visits
  walk_depth          = 6,          -- walk DOWN from `list`: max depth
  row_max             = 60,         -- most stat rows paired
  dump_max            = 700,        -- most components dumped in step A
  ctx_cap             = 500,        -- most GetContextObjectId calls in step A
  tracked_max         = 400,        -- most tracked fields (change detection)
  max_sims            = 8,          -- SimulateMouseOn cap per run (4 passes + slack)
  -- the four passes; the last one is the CONTROL (tooltip will draw - expected)
  holds               = { 100, 150, 250, 1500 },
  -- the DISCOVERED panel path (root-first; each link is a direct child of the one before)
  chain               = { "hud_battle", "info_panel_parent", "info_panel_background",
                          "unit_information", "info_parent", "info_panel", "list" },
  -- resolved handles / walk state
  nodes               = {},         -- level -> { id, uic, how, children, path }
  list_uic            = nil,
  list_path           = nil,
  chain_ok            = false,
  walked              = {},         -- { id, uic, path, stext, tip, depth }
  walk_count          = 0,
  walk_seen           = {},
  walk_cap_spoken     = false,
  -- rows / tracked fields
  rows                = {},         -- n -> { n, name, value, rowid, uic }
  tracked             = {},         -- i -> { row, field, kind, uic, base, last, deviated }
  seen_comp           = {},         -- component -> true (tracked once)
  compar_n            = 0,          -- comparison-named components found
  label_compare_seen  = false,      -- the FIRST label_compare gets field "label_compare"
  tracked_cap_spoken  = false,
  dump_nodes          = 0,
  dump_cap_spoken     = false,
  ctx_calls           = 0,
  ctx_cap_spoken      = false,
  -- the hover target (ONE non-selected visible card)
  target              = nil,        -- { id, uic, ctx, state }
  selected_card       = nil,
  -- baseline / pass state
  baseline_ok         = false,
  pass                = nil,        -- the pass in flight (or the last one, inactive)
  results             = {},         -- pass n -> { hold, events, fields_dev, ... }
  sim_on_total        = 0,
  sim_off_total       = 0,
  pairs_spoken        = false,
  -- verdict bookkeeping
  deltas              = 0,
  events_total        = 0,
  warn_total          = 0,
  first_evidence      = nil,        -- { pass, row, field, was, now } (any value-bearing deviation)
  first_text          = nil,        -- the FIRST text-kind deviation (the WIN line prefers it)
  vis_only_note       = false,
  win                 = false,
}

-- ---------------------------------------------------------------- R15 logging
function R15.out(msg)
  if R15.lines >= R15.max_lines then
    if not R15.line_cap_spoken then
      R15.line_cap_spoken = true
      log("R15 line cap reached (" .. tostring(R15.max_lines) .. ") - further R15 lines are not logged")
    end
    return
  end
  R15.lines = R15.lines + 1
  log("R15 " .. tostring(msg))
end

-- ALWAYS call this IMMEDIATELY before a native call: it names the fatal call if
-- the engine dies on the next statement. (The 25 ms pass sampler does NOT emit
-- CALL lines - that would flood the log; its reads are pcall-walled and a
-- failure is a counted warning, never a change.)
function R15.call(desc)
  R15.out("CALL " .. tostring(R15.step) .. " " .. tostring(desc))
end

-- Log the walk visit-cap ONCE (both the top-of-walk and the in-loop cut paths
-- call this).
function R15.walk_cap()
  if not R15.walk_cap_spoken then
    R15.walk_cap_spoken = true
    R15.out("WALK visit budget reached (" .. tostring(R15.walk_visits) .. ") - subtree truncated here")
  end
end

-- ---------------------------------------------------- proven-shape primitives
-- (pure readers borrowed from R14: no logging inside them)
function R15.child_count(uic) return R14.child_count(uic) end
function R15.child_at(uic, i) return R14.child_at(uic, i) end
function R15.id_of(uic) return R14.id_of(uic) end
function R15.read_text(fn) return R14.read_text(fn) end

-- the DIRECT child of `uic` whose Id() == want (bounded by child_max; every Find
-- is logged BEFORE it is made). Returns the child, or nil.
function R15.find_child_named(uic, want)
  if uic == nil then return nil end
  local cn = R15.child_count(uic)
  local lim = cn
  if lim > R15.child_max then lim = R15.child_max end
  for i = 0, lim - 1 do
    R15.call(q(R15.id_of(uic) or "?") .. ":Find(" .. tostring(i) .. ") looking for " .. q(want))
    local ch = R15.child_at(uic, i)
    if ch ~= nil and R15.id_of(ch) == want then return ch end
  end
  return nil
end

-- ---------------------------------------------------------------- the chain
-- Resolve the DISCOVERED panel path link by link (same shape as round 14).
function R15.resolve_chain()
  R15.nodes = {}
  R15.list_uic = nil
  R15.list_path = nil
  R15.chain_ok = false
  local root = nil
  R15.call("core:get_ui_root()")
  local ok_r, r = pcall(function() return core:get_ui_root() end)
  if ok_r and r ~= nil then root = r end
  if root == nil then
    R15.out("CHAIN aborted: core:get_ui_root() returned nil")
    return false
  end
  local cur = nil
  local cur_path = nil
  for k = 1, #R15.chain do
    local name = R15.chain[k]
    local got, how = nil, nil
    if k == 1 then
      R15.call("ui_root:Find(" .. q(name) .. ", false)")
      local ok_f, raw = pcall(function() return root:Find(name, false) end)
      if ok_f and raw ~= nil and raw ~= false then got = wrap(raw); how = "root:Find" end
      if got == nil then
        got = R15.find_child_named(root, name)
        if got ~= nil then how = "root direct child" end
      end
      cur_path = name
    else
      got = R15.find_child_named(cur, name)
      if got ~= nil then how = "direct child" end
      if got == nil then
        R15.call(q(cur_path) .. ":Find(" .. q(name) .. ", false)")
        local ok_f, raw = pcall(function() return cur:Find(name, false) end)
        if ok_f and raw ~= nil and raw ~= false then
          got = wrap(raw); how = "Find (recursive) from parent"
        end
      end
      cur_path = (cur_path or "?") .. "/" .. name
    end
    if got == nil then
      R15.out("CHAIN link " .. tostring(k) .. "/" .. tostring(#R15.chain)
        .. " id=" .. q(name) .. " NOT FOUND under " .. R14.qpath(cur_path or "?"))
      return false
    end
    local cn = R15.child_count(got)
    R15.nodes[k] = { id = name, uic = got, how = how, children = cn, path = cur_path }
    R15.out("SEED link " .. tostring(k) .. "/" .. tostring(#R15.chain) .. " path=" .. R14.qpath(cur_path)
      .. " id=" .. q(name) .. " how=" .. q(how) .. " children=" .. tostring(cn))
    cur = got
  end
  R15.list_uic = cur
  R15.list_path = cur_path
  R15.chain_ok = true
  R15.out("SEED resolved the FULL chain; list path=" .. R14.qpath(R15.list_path)
    .. " children=" .. tostring(R15.child_count(R15.list_uic)))
  return true
end

-- ---------------------------------------------------------------- the walk
function R15.walk(uic, path, depth)
  if uic == nil then return end
  if R15.walk_count >= R15.walk_visits then
    R15.walk_cap()
    return
  end
  if depth > R15.walk_depth then return end
  if R15.walk_seen[uic] ~= nil then return end
  R15.walk_seen[uic] = true
  R15.walk_count = R15.walk_count + 1
  local id = R15.id_of(uic)
  R15.call("WALK " .. R14.qpath(path) .. " ChildCount/GetStateText/GetTooltipText/Visible/VisibleFromRoot")
  local cn = R15.child_count(uic)
  local st = R15.read_text(function() return uic:GetStateText() end)
  local tip = R15.read_text(function() return uic:GetTooltipText() end)
  local vis, vfr = R14.vis_of(uic)
  R15.out("DOWN path=" .. R14.qpath(path) .. " id=" .. q(id) .. " children=" .. tostring(cn)
    .. " stext=" .. q(st) .. " tip=" .. q(tip) .. " vis=" .. tostring(vis) .. " vfr=" .. tostring(vfr))
  R15.walked[#R15.walked + 1] = { id = id, uic = uic, path = path, stext = st, tip = tip, depth = depth }
  if depth >= R15.walk_depth then return end
  for i = 0, cn - 1 do
    if R15.walk_count >= R15.walk_visits then R15.walk_cap(); return end
    R15.call("WALK " .. R14.qpath(path) .. ":Find(" .. tostring(i) .. ")")
    local ch = R15.child_at(uic, i)
    if ch ~= nil then
      local cid = R15.id_of(ch)
      if cid == nil or cid == "" then cid = "#" .. tostring(i) end
      R15.walk(ch, path .. "/" .. cid, depth + 1)
    end
  end
end

-- ---------------------------------------------------------------- the readers
-- ONE tracked-field read: returns (value-text, ok). kind = "text" | "vis" | "ctx".
-- A raising read returns ok=false (counted as a warning, IGNORED by the change
-- detection - a dead handle can never fake a WIN).
function R15.read_field(e)
  if e.kind == "vis" then
    local v, ok = readb(function() return e.uic:Visible() end)
    return v, ok
  elseif e.kind == "ctx" then
    local ok, raw = pcall(function() return e.uic:GetContextObjectId("CcoUnitStat") end)
    if not ok then return nil, false end
    if raw == nil then return "<nil>", true end
    local s = safe_text(raw)
    if s == nil then return "<opaque>", true end
    return s, true
  else
    local ok, raw = pcall(function() return e.uic:GetStateText() end)
    if not ok then return nil, false end
    if raw == nil then return "<nil>", true end
    local s = safe_text(raw)
    if s == nil then return "<opaque>", true end
    return s, true
  end
end

-- ONE GetContextObjectId read for the step-A dump (counted; capped).
function R15.read_ctxid(comp, type_id)
  if R15.ctx_calls >= R15.ctx_cap then
    if not R15.ctx_cap_spoken then
      R15.ctx_cap_spoken = true
      R15.out("ctx-id call budget reached (" .. tostring(R15.ctx_cap) .. ") - further GetContextObjectId calls are skipped")
    end
    return "<cap>"
  end
  R15.ctx_calls = R15.ctx_calls + 1
  local ok, raw = pcall(function() return comp:GetContextObjectId(type_id) end)
  if not ok then return "<ERR>" end
  if raw == nil then return "<nil>" end
  local s = safe_text(raw)
  if s == nil then return "<opaque>" end
  return s
end

-- ------------------------------------------------------------- step A plumbing
-- Register ONE comparison-named component (stext + Visible tracked), once.
function R15.register_compare(n, comp, id)
  if R15.seen_comp[comp] then return end
  if #R15.tracked + 2 > R15.tracked_max then
    if not R15.tracked_cap_spoken then
      R15.tracked_cap_spoken = true
      R15.out("tracker cap reached (" .. tostring(R15.tracked_max) .. ") - further comparison components are not tracked")
    end
    return
  end
  R15.seen_comp[comp] = true
  R15.compar_n = R15.compar_n + 1
  local field = nil
  if id ~= nil and R14.id_has(id, "label_compare") and not R15.label_compare_seen then
    R15.label_compare_seen = true
    field = "label_compare"
  else
    field = "compare:" .. tostring(id)
  end
  R15.track_new(n, field, "text", comp)
  R15.track_new(n, "vis:" .. tostring(id), "vis", comp)
end

-- Add ONE tracked field, recording its baseline value.
function R15.track_new(n, field, kind, comp)
  if #R15.tracked >= R15.tracked_max then
    if not R15.tracked_cap_spoken then
      R15.tracked_cap_spoken = true
      R15.out("tracker cap reached (" .. tostring(R15.tracked_max) .. ") - further fields are not tracked")
    end
    return
  end
  local v, ok = R15.read_field({ kind = kind, uic = comp })
  if not ok then v = "<ERR>" end
  R15.tracked[#R15.tracked + 1] = { row = n, field = field, kind = kind, uic = comp,
    base = v, last = v, deviated = false }
  R15.out("TRACK row=" .. tostring(n) .. " field=" .. q(field) .. " base=" .. q(v))
end

-- ONE dumped component: id/stext/tip/vis/state + compare-named registration.
function R15.dump_node(n, kind, i, j, comp)
  if R15.dump_nodes >= R15.dump_max then
    if not R15.dump_cap_spoken then
      R15.dump_cap_spoken = true
      R15.out("CMP dump budget reached (" .. tostring(R15.dump_max) .. ") - remaining components are not dumped")
    end
    return
  end
  R15.dump_nodes = R15.dump_nodes + 1
  R15.call(kind .. " row=" .. tostring(n) .. " read Id/GetStateText/GetTooltipText/Visible/CurrentState")
  local id = R15.id_of(comp)
  local cn = R15.child_count(comp)
  local st = R15.read_text(function() return comp:GetStateText() end)
  local tip = R15.read_text(function() return comp:GetTooltipText() end)
  local vis, vfr = R14.vis_of(comp)
  local state = R15.read_text(function() return comp:CurrentState() end)
  local at = " o=" .. tostring(i)
  if kind == "CMPG" then at = at .. " g=" .. tostring(j) end
  R15.out(kind .. " row=" .. tostring(n) .. at .. " id=" .. q(id) .. " children=" .. tostring(cn)
    .. " stext=" .. q(st) .. " tip=" .. q(tip) .. " vis=" .. tostring(vis) .. " vfr=" .. tostring(vfr)
    .. " state=" .. q(state))
  if id ~= nil and R14.id_has(id, "compar") then
    R15.register_compare(n, comp, id)
  end
end

-- The row's OWN context ids (logged ALWAYS - a nil here is a baseline fact).
function R15.ctx_row_line(n, rec)
  local a = R15.read_ctxid(rec.uic, "CcoUnitStat")
  local b = R15.read_ctxid(rec.uic, "CcoUnitDetails")
  R15.out("CTXROW row=" .. tostring(n) .. " CcoUnitStat=" .. q(a) .. " CcoUnitDetails=" .. q(b))
end

-- The row's CHILDREN context ids (every NON-nil id is logged, per the plan).
function R15.ctx_child_line(n, i, ch)
  local id = R15.id_of(ch)
  local a = R15.read_ctxid(ch, "CcoUnitStat")
  if a ~= "<nil>" and a ~= "<cap>" and a ~= "<ERR>" then
    R15.out("CTXID row=" .. tostring(n) .. " o=" .. tostring(i) .. " comp=" .. q(id)
      .. " type=CcoUnitStat -> " .. q(a))
  end
  local b = R15.read_ctxid(ch, "CcoUnitDetails")
  if b ~= "<nil>" and b ~= "<cap>" and b ~= "<ERR>" then
    R15.out("CTXID row=" .. tostring(n) .. " o=" .. tostring(i) .. " comp=" .. q(id)
      .. " type=CcoUnitDetails -> " .. q(b))
  end
end

-- ONE paired stat row: name -> value, then the comparison dump (children and one
-- level deeper), the ctx-id calls, and the trackers (rowctx + compare fields).
function R15.pair_row(n, rec, sn)
  if sn == nil then sn = R15.find_child_named(rec.uic, "stat_name") end
  R15.call("row " .. tostring(n) .. " name read (stat_name:GetStateText)")
  local name_text = nil
  if sn ~= nil then name_text = R15.read_text(function() return sn:GetStateText() end) end
  local dv = nil
  local vh = R15.find_child_named(rec.uic, "value_holder")
  if vh ~= nil then dv = R15.find_child_named(vh, "dy_value") end
  if dv == nil then dv = R15.find_child_named(rec.uic, "dy_value") end
  if dv == nil then dv = R15.find_child_named(rec.uic, "value") end
  local val_text = nil
  if dv ~= nil then val_text = R15.read_text(function() return dv:GetStateText() end) end
  R15.rows[n] = { n = n, name = name_text, value = val_text, rowid = rec.id, uic = rec.uic }
  R15.out("CMP row=" .. tostring(n) .. " name=" .. q(name_text) .. " value=" .. q(val_text)
    .. " rowid=" .. q(rec.id) .. " path=" .. R14.qpath(rec.path))
  R15.ctx_row_line(n, rec)
  R15.track_new(n, "rowctx", "ctx", rec.uic)
  local cn = R15.child_count(rec.uic)
  local lim = cn
  if lim > R15.child_max then lim = R15.child_max end
  for i = 0, lim - 1 do
    local ch = R15.child_at(rec.uic, i)
    if ch ~= nil then
      R15.dump_node(n, "CMPB", i, nil, ch)
      R15.ctx_child_line(n, i, ch)
      local cn2 = R15.child_count(ch)
      local lim2 = cn2
      if lim2 > R15.child_max then lim2 = R15.child_max end
      for j = 0, lim2 - 1 do
        local g = R15.child_at(ch, j)
        if g ~= nil then R15.dump_node(n, "CMPG", i, j, g) end
      end
    end
  end
end

-- Pair every row found under `list`, then dump it.
function R15.pair_and_dump_rows()
  R15.rows = {}
  R15.tracked = {}
  R15.seen_comp = {}
  R15.compar_n = 0
  R15.label_compare_seen = false
  local n = 0
  for k = 1, #R15.walked do
    if n >= R15.row_max then break end
    local rec = R15.walked[k]
    if rec.id ~= nil and R14.id_has(rec.id, "row_header_stats") then
      R15.out("ROWHEADER path=" .. R14.qpath(rec.path) .. " id=" .. q(rec.id) .. " stext=" .. q(rec.stext))
    end
    local is_row = (rec.id ~= nil and R14.id_has(rec.id, "template_stat"))
    local sn = nil
    if not is_row and rec.uic ~= nil then
      sn = R15.find_child_named(rec.uic, "stat_name")
      if sn ~= nil then is_row = true end
    end
    if is_row then
      n = n + 1
      R15.pair_row(n, rec, sn)
    end
  end
  R15.out("CMP dump done: rows=" .. tostring(#R15.rows) .. " tracked=" .. tostring(#R15.tracked)
    .. " compar_comps=" .. tostring(R15.compar_n) .. " dump_nodes=" .. tostring(R15.dump_nodes)
    .. " ctx_calls=" .. tostring(R15.ctx_calls))
end

-- Pick ONE non-selected visible card as the hover target.
function R15.pick_target()
  R15.target = nil
  R15.selected_card = nil
  local cards = r5_read_cards()
  local sel = r5_selected_set(cards)
  for i = 1, #cards do
    local c = cards[i]
    if c.id ~= nil and sel[c.id] == true then
      R15.selected_card = c.id
      break
    end
  end
  for i = 1, #cards do
    local c = cards[i]
    if c.uic ~= nil and c.vis == "true" and c.id ~= nil and sel[c.id] ~= true then
      local ok_id, raw = pcall(function() return c.uic:GetContextObjectId("CcoBattleUnit") end)
      local ctx = nil
      if ok_id then ctx = safe_text(raw) end
      if ctx == nil or ctx == "" then ctx = c.id end
      R15.target = { id = c.id, uic = c.uic, ctx = ctx, state = c.state }
      break
    end
  end
  if R15.target ~= nil then
    R15.out("TARGET card=" .. q(R15.target.id) .. " ctx=" .. q(R15.target.ctx)
      .. " state=" .. q(R15.target.state) .. " | selected_card=" .. q(R15.selected_card)
      .. " cards=" .. tostring(#cards))
  else
    R15.out("TARGET NONE: no NON-selected visible card was found - keep the cards panel up with >= 2 units"
      .. " and ONE selected, then re-run zz_probe_r15()")
  end
end

-- ------------------------------------------------------------- the pass engine
-- ONE SimulateMouseOn - logged IMMEDIATELY BEFORE the call (a crash names it).
function R15.sim_on(card, pass_n, hold)
  R15.sim_on_total = R15.sim_on_total + 1
  local n = R15.sim_on_total
  R15.out("SIMHOVER SimulateMouseOn pass=" .. tostring(pass_n) .. " card=" .. q(card.id)
    .. " hold=" .. tostring(hold) .. "ms (call " .. tostring(n) .. "; logged BEFORE the call)")
  local ok, err = pcall(function() return card.uic:SimulateMouseOn() end)
  if not ok then
    R15.out("SIMHOVER SimulateMouseOn error (swallowed): " .. truncate(err, 140))
    return false
  end
  return true
end

-- ONE SimulateMouseOff - EVERY On is paired with this, whatever happened.
function R15.sim_off(card, pass_n)
  R15.sim_off_total = R15.sim_off_total + 1
  local n = R15.sim_off_total
  R15.out("SIMHOVER SimulateMouseOff pass=" .. tostring(pass_n) .. " card=" .. q(card.id)
    .. " (call " .. tostring(n) .. "; logged BEFORE the call)")
  local ok, err = pcall(function() return card.uic:SimulateMouseOff() end)
  if not ok then
    R15.out("SIMHOVER SimulateMouseOff error (swallowed): " .. truncate(err, 140))
    return false
  end
  return true
end

-- Refresh the baseline RIGHT BEFORE a pass (absorbs any pre-hover drift; the
-- refresh is logged for every field it actually moved).
function R15.rebase()
  for i = 1, #R15.tracked do
    local e = R15.tracked[i]
    local cur, ok = R15.read_field(e)
    if ok then
      if cur ~= e.base then
        R15.out("REBASE row=" .. tostring(e.row) .. " field=" .. q(e.field)
          .. " stored=" .. q(e.base) .. " now=" .. q(cur) .. " (pre-hover drift absorbed; baseline refreshed for this pass)")
      end
      e.base = cur
      e.last = cur
    else
      e.last = e.base
    end
    e.deviated = false
  end
end

-- The delta arithmetic line: the selected value + the delta, so the
-- hover = selected - delta check can be made.
function R15.maybe_delta(p, e, cur)
  local d = tonumber(cur)
  if d == nil then return end
  local r = R15.rows[e.row]
  local sv = nil
  local sn = nil
  if r ~= nil then
    sv = r.value
    if sv ~= nil then sn = tonumber(sv) end
  end
  local exp = "?"
  if sn ~= nil then exp = q(tostring(sn - d)) end
  R15.deltas = R15.deltas + 1
  R15.out("DELTA pass=" .. tostring(p.n) .. " row=" .. tostring(e.row) .. " field=" .. q(e.field)
    .. " delta=" .. q(cur) .. " selected(" .. q(r ~= nil and r.name or "?") .. ")=" .. q(sv or "<nil>")
    .. " hovered_expected=" .. exp .. " (label = selected - hovered)")
end

-- ONE pass poll sample: read every tracked field; log the instant any changes.
function R15.sample_pass(p)
  p.samples = p.samples + 1
  for i = 1, #R15.tracked do
    local e = R15.tracked[i]
    local cur, ok = R15.read_field(e)
    if not ok then
      p.warns = p.warns + 1
      R15.warn_total = R15.warn_total + 1
      if not p.warn_spoken then
        p.warn_spoken = true
        R15.out("WARN pass=" .. tostring(p.n) .. " row=" .. tostring(e.row) .. " field=" .. q(e.field)
          .. " read failed (ignored; warns counted - a dead handle never fakes a WIN)")
      end
    elseif cur ~= e.last then
      p.events = p.events + 1
      R15.events_total = R15.events_total + 1
      R15.out("HOVER pass=" .. tostring(p.n) .. " hold=" .. tostring(p.hold) .. " t=" .. tostring(p.t)
        .. " row=" .. tostring(e.row) .. " field=" .. q(e.field)
        .. " was=" .. q(e.last) .. " now=" .. q(cur))
      if cur ~= e.base and not e.deviated then
        e.deviated = true
        p.fields_dev = p.fields_dev + 1
        if e.kind == "text" then p.text_dev = p.text_dev + 1
        elseif e.kind == "ctx" then p.ctx_dev = p.ctx_dev + 1
        elseif e.kind == "vis" then p.vis_dev = p.vis_dev + 1 end
        if e.kind ~= "vis" then
          if R15.first_evidence == nil then
            R15.first_evidence = { pass = p.n, row = e.row, field = e.field, was = e.base, now = cur }
          end
          if e.kind == "text" then
            if R15.first_text == nil then
              R15.first_text = { pass = p.n, row = e.row, field = e.field, was = e.base, now = cur }
            end
            R15.maybe_delta(p, e, cur)
          end
        end
      end
      e.last = cur
    end
  end
end

-- Arm ONE pass; the async 25 ms poll drives it from here.
function R15.arm(pass_n)
  if not R15.baseline_ok then
    return false, "the baseline (step A) recorded no stat rows - open AND PIN the unit-info panel with ONE unit"
      .. " selected and the Stats tab visible, then re-run zz_probe_r15() and start again"
  end
  if R15.pass ~= nil and R15.pass.active then
    local p = R15.pass
    return false, "a pass is still in flight (pass " .. tostring(p.n) .. ", phase=" .. tostring(p.phase)
      .. ", t=" .. tostring(p.t) .. " ms, samples=" .. tostring(p.samples)
      .. ") - wait for 'R15 PASS n=" .. tostring(p.n) .. " ... done' in the log, then call zz_probe_r15_step() again"
  end
  if R15.target == nil then
    return false, "no NON-selected visible card was found at baseline - keep the cards panel up with >= 2 units,"
      .. " select ONE, then re-run zz_probe_r15() and start again"
  end
  if #R15.tracked == 0 then
    return false, "no tracked comparison fields (the step-A dump found none) - check the log, then re-run zz_probe_r15()"
  end
  if R15.sim_on_total >= R15.max_sims then
    return false, "the simulated-hover cap (" .. tostring(R15.max_sims) .. ") is reached - run the verdict/done or restart"
  end
  local hold = R15.holds[pass_n]
  if hold == nil then return false, "unknown pass " .. tostring(pass_n) end
  R15.rebase()
  R15.pass = { n = pass_n, hold = hold, active = true, phase = "arm", t = 0, polls = 0, samples = 0,
               events = 0, fields_dev = 0, text_dev = 0, ctx_dev = 0, vis_dev = 0,
               warns = 0, warn_spoken = false, on_ok = false, off_ok = false, settle_n = 0 }
  local kind = "INVISIBLE (below the " .. tostring(R15.visible_ms) .. " ms tooltip draw delay)"
  if pass_n == 4 then kind = "CONTROL (the tooltip WILL draw - expected)" end
  R15.out("PASS n=" .. tostring(pass_n) .. " arm hold=" .. tostring(hold) .. " ms [" .. kind
    .. "] - SimulateMouseOn on the next 25 ms poll, sampling every poll")
  if pass_n == 4 then
    R15.out("CONTROL pass running - WATCH THE SCREEN NOW (the tooltip drawing is EXPECTED);"
      .. " hands OFF the console until 'R15 PASS n=4 ... done' appears in the log")
  end
  return true, "pass " .. tostring(pass_n) .. " armed (hold " .. tostring(hold) .. " ms, " .. kind
    .. "); it finishes in ~" .. tostring(hold + R15.settle_ms)
    .. " ms - wait for 'R15 PASS n=" .. tostring(pass_n) .. " ... done' in the log, then call zz_probe_r15_step() again"
end

-- ONE pass poll (driven by zz_probe_r15_poll at the requested 25 ms cadence).
function R15.poll_body()
  local p = R15.pass
  if p == nil or not p.active then return end
  p.polls = p.polls + 1
  if p.phase == "arm" then
    p.on_ok = R15.sim_on(R15.target, p.n, p.hold)
    p.phase = "hold"
    p.t = 0
  end
  p.t = p.t + R15.poll_ms
  if p.phase == "hold" then
    R15.sample_pass(p)
    if p.t >= p.hold then
      p.off_ok = R15.sim_off(R15.target, p.n)
      p.phase = "settle"
      p.settle_n = 0
      R15.out("PASS n=" .. tostring(p.n) .. " SimulateMouseOff issued at t=" .. tostring(p.t)
        .. " ms nominal (" .. tostring(p.samples) .. " samples so far); settling "
        .. tostring(R15.settle_ms) .. " ms")
    end
  else
    R15.sample_pass(p)
    p.settle_n = p.settle_n + 1
    if p.settle_n >= math.ceil(R15.settle_ms / R15.poll_ms) then
      R15.finish_pass(p)
    end
  end
end

-- Finish ONE pass: the verdict-grade line + the record the R15 verdict reads.
function R15.finish_pass(p)
  local still = 0
  for i = 1, #R15.tracked do
    local e = R15.tracked[i]
    if e.last ~= e.base then still = still + 1 end
  end
  R15.results[p.n] = { hold = p.hold, events = p.events, fields_dev = p.fields_dev,
    text_dev = p.text_dev, ctx_dev = p.ctx_dev, vis_dev = p.vis_dev, still = still,
    warns = p.warns, on_ok = p.on_ok, off_ok = p.off_ok, samples = p.samples, polls = p.polls }
  R15.out("PASS n=" .. tostring(p.n) .. " hold=" .. tostring(p.hold) .. " done changed=" .. tostring(p.events)
    .. " fields_dev=" .. tostring(p.fields_dev) .. " still_at_end=" .. tostring(still)
    .. " text_dev=" .. tostring(p.text_dev) .. " ctx_dev=" .. tostring(p.ctx_dev)
    .. " vis_dev=" .. tostring(p.vis_dev) .. " warns=" .. tostring(p.warns)
    .. " on_ok=" .. tostring(p.on_ok) .. " off_ok=" .. tostring(p.off_ok)
    .. " samples=" .. tostring(p.samples) .. " polls=" .. tostring(p.polls))
  if p.vis_dev > 0 and p.text_dev == 0 and p.ctx_dev == 0 then R15.vis_only_note = true end
  p.active = false
  if p.n == 4 and not R15.pairs_spoken then
    R15.pairs_spoken = true
    R15.out("PAIRS sim_on=" .. tostring(R15.sim_on_total) .. " sim_off=" .. tostring(R15.sim_off_total)
      .. " paired=" .. tostring(R15.sim_on_total == R15.sim_off_total))
    if R15.sim_on_total ~= R15.sim_off_total then
      R15.out("WARNING: SimulateMouseOn and SimulateMouseOff counts differ - a simulated hover may be stuck")
    end
  end
end

-- ---------------------------------------------------------------- the steps
R15.steps = {}

-- STEP 1 (A) - the read-only baseline dump.
R15.steps[1] = function()
  R15.out("STEP 1 - A BASELINE (READ-ONLY, no hover): dump every stat row's comparison components"
    .. " + context ids, record the baseline values, pick ONE non-selected card")
  R15.nodes = {}
  R15.list_uic = nil
  R15.list_path = nil
  R15.chain_ok = false
  R15.walked = {}
  R15.walk_count = 0
  R15.walk_seen = {}
  R15.walk_cap_spoken = false
  R15.rows = {}
  R15.tracked = {}
  R15.seen_comp = {}
  R15.compar_n = 0
  R15.label_compare_seen = false
  R15.tracked_cap_spoken = false
  R15.dump_nodes = 0
  R15.dump_cap_spoken = false
  R15.ctx_calls = 0
  R15.ctx_cap_spoken = false
  R15.target = nil
  R15.selected_card = nil
  R15.baseline_ok = false
  if not R15.resolve_chain() then
    R15.out("STEP 1 aborted: the discovered chain did not resolve - is the unit-info panel OPEN and PINNED?"
      .. " (re-run zz_probe_r15() after fixing it)")
    return true, "baseline aborted (chain not resolved)"
  end
  if R15.list_uic == nil then
    R15.out("STEP 1 aborted: the `list` node was not resolved")
    return true, "baseline aborted (no `list`)"
  end
  R15.walk(R15.list_uic, R15.list_path, 0)
  R15.pair_and_dump_rows()
  R15.pick_target()
  R15.baseline_ok = (R15.chain_ok and #R15.rows > 0)
  R15.out("BASELINE rows=" .. tostring(#R15.rows) .. " tracked=" .. tostring(#R15.tracked)
    .. " compar_comps=" .. tostring(R15.compar_n) .. " ctx_calls=" .. tostring(R15.ctx_calls)
    .. " target=" .. (R15.target ~= nil and q(R15.target.id) or "NONE")
    .. " selected_card=" .. q(R15.selected_card) .. " baseline_ok=" .. tostring(R15.baseline_ok))
  if not R15.baseline_ok then
    R15.out("BASELINE INCOMPLETE: no stat rows were found - open AND PIN the unit-info panel with ONE unit"
      .. " SELECTED (Stats tab visible), then re-run zz_probe_r15()")
  end
  return true, "baseline done (rows=" .. tostring(#R15.rows) .. ", tracked=" .. tostring(#R15.tracked) .. ")"
end

-- STEPS 2-5 - the four passes (3 invisible + 1 control).
R15.steps[2] = function() return R15.arm(1) end
R15.steps[3] = function() return R15.arm(2) end
R15.steps[4] = function() return R15.arm(3) end
R15.steps[5] = function() return R15.arm(4) end

-- per-pass event count for the verdict line (-1 = the pass never completed).
function R15.ev(i)
  local r = R15.results[i]
  if r == nil then return -1 end
  return r.events or 0
end

-- summed field counts over the three INVISIBLE passes.
function R15.sum3(f)
  local s = 0
  for i = 1, 3 do
    local r = R15.results[i]
    if r ~= nil then s = s + (r[f] or 0) end
  end
  return s
end

-- STEP 6 - VERDICT.
R15.steps[6] = function()
  R15.out("STEP 6 - VERDICT")
  local t3 = R15.sum3("text_dev")
  local c3 = R15.sum3("ctx_dev")
  local v3 = R15.sum3("vis_dev")
  local r4 = R15.results[4]
  local t4 = (r4 ~= nil and r4.text_dev) or 0
  local c4 = (r4 ~= nil and r4.ctx_dev) or 0
  local v4 = (r4 ~= nil and r4.vis_dev) or 0
  R15.out("VERDICT pass1_changed=" .. tostring(R15.ev(1)) .. " pass2_changed=" .. tostring(R15.ev(2))
    .. " pass3_changed=" .. tostring(R15.ev(3)) .. " control_changed=" .. tostring(R15.ev(4)))
  R15.out("VERDICT detail invisible: text_dev=" .. tostring(t3) .. " ctx_dev=" .. tostring(c3)
    .. " vis_dev=" .. tostring(v3) .. " | control: text_dev=" .. tostring(t4) .. " ctx_dev=" .. tostring(c4)
    .. " vis_dev=" .. tostring(v4) .. " | deltas=" .. tostring(R15.deltas)
    .. " events_total=" .. tostring(R15.events_total) .. " warns=" .. tostring(R15.warn_total))
  R15.win = ((t3 + c3) > 0)
  if R15.win then
    local e = R15.first_text or R15.first_evidence or {}
    R15.out("*** WIN: hover exposes non-selected stats INVISIBLY *** first_evidence pass=" .. tostring(e.pass)
      .. " row=" .. tostring(e.row) .. " field=" .. q(e.field) .. " was=" .. q(e.was) .. " now=" .. q(e.now))
  else
    R15.out("no invisible exposure; control_changed=" .. tostring(R15.ev(4)))
    if v3 > 0 then
      R15.out("NOTE: an invisible pass saw visibility-only reactivity (no VALUE deviation) - see the detail line")
    end
  end
  if R15.deltas > 0 then
    R15.out("VERDICT deltas=" .. tostring(R15.deltas)
      .. " (see the R15 DELTA lines for the selected value + the hover = selected - delta check)")
  end
  return true, "verdict done (win=" .. tostring(R15.win) .. ")"
end

-- STEP 7 - DONE.
R15.steps[7] = function()
  R15.out("STEP 7 - DONE")
  local paired = (R15.sim_on_total == R15.sim_off_total)
  R15.out("DONE run #" .. tostring(R15.run_no) .. ": sim pairs on=" .. tostring(R15.sim_on_total)
    .. " off=" .. tostring(R15.sim_off_total) .. " paired=" .. tostring(paired)
    .. " | events=" .. tostring(R15.events_total) .. " deltas=" .. tostring(R15.deltas)
    .. " win=" .. tostring(R15.win))
  if not paired then
    R15.out("WARNING: SimulateMouseOn and SimulateMouseOff counts differ - a simulated hover may be stuck")
  end
  R15.out("R15 TOTAL STEPS 7 - you are done (STOP). Log: " .. LOG_FILE)
  return true, "done"
end

-- ---------------------------------------------------------------- the driver
function R15.advance()
  if R15.done then
    R15.out("step ignored: the run is done (" .. tostring(R15.total_steps) .. " steps) - zz_probe_r15() restarts it")
    return false, "the run is done (" .. tostring(R15.total_steps) .. " steps) - zz_probe_r15() restarts it"
  end
  local nxt = R15.step + 1
  local fn = R15.steps[nxt]
  if fn == nil then
    R15.done = true
    R15.out("===== ROUND 15 RUN done after " .. tostring(R15.total_steps)
      .. " steps (A, pass1, pass2, pass3, control, verdict, done) - R15 TOTAL STEPS 7 - YOU ARE DONE =====")
    return false, "the run is done (" .. tostring(R15.total_steps) .. " steps)"
  end
  R15.out("")
  R15.out("===== R15 STEP " .. tostring(nxt) .. "/" .. tostring(R15.total_steps)
    .. " (run #" .. tostring(R15.run_no) .. ") =====")
  local ok, a, b = pcall(fn)
  if not ok then
    R15.out("STEP " .. tostring(nxt) .. " raised (swallowed): " .. truncate(a, 160))
    return false, "step " .. tostring(nxt) .. " raised - see the log"
  end
  if a == true then
    R15.step = nxt
    return true, tostring(b or ("step " .. tostring(nxt) .. " ran"))
  end
  R15.out("STEP " .. tostring(nxt) .. " refused (the step did not run; the counter stays at "
    .. tostring(R15.step) .. "): " .. tostring(b))
  return false, tostring(b)
end

-- ---------------------------------------------------------------- the hooks
function R15.reset_run()
  R15.step = 0
  R15.done = false
  R15.results = {}
  R15.pass = nil
  R15.sim_on_total = 0
  R15.sim_off_total = 0
  R15.pairs_spoken = false
  R15.nodes = {}
  R15.list_uic = nil
  R15.list_path = nil
  R15.chain_ok = false
  R15.walked = {}
  R15.walk_count = 0
  R15.walk_seen = {}
  R15.walk_cap_spoken = false
  R15.rows = {}
  R15.tracked = {}
  R15.seen_comp = {}
  R15.compar_n = 0
  R15.label_compare_seen = false
  R15.tracked_cap_spoken = false
  R15.dump_nodes = 0
  R15.dump_cap_spoken = false
  R15.ctx_calls = 0
  R15.ctx_cap_spoken = false
  R15.target = nil
  R15.selected_card = nil
  R15.baseline_ok = false
  R15.deltas = 0
  R15.events_total = 0
  R15.warn_total = 0
  R15.first_evidence = nil
  R15.first_text = nil
  R15.vis_only_note = false
  R15.win = false
end

function zz_probe_r15()
  R15.reset_run()
  return PROBE_TAG .. "R15 READY (step 0 of 7). R15 TOTAL STEPS 7 - you are done after step 7."
    .. " With the unit-info panel OPEN and PINNED and ONE unit selected (cards panel up with >= 2 units),"
    .. " call zz_probe_r15_step() SEVEN times, ONE step at a time. The steps: A baseline (read-only),"
    .. " pass1 hold=100 ms, pass2 hold=150 ms, pass3 hold=250 ms (the three INVISIBLE passes - below the "
    .. tostring(R15.visible_ms) .. " ms tooltip delay), the CONTROL pass hold=1500 ms (the tooltip WILL draw -"
    .. " WATCH THE SCREEN on that one only), verdict, done. Between pass steps wait for 'R15 PASS n=.. done'"
    .. " in the log. log=" .. LOG_FILE
end

function zz_probe_r15_step()
  if R15.step == 0 and (not R15.done) then
    R15.run_no = R15.run_no + 1
    R15.lines = 0
    R15.line_cap_spoken = false
    R15.out("")
    R15.out("===== ROUND 15 RUN #" .. tostring(R15.run_no) .. " (manual zz_probe_r15_step) =====")
    R15.out("R15 TOTAL STEPS 7: 1) A baseline dump (read-only), 2) pass1 hold=100 ms, 3) pass2 hold=150 ms,"
      .. " 4) pass3 hold=250 ms (ALL THREE INVISIBLE - below the " .. tostring(R15.visible_ms)
      .. " ms tooltip draw delay), 5) the CONTROL pass hold=1500 ms (the tooltip WILL draw - WATCH THE SCREEN),"
      .. " 6) verdict, 7) done. ONE step per call; after any pass step, wait for 'R15 PASS n=.. done' in the"
      .. " log (the pass runs asynchronously on its own 25 ms poll) before the next call.")
  end
  local before = R15.step
  local adv, note = R15.advance()
  local nxt
  if R15.done or R15.step >= R15.total_steps then
    nxt = "DONE - STOP (zz_probe_r15 finished after " .. tostring(R15.total_steps) .. " steps)"
  else
    nxt = "step " .. tostring(R15.step + 1) .. " of " .. tostring(R15.total_steps)
  end
  if adv then
    return PROBE_TAG .. "R15 step " .. tostring(R15.step) .. "/" .. tostring(R15.total_steps)
      .. " done (was " .. tostring(before) .. "): " .. note
      .. " | next: " .. nxt .. " - call zz_probe_r15_step() again. log=" .. LOG_FILE
  end
  return PROBE_TAG .. "R15 step NOT advanced (still " .. tostring(R15.step) .. "/" .. tostring(R15.total_steps)
    .. "): " .. note .. " | call zz_probe_r15_step() again. log=" .. LOG_FILE
end

-- the 25 ms poll: idle and SILENT between passes; wraps the body in a pcall so
-- an error can never escape a timer callback.
function zz_probe_r15_poll()
  local ok, err = pcall(R15.poll_body)
  if not ok then
    log("R15 poll error (swallowed): " .. truncate(err, 160))
  end
end

function zz_probe_r15_status()
  local p = R15.pass
  return PROBE_TAG .. "R15 TOTAL STEPS " .. tostring(R15.total_steps) .. " - step=" .. tostring(R15.step)
    .. "/" .. tostring(R15.total_steps) .. " done=" .. tostring(R15.done)
    .. " lines=" .. tostring(R15.lines) .. "/" .. tostring(R15.max_lines)
    .. " | baseline_ok=" .. tostring(R15.baseline_ok) .. " rows=" .. tostring(#R15.rows)
    .. " tracked=" .. tostring(#R15.tracked) .. " target=" .. (R15.target ~= nil and q(R15.target.id) or "nil")
    .. " | pass=" .. ((p ~= nil and p.active) and (tostring(p.n) .. " phase=" .. tostring(p.phase)
      .. " t=" .. tostring(p.t) .. "ms samples=" .. tostring(p.samples)) or "idle")
    .. " sim_on=" .. tostring(R15.sim_on_total) .. " sim_off=" .. tostring(R15.sim_off_total)
    .. " | results changed: 1:" .. tostring(R15.ev(1)) .. " 2:" .. tostring(R15.ev(2))
    .. " 3:" .. tostring(R15.ev(3)) .. " 4:" .. tostring(R15.ev(4))
    .. " win=" .. tostring(R15.win) .. " | zz_probe_r15() to start/restart; log=" .. LOG_FILE
end

function zz_probe_r15_help()
  return PROBE_TAG .. "ROUND 15 - THE FINAL EXPERIMENT (user-designed). R15 TOTAL STEPS 7 - you are done"
    .. " after step 7. RELAUNCH so this build loads, start a battle, OPEN AND PIN the unit-info panel,"
    .. " select ONE unit, keep the cards panel up with >= 2 units, then: zz_probe_r15() once, then"
    .. " zz_probe_r15_step() SEVEN times, ONE step at a time. Steps: 1) A baseline (read-only dump of every"
    .. " stat row's comparison components + context ids); 2-4) three SIMULATED hover passes over ONE"
    .. " NON-selected card at holds 100/150/250 ms - ALL INVISIBLE (below the " .. tostring(R15.visible_ms)
    .. " ms tooltip draw delay); 5) the CONTROL pass at 1500 ms - THE TOOLTIP WILL DRAW (expected): WATCH"
    .. " THE SCREEN ON THIS PASS ONLY; 6) the verdict (pass1_changed/pass2_changed/pass3_changed/"
    .. " control_changed + the R15 *** WIN *** line if an invisible pass exposed a non-selected unit's stat"
    .. " value, else 'no invisible exposure; control_changed=<n>'; the R15 DELTA lines carry the selected"
    .. " value + the delta for the hover = selected - delta check); 7) done. Every pass polls every 25 ms"
    .. " for changes in label_compare text, comparison-named component text and the row's CcoUnitStat"
    .. " context id, logging each change with before/after values. EVERY SimulateMouseOn is paired with its"
    .. " SimulateMouseOff. ZERO context writes; the name-lookup helper is BANNED. Log: " .. LOG_FILE
end
