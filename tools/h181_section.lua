-- ============================================================================
-- HARNESS 181 (round 182): THE FINISHERS (the last review's row 23 and section 7; user rulings 2026-11-17 / 2026-11-20).
--   0zz30 the 2 new families wired, the 90% fraction and the Executioner's field, the execute ranking, Skjalandir moved.
--   EX1 Executioner: two heroes at 30% (worth 300) and 80% (worth 900) -> ONE cast at the 30% one (RED: not it).
--   EX2 Executioner: a hero at 40%, 210 m away (inside 225 m, beyond the old 175 m) -> ONE cast (RED: none).
--   EX3 Executioner: our Swordsmen 5 m from the only hero -> no cast (RED: none).
--   EE1 The Emperor's Executioner: Lords at 5% (worth 900) and 15% (worth 300), both below the 20% line -> ONE cast at
--       the 15% one (RED: not it, the old pick was the most valuable).
--   SF1 Skjalandir's Fall: shooting at a target NOT in melee -> ONE cast (every hit blinds; RED: none).
--   CA10 the cards of the Executioner, the Emperor's Executioner and Skjalandir's Fall.
--   RED control: H181_LIVE / H181_ANN on docs/backups/round182/pre182_*.lua.
-- ============================================================================
function run_h181()
  local L181 = os.getenv("H181_LIVE") or LIVE
  local A181 = os.getenv("H181_ANN") or ANN
  local RED181 = (os.getenv("H181_LIVE") ~= nil) or (os.getenv("H181_ANN") ~= nil)
  local K = {
    EX = "wh2_dlc13_lord_abilities_executioner", EE = "wh3_dlc24_lord_abilities_the_emperors_executioner",
    SF = "wh3_dlc23_character_abilities_skjalandirs_fall",
  }
  local CASTER = "wh2_dlc13_emp_cha_huntsmen_general_0"
  local HERO = "wh2_dlc13_emp_cha_hunter_jorek_grimm_0"
  local SW = "wh_main_emp_inf_swordsmen"
  local UL = "wh3_dlc23_neu_cha_ulrika"
  local pre181 = checks
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1; at = i + #tok
    end
  end
  print("== HARNESS 181 - section 0zz30: the round-182 tokens ==")
  if not RED181 then
    for _, f in ipairs({ { name = "live", path = L181 }, { name = "ann", path = A181 } }) do
      local s = read_file(f.path)
      local wired = 0
      for _, fam in ipairs({ "enemy_finisher", "melee_or_self_shooting" }) do
        if cp(s, fam .. " = FOURTH.evaluate_" .. fam .. ",") == 1 and cp(s, 'trigger = "' .. fam .. '"') == 1 then
          wired = wired + 1
        end
      end
      check("0zz30 " .. f.name .. ": 2 families wired (" .. wired .. "), the 90% fraction, the execute ranking, Skjalandir moved",
        wired == 2 and cp(s, "\nFOURTH.SINGLE_RANGE_FRACTION = 0.90") == 1 and cp(s, "\t\trange_frac = 0.90,\n") == 1
        and cp(s, 'elseif kind == "finisher" then') == 1 and cp(s, 'trigger = "melee_or_shooting_into_melee"') == 0
        and cp(s, "\t\t\ts1 = FOURTH.enemy_health_pct(e.unit) or 0\n") == 1)
    end
  end
  local FILES = { { path = A181, tag = "[annotated] " }, { path = L181, tag = "[live] " } }
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
        pr.unit.is_visible_to_alliance = function(self, a) return true end
        pr.unit.is_currently_flying = function(self) return false end
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
  local function caster(b, key, o)
    local c = { name = CASTER, uid = b, owns = { key }, melee = false, dist = 30, health_percent = 100, pos = { 0, 0, 0 },
                width = 2, unit_class = "com" }
    for k, v in pairs(o or {}) do c[k] = v end
    return c
  end
  local function hero(uid, x, z, o)
    local e = { uid = uid, name = HERO, melee = false, pos = { x, 0, z }, width = 2, men_alive = 1, initial_men = 1,
                unit_class = "com", dist = 30 }
    for k, v in pairs(o or {}) do e[k] = v end
    return e
  end
  local function S(t) local r = {} for k, v in pairs(t) do r[tostring(k)] = v end return r end
  local WORLDS = {
    { "EX1. Executioner: heroes at 30% (worth 300) and 80% (worth 900) -> ONE cast at the 30% one",
      function(b) return { caster(b, K.EX, { dist_by_target = { [b + 5] = 100, [b + 6] = 100 } }) },
        { hero(b + 5, 0, 100, { hp_frac = 0.30 }), hero(b + 6, 60, 100, { hp_frac = 0.80 }) },
        { sv = S({ [b + 5] = 300, [b + 6] = 900 }) } end, "lord_abilities_executioner", K.EX, 1, "u5", "nottarget" },
    { "EX2. Executioner: a hero at 40%, 210 m away -> ONE cast",
      function(b) return { caster(b, K.EX, { dist_by_target = { [b + 5] = 210 } }) },
        { hero(b + 5, 0, 210, { hp_frac = 0.40 }) }, { sv = S({ [b + 5] = 500 }) } end,
      "lord_abilities_executioner", K.EX, 1, "u5", "none" },
    { "EX3. Executioner: our Swordsmen 5 m from the only hero -> no cast",
      function(b) return { caster(b, K.EX, { dist_by_target = { [b + 5] = 100 } }),
        { name = SW, uid = b + 1, owns = {}, melee = false, dist = 30, health_percent = 100, pos = { 0, 0, 92 },
          width = 10, men_alive = 120, unit_class = "inf_mel" } },
        { hero(b + 5, 0, 100, { hp_frac = 0.30 }) }, { sv = S({ [b + 5] = 500 }) } end,
      "lord_abilities_executioner", K.EX, 0, nil, "none" },
    { "EE1. The Emperor's Executioner: Lords at 5% (worth 900) and 15% (worth 300) -> ONE cast at the 15% one",
      function(b) return { caster(b, K.EE, { dist_by_target = { [b + 5] = 20, [b + 6] = 20 } }) },
        { hero(b + 5, 0, 30, { hp_frac = 0.05 }), hero(b + 6, 20, 30, { hp_frac = 0.15 }) },
        { sv = S({ [b + 5] = 900, [b + 6] = 300 }) } end, "emperors_executioner", K.EE, 1, "u6", "nottarget" },
    { "SF1. Skjalandir's Fall: shooting at a target NOT in melee -> ONE cast",
      function(b) return { { name = UL, uid = b, owns = { K.SF }, melee = false, ammo_start = 30, ammo_seq = { 30, 29 },
          ammo_target = { type = "wh_main_vmp_inf_zombie", melee = false } } }, {}, { polls = 20 } end,
      "skjalandirs_fall", K.SF, 1, nil, "none" },
  }
  for _, f in ipairs(FILES) do
    local TAG = f.tag
    for i, w in ipairs(WORLDS) do
      local b = 49000 + i * 20
      local units, enemies, o = w[2](b)
      local W = world(w[1], units, enemies, w[3], w[4], f.path, TAG, o)
      if W ~= nil then
        local got, on_t = 0, 0
        local want = w[6]
        local tuid = want and tostring(b + tonumber(want:sub(2)))
        for _, x in ipairs(W.fires) do
          if x.key == w[4] then
            got = got + 1
            local tid = nil
            pcall(function() tid = tostring(x.target:unique_ui_id()) end)
            if tuid ~= nil and tid == tuid then on_t = on_t + 1 end
          end
        end
        for _, x in ipairs(W.ground_fires or {}) do if x.key == w[4] then got = got + 1 end end
        local a, txt
        if RED181 then
          local rule = w[7]
          if rule == "none" then a = (got == 0)
          elseif rule == "one" then a = (got == 1)
          elseif rule == "nottarget" then a = (on_t == 0)
          else a = (got == w[5] and (want == nil or on_t == w[5])) end
          txt = "-REDa: rule " .. rule .. ", got " .. got .. ", " .. on_t .. " on the new target"
        else
          a = (got == w[5]) and (w[5] == 0 or want == nil or on_t == w[5])
          txt = "a: " .. w[5] .. " cast(s) expected, got " .. got .. ", on target " .. on_t
        end
        check(TAG .. w[1]:sub(1, 3) .. txt, a)
        done(a)
        if i == 1 then
          local by = {}
          for _, e in ipairs(W.cap or {}) do by[e.marker] = e.card end
          local c_ok = by.lord_abilities_executioner == "Fires when standing still, on the most hurt enemy monster or character clear of allies"
            and by.skjalandirs_fall == "Fires in melee unless wavering, or while shooting"
            and by.emperors_executioner ~= nil and raw_find(by.emperors_executioner, "Fires on the healthiest enemy below 20% health", 1, true) == 1
          check(TAG .. "CA10: the cards of the finishers (" .. tostring(by.emperors_executioner) .. ")",
            (RED181 and not c_ok) or (not RED181 and c_ok))
          done((RED181 and not c_ok) or (not RED181 and c_ok))
        end
        tally(W)
      end
    end
  end
  if RED181 then
    check("RED CONTROL (harness 181): the pre-182 build keeps the old triggers - " .. n_ok .. "/" .. n_all,
      n_all == 12 and n_ok == 12)
  else
    check("HARNESS 181: every check behaved - " .. n_ok .. "/" .. n_all, n_all == 12 and n_ok == 12)
  end
  print("== HARNESS 181 done: " .. (checks - pre181) .. " checks in this section ==")
end
