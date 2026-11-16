-- ============================================================================
-- HARNESS 163 (round 164): THE FRIENDLY-FIRE BREATHS (user rulings 2026-11-16).
--   BR1 Sunfang (12 m wave, starts 24 m before the target): Grave Guard standing 40 m away -> ONE cast at it
--       (the caster sits inside its own corridor: it does not count).
--   BR2 Kovsh Breath (10 m reach): Grave Guard standing 8 m away -> ONE cast at it.
--   BR3 Blue Fire of Chaos (the game refuses it in melee): the caster fighting -> no cast.
--   BR4 Blue Fire of Chaos: the caster free, a standing block 40 m away -> ONE ground cast.
--   WV6 Wrath of Manann (round 162): Grave Guard 45 m away, the caster inside the old corridor -> ONE cast (RED: none).
--   CH1 Wind Blast (slows, rule 10): a fast enemy 20 m from us, the path clear -> ONE cast at it.
--   CH2 Wind Blast: the same enemy standing -> no cast.
--   CN1 Pestilent Breath (a cone from the caster): Grave Guard standing 15 m away -> ONE cast at it.
--   CN2 Pestilent Breath: our Swordsmen 15 m beside the cone -> no cast.
--   SW1 Disembowelling Sweep (12 m reach): the caster and Grave Guard in melee, none of ours near -> ONE cast at it.
--   SW2 Disembowelling Sweep: our Swordsmen 15 m from the caster (inside 12 + 10) -> no cast.
--   LN1 Da Boss' Loons (98 m from the caster): a 200-man block 8 m away, none of ours -> ONE cast.
--   LN2 Da Boss' Loons: our Swordsmen 90 m from the caster -> no cast.
--   RED (pre-164 = round 163): BR1, BR2, BR4, WV6, CH1, CN1, SW1, LN1 cast nothing.
-- ============================================================================
function run_h163()
  local L163 = os.getenv("H163_LIVE") or LIVE
  local A163 = os.getenv("H163_ANN") or ANN
  local RED163 = (os.getenv("H163_LIVE") ~= nil) or (os.getenv("H163_ANN") ~= nil)
  local SF = "wh2_main_weapon_abilities_sunfang"
  local KB = "wh3_main_item_abilities_kovsh_breath"
  local BF = "wh3_main_daemon_arms_abilities_blue_fire"
  local WM = "wh_dlc07_item_abilities_wrath_of_manann"
  local WB = "wh2_dlc11_spell_bound_wind_blast"
  local PB = "wh3_main_spell_bound_pestilent_breath"
  local DS = "wh3_dlc29_unit_active_ripping_blades"
  local LO = "wh2_dlc15_lord_abilities_da_boss_loons"
  local CASTER = "wh2_dlc13_emp_cha_huntsmen_general_0"
  local GG = "wh_main_vmp_inf_grave_guard_0"
  local VA = "wh_main_vmp_cha_vampire_0"
  local SW = "wh_main_emp_inf_swordsmen"
  local pre163 = checks
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1; at = i + #tok
    end
  end

  print("== HARNESS 163 - section 0zz11: the round-164 tokens ==")
  if not RED163 then
    for _, f in ipairs({ { name = "live", path = L163 }, { name = "ann", path = A163 } }) do
      local s = read_file(f.path)
      check("0zz11 " .. f.name .. ": 946 entries, 30 waves, the charge / cone / sweep families wired, the melee rule",
        cp(s, "\t{ marker = ") == 946 and cp(s, 'trigger = "enemy_wave"') == 30
        and cp(s, 'trigger = "enemy_wave_charge"') == 2 and cp(s, 'trigger = "enemy_cone"') == 5
        and cp(s, 'trigger = "enemy_sweep"') == 2 and cp(s, 'trigger = "enemy_wander"') == 43
        and raw_find(s, "enemy_wave_charge = FOURTH.evaluate_enemy_wave_charge,", 1, true) ~= nil
        and raw_find(s, "enemy_cone = FOURTH.evaluate_enemy_cone,", 1, true) ~= nil
        and raw_find(s, "enemy_sweep = FOURTH.evaluate_enemy_sweep,", 1, true) ~= nil
        and raw_find(s, 'FOURTH.WW_NOMELEE_TEXT = "wh3_main_daemon_arms_abilities_blue_fire;', 1, true) ~= nil)
    end
  end

  local FILES = { { path = A163, tag = "[annotated] " }, { path = L163, tag = "[live] " } }
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
  local function ours(uid, x, z)
    return { uid = uid, name = SW, owns = {}, melee = false, pos = { x, 0, z }, width = 29.4, men_alive = 120,
             initial_men = 120, unit_class = "inf_mel" }
  end
  local BIG = { men_alive = 200, initial_men = 200, width = 20, dist = 8 }
  -- name, builder(b) -> units, enemies, sv; marker; key; GREEN casts; RED casts (nil = not RED); target offset
  local WORLDS = {
    { "BR1. Sunfang: Grave Guard standing 40 m away (the caster inside its own corridor) -> ONE cast at it",
      function(b) return { caster(b, SF) }, { block(b + 5, GG, 0, 55) }, { [tostring(b + 5)] = 800 } end,
      "sunfang", SF, 1, 0, 5 },
    { "BR2. Kovsh Breath: Grave Guard standing 8 m away -> ONE cast at it",
      function(b) return { caster(b, KB, { dist = 8 }) }, { block(b + 5, GG, 0, 20, { dist = 8 }) },
        { [tostring(b + 5)] = 800 } end, "kovsh_breath", KB, 1, 0, 5 },
    { "BR3. Blue Fire of Chaos: the caster fighting in melee -> no cast",
      function(b) return { caster(b, BF, { melee = true }) }, { block(b + 5, GG, 0, 55) }, { [tostring(b + 5)] = 800 } end,
      "blue_fire", BF, 0, nil, nil },
    { "BR4. Blue Fire of Chaos: the caster free, a standing block 40 m away -> ONE ground cast",
      function(b) return { caster(b, BF) }, { block(b + 5, GG, 0, 55) }, { [tostring(b + 5)] = 800 } end,
      "blue_fire", BF, 1, 0, nil },
    { "WV6. Wrath of Manann: Grave Guard 45 m away, the caster inside the old corridor -> ONE cast at it",
      function(b) return { caster(b, WM) }, { block(b + 5, GG, 0, 45) }, { [tostring(b + 5)] = 800 } end,
      "wrath_of_manann", WM, 1, 0, 5 },
    { "CH1. Wind Blast: a fast enemy 20 m from us, the path clear -> ONE cast at it",
      function(b) return { caster(b, WB, { dist = 20 }) },
        { { uid = b + 5, name = VA, melee = false, pos = { 0, 0, 40 }, width = 6, men_alive = 1, initial_men = 1,
            unit_class = "com", dist = 20, moving = true, fast_speed = 8 } }, { [tostring(b + 5)] = 900 } end,
      "wind_blast", WB, 1, 0, 5 },
    { "CH2. Wind Blast: the same enemy standing -> no cast",
      function(b) return { caster(b, WB, { dist = 20 }) },
        { { uid = b + 5, name = VA, melee = false, pos = { 0, 0, 40 }, width = 6, men_alive = 1, initial_men = 1,
            unit_class = "com", dist = 20 } }, { [tostring(b + 5)] = 900 } end, "wind_blast", WB, 0, nil, nil },
    { "CN1. Pestilent Breath: Grave Guard standing 15 m away -> ONE cast at it",
      function(b) return { caster(b, PB, { dist = 15 }) }, { block(b + 5, GG, 0, 25, { dist = 15 }) },
        { [tostring(b + 5)] = 800 } end, "pestilent_breath", PB, 1, 0, 5 },
    { "CN2. Pestilent Breath: our Swordsmen 15 m beside the cone -> no cast",
      function(b) return { caster(b, PB, { dist = 15 }), ours(b + 1, 30, 40) }, { block(b + 5, GG, 0, 25, { dist = 15 }) },
        { [tostring(b + 5)] = 800 } end, "pestilent_breath", PB, 0, nil, nil },
    { "SW1. Disembowelling Sweep: the caster and Grave Guard in melee, none of ours near -> ONE cast at it",
      function(b) return { caster(b, DS, { melee = true, dist = 2 }) }, { block(b + 5, GG, 0, 8, { melee = true, dist = 2 }) },
        { [tostring(b + 5)] = 800 } end, "disembowelling_sweep", DS, 1, 0, 5 },
    { "SW2. Disembowelling Sweep: our Swordsmen 15 m from the caster -> no cast",
      function(b) return { caster(b, DS, { melee = true, dist = 2 }), ours(b + 1, 0, -20) },
        { block(b + 5, GG, 0, 8, { melee = true, dist = 2 }) }, { [tostring(b + 5)] = 800 } end,
      "disembowelling_sweep", DS, 0, nil, nil },
    { "LN1. Da Boss' Loons: a 200-man block 8 m away, none of ours -> ONE cast",
      function(b) return { caster(b, LO, { dist = 8 }) }, { block(b + 5, GG, 0, 20, BIG) },
        { [tostring(b + 5)] = 1600 } end, "da_boss_loons", LO, 1, 0, 5 },
    { "LN2. Da Boss' Loons: our Swordsmen 90 m from the caster -> no cast",
      function(b) return { caster(b, LO, { dist = 8 }), ours(b + 1, 0, -90) }, { block(b + 5, GG, 0, 20, BIG) },
        { [tostring(b + 5)] = 1600 } end, "da_boss_loons", LO, 0, nil, nil },
  }
  for _, f in ipairs(FILES) do
    local TAG = f.tag
    for i, w in ipairs(WORLDS) do
      local want = w[5]
      if RED163 then want = w[6] end
      if want ~= nil then
        local b = 27000 + i * 20
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
          if want > 0 and not RED163 and w[7] ~= nil then
            a = a and tid == tostring(b + w[7])
            ttxt = ", target " .. tostring(tid) .. " want " .. tostring(b + w[7])
          end
          check(TAG .. w[1]:sub(1, 3) .. (RED163 and "-RED" or "") .. "a: " .. want .. " cast(s) expected, got " .. got
            .. ttxt, a)
          done(a)
          tally(W)
        end
      end
    end
  end
  if RED163 then
    check("RED CONTROL (harness 163): the pre-164 build has none of the breaths and lets the caster block its wave - "
      .. n_ok .. "/" .. n_all, n_all == 16 and n_ok == 16)
  else
    check("HARNESS 163: every world behaved - " .. n_ok .. "/" .. n_all, n_all == 26 and n_ok == 26)
  end
  print("== HARNESS 163 done: " .. (checks - pre163) .. " checks in this section ==")
end
