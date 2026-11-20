-- ============================================================================
-- HARNESS 185 (round 186): WARPSTORM SCROLL AS A DAMAGE DEALER (user 2026-11-20: "No need to enforce single-entity. No
--   need to enforce charge, treat it just as a damage dealer").
--   0zz34 enemy_most_valuable wired, Warpstorm Scroll on it with the flying class.
--   WS2 a FLYING unit of 20 men worth 500, a FLYING hero worth 300, a ground hero worth 900 -> ONE cast at the 20-man
--       flier (RED: the pre-186 build takes the single-entity hero).
--   WS3 only a ground hero -> no cast.
--   CA14 Warpstorm Scroll's card.
--   RED control: H185_LIVE / H185_ANN on docs/backups/round186/pre186_*.lua.
-- ============================================================================
function run_h185()
  local L185 = os.getenv("H185_LIVE") or LIVE
  local A185 = os.getenv("H185_ANN") or ANN
  local RED185 = (os.getenv("H185_LIVE") ~= nil) or (os.getenv("H185_ANN") ~= nil)
  local WS = "wh2_main_item_abilities_warpstorm_scroll"
  local CASTER = "wh2_dlc13_emp_cha_huntsmen_general_0"
  local HERO = "wh2_dlc13_emp_cha_hunter_jorek_grimm_0"
  local HARPY = "wh2_main_def_mon_harpies"
  local pre185 = checks
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1; at = i + #tok
    end
  end
  print("== HARNESS 185 - section 0zz34: the round-186 tokens ==")
  if not RED185 then
    for _, f in ipairs({ { name = "live", path = L185 }, { name = "ann", path = A185 } }) do
      local s = read_file(f.path)
      check("0zz34 " .. f.name .. ": enemy_most_valuable wired; Warpstorm Scroll on it, flying only",
        cp(s, "\tenemy_most_valuable = FOURTH.evaluate_enemy_most_valuable,") == 1
        and cp(s, 'trigger = "enemy_most_valuable"') == 1
        and cp(s, '{ marker = "warpstorm_scroll", name = "Warpstorm Scroll", trigger = "enemy_most_valuable",') == 1
        and cp(s, "wh2_main_item_abilities_warpstorm_scroll\" },\n\t\trange_real = 100,\n\t\ttarget_class = \"flying\",\n") == 1)
    end
  end
  local FILES = { { path = A185, tag = "[annotated] " }, { path = L185, tag = "[live] " } }
  local n_ok, n_all = 0, 0
  local function done(ok) n_all = n_all + 1; if ok then n_ok = n_ok + 1 end end
  local function world(wname, units, enemies, PATH, TAG, o)
    local cards = {}
    for _, d in ipairs(units) do cards[#cards + 1] = { id = tostring(d.uid), state = "active", vis = true } end
    local W = make_world({ can_perform = true, units = units, enemies = enemies or {}, cards = cards,
      bar = { { id = "b1", key = WS } } })
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
        local fly = (o.fly[id] == true)
        local v = o.sv[id]
        pr.unit.is_visible_to_alliance = function(self, a) return true end
        pr.unit.is_currently_flying = function(self) return fly end
        if v ~= nil then pr.unit.strategic_value = function(self) return v end end
      end
    end
    sel_event(W, units[1].uid, true); ui(W); ui(W)
    click(W, "zz_auto_badge_warpstorm_scroll"); ui(W)
    sel_event(W, units[1].uid, false); ui(W)
    W.conflict = true
    polln(W, 4)
    return W
  end
  local function S(t) local r = {} for k, v in pairs(t) do r[tostring(k)] = v end return r end
  local function single(uid, name, x, z, men)
    return { uid = uid, name = name, melee = false, pos = { x, 0, z }, width = 6, men_alive = men, initial_men = men,
             unit_class = (men == 1) and "com" or "inf_mel", dist = 50 }
  end
  local WORLDS = {
    { "WS2. Warpstorm Scroll: a flying 20-man unit worth 500, a flying hero worth 300, a ground hero worth 900 -> ONE cast at the 20-man flier",
      function(b) return { { name = CASTER, uid = b, owns = { WS }, melee = false, dist = 50, health_percent = 100,
          dist_by_target = { [b + 5] = 50, [b + 6] = 50, [b + 7] = 50 } } },
        { single(b + 5, HARPY, 0, 50, 20), single(b + 6, HERO, 20, 50, 1), single(b + 7, HERO, 40, 50, 1) },
        { sv = S({ [b + 5] = 500, [b + 6] = 300, [b + 7] = 900 }), fly = S({ [b + 5] = true, [b + 6] = true }) } end,
      1, 5 },
    { "WS3. Warpstorm Scroll: only a ground hero -> no cast",
      function(b) return { { name = CASTER, uid = b, owns = { WS }, melee = false, dist = 50, health_percent = 100 } },
        { single(b + 5, HERO, 0, 50, 1) }, { sv = S({ [b + 5] = 900 }), fly = {} } end, 0, nil },
  }
  for _, f in ipairs(FILES) do
    local TAG = f.tag
    for i, w in ipairs(WORLDS) do
      local b = 57000 + i * 20
      local units, enemies, o = w[2](b)
      local W = world(w[1], units, enemies, f.path, TAG, o)
      if W ~= nil then
        local got, on_t = 0, 0
        for _, x in ipairs(W.fires) do
          if x.key == WS then
            got = got + 1
            local tid = nil
            pcall(function() tid = tostring(x.target:unique_ui_id()) end)
            if w[4] ~= nil and tid == tostring(b + w[4]) then on_t = on_t + 1 end
          end
        end
        local a, txt
        if RED185 then
          a = (on_t == 0)
          txt = "-REDa: the pre-186 build does not take the multi-model flier (got " .. got .. ", on it " .. on_t .. ")"
        else
          a = (got == w[3]) and (w[3] == 0 or on_t == w[3])
          txt = "a: " .. w[3] .. " cast(s) expected, got " .. got .. ", on target " .. on_t
        end
        check(TAG .. w[1]:sub(1, 3) .. txt, a)
        done(a)
        if i == 1 then
          local by = {}
          for _, e in ipairs(W.cap or {}) do by[e.marker] = e.card end
          local c_ok = by.warpstorm_scroll == "Fires on the most valuable enemy; flying targets only"
          check(TAG .. "CA14: Warpstorm Scroll's card (" .. tostring(by.warpstorm_scroll) .. ")",
            (RED185 and not c_ok) or (not RED185 and c_ok))
          done((RED185 and not c_ok) or (not RED185 and c_ok))
        end
        tally(W)
      end
    end
  end
  if RED185 then
    check("RED CONTROL (harness 185): the pre-186 build keeps Warpstorm Scroll on single entities - " .. n_ok .. "/" .. n_all,
      n_all == 6 and n_ok == 6)
  else
    check("HARNESS 185: every check behaved - " .. n_ok .. "/" .. n_all, n_all == 6 and n_ok == 6)
  end
  print("== HARNESS 185 done: " .. (checks - pre185) .. " checks in this section ==")
end
