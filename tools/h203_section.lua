-- ============================================================================
-- HARNESS 203 (round 205, user 2026-11-22: "I tested with Sunfang and it casted on the terrain, not on the enemy unit"
--   and "we should also ignore enemy single entities as the damage to them would be negligible").
--   0zz51 the round-205 tokens in both files.
--   A hero at (0,0) owns Sunfang: a CONE, 0.1 m wide at its start, growing 0.25 m per metre to 12 m over its 48 m path.
--   CN1 our block at (0,40) fights an enemy block at (0,48) (they overlap) -> ONE aimed order whose REAL CONE has at
--       most 5 of our soldiers and at least 30 enemy soldiers under it. RED (round 204, a 12 m band from start to end):
--       ONE order whose real cone has fewer than 30 enemy soldiers under it (what the user saw: fire on the terrain).
--   SE1 the only enemy is a single entity standing at (0,50) -> no order. RED: ONE order.
--   SE2 an enemy single entity at (0,50) and an enemy block at (40,50) -> ONE order whose real cone has at least 30
--       soldiers of the block under it (the single entity does not attract the wave). GREEN only.
--   RED control: H203_LIVE / H203_ANN on docs/backups/round205/pre205_*.lua.
-- ============================================================================
function run_h203()
  local L203 = os.getenv("H203_LIVE") or LIVE
  local A203 = os.getenv("H203_ANN") or ANN
  local RED203 = (os.getenv("H203_LIVE") ~= nil) or (os.getenv("H203_ANN") ~= nil)
  local SUN = "wh2_main_weapon_abilities_sunfang"
  local HERO = "wh2_main_hef_cha_tyrion_0"
  local GG = "wh_main_vmp_inf_grave_guard_0"
  local SHIP = "wh3_dlc27_hef_inf_ships_company"
  local LORD = "wh_main_vmp_cha_vampire_lord_0"
  local pre203 = checks
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1; at = i + #tok
    end
  end
  print("== HARNESS 203 - section 0zz51: the round-205 tokens ==")
  for _, f in ipairs({ { name = "live", path = L203 }, { name = "ann", path = A203 } }) do
    local s = read_file(f.path)
    local txt = cp(s, '\nFOURTH.WW_CONE_TEXT = "')
    local sun = cp(s, "wh2_main_weapon_abilities_sunfang=0.1,0.25")
    local ring = cp(s, "wh_main_item_abilities_fiery_ring_of_thori=0.1,0.0833")
    local fn = cp(s, "\nfunction FOURTH.ww_in_wave(px, pz, sx, sz, ex, ez, r)\n")
    local use = cp(s, "FOURTH.ww_in_wave(")
    local slot = cp(s, "\t\tFOURTH.ww_cone = (row.r0 ~= nil) and row or nil   -- ROUND 205")
    local single = cp(s, "\t\t\tif o.men > 1 then\n\t\t\t\tlocal c = FOURTH.wave_cover(o, sx, sz, ex, ez, row.r)\n")
    if RED203 then
      check("0zz51 " .. f.name .. " (RED): the pre-205 file has no cone table and counts enemy single entities",
        txt == 0 and sun == 0 and fn == 0 and use == 0 and slot == 0 and single == 0)
    else
      check("0zz51 " .. f.name .. ": the cone table (" .. txt .. ") with Sunfang (" .. sun .. ") and the ring (" .. ring
        .. "), ww_in_wave (" .. fn .. ", " .. use .. " mentions), the cone slot (" .. slot .. "), enemy single entities skipped ("
        .. single .. ")", txt == 1 and sun == 1 and ring == 1 and fn == 1 and use == 3 and slot == 1 and single == 1)
    end
  end
  local FILES = { { path = A203, tag = "[annotated] " }, { path = L203, tag = "[live] " } }
  local n_ok, n_all = 0, 0
  local function done(ok) n_all = n_all + 1; if ok then n_ok = n_ok + 1 end end
  local function casts(W, key)
    local u, g = 0, 0
    for _, x in ipairs(W.fires) do if x.key == key then u = u + 1 end end
    for _, x in ipairs(W.ground_fires or {}) do if x.key == key then g = g + 1 end end
    return u, g
  end
  -- the soldiers of an axis-aligned block (x x0..x1, z z0..z1, men spread evenly) under Sunfang's REAL cone
  local function under_cone(o, x0, x1, z0, z1, men)
    local a = math.rad(o.orient)
    local sx, sz = o.pos.vx, o.pos.vz
    local hx, hz = math.sin(a), math.cos(a)
    local hit, all = 0, 0
    for x = x0 + 0.5, x1 - 0.5, 1 do
      for z = z0 + 0.5, z1 - 0.5, 1 do
        all = all + 1
        local d = (x - sx) * hx + (z - sz) * hz
        if d < 0 then d = 0 elseif d > 48 then d = 48 end
        local rr = math.min(12, 0.1 + 0.25 * d)
        local qx, qz = sx + hx * d, sz + hz * d
        if (x - qx) ^ 2 + (z - qz) ^ 2 <= rr * rr then hit = hit + 1 end
      end
    end
    return men * hit / all
  end
  local function mk(wname, units, enemies, PATH, TAG)
    local cards = {}
    for _, d in ipairs(units) do cards[#cards + 1] = { id = tostring(d.uid), state = "active", vis = true } end
    local W = make_world({ can_perform = true, units = units, enemies = enemies, cards = cards,
      bar = { { id = "b1", key = SUN } } })
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
        pr.unit.strategic_value = function(self) return 1000 end
      end
    end
    sel_event(W, units[1].uid, true); ui(W); ui(W)
    pcall(click, W, "zz_auto_badge_sunfang"); ui(W)
    sel_event(W, units[1].uid, false); ui(W)
    W.conflict = true
    polln(W, 6)
    v = nil
    return W
  end
  local function hero(uid)
    return { name = HERO, uid = uid, owns = { SUN }, melee = false, dist = 40, pos = { 0, 0, 0 }, width = 2, men_alive = 1,
             unit_class = "com", hp_frac = 1.0 }
  end
  local function block(uid, name, x, z, men, o)
    local e = { uid = uid, name = name, melee = true, pos = { x, 0, z }, width = 30, men_alive = men, initial_men = men,
                unit_class = "inf_mel", dist = math.sqrt(x * x + z * z), owns = {} }
    for k, val in pairs(o or {}) do e[k] = val end
    return e
  end
  local function lord(uid, x, z)
    return { uid = uid, name = LORD, melee = false, pos = { x, 0, z }, width = 2, men_alive = 1, initial_men = 1,
             unit_class = "com", dist = math.sqrt(x * x + z * z) }
  end
  local function verdict(TAG, id, text, ok)
    check(TAG .. id .. (RED203 and "-RED" or "") .. ": " .. text, ok)
    done(ok)
  end
  for _, f in ipairs(FILES) do
    local TAG, P = f.tag, f.path
    do
      -- the mock's blocks: ours 120 men -> 6 ranks x 1.6 = 9.6 m deep (z 35.2..44.8); theirs 120 men (z 43.2..52.8)
      local W = mk("CN1. Sunfang: our block at (0,40) fights an enemy block at (0,48)",
        { hero(20301), block(20302, SHIP, 0, 40, 120) }, { block(20305, GG, 0, 48, 120) }, P, TAG)
      if W ~= nil then
        local u, g = casts(W, SUN)
        local good, txt = false, u .. " unit-form, " .. g .. " ground"
        if u == 0 and g == 1 then
          local o = W.ground_fires[1]
          local ours, theirs = under_cone(o, -15, 15, 35.2, 44.8, 120), under_cone(o, -15, 15, 43.2, 52.8, 120)
          txt = txt .. string.format("; start (%.1f,%.1f), bearing %.0f: the real cone covers %.1f of our soldiers and %.0f "
            .. "enemy soldiers", o.pos.vx, o.pos.vz, o.orient, ours, theirs)
          if RED203 then good = theirs < 30 else good = (ours <= 5 and theirs >= 30) end
        end
        verdict(TAG, "CN1a", (RED203 and "ONE order whose real cone misses (fewer than 30 enemy soldiers)"
          or "ONE order: the real cone covers at most 5 of ours and at least 30 enemy soldiers") .. " (" .. txt .. ")", good)
        tally(W)
      else
        done(false)
      end
    end
    do
      local W = mk("SE1. Sunfang: the only enemy is a single entity standing at (0,50)", { hero(20311) }, { lord(20315, 0, 50) }, P, TAG)
      if W ~= nil then
        local u, g = casts(W, SUN)
        local good = (u == 0 and g == 0)
        if RED203 then good = (u + g == 1) end
        verdict(TAG, "SE1a", (RED203 and "ONE order at the single entity" or "no order, a single entity is not worth a wave")
          .. " (" .. u .. ", " .. g .. ")", good)
        tally(W)
      else
        done(false)
      end
    end
    if not RED203 then
      local W = mk("SE2. Sunfang: an enemy single entity at (0,50) and an enemy block at (40,50)", { hero(20321) },
        { lord(20325, 0, 50), block(20326, GG, 40, 50, 120, { melee = false }) }, P, TAG)
      if W ~= nil then
        local u, g = casts(W, SUN)
        local good, txt = false, u .. " unit-form, " .. g .. " ground"
        if u == 0 and g == 1 then
          local theirs = under_cone(W.ground_fires[1], 25, 55, 45.2, 54.8, 120)
          txt = txt .. string.format("; the real cone covers %.0f soldiers of the block", theirs)
          good = theirs >= 30
        end
        verdict(TAG, "SE2a", "ONE order at the block (" .. txt .. ")", good)
        tally(W)
      else
        done(false)
      end
    end
  end
  check("HARNESS 203: every world behaved - " .. n_ok .. "/" .. n_all, n_ok == n_all)
  print("== HARNESS 203 done: " .. (checks - pre203) .. " checks in this section ==")
end
