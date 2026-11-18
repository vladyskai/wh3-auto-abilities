-- ============================================================================
-- HARNESS 173 (round 174): THE SCORE 1-2 REVIEW, ROWS 24-50 (user, 2026-11-18: "You may implement items 24 to 50";
--   read F: "Okay, then let's use the caster list").
--   0zz22 the 13 new families wired, the spellcaster table, the SHOT table covers 53 keys, the entries moved.
--   Enemy worlds (the caster at 60 m from every enemy unless stated; enemies idle, so the old in-melee-or-under-fire
--   triggers stay silent):
--   AB1 Amber Bow: a Terrorgheist (2000) and Grave Guard (800) -> ONE cast at the Terrorgheist (large first).
--   HG1 Hand of Gods: a Terrorgheist and Grave Guard -> ONE cast at the Terrorgheist.
--   HG2 Hand of Gods: Zombies (75), Grave Guard (300), Swordsmen (900), no large -> ONE cast at the Swordsmen (the
--       most valuable per soldier, never the armour fallback).
--   DT1 Don't Even Try It: a Vampire standing 60 m away -> ONE cast at it.
--   SC1 Cube of Darkness: a Fire Wizard (300) and a Captain (900) -> ONE cast at the Wizard.
--   SC2 Cube of Darkness: only a Captain -> no cast.
--   BT1 The Black Tongue: a Fire Wizard 120 m away (bound 140 m) -> ONE cast at it.
--   TP1 The Trickster's Pendant: Wizard A alone (900), Wizards B and C 10 m apart (300 each) -> ONE ground cast under B.
--   SP1 Silence the Prey: a Captain (900) and Swordsmen (1500) -> ONE cast at the Captain.
--   PS1 Pageant of Shrikes: two shooting Handgunner units, 30 m (300) and 45 m (900) -> ONE cast at the 900 one.
--   CH1 Chalice of Dark Rain: shooting X alone (500), Y and Z 10 m apart (400 each) -> ONE ground cast under Y.
--   TX1 Transfix: a wavering Captain (500) and a steady Captain (2000) -> ONE cast at the wavering one.
--   TX2 Transfix: no wavering Lord -> no cast.
--   Ally worlds (the caster idle, so the old in-melee ally buffs stay silent):
--   FK1 Fury of Khaine: a charging Handgunner ally 10 m away and charging Swordsmen 20 m away -> ONE cast on the
--       Swordsmen (never a missile unit).
--   FK2 Fury of Khaine: Swordsmen in fresh contact 10 m away and charging Swordsmen 20 m away -> ONE cast on the
--       charging one.
--   VF1 Verminous Fury: wavering in melee - Swordsmen (300), Swordsmen (900), Handgunners (2000) -> ONE cast on the 900.
--   HH1 Helping Hand: a Captain ally in melee 20 m away, the caster idle -> ONE cast on the Captain.
--   IM1 Inspired Marksmanship I: two shooting Handgunner allies, 300 (closer) and 900 -> casts on the 900 only (the
--       mock accepts every repeat cast, so it may cast more than once in 15 s).
--   IM2 Inspired Marksmanship I: a missile ally not shooting -> no cast.
--   OV1 Overseer of the Unseen: in melee - Swordsmen at 40% (300) and Swordsmen at full health (900, closer) -> ONE
--       cast on the 40% one.
--   WH1 Whiplash!: an idle beast ally -> no cast.
--   IH1 Iron-Handed Captain: a routing ally -> ONE cast on it.
--   CA4 the cards of five new families.   DF1 Helping Hand starts armed.
--   RED (pre-174 = round 173): each world's old trigger misses the new target (nottarget) or casts as listed.
-- ============================================================================
function run_h173()
  local L173 = os.getenv("H173_LIVE") or LIVE
  local A173 = os.getenv("H173_ANN") or ANN
  local RED173 = (os.getenv("H173_LIVE") ~= nil) or (os.getenv("H173_ANN") ~= nil)
  local K = {
    AB = "wh2_dlc13_weapon_abilities_amber_bow", HG = "wh2_main_spell_bound_hand_of_gods",
    DT = "wh2_dlc15_lord_abilities_dont_even_try_it", SC = "wh2_main_item_abilities_cube_of_darkness",
    BT = "wh3_dlc27_character_abilities_the_black_tongue", TP = "wh2_main_item_abilities_the_tricksters_pendant",
    SP = "wh3_main_character_abilities_silence_the_prey", PS = "wh2_dlc16_character_abilities_pageant_of_shrikes",
    CH = "wh_dlc03_item_abilities_chalice_of_dark_rain", TX = "wh3_dlc29_lord_abilities_transfix",
    FK = "wh2_main_unit_abilities_fury_of_khaine", VF = "wh3_dlc29_lord_abilities_verminous_fury",
    HH = "wh2_pro08_character_abilities_helping_hand", IM = "wh3_main_lord_abilities_inspired_marksmanship_i",
    OV = "wh3_dlc29_hero_active_overseer_of_the_unseen", WH = "wh2_dlc14_lord_abilities_whiplash",
    IH = "wh3_dlc27_character_abilities_iron_hand_captain",
  }
  local CASTER = "wh2_dlc13_emp_cha_huntsmen_general_0"
  local TG = "wh_main_vmp_mon_terrorgheist"
  local VA = "wh_main_vmp_cha_vampire_0"
  local GG = "wh_main_vmp_inf_grave_guard_0"
  local ZB = "wh_main_vmp_inf_zombie"
  local SW = "wh_main_emp_inf_swordsmen"
  local GUNS = "wh_main_emp_inf_handgunners"
  local CAP = "wh_main_emp_cha_captain_0"
  local WIZ = "wh_main_emp_cha_wizard_fire_0"
  local WOLF = "wh2_dlc09_tmb_mon_dire_wolves"
  local pre173 = checks
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1; at = i + #tok
    end
  end

  print("== HARNESS 173 - section 0zz22: the round-174 tokens ==")
  if not RED173 then
    local NEWF = { "enemy_large_value_shot", "enemy_spellcaster", "enemy_ground_spellcasters", "enemy_missile_value",
      "enemy_ground_shooters", "enemy_commander_wavering", "ally_charge_melee", "ally_wavering_melee", "ally_lord_melee",
      "ally_missile_shooting", "ally_melee_risk", "ally_beast_charge", "ally_routing" }
    for _, f in ipairs({ { name = "live", path = L173 }, { name = "ann", path = A173 } }) do
      local s = read_file(f.path)
      local wired = 0
      for _, fam in ipairs(NEWF) do
        if cp(s, fam .. " = FOURTH.evaluate_" .. fam .. ",") == 1 and cp(s, 'trigger = "' .. fam .. '"') >= 1 then
          wired = wired + 1
        end
      end
      check("0zz22 " .. f.name .. ": 13 families wired and ridden (" .. wired .. "), the spellcaster table, 53 SHOT keys,"
        .. " 937 entries, the emptied families unused",
        wired == 13 and cp(s, "\t{ marker = ") == 937 and cp(s, 'FOURTH.SPELLCASTER_TEXT = "') == 1
        and cp(s, 'if cls == "spellcaster" then return FOURTH.class_keys.spellcaster[t] == true end') == 1
        and cp(s, 'trigger = "enemy_large_shot"') == 7 and cp(s, 'trigger = "enemy_single_drain"') == 12
        and cp(s, 'trigger = "enemy_commander_value"') == 5 and cp(s, 'trigger = "enemy_blob"') == 71
        and cp(s, 'trigger = "ally_missile"') == 0 and cp(s, 'trigger = "ally_beast"') == 0
        and cp(s, 'trigger = "ally_broken"') == 0 and cp(s, 'trigger = "ally_overseer"') == 0)
    end
  end

  local FILES = { { path = A173, tag = "[annotated] " }, { path = L173, tag = "[live] " } }
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
    local sv = o.sv or {}
    local function dress(pr, enemy)
      if pr == nil or pr.unit == nil then return end
      local id = nil
      pcall(function() id = tostring(pr.unit:unique_ui_id()) end)
      if enemy then
        pr.unit.is_visible_to_alliance = function(self, a) return true end
        pr.unit.is_currently_flying = function(self) return false end
      end
      local v = sv[id]
      if v ~= nil then pr.unit.strategic_value = function(self) return v end end
    end
    for i = 1, #(W.enemy_entries or {}) do dress(W.enemy_entries[i], true) end
    for i = 1, #(W.live_entries or {}) do dress(W.live_entries[i], false) end
    sel_event(W, units[1].uid, true); ui(W); ui(W)
    click(W, "zz_auto_badge_" .. marker); ui(W)
    sel_event(W, units[1].uid, false); ui(W)
    W.conflict = true
    polln(W, o.polls or 4)
    return W
  end
  local function caster(b, key, o)
    local c = { name = CASTER, uid = b, owns = { key }, melee = false, dist = 60, pos = { 0, 0, 0 }, width = 2,
                men_alive = 1, unit_class = "com" }
    for k, v in pairs(o or {}) do c[k] = v end
    return c
  end
  local function block(uid, name, x, z, o)
    local e = { uid = uid, name = name, melee = false, pos = { x, 0, z }, width = 29.4, men_alive = 120,
                initial_men = 120, unit_class = "inf_mel", dist = 60 }
    for k, v in pairs(o or {}) do e[k] = v end
    return e
  end
  local function single(uid, name, x, z, cls, o)
    local e = { uid = uid, name = name, melee = false, pos = { x, 0, z }, width = 6, men_alive = 1, initial_men = 1,
                unit_class = cls, dist = 60 }
    for k, v in pairs(o or {}) do e[k] = v end
    return e
  end
  local function ally(uid, name, o)
    local a = { name = name, uid = uid, owns = {}, melee = false, men_alive = 120, initial_men = 120,
                unit_class = "inf_mel" }
    for k, v in pairs(o or {}) do a[k] = v end
    return a
  end
  local CHG = { fast = true, melee = false, target = true, dist = 20 }   -- a unit in its charge window
  local function merge(a, b) local r = {} for k, v in pairs(a) do r[k] = v end for k, v in pairs(b) do r[k] = v end return r end
  local DROPS = { 100, 99, 98, 97, 96, 95, 94, 93, 92, 91, 90, 89, 88, 87, 86, 85, 84, 83, 82, 81, 80 }
  local function S(t) local r = {} for k, v in pairs(t) do r[tostring(k)] = v end return r end
  -- name; builder(b) -> units, enemies, opts; marker; key; GREEN casts; target offset (nil: any); ground x (ground
  -- casts); RED rule: "none" = 0 casts, "nottarget" = no cast on the GREEN target, nil = not run in RED
  local WORLDS = {
    { "AB1. Amber Bow: a Terrorgheist and Grave Guard -> ONE cast at the Terrorgheist",
      function(b) return { caster(b, K.AB) }, { single(b + 5, TG, 0, 100, "mon"), block(b + 6, GG, 60, 100) },
        { sv = S({ [b + 5] = 2000, [b + 6] = 800 }) } end, "weapon_abilities_amber_bow", K.AB, 1, 5, nil, "nottarget" },
    { "HG1. Hand of Gods: a Terrorgheist and Grave Guard -> ONE cast at the Terrorgheist",
      function(b) return { caster(b, K.HG) }, { single(b + 5, TG, 0, 100, "mon"), block(b + 6, GG, 60, 100) },
        { sv = S({ [b + 5] = 2000, [b + 6] = 800 }) } end, "spell_bound_hand_of_gods", K.HG, 1, 5, nil, "nottarget" },
    { "HG2. Hand of Gods: Zombies, Grave Guard (300), Swordsmen (900) -> ONE cast at the Swordsmen",
      function(b) return { caster(b, K.HG) }, { block(b + 5, ZB, 0, 100), block(b + 6, GG, 60, 100),
        block(b + 7, SW, -60, 100) }, { sv = S({ [b + 5] = 75, [b + 6] = 300, [b + 7] = 900 }) } end,
      "spell_bound_hand_of_gods", K.HG, 1, 7, nil, nil },
    { "DT1. Don't Even Try It: a Vampire standing 60 m away -> ONE cast at it",
      function(b) return { caster(b, K.DT) }, { single(b + 5, VA, 0, 100, "com") }, { sv = S({ [b + 5] = 900 }) } end,
      "dont_even_try_it", K.DT, 1, 5, nil, "none" },
    { "SC1. Cube of Darkness: a Fire Wizard (300) and a Captain (900) -> ONE cast at the Wizard",
      function(b) return { caster(b, K.SC) }, { single(b + 5, WIZ, 0, 100, "com"), single(b + 6, CAP, 30, 100, "com") },
        { sv = S({ [b + 5] = 300, [b + 6] = 900 }) } end, "cube_of_darkness", K.SC, 1, 5, nil, "none" },
    { "SC2. Cube of Darkness: only a Captain -> no cast",
      function(b) return { caster(b, K.SC) }, { single(b + 5, CAP, 0, 100, "com") }, { sv = S({ [b + 5] = 900 }) } end,
      "cube_of_darkness", K.SC, 0, nil, nil, "none" },
    { "BT1. The Black Tongue: a Fire Wizard 120 m away -> ONE cast at it",
      function(b) return { caster(b, K.BT, { dist = 120 }) }, { single(b + 5, WIZ, 0, 160, "com", { dist = 120 }) },
        { sv = S({ [b + 5] = 300 }) } end, "the_black_tongue", K.BT, 1, 5, nil, "none" },
    { "TP1. The Trickster's Pendant: Wizard A alone, Wizards B and C 10 m apart -> ONE ground cast under B",
      function(b) return { caster(b, K.TP) }, {
          single(b + 5, WIZ, -80, 100, "com", { dist_by_target = { [b + 6] = 80, [b + 7] = 80 } }),
          single(b + 6, WIZ, 40, 100, "com", { dist_by_target = { [b + 5] = 80, [b + 7] = 10 } }),
          single(b + 7, WIZ, 50, 100, "com", { dist_by_target = { [b + 5] = 80, [b + 6] = 10 } }) },
        { sv = S({ [b + 5] = 900, [b + 6] = 300, [b + 7] = 300 }) } end,
      "the_tricksters_pendant", K.TP, 1, nil, 40, "none" },
    { "SP1. Silence the Prey: a Captain (900) and Swordsmen (1500) -> ONE cast at the Captain",
      function(b) return { caster(b, K.SP) }, { single(b + 5, CAP, 0, 100, "com"), block(b + 6, SW, 60, 100) },
        { sv = S({ [b + 5] = 900, [b + 6] = 1500 }) } end, "silence_the_prey", K.SP, 1, 5, nil, "none" },
    { "PS1. Pageant of Shrikes: shooting Handgunners at 30 m (300) and 45 m (900) -> ONE cast at the 900 one",
      function(b) return { caster(b, K.PS, { dist_by_target = { [b + 5] = 30, [b + 6] = 45 } }) },
        { block(b + 5, GUNS, 0, 100, { ammo_start = 100, ammo_seq = DROPS }),
          block(b + 6, GUNS, 60, 100, { ammo_start = 100, ammo_seq = DROPS }) },
        { sv = S({ [b + 5] = 300, [b + 6] = 900 }) } end, "pageant_of_shrikes", K.PS, 1, 6, nil, "nottarget" },
    { "CH1. Chalice of Dark Rain: shooting X alone (500), Y and Z 10 m apart (400 each) -> ONE ground cast under Y",
      function(b) return { caster(b, K.CH) }, {
          block(b + 5, GUNS, -80, 100, { ammo_start = 100, ammo_seq = DROPS, dist_by_target = { [b + 6] = 80, [b + 7] = 80 } }),
          block(b + 6, GUNS, 40, 100, { ammo_start = 100, ammo_seq = DROPS, dist_by_target = { [b + 5] = 80, [b + 7] = 10 } }),
          block(b + 7, GUNS, 50, 100, { ammo_start = 100, ammo_seq = DROPS, dist_by_target = { [b + 5] = 80, [b + 6] = 10 } }) },
        { sv = S({ [b + 5] = 500, [b + 6] = 400, [b + 7] = 400 }) } end,
      "chalice_of_dark_rain", K.CH, 1, nil, 40, "none" },
    { "TX1. Transfix: a wavering Captain (500) and a steady Captain (2000) -> ONE cast at the wavering one",
      function(b) return { caster(b, K.TX) }, { single(b + 5, CAP, 0, 100, "com", { wavering = true }),
        single(b + 6, CAP, 30, 100, "com") }, { sv = S({ [b + 5] = 500, [b + 6] = 2000 }) } end,
      "transfix_hex", K.TX, 1, 5, nil, "none" },
    { "TX2. Transfix: no wavering Lord -> no cast",
      function(b) return { caster(b, K.TX) }, { single(b + 5, CAP, 0, 100, "com") }, { sv = S({ [b + 5] = 500 }) } end,
      "transfix_hex", K.TX, 0, nil, nil, "none" },
    { "FK1. Fury of Khaine: a charging Handgunner ally 10 m away, charging Swordsmen 20 m away -> ONE cast on the Swordsmen",
      -- the ally picker reads the gap from the ALLY (ally:unit_distance(caster)): each ally carries its own dist
      function(b) return { caster(b, K.FK), ally(b + 1, GUNS, merge(CHG, { dist = 10 })),
        ally(b + 2, SW, merge(CHG, { dist = 20 })) }, nil, {} end, "fury_of_khaine", K.FK, 1, 2, nil, "none" },
    { "FK2. Fury of Khaine: fresh contact 10 m away, charging 20 m away -> ONE cast on the charging one",
      function(b) return { caster(b, K.FK), ally(b + 1, SW, { melee = true, dist = 10 }),
        ally(b + 2, SW, merge(CHG, { dist = 20 })) }, nil, {} end, "fury_of_khaine", K.FK, 1, 2, nil, "none" },
    { "VF1. Verminous Fury: wavering in melee - Swordsmen 300, Swordsmen 900, Handgunners 2000 -> ONE cast on the 900",
      function(b) return { caster(b, K.VF), ally(b + 1, SW, { melee = true, wavering = true }),
        ally(b + 2, SW, { melee = true, wavering = true }), ally(b + 3, GUNS, { melee = true, wavering = true }) }, nil,
        { sv = S({ [b + 1] = 300, [b + 2] = 900, [b + 3] = 2000 }) } end, "verminous_fury", K.VF, 1, 2, nil, "none" },
    { "HH1. Helping Hand: a Captain ally in melee 20 m away, the caster idle -> ONE cast on the Captain",
      function(b) return { caster(b, K.HH, { dist = 20 }), ally(b + 1, CAP, { melee = true, men_alive = 1, initial_men = 1,
        unit_class = "com" }) }, nil, {} end, "helping_hand", K.HH, 1, 1, nil, "none" },
    { "IM1. Inspired Marksmanship I: shooting allies 300 (10 m) and 900 (30 m) -> ONE cast on the 900",
      function(b) return { caster(b, K.IM), ally(b + 1, GUNS, { ammo_start = 100, ammo_seq = { 100, 99 }, dist = 10 }),
        ally(b + 2, GUNS, { ammo_start = 100, ammo_seq = { 100, 99 }, dist = 30 }) }, nil,
        { sv = S({ [b + 1] = 300, [b + 2] = 900 }), polls = 60 } end,
      "inspired_marksmanship_i", K.IM, -1, 2, nil, "nottarget" },
    { "IM2. Inspired Marksmanship I: a missile ally not shooting -> no cast",
      function(b) return { caster(b, K.IM), ally(b + 1, GUNS, { ammo_start = 100, ammo_seq = { 100 } }) }, nil, {} end,
      "inspired_marksmanship_i", K.IM, 0, nil, nil, nil },
    { "OV1. Overseer of the Unseen: in melee - 40% health (300) and full health (900, closer) -> ONE cast on the 40% one",
      function(b) return { caster(b, K.OV), ally(b + 1, SW, { melee = true, hp_frac = 0.4, dist = 30 }),
        ally(b + 2, SW, { melee = true, dist = 10 }) }, nil,
        { sv = S({ [b + 1] = 300, [b + 2] = 900 }) } end, "overseer_of_the_unseen", K.OV, 1, 1, nil, "nottarget" },
    { "WH1. Whiplash!: an idle beast ally -> no cast",
      function(b) return { caster(b, K.WH), ally(b + 1, WOLF, { unit_class = "mon" }) }, nil, {} end,
      "whiplash", K.WH, 0, nil, nil, nil },
    { "IH1. Iron-Handed Captain: a routing ally -> ONE cast on it",
      function(b) return { caster(b, K.IH), ally(b + 1, SW, { routing = true }) }, nil, {} end,
      "iron_hand_captain", K.IH, 1, 1, nil, "none" },
  }
  for _, f in ipairs(FILES) do
    local TAG = f.tag
    for i, w in ipairs(WORLDS) do
      if not (RED173 and w[8] == nil) then
        local b = 38000 + i * 20
        local units, enemies, opts = w[2](b)
        local W = world(w[1], units, enemies, w[3], w[4], f.path, TAG, opts)
        if W ~= nil then
          local got, on_target, gx = 0, 0, nil
          for _, x in ipairs(W.fires) do
            if x.key == w[4] then
              got = got + 1
              local tid = nil
              pcall(function() tid = tostring(x.target:unique_ui_id()) end)
              if w[6] ~= nil and tid == tostring(b + w[6]) then on_target = on_target + 1 end
            end
          end
          for _, x in ipairs(W.ground_fires or {}) do
            if x.key == w[4] then
              got = got + 1
              pcall(function() gx = x.pos:get_x() end)
            end
          end
          local a, txt
          if RED173 then
            if w[8] == "none" then a = (got == 0) else a = (on_target == 0) end
            txt = "-REDa: rule " .. w[8] .. ", got " .. got .. " cast(s), " .. on_target .. " on the new target"
          else
            a = (got == w[5])
            if w[5] == -1 then a = (got >= 1 and on_target == got) end   -- the mock accepts every repeat cast
            if w[5] > 0 and w[6] ~= nil then a = a and on_target == w[5] end
            if w[5] > 0 and w[7] ~= nil then a = a and gx == w[7] end
            txt = "a: " .. w[5] .. " cast(s) expected, got " .. got .. ", on target " .. on_target
              .. ((w[7] ~= nil) and (", ground x " .. tostring(gx) .. " want " .. w[7]) or "")
          end
          check(TAG .. w[1]:sub(1, 3) .. txt, a)
          done(a)
          if i == 1 then
            local by, armed = {}, {}
            for _, e in ipairs(W.cap or {}) do by[e.marker] = e.card end
            local c_ok = by.spell_bound_hand_of_gods == "Fires at the most valuable large enemy, else at the best infantry"
              and by.cube_of_darkness == "Fires at the most valuable enemy spellcaster"
              and by.chalice_of_dark_rain == "Fires under the thickest group of shooting enemies"
              and by.inspired_marksmanship_i == "Fires on the most valuable shooting missile ally"
              and by.iron_hand_captain == "Fires on the most valuable routing ally"
            check(TAG .. "CA4: the cards of five new families (Cube: " .. tostring(by.cube_of_darkness) .. ")",
              (RED173 and not c_ok) or (not RED173 and c_ok))
            done((RED173 and not c_ok) or (not RED173 and c_ok))
          end
          tally(W)
        end
      end
    end
  end
  if not RED173 then
    for _, f in ipairs(FILES) do
      local s = read_file(f.path)
      local i = raw_find(s, '{ marker = "helping_hand", name = "Helping Hand", trigger = "ally_lord_melee",', 1, true)
      local blk = i and s:sub(i, i + 400) or ""
      local a = raw_find(blk, "start_armed = true,", 1, true) ~= nil
      check(f.tag .. "DF1: Helping Hand keeps its default (start_armed)", a)
      done(a)
    end
  end
  local want_n = RED173 and 40 or 48
  if RED173 then
    check("RED CONTROL (harness 173): the pre-174 build keeps the old triggers - " .. n_ok .. "/" .. n_all,
      n_all == want_n and n_ok == want_n)
  else
    check("HARNESS 173: every check behaved - " .. n_ok .. "/" .. n_all, n_all == want_n and n_ok == want_n)
  end
  print("== HARNESS 173 done: " .. (checks - pre173) .. " checks in this section ==")
end
