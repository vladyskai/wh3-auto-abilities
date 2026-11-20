-- ============================================================================
-- HARNESS 180 (round 181): LAND MINE (row 98: "A"), SURPRISE SQUIG! (row 28: "implement blob with clearance") and THE
--   RANGE FIXES ("Fix the range mismatches"; user, 2026-11-20).
--   0zz29 the 2 new families wired, the 60-soldier line, the GENERATED summon blast (21 m), the range fixes, 936 entries.
--   LM1 Land Mine: in melee inside a 240-man block, no friend near -> ONE cast (RED: same).
--   LM2 Land Mine: in melee against a 30-man unit -> no cast (60 soldiers needed; RED: one).
--   SQ1 Surprise Squig!: two standing blocks worth 600 and 1,200, none of ours near -> ONE ground cast under the 1,200
--       (RED: none, it needed an enemy in melee).
--   SQ2 Surprise Squig!: our Swordsmen 15 m from the only block -> no cast (the 21 m blast + 10 m).
--   SQ3 Surprise Squig!: the only block is moving -> no cast.
--   RS1 Ravaging Swarm: an enemy in melee 60 m away -> ONE cast (its real 100 m; RED: none, it stopped at 21 m).
--   CK1 Curse of Khsar: an enemy in melee 60 m away -> ONE ground cast (RED: none, it stopped at 24 m).
--   LU1 Lord of Undeath (a 50 m key): an enemy in melee 60 m away -> no cast (35 m bound; RED: one, it used 140 m).
--   LU2 Lord of Undeath (the 200 m key, its own entry): an enemy in melee 60 m away -> ONE cast (RED: none, no such
--       badge before the split).
--   CA9 the cards of Land Mine and Surprise Squig!.
--   RED control: H180_LIVE / H180_ANN on docs/backups/round181/pre181_*.lua.
-- ============================================================================
function run_h180()
  local L180 = os.getenv("H180_LIVE") or LIVE
  local A180 = os.getenv("H180_ANN") or ANN
  local RED180 = (os.getenv("H180_LIVE") ~= nil) or (os.getenv("H180_ANN") ~= nil)
  local K = {
    LM = "wh3_dlc25_unit_abilities_marienburg_land_mines", SQ = "wh3_dlc25_character_abilities_surprise_squig",
    RS = "wh3_dlc29_hero_active_dispatch_the_swarm_attack", CK = "wh2_dlc09_character_abilities_curse_of_khsar",
    LU = "wh_pro03_lord_abilities_lord_of_undeath_0", LU4 = "wh_pro03_lord_abilities_lord_of_undeath_4",
  }
  local CASTER = "wh2_dlc13_emp_cha_huntsmen_general_0"
  local SW = "wh_main_emp_inf_swordsmen"
  local pre180 = checks
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1; at = i + #tok
    end
  end
  print("== HARNESS 180 - section 0zz29: the round-181 tokens ==")
  if not RED180 then
    for _, f in ipairs({ { name = "live", path = L180 }, { name = "ann", path = A180 } }) do
      local s = read_file(f.path)
      local wired = 0
      for _, fam in ipairs({ "melee_clear_block", "enemy_summon_blob" }) do
        if cp(s, fam .. " = FOURTH.evaluate_" .. fam .. ",") == 1 and cp(s, 'trigger = "' .. fam .. '"') == 1 then
          wired = wired + 1
        end
      end
      check("0zz29 " .. f.name .. ": 2 families wired (" .. wired .. "), the 60-soldier line, the 21 m summon blast, the range "
        .. "fixes, 936 entries",
        wired == 2 and cp(s, "\t{ marker = ") == 936 and cp(s, "\nFOURTH.LAND_MINE_MIN_MEN = 60") == 1
        and cp(s, 'FOURTH.SUMMON_BLAST_TEXT = "wh3_dlc25_character_abilities_surprise_squig=21"') == 1
        and cp(s, "-- ROUND 181 (range fix): ") == 5
        and cp(s, '{ marker = "lord_of_undeath_4", name = "Lord of Undeath", trigger = "enemy_ground_melee",') == 1
        and cp(s, 'or FOURTH.SUMMON_BLAST_R[key])') == 1)
    end
  end
  local FILES = { { path = A180, tag = "[annotated] " }, { path = L180, tag = "[live] " } }
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
    polln(W, 4)
    return W
  end
  local function caster(b, key, o)
    local c = { name = CASTER, uid = b, owns = { key }, melee = false, dist = 30, health_percent = 100, pos = { 0, 0, 0 },
                width = 2, unit_class = "com" }
    for k, v in pairs(o or {}) do c[k] = v end
    return c
  end
  local function ours(uid, x, z)
    return { name = SW, uid = uid, owns = {}, melee = false, dist = 30, health_percent = 100, pos = { x, 0, z },
             width = 29.4, men_alive = 120, unit_class = "inf_mel" }
  end
  local function enemy(uid, name, o)
    local e = { uid = uid, name = name, melee = false, pos = { 0, 0, 60 }, width = 29.4, men_alive = 120,
                initial_men = 120, unit_class = "inf_mel", dist = 30 }
    for k, v in pairs(o or {}) do e[k] = v end
    return e
  end
  local function S(t) local r = {} for k, v in pairs(t) do r[tostring(k)] = v end return r end
  -- name; builder(b) -> units, enemies, opts; marker; key; GREEN casts; GREEN target ("uN" unit / "gN" ground under
  -- b+N / nil); RED rule ("none", "one", "nottarget", "same")
  local WORLDS = {
    { "LM1. Land Mine: in melee inside a 240-man block, no friend near -> ONE cast",
      function(b) return { caster(b, K.LM, { melee = true }) },
        { enemy(b + 5, SW, { pos = { 0, 0, 0 }, melee = true, men_alive = 240, initial_men = 240 }) } end,
      "land_mine", K.LM, 1, nil, "same" },
    { "LM2. Land Mine: in melee against a 30-man unit -> no cast",
      function(b) return { caster(b, K.LM, { melee = true }) },
        { enemy(b + 5, SW, { pos = { 0, 0, 0 }, melee = true, men_alive = 30, initial_men = 30, width = 12 }) } end,
      "land_mine", K.LM, 0, nil, "one" },
    { "SQ1. Surprise Squig!: standing blocks worth 600 and 1,200, none of ours near -> ONE ground cast under the 1,200",
      function(b) return { caster(b, K.SQ, { dist_by_target = { [b + 5] = 30, [b + 6] = 30 } }) },
        { enemy(b + 5, SW, { pos = { 0, 0, 60 } }), enemy(b + 6, SW, { pos = { 80, 0, 60 } }) },
        { sv = S({ [b + 5] = 600, [b + 6] = 1200 }) } end,
      "surprise_squig", K.SQ, 1, "g6", "none" },
    { "SQ2. Surprise Squig!: our Swordsmen 15 m from the only block -> no cast",
      function(b) return { caster(b, K.SQ, { dist_by_target = { [b + 5] = 30 } }), ours(b + 1, 0, 35) },
        { enemy(b + 5, SW, { pos = { 0, 0, 60 } }) }, { sv = S({ [b + 5] = 600 }) } end,
      "surprise_squig", K.SQ, 0, nil, "none" },
    { "SQ3. Surprise Squig!: the only block is moving -> no cast",
      function(b) return { caster(b, K.SQ, { dist_by_target = { [b + 5] = 30 } }) },
        { enemy(b + 5, SW, { pos = { 0, 0, 60 }, moving = true }) }, { sv = S({ [b + 5] = 600 }) } end,
      "surprise_squig", K.SQ, 0, nil, "none" },
    { "RS1. Ravaging Swarm: an enemy in melee 60 m away -> ONE cast",
      function(b) return { caster(b, K.RS, { dist = 60 }) }, { enemy(b + 5, SW, { melee = true, dist = 60 }) } end,
      "dispatch_the_swarm_attack", K.RS, 1, "u5", "none" },
    { "CK1. Curse of Khsar: an enemy in melee 60 m away -> ONE ground cast",
      function(b) return { caster(b, K.CK, { dist = 60, health_percent = 40 }) }, { enemy(b + 5, SW, { melee = true, dist = 60 }) } end,
      "curse_of_khsar", K.CK, 1, "g5", "none" },   -- the game refuses Curse of Khsar above 50% caster health
    { "LU1. Lord of Undeath (a 50 m key): an enemy in melee 60 m away -> no cast",
      function(b) return { caster(b, K.LU, { dist = 60 }) }, { enemy(b + 5, SW, { melee = true, dist = 60 }) } end,
      "lord_of_undeath", K.LU, 0, nil, "one" },
    { "LU2. Lord of Undeath (the 200 m key): an enemy in melee 60 m away -> ONE cast",
      function(b) return { caster(b, K.LU4, { dist = 60 }) }, { enemy(b + 5, SW, { melee = true, dist = 60 }) } end,
      "lord_of_undeath_4", K.LU4, 1, "g5", "none" },
  }
  for _, f in ipairs(FILES) do
    local TAG = f.tag
    for i, w in ipairs(WORLDS) do
      local b = 47000 + i * 20
      local units, enemies, o = w[2](b)
      local W = world(w[1], units, enemies, w[3], w[4], f.path, TAG, o)
      if W ~= nil then
        local got, on_t = 0, 0
        local want = w[6]
        local form = want and want:sub(1, 1)
        local tuid = want and tostring(b + tonumber(want:sub(2)))
        for _, x in ipairs(W.fires) do
          if x.key == w[4] then
            got = got + 1
            local tid = nil
            pcall(function() tid = tostring(x.target:unique_ui_id()) end)
            if form == "u" and tid == tuid then on_t = on_t + 1 end
          end
        end
        for _, x in ipairs(W.ground_fires or {}) do
          if x.key == w[4] then
            got = got + 1
            if form == "g" and x.pos ~= nil and x.pos.marker == ("pos:" .. tuid) then on_t = on_t + 1 end
          end
        end
        local a, txt
        if RED180 then
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
          local c_ok = by.land_mine == "Fires in melee unless wavering, clear of allies, with 60+ enemies in the blast"
            and by.surprise_squig == "Fires under the standing enemy block worth the most, clear of allies"
            and by.lord_of_undeath_4 ~= nil and by.lord_of_undeath_4 == by.lord_of_undeath
          check(TAG .. "CA9: the cards of Land Mine and Surprise Squig!, the split Lord of Undeath (" .. tostring(by.surprise_squig) .. ")",
            (RED180 and not c_ok) or (not RED180 and c_ok))
          done((RED180 and not c_ok) or (not RED180 and c_ok))
        end
        tally(W)
      end
    end
  end
  if RED180 then
    check("RED CONTROL (harness 180): the pre-181 build keeps the old triggers - " .. n_ok .. "/" .. n_all,
      n_all == 20 and n_ok == 20)
  else
    check("HARNESS 180: every check behaved - " .. n_ok .. "/" .. n_all, n_all == 20 and n_ok == 20)
  end
  print("== HARNESS 180 done: " .. (checks - pre180) .. " checks in this section ==")
end
