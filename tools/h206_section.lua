-- ============================================================================
-- HARNESS 206 (round 208, tuning: the cost of the free-aim search. No cast decision changes).
--   0zz54 the round-208 tokens in both files.
--   PF1 a hero owns the Fiery Ring of Thori, Zombies stand in range, the ability CANNOT be cast (recharging): no order,
--       and the search never runs (in 8 polls the enemy's is_moving() is read once, by the map probe). RED (round
--       207): no order either, but the search runs (is_moving() is read 7 times).
--   PF2 four heroes with consecutive ids own the ring, no vector constructor (every search ends in a held order): the
--       four searches fall on FOUR different polls. RED: all four on the same poll.
--   PF3 one hero, the ability ready -> ONE aimed order within 6 polls (GREEN and RED: nothing is lost).
--   RED control: H206_LIVE / H206_ANN on docs/backups/round208/pre208_*.lua.
-- ============================================================================
function run_h206()
  local L206 = os.getenv("H206_LIVE") or LIVE
  local A206 = os.getenv("H206_ANN") or ANN
  local RED206 = (os.getenv("H206_LIVE") ~= nil) or (os.getenv("H206_ANN") ~= nil)
  local RING = "wh_main_item_abilities_fiery_ring_of_thori"
  local ENG = "wh_main_dwf_cha_master_engineer_0"
  local ZOM = "wh_main_vmp_inf_zombie"
  local pre206 = checks
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1; at = i + #tok
    end
  end
  print("== HARNESS 206 - section 0zz54: the round-208 tokens ==")
  for _, f in ipairs({ { name = "live", path = L206 }, { name = "ann", path = A206 } }) do
    local s = read_file(f.path)
    local stag = cp(s, "\t\tif (tick_count + idn) % FOURTH.FREE_AIM_EVERY ~= 0 then return ")
    local can = cp(s, "\t\tif ok_can and can == false then return ")
    local old = cp(s, "per[key] = tick_count + FOURTH.FREE_AIM_EVERY")
    if RED206 then
      check("0zz54 " .. f.name .. " (RED): the pre-208 file has the per-caster table and no readiness test",
        stag == 0 and can == 0 and old == 1)
    else
      check("0zz54 " .. f.name .. ": the poll depends on the unit id (" .. stag .. "), no search while not ready (" .. can
        .. "), the old table is gone (" .. old .. ")", stag == 1 and can == 1 and old == 0)
    end
  end
  local FILES = { { path = A206, tag = "[annotated] " }, { path = L206, tag = "[live] " } }
  local n_ok, n_all = 0, 0
  local function done(ok) n_all = n_all + 1; if ok then n_ok = n_ok + 1 end end
  local function mk(wname, base, n_casters, can, vector, PATH, TAG, polls)
    local units, cards = {}, {}
    for c = 1, n_casters do
      units[c] = { name = ENG, uid = base + c, owns = { RING }, melee = false, dist = 60, pos = { (c - 1) * 3, 0, 0 }, width = 2,
                   men_alive = 1, unit_class = "com", hp_frac = 1.0 }
      cards[c] = { id = tostring(base + c), state = "active", vis = true }
    end
    local e = { uid = base + 9, name = ZOM, melee = false, pos = { 0, 0, 60 }, width = 30, men_alive = 160, initial_men = 160,
                unit_class = "inf_mel", dist = 60 }
    local W = make_world({ can_perform = can, units = units, enemies = { e }, cards = cards, bar = { { id = "b1", key = RING } } })
    W.defaults_on = false
    W.free_aim_on = true
    print("== " .. TAG .. wname .. " ==")
    W.bm.get_player_alliance = function() return "OUR_ALLIANCE" end
    W.height_reads = {}
    W.bm.get_terrain_height = function(self, x, z)
      W.height_reads[#W.height_reads + 1] = W.poll_ticks
      return 0
    end
    v = nil
    if vector then v = function(x, y, z) return { vx = x, vy = y, vz = z } end end
    local ok = pcall(load_world, W, PATH)
    check(TAG .. wname .. ": the file loads", ok)
    if not ok then v = nil; tally(W); return nil end
    deploy_phases(W); ui(W)
    W.moving_reads = 0
    for i = 1, #(W.enemy_entries or {}) do
      local pr = W.enemy_entries[i]
      if pr ~= nil and pr.unit ~= nil then
        pr.unit.is_visible_to_alliance = function(self, a) return true end
        pr.unit.is_currently_flying = function(self) return false end
        pr.unit.strategic_value = function(self) return 100 end
        local old_mv = pr.unit.is_moving
        pr.unit.is_moving = function(self)
          if W.count_moving then W.moving_reads = W.moving_reads + 1 end
          if old_mv ~= nil then return old_mv(self) end
          return false
        end
      end
    end
    for c = 1, n_casters do
      sel_event(W, base + c, true); ui(W); ui(W)
      pcall(click, W, "zz_auto_badge_fiery_ring_of_thori"); ui(W)
      sel_event(W, base + c, false); ui(W)
    end
    W.conflict = true
    W.count_moving = true
    polln(W, polls)
    W.count_moving = false
    v = nil
    return W
  end
  local function verdict(TAG, id, text, ok)
    check(TAG .. id .. (RED206 and "-RED" or "") .. ": " .. text, ok)
    done(ok)
  end
  for _, f in ipairs(FILES) do
    local TAG, P = f.tag, f.path
    do
      local W = mk("PF1. the ring cannot be cast (recharging), Zombies stand in range", 20600, 1, false, true, P, TAG, 8)
      if W ~= nil then
        local n = #W.fires + #W.ground_fires
        -- the read-only map probe reads is_moving() once in 8 polls: the evaluator itself must add nothing
        local good = (n == 0 and W.moving_reads <= 1)
        if RED206 then good = (n == 0 and W.moving_reads > 1) end
        verdict(TAG, "PF1a", "no order, the enemy's is_moving() read " .. W.moving_reads .. " time(s) ("
          .. (RED206 and "RED: the search ran" or "need at most 1, the map probe's own read: no search") .. ")", good)
        tally(W)
      else
        done(false)
      end
    end
    do
      local W = mk("PF2. four casters with consecutive ids, every search ends in a held order", 20620, 4, true, false, P, TAG, 8)
      if W ~= nil then
        local per, most, polls_used = {}, 0, 0
        for _, t in ipairs(W.height_reads) do
          if per[t] == nil then polls_used = polls_used + 1 end
          per[t] = (per[t] or 0) + 1
          if per[t] > most then most = per[t] end
        end
        local good = (#W.height_reads >= 4 and most == 1)
        if RED206 then good = (#W.height_reads >= 4 and most == 4) end
        verdict(TAG, "PF2a", #W.height_reads .. " searches reached the aim over " .. polls_used .. " poll(s), at most " .. most
          .. " on one poll (" .. (RED206 and "RED: 4 together" or "need 1") .. ")", good)
        tally(W)
      else
        done(false)
      end
    end
    do
      local W = mk("PF3. one caster, the ring ready", 20640, 1, true, true, P, TAG, 6)
      if W ~= nil then
        verdict(TAG, "PF3a", "ONE aimed order within 6 polls (" .. #W.fires .. ", " .. #W.ground_fires .. ")",
          #W.fires == 0 and #W.ground_fires == 1)
        tally(W)
      else
        done(false)
      end
    end
  end
  check("HARNESS 206: every world behaved - " .. n_ok .. "/" .. n_all, n_ok == n_all)
  print("== HARNESS 206 done: " .. (checks - pre206) .. " checks in this section ==")
end
