-- ============================================================================
-- HARNESS 156 (round 157): THE DRAINS AND THE EXECUTIONER (user rulings 2026-11-15).
--   Spirit Leech (wh3_main, 70 m bound), Punch-Dagger (10 m bound), The
--   Emperor's Executioner (35 m bound; base 20% Lord/Hero only, upgrade 33%).
--   VA a Vampire (single entity, a hero), TG a Terrorgheist (large single
--   monster), GG Grave Guard.
--   DR1 Spirit Leech: VA (900) + GG (1500, not single) -> ONE cast at VA.
--   DR2 Spirit Leech: VA with our Swordsmen on it (a drain has no safety margin)
--       -> ONE cast at VA.
--   DR3 Spirit Leech: the caster is moving -> no cast.
--   DR4 Punch-Dagger: VA 60 m away (bound 10 m) -> no cast.
--   DR5 Punch-Dagger: VA 8 m away -> ONE cast at VA.
--   EX1 Executioner: VA at 15% health -> ONE cast at VA.
--   EX2 Executioner: VA at 30% health (line 20%) -> no cast.
--   EX3 Executioner upgrade: TG at 30% health (line 33%) -> ONE cast at TG.
--   EX4 Executioner (Lord/Hero only): TG at 15% health -> no cast.
--   RED (pre-157 = round 156): DR1, DR2, EX1, EX3 cast nothing.
-- ============================================================================
function run_h156()
  local L156 = os.getenv("H156_LIVE") or LIVE
  local A156 = os.getenv("H156_ANN") or ANN
  local RED156 = (os.getenv("H156_LIVE") ~= nil) or (os.getenv("H156_ANN") ~= nil)
  local SL = "wh3_main_spell_bound_spirit_leech"
  local PD = "wh3_dlc29_item_abilities_punch_dagger"
  local EX = "wh3_dlc24_lord_abilities_the_emperors_executioner"
  local EU = "wh3_dlc24_lord_abilities_the_emperors_executioner_upgrade"
  local CASTER = "wh2_dlc13_emp_cha_huntsmen_general_0"
  local TG = "wh_main_vmp_mon_terrorgheist"
  local VA = "wh_main_vmp_cha_vampire_0"
  local GG = "wh_main_vmp_inf_grave_guard_0"
  local SW = "wh_main_emp_inf_swordsmen"
  local pre156 = checks
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1; at = i + #tok
    end
  end

  print("== HARNESS 156 - section 0zz4: the round-157 tokens ==")
  if not RED156 then
    for _, f in ipairs({ { name = "live", path = L156 }, { name = "ann", path = A156 } }) do
      local s = read_file(f.path)
      check("0zz4 " .. f.name .. ": 822 entries, 10 drains, 2 executes, the EXEC table, the re-check kinds",
        cp(s, "\t{ marker = ") == 822
        and cp(s, 'trigger = "enemy_single_drain"') == 10 and cp(s, 'trigger = "enemy_execute"') == 2
        and raw_find(s, "enemy_single_drain = FOURTH.evaluate_enemy_single_drain,", 1, true) ~= nil
        and raw_find(s, "enemy_execute = FOURTH.evaluate_enemy_execute,", 1, true) ~= nil
        and raw_find(s, "wh3_dlc24_lord_abilities_the_emperors_executioner=0.2;", 1, true) ~= nil
        and raw_find(s, "wh3_dlc24_lord_abilities_the_emperors_executioner_upgrade=0.33\"", 1, true) ~= nil
        and raw_find(s, 'if kind == "execute" and not FOURTH.exec_ok(e) then return false end', 1, true) ~= nil
        and raw_find(s, "function FOURTH.shot_cand_ok(unit, e, m, nosafe)", 1, true) ~= nil)
    end
  end

  local FILES = { { path = A156, tag = "[annotated] " }, { path = L156, tag = "[live] " } }
  local n_ok, n_all = 0, 0
  local function done(ok) n_all = n_all + 1; if ok then n_ok = n_ok + 1 end end
  local function world(wname, units, enemies, marker, key, PATH, TAG, sv)
    local cards = {}
    for _, d in ipairs(units) do cards[#cards + 1] = { id = tostring(d.uid), state = "active", vis = true } end
    local W = make_world({ can_perform = true, units = units, enemies = enemies, cards = cards,
      bar = { { id = "b1", key = key } } })
    W.defaults_on = false
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
        local v = sv[id]
        if v ~= nil then pr.unit.strategic_value = function(self) return v end end
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
    local c = { name = CASTER, uid = b, owns = { key }, melee = false, dist = 60, pos = { 0, 0, 0 }, width = 2,
                men_alive = 1, unit_class = "com" }
    for k, v in pairs(o or {}) do c[k] = v end
    return c
  end
  local function single(uid, name, x, z, cls, hp)
    return { uid = uid, name = name, melee = false, pos = { x, 0, z }, width = 6, men_alive = 1, initial_men = 1,
             unit_class = cls, dist = 60, hp_frac = hp }
  end
  local function block(uid, name, x, z)
    return { uid = uid, name = name, melee = false, pos = { x, 0, z }, width = 29.4, men_alive = 120,
             initial_men = 120, unit_class = "inf_mel", dist = 60 }
  end
  local function ours(uid, z)
    return { uid = uid, name = SW, owns = {}, melee = true, pos = { 0, 0, z }, width = 29.4, men_alive = 120,
             initial_men = 120, unit_class = "inf_mel" }
  end
  -- name, builder(b) -> units, enemies, sv; marker; key; GREEN casts; RED casts (nil = not RED); target offset
  local WORLDS = {
    { "DR1. Spirit Leech: a Vampire (900) and Grave Guard (1500, not single) -> ONE cast at the Vampire",
      function(b) return { caster(b, SL) }, { single(b + 5, VA, 0, 100, "com"), block(b + 6, GG, 60, 100) },
        { [tostring(b + 5)] = 900, [tostring(b + 6)] = 1500 } end, "spirit_leech", SL, 1, 0, 5 },
    { "DR2. Spirit Leech: our Swordsmen fight the Vampire (a drain has no safety margin) -> ONE cast at the Vampire",
      function(b) return { caster(b, SL), ours(b + 1, 100) }, { single(b + 5, VA, 0, 100, "com") },
        { [tostring(b + 5)] = 900 } end, "spirit_leech", SL, 1, 0, 5 },
    { "DR3. Spirit Leech: the caster is moving -> no cast",
      function(b) return { caster(b, SL, { moving = true }) }, { single(b + 5, VA, 0, 100, "com") },
        { [tostring(b + 5)] = 900 } end, "spirit_leech", SL, 0, nil, nil },
    { "DR4. Punch-Dagger: the Vampire 60 m away (bound 10 m) -> no cast",
      function(b) return { caster(b, PD) }, { single(b + 5, VA, 0, 100, "com") },
        { [tostring(b + 5)] = 900 } end, "punch_dagger", PD, 0, nil, nil },
    { "DR5. Punch-Dagger: the Vampire 8 m away -> ONE cast at it",
      function(b) return { caster(b, PD, { dist = 8 }) }, { single(b + 5, VA, 0, 100, "com") },
        { [tostring(b + 5)] = 900 } end, "punch_dagger", PD, 1, nil, 5 },
    { "EX1. Executioner: a Vampire at 15% health (line 20%) -> ONE cast at it",
      function(b) return { caster(b, EX, { dist = 30 }) }, { single(b + 5, VA, 0, 100, "com", 0.15) },
        { [tostring(b + 5)] = 900 } end, "emperors_executioner", EX, 1, 0, 5 },
    { "EX2. Executioner: the Vampire at 30% health -> no cast",
      function(b) return { caster(b, EX, { dist = 30 }) }, { single(b + 5, VA, 0, 100, "com", 0.30) },
        { [tostring(b + 5)] = 900 } end, "emperors_executioner", EX, 0, nil, nil },
    { "EX3. Executioner upgrade: a Terrorgheist at 30% health (line 33%) -> ONE cast at it",
      function(b) return { caster(b, EU, { dist = 30 }) }, { single(b + 5, TG, 0, 100, "mon", 0.30) },
        { [tostring(b + 5)] = 2000 } end, "emperors_executioner_upgrade", EU, 1, 0, 5 },
    { "EX4. Executioner (Lord/Hero only): a Terrorgheist at 15% health -> no cast",
      function(b) return { caster(b, EX, { dist = 30 }) }, { single(b + 5, TG, 0, 100, "mon", 0.15) },
        { [tostring(b + 5)] = 2000 } end, "emperors_executioner", EX, 0, nil, nil },
  }
  for _, f in ipairs(FILES) do
    local TAG = f.tag
    for i, w in ipairs(WORLDS) do
      local want = w[5]
      if RED156 then want = w[6] end
      if want ~= nil then
        local b = 18500 + i * 20
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
          local a = (got == want)
          local ttxt = ""
          if want > 0 and not RED156 and w[7] ~= nil then
            a = a and tid == tostring(b + w[7])
            ttxt = ", target " .. tostring(tid) .. " want " .. tostring(b + w[7])
          end
          check(TAG .. w[1]:sub(1, 3) .. (RED156 and "-RED" or "") .. "a: " .. want .. " cast(s) expected, got " .. got
            .. ttxt, a)
          done(a)
          tally(W)
        end
      end
    end
  end
  if RED156 then
    check("RED CONTROL (harness 156): the pre-157 build has no drains and no executioner - " .. n_ok .. "/" .. n_all,
      n_all == 8 and n_ok == 8)
  else
    check("HARNESS 156: every drain / execute world behaved - " .. n_ok .. "/" .. n_all, n_all == 18 and n_ok == 18)
  end
  print("== HARNESS 156 done: " .. (checks - pre156) .. " checks in this section ==")
end
