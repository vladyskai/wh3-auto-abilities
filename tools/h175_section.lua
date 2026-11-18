-- ============================================================================
-- HARNESS 175 (round 176): MASTER OF MISTS STARTS ARMED (user, 2026-11-18: "Start it on A").
--   0zz24 the entry carries start_armed; 9 plain start_armed lines.
--   DM1 the family defaults ON (as in battle), NO click: one Handgunner ally shooting -> ground casts under it.
--   RED (pre-176 = round 175): DM1 casts nothing (it starts on M).
-- ============================================================================
function run_h175()
  local L175 = os.getenv("H175_LIVE") or LIVE
  local A175 = os.getenv("H175_ANN") or ANN
  local RED175 = (os.getenv("H175_LIVE") ~= nil) or (os.getenv("H175_ANN") ~= nil)
  local MM = "wh3_dlc27_character_abilities_master_of_mists"
  local pre175 = checks
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1; at = i + #tok
    end
  end
  print("== HARNESS 175 - section 0zz24: the round-176 tokens ==")
  if not RED175 then
    for _, f in ipairs({ { name = "live", path = L175 }, { name = "ann", path = A175 } }) do
      local s = read_file(f.path)
      check("0zz24 " .. f.name .. ": Master of Mists carries start_armed; 9 plain start_armed lines",
        cp(s, '\t\tally_range_real = 250,\n\t\tstart_armed = true,\n\t\tox = 0, oy = 0 },') >= 1
        and cp(s, "\t\tstart_armed = true,\n") == 9)
    end
  end
  local n_ok, n_all = 0, 0
  for _, f in ipairs({ { path = A175, tag = "[annotated] " }, { path = L175, tag = "[live] " } }) do
    local TAG = f.tag
    local b = 39500
    local units = {
      { name = "wh3_dlc27_hef_cha_sea_lord_aislinn", uid = b, owns = { MM }, melee = false, pos = { 0, 0, 0 }, width = 2,
        men_alive = 1, unit_class = "com" },
      { name = "wh_main_emp_inf_handgunners", uid = b + 1, owns = {}, melee = false, pos = { 40, 0, 50 }, width = 30,
        men_alive = 120, initial_men = 120, unit_class = "inf_mis", ammo_start = 100, ammo_seq = { 100, 99 },
        dist_by_target = { [b] = 20 } } }
    local cards = {}
    for _, d in ipairs(units) do cards[#cards + 1] = { id = tostring(d.uid), state = "active", vis = true } end
    local W = make_world({ can_perform = true, units = units, enemies = {}, cards = cards,
      bar = { { id = "b1", key = MM } } })
    W.defaults_on = true   -- the defaults as in battle; nobody clicks
    print("== " .. TAG .. "DM1. defaults ON, no click: a shooting Handgunner ally -> ground casts under it ==")
    W.bm.get_player_alliance = function() return "OUR_ALLIANCE" end
    local ok = pcall(load_world, W, f.path)
    check(TAG .. "DM1: the file loads", ok)
    if ok then
      deploy_phases(W); ui(W)
      W.conflict = true
      polln(W, 60)
      local got, at_x = 0, 0
      for _, x in ipairs(W.ground_fires or {}) do
        if x.key == MM then
          got = got + 1
          local gx = nil
          pcall(function() gx = x.pos:get_x() end)
          if gx == 40 then at_x = at_x + 1 end
        end
      end
      local a
      if RED175 then a = (got == 0) else a = (got >= 1 and at_x == got) end
      check(TAG .. "DM1" .. (RED175 and "-RED" or "") .. "a: got " .. got .. " cast(s), " .. at_x .. " at x 40", a)
      n_all = n_all + 1
      if a then n_ok = n_ok + 1 end
    end
    tally(W)
  end
  if RED175 then
    check("RED CONTROL (harness 175): the pre-176 build starts Master of Mists on M - " .. n_ok .. "/" .. n_all,
      n_all == 2 and n_ok == 2)
  else
    check("HARNESS 175: every check behaved - " .. n_ok .. "/" .. n_all, n_all == 2 and n_ok == 2)
  end
  print("== HARNESS 175 done: " .. (checks - pre175) .. " checks in this section ==")
end
