
-- ============================================================================
-- HARNESS 148 (round 149): THE REVERT (user ruling 2026-11-14: "we close this
-- project and reverse everything"; "Yes, revert"). The source and the reading
-- copy are byte-identical to round 146; the address field (round 147) and the
-- memreader probe (round 148) are gone, and a memreader present in the game
-- changes nothing.
-- RED: H148_LIVE / H148_ANN = the pre-149 snapshot (with both probes).
-- ============================================================================
function run_h148()
  local pre148 = checks
  local L148 = os.getenv("H148_LIVE") or LIVE
  local A148 = os.getenv("H148_ANN") or ANN
  local RED148 = (os.getenv("H148_LIVE") ~= nil) or (os.getenv("H148_ANN") ~= nil)
  local B146_LIVE = "C:/Users/vlady/Desktop/WH3_mod/docs/backups/round147/pre147_zz_test_deadly_onslaught.lua"
  local B146_ANN = "C:/Users/vlady/Desktop/WH3_mod/docs/backups/round147/pre147_WH3_auto_ability_annotated.lua"
  local SW = "wh_main_emp_inf_swordsmen"
  local ORC = "wh_main_grn_inf_orc_boyz"
  print("== HARNESS 148 - section 0zu: the round-149 revert ==")
  local n_ok, n_all = 0, 0
  local function done(ok) n_all = n_all + 1; if ok then n_ok = n_ok + 1 end end
  for _, f in ipairs({ { name = "live", path = L148, base = B146_LIVE }, { name = "ann", path = A148, base = B146_ANN } }) do
    local s = read_file(f.path)
    local a = (s == read_file(f.base))
    if RED148 then
      check("0zu-RED " .. f.name .. ": the pre-149 file differs from round 146", not a)
      done(not a)
    else
      check("0zu " .. f.name .. ": byte-identical to the round-146 file (" .. #s .. " bytes)", a)
      done(a)
      a = (raw_find(s, "map_addr", 1, true) == nil and raw_find(s, "mr_unit", 1, true) == nil
        and raw_find(s, "memreader", 1, true) == nil and raw_find(s, "MEMREADER", 1, true) == nil)
      check("0zu " .. f.name .. ": no address field and no memreader code", a)
      done(a)
    end
  end
  local function lines_with(W, tok)
    local r = {}
    for _, l in ipairs(W.log_lines or {}) do if raw_find(l, tok, 1, true) ~= nil then r[#r + 1] = l end end
    return r
  end
  -- a memreader mock that counts every call: the reverted mod must never touch it
  local touched = 0
  local mock = setmetatable({}, { __index = function() return function() touched = touched + 1 end end })
  _G.memreader_plus = mock
  local units = { { name = SW, uid = 18800, owns = {}, melee = true, pos = { 10, 0, 20 }, width = 29.4, initial_men = 120 } }
  local enemies = { { name = ORC, uid = 18805, melee = true, pos = { 12, 0, 24 }, width = 30.2, initial_men = 120 } }
  local W = make_world({ can_perform = true, units = units, enemies = enemies,
    cards = { { id = "18800", state = "active", vis = true } }, bar = {} })
  print("== [live] R1. a battle with memreader Plus present ==")
  local ok = pcall(load_world, W, L148)
  check("[live] R1: the file loads", ok)
  if ok then
    deploy_phases(W); ui(W)
    W.conflict = true
    polln(W, 24)
    local maps = lines_with(W, "MAP t=")
    local clean = (#maps >= 4)
    for _, l in ipairs(maps) do
      if l:match(" routing=%S+$") == nil then clean = false end
    end
    if RED148 then
      local a = (#lines_with(W, " addr=") > 0 and #lines_with(W, " mr_lead=") > 0)
      check("[live] R1-RED: the pre-149 build logs addr= and mr_ fields", a)
      done(a)
    else
      local a = (clean and #lines_with(W, " addr=") == 0 and #lines_with(W, "mr_") == 0
        and #lines_with(W, "MEMREADER") == 0 and touched == 0)
      check("[live] R1a: every MAP row ends at routing= again (" .. #maps .. " rows), no addr / mr_ / MEMREADER, memreader untouched ("
        .. touched .. ")", a)
      done(a)
      a = (#lines_with(W, "POLL ERROR") == 0)
      check("[live] R1b: no poll error", a)
      done(a)
    end
    tally(W)
  end
  _G.memreader_plus = nil
  if RED148 then
    check("RED CONTROL (harness 148): the pre-149 build still carries both probes - " .. n_ok .. "/" .. n_all,
      n_all == 3 and n_ok == 3)
  else
    check("HARNESS 148: the revert is complete - " .. n_ok .. "/" .. n_all, n_all == 6 and n_ok == 6)
  end
  print("== HARNESS 148 done: " .. (checks - pre148) .. " checks in this section ==")
end
