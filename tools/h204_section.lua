-- ============================================================================
-- HARNESS 204 (round 206, tuning, from the user's Sunfang battle: the first cast landed behind a unit that was still
--   walking in, the second, on standing units, was perfect).
--   0zz52 the round-206 token in both files.
--   A hero at (0,0) owns Sunfang. An enemy block S STANDS at (-20,60).
--   MV1 S alone -> ONE aimed order (its start and bearing are remembered).
--   MV2 S and a second block M WALKING at (20,60) -> ONE aimed order with THE SAME start and bearing as MV1 (the walking
--       unit does not pull the cone). RED (round 205): a different order, aimed across both.
--   MV3 only the walking block M -> no order (GREEN and RED: a path needs a standing enemy to anchor on).
--   RED control: H204_LIVE / H204_ANN on docs/backups/round206/pre206_*.lua.
-- ============================================================================
function run_h204()
  local L204 = os.getenv("H204_LIVE") or LIVE
  local A204 = os.getenv("H204_ANN") or ANN
  local RED204 = (os.getenv("H204_LIVE") ~= nil) or (os.getenv("H204_ANN") ~= nil)
  local SUN = "wh2_main_weapon_abilities_sunfang"
  local HERO = "wh2_main_hef_cha_tyrion_0"
  local GG = "wh_main_vmp_inf_grave_guard_0"
  local pre204 = checks
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1; at = i + #tok
    end
  end
  print("== HARNESS 204 - section 0zz52: the round-206 token ==")
  for _, f in ipairs({ { name = "live", path = L204 }, { name = "ann", path = A204 } }) do
    local s = read_file(f.path)
    local still = cp(s, "\t\t\tif o.still == nil then o.still = FOURTH.ww_target_still(o) end\n")
    local use = cp(s, "\t\t\t\tif c > 0 and o.still then val = val + (o.value or 1) * c end\n")
    if RED204 then
      check("0zz52 " .. f.name .. " (RED): the pre-206 file counts walking enemies", still == 0 and use == 0)
    else
      check("0zz52 " .. f.name .. ": a walking enemy is not counted (" .. still .. ", " .. use .. ")", still == 1 and use == 1)
    end
  end
  local FILES = { { path = A204, tag = "[annotated] " }, { path = L204, tag = "[live] " } }
  local n_ok, n_all = 0, 0
  local function done(ok) n_all = n_all + 1; if ok then n_ok = n_ok + 1 end end
  local function mk(wname, enemies, PATH, TAG)
    local c = { name = HERO, uid = enemies[1].uid - 4, owns = { SUN }, melee = false, dist = 50, pos = { 0, 0, 0 }, width = 2,
                men_alive = 1, unit_class = "com", hp_frac = 1.0 }
    local W = make_world({ can_perform = true, units = { c }, enemies = enemies,
      cards = { { id = tostring(c.uid), state = "active", vis = true } }, bar = { { id = "b1", key = SUN } } })
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
    sel_event(W, c.uid, true); ui(W); ui(W)
    pcall(click, W, "zz_auto_badge_sunfang"); ui(W)
    sel_event(W, c.uid, false); ui(W)
    W.conflict = true
    polln(W, 6)
    v = nil
    return W
  end
  local function block(uid, x, z, moving)
    return { uid = uid, name = GG, melee = false, pos = { x, 0, z }, width = 30, men_alive = 120, initial_men = 120,
             unit_class = "inf_mel", dist = math.sqrt(x * x + z * z), moving = moving }
  end
  local function verdict(TAG, id, text, ok)
    check(TAG .. id .. (RED204 and "-RED" or "") .. ": " .. text, ok)
    done(ok)
  end
  local function order(W)
    local o = (#W.fires == 0 and #W.ground_fires == 1) and W.ground_fires[1] or nil
    if o == nil then return nil end
    return string.format("start (%.1f,%.1f) bearing %.0f", o.pos.vx, o.pos.vz, o.orient)
  end
  for _, f in ipairs(FILES) do
    local TAG, P = f.tag, f.path
    local alone = nil
    do
      local W = mk("MV1. Sunfang: one block standing at (-20,60)", { block(20405, -20, 60, false) }, P, TAG)
      if W ~= nil then
        alone = order(W)
        verdict(TAG, "MV1a", "ONE aimed order (" .. tostring(alone) .. ")", alone ~= nil)
        tally(W)
      else
        done(false)
      end
    end
    do
      local W = mk("MV2. Sunfang: the standing block and a second block walking at (20,60)",
        { block(20415, -20, 60, false), block(20416, 20, 60, true) }, P, TAG)
      if W ~= nil then
        local both = order(W)
        local good = (both ~= nil and both == alone)
        if RED204 then good = (both ~= nil and both ~= alone) end
        verdict(TAG, "MV2a", (RED204 and "a different order, pulled by the walking unit" or "the same order as with the standing block alone")
          .. " (" .. tostring(both) .. " vs " .. tostring(alone) .. ")", good)
        tally(W)
      else
        done(false)
      end
    end
    do
      local W = mk("MV3. Sunfang: only a walking block", { block(20425, 20, 60, true) }, P, TAG)
      if W ~= nil then
        verdict(TAG, "MV3a", "no order (" .. #W.fires .. ", " .. #W.ground_fires .. ")", #W.fires == 0 and #W.ground_fires == 0)
        tally(W)
      else
        done(false)
      end
    end
  end
  check("HARNESS 204: every world behaved - " .. n_ok .. "/" .. n_all, n_ok == n_all)
  print("== HARNESS 204 done: " .. (checks - pre204) .. " checks in this section ==")
end
