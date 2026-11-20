-- ============================================================================
-- HARNESS 183 (round 184): THE RULE-SHUT REVIEW, ROWS 10-19 (user 2026-11-20: "Up to #19 ruled"; rulings from the
--   Claude Docs review, rev 83).
--   0zz32 the 10 entries, the two new families wired, the 75% gate, the AREA rows, the holds and wind-ups.
--   FD1 Flock of Doom: a MOVING zombie block 50 m away -> ONE cast (the enemy need not stand still; RED: none).
--   SD1 Sword of Daith: a zombie block 50 m away -> ONE cast (RED: none).
--   ZN1 Zefet-nebtar: a zombie block 50 m away with our Swordsmen next to it -> ONE cast (no clearance; RED: none).
--   RC1 Ring of Corin: a hero 130 m away (inside 140 m) -> ONE cast on it (RED: none).
--   SS1 Soul Stealer: the caster at 60% health, a zombie block 50 m away -> ONE cast (RED: none).
--   SS2 Soul Stealer: the caster at 90% health -> no cast.
--   WS1 Warpstorm Scroll: a ground hero worth 900 and a FLYING hero worth 300 -> ONE cast at the flying one (RED: none).
--   RT1 Raging Tornado: a lone enemy in melee worth 900 and two in melee 8 m apart worth 500 each -> ONE ground cast
--       under one of the pair (RED: none).
--   RT2 Raging Tornado: no enemy in melee -> no cast.
--   CA12 the cards of Soul Stealer, Warpstorm Scroll and Raging Tornado.
--   RED control: H183_LIVE / H183_ANN on docs/backups/round184/pre184_*.lua.
-- ============================================================================
function run_h183()
  local L183 = os.getenv("H183_LIVE") or LIVE
  local A183 = os.getenv("H183_ANN") or ANN
  local RED183 = (os.getenv("H183_LIVE") ~= nil) or (os.getenv("H183_ANN") ~= nil)
  local K = {
    FD = "wh_dlc08_spell_bound_flock_of_doom", SD = "wh_dlc05_weapon_abilities_daiths_sword",
    ZN = "wh3_dlc29_item_abilities_zefet_nebtar_the_mortis_blade", RC = "wh2_main_spell_bound_ring_of_corin",
    SS = "wh2_dlc10_spell_bound_soul_stealer_ror", WS = "wh2_main_item_abilities_warpstorm_scroll",
    RT = "wh3_dlc29_unit_abilities_raging_tornado",
  }
  local CASTER = "wh2_dlc13_emp_cha_huntsmen_general_0"
  local HURR = "wh3_dlc29_emp_veh_celestial_hurricanum_0"
  local HERO = "wh2_dlc13_emp_cha_hunter_jorek_grimm_0"
  local SW = "wh_main_emp_inf_swordsmen"
  local ZOMBIE = "wh_main_vmp_inf_zombie"
  local pre183 = checks
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1; at = i + #tok
    end
  end
  print("== HARNESS 183 - section 0zz32: the round-184 entries ==")
  if not RED183 then
    local ENT = {
      { "flock_of_doom_runecaller", "enemy_area_drain" }, { "flock_of_doom_wh3", "enemy_area_drain" },
      { "flock_of_doom", "enemy_area_drain" }, { "sword_of_daith", "enemy_area_drain" },
      { "zefet_nebtar", "enemy_area_drain" }, { "ring_of_corin", "enemy_single_drain" },
      { "soul_stealer_ror", "enemy_area_drain_hurt" }, { "soul_stealer_anointed", "enemy_area_drain_hurt" },
      { "warpstorm_scroll", "enemy_single_drain" }, { "raging_tornado", "enemy_ground_melee_cluster" },
    }
    for _, f in ipairs({ { name = "live", path = L183 }, { name = "ann", path = A183 } }) do
      local s = read_file(f.path)
      local got = 0
      for _, e in ipairs(ENT) do
        local i = raw_find(s, '{ marker = "' .. e[1] .. '", name = "', 1, true)
        if i ~= nil and cp(s, '{ marker = "' .. e[1] .. '", ') == 1
          and raw_find(s:sub(i, i + 120), 'trigger = "' .. e[2] .. '",', 1, true) ~= nil then
          got = got + 1
        end
      end
      local wired = 0
      for _, fam in ipairs({ "enemy_area_drain_hurt", "enemy_ground_melee_cluster" }) do
        if cp(s, "\t" .. fam .. " = FOURTH.evaluate_" .. fam .. ",") == 1 then wired = wired + 1 end
      end
      check("0zz32 " .. f.name .. ": 10 entries on their families (" .. got .. "), 2 families wired (" .. wired
        .. "), the 75% gate, the flying class, the AREA rows, the holds and wind-ups",
        got == 10 and wired == 2 and cp(s, "\nFOURTH.DRAIN_HURT_PCT = 75") == 1
        and cp(s, "-- ROUND 184 (rule-shut review row ") == 10
        and cp(s, "wh2_main_item_abilities_warpstorm_scroll\" },\n\t\trange_real = 100,\n\t\ttarget_class = \"flying\",\n") == 1
        and cp(s, "wh2_dlc10_spell_bound_soul_stealer_ror=1;") == 1 and cp(s, "wh_dlc08_spell_bound_flock_of_doom=25\"") == 1
        and cp(s, '\t\t["wh3_dlc29_unit_abilities_raging_tornado"] = 120,\n') == 1
        and cp(s, '\t\t["wh3_dlc29_unit_abilities_raging_tornado"] = 5,\n') == 1)
    end
  end
  local FILES = { { path = A183, tag = "[annotated] " }, { path = L183, tag = "[live] " } }
  local n_ok, n_all = 0, 0
  local function done(ok) n_all = n_all + 1; if ok then n_ok = n_ok + 1 end end
  local function world(wname, units, enemies, marker, key, PATH, TAG, o)
    o = o or {}
    local cards = {}
    for _, d in ipairs(units) do cards[#cards + 1] = { id = tostring(d.uid), state = "active", vis = true } end
    local W = make_world({ can_perform = true, units = units, enemies = enemies or {}, cards = cards,
      bar = { { id = "b1", key = key } } })
    W.defaults_on = false
    print("== " .. TAG .. wname .. " ==")
    W.bm.get_player_alliance = function() return "OUR_ALLIANCE" end
    OH77.cap = nil
    local ok = pcall(load_world, W, PATH)
    check(TAG .. wname .. ": the file loads", ok)
    if not ok then tally(W); return nil end
    W.cap = OH77.cap
    deploy_phases(W); ui(W)
    for i = 1, #(W.enemy_entries or {}) do
      local pr = W.enemy_entries[i]
      if pr ~= nil and pr.unit ~= nil then
        local id = nil
        pcall(function() id = tostring(pr.unit:unique_ui_id()) end)
        local fly = (o.fly ~= nil and o.fly[id] == true)
        pr.unit.is_visible_to_alliance = function(self, a) return true end
        pr.unit.is_currently_flying = function(self) return fly end
        if o.sv ~= nil and o.sv[id] ~= nil then
          local v = o.sv[id]
          pr.unit.strategic_value = function(self) return v end
        end
      end
    end
    sel_event(W, units[1].uid, true); ui(W); ui(W)
    click(W, "zz_auto_badge_" .. marker); ui(W)
    sel_event(W, units[1].uid, false); ui(W)
    W.conflict = true
    polln(W, o.polls or 4)
    return W
  end
  local function own(name, b, key, o)
    local c = { name = name, uid = b, owns = { key }, melee = false, dist = 30, health_percent = 100, pos = { 0, 0, 0 },
                width = 10, unit_class = "com" }
    for k, v in pairs(o or {}) do c[k] = v end
    return c
  end
  local function block(uid, x, z, o)
    local e = { uid = uid, name = ZOMBIE, melee = false, pos = { x, 0, z }, width = 20, men_alive = 80, initial_men = 80,
                unit_class = "inf_mel", dist = 30 }
    for k, v in pairs(o or {}) do e[k] = v end
    return e
  end
  local function hero(uid, x, z, o)
    local e = { uid = uid, name = HERO, melee = false, pos = { x, 0, z }, width = 2, men_alive = 1, initial_men = 1,
                unit_class = "com", dist = 30 }
    for k, v in pairs(o or {}) do e[k] = v end
    return e
  end
  local function S(t) local r = {} for k, v in pairs(t) do r[tostring(k)] = v end return r end
  -- { name, builder, marker, key, casts expected, target suffix (unit cast) or ground pos suffix list }
  local WORLDS = {
    { "FD1. Flock of Doom: a MOVING zombie block 50 m away -> ONE cast",
      function(b) return { own(CASTER, b, K.FD, { dist_by_target = { [b + 5] = 50 } }) },
        { block(b + 5, 0, 50, { moving = true }) }, { sv = S({ [b + 5] = 400 }) } end, "flock_of_doom", K.FD, 1, "u5" },
    { "SD1. Sword of Daith: a zombie block 50 m away -> ONE cast",
      function(b) return { own(CASTER, b, K.SD, { dist_by_target = { [b + 5] = 50 } }) },
        { block(b + 5, 0, 50) }, { sv = S({ [b + 5] = 400 }) } end, "sword_of_daith", K.SD, 1, "u5" },
    { "ZN1. Zefet-nebtar: a zombie block 50 m away, our Swordsmen next to it -> ONE cast",
      function(b) return { own(CASTER, b, K.ZN, { dist_by_target = { [b + 5] = 50 } }),
        { name = SW, uid = b + 1, owns = {}, melee = true, dist = 30, health_percent = 100, pos = { 0, 0, 47 },
          width = 10, men_alive = 120, unit_class = "inf_mel" } },
        { block(b + 5, 0, 50, { melee = true }) }, { sv = S({ [b + 5] = 400 }) } end, "zefet_nebtar", K.ZN, 1, "u5" },
    { "RC1. Ring of Corin: a hero 130 m away -> ONE cast on it",
      function(b) return { own(CASTER, b, K.RC, { dist_by_target = { [b + 5] = 130 } }) },
        { hero(b + 5, 0, 130) }, { sv = S({ [b + 5] = 500 }) } end, "ring_of_corin", K.RC, 1, "u5" },
    { "SS1. Soul Stealer: the caster at 60% health -> ONE cast",
      function(b) return { own(CASTER, b, K.SS, { health_percent = 60, dist_by_target = { [b + 5] = 50 } }) },
        { block(b + 5, 0, 50) }, { sv = S({ [b + 5] = 400 }) } end, "soul_stealer_ror", K.SS, 1, "u5" },
    { "SS2. Soul Stealer: the caster at 90% health -> no cast",
      function(b) return { own(CASTER, b, K.SS, { health_percent = 90, dist_by_target = { [b + 5] = 50 } }) },
        { block(b + 5, 0, 50) }, { sv = S({ [b + 5] = 400 }) } end, "soul_stealer_ror", K.SS, 0, nil },
    { "WS1. Warpstorm Scroll: a ground hero worth 900, a FLYING hero worth 300 -> ONE cast at the flying one",
      function(b) return { own(CASTER, b, K.WS, { dist_by_target = { [b + 5] = 50, [b + 6] = 50 } }) },
        { hero(b + 5, 0, 50), hero(b + 6, 20, 50) },
        { sv = S({ [b + 5] = 900, [b + 6] = 300 }), fly = S({ [b + 6] = true }) } end, "warpstorm_scroll", K.WS, 1, "u6" },
    { "RT1. Raging Tornado: a lone melee worth 900, a pair 8 m apart worth 500 each -> ONE ground cast under the pair",
      function(b) return { own(HURR, b, K.RT, { unit_class = "art_fix", dist_by_target = { [b + 5] = 60, [b + 6] = 40, [b + 7] = 40 } }) },
        { block(b + 5, 60, 30, { melee = true, dist_by_target = { [b + 6] = 40, [b + 7] = 40 } }),
          block(b + 6, 0, 40, { melee = true, dist_by_target = { [b + 5] = 40, [b + 7] = 8 } }),
          block(b + 7, 10, 40, { melee = true, dist_by_target = { [b + 5] = 40, [b + 6] = 8 } }) },
        { sv = S({ [b + 5] = 900, [b + 6] = 500, [b + 7] = 500 }) } end, "raging_tornado", K.RT, 1, "g67" },
    { "RT2. Raging Tornado: no enemy in melee -> no cast",
      function(b) return { own(HURR, b, K.RT, { unit_class = "art_fix", dist_by_target = { [b + 5] = 40 } }) },
        { block(b + 5, 0, 40) }, { sv = S({ [b + 5] = 900 }) } end, "raging_tornado", K.RT, 0, nil },
  }
  for _, f in ipairs(FILES) do
    local TAG = f.tag
    for i, w in ipairs(WORLDS) do
      local b = 53000 + i * 20
      local units, enemies, o = w[2](b)
      local W = world(w[1], units, enemies, w[3], w[4], f.path, TAG, o)
      if W ~= nil then
        local got, on_t = 0, 0
        local want = w[6]
        local ok_t = {}
        if want ~= nil and want:sub(1, 1) == "u" then
          ok_t[tostring(b + tonumber(want:sub(2)))] = true
        elseif want ~= nil then
          for c = 2, #want do ok_t["pos:" .. tostring(b + tonumber(want:sub(c, c)))] = true end
        end
        for _, x in ipairs(W.fires) do
          if x.key == w[4] then
            got = got + 1
            local tid = nil
            pcall(function() tid = tostring(x.target:unique_ui_id()) end)
            if tid ~= nil and ok_t[tid] then on_t = on_t + 1 end
          end
        end
        for _, x in ipairs(W.ground_fires or {}) do
          if x.key == w[4] then
            got = got + 1
            if x.pos ~= nil and ok_t[tostring(x.pos.marker)] then on_t = on_t + 1 end
          end
        end
        local a, txt
        if RED183 then
          a = (got == 0)
          txt = "-REDa: the pre-184 build has no entry, got " .. got
        else
          a = (got == w[5]) and (w[5] == 0 or want == nil or on_t == w[5])
          local gpos = (W.ground_fires ~= nil and W.ground_fires[1] ~= nil and W.ground_fires[1].pos ~= nil)
            and tostring(W.ground_fires[1].pos.marker) or "-"
          txt = "a: " .. w[5] .. " cast(s) expected, got " .. got .. ", on target " .. on_t .. " (ground " .. gpos .. ")"
        end
        check(TAG .. w[1]:sub(1, 3) .. txt, a)
        done(a)
        if i == 1 then
          local by = {}
          for _, e in ipairs(W.cap or {}) do by[e.marker] = e.card end
          local c_ok = by.soul_stealer_ror == "%CARD_SS%"
            and by.warpstorm_scroll == "%CARD_WS%"
            and by.raging_tornado == "%CARD_RT%"
          check(TAG .. "CA12: the cards (" .. tostring(by.soul_stealer_ror) .. " | " .. tostring(by.warpstorm_scroll)
            .. " | " .. tostring(by.raging_tornado) .. ")", (RED183 and not c_ok) or (not RED183 and c_ok))
          done((RED183 and not c_ok) or (not RED183 and c_ok))
        end
        tally(W)
      end
    end
  end
  if RED183 then
    check("RED CONTROL (harness 183): the pre-184 build has none of the 10 entries - " .. n_ok .. "/" .. n_all,
      n_all == 20 and n_ok == 20)
  else
    check("HARNESS 183: every check behaved - " .. n_ok .. "/" .. n_all, n_all == 20 and n_ok == 20)
  end
  print("== HARNESS 183 done: " .. (checks - pre183) .. " checks in this section ==")
end
