
-- ============================================================================
-- HARNESS 151 (round 152).
--   NH1 Soporific: the Zombie Dragon 200 m away, Grave Guard in range: ONE cast
--   at the Grave Guard (no whole-map hold any more).
--   FL1 Soporific: a FLYING Zombie Dragon and Grave Guard both in range: ONE cast
--   at the Grave Guard (large first never takes a flying target).
--   AN1 Fireball (prefer-central, not a breath): two equal Grave Guard blocks,
--   one facing the caster (listed first), one side-on: the SIDE-ON one.
--   TI1 Foe-Seeker, defaults ON, no click, the unit Tired: ONE cast.
--   AP1 the ALL badge sits at offset (-880, 8), bottom-centre docked.
--   RED (pre-152): NH1 silent (held), FL1 hits the flying dragon, AN1 hits the
--   facing block, TI1 silent (not a default family), AP1 at the old off-screen
--   offset.
-- ============================================================================
function run_h151()
  local L151 = os.getenv("H151_LIVE") or LIVE
  local A151 = os.getenv("H151_ANN") or ANN
  local RED151 = (os.getenv("H151_LIVE") ~= nil) or (os.getenv("H151_ANN") ~= nil)
  local SO = "wh2_main_unit_abilities_soporific_breath"
  local FB = "wh_main_spell_bound_fireball"
  local FS = "wh_main_character_abilities_foe_seeker"
  local BH = "wh2_main_item_abilities_book_of_hoeth"
  local RF = "wh_main_weapon_abilities_runefang"
  local CASTER = "wh2_dlc13_emp_cha_huntsmen_general_0"
  local GG = "wh_main_vmp_inf_grave_guard_0"
  local ZD = "wh3_dlc29_vmp_mon_zombie_dragon"
  local pre151 = checks

  print("== HARNESS 151 - section 0zx: the round-152 tokens ==")
  if not RED151 then
    for _, f in ipairs({ { name = "live", path = L151 }, { name = "ann", path = A151 } }) do
      local s = read_file(f.path)
      check("0zx " .. f.name .. ": no hold, fliers skipped, 90 degrees for every central attack, tired armed, the ALL spot",
        raw_find(s, "blob_large_hold", 1, true) == nil
        and raw_find(s, "function FOURTH.blob_not_flying(u)", 1, true) ~= nil
        and raw_find(s, "and FOURTH.blob_not_flying(e.unit) then", 1, true) ~= nil
        and raw_find(s, "if shot ~= nil and (shot[5] == 1 or shot[6] == 1) then", 1, true) ~= nil
        and raw_find(s, "\ttired = true,", 1, true) ~= nil
        and raw_find(s, "FOURTH.ALL_OX, FOURTH.ALL_OY = -880, 8", 1, true) ~= nil)
    end
  end

  local FILES = { { path = A151, tag = "[annotated] " }, { path = L151, tag = "[live] " } }
  local n_ok, n_all = 0, 0
  local function done(ok) n_all = n_all + 1; if ok then n_ok = n_ok + 1 end end
  local function our_unit(W, uid)
    for _, u in ipairs(W.mock_units or {}) do
      local ok, id = pcall(function() return u:unique_ui_id() end)
      if ok and tostring(id) == tostring(uid) then return u end
    end
    return nil
  end
  local function world(wname, units, enemies, arm, key, PATH, TAG, opts)
    opts = opts or {}
    local cards = {}
    for _, d in ipairs(units) do cards[#cards + 1] = { id = tostring(d.uid), state = "active", vis = true } end
    local W = make_world({ can_perform = true, units = units, enemies = enemies, cards = cards,
      bar = { { id = "b1", key = key } } })
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
        local fl = (opts.flying ~= nil and opts.flying[id] == true)
        pr.unit.is_currently_flying = function(self) return fl end
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
    { "NH1. Soporific: the dragon 200 m away, Grave Guard in range -> ONE cast at the Grave Guard (no hold)",
      function(b) return { caster(b, SO, { dist_by_target = { [b + 5] = 40, [b + 6] = 200 } }) },
        { block(b + 5, GG, 120, 0, 60), dragon(b + 6, 0, 260) },
        { sv = { [tostring(b + 5)] = 850, [tostring(b + 6)] = 2380 }, fly = true } end,
      "unit_abilities_soporific_breath", SO, 1, 0, 5, nil },
    { "FL1. Soporific: a FLYING dragon and Grave Guard both in range -> ONE cast at the Grave Guard",
      function(b) return { caster(b, SO) }, { block(b + 5, GG, 120, 0, 60), dragon(b + 6, 40, 60) },
        { sv = { [tostring(b + 5)] = 850, [tostring(b + 6)] = 2380 }, fly = true, flying = { [tostring(b + 6)] = true } } end,
      "unit_abilities_soporific_breath", SO, 1, 1, 5, 6 },
    { "AN1. Fireball: a block facing the caster (first) and an equal side-on block -> the SIDE-ON one",
      function(b) return { caster(b, FB) }, { block(b + 5, GG, 120, 0, 150, { bearing = 0 }),
          block(b + 6, GG, 120, 60, 150, { bearing = 112 }) },
        { sv = { [tostring(b + 5)] = 850, [tostring(b + 6)] = 850 } } end,
      "spell_bound_fireball", FB, 1, 1, 6, 5 },
    { "TI1. Foe-Seeker, defaults ON, no click, the unit Tired -> ONE cast",
      function(b) return { caster(b, FS, { dist = 300, fatigue = "threshold_tired" }) }, nil,
        { defaults = true, clicks = 0 } end,
      "foe_seeker", FS, 1, 0, nil, nil },
  }
  for _, f in ipairs(FILES) do
    local TAG = f.tag
    for i, w in ipairs(WORLDS) do
      local want = w[5]
      if RED151 then want = w[6] end
      if want ~= nil then
        local base = 17100 + i * 20
        local units, enemies, opts = w[2](base)
        local W = world(w[1], units, enemies, { base, w[3] }, w[4], f.path, TAG, opts)
        if W ~= nil then
          local got, last = 0, nil
          for _, x in ipairs(W.fires) do if x.key == w[4] then got = got + 1; last = x end end
          local off = RED151 and w[8] or w[7]
          local tid = nil
          if last ~= nil and last.target ~= nil then pcall(function() tid = tostring(last.target:unique_ui_id()) end) end
          local a = (got == want)
          if a and got >= 1 and off ~= nil then a = (tid == tostring(base + off)) end
          check(TAG .. w[1]:sub(1, 3) .. (RED151 and "-RED" or "") .. "a: " .. tostring(want) .. " cast(s) expected, got "
            .. got .. ((off ~= nil) and (" (want target +" .. off .. ", got " .. tostring(tid and (tonumber(tid) - base)) .. ")") or ""), a)
          done(a)
          tally(W)
        end
      end
    end
    -- AP1: the ALL badge's spot
    do
      local b = 17390
      local units = { { name = CASTER, uid = b, owns = { BH, RF }, melee = false, dist = 300 } }
      local W = make_world({ can_perform = true, units = units, cards = { { id = tostring(b), state = "active", vis = true } },
        bar = { { id = "b1", key = BH }, { id = "b2", key = RF } } })
      W.defaults_on = false
      print("== " .. TAG .. "AP1. the ALL badge's spot ==")
      local ok = pcall(load_world, W, f.path)
      check(TAG .. "AP1: the file loads", ok)
      if ok then
        deploy_phases(W); ui(W)
        sel_event(W, b, true); ui(W); ui(W); ui(W)
        local rec = W.badge_records["zz_auto_badge_all"]
        local ox, oy = rec and rec.offset and rec.offset[1], rec and rec.offset and rec.offset[2]
        local a
        if RED151 then
          a = (rec ~= nil and ox ~= -880)
          check(TAG .. "AP1-RED: the pre-152 build puts it elsewhere (" .. tostring(ox) .. ", " .. tostring(oy) .. ")", a)
        else
          a = (rec ~= nil and ox == -880 and oy == 8 and rec.dock == 8)
          check(TAG .. "AP1a: the ALL badge sits at (-880, 8), bottom-centre docked (" .. tostring(ox) .. ", "
            .. tostring(oy) .. ", dock " .. tostring(rec and rec.dock) .. ")", a)
        end
        done(a)
        tally(W)
      end
    end
  end
  if RED151 then
    check("RED CONTROL (harness 151): the pre-152 build holds, takes the flier, ignores the angle for Fireball, keeps "
      .. "Foe-Seeker on M and puts the ALL badge off-screen - " .. n_ok .. "/" .. n_all, n_all == 10 and n_ok == 10)
  else
    check("HARNESS 151: every world behaved - " .. n_ok .. "/" .. n_all, n_all == 10 and n_ok == 10)
  end
  print("== HARNESS 151 done: " .. (checks - pre151) .. " checks in this section ==")
end
