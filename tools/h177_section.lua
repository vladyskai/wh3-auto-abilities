-- ============================================================================
-- HARNESS 177 (round 178): THE SCORE-3 REVIEW, ROWS 23-55 (user, 2026-11-18: "Approve rows 23-55. Row 56 stays"),
--   built from the review doc's RULED texts (rows 23-24, 29, 36-41, 44-45, 49, 53).
--   0zz26 the 3 new families wired, 20 entries moved, Trophy Heads split (938 entries), the fire-first picker option,
--         Eye of Khorne's pick ranks the value first, the 16-model floor.
--   SO1 The Soulstealer: an idle 120-man block, the caster standing -> ONE ground cast (RED: none, it needed melee).
--   CL1 Chain Lightning: an 80-man block (value 800) and a 120-man block (value 600) -> ONE cast at the 80 (both
--       count as 75, the higher value per soldier wins).
--   CL2 Chain Lightning: a 20-man block alone -> ONE cast (FIRST-PASS RED: none, it asked 75 men).
--   CL3 Chain Lightning: a 12-man block alone -> no cast (the 16-model floor).
--   WP1 Word of Pain: an enemy in melee -> ONE cast at it.
--   WP2 Word of Pain: a shooting Handgunner unit, not in melee -> ONE cast at it (RED: none).
--   RT1 Net of Amyntok: a fast enemy closing 25 m away and an enemy in melee 15 m away -> ONE cast at the fast one
--       (RED: the melee one).
--   RT2 Net of Amyntok: only an enemy in melee -> no cast (no melee arm; RED and FIRST-PASS RED: one).
--   PA1 Prey of Anath Raema: an enemy under our fire 25 m away and one in melee 15 m away -> ONE cast at the one under
--       fire (RED: the melee one).
--   GL1 Glory Seeker: an enemy Captain under our fire, not in melee -> no cast (RED: one).
--   GL2 Glory Seeker: an enemy Captain charging 25 m away -> ONE cast (RED and FIRST-PASS RED: none).
--   GL3 Glory Seeker: an enemy Captain in melee -> ONE cast.
--   PB1 Prey of the Blood God: an idle enemy Captain -> ONE cast (RED: none).
--   VP1 Void Pendulum: an idle Fire Wizard -> ONE cast (RED: none).   VP2 an idle Captain -> no cast.
--   EK1 Eye of Khorne: a 3-man remnant at 10% (value 50) and a 40-man unit at 15% (value 400) -> ONE cast at the 400
--       (RED: the remnant).
--   TH1 Trophy Heads (Daemon Wings key): a Swordsmen unit in melee -> ONE cast (RED: none, it was Lord/Hero only).
--   CA6 the cards of the 3 new families, the roots and Eye of Khorne's family.
--   Two RED controls: H177_LIVE / H177_ANN on docs/backups/round178/pre178_*.lua (rule 7 of each world), and with
--   H177_RED2=1 on docs/backups/round178/first178_*.lua, the first pass that built the older proposals (rule 8).
--   'any' = not compared in that RED (the older family's answer is not the question).
-- ============================================================================
function run_h177()
  local L177 = os.getenv("H177_LIVE") or LIVE
  local A177 = os.getenv("H177_ANN") or ANN
  local RED177 = (os.getenv("H177_LIVE") ~= nil) or (os.getenv("H177_ANN") ~= nil)
  local RED2 = RED177 and os.getenv("H177_RED2") == "1"
  local K = {
    SO = "wh3_dlc29_spell_bound_undeath_khizaar_the_soulstealer", WP = "wh2_dlc10_spell_bound_word_of_pain",
    NA = "wh_dlc04_spell_bound_net_of_amyntok", PA = "wh_dlc05_character_abilities_prey_of_anath_raema",
    GL = "wh3_dlc29_hero_active_glory_seeker", PB = "wh3_pro12_hero_abilities_prey_of_the_blood_god",
    VP = "wh3_main_item_abilities_void_pendulum", EK = "wh3_dlc26_lord_abilities_eye_of_khorne",
    TH = "wh3_main_daemon_wings_abilities_trophy_heads", CL = "wh3_dlc27_spell_heavens_chain_lightning_bound",
  }
  local CASTER = "wh2_dlc13_emp_cha_huntsmen_general_0"
  local SW = "wh_main_emp_inf_swordsmen"
  local GUNS = "wh_main_emp_inf_handgunners"
  local CAP = "wh_main_emp_cha_captain_0"
  local WIZ = "wh_main_emp_cha_wizard_fire_0"
  local DROPS = { 100, 99, 98, 97, 96, 95, 94, 93, 92, 91, 90, 89, 88, 87, 86, 85 }
  local pre177 = checks
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1; at = i + #tok
    end
  end
  print("== HARNESS 177 - section 0zz26: the round-178 tokens ==")
  if not RED177 then
    for _, f in ipairs({ { name = "live", path = L177 }, { name = "ann", path = A177 } }) do
      local s = read_file(f.path)
      local wired = 0
      for _, fam in ipairs({ "enemy_fast_or_melee", "enemy_fast_fire_melee", "enemy_most_models" }) do
        if cp(s, fam .. " = FOURTH.evaluate_" .. fam .. ",") == 1 and cp(s, 'trigger = "' .. fam .. '"') >= 1 then
          wired = wired + 1
        end
      end
      check("0zz26 " .. f.name .. ": 3 families wired (" .. wired .. "), 20 moved, Trophy Heads split, fire-first, value-first, floor 16",
        wired == 3 and cp(s, "-- ROUND 178 (score-3 review): ") == 20 and cp(s, "\t{ marker = ") == 938
        and cp(s, "local v, bv = FOURTH.unit_value(enemy), FOURTH.unit_value(best_enemy)") == 1
        and cp(s, '{ marker = "trophy_heads_daemon_wings", name = "Trophy Heads", trigger = "enemy_melee",') == 1
        and cp(s, '(arm == (FOURTH.eg_fire_first and "missile" or "melee")') == 1
        and cp(s, "\nFOURTH.MODELS_FLOOR = 16\n") == 1
        and cp(s, 'trigger = "enemy_most_models"') == 3 and cp(s, 'trigger = "enemy_fast_or_melee"') == 2)
    end
  end
  local FILES = { { path = A177, tag = "[annotated] " }, { path = L177, tag = "[live] " } }
  local n_ok, n_all = 0, 0
  local function done(ok) n_all = n_all + 1; if ok then n_ok = n_ok + 1 end end
  local function world(wname, units, enemies, marker, key, PATH, TAG, sv)
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
        if sv ~= nil and sv[id] ~= nil then
          local v = sv[id]
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
    local c = { name = CASTER, uid = b, owns = { key }, melee = false, dist = 30, pos = { 0, 0, 0 }, width = 2,
                men_alive = 1, unit_class = "com" }
    for k, v in pairs(o or {}) do c[k] = v end
    return c
  end
  local function block(uid, name, x, z, o)
    local e = { uid = uid, name = name, melee = false, pos = { x, 0, z }, width = 29.4, men_alive = 120,
                initial_men = 120, unit_class = "inf_mel", dist = 30 }
    for k, v in pairs(o or {}) do e[k] = v end
    return e
  end
  local function single(uid, name, x, z, o)
    local e = { uid = uid, name = name, melee = false, pos = { x, 0, z }, width = 6, men_alive = 1, initial_men = 1,
                unit_class = "com", dist = 30 }
    for k, v in pairs(o or {}) do e[k] = v end
    return e
  end
  local function S(t) local r = {} for k, v in pairs(t) do r[tostring(k)] = v end return r end
  -- name; builder(b) -> units, enemies, sv; marker; key; GREEN casts; GREEN target offset; RED rule vs pre178; RED rule
  -- vs the first pass ("none" = 0 casts, "one" = 1, "nottarget" = no cast on the GREEN target, "same" = as GREEN,
  -- "any" = not compared)
  local WORLDS = {
    { "SO1. The Soulstealer: an idle 120-man block -> ONE ground cast",
      function(b) return { caster(b, K.SO) }, { block(b + 5, SW, 0, 60) }, S({ [b + 5] = 600 }) end,
      "the_soulstealer", K.SO, 1, nil, "none", "same" },
    { "CL1. Chain Lightning: an 80-man block (800) and a 120-man block (600) -> ONE cast at the 80",
      function(b) return { caster(b, K.CL) },
        { block(b + 5, SW, 0, 60, { men_alive = 80 }), block(b + 6, SW, 40, 60) }, S({ [b + 5] = 800, [b + 6] = 600 }) end,
      "spell_heavens_chain_lightning_bound", K.CL, 1, 5, "any", "same" },
    { "CL2. Chain Lightning: a 20-man block alone -> ONE cast",
      function(b) return { caster(b, K.CL) }, { block(b + 5, SW, 0, 60, { men_alive = 20 }) }, S({ [b + 5] = 200 }) end,
      "spell_heavens_chain_lightning_bound", K.CL, 1, nil, "any", "none" },
    { "CL3. Chain Lightning: a 12-man block alone -> no cast (the floor)",
      function(b) return { caster(b, K.CL) }, { block(b + 5, SW, 0, 60, { men_alive = 12 }) }, S({ [b + 5] = 120 }) end,
      "spell_heavens_chain_lightning_bound", K.CL, 0, nil, "any", "same" },
    { "WP1. Word of Pain: an enemy in melee -> ONE cast at it",
      function(b) return { caster(b, K.WP) }, { block(b + 5, SW, 0, 60, { melee = true }) }, nil end,
      "word_of_pain", K.WP, 1, 5, "same", "same" },
    { "WP2. Word of Pain: a shooting Handgunner unit, not in melee -> ONE cast at it",
      function(b) return { caster(b, K.WP) }, { block(b + 5, GUNS, 0, 60, { ammo_start = 100, ammo_seq = DROPS }) }, nil end,
      "word_of_pain", K.WP, 1, 5, "none", "same" },
    { "RT1. Net of Amyntok: a fast enemy closing 25 m away, an enemy in melee 15 m away -> ONE cast at the fast one",
      function(b) return { caster(b, K.NA, { dist_by_target = { [b + 5] = 25, [b + 6] = 15 } }) },
        { block(b + 5, SW, 0, 60, { moving = true, fast_speed = 8 }), block(b + 6, SW, 40, 60, { melee = true }) }, nil end,
      "net_of_amyntok", K.NA, 1, 5, "nottarget", "same" },
    { "RT2. Net of Amyntok: only an enemy in melee -> no cast (no melee arm)",
      function(b) return { caster(b, K.NA, { dist = 15 }) }, { block(b + 5, SW, 0, 60, { melee = true, dist = 15 }) }, nil end,
      "net_of_amyntok", K.NA, 0, nil, "one", "one" },
    { "PA1. Prey of Anath Raema: under our fire 25 m away, in melee 15 m away -> ONE cast at the one under fire",
      function(b) return { caster(b, K.PA, { dist_by_target = { [b + 5] = 25, [b + 6] = 15 } }) },
        { block(b + 5, SW, 0, 60, { missile = true }), block(b + 6, SW, 40, 60, { melee = true }) }, nil end,
      "prey_of_anath_raema", K.PA, 1, 5, "nottarget", "same" },
    { "GL1. Glory Seeker: an enemy Captain under our fire, not in melee -> no cast",
      function(b) return { caster(b, K.GL) }, { single(b + 5, CAP, 0, 60, { missile = true }) }, nil end,
      "glory_seeker", K.GL, 0, nil, "one", "same" },
    { "GL2. Glory Seeker: an enemy Captain charging 25 m away -> ONE cast",
      function(b) return { caster(b, K.GL, { dist = 25 }) },
        { single(b + 5, CAP, 0, 60, { moving = true, fast_speed = 8, dist = 25 }) }, nil end,
      "glory_seeker", K.GL, 1, 5, "none", "none" },
    { "GL3. Glory Seeker: an enemy Captain in melee -> ONE cast",
      function(b) return { caster(b, K.GL) }, { single(b + 5, CAP, 0, 60, { melee = true }) }, nil end,
      "glory_seeker", K.GL, 1, 5, "same", "same" },
    { "PB1. Prey of the Blood God: an idle enemy Captain -> ONE cast",
      function(b) return { caster(b, K.PB) }, { single(b + 5, CAP, 0, 60) }, S({ [b + 5] = 900 }) end,
      "prey_of_the_blood_god", K.PB, 1, 5, "none", "same" },
    { "VP1. Void Pendulum: an idle Fire Wizard -> ONE cast",
      function(b) return { caster(b, K.VP) }, { single(b + 5, WIZ, 0, 60) }, S({ [b + 5] = 600 }) end,
      "void_pendulum", K.VP, 1, 5, "none", "same" },
    { "VP2. Void Pendulum: an idle Captain -> no cast",
      function(b) return { caster(b, K.VP) }, { single(b + 5, CAP, 0, 60) }, S({ [b + 5] = 600 }) end,
      "void_pendulum", K.VP, 0, nil, "none", "same" },
    { "EK1. Eye of Khorne: a remnant at 10% (50) and a 40-man unit at 15% (400) -> ONE cast at the 400",
      function(b) return { caster(b, K.EK, { dist = 20 }) },
        { block(b + 5, SW, 0, 60, { men_alive = 3, hp_frac = 0.10, dist = 20 }),
          block(b + 6, SW, 40, 60, { men_alive = 40, hp_frac = 0.15, dist = 20 }) }, S({ [b + 5] = 50, [b + 6] = 400 }) end,
      "eye_of_khorne", K.EK, 1, 6, "nottarget", "same" },
    { "TH1. Trophy Heads (Daemon Wings): Swordsmen in melee -> ONE cast",
      function(b) return { caster(b, K.TH) }, { block(b + 5, SW, 0, 60, { melee = true }) }, nil end,
      "trophy_heads_daemon_wings", K.TH, 1, 5, "none", "same" },
  }
  for _, f in ipairs(FILES) do
    local TAG = f.tag
    for i, w in ipairs(WORLDS) do
      local b = 41000 + i * 20
      local units, enemies, sv = w[2](b)
      local W = world(w[1], units, enemies, w[3], w[4], f.path, TAG, sv)
      if W ~= nil then
        local got, on_t = 0, 0
        for _, x in ipairs(W.fires) do
          if x.key == w[4] then
            got = got + 1
            local tid = nil
            pcall(function() tid = tostring(x.target:unique_ui_id()) end)
            if w[6] ~= nil and tid == tostring(b + w[6]) then on_t = on_t + 1 end
          end
        end
        for _, x in ipairs(W.ground_fires or {}) do if x.key == w[4] then got = got + 1 end end
        local a, txt
        if RED177 then
          local rule = RED2 and w[8] or w[7]
          if rule == "none" then a = (got == 0)
          elseif rule == "one" then a = (got == 1)
          elseif rule == "nottarget" then a = (on_t == 0)
          elseif rule == "any" then a = true
          else a = (got == w[5] and (w[6] == nil or on_t == w[5])) end
          txt = "-RED" .. (RED2 and "2" or "") .. "a: rule " .. rule .. ", got " .. got .. ", " .. on_t .. " on the new target"
        else
          a = (got == w[5]) and (w[5] == 0 or w[6] == nil or on_t == w[5])
          txt = "a: " .. w[5] .. " cast(s) expected, got " .. got .. ", on target " .. on_t
        end
        check(TAG .. w[1]:sub(1, 3) .. txt, a)
        done(a)
        if i == 1 then
          local by = {}
          for _, e in ipairs(W.cap or {}) do by[e.marker] = e.card end
          local c_ok = by.glory_seeker == "Fires at a charging enemy, else at one in melee; Lords and Heroes only"
            and by.net_of_amyntok == "Fires on a fast enemy closing on allies"
            and by.prey_of_anath_raema == "Fires at a charging enemy, else at one we shoot, else at one in melee"
            and by.spell_heavens_chain_lightning_bound ~= nil
            and raw_find(by.spell_heavens_chain_lightning_bound, "on the enemy unit with the most soldiers, 16 at least", 1, true) ~= nil
            and by.eye_of_khorne == "Fires on the most valuable enemy below 20% health, not Lords or Heroes"
          check(TAG .. "CA6: the cards of the 3 new families, the roots and Eye of Khorne (" .. tostring(by.spell_heavens_chain_lightning_bound) .. ")",
            (RED177 and not c_ok) or (not RED177 and c_ok))
          done((RED177 and not c_ok) or (not RED177 and c_ok))
        end
        tally(W)
      end
    end
  end
  if RED177 then
    check("RED CONTROL (harness 177" .. (RED2 and ", first pass" or "") .. "): the old build keeps the old triggers - "
      .. n_ok .. "/" .. n_all, n_all == 36 and n_ok == 36)
  else
    check("HARNESS 177: every check behaved - " .. n_ok .. "/" .. n_all, n_all == 36 and n_ok == 36)
  end
  print("== HARNESS 177 done: " .. (checks - pre177) .. " checks in this section ==")
end
