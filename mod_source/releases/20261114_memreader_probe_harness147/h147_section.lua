
-- ============================================================================
-- HARNESS 147 (round 148): THE MEMREADER PROBE. A mock _G.memreader_plus:
--   B1 absent   -> one "MEMREADER absent" row, mr_ fields "-", nothing cast
--   B2 present  -> the three reads land on the row (lead / hp / men per unit)
--   B3 throwing -> "?" fields, ONE "read failed" row, "off" after 3 units in a
--                  row, then "-" fields; no poll error, nothing cast
--   every world -> the mod never calls write / hook / hook_site / call / patch
-- RED: H147_LIVE / H147_ANN = the pre-148 snapshot (no mr_ fields, no status row).
-- ============================================================================
function run_h147()
  local pre147 = checks
  local L147 = os.getenv("H147_LIVE") or LIVE
  local A147 = os.getenv("H147_ANN") or ANN
  local RED147 = (os.getenv("H147_LIVE") ~= nil) or (os.getenv("H147_ANN") ~= nil)
  local SW = "wh_main_emp_inf_swordsmen"
  local ORC = "wh_main_grn_inf_orc_boyz"
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1; at = i + #tok
    end
  end
  print("== HARNESS 147 - section 0zt: the round-148 tokens ==")
  if not RED147 then
    for _, f in ipairs({ { name = "live", path = L147 }, { name = "ann", path = A147 } }) do
      local s = read_file(f.path)
      check("0zt " .. f.name .. ": the probe is defined once, checked once per snapshot, its offsets are round 147's",
        cp(s, "function FOURTH.mr_check()") == 1 and cp(s, "function FOURTH.mr_unit(u)") == 1
        and cp(s, "\tFOURTH.mr_check()\n") == 1
        and cp(s, "FOURTH.MR_LEAD_OFF = 0x3B78\n") == 1 and cp(s, "FOURTH.MR_HP_OFF = 0x5CC\n") == 1
        and cp(s, "FOURTH.MR_MEN_OFF = 0xA4\n") == 1 and cp(s, "FOURTH.MR_FAIL_LIMIT = 3\n") == 1
        and cp(s, '.. " addr=" .. FOURTH.map_addr(u)\nend') == 1
        and cp(s, "\t{ marker = ") == 799)
    end
    local live = read_file(L147)
    local a = raw_find(live, "-- ROUND 148 - THE MEMREADER PROBE", 1, true)
    local b = raw_find(live, "function FOURTH.map_row(u, side, t, alliance)", 1, true)
    local span = (a ~= nil and b ~= nil) and live:sub(a, b) or ""
    check("0zt live: the probe only reads (no write, hook, call, patch; no cast; no string.find)",
      #span > 0 and raw_find(span, "m.write", 1, true) == nil and raw_find(span, "m.hook", 1, true) == nil
      and raw_find(span, "m.call", 1, true) == nil and raw_find(span, "m.patch", 1, true) == nil
      and raw_find(span, "perform_special_ability", 1, true) == nil and raw_find(span, "string.find", 1, true) == nil)
  end

  -- the mock memreader: pointers are tables, memory is a function of the unit's uid
  local forbidden = 0
  local function mock_mr(mode)
    local m = { version = "0.15.2-mock" }
    m.ud_topointer = function(u) return { kind = "iface", u = u } end
    m.is_null = function(p) return p == nil end
    m.read_pointer = function(p, off)
      if mode == "throw" then error("mock: failed to read memory") end
      if p.kind == "iface" and off == 0x8 then return { kind = "obj", u = p.u } end
      if p.kind == "obj" and off == 0x280 then return { kind = "hpo", u = p.u } end
      return nil
    end
    m.read_int32 = function(p, off)
      local uid = 0
      pcall(function() uid = p.u.zz_uid end)
      if p.kind == "obj" and off == 0x3B78 then return 40 + (uid % 100) end
      if p.kind == "obj" and off == 0xA4 then return 100 + (uid % 10) end
      if p.kind == "hpo" and off == 0x5CC then return 7000 + (uid % 100) end
      return -1
    end
    for _, k in ipairs({ "write", "hook", "hook_site", "call", "patch", "code_cave", "unhook" }) do
      m[k] = function() forbidden = forbidden + 1 end
    end
    return m
  end

  local n_ok, n_all = 0, 0
  local function done(ok) n_all = n_all + 1; if ok then n_ok = n_ok + 1 end end
  local function lines_with(W, tok)
    local r = {}
    for _, l in ipairs(W.log_lines or {}) do if raw_find(l, tok, 1, true) ~= nil then r[#r + 1] = l end end
    return r
  end
  local function run_world(label, mode, PATH, TAG)
    forbidden = 0
    _G.memreader_plus = (mode ~= "absent") and mock_mr(mode) or nil
    local units = {
      { name = SW, uid = 17800, owns = {}, melee = false, pos = { 10, 0, 20 }, width = 29.4, initial_men = 120 },
      { name = SW, uid = 17801, owns = {}, melee = true, pos = { 40, 0, 20 }, width = 29.4, initial_men = 120 },
    }
    local enemies = {
      { name = ORC, uid = 17805, melee = true, pos = { 40, 0, 32 }, width = 30.2, initial_men = 120 },
      { name = ORC, uid = 17806, melee = false, pos = { 80, 0, 60 }, width = 30.2, initial_men = 120 },
    }
    local W = make_world({ can_perform = true, units = units, enemies = enemies,
      cards = { { id = "17800", state = "active", vis = true }, { id = "17801", state = "active", vis = true } }, bar = {} })
    print("== " .. TAG .. label .. " ==")
    local ok = pcall(load_world, W, PATH)
    check(TAG .. label .. ": the file loads", ok)
    if ok then
      deploy_phases(W); ui(W)
      W.conflict = true
      polln(W, 24)
    end
    _G.memreader_plus = nil
    return ok and W or nil
  end

  for _, f in ipairs({ { path = A147, tag = "[annotated] " }, { path = L147, tag = "[live] " } }) do
    local TAG = f.tag
    local live = (TAG == "[live] ")
    -- B1 absent
    local W = run_world("B1. memreader Plus absent", "absent", f.path, TAG)
    if W ~= nil then
      local a
      local maps = lines_with(W, "MAP t=")
      if RED147 then
        a = (#lines_with(W, " mr_lead=") == 0 and #lines_with(W, "MEMREADER") == 0)
        check(TAG .. "B1-RED: the pre-148 build has no mr_ field and no MEMREADER row", a)
        done(a)
      elseif live then
        a = (#maps >= 8 and #lines_with(W, " mr_lead=- mr_hp=- mr_men=- ") == #maps
          and #lines_with(W, "MEMREADER absent") == 1 and #lines_with(W, "MEMREADER") == 1)
        check(TAG .. "B1a: every row reads mr_ -, ONE 'absent' row (" .. #maps .. " rows)", a)
        done(a)
        a = (#W.fires == 0 and #lines_with(W, "POLL ERROR") == 0 and forbidden == 0)
        check(TAG .. "B1b: nothing cast, no poll error", a)
        done(a)
      else
        a = (#W.fires == 0 and #lines_with(W, "POLL ERROR") == 0)
        check(TAG .. "B1: the reading copy runs without a poll error and casts nothing", a)
        done(a)
      end
      tally(W)
    end
    if not RED147 then
      -- B2 present
      W = run_world("B2. memreader Plus present", "present", f.path, TAG)
      if W ~= nil then
        local a
        if live then
          local r1 = lines_with(W, " id=17801 ")[1] or ""
          local r2 = lines_with(W, " id=17805 ")[1] or ""
          a = (raw_find(r1, " mr_lead=41 mr_hp=7001 mr_men=101 ", 1, true) ~= nil
            and raw_find(r2, " mr_lead=45 mr_hp=7005 mr_men=105 ", 1, true) ~= nil
            and #lines_with(W, "MEMREADER present version=0.15.2-mock") == 1 and #lines_with(W, "MEMREADER") == 1)
          check(TAG .. "B2a: our row and the enemy's carry their own three reads; ONE 'present' row (" .. r2 .. ")", a)
          done(a)
          a = (#W.fires == 0 and #lines_with(W, "POLL ERROR") == 0 and forbidden == 0)
          check(TAG .. "B2b: nothing cast, no poll error, no write/hook/call (" .. forbidden .. ")", a)
          done(a)
        else
          a = (#W.fires == 0 and #lines_with(W, "POLL ERROR") == 0 and forbidden == 0)
          check(TAG .. "B2: the reading copy reads without a poll error, casts nothing, never writes", a)
          done(a)
        end
        tally(W)
      end
      -- B3 throwing
      W = run_world("B3. memreader Plus reads throw", "throw", f.path, TAG)
      if W ~= nil then
        local a
        if live then
          local maps = lines_with(W, "MAP t=")
          local q = #lines_with(W, " mr_lead=? mr_hp=? mr_men=? ")
          local dash = #lines_with(W, " mr_lead=- mr_hp=- mr_men=- ")
          a = (q == 3 and dash == #maps - 3 and #lines_with(W, "MEMREADER read failed: ") == 1
            and #lines_with(W, "MEMREADER off for this battle after 3 failed units in a row") == 1)
          check(TAG .. "B3a: 3 rows of ?, ONE 'failed' row, ONE 'off' row, then - (" .. q .. " ?, " .. dash
            .. " -, " .. #maps .. " rows)", a)
          done(a)
          a = (#W.fires == 0 and #lines_with(W, "POLL ERROR") == 0 and forbidden == 0)
          check(TAG .. "B3b: nothing cast, no poll error", a)
          done(a)
        else
          a = (#W.fires == 0 and #lines_with(W, "POLL ERROR") == 0)
          check(TAG .. "B3: the reading copy survives throwing reads", a)
          done(a)
        end
        tally(W)
      end
    end
  end
  if RED147 then
    check("RED CONTROL (harness 147): the pre-148 build has no memreader probe - " .. n_ok .. "/" .. n_all,
      n_all == 2 and n_ok == 2)
  else
    check("HARNESS 147: every memreader world behaved - " .. n_ok .. "/" .. n_all, n_all == 9 and n_ok == 9)
  end
  print("== HARNESS 147 done: " .. (checks - pre147) .. " checks in this section ==")
end
