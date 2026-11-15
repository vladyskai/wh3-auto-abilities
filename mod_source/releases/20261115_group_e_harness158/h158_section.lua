-- ============================================================================
-- HARNESS 158 (round 159): GROUP E (user rulings 2026-11-15).
--   BG1 Burp of Grom (melee_unwavering): in melee -> ONE cast.
--   MC1 Groundbreaker (melee_clear, 10 m blast): in melee, ours 100 m away -> ONE cast.
--   MC2 Groundbreaker: our Swordsmen 15 m away (inside 10 + 10 m) -> no cast.
--   MC3 Groundbreaker: not in melee -> no cast.
--   FD1 Emberstorm (fly_dive, 10 m blast): flying over an enemy block -> ONE cast.
--   FD2 Emberstorm: the same, landed (not flying) -> no cast.
--   FD3 Emberstorm: flying, the enemy 40 m away (beyond 7 m) -> no cast.
--   FD4 Emberstorm: flying over the enemy, our Swordsmen 15 m away -> no cast.
--   LS1 Necrotic Explosion (last_stand_clear, 15 m): 8% health in melee -> ONE cast.
--   LS2 Necrotic Explosion: 50% health in melee -> no cast.
--   LS3 Necrotic Explosion: 8% in melee, our Swordsmen 20 m away (inside 25 m) -> no cast.
--   SG1 Deathmaster's Sigil: a Vampire on the ground, none of ours near -> ONE cast at it.
--   SG2 Deathmaster's Sigil: the Vampire flying -> no cast.
--   SG3 Deathmaster's Sigil: our Swordsmen 12 m from the Vampire (inside 25 m) -> no cast.
--   SL1 Slann Gold: a Vampire (900) and Grave Guard (1500) -> ONE cast at the Vampire.
--   FS1 Frost Dragon Scale (enemy_blob_vortex, 7 m): Grave Guard 15 m away, standing -> ONE cast at it.
--   HF1 Heaven's Flash (enemy_ground_melee): an enemy in melee -> ONE cast.
--   SS1 Slime Smoothie (health_aura_ground): the caster at 60% -> ONE cast.
--   SB1 Maneater Smoke Bomb (charge_or_melee): in melee -> ONE cast.
--   VV1 Verminous Valour (wavering_self): wavering -> ONE cast.
--   RED (pre-159 = round 158): BG1, MC1, FD1, LS1, SG1, SL1, FS1, HF1, SS1, SB1, VV1 cast nothing.
-- ============================================================================
function run_h158()
  local L158 = os.getenv("H158_LIVE") or LIVE
  local A158 = os.getenv("H158_ANN") or ANN
  local RED158 = (os.getenv("H158_LIVE") ~= nil) or (os.getenv("H158_ANN") ~= nil)
  local BG = "wh2_dlc15_character_abilities_burp_of_grom_0"
  local GB = "wh3_main_character_abilities_groundbreaker"
  local EM = "wh2_dlc15_unit_abilities_emberstorm"
  local NE = "wh3_main_unit_abilities_necrotic_explosion"
  local SG = "wh2_dlc14_lord_abilities_deathmasters_sigil"
  local SL = "wh2_dlc11_item_abilities_slann_gold"
  local FS = "wh_dlc08_item_abilities_ancient_frost_wyrm_scale"
  local HF = "wh3_main_unit_abilities_stun_bomb"
  local SS = "wh2_dlc15_character_abilities_slimy_smoothie"
  local SB = "wh3_dlc26_unit_abilities_maneater_smoke_bomb"
  local VV = "wh2_main_character_abilities_verminous_valour"
  local CASTER = "wh2_dlc13_emp_cha_huntsmen_general_0"
  local VA = "wh_main_vmp_cha_vampire_0"
  local GG = "wh_main_vmp_inf_grave_guard_0"
  local SW = "wh_main_emp_inf_swordsmen"
  local pre158 = checks
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1; at = i + #tok
    end
  end

  print("== HARNESS 158 - section 0zz6: the round-159 tokens ==")
  if not RED158 then
    for _, f in ipairs({ { name = "live", path = L158 }, { name = "ann", path = A158 } }) do
      local s = read_file(f.path)
      check("0zz6 " .. f.name .. ": 860 entries, the 4 new families wired, the VORTEX table, commander_ground",
        cp(s, "\t{ marker = ") == 860
        and cp(s, 'trigger = "melee_clear"') == 5 and cp(s, 'trigger = "fly_dive"') == 2
        and cp(s, 'trigger = "last_stand_clear"') == 1 and cp(s, 'trigger = "enemy_blob_vortex"') == 1
        and cp(s, 'trigger = "enemy_commander_value"') == 3
        and raw_find(s, "melee_clear = FOURTH.evaluate_melee_clear,", 1, true) ~= nil
        and raw_find(s, "fly_dive = FOURTH.evaluate_fly_dive,", 1, true) ~= nil
        and raw_find(s, "last_stand_clear = FOURTH.evaluate_last_stand_clear,", 1, true) ~= nil
        and raw_find(s, "enemy_blob_vortex = FOURTH.evaluate_enemy_blob,", 1, true) ~= nil
        and raw_find(s, 'if cls == "commander_ground" then', 1, true) ~= nil
        and raw_find(s, "wh3_dlc25_unit_abilities_marienburg_land_mines=25;", 1, true) ~= nil
        and raw_find(s, "wh_dlc08_item_abilities_ancient_frost_wyrm_scale=7", 1, true) ~= nil)
    end
  end

  local FILES = { { path = A158, tag = "[annotated] " }, { path = L158, tag = "[live] " } }
  local n_ok, n_all = 0, 0
  local function done(ok) n_all = n_all + 1; if ok then n_ok = n_ok + 1 end end
  local function our_unit(W, uid)
    for _, u in ipairs(W.mock_units or {}) do
      local ok, id = pcall(function() return u:unique_ui_id() end)
      if ok and tostring(id) == tostring(uid) then return u end
    end
    return nil
  end
  local function world(wname, units, enemies, marker, key, PATH, TAG, sv, efly, selffly)
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
        local f = (efly ~= nil and efly[id] == true)
        pr.unit.is_visible_to_alliance = function(self, a) return true end
        pr.unit.is_currently_flying = function(self) return f end
        local v = sv[id]
        if v ~= nil then pr.unit.strategic_value = function(self) return v end end
      end
    end
    if selffly ~= nil then
      local u = our_unit(W, units[1].uid)
      if u ~= nil then u.is_currently_flying = function(self) return selffly end end
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
  local function single(uid, name, x, z, cls, o)
    local e = { uid = uid, name = name, melee = false, pos = { x, 0, z }, width = 6, men_alive = 1, initial_men = 1,
                unit_class = cls, dist = 60 }
    for k, v in pairs(o or {}) do e[k] = v end
    return e
  end
  local function ours(uid, x, z)
    return { uid = uid, name = SW, owns = {}, melee = false, pos = { x, 0, z }, width = 29.4, men_alive = 120,
             initial_men = 120, unit_class = "inf_mel" }
  end
  local M = { melee = true }
  -- name, builder(b) -> units, enemies, sv, enemy fly, self fly; marker; key; GREEN casts; RED casts (nil = not RED);
  -- target offset (nil = not checked)
  local WORLDS = {
    { "BG1. Burp of Grom: in melee -> ONE cast",
      function(b) return { caster(b, BG, M) }, { block(b + 5, SW, 0, 3, M) }, {} end, "burp_of_grom", BG, 1, 0, nil },
    { "MC1. Groundbreaker: in melee, ours 100 m away -> ONE cast",
      function(b) return { caster(b, GB, M), ours(b + 1, 0, 100) }, { block(b + 5, SW, 0, -8, M) }, {} end,
      "groundbreaker", GB, 1, 0, nil },
    { "MC2. Groundbreaker: our Swordsmen 15 m away (inside 10 + 10 m) -> no cast",
      function(b) return { caster(b, GB, M), ours(b + 1, 0, 15) }, { block(b + 5, SW, 0, -8, M) }, {} end,
      "groundbreaker", GB, 0, nil, nil },
    { "MC3. Groundbreaker: not in melee -> no cast",
      function(b) return { caster(b, GB) }, { block(b + 5, SW, 0, -8) }, {} end, "groundbreaker", GB, 0, nil, nil },
    { "FD1. Emberstorm: flying over an enemy block -> ONE cast",
      function(b) return { caster(b, EM) }, { block(b + 5, SW, 0, 3) }, {}, {}, true end, "emberstorm", EM, 1, 0, nil },
    { "FD2. Emberstorm: landed over the same block -> no cast",
      function(b) return { caster(b, EM) }, { block(b + 5, SW, 0, 3) }, {}, {}, false end, "emberstorm", EM, 0, nil, nil },
    { "FD3. Emberstorm: flying, the enemy 40 m away -> no cast",
      function(b) return { caster(b, EM) }, { block(b + 5, SW, 0, 40) }, {}, {}, true end, "emberstorm", EM, 0, nil, nil },
    { "FD4. Emberstorm: flying over the enemy, our Swordsmen 15 m away -> no cast",
      function(b) return { caster(b, EM), ours(b + 1, 0, -15) }, { block(b + 5, SW, 0, 3) }, {}, {}, true end,
      "emberstorm", EM, 0, nil, nil },
    { "LS1. Necrotic Explosion: 8% health in melee -> ONE cast",
      function(b) return { caster(b, NE, { melee = true, hp_frac = 0.08 }) }, { block(b + 5, SW, 0, -8, M) }, {} end,
      "necrotic_explosion", NE, 1, 0, nil },
    { "LS2. Necrotic Explosion: 50% health in melee -> no cast",
      function(b) return { caster(b, NE, { melee = true, hp_frac = 0.5 }) }, { block(b + 5, SW, 0, -8, M) }, {} end,
      "necrotic_explosion", NE, 0, nil, nil },
    { "LS3. Necrotic Explosion: 8% in melee, our Swordsmen 20 m away (inside 25 m) -> no cast",
      function(b) return { caster(b, NE, { melee = true, hp_frac = 0.08 }), ours(b + 1, 0, 20) },
        { block(b + 5, SW, 0, -8, M) }, {} end, "necrotic_explosion", NE, 0, nil, nil },
    { "SG1. Deathmaster's Sigil: a Vampire on the ground, none of ours near -> ONE cast at it",
      function(b) return { caster(b, SG) }, { single(b + 5, VA, 0, 100, "com") }, { [tostring(b + 5)] = 900 } end,
      "deathmasters_sigil", SG, 1, 0, 5 },
    { "SG2. Deathmaster's Sigil: the Vampire flying -> no cast",
      function(b) return { caster(b, SG) }, { single(b + 5, VA, 0, 100, "com") }, { [tostring(b + 5)] = 900 },
        { [tostring(b + 5)] = true } end, "deathmasters_sigil", SG, 0, nil, nil },
    { "SG3. Deathmaster's Sigil: our Swordsmen 12 m from the Vampire (inside 25 m) -> no cast",
      function(b) return { caster(b, SG), ours(b + 1, 0, 80) }, { single(b + 5, VA, 0, 100, "com") },
        { [tostring(b + 5)] = 900 } end, "deathmasters_sigil", SG, 0, nil, nil },
    { "SL1. Slann Gold: a Vampire (900) and Grave Guard (1500) -> ONE cast at the Vampire",
      function(b) return { caster(b, SL) }, { single(b + 5, VA, 0, 100, "com"), block(b + 6, GG, 60, 100) },
        { [tostring(b + 5)] = 900, [tostring(b + 6)] = 1500 } end, "slann_gold", SL, 1, 0, 5 },
    { "FS1. Frost Dragon Scale: Grave Guard 15 m away, standing -> ONE cast at it",
      function(b) return { caster(b, FS, { dist = 15 }) }, { block(b + 5, GG, 0, 30, { dist = 15 }) },
        { [tostring(b + 5)] = 800 } end, "frost_dragon_scale", FS, 1, 0, 5 },
    { "HF1. Heaven's Flash: an enemy in melee -> ONE cast",
      function(b) return { caster(b, HF, { dist = 30 }) }, { block(b + 5, SW, 0, 40, { melee = true, dist = 30 }) },
        {} end, "heavens_flash", HF, 1, 0, nil },
    { "SS1. Slime Smoothie: the caster at 60% -> ONE cast",
      function(b) return { caster(b, SS, { hp_frac = 0.6 }) }, {}, {} end, "slime_smoothie", SS, 1, 0, nil },
    { "SB1. Maneater Smoke Bomb: in melee -> ONE cast",
      function(b) return { caster(b, SB, M) }, { block(b + 5, SW, 0, -8, M) }, {} end,
      "maneater_smoke_bomb", SB, 1, 0, nil },
    { "VV1. Verminous Valour: wavering -> ONE cast",
      function(b) return { caster(b, VV, { wavering = true }) }, {}, {} end, "verminous_valour", VV, 1, 0, nil },
  }
  for _, f in ipairs(FILES) do
    local TAG = f.tag
    for i, w in ipairs(WORLDS) do
      local want = w[5]
      if RED158 then want = w[6] end
      if want ~= nil then
        local b = 21000 + i * 20
        local units, enemies, sv, efly, selffly = w[2](b)
        local W = world(w[1], units, enemies, w[3], w[4], f.path, TAG, sv, efly, selffly)
        if W ~= nil then
          local got, tid = 0, nil
          for _, x in ipairs(W.fires) do
            if x.key == w[4] then
              got = got + 1
              if tid == nil then pcall(function() tid = tostring(x.target:unique_ui_id()) end) end
            end
          end
          -- a ground-form cast (Slime Smoothie) lands in W.ground_fires
          for _, x in ipairs(W.ground_fires or {}) do
            if x.key == w[4] then got = got + 1 end
          end
          local a = (got == want)
          local ttxt = ""
          if want > 0 and not RED158 and w[7] ~= nil then
            a = a and tid == tostring(b + w[7])
            ttxt = ", target " .. tostring(tid) .. " want " .. tostring(b + w[7])
          end
          check(TAG .. w[1]:sub(1, 3) .. (RED158 and "-RED" or "") .. "a: " .. want .. " cast(s) expected, got " .. got
            .. ttxt, a)
          done(a)
          tally(W)
        end
      end
    end
  end
  if RED158 then
    check("RED CONTROL (harness 158): the pre-159 build has none of group E - " .. n_ok .. "/" .. n_all,
      n_all == 22 and n_ok == 22)
  else
    check("HARNESS 158: every world behaved - " .. n_ok .. "/" .. n_all, n_all == 40 and n_ok == 40)
  end
  print("== HARNESS 158 done: " .. (checks - pre158) .. " checks in this section ==")
end
