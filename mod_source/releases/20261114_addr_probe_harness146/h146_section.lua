
-- ============================================================================
-- HARNESS 146 (round 147): THE ADDRESS PROBE. Every MAP row ends with
-- " addr=<tostring of the unit handle, spaces as _>". Read-only: it casts
-- nothing. A hostile tostring (raising, non-string) gives "addr=?".
-- RED: H146_LIVE / H146_ANN = the pre-147 snapshot (no addr field).
-- ============================================================================
function run_h146()
  local pre146 = checks
  local L146 = os.getenv("H146_LIVE") or LIVE
  local A146 = os.getenv("H146_ANN") or ANN
  local RED146 = (os.getenv("H146_LIVE") ~= nil) or (os.getenv("H146_ANN") ~= nil)
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
  print("== HARNESS 146 - section 0zs: the round-147 tokens ==")
  if not RED146 then
    for _, f in ipairs({ { name = "live", path = L146 }, { name = "ann", path = A146 } }) do
      local s = read_file(f.path)
      check("0zs " .. f.name .. ": map_addr is defined once and appended once, as the LAST field of the row",
        cp(s, "function FOURTH.map_addr(u)") == 1
        and cp(s, '.. " addr=" .. FOURTH.map_addr(u)\nend') == 1
        and cp(s, "\t{ marker = ") == 799)
    end
    local live = read_file(L146)
    local a = raw_find(live, "function FOURTH.map_addr(u)", 1, true)
    local b = raw_find(live, "function FOURTH.map_row(u, side, t, alliance)", 1, true)
    local span = (a ~= nil and b ~= nil) and live:sub(a, b) or ""
    check("0zs live: map_addr reads nothing from the engine and casts nothing",
      #span > 0 and raw_find(span, "u:", 1, true) == nil
      and raw_find(span, "perform_special_ability", 1, true) == nil
      and raw_find(span, "string.find", 1, true) == nil)
  end

  local n_ok, n_all = 0, 0
  local function done(ok) n_all = n_all + 1; if ok then n_ok = n_ok + 1 end end
  local function lines_with(W, tok)
    local r = {}
    for _, l in ipairs(W.log_lines or {}) do if raw_find(l, tok, 1, true) ~= nil then r[#r + 1] = l end end
    return r
  end
  for _, f in ipairs({ { path = A146, tag = "[annotated] " }, { path = L146, tag = "[live] " } }) do
    local TAG = f.tag
    local units = {
      { name = SW, uid = 16800, owns = {}, melee = false, pos = { 10, 0, 20 }, width = 29.4, initial_men = 120 },
    }
    local enemies = {
      { name = ORC, uid = 16805, melee = true, pos = { 40, 0, 32 }, width = 30.2, initial_men = 120 },
    }
    local W = make_world({ can_perform = true, units = units, enemies = enemies,
      cards = { { id = "16800", state = "active", vis = true } }, bar = {} })
    print("== " .. TAG .. "A1. one of ours, one enemy, 24 polls ==")
    local ok = pcall(load_world, W, f.path)
    check(TAG .. "A1: the file loads", ok)
    if ok then
      deploy_phases(W); ui(W)
      W.conflict = true
      polln(W, 24)
      local maps = lines_with(W, "MAP t=")
      local with_addr = lines_with(W, " addr=")
      local a
      if RED146 then
        if TAG == "[live] " then a = (#maps >= 2 and #with_addr == 0) else a = (#maps == 0) end
        check(TAG .. "A1-RED: the pre-147 build logs MAP rows without an addr field (" .. #maps .. " rows, "
          .. #with_addr .. " with addr)", a)
        done(a)
      elseif TAG == "[live] " then
        local clean = (#maps >= 2 and #with_addr == #maps)
        for _, l in ipairs(maps) do
          local v = l:match(" addr=(%S*)$")
          if v == nil or v == "" then clean = false end
        end
        check(TAG .. "A1a: every MAP row (" .. #maps .. ") ends with a one-word addr field", clean)
        done(clean)
        local r = lines_with(W, " id=16805 ")[1] or ""
        a = (r:match(" routing=0 addr=table:_0?x?%x+$") ~= nil) or (r:match(" routing=0 addr=table:_%x+$") ~= nil)
        check(TAG .. "A1b: the enemy row's addr is the handle's tostring with the space as _ (" .. r .. ")", a)
        done(a)
        a = (#W.fires == 0 and #(W.ground_fires or {}) == 0 and #lines_with(W, "POLL ERROR") == 0)
        check(TAG .. "A1c: nothing was cast and no poll error", a)
        done(a)
        -- A2: the enemy handle's tostring is made hostile (raises), then
        -- engine-like ("userdata: <hex>"); the live mod is polled on each
        local eu = nil
        for i = 1, #(W.enemy_entries or {}) do
          local pr = W.enemy_entries[i]
          if pr ~= nil and pr.unit ~= nil and pr.unit.zz_uid == 16805 then eu = pr.unit end
        end
        local mt = { __tostring = function() error("boom") end }
        if eu ~= nil and getmetatable(eu) == nil then setmetatable(eu, mt) end
        local n0 = #(W.log_lines or {})
        polln(W, 8)
        local r2 = nil
        for i = n0 + 1, #(W.log_lines or {}) do
          local l = W.log_lines[i]
          if raw_find(l, " id=16805 ", 1, true) ~= nil then r2 = l end
        end
        mt.__tostring = function() return "userdata: 000001A2B3C4D5E6" end
        local n1 = #(W.log_lines or {})
        polln(W, 8)
        local r3 = nil
        for i = n1 + 1, #(W.log_lines or {}) do
          local l = W.log_lines[i]
          if raw_find(l, " id=16805 ", 1, true) ~= nil then r3 = l end
        end
        a = (eu ~= nil and r2 ~= nil and r2:match(" addr=%?$") ~= nil
          and r3 ~= nil and r3:match(" addr=userdata:_000001A2B3C4D5E6$") ~= nil
          and #lines_with(W, "POLL ERROR") == 0 and #W.fires == 0)
        check(TAG .. "A2: a raising tostring logs addr=? with no poll error; an engine-like one keeps its address ("
          .. tostring(r2 and r2:match("addr=%S*$")) .. " | " .. tostring(r3 and r3:match("addr=%S*$")) .. ")", a)
        done(a)
      else
        a = (#maps == 0 and #lines_with(W, "POLL ERROR") == 0 and #W.fires == 0)
        check(TAG .. "A1: the log-free reading copy runs the probe without a poll error and casts nothing", a)
        done(a)
      end
      tally(W)
    end
  end
  if RED146 then
    check("RED CONTROL (harness 146): the pre-147 build has no addr field - " .. n_ok .. "/" .. n_all,
      n_all == 2 and n_ok == 2)
  else
    check("HARNESS 146: every address world behaved - " .. n_ok .. "/" .. n_all, n_all == 5 and n_ok == 5)
  end
  print("== HARNESS 146 done: " .. (checks - pre146) .. " checks in this section ==")
end
