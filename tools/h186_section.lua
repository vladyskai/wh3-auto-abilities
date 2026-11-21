-- ============================================================================
-- HARNESS 186 (round 187): THE BADGES FOLLOW THE WHEEL AT ANY RESOLUTION OR UI SCALE (user 2026-11-21: "we need to
--   fix the UI scale ... when I change Resolution in the game, the A/M and the arm all buttons are not aligned").
--   The positions are the 2026-11-21 log's: tuned frame (UI scale about 1.29) wheel ability_parent (42,893), centre
--   orders_parent (691,1055); UI scale 1.6 wheel (42,677), centre (499,839).
--   0zz35 the shift block, its tick call, the badge and ALL offsets carry ui_dx / ui_dy.
--   US1 UI scale 1.6: the slot-1 badge at (-673,-209) and the ALL button at (-731,0) (RED: -865 / -923, off screen).
--   US2 the tuned frame: (-865,-209) and (-923,0), unchanged.
--   US3 no readable reference: (-865,-209) and (-923,0), unchanged.
--   US4 the resolution changes in battle (tuned -> 1.6): the badge and the ALL button move within 2 s.
--   RED control: H186_LIVE / H186_ANN on docs/backups/round187/pre187_*.lua.
-- ============================================================================
function run_h186()
  local L186 = os.getenv("H186_LIVE") or LIVE
  local A186 = os.getenv("H186_ANN") or ANN
  local RED186 = (os.getenv("H186_LIVE") ~= nil) or (os.getenv("H186_ANN") ~= nil)
  local KEY = "wh2_dlc13_lord_abilities_kill_shot"
  local MARK = "focused_shot"
  local WULF = "wh2_dlc13_emp_cha_markus_wulfhart_0"
  local pre186 = checks
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1; at = i + #tok
    end
  end
  print("== HARNESS 186 - section 0zz35: the round-187 tokens ==")
  if not RED186 then
    for _, f in ipairs({ { name = "live", path = L186 }, { name = "ann", path = A186 } }) do
      local s = read_file(f.path)
      check("0zz35 " .. f.name .. ": the UI shift block, its tick call, the badge and ALL offsets carry it",
        cp(s, "\nfunction FOURTH.ui_shift_tick()\n") == 1
        and cp(s, "\tpcall(FOURTH.ui_shift_tick)   -- ROUND 187") == 1
        and cp(s, 'FOURTH.UI_WHEEL_REFS = { { "ability_parent", 42, 893 }, { "button_ability", 96, 845 } }') == 1
        and cp(s, 'FOURTH.UI_CENTRE_REFS = { { "orders_parent", 691, 1055 }, { "behaviour_parent", 1021, 1055 }, { "button_parent", 1072, 1052 } }') == 1
        and cp(s, "FOURTH.ALL_OX + FOURTH.ui_dx, FOURTH.ALL_OY + FOURTH.ui_dy") == 2
        and cp(s, "(slot[1] - WHEEL_TOP_X) + FOURTH.ui_dx") == 1
        and cp(s, "find_uicomponent(") == cp(read_file(f.name == "live" and "docs/backups/round187/pre187_live.lua"
          or "docs/backups/round187/pre187_ann.lua"), "find_uicomponent("))
    end
  end
  local FILES = { { path = A186, tag = "[annotated] " }, { path = L186, tag = "[live] " } }
  local n_ok, n_all = 0, 0
  local function done(ok) n_all = n_all + 1; if ok then n_ok = n_ok + 1 end end
  local TUNED = { ability_parent = { 42, 893 }, orders_parent = { 691, 1055 } }
  local SCALE16 = { ability_parent = { 42, 677 }, orders_parent = { 499, 839 } }
  -- frames: the reference positions the mock's ui root answers, one table per phase (nil = no reference)
  local function world(wname, PATH, TAG, frames, switch_at)
    local units = { { name = WULF, uid = 1001, owns = { KEY }, melee = false, dist = 300, health_percent = 100 } }
    local W = make_world({ can_perform = false, units = units, enemies = {},
      cards = { { id = "1001", state = "active", vis = true } }, bar = { { id = "b1", key = KEY } } })
    W.defaults_on = false
    print("== " .. TAG .. wname .. " ==")
    W.bm.get_player_alliance = function() return "OUR_ALLIANCE" end
    local ok = pcall(load_world, W, PATH)
    check(TAG .. wname .. ": the file loads", ok)
    if not ok then tally(W); return nil end
    local root = core:get_ui_root()
    local old_find = root.Find
    local frame = frames[1]
    root.Find = function(self, what, a)
      if frame ~= nil and type(what) == "string" and frame[what] ~= nil then
        local p = frame[what]
        local c = {}
        function c:Id() return what end
        function c:Position() return p[1], p[2] end
        return c
      end
      return old_find(self, what, a)
    end
    deploy_phases(W); ui(W)
    sel_event(W, 1001, true); ui(W); ui(W)
    polln(W, 4)
    if switch_at ~= nil then
      frame = frames[2]
      for _ = 1, switch_at do ui(W) end   -- the ui tick (50 ms in game): the shift is re-read every 40 of them
    end
    return W
  end
  local function offs(W, name)
    local rec = W.badge_records and W.badge_records[name]
    if rec == nil or rec.offset == nil then return nil, nil end
    return rec.offset[1], rec.offset[2]
  end
  local WORLDS = {
    { "US1. UI scale 1.6: the badge and the ALL button follow the wheel", { SCALE16 }, nil, -673, -209, -731, 0 },
    { "US2. the tuned frame: unchanged", { TUNED }, nil, -865, -209, -923, 0 },
    { "US3. no readable reference: unchanged", { nil }, nil, -865, -209, -923, 0 },
    { "US4. the resolution changes in battle (tuned -> 1.6): both move within 2 s", { TUNED, SCALE16 }, 41, -673, -209, -731, 0 },
  }
  for _, f in ipairs(FILES) do
    local TAG = f.tag
    for i, w in ipairs(WORLDS) do
      local W = world(w[1], f.path, TAG, w[2], w[3])
      if W ~= nil then
        local bx, by = offs(W, "zz_auto_badge_" .. MARK)
        local ax, ay = offs(W, "zz_auto_badge_all")
        local want = (bx == w[4] and by == w[5] and ax == w[6] and ay == w[7])
        local a, txt
        if RED186 then
          -- the pre-187 build: the tuned offsets whatever the frame (the user's off-screen badges at 1.6)
          a = (bx == -865 and by == -209 and ax == -923 and ay == 0)
          txt = "-REDa: the pre-187 build keeps the tuned offsets"
        else
          a = want
          txt = "a: badge (" .. tostring(w[4]) .. "," .. tostring(w[5]) .. ") ALL (" .. tostring(w[6]) .. "," .. tostring(w[7]) .. ")"
        end
        check(TAG .. w[1]:sub(1, 3) .. txt .. " - got badge (" .. tostring(bx) .. "," .. tostring(by) .. ") ALL ("
          .. tostring(ax) .. "," .. tostring(ay) .. ")", a)
        done(a)
        tally(W)
      end
    end
  end
  if RED186 then
    check("RED CONTROL (harness 186): the pre-187 build keeps the tuned offsets at every UI scale - " .. n_ok .. "/" .. n_all,
      n_all == 8 and n_ok == 8)
  else
    check("HARNESS 186: every check behaved - " .. n_ok .. "/" .. n_all, n_all == 8 and n_ok == 8)
  end
  print("== HARNESS 186 done: " .. (checks - pre186) .. " checks in this section ==")
end
