-- ============================================================================
-- HARNESS 166 (round 167): NO FINAL PERIOD, AND THE SAFER DEFAULTS (user rulings 2026-11-17).
--   0zz14 the round-167 tokens in both files: the RISKY table and its loader, the default rule, the bare return,
--         the ALL text without a period.
--   NP1 no card ends with '.' (946 / 946).
--   SD1 no entry with a risky key starts armed (the 15 in armed families); the others in those families still do.
--   RK1 Fury of Khaine (rampage, ally_melee_buff), no badge click, in melee with an ally -> no cast.
--   RK2 Fury of Khaine, ONE badge click (the player arms it) -> ONE cast.
--   RK3 Favour of the Fay (same family, not risky), no badge click -> ONE cast (the family still starts armed).
--   RK4 Witchbrew (rampage, melee_unwavering), no badge click, in melee -> no cast.
--   RED (pre-167 = round 166): cards end with '.', 15 risky entries start armed, RK1 and RK4 cast, RK2's click
--       switches it OFF (no cast).
-- ============================================================================
function run_h166()
  local L166 = os.getenv("H166_LIVE") or LIVE
  local A166 = os.getenv("H166_ANN") or ANN
  local RED166 = (os.getenv("H166_LIVE") ~= nil) or (os.getenv("H166_ANN") ~= nil)
  local FK = "wh2_main_unit_abilities_fury_of_khaine"
  local FAY = "wh_dlc07_lord_abilities_favour_of_the_fay"
  local WB = "wh2_main_character_abilities_witchbrew"
  local CASTER = "wh_dlc07_brt_cha_prophetess_life_0"
  local SW = "wh_main_emp_inf_swordsmen"
  local pre166 = checks
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1; at = i + #tok
    end
  end

  print("== HARNESS 166 - section 0zz14: the round-167 tokens ==")
  if not RED166 then
    for _, f in ipairs({ { name = "live", path = L166 }, { name = "ann", path = A166 } }) do
      local s = read_file(f.path)
      check("0zz14 " .. f.name .. ": the RISKY table and loader, the default rule, the bare return, the ALL text",
        cp(s, 'FOURTH.RISKY_TEXT = "') == 1 and cp(s, "function FOURTH.entry_risky(ability)") == 1
        and cp(s, "\t\tand not FOURTH.entry_risky(ability)   -- ROUND 167") == 1
        and cp(s, 'wh2_main_unit_abilities_fury_of_khaine=R;') == 1
        and cp(s, 'wh2_dlc15_unit_abilities_rock_bottom=D;') == 1
        and cp(s, '\treturn table.concat(parts, "; ")   -- ROUND 166') == 1
        and cp(s, 'FOURTH.ALL_TIP = "Arm or disarm every automatic ability of the selected unit(s)"\n') == 1)
    end
  end

  local FILES = { { path = A166, tag = "[annotated] " }, { path = L166, tag = "[live] " } }
  local n_ok, n_all = 0, 0
  local function done(ok) n_all = n_all + 1; if ok then n_ok = n_ok + 1 end end
  local function world(wname, key, marker, clicks, PATH, TAG, b)
    local units = {
      { name = CASTER, uid = b, owns = { key }, melee = true, dist = 2, pos = { 0, 0, 0 }, width = 2, men_alive = 1,
        unit_class = "com" },
      { name = SW, uid = b + 1, owns = {}, melee = true, dist = 20, pos = { 0, 0, 20 }, width = 29.4, men_alive = 120,
        initial_men = 120, unit_class = "inf_mel" } }
    local cards = { { id = tostring(b), state = "active", vis = true }, { id = tostring(b + 1), state = "active", vis = true } }
    local W = make_world({ can_perform = true, units = units, enemies = {}, cards = cards,
      bar = { { id = "b1", key = key } } })
    W.defaults_on = true
    print("== " .. TAG .. wname .. " ==")
    W.bm.get_player_alliance = function() return "OUR_ALLIANCE" end
    OH77.cap = nil
    local ok = pcall(load_world, W, PATH)
    check(TAG .. wname .. ": the file loads", ok)
    if not ok then tally(W); return nil end
    W.cap = OH77.cap
    deploy_phases(W); ui(W)
    sel_event(W, b, true); ui(W); ui(W)
    for _ = 1, clicks do click(W, "zz_auto_badge_" .. marker); ui(W) end
    sel_event(W, b, false); ui(W)
    W.conflict = true
    polln(W, 4)
    return W
  end
  -- name, key, marker, clicks, GREEN casts, RED casts
  local WORLDS = {
    { "RK1. Fury of Khaine (rampage), no badge click, in melee with an ally -> no cast", FK, "fury_of_khaine", 0, 0, 1 },
    { "RK2. Fury of Khaine, one badge click (the player arms it) -> ONE cast", FK, "fury_of_khaine", 1, 1, 0 },
    { "RK3. Favour of the Fay (same family, not risky), no badge click -> ONE cast", FAY, "favour_of_the_fay", 0, 1, 1 },
    { "RK4. Witchbrew (rampage, melee_unwavering), no badge click, in melee -> no cast", WB, "witchbrew", 0, 0, 1 },
  }
  for _, f in ipairs(FILES) do
    local TAG = f.tag
    for i, w in ipairs(WORLDS) do
      local want = RED166 and w[6] or w[5]
      local W = world(w[1], w[2], w[3], w[4], f.path, TAG, 31000 + i * 20)
      if W ~= nil then
        local got = 0
        for _, x in ipairs(W.fires) do if x.key == w[2] then got = got + 1 end end
        for _, x in ipairs(W.ground_fires or {}) do if x.key == w[2] then got = got + 1 end end
        local a = (got == want)
        check(TAG .. w[1]:sub(1, 3) .. (RED166 and "-RED" or "") .. "a: " .. want .. " cast(s) expected, got " .. got, a)
        done(a)
        if i == 1 then
          -- NP1 / SD1 from the captured ABILITIES table (defaults on in this world)
          local cap = W.cap or {}
          local dot, total, risky_on, armed_left = 0, 0, 0, 0
          for _, e in ipairs(cap) do
            total = total + 1
            if type(e.card) == "string" and e.card:sub(-1) == "." then dot = dot + 1 end
            local risky = false
            for _, k in ipairs(e.keys or {}) do
              if k == FK or k == WB or k == "wh2_dlc15_unit_abilities_rock_bottom" or k == "wh3_dlc29_lord_abilities_verminous_fury"
                or k == "wh2_dlc14_lord_abilities_the_blood_price" or k == "wh2_main_spell_bound_black_staff" then risky = true end
            end
            if risky and e.default_on == true then risky_on = risky_on + 1 end
            if e.default_on == true then armed_left = armed_left + 1 end
          end
          local np = (total == 946 and dot == 0)
          check(TAG .. "NP1: no card ends with a period (" .. dot .. " of " .. total .. " do)",
            (RED166 and dot == 946) or (not RED166 and np))
          done((RED166 and dot == 946) or (not RED166 and np))
          local rd = (risky_on == 0 and armed_left > 400)
          check(TAG .. "SD1: Fury of Khaine, Witchbrew, Rock Bottom, Verminous Fury, The Blood Price and Black Staff start on M; "
            .. armed_left .. " entries still start armed (risky armed " .. risky_on .. ")",
            (RED166 and risky_on > 0) or (not RED166 and rd))
          done((RED166 and risky_on > 0) or (not RED166 and rd))
        end
        tally(W)
      end
    end
  end
  if RED166 then
    check("RED CONTROL (harness 166): the pre-167 build ends cards with a period and arms the risky abilities - "
      .. n_ok .. "/" .. n_all, n_all == 12 and n_ok == 12)
  else
    check("HARNESS 166: every check behaved - " .. n_ok .. "/" .. n_all, n_all == 12 and n_ok == 12)
  end
  print("== HARNESS 166 done: " .. (checks - pre166) .. " checks in this section ==")
end
