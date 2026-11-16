-- ============================================================================
-- HARNESS 161 (round 162): THE WANDERING WINDS (user rulings 2026-11-16).
--   WV1 Wrath of Manann (6 m wave, 70 m path, 95% drift 17 m): Grave Guard (800) standing 60 m ahead, Zombies (75)
--       off to the side -> ONE cast at the Grave Guard (the most value on the path).
--   WV2 Wrath of Manann: our Swordsmen 25 m beside the far half of the path (inside 6 + 10 + 17 x 0.9) -> no cast.
--   WV5 Seafang (straight, drift 0): the same Swordsmen (outside 4 + 10) -> ONE cast (a low-drift wave needs less room).
--   WV3 Wrath of Manann: the Grave Guard is moving -> no cast.
--   WV4 Wrath of Manann: the caster is moving -> no cast.
--   WN1 Banishment (12 m, 95% reach 16 m): a 200-man Grave Guard block, ours 55 m away -> ONE cast at it.
--   WN2 Banishment: ours 25 m from the target (inside 12 + 16 + 10) -> no cast.
--   WN3 Heaven's Gate (cannot hurt our units, ground-only): our Swordsmen fighting the block -> ONE ground cast.
--   WN4 The Dwellers Below (20 m static): ours 20 m from the target (inside 20 + 10) -> no cast.
--   RED (pre-162 = round 161): WV1, WV5, WN1, WN3 cast nothing.
-- ============================================================================
function run_h161()
  local L161 = os.getenv("H161_LIVE") or LIVE
  local A161 = os.getenv("H161_ANN") or ANN
  local RED161 = (os.getenv("H161_LIVE") ~= nil) or (os.getenv("H161_ANN") ~= nil)
  local WM = "wh_dlc07_item_abilities_wrath_of_manann"
  local SF = "wh_dlc08_lord_abilities_seafang"
  local BN = "wh3_main_spell_bound_banishment"
  local HG = "wh3_cp1_item_abilities_heavens_gate"
  local DB = "wh3_main_spell_bound_the_dwellers_below"
  local CASTER = "wh_dlc07_brt_cha_prophetess_life_0"
  local GG = "wh_main_vmp_inf_grave_guard_0"
  local ZB = "wh_main_vmp_inf_zombie"
  local SW = "wh_main_emp_inf_swordsmen"
  local pre161 = checks
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1; at = i + #tok
    end
  end

  print("== HARNESS 161 - section 0zz9: the round-162 tokens ==")
  if not RED161 then
    for _, f in ipairs({ { name = "live", path = L161 }, { name = "ann", path = A161 } }) do
      local s = read_file(f.path)
      check("0zz9 " .. f.name .. ": 892 entries, 12 waves, 20 wanderers, both wired, the WW table, the ww re-check",
        cp(s, "\t{ marker = ") == 892
        and cp(s, 'trigger = "enemy_wave"') == 12 and cp(s, 'trigger = "enemy_wander"') == 20
        and raw_find(s, "enemy_wave = FOURTH.evaluate_enemy_wave,", 1, true) ~= nil
        and raw_find(s, "enemy_wander = FOURTH.evaluate_enemy_wander,", 1, true) ~= nil
        and raw_find(s, "wh_dlc07_item_abilities_wrath_of_manann=1,6,70,24,17,1,0;", 1, true) ~= nil
        and raw_find(s, 'elseif eg_mode_now == "ww" then', 1, true) ~= nil)
    end
  end

  local FILES = { { path = A161, tag = "[annotated] " }, { path = L161, tag = "[live] " } }
  local n_ok, n_all = 0, 0
  local function done(ok) n_all = n_all + 1; if ok then n_ok = n_ok + 1 end end
  local function world(wname, units, enemies, marker, key, PATH, TAG, sv)
    local cards = {}
    for _, d in ipairs(units) do cards[#cards + 1] = { id = tostring(d.uid), state = "active", vis = true } end
    local W = make_world({ can_perform = true, units = units, enemies = enemies, cards = cards,
      bar = { { id = "b1", key = key } } })
    W.defaults_on = false
    print("== " .. TAG .. wname .. " ==")
    W.bm.get_player_alliance = function() return "OUR_ALLIANCE" end
    local ok = pcall(load_world, W, PATH)
    check(TAG .. wname .. ": the file loads", ok)
    if not ok then tally(W); return nil end
    deploy_phases(W); ui(W)
    for i = 1, #(W.enemy_entries or {}) do
      local pr = W.enemy_entries[i]
      if pr ~= nil and pr.unit ~= nil then
        local id = nil
        pcall(function() id = tostring(pr.unit:unique_ui_id()) end)
        pr.unit.is_visible_to_alliance = function(self, a) return true end
        pr.unit.is_currently_flying = function(self) return false end
        local v = sv[id]
        if v ~= nil then pr.unit.strategic_value = function(self) return v end end
      end
    end
    sel_event(W, units[1].uid, true); ui(W); ui(W)
    click(W, "zz_auto_badge_" .. marker); ui(W)
    sel_event(W, units[1].uid, false); ui(W)
    W.conflict = true
    polln(W, 4)
    return W
  end
  local function caster(b, key, o)
    local c = { name = CASTER, uid = b, owns = { key }, melee = false, dist = 40, pos = { 0, 0, 0 }, width = 2,
                men_alive = 1, unit_class = "com" }
    for k, v in pairs(o or {}) do c[k] = v end
    return c
  end
  local function block(uid, name, x, z, o)
    local e = { uid = uid, name = name, melee = false, pos = { x, 0, z }, width = 29.4, men_alive = 120,
                initial_men = 120, unit_class = "inf_mel", dist = 40 }
    for k, v in pairs(o or {}) do e[k] = v end
    return e
  end
  local function ours(uid, x, z, o)
    local u = { uid = uid, name = SW, owns = {}, melee = false, pos = { x, 0, z }, width = 29.4, men_alive = 120,
                initial_men = 120, unit_class = "inf_mel" }
    for k, v in pairs(o or {}) do u[k] = v end
    return u
  end
  local BIG = { men_alive = 200, initial_men = 200, width = 20, dist = 60 }
  -- name, builder(b) -> units, enemies, sv; marker; key; GREEN casts; RED casts (nil = not RED); target offset
  local WORLDS = {
    { "WV1. Wrath of Manann: Grave Guard (800) standing 60 m ahead, Zombies (75) aside -> ONE cast at the Grave Guard",
      function(b) return { caster(b, WM) }, { block(b + 5, GG, 0, 60), block(b + 6, ZB, -60, 40) },
        { [tostring(b + 5)] = 800, [tostring(b + 6)] = 75 } end, "wrath_of_manann", WM, 1, 0, 5 },
    { "WV2. Wrath of Manann: our Swordsmen 25 m beside the far half of the path -> no cast",
      function(b) return { caster(b, WM), ours(b + 1, 40, 80) }, { block(b + 5, GG, 0, 60) },
        { [tostring(b + 5)] = 800 } end, "wrath_of_manann", WM, 0, nil, nil },
    { "WV5. Seafang (straight, no drift): the same Swordsmen -> ONE cast at the Grave Guard",
      function(b) return { caster(b, SF), ours(b + 1, 40, 80) }, { block(b + 5, GG, 0, 60) },
        { [tostring(b + 5)] = 800 } end, "seafang", SF, 1, 0, 5 },
    { "WV3. Wrath of Manann: the Grave Guard is moving -> no cast",
      function(b) return { caster(b, WM) }, { block(b + 5, GG, 0, 60, { moving = true }) },
        { [tostring(b + 5)] = 800 } end, "wrath_of_manann", WM, 0, nil, nil },
    { "WV4. Wrath of Manann: the caster is moving -> no cast",
      function(b) return { caster(b, WM, { moving = true }) }, { block(b + 5, GG, 0, 60) },
        { [tostring(b + 5)] = 800 } end, "wrath_of_manann", WM, 0, nil, nil },
    { "WN1. Banishment: a 200-man Grave Guard block, ours 55 m away -> ONE cast at it",
      function(b) return { caster(b, BN, { dist = 60 }), ours(b + 1, 0, 140) }, { block(b + 5, GG, 0, 80, BIG) },
        { [tostring(b + 5)] = 1600 } end, "banishment", BN, 1, 0, 5 },
    { "WN2. Banishment: ours 25 m from the target -> no cast",
      function(b) return { caster(b, BN, { dist = 60 }), ours(b + 1, 0, 110) }, { block(b + 5, GG, 0, 80, BIG) },
        { [tostring(b + 5)] = 1600 } end, "banishment", BN, 0, nil, nil },
    { "WN3. Heaven's Gate (cannot hurt our units): our Swordsmen fighting the block -> ONE ground cast",
      function(b) return { caster(b, HG, { dist = 60 }), ours(b + 1, 0, 95, { melee = true }) },
        { block(b + 5, GG, 0, 80, { men_alive = 200, initial_men = 200, width = 20, dist = 60, melee = true }) },
        { [tostring(b + 5)] = 1600 } end, "heavens_gate", HG, 1, 0, nil },
    { "WN4. The Dwellers Below (20 m static): ours 20 m from the target -> no cast",
      function(b) return { caster(b, DB, { dist = 60 }), ours(b + 1, 0, 105) }, { block(b + 5, GG, 0, 80, BIG) },
        { [tostring(b + 5)] = 1600 } end, "dwellers_below", DB, 0, nil, nil },
  }
  for _, f in ipairs(FILES) do
    local TAG = f.tag
    for i, w in ipairs(WORLDS) do
      local want = w[5]
      if RED161 then want = w[6] end
      if want ~= nil then
        local b = 25000 + i * 20
        local units, enemies, sv = w[2](b)
        local W = world(w[1], units, enemies, w[3], w[4], f.path, TAG, sv)
        if W ~= nil then
          local got, tid = 0, nil
          for _, x in ipairs(W.fires) do
            if x.key == w[4] then
              got = got + 1
              if tid == nil then pcall(function() tid = tostring(x.target:unique_ui_id()) end) end
            end
          end
          for _, x in ipairs(W.ground_fires or {}) do
            if x.key == w[4] then got = got + 1 end
          end
          local a = (got == want)
          local ttxt = ""
          if want > 0 and not RED161 and w[7] ~= nil then
            a = a and tid == tostring(b + w[7])
            ttxt = ", target " .. tostring(tid) .. " want " .. tostring(b + w[7])
          end
          check(TAG .. w[1]:sub(1, 3) .. (RED161 and "-RED" or "") .. "a: " .. want .. " cast(s) expected, got " .. got
            .. ttxt, a)
          done(a)
          tally(W)
        end
      end
    end
  end
  if RED161 then
    check("RED CONTROL (harness 161): the pre-162 build has none of the wandering winds - " .. n_ok .. "/" .. n_all,
      n_all == 8 and n_ok == 8)
  else
    check("HARNESS 161: every world behaved - " .. n_ok .. "/" .. n_all, n_all == 18 and n_ok == 18)
  end
  print("== HARNESS 161 done: " .. (checks - pre161) .. " checks in this section ==")
end
