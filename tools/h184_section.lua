-- ============================================================================
-- HARNESS 184 (round 185): THE RULE-SHUT REVIEW, ROWS 20-64 (user 2026-11-20: "Review ended, implement pls"; rulings
--   from the Claude Docs review, rev 127).
--   0zz33 the 33 entries on their families, the 2 new families wired, the 30-men floor, the 2 ground keys, the
--         bombardment radius of the Immolation rune, the holds and wind-ups.
--   MU1 Venom Wave: in melee -> ONE cast (RED: none).
--   MC1 Glacial Blast: in melee, our Swordsmen 15 m away (inside 15 + 10) -> no cast.
--   MC2 Glacial Blast: in melee, none of ours near -> ONE cast (RED: none).
--   LS1 Master Rune of Immolation: in melee at 8% health -> ONE cast (its 10 m bombardment; RED: none).
--   LS2 Master Rune of Immolation: in melee at 50% health -> no cast.
--   AC1 Battle Howl: the caster idle, an ally 30 m away charging (inside 38 m) -> ONE cast (RED: none).
--   AC2 Silver Horn of Vengeance: an ally 30 m away charging (beyond 24 m) -> no cast.
--   OF1 Offering to the Gods: allies in melee worth 600 (120 men) and 900 (20 men) -> ONE cast at the 600 (RED: none).
--   FG1 Fog of the Damned: a FLYING enemy in melee worth 2,000, a pair in melee 8 m apart worth 500 each -> ONE ground
--       cast under the pair (RED: none).
--   MK1 Mirror of Knowledge: a fast enemy 300 m from the caster, 30 m from our ally -> ONE ground cast (unbounded; RED:
--       none).
--   BG1 The Black Gem of Gnar: in melee at 8% health -> ONE cast (RED: none).
--   LC1 Locus of Contagion: an enemy in melee 30 m away (inside 38 m) -> ONE cast (RED: none).
--   TH1 Twilight Horn II: the caster idle, an ally 20 m away charging -> ONE cast on it (RED: none). (The mock reads
--       an ally's dist field as both its gap to the caster and its gap to its own target.)
--   BZ1 Beastlord's Gaze: an ally in melee and wavering, 100 m away -> ONE cast on it (RED: none).
--   SN1 Seismic Snare: in melee -> ONE cast (RED: none).
--   IT1 Swiftness of Itzl: the caster charging -> ONE cast (RED: none).
--   CA13 the cards of Battle Howl, Offering to the Gods, Fog of the Damned and the Immolation rune.
--   RED control: H184_LIVE / H184_ANN on docs/backups/round185/pre185_*.lua.
-- ============================================================================
function run_h184()
  local L184 = os.getenv("H184_LIVE") or LIVE
  local A184 = os.getenv("H184_ANN") or ANN
  local RED184 = (os.getenv("H184_LIVE") ~= nil) or (os.getenv("H184_ANN") ~= nil)
  local K = {
    VW = "wh2_dlc09_lord_abilities_venom_wave", GB = "wh3_main_character_abilities_glacial_blast",
    MR = "wh2_dlc17_rune_abilities_master_rune_of_immolation", BH = "wh3_dlc29_spell_bound_prayer_battle_howl",
    SH = "wh_main_item_abilities_silver_horn_of_vengeance", OF = "wh3_dlc27_lord_abilities_offering_to_the_gods",
    FG = "wh3_dlc29_bound_deep_fog_of_the_damned", MK = "wh3_dlc24_item_abilities_mirror_of_knowledge",
    BG = "wh3_dlc23_item_abilities_black_gem_of_gnar", LC = "wh3_main_character_abilities_locus_of_contagion",
    TH = "wh2_dlc16_item_abilities_twilight_horn_ii", BZ = "wh2_twa03_lord_abilities_beastlords_gaze",
    SN = "wh2_dlc14_unit_abilities_seismic_snare", IT = "wh2_main_character_abilities_swiftness_of_itzl",
  }
  local CASTER = "wh2_dlc13_emp_cha_huntsmen_general_0"
  local SW = "wh_main_emp_inf_swordsmen"
  local ZOMBIE = "wh_main_vmp_inf_zombie"
  local CH = { fast = true, melee = false, target = true }   -- a unit in its charge window
  local pre184 = checks
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1; at = i + #tok
    end
  end
  print("== HARNESS 184 - section 0zz33: the round-185 entries ==")
  if not RED184 then
    local ENT = {
      { "alakanash", "melee_unwavering" }, { "ark_of_sotek", "melee_unwavering" }, { "celestial_sweep", "melee_unwavering" },
      { "prayer_destruction", "melee_unwavering" }, { "eruption", "melee_unwavering" },
      { "ferocious_destruction", "melee_unwavering" }, { "kill_for_khorne", "melee_unwavering" },
      { "sonic_boom", "melee_unwavering" }, { "hammer_of_harry", "melee_unwavering" }, { "venom_wave", "melee_unwavering" },
      { "wrath_of_ptra", "melee_unwavering" }, { "whirlwind_of_death", "melee_unwavering" },
      { "whirlwind_of_death_upgraded", "melee_unwavering" }, { "glacial_blast", "melee_clear" },
      { "thundermace", "melee_clear" }, { "cellular_instability", "melee_clear_block" },
      { "splode_da_big_one", "last_stand_clear" }, { "battle_howl_hounds", "aura_charge_only" },
      { "battle_howl", "aura_charge_only" }, { "twilight_horn_ii", "self_or_ally_charge" },
      { "silver_horn_of_vengeance", "aura_charge_only" }, { "swiftness_of_itzl", "charge_only" },
      { "bonecrusher", "enemy_blob_vortex" }, { "master_rune_of_immolation", "last_stand_clear" },
      { "beastlords_gaze", "ally_melee_risk" }, { "fog_of_the_damned", "enemy_ground_melee_cluster" },
      { "locus_of_contagion", "enemy_melee_near" }, { "mad_cap_mushrooms", "self_recharging" },
      { "mirror_of_knowledge", "enemy_fast_near_ally" }, { "offering_to_the_gods", "ally_offering" },
      { "seismic_snare", "slow_aura" }, { "seismic_snare_stormfiend", "slow_aura" }, { "black_gem_of_gnar", "self_last_stand" },
    }
    for _, f in ipairs({ { name = "live", path = L184 }, { name = "ann", path = A184 } }) do
      local s = read_file(f.path)
      local got = 0
      for _, e in ipairs(ENT) do
        local i = raw_find(s, '{ marker = "' .. e[1] .. '", name = "', 1, true)
        if i ~= nil and cp(s, '{ marker = "' .. e[1] .. '", ') == 1
          and raw_find(s:sub(i, i + 140), 'trigger = "' .. e[2] .. '",', 1, true) ~= nil then
          got = got + 1
        end
      end
      local wired = 0
      for _, fam in ipairs({ "aura_charge_only", "ally_offering" }) do
        if cp(s, "\t" .. fam .. " = FOURTH.evaluate_" .. fam .. ",") == 1 then wired = wired + 1 end
      end
      check("0zz33 " .. f.name .. ": 33 entries on their families (" .. got .. "), 2 families wired (" .. wired
        .. "), the 30-men floor, the 2 ground keys, the rune's 10 m bombardment, Mirror unbounded",
        got == 33 and wired == 2 and cp(s, "\nFOURTH.OFFERING_MIN_MEN = 30") == 1
        and cp(s, "-- ROUND 185 (rule-shut review row ") == 33
        and cp(s, '\t\t["wh3_dlc29_bound_deep_fog_of_the_damned"] = true,\n') == 1
        and cp(s, '\t\t["wh3_dlc24_item_abilities_mirror_of_knowledge"] = true,\n') == 1
        and cp(s, "wh2_dlc17_rune_abilities_master_rune_of_immolation=10;") == 1
        and cp(s, "wh3_dlc24_item_abilities_mirror_of_knowledge\" },\n\t\tunbounded = true,\n") == 1)
    end
  end
  local FILES = { { path = A184, tag = "[annotated] " }, { path = L184, tag = "[live] " } }
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
    if o.osv ~= nil then
      for uid, v in pairs(o.osv) do
        local u = unit_of(W, uid)
        if u ~= nil then u.strategic_value = function(self) return v end end
      end
    end
    sel_event(W, units[1].uid, true); ui(W); ui(W)
    click(W, "zz_auto_badge_" .. marker); ui(W)
    sel_event(W, units[1].uid, false); ui(W)
    W.conflict = true
    polln(W, o.polls or 4)
    return W
  end
  local function own(b, key, o)
    local c = { name = CASTER, uid = b, owns = { key }, melee = false, dist = 30, health_percent = 100, pos = { 0, 0, 0 },
                width = 2, men_alive = 1, initial_men = 1, unit_class = "com" }
    for k, v in pairs(o or {}) do c[k] = v end
    return c
  end
  local function ally(uid, o)
    local a = { name = SW, uid = uid, owns = {}, melee = false, dist = 30, health_percent = 100, in_range = true,
                men_alive = 120, initial_men = 120, unit_class = "inf_mel" }
    for k, v in pairs(o or {}) do a[k] = v end
    return a
  end
  local function block(uid, x, z, o)
    local e = { uid = uid, name = ZOMBIE, melee = false, pos = { x, 0, z }, width = 20, men_alive = 80, initial_men = 80,
                unit_class = "inf_mel", dist = 30 }
    for k, v in pairs(o or {}) do e[k] = v end
    return e
  end
  local function S(t) local r = {} for k, v in pairs(t) do r[tostring(k)] = v end return r end
  local function M(t) local r = {} for k, v in pairs(t) do r[k] = v end return r end
  -- { name, builder -> units, enemies, o; marker; key; casts expected; target ("uN" a unit, "gNM.." a ground under N/M) }
  local WORLDS = {
    { "MU1. Venom Wave: in melee -> ONE cast",
      function(b) return { own(b, K.VW, { melee = true }) }, { block(b + 5, 0, 3, { melee = true, dist = 1 }) } end,
      "venom_wave", K.VW, 1, nil },
    { "MC1. Glacial Blast: in melee, our Swordsmen 15 m away -> no cast",
      function(b) return { own(b, K.GB, { melee = true }), ally(b + 1, { pos = { 0, 0, 15 }, width = 10 }) },
        { block(b + 5, 0, -3, { melee = true, dist = 1 }) } end, "glacial_blast", K.GB, 0, nil },
    { "MC2. Glacial Blast: in melee, none of ours near -> ONE cast",
      function(b) return { own(b, K.GB, { melee = true }) }, { block(b + 5, 0, -3, { melee = true, dist = 1 }) } end,
      "glacial_blast", K.GB, 1, nil },
    { "LS1. Master Rune of Immolation: in melee at 8% health -> ONE cast",
      function(b) return { own(b, K.MR, { melee = true, health_percent = 8 }) },
        { block(b + 5, 0, 3, { melee = true, dist = 1 }) } end, "master_rune_of_immolation", K.MR, 1, nil },
    { "LS2. Master Rune of Immolation: in melee at 50% health -> no cast",
      function(b) return { own(b, K.MR, { melee = true, health_percent = 50 }) },
        { block(b + 5, 0, 3, { melee = true, dist = 1 }) } end, "master_rune_of_immolation", K.MR, 0, nil },
    { "AC1. Battle Howl: the caster idle, an ally 30 m away charging -> ONE cast",
      function(b) local a = M(CH); a.dist = 20 return { own(b, K.BH, { dist_by_target = { [b + 1] = 30 } }), ally(b + 1, a) } end,
      "battle_howl", K.BH, 1, nil },
    { "AC2. Silver Horn of Vengeance: an ally 30 m away charging (beyond 24 m) -> no cast",
      function(b) local a = M(CH); a.dist = 20 return { own(b, K.SH, { dist_by_target = { [b + 1] = 30 } }), ally(b + 1, a) } end,
      "silver_horn_of_vengeance", K.SH, 0, nil },
    { "OF1. Offering to the Gods: allies in melee worth 600 (120 men) and 900 (20 men) -> ONE cast at the 600",
      function(b) return { own(b, K.OF), ally(b + 5, { melee = true, dist = 30 }),
        ally(b + 6, { melee = true, dist = 30, men_alive = 20, initial_men = 20 }) },
        {}, { osv = { [b + 5] = 600, [b + 6] = 900 } } end, "offering_to_the_gods", K.OF, 1, "u5" },
    { "FG1. Fog of the Damned: a FLYING enemy in melee worth 2000, a pair in melee worth 500 each -> ONE ground cast under the pair",
      function(b) return { own(b, K.FG, { dist_by_target = { [b + 5] = 60, [b + 6] = 40, [b + 7] = 40 } }) },
        { block(b + 5, 60, 30, { melee = true, dist_by_target = { [b + 6] = 40, [b + 7] = 40 } }),
          block(b + 6, 0, 40, { melee = true, dist_by_target = { [b + 5] = 40, [b + 7] = 8 } }),
          block(b + 7, 10, 40, { melee = true, dist_by_target = { [b + 5] = 40, [b + 6] = 8 } }) },
        { sv = S({ [b + 5] = 2000, [b + 6] = 500, [b + 7] = 500 }), fly = S({ [b + 5] = true }) } end,
      "fog_of_the_damned", K.FG, 1, "g67" },
    { "MK1. Mirror of Knowledge: a fast enemy 300 m from the caster, 30 m from our ally -> ONE ground cast",
      function(b) return { own(b, K.MK, { dist = 300 }), ally(b + 1, { dist = 30 }) },
        { { name = "enemy_cavalry", uid = b + 5, melee = false, moving = true, fast_speed = 7, dist = 30 } } end,
      "mirror_of_knowledge", K.MK, 1, "g5" },
    { "BG1. The Black Gem of Gnar: in melee at 8% health -> ONE cast",
      function(b) return { own(b, K.BG, { melee = true, health_percent = 8 }) },
        { block(b + 5, 0, 3, { melee = true, dist = 1 }) } end, "black_gem_of_gnar", K.BG, 1, nil },
    { "LC1. Locus of Contagion: an enemy in melee 30 m away -> ONE cast",
      function(b) return { own(b, K.LC, { dist_by_target = { [b + 5] = 30 } }),
        ally(b + 1, { melee = true, pos = { 0, 0, 35 } }) },
        { block(b + 5, 0, 35, { melee = true, dist = 30 }) } end, "locus_of_contagion", K.LC, 1, nil },
    { "TH1. Twilight Horn II: the caster idle, an ally 20 m away charging -> ONE cast on it",
      function(b) return { own(b, K.TH), ally(b + 5, (function() local t = M(CH); t.dist = 20 return t end)()) } end,
      "twilight_horn_ii", K.TH, 1, "u5" },
    { "BZ1. Beastlord's Gaze: an ally in melee and wavering, 100 m away -> ONE cast on it",
      function(b) return { own(b, K.BZ), ally(b + 5, { melee = true, wavering = true, dist = 100 }) } end,
      "beastlords_gaze", K.BZ, 1, "u5" },
    { "SN1. Seismic Snare: in melee -> ONE cast",
      function(b) return { own(b, K.SN, { melee = true }) }, { block(b + 5, 0, 3, { melee = true, dist = 1 }) } end,
      "seismic_snare", K.SN, 1, nil },
    { "IT1. Swiftness of Itzl: the caster charging -> ONE cast",
      function(b) local c = own(b, K.IT, M(CH)); c.dist = 20 return { c } end, "swiftness_of_itzl", K.IT, 1, nil },
  }
  for _, f in ipairs(FILES) do
    local TAG = f.tag
    for i, w in ipairs(WORLDS) do
      local b = 55000 + i * 20
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
        if RED184 then
          a = (got == 0)
          txt = "-REDa: the pre-185 build has no entry, got " .. got
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
          local c_ok = by.battle_howl == "%CARD_BH%" and by.offering_to_the_gods == "%CARD_OF%"
            and by.fog_of_the_damned == "%CARD_FG%" and by.master_rune_of_immolation == "%CARD_MR%"
          check(TAG .. "CA13: the cards (" .. tostring(by.battle_howl) .. " | " .. tostring(by.offering_to_the_gods)
            .. " | " .. tostring(by.fog_of_the_damned) .. " | " .. tostring(by.master_rune_of_immolation) .. ")",
            (RED184 and not c_ok) or (not RED184 and c_ok))
          done((RED184 and not c_ok) or (not RED184 and c_ok))
        end
        tally(W)
      end
    end
  end
  if RED184 then
    check("RED CONTROL (harness 184): the pre-185 build has none of the 33 entries - " .. n_ok .. "/" .. n_all,
      n_all == 34 and n_ok == 34)
  else
    check("HARNESS 184: every check behaved - " .. n_ok .. "/" .. n_all, n_all == 34 and n_ok == 34)
  end
  print("== HARNESS 184 done: " .. (checks - pre184) .. " checks in this section ==")
end
