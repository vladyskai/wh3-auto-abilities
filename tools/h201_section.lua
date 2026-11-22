-- ============================================================================
-- HARNESS 201 (round 203, user 2026-11-22: "A: but be careful ..." and "All 30 placed"). FREE AIM for the straight waves.
--   0zz49 the round-203 tokens in both files.
--   A Master Engineer at (0,0) owns the Fiery Ring of Thori (radius 6, path 72, start 36 m + the half extent before the
--   target, none of ours within 16 m of the path, cast bound 80 m).
--   FA1 the user's battle: Zombies stand at (0,60), our Miners at (0,30) on the caster's line -> ONE GROUND order whose
--       path starts within 80 m of the caster, crosses the Zombies and stays more than 16 m from the Miners' centre.
--       No unit-form order. RED: no order at all (the caster's line is blocked and nothing else is tested).
--   FA2 no friend in the way -> ONE unit-form order, no ground order (the caster's line keeps a tie). GREEN and RED.
--   FA3 two Zombie units side by side at (-20,60) and (20,60) -> ONE GROUND order (a path across both is worth more
--       than the caster's line through one). RED: ONE unit-form order.
--   FA4 FA1 without the game's vector constructor -> no order (fail closed). GREEN and RED.
--   FA5 Blue Fire of Chaos (a ground-only wave), an enemy at (30,40), the line clear -> ONE GROUND order at the path's
--       start with orientation 37 (the bearing). RED: the old order, on the enemy's centre with orientation 0.
--   FA6 FA1 with the enemy WALKING -> no order (option A: standing targets only). GREEN and RED.
--   RED control: H201_LIVE / H201_ANN on docs/backups/round203/pre203_*.lua.
-- ============================================================================
function run_h201()
  local L201 = os.getenv("H201_LIVE") or LIVE
  local A201 = os.getenv("H201_ANN") or ANN
  local RED201 = (os.getenv("H201_LIVE") ~= nil) or (os.getenv("H201_ANN") ~= nil)
  local RING = "wh_main_item_abilities_fiery_ring_of_thori"
  local BLUE = "wh3_main_daemon_arms_abilities_blue_fire"
  local ENG = "wh_main_dwf_cha_master_engineer_0"
  local ZOM = "wh_main_vmp_inf_zombie"
  local MIN = "wh_main_dwf_inf_miners_0"
  local pre201 = checks
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1; at = i + #tok
    end
  end
  print("== HARNESS 201 - section 0zz49: the round-203 tokens ==")
  for _, f in ipairs({ { name = "live", path = L201 }, { name = "ann", path = A201 } }) do
    local s = read_file(f.path)
    local steps = cp(s, "\nFOURTH.FREE_AIM_STEPS = 24 ")
    local fns = cp(s, "\nfunction FOURTH.ww_aim_value(unit, e, m, row, hx, hz)\n") + cp(s, "\nfunction FOURTH.aim_cast(uc, ability_key, aim)\n")
      + cp(s, "\nfunction FOURTH.ww_line_value(unit, m, row, sx, sz, ex, ez)\n")
    local cast = cp(s, '\telseif FOURTH.eg_arm == "ww" and FOURTH.ww_aim ~= nil then\n')
    local order = cp(s, "uc:perform_special_ability_ground(ability_key, pos, aim.deg, 0)")
    local reset = cp(s, "\tFOURTH.ww_aim = nil   -- ROUND 203: the free aim of a wave\n")
    local sw = cp(s, "local free = (ZZ_AUTO_TEST_NO_FREE_AIM ~= true)")
    if RED201 then
      check("0zz49 " .. f.name .. " (RED): the pre-203 file has no free aim",
        steps == 0 and fns == 0 and cast == 0 and order == 0 and reset == 0 and sw == 0)
    else
      check("0zz49 " .. f.name .. ": 24 headings (" .. steps .. "), the three functions (" .. fns .. "), the cast branch ("
        .. cast .. "), the oriented order (" .. order .. "), the reset (" .. reset .. "), the test switch (" .. sw .. ")",
        steps == 1 and fns == 3 and cast == 1 and order == 1 and reset == 1 and sw == 1)
    end
  end
  local FILES = { { path = A201, tag = "[annotated] " }, { path = L201, tag = "[live] " } }
  local n_ok, n_all = 0, 0
  local function done(ok) n_all = n_all + 1; if ok then n_ok = n_ok + 1 end end
  local function casts(W, key)
    local u, g = 0, 0
    for _, x in ipairs(W.fires) do if x.key == key then u = u + 1 end end
    for _, x in ipairs(W.ground_fires or {}) do if x.key == key then g = g + 1 end end
    return u, g
  end
  -- the distance from a point to the segment S-E
  local function seg(px, pz, sx, sz, ex, ez)
    local l2 = (ex - sx) ^ 2 + (ez - sz) ^ 2
    local t = 0
    if l2 > 0 then t = math.max(0, math.min(1, ((px - sx) * (ex - sx) + (pz - sz) * (ez - sz)) / l2)) end
    return math.sqrt((px - (sx + t * (ex - sx))) ^ 2 + (pz - (sz + t * (ez - sz))) ^ 2)
  end
  local function mk(wname, key, marker, units, enemies, PATH, TAG, opt)
    opt = opt or {}
    local cards = {}
    for _, d in ipairs(units) do cards[#cards + 1] = { id = tostring(d.uid), state = "active", vis = true } end
    local W = make_world({ can_perform = true, units = units, enemies = enemies, cards = cards,
      bar = { { id = "b1", key = key } } })
    W.defaults_on = false
    W.free_aim_on = true
    print("== " .. TAG .. wname .. " ==")
    W.bm.get_player_alliance = function() return "OUR_ALLIANCE" end
    W.bm.get_terrain_height = function(self, x, z) return 0 end
    v = nil
    if opt.no_vector ~= true then v = function(x, y, z) return { vx = x, vy = y, vz = z } end end
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
    polln(W, 6)
    v = nil
    return W
  end
  local function eng(uid, key)
    return { name = ENG, uid = uid, owns = { key }, melee = false, dist = 60, pos = { 0, 0, 0 }, width = 2, men_alive = 1,
             unit_class = "com", hp_frac = 1.0 }
  end
  local function zom(uid, x, z, o)
    local e = { uid = uid, name = ZOM, melee = false, pos = { x, 0, z }, width = 30, men_alive = 160, initial_men = 160,
                unit_class = "inf_mel", dist = math.sqrt(x * x + z * z) }
    for k, val in pairs(o or {}) do e[k] = val end
    return e
  end
  local function miners(uid, x, z)
    return { name = MIN, uid = uid, owns = {}, melee = false, pos = { x, 0, z }, width = 30, men_alive = 100,
             initial_men = 100, unit_class = "inf_mel", dist = 30 }
  end
  local function verdict(TAG, id, text, ok)
    check(TAG .. id .. (RED201 and "-RED" or "") .. ": " .. text, ok)
    done(ok)
  end
  for _, f in ipairs(FILES) do
    local TAG, P = f.tag, f.path
    do
      local W = mk("FA1. Zombies at (0,60), our Miners at (0,30) on the caster's line", RING, "fiery_ring_of_thori",
        { eng(20101, RING), miners(20102, 0, 30) }, { zom(20105, 0, 60) }, P, TAG)
      if W ~= nil then
        local u, g = casts(W, RING)
        local good, txt = false, u .. " unit-form, " .. g .. " ground"
        if RED201 then
          good = (u == 0 and g == 0)
        elseif u == 0 and g == 1 then
          local o = W.ground_fires[1]
          local a = math.rad(o.orient)
          local sx, sz = o.pos.vx, o.pos.vz
          local ex, ez = sx + math.sin(a) * 72, sz + math.cos(a) * 72
          local start = math.sqrt(sx * sx + sz * sz)
          local d_zom, d_min = seg(0, 60, sx, sz, ex, ez), seg(0, 30, sx, sz, ex, ez)
          txt = txt .. string.format("; start (%.1f,%.1f) %.1f m from the caster, bearing %.0f, %.1f m from the Zombies' centre, "
            .. "%.1f m from the Miners' centre", sx, sz, start, o.orient, d_zom, d_min)
          good = start <= 80.01 and d_zom <= 6 and d_min > 16 and o.width == 0
        end
        verdict(TAG, "FA1a", (RED201 and "no order at all" or "ONE aimed ground order on a free path") .. " (" .. txt .. ")", good)
        if not RED201 then
          local l = (TAG ~= "[live] ") or (count_log(W, "FREE AIM: the wave starts at") >= 1
            and count_log(W, "  free-aim cast          : perform_special_ability_ground('" .. RING) == 1)
          verdict(TAG, "FA1b", "the log names the free aim and the oriented order", l)
        end
        tally(W)
      else
        done(false)
      end
    end
    do
      local W = mk("FA2. Zombies at (0,60), no friend in the way", RING, "fiery_ring_of_thori",
        { eng(20111, RING) }, { zom(20115, 0, 60) }, P, TAG)
      if W ~= nil then
        local u, g = casts(W, RING)
        verdict(TAG, "FA2a", "ONE unit-form order, no ground order (" .. u .. ", " .. g .. ")", u == 1 and g == 0)
        tally(W)
      else
        done(false)
      end
    end
    do
      local W = mk("FA3. two Zombie units side by side at (-20,60) and (20,60)", RING, "fiery_ring_of_thori",
        { eng(20121, RING) }, { zom(20125, -20, 60), zom(20126, 20, 60) }, P, TAG)
      if W ~= nil then
        local u, g = casts(W, RING)
        local good = (u == 0 and g == 1)
        local txt = u .. " unit-form, " .. g .. " ground"
        if good then
          local o = W.ground_fires[1]
          local a = math.rad(o.orient)
          local sx, sz = o.pos.vx, o.pos.vz
          local ex, ez = sx + math.sin(a) * 72, sz + math.cos(a) * 72
          local d1, d2 = seg(-20, 60, sx, sz, ex, ez), seg(20, 60, sx, sz, ex, ez)
          txt = txt .. string.format("; bearing %.0f, %.1f m and %.1f m from the two centres", o.orient, d1, d2)
          good = d1 <= 21 and d2 <= 21
        end
        if RED201 then good = (u == 1 and g == 0) end
        verdict(TAG, "FA3a", (RED201 and "ONE unit-form order" or "ONE aimed ground order across both") .. " (" .. txt .. ")", good)
        tally(W)
      else
        done(false)
      end
    end
    do
      local W = mk("FA4. FA1 without the game's vector constructor", RING, "fiery_ring_of_thori",
        { eng(20131, RING), miners(20132, 0, 30) }, { zom(20135, 0, 60) }, P, TAG, { no_vector = true })
      if W ~= nil then
        local u, g = casts(W, RING)
        verdict(TAG, "FA4a", "no order, fail closed (" .. u .. ", " .. g .. ")", u == 0 and g == 0)
        tally(W)
      else
        done(false)
      end
    end
    do
      local W = mk("FA5. Blue Fire of Chaos (ground-only), an enemy at (30,40), the line clear", BLUE, "blue_fire",
        { eng(20141, BLUE) }, { zom(20145, 30, 40) }, P, TAG)
      if W ~= nil then
        local u, g = casts(W, BLUE)
        local o = W.ground_fires[1]
        local good, txt = false, u .. " unit-form, " .. g .. " ground"
        if u == 0 and g == 1 then
          if RED201 then
            good = (o.orient == 0)
            txt = txt .. "; orientation " .. tostring(o.orient)
          else
            local sx, sz = o.pos.vx, o.pos.vz
            -- the start lies on the caster's line (x / z = 30 / 40), before the enemy's centre
            txt = txt .. string.format("; start (%.1f,%.1f), orientation %.1f", sx, sz, o.orient)
            good = math.abs(o.orient - 36.87) < 0.01 and math.abs(sx * 40 - sz * 30) < 0.01 and sz < 40
          end
        end
        verdict(TAG, "FA5a", (RED201 and "the old order: orientation 0" or "ONE ground order at the path's start, orientation 37")
          .. " (" .. txt .. ")", good)
        tally(W)
      else
        done(false)
      end
    end
    do
      local W = mk("FA6. FA1 with the Zombies walking", RING, "fiery_ring_of_thori",
        { eng(20151, RING), miners(20152, 0, 30) }, { zom(20155, 0, 60, { moving = true }) }, P, TAG)
      if W ~= nil then
        local u, g = casts(W, RING)
        verdict(TAG, "FA6a", "no order on a moving target (" .. u .. ", " .. g .. ")", u == 0 and g == 0)
        tally(W)
      else
        done(false)
      end
    end
  end
  check("HARNESS 201: every world behaved - " .. n_ok .. "/" .. n_all, n_ok == n_all)
  print("== HARNESS 201 done: " .. (checks - pre201) .. " checks in this section ==")
end
