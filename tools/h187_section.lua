-- ============================================================================
-- HARNESS 187 (round 188): THE RANGE RULE (user ruling 2026-11-21: "C. Your rule, the larger of 70% and real minus
--   20 m, everywhere." / "This one, thanks"). Every cast-range bound is max(floor(real x 0.70), real - 20).
--   0zz36 the margin constant, FOURTH.range_bound, EVERY ENEMY_CAST / ALLY_CAST constant obeys the rule, the three
--         named bounds (Blood Sacrifice 80, Eat da Runts! 80, Accusation 55), the Executioner takes the larger bound.
--   RB1   at load, every entry with a game range carries the new bound (Focused Shot 230, the Executioner 230,
--         Accusation 55); RED: the 70% bounds (Focused Shot 175).
--   FS1   Focused Shot: a Vampire 229 m away (inside 230) -> ONE cast (RED: none, 229 > 175).
--   FS2   Focused Shot: a Vampire 231 m away (beyond 230) -> no cast (RED: none).
--   RED control: H187_LIVE / H187_ANN on docs/backups/round188/pre188_*.lua.
-- ============================================================================
function run_h187()
  local L187 = os.getenv("H187_LIVE") or LIVE
  local A187 = os.getenv("H187_ANN") or ANN
  local RED187 = (os.getenv("H187_LIVE") ~= nil) or (os.getenv("H187_ANN") ~= nil)
  local FS = "wh2_dlc13_lord_abilities_kill_shot"
  local CASTER = "wh2_dlc13_emp_cha_markus_wulfhart_0"
  local VA = "wh_main_vmp_cha_vampire_0"
  local pre187 = checks
  local function rb(real) return math.max(math.floor(real * 0.70 + 1e-9), real - 20) end
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1; at = i + #tok
    end
  end
  print("== HARNESS 187 - section 0zz36: the round-188 tokens ==")
  for _, f in ipairs({ { name = "live", path = L187 }, { name = "ann", path = A187 } }) do
    local s = read_file(f.path)
    local n_c, bad = 0, {}
    for side, real, val in s:gmatch("\nFOURTH%.(%u+)_CAST_R(%d+)%s*=%s*(%d+)") do
      n_c = n_c + 1
      if tonumber(val) ~= rb(tonumber(real)) then bad[#bad + 1] = side .. " " .. real .. "=" .. val end
    end
    local ok = cp(s, "FOURTH.RANGE_MARGIN_M = 20 ") == 1
      and cp(s, "\nfunction FOURTH.range_bound(real)\n") == 1
      and cp(s, "math.max(math.floor(real * FOURTH.RANGE_FRACTION + 1e-9), real - FOURTH.RANGE_MARGIN_M)") == 1
      and cp(s, "FOURTH.BLOOD_SACRIFICE_RANGE_M = 80 ") == 1 and cp(s, "FOURTH.EAT_DA_RUNTS_RANGE_M = 80 ") == 1
      and cp(s, "FOURTH.ACCUSATION_RANGE_M = 55 ") == 1
      and cp(s, "ability.range_m = math.max(ability.range_m or 0,") == 1
      and n_c >= 25 and #bad == 0
    if RED187 then
      check("0zz36 " .. f.name .. " (RED): the pre-188 file has the 70% bounds (" .. #bad .. " constants off the new rule)",
        not ok and #bad > 0)
    else
      check("0zz36 " .. f.name .. ": the margin, range_bound, " .. n_c .. " cast constants on the new rule (off: "
        .. #bad .. (#bad > 0 and (", " .. bad[1]) or "") .. "), the named bounds 80/80/55, the Executioner", ok)
    end
  end
  local FILES = { { path = A187, tag = "[annotated] " }, { path = L187, tag = "[live] " } }
  local n_ok, n_all = 0, 0
  local function done(ok) n_all = n_all + 1; if ok then n_ok = n_ok + 1 end end
  local function world(wname, units, enemies, PATH, TAG)
    local cards = {}
    for _, d in ipairs(units) do cards[#cards + 1] = { id = tostring(d.uid), state = "active", vis = true } end
    local W = make_world({ can_perform = true, units = units, enemies = enemies, cards = cards,
      bar = { { id = "b1", key = FS } } })
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
        pr.unit.strategic_value = function(self) return 1500 end
      end
    end
    sel_event(W, units[1].uid, true); ui(W); ui(W)
    click(W, "zz_auto_badge_focused_shot"); ui(W)
    sel_event(W, units[1].uid, false); ui(W)
    W.conflict = true
    polln(W, 4)
    return W
  end
  local function caster(b, dist)
    return { name = CASTER, uid = b, owns = { FS }, melee = false, dist = dist, pos = { 0, 0, 0 }, width = 2,
             men_alive = 1, unit_class = "com" }
  end
  local function vampire(uid, dist)
    return { uid = uid, name = VA, melee = false, pos = { 0, 0, dist }, width = 6, men_alive = 1, initial_men = 1,
             unit_class = "com", dist = dist }
  end
  local function casts(W)
    local n = 0
    for _, x in ipairs(W.fires) do if x.key == FS then n = n + 1 end end
    for _, x in ipairs(W.ground_fires or {}) do if x.key == FS then n = n + 1 end end
    return n
  end
  for _, f in ipairs(FILES) do
    local TAG = f.tag
    -- FS1 (and RB1 on the same load)
    local W = world("FS1. Focused Shot: a Vampire 229 m away (bound 230) -> ONE cast",
      { caster(18701, 229) }, { vampire(18705, 229) }, f.path, TAG)
    if W ~= nil then
      local by, bad, n = {}, {}, 0
      for _, e in ipairs(W.cap or {}) do
        by[e.marker] = e
        local want = nil
        if e.trigger == "air_drop_on_infantry" then
          want = nil
        elseif e.ally_range_real ~= nil then
          want = rb(e.ally_range_real)
        elseif e.range_real ~= nil and e.unbounded ~= true then
          want = rb(e.range_real)
          if e.range_frac ~= nil then want = math.max(want, math.floor(e.range_real * e.range_frac + 1e-9)) end
        end
        if want ~= nil then
          n = n + 1
          if e.range_m ~= want then bad[#bad + 1] = tostring(e.marker) .. "=" .. tostring(e.range_m) .. "/" .. want end
        end
      end
      local fsb = by.focused_shot and by.focused_shot.range_m
      local exb = by.lord_abilities_executioner and by.lord_abilities_executioner.range_m
      local acb = by.accusation and by.accusation.range_m
      local a
      if RED187 then
        a = (#bad > 0 and fsb == 175)
        check(TAG .. "RB1 (RED): the pre-188 bounds are 70% (Focused Shot " .. tostring(fsb) .. ", " .. #bad .. " of " .. n
          .. " off the new rule)", a)
      else
        a = (n > 400 and #bad == 0 and fsb == 230 and exb == 230 and acb == 55)
        check(TAG .. "RB1: all " .. n .. " bounded entries carry max(70%, real - 20) (off " .. #bad
          .. (#bad > 0 and (": " .. bad[1]) or "") .. "); Focused Shot " .. tostring(fsb) .. ", the Executioner "
          .. tostring(exb) .. ", Accusation " .. tostring(acb), a)
      end
      done(a)
      local want = RED187 and 0 or 1
      local b = (casts(W) == want)
      check(TAG .. "FS1a: " .. want .. " cast(s) expected at 229 m, got " .. casts(W), b)
      done(b)
      tally(W)
    end
    local W2 = world("FS2. Focused Shot: a Vampire 231 m away (bound 230) -> no cast",
      { caster(18721, 231) }, { vampire(18725, 231) }, f.path, TAG)
    if W2 ~= nil then
      local c = (casts(W2) == 0)
      check(TAG .. "FS2a: 0 casts expected at 231 m, got " .. casts(W2), c)
      done(c)
      tally(W2)
    end
  end
  check("HARNESS 187: every world behaved - " .. n_ok .. "/" .. n_all, n_ok == n_all)
  print("== HARNESS 187 done: " .. (checks - pre187) .. " checks in this section ==")
end
