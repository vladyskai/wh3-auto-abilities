-- ============================================================================
-- HARNESS 208 (round 210, the user's second replies to the afternoon code review).
--   0zz56 the round-210 tokens in both files.
--   THE LOONS (the Night Goblins at 0,0, enemy Swordsmen walking in along +z, 1 m per poll):
--   LO1 the caster stands, nobody else of ours -> an aimed ground order while the enemy is 15 to 25 m away (a point
--       at most 20 m from the caster, bearing 0), none before 25 m. RED (round 209: an enemy in melee and a clear
--       ring): no order.
--   LO2 one of our 120-man units stands in the path, 50 m ahead -> no order (GREEN and RED).
--   LO3 one of our Heroes (a single entity) stands in the path -> an order. RED: none.
--   LO4 the enemy stands still 20 m away -> no order (GREEN and RED).
--   LO5 the caster is moving -> no order (GREEN and RED).
--   LO6 one of our 120-man units stands beside the caster (35 m to the side, a line neighbour) -> an order. RED: none.
--   LO7 the approaching enemy is a single entity -> no order (GREEN and RED).
--   LO8 The Loons of Eight Peaks, as LO1 -> an order. RED: none.
--   THE CASTER-FRONT BREATHS (a hero with Skabscrath at 0,0, 160 Zombies standing 30 m ahead):
--   CN1 nobody else -> ONE unit-form order (GREEN and RED).
--   CN2 one of our 120-man units 12 m beside the line at the enemy's depth -> ONE order (the cone is 2.6 m wide
--       there). RED: none (the old 6 m band + 10 m).
--   CN3 one of our 120-man units ON the line 55 m ahead -> no order (GREEN and RED).
--   CN4 one of our 120-man units on the line 90 m ahead (beyond the 72 m path) -> ONE order. RED: none (the old
--       zone was 108 m long).
--   THE CHARGE RUN-UP (a hero with Deadly Onslaught, running at its target, not in melee):
--   CH1 run speed 2.8 m/s, 8 m to go -> ONE cast (run-up 5.6 m). RED: none (12 m).
--   CH2 run speed 2.8 m/s, 4 m to go -> no cast (GREEN and RED).
--   CH3 run speed 9 m/s, 8 m to go -> no cast (GREEN and RED: a fast unit keeps the 12 m).
--   THE TRANSFORMATION:
--   TR1 a hero in melee owns the Whirlwind and casts it. Its owned list then changes to Eruption (the same unit id and
--       type) -> Eruption is cast within 24 polls. RED: never.
--   RED control: H208_LIVE / H208_ANN on docs/backups/round210/pre210_*.lua.
-- ============================================================================
function run_h208()
  local L208 = os.getenv("H208_LIVE") or LIVE
  local A208 = os.getenv("H208_ANN") or ANN
  local RED208 = (os.getenv("H208_LIVE") ~= nil) or (os.getenv("H208_ANN") ~= nil)
  local LO = "wh_main_unit_abilities_spinning_loons"
  local LE = "wh_dlc06_unit_abilities_the_loons_of_eight_peaks"
  local SK = "wh_main_weapon_abilities_skabscrath"
  local EW = "wh3_dlc25_unit_abilities_whirlwind_of_death_ror"
  local ERU = "wh3_main_character_abilities_eruption"
  local DO = "wh_main_character_abilities_deadly_onslaught"
  local CASTER = "wh2_dlc13_emp_cha_huntsmen_general_0"
  local GOBS = "wh_main_grn_inf_night_goblins"
  local LIVING = "wh_main_emp_inf_swordsmen"
  local ZOM = "wh_main_vmp_inf_zombie"
  local pre208 = checks
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1; at = i + #tok
    end
  end
  print("== HARNESS 208 - section 0zz56: the round-210 tokens ==")
  for _, f in ipairs({ { name = "live", path = L208 }, { name = "ann", path = A208 } }) do
    local s = read_file(f.path)
    local loons = cp(s, '\t{ marker = "spinning_loons", name = "Spinning Loons", trigger = "enemy_wave_charge",\n')
      + cp(s, '\t{ marker = "loons_of_eight_peaks", name = "The Loons of Eight Peaks", trigger = "enemy_wave_charge",\n')
    local rows = cp(s, "wh_main_unit_abilities_spinning_loons=8,4,84,0,56,1,0")
      + cp(s, "wh_dlc06_unit_abilities_the_loons_of_eight_peaks=8,4,84,0,56,1,0")
    local ring = cp(s, "\t\tring_clear = true,")
    local fns = cp(s, "\nfunction FOURTH.evaluate_loons(unit, routing, row)\n") + cp(s, "\nfunction FOURTH.ww_loons_ok(unit, e, m, row, closing)\n")
      + cp(s, "\nfunction FOURTH.loons_closing(unit, enemy, gap)\n") + cp(s, "\nfunction FOURTH.keys_changed(old, new)\n")
    local band = cp(s, "\nFOURTH.LOONS_MIN_M = 15 ") + cp(s, "\nFOURTH.LOONS_MAX_M = 25 ")
    local cone = cp(s, "wh_main_weapon_abilities_skabscrath=0.1,0.0833") + cp(s, "\tif FOURTH.ww_exact(row) and row.r0 ~= nil then\n")
    local run = cp(s, "\t\t\tif m.speed ~= nil and m.speed * 2 < run_up then run_up = m.speed * 2 end\n")
    local scan = cp(s, "\t\t\t\tlocal changed210, found210 = FOURTH.reread_unit(unit, ui_id, do_redetect)\n")
    if RED208 then
      check("0zz56 " .. f.name .. " (RED): the pre-210 file has none of it and the ring on both Loons",
        loons == 0 and rows == 0 and ring == 2 and fns == 0 and band == 0 and cone == 0 and run == 0 and scan == 0)
    else
      check("0zz56 " .. f.name .. ": the Loons on enemy_wave_charge (" .. loons .. "), their kind-8 rows (" .. rows
        .. "), no ring (" .. ring .. "), the four functions (" .. fns .. "), the user's band (" .. band
        .. "), the breath cone (" .. cone .. "), the run-up (" .. run .. "), the re-read (" .. scan .. ")",
        loons == 2 and rows == 2 and ring == 0 and fns == 4 and band == 2 and cone == 2 and run == 1 and scan == 1)
    end
  end
  local FILES = { { path = A208, tag = "[annotated] " }, { path = L208, tag = "[live] " } }
  local n_ok, n_all = 0, 0
  local function done(ok) n_all = n_all + 1; if ok then n_ok = n_ok + 1 end end
  local function casts(W, key)
    local u, g = 0, 0
    for _, x in ipairs(W.fires) do if x.key == key then u = u + 1 end end
    for _, x in ipairs(W.ground_fires or {}) do if x.key == key then g = g + 1 end end
    return u, g
  end
  local function verdict(TAG, id, text, ok)
    check(TAG .. id .. (RED208 and "-RED" or "") .. ": " .. text, ok)
    done(ok)
  end
  -- a world armed by a click on the first unit, free aim on (the vector constructor and the terrain read exist)
  local function clicked(wname, key, marker, units, enemies, PATH, TAG)
    local cards = {}
    for _, d in ipairs(units) do cards[#cards + 1] = { id = tostring(d.uid), state = "active", vis = true } end
    local W = make_world({ can_perform = true, units = units, enemies = enemies, cards = cards,
      bar = { { id = "b1", key = key } } })
    W.defaults_on = false
    W.free_aim_on = true
    print("== " .. TAG .. wname .. " ==")
    W.bm.get_player_alliance = function() return "OUR_ALLIANCE" end
    W.bm.get_terrain_height = function(self, x, z) return 0 end
    v = function(x, y, z) return { vx = x, vy = y, vz = z } end
    local ok = pcall(load_world, W, PATH)
    check(TAG .. wname .. ": the file loads", ok)
    if not ok then v = nil; tally(W); return nil end
    deploy_phases(W); ui(W)
    for i = 1, #(W.enemy_entries or {}) do
      local pr = W.enemy_entries[i]
      if pr ~= nil and pr.unit ~= nil then
        pr.unit.is_visible_to_alliance = function(self, a) return true end
        pr.unit.is_currently_flying = function(self) return false end
        pr.unit.strategic_value = function(self) return 100 end
      end
    end
    sel_event(W, units[1].uid, true); ui(W); ui(W)
    pcall(click, W, "zz_auto_badge_" .. marker); ui(W)
    sel_event(W, units[1].uid, false); ui(W)
    W.conflict = true
    return W
  end
  local function block(uid, name, x, z, men, width, extra)
    local d = { name = name, uid = uid, owns = {}, melee = false, dist = 60, pos = { x, 0, z }, width = width or 30,
                men_alive = men, initial_men = men, unit_class = (men > 1) and "inf_mel" or "com" }
    for k, val in pairs(extra or {}) do d[k] = val end
    return d
  end
  -- the Loons: the enemy walks in from 40 m to 14 m, one metre per poll. o: friend (a def), enemy (overrides),
  -- caster (overrides), still (the enemy does not move)
  local function loons(TAG, P, id, wname, base, key, marker, o, want, want_red)
    o = o or {}
    local c = block(base, GOBS, 0, 0, 120, 30, { owns = { key }, dist = 40 })
    for k, val in pairs(o.caster or {}) do c[k] = val end
    local units = { c }
    if o.friend ~= nil then units[2] = o.friend(base + 1) end
    local e = block(base + 5, LIVING, 0, 48, 120, 30, { moving = true, dist = 40 })
    e.owns = nil
    for k, val in pairs(o.enemy or {}) do e[k] = val end
    local W = clicked(id .. ". " .. wname, key, marker, units, { e }, P, TAG)
    if W == nil then done(false); return end
    local early = 0
    if o.still then
      W.unit_defs[1].dist = 20
      W.enemy_defs[1].pos = { 0, 0, 28 }
      polln(W, 12)
    else
      for gap = 40, 14, -1 do
        W.unit_defs[1].dist = gap
        W.enemy_defs[1].pos = { 0, 0, gap + 8 }
        polln(W, 1)
        if gap > 25 then
          local u0, g0 = casts(W, key)
          early = u0 + g0
        end
      end
    end
    v = nil
    local u, g = casts(W, key)
    local first = nil
    for _, x in ipairs(W.ground_fires or {}) do if x.key == key and first == nil then first = x end end
    local w = want
    if RED208 then w = want_red end
    local good
    if w == 0 then
      good = (u + g == 0)
    else
      good = (u == 0 and g >= 1 and early == 0 and first ~= nil and type(first.pos) == "table" and first.pos.vx ~= nil
        and math.abs(first.pos.vx) < 0.01 and first.pos.vz > 0 and first.pos.vz <= 20.01
        and type(first.orient) == "number" and (first.orient < 0.5 or first.orient > 359.5))
    end
    verdict(TAG, id .. "a", ((w == 0) and "no order expected" or "an aimed ground order expected") .. ", got " .. g
      .. " ground and " .. u .. " unit-form (" .. early .. " before 25 m)"
      .. ((first ~= nil) and (", the first at z " .. tostring(first.pos.vz) .. " bearing " .. tostring(first.orient)) or ""), good)
    tally(W)
  end
  -- the breath: a hero with Skabscrath at 0,0, Zombies standing 30 m ahead (edge 17 m), an optional friend
  local function breath(TAG, P, id, wname, base, friend, want, want_red)
    local units = { { name = CASTER, uid = base, owns = { SK }, melee = false, dist = 17, pos = { 0, 0, 0 }, width = 2,
                      men_alive = 1, unit_class = "com", hp_frac = 1.0 } }
    if friend ~= nil then units[2] = friend(base + 1) end
    local enemies = { block(base + 5, ZOM, 0, 30, 160, 30, { dist = 17 }) }
    enemies[1].owns = nil
    local W = clicked(id .. ". " .. wname, SK, "skabscrath", units, enemies, P, TAG)
    if W == nil then done(false); return end
    polln(W, 4)
    v = nil
    local u, g = casts(W, SK)
    local w = want
    if RED208 then w = want_red end
    verdict(TAG, id .. "a", w .. " unit-form order(s) expected, got " .. u .. " (and " .. g .. " ground)", u == w and g == 0)
    tally(W)
  end
  -- a world on the default M/A states
  local function defaults(wname, key, units, PATH, TAG)
    local cards = {}
    for _, d in ipairs(units) do cards[#cards + 1] = { id = tostring(d.uid), state = "active", vis = true } end
    local W = make_world({ can_perform = true, units = units, enemies = {}, cards = cards, bar = { { id = "b1", key = key } } })
    W.defaults_on = true
    print("== " .. TAG .. wname .. " ==")
    W.bm.get_player_alliance = function() return "OUR_ALLIANCE" end
    local ok = pcall(load_world, W, PATH)
    check(TAG .. wname .. ": the file loads", ok)
    if not ok then tally(W); return nil end
    deploy_phases(W); ui(W)
    W.conflict = true
    return W
  end
  local function charge(TAG, P, id, wname, uid, speed, dist, want, want_red)
    local W = defaults(id .. ". " .. wname, DO,
      { { name = CASTER, uid = uid, owns = { DO }, melee = false, fast = true, target = "enemy", dist = dist,
          fast_speed = speed, width = 2, men_alive = 1, unit_class = "com", hp_frac = 1.0 } }, P, TAG)
    if W == nil then done(false); return end
    polln(W, 4)
    local u = casts(W, DO)
    local w = want
    if RED208 then w = want_red end
    verdict(TAG, id .. "a", ((w == 0) and "no cast" or "at least one cast") .. " expected, got " .. u,
      (w == 0 and u == 0) or (w > 0 and u >= 1))
    tally(W)
  end
  for _, f in ipairs(FILES) do
    local TAG, P = f.tag, f.path
    loons(TAG, P, "LO1", "Spinning Loons: enemy infantry walks in, the caster stands, nobody else -> an aimed order in the band",
      20900, LO, "spinning_loons", nil, 1, 0)
    loons(TAG, P, "LO2", "Spinning Loons: one of our 120-man units stands in the path 50 m ahead -> no order",
      20910, LO, "spinning_loons", { friend = function(uid) return block(uid, LIVING, 0, 50, 120, 30) end }, 0, 0)
    loons(TAG, P, "LO3", "Spinning Loons: one of our Heroes stands in the path -> an order",
      20920, LO, "spinning_loons", { friend = function(uid) return block(uid, CASTER, 0, 50, 1, 2) end }, 1, 0)
    loons(TAG, P, "LO4", "Spinning Loons: the enemy stands still 20 m away -> no order",
      20930, LO, "spinning_loons", { still = true, enemy = { moving = false } }, 0, 0)
    loons(TAG, P, "LO5", "Spinning Loons: the caster is moving -> no order",
      20940, LO, "spinning_loons", { caster = { moving = true } }, 0, 0)
    loons(TAG, P, "LO6", "Spinning Loons: one of our 120-man units stands beside the caster -> an order",
      20950, LO, "spinning_loons", { friend = function(uid) return block(uid, LIVING, 35, 0, 120, 30) end }, 1, 0)
    loons(TAG, P, "LO7", "Spinning Loons: the approaching enemy is a single entity -> no order",
      20960, LO, "spinning_loons", { enemy = { name = CASTER, men_alive = 1, initial_men = 1, width = 2, unit_class = "com" } }, 0, 0)
    loons(TAG, P, "LO8", "The Loons of Eight Peaks: enemy infantry walks in -> an aimed order in the band",
      20970, LE, "loons_of_eight_peaks", nil, 1, 0)
    breath(TAG, P, "CN1", "Skabscrath: Zombies standing 30 m ahead, nobody else -> ONE order", 21000, nil, 1, 1)
    breath(TAG, P, "CN2", "Skabscrath: one of our units 12 m beside the line at the enemy's depth -> ONE order",
      21010, function(uid) return block(uid, LIVING, 12, 30, 120, 10) end, 1, 0)
    breath(TAG, P, "CN3", "Skabscrath: one of our units ON the line 55 m ahead -> no order",
      21020, function(uid) return block(uid, LIVING, 0, 55, 120, 30) end, 0, 0)
    breath(TAG, P, "CN4", "Skabscrath: one of our units on the line 90 m ahead, beyond the 72 m path -> ONE order",
      21030, function(uid) return block(uid, LIVING, 0, 90, 120, 30) end, 1, 0)
    charge(TAG, P, "CH1", "Deadly Onslaught: run speed 2.8 m/s, 8 m to go -> a cast (the run-up is 5.6 m)", 21040, 2.8, 8, 1, 0)
    charge(TAG, P, "CH2", "Deadly Onslaught: run speed 2.8 m/s, 4 m to go -> no cast", 21041, 2.8, 4, 0, 0)
    charge(TAG, P, "CH3", "Deadly Onslaught: run speed 9 m/s, 8 m to go -> no cast (12 m for a fast unit)", 21042, 9, 8, 0, 0)
    do
      local W = defaults("TR1. a transformation: the owned list changes, the unit id and type stay", EW,
        { { name = CASTER, uid = 21050, owns = { EW }, melee = true, dist = 5, width = 2, men_alive = 1, unit_class = "com",
            hp_frac = 1.0 } }, P, TAG)
      if W ~= nil then
        polln(W, 4)
        local before = casts(W, EW)
        set_state(W, 1, { owns = { ERU } })
        polln(W, 24)
        local after = casts(W, ERU)
        local good = (before >= 1 and after >= 1)
        if RED208 then good = (before >= 1 and after == 0) end
        verdict(TAG, "TR1a", "the Whirlwind was cast " .. before .. " time(s), then Eruption " .. after .. " time(s) within 24 polls ("
          .. (RED208 and "RED: never" or "need at least 1") .. ")", good)
        tally(W)
      else
        done(false)
      end
    end
  end
  check("HARNESS 208: every world behaved - " .. n_ok .. "/" .. n_all, n_ok == n_all)
  print("== HARNESS 208 done: " .. (checks - pre208) .. " checks in this section ==")
end
