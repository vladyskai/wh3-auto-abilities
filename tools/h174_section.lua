-- ============================================================================
-- HARNESS 174 (round 175): MASTER OF MISTS, 'A: before range, else shooting' (user ruling 2026-11-18).
--   0zz23 the shooting arm, its re-check, the 35 m area at the 70% rule, the card.
--   MM1 one Handgunner ally shooting, no enemy anywhere -> ground casts under it (x = 40).
--   MM2 three shooting allies: A alone (the closest), B and C 10 m apart -> ground casts under B (the group; B is the
--       closer of the two).
--   MM3 a Handgunner ally with ammunition that never shoots -> no cast.
--   RED (pre-175 = round 174): MM1 and MM2 cast nothing (no enemy just out of range).
-- ============================================================================
function run_h174()
  local L174 = os.getenv("H174_LIVE") or LIVE
  local A174 = os.getenv("H174_ANN") or ANN
  local RED174 = (os.getenv("H174_LIVE") ~= nil) or (os.getenv("H174_ANN") ~= nil)
  local MM = "wh3_dlc27_character_abilities_master_of_mists"
  local CASTER = "wh3_dlc27_hef_cha_sea_lord_aislinn"
  local GUNS = "wh_main_emp_inf_handgunners"
  local pre174 = checks
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1; at = i + #tok
    end
  end

  print("== HARNESS 174 - section 0zz23: the round-175 tokens ==")
  if not RED174 then
    for _, f in ipairs({ { name = "live", path = L174 }, { name = "ann", path = A174 } }) do
      local s = read_file(f.path)
      check("0zz23 " .. f.name .. ": the shooting arm, its re-check, the 70% area, the card",
        cp(s, "function FOURTH.mist_shooting(unit)") == 1
        and cp(s, 'if FOURTH.ah_mode == "mist_shoot" then') == 1
        and cp(s, "FOURTH.MIST_AREA_M = math.floor(FOURTH.MIST_AREA_REAL_M * 0.70)") == 1
        and cp(s, 'ground_ally_before_range = "Fires under missile allies just before their enemy is in range, else while they shoot",') == 1)
    end
  end

  local FILES = { { path = A174, tag = "[annotated] " }, { path = L174, tag = "[live] " } }
  local n_ok, n_all = 0, 0
  local function done(ok) n_all = n_all + 1; if ok then n_ok = n_ok + 1 end end
  local function world(wname, units, PATH, TAG)
    local cards = {}
    for _, d in ipairs(units) do cards[#cards + 1] = { id = tostring(d.uid), state = "active", vis = true } end
    local W = make_world({ can_perform = true, units = units, enemies = {}, cards = cards,
      bar = { { id = "b1", key = MM } } })
    W.defaults_on = false
    print("== " .. TAG .. wname .. " ==")
    W.bm.get_player_alliance = function() return "OUR_ALLIANCE" end
    local ok = pcall(load_world, W, PATH)
    check(TAG .. wname .. ": the file loads", ok)
    if not ok then tally(W); return nil end
    deploy_phases(W); ui(W)
    sel_event(W, units[1].uid, true); ui(W); ui(W)
    click(W, "zz_auto_badge_master_of_mists"); ui(W)
    sel_event(W, units[1].uid, false); ui(W)
    W.conflict = true
    polln(W, 60)
    return W
  end
  local function caster(b)
    return { name = CASTER, uid = b, owns = { MM }, melee = false, pos = { 0, 0, 0 }, width = 2, men_alive = 1,
             unit_class = "com" }
  end
  local function guns(uid, x, dists, shooting)
    return { name = GUNS, uid = uid, owns = {}, melee = false, pos = { x, 0, 50 }, width = 30, men_alive = 120,
             initial_men = 120, unit_class = "inf_mis", ammo_start = 100,
             ammo_seq = shooting and { 100, 99 } or { 100 }, dist_by_target = dists }
  end
  -- name; builder(b) -> units; GREEN: -1 = at least one cast, all at ground x; 0 = none; ground x; RED casts
  local WORLDS = {
    { "MM1. one Handgunner ally shooting, no enemy just out of range -> ground casts under it",
      function(b) return { caster(b), guns(b + 1, 40, { [b] = 20 }, true) } end, -1, 40, 0 },
    { "MM2. three shooting allies: A alone (closest), B and C 10 m apart -> ground casts under B",
      function(b) return { caster(b),
        guns(b + 1, -80, { [b] = 10, [b + 2] = 80, [b + 3] = 80 }, true),
        guns(b + 2, 40, { [b] = 20, [b + 1] = 80, [b + 3] = 10 }, true),
        guns(b + 3, 50, { [b] = 30, [b + 1] = 80, [b + 2] = 10 }, true) } end, -1, 40, 0 },
    { "MM3. a Handgunner ally that never shoots -> no cast",
      function(b) return { caster(b), guns(b + 1, 40, { [b] = 20 }, false) } end, 0, nil, 0 },
  }
  for _, f in ipairs(FILES) do
    local TAG = f.tag
    for i, w in ipairs(WORLDS) do
      local b = 39000 + i * 20
      local W = world(w[1], w[2](b), f.path, TAG)
      if W ~= nil then
        local got, at_x = 0, 0
        for _, x in ipairs(W.fires) do if x.key == MM then got = got + 1 end end
        for _, x in ipairs(W.ground_fires or {}) do
          if x.key == MM then
            got = got + 1
            local gx = nil
            pcall(function() gx = x.pos:get_x() end)
            if gx == w[4] then at_x = at_x + 1 end
          end
        end
        local a
        if RED174 then
          a = (got == w[5])
        elseif w[3] == -1 then
          a = (got >= 1 and at_x == got)
        else
          a = (got == 0)
        end
        check(TAG .. w[1]:sub(1, 3) .. (RED174 and "-RED" or "") .. "a: got " .. got .. " cast(s), " .. at_x
          .. " at x " .. tostring(w[4]), a)
        done(a)
        tally(W)
      end
    end
  end
  if RED174 then
    check("RED CONTROL (harness 174): the pre-175 build never casts on shooting alone - " .. n_ok .. "/" .. n_all,
      n_all == 6 and n_ok == 6)
  else
    check("HARNESS 174: every check behaved - " .. n_ok .. "/" .. n_all, n_all == 6 and n_ok == 6)
  end
  print("== HARNESS 174 done: " .. (checks - pre174) .. " checks in this section ==")
end
