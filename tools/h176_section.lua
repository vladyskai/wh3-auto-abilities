-- ============================================================================
-- HARNESS 176 (round 177): THE SCORE-3 REVIEW, ROWS 1-22 (user, 2026-11-18: "Implement all until item 22, except the
--   number 3"). The caster idles unless stated; enemies and allies are placed by distance.
--   0zz25 the 9 new families wired and ridden, the squig set, 15 entries moved, Daemonshield unchanged.
--   BO1 Blood Omens: a fast enemy moving 30 m from the caster -> ONE cast (RED: none, it needed melee).
--   CK1 Creature-Killer: the caster fights Swordsmen -> no cast (RED: one, any melee).
--   CK2 Creature-Killer: the caster fights a Terrorgheist -> ONE cast.
--   CK3 Creature-Killer: the caster idles, an ally 15 m away fights a Terrorgheist -> ONE cast (RED: none).
--   ES1 Empowering Shrooms: a squig ally in melee 20 m away -> ONE cast on it (RED: none).
--   ES2 Empowering Shrooms: a Swordsmen ally in melee -> no cast.
--   EP1 Everyone Has Their Price: an enemy in melee 15 m away -> ONE cast (RED: none).
--   FU1 Fury of the Land: an ally 20 m away charging -> ONE cast (RED: none).
--   RF1 Refuse to Die: in melee at full health -> no cast (RED: one).   RF2 at 20% -> ONE cast.
--   RO1 Rune of Oath & Steel: under missile fire, not in melee -> ONE cast (RED: none).
--   AE1 Shield of Aeons: a fast enemy moving 20 m away -> ONE cast (RED: none).
--   SW1 Shielding Swarm: allies under fire, 300 at 20 m and 900 at 40 m -> ONE cast on the 900 (RED: none).
--   SL1 Slayer for Chaos: in melee at full health -> no cast (RED: one).   SL2 in melee at 8% -> ONE cast.
--   OR1 The Ostermark Runefang: the caster fights Swordsmen -> no cast (RED: one).
--   BP1 The Blood Price: in melee at 40% -> no cast (RED: one).   BP2 in melee at 90% -> ONE cast.
--   CA5 the cards of four new families.
-- ============================================================================
function run_h176()
  local L176 = os.getenv("H176_LIVE") or LIVE
  local A176 = os.getenv("H176_ANN") or ANN
  local RED176 = (os.getenv("H176_LIVE") ~= nil) or (os.getenv("H176_ANN") ~= nil)
  local K = {
    BO = "wh3_dlc29_unit_abilities_blood_omens", CK = "wh2_dlc16_weapon_abilities_creature_killer",
    ES = "wh3_dlc26_character_abilities_empowering_shrooms", EP = "wh3_main_lord_abilities_everyone_has_their_price",
    FL = "wh3_dlc24_character_abilities_fury_of_the_land", RD = "wh2_dlc12_unit_abilities_refuse_to_die",
    RO = "wh_main_rune_abilities_rune_of_oath_and_steel", SA = "wh2_dlc13_item_abilities_shield_of_aeons",
    SS = "wh3_dlc29_hero_active_dispatch_the_swarm_protect", SC = "wh3_dlc23_item_abilities_slayer_for_chaos",
    OR = "wh2_dlc13_weapon_abilities_ostermark_runefang", BP = "wh2_dlc14_lord_abilities_the_blood_price",
  }
  local CASTER = "wh2_dlc13_emp_cha_huntsmen_general_0"
  local SW = "wh_main_emp_inf_swordsmen"
  local TG = "wh_main_vmp_mon_terrorgheist"
  local SQ = "wh_dlc06_grn_inf_squig_herd_0"
  local pre176 = checks
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1; at = i + #tok
    end
  end
  print("== HARNESS 176 - section 0zz25: the round-177 tokens ==")
  if not RED176 then
    local NEWF = { "slow_army", "melee_vs_large", "ally_squig_melee", "enemy_melee_near", "aura_charge_or_melee",
      "melee_health25", "guard_aura", "self_or_ally_fire_melee", "melee_healthy" }
    for _, f in ipairs({ { name = "live", path = L176 }, { name = "ann", path = A176 } }) do
      local s = read_file(f.path)
      local wired = 0
      for _, fam in ipairs(NEWF) do
        if cp(s, fam .. " = FOURTH.evaluate_" .. fam .. ",") == 1 and cp(s, 'trigger = "' .. fam .. '"') >= 1 then
          wired = wired + 1
        end
      end
      check("0zz25 " .. f.name .. ": 9 families wired and ridden (" .. wired .. "), the squig set, Daemonshield unchanged",
        wired == 9 and cp(s, 'FOURTH.SQUIG_TEXT = "') == 1 and cp(s, "-- ROUND 177 (score-3 review): ") == 15
        and cp(s, '{ marker = "daemonshield", name = "Daemonshield", trigger = "melee_unwavering",') == 1)
    end
  end

  local FILES = { { path = A176, tag = "[annotated] " }, { path = L176, tag = "[live] " } }
  local n_ok, n_all = 0, 0
  local function done(ok) n_all = n_all + 1; if ok then n_ok = n_ok + 1 end end
  local function world(wname, units, enemies, marker, key, PATH, TAG, sv)
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
      if pr ~= nil and pr.unit ~= nil then pr.unit.is_visible_to_alliance = function(self, a) return true end end
    end
    for i = 1, #(W.live_entries or {}) do
      local pr = W.live_entries[i]
      local id = nil
      pcall(function() id = tostring(pr.unit:unique_ui_id()) end)
      if sv ~= nil and sv[id] ~= nil then
        local v = sv[id]
        pr.unit.strategic_value = function(self) return v end
      end
    end
    sel_event(W, units[1].uid, true); ui(W); ui(W)
    click(W, "zz_auto_badge_" .. marker); ui(W)
    sel_event(W, units[1].uid, false); ui(W)
    W.conflict = true
    polln(W, 3)
    return W
  end
  local function caster(b, key, o)
    local c = { name = CASTER, uid = b, owns = { key }, melee = false, dist = 30, width = 2, men_alive = 1,
                unit_class = "com", hp_frac = 1.0 }
    for k, v in pairs(o or {}) do c[k] = v end
    return c
  end
  local function ally(uid, name, o)
    local a = { name = name, uid = uid, owns = {}, melee = false, men_alive = 120, initial_men = 120, unit_class = "inf_mel" }
    for k, v in pairs(o or {}) do a[k] = v end
    return a
  end
  local function enemy(uid, name, o)
    local e = { uid = uid, name = name, melee = false, men_alive = 120, initial_men = 120, unit_class = "inf_mel" }
    for k, v in pairs(o or {}) do e[k] = v end
    return e
  end
  local CH = { fast = true, melee = false, target = true, dist = 20 }
  local function S(t) local r = {} for k, v in pairs(t) do r[tostring(k)] = v end return r end
  -- name; builder(b) -> units, enemies, sv; marker; key; GREEN casts; RED casts; GREEN target offset (nil: any)
  local WORLDS = {
    { "BO1. Blood Omens: a fast enemy moving 30 m away -> ONE cast",
      function(b) return { caster(b, K.BO) }, { enemy(b + 5, SW, { moving = true, fast_speed = 8 }) } end,
      "blood_omens", K.BO, 1, 0 },
    { "CK1. Creature-Killer: the caster fights Swordsmen -> no cast",
      function(b) return { caster(b, K.CK, { melee = true, dist = 5 }) }, { enemy(b + 5, SW, { melee = true }) } end,
      "creature_killer", K.CK, 0, 1 },
    { "CK2. Creature-Killer: the caster fights a Terrorgheist -> ONE cast",
      function(b) return { caster(b, K.CK, { melee = true, dist = 5 }) },
        { enemy(b + 5, TG, { melee = true, men_alive = 1, initial_men = 1, unit_class = "mon" }) } end,
      "creature_killer", K.CK, 1, 1 },
    { "CK3. Creature-Killer: an ally 15 m away fights a Terrorgheist -> ONE cast",
      function(b) return { caster(b, K.CK, { dist_by_target = { [b + 1] = 15, [b + 5] = 60 } }),
        ally(b + 1, SW, { melee = true, dist = 5 }) },
        { enemy(b + 5, TG, { melee = true, men_alive = 1, initial_men = 1, unit_class = "mon" }) } end,
      "creature_killer", K.CK, 1, 0 },
    { "ES1. Empowering Shrooms: a squig ally in melee 20 m away -> ONE cast on it",
      function(b) return { caster(b, K.ES), ally(b + 1, SQ, { melee = true, dist = 20 }) } end,
      "empowering_shrooms", K.ES, 1, 0, 1 },
    { "ES2. Empowering Shrooms: a Swordsmen ally in melee -> no cast",
      function(b) return { caster(b, K.ES), ally(b + 1, SW, { melee = true, dist = 20 }) } end,
      "empowering_shrooms", K.ES, 0, 0 },
    { "EP1. Everyone Has Their Price: an enemy in melee 15 m away -> ONE cast",
      function(b) return { caster(b, K.EP, { dist = 15 }) }, { enemy(b + 5, SW, { melee = true }) } end,
      "everyone_has_their_price", K.EP, 1, 0 },
    { "FU1. Fury of the Land: an ally 20 m away charging -> ONE cast",
      function(b) return { caster(b, K.FL, { dist = 20 }), ally(b + 1, SW, CH) } end,
      "fury_of_the_land", K.FL, 1, 0 },
    { "RF1. Refuse to Die: in melee at full health -> no cast",
      function(b) return { caster(b, K.RD, { melee = true }) } end, "refuse_to_die", K.RD, 0, 1 },
    { "RF2. Refuse to Die: in melee at 20% -> ONE cast",
      function(b) return { caster(b, K.RD, { melee = true, hp_frac = 0.2 }) } end, "refuse_to_die", K.RD, 1, 1 },
    { "RO1. Rune of Oath & Steel: under missile fire, not in melee -> ONE cast",
      function(b) return { caster(b, K.RO, { missile = true }) } end, "rune_of_oath_and_steel", K.RO, 1, 0 },
    { "AE1. Shield of Aeons: a fast enemy moving 20 m away -> ONE cast",
      function(b) return { caster(b, K.SA, { dist = 20 }) }, { enemy(b + 5, SW, { moving = true, fast_speed = 8 }) } end,
      "shield_of_aeons", K.SA, 1, 0 },
    { "SW1. Shielding Swarm: allies under fire, 300 at 20 m and 900 at 40 m -> ONE cast on the 900",
      function(b) return { caster(b, K.SS), ally(b + 1, SW, { missile = true, dist = 20 }),
        ally(b + 2, SW, { missile = true, dist = 40 }) }, nil, S({ [b + 1] = 300, [b + 2] = 900 }) end,
      "dispatch_the_swarm_protect", K.SS, 1, 0, 2 },
    { "SL1. Slayer for Chaos: in melee at full health -> no cast",
      function(b) return { caster(b, K.SC, { melee = true }) } end, "slayer_for_chaos", K.SC, 0, 1 },
    { "SL2. Slayer for Chaos: in melee at 8% -> ONE cast",
      function(b) return { caster(b, K.SC, { melee = true, hp_frac = 0.08 }) } end, "slayer_for_chaos", K.SC, 1, 1 },
    { "OR1. The Ostermark Runefang: the caster fights Swordsmen -> no cast",
      function(b) return { caster(b, K.OR, { melee = true, dist = 5 }) }, { enemy(b + 5, SW, { melee = true }) } end,
      "ostermark_runefang", K.OR, 0, 1 },
    { "BP1. The Blood Price: in melee at 40% -> no cast",
      function(b) return { caster(b, K.BP, { melee = true, hp_frac = 0.4 }) } end, "the_blood_price", K.BP, 0, 1 },
    { "BP2. The Blood Price: in melee at 90% -> ONE cast",
      function(b) return { caster(b, K.BP, { melee = true, hp_frac = 0.9 }) } end, "the_blood_price", K.BP, 1, 1 },
  }
  for _, f in ipairs(FILES) do
    local TAG = f.tag
    for i, w in ipairs(WORLDS) do
      local want = RED176 and w[6] or w[5]
      local b = 40000 + i * 20
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
        for _, x in ipairs(W.ground_fires or {}) do if x.key == w[4] then got = got + 1 end end
        local a = (got == want)
        local txt = ""
        if not RED176 and want > 0 and w[7] ~= nil then
          a = a and tid == tostring(b + w[7])
          txt = ", target " .. tostring(tid) .. " want " .. tostring(b + w[7])
        end
        check(TAG .. w[1]:sub(1, 3) .. (RED176 and "-RED" or "") .. "a: " .. want .. " cast(s) expected, got " .. got .. txt, a)
        done(a)
        if i == 1 then
          local by = {}
          for _, e in ipairs(W.cap or {}) do by[e.marker] = e.card end
          local c_ok = by.blood_omens == "Fires when an enemy charges your army, or in melee"
            and by.creature_killer == "Fires when it or a nearby ally fights a large enemy"
            and by.refuse_to_die == "Fires in melee at 25% health or less"
            and by.shield_of_aeons == "Fires in melee, under fire, or when an enemy charges in"
          check(TAG .. "CA5: the cards of four new families (Blood Omens: " .. tostring(by.blood_omens) .. ")",
            (RED176 and not c_ok) or (not RED176 and c_ok))
          done((RED176 and not c_ok) or (not RED176 and c_ok))
        end
        tally(W)
      end
    end
  end
  if RED176 then
    check("RED CONTROL (harness 176): the pre-177 build keeps the old triggers - " .. n_ok .. "/" .. n_all,
      n_all == 38 and n_ok == 38)
  else
    check("HARNESS 176: every check behaved - " .. n_ok .. "/" .. n_all, n_all == 38 and n_ok == 38)
  end
  print("== HARNESS 176 done: " .. (checks - pre176) .. " checks in this section ==")
end
