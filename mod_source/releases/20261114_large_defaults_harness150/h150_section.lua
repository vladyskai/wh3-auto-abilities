
-- ============================================================================
-- HARNESS 150 (round 151).
--   Soporific / Sun Dragon's Breath: 5 m blast, bound 56 m, prefer-central,
--   breaths, the game forbids them grounded or in melee (the caster flies).
--   LG1 a Zombie Dragon (large, value 2380) and a Grave Guard block both in
--   range: Soporific goes at the ZOMBIE DRAGON (large first).
--   LG2 the Zombie Dragon out of range (200 m), Grave Guard in range: no cast
--   (the hold: the dragon would lose more value).
--   LG3 only Grave Guard: one cast at it.
--   UG1 the caster is GROUNDED, Grave Guard in range: no cast (usage rule).
--   BR1 Sun Dragon's Breath, two equal Grave Guard blocks: one facing the
--   caster (listed first), one side-on: the cast goes at the SIDE-ON block.
--   DF1 Book of Hoeth with the defaults ON and no click: one cast.
--   DF2 Runefang in melee, defaults ON, no click: one cast.
--   DF3 Runefang in melee, defaults ON, ONE click (switches it off): none.
--   DF4 Fireball (not a default family), defaults ON, no click: none.
--   AB1 the ALL badge: created once; a click arms Book of Hoeth and Runefang on
--   the selected unit (letters A, both cast); a second click disarms (letters M).
--   RED (pre-151): LG1 hits the Grave Guard, LG2 and UG1 cast, BR1 hits the
--   facing block, DF1 / DF2 stay silent, AB1 has no ALL badge.
-- ============================================================================
function run_h150()
  local L150 = os.getenv("H150_LIVE") or LIVE
  local A150 = os.getenv("H150_ANN") or ANN
  local RED150 = (os.getenv("H150_LIVE") ~= nil) or (os.getenv("H150_ANN") ~= nil)
  local SO = "wh2_main_unit_abilities_soporific_breath"
  local SU = "wh2_main_unit_abilities_sun_dragons_breath"
  local FB = "wh_main_spell_bound_fireball"
  local BH = "wh2_main_item_abilities_book_of_hoeth"
  local RF = "wh_main_weapon_abilities_runefang"
  local CASTER = "wh2_dlc13_emp_cha_huntsmen_general_0"
  local GG = "wh_main_vmp_inf_grave_guard_0"
  local ZD = "wh3_dlc29_vmp_mon_zombie_dragon"
  local pre150 = checks
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1; at = i + #tok
    end
  end

  print("== HARNESS 150 - section 0zw: the round-151 tokens ==")
  if not RED150 then
    for _, f in ipairs({ { name = "live", path = L150 }, { name = "ann", path = A150 } }) do
      local s = read_file(f.path)
      check("0zw " .. f.name .. ": large first + hold, usage rules, breaths at 90, the defaults, the ALL badge, the tables",
        raw_find(s, "function FOURTH.blob_pick_large(unit, m, r, key)", 1, true) ~= nil
        and raw_find(s, "function FOURTH.blob_large_hold(m, key, inf_value)", 1, true) ~= nil
        and raw_find(s, "function FOURTH.blob_usage_ok(unit, key)", 1, true) ~= nil
        and raw_find(s, "FOURTH.BREATH_VALUE_BAND = 0.8 ", 1, true) ~= nil
        and raw_find(s, "FOURTH.DEFAULT_ON_TRIGGERS = {", 1, true) ~= nil
        and raw_find(s, "and ZZ_AUTO_TEST_NO_DEFAULTS ~= true", 1, true) ~= nil
        and raw_find(s, 'FOURTH.ALL_BADGE_ID = "zz_auto_badge_all"', 1, true) ~= nil
        and cp(s, "pcall(FOURTH.all_badge_tick)") == 1
        and raw_find(s, "wh2_main_unit_abilities_soporific_breath=15,63,27,0,1,1,1,1;", 1, true) ~= nil
        and raw_find(s, "wh3_dlc29_vmp_mon_zombie_dragon=90,8236;", 1, true) ~= nil)
    end
  end

  local FILES = { { path = A150, tag = "[annotated] " }, { path = L150, tag = "[live] " } }
  local n_ok, n_all = 0, 0
  local function done(ok) n_all = n_all + 1; if ok then n_ok = n_ok + 1 end end
  local function our_unit(W, uid)
    for _, u in ipairs(W.mock_units or {}) do
      local ok, id = pcall(function() return u:unique_ui_id() end)
      if ok and tostring(id) == tostring(uid) then return u end
    end
    return nil
  end
  -- opts: sv (uid -> value), fly (our caster flying), defaults (W.defaults_on), clicks (badge clicks), bar (keys)
  local function world(wname, units, enemies, arm, key, PATH, TAG, opts)
    opts = opts or {}
    local cards = {}
    for _, d in ipairs(units) do cards[#cards + 1] = { id = tostring(d.uid), state = "active", vis = true } end
    local bar = {}
    for i, k in ipairs(opts.bar or { key }) do bar[#bar + 1] = { id = "b" .. i, key = k } end
    local W = make_world({ can_perform = true, units = units, enemies = enemies, cards = cards, bar = bar })
    W.defaults_on = (opts.defaults == true)
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
        if opts.sv ~= nil and opts.sv[id] ~= nil then
          local v = opts.sv[id]
          pr.unit.strategic_value = function(self) return v end
        end
      end
    end
    if opts.fly ~= nil then
      local u = our_unit(W, arm[1])
      if u ~= nil then
        local f = opts.fly
        u.is_currently_flying = function(self) return f end
      end
    end
    sel_event(W, arm[1], true); ui(W); ui(W)
    for _ = 1, (opts.clicks or 1) do click(W, "zz_auto_badge_" .. arm[2]); ui(W) end
    sel_event(W, arm[1], false); ui(W)
    W.conflict = true
    polln(W, 4)
    return W
  end
  local function caster(b, key, extra)
    local c = { name = CASTER, uid = b, owns = { key }, melee = false, dist = 40, pos = { 0, 0, 0 }, width = 2,
                men_alive = 1, unit_class = "com" }
    for k, v in pairs(extra or {}) do c[k] = v end
    return c
  end
  local function block(uid, name, men, x, z, extra)
    local e = { uid = uid, name = name, melee = false, pos = { x, 0, z }, width = 29.4, men_alive = men,
                initial_men = men, unit_class = "inf_mel" }
    for k, v in pairs(extra or {}) do e[k] = v end
    return e
  end
  local function dragon(uid, x, z)
    return { uid = uid, name = ZD, melee = false, pos = { x, 0, z }, width = 3.5, men_alive = 1, initial_men = 1,
             unit_class = "inf_mel", hp_frac = 1.0 }
  end
  -- name, builder(b) -> units, enemies, opts; marker; key; GREEN casts; RED casts; GREEN target; RED target
  local WORLDS = {
    { "LG1. Soporific: a Zombie Dragon and a Grave Guard block both in range -> ONE cast at the DRAGON",
      function(b) return { caster(b, SO) }, { block(b + 5, GG, 120, 0, 60), dragon(b + 6, 40, 60) },
        { sv = { [tostring(b + 5)] = 850, [tostring(b + 6)] = 2380 }, fly = true } end,
      "unit_abilities_soporific_breath", SO, 1, 1, 6, 5 },
    { "LG2. Soporific: the dragon is 200 m away, Grave Guard in range -> no cast (the hold)",
      function(b) return { caster(b, SO, { dist_by_target = { [b + 5] = 40, [b + 6] = 200 } }) },
        { block(b + 5, GG, 120, 0, 60), dragon(b + 6, 0, 260) },
        { sv = { [tostring(b + 5)] = 850, [tostring(b + 6)] = 2380 }, fly = true } end,
      "unit_abilities_soporific_breath", SO, 0, 1, nil, 5 },
    { "LG3. Soporific: only Grave Guard in range -> ONE cast at it",
      function(b) return { caster(b, SO) }, { block(b + 5, GG, 120, 0, 60) },
        { sv = { [tostring(b + 5)] = 850 }, fly = true } end,
      "unit_abilities_soporific_breath", SO, 1, nil, 5, nil },
    { "UG1. Soporific: the caster is GROUNDED, Grave Guard in range -> no cast (the game's usage rule)",
      function(b) return { caster(b, SO) }, { block(b + 5, GG, 120, 0, 60) },
        { sv = { [tostring(b + 5)] = 850 }, fly = false } end,
      "unit_abilities_soporific_breath", SO, 0, 1, nil, 5 },
    { "BR1. Sun Dragon's Breath: a block facing the caster (first) and an equal side-on block -> the SIDE-ON one",
      function(b) return { caster(b, SU) }, { block(b + 5, GG, 120, 0, 150, { bearing = 0 }),
          block(b + 6, GG, 120, 60, 150, { bearing = 112 }) },
        { sv = { [tostring(b + 5)] = 850, [tostring(b + 6)] = 850 }, fly = true } end,
      "unit_abilities_sun_dragons_breath", SU, 1, 1, 6, 5 },
    { "DF1. Book of Hoeth, defaults ON, no click -> ONE cast",
      function(b) return { caster(b, BH, { dist = 300 }) }, nil, { defaults = true, clicks = 0 } end,
      "book_of_hoeth", BH, 1, 0, nil, nil },
    { "DF2. Runefang in melee, defaults ON, no click -> ONE cast",
      function(b) return { caster(b, RF, { melee = true, dist = 300 }) }, nil, { defaults = true, clicks = 0 } end,
      "runefang", RF, 1, 0, nil, nil },
    { "DF3. Runefang in melee, defaults ON, ONE click (switches it OFF) -> no cast",
      function(b) return { caster(b, RF, { melee = true, dist = 300 }) }, nil, { defaults = true, clicks = 1 } end,
      "runefang", RF, 0, nil, nil, nil },
    { "DF4. Fireball (not a default family), defaults ON, no click -> no cast",
      function(b) return { caster(b, FB) }, { block(b + 5, GG, 120, 0, 60) },
        { defaults = true, clicks = 0, sv = { [tostring(b + 5)] = 850 } } end,
      "spell_bound_fireball", FB, 0, nil, nil, nil },
  }
  for _, f in ipairs(FILES) do
    local TAG = f.tag
    for i, w in ipairs(WORLDS) do
      local want = w[5]
      if RED150 then want = w[6] end
      if want ~= nil then
        local base = 16700 + i * 20
        local units, enemies, opts = w[2](base)
        local W = world(w[1], units, enemies, { base, w[3] }, w[4], f.path, TAG, opts)
        if W ~= nil then
          local got, last = 0, nil
          for _, x in ipairs(W.fires) do if x.key == w[4] then got = got + 1; last = x end end
          local off = RED150 and w[8] or w[7]
          local tid = nil
          if last ~= nil and last.target ~= nil then pcall(function() tid = tostring(last.target:unique_ui_id()) end) end
          local a = (got == want)
          if a and got >= 1 and off ~= nil then a = (tid == tostring(base + off)) end
          check(TAG .. w[1]:sub(1, 3) .. (RED150 and "-RED" or "") .. "a: " .. tostring(want) .. " cast(s) expected, got "
            .. got .. ((off ~= nil) and (" (want target +" .. off .. ", got " .. tostring(tid and (tonumber(tid) - base)) .. ")") or ""), a)
          done(a)
          tally(W)
        end
      end
    end
    -- AB1: the ALL badge
    do
      local b = 16990
      local units = { { name = CASTER, uid = b, owns = { BH, RF }, melee = true, dist = 300 } }
      local cards = { { id = tostring(b), state = "active", vis = true } }
      local W = make_world({ can_perform = true, units = units, cards = cards,
        bar = { { id = "b1", key = BH }, { id = "b2", key = RF } } })
      W.defaults_on = false
      print("== " .. TAG .. "AB1. the ALL badge ==")
      local ok = pcall(load_world, W, f.path)
      check(TAG .. "AB1: the file loads", ok)
      if ok then
        deploy_phases(W); ui(W)
        sel_event(W, b, true); ui(W); ui(W); ui(W)
        local made = (W.all_badge_created or 0)
        if RED150 then
          check(TAG .. "AB1-RED: the pre-151 build makes no ALL badge (" .. made .. ")", made == 0)
          done(made == 0)
        else
          check(TAG .. "AB1a: the ALL badge was created once (" .. made .. ")", made == 1)
          done(made == 1)
          click(W, "zz_auto_badge_all"); ui(W); ui(W)
          local lb = W.badge_records["zz_auto_badge_book_of_hoeth"]
          local lr = W.badge_records["zz_auto_badge_runefang"]
          local a = (lb ~= nil and lb.text == "A" and lr ~= nil and lr.text == "A")
          check(TAG .. "AB1b: one click armed both abilities (letters " .. tostring(lb and lb.text) .. " / "
            .. tostring(lr and lr.text) .. ")", a)
          done(a)
          -- the unit stays selected: a second click disarms both, a third arms both again
          click(W, "zz_auto_badge_all"); ui(W); ui(W)
          a = (lb ~= nil and lb.text == "M" and lr ~= nil and lr.text == "M")
          check(TAG .. "AB1c: a second click disarmed both (letters " .. tostring(lb and lb.text) .. " / "
            .. tostring(lr and lr.text) .. ")", a)
          done(a)
          click(W, "zz_auto_badge_all"); ui(W); ui(W)
          sel_event(W, b, false); ui(W)
          W.conflict = true
          polln(W, 16)
          local nb, nr = 0, 0
          for _, x in ipairs(W.fires) do
            if x.key == BH then nb = nb + 1 end
            if x.key == RF then nr = nr + 1 end
          end
          a = (nb >= 1 and nr >= 1)
          check(TAG .. "AB1d: after a third click both fire (Book of Hoeth " .. nb .. ", Runefang " .. nr
            .. "; one unit casts one ability per wind-up window)", a)
          done(a)
        end
        tally(W)
      end
    end
  end
  if RED150 then
    check("RED CONTROL (harness 150): the pre-151 build ignores large targets, the usage rule, the 90-degree preference, "
      .. "the defaults and the ALL badge - " .. n_ok .. "/" .. n_all, n_all == 14 and n_ok == 14)
  else
    check("HARNESS 150: every world behaved - " .. n_ok .. "/" .. n_all, n_all == 26 and n_ok == 26)
  end
  print("== HARNESS 150 done: " .. (checks - pre150) .. " checks in this section ==")
end
