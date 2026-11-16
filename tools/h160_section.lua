-- ============================================================================
-- HARNESS 160 (round 161): the 14 ally melee buffs start ARMED (user ruling 2026-11-16, "Whole family").
--   FF1 Favour of the Fay, NO badge click, the caster and an ally 20 m away in melee -> ONE cast (armed by default).
--   FF2 Favour of the Fay, ONE badge click (the explicit switch-off) -> no cast.
--   HH1 Helping Hand, NO badge click, the same world -> ONE cast.
--   RED (pre-161 = round 160): FF1 and HH1 cast nothing (the family started unarmed).
-- ============================================================================
function run_h160()
  local L160 = os.getenv("H160_LIVE") or LIVE
  local A160 = os.getenv("H160_ANN") or ANN
  local RED160 = (os.getenv("H160_LIVE") ~= nil) or (os.getenv("H160_ANN") ~= nil)
  local FAY = "wh_dlc07_lord_abilities_favour_of_the_fay"
  local HH = "wh2_pro08_character_abilities_helping_hand"
  local CASTER = "wh_dlc07_brt_cha_prophetess_life_0"
  local SW = "wh_main_emp_inf_swordsmen"
  local pre160 = checks

  print("== HARNESS 160 - section 0zz8: the round-161 token ==")
  if not RED160 then
    for _, f in ipairs({ { name = "live", path = L160 }, { name = "ann", path = A160 } }) do
      local s = read_file(f.path)
      local blk = s:match("FOURTH%.DEFAULT_ON_TRIGGERS = (%b{})")
      check("0zz8 " .. f.name .. ": ally_melee_buff starts armed",
        blk ~= nil and raw_find(blk, "\tally_melee_buff = true,", 1, true) ~= nil)
    end
  end

  local FILES = { { path = A160, tag = "[annotated] " }, { path = L160, tag = "[live] " } }
  local n_ok, n_all = 0, 0
  local function done(ok) n_all = n_all + 1; if ok then n_ok = n_ok + 1 end end
  local function world(wname, key, marker, clicks, PATH, TAG, b)
    local units = {
      { name = CASTER, uid = b, owns = { key }, melee = true, dist = 2, pos = { 0, 0, 0 }, width = 2, men_alive = 1,
        unit_class = "com" },
      { name = SW, uid = b + 1, owns = {}, melee = true, dist = 20, pos = { 0, 0, 20 }, width = 29.4, men_alive = 120,
        initial_men = 120, unit_class = "inf_mel" } }
    local cards = { { id = tostring(b), state = "active", vis = true }, { id = tostring(b + 1), state = "active", vis = true } }
    local W = make_world({ can_perform = true, units = units, enemies = {}, cards = cards,
      bar = { { id = "b1", key = key } } })
    W.defaults_on = true
    print("== " .. TAG .. wname .. " ==")
    W.bm.get_player_alliance = function() return "OUR_ALLIANCE" end
    local ok = pcall(load_world, W, PATH)
    check(TAG .. wname .. ": the file loads", ok)
    if not ok then tally(W); return nil end
    deploy_phases(W); ui(W)
    sel_event(W, b, true); ui(W); ui(W)
    for _ = 1, clicks do click(W, "zz_auto_badge_" .. marker); ui(W) end
    sel_event(W, b, false); ui(W)
    W.conflict = true
    polln(W, 4)
    return W
  end
  -- name, key, marker, clicks, GREEN casts, RED casts (nil = not RED)
  local WORLDS = {
    { "FF1. Favour of the Fay, no badge click, in melee with an ally -> ONE cast", FAY, "favour_of_the_fay", 0, 1, 0 },
    { "FF2. Favour of the Fay, one badge click (switched off) -> no cast", FAY, "favour_of_the_fay", 1, 0, nil },
    { "HH1. Helping Hand, no badge click, in melee with an ally -> ONE cast", HH, "helping_hand", 0, 1, 0 },
  }
  for _, f in ipairs(FILES) do
    local TAG = f.tag
    for i, w in ipairs(WORLDS) do
      local want = w[5]
      if RED160 then want = w[6] end
      if want ~= nil then
        local W = world(w[1], w[2], w[3], w[4], f.path, TAG, 24000 + i * 20)
        if W ~= nil then
          local got = 0
          for _, x in ipairs(W.fires) do if x.key == w[2] then got = got + 1 end end
          for _, x in ipairs(W.ground_fires or {}) do if x.key == w[2] then got = got + 1 end end
          local a = (got == want)
          check(TAG .. w[1]:sub(1, 3) .. (RED160 and "-RED" or "") .. "a: " .. want .. " cast(s) expected, got " .. got, a)
          done(a)
          tally(W)
        end
      end
    end
  end
  if RED160 then
    check("RED CONTROL (harness 160): the pre-161 build starts the ally melee buffs unarmed - " .. n_ok .. "/" .. n_all,
      n_all == 4 and n_ok == 4)
  else
    check("HARNESS 160: every world behaved - " .. n_ok .. "/" .. n_all, n_all == 6 and n_ok == 6)
  end
  print("== HARNESS 160 done: " .. (checks - pre160) .. " checks in this section ==")
end
