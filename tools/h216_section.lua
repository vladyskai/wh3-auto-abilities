-- ============================================================================
-- HARNESS 216 (round 218, tuning, LIVE COPY ONLY: the timing probe measures the test build's own log).
--   0zz64 the round-218 tokens in the live copy.
--   LG1 a world with the probe on (W.perf_on): 45 UI ticks and 9 polls -> two PERF lines, each ending with the log
--       part (' | log ', ' lines (in polls ', ' | probe ', '(its log '), the line count above 0, the same casts as
--       with the probe off. RED: the PERF lines have no log part.
--   LG2 the probe off: no PERF line, and the log does not time itself (cast_gate.log_on is never set).
--   RED control: H216_LIVE on docs/backups/round218/pre218_live.lua.
-- ============================================================================
function run_h216()
  local L216 = os.getenv("H216_LIVE") or LIVE
  local RED216 = (os.getenv("H216_LIVE") ~= nil)
  local EW = "wh3_dlc25_unit_abilities_whirlwind_of_death_ror"
  local CASTER = "wh2_dlc13_emp_cha_huntsmen_general_0"
  local pre216 = checks
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1; at = i + #tok
    end
  end
  print("== HARNESS 216 - section 0zz64: the round-218 tokens ==")
  do
    local s = read_file(L216)
    local got = cp(s, "\tif cast_gate.log_on == true then log_t0 = os.clock() end\n")
      + cp(s, "\tcast_gate.log_on = true   -- ROUND 218\n")
      + cp(s, " | log %.1f ms %d lines (in polls %.1f) | probe %.1f ms (its log %.1f)")
      + cp(s, "\tFOURTH.perf_probe0 = FOURTH.perf_now()")
    if RED216 then
      check("0zz64 live (RED): the pre-218 file does not time its log", got == 0)
    else
      check("0zz64 live: the log times itself only while the probe is on, the PERF line carries it (" .. got .. " of 4)", got == 4)
    end
  end
  local n_ok, n_all = 0, 0
  local function done(ok) n_all = n_all + 1; if ok then n_ok = n_ok + 1 end end
  local function verdict(id, text, ok)
    check("[live] " .. id .. (RED216 and "-RED" or "") .. ": " .. text, ok)
    done(ok)
  end
  local function mk(wname, uid, perf_on)
    local W = make_world({ can_perform = true, units = { { name = CASTER, uid = uid, owns = { EW }, melee = true, dist = 5,
      width = 2, men_alive = 1, unit_class = "com", hp_frac = 1.0 } }, enemies = {},
      cards = { { id = tostring(uid), state = "active", vis = true } }, bar = { { id = "b1", key = EW } } })
    W.defaults_on = true
    W.perf_on = perf_on
    print("== [live] " .. wname .. " ==")
    W.bm.get_player_alliance = function() return "OUR_ALLIANCE" end
    local ok = pcall(load_world, W, L216)
    check("[live] " .. wname .. ": the file loads", ok)
    if not ok then tally(W); return nil end
    deploy_phases(W)
    W.conflict = true
    for i = 1, 45 do
      ui(W)
      if i % 5 == 0 then polln(W, 1) end
    end
    return W
  end
  local function casts(W)
    local n = 0
    for _, x in ipairs(W.fires) do if x.key == EW then n = n + 1 end end
    return n
  end
  local base = nil
  do
    local W = mk("LG2. the probe off (the default)", 21800, nil)
    if W ~= nil then
      base = casts(W)
      local lines = count_log(W, "PERF 1s:")
      verdict("LG2a", lines .. " PERF line(s) (need 0), " .. base .. " cast(s) (need at least 1)", lines == 0 and base >= 1)
      tally(W)
    else
      done(false)
    end
  end
  do
    local W = mk("LG1. the probe on: the PERF line carries the log's own cost", 21810, true)
    if W ~= nil then
      local lines = count_log(W, "PERF 1s:")
      local parts = count_log(W, " | log ") + count_log(W, " lines (in polls ") + count_log(W, " | probe ") + count_log(W, "(its log ")
      local zero = count_log(W, " ms 0 lines (in polls ")
      local good = (lines == 2 and parts == 8 and zero == 0 and casts(W) == base)
      if RED216 then good = (lines == 2 and parts == 0 and casts(W) == base) end
      verdict("LG1a", lines .. " PERF line(s) (need 2), " .. parts .. " log parts (" .. (RED216 and "RED: 0" or "need 8")
        .. "), " .. zero .. " line(s) counting 0 log lines (need 0), " .. casts(W) .. " cast(s) (the same as with the probe off: "
        .. tostring(base) .. ")", good)
      tally(W)
    else
      done(false)
    end
  end
  check("HARNESS 216: every world behaved - " .. n_ok .. "/" .. n_all, n_ok == n_all)
  print("== HARNESS 216 done: " .. (checks - pre216) .. " checks in this section ==")
end
