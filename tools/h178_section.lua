-- ============================================================================
-- HARNESS 178 (round 179): THE SCORE-3 REVIEW, ROWS 115-134 (user, 2026-11-18: "Items 115-134 approved"), built from
--   the CURRENT text of each row on disk.
--   0zz27 the 6 new families wired, 12 entries moved (start_armed kept), the 5 ranked modes, the heal re-check modes,
--         the wavering pair without its melee condition, Grut's Sickle's winds gate.
--   IA1 Inspired Assault I: the caster NOT in melee, an ally in melee 20 m away -> ONE cast at it (RED: none).
--   IA2 Inspired Assault I: a Handgunner ally in melee -> no cast (never a missile unit).
--   ID1 Inspired Defence I: a plain ally in melee 15 m away and a WAVERING one in melee 40 m away -> ONE cast at the
--       wavering one (RED: none, the caster is not in melee).
--   OB1 Orcs are da Best!: allies in melee worth 300 (15 m) and 900 (40 m) -> ONE cast at the 900 (RED: none).
--   HV1 Hellish Vigour: an ally in melee 30 m away, the caster not in melee -> ONE cast at it (RED: none).
--   HV2 Hellish Vigour: an ally NOT in melee -> no cast.
--   FF1 Favour of the Fay: the caster not in melee, an ally in melee 30 m away -> ONE cast at it (RED: none).
--   BW1 Berry Wine: an ally at 65% -> no cast (RED: one, the old line was 75%).
--   BW2 Berry Wine: an ally at 50% -> ONE cast at it.
--   SA1 Star of Avelorn: a hurt ally (60%) alone 60 m away -> ONE ground cast under it (RED: none, 10 m reach).
--   SA2 Star of Avelorn: a hurt ally alone at 30 m (50%) and two hurt allies 5 m apart at 80 m (65%, 70%) -> ONE
--       ground cast under the 65% one (the most hurt units around it) (RED: none).
--   CP1 Commanding Presence: an ally wavering, NOT in melee, 20 m away -> ONE cast (RED: none, it needed melee).
--   GR1 Grut's Sickle: winds 50 / reserve 30 (not low), an ally -> no cast (RED: one, it fired when ready).
--   GR2 Grut's Sickle: winds 12 / reserve 68; Skavenslaves (expendable, 800 hp) and Swordsmen (2,000 hp) -> ONE cast
--       at the Skavenslaves (RED: not them, the old pick was the most hit points).
--   GR3 Grut's Sickle: winds low, no expendable ally; Swordsmen worth 300 at 90%, Greatswords worth 900 at 95% (more
--       hit points), a 50% unit worth 80 -> ONE cast at the Swordsmen (RED: not them).
--   CA7 the cards of the 6 new families and Grut's Sickle.
--   RED control: H178_LIVE / H178_ANN on docs/backups/round179/pre179_*.lua.
-- ============================================================================
function run_h178()
  local L178 = os.getenv("H178_LIVE") or LIVE
  local A178 = os.getenv("H178_ANN") or ANN
  local RED178 = (os.getenv("H178_LIVE") ~= nil) or (os.getenv("H178_ANN") ~= nil)
  local K = {
    IA = "wh3_main_lord_abilities_inspired_assault_i", ID = "wh3_main_lord_abilities_inspired_defence_i",
    OB = "wh3_dlc26_character_abilities_orcs_are_da_best", HV = "wh3_dlc29_lord_abilities_hellish_vigour",
    FF = "wh_dlc07_lord_abilities_favour_of_the_fay", BW = "wh2_dlc16_item_abilities_berry_wine",
    SA = "wh2_dlc10_item_abilities_star_of_avelorn", CP = "wh3_dlc29_lord_active_commanding_presence",
    GR = "wh3_main_item_abilities_gruts_sickle",
  }
  local CASTER = "wh2_dlc13_emp_cha_huntsmen_general_0"
  local SW = "wh_main_emp_inf_swordsmen"
  local GS = "wh_main_emp_inf_greatswords"
  local GUNS = "wh_main_emp_inf_handgunners"
  local SLAVES = "wh2_main_skv_inf_skavenslaves_0"
  local pre178 = checks
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1; at = i + #tok
    end
  end
  print("== HARNESS 178 - section 0zz27: the round-179 tokens ==")
  if not RED178 then
    for _, f in ipairs({ { name = "live", path = L178 }, { name = "ann", path = A178 } }) do
      local s = read_file(f.path)
      local wired = 0
      for _, fam in ipairs({ "ally_charge_or_melee", "ally_melee_wavering_first", "ally_value_melee", "ally_in_melee",
                             "health_aura_ally_deep", "heal_ground_best" }) do
        if cp(s, fam .. " = FOURTH.evaluate_" .. fam .. ",") == 1 and cp(s, 'trigger = "' .. fam .. '"') >= 1 then
          wired = wired + 1
        end
      end
      local ranked = 0
      for _, r in ipairs({ "charge_contact_melee", "melee_wavering_first", "value_melee", "expendable_hp", "cheap_healthy" }) do
        if cp(s, 'if family == "' .. r .. '" then') == 1 then ranked = ranked + 1 end
      end
      check("0zz27 " .. f.name .. ": 6 families wired (" .. wired .. "), 12 moved with start_armed, 5 ranked modes ("
        .. ranked .. "), the spot/deep re-checks, no wavering melee condition, the winds gate",
        wired == 6 and ranked == 5 and cp(s, "-- ROUND 179 (score-3 review): ") == 12
        and cp(s, "\t\tstart_armed = true,\n") == 33 and cp(s, 'if FOURTH.ah_mode == "spot" then') == 1
        and cp(s, 'if FOURTH.ah_mode == "deep" then') == 1
        and cp(s, "and not unit_is_routing(other)   -- ROUND 179: no melee condition") == 1
        and cp(s, "if c == nil or c >= FOURTH.WINDS_LOW_POOL or r < FOURTH.WINDS_LOW_RESERVE then return nil end") == 2
        and cp(s, 'trigger = "ally_melee_buff"') == 1)
    end
  end
  local FILES = { { path = A178, tag = "[annotated] " }, { path = L178, tag = "[live] " } }
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
    if o.winds ~= nil then
      local army = {}
      function army:winds_of_magic_current() return o.winds[1] end
      function army:winds_of_magic_reserve() return o.winds[2] end
      function army:winds_of_magic_remaining_recharge_rate() return 0 end
      W.bm.get_player_army = function() return army end
    end
    OH77.cap = nil
    local ok = pcall(load_world, W, PATH)
    check(TAG .. wname .. ": the file loads", ok)
    if not ok then tally(W); return nil end
    W.cap = OH77.cap
    deploy_phases(W); ui(W)
    if o.sv ~= nil then
      for uid, v in pairs(o.sv) do
        local u = unit_of(W, uid)
        if u ~= nil then u.strategic_value = function(self) return v end end
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
    local c = { name = CASTER, uid = b, owns = { key }, melee = false, dist = 30, health_percent = 100 }
    for k, v in pairs(o or {}) do c[k] = v end
    return c
  end
  local function ally(uid, name, o)
    local a = { name = name, uid = uid, owns = {}, melee = false, dist = 30, health_percent = 100, in_range = true }
    for k, v in pairs(o or {}) do a[k] = v end
    return a
  end
  -- name; builder(b) -> units, opts; marker; key; GREEN casts; GREEN target offset (unit form) or "g<offset>" (ground
  -- form under that unit); RED rule ("none" = 0 casts, "one" = 1, "nottarget" = none on the GREEN target, "same")
  local WORLDS = {
    { "IA1. Inspired Assault I: the caster not in melee, an ally in melee 20 m away -> ONE cast at it",
      function(b) return { caster(b, K.IA), ally(b + 5, SW, { melee = true, dist = 20 }) } end,
      "inspired_assault_i", K.IA, 1, 5, "none" },
    { "IA2. Inspired Assault I: a Handgunner ally in melee -> no cast (never a missile unit)",
      function(b) return { caster(b, K.IA), ally(b + 5, GUNS, { melee = true, dist = 20 }) } end,
      "inspired_assault_i", K.IA, 0, nil, "none" },
    { "ID1. Inspired Defence I: a plain ally in melee 15 m, a wavering one in melee 40 m -> ONE cast at the wavering one",
      function(b) return { caster(b, K.ID), ally(b + 5, SW, { melee = true, dist = 15 }),
        ally(b + 6, SW, { melee = true, wavering = true, dist = 40 }) } end,
      "inspired_defence_i", K.ID, 1, 6, "none" },
    { "OB1. Orcs are da Best!: allies in melee worth 300 (15 m) and 900 (40 m) -> ONE cast at the 900",
      function(b) return { caster(b, K.OB), ally(b + 5, SW, { melee = true, dist = 15 }),
        ally(b + 6, GS, { melee = true, dist = 40 }) }, { sv = { [b + 5] = 300, [b + 6] = 900 } } end,
      "orcs_are_da_best", K.OB, 1, 6, "none" },
    { "HV1. Hellish Vigour: an ally in melee 30 m away, the caster not in melee -> ONE cast at it",
      function(b) return { caster(b, K.HV), ally(b + 5, SW, { melee = true, dist = 30 }) } end,
      "hellish_vigour", K.HV, 1, 5, "none" },
    { "HV2. Hellish Vigour: an ally NOT in melee -> no cast",
      function(b) return { caster(b, K.HV), ally(b + 5, SW, { dist = 20 }) } end,
      "hellish_vigour", K.HV, 0, nil, "none" },
    { "FF1. Favour of the Fay: the caster not in melee, an ally in melee 30 m away -> ONE cast at it",
      function(b) return { caster(b, K.FF), ally(b + 5, SW, { melee = true, dist = 30 }) } end,
      "favour_of_the_fay", K.FF, 1, 5, "none" },
    { "BW1. Berry Wine: an ally at 65% -> no cast",
      function(b) return { caster(b, K.BW), ally(b + 5, SW, { health_percent = 65, dist = 20 }) } end,
      "berry_wine", K.BW, 0, nil, "one" },
    { "BW2. Berry Wine: an ally at 50% -> ONE cast at it",
      function(b) return { caster(b, K.BW), ally(b + 5, SW, { health_percent = 50, dist = 20 }) } end,
      "berry_wine", K.BW, 1, 5, "same" },
    { "SA1. Star of Avelorn: a hurt ally (60%) alone 60 m away -> ONE ground cast under it",
      function(b) return { caster(b, K.SA), ally(b + 5, SW, { health_percent = 60, dist = 60 }) } end,
      "star_of_avelorn", K.SA, 1, "g5", "none" },
    { "SA2. Star of Avelorn: a lone 50% ally at 30 m, two hurt allies 5 m apart at 80 m -> ONE ground cast under the 65%",
      function(b) return { caster(b, K.SA),
        ally(b + 5, SW, { health_percent = 50, dist = 30, dist_by_target = { [b + 6] = 60, [b + 7] = 60 } }),
        ally(b + 6, SW, { health_percent = 65, dist = 80, dist_by_target = { [b + 5] = 60, [b + 7] = 5 } }),
        ally(b + 7, GS, { health_percent = 70, dist = 80, dist_by_target = { [b + 5] = 60, [b + 6] = 5 } }) } end,
      "star_of_avelorn", K.SA, 1, "g6", "none" },
    { "CP1. Commanding Presence: an ally wavering, NOT in melee, 20 m away -> ONE cast",
      function(b) return { caster(b, K.CP), ally(b + 5, SW, { wavering = true, dist = 20 }) } end,
      "commanding_presence", K.CP, 1, nil, "none" },
    { "GR1. Grut's Sickle: winds 50 / reserve 30 (not low), an ally -> no cast",
      function(b) return { caster(b, K.GR), ally(b + 5, SW, { dist = 20, ctx = { HealthValue = 1000 } }) },
        { winds = { 50, 30 } } end,
      "gruts_sickle", K.GR, 0, nil, "one" },
    { "GR2. Grut's Sickle: winds low; Skavenslaves (expendable, 800 hp), Swordsmen (2,000 hp) -> ONE cast at the Skavenslaves",
      function(b) return { caster(b, K.GR), ally(b + 5, SLAVES, { dist = 30, ctx = { HealthValue = 800 } }),
        ally(b + 6, SW, { dist = 20, ctx = { HealthValue = 2000 } }) }, { winds = { 12, 68 } } end,
      "gruts_sickle", K.GR, 1, 5, "nottarget" },
    { "GR3. Grut's Sickle: winds low, no expendable; Swordsmen 300 at 90%, Greatswords 900 at 95%, a 50% unit -> ONE cast at the Swordsmen",
      function(b) return { caster(b, K.GR),
        ally(b + 5, SW, { dist = 30, health_percent = 90, ctx = { HealthValue = 1000 } }),
        ally(b + 6, GS, { dist = 20, health_percent = 95, ctx = { HealthValue = 3000 } }),
        ally(b + 7, SW, { dist = 25, health_percent = 50, ctx = { HealthValue = 500 } }) },
        { winds = { 12, 68 }, sv = { [b + 5] = 300, [b + 6] = 900, [b + 7] = 80 } } end,
      "gruts_sickle", K.GR, 1, 5, "nottarget" },
  }
  for _, f in ipairs(FILES) do
    local TAG = f.tag
    for i, w in ipairs(WORLDS) do
      local b = 43000 + i * 20
      local units, o = w[2](b)
      local W = world(w[1], units, w[3], w[4], f.path, TAG, o)
      if W ~= nil then
        local got, on_t = 0, 0
        local want = w[6]
        local ground = (type(want) == "string")
        local tuid = nil
        if want ~= nil then tuid = tostring(b + (ground and tonumber(want:sub(2)) or want)) end
        for _, x in ipairs(W.fires) do
          if x.key == w[4] then
            got = got + 1
            local tid = nil
            pcall(function() tid = tostring(x.target:unique_ui_id()) end)
            if not ground and tuid ~= nil and tid == tuid then on_t = on_t + 1 end
          end
        end
        for _, x in ipairs(W.ground_fires or {}) do
          if x.key == w[4] then
            got = got + 1
            if ground and x.pos ~= nil and x.pos.marker == ("pos:" .. tuid) then on_t = on_t + 1 end
          end
        end
        local a, txt
        if RED178 then
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
          local c_ok = by.inspired_assault_i == "Fires on an ally charging, else just in contact, else in melee; no missile units"
            and by.inspired_defence_i == "Fires on the nearest ally in melee, a wavering one first"
            and by.orcs_are_da_best == "Fires on the most valuable ally in melee; no missile units"
            and by.hellish_vigour == "Fires on the nearest ally in melee"
            and by.berry_wine == "Fires on the most hurt unit nearby, below 55% health"
            and by.star_of_avelorn == "Fires under the hurt unit with the most hurt units around it"
            and by.gruts_sickle == "Fires when the winds run low, on an expendable ally, else the cheapest healthy one"
          check(TAG .. "CA7: the cards of the 6 new families and Grut's Sickle (" .. tostring(by.star_of_avelorn) .. ")",
            (RED178 and not c_ok) or (not RED178 and c_ok))
          done((RED178 and not c_ok) or (not RED178 and c_ok))
        end
        tally(W)
      end
    end
  end
  if RED178 then
    check("RED CONTROL (harness 178): the pre-179 build keeps the old triggers - " .. n_ok .. "/" .. n_all,
      n_all == 32 and n_ok == 32)
  else
    check("HARNESS 178: every check behaved - " .. n_ok .. "/" .. n_all, n_all == 32 and n_ok == 32)
  end
  print("== HARNESS 178 done: " .. (checks - pre178) .. " checks in this section ==")
end
