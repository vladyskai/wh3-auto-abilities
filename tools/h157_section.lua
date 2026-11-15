-- ============================================================================
-- HARNESS 157 (round 158): THE LAST GROUP B ATTACKS (user rulings 2026-11-15).
--   AD1 Fate of Bjuna: Zombies (value 75) and Grave Guard (800), 120 men each
--       -> ONE cast at the Grave Guard (value per soldier).
--   AD2 Fate of Bjuna: Grave Guard with 20 men (fewer than its 25) -> no cast.
--   AD3 Fate of Bjuna: the caster is moving -> no cast.
--   AD4 Staff of Masks (15 per tick, 35 m bound): Grave Guard with 20 men,
--       30 m away -> ONE cast at it.
--   AD5 Blood Statuette: our Swordsmen fight the Grave Guard (no margin) -> ONE cast.
--   SN1 Storm of the Night: a FLYING enemy (8 m/s) 20 m from us -> ONE cast at it.
--   SN2 Storm of the Night: the same enemy on the ground -> no cast.
--   EB1 Ethrac's Brazier: an enemy in melee -> ONE cast at it.
--   PH1 Preyton Horns: an enemy in melee -> ONE cast at it.
--   PH2 Preyton Horns: an idle enemy -> no cast.
--   AT1 The Amber Trance: a wavering enemy -> ONE cast at it.
--   AT2 The Amber Trance: a steady enemy -> no cast.
--   DL1 Dweomer Leach Orb: a Vampire (900) and Grave Guard (1500) -> ONE cast at the Vampire.
--   DL2 Dweomer Leach Orb: Grave Guard only -> no cast.
--   RED (pre-158 = round 157): AD1, SN1, EB1, PH1, AT1, DL1 cast nothing.
-- ============================================================================
function run_h157()
  local L157 = os.getenv("H157_LIVE") or LIVE
  local A157 = os.getenv("H157_ANN") or ANN
  local RED157 = (os.getenv("H157_LIVE") ~= nil) or (os.getenv("H157_ANN") ~= nil)
  local BJ = "wh3_main_spell_bound_the_fate_of_bjuna"
  local SM = "wh3_dlc27_item_abilities_staff_of_the_masque"
  local BS = "wh2_main_item_abilities_blood_statuette_of_spite"
  local SN = "wh2_dlc11_lord_abilities_storm_of_the_night"
  local EB = "wh3_dlc29_item_active_ethracs_brazier"
  local PH = "wh3_dlc27_item_abilities_preyton_horns"
  local AT = "wh2_dlc10_item_abilities_the_amber_trance"
  local DL = "wh3_dlc23_item_abilities_dweomer_leach_orb"
  local CASTER = "wh2_dlc13_emp_cha_huntsmen_general_0"
  local VA = "wh_main_vmp_cha_vampire_0"
  local GG = "wh_main_vmp_inf_grave_guard_0"
  local ZB = "wh_main_vmp_inf_zombie"
  local SW = "wh_main_emp_inf_swordsmen"
  local pre157 = checks
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1; at = i + #tok
    end
  end

  print("== HARNESS 157 - section 0zz5: the round-158 tokens ==")
  if not RED157 then
    for _, f in ipairs({ { name = "live", path = L157 }, { name = "ann", path = A157 } }) do
      local s = read_file(f.path)
      check("0zz5 " .. f.name .. ": 834 entries, 7 area drains, the Leach Orb, the flying class, the AREA table",
        cp(s, "\t{ marker = ") == 834
        and cp(s, 'trigger = "enemy_area_drain"') == 7 and cp(s, 'trigger = "enemy_commander_value"') == 1
        and raw_find(s, "enemy_area_drain = FOURTH.evaluate_enemy_area_drain,", 1, true) ~= nil
        and raw_find(s, "enemy_commander_value = FOURTH.evaluate_enemy_commander_value,", 1, true) ~= nil
        and raw_find(s, 'if cls == "flying" then', 1, true) ~= nil
        and raw_find(s, "wh3_dlc27_item_abilities_staff_of_the_masque=15;", 1, true) ~= nil
        and raw_find(s, 'if kind == "area" and e.men < FOURTH.area_min() then return false end', 1, true) ~= nil)
    end
  end

  local FILES = { { path = A157, tag = "[annotated] " }, { path = L157, tag = "[live] " } }
  local n_ok, n_all = 0, 0
  local function done(ok) n_all = n_all + 1; if ok then n_ok = n_ok + 1 end end
  local function world(wname, units, enemies, marker, key, PATH, TAG, sv, fly)
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
        local f = (fly ~= nil and fly[id] == true)
        pr.unit.is_visible_to_alliance = function(self, a) return true end
        pr.unit.is_currently_flying = function(self) return f end
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
    local c = { name = CASTER, uid = b, owns = { key }, melee = false, dist = 60, pos = { 0, 0, 0 }, width = 2,
                men_alive = 1, unit_class = "com" }
    for k, v in pairs(o or {}) do c[k] = v end
    return c
  end
  local function block(uid, name, x, z, o)
    local e = { uid = uid, name = name, melee = false, pos = { x, 0, z }, width = 29.4, men_alive = 120,
                initial_men = 120, unit_class = "inf_mel", dist = 60 }
    for k, v in pairs(o or {}) do e[k] = v end
    return e
  end
  local function single(uid, name, x, z, cls)
    return { uid = uid, name = name, melee = false, pos = { x, 0, z }, width = 6, men_alive = 1, initial_men = 1,
             unit_class = cls, dist = 60 }
  end
  local function ours(uid, z)
    return { uid = uid, name = SW, owns = {}, melee = true, pos = { 0, 0, z }, width = 29.4, men_alive = 120,
             initial_men = 120, unit_class = "inf_mel" }
  end
  -- name, builder(b) -> units, enemies, sv, fly; marker; key; GREEN casts; RED casts (nil = not RED); target offset
  local WORLDS = {
    { "AD1. Fate of Bjuna: Zombies (75) and Grave Guard (800) -> ONE cast at the Grave Guard",
      function(b) return { caster(b, BJ) }, { block(b + 5, ZB, 0, 100), block(b + 6, GG, 60, 100) },
        { [tostring(b + 5)] = 75, [tostring(b + 6)] = 800 } end, "fate_of_bjuna", BJ, 1, 0, 6 },
    { "AD2. Fate of Bjuna: Grave Guard down to 20 men (fewer than its 25 per tick) -> no cast",
      function(b) return { caster(b, BJ) }, { block(b + 5, GG, 0, 100, { men_alive = 20 }) },
        { [tostring(b + 5)] = 140 } end, "fate_of_bjuna", BJ, 0, nil, nil },
    { "AD3. Fate of Bjuna: the caster is moving -> no cast",
      function(b) return { caster(b, BJ, { moving = true }) }, { block(b + 5, GG, 0, 100) },
        { [tostring(b + 5)] = 800 } end, "fate_of_bjuna", BJ, 0, nil, nil },
    { "AD4. Staff of Masks (15 per tick): Grave Guard with 20 men 30 m away -> ONE cast at it",
      function(b) return { caster(b, SM, { dist = 30 }) }, { block(b + 5, GG, 0, 100, { men_alive = 20, dist = 30 }) },
        { [tostring(b + 5)] = 140 } end, "staff_of_masks", SM, 1, nil, 5 },
    { "AD5. Blood Statuette: our Swordsmen fight the Grave Guard (no margin) -> ONE cast at it",
      function(b) return { caster(b, BS), ours(b + 1, 100) }, { block(b + 5, GG, 0, 100, { melee = true }) },
        { [tostring(b + 5)] = 800 } end, "blood_statuette_of_spite", BS, 1, nil, 5 },
    { "SN1. Storm of the Night: a FLYING enemy at 8 m/s 20 m from us -> ONE cast at it",
      function(b) return { caster(b, SN, { dist = 20 }) }, { single(b + 5, VA, 0, 100, "com") }, {},
        { [tostring(b + 5)] = true } end, "storm_of_the_night", SN, 1, 0, 5, { moving = true, fast_speed = 8 } },
    { "SN2. Storm of the Night: the same enemy on the ground -> no cast",
      function(b) return { caster(b, SN, { dist = 20 }) }, { single(b + 5, VA, 0, 100, "com") }, {}, {} end,
      "storm_of_the_night", SN, 0, nil, nil, { moving = true, fast_speed = 8 } },
    { "EB1. Ethrac's Brazier: an enemy in melee -> ONE cast at it",
      function(b) return { caster(b, EB) }, { block(b + 5, SW, 0, 100, { melee = true }) }, {} end,
      "ethracs_brazier", EB, 1, 0, 5 },
    { "PH1. Preyton Horns: an enemy in melee -> ONE cast at it",
      function(b) return { caster(b, PH) }, { block(b + 5, SW, 0, 100, { melee = true }) }, {} end,
      "preyton_horns", PH, 1, 0, 5 },
    { "PH2. Preyton Horns: an idle enemy -> no cast",
      function(b) return { caster(b, PH) }, { block(b + 5, SW, 0, 100) }, {} end, "preyton_horns", PH, 0, nil, nil },
    { "AT1. The Amber Trance: a wavering enemy -> ONE cast at it",
      function(b) return { caster(b, AT) }, { block(b + 5, SW, 0, 100, { wavering = true }) }, {} end,
      "the_amber_trance", AT, 1, 0, 5 },
    { "AT2. The Amber Trance: a steady enemy -> no cast",
      function(b) return { caster(b, AT) }, { block(b + 5, SW, 0, 100, { wavering = false }) }, {} end,
      "the_amber_trance", AT, 0, nil, nil },
    { "DL1. Dweomer Leach Orb: a Vampire (900) and Grave Guard (1500) -> ONE cast at the Vampire",
      function(b) return { caster(b, DL) }, { single(b + 5, VA, 0, 100, "com"), block(b + 6, GG, 60, 100) },
        { [tostring(b + 5)] = 900, [tostring(b + 6)] = 1500 } end, "dweomer_leach_orb", DL, 1, 0, 5 },
    { "DL2. Dweomer Leach Orb: Grave Guard only -> no cast",
      function(b) return { caster(b, DL) }, { block(b + 5, GG, 0, 100) }, { [tostring(b + 5)] = 1500 } end,
      "dweomer_leach_orb", DL, 0, nil, nil },
  }
  for _, f in ipairs(FILES) do
    local TAG = f.tag
    for i, w in ipairs(WORLDS) do
      local want = w[5]
      if RED157 then want = w[6] end
      if want ~= nil then
        local b = 19000 + i * 20
        local units, enemies, sv, fly = w[2](b)
        for k, v in pairs(w[8] or {}) do enemies[1][k] = v end
        local W = world(w[1], units, enemies, w[3], w[4], f.path, TAG, sv, fly)
        if W ~= nil then
          local got, tid = 0, nil
          for _, x in ipairs(W.fires) do
            if x.key == w[4] then
              got = got + 1
              if tid == nil then pcall(function() tid = tostring(x.target:unique_ui_id()) end) end
            end
          end
          local a = (got == want)
          local ttxt = ""
          if want > 0 and not RED157 and w[7] ~= nil then
            a = a and tid == tostring(b + w[7])
            ttxt = ", target " .. tostring(tid) .. " want " .. tostring(b + w[7])
          end
          check(TAG .. w[1]:sub(1, 3) .. (RED157 and "-RED" or "") .. "a: " .. want .. " cast(s) expected, got " .. got
            .. ttxt, a)
          done(a)
          tally(W)
        end
      end
    end
  end
  if RED157 then
    check("RED CONTROL (harness 157): the pre-158 build has none of the last group B attacks - " .. n_ok .. "/" .. n_all,
      n_all == 12 and n_ok == 12)
  else
    check("HARNESS 157: every world behaved - " .. n_ok .. "/" .. n_all, n_all == 28 and n_ok == 28)
  end
  print("== HARNESS 157 done: " .. (checks - pre157) .. " checks in this section ==")
end
