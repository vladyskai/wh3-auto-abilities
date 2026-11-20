-- ============================================================================
-- HARNESS 182 (round 183): THE RULE-SHUT REVIEW, ROWS 1-9 (the "own-troop damage" rows; user 2026-11-20: "You may
--   start implementing #1-9 for now"; rulings from the Claude Docs review, rev 44).
--   0zz31 the 9 entries, their families, the 35 m aura of rows 1-4, the multi-use holds.
--   DD1 Defiling Deluge: an enemy in melee 15 m away (inside 24 m = 70% of 35) -> ONE cast (RED: none).
--   DD2 Defiling Deluge: the only enemy in melee is 40 m away -> no cast.
--   PR1 Plaguereaper: the caster in melee at 60% health -> ONE cast (RED: none).
--   PR2 Plaguereaper: the caster in melee at 90% health -> no cast.
--   RS1 Reaper of Souls: the caster in melee at 60% health -> ONE cast (RED: none).
--   WQ1 Warp-Quake: the caster in melee -> ONE cast (RED: none).
--   WS1 Web of Shadows: the caster in melee -> ONE cast (RED: none).
--   CA11 the cards of the three families on the new entries.
--   RED control: H182_LIVE / H182_ANN on docs/backups/round183/pre183_*.lua.
-- ============================================================================
function run_h182()
  local L182 = os.getenv("H182_LIVE") or LIVE
  local A182 = os.getenv("H182_ANN") or ANN
  local RED182 = (os.getenv("H182_LIVE") ~= nil) or (os.getenv("H182_ANN") ~= nil)
  local K = {
    DD = "wh3_twa08_unit_abilities_defiling_deluge", PR = "wh3_dlc29_item_abilities_plaguereaper",
    RS = "wh2_dlc14_lord_abilities_reaper_of_souls", WQ = "wh2_dlc14_unit_abilities_warp_quake",
    WS = "wh2_main_weapon_abilities_web_of_shadows",
  }
  local GUO = "wh3_twa08_nur_mon_great_unclean_one_0_ror"
  local MALUS = "wh2_dlc14_def_cha_malus_darkblade_tzarkan_0"
  local GRINDER = "wh2_dlc14_skv_inf_warp_grinder_0"
  local SW = "wh_main_emp_inf_swordsmen"
  local ZOMBIE = "wh_main_vmp_inf_zombie"
  local pre182 = checks
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1; at = i + #tok
    end
  end
  print("== HARNESS 182 - section 0zz31: the round-183 entries ==")
  if not RED182 then
    local ENT = {
      { "defiling_deluge", "enemy_melee_near" }, { "murderous_exhortations", "enemy_melee_near" },
      { "rod_of_corruption", "enemy_melee_near" }, { "wail_of_malice", "enemy_melee_near" },
      { "plaguereaper", "melee_health75" }, { "reaper_of_souls", "melee_health75" },
      { "shard_blade", "melee_unwavering" }, { "web_of_shadows", "melee_unwavering" },
      { "warp_quake", "melee_unwavering" },
    }
    for _, f in ipairs({ { name = "live", path = L182 }, { name = "ann", path = A182 } }) do
      local s = read_file(f.path)
      local got = 0
      for _, e in ipairs(ENT) do
        if cp(s, '{ marker = "' .. e[1] .. '", ') == 1 and cp(s, 'marker = "' .. e[1] .. '", name = ') == 1
          and raw_find(s, 'marker = "' .. e[1] .. '", name = "', 1, true) ~= nil then
          local i = raw_find(s, 'marker = "' .. e[1] .. '", name = "', 1, true)
          local line = s:sub(i, i + 120)
          if raw_find(line, 'trigger = "' .. e[2] .. '",', 1, true) ~= nil then got = got + 1 end
        end
      end
      check("0zz31 " .. f.name .. ": the 9 entries on their families (" .. got .. "), 4 auras of 35 m, 6 multi-use holds",
        got == 9 and cp(s, "\t\tkeys = { \"wh3_twa08_unit_abilities_defiling_deluge\" },\n\t\taura_real = 35,\n") == 1
        and cp(s, "-- ROUND 183 (rule-shut review row ") == 9
        and cp(s, '\t\t["wh3_main_weapon_abilities_shard_blade"] = 120,\n') == 1
        and cp(s, '\t\t["wh2_dlc14_unit_abilities_wail_of_malice"] = 90,\n') == 1)
    end
  end
  local FILES = { { path = A182, tag = "[annotated] " }, { path = L182, tag = "[live] " } }
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
        pr.unit.is_visible_to_alliance = function(self, a) return true end
        pr.unit.is_currently_flying = function(self) return false end
      end
    end
    sel_event(W, units[1].uid, true); ui(W); ui(W)
    click(W, "zz_auto_badge_" .. marker); ui(W)
    sel_event(W, units[1].uid, false); ui(W)
    W.conflict = true
    polln(W, o.polls or 4)
    return W
  end
  local function own(name, b, key, o)
    local c = { name = name, uid = b, owns = { key }, melee = false, dist = 30, health_percent = 100, pos = { 0, 0, 0 },
                width = 10, unit_class = "com" }
    for k, v in pairs(o or {}) do c[k] = v end
    return c
  end
  local function foe(uid, z, o)
    local e = { uid = uid, name = ZOMBIE, melee = false, pos = { 0, 0, z }, width = 20, men_alive = 80, initial_men = 80,
                unit_class = "inf_mel", dist = 30 }
    for k, v in pairs(o or {}) do e[k] = v end
    return e
  end
  local WORLDS = {
    { "DD1. Defiling Deluge: an enemy in melee 15 m away -> ONE cast",
      function(b) return { own(GUO, b, K.DD, { dist_by_target = { [b + 5] = 15 } }),
        { name = SW, uid = b + 1, owns = {}, melee = true, dist = 30, health_percent = 100, pos = { 0, 0, 20 },
          width = 10, men_alive = 120, unit_class = "inf_mel" } },
        { foe(b + 5, 20, { melee = true, dist = 15 }) } end, "defiling_deluge", K.DD, 1 },
    { "DD2. Defiling Deluge: the only enemy in melee is 40 m away -> no cast",
      function(b) return { own(GUO, b, K.DD, { dist_by_target = { [b + 5] = 40 } }),
        { name = SW, uid = b + 1, owns = {}, melee = true, dist = 30, health_percent = 100, pos = { 0, 0, 45 },
          width = 10, men_alive = 120, unit_class = "inf_mel" } },
        { foe(b + 5, 45, { melee = true, dist = 40 }) } end, "defiling_deluge", K.DD, 0 },
    { "PR1. Plaguereaper: the caster in melee at 60% health -> ONE cast",
      function(b) return { own(MALUS, b, K.PR, { melee = true, health_percent = 60 }) },
        { foe(b + 5, 3, { melee = true, dist = 1 }) } end, "plaguereaper", K.PR, 1 },
    { "PR2. Plaguereaper: the caster in melee at 90% health -> no cast",
      function(b) return { own(MALUS, b, K.PR, { melee = true, health_percent = 90 }) },
        { foe(b + 5, 3, { melee = true, dist = 1 }) } end, "plaguereaper", K.PR, 0 },
    { "RS1. Reaper of Souls: the caster in melee at 60% health -> ONE cast",
      function(b) return { own(MALUS, b, K.RS, { melee = true, health_percent = 60 }) },
        { foe(b + 5, 3, { melee = true, dist = 1 }) } end, "reaper_of_souls", K.RS, 1 },
    { "WQ1. Warp-Quake: the caster in melee -> ONE cast",
      function(b) return { own(GRINDER, b, K.WQ, { melee = true, unit_class = "inf_mel", men_alive = 60 }) },
        { foe(b + 5, 3, { melee = true, dist = 1 }) } end, "warp_quake", K.WQ, 1 },
    { "WS1. Web of Shadows: the caster in melee -> ONE cast",
      function(b) return { own(MALUS, b, K.WS, { melee = true }) },
        { foe(b + 5, 3, { melee = true, dist = 1 }) } end, "web_of_shadows", K.WS, 1 },
  }
  for _, f in ipairs(FILES) do
    local TAG = f.tag
    for i, w in ipairs(WORLDS) do
      local b = 51000 + i * 20
      local units, enemies, o = w[2](b)
      local W = world(w[1], units, enemies, w[3], w[4], f.path, TAG, o)
      if W ~= nil then
        local got = 0
        for _, x in ipairs(W.fires) do if x.key == w[4] then got = got + 1 end end
        for _, x in ipairs(W.ground_fires or {}) do if x.key == w[4] then got = got + 1 end end
        local a, txt
        if RED182 then
          a = (got == 0)
          txt = "-REDa: the pre-183 build has no entry, got " .. got
        else
          a = (got == w[5])
          txt = "a: " .. w[5] .. " cast(s) expected, got " .. got
        end
        check(TAG .. w[1]:sub(1, 3) .. txt, a)
        done(a)
        if i == 1 then
          local by = {}
          for _, e in ipairs(W.cap or {}) do by[e.marker] = e.card end
          local c_ok = by.defiling_deluge == "Fires when it or a nearby enemy is in melee"
            and by.reaper_of_souls == "Fires in melee below 75% health"
            and by.warp_quake == "Fires in melee unless wavering"
          check(TAG .. "CA11: the cards of the new entries (" .. tostring(by.defiling_deluge) .. ")",
            (RED182 and not c_ok) or (not RED182 and c_ok))
          done((RED182 and not c_ok) or (not RED182 and c_ok))
        end
        tally(W)
      end
    end
  end
  if RED182 then
    check("RED CONTROL (harness 182): the pre-183 build has none of the 9 entries - " .. n_ok .. "/" .. n_all,
      n_all == 16 and n_ok == 16)
  else
    check("HARNESS 182: every check behaved - " .. n_ok .. "/" .. n_all, n_all == 16 and n_ok == 16)
  end
  print("== HARNESS 182 done: " .. (checks - pre182) .. " checks in this section ==")
end
