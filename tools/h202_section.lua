-- ============================================================================
-- HARNESS 202 (round 204, user ruling 2026-11-22: "the safety was meant for abilities that have a deviation from their
--   path ... We only need to know that in the path of the ability, there is very little of our ... soldiers ... we
--   should ignore single entities ... please implement for tight call and wind blast").
--   It replaces run_h201 (round 203's worlds tested paths through the centre with the 16 m distance).
--   0zz50 the round-204 tokens in both files.
--   A Master Engineer at (0,0) owns the Fiery Ring of Thori (an EXACT wave: radius 6, path 72, no drift).
--   EX1 the user's battle: our Miners at (0,40) fight Skeletons at (0,48) (the two blocks overlap) -> ONE aimed ground
--       order with at most 5 of our soldiers under the wave and at least 40 Skeletons under it. RED (round 203): no
--       order (every path through the enemy's centre passes within 16 m of the Miners).
--   EX2 one of OUR HEROES stands inside the Zombies at (0,60), no other friend -> ONE aimed ground order (a single
--       entity of ours is not counted). RED: no order.
--   EX3 Tidecall, a STANDING enemy at (0,50), nothing charging -> ONE aimed ground order (Tidecall rides enemy_wave
--       now). RED: no order (the charge trigger).
--   EX4 Wind of Death (a wave WITH drift) in the EX1 melee -> no order (the safety distance stays). GREEN and RED.
--   EX5 nothing in the way, Zombies at (0,60) -> ONE aimed ground order along the block's frontage (an exact wave is
--       always aimed, and the path under the most soldiers wins). RED: ONE unit-form order.
--   EX6 EX1 without the game's vector constructor -> no order (fail closed). GREEN and RED.
--   EX7 EX1 with the Skeletons WALKING -> no order (standing targets only). GREEN and RED.
--   RED control: H202_LIVE / H202_ANN on docs/backups/round204/pre204_*.lua.
-- ============================================================================
function run_h202()
  local L202 = os.getenv("H202_LIVE") or LIVE
  local A202 = os.getenv("H202_ANN") or ANN
  local RED202 = (os.getenv("H202_LIVE") ~= nil) or (os.getenv("H202_ANN") ~= nil)
  local RING = "wh_main_item_abilities_fiery_ring_of_thori"
  local TIDE = "wh2_dlc11_spell_bound_tidecall"
  local WOD = "wh2_dlc15_spell_bound_wind_of_death"
  local ENG = "wh_main_dwf_cha_master_engineer_0"
  local ZOM = "wh_main_vmp_inf_zombie"
  local SKE = "wh_main_vmp_inf_skeleton_warriors_1"
  local MIN = "wh_main_dwf_inf_miners_0"
  local pre202 = checks
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1; at = i + #tok
    end
  end
  print("== HARNESS 202 - section 0zz50: the round-204 tokens ==")
  for _, f in ipairs({ { name = "live", path = L202 }, { name = "ann", path = A202 } }) do
    local s = read_file(f.path)
    local own = cp(s, "\nFOURTH.WAVE_OWN_MAX = 5 ")
    local fns = cp(s, "\nfunction FOURTH.wave_cover(s, sx, sz, ex, ez, r)\n") + cp(s, "\nfunction FOURTH.ww_exact(row)\n")
      + cp(s, "\nfunction FOURTH.ww_aim_value(unit, e, m, row, hx, hz, shift)\n")
    local single = cp(s, "\t\t\t\tif o.men > 1 then\n")
    local shifts = cp(s, "\nFOURTH.FREE_AIM_SHIFTS = { 0, 6, -6, 12, -12, 18, -18 }")
    local waves = cp(s, 'trigger = "enemy_wave"')
    local charge = cp(s, 'trigger = "enemy_wave_charge"')
    local steps = cp(s, "\nFOURTH.FREE_AIM_STEPS = 24 ")
    local order = cp(s, "uc:perform_special_ability_ground(ability_key, pos, aim.deg, 0)")
    local reset = cp(s, "\tFOURTH.ww_aim = nil   -- ROUND 203: the free aim of a wave\n")
    if RED202 then
      check("0zz50 " .. f.name .. " (RED): the pre-204 file has no soldiers rule, 30 waves and 2 charge waves",
        own == 0 and fns == 0 and shifts == 0 and waves == 30 and charge == 2)
    else
      check("0zz50 " .. f.name .. ": the limit of 5 (" .. own .. "), the three functions (" .. fns .. "), single entities skipped ("
        .. single .. "), the shifts (" .. shifts .. "), " .. waves .. " waves, " .. charge .. " charge waves, round 203's 24 headings ("
        .. steps .. "), oriented order (" .. order .. ") and reset (" .. reset .. ")",
        own == 1 and fns == 3 and single == 1 and shifts == 1 and waves == 32 and charge == 0 and steps == 1 and order == 1
        and reset == 1)
    end
  end
  local FILES = { { path = A202, tag = "[annotated] " }, { path = L202, tag = "[live] " } }
  local n_ok, n_all = 0, 0
  local function done(ok) n_all = n_all + 1; if ok then n_ok = n_ok + 1 end end
  local function casts(W, key)
    local u, g = 0, 0
    for _, x in ipairs(W.fires) do if x.key == key then u = u + 1 end end
    for _, x in ipairs(W.ground_fires or {}) do if x.key == key then g = g + 1 end end
    return u, g
  end
  local function seg(px, pz, sx, sz, ex, ez)
    local l2 = (ex - sx) ^ 2 + (ez - sz) ^ 2
    local t = 0
    if l2 > 0 then t = math.max(0, math.min(1, ((px - sx) * (ex - sx) + (pz - sz) * (ez - sz)) / l2)) end
    return math.sqrt((px - (sx + t * (ex - sx))) ^ 2 + (pz - (sz + t * (ez - sz))) ^ 2)
  end
  -- the soldiers of an axis-aligned block (x -15..15, z z0..z1, men spread evenly) under the wave of an order
  local function under(o, z0, z1, men, r, path)
    local a = math.rad(o.orient)
    local sx, sz = o.pos.vx, o.pos.vz
    local ex, ez = sx + math.sin(a) * path, sz + math.cos(a) * path
    local hit, all = 0, 0
    for x = -14.5, 14.5, 1 do
      for z = z0 + 0.5, z1 - 0.5, 1 do
        all = all + 1
        if seg(x, z, sx, sz, ex, ez) <= r then hit = hit + 1 end
      end
    end
    return men * hit / all
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
    return { name = ENG, uid = uid, owns = { key }, melee = false, dist = 40, pos = { 0, 0, 0 }, width = 2, men_alive = 1,
             unit_class = "com", hp_frac = 1.0 }
  end
  local function foe(uid, name, x, z, o)
    local e = { uid = uid, name = name, melee = false, pos = { x, 0, z }, width = 30, men_alive = 160, initial_men = 160,
                unit_class = "inf_mel", dist = math.sqrt(x * x + z * z) }
    for k, val in pairs(o or {}) do e[k] = val end
    return e
  end
  local function miners(uid, x, z)
    return { name = MIN, uid = uid, owns = {}, melee = true, pos = { x, 0, z }, width = 30, men_alive = 100,
             initial_men = 100, unit_class = "inf_mel", dist = 8 }
  end
  local function verdict(TAG, id, text, ok)
    check(TAG .. id .. (RED202 and "-RED" or "") .. ": " .. text, ok)
    done(ok)
  end
  for _, f in ipairs(FILES) do
    local TAG, P = f.tag, f.path
    do
      local W = mk("EX1. our Miners at (0,40) fight Skeletons at (0,48)", RING, "fiery_ring_of_thori",
        { eng(20201, RING), miners(20202, 0, 40) }, { foe(20205, SKE, 0, 48, { melee = true }) }, P, TAG)
      if W ~= nil then
        local u, g = casts(W, RING)
        local good, txt = false, u .. " unit-form, " .. g .. " ground"
        if RED202 then
          good = (u == 0 and g == 0)
        elseif u == 0 and g == 1 then
          local o = W.ground_fires[1]
          -- the mock's blocks: Miners 100 men, 8 m deep (z 36..44); Skeletons 160 men, 12.8 m deep (z 41.6..54.4)
          local ours, theirs = under(o, 36, 44, 100, 6, 72), under(o, 41.6, 54.4, 160, 6, 72)
          local start = math.sqrt(o.pos.vx ^ 2 + o.pos.vz ^ 2)
          txt = txt .. string.format("; start (%.1f,%.1f) %.1f m from the caster, bearing %.0f: %.1f of our soldiers and %.0f "
            .. "Skeletons under the wave", o.pos.vx, o.pos.vz, start, o.orient, ours, theirs)
          good = ours <= 5 and theirs >= 40 and start <= 80.01
        end
        verdict(TAG, "EX1a", (RED202 and "no order at all" or "ONE aimed order: at most 5 of ours, at least 40 Skeletons")
          .. " (" .. txt .. ")", good)
        if not RED202 then
          verdict(TAG, "EX1b", "the log names the free aim and its sideways move",
            (TAG ~= "[live] ") or (count_log(W, "FREE AIM: the wave starts at") >= 1 and count_log(W, "m sideways)") >= 1))
        end
        tally(W)
      else
        done(false)
      end
    end
    do
      local hero = { name = ENG, uid = 20212, owns = {}, melee = true, pos = { 0, 0, 60 }, width = 2, men_alive = 1,
                     unit_class = "com", hp_frac = 1.0, dist = 2 }
      local W = mk("EX2. one of our Heroes stands inside the Zombies at (0,60)", RING, "fiery_ring_of_thori",
        { eng(20211, RING), hero }, { foe(20215, ZOM, 0, 60, { melee = true }) }, P, TAG)
      if W ~= nil then
        local u, g = casts(W, RING)
        local good = (u == 0 and g == 1)
        if RED202 then good = (u == 0 and g == 0) end
        verdict(TAG, "EX2a", (RED202 and "no order" or "ONE aimed order, the single entity is not counted") .. " (" .. u .. ", " .. g .. ")", good)
        tally(W)
      else
        done(false)
      end
    end
    do
      local W = mk("EX3. Tidecall, a standing enemy at (0,50), nothing charging", TIDE, "tidecall",
        { eng(20221, TIDE) }, { foe(20225, ZOM, 0, 50) }, P, TAG)
      if W ~= nil then
        local u, g = casts(W, TIDE)
        local good = (u == 0 and g == 1)
        if RED202 then good = (u == 0 and g == 0) end
        verdict(TAG, "EX3a", (RED202 and "no order (the charge trigger)" or "ONE aimed order on a standing enemy") .. " (" .. u .. ", " .. g .. ")", good)
        tally(W)
      else
        done(false)
      end
    end
    do
      local W = mk("EX4. Wind of Death (a wave with drift) in the EX1 melee", WOD, "wind_of_death",
        { eng(20231, WOD), miners(20232, 0, 40) }, { foe(20235, SKE, 0, 48, { melee = true }) }, P, TAG)
      if W ~= nil then
        local u, g = casts(W, WOD)
        verdict(TAG, "EX4a", "no order, the safety distance stays for a drifting wave (" .. u .. ", " .. g .. ")", u == 0 and g == 0)
        tally(W)
      else
        done(false)
      end
    end
    do
      local W = mk("EX5. Zombies at (0,60), nothing in the way", RING, "fiery_ring_of_thori",
        { eng(20241, RING) }, { foe(20245, ZOM, 0, 60) }, P, TAG)
      if W ~= nil then
        local u, g = casts(W, RING)
        local good, txt = false, u .. " unit-form, " .. g .. " ground"
        if RED202 then
          good = (u == 1 and g == 0)
        elseif u == 0 and g == 1 then
          local o = W.ground_fires[1]
          -- the mock's Zombies: 160 men, 12.8 m deep (z 53.6..66.4)
          local theirs = under(o, 53.6, 66.4, 160, 6, 72)
          txt = txt .. string.format("; bearing %.0f, %.0f Zombies under the wave", o.orient, theirs)
          good = theirs >= 120
        end
        verdict(TAG, "EX5a", (RED202 and "ONE unit-form order" or "ONE aimed order under most of the block") .. " (" .. txt .. ")", good)
        tally(W)
      else
        done(false)
      end
    end
    do
      local W = mk("EX6. EX1 without the game's vector constructor", RING, "fiery_ring_of_thori",
        { eng(20251, RING), miners(20252, 0, 40) }, { foe(20255, SKE, 0, 48, { melee = true }) }, P, TAG, { no_vector = true })
      if W ~= nil then
        local u, g = casts(W, RING)
        verdict(TAG, "EX6a", "no order, fail closed (" .. u .. ", " .. g .. ")", u == 0 and g == 0)
        tally(W)
      else
        done(false)
      end
    end
    do
      local W = mk("EX7. EX1 with the Skeletons walking", RING, "fiery_ring_of_thori",
        { eng(20261, RING), miners(20262, 0, 40) }, { foe(20265, SKE, 0, 48, { moving = true }) }, P, TAG)
      if W ~= nil then
        local u, g = casts(W, RING)
        verdict(TAG, "EX7a", "no order on a moving target (" .. u .. ", " .. g .. ")", u == 0 and g == 0)
        tally(W)
      else
        done(false)
      end
    end
  end
  check("HARNESS 202: every world behaved - " .. n_ok .. "/" .. n_all, n_ok == n_all)
  print("== HARNESS 202 done: " .. (checks - pre202) .. " checks in this section ==")
end
