-- ============================================================================
-- HARNESS 170 (round 171): THE SCORE 1-2 REVIEW, ROWS 1-15 AND 21 (user rulings 2026-11-17).
--   0zz19 the six families wired, the two split entries, the nine closed markers absent, the contact table, the
--         fresh-contact tracker called once per poll.
--   AC1 Horn of the Wild Hunt: the caster and 2 allies charging (3 units) -> ONE cast.
--   AC2 Horn: the caster and 1 ally charging (2 units) -> no cast.
--   AC3 Horn: the caster idle, 3 allies that have just made contact -> ONE cast (fresh contact).
--   WA1 Waaagh! (the army-wide key, its own entry): 3 units charging -> ONE cast.
--   UR1 Ursun's Roar (the charge key, its own entry): the caster charging -> ONE cast.
--   UR2 Ursun's Roar: the caster idle, 2 allies within its 24 m aura charging -> ONE cast.
--   RF1 Red Fury: the caster idle, an ally 30 m away charging -> ONE cast, on that ally.
--   RF2 Red Fury: the caster in melee -> ONE cast on itself.
--   SA1 The Rock of Inevitability: the caster idle, a fast enemy moving 15 m away -> ONE cast.
--   SA2 the same enemy HIDDEN -> no cast.
--   WS1 The Wissenland Runefang: the caster in melee -> ONE cast.
--   WL1 Black Staff: winds pool 20, reserve 50, caster at 90% -> ONE cast.
--   WL2 pool 60 -> no cast.   WL3 caster at 40% -> no cast.
--   WJ1 Wand of Jet: idle, ready -> ONE cast (when_ready).
--   CM1 Necrotic Phylactery: in melee with Plaguebearers (contact effect), at full health -> ONE cast.
--   CM2 in melee with Swordsmen (no contact effect) -> no cast.
--   CA2 the cards of the six families.
--   RED (pre-171 = round 170): the moved entries ride their old families (in melee / at 75% health); the new markers
--       do not exist.
-- ============================================================================
function run_h170()
  local L170 = os.getenv("H170_LIVE") or LIVE
  local A170 = os.getenv("H170_ANN") or ANN
  local RED170 = (os.getenv("H170_LIVE") ~= nil) or (os.getenv("H170_ANN") ~= nil)
  local HORN = "wh_dlc05_item_abilities_horn_of_the_wild_hunt"
  local WAAA = "wh_main_character_abilities_waaagh"
  local URS = "wh3_main_character_abilities_ursuns_roar"
  local RF = "wh_main_character_abilities_red_fury"
  local ROCK = "wh3_main_item_abilities_the_rock_of_inevitability"
  local WISS = "wh2_dlc13_weapon_abilities_wissenland_runefang"
  local BS = "wh2_main_spell_bound_black_staff"
  local WJ = "wh_main_item_abilities_wand_of_jet"
  local NP = "wh3_dlc25_item_abilities_necrotic_phylactry"
  local CASTER = "wh2_dlc13_emp_cha_huntsmen_general_0"
  local SW = "wh_main_emp_inf_swordsmen"
  local PB = "wh3_main_nur_inf_plaguebearers_0"
  local pre170 = checks
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1; at = i + #tok
    end
  end

  print("== HARNESS 170 - section 0zz19: the round-171 tokens ==")
  if not RED170 then
    for _, f in ipairs({ { name = "live", path = L170 }, { name = "ann", path = A170 } }) do
      local s = read_file(f.path)
      local closed = 0
      for _, m in ipairs({ "earthing_rod", "hagtree_fetish", "master_of_the_black_arts", "maw_shard", "power_familiar",
                           "watched_by_the_watcher", "sceptre_of_stability", "locus_of_abjuration", "focus_instincts" }) do
        if raw_find(s, 'marker = "' .. m .. '"', 1, true) ~= nil then closed = closed + 1 end
      end
      check("0zz19 " .. f.name .. ": six families wired, two split entries, nine closed, the contact table, the tracker",
        cp(s, "\t{ marker = ") == 939 and closed == 0
        and cp(s, "army_charge = FOURTH.evaluate_army_charge,") == 1 and cp(s, "aura_charge = FOURTH.evaluate_aura_charge,") == 1
        and cp(s, "self_or_ally_charge = FOURTH.evaluate_self_or_ally_charge,") == 1
        and cp(s, "slow_aura = FOURTH.evaluate_slow_aura,") == 1 and cp(s, "winds_low = FOURTH.evaluate_winds_low,") == 1
        and cp(s, "contact_melee = FOURTH.evaluate_contact_melee,") == 1
        and cp(s, 'marker = "ursuns_roar_charge"') == 1 and cp(s, 'marker = "waaagh_army"') == 1
        and cp(s, 'FOURTH.CONTACT_TEXT = "') == 1 and cp(s, "\tpcall(FOURTH.track_melee)") == 1)
    end
  end

  local FILES = { { path = A170, tag = "[annotated] " }, { path = L170, tag = "[live] " } }
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
    if o.winds ~= nil then
      local army = {}
      function army:winds_of_magic_current() return o.winds[1] end
      function army:winds_of_magic_reserve() return o.winds[2] end
      function army:winds_of_magic_remaining_recharge_rate() return 0 end
      W.bm.get_player_army = function() return army end
    end
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
        local vis = not (o.hidden ~= nil and o.hidden[id] == true)
        pr.unit.is_visible_to_alliance = function(self, a) return vis end
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
    local c = { name = CASTER, uid = b, owns = { key }, melee = false, dist = 15, width = 2, men_alive = 1,
                unit_class = "com", hp_frac = 1.0 }
    for k, v in pairs(o or {}) do c[k] = v end
    return c
  end
  local CH = { fast = true, melee = false, target = true, dist = 20 }   -- a unit in its charge window
  local function ally(uid, o)
    local a = { name = SW, uid = uid, owns = {}, melee = false, men_alive = 120, initial_men = 120, unit_class = "inf_mel" }
    for k, v in pairs(o or {}) do a[k] = v end
    return a
  end
  local function enemy(uid, name, o)
    local e = { uid = uid, name = name, melee = false, men_alive = 120, initial_men = 120, unit_class = "inf_mel" }
    for k, v in pairs(o or {}) do e[k] = v end
    return e
  end
  -- name, builder(b) -> units, enemies, opts; marker; key; GREEN casts; RED casts; GREEN target offset (nil = caster)
  local WORLDS = {
    { "AC1. Horn of the Wild Hunt: the caster and 2 allies charging -> ONE cast",
      function(b) return { caster(b, HORN, CH), ally(b + 1, CH), ally(b + 2, CH) } end, "horn_of_the_wild_hunt", HORN, 1, 0 },
    { "AC2. Horn: the caster and 1 ally charging -> no cast",
      function(b) return { caster(b, HORN, CH), ally(b + 1, CH) } end, "horn_of_the_wild_hunt", HORN, 0, 0 },
    { "AC3. Horn: the caster idle, 3 allies that have just made contact -> ONE cast",
      function(b) return { caster(b, HORN), ally(b + 1, { melee = true }), ally(b + 2, { melee = true }),
        ally(b + 3, { melee = true }) } end, "horn_of_the_wild_hunt", HORN, 1, 0 },
    { "WA1. Waaagh! (army-wide key): 3 units charging -> ONE cast",
      function(b) return { caster(b, WAAA, CH), ally(b + 1, CH), ally(b + 2, CH) } end, "waaagh_army", WAAA, 1, 0 },
    { "UR1. Ursun's Roar (charge key): the caster charging -> ONE cast",
      function(b) return { caster(b, URS, CH) } end, "ursuns_roar_charge", URS, 1, 0 },
    { "UR2. Ursun's Roar: the caster idle, 2 allies within 24 m charging -> ONE cast",
      function(b) return { caster(b, URS), ally(b + 1, CH), ally(b + 2, CH) } end, "ursuns_roar_charge", URS, 1, 0 },
    { "RF1. Red Fury: the caster idle, an ally 30 m away charging -> ONE cast on the ally",
      function(b) return { caster(b, RF, { dist = 30 }), ally(b + 1, CH) } end, "red_fury", RF, 1, 0, 1 },
    { "RF2. Red Fury: the caster in melee -> ONE cast on itself",
      function(b) return { caster(b, RF, { melee = true }) } end, "red_fury", RF, 1, 1 },
    { "SA1. The Rock of Inevitability: a fast enemy moving 15 m away -> ONE cast",
      function(b) return { caster(b, ROCK) }, { enemy(b + 5, SW, { moving = true, fast = true }) } end,
      "the_rock_of_inevitability", ROCK, 1, 0 },
    { "SA2. The Rock: the same enemy HIDDEN -> no cast",
      function(b) return { caster(b, ROCK) }, { enemy(b + 5, SW, { moving = true, fast = true }) },
        { hidden = { [tostring(b + 5)] = true } } end, "the_rock_of_inevitability", ROCK, 0, 0 },
    { "WS1. The Wissenland Runefang: the caster in melee -> ONE cast",
      function(b) return { caster(b, WISS, { melee = true }) } end, "wissenland_runefang", WISS, 1, 1 },
    { "WL1. Black Staff: winds pool 20, reserve 50, the caster at 90% -> ONE cast",
      function(b) return { caster(b, BS, { hp_frac = 0.9 }) }, nil, { winds = { 20, 50 } } end, "black_staff", BS, 1, 0 },
    { "WL2. Black Staff: pool 60 -> no cast",
      function(b) return { caster(b, BS, { hp_frac = 0.9 }) }, nil, { winds = { 60, 50 } } end, "black_staff", BS, 0, 0 },
    { "WL3. Black Staff: the caster at 40% -> no cast",
      function(b) return { caster(b, BS, { hp_frac = 0.4 }) }, nil, { winds = { 20, 50 } } end, "black_staff", BS, 0, 0 },
    { "WJ1. Wand of Jet: idle, ready -> ONE cast (when ready)",
      function(b) return { caster(b, WJ) } end, "wand_of_jet", WJ, 1, 0 },
    { "CM1. Necrotic Phylactery: in melee with Plaguebearers, at full health -> ONE cast",
      function(b) return { caster(b, NP, { melee = true, dist = 5 }) }, { enemy(b + 5, PB, { melee = true }) } end,
      "necrotic_phylactry", NP, 1, 0 },
    { "CM2. Necrotic Phylactery: in melee with Swordsmen (no contact effect) -> no cast",
      function(b) return { caster(b, NP, { melee = true, dist = 5 }) }, { enemy(b + 5, SW, { melee = true }) } end,
      "necrotic_phylactry", NP, 0, 0 },
  }
  for _, f in ipairs(FILES) do
    local TAG = f.tag
    for i, w in ipairs(WORLDS) do
      local want = RED170 and w[6] or w[5]
      local b = 35000 + i * 20
      local units, enemies, opts = w[2](b)
      local W = world(w[1], units, enemies, w[3], w[4], f.path, TAG, opts)
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
        local ttxt = ""
        if not RED170 and want > 0 and w[7] ~= nil then
          a = a and tid == tostring(b + w[7])
          ttxt = ", target " .. tostring(tid) .. " want " .. tostring(b + w[7])
        end
        check(TAG .. w[1]:sub(1, 3) .. (RED170 and "-RED" or "") .. "a: " .. want .. " cast(s) expected, got " .. got .. ttxt, a)
        done(a)
        if i == 1 then
          local by = {}
          for _, e in ipairs(W.cap or {}) do by[e.marker] = e.card end
          local c_ok = by.horn_of_the_wild_hunt == "Fires when 3+ of your units charge at once"
            and by.ursuns_roar_charge == "Fires when charging, or when 2+ nearby allies charge"
            and by.red_fury == "Fires on itself or the nearest charging ally, else in melee"
            and by.the_rock_of_inevitability == "Fires in melee, or when a fast enemy comes near"
            and by.black_staff == "Fires when the winds pool is low, above 50% health"
            and by.necrotic_phylactry == "Fires in melee unless wavering, against an enemy with contact effects"
          check(TAG .. "CA2: the cards of the six families (Horn: " .. tostring(by.horn_of_the_wild_hunt) .. ")",
            (RED170 and not c_ok) or (not RED170 and c_ok))
          done((RED170 and not c_ok) or (not RED170 and c_ok))
        end
        tally(W)
      end
    end
  end
  if RED170 then
    check("RED CONTROL (harness 170): the pre-171 build keeps the old families - " .. n_ok .. "/" .. n_all,
      n_all == 36 and n_ok == 36)
  else
    check("HARNESS 170: every check behaved - " .. n_ok .. "/" .. n_all, n_all == 36 and n_ok == 36)
  end
  print("== HARNESS 170 done: " .. (checks - pre170) .. " checks in this section ==")
end
