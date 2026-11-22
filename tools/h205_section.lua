-- ============================================================================
-- HARNESS 205 (round 207, tuning, from the afternoon code review of 2026-11-22).
--   0zz53 the round-207 tokens in both files.
--   A hero at (0,0) owns Wind of Death, a DRIFTING wave (radius 6, 100 m path, 3 s wind-up). A block S STANDS at (-20,60).
--   DW1 S alone -> ONE order (its form and aim are remembered).
--   DW2 S and a second block M WALKING at (20,60) -> the SAME order as DW1 (the walking unit adds no value). RED
--       (round 206): a different order, a path across both blocks.
--   DW3 only the walking block -> no order (GREEN and RED).
--   RED control: H205_LIVE / H205_ANN on docs/backups/round207/pre207_*.lua.
-- ============================================================================
function run_h205()
  local L205 = os.getenv("H205_LIVE") or LIVE
  local A205 = os.getenv("H205_ANN") or ANN
  local RED205 = (os.getenv("H205_LIVE") ~= nil) or (os.getenv("H205_ANN") ~= nil)
  local WOD = "wh2_dlc15_spell_bound_wind_of_death"
  local HERO = "wh2_main_hef_cha_tyrion_0"
  local GG = "wh_main_vmp_inf_grave_guard_0"
  local pre205 = checks
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1; at = i + #tok
    end
  end
  print("== HARNESS 205 - section 0zz53: the round-207 tokens ==")
  for _, f in ipairs({ { name = "live", path = L205 }, { name = "ann", path = A205 } }) do
    local s = read_file(f.path)
    local slot = cp(s, "\tFOURTH.ww_still_only = free   -- ROUND 207")
    local reset = cp(s, "\tFOURTH.ww_still_only = nil   -- ROUND 207")
    local use = cp(s, "\t\t\tif not still_only or o.still then v = v + (o.value or 0) end\n")
    local hold = cp(s, "\tif free and row.ground and aim == nil then return ")
    if RED205 then
      check("0zz53 " .. f.name .. " (RED): the pre-207 file has none of the round's tokens", slot + reset + use + hold == 0)
    else
      check("0zz53 " .. f.name .. ": the slot (" .. slot .. "), its reset (" .. reset .. "), the standing test (" .. use
        .. "), the ground-only hold (" .. hold .. ")", slot == 1 and reset == 1 and use == 1 and hold == 1)
    end
  end
  local FILES = { { path = A205, tag = "[annotated] " }, { path = L205, tag = "[live] " } }
  local n_ok, n_all = 0, 0
  local function done(ok) n_all = n_all + 1; if ok then n_ok = n_ok + 1 end end
  local function mk(wname, enemies, PATH, TAG)
    local c = { name = HERO, uid = enemies[1].uid - 4, owns = { WOD }, melee = false, dist = 50, pos = { 0, 0, 0 }, width = 2,
                men_alive = 1, unit_class = "com", hp_frac = 1.0 }
    local W = make_world({ can_perform = true, units = { c }, enemies = enemies,
      cards = { { id = tostring(c.uid), state = "active", vis = true } }, bar = { { id = "b1", key = WOD } } })
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
    pcall(click, W, "zz_auto_badge_wind_of_death"); ui(W)
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
    check(TAG .. id .. (RED205 and "-RED" or "") .. ": " .. text, ok)
    done(ok)
  end
  local function order(W)
    if #W.fires + #W.ground_fires ~= 1 then return nil end
    if #W.fires == 1 then return "the unit form (the caster's own line)" end
    local o = W.ground_fires[1]
    return string.format("aimed: start (%.1f,%.1f) bearing %.0f", o.pos.vx, o.pos.vz, o.orient)
  end
  for _, f in ipairs(FILES) do
    local TAG, P = f.tag, f.path
    local alone = nil
    do
      local W = mk("DW1. Wind of Death: one block standing at (-20,60)", { block(20505, -20, 60, false) }, P, TAG)
      if W ~= nil then
        alone = order(W)
        verdict(TAG, "DW1a", "ONE order (" .. tostring(alone) .. ")", alone ~= nil)
        tally(W)
      else
        done(false)
      end
    end
    do
      local W = mk("DW2. Wind of Death: the standing block and a second block walking at (20,60)",
        { block(20515, -20, 60, false), block(20516, 20, 60, true) }, P, TAG)
      if W ~= nil then
        local both = order(W)
        local good = (both ~= nil and both == alone)
        if RED205 then good = (both ~= nil and both ~= alone) end
        verdict(TAG, "DW2a", (RED205 and "a different order, pulled by the walking unit" or "the same order as with the standing block alone")
          .. " (" .. tostring(both) .. " vs " .. tostring(alone) .. ")", good)
        tally(W)
      else
        done(false)
      end
    end
    do
      local W = mk("DW3. Wind of Death: only a walking block", { block(20525, 20, 60, true) }, P, TAG)
      if W ~= nil then
        verdict(TAG, "DW3a", "no order (" .. #W.fires .. ", " .. #W.ground_fires .. ")", #W.fires == 0 and #W.ground_fires == 0)
        tally(W)
      else
        done(false)
      end
    end
  end
  check("HARNESS 205: every world behaved - " .. n_ok .. "/" .. n_all, n_ok == n_all)
  print("== HARNESS 205 done: " .. (checks - pre205) .. " checks in this section ==")
end
