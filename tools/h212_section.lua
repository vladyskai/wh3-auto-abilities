-- ============================================================================
-- HARNESS 212 (round 214, tuning: the timing probe of the test build, live copy only. No cast decision changes).
--   0zz60 the round-214 tokens in the live file.
--   PF1 a world with the probe on (W.perf_on): 45 UI ticks and 8 polls -> exactly TWO "PERF 1s:" lines, the first
--       names 20 ticks and a poll count, and the hero still casts.
--   PF2 the same world with the probe off (the default of every older world) -> no PERF line, the same casts.
--   PF3 the probe on, but os.clock is missing -> no PERF line, no error, the same casts.
--   RED control: H212_LIVE on docs/backups/round214/pre214_live.lua (no PERF line anywhere).
-- ============================================================================
function run_h212()
  local L212 = os.getenv("H212_LIVE") or LIVE
  local RED212 = (os.getenv("H212_LIVE") ~= nil)
  local EW = "wh3_dlc25_unit_abilities_whirlwind_of_death_ror"
  local CASTER = "wh2_dlc13_emp_cha_huntsmen_general_0"
  local pre212 = checks
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1; at = i + #tok
    end
  end
  print("== HARNESS 212 - section 0zz60: the round-214 tokens ==")
  do
    local s = read_file(L212)
    local fns = cp(s, "\nfunction FOURTH.perf_now()\n") + cp(s, "\nfunction FOURTH.perf_add(name, t0)\n") + cp(s, "\nfunction FOURTH.perf_end_ui(t0)\n")
    local gate = cp(s, "\tif ZZ_AUTO_TEST_NO_PERF == true or zz_badge_set == nil then return nil end\n")
    local uses = cp(s, "FOURTH.perf_add(")
    if RED212 then
      check("0zz60 live (RED): the pre-214 file has no timing probe", fns == 0 and gate == 0)
    else
      check("0zz60 live: the three functions (" .. fns .. "), off outside the development build and in older worlds ("
        .. gate .. "), " .. uses .. " timed places", fns == 3 and gate == 1 and uses == 9)
    end
  end
  local n_ok, n_all = 0, 0
  local function done(ok) n_all = n_all + 1; if ok then n_ok = n_ok + 1 end end
  local function verdict(id, text, ok)
    check("[live] " .. id .. (RED212 and "-RED" or "") .. ": " .. text, ok)
    done(ok)
  end
  local function mk(wname, uid, perf_on, no_clock)
    local W = make_world({ can_perform = true, units = { { name = CASTER, uid = uid, owns = { EW }, melee = true, dist = 5,
      width = 2, men_alive = 1, unit_class = "com", hp_frac = 1.0 } }, enemies = {},
      cards = { { id = tostring(uid), state = "active", vis = true } }, bar = { { id = "b1", key = EW } } })
    W.defaults_on = true
    W.perf_on = perf_on
    print("== [live] " .. wname .. " ==")
    W.bm.get_player_alliance = function() return "OUR_ALLIANCE" end
    local ok = pcall(load_world, W, L212)
    check("[live] " .. wname .. ": the file loads", ok)
    if not ok then tally(W); return nil end
    local saved = os.clock
    if no_clock then os.clock = nil end
    deploy_phases(W)
    W.conflict = true
    for i = 1, 45 do
      ui(W)
      if i % 5 == 0 then polln(W, 1) end
    end
    os.clock = saved
    return W
  end
  local function casts(W)
    local n = 0
    for _, x in ipairs(W.fires) do if x.key == EW then n = n + 1 end end
    return n
  end
  local base = nil
  do
    local W = mk("PF2. the probe off (the default)", 21400, nil, false)
    if W ~= nil then
      base = casts(W)
      local lines = count_log(W, "PERF 1s:")
      verdict("PF2a", lines .. " PERF line(s) (need 0), " .. base .. " cast(s) (need at least 1)", lines == 0 and base >= 1)
      tally(W)
    else
      done(false)
    end
  end
  do
    local W = mk("PF1. the probe on: 45 UI ticks and 9 polls", 21410, true, false)
    if W ~= nil then
      local lines, shape = count_log(W, "PERF 1s:"), count_log(W, "PERF 1s: ui 20 ticks ")
      local polls = count_log(W, "| poll 4x ") + count_log(W, "| poll 5x ") + count_log(W, "| poll 3x ")
      local good = (lines == 2 and shape == 2 and polls >= 1 and casts(W) == base)
      if RED212 then good = (lines == 0 and casts(W) == base) end
      verdict("PF1a", lines .. " PERF line(s) (" .. (RED212 and "RED: 0" or "need 2") .. "), " .. shape
        .. " naming 20 ticks, " .. polls .. " naming the polls, " .. casts(W) .. " cast(s) (the same as with the probe off: "
        .. tostring(base) .. ")", good)
      tally(W)
    else
      done(false)
    end
  end
  do
    local W = mk("PF3. the probe on, os.clock missing", 21420, true, true)
    if W ~= nil then
      local lines = count_log(W, "PERF 1s:")
      verdict("PF3a", lines .. " PERF line(s) (need 0), " .. casts(W) .. " cast(s) (need " .. tostring(base) .. ")",
        lines == 0 and casts(W) == base)
      tally(W)
    else
      done(false)
    end
  end
  check("HARNESS 212: every world behaved - " .. n_ok .. "/" .. n_all, n_ok == n_all)
  print("== HARNESS 212 done: " .. (checks - pre212) .. " checks in this section ==")
end
