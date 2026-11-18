-- ============================================================================
-- HARNESS 171 (round 172): ROWS 1, 3 AND 5 AS RULED IN docs\WH3_low_score_review_2026-11-17.md (round 171 built the
--   first proposals; the user: "I feel like you ignored the current version").
--   0zz20 army_charge_or_melee wired; Waaagh! rides it; AURA_CHARGE_ALLIES and {ACA} gone; army_moments exists.
--   AC4 Horn of the Wild Hunt: an army of 2 living units, both charging -> ONE cast (every living unit).
--   AC5 Horn: an army of 2, only the caster charging -> no cast.
--   WA2 Waaagh!: 3 units in a melee older than 2 s (no charge, no fresh contact) -> ONE cast (army melee).
--   WA3 Waaagh!: an army of 2, both in an old melee -> ONE cast (every living unit).
--   WA4 Waaagh!: 3 living units, 2 in an old melee -> no cast.
--   UR3 Ursun's Roar: the caster idle, ONE ally within 24 m charging -> ONE cast.
--   UR4 Ursun's Roar: the caster wavering -> ONE cast.
--   UR5 Ursun's Roar: an ally 15 m away wavering -> ONE cast.
--   UR6 Ursun's Roar: an ally 40 m away wavering (outside the 24 m aura) -> no cast.
--   CA3 the three cards.
--   RED (pre-172 = round 171): AC4, WA2, WA3, UR3, UR4, UR5 do not fire.
-- ============================================================================
function run_h171()
  local L171 = os.getenv("H171_LIVE") or LIVE
  local A171 = os.getenv("H171_ANN") or ANN
  local RED171 = (os.getenv("H171_LIVE") ~= nil) or (os.getenv("H171_ANN") ~= nil)
  local HORN = "wh_dlc05_item_abilities_horn_of_the_wild_hunt"
  local WAAA = "wh_main_character_abilities_waaagh"
  local URS = "wh3_main_character_abilities_ursuns_roar"
  local CASTER = "wh2_dlc13_emp_cha_huntsmen_general_0"
  local SW = "wh_main_emp_inf_swordsmen"
  local pre171 = checks
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1; at = i + #tok
    end
  end

  print("== HARNESS 171 - section 0zz20: the round-172 tokens ==")
  if not RED171 then
    for _, f in ipairs({ { name = "live", path = L171 }, { name = "ann", path = A171 } }) do
      local s = read_file(f.path)
      check("0zz20 " .. f.name .. ": army_charge_or_melee wired, Waaagh! on it, AURA_CHARGE_ALLIES gone, army_moments",
        cp(s, "\t{ marker = ") == 939
        and cp(s, "army_charge_or_melee = FOURTH.evaluate_army_charge_or_melee,") == 1
        and cp(s, '{ marker = "waaagh_army", name = "Waaagh!", trigger = "army_charge_or_melee",') == 1
        and cp(s, 'trigger = "army_charge"') == 1 and cp(s, 'trigger = "aura_charge"') == 1
        and cp(s, "AURA_CHARGE_ALLIES =") == 0 and cp(s, "{ACA}") == 0
        and cp(s, "function FOURTH.army_moments()") == 1)
    end
  end

  local FILES = { { path = A171, tag = "[annotated] " }, { path = L171, tag = "[live] " } }
  local n_ok, n_all = 0, 0
  local function done(ok) n_all = n_all + 1; if ok then n_ok = n_ok + 1 end end
  local function world(wname, units, marker, key, PATH, TAG, o)
    o = o or {}
    local cards = {}
    for _, d in ipairs(units) do cards[#cards + 1] = { id = tostring(d.uid), state = "active", vis = true } end
    local W = make_world({ can_perform = true, units = units, enemies = {}, cards = cards,
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
    if o.pre ~= nil then
      -- an OLD melee: the units fight for o.pre polls (0.25 s each) BEFORE the ability is armed
      W.conflict = true
      polln(W, o.pre)
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
  local MEL = { melee = true }
  local OLD = { pre = 12 }   -- 3 s of melee before arming: no fresh contact left (FRESH_CONTACT_S = 2)
  -- name, builder(b) -> units, opts; marker; key; GREEN casts; RED casts
  local WORLDS = {
    { "AC4. Horn: an army of 2, both charging -> ONE cast (every living unit)",
      function(b) return { caster(b, HORN, CH), ally(b + 1, CH) } end, "horn_of_the_wild_hunt", HORN, 1, 0 },
    { "AC5. Horn: an army of 2, only the caster charging -> no cast",
      function(b) return { caster(b, HORN, CH), ally(b + 1) } end, "horn_of_the_wild_hunt", HORN, 0, 0 },
    { "WA2. Waaagh!: 3 units in an old melee -> ONE cast (army melee)",
      function(b) return { caster(b, WAAA, MEL), ally(b + 1, MEL), ally(b + 2, MEL) }, OLD end, "waaagh_army", WAAA, 1, 0 },
    { "WA3. Waaagh!: an army of 2, both in an old melee -> ONE cast",
      function(b) return { caster(b, WAAA, MEL), ally(b + 1, MEL) }, OLD end, "waaagh_army", WAAA, 1, 0 },
    { "WA4. Waaagh!: 3 living units, 2 in an old melee -> no cast",
      function(b) return { caster(b, WAAA, MEL), ally(b + 1, MEL), ally(b + 2) }, OLD end, "waaagh_army", WAAA, 0, 0 },
    { "UR3. Ursun's Roar: the caster idle, ONE ally within 24 m charging -> ONE cast",
      function(b) return { caster(b, URS), ally(b + 1, CH) } end, "ursuns_roar_charge", URS, 1, 0 },
    { "UR4. Ursun's Roar: the caster wavering -> ONE cast",
      function(b) return { caster(b, URS, { wavering = true }) } end, "ursuns_roar_charge", URS, 1, 0 },
    { "UR5. Ursun's Roar: an ally 15 m away wavering -> ONE cast",
      function(b) return { caster(b, URS), ally(b + 1, { wavering = true }) } end, "ursuns_roar_charge", URS, 1, 0 },
    { "UR6. Ursun's Roar: an ally 40 m away wavering -> no cast",
      function(b) return { caster(b, URS, { dist_by_target = { [b + 1] = 40 } }), ally(b + 1, { wavering = true }) } end,
      "ursuns_roar_charge", URS, 0, 0 },
  }
  for _, f in ipairs(FILES) do
    local TAG = f.tag
    for i, w in ipairs(WORLDS) do
      local want = RED171 and w[6] or w[5]
      local b = 36000 + i * 20
      local units, opts = w[2](b)
      local W = world(w[1], units, w[3], w[4], f.path, TAG, opts)
      if W ~= nil then
        local got = 0
        for _, x in ipairs(W.fires) do if x.key == w[4] then got = got + 1 end end
        for _, x in ipairs(W.ground_fires or {}) do if x.key == w[4] then got = got + 1 end end
        local a = (got == want)
        check(TAG .. w[1]:sub(1, 3) .. (RED171 and "-RED" or "") .. "a: " .. want .. " cast(s) expected, got " .. got, a)
        done(a)
        if i == 1 then
          local by = {}
          for _, e in ipairs(W.cap or {}) do by[e.marker] = e.card end
          local c_ok = by.horn_of_the_wild_hunt == "Fires when 3+ of your units charge at once (all of them in a smaller army)"
            and by.waaagh_army == "Fires when 3+ of your units charge or fight at once (all of them in a smaller army)"
            and by.ursuns_roar_charge == "Fires when it or a nearby ally charges or wavers"
          check(TAG .. "CA3: the three cards (Waaagh!: " .. tostring(by.waaagh_army) .. ")",
            (RED171 and not c_ok) or (not RED171 and c_ok))
          done((RED171 and not c_ok) or (not RED171 and c_ok))
        end
        tally(W)
      end
    end
  end
  if RED171 then
    check("RED CONTROL (harness 171): the pre-172 build keeps round 171's first proposals - " .. n_ok .. "/" .. n_all,
      n_all == 20 and n_ok == 20)
  else
    check("HARNESS 171: every check behaved - " .. n_ok .. "/" .. n_all, n_all == 20 and n_ok == 20)
  end
  print("== HARNESS 171 done: " .. (checks - pre171) .. " checks in this section ==")
end
