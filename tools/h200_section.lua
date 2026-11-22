-- ============================================================================
-- HARNESS 200 (round 202, user 2026-11-22: "Yes, build the probe"). THE WAVE PROBE, the console command zz_wave.
--   0zz48 the round-202 tokens in both files.
--   A Master Engineer at (0,0) owns the Fiery Ring of Thori. Zombies stand at (30,40): 50 m away, compass bearing 37.
--   WP1 selected, zz_wave(90) -> ONE ground order for the ring with orientation 90 at the enemy's position, and the
--       answer line names the bearing 37 and "ORIENTATION SENT 90". RED: the command does not exist.
--   WP2 selected, zz_wave() -> the orientation sent is the bearing (37).
--   WP3 nothing selected, zz_wave(90) -> "select exactly ONE unit", no order.
--   WP4 selected, zz_wave(0, 10, 0) with no vector constructor -> "could not be built", no order (fail closed).
--   WP5 selected, zz_wave(0, 10, 5) with a vector constructor -> ONE order at the built point (39, 44).
--   WP6 no call at all, 8 polls -> the probe orders nothing by itself (no ground order).
--   RED control: H200_LIVE / H200_ANN on docs/backups/round202/pre202_*.lua.
-- ============================================================================
function run_h200()
  local L200 = os.getenv("H200_LIVE") or LIVE
  local A200 = os.getenv("H200_ANN") or ANN
  local RED200 = (os.getenv("H200_LIVE") ~= nil) or (os.getenv("H200_ANN") ~= nil)
  local RING = "wh_main_item_abilities_fiery_ring_of_thori"
  local ENG = "wh_main_dwf_cha_master_engineer_0"
  local ZOM = "wh_main_vmp_inf_zombie"
  local pre200 = checks
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1; at = i + #tok
    end
  end
  print("== HARNESS 200 - section 0zz48: the round-202 tokens ==")
  for _, f in ipairs({ { name = "live", path = L200 }, { name = "ann", path = A200 } }) do
    local s = read_file(f.path)
    local fn = cp(s, "\nfunction zz_wave(deg, fwd, side, key)\n")
    local call = cp(s, "su.uc:perform_special_ability_ground(key, pos, deg, 0)")
    local users = cp(s, "zz_wave(")
    if RED200 then
      check("0zz48 " .. f.name .. " (RED): the pre-202 file has no wave probe", fn == 0 and call == 0 and users == 0)
    else
      -- three mentions: the two comment lines of its banner and the definition. Nothing calls it.
      check("0zz48 " .. f.name .. ": zz_wave is defined once (" .. fn .. "), sends the orientation (" .. call
        .. "), and nothing calls it (" .. users .. " mentions)", fn == 1 and call == 1 and users == 2)
    end
  end
  local FILES = { { path = A200, tag = "[annotated] " }, { path = L200, tag = "[live] " } }
  local n_ok, n_all = 0, 0
  local function done(ok) n_all = n_all + 1; if ok then n_ok = n_ok + 1 end end
  local function has(m, t) return type(m) == "string" and raw_find(m, t, 1, true) ~= nil end
  local function mk(wname, uid, PATH, TAG, select)
    local c = { name = ENG, uid = uid, owns = { RING }, melee = false, dist = 50, pos = { 0, 0, 0 }, width = 2,
                men_alive = 1, unit_class = "com", hp_frac = 1.0 }
    local e = { uid = uid + 1, name = ZOM, melee = false, pos = { 30, 0, 40 }, width = 30, men_alive = 160,
                initial_men = 160, unit_class = "inf_mel", dist = 50 }
    local W = make_world({ can_perform = true, units = { c }, enemies = { e },
      cards = { { id = tostring(uid), state = "active", vis = true } }, bar = { { id = "b1", key = RING } } })
    W.defaults_on = false
    print("== " .. TAG .. wname .. " ==")
    W.bm.get_player_alliance = function() return "OUR_ALLIANCE" end
    zz_wave = nil   -- one Lua state loads many copies: an earlier copy's command must not answer for this one
    v = nil
    local ok = pcall(load_world, W, PATH)
    check(TAG .. wname .. ": the file loads", ok)
    if not ok then tally(W); return nil end
    deploy_phases(W); ui(W)
    for i = 1, #(W.enemy_entries or {}) do
      local pr = W.enemy_entries[i]
      if pr ~= nil and pr.unit ~= nil then
        pr.unit.is_visible_to_alliance = function(self, a) return true end
        pr.unit.is_currently_flying = function(self) return false end
        pr.unit.strategic_value = function(self) return 100 end
      end
    end
    if select then sel_event(W, uid, true); ui(W); ui(W) end
    W.conflict = true
    return W
  end
  local function verdict(TAG, id, text, ok)
    check(TAG .. id .. (RED200 and "-RED" or "") .. ": " .. text, ok)
    done(ok)
  end
  local function call(...)
    if type(zz_wave) ~= "function" then return false, "zz_wave does not exist" end
    return pcall(zz_wave, ...)
  end
  for _, f in ipairs(FILES) do
    local TAG, P = f.tag, f.path
    do
      local W = mk("WP1. the Engineer selected, zz_wave(90)", 20001, P, TAG, true)
      if W ~= nil then
        local ok, m = call(90)
        local g = W.ground_fires[1]
        local good = ok and #W.ground_fires == 1 and #W.fires == 0 and g.key == RING and g.orient == 90 and g.width == 0
          and has(m, "WAVE PROBE: " .. RING) and has(m, "ORIENTATION SENT 90") and has(m, "bearing caster->target 37")
          and has(m, "50.0 m away") and has(m, "order accepted")
        if RED200 then good = (not ok) and #W.ground_fires == 0 end
        verdict(TAG, "WP1a", (RED200 and "the command does not exist, no order" or "ONE ground order, orientation 90")
          .. " (" .. tostring(m) .. ")", good)
        tally(W)
      else
        done(false)
      end
    end
    do
      local W = mk("WP2. the Engineer selected, zz_wave() with no direction", 20011, P, TAG, true)
      if W ~= nil then
        local ok, m = call()
        local g = W.ground_fires[1]
        local good = ok and #W.ground_fires == 1 and g.key == RING and math.abs(g.orient - 36.87) < 0.01
          and has(m, "ORIENTATION SENT 37")
        if RED200 then good = (not ok) and #W.ground_fires == 0 end
        verdict(TAG, "WP2a", "the orientation sent is the bearing to the target (" .. tostring(m) .. ")", good)
        tally(W)
      else
        done(false)
      end
    end
    do
      local W = mk("WP3. nothing selected, zz_wave(90)", 20021, P, TAG, false)
      if W ~= nil then
        local ok, m = call(90)
        local good = ok and #W.ground_fires == 0 and #W.fires == 0 and has(m, "select exactly ONE unit")
        if RED200 then good = (not ok) and #W.ground_fires == 0 end
        verdict(TAG, "WP3a", "no order (" .. tostring(m) .. ")", good)
        tally(W)
      else
        done(false)
      end
    end
    do
      local W = mk("WP4. the Engineer selected, zz_wave(0, 10, 0), no vector constructor", 20031, P, TAG, true)
      if W ~= nil then
        local ok, m = call(0, 10, 0)
        local good = ok and #W.ground_fires == 0 and has(m, "could not be built")
        if RED200 then good = (not ok) and #W.ground_fires == 0 end
        verdict(TAG, "WP4a", "fails closed, no order (" .. tostring(m) .. ")", good)
        tally(W)
      else
        done(false)
      end
    end
    do
      local W = mk("WP5. the Engineer selected, zz_wave(0, 10, 5), a vector constructor", 20041, P, TAG, true)
      if W ~= nil then
        v = function(x, y, z) return { vx = x, vy = y, vz = z } end
        local ok, m = call(0, 10, 5)
        v = nil
        local g = W.ground_fires[1]
        -- the heading is (0.6, 0.8): 10 m further = (36, 48), 5 m to the right = (+4, -3) -> (40, 45)
        local good = ok and #W.ground_fires == 1 and g.orient == 0 and type(g.pos) == "table"
          and math.abs(g.pos.vx - 40) < 0.01 and math.abs(g.pos.vz - 45) < 0.01 and has(m, "point (40.0,45.0) = a built point")
        if RED200 then good = (not ok) and #W.ground_fires == 0 end
        verdict(TAG, "WP5a", "ONE order at the built point (" .. tostring(m) .. ")", good)
        tally(W)
      else
        done(false)
      end
    end
    do
      local W = mk("WP6. no call, 8 polls", 20051, P, TAG, true)
      if W ~= nil then
        polln(W, 8)
        verdict(TAG, "WP6a", "the probe orders nothing by itself (ground orders " .. #W.ground_fires .. ")",
          #W.ground_fires == 0)
        tally(W)
      else
        done(false)
      end
    end
  end
  zz_wave = nil
  check("HARNESS 200: every world behaved - " .. n_ok .. "/" .. n_all, n_ok == n_all)
  print("== HARNESS 200 done: " .. (checks - pre200) .. " checks in this section ==")
end
