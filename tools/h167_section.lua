-- ============================================================================
-- HARNESS 167 (round 168): THE CAST ANIMATION DECIDES THE STAND-STILL RULE; THE OLDER PICKERS SKIP HIDDEN ENEMIES
--   (user rulings 2026-11-17: "Option A, animation decides all. And please implement the visibility.").
--   0zz16 the round-168 tokens in both files.
--   AN1 Volley of High Arrows (cast_forward_short: its cast stops the caster), the caster MOVING, a Grave Guard block
--       in reach -> no cast (the rule stays for an animated cast).
--   AN2 Fireball (no cast animation), the caster MOVING, the same block -> ONE cast.
--   AN3 Wrath of Manann (no cast animation), the caster MOVING, a standing Grave Guard 60 m ahead -> ONE cast.
--   VS1 Blight Swarm (enemy_melee): the only enemy in melee is HIDDEN (is_visible_to_alliance false) -> no cast.
--   VS2 the same enemy visible -> ONE cast at it.
--   VS3 The Dreaded Thirteenth (the non-commander picker): the only enemy in melee is HIDDEN -> no cast.
--   VS4 the same enemy visible -> ONE cast.
--   CA1 the cards: Fireball and Banishment carry no stand-still words for the caster; Volley of High Arrows and Frost
--       Fang (animated) still do.
--   RED (pre-168 = round 167): AN2, AN3 no cast (the family rule); VS1, VS3 cast at the hidden enemy; the cards still
--       say 'standing still' for Fireball.
-- ============================================================================
function run_h167()
  local L167 = os.getenv("H167_LIVE") or LIVE
  local A167 = os.getenv("H167_ANN") or ANN
  local RED167 = (os.getenv("H167_LIVE") ~= nil) or (os.getenv("H167_ANN") ~= nil)
  local FB = "wh_main_spell_bound_fireball"
  local VO = "wh2_main_character_abilities_volley_of_high_arrows"
  local WM = "wh_dlc07_item_abilities_wrath_of_manann"
  local BS = "wh3_main_lord_abilities_blight_swarm"
  local D13 = "wh3_dlc29_spell_bound_the_dreaded_thirteenth"
  local CASTER = "wh2_dlc13_emp_cha_huntsmen_general_0"
  local GG = "wh_main_vmp_inf_grave_guard_0"
  local pre167 = checks
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1; at = i + #tok
    end
  end

  print("== HARNESS 167 - section 0zz16: the round-168 tokens ==")
  if not RED167 then
    for _, f in ipairs({ { name = "live", path = L167 }, { name = "ann", path = A167 } }) do
      local s = read_file(f.path)
      check("0zz16 " .. f.name .. ": the ANIM table and loader, the stand-still gate, the visibility test in both pickers",
        cp(s, 'FOURTH.ANIM_TEXT = "') == 1 and cp(s, "function FOURTH.cast_stops_caster()") == 1
        and cp(s, "\tif not FOURTH.cast_stops_caster() then return true end\n") == 1
        and cp(s, "function FOURTH.enemy_not_hidden(enemy)") == 1
        and cp(s, "\tif not FOURTH.enemy_not_hidden(enemy) then return false end   -- ROUND 168") == 1
        and cp(s, "\t\t\t\t\t\t\t\tand FOURTH.enemy_not_hidden(enemy) then   -- ROUND 168") == 1
        and cp(s, "wh2_main_character_abilities_volley_of_high_arrows;") == 1
        and cp(s, "wh_main_spell_bound_fireball;") == 0)
    end
  end

  local FILES = { { path = A167, tag = "[annotated] " }, { path = L167, tag = "[live] " } }
  local n_ok, n_all = 0, 0
  local function done(ok) n_all = n_all + 1; if ok then n_ok = n_ok + 1 end end
  -- hidden: uid -> true for an enemy the game reads as NOT visible to our alliance
  local function world(wname, units, enemies, marker, key, PATH, TAG, sv, hidden)
    local cards = {}
    for _, d in ipairs(units) do cards[#cards + 1] = { id = tostring(d.uid), state = "active", vis = true } end
    local W = make_world({ can_perform = true, units = units, enemies = enemies, cards = cards,
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
        local vis = not (hidden ~= nil and hidden[id] == true)
        pr.unit.is_visible_to_alliance = function(self, a) return vis end
        pr.unit.is_currently_flying = function(self) return false end
        local v = sv and sv[id] or 800
        pr.unit.strategic_value = function(self) return v end
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
    local c = { name = CASTER, uid = b, owns = { key }, melee = false, dist = 100, pos = { 0, 0, 0 }, width = 2,
                men_alive = 1, unit_class = "com" }
    for k, v in pairs(o or {}) do c[k] = v end
    return c
  end
  local function block(uid, name, x, z, o)
    local e = { uid = uid, name = name, melee = false, pos = { x, 0, z }, width = 29.4, men_alive = 120,
                initial_men = 120, unit_class = "inf_mel", dist = 40 }
    for k, v in pairs(o or {}) do e[k] = v end
    return e
  end
  local function sv(b) return { [tostring(b + 5)] = 850 } end
  local function hid(b) return { [tostring(b + 5)] = true } end
  -- name, builder(b) -> units, enemies, values, hidden; marker; key; GREEN casts; RED casts
  local WORLDS = {
    { "AN1. Volley of High Arrows (animated), the caster MOVING, Grave Guard in reach -> no cast",
      function(b) return { caster(b, VO, { moving = true }) }, { block(b + 5, GG, 0, 150, { dist = 100 }) }, sv(b), nil end,
      "character_abilities_volley_of_high_arrows", VO, 0, 0 },
    { "AN2. Fireball (no cast animation), the caster MOVING, Grave Guard in reach -> ONE cast",
      function(b) return { caster(b, FB, { moving = true }) }, { block(b + 5, GG, 0, 150, { dist = 100 }) }, sv(b), nil end,
      "spell_bound_fireball", FB, 1, 0 },
    { "AN3. Wrath of Manann (no cast animation), the caster MOVING, a standing Grave Guard 60 m ahead -> ONE cast",
      function(b) return { caster(b, WM, { moving = true, dist = 40 }) }, { block(b + 5, GG, 0, 60) }, sv(b), nil end,
      "wrath_of_manann", WM, 1, 0 },
    { "VS1. Blight Swarm: the only enemy in melee is HIDDEN -> no cast",
      function(b) return { caster(b, BS, { dist = 10 }) }, { block(b + 5, GG, 0, 20, { melee = true, dist = 10 }) }, sv(b),
        hid(b) end, "blight_swarm", BS, 0, 1 },
    { "VS2. Blight Swarm: the same enemy visible -> ONE cast",
      function(b) return { caster(b, BS, { dist = 10 }) }, { block(b + 5, GG, 0, 20, { melee = true, dist = 10 }) }, sv(b),
        nil end, "blight_swarm", BS, 1, 1 },
    { "VS3. The Dreaded Thirteenth (non-commander picker): the only enemy in melee is HIDDEN -> no cast",
      function(b) return { caster(b, D13, { dist = 10 }) }, { block(b + 5, GG, 0, 20, { melee = true, dist = 10 }) }, sv(b),
        hid(b) end, "the_dreaded_thirteenth", D13, 0, 1 },
    { "VS4. The Dreaded Thirteenth: the same enemy visible -> ONE cast",
      function(b) return { caster(b, D13, { dist = 10 }) }, { block(b + 5, GG, 0, 20, { melee = true, dist = 10 }) }, sv(b),
        nil end, "the_dreaded_thirteenth", D13, 1, 1 },
  }
  local cards = nil
  for _, f in ipairs(FILES) do
    local TAG = f.tag
    for i, w in ipairs(WORLDS) do
      local want = RED167 and w[6] or w[5]
      local b = 32000 + i * 20
      local units, enemies, values, hidden = w[2](b)
      local W = world(w[1], units, enemies, w[3], w[4], f.path, TAG, values, hidden)
      if W ~= nil then
        local got = 0
        for _, x in ipairs(W.fires) do if x.key == w[4] then got = got + 1 end end
        for _, x in ipairs(W.ground_fires or {}) do if x.key == w[4] then got = got + 1 end end
        local a = (got == want)
        check(TAG .. w[1]:sub(1, 3) .. (RED167 and "-RED" or "") .. "a: " .. want .. " cast(s) expected, got " .. got, a)
        done(a)
        if i == 1 then
          local by = {}
          for _, e in ipairs(W.cap or {}) do by[e.marker] = e.card end
          local still_fb = type(by.spell_bound_fireball) == "string" and raw_find(by.spell_bound_fireball, "standing still", 1, true) ~= nil
          local ok = by.spell_bound_fireball == "Fires where the blast hurts the enemy most, clear of allies"
            and by.banishment == "Fires when the target stands still, where the blast hurts the enemy most, clear of allies"
            and type(by.character_abilities_volley_of_high_arrows) == "string"
            and raw_find(by.character_abilities_volley_of_high_arrows, "Fires when standing still, ", 1, true) == 1
            and type(by.frost_fang) == "string"
            and raw_find(by.frost_fang, "Fires when it and the target stand still, where the blast hurts the enemy most", 1, true) == 1
          check(TAG .. "CA1: the stand-still words only on animated casts (Fireball: " .. tostring(by.spell_bound_fireball) .. ")",
            (RED167 and still_fb) or (not RED167 and ok))
          done((RED167 and still_fb) or (not RED167 and ok))
        end
        tally(W)
      end
    end
  end
  if RED167 then
    check("RED CONTROL (harness 167): the pre-168 build waits on every family caster and casts at hidden enemies - "
      .. n_ok .. "/" .. n_all, n_all == 16 and n_ok == 16)
  else
    check("HARNESS 167: every check behaved - " .. n_ok .. "/" .. n_all, n_all == 16 and n_ok == 16)
  end
  print("== HARNESS 167 done: " .. (checks - pre167) .. " checks in this section ==")
end
