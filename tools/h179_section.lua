-- ============================================================================
-- HARNESS 179 (round 180): THE SCORE-3 REVIEW, ROWS 87-114 AND 128 (user, 2026-11-18), built from the CURRENT text of
--   each row on disk.
--   0zz28 the 4 new families wired, the moves (Land Mine NOT moved: row 98 waits), 3 closed (Heaven's Gate, Snowflake Pendant, Stave of Avelorn: marker,
--         badge, key gone), the roots' real 100 m range, the 80% WW buffers, the lizard / tiger sets, the Z / T codes.
--   RT1 Entangle: a fast enemy closing 25 m away -> ONE ground cast under it (RED: none).
--   RT2 Entangle: only an enemy in melee 5 m away -> no cast (no melee arm; RED: one).
--   RT3 Get 'Em!: a fast enemy 50 m away (beyond the old 24 m bound) -> ONE ground cast (RED: none).
--   ST1 Shield of Thorns: the caster idle, an ally in melee 30 m away -> ONE cast at it (RED: none).
--   BC1 Blood Chalice: a hurt Swordsmen (40%) 15 m and a hurt Captain (60%) 20 m -> ONE cast at the Captain (RED: none).
--   BD1 Breath of Darkness: a hurt Swordsmen (40%) and hurt Skeleton Horsemen (50%) -> ONE cast at the skeletons.
--   MI1 Mantra of Invigoration: a hurt Swordsmen (40%) and hurt Tiger Warriors (50%) -> ONE cast at the Tiger Warriors.
--   BG1 Bugman's XXXXXX: at 60% with an enemy 20 m away -> no cast (RED: one).  BG2: the enemy 60 m away -> ONE cast.
--   PC1 Potion of Charoi: at 60%, idle -> no cast (RED: one).  PC2: at 60% in melee -> ONE cast.
--   SK1 Skar's Kraken-Killer: at 60% under missile fire -> ONE cast.
--   FS1 Foe-Seeker: charging -> ONE cast (RED: none, it waited for tired).
--   RB1 Rock Bottom: out of ammunition at 40% -> no cast (RED: one).  RB2: out of ammunition at 90% -> ONE cast.
--   ED1 Eat da Runts!: the caster at 60%; Skavenslaves (expendable) 30 m and Swordsmen 20 m, both healthy -> ONE cast
--       at the Skavenslaves (RED: not them, the self arm).  ED2: only a hurt ally -> no cast (RED: one).
--   ED3 Eat da Runts!: the caster at 60%, a healthy ally 75 m away (beyond 70 m) -> no cast (RED: one).
--   CB1 Cold-Blooded: a wavering Swordsmen ally -> no cast (Lizardmen only; RED: one).  CB2: wavering Saurus -> ONE cast.
--   CA8 the cards of the 4 new families and the 2 re-ruled ones.
--   RED control: H179_LIVE / H179_ANN on docs/backups/round180/pre180_*.lua.
-- ============================================================================
function run_h179()
  local L179 = os.getenv("H179_LIVE") or LIVE
  local A179 = os.getenv("H179_ANN") or ANN
  local RED179 = (os.getenv("H179_LIVE") ~= nil) or (os.getenv("H179_ANN") ~= nil)
  local K = {
    EN = "wh2_dlc10_character_abilities_entangle", GE = "wh3_dlc25_character_abilities_get_em",
    LM = "wh3_dlc25_unit_abilities_marienburg_land_mines", ST = "wh2_dlc17_spell_bound_shield_of_thorns",
    BC = "wh_pro02_item_abilities_blood_chalice_of_bathori", BD = "wh3_dlc29_spell_bound_undeath_morkharn_breath_of_darkness",
    MI = "wh3_cp1_character_abilities_protection_prayer", BG = "wh3_dlc26_item_abilities_bugmans_xxxxxx",
    PC = "wh2_main_lord_abilities_potion_of_charoi", SK = "wh3_main_weapon_abilities_skars_kraken_killer",
    FS = "wh_main_character_abilities_foe_seeker", RB = "wh2_dlc15_unit_abilities_rock_bottom",
    ED = "wh3_dlc26_unit_abilities_eat_da_runts", CB = "wh2_main_character_abilities_cold_blooded",
  }
  local CASTER = "wh2_dlc13_emp_cha_huntsmen_general_0"
  local SW = "wh_main_emp_inf_swordsmen"
  local CAP = "wh_main_emp_cha_captain_0"
  local SKEL = "wh2_dlc09_tmb_cav_skeleton_horsemen_0"
  local TIGER = "wh3_cp1_cth_inf_tiger_warriors_dual_axe"
  local SAURUS = "wh2_main_lzd_inf_saurus_warriors_0"
  local SLAVES = "wh2_main_skv_inf_skavenslaves_0"
  local pre179 = checks
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1; at = i + #tok
    end
  end
  print("== HARNESS 179 - section 0zz28: the round-180 tokens ==")
  if not RED179 then
    for _, f in ipairs({ { name = "live", path = L179 }, { name = "ann", path = A179 } }) do
      local s = read_file(f.path)
      local wired = 0
      for _, fam in ipairs({ "health_aura_ally_rule", "self_heal_clear", "self_hurt_attacked", "charge_or_tired" }) do
        if cp(s, fam .. " = FOURTH.evaluate_" .. fam .. ",") == 1 and cp(s, 'trigger = "' .. fam .. '"') >= 1 then
          wired = wired + 1
        end
      end
      check("0zz28 " .. f.name .. ": 4 families wired (" .. wired .. "), 13 moved, Land Mine kept, 3 closed, the roots at 100 m, the 80% "
        .. "buffers, the lizard / tiger sets, the Z / T codes",
        wired == 4 and cp(s, "-- ROUND 180 (score-3 review): ") == 13 and cp(s, "melee_clear_block") == 0 and cp(s, "\t{ marker = ") == 935
        and cp(s, "heavens_gate") == 0 and cp(s, "snowflake_pendant") == 0 and cp(s, "stave_of_avelorn") == 0
        and cp(s, 'trigger = "enemy_ground_area"') == 2
        and cp(s, "wh2_dlc09_lord_abilities_sand_storm=2,12,56,0,41,1,0;") == 1
        and cp(s, "wh3_dlc25_spell_bound_fire_the_burning_head=1,7,180,24,78,1,0;") == 1
        and cp(s, "wh2_dlc10_item_bound_arnizipals_black_horror=1,10,140,24,44,1,0;") == 1
        and cp(s, "FOURTH.load_rule_sets()\n") == 1
        and cp(s, "wh2_main_character_abilities_cold_blooded=Z;") == 1
        and cp(s, "wh3_cp1_character_abilities_protection_prayer=T;") == 1
        and cp(s, 'if a.Z and not FOURTH.class_member(unit, "lizard") then return false end') == 1
        and cp(s, "\nFOURTH.BUGMAN_CLEAR_M = 38") == 1 and cp(s, "\nFOURTH.ROCK_BOTTOM_PCT = 50") == 1)
    end
  end
  local FILES = { { path = A179, tag = "[annotated] " }, { path = L179, tag = "[live] " } }
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
    local c = { name = CASTER, uid = b, owns = { key }, melee = false, dist = 30, health_percent = 100, pos = { 0, 0, 0 },
                width = 2, unit_class = "com" }
    for k, v in pairs(o or {}) do c[k] = v end
    return c
  end
  local function ally(uid, name, o)
    local a = { name = name, uid = uid, owns = {}, melee = false, dist = 30, health_percent = 100, in_range = true }
    for k, v in pairs(o or {}) do a[k] = v end
    return a
  end
  local function enemy(uid, name, o)
    local e = { uid = uid, name = name, melee = false, pos = { 0, 0, 60 }, width = 29.4, men_alive = 120,
                initial_men = 120, unit_class = "inf_mel", dist = 30 }
    for k, v in pairs(o or {}) do e[k] = v end
    return e
  end
  -- name; builder(b) -> units, enemies, opts; marker; key; GREEN casts; GREEN target ("uN" unit form / "gN" ground form
  -- under unit b+N / nil); RED rule ("none", "one", "nottarget", "same")
  local WORLDS = {
    { "RT1. Entangle: a fast enemy closing 25 m away -> ONE ground cast under it",
      function(b) return { caster(b, K.EN, { dist_by_target = { [b + 5] = 25 } }) },
        { enemy(b + 5, SW, { moving = true, fast_speed = 8 }) } end, "entangle", K.EN, 1, "g5", "none" },
    { "RT2. Entangle: only an enemy in melee 5 m away -> no cast",
      function(b) return { caster(b, K.EN, { dist = 5 }) }, { enemy(b + 5, SW, { melee = true, dist = 5 }) } end,
      "entangle", K.EN, 0, nil, "one" },
    { "RT3. Get 'Em!: a fast enemy 50 m away -> ONE ground cast under it",
      function(b) return { caster(b, K.GE, { dist_by_target = { [b + 5] = 50 } }), ally(b + 1, SW, { dist = 20 }) },
        { enemy(b + 5, SW, { moving = true, fast_speed = 8, dist = 30 }) } end, "get_em", K.GE, 1, "g5", "none" },
    { "ST1. Shield of Thorns: the caster idle, an ally in melee 30 m away -> ONE cast at it",
      function(b) return { caster(b, K.ST), ally(b + 5, SW, { melee = true, dist = 30 }) } end,
      "shield_of_thorns", K.ST, 1, "u5", "none" },
    { "BC1. Blood Chalice of Bathori: a hurt Swordsmen (40%) 15 m, a hurt Captain (60%) 20 m -> ONE cast at the Captain",
      function(b) return { caster(b, K.BC), ally(b + 5, SW, { health_percent = 40, dist = 15 }),
        ally(b + 6, CAP, { health_percent = 60, dist = 20, unit_class = "com", men_alive = 1 }) } end,
      "blood_chalice_of_bathori", K.BC, 1, "u6", "none" },
    { "BD1. Breath of Darkness: a hurt Swordsmen (40%), hurt Skeleton Horsemen (50%) -> ONE cast at the skeletons",
      function(b) return { caster(b, K.BD), ally(b + 5, SW, { health_percent = 40, dist = 20 }),
        ally(b + 6, SKEL, { health_percent = 50, dist = 30 }) } end,
      "undeath_morkharn_breath_of_darkness", K.BD, 1, "u6", "none" },
    { "MI1. Mantra of Invigoration: a hurt Swordsmen (40%), hurt Tiger Warriors (50%) -> ONE cast at the Tiger Warriors",
      function(b) return { caster(b, K.MI), ally(b + 5, SW, { health_percent = 40, dist = 20 }),
        ally(b + 6, TIGER, { health_percent = 50, dist = 30 }) } end,
      "protection_prayer", K.MI, 1, "u6", "none" },
    { "BG1. Bugman's XXXXXX: at 60% with an enemy 20 m away -> no cast",
      function(b) return { caster(b, K.BG, { health_percent = 60, dist_by_target = { [b + 5] = 20 } }) },
        { enemy(b + 5, SW) } end, "bugmans_xxxxxx", K.BG, 0, nil, "one" },
    { "BG2. Bugman's XXXXXX: at 60% with the enemy 60 m away -> ONE cast",
      function(b) return { caster(b, K.BG, { health_percent = 60, dist_by_target = { [b + 5] = 60 } }) },
        { enemy(b + 5, SW) } end, "bugmans_xxxxxx", K.BG, 1, nil, "same" },
    { "PC1. Potion of Charoi: at 60%, idle -> no cast",
      function(b) return { caster(b, K.PC, { health_percent = 60 }) } end, "potion_of_charoi", K.PC, 0, nil, "one" },
    { "PC2. Potion of Charoi: at 60% in melee -> ONE cast",
      function(b) return { caster(b, K.PC, { health_percent = 60, melee = true }) } end, "potion_of_charoi", K.PC, 1, nil, "same" },
    { "SK1. Skar's Kraken-Killer: at 60% under missile fire -> ONE cast",
      function(b) return { caster(b, K.SK, { health_percent = 60, missile = true }) } end, "skars_kraken_killer", K.SK, 1, nil, "same" },
    { "FS1. Foe-Seeker: charging -> ONE cast",
      function(b) return { caster(b, K.FS, { fast = true, target = "enemy", dist = 20 }) } end, "fs", K.FS, 1, nil, "none" },   -- the legacy badge zz_auto_badge_fs
    { "RB1. Rock Bottom: out of ammunition at 40% -> no cast",
      function(b) return { caster(b, K.RB, { health_percent = 40, ammo_start = 10, ammo_seq = { 0 } }) } end, "rock_bottom", K.RB, 0, nil, "one" },
    { "RB2. Rock Bottom: out of ammunition at 90% -> ONE cast",
      function(b) return { caster(b, K.RB, { health_percent = 90, ammo_start = 10, ammo_seq = { 0 } }) } end, "rock_bottom", K.RB, 1, nil, "same" },
    { "ED1. Eat da Runts!: the caster at 60%; healthy Skavenslaves 30 m and Swordsmen 20 m -> ONE cast at the Skavenslaves",
      function(b) return { caster(b, K.ED, { health_percent = 60 }), ally(b + 5, SLAVES, { dist = 30 }),
        ally(b + 6, SW, { dist = 20 }) } end, "eat_da_runts", K.ED, 1, "u5", "nottarget" },
    { "ED2. Eat da Runts!: the caster at 60%, only a hurt ally -> no cast",
      function(b) return { caster(b, K.ED, { health_percent = 60 }), ally(b + 5, SW, { dist = 20, health_percent = 50 }) } end,
      "eat_da_runts", K.ED, 0, nil, "one" },
    { "ED3. Eat da Runts!: the caster at 60%, a healthy ally 75 m away -> no cast",
      function(b) return { caster(b, K.ED, { health_percent = 60 }), ally(b + 5, SW, { dist = 75 }) } end,
      "eat_da_runts", K.ED, 0, nil, "one" },
    { "CB1. Cold-Blooded: a wavering Swordsmen ally -> no cast",
      function(b) return { caster(b, K.CB), ally(b + 5, SW, { wavering = true, dist = 30 }) } end,
      "cold_blooded", K.CB, 0, nil, "one" },
    { "CB2. Cold-Blooded: a wavering Saurus Warriors ally -> ONE cast at it",
      function(b) return { caster(b, K.CB), ally(b + 5, SAURUS, { wavering = true, dist = 30 }) } end,
      "cold_blooded", K.CB, 1, "u5", "same" },
  }
  for _, f in ipairs(FILES) do
    local TAG = f.tag
    for i, w in ipairs(WORLDS) do
      local b = 45000 + i * 20
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
        if RED179 then
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
          local c_ok = by.land_mine == "Fires in melee unless wavering, clear of allies"
            and by.blood_chalice_of_bathori == "Fires on the most hurt unit nearby it may target, below 75% health; Lord or Hero allies only"
            and by.protection_prayer == "Fires on the most hurt unit nearby it may target, below 75% health; Tiger Warrior allies only"
            and by.bugmans_xxxxxx == "Fires below 75% health with no enemy near"
            and by.potion_of_charoi == "Fires below 75% health while fighting or shot at"
            and by.foe_seeker == "Fires when charging or tired"
            and by.rock_bottom == "Fires when out of ammo, above 50% health"
            and by.eat_da_runts == "Fires below 75% health, on the cheapest healthy ally"
            and by.heavens_gate == nil
          check(TAG .. "CA8: the cards of the 4 new families and the re-ruled ones (" .. tostring(by.blood_chalice_of_bathori) .. ")",
            (RED179 and not c_ok) or (not RED179 and c_ok))
          done((RED179 and not c_ok) or (not RED179 and c_ok))
        end
        tally(W)
      end
    end
  end
  if RED179 then
    check("RED CONTROL (harness 179): the pre-180 build keeps the old triggers - " .. n_ok .. "/" .. n_all,
      n_all == 42 and n_ok == 42)
  else
    check("HARNESS 179: every check behaved - " .. n_ok .. "/" .. n_all, n_all == 42 and n_ok == 42)
  end
  print("== HARNESS 179 done: " .. (checks - pre179) .. " checks in this section ==")
end
