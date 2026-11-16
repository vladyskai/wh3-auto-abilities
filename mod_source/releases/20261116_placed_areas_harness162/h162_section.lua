-- ============================================================================
-- HARNESS 162 (round 163): THE PLACED AREAS AND THE EXPENDABLE UNITS (user rulings 2026-11-16).
--   IB1 Frost Fang (15 m blast): a 200-man Grave Guard block standing, our Swordsmen 55 m away -> ONE cast at it.
--   IB2 Frost Fang: our Swordsmen 20 m from the target (inside 15 + 10) -> no cast.
--   EX1 Frost Fang: our SKAVENSLAVES 20 m from the target (expendable) -> ONE cast.
--   EX2 Frost Fang: our ZOMBIES 20 m from the target, live value 0.5 per soldier (cheap) -> ONE cast.
--   EX3 Banishment (round 162): our Skavenslaves 25 m from the target (inside its 38 m) -> ONE cast (RED: none).
--   MS1 Magma Storm (20 m vortex + 60 m bombardment = 75 m clear): ours 55 m away -> no cast.
--   MS2 Magma Storm: ours 115 m away, a 400-man block -> ONE ground cast.
--   AV1 Arcane Vassal: our Hero fighting inside a 200-man enemy block 55 m away -> ONE cast ON that Hero.
--   AV2 Arcane Vassal: the same Hero, no enemy near -> no cast.
--   BF1 Befuddlement of Mischiefs: a fast enemy 20 m from us -> ONE cast at it.
--   WS1 Winged Staff: Grave Guard (120) 60 m away, the caster standing -> ONE cast at it.
--   CL1 Chain Lightning (RoR): a 200-man block, ours 55 m away -> ONE cast at it.
--   SB1 Siegebreaker: a standing Vampire (900), none of ours near -> ONE ground cast.
--   SB2 Siegebreaker: the Vampire moving -> no cast.
--   RED (pre-163 = round 162): IB1, EX3, MS2, AV1, BF1, WS1, CL1, SB1 cast nothing.
-- ============================================================================
function run_h162()
  local L162 = os.getenv("H162_LIVE") or LIVE
  local A162 = os.getenv("H162_ANN") or ANN
  local RED162 = (os.getenv("H162_LIVE") ~= nil) or (os.getenv("H162_ANN") ~= nil)
  local FF = "wh3_main_weapon_abilities_frost_fang"
  local BN = "wh3_main_spell_bound_banishment"
  local MS = "wh3_pro10_cataclysm_fire_magma_storm_bound"
  local AV = "wh2_main_character_abilities_arcane_vassal"
  local BF = "wh2_dlc16_character_abilities_befuddlement_of_mischiefs"
  local WS = "wh2_main_weapon_bound_winged_staff"
  local CL = "wh_main_spell_bound_chain_lightning_ror"
  local SB = "wh3_main_weapon_abilities_siegebreaker"
  local CASTER = "wh2_dlc13_emp_cha_huntsmen_general_0"
  local HERO = "wh_main_emp_cha_captain_0"
  local GG = "wh_main_vmp_inf_grave_guard_0"
  local VA = "wh_main_vmp_cha_vampire_0"
  local SW = "wh_main_emp_inf_swordsmen"
  local SLAVES = "wh2_main_skv_inf_skavenslaves_0"
  local ZOMB = "wh_main_vmp_inf_zombie"
  local pre162 = checks
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1; at = i + #tok
    end
  end

  print("== HARNESS 162 - section 0zz10: the round-163 tokens ==")
  if not RED162 then
    for _, f in ipairs({ { name = "live", path = L162 }, { name = "ann", path = A162 } }) do
      local s = read_file(f.path)
      check("0zz10 " .. f.name .. ": 918 entries, 42 wanderers, the strike and the vassal wired, the expendable skip",
        cp(s, "\t{ marker = ") == 918 and cp(s, 'trigger = "enemy_wander"') == 42
        and cp(s, 'trigger = "enemy_strike"') == 1 and cp(s, 'trigger = "ally_blast"') == 1
        and raw_find(s, "enemy_strike = FOURTH.evaluate_enemy_strike,", 1, true) ~= nil
        and raw_find(s, "ally_blast = FOURTH.evaluate_ally_blast,", 1, true) ~= nil
        and raw_find(s, "if s ~= nil and not FOURTH.ff_ignored(s) then m.ours[#m.ours + 1] = s end", 1, true) ~= nil
        and raw_find(s, "wh3_pro10_cataclysm_fire_magma_storm_bound=2,20,0,0,45,1,1;", 1, true) ~= nil
        and raw_find(s, "wh2_main_skv_inf_skavenslaves_0;", 1, true) ~= nil)
    end
  end

  local FILES = { { path = A162, tag = "[annotated] " }, { path = L162, tag = "[live] " } }
  local n_ok, n_all = 0, 0
  local function done(ok) n_all = n_all + 1; if ok then n_ok = n_ok + 1 end end
  local function our_unit(W, uid)
    for _, u in ipairs(W.mock_units or {}) do
      local ok, id = pcall(function() return u:unique_ui_id() end)
      if ok and tostring(id) == tostring(uid) then return u end
    end
    return nil
  end
  local function world(wname, units, enemies, marker, key, PATH, TAG, sv, osv)
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
    for uid, v in pairs(osv or {}) do
      local u = our_unit(W, uid)
      if u ~= nil then u.strategic_value = function(self) return v end end
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
    local e = { uid = uid, name = name, melee = false, pos = { x, 0, z }, width = 20, men_alive = 200,
                initial_men = 200, unit_class = "inf_mel", dist = 60 }
    for k, v in pairs(o or {}) do e[k] = v end
    return e
  end
  local function ours(uid, name, x, z, o)
    local u = { uid = uid, name = name, owns = {}, melee = false, pos = { x, 0, z }, width = 29.4, men_alive = 120,
                initial_men = 120, unit_class = "inf_mel" }
    for k, v in pairs(o or {}) do u[k] = v end
    return u
  end
  local BIG = { men_alive = 400, initial_men = 400, width = 30 }
  -- name, builder(b) -> units, enemies, sv, our sv; marker; key; GREEN casts; RED casts (nil = not RED);
  -- target offset (nil = not checked; 1 = our unit b + 1)
  local WORLDS = {
    { "IB1. Frost Fang: a 200-man block standing, our Swordsmen 55 m away -> ONE cast at it",
      function(b) return { caster(b, FF), ours(b + 1, SW, 0, 140) }, { block(b + 5, GG, 0, 80) },
        { [tostring(b + 5)] = 1600 } end, "frost_fang", FF, 1, 0, 5 },
    { "IB2. Frost Fang: our Swordsmen 20 m from the target -> no cast",
      function(b) return { caster(b, FF), ours(b + 1, SW, 0, 105) }, { block(b + 5, GG, 0, 80) },
        { [tostring(b + 5)] = 1600 } end, "frost_fang", FF, 0, nil, nil },
    { "EX1. Frost Fang: our SKAVENSLAVES 20 m from the target (expendable) -> ONE cast",
      function(b) return { caster(b, FF), ours(b + 1, SLAVES, 0, 105) }, { block(b + 5, GG, 0, 80) },
        { [tostring(b + 5)] = 1600 } end, "frost_fang", FF, 1, nil, 5 },
    { "EX2. Frost Fang: our ZOMBIES 20 m from the target, 0.5 per soldier (cheap) -> ONE cast",
      function(b) return { caster(b, FF), ours(b + 1, ZOMB, 0, 105) }, { block(b + 5, GG, 0, 80) },
        { [tostring(b + 5)] = 1600 }, { [b + 1] = 60 } end, "frost_fang", FF, 1, nil, 5 },
    { "EX3. Banishment: our Skavenslaves 25 m from the target (inside 38 m) -> ONE cast",
      function(b) return { caster(b, BN), ours(b + 1, SLAVES, 0, 110) }, { block(b + 5, GG, 0, 80) },
        { [tostring(b + 5)] = 1600 } end, "banishment", BN, 1, 0, 5 },
    { "MS1. Magma Storm (75 m clear): ours 55 m away -> no cast",
      function(b) return { caster(b, MS), ours(b + 1, SW, 0, 140) }, { block(b + 5, GG, 0, 80, BIG) },
        { [tostring(b + 5)] = 3200 } end, "magma_storm", MS, 0, nil, nil },
    { "MS2. Magma Storm: ours 115 m away, a 400-man block -> ONE ground cast",
      function(b) return { caster(b, MS), ours(b + 1, SW, 0, 200) }, { block(b + 5, GG, 0, 80, BIG) },
        { [tostring(b + 5)] = 3200 } end, "magma_storm", MS, 1, 0, nil },
    { "AV1. Arcane Vassal: our Hero fighting inside a 200-man block 55 m away -> ONE cast ON the Hero",
      function(b) return { caster(b, AV), ours(b + 1, HERO, 0, 55, { width = 2, men_alive = 1, initial_men = 1,
          unit_class = "com", melee = true, dist = 55 }) }, { block(b + 5, GG, 0, 55, { melee = true }) },
        { [tostring(b + 5)] = 1600 } end, "arcane_vassal", AV, 1, 0, 1 },
    { "AV2. Arcane Vassal: the same Hero, no enemy near -> no cast",
      function(b) return { caster(b, AV), ours(b + 1, HERO, 0, 55, { width = 2, men_alive = 1, initial_men = 1,
          unit_class = "com", dist = 55 }) }, {}, {} end, "arcane_vassal", AV, 0, nil, nil },
    { "BF1. Befuddlement of Mischiefs: a fast enemy 20 m from us -> ONE cast at it",
      function(b) return { caster(b, BF, { dist = 20 }) },
        { { uid = b + 5, name = VA, melee = false, pos = { 0, 0, 30 }, width = 6, men_alive = 1, initial_men = 1,
            unit_class = "com", dist = 20, moving = true, fast_speed = 8 } }, {} end,
      "befuddlement_of_mischiefs", BF, 1, 0, 5 },
    { "WS1. Winged Staff: Grave Guard (120) 60 m away, the caster standing -> ONE cast at it",
      function(b) return { caster(b, WS) }, { block(b + 5, GG, 0, 80, { men_alive = 120, initial_men = 120, width = 29.4 }) },
        { [tostring(b + 5)] = 800 } end, "winged_staff", WS, 1, 0, 5 },
    { "CL1. Chain Lightning (RoR): a 200-man block, ours 55 m away -> ONE cast at it",
      function(b) return { caster(b, CL), ours(b + 1, SW, 0, 140) }, { block(b + 5, GG, 0, 80) },
        { [tostring(b + 5)] = 1600 } end, "chain_lightning_ror", CL, 1, 0, 5 },
    { "SB1. Siegebreaker: a standing Vampire (900), none of ours near -> ONE ground cast",
      function(b) return { caster(b, SB) },
        { { uid = b + 5, name = VA, melee = false, pos = { 0, 0, 100 }, width = 6, men_alive = 1, initial_men = 1,
            unit_class = "com", dist = 60 } }, { [tostring(b + 5)] = 900 } end, "siegebreaker", SB, 1, 0, nil },
    { "SB2. Siegebreaker: the Vampire moving -> no cast",
      function(b) return { caster(b, SB) },
        { { uid = b + 5, name = VA, melee = false, pos = { 0, 0, 100 }, width = 6, men_alive = 1, initial_men = 1,
            unit_class = "com", dist = 60, moving = true } }, { [tostring(b + 5)] = 900 } end,
      "siegebreaker", SB, 0, nil, nil },
  }
  for _, f in ipairs(FILES) do
    local TAG = f.tag
    for i, w in ipairs(WORLDS) do
      local want = w[5]
      if RED162 then want = w[6] end
      if want ~= nil then
        local b = 26000 + i * 20
        local units, enemies, sv, osv = w[2](b)
        local W = world(w[1], units, enemies, w[3], w[4], f.path, TAG, sv, osv)
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
          if want > 0 and not RED162 and w[7] ~= nil then
            a = a and tid == tostring(b + w[7])
            ttxt = ", target " .. tostring(tid) .. " want " .. tostring(b + w[7])
          end
          check(TAG .. w[1]:sub(1, 3) .. (RED162 and "-RED" or "") .. "a: " .. want .. " cast(s) expected, got " .. got
            .. ttxt, a)
          done(a)
          tally(W)
        end
      end
    end
  end
  if RED162 then
    check("RED CONTROL (harness 162): the pre-163 build has none of the placed areas and protects expendables - "
      .. n_ok .. "/" .. n_all, n_all == 16 and n_ok == 16)
  else
    check("HARNESS 162: every world behaved - " .. n_ok .. "/" .. n_all, n_all == 28 and n_ok == 28)
  end
  print("== HARNESS 162 done: " .. (checks - pre162) .. " checks in this section ==")
end
